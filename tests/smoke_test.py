"""Exercise the environment, core figures, PNG export, and Word tables.

Generated files are written to ``tests/out`` and are not source assets.
"""

from __future__ import annotations

import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sys.path.insert(0, PKG)
sys.path.insert(0, os.path.join(PKG, "chartlib"))

import pandas as pd  # noqa: E402

from chartlib import data_io, env_check, figures, savefig, tables  # noqa: E402

OUT = os.environ.get('ECONFIGURE_TEST_OUTPUT') or tempfile.mkdtemp(prefix='econfigure-smoke-')
os.makedirs(OUT, exist_ok=True)
DATA = os.path.join(HERE, "sample_data.csv")
DOC = os.path.join(OUT, "smoke_three_line_tables.docx")


def _save(fig, name: str) -> None:
    savefig.save_figure(fig, name, OUT)
    print(f"  -> {name}.png / {name}_gray.png\n")


def main() -> None:
    ok, report = env_check.check()
    print(report, "\n")
    if not ok:
        print("Environment check failed; smoke test stopped.")
        raise SystemExit(1)

    audit = data_io.AuditLog()
    df = data_io.load_table(DATA, audit)
    df = data_io.dedupe(df, audit)
    long = df.melt(id_vars="year", var_name="market", value_name="value")
    print(audit.render(), "\n")

    _save(
        figures.line_trend(
            df,
            x_col="year",
            y_cols=["china", "asean", "eu", "us"],
            ylabel="Exports (USD 100 million)",
        ),
        "smoke_line_trend",
    )

    bar_df = long[long["year"] == 2024][["market", "value"]]
    _save(
        figures.bar_compare(bar_df, "market", "value", ylabel="Exports (USD 100 million)"),
        "smoke_bar_compare",
    )

    long5 = long[long["market"] != "other"]
    _save(
        figures.stacked_bar(
            long5,
            "year",
            "market",
            "value",
            ylabel="Exports (USD 100 million)",
        ),
        "smoke_stacked_bar",
    )

    scatter_data = df.copy()
    scatter_data["total"] = scatter_data[["china", "asean", "eu", "us"]].sum(axis=1)
    scatter_data["ratio"] = scatter_data["china"] / scatter_data["total"]
    _save(
        figures.scatter_rel(
            scatter_data,
            "total",
            "ratio",
            xlabel="Total exports (USD 100 million)",
            ylabel="China share",
        ),
        "smoke_scatter",
    )

    _save(
        figures.box_group(long, "market", "value", xlabel="Market", ylabel="Exports"),
        "smoke_box",
    )

    coefficients = pd.DataFrame(
        {
            "term": ["Policy interaction", "Firm size", "Financing constraint", "Competition", "Constant"],
            "coef": [0.042, -0.013, 0.008, 0.021, 1.25],
            "se": [0.012, 0.005, 0.004, 0.009, 0.31],
        }
    )
    _save(
        figures.coef_plot(coefficients, "term", "coef", se_col="se", ylabel="Variable"),
        "smoke_coefficient_plot",
    )

    rng = __import__("numpy").random.default_rng(1)
    distribution = pd.DataFrame({"x": rng.normal(100, 15, 300)})
    _save(
        figures.hist_density(distribution, "x", xlabel="Variable x", density=True),
        "smoke_distribution",
    )

    first = tables.TableSpec(
        chapter=4,
        title="Descriptive statistics for major export markets",
        header=["Variable", "Mean", "Standard deviation", "Observations"],
        rows=[["Exports", "1182.4", "186.3", "6"], ["Market share", "0.182", "0.043", "6"]],
        italic_cols=[0],
        note=["Note: The sample covers 2019-2024; export values use USD 100 million."],
        source="Source: Simulated data for smoke testing.",
    )
    second = tables.TableSpec(
        chapter=4,
        title="Baseline regression results",
        header=["Variable", "(1) Exports", "(2) Market share"],
        rows=[
            ["Policy interaction", "0.042*** (0.012)", "0.021*** (0.006)"],
            ["Firm size", "-0.013 (0.005)", "-0.002 (0.004)"],
        ],
        italic_cols=[0],
        note=["Note: ***, **, and * indicate significance at 1%, 5%, and 10%; robust standard errors are in parentheses."],
    )
    made = tables.render_tables([first, second], DOC)
    print("Tables written:", made.replace("\n", " | "))
    print(f"  -> {DOC}\n")
    print("SMOKE OK")


if __name__ == "__main__":
    main()
