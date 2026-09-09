"""Render supplied summaries with the validated mental-health-study-comparison layout."""
from pathlib import Path
import sys, argparse
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from chartlib.asset_runtime import save_outputs
from chartlib.inference_renderers import RENDERERS
STEM="mental-health-study-comparison"
def render(source):
    return RENDERERS[STEM](source)
def main():
    home=Path(__file__).resolve().parent
    p=argparse.ArgumentParser()
    p.add_argument("--data",type=Path,default=home/f"{STEM}.fixture.csv")
    p.add_argument("--output-dir",type=Path,default=home)
    p.add_argument("--qa-preview",type=Path)
    a=p.parse_args()
    print(save_outputs(render(a.data),a.output_dir,STEM,qa_preview=a.qa_preview))
if __name__=="__main__":main()

