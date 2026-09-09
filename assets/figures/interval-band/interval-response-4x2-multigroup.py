"""Render eight response panels with three groups and supplied intervals."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from chartlib.asset_runtime import read_frame, require_columns, require_finite, save_outputs, style_axis
from matplotlib.figure import Figure


@dataclass(frozen=True)
class ChartStyle:
    figure_size: tuple[float, float] = (5.18, 6.81)
    colors: tuple[str, ...] = ("#5A35A5", "#FF7A28", "#474747")
    fills: tuple[str, ...] = ("#CFC6E2", "#F4D5C0", "#C9C2BC")
    line_styles: tuple[str, ...] = ("-", "--", "-.")


def load_data(source) -> pd.DataFrame:
    frame = read_frame(source)
    columns = ("panel", "horizon", "group", "group_order", "estimate", "lower", "upper")
    require_columns(frame, columns)
    frame = frame.loc[:, columns].copy()
    require_finite(frame, ("horizon", "group_order", "estimate", "lower", "upper"))
    if frame["panel"].nunique() != 8:
        raise ValueError("This asset requires exactly eight panels.")
    if frame.duplicated(["panel", "group", "horizon"]).any():
        raise ValueError("Panel, group, and horizon keys must be unique.")
    if (frame.lower > frame.estimate).any() or (frame.estimate > frame.upper).any():
        raise ValueError("Every supplied interval must contain its estimate.")
    for panel, group in frame.groupby("panel", sort=False):
        if group["group"].nunique() != 3 or set(group.group_order) != {1, 2, 3}:
            raise ValueError(f"Panel {panel!r} requires three ordered groups.")
        mapping = group[["group", "group_order"]].drop_duplicates()
        if len(mapping) != 3 or mapping["group_order"].nunique() != 3:
            raise ValueError(f"Panel {panel!r} requires a one-to-one group order mapping.")
        horizons = [tuple(g.horizon) for _, g in group.groupby("group_order", sort=True)]
        if len(set(horizons)) != 1:
            raise ValueError(f"Panel {panel!r} groups must share horizons.")
    return frame


def load_panels(source) -> pd.DataFrame:
    panels = read_frame(source)
    columns = ("panel", "panel_order", "title", "unit", "y_min", "y_max", "y_tick_start", "y_tick_end", "y_tick_interval")
    require_columns(panels, columns)
    panels = panels.loc[:, columns].copy()
    require_finite(panels, ("panel_order", "y_min", "y_max", "y_tick_start", "y_tick_end", "y_tick_interval"))
    if len(panels) != 8 or set(panels.panel_order) != set(range(1, 9)):
        raise ValueError("Panel specifications must contain orders 1 through 8.")
    return panels.sort_values("panel_order")


def render(data, panel_specs, config: ChartStyle | None = None) -> Figure:
    style = config or ChartStyle()
    frame = load_data(data)
    panels = load_panels(panel_specs)
    if set(frame.panel) != set(panels.panel):
        raise ValueError("Data and panel specifications must match.")
    fig = Figure(figsize=style.figure_size, facecolor="white")
    gs = fig.add_gridspec(4, 2, left=.10, right=.95, bottom=.145, top=.965, wspace=.20, hspace=.32)
    legend_handles = []
    for index, spec in enumerate(panels.itertuples(index=False)):
        ax = fig.add_subplot(gs[index // 2, index % 2])
        style_axis(ax, grid=True)
        panel = frame.loc[frame.panel == spec.panel]
        if panel.lower.min() < spec.y_min or panel.upper.max() > spec.y_max:
            raise ValueError(f"Panel {spec.panel!r} intervals exceed its configured limits.")
        for order in (1, 2, 3):
            series = panel.loc[panel.group_order == order].sort_values("horizon")
            ax.fill_between(series.horizon, series.lower, series.upper, color=style.fills[order - 1], alpha=.75, linewidth=0)
            handle = ax.plot(series.horizon, series.estimate, color=style.colors[order - 1], linestyle=style.line_styles[order - 1], linewidth=1.05, label=series.group.iloc[0])[0]
            if index == 0:
                legend_handles.append(handle)
        ax.axhline(0, color="#777777", linewidth=.55)
        ax.set_xlim(-.2, 8.2)
        ax.set_xticks([0, 2, 4, 6, 8])
        ax.set_ylim(spec.y_min, spec.y_max)
        ax.set_yticks(np.arange(spec.y_tick_start, spec.y_tick_end + spec.y_tick_interval / 2, spec.y_tick_interval))
        ax.set_title(spec.title, fontsize=7.3, pad=3)
        ax.set_ylabel(spec.unit, fontsize=7)
        if index >= 6:
            ax.set_xlabel("Year after start of war", fontsize=7)
    fig.legend(legend_handles, [h.get_label() for h in legend_handles], loc="lower center", bbox_to_anchor=(.52, .012), ncol=3, frameon=False, fontsize=7, handlelength=3)
    return fig


def main() -> None:
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=directory / "interval-response-4x2-multigroup.fixture.csv")
    parser.add_argument("--panels", type=Path, default=directory / "interval-response-4x2-multigroup.panels.csv")
    parser.add_argument("--output-dir", type=Path, default=directory)
    parser.add_argument("--qa-preview", type=Path)
    args = parser.parse_args()
    print(save_outputs(render(args.data, args.panels), args.output_dir, "interval-response-4x2-multigroup", qa_preview=args.qa_preview))


if __name__ == "__main__":
    main()
