"""Figures for Chapter 19 (数量论、价格–铸币流动与金块论战).

Style as in fig_ch18.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series, the second series in AMBER and dashed with square markers, the Restriction (February 1797 to
May 1821) shaded light grey. All numbers come from checks/check_ch19.py, which reads the snapshots bullion_facts
(Cannan's Tables I and II, Silberling's Tables 6 and 7, Hume's examples), boe_millennium_gb_1790_1830 and
riksbank_sweden_1740_1777. bullion_hume is a teaching diagram; its speed of adjustment kappa is assumed.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, NullLocator

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch19 as C  # noqa: E402
from style import (AMBER, EXTERNAL, FIG_W, FISCAL, INK, LIGHT, MONEY, MUTED, OUTPUT, PRICE, T,  # noqa: E402
                   arrow, clean_axes, figure, halo, label, rbox, shade_periods, tint)

SQUARE = dict(marker="s", ms=4, mfc=AMBER, mec="white", mew=0.5)
DOT = dict(marker="o", ms=5, mec="white", mew=0.6)
RESTRICTION = [(1797 + 2 / 12, 1821 + 4 / 12)]          # February 1797 to May 1821
FIAT_SE = [(1745, 1776)]


def _title(ax, s):
    ax.set_title(s, fontsize=9.0, weight="bold", loc="left", pad=4)


def _grid(ax, axis="y"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


def _dashed(ax, x, y, **kw):
    line, = ax.plot(x, y, color=AMBER, lw=1.5, zorder=3, **kw)
    line.set_dashes((4, 2))
    return line


def _log_ticks(ax, ticks, fmt=lambda t: f"{t:g}"):
    ax.yaxis.set_major_locator(FixedLocator(ticks))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.set_yticklabels([fmt(t) for t in ticks])


# ---------------------------------------------------------------------------
@figure("bullion_bank")
def bullion_bank():
    """(a) public expenditure and revenue, 1792-1821; (b) the Bank's notes, coin and bullion, and bills discounted."""
    Tb = C.cannan()
    yrs = list(Tb.index)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(FIG_W, 4.5), sharex=True)
    fig.subplots_adjust(left=0.1, right=0.975, top=0.945, bottom=0.085, hspace=0.36)

    # (a) the budget
    shade_periods(a1, RESTRICTION)
    a1.plot(yrs, Tb.exp, color=FISCAL, lw=2.0, zorder=4)
    _dashed(a1, yrs, Tb.rev, **SQUARE)
    a1.fill_between(yrs, Tb.rev, Tb.exp, where=Tb.exp > Tb.rev, color=tint(FISCAL, 0.15), lw=0, zorder=1)
    a1.text(1809.3, 89, T("公共支出", "expenditure"), fontsize=7.8, color=FISCAL, ha="center", va="bottom")
    a1.text(1806.5, 46, T("收入", "revenue"), fontsize=7.8, color=AMBER, ha="center", va="top")
    for y in (1795, 1796):
        a1.plot([y], [Tb.exp[y]], color=FISCAL, zorder=5, **DOT)
    e95, e96 = C.facts()["ci_x"][2:4]
    halo(a1.annotate(T(f"Cannan：1795—1796 年支出 {e95 * 100:,.0f} 万与 {e96 * 100:,.0f} 万英镑",
                       f"Cannan: £{e95:g}m and £{e96:g}m spent in 1795–96"),
                     (1796, Tb.exp[1796]), xytext=(1787.6, 82), fontsize=7.6, color=FISCAL, ha="left", va="center",
                     arrowprops=dict(arrowstyle="-", color=FISCAL, lw=0.6, shrinkB=3), zorder=6))
    a1.text(1809, 4, T("停兑期", "the Restriction"), fontsize=7.6, color=MUTED, ha="center", va="bottom")
    a1.set_ylim(0, 125)
    a1.set_ylabel(T("百万英镑", "£ millions"))
    _grid(a1)
    _title(a1, T("(a) 1795 年以后，战争使支出远远超过收入", "(a) From 1795 the war drove spending far above revenue"))

    # (b) the Bank
    shade_periods(a2, RESTRICTION)
    tf = [y + 2 / 12 for y in yrs]
    ta = [y + 8 / 12 for y in yrs]
    t = [v for pair in zip(tf, ta) for v in pair]
    notes = [v for pair in zip(Tb.notes_f, Tb.notes_a) for v in pair]
    coin = [v for pair in zip(Tb.coin_f, Tb.coin_a) for v in pair]
    b = Tb.bills.dropna()
    a2.plot([y + 0.5 for y in b.index], b.values, color=tint(MONEY, 0.45), lw=1.3, zorder=2)
    a2.plot(t, notes, color=MONEY, lw=1.9, zorder=4)
    _dashed(a2, t, coin)
    a2.text(1813.5, 28.6, T("银行券", "notes"), fontsize=7.8, color=MONEY, ha="center", va="bottom")
    a2.text(1812.6, 17.6, T("贴现的商业票据", "bills discounted"), fontsize=7.8, color=tint(MONEY, 0.7), ha="left",
            va="center")
    a2.text(1803.5, 0.6, T("金币与金银块", "coin and bullion"), fontsize=7.8, color=AMBER, ha="center", va="bottom")
    x97 = 1797 + 2 / 12
    a2.plot([x97], [Tb.coin_f[1797]], color=AMBER, zorder=5, **DOT)
    a2.plot([x97], [Tb.notes_f[1797]], color=MONEY, zorder=5, **DOT)
    halo(a2.annotate(T(f"1797 年 2 月底：金银 {Tb.coin_f[1797] * 100:,.0f} 万，银行券 {Tb.notes_f[1797] * 100:,.0f} 万",
                       f"end of Feb. 1797: bullion £{Tb.coin_f[1797]:g}m, notes £{Tb.notes_f[1797]:g}m"),
                     (x97, Tb.coin_f[1797]), xytext=(1787.6, 24.5), fontsize=7.6, color=INK, ha="left", va="center",
                     arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6, shrinkB=3), zorder=6))
    a2.set_ylim(0, 32)
    a2.set_xlim(1787.2, 1822.5)
    a2.set_xticks(range(1790, 1821, 5))
    a2.set_ylabel(T("百万英镑", "£ millions"))
    a2.set_xlabel(T("年份", "year"))
    _grid(a2)
    r = 100 * Tb.coin_f[1797] / Tb.notes_f[1797]
    _title(a2, T(f"(b) 停兑前夕，金银只有银行券的 {r:.0f}%", f"(b) On the eve of the stop, bullion was {r:.0f}% of the notes"))
    return fig


# ---------------------------------------------------------------------------
def _node(ax, x, y, w, h, txt, color):
    rbox(ax, x - w / 2, y - h / 2, w, h, fc=tint(color, 0.12), ec=tint(color, 0.6), lw=0.9, r=0.1, z=3)
    label(ax, x, y, txt, size=7.8, color=INK, z=4)


@figure("bullion_hume")
def bullion_hume():
    """(a) the price-specie flow, drawn as a loop; (b) Hume's two experiments with eq:bullion-hume."""
    F = C.facts()
    fig = plt.figure(figsize=(FIG_W, 4.6))
    gs = fig.add_gridspec(2, 1, height_ratios=[0.85, 1.05], hspace=0.38, left=0.1, right=0.975, top=0.95, bottom=0.085)
    a1, a2 = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])

    # (a) the loop
    a1.set_xlim(0, 10)
    a1.set_ylim(0.3, 3.0)
    a1.axis("off")
    w, h = 2.55, 0.62
    pts = [(1.7, 2.45, T("货币 M 减少", "money M falls"), MONEY),
           (5.0, 2.45, T("物价 P 下降", "prices P fall"), PRICE),
           (8.3, 2.45, T("实际汇率 q 上升\n本国的东西便宜", "real rate q rises:\nhome goods cheap"), EXTERNAL),
           (8.3, 0.75, T("出口增加\n进口减少", "exports up,\nimports down"), OUTPUT),
           (5.0, 0.75, T("贸易顺差", "trade surplus"), OUTPUT),
           (1.7, 0.75, T("金银流入", "gold and silver\nflow in"), MONEY)]
    for x, y, txt, col in pts:
        _node(a1, x, y, w, h, txt, col)
    for (x0, y0, *_), (x1, y1, *_) in zip(pts, pts[1:]):
        if y0 == y1:
            s = 1 if x1 > x0 else -1
            arrow(a1, (x0 + s * w / 2, y0), (x1 - s * w / 2, y1), color=INK, lw=1.1, ms=8)
        else:
            arrow(a1, (x0, y0 - h / 2), (x1, y1 + h / 2), color=INK, lw=1.1, ms=8)
    x0, y0 = pts[-1][:2]
    arrow(a1, (x0, y0 + h / 2), (x0, pts[0][1] - h / 2), color=MONEY, lw=1.3, ms=9)
    label(a1, x0 - 0.15, 1.6, T("货币回升", "money\nrecovers"), size=7.6, color=MONEY, ha="right")
    label(a1, 5.0, 1.6, T("货币增加时，每一步都反过来", "when money rises, every step reverses"), size=7.6,
          color=MUTED)
    a1.set_title(T("(a) 钱少了，物价跌，金银流回来", "(a) Less money, lower prices, and the metal flows back"),
                 fontsize=9.0, weight="bold", loc="left", pad=2)

    # (b) the two experiments
    x_lo = math.log(1 - F["hm_fourfifths"][0])
    x_hi = math.log(F["hm_fivefold"][0])
    t = [i / 4 for i in range(0, 61)]
    lo = [C.hume(x_lo, C.KAPPA, s) for s in t]
    hi = [C.hume(x_hi, C.KAPPA, s) for s in t]
    a2.axhline(1, color=MUTED, lw=0.8, ls=(0, (1, 2)), zorder=1)
    a2.plot(t, lo, color=MONEY, lw=2.0, zorder=4)
    _dashed(a2, t, hi)
    for s in (1, 5):
        a2.plot([s], [C.hume(x_lo, C.KAPPA, s)], color=MONEY, zorder=5, **DOT)
        a2.plot([s], [C.hume(x_hi, C.KAPPA, s)], color=AMBER, zorder=5, **SQUARE)
    a2.text(1.3, C.hume(x_lo, C.KAPPA, 1) * 0.86, T(f"一年后 {C.hume(x_lo, C.KAPPA, 1):.3f}", f"after a year: {C.hume(x_lo, C.KAPPA, 1):.3f}"),
            fontsize=7.6, color=MONEY, ha="left", va="top")
    a2.text(1.3, C.hume(x_hi, C.KAPPA, 1) * 1.08, T(f"一年后 {C.hume(x_hi, C.KAPPA, 1):.2f} 倍", f"after a year: {C.hume(x_hi, C.KAPPA, 1):.2f}×"),
            fontsize=7.6, color=AMBER, ha="left", va="bottom")
    a2.text(9.2, 0.62, T("只剩五分之一", "a fifth left"), fontsize=7.8, color=MONEY, ha="left", va="top")
    a2.text(9.2, 1.6, T("增加到五倍", "five times as much"), fontsize=7.8, color=AMBER, ha="left", va="bottom")
    hl = C.half_life(C.KAPPA)
    a2.text(14.8, 0.3, T(f"κ = {C.KAPPA:g}：偏离缩小一半要 {hl:.1f} 年", f"κ = {C.KAPPA:g}: half the gap closes in {hl:.1f} years"),
            fontsize=7.6, color=MUTED, ha="right", va="center")
    a2.set_yscale("log")
    a2.set_ylim(0.17, 6.5)
    _log_ticks(a2, [0.2, 0.5, 1, 2, 5])
    a2.set_xlim(0, 15)
    a2.set_xlabel(T("年", "years"))
    a2.set_ylabel(T("货币量 / 常态（对数）", "money / normal (log)"))
    _grid(a2)
    _title(a2, T("(b) 两个思想实验：对数上对称地回到常态", "(b) Hume's two experiments return symmetrically in logs"))
    return fig


# ---------------------------------------------------------------------------
@figure("bullion_premium")
def bullion_premium():
    """(a) Silberling's premium and exchange deviation, 1790-1824; (b) one against the other, with the gold point."""
    S = C.silberling()
    yrs = list(S.index)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(FIG_W, 4.6), gridspec_kw=dict(height_ratios=[1.0, 1.1]))
    fig.subplots_adjust(left=0.105, right=0.975, top=0.945, bottom=0.085, hspace=0.42)

    # (a) the two series
    shade_periods(a1, RESTRICTION)
    a1.axhline(0, color=MUTED, lw=0.7, zorder=1)
    a1.plot(yrs, S.pi, color=PRICE, lw=2.0, zorder=4)
    _dashed(a1, yrs, S.dev, **SQUARE)
    a1.text(1804.5, 21, T("金的溢价（白银折算）", "premium on gold (via silver)"), fontsize=7.8, color=PRICE,
            ha="center", va="bottom")
    a1.text(1803, -16, T("对汉堡的汇率偏离平价", "exchange on Hamburg, from par"), fontsize=7.8, color=AMBER,
            ha="center", va="top")
    a1.plot([1813], [S.pi[1813]], color=PRICE, zorder=5, **DOT)
    a1.text(1814.2, S.pi[1813], T(f"1813 年：{S.pi[1813]:+.1f}%", f"1813: {S.pi[1813]:+.1f}%"), fontsize=7.6, color=PRICE,
            ha="left", va="center")
    a1.text(1798, -33, T("停兑期", "the Restriction"), fontsize=7.6, color=MUTED, ha="left", va="bottom")
    a1.set_xlim(1789.5, 1824.5)
    a1.set_ylim(-36, 47)
    a1.set_ylabel("%")
    _grid(a1)
    _title(a1, T("(a) 金价涨的时候，汇率就跌", "(a) When the price of gold rose, the exchange fell"))

    # (b) the scatter
    pis = [i / 2 for i in range(-4, 89)]
    a2.plot(pis, [100 * (1 / (1 + p / 100) - 1) for p in pis], color=MUTED, lw=1.0, ls=(0, (4, 2)), zorder=2)
    a2.text(33, -17, T("虚线：(1+π)(1−δ) = 1", "dashed: (1+π)(1−δ) = 1"), fontsize=7.6, color=MUTED, ha="left",
            va="center")
    hot = (1809, 1810, 1811)
    for y in yrs:
        col = PRICE if y in hot else tint(INK, 0.45)
        a2.plot([S.pi[y]], [S.dev[y]], color=col, zorder=4 if y in hot else 3, marker="o", ms=4.5 if y in hot else 3.5,
                mec="white", mew=0.5, ls="none")
    for y, ty in zip(sorted(hot, key=lambda y: -S.dev[y]), (-17.5, -23, -28.5)):
        c = 100 * C.min_cost(S.pi[y] / 100, -S.dev[y] / 100)
        halo(a2.annotate(T(f"{y} 年：运金成本 ≥ {c:.1f}%", f"{y}: cost of sending gold ≥ {c:.1f}%"),
                         (S.pi[y], S.dev[y]), xytext=(-1.5, ty), fontsize=7.6, color=PRICE, ha="left", va="center",
                         arrowprops=dict(arrowstyle="-", color=PRICE, lw=0.6, shrinkB=3), zorder=6))
    a2.text(T(30.5, 26), -5, T("其余各年：两者几乎互相抵消", "other years: the two nearly offset"), fontsize=7.6,
            color=tint(INK, 0.6), ha="left", va="center")
    a2.axhline(0, color=LIGHT, lw=0.8, zorder=1)
    a2.axvline(0, color=LIGHT, lw=0.8, zorder=1)
    a2.set_xlim(-3, 44)
    a2.set_ylim(-34, 8)
    a2.set_xlabel(T("金的溢价 π（%）", "premium on gold π (%)"))
    a2.set_ylabel(T("汇率偏离平价（%）", "exchange from par (%)"))
    _grid(a2, "both")
    _title(a2, T("(b) 1809—1811 年，汇率跌得比金价涨得多", "(b) In 1809–11 the exchange fell by more than gold rose"))
    return fig


# ---------------------------------------------------------------------------
@figure("bullion_prices")
def bullion_prices():
    """(a) wholesale prices in paper and in gold, 1790-1824, log scale; (b) four periods split into the two parts."""
    B, S = C.boe(), C.silberling()
    yrs = list(S.index)
    P = B.wholesale_1821_25[yrs]
    G = C.gold_prices(B, S)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(FIG_W, 4.55), gridspec_kw=dict(height_ratios=[1.15, 1.0]))
    fig.subplots_adjust(left=0.2, right=0.975, top=0.945, bottom=0.085, hspace=0.45)

    # (a) the two price levels
    shade_periods(a1, RESTRICTION)
    a1.fill_between(yrs, G, P, where=P >= G, color=tint(PRICE, 0.13), lw=0, zorder=1)
    a1.plot(yrs, P, color=PRICE, lw=2.0, zorder=4)
    _dashed(a1, yrs, G, **SQUARE)
    a1.text(1801, 160, T("批发物价（纸币）", "wholesale prices (paper)"), fontsize=7.8, color=PRICE, ha="center",
            va="bottom")
    a1.text(1817.5, 109, T("以金计", "in gold"), fontsize=7.8, color=AMBER, ha="center", va="top")
    a1.text(1813, 143.5, T("溢价", "premium"), fontsize=7.6, color=tint(PRICE, 0.8), ha="center", va="center")
    for y in (1813, 1821):
        a1.plot([y], [P[y]], color=PRICE, zorder=5, **DOT)
    a1.text(1813, P[1813] * 1.04, f"{P[1813]:.1f}", fontsize=7.6, color=PRICE, ha="center", va="bottom")
    a1.text(1820.7, P[1821] * 0.965, f"{P[1821]:.1f}", fontsize=7.6, color=PRICE, ha="right", va="top")
    a1.set_yscale("log")
    a1.set_ylim(78, 195)
    _log_ticks(a1, [80, 100, 120, 140, 160, 180])
    a1.set_xlim(1789.5, 1824.5)
    a1.set_ylabel(T("1821—1825 年 = 100（对数）", "1821–25 = 100 (log)"))
    _grid(a1)
    _title(a1, T("(a) 纸币物价与以金计的物价之间的缝隙，是溢价", "(a) The gap between paper and gold prices is the premium"))

    # (b) the decomposition
    rows = []
    for a, b in C.PERIODS:
        d = C.decompose(B, S, a, b)
        rows.append((T(f"{a}—{b} 年", f"{a}–{b}"), d["prem"], d["gold"], d["total"]))
    h = 0.62
    for i, (name, pr, go, tot) in enumerate(rows):
        y = len(rows) - 1 - i
        # stack each part on its own side of zero
        pos, neg = 0.0, 0.0
        for v, col in ((pr, PRICE), (go, tint(AMBER, 0.55))):
            left = pos if v >= 0 else neg
            a2.barh(y, v, left=left, height=h, color=col, zorder=3)
            if v >= 0:
                pos += v
            else:
                neg += v
        a2.plot([tot], [y], color=INK, marker="o", ms=4.5, mec="white", mew=0.5, ls="none", zorder=5)
        a2.text(max(pos, 0) + 0.012, y, f"{tot:+.3f}".replace("-", "−"), fontsize=7.6, color=INK, ha="left",
                va="center")
    a2.axvline(0, color=MUTED, lw=0.8, zorder=2)
    a2.set_yticks(range(len(rows)))
    a2.set_yticklabels([r[0] for r in reversed(rows)], fontsize=7.8)
    a2.text(0.165, 3.42, T("溢价", "premium"), fontsize=7.6, color=PRICE, ha="center", va="bottom")
    a2.text(0.33, 3.42, T("以金计的物价", "prices in gold"), fontsize=7.6, color=tint(AMBER, 0.8), ha="left",
            va="bottom")
    a2.set_xlim(-0.42, 0.52)
    a2.set_ylim(-0.55, 3.75)
    a2.set_xlabel(T("批发物价的对数变化（黑点为合计）", "change in log wholesale prices (dot: total)"))
    _grid(a2, "x")
    _title(a2, T("(b) 中间两段主要是溢价，头尾两段主要是以金计的物价", "(b) The premium drove the middle, prices in gold the ends"))
    return fig


# ---------------------------------------------------------------------------
@figure("bullion_sweden")
def bullion_sweden():
    """(a) the riksdaler in marks, 1740-1777, with the old par and the par of 1776; (b) notes and metal reserves."""
    W, F = C.sweden(), C.facts()
    yrs = list(W.index)
    par, new = F["ed_caps"][2], F["ed_1776"][3]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(FIG_W, 4.5), sharex=True)
    fig.subplots_adjust(left=0.1, right=0.975, top=0.945, bottom=0.085, hspace=0.36)

    # (a) the riksdaler
    shade_periods(a1, FIAT_SE)
    band = W.dropna(subset=["riksdaler_low"])
    a1.fill_between(band.index, band.riksdaler_low, band.riksdaler_high, color=tint(PRICE, 0.18), lw=0, zorder=1)
    a1.plot(yrs, W.riksdaler_marks, color=PRICE, lw=2.0, zorder=4)
    for v, txt in ((par, T(f"旧平价 {par:g} 马克", f"old par, {par:g} marks")),
                   (new, T(f"1776 年的新平价 {new:g} 马克", f"the par of 1776, {new:g} marks"))):
        a1.axhline(v, color=MUTED, lw=0.9, ls=(0, (4, 2)), zorder=2)
        a1.text(1740.3, v - 1.5, txt, fontsize=7.6, color=MUTED, ha="left", va="top")
    for y, xy, va in ((1764, (1757.2, 100), "center"), (1768, (1770.6, 42), "center")):
        v = W.riksdaler_marks[y]
        a1.plot([y], [v], color=PRICE, zorder=5, **DOT)
        halo(a1.annotate(T(f"{y} 年：{v:.1f}", f"{y}: {v:.1f}"), (y, v), xytext=xy, fontsize=7.6, color=PRICE,
                         ha="center", va=va, arrowprops=dict(arrowstyle="-", color=PRICE, lw=0.6, shrinkB=3), zorder=6))
    a1.text(1748.5, 55, T("一年里的最低—最高", "low–high of the year"), fontsize=7.6, color=tint(PRICE, 0.8),
            ha="center", va="bottom")
    a1.set_ylim(25, 112)
    a1.set_ylabel(T("马克（铜本位）", "marks kopparmynt"))
    _grid(a1)
    _title(a1, T("(a) 便帽党试图回到旧平价：里克斯达勒四年跌了 45%", "(a) The Caps try for the old par: down 45% in four years"))

    # (b) notes and reserves
    shade_periods(a2, FIAT_SE)
    a2.plot(yrs, W.notes_sek / 1e6, color=MONEY, lw=2.0, zorder=4)
    _dashed(a2, yrs, W.metal_reserves_sek / 1e6, **SQUARE)
    a2.text(1752, 4.4, T("银行券", "notes"), fontsize=7.8, color=MONEY, ha="center", va="bottom")
    a2.text(1752, 0.27, T("金属储备", "metal reserves"), fontsize=7.8, color=AMBER, ha="center", va="top")
    R = W.metal_reserves_sek / W.notes_sek
    for y, xy, ha in ((1745, (1740.4, 0.085), "left"), (1777, (1770.5, 6.0), "center")):
        halo(a2.annotate(T(f"{y} 年：储备 / 银行券 = {100 * R[y]:.1f}%", f"{y}: reserves / notes {100 * R[y]:.1f}%"),
                         (y, W.metal_reserves_sek[y] / 1e6), xytext=xy, fontsize=7.6, color=AMBER, ha=ha,
                         va="center", arrowprops=dict(arrowstyle="-", color=AMBER, lw=0.6, shrinkB=3), zorder=6))
    a2.set_yscale("log")
    a2.set_ylim(0.06, 25)
    _log_ticks(a2, [0.1, 0.3, 1, 3, 10])
    a2.set_xlim(1739.5, 1778)
    a2.set_xticks(range(1740, 1778, 5))
    a2.set_ylabel(T("百万瑞典克朗（对数）", "SEK millions (log)"))
    a2.set_xlabel(T("年份", "year"))
    _grid(a2)
    _title(a2, T("(b) 不兑现的三十年里，储备远远落在银行券后面", "(b) Under fiat money the reserves lagged far behind the notes"))
    return fig
