"""Render PDF and upper-tail CDF panels with dashed parametric bounds."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from chartlib.asset_runtime import read_frame, require_columns, require_finite, save_outputs, style_axis
from matplotlib.figure import Figure


@dataclass(frozen=True)
class ChartStyle:
    figure_size: tuple[float, float] = (6.12, 6.30)
    axes_bounds: tuple[tuple[float, float, float, float], ...] = ((60 / 612, 344 / 630, 498 / 612, 246 / 630), (60 / 612, 35 / 630, 498 / 612, 225 / 630))


def load_data(source) -> pd.DataFrame:
    frame = read_frame(source)
    columns = ("panel", "x", "series", "series_order", "value")
    require_columns(frame, columns)
    frame = frame.loc[:, columns].copy()
    require_finite(frame, ("x", "series_order", "value"))
    if frame["panel"].nunique() != 2:
        raise ValueError("This asset requires exactly two panels.")
    for panel, group in frame.groupby("panel", sort=False):
        if group.series.nunique() != 3 or set(group.series_order) != {1, 2, 3}:
            raise ValueError(f"Panel {panel!r} requires three ordered curves.")
        x_sets = [tuple(s.x) for _, s in group.groupby("series_order", sort=True)]
        if len(set(x_sets)) != 1:
            raise ValueError(f"Panel {panel!r} curves must share x values.")
    return frame


def render(data, config: ChartStyle | None = None) -> Figure:
    style = config or ChartStyle()
    frame = load_data(data)
    fig = Figure(figsize=style.figure_size, facecolor="white")
    specs = (
        ("pdf", "Panel A. Distribution of school effects: students scoring 100+ on the AMC 12", r"Estimated PDF $F_\mu(u)$", "Multiplicative school effect $u$", (0, 2), (0, 1.2), [0,.2,.4,.6,.8,1.0,1.2]),
        ("cdf", "Panel B. Detail on CDF in the upper tail", r"Estimated CDF $F_\mu(u)$", "Multiplicative school effect $u$", (2, 8), (.90, 1.00), [.90,.91,.92,.93,.94,.95,.96,.97,.98,.99,1.00]),
    )
    for index, spec in enumerate(specs):
        panel, title, ylabel, xlabel, xlim, ylim, yticks = spec
        ax = fig.add_axes(style.axes_bounds[index])
        style_axis(ax, grid=True)
        group = frame.loc[frame.panel == panel]
        handles = []
        for order in (1, 2, 3):
            series = group.loc[group.series_order == order].sort_values("x")
            handle = ax.plot(series.x, series.value, color="#111111", linewidth=1.25 if order == 1 else .9, linestyle="-" if order == 1 else (0, (1.5, 1.2)), label=series.series.iloc[0])[0]
            handles.append(handle)
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.set_yticks(yticks)
        ax.set_title(title, fontsize=8.5, loc="left", pad=13)
        ax.set_ylabel(ylabel, fontsize=8.5)
        ax.set_xlabel(xlabel, fontsize=8.5)
        ax.legend(handles=handles, loc="upper right" if index == 0 else "lower right", frameon=True, fancybox=False, edgecolor="#333333", fontsize=7.5)
    return fig


def main() -> None:
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=directory / "pdf-cdf-parametric-bounds-2panel.fixture.csv")
    parser.add_argument("--output-dir", type=Path, default=directory)
    parser.add_argument("--qa-preview", type=Path)
    args = parser.parse_args()
    print(save_outputs(render(args.data), args.output_dir, "pdf-cdf-parametric-bounds-2panel", qa_preview=args.qa_preview))


if __name__ == "__main__":
    main()
