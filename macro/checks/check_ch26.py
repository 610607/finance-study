"""Chapter 26: documentary readings, units, numerical examples and evidence anchors.

python checks/check_ch26.py
Modern quotations: data/fetch/verify_web_quotes.py data/snapshots/weimar_facts.csv
No fitted model or custom solver: the teaching calculations use the chapter's exact
budget identity, percentage arithmetic and logarithms (NumPy/standard library).
"""
from __future__ import annotations
import math,re,sys,os
from pathlib import Path
import numpy as np
from common import ROOT,load_snapshot,quoted,anchors
TEX=ROOT/'zh/ch26_weimar.tex'

def prices():
    d,_=load_snapshot('weimar_prices_1920_1924');return d.set_index('date')
def notes():return load_snapshot('weimar_notes_1923_1924')[0]
def budget():return load_snapshot('weimar_budget_1923_1924')[0]
def facts():return load_snapshot('weimar_facts',dtype=str,keep_default_na=False)[0].set_index('id')

def inflation_multiples():
    f=facts()
    pairs=[list(map(float,f.loc[k,'value'].split(';')))[-2:] for k in ['s_ratio1','s_ratio2']]
    return np.array([v[0] for v in pairs]),np.array([v[1] for v in pairs])

def eq_budget(H0,P0,H1,P1):
    """eq:weimar-budget, fixed basket units; no private-asset acquisition."""
    h0,h1=H0/P0,H1/P1;pi=P1/P0-1
    return (H1-H0)/P1,h1-h0,pi/(1+pi)*h0

def main():
    f=facts();assert f.index.is_unique
    # Each empirical numeric reading is anchored to a short verbatim passage.
    # OCR nth in bt_valorize is the scanned 11th; r,2oo in bt_limit24 is 1,200.
    # Numeric tokens are checked in both English and German punctuation conventions.
    word_reads={'bt_warloans':{.125},'bt_wagetax':{14},'bt_limit24':{1200},'bt_valorize':{11}}
    for id,row in f.iterrows():
        q=row['quote'];tokens=re.findall(r'\d+(?:[.,*·]\d+)*',q)
        seen=set()
        for token in tokens:
            for cand in [token.replace(',',''),token.replace('.','').replace(',','.'),token.replace('*','.'),token.replace(',','').replace('*','.')]:
                try:seen.add(float(cand))
                except ValueError:pass
        if '1914-18' in q:seen.add(1918)
        seen|=word_reads.get(id,set())
        for value in filter(None,row['value'].split(';')):
            if '/' in value:
                a,b=value.split('/');v=float(a)/float(b)
            else:v=float(value)
            assert v in seen,(id,v,q)
            quoted('document reading '+id,v,expected=v)
    # Currency conversion: modern 10^12, British 1937 trillion=10^18.
    quoted('one rentenmark in paper marks',1000*10**9,10**12)
    quoted('British trillion in paper marks',(10**6)**3,10**18)
    quoted('496 British trillions in million new marks',496*10**18/10**12/10**6,496)
    # Dates and counts explicitly printed in the narrative.
    quoted('15 to 20 November: five days',20-15,5)
    quoted('London A plus B (billion gold marks)',12+38,50)
    quoted('statutory government plus private credit quotas (million)',1200+1200,2400)
    assert float(f.loc['law_capital','value'])==3200
    assert float(f.loc['law_credit','value'])==1200
    # Sargent's stated price/note ratios are rounded source summaries.
    for month,p,n in [('July',2038,378),('August',25723,5748)]:
        frac=n/p
        quoted(month+' real note balance ratio',frac,.1855 if month=='July' else .2235,tol=.0001)
        quoted(month+' rounded percent in figure',round(frac*100),19 if month=='July' else 22)
    quoted('roughly 380-fold note increase',378,380,tol=2)
    # Numerical table subsets: monthly prices preserve old-unit observations only.
    p=prices();assert len(p)==54 and p.index.is_monotonic_increasing
    assert p.loc['1920-01','wpi_1913_100']==1260
    assert p.loc['1921-05','wpi_1913_100']==1310
    assert p.loc['1923-09','wpi_1913_100']==2394889300
    assert p.loc['1923-10','wpi_1913_100']==709480000000
    assert p.loc['1924-06','wpi_1913_100']==115900000000000
    ratio=p.loc['1923-10','wpi_1913_100']/p.loc['1923-09','wpi_1913_100']
    quoted('Sep to Oct monthly index ratio',ratio,296.25,tol=.005)
    quoted('monthly-index percentage change',100*(ratio-1),29525,tol=.5)
    quoted('equivalent 30-day doubling time',30*math.log(2)/math.log(ratio),3.65,tol=.005)
    quoted('narrative equivalent doubling time',30*math.log(2)/math.log(ratio),3.7,tol=.05)
    quoted('daily doubling for 30 days',2**30,1073741824)
    # Original table G1 has two columns, each with its own year counter.
    # Only runs if the source cache exists; verify_web_quotes provides the online path.
    cache=Path(os.environ.get('WEB_CACHE',Path.home()/'.cache'/'finance-study'/'web'))/'sargent1982.pdf'
    if cache.exists():
        import subprocess
        raw=subprocess.run(['pdftotext','-layout',str(cache),'-'],capture_output=True,text=True,check=True).stdout
        block=raw[raw.index('Table Gl         German Wholesale Prices'):raw.index('surely understated by the reparations')]
        monthnames=['January','February','March','April','May','June','July','August','September','October','November','December']
        pat=re.compile(r'(?:(19\d{2})\s+)?('+'|'.join(monthnames)+r')\s+([\d,]+)')
        years=[None,None];original={}
        for line in block.splitlines():
            matches=list(pat.finditer(line))
            for side,m in enumerate(matches):
                y,mon,v=m.groups()
                if y:years[side]=int(y)
                if years[side]:original[f'{years[side]}-{monthnames.index(mon)+1:02d}']=int(v.replace(',',''))
        for date,row in p.iterrows():assert original[date]==row.wpi_1913_100,(date,original.get(date),row.wpi_1913_100)
        print('ok all 54 monthly price observations against the original PDF table')
    # Keynes original price/volume example and Ohlin-based teaching input.
    quoted('Keynes export proceeds',.9*1.2,1.08,tol=1e-12)
    quoted('Keynes export proceeds increase (%)',100*(.9*1.2-1),8,tol=1e-12)
    quoted('Ohlin teaching split',100-20,80)
    quoted('reversed transfer: direct trade adjustment',100*.2+100*.2,40)
    quoted('reversed transfer: residual',100-40,60)
    # Fixed commodity basket makes every real balance's unit unambiguous.
    for params,expected in [((100,100,200,400),(.25,-.5,.75)),((100,100,300,500),(.4,-.4,.8))]:
        result=eq_budget(*params)
        for v,e in zip(result,expected):quoted('real financing teaching calculation',v,e,tol=1e-12)
        assert math.isclose(result[0],result[1]+result[2])
    quoted('two-week lag when prices double weekly',100/2**2,25)
    quoted('loss during two-week lag',100-100/4,75)
    quoted('paper-mark dollar quotation on Nov 15 (trillion)',2520/1000,2.5,tol=.05)
    quoted('official quotation on Nov 20 (trillion)',4200/1000,4.2)
    quoted('Cologne free quote on Nov 20 (trillion)',11700/1000,11.7)
    # Budget: retain real deficits, do not turn ordinary into consolidated accounts.
    b=budget();balance=b.revenue_million_goldmark-b.expenditure_million_goldmark
    for x,y in zip(balance,[-334.8,124.1,-17.8,133.8,56.0,107.6,25.2]):quoted('ordinary budget balance (million gold marks)',x,y,tol=1e-9)
    quoted('December revenue (hundred million gold marks)',b.iloc[0].revenue_million_goldmark/100,3.3,tol=.05)
    quoted('December spending (hundred million gold marks)',b.iloc[0].expenditure_million_goldmark/100,6.7,tol=.05)
    quoted('December deficit (hundred million gold marks)',-balance.iloc[0]/100,3.3,tol=.05)
    n=notes();total=n.old_notes_million_newunit+n.new_rentenmarks_million
    for a,e in zip(total,[1545,2450,3014]):quoted('both issuers: million new-mark equivalent',a,e)
    quoted('March total (hundred million new marks)',total.iloc[1]/100,24.5)
    quoted('Austrian relief recipients, rounded',167000,170000,tol=3000)
    # Chinese quotations are translations, keyed to exact original snippets.
    text=TEX.read_text()
    translations={
        '盖房子，从屋顶盖起':'bt_lutherroof',
        '德国劳动每年能为本国的资本改良生产多少剩余，在理论上和实践上，都不是它每年能向国外缴纳多少贡赋的尺度。':'k19_investexport',
        '财政筹措问题取决于德国人民的财富与繁荣；转移问题取决于其产业在国际市场上的竞争地位。':'k29_wages',
        '地租银行一开始发行银行券，帝国银行就不得再贴现国库券。':'law_stop',
        '从屋顶盖起':'bt_lutherroof',
    }
    terms={'ALL RIGHTS RESERVED','消失','缺钱','已经征到税','已经付得出外汇','钱不够用','一夜平衡','每天翻倍','今天尚有缺口','以后每个缺口都由央行满足','货币数量增加'}
    for q in re.findall('“([^”]+)”',text):assert q in translations or q in terms,('unregistered quotation',q)
    for q,id in translations.items():assert q in text and id in f.index
    assert 'ALL RIGHTS RESERVED' in f.loc['bt_edition','quote']
    # Citation keys and cross references are checked globally by validate_source.py.
    anchors(TEX,f.index,script=Path(__file__))
    print('Chapter 26: all numerical examples, readings, translations and anchors passed.')

if __name__=='__main__':main()
