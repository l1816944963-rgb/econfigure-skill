"""Render two vertically stacked two-series trend panels from external data."""

from __future__ import annotations

import argparse
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
MPL_CACHE = Path(os.environ.get("MPLCONFIGDIR") or (Path(tempfile.gettempdir()) / "econfigure-matplotlib"))
MPL_CACHE.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE))

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")

from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter


@dataclass(frozen=True)
class ChartStyle:
    figure_size: tuple[float, float] = (5.75, 6.55)
    axes_bounds: tuple[tuple[float, float, float, float], ...] = (
        (72 / 456, (519 - 197) / 519, (414 - 72) / 456, (197 - 21) / 519),
        (73 / 456, (519 - 465) / 519, (413 - 73) / 456, (465 - 287) / 519),
    )
    series_colors: tuple[str, str] = ("#303030", "#686868")
    line_styles: tuple[str | tuple[int, tuple[float, ...]], ...] = (
        "-",
        (0, (4.5, 2.5)),
    )
    markers: tuple[str, str] = ("o", "D")
    font_family: str | None = None
    title_font_size: float = 9.0
    axis_label_font_size: float = 7.2
    tick_font_size: float = 6.4
    legend_font_size: float = 7.0
    line_width: float = 0.88
    marker_size: float = 2.7
    marker_edge_width: float = 0.55
    axis_color: str = "#707070"
    axis_width: float = 0.62
    reference_color: str = "#505050"
    reference_width: float = 0.75
    tick_length: float = 2.7
    tick_width: float = 0.50
    tick_pad: float = 2.0
    title_pad: float = 3.5
    y_label_pad: float = 3.0
    legend_y: tuple[float, float] = (278 / 519, 8 / 519)
    legend_handle_length: float = 3.7
    legend_column_spacing: float = 1.8
    x_limits: tuple[float, float] = (1962.0, 2006.0)
    x_ticks: tuple[int, ...] = (1963, 1969, 1975, 1981, 1987, 1993, 1999, 2005)


DEFAULT_STYLE = ChartStyle()
DATA_COLUMNS = ("panel", "year", "series", "series_order", "value")
PANEL_COLUMNS = (
    "panel",
    "panel_order",
    "title",
    "y_label",
    "y_min",
    "y_max",
    "y_tick_start",
    "y_tick_end",
    "y_tick_interval",
    "reference_x",
    "reference_y",
)


def _read_frame(source: str | Path | pd.DataFrame) -> pd.DataFrame:
    return source.copy() if isinstance(source, pd.DataFrame) else pd.read_csv(source)


def load_data(source: str | Path | pd.DataFrame) -> pd.DataFrame:
    data = _read_frame(source)
    missing = [column for column in DATA_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(f"Missing required data columns: {', '.join(missing)}")
    data = data.loc[:, DATA_COLUMNS].copy()
    for column in ("year", "series_order", "value"):
        data[column] = pd.to_numeric(data[column], errors="raise")
    if data.isna().any().any():
        raise ValueError("Trend data cannot contain missing values.")
    if not np.isfinite(data[["year", "series_order", "value"]]).all().all():
        raise ValueError("Trend values must be finite.")
    if data["panel"].nunique() != 2:
        raise ValueError("This asset requires exactly two panels.")
    if data.duplicated(["panel", "year", "series"]).any():
        raise ValueError("Each panel-year-series combination must be unique.")

    year_sets = []
    for panel, panel_data in data.groupby("panel", sort=False):
        if panel_data["series"].nunique() != 2:
            raise ValueError(f"Panel {panel!r} requires exactly two series.")
        orders = panel_data.loc[:, ["series", "series_order"]].drop_duplicates()
        if len(orders) != 2 or set(orders["series_order"]) != {1, 2}:
            raise ValueError(f"Panel {panel!r} must use unique series_order values 1 and 2.")
        counts = panel_data.groupby("year")["series"].nunique()
        if not (counts == 2).all():
            raise ValueError(f"Every year in panel {panel!r} must contain both series.")
        years = np.sort(panel_data["year"].unique().astype(float))
        if len(years) < 3:
            raise ValueError("Each panel requires at least three years.")
        if not np.allclose(np.diff(years), 1):
            raise ValueError("Annual trend data must contain continuous years.")
        year_sets.append(tuple(years))
    if year_sets[0] != year_sets[1]:
        raise ValueError("Both panels must contain the same annual periods.")
    return data


def load_panel_specs(source: str | Path | pd.DataFrame) -> pd.DataFrame:
    specs = _read_frame(source)
    missing = [column for column in PANEL_COLUMNS if column not in specs.columns]
    if missing:
        raise ValueError(f"Missing required panel columns: {', '.join(missing)}")
    specs = specs.loc[:, PANEL_COLUMNS].copy()
    for column in (
        "panel_order",
        "y_min",
        "y_max",
        "y_tick_start",
        "y_tick_end",
        "y_tick_interval",
    ):
        specs[column] = pd.to_numeric(specs[column], errors="raise")
    required = [column for column in PANEL_COLUMNS if column not in ("reference_x", "reference_y")]
    if specs[required].isna().any().any():
        raise ValueError("Required panel specifications cannot contain missing values.")
    if len(specs) != 2 or specs["panel"].nunique() != 2:
        raise ValueError("Panel specifications must contain exactly two unique panels.")
    if set(specs["panel_order"]) != {1, 2}:
        raise ValueError("panel_order must contain 1 and 2.")
    if (specs["y_min"] >= specs["y_max"]).any():
        raise ValueError("Every panel requires y_min < y_max.")
    if (specs["y_tick_interval"] <= 0).any():
        raise ValueError("Every y_tick_interval must be positive.")
    return specs.sort_values("panel_order", kind="stable").reset_index(drop=True)


def _display_tick(value: float, _position: float | None = None) -> str:
    if abs(value) < 1e-10:
        return "0"
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    if text.startswith("-0."):
        return f"-{text[2:]}"
    if text.startswith("0."):
        return text[1:]
    return text


def _reference_values(value: object) -> tuple[float, ...]:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return ()
    text = str(value).strip()
    if not text:
        return ()
    return tuple(float(item.strip()) for item in text.split(";") if item.strip())


def render(
    data: str | Path | pd.DataFrame,
    panel_specs: str | Path | pd.DataFrame,
    config: ChartStyle | None = None,
) -> Figure:
    """Build the figure without performing analytical calculations or file output."""
    style = config or DEFAULT_STYLE
    frame = load_data(data)
    specs = load_panel_specs(panel_specs)
    if set(frame["panel"]) != set(specs["panel"]):
        raise ValueError("Data panels and panel specifications must match exactly.")

    fig = Figure(figsize=style.figure_size, facecolor="white")
    for panel_index, (bounds, spec) in enumerate(
        zip(style.axes_bounds, specs.itertuples(index=False))
    ):
        panel = frame.loc[frame["panel"] == spec.panel].copy()
        if panel["value"].min() < spec.y_min or panel["value"].max() > spec.y_max:
            raise ValueError(f"Panel {spec.panel!r} values exceed its configured y limits.")

        ax = fig.add_axes(bounds, facecolor="white")
        series_meta = (
            panel.loc[:, ["series", "series_order"]]
            .drop_duplicates()
            .sort_values("series_order", kind="stable")
        )
        handles = []
        labels = []
        for style_index, series in enumerate(series_meta["series"]):
            series_data = panel.loc[panel["series"] == series].sort_values(
                "year", kind="stable"
            )
            line = ax.plot(
                series_data["year"],
                series_data["value"],
                color=style.series_colors[style_index],
                linewidth=style.line_width,
                linestyle=style.line_styles[style_index],
                marker=style.markers[style_index],
                markersize=style.marker_size,
                markerfacecolor="white",
                markeredgecolor=style.series_colors[style_index],
                markeredgewidth=style.marker_edge_width,
                zorder=3,
            )[0]
            handles.append(line)
            labels.append(str(series))

        for x_value in _reference_values(spec.reference_x):
            if not style.x_limits[0] <= x_value <= style.x_limits[1]:
                raise ValueError(f"Reference year {x_value:g} lies outside the x limits.")
            ax.axvline(
                x_value,
                color=style.reference_color,
                linewidth=style.reference_width,
                zorder=1,
            )
        for y_value in _reference_values(spec.reference_y):
            if not spec.y_min <= y_value <= spec.y_max:
                raise ValueError(f"Reference value {y_value:g} lies outside the y limits.")
            ax.axhline(
                y_value,
                color=style.reference_color,
                linewidth=style.reference_width,
                zorder=1,
            )

        ax.set_xlim(*style.x_limits)
        ax.set_ylim(float(spec.y_min), float(spec.y_max))
        ax.set_xticks(style.x_ticks)
        ax.set_yticks(
            np.arange(
                spec.y_tick_start,
                spec.y_tick_end + spec.y_tick_interval / 2,
                spec.y_tick_interval,
            )
        )
        ax.yaxis.set_major_formatter(FuncFormatter(_display_tick))
        ax.grid(False)
        for spine in ax.spines.values():
            spine.set_color(style.axis_color)
            spine.set_linewidth(style.axis_width)
        ax.tick_params(
            axis="both",
            direction="out",
            length=style.tick_length,
            width=style.tick_width,
            pad=style.tick_pad,
            colors=style.axis_color,
        )
        for label in (*ax.get_xticklabels(), *ax.get_yticklabels()):
            label.set_fontfamily(style.font_family)
            label.set_fontsize(style.tick_font_size)
            label.set_color("black")
        ax.set_ylabel(
            str(spec.y_label),
            family=style.font_family,
            fontsize=style.axis_label_font_size,
            labelpad=style.y_label_pad,
            color="black",
        )
        ax.set_title(
            str(spec.title),
            family=style.font_family,
            fontsize=style.title_font_size,
            fontweight="bold",
            pad=style.title_pad,
            color="black",
        )
        legend = fig.legend(
            handles,
            labels,
            loc="lower center",
            bbox_to_anchor=(0.535, style.legend_y[panel_index]),
            ncol=2,
            frameon=False,
            fontsize=style.legend_font_size,
            handlelength=style.legend_handle_length,
            handletextpad=0.65,
            columnspacing=style.legend_column_spacing,
            borderaxespad=0,
        )
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
    qa_dpi: float = 79.31,
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
        default=asset_dir / "dual-series-trend-prediction-2panel.fixture.csv",
    )
    parser.add_argument(
        "--panels",
        type=Path,
        default=asset_dir / "dual-series-trend-prediction-2panel.panels.csv",
    )
    parser.add_argument("--output-dir", type=Path, default=asset_dir)
    parser.add_argument("--png-dpi", type=int, default=600)
    parser.add_argument("--qa-preview", type=Path)
    parser.add_argument("--qa-dpi", type=float, default=79.31)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    figure = render(args.data, args.panels)
    output = save_outputs(
        figure,
        args.output_dir,
        "dual-series-trend-prediction-2panel",
        png_dpi=args.png_dpi,
        qa_preview=args.qa_preview,
        qa_dpi=args.qa_dpi,
    )
    print(output)


if __name__ == "__main__":
    main()
