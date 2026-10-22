"""Figures for Chapter 30 (1930 年代的另类出路：纳粹德国、高桥财政与瑞典).

Style as in fig_ch29.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series. Output is OUTPUT, exchange rates EXTERNAL, prices PRICE, the discount rate and the notes
MONEY, government bonds and bills FISCAL; the second series of a panel is AMBER (the bonds the Bank of Japan sold).
In the comparison of six economies the three of the chapter are drawn thick in their own colours and the three
others thin in INSTIT, each with a direct label.
All numbers come from checks/check_ch30.py: the Maddison Project Database (ratios()), the yen in cents from
Banking and Monetary Statistics Table 173 (yen_monthly()), the Bank of Japan's Table 1-17 (boj_sales()), the
Reichsbank's accounts from Table 167 (reichsbank()) and the Riksbank's historical series (cpi1931(), discount()).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch30 as C
from style import (
    AMBER,
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
)

DOT = dict(marker="o", ms=3.2, mec="white", mew=0.5)


def _title(ax, s):
    ax.set_title(s, fontsize=9.0, weight="bold", loc="left", pad=4)


def _grid(ax, axis="y"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


def _t(y: int, m: int) -> float:
    """The middle of a month on a time axis in years."""
    return y + (m - 0.5) / 12


def _day(s: str) -> float:
    """'1938-02-28' -> a point on a time axis in years."""
    y, m, d = (int(v) for v in s.split("-"))
    return y + (m - 1) / 12 + d / 365.25


# the six economies of the figure: names, colour, line width, and the label's offset at 1938 (points of the index)
GDP = {"DEU": (("德国", "Germany"), OUTPUT, 1.9, 1.8),
       "SWE": (("瑞典", "Sweden"), EXTERNAL, 1.9, -0.6),
       "JPN": (("日本", "Japan"), MONEY, 1.9, -0.6),
       "GBR": (("英国", "UK"), INSTIT, 1.0, -2.0),
       "FRA": (("法国", "France"), INSTIT, 1.0, 0.0),
       "USA": (("美国", "US"), INSTIT, 1.0, 0.0)}
THIN = {"GBR": "-", "FRA": (0, (4, 2)), "USA": (0, (1, 1.5))}


@figure("alternatives_gdp")
def alternatives_gdp():
    """GDP per head, 1929 = 100, 1929-1938: Germany, Japan and Sweden thick; the US, the UK and France thin."""
    R = C.ratios()
    assert list(R.index) == C.SIX and set(GDP) == set(C.SIX)
    assert list(R.columns) == list(range(1929, 1939))
    # the troughs the text gives, and the three of the chapter ahead of the three others by 1938
    assert R.loc["DEU"].idxmin() == 1932 and R.loc["JPN"].idxmin() == 1931 and R.loc["SWE"].idxmin() == 1932
    assert R.loc["USA"].idxmin() == 1933
    assert min(R.loc[k, 1938] for k in ("DEU", "JPN", "SWE")) > max(R.loc[k, 1938] for k in ("USA", "GBR", "FRA"))
    fig, ax = plt.subplots(figsize=(FIG_W, 3.2))
    fig.subplots_adjust(left=0.085, right=0.88, top=0.97, bottom=0.14)
    yrs = np.array(R.columns)
    for k, (names, col, lw, dy) in GDP.items():
        thick = lw > 1.5
        ax.plot(yrs, R.loc[k].values, color=col, lw=lw, ls="-" if thick else THIN[k], zorder=5 if thick else 3,
                **(DOT if thick else {}))
        lab = ax.text(yrs[-1] + 0.18, R.loc[k, 1938] + dy, T(*names), color=col, fontsize=7.6, ha="left",
                      va="center", weight="bold" if thick else "normal")
        halo(lab, 2.0)
    ax.axhline(100, color=MUTED, lw=0.6, ls=(0, (1, 2)), zorder=2)
    assert round(R.loc["DEU", 1932], 1) == 83.0 and round(R.loc["USA", 1932], 1) == 70.1
    # the values of 1932 the text gives
    for k, dy, va in (("DEU", -1.6, "top"), ("USA", -1.6, "top")):
        y0 = 1932
        lab = ax.text(y0, R.loc[k, y0] + dy, f"{R.loc[k, y0]:.1f}", color=GDP[k][1], fontsize=7.6, ha="center",
                      va=va)
        halo(lab, 2.0)
    ax.set_xlim(1928.7, 1938.3)
    ax.set_ylim(62, 128)
    ax.set_xticks(range(1929, 1939))
    ax.set_xlabel(T("年份", "year"))
    ax.set_ylabel(T("人均 GDP（1929 年 = 100）", "GDP per head (1929 = 100)"))
    _grid(ax)
    return fig


@figure("alternatives_japan")
def alternatives_japan():
    """(a) The yen in US cents, monthly, 1929-1938, with the gold parity; (b) the long-term government bonds the Bank
    of Japan underwrote and sold, by half-year, November 1932 to December 1936, hundred million yen."""
    F = C.facts()
    Ym = C.yen_monthly()
    par = F["sz_parity"][0]
    x = np.array([_t(y, m) for y, m in Ym.index])
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.95))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.86, bottom=0.15, wspace=0.27)

    lo = Ym.idxmin()
    assert lo == (1932, 11) and Ym[(1931, 11)] > 49
    a1.plot(x, Ym.values, color=EXTERNAL, lw=1.6, zorder=4)
    a1.axhline(par, color=MUTED, lw=0.8, ls=(0, (4, 2)), zorder=2)
    lab = a1.text(1937.9, par + 0.8, T(f"金平价 {par:.1f}", f"gold parity {par:.1f}"), color=MUTED, fontsize=7.6,
                  ha="right", va="bottom")
    halo(lab, 2.0)
    for (y, m), txt, ha in (((1931, 12), T("禁止黄金出口", "gold embargo"), "right"),
                            ((1933, 4), T("美元离开黄金", "dollar off gold"), "left")):
        xv = _t(y, m) - 0.5 / 12
        a1.axvline(xv, color=MUTED, lw=0.6, ls=(0, (1, 2)), zorder=2)
        lab = a1.text(xv + (-0.08 if ha == "right" else 0.08), 15.0, txt, color=MUTED, fontsize=7.6, ha=ha,
                      va="bottom")
        halo(lab, 2.0)
    lab = a1.text(_t(*lo), Ym[lo] - 1.0, f"{Ym[lo]:.1f}", color=EXTERNAL, fontsize=7.6, ha="center", va="top")
    halo(lab, 2.0)
    a1.set_xlim(1929, 1939)
    a1.set_ylim(12, 56)
    a1.set_xticks([1929, 1931, 1933, 1935, 1937])
    a1.set_xlabel(T("年份", "year"))
    a1.set_ylabel(T("一日元合多少美分", "US cents per yen"))
    _grid(a1)
    _title(a1, T("(a) 一年里，日元跌了近六成", "(a) In a year the yen lost nearly 60%"))

    H, total = C.boj_sales()
    u, s = H.underwritten_kyen.values / 1e5, H.sold_kyen.values / 1e5
    assert abs(u[1:7].sum() - total.underwritten_kyen / 1e5) < 1e-9 and abs(s[1:7].sum() - total.sold_kyen / 1e5) < 1e-9
    assert u.argmax() == 7 and s[7] < u[7] / 2                      # 1936 H1: underwritten far more than sold
    i = np.arange(len(H))
    w = 0.38
    a2.bar(i - w / 2, u, w, color=FISCAL, zorder=4, label=T("承购", "underwritten"))
    a2.bar(i + w / 2, s, w, color=AMBER, zorder=4, label=T("卖出", "sold"))
    lab = a2.text(i[7] - w / 2, u[7] + 0.2, f"{u[7]:.1f}", color=FISCAL, fontsize=7.6, ha="center", va="bottom")
    halo(lab, 2.0)
    lab = a2.text(0.2, 11.4, T("承购", "underwritten"), color=FISCAL, fontsize=7.8, ha="left", va="center",
                  weight="bold")
    halo(lab, 2.0)
    lab = a2.text(0.2, 10.2, T("卖给市场", "sold to the market"), color=AMBER, fontsize=7.8, ha="left", va="center",
                  weight="bold")
    halo(lab, 2.0)
    # one tick between years, the year in the middle of its halves (1932 has only November and December)
    years = [int(f[:4]) for f in H["first"]]
    assert years == [1932, 1933, 1933, 1934, 1934, 1935, 1935, 1936, 1936]
    centres = {y: np.mean([k for k, yy in enumerate(years) if yy == y]) for y in sorted(set(years))}
    a2.set_xticks(list(centres.values()))
    a2.set_xticklabels([str(y) for y in centres])
    a2.tick_params(axis="x", length=0)
    for b in (0.5, 2.5, 4.5, 6.5):
        a2.axvline(b, color=LIGHT, lw=0.8, zorder=1)
    a2.set_xlim(-0.6, len(H) - 0.4)
    a2.set_ylim(0, 12.5)
    a2.set_xlabel(T("每半年", "half-years"))
    a2.set_ylabel(T("亿日元", "hundred million yen"))
    _grid(a2)
    _title(a2, T("(b) 1936 年，卖出的跟不上承购的", "(b) In 1936 sales fell behind"))
    return fig


@figure("alternatives_reichsbank")
def alternatives_reichsbank():
    """The Reichsbank at the end of each year 1929-1938 and on 28 February 1938: reserves of gold and foreign
    exchange, bills and checks (with Treasury bills), notes in circulation, hundred million reichsmarks."""
    Rb = C.reichsbank()
    x = np.array([_day(d) for d in Rb.index])
    assert list(Rb.index).index("1938-02-28") == 9 and len(Rb) == 11
    rows = (("reserves_mrm", T("黄金与外汇储备", "gold and foreign exchange"), EXTERNAL, -0.0),
            ("bills_mrm", T("票据与支票（含国库券）", "bills and checks (with Treasury bills)"), FISCAL, 0.0),
            ("notes_mrm", T("流通的银行券", "notes in circulation"), MONEY, 0.0))
    fig, ax = plt.subplots(figsize=(FIG_W, 3.0))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.97, bottom=0.15)
    for col, _, c, _ in rows:
        ax.plot(x, Rb[col].values / 100, color=c, lw=1.6, zorder=4, **DOT)
    # direct labels placed where the three lines are apart
    v = {col: Rb[col] / 100 for col, *_ in rows}
    assert v["bills_mrm"]["1936-12-31"] > v["notes_mrm"]["1936-12-31"] + 4 and v["bills_mrm"]["1933-12-30"] > 30
    assert v["reserves_mrm"]["1934-12-31"] < 1
    lab = ax.text(_day("1933-12-30") + 0.1, v["bills_mrm"]["1933-12-30"] - 4.5, rows[1][1], color=FISCAL, fontsize=7.8,
                  ha="left", va="top")
    halo(lab, 2.0)
    lab = ax.text(_day("1935-12-31"), v["notes_mrm"]["1935-12-31"] - 2.0, rows[2][1], color=MONEY, fontsize=7.8,
                  ha="left", va="top")
    halo(lab, 2.0)
    lab = ax.text(_day("1931-12-31") + 0.15, v["reserves_mrm"]["1931-12-31"] + 0.3, rows[0][1], color=EXTERNAL,
                  fontsize=7.8, ha="left", va="bottom")
    halo(lab, 2.0)
    # the last ten months: 28 February to 31 December 1938
    feb, dec = v["notes_mrm"]["1938-02-28"], v["notes_mrm"]["1938-12-31"]
    lab = ax.text(_day("1938-02-28") + 0.1, feb - 1.5, f"{feb:.1f}", color=MONEY, fontsize=7.6, ha="left",
                  va="top")
    halo(lab, 2.0)
    lab = ax.text(_day("1938-12-31") - 0.12, dec + 0.6, f"{dec:.1f}", color=MONEY, fontsize=7.6, ha="right",
                  va="bottom")
    halo(lab, 2.0)
    lab = ax.text(_day("1938-02-28"), 13.5, T("1938 年\n2 月底", "end Feb\n1938"), color=MUTED, fontsize=7.4,
                  ha="center", va="center", linespacing=1.1)
    halo(lab, 2.0)
    ax.axvline(_day("1938-02-28"), color=MUTED, lw=0.6, ls=(0, (1, 2)), zorder=2, ymin=0.21, ymax=0.86)
    ax.set_xlim(1929.6, 1939.3)
    ax.set_ylim(0, 92)
    ax.set_xticks(range(1930, 1940))
    ax.set_xticklabels([str(y - 1) for y in range(1930, 1940)])
    ax.set_xlabel(T("年底", "end of year"))
    ax.set_ylabel(T("亿帝国马克", "hundred million reichsmarks"))
    _grid(ax)
    return fig


@figure("alternatives_sweden")
def alternatives_sweden():
    """(a) Sweden's consumer price index, annual, 1931 = 100, 1925-1939; (b) the Riksbank's discount rate, monthly,
    1929-1939, as steps."""
    P = C.cpi1931()
    D = C.discount()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.85))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.86, bottom=0.15, wspace=0.27)

    yrs = np.array(P.index)
    assert yrs[0] == 1925 and yrs[-1] == 1939 and P[1931] == 100
    assert P.loc[1931:1936].max() - P.loc[1931:1936].min() < 4
    a1.axvspan(1930.5, 1936.5, color=LIGHT, lw=0, zorder=1)
    a1.plot(yrs, P.values, color=PRICE, lw=1.6, zorder=4, **DOT)
    a1.axhline(100, color=MUTED, lw=0.6, ls=(0, (1, 2)), zorder=2)
    lab = a1.text(1933.5, 113.0, T("1931—1936 年", "1931-1936"), color=MUTED, fontsize=7.6, ha="center",
                  va="center")
    halo(lab, 2.0)
    k = P.loc[1931:1936].idxmin()
    lab = a1.text(k, P[k] - 0.8, f"{P[k]:.1f}", color=PRICE, fontsize=7.6, ha="center", va="top")
    halo(lab, 2.0)
    a1.set_xlim(1924.5, 1939.5)
    a1.set_ylim(92, 116)
    a1.set_xticks([1925, 1929, 1933, 1937])
    a1.set_ylabel(T("消费物价（1931 年 = 100）", "consumer prices (1931 = 100)"))
    _grid(a1)
    _title(a1, T("(a) 1931 年以后，物价大致不变", "(a) After 1931 prices held steady"))

    months = [C.ym(m) for m in D.index]
    xs = [y + (m - 1) / 12 for y, m in months] + [1940.0]
    ys = list(D.values) + [D.values[-1]]
    top = D.idxmax()
    assert top == "1931-09" and D[top] == 8 and D["1933-12"] == 2.5 and D["1939-11"] == 2.5
    a2.step(xs, ys, where="post", color=MONEY, lw=1.6, zorder=4)
    lab = a2.text(1931 + 9 / 12 + 0.15, 8.0, T("1931 年 9 月：8%", "Sep 1931: 8%"), color=MONEY, fontsize=7.6,
                  ha="left", va="center")
    halo(lab, 2.0)
    lab = a2.text(1936.5, 2.5 + 0.35, "2.5%", color=MONEY, fontsize=7.6, ha="center", va="bottom")
    halo(lab, 2.0)
    a2.set_xlim(1929, 1940)
    a2.set_ylim(0, 9.5)
    a2.set_xticks([1929, 1931, 1933, 1935, 1937, 1939])
    a2.set_ylabel(T("贴现率（%）", "discount rate (%)"))
    _grid(a2)
    _title(a2, T("(b) 贴现率 1933 年底降到 2.5%", "(b) Down to 2.5% by end-1933"))
    for ax in (a1, a2):
        ax.set_xlabel(T("年份", "year"))
    return fig
