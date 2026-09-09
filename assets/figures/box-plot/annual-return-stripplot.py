"""Render annual inflation-adjusted return observations as a horizontal strip plot."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
from matplotlib.figure import Figure
PROJECT_ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PROJECT_ROOT))
from chartlib.asset_runtime import read_frame,require_columns,require_finite,save_outputs,style_axis
STEM="annual-return-stripplot"
def load_data(source):
    d=read_frame(source); require_columns(d,("year","return_value")); require_finite(d,("year","return_value"))
    if sorted(d.year.unique())!=list(range(1980,2002)) or d.groupby("year").size().min()<4: raise ValueError("Continuous years 1980 through 2001 with at least four observations each are required.")
    return d
def render(source):
    d=load_data(source); fig=Figure(figsize=(8.41,6.46),facecolor="white"); ax=fig.add_axes((.17,.11,.78,.82)); style_axis(ax,grid=True,full_spines=True)
    ax.scatter(d.return_value,d.year,s=18,color="#4d4d4d",alpha=.86,linewidths=0); ax.axvline(0,color="#8b8b8b",lw=.8); ax.set_xlim(-23000,21000); ax.set_ylim(2001.7,1979.3); ax.set_yticks(range(1980,2002)); ax.set_xticks([-20000,-10000,0,10000,20000],["-20,000","-10,000","0","10,000","20,000"]); ax.set_xlabel("Inflation-adjusted dollar returns",fontsize=11); ax.set_title("Year",loc="left",fontsize=12,pad=10); ax.tick_params(labelsize=9,length=0); ax.grid(axis="x",color="#d8d8d8",lw=.8); ax.grid(axis="y",visible=False)
    return fig
def main():
    p=argparse.ArgumentParser(description=__doc__); h=Path(__file__).resolve().parent; p.add_argument("--data",type=Path,default=h/f"{STEM}.fixture.csv"); p.add_argument("--output-dir",type=Path,default=h); p.add_argument("--qa-preview",type=Path); a=p.parse_args(); print(save_outputs(render(a.data),a.output_dir,STEM,qa_preview=a.qa_preview))
if __name__=="__main__": main()
