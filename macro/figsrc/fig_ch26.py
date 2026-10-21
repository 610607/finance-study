"""Figures for Chapter 26 (一战、赔款与魏玛恶性通胀).

Style as in fig_ch25.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series. Prices are PRICE, Reichsbank notes MONEY in every panel, the new rentenmarks AMBER and
hatched, the budget FISCAL. All numbers come from checks/check_ch26.py: Sargent's Table G1 (prices), his p. 82
(inflation_multiples), Bresciani-Turroni's p. 337 (notes) and Sargent's Table G5 (budget).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch26 as C  # noqa: E402
from style import AMBER, FIG_W, FISCAL, LIGHT, MONEY, MUTED, PRICE, T, ZH, clean_axes, figure, halo  # noqa: E402

HATCH = "////"


def _title(ax, s):
    ax.set_title(s, fontsize=9.0, weight="bold", loc="left", pad=4)


def _grid(ax, axis="y"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


def _powers(ax, exponents):
    """A log axis with ticks at the given powers of ten, printed as 10^n."""
    ax.set_yscale("log")
    ax.yaxis.set_major_locator(FixedLocator([10.0 ** e for e in exponents]))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"$\\mathdefault{{10^{{{np.log10(v):.0f}}}}}$"))


def _signed(x: float) -> str:
    """One decimal with a sign, and a true minus sign."""
    return f"{x:+.1f}".replace("-", "−")


def _years(ax, months):
    """Ticks at the Januaries of a monthly index 'YYYY-MM'."""
    starts = [i for i, m in enumerate(months) if m.endswith("-01")]
    ax.set_xticks(starts)
    ax.set_xticklabels([months[i][:4] for i in starts])
    ax.set_xlim(-0.7, len(months) - 0.3)


@figure("weimar_prices")
def weimar_prices():
    """Wholesale prices (1913 = 100, paper marks, log): (a) 1920-1922, the plateau of February 1920 - May 1921 and
    the acceleration; (b) 1923 - June 1924, with November 1923 marked."""
    P = C.prices().wpi_1913_100
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.8))
    fig.subplots_adjust(left=0.095, right=0.985, top=0.86, bottom=0.17, wspace=0.32)

    a = P.loc["1920-01":"1922-12"]
    x = np.arange(len(a))
    a1.plot(x, a.values, color=PRICE, lw=2.0, zorder=4)
    _years(a1, list(a.index))
    _powers(a1, [3, 4, 5])
    a1.set_ylim(900, 2.6e5)
    a1.set_ylabel(T("批发物价指数（1913 年 = 100，对数）", "wholesale prices (1913 = 100, log)"))
    _grid(a1)
    k0, k1 = list(a.index).index("1920-02"), list(a.index).index("1921-05")
    a1.plot([k0, k1], [a.iloc[k0], a.iloc[k1]], "o", ms=3.8, color=PRICE, mec="white", mew=0.5, zorder=5)
    lab = a1.text(1, 6500, T("1920 年 2 月至 1921 年 5 月\n物价大体稳住", "Feb 1920 to May 1921:\nprices roughly flat"),
                  fontsize=7.8, color=PRICE, ha="left", va="bottom", linespacing=1.3)
    halo(lab, 2.0)
    _title(a1, T("(a) 平台以后，速度加快", "(a) A plateau, then acceleration"))

    b = P.loc["1923-01":"1924-06"]
    x = np.arange(len(b))
    a2.plot(x, b.values, color=PRICE, lw=2.0, zorder=4)
    _years(a2, list(b.index))
    _powers(a2, [6, 8, 10, 12, 14])
    a2.set_ylim(1.5e5, 6e14)
    _grid(a2)
    nov = list(b.index).index("1923-11")
    a2.axvline(nov, color=MUTED, lw=0.8, ls=(0, (1, 2)), zorder=2)
    lab = a2.text(nov + 0.5, 1e9, T("1923 年 11 月\n新币开始发行", "Nov 1923:\nnew notes"), fontsize=7.8,
                  color=MUTED, ha="left", va="center", linespacing=1.3)
    halo(lab, 2.0)
    _title(a2, T("(b) 陡升以后，停在高位", "(b) A surge, then a high plateau"))
    for ax in (a1, a2):
        ax.set_xlabel(T("年份", "year"))
    return fig


@figure("weimar_balances")
def weimar_balances():
    """(a) Wholesale prices and Reichsbank notes in July and August 1923 (January 1922 = 1, log); (b) old Reichsbank
    notes (divided by 10^12) and new rentenmarks at three month ends, in million rentenmarks."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.8))
    fig.subplots_adjust(left=0.095, right=0.985, top=0.86, bottom=0.17, wspace=0.36)

    p, n = C.inflation_multiples()
    x = np.arange(len(p))
    w = 0.32
    a1.bar(x - w / 2 - 0.02, p, w, color=PRICE, lw=0, zorder=3)
    a1.bar(x + w / 2 + 0.02, n, w, color=MONEY, lw=0, zorder=3)
    for j in range(len(p)):
        a1.text(x[j] - w / 2 - 0.02, p[j] * 1.2, f"{p[j]:,.0f}", ha="center", va="bottom", color=PRICE, fontsize=7.6)
        a1.text(x[j] + w / 2 + 0.02, n[j] * 1.2, f"{n[j]:,.0f}", ha="center", va="bottom", color=MONEY, fontsize=7.6)
    _powers(a1, [0, 1, 2, 3, 4, 5, 6])
    a1.set_ylim(1, 1.5e6)
    a1.set_xticks(x)
    a1.set_xticklabels([T("1923 年 7 月", "Jul 1923"), T("8 月", "Aug 1923")])
    a1.set_xlim(-0.6, 1.6)
    a1.set_ylabel(T("倍数（1922 年 1 月 = 1，对数）", "multiple (Jan 1922 = 1, log)"))
    _grid(a1)
    a1.text(-0.5, 6e5, T("批发物价", "wholesale prices"), color=PRICE, fontsize=7.8, ha="left", va="center")
    a1.text(-0.5, 2.2e5, T("帝国银行券", "Reichsbank notes"), color=MONEY, fontsize=7.8, ha="left", va="center")
    real = 100 * n / p
    note = T(f"实际余额约剩\n{real[0]:.0f}% 与 {real[1]:.0f}%", f"real balances:\n{real[0]:.0f}% and {real[1]:.0f}%")
    a1.text(1.55, 1e6, note, color=MUTED, fontsize=7.6, ha="right", va="top", linespacing=1.2)
    _title(a1, T("(a) 钞票追不上物价", "(a) Notes lag behind prices"))

    d = C.notes()
    x = np.arange(len(d))
    old, new = d.old_notes_million_newunit.values, d.new_rentenmarks_million.values
    a2.bar(x, old, 0.55, color=MONEY, lw=0, zorder=3)
    a2.bar(x, new, 0.55, bottom=old, color=AMBER, ec="white", hatch=HATCH, lw=0, zorder=3)
    for j in range(len(d)):
        a2.text(x[j], old[j] + new[j] + 60, f"{old[j] + new[j]:,.0f}", ha="center", va="bottom", color=MUTED,
                fontsize=7.6)
    a2.set_ylim(0, 3900)
    a2.set_xticks(x)
    a2.set_xticklabels([T("1923 年\n12 月末", "end-Dec\n1923"), T("1924 年\n3 月末", "end-Mar\n1924"),
                        T("1924 年\n7 月末", "end-Jul\n1924")])
    a2.set_xlim(-0.6, len(d) - 0.4)
    a2.set_ylabel(T("百万地租马克", "million rentenmarks"))
    _grid(a2)
    a2.text(-0.5, 3650, T("地租银行新钞", "new rentenmarks"), color=AMBER, fontsize=7.8, ha="left", va="center")
    a2.text(-0.5, 3300, T("帝国银行旧钞", "old Reichsbank notes"), color=MONEY, fontsize=7.8, ha="left", va="center")
    _title(a2, T("(b) 稳定以后，正式钞票增加", "(b) Notes grow after stability"))
    return fig


@figure("weimar_budget")
def weimar_budget():
    """The balance of the Reich's ordinary budget (revenue minus expenditure, million gold marks), December 1923 -
    June 1924."""
    d = C.budget()
    balance = (d.revenue_million_goldmark - d.expenditure_million_goldmark).values
    x = np.arange(len(d))
    fig, ax = plt.subplots(figsize=(FIG_W, 2.5))
    fig.subplots_adjust(left=0.12 if ZH else 0.14, right=0.985, top=0.95, bottom=0.2)

    ax.bar(x, balance, 0.55, color=FISCAL, lw=0, zorder=3)
    ax.axhline(0, color=MUTED, lw=0.8, zorder=4)
    for i, v in enumerate(balance):
        ax.text(i, v + (9 if v > 0 else -10), _signed(v), ha="center", va="bottom" if v > 0 else "top", fontsize=7.8,
                color=FISCAL)
    ax.set_ylim(-420, 215)
    ax.set_xlim(-0.6, len(d) - 0.4)
    months = [T("1923 年\n12 月", "Dec\n1923"), T("1924 年\n1 月", "Jan\n1924")]
    months += [T(f"{int(m[-2:])} 月", f) for m, f in zip(d.date[2:], ["Feb", "Mar", "Apr", "May", "Jun"])]
    ax.set_xticks(x)
    ax.set_xticklabels(months)
    ax.set_ylabel(T("普通预算余额（百万金马克）", "ordinary budget balance\n(million gold marks)"))
    _grid(ax)
    lab = ax.text(3.0, -250, T("12 月仍有赤字，1924 年 2 月又有一笔小赤字", "a deficit in December, a small one again in February"),
                  fontsize=7.8, color=MUTED, ha="center", va="center")
    halo(lab, 2.0)
    return fig
