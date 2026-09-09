"""Render four synthetic thesis examples; never estimate research statistics."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "assets" / "standard_samples"
CASES = ["regional-export-trend", "ownership-productivity-comparison", "policy-coefficients", "event-study-dynamics"]
TITLES = ["Regional export growth", "Productivity across ownership groups", "Policy effects across outcomes", "Effects around policy adoption"]
COLORS = ["#236B83", "#CB7652", "#7C849B"]


def validate(case, data):
    if data.empty:
        raise ValueError("Sample data must not be empty")
    if data.isna().any().any():
        raise ValueError("Sample values must not be missing")
    if not np.isfinite(data.select_dtypes(include='number').to_numpy()).all():
        raise ValueError("Numeric values must be finite")
    if case == CASES[0]:
        for _, group in data.groupby("region", sort=False):
            if not np.all(np.diff(group.year) == 1):
                raise ValueError("Years must be unique and continuous within each series")
    elif case == CASES[1]:
        if data.duplicated(["industry", "ownership"]).any():
            raise ValueError("Duplicate group key")
        expected = set(data.ownership)
        if len(expected) != 2 or any(set(group.ownership) != expected for _, group in data.groupby('industry')):
            raise ValueError("Incomplete group pairing")
    else:
        if not ((data.low <= data.estimate) & (data.estimate <= data.high)).all():
            raise ValueError("Supplied interval must contain its estimate")
        key = "term" if case == CASES[2] else "event_time"
        if data[key].duplicated().any():
            raise ValueError("Duplicate estimate key")
        if case == CASES[3] and not np.all(np.diff(data.event_time) == 1):
            raise ValueError("Event times must be continuous and ordered")
        if case == CASES[3]:
            baseline = data[data.event_time == -1]
            if len(baseline) != 1 or not (baseline[['estimate', 'low', 'high']] == 0).all().all():
                raise ValueError("This sample requires a supplied zero reference at period -1")


def draw(ax, case, data):
    validate(case, data)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["bottom", "left"]].set_color("#BAC4CD")
    ax.tick_params(colors="#445364", labelsize=10, length=3, pad=6)
    ax.grid(axis="y", color="#EDF0F3", linewidth=.65)
    if case == CASES[0]:
        for i, (name, group) in enumerate(data.groupby("region", sort=False)):
            ax.plot(group.year, group.export_growth, color=COLORS[i], marker=["o", "s", "^"][i], linestyle=["-", "--", "-."][i], linewidth=2, markersize=5, label=name)
        ax.set(ylabel="Export growth (%)", xlabel="Year", ylim=(0, 8.5))
        ax.set_xticks(sorted(data.year.unique()))
        ax.legend(loc="upper left", ncol=3, frameon=False, fontsize=9, handlelength=2.2, columnspacing=1.5)
    elif case == CASES[1]:
        categories = data.industry.unique()
        x = np.arange(len(categories))
        for i, name in enumerate(data.ownership.unique()):
            values = data[data.ownership == name].set_index("industry").loc[categories].productivity_index
            bars = ax.bar(x + (i-.5)*.34, values, width=.30, color=COLORS[i], label=name, hatch="" if i == 0 else "//", edgecolor="white", linewidth=.6)
            ax.bar_label(bars, padding=5, fontsize=9, color="#445364")
        ax.set_xticks(x, categories)
        ax.set(ylabel="Productivity index", ylim=(0, 150))
        ax.legend(loc="upper left", ncol=2, frameon=False, fontsize=9, columnspacing=2)
    elif case == CASES[2]:
        y = np.arange(len(data))
        ax.grid(False)
        ax.grid(axis="x", color="#EDF0F3", linewidth=.65)
        ax.axvline(0, color="#929BA5", linestyle="--", linewidth=1)
        ax.errorbar(data.estimate, y, xerr=np.array([data.estimate-data.low, data.high-data.estimate]), fmt="o", color=COLORS[0], elinewidth=2, capsize=4, markersize=7)
        ax.set_yticks(y, data.term)
        ax.set(xlabel="Estimated effect with supplied 95% interval", xlim=(-.025, .205), ylim=(3.6, -.6))
        ax.spines["left"].set_visible(False)
    else:
        shown = data[data.event_time != -1]
        ax.axhline(0, color="#929BA5", linestyle="--", linewidth=1)
        ax.axvline(0, color="#D1A28C", linestyle=":", linewidth=1.3)
        ax.errorbar(shown.event_time, shown.estimate, yerr=np.array([shown.estimate-shown.low, shown.high-shown.estimate]), fmt="o", color=COLORS[0], elinewidth=1.6, capsize=4, markersize=6, label="Estimate and supplied 95% interval")
        ax.plot(-1, 0, "o", color=COLORS[0], markerfacecolor="white", markersize=6)
        ax.set_xticks(data.event_time)
        ax.set(xlabel="Years relative to adoption (−1: reference)", ylabel="Estimated effect", ylim=(-.085, .205))
        ax.legend(loc="upper left", frameon=False, fontsize=9)
    ax.xaxis.labelpad = 12
    ax.yaxis.labelpad = 10


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=SAMPLES)
    parser.add_argument("--showcase", action="store_true")
    args = parser.parse_args()
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.labelcolor": "#445364", "savefig.facecolor": "white"})
    report = []
    for i, case in enumerate(CASES):
        source = SAMPLES / case / "input.csv"
        before = hashlib.sha256(source.read_bytes()).hexdigest()
        data = pd.read_csv(source)
        fig, ax = plt.subplots(figsize=(7.4, 4.7), layout="constrained")
        draw(ax, case, data)
        ax.set_title(TITLES[i], loc="left", fontsize=15, fontweight="bold", pad=22, color="#18364B")
        dest = args.output_dir / case
        dest.mkdir(parents=True, exist_ok=True)
        path = dest / "figure.png"
        fig.savefig(path, dpi=600)
        plt.close(fig)
        with Image.open(path) as im:
            assert all(abs(d-600) < 1 for d in im.info["dpi"])
            size = list(im.size)
        assert before == hashlib.sha256(source.read_bytes()).hexdigest()
        report.append({"id": case, "input_unchanged": True, "pixel_size": size, "dpi": 600, "rows": len(data), "checks": "required values, ordered keys or paired groups, supplied interval order; visual review separate"})
    (args.output_dir / "validation.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    if args.showcase:
        fig, axes = plt.subplots(2, 2, figsize=(15.2, 10.2))
        fig.subplots_adjust(left=.075, right=.975, bottom=.085, top=.85, hspace=.58, wspace=.28)
        fig.text(.075, .955, "ECONOMIC QUESTIONS. CLEAR FIGURES.", fontsize=23, weight="bold", color="#18364B")
        fig.text(.075, .911, "Econfigure Skill  /  Applied economics master's theses", fontsize=13, color="#596B7B")
        for i, (case, ax) in enumerate(zip(CASES, axes.flat)):
            draw(ax, case, pd.read_csv(SAMPLES / case / "input.csv"))
            ax.set_title(f"0{i+1}  {TITLES[i]}", loc="left", fontsize=13, weight="bold", pad=22, color="#18364B")
        fig.text(.075, .018, "Synthetic demonstration data · Supplied estimates and intervals · No empirical findings implied", fontsize=9, color="#6D7D8A")
        output = ROOT / "assets" / "showcase" / "econfigure-skill-preview.png"
        output.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output, dpi=160)
        plt.close(fig)
    print(f"samples={len(report)} passed={len(report)}")


if __name__ == "__main__":
    main()
