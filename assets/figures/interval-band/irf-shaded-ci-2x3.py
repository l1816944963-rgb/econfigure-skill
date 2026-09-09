"""Render six impulse-response panels with supplied shaded intervals."""

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
    figure_size: tuple[float, float] = (6.79, 6.53)
    line_color: str = "#2D3036"
    band_color: str = "#D5D6D8"


def load_data(source) -> pd.DataFrame:
    frame = read_frame(source)
    columns = ("panel", "panel_order", "month", "estimate", "lower", "upper")
    require_columns(frame, columns)
    frame = frame.loc[:, columns].copy()
    require_finite(frame, ("panel_order", "month", "estimate", "lower", "upper"))
    if frame.panel.nunique() != 6 or set(frame.panel_order) != set(range(1, 7)):
        raise ValueError("This asset requires six panels ordered 1 through 6.")
    if frame.duplicated(["panel", "month"]).any():
        raise ValueError("Panel and month keys must be unique.")
    panel_mapping = frame[["panel", "panel_order"]].drop_duplicates()
    if len(panel_mapping) != 6 or panel_mapping["panel_order"].nunique() != 6:
        raise ValueError("Each panel must map to one unique panel order.")
    if (frame.lower > frame.estimate).any() or (frame.estimate > frame.upper).any():
        raise ValueError("Every supplied interval must contain its estimate.")
    month_sets = [tuple(group.month) for _, group in frame.groupby("panel_order", sort=True)]
    if len(set(month_sets)) != 1:
        raise ValueError("All panels must share horizons.")
    return frame


def render(data, config: ChartStyle | None = None) -> Figure:
    style = config or ChartStyle()
    frame = load_data(data)
    fig = Figure(figsize=style.figure_size, facecolor="white")
    gs = fig.add_gridspec(2, 3, left=.06, right=.94, bottom=.08, top=.97, wspace=.20, hspace=.32)
    titles = ("log Real imports", "log IP", "log (Real imports / IP)") * 2
    for order in range(1, 7):
        ax = fig.add_subplot(gs[(order - 1) // 3, (order - 1) % 3])
        style_axis(ax, grid=True, full_spines=True)
        group = frame.loc[frame.panel_order == order].sort_values("month")
        ax.fill_between(group.month, group.lower, group.upper, color=style.band_color, linewidth=0)
        ax.plot(group.month, group.estimate, color=style.line_color, linewidth=1.35)
        ax.axhline(0, color="#999999", linewidth=.5)
        ax.set_xlim(-1, 37)
        ax.set_ylim(-.021, .011)
        ax.set_xticks([0, 12, 24, 36])
        ax.set_yticks([-.02, -.01, 0, .01])
        ax.set_yticklabels(["-.02", "-.01", "0", ".01"])
        ax.set_title(titles[order - 1], fontsize=9, fontfamily="serif", pad=3)
        ax.set_xlabel("month", fontsize=8.5, fontfamily="serif")
    return fig


def main() -> None:
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=directory / "irf-shaded-ci-2x3.fixture.csv")
    parser.add_argument("--output-dir", type=Path, default=directory)
    parser.add_argument("--qa-preview", type=Path)
    args = parser.parse_args()
    print(save_outputs(render(args.data), args.output_dir, "irf-shaded-ci-2x3", qa_preview=args.qa_preview))


if __name__ == "__main__":
    main()
