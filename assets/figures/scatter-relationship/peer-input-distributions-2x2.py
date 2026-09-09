"""Render two input histograms and two peer-comparison scatter panels."""
from __future__ import annotations
import argparse,sys
from pathlib import Path
import numpy as np
from matplotlib.figure import Figure
from matplotlib.patches import Patch
PROJECT_ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PROJECT_ROOT))
from chartlib.asset_runtime import read_frame,require_columns,require_finite,save_outputs,style_axis

def load_data(source):
    d=read_frame(source); require_columns(d,("panel","kind","series","x","y")); require_finite(d,("x","y"));
    if set(d.panel)!={"price-hist","size-hist","rank","share"} or (d.y<0).any(): raise ValueError("Four non-negative input panels are required.")
    if set(d[d.panel=="price-hist"].series)!={"Private feeder","Other"} or set(d[d.panel=="size-hist"].kind)!={"bar"}: raise ValueError("Histogram panel series are incomplete.")
    for panel in ("rank","share"):
        q=d[d.panel==panel]
        if set(q.kind)!={"mean","range"} or set(q[q.kind=="mean"].x)!=set(q[q.kind=="range"].x): raise ValueError("Each peer panel requires paired mean and range observations.")
    return d

def render(source):
    d=load_data(source); fig=Figure(figsize=(7.6,10),facecolor="white"); gs=fig.add_gridspec(2,2,left=.06,right=.98,bottom=.10,top=.965,wspace=.20,hspace=.27); axes=[fig.add_subplot(gs[i,j]) for i in range(2) for j in range(2)]
    titles=["(A) Price per student by high school","(B) Residential peer group size","(C) Peer neighborhood rank","(D) Peer private feeder share"]
    for ax,title in zip(axes,titles): style_axis(ax,grid=False,full_spines=True); ax.set_title(title,fontsize=13,pad=6); ax.tick_params(labelsize=9,length=4.2)
    q=d[d.panel=="price-hist"]; colors={"Private feeder":"#5E57EB","Other":"#F4B0B0"};
    for s in ("Other","Private feeder"):
        p=q[q.series==s]; axes[0].bar(p.x,p.y,width=p.width,color=colors[s],edgecolor=colors[s],alpha=.58,label=s)
    axes[0].set_xlim(-15,620); axes[0].set_xticks([0,200,400,600]); axes[0].set_ylim(0,.305); axes[0].set_yticks([0,.1,.2,.3],["0",".1",".2",".3"]); axes[0].set_xlabel("Price per occupant",fontsize=11); axes[0].set_ylabel("Share",fontsize=11); handles=[Patch(facecolor=colors[s],edgecolor=colors[s],alpha=.7,label=s) for s in ("Private feeder","Other")]; axes[0].legend(handles=handles,loc="upper left",bbox_to_anchor=(0,-.09,1,0),mode="expand",ncols=2,frameon=True,fancybox=False,fontsize=10,borderpad=.35)
    q=d[d.panel=="size-hist"]; axes[1].bar(q.x,q.y,width=q.width,color="#BD78B7",edgecolor="#934C90",alpha=.72); axes[1].set_xlim(-1,40); axes[1].set_ylim(0,.16); axes[1].set_yticks([0,.05,.1,.15],["0",".05",".1",".15"]); axes[1].set_xlabel("Peer group size",fontsize=11); axes[1].set_ylabel("Share",fontsize=11)
    for ax,panel in zip(axes[2:],("rank","share")):
        q=d[d.panel==panel]; m=q[q.kind=="mean"]; r=q[q.kind=="range"]; ax.scatter(m.x,m.y,s=26,facecolors="none",edgecolors="#176E27",linewidths=1.1,label="Mean peer price" if panel=="rank" else "Peer pf mean"); ax.scatter(r.x,r.y,s=25,marker="+",color="#555",linewidths=1.0,label="Peer price p90/p10" if panel=="rank" else "Peer pf p90/p10"); ax.set_xlim(-.02,1.02); ax.set_ylim(-.02,1.02); ax.set_xticks(np.arange(0,1.01,.2),["0",".2",".4",".6",".8","1"]); ax.set_yticks(np.arange(0,1.01,.2),["0",".2",".4",".6",".8","1"]); ax.set_xlabel("Own room price rank",fontsize=11); ax.legend(loc="upper left",bbox_to_anchor=(0,-.08,1,0),mode="expand",ncols=2,frameon=True,fancybox=False,fontsize=9,borderpad=.35,handletextpad=.3,columnspacing=.5)
    return fig

def main():
    p=argparse.ArgumentParser(description=__doc__); h=Path(__file__).resolve().parent; p.add_argument("--data",type=Path,default=h/"peer-input-distributions-2x2.fixture.csv"); p.add_argument("--output-dir",type=Path,default=h); p.add_argument("--qa-preview",type=Path); a=p.parse_args(); print(save_outputs(render(a.data),a.output_dir,"peer-input-distributions-2x2",qa_preview=a.qa_preview))
if __name__=="__main__": main()
