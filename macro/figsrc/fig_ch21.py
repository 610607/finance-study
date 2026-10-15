"""Figures for Chapter 21 (工业革命与大分流).

Style as in fig_ch20.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series, the second series in AMBER and dashed with square markers, Western Europe and the United
States in shades of OUTPUT and the Asian economies in shades of AMBER. All numbers come from checks/check_ch21.py,
which reads the snapshots maddison2023_divergence, boe_millennium_england_1270_1913, gpih_allen2011_welfare,
clark2015_england_decadal_1250_1860 and divergence_facts (Broadberry, Guan and Li's Table 8; Broadberry and Gupta's
Tables 1 and 13). div_model is a teaching diagram of eq:divergence-escape with the parameters of
ex:divergence-plateau.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_rgb
from matplotlib.ticker import FixedLocator, NullLocator

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch21 as C  # noqa: E402
from style import (AMBER, FIG_W, INK, LIGHT, MUTED, OUTPUT, PRICE, ZH, T, clean_axes, figure,  # noqa: E402
                   halo, shade_periods, tint)

SQUARE = dict(marker="s", ms=3.4, mfc=AMBER, mec="white", mew=0.4)
DOT = dict(marker="o", ms=4.2, mec="white", mew=0.5)
BLACK_DEATH = [(1348, 1350)]


def _title(ax, s):
    ax.set_title(s, fontsize=9.0, weight="bold", loc="left", pad=4)


def _grid(ax, axis="y"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


def _dashed(ax, x, y, color=AMBER, lw=1.5, **kw):
    line, = ax.plot(x, y, color=color, lw=lw, zorder=3, **kw)
    line.set_dashes((4, 2))
    return line


def _log_ticks(ax, ticks, axis="y", fmt=lambda t: f"{t:,g}"):
    a = ax.yaxis if axis == "y" else ax.xaxis
    a.set_major_locator(FixedLocator(ticks))
    a.set_minor_locator(NullLocator())
    (ax.set_yticklabels if axis == "y" else ax.set_xticklabels)([fmt(t) for t in ticks])


def _minus(s: str) -> str:
    return s.replace("-", "−")


def _spread(ys, gap: float) -> list[float]:
    """Positions for end labels on a log axis: each at least `gap` (in log10) from the next, as near as possible to
    its series."""
    order = sorted(range(len(ys)), key=lambda i: ys[i])
    pos = [math.log10(ys[i]) for i in order]
    for i in range(1, len(pos)):
        pos[i] = max(pos[i], pos[i - 1] + gap)
    shift = (sum(pos) - sum(math.log10(ys[i]) for i in order)) / len(pos)
    pos = [p - shift for p in pos]
    for i in range(1, len(pos)):
        pos[i] = max(pos[i], pos[i - 1] + gap)
    out = [0.0] * len(ys)
    for k, i in enumerate(order):
        out[i] = 10 ** pos[k]
    return out


def _dark(color, k: float):
    """A darker shade for the label of a light line (tint() only lightens)."""
    return tuple((1 - k) * c for c in to_rgb(color))


# Western Europe and the United States in OUTPUT, Asia in AMBER (dashed)
ECONOMY = {"GBR": (OUTPUT, False, 2.0), "NLD": (tint(OUTPUT, 0.45), False, 1.4), "USA": (tint(OUTPUT, 0.7), False, 1.4),
           "CHN": (AMBER, True, 1.7), "JPN": (tint(AMBER, 0.45), True, 1.3), "IND": (tint(AMBER, 0.7), True, 1.3)}


# ---------------------------------------------------------------------------
@figure("div_world")
def div_world():
    """(a) MPD GDP per head of six economies, 1500-1913, log scale; (b) England's population and GDP per head,
    1270 = 100, log scale."""
    G, _ = C.maddison()
    B = C.boe()
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(FIG_W, 4.45), gridspec_kw=dict(height_ratios=[1.25, 1.0]))
    fig.subplots_adjust(left=0.11 if ZH else 0.125, right=0.86 if ZH else 0.79, top=0.95, bottom=0.075, hspace=0.42)

    # (a) six economies
    names = {c: (zh, en) for c, zh, en in C.COUNTRIES}
    ylab = dict(zip(ECONOMY, _spread([G[c][1913] for c in ECONOMY], 0.085)))
    for c, (col, dashed, lw) in ECONOMY.items():
        s = G[c].dropna()
        if dashed:
            _dashed(a1, s.index, s.values, color=col, lw=lw)
        else:
            a1.plot(s.index, s.values, color=col, lw=lw, zorder=4 if c == "GBR" else 3)
        sparse = s.loc[:1819]
        sparse = sparse[sparse.index.to_series().diff().fillna(10) > 1]
        a1.plot(sparse.index, sparse.values, color=col, ls="none", zorder=5, marker="o", ms=2.6, mec="white",
                mew=0.3)
        zh, en = names[c]
        a1.text(1917, ylab[c], T(f"{zh} {s[1913]:,.0f}", f"{en} {s[1913]:,.0f}"), fontsize=7.6,
                color=col if c in ("GBR", "CHN") else _dark(col, 0.3), ha="left", va="center")
    a1.set_yscale("log")
    a1.set_ylim(500, 13000)
    _log_ticks(a1, [500, 1000, 2000, 5000, 10000])
    a1.set_xlim(1500, 1913)
    a1.set_xticks(range(1500, 1901, 100))
    a1.set_ylabel(T("2011 年国际元（对数）", "2011 int. dollars (log)"))
    _grid(a1)
    r1700, r1913 = G.GBR[1700] / G.CHN[1700], G.GBR[1913] / G.CHN[1913]
    _title(a1, T(f"(a) 英国对中国：1700 年 {r1700:.2f} 倍，1913 年 {r1913:.2f} 倍",
                 f"(a) Britain over China: {r1700:.2f}× in 1700, {r1913:.2f}× in 1913"))

    # (b) England
    L = B.pop_england_m.dropna()
    y = B.england_real_gdp_pc_2013gbp
    shade_periods(a2, BLACK_DEATH)
    a2.plot(y.index, 100 * y / y[1270], color=OUTPUT, lw=1.7, zorder=4)
    _dashed(a2, L.index, 100 * L / L[1270])
    a2.text(1560, 215, T("人均实际 GDP", "real GDP per head"), fontsize=7.8, color=OUTPUT, ha="center", va="center")
    a2.text(1480, 68, T("人口", "population"), fontsize=7.8, color=AMBER, ha="center", va="center")
    a2.text(1352, 330, T("黑死病", "Black Death"), fontsize=7.6, color=MUTED, ha="left", va="center")
    a2.set_yscale("log")
    a2.set_ylim(40, 1000)
    _log_ticks(a2, [50, 100, 200, 500, 1000])
    a2.set_xlim(1270, 1913)
    a2.set_xticks([1300, 1400, 1500, 1600, 1700, 1800, 1900])
    a2.set_ylabel(T("1270 年 = 100（对数）", "1270 = 100 (log)"))
    a2.set_xlabel(T("年份", "year"))
    _grid(a2)
    _title(a2, T("(b) 英格兰：1700 年以前此消彼长，以后一起上升",
                 "(b) England: one up, the other down before 1700; both up after"))
    return fig


# ---------------------------------------------------------------------------
@figure("div_model")
def div_model():
    """(a) income relative to the steady state over ten generations, three cases; (b) the phase diagram."""
    a, b, t = C.PLATEAU["alpha"], C.PLATEAU["beta"], C.PLATEAU["tfp"]
    a3, b3, t3 = C.FAST["alpha"], C.FAST["beta"], C.FAST["tfp"]
    g, g3 = C.GEN * t, C.GEN * t3
    bh = b * C.SLOW_POP
    n = C.GENS
    cases = [(a, b, g, OUTPUT, False, T("基准", "baseline")),
             (a, bh, g, AMBER, True, T("β 减半", "β halved")),
             (a3, b3, g3, tint(OUTPUT, 0.5), False, T("α = 0.15，每年 0.8%", "α = 0.15, 0.8% a year"))]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.75), gridspec_kw=dict(width_ratios=[1.15, 1.0]))
    fig.subplots_adjust(left=0.085, right=0.975, top=0.86, bottom=0.17, wspace=0.3)

    # (a) paths
    xs = list(range(n + 1))
    for al, be, gg, col, dashed, name in cases:
        z = C.escape(0, gg, al, be, n)
        y = np.exp(z)
        if dashed:
            _dashed(a1, xs, y, color=col, **SQUARE)
        else:
            a1.plot(xs, y, color=col, lw=2.0 if col == OUTPUT else 1.6, zorder=4, **DOT, mfc=col)
        top = math.exp(C.plateau(gg, al, be))
        a1.axhline(top, color=col, lw=0.7, ls=(0, (1, 2)), zorder=2)
        where = {OUTPUT: (n - 0.2, 1.12, "right", "center"), AMBER: (n - 0.2, top + 0.04, "right", "bottom")}
        x, yy, ha, va = where.get(col, (0.2, top + 0.04, "left", "bottom"))
        a1.text(x, yy, T(f"{name}：平台 {top:.2f}", f"{name}: plateau {top:.2f}"), fontsize=7.6,
                color=col if col in (OUTPUT, AMBER) else _dark(col, 0.3), ha=ha, va=va)
    a1.set_xlim(0, n)
    a1.set_ylim(0.9, 5.4)
    a1.set_xticks(range(0, n + 1, 2))
    a1.set_xlabel(T(f"代（一代 {C.GEN} 年）", f"generation ({C.GEN} years)"))
    a1.set_ylabel(T("人均收入 / 稳态", "income / steady state"))
    _grid(a1)
    _title(a1, T("(a) 技术进步只把收入推上一个平台", "(a) Progress lifts income only to a plateau"))

    # (b) phase diagram
    zz = np.linspace(0, 0.8, 50)
    a2.plot(zz, zz, color=MUTED, lw=0.8, ls=(0, (1, 2)), zorder=2)
    a2.text(0.2, 0.17, "45°", fontsize=7.6, color=MUTED, ha="left", va="top")
    for al, be, gg, col, dashed, name in cases[:2]:
        f = (1 - al * be) * zz + gg
        if dashed:
            _dashed(a2, zz, f, color=col)
        else:
            a2.plot(zz, f, color=col, lw=1.8, zorder=3)
        zs = C.plateau(gg, al, be)
        a2.plot([zs], [zs], color=col, zorder=6, **DOT, mfc=col)
        halo(a2.annotate(T(f"z* = {zs:.1f}", f"z* = {zs:.1f}"), (zs, zs), xytext=(zs + 0.02, zs - 0.13),
                         fontsize=7.6, color=col, ha="left", va="top",
                         arrowprops=dict(arrowstyle="-", color=col, lw=0.6, shrinkB=3)))
    z = C.escape(0, g, a, b, 4)
    for z0, z1 in zip(z[:-1], z[1:]):
        a2.plot([z0, z0, z1], [z0, z1, z1], color=OUTPUT, lw=0.7, zorder=4)
    a2.set_xlim(0, 0.8)
    a2.set_ylim(0, 0.8)
    a2.set_xlabel(T("这一代 $z_t$", "this generation $z_t$"))
    a2.set_ylabel(T("下一代 $z_{t+1}$", "next generation $z_{t+1}$"))
    _grid(a2, "both")
    _title(a2, T("(b) 平台是与 45 度线的交点", "(b) The plateau is on the 45° line"))
    return fig


# ---------------------------------------------------------------------------
@figure("div_wages")
def div_wages():
    """(a) decade means of the welfare ratios of eight cities; (b) Broadberry, Guan and Li's Table 8, log scale."""
    W = C.welfare()
    F = C.facts()
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(FIG_W, 4.45), gridspec_kw=dict(height_ratios=[1.3, 1.0]))
    fig.subplots_adjust(left=0.1 if ZH else 0.12, right=0.83 if ZH else 0.795, top=0.95, bottom=0.075, hspace=0.42)

    # (a) welfare ratios
    china = {"beijing": OUTPUT, "suzhou_shanghai": tint(OUTPUT, 0.35), "canton": tint(OUTPUT, 0.6)}
    other = tint(MUTED, 0.35)
    decades = list(range(1730, 1911, 10))
    ends = {}
    a1.set_yscale("log")
    for c, zh, en in C.CITIES:
        s = W[c]
        xs, ys = [], []
        for d in decades:
            v = s.loc[d:d + 9].dropna()
            if len(v):
                xs.append(d + 5 if d < 1910 else 1912)
                ys.append(float(v.mean()))
        col = china.get(c, other)
        a1.plot(xs, ys, color=col, lw=1.9 if c in china else 1.1, zorder=4 if c in china else 3)
        ends[c] = (xs[-1], ys[-1], col, zh, en)
    ylab = dict(zip(ends, _spread([v[1] for v in ends.values()], 0.09)))
    for c, (x, y, col, zh, en) in ends.items():
        lab = col if c in china else _dark(MUTED, 0.1)
        a1.text(1917, ylab[c], T(zh, en), fontsize=7.6, color=lab, ha="left", va="center")
    a1.axhline(1, color=MUTED, lw=0.7, ls=(0, (1, 2)), zorder=2)
    a1.text(1912, 0.47, T("1 = 仅够糊口", "1 = bare subsistence"), fontsize=7.6, color=MUTED, ha="right",
            va="bottom")
    a1.set_xlim(1730, 1915)
    a1.set_ylim(0.45, 9.5)
    _log_ticks(a1, [0.5, 1, 2, 4, 8])
    a1.set_ylabel(T("福利比率", "welfare ratio"))
    _grid(a1)
    m = {c: C.decade_mean(W[c], a, b) for c, a, b in (("london", 1750, 1759), ("beijing", 1750, 1759))}
    l13, b13 = C.decade_mean(W.london, 1900, 1913), C.decade_mean(W.beijing, 1900, 1913)
    _title(a1, T(f"(a) 伦敦对北京：1750 年代 {m['london'] / m['beijing']:.1f} 倍，1900—1913 年 {l13 / b13:.1f} 倍",
                 f"(a) London over Beijing: {m['london'] / m['beijing']:.1f}× in the 1750s, {l13 / b13:.1f}× in 1900–13"))

    # (b) Table 8
    yrs = [1600, 1700, 1750, 1800, 1850]
    t8 = np.array([F[f"bgl_t8_{y}"][1:] for y in yrs])
    econ = [(T("英国", "Britain"), OUTPUT, False, 2.0), (T("荷兰", "Netherlands"), tint(OUTPUT, 0.45), False, 1.4),
            (T("意大利", "Italy"), tint(OUTPUT, 0.7), False, 1.3), (T("日本", "Japan"), tint(AMBER, 0.45), True, 1.3),
            (T("中国", "China"), AMBER, True, 1.7), (T("印度", "India"), tint(AMBER, 0.7), True, 1.3)]
    yo = _spread(list(t8[-1]), 0.075)
    for j, (name, col, dashed, lw) in enumerate(econ):
        if dashed:
            _dashed(a2, yrs, t8[:, j], color=col, lw=lw, marker="s", ms=3.2, mfc=col, mec="white", mew=0.4)
        else:
            a2.plot(yrs, t8[:, j], color=col, lw=lw, zorder=4, marker="o", ms=3.4, mfc=col, mec="white", mew=0.4)
        lab = col if j in (0, 4) else _dark(col, 0.3)
        a2.text(1856, yo[j], f"{name} {t8[-1, j]:,.0f}", fontsize=7.6, color=lab, ha="left", va="center")
    a2.set_yscale("log")
    a2.set_ylim(450, 3600)
    _log_ticks(a2, [500, 1000, 2000, 3000])
    a2.set_xlim(1600, 1850)
    a2.set_xticks(yrs)
    a2.set_ylabel(T("1990 年国际元（对数）", "1990 int. dollars (log)"))
    a2.set_xlabel(T("年份", "year"))
    _grid(a2)
    _title(a2, T(f"(b) 1600 年英国是中国的 {t8[0, 0] / t8[0, 4]:.1f} 倍，1850 年 {t8[-1, 0] / t8[-1, 4]:.1f} 倍",
                 f"(b) Britain over China: {t8[0, 0] / t8[0, 4]:.1f}× in 1600, {t8[-1, 0] / t8[-1, 4]:.1f}× in 1850"))
    return fig


# ---------------------------------------------------------------------------
@figure("div_cotton")
def div_cotton():
    """(a) Table 1: raw cotton consumption by decade, log scale; (b) Table 13, India = 100, log scale."""
    F = C.facts()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.9), gridspec_kw=dict(width_ratios=[1.0, 1.1]))
    fig.subplots_adjust(left=0.1, right=0.835 if ZH else 0.8, top=0.86, bottom=0.15, wspace=0.32)

    # (a) Table 1
    t1 = {}
    for k, v in F.items():
        if k.startswith("bg_t1_"):
            t1[v[0]], t1[v[3]] = v[2], v[5]
    xs = sorted(t1)
    mid = [1698 if x == 1697 else x + 5 for x in xs]
    a1.plot(mid, [t1[x] for x in xs], color=OUTPUT, lw=2.0, zorder=4, **DOT, mfc=OUTPUT)
    for x, dy, ha in ((1697, 1.35, "left"), (1770, 1.4, "right"), (1840, 1.32, "right")):
        v = t1[x]
        a1.text((1698 if x == 1697 else x + 5) + (-2 if ha == "right" else 1), v * dy, f"{v:g}", fontsize=7.6,
                color=OUTPUT, ha=ha, va="center")
    a1.set_yscale("log")
    a1.set_ylim(0.7, 900)
    _log_ticks(a1, [1, 10, 100, 500])
    a1.set_xlim(1690, 1850)
    a1.set_xticks([1700, 1750, 1800, 1850])
    a1.set_ylabel(T("百万磅 / 年（对数）", "million lb a year (log)"))
    _grid(a1)
    _title(a1, T(f"(a) 原棉消费：{t1[1840] / t1[1697]:.0f} 倍", f"(a) Raw cotton: {t1[1840] / t1[1697]:.0f}-fold"))

    # (b) Table 13
    yrs = [1680, 1770, 1790, 1820]
    t13 = np.array([F[f"bg_t13_{y}"][1:] for y in yrs])
    series = [(0, T("工资", "wages"), PRICE, False, 1.8), (1, T("原棉价格", "raw cotton"), AMBER, True, 1.5),
              (2, T("加权成本", "combined cost"), tint(PRICE, 0.5), False, 1.2),
              (3, T("离岸价格", "FOB price"), tint(AMBER, 0.5), True, 1.2),
              (4, T("全要素生产率", "TFP"), OUTPUT, False, 2.0)]
    yo = _spread(list(t13[-1]), 0.085)
    for j, name, col, dashed, lw in series:
        if dashed:
            _dashed(a2, yrs, t13[:, j], color=col, lw=lw, marker="s", ms=3.2, mfc=col, mec="white", mew=0.4)
        else:
            a2.plot(yrs, t13[:, j], color=col, lw=lw, zorder=4, marker="o", ms=3.4, mfc=col, mec="white", mew=0.4)
        lab = col if j not in (2, 3) else _dark(col, 0.4)
        a2.text(1826, yo[j], f"{name} {t13[-1, j]:g}", fontsize=7.6, color=lab, ha="left", va="center")
    a2.axhline(100, color=MUTED, lw=0.8, ls=(0, (3, 2)), zorder=2)
    a2.text(1683, 104, T("印度 = 100", "India = 100"), fontsize=7.6, color=MUTED, ha="left", va="bottom")
    a2.set_yscale("log")
    a2.set_ylim(30, 900)
    _log_ticks(a2, [50, 100, 200, 500])
    a2.set_xlim(1675, 1822)
    a2.set_xticks(yrs)
    a2.set_xticklabels([T(f"约 {y}", f"c. {y}") if y in (1680, 1820) else str(y) for y in yrs], fontsize=7.8)
    a2.set_ylabel(T("印度 = 100（对数）", "India = 100 (log)"))
    _grid(a2)
    _title(a2, T(f"(b) 1820 年：工资 {t13[-1, 0] / 100:.1f} 倍，全要素生产率 {t13[-1, 4] / 100:.1f} 倍",
                 f"(b) 1820: wages {t13[-1, 0] / 100:.1f}×, TFP {t13[-1, 4] / 100:.1f}×"))
    return fig


# ---------------------------------------------------------------------------
@figure("div_england")
def div_england():
    """(a) ln real NNI per head against ln population by decade, three periods, with the 1250-1630 fit;
    (b) Clark's real NNI per head and Broadberry et al.'s real GDP per head by decade."""
    Cl = C.clark()
    B = C.boe()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 3.0), gridspec_kw=dict(width_ratios=[1.1, 1.0]))
    fig.subplots_adjust(left=0.09, right=0.975, top=0.86, bottom=0.15, wspace=0.3)

    # (a) the frontier
    groups = [((1250, 1630), OUTPUT, "o", T("1250—1630", "1250–1630")),
              ((1640, 1790), AMBER, "s", T("1640—1790", "1640–1790")),
              ((1800, 1860), tint(OUTPUT, 0.5), "D", T("1800—1860", "1800–1860"))]
    for (a, b), col, mk, name in groups:
        s = Cl.loc[a:b]
        a1.plot(s.pop_england_m, s.real_nni_pc_1860s_100, color=col, ls="none", marker=mk, ms=4.0, mec="white",
                mew=0.4, zorder=4)
    f = C.frontier(Cl, 1250, 1630)
    s = Cl.loc[1250:1630]
    xx = np.linspace(s.pop_england_m.min(), s.pop_england_m.max(), 20)
    a1.plot(xx, np.exp(f.params.Intercept + f.params.lL * np.log(xx)), color=OUTPUT, lw=1.2, zorder=3)
    a1.text(2.0, 100, T("1250—1630", "1250–1630"), fontsize=7.6, color=OUTPUT, ha="left", va="center")
    a1.text(3.25, 40.5, _minus(T(f"斜率 {f.params.lL:.2f}", f"slope {f.params.lL:.2f}")), fontsize=7.6,
            color=OUTPUT, ha="left", va="center")
    a1.text(4.3, 72, T("1640—1790", "1640–1790"), fontsize=7.6, color=AMBER, ha="left", va="center")
    a1.text(9.2, 95, T("1800—1860", "1800–1860"), fontsize=7.6, color=_dark(tint(OUTPUT, 0.5), 0.3), ha="right",
            va="center")
    a1.set_xscale("log")
    a1.set_yscale("log")
    a1.set_xlim(1.9, 22)
    a1.set_ylim(36, 112)
    _log_ticks(a1, [2, 3, 5, 10, 20], axis="x")
    _log_ticks(a1, [40, 50, 60, 80, 100])
    a1.set_xlabel(T("人口（百万，对数）", "population (millions, log)"))
    a1.set_ylabel(T("人均实际国民净收入（对数）", "real NNI per head (log)"))
    _grid(a1, "both")
    _title(a1, T("(a) 人多则穷，1640 年以后不再如此", "(a) More people, poorer, until 1640"))

    # (b) two estimates
    bd = C.boe_decades(B)
    cd = Cl.real_nni_pc_1860s_100
    a2.plot(cd.index + 5, cd.values, color=OUTPUT, lw=1.9, zorder=4)
    _dashed(a2, bd.index + 5, bd.values)
    a2.text(1560, 82, "Clark", fontsize=7.8, color=OUTPUT, ha="left", va="center")
    a2.text(1520, 24, T("Broadberry 等", "Broadberry et al."), fontsize=7.8, color=AMBER, ha="left", va="center")
    for d in (1450,):
        for v, col, dy in ((cd[d], OUTPUT, 1.08), (bd[d], AMBER, 0.86)):
            a2.text(d + 5, v * dy, f"{v:.0f}", fontsize=7.6, color=col, ha="center", va="center")
    a2.set_yscale("log")
    a2.set_ylim(18, 130)
    _log_ticks(a2, [20, 30, 50, 100])
    a2.set_xlim(1250, 1870)
    a2.set_xticks([1300, 1450, 1600, 1750])
    a2.set_ylabel(T("1860 年代约为 100（对数）", "1860s ≈ 100 (log)"))
    _grid(a2)
    _title(a2, T("(b) 两套估计在 1700 年以前分开", "(b) The estimates part before 1700"))
    return fig
