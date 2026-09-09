"""Render ordered sector changes as vertical bars below a zero baseline."""

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
    figure_size: tuple[float, float] = (6.99, 4.12)
    axes_bounds: tuple[float, float, float, float] = (125 / 699, 157 / 412, 513 / 699, 215 / 412)
    bar_color: str = "#999A9C"


def load_data(source) -> pd.DataFrame:
    frame = read_frame(source)
    columns = ("category", "order", "value")
    require_columns(frame, columns)
    frame = frame.loc[:, columns].copy()
    require_finite(frame, ("order", "value"))
    if frame.category.duplicated().any() or frame.order.duplicated().any():
        raise ValueError("Categories and order values must be unique.")
    if not (frame.value < 0).any():
        raise ValueError("This signed-change asset requires at least one negative value.")
    return frame.sort_values("order")


def render(data, config: ChartStyle | None = None) -> Figure:
    style = config or ChartStyle()
    frame = load_data(data)
    fig = Figure(figsize=style.figure_size, facecolor="white")
    ax = fig.add_axes(style.axes_bounds)
    style_axis(ax, grid=True)
    ax.bar(range(len(frame)), frame.value, color=style.bar_color, width=.66, zorder=2)
    ax.axhline(0, color="#A7AAAD", linewidth=.7)
    ax.set_ylim(-.325, .08)
    ax.set_yticks([-.25,-.20,-.15,-.10,-.05,0])
    ax.set_xticks(range(len(frame)), frame.category, rotation=48, ha="right", fontsize=8)
    ax.set_ylabel("Change in ln(1 + tariff), 1990–1995", fontsize=10)
    return fig


def main() -> None:
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=directory / "negative-bar-sector-change.fixture.csv")
    parser.add_argument("--output-dir", type=Path, default=directory)
    parser.add_argument("--qa-preview", type=Path)
    args = parser.parse_args()
    print(save_outputs(render(args.data), args.output_dir, "negative-bar-sector-change", qa_preview=args.qa_preview))


if __name__ == "__main__":
    main()
