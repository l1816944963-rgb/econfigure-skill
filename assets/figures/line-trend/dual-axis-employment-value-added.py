"""Render two long annual series with a secondary axis and compact legend."""

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
    figure_size: tuple[float, float] = (7.18, 3.92)
    axes_bounds: tuple[float, float, float, float] = (79 / 718, 43 / 392, 547 / 718, 334 / 392)


def load_data(source) -> pd.DataFrame:
    frame = read_frame(source)
    columns = ("year", "employment_million", "real_value_added_billion")
    require_columns(frame, columns)
    frame = frame.loc[:, columns].copy()
    require_finite(frame, columns)
    require_continuous_years(frame["year"])
    if frame["year"].duplicated().any():
        raise ValueError("Each year must appear once.")
    return frame.sort_values("year", kind="stable")


def render(data, config: ChartStyle | None = None) -> Figure:
    style = config or ChartStyle()
    frame = load_data(data)
    fig = Figure(figsize=style.figure_size, facecolor="white")
    left = fig.add_axes(style.axes_bounds)
    right = left.twinx()
    style_axis(left, grid=True)
    right.spines["top"].set_visible(False)
    right.spines["left"].set_visible(False)
    right.spines["right"].set_color("#5E6165")
    employment = left.plot(frame.year, frame.employment_million, color="#2D3035", linewidth=1.55, label="BLS employment")[0]
    value_added = right.plot(frame.year, frame.real_value_added_billion, color="#A0A2A4", linewidth=1.7, label="BEA real value added")[0]
    left.set_xlim(frame.year.min() - 1.5, frame.year.max() + 1.5)
    left.set_ylim(9.7, 20.4)
    right.set_ylim(170, 1680)
    left.set_xticks([1948, 1958, 1968, 1978, 1988, 1998, 2008])
    left.set_yticks([10, 12, 14, 16, 18, 20])
    right.set_yticks([200, 400, 800, 1200, 1600])
    right.set_yticklabels(["200", "400", "800", "1,200", "1,600"])
    left.set_ylabel("Employment (million)", fontsize=11)
    right.set_ylabel("Real value added (billion)", fontsize=11, rotation=270, labelpad=18)
    left.legend([employment, value_added], [employment.get_label(), value_added.get_label()], loc="lower center", bbox_to_anchor=(0.57, 0.035), frameon=True, fancybox=False, edgecolor="#333333", fontsize=9.5, handlelength=3.1)
    return fig


def main() -> None:
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=directory / "dual-axis-employment-value-added.fixture.csv")
    parser.add_argument("--output-dir", type=Path, default=directory)
    parser.add_argument("--qa-preview", type=Path)
    args = parser.parse_args()
    print(save_outputs(render(args.data), args.output_dir, "dual-axis-employment-value-added", qa_preview=args.qa_preview))


if __name__ == "__main__":
    main()
