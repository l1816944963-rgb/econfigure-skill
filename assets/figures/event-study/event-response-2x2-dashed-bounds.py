"""Render a four-panel event-response figure with dashed interval bounds."""

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
    figure_size: tuple[float, float] = (6.10, 3.76)
    axes_bounds: tuple[tuple[float, float, float, float], ...] = (
        (54 / 571, (352 - 132) / 352, (258 - 54) / 571, (132 - 27) / 352),
        (323 / 571, (352 - 132) / 352, (527 - 323) / 571, (132 - 27) / 352),
        (54 / 571, (352 - 309) / 352, (258 - 54) / 571, (309 - 198) / 352),
        (323 / 571, (352 - 309) / 352, (527 - 323) / 571, (309 - 198) / 352),
    )
    estimate_color: str = "#000000"
    interval_color: str = "#203055"
    grid_color: str = "#DFDFDF"
    reference_color: str = "#B8B8B8"
    axis_color: str = "#A8A8A8"
    font_family: str | None = None
    title_font_size: float = 7.5
    axis_label_font_size: float = 7.0
    tick_font_size: float = 6.0
    estimate_width: float = 0.72
    interval_width: float = 0.68
    interval_dash: tuple[float, float] = (6.0, 4.0)
    marker_size: float = 2.5
    marker_edge_width: float = 0.35
    grid_width: float = 0.45
    reference_width: float = 0.65
    axis_width: float = 0.50
    tick_width: float = 0.45
    tick_length: float = 2.5
    title_pad: float = 6.5
    x_label_pad: float = 2.0
    y_label_pad: float = 3.0


DEFAULT_STYLE = ChartStyle()
DATA_COLUMNS = ("panel", "period", "period_label", "estimate", "lower", "upper")
PANEL_COLUMNS = (
    "panel",
    "panel_order",
    "title",
    "y_min",
    "y_max",
    "y_tick_interval",
)


def _read_frame(source: str | Path | pd.DataFrame) -> pd.DataFrame:
    return source.copy() if isinstance(source, pd.DataFrame) else pd.read_csv(source)


def load_data(source: str | Path | pd.DataFrame) -> pd.DataFrame:
    data = _read_frame(source)
    missing = [column for column in DATA_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(f"Missing required data columns: {', '.join(missing)}")
    data = data.loc[:, DATA_COLUMNS].copy()
    for column in ("period", "estimate", "lower", "upper"):
        data[column] = pd.to_numeric(data[column], errors="raise")
    if data.isna().any().any():
        raise ValueError("Event-response data cannot contain missing values.")
    if not np.isfinite(data[["period", "estimate", "lower", "upper"]]).all().all():
        raise ValueError("Event-response values must be finite.")
    if (data["lower"] > data["estimate"]).any() or (
        data["estimate"] > data["upper"]
    ).any():
        raise ValueError("Every row must satisfy lower <= estimate <= upper.")
    if data.duplicated(["panel", "period"]).any():
        raise ValueError("Each panel-period pair must occur exactly once.")
    if data["panel"].nunique() != 4:
        raise ValueError("This asset requires exactly four panels.")

    period_sets = [
        tuple(group.sort_values("period")["period"])
        for _, group in data.groupby("panel", sort=False)
    ]
    if any(periods != period_sets[0] for periods in period_sets[1:]):
        raise ValueError("Every panel must contain the same ordered periods.")
    periods = np.asarray(period_sets[0], dtype=float)
    if len(periods) < 3:
        raise ValueError("Each panel requires at least three periods.")
    if not np.allclose(np.diff(periods), 1):
        raise ValueError("Event periods must form a continuous integer sequence.")
    if 0 not in periods:
        raise ValueError("The event period 0 must be present.")
    return data


def load_panel_specs(source: str | Path | pd.DataFrame) -> pd.DataFrame:
    specs = _read_frame(source)
    missing = [column for column in PANEL_COLUMNS if column not in specs.columns]
    if missing:
        raise ValueError(f"Missing required panel columns: {', '.join(missing)}")
    specs = specs.loc[:, PANEL_COLUMNS].copy()
    for column in ("panel_order", "y_min", "y_max", "y_tick_interval"):
        specs[column] = pd.to_numeric(specs[column], errors="raise")
    if specs.isna().any().any():
        raise ValueError("Panel specifications cannot contain missing values.")
    if len(specs) != 4 or specs["panel"].nunique() != 4:
        raise ValueError("Panel specifications must contain exactly four unique panels.")
    if set(specs["panel_order"]) != {1, 2, 3, 4}:
        raise ValueError("panel_order must contain the integers 1 through 4.")
    if (specs["y_min"] >= specs["y_max"]).any():
        raise ValueError("Every panel requires y_min < y_max.")
    if (specs["y_tick_interval"] <= 0).any():
        raise ValueError("Every y_tick_interval must be positive.")
    return specs.sort_values("panel_order", kind="stable").reset_index(drop=True)


def _display_tick(value: float, _position: float | None = None) -> str:
    if abs(value) < 1e-10:
        return "0"
    if np.isclose(value, round(value)):
        return str(int(round(value)))
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    if text.startswith("-0."):
        return f"-{text[2:]}"
    if text.startswith("0."):
        return text[1:]
    return text


def render(
    data: str | Path | pd.DataFrame,
    panel_specs: str | Path | pd.DataFrame,
    config: ChartStyle | None = None,
) -> Figure:
    """Build the figure without reading or writing any output path."""
    style = config or DEFAULT_STYLE
    frame = load_data(data)
    specs = load_panel_specs(panel_specs)
    if set(frame["panel"]) != set(specs["panel"]):
        raise ValueError("Data panels and panel specifications must match exactly.")

    fig = Figure(figsize=style.figure_size, facecolor="white")
    for bounds, spec in zip(style.axes_bounds, specs.itertuples(index=False)):
        panel = frame.loc[frame["panel"] == spec.panel].sort_values(
            "period", kind="stable"
        )
        x = panel["period"].to_numpy(dtype=float)
        estimate = panel["estimate"].to_numpy(dtype=float)
        lower = panel["lower"].to_numpy(dtype=float)
        upper = panel["upper"].to_numpy(dtype=float)

        if lower.min() < spec.y_min or upper.max() > spec.y_max:
            raise ValueError(f"Panel {spec.panel!r} values exceed its configured y limits.")

        ax = fig.add_axes(bounds, facecolor="white")
        ax.set_axisbelow(True)
        ax.grid(
            True,
            axis="both",
            color=style.grid_color,
            linewidth=style.grid_width,
            linestyle=(0, (1.0, 2.0)),
        )
        ax.axhline(
            0,
            color=style.reference_color,
            linewidth=style.reference_width,
            linestyle=(0, (3.0, 2.5)),
            zorder=1,
        )
        ax.axvline(
            0,
            color=style.reference_color,
            linewidth=style.reference_width,
            linestyle=(0, (3.0, 2.5)),
            zorder=1,
        )
        for bound in (lower, upper):
            line = ax.plot(
                x,
                bound,
                color=style.interval_color,
                linewidth=style.interval_width,
                zorder=2,
            )[0]
            line.set_dashes(style.interval_dash)
        ax.plot(
            x,
            estimate,
            color=style.estimate_color,
            linewidth=style.estimate_width,
            marker="o",
            markersize=style.marker_size,
            markerfacecolor=style.estimate_color,
            markeredgecolor=style.estimate_color,
            markeredgewidth=style.marker_edge_width,
            zorder=3,
        )

        ax.set_xlim(float(x.min()) - 0.15, float(x.max()) + 0.15)
        ax.set_ylim(float(spec.y_min), float(spec.y_max))
        ax.set_xticks(x, panel["period_label"].astype(str).tolist())
        first_tick = np.ceil(spec.y_min / spec.y_tick_interval) * spec.y_tick_interval
        ax.set_yticks(
            np.arange(
                first_tick,
                spec.y_max + spec.y_tick_interval / 2,
                spec.y_tick_interval,
            )
        )
        ax.yaxis.set_major_formatter(FuncFormatter(_display_tick))

        for name in ("top", "right"):
            ax.spines[name].set_visible(False)
        for name in ("left", "bottom"):
            ax.spines[name].set_color(style.axis_color)
            ax.spines[name].set_linewidth(style.axis_width)
        ax.tick_params(
            axis="both",
            direction="out",
            length=style.tick_length,
            width=style.tick_width,
            pad=1.8,
            colors=style.axis_color,
        )
        for label in (*ax.get_xticklabels(), *ax.get_yticklabels()):
            label.set_fontfamily(style.font_family)
            label.set_fontsize(style.tick_font_size)
            label.set_color("black")

        ax.set_title(
            str(spec.title),
            family=style.font_family,
            fontsize=style.title_font_size,
            fontweight="normal",
            pad=style.title_pad,
            color="black",
        )
        ax.set_xlabel(
            "Months Relative to Tariff Increase",
            family=style.font_family,
            fontsize=style.axis_label_font_size,
            labelpad=style.x_label_pad,
            color="black",
        )
        ax.set_ylabel(
            "Percent",
            family=style.font_family,
            fontsize=style.axis_label_font_size,
            labelpad=style.y_label_pad,
            color="black",
        )
    return fig


def save_outputs(
    fig: Figure,
    output_dir: str | Path,
    stem: str,
    png_dpi: int = 600,
    qa_preview: str | Path | None = None,
    qa_dpi: float = 93.62,
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
        default=asset_dir / "event-response-2x2-dashed-bounds.fixture.csv",
    )
    parser.add_argument(
        "--panels",
        type=Path,
        default=asset_dir / "event-response-2x2-dashed-bounds.panels.csv",
    )
    parser.add_argument("--output-dir", type=Path, default=asset_dir)
    parser.add_argument("--png-dpi", type=int, default=600)
    parser.add_argument("--qa-preview", type=Path)
    parser.add_argument("--qa-dpi", type=float, default=93.62)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    figure = render(args.data, args.panels)
    output = save_outputs(
        figure,
        args.output_dir,
        "event-response-2x2-dashed-bounds",
        png_dpi=args.png_dpi,
        qa_preview=args.qa_preview,
        qa_dpi=args.qa_dpi,
    )
    print(output)


if __name__ == "__main__":
    main()
