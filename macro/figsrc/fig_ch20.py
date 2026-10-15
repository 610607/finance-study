"""Figures for Chapter 20 (萨伊定律与普遍过剩之争).

Style as in fig_ch19.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series, the second series in AMBER and dashed with square markers, the panic of December 1825 and
the years of falling output shaded light grey. All numbers come from checks/check_ch20.py, which reads the snapshots
say_facts (Walras's example, English's table of loans, Reinhart and Rogoff's Table 3), boe_millennium_gb_1815_1830
and boe_millennium_gb_1822_1827_monthly. say_walras is a teaching diagram; the split of the excess supply of goods
between cloth and corn in its panel (b) is assumed.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, NullLocator

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch20 as C  # noqa: E402
from style import (AMBER, FIG_W, FISCAL, INK, LIGHT, MONEY, MUTED, OUTPUT, PRICE, T, clean_axes,  # noqa: E402
                   figure, halo, shade_periods, tint)

SQUARE = dict(marker="s", ms=3.2, mfc=AMBER, mec="white", mew=0.4)
DOT = dict(marker="o", ms=5, mec="white", mew=0.6)
PANIC = [(1825 + 11 / 12, 1826)]                 # December 1825


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


def _minus(s: str) -> str:
    return s.replace("-", "−")


# ---------------------------------------------------------------------------
@figure("say_walras")
def say_walras():
    """(a) Walras's example of §45, valued in wheat; (b) the excess demands of ex:say-walras (2) by value."""
    F = C.facts()
    p = C.WALRAS["price"]
    d_oats, s_wheat = F["wl_avoine"]
    s_oats, d_wheat = F["wl_150"]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(FIG_W, 4.3), gridspec_kw=dict(height_ratios=[1.0, 1.0]))
    fig.subplots_adjust(left=0.2, right=0.975, top=0.945, bottom=0.075, hspace=0.5)

    # (a) two pairs of bars
    xs = [0, 1, 2.6, 3.6]
    vals = [d_oats * p, s_wheat, s_oats * p, d_wheat]
    cols = [OUTPUT, AMBER, OUTPUT, AMBER]
    names = [T(f"需求燕麦\n{d_oats:g} 百升", f"oats demanded\n{d_oats:g} hl"),
             T(f"供给小麦\n{s_wheat:g} 百升", f"wheat offered\n{s_wheat:g} hl"),
             T(f"供给燕麦\n{s_oats:g} 百升", f"oats offered\n{s_oats:g} hl"),
             T(f"需求小麦\n{d_wheat:g} 百升", f"wheat demanded\n{d_wheat:g} hl")]
    a1.bar(xs, vals, width=0.72, color=[tint(c, 0.75) for c in cols], zorder=3)
    for x, v in zip(xs, vals):
        a1.text(x, v + 3, f"{v:g}", fontsize=7.8, color=INK, ha="center", va="bottom")
    for x0, x1, v in ((0, 1, vals[0]), (2.6, 3.6, vals[2])):
        a1.text((x0 + x1) / 2, v / 2, "=", fontsize=12, color=MUTED, ha="center", va="center")
    a1.set_xticks(xs)
    a1.set_xticklabels(names, fontsize=7.6)
    a1.tick_params(axis="x", length=0)
    a1.text(-0.62, 118, T("燕麦以小麦计的价格 ½", "price of oats in wheat: ½"), fontsize=7.6, color=MUTED, ha="left",
            va="center")
    a1.set_xlim(-0.65, 4.1)
    a1.set_ylim(0, 128)
    a1.set_ylabel(T("按小麦计的价值（百升）", "value in wheat (hl)"))
    _grid(a1)
    _title(a1, T(f"(a) 需求 {d_oats:g} 百升燕麦，就是供给 {s_wheat:g} 百升小麦",
                 f"(a) To demand {d_oats:g} hl of oats is to offer {s_wheat:g} hl of wheat"))

    # (b) excess demands by value
    goods = C.GOODS["buy"] - C.GOODS["sell"]
    rows = [(T("呢绒", "cloth"), C.SPLIT["cloth"], tint(OUTPUT, 0.6)),
            (T("谷物", "corn"), C.SPLIT["corn"], tint(OUTPUT, 0.6)),
            (T("货币", "money"), -goods, MONEY),
            (T("合计，包括货币", "sum with money"), C.SPLIT["cloth"] + C.SPLIT["corn"] - goods, INK),
            (T("合计，不包括货币", "sum without money"), goods, PRICE)]
    ys = [5, 4, 3, 1.5, 0.5]
    for y, (name, v, col) in zip(ys, rows):
        if v == 0:
            a2.plot([0], [y], color=INK, ls="none", zorder=5, **DOT)
        else:
            a2.barh(y, v, height=0.62, color=col, zorder=3)
        a2.text(v + (1.5 if v >= 0 else -1.5), y, _minus(f"{v:+g}") if v else "0", fontsize=7.8, color=INK,
                ha="left" if v >= 0 else "right", va="center")
    a2.axhline(2.25, color=MUTED, lw=0.6, zorder=2)
    a2.axvline(0, color=MUTED, lw=0.8, zorder=2)
    a2.set_yticks(ys)
    a2.set_yticklabels([r[0] for r in rows], fontsize=7.8)
    a2.text(29, 0.5, T("萨伊恒等式不成立", "Say's identity fails"), fontsize=7.6, color=PRICE, ha="center",
            va="center")
    a2.text(29, 1.5, T("瓦尔拉斯定律", "Walras' law"), fontsize=7.6, color=INK, ha="center", va="center")
    a2.set_xlim(-58, 58)
    a2.set_ylim(-0.1, 5.6)
    a2.set_xlabel(T("超额需求（按价值）", "excess demand (by value)"))
    _grid(a2, "x")
    _title(a2, T(f"(b) 商品合起来供过于求 {-goods:g}，货币就求过于供 {-goods:g}",
                 f"(b) Goods short of buyers by {-goods:g}, money in excess demand by {-goods:g}"))
    return fig


# ---------------------------------------------------------------------------
@figure("say_mania")
def say_mania():
    """(a) the share price indices with and without mines, 1822-1827, log scale; (b) Bank Rate, prime bills, consols."""
    Mo = C.monthly()
    t = Mo.t.values
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(FIG_W, 4.45), sharex=True, gridspec_kw=dict(height_ratios=[1.25, 1.0]))
    fig.subplots_adjust(left=0.1, right=0.975, top=0.95, bottom=0.08, hspace=0.32)

    # (a) shares
    s, x = Mo.shares_incl_mines, Mo.shares_excl_mines
    shade_periods(a1, PANIC)
    a1.plot(t, s.values, color=PRICE, lw=1.9, zorder=4)
    _dashed(a1, t, x.values)
    a1.text(1822.1, 123, T("包括矿业公司", "with mines"), fontsize=7.8, color=PRICE, ha="left", va="bottom")
    a1.text(1827.9, 93, T("不包括矿业公司", "without mines"), fontsize=7.8, color=AMBER, ha="right", va="bottom")
    pts = [((1824, 10), (1823.4, 190), "center"), ((1825, 1), (1826.4, 360), "center"),
           ((1826, 9), (1827.1, 215), "center")]
    for (y, m), xy, va in pts:
        v = s[y, m]
        tt = y + (m - 1) / 12
        a1.plot([tt], [v], color=PRICE, zorder=5, **DOT)
        halo(a1.annotate(T(f"{y} 年 {m} 月：{v:.1f}", f"{y}/{m}: {v:.1f}"), (tt, v), xytext=xy, fontsize=7.6,
                         color=PRICE, ha="center", va=va,
                         arrowprops=dict(arrowstyle="-", color=PRICE, lw=0.6, shrinkB=3), zorder=6))
    a1.text(1825.96, 72, T("1825 年 12 月", "Dec. 1825"), fontsize=7.6, color=MUTED, ha="center", va="bottom")
    a1.set_yscale("log")
    a1.set_ylim(70, 470)
    _log_ticks(a1, [80, 100, 150, 200, 300, 400])
    a1.set_ylabel(T("1840 年 6 月 = 100（对数）", "June 1840 = 100 (log)"))
    _grid(a1)
    up = s[1825, 1] / s[1824, 10]
    down = 100 * (1 - s[1826, 9] / s[1825, 1])
    _title(a1, T(f"(a) 包括矿业股的指数三个月涨到 {up:.2f} 倍，又跌掉 {down:.1f}%",
                 f"(a) With mines, shares rose {up:.2f}-fold in three months, then lost {down:.1f}%"))

    # (b) interest rates
    br, pb, cy = Mo.bank_rate, Mo.prime_bills_rate, Mo.consol_yield
    shade_periods(a2, PANIC)
    a2.step(t, br.values, where="post", color=MONEY, lw=1.9, zorder=4)
    ok = pb.notna().values
    _dashed(a2, t[ok], pb.values[ok], **SQUARE)
    ok = cy.notna().values
    a2.plot(t[ok], cy.values[ok], color=tint(MUTED, 0.55), lw=1.4, zorder=3)
    a2.text(1822.1, 5.12, T("英格兰银行贴现率", "Bank Rate"), fontsize=7.8, color=MONEY, ha="left", va="bottom")
    a2.text(1824.2, 3.6, T("优质票据", "prime bills"), fontsize=7.8, color=AMBER, ha="left", va="bottom")
    a2.text(1823.05, 4.2, T("统一公债收益率", "consol yield"), fontsize=7.8, color=tint(MUTED, 0.8), ha="left",
            va="bottom")
    a2.set_ylim(2.7, 5.6)
    a2.set_xlim(1822, 1828)
    a2.set_xticks(range(1822, 1829))
    a2.set_ylabel(T("% / 年", "% a year"))
    a2.set_xlabel(T("年份", "year"))
    _grid(a2)
    lo, hi = pb[1825, 5], pb.loc[(1825, 6):(1826, 5)].max()
    _title(a2, T(f"(b) 1825 年 5 月以后，票据利率从 {lo:g}% 升到 {hi:g}%",
                 f"(b) After May 1825 the bill rate rose from {lo:g}% to {hi:g}%"))
    return fig


# ---------------------------------------------------------------------------
@figure("say_loans")
def say_loans():
    """(a) the current yields of the fifteen loans, sorted; (b) the share of the money paid in default by year end."""
    L = C.loans().sort_values("cy").reset_index(drop=True)
    Mo = C.monthly()
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(FIG_W, 4.55), gridspec_kw=dict(height_ratios=[1.75, 1.0]))
    fig.subplots_adjust(left=0.25, right=0.975, top=0.955, bottom=0.075, hspace=0.42)

    # (a) yields
    dark, light = FISCAL, tint(FISCAL, 0.32)
    for i, r in L.iterrows():
        a1.barh(i, r.cy, height=0.66, color=dark if r.default == r.default else light, zorder=3)
        a1.text(r.cy + 0.08, i, f"{r.cy:.2f}", fontsize=7.6, color=INK, ha="left", va="center")
    a1.set_yticks(range(len(L)))
    a1.set_yticklabels([T(f"{r.zh} {r.year}（{r.coupon}%）", f"{r.en} {r.year} ({r.coupon}%)")
                        for r in L.itertuples()], fontsize=7.6)
    m24, m25 = C.consol_mean(Mo, 1824), C.consol_mean(Mo, 1825)
    for m in (m24, m25):
        a1.axvline(m, color=MUTED, lw=0.8, ls=(0, (3, 2)), zorder=4)
    a1.text(m24 - 0.08, 15.4, T(f"统一公债 1824：{m24:.2f}", f"consols 1824: {m24:.2f}"), fontsize=7.6,
            color=MUTED, ha="right", va="center")
    a1.text(m25 + 0.08, 15.4, T(f"1825：{m25:.2f}", f"1825: {m25:.2f}"), fontsize=7.6, color=MUTED, ha="left",
            va="center")
    a1.text(9.9, 2.0, T("深色：1825—1849 年违约", "dark: default in 1825–49"), fontsize=7.6, color=dark, ha="right",
            va="center")
    a1.text(9.9, 0.9, T("浅色：没有违约", "light: no default"), fontsize=7.6, color=tint(FISCAL, 0.7), ha="right",
            va="center")
    a1.set_xlim(0, 10)
    a1.set_ylim(-0.6, 16.0)
    a1.set_xlabel(T("当期收益率 = 票息 / 订约价格（%）", "current yield = coupon / contract price (%)"))
    _grid(a1, "x")
    top = 0
    for r in L.sort_values("cy", ascending=False).itertuples():
        if r.default != r.default:
            break
        top += 1
    _title(a1, T(f"(a) 收益率最高的 {top} 笔借款，全部违约", f"(a) The {top} highest-yielding loans all defaulted"))

    # (b) defaults by the end of each year
    yrs = [1825, 1826, 1827, 1828]
    sh = [C.defaulted_share(L, y) for y in yrs]
    a2.bar(yrs, sh, width=0.8, color=FISCAL, zorder=3)
    for y, v in zip(yrs, sh):
        a2.text(y, v + 2, f"{v:.1f}%", fontsize=7.8, color=INK, ha="center", va="bottom")
        new = L[L.default == y]
        if len(new):
            names = T("\n".join(dict.fromkeys(new.zh)), "\n".join(dict.fromkeys(new.en)))
            a2.text(y, v / 2, names, fontsize=7.6, color="white", ha="center", va="center", zorder=5,
                    linespacing=1.15)
    a2.set_xticks(yrs)
    a2.set_xticklabels([T(f"{y} 年底", f"end of {y}") for y in yrs])
    a2.set_xlim(1824.5, 1828.5)
    a2.set_ylim(0, 75)
    a2.set_ylabel(T("占实付的 %", "% of the money paid"))
    _grid(a2)
    _title(a2, T(f"(b) 到 1828 年底，拿到实付 {sh[-1]:.1f}% 的借款者已经违约",
                 f"(b) By the end of 1828, borrowers of {sh[-1]:.1f}% of the money had defaulted"))
    return fig


# ---------------------------------------------------------------------------
@figure("say_output")
def say_output():
    """(a) real GDP and the deflator, 1815 = 100; (b) the change of 1825-1826 by sector and industry."""
    A = C.annual()
    yrs = list(A.index)
    g = A.pct_change() * 100
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(FIG_W, 4.45), gridspec_kw=dict(height_ratios=[1.0, 1.25]))
    fig.subplots_adjust(left=0.2, right=0.975, top=0.955, bottom=0.075, hspace=0.42)

    # (a) real GDP and the deflator
    shade_periods(a1, [(1815.5, 1816.5), (1825.5, 1826.5)])
    real = 100 * A.real_gdp / A.real_gdp[1815]
    defl = 100 * A.gdp_deflator / A.gdp_deflator[1815]
    a1.plot(yrs, real, color=OUTPUT, lw=2.0, zorder=4, marker="o", ms=3, mec="white", mew=0.4)
    _dashed(a1, yrs, defl, **SQUARE)
    a1.text(1829.8, real[1830] + 3, T("实际 GDP", "real GDP"), fontsize=7.8, color=OUTPUT, ha="right", va="bottom")
    a1.text(1829.8, defl[1830] - 3, T("GDP 平减指数", "GDP deflator"), fontsize=7.8, color=AMBER, ha="right",
            va="top")
    for y, dy in ((1816, -4), (1826, -4)):
        a1.text(y, real[y] + dy, _minus(f"{g.real_gdp[y]:.1f}%"), fontsize=7.6, color=OUTPUT, ha="center", va="top")
    a1.set_xlim(1814.5, 1830.5)
    a1.set_ylim(65, 135)
    a1.set_xticks(range(1815, 1831, 5))
    a1.set_ylabel(T("1815 年 = 100", "1815 = 100"))
    _grid(a1)
    _title(a1, T(f"(a) 两次下降都只有一年；15 年里实际 GDP 增加 {C.change(A.real_gdp, 1815, 1830):.1f}%",
                 f"(a) Both falls lasted a year; real GDP grew {C.change(A.real_gdp, 1815, 1830):.1f}% in 15 years"))

    # (b) 1825-1826 by sector and industry
    rows = [(T("实际 GDP", "real GDP"), g.real_gdp[1826], INK)]
    rows += [(T(zh, en), g[c][1826], OUTPUT) for c, zh, en in C.SECTORS]
    rows += [(T(zh, en), g[c][1826], tint(OUTPUT, 0.5)) for c, zh, en in C.INDUSTRIES]
    ys = [12.2, 10.8, 9.8, 8.8] + [7.4 - i for i in range(len(C.INDUSTRIES))]
    for y, (name, v, col) in zip(ys, rows):
        a2.barh(y, v, height=0.7, color=col, zorder=3)
        a2.text(v + (0.6 if v >= 0 else -0.6), y, _minus(f"{v:+.1f}"), fontsize=7.6, color=INK,
                ha="left" if v >= 0 else "right", va="center")
    a2.axvline(0, color=MUTED, lw=0.8, zorder=2)
    a2.axhline(11.5, color=LIGHT, lw=0.8, zorder=1)
    a2.axhline(8.1, color=LIGHT, lw=0.8, zorder=1)
    a2.set_yticks(ys)
    a2.set_yticklabels([r[0] for r in rows], fontsize=7.6)
    a2.text(24, 9.8, T("三个部门", "three sectors"), fontsize=7.6, color=OUTPUT, ha="right", va="center")
    a2.text(24, 5.4, T("八个主要行业", "eight key industries"), fontsize=7.6, color=tint(OUTPUT, 0.8), ha="right",
            va="center")
    a2.set_xlim(-25, 25)
    a2.set_ylim(-0.2, 12.8)
    a2.set_xlabel(T("1825—1826 年实际产出的变化（%）", "change in real output, 1825–26 (%)"))
    _grid(a2, "x")
    down = sum(g[c][1826] < 0 for c, _, _ in C.INDUSTRIES)
    up = sum(g[c][1826] > 0 for c, _, _ in C.INDUSTRIES)
    _title(a2, T(f"(b) 1826 年：三个部门都下降，八个行业 {down} 降 {up} 升",
                 f"(b) 1826: all three sectors fell; of eight industries {down} fell, {up} rose"))
    return fig
