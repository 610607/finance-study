"""Figures for Chapter 2 (国民核算与恒等式).

Style as in fig_ch12.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series, the second series of a panel in AMBER, dashed, with square markers. Sector colours follow
the semantics of §7: private sector and output green, government purple, rest of the world orange, data and
statistics warm grey. Every number comes from checks/check_ch02.py, which reads the snapshots accounts_facts and
bea_nipa_annual; the cotton economy is the teaching example of the text (ex:accounts-cloth).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch02 as C  # noqa: E402
from style import (AMBER, EXTERNAL, FIG_W, FISCAL, INK, INSTIT, LIGHT, MUTED, OUTPUT, T,  # noqa: E402
                   clean_axes, figure, halo, tint)

SQUARE = dict(marker="s", ms=4.6, mfc=AMBER, mec="white", mew=0.6)
DOT = dict(marker="o", ms=5.0, mec="white", mew=0.6)


def _title(ax, s):
    ax.set_title(s, fontsize=8.8, weight="bold", loc="left", pad=4)


def _grid(ax, axis="y"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


@figure("accounts_chain")
def accounts_chain():
    a = C.chain_accounts()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIG_W, 2.9), gridspec_kw=dict(width_ratios=[1.0, 1.05], wspace=0.32))
    # (a) output of each firm = intermediate input + value added
    names = [T("棉农", "cotton\nfarmer"), T("纺纱厂", "spinner"), T("织布厂", "weaver")]
    keys = ["棉农", "纺纱厂", "织布厂"]
    inputs = [C.CHAIN[k]["inputs"] for k in keys]
    va = [C.CHAIN[k]["output"] - C.CHAIN[k]["inputs"] for k in keys]
    x = range(3)
    ax1.bar(x, inputs, width=0.58, color=tint(INSTIT, 0.30), edgecolor="white", zorder=3)
    ax1.bar(x, va, bottom=inputs, width=0.58, color=OUTPUT, edgecolor="white", zorder=3)
    for i in x:
        if inputs[i]:
            ax1.text(i, inputs[i] / 2, T(f"中间投入\n{inputs[i]}", f"inputs\n{inputs[i]}"), ha="center", va="center",
                     fontsize=7.6, color=INK, zorder=4)
        ax1.text(i, inputs[i] + va[i] / 2, T(f"增加值\n{va[i]}", f"value\nadded\n{va[i]}"), ha="center", va="center",
                 fontsize=7.6, color="white", weight="bold", zorder=4)
        ax1.text(i, inputs[i] + va[i] + 2, T(f"产出 {inputs[i] + va[i]}", f"output {inputs[i] + va[i]}"), ha="center",
                 va="bottom", fontsize=7.8, color=INK)
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(names, fontsize=8.5)
    ax1.set_ylim(0, 106)
    ax1.set_ylabel(T("元", "yuan"), fontsize=9)
    _grid(ax1)
    ax1.tick_params(labelsize=8.5)
    ax1.text(-0.3, 103, T(f"产出相加 = {a['output']}\n增加值相加 = {a['production']}",
                          f"outputs add up to {a['output']}\nvalue added to {a['production']}"),
             fontsize=7.6, color=MUTED, ha="left", va="top")
    _title(ax1, T("(a) 每家企业只算自己新增的部分", "(a) Each firm counts only what it adds"))

    # (b) three approaches, one total
    cols = [T("生产法", "production"), T("支出法", "expenditure"), T("收入法", "income")]
    stacks = [
        [(a["va_farmer"], "棉农", "farmer"), (a["va_spinner"], "纺纱", "spinner"), (a["va_weaver"], "织布", "weaver")],
        [(a["consumption"], "消费", "consumer\nspending"), (a["investment"], "存货投资", "stocks")],
        [(a["wages"], "工资", "wages"), (a["profits"], "利润", "profits")],
    ]
    shades = [OUTPUT, tint(OUTPUT, 0.45), tint(OUTPUT, 0.7)]
    for i, st in enumerate(stacks):
        bottom = 0
        for j, (v, zh, en) in enumerate(st):
            ax2.bar(i, v, bottom=bottom, width=0.78, color=shades[j], edgecolor="white", zorder=3)
            # English labels go on two lines: the words are wider than the bars
            ax2.text(i, bottom + v / 2, T(f"{zh} {v}", f"{en}\n{v}" if v >= 20 else f"{en} {v}"), ha="center", va="center", fontsize=7.6,
                           color="white" if j == 0 else INK, weight="bold" if j == 0 else "normal", zorder=4)
            bottom += v
        ax2.text(i, bottom + 2, f"= {bottom}", ha="center", va="bottom", fontsize=8.2, color=INK, weight="bold")
    ax2.set_xticks(range(3))
    ax2.set_xticklabels(cols, fontsize=8.5)
    ax2.set_ylim(0, 106)
    _grid(ax2)
    ax2.tick_params(labelsize=8.5)
    _title(ax2, T("(b) 三种算法得到同一个数", "(b) Three approaches, one total"))
    return fig


@figure("accounts_depression")
def accounts_depression():
    F, B = C.facts(), C.bea()
    K = C.kuznets_table(F) / 1000
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIG_W, 2.75), gridspec_kw=dict(wspace=0.3))
    yrs = list(K.index)
    ax1.fill_between(yrs, K.produced, K.paid_out, color=tint(INSTIT, 0.18), lw=0, zorder=1)
    ax1.plot(yrs, K.produced, color=OUTPUT, lw=2.0, **DOT, mfc=OUTPUT, zorder=3)
    ax1.plot(yrs, K.paid_out, color=AMBER, lw=2.0, dashes=(4, 2), **SQUARE, zorder=3)
    ax1.text(1929.15, K.produced[1929] + 2.5, T(f"生产的国民收入\n{K.produced[1929]:.1f}", f"income produced\n{K.produced[1929]:.1f}"),
             color=OUTPUT, fontsize=7.8, ha="left", va="bottom")
    ax1.text(1932, K.produced[1932] - 3, f"{K.produced[1932]:.1f}\n(−{F['k_produced_53'][0]:g}%)", color=OUTPUT,
             fontsize=7.8, ha="center", va="top")
    ax1.text(1931.15, K.paid_out[1931] + 3.5, T("支付的国民收入", "income paid out"), color=AMBER, fontsize=7.8, ha="left")
    ax1.text(1932.1, K.paid_out[1932] + 1.0, f"{K.paid_out[1932]:.1f}\n(−{F['k_paid_40'][0]:g}%)", color=AMBER,
             fontsize=7.8, ha="left", va="bottom")
    gap = (K.produced[1931] + K.paid_out[1931]) / 2
    ax1.annotate(T("两线之差 = 企业储蓄\n（1930 年起为负）", "gap = business savings\n(negative from 1930)"), (1931, gap),
                 xytext=(1929.15, 44), fontsize=7.6, color=MUTED, ha="left", va="center",
                 arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    ax1.set_xticks(yrs)
    ax1.set_xlim(1928.7, 1932.9)
    ax1.set_ylim(28, 96)
    ax1.set_ylabel(T("十亿美元", "billion dollars"), fontsize=9)
    _grid(ax1)
    ax1.tick_params(labelsize=8.5)
    _title(ax1, T("(a) 1934 年的估计：生产的比支付的跌得多", "(a) 1934: income produced fell more"))

    yrs2 = list(range(1929, 1940))
    real = 100 * B.gdp_real_2017.loc[yrs2] / B.gdp_real_2017[1929]
    defl = (B.gdp / B.gdp_real_2017).loc[yrs2]
    defl = 100 * defl / defl[1929]
    nom = 100 * B.gdp.loc[yrs2] / B.gdp[1929]
    ax2.axhline(100, color=MUTED, lw=0.7, ls=":", zorder=1)
    ax2.plot(yrs2, real, color=OUTPUT, lw=2.0, **DOT, mfc=OUTPUT, zorder=3)
    ax2.plot(yrs2, defl, color=AMBER, lw=2.0, dashes=(4, 2), **SQUARE, zorder=3)
    ax2.text(1937, real[1937] + 3, T("实际 GDP", "real GDP"), color=OUTPUT, fontsize=7.8, ha="center", va="bottom")
    ax2.text(1937.3, defl[1937] - 4, T("GDP 平减指数", "GDP deflator"), color=AMBER, fontsize=7.8, ha="center", va="top")
    ax2.text(1929.3, 58, T(f"1933 年：实际 GDP {real[1933]:.1f}，平减指数 {defl[1933]:.1f}\n"
                           f"名义 GDP = {real[1933]:.1f} × {defl[1933]:.1f} / 100 = {nom[1933]:.1f}",
                           f"1933: real GDP {real[1933]:.1f}, deflator {defl[1933]:.1f}\n"
                           f"nominal = {real[1933]:.1f} × {defl[1933]:.1f} / 100 = {nom[1933]:.1f}"),
             fontsize=7.6, color=INK, ha="left", va="center")
    ax2.set_xticks([1929, 1931, 1933, 1935, 1937, 1939])
    ax2.set_ylim(48, 119)
    ax2.set_ylabel(T("1929 = 100", "1929 = 100"), fontsize=9)
    _grid(ax2)
    ax2.tick_params(labelsize=8.5)
    _title(ax2, T("(b) 今天的数据：物价跌了约四分之一", "(b) Today: prices fell by a quarter"))
    return fig


@figure("accounts_balances")
def accounts_balances():
    B = C.bea()
    S = C.sector_balances(B)
    sd = 100 * B.stat_discrepancy.loc[1960:] / B.gdp.loc[1960:]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(FIG_W, 4.3), gridspec_kw=dict(height_ratios=[2.3, 1.0], hspace=0.42))
    ax1.axhline(0, color=INK, lw=0.7, zorder=1)
    ax1.plot(S.index, S.private, color=OUTPUT, lw=2.0, zorder=3)
    ax1.plot(S.index, S.government, color=FISCAL, lw=2.0, zorder=3)
    ax1.plot(S.index, S.rest_of_world, color=EXTERNAL, lw=2.0, dashes=(4, 2), zorder=3)
    ax1.text(1961, 7.2, T("私人部门", "private sector"), color=OUTPUT, fontsize=8.2, ha="left")
    ax1.text(1961, -7.2, T("政府", "government"), color=FISCAL, fontsize=8.2, ha="left")
    ax1.text(2006, 7.0, T("国外", "rest of\nthe world"), color=EXTERNAL, fontsize=8.2, ha="center", va="bottom")
    # (year, column, colour, x offset, y offset, ha) for the marked years
    marks = [(2000, "private", OUTPUT, 0.0, -1.6, "center"), (2000, "government", FISCAL, 0.0, 1.5, "center"),
             (2009, "private", OUTPUT, 0.8, 0.4, "left"), (2009, "government", FISCAL, 0.8, -0.6, "left"),
             (2020, "private", OUTPUT, -0.8, 0.5, "right"), (2020, "government", FISCAL, -0.8, -0.3, "right")]
    for y, col, c, dx, dy, ha in marks:
        v = S.loc[y, col]
        ax1.plot([y], [v], "o", color=c, ms=4.6, mec="white", mew=0.6, zorder=4)
        ax1.text(y + dx, v + dy, f"{v:+.1f}".replace("-", "\u2212"), color=c, fontsize=7.6, ha=ha, va="center", zorder=5)
    ax1.text(1961, -14.6, T("三条线每年相加等于零：一个部门借出的，就是其他部门借入的",
                            "The three lines add up to zero every year:\nwhat one sector lends, the others borrow"),
             fontsize=7.6, color=MUTED, ha="left", va="bottom")
    ax1.set_xlim(1959, 2026)
    ax1.set_ylim(-16.5, 14.5)
    ax1.set_ylabel(T("占 GDP 的 %", "% of GDP"), fontsize=9)
    _grid(ax1)
    ax1.tick_params(labelsize=8.5)
    _title(ax1, T("(a) 美国各部门的净借出（+）与净借入（−）", "(a) US net lending (+) and borrowing (−) by sector"))

    ax2.bar(sd.index, sd.values, width=0.75, color=[tint(INSTIT, 0.75) if v >= 0 else tint(INSTIT, 0.4) for v in sd],
            zorder=3)
    ax2.axhline(0, color=INK, lw=0.6, zorder=2)
    for y, va in [(sd.idxmax(), "bottom"), (sd.idxmin(), "top")]:
        v = sd[y]
        ax2.text(y + 0.8, v, f"{y}: {v:+.1f}".replace("-", "\u2212"), fontsize=7.6, color=INSTIT, ha="left", va=va)
    ax2.text(1961, 2.0, T("GDP − GDI，占 GDP 的 %", "GDP − GDI, % of GDP"), fontsize=7.6, color=MUTED, ha="left", va="top")
    ax2.set_xlim(1959, 2026)
    ax2.set_ylim(-2.2, 2.8)
    _grid(ax2)
    ax2.tick_params(labelsize=8.5)
    _title(ax2, T("(b) 支出法与收入法之差：统计误差", "(b) Expenditure less income: the statistical discrepancy"))
    return fig


@figure("accounts_china")
def accounts_china():
    D = C.china_revision(C.facts())
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIG_W, 2.75), gridspec_kw=dict(width_ratios=[1.0, 1.15], wspace=0.32))
    names = [T("第一产业", "primary"), T("第二产业", "secondary"), T("第三产业", "tertiary")]
    old = [D.p1_old[2004], D.p2_old[2004], D.p3_old[2004]]
    new = [D.p1_new[2004], D.p2_new[2004], D.p3_new[2004]]
    x = range(3)
    ax1.bar([i - 0.18 for i in x], [v / 1e4 for v in old], width=0.34, color="white", edgecolor=AMBER, hatch="////",
            lw=1.0, zorder=3)
    ax1.bar([i + 0.18 for i in x], [v / 1e4 for v in new], width=0.34, color=OUTPUT, edgecolor="white", zorder=3)
    for i in x:
        ax1.text(i + 0.18, new[i] / 1e4 + 0.15, f"{new[i] / 1e4:.1f}", ha="center", va="bottom", fontsize=7.6,
                 color=OUTPUT)
        ax1.text(i - 0.18, old[i] / 1e4 + 0.15, f"{old[i] / 1e4:.1f}", ha="center", va="bottom", fontsize=7.6,
                 color=AMBER)
    ax1.text(-0.32, 8.6, T("普查前（快报）", "before (preliminary)"), color=AMBER, fontsize=7.8, ha="left")
    ax1.text(-0.32, 7.8, T("普查后", "after"), color=OUTPUT, fontsize=7.8, ha="left")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(names, fontsize=8.5)
    ax1.set_ylim(0, 9.2)
    ax1.set_ylabel(T("万亿元", "trillion yuan"), fontsize=9)
    _grid(ax1)
    ax1.tick_params(labelsize=8.5)
    _title(ax1, T("(a) 2004 年：多出来的几乎都是服务业", "(a) 2004: nearly all services"))

    yrs = list(D.index)
    ax2.plot(yrs, D.rev_pct, color=OUTPUT, lw=2.0, **DOT, mfc=OUTPUT, zorder=3)
    for y, dx, ha in ((1993, 0.0, "center"), (1998, -0.35, "right"), (2004, 0.0, "center")):
        ax2.text(y + dx, D.rev_pct[y] + 0.9, f"{D.rev_pct[y]:.1f}%", color=OUTPUT, fontsize=7.6, ha=ha, va="bottom")
    ax2.text(1993.0, 15.0, T(f"各年上调的部分中，第三产业占\n{D.tertiary_share.min():.1f}%—{D.tertiary_share.max():.1f}%",
                             f"Services make up {D.tertiary_share.min():.1f}–{D.tertiary_share.max():.1f}%\nof each year's revision"),
             fontsize=7.6, color=INK, ha="left", va="center")
    ax2.set_xticks([1993, 1996, 1999, 2002, 2004])
    ax2.set_xlim(1992.3, 2004.8)
    ax2.set_ylim(0, 19.5)
    ax2.set_ylabel(T("GDP 上调幅度（%）", "upward revision of GDP (%)"), fontsize=9)
    _grid(ax2)
    ax2.tick_params(labelsize=8.5)
    _title(ax2, T("(b) 离普查年越近，修订越大", "(b) Larger near the census year"))
    return fig
