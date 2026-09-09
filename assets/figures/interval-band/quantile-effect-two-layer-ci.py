"""Render a quantile-effect line with nested supplied confidence bands."""

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
    figure_size: tuple[float, float] = (5.38, 3.47)
    axes_bounds: tuple[float, float, float, float] = (78 / 538, 57 / 347, 412 / 538, 267 / 347)


def load_data(source) -> pd.DataFrame:
    frame = read_frame(source)
    columns = ("quantile", "estimate", "inner_lower", "inner_upper", "outer_lower", "outer_upper")
    require_columns(frame, columns)
    frame = frame.loc[:, columns].copy()
    require_finite(frame, columns)
    if frame["quantile"].duplicated().any() or not frame["quantile"].is_monotonic_increasing:
        raise ValueError("Quantiles must be unique and increasing.")
    if (frame.outer_lower > frame.inner_lower).any() or (frame.inner_lower > frame.estimate).any() or (frame.estimate > frame.inner_upper).any() or (frame.inner_upper > frame.outer_upper).any():
        raise ValueError("Nested interval order must be outer lower <= inner lower <= estimate <= inner upper <= outer upper.")
    return frame


def render(data, config: ChartStyle | None = None) -> Figure:
    style = config or ChartStyle()
    frame = load_data(data)
    fig = Figure(figsize=style.figure_size, facecolor="white")
    ax = fig.add_axes(style.axes_bounds)
    style_axis(ax)
    ax.fill_between(frame["quantile"], frame.outer_lower, frame.outer_upper, color="#EEDCDE", linewidth=0)
    ax.fill_between(frame["quantile"], frame.inner_lower, frame.inner_upper, color="#D5B2B5", linewidth=0)
    ax.plot(frame["quantile"], frame.estimate, color="#973238", linewidth=1.35)
    ax.axhline(0, color="#383838", linewidth=.85)
    ax.set_xlim(4.3, 50.7)
    ax.set_ylim(-.55, 1.05)
    ax.set_xticks([5,10,15,20,25,30,35,40,45,50])
    ax.set_yticks([-.5,0,.5,1])
    ax.set_title("Long-run (3+ year lagged) effects", fontsize=9.5, pad=6)
    ax.set_xlabel("Family income quantile", fontsize=9.5)
    ax.set_ylabel("Minimum wage elasticity", fontsize=9.5)
    return fig


def main() -> None:
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=directory / "quantile-effect-two-layer-ci.fixture.csv")
    parser.add_argument("--output-dir", type=Path, default=directory)
    parser.add_argument("--qa-preview", type=Path)
    args = parser.parse_args()
    print(save_outputs(render(args.data), args.output_dir, "quantile-effect-two-layer-ci", qa_preview=args.qa_preview))


if __name__ == "__main__":
    main()
