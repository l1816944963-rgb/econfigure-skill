"""Render cumulative-frequency profiles for small and large markets."""
from __future__ import annotations
import argparse,sys
from pathlib import Path
from matplotlib.figure import Figure
PROJECT_ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PROJECT_ROOT))
from chartlib.asset_runtime import read_frame,require_columns,require_finite,save_outputs,style_axis

def load_data(source):
    d=read_frame(source); require_columns(d,("series","age","cumulative_frequency")); require_finite(d,("age","cumulative_frequency"));
    if set(d.series)!={"SMALL MARKET","LARGE MARKET"} or d.duplicated(["series","age"]).any(): raise ValueError("Two complete market series with unique ages are required.")
    for _,q in d.groupby("series"):
        q=q.sort_values("age")
        if list(q.age)!=list(range(1,61)) or not q.cumulative_frequency.is_monotonic_increasing: raise ValueError("Ages 1 through 60 and non-decreasing cumulative frequencies are required.")
    return d

def render(source):
    d=load_data(source); fig=Figure(figsize=(8.04,4.78),facecolor="white"); ax=fig.add_axes((.095,.11,.83,.84)); style_axis(ax,grid=True,full_spines=True)
    for series,color,lw in (("SMALL MARKET","#50545A",1.0),("LARGE MARKET","#30343A",1.9)):
        q=d[d.series==series].sort_values("age"); ax.plot(q.age,q.cumulative_frequency,color=color,lw=lw,label=series)
    ax.set_xlim(0,61); ax.set_ylim(0,400); ax.set_xticks(range(0,61,2)); ax.set_yticks(range(0,401,50)); ax.set_xlabel("AGE",fontsize=11,weight="bold"); ax.set_ylabel("Cumulative frequency",fontsize=10.5,weight="bold"); ax.tick_params(labelsize=8.5,length=4.2)
    ax.legend(loc="lower right",bbox_to_anchor=(.99,.13),ncols=2,frameon=True,fancybox=False,edgecolor="#444",fontsize=8.5,handlelength=1.7,handletextpad=.2,columnspacing=.6,borderpad=.25,labelspacing=.1)
    return fig

def main():
    p=argparse.ArgumentParser(description=__doc__); h=Path(__file__).resolve().parent; p.add_argument("--data",type=Path,default=h/"cumulative-frequency-market-age.fixture.csv"); p.add_argument("--output-dir",type=Path,default=h); p.add_argument("--qa-preview",type=Path); a=p.parse_args(); print(save_outputs(render(a.data),a.output_dir,"cumulative-frequency-market-age",qa_preview=a.qa_preview))
if __name__=="__main__": main()
