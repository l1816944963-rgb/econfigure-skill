"""Render a two-series grouped vertical bar chart from long-form data."""

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
from matplotlib.patches import Rectangle


@dataclass(frozen=True)
class ChartStyle:
    figure_size: tuple[float, float] = (5.25, 3.07)
    outer_bounds: tuple[float, float, float, float] = (
        28 / 525,
        9 / 307,
        468 / 525,
        287 / 307,
    )
    axes_bounds: tuple[float, float, float, float] = (
        64 / 525,
        61 / 307,
        420 / 525,
        225 / 307,
    )
    outer_color: str = "#EAF2F3"
    axes_color: str = "#FFFFFF"
    grid_color: str = "#EAF2F3"
    axis_color: str = "#333333"
    series_colors: tuple[str, str] = ("#E99833", "#1A476F")
    font_family: str | None = None
    font_size: float = 7.5
    legend_font_size: float = 8.0
    bar_width: float = 0.35
    series_offset: float = 0.19
    x_left_margin: float = 0.65
    x_right_margin: float = 0.67
    y_limits: tuple[float, float] = (0.0, 0.84)
    y_ticks: tuple[float, ...] = (0.0, 0.2, 0.4, 0.6, 0.8)


DEFAULT_STYLE = ChartStyle()
REQUIRED_COLUMNS = ("period", "series", "value")


def load_data(source: str | Path | pd.DataFrame) -> pd.DataFrame:
    if isinstance(source, pd.DataFrame):
        data = source.copy()
    else:
        data = pd.read_csv(source)

    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    data = data.loc[:, REQUIRED_COLUMNS].copy()
    data["value"] = pd.to_numeric(data["value"], errors="raise")
    if data.isna().any().any():
        raise ValueError("The chart data cannot contain missing values.")
    if (data["value"] < 0).any():
        raise ValueError("Grouped bars require a zero baseline and non-negative values.")
    if data.duplicated(["period", "series"]).any():
        raise ValueError("Each period-series pair must occur exactly once.")

    observed_series = tuple(data["series"].drop_duplicates())
    if len(observed_series) != 2:
        raise ValueError("This asset requires exactly two series.")

    counts = data.groupby("period", sort=False)["series"].nunique()
    if not (counts == 2).all():
        raise ValueError("Every period must contain both series.")
    return data


def _tick_label(value: float) -> str:
    if value == 0:
        return "0"
    return f"{value:.1f}".removeprefix("0")


def render(
    data: str | Path | pd.DataFrame,
    config: ChartStyle | None = None,
) -> Figure:
    """Build the figure without reading or writing any output path."""
    style = config or DEFAULT_STYLE
    frame = load_data(data)

    periods = list(dict.fromkeys(frame["period"].tolist()))
    series_order = tuple(frame["series"].drop_duplicates().tolist())
    values: Mapping[str, list[float]] = {
        series: [
            float(frame.loc[(frame["period"] == period) & (frame["series"] == series), "value"].iloc[0])
            for period in periods
        ]
        for series in series_order
    }

    fig = Figure(figsize=style.figure_size, facecolor="white")
    fig.add_artist(
        Rectangle(
            style.outer_bounds[:2],
            style.outer_bounds[2],
            style.outer_bounds[3],
            transform=fig.transFigure,
            facecolor=style.outer_color,
            edgecolor="none",
            zorder=-10,
        )
    )
    ax = fig.add_axes(style.axes_bounds, facecolor=style.axes_color)

    x = np.arange(len(periods), dtype=float)
    bars = []
    offsets = (-style.series_offset, style.series_offset)
    for series, offset, color in zip(series_order, offsets, style.series_colors):
        bars.append(
            ax.bar(
                x + offset,
                values[series],
                width=style.bar_width,
                color=color,
                edgecolor="none",
                linewidth=0,
                label=series,
                zorder=3,
            )
        )

    ax.set_xlim(-style.x_left_margin, len(periods) - 1 + style.x_right_margin)
    ax.set_ylim(*style.y_limits)
    ax.set_xticks(x, [str(period) for period in periods])
    ax.set_yticks(style.y_ticks, [_tick_label(value) for value in style.y_ticks])
    ax.yaxis.grid(True, color=style.grid_color, linewidth=0.65, zorder=0)
    ax.xaxis.grid(False)

    for name in ("top", "right"):
        ax.spines[name].set_visible(False)
    for name in ("left", "bottom"):
        ax.spines[name].set_color(style.axis_color)
        ax.spines[name].set_linewidth(0.7)

    ax.tick_params(axis="both", length=0, width=0, pad=3, colors="black")
    for label in (*ax.get_xticklabels(), *ax.get_yticklabels()):
        label.set_fontfamily(style.font_family)
        label.set_fontsize(style.font_size)

    fig.add_artist(
        Rectangle(
            (165 / 525, 23 / 307),
            218 / 525,
            19 / 307,
            transform=fig.transFigure,
            facecolor="white",
            edgecolor="#808080",
            linewidth=0.6,
            zorder=5,
        )
    )
    for left, color in zip((171, 275), style.series_colors):
        fig.add_artist(
            Rectangle(
                (left / 525, 27 / 307),
                43 / 525,
                9 / 307,
                transform=fig.transFigure,
                facecolor=color,
                edgecolor="none",
                zorder=6,
            )
        )
    for left, label in zip((220, 324), series_order):
        fig.text(
            left / 525,
            31.5 / 307,
            label,
            transform=fig.transFigure,
            ha="left",
            va="center",
            family=style.font_family,
            fontsize=style.legend_font_size,
            color="black",
            zorder=7,
        )
    return fig


def save_outputs(
    fig: Figure,
    output_dir: str | Path,
    stem: str,
    png_dpi: int = 600,
    qa_preview: str | Path | None = None,
) -> Path:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    png_path = destination / f"{stem}.png"
    fig.savefig(png_path, dpi=png_dpi, facecolor="white", bbox_inches=None)
    if qa_preview is not None:
        qa_path = Path(qa_preview)
        qa_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(qa_path, dpi=100, facecolor="white", bbox_inches=None)
    return png_path


def parse_args() -> argparse.Namespace:
    asset_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data",
        type=Path,
        default=asset_dir / "grouped-vbar-2series-year.fixture.csv",
    )
    parser.add_argument("--output-dir", type=Path, default=asset_dir)
    parser.add_argument("--png-dpi", type=int, default=600)
    parser.add_argument("--qa-preview", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    figure = render(args.data)
    output = save_outputs(
        figure,
        args.output_dir,
        "grouped-vbar-2series-year",
        png_dpi=args.png_dpi,
        qa_preview=args.qa_preview,
    )
    print(output)


if __name__ == "__main__":
    main()
