"""Figures for Chapter 13 (白银的世纪：波托西、马尼拉与价格革命).

Style as in fig_ch11.py (docs/STYLE.md §7.1): bold "(a) …" panel titles that state the point, direct
labels in the colour of their series, a second series in AMBER and dashed.  All numbers come from
checks/check_ch13.py, which reads the snapshots silver_century_facts, hamilton1929_treasure,
quan1969_manila_silver, boe_millennium_england_money, gpih_silver_pound, gpih_allen_silver_cpi,
dv2010_castile_annual and dv2010_philip2.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch13 as C  # noqa: E402
from style import (AMBER, FIG_W, FISCAL, INK, INSTIT, LIGHT, MONEY, MUTED, PRICE, T,  # noqa: E402
                   clean_axes, figure, tint)


def _title(ax, s):
    ax.set_title(s, fontsize=8.8, weight="bold", loc="left", pad=4)


def _grid(ax):
    clean_axes(ax)
    ax.grid(True, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


# ---------------------------------------------------------------------------
@figure("silver_flows")
def silver_flows():
    """(a) Hamilton's Table A as shares of 1503-1660; (b) Quan's estimates of the silver sent to Manila."""
    H = C.hamilton()
    F = C.facts()
    M = C.manila()
    M = M[(M["year"] >= 1598) & (M["year"] <= 1700)]
    cap = F["quan1969_cap"][0]

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.85), gridspec_kw=dict(width_ratios=[1.15, 1]))
    fig.subplots_adjust(left=0.075, right=0.985, top=0.89, bottom=0.17, wspace=0.27)

    mid = (H["first"] + H["last"]) / 2 + 0.5
    width = H["years"] - 1.2
    early = H["last"] <= 1550
    a1.bar(mid[early], 100 * H["share"][early], width=width[early], color=tint(MONEY, 0.45), lw=0, zorder=2)
    a1.bar(mid[~early], 100 * H["share"][~early], width=width[~early], color=MONEY, lw=0, zorder=2)
    before = 100 * H.loc[early, "share"].sum()
    peak = H.loc[H["share"].idxmax()]
    a1.text(1505, 3.2, T(f"1550 年以前\n合计 {before:.1f}%", f"before 1550\n{before:.1f}% in all"), fontsize=7.4,
            color=tint(MONEY, 0.6), ha="left", va="bottom", linespacing=1.25)
    a1.text(peak["first"] - 1.5, 100 * peak["share"] + 0.3,
            T(f"1591—1600：{100 * peak['share']:.1f}%", f"1591–1600: {100 * peak['share']:.1f}%"),
            fontsize=7.4, color=MONEY, ha="center", va="bottom")
    a1.axvline(1545, color=MUTED, lw=0.7, ls=(0, (1, 2)))
    a1.text(1546, 13.2, T("1545\n波托西", "1545\nPotosí"), fontsize=7.2, color=MUTED, ha="left", va="top",
            linespacing=1.2)
    a1.set_xlim(1500, 1663)
    a1.set_ylim(0, 17.5)
    a1.set_xticks([1500, 1550, 1600, 1650])
    a1.set_ylabel(T("占 1503—1660 年总数（%）", "share of 1503–1660 (%)"))
    _title(a1, T("(a) 运到塞维利亚：1550 年以后才多", "(a) to Seville: large only after 1550"))

    a2.plot([1593, 1700], [cap / 1e6] * 2, color=INSTIT, lw=1.2, ls=(0, (4, 2)))
    a2.text(1699, cap / 1e6 + 0.12, T("1593、1595 年敕令的上限 50 万", "legal cap of 1593/95: 0.5 m"),
            fontsize=7.2, color=INSTIT, ha="right", va="bottom")
    for _, r in M.iterrows():
        lo, hi = r["low_pesos"] / 1e6, r["high_pesos"] / 1e6
        if hi > lo:
            a2.plot([r["year"]] * 2, [lo, hi], color=MONEY, lw=1.4)
        filled = r["plus"] == 0
        a2.plot([r["year"]], [lo], "o", ms=5.2, color=MONEY, mfc=MONEY if filled else "white", mew=1.3)
    a2.annotate(T("“250 万以上”", "“over 2.5 m”"), xy=(1604, 2.5), xytext=(1609, 1.55), fontsize=7.2, color=MONEY,
                ha="left", va="center", arrowprops=dict(arrowstyle="-", color=MONEY, lw=0.6))
    a2.text(1601.8, 1.0, T("1598 年大主教的信", "1598 letter of the archbishop"), fontsize=7.0, color=MONEY,
            ha="left", va="center")
    a2.set_xlim(1590, 1705)
    a2.set_ylim(0, 4.0)
    a2.set_xticks([1600, 1650, 1700])
    a2.set_ylabel(T("每年百万比索", "million pesos a year"))
    _title(a2, T("(b) 运往马尼拉：远超上限", "(b) to Manila: far above the cap"))
    for ax in (a1, a2):
        _grid(ax)
    return fig


# ---------------------------------------------------------------------------
@figure("gold_silver_ratio")
def gold_silver_ratio():
    """Gold-silver ratios by weight: Ming official 5, Canton 6.6-7, Japan 8.3, Europe 11.3 and 13.9."""
    F = C.facts()
    fine, common, japan = F["br19_gold"]
    eu16, eu17 = F["em_barrett"]
    ming = F["ming_1397_gold"][0] / F["ming_1397_silver"][0]
    rows = [(T("明朝官定（1397）", "Ming, official (1397)"), ming, None),
            (T("广州（17 世纪初）", "Canton (early 17th c.)"), fine, common),
            (T("日本（17 世纪初）", "Japan (early 17th c.)"), japan, None),
            (T("欧洲，16 世纪", "Europe, 16th c."), eu16, None),
            (T("欧洲，17 世纪", "Europe, 17th c."), eu17, None)]

    fig, ax = plt.subplots(figsize=(FIG_W, 2.45))
    fig.subplots_adjust(left=0.215, right=0.97, top=0.97, bottom=0.18)
    h = 0.58
    for i, (name, v, hi) in enumerate(rows):
        if i == 0:
            ax.add_patch(Rectangle((0, i - h / 2), v, h, fill=False, ec=INSTIT, lw=1.2, ls=(0, (3, 2)), zorder=3))
            ax.text(v + 0.2, i, T(f"{v:g}（官定折价，不是市场价格）", f"{v:g} (official rate, not a market price)"),
                    fontsize=7.6, color=INSTIT, ha="left", va="center")
            continue
        ax.barh(i, v, height=h, color=MONEY, lw=0, zorder=2)
        if hi is not None:
            ax.barh(i, hi - v, left=v, height=h, color=tint(MONEY, 0.5), lw=0, zorder=2)
            ax.text(hi + 0.2, i, T(f"{v:g}—{hi:g}", f"{v:g}–{hi:g}"), fontsize=7.8,
                    color=MONEY, ha="left", va="center")
        else:
            ax.text(v + 0.2, i, f"{v:g}", fontsize=7.8, color=MONEY, ha="left", va="center")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows], fontsize=8.0)
    ax.set_xlim(0, 15.5)
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.set_xlabel(T("一份黄金换多少份白银（按重量）", "units of silver per unit of gold, by weight"))
    ax.text(15.3, -0.05, T("比价越低，\n白银越贵", "the lower the ratio,\nthe dearer silver"), fontsize=7.4,
            color=INK, ha="right", va="center", linespacing=1.25)
    clean_axes(ax)
    ax.grid(True, axis="x", color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    return fig


# ---------------------------------------------------------------------------
@figure("price_revolution")
def price_revolution():
    """(a) England: coin, prices in pounds and in silver, decade means, 1500s = 100; (b) Allen's silver CPI."""
    E = C.england().loc[1490:1690]
    x = E.index.to_numpy() + 5
    idx = {c: 100 * E[c] / E.loc[1500, c] for c in ("M", "P", "P_ag")}
    A = C.allen().loc[1490:1690]
    xa = A.index.to_numpy() + 5

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.95))
    fig.subplots_adjust(left=0.075, right=0.985, top=0.89, bottom=0.16, wspace=0.27)

    a1.axvspan(1540, 1560, color=tint(INSTIT, 0.12), lw=0, zorder=0)
    a1.plot(x, idx["M"], "-o", color=MONEY, lw=1.8, ms=3.2)
    a1.plot(x, idx["P"], "-o", color=PRICE, lw=2.0, ms=3.2)
    a1.plot(x, idx["P_ag"], "-s", color=AMBER, lw=1.6, ms=3.0, dashes=(4, 2))
    a1.text(1640, 1480, T("铸币存量", "coin"), fontsize=7.6, color=MONEY, ha="right", va="bottom")
    a1.text(1690, 520, T("物价（英镑）", "prices (£)"), fontsize=7.6, color=PRICE, ha="right", va="bottom")
    a1.text(1690, 250, T("物价（白银）", "prices (silver)"), fontsize=7.6, color=AMBER, ha="right", va="top")
    a1.text(1550, 70, T("大贬值", "Great\nDebasement"), fontsize=7.0, color=INSTIT, ha="center", va="bottom",
            linespacing=1.15)
    a1.set_yscale("log")
    a1.set_ylim(60, 2200)
    a1.set_yticks([100, 200, 500, 1000, 2000])
    a1.set_yticklabels(["100", "200", "500", "1000", "2000"])
    a1.minorticks_off()
    a1.set_ylabel(T("1500 年代 = 100（对数）", "1500s = 100 (log)"))
    _title(a1, T("(a) 英格兰：货币涨得比物价快", "(a) England: money rose faster"))

    style = {"valencia": (PRICE, 2.0, "-", T("瓦伦西亚", "Valencia")),
             "paris": (MONEY, 1.3, "-", T("巴黎", "Paris")),
             "london": (INSTIT, 1.3, "-", T("伦敦", "London")),
             "florence": (AMBER, 1.3, (0, (4, 2)), T("佛罗伦萨", "Florence")),
             "krakow": (MUTED, 1.3, (0, (1.5, 1.5)), T("克拉科夫", "Krakow"))}
    ends = {"paris": 1.80, "london": 1.40, "florence": 1.00, "krakow": 0.50}
    for city, (col, lw, ls, name) in style.items():
        a2.plot(xa, A[city], color=col, lw=lw, ls=ls)
        if city in ends:
            a2.text(1697, ends[city], name, fontsize=7.4, color=col, ha="left", va="center")
    a2.text(1645, 2.3, style["valencia"][3], fontsize=7.6, color=PRICE, ha="center", va="bottom")
    a2.set_yscale("log")
    a2.set_ylim(0.3, 2.6)
    a2.set_yticks([0.3, 0.5, 1, 2])
    a2.set_yticklabels(["0.3", "0.5", "1", "2"])
    a2.minorticks_off()
    a2.set_xlim(1490, 1740)
    a2.set_ylabel(T("Allen 指数（白银计，对数）", "Allen index (silver, log)"))
    _title(a2, T("(b) 以白银计：西班牙高，克拉科夫低", "(b) in silver: Spain high, Krakow low"))
    for ax in (a1, a2):
        _grid(ax)
        ax.set_xticks([1500, 1550, 1600, 1650, 1700])
        ax.tick_params(labelsize=8.0)
    a1.set_xlim(1490, 1700)
    return fig


# ---------------------------------------------------------------------------
@figure("philip_debt")
def philip_debt():
    """(a) Castile's revenue and the Indies, 1566-1596; (b) debt/revenue against D* = PS/(r-g)."""
    D = C.castile()
    T3 = C.table3()
    years = D.index.to_numpy()

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.85))
    fig.subplots_adjust(left=0.075, right=0.985, top=0.89, bottom=0.16, wspace=0.27)

    for y in (1575, 1596):
        for ax in (a1, a2):
            ax.axvline(y, color=PRICE, lw=0.9, ls=(0, (1.5, 1.5)), zorder=1)
    a1.plot(years, D["revenue"], "-o", color=FISCAL, lw=2.0, ms=3.0)
    a1.plot(years, D["indies"], "-s", color=AMBER, lw=1.5, ms=2.8, dashes=(4, 2))
    a1.text(1567, 6.6, T("全部收入", "revenue"), fontsize=7.6, color=FISCAL, ha="left", va="bottom")
    a1.text(1567, 2.2, T("白银收入", "silver"), fontsize=7.6, color=AMBER, ha="left", va="bottom")
    a1.text(1575.4, 16.8, T("1575 停付", "1575 default"), fontsize=7.2, color=PRICE, ha="left", va="top")
    a1.text(1595.6, 16.8, T("1596 停付", "1596 default"), fontsize=7.2, color=PRICE, ha="right", va="top")
    a1.set_ylim(0, 17)
    a1.set_ylabel(T("百万杜卡特", "million ducats"))
    _title(a1, T("(a) 白银收入的低谷之后是停付", "(a) silver dips before the defaults"))

    a2.plot(years, D["debt_ratio"], "-o", color=FISCAL, lw=2.0, ms=3.0)
    for period, (y0, y1) in {"1565-74": (1566, 1574), "1574-84": (1574, 1584), "1584-96": (1584, 1596)}.items():
        a2.plot([y0, y1], [T3.loc[period, "D_star"]] * 2, color=AMBER, lw=1.6, ls=(0, (4, 2)))
    a2.text(1575.7, T3.loc["1574-84", "D_star"] - 0.15, T("可维持的 $D^{*}$", "sustainable $D^{*}$"), fontsize=7.6,
            color=AMBER, ha="left", va="top")
    a2.text(1565.4, 6.45, T("债务 / 收入", "debt /\nrevenue"), fontsize=7.6, color=FISCAL, ha="left", va="bottom",
            linespacing=1.15)
    for y in (1574, 1594):
        v = D.loc[y, "debt_ratio"]
        a2.annotate(f"{v:.1f}", xy=(y, v), xytext=(y - 2.2, v + 0.35), fontsize=7.4, color=FISCAL, ha="center",
                    arrowprops=dict(arrowstyle="-", color=FISCAL, lw=0.6))
    a2.set_ylim(2, 9.3)
    a2.set_ylabel(T("收入的倍数", "times revenue"))
    _title(a2, T("(b) 债务围绕可维持的水平", "(b) debt around its sustainable level"))
    for ax in (a1, a2):
        _grid(ax)
        ax.set_xlim(1565, 1597.5)
        ax.set_xticks([1566, 1575, 1585, 1596])
        ax.tick_params(labelsize=8.0)
    return fig
