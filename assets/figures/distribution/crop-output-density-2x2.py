"""Render four crop-output density panels with histogram-like bars and density outlines."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import numpy as np
from matplotlib.figure import Figure
PROJECT_ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PROJECT_ROOT))
from chartlib.asset_runtime import read_frame,require_columns,require_finite,save_outputs,style_axis
STEM="crop-output-density-2x2"
def load_data(source):
    d=read_frame(source); require_columns(d,("panel","x","density")); require_finite(d,("x","density"))
    if d.panel.nunique()!=4 or (d.density<0).any(): raise ValueError("Four non-negative density series are required.")
    if d.groupby("panel").x.nunique().min()<50: raise ValueError("Every panel requires at least 50 supplied density points.")
    return d
def render(source):
    d=load_data(source); fig=Figure(figsize=(7.62,4.76),facecolor="white")
    for i,(panel,q) in enumerate(d.groupby("panel",sort=False)):
        row,col=divmod(i,2); ax=fig.add_axes((.09+col*.46,.56-row*.45,.41,.36)); style_axis(ax,grid=True,full_spines=False); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False); q=q.sort_values("x"); dx=np.diff(q.x).mean()
        ax.bar(q.x.iloc[::2],q.density.iloc[::2],width=dx*1.82,color="#888888",edgecolor="#303030",linewidth=.42,zorder=2); ax.plot(q.x,q.density,color="#303030",lw=1.2,zorder=3)
        ax.axvline(0,color="#777777",lw=.8); ax.set_xlim(-5.4,5.4); ax.set_ylim(0,.68); ax.set_title(panel,fontsize=12,pad=6); ax.tick_params(labelsize=8,length=3.5); ax.set_xlabel("",fontsize=9)
        if col==0: ax.set_ylabel("Density",fontsize=10)
        else: ax.set_yticklabels([])
    return fig
def main():
    p=argparse.ArgumentParser(description=__doc__); h=Path(__file__).resolve().parent; p.add_argument("--data",type=Path,default=h/f"{STEM}.fixture.csv"); p.add_argument("--output-dir",type=Path,default=h); p.add_argument("--qa-preview",type=Path); a=p.parse_args(); print(save_outputs(render(a.data),a.output_dir,STEM,qa_preview=a.qa_preview))
if __name__=="__main__": main()
