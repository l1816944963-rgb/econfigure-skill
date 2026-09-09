"""Render a two-by-two grid of labeled 100-percent horizontal decompositions."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import numpy as np
PROJECT_ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PROJECT_ROOT))
from chartlib.asset_runtime import read_frame, require_columns, require_finite, save_outputs, style_axis
from matplotlib.figure import Figure
from matplotlib.patches import Patch

def load_data(source):
    d=read_frame(source); cols=("panel","panel_order","category","category_order","component","component_order","share"); require_columns(d,cols); d=d.loc[:,cols].copy(); require_finite(d,("panel_order","category_order","component_order","share"))
    if set(d.panel_order)!={1,2,3,4} or d.duplicated(["panel","category","component"]).any() or (d.share<0).any(): raise ValueError("Four complete non-negative decomposition panels are required.")
    if not np.allclose(d.groupby(["panel","category"]).share.sum(),100,atol=.2): raise ValueError("Every decomposition must sum to 100 percent.")
    return d

def render(data):
    d=load_data(data); fig=Figure(figsize=(7.30,5.29),facecolor="white"); gs=fig.add_gridspec(2,2,left=.115,right=.905,bottom=.10,top=.94,wspace=.30,hspace=.62); colors=["#D1D1D1","#414070","#7070C9","#D0CF63","#707070"]
    for order in range(1,5):
        ax=fig.add_subplot(gs[(order-1)//2,(order-1)%2]); style_axis(ax); p=d[d.panel_order==order]; cats=p.sort_values("category_order").category.drop_duplicates().tolist(); y=np.arange(len(cats)); left=np.zeros(len(cats))
        for co,(component,color) in enumerate(zip(p.sort_values("component_order").component.drop_duplicates(),colors),1):
            vals=np.array([p[(p.category==c)&(p.component==component)].share.iloc[0] for c in cats]); bars=ax.barh(y,vals,left=left,height=.58,color=color,edgecolor="white",linewidth=.4)
            for bar,val in zip(bars,vals):
                if val>=6: ax.text(bar.get_x()+bar.get_width()/2,bar.get_y()+bar.get_height()/2,f"{val:.1f}",ha="center",va="center",fontsize=5.2,color="white" if co in [2,3,5] else "#222222")
            left+=vals
        ax.set_xlim(0,100); ax.set_xticks(range(0,101,20)); ax.set_yticks(y,cats,fontsize=5.8); ax.tick_params(axis="x",pad=4); ax.invert_yaxis(); ax.set_title(f"({chr(64+order)}) {p.panel.iloc[0]}",fontsize=12,family="serif",pad=6)
        handles=[Patch(facecolor=c,edgecolor="#555555",linewidth=.4,label=l) for c,l in zip(colors,["Fixed Income","C-corp","Pass-through","Housing","Pensions, Other"])]
        ax.legend(handles=handles,loc="upper center",bbox_to_anchor=(.5,-.19),ncol=5,frameon=False,fontsize=5.8,handlelength=1.1,handleheight=.9,handletextpad=.32,columnspacing=.65,labelspacing=.45,borderaxespad=0)
    return fig

def main():
    p=argparse.ArgumentParser(description=__doc__); h=Path(__file__).resolve().parent; p.add_argument("--data",type=Path,default=h/"decomposition-100pct-hbar-2x2.fixture.csv"); p.add_argument("--output-dir",type=Path,default=h); p.add_argument("--qa-preview",type=Path); a=p.parse_args(); print(save_outputs(render(a.data),a.output_dir,"decomposition-100pct-hbar-2x2",qa_preview=a.qa_preview))
if __name__=="__main__": main()
