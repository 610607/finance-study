"""Figures for Chapter 29 (大萧条：世界与“金色枷锁”).

Style as in fig_ch28.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series. Exchange rates are EXTERNAL, Bank Rate MONEY, the price of silver PRICE, output OUTPUT; the
second series of a panel is AMBER, dashed, with square markers (the yuan's silver value, the least-squares line).
All numbers come from checks/check_ch29.py: the Bank of England's monthly data and Bank Rate (boe(), bank_rate()),
the exits from gold of Bernanke and James (1991) with the Maddison Project Database (exit_dates(), ratio1935()),
the ten points of Eichengreen and Sachs's Figure 1 (es(), es_fit()) and the silver and yuan series (silver(),
yuan_monthly()).
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch29 as C
from style import (
    AMBER,
    EXTERNAL,
    FIG_W,
    INSTIT,
    LIGHT,
    MONEY,
    MUTED,
    OUTPUT,
    PRICE,
    T,
    clean_axes,
    figure,
    halo,
)

SQUARE = dict(marker="s", ms=3.2, mfc=AMBER, mec="white", mew=0.4)
DOT = dict(marker="o", ms=3.2, mec="white", mew=0.5)


def _title(ax, s):
    ax.set_title(s, fontsize=9.0, weight="bold", loc="left", pad=4)


def _grid(ax, axis="y"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


def _t(y: int, m: int) -> float:
    """The middle of a month on a time axis in years."""
    return y + (m - 0.5) / 12


def _d(d: date) -> float:
    return d.year + (d.timetuple().tm_yday - 1) / 365.25


@figure("depressionworld_sterling")
def depressionworld_sterling():
    """(a) Dollars per pound, monthly, 1929-1936, with the old parity; (b) Bank Rate, 1929-1936, as steps."""
    B = C.boe()
    g = B.usd_per_gbp
    x = np.array([_t(y, m) for y, m in g.index])
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.85))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.86, bottom=0.15, wspace=0.27)

    P = C.parity()
    drop = C.fall(g[(1931, 8)], g[(1931, 12)])
    assert 29 < drop < 32                                          # 跌了约三成
    a1.plot(x, g.values, color=EXTERNAL, lw=1.6, zorder=4)
    a1.axhline(P, color=MUTED, lw=0.8, ls=(0, (4, 2)), zorder=2)
    lab = a1.text(1929.1, P + 0.04, T(f"旧平价 {P:.2f}", f"old parity {P:.2f}"), color=MUTED, fontsize=7.6,
                  ha="left", va="bottom")
    halo(lab, 2.0)
    for (y, m), txt, dy, ha in (((1931, 9), T("1931 年 9 月", "Sep 1931"), 0, "right"),
                                ((1933, 4), T("美元离开黄金", "dollar off gold"), 0, "left")):
        xv = _t(y, m) - 0.5 / 12
        a1.axvline(xv, color=MUTED, lw=0.6, ls=(0, (1, 2)), zorder=2)
        lab = a1.text(xv + (-0.08 if ha == "right" else 0.08), 3.18, txt, color=MUTED, fontsize=7.6, ha=ha,
                      va="bottom")
        halo(lab, 2.0)
    lo = g.loc[1931:1933].idxmin()
    lab = a1.text(_t(*lo), g[lo] - 0.06, f"{g[lo]:.2f}", color=EXTERNAL, fontsize=7.6, ha="center", va="top")
    halo(lab, 2.0)
    a1.set_xlim(1929, 1937)
    a1.set_ylim(3.0, 5.4)
    a1.set_xticks([1929, 1931, 1933, 1935])
    a1.set_ylabel(T("美元／英镑", "dollars per pound"))
    _grid(a1)
    _title(a1, T("(a) 1931 年 9 月以后，英镑跌了三成", "(a) After September 1931 the pound fell 30%"))

    r = C.bank_rate()
    days = list(r.index) + [date(1936, 12, 31)]
    xs = [_d(d) for d in days]
    ys = list(r.values) + [r.values[-1]]
    assert r[date(1931, 9, 21)] == 6 and r.min() == 2 and r.index[-1] == date(1932, 6, 30)
    a2.step(xs, ys, where="post", color=MONEY, lw=1.6, zorder=4)
    for d, dy, ha in ((date(1931, 9, 21), 0.25, "left"), (date(1932, 6, 30), 0.25, "left")):
        lab = a2.text(_d(d) + 0.08, r[d] + dy, f"{r[d]:g}%", color=MONEY, fontsize=7.6, ha=ha, va="bottom")
        halo(lab, 2.0)
    a2.set_xlim(1929, 1937)
    a2.set_ylim(0, 7.5)
    a2.set_xticks([1929, 1931, 1933, 1935])
    a2.set_ylabel(T("贴现率（%）", "Bank Rate (%)"))
    _grid(a2)
    _title(a2, T("(b) 贴现率 1932 年降到 2%", "(b) Bank Rate down to 2% in 1932"))
    for ax in (a1, a2):
        ax.set_xlabel(T("年份", "year"))
    return fig


NAMES = {"AUS": ("澳大利亚", "Australia"), "ARG": ("阿根廷", "Argentina"), "NZL": ("新西兰", "New Zealand"),
         "DEU": ("德国", "Germany"), "HUN": ("匈牙利", "Hungary"), "AUT": ("奥地利", "Austria"),
         "CAN": ("加拿大", "Canada"), "DNK": ("丹麦", "Denmark"), "GRC": ("希腊", "Greece"), "NOR": ("挪威", "Norway"),
         "SWE": ("瑞典", "Sweden"), "GBR": ("英国", "UK"), "FIN": ("芬兰", "Finland"), "JPN": ("日本", "Japan"),
         "ROU": ("罗马尼亚", "Rumania"), "USA": ("美国", "US"), "ITA": ("意大利", "Italy"), "BEL": ("比利时", "Belgium"),
         "POL": ("波兰", "Poland"), "FRA": ("法国", "France"), "NLD": ("荷兰", "Netherlands"),
         "CHE": ("瑞士", "Switzerland")}
# label offsets (years, points of the index) and alignment; the five of September 1931 above 105 share one label
EXIT_LABELS = {"AUS": (0.09, 0.0, "left"), "ARG": (0.09, 0.0, "left"), "NZL": (0.09, 0.0, "left"),
               "DEU": (-0.09, 0.0, "right"), "HUN": (-0.09, -0.6, "right"), "AUT": (0.09, 0.9, "left"),
               "CAN": (0.09, -0.9, "left"), "FIN": (0.09, 0.0, "left"), "JPN": (0.09, -0.6, "left"),
               "ROU": (0.09, 0.0, "left"), "USA": (0.09, 0.0, "left"), "ITA": (0.09, 0.0, "left"),
               "BEL": (0.09, 0.0, "left"), "POL": (-0.09, 0.0, "right"), "CHE": (0.0, 2.2, "center")}
CLUSTER = ["SWE", "NOR", "DNK", "GRC", "GBR"]
PAIR = ["FRA", "NLD"]                       # the same month and nearly the same value: one label


@figure("depressionworld_exits")
def depressionworld_exits():
    """GDP per head in 1935 (1929 = 100) against the month of leaving gold, 22 economies."""
    E, R = C.exit_dates(), C.ratio1935()
    early, late = C.exit_groups()
    assert set(EXIT_LABELS) | set(CLUSTER) | set(PAIR) == set(E) and len(E) == 22
    assert E["FRA"] == E["NLD"] and abs(R["FRA"] - R["NLD"]) < 0.5
    assert all(E[k] == (1931, 9) and R[k] > 105 for k in CLUSTER)
    fig, ax = plt.subplots(figsize=(FIG_W, 3.1))
    fig.subplots_adjust(left=0.10, right=0.985, top=0.97, bottom=0.15)
    for k, (y, m) in E.items():
        col = EXTERNAL if k in early else INSTIT
        ax.plot(_t(y, m), R[k], color=col, zorder=4, **DOT)
        if k in EXIT_LABELS:
            dx, dy, ha = EXIT_LABELS[k]
            lab = ax.text(_t(y, m) + dx, R[k] + dy, T(*NAMES[k]), color=col, fontsize=7.6, ha=ha, va="center")
            halo(lab, 2.0)
    xc = _t(1931, 9)
    lab = ax.text(xc - 0.12, 109.0, T("瑞典、挪威、丹麦、\n希腊、英国", "Sweden, Norway, Denmark,\nGreece, UK"),
                  color=EXTERNAL, fontsize=7.6, ha="right", va="center", linespacing=1.1)
    halo(lab, 2.0)
    lab = ax.text(_t(*E["FRA"]) - 0.09, R["FRA"], T("法国、荷兰", "France, Netherlands"), color=INSTIT, fontsize=7.6,
                  ha="right", va="center")
    halo(lab, 2.0)
    ax.axhline(100, color=MUTED, lw=0.6, ls=(0, (1, 2)), zorder=2)
    ax.axvline(1932, color=MUTED, lw=0.6, ls=(0, (1, 2)), zorder=2)
    me, ml = R[early].mean(), R[late].mean()
    lab = ax.text(1932.08, 117.5, T(f"1932 年或更晚离开的 {len(late)} 个：平均 {ml:.1f}",
                                    f"{len(late)} leaving after 1931: mean {ml:.1f}"), color=INSTIT, fontsize=7.8,
                  ha="left", va="center")
    halo(lab, 2.0)
    lab = ax.text(1929.45, 84.5, T(f"1931 年底以前离开的 {len(early)} 个：平均 {me:.1f}",
                                  f"{len(early)} leaving by 1931: mean {me:.1f}"), color=EXTERNAL, fontsize=7.8,
                  ha="left", va="center")
    halo(lab, 2.0)
    ax.set_xlim(1929.4, 1937.3)
    ax.set_ylim(70, 120)
    ax.set_xticks(range(1930, 1938))
    ax.set_xlabel(T("离开金本位的时间", "date of leaving gold"))
    ax.set_ylabel(T("1935 年的人均 GDP（1929 年 = 100）", "GDP per head, 1935 (1929 = 100)"))
    _grid(ax, axis="both")
    return fig


ES_LABELS = {"Finland": (1.2, 0.0, "left"), "Denmark": (-1.2, 0.0, "right"), "Sweden": (1.2, -1.2, "left"),
             "United Kingdom": (1.2, 0.0, "left"), "Norway": (1.2, -0.6, "left"), "Germany": (-1.2, 0.0, "right"),
             "Italy": (-1.2, 0.0, "right"), "Netherlands": (1.2, 0.0, "left"), "Belgium": (1.2, 0.0, "left"),
             "France": (1.2, 0.0, "left")}
ES_NAMES = {"Finland": ("芬兰", "Finland"), "Denmark": ("丹麦", "Denmark"), "Sweden": ("瑞典", "Sweden"),
            "United Kingdom": ("英国", "UK"), "Norway": ("挪威", "Norway"), "Germany": ("德国", "Germany"),
            "Italy": ("意大利", "Italy"), "Netherlands": ("荷兰", "Netherlands"), "Belgium": ("比利时", "Belgium"),
            "France": ("法国", "France")}


@figure("depressionworld_es")
def depressionworld_es():
    """Industrial production in 1935 against the gold value of the currency in 1935 (1929 = 100), ten European
    countries, with the least-squares line."""
    S = C.es()
    fit = C.es_fit()
    a, b = fit.params
    assert b < 0 and set(ES_LABELS) == set(S.index)
    fig, ax = plt.subplots(figsize=(FIG_W, 3.0))
    fig.subplots_adjust(left=0.10, right=0.97, top=0.97, bottom=0.15)
    xs = np.array([42, 106])
    ax.plot(xs, a + b * xs, color=AMBER, lw=1.4, dashes=(4, 2), zorder=3)
    lab = ax.text(57, 92, T(f"最小二乘：{a:.1f} − {-b:.2f} × 汇率", f"least squares: {a:.1f} − {-b:.2f} × rate"),
                  color=AMBER, fontsize=7.8, ha="left", va="top")
    halo(lab, 2.0)
    for c, r in S.iterrows():
        ax.plot(r.er1935, r.ip1935, color=OUTPUT, zorder=4, **DOT)
        dx, dy, ha = ES_LABELS[c]
        lab = ax.text(r.er1935 + dx, r.ip1935 + dy, T(*ES_NAMES[c]), color=OUTPUT, fontsize=7.6, ha=ha, va="center")
        halo(lab, 2.0)
    ax.set_xlim(40, 110)
    ax.set_ylim(65, 132)
    ax.set_xlabel(T("1935 年本币的黄金价值（1929 年的平价 = 100）", "gold value of the currency, 1935 (1929 parity = 100)"))
    ax.set_ylabel(T("1935 年的工业生产（1929 年 = 100）", "industrial production, 1935 (1929 = 100)"))
    _grid(ax, axis="both")
    return fig


@figure("depressionworld_silver")
def depressionworld_silver():
    """(a) The New York price of silver and the yuan, US cents, annual, 1929-1936, with the yuan's silver value
    0.7553 p_s; (b) the yuan in cents, monthly, 1929-1936."""
    S = C.silver().loc[1929:1936]
    F = C.facts()
    fine = F["bs_7553"][1]
    yrs = np.array(S.index)
    p, yu = S.ny_silver_cents_per_oz.values, S.yuan_cents_year.values
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.9))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.86, bottom=0.15, wspace=0.27)

    assert np.all(np.abs(fine * p[:5] - yu[:5]) < 2.5)                      # 1929-1933: the yuan follows silver
    assert fine * p[6] - yu[6] > 10                                          # 1935: far below
    a1.plot(yrs, p, color=PRICE, lw=1.6, zorder=4, **DOT)
    a1.plot(yrs, fine * p, color=AMBER, lw=1.4, dashes=(4, 2), zorder=3, **SQUARE)
    a1.plot(yrs, yu, color=EXTERNAL, lw=1.6, zorder=5, **DOT)
    for v, txt, col, dy in ((p[-1], T("银价", "silver"), PRICE, 0.0), (fine * p[-1], T("含银值", "its silver"), AMBER, 0.6),
                            (yu[-1], T("汇价", "the yuan"), EXTERNAL, -0.8)):
        lab = a1.text(yrs[-1] + 0.18, v + dy, txt, color=col, fontsize=7.6, ha="left", va="center")
        halo(lab, 2.0)
    a1.set_xlim(1928.6, 1937.5)
    a1.set_ylim(10, 72)
    a1.set_xticks([1929, 1931, 1933, 1935])
    a1.set_ylabel(T("美分", "US cents"))
    _grid(a1)
    _title(a1, T("(a) 1934 年以前，一元跟着银价走", "(a) Until 1934 the yuan followed silver"))

    m = C.yuan_monthly()
    x = np.array([_t(y, mm) for y, mm in m.index])
    after = m[[k for k in m.index if k >= (1935, 12)]]
    assert 29 < after.min() and after.max() < 31                             # 改革以后稳在 30 美分左右
    peak = m.loc[1932:1936].idxmax()
    assert peak == (1935, 5)
    a2.plot(x, m.values, color=EXTERNAL, lw=1.5, zorder=4)
    for (y, mm), txt, yt, ha in (((1934, 10), T("出口税", "export duty"), 44.2, "right"),
                                 ((1935, 11), T("改行纸币", "fiat money"), 24.0, "right")):
        xv = _t(y, mm) - 0.5 / 12
        a2.axvline(xv, color=MUTED, lw=0.6, ls=(0, (1, 2)), zorder=2)
        lab = a2.text(xv + (-0.08 if ha == "right" else 0.08), yt, txt, color=MUTED, fontsize=7.6, ha=ha, va="center")
        halo(lab, 2.0)
    lab = a2.text(_t(*peak), m[peak] + 0.6, f"{m[peak]:.1f}", color=EXTERNAL, fontsize=7.6, ha="center", va="bottom")
    halo(lab, 2.0)
    a2.set_xlim(1929, 1937)
    a2.set_ylim(18, 47)
    a2.set_xticks([1929, 1931, 1933, 1935])
    a2.set_ylabel(T("一元合多少美分", "US cents per yuan"))
    _grid(a2)
    _title(a2, T("(b) 改革以后，一元稳在 30 美分", "(b) After the reform, 30 cents"))
    for ax in (a1, a2):
        ax.set_xlabel(T("年份", "year"))
    return fig
