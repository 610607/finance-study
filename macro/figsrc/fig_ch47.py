"""Figures for Chapter 47 (石油危机与滞胀).

Style as in fig_ch46.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the colour
of their series, no legends. Prices and inflation are PRICE (the second series of a panel AMBER, dashed, with squares),
the two policies of the teaching example MONEY and AMBER, growth across countries OUTPUT, reference lines MUTED, the
shocks of 1973-1974 and 1979-1980 shaded with shade_periods(). All numbers come from checks/check_ch47.py: the World
Bank's crude-oil price (crude()), the World Development Indicators and Penn World Table (cpi(), growth(),
regression(), fit_line()) and the paths of the teaching example ex:oil-paths (paths(), EX). The Chinese labels of the
World Bank's and PWT's series are the book's translation.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch47 as C
from style import (
    AMBER,
    FIG_W,
    INK,
    LIGHT,
    MONEY,
    MUTED,
    OUTPUT,
    PRICE,
    T,
    clean_axes,
    figure,
    halo,
    shade_periods,
)

DOT = dict(marker="o", ms=4.6, mec="white", mew=0.6)
SQUARE = dict(marker="s", ms=4.4, mec="white", mew=0.6)
DASH = dict(dashes=(4, 2))


def _title(ax, s):
    ax.set_title(s, fontsize=9.0, weight="bold", loc="left", pad=4)


def _grid(ax, axis="both"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


def _text(ax, x, y, s, color, ha="left", va="center", weight="normal", size=7.8):
    lab = ax.text(x, y, s, color=color, fontsize=size, ha=ha, va=va, weight=weight, linespacing=1.3, zorder=8)
    halo(lab, 2.0)
    return lab


def _shocks(ax):
    shade_periods(ax, [(a - 0.5, b + 0.5) for a, b in C.SHOCKS])


# ---------------------------------------------------------------------------------------------------
@figure("oil_price")
def oil_price():
    """The World Bank's annual crude-oil price (the average of Brent, Dubai and WTI), nominal and in 2010 dollars, a
    barrel, 1960-2025, on a log scale; the shocks shaded; the real price of 1973, 1974, 1978, 1980, 1998 and 2008
    marked with its value."""
    P = C.crude()
    yrs = P.index.values
    nom, real = P["crude_nominal"].values, P["crude_real"].values
    fig, ax = plt.subplots(figsize=(FIG_W, 2.75))
    fig.subplots_adjust(left=0.10, right=0.985, top=0.97, bottom=0.12)
    _grid(ax, "y")
    _shocks(ax)
    ax.set_yscale("log")
    ax.plot(yrs, nom, color=PRICE, lw=2.0, zorder=4)
    ax.plot(yrs, real, color=AMBER, lw=2.0, zorder=4, **DASH)
    marks = (1973, 1974, 1978, 1980, 1998, 2008)
    ax.plot(marks, [C.real(y) for y in marks], ls="none", color=AMBER, zorder=5, **SQUARE)
    ax.plot((1973, 1974, 1980), [C.nominal(y) for y in (1973, 1974, 1980)], ls="none", color=PRICE, zorder=5, **DOT)
    for y, dx, dy, ha in ((1973, -0.7, 1.0, "right"), (1974, -0.6, 1.22, "right"), (1978, 0.4, 0.80, "left"),
                          (1980, 0.8, 1.10, "left"), (1998, 0.0, 0.76, "center"), (2008, 0.0, 1.17, "center")):
        _text(ax, y + dx, C.real(y) * dy, f"{C.real(y):.1f}", AMBER, ha=ha, va="center" if dx else "bottom" if dy > 1
              else "top", weight="bold")
    _text(ax, 1974 + 0.8, C.nominal(1974) * 0.86, f"{C.nominal(1974):.1f}", PRICE, va="top", weight="bold")
    _text(ax, 1973 + 0.6, C.nominal(1973) * 0.80, f"{C.nominal(1973):.1f}", PRICE, va="top", weight="bold")
    _text(ax, 1984, 80, T("实际价格（2010 年美元）", "real (2010 dollars)"), AMBER, weight="bold")
    _text(ax, 1961, 1.05, T("名义价格", "nominal"), PRICE, weight="bold", va="top")
    ticks = [1, 2, 5, 10, 20, 50, 100]
    ax.set_ylim(0.75, 160)
    ax.yaxis.set_major_locator(mticker.FixedLocator(ticks))
    ax.yaxis.set_major_formatter(mticker.FixedFormatter([str(v) for v in ticks]))
    ax.yaxis.set_minor_locator(mticker.NullLocator())
    ax.set_ylabel(T("美元／桶（对数刻度）", "dollars a barrel (log scale)"))
    ax.set_xlim(1959, 2026)
    ax.set_xticks(range(1960, 2030, 10))
    return fig


@figure("oil_paths")
def oil_paths():
    """ex:oil-paths (C.paths with C.EX): inflation (a) and unemployment (b), years 0-12, not accommodating (nominal
    demand growing by x) and accommodating (unemployment held at the natural rate)."""
    E = C.EX
    N = 12
    P, A = C.paths(N), C.paths(N, accommodate=True)
    t = np.arange(N + 1)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.6), sharex=True)
    fig.subplots_adjust(left=0.075, right=0.99, top=0.88, bottom=0.16, wspace=0.22)
    for ax, key, ref in ((a1, "pi", E["pi0"]), (a2, "u", E["un"])):
        _grid(ax, "y")
        ax.axvline(1, color=MUTED, lw=0.8, ls=(0, (3, 2)), zorder=2)
        ax.axhline(ref, color=MUTED, lw=0.7, ls=":", zorder=2)
        ax.plot(t, P[key], color=MONEY, lw=2.0, zorder=4, marker="o", ms=4.4, mec="white", mew=0.6)
        ax.plot(t, A[key], color=AMBER, lw=2.0, zorder=3, marker="s", ms=4.2, mec="white", mew=0.6, **DASH)
        ax.set_xlim(-0.4, N + 0.4)
        ax.set_xticks(range(0, N + 1, 2))
        ax.set_xlabel(T("年", "year"))
    assert np.isclose(P["pi"][1], 7.2) and np.isclose(P["u"][1], 7.6) and np.isclose(A["pi"][-1], 8)
    k = int(np.argmax(P["u"]))
    _text(a1, 1.35, P["pi"][1] + 0.05, f"{P['pi'][1]:.1f}", MONEY, weight="bold")
    _text(a1, 12, A["pi"][-1] + 0.45, T("迁就：停在 8%", "accommodate: stays at 8%"), AMBER, ha="right", va="bottom",
          weight="bold")
    _text(a1, 6.5, 1.75, T("不迁就：回落", "do not accommodate: falls back"), MONEY, ha="center", va="top", weight="bold")
    a1.set_ylim(1, 10)
    a1.set_yticks([2, 4, 6, 8, 10])
    a1.set_ylabel("%")
    _title(a1, T("(a) 通胀：冲击过后回落或停在高处", "(a) Inflation: falls back, or stays up"))
    _text(a2, k + 0.35, P["u"][k] + 0.1, f"{P['u'][k]:.1f}", MONEY, weight="bold", va="bottom")
    _text(a2, 1.35, P["u"][1] - 0.05, f"{P['u'][1]:.1f}", MONEY, weight="bold", va="top")
    _text(a2, 12, E["un"] - 0.25, T("迁就：守在 6%", "accommodate: 6%"), AMBER, ha="right", va="top", weight="bold")
    _text(a2, 12, 5.9 + 1.25, T("不迁就：上升\n后摆回", "do not accommodate:\nrises, swings back"), MONEY, ha="right",
          va="bottom", weight="bold")
    a2.set_ylim(4, 9.8)
    a2.set_yticks([4, 6, 8])
    _title(a2, T(f"(b) 失业：第 {k} 年最高", f"(b) Unemployment: highest in year {k}"))
    return fig


@figure("oil_g7")
def oil_g7():
    """Consumer-price inflation (WDI) and the growth of real GDP at constant national prices (PWT 10.01, rgdpna) of
    the G7 and Switzerland, 1970-1985, one panel each; the shocks shaded."""
    names = {"USA": T("美国", "United States"), "JPN": T("日本", "Japan"), "DEU": T("联邦德国", "West Germany"),
             "FRA": T("法国", "France"), "GBR": T("英国", "United Kingdom"), "ITA": T("意大利", "Italy"),
             "CAN": T("加拿大", "Canada"), "CHE": T("瑞士", "Switzerland")}
    order = ("USA", "JPN", "DEU", "CHE", "GBR", "ITA", "FRA", "CAN")
    assert set(order) == set(C.G8)
    yrs = np.arange(C.SPAN[0], C.SPAN[1] + 1)
    fig, axes = plt.subplots(2, 4, figsize=(FIG_W, 3.7), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.085, right=0.99, top=0.93, bottom=0.08, hspace=0.30, wspace=0.10)
    lo = min(C.growth(c, y) for c in C.G8 for y in yrs)
    hi = max(C.cpi(c, y) for c in C.G8 for y in yrs)
    assert -8 < lo and hi < 25
    for ax, c in zip(axes.flat, order):
        _grid(ax, "y")
        _shocks(ax)
        ax.axhline(0, color=MUTED, lw=0.7, zorder=2)
        p = [C.cpi(c, y) for y in yrs]
        g = [C.growth(c, y) for y in yrs]
        ax.plot(yrs, p, color=PRICE, lw=1.6, zorder=4)
        ax.plot(yrs, g, color=AMBER, lw=1.4, zorder=4, **DASH)
        i = int(np.argmax(p))
        ax.plot(yrs[i], p[i], ls="none", color=PRICE, zorder=5, **DOT)
        _text(ax, yrs[i] + (0.6 if yrs[i] < 1980 else -0.6), p[i] + 0.4, f"{p[i]:.1f}", PRICE, weight="bold",
              ha="left" if yrs[i] < 1980 else "right", va="bottom", size=7.6)
        j = int(np.argmin(g))
        ax.plot(yrs[j], g[j], ls="none", color=AMBER, zorder=5, **SQUARE)
        low = g[j] < -5                                                          # beside the point, not below it
        _text(ax, yrs[j] + (0.7 if low else 0.6), g[j] + (0.0 if low else -0.3), f"{g[j]:.1f}".replace("-", "−"), AMBER,
              weight="bold", va="center" if low else "top", size=7.6)
        ax.set_title(names[c], fontsize=9.0, weight="bold", loc="left", pad=3)
        ax.set_ylim(-10, 29)
        ax.set_yticks([-5, 0, 5, 10, 15, 20, 25])
        ax.set_xlim(1969, 1986)
        ax.set_xticks([1970, 1975, 1980, 1985])
        ax.set_xticklabels(["70", "75", "80", "85"])
    _text(axes[0, 0], 1985.6, 26.5, T("消费物价", "consumer prices"), PRICE, ha="right", va="top", weight="bold",
          size=7.6)
    _text(axes[0, 0], 1969.4, -8.8, T("实际 GDP", "real GDP"), AMBER, ha="left", va="bottom", weight="bold",
          size=7.6)
    for ax in axes[:, 0]:
        ax.set_ylabel("%")
    return fig


@figure("oil_curse")
def oil_curse():
    """Total natural-resource rents (% of GDP) at the start and the log growth of real GDP per head afterwards, per
    cent a year: (a) 1970-1990, (b) 1990-2019; the Gulf states as triangles; the regression line (rents and the log of
    income per head at the start) at the mean log income of the start."""
    fig, axes = plt.subplots(1, 2, figsize=(FIG_W, 2.9), sharey=True)
    fig.subplots_adjust(left=0.085, right=0.975, top=0.88, bottom=0.16, wspace=0.08)
    for ax, (a, b), xmax in zip(axes, C.PERIODS, (50, 80)):
        R = C.regression(a, b)
        gulf = np.array([c in C.GULF for c in R["codes"]])
        _grid(ax)
        ax.axhline(0, color=MUTED, lw=0.7, zorder=2)
        ax.plot(R["x"][~gulf], R["y"][~gulf], ls="none", marker="o", ms=3.6, color=OUTPUT, alpha=0.75, mec="white",
                mew=0.4, zorder=3)
        ax.plot(R["x"][gulf], R["y"][gulf], ls="none", marker="^", ms=5.4, color=AMBER, mec="white", mew=0.5,
                zorder=4)
        xs = np.array([0.0, xmax])
        ax.plot(xs, C.fit_line(a, b, xs), color=INK, lw=1.4, zorder=5)
        for c, dx, dy, ha in (("ZMB", 1.0, 0.0, "left"), ("SAU", 0.6, -0.75, "left"), ("MYS", 1.0, 0.0, "left"),
                              ("BWA", 1.0, 0.0, "left"), ("NOR", 0.8, -0.85 if a == 1990 else 0.0, "left")):
            if c in R["codes"] and (a == 1970 or c == "NOR"):
                i = R["codes"].index(c)
                name = {"ZMB": T("赞比亚", "Zambia"), "SAU": T("沙特", "Saudi"), "MYS": T("马来西亚", "Malaysia"),
                        "BWA": T("博茨瓦纳", "Botswana"), "NOR": T("挪威", "Norway")}[c]
                _text(ax, R["x"][i] + dx, R["y"][i] + dy, name, INK, ha=ha, size=7.6)
        bs = f"{R['b']:.2f}".replace("-", "−")
        _text(ax, xmax * 0.97, 8.9, T(f"{R['n']} 个经济体\n斜率 {bs}，t = {R['t']:.1f}".replace("-", "−"),
                                     f"{R['n']} economies\nslope {bs}, t = {R['t']:.1f}".replace("-", "−")),
              INK, ha="right", va="top", size=7.6)
        ax.set_xlim(-2, xmax)
        ax.set_xlabel(T(f"{a} 年的租金（占 GDP 的 %）", f"rents in {a} (% of GDP)"))
    assert max(R_["y"].max() for R_ in (C.regression(*C.PERIODS[0]), C.regression(*C.PERIODS[1]))) < 9.5
    assert min(R_["y"].min() for R_ in (C.regression(*C.PERIODS[0]), C.regression(*C.PERIODS[1]))) > -8
    axes[0].set_ylim(-8.5, 9.8)
    axes[0].set_yticks(range(-6, 10, 3))
    axes[0].set_ylabel(T("人均增长（%／年）", "growth per head (% a year)"))
    _title(axes[0], T("(a) 1970—1990 年：租金高，增长慢", "(a) 1970-1990: high rents, slow growth"))
    _title(axes[1], T("(b) 1990—2019 年：关系弱得多", "(b) 1990-2019: a much weaker link"))
    _text(axes[1], 78, -6.2, T("三角：海湾国家", "triangles: the Gulf"), AMBER, ha="right", weight="bold", size=7.6)
    return fig
