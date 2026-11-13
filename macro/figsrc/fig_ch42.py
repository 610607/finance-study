"""Figures for Chapter 42 (东亚奇迹：日本高速增长与发展型国家).

Style as in fig_ch41.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the colour
of their series, no legends where labels fit. Output and its parts are OUTPUT, capital MONEY, the residual AMBER;
reference lines MUTED. All numbers come from checks/check_ch42.py: the GDP per head of Penn World Table 10.01 relative
to the United States (levels()), the growth accounting on PWT 10.01 (accounting()), the estimates of Young (1994) and
Collins and Bosworth (1996) read from eastasia_facts (young_tfp(), cb_tfp()), and the CPF rates (cpf()).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch42 as C
from style import (
    AMBER,
    CASE,
    EXTERNAL,
    FIG_W,
    INK,
    INSTIT,
    LANG,
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

NAMES = {"JPN": T("日本", "Japan"), "KOR": T("韩国", "Korea"), "TWN": T("台湾", "Taiwan"),
         "HKG": T("香港", "Hong Kong"), "SGP": T("新加坡", "Singapore"), "USA": T("美国", "United States")}


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


# ---------------------------------------------------------------------------------------------------
@figure("eastasia_levels")
def eastasia_levels():
    """PWT 10.01: GDP per head (rgdpe/pop) relative to the United States, 1950-2019, log scale."""
    L = C.levels()
    fig, ax = plt.subplots(figsize=(FIG_W, 3.0))
    fig.subplots_adjust(left=0.10, right=0.86, top=0.96, bottom=0.12)
    colors = {"JPN": OUTPUT, "KOR": MONEY, "TWN": EXTERNAL, "HKG": PRICE, "SGP": CASE}
    ends = T({"SGP": 140, "HKG": 101, "TWN": 81, "KOR": 66, "JPN": 54},   # label heights, apart on the log scale
             {"SGP": 152, "HKG": 112, "TWN": 84, "KOR": 66, "JPN": 52})
    for code, color in colors.items():
        s = L[code].dropna()
        ax.plot(s.index, s.values, color=color, lw=1.8, zorder=5)
        _text(ax, 2020.5, ends[code], NAMES[code], color, weight="bold")
        assert 0.8 < ends[code] / s.iloc[-1] < 1.2, code
    ax.axhline(100, color=MUTED, lw=0.8, ls=(0, (3, 2)), zorder=2)
    _text(ax, 1951, 112, T("美国＝100", "United States = 100"), MUTED)
    ax.set_yscale("log")
    ax.set_xlim(1950, 2019)
    ax.set_ylim(4, 200)
    ax.set_yticks([5, 10, 20, 50, 100, 200])
    ax.set_yticklabels(["5", "10", "20", "50", "100", "200"])
    ax.minorticks_off()
    ax.set_xticks([1950, 1960, 1970, 1980, 1990, 2000, 2010, 2019])
    ax.set_ylabel(T("人均 GDP，美国＝100（对数刻度）", "GDP per head, US = 100 (log scale)"), labelpad=2)
    _grid(ax, "y")
    j = L["JPN"]
    ax.plot(1973, j[1973], marker="o", ms=4.6, color=OUTPUT, mec="white", mew=0.6, zorder=7)
    ax.annotate(T(f"日本 1973 年：{j[1973]:.0f}", f"Japan 1973: {j[1973]:.0f}"), xy=(1973, j[1973]), xytext=(1956, 150),
                color=OUTPUT, fontsize=7.6, arrowprops=dict(arrowstyle="-", color=OUTPUT, lw=0.6), zorder=8)
    k = L["KOR"]
    ax.plot(1960, k[1960], marker="o", ms=4.6, color=MONEY, mec="white", mew=0.6, zorder=7)
    _text(ax, 1961, k[1960] * 0.74, T(f"韩国 1960 年：{k[1960]:.1f}", f"Korea 1960: {k[1960]:.1f}"), MONEY)
    assert L.min().min() > 4 and L.max().max() < 200
    return fig


@figure("eastasia_accounting")
def eastasia_accounting():
    """(a) The growth accounting of PWT 10.01 over Young's periods: capital, labour with human capital and the residual
    (per cent a year). (b) The residual in four sets of estimates."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, T(3.1, 3.4)), gridspec_kw=dict(width_ratios=[1.05, 1]))
    fig.subplots_adjust(left=0.09, right=0.985, top=T(0.86, 0.87), bottom=T(0.21, 0.27), wspace=0.30)
    codes = [c for c, _, _ in C.PERIODS]
    A = {c: C.accounting(c, a, b) for c, a, b in C.PERIODS}
    x = np.arange(len(codes))
    cap = np.array([A[c]["cap"] for c in codes])
    lab = np.array([A[c]["lab"] for c in codes])
    tfp = np.array([A[c]["gA"] for c in codes])
    a1.bar(x, cap, 0.62, color=MONEY, zorder=3)
    a1.bar(x, lab, 0.62, bottom=cap, color=OUTPUT, zorder=3)
    a1.bar(x, tfp, 0.62, bottom=cap + lab, color=AMBER, zorder=3)
    a1.set_xticks(x)
    rot = 30 if LANG == "zh" else 90
    a1.set_xticklabels([NAMES[c] for c in codes], fontsize=7.6, rotation=rot, ha="right", rotation_mode="anchor")
    a1.set_ylabel(T("每年 %", "% a year"), labelpad=2)
    a1.set_ylim(0, 11)
    _grid(a1, "y")
    _text(a1, -0.45, 10.3, T("资本", "capital"), MONEY, weight="bold")
    _text(a1, T(1.15, 0.75), 10.3, T("劳动与人力资本", "labour, human capital"), OUTPUT, weight="bold")
    _text(a1, T(3.55, 4.55), 10.3, T("余量", "residual"), AMBER, weight="bold")
    _title(a1, T("(a) 产出的增长多半来自资本与劳动", "(a) Most output growth is capital and labour"))
    # (b) the residual in four sets of estimates
    Y, CB = C.young_tfp(), C.cb_tfp()
    share = C.facts()[C.CB_SHARE_ROW][0]
    order = ["HKG", "SGP", "KOR", "TWN", "JPN"]
    xs = np.arange(len(order))
    pw = [A[c]["gA"] for c in order]
    yo = [Y[c] for c in order]
    a2.bar(xs - 0.2, pw, 0.36, color=AMBER, zorder=3)
    a2.bar(xs + 0.2, yo, 0.36, color=INSTIT, zorder=3)
    for i, c in enumerate(order):
        if c in CB:
            a2.plot(i, CB[c], marker="s", ms=5.2, color=INK, mec="white", mew=0.6, zorder=6, ls="none")
            a2.plot(i, C.accounting(c, 1960, 1994, share)["gA"], marker="o", ms=5.2, color=MONEY, mec="white",
                    mew=0.6, zorder=6, ls="none")
    a2.axhline(0, color=MUTED, lw=0.8, zorder=2)
    a2.set_xticks(xs)
    a2.set_xticklabels([NAMES[c] for c in order], fontsize=7.6, rotation=rot, ha="right", rotation_mode="anchor")
    a2.set_ylim(-1.7, 5.2)
    a2.set_ylabel(T("余量，每年 %", "residual, % a year"), labelpad=2)
    _grid(a2, "y")
    _text(a2, -0.55, 4.85, T("Penn World Table，同 (a)", "PWT, as in (a)"), AMBER, size=7.6)
    _text(a2, -0.55, 4.25, T("Young（1994）", "Young (1994)"), INSTIT, size=7.6)
    _text(a2, -0.55, -0.72, T("■ Collins 与 Bosworth，1960—1994", "■ Collins–Bosworth, 1960–94"), INK, size=7.6)
    _text(a2, -0.55, -1.3, T("● Penn World Table 同期，份额 0.35", "● PWT, same years, share 0.35"), MONEY, size=7.6)
    _title(a2, T("(b) 同期两套估计里新加坡都最低", "(b) Singapore lowest in both sets"))
    sg = order.index("SGP")
    assert pw[sg] == min(pw) and yo[sg] == min(yo)
    assert all(A[c]["gA"] < 0.5 * A[c]["gY"] for c in codes)                       # panel (a)'s title
    assert min(pw + yo) > -1 and max(pw + yo) < 4.8
    return fig


@figure("eastasia_cpf")
def eastasia_cpf():
    """The CPF contribution rates of employers and employees aged 35 and below, July 1955 to 1990 (step plot)."""
    D = C.cpf()
    D = D[D.index <= "1990-12"]
    t = np.array([int(m[:4]) + (int(m[5:]) - 1) / 12 for m in D.index] + [1991.0])
    fig, ax = plt.subplots(figsize=(FIG_W, 2.5))
    fig.subplots_adjust(left=0.09, right=0.98, top=0.96, bottom=0.14)
    er = np.append(D["Employer"].values, D["Employer"].values[-1])
    ee = np.append(D["Employee"].values, D["Employee"].values[-1])
    ax.step(t, er, where="post", color=MONEY, lw=2.0, zorder=5)
    ax.step(t, ee, where="post", color=AMBER, lw=2.0, ls=(0, (4, 2)), zorder=6)
    ax.set_xlim(1955, 1991)
    ax.set_ylim(0, 28)
    ax.set_xticks([1955, 1960, 1965, 1970, 1975, 1980, 1985, 1990])
    ax.set_ylabel(T("工资的 %", "% of wage"), labelpad=2)
    _grid(ax, "y")
    _text(ax, 1956, 7.2, T("1955 年 7 月：各 5%", "July 1955: 5% each"), INK)
    _text(ax, 1975.6, 26.6, T("1984 年 7 月：各 25%", "July 1984: 25% each"), INK)
    _text(ax, 1985.9, 8.0, T("1986 年 4 月：雇主 10%", "April 1986: employer 10%"), INK, ha="right")
    _text(ax, T(1979.7, 1975.4), T(22.3, 18.6), T("雇主", "employer"), MONEY, weight="bold")
    _text(ax, 1972.6, 8.2, T("雇员", "employee"), AMBER, weight="bold")
    assert C.cpf_at("1984-07", "Employer") == C.cpf_at("1984-07", "Employee") == 25
    assert C.cpf_at("1986-04", "Employer") == 10
    return fig
