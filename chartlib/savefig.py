"""Shared PNG export and grayscale-preview utilities.

Responsibilities:
1. Load the shared base and figure styles.
2. Export one 600 dpi PNG.
3. Create a grayscale QA preview.
4. Print the post-render review checklist.
"""
from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

HERE = os.path.dirname(os.path.abspath(__file__))
STYLES_DIR = os.path.join(os.path.dirname(HERE), "styles")

CHECKLIST = [
    "Figure title, number, caption, and notes remain outside the PNG",
    "Axis labels identify variables and applicable units",
    "Typography follows the approved target document and insertion size",
    "Critical series use redundant encoding where needed",
    "Bar zero baselines and annual time continuity have been verified",
    "Data labels are numeric, necessary, accurate, and non-overlapping",
]


def use_style() -> None:
    """Apply the econfigure base and figure styles."""
    plt.style.use(
        [
            os.path.join(STYLES_DIR, "base.mplstyle"),
            os.path.join(STYLES_DIR, "figure.mplstyle"),
        ]
    )


def grayscale_of(png_path: str) -> None:
    """Create a grayscale PNG for QA only."""
    img = mpimg.imread(png_path)
    if img.ndim == 3:
        gray = 0.299 * img[..., 0] + 0.587 * img[..., 1] + 0.114 * img[..., 2]
        img = gray
    out = png_path.rsplit(".", 1)[0] + "_gray.png"
    mpimg.imsave(out, img, cmap="gray", dpi=600)
    return out


def save_figure(
    fig: Figure,
    name: str,
    out_dir: str,
    dpi: int = 600,
    grayscale_check: bool = True,
) -> dict[str, str | None]:
    """Export one 600 dpi PNG and an optional grayscale QA preview."""
    os.makedirs(out_dir, exist_ok=True)
    # Remove an attached interactive toolbar before writing a static image.
    mgr = getattr(fig.canvas, "manager", None)
    if mgr is not None:
        try:
            mgr.toolbar = None
        except Exception:
            pass
        fig.canvas.manager = None
    png_path = os.path.join(out_dir, name + ".png")
    fig.savefig(png_path, dpi=dpi)
    plt.close(fig)
    gray_path = None
    if grayscale_check:
        gray_path = grayscale_of(png_path)
    print("OUTPUT")
    print(f"  PNG ({dpi} dpi): {png_path}")
    if gray_path:
        print(f"  Grayscale QA preview: {gray_path}")
    print("POST-RENDER REVIEW")
    for item in CHECKLIST:
        print(f"  [ ] {item}")
    return {"png": png_path, "gray": gray_path}
