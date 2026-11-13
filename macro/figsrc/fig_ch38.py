"""Figures for Chapter 38 (菲利普斯曲线与宏观计量模型).

Style as in fig_ch37.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the colour
of their series, no legends. Wage and price changes are PRICE (a second series of a panel AMBER, squares), the record
of a case CASE, output and the capital stock OUTPUT; the yearly points behind a summary are a light tint, reference
lines MUTED. All numbers come from checks/check_ch38.py: Phillips's curve (curve(), curve_pars()), the six crosses
recomputed from the Bank of England's series (crosses(), scatter_1861_1913(), scatter_1948_1957()), Phillips's
Table 1 (table1()), the menu snapshot (menu(), FIG_US, FIG_CA) with Samuelson and Solow's points, and Klein's Model I
(klein_path(), klein_closed()).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch38 as C
from style import (
    AMBER,
    CASE,
    FIG_W,
    INK,
    LIGHT,
    MUTED,
    OUTPUT,
    PRICE,
    T,
    clean_axes,
    figure,
    halo,
    tint,
)

DOT = dict(marker="o", ms=4.6, mec="white", mew=0.6)
HOLLOW = dict(marker="o", ms=6.0, mfc="white", mew=1.3)


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


def _ref(ax, y, x0, x1):
    ax.plot([x0, x1], [y, y], color=MUTED, lw=0.8, ls=(0, (1, 2)), zorder=2)


# ---------------------------------------------------------------------------------------------------
@figure("phillips_uk")
def phillips_uk():
    """(a) 1861-1913: each year's rate of change of Feinstein's average weekly earnings (first central difference)
    against the trade-union unemployment rate (tinted points), the six averages in Phillips's intervals (black crosses),
    Phillips's curve eq:phillips-curve, and 1948-1957 with the civilian rate (squares). (b) Phillips's Table 1,
    1948-1957: the actual change of wage rates against the demand pull, with the diagonal."""
    S, L, X, T1 = C.scatter_1861_1913(), C.scatter_1948_1957(), C.crosses(), C.table1()
    a_, b_, c_ = C.curve_pars()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 3.05), gridspec_kw=dict(width_ratios=[1.25, 1]))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.885, bottom=0.14, wspace=0.25)

    # (a) the years, the crosses, the curve
    a1.axhline(0, color=MUTED, lw=0.7, ls=(0, (1, 2)), zorder=2)
    a1.plot(S["u"], S["y"], ls="none", marker="o", ms=3.6, color=tint(PRICE, 0.55), mec="white", mew=0.4, zorder=3)
    x = np.linspace(0.75, 11, 300)
    a1.plot(x, C.curve(x), color=PRICE, lw=2.0, zorder=5)
    a1.plot([c["u"] for c in X], [c["y"] for c in X], ls="none", marker="+", ms=9, mew=1.8, color=INK, zorder=7)
    a1.plot(L["u"], L["y"], ls="none", marker="s", ms=4.2, color=AMBER, mec="white", mew=0.5, zorder=6)
    _text(a1, 3.4, 6.4,
          T(f"菲利普斯的曲线\n$y+{a_:.3f}={b_:.3f}\\,x^{{{c_:.3f}}}$", f"Phillips's curve\n$y+{a_:.3f}={b_:.3f}\\,x^{{{c_:.3f}}}$"),
          PRICE, weight="bold")
    _text(a1, 11.0, 3.4, T("十字：六组的平均", "crosses: the six averages"), INK, ha="right")
    _text(a1, L["u"].max() + 0.35, L["y"].max() + 0.2, T("1948—1957 年", "1948-1957"), AMBER, weight="bold")
    a1.set_xlim(0, 11.2)
    a1.set_ylim(-4.5, 10.5)
    a1.set_xticks([0, 2, 4, 6, 8, 10])
    a1.set_yticks([-4, -2, 0, 2, 4, 6, 8, 10])
    a1.set_xlabel(T("失业率（%）", "unemployment rate (%)"))
    a1.set_ylabel(T("工资的年变动（%）", "wage change (%)"))
    _grid(a1)
    _title(a1, T("(a) 1861—1913 年：六组的平均顺着曲线走", "(a) 1861-1913: the six averages follow the curve"))
    assert all(X[i]["y"] > X[i + 1]["y"] for i in range(len(X) - 1))
    assert S["y"].between(-4.5, 10.5).all() and S["u"].max() < 11.2 and L["y"].max() < 10.5

    # (b) Table 1: actual change against the demand pull
    lim = (0, 11.5)
    a2.plot(lim, lim, color=MUTED, lw=0.8, ls=(0, (1, 2)), zorder=2)
    cost = [1951, 1952]
    for y, r in T1.iterrows():
        col = AMBER if y in cost else PRICE
        mk = dict(marker="s", ms=4.8, mec="white", mew=0.5) if y in cost else DOT
        a2.plot([r["demand"]], [r["actual"]], ls="none", color=col, zorder=6, **mk)
    place = {1948: (-0.25, 0.1, "right"), 1949: (-0.25, -0.1, "right"), 1950: (-0.25, 0.45, "right"),
             1951: (0.25, 0.2, "left"), 1952: (0.25, 0.0, "left"), 1953: (0.25, -0.15, "left"),
             1954: (0.25, -0.35, "left"), 1955: (-0.25, 0.35, "right"), 1956: (0.25, 0.0, "left"),
             1957: (0.25, -0.1, "left")}
    for y, r in T1.iterrows():
        dx, dy, ha = place[y]
        _text(a2, r["demand"] + dx, r["actual"] + dy, f"{y:.0f}", AMBER if y in cost else PRICE, ha=ha, size=7.6)
    _text(a2, 8.3, 9.4, T("两者相等", "equal"), MUTED, ha="center")
    _text(a2, 11.2, 0.5, T("方块：成本通胀的两年", "squares: cost inflation"), AMBER, ha="right", va="bottom")
    a2.set_xlim(*lim)
    a2.set_ylim(*lim)
    a2.set_xticks([0, 2, 4, 6, 8, 10])
    a2.set_yticks([0, 2, 4, 6, 8, 10])
    a2.set_xlabel(T("需求拉动（%）", "demand pull (%)"))
    a2.set_ylabel(T("工资率的实际变动（%）", "actual change of wage rates (%)"))
    _grid(a2)
    _title(a2, T("(b) 1951、1952 年远在对角线上方", "(b) 1951 and 1952 far above the line"))
    assert all(T1.loc[y, "actual"] - T1.loc[y, "demand"] > 1.5 for y in cost)
    assert T1["actual"].max() < lim[1] and T1["demand"].max() < lim[1]
    return fig


# ---------------------------------------------------------------------------------------------------
@figure("phillips_menu")
def phillips_menu():
    """(a) The United States, FIG_US: the unemployment rate against the change of the yearly average CPI (Tables C-24
    and C-45 of the Economic Report of the President 1971), with Samuelson and
    Solow's points A and B and a dashed line between them (only a sketch). (b) Canada, FIG_CA, the same (Historical
    Statistics of Canada, D491 and K8), the years 1956-1961 joined in order and labelled."""
    F, M = C.facts(), C.menu()
    uA, (uB, pB) = F["ss_pointA"][0], F["ss_pointB"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 3.0), sharey=True)
    fig.subplots_adjust(left=0.075, right=0.985, top=0.885, bottom=0.14, wspace=0.10)
    for ax in (a1, a2):
        ax.axhline(0, color=MUTED, lw=0.7, ls=(0, (1, 2)), zorder=2)
        ax.set_xlim(1.5, 7.8)
        ax.set_ylim(-1.8, 11.5)
        ax.set_xticks([2, 3, 4, 5, 6, 7])
        ax.set_yticks([0, 2, 4, 6, 8, 10])
        ax.set_xlabel(T("失业率（%）", "unemployment rate (%)"))
        _grid(ax)
    a1.set_ylabel(T("消费物价的年涨幅（%）", "change of consumer prices (%)"))

    # (a) the United States and the two points
    U = M.loc[C.FIG_US[0]:C.FIG_US[1]]
    a1.plot(U["us_unemp_pct"], U["us_infl"], ls="none", color=PRICE, zorder=5, **DOT)
    a1.plot([uA, uB], [0, pB], color=INK, lw=1.2, dashes=(4, 2), zorder=4)
    a1.plot([uA, uB], [0, pB], ls="none", color=INK, mec=INK, zorder=7, **HOLLOW)
    _text(a1, uA - 0.2, -0.6, "A", INK, ha="right", weight="bold", size=8.4)
    _text(a1, uB - 0.15, pB + 0.45, "B", INK, ha="right", weight="bold", size=8.4)
    label = {1948: (0.15, 0.35, "left"), 1951: (-0.15, 0.35, "right"), 1958: (0.12, 0.35, "left"),
             1961: (0.12, 0.3, "left"), 1966: (-0.12, 0.35, "right"), 1968: (0.15, 0.0, "left"),
             1969: (0.15, 0.3, "left")}
    for y, (dx, dy, ha) in label.items():
        _text(a1, U.loc[y, "us_unemp_pct"] + dx, U.loc[y, "us_infl"] + dy, f"{y}", PRICE, ha=ha, size=7.6)
    _text(a1, 4.9, 9.6, T("A、B：萨缪尔森与索洛（1960）", "A, B: Samuelson and Solow (1960)"), INK, ha="center")
    _title(a1, T(f"(a) 美国：{C.FIG_US[1]} 年比 B 点更差", f"(a) US: {C.FIG_US[1]} worse than B"))
    u69, i69 = U.loc[1969, "us_unemp_pct"], U.loc[1969, "us_infl"]
    assert u69 > uB and i69 > pB and U["us_infl"].between(-1.8, 11.5).all() and U["us_unemp_pct"].between(1.5, 7.8).all()

    # (b) Canada, 1956-1961 labelled
    K = M.loc[C.FIG_CA[0]:C.FIG_CA[1]]
    case = K.loc[1956:1961]
    a2.plot(K["ca_unemp_pct"], K["ca_infl"], ls="none", marker="o", ms=4.0, color=tint(CASE, 0.5), mec="white", mew=0.5,
            zorder=4)
    a2.plot(case["ca_unemp_pct"], case["ca_infl"], color=CASE, lw=1.6, zorder=5)
    a2.plot(case["ca_unemp_pct"], case["ca_infl"], ls="none", color=CASE, zorder=6, **DOT)
    place = {1956: (-0.12, 0.35, "right"), 1957: (0.15, 0.3, "left"), 1958: (0.12, 0.35, "left"),
             1959: (-0.12, -0.45, "right"), 1960: (0.0, 0.5, "center"), 1961: (0.12, -0.5, "left")}
    for y, (dx, dy, ha) in place.items():
        _text(a2, case.loc[y, "ca_unemp_pct"] + dx, case.loc[y, "ca_infl"] + dy, f"{y}", CASE, ha=ha, size=7.6,
              weight="bold")
    _text(a2, 2.5, 10.55, "1951", MUTED, size=7.6)
    _title(a2, T("(b) 加拿大：1956—1961 年移向右下", "(b) Canada, 1956-61: down and right"))
    assert case["ca_unemp_pct"].iloc[-1] > case["ca_unemp_pct"].iloc[0] and K["ca_infl"].between(-1.8, 11.5).all()
    assert abs(K.loc[1951, "ca_unemp_pct"] - 2.4) < 0.2 and abs(K.loc[1951, "ca_infl"] - 10.55) < 0.1
    return fig


# ---------------------------------------------------------------------------------------------------
@figure("phillips_klein")
def phillips_klein():
    """ex:phillips-klein: G up by 1 for good from year 1 in Model I (eq:phillips-klein), the other exogenous variables
    unchanged and the disturbances zero. (a) The change of X = Y + T - W2 with the impact and long-run multipliers;
    (b) the change of the capital stock K with its long-run value."""
    P, cf = C.klein_path(30), C.klein_closed()
    t = P.index.to_numpy()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.7), sharex=True)
    fig.subplots_adjust(left=0.07, right=0.985, top=0.87, bottom=0.16, wspace=0.22)
    for ax in (a1, a2):
        ax.set_xlim(0, 31)
        ax.set_xticks([1, 5, 10, 15, 20, 25, 30])
        ax.set_xlabel(T("年", "year"))
        _grid(ax, "y")
        ax.axhline(0, color=MUTED, lw=0.7, zorder=2)

    a1.plot(t, P["X"], color=OUTPUT, lw=2.0, zorder=5, marker="o", ms=3.2, mec="white", mew=0.4)
    _ref(a1, cf["impact"], 0, 31)
    _ref(a1, cf["long"], 0, 31)
    _text(a1, 30.6, cf["impact"] - 0.3, T(f"冲击乘数 {cf['impact']:.2f}", f"impact {cf['impact']:.2f}"), MUTED, ha="right",
          va="top")
    _text(a1, 30.6, cf["long"] + 0.3, T(f"长期乘数 {cf['long']:.2f}", f"long run {cf['long']:.2f}"), MUTED, ha="right",
          va="bottom")
    pk = int(P["X"].loc[:10].idxmax())
    _text(a1, pk + 0.8, P.loc[pk, "X"] + 0.1, T(f"第 {pk} 年 {P.loc[pk, 'X']:.1f}", f"year {pk}: {P.loc[pk, 'X']:.1f}"),
          OUTPUT, weight="bold")
    a1.set_ylim(-0.3, 6.6)
    a1.set_yticks([0, 1, 2, 3, 4, 5, 6])
    a1.set_ylabel(T("变动（十亿 1934 年美元）", "change (billions of 1934 dollars)"))
    _title(a1, T(f"(a) $X$ 先升到 {P.loc[pk, 'X']:.1f}，再回落", f"(a) $X$ up to {P.loc[pk, 'X']:.1f}, then down"))
    assert P["X"].max() < 6.6 and pk == 4

    a2.plot(t, P["K"], color=OUTPUT, lw=2.0, zorder=5, marker="o", ms=3.2, mec="white", mew=0.4)
    _ref(a2, cf["capital"], 0, 31)
    _text(a2, 30.6, cf["capital"] - 0.35, T(f"长期 {cf['capital']:.2f}", f"long run {cf['capital']:.2f}"), MUTED,
          ha="right", va="top")
    kp = int(P["K"].idxmax())
    _text(a2, kp + 0.8, P.loc[kp, "K"] + 0.25, T(f"第 {kp} 年 {P.loc[kp, 'K']:.1f}", f"year {kp}: {P.loc[kp, 'K']:.1f}"),
          OUTPUT, weight="bold")
    a2.set_ylim(-0.3, 7.6)
    a2.set_yticks([0, 2, 4, 6])
    _title(a2, T("(b) 资本存量 $K$ 多起来又减少", "(b) The capital stock $K$ overshoots"))
    assert P["K"].max() < 7.6 and P["K"].iloc[-1] < P["K"].max()
    return fig
