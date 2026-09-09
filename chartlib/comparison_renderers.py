"""Approved comparison, interval, box, and coefficient-plot renderers.

Values are supplied by external inputs; no empirical statistic is calculated.
"""
import numpy as np
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle, Patch
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
from chartlib.asset_runtime import read_frame, require_columns, require_finite

def axis(fig,bounds):
    ax=fig.add_axes(bounds)
    for s in ['top','right']:ax.spines[s].set_visible(False)
    for s in ['left','bottom']:ax.spines[s].set_color('#888');ax.spines[s].set_linewidth(.55)
    ax.tick_params(length=3.5,width=.55,labelsize=7,pad=2)
    return ax

def num(x,pos=None):
    if abs(x)<1e-9:return '0'
    return f'{x:g}'.replace('0.','.').replace('−0.','−.')

def validate(source,cols,keys,interval=False,box=False):
    d=read_frame(source); require_columns(d,cols)
    if d.duplicated(keys).any() or len(d)<6:raise ValueError('Duplicate keys or insufficient information cells.')
    if interval:
        require_finite(d,('estimate','low','high'))
        if not ((d.low<=d.estimate)&(d.estimate<=d.high)).all():raise ValueError('Interval order is invalid.')
    if box:
        require_finite(d,('low','q1','median','q3','high'))
        if not ((d.low<=d.q1)&(d.q1<=d['median'])&(d['median']<=d.q3)&(d.q3<=d.high)).all():raise ValueError('Quartile order is invalid.')
    return d

def tariff(source):
    d=validate(source,('block','panel_order','title','month','estimate','lower','upper','ymin','ymax','step'),['block','panel_order','month'])
    require_finite(d,('month','estimate','lower','upper','ymin','ymax','step'))
    if not ((d.lower<=d.estimate)&(d.estimate<=d.upper)).all():raise ValueError('Invalid interval.')
    if len(d)!=104 or any(sorted(g.month)!=list(range(-6,7)) for _,g in d.groupby(['block','panel_order'])):raise ValueError('Eight complete event panels required.')
    fig=Figure(figsize=(6.1,8.10),facecolor='white')
    for block in [0,1]:
        for p in range(1,5):
            g=d[(d.block==block)&(d.panel_order==p)].sort_values('month');left=(54 if p%2 else 323)/571
            top=[22,198,428,606][block*2+(p-1)//2];height=110
            ax=axis(fig,(left,1-(top+height)/758,204/571,height/758))
            ax.set_axisbelow(True);ax.grid(color='#dddddd',lw=.48,ls=':')
            ax.axvline(0,color='#b7b7b7',ls='--',lw=.65);ax.axhline(0,color='#b7b7b7',ls='--',lw=.65)
            ax.plot(g.month,g.lower,color='#697b9b',ls=(0,(6,3)),lw=.8);ax.plot(g.month,g.upper,color='#697b9b',ls=(0,(6,3)),lw=.8)
            ax.plot(g.month,g.estimate,color='#222',marker='o',mfc='white',mew=.6,ms=2.5,lw=.8)
            ax.set_xlim(-6.2,6.2);ax.set_ylim(g.ymin.iloc[0],g.ymax.iloc[0]);step=g.step.iloc[0]
            ax.set_yticks(np.arange(np.ceil(g.ymin.iloc[0]/step)*step,g.ymax.iloc[0]+.001,step));ax.yaxis.set_major_formatter(FuncFormatter(num))
            ax.set_xticks(range(-6,7),[str(x) if x<6 else '6+' for x in range(-6,7)])
            ax.tick_params(labelsize=5.5,length=3.5,pad=1);ax.set_title(g.title.iloc[0],fontsize=7,pad=4)
            ax.set_xlabel('Months Relative to Tariff Increase',fontsize=6.5,labelpad=2);ax.set_ylabel('Percent',fontsize=6.5,labelpad=3)
    fig.text(.51,1-386/758,'(B)  Retaliatory Tariffs on U.S. Exports',ha='center',va='center',family='serif',fontsize=10)
    return fig

def grouped(source):
    d=validate(source,('order','section','category','series','value'),['order','series']);require_finite(d,('value',))
    if (d.value<0).any() or len(d)!=21:raise ValueError('Seven groups of three nonnegative values required.')
    fig=Figure(figsize=(7.18,3.45),facecolor='white');ax=axis(fig,(45/718,85/345,633/718,252/345))
    for s in ['top','right']:ax.spines[s].set_visible(True)
    colors=['#2d2e35','#a6a7ab','white'];x=np.arange(7)
    for j,s in enumerate('ABC'):
        vals=d[d.series==s].sort_values('order').value
        ax.bar(x+(j-1)*.23,vals,width=.23,color=colors[j],edgecolor='#35383e',lw=.65)
    ax.set_ylim(0,5);ax.set_xlim(-.5,6.5);ax.set_yticks(range(6));ax.tick_params(axis='y',labelsize=8)
    cats=d.sort_values('order').drop_duplicates('order').category
    ax.set_xticks(x,cats,fontsize=7.5);ax.tick_params(axis='x',length=0,pad=7)
    for i in np.arange(-.5,7,1):
        ax.plot([i,i],[0,-.27 if i in [-.5,3.5,6.5] else -.17],transform=ax.get_xaxis_transform(),color='#555',lw=.65,clip_on=False)
    ax.text(1.5,-.215,'random',transform=ax.get_xaxis_transform(),ha='center',va='top',fontsize=8)
    ax.text(5,-.215,'asymmetric',transform=ax.get_xaxis_transform(),ha='center',va='top',fontsize=8)
    ax.set_ylabel('Average Punishment',fontsize=9,fontweight='bold')
    ax.legend([Patch(facecolor=c,edgecolor='#333') for c in colors],list('ABC'),loc='upper right',bbox_to_anchor=(.985,.96),frameon=False,ncol=3,fontsize=9,handlelength=.6,handletextpad=.3,columnspacing=1.3)
    return fig

def compensation(source):
    d=read_frame(source);require_columns(d,('order','label','low','q1','median','q3','high'));require_finite(d,('low','q1','median','q3','high'))
    if len(d)!=5 or not ((d.low<=d.q1)&(d.q1<=d['median'])&(d['median']<=d.q3)&(d.q3<=d.high)).all():raise ValueError('Five valid box summaries required.')
    fig=Figure(figsize=(10.0,4.89),facecolor='white');ax=axis(fig,(.207,.307,.786,.655))
    for r in d.sort_values('order').itertuples():
        y=4-r.order;ax.plot([r.low,r.high],[y,y],color='#4b6283',lw=1.25)
        ax.vlines([r.low,r.high],y-.16,y+.16,color='#4b6283',lw=1.3)
        ax.add_patch(Rectangle((r.q1,y-.24),r.q3-r.q1,.48,facecolor='#8ea5b6',edgecolor='#4b6283',lw=1.25,zorder=3))
        ax.vlines(r.median,y-.24,y+.24,color='#4b6283',lw=1.25,zorder=4)
    ax.set_xlim(-50000,2120000);ax.set_ylim(-.65,4.65)
    ax.set_yticks(range(5),d.sort_values('order',ascending=False).label);ax.tick_params(axis='y',length=0,labelsize=13)
    ax.set_xticks([0,500000,1000000,1500000,2000000],[f'{v:,}' for v in [0,500000,1000000,1500000,2000000]])
    ax.tick_params(axis='x',labelsize=13)
    ax.grid(axis='x',color='#f4f6f7',lw=.6);ax.set_axisbelow(True)
    for value,label in [(275000,'25th%ile'),(490000,'50th%ile'),(770000,'75th%ile')]:
        ax.axvline(value,color='#ee8b70',ls=(0,(5,3)),lw=1.4,zorder=1)
        ax.text(value,-.102,label,transform=ax.get_xaxis_transform(),rotation=-90,ha='center',va='top',fontsize=11,color='#ee8b70')
    ax.set_title('Prior Profession of Investment Manager',loc='left',fontsize=14,pad=0)
    fig.text(.20,.015,'excludes outside values',fontsize=10)
    fig.text(.63,.065,'Compensation of Investment Manager',ha='center',fontsize=13)
    return fig

def frequency(source):
    d=validate(source,('panel','frequency','x','low','q1','median','q3','high'),['panel','frequency','x'],box=True)
    if len(d)!=52:raise ValueError('Two panels, two series, thirteen positions required.')
    fig=Figure(figsize=(8.4,3.16),facecolor='white')
    for i,p in enumerate(['S','j']):
        ax=axis(fig,(.087+i*.469,.113,.388,.797))
        for label,c in [('Mixed Frequency','#f7847e'),('Quarterly Frequency','#bee0e8')]:
            for r in d[(d.panel==p)&(d.frequency==label)].itertuples():
                ax.plot([r.x,r.x],[r.low,r.high],color='#70777a',lw=.55)
                ax.add_patch(Rectangle((r.x-.42,r.q1),.84,r.q3-r.q1,facecolor=c,edgecolor='#6c7375',lw=.9))
                ax.plot([r.x-.42,r.x+.42],[r.median,r.median],color='#54595b',lw=1.0)
        ax.set_xlim(-.6,12.6);ax.set_ylim(.035,.315 if i==0 else .295);ax.set_xticks(range(13),[str(j) for j in range(13)])
        ax.set_yticks([.05,.10,.15,.20,.25,.30] if i==0 else [.05,.10,.15,.20,.25]);ax.tick_params(labelsize=7.2,length=3.5,pad=1)
        ax.set_xlabel(p,fontsize=10,labelpad=1)
        ax.set_ylabel(r'Variance decomposition of $\Delta C_{t+1,t}$',fontsize=10,labelpad=2)
        ax.legend([Patch(facecolor='#f7847e',edgecolor='#6c7375'),Patch(facecolor='#bee0e8',edgecolor='#6c7375')],['Mixed Frequency','Quarterly Frequency'],loc='upper right',bbox_to_anchor=(1,.935),frameon=False,fontsize=10.5,handlelength=1.1,handletextpad=.5,labelspacing=.1,borderpad=.1)
    return fig

def forest(source):
    d=validate(source,('panel','section','label','y','estimate','low','high','color','display'),['y'],interval=True)
    if len(d)!=12:raise ValueError('Twelve outcome rows required.')
    fig=Figure(figsize=(12,8.42),facecolor='white')
    # Separate display columns avoid repurposing the numerical effect scale as padding.
    sections=list(d.section.drop_duplicates());ys=[(.851,.144),(.672,.144),(.493,.144),(.314,.144),(.135,.144)]
    for j,(sec,(bottom,height)) in enumerate(zip(sections,ys)):
        g=d[d.section==sec];ax=axis(fig,(.266,bottom,.484,height));ax.set_xlim(-.9,1.3);ax.set_ylim(-.6,len(g)-.4)
        fig.add_artist(Rectangle((.133,bottom),.133,height,transform=fig.transFigure,facecolor='#d8d8d8',edgecolor='none'))
        ax.set_axisbelow(True);ax.set_xticks([-.5,0,.5,1]);ax.grid(axis='x',color='#e9e9e9',lw=2)
        ax.axvline(0,color='black',ls=(0,(5,4)),lw=1.5)
        for k,r in enumerate(g.itertuples()):
            y=len(g)-1-k;c='#107d68' if r.color=='green' else '#d3d3d3'
            ax.axhline(y,color='#e9e9e9',lw=2,zorder=0);ax.plot([r.low,r.high],[y,y],color=c,lw=3.3);ax.plot(r.estimate,y,'o',ms=11,color=c)
            ax.text(-.89,y,r.display,fontsize=9,ha='left',va='center')
            ax.text(1.025,y,r.label,transform=ax.get_yaxis_transform(),fontsize=11,fontstyle='italic',ha='left',va='center')
        for s in ax.spines.values():s.set_visible(True);s.set_color('#d0d0d0');s.set_linewidth(.9)
        ax.set_yticks([]);ax.tick_params(axis='x',bottom=j==4,labelbottom=j==4,length=5,labelsize=15)
        captions=['A. Social\npreferences','B. Willingness\nto interact','C. National\nidentity','D. Attitudes','E. Well-being']
        fig.text(.201,bottom+height/2,captions[j],ha='center',va='center',fontsize=14)
    fig.add_artist(Rectangle((0,.314),.133,.681,transform=fig.transFigure,color='#d8d8d8',lw=0))
    fig.add_artist(Rectangle((0,.135),.133,.144,transform=fig.transFigure,color='#d8d8d8',lw=0))
    fig.text(.066,.655,'Panel 1:\nSocialization\n(primary)',ha='center',va='center',fontsize=15)
    fig.text(.066,.207,'Panel 2:\nWell-being\n(secondary)',ha='center',va='center',fontsize=15)
    fig.text(.507,.029,'Estimated effect of number of lecture days attended,\nstandard deviations',ha='center',va='center',fontsize=15)
    return fig

def quartile(source):
    d=validate(source,('panel','title','quartile','estimate','low','high','fit'),['panel','quartile'],interval=True)
    if len(d)!=16:raise ValueError('Four complete quartile panels required.')
    fig=Figure(figsize=(8.0,11.10),facecolor='white')
    for p in range(1,5):
        g=d[d.panel==p].sort_values('quartile');left=.054 if p%2 else .579;bottom=.603 if p<3 else .096
        ax=axis(fig,(left,bottom,.405,.386));c='#0000d9' if p%2 else '#008719';ec='#928bd4' if p%2 else '#8dba90'
        ax.set_axisbelow(True);ax.grid(axis='y',color='#e8e8e8',lw=.8);ax.axhline(0,color='#be2626',ls=(0,(6,3)),lw=1.1)
        ax.plot(g.quartile,g['fit'],color='#999',ls=(0,(1.5,2.5)),lw=.8)
        ax.errorbar(g.quartile,g.estimate,yerr=[g.estimate-g.low,g.high-g.estimate],fmt='D' if p%2 else 'o',color=c,ecolor=ec,elinewidth=.9,capsize=0,ms=5)
        ax.set_xlim(.87,4.14);ax.set_ylim(-.212,.412);ax.set_yticks([-.2,0,.2,.4]);ax.yaxis.set_major_formatter(FuncFormatter(num))
        ax.set_xticks(range(1,5),['1\n0-10%','2\n10-20%','3\n20-35%','4\n35-100%'],family='serif',fontsize=9)
        ax.get_xticklabels()[-1].set_ha('right')
        ax.tick_params(axis='y',labelsize=9);ax.set_xlabel('Quartiles Patient Percent Black',family='serif',fontsize=9,labelpad=2)
        fig.text(left+.2025,bottom-.083,f'({"ABCD"[p-1]}) '+g.title.iloc[0],ha='center',va='center',family='serif',fontsize=11)
    return fig

def host(source):
    d=validate(source,('panel','order','label','estimate','low','high','display'),['panel','order'],interval=True)
    if len(d)!=6:raise ValueError('Six estimates required.')
    fig=Figure(figsize=(7.1,5.18),facecolor='white')
    for i,p in enumerate(['Host','Refugee']):
        ax=axis(fig,(.257+i*.363,.14,.342,.765));g=d[d.panel==p].sort_values('order')
        ax.axvline(0,color='#222',lw=.8);ax.errorbar(g.estimate,2-g.order,xerr=[g.estimate-g.low,g.high-g.estimate],fmt='o',ms=4,color='#555',ecolor='#999',elinewidth=.65,capsize=2)
        for r in g.itertuples():ax.text(r.estimate,2-r.order+.09,r.display,ha='center',va='bottom',fontsize=8.5)
        ax.set_xlim(-.54,.54);ax.set_ylim(-1,3);ax.set_yticks([0,1,2],g.label.iloc[::-1] if i==0 else ['','','']);ax.tick_params(axis='y',length=3.5 if i==0 else 0,labelsize=11)
        if i:ax.spines['left'].set_visible(False)
        ax.set_xticks([-.5,0,.5],['-0.50','0.00','0.50']);ax.tick_params(axis='x',labelsize=10)
        ax.add_patch(Rectangle((0,1),1,.05,transform=ax.transAxes,color='#393939',clip_on=False))
        ax.text(.5,1.025,p,transform=ax.transAxes,ha='center',va='center',color='white',fontsize=10)
    fig.text(.61,.048,'Point Estimates with 95% CIs',ha='center',fontsize=12)
    return fig

def drugs(source):
    d=validate(source,('panel','order','label','estimate','low','high'),['panel','order'],interval=True)
    if len(d)!=40:raise ValueError('Two columns with twenty outcomes required.')
    fig=Figure(figsize=(7.6,5.42),facecolor='white')
    for i,p in enumerate(['Characteristics','Coefficients']):
        ax=axis(fig,(.222+i*.39,.066,.362,.88));g=d[d.panel==p].sort_values('order');y=19-g.order
        ax.set_axisbelow(True);ax.set_yticks(y,g.label if i==0 else ['']*20);ax.grid(axis='y',color='#eaf0f1',lw=.6)
        ax.barh(y,g.estimate,height=.46,color='#302cff',edgecolor='#2116bd',lw=.5,zorder=3)
        ax.errorbar(g.estimate,y,xerr=[g.estimate-g.low,g.high-g.estimate],fmt='none',color='#333',elinewidth=.7,capsize=2,zorder=4)
        ax.set_xlim(-.43,.47);ax.set_ylim(-.5,19.5);ax.set_xticks([-.4,-.2,0,.2,.4]);ax.xaxis.set_major_formatter(FuncFormatter(num));ax.tick_params(labelsize=11.5,length=3.5)
        if i:ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0)
        ax.add_patch(Rectangle((0,1),1,.052,transform=ax.transAxes,facecolor='#f0f0f0',edgecolor='#dae7eb',lw=.6,clip_on=False))
        ax.text(.5,1.026,p,transform=ax.transAxes,ha='center',va='center',fontsize=13)
    return fig

def alpha(source):
    d=validate(source,('panel','title','rate','rank','estimate','low','high','status'),['panel','rank'],interval=True)
    if set(d.status)!={'Replicated','Not Replicated','Never Significant'}:raise ValueError('Unknown status.')
    fig=Figure(figsize=(10,5.19),facecolor='white');colors={'Replicated':'#0074a5','Not Replicated':'#da234a','Never Significant':'#00a879'};styles=['solid',(0,(5,3)),(0,(1,2))]
    for p in range(1,5):
        g=d[d.panel==p];ax=axis(fig,(.063 if p%2 else .536,.503 if p<3 else .010,.463,.377))
        ax.axhline(0,color='#111',ls=(0,(5,4)),lw=.9)
        for (status,c),ls in zip(colors.items(),styles):
            h=g[g.status==status]
            for r in h.itertuples():ax.plot([r.rank,r.rank],[r.low,r.high],color=c,lw=.7,ls=ls);ax.plot([r.rank-.25,r.rank+.25],[r.low,r.low],color=c,lw=.55);ax.plot([r.rank-.25,r.rank+.25],[r.high,r.high],color=c,lw=.55)
            ax.plot(h['rank'],h.estimate,ls='none',marker='o',ms=2.2,color=c)
        ax.set_xlim(0,100);ax.set_ylim(-1.12,1.57);ax.set_yticks([-1,-.5,0,.5,1,1.5]);ax.set_xticks([]);ax.tick_params(axis='y',labelsize=8,length=3.5)
        if p%2==0:ax.set_yticklabels([]);ax.tick_params(axis='y',length=0);ax.spines['left'].set_visible(False)
        ax.add_patch(Rectangle((0,1),1,.14,transform=ax.transAxes,facecolor='white',edgecolor='black',lw=.8,clip_on=False))
        ax.text(.5,1.07,g.title.iloc[0],ha='center',va='center',transform=ax.transAxes,fontsize=10)
        ax.text(.06,.91,g.rate.iloc[0],transform=ax.transAxes,fontsize=9)
    fig.text(.01,.5,'Monthly Alpha (%)',rotation=90,va='center',ha='center',fontsize=11)
    fig.legend([Line2D([],[],color=c,ls=ls,lw=1) for (s,c),ls in zip(colors.items(),styles)],list(colors),loc='upper center',bbox_to_anchor=(.55,1.0),ncol=3,frameon=False,fontsize=10,handlelength=1.5,columnspacing=.8)
    return fig

RENDERERS={'tariff-response-2x4-dashed-ci':tariff,'grouped-hbar-3series-3gray':grouped,'investment-manager-compensation-boxplot':compensation,'variance-decomposition-frequency-boxplots-2panel':frequency,'lecture-days-forest-by-domain':forest,'quartile-effect-coefficients-2x2':quartile,'host-refugee-coefficients-2panel':host,'drug-characteristics-coefficients-2panel':drugs,'replication-alpha-coefficients-2x2':alpha}
