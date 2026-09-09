"""Render paired stacked vertical bars for two samples across years."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import numpy as np
PROJECT_ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PROJECT_ROOT))
from chartlib.asset_runtime import read_frame, require_columns, require_finite, save_outputs, style_axis
from matplotlib.figure import Figure
from matplotlib.patches import Patch

def load_data(source):
    d=read_frame(source); cols=("year","sample","sample_order","component","component_order","value"); require_columns(d,cols); d=d.loc[:,cols].copy(); require_finite(d,("year","sample_order","component_order","value"))
    if d.duplicated(["year","sample","component"]).any() or (d.value<0).any(): raise ValueError("Year-sample-component keys must be unique and non-negative.")
    if not (d.groupby(["year","sample"]).component.nunique()==2).all(): raise ValueError("Every sample-year requires both stack components.")
    return d

def render(data):
    d=load_data(data); fig=Figure(figsize=(7.85,3.86),facecolor="white"); ax=fig.add_axes((54/785,36/386,701/785,338/386)); style_axis(ax,full_spines=True); years=sorted(d.year.unique()); x=np.arange(len(years)); samples=["Aggregate banking sector","Firms in KIS data"]; offsets=[-.18,.18]; colors={"ST":"#3F3AA2","LT":"#B7B7B7"}
    for sample,offset in zip(samples,offsets):
        bottom=np.zeros(len(years))
        for component in ["ST","LT"]:
            vals=np.array([d[(d.year==y)&(d["sample"]==sample)&(d.component==component)].value.iloc[0] for y in years]); ax.bar(x+offset,vals,bottom=bottom,width=.30,color=colors[component],edgecolor="#111111",linewidth=1); bottom+=vals
    ax.set_ylim(0,120); ax.set_yticks(range(0,121,20)); ax.set_xticks(x,years); ax.tick_params(axis="both",length=0); ax.annotate("Aggregate Banking Sector",xy=(1.7,86),xytext=(-.1,107),arrowprops=dict(arrowstyle="-|>",color="black",lw=1.2),fontsize=11); ax.annotate("Firms in KIS Data",xy=(4.18,34),xytext=(3.8,101),arrowprops=dict(arrowstyle="-|>",color="black",lw=1.2),fontsize=11)
    ax.legend(handles=[Patch(facecolor=colors["LT"],edgecolor="black",label="LT"),Patch(facecolor=colors["ST"],edgecolor="black",label="ST")],loc="upper right",bbox_to_anchor=(.92,.94),frameon=False,fontsize=12.5,handlelength=1.0,handleheight=.9,handletextpad=.45,labelspacing=.55,borderaxespad=0)
    return fig

def main():
    p=argparse.ArgumentParser(description=__doc__); h=Path(__file__).resolve().parent; p.add_argument("--data",type=Path,default=h/"paired-stacked-vbar-sector.fixture.csv"); p.add_argument("--output-dir",type=Path,default=h); p.add_argument("--qa-preview",type=Path); a=p.parse_args(); print(save_outputs(render(a.data),a.output_dir,"paired-stacked-vbar-sector",qa_preview=a.qa_preview))
if __name__=="__main__": main()
