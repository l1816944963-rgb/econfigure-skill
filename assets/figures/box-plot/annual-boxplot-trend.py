"""Render annual boxplot summaries as a rising time sequence."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
from matplotlib.figure import Figure
PROJECT_ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PROJECT_ROOT))
from chartlib.asset_runtime import read_frame,require_columns,require_finite,save_outputs,style_axis
STEM="annual-boxplot-trend"
def load_data(source):
    d=read_frame(source); cols=("year","low","q1","median","q3","high"); require_columns(d,cols+("outlier_low","outlier_high")); require_finite(d,cols)
    if d.year.tolist()!=list(range(1982,1996)): raise ValueError("Continuous annual summaries from 1982 through 1995 are required.")
    if not ((d.low<=d.q1)&(d.q1<=d["median"])&(d["median"]<=d.q3)&(d.q3<=d.high)).all(): raise ValueError("Every five-number summary must be ordered.")
    return d
def render(source):
    d=load_data(source); fig=Figure(figsize=(7.75,5.8),facecolor="white"); ax=fig.add_axes((.12,.30,.83,.62)); style_axis(ax,grid=False,full_spines=False); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    stats=[{"label":str(int(r.year)),"whislo":r.low,"q1":r.q1,"med":r.median,"q3":r.q3,"whishi":r.high,"fliers":[v for v in (r.outlier_low,r.outlier_high) if v==v]} for r in d.itertuples()]
    ax.bxp(stats,showfliers=True,widths=.62,patch_artist=True,boxprops={"facecolor":"white","edgecolor":"#777777","linewidth":1},medianprops={"color":"#777777","linewidth":1.2},whiskerprops={"color":"#777777"},capprops={"color":"#777777"},flierprops={"marker":"_","markersize":6,"markeredgecolor":"#777777"})
    ax.set_ylim(-8,8); ax.set_title("Box Plot",fontsize=14,fontweight="bold",pad=10); ax.set_xlabel("year",fontsize=10,fontweight="bold",labelpad=86); ax.tick_params(axis="x",labelbottom=False,length=0); ax.tick_params(axis="y",labelsize=9,length=4)
    for i,year in enumerate(d.year): ax.text(i+1,-.085 if i%2==0 else -.205,str(int(year)),transform=ax.get_xaxis_transform(),ha="center",va="top",fontsize=7.5,fontweight="bold")
    return fig
def main():
    p=argparse.ArgumentParser(description=__doc__); h=Path(__file__).resolve().parent; p.add_argument("--data",type=Path,default=h/f"{STEM}.fixture.csv"); p.add_argument("--output-dir",type=Path,default=h); p.add_argument("--qa-preview",type=Path); a=p.parse_args(); print(save_outputs(render(a.data),a.output_dir,STEM,qa_preview=a.qa_preview))
if __name__=="__main__": main()
