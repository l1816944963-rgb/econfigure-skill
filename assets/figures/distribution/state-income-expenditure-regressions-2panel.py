"""Render two state-level income and expenditure regressions with direct labels."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
from matplotlib.figure import Figure
PROJECT_ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PROJECT_ROOT))
from chartlib.asset_runtime import read_frame,require_columns,require_finite,save_outputs,style_axis
STEM="state-income-expenditure-regressions-2panel"
def load_data(source):
    d=read_frame(source); require_columns(d,("panel","state","income","expenditure","kind")); require_finite(d,("income","expenditure"))
    if d.panel.nunique()!=2 or set(d.kind)!={"point","fit"}: raise ValueError("Two panels with point and supplied fit rows are required.")
    for _,q in d.groupby("panel"):
        if len(q[q.kind=="fit"])!=2 or len(q[q.kind=="point"])<30: raise ValueError("Each panel requires at least 30 states and a two-point fit path.")
    return d
def render(source):
    d=load_data(source); fig=Figure(figsize=(5.07,7.11),facecolor="white")
    for i,(panel,q) in enumerate(d.groupby("panel",sort=False)):
        ax=fig.add_axes((.16,.58-i*.47,.76,.31)); style_axis(ax,grid=True,full_spines=True); p=q[q.kind=="point"]; f=q[q.kind=="fit"].sort_values("income")
        ax.scatter(p.income,p.expenditure,s=10,color="#286899",zorder=3); ax.plot(f.income,f.expenditure,color="#b64d52",lw=1.2)
        for r in p.itertuples(): ax.annotate(r.state,(r.income,r.expenditure),xytext=(2,1),textcoords="offset points",fontsize=4.7,color="#22587f")
        ax.set_xlim(33000,57000); ax.set_xticks([35000,40000,45000,50000,55000]); ax.set_title(panel,fontsize=8,fontweight="bold",pad=24); ax.text(.5,1.08,"State Fixed Effect estimate with adjusted R-squared",transform=ax.transAxes,ha="center",fontsize=6.2,color="#35617c"); ax.set_xlabel("Mean State Income For Whites",fontsize=7); ax.set_ylabel("Mean State Expenditures",fontsize=7); ax.tick_params(labelsize=6,length=3.5); ax.grid(color="#e6edf1",lw=.55)
    return fig
def main():
    p=argparse.ArgumentParser(description=__doc__); h=Path(__file__).resolve().parent; p.add_argument("--data",type=Path,default=h/f"{STEM}.fixture.csv"); p.add_argument("--output-dir",type=Path,default=h); p.add_argument("--qa-preview",type=Path); a=p.parse_args(); print(save_outputs(render(a.data),a.output_dir,STEM,qa_preview=a.qa_preview))
if __name__=="__main__": main()
