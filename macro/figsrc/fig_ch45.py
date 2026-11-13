"""Figures for Chapter 45 (货币主义).

Style as in fig_ch44.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the colour
of their series, no legends. Money and its velocity are MONEY, the second aggregate (M2) and the interest-rate target
AMBER (in Poole's panel dashed with squares, the second series of STYLE.md §7.1), the misses of a target PRICE, targets
and reference lines MUTED. All numbers come from checks/check_ch45.py:
the American series of tables B-1 and B-67 (us()), Table 10 of Gerberding, Worms and Seitz (gwz()), Table 1 of Rich
(rich()) and Poole's variances with the teaching inputs of ex:monetarism-poole (poole_var(), POOLE).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch45 as C
from style import (
    AMBER,
    FIG_W,
    INK,
    LIGHT,
    MONEY,
    MUTED,
    PRICE,
    SHADE,
    T,
    clean_axes,
    figure,
    halo,
    tint,
)

DOT = dict(marker="o", ms=4.4, mec="white", mew=0.6)


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
@figure("monetarism_velocity")
def monetarism_velocity():
    """The velocity of M1 (a) and of M2 (b): GDP of the year over the December average of the money stock, 1959-1999,
    with vertical lines at 1979, 1982 and 1986 (C.VLINES)."""
    U = C.us()
    years = U.index.values
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(FIG_W, 4.5), sharex=True)
    fig.subplots_adjust(left=0.085, right=0.985, top=0.93, bottom=0.08, hspace=0.32)
    for ax in (a1, a2):
        _grid(ax, "y")
        for y in C.VLINES:
            ax.axvline(y, color=MUTED, lw=0.8, ls=(0, (3, 2)), zorder=2)
    a1.plot(years, U["v1"], color=MONEY, lw=1.6, zorder=4)
    a1.plot(years, U["v1"], ls="none", color=MONEY, zorder=5, marker="o", ms=2.6, mec="white", mew=0.4)
    for y in C.VLINES:
        _text(a1, y, 8.62, f"{y}", MUTED, ha="center", va="bottom", size=7.6)
    _text(a1, 1960, 5.75, T("1959—1981 年\n每年约升 3.2%", "1959-1981:\nabout +3.2% a year"), MONEY, weight="bold")
    a1.set_ylim(3, 9.2)
    a1.set_yticks([3, 4, 5, 6, 7, 8])
    a1.set_ylabel(T("GDP / M1", "GDP / M1"))
    _title(a1, T("(a) M1 的流通速度：1981 年以前一路上升，此后忽上忽下",
                 "(a) M1 velocity: a steady rise to 1981, then swings"))
    a2.plot(years, U["v2"], color=AMBER, lw=1.6, zorder=4)
    a2.plot(years, U["v2"], ls="none", color=AMBER, zorder=5, marker="o", ms=2.6, mec="white", mew=0.4)
    lo, hi = U["v2"].loc[1959:1990].min(), U["v2"].loc[1959:1990].max()
    a2.fill_between([1959, 1990], lo, hi, color=SHADE, alpha=0.6, lw=0, zorder=1)
    assert 1.5 < lo < hi < 1.8
    _text(a2, 1960, 1.93, T("1959—1990 年都在 1.55 到 1.78 之间", "1959-1990: between 1.55 and 1.78"), MUTED)
    assert round(lo, 2) == 1.55 and round(hi, 2) == 1.78
    a2.set_ylim(1.4, 2.15)
    a2.set_yticks([1.4, 1.6, 1.8, 2.0])
    a2.set_ylabel(T("GDP / M2", "GDP / M2"))
    a2.set_xlim(1958, 2000)
    a2.set_xticks(range(1960, 2000, 5))
    _title(a2, T("(b) M2 的流通速度：1990 年以前在窄的范围里，1990 年代上升",
                 "(b) M2 velocity: a narrow band until 1990, higher in the 1990s"))
    return fig


@figure("monetarism_targets")
def monetarism_targets():
    """(a) The Bundesbank's target ranges 1979-1998 (bars; the point target of 1989 a short bar) and the actual growth
    (dots; the seven misses PRICE). (b) The SNB's annual targets 1975-1990 (squares) and outcomes (dots); no target in
    1979."""
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(FIG_W, 4.6))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.94, bottom=0.07, hspace=0.42)
    _grid(a1, "y")
    miss = C.misses()
    for y in range(1979, 1999):
        g = C.gwz(y)
        h = g["hi"] - g["lo"]
        a1.bar(y, h if h > 0 else 0.18, bottom=g["lo"] if h > 0 else g["lo"] - 0.09, width=0.62,
               color=tint(MUTED, 0.45), edgecolor="none", zorder=2)
        a1.plot(y, g["actual"], ls="none", color=PRICE if y in miss else MONEY, zorder=5, **DOT)
    assert len(miss) == 7
    _text(a1, 1984.6, 9.0, T("落空 7 次，6 次偏高", "missed 7 times, 6 above"), PRICE, weight="bold")
    _text(a1, 1979.0, 9.6, T("灰条：目标区间", "grey bars: target range"), MUTED)
    _text(a1, 1989, 3.9, T("点目标", "point\ntarget"), MUTED, ha="center", va="top", size=7.6)
    a1.set_xlim(1978.3, 1998.7)
    a1.set_xticks(range(1980, 1999, 2))
    a1.set_ylim(0, 10.5)
    a1.set_yticks([0, 2, 4, 6, 8, 10])
    a1.set_ylabel(T("增长率（%）", "growth (%)"))
    _title(a1, T("(a) 联邦银行：20 年里目标落空 7 次", "(a) Bundesbank: 7 misses in 20 years"))
    _grid(a2, "y")
    a2.axhline(0, color=MUTED, lw=0.7, zorder=2)
    ys = C.RICH_YEARS
    a2.plot(ys, [C.rich(y)["target"] for y in ys], ls="none", marker="s", ms=5.0, mfc="white", mec=INK, mew=1.0,
            zorder=4)
    a2.plot(ys, [C.rich(y)["outcome"] for y in ys], ls="none", color=MONEY, zorder=5, **DOT)
    _text(a2, 1979, 1.2, T("无目标", "no\ntarget"), MUTED, ha="center", va="bottom", size=7.6)
    r78 = C.rich(1978)
    _text(a2, 1977.6, r78["outcome"], T("1978 年：16.2%", "1978: 16.2%"), MONEY, ha="right")
    assert r78["outcome"] == 16.2
    _text(a2, 1980.4, 12.0, T("方块：目标　圆点：实际", "squares: target   dots: outcome"), INK)
    _text(a2, 1987.7, -4.2, T("1988 年：新的支付系统", "1988: new payment system"), MONEY, ha="right", size=7.6)
    a2.set_xlim(1974.3, 1990.7)
    a2.set_xticks(range(1975, 1991, 3))
    a2.set_ylim(-6, 18)
    a2.set_yticks([-5, 0, 5, 10, 15])
    a2.set_ylabel(T("增长率（%）", "growth (%)"))
    _title(a2, T("(b) 瑞士国家银行：1978 年转盯汇率，1979 年没有目标", "(b) SNB: the exchange rate first in 1978, no target in 1979"))
    return fig


@figure("monetarism_poole")
def monetarism_poole():
    """The variance of output under the two instruments against the variance of the monetary disturbance, with the
    teaching inputs of ex:monetarism-poole: flat at the real disturbance's variance under the rate target, rising
    under the money target, crossing at C.threshold() = 2."""
    P = C.POOLE
    a1, b1, b2, su = P["a1"], P["b1"], P["b2"], P["su"]
    s = C.threshold(a1, b1, b2, su)
    assert s == 2
    x = np.linspace(0, 5, 101)
    ym = np.array([C.poole_var(a1, b1, b2, su, v) for v in x])
    fig, ax = plt.subplots(figsize=(FIG_W, 2.9))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.89, bottom=0.16)
    _grid(ax)
    ax.axvspan(0, s, color=tint(MONEY, 0.08), lw=0, zorder=1)
    ax.axvspan(s, 5, color=tint(AMBER, 0.07), lw=0, zorder=1)
    # the second series of the panel: AMBER, dashed, squares (STYLE.md §7.1)
    ax.plot(x, np.full_like(x, su), color=AMBER, lw=1.8, dashes=(4, 2), zorder=4)
    ax.plot([0.5, 1.5, 2.5, 3.5, 4.5], [su] * 5, ls="none", marker="s", ms=5.0, color=AMBER, mec="white", mew=0.6,
            zorder=5)
    ax.plot(x, ym, color=MONEY, lw=1.8, zorder=4)
    ax.axvline(s, color=MUTED, lw=0.8, ls=(0, (3, 2)), zorder=3)
    for v in (*P["sv"], s):
        ax.plot(v, C.poole_var(a1, b1, b2, su, v), ls="none", color=MONEY if v != s else INK, zorder=6, **DOT)
    _text(ax, 1.0, C.poole_var(a1, b1, b2, su, 1.0) - 0.16, "0.56", MONEY, ha="center")
    _text(ax, 4.0, C.poole_var(a1, b1, b2, su, 4.0) + 0.17, "1.89", MONEY, ha="center")
    _text(ax, 3.35, 1.85, T("盯货币", "money target"), MONEY, ha="right", weight="bold")
    _text(ax, 4.95, su - 0.17, T("盯利率", "rate target"), AMBER, ha="right", weight="bold")
    _text(ax, 0.1, 2.05, T("盯货币更稳", "money target\nsteadier"), MONEY)
    _text(ax, s + 0.1, 0.3, T("盯利率更稳", "rate target steadier"), AMBER)
    ax.set_xlim(0, 5)
    ax.set_ylim(0, 2.5)
    ax.set_xticks([0, 1, 2, 3, 4, 5])
    ax.set_yticks([0, 0.5, 1, 1.5, 2, 2.5])
    ax.set_xlabel(T("货币扰动的方差", "variance of the monetary disturbance"))
    ax.set_ylabel(T("产出的方差", "variance of output"))
    _title(ax, T("货币扰动越大，盯利率越好", "The larger the monetary disturbance, the better the rate target"))
    return fig
