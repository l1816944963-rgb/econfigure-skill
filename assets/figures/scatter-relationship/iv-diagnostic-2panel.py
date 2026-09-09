"""Render paired instrumental-variable diagnostic profiles."""
from __future__ import annotations
import argparse,sys
from pathlib import Path
from matplotlib.figure import Figure
PROJECT_ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PROJECT_ROOT))
from chartlib.asset_runtime import read_frame,require_columns,require_finite,save_outputs,style_axis

def load_data(source):
    d=read_frame(source); require_columns(d,("panel","series","x","y")); require_finite(d,("x","y"));
    if set(d.panel)!={"Rejection rate","Mean goodness of fit"} or set(d.series)!={"naive IV","preferred IV"}: raise ValueError("Two diagnostic panels and two complete series are required.")
    if d.duplicated(["panel","series","x"]).any(): raise ValueError("Panel-series-x keys must be unique.")
    for _,q in d.groupby("panel"):
        keys=[set(q[q.series==series].x) for series in ("naive IV","preferred IV")]
        if not keys[0] or keys[0]!=keys[1]: raise ValueError("Both procedures require identical complete x keys within each panel.")
    return d

def render(source):
    d=load_data(source); fig=Figure(figsize=(8.3,4.43),facecolor="white"); gs=fig.add_gridspec(1,2,left=.055,right=.965,bottom=.14,top=.90,wspace=.25); axes=[fig.add_subplot(gs[0,i]) for i in range(2)]
    for i,(ax,panel) in enumerate(zip(axes,("Rejection rate","Mean goodness of fit"))):
        style_axis(ax,grid=False,full_spines=True)
        for series,color,marker in (("naive IV","#939393","D"),("preferred IV","#242424","o")):
            q=d[(d.panel==panel)&(d.series==series)].sort_values("x"); ax.plot(q.x,q.y,color=color,lw=.8,marker=marker,ms=5.5,label=series)
        ax.axvline(0,color="#777",lw=.75)
        ax.set_xlim(-.06,.06); ax.set_xticks([-.06,-.04,-.02,0,.02,.04,.06]); ax.set_xlabel("Eₜ[W (Δ x*) - W (Δ x)]",fontsize=11); ax.tick_params(direction="in",top=True,right=True,labelsize=9,length=4.2)
        if i==0: ax.set_ylim(0,1); ax.set_yticks([0,.2,.4,.6,.8,1]); ax.set_title("(A) Rejection rate",fontsize=14,pad=12)
        else: ax.axhline(0,color="#777",lw=.75); ax.set_ylim(-.06,.06); ax.set_yticks([-.06,-.04,-.02,0,.02,.04,.06]); ax.set_title("(B) Mean of goodness-of-fit measure",fontsize=14,pad=12)
        ax.legend(loc="upper center",frameon=True,fancybox=False,edgecolor="#333",fontsize=9,handlelength=1.5,handletextpad=.25,labelspacing=.1,borderpad=.25)
    return fig

def main():
    p=argparse.ArgumentParser(description=__doc__); h=Path(__file__).resolve().parent; p.add_argument("--data",type=Path,default=h/"iv-diagnostic-2panel.fixture.csv"); p.add_argument("--output-dir",type=Path,default=h); p.add_argument("--qa-preview",type=Path); a=p.parse_args(); print(save_outputs(render(a.data),a.output_dir,"iv-diagnostic-2panel",qa_preview=a.qa_preview))
if __name__=="__main__": main()
