"""Figures for Chapter 43 (成熟的计划经济：苏联、东欧、毛泽东时期的中国与南斯拉夫).

Style as in fig_ch42.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the colour
of their series, no legends where labels fit; the famine years 1959-1961 shaded. Births and output OUTPUT, deaths and
the procurement share PRICE, procurement MONEY; reference marks MUTED. All numbers come from checks/check_ch43.py: the
official vital rates of table A-1 of the 1999 compilation (vital()) and table A8 of Meng, Qian and Yared (2010), from
Li and Yang (2005) (grain()).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch43 as C
from style import (
    FIG_W,
    LIGHT,
    MONEY,
    MUTED,
    OUTPUT,
    PRICE,
    SHADE,
    T,
    clean_axes,
    figure,
    halo,
)

FAMINE = (1959, 1961)


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


def _famine(ax):
    ax.axvspan(FAMINE[0] - 0.5, FAMINE[1] + 0.5, color=SHADE, lw=0, zorder=1)


# ---------------------------------------------------------------------------------------------------
@figure("planned_vital")
def planned_vital():
    """Table A-1 of the 1999 compilation: the official crude birth and death rates, 1949-1970 (per thousand)."""
    V = C.vital().set_index("year")
    fig, ax = plt.subplots(figsize=(FIG_W, 2.8))
    fig.subplots_adjust(left=0.09, right=0.98, top=0.96, bottom=0.13)
    _famine(ax)
    ax.plot(V.index, V["cbr"], color=OUTPUT, lw=1.9, marker="o", ms=2.8, zorder=5)
    ax.plot(V.index, V["cdr"], color=PRICE, lw=1.9, marker="o", ms=2.8, zorder=5)
    ax.set_xlim(1948.5, 1970.5)
    ax.set_ylim(0, 48)
    ax.set_xticks([1949, 1952, 1955, 1958, 1961, 1964, 1967, 1970])
    ax.set_ylabel(T("每千人", "per thousand"), labelpad=2)
    _grid(ax, "y")
    _text(ax, 1949.2, 40.5, T("出生率", "birth rate"), OUTPUT, weight="bold")
    _text(ax, 1949.2, 22.0, T("死亡率", "death rate"), PRICE, weight="bold")
    _text(ax, 1960, 46.0, T("1959—1961 年", "1959–1961"), MUTED, ha="center")
    d60, b61 = V.loc[1960, "cdr"], V.loc[1961, "cbr"]
    ax.annotate(T(f"1960 年死亡率 {d60:.1f}", f"1960 death rate {d60:.1f}"), xy=(1960, d60), xytext=(1962.2, 30.5),
                color=PRICE, fontsize=7.6, arrowprops=dict(arrowstyle="-", color=PRICE, lw=0.6), zorder=8)
    ax.annotate(T(f"1961 年出生率 {b61:.1f}", f"1961 birth rate {b61:.1f}"), xy=(1961, b61), xytext=(1962.2, 15.0),
                color=OUTPUT, fontsize=7.6, arrowprops=dict(arrowstyle="-", color=OUTPUT, lw=0.6), zorder=8)
    assert V["cdr"].idxmax() == 1960 and V["cbr"].idxmin() == 1961
    assert V["cbr"].max() < 46 and V["cdr"].min() > 0
    return fig


@figure("planned_grain")
def planned_grain():
    """Table A8 of Meng, Qian and Yared (2010), from Li and Yang (2005): (a) grain production and state procurement,
    1952-1976 (million tonnes); (b) procurement as a share of production (per cent)."""
    A = C.grain().set_index("year")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.9))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.86, bottom=0.12, wspace=0.30)
    for ax in (a1, a2):
        _famine(ax)
        ax.set_xlim(1951.5, 1976.5)
        ax.set_xticks([1952, 1958, 1964, 1970, 1976])
        _grid(ax, "y")
    a1.plot(A.index, A["production"], color=OUTPUT, lw=1.9, zorder=5)
    a1.plot(A.index, A["procurement"], color=MONEY, lw=1.9, zorder=5)
    a1.set_ylim(0, 320)
    a1.set_ylabel(T("百万吨", "million tonnes"), labelpad=2)
    _text(a1, 1952.6, 226, T("产量", "production"), OUTPUT, weight="bold")
    _text(a1, 1966.5, 72, T("征购量", "procurement"), MONEY, weight="bold")
    for y in (1958, 1959):
        a1.plot(y, A.loc[y, "procurement"], marker="o", ms=3.6, color=MONEY, mec="white", mew=0.5, zorder=6)
    _text(a1, 1953.0, 100, T(f"1958 年 {A.loc[1958, 'procurement']:.0f}，1959 年 {A.loc[1959, 'procurement']:.0f}",
                             f"1958: {A.loc[1958, 'procurement']:.0f}; 1959: {A.loc[1959, 'procurement']:.0f}"),
          MONEY)
    _title(a1, T("(a) 1959 年减产，征购反而增加", "(a) Output fell, procurement rose"))
    a2.plot(A.index, A["share"], color=PRICE, lw=1.9, zorder=5)
    a2.set_ylim(0, 42)
    a2.set_ylabel(T("占产量的 %", "% of production"), labelpad=2)
    s59 = A.loc[1959, "share"]
    a2.plot(1959, s59, marker="o", ms=4.2, color=PRICE, mec="white", mew=0.6, zorder=6)
    _text(a2, 1960.6, s59 + 0.6, T(f"1959 年 {s59:.2f}%", f"1959: {s59:.2f}%"), PRICE)
    _title(a2, T("(b) 征购的比例 1959 年最高", "(b) The share peaked in 1959"))
    assert A.loc[1959, "production"] < A.loc[1958, "production"]
    assert A.loc[1959, "procurement"] > A.loc[1958, "procurement"]               # panel (a)'s title
    assert A["share"].idxmax() == 1959                                           # panel (b)'s title
    assert A["production"].max() < 320 and A["share"].max() < 42
    return fig
