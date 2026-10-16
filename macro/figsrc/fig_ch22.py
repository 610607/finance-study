"""Figures for Chapter 22 (马克思：积累、危机与再生产图式).

Style as in fig_ch21.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series, the second series in AMBER and dashed with square markers. Interest rates are MONEY, output,
employment and the wage share OUTPUT. All numbers come from checks/check_ch22.py, which reads the snapshots
boe_millennium_bank_rate_1856_1858, boe_millennium_gb_1855_1859_monthly, boe_millennium_uk_1855_1913,
clark2015_england_decadal_1250_1860 and marx_facts (Marx's schemes, Allen's Table 1). marx_schemes (a) is a diagram
of the simple scheme; (b) computes the expanded scheme by Marx's rule with check_ch22.expanded.
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch22 as C  # noqa: E402
from style import (ACCENT, AMBER, FIG_W, INK, LIGHT, MONEY, MUTED, OUTPUT, ZH, T, clean_axes, figure,  # noqa: E402
                   halo, label, rbox, shade_periods, tint)

SQUARE = dict(marker="s", ms=3.4, mfc=AMBER, mec="white", mew=0.4)
DOT = dict(marker="o", ms=4.2, mec="white", mew=0.5)


def _title(ax, s):
    ax.set_title(s, fontsize=9.0, weight="bold", loc="left", pad=4)


def _grid(ax, axis="y"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


def _dashed(ax, x, y, color=AMBER, lw=1.5, **kw):
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


def _mid(year: int, month: int) -> datetime:
    return datetime(year, month, 15)


def _month_ticks(ax):
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_minor_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(FuncFormatter(
        lambda x, _: (f"{mdates.num2date(x).year}" if mdates.num2date(x).month == 1 else
                      T(f"{mdates.num2date(x).month} 月", mdates.num2date(x).strftime("%b")))))
    ax.tick_params(axis="x", which="minor", length=1.5)


EVENTS = [("1857-10-27", T("利物浦", "Liverpool")), ("1857-11-09", T("西部银行", "Western Bank")),
          ("1857-11-12", T("财政部的信", "Treasury letter"))]


@figure("marx_1857")
def marx_1857():
    """(a) Bank Rate (steps at the dates of sheet D1) and the market rate for prime bills (monthly), 1856-1858;
    (b) the ironfounders' unemployment rate and raw cotton consumption (September 1857 = 100)."""
    D, M = C.bank_rate(), C.monthly()
    a, b = pd.Timestamp("1856-01-01"), pd.Timestamp("1858-12-31")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.75))
    fig.subplots_adjust(left=0.075, right=0.91, top=0.86, bottom=0.15, wspace=0.42)

    # (a) the steps
    steps = pd.concat([D, pd.Series([D.iloc[-1]], index=[b])])
    a1.step(steps.index, steps.values, where="post", color=MONEY, lw=1.9, zorder=4)
    m = M.loc[(1856, 1):(1858, 12)]
    xs = [_mid(y, mo) for y, mo in m.index]
    _dashed(a1, xs, m.prime_bills_rate.values, color=AMBER, **SQUARE)
    for day, _ in EVENTS:
        a1.axvline(pd.Timestamp(day), color=MUTED, lw=0.6, ls=(0, (1, 2)), zorder=2)
    a1.text(pd.Timestamp("1857-10-20"), 10.75, T("10 月 27 日—11 月 12 日：\n两家银行倒闭，财政部的信",
                                                 "27 Oct-12 Nov: failures;\nthe Treasury letter"),
            fontsize=7.8, color=INK, ha="right", va="top", linespacing=1.25)
    top = D.max()
    a1.annotate(f"{top:g}%", (pd.Timestamp("1857-11-12"), top), xytext=(pd.Timestamp("1858-02-20"), top - 0.3),
                fontsize=7.8, color=MONEY, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", lw=0.6, color=MONEY))
    a1.text(pd.Timestamp("1856-02-01"), 7.6, T("贴现率", "Bank Rate"), fontsize=8.0, color=MONEY, ha="left")
    a1.text(pd.Timestamp("1858-06-01"), 4.0, T("优质票据\n市场贴现率", "market rate,\nprime bills"), fontsize=7.8,
            color=AMBER, ha="left", va="bottom", linespacing=1.2)
    a1.set_xlim(a, b)
    a1.set_ylim(0, 11)
    _month_ticks(a1)
    a1.set_ylabel(T("年率（%）", "% a year"))
    _grid(a1)
    _title(a1, T("(a) 十月中旬起，阶梯陡起来", "(a) The steps steepen in October"))

    # (b) unemployment and cotton
    u = m.unemp_ironfounders
    base = M.cotton_bales_week[(1857, 9)]
    cot = 100 * m.cotton_bales_week / base
    a2.plot(xs, u.values, color=OUTPUT, lw=1.9, zorder=4, **DOT, mfc=OUTPUT)
    a3 = _right_axis(a2, AMBER)
    _dashed(a3, xs, cot.values, color=AMBER, lw=1.1, marker="s", ms=2.6, mfc=AMBER, mec="white", mew=0.3)
    pk = u.idxmax()
    a2.annotate(T(f"{pk[0]} 年 {pk[1]} 月 {u.max():.1f}%", f"{datetime(pk[0], pk[1], 1):%b} {pk[0]}: {u.max():.1f}%"),
                (_mid(*pk), u.max()), xytext=(_mid(1857, 12), u.max() + 1.6), fontsize=7.8, color=OUTPUT,
                ha="right", va="center", arrowprops=dict(arrowstyle="-", lw=0.6, color=OUTPUT))
    a2.text(_mid(1856, 2), 4.2, T("铸铁工人失业率（左）", "ironfounders (left)"), fontsize=7.8,
            color=OUTPUT, ha="left", va="center")
    low = cot.idxmin()
    a3.annotate(f"{cot.min():.0f}", (_mid(*low), cot.min()), xytext=(_mid(1857, 6), 37),
                fontsize=7.8, color=AMBER, ha="right", va="center",
                arrowprops=dict(arrowstyle="-", lw=0.6, color=AMBER))
    a3.text(_mid(1858, 11), 25, T("原棉消耗（右）", "raw cotton (right)"), fontsize=7.8, color=AMBER,
            ha="right", va="center")
    for day, _ in EVENTS[2:]:
        a2.axvline(pd.Timestamp(day), color=MUTED, lw=0.6, ls=(0, (1, 2)), zorder=2)
    a2.set_xlim(a, b)
    a2.set_ylim(0, 24)
    a3.set_ylim(0, 140)
    a3.set_ylabel(T("1857 年 9 月 = 100", "Sep 1857 = 100"), color=AMBER)
    _month_ticks(a2)
    a2.set_ylabel(T("失业率（%）", "unemployment (%)"))
    _grid(a2)
    a2.spines["right"].set_visible(False)
    _title(a2, T("(b) 失业到 1858 年春天才到顶", "(b) Unemployment peaks in 1858"))
    return fig


def _flow(ax, p, q, color, lw=1.6, rad=0.0, ms=11):
    a = FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=ms, lw=lw, color=color, zorder=5,
                        connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0)
    ax.add_patch(a)
    return a


@figure("marx_schemes")
def marx_schemes():
    """(a) the simple scheme as two flows between the departments; (b) the expanded scheme, computed by the rule
    and as printed, log scale."""
    F = C.facts()
    sI, sII = F["k2_simple_I"], F["k2_simple_II"]
    fig = plt.figure(figsize=(FIG_W, 2.95))
    a1 = fig.add_axes([0.0, 0.03, 0.50, 0.84])
    a2 = fig.add_axes([0.60 if ZH else 0.63, 0.14, 0.33, 0.73])

    # (a) the diagram
    W = 10.0
    H = W * (0.84 * 2.95) / (0.50 * FIG_W)
    a1.set_xlim(0, W)
    a1.set_ylim(0, H)
    a1.set_aspect("equal")
    a1.axis("off")
    a1.set_xticks([])
    a1.set_yticks([])
    bw, bh, y0 = 3.5, 3.0, 2.55
    boxes = {"I": (0.25, sI, T("第 I 部类：生产资料", "I: producer goods")),
             "II": (W - 0.25 - bw, sII, T("第 II 部类：消费资料", "II: consumer goods"))}
    for k, (x, s, name) in boxes.items():
        rbox(a1, x, y0, bw, bh, fc=tint(OUTPUT, 0.14), ec=tint(OUTPUT, 0.6), lw=0.8)
        rbox(a1, x, y0 + bh - 0.62, bw, 0.62, fc=tint(ACCENT, 0.88), r=0.1)
        label(a1, x + bw / 2, y0 + bh - 0.31, name, color="white", size=7.8, weight="bold")
        label(a1, x + bw / 2, y0 + 1.85, f"{s[0]:.0f}c", size=8.0)
        label(a1, x + bw / 2, y0 + 1.25, f"+ {s[1]:.0f}v + {s[2]:.0f}m", size=8.0)
        label(a1, x + bw / 2, y0 + 0.5, T(f"产品 {s[3]:,.0f}", f"product {s[3]:,.0f}"), size=7.8, color=MUTED)
    xI, xII = boxes["I"][0] + bw, boxes["II"][0]
    _flow(a1, (xI + 0.1, y0 + bh - 0.35), (xII - 0.1, y0 + bh - 0.35), OUTPUT)
    label(a1, W / 2, y0 + bh + 0.05, T(f"生产资料 {sII[0]:,.0f}\n= II 的 c", f"means of prod. {sII[0]:,.0f}\n= II's c"),
          size=7.6, color=OUTPUT, va="bottom")
    _flow(a1, (xII - 0.1, y0 + 0.35), (xI + 0.1, y0 + 0.35), AMBER)
    label(a1, W / 2, y0 + 0.2, T(f"消费资料 {sI[1] + sI[2]:,.0f}\n= I 的 v + m", f"consumer\ngoods {sI[1] + sI[2]:,.0f}\n= I's v + m"),
          size=7.6, color=AMBER, va="top")
    # flows that stay within a department
    for k, own, col in (("I", sI[0], OUTPUT), ("II", sII[1] + sII[2], AMBER)):
        x = boxes[k][0]
        _flow(a1, (x + bw * 0.30, y0 - 0.02), (x + bw * 0.70, y0 - 0.02), col, lw=1.0, rad=1.1, ms=8)
        label(a1, x + bw / 2, y0 - 1.05, T(f"{own:,.0f} 留在部类内部", f"{own:,.0f} stays inside"), size=7.6, color=col)
    a1.set_title(T("(a) 两股流一样粗", "(a) The two flows are equal"), fontsize=9.0, weight="bold", loc="left",
                 pad=4)

    # (b) the expanded scheme
    E, P = C.expanded(F), C.printed(F)
    t = np.arange(len(E))
    series = [("total", OUTPUT, T("合计", "total")), ("I", tint(OUTPUT, 0.45), T("第 I 部类", "I")),
              ("II", AMBER, T("第 II 部类", "II"))]
    for col, colour, name in series:
        if col == "II":
            _dashed(a2, t, E[col], color=colour)
        else:
            a2.plot(t, E[col], color=colour, lw=1.9 if col == "total" else 1.6, zorder=3)
        a2.plot(t, P[col], ls="none", marker="s" if col == "II" else "o", ms=4.0, mfc="white", mec=colour, mew=1.0,
                zorder=4)
        a2.text(5.15, E[col].iloc[-1], name, fontsize=7.6, color=colour if col != "I" else OUTPUT, ha="left",
                va="center")
    a2.annotate(T(f"印作 {P.II[4]:,.0f}\n应为 {E.II[4]:,.1f}", f"printed {P.II[4]:,.0f},\nrule {E.II[4]:,.1f}"),
                (4, P.II[4]), xytext=(2.3, 2400), fontsize=7.6, color=AMBER, ha="center", va="center",
                linespacing=1.2, arrowprops=dict(arrowstyle="-", lw=0.6, color=AMBER))
    a2.text(0.1, 12500, T("线：按规则\n点：马克思印出", "lines: the rule\npoints: as printed"), fontsize=7.6,
            color=MUTED, ha="left", va="center", linespacing=1.25)
    a2.set_yscale("log")
    a2.set_ylim(2000, 20000)
    a2.yaxis.set_major_locator(FixedLocator([2000, 3000, 5000, 10000, 20000]))
    a2.yaxis.set_minor_locator(NullLocator())
    a2.set_yticklabels(["2,000", "3,000", "5,000", "10,000", "20,000"])
    a2.set_xlim(-0.3, 5.9)
    a2.set_xticks(t)
    a2.set_xlabel(T("年末（0 = 开始）", "end of year (0 = start)"))
    a2.set_ylabel(T("产品（对数）", "product (log)"))
    _grid(a2)
    _title(a2, T("(b) 第一年以后每年 10%", "(b) 10% a year after year 1"))
    return fig


@figure("marx_shares")
def marx_shares():
    """(a) Clark's shares of NNI by decade, 1700s-1860s; (b) Allen's Table 1: growth of output per worker and of the
    real wage, % a year."""
    Cl, F = C.clark(), C.facts()
    d = Cl.loc[1700:1860]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.75), gridspec_kw=dict(width_ratios=[1.1, 1.0]))
    fig.subplots_adjust(left=0.085, right=0.98, top=0.86, bottom=0.17, wspace=0.3)

    x = d.index + 5
    a1.plot(x, 100 * d.wage_share, color=OUTPUT, lw=1.9, zorder=4, **DOT, mfc=OUTPUT)
    _dashed(a1, x, 100 * d.rest_share, color=AMBER, **SQUARE)
    a1.plot(x, 100 * d.rent_share, color=tint(OUTPUT, 0.45), lw=1.4, zorder=3)
    a1.text(1712, 61.5, T("工资收入", "wage income"), fontsize=7.6, color=OUTPUT, ha="left")
    a1.text(1712, 33.5, T("其余（主要是资本）", "the rest (mostly capital)"), fontsize=7.6, color=AMBER, ha="left")
    a1.text(1712, 15.0, T("地租", "land rents"), fontsize=7.6, color=OUTPUT, ha="left", va="top")
    for dec, va in ((1700, "bottom"), (1800, "top"), (1860, "bottom")):
        v = 100 * d.wage_share[dec]
        a1.text(dec + 5, v + (1.6 if va == "bottom" else -1.8), f"{v:.0f}", fontsize=7.6, color=OUTPUT,
                ha="center", va=va)
    a1.axvline(1805, color=MUTED, lw=0.6, ls=(0, (1, 2)), zorder=2)
    a1.set_xlim(1700, 1870)
    a1.set_xticks([1705, 1755, 1805, 1855])
    a1.set_xticklabels([T("1700 年代", "1700s"), T("1750 年代", "1750s"), T("1800 年代", "1800s"),
                        T("1850 年代", "1850s")])
    a1.set_ylim(0, 70)
    a1.set_ylabel(T("占国民净收入（%）", "% of NNI"))
    _grid(a1)
    _title(a1, T("(a) Clark：1800 年以后工资份额回升", "(a) Clark: the wage share recovers after 1800"))

    tab = C.allen_table(F)
    k = np.arange(len(tab))
    w = 0.36
    b1 = a2.bar(k - w / 2, tab.yl, w, color=OUTPUT, zorder=3)
    b2 = a2.bar(k + w / 2, tab.wage, w, color=tint(AMBER, 0.15), ec=AMBER, lw=0.8, hatch="////", zorder=3)
    for bars, col in ((b1, OUTPUT), (b2, AMBER)):
        for r in bars:
            h = r.get_height()
            a2.text(r.get_x() + r.get_width() / 2, h + 0.03, f"{h:.2f}", fontsize=7.6, color=col, ha="center",
                    va="bottom")
    a2.text(-0.45, 1.68, T("每个工人的产出", "output per worker"), fontsize=7.6, color=OUTPUT, ha="left")
    a2.text(-0.45, 1.52, T("实际工资", "real wage"), fontsize=7.6, color=AMBER, ha="left")
    a2.set_xticks(k)
    a2.set_xticklabels([f"{a}—\n{b}" if ZH else f"{a}-\n{b}" for a, b in zip(tab.start, tab.end)])
    a2.tick_params(axis="x", labelsize=8.0)
    a2.set_ylim(0, 1.85)
    a2.set_ylabel(T("每年增长（%）", "growth, % a year"))
    _grid(a2)
    _title(a2, T("(b) Allen：1800—1830 年工资不动", "(b) Allen: wages flat, 1800-1830"))
    return fig


@figure("marx_uk")
def marx_uk():
    """(a) union unemployment, 1855-1913, with the peaks found by SciPy; (b) the wage share and the profit proxy,
    with the recessions (trough to peak of unemployment) shaded."""
    A = C.annual()
    cy = C.cycles(A)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.75))
    fig.subplots_adjust(left=0.075, right=0.92, top=0.86, bottom=0.15, wspace=0.42)

    u = A.unemp_unions
    a1.plot(u.index, u.values, color=OUTPUT, lw=1.7, zorder=3)
    a1.plot(cy["peaks"], u[cy["peaks"]], ls="none", marker="o", ms=4.6, mfc=OUTPUT, mec="white", mew=0.5, zorder=4)
    for y in cy["peaks"]:
        left = y == cy["peaks"][1]                     # 1862 sits between 1858 and 1868
        t = a1.text(y + (0.6 if left else 0), u[y] + 0.35, f"{y}", fontsize=7.5, color=OUTPUT,
                    ha="right" if left else "center", va="bottom")
        halo(t, 2.0)
    g = np.diff(cy["peaks"])
    a1.text(1854, 13.9, T(f"高峰间隔 {g.min()}—{g.max()} 年，平均约 {g.mean():.0f} 年",
                          f"peaks {g.min()}-{g.max()} years apart, mean about {g.mean():.0f}"),
            fontsize=7.6, color=INK, ha="left", va="top")
    a1.set_xlim(1853, 1915)
    a1.set_ylim(0, 14)
    a1.set_xticks([1860, 1880, 1900])
    a1.set_ylabel(T("失业率（%）", "unemployment (%)"))
    _grid(a1)
    _title(a1, T("(a) 有周期，但不整齐", "(a) Cycles, but irregular"))

    shade_periods(a2, cy["recessions"])
    ws, pr = 100 * A.wage_share, 100 * A.profit_rate
    a2.plot(ws.index, ws.values, color=OUTPUT, lw=1.7, zorder=4)
    a3 = _right_axis(a2, AMBER)
    _dashed(a3, pr.index, pr.values, color=AMBER, lw=1.3)
    a2.text(1856, 57.6, T("工资份额（左）", "wage share (left)"), fontsize=7.6, color=OUTPUT, ha="left", va="center")
    a3.text(1913, 30.2, T("利润率代理（右）", "profit proxy (right)"), fontsize=7.6, color=AMBER, ha="right",
            va="center")
    a2.set_xlim(1855, 1913)
    a2.set_ylim(40, 60)
    a2.set_yticks([40, 45, 50, 55, 60])
    a3.set_ylim(10, 32)
    a2.set_xticks([1860, 1880, 1900])
    a2.set_ylabel(T("占 GDP（%）", "% of GDP"))
    a3.set_ylabel(T("利润 / 资本（%）", "profits / capital (%)"), color=AMBER)
    _grid(a2)
    a2.spines["right"].set_visible(False)
    _title(a2, T("(b) 衰退时利润率多半下降", "(b) Profits mostly fall in recessions"))
    return fig
