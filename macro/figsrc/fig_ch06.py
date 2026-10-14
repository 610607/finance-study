"""Figures for Chapter 6 (美索不达米亚与埃及：神庙、宫廷与记账).

Style as in fig_ch05.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series, the second series of a panel in AMBER, dashed. Colours follow §7: the unit of account and
debts at interest MONEY, the goods handed over INSTIT, prices PRICE. Every number comes from checks/check_ch06.py,
which reads the snapshots meso_facts and babylon_prices; meso_debt is the teaching model of ex:meso-debt
(eq:meso-debt).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch06 as C  # noqa: E402
from style import (AMBER, FIG_W, INK, INSTIT, LIGHT, MONEY, MUTED, PRICE, SHADE, T, clean_axes,  # noqa: E402
                   figure, tint)

DOT = dict(marker="o", ms=5.0, mec="white", mew=0.6)
SQ = dict(marker="s", ms=4.6, mec="white", mew=0.6)
MINUS = "−"


def _title(ax, s):
    ax.set_title(s, fontsize=9.0, weight="bold", loc="left", pad=4)


def _grid(ax, axis="y"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=8.5)


def _num(v: float, fmt: str = ".2f") -> str:
    return f"{v:{fmt}}".replace("-", MINUS)


def _bc(y: float) -> str:
    return T(f"前 {-int(y)}", f"{-int(y)} BC")


# ---------------------------------------------------------------------------
@figure("meso_ox")
def meso_ox():
    F = C.facts()
    total, ox = F["erman_ox119"][0], F["erman_ox111"][0]
    sub = F["erman_subst"]
    paid = [(sub[0], T("镶嵌的手杖\n25", "inlaid stick\n25"), tint(INSTIT, 0.80), "white"),
            (sub[1], T("手杖\n12", "stick\n12"), tint(INSTIT, 0.55), "white"),
            (sub[3], T("蜂蜜\n11 罐", "11 jars\nhoney"), tint(INSTIT, 0.32), INK)]
    rest = total - sum(p[0] for p in paid)
    fig, ax = plt.subplots(figsize=(FIG_W, 2.15))
    h = 0.52
    y_top, y_bot = 1.0, 0.0
    ax.add_patch(Rectangle((0, y_top - h / 2), ox, h, fc=MONEY, ec="white", lw=1.0, zorder=3))
    ax.text(ox / 2, y_top, T(f"牛价 {ox:.0f}", f"the ox {ox:.0f}"), color="white", fontsize=8.6, weight="bold",
            ha="center", va="center", zorder=4)
    ax.add_patch(Rectangle((ox, y_top - h / 2), total - ox, h, fc=tint(MONEY, 0.40), ec="white", lw=1.0, zorder=3))
    ax.annotate(T(f"礼物与花费 {total - ox:.0f}", f"presents and expenses {total - ox:.0f}"),
                xy=(ox + (total - ox) / 2, y_top + h / 2), xytext=(total, y_top + h / 2 + 0.30),
                fontsize=7.8, color=MONEY, ha="right", va="center",
                arrowprops=dict(arrowstyle="-", color=MONEY, lw=0.6))
    x = 0.0
    for w, s, fc, tc in paid:
        ax.add_patch(Rectangle((x, y_bot - h / 2), w, h, fc=fc, ec="white", lw=1.0, zorder=3))
        ax.text(x + w / 2, y_bot, s, color=tc, fontsize=7.8, ha="center", va="center", zorder=4, linespacing=1.15)
        x += w
    ax.add_patch(Rectangle((x, y_bot - h / 2), rest, h, fc="white", ec=MUTED, lw=0.9, ls=(0, (3, 2)), zorder=3))
    ax.text(x + rest / 2, y_bot, T(f"其余 {rest:.0f}：埃尔曼只写了“等等”", f"the other {rest:.0f}: Erman says only “and so on”"),
            color=MUTED, fontsize=7.8, ha="center", va="center", zorder=4)
    kg = total * F["erman_uten"][1] / 1000
    ax.text(0, y_top + h / 2 + 0.30, T(f"共 {total:.0f} 德本 = {kg:.1f} 公斤铜，没有一块铜转手",
                                           f"{total:.0f} deben in all = {kg:.1f} kg of copper; no copper changed hands"),
            fontsize=7.8, color=INK, ha="left", va="center")
    ax.set_xlim(0, total + 0.5)
    ax.set_ylim(-0.45, 1.75)
    ax.set_yticks([y_top, y_bot])
    ax.set_yticklabels([T("账上应付\n（计价）", "owed\n(account)"), T("实际交付\n（结算）", "paid\n(goods)")],
                       fontsize=8.5)
    ax.set_xticks([0, 25, 37, 48, 75, 100, total])
    ax.set_xlabel(T("德本（1 德本 = 91 克铜）", "deben (1 deben = 91 g of copper)"), fontsize=9)
    clean_axes(ax)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", labelsize=8.5)
    return fig


# ---------------------------------------------------------------------------
@figure("meso_debt")
def meso_debt():
    D = C.DEBT
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIG_W, 2.75), gridspec_kw=dict(wspace=0.30))

    t = np.linspace(0, 6, 241)
    for i, col, kw, ls, lab, at in ((D["i_s"], MONEY, DOT, "-", T("20%（白银）", "20% (silver)"), (4.25, 1.55)),
                                    (D["i_b"], AMBER, SQ, (0, (4, 2)), T("33⅓%（大麦）", "33⅓% (barley)"), (2.0, 4.6))):
        ax1.plot(t, (1 + i) ** t, color=col, lw=2.0, ls=ls, zorder=3)
        k = np.arange(0, 7)
        ax1.plot(k, (1 + i) ** k, ls="none", color=col, zorder=4, **kw)
        td = C.doubling(i)
        ax1.plot([td, td], [0.8, 2], color=col, lw=0.7, ls=":", zorder=2)
        ax1.text(td, 0.86, T(f"{td:.2f} 年", f"{td:.2f} yr"), fontsize=7.8, color=col, ha="center", va="bottom",
                 bbox=dict(fc="white", ec="none", pad=0.6))
        ax1.text(*at, lab, fontsize=8.0, color=col, ha="left", va="center")
    ax1.axhline(2, color=MUTED, lw=0.8, ls=":", zorder=1)
    ax1.text(0.08, 2.08, T("翻一番", "doubled"), fontsize=7.8, color=MUTED, ha="left", va="bottom")
    ax1.axvline(3, color=MUTED, lw=0.8, ls=":", zorder=1)
    ax1.text(3.08, 5.55, T("第 117 条：\n劳役三年", "§ 117:\nthree years"), fontsize=7.8, color=MUTED, ha="left",
             va="top", linespacing=1.25)
    ax1.set_xlim(0, 6)
    ax1.set_ylim(0.8, 5.8)
    ax1.set_xlabel(T("年", "years"), fontsize=9)
    ax1.set_ylabel(T("债务 ÷ 本金", "debt ÷ principal"), fontsize=9)
    _grid(ax1)
    _title(ax1, T("(a) 33⅓% 的债 2.41 年翻一番", "(a) At 33⅓%, doubled in 2.41 years"))

    n = D["years"]
    yrs = np.arange(n + 1)
    ok = C.debt_path(D["d0"], D["i_b"], D["x_bar"], years=n)
    bad = C.debt_path(D["d0"], D["i_b"], D["x_bar"], bad=D["bad"], years=n)
    s48 = C.debt_path(D["d0"], D["i_b"], D["x_bar"], bad=D["bad"], s48=True, years=n)
    ax2.axvspan(0, max(D["bad"]), color=SHADE, lw=0, zorder=0)
    ax2.text(1.0, 6.55, T("歉收两年", "failed\nharvests"), fontsize=7.8, color=MUTED, ha="center", va="top",
             linespacing=1.15)
    dbar = D["x_bar"] / D["i_b"]
    ax2.axhline(dbar, color=MUTED, lw=0.8, ls=":", zorder=1)
    ax2.text(n, dbar - 0.12, T(f"界线 $\\bar D$ = {dbar:.0f} 库尔", f"threshold $\\bar D$ = {dbar:.0f} kur"),
             fontsize=7.8, color=MUTED, ha="right", va="top")
    ax2.plot(yrs, ok, color=tint(MONEY, 0.45), lw=1.4, zorder=2, marker="o", ms=3.6, mec="white", mew=0.5)
    ax2.plot(yrs, bad, color=MONEY, lw=2.0, zorder=3, **DOT)
    ax2.plot(yrs, s48, color=AMBER, lw=2.0, ls=(0, (4, 2)), zorder=4, **SQ)
    ax2.text(n - 0.1, bad[-1] - 0.15, T("利息照算", "interest accrues"), fontsize=7.8, color=MONEY, ha="right",
             va="top")
    ax2.text(5.05, 1.25, T("按第 48 条免息：\n第六年还清", "§ 48, no interest:\nrepaid in year 6"), fontsize=7.8,
             color=AMBER, ha="left", va="center", linespacing=1.25)
    ax2.text(0.12, 0.62, T("正常年份：\n第四年还清", "no failure:\nrepaid in year 4"), fontsize=7.8,
             color=MONEY, ha="left", va="center", linespacing=1.25)
    ax2.set_xlim(0, n)
    ax2.set_ylim(0, 6.7)
    ax2.set_xticks(yrs)
    ax2.set_xlabel(T("年", "years"), fontsize=9)
    ax2.set_ylabel(T("年末债务（库尔大麦）", "debt at end of year (kur of barley)"), fontsize=9)
    _grid(ax2)
    _title(ax2, T("(b) 越过界线，债就还不清", "(b) Past the threshold, never repaid"))
    return fig


# ---------------------------------------------------------------------------
@figure("meso_prices")
def meso_prices():
    P = C.prices()
    A = C.annual(P)
    full = A.reindex(range(int(P["year"].min()), int(P["year"].max()) + 1))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIG_W, 2.95), gridspec_kw=dict(width_ratios=[1.3, 1], wspace=0.27))

    ax1.plot(full.index, full["barley"], color=PRICE, lw=1.1, zorder=3)
    ax1.plot(A.index, A["barley"], ls="none", marker="o", ms=2.8, color=PRICE, mec="none", zorder=4)
    ax1.plot(full.index, full["dates"], color=AMBER, lw=1.0, ls=(0, (4, 2)), zorder=2)
    ax1.plot(A.index, A["dates"], ls="none", marker="s", ms=2.4, color=AMBER, mec="none", zorder=3)
    for y, dy in ((-322, 1.0), (-309, 1.0), (-83, 1.0)):
        v = max(A.loc[y, "barley"], A.loc[y, "dates"])
        ax1.annotate(_bc(y), xy=(y, v * 1.08), xytext=(y + (-40 if y == -322 else 40 if y == -309 else -10), v * 2.2),
                     fontsize=7.6, color=INK, ha="center", va="bottom",
                     arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    ax1.text(-580, 210, T("大麦", "barley"), fontsize=8.0, color=PRICE, ha="left", va="center")
    ax1.text(-580, 135, T("椰枣", "dates"), fontsize=8.0, color=AMBER, ha="left", va="center")
    ax1.set_yscale("log")
    ax1.set_ylim(1.0, 300)
    ax1.set_yticks([1, 2, 5, 10, 20, 50, 100, 200])
    ax1.set_yticklabels(["1", "2", "5", "10", "20", "50", "100", "200"])
    ax1.minorticks_off()
    ax1.set_xlim(-590, -50)
    ticks = [-550, -450, -350, -250, -150, -50]
    ax1.set_xticks(ticks)
    ax1.set_xticklabels([T(f"前 {-y}", f"{-y}") for y in ticks])
    ax1.set_xlabel(T("", "year BC"), fontsize=9)
    ax1.set_ylabel(T("克白银 / 100 升（对数）", "g of silver per 100 l (log)"), fontsize=9)
    _grid(ax1)
    _title(ax1, T("(a) 价格大起大落，两种作物多半一起涨", "(a) Big swings, mostly in both crops"))

    m = np.arange(1, 13)
    for good, col, kw, dx, txt in (("barley", PRICE, DOT, -0.13, T("大麦", "barley")),
                                   ("dates", AMBER, SQ, 0.13, T("椰枣", "dates"))):
        r = C.seasonal(good, P)
        ax2.errorbar(m + dx, 100 * r["eff"], yerr=100 * r["se"], ls="none", color=col, elinewidth=0.8, capsize=0,
                     zorder=3)
        ax2.plot(m + dx, 100 * r["eff"], color=col, lw=1.4 if good == "barley" else 1.2,
                 ls="-" if good == "barley" else (0, (4, 2)), zorder=4, **kw)
        p = r["p"]
        if good == "barley":
            ax2.text(4.6, 25.5, T(f"大麦  p = {p:.3f}", f"barley  p = {p:.3f}"), fontsize=8.0, color=col, ha="left")
        else:
            ax2.text(4.6, 20.5, T(f"椰枣  p = {p:.2f}", f"dates  p = {p:.2f}"), fontsize=8.0, color=col, ha="left")
    ax2.axhline(0, color=MUTED, lw=0.8, ls=":", zorder=1)
    ax2.set_xlim(0.4, 12.6)
    ax2.set_ylim(-32, 30)
    ax2.set_xticks(m)
    ax2.set_xlabel(T("数据集的月份编号", "month as numbered in the dataset"), fontsize=9)
    ax2.set_ylabel(T("比全年平均（对数百分点）", "vs. the year's mean (log points)"), fontsize=9)
    _grid(ax2)
    ax2.tick_params(axis="x", labelsize=7.8)
    _title(ax2, T("(b) 大麦有季节，椰枣看不出", "(b) Barley seasonal, dates not"))
    return fig
