"""Figures for Chapter 40 (索洛增长模型).

Style as in fig_ch39.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the colour
of their series, no legends. Output and saving are OUTPUT (the second saving rate dashed), the investment needed and
capital INK, a second series of a panel AMBER; reference lines MUTED. All numbers come from checks/check_ch40.py: the
teaching model (diagram(), transition(), steady(), S0, S1, NGD, G), the regressions on Penn World Table 10.01
(convergence_points(), regressions()) and the Soviet tables of Easterly and Fischer (1995) and of the Joint Economic
Committee (1990) (soviet()).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch40 as C
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

DOT = dict(marker="o", ms=4.6, mec="white", mew=0.6)


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


def _pct(x: float) -> str:
    return f"{100 * x:.0f}%"


# ---------------------------------------------------------------------------------------------------
@figure("solow_diagram")
def solow_diagram():
    """The Solow diagram of ex:solow-double: saving per effective worker s k^alpha for s = 10% (solid) and 20%
    (dashed), the investment needed (n + g + delta) k, and the two steady states."""
    D = C.diagram()
    (k0, y0), (k1, y1) = C.steady(C.S0), C.steady(C.S1)
    fig, ax = plt.subplots(figsize=(FIG_W, 2.75))
    fig.subplots_adjust(left=0.10, right=0.97, top=0.89, bottom=0.16)
    ax.plot(D["k"], D["need"], color=INK, lw=1.6, zorder=5)
    ax.plot(D["k"], D["save0"], color=OUTPUT, lw=2.0, zorder=6)
    ax.plot(D["k"], D["save1"], color=OUTPUT, lw=2.0, ls=(0, (4, 2)), zorder=6)
    for k, s in ((k0, C.S0), (k1, C.S1)):
        ax.plot([k, k], [0, C.NGD * k], color=MUTED, lw=0.8, ls=(0, (1, 2)), zorder=3)
        ax.plot([k], [C.NGD * k], color=INK, zorder=7, **DOT)
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 0.56)
    ax.set_xticks([0, 2, 4, 6, 8])
    ax.set_yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5])
    ax.set_xlabel(T("每个有效工人的资本 $k$", "capital per effective worker $k$"))
    ax.set_ylabel(T("每个有效工人每年的量", "per effective worker, a year"))
    _grid(ax)
    _text(ax, 7.95, C.NGD * 7.95 + 0.012, T(f"维持资本所需的投资 $(n+g+\\delta)\\,k$，{_pct(C.NGD)}",
                                            f"investment needed $(n+g+\\delta)\\,k$, {_pct(C.NGD)}"), INK, ha="right",
          va="bottom")
    _text(ax, 7.85, 0.33, T(f"储蓄 $s\\,k^{{\\alpha}}$，$s$ = {_pct(C.S1)}",
                                                     f"saving $s\\,k^{{\\alpha}}$, $s$ = {_pct(C.S1)}"), OUTPUT,
          ha="right", va="center", weight="bold")
    _text(ax, 7.85, C.S0 * 7.85 ** C.ALPHA - 0.02, T(f"$s$ = {_pct(C.S0)}", f"$s$ = {_pct(C.S0)}"), OUTPUT, ha="right",
          va="top", weight="bold")
    _text(ax, k0 + 0.12, 0.012, f"$k^*$ = {k0:.2f}", INK, va="bottom")
    _text(ax, k1 + 0.12, 0.012, f"$k^*$ = {k1:.2f}", INK, va="bottom")
    _title(ax, T(f"储蓄率翻一番：稳态资本变为 {k1 / k0:.2f} 倍，产出只变为 {y1 / y0:.2f} 倍",
                 f"Saving doubled: steady-state capital ×{k1 / k0:.2f}, output only ×{y1 / y0:.2f}"))
    assert D["need"].max() < 0.5 and C.S1 * 8 ** C.ALPHA < C.NGD * 8 and k1 < 7.5
    return fig


# ---------------------------------------------------------------------------------------------------
@figure("solow_transition")
def solow_transition():
    """ex:solow-transition: the saving rate raised from 10% to 20% in year 0. (a) Log output per worker (year 0 = 0) on
    the new path and on the old one. (b) The growth rate of output per worker from each year to the next."""
    P = C.transition(60)
    g = P["growth"].dropna()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.75))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.875, bottom=0.16, wspace=0.30)
    a1.plot(P["year"], P["lny_old"], color=MUTED, lw=1.5, ls=(0, (4, 2)), zorder=4)
    a1.plot(P["year"], P["lny"], color=OUTPUT, lw=2.0, zorder=5)
    a1.set_xlim(0, 60)
    a1.set_ylim(0, 1.7)
    a1.set_xticks([0, 10, 20, 30, 40, 50, 60])
    a1.set_yticks([0, 0.4, 0.8, 1.2, 1.6])
    a1.set_xlabel(T("储蓄率提高以后的年数", "years after the rise"))
    a1.set_ylabel(T("每个工人的产出（对数）", "log output per worker"))
    _grid(a1)
    _text(a1, 34, P["lny"].iloc[34] + 0.1, T("新路径", "new path"), OUTPUT, va="bottom", ha="right", weight="bold")
    _text(a1, 40, P["lny_old"].iloc[40] - 0.1, T("旧路径", "old path"), MUTED, va="top", weight="bold")
    gap = P["lny"].iloc[-1] - P["lny_old"].iloc[-1]
    _title(a1, T("(a) 新路径最终与旧路径平行", "(a) The new path ends parallel to the old"))
    full = np.log(C.steady(C.S1)[1] / C.steady(C.S0)[1])                      # the gap at the new steady state
    assert 0.9 * full < gap < full and P["lny"].max() < 1.7

    a2.axhline(100 * C.G, color=MUTED, lw=0.8, ls=(0, (1, 2)), zorder=3)
    a2.plot(g.index, g, color=OUTPUT, lw=2.0, zorder=5)
    a2.plot([0], [g.iloc[0]], color=OUTPUT, zorder=6, **DOT)
    a2.set_xlim(0, 60)
    a2.set_ylim(0, 4.6)
    a2.set_xticks([0, 10, 20, 30, 40, 50, 60])
    a2.set_yticks([0, 1, 2, 3, 4])
    a2.set_xlabel(T("储蓄率提高以后的年数", "years after the rise"))
    a2.set_ylabel(T("每个工人的产出增长率（%）", "growth of output per worker (%)"))
    _grid(a2)
    _text(a2, 1.5, g.iloc[0] + 0.05, T(f"当年 {g.iloc[0]:.1f}%", f"first year {g.iloc[0]:.1f}%"), OUTPUT,
          va="bottom", weight="bold")
    _text(a2, 58, 100 * C.G - 0.15, T(f"长期 {100 * C.G:.0f}%", f"long run {100 * C.G:.0f}%"), MUTED, ha="right",
          va="top")
    _title(a2, T("(b) 增长率先接近翻倍，再逐年回落", "(b) Growth doubles, then falls back"))
    assert 3.8 < g.iloc[0] < 4.6 and 0 < g.iloc[-1] - 100 * C.G < 0.1 and g.is_monotonic_decreasing
    return fig


# ---------------------------------------------------------------------------------------------------
@figure("solow_convergence")
def solow_convergence():
    """Penn World Table 10.01, the 111 countries of tab:solow-convergence. (a) Growth of real GDP per head 1960-2019
    against real GDP per head in 1960 (log scale). (b) The same growth net of the investment share and population
    growth (plus the sample mean), with the regression line."""
    P = C.convergence_points()
    R = C.regressions()
    x = np.exp(P["lny0"])
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.9), sharex=True)
    fig.subplots_adjust(left=0.085, right=0.985, top=0.875, bottom=0.19, wspace=0.28)
    fig.text(0.535, 0.015, T("1960 年人均实际 GDP（2017 年美元，对数刻度）", "real GDP per head in 1960 (2017 dollars, log scale)"),
             ha="center", va="bottom", fontsize=plt.rcParams["axes.labelsize"], color=INK)
    grid = np.linspace(P["lny0"].min(), P["lny0"].max(), 50)
    for ax, col, slope in ((a1, "g", R["absolute"]["b"]), (a2, "net", P["slope"].iloc[0])):
        ax.axhline(0, color=MUTED, lw=0.7, zorder=2)
        ax.scatter(x, P[col], s=13, color=tint(OUTPUT, 0.65), edgecolor=OUTPUT, lw=0.5, zorder=5)
        mid = P[col].mean() + slope * (grid - P["lny0"].mean())
        ax.plot(np.exp(grid), mid, color=INK, lw=1.4, zorder=6)
        ax.set_xscale("log")
        ax.set_xlim(250, 40000)
        ax.set_ylim(-2, 6.5)
        ax.set_xticks([300, 1000, 3000, 10000, 30000])
        ax.set_xticklabels(["300", "1,000", "3,000", "10,000", "30,000"])
        ax.minorticks_off()
        ax.set_yticks([-2, 0, 2, 4, 6])
        _grid(ax, "y")
    a1.set_ylabel(T("每年的人均增长率（%）", "growth per head a year (%)"))
    a2.set_ylabel(T("去掉投资与人口的影响（%）", "net of investment and population (%)"))
    names = {"KOR": T("韩国", "Korea"), "CHN": T("中国大陆", "China"), "BWA": T("博茨瓦纳", "Botswana"),
             "VEN": T("委内瑞拉", "Venezuela")}
    for code, name in names.items():
        r = P[P["code"] == code].iloc[0]
        if code == "KOR":                                                        # above its dot, clear of Taiwan's
            _text(a1, np.exp(r["lny0"]), r["g"] + 0.25, name, INK, ha="center", va="bottom")
            continue
        left = code in ("VEN", "BWA", "CHN")
        _text(a1, np.exp(r["lny0"]) * (0.88 if left else 1.13), r["g"], name, INK, ha="right" if left else "left")
    for ax, b in ((a1, R["absolute"]["b"]), (a2, P["slope"].iloc[0])):
        num = f"{b:.2f}".replace("-", "−")
        _text(ax, 38000, 5.9, T(f"斜率 {num}", f"slope {num}"), INK, ha="right")
    _title(a1, T("(a) 1960 年的穷国没有普遍增长更快", "(a) Poor countries did not grow faster"))
    _title(a2, T("(b) 控制投资与人口以后，斜率为负", "(b) With controls, a negative slope"))
    assert x.min() > 250 and x.max() < 40000 and P["g"].between(-2, 6.5).all() and P["net"].between(-2, 6.5).all()
    assert np.isclose(P["slope"].iloc[0], R["conditional"]["b"])
    return fig


# ---------------------------------------------------------------------------------------------------
@figure("solow_soviet")
def solow_soviet():
    """(a) Easterly and Fischer (1995), Table 1, Western data: the growth of output and capital per worker by decade.
    (b) The Joint Economic Committee (1990), Table 2: the growth of GNP, consumption and investment, 1982 factor cost."""
    S = C.soviet()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.9), gridspec_kw=dict(width_ratios=[1, 1.35]))
    fig.subplots_adjust(left=0.075, right=0.99, top=0.875, bottom=0.17, wspace=0.22)
    xs = np.arange(len(S["periods"]))
    w = 0.38
    a1.bar(xs - w / 2, S["y"], w, color=OUTPUT, zorder=4)
    a1.bar(xs + w / 2, S["k"], w, color=INK, zorder=4)
    for i, (y, k) in enumerate(zip(S["y"], S["k"])):
        _text(a1, i - w / 2, y + 0.15, f"{y:.1f}", OUTPUT, ha="center", va="bottom")
        _text(a1, i + w / 2, k + 0.15, f"{k:.1f}", INK, ha="center", va="bottom")
    a1.set_xticks(xs)
    a1.set_xticklabels([p.replace("–", "\n–") for p in S["periods"]])
    a1.set_ylim(0, 9.5)
    a1.set_yticks([0, 2, 4, 6, 8])
    a1.set_ylabel(T("每年的增长率（%）", "growth a year (%)"))
    _grid(a1, "y")
    _text(a1, 3.45, 8.9, T("产出／工人", "output per worker"), OUTPUT, ha="right", weight="bold")
    _text(a1, 3.45, 7.9, T("资本／工人", "capital per worker"), INK, ha="right", weight="bold")
    _title(a1, T("(a) 资本一直比产出长得快", "(a) Capital outgrew output"))

    xs2 = np.arange(len(S["t2"]))
    w2 = 0.27
    for off, vals, col in ((-w2, S["gnp"], OUTPUT), (0, S["cons"], AMBER), (w2, S["inv"], INK)):
        a2.bar(xs2 + off, vals, w2, color=col, zorder=4)
    a2.set_xticks(xs2)
    a2.set_xticklabels([p.replace("–", "\n–") for p in S["t2"]])
    a2.set_ylim(0, 10.5)
    a2.set_yticks([0, 2, 4, 6, 8, 10])
    _grid(a2, "y")
    _text(a2, 5.45, 9.9, T("国民生产总值", "GNP"), OUTPUT, ha="right", weight="bold")
    _text(a2, 5.45, 8.9, T("消费", "consumption"), AMBER, ha="right", weight="bold")
    _text(a2, 5.45, 7.9, T("投资", "investment"), INK, ha="right", weight="bold")
    _text(a2, 0 + w2, S["inv"][0] + 0.15, f"{S['inv'][0]:.1f}", INK, ha="center", va="bottom")
    _title(a2, T("(b) 1975 年以后，投资与消费都放慢", "(b) All three slowed after 1975"))
    assert max(S["k"]) < 8.0 and max(S["inv"]) < 9.8 and S["inv"][0] == max(S["inv"])
    return fig
