"""Chapter 26: dated wholesale prices, note balances and the ordinary budget."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter
from style import figure, T, FIG_W, ZH, MONEY, PRICE, FISCAL, INSTIT, AMBER, MUTED, tint
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'checks'))
import check_ch26 as C

@figure('weimar_prices')
def weimar_prices():
    d=C.prices();fig,axs=plt.subplots(1,2,figsize=(FIG_W,2.9))
    fig.subplots_adjust(left=.10,right=.98,bottom=.21,top=.84,wspace=.41)
    for ax,lo,hi,title in [(axs[0],'1920-01','1922-12',T('(a) 平台以后，速度加快','(a) A plateau, then acceleration')),(axs[1],'1923-01','1924-06',T('(b) 陡升以后，停在高位','(b) A surge, then a high plateau'))]:
        a=d.loc[lo:hi];x=np.arange(len(a));ax.plot(x,a.wpi_1913_100,color=PRICE,lw=2)
        ax.set_yscale('log');ax.set_title(title,loc='left',fontsize=9,weight='bold',pad=7)
        starts=[i for i,s in enumerate(a.index) if s.endswith('-01')];ax.set_xticks(starts,[a.index[i][:4] for i in starts]);ax.tick_params(labelsize=8.5)
        ax.set_xlabel(T('年份','Year'),fontsize=9.5)
        ax.yaxis.set_major_locator(LogLocator(base=10,numticks=5));ax.yaxis.set_minor_formatter(NullFormatter())
        ax.grid(axis='y',alpha=.15);ax.spines[['top','right']].set_visible(False)
        ax.set_xlim(-.7,len(a)-.3)
    axs[0].set_ylabel(T('批发物价指数（1913 = 100，对数）','Wholesale prices (1913 = 100, log)'),fontsize=9.5)
    axs[0].text(.05,.86,T('1920—1921年中\n物价没有一路急涨','1920–mid-1921\nprices did not soar'),transform=axs[0].transAxes,fontsize=7.8,color=PRICE)
    axs[1].axvline(10,color=MUTED,ls=':',lw=.8)
    axs[1].text(.05,.68,T('1923年11月\n新币开始发行','November 1923\nnew notes issued'),transform=axs[1].transAxes,fontsize=7.8,color=MUTED)
    return fig

@figure('weimar_balances')
def weimar_balances():
    fig,axs=plt.subplots(1,2,figsize=(FIG_W,2.9));fig.subplots_adjust(left=.10,right=.98,bottom=.21,top=.83,wspace=.40)
    ax=axs[0];p,n=C.inflation_multiples();x=np.arange(2)
    ax.bar(x-.17,p,.31,color=PRICE);ax.bar(x+.17,n,.31,color=AMBER,hatch='//',linewidth=0)
    ax.set_yscale('log');ax.set_ylim(1,2e5);ax.set_xticks(x,[T('1923年7月','Jul 1923'),T('8月','Aug')]);ax.set_title(T('(a) 钞票追不上物价','(a) Notes lag behind prices'),loc='left',fontsize=9,weight='bold',pad=7)
    ax.set_ylabel(T('倍数（1922年1月 = 1，对数）','Multiples (Jan 1922 = 1, log)'),fontsize=9.5)
    for j in range(2):
        ax.text(x[j]-.17,p[j]*1.25,f'{p[j]:,.0f}',ha='center',va='bottom',color=PRICE,fontsize=7.7)
        ax.text(x[j]+.17,n[j]*1.25,f'{n[j]:,.0f}',ha='center',va='bottom',color=AMBER,fontsize=7.7)
    ax.text(.04,.92,T('批发物价','Wholesale prices'),transform=ax.transAxes,color=PRICE,fontsize=7.8)
    ax.text(.04,.81,T('帝国银行券','Reichsbank notes'),transform=ax.transAxes,color=AMBER,fontsize=7.8)
    ax.text(.05,.08,T('实际余额约剩19%与22%','Real balances: about 19% and 22%'),transform=ax.transAxes,color=MUTED,fontsize=7.6,bbox=dict(facecolor='white',edgecolor='none',alpha=.95,pad=1.5))
    ax=axs[1];d=C.notes();x=np.arange(len(d));ax.bar(x,d.old_notes_million_newunit,color=MONEY,width=.55);ax.bar(x,d.new_rentenmarks_million,bottom=d.old_notes_million_newunit,color=AMBER,width=.55,hatch='//',linewidth=0)
    ax.set_ylim(0,3900);ax.set_xticks(x,[T('1923末','Dec 1923'),T('1924.3','Mar 1924'),T('7月','Jul')]);ax.set_title(T('(b) 稳定后，正式钞票增加','(b) Notes grow after stability'),loc='left',fontsize=9,weight='bold',pad=7)
    ax.set_ylabel(T('百万地租马克等值','Millions of rentenmark equivalents'),fontsize=9.5)
    for j,r in enumerate(d.itertuples()):ax.text(j,r.old_notes_million_newunit+r.new_rentenmarks_million+65,f'{r.old_notes_million_newunit+r.new_rentenmarks_million:,.0f}',ha='center',color=MONEY,fontsize=7.8)
    ax.text(.03,.93,T('地租银行新钞','New Rentenbank notes'),transform=ax.transAxes,color=AMBER,fontsize=7.8)
    ax.text(.03,.83,T('帝国银行旧钞','Old Reichsbank notes'),transform=ax.transAxes,color=MONEY,fontsize=7.8)
    for ax in axs:ax.spines[['top','right']].set_visible(False);ax.tick_params(labelsize=8.5);ax.grid(axis='y',alpha=.12);ax.set_axisbelow(True)
    return fig

@figure('weimar_budget')
def weimar_budget():
    d=C.budget();x=np.arange(len(d));balance=d.revenue_million_goldmark-d.expenditure_million_goldmark
    fig,ax=plt.subplots(figsize=(FIG_W,2.5));fig.subplots_adjust(left=.12 if ZH else .14,right=.98,bottom=.24,top=.93)  # Inter needs room for the two-line ylabel.
    ax.bar(x,balance,width=.55,color=FISCAL);ax.axhline(0,color=MUTED,lw=.8)
    for i,v in enumerate(balance):ax.text(i,v+(9 if v>0 else -10),f'{v:+.1f}',ha='center',va='bottom' if v>0 else 'top',fontsize=8,color=FISCAL)
    ax.set_ylim(-420,215);ax.set_xticks(x,[T('1923.12','Dec 1923'),T('1924.1','Jan 1924'),T('2月','Feb'),T('3月','Mar'),T('4月','Apr'),T('5月','May'),T('6月','Jun')]);ax.set_ylabel(T('普通预算余额（百万金马克）','Ordinary budget balance\n(million gold marks)'),fontsize=9.5)
    ax.text(.30,.12,T('12月仍有赤字；次年2月再现小额赤字','Deficit in December; a small deficit again in February'),transform=ax.transAxes,fontsize=8,color=INSTIT)
    ax.spines[['top','right']].set_visible(False);ax.tick_params(labelsize=8.5);ax.grid(axis='y',alpha=.12);ax.set_axisbelow(True)
    return fig
