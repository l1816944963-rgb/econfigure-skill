"""Generate the public asset atlas from runtime manifests."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "assets" / "figures"
OUTPUT = ROOT / "assets" / "figure-atlas.md"


def load_assets() -> list[tuple[Path, dict]]:
    assets = []
    for path in sorted(ASSET_ROOT.rglob("*.asset.yaml")):
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
        if record.get("status") == "approved":
            assets.append((path, record))
    return assets


def render() -> str:
    grouped: dict[str, list[tuple[Path, dict]]] = defaultdict(list)
    for path, record in load_assets():
        grouped[str(record["family"])].append((path, record))

    lines = [
        "# Econfigure Skill Public Figure Atlas",
        "",
        "> This file is generated from public runtime manifests. Run `python scripts/generate_atlas.py` after changing an asset manifest.",
        "",
        "The library contains independently implemented figure assets collected and studied from publicly accessible academic literature. Original publications and their figures remain the property of their respective authors and publishers. The atlas is a retrieval index, not a claim of ownership over the underlying visual ideas.",
        "",
        f"**Assets:** {sum(len(items) for items in grouped.values())}  ",
        f"**Families:** {len(grouped)}",
        "",
        "## Family index",
        "",
        "| Family | Assets |",
        "|---|---:|",
    ]
    for family, items in sorted(grouped.items()):
        lines.append(f"| [{family}](#{family}) | {len(items)} |")

    for family, items in sorted(grouped.items()):
        lines.extend(["", f"## {family}", ""])
        for path, record in items:
            files = record.get("files") or {}
            relative_dir = path.parent.relative_to(ROOT / "assets").as_posix()
            preview = f"{relative_dir}/{files['preview']}"
            script = f"{relative_dir}/{files['script']}"
            contract = record.get("data_contract") or {}
            semantic = contract.get("semantic_contract") or {}
            roles = contract.get("required_data_roles") or []
            fields = sorted({str(role["field"]) for role in roles if role.get("required")})
            elements = record.get("elements") or {}
            tags = sorted({str(value) for values in elements.values() for value in (values if isinstance(values, list) else [values])})
            scenes = record.get("scene") or []
            lines.extend([
                f"### {record['id']}",
                "",
                f"![{record['id']}]({preview})",
                "",
                f"- **Subtype:** `{record.get('subtype', '')}`",
                f"- **Use when:** {'; '.join(str(x) for x in scenes)}",
                f"- **Required fields:** `{', '.join(fields)}`",
                f"- **Data meaning:** {semantic.get('mark_to_data_mapping', '')}",
                f"- **Tags:** `{', '.join(tags)}`",
                f"- **Code:** [`{files['script']}`]({script})",
                "",
            ])
            rules = semantic.get("rules") or []
            if len(rules) > 1:
                lines.append(f"> Specialized constraint: {' '.join(str(rule) for rule in rules[1:])}")
                lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail when the committed atlas is stale.")
    args = parser.parse_args()
    content = render()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content:
            print("atlas_stale=true")
            return 1
        print("atlas_stale=false")
        return 0
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"atlas={OUTPUT}")
    print(f"assets={len(load_assets())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
