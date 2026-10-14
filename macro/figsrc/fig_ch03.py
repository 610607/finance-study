"""Figures for Chapter 3 (价格、通胀与利率).

Style as in fig_ch12.py and fig_ch02.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct
labels in the colour of their series, the second series of a panel in AMBER, dashed, with square markers where the
series is short. Colours follow §7: prices and inflation PRICE, interest rates and bond prices MONEY, real wages
OUTPUT. Every number comes from checks/check_ch03.py, which reads the snapshots fred_prices_monthly,
fred_prices_quarterly, fred_yields_daily and mof_jgb_curves; the bond of fig prices_bond is the teaching example of
the text (ex:prices-bond).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FixedLocator, NullLocator

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch03 as C  # noqa: E402
from style import AMBER, FIG_W, INK, INSTIT, LIGHT, MONEY, MUTED, OUTPUT, PRICE, T, clean_axes, figure, tint  # noqa: E402

SQUARE = dict(marker="s", ms=4.6, mfc=AMBER, mec="white", mew=0.6)
DOT = dict(marker="o", ms=5.0, mec="white", mew=0.6)
MINUS = "−"


def _title(ax, s):
    ax.set_title(s, fontsize=9.0, weight="bold", loc="left", pad=4)


def _grid(ax, axis="y"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=8.5)


def _num(v: float, fmt: str = ".2f") -> str:
    return f"{v:{fmt}}".replace("-", MINUS)


@figure("prices_wages")
def prices_wages():
    W = C.wages_and_prices(C.monthly(), C.quarterly()).loc[1972:2024]
    yrs = W.index
    rc = 100 * W.real_cpi / W.real_cpi[1972]
    rp = 100 * W.real_pce / W.real_pce[1972]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIG_W, 2.85), gridspec_kw=dict(wspace=0.3))
    ax1.axhline(100, color=MUTED, lw=0.7, ls=":", zorder=1)
    ax1.plot(yrs, rc, color=OUTPUT, lw=2.0, zorder=3)
    ax1.plot(yrs, rp, color=AMBER, lw=2.0, dashes=(4, 2), zorder=3)
    for y, s, c, mk in ((2024, rc, OUTPUT, DOT), (2024, rp, AMBER, SQUARE), (1995, rc, OUTPUT, DOT)):
        kw = dict(mk, mfc=c) if mk is DOT else mk
        ax1.plot([y], [s[y]], color=c, zorder=4, **kw)
    ax1.text(2023, rp[2024] + 3, _num(rp[2024], ".1f"), color=AMBER, fontsize=7.8, ha="center", va="bottom")
    ax1.text(2023, rc[2024] - 3.5, _num(rc[2024], ".1f"), color=OUTPUT, fontsize=7.8, ha="center", va="top")
    ax1.text(1995, rc[1995] - 3.5, T(f"1995 年 {rc[1995]:.1f}", f"1995: {rc[1995]:.1f}"), color=OUTPUT, fontsize=7.8,
             ha="center", va="top")
    ax1.text(1999, 121, T("用 PCE 价格指数平减", "deflated by the\nPCE price index"), color=AMBER, fontsize=7.8,
             ha="right", va="bottom")
    ax1.text(2003, 85.5, T("用 CPI-U 平减", "deflated by\nthe CPI-U"), color=OUTPUT, fontsize=7.8, ha="left",
             va="top")
    ax1.set_xlim(1970, 2027)
    ax1.set_ylim(72, 142)
    ax1.set_xticks([1972, 1985, 1998, 2011, 2024])
    ax1.set_ylabel(T("实际时薪，1972 = 100", "real hourly earnings, 1972 = 100"), fontsize=9)
    _grid(ax1)
    _title(ax1, T("(a) 同一份工资：平减指数决定涨没涨", "(a) One wage, two real wages"))

    idx = {k: 100 * W[k] / W.loc[1972, k] for k in ("CPIAUCSL", "PCEPI", "GDPDEF")}
    ax2.plot(yrs, idx["CPIAUCSL"], color=PRICE, lw=2.0, zorder=4)
    ax2.plot(yrs, idx["PCEPI"], color=AMBER, lw=2.0, dashes=(4, 2), zorder=3)
    ax2.plot(yrs, idx["GDPDEF"], color=tint(PRICE, 0.45), lw=1.6, ls=":", zorder=3)
    ax2.set_yscale("log")
    for k, zh, en, c, dy in (("CPIAUCSL", "CPI-U", "CPI-U", PRICE, 1.07),
                             ("PCEPI", "PCE 价格指数", "PCE price index", AMBER, 1.0),
                             ("GDPDEF", "GDP 平减指数", "GDP deflator", tint(PRICE, 0.6), 0.88)):
        v = idx[k][2024]
        ax2.text(2025.2, v * dy, f"{v:.0f}", color=c, fontsize=7.8, ha="left", va="center")
    ax2.text(1990, idx["CPIAUCSL"][1990] * 1.2, T("CPI-U", "CPI-U"), color=PRICE, fontsize=7.8, ha="right")
    ax2.text(2000, 255, T("PCE 价格指数（虚线）", "PCE price index (dashed)"), color=AMBER, fontsize=7.8, ha="left",
             va="center")
    ax2.text(2000, 212, T("GDP 平减指数（点线）", "GDP deflator (dotted)"), color=tint(PRICE, 0.6), fontsize=7.8,
             ha="left", va="center")
    ax2.set_xlim(1970, 2031)
    ax2.set_ylim(90, 900)
    ax2.yaxis.set_major_locator(FixedLocator([100, 200, 400, 800]))
    ax2.yaxis.set_minor_locator(NullLocator())
    ax2.set_yticklabels(["100", "200", "400", "800"])
    ax2.set_xticks([1972, 1985, 1998, 2011, 2024])
    ax2.set_ylabel(T("1972 = 100（对数）", "1972 = 100 (log scale)"), fontsize=9)
    _grid(ax2)
    _title(ax2, T("(b) 三种价格指数，CPI 涨得最快", "(b) The CPI rose fastest"))
    fig.subplots_adjust(left=0.09, right=0.97, top=0.9, bottom=0.1)
    return fig


@figure("prices_bond")
def prices_bond():
    i0 = C.BOND["i0"]
    dm = C.modified(i0)
    ys = np.linspace(0.0, 0.065, 131)
    price = np.array([C.bond_price(y) for y in ys])
    tangent = 100 - 100 * dm * (ys - i0)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIG_W, 2.85), gridspec_kw=dict(width_ratios=[1.0, 1.1], wspace=0.3))
    ax1.fill_between(100 * ys, tangent, price, color=tint(MONEY, 0.12), lw=0, zorder=1)
    ax1.plot(100 * ys, price, color=MONEY, lw=2.0, zorder=3)
    ax1.plot(100 * ys, tangent, color=AMBER, lw=1.6, dashes=(4, 2), zorder=3)
    for y in (0.02, 0.03, 0.04):
        p = C.bond_price(y)
        ax1.plot([100 * y], [p], color=MONEY, zorder=4, **dict(DOT, mfc=MONEY))
        ax1.text(100 * y + 0.18, p + 1.5, f"{p:.2f}", color=MONEY, fontsize=7.8, ha="left", va="bottom")
    ax1.plot([4], [100 - 100 * dm * 0.01], zorder=4, color=AMBER, **SQUARE)
    ax1.text(4.0, 100 - 100 * dm * 0.01 - 2.0, f"{100 - 100 * dm * 0.01:.2f}", color=AMBER, fontsize=7.8, ha="center",
             va="top")
    ax1.text(0.15, 82.6, T(f"切线：斜率由修正久期\n{dm:.2f} 给出", f"tangent: slope given by\nmodified duration {dm:.2f}"),
             color=AMBER, fontsize=7.6, ha="left", va="center", linespacing=1.3)
    ax1.annotate(T("两者之差 = 凸性", "the gap = convexity"), (0.8, 0.5 * (C.bond_price(0.008) + 100 + 100 * dm * 0.022)),
                 xytext=(0.15, 135), fontsize=7.6, color=MONEY, ha="left", va="center",
                 arrowprops=dict(arrowstyle="-", color=MONEY, lw=0.6))
    ax1.set_xlim(0, 6.5)
    ax1.set_ylim(78, 140)
    ax1.set_xlabel(T("到期收益率（%）", "yield to maturity (%)"), fontsize=9)
    ax1.set_ylabel(T("价格（元）", "price (yuan)"), fontsize=9)
    _grid(ax1)
    _title(ax1, T("(a) 价格曲线向上弯", "(a) The price curve bends upward"))

    tab = C.price_changes_by_maturity()
    n = tab.index.values
    ax2.axhline(0, color=INK, lw=0.7, zorder=2)
    ax2.bar(n, tab["down"], width=0.72, color=MONEY, edgecolor="white", lw=0.3, zorder=3)
    ax2.bar(n, tab["up"], width=0.72, color="white", edgecolor=AMBER, hatch="////", lw=0.8, zorder=3)
    for k in (2, 10, 30):
        ax2.text(k, tab.loc[k, "down"] + 0.6, f"+{tab.loc[k, 'down']:.1f}", color=MONEY, fontsize=7.6, ha="center",
                 va="bottom")
        ax2.text(k, tab.loc[k, "up"] - 0.6, _num(tab.loc[k, "up"], ".1f"), color=AMBER, fontsize=7.6, ha="center",
                 va="top")
    ax2.text(1.0, 17.0, T("收益率下降 1 个百分点", "yields fall 1 pp"), color=MONEY, fontsize=7.8, ha="left")
    ax2.text(1.0, -15.5, T("收益率上升 1 个百分点", "yields rise 1 pp"), color=AMBER, fontsize=7.8, ha="left")
    ax2.set_xlim(0, 31.5)
    ax2.set_ylim(-21, 26)
    ax2.set_xticks([1, 5, 10, 15, 20, 25, 30])
    ax2.set_xlabel(T("期限（年）", "maturity (years)"), fontsize=9)
    ax2.set_ylabel(T("价格变化（%）", "price change (%)"), fontsize=9)
    _grid(ax2)
    _title(ax2, T("(b) 期限越长，价格变化越大", "(b) Longer bonds move more"))
    fig.subplots_adjust(left=0.085, right=0.98, top=0.9, bottom=0.16)
    return fig


def _curve(J, d):
    c = J.loc[d].dropna()
    return np.array([int(k[:-1]) for k in c.index]), c.values


@figure("prices_jgb")
def prices_jgb():
    J = C.jgb()
    d0, d1, d2, d3, d4 = C.JGB_DATES
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIG_W, 2.85), sharey=True, gridspec_kw=dict(wspace=0.12))
    for ax in (ax1, ax2):
        ax.axhline(0, color=MUTED, lw=0.8, ls=":", zorder=1)
    x, y = _curve(J, d0)
    ax1.plot(x, y, color=MONEY, lw=2.0, zorder=4, **dict(DOT, mfc=MONEY, ms=4.2))
    x, y = _curve(J, d1)
    ax1.plot(x, y, color=AMBER, lw=2.0, dashes=(4, 2), zorder=4, **dict(SQUARE, ms=4.0))
    x, y = _curve(J, d2)
    ax1.plot(x, y, color=tint(MONEY, 0.5), lw=1.6, ls=":", zorder=3)
    c1 = J.loc[d1]
    ax1.text(0.8, c1["7Y"] - 0.12, T(f"最低点 7 年期 {_num(c1['7Y'], '.3f')}", f"lowest: 7-year {_num(c1['7Y'], '.3f')}"),
             color=AMBER, fontsize=7.6, ha="left", va="top")
    ax1.annotate(T(f"直到 15 年期为负（{_num(c1['15Y'], '.3f')}）", f"negative to 15 years ({_num(c1['15Y'], '.3f')})"),
                 (15, c1["15Y"]), xytext=(19, -0.52), color=AMBER, fontsize=7.6, ha="left", va="center",
                 arrowprops=dict(arrowstyle="-", color=AMBER, lw=0.6))
    ax1.text(26, J.loc[d0, "30Y"] + 0.12, T("2016 年 1 月 28 日", "28 Jan 2016"), color=MONEY, fontsize=7.8,
             ha="center", va="bottom")
    ax1.text(31, J.loc[d1, "30Y"] + 0.33, T("2016 年 7 月 27 日", "27 Jul 2016"), color=AMBER, fontsize=7.8, ha="center",
             va="bottom")
    ax1.text(31, J.loc[d2, "30Y"] - 0.2, T("2019 年 8 月 28 日", "28 Aug 2019"), color=tint(MONEY, 0.6),
             fontsize=7.8, ha="center", va="top")
    ax1.set_xlim(0, 41)
    ax1.set_ylim(-0.88, 4.6)
    ax1.set_xticks([1, 5, 10, 20, 30, 40])
    ax1.set_xlabel(T("期限（年）", "maturity (years)"), fontsize=9)
    ax1.set_ylabel(T("收益率（%）", "yield (%)"), fontsize=9)
    _grid(ax1)
    _title(ax1, T("(a) 2016 年：曲线沉到零以下", "(a) 2016: the curve sinks below zero"))

    x, y = _curve(J, d1)
    ax2.plot(x, y, color=INSTIT, lw=0.9, zorder=2)
    x, y = _curve(J, d3)
    ax2.plot(x, y, color=MONEY, lw=2.0, zorder=4, **dict(DOT, mfc=MONEY, ms=4.2))
    x, y = _curve(J, d4)
    ax2.plot(x, y, color=AMBER, lw=2.0, dashes=(4, 2), zorder=4, **dict(SQUARE, ms=4.0))
    ax2.text(29, J.loc[d3, "30Y"] + 0.15, T("2024 年 3 月 18 日", "18 Mar 2024"), color=MONEY, fontsize=7.8, ha="center",
             va="bottom")
    ax2.text(22, J.loc[d4, "20Y"] + 0.3, T("2026 年 9 月 30 日", "30 Sep 2026"), color=AMBER, fontsize=7.8, ha="center",
             va="bottom")
    ax2.text(30, J.loc[d1, "30Y"] + 0.05, T("2016 年 7 月 27 日", "27 Jul 2016"), color=INSTIT, fontsize=7.6, ha="center",
             va="bottom")
    c4 = J.loc[d4]
    ax2.text(10, c4["10Y"] - 0.3, T(f"10 年期 {c4['10Y']:.3f}", f"10-year {c4['10Y']:.3f}"), color=AMBER, fontsize=7.6,
             ha="left", va="top")
    ax2.set_xlim(0, 41)
    ax2.set_xticks([1, 5, 10, 20, 30, 40])
    ax2.set_xlabel(T("期限（年）", "maturity (years)"), fontsize=9)
    _grid(ax2)
    ax2.tick_params(labelleft=False)
    _title(ax2, T("(b) 退出以后：整条曲线抬升", "(b) After the exit: the whole curve rises"))
    fig.subplots_adjust(left=0.08, right=0.985, top=0.9, bottom=0.16)
    return fig


@figure("prices_breakeven")
def prices_breakeven():
    D, M = C.daily(), C.monthly()
    bm = C.breakeven_monthly(D)
    ft = C.forecast_test(D, M).loc[C.TEST_FROM:C.TEST_TO]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(FIG_W, 4.4), gridspec_kw=dict(hspace=0.45))
    t = bm.index
    ax1.axhline(0, color=MUTED, lw=0.7, ls=":", zorder=1)
    ax1.fill_between(t, bm.DFII10, bm.DGS10, color=tint(PRICE, 0.22), lw=0, zorder=1)
    ax1.plot(t, bm.DGS10, color=MONEY, lw=1.8, zorder=3)
    ax1.plot(t, bm.DFII10, color=AMBER, lw=1.8, dashes=(4, 2), zorder=3)
    lo = bm.BE.idxmin()
    ax1.annotate(T(f"{lo.year} 年 {lo.month} 月：两线之差只有 {bm.BE.min():.2f}",
                   f"{lo:%b %Y}: a gap of only {bm.BE.min():.2f}"),
                 (lo, bm.loc[lo, "DGS10"]), xytext=(pd.Timestamp("2010-03-01"), 4.9), fontsize=7.6, color=INK,
                 ha="left", va="center", arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    ax1.text(pd.Timestamp("2004-01-01"), 5.4, T("10 年期名义国债", "10-year nominal Treasury"), color=MONEY, fontsize=7.8,
             ha="left", va="bottom")
    ax1.text(pd.Timestamp("2012-06-01"), -1.15, T("10 年期 TIPS（实际收益率）", "10-year TIPS (real yield)"), color=AMBER,
             fontsize=7.8, ha="left", va="center")
    ax1.text(pd.Timestamp("2005-07-01"), 3.1, T("盈亏平衡通胀率", "breakeven inflation"), color=PRICE, fontsize=7.8,
             ha="center", va="center")
    last = bm.index[-1]
    ax1.text(last + pd.DateOffset(months=4), bm.loc[last, "DGS10"], _num(bm.loc[last, "DGS10"]), color=MONEY,
             fontsize=7.6, ha="left", va="center")
    ax1.text(last + pd.DateOffset(months=4), bm.loc[last, "DFII10"], _num(bm.loc[last, "DFII10"]), color=AMBER,
             fontsize=7.6, ha="left", va="center")
    ax1.set_xlim(pd.Timestamp("2002-07-01"), pd.Timestamp("2027-09-01"))
    ax1.set_xticks([pd.Timestamp(f"{y}-01-01") for y in range(2004, 2025, 4)])
    ax1.set_xticklabels([str(y) for y in range(2004, 2025, 4)])
    ax1.set_ylim(-1.7, 6.3)
    ax1.set_ylabel(T("收益率（%）", "yield (%)"), fontsize=9)
    _grid(ax1)
    _title(ax1, T("(a) 名义收益率减实际收益率", "(a) Nominal yield less real yield"))

    t2 = ft.index
    ax2.plot(t2, ft.be, color=PRICE, lw=1.8, zorder=3)
    ax2.plot(t2, ft.realized, color=AMBER, lw=1.8, dashes=(4, 2), zorder=3)
    ax2.text(pd.Timestamp("2003-03-01"), 3.15, T("盈亏平衡通胀率（当月）", "breakeven (that month)"), color=PRICE,
             fontsize=7.8, ha="left", va="bottom")
    ax2.text(pd.Timestamp("2010-06-01"), 3.62, T("此后十年 CPI-U 的实际年均通胀", "CPI-U inflation over the next ten years"),
             color=AMBER, fontsize=7.8, ha="left", va="bottom")
    # (month, position of the realized label: offset in months, in pp)
    for d, dm, dy in (("2008-12-01", 7, 0.85), ("2016-02-01", 8, 0.0)):
        v = ft.loc[d, "be"]
        ax2.plot([pd.Timestamp(d)], [v], color=PRICE, zorder=4, **dict(DOT, mfc=PRICE, ms=4.4))
        ax2.text(pd.Timestamp(d), v - 0.12, f"{v:.2f}", color=PRICE, fontsize=7.6, ha="center", va="top")
        r = ft.loc[d, "realized"]
        ax2.plot([pd.Timestamp(d)], [r], color=AMBER, zorder=4, **dict(SQUARE, ms=4.2))
        ax2.annotate(f"{r:.2f}", (pd.Timestamp(d), r), xytext=(pd.Timestamp(d) + pd.DateOffset(months=dm), r + dy),
                     color=AMBER, fontsize=7.6, ha="left", va="center",
                     arrowprops=dict(arrowstyle="-", color=AMBER, lw=0.6) if dy else None)
    ax2.set_xlim(pd.Timestamp("2002-07-01"), pd.Timestamp("2017-04-01"))
    ax2.set_ylim(-0.2, 4.2)
    ax2.set_ylabel("%", fontsize=9)
    _grid(ax2)
    _title(ax2, T("(b) 当作预测，它的误差很大", "(b) As a forecast, it misses by a lot"))
    fig.subplots_adjust(left=0.085, right=0.965, top=0.95, bottom=0.06)
    return fig
