"""Render control and treatment sales-density comparisons at baseline and endline."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
from matplotlib.figure import Figure
PROJECT_ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PROJECT_ROOT))
from chartlib.asset_runtime import read_frame,require_columns,require_finite,save_outputs,style_axis
STEM="sales-density-baseline-endline-2panel"
def load_data(source):
    d=read_frame(source); require_columns(d,("panel","series","line","x","density")); require_finite(d,("x","density"))
    if set(d.panel)!={"Control","Treatment"} or set(d.series)!={"Baseline","Endline"} or (d.density<0).any(): raise ValueError("Control and treatment panels each require baseline and endline densities.")
    return d
def render(source):
    d=load_data(source); fig=Figure(figsize=(7.46,3.05),facecolor="white")
    for i,panel in enumerate(("Control","Treatment")):
        ax=fig.add_axes((.09+i*.48,.36,.39,.57)); style_axis(ax,grid=True,full_spines=False); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        for series,color,ls in (("Baseline","#2f557f","-"),("Endline","#d97872","--")):
            q=d[(d.panel==panel)&(d.series==series)].sort_values("x"); ax.plot(q.x,q.density,color=color,lw=1.45,ls=ls,label=f"{panel} {series}")
        ax.set_xlim(-5,15); ax.set_ylim(0,.205); ax.set_yticks([0,.05,.10,.15,.20]); ax.set_xlabel("log Sales",fontsize=8,labelpad=3); ax.set_ylabel("Density",fontsize=8); ax.tick_params(labelsize=7,length=3.5); ax.legend(loc="upper center",bbox_to_anchor=(.5,-.28),fontsize=6.5,frameon=True,ncols=2,handlelength=3,columnspacing=1.0,borderpad=.45)
    return fig
def main():
    p=argparse.ArgumentParser(description=__doc__); h=Path(__file__).resolve().parent; p.add_argument("--data",type=Path,default=h/f"{STEM}.fixture.csv"); p.add_argument("--output-dir",type=Path,default=h); p.add_argument("--qa-preview",type=Path); a=p.parse_args(); print(save_outputs(render(a.data),a.output_dir,STEM,qa_preview=a.qa_preview))
if __name__=="__main__": main()
