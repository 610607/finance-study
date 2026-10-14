"""Figures for Chapter 4 (货币、银行与央行的资产负债表).

Style as in fig_ch03.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series, the second series of a panel in AMBER, dashed. Colours follow §7: money, reserves and
interest rates MONEY (currency a lighter tint), the Treasury's account and claims on the government FISCAL, foreign
assets and dollarization EXTERNAL, inflation PRICE, everything else INSTIT; in the two balance sheets the crisis
lending of 2008 and the central bank bills of the PBoC, the items the text is about, are AMBER. Every number comes
from checks/check_ch04.py, which reads the snapshots fred_fed_weekly, fred_money_monthly, fred_policy_rates_daily,
pbc_balance_sheet and bcrp_dollarization.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FixedLocator, NullLocator

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch04 as C  # noqa: E402
from style import (AMBER, EXTERNAL, FIG_W, FISCAL, INK, INSTIT, LIGHT, MONEY, MUTED, PRICE, T, clean_axes,  # noqa: E402
                   figure, tint)

SQUARE = dict(marker="s", ms=4.6, mfc=AMBER, mec="white", mew=0.6)
DOT = dict(marker="o", ms=5.0, mec="white", mew=0.6)
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


def _years(ax, years):
    ax.set_xticks([pd.Timestamp(f"{y}-01-01") for y in years])
    ax.set_xticklabels([str(y) for y in years])


def _stack(ax, t, layers):
    """Stacked areas; layers is a list of (values, colour, label, (x, y) of the label or None, label colour)."""
    base = np.zeros(len(t))
    for v, col, lab, at, lc in layers:
        top = base + np.asarray(v, dtype=float)
        ax.fill_between(t, base, top, color=col, lw=0, zorder=2)
        if at is not None:
            ax.text(*at, lab, color=lc, fontsize=7.6, ha="left", va="center", zorder=5, linespacing=1.25)
        base = top
    return base


@figure("money_mult")
def money_mult():
    M = C.money()
    t = M.index
    a, b = (pd.Timestamp(d) for d in C.MULT_MONTHS)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIG_W, 2.85), gridspec_kw=dict(wspace=0.3))
    ax1.plot(t, M.M2NS, color=MONEY, lw=2.0, zorder=3)
    ax1.plot(t, M.BOGMBASE, color=AMBER, lw=2.0, dashes=(4, 2), zorder=3)
    ax1.set_yscale("log")
    ax1.text(pd.Timestamp("1962-01-01"), T(3000, 4200), T("广义货币 M2", "broad money (M2)"), color=MONEY, fontsize=7.8,
             ha="left", va="center")
    ax1.text(pd.Timestamp("1986-01-01"), 120, T("基础货币", "base money"), color=AMBER, fontsize=7.8, ha="left",
             va="center")
    ax1.axvspan(pd.Timestamp("2008-08-01"), pd.Timestamp("2008-12-31"), color=tint(MONEY, 0.12), lw=0, zorder=1)
    ax1.annotate(T(f"2008 年 8—12 月：基础货币 ×{M.loc[b, 'BOGMBASE'] / M.loc[a, 'BOGMBASE']:.2f}，\n"
                   f"M2 只增长 {100 * (M.loc[b, 'M2NS'] / M.loc[a, 'M2NS'] - 1):.1f}%",
                   f"Aug–Dec 2008:\nbase money ×{M.loc[b, 'BOGMBASE'] / M.loc[a, 'BOGMBASE']:.2f},\n"
                   f"M2 only +{100 * (M.loc[b, 'M2NS'] / M.loc[a, 'M2NS'] - 1):.1f}%"),
                 (b, M.loc[b, "BOGMBASE"]), xytext=(pd.Timestamp(T("1989-01-01", "1962-01-01")), T(50, 19000)), fontsize=7.6, color=INK,
                 ha="left", va="center", linespacing=1.3, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    ax1.set_ylim(30, 60000)
    ax1.yaxis.set_major_locator(FixedLocator([100, 1000, 10000]))
    ax1.yaxis.set_minor_locator(NullLocator())
    ax1.set_yticklabels(["100", "1,000", "10,000"])
    ax1.set_xlim(pd.Timestamp("1958-01-01"), pd.Timestamp("2028-01-01"))
    _years(ax1, [1960, 1980, 2000, 2020])
    ax1.set_ylabel(T("十亿美元（对数）", "billion dollars (log scale)"), fontsize=9)
    _grid(ax1)
    _title(ax1, T("(a) 2008 年以后两条线分开了", "(a) After 2008 the lines part"))

    ax2.plot(t, M.m, color=MONEY, lw=2.0, zorder=3)
    # (month, horizontal offset in months, vertical offset, va, ha)
    for d, dm, dy, va, ha in ((a, 0, 0.55, "bottom", "center"), (b, -10, 0.0, "center", "right"),
                              (M.m.idxmin(), 0, -0.5, "top", "center"), (t[-1], -40, 1.0, "bottom", "center")):
        ax2.plot([d], [M.loc[d, "m"]], color=MONEY, zorder=4, **dict(DOT, mfc=MONEY))
        lab = T(f"{d.year} 年 {d.month} 月\n{M.loc[d, 'm']:.2f}", f"{d:%b %Y}\n{M.loc[d, 'm']:.2f}")
        ax2.text(d + pd.DateOffset(months=dm), M.loc[d, "m"] + dy, lab, color=MONEY, fontsize=7.6, ha=ha, va=va,
                 linespacing=1.2)
    ax2.set_xlim(pd.Timestamp("1958-01-01"), pd.Timestamp("2029-06-01"))
    ax2.set_ylim(0, 13.5)
    _years(ax2, [1960, 1980, 2000, 2020])
    ax2.set_ylabel(T("M2 ÷ 基础货币", "M2 ÷ base money"), fontsize=9)
    _grid(ax2)
    _title(ax2, T("(b) “乘数”不是常数", "(b) The “multiplier” is no constant"))
    fig.subplots_adjust(left=0.115, right=0.98, top=0.9, bottom=0.1)
    return fig


@figure("money_fed")
def money_fed():
    W = C.fed().loc["2007-01-01":]
    t = W.index
    tn = 1e6
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIG_W, 2.95), sharey=True, gridspec_kw=dict(wspace=0.1))
    x0 = pd.Timestamp("2007-03-01")
    _stack(ax1, t, [
        (W.TREAST / tn, MONEY, T("美国国债", "Treasury\nsecurities"), (pd.Timestamp("2020-09-01"), T(2.6, 1.9)), "white"),
        (W.WSHOMCB / tn, tint(MONEY, 0.45), T("抵押贷款\n支持证券", "mortgage-\nbacked\nsecurities"),
         (pd.Timestamp("2014-09-01"), T(3.35, 3.4)), INK),
        (W.other_assets / tn, tint(AMBER, 0.6), T("其他（2008 年\n多为流动性便利）", "other (in 2008\nmostly facilities)"),
         (x0, 5.6), AMBER),
    ])
    ax1.annotate("", (pd.Timestamp("2008-12-15"), 1.9), xytext=(pd.Timestamp("2008-06-01"), 5.0),
                 arrowprops=dict(arrowstyle="-", color=AMBER, lw=0.6))
    last = t[-1]
    ax1.text(last, W.WALCL.iloc[-1] / tn + 0.25, f"{W.WALCL.iloc[-1] / tn:.2f}", color=INK, fontsize=7.6, ha="right",
             va="bottom")
    pk = W.WALCL.idxmax()
    ax1.text(pk, W.WALCL.max() / tn + 0.25, T(f"峰值 {W.WALCL.max() / tn:.2f}", f"peak {W.WALCL.max() / tn:.2f}"),
             color=INK, fontsize=7.6, ha="center", va="bottom")
    ax1.set_ylim(0, 10.3)
    ax1.set_xlim(t[0], pd.Timestamp("2027-01-01"))
    _years(ax1, [2008, 2014, 2020, 2026])
    ax1.set_ylabel(T("万亿美元", "trillion dollars"), fontsize=9)
    _grid(ax1)
    _title(ax1, T("(a) 资产：从流动性便利到证券", "(a) Assets: from facilities to securities"))

    _stack(ax2, t, [
        (W.WLFN / tn, tint(MONEY, 0.45), T("联邦储备券（现钞）", "Federal Reserve notes"), (x0, 0.45), INK),
        (W.WLODLL / tn, MONEY, T("准备金余额", "reserve balances"), (pd.Timestamp("2012-01-01"), 2.3), "white"),
        (W.WDTGAL / tn, FISCAL, T("财政部一般账户", "Treasury General\nAccount"), (pd.Timestamp("2011-01-01"), 5.7),
         FISCAL),
        (W.WLRRAL / tn, tint(MONEY, 0.2), T("逆回购", "reverse repos"), (pd.Timestamp(T("2023-06-01", "2017-08-01")), T(9.25, 9.45)),
         MONEY),
        (W.other_liab / tn, tint(INSTIT, 0.35), "", None, INK),
    ])
    ax2.annotate("", (pd.Timestamp("2016-06-01"), 4.15), xytext=(pd.Timestamp("2014-06-01"), 5.4),
                 arrowprops=dict(arrowstyle="-", color=FISCAL, lw=0.6))
    ax2.annotate("", (pd.Timestamp("2022-12-01"), 8.2), xytext=(pd.Timestamp("2023-05-01"), 9.2),
                 arrowprops=dict(arrowstyle="-", color=MONEY, lw=0.6))
    ax2.text(pd.Timestamp("2007-06-01"), 7.6, T("其他负债与资本（浅灰）", "other liabilities and\ncapital (light grey)"),
             color=INSTIT, fontsize=7.6, ha="left", va="center", linespacing=1.25)
    ax2.set_xlim(t[0], pd.Timestamp("2027-01-01"))
    _years(ax2, [2008, 2014, 2020, 2026])
    _grid(ax2)
    ax2.tick_params(labelleft=False)
    _title(ax2, T("(b) 负债：准备金成了大头", "(b) Liabilities: reserves dominate"))
    fig.subplots_adjust(left=0.075, right=0.985, top=0.9, bottom=0.1)
    return fig


@figure("money_rates")
def money_rates():
    R = C.rates()
    Wk = C.fed()
    d = R.loc["2007-01-01":]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIG_W, 2.95), gridspec_kw=dict(width_ratios=[1.25, 1.0], wspace=0.3))
    # target (to 2008-12-15) and target range (from 2008-12-16)
    tgt = d.DFEDTAR.dropna()
    ax1.plot(tgt.index, tgt, color=INSTIT, lw=1.0, zorder=2)
    rng = d[["DFEDTARL", "DFEDTARU"]].dropna()
    ax1.fill_between(rng.index, rng.DFEDTARL, rng.DFEDTARU, color=tint(INSTIT, 0.35), lw=0, zorder=1, step="post")
    ior = d.IOR.dropna()
    ax1.plot(ior.index, ior, color=AMBER, lw=1.5, dashes=(4, 2), zorder=3)
    rrp = d.RRPONTSYAWARD.dropna()
    ax1.plot(rrp.index, rrp, color=tint(MONEY, 0.5), lw=1.1, ls=":", zorder=3)
    ef = d.EFFR.dropna()
    ax1.plot(ef.index, ef, color=MONEY, lw=1.1, zorder=4)
    ax1.text(pd.Timestamp("2009-06-01"), 0.72, T("目标区间（灰带）", "target range\n(grey band)"), color=INSTIT,
             fontsize=7.6, ha="left", va="center", linespacing=1.25)
    ax1.text(pd.Timestamp("2016-01-01"), 5.45, T("准备金利率（虚线）", "interest on reserves\n(dashed)"), color=AMBER,
             fontsize=7.6, ha="left", va="center", linespacing=1.25)
    ax1.annotate("", (pd.Timestamp("2023-03-01"), 4.95), xytext=(pd.Timestamp("2021-06-01"), 5.3),
                 arrowprops=dict(arrowstyle="-", color=AMBER, lw=0.6))
    ax1.text(pd.Timestamp("2009-04-01"), 1.5, T("隔夜逆回购利率（点线）", "ON RRP rate (dotted)"), color=MONEY,
             fontsize=7.6, ha="left", va="center")
    ax1.annotate("", (pd.Timestamp(T("2014-09-01", "2015-06-01")), 0.08),
                 xytext=(pd.Timestamp(T("2013-06-01", "2015-01-01")), 1.35),
                 arrowprops=dict(arrowstyle="-", color=MONEY, lw=0.6))
    ax1.text(pd.Timestamp("2009-06-01"), 4.4, T("联邦基金有效利率\n（蓝色实线）", "effective federal funds\nrate (blue line)"),
             color=MONEY, fontsize=7.6, ha="left", va="center", linespacing=1.25)
    ax1.annotate("", (pd.Timestamp("2007-12-01"), 4.25), xytext=(pd.Timestamp("2009-05-01"), 4.4),
                 arrowprops=dict(arrowstyle="-", color=MONEY, lw=0.6))
    ax1.set_ylim(-0.2, 6.2)
    ax1.set_xlim(pd.Timestamp("2007-01-01"), pd.Timestamp("2027-03-01"))
    _years(ax1, [2008, 2014, 2020, 2026])
    ax1.set_ylabel("%", fontsize=9)
    _grid(ax1)
    _title(ax1, T("(a) 管理利率框住市场利率", "(a) Administered rates frame the market"))

    J = C.weekly_spread(Wk, R)
    groups = ((slice("2009", "2015"), tint(MONEY, 0.3), T("2009—2015", "2009–2015")),
              (slice("2016", "2021"), tint(MONEY, 0.6), T("2016—2021", "2016–2021")),
              (slice("2022", "2026"), MONEY, T("2022—2026", "2022–2026")))
    for sl, col, lab in groups:
        g = J.loc[sl]
        ax2.scatter(g.res, g.sp, s=7, color=col, lw=0, zorder=3)
    ax2.axhline(0, color=MUTED, lw=0.7, ls=":", zorder=1)
    for (sl, col, lab), (x, y) in zip(groups, ((1.0, -21.0), (2.7, 7.5), (3.65, 3.0))):
        ax2.text(x, y, lab, color=col if col != tint(MONEY, 0.3) else tint(MONEY, 0.55), fontsize=7.6, ha="center",
                 va="center")
    s19 = J.loc["2019-09-18"]
    ax2.plot([s19.res], [s19.sp], color=AMBER, zorder=5, **SQUARE)
    ax2.annotate(T(f"2019 年 9 月 18 日\n准备金 {s19.res:.2f} 万亿美元", f"18 Sep 2019\nreserves ${s19.res:.2f} tn"),
                 (s19.res, s19.sp), xytext=(1.85, 15.5), fontsize=7.6, color=AMBER, ha="left", va="center",
                 linespacing=1.25, arrowprops=dict(arrowstyle="-", color=AMBER, lw=0.6))
    ax2.set_xlim(0.4, 4.5)
    ax2.set_ylim(-25, 21)
    ax2.set_xlabel(T("准备金余额（万亿美元，周三）", "reserve balances ($ tn, Wednesday)"), fontsize=9)
    ax2.set_ylabel(T("有效利率 − 准备金利率（基点）", "EFFR − interest on reserves (bp)"), fontsize=9)
    _grid(ax2, axis="both")
    _title(ax2, T("(b) 准备金少了，利差就抬头", "(b) Fewer reserves, a higher spread"))
    fig.subplots_adjust(left=0.07, right=0.985, top=0.9, bottom=0.16)
    return fig


@figure("money_pbc")
def money_pbc():
    P = C.pbc()
    t = pd.to_datetime(P.index + "-01")
    wy = 1e4
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIG_W, 2.95), sharey=True, gridspec_kw=dict(wspace=0.1))
    other_foreign = P.foreign_assets - P.fx
    other_a = P.total_assets - P.foreign_assets - P.claims_banks - P.claims_gov
    _stack(ax1, t, [
        (P.fx / wy, EXTERNAL, T("外汇", "foreign\nexchange"), (pd.Timestamp("2008-06-01"), 9.0), "white"),
        (other_foreign / wy, tint(EXTERNAL, 0.45), "", None, INK),
        (P.claims_gov / wy, FISCAL, "", None, INK),
        (P.claims_banks / wy, MONEY, T("对其他存款性\n公司债权", "claims on\nbanks"),
         (pd.Timestamp("2019-09-01"), 31.5), "white"),
        (other_a / wy, tint(INSTIT, 0.35), "", None, INK),
    ])
    ax1.text(pd.Timestamp("2002-06-01"), 42.0, T("对政府债权（紫）", "claims on government\n(purple)"), color=FISCAL,
             fontsize=7.6, ha="left", va="center", linespacing=1.25)
    ax1.text(pd.Timestamp("2002-06-01"), T(35.5, 34.6), T("黄金与其他国外资产\n（浅橙）", "gold, other foreign\nassets (light orange)"),
             color=EXTERNAL, fontsize=7.6, ha="left", va="center", linespacing=1.25)
    pk = pd.Timestamp(P.fx_sh.idxmax() + "-01")
    ax1.annotate(T(f"外汇占总资产 {P.fx_sh.max():.1f}%", f"FX {P.fx_sh.max():.1f}% of assets"),
                 (pk, P.loc[P.fx_sh.idxmax(), "fx"] / wy * 0.85), xytext=(pd.Timestamp("2002-06-01"), 30.0),
                 fontsize=7.6, color=EXTERNAL, ha="left", va="center", arrowprops=dict(arrowstyle="-", color=EXTERNAL, lw=0.6))
    ax1.set_ylim(0, 52)
    ax1.set_xlim(t[0], pd.Timestamp("2027-01-01"))
    _years(ax1, [2002, 2008, 2014, 2020, 2026])
    ax1.set_ylabel(T("万亿元", "trillion yuan"), fontsize=9)
    _grid(ax1)
    _title(ax1, T("(a) 资产：从外汇到对银行的贷款", "(a) Assets: from FX to loans to banks"))

    other_l = P.total_liab - P.currency - P.bank_deposits - P.bonds.fillna(0) - P.gov_deposits
    _stack(ax2, t, [
        (P.currency / wy, tint(MONEY, 0.45), T("货币发行", "currency issue"), (pd.Timestamp("2015-01-01"), 3.5), INK),
        (P.bank_deposits / wy, MONEY, T("其他存款性公司存款\n（准备金）", "bank deposits\n(reserves)"),
         (pd.Timestamp("2014-03-01"), 17.5), "white"),
        (P.bonds.fillna(0) / wy, tint(AMBER, 0.65), T("发行债券\n（央行票据）", "bonds issued\n(central bank\nbills)"),
         (pd.Timestamp("2002-06-01"), T(27.0, 28.0)), AMBER),
        (P.gov_deposits / wy, FISCAL, T("政府存款", "government\ndeposits"),
         (pd.Timestamp(T("2021-01-01", "2014-06-01")), T(43.5, 45.0)), FISCAL),
        (other_l / wy, tint(INSTIT, 0.35), "", None, INK),
    ])
    bp = pd.Timestamp(P.bonds.idxmax() + "-01")
    ax2.annotate(T(f"峰值 {P.bonds.max() / wy:.2f}", f"peak {P.bonds.max() / wy:.2f}"),
                 (bp, (P.loc[P.bonds.idxmax(), ["currency", "bank_deposits"]].sum() + P.bonds.max() / 2) / wy),
                 xytext=(pd.Timestamp("2004-06-01"), 21.5), fontsize=7.6, color=AMBER, ha="left", va="center",
                 arrowprops=dict(arrowstyle="-", color=AMBER, lw=0.6))
    ax2.annotate("", (pd.Timestamp("2024-06-01"), 40.0), xytext=(pd.Timestamp(T("2022-06-01", "2019-09-01")), T(42.6, 43.6)),
                 arrowprops=dict(arrowstyle="-", color=FISCAL, lw=0.6))
    ax2.set_xlim(t[0], pd.Timestamp("2027-01-01"))
    _years(ax2, [2002, 2008, 2014, 2020, 2026])
    _grid(ax2)
    ax2.tick_params(labelleft=False)
    _title(ax2, T("(b) 负债：央票先升后退", "(b) Liabilities: the bills come and go"))
    fig.subplots_adjust(left=T(0.075, 0.085), right=0.985, top=0.9, bottom=0.1)
    return fig


@figure("money_peru")
def money_peru():
    B = C.peru()
    t = pd.to_datetime(B.index + "-01")
    p = B.cpi_12m_pct
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIG_W, 2.85), gridspec_kw=dict(wspace=0.32))
    y = np.log10(1 + p / 100)
    ax1.plot(t, y, color=PRICE, lw=1.8, zorder=3)
    ticks = [10, 100, 1000, 10000]
    ax1.yaxis.set_major_locator(FixedLocator([np.log10(1 + v / 100) for v in ticks]))
    ax1.yaxis.set_minor_locator(NullLocator())
    ax1.set_yticklabels([f"{v:,}" for v in ticks])
    ax1.axhline(0, color=MUTED, lw=0.7, ls=":", zorder=1)
    pk = p.idxmax()
    ax1.plot([pd.Timestamp(pk + "-01")], [np.log10(1 + p.max() / 100)], color=PRICE, zorder=4, **dict(DOT, mfc=PRICE))
    ax1.text(pd.Timestamp(pk + "-01") + pd.DateOffset(months=14), np.log10(1 + p.max() / 100),
             T(f"{pk[:4]} 年 {int(pk[5:])} 月\n{p.max():,.0f}%", f"{pd.Timestamp(pk + '-01'):%b %Y}\n{p.max():,.0f}%"),
             color=PRICE, fontsize=7.6, ha="left", va="center", linespacing=1.2)
    ax1.text(pd.Timestamp("2005-01-01"), np.log10(1.45), T("1997 年以后\n一直低于 10%", "below 10% since 1997"),
             color=PRICE, fontsize=7.6, ha="left", va="center", linespacing=1.25)
    ax1.set_xlim(pd.Timestamp("1984-06-01"), pd.Timestamp("2027-06-01"))
    ax1.set_ylim(-0.03, 2.35)
    _years(ax1, [1985, 1995, 2005, 2015, 2025])
    ax1.set_ylabel(T("12 个月通胀率（%，对数刻度）", "12-month inflation (%, log)"), fontsize=9)
    _grid(ax1)
    _title(ax1, T("(a) 物价：1990 年前后的恶性通胀", "(a) Prices: hyperinflation around 1990"))

    d = B.dollarization_pct.dropna()
    td = pd.to_datetime(d.index + "-01")
    ax2.axvspan(pd.Timestamp("2013-09-01"), pd.Timestamp("2015-06-30"), color=tint(MONEY, 0.12), lw=0, zorder=1)
    ax2.text(pd.Timestamp("2014-08-01"), 16, T("去美元化\n计划", "de-dollar-\nization\nplan"), color=MONEY, fontsize=7.6,
             ha="center", va="top", linespacing=1.2)
    ax2.axvline(pd.Timestamp("2002-09-24"), color=MUTED, lw=0.7, ls=":", zorder=1)
    ax2.text(pd.Timestamp("2002-03-01"), 16, T("2002 年 9 月：\n纳税用本币", "Sep 2002: taxes\nin soles"), color=MUTED,
             fontsize=7.6, ha="right", va="top", linespacing=1.2)
    ax2.plot(td, d, color=EXTERNAL, lw=2.0, zorder=3)
    for m, dy, va in ((d.idxmax(), 2.0, "bottom"), ("1992-01", -6.5, "top"), (d.index[-1], -2.5, "top")):
        ax2.plot([pd.Timestamp(m + "-01")], [d[m]], color=EXTERNAL, zorder=4, **dict(DOT, mfc=EXTERNAL))
        ax2.text(pd.Timestamp(m + "-01"), d[m] + dy, f"{d[m]:.1f}", color=EXTERNAL, fontsize=7.6, ha="center", va=va)
    ax2.set_xlim(pd.Timestamp("1989-06-01"), pd.Timestamp("2027-06-01"))
    ax2.set_ylim(0, 82)
    _years(ax2, [1992, 2002, 2012, 2022])
    ax2.set_ylabel(T("外币占广义货币（%）", "foreign currency, % of broad money"), fontsize=9)
    _grid(ax2)
    _title(ax2, T("(b) 美元：通胀过去以后还留了十年", "(b) Dollars stayed a decade longer"))
    fig.subplots_adjust(left=T(0.11, 0.122), right=0.985, top=0.9, bottom=0.1)
    return fig
