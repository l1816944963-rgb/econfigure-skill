"""Render eight normalized stacked-bar panels across a standardized position axis."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import numpy as np
PROJECT_ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PROJECT_ROOT))
from chartlib.asset_runtime import read_frame, require_columns, require_finite, save_outputs, style_axis
from matplotlib.figure import Figure

def load_data(source):
    d=read_frame(source); cols=("panel_order","row_group","gamma","position","component","component_order","share"); require_columns(d,cols); d=d.loc[:,cols].copy(); require_finite(d,("panel_order","gamma","position","component_order","share"))
    if set(d.panel_order)!=set(range(1,9)) or d.duplicated(["panel_order","position","component"]).any(): raise ValueError("Eight panels with unique position-component keys are required.")
    sums=d.groupby(["panel_order","position"]).share.sum();
    if not np.allclose(sums,1,atol=.002) or (d.share<0).any(): raise ValueError("Every stack must contain non-negative shares summing to one.")
    return d

def render(data):
    d=load_data(data); fig=Figure(figsize=(12.68,6.66),facecolor="white"); gs=fig.add_gridspec(2,4,left=.038,right=.995,bottom=.055,top=.93,wspace=.09,hspace=.52); colors=["#000000","#A9A9A9","#FFFFFF"]
    for order in range(1,9):
        ax=fig.add_subplot(gs[(order-1)//4,(order-1)%4]); style_axis(ax,full_spines=True); p=d[d.panel_order==order]; xs=sorted(p.position.unique()); bottom=np.zeros(len(xs))
        for co,(component,color) in enumerate(zip(["Allocation 1","Allocation 2","Allocation 3"],colors),1):
            vals=np.array([p[(p.position==x)&(p.component==component)].share.iloc[0] for x in xs]); ax.bar(xs,vals,bottom=bottom,width=.20,color=color,edgecolor="#111111",linewidth=.65); bottom+=vals
        ax.set_xlim(-2.15,2.15); ax.set_ylim(0,1); ax.set_xticks([-2,0,2],["−2 Std","Mean","+2 Std"],fontsize=7); ax.set_yticks(np.arange(0,1.01,.2),labels=[f"{v:.1f}" for v in np.arange(0,1.01,.2)],fontsize=7); ax.set_title(rf"$\gamma = {int(p.gamma.iloc[0])}$",fontsize=14,pad=4)
    fig.text(.5,.495,"With Risk-Free Rate, One-Year Horizon",ha="center",va="center",fontsize=16,family="serif")
    return fig

def main():
    p=argparse.ArgumentParser(description=__doc__); h=Path(__file__).resolve().parent; p.add_argument("--data",type=Path,default=h/"normalized-stacked-vbar-2x4.fixture.csv"); p.add_argument("--output-dir",type=Path,default=h); p.add_argument("--qa-preview",type=Path); a=p.parse_args(); print(save_outputs(render(a.data),a.output_dir,"normalized-stacked-vbar-2x4",qa_preview=a.qa_preview))
if __name__=="__main__": main()
