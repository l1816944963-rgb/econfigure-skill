"""Render the approved layout from external plotting tables."""
from pathlib import Path
import sys,argparse
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from chartlib.asset_runtime import save_outputs
from chartlib.matrix_decomposition_renderers import RENDERERS
STEM="index-change-component-dashboard"
def render(source,**kwargs):return RENDERERS[STEM](source,**kwargs)
def main():
    home=Path(__file__).resolve().parent
    p=argparse.ArgumentParser()
    p.add_argument("--data",type=Path,default=home/f"{STEM}.fixture.csv")
    p.add_argument("--output-dir",type=Path,default=home)
    p.add_argument("--qa-preview",type=Path)
    args=p.parse_args()
    print(save_outputs(render(args.data),args.output_dir,STEM,qa_preview=args.qa_preview))
if __name__=="__main__":main()
