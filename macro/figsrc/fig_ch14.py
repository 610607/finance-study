"""Figures for Chapter 14 (非洲与美洲：黄金、贝币与没有货币的帝国).

Style as in fig_ch13.py (docs/STYLE.md §7.1): bold "(a) …" panel titles that state the point, direct labels in
the colour of their series, a second series in AMBER.  All numbers come from checks/check_ch14.py, which reads the
snapshot africa_money_facts; inca_store is a teaching model whose inputs are stated in the text.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import NullFormatter

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch14 as C  # noqa: E402
from style import (AMBER, FIG_W, INK, LIGHT, MONEY, MUTED, OUTPUT, PRICE, T,  # noqa: E402
                   clean_axes, figure, halo, tint)


def _title(ax, s):
    ax.set_title(s, fontsize=8.8, weight="bold", loc="left", pad=4)


def _grid(ax, axis="both"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


def _n(v: float) -> str:
    """Thousands separator as printed in the text."""
    return f"{v:,.0f}"


# ---------------------------------------------------------------------------
@figure("cowrie_value")
def cowrie_value():
    """(a) cowries for a unit of gold, Maldives to Kano; (b) cowries for a shilling, 1720-1894."""
    F = C.facts()
    names = {"maldives": T("马尔代夫", "Maldives"), "mali": T("马里与加奥", "Mali and Gao"),
             "timbuktu": T("廷巴克图", "Timbuktu"), "kano": T("卡诺", "Kano")}
    rows = C.per_gold(F)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.9), gridspec_kw=dict(width_ratios=[1.0, 1.12]))
    fig.subplots_adjust(left=0.135, right=0.985, top=0.89, bottom=0.17, wspace=0.36)

    h = 0.56
    for i, (place, year, lo, hi) in enumerate(rows):
        a1.barh(i, lo, height=h, color=MONEY, lw=0, zorder=2)
        if hi > lo:
            a1.barh(i, hi - lo, left=lo, height=h, color=tint(MONEY, 0.5), lw=0, zorder=2)
        txt = _n(lo) if hi == lo else T(f"{_n(lo)}—{_n(hi)}", f"{_n(lo)}–{_n(hi)}")
        if place == "maldives":
            a1.text(lo / 1.25, i, txt, fontsize=7.4, color="white", ha="right", va="center", zorder=4)
        else:
            a1.text(hi * 1.25, i, txt, fontsize=7.6, color=MONEY, ha="left", va="center")
    a1.set_xscale("log")
    a1.set_xlim(300, 3e6)
    a1.set_xticks([1e3, 1e4, 1e5, 1e6])
    a1.set_xticklabels(["1,000", T("1 万", "10,000"), T("10 万", "100,000"), T("100 万", "1 m")])
    a1.xaxis.set_minor_formatter(NullFormatter())
    a1.set_yticks(range(len(rows)))
    a1.set_yticklabels([f"{names[r[0]]} {r[1]}" for r in rows], fontsize=7.8)
    a1.set_ylim(len(rows) - 0.4, -0.6)
    a1.set_xlabel(T("一第纳尔或一米斯卡勒金换几枚贝壳（对数）", "cowries per dinar or mithqal of gold (log)"))
    lo_r = F["battuta_four_bostu"][0] / F["battuta_mali_1150"][0]
    hi_r = F["battuta_twelve_bostu"][0] / F["battuta_mali_1150"][0]
    a1.text(2.8e6, 2.5, T(f"马里的一枚贝壳\n值马尔代夫的\n{lo_r:.0f}—{hi_r:,.0f} 倍", f"a shell in Mali was\nworth {lo_r:.0f}–{hi_r:,.0f}×\nits Maldives value"),
            fontsize=7.4, color=INK, ha="right", va="center", linespacing=1.3)
    _grid(a1, axis="x")
    _title(a1, T("(a) 离产地越远，贝壳越值钱", "(a) the farther from the Maldives, the dearer"))

    pts = C.per_shilling(F)
    lab = {"coast": T("西非海岸", "West African coast"), "jf": T("维达（J. F.）", "Whydah (J. F.)"),
           "whydah": T("维达", "Whydah"), "lagos": T("拉各斯", "Lagos"), "kaffi": T("卡菲", "Kaffi"),
           "lokoja": T("洛科贾", "Lokoja"), "zaria": T("扎里亚", "Zaria"), "kano": T("卡诺", "Kano")}
    side = {"lokoja": 2200, "kaffi": 1800, "zaria": 1470, "kano": 1200}
    for place, year, v in pts:
        a2.plot(year, v, "o", color=PRICE, ms=5, zorder=4)
        txt = f"{lab[place]} {_n(v)}"
        if place in side:
            a2.annotate(txt, (year, v), xytext=(1899, side[place]), fontsize=7.2, color=PRICE, ha="left",
                        va="center", arrowprops=dict(arrowstyle="-", color=PRICE, lw=0.6, shrinkA=0, shrinkB=2.5))
        elif place in ("whydah", "lagos"):
            halo(a2.annotate(txt, (year, v), xytext=(-6, 0), textcoords="offset points", fontsize=7.2, color=PRICE,
                             ha="right", va="center", zorder=5))
        else:
            a2.annotate(txt, (year, v), xytext=(6, -1), textcoords="offset points", fontsize=7.2, color=PRICE,
                        ha="left", va="center")
    p0 = dict((p, (y, v)) for p, y, v in pts)
    (y0, v0), (y1, v1) = p0["coast"], p0["lokoja"]
    g = C.compound(v1 / v0, y1 - y0)
    yy = np.linspace(y0, y1, 50)
    a2.plot(yy, v0 * (1 + g) ** (yy - y0), color=MUTED, lw=0.8, ls=(0, (1, 2)), zorder=2)
    a2.text(1872, 560, T(f"1720—1894 年\n年均 {100 * g:.2f}%", f"1720–1894:\n{100 * g:.2f}% a year"), fontsize=7.4,
            color=MUTED, ha="center", va="center", linespacing=1.25)
    a2.set_yscale("log")
    a2.set_ylim(130, 4000)
    a2.set_yticks([200, 500, 1000, 2000])
    a2.set_yticklabels(["200", "500", "1,000", "2,000"])
    a2.yaxis.set_minor_formatter(NullFormatter())
    a2.set_xlim(1705, 1945)
    a2.set_xticks([1720, 1760, 1800, 1840, 1880])
    a2.set_ylabel(T("一先令换几枚贝壳（对数）", "cowries per shilling (log)"))
    _grid(a2)
    _title(a2, T("(b) 一先令换的贝壳越来越多", "(b) more and more shells to the shilling"))
    return fig


# ---------------------------------------------------------------------------
@figure("carry_cost")
def carry_cost():
    """(a) salt at Iwalatan and Mali, 1352; (b) Robinson's carrying costs against the price gaps, 1894."""
    F = C.facts()
    lo_w, hi_w, lo_m, hi_m, top = F["battuta_salt_price"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.65), gridspec_kw=dict(width_ratios=[0.8, 1.2]))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.88, bottom=0.2, wspace=0.62)

    w = 0.5
    a1.bar(0, hi_w - lo_w, bottom=lo_w, width=w, color=PRICE, lw=0, zorder=2)
    a1.bar(1, hi_m - lo_m, bottom=lo_m, width=w, color=PRICE, lw=0, zorder=2)
    a1.bar(1, top - hi_m, bottom=hi_m, width=w, color="white", ec=PRICE, lw=1.0, ls=(0, (3, 2)), zorder=2)
    a1.text(0, hi_w + 1.2, T(f"{lo_w:g}—{hi_w:g}", f"{lo_w:g}–{hi_w:g}"), fontsize=7.8, color=PRICE, ha="center",
            va="bottom")
    a1.text(1 + w / 2 + 0.06, (lo_m + hi_m) / 2, T(f"{lo_m:g}—{hi_m:g}", f"{lo_m:g}–{hi_m:g}"), fontsize=7.8,
            color=PRICE, ha="left", va="center")
    a1.text(1, top + 0.8, T(f"有时 {top:g}", f"at times {top:g}"), fontsize=7.4, color=PRICE, ha="center",
            va="bottom")
    a1.set_xticks([0, 1])
    a1.set_xticklabels([T("伊瓦拉坦", "Iwalatan"), T("马里城", "Mali")], fontsize=8.0)
    a1.set_xlim(-0.55, 1.9)
    a1.set_ylim(0, 46)
    a1.set_ylabel(T("一驮盐卖几个金米斯卡勒", "mithqals of gold per camel load"))
    _grid(a1, axis="y")
    _title(a1, T("(a) 盐：马里贵到 2—3.75 倍", "(a) salt: 2–3.75× dearer in Mali"))

    c = C.carry(F)
    rows = [(T("扎里亚比洛科贾贵", "Zaria over Lokoja"), c["gap_zaria"], PRICE),
            (T("卡诺比洛科贾贵", "Kano over Lokoja"), c["gap_kano"], PRICE),
            (T(f"脚夫 {c['days']:.0f} 天的工钱", f"porter, {c['days']:.0f} days"), c["fee4"], AMBER),
            (T(f"运到扎里亚（{c['miles']:.0f} 英里）", f"to Zaria, {c['miles']:.0f} miles"), c["zaria"], AMBER)]
    for i, (name, v, col) in enumerate(rows):
        a2.barh(i, 100 * v, height=0.56, color=col, lw=0, zorder=2)
        a2.text(100 * v + 2, i, f"{100 * v:.0f}%", fontsize=7.8, color=col, ha="left", va="center")
    a2.set_yticks(range(len(rows)))
    a2.set_yticklabels([r[0] for r in rows], fontsize=7.6)
    a2.invert_yaxis()
    a2.set_xlim(0, 118)
    a2.set_xlabel(T("占一担 95 磅贝壳价值的比例（%）", "share of the value of a 95 lb load (%)"))
    a2.text(116, 0.5, T("价差", "price gap"), fontsize=7.6, color=PRICE, ha="right", va="center", weight="bold")
    a2.text(116, 2.5, T("运费", "carrying cost"), fontsize=7.6, color=AMBER, ha="right", va="center",
            weight="bold")
    _grid(a2, axis="x")
    _title(a2, T("(b) 贝币：运费大于价差", "(b) cowries: the carry costs more than the gap"))
    return fig


# ---------------------------------------------------------------------------
@figure("inca_store")
def inca_store():
    """Teaching model eq:africa-store: storehouse stocks for two loss rates, a famine in year 30."""
    T_ = 50
    sd, _ = C.store_path(C.DELTA_DRY, T_, famine=C.FAMINE)
    sf, short = C.store_path(C.DELTA_FRESH, T_, famine=C.FAMINE)
    t = np.arange(T_ + 1)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.75), gridspec_kw=dict(width_ratios=[1.35, 1]))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.89, bottom=0.17, wspace=0.3)

    a1.plot(t, sd, color=OUTPUT, lw=2.0, zorder=3)
    a1.plot(t, sf, color=AMBER, lw=2.0, dashes=(4, 2), zorder=3)
    for d, col in ((C.DELTA_DRY, OUTPUT), (C.DELTA_FRESH, AMBER)):
        a1.axhline(C.store_star(d), color=col, lw=0.7, ls=(0, (1, 2)), zorder=1)
    a1.text(1, C.store_star(C.DELTA_DRY) + 2, T(f"$S^*$ = {C.store_star(C.DELTA_DRY):.0f}", f"$S^*$ = {C.store_star(C.DELTA_DRY):.0f}"),
            fontsize=7.4, color=OUTPUT, ha="left", va="bottom")
    a1.text(14, C.store_star(C.DELTA_FRESH) - 2.5, f"$S^*$ = {C.store_star(C.DELTA_FRESH):.0f}", fontsize=7.4,
            color=AMBER, ha="left", va="top")
    a1.text(49, 84, T(f"不易坏，$\\delta$ = {100 * C.DELTA_DRY:.0f}%", f"keeps well, $\\delta$ = {100 * C.DELTA_DRY:.0f}%"),
            fontsize=7.6, color=OUTPUT, ha="right", va="bottom")
    a1.text(47, 25, T(f"易坏，$\\delta$ = {100 * C.DELTA_FRESH:.0f}%", f"keeps badly, $\\delta$ = {100 * C.DELTA_FRESH:.0f}%"),
            fontsize=7.6, color=AMBER, ha="right", va="bottom")
    a1.axvline(C.FAMINE_YEAR, color=MUTED, lw=0.7, ls=(0, (1, 2)))
    a1.text(C.FAMINE_YEAR + 0.6, 112, T(f"第 {C.FAMINE_YEAR} 年饥荒，\n多用 {C.FAMINE:.0f}", f"famine in year {C.FAMINE_YEAR}:\nextra use {C.FAMINE:.0f}"),
            fontsize=7.4, color=INK, ha="left", va="top", linespacing=1.25)
    a1.annotate(T(f"缺 {short:.0f}", f"short by {short:.0f}"), (C.FAMINE_YEAR, 0), xytext=(C.FAMINE_YEAR + 6.5, 3),
                fontsize=7.4, color=AMBER, ha="left", va="bottom",
                arrowprops=dict(arrowstyle="-", color=AMBER, lw=0.7))
    a1.set_xlim(0, 50)
    a1.set_ylim(0, 118)
    a1.set_xlabel(T("建仓以后的年数", "years after the storehouses are built"))
    a1.set_ylabel(T("库存（一年消费 = 100）", "stock (a year's consumption = 100)"))
    _grid(a1)
    _title(a1, T("(a) 越不容易坏，存得越多", "(a) the better it keeps, the more is stored"))

    d = np.linspace(0.02, 0.4, 200)
    months = 12 * C.store_star(d) / 100
    a2.plot(100 * d, months, color=OUTPUT, lw=2.0, zorder=3)
    for dd, col in ((C.DELTA_DRY, OUTPUT), (C.DELTA_FRESH, AMBER)):
        m = 12 * C.store_star(dd) / 100
        a2.plot(100 * dd, m, "o", color=col, ms=5.5, zorder=4)
        a2.text(100 * dd + 1.5, m + 0.6, T(f"{m:g} 个月", f"{m:g} months"), fontsize=7.6, color=col,
                ha="left", va="bottom")
    a2.set_xlim(0, 40)
    a2.set_ylim(0, 32)
    a2.set_xlabel(T("每年损耗 $\\delta$（%）", "loss a year, $\\delta$ (%)"))
    a2.set_ylabel(T("稳态库存够吃几个月", "steady-state stock, months"))
    _grid(a2)
    _title(a2, T("(b) 稳态库存与损耗率", "(b) steady-state stock and loss"))
    return fig
