"""Read-only data loading and plot-required reshaping.

Allowed operations include missing-value handling, duplicate removal, pivoting,
column renaming, and sorting. Analytical calculations and writes to source data
are forbidden. Record every operation in AuditLog and deliver the rendered log.

Example:
    audit = AuditLog()
    df = load_table(path, audit)
    df = rename_columns(df, {"old": "new"}, audit)
    df = drop_na(df, audit, how="all")
    df = dedupe(df, audit)
    df = pivot_summary(df, index="year", values="value", aggfunc="mean", audit=audit)
    print(audit.render())
"""
from __future__ import annotations

import os
from typing import Callable

import pandas as pd


class AuditLog:
    """Record permitted transformations and render a user-readable report."""

    def __init__(self) -> None:
        self.steps: list[str] = []

    def add(self, text: str) -> None:
        self.steps.append(text)

    def render(self) -> str:
        if not self.steps:
            return "Data-processing note: the source data was used without reshaping."
        head = "Data-processing note (the source file was not modified):"
        body = "\n".join(f"{i}. {s}" for i, s in enumerate(self.steps, 1))
        return head + "\n" + body


def load_table(path: str, audit: AuditLog) -> pd.DataFrame:
    """Read an Excel or delimited text file without modifying it."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data file does not exist: {path}")
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".xls", ".xlsm"):
        df = pd.read_excel(path)
        audit.add(f"Read Excel file {os.path.basename(path)}: {df.shape[0]} rows by {df.shape[1]} columns.")
    elif ext in (".csv", ".tsv", ".txt"):
        sep = "\t" if ext == ".tsv" else ("," if ext == ".csv" else None)
        enc = _detect_encoding(path)
        df = pd.read_csv(path, sep=sep, encoding=enc, engine="python" if sep is None else "c")
        audit.add(f"Read text file {os.path.basename(path)} using {enc}: {df.shape[0]} rows by {df.shape[1]} columns.")
    else:
        raise ValueError(f"Unsupported data type {ext}; use .xlsx, .xls, .csv, or .tsv.")
    return df


def _detect_encoding(path: str) -> str:
    try:
        with open(path, "rb") as f:
            raw = f.read(4000)
        if raw.startswith(b"\xef\xbb\xbf"):
            return "utf-8-sig"
        decoded = raw.decode("utf-8")
        if decoded.count("\ufffd") == 0:
            return "utf-8"
        return "gbk"
    except UnicodeDecodeError:
        return "gbk"


def rename_columns(df: pd.DataFrame, mapping: dict, audit: AuditLog) -> pd.DataFrame:
    df = df.rename(columns=mapping)
    audit.add("Renamed columns: " + ", ".join(f"{k} -> {v}" for k, v in mapping.items()) + ".")
    return df


def drop_na(df: pd.DataFrame, audit: AuditLog, how: str = "any", subset: list | None = None) -> pd.DataFrame:
    before = len(df)
    df = df.dropna(how=how, subset=subset)
    dropped = before - len(df)
    if dropped:
        scope = f", columns={subset}" if subset else ""
        audit.add(f"Removed {dropped} rows during missing-value handling (how={how}{scope}).")
    return df


def dedupe(df: pd.DataFrame, audit: AuditLog, subset: list | None = None) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates(subset=subset)
    dropped = before - len(df)
    if dropped:
        audit.add(f"Removed {dropped} duplicate rows (subset={subset}).")
    return df


def pivot_summary(
    df: pd.DataFrame,
    index: str,
    values: str,
    audit: AuditLog,
    aggfunc: str | Callable = "sum",
) -> pd.DataFrame:
    out = df.groupby(index, as_index=False)[values].agg(aggfunc)
    audit.add(f"Grouped by {index} and aggregated {values} with {_agg_name(aggfunc)}.")
    return out


def _agg_name(aggfunc):
    if callable(aggfunc):
        return getattr(aggfunc, "__name__", "custom function")
    return str(aggfunc)


def sort_values(df: pd.DataFrame, by: str, audit: AuditLog, ascending: bool = True) -> pd.DataFrame:
    df = df.sort_values(by=by, ascending=ascending).reset_index(drop=True)
    direction = "ascending" if ascending else "descending"
    audit.add(f"Sorted by {by} in {direction} order.")
    return df
