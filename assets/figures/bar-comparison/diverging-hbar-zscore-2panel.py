"""Render two panels of signed category z-scores as horizontal bars."""

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
    figure_size: tuple[float, float] = (6.40, 2.58)
    color: str = "#164B7B"


def load_data(source) -> pd.DataFrame:
    frame = read_frame(source)
    columns = ("panel", "panel_order", "category", "category_order", "value")
    require_columns(frame, columns)
    frame = frame.loc[:, columns].copy()
    require_finite(frame, ("panel_order", "category_order", "value"))
    if frame.panel.nunique() != 2 or set(frame.panel_order) != {1, 2}:
        raise ValueError("This asset requires two ordered panels.")
    for panel, group in frame.groupby("panel", sort=False):
        if group.category.duplicated().any() or group.category_order.duplicated().any():
            raise ValueError(f"Panel {panel!r} category labels and orders must be unique.")
    return frame


def render(data, config: ChartStyle | None = None) -> Figure:
    style = config or ChartStyle()
    frame = load_data(data)
    fig = Figure(figsize=style.figure_size, facecolor="white")
    bounds = ((64/640, 28/258, 240/640, 177/258), (373/640, 28/258, 236/640, 177/258))
    titles = ("Panel A. People-management z-scores,\nall firms by country of location", "Panel B. People-management z-scores,\nmultinationals by country of origin")
    xlimits = ((-.53, .65), (-.23, .63))
    xticks = ((-.4,-.2,0,.2,.4,.6), (-.2,0,.2,.4,.6))
    for index, order in enumerate((1, 2)):
        ax = fig.add_axes(bounds[index])
        style_axis(ax, grid=True)
        group = frame.loc[frame.panel_order == order].sort_values("category_order", ascending=False)
        ax.barh(range(len(group)), group.value, color=style.color, height=.62, zorder=2)
        ax.axvline(0, color="#9AA0A4", linewidth=.7)
        ax.set_yticks(range(len(group)), group.category, fontsize=7.5)
        ax.set_xlim(*xlimits[index])
        ax.set_xticks(xticks[index])
        ax.set_title(titles[index], fontsize=8.5, loc="left", pad=9)
    return fig


def main() -> None:
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=directory / "diverging-hbar-zscore-2panel.fixture.csv")
    parser.add_argument("--output-dir", type=Path, default=directory)
    parser.add_argument("--qa-preview", type=Path)
    args = parser.parse_args()
    print(save_outputs(render(args.data), args.output_dir, "diverging-hbar-zscore-2panel", qa_preview=args.qa_preview))


if __name__ == "__main__":
    main()
