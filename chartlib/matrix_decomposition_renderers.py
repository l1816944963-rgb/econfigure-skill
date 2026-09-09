"""Approved heatmap and decomposition renderers with supplied values only."""
from pathlib import Path
import numpy as np
from chartlib.asset_runtime import read_frame,require_columns,require_finite
from matplotlib.figure import Figure
from matplotlib.colors import ListedColormap,Normalize
from matplotlib.colorbar import ColorbarBase
from matplotlib.patches import Rectangle,Patch
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter

def data(source,cols,keys,n):
    d=read_frame(source);require_columns(d,cols)
    if len(d)!=n or d.duplicated(keys).any():raise ValueError('Invalid shape or duplicate plotting keys.')
    nums=[c for c in ['row','column','panel','order','red','green','blue','start','end','level','bottom','top','year'] if c in d]
    require_finite(d,tuple(nums))
    if 'red' in d and ((d[['red','green','blue']]<0)|(d[['red','green','blue']]>255)).any().any():raise ValueError('Colors must lie within 0..255.')
    return d.sort_values(keys).reset_index(drop=True)
def companion(source,provided,suffix):
    if provided is not None:return read_frame(provided)
    if not isinstance(source,(str,Path)):raise ValueError(f'Caller must supply the {suffix} table with frame inputs.')
    p=Path(source);return read_frame(p.with_name(p.name.replace('.fixture.csv',f'.{suffix}.csv')))
def cmap(p):
    require_columns(p,('red','green','blue'));require_finite(p,('red','green','blue'))
    if ((p[['red','green','blue']]<0)|(p[['red','green','blue']]>255)).any().any():raise ValueError('Invalid palette.')
    return ListedColormap(p[['red','green','blue']].to_numpy()/255)
def axis(fig,b):
    a=fig.add_axes(b);a.tick_params(length=3.5,width=.8,labelsize=11)
    for s in ['top','right']:a.spines[s].set_visible(False)
    return a

def exposure(source,palette=None):
    d=data(source,('row','column','date','red','green','blue'),['row','column'],5000);p=companion(source,palette,'palette')
    fig=Figure(figsize=(10,6.65),facecolor='white');a=fig.add_axes((.102,.058,.734,.924))
    a.imshow(d[['red','green','blue']].to_numpy().reshape(100,50,3)/255,origin='upper',aspect='auto',interpolation='nearest',extent=(-.5,49.5,0,100))
    a.set_yticks([25,50,75,100],['25-','50-','75-','100-']);a.set_xticks(range(0,49,6),['Sep 2007','Mar 2008','Sep 2008','Mar 2009','Sep 2009','Mar 2010','Sep 2010','Mar 2011','Sep 2011'])
    a.tick_params(length=0,labelsize=8,pad=3);a.set_ylabel('Quantile of Exposure',fontsize=11,labelpad=6)
    for s in a.spines.values():s.set_visible(False)
    for x in [16,26,33]:a.axvline(x,color='#909c9d',ls=(0,(4,2)),lw=1.1)
    cbax=fig.add_axes((.884,.42,.020,.15));cb=ColorbarBase(cbax,cmap=cmap(p),norm=Normalize(.45,1.4),ticks=[.6,.8,1,1.2]);cb.outline.set_visible(False);cbax.tick_params(length=0,labelsize=8,pad=3)
    cbax.set_title('Scaled\nSales',fontsize=11,loc='left',pad=5)
    return fig

def factors(source,palette=None):
    d=data(source,('panel','row','column','assets','factors','red','green','blue'),['panel','row','column'],1584);p=companion(source,palette,'palette')
    fig=Figure(figsize=(8,11.16),facecolor='white');titles=['Market','HML','SMB','RMW','CMA','Momentum','BAB','QMJ']
    ranges=[(.84,.99),(-.25,.8),(.28,.88),(-.17,.67),(-.05,.61),(-.12,.9),(-.4,.51),(.34,.81)]
    marks=[[(3,100),(5,100),(7,100),(11,100)],[(3,100),(5,100),(7,150),(11,250)],[(3,100),(5,100),(7,100),(11,100)],[(3,100),(5,100),(7,100),(11,150)],[(5,100),(3,250),(7,200),(11,350)],[(3,100),(5,100),(7,100),(11,100)],[(3,100),(5,100),(7,150),(11,150)],[(3,100),(5,100),(7,100),(11,150)]]
    for panel in range(1,9):
        row=(panel-1)//2;col=(panel-1)%2;left=.067+col*.482;bottom=.784-row*.248;a=fig.add_axes((left,bottom,.39,.175));g=d[d.panel==panel]
        a.imshow(g[['red','green','blue']].to_numpy().reshape(18,11,3)/255,origin='upper',aspect='auto',interpolation='nearest',extent=(.5,11.5,975,75))
        a.set_xticks([2,4,6,8,10]);a.set_yticks(range(100,1000,100));a.tick_params(length=1.5,width=.4,labelsize=6.5,pad=1)
        a.set_xlabel('Number of factors (p)',fontsize=8,family='serif',labelpad=2);a.set_ylabel('Number of assets selected',fontsize=8,family='serif',labelpad=1)
        a.set_title(f'Panel {"ABCDEFGH"[panel-1]}. {titles[panel-1]}',fontsize=11,family='serif',pad=7)
        for s in a.spines.values():s.set_color('#aaa');s.set_linewidth(.4)
        x,y=zip(*marks[panel-1]);a.scatter(x,y,marker='x',s=12,linewidths=.7,color='#fa443d')
        cbax=fig.add_axes((left+.395,bottom,.009,.175));cb=ColorbarBase(cbax,cmap=cmap(p[p.panel==panel].sort_values('index')),norm=Normalize(*ranges[panel-1]))
        cb.outline.set_edgecolor('#aaa');cb.outline.set_linewidth(.4);cbax.tick_params(length=1,labelsize=6.5,pad=1)
    return fig

def ageyear(source):
    d=data(source,('panel','row','column','age','year','red','green','blue'),['panel','row','column'],22080)
    fig=Figure(figsize=(10,11.67),facecolor='white');maxima=[.158,.031,.229,1.68];ticksets=[[0,.05,.1,.15],[0,.01,.02,.03],[0,.05,.1,.15,.2],[.5,1,1.5]]
    for panel in range(1,5):
        col=(panel-1)%2;row=(panel-1)//2;left=.066+col*.522;bottom=.579-row*.525;a=fig.add_axes((left,bottom,.399,.342));g=d[d.panel==panel]
        a.imshow(g[['red','green','blue']].to_numpy().reshape(80,69,3)/255,origin='upper',aspect='auto',interpolation='nearest',extent=(1953.5,2022.5,100,20))
        a.set_xticks([1960,1980,2000,2020]);a.xaxis.tick_top();a.xaxis.set_label_position('top');a.set_xlabel('Year',fontsize=15,labelpad=9);a.set_ylabel('Age',fontsize=15,labelpad=4)
        a.set_yticks(range(20,100,10));a.tick_params(length=4,width=1.5,labelsize=14,top=True,bottom=True,right=True,labelbottom=False)
        for s in a.spines.values():s.set_color('#333');s.set_linewidth(1.3)
        # Cell boundaries are white gaps, not smoothing or interpolated surface values.
        a.set_xticks(np.arange(1953.5,2023,1),minor=True);a.set_yticks(np.arange(20,101,1),minor=True);a.grid(which='minor',color='white',lw=.40,alpha=.95);a.tick_params(which='minor',length=0)
        cbax=fig.add_axes((left,bottom-.024,.399,.013));cb=ColorbarBase(cbax,cmap='Greys',norm=Normalize(0,maxima[panel-1]),orientation='horizontal',ticks=ticksets[panel-1]);cb.outline.set_linewidth(.7);cbax.tick_params(length=3,pad=6,labelsize=13);cbax.xaxis.set_major_formatter(FuncFormatter(lambda v,p:f'{v:g}'))
        fig.text(.008+col*.519,.979-row*.524,'ABCD'[panel-1],fontsize=22,fontweight='bold')
    return fig

def exports(source):
    d=data(source,('panel','order','label','start','end','kind','display'),['panel','order'],10)
    if (d[['start','end']]<0).any().any() or not set(d.kind)<= {'total','negative','positive'}:raise ValueError('Invalid supplied waterfall endpoints.')
    fig=Figure(figsize=(12.6,5),facecolor='white')
    for panel in [1,2]:
        a=axis(fig,(.073+(panel-1)*.496,.21,.407,.692));g=d[d.panel==panel]
        for r in g.itertuples():
            low=min(r.start,r.end);high=max(r.start,r.end);a.bar(r.order,high-low,bottom=low,width=.67,color='#aaa' if r.kind=='total' else 'white',edgecolor='#222',lw=1,hatch=None if r.kind=='total' else 'xxxx' if r.kind=='negative' else '////')
            if r.order<4:a.plot([r.order+.335,r.order+1-.335],[r.end,r.end],color='#333',lw=.7)
            a.text(r.order,low-(390 if panel==1 else 48) if r.kind=='negative' else high+(155 if panel==1 else 20),r.display,ha='center',va='top' if r.kind=='negative' else 'bottom',family='serif',fontsize=16,color='#16314b')
        a.set_xlim(-.52,4.5);a.set_ylim(0,8000 if panel==1 else 900);a.set_yticks(range(0,8001,1000) if panel==1 else range(0,901,100));a.yaxis.set_major_formatter(FuncFormatter(lambda v,p:f'{int(v):,}'.replace(',',' ')))
        a.set_xticks(range(5),g.label,fontsize=12,family='serif',color='#16314b');a.tick_params(axis='x',length=0,pad=10);a.tick_params(axis='y',direction='in',labelsize=14)
        for t in a.get_yticklabels():t.set_fontfamily('serif');t.set_color('#16314b')
        a.text(-.16,1.065,'USD 100 million',transform=a.transAxes,ha='left',family='serif',fontsize=16,color='#16314b')
    return fig

def dashboard(source,components=None):
    d=data(source,('year','order','level','start','end','display','color'),['order'],18);c=companion(source,components,'components')
    require_columns(c,('order','series','bottom','top','display'));require_finite(c,('order','bottom','top'))
    if (d.level<=0).any() or (d[['start','end']]<0).any().any() or len(c)<90 or (c.bottom>c.top).any():raise ValueError('Invalid supplied levels or component endpoints.')
    fig=Figure(figsize=(14,6.14),facecolor='white');a=axis(fig,(.030,.523,.467,.414))
    for r in d.itertuples():
        a.plot([r.year,r.year],[1,r.level],color=r.color,alpha=.42,lw=.75,ls=(0,(2,2)));a.plot(r.year,r.level,'o',color=r.color,ms=5.5)
        below=r.order in [0,8,10,11,13,15,17]
        a.annotate(f'{r.level:.4f}',(r.year,r.level),xytext=(0,-7 if below else 5),textcoords='offset points',ha='center',va='top' if below else 'bottom',fontsize=11,family='serif')
    a.set_xlim(1999,2018);a.set_ylim(2.6,1);a.set_xticks([2000,2002,2004,2006,2008,2010,2012,2014,2016,2017]);a.xaxis.tick_top();a.tick_params(top=True,labeltop=True,bottom=False,labelbottom=False,labelsize=12);a.set_yticks(np.arange(1,2.61,.2));a.tick_params(axis='y',labelsize=12)
    a.tick_params(axis='x',labelsize=11);a.get_xticklabels()[-2].set_ha('right')
    for s in a.spines.values():s.set_visible(True);s.set_linewidth(1)
    a.text(1999.6,2.52,r'$\circ\quad I(PC)$',family='serif',fontsize=15)
    # Split only the waterfall's display axis; both total bars still start at zero.
    upper=axis(fig,(.030,.112,.467,.356));lower=axis(fig,(.030,.056,.467,.049))
    for ax in [upper,lower]:
        for r in d.itertuples():
            if r.order==0:low,high,color=0,r.level,'#76c9ef'
            else:low,high,color=min(r.start,r.end),max(r.start,r.end),'#b9e66e' if r.end<r.start else '#f6bdbe'
            ax.bar(r.order,high-low,bottom=low,width=.81,color=color,edgecolor='#bbb',lw=.7)
        ax.bar(18,2.3688,bottom=0,width=.81,color='#76c9ef',edgecolor='#bbb',lw=.7)
        ax.set_xlim(-.5,18.5);ax.spines['right'].set_visible(True);ax.spines['right'].set_linewidth(1)
    upper.set_ylim(1,2.4);upper.set_yticks(np.arange(1.2,2.41,.2));upper.tick_params(axis='x',bottom=False,labelbottom=False);upper.spines['top'].set_visible(True);upper.spines['bottom'].set_visible(False)
    lower.set_ylim(0,.2);lower.set_yticks([0]);lower.spines['top'].set_visible(False);lower.set_xticks([0,2,4,6,8,10,12,14,16,18],[2000,2002,2004,2006,2008,2010,2012,2014,2016,2017]);lower.tick_params(labelsize=12)
    for r in d.itertuples():
        if r.order==0:continue
        high=max(r.start,r.end);low=min(r.start,r.end);above=r.order<=7
        upper.text(r.order,high+.015 if above else low-.025,r.display,rotation=90,ha='center',va='bottom' if above else 'top',fontsize=11,family='serif',color='#48822b' if r.end<r.start else '#d54141' if r.order==5 else '#222')
    upper.text(18,2.34,'2.3688',rotation=90,ha='center',va='top',fontsize=13,family='serif');fig.text(.037,.066,'1.1364',rotation=90,ha='center',va='bottom',fontsize=12,family='serif')
    for y in [.105,.112]:fig.add_artist(Line2D([.024,.035],[y-.005,y+.006],transform=fig.transFigure,color='#444',lw=1))
    upper.legend(handles=[Patch(facecolor='#f6bdbe',label='Increase'),Patch(facecolor='#b9e66e',label='Decrease')],loc='upper left',frameon=False,fontsize=12,handlelength=1.1,labelspacing=.25)
    right=axis(fig,(.53,.056,.467,.881));colors={'pCF':'#f8c99d','pES':'#99cf97','pEI':'#bcadcb','pIS':'#fcfbb0','pED':'#97b8ec','ICF':'#edb3f0','IES':'#aeb390','IPE':'#afe0e5'}
    for r in c.itertuples():
        right.bar(r.order,r.top-r.bottom,bottom=r.bottom,width=.50,color=colors[r.series],edgecolor='#52656b',lw=.7)
        if isinstance(r.display,str) and r.display:
            right.text(r.order,(r.bottom+r.top)/2 if r.bottom>=0 else r.bottom+.015,r.display,rotation=90 if r.bottom>=0 else 0,ha='center',va='center' if r.bottom>=0 else 'bottom',fontsize=11,family='serif')
    right.set_xlim(-.5,17.5);right.set_ylim(-.5,2.5);right.set_yticks(np.arange(-.5,2.6,.5));right.set_xticks(range(18),range(2000,2018),rotation=15,fontsize=10);right.tick_params(axis='y',labelsize=12)
    right.spines['bottom'].set_position(('data',0));right.spines['top'].set_visible(True);right.spines['right'].set_visible(True)
    right.add_patch(Rectangle((-.5,-.5),18,3,fill=False,edgecolor='#222',lw=.8))
    top_handles=[Patch(facecolor=c,edgecolor='#555',label=label) for c,label in [('#f8c99d',r'$I_{pCF}$'),('#99cf97',r'$I_{pES}$'),('#bcadcb',r'$I_{pEI}$'),('#fcfbb0',r'$I_{pIS}$'),('#97b8ec',r'$I_{pED}$')]]
    leg=right.legend(handles=top_handles,loc='upper left',frameon=False,fontsize=16,handlelength=2,labelspacing=.2,handletextpad=.3,borderpad=.1);right.add_artist(leg)
    right.legend(handles=[Patch(facecolor=c,edgecolor='#555',label=l) for c,l in [('#edb3f0',r'$I_{ICF}$'),('#aeb390',r'$I_{IES}$'),('#afe0e5',r'$I_{IPE}$')]],loc='lower right',frameon=False,ncol=3,fontsize=16,handlelength=2,handletextpad=.25,columnspacing=.7,borderpad=.2)
    for x,y,label in [(.006,.962,'A'),(.032,.484,'B'),(.519,.968,'C')]:fig.text(x,y,label,family='serif',fontsize=15)
    return fig

RENDERERS=dict(zip(['exposure-sales-diverging-heatmap','factor-selection-heatmaps-8panel','age-year-grayscale-heatmaps-4panel','export-value-added-waterfall-2panel','index-change-component-dashboard'],[exposure,factors,ageyear,exports,dashboard]))
