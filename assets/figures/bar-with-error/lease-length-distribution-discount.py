"""Render lease-length histograms and a supplied discount summary with errors."""
from __future__ import annotations
import argparse,sys
from pathlib import Path
import numpy as np
from matplotlib.figure import Figure
PROJECT_ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PROJECT_ROOT))
from chartlib.asset_runtime import read_frame,require_columns,require_finite,save_outputs,style_axis

def load_data(source):
    d=read_frame(source); require_columns(d,("panel","order","x","width","value")); require_finite(d,("order","x","width","value"))
    if d.duplicated(["panel","order"]).any(): raise ValueError("Panel-order keys must be unique.")
    if set(d.panel)!={"hist-short","hist-long","discount"}: raise ValueError("Two histogram panels and one discount panel are required.")
    hist=d[d.panel.str.startswith("hist")]; disc=d[d.panel=="discount"]
    if (hist.value<0).any() or len(disc)!=5 or disc.label.nunique()!=5 or disc[["error","label"]].isna().any().any() or (disc.error<0).any(): raise ValueError("Histogram counts and supplied discount errors are invalid.")
    return d

def render(source):
    d=load_data(source); fig=Figure(figsize=(6.83,7.13),facecolor="white"); gs=fig.add_gridspec(2,2,left=.09,right=.97,bottom=.08,top=.94,wspace=.20,hspace=.42,height_ratios=[1,1.12]); ax1=fig.add_subplot(gs[0,0]); ax2=fig.add_subplot(gs[0,1]); ax3=fig.add_subplot(gs[1,:])
    for ax,panel,ylim,xticks in ((ax1,"hist-short",320,[50,100,150,200,250,300]),(ax2,"hist-long",155,[700,800,900,1000])):
        style_axis(ax,grid=False,full_spines=True); q=d[d.panel==panel].sort_values("order"); ax.bar(q.x,q.value,width=q.width,color="#94969A",edgecolor="#34363A",linewidth=.75); ax.set_ylim(0,ylim); ax.set_xticks(xticks); ax.set_xlabel("Years Remaining on Lease",fontsize=10.5); ax.set_ylabel("Number of Observations",fontsize=10.5); ax.tick_params(labelsize=9,length=4.2)
    ax1.set_yticks([100,200,300],["100k","200k","300k"]); ax2.set_yticks([50,100,150],["50k","100k","150k"]); fig.text(.5,.965,"Histogram of Remaining Lease Length",ha="center",va="top",fontsize=11.5); fig.text(.02,.955,"A",weight="bold",fontsize=15)
    style_axis(ax3,grid=False,full_spines=True); q=d[d.panel=="discount"].sort_values("order"); x=np.arange(5); ax3.bar(x,q.value,width=.72,color="#96989C",edgecolor="#606267",linewidth=.7); ax3.errorbar(x,q.value,yerr=q.error,fmt="none",ecolor="#303136",elinewidth=3,capsize=0); ax3.axhline(0,color="#222",lw=.9); ax3.set_ylim(-.21,.02); ax3.set_yticks([-.2,-.15,-.1,-.05,0],["-.2","-.15","-.1","-.05","0"]); ax3.set_xticks(x,q.label); ax3.set_ylabel("Average Discount to Freehold",fontsize=10.5); ax3.set_xlabel("Lease Length Remaining",fontsize=10.5); ax3.tick_params(labelsize=9,length=4.2); ax3.set_title("Price Discount by Remaining Lease Length",fontsize=11.5,pad=12); fig.text(.02,.49,"B",weight="bold",fontsize=15)
    return fig

def main():
    p=argparse.ArgumentParser(description=__doc__); h=Path(__file__).resolve().parent; p.add_argument("--data",type=Path,default=h/"lease-length-distribution-discount.fixture.csv"); p.add_argument("--output-dir",type=Path,default=h); p.add_argument("--qa-preview",type=Path); a=p.parse_args(); print(save_outputs(render(a.data),a.output_dir,"lease-length-distribution-discount",qa_preview=a.qa_preview))
if __name__=="__main__": main()
