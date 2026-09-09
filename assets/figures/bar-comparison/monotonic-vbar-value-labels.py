"""Render ordered vertical bars with independent text labels above each bar."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import pandas as pd
PROJECT_ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PROJECT_ROOT))
from chartlib.asset_runtime import read_frame, require_columns, require_finite, save_outputs, style_axis
from matplotlib.figure import Figure

def load_data(source):
    d=read_frame(source); cols=("category","order","value","label"); require_columns(d,cols); d=d.loc[:,cols].copy(); require_finite(d,("order","value"))
    if d.category.duplicated().any() or d.order.duplicated().any(): raise ValueError("Category and order keys must be unique.")
    if (d.value<0).any() or len(d)<6: raise ValueError("Bars require a zero baseline and at least six categories.")
    return d.sort_values("order")

def render(data):
    d=load_data(data); fig=Figure(figsize=(5.94,3.99),facecolor="white"); ax=fig.add_axes((78/594,24/399,493/594,358/399)); style_axis(ax,grid=True)
    bars=ax.bar(range(len(d)),d.value,width=.60,color="#1C4E7A",zorder=2)
    ax.bar_label(bars,labels=d.label,padding=3,fontsize=8)
    ax.set_ylim(0,2.15); ax.set_yticks([0,.5,1,1.5,2],labels=["0",".5","1","1.5","2"]); ax.set_xticks(range(len(d)),d.category.astype(str)); ax.set_ylabel("Floating Rate Exposure",fontsize=10)
    return fig

def main():
    p=argparse.ArgumentParser(description=__doc__); here=Path(__file__).resolve().parent; p.add_argument("--data",type=Path,default=here/"monotonic-vbar-value-labels.fixture.csv"); p.add_argument("--output-dir",type=Path,default=here); p.add_argument("--qa-preview",type=Path); a=p.parse_args(); print(save_outputs(render(a.data),a.output_dir,"monotonic-vbar-value-labels",qa_preview=a.qa_preview))
if __name__=="__main__": main()
