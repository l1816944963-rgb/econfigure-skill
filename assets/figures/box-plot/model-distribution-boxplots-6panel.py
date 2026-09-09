"""Render six model panels with horizontal box summaries for two groups."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
PROJECT_ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PROJECT_ROOT))
from chartlib.asset_runtime import read_frame,require_columns,require_finite,save_outputs,style_axis
STEM="model-distribution-boxplots-6panel"
MODELS=["Exponential","Logit","Lognormal","Normal","Normal(v)","Uniform"]
def load_data(source):
    d=read_frame(source); cols=("model","group","low","q1","median","q3","high"); require_columns(d,cols); require_finite(d,("low","q1","median","q3","high"))
    if list(d.model.drop_duplicates())!=MODELS or set(d.group)!={"CP","MB"}: raise ValueError("Six ordered models and both groups are required.")
    if not ((d.low<=d.q1)&(d.q1<=d["median"])&(d["median"]<=d.q3)&(d.q3<=d.high)).all(): raise ValueError("Every horizontal box summary must have ordered whiskers, quartiles, and median.")
    return d
def render(source):
    d=load_data(source); fig=Figure(figsize=(5.31,6.29),facecolor="white")
    for i,model in enumerate(MODELS):
        ax=fig.add_axes((.16,.845-i*.145,.68,.095)); style_axis(ax,grid=False,full_spines=False); ax.spines["left"].set_visible(False); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False); ax.set_xlim(.38,1.42); ax.set_ylim(-.6,1.6); ax.axvline(1,color="#ef5b5b",lw=1,ls=(0,(3,2)))
        for y,group,color in ((.65,"CP","#bdeaf0"),(.20,"MB","#90d7e4")):
            r=d[(d.model==model)&(d.group==group)].iloc[0]
            ax.hlines(y,r.low,r.high,color="#375677",lw=1.05)
            ax.vlines([r.low,r.high],y-.085,y+.085,color="#375677",lw=1.05)
            ax.add_patch(Rectangle((r.q1,y-.16),r.q3-r.q1,.32,facecolor=color,edgecolor="none"))
            ax.vlines(r["median"],y-.16,y+.16,color="#294b67",lw=1.15)
            ax.text(1.43,y,group,ha="left",va="center",fontsize=7)
        ax.set_title(model,fontsize=7,pad=1); ax.set_yticks([]); ax.set_xticks([.5,.6,.7,.8,.9,1,1.1,1.2,1.3,1.4]); ax.tick_params(axis="x",labelsize=5.5,length=3.8)
    return fig
def main():
    p=argparse.ArgumentParser(description=__doc__); h=Path(__file__).resolve().parent; p.add_argument("--data",type=Path,default=h/f"{STEM}.fixture.csv"); p.add_argument("--output-dir",type=Path,default=h); p.add_argument("--qa-preview",type=Path); a=p.parse_args(); print(save_outputs(render(a.data),a.output_dir,STEM,qa_preview=a.qa_preview))
if __name__=="__main__": main()
