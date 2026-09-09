"""Render a grayscale historical stacked-area composition chart."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from matplotlib.figure import Figure
from matplotlib.patches import Patch

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
    columns = ("year", "year_order", "component", "component_order", "value")
    require_columns(data, columns)
    data = data.loc[:, columns].copy()
    require_finite(data, ("year", "year_order", "component_order", "value"))
    if data.duplicated(["year", "component"]).any():
        raise ValueError("Year-component keys must be unique.")
    if data["component"].nunique() != 5:
        raise ValueError("Exactly five components are required.")
    if not (data.groupby("year")["component"].nunique() == 5).all():
        raise ValueError("Every observation requires all five components.")
    if (data["value"] < 0).any():
        raise ValueError("Stacked-area values must be non-negative.")
    years = data.sort_values("year_order").drop_duplicates("year_order")
    if len(years) != 11 or not years["year_order"].is_monotonic_increasing:
        raise ValueError("Exactly eleven strictly ordered observations are required.")
    if not years["year"].is_monotonic_increasing:
        raise ValueError("Displayed years must increase with observation order.")
    return data


def render(source):
    data = load_data(source)
    fig = Figure(figsize=(7.20, 4.56), facecolor="white")
    ax = fig.add_axes((92 / 720, 43 / 456, 594 / 720, 395 / 456))
    style_axis(ax, full_spines=True)
    ax.set_axisbelow(True)
    ax.grid(True, axis="both", color="#8A8A8A", linewidth=.7)

    years = (
        data.sort_values("year_order")[["year", "year_order"]]
        .drop_duplicates("year_order")["year"]
        .astype(int)
        .tolist()
    )
    components = (
        data.sort_values("component_order")["component"].drop_duplicates().tolist()
    )
    x = np.arange(len(years))
    values = [
        np.array(
            [
                data[(data["year"] == year) & (data["component"] == component)][
                    "value"
                ].iloc[0]
                for year in years
            ]
        )
        for component in components
    ]
    colors = ["#050505", "#FFFFFF", "#C9C9C9", "#999999", "#FFFFFF"]
    hatches = [None, "\\\\\\\\", None, None, None]
    layers = ax.stackplot(
        x,
        *values,
        colors=colors,
        edgecolor="#171717",
        linewidth=1.15,
        zorder=2,
    )
    for layer, hatch in zip(layers, hatches):
        layer.set_hatch(hatch)

    ax.set_xlim(0, len(years) - 1)
    ax.set_ylim(0, 700)
    ax.set_xticks(x, years)
    ax.set_yticks(np.arange(0, 701, 100), [f"{value}%" for value in range(0, 701, 100)])
    ax.tick_params(axis="both", length=0, labelsize=10.5)
    ax.set_ylabel("% national income", fontsize=11)

    legend_order = [4, 3, 2, 1, 0]
    handles = [
        Patch(
            facecolor=colors[index],
            edgecolor="#171717",
            hatch=hatches[index],
            label=components[index],
        )
        for index in legend_order
    ]
    ax.legend(
        handles=handles,
        loc="upper right",
        bbox_to_anchor=(1.0, 1.0),
        frameon=True,
        fancybox=False,
        framealpha=1,
        edgecolor="#9A9A9A",
        fontsize=10.5,
        handlelength=.9,
        handleheight=.9,
        handletextpad=.35,
        labelspacing=.45,
        borderpad=.55,
        borderaxespad=0,
    )
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve().parent
    parser.add_argument(
        "--data",
        type=Path,
        default=here / "stacked-area-national-assets.fixture.csv",
    )
    parser.add_argument("--output-dir", type=Path, default=here)
    parser.add_argument("--qa-preview", type=Path)
    args = parser.parse_args()
    print(
        save_outputs(
            render(args.data),
            args.output_dir,
            "stacked-area-national-assets",
            qa_preview=args.qa_preview,
        )
    )


if __name__ == "__main__":
    main()
