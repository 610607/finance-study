"""Figures for Chapter 24 (第一次全球化中的边缘).

Style as in fig_ch23.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series, the second series in AMBER and dashed. Capital flows and exchange rates are EXTERNAL, money
(silver and the rupee) MONEY. All numbers come from checks/check_ch24.py, which reads the Bank of England's
Millennium dataset (A46, A9), Lindert's silver prices (GPIH), Meissner's Table 1, the Herschell report's table of
exchange and Keynes (1913).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch24 as C  # noqa: E402
from style import (AMBER, EXTERNAL, FIG_W, INK, LIGHT, MONEY, MUTED, SHADE, T, arrow, canvas,  # noqa: E402
                   clean_axes, figure, halo, label, rbox, tint)


def _title(ax, s):
    ax.set_title(s, fontsize=9.0, weight="bold", loc="left", pad=4)


def _grid(ax, axis="y"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


@figure("periph_world")
def periph_world():
    """(a) the UK current account surplus, % of GDP, 1850-1913, with Reinhart and Rogoff's two clusters of
    defaults shaded; (b) the number of countries on gold by Meissner's Table 1."""
    E = C.external().loc[1850:1913]
    A = C.adoptions()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.7))
    fig.subplots_adjust(left=0.08, right=0.98, top=0.86, bottom=0.15, wspace=0.3)

    for a, b in C.RR_CLUSTERS:
        a1.axvspan(a, b, color=SHADE, lw=0, zorder=0)
    a1.plot(E.index, E.ca_gdp, color=EXTERNAL, lw=1.7, zorder=3)
    a1.text(np.mean(C.RR_CLUSTERS[0]), 10.6, T("违约集中", "defaults"), fontsize=7.4, color=MUTED, ha="center")
    a1.text(np.mean(C.RR_CLUSTERS[1]), 10.6, T("违约集中", "defaults"), fontsize=7.4, color=MUTED, ha="center")
    for y, dx, ha in ((1872, -1.0, "right"), (1890, 1.0, "left"), (1913, -1.0, "right")):
        t = a1.text(y + dx, E.ca_gdp[y] + 0.15, f"{E.ca_gdp[y]:.1f}", fontsize=7.4, color=EXTERNAL, ha=ha,
                    va="bottom")
        halo(t, 2.0)
        a1.plot([y], [E.ca_gdp[y]], "o", ms=3.0, color=EXTERNAL, mec="white", mew=0.4, zorder=4)
    a1.set_xlim(1850, 1914)
    a1.set_ylim(0, 11.5)
    a1.set_xticks([1850, 1870, 1890, 1910])
    a1.set_ylabel(T("占 GDP 的比例（%）", "% of GDP"))
    _title(a1, T("(a) 英国顺差的高峰与违约同时", "(a) UK surplus peaks with defaults"))
    _grid(a1)

    years = np.arange(1850, 1914)
    count = np.array([(A <= y).sum() for y in years])
    a2.step(years, count, where="post", color=MONEY, lw=1.8, zorder=3)
    for a, b in ((1871, 1880), (1890, 1900)):
        a2.axvspan(a, b, color=tint(MONEY, 0.1), lw=0, zorder=0)
    t = a2.text(1913.5, count[-1] - 13.0, T(f"1913 年：{count[-1]} 国", f"1913: {count[-1]}"), fontsize=7.6,
                color=MONEY, ha="right", va="top")
    halo(t, 2.0)
    n = len(C.not_adopted())
    a2.text(1851, count[-1] - 1, T(f"到 1913 年仍有\n{n} 国没有采用", f"{n} countries\nnot on gold by 1913"),
            fontsize=7.4, color=MUTED, ha="left", va="top")
    a2.set_xlim(1850, 1914)
    a2.set_ylim(0, count[-1] + 3)
    a2.set_xticks([1850, 1870, 1890, 1910])
    a2.set_ylabel(T("已采用金本位的国家数", "countries on gold"))
    _title(a2, T("(b) 金本位的两次扩散", "(b) Two waves of gold"))
    _grid(a2)
    return fig


@figure("periph_silver")
def periph_silver():
    """(a) the London price of standard silver, 1850-1914; (b) the silver value of the rupee (eq:periph-silver)
    with the Herschell table's exchange rates and the 16d. of 1898."""
    P = C.silver()
    H = C.herschell()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.7))
    fig.subplots_adjust(left=0.085, right=0.98, top=0.86, bottom=0.15, wspace=0.3)

    a1.plot(P.index, P.values, color=MONEY, lw=1.8, zorder=3)
    for y in (1873, 1893):
        a1.axvline(y, color=MUTED, lw=0.6, ls=(0, (1, 2)), zorder=2)
        a1.text(y + 0.7, 19.0, T(f"{y} 年", f"{y}"), fontsize=7.4, color=MUTED, ha="left", va="bottom")
    for y, dx, dy, ha, va in ((1873, 0.6, 0.8, "left", "bottom"), (1892, 0.8, 0.0, "left", "center"),
                              (1909, 0.0, -1.0, "center", "top")):
        t = a1.text(y + dx, P[y] + dy, f"{P[y]:.1f}", fontsize=7.4, color=MONEY, ha=ha, va=va)
        halo(t, 2.0)
    a1.set_xlim(1850, 1914)
    a1.set_ylim(18, 66)
    a1.set_xticks([1850, 1870, 1890, 1910])
    a1.set_ylabel(T("便士／盎司标准银", "pence per oz (standard)"))
    _title(a1, T("(a) 1873 年以后银价一路下跌", "(a) Silver falls after 1873"))
    _grid(a1)

    x = C.rupee_silver(P.loc[1870:1914])
    a2.plot(x.index, x.values, color=MONEY, lw=1.8, zorder=3)
    a2.plot(H.index, H.values, "o", ms=3.6, color=AMBER, mec="white", mew=0.4, zorder=4)
    line, = a2.plot([1898, 1914], [C.PAR, C.PAR], color=AMBER, lw=1.5, zorder=3)
    line.set_dashes((4, 2))
    t = a2.text(1899, C.PAR + 0.5, T("1898 年起 16 便士", "16d. from 1898"), fontsize=7.4, color=AMBER, ha="left",
                va="bottom")
    halo(t, 2.0)
    t = a2.text(1880.5, 21.0, T("汇率（赫歇尔表）", "exchange (Herschell)"), fontsize=7.4, color=AMBER, ha="left")
    halo(t, 2.0)
    t = a2.text(1903, 8.1, T("卢比的白银价值", "silver in a rupee"), fontsize=7.4, color=MONEY, ha="center",
                va="top")
    halo(t, 2.0)
    a2.axvline(1893, color=MUTED, lw=0.6, ls=(0, (1, 2)), zorder=2)
    a2.set_xlim(1870, 1914)
    a2.set_ylim(6, 24)
    a2.set_xticks([1870, 1880, 1890, 1900, 1910])
    a2.set_ylabel(T("便士／卢比", "pence per rupee"))
    _title(a2, T("(b) 汇率先跟着银值，后来离开它", "(b) The rupee leaves its silver"))
    _grid(a2)
    return fig


@figure("periph_council")
def periph_council():
    """The gold-exchange standard as two routes between London and India and the band of eq:periph-band."""
    W, Hh = 10.0, 4.1
    fig, ax = canvas(FIG_W, FIG_W * Hh / W, xlim=(0, W), ylim=(0, Hh))
    bw, xl, xi = 2.45, 0.1, 5.0                       # box width; left edges of London and India
    top, low = 2.75, 0.95
    for x, name, sub in ((xl, T("伦敦", "London"), T("英镑、黄金、金本位储备", "sterling, gold, the Reserve")),
                         (xi, T("印度", "India"), T("卢比（不能兑现）", "rupees (inconvertible)"))):
        rbox(ax, x, 0.3, bw, 3.45, fc=tint(MUTED, 0.06), ec=tint(MUTED, 0.35), lw=0.8, r=0.12, z=1)
        label(ax, x + bw / 2, 3.5, name, size=9.0, weight="bold", color=INK)
        label(ax, x + bw / 2, 3.18, sub, size=7.6, color=MUTED)
    g0, g1 = xl + bw + 0.08, xi - 0.08                # the gap between the boxes
    gm = (g0 + g1) / 2
    # the ceiling: Council Bills sold in London, or gold sent to India at 16d.
    arrow(ax, (g0, top + 0.12), (g1, top + 0.12), color=EXTERNAL, lw=1.4)
    label(ax, gm, top + 0.36, T("参事会汇票", "Council Bills"), size=7.8, color=EXTERNAL)
    arrow(ax, (g0, top - 0.3), (g1, top - 0.3), color=EXTERNAL, lw=1.2, ls=(0, (4, 2)))
    label(ax, gm, top - 0.68, T("或运金镑，\n按 16 便士换卢比", "or ship sovereigns,\nrupees at 16d."), size=7.6,
          color=EXTERNAL)
    label(ax, xl + bw / 2, top - 0.1, T("银行付英镑", "banks pay sterling"), size=7.8, color=INK)
    label(ax, xi + bw / 2, top - 0.1, T("银行领卢比", "banks get rupees"), size=7.8, color=INK)
    # the floor: sterling drafts sold in Calcutta, paid out of the Gold Standard Reserve
    arrow(ax, (g1, low + 0.3), (g0, low + 0.3), color=MONEY, lw=1.4)
    label(ax, gm, low - 0.02, T("加尔各答出售的\n英镑汇票", "sterling drafts\nsold in Calcutta"), size=7.6,  # below its arrow
          color=MONEY)
    label(ax, xl + bw / 2, low + 0.3, T("用金本位储备兑付", "paid from the Reserve"), size=7.8, color=INK)
    label(ax, xi + bw / 2, low + 0.3, T("政府收进卢比", "Government takes rupees"), size=7.8, color=INK)
    # the band, as a scale
    xs, y0, y1 = 7.95, 0.75, 3.35
    lo, hi = C.PAR - 3 / 32, C.PAR + 1 / 8

    def yy(v):
        return y0 + (v - (lo - 1 / 32)) / ((hi + 1 / 32) - (lo - 1 / 32)) * (y1 - y0)

    ax.plot([xs, xs], [yy(lo), yy(hi)], color=INK, lw=1.0, zorder=3)
    for v, txt, col in ((hi, T("16⅛ 便士：上限", "16⅛d.: ceiling"), EXTERNAL), (C.PAR, T("16 便士", "16d."), INK),
                        (lo, T("15 29/32 便士：下限", "15 29/32d.: floor"), MONEY)):
        ax.plot([xs - 0.12, xs + 0.12], [yy(v), yy(v)], color=col, lw=1.4, zorder=4)
        label(ax, xs + 0.2, yy(v), txt, size=7.6, color=col, ha="left")
    label(ax, xs + 0.9, 0.42, T("汇率带", "the band"), size=7.8, color=MUTED)
    return fig
