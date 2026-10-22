"""Figures for Chapter 28 (大萧条：美国).

Style as in fig_ch27.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series. Real GDP and unemployment are OUTPUT, the consumer price index PRICE (the GDP deflator, the
second price series, AMBER, dashed), the banks INSTIT (the years 1930-1933 in full colour, the others tinted). All
numbers come from checks/check_ch28.py: BEA's NIPA snapshot of Chapter 2 (output_index()) and the annual snapshot
read from Historical Statistics (1975) and the Federal Reserve Bulletin (annual(), cpi_years()).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch28 as C
from style import (
    AMBER,
    FIG_W,
    INSTIT,
    LIGHT,
    MUTED,
    OUTPUT,
    PRICE,
    ZH,
    T,
    clean_axes,
    figure,
    halo,
    tint,
)

PANIC = range(1930, 1934)          # the four years of the banking panics


def _title(ax, s):
    ax.set_title(s, fontsize=9.0, weight="bold", loc="left", pad=4)


def _grid(ax, axis="y"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


@figure("depressionus_output")
def depressionus_output():
    """(a) Real GDP, the GDP deflator and the CPI, 1929 = 100, 1929-1941 (the CPI to 1936); (b) the unemployment rate,
    per cent of the civilian labour force, 1929-1941."""
    X, A = C.output_index(), C.annual()
    yrs = list(X.index)
    assert yrs == list(range(1929, 1942))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.85))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.86, bottom=0.15, wspace=0.27)

    cy = C.cpi_years()
    a1.plot(yrs, X.real.values, color=OUTPUT, lw=1.8, zorder=4)
    a1.plot(yrs, X.deflator.values, color=AMBER, lw=1.6, dashes=(4, 2), zorder=4)
    a1.plot(cy, X.cpi.loc[cy].values, color=PRICE, lw=1.6, zorder=5)
    a1.axhline(100, color=MUTED, lw=0.6, ls=(0, (1, 2)), zorder=2)
    for k in ("real", "deflator", "cpi"):
        fall = 1 - X[k][1933] / 100
        assert 0.2 < fall < 0.3                                  # 1929-1933: each fell by about a quarter
        assert X[k][1933] == X[k].loc[1929:1936].min()            # 1933 the low of each
    assert X.real[1936] > 100 > X.deflator[1936]                 # output back by 1936, prices not
    a1.set_xlim(1928.6, 1941.5)
    a1.set_ylim(60, 150)
    a1.set_xticks([1929, 1933, 1937, 1941])
    a1.set_ylabel(T("1929 年 = 100", "1929 = 100"))
    _grid(a1)
    lab = a1.text(1940.3, 134, T("实际 GDP", "real GDP"), color=OUTPUT, fontsize=7.8, ha="right", va="bottom")
    halo(lab, 2.0)
    lab = a1.text(1938.6, 77.5, T("GDP 平减指数", "GDP deflator"), color=AMBER, fontsize=7.8, ha="center", va="top")
    halo(lab, 2.0)
    lab = a1.text(1930.2, 101.5, T("消费物价", "consumer prices"), color=PRICE, fontsize=7.8, ha="left",
                  va="bottom")
    halo(lab, 2.0)
    _title(a1, T("(a) 产量与物价都降了约四分之一", "(a) Output and prices fell by a quarter"))

    u = A.unemployment_pct.loc[1929:1941]
    assert u.idxmax() == 1933 and 24 < u[1933] < 26              # one worker in four
    assert u[1938] > u[1937]                                     # the recession of 1937-38
    a2.plot(u.index, u.values, color=OUTPUT, lw=1.8, marker="o", ms=3.2, mec="white", mew=0.5, zorder=4)
    for y, dx, dy, ha in ((1929, 0.35, -0.3, "left"), (1933, 0.0, 1.2, "center"), (1937, 0.0, -1.4, "center"),
                          (1941, 0.0, -1.4, "center")):
        lab = a2.text(y + dx, u[y] + dy, f"{u[y]:.1f}%", color=OUTPUT, fontsize=7.6, ha=ha,
                      va="bottom" if dy > 0 else "top")
        halo(lab, 2.0)
    a2.set_xlim(1928.4, 1941.6)
    a2.set_ylim(0, 29)
    a2.set_xticks([1929, 1933, 1937, 1941])
    a2.set_ylabel(T("失业率（%）", "unemployment (%)"))
    _grid(a2)
    _title(a2, T("(b) 1933 年，四个工人里一个失业", "(b) 1933: one worker in four out of work"))
    for ax in (a1, a2):
        ax.set_xlabel(T("年份", "year"))
    return fig


@figure("depressionus_banks")
def depressionus_banks():
    """(a) Bank suspensions per year, 1921-1936 (mutual savings banks excluded); (b) the deposits of the suspended
    banks, hundred million dollars."""
    A = C.annual().loc[1921:1936]
    yrs = np.array(A.index)
    n = A.susp_banks.values
    unit = 1e5 if ZH else 1e6                                   # thousands of dollars -> 亿美元 or $ billion
    dep = A.susp_deposits_thousands.values / unit
    colours = [INSTIT if y in PANIC else tint(INSTIT, 0.45) for y in yrs]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.8))
    fig.subplots_adjust(left=0.105, right=0.985, top=0.86, bottom=0.15, wspace=0.30)

    s = A.susp_banks
    assert s.idxmax() == 1933 and s[1933] == 4000
    assert 300 < s.loc[1921:1929].min() and s.loc[1921:1929].max() < 1000     # hundreds a year in the 1920s
    a1.bar(yrs, n, 0.72, color=colours, lw=0, zorder=3)
    for y in (1931, 1933):
        a1.text(y, s[y] + 60, f"{s[y]:,.0f}", ha="center", va="bottom", color=INSTIT, fontsize=7.6)
    a1.set_xlim(1920.3, 1936.7)
    a1.set_ylim(0, 4500)
    a1.set_xticks([1921, 1925, 1929, 1933])
    a1.set_ylabel(T("停业银行（家）", "suspended banks"))
    _grid(a1)
    _title(a1, T("(a) 1933 年停业 4,000 家", "(a) 4,000 suspensions in 1933"))

    d = A.susp_deposits_thousands
    share = d.loc[1930:1933].sum() / d.sum()
    assert 0.78 < share < 0.82                                  # four-fifths of the deposits in 1930-1933
    a2.bar(yrs, dep, 0.72, color=colours, lw=0, zorder=3)
    for y in (1931, 1933):
        lab = f"{d[y] / unit:.1f}" if ZH else f"{d[y] / unit:.2f}"
        a2.text(y, d[y] / unit + 4e4 / unit, lab, ha="center", va="bottom", color=INSTIT, fontsize=7.6)
    a2.set_xlim(1920.3, 1936.7)
    a2.set_ylim(0, 4e6 / unit)
    a2.set_xticks([1921, 1925, 1929, 1933])
    a2.set_ylabel(T("存款（亿美元）", "deposits ($ billion)"))
    _grid(a2)
    _title(a2, T("(b) 存款的八成在 1930—1933 年", "(b) 1930-33: 80% of the deposits"))
    for ax in (a1, a2):
        ax.set_xlabel(T("年份", "year"))
    return fig
