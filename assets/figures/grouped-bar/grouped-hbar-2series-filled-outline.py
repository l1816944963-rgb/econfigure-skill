"""Render a two-series horizontal grouped bar chart with filled-outline encoding."""

from __future__ import annotations

import argparse
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MPL_CACHE = Path(os.environ.get("MPLCONFIGDIR") or (Path(tempfile.gettempdir()) / "econfigure-matplotlib"))
MPL_CACHE.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE))

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")

from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter


@dataclass(frozen=True)
class ChartStyle:
    figure_size: tuple[float, float] = (5.75, 3.40)
    axes_bounds: tuple[float, float, float, float] = (
        120 / 737,
        (436 - 359) / 436,
        (689 - 120) / 737,
        (359 - 9) / 436,
    )
    ink_color: str = "#2C2E35"
    axis_color: str = "#5F6166"
    font_family: str | None = None
    tick_font_size: float = 8.75
    legend_font_size: float = 8.00
    bar_height: float = 0.27
    series_offset: float = 0.135
    bar_edge_width: float = 0.60
    axis_width: float = 0.60
    tick_width: float = 0.60
    tick_length: float = 4.0
    x_tick_pad: float = 3.5
    y_tick_pad: float = 2.8
    x_limits: tuple[float, float] = (0.0, 0.6)
    x_tick_interval: float = 0.1
    legend_anchor: tuple[float, float] = (400 / 737, 9 / 436)
    legend_marker_size: float = 4.5
    legend_edge_width: float = 0.60
    legend_border_pad: float = 0.38
    legend_handle_text_pad: float = 0.58
    legend_column_spacing: float = 1.30


DEFAULT_STYLE = ChartStyle()
REQUIRED_COLUMNS = ("category", "series", "value", "category_order")


def load_data(source: str | Path | pd.DataFrame) -> pd.DataFrame:
    if isinstance(source, pd.DataFrame):
        data = source.copy()
    else:
        data = pd.read_csv(source)

    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    data = data.loc[:, REQUIRED_COLUMNS].copy()
    data["category"] = data["category"].astype(str)
    data["series"] = data["series"].astype(str)
    data["value"] = pd.to_numeric(data["value"], errors="raise")
    data["category_order"] = pd.to_numeric(
        data["category_order"], errors="raise"
    )

    if data.isna().any().any():
        raise ValueError("The chart data cannot contain missing values.")
    if not np.isfinite(data["value"]).all():
        raise ValueError("Bar values must be finite.")
    if (data["value"] < 0).any():
        raise ValueError("Grouped bars require a zero baseline and non-negative values.")
    if data.duplicated(["category", "series"]).any():
        raise ValueError("Each category-series pair must occur exactly once.")

    series_order = tuple(data["series"].drop_duplicates())
    if len(series_order) != 2:
        raise ValueError("This asset requires exactly two series.")

    category_count = data["category"].nunique()
    if category_count < 3:
        raise ValueError(
            "This two-series asset requires at least three categories to meet the "
            "six-information-cell rule."
        )

    counts = data.groupby("category", sort=False)["series"].nunique()
    if not (counts == 2).all():
        raise ValueError("Every category must contain both series.")

    order_counts = data.groupby("category", sort=False)["category_order"].nunique()
    if not (order_counts == 1).all():
        raise ValueError("Each category must have exactly one category_order value.")

    category_orders = data.drop_duplicates("category")["category_order"]
    if category_orders.duplicated().any():
        raise ValueError("category_order values must be unique across categories.")

    return data.sort_values(["category_order"], kind="stable").reset_index(drop=True)


def _tick_formatter(interval: float) -> FuncFormatter:
    decimals = max(0, int(np.ceil(-np.log10(interval)))) if interval < 1 else 0

    def format_tick(value: float, _position: float) -> str:
        if abs(value) < interval / 1000:
            return "0"
        return f"{value:.{decimals}f}"

    return FuncFormatter(format_tick)


def render(
    data: str | Path | pd.DataFrame,
    config: ChartStyle | None = None,
) -> Figure:
    """Build the figure without reading or writing any output path."""
    style = config or DEFAULT_STYLE
    frame = load_data(data)

    if style.x_limits[0] != 0:
        raise ValueError("Horizontal grouped bars must use a zero baseline.")
    if style.x_tick_interval <= 0:
        raise ValueError("x_tick_interval must be positive.")
    if frame["value"].max() > style.x_limits[1]:
        raise ValueError("The configured x-axis maximum is smaller than the data maximum.")

    categories = (
        frame.loc[:, ["category", "category_order"]]
        .drop_duplicates()
        .sort_values("category_order", kind="stable")["category"]
        .tolist()
    )
    series_order = tuple(frame["series"].drop_duplicates().tolist())
    values: Mapping[str, list[float]] = {
        series: [
            float(
                frame.loc[
                    (frame["category"] == category)
                    & (frame["series"] == series),
                    "value",
                ].iloc[0]
            )
            for category in categories
        ]
        for series in series_order
    }

    fig = Figure(figsize=style.figure_size, facecolor="white")
    ax = fig.add_axes(style.axes_bounds, facecolor="white")
    y = np.arange(len(categories), dtype=float)

    ax.barh(
        y - style.series_offset,
        values[series_order[0]],
        height=style.bar_height,
        color=style.ink_color,
        edgecolor="none",
        linewidth=0,
        zorder=3,
    )
    ax.barh(
        y + style.series_offset,
        values[series_order[1]],
        height=style.bar_height,
        color="white",
        edgecolor=style.ink_color,
        linewidth=style.bar_edge_width,
        zorder=2,
    )

    ax.set_xlim(*style.x_limits)
    ax.set_ylim(-0.5, len(categories) - 0.5)
    ax.invert_yaxis()
    display_categories = [category.replace("$", r"\$") for category in categories]
    ax.set_yticks(y, display_categories)
    ax.set_xticks(
        np.arange(
            style.x_limits[0],
            style.x_limits[1] + style.x_tick_interval / 2,
            style.x_tick_interval,
        )
    )
    ax.xaxis.set_major_formatter(_tick_formatter(style.x_tick_interval))
    ax.grid(False)

    for name in ("top", "right"):
        ax.spines[name].set_visible(False)
    for name in ("left", "bottom"):
        ax.spines[name].set_color(style.axis_color)
        ax.spines[name].set_linewidth(style.axis_width)

    ax.tick_params(
        axis="x",
        direction="out",
        length=style.tick_length,
        width=style.tick_width,
        pad=style.x_tick_pad,
        colors=style.axis_color,
    )
    ax.tick_params(
        axis="y",
        direction="out",
        length=style.tick_length,
        width=style.tick_width,
        pad=style.y_tick_pad,
        colors=style.axis_color,
    )
    for label in (*ax.get_xticklabels(), *ax.get_yticklabels()):
        label.set_fontfamily(style.font_family)
        label.set_fontsize(style.tick_font_size)
        label.set_color("black")

    legend_handles = [
        Line2D(
            [],
            [],
            linestyle="none",
            marker="s",
            markersize=style.legend_marker_size,
            markerfacecolor=style.ink_color,
            markeredgecolor=style.ink_color,
            markeredgewidth=style.legend_edge_width,
        ),
        Line2D(
            [],
            [],
            linestyle="none",
            marker="s",
            markersize=style.legend_marker_size,
            markerfacecolor="white",
            markeredgecolor=style.ink_color,
            markeredgewidth=style.legend_edge_width,
        ),
    ]
    legend = fig.legend(
        legend_handles,
        series_order,
        loc="lower center",
        bbox_to_anchor=style.legend_anchor,
        ncol=2,
        frameon=True,
        fancybox=False,
        borderpad=style.legend_border_pad,
        handlelength=0.8,
        handletextpad=style.legend_handle_text_pad,
        columnspacing=style.legend_column_spacing,
        fontsize=style.legend_font_size,
        borderaxespad=0,
    )
    legend.get_frame().set_facecolor("white")
    legend.get_frame().set_edgecolor(style.axis_color)
    legend.get_frame().set_linewidth(style.legend_edge_width)
    for text in legend.get_texts():
        text.set_fontfamily(style.font_family)
        text.set_color("black")

    return fig


def save_outputs(
    fig: Figure,
    output_dir: str | Path,
    stem: str,
    png_dpi: int = 600,
    qa_preview: str | Path | None = None,
    qa_dpi: float = 128.24,
) -> Path:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    png_path = destination / f"{stem}.png"
    fig.savefig(png_path, dpi=png_dpi, facecolor="white", bbox_inches=None)
    if qa_preview is not None:
        qa_path = Path(qa_preview)
        qa_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(qa_path, dpi=qa_dpi, facecolor="white", bbox_inches=None)
    return png_path


def parse_args() -> argparse.Namespace:
    asset_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data",
        type=Path,
        default=asset_dir / "grouped-hbar-2series-filled-outline.fixture.csv",
    )
    parser.add_argument("--output-dir", type=Path, default=asset_dir)
    parser.add_argument("--png-dpi", type=int, default=600)
    parser.add_argument("--qa-preview", type=Path)
    parser.add_argument("--qa-dpi", type=float, default=128.24)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    figure = render(args.data)
    output = save_outputs(
        figure,
        args.output_dir,
        "grouped-hbar-2series-filled-outline",
        png_dpi=args.png_dpi,
        qa_preview=args.qa_preview,
        qa_dpi=args.qa_dpi,
    )
    print(output)


if __name__ == "__main__":
    main()
