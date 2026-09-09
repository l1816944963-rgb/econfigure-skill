"""Render outcome-level horizontal 100-percent factor decompositions."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import numpy as np
PROJECT_ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PROJECT_ROOT))
from chartlib.asset_runtime import read_frame, require_columns, require_finite, save_outputs, style_axis
from matplotlib.figure import Figure
from matplotlib.patches import Patch

def load_data(source):
    d=read_frame(source); cols=("outcome","outcome_order","component","component_order","share","left_label","right_label"); require_columns(d,cols); d=d.loc[:,cols].copy(); require_finite(d,("outcome_order","component_order","share"))
    if d.duplicated(["outcome","component"]).any() or (d.share<0).any(): raise ValueError("Outcome-component keys must be unique and non-negative.")
    if not np.allclose(d.groupby("outcome").share.sum(),1): raise ValueError("Every outcome decomposition must sum to one.")
    return d

def render(data):
    d=load_data(data); fig=Figure(figsize=(6.40,3.60),facecolor="white"); ax=fig.add_axes((267/640,53/360,337/640,285/360)); style_axis(ax); outcomes=d.sort_values("outcome_order").outcome.drop_duplicates().tolist(); y=np.arange(len(outcomes)); left=np.zeros(len(outcomes)); colors=["#E94D3D","#FFFFFF","#D6F2D7","#F7F7F7"]; hatches=[None,"----","++++","......"]
    for component,color,hatch in zip(d.sort_values("component_order").component.drop_duplicates(),colors,hatches):
        vals=np.array([d[(d.outcome==o)&(d.component==component)].share.iloc[0] for o in outcomes]); ax.barh(y,vals,left=left,height=.44,color=color,edgecolor="#20A8D8" if component=="Externalizing behavior" else "#777777",linewidth=.7,hatch=hatch,label=component); left+=vals
    ax.set_xlim(0,1); ax.set_ylim(-.68,len(outcomes)-.5); ax.set_xticks(np.arange(0,1.01,.2),labels=[f"{int(v*100)}%" for v in np.arange(0,1.01,.2)]); ax.tick_params(axis="x",length=0,pad=5); ax.set_yticks(y,outcomes,fontsize=6.6); ax.tick_params(axis="y",length=0); ax.invert_yaxis()
    labels=d.sort_values("outcome_order").drop_duplicates("outcome")
    for yy,row in zip(y,labels.itertuples(index=False)):
        ax.text(.012,yy-.30,row.left_label,ha="left",va="bottom",fontsize=6.2)
        ax.text(.988,yy-.30,row.right_label,ha="right",va="bottom",fontsize=6.2)
    handles=[Patch(facecolor=c,edgecolor="#777777",hatch=h,label=l) for c,h,l in zip(colors,hatches,["Cognitive factor","Externalizing behavior","Academic motivation","Other factors"])]
    legend=fig.legend(handles=handles,loc="lower center",bbox_to_anchor=(.50,.005),ncol=4,frameon=True,fancybox=False,fontsize=7.2,handlelength=1.3,handleheight=1.0,columnspacing=1.0,handletextpad=.5,labelspacing=.5,borderpad=.7); legend.get_frame().set_edgecolor("#555555"); legend.get_frame().set_linewidth(.8)
    return fig

def main():
    p=argparse.ArgumentParser(description=__doc__); h=Path(__file__).resolve().parent; p.add_argument("--data",type=Path,default=h/"decomposition-100pct-hbar-outcomes.fixture.csv"); p.add_argument("--output-dir",type=Path,default=h); p.add_argument("--qa-preview",type=Path); a=p.parse_args(); print(save_outputs(render(a.data),a.output_dir,"decomposition-100pct-hbar-outcomes",qa_preview=a.qa_preview))
if __name__=="__main__": main()
