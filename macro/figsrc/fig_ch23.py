"""Figures for Chapter 23 (金本位、挤兑与最后贷款人).

Style as in fig_ch22.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series, the second series in AMBER and dashed, a third series of the same quantity in a tint of the
first. Reserves and interest rates are MONEY, prices PRICE. All numbers come from checks/check_ch23.py, which reads
the Bank of England's weekly returns (sheets W1 and W2), Bank Rate (sheet D1), the price indices (sheet A47) and
goldstandard_facts (Bloomfield's shares, as Dutton gives them).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FixedLocator, NullLocator

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch23 as C  # noqa: E402
from style import (AMBER, FIG_W, INK, LIGHT, MONEY, MUTED, PRICE, SHADE, T, clean_axes, figure, halo,  # noqa: E402
                   tint)

PALE = tint(MONEY, 0.5)
# the three panics: (colour, line style, marker) - 1866 solid, 1857 dashed (AMBER), 1847 pale and dotted
STYLE = {1866: dict(color=MONEY, lw=1.9, marker="o", ms=3.2, mec="white", mew=0.4),
         1857: dict(color=AMBER, lw=1.5, marker="s", ms=3.0, mec="white", mew=0.4, dashes=(4, 2)),
         1847: dict(color=PALE, lw=1.7, marker="^", ms=3.2, mec="white", mew=0.4, dashes=(1, 1.3))}


def _title(ax, s):
    ax.set_title(s, fontsize=9.0, weight="bold", loc="left", pad=4)


def _grid(ax, axis="y"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


def _line(ax, x, y, year, step=False, **extra):
    st = dict(STYLE[year])
    dashes = st.pop("dashes", None)
    if step:
        for k in ("marker", "ms", "mec", "mew"):
            st.pop(k)
        line, = ax.step(x, y, where="post", zorder=4 if year == 1866 else 3, **st, **extra)
    else:
        line, = ax.plot(x, y, zorder=4 if year == 1866 else 3, mfc=st["color"], **st, **extra)
    if dashes:
        line.set_dashes(dashes)
    return line


@figure("gold_panics")
def gold_panics():
    """(a) the Banking Department's reserve (notes and coin) in the ten weeks before and after the Treasury letters of
    1847, 1857 and 1866; (b) Bank Rate over the same weeks, as steps at the dates of sheet D1."""
    W, D = C.weekly(), C.bank_rate()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.75))
    fig.subplots_adjust(left=0.075, right=0.98, top=0.86, bottom=0.16, wspace=0.28)

    for year, day in C.LETTERS.items():
        s = C.aligned(W, "bd_reserve", day)
        _line(a1, s.index, s.values, year)
        col = STYLE[year]["color"] if year != 1847 else MUTED
        y0, dy = s.iloc[0], {1866: 0.95, 1857: 0.55, 1847: -0.6}[year]
        a1.text(s.index[0], y0 + dy, T(f"{year} 年", f"{year}"), fontsize=7.8, color=col, ha="left", va="center")
        t, v = C.window_min(W, "bd_reserve", day)
        x = (t - pd.Timestamp(day)).days / 7
        xt, yt, ha = {1847: (-3.2, 0.95, "right"), 1857: (-3.2, 0.3, "right"), 1866: (4.2, 0.45, "left")}[year]
        txt = a1.annotate(T(f"最低 {v:.2f}", f"low {v:.2f}"), (x, v), xytext=(xt, yt), fontsize=7.6, color=col,
                          ha=ha, va="center", arrowprops=dict(arrowstyle="-", lw=0.5, color=col))
        halo(txt, 2.0)
    a1.axvline(0, color=MUTED, lw=0.6, ls=(0, (1, 2)), zorder=2)
    a1.text(0.25, 9.6, T("财政部的信", "Treasury letter"), fontsize=7.6, color=INK, ha="left", va="top")
    a1.set_xlim(-10.5, 10.5)
    a1.set_ylim(0, 10)
    a1.set_xticks([-10, -5, 0, 5, 10])
    a1.set_xlabel(T("距写信的周数", "weeks from the letter"))
    a1.set_ylabel(T("准备金（百万英镑）", "reserve (£ m)"))
    _grid(a1)
    _title(a1, T("(a) 准备金在信前后跌到谷底", "(a) The reserve bottoms out at the letter"))

    for year, day in C.LETTERS.items():
        r = C.rate_aligned(D, day)
        _line(a2, r.index, r.values, year, step=True)
        top = r.max()
        x0 = r[r == top].index[0]
        xt, yt, ha = {1847: (0.45, 8.12, "left"), 1857: (-0.4, 10.45, "right"), 1866: (1.2, 10.45, "left")}[year]
        txt = a2.text(xt, yt, T(f"{year} 年 {top:g}%", f"{year}: {top:g}%"), fontsize=7.6,
                      color=STYLE[year]["color"] if year != 1847 else MUTED, ha=ha, va="bottom")
        halo(txt, 2.0)
    a2.axvline(0, color=MUTED, lw=0.6, ls=(0, (1, 2)), zorder=2)
    a2.set_xlim(-10.5, 10.5)
    a2.set_ylim(4, 11.5)
    a2.set_xticks([-10, -5, 0, 5, 10])
    a2.set_xlabel(T("距写信的周数", "weeks from the letter"))
    a2.set_ylabel(T("贴现率（%）", "Bank Rate (%)"))
    _grid(a2)
    _title(a2, T("(b) 贴现率在信的那一周升到顶", "(b) Bank Rate peaks in the week of the letter"))
    return fig


@figure("gold_rules")
def gold_rules():
    """(a) the yearly changes of the Bank of England's international and domestic assets, year-end to year-end,
    1880-1913; (b) the shares of years of compliance, violation and no change: Bloomfield's (as Dutton gives them)
    and the two counts from the weekly returns."""
    W, F = C.weekly(), C.facts()
    e, m = C.changes(W, "end"), C.changes(W, "mean")
    cls = C.classify(e)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.85), gridspec_kw=dict(width_ratios=[1.0, 1.05]))
    fig.subplots_adjust(left=0.075, right=0.98, top=0.86, bottom=0.17, wspace=0.32)

    lim_x, lim_y = (-12, 12), (-12, 21)
    a1.fill_between([0, lim_x[1]], 0, lim_y[1], color=tint(MONEY, 0.1), lw=0, zorder=0)
    a1.fill_between([lim_x[0], 0], lim_y[0], 0, color=tint(MONEY, 0.1), lw=0, zorder=0)
    a1.axhline(0, color=MUTED, lw=0.6, zorder=1)
    a1.axvline(0, color=MUTED, lw=0.6, zorder=1)
    ok = cls == "comply"
    a1.plot(e.intl[ok], e.dom[ok], ls="none", marker="o", ms=4.4, mfc=MONEY, mec="white", mew=0.5, zorder=4)
    a1.plot(e.intl[~ok], e.dom[~ok], ls="none", marker="s", ms=4.0, mfc=AMBER, mec="white", mew=0.5, zorder=4)
    for y, (dx, dy, ha) in {1894: (0.6, -1.4, "left"), 1895: (-0.5, 1.4, "right"), 1896: (0.5, 1.6, "left")}.items():
        t = a1.text(e.intl[y] + dx, e.dom[y] + dy, str(y), fontsize=7.4, color=INK, ha=ha, va="center")
        halo(t, 2.0)
    a1.text(11.5, 20.2, T(f"同向 {int(ok.sum())} 年", f"same sign: {int(ok.sum())}"), fontsize=7.8, color=MONEY,
            ha="right", va="top")
    a1.text(-11.5, 20.2, T(f"反向 {int((~ok).sum())} 年", f"opposite: {int((~ok).sum())}"), fontsize=7.8,
            color=AMBER, ha="left", va="top")
    a1.set_xlim(*lim_x)
    a1.set_ylim(*lim_y)
    a1.set_xlabel(T("国际资产的变化（百万英镑）", "change in international assets (£ m)"))
    a1.set_ylabel(T("国内资产的变化（百万英镑）", "change in domestic assets (£ m)"))
    clean_axes(a1)
    _title(a1, T("(a) 1880—1913 年，点散在四个象限", "(a) 1880-1913: points in all four quadrants"))

    se, sm = C.shares(e), C.shares(m)
    comply, violate = F["du_boe"]
    rows = [(T("Bloomfield\n（1959）", "Bloomfield\n(1959)"), comply, violate, 100 - comply - violate),
            (T("年末数", "year-end"), 100 * se["comply"] / se["n"], 100 * se["violate"] / se["n"], 0.0),
            (T("全年平均", "annual means"), 100 * sm["comply"] / sm["n"], 100 * sm["violate"] / sm["n"], 0.0)]
    k = np.arange(len(rows))[::-1]
    h = 0.56
    for y, (_, c, v, n) in zip(k, rows):
        a2.barh(y, c, h, color=MONEY, zorder=3)
        a2.barh(y, v, h, left=c, color=tint(AMBER, 0.15), ec=AMBER, lw=0.8, hatch="////", zorder=3)
        if n > 0:
            a2.barh(y, n, h, left=c + v, color=LIGHT, ec=MUTED, lw=0.6, zorder=3)
        a2.text(c / 2, y, f"{c:.0f}", fontsize=7.8, color="white", ha="center", va="center", zorder=5)
        t = a2.text(c + v / 2, y, f"{v:.0f}", fontsize=7.8, color=INK, ha="center", va="center", zorder=5)
        halo(t, 2.2, color=tint(AMBER, 0.15))
    a2.axvline(50, color=INK, lw=0.6, ls=(0, (2, 2)), zorder=4)
    a2.text(2, k[0] + 0.52, T("遵守", "comply"), fontsize=7.8, color=MONEY, ha="left", va="bottom")
    a2.text(52, k[0] + 0.52, T("违反", "violate"), fontsize=7.8, color=AMBER, ha="left", va="bottom")
    a2.annotate(T("没有变化 3", "no change: 3"), (98.5, k[0] + h / 2), xytext=(99.5, k[0] + 0.52),
                fontsize=7.4, color=MUTED, ha="right", va="bottom",
                arrowprops=dict(arrowstyle="-", lw=0.5, color=MUTED))
    a2.set_yticks(k)
    a2.set_yticklabels([r[0] for r in rows], fontsize=7.8)
    a2.set_xlim(0, 100)
    a2.set_ylim(-0.55, len(rows) - 0.25)
    a2.set_xticks([0, 25, 50, 75, 100])
    a2.set_xlabel(T("占年份的比例（%）", "share of years (%)"))
    a2.tick_params(axis="y", length=0)
    _grid(a2, axis="x")
    a2.spines["left"].set_visible(False)
    _title(a2, T("(b) 三种数法都是一半对一半", "(b) Three counts, all about half and half"))
    return fig


@figure("gold_prices")
def gold_prices():
    """UK wholesale prices, UK consumer prices and the US CPI, 1870-1913, 1873 = 100, on a log axis."""
    P = C.prices().loc[1870:1913]
    base = P.loc[1873]
    fig, ax = plt.subplots(figsize=(FIG_W, 2.65))
    fig.subplots_adjust(left=0.085, right=0.86, top=0.95, bottom=0.12)
    ax.axvspan(1873, 1896, color=tint(PRICE, 0.1), lw=0, zorder=0)
    w = 100 * P.uk_wholesale_2010_100 / base.uk_wholesale_2010_100
    c = 100 * P.uk_cpi_2015_100 / base.uk_cpi_2015_100
    u = 100 * P.us_cpi_1982_84_100 / base.us_cpi_1982_84_100
    ax.plot(w.index, w.values, color=PRICE, lw=1.9, zorder=4)
    line, = ax.plot(c.index, c.values, color=AMBER, lw=1.5, zorder=3)
    line.set_dashes((4, 2))
    ax.plot(u.index, u.values, color=tint(PRICE, 0.55), lw=1.5, zorder=3)
    end = P.index[-1]
    for s, col, lab in ((w, PRICE, T("英国批发物价", "UK wholesale")), (c, AMBER, T("英国消费物价", "UK consumer")),
                        (u, tint(PRICE, 0.7), T("美国消费物价", "US consumer"))):
        dy = {id(w): -1.5, id(c): 2.5, id(u): -1.0}[id(s)]
        ax.text(end + 0.8, s[end] + dy, lab, fontsize=7.8, color=col, ha="left", va="center")
    for s, col, va, off in ((w, PRICE, "top", 0.965), (c, AMBER, "bottom", 1.03), (u, tint(PRICE, 0.7), "top", 0.965)):
        t = ax.text(1896, s[1896] * off, f"{s[1896]:.0f}", fontsize=7.6, color=col, ha="center", va=va)
        halo(t, 2.0)
    ax.text(1884.5, 118, T("1873—1896 年", "1873-1896"), fontsize=7.8, color=PRICE, ha="center", va="center")
    ax.set_yscale("log")
    ticks = [50, 60, 70, 80, 90, 100, 120]
    ax.yaxis.set_major_locator(FixedLocator(ticks))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.set_yticklabels([str(t) for t in ticks])
    ax.set_ylim(48, 128)
    ax.set_xlim(1870, 1913)
    ax.set_xticks([1870, 1880, 1890, 1900, 1910])
    ax.set_ylabel(T("1873 年 = 100（对数）", "1873 = 100 (log)"))
    _grid(ax)
    ax.spines["right"].set_visible(False)
    return fig
