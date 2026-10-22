"""Figures for Chapter 27 (两次大战之间的金本位).

Style as in fig_ch26.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series. The exchange rate and the reserves are EXTERNAL, prices PRICE (the second price series
AMBER, dashed), wages and unemployment OUTPUT, Bank Rate MONEY. All numbers come from checks/check_ch27.py: the
Bank of England's millennium workbook (monthly(), bank_rate(), ppp()) and Nurkse's Table 2 and p. 29
(gold_reserves(), fx_shares()).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch27 as C
from style import (
    AMBER,
    EXTERNAL,
    FIG_W,
    LIGHT,
    MONEY,
    MUTED,
    OUTPUT,
    PRICE,
    ZH,
    T,
    clean_axes,
    figure,
    halo,
    tint,
)


def _title(ax, s):
    ax.set_title(s, fontsize=9.0, weight="bold", loc="left", pad=4)


def _grid(ax, axis="y"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


def _x(months) -> np.ndarray:
    """'YYYY-MM' -> the middle of the month in years."""
    return np.array([int(m[:4]) + (int(m[5:]) - 0.5) / 12 for m in months])


def _mark(ax, month: str, text: str, y: float, ha: str = "left"):
    """A dotted vertical line at a month, with a note."""
    x = _x([month])[0]
    ax.axvline(x, color=MUTED, lw=0.8, ls=(0, (1, 2)), zorder=2)
    lab = ax.text(x + (0.15 if ha == "left" else -0.15), y, text, fontsize=7.6, color=MUTED, ha=ha, va="center",
                  linespacing=1.3)
    halo(lab, 2.0)


@figure("interwar_sterling")
def interwar_sterling():
    """(a) The monthly $/£ rate, July 1914 - December 1931, the mint par and the annual consumer-price PPP (1913 base);
    (b) the Sauerbeck index, the cost of living and weekly wages, January 1924 = 100, with April 1925 marked."""
    M, par, P = C.monthly(), C.mint_par(), C.ppp()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.9))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.86, bottom=0.15, wspace=0.27)

    a1.plot(_x(M.index), M.usd_per_gbp.values, color=EXTERNAL, lw=1.6, zorder=4)
    a1.axhline(par, color=MUTED, lw=0.8, ls=(0, (1, 2)), zorder=2)
    pp = P.loc[1914:1931]
    assert pp.loc[1925:1931].max() < par                       # the PPP stays below the par after the return
    a1.plot(pp.index + 0.5, pp.values, "o", ms=3.6, color=PRICE, mec="white", mew=0.5, zorder=5)
    a1.set_xlim(1914, 1932.3)
    a1.set_ylim(3.1, 5.45)
    a1.set_xticks([1915, 1920, 1925, 1930])
    a1.set_ylabel(T("美元/英镑", "dollars per pound"))
    _grid(a1)
    lab = a1.text(1920.6, par + 0.05, T(f"铸币平价 {par:.4f}", f"mint par {par:.4f}"), color=MUTED, fontsize=7.6,
                  ha="left", va="bottom")
    halo(lab, 2.0)
    lab = a1.text(1922.2, 3.5, T("每月汇价", "monthly rate"), color=EXTERNAL, fontsize=7.8, ha="left", va="center")
    halo(lab, 2.0)
    lab = a1.text(1926.0, 4.30, T("购买力平价\n（消费物价）", "PPP\n(CPI)"), color=PRICE, fontsize=7.8,
                  ha="left", va="top", linespacing=1.25)
    halo(lab, 2.0)
    _title(a1, T("(a) 汇价回到平价，购买力平价在下面", "(a) The rate back at par, PPP below"))

    span = slice("1919-01", "1931-12")
    s = C.rebased("sauerbeck_1867_77_100").loc[span]
    c = C.rebased("cost_of_living_jul1914_100").loc[span]
    w = C.rebased("wages_jan1939_100").loc[span]
    x = _x(s.index)
    a2.plot(x, s.values, color=PRICE, lw=1.8, zorder=4)
    a2.plot(x, c.values, color=AMBER, lw=1.6, dashes=(4, 2), zorder=4)
    a2.plot(x, w.values, color=OUTPUT, lw=1.6, zorder=4)
    a2.hlines(100, 1919, 1932, color=MUTED, lw=0.6, ls=(0, (1, 2)), zorder=2)
    _mark(a2, "1925-04", T("1925 年 4 月", "Apr 1925"), 185)
    a2.set_xlim(1919, 1935.6 if ZH else 1937.4)
    a2.set_ylim(50, 205)
    a2.set_xticks([1920, 1925, 1930])
    a2.set_ylabel(T("1924 年 1 月 = 100", "Jan 1924 = 100"))
    _grid(a2)
    fall = {k: 100 * (1 - v.loc["1929-10"] / v.loc["1925-04"]) for k, v in (("s", s), ("c", c), ("w", w))}
    assert fall["s"] > fall["c"] > fall["w"]                    # wholesale prices fell most after the return
    for v, col, zh_, en_ in ((s, PRICE, "批发物价", "wholesale"), (c, AMBER, "生活费用", "cost of living"),
                             (w, OUTPUT, "周工资", "wages")):
        a2.text(1932.2, v.iloc[-1], T(zh_, en_), color=col, fontsize=7.8, ha="left", va="center", linespacing=1.1)
    _title(a2, T("(b) 回到黄金以后，批发物价降得最多", "(b) Wholesale prices fell most"))
    for ax in (a1, a2):
        ax.set_xlabel(T("年份", "year"))
    return fig


@figure("interwar_labour")
def interwar_labour():
    """(a) The administrative unemployment rate, monthly, 1919-1931 (gaps where the sheet is empty), with April 1925
    and May 1926 marked; (b) Bank Rate, 1919-1931, as steps."""
    M = C.monthly()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.8))
    fig.subplots_adjust(left=0.08, right=0.985, top=0.86, bottom=0.16, wspace=0.25)

    u = M.unemp_admin.loc["1919-01":"1931-12"]
    a1.plot(_x(u.index), u.values, color=OUTPUT, lw=1.6, zorder=4)
    floor = u.loc["1925-05":].min()
    assert floor >= 8
    _mark(a1, "1925-04", T("回到黄金", "return\nto gold"), 21.5, ha="right")
    _mark(a1, "1926-05", T("总罢工", "general\nstrike"), 21.5)
    a1.set_xlim(1919, 1932.2)
    a1.set_ylim(0, 25)
    a1.set_xticks([1920, 1925, 1930])
    a1.set_ylabel(T("行政失业率（%）", "administrative unemployment (%)"))
    _grid(a1)
    _title(a1, T("(a) 回到黄金以后，失业率一直在 8% 以上", "(a) Unemployment stayed above 8%"))

    b = C.bank_rate()
    days = list(b.date) + ["1931-12-31"]
    xs = np.array([int(d[:4]) + (int(d[5:7]) - 1 + (int(d[8:]) - 1) / 31) / 12 for d in days])
    ys = list(b.bank_rate) + [b.bank_rate.iloc[-1]]
    a2.step(xs, ys, where="post", color=MONEY, lw=1.8, zorder=4)
    low = b[(b.date >= "1925-03-05") & (b.date < "1930-01-01")].bank_rate.min()
    a2.axhline(low, color=MUTED, lw=0.6, ls=(0, (1, 2)), zorder=2)
    for day, dy in (("1920-04-15", 0.35), ("1925-03-05", 0.35), ("1929-09-26", 0.35)):
        r = C.rate_on(day)
        x = int(day[:4]) + (int(day[5:7]) - 1) / 12
        lab = a2.text(x + 0.1, r + dy, T(f"{r:g}%", f"{r:g}%"), color=MONEY, fontsize=7.6, ha="left", va="bottom")
        halo(lab, 2.0)
    a2.set_xlim(1919, 1932.2)
    a2.set_ylim(0, 8.2)
    a2.set_xticks([1920, 1925, 1930])
    a2.set_ylabel(T("贴现率（%）", "Bank Rate (%)"))
    _grid(a2)
    _title(a2, T(f"(b) 1925—1929 年，贴现率没有低于 {low:g}%", f"(b) 1925-29: Bank Rate never below {low:g}%"))
    for ax in (a1, a2):
        ax.set_xlabel(T("年份", "year"))
    return fig


@figure("interwar_gold")
def interwar_gold():
    """(a) Central gold reserves of the United States, France, the United Kingdom and Germany at the end of 1913, 1918,
    1923 and 1928 (million dollars of the old parity); (b) the share of foreign exchange in the reserves of the
    European central banks, 1913, 1925 and 1928."""
    yrs, R = C.gold_reserves()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.8), gridspec_kw={"width_ratios": [1.6, 1]})
    fig.subplots_adjust(left=0.105, right=0.985, top=0.86, bottom=0.17, wspace=0.28)

    order = ["us", "fr", "uk", "de"]
    for j in range(len(yrs)):
        assert R["us"][j] > sum(R[k][j] for k in order[1:])    # the US holds more than the other three together
    names = {"us": T("美国", "US"), "fr": T("法国", "France"), "uk": T("英国", "UK"), "de": T("德国", "Germany")}
    shades = [tint(EXTERNAL, a) for a in (0.25, 0.5, 0.75)] + [EXTERNAL]       # light to dark
    w = 0.19
    for i, k in enumerate(order):
        for j, y in enumerate(yrs):
            a1.bar(i + (j - 1.5) * w, R[k][j], w * 0.92, color=shades[j], lw=0, zorder=3)
        a1.text(i + 1.5 * w, R[k][3] + 60, f"{R[k][3]:,.0f}", ha="center", va="bottom", color=EXTERNAL, fontsize=7.6)
    handles = [Patch(color=shades[j], lw=0) for j in range(len(yrs))]
    a1.legend(handles, [T(f"{y} 年底", f"end-{y}") for y in yrs], frameon=False, fontsize=7.6, loc="upper right",
              handlelength=1.0, handletextpad=0.4, labelspacing=0.3, borderaxespad=0.2)
    a1.set_xticks(range(len(order)))
    a1.set_xticklabels([names[k] for k in order])
    a1.set_xlim(-0.55, len(order) - 0.45)
    a1.set_ylim(0, 4200)
    a1.set_ylabel(T("百万旧美元", "million old dollars"))
    _grid(a1)
    _title(a1, T("(a) 美国的黄金多过其余三国之和", "(a) US gold exceeds the other three together"))

    fy, share, banks = C.fx_shares()
    x = np.arange(len(fy))
    a2.bar(x, share, 0.55, color=EXTERNAL, lw=0, zorder=3)
    for j in range(len(fy)):
        a2.text(x[j], share[j] + 1.2, f"{share[j]:g}%", ha="center", va="bottom", color=EXTERNAL, fontsize=7.8)
    a2.set_xticks(x)
    a2.set_xticklabels([T(f"{y}\n{n} 家", f"{y}\n{n} banks") for y, n in zip(fy, banks)])
    a2.set_xlim(-0.6, len(fy) - 0.4)
    a2.set_ylim(0, 50)
    a2.set_ylabel(T("外汇占储备（%）", "foreign exchange in reserves (%)"))
    _grid(a2)
    _title(a2, T("(b) 外汇升到储备的四成", "(b) Exchange rises to 42%"))
    return fig
