"""Generate the compact runtime catalog from validated asset manifests."""

from __future__ import annotations

from pathlib import Path
import argparse

import yaml


ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "assets" / "figures"
OUTPUT = ROOT / "assets" / "catalog.index.yaml"


def string_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    records: list[dict] = []
    seen: set[str] = set()
    for path in sorted(ASSET_ROOT.rglob("*.asset.yaml")):
        manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict) or manifest.get("status") != "approved":
            continue
        asset_id = str(manifest.get("id", "")).strip()
        if not asset_id:
            raise ValueError(f"Missing asset id: {path}")
        if asset_id in seen:
            raise ValueError(f"Duplicate asset id: {asset_id}")
        seen.add(asset_id)

        elements = manifest.get("elements") or {}
        compatibility = manifest.get("compatibility") or {}
        data_contract = manifest.get("data_contract") or {}
        files = manifest.get("files") or {}
        element_values: list[str] = []
        for key in ("geometry", "encoding", "annotation", "axes", "layout"):
            element_values.extend(string_list(elements.get(key)))
        search_terms = sorted(
            {
                str(manifest.get("family", "")),
                str(manifest.get("subtype", "")),
                *element_values,
            }
            - {""}
        )
        relative_dir = path.parent.relative_to(ROOT / "assets").as_posix()
        record = {
            "id": asset_id,
            "family": manifest.get("family"),
            "subtype": manifest.get("subtype"),
            "scenes": string_list(manifest.get("scene")),
            "data_contract_summary": data_contract.get("summary"),
            "required_role_names": sorted({role['role'] for role in data_contract.get('required_data_roles', [])}),
            "specialized": bool((data_contract.get('semantic_contract') or {}).get('specialized')),
            "elements": {
                key: string_list(elements.get(key))
                for key in ("geometry", "encoding", "annotation", "axes", "layout")
                if elements.get(key)
            },
            "compatibility": {
                key: compatibility.get(key)
                for key in ("grayscale", "academic-publication", "warnings")
                if key in compatibility
            },
            "search_terms": search_terms,
            "files": {
                "manifest": f"{relative_dir}/{path.name}",
                "script": f"{relative_dir}/{files.get('script')}",
                "preview": f"{relative_dir}/{files.get('preview')}",
            },
        }
        records.append(record)

    payload = {
        "schema_version": 2,
        "source": "validated runtime asset manifests",
        "asset_count": len(records),
        "assets": records,
    }
    content = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, width=120)
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding='utf-8') != content:
            print('Catalog is stale; run scripts/build_catalog.py')
            return 1
    else:
        OUTPUT.write_text(content, encoding='utf-8')
    print(f"catalog={OUTPUT}")
    print(f"assets={len(records)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
