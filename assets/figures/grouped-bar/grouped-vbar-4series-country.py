"""Render four-series grouped country bars on a percent scale."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import numpy as np
PROJECT_ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PROJECT_ROOT))
from chartlib.asset_runtime import read_frame, require_columns, require_finite, save_outputs, style_axis
from matplotlib.figure import Figure
from matplotlib.ticker import FixedLocator

def load_data(source):
    d=read_frame(source); cols=("country","country_order","series","series_order","value"); require_columns(d,cols); d=d.loc[:,cols].copy(); require_finite(d,("country_order","series_order","value"))
    if d.series.nunique()!=4 or d.duplicated(["country","series"]).any() or (d.value<0).any(): raise ValueError("Four complete non-negative series are required.")
    if not (d.groupby("country").series.nunique()==4).all(): raise ValueError("Every country requires four series.")
    return d

def render(data):
    d=load_data(data); fig=Figure(figsize=(10.67,5.05),facecolor="white"); ax=fig.add_axes((59/1067,31/505,917/1067,458/505)); style_axis(ax,grid=True,full_spines=True); countries=d.sort_values("country_order").country.drop_duplicates().tolist(); series=d.sort_values("series_order").series.drop_duplicates().tolist(); x=np.arange(len(countries)); colors=["#C9C9F4","#DCC8D0","#FFF85D","#64E4E8"]
    for i,(s,c) in enumerate(zip(series,colors)):
        vals=[d[(d.country==q)&(d.series==s)].value.iloc[0] for q in countries]; ax.bar(x+(i-1.5)*.19,vals,width=.18,color=c,edgecolor="#222222",linewidth=.7,label=s,zorder=3)
    ax.set_ylim(0,35); ax.set_yticks(range(0,36,5)); ax.set_xlim(-.5,len(countries)-.5); ax.set_xticks(x,countries,fontsize=8); ax.tick_params(axis="x",which="major",length=0); ax.xaxis.set_minor_locator(FixedLocator(np.arange(len(countries)+1)-.5)); ax.tick_params(axis="x",which="minor",bottom=True,top=False,direction="out",length=4.2,width=.8,color="#45484C"); ax.set_ylabel("Percent of firms exposed at 5% level",fontsize=9); ax.legend(loc="center left",bbox_to_anchor=(1.01,.50),frameon=True,fancybox=False,fontsize=9.5,handlelength=1.0,handleheight=1.0,handletextpad=.5,labelspacing=.5,borderpad=.6)
    return fig

def main():
    p=argparse.ArgumentParser(description=__doc__); h=Path(__file__).resolve().parent; p.add_argument("--data",type=Path,default=h/"grouped-vbar-4series-country.fixture.csv"); p.add_argument("--output-dir",type=Path,default=h); p.add_argument("--qa-preview",type=Path); a=p.parse_args(); print(save_outputs(render(a.data),a.output_dir,"grouped-vbar-4series-country",qa_preview=a.qa_preview))
if __name__=="__main__": main()
