"""Render two labeled binscatter series with separate fitted lines."""
from __future__ import annotations
import argparse,sys
from pathlib import Path
from matplotlib.figure import Figure
PROJECT_ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PROJECT_ROOT))
from chartlib.asset_runtime import read_frame,require_columns,require_finite,save_outputs,style_axis

def load_data(source):
    d=read_frame(source); require_columns(d,("series","kind","x","y")); require_finite(d,("x","y"));
    if set(d.series)!={"Exposed Households","Unexposed Households"} or set(d.kind)!={"point","fit"}: raise ValueError("Two series with supplied points and fits are required.")
    for _,q in d.groupby("series"):
        if len(q[q.kind=="point"])!=48 or len(q[q.kind=="fit"])!=2: raise ValueError("Each series requires exactly 48 bin means and a two-point supplied fit path.")
    return d

def render(source):
    d=load_data(source); fig=Figure(figsize=(8,5.22),facecolor="white"); ax=fig.add_axes((.085,.17,.88,.79)); style_axis(ax,grid=True,full_spines=False); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    for series,marker,edge,face,z in (("Unexposed Households","o","#909090","none",3),("Exposed Households","D","#111111","#111111",4)):
        p=d[(d.series==series)&(d.kind=="point")]; f=d[(d.series==series)&(d.kind=="fit")].sort_values("x"); ax.scatter(p.x,p.y,s=34,marker=marker,facecolors=face,edgecolors=edge,linewidths=1.5,zorder=z); ax.plot(f.x,f.y,color=edge,lw=1.5,zorder=2)
    ax.set_xlim(-.205,.012); ax.set_ylim(.375,.605); ax.set_xticks([-.2,-.15,-.1,-.05,0],["-.2","-.15","-.1","-.05","0"]); ax.set_yticks([.4,.45,.5,.55,.6],[".4",".45",".5",".55",".6"]); ax.set_xlabel("U.S. Employment Shock",fontsize=15); ax.set_ylabel("Employed Share of Working-Age Population",fontsize=14); ax.tick_params(labelsize=11,length=4.2)
    text_box={"facecolor":"white","edgecolor":"none","boxstyle":"square,pad=0.15"}; ax.text(-.06,.54,"Unexposed Households",fontsize=13,ha="center",va="center",bbox=text_box,zorder=6); ax.text(-.055,.425,"Exposed Households",fontsize=13,ha="center",va="center",bbox=text_box,zorder=6); fig.text(.085,.015,"Points are binscatter means in 48 quantile bins.",fontsize=9)
    return fig

def main():
    p=argparse.ArgumentParser(description=__doc__); h=Path(__file__).resolve().parent; p.add_argument("--data",type=Path,default=h/"employment-shock-binscatter.fixture.csv"); p.add_argument("--output-dir",type=Path,default=h); p.add_argument("--qa-preview",type=Path); a=p.parse_args(); print(save_outputs(render(a.data),a.output_dir,"employment-shock-binscatter",qa_preview=a.qa_preview))
if __name__=="__main__": main()
