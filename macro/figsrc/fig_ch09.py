"""Figures for Chapter 9 (古代印度与印度洋贸易).

Style as in fig_ch08.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series, the second series of a panel in AMBER. Colours follow §7: the routes and the outflow are
the external sector (EXTERNAL), interest rates are money (MONEY); the coins found in India are coloured by metal
(silver MONEY, gold AMBER, copper CASE). Every number comes from checks/check_ch09.py, which reads the snapshots
india_facts and darley2014_coin_finds (run data/fetch/darley2014_coin_finds.py first) and wb_external_annual.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch09 as C  # noqa: E402
from style import (AMBER, CASE, EXTERNAL, FIG_W, INK, LIGHT, MONEY, MUTED, T, clean_axes, figure,  # noqa: E402
                   tint)

METAL = {"AR": MONEY, "AV": AMBER, "AE": CASE}


def _title(ax, s):
    ax.set_title(s, fontsize=9.0, weight="bold", loc="left", pad=4)


def _grid(ax, axis="y"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=8.5)


def _stack(ax, y, segments, color, h=0.56, ls="-", fill=True, text=True):
    """A horizontal stacked bar of (label, days); segments alternate between two tints of the colour."""
    x = 0.0
    for k, (lab, d) in enumerate(segments):
        fc = tint(color, 0.85 if k % 2 == 0 else 0.45) if fill else "none"
        ax.barh(y, d, left=x, height=h, color=fc, ec=color if not fill else "white", lw=0.9 if not fill else 0.6,
                ls=ls, zorder=3)
        if text and lab:
            ax.text(x + d / 2, y, lab, fontsize=7.6, ha="center", va="center", zorder=4,
                    color="white" if (fill and k % 2 == 0) else INK)
        x += d
    return x


# ---------------------------------------------------------------------------
@figure("india_route")
def india_route():
    F = C.facts()
    R = C.route(F)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(FIG_W, 3.3), gridspec_kw=dict(height_ratios=[1, 1.75], hspace=0.62))
    xmax = 520

    r = R["rome"]
    segs = [("", r[k]) for k in ("nile", "desert", "red_sea", "ocean")]
    tot = _stack(ax1, 0, segs, EXTERNAL, h=0.62, text=False)
    ax1.text(tot + 6, 0.12, T(f"尼罗河 {r['nile']:.0f} + 沙漠 {r['desert']:.0f} + 红海 {r['red_sea']:.0f} + 大洋 {r['ocean']:.0f}"
                              f" = {tot:.0f} 天", f"Nile {r['nile']:.0f} + desert {r['desert']:.0f} + Red Sea {r['red_sea']:.0f}"
                              f" + ocean {r['ocean']:.0f} = {tot:.0f} days"), fontsize=7.8, color=EXTERNAL, ha="left", va="bottom")
    ax1.text(tot + 6, -0.12, T("十二月到一月中旬回航，一年之内往返", "back from December to mid-January, within the year"),
             fontsize=7.6, color=MUTED, ha="left", va="top")
    ax1.set_yticks([0], [T("去程", "out")])
    ax1.set_ylim(-0.6, 0.6)
    _title(ax1, T("(a) 罗马：借季风横渡大洋，去程 94 天", "(a) Rome: across the ocean with the monsoon, 94 days out"))

    o, b, bw = R["han_out"], R["han_back"], R["han_back_ws"]
    segs_o = [(T("5 个月", "5 months"), o["dou"]), (T("4 个月", "4 months"), o["yilu"]), ("", o["chenli"]), ("", o["walk"]),
              (T("2 个月", "2 months"), o["huangzhi"])]
    t_out = _stack(ax2, 1, segs_o, EXTERNAL)
    ax2.text(t_out + 6, 1, T(f"≥{t_out:.0f} 天", f"≥{t_out:.0f} days"), fontsize=7.8, color=EXTERNAL, ha="left", va="center")
    ax2.annotate(T("船行 20 余日，步行 10 余日", "20+ days by ship, 10+ on foot"), xy=(o["dou"] + o["yilu"] + 15, 1.3),
                 xytext=(o["dou"] + o["yilu"] + 15, 1.72), fontsize=7.6, color=MUTED, ha="center", va="bottom",
                 arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7))
    _stack(ax2, 0, [("", bw["pizong"]), ("", bw["rinan"])], EXTERNAL, fill=False, ls=(0, (3, 2)), text=False)
    t_back = _stack(ax2, 0, [(T("8 个月", "8 months"), b["pizong"]), (T("2 个月", "2 months"), b["rinan"])], EXTERNAL)
    ax2.text(t_back + 6, -0.02, T(f"{t_back:.0f} 天", f"{t_back:.0f} days"), fontsize=7.8, color=EXTERNAL, ha="left", va="center")
    t_ws = sum(bw.values())
    ax2.text(t_ws - 4, -0.48, T(f"维基文库本“八月”：{t_ws:.0f} 天", f"Wikisource '8 months': {t_ws:.0f} days"), fontsize=7.6,
             color=MUTED, ha="right", va="top")
    ax2.set_yticks([1, 0], [T("去程", "out"), T("回程", "back")])
    ax2.set_ylim(-0.95, 1.95)
    _title(ax2, T("(b) 汉朝：沿岸转送，去程至少 360 天", "(b) Han: from port to port, at least 360 days out"))
    for ax in (ax1, ax2):
        ax.set_xlim(0, xmax)
        _grid(ax, axis="x")
        ax.tick_params(axis="y", length=0)
    ax2.set_xlabel(T("天（一个月按 30 天）", "days (a month taken as 30 days)"), fontsize=9)
    return fig


@figure("india_rates")
def india_rates():
    F = C.facts()
    R = C.rates(F)
    names = [T(f"{n}\n月 {m:g}", f"{e}\n{m:g}/mo") for n, e, m in
             zip(("公正", "商业", "林中", "海上"), ("just", "trade", "forest", "sea"), R["monthly"])]
    x = np.arange(len(R))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIG_W, 2.7), gridspec_kw=dict(wspace=0.34))

    a = 100 * R["annual"].to_numpy()
    ax1.bar(x, a, width=0.6, color=MONEY, zorder=3)
    for xi, ai in zip(x, a):
        ax1.text(xi, ai + 5, f"{ai:.0f}%", fontsize=7.8, color=MONEY, ha="center", va="bottom")
    ax1.set_xticks(x, names)
    ax1.set_ylim(0, 275)
    ax1.set_ylabel(T("年利率（%，单利）", "annual rate (%, simple)"), fontsize=9)
    _grid(ax1)
    _title(ax1, T("(a) 海上的利率是公正利率的 16 倍", "(a) Sea-traders pay 16 times the just rate"))

    p = R["p"].to_numpy()
    ax2.bar(x, p, width=0.6, color=AMBER, zorder=3)
    for xi, pi in zip(x, p):
        ax2.text(xi, pi + 0.03, f"{pi:.2f}", fontsize=7.8, color=AMBER, ha="center", va="bottom")
    ax2.set_xticks(x, names)
    ax2.set_ylim(0, 1.15)
    ax2.set_ylabel(T("还款概率 $p$", "probability of repayment $p$"), fontsize=9)
    ax2.text(3.4, 1.08, T(f"$p=(1+r_f)/(1+i)$，$r_f={100 * C.R_F:.0f}\\%$", f"$p=(1+r_f)/(1+i)$, $r_f={100 * C.R_F:.0f}\\%$"),
             fontsize=7.8, color=MUTED, ha="right", va="center")
    _grid(ax2)
    _title(ax2, T("(b) 海上贷款，预期只收回三分之一", "(b) A third of sea loans expected back"))
    return fig


@figure("india_scale")
def india_scale():
    F = C.facts()
    S = C.scale(F)
    us = -C.us_ca_2025()
    labels = {
        "duty": T("赫尔玛波隆号的关税", "Hermapollon's duty"),
        "ship": T("赫尔玛波隆号一船货", "Hermapollon's cargo"),
        "india": T("印度：五千万（本章的读法）", "India: 50 million (this chapter)"),
        "india_dl": T("印度：五千五百万（校勘记）", "India: 55 million (apparatus)"),
        "three": T("三个地区：一亿（12.84）", "three regions: 100 million"),
        "translation": T("英译的五亿五千万", "the translation's 550 million"),
        "centiplicato": T("“一百倍”：印度货在罗马的价值", "'a hundred times': in Rome"),
    }
    keys = list(labels)[::-1]
    y = np.arange(len(keys))
    v = S.loc[keys, "pct_gdp"].to_numpy()
    doubt = {"translation", "centiplicato"}
    cols = [MUTED if k in doubt else EXTERNAL for k in keys]
    fig, ax = plt.subplots(figsize=(FIG_W, 2.9))
    fig.subplots_adjust(left=0.34, right=0.97)
    ax.barh(y, v, height=0.62, color=[tint(c, 0.9) for c in cols], zorder=3)
    for yi, vi, c, k in zip(y, v, cols, keys):
        s = f"{vi:.2f}%" if vi < 1 else f"{vi:.1f}%"      # two decimals below 1%, as the text
        if k in doubt:      # inside the bar, clear of the dashed line
            ax.text(vi / 1.12, yi, s, fontsize=7.8, color="white", ha="right", va="center", zorder=4)
        else:
            ax.text(vi * 1.12, yi, s, fontsize=7.8, color=c, ha="left", va="center")
    ax.set_yticks(y, [labels[k] for k in keys])
    ax.set_xscale("log")
    ax.set_xlim(0.005, 200)
    ax.axvline(us, color=INK, lw=1.0, ls=(0, (4, 2)), zorder=2)
    ax.text(us * 1.12, len(keys) - 0.5, T(f"美国 2025 年经常账户逆差 {us:.1f}%", f"US deficit, 2025: {us:.1f}%"),
            fontsize=7.6, color=INK, ha="left", va="center")
    ax.set_xticks([0.01, 0.1, 1, 10, 100], ["0.01%", "0.1%", "1%", "10%", "100%"])
    ax.set_xlabel(T("占罗马 GDP 的比例（对数轴；GDP = 180 亿塞斯特斯）", "share of Roman GDP (log scale; GDP = 18 billion sesterces)"),
                  fontsize=9)
    ax.set_ylim(-0.6, len(keys) + 0.1)
    _grid(ax, axis="x")
    ax.tick_params(axis="y", length=0)
    _title(ax, T("普林尼的数字只占罗马 GDP 的 0.3%—0.6%", "Pliny's figures are 0.3-0.6% of Roman GDP"))
    return fig


@figure("india_coins")
def india_coins():
    Tt = C.darley_totals()
    I = C.finds_1st(C.darley())
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIG_W, 3.3), gridspec_kw=dict(width_ratios=[1.25, 1], wspace=0.42))

    cent = [T("公元前", "BC"), "1", "2", "3", "4", "5", "6", "7"]
    x = np.arange(len(Tt))
    w = 0.27
    for k, m in enumerate(C.METALS):
        v = Tt[m].to_numpy(dtype=float)
        mask = v > 0
        ax1.bar(x[mask] + (k - 1) * w, v[mask], width=w, color=METAL[m], zorder=3)
    ax1.set_yscale("log")
    ax1.set_ylim(0.8, 12000)
    ax1.set_xticks(x, cent)
    ax1.set_xlabel(T("发行者的世纪", "century of the issuer"), fontsize=9)
    ax1.set_ylabel(T("枚（对数轴）", "coins (log scale)"), fontsize=9)
    ax1.text(1 - w, Tt.loc["1st", "AR"] * 1.25, f"{Tt.loc['1st', 'AR']:.0f}", fontsize=7.6, color=MONEY, ha="center", va="bottom")
    ax1.text(4 + w, Tt.loc["4th", "AE"] * 1.25, f"{Tt.loc['4th', 'AE']:.0f}", fontsize=7.6, color=CASE, ha="center", va="bottom")
    for m, xt, yt in (("AR", 3.0, 3000), ("AV", 3.0, 900), ("AE", 3.0, 270)):
        ax1.text(xt + 2.2, yt, {"AR": T("银", "silver"), "AV": T("金", "gold"), "AE": T("铜", "copper")}[m], fontsize=7.8,
                 color=METAL[m], ha="left", va="center", weight="bold")
    _grid(ax1)
    _title(ax1, T("(a) 1 世纪以银为主，以后是金", "(a) Silver in the 1st century, then gold"))

    order = ["Augustus", "Augustus/Tiberius", "Tiberius", "Caligula", "Claudius", "Nero", "Vespasian", "Titus", "Domitian", "Nerva"]
    names = {"Augustus": T("奥古斯都", "Augustus"), "Augustus/Tiberius": T("奥古斯都或提比略", "Aug./Tib."),
             "Tiberius": T("提比略", "Tiberius"), "Caligula": T("卡利古拉", "Caligula"), "Claudius": T("克劳狄乌斯", "Claudius"),
             "Nero": T("尼禄（64 年改革）", "Nero (reform, 64)"), "Vespasian": T("韦斯巴芗", "Vespasian"), "Titus": T("提图斯", "Titus"),
             "Domitian": T("图密善", "Domitian"), "Nerva": T("涅尔瓦", "Nerva")}
    I = I.reindex(order).fillna(0)
    y = np.arange(len(order))[::-1]
    h = 0.38
    ax2.barh(y + h / 2, I["silver"], height=h, color=MONEY, zorder=3)
    ax2.barh(y - h / 2, I["gold"], height=h, color=AMBER, zorder=3)
    for yi, s, g in zip(y, I["silver"], I["gold"]):
        if s:
            ax2.text(s + 25, yi + h / 2 + 0.06, f"{s:.0f}", fontsize=7.6, color=MONEY, ha="left", va="center")
        if g:
            ax2.text(g + 25, yi - h / 2 - 0.06, f"{g:.0f}", fontsize=7.6, color=AMBER, ha="left", va="center")
    ax2.set_yticks(y, [names[k] for k in order])
    ax2.set_xlim(0, 1900)
    ax2.set_xlabel(T("枚", "coins"), fontsize=9)
    _grid(ax2, axis="x")
    ax2.tick_params(axis="y", length=0)
    _title(ax2, T("(b) 1 世纪的银币几乎全是旧钱", "(b) 1st-century silver: old coins"))
    return fig
