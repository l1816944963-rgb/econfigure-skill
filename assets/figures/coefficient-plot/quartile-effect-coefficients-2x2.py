"""Render the approved layout from an external plotting fixture."""
from pathlib import Path
import argparse
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from chartlib.asset_runtime import save_outputs
from chartlib.comparison_renderers import RENDERERS
STEM = "quartile-effect-coefficients-2x2"
def render(source):
    return RENDERERS[STEM](source)
def main():
    home = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=home / f"{STEM}.fixture.csv")
    parser.add_argument("--output-dir", type=Path, default=home)
    parser.add_argument("--qa-preview", type=Path)
    args = parser.parse_args()
    print(save_outputs(render(args.data), args.output_dir, STEM, qa_preview=args.qa_preview))
if __name__ == "__main__":
    main()

