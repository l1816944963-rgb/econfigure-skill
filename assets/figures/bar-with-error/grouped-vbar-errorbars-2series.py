"""Render two-series grouped bars with supplied symmetric error bars."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import numpy as np
PROJECT_ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PROJECT_ROOT))
from chartlib.asset_runtime import read_frame, require_columns, require_finite, save_outputs, style_axis
from matplotlib.figure import Figure
from matplotlib.ticker import FixedLocator

def load_data(source):
    d=read_frame(source); cols=("utility_difference","category_order","series","series_order","estimate","error"); require_columns(d,cols); d=d.loc[:,cols].copy(); require_finite(d,("utility_difference","category_order","series_order","estimate","error"))
    if d.series.nunique()!=2 or d.duplicated(["utility_difference","series"]).any(): raise ValueError("Exactly two complete series are required.")
    if (d.estimate<0).any() or (d.error<0).any() or not (d.groupby("utility_difference").series.nunique()==2).all(): raise ValueError("Estimates and supplied errors must be non-negative and complete.")
    return d

def render(data):
    d=load_data(data); fig=Figure(figsize=(4.82,4.59),facecolor="white"); ax=fig.add_axes((78/482,82/459,382/482,347/459)); style_axis(ax,grid=True,full_spines=True); cats=d.sort_values("category_order").utility_difference.drop_duplicates().tolist(); x=np.arange(len(cats))
    for s,color,offset in [("State 1","#303030",-.14),("State 2","#FFFFFF",.14)]:
        p=d[d.series==s].sort_values("category_order"); positions=x+offset; ax.bar(positions,p.estimate,width=.28,color=color,edgecolor="#222222",linewidth=1.2,label=s,zorder=3)
        if s=="State 1":
            for xpos,estimate,error in zip(positions,p.estimate,p.error):
                cap=.055; ax.vlines(xpos,estimate-error,estimate,color="white",linewidth=1.8,zorder=5); ax.hlines(estimate-error,xpos-cap,xpos+cap,color="white",linewidth=1.8,zorder=5); ax.vlines(xpos,estimate,estimate+error,color="#222222",linewidth=1.5,zorder=5); ax.hlines(estimate+error,xpos-cap,xpos+cap,color="#222222",linewidth=1.5,zorder=5)
        else:
            ax.errorbar(positions,p.estimate,yerr=p.error,fmt="none",ecolor="#222222",elinewidth=1.5,capsize=5,zorder=5)
    ax.set_ylim(0,120); ax.set_yticks(range(0,121,20)); ax.set_xlim(-.5,len(cats)-.5); ax.set_xticks(x,[str(v) for v in cats]); ax.tick_params(axis="x",which="major",length=0); ax.xaxis.set_minor_locator(FixedLocator(np.arange(len(cats)+1)-.5)); ax.tick_params(axis="x",which="minor",bottom=True,top=False,direction="out",length=4.2,width=.8,color="#45484C"); ax.set_xlabel("Utility Difference",fontsize=12.5,weight="bold",labelpad=10); ax.set_ylabel("Estimated Cost",fontsize=11.5,weight="bold"); ax.legend(loc="upper left",frameon=False,fontsize=12,handlelength=1.0,handleheight=.9,handletextpad=.45,labelspacing=.65)
    return fig

def main():
    p=argparse.ArgumentParser(description=__doc__); h=Path(__file__).resolve().parent; p.add_argument("--data",type=Path,default=h/"grouped-vbar-errorbars-2series.fixture.csv"); p.add_argument("--output-dir",type=Path,default=h); p.add_argument("--qa-preview",type=Path); a=p.parse_args(); print(save_outputs(render(a.data),a.output_dir,"grouped-vbar-errorbars-2series",qa_preview=a.qa_preview))
if __name__=="__main__": main()
