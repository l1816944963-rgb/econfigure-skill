"""Validate every public asset and optionally execute its production script."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pandas as pd
import yaml
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "assets" / "figures"
REQUIRED_MANIFEST_FIELDS = {"id", "family", "subtype", "status", "files", "output", "scene", "data_contract", "elements", "implementation", "compatibility"}
REQUIRED_CONTRACT_FIELDS = {"required_data_roles", "semantic_contract", "retrieval_contract"}


def error(record: dict, message: str) -> None:
    record["errors"].append(message)


def validate_manifest(path: Path) -> dict:
    started = time.perf_counter()
    record = {"asset": path.stem.removesuffix(".asset"), "manifest": str(path.relative_to(ROOT)), "errors": [], "warnings": []}
    try:
        manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as exc:
        error(record, f"manifest parse failed: {exc}")
        return record

    missing = REQUIRED_MANIFEST_FIELDS - set(manifest)
    if missing:
        error(record, f"missing manifest fields: {sorted(missing)}")
    if manifest.get("family") != path.parent.name:
        error(record, "family must equal the containing directory name")
    if manifest.get("status") != "approved":
        error(record, "runtime assets must have approved status")

    files = manifest.get("files") or {}
    for key in ("script", "preview"):
        value = files.get(key)
        if not value or not (path.parent / value).is_file():
            error(record, f"missing {key} file: {value}")
    if (manifest.get("output") or {}).get("format") != "png":
        error(record, "output format must be png")
    if int((manifest.get("output") or {}).get("dpi", 0)) != 600:
        error(record, "output dpi must be 600")

    contract = manifest.get("data_contract") or {}
    missing_contract = REQUIRED_CONTRACT_FIELDS - set(contract)
    if missing_contract:
        error(record, f"missing data-contract fields: {sorted(missing_contract)}")
    roles = contract.get("required_data_roles") or []
    if not roles:
        error(record, "required_data_roles cannot be empty")
    available: set[tuple[str, str]] = set()
    for value in files.values():
        values = value if isinstance(value, list) else [value]
        for item in values:
            item = str(item)
            source = path.parent / item
            if source.suffix.lower() == ".csv" and source.is_file():
                try:
                    available.update((item, str(column)) for column in pd.read_csv(source, nrows=0).columns)
                except Exception as exc:
                    error(record, f"cannot read fixture {item}: {exc}")
    declared = {(str(role.get("source")), str(role.get("field"))) for role in roles}
    if declared != available:
        error(record, f"data roles do not match CSV fields; missing={sorted(available-declared)}, extra={sorted(declared-available)}")
    for role in roles:
        for field in ("field", "source", "role", "value_type", "required", "description"):
            if field not in role:
                error(record, f"data role is missing {field}")

    semantic = contract.get("semantic_contract") or {}
    for field in ("unit_of_observation", "mark_to_data_mapping", "specialized", "rules"):
        if field not in semantic:
            error(record, f"semantic contract is missing {field}")
    retrieval = contract.get("retrieval_contract") or {}
    for field in ("match_first", "match_second", "reject_if"):
        if not retrieval.get(field):
            error(record, f"retrieval contract is missing {field}")

    script_name = files.get("script")
    if script_name and (path.parent / script_name).is_file():
        text = (path.parent / script_name).read_text(encoding="utf-8")
        forbidden = ("reconstruction_batch", "batch_modules", "source_references")
        for token in forbidden:
            if token in text:
                error(record, f"script depends on private development token: {token}")
    record["duration_seconds"] = round(time.perf_counter() - started, 4)
    return record


def execute_asset(path: Path, record: dict, output_root: Path, timeout: int) -> None:
    manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
    script = path.parent / manifest["files"]["script"]
    destination = output_root / str(manifest["id"])
    destination.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["MPLCONFIGDIR"] = str(output_root / "matplotlib-cache")
    started = time.perf_counter()
    try:
        result = subprocess.run(
            [sys.executable, "-B", str(script), "--output-dir", str(destination)],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        error(record, f"execution exceeded {timeout} seconds")
        return
    record["execution_seconds"] = round(time.perf_counter() - started, 3)
    if result.returncode != 0:
        error(record, f"execution failed: {(result.stderr or result.stdout)[-1000:]}")
        return
    outputs = sorted(destination.glob("*.png"))
    if not outputs:
        error(record, "execution produced no PNG")
        return
    expected_stem = str(manifest["id"])
    primary = destination / f"{expected_stem}.png"
    if not primary.exists():
        primary = outputs[0]
        record["warnings"].append(f"expected {expected_stem}.png; inspected {primary.name}")
    try:
        with Image.open(primary) as image:
            image.verify()
        with Image.open(primary) as image:
            if image.width < 300 or image.height < 200:
                error(record, f"implausibly small output: {image.width}x{image.height}")
            record["pixel_size"] = [image.width, image.height]
    except Exception as exc:
        error(record, f"invalid PNG: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true", help="Run every selected production script in an isolated temporary directory.")
    parser.add_argument("--family", help="Limit the audit to one asset family.")
    parser.add_argument("--asset", help="Limit the audit to one asset id.")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    paths = sorted(ASSET_ROOT.rglob("*.asset.yaml"))
    if args.family:
        paths = [path for path in paths if path.parent.name == args.family]
    if args.asset:
        paths = [path for path in paths if path.name == f"{args.asset}.asset.yaml"]
    if not paths:
        print("No assets selected.", file=sys.stderr)
        return 2

    records = [validate_manifest(path) for path in paths]
    if args.execute:
        with tempfile.TemporaryDirectory(prefix="econfigure-eval-") as temporary:
            output_root = Path(temporary)
            for index, (path, record) in enumerate(zip(paths, records), 1):
                if not record["errors"]:
                    execute_asset(path, record, output_root, args.timeout)
                print(f"[{index:02d}/{len(paths):02d}] {record['asset']}: {'PASS' if not record['errors'] else 'FAIL'}")

    summary = {
        "assets": len(records),
        "passed": sum(not record["errors"] for record in records),
        "failed": sum(bool(record["errors"]) for record in records),
        "executed": args.execute,
        "records": records,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"assets={summary['assets']} passed={summary['passed']} failed={summary['failed']} executed={str(args.execute).lower()}")
    if summary["failed"]:
        for record in records:
            for message in record["errors"]:
                print(f"FAIL {record['asset']}: {message}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
