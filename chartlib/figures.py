"""Core figure functions with hard validation and redundant encodings.

The module covers trends, ranked bars, grouped bars, stacked bars, scatter
plots, box plots, coefficient plots, histograms, and kernel-density overlays.
It rejects truncated bar axes, incomplete annual sequences, missing confidence
intervals, fewer than six information cells, and more than six unsplit lines.
"""
from __future__ import annotations

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from .savefig import use_style

LINESTYLES = ["-", "--", ":", "-."]
MARKERS = ["o", "s", "^", "D", "v"]
BASE_COLORS = ["#000000", "#404040", "#7F7F7F", "#A6A6A6", "#CCCCCC"]


def _style(idx: int):
    """Return color, line-style, and marker encodings for one series."""
    c = BASE_COLORS[idx % len(BASE_COLORS)]
    ls = LINESTYLES[(idx // len(BASE_COLORS)) % len(LINESTYLES)]
    m = MARKERS[idx % len(MARKERS)]
    return dict(color=c, linestyle=ls, marker=m, fillstyle="none")


def _new_fig_ax():
    """Create a figure without a pyplot manager or interactive toolbar."""
    fig = Figure(figsize=(3.5, 2.6), dpi=100)
    ax = fig.add_subplot(111)
    return fig, ax


# ------------------------------------------------------------- validation ----
def _require_min_info(df: pd.DataFrame) -> None:
    if df.shape[0] * df.shape[1] < 6:
        raise ValueError("Fewer than six information cells; use a table or prose instead.")


def _require_complete_years(df: pd.DataFrame, x_col: str) -> None:
    s = pd.to_numeric(df[x_col], errors="coerce")
    if s.isna().any():
        raise ValueError(f"Time column {x_col} contains non-numeric values.")
    vals = sorted(s.unique())
    gaps = [a for a, b in zip(vals, vals[1:]) if b - a != 1]
    if gaps:
        raise ValueError(f"Annual periods are incomplete near {gaps[0]}; add missing periods or change the chart.")


def _require_cols(df: pd.DataFrame, cols: list[str]) -> None:
    miss = [c for c in cols if c not in df.columns]
    if miss:
        raise ValueError(f"Missing required columns: {miss}")


# ------------------------------------------------------------------ lines ----
def line_trend(
    df: pd.DataFrame,
    x_col: str = "year",
    y_cols: list[str] | None = None,
    xlabel: str = "",
    ylabel: str = "",
    data_labels: bool = False,
) -> plt.Figure:
    """Render up to six series over a complete annual time axis."""
    _require_min_info(df)
    _require_complete_years(df, x_col)
    y_cols = y_cols or [c for c in df.columns if c != x_col]
    if len(y_cols) > 6:
        raise ValueError(f"The line chart has {len(y_cols)} series; split it or keep no more than six.")
    use_style()
    fig, ax = _new_fig_ax()
    for i, y in enumerate(y_cols):
        st = _style(i)
        ax.plot(df[x_col], df[y], label=str(y), linewidth=0.9, **st)
        if data_labels:
            for xi, yi in zip(df[x_col], df[y]):
                ax.annotate(f"{yi:g}", (xi, yi), textcoords="offset points",
                            xytext=(0, 4), ha="center", fontsize=6)
    ax.set_xlabel(xlabel or str(x_col))
    ax.set_ylabel(ylabel)
    ax.legend(loc="best", ncol=1)
    return fig


# ------------------------------------------------------------------- bars ----
def bar_compare(
    df: pd.DataFrame,
    label_col: str,
    value_col: str,
    horizontal: bool = False,
    xlabel: str = "",
    ylabel: str = "",
    data_labels: bool = True,
) -> plt.Figure:
    """Render sorted comparison bars with a mandatory zero baseline."""
    _require_min_info(df)
    _require_cols(df, [label_col, value_col])
    d = df.sort_values(value_col, ascending=horizontal).reset_index(drop=True)
    use_style()
    fig, ax = _new_fig_ax()
    if horizontal:
        ax.barh(d[label_col], d[value_col], color=BASE_COLORS[0])
        if data_labels:
            for i, v in enumerate(d[value_col]):
                ax.text(v, i, f"{v:g}", va="center", ha="left", fontsize=6, color="#404040")
        ax.set_ylabel(xlabel or str(label_col))
        ax.set_xlabel(ylabel or str(value_col))
    else:
        ax.bar(d[label_col], d[value_col], color=BASE_COLORS[0])
        if data_labels:
            for i, v in enumerate(d[value_col]):
                ax.text(i, v, f"{v:g}", ha="center", va="bottom", fontsize=6, color="#404040")
        ax.set_xlabel(xlabel or str(label_col))
        ax.set_ylabel(ylabel or str(value_col))
    ax.set_ylim(bottom=0)
    ax.tick_params(axis="x", labelrotation=30 if not horizontal else 0)
    return fig


def grouped_bar(
    df: pd.DataFrame,
    x_col: str,
    group_col: str,
    value_col: str,
    xlabel: str = "",
    ylabel: str = "",
) -> plt.Figure:
    """Render side-by-side bars for up to four groups and four x categories."""
    _require_min_info(df)
    _require_cols(df, [x_col, group_col, value_col])
    cats = list(dict.fromkeys(df[group_col]))
    if len(cats) > 4:
        raise ValueError(f"The chart has {len(cats)} groups; split it at more than four.")
    xs = list(dict.fromkeys(df[x_col]))
    if len(xs) > 4:
        raise ValueError(f"The chart has {len(xs)} x categories; split it at more than four.")
    use_style()
    fig, ax = _new_fig_ax()
    width = 0.8 / len(cats)
    for i, g in enumerate(cats):
        sub = df[df[group_col] == g].set_index(x_col).reindex(xs)
        vals = sub[value_col].fillna(0)
        ax.bar(np.arange(len(xs)) + (i - len(cats) / 2 + 0.5) * width, vals,
               width=width, label=str(g), color=BASE_COLORS[i % len(BASE_COLORS)],
               edgecolor="white", linewidth=0.3)
    ax.set_xticks(range(len(xs)), xs)
    ax.set_ylim(bottom=0)
    ax.set_xlabel(xlabel or str(x_col))
    ax.set_ylabel(ylabel or str(value_col))
    ax.legend(loc="best")
    return fig


def stacked_bar(
    df: pd.DataFrame,
    x_col: str,
    group_col: str,
    value_col: str,
    xlabel: str = "",
    ylabel: str = "",
) -> plt.Figure:
    """Render composition over time or categories with no more than five layers."""
    _require_min_info(df)
    _require_cols(df, [x_col, group_col, value_col])
    cats = list(dict.fromkeys(df[group_col]))
    if len(cats) > 5:
        raise ValueError(f"The stack has {len(cats)} layers; combine minor categories above five.")
    xs = list(dict.fromkeys(df[x_col]))
    use_style()
    fig, ax = _new_fig_ax()
    bottom = np.zeros(len(xs))
    for i, g in enumerate(cats):
        sub = df[df[group_col] == g].set_index(x_col).reindex(xs)[value_col].fillna(0).to_numpy()
        ax.bar(xs, sub, bottom=bottom, width=0.62, label=str(g),
               color=BASE_COLORS[i % len(BASE_COLORS)], linewidth=0.3, edgecolor="white")
        bottom += sub
    ax.set_ylim(bottom=0)
    ax.set_xlabel(xlabel or str(x_col))
    ax.set_ylabel(ylabel or str(value_col))
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0))
    return fig


# ------------------------------------------------------------ scatter/box ----
def scatter_rel(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    xlabel: str = "",
    ylabel: str = "",
    fit: bool = False,
) -> plt.Figure:
    """Render a two-variable scatter plot with an optional disclosed fit."""
    _require_min_info(df)
    _require_cols(df, [x_col, y_col])
    use_style()
    fig, ax = _new_fig_ax()
    ax.scatter(
        df[x_col],
        df[y_col],
        s=14,
        color=BASE_COLORS[0],
        linewidths=0.6,
    )
    if fit:
        a, b = np.polyfit(df[x_col], df[y_col], 1)
        xx = np.linspace(df[x_col].min(), df[x_col].max(), 50)
        ax.plot(xx, a * xx + b, color=BASE_COLORS[1], linestyle="--", linewidth=0.8)
    ax.set_xlabel(xlabel or str(x_col))
    ax.set_ylabel(ylabel or str(y_col))
    return fig


def box_group(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    xlabel: str = "",
    ylabel: str = "",
) -> plt.Figure:
    """Render grouped distributions as box plots."""
    _require_min_info(df)
    _require_cols(df, [x_col, y_col])
    groups = [g for _, g in df.groupby(x_col, sort=True)[y_col]]
    labels = [str(k) for k in sorted(df[x_col].unique())]
    if len(groups) < 2 or len(groups) > 6:
        raise ValueError(f"Box plots require two to six groups; received {len(groups)}.")
    use_style()
    fig, ax = _new_fig_ax()
    bp = ax.boxplot(groups, widths=0.5, patch_artist=False)
    ax.set_xticks(range(1, len(groups) + 1))
    ax.set_xticklabels(labels)
    for element in ("boxes", "whiskers"):
        for line in bp[element]:
            line.set_color(BASE_COLORS[0])
    for line in bp["medians"]:
        line.set_color(BASE_COLORS[1])
        line.set_linewidth(1.0)
    ax.set_xlabel(xlabel or str(x_col))
    ax.set_ylabel(ylabel or str(y_col))
    return fig


# ----------------------------------------------------------- coefficients ----
def coef_plot(
    df: pd.DataFrame,
    term_col: str,
    coef_col: str,
    lo_col: str | None = None,
    hi_col: str | None = None,
    se_col: str | None = None,
    xlabel: str = "Coefficient estimate",
    ylabel: str = "",
) -> plt.Figure:
    """Render coefficient estimates with 95% intervals and a zero line."""
    _require_min_info(df)
    _require_cols(df, [term_col, coef_col])
    if not (lo_col and hi_col) and not se_col:
        raise ValueError("Coefficient plots require lo/hi columns or an SE column for 95% intervals.")
    d = df.copy()
    if se_col:
        d["_lo"] = d[coef_col] - 1.96 * d[se_col]
        d["_hi"] = d[coef_col] + 1.96 * d[se_col]
    else:
        d["_lo"], d["_hi"] = d[lo_col], d[hi_col]
    use_style()
    fig, ax = _new_fig_ax()
    ypos = np.arange(len(d))
    ax.errorbar(d[coef_col], ypos, xerr=[d[coef_col] - d["_lo"], d["_hi"] - d[coef_col]],
                fmt="o", ms=4, color=BASE_COLORS[0], fillstyle="none", capsize=2,
                elinewidth=0.7, markeredgewidth=0.7)
    ax.axvline(0, color="#404040", linewidth=0.9, linestyle="-")
    ax.set_yticks(ypos, d[term_col])
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    return fig


# --------------------------------------------------------------- distribution ----
def hist_density(
    df: pd.DataFrame,
    x_col: str,
    xlabel: str = "",
    ylabel: str = "Frequency",
    bins: int | str = "auto",
    density: bool = False,
) -> plt.Figure:
    """Render a histogram with an optional kernel-density overlay."""
    _require_min_info(df)
    _require_cols(df, [x_col])
    use_style()
    fig, ax = _new_fig_ax()
    vals = df[x_col].dropna()
    ax.hist(vals, bins=bins, density=density, color="#BFBFBF", edgecolor=BASE_COLORS[0],
            linewidth=0.4)
    if density:
        ax2 = ax.twinx()
        ax2.set_ylabel("")
        ax2.set_yticks([])
        kernel = _kde(vals.to_numpy())
        xx = np.linspace(vals.min(), vals.max(), 200)
        ax2.plot(xx, kernel(xx), color=BASE_COLORS[0], linewidth=0.9)
    ax.set_xlabel(xlabel or str(x_col))
    ax.set_ylabel(ylabel)
    return fig


def _kde(data: np.ndarray):
    """Return a Gaussian kernel-density function for display only."""
    h = 1.06 * np.std(data) * len(data) ** (-1 / 5) or 1.0
    def f(x):
        u = (x[:, None] - data[None, :]) / h
        return np.mean(np.exp(-0.5 * u**2) / (h * np.sqrt(2 * np.pi)), axis=1)
    return f
