"""Render four transaction-price scatter panels against an identity line."""
from __future__ import annotations
import argparse,sys
from pathlib import Path
from matplotlib.figure import Figure
PROJECT_ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PROJECT_ROOT))
from chartlib.asset_runtime import read_frame,require_columns,require_finite,save_outputs,style_axis

def load_data(source):
    d=read_frame(source); require_columns(d,("panel","kind","x","y")); require_finite(d,("x","y"));
    if d.panel.nunique()!=4 or set(d.kind)!={"point","identity"} or (d[["x","y"]]<0).any().any(): raise ValueError("Four non-negative scatter panels with identity lines are required.")
    for _,q in d.groupby("panel"):
        identity=q[q.kind=="identity"]
        if len(q[q.kind=="point"])<2 or len(identity)!=2 or not (identity.x.to_numpy()==identity.y.to_numpy()).all(): raise ValueError("Every panel requires observations and a two-point identity path.")
    return d

def render(source):
    d=load_data(source); fig=Figure(figsize=(7.2,7.57),facecolor="white"); gs=fig.add_gridspec(2,2,left=.12,right=.98,bottom=.11,top=.96,wspace=.06,hspace=.18); panels=["Low exposure, selling","Low exposure, buying","High exposure, selling","High exposure, buying"]
    axes=[]
    for i,panel in enumerate(panels):
        ax=fig.add_subplot(gs[i//2,i%2]); axes.append(ax); style_axis(ax,grid=True); q=d[d.panel==panel]; pts=q[q.kind=="point"]; line=q[q.kind=="identity"].sort_values("x"); ax.scatter(pts.x,pts.y,s=27,color="#314E78",edgecolor="#233B60",alpha=.62,linewidths=.7); ax.plot(line.x,line.y,color="#2473A9",lw=1); ax.set_xlim(-4,80); ax.set_ylim(-4,79); ax.set_xticks([0,25,50,75]); ax.set_yticks([0,25,50,75]); ax.tick_params(labelsize=11,length=4.2); ax.set_title(panel,fontsize=12,pad=8)
        if i%2: ax.tick_params(labelleft=False); ax.spines["left"].set_visible(False)
        if i<2: ax.tick_params(labelbottom=False); ax.spines["bottom"].set_visible(False)
    fig.supxlabel("Trader's value for house",fontsize=16,y=.025); fig.supylabel("Transaction price",fontsize=16,x=.025)
    return fig

def main():
    p=argparse.ArgumentParser(description=__doc__); h=Path(__file__).resolve().parent; p.add_argument("--data",type=Path,default=h/"transaction-price-value-2x2.fixture.csv"); p.add_argument("--output-dir",type=Path,default=h); p.add_argument("--qa-preview",type=Path); a=p.parse_args(); print(save_outputs(render(a.data),a.output_dir,"transaction-price-value-2x2",qa_preview=a.qa_preview))
if __name__=="__main__": main()
