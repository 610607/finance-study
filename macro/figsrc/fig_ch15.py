"""Figures for Chapter 15 (早期金融革命：荷兰、英国与可信的国债).

Style as in fig_ch13.py (docs/STYLE.md §7.1): bold "(a) …" panel titles that state the point, direct labels in
the colour of their series.  All numbers come from checks/check_ch15.py, which reads the snapshots finrev_facts,
gj2011_holland_debt, boe_millennium_england_debt and dv2010_philip2; agio_band draws eq:finrev-agio with the
statutory values of Quinn and Roberds' Table 5.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch15 as C  # noqa: E402
from style import (AMBER, FIG_W, FISCAL, INK, LIGHT, MONEY, MUTED, OUTPUT, PRICE, T,  # noqa: E402
                   clean_axes, figure, halo, tint)


def _title(ax, s):
    ax.set_title(s, fontsize=8.8, weight="bold", loc="left", pad=4)


def _grid(ax, axis="both"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


def _pct(v: float) -> str:
    return f"{v:.2f}%"


# ---------------------------------------------------------------------------
@figure("agio_band")
def agio_band():
    """eq:finrev-agio: no-arbitrage agio bands of the dukaat and the rijder against the withdrawal fee."""
    F = C.facts()
    ws = np.linspace(0.0, 2.0, 201)
    bands = C.agio_curves(F, ws)
    w15, w025 = F["qr_t5_w15"][0], F["qr_t5_w025"][0]
    pre, post = F["qr_t3_agio_pre"][0], F["qr_t3_agio_post"][0]
    fig, ax = plt.subplots(figsize=(FIG_W, 2.85))
    fig.subplots_adjust(left=0.1, right=0.975, top=0.9, bottom=0.16)

    for coin, col, dash in (("dukaat", MONEY, None), ("rijder", AMBER, (4, 2))):
        lo = np.array([b[0] for b in bands[coin]])
        hi = np.array([b[1] for b in bands[coin]])
        ax.fill_between(ws, lo, hi, color=tint(col, 0.62), lw=0, alpha=0.75, zorder=2)
        for edge in (lo, hi):
            line, = ax.plot(ws, edge, color=col, lw=1.2, zorder=3)
            if dash:
                line.set_dashes(dash)
    a_d, a_r = bands["dukaat"][0][1], bands["rijder"][0][1]
    ax.text(1.98, a_d + 0.06, T(f"达克特银币：法定升水 {a_d:.2f}%", f"dukaat: statutory agio {a_d:.2f}%"),
            fontsize=7.6, color=MONEY, ha="right", va="bottom")
    ax.text(1.98, a_r + 0.06, T(f"骑士银币：法定升水 {a_r:.2f}%", f"rijder: statutory agio {a_r:.2f}%"),
            fontsize=7.6, color=AMBER, ha="right", va="bottom")
    for w in (w025, w15):
        ax.axvline(w, color=MUTED, lw=0.7, ls=(0, (1, 2)), zorder=1)
    ax.text(w15 - 0.03, 5.5, T(f"1683 年以前常见：$w$ = {w15:g}%", f"usual before 1683: $w$ = {w15:g}%"),
            fontsize=7.6, color=INK, ha="right", va="top")
    ax.text(w025 + 0.03, 5.5, T(f"1683 年收据：$w$ = {w025:g}%", f"1683 receipts: $w$ = {w025:g}%"),
            fontsize=7.6, color=INK, ha="left", va="top")
    ax.plot(w15, pre, "o", color=INK, ms=5, zorder=5)
    halo(ax.annotate(T(f"1666—1683 年平均 {pre:.2f}%", f"1666–1683 mean {pre:.2f}%"), (w15, pre), xytext=(0, -7),
                     textcoords="offset points", fontsize=7.6, color=INK, ha="center", va="top", zorder=6))
    ax.plot(w025, post, "s", color=INK, ms=5, zorder=5)
    halo(ax.annotate(T(f"1683—1703 年平均 {post:.2f}%", f"1683–1703 mean {post:.2f}%"), (w025, post),
                     xytext=(8, -1), textcoords="offset points", fontsize=7.6, color=INK, ha="left", va="center",
                     zorder=6))
    ax.set_xlim(0, 2.0)
    ax.set_ylim(2.2, 5.6)
    ax.set_xlabel(T("取款费 $w$（%）", "withdrawal fee $w$ (%)"))
    ax.set_ylabel(T("不被套利的市场升水 $a$（%）", "arbitrage-free market agio $a$ (%)"))
    _grid(ax)
    _title(ax, T("取款费越低，范围越窄；降到 0.25%，两种银币的范围不再重叠",
                 "the lower the fee, the narrower the band; at 0.25% the two bands no longer overlap"))
    return fig


# ---------------------------------------------------------------------------
@figure("finrev_debt")
def finrev_debt():
    """(a) Holland's debt by kind, 1591-1720; (b) England's debt over receipts, 1690-1760, against Philip II."""
    H, E, Tb = C.holland(), C.england(), C.table3()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.95), gridspec_kw=dict(width_ratios=[1.15, 1.0]))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.89, bottom=0.15, wspace=0.3)

    yrs = H.index.values
    parts = [("bills", T("债券", "bills"), MONEY), ("redeemable", T("可赎回年金", "redeemable annuities"), OUTPUT),
             ("life", T("终身年金", "life annuities"), AMBER), ("lottery", T("彩票借款等", "lottery loans etc."), MUTED)]
    a1.stackplot(yrs, *[H[k].values for k, _, _ in parts], colors=[tint(c, 0.4) for _, _, c in parts], lw=0,
                 zorder=2)
    a1.text(1695, 62, parts[0][1], fontsize=7.6, color=MONEY, ha="center", va="center", weight="bold", zorder=4)
    a1.text(1693, 133, parts[1][1], fontsize=7.6, color=OUTPUT, ha="center", va="center", weight="bold", zorder=4)
    for k, txt, xy, at in (("life", parts[2][1], (1700, 185), (1676, 214)),
                           ("lottery", parts[3][1], (1716, 294), (1690, 292))):
        col = dict((p[0], p[2]) for p in parts)[k]
        a1.annotate(txt, xy, xytext=at, fontsize=7.6, color=col, ha="right", va="center",
                    arrowprops=dict(arrowstyle="-", color=col, lw=0.6, shrinkA=1, shrinkB=1), zorder=4)
    for y, at in ((1609, (1604, 40)), (1648, (1640, 162)), (1713, (1690, 340))):
        v = H.loc[y, "total"]
        a1.annotate(T(f"{y} 年 {v:.0f}", f"{y}: {v:.0f}"), (y, v), xytext=at, fontsize=7.6, color=INK,
                    ha="center", va="bottom", arrowprops=dict(arrowstyle="-", color=INK, lw=0.6, shrinkB=1))
    a1.set_xlim(1590, 1720)
    a1.set_ylim(0, 370)
    a1.set_xticks([1600, 1640, 1680, 1720])
    a1.set_ylabel(T("年末债务（百万盾）", "debt at year end (m guilders)"))
    _grid(a1, axis="y")
    _title(a1, T("(a) 荷兰省：1648—1672 年不再增加", "(a) Holland: flat from 1648 to 1672"))

    s = E["debt_ratio"].dropna()
    a2.axvspan(C.PERIOD[0], C.PERIOD[1], color=tint(FISCAL, 0.08), lw=0, zorder=1)
    a2.plot(s.index, s.values, color=FISCAL, lw=1.8, zorder=3)
    mean = E.loc[C.PERIOD[0]:C.PERIOD[1], "debt_ratio"].mean()
    a2.plot([C.PERIOD[0], C.PERIOD[1]], [mean, mean], color=FISCAL, lw=0.8, ls=(0, (3, 2)), zorder=3)
    a2.text((C.PERIOD[0] + C.PERIOD[1]) / 2, mean + 1.6,
            T(f"{C.PERIOD[0]}—{C.PERIOD[1]} 年平均 {mean:.2f}", f"{C.PERIOD[0]}–{C.PERIOD[1]} mean {mean:.2f}"),
            fontsize=7.6, color=FISCAL, ha="center", va="bottom")
    d_p = Tb.loc["1565-96", "D"]
    a2.axhline(d_p, color=MUTED, lw=1.0, ls=(0, (4, 2)), zorder=2)
    a2.text(1759, d_p - 0.3, T(f"腓力二世 1565—1596 年 {d_p:.2f}", f"Philip II 1565–1596: {d_p:.2f}"), fontsize=7.6,
            color=MUTED, ha="right", va="top")
    a2.set_xlim(1688, 1760)
    a2.set_ylim(0, 14.5)
    a2.set_xticks([1690, 1710, 1730, 1750])
    a2.set_ylabel(T("债务（含年金）与收入之比", "debt (incl. annuities) / receipts"))
    _grid(a2, axis="y")
    _title(a2, T("(b) 英格兰：债务是收入的 9 倍多", "(b) England: debt over 9 times revenue"))
    return fig


# ---------------------------------------------------------------------------
@figure("finrev_rates")
def finrev_rates():
    """Holland's issuing rates, England's Crown loans, the yield on new long-term issues and the mortgage rate."""
    F, E = C.facts(), C.england()
    fig, ax = plt.subplots(figsize=(FIG_W, 3.05))
    fig.subplots_adjust(left=0.085, right=0.975, top=0.9, bottom=0.14)

    ax.axvspan(1710, 1714, color=tint(FISCAL, 0.08), lw=0, zorder=1)
    ax.text(1712, 15.7, T("托利党\n掌权", "Tory\nministry"), fontsize=7.6, color=FISCAL, ha="center", va="top",
            linespacing=1.15)
    m = E["mortgage_rate_pct"].dropna()
    ax.plot(m.index, m.values, color=MUTED, lw=1.0, ls=(0, (4, 2)), drawstyle="steps-post", zorder=2)
    ax.text(1745, m.loc[1744] + 0.35, T("私人抵押贷款（Allen）", "mortgages (Allen)"), fontsize=7.6, color=MUTED,
            ha="left", va="bottom")
    y = E["yield_long_pct"].dropna()
    ax.plot(y.index, y.values, color=PRICE, lw=1.7, zorder=3)
    ax.text(1726, 7.2, T("新发长期借款的收益率\n（1727 年起为 3% 永续年金）", "yield on new long-term loans\n(3% perpetuals from 1727)"),
            fontsize=7.6, color=PRICE, ha="left", va="bottom", linespacing=1.25)
    for yr, r, perp in C.crown_loans(F):
        ax.plot(yr, r, "o", ms=4.6, zorder=4, mfc=PRICE if perp else "white", mec=PRICE, mew=1.1)
    ax.text(1614, 10.6, T("斯图亚特王朝的强制借款", "early Stuart forced loans"), fontsize=7.6, color=PRICE,
            ha="center", va="bottom")
    ax.text(1696, 13.3, T("14%：终身年金与彩票借款", "14%: life annuities and the lottery"), fontsize=7.6,
            color=PRICE, ha="left", va="top")
    lo, hi = F["nw_holland"][2], F["nw_holland"][3]
    ax.annotate("", (1686, 16.0), (1686, lo), arrowprops=dict(arrowstyle="-|>", color=PRICE, lw=1.0), zorder=4)
    ax.text(1684.5, 11.5, T(f"1688 年以前\n{lo:g}%—{hi:g}%", f"before 1688\n{lo:g}–{hi:g}%"), fontsize=7.6,
            color=PRICE, ha="right", va="center", linespacing=1.2)
    hr = C.holland_rates(F)
    ax.plot([h[0] for h in hr], [h[1] for h in hr], "D", color=MONEY, ms=4.6, zorder=5)
    ax.text(1612, 6.25, T("荷兰省的发行利率", "Holland's issuing rates"), fontsize=7.6, color=MONEY, ha="left",
            va="center")
    ax.text(1673, 3.3, T("坦普尔 1673", "Temple 1673"), fontsize=7.6, color=MONEY, ha="center", va="top")
    ax.set_xlim(1585, 1760)
    ax.set_ylim(0, 16)
    ax.set_xticks([1600, 1640, 1680, 1720, 1760])
    ax.set_ylabel(T("年利率（%）", "interest rate (% a year)"))
    _grid(ax)
    _title(ax, T("英格兰的借款利率过了三十年才落到荷兰省的水平", "England's borrowing rates took thirty years to reach Holland's"))
    return fig
