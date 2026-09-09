"""Render three grouped treatments with supplied errors and significance labels."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from matplotlib.figure import Figure
from matplotlib.ticker import FixedLocator

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from chartlib.asset_runtime import (  # noqa: E402
    read_frame,
    require_columns,
    require_finite,
    save_outputs,
    style_axis,
)


def load_data(source):
    data = read_frame(source)
    columns = (
        "treatment",
        "treatment_order",
        "group",
        "group_order",
        "estimate",
        "error",
        "display_label",
        "within_p",
    )
    require_columns(data, columns)
    data = data.loc[:, columns].copy()
    require_finite(data, ("treatment_order", "group_order", "estimate", "error"))
    if data.duplicated(["treatment", "group"]).any():
        raise ValueError("Treatment-group keys must be unique.")
    if set(data["treatment_order"]) != {1, 2, 3}:
        raise ValueError("Exactly three ordered treatments are required.")
    if set(data["group"]) != {"Private", "Public"}:
        raise ValueError("Exactly the Private and Public groups are required.")
    if not (data.groupby("treatment")["group"].nunique() == 2).all():
        raise ValueError("Every treatment must contain both groups.")
    if (data[["estimate", "error"]] < 0).any().any():
        raise ValueError("Estimates and supplied errors must be non-negative.")
    if data[["display_label", "within_p"]].isna().any().any():
        raise ValueError("Display and within-treatment significance labels are required.")
    return data


def _bracket(ax, start, end, y, label):
    stem = 1.25
    ax.plot(
        [start, start, end, end],
        [y - stem, y, y, y - stem],
        color="#222222",
        lw=1.1,
        clip_on=False,
        zorder=5,
    )
    ax.text(
        (start + end) / 2,
        y,
        label,
        ha="center",
        va="center",
        fontsize=11,
        zorder=6,
        bbox={"facecolor": "white", "edgecolor": "none", "boxstyle": "square,pad=0.05"},
    )


def render(source):
    data = load_data(source)
    fig = Figure(figsize=(7.18, 5.06), facecolor="white")
    ax = fig.add_axes((72 / 718, 42 / 506, 625 / 718, 443 / 506))
    style_axis(ax, grid=False)

    treatments = (
        data.sort_values("treatment_order")["treatment"].drop_duplicates().tolist()
    )
    centers = np.arange(len(treatments)) * 2.18
    offsets = {"Private": -.37, "Public": .37}
    styles = {
        "Private": {"facecolor": "#FFFFFF", "edgecolor": "#222222"},
        "Public": {"facecolor": "#C39A9D", "edgecolor": "#222222"},
    }

    for group in ["Private", "Public"]:
        part = data[data["group"] == group].sort_values("treatment_order")
        x = centers + offsets[group]
        bars = ax.bar(
            x,
            part["estimate"],
            width=.58,
            linewidth=1.1,
            label=group,
            zorder=2,
            **styles[group],
        )
        ax.errorbar(
            x,
            part["estimate"],
            yerr=part["error"],
            fmt="none",
            ecolor="#222222",
            elinewidth=1.25,
            capsize=3.5,
            zorder=4,
        )
        for bar, label in zip(bars, part["display_label"]):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                18.2,
                str(label),
                ha="center",
                va="center",
                fontsize=10.5,
                weight="bold",
            )

    for center, treatment in zip(centers, treatments):
        label = data[data["treatment"] == treatment]["within_p"].iloc[0]
        _bracket(
            ax,
            center + offsets["Private"],
            center + offsets["Public"],
            72.0,
            label,
        )

    _bracket(ax, centers[0] + offsets["Public"], centers[1] + offsets["Public"], 59.0, "P=0.089")
    _bracket(ax, centers[0] + offsets["Public"], centers[2] + offsets["Public"], 65.0, "P=0.060")

    ax.set_ylim(-2, 75)
    ax.set_yticks(np.arange(0, 71, 10))
    ax.set_ylabel("Donation Rates", fontsize=12)
    ax.set_xticks(centers, treatments, fontsize=10.5)
    half_step = (centers[1] - centers[0]) / 2
    boundaries = np.r_[centers[0] - half_step, (centers[:-1] + centers[1:]) / 2, centers[-1] + half_step]
    ax.set_xlim(boundaries[0], boundaries[-1])
    ax.tick_params(axis="both", labelsize=10.5)
    ax.tick_params(axis="x", which="major", length=0)
    ax.xaxis.set_minor_locator(FixedLocator(boundaries))
    ax.tick_params(axis="x", which="minor", bottom=True, top=False, direction="out", length=4.2, width=.8, color="#45484C")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(.68, .83),
        frameon=True,
        fancybox=False,
        edgecolor="#E2E7EA",
        fontsize=12,
        handlelength=1.15,
        handleheight=1.1,
        handletextpad=.5,
        borderpad=.55,
        labelspacing=.4,
    )
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve().parent
    parser.add_argument(
        "--data",
        type=Path,
        default=here / "grouped-vbar-errorbars-three-treatments.fixture.csv",
    )
    parser.add_argument("--output-dir", type=Path, default=here)
    parser.add_argument("--qa-preview", type=Path)
    args = parser.parse_args()
    print(
        save_outputs(
            render(args.data),
            args.output_dir,
            "grouped-vbar-errorbars-three-treatments",
            qa_preview=args.qa_preview,
        )
    )


if __name__ == "__main__":
    main()
