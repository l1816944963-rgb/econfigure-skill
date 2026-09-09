"""Render a two-by-two benchmark-versus-alternative grouped bar figure."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import numpy as np, pandas as pd
PROJECT_ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PROJECT_ROOT))
from chartlib.asset_runtime import read_frame, require_columns, require_finite, save_outputs, style_axis
from matplotlib.figure import Figure
from matplotlib.ticker import FixedLocator

def load_data(source):
    d=read_frame(source); cols=("panel","panel_order","period","period_order","series","series_order","value"); require_columns(d,cols); d=d.loc[:,cols].copy(); require_finite(d,("panel_order","period_order","series_order","value"))
    if d.panel.nunique()!=4 or set(d.panel_order)!={1,2,3,4}: raise ValueError("Exactly four ordered panels are required.")
    if d.duplicated(["panel","period","series"]).any() or (d.value<0).any(): raise ValueError("Panel-period-series keys must be unique and non-negative.")
    if not (d.groupby(["panel","period"]).series.nunique()==2).all(): raise ValueError("Every panel-period requires two series.")
    return d

def render(data):
    d=load_data(data); fig=Figure(figsize=(6.79,6.08),facecolor="white"); gs=fig.add_gridspec(2,2,left=.095,right=.975,bottom=.08,top=.98,wspace=.19,hspace=.08)
    for order in range(1,5):
        ax=fig.add_subplot(gs[(order-1)//2,(order-1)%2]); style_axis(ax,grid=True,full_spines=True); p=d[d.panel_order==order]; periods=p.sort_values("period_order").period.drop_duplicates().tolist(); alt=p.panel.iloc[0]; x=np.arange(2)
        for so,(series,color,offset) in enumerate([("Benchmark","#C6504D",-.14),(alt,"#5286BE",.14)],1):
            vals=[p[(p.period==q)&(p.series==series)].value.iloc[0] for q in periods]; ax.bar(x+offset,vals,width=.28,color=color,zorder=3,label=series)
        ax.set_ylim(0,15.5); ax.set_yticks(range(0,15,2),labels=[f"{v}%" for v in range(0,15,2)]); ax.set_xlim(-.5,1.5); ax.set_xticks(x,periods,fontsize=7.5); ax.tick_params(axis="x",which="major",length=0,pad=6); ax.xaxis.set_minor_locator(FixedLocator([-.5,.5,1.5])); ax.tick_params(axis="x",which="minor",bottom=True,top=False,direction="out",length=4.2,width=.8,color="#45484C"); ax.legend(loc="upper left",bbox_to_anchor=(.03,.96),frameon=True,fancybox=False,framealpha=1,fontsize=9.5,handlelength=1.0,handleheight=1.0,handletextpad=.45,labelspacing=.55,borderpad=.75)
    return fig

def main():
    p=argparse.ArgumentParser(description=__doc__); h=Path(__file__).resolve().parent; p.add_argument("--data",type=Path,default=h/"grouped-vbar-benchmark-2x2.fixture.csv"); p.add_argument("--output-dir",type=Path,default=h); p.add_argument("--qa-preview",type=Path); a=p.parse_args(); print(save_outputs(render(a.data),a.output_dir,"grouped-vbar-benchmark-2x2",qa_preview=a.qa_preview))
if __name__=="__main__": main()
