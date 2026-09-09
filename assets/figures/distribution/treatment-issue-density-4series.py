"""Render four treatment-control issue-position density curves."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
from matplotlib.figure import Figure
PROJECT_ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PROJECT_ROOT))
from chartlib.asset_runtime import read_frame,require_columns,require_finite,save_outputs,style_axis
STEM="treatment-issue-density-4series"
def load_data(source):
    d=read_frame(source); require_columns(d,("series","color","line","x","density")); require_finite(d,("x","density"))
    if d.series.nunique()!=4 or (d.density<0).any() or d.groupby("series").x.nunique().min()<100: raise ValueError("Four dense non-negative supplied curves are required.")
    return d
def render(source):
    d=load_data(source); fig=Figure(figsize=(4.83,3.65),facecolor="white"); ax=fig.add_axes((.15,.36,.80,.57)); style_axis(ax,grid=True,full_spines=False); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    for series,q in d.groupby("series",sort=False):
        r=q.iloc[0]; ax.plot(q.x,q.density,color=r.color,lw=1.8,ls="--" if r.line=="dashed" else "-",label=series)
    ax.set_xlim(-4,4); ax.set_ylim(0,.64); ax.set_yticks([0,.2,.4,.6]); ax.set_xlabel("Issue opinions (in units of Control group standard deviations)",fontsize=7.5,labelpad=3); ax.set_ylabel("Density",fontsize=8); ax.tick_params(labelsize=7,length=3.5); ax.legend(loc="upper center",bbox_to_anchor=(.5,-.25),ncols=2,fontsize=6.5,frameon=True,handlelength=3,columnspacing=1.0,borderpad=.45); fig.text(.15,.035,"kernel = epanechnikov, bandwidth = 0.2231",fontsize=6)
    return fig
def main():
    p=argparse.ArgumentParser(description=__doc__); h=Path(__file__).resolve().parent; p.add_argument("--data",type=Path,default=h/f"{STEM}.fixture.csv"); p.add_argument("--output-dir",type=Path,default=h); p.add_argument("--qa-preview",type=Path); a=p.parse_args(); print(save_outputs(render(a.data),a.output_dir,STEM,qa_preview=a.qa_preview))
if __name__=="__main__": main()
