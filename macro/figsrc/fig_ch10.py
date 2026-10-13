"""Figures for Chapter 10 (伊斯兰世界与地中海的商业革命).

Style as in fig_ch12.py (docs/STYLE.md §4 and §7.1): bold "(a) …" panel titles that state the
point, direct labels in the colour of their series, a second series in AMBER and dashed, and
rounded boxes for diagrams.  All numbers come from checks/check_ch10.py, which reads
data/snapshots/medieval_credit_facts.csv and data/snapshots/bbm2017_implied_rates.csv.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch10 as C  # noqa: E402
from style import (ACCENT, AMBER, EXTERNAL, FIG_W, INK, LIGHT, MONEY, MUTED, OUTPUT, PRICE, ZH, T,  # noqa: E402
                   arrow, canvas, clean_axes, figure, label, pill, rbox, tint)


# ---------------------------------------------------------------------------
@figure("bill_flows")
def bill_flows():
    """The bill of 26 September 1442: Venice -> London, protest, rechange -> Venice."""
    F = C.facts()
    ducats, e_ven, e_lon = F["csp_bill"], F["csp_rate_venice"], F["csp_rate_london"]
    pence = ducats * e_ven
    back = pence / e_lon
    sp = C.spread(e_ven, e_lon)
    simple, comp = C.annualized(sp, 0.5)
    p, s, d = C.lsd(pence)

    W, H = 10.4, 5.5
    fig, ax = canvas(FIG_W, FIG_W * H / W, xlim=(0, W), ylim=(0, H))
    # two cities as horizontal bands
    yv, yl = 3.55, 0.75            # bottom of the Venice band and of the London band
    bh = 1.45
    for y, name in [(yv, T("威尼斯", "Venice")), (yl, T("伦敦", "London"))]:
        rbox(ax, 0.05, y, W - 0.1, bh, fc=tint(MUTED, 0.06), ec=tint(MUTED, 0.3), lw=0.7, r=0.12, z=1)
        label(ax, 0.42, y + bh / 2, name, size=9.0, weight="bold", color=MUTED, rotation=90)
    # time columns
    cols = [(2.45, T("1442 年 9 月 26 日", "26 Sep 1442")), (5.75, T("1442 年 12 月 31 日", "31 Dec 1442")),
            (8.85, T("约 1443 年 3 月 31 日", "c. 31 Mar 1443"))]
    for x, txt in cols:
        label(ax, x, H - 0.17, txt, size=7.8, color=MUTED)

    def party(x, y, w, title, sub, color):
        rbox(ax, x - w / 2, y, w, 0.92, fc=tint(color, 0.12), ec=tint(color, 0.6), lw=0.9, r=0.1, z=3)
        label(ax, x, y + 0.62, title, size=8.2, weight="bold", color=color, z=4)
        label(ax, x, y + 0.27, sub, size=7.4, color=INK, z=4)

    # Venice, September: the Medici company pays 150 ducats to the Venier brothers
    party(1.6, yv + 0.27, 1.9, T("美第奇公司", "Medici company"),
          T(f"付出 {ducats:.0f} 杜卡特", f"pays {ducats:.0f} ducats"), MONEY)
    party(3.95, yv + 0.27, 1.75, T("韦尼尔兄弟", "Venier brothers"), T("收下，开出汇票", "draw the bill"), EXTERNAL)
    arrow(ax, (2.6, yv + 0.73), (3.03, yv + 0.73), color=MONEY, lw=1.4)
    # London, December: Bardi company is to pay; the bill is protested
    party(5.75, yl + 0.27, 2.55, T("巴尔迪公司（付款人）", "Bardi company (drawee)"),
          T("应付 " + f"{pence:.0f} 便士" + "，拒付", f"owes {pence:.0f}d, does not pay"), PRICE)
    # bill travels to London
    arrow(ax, (4.1, yv + 0.25), (5.3, yl + 1.22), color=INK, lw=1.2, ls=(0, (4, 2)))
    label(ax, 2.85, 2.62, T(f"汇票：每杜卡特 {e_ven:g} 便士\n= {p} 镑 {s} 先令 {d:.0f} 便士\n惯例期 3 个月",
                            f"bill at {e_ven:g}d per ducat\n= £{p} {s}s {d:.0f}d\nusance 3 months"),
          size=7.4, ha="center", color=INK)
    # rechange bill back to Venice at the London rate
    arrow(ax, (6.3, yl + 1.22), (8.4, yv + 0.25), color=INK, lw=1.2, ls=(0, (4, 2)))
    label(ax, 8.85, 2.62, T(f"拒付证书与回汇票：\n按伦敦汇率 {e_lon:g} 便士\n再过 3 个月",
                           f"protest and rechange at\nthe London rate {e_lon:g}d\nanother 3 months"),
          size=7.4, ha="center", color=INK)
    # Venice, March: the Venier brothers owe the Medici
    party(8.85, yv + 0.27, 2.6, T("韦尼尔兄弟", "Venier brothers"),
          T(f"欠美第奇 {back:.2f} 杜卡特", f"owe the Medici {back:.2f} ducats"), EXTERNAL)
    pill(ax, W / 2, 0.33, T(f"六个月：{ducats:.0f} → {back:.2f} 杜卡特，增加 {100 * sp:.1f}%；"
                            f"年率 {100 * simple:.1f}%（单利），{100 * comp:.1f}%（复利）",
                            f"six months: {ducats:.0f} → {back:.2f} ducats, +{100 * sp:.1f}%; "
                            f"{100 * simple:.1f}% a year simple, {100 * comp:.1f}% compound"),
         color=ACCENT, size=7.8)
    return fig


# ---------------------------------------------------------------------------
@figure("fx_implied_rates")
def fx_implied_rates():
    """(a) spread against round-trip term with constant-rate lines; (b) share of losing transactions."""
    d, slope = C.bbm_table(C.facts())
    F = C.facts()
    sp1442 = 100 * C.spread(F["csp_rate_venice"], F["csp_rate_london"])
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.9), gridspec_kw=dict(width_ratios=[1.25, 1]))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.89, bottom=0.17, wspace=0.3)

    x = np.linspace(0, 200, 50)
    for r in (0.10, 0.16):
        a1.plot(x, 100 * r * x / 365, color=MUTED, lw=0.8, ls=(0, (1.5, 2)), zorder=1)
    a1.text(56, 100 * 0.16 * 56 / 365 + 0.2, T("年率 16%", "16% a year"), fontsize=7.4, color=MUTED, ha="right", va="bottom")
    a1.text(203, 100 * 0.10 * 203 / 365 - 1.3, T("年率 10%", "10% a year"), fontsize=7.4, color=MUTED, ha="right", va="top")
    a1.plot(x, slope * x / 365, color=AMBER, lw=1.4, ls=(0, (4, 2)), zorder=2)
    a1.text(118, slope * 118 / 365 - 0.95, T(f"过原点的拟合线\n斜率 = 年率 {slope:.0f}%", f"line through 0:\n{slope:.0f}% a year"),
            fontsize=7.4, color=AMBER, ha="left", va="top", linespacing=1.25)
    a1.scatter(d.term_days, d.spread_pct, s=14, color=MONEY, zorder=4, lw=0)
    a1.scatter([182.5], [sp1442], s=34, marker="D", color=PRICE, zorder=5, lw=0)
    a1.annotate(T("1442 年的汇票", "the 1442 bill"), xy=(182.5, sp1442), xytext=(150, 8.75), fontsize=7.4,
                color=PRICE, ha="right", va="center", arrowprops=dict(arrowstyle="-", color=PRICE, lw=0.6))
    for a, b, xt, yt in [("Florence", "Venice", 40, 0.3), ("Genoa", "London", 150, 7.8)]:
        r = d[(d.city_from == a) & (d.city_to == b)].iloc[0]
        txt = T({"Florence": "佛罗伦萨→威尼斯", "Genoa": "热那亚→伦敦"}[a], f"{a}→{b}")
        a1.annotate(txt, xy=(r.term_days, r.spread_pct), xytext=(xt, yt), fontsize=7.4, color=MONEY,
                    ha="left" if a == "Florence" else "right", va="center",
                    arrowprops=dict(arrowstyle="-", color=MONEY, lw=0.6))
    a1.set_xlim(0, 205)
    a1.set_ylim(0, 9.3)
    a1.set_xlabel(T("汇出与汇回的总期限（天）", "round-trip term (days)"))
    a1.set_ylabel(T("两地汇率之差（%）", "spread between the two quotes (%)"))
    a1.set_title(T("(a) 价差随期限成比例变大", "(a) the spread grows with the term"), fontsize=9.0,
                 weight="bold", loc="left", pad=4)

    a2.scatter(d.term_days, d.negative_return_pct, s=14, color=MONEY, zorder=4, lw=0)
    vf = d[(d.city_from == "Venice") & (d.city_to == "Florence")].iloc[0]
    lg = d[(d.city_from == "London") & (d.city_to == "Genoa")].iloc[0]
    a2.annotate(T("威尼斯→佛罗伦萨", "Venice→Florence"), xy=(vf.term_days, vf.negative_return_pct),
                xytext=(22, 16.0), fontsize=7.4, color=MONEY, arrowprops=dict(arrowstyle="-", color=MONEY, lw=0.6))
    a2.annotate(T("伦敦→热那亚", "London→Genoa"), xy=(lg.term_days, lg.negative_return_pct),
                xytext=(203, 2.7), ha="right", va="center", fontsize=7.4, color=MONEY, arrowprops=dict(arrowstyle="-", color=MONEY, lw=0.6))
    a2.set_xlim(0, 205)
    a2.set_ylim(0, 22)
    a2.set_xlabel(T("总期限（天）", "round-trip term (days)"))
    a2.set_ylabel(T("亏损交易的比例（%）", "transactions that lost (%)"))
    a2.set_title(T("(b) 期限越短，越常亏损", "(b) short terms lost more often"), fontsize=9.0, weight="bold",
                 loc="left", pad=4)
    for a in (a1, a2):
        clean_axes(a)
        a.grid(True, color=LIGHT, lw=0.6, zorder=0)
        a.set_axisbelow(True)
    return fig


# ---------------------------------------------------------------------------
@figure("commenda_payoffs")
def commenda_payoffs():
    """What the investor and the travelling merchant receive, commenda against a loan at 20%."""
    F = C.facts()
    _, v_star = C.commenda(F)
    K, s_inv = F["pt_1199_capital"], F["pt_1199_share"]
    repay = K * (1 + C.LOAN_RATE)
    V = np.linspace(0, 700, 400)
    inv_c = np.minimum(V, K) + s_inv * np.maximum(V - K, 0)
    agent_c = (1 - s_inv) * np.maximum(V - K, 0)
    inv_l = np.full_like(V, repay)
    agent_l = V - repay

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.85), sharex=True)
    fig.subplots_adjust(left=0.085, right=0.985, top=0.89, bottom=0.17, wspace=0.28)
    a1.plot(V, inv_c, color=MONEY, lw=2.0)
    a1.plot(V, inv_l, color=AMBER, lw=1.8, ls=(0, (4, 2)))
    a1.text(640, 300 + s_inv * 340 + 18, T("合伙", "commenda"), fontsize=7.8, color=MONEY, ha="right", va="bottom")
    a1.text(690, repay + 15, T("借款（20%）", "loan (20%)"), fontsize=7.8, color=AMBER, ha="right", va="bottom")
    a1.axvline(v_star, color=MUTED, lw=0.6, ls=(0, (1, 2)))
    a1.text(v_star + 8, 60, T(f"{v_star:.0f}：两者相等", f"{v_star:.0f}: equal"), fontsize=7.4, color=MUTED, ha="left")
    a1.set_ylim(0, 600)
    a1.set_ylabel(T("收回（镑）", "received (pounds)"))
    a1.set_title(T("(a) 投资人：合伙时亏损由他承担", "(a) investor: bears the loss in a commenda"), fontsize=8.8,
                 weight="bold", loc="left", pad=4)

    a2.axhline(0, color=MUTED, lw=0.6)
    a2.plot(V, agent_c, color=MONEY, lw=2.0)
    a2.plot(V, agent_l, color=AMBER, lw=1.8, ls=(0, (4, 2)))
    a2.text(690, (1 - s_inv) * 390 + 14, T("合伙", "commenda"), fontsize=7.8, color=MONEY, ha="right", va="bottom")
    a2.text(560, 560 - repay + 30, T("借款", "loan"), fontsize=7.8, color=AMBER, ha="right", va="bottom")
    a2.text(175, -350, T("借款：亏多少，\n行商赔多少", "loan: he bears\nthe whole loss"), fontsize=7.4,
            color=AMBER, ha="left", va="bottom", linespacing=1.25)
    a2.set_ylim(-380, 360)
    a2.set_ylabel(T("得到（镑）", "received (pounds)"))
    a2.set_title(T("(b) 行商：合伙时最多白跑一趟", "(b) traveller: at worst, unpaid work"), fontsize=8.8,
                 weight="bold", loc="left", pad=4)
    for a in (a1, a2):
        clean_axes(a)
        a.set_xlim(0, 700)
        a.set_xlabel(T("运回威尼斯的货值 V（镑）", "value brought back, V (pounds)"))
        a.axvline(K, color=MUTED, lw=0.6, ls=(0, (1, 2)))
    a2.text(K + 8, 300, T("本金 300", "capital 300"), fontsize=7.4, color=MUTED, ha="left")
    return fig
