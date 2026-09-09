"""Dependency and glyph-coverage font check.

Return ``(ok, report)`` after checking the required packages and whether the
environment offers fonts likely to cover Latin and CJK text. The check does not
select a publication font or imply compliance with an institution.
"""
from __future__ import annotations

import os
import tempfile

# Match package initialization when this file is run directly.
_EC_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MPLCACHE = os.environ.get("MPLCONFIGDIR") or os.path.join(tempfile.gettempdir(), "econfigure-matplotlib")
os.makedirs(_MPLCACHE, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", _MPLCACHE)

PACKAGES = ["pandas", "numpy", "matplotlib", "openpyxl", "docx"]
PACKAGE_LABEL = {
    "pandas": "pandas",
    "numpy": "numpy",
    "matplotlib": "matplotlib",
    "openpyxl": "openpyxl",
    "docx": "python-docx",
}
CJK_FONT_CANDIDATES = ["Noto Sans CJK SC", "Noto Serif CJK SC", "SimSun", "SimHei", "STSong", "Microsoft YaHei"]
LATIN_FONT_CANDIDATES = ["DejaVu Sans", "DejaVu Serif", "Liberation Sans", "Liberation Serif", "Arial"]


def _import_ok() -> tuple[bool, list[str]]:
    bad: list[str] = []
    for p in PACKAGES:
        try:
            __import__(p)
        except Exception:
            bad.append(PACKAGE_LABEL[p])
    return (len(bad) == 0, bad)


def _fonts_missing() -> tuple[list[str], list[str]]:
    """Return missing Chinese and Latin font candidates."""
    try:
        import matplotlib.font_manager as fm
    except Exception:
        return CJK_FONT_CANDIDATES, LATIN_FONT_CANDIDATES
    names = {f.name for f in fm.fontManager.ttflist}
    miss_cn = [f for f in CJK_FONT_CANDIDATES if f not in names]
    miss_en = [f for f in LATIN_FONT_CANDIDATES if f not in names]
    return miss_cn, miss_en


def check() -> tuple[bool, str]:
    lines: list[str] = []
    ok = True

    p_ok, p_bad = _import_ok()
    if p_ok:
        lines.append("[OK] Required packages: pandas / numpy / matplotlib / openpyxl / python-docx")
    else:
        ok = False
        lines.append(f"[MISSING] Cannot import: {', '.join(p_bad)}")
        lines.append("          Fix: pip install -r requirements.txt")

    miss_cn, miss_en = _fonts_missing()
    if len(miss_en) == len(LATIN_FONT_CANDIDATES):
        ok = False
        lines.append("[MISSING] No verified Latin font found; select and install a font required by the target document")
    else:
        lines.append("[OK] Latin glyph coverage is available; choose typography from the target document")
    if miss_cn and len(miss_cn) == len(CJK_FONT_CANDIDATES):
        ok = False
        lines.append("[MISSING] No verified CJK font found; select and install a font required by the target document")
    elif miss_cn:
        lines.append("[OK] CJK glyph coverage is available; choose typography from the target document")
    else:
        lines.append("[OK] CJK glyph coverage is available; choose typography from the target document")

    lines.append("[INFO] Stata rendering requires a configured Stata MCP; otherwise use Python")
    return ok, "\n".join(lines)


if __name__ == "__main__":
    ok, report = check()
    print(report)
    raise SystemExit(0 if ok else 1)
