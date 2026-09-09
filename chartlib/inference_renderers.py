"""Approved estimate, event-study, interval, and heatmap renderers."""
from chartlib.asset_runtime import read_frame, require_columns, require_finite
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
import numpy as np

def frame(source,columns,keys,rows):
    d=read_frame(source);require_columns(d,columns)
    if len(d)!=rows or d.duplicated(keys).any():raise ValueError('Unexpected record count or duplicate plotting keys.')
    nums=[c for c in ['x','order','panel','estimate','low','high','outer_low','outer_high','control','treated','row','column','red','green','blue'] if c in d]
    require_finite(d,tuple(nums))
    if 'low' in d and not ((d.low<=d.estimate)&(d.estimate<=d.high)).all():raise ValueError('Invalid interval ordering.')
    if 'outer_low' in d and not ((d.outer_low<=d.low)&(d.high<=d.outer_high)).all():raise ValueError('Invalid nested boundary ordering.')
    return d.sort_values(keys).reset_index(drop=True)
def axis(fig,b):
    a=fig.add_axes(b)
    for s in ['right','top']:a.spines[s].set_visible(False)
    for s in ['bottom','left']:a.spines[s].set_color('#888');a.spines[s].set_linewidth(.7)
    a.tick_params(length=3.5,width=.7,labelsize=10,pad=3);a.set_axisbelow(True)
    return a
def fmt(x,pos=None):return '0' if abs(x)<1e-9 else f'{x:g}'.replace('-0.','-.').replace('0.','.')
def interval(a,g,color='black',marker='o',offset=0,ms=4,caps=0):
    a.errorbar(g.x+offset,g.estimate,yerr=[g.estimate-g.low,g.high-g.estimate],fmt=marker,color=color,ecolor=color,elinewidth=.9,capsize=caps,ms=ms,mfc='white' if marker in ['D','o'] else color,mew=.9,zorder=3)

def values(source):
    d=frame(source,('order','label','series','estimate','low','high'),['series','order'],22)
    fig=Figure(figsize=(10,7.7),facecolor='white');a=axis(fig,(.267,.260,.692,.714))
    a.set_xlim(-.121,.105);a.set_ylim(-.5,10.5);a.axvline(0,color='#b42e3b',lw=2.8,zorder=1)
    for y in np.arange(.5,10,.999999):a.axhline(y,color='#c8c9ca',ls=(0,(5,3)),lw=1.8,zorder=0)
    handles=[]
    for s,dy,edge,fill,line in [('Financial',.15,'#274f73','#3d5098','#7e95aa'),('Promotion',-.15,'#8b3b40','white','#b58a8d')]:
        g=d[d.series==s].sort_values('order');y=10-g.order+dy
        a.hlines(y,g.low,g.high,color=line,lw=3.4,zorder=2)
        a.plot(g.estimate,y,'D',mfc=fill,mec=edge,mew=2.8,ms=8,zorder=3)
        handles.append(Line2D([],[],ls='none',marker='D',mfc=fill,mec=edge,mew=2.8,ms=11,label=s))
    a.set_yticks(range(11),d[d.series=='Financial'].sort_values('order',ascending=False).label,fontsize=22);a.tick_params(axis='y',length=0,pad=7)
    a.set_xticks([-.1,-.05,0,.05,.1]);a.xaxis.set_major_formatter(FuncFormatter(lambda x,p:'0' if x==0 else f'{x:g}'));a.tick_params(axis='x',labelsize=22,length=7)
    for s in ['left','bottom']:a.spines[s].set_color('#222');a.spines[s].set_linewidth(1.9)
    leg=fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.596,.047),ncol=2,fontsize=20,frameon=True,fancybox=False,edgecolor='#222',framealpha=1,borderpad=.95,handletextpad=.6,columnspacing=1.6)
    leg.get_frame().set_linewidth(2)
    return fig

def mental(source):
    d=frame(source,('order','label','duration','estimate','low','high'),['order'],5)
    fig=Figure(figsize=(7.4,5.02),facecolor='white');a=axis(fig,(.114,.125,.837,.825));a.axhline(0,color='#555',ls=(0,(3,3)),lw=.8)
    a.errorbar(d.order,d.estimate,yerr=[d.estimate-d.low,d.high-d.estimate],fmt='D',color='#333',ecolor='#666',ms=4,capsize=4,elinewidth=.8)
    for r in d.itertuples():a.text(r.order+.095,r.estimate,f'{r.estimate:.2f}',fontsize=10,ha='left',va='center')
    a.set_xlim(-.6,4.6);a.set_ylim(-1,6);a.set_yticks(range(-1,7));a.yaxis.set_major_formatter(FuncFormatter(lambda x,p:f'{x:.2f}'))
    a.set_xticks(d.order,d.label,fontsize=10.5);a.tick_params(axis='x',length=0,pad=3);a.tick_params(axis='y',length=0,labelsize=10.5)
    for r in d.itertuples():a.text(r.order,-.105,r.duration,transform=a.get_xaxis_transform(),ha='center',va='top',fontsize=10.5)
    a.set_ylabel('Effect of $100K on Mental Health (SD Units)',fontsize=12,labelpad=1)
    return fig

def treatments(source):
    d=frame(source,('panel','order','label','series','estimate','low','high','display'),['panel','order','series'],36)
    fig=Figure(figsize=(10,6.38),facecolor='white')
    for p,title in enumerate(['Cash only','Therapy only','Both'],1):
        a=axis(fig,(.202+(p-1)*.25,.198,.232,.745));a.set_xlim(-.43,.64);a.set_ylim(-.73,5.65)
        a.set_xticks([-.2,0,.2,.4,.6]);a.xaxis.set_major_formatter(FuncFormatter(fmt));a.tick_params(axis='x',labelsize=13)
        a.axvline(0,color='#555',ls=(0,(8,4)),lw=.8);a.grid(axis='x',color='#eee',lw=.6)
        for j,(s,c,m) in enumerate([('2–5 weeks','#2dc341','s'),('12–13 weeks','#264bb6','s')]):
            g=d[(d.panel==p)&(d.series==s)].sort_values('order');y=5-g.order+(.15 if j==0 else -.15)
            a.hlines(y,g.low,g.high,color=c,lw=1.1 if j==0 else 2.1)
            a.plot(g.estimate,y,ls='none',marker=m,color=c,ms=3.5)
            for r in g.itertuples():
                label=r.display.replace('p ',r'$p$ ')
                a.text(.17,5-r.order+(.39 if j==0 else -.34),label,ha='center',va='center',fontsize=10.5,color='#081630',family='serif')
        g=d[(d.panel==p)&(d.series=='2–5 weeks')].sort_values('order');a.set_yticks(5-g.order,g.label if p==1 else ['']*6)
        a.tick_params(axis='y',length=0,labelsize=15);a.set_xlabel(title,fontsize=14,labelpad=2)
        if p>1:a.spines['left'].set_visible(False)
    handles=[Line2D([],[],color=c,marker=m,ls='none',ms=5,label=s) for s,c,m in [('2–5 weeks','#2dc341','o'),('12–13 weeks','#264bb6','s')]]
    fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.56,.035),ncol=2,frameon=True,fancybox=False,edgecolor='#555',fontsize=13,borderpad=.35,columnspacing=1,handletextpad=.25,handlelength=.7)
    fig.text(.56,.010,'Impact by treatment arm, standard deviations',ha='center',fontsize=16)
    return fig

def expansion(source):
    d=frame(source,('panel','x','estimate','low','high'),['panel','x'],18)
    fig=Figure(figsize=(7.4,10.99),facecolor='white')
    for p in [1,2]:
        bottom=.615 if p==1 else .107;a=axis(fig,(.091,bottom,.900,.375));g=d[d.panel==p]
        a.errorbar(g.x,g.estimate,yerr=[g.estimate-g.low,g.high-g.estimate],fmt='o',ms=4.5,color='black',elinewidth=1.2,capsize=0)
        a.set_xlim(-5.5,3.5);a.set_ylim(-2.4,8.65 if p==1 else 9.1);a.set_xticks(range(-5,4));a.set_yticks([-2,0,2,4,6,8]);a.tick_params(labelsize=12)
        a.grid(axis='y',color='#c3c3c3',ls=(0,(1,3)),lw=.9);a.axhline(0,color='#777',ls=(0,(3,3)),lw=1);a.axvline(-.5,color='#777',ls=(0,(3,3)),lw=1)
        a.set_ylabel('Coefficient Estimate',family='serif',fontsize=14,labelpad=7);a.set_xlabel('Year Relative to Expansion',family='serif',fontsize=14,labelpad=6)
        fig.text(.53,.522 if p==1 else .012,['(a) Actual Eligibility','(b) Simulated Eligibility'][p-1],ha='center',family='serif',fontsize=18)
    return fig

def delay(source):
    d=frame(source,('panel','x','estimate','low','high'),['panel','x'],24);fig=Figure(figsize=(8,10.92),facecolor='white')
    dates=['Nov-Jan 2011','Feb-Apr 2011','May-Jul 2011','Aug-Oct 2011','Nov-Jan 2012','Feb-Apr 2012','May-Jul 2012','Aug-Oct 2012','Nov-Jan 2013','Feb-Apr 2013','May-Jul 2013','Aug-Oct 2013']
    for p in [1,2]:
        a=axis(fig,(.124,.617 if p==1 else .13,.863,.335 if p==1 else .319));g=d[d.panel==p]
        for left,right,c in [(-.75,1.05,'#efefef'),(3.25,5.05,'#eeeeee'),(7.3,9.1,'#d3d4d5')]:a.axvspan(left,right,color=c,zorder=0)
        a.set_xlim(-1.35,11.6);a.set_ylim((-.235,.265) if p==1 else (-.082,.05));a.grid(color='#e4e4e4',lw=.55,alpha=.5)
        a.axhline(0,color='#555',lw=.9);a.errorbar(g.x,g.estimate,yerr=[g.estimate-g.low,g.high-g.estimate],fmt='o',color='#222',ms=3,elinewidth=.75,capsize=0);a.plot(g.x,g.estimate,color='#555',lw=.7,ls=(0,(1,2)))
        a.set_yticks([-.2,-.1,0,.1,.2] if p==1 else [-.075,-.05,-.025,0,.025,.05]);a.yaxis.set_major_formatter(FuncFormatter(lambda x,q,panel=p:f'{x:.1f}' if panel==1 else f'{x:.3f}'))
        a.set_xticks(range(12),dates,rotation=45,ha='right',family='serif',fontsize=11);a.tick_params(axis='y',labelsize=10.5)
        a.set_ylabel('Coefficient / 95% CI',family='serif',fontsize=15,labelpad=9)
        a.legend([Line2D([],[],marker='o',ls=(0,(1,2)),color='#222',ms=3)],['Effect of Delay state\non Growth rate '+('handgun sale bg checks per 100,000 pop' if p==1 else 'handgun homicides per 100,000 pop')],loc='lower left',bbox_to_anchor=(0,1.018),frameon=False,fontsize=11,handlelength=1,handletextpad=.4,borderpad=0)
        fig.text(.53,.510 if p==1 else .007,['(A)  NICS BGCs','(B)  Handgun homicide rate'][p-1],ha='center',family='serif',fontsize=14)
    return fig

def mortality(source):
    d=frame(source,('panel','x','estimate','low','high','outer_low','outer_high'),['panel','x'],126)
    fig=Figure(figsize=(9.5,11.99),facecolor='white')
    titles=['All deaths','Overdose','Natural causes','Murder','Accidents','Suicide'];limits=[(-650,225),(-210,110),(-210,250),(-310,110),(-63,48),(-104,54)];ticks=[[-600,-400,-200,0,200],[-200,-100,0,100],[-200,-100,0,100,200],[-300,-200,-100,0,100],[-60,-40,-20,0,20,40],[-100,-50,0,50]]
    for p in range(1,7):
        col=(p-1)%2;row=(p-1)//2;a=axis(fig,(.054+col*.509,.714-row*.333,.439,.242));g=d[d.panel==p]
        a.set_xlim(-5.2,5.2);a.set_ylim(*limits[p-1]);a.set_xticks(range(-5,6));a.set_yticks(ticks[p-1]);a.tick_params(labelsize=9)
        a.grid(axis='y',color='#eee',lw=.7);a.axvline(0,color='#888',lw=.8)
        for field in ['outer_low','outer_high']:a.plot(g.x,g[field],color='#999',lw=.45,ls=(0,(4,3)))
        for field in ['low','high']:a.plot(g.x,g[field],color='#777',lw=.7,ls=(0,(3,2)))
        a.plot(g.x,g.estimate,color='#888',lw=.9)
        a.set_xlabel('Year relative to release',fontsize=10,labelpad=3);a.set_ylabel('Mortality relative to non-incarcerated',fontsize=10,labelpad=1)
        a.tick_params(axis='y',labelrotation=90,pad=1)
        a.set_title(f'({"abcdef"[p-1]}) '+titles[p-1],fontsize=16,family='serif',pad=22)
    return fig

def evolution(source):
    d=frame(source,('panel','series','x','estimate','low','high'),['panel','series','x'],28)
    fig=Figure(figsize=(8,12.90),facecolor='white');colors=['#64738b','#bb0038'];names=['TWFE OLS','Callaway-Sant’Anna']
    for p in [1,2]:
        a=axis(fig,(.11,.594 if p==1 else .090,.875,.352));a.grid(color='#e6e6e6',lw=1)
        for j,(name,c) in enumerate(zip(names,colors)):
            g=d[(d.panel==p)&(d.series==name)];interval(a,g,c,'o' if j==0 else 'D',offset=-.1 if j==0 else 0,ms=4.5,caps=3)
        a.axvline(-1,color='#aaa',ls=(0,(6,3)),lw=1.2);a.axhline(0,color='#aaa',ls=(0,(6,3)),lw=1.2)
        a.set_xlim(-7.35,5.22);a.set_ylim((-.108,.171) if p==1 else (-.118,.158));a.set_xticks([-7,-5,-3,-1,1,3,5]);a.set_yticks([-.1,-.05,0,.05,.1,.15]);a.yaxis.set_major_formatter(FuncFormatter(fmt));a.tick_params(labelsize=14)
        a.set_xlabel('Year to/from Evolution Curriculum Reform (two-year bins)',fontsize=14,labelpad=2);a.set_ylabel('Evolution Knowledge',fontsize=15,labelpad=6)
        handles=[Line2D([],[],ls='none',marker=m,mfc='white',mec=c,ms=5,label=n) for n,c,m in zip(names,colors,['o','D'])]
        a.legend(handles=handles,loc='upper center',bbox_to_anchor=(.5,-.14),ncol=2,frameon=False,fontsize=14,handlelength=.5,columnspacing=1.4,handletextpad=.4)
        fig.text(.54,.982 if p==1 else .466,'('+('A' if p==1 else 'B')+') States '+('reducing' if p==1 else 'expanding')+' evolution coverage',ha='center',family='serif',fontsize=21,fontweight='bold')
    return fig

def receipt(source):
    d=frame(source,('panel','series','x','estimate','low','high'),['panel','series','x'],64)
    fig=Figure(figsize=(13,4.59),facecolor='white');names=['Conventional','Imputation'];colors=['#963f4c','#285a7b']
    for p in [1,2]:
        a=axis(fig,(.047+(p-1)*.524,.22,.416,.72));a.set_xlim(-8.3,7.3);a.set_ylim(-21.2,21.2);a.set_yticks([-20,-10,0,10,20]);a.set_xticks(range(-8,8,2));a.grid(axis='y',color='#e7eef0',lw=.9)
        for name,c,m in zip(names,colors,['s','o']):
            g=d[(d.panel==p)&(d.series==name)];a.fill_between(g.x,g.low,g.high,color=c,alpha=.26,edgecolor=c,lw=1)
            a.plot(g.x,g.estimate,color=c,marker=m,ms=5,lw=1)
        a.axvline(0,color='#888',lw=.9);a.axhline(0,color='#888',lw=.9);a.tick_params(labelsize=12);a.tick_params(axis='y',labelrotation=90,pad=1)
        a.set_xlabel('Week since receipt',fontsize=12,labelpad=2);a.set_ylabel('MPX, $',fontsize=12,labelpad=4)
        a.legend([Line2D([],[],color=c,marker=m,ms=5,lw=1) for c,m in zip(colors,['s','o'])],names,loc='upper center',bbox_to_anchor=(.5,-.13),ncol=2,frameon=False,fontsize=12,columnspacing=1.6,handlelength=3)
        fig.text(.002+(p-1)*.513,.93,'AB'[p-1],fontsize=25,fontweight='bold')
    return fig

def transforms(source):
    d=frame(source,('panel','x','control','treated','estimate','low','high'),['panel','x'],18)
    fig=Figure(figsize=(10,6.982),facecolor='white');periods=['1986–1989','1990–1994','1995–1999','2000–2004','2005–2009','2010–2014']
    for p in [1,2,3]:
        left=.052+(p-1)*.34;g=d[d.panel==p]
        for row in [0,1]:
            a=axis(fig,(left,.70 if row==0 else .126,.26,.255 if row==0 else .342));a.set_xlim(-.2,5.2);a.axhline(0,color='#999',ls=(0,(1,2)),lw=.7);a.axvline(1.5,color='#aaa',lw=.6)
            a.set_xticks(range(6),periods,rotation=45,ha='right',fontsize=9);a.tick_params(axis='x',pad=1,length=3.5);a.tick_params(axis='y',labelrotation=90,labelsize=11,pad=1,length=3.5)
            for s in ['top','right']:a.spines[s].set_visible(True)
            a.set_xlabel('Period',fontsize=12,labelpad=1)
            if row==0:
                a.plot(g.x,g.control,color='#555',marker='s',ms=5,lw=.9);a.plot(g.x,g.treated,color='#bbb',marker='^',ms=5,lw=.9,ls=(0,(6,3)))
                a.set_ylim(-.25,1.65);a.set_yticks([0,1.5]);a.set_yticks([.5,1],minor=True);a.tick_params(axis='y',which='minor',length=3.5)
                a.set_ylabel(['E(lnexp|treat)','E(lnexpplus1|treat)','E(asinhexp|treat)'][p-1],fontsize=11,labelpad=0)
                a.set_title(['log(exp)','log(exp+1)','asinh(exp)'][p-1],fontsize=14,pad=4)
                handles=[Line2D([],[],color=c,marker=m,ms=5,lw=.9,ls=ls,label=label) for c,m,ls,label in [('#555','s','solid','treat=0'),('#bbb','^',(0,(6,3)),'treat=σ')]]
                a.legend(handles=handles,loc='upper center',bbox_to_anchor=(.5,-.52),ncol=2,frameon=True,fancybox=False,framealpha=1,edgecolor='#666',fontsize=12,handlelength=1.2,columnspacing=1,borderpad=.3)
            else:
                a.errorbar(g.x,g.estimate,yerr=[g.estimate-g.low,g.high-g.estimate],fmt='D',color='#b1b1b1',ecolor='#777',capsize=2,elinewidth=.7,ms=3.7)
                a.set_ylim((-.25,.51) if p==1 else (-.43,.65));a.set_yticks([-.2,0,.2,.4] if p==1 else [-.4,-.2,0,.2,.4,.6]);a.yaxis.set_major_formatter(FuncFormatter(fmt));a.set_ylabel('βᴰᴰ (95% CI)',fontsize=10,labelpad=0)
    return fig

def heatmap(source):
    d=frame(source,('row','state','column','date','red','green','blue'),['row','column'],2950)
    if ((d[['red','green','blue']]<0)|(d[['red','green','blue']]>255)).any().any():raise ValueError('Invalid supplied display color.')
    d=d.sort_values(['row','column']);fig=Figure(figsize=(10,9.00),facecolor='white');a=fig.add_axes((.100,.136,.86,.811))
    rgb=d[['red','green','blue']].to_numpy().reshape(50,59,3)/255
    a.imshow(rgb,interpolation='nearest',aspect='auto',origin='upper',extent=(-.5,58.5,49.5,-.5))
    a.set_xticks(range(59),d.drop_duplicates('column').date,rotation=90,fontsize=6.5);a.set_yticks(range(50),d.drop_duplicates('row').state,fontsize=6.5)
    a.set_xticks(np.arange(-.5,59,1),minor=True);a.set_yticks(np.arange(-.5,50,1),minor=True);a.grid(which='minor',color='#62656a',lw=.45);a.tick_params(which='both',length=0,pad=1.5)
    a.set_xlabel('Week',fontsize=8,labelpad=2);a.set_ylabel('State',fontsize=8,labelpad=2)
    for s in a.spines.values():s.set_color('#686868');s.set_linewidth(.7)
    palette=np.array([[222,222,223],[206,206,207],[180,181,183],[157,158,161],[138,139,142],[116,117,121],[94,96,101],[73,75,81],[53,56,62],[41,44,50]])/255
    cb=fig.add_axes((.15,.01,.75,.028));cb.imshow(palette[None,:,:],aspect='auto',interpolation='nearest');cb.set_xticks([]);cb.set_yticks([])
    for s in cb.spines.values():s.set_color('#666');s.set_linewidth(.5)
    # Preserve the visual scale without inventing numeric labels absent in the source.
    return fig

RENDERERS=dict(zip(['values-financial-promotion-forest','mental-health-study-comparison','treatment-arm-domain-intervals','expansion-eligibility-event-2panel','delay-state-event-shaded-windows','release-mortality-five-paths-6panel','evolution-reform-two-estimators','receipt-week-overlapping-bands','transformation-trends-effects-2x3','state-week-grayscale-heatmap'],[values,mental,treatments,expansion,delay,mortality,evolution,receipt,transforms,heatmap]))
