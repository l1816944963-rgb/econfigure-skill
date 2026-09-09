"""Render two labeled occupation exposure scatter panels."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
from matplotlib.figure import Figure
PROJECT_ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(PROJECT_ROOT))
from chartlib.asset_runtime import read_frame,require_columns,require_finite,save_outputs,style_axis

STEM="automation-exposure-occupations-2panel"
def load_data(source):
    d=read_frame(source); require_columns(d,("panel","kind","label","automation_exposure","routine_exposure")); require_finite(d,("automation_exposure","routine_exposure"))
    if d.panel.nunique()!=2 or set(d.kind)!={"background","labeled","fit"}: raise ValueError("Exactly two panels with background points, labeled points, and fits are required.")
    if d[d.kind=="labeled"].duplicated(["panel","label"]).any(): raise ValueError("Labeled occupations must be unique within panel.")
    for _,q in d.groupby("panel"):
        if len(q[q.kind=="background"])<100 or len(q[q.kind=="fit"])!=2: raise ValueError("Each panel requires at least 100 background points and two fit endpoints.")
    if not d.automation_exposure.between(0,100).all() or not d.routine_exposure.between(0,100).all(): raise ValueError("Exposure values must lie from zero to 100.")
    return d
def render(source):
    d=load_data(source); fig=Figure(figsize=(6.16,7.12),facecolor="white")
    for i,(panel,q) in enumerate(d.groupby("panel",sort=False)):
        ax=fig.add_axes((.13,.57-i*.47,.82,.35)); style_axis(ax,grid=False,full_spines=False); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        bg=q[q.kind=="background"]; labeled=q[q.kind=="labeled"]; fit=q[q.kind=="fit"].sort_values("automation_exposure")
        ax.scatter(bg.automation_exposure,bg.routine_exposure,s=14,facecolor="#f3f7fa",edgecolor="#dbe3e8",linewidth=.55,zorder=1)
        ax.plot(fit.automation_exposure,fit.routine_exposure,color="#9aa3aa",lw=1.05,ls=(0,(5,4)),zorder=2)
        ax.scatter(labeled.automation_exposure,labeled.routine_exposure,s=15,facecolor="#e6a0a0",edgecolor="#9f4b4b",linewidth=.65,zorder=3)
        for j,r in labeled.reset_index(drop=True).iterrows():
            right=r.automation_exposure>84
            ax.annotate(r.label,(r.automation_exposure,r.routine_exposure),xytext=(-2 if right else 2,2 if j%2 else -5),textcoords="offset points",ha="right" if right else "left",fontsize=5.1,color="#a95858",alpha=.86)
        ax.set_xlim(0,102); ax.set_ylim(0,103); ax.set_xticks(range(0,101,20)); ax.set_yticks(range(0,101,20)); ax.tick_params(labelsize=7,length=3.5); ax.set_xlabel("Automation Patents Exposure (percentiles)",fontsize=8); ax.set_ylabel("Automation Patents Exposure (percentiles)",fontsize=8); ax.set_title(panel,fontsize=8,fontstyle="italic",pad=10)
    return fig
def main():
    p=argparse.ArgumentParser(description=__doc__); h=Path(__file__).resolve().parent; p.add_argument("--data",type=Path,default=h/f"{STEM}.fixture.csv"); p.add_argument("--output-dir",type=Path,default=h); p.add_argument("--qa-preview",type=Path); a=p.parse_args(); print(save_outputs(render(a.data),a.output_dir,STEM,qa_preview=a.qa_preview))
if __name__=="__main__": main()
