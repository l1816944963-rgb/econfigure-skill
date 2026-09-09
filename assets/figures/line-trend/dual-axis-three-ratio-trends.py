"""Render three sparse annual ratio series with one secondary y axis."""

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
    figure_size: tuple[float, float] = (7.29, 5.03)
    axes_bounds: tuple[float, float, float, float] = (67 / 729, 126 / 503, 580 / 729, 355 / 503)
    colors: tuple[str, ...] = ("#147A22", "#123F6D", "#9A3131")
    markers: tuple[str, ...] = ("o", "s", "D")


def load_data(source) -> pd.DataFrame:
    frame = read_frame(source)
    columns = ("year", "series", "series_order", "axis", "value")
    require_columns(frame, columns)
    frame = frame.loc[:, columns].copy()
    require_finite(frame, ("year", "series_order", "value"))
    if set(frame["series_order"]) != {1, 2, 3} or frame["series"].nunique() != 3:
        raise ValueError("This asset requires exactly three ordered series.")
    if set(frame["axis"]) != {"left", "right"}:
        raise ValueError("Series must declare left or right axis assignment.")
    if frame.duplicated(["year", "series"]).any():
        raise ValueError("Each year-series pair must be unique.")
    return frame


def render(data, config: ChartStyle | None = None) -> Figure:
    style = config or ChartStyle()
    frame = load_data(data)
    fig = Figure(figsize=style.figure_size, facecolor="white")
    left = fig.add_axes(style.axes_bounds)
    right = left.twinx()
    style_axis(left, grid=True)
    right.spines["top"].set_visible(False)
    right.spines["left"].set_visible(False)
    right.spines["right"].set_color("#4E4E4E")
    handles = []
    labels = []
    for order in (1, 2, 3):
        group = frame.loc[frame.series_order == order].sort_values("year")
        axis = left if group.axis.iloc[0] == "left" else right
        handle = axis.plot(group.year, group.value, color=style.colors[order - 1], marker=style.markers[order - 1], markersize=4.8, linewidth=1.35, label=group.series.iloc[0])[0]
        handles.append(handle)
        labels.append(group.series.iloc[0])
    left.set_xlim(1979.2, 2012.8)
    left.set_ylim(24, 52)
    right.set_ylim(9.7, 18.2)
    left.set_xticks([1980, 1990, 2000, 2010])
    left.set_yticks([25, 30, 35, 40, 45, 50])
    right.set_yticks([10, 12, 14, 16, 18])
    left.set_xlabel("year", fontsize=11)
    left.set_ylabel("Compensation (or Payroll) over Value Added", fontsize=10)
    right.set_ylabel("Payroll over Sales", fontsize=10, rotation=270, labelpad=17)
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.49, 0.025), ncol=2, frameon=True, fancybox=False, edgecolor="#D5E0E5", fontsize=10, handlelength=3.2, columnspacing=1.5)
    return fig


def main() -> None:
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=directory / "dual-axis-three-ratio-trends.fixture.csv")
    parser.add_argument("--output-dir", type=Path, default=directory)
    parser.add_argument("--qa-preview", type=Path)
    args = parser.parse_args()
    print(save_outputs(render(args.data), args.output_dir, "dual-axis-three-ratio-trends", qa_preview=args.qa_preview))


if __name__ == "__main__":
    main()
