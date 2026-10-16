"""Figures for Chapter 25 (维克塞尔与费雪：自然利率与实际利率).

Style as in fig_ch23.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series, the second series in AMBER and dashed. Interest rates are MONEY, prices PRICE; a second axis
on the right is drawn in the colour of its series. All numbers come from checks/check_ch25.py: the teaching model of
eq:wicksell-process (cumulative, natural_cycle), the Bank of England's consol yield and wholesale prices (gibson) and
the Swedish series of Edvinsson and Soederberg and of Waldenstroem (sweden, sweden_monthly).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FixedLocator, NullLocator

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch25 as C  # noqa: E402
from style import AMBER, FIG_W, INK, LIGHT, MONEY, MUTED, PRICE, T, clean_axes, figure, halo, tint  # noqa: E402

PALE = tint(MONEY, 0.5)


def _title(ax, s):
    ax.set_title(s, fontsize=9.0, weight="bold", loc="left", pad=4)


def _grid(ax, axis="y"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


def _dashed(ax, x, y, color=AMBER, lw=1.6, **kw):
    line, = ax.plot(x, y, color=color, lw=lw, zorder=3, **kw)
    line.set_dashes((4, 2))
    return line


def _right_axis(ax, color):
    """A second y axis on the right, in the colour of its series."""
    ax2 = ax.twinx()
    ax2.spines[["top", "left"]].set_visible(False)
    ax2.spines["right"].set_color(color)
    ax2.tick_params(axis="y", colors=color, length=3, width=0.7)
    ax.spines["right"].set_visible(False)
    return ax2


def _signed(x: float) -> str:
    """Two decimals with a true minus sign."""
    return f"{x:.2f}".replace("-", "\u2212")


def _log_ticks(ax, ticks, lim):
    ax.set_yscale("log")
    ax.yaxis.set_major_locator(FixedLocator(ticks))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.set_yticklabels([f"{t:g}" for t in ticks])
    ax.set_ylim(*lim)


@figure("wicksell_model")
def wicksell_model():
    """eq:wicksell-process. (a) the price level when the bank keeps its rate at 4% below a natural rate of 5% (beta = 0)
    and when it raises the rate with the prices (beta = 0.1); (b) a natural rate that swings between 5% and 6%: the
    market rate follows it with a lag, and the price level moves with the market rate."""
    m = C.MODEL
    years = 40
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.8))
    fig.subplots_adjust(left=0.085, right=0.915, top=0.86, bottom=0.16, wspace=0.42)

    t = np.arange(years + 1)
    _, p0, _ = C.cumulative(np.full(years, m["rn"]), m["i0"], m["kappa"], 0.0)
    _, p1, _ = C.cumulative(np.full(years, m["rn"]), m["i0"], m["kappa"], m["beta"])
    P0, P1 = 100 * np.exp(p0 / 100), 100 * np.exp(p1 / 100)
    a1.plot(t, P1, color=PRICE, lw=2.0, zorder=4)
    _dashed(a1, t, P0)
    a1.axhline(100, color=MUTED, lw=0.6, ls=(0, (1, 2)), zorder=2)
    lab = a1.text(3, 205, T("银行不动利率（$\\beta=0$）", "rate kept at 4% ($\\beta=0$)"), fontsize=7.8,
                  color=AMBER, ha="left", va="bottom")
    halo(lab, 2.0)
    lab = a1.text(39, P1[-1] + 6, T("银行跟着物价提高利率\n（$\\beta=0.1$）", "rate raised\nwith prices ($\\beta=0.1$)"),
                  fontsize=7.8, color=PRICE, ha="right", va="bottom", linespacing=1.3)
    halo(lab, 2.0)
    a1.annotate(f"{P1[-1]:.1f}", (years, P1[-1]), xytext=(years - 2.5, P1[-1] - 13), fontsize=7.6, color=PRICE,
                ha="center", va="top", arrowprops=dict(arrowstyle="-", lw=0.6, color=PRICE))
    a1.annotate(f"{P0[-1]:.0f}", (years, P0[-1]), xytext=(years - 4.5, P0[-1] + 2), fontsize=7.6, color=AMBER,
                ha="right", va="center", arrowprops=dict(arrowstyle="-", lw=0.6, color=AMBER))
    a1.set_xlim(0, years + 0.5)
    a1.set_ylim(90, 240)
    a1.set_xticks([0, 10, 20, 30, 40])
    a1.set_xlabel(T("年", "year"))
    a1.set_ylabel(T("物价水平（第 0 年 = 100）", "price level (year 0 = 100)"))
    _grid(a1)
    _title(a1, T("(a) 利差不消失，物价就一直涨", "(a) Prices rise while the gap lasts"))

    r = C.natural_cycle()
    i, p, _ = C.cumulative(r, C.CYCLE["low"], m["kappa"], m["beta"])
    T_ = C.CYCLE["T"]
    x = np.arange(T_)
    line, = a2.plot(x, r, color=PALE, lw=1.4, zorder=3)
    line.set_dashes((1, 1.3))
    a2.plot(x, i[:T_], color=MONEY, lw=2.0, zorder=4)
    a2.set_xlim(0, T_)
    a2.set_ylim(4.6, 6.8)
    a2.set_xticks([0, 40, 80, 120])
    a2.set_xlabel(T("年", "year"))
    a2.set_ylabel(T("利率（%）", "interest rate (%)"))
    _grid(a2)
    b = _right_axis(a2, PRICE)
    _dashed(b, x, 100 * np.exp(p[:T_] / 100), color=PRICE, lw=1.5)
    b.set_ylim(97, 119)
    b.set_yticks([100, 105, 110, 115])
    b.set_ylabel(T("物价水平（第 0 年 = 100）", "price level (year 0 = 100)"), color=PRICE)
    k = int(np.argmax(r[:40]))
    lab = a2.text(k, r[k] + 0.07, T("自然利率", "natural rate"), fontsize=7.8, color=tint(MONEY, 0.7), ha="center",
                  va="bottom")
    halo(lab, 2.0)
    lab = a2.annotate(T("市场利率", "market rate"), (67, i[67]), xytext=(73, 6.35), fontsize=7.8, color=MONEY,
                      ha="left", va="center", arrowprops=dict(arrowstyle="-", lw=0.6, color=MONEY))
    halo(lab, 2.0)
    P = 100 * np.exp(p / 100)
    lab = b.annotate(T("物价水平", "price level"), (49, P[49]), xytext=(56, 98.3), fontsize=7.8, color=PRICE,
                     ha="left", va="center", arrowprops=dict(arrowstyle="-", lw=0.6, color=PRICE))
    halo(lab, 2.0)
    _title(a2, T("(b) 利率与物价一起涨落", "(b) Rates and prices move together"))
    return fig


@figure("wicksell_gibson")
def wicksell_gibson():
    """Gibson's paradox, UK 1821-1913: (a) the consol yield and the wholesale price index (1913 = 100, log, right
    axis); (b) the yield against the inflation of the same year."""
    G = C.gibson()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.8), gridspec_kw=dict(width_ratios=[1.35, 1.0]))
    fig.subplots_adjust(left=0.075, right=0.985, top=0.86, bottom=0.16, wspace=0.5)

    y = G.consol_yield
    a1.plot(G.index, y, color=MONEY, lw=1.8, zorder=4)
    a1.set_xlim(1821, 1913)
    a1.set_ylim(2.0, 4.6)
    a1.set_xticks([1830, 1850, 1870, 1890, 1910])
    a1.set_ylabel(T("统一公债收益率（%）", "consol yield (%)"))
    _grid(a1)
    b = _right_axis(a1, PRICE)
    w = 100 * G.uk_wholesale_2010_100 / G.uk_wholesale_2010_100[1913]
    _dashed(b, G.index, w, color=PRICE, lw=1.4)
    _log_ticks(b, [60, 80, 100, 120, 150], (52, 175))
    b.set_ylabel(T("批发物价（1913 年 = 100，对数）", "wholesale prices (1913 = 100, log)"), color=PRICE)
    lab = a1.text(1838, 4.38, T("公债收益率", "consol yield"), fontsize=7.8, color=MONEY, ha="center", va="center")
    halo(lab, 2.0)
    lab = b.text(1884, 135, T("批发物价", "wholesale prices"), fontsize=7.8, color=PRICE, ha="center", va="center")
    halo(lab, 2.0)
    r = C.corr(G.lnP, y)
    lab = a1.text(1893, 2.2, T(f"相关系数 {_signed(r)}", f"correlation {_signed(r)}"), fontsize=7.8, color=INK, ha="center",
                  va="center")
    halo(lab, 2.0)
    _title(a1, T("(a) 收益率与物价水平一起起落", "(a) The yield moves with the price level"))

    d = pd.concat([G.infl, y], axis=1).dropna()
    a2.scatter(d.infl, d.consol_yield, s=11, color=MONEY, ec="white", lw=0.3, zorder=4)
    a2.axvline(0, color=MUTED, lw=0.6, ls=(0, (1, 2)), zorder=2)
    a2.set_xlim(-22, 22)
    a2.set_ylim(2.0, 4.6)
    a2.set_xticks([-20, -10, 0, 10, 20])
    a2.set_xlabel(T("批发物价当年的涨幅（%）", "wholesale inflation (%)"))
    a2.set_ylabel(T("统一公债收益率（%）", "consol yield (%)"))
    _grid(a2)
    r = C.corr(G.infl, y)
    lab = a2.text(20, 4.42, T(f"相关系数 {_signed(r)}", f"correlation {_signed(r)}"), fontsize=7.8, color=INK, ha="right",
                  va="center")
    halo(lab, 2.0)
    _title(a2, T("(b) 与通胀率几乎无关", "(b) Not with inflation"))
    return fig


@figure("wicksell_sweden")
def wicksell_sweden():
    """Sweden on gold, 1874-1913: (a) the CPI (1914 = 100, log); (b) the monthly long-term bond yield and the
    Riksbank's discount rate."""
    S, M = C.sweden(), C.sweden_monthly()
    a0, a9 = C.SWEDEN
    cpi = S.cpi_1914_100.loc[a0:a9]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.8))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.86, bottom=0.16, wspace=0.3)

    a1.plot(cpi.index, cpi.values, color=PRICE, lw=2.0, zorder=4)
    low = int(cpi.idxmin())
    a1.plot([low], [cpi[low]], "o", ms=4.5, color=PRICE, mec="white", mew=0.5, zorder=5)
    lab = a1.annotate(T(f"{low} 年 {cpi[low]:.1f}", f"{low}: {cpi[low]:.1f}"), (low, cpi[low]),
                      xytext=(low + 2, cpi[low] * 0.93), fontsize=7.6, color=PRICE, ha="left", va="top",
                      arrowprops=dict(arrowstyle="-", lw=0.6, color=PRICE))
    halo(lab, 2.0)
    for yr, ha in ((a0, "left"), (a9, "center")):
        lab = a1.text(yr, cpi[yr] * 1.03, f"{cpi[yr]:.1f}", fontsize=7.6, color=PRICE, ha=ha, va="bottom")
        halo(lab, 2.0)
    a1.set_xlim(a0 - 1, a9 + 1.5)
    _log_ticks(a1, [60, 70, 80, 90, 100], (58, 110))
    a1.set_xticks([1875, 1885, 1895, 1905])
    a1.set_ylabel(T("消费物价（1914 年 = 100，对数）", "CPI (1914 = 100, log)"))
    _grid(a1)
    _title(a1, T(f"(a) 物价 {low} 年见底", f"(a) Prices bottom out in {low}"))

    m = M.loc[f"{a0}-01":f"{a9}-12"]
    x = pd.to_datetime(m.index + "-15")
    xs = x.year + (x.dayofyear - 1) / 365.25
    a2.plot(xs, m.bond_yield, color=MONEY, lw=1.6, zorder=4)
    line, = a2.step(xs, m.discount_rate, where="post", color=AMBER, lw=1.3, zorder=3)
    line.set_dashes((4, 2))
    by = m.bond_yield.dropna()
    k = by.idxmin()
    kx = xs[list(m.index).index(k)]
    a2.plot([kx], [by.min()], "o", ms=4.5, color=MONEY, mec="white", mew=0.5, zorder=5)
    yr, mo = k.split("-")
    lab = a2.annotate(T(f"{yr} 年 {int(mo)} 月 {by.min():.2f}%", f"{yr}-{mo}: {by.min():.2f}%"), (kx, by.min()),
                      xytext=(kx - 1.5, 2.75), fontsize=7.6, color=MONEY, ha="center", va="center",
                      arrowprops=dict(arrowstyle="-", lw=0.6, color=MONEY))
    halo(lab, 2.0)
    lab = a2.text(1875, 3.3, T("长期国债收益率", "bond yield"), fontsize=7.8, color=MONEY, ha="left", va="top")
    halo(lab, 2.0)
    lab = a2.text(1903.5, 6.5, T("贴现率", "discount rate"), fontsize=7.8, color=AMBER, ha="center", va="bottom")
    halo(lab, 2.0)
    a2.set_xlim(a0, a9 + 1)
    a2.set_ylim(2.4, 7.6)
    a2.set_xticks([1875, 1885, 1895, 1905])
    a2.set_ylabel(T("利率（%）", "interest rate (%)"))
    _grid(a2)
    _title(a2, T(f"(b) 长期利率晚 {int(yr) - low} 年才见底", f"(b) Yields bottom out {int(yr) - low} years later"))
    return fig
