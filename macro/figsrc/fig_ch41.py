"""Figures for Chapter 41 (发展经济学：二元经济、进口替代与大推进).

Style as in fig_ch40.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the colour
of their series, no legends. Output, profit and the saving rate are OUTPUT, employment and the wage INK, a third series
AMBER; reference lines MUTED. All numbers come from checks/check_ch41.py: the Lewis economy of ex:development-lewis
(lewis_diagram(), lewis_path(), turning_year()), Prebisch's Table 1 as read on the page image (terms()) and the GDP per
head of the Maddison Project Database 2023 (paths()).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch41 as C
from style import (
    AMBER,
    FIG_W,
    INK,
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

DOT = dict(marker="o", ms=4.6, mec="white", mew=0.6)


def _title(ax, s):
    ax.set_title(s, fontsize=9.0, weight="bold", loc="left", pad=4)


def _grid(ax, axis="both"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


def _text(ax, x, y, s, color, ha="left", va="center", weight="normal", size=7.6):
    lab = ax.text(x, y, s, color=color, fontsize=size, ha=ha, va=va, weight=weight, linespacing=1.3, zorder=8)
    halo(lab, 2.0)
    return lab


# ---------------------------------------------------------------------------------------------------
@figure("development_lewis")
def development_lewis():
    """ex:development-lewis. (a) Lewis's diagram: the marginal product of labour in the capitalist sector for the
    capital that employs 8, 16 and 24 workers at the wage 1.3; the profit is the area above the wage, left of the
    point where the curve meets it. (b) The saving rate and the capitalist sector's share of the labour force, year by
    year to the turning point."""
    D = C.lewis_diagram()
    P = C.lewis_path()
    Tp = C.turning_year()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.85))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.875, bottom=0.165, wspace=0.30)
    shown = D[D["L"] <= 40]
    last = f"mpl{C.LCMAX}"
    k = shown["L"] <= C.LCMAX
    a1.fill_between(shown["L"][k], C.WBAR, np.minimum(shown[last][k], 3.0), color=tint(OUTPUT, 0.78), lw=0, zorder=2)
    for lc, shade in ((C.LC0, 0.55), (2 * C.LC0, 0.3), (C.LCMAX, 0.0)):
        a1.plot(shown["L"], shown[f"mpl{lc}"], color=tint(OUTPUT, shade) if shade else OUTPUT, lw=1.8, zorder=5)
        a1.plot([lc], [C.WBAR], color=INK, zorder=7, **DOT)
        _text(a1, lc + 0.6, C.WBAR - 0.07, f"{lc}", INK, va="top")
    a1.axhline(C.WBAR, color=INK, lw=1.4, zorder=4)
    a1.axhline(C.SUBS, color=MUTED, lw=1.0, ls=(0, (4, 2)), zorder=3)
    a1.set_xlim(0, 40)
    a1.set_ylim(0, 3.0)
    a1.set_xticks([0, 8, 16, 24, 32, 40])
    a1.set_yticks([0, 1, 2, 3])
    a1.set_xlabel(T("资本主义部门雇用的人数", "workers in the capitalist sector"))
    a1.set_ylabel(T("劳动的边际产品与工资", "marginal product and wage"))
    _grid(a1)
    _text(a1, 39.5, C.WBAR + 0.06, T(f"工资 {C.WBAR}", f"wage {C.WBAR}"), INK, ha="right", va="bottom", weight="bold")
    _text(a1, 0.8, C.SUBS - 0.06, T("维持生计的收入 1", "subsistence income 1"), MUTED, ha="left", va="top")
    _text(a1, 4.8, 1.95, T("利润", "profit"), OUTPUT, ha="center", weight="bold")
    y_arrow = 1.45
    x0 = float(np.interp(-y_arrow, -shown[f"mpl{C.LC0}"], shown["L"]))
    x1 = float(np.interp(-y_arrow, -shown[last], shown["L"]))
    a1.annotate("", xy=(x1, y_arrow), xytext=(x0, y_arrow), zorder=8,
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.0, shrinkA=0, shrinkB=0))
    _text(a1, x1 + 0.6, y_arrow + 0.12, T("资本增加，曲线右移", "more capital"), INK, ha="left",
          va="bottom")
    _title(a1, T("(a) 积累使需求曲线右移，工资不动", "(a) Capital shifts demand out; the wage stays"))
    assert shown[f"mpl{C.LC0}"].iloc[-1] < C.SUBS < shown[last].iloc[-1] < C.WBAR

    a2.plot(P["year"], 100 * P["lc"] / C.LAB, color=INK, lw=1.8, zorder=5)
    a2.plot(P["year"], 100 * P["s"], color=OUTPUT, lw=2.0, zorder=6)
    a2.axvline(Tp, color=MUTED, lw=0.9, ls=(0, (3, 2)), zorder=3)
    for col, color in (("lc", INK), ("s", OUTPUT)):
        v0 = 100 * P[col].iloc[0] / (C.LAB if col == "lc" else 1)
        v1 = 100 * P[col].iloc[-1] / (C.LAB if col == "lc" else 1)
        a2.plot([0, Tp], [v0, v1], ls="none", color=color, zorder=7, **DOT)
        _text(a2, Tp + 0.25, v1, f"{v1:.1f}%" if col == "s" else f"{v1:.0f}%", color, va="center")
        _text(a2, 0.3, v0 + 1.0, f"{v0:.1f}%" if col == "s" else f"{v0:.0f}%", color, va="bottom")
    _text(a2, 5.3, 100 * P["lc"].iloc[53] / C.LAB + 1.2, T("就业份额", "employment share"), INK, ha="right",
          va="bottom", weight="bold")
    _text(a2, 6.0, 100 * P["s"].iloc[60] - 1.0, T("储蓄率", "saving rate"), OUTPUT, ha="left", va="top",
          weight="bold")
    _text(a2, Tp - 0.2, 28.5, T(f"转折点\n第 {Tp:.1f} 年", f"turning point\nyear {Tp:.1f}"), MUTED, ha="right", va="top")
    a2.set_xlim(0, 13)
    a2.set_ylim(0, 30)
    a2.set_xticks([0, 2, 4, 6, 8, 10, 12])
    a2.set_yticks([0, 10, 20, 30])
    a2.set_xlabel(T("年", "year"))
    a2.set_ylabel(T("占比（%）", "share (%)"))
    _grid(a2)
    _title(a2, T("(b) 储蓄率随资本主义部门上升", "(b) The saving rate rises"))
    assert np.isclose(P["s"].iloc[-1], C.lewis(C.LCMAX)["s"]) and 10 < Tp < 11
    return fig


# ---------------------------------------------------------------------------------------------------
@figure("development_terms")
def development_terms():
    """Prebisch (1950), Table 1: the ratio of the prices of primary commodities to those of manufactured goods
    (1876-80 = 100), each period at its midpoint; the lines are broken across the two wars."""
    D = C.terms()
    fig, ax = plt.subplots(figsize=(FIG_W, 2.6))
    fig.subplots_adjust(left=0.10, right=0.97, top=0.88, bottom=0.17)
    ax.axhline(100, color=MUTED, lw=0.8, ls=(0, (1, 2)), zorder=2)
    parts = [D[D["last"] <= 1913], D[(D["first"] > 1913) & (D["last"] <= 1938)], D[D["first"] > 1938]]
    for part in parts:
        ax.plot(part["mid"], part["ratio"], color=PRICE, lw=1.8, zorder=5)
        ax.plot(part["mid"], part["ratio"], ls="none", color=PRICE, zorder=6, **DOT)
    for period, ha, dy in (("1881-1885", "left", 2.2), ("1931-1935", "center", -2.6), ("1936-1938", "left", 2.2),
                           ("1946-1947", "center", 2.2), ("1921-1925", "center", -2.6)):
        r = D[D["period"] == period].iloc[0]
        x = r["mid"] + (0.6 if ha == "left" else 0)
        _text(ax, x, r["ratio"] + dy, f"{r['ratio']:.1f}", PRICE, ha=ha, va="bottom" if dy > 0 else "top")
    for x0, x1 in ((1913, 1921), (1938, 1946)):
        ax.axvspan(x0, x1, color=LIGHT, lw=0, zorder=1)
    _text(ax, 1917, 58, T("第一次\n世界大战", "First\nWorld War"), MUTED, ha="center")
    _text(ax, 1942, 58, T("第二次\n世界大战", "Second\nWorld War"), MUTED, ha="center")
    ax.set_xlim(1872, 1952)
    ax.set_ylim(52, 110)
    ax.set_xticks([1880, 1890, 1900, 1910, 1920, 1930, 1940, 1950])
    ax.set_yticks([60, 70, 80, 90, 100])
    ax.set_ylabel(T("1876—1880 年 = 100", "1876–80 = 100"))
    _grid(ax, "y")
    low = D.loc[D["ratio"].idxmin()]
    _title(ax, T(f"初级产品与工业品的价格之比：最低 {low['ratio']:.1f}（{low['first']}—{low['last']} 年）",
                 f"Primary to manufactured prices: lowest {low['ratio']:.1f} ({low['first']}–{low['last']})"))
    assert D["ratio"].between(55, 108).all() and D["mid"].between(1872, 1952).all()
    return fig


# ---------------------------------------------------------------------------------------------------
@figure("development_paths")
def development_paths():
    """The Maddison Project Database 2023: GDP per head, 1950-2022, 2011 international dollars, log scale. (a) Argentina,
    Brazil and Mexico. (b) India, Ghana and the Republic of Korea."""
    P = C.paths()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.9), sharey=True)
    fig.subplots_adjust(left=0.125, right=0.985, top=0.875, bottom=0.13, wspace=0.10)
    groups = ((a1, (("ARG", INK), ("BRA", OUTPUT), ("MEX", AMBER))),
              (a2, (("IND", AMBER), ("GHA", PRICE), ("KOR", MONEY))))
    names = {"ARG": T("阿根廷", "Argentina"), "BRA": T("巴西", "Brazil"), "MEX": T("墨西哥", "Mexico"),
             "IND": T("印度", "India"), "GHA": T("加纳", "Ghana"), "KOR": T("韩国", "Korea")}
    place = {"ARG": (1951, 11500, "left"), "MEX": (1951, 5600, "left"), "BRA": (1951, 1750, "left"),
             "IND": (2023, P.loc[2022, "IND"], "left"), "GHA": (2023, P.loc[2022, "GHA"], "left"),
             "KOR": (2023, P.loc[2022, "KOR"], "left")}
    for ax, series in groups:
        for code, color in series:
            ax.plot(P.index, P[code], color=color, lw=1.8, zorder=5)
            x, y, ha = place[code]
            _text(ax, x, y, names[code], color, ha=ha, weight="bold")
        ax.axvline(1980, color=MUTED, lw=0.8, ls=(0, (3, 2)), zorder=2)
        ax.set_yscale("log")
        ax.set_xlim(1950, 2022 if ax is a1 else 2033)
        ax.set_ylim(700, 50000)
        ax.set_xticks([1950, 1970, 1990, 2010])
        ax.set_yticks([1000, 3000, 10000, 30000])
        ax.set_yticklabels(["1,000", "3,000", "10,000", "30,000"])
        ax.minorticks_off()
        _grid(ax, "y")
    a1.set_ylabel(T("人均 GDP（2011 年国际元）", "GDP per head (2011 int. $)"), labelpad=2)
    _title(a1, T("(a) 拉美三国 1980 年以后停滞", "(a) Latin America stalled after 1980"))
    _title(a2, T("(b) 起点相近，此后分开", "(b) Similar starts, different paths"))
    assert P.min().min() > 700 and P.max().max() < 50000
    assert P.loc[1980, ["ARG", "BRA", "MEX"]].min() > P.loc[1950, ["ARG", "BRA", "MEX"]].max() / 2
    return fig
