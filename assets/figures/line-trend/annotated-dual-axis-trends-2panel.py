"""Render two annotated panels containing three annual trend series."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from chartlib.asset_runtime import read_frame, require_columns, require_continuous_years, require_finite, save_outputs, style_axis
from matplotlib.figure import Figure


@dataclass(frozen=True)
class ChartStyle:
    figure_size: tuple[float, float] = (4.72, 6.78)
    axes_bounds: tuple[tuple[float, float, float, float], ...] = ((55 / 472, 369 / 678, 334 / 472, 282 / 678), (55 / 472, 30 / 678, 334 / 472, 289 / 678))
    colors: tuple[str, ...] = ("#333333", "#444444", "#444444")
    markers: tuple[str, ...] = ("D", "^", "s")


def load_data(source) -> pd.DataFrame:
    frame = read_frame(source)
    columns = ("panel", "year", "series", "series_order", "axis", "value")
    require_columns(frame, columns)
    frame = frame.loc[:, columns].copy()
    require_finite(frame, ("year", "series_order", "value"))
    if frame["panel"].nunique() != 2:
        raise ValueError("This asset requires exactly two panels.")
    for panel, group in frame.groupby("panel", sort=False):
        if group["series"].nunique() != 3:
            raise ValueError(f"Panel {panel!r} requires exactly three series.")
        require_continuous_years(group["year"])
    if frame.duplicated(["panel", "year", "series"]).any():
        raise ValueError("Each panel-year-series combination must be unique.")
    return frame


def render(data, config: ChartStyle | None = None) -> Figure:
    style = config or ChartStyle()
    frame = load_data(data)
    fig = Figure(figsize=style.figure_size, facecolor="white")
    panel_specs = (
        ("march", "A. March CPS Full-Time Weekly Earnings, 1963–2005", 1963, [1963, 1969, 1975, 1981, 1987, 1993, 1999, 2005], [1973, 1979, 1992]),
        ("morg", "B. MORG CPS Hourly Earnings, 1973–2005", 1973, [1973, 1977, 1981, 1985, 1989, 1993, 1997, 2001, 2005], [1979, 1992]),
    )
    for index, (panel, title, xmin, xticks, references) in enumerate(panel_specs):
        left = fig.add_axes(style.axes_bounds[index])
        right = left.twinx()
        style_axis(left, full_spines=True)
        right.spines["left"].set_visible(False)
        right.spines["right"].set_color("#5E6165")
        group = frame.loc[frame.panel == panel]
        for order in (1, 2, 3):
            series = group.loc[group.series_order == order].sort_values("year")
            axis = right if series.axis.iloc[0] == "right" else left
            axis.plot(series.year, series.value, color=style.colors[order - 1], linewidth=1.05, marker=style.markers[order - 1], markersize=2.8, markerfacecolor="white")
        for year in references:
            left.axvline(year, color="#303030", linewidth=0.85)
            left.text(year, 1.655, str(year), ha="center", va="top", fontsize=7)
        left.set_xlim(xmin, 2005)
        left.set_ylim(.8, 1.7)
        right.set_ylim(.35, .70)
        left.set_xticks(xticks)
        left.set_yticks([.8,.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7])
        right.set_yticks([.35,.40,.45,.50,.55,.60,.65,.70])
        left.set_title(title, fontsize=8.2, fontweight="bold", pad=5)
        left.set_ylabel("Log Earnings Ratio", fontsize=7.8)
        right.set_ylabel("Log College/HS Wage Gap", fontsize=7.8, rotation=270, labelpad=11)
        if index == 0:
            left.annotate("Overall 90/10", xy=(1979, 1.30), xytext=(1964.5, 1.38), fontsize=7, arrowprops=dict(arrowstyle="-|>", lw=.8, color="black"))
            left.annotate("College/HS Gap", xy=(1988, 1.18), xytext=(1979, 1.20), fontsize=7, arrowprops=dict(arrowstyle="-|>", lw=.8, color="black"))
            left.annotate("Residual 90/10", xy=(1998, 1.14), xytext=(1995, 1.04), fontsize=7, arrowprops=dict(arrowstyle="-|>", lw=.8, color="black"))
        else:
            left.annotate("Overall 90/10", xy=(1986, 1.42), xytext=(1978.5, 1.53), fontsize=7, arrowprops=dict(arrowstyle="-|>", lw=.8, color="black"))
            left.annotate("College/HS Gap", xy=(1986, 1.22), xytext=(1975, 1.12), fontsize=7, arrowprops=dict(arrowstyle="-|>", lw=.8, color="black"))
            left.annotate("Residual 90/10", xy=(2002.5, 1.14), xytext=(1994, 1.01), fontsize=7, arrowprops=dict(arrowstyle="-|>", lw=.8, color="black"))
    return fig


def main() -> None:
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=directory / "annotated-dual-axis-trends-2panel.fixture.csv")
    parser.add_argument("--output-dir", type=Path, default=directory)
    parser.add_argument("--qa-preview", type=Path)
    args = parser.parse_args()
    print(save_outputs(render(args.data), args.output_dir, "annotated-dual-axis-trends-2panel", qa_preview=args.qa_preview))


if __name__ == "__main__":
    main()
