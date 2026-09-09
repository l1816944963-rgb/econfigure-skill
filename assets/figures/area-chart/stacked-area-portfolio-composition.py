"""Render a seven-component normalized portfolio area chart."""
from __future__ import annotations
import argparse,sys
from pathlib import Path
import numpy as np
from matplotlib.figure import Figure
from matplotlib.patches import Patch
PROJECT_ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PROJECT_ROOT))
from chartlib.asset_runtime import read_frame,require_columns,require_finite,save_outputs,style_axis

def load_data(source):
    d=read_frame(source); cols=("year","component","component_order","share"); require_columns(d,cols); d=d.loc[:,cols].copy(); require_finite(d,("year","component_order","share"))
    if d.duplicated(["year","component"]).any() or d.component.nunique()!=7: raise ValueError("Unique year-component keys and exactly seven components are required.")
    if (d.share<0).any() or not np.allclose(d.groupby("year").share.sum(),100,atol=1e-8): raise ValueError("Every year must contain non-negative shares summing to 100.")
    if sorted(d.year.unique())!=list(range(2011,2016)): raise ValueError("Continuous years 2011 through 2015 are required.")
    return d

def render(source):
    d=load_data(source); fig=Figure(figsize=(8.4,6.44),facecolor="white"); ax=fig.add_axes((.075,.18,.90,.78)); style_axis(ax,full_spines=False); ax.spines["left"].set_visible(False); ax.spines["bottom"].set_visible(False)
    years=np.arange(2011,2016); comps=d.sort_values("component_order").component.drop_duplicates().tolist(); vals=[d[d.component==c].sort_values("year").share.to_numpy() for c in comps]
    colors=["#ED6AD0","#A893F0","#35B5DE","#2FC2A0","#71C42B","#D2AD28","#F78782"]
    ax.stackplot(years,*vals,colors=colors,edgecolor="#202020",linewidth=.75,alpha=.96)
    ax.set_xlim(2010.8,2015.2); ax.set_ylim(0,105); ax.set_xticks(years); ax.set_yticks([0,25,50,75,100],["0%","25%","50%","75%","100%"]); ax.grid(True,color="#FFFFFF",linewidth=.34,alpha=.22); ax.tick_params(length=0,labelsize=13)
    order=[6,5,4,3,2,1,0]; handles=[Patch(facecolor=colors[i],edgecolor="#202020",label=comps[i]) for i in order]
    ax.legend(handles=handles,loc="upper center",bbox_to_anchor=(.5,-.105),ncols=4,frameon=False,fontsize=11.5,handlelength=.8,handleheight=1.1,columnspacing=1.1,handletextpad=.35,labelspacing=.15)
    return fig

def main():
    p=argparse.ArgumentParser(description=__doc__); h=Path(__file__).resolve().parent; p.add_argument("--data",type=Path,default=h/"stacked-area-portfolio-composition.fixture.csv"); p.add_argument("--output-dir",type=Path,default=h); p.add_argument("--qa-preview",type=Path); a=p.parse_args(); print(save_outputs(render(a.data),a.output_dir,"stacked-area-portfolio-composition",qa_preview=a.qa_preview))
if __name__=="__main__": main()
