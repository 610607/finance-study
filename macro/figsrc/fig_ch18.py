"""Figures for Chapter 18 (亚当·斯密：分工、积累与真实票据).

Style as in fig_ch17.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series, the second series in AMBER and dashed with square markers. All numbers come from
checks/check_ch18.py, which reads the snapshots smith_facts and boe_millennium_gb_1660_1780. smith_division draws
Smith's own numbers (Book I, chapters 1 and 3); smith_banks is a schematic of two balance sheets with Smith's figures
for the Ayr Bank (Book II, chapter 2).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, NullLocator

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch18 as C  # noqa: E402
from style import (ACCENT, AMBER, EXTERNAL, FIG_W, FISCAL, INK, INSTIT, LIGHT, MONEY, MUTED, OUTPUT, PRICE, ZH, T,  # noqa: E402
                   arrow, canvas, clean_axes, figure, halo, label, rbox, tint)

SQUARE = dict(marker="s", ms=5, mfc=AMBER, mec="white", mew=0.6)
DOT = dict(marker="o", ms=5.5, mec="white", mew=0.6)
WARS = (1688, 1701, 1742, 1756)


def _title(ax, s):
    ax.set_title(s, fontsize=9.0, weight="bold", loc="left", pad=4)


def _grid(ax, axis="y"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


def _count(v: float, digits: int | None = None) -> str:
    """A count of people or things: 万 in Chinese, thousands and millions in English (`digits` decimals, or :g)."""
    fmt = (lambda x: f"{x:g}") if digits is None else (lambda x: f"{x:.{digits}f}")
    if ZH:
        return f"{fmt(v / 1e4)} 万" if v >= 1e4 else f"{v:,.0f}"
    if v >= 1e6:
        return f"{fmt(v / 1e6)} m"
    return f"{fmt(v / 1e3)}k" if v >= 1e4 and digits is not None else f"{v:,.0f}"


def _log_ticks(ax, ticks, axis="x"):
    loc = FixedLocator(ticks)
    names = [_count(t) for t in ticks]
    if axis == "x":
        ax.xaxis.set_major_locator(loc)
        ax.xaxis.set_minor_locator(NullLocator())
        ax.set_xticklabels(names)
    else:
        ax.yaxis.set_major_locator(loc)
        ax.yaxis.set_minor_locator(NullLocator())
        ax.set_yticklabels(names)


# ---------------------------------------------------------------------------
@figure("smith_division")
def smith_division():
    """(a) pins a worker a day; (b) men and horses to carry 200 tons; (c) a nailer's year against a Highland market."""
    F = C.facts()
    P, K = C.pins(F), C.carriage(F)
    one, twenty = F["wn_240"][1], F["wn_240"][0]
    fig = plt.figure(figsize=(FIG_W, 4.35))
    gs = fig.add_gridspec(3, 1, height_ratios=[1.15, 1.0, 0.8], hspace=0.95, left=0.28, right=0.96, top=0.95,
                          bottom=0.08)
    a1, a2, a3 = (fig.add_subplot(gs[i]) for i in range(3))

    # (a) pins
    rows = [(T("生手：也许一枚也做不出", "untrained: perhaps not one"), one, MUTED),
            (T("生手：肯定做不出二十枚", "untrained: certainly not twenty"), twenty, MUTED),
            (T("分了工的工场：每人", "the manufactory, each man"), P["each"], OUTPUT)]
    for i, (name, v, col) in enumerate(rows):
        y = len(rows) - 1 - i
        a1.hlines(y, 0.5, v, color=tint(col, 0.5), lw=1.2, zorder=2)
        a1.plot([v], [y], color=col, zorder=3, **DOT)
        a1.text(v * 1.35, y, f"{v:,.0f}", fontsize=7.8, color=col, ha="left", va="center")
    a1.set_yticks(range(len(rows)))
    a1.set_yticklabels([r[0] for r in reversed(rows)], fontsize=7.8)
    a1.set_xscale("log")
    a1.set_xlim(0.5, 9e4)
    _log_ticks(a1, [1, 10, 100, 1000, 10_000])
    a1.set_ylim(-0.6, 2.6)
    _grid(a1, "x")
    a1.set_xlabel(T("每人每天的别针（枚，对数刻度）", "pins a man a day (log scale)"), fontsize=8.5)
    _title(a1, T(f"(a) 分了工，每人每天做的别针是生手的 {P['x20']:,.0f} 到 {P['x1']:,.0f} 倍",
                 f"(a) Divided, each man makes {P['x20']:,.0f} to {P['x1']:,.0f} times as many pins"))

    # (b) carriage of 200 tons
    land_men, land_horses, ship_lo, ship_hi = K["men"], K["horses"], F["wn_ship"][0], F["wn_ship"][1]
    h = 0.34
    a2.barh(1 + h / 2, land_men, height=h, color=OUTPUT, zorder=3)
    a2.barh(1 - h / 2, land_horses, height=h, color=AMBER, zorder=3)
    a2.barh(0 + h / 2, ship_hi, height=h, color=tint(OUTPUT, 0.45), zorder=3)
    a2.barh(0 + h / 2, ship_lo, height=h, color=OUTPUT, zorder=3)
    a2.text(land_men + 6, 1 + h / 2, T(f"{land_men:.0f} 人", f"{land_men:.0f} men"), fontsize=7.6, color=OUTPUT,
            ha="left", va="center")
    a2.text(land_horses + 6, 1 - h / 2, T(f"{land_horses:.0f} 匹马", f"{land_horses:.0f} horses"), fontsize=7.6,
            color=AMBER, ha="left", va="center")
    a2.text(ship_hi + 6, 0 + h / 2, T(f"{ship_lo:.0f}—{ship_hi:.0f} 人，不用马", f"{ship_lo:.0f}–{ship_hi:.0f} men, no horses"),
            fontsize=7.6, color=OUTPUT, ha="left", va="center")
    a2.set_yticks([1, 0])
    a2.set_yticklabels([T(f"陆运：{K['waggons']:.0f} 辆宽轮大车", f"by land: {K['waggons']:.0f} waggons"),
                        T("水运：一条船", "by sea: one ship")], fontsize=7.8)
    a2.set_xlim(0, 470)
    a2.set_ylim(-0.45, 1.55)
    _grid(a2, "x")
    a2.set_xlabel(T("在伦敦与爱丁堡之间运送 200 吨货物需要的人与马", "men and horses to carry 200 tons, London–Edinburgh"),
                  fontsize=8.5)
    _title(a2, T(f"(b) 运同样多的货，陆运用的人是水运的 {K['x_lo']:.1f}—{K['x_hi']:.1f} 倍",
                 f"(b) The same goods by land take {K['x_lo']:.1f}–{K['x_hi']:.1f} times the men"))

    # (c) the nailer
    year, market = F["wn_nails"][2], F["wn_nails2"][0]
    for y, v, col, name in ((1, year, OUTPUT, T("一个钉匠一年能做", "a nailer can make in a year")),
                            (0, market, PRICE, T("高地偏远处一年能卖出", "a Highland place can sell in a year"))):
        a3.hlines(y, 0.5, v, color=tint(col, 0.5), lw=1.2, zorder=2)
        a3.plot([v], [y], color=col, zorder=3, **DOT)
        a3.text(v * 1.35, y, _count(v) if y else T(f"不到 {v:,.0f}", f"under {v:,.0f}"), fontsize=7.8, color=col,
                ha="left", va="center")
    a3.set_yticks([1, 0])
    a3.set_yticklabels([T("一个钉匠一年能做", "a nailer, one year"), T("高地偏远处一年能卖出", "a Highland market, one year")],
                       fontsize=7.8)
    a3.set_xscale("log")
    a3.set_xlim(0.5, 9e6)
    _log_ticks(a3, [1, 100, 10_000, 1_000_000])
    a3.set_ylim(-0.6, 1.6)
    _grid(a3, "x")
    a3.set_xlabel(T("钉子（枚，对数刻度）", "nails (log scale)"), fontsize=8.5)
    _title(a3, T("(c) 市场太小，分工就停在那里", "(c) Too small a market stops the division of labour"))
    return fig


# ---------------------------------------------------------------------------
@figure("smith_debt")
def smith_debt():
    """(a) the national debt, 1690-1780, with the four French wars; (b) real GDP per head, Great Britain and England."""
    F, B = C.facts(), C.boe()
    d, s = B["total_debt_gbp_m"].dropna(), B["debt_incl_annuities_gbp_m"].dropna()
    gb, en = B["gb_real_gdp_pc_2013gbp"].dropna(), B["england_real_gdp_pc_2013gbp"].dropna()
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(FIG_W, 4.3), sharex=True)
    fig.subplots_adjust(left=0.115, right=0.975, top=0.94, bottom=0.085, hspace=0.34)

    # (a) debt
    for w in WARS:
        a1.axvline(w, color=MUTED, lw=0.7, ls=(0, (1, 2)), zorder=1)
        a1.text(w + 0.8, 222, str(w), fontsize=7.6, color=MUTED, ha="left", va="top")
    smith = F["wn_145"][0] / 1e6
    a1.axhline(smith, color=FISCAL, lw=0.7, ls=(0, (4, 2)), zorder=1)
    a1.text(1662, smith + 4, T(f"斯密：“超过 {smith / 100:.2f} 亿英镑”", f"Smith: “more than £{F['wn_145'][0]:,.0f}”"),
            fontsize=7.6, color=FISCAL, ha="left", va="bottom")
    line, = a1.plot(s.index, s.values, color=AMBER, lw=1.6, zorder=3)
    line.set_dashes((4, 2))
    a1.plot(d.index, d.values, color=FISCAL, lw=2.0, zorder=4)
    for y, xy in ((1700, (1697, 46)), (1763, (1752, 170)), (1776, (1772, 108))):
        v = d.loc[y]
        txt = T(f"{y} 年：{v * 100:,.0f} 万" if v < 100 else f"{y} 年：{v / 100:.3f} 亿", f"{y}: £{v:.1f}m")
        a1.plot([y], [v], color=FISCAL, zorder=5, **DOT)
        halo(a1.annotate(txt, (y, v), xytext=xy, fontsize=7.6, color=FISCAL, ha="center", va="center", zorder=6,
                         arrowprops=dict(arrowstyle="-", color=FISCAL, lw=0.6, shrinkB=3)))
    a1.text(1714, 66, T("国债面值", "debt at par"), fontsize=7.8, color=FISCAL, ha="center", va="bottom")
    a1.text(1727, 22, T("另加定期年金的资本价值", "including terminable annuities"), fontsize=7.6, color=AMBER,
            ha="left", va="top")
    a1.set_ylim(0, 225)
    a1.set_ylabel(T("百万英镑", "£ millions"))
    _grid(a1)
    _title(a1, T("(a) 国债：每一次对法战争都把它推上一个台阶", "(a) The national debt: each French war added a step"))

    # (b) GDP per head
    a2.plot(en.index, en.values, color=tint(OUTPUT, 0.55), lw=1.4, zorder=2)
    line, = a2.plot(gb.index, gb.values, color=OUTPUT, lw=2.0, zorder=3)
    for y, xy in ((1700, (1716, 1300)), (1776, (1768, 1700))):
        v = gb.loc[y]
        a2.plot([y], [v], color=OUTPUT, zorder=4, **DOT)
        halo(a2.annotate(T(f"{y} 年：{v:,.0f}", f"{y}: {v:,.0f}"), (y, v), xytext=xy, fontsize=7.6, color=OUTPUT,
                         ha="center", va="top", zorder=6,
                         arrowprops=dict(arrowstyle="-", color=OUTPUT, lw=0.6, shrinkB=3)))
    g = 100 * (gb.loc[1776] / gb.loc[1700] - 1)
    a2.text(1738, 1480, T(f"大不列颠：1700—1776 年共增长 {g:.1f}%", f"Great Britain: +{g:.1f}% in 1700–1776"),
            fontsize=7.8, color=OUTPUT, ha="left", va="center")
    a2.text(1664, 1010, T("英格兰", "England"), fontsize=7.8, color=tint(OUTPUT, 0.75), ha="left", va="bottom")
    for w in WARS:
        a2.axvline(w, color=MUTED, lw=0.7, ls=(0, (1, 2)), zorder=1)
    a2.set_ylim(900, 2300)
    a2.set_xlim(1660, 1781)
    a2.set_xticks(range(1660, 1781, 20))
    a2.set_xlabel(T("年份", "year"))
    a2.set_ylabel(T("2013 年英镑", "2013 £"))
    _grid(a2)
    _title(a2, T("(b) 人均实际 GDP：增长慢，但没有停下来", "(b) Real GDP per head: slow, but it did not stop"))
    return fig


# ---------------------------------------------------------------------------
def _sheet(ax, x, y, w, h, head, assets, liabs, color):
    """A T-account: a dark title band, assets on the left, liabilities on the right. Returns the item boxes."""
    rbox(ax, x, y + h - 0.5, w, 0.5, fc=tint(ACCENT, 0.88), r=0.1, z=3)
    label(ax, x + w / 2, y + h - 0.25, head, color="white", size=8.4, weight="bold", z=4)
    rbox(ax, x, y, w, h - 0.55, fc=tint(color, 0.05), ec=tint(color, 0.45), lw=0.8, r=0.1, z=2)
    ax.plot([x + w / 2, x + w / 2], [y + 0.12, y + h - 0.68], color=tint(color, 0.45), lw=0.8, zorder=3)
    label(ax, x + w / 4, y + h - 0.8, T("资产", "assets"), size=7.8, color=MUTED, z=4)
    label(ax, x + 3 * w / 4, y + h - 0.8, T("负债", "liabilities"), size=7.8, color=MUTED, z=4)
    boxes = {}
    for side, items in (("a", assets), ("l", liabs)):
        x0 = x + 0.15 if side == "a" else x + w / 2 + 0.15
        top = y + h - 1.05
        for key, txt, hh, col in items:
            rbox(ax, x0, top - hh, w / 2 - 0.3, hh, fc=tint(col, 0.14), ec=tint(col, 0.6), lw=0.9, r=0.08, z=3)
            label(ax, x0 + (w / 2 - 0.3) / 2, top - hh / 2, txt, size=7.6, color=INK, z=4)
            boxes[key] = (x0, top - hh, w / 2 - 0.3, hh)
            top -= hh + 0.12
    return boxes


def _party(ax, x, y, w, h, txt, color):
    rbox(ax, x, y, w, h, fc="white", ec=tint(color, 0.6), lw=0.9, r=0.08, z=3)
    label(ax, x + w / 2, y + h / 2, txt, size=7.6, color=color, z=4)


@figure("smith_banks")
def smith_banks():
    """(a) a bank that discounts only real bills; (b) the Ayr Bank when it stopped, with Smith's figures."""
    F, Y = C.facts(), C.years()
    notes, london, loans = F["wn_200k"][0], F["wn_600k"][0], F["wn_800k"][0]
    rate, months = F["wn_800k"][1], F["wn_AB"][0]
    W, H = 10.4, 5.0
    fig, ax = canvas(FIG_W, FIG_W * H / W, xlim=(0, W), ylim=(0, H))
    sw, sh, y0 = 4.4, 3.35, 1.25
    inner = sh - 1.17                                   # height of the item columns
    ya, yp = 0.15, 0.55                                 # the parties below the balance sheets

    # (a) the real-bills bank
    xa = 0.3
    label(ax, xa, H - 0.05, T("(a) 只贴现真实票据：流出去的会流回来", "(a) Real bills only: what goes out comes back"),
          size=8.8, weight="bold", ha="left", va="top")
    b = _sheet(ax, xa, y0, sw, sh, T("真实票据银行", "a real-bills bank"),
               [("res", T("金银准备", "gold and silver"), 0.5, EXTERNAL),
                ("bills", T(f"商业票据\n{months:.0f} 个月内到期", f"trade bills due\nwithin {months:.0f} months"),
                 inner - 0.5 - 0.12, MONEY)],
               [("notes", T("银行券", "notes"), inner, MONEY)], MONEY)
    _party(ax, xa + 0.9, ya, sw - 1.8, yp, T("商人：真实票据的债务人", "merchants (the debtors)"), INK)
    bx, by, bw, bh = b["bills"]
    x_out, x_in = xa + 1.25, xa + sw - 1.25
    arrow(ax, (x_out, y0 + 0.02), (x_out, ya + yp + 0.02), color=MONEY, lw=1.3, ms=9)
    arrow(ax, (x_in, ya + yp + 0.02), (x_in, y0 + 0.02), color=OUTPUT, lw=1.3, ms=9)
    label(ax, x_out - 0.1, (y0 + ya + yp) / 2, T("贴现：\n放出银行券", "discount:\nnotes out"), size=7.6, color=MONEY,
          ha="right")
    label(ax, x_in + 0.1, (y0 + ya + yp) / 2, T("到期付清：\n钱流回", "bills paid:\nmoney back"), size=7.6,
          color=OUTPUT, ha="left")
    label(ax, xa + sw / 2, (y0 + ya + yp) / 2, T("“像一个水池”", "“a water-pond”"), size=7.6, color=MUTED)

    # (b) the Ayr Bank
    xb = W - 0.3 - sw
    label(ax, xb, H - 0.05, T("(b) 艾尔银行：放出去的回不来", "(b) The Ayr Bank: what goes out stays out"), size=8.8,
          weight="bold", ha="left", va="top")
    k = (inner - 0.12) / (notes + london)               # liabilities in proportion to Smith's sums
    b = _sheet(ax, xb, y0, sw, sh, T(f"艾尔银行，{Y['rk_june22']} 年 6 月", f"the Ayr Bank, June {Y['rk_june22']}"),
               [("loans", T(f"贷款\n超过 {_count(loans)}英镑\n利率 {rate:g}%\n\n改良土地\n续借的循环汇票",
                            f"loans\nupwards of\n£{loans / 1e3:.0f},000\nat {rate:g}%\n\nland,\ncirculating bills"), inner,
                 PRICE)],
               [("notes", T(f"银行券\n约 {_count(notes)}英镑", f"notes ≈ £{notes / 1e3:.0f},000"), k * notes, MONEY),
                ("london", T(f"在伦敦开出的汇票\n超过 {_count(london)}英镑", f"bills on London,\nupwards of\n£{london / 1e3:.0f},000"),
                 k * london, FISCAL)], PRICE)
    lx, ly, lw_, lh = b["loans"]
    gx, gy, gw, gh = b["london"]
    _party(ax, lx, ya, lw_, yp, T("借款人", "borrowers"), PRICE)
    _party(ax, gx, ya, gw, yp, T("伦敦的代理行", "London agents"), FISCAL)
    xl = lx + lw_ / 2
    arrow(ax, (xl, y0 + 0.02), (xl, ya + yp + 0.02), color=PRICE, lw=1.3, ms=9)
    label(ax, xl + 0.1, (y0 + ya + yp) / 2, T("回收很慢", "slow to\ncome back"), size=7.6, color=PRICE, ha="left")
    xg = gx + gw / 2
    arrow(ax, (xg - 0.6, ya + yp + 0.02), (xg - 0.6, y0 + 0.02), color=FISCAL, lw=1.3, ms=9)
    arrow(ax, (xg - 0.2, y0 + 0.02), (xg - 0.2, ya + yp + 0.02), color=FISCAL, lw=1.3, ms=9)
    label(ax, xg - 0.05, (y0 + ya + yp) / 2, T("开新票\n还旧票", "new bills\npay old"), size=7.6, color=FISCAL,
          ha="left")
    return fig


# ---------------------------------------------------------------------------
@figure("smith_population")
def smith_population():
    """(a) population of the American colonies and of England, log scale; (b) doubling times against Smith's claims."""
    F, B, Cn = C.facts(), C.boe(), C.colonies()
    pa, pb = C.qing()
    en = B["pop_england_m"].dropna() * 1e6
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(FIG_W, 4.5), gridspec_kw=dict(height_ratios=[1.1, 1.0]))
    fig.subplots_adjust(left=0.26, right=0.96, top=0.945, bottom=0.08, hspace=0.42)

    # (a) levels
    a1.plot(en.index, en.values, color=tint(OUTPUT, 0.5), lw=1.4, zorder=2)
    a1.plot(Cn.index, Cn.total, color=OUTPUT, lw=2.0, zorder=3, **DOT)
    line, = a1.plot(Cn.index, Cn.negro, color=AMBER, lw=1.6, zorder=4, **SQUARE)
    line.set_dashes((4, 2))
    a1.text(1700, en.loc[1700] * 1.3, T("英格兰", "England"), fontsize=7.8, color=tint(OUTPUT, 0.75), ha="center",
            va="bottom")
    a1.text(1634, 2e5, T("北美殖民地", "American colonies"), fontsize=7.8, color=OUTPUT, ha="left", va="bottom")
    for y, xy in ((1700, (1700, 8e5)), (1770, (1745, 2.9e6))):
        v = Cn.total[y]
        halo(a1.annotate(T(f"{y} 年：{_count(v, 1)}", f"{y}: {_count(v, 0 if v < 1e6 else 2)}"), (y, v), xytext=xy,
                         fontsize=7.6, color=OUTPUT, ha="center", va="center", zorder=6,
                         arrowprops=dict(arrowstyle="-", color=OUTPUT, lw=0.6, shrinkB=3)))
    a1.text(1712, Cn.negro[1710] * 0.4, T("其中的黑人", "of whom Negroes"), fontsize=7.8, color=AMBER, ha="left",
            va="top")
    a1.set_yscale("log")
    a1.set_ylim(30, 2e7)
    _log_ticks(a1, [1e2, 1e3, 1e4, 1e5, 1e6, 1e7], axis="y")
    a1.set_xlim(1625, 1785)
    a1.set_xticks(range(1640, 1781, 20))
    a1.set_ylabel(T("人（对数刻度）", "people (log scale)"))
    _grid(a1)
    _title(a1, T("(a) 北美的线比英格兰陡得多", "(a) The colonies' line is far steeper than England's"))

    # (b) doubling times
    rows = [(T("北美殖民地 1700—1770", "colonies 1700–1770"), C.doubling(Cn.total[1700], Cn.total[1770], 70), OUTPUT),
            (T("其中白人 1700—1770", "whites 1700–1770"), C.doubling(Cn.white[1700], Cn.white[1770], 70), OUTPUT),
            (T("其中黑人 1700—1770", "Negroes 1700–1770"), C.doubling(Cn.negro[1700], Cn.negro[1770], 70), AMBER),
            (T("清代登记民数 1764—1795", "Qing registers 1764–1795"), C.doubling(pa, pb, 1795 - 1764), INSTIT),
            (T("英格兰 1750—1780", "England 1750–1780"), C.doubling(B.pop_england_m[1750], B.pop_england_m[1780], 30),
             tint(OUTPUT, 0.5)),
            (T("英格兰 1700—1770", "England 1700–1770"), C.doubling(B.pop_england_m[1700], B.pop_england_m[1770], 70),
             tint(OUTPUT, 0.5))]
    lo, hi = F["wn_double"][1], F["wn_double"][2]
    europe = F["wn_double"][0]
    a2.axvspan(lo, hi, color=tint(OUTPUT, 0.12), lw=0, zorder=1)
    a2.axvline(europe, color=MUTED, lw=0.9, ls=(0, (1, 2)), zorder=1)
    for i, (name, v, col) in enumerate(rows):
        y = len(rows) - 1 - i
        a2.barh(y, v, height=0.6, color=col, zorder=3)
        a2.text(v + 6, y, f"{v:.1f}" if v < 50 else f"{v:.0f}", fontsize=7.6, color=INK, ha="left", va="center")
    a2.set_yticks(range(len(rows)))
    a2.set_yticklabels([r[0] for r in reversed(rows)], fontsize=7.8)
    a2.text(hi + 4, len(rows) - 0.35, T(f"斯密：北美 {lo:.0f}—{hi:.0f} 年", f"Smith: colonies {lo:.0f}–{hi:.0f}"),
            fontsize=7.6, color=OUTPUT, ha="left", va="center")
    a2.text(europe - 6, 1.5, T(f"斯密：欧洲\n至少 {europe:.0f} 年", f"Smith: Europe,\nat least {europe:.0f}"),
            fontsize=7.6, color=MUTED, ha="right", va="center", linespacing=1.2)
    a2.set_xlim(0, 540)
    a2.set_ylim(-0.6, len(rows) - 0.1)
    a2.set_xlabel(T("翻一番所需的年数", "years to double"))
    _grid(a2, "x")
    _title(a2, T("(b) 北美合于斯密的说法，英格兰比他说的快得多", "(b) The colonies fit Smith; England was far faster than he said"))
    return fig
