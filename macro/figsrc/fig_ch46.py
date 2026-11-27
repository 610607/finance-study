"""Figures for Chapter 46 (布雷顿森林解体与浮动汇率).

Style as in fig_ch45.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the colour
of their series, no legends. Exchange rates are EXTERNAL (the second rate of a panel AMBER, dashed, with squares), the
price level PRICE, the interest differential MONEY, reference lines MUTED. All numbers come from checks/check_ch46.py:
the BIS series of the snapshot floating_bis_1959_1985 (series(), index(), volatility()) and the path of the teaching
example ex:floating-overshoot (path(), EX). The Chinese labels of the BIS series are not an official BIS translation
(said in the bibliography item bisdata46).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch46 as C
from style import (
    AMBER,
    EXTERNAL,
    FIG_W,
    INK,
    LIGHT,
    MONEY,
    MUTED,
    PRICE,
    T,
    clean_axes,
    figure,
    halo,
    tint,
)

DOT = dict(marker="o", ms=4.4, mec="white", mew=0.6)
SQUARE = dict(marker="s", ms=4.4, mec="white", mew=0.6)


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


def _ts(months) -> pd.DatetimeIndex:
    """The middle of each month, for plotting."""
    return months.to_timestamp() + pd.Timedelta(days=14)


def _day(s: str) -> pd.Timestamp:
    return pd.Timestamp(s)


# ---------------------------------------------------------------------------------------------------
@figure("floating_rates")
def floating_rates():
    """The yen (a), the mark (b), the Swiss franc (c) and sterling (d) per US dollar, monthly averages 1965-1985, as
    indices of their 1970 average = 100 on one log scale (down: the currency appreciates), with vertical lines at
    C.VLINES; the extreme month after August 1971 of each is marked with its rate."""
    S = C.series()
    assert (C.index("deu_eur") - 100 * S.loc[C.SPAN[0]:C.SPAN[1], "deu_eur"] * C.MARK
            / (S.loc[C.BASE[0]:C.BASE[1], "deu_eur"] * C.MARK).mean()).abs().max() < 1e-9   # the mark = euro x MARK
    fig, axes = plt.subplots(2, 2, figsize=(FIG_W, 4.3), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.10, right=0.985, top=0.93, bottom=0.07, hspace=0.32, wspace=0.08)
    ticks = [30, 50, 70, 100, 150, 200]
    after = slice("1971-08", None)
    for ax, col in zip(axes.flat, C.RATES):
        x = C.index(col)
        t = _ts(x.index)
        marks = [i for i, m in enumerate(x.index) if m.month == 1 and m.year % 2 == 1]   # every second January
        _grid(ax, "y")
        ax.set_yscale("log")
        for v in C.VLINES:
            ax.axvline(_day(v), color=MUTED, lw=0.8, ls=(0, (3, 2)), zorder=2)
        ax.axhline(100, color=MUTED, lw=0.7, ls=":", zorder=2)
        ax.plot(t, x.values, color=EXTERNAL, lw=1.6, zorder=4)
        ax.plot(t[marks], x.values[marks], ls="none", color=EXTERNAL, zorder=5, **DOT)
        m = x.loc[after].idxmax() if col == "gbp" else x.loc[after].idxmin()
        tm = _ts(pd.PeriodIndex([m]))[0]
        ax.plot(tm, x[m], ls="none", color=INK, zorder=6, **DOT)
        ax.set_ylim(28, 260)
        ax.yaxis.set_major_locator(mticker.FixedLocator(ticks))
        ax.yaxis.set_major_formatter(mticker.FixedFormatter([str(v) for v in ticks]))
        ax.yaxis.set_minor_locator(mticker.NullLocator())
    (a1, a2), (a3, a4) = axes
    S_ = lambda col, m: S.loc[m, col]                                                    # noqa: E731
    yen = C.index("jpy").loc[after].idxmin()
    chf = C.index("chf").loc[after].idxmin()
    gbp = C.index("gbp").loc[after].idxmax()
    dem = C.index("deu_eur").loc[after].idxmin()
    assert (str(yen), str(chf), str(gbp)) == ("1978-10", "1978-10", "1985-02")
    _title(a1, T(f"(a) 日元：{yen.year} 年 {yen.month} 月升到 {S_('jpy', yen):.1f}",
                 f"(a) Yen: {S_('jpy', yen):.1f} in {yen.strftime('%b %Y')}"))
    _title(a2, T(f"(b) 马克：{dem.year} 年 {dem.month} 月升到 {S_('deu_eur', dem) * C.MARK:.2f}",
                 f"(b) Mark: {S_('deu_eur', dem) * C.MARK:.2f} in {dem.strftime('%b %Y')}"))
    _title(a3, T(f"(c) 瑞士法郎：{chf.year} 年 {chf.month} 月升到 {S_('chf', chf):.2f}",
                 f"(c) Swiss franc: {S_('chf', chf):.2f} in {chf.strftime('%b %Y')}"))
    usd = 1 / S_("gbp", gbp)
    _title(a4, T(f"(d) 英镑：{gbp.year} 年 {gbp.month} 月跌到 {usd:.2f} 美元",
                 f"(d) Sterling: ${usd:.2f} in {gbp.strftime('%b %Y')}"))
    _text(a1, _day("1985-10-01"), 36, T("向下：本币升值", "down: the currency appreciates"), MUTED, ha="right")
    _text(a4, _day("1965-04-01"), 122, T("1967 年 11 月贬值", "devalued\nNov 1967"), MUTED, va="bottom")
    assert C.index("gbp").loc["1967-12"] > 1.1 * C.index("gbp").loc["1967-10"]
    for ax in (a1, a3):
        ax.set_ylabel(T("指数（1970 年 = 100）", "1970 = 100"))
    for ax in (a3, a4):
        ax.set_xlim(_day("1965-01-01"), _day("1986-01-01"))
        ax.xaxis.set_major_locator(plt.matplotlib.dates.YearLocator(5))
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%Y"))
    return fig


@figure("floating_paths")
def floating_paths():
    """The path of ex:floating-overshoot (C.path with C.EX): (a) the exchange rate and the price level, (b) the interest
    differential, from one year before to five years after money rises by 10% at t = 0."""
    t = np.linspace(-1, 5, 601)
    P = C.path(t)
    yrs = np.arange(0, 6)
    Q = C.path(yrs.astype(float))
    dm = C.EX["dm"]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(FIG_W, 3.9), sharex=True, gridspec_kw=dict(height_ratios=[1.45, 1]))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.93, bottom=0.11, hspace=0.30)
    for ax in (a1, a2):
        _grid(ax, "y")
        ax.axvline(0, color=MUTED, lw=0.8, ls=(0, (3, 2)), zorder=2)
    a1.axhline(dm, color=MUTED, lw=0.7, ls=":", zorder=2)
    before, after = t < 0, t >= 0
    a1.plot(t[before], P["e"][before], color=EXTERNAL, lw=1.8, zorder=4)
    a1.plot(t[after], P["e"][after], color=EXTERNAL, lw=1.8, zorder=4)
    a1.plot([0, 0], [0, P["e"][after][0]], color=EXTERNAL, lw=0.9, ls=(0, (1, 1.5)), zorder=4)
    a1.plot(yrs, Q["e"], ls="none", color=EXTERNAL, zorder=5, **DOT)
    a1.plot(t, P["p"], color=PRICE, lw=1.8, dashes=(4, 2), zorder=4)
    a1.plot(yrs, Q["p"], ls="none", color=PRICE, zorder=5, **SQUARE)
    e0 = Q["e"][0]
    assert np.isclose(e0, 15) and np.isclose(Q["p"][0], 0)
    _text(a1, 0.12, e0, T(f"汇率当时跳到 {e0:.0f}%", f"the exchange rate jumps to {e0:.0f}%"), EXTERNAL, weight="bold")
    _text(a1, 2.2, Q["p"][1] - 1.6, T("物价慢慢上升", "prices rise slowly"), PRICE, weight="bold")
    _text(a1, 4.95, dm + 0.8, T(f"长期水平 {dm:.0f}%", f"long run {dm:.0f}%"), MUTED, ha="right", va="bottom")
    a1.set_ylim(-1.5, 17)
    a1.set_yticks([0, 5, 10, 15])
    a1.set_ylabel(T("比原来高（%）", "above old level (%)"))
    _title(a1, T("(a) 汇率先超过长期水平，再回落；物价慢慢跟上",
                 "(a) The exchange rate overshoots and falls back; prices catch up slowly"))
    a2.axhline(0, color=MUTED, lw=0.7, zorder=2)
    a2.plot(t[before], P["i"][before], color=MONEY, lw=1.8, zorder=4)
    a2.plot(t[after], P["i"][after], color=MONEY, lw=1.8, zorder=4)
    a2.plot([0, 0], [0, P["i"][after][0]], color=MONEY, lw=0.9, ls=(0, (1, 1.5)), zorder=4)
    a2.plot(yrs, Q["i"], ls="none", color=MONEY, zorder=5, **DOT)
    i0 = Q["i"][0]
    assert np.isclose(i0, -dm / C.EX["lam"])
    i0s = f"{i0:.0f}".replace("-", "−")
    _text(a2, 0.12, i0, T(f"利率差跳到 {i0s} 个百分点", f"the differential drops to {i0s} points"), MONEY,
          weight="bold")
    a2.set_ylim(-6, 1)
    a2.set_yticks([-6, -4, -2, 0])
    a2.set_ylabel(T("$i-i^{f}$（百分点）", "$i-i^{f}$ (points)"))
    a2.set_xlim(-1, 5)
    a2.set_xticks(range(-1, 6))
    a2.set_xlabel(T("年", "years"))
    _title(a2, T("(b) 本国利率低于外国利率，差距逐年缩小", "(b) The home rate below the foreign rate, the gap closing"))
    return fig


@figure("floating_volatility")
def floating_volatility():
    """The standard deviations of the monthly changes (100 x log) of the nominal rate (a), the real rate (b) and the
    ratio of the price levels (c), 1960-1970 (light) and 1974-1985 (full colour), four currencies against the dollar."""
    V = {c: (C.volatility(c, C.FIXED), C.volatility(c, C.FLOAT)) for c in C.RATES}
    names = [T("日元", "yen"), T("马克", "mark"), T("瑞士\n法郎", "Swiss\nfranc"), T("英镑", "sterling")]
    fig, axes = plt.subplots(1, 3, figsize=(FIG_W, 2.75), sharey=True)
    fig.subplots_adjust(left=0.085, right=0.99, top=0.86, bottom=0.17, wspace=0.10)
    x = np.arange(len(C.RATES))
    w = 0.38
    for ax, what, color, title in zip(axes, ("nominal", "real", "relp"), (EXTERNAL, EXTERNAL, PRICE),
                                      (T("(a) 名义汇率：大了几倍", "(a) Nominal: far larger"),
                                       T("(b) 实际汇率：跟着变大", "(b) Real: as large"),
                                       T("(c) 物价之比：差不多", "(c) Prices: about the same"))):
        _grid(ax, "y")
        fixed = [V[c][0][what] for c in C.RATES]
        flo = [V[c][1][what] for c in C.RATES]
        ax.bar(x - w / 2, fixed, width=w, color=tint(color, 0.62), lw=0, zorder=3)
        ax.bar(x + w / 2, flo, width=w, color=color, lw=0, zorder=3)
        for xi, v in zip(x, flo):
            _text(ax, xi + w / 2, v + 0.08, f"{v:.1f}", color, ha="center", va="bottom", size=7.6)
        ax.set_xticks(x)
        ax.set_xticklabels(names, fontsize=8.0)
        ax.tick_params(axis="x", length=0)
        ax.set_xlim(-0.6, len(x) - 0.4)
        _title(ax, title)
    assert max(V[c][1]["nominal"] for c in C.RATES) < 3.3 and max(V[c][0]["relp"] for c in C.RATES) < 0.9
    axes[0].set_ylim(0, 3.6)
    axes[0].set_yticks([0, 1, 2, 3])
    axes[0].set_ylabel(T("标准差（百分点）", "std. dev. (points)"))
    _text(axes[2], -0.45, 3.3, T("浅色：1960—1970 年\n深色：1974—1985 年", "light: 1960-1970\nfull: 1974-1985"),
          INK, va="top")
    return fig
