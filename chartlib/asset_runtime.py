"""Deterministic utilities shared by executable figure assets."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MPL_CACHE = Path(os.environ.get("MPLCONFIGDIR") or (Path(tempfile.gettempdir()) / "econfigure-matplotlib"))
MPL_CACHE.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE))

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")

from matplotlib.figure import Figure


def read_frame(source: str | Path | pd.DataFrame) -> pd.DataFrame:
    """Return an isolated data frame from a path or caller-supplied frame."""
    return source.copy() if isinstance(source, pd.DataFrame) else pd.read_csv(source)


def require_columns(frame: pd.DataFrame, columns: tuple[str, ...]) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")


def require_finite(frame: pd.DataFrame, columns: tuple[str, ...]) -> None:
    for column in columns:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    if frame[list(columns)].isna().any().any():
        raise ValueError("Numeric plotting values cannot be missing.")
    if not np.isfinite(frame[list(columns)]).all().all():
        raise ValueError("Numeric plotting values must be finite.")


def require_continuous_years(values: pd.Series) -> None:
    years = np.sort(pd.to_numeric(values, errors="raise").unique())
    if len(years) < 3 or not np.allclose(np.diff(years), 1):
        raise ValueError("Annual trend data must contain at least three continuous years.")


def save_outputs(
    fig: Figure,
    output_dir: str | Path,
    stem: str,
    png_dpi: int = 600,
    qa_preview: str | Path | None = None,
    qa_dpi: float = 100.0,
) -> Path:
    """Write one production PNG and an optional QA preview."""
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    png_path = destination / f"{stem}.png"
    fig.savefig(png_path, dpi=png_dpi, facecolor="white", bbox_inches=None)
    if qa_preview is not None:
        qa_path = Path(qa_preview)
        qa_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(qa_path, dpi=qa_dpi, facecolor="white", bbox_inches=None)
    return png_path


def style_axis(ax, *, grid: bool = False, full_spines: bool = False) -> None:
    """Apply the neutral publication axis used by approved assets."""
    ax.set_facecolor("white")
    if grid:
        ax.grid(True, axis="y", color="#D7DADD", linewidth=0.65, zorder=0)
    else:
        ax.grid(False)
    ax.tick_params(axis="both", direction="out", length=3.0, width=0.65, labelsize=8)
    for side, spine in ax.spines.items():
        spine.set_visible(full_spines or side in ("left", "bottom"))
        spine.set_color("#5E6165")
        spine.set_linewidth(0.7)
