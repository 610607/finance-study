"""Figures for Chapter 11 (中世纪欧洲：庄园、黑死病与货币贬值).

Style as in fig_ch12.py (docs/STYLE.md §7.1): bold "(a) …" panel titles that state the point, direct
labels in the colour of their series, a second series in AMBER and dashed.  All numbers come from
checks/check_ch11.py, which reads the snapshots clark2015_england_decadal, boe_millennium_pop_england,
wailly1857_livre_tournois and medieval_europe_facts.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch11 as C  # noqa: E402
from style import (AMBER, CASE, FIG_W, INK, LIGHT, MONEY, MUTED, OUTPUT, PRICE, T,  # noqa: E402
                   clean_axes, figure, tint)


def _title(ax, s):
    ax.set_title(s, fontsize=8.8, weight="bold", loc="left", pad=4)


def _grid(ax):
    clean_axes(ax)
    ax.grid(True, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


# ---------------------------------------------------------------------------
@figure("malthus_dynamics")
def malthus_dynamics():
    """Ashraf-Galor dynamics after a one-time fall of population (eq:medieval-dynamics)."""
    a = C.ALPHA
    pop = C.clark()["pop_england_m"]
    l0 = pop[1400] / pop.loc[1300:1340].mean()        # Clark: 1400s against 1300-49
    T_ = 7
    ell = [l0]
    for _ in range(T_):
        ell.append(float(C.labour_map(np.array(ell[-1]), a)))
    ell = np.array(ell)
    x = ell ** (-a)                                   # income per person relative to the steady state

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.9), gridspec_kw=dict(width_ratios=[1, 1.15]))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.89, bottom=0.17, wspace=0.3)

    g = np.linspace(0, 1.35, 200)
    a1.plot(g, g, color=MUTED, lw=0.8, ls=(0, (1.5, 2)))
    a1.text(1.20, 1.27, "45°", fontsize=7.6, color=MUTED, ha="right", va="center")
    a1.plot(g, C.labour_map(g, a), color=OUTPUT, lw=2.0)
    a1.text(0.05, 1.30, T("下一代的人口\n$L_{t+1}=\\varphi(L_t)$", "next generation\n$L_{t+1}=\\varphi(L_t)$"),
            fontsize=7.6, color=OUTPUT, ha="left", va="top", linespacing=1.3)
    # staircase from the post-plague level back to the steady state
    xs, ys = [ell[0]], [ell[0]]
    for k in range(4):
        xs += [ell[k], ell[k + 1]]
        ys += [ell[k + 1], ell[k + 1]]
    a1.plot(xs, ys, color=AMBER, lw=1.2, ls=(0, (4, 2)))
    a1.plot([ell[0]], [ell[0]], "s", color=AMBER, ms=5)
    a1.plot([1], [1], "o", color=OUTPUT, ms=5.5)
    a1.annotate(T(f"瘟疫后：{l0:.2f}", f"after the plague: {l0:.2f}"), xy=(ell[0], ell[0]), xytext=(0.62, 0.30),
                fontsize=7.6, color=AMBER, ha="left", va="center", arrowprops=dict(arrowstyle="-", color=AMBER, lw=0.6))
    a1.annotate(T("稳态 $\\bar L$", "steady\nstate $\\bar L$"), xy=(1, 1), xytext=(1.05, 0.72), fontsize=7.6,
                color=OUTPUT, ha="left", arrowprops=dict(arrowstyle="-", color=OUTPUT, lw=0.6))
    a1.set_xlim(0, 1.35)
    a1.set_ylim(0, 1.35)
    a1.set_xlabel(T("这一代的人口 $L_t/\\bar L$", "population this generation, $L_t/\\bar L$"))
    a1.set_ylabel(T("下一代的人口 $L_{t+1}/\\bar L$", "next generation, $L_{t+1}/\\bar L$"))
    _title(a1, T("(a) 人口回到原来的稳态", "(a) population returns to its steady state"))

    gen = np.arange(-2, T_ + 1)
    yy = np.concatenate([[1, 1], x])
    ll = np.concatenate([[1, 1], ell])
    a2.axhline(1, color=MUTED, lw=0.6, ls=(0, (1, 2)))
    a2.plot(gen, 100 * yy, "-o", color=OUTPUT, lw=2.0, ms=5)
    a2.plot(gen, 100 * ll, "-s", color=AMBER, lw=1.8, ms=4.5, dashes=(4, 2))
    a2.text(-0.6, 128, T(f"人均收入\n+{100 * (x[0] - 1):.0f}%", f"income\nper head\n+{100 * (x[0] - 1):.0f}%"),
            fontsize=7.8, color=OUTPUT, ha="right", va="center", linespacing=1.25)
    a2.text(1.25, 100 * ell[1] - 3, T("人口", "population"), fontsize=7.8, color=AMBER, ha="left", va="top")
    hl = C.half_life(a)
    a2.text(T_ + 0.3, 138, T(f"$\\alpha={a:.3f}$：每过一代，\n偏离只剩上一代的 $(1-\\alpha)$ 次方；\n约 {hl:.1f} 代后收入的增幅减半",
                            f"$\\alpha={a:.3f}$: each generation\nthe gap shrinks to its\n$(1-\\alpha)$ power; half gone\nin about {hl:.1f} generations"),
            fontsize=7.6, color=INK, ha="right", va="top", linespacing=1.3)
    a2.set_xlim(-2.4, T_ + 0.4)
    a2.set_ylim(45, 140)
    a2.set_xticks(range(-2, T_ + 1))
    a2.set_xlabel(T("代（0 = 瘟疫之后的第一代）", "generation (0 = first after the plague)"))
    a2.set_ylabel(T("稳态 = 100", "steady state = 100"))
    _title(a2, T("(b) 人均收入先跳升，再逐代回落", "(b) income jumps, then falls back"))
    for ax in (a1, a2):
        _grid(ax)
    return fig


# ---------------------------------------------------------------------------
@figure("plague_wages")
def plague_wages():
    """Population, real wages and real rents in England, 1250-1500, against the model's prediction."""
    d = C.clark()
    B = C.broadberry()
    dec = d.index.to_numpy() + 5                      # plot decades at their midpoints
    pop_i = C.clark_index("pop_england_m")
    blab, farm = C.clark_index("real_blab_1860s_100"), C.clark_index("real_farm_1860s_100")
    rent = C.clark_index("real_rent")
    w_m, s_m = C.factor_prices(pop_i.to_numpy())

    fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(FIG_W, 2.75))
    fig.subplots_adjust(left=0.07, right=0.99, top=0.88, bottom=0.17, wspace=0.36)
    for ax in (a1, a2, a3):
        ax.axvspan(1348, 1350, color=tint(PRICE, 0.18), lw=0, zorder=0)

    a1.plot(B.index, B.values, "-", color=OUTPUT, lw=2.0)
    a1.plot(dec, d["pop_england_m"], "s", color=AMBER, ms=3.6, ls=(0, (4, 2)), lw=1.2)
    a1.text(1395, 3.25, "Broadberry\n" + T("等", "et al."), fontsize=7.6, color=OUTPUT, ha="left", va="bottom",
            linespacing=1.2)
    a1.text(1430, 2.62, "Clark", fontsize=7.6, color=AMBER, ha="left", va="bottom")
    a1.text(1352, 5.55, T("1348—1349", "1348–49"), fontsize=7.6, color=PRICE, ha="left")
    a1.set_ylim(1.5, 6.0)
    a1.set_ylabel(T("百万人", "millions"))
    _title(a1, T("(a) 英格兰人口", "(a) population of England"))

    a2.axhline(1, color=MUTED, lw=0.6, ls=(0, (1, 2)))
    a2.plot(dec, blab, "-o", color=OUTPUT, lw=2.0, ms=3.6)
    a2.plot(dec, farm, "-", color=tint(OUTPUT, 0.45), lw=1.3)
    a2.plot(dec, w_m, color=AMBER, lw=1.6, dashes=(4, 2))
    a2.text(1395, 2.45, T("农工", "farm"), fontsize=7.6, color=tint(OUTPUT, 0.45), ha="right", va="bottom")
    a2.text(1500, 1.75, T("建筑小工", "building\nlabourer"), fontsize=7.6, color=OUTPUT, ha="right", va="top",
            linespacing=1.15)
    a2.text(1500, 1.27, T("模型", "model"), fontsize=7.6, color=AMBER, ha="right", va="top")
    a2.set_ylim(0.6, 2.8)
    a2.set_ylabel(T("1300—1349 年 = 1", "1300–49 = 1"))
    _title(a2, T("(b) 实际工资涨得比模型多", "(b) wages rose more"))

    a3.axhline(1, color=MUTED, lw=0.6, ls=(0, (1, 2)))
    a3.plot(dec, rent, "-o", color=OUTPUT, lw=2.0, ms=3.6)
    a3.plot(dec, s_m, color=AMBER, lw=1.6, dashes=(4, 2))
    a3.text(1500, 1.03, T("实际地租", "real rent"), fontsize=7.6, color=OUTPUT, ha="right", va="bottom")
    a3.text(1440, 0.62, T("模型", "model"), fontsize=7.6, color=AMBER, ha="right", va="top")
    a3.set_ylim(0.4, 1.4)
    _title(a3, T("(c) 地租跌得比模型少", "(c) rents fell less"))
    for ax in (a1, a2, a3):
        _grid(ax)
        ax.set_xlim(1250, 1505)
        ax.set_xticks([1250, 1350, 1450])
        ax.tick_params(labelsize=8.0)
    return fig


# ---------------------------------------------------------------------------
@figure("wage_ceiling")
def wage_ceiling():
    """(a) a ceiling at the old wage after the labour force shrinks; (b) day wages and the 1351 caps."""
    a = C.ALPHA
    pop = C.clark()["pop_england_m"]
    l1 = pop[1350] / pop.loc[1300:1340].mean()   # the 1350s, when the ordinance and statute were made
    w1, _ = C.factor_prices(l1)
    F = C.facts()
    caps = F["stat_1351_c3"]
    d = C.clark().loc[1300:1400]

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.9), gridspec_kw=dict(width_ratios=[1, 1.1]))
    fig.subplots_adjust(left=0.09, right=0.985, top=0.89, bottom=0.17, wspace=0.3)

    L = np.linspace(0.3, 1.25, 200)
    a1.plot(L, L ** (-a), color=OUTPUT, lw=2.0)
    a1.text(1.24, 0.85, T("劳动需求", "labour\ndemand"), fontsize=7.6, color=OUTPUT, ha="right", va="top")
    for lv, txt, ls in [(1.0, T("瘟疫前的劳动力", "labour before"), "-"), (l1, T("1350 年代", "1350s"), (0, (4, 2)))]:
        a1.plot([lv, lv], [0.4, 1.75], color=AMBER, lw=1.6, ls=ls)
        a1.text(lv + 0.02, 1.70, txt, fontsize=7.6, color=AMBER, ha="left", va="top")
    a1.axhline(1.0, color=PRICE, lw=1.2, ls=(0, (1.5, 1.5)))
    a1.text(0.31, 0.97, T("法定上限\n= 旧工资", "cap =\nold wage"), fontsize=7.6, color=PRICE, ha="left", va="top",
            linespacing=1.25)
    a1.plot([l1], [w1], "o", color=OUTPUT, ms=5.5)
    a1.annotate(T(f"市场工资\n×{w1:.2f}", f"market\nwage ×{w1:.2f}"), xy=(l1, w1), xytext=(0.76, 1.38), fontsize=7.6,
                color=OUTPUT, ha="left", va="bottom", linespacing=1.2,
                arrowprops=dict(arrowstyle="-", color=OUTPUT, lw=0.6, shrinkA=1))
    a1.annotate("", xy=(l1, 0.93), xytext=(1.0, 0.93),
                arrowprops=dict(arrowstyle="<->", color=INK, lw=0.8, shrinkA=0, shrinkB=0))
    a1.text((l1 + 1) / 2, 0.88, T(f"缺口 {1 - l1:.2f}", f"gap {1 - l1:.2f}"), fontsize=7.6, color=INK,
            ha="center", va="top")
    a1.set_xlim(0.3, 1.25)
    a1.set_ylim(0.4, 1.8)
    a1.set_xlabel(T("劳动（瘟疫前 = 1）", "labour (before the plague = 1)"))
    a1.set_ylabel(T("实际工资（瘟疫前 = 1）", "real wage (before = 1)"))
    _title(a1, T("(a) 上限压在旧工资：雇主抢人", "(a) a cap at the old wage: a shortage"))

    x = d.index.to_numpy() + 5
    a2.axvspan(1349, 1351, color=tint(PRICE, 0.18), lw=0, zorder=0)
    a2.plot(x, d["bcraft_wage_d"], "-o", color=PRICE, lw=2.0, ms=4.5)
    a2.plot(x, d["blab_wage_d"], "-s", color=AMBER, lw=1.8, ms=4, dashes=(4, 2))
    a2.axhline(caps[0], color=PRICE, lw=0.8, ls=(0, (1, 1.5)))
    a2.axhline(caps[4], color=AMBER, lw=0.8, ls=(0, (1, 1.5)))
    a2.text(1301, caps[0] - 0.06, T("木匠师傅上限 3 便士", "master carpenter\ncap 3d"), fontsize=7.6, color=PRICE,
            ha="left", va="top")
    a2.text(1301, caps[4] - 0.06, T("帮工上限 1½ 便士", "servant cap 1½d"), fontsize=7.6, color=AMBER,
            ha="left", va="top")
    a2.text(1408, 4.38, T("建筑工匠", "craftsmen"), fontsize=7.6, color=PRICE, ha="right", va="top")
    a2.text(1408, 2.68, T("建筑小工", "labourers"), fontsize=7.6, color=AMBER, ha="right", va="top")
    a2.text(1352, 0.95, T("1349 条例\n1351 法令", "1349 ordinance\n1351 statute"), fontsize=7.6, color=PRICE,
            ha="left", va="bottom", linespacing=1.2)
    a2.set_xlim(1300, 1410)
    a2.set_ylim(0.8, 5.2)
    a2.set_xticks([1300, 1325, 1350, 1375, 1400])
    a2.set_ylabel(T("名义日工资（便士）", "nominal day wage (pence)"))
    _title(a2, T("(b) 1350 年代起，工资越过上限", "(b) from the 1350s, wages above the caps"))
    for ax in (a1, a2):
        _grid(ax)
    return fig


# ---------------------------------------------------------------------------
@figure("livre_tournois")
def livre_tournois():
    """The livre tournois in francs of 1857 at each change of the legal coin rates, 1258-1360."""
    W = C.wailly()
    t = np.append(W["t"].to_numpy(), 1361.0)
    v = np.append(W["livre_francs"].to_numpy(), W["livre_francs"].iloc[-1])
    val = dict(zip(W["date_fr"], W["livre_francs"]))

    fig, ax = plt.subplots(figsize=(FIG_W, 2.75))
    fig.subplots_adjust(left=0.08, right=0.985, top=0.97, bottom=0.15)
    ax.axvspan(1285, 1314.9, color=tint(CASE, 0.08), lw=0, zorder=0)
    ax.axvspan(1351, 1361, color=tint(PRICE, 0.08), lw=0, zorder=0)
    ax.step(t, v, where="post", color=MONEY, lw=1.6, zorder=3)
    ax.text(1286, 21.4, T("腓力四世 1285—1314", "Philip IV 1285–1314"), fontsize=7.6, color=CASE, ha="left")
    ax.text(1361.5, 21.4, T("1351—1360：变动 71 次", "1351–60: 71 changes"), fontsize=7.6, color=PRICE, ha="right")
    ax.annotate(T(f"1305 年 4 月：{val['1305, avril']:.2f}", f"Apr 1305: {val['1305, avril']:.2f}"),
                xy=(1305.3, val["1305, avril"]), xytext=(1300.5, 3.0), fontsize=7.6, color=MONEY, ha="center",
                arrowprops=dict(arrowstyle="-", color=MONEY, lw=0.6))
    ax.annotate(T(f"1306 年 10 月\n恢复：{val['1306, oct.']:.2f}", f"restored\nOct 1306: {val['1306, oct.']:.2f}"),
                xy=(1307.4, val["1306, oct."]), xytext=(1299.5, 19.6), fontsize=7.6, color=MONEY, ha="left",
                va="center", linespacing=1.25, arrowprops=dict(arrowstyle="-", color=MONEY, lw=0.6))
    ax.annotate(T(f"1360 年 3 月：{val['1360, mars 15']:.2f}", f"Mar 1360: {val['1360, mars 15']:.2f}"),
                xy=(1360.2, val["1360, mars 15"]), xytext=(1340, 1.6), fontsize=7.6, color=MONEY, ha="center",
                arrowprops=dict(arrowstyle="-", color=MONEY, lw=0.6))
    ax.text(1262, 18.2, T(f"圣路易时代\n{val['1258']:.2f} 法郎", f"St Louis\n{val['1258']:.2f} francs"), fontsize=7.6,
            color=MONEY, ha="left", va="top", linespacing=1.25)
    ax.set_xlim(1255, 1362)
    ax.set_ylim(0, 23)
    ax.set_xlabel(T("年份", "year"))
    ax.set_ylabel(T("一里弗尔合 1857 年法郎", "francs of 1857 per livre"))
    _grid(ax)
    return fig
