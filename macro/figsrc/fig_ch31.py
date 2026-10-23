"""Figures for Chapter 31 (苏联工业化与社会主义核算论战).

Style as in fig_ch30.py (docs/STYLE.md §7): direct labels in the colour of their series, no legends. Output is
OUTPUT, the state's grain procurement FISCAL, official figures MUTED; in the comparison of seven economies the USSR is
drawn thick in PRICE, Argentina and India (the two economies of Allen's counterfactual) dashed in EXTERNAL and MONEY,
and the four industrial economies thin in INSTIT, each with a direct label.
All numbers come from checks/check_ch31.py: the State Planning Commission's plan (1929) and its report (1933)
(plan_items()), Markevich, Naumenko and Qian's Table A.2 (grain()) and the Maddison Project Database (maddison()).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FixedLocator, NullLocator

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch31 as C
from style import (
    EXTERNAL,
    FIG_W,
    FISCAL,
    INSTIT,
    LIGHT,
    MONEY,
    MUTED,
    OUTPUT,
    PRICE,
    T,
    clean_axes,
    figure,
    halo,
    tint,
)

DOT = dict(marker="o", ms=3.2, mec="white", mew=0.5)


def _grid(ax, axis="y"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


ITEMS = {"gross": T("工业总产值", "industrial output"),
         "pig": T("生铁", "pig iron"),
         "steel": T("钢", "steel"),
         "coal": T("煤", "coal"),
         "oil": T("石油与天然气", "oil and gas")}


@figure("soviet_plan")
def soviet_plan():
    """Output of 1927/28 and of 1932 as per cent of the first five-year plan's target for 1932/33, five items."""
    rows = C.plan_items()
    assert [k for k, *_ in rows] == list(ITEMS)
    pct = [(k, 100 * a / c, 100 * b / c) for k, a, b, c in rows]
    assert max(p1 for k, _, p1 in pct if k != "oil") < 100 < dict((k, p1) for k, _, p1 in pct)["oil"]
    fig, ax = plt.subplots(figsize=(FIG_W, 2.75))
    fig.subplots_adjust(left=0.19, right=0.97, top=0.88, bottom=0.17)
    y = np.arange(len(pct))[::-1]
    h = 0.36
    for yi, (k, p0, p1) in zip(y, pct):
        ax.barh(yi + h / 2, p0, h, color=tint(OUTPUT, 0.55), zorder=4)
        ax.barh(yi - h / 2, p1, h, color=OUTPUT, zorder=4)
        s = f"{p1:.1f}" if k == "gross" else f"{p1:.0f}"
        if 85 < p1 < 100:                                       # inside the bar, clear of the line at 100
            ax.text(p1 - 1.2, yi - h / 2, s, color="white", fontsize=7.6, ha="right", va="center", weight="bold",
                    zorder=6)
        else:
            lab = ax.text(p1 + 1.2, yi - h / 2, s, color=OUTPUT, fontsize=7.6, ha="left", va="center", zorder=6)
            halo(lab, 2.0)
    ax.axvline(100, color=MUTED, lw=0.9, ls=(0, (4, 2)), zorder=5)
    lab = ax.text(98.8, len(pct) - 0.42, T("计划指标 = 100", "target = 100"), color=MUTED, fontsize=7.6,
                  ha="right", va="bottom")
    halo(lab, 2.0)
    # direct labels of the two bars, on the top item
    top = y[0]
    k0, p00, p01 = pct[0]
    lab = ax.text(p00 + 1.2, top + h / 2, T("1927/28 年度", "1927/28"), color=tint(OUTPUT, 0.8), fontsize=7.6,
                  ha="left", va="center", zorder=6)
    halo(lab, 2.0)
    ax.text(2, top - h / 2, T("1932 年", "1932"), color="white", fontsize=7.6, ha="left", va="center",
            weight="bold", zorder=6)
    ax.set_yticks(y)
    ax.set_yticklabels([ITEMS[k] for k, *_ in pct])
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 112)
    ax.set_ylim(-0.6, len(pct) - 0.2)
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.set_xlabel(T("产量，占 1932/33 年度计划指标的 %", "output, % of the target for 1932/33"))
    _grid(ax, axis="x")
    return fig


@figure("soviet_grain")
def soviet_grain():
    """The USSR's grain: official and revised harvests, Davies and Wheatcroft's range, and the state's procurement,
    1927-1933, 1937 and 1939, million tons."""
    G = C.grain()
    early = G.loc[1927:1933]
    late = G.loc[[1933, 1937, 1939]]
    fig, ax = plt.subplots(figsize=(FIG_W, 3.0))
    fig.subplots_adjust(left=0.085, right=0.86, top=0.97, bottom=0.15)
    dw = G.dropna(subset=["dw_min_mt"])
    ax.fill_between(dw.index, dw.dw_min_mt, dw.dw_max_mt, color=tint(OUTPUT, 0.22), lw=0, zorder=2)
    ax.plot(early.index, early.official_mt, color=MUTED, lw=1.2, ls=(0, (4, 2)), zorder=4, **DOT)
    ax.plot(late.index, late.official_mt, color=MUTED, lw=0.8, ls=(0, (1, 2)), zorder=3, **DOT)
    rev = G.revised_mt.dropna()
    ax.plot(rev.index, rev.values, color=OUTPUT, lw=1.9, zorder=5, **DOT)
    ax.plot(early.index, early.procurement_mt, color=FISCAL, lw=1.6, zorder=5, **DOT)
    ax.plot(late.index, late.procurement_mt, color=FISCAL, lw=0.8, ls=(0, (1, 2)), zorder=3, **DOT)
    assert G.revised_mt.idxmin() == 1932 and G.official_mt.idxmax() == 1937
    # direct labels
    lab = ax.text(1935.3, 97.0, T("官方公布的产量", "official harvest"), color=MUTED, fontsize=7.6, ha="center",
                  va="top")
    halo(lab, 2.0)
    lab = ax.text(1931.2, 47.0, T("修正的产量", "revised harvest"), color=OUTPUT, fontsize=7.8, ha="center",
                  va="top", weight="bold")
    halo(lab, 2.0)
    lab = ax.text(1933.35, 66.0, T("Davies 与 Wheatcroft\n的范围", "Davies and\nWheatcroft's range"),
                  color=tint(OUTPUT, 0.8), fontsize=7.6, ha="left", va="center", linespacing=1.05)
    halo(lab, 2.0)
    lab = ax.text(1937.0, G.loc[1937, "procurement_mt"] + 4, T("国家征购", "state procurement"), color=FISCAL,
                  fontsize=7.8, ha="center", va="bottom", weight="bold")
    halo(lab, 2.0)
    for yr, col, dy, va in ((1932, "revised_mt", -2.2, "top"), (1932, "procurement_mt", 2.2, "bottom"),
                            (1928, "procurement_mt", 2.2, "bottom")):
        c = OUTPUT if col == "revised_mt" else FISCAL
        lab = ax.text(yr, G.loc[yr, col] + dy, f"{G.loc[yr, col]:.1f}", color=c, fontsize=7.6, ha="center", va=va)
        halo(lab, 2.0)
    ax.set_xlim(1926.5, 1939.6)
    ax.set_ylim(0, 130)
    ax.set_xticks([1927, 1928, 1929, 1930, 1931, 1932, 1933, 1937, 1939])
    ax.set_xlabel(T("年份", "year"))
    ax.set_ylabel(T("百万吨", "million tons"))
    _grid(ax)
    return fig


# the seven economies: names, colour, line width, line style, the label's factor at 1940 (log axis)
GDP = {"SUN": (("苏联", "USSR"), PRICE, 2.2, "-", 1.0),
       "ARG": (("阿根廷", "Argentina"), EXTERNAL, 1.3, (0, (4, 2)), 1.0),
       "IND": (("印度", "India"), MONEY, 1.3, (0, (4, 2)), 1.0),
       "USA": (("美国", "US"), INSTIT, 0.9, "-", 1.07),
       "GBR": (("英国", "UK"), INSTIT, 0.9, "-", 0.94),
       "DEU": (("德国", "Germany"), INSTIT, 0.9, "-", 1.0),
       "JPN": (("日本", "Japan"), INSTIT, 0.9, "-", 1.0)}


@figure("soviet_gdp")
def soviet_gdp():
    """GDP per head, 2011 international dollars, log scale, 1913-1940: the USSR thick, Argentina and India dashed,
    the United States, the United Kingdom, Germany and Japan thin."""
    M = C.maddison()
    assert set(GDP) == set(C.SIX) == set(M.index)
    U = M.loc["SUN"]
    assert U.idxmin() == 1921
    fig, ax = plt.subplots(figsize=(FIG_W, 3.3))
    fig.subplots_adjust(left=0.12, right=0.86, top=0.97, bottom=0.14)
    yrs = np.array(M.columns)
    for k, (names, col, lw, ls, f) in GDP.items():
        ax.plot(yrs, M.loc[k].values, color=col, lw=lw, ls=ls, zorder=6 if k == "SUN" else 4)
        lab = ax.text(yrs[-1] + 0.4, M.loc[k, 1940] * f, T(*names), color=col, fontsize=7.6, ha="left", va="center",
                      weight="bold" if k == "SUN" else "normal")
        halo(lab, 2.0)
    for yr, dy, va in ((1921, 0.88, "top"), (1928, 0.88, "top"), (1940, 1.12, "bottom")):
        lab = ax.text(yr, U[yr] * dy, f"{U[yr]:,.0f}", color=PRICE, fontsize=7.6, ha="center", va=va)
        halo(lab, 2.0)
    ax.plot([1921, 1928, 1940], [U[1921], U[1928], U[1940]], ls="none", color=PRICE, zorder=7, **DOT)
    ax.set_yscale("log")
    ticks = [500, 1000, 2000, 4000, 8000, 16000]
    ax.yaxis.set_major_locator(FixedLocator(ticks))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.set_yticklabels([f"{t:,}" for t in ticks])
    ax.set_ylim(600, 17000)
    ax.set_xlim(1912.5, 1940.5)
    ax.set_xticks([1913, 1917, 1921, 1925, 1929, 1933, 1937, 1940])
    ax.set_xlabel(T("年份", "year"))
    ax.set_ylabel(T("人均 GDP（2011 年国际元）", "GDP per head (2011 int. dollars)"))
    _grid(ax)
    return fig
