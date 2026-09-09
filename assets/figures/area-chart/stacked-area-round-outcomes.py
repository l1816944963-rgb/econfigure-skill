"""Render a normalized three-outcome stacked area across repeated rounds."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import numpy as np
from matplotlib.figure import Figure
from matplotlib.patches import Patch
PROJECT_ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PROJECT_ROOT))
from chartlib.asset_runtime import read_frame,require_columns,require_finite,save_outputs,style_axis

def load_data(source):
    d=read_frame(source); cols=("round","component","component_order","share"); require_columns(d,cols); d=d.loc[:,cols].copy(); require_finite(d,("round","component_order","share"))
    if d.duplicated(["round","component"]).any() or d.component.nunique()!=3: raise ValueError("Unique round-component keys and exactly three components are required.")
    if (d.share<0).any() or not np.allclose(d.groupby("round").share.sum(),1,atol=1e-8): raise ValueError("Every round must contain non-negative shares summing to one.")
    if sorted(d["round"].unique())!=list(range(1,31)): raise ValueError("Continuous rounds 1 through 30 are required.")
    return d

def render(source):
    d=load_data(source); fig=Figure(figsize=(5.62,4),facecolor="white"); ax=fig.add_axes((.12,.12,.82,.84)); style_axis(ax,full_spines=True)
    rounds=np.arange(1,31); comps=d.sort_values("component_order").component.drop_duplicates().tolist(); vals=[d[d.component==c].sort_values("round").share.to_numpy() for c in comps]
    colors=["#A5A7AA","#52545A","#FFFFFF"]; layers=ax.stackplot(rounds,*vals,colors=colors,edgecolor="#30343A",linewidth=1.0)
    ax.set_xlim(.5,30.5); ax.set_ylim(0,1); ax.set_xticks([1,5,10,15,20,25,30]); ax.set_yticks(np.arange(0,1.01,.1),["0"]+[f".{i}" for i in range(1,10)]+["1"])
    ax.set_xlabel("Round",fontsize=11); ax.set_ylabel("Frequency",fontsize=11); ax.tick_params(labelsize=9.5,length=4.2)
    handles=[Patch(facecolor=colors[i],edgecolor="#30343A",label=comps[i]) for i in [2,1,0]]
    ax.legend(handles=handles,loc="lower right",bbox_to_anchor=(1.01,-.01),frameon=True,fancybox=False,framealpha=1,edgecolor="#30343A",fontsize=10.5,handlelength=2.8,handleheight=1.1,labelspacing=.2,borderpad=.45,handletextpad=.45)
    return fig

def main():
    p=argparse.ArgumentParser(description=__doc__); h=Path(__file__).resolve().parent; p.add_argument("--data",type=Path,default=h/"stacked-area-round-outcomes.fixture.csv"); p.add_argument("--output-dir",type=Path,default=h); p.add_argument("--qa-preview",type=Path); a=p.parse_args(); print(save_outputs(render(a.data),a.output_dir,"stacked-area-round-outcomes",qa_preview=a.qa_preview))
if __name__=="__main__": main()
