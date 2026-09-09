"""Render two panels of group estimates with supplied linear, quadratic, and local fits."""
from __future__ import annotations
import argparse,sys
from pathlib import Path
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
PROJECT_ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PROJECT_ROOT))
from chartlib.asset_runtime import read_frame,require_columns,require_finite,save_outputs,style_axis

def load_data(source):
    d=read_frame(source); require_columns(d,("panel","group","kind","x","y")); require_finite(d,("x","y"));
    if set(d.panel)!={"All Hotline Calls","Screened-in Calls"} or set(d.group)!={"White","Black"} or set(d.kind)!={"estimate","linear","quadratic","local"}: raise ValueError("Two panels, two groups, estimates, and three supplied fits are required.")
    for _,q in d.groupby(["panel","group"]):
        if set(q.kind)!={"estimate","linear","quadratic","local"} or len(q[q.kind=="estimate"])<2 or any(len(q[q.kind==kind])<2 for kind in ("linear","quadratic","local")): raise ValueError("Every panel-group key requires estimates and all three complete fit paths.")
    return d

def render(source):
    d=load_data(source); fig=Figure(figsize=(7,10.6),facecolor="white"); gs=fig.add_gridspec(2,1,left=.075,right=.73,bottom=.12,top=.97,hspace=.37); axes=[fig.add_subplot(gs[i,0]) for i in range(2)]; colors={"White":"#137CA8","Black":"#E99A3C"}; markers={"White":"o","Black":"x"}; styles={"linear":"-","quadratic":(0,(5,3)),"local":(0,(2,2))}
    for ax,panel in zip(axes,("All Hotline Calls","Screened-in Calls")):
        style_axis(ax,grid=True); q=d[d.panel==panel]
        for group in ("White","Black"):
            p=q[(q.group==group)&(q.kind=="estimate")]
            if group=="White": ax.scatter(p.x,p.y,s=24,marker="o",facecolors="none",edgecolors=colors[group],linewidths=1.4)
            else: ax.scatter(p.x,p.y,s=24,marker="x",color=colors[group],linewidths=1.4)
            for kind in ("linear","quadratic","local"):
                f=q[(q.group==group)&(q.kind==kind)].sort_values("x"); ax.plot(f.x,f.y,color=colors[group],lw=1.5,ls=styles[kind])
        xmax=.1 if panel.startswith("All") else .15; ax.set_xlim(0,xmax); ax.set_ylim(.045,.205); ax.set_xticks([0,xmax/2,xmax],["0",f"{xmax/2:.2f}".lstrip("0").rstrip("0"),f"{xmax:.2f}".lstrip("0")]); ax.set_yticks([.05,.1,.15,.2],[".05",".1",".15",".2"]); ax.set_xlabel("Placement Rate",fontsize=11); ax.set_ylabel("Subsequent Maltreatment, When Left at Home",fontsize=10.5); ax.tick_params(labelsize=9,length=4.2); ax.set_title(f"Panel {'A' if panel.startswith('All') else 'B'}: {panel}",y=-.24,fontsize=14,fontfamily="serif")
        handles=[Line2D([],[],marker="o",mfc="none",mec=colors["White"],ls="none",label="White Estimate"),Line2D([],[],marker="x",color=colors["Black"],ls="none",label="Black Estimate")]
        for kind,label in (("linear","Linear Fit"),("quadratic","Quadratic Fit"),("local","Local Linear Fit")):
            handles.extend([Line2D([],[],color=colors[g],lw=1.5,ls=styles[kind],label=f"{g} {label}") for g in ("White","Black")])
        ax.legend(handles=handles,loc="center left",bbox_to_anchor=(1.03,.38),frameon=False,fontsize=9,handlelength=1.7,handletextpad=.25,labelspacing=.35)
    return fig

def main():
    p=argparse.ArgumentParser(description=__doc__); h=Path(__file__).resolve().parent; p.add_argument("--data",type=Path,default=h/"placement-rate-maltreatment-fits-2panel.fixture.csv"); p.add_argument("--output-dir",type=Path,default=h); p.add_argument("--qa-preview",type=Path); a=p.parse_args(); print(save_outputs(render(a.data),a.output_dir,"placement-rate-maltreatment-fits-2panel",qa_preview=a.qa_preview))
if __name__=="__main__": main()
