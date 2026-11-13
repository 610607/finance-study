"""Figures for Chapter 39 (消费与投资理论).

Style as in fig_ch38.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the colour
of their series, no legends. Consumption, saving and output are OUTPUT (a second series of a panel AMBER, dashed or
with squares), income INK, the wealth of the life cycle AMBER on an axis of its own colour; the numbers a source
prints are black squares, reference lines MUTED. All numbers come from checks/check_ch39.py: the stripped-down life
cycle (lifecycle_path(), growth_curve(), LC, F["md_numbers"]), the windfall rules (windfall_paths(), YEARS_LEFT, MPC,
RATE, K_PIH), the estimates of 2001 and 2008 (rebate_bars()) and ESRI's Japanese series (esri()).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch39 as C
from style import (
    AMBER,
    FIG_W,
    INK,
    LIGHT,
    MUTED,
    OUTPUT,
    T,
    clean_axes,
    figure,
    halo,
    tint,
)

SQUARE = dict(marker="s", ms=5.2, mec="white", mew=0.6)


def _title(ax, s):
    ax.set_title(s, fontsize=9.0, weight="bold", loc="left", pad=4)


def _grid(ax, axis="both"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


def _text(ax, x, y, s, color, ha="left", va="center", weight="normal", size=7.6):
    lab = ax.text(x, y, s, color=color, fontsize=size, ha=ha, va=va, weight=weight, linespacing=1.3, zorder=8)
    halo(lab, 2.0)
    return lab


def _right_axis(ax, color):
    """A second y axis on the right, in the colour of its series (as in fig_ch22.py)."""
    ax2 = ax.twinx()
    ax2.spines[["top", "left"]].set_visible(False)
    ax2.spines["right"].set_color(color)
    ax2.tick_params(axis="y", colors=color, length=3, width=0.7)
    ax.spines["right"].set_visible(False)
    return ax2


# ---------------------------------------------------------------------------------------------------
@figure("consumption_lifecycle")
def consumption_lifecycle():
    """(a) ex:consumption-lifecycle: a life of 50 years, 40 at work, income 1 a year, a zero rate of interest: income,
    consumption (left axis) and wealth (right axis) by age. (b) The aggregate saving rate of the same model, with ages
    continuous, against the growth rate of population (growth_curve()), and Modigliani's two numbers of the lecture
    (2 per cent: 8 per cent, 4 per cent: 13 per cent) as squares."""
    L, N = C.LC
    P, G, S = C.lifecycle_path(L, N), C.growth_curve(), C.stationary(L, N)
    r2, _, s2, r4, _, s4 = C.facts()["md_numbers"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.9), gridspec_kw=dict(width_ratios=[1.2, 1]))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.875, bottom=0.15, wspace=0.42)

    # (a) income, consumption and wealth by age
    a1.plot(P["age"], P["income"], color=INK, lw=1.6, zorder=5)
    a1.plot(P["age"], P["consumption"], color=OUTPUT, lw=2.0, zorder=6)
    a1.axvline(N, color=MUTED, lw=0.8, ls=(0, (1, 2)), zorder=2)
    a1.set_xlim(0, L + 1)
    a1.set_ylim(0, 1.25)
    a1.set_xticks([0, 10, 20, 30, 40, 50])
    a1.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    a1.set_xlabel(T("工作开始以后的年数", "years since starting work"))
    a1.set_ylabel(T("每年的收入与消费", "income and consumption a year"))
    _grid(a1, "y")
    w = _right_axis(a1, AMBER)
    w.fill_between(P["age"], 0, P["wealth"], color=tint(AMBER, 0.22), lw=0, zorder=1)
    w.plot(P["age"], P["wealth"], color=AMBER, lw=1.6, zorder=4)
    w.set_ylim(0, 10)
    w.set_yticks([0, 2, 4, 6, 8])
    w.set_ylabel(T("财富", "wealth"), color=AMBER)
    a1.set_zorder(w.get_zorder() + 1)
    a1.patch.set_visible(False)
    _text(a1, 3, 1.06, T("收入 1", "income 1"), INK)
    _text(a1, 3, S["c"] - 0.08, T(f"消费 {S['c']:.1f}", f"consumption {S['c']:.1f}"), OUTPUT, weight="bold")
    _text(a1, 22, 0.47, T("财富", "wealth"), AMBER, weight="bold")
    _text(a1, N + 0.8, 1.17, T(f"退休，财富 {S['peak']:.0f}", f"retires, wealth {S['peak']:.0f}"), AMBER, ha="right")
    _title(a1, T(f"(a) 工作 {N} 年攒下，退休 {L - N} 年花完", f"(a) Save for {N} years, spend in {L - N}"))
    assert np.isclose(P["wealth"].max(), S["peak"]) and S["peak"] < 10 and np.isclose(P["wealth"].iloc[-1], 0)

    # (b) the saving rate against the growth of population
    a2.plot(100 * G["n"], 100 * G["s"], color=OUTPUT, lw=2.0, zorder=5)
    a2.plot([r2, r4], [s2, s4], ls="none", color=INK, zorder=7, **SQUARE)
    _text(a2, r2 + 0.15, s2 + 0.5, f"{s2:.0f}%", INK, va="bottom", ha="right")
    _text(a2, r4 - 0.15, s4 + 0.5, f"{s4:.0f}%", INK, va="bottom", ha="right")
    _text(a2, 4.9, 4.4, T("曲线：同一模型\n方块：莫迪利亚尼的数", "curve: the same model\nsquares: Modigliani's"),
          MUTED, ha="right")
    a2.set_xlim(0, 5)
    a2.set_ylim(0, 17.5)
    a2.set_xticks([0, 1, 2, 3, 4, 5])
    a2.set_yticks([0, 4, 8, 12, 16])
    a2.set_xlabel(T("人口增长率（%）", "population growth (%)"))
    a2.set_ylabel(T("总储蓄率（%）", "aggregate saving rate (%)"))
    _grid(a2)
    _title(a2, T("(b) 增长越快，储蓄率越高", "(b) Faster growth, more saving"))
    assert np.isclose(G["s"].iloc[0], 0, atol=1e-9) and G["s"].is_monotonic_increasing and 100 * G["s"].max() < 17.5
    return fig


# ---------------------------------------------------------------------------------------------------
@figure("consumption_windfall")
def consumption_windfall():
    """(a) ex:consumption-windfall: the share of a windfall spent, cumulated, year by year: Keynes's rule (MPC in the
    first year), the permanent-income rule (k r every year), the life cycle of a head of household with 40 years to
    live and of a retiree with 10. (b) The estimates of the share spent in the three months of receipt (Johnson, Parker
    and Souleles 2004 on 2001; Parker et al. 2011 on 2008) as bars, the three rules' first quarter as vertical lines."""
    W, B = C.windfall_paths(), C.rebate_bars()
    young, old = C.YEARS_LEFT
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.9), gridspec_kw=dict(width_ratios=[1, 1.1]))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.875, bottom=0.15, wspace=0.30)

    # (a) the cumulated share spent
    a1.step(W["year"], 100 * W["keynes"], where="post", color=INK, lw=1.6, zorder=5)
    a1.plot(W["year"], 100 * W["pih"], color=AMBER, lw=1.8, zorder=5)
    a1.plot(W["year"], 100 * W["lch"], color=OUTPUT, lw=2.0, zorder=6)
    a1.plot(W["year"], 100 * W["retiree"], color=OUTPUT, lw=1.6, ls=(0, (4, 2)), zorder=6)
    a1.set_xlim(0, 41)
    a1.set_ylim(0, 118)
    a1.set_xticks([0, 10, 20, 30, 40])
    a1.set_yticks([0, 20, 40, 60, 80, 100])
    a1.set_xlabel(T("收到以后的年数", "years after receipt"))
    a1.set_ylabel(T("累计花掉的比例（%）", "share spent, cumulated (%)"))
    _grid(a1)
    _text(a1, 8, 100 * C.MPC + 3, T(f"凯恩斯式 {100 * C.MPC:.0f}%", f"Keynes {100 * C.MPC:.0f}%"), INK, va="bottom")
    _text(a1, old + 0.8, 104, T(f"退休者，还有 {old} 年", f"retiree, {old} years left"), OUTPUT, va="bottom")
    _text(a1, 24, 46, T(f"生命周期，\n还有 {young} 年", f"life cycle,\n{young} years left"), OUTPUT, va="top",
          weight="bold")
    _text(a1, 28.5, 79, T(f"永久收入：每年\n$k r$ = {100 * C.K_PIH * C.RATE:.1f}%", f"permanent income:\n$k r$ = "
                        f"{100 * C.K_PIH * C.RATE:.1f}% a year"), AMBER, ha="right", va="bottom")
    _title(a1, T("(a) 只有凯恩斯式规则当年花掉多半", "(a) Only Keynes's rule spends at once"))
    assert W["pih"].max() * 100 < 118 and np.isclose(W.loc[old, "retiree"], 1) and np.isclose(W.loc[young, "lch"], 1)

    # (b) the estimates and the rules' first quarter
    names = {"2001 nondurables": T("2001 年\n非耐用品", "2001\nnondurables"),
             "2008 nondurables": T("2008 年\n非耐用品", "2008\nnondurables"),
             "2008 total": T("2008 年\n全部支出", "2008\nall spending")}
    ys = [2, 1, 0]
    for y, (name, lo, hi) in zip(ys, B["bars"]):
        a2.barh(y, hi - lo, left=lo, height=0.42, color=tint(OUTPUT, 0.35), edgecolor=OUTPUT, lw=0.8, zorder=4)
        _text(a2, hi + 1.5, y, T(f"{lo:.0f}%—{hi:.0f}%", f"{lo:.0f}-{hi:.0f}%"), OUTPUT, size=7.6)
    R = B["rules"]
    a2.axvline(R["keynes"], color=INK, lw=1.2, zorder=3)
    low = max(R["pih"], R["lch"])
    a2.axvline(R["pih"], color=AMBER, lw=1.2, zorder=3)
    a2.axvline(R["lch"], color=OUTPUT, lw=1.2, ls=(0, (4, 2)), zorder=3)
    _text(a2, R["keynes"] + 1.2, 2.62, T(f"凯恩斯式 {R['keynes']:.0f}%", f"Keynes {R['keynes']:.0f}%"), INK, size=7.6)
    # The two long-run rules sit below 1%, on the zero line at this scale: the axis starts a little left of zero so
    # that their lines stand clear of it, and each is labelled, with a leader, in a gap between the bars.
    lead = 8
    for y, key, col, name in ((1.5, "pih", AMBER, T("永久收入", "permanent income")),
                              (0.5, "lch", OUTPUT, T("生命周期", "life cycle"))):
        lab = a2.annotate(f"{name} {R[key]:.3f}%", xy=(R[key], y), xytext=(lead, y), color=col, fontsize=7.6,
                          ha="left", va="center", zorder=8,
                          arrowprops=dict(arrowstyle="-", color=col, lw=0.7, shrinkA=1, shrinkB=0))
        halo(lab, 2.0)
    a2.set_yticks(ys)
    a2.set_yticklabels([names[n] for n, _, _ in B["bars"]])
    a2.set_ylim(-0.5, 2.9)
    a2.set_xlim(-6, 120)
    a2.set_xticks([0, 20, 40, 60, 80, 100])
    a2.set_xlabel(T("三个月里花掉的比例（%）", "share spent in three months (%)"))
    _grid(a2, "x")
    _title(a2, T("(b) 实测远高于两条长期规则", "(b) Far above the long-run rules"))
    assert low < 1 < lead < min(lo for _, lo, _ in B["bars"]) and max(hi for _, _, hi in B["bars"]) + 20 < 120
    assert abs(R["pih"] - R["lch"]) > 0.01                       # two labels, as the lines nearly coincide
    return fig


# ---------------------------------------------------------------------------------------------------
@figure("consumption_japan")
def consumption_japan():
    """(a) Japan's household saving rate (households including private unincorporated enterprises): the 1968 SNA
    (1990 base, saving over disposable income), 1955-1998, solid; the 2008 SNA (2020 base, the denominator adds the
    adjustment for the change in pension entitlements), 1994-2024, dashed. (b) The yearly growth rate of real gross
    domestic expenditure on the same two bases."""
    E = C.esri()
    s68, s08 = E["saving_68sna_pct"].dropna(), E["saving_08sna_pct"].dropna()
    g68, g08 = E["growth_68sna_pct"].dropna(), E["growth_08sna_pct"].dropna()
    peak = s68[s68 == s68.max()]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.9), sharex=True)
    fig.subplots_adjust(left=0.08, right=0.985, top=0.875, bottom=0.14, wspace=0.26)
    for ax in (a1, a2):
        ax.axhline(0, color=MUTED, lw=0.7, zorder=2)
        ax.set_xlim(1953, 2026)
        ax.set_xticks([1960, 1980, 2000, 2020])
        _grid(ax, "y")

    # (a) the saving rate
    a1.plot(s68.index, s68, color=OUTPUT, lw=1.9, zorder=5)
    a1.plot(s08.index, s08, color=AMBER, lw=1.7, ls=(0, (4, 2)), zorder=5)
    a1.plot(peak.index, peak, ls="none", color=OUTPUT, zorder=6, marker="o", ms=4.2, mec="white", mew=0.5)
    _text(a1, 1975, peak.iloc[0] + 1.2, T(f"{peak.index[0]}、{peak.index[1]} 年 {peak.iloc[0]:.1f}%",
                                          f"{peak.index[0]}, {peak.index[1]}: {peak.iloc[0]:.1f}%"), OUTPUT,
          ha="center", va="bottom", weight="bold")
    _text(a1, 1957, 8.6, T("1968 年体系", "1968 SNA"), OUTPUT, weight="bold")
    _text(a1, 2005, 7.0, T("2008 年体系", "2008 SNA"), AMBER, weight="bold")
    _text(a1, 2020, s08[2020] + 0.9, f"2020: {s08[2020]:.1f}%", AMBER, ha="center", va="bottom")
    a1.set_ylim(-4, 27.5)
    a1.set_yticks([0, 5, 10, 15, 20, 25])
    a1.set_ylabel(T("储蓄率（%）", "saving rate (%)"))
    _title(a1, T("(a) 储蓄率 1970 年代中期最高", "(a) Saving peaked in the mid-1970s"))
    assert list(peak.index) == [1974, 1976] and s08.min() > -4 and s68.max() < 25.5
    assert s08[2020] == s08.loc[1999:].max()

    # (b) the growth rate
    a2.plot(g68.index, g68, color=OUTPUT, lw=1.6, zorder=5, marker="o", ms=2.6, mec="white", mew=0.3)
    a2.plot(g08.index, g08, color=AMBER, lw=1.5, ls=(0, (4, 2)), zorder=5, marker="o", ms=2.6, mec="white", mew=0.3)
    early = C.compound(g68.loc[1956:1973])
    a2.plot([1956, 1973], [early, early], color=INK, lw=1.0, zorder=6)
    _text(a2, 1966, 14.3, T(f"1956—1973 年\n平均 {early:.1f}%", f"1956-73\naverage {early:.1f}%"), INK, ha="center",
          va="bottom")
    _text(a2, 1974.6, -1.2, "1974", OUTPUT, ha="left", va="top")
    a2.set_ylim(-7.5, 19)
    a2.set_yticks([-5, 0, 5, 10, 15])
    a2.set_ylabel(T("实际增长率（%）", "real growth (%)"))
    _title(a2, T("(b) 1974 年以后增长放慢", "(b) Growth slowed after 1974"))
    assert g68[1974] < 0 and g68.loc[1975:].max() < early and g68.max() < 14.0 and g08.min() > -7.5
    return fig
