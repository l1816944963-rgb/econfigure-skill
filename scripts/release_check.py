"""Check that the repository is internally consistent and ready to publish."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_ROOT = {
    "README.md", "README_EN.md", "SKILL.md", "LICENSE", "NOTICE",
    "CONTRIBUTING.md", "SECURITY.md", "CHANGELOG.md", "requirements.txt",
}
FORBIDDEN_DIRS = {".venv", ".cache", "__pycache__", "out"}
FORBIDDEN_TEXT = (
    "D:" + "\\project\\",
    "C:" + "\\Users\\",
    "immutable " + "source",
    "candidate-" + "normalized",
    "diff-" + "amplified",
    "review-" + "sheet",
)


def run(*args: str) -> bool:
    result = subprocess.run([sys.executable, "-B", *args], cwd=ROOT, text=True, capture_output=True)
    if result.returncode:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        return False
    return True


def section_ids(path: Path) -> list[str]:
    return re.findall(r"<!-- section:([a-z0-9-]+) -->", path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    missing = sorted(name for name in REQUIRED_ROOT if not (ROOT / name).is_file())
    if missing:
        errors.append(f"missing release files: {missing}")

    zh_sections = section_ids(ROOT / "README.md") if (ROOT / "README.md").exists() else []
    en_sections = section_ids(ROOT / "README_EN.md") if (ROOT / "README_EN.md").exists() else []
    if not zh_sections or zh_sections != en_sections:
        errors.append("Chinese and English README section ids are absent or inconsistent")

    for directory in ROOT.rglob("*"):
        if directory.is_dir() and directory.name in FORBIDDEN_DIRS:
            errors.append(f"runtime directory is committed: {directory.relative_to(ROOT)}")

    text_suffixes = {".md", ".py", ".yaml", ".yml", ".txt", ".csv", ".mdc"}
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in text_suffixes:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for token in FORBIDDEN_TEXT:
                if token.lower() in text.lower():
                    errors.append(f"private or development token {token!r} in {path.relative_to(ROOT)}")

    template_root = ROOT / "assets" / "institution-templates"
    for template in template_root.glob("*/template.yaml"):
        payload = yaml.safe_load(template.read_text(encoding="utf-8"))
        if payload.get("selection", {}).get("explicit_only") is not True:
            errors.append(f"institution template must be explicit-only: {template.relative_to(ROOT)}")

    samples = ROOT / "assets" / "standard_samples"
    scenario_dirs = [path for path in samples.iterdir() if path.is_dir()]
    if len(scenario_dirs) < 4:
        errors.append("at least four standard acceptance scenarios are required")
    for scenario in scenario_dirs:
        for name in ("request.md", "input.csv", "expected.yaml", "figure.png"):
            if not (scenario / name).is_file():
                errors.append(f"missing {name} in {scenario.relative_to(ROOT)}")

    if not run("scripts/eval_runner.py"):
        errors.append("static asset evaluation failed")
    if not run("scripts/generate_atlas.py", "--check"):
        errors.append("public atlas is stale")
    if not run("scripts/build_catalog.py", "--check"):
        errors.append("machine catalog is stale")
    for name in ('README.md', 'README_EN.md'):
        body = (ROOT / name).read_text(encoding='utf-8')
        targets = re.findall(r'(?:src|href)="([^"]+)"', body)
        targets += re.findall(r'\]\(([^)]+)\)', body)
        for target in targets:
            if target.startswith(('https://', 'http://', '#')):
                continue
            if not (ROOT / target.split('#')[0]).exists():
                errors.append(f'{name}: missing local link {target}')

    if errors:
        for message in errors:
            print(f"FAIL: {message}")
        print(f"release_ready=false errors={len(errors)}")
        return 1
    print(f"static_release_checks=passed assets={len(list((ROOT / 'assets' / 'figures').rglob('*.asset.yaml')))} samples={len(scenario_dirs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
