"""Render two annual series on separate y axes with divergent trends."""

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
    figure_size: tuple[float, float] = (5.86, 3.36)
    axes_bounds: tuple[float, float, float, float] = (72 / 586, 51 / 336, 433 / 586, 271 / 336)
    left_color: str = "#0B477E"
    right_color: str = "#B13D3D"
    font_family: str | None = None


def load_data(source) -> pd.DataFrame:
    frame = read_frame(source)
    columns = ("year", "import_penetration", "manufacturing_emp_population")
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
    right.spines["right"].set_linewidth(0.7)
    first = left.plot(frame.year, frame.import_penetration, color=style.left_color, linewidth=1.45, label="China import penetration ratio")[0]
    second = right.plot(frame.year, frame.manufacturing_emp_population, color=style.right_color, linewidth=1.45, linestyle=(0, (4, 2.2)), label="Manufacturing employment/population")[0]
    left.set_xlim(frame.year.min() - 0.4, frame.year.max() + 0.4)
    left.set_ylim(-0.002, 0.052)
    right.set_ylim(0.078, 0.142)
    left.set_xticks(range(int(frame.year.min()), int(frame.year.max()) + 1, 2))
    left.set_yticks([0, .01, .02, .03, .04, .05])
    right.set_yticks([.08, .10, .12, .14])
    left.set_xlabel("Year", family=style.font_family, fontsize=10)
    left.set_ylabel("Import penetration", family=style.font_family, fontsize=10)
    right.set_ylabel("Manufacturing emp/pop", family=style.font_family, fontsize=10, rotation=270, labelpad=14)
    left.legend([first, second], [first.get_label(), second.get_label()], loc="upper center", bbox_to_anchor=(0.58, 0.98), frameon=True, fancybox=False, edgecolor="#333333", fontsize=8, handlelength=4.5)
    return fig


def main() -> None:
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=directory / "dual-axis-diverging-trends.fixture.csv")
    parser.add_argument("--output-dir", type=Path, default=directory)
    parser.add_argument("--qa-preview", type=Path)
    args = parser.parse_args()
    print(save_outputs(render(args.data), args.output_dir, "dual-axis-diverging-trends", qa_preview=args.qa_preview))


if __name__ == "__main__":
    main()
