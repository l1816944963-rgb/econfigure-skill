"""Render a four-panel raw-scatter and binscatter diagnostic."""
from __future__ import annotations
import argparse,sys
from pathlib import Path
import numpy as np
from matplotlib.figure import Figure
PROJECT_ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PROJECT_ROOT))
from chartlib.asset_runtime import read_frame,require_columns,require_finite,save_outputs,style_axis

def load_data(source):
    d=read_frame(source); require_columns(d,("panel","kind","x","y")); require_finite(d,("x",));
    if set(d.panel)!={"raw","cutoffs","binscatter","conditional"}: raise ValueError("Exactly four declared panels are required.")
    required={"raw":{"point"},"cutoffs":{"point","cut","mean"},"binscatter":{"mean","fit"},"conditional":{"segment"}}
    if any(set(d[d.panel==panel].kind)!=kinds for panel,kinds in required.items()): raise ValueError("Every panel requires its declared visual layers.")
    if d[d.kind!="cut"].y.isna().any(): raise ValueError("Every plotted observation requires a y value.")
    return d

def render(source):
    d=load_data(source); fig=Figure(figsize=(6.57,4.78),facecolor="white"); gs=fig.add_gridspec(2,2,left=.105,right=.98,bottom=.10,top=.94,wspace=.25,hspace=.42); axes=[fig.add_subplot(gs[i,j]) for i in range(2) for j in range(2)]; titles=["Panel A. Raw scatter plot","Panel B. Bin cutoffs and binscatter","Panel C. Binscatter plot","Panel D. Conditional mean point est."]
    for ax,title in zip(axes,titles): style_axis(ax,grid=False); ax.set_xlim(-.73,.02); ax.set_xticks([-.7,-.6,-.3,0]); ax.set_xlabel("log 90th percentile marginal net of tax rate",fontsize=8); ax.set_ylabel("log patents",fontsize=8); ax.tick_params(labelsize=7,length=4.2); ax.set_title(title,fontsize=9,pad=6)
    q=d[d.panel=="raw"]; axes[0].scatter(q.x,q.y,s=4,color="#0B529E",linewidths=0); axes[0].set_ylim(0,10.3); axes[0].set_yticks([0,2,4,6,8,10])
    q=d[d.panel=="cutoffs"]; p=q[q.kind=="point"]; axes[1].scatter(p.x,p.y,s=2,color="#79A9DE",alpha=.75,linewidths=0); [axes[1].axvline(v,color="#7A7A7A",lw=.55,ls=(0,(3,3))) for v in q[q.kind=="cut"].x]; m=q[q.kind=="mean"]; axes[1].scatter(m.x,m.y,s=15,color="#303030"); axes[1].set_ylim(3.8,8.2); axes[1].set_yticks([4,6,8])
    q=d[d.panel=="binscatter"]; m=q[q.kind=="mean"]; f=q[q.kind=="fit"]; axes[2].scatter(m.x,m.y,s=16,color="#404040",label="Binscatter"); axes[2].plot(f.x,f.y,color="#2D8438",lw=1.2,label="Linear fit"); axes[2].set_ylim(3.8,8.2); axes[2].set_yticks([4,6,8]); axes[2].legend(loc="upper right",frameon=True,fancybox=False,fontsize=7,handlelength=1.5,labelspacing=.25,borderpad=.35)
    q=d[d.panel=="conditional"].sort_values("x"); step=(q.x.max()-q.x.min())/(len(q)-1); [axes[3].plot([r.x-step*.38,r.x+step*.38],[r.y,r.y],color="#303030",lw=1.0) for r in q.itertuples()]; axes[3].plot([-.68,-.02],[6.5,5.5],color="#2D8438",lw=1.2); axes[3].set_ylim(3.8,8.2); axes[3].set_yticks([4,6,8])
    return fig

def main():
    p=argparse.ArgumentParser(description=__doc__); h=Path(__file__).resolve().parent; p.add_argument("--data",type=Path,default=h/"binscatter-diagnostic-2x2.fixture.csv"); p.add_argument("--output-dir",type=Path,default=h); p.add_argument("--qa-preview",type=Path); a=p.parse_args(); print(save_outputs(render(a.data),a.output_dir,"binscatter-diagnostic-2x2",qa_preview=a.qa_preview))
if __name__=="__main__": main()
