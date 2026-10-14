"""Figures for Chapter 7 (希腊与罗马：铸币、城邦财政与帝国的贬值).

Style as in fig_ch06.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series, the second series of a panel in AMBER, dashed. Colours follow §7: the silver in the coin
MONEY, prices PRICE, the state's price ceiling FISCAL, quantities OUTPUT. Every number comes from
checks/check_ch07.py, which reads the snapshots greek_facts and kelly_egypt_prices; greek_trust and greek_ceiling
draw the teaching models eq:greek-value and eq:greek-ceiling.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch07 as C  # noqa: E402
from style import (AMBER, FIG_W, FISCAL, INK, LIGHT, MONEY, MUTED, OUTPUT, PRICE, T, clean_axes,  # noqa: E402
                   figure, tint)

DOT = dict(marker="o", ms=5.0, mec="white", mew=0.6)
SQ = dict(marker="s", ms=4.6, mec="white", mew=0.6)
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


def _logy(ax, ticks, labels):
    ax.set_yscale("log")
    ax.set_yticks(ticks)
    ax.set_yticklabels(labels)
    ax.minorticks_off()


# ---------------------------------------------------------------------------
@figure("greek_silver")
def greek_silver():
    F = C.facts()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIG_W, 3.05), gridspec_kw=dict(width_ratios=[1, 1.15], wspace=0.36))

    # (a) fineness: the Roman silver coin (Haklai-Rotenberg, Howgego et al., Cope) and the Egyptian tetradrachm
    t1 = F["hb_t1"]
    rome = [(64, F["hr_nero"][1]), (100, F["hr_nero"][1]), (155, t1[1]), (155, t1[2]), (180, t1[2]), (180, t1[4]),
            (193, t1[4]), (193, C.fineness_unciae(F["cope_severus"][3]))]
    x, y = zip(*rome)
    ax1.plot(x, y, color=MONEY, lw=2.0, zorder=3)
    ax1.plot([64, 155, 180, 193], [F["hr_nero"][1], t1[2], t1[4], C.fineness_unciae(F["cope_severus"][3])],
             ls="none", color=MONEY, zorder=4, **DOT)
    lo, hi = C.fineness_scrupula(F["cope_gallienus"][0]), C.fineness_scrupula(F["cope_animal"][0])
    ax1.plot([193, 265], [C.fineness_unciae(F["cope_severus"][3]), (lo * hi) ** 0.5], color=MONEY, lw=1.0,
             ls=":", zorder=2)
    ax1.plot([265, 265], [lo, hi], color=MONEY, lw=3.2, solid_capstyle="round", zorder=4)
    ax1.plot([274], [F["hr_improved"][2]], color=MONEY, zorder=5, **DOT)
    ax1.annotate("", xy=(274, F["hr_improved"][2] * 0.93), xytext=(274, 2.5),
                 arrowprops=dict(arrowstyle="-|>", color=MONEY, lw=0.9, mutation_scale=8))
    ax1.text(66, 98, T("尼禄 80%", "Nero 80%"), fontsize=7.8, color=MONEY, ha="left", va="bottom")
    ax1.text(197, 46, T("塞维鲁 44%", "Severus 44%"), fontsize=7.8, color=MONEY, ha="left", va="center")
    ax1.text(258, hi * 1.08, T("伽利埃努斯\n1%—2%", "Gallienus\n1%–2%"), fontsize=7.8, color=MONEY, ha="right",
             va="bottom", linespacing=1.2)
    ax1.text(271, F["hr_improved"][2] * 1.25, T("奥勒良\n约 5%", "Aurelian\nc. 5%"), fontsize=7.8, color=MONEY,
             ha="right", va="bottom", linespacing=1.2)
    t2 = F["hb_t2"]
    egy = [(138, t2[1]), (167, t2[1]), (167.5, t2[2]), (169.5, t2[2]), (169.5, t2[3]), (185.5, t2[3]), (192, t2[2])]
    x, y = zip(*egy)
    ax1.plot(x, y, color=AMBER, lw=1.8, ls=(0, (4, 2)), zorder=3)
    ax1.plot([138, 168, 175, 192], [t2[1], t2[2], t2[3], t2[2]], ls="none", color=AMBER, zorder=4, **SQ)
    ax1.text(60, 3.9, T("埃及四德拉克马\n18% → 5%", "Egyptian tetradrachm\n18% → 5%"), fontsize=7.8, color=AMBER,
             ha="left", va="top", linespacing=1.2)
    ax1.set_xlim(50, 300)
    ax1.set_ylim(0.6, 140)
    _logy(ax1, [1, 2, 5, 10, 20, 50, 100], ["1", "2", "5", "10", "20", "50", "100"])
    ax1.set_xticks([50, 100, 150, 200, 250, 300])
    ax1.set_xlabel(T("公元年份", "year AD"), fontsize=9)
    ax1.set_ylabel(T("含银（%，对数）", "silver (%, log)"), fontsize=9)
    _grid(ax1)
    _title(ax1, T("(a) 银从八成降到一两成", "(a) Silver: from 80% to 1–2%"))

    # (b) Egyptian wheat, drachmas per artaba
    P = C.prices()
    w = C.table("wheat_private", P)
    s = C.table("wheat_state", P)
    post = C.table("wheat_post274", P)
    ax2.axvline(274, color=MUTED, lw=0.8, ls=":", zorder=1)
    ax2.axvline(301, color=MUTED, lw=0.8, ls=":", zorder=1)
    ax2.text(270, 2500, T("274 年\n改革", "reform\n274"), fontsize=7.6, color=MUTED, ha="right", va="center",
             linespacing=1.15)
    ax2.text(305, 2.0, T("301 年\n限价令", "edict\n301"), fontsize=7.6, color=MUTED, ha="left", va="center",
             linespacing=1.15)
    ax2.plot(s["year"], s["dr_per_artaba"], ls="none", color=AMBER, zorder=3, **SQ)
    ax2.plot(w["year"], w["dr_per_artaba"], ls="none", color=PRICE, zorder=4, **DOT)
    ax2.plot(post["year"], post["dr_per_artaba"], ls="none", color=PRICE, zorder=4, **DOT)
    ax2.text(60, 40, T("私人价格", "private prices"), fontsize=7.8, color=PRICE, ha="left", va="bottom")
    ax2.text(118, 3.3, T("国家价格", "state prices"), fontsize=7.8, color=AMBER, ha="left", va="top")
    pre = w[w["year"] < 160]["dr_per_artaba"].median()
    mid = w[(w["year"] >= 190) & (w["year"] <= 270)]["dr_per_artaba"].median()
    ax2.plot([45, 139], [pre, pre], color=PRICE, lw=1.0, zorder=2)
    ax2.plot([190, 270], [mid, mid], color=PRICE, lw=1.0, zorder=2)
    ax2.text(92, 17, T(f"中位数 {pre:.2f}", f"median {pre:.2f}"), fontsize=7.6, color=PRICE, ha="center",
             va="bottom")
    ax2.text(205, mid * 2.4, T(f"中位数 {mid:.0f}", f"median {mid:.0f}"), fontsize=7.6, color=PRICE, ha="center",
             va="bottom")
    x340 = post[post["reference"].str.startswith("P.Oxy. LIV 3773")]
    ax2.annotate(T("约 340 年：27 万", "c. 340: 270,000"), xy=(340, x340["dr_per_artaba"].item() * 1.25),
                 xytext=(292, 1.4e6), fontsize=7.6, color=PRICE, ha="right", va="center",
                 arrowprops=dict(arrowstyle="-", color=PRICE, lw=0.6))
    ax2.set_xlim(30, 360)
    ax2.set_ylim(1.5, 3e6)
    _logy(ax2, [1e1, 1e2, 1e3, 1e4, 1e5, 1e6], ["10", "100", "1000", T("1 万", "10⁴"), T("10 万", "10⁵"),
                                                T("100 万", "10⁶")])
    ax2.set_xticks([50, 100, 150, 200, 250, 300, 350])
    ax2.set_xlabel(T("公元年份", "year AD"), fontsize=9)
    ax2.set_ylabel(T("德拉克马 / 阿塔巴（对数）", "drachmas per artaba (log)"), fontsize=9)
    _grid(ax2)
    _title(ax2, T("(b) 小麦价格：先平稳，后暴涨", "(b) Wheat: calm, then a leap"))
    return fig


# ---------------------------------------------------------------------------
@figure("greek_trust")
def greek_trust():
    F = C.facts()
    fig, ax = plt.subplots(figsize=(FIG_W, 2.95))
    x = np.geomspace(0.05, 1.0, 200)                 # c1 / c0, with vbar = c0
    for tau, col, ls, lab, at in ((0.0, PRICE, "-", T("τ = 0：按成色作价", "τ = 0: by content"), (0.115, 7.6)),
                                  (0.3, tint(PRICE, 0.55), (0, (4, 2)), "τ = 0.3", (0.12, 2.75)),
                                  (1.0, MUTED, ":", T("τ = 1：按法定价值作价", "τ = 1: at the official value"),
                                   (0.30, 1.09))):
        v = C.exchange_value(x, 1.0, tau)
        ax.plot(x, 1 / v, color=col, lw=2.0 if tau < 1 else 1.2, ls=ls, zorder=3)
        ax.text(*at, lab, fontsize=7.8, color=col if tau < 1 else MUTED, ha="left", va="bottom")
    c0, c1 = F["hb_t3b"][2], F["hb_t3f"][2]
    r = c1 / c0
    ax.plot([r], [18 / 8.73], color=AMBER, zorder=5, **SQ)
    ax.plot([r], [16 / 8.73], color=AMBER, zorder=5, marker="s", ms=4.6, mfc="white", mec=AMBER, mew=1.0, ls="none")
    ax.annotate(T("192 年：18 ÷ 8.73 = 2.06", "192: 18 ÷ 8.73 = 2.06"), xy=(r, 18 / 8.73), xytext=(0.42, 3.4),
                fontsize=7.8, color=AMBER, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=AMBER, lw=0.6))
    ax.annotate(T("190—270 年中位数：16 ÷ 8.73 = 1.83", "190–270 median: 16 ÷ 8.73 = 1.83"), xy=(r, 16 / 8.73),
                xytext=(0.42, 1.55), fontsize=7.8, color=AMBER, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=AMBER, lw=0.6))
    cn = C.REFORMED / C.REF_FINENESS
    ax.plot([cn], [200 / 16], color=MONEY, zorder=5, **DOT)
    ax.annotate(T("274 年改革后：200 ÷ 16 = 12.5\n（设改革前 τ = 1）", "after 274: 200 ÷ 16 = 12.5\n(τ = 1 before)"),
                xy=(cn, 200 / 16), xytext=(0.62, 15.5), fontsize=7.8, color=MONEY, ha="left", va="center",
                linespacing=1.2, arrowprops=dict(arrowstyle="-", color=MONEY, lw=0.6))
    ax.set_xscale("log")
    ax.set_xlim(1.05, 0.05)
    ax.set_xticks([1, 0.5, 0.26, 0.1, 0.05])
    ax.set_xticklabels(["1", "0.5", "0.26", "0.1", "0.05"])
    ax.set_ylim(0.85, 25)
    _logy(ax, [1, 2, 5, 10, 20], ["1", "2", "5", "10", "20"])
    ax.set_xlabel(T("钱币含银 ÷ 原来的含银 $c_1/c_0$（对数，向右减少）", "silver now ÷ silver before, $c_1/c_0$ (log)"),
                  fontsize=9)
    ax.set_ylabel(T("物价 ÷ 原来的物价（对数）", "price now ÷ price before (log)"), fontsize=9)
    _grid(ax, axis="both")
    _title(ax, T("银少了，物价涨多少取决于信任 τ", "How far prices follow the silver depends on trust τ"))
    return fig


# ---------------------------------------------------------------------------
@figure("greek_ceiling")
def greek_ceiling():
    pi = C.cagr(640, 7000, 13)
    a, b, c0, d = (C.CEIL[k] for k in ("a", "b", "c0", "d"))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIG_W, 2.85), gridspec_kw=dict(width_ratios=[1.05, 1], wspace=0.32))

    q = np.linspace(0, 200, 50)
    ax1.plot(q, a - q / b, color=OUTPUT, lw=2.0, zorder=3)                     # demand: p = (a - Q) / b
    ax1.plot(q, (q - c0) / d, color=AMBER, lw=2.0, ls=(0, (4, 2)), zorder=3)   # supply: p = (Q - c0) / d
    ax1.text(178, a - 178 / b + 6, T("需求", "demand"), fontsize=7.8, color=OUTPUT, ha="center", va="bottom")
    ax1.text(170, 170 / d - 16, T("供给", "supply"), fontsize=7.8, color=AMBER, ha="left", va="top")
    s0, s4 = C.shortage(0, pi), C.shortage(4, pi)
    ax1.axhline(s0["pstar"], color=FISCAL, lw=1.0, ls=":", zorder=2)
    ax1.text(3, s0["pstar"] + 3, T("301 年的限价 100", "ceiling in 301: 100"),
             fontsize=7.6, color=FISCAL, ha="left", va="bottom")
    ax1.plot([0, 200], [s4["real"]] * 2, color=FISCAL, lw=1.8, zorder=4)
    ax1.text(55, s4["real"] - 3, T(f"4 年后只值 {s4['real']:.1f}", f"4 years on: {s4['real']:.1f}"),
             fontsize=7.6, color=FISCAL, ha="left", va="top")
    ax1.fill_between([s4["supply"], s4["demand"]], s4["real"] - 2.2, s4["real"] + 2.2, color=tint(PRICE, 0.35),
                     lw=0, zorder=3)
    ax1.text((s4["supply"] + s4["demand"]) / 2, s4["real"] + 6, T(f"短缺 {s4['x']:.0f}", f"shortage {s4['x']:.0f}"),
             fontsize=7.8, color=PRICE, ha="center", va="bottom", weight="bold")
    ax1.set_xlim(0, 200)
    ax1.set_ylim(0, 205)
    ax1.set_xlabel(T("数量", "quantity"), fontsize=9)
    ax1.set_ylabel(T("价格（301 年的价格水平）", "price (at 301 prices)"), fontsize=9)
    _grid(ax1)
    _title(ax1, T("(a) 物价涨了，名义限价变低了", "(a) Inflation lowers a nominal ceiling"))

    t = np.arange(0, 6)
    sh = [C.shortage(k, pi) for k in t]
    ax2.bar(t, [s["x"] for s in sh], width=0.55, color=tint(PRICE, 0.55), zorder=3)
    ax2.plot(t, [s["supply"] for s in sh], color=AMBER, lw=1.8, ls=(0, (4, 2)), zorder=4, **SQ)
    for k, s in zip(t, sh):
        if k in (1, 4):
            ax2.text(k, s["x"] + 4, f"{s['x']:.1f}", fontsize=7.6, color=PRICE, ha="center", va="bottom")
    ax2.text(0.3, 112, T("短缺", "shortage"), fontsize=7.8, color=PRICE, ha="left", va="center")
    ax2.text(1.25, 90, T("卖出的数量", "quantity sold"), fontsize=7.8, color=AMBER, ha="left", va="bottom")
    ax2.text(5.4, 196, T(f"物价每年涨 {100 * pi:.1f}%\n（埃及小麦，301—314 年）",
                         f"prices up {100 * pi:.1f}% a year\n(Egyptian wheat, 301–314)"),
             fontsize=7.6, color=INK, ha="right", va="top", linespacing=1.25)
    ax2.set_xticks(t)
    ax2.set_xticklabels([str(301 + k) for k in t])
    ax2.set_ylim(0, 205)
    ax2.set_xlabel(T("年份", "year"), fontsize=9)
    ax2.set_ylabel(T("数量", "quantity"), fontsize=9)
    _grid(ax2)
    _title(ax2, T("(b) 限价不动，短缺一年比一年大", "(b) A fixed ceiling bites harder"))
    return fig


# ---------------------------------------------------------------------------
@figure("greek_sectors")
def greek_sectors():
    P = C.prices()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIG_W, 2.85), gridspec_kw=dict(width_ratios=[1.25, 1], wspace=0.30))

    w = C.table("wheat_private", P)
    w = w[(w["year"] >= 190) & (w["year"] <= 270)]
    b = C.table("barley", P)
    b = b[(b["year"] >= 190) & (b["year"] <= 270)]
    tw, tb = C.trend(w), C.trend(b)
    yy = np.linspace(190, 270, 50)
    ax1.plot(w["year"], w["dr_per_artaba"], ls="none", color=PRICE, zorder=4, **DOT)
    ax1.plot(yy, np.exp(tw["fit"].params["Intercept"] + tw["fit"].params["year"] * yy), color=PRICE, lw=1.6,
             zorder=3)
    ax1.plot(b["year"], b["dr_per_artaba"], ls="none", color=AMBER, zorder=4, **SQ)
    ax1.plot(yy, np.exp(tb["fit"].params["Intercept"] + tb["fit"].params["year"] * yy), color=AMBER, lw=1.6,
             ls=(0, (4, 2)), zorder=3)
    ax1.text(192, 33, T(f"小麦（{tw['n']} 份文书）：每年 {_num(100 * tw['b'])}%，p = {tw['p']:.2f}",
                        f"wheat ({tw['n']} documents): {_num(100 * tw['b'])}% a year, p = {tw['p']:.2f}"),
             fontsize=7.6, color=PRICE, ha="left", va="center")
    ax1.text(192, 2.75, T(f"大麦（{tb['n']} 份）：每年 +{100 * tb['b']:.2f}%，p = {tb['p']:.3f}",
                          f"barley ({tb['n']}): +{100 * tb['b']:.2f}% a year, p = {tb['p']:.3f}"),
             fontsize=7.6, color=AMBER, ha="left", va="center")
    ax1.set_xlim(185, 275)
    ax1.set_ylim(2.2, 42)
    _logy(ax1, [3, 5, 10, 20, 30], ["3", "5", "10", "20", "30"])
    ax1.set_xlabel(T("公元年份", "year AD"), fontsize=9)
    ax1.set_ylabel(T("德拉克马 / 阿塔巴（对数）", "drachmas per artaba (log)"), fontsize=9)
    _grid(ax1)
    _title(ax1, T("(a) 190—270 年：小麦不涨，大麦涨", "(a) 190–270: wheat flat, barley up"))

    s = C.table("wheat_state", P)
    v = s["dr_per_artaba"]
    groups = [(v < 8).sum(), (v == 8).sum(), (v > 8).sum()]
    xs = np.arange(3)
    ax2.bar(xs, groups, width=0.6, color=[tint(AMBER, 0.45), AMBER, tint(AMBER, 0.45)], zorder=3)
    for x, n in zip(xs, groups):
        ax2.text(x, n + 0.4, f"{n}", fontsize=8.0, color=AMBER, ha="center", va="bottom", weight="bold")
    lo, hi = v[v < 8], v[v > 8]
    ax2.text(0, groups[0] + 2.4, T(f"{lo.min():.2f}—{lo.max():.2f}", f"{lo.min():.2f}–{lo.max():.2f}"), fontsize=7.6,
             color=MUTED, ha="center", va="bottom")
    ax2.text(2, groups[2] + 2.4, T(f"{hi.min():.2f}—{hi.max():.0f}\n含 246 年强制收购 24", f"{hi.min():.2f}–{hi.max():.0f}\nincl. 24 in 246"),
             fontsize=7.6, color=MUTED, ha="center", va="bottom", linespacing=1.2)
    ax2.set_xticks(xs)
    ax2.set_xticklabels([T("低于 8", "below 8"), T("正好 8", "exactly 8"), T("高于 8", "above 8")])
    ax2.set_yticks([0, 5, 10, 15, 20])
    ax2.set_ylim(0, 23)
    ax2.set_xlabel(T(f"国家价格（{len(v)} 份文书，274 年以前）", f"state prices ({len(v)} documents, before 274)"), fontsize=9)
    ax2.set_ylabel(T("文书数", "documents"), fontsize=9)
    _grid(ax2)
    _title(ax2, T("(b) 国家价格多半是定好的 8", "(b) State prices: mostly a set 8"))
    return fig
