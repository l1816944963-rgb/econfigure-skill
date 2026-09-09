"""Render importance boxplots with supplied outliers for eleven predictors."""
from __future__ import annotations
import argparse,sys
from pathlib import Path
from matplotlib.figure import Figure
PROJECT_ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PROJECT_ROOT))
from chartlib.asset_runtime import read_frame,require_columns,require_finite,save_outputs,style_axis
STEM="importance-boxplot-outliers"
LABELS=["infl","ntis","bm","m2gr","itgr","de","dp","mtr","ep","svar","tms"]
def load_data(source):
    d=read_frame(source); require_columns(d,("label","kind","low","q1","median","q3","high")); require_finite(d,("low","q1","median","q3","high"))
    s=d[d.kind=="summary"]
    if s.label.tolist()!=LABELS or not ((s.low<=s.q1)&(s.q1<=s["median"])&(s["median"]<=s.q3)&(s.q3<=s.high)).all(): raise ValueError("Eleven ordered supplied box summaries are required.")
    if not set(d.kind).issubset({"summary","outlier"}): raise ValueError("Only summary and outlier rows are allowed.")
    return d
def render(source):
    d=load_data(source); fig=Figure(figsize=(10.94,5.2),facecolor="white"); ax=fig.add_axes((.07,.13,.91,.83)); style_axis(ax,grid=True,full_spines=True)
    s=d[d.kind=="summary"]; stats=[]
    for r in s.itertuples():
        f=d[(d.kind=="outlier")&(d.label==r.label)].low.tolist(); stats.append({"label":r.label,"whislo":r.low,"q1":r.q1,"med":r.median,"q3":r.q3,"whishi":r.high,"fliers":f})
    ax.bxp(stats,patch_artist=True,widths=.50,boxprops={"facecolor":"white","edgecolor":"#2020ff","linewidth":1.5},medianprops={"color":"red","linewidth":1.2},whiskerprops={"color":"#222222","linewidth":1.1},capprops={"color":"#222222","linewidth":1.1},flierprops={"marker":"+","markersize":10,"markeredgecolor":"red","markeredgewidth":1.1})
    ax.set_ylim(-3,49); ax.set_ylabel("Importance in %",fontsize=15); ax.tick_params(labelsize=11,length=5,direction="in",top=True,right=True); ax.grid(color="#d7d7d7",lw=.8)
    return fig
def main():
    p=argparse.ArgumentParser(description=__doc__); h=Path(__file__).resolve().parent; p.add_argument("--data",type=Path,default=h/f"{STEM}.fixture.csv"); p.add_argument("--output-dir",type=Path,default=h); p.add_argument("--qa-preview",type=Path); a=p.parse_args(); print(save_outputs(render(a.data),a.output_dir,STEM,qa_preview=a.qa_preview))
if __name__=="__main__": main()
