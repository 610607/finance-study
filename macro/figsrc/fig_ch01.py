"""Figures for Chapter 1 (一个问题引出整门课).

Style as in fig_ch05.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series, the second series of a panel in AMBER, dashed. Colours follow §7: the government's
payments and its debt FISCAL, base money and interest rates MONEY, foreign currency and exchange rates EXTERNAL,
prices PRICE; the peg, which ties two paths together, AMBER. Every number comes from checks/check_ch01.py, which
reads the snapshots intro_facts, paper_money_facts, external_facts, prices_facts, bis_japan_govcredit,
bis_japan_govsec, boj_jgb_holders, mof_jgb_curves, wb_inflation_annual, cbr_rub_usd and cbsl_reserves; the reading
routes come from structure.py and check_ch01.ROUTES. BIS series carry the notice that the Chinese labels are not
an official BIS translation (in the captions of the text).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch01 as C  # noqa: E402
import structure  # noqa: E402
from style import (ACCENT, AMBER, CASE, EXTERNAL, FIG_W, FISCAL, INK, LIGHT, MONEY, MUTED, PRICE, ZH, T,  # noqa: E402
                   arrow, canvas, clean_axes, figure, label, rbox, tint)

MINUS = "−"
ZH_NUM = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一"]
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"]


def _title(ax, s):
    ax.set_title(s, fontsize=9.0, weight="bold", loc="left", pad=4)


def _grid(ax, axis="y"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=8.5)


def _num(v: float, fmt: str = ".1f") -> str:
    return f"{v:{fmt}}".replace("-", MINUS)


def _q(index) -> pd.DatetimeIndex:
    """'1997-Q4' -> the end of the quarter."""
    return pd.PeriodIndex(pd.Index(index).str.replace("-", ""), freq="Q").to_timestamp(how="end")


def _m(index) -> pd.DatetimeIndex:
    return pd.to_datetime(pd.Index(index) + "-01") + pd.offsets.MonthEnd(0)


# ---------------------------------------------------------------------------
@figure("intro_budget")
def intro_budget():
    F = C.facts()
    W, H = 10.4, 4.5
    fig, ax = canvas(FIG_W, FIG_W * H / W, xlim=(0, W), ylim=(0, H))
    # left: what has to be paid this period
    rbox(ax, 0.15, 1.05, 3.1, 2.4, fc=tint(ACCENT, 0.88), r=0.14)
    label(ax, 1.7, 2.95, T("这一期要付的钱", "to be paid this period"), color="white", size=9.6, weight="bold")
    label(ax, 1.7, 2.3, r"$G_t-T_t$", color="white", size=10.5)
    label(ax, 1.7, 1.85, r"$+\,i_{t-1}B_{t-1}+e_t\,i^{f}_{t-1}B^{f}_{t-1}$", color="white", size=9.6)
    label(ax, 1.7, 1.38, T("赤字加利息", "deficit plus interest"), color=tint(ACCENT, 0.25), size=8.0)
    label(ax, 3.65, 2.25, "=", size=16, color=INK)
    # right: the three sources
    paths = [
        (FISCAL, T("借本币", "borrow in own currency"), r"$\Delta B_t$",
         T("要有人买：代价是利率", "someone must buy: the cost is the interest rate"),
         T(f"俄罗斯 1998：卢布债券年收益率超过 {F['co_yield'][0]:.0f}%",
           f"Russia 1998: rouble bond yields above {F['co_yield'][0]:.0f}%")),
        (EXTERNAL, T("借外币", "borrow in foreign currency"), r"$e_t\,\Delta B^{f}_t$",
         T("要挣到或借到外汇", "foreign currency must be earned or borrowed"),
         T(f"斯里兰卡 2022：储备只够 {F['lk_gor_months'][0]:.1f} 个月的进口",
           f"Sri Lanka 2022: reserves for {F['lk_gor_months'][0]:.1f} months of imports")),
        (MONEY, T("发行货币", "issue money"), r"$\Delta H_t$",
         T("要有人愿意持有：代价是通胀", "someone must hold it: the cost is inflation"),
         T("明、魏玛、津巴布韦：没有人愿意持有", "Ming, Weimar, Zimbabwe: nobody would hold it")),
    ]
    x0, w, h, gap = 4.05, 6.2, 1.2, 0.3
    tops = []
    for k, (col, name, sym, cost, case) in enumerate(paths):
        y = H - 0.2 - (k + 1) * h - k * gap
        tops.append(y)
        rbox(ax, x0, y, w, h, fc=tint(col, 0.13), ec=tint(col, 0.6), lw=0.9, r=0.1)
        label(ax, x0 + 0.18, y + h - 0.29, name + "   " + sym, color=col, size=9.4, weight="bold", ha="left")
        label(ax, x0 + 0.18, y + 0.57, cost, color=INK, size=8.2, ha="left")
        label(ax, x0 + 0.18, y + 0.22, case, color=MUTED, size=7.7, ha="left")
        if k:
            label(ax, x0 + 1.2, y + h + gap / 2, "+", size=12, color=INK)
    # the peg ties 'issue money' to foreign currency
    ya, yb = tops[1] + 0.25, tops[2] + h - 0.25
    xa = x0 + w - 0.35
    arrow(ax, (xa, yb), (xa, ya), color=AMBER, lw=1.3, style="<|-|>", ms=8, ls=(0, (4, 2)))
    label(ax, xa - 0.12, (ya + yb) / 2 + 0.01, T("钉住汇率：印钱就是卖储备", "a peg: printing money sells reserves"),
          color=AMBER, size=7.7, ha="right")
    label(ax, 1.7, 0.6, T("合并的政府：财政部 + 中央银行", "consolidated government:\nTreasury + central bank"),
          color=MUTED, size=8.0)
    return fig


# ---------------------------------------------------------------------------
@figure("intro_japan")
def intro_japan():
    B = C.bis()
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(FIG_W, 2.75),
                                        gridspec_kw=dict(width_ratios=[1, 1.12, 1], wspace=0.42))
    t = _q(B.index)
    ax1.plot(t, B.nominal_pct, color=FISCAL, lw=2.0, zorder=3)
    ax1.plot(t, B.market_pct, color=AMBER, lw=1.7, dashes=(4, 2), zorder=3)
    pk = B.nominal_pct.idxmax()
    tp = _q([pk])[0]
    ax1.plot([tp], [B.nominal_pct[pk]], color=FISCAL, marker="o", ms=4.5, mec="white", mew=0.6, zorder=4)
    ax1.text(tp - pd.Timedelta(days=150), 229, T(f"{_num(B.nominal_pct[pk])}%\n{pk[:4]} 年末",
                                                 f"{_num(B.nominal_pct[pk])}%\nend-{pk[:4]}"),
             fontsize=7.6, color=FISCAL, ha="right", va="bottom", linespacing=1.2)
    last = B.index[-1]
    for col, c in (("nominal_pct", FISCAL), ("market_pct", AMBER)):
        ax1.text(t[-1] + pd.Timedelta(days=150), B[col][last], _num(B[col][last]), color=c, fontsize=7.6,
                 ha="left", va="center")
    ax1.text(pd.Timestamp("2019-01-01"), 180, T("面值", "nominal"), color=FISCAL, fontsize=7.8, ha="center")
    ax1.text(pd.Timestamp("2013-06-01"), 214, T("市值", "market"), color=AMBER, fontsize=7.8, ha="center")
    ax1.set_ylim(60, 262)
    ax1.set_xlim(pd.Timestamp("1997-01-01"), pd.Timestamp("2031-06-30"))
    ax1.set_ylabel(T("占 GDP 的 %", "% of GDP"), fontsize=9)
    _grid(ax1)
    ax1.set_xticks([pd.Timestamp(f"{y}-01-01") for y in (2000, 2010, 2020)])
    ax1.set_xticklabels(["2000", "2010", "2020"])
    _title(ax1, T("(a) 债务率 2020 年见顶", "(a) Debt peaked in 2020"))

    y10 = C.jgb10_monthly().loc["1990-01":]
    j = C.wdi()["JPN"].loc[1990:]
    ax2.bar([pd.Timestamp(f"{y}-07-01") for y in j.index], j.values, width=300, color=tint(PRICE, 0.45),
            zorder=2)
    ax2.plot(_m(y10.index), y10.values, color=MONEY, lw=1.6, zorder=3)
    ax2.axhline(0, color=INK, lw=0.6, zorder=4)
    ax2.text(pd.Timestamp("1996-01-01"), 5.6, T("十年期国债\n收益率", "10-year\nJGB yield"), color=MONEY,
             fontsize=7.6, ha="left", linespacing=1.2)
    ax2.text(pd.Timestamp("2008-01-01"), 3.4, T("消费价格\n年涨幅", "CPI\ninflation"), color=PRICE, fontsize=7.6,
             ha="center", linespacing=1.2)
    ax2.text(pd.Timestamp("2026-09-30"), y10.iloc[-1] + 0.35, _num(y10.iloc[-1], ".2f"), color=MONEY, fontsize=7.6,
             ha="right", va="bottom")
    ax2.set_ylim(-1.5, 9)
    ax2.set_ylabel("%", fontsize=9)
    _grid(ax2)
    ax2.set_xticks([pd.Timestamp(f"{y}-01-01") for y in (1990, 2000, 2010, 2020)])
    ax2.set_xticklabels(["1990", "2000", "2010", "2020"])
    _title(ax2, T("(b) 利率与通胀一起离开零", "(b) Rates, prices leave zero"))

    S = C.holders()
    tm = _m(S.index)
    ax3.plot(tm, S.central_bank, color=MONEY, lw=2.0, zorder=3)
    ax3.plot(tm, S.overseas, color=AMBER, lw=1.7, dashes=(4, 2), zorder=3)
    for m, dx, dy, ha, va in (("2012-03", 75, -1.2, "left", "top"), ("2023-09", 0, 3, "center", "bottom"),
                              (S.index[-1], 0, -4, "right", "top")):
        ax3.text(_m([m])[0] + pd.Timedelta(days=dx), S.central_bank[m] + dy, _num(S.central_bank[m], ".2f"),
                 color=MONEY, fontsize=7.6, ha=ha, va=va)
    ax3.set_xlim(pd.Timestamp("2011-01-01"), pd.Timestamp("2027-03-31"))
    ax3.text(_m([S.index[-1]])[0], S.overseas.iloc[-1] + 2.5, _num(S.overseas.iloc[-1], ".2f"), color=AMBER,
             fontsize=7.6, ha="right", va="bottom")
    ax3.text(pd.Timestamp("2016-06-01"), 41, T("日本银行", "Bank of\nJapan"), color=MONEY, fontsize=7.8, ha="right",
             linespacing=1.2)
    ax3.text(pd.Timestamp("2017-06-01"), 13, T("海外", "overseas"), color=AMBER, fontsize=7.8, ha="center")
    ax3.set_ylim(0, 62)
    ax3.set_ylabel(T("持有的 %", "% held"), fontsize=9)
    _grid(ax3)
    ax3.set_xticks([pd.Timestamp(f"{y}-01-01") for y in (2013, 2019, 2025)])
    ax3.set_xticklabels(["2013", "2019", "2025"])
    _title(ax3, T("(c) 日本银行持有近一半", "(c) The BoJ holds half"))
    fig.subplots_adjust(left=0.09, right=0.985, top=0.88, bottom=0.1)
    return fig


# ---------------------------------------------------------------------------
@figure("intro_scale")
def intro_scale():
    S = C.scale(C.facts())
    rows = [  # case, label, colour, value text
        ("ming", T("明：宝钞按铜钱计", "Ming: the note in copper cash"), PRICE,
         T("至少 1,000 倍", "at least 1,000 times")),
        ("weimar", T("魏玛：美元的马克价格", "Weimar: marks per dollar"), EXTERNAL,
         T(f"{S.factor['weimar'] / 1e12:.2f} 万亿倍", f"{S.factor['weimar'] / 1e12:.2f} trillion times")),
        ("zimbabwe", T("津巴布韦：去掉的零", "Zimbabwe: zeros removed"), MONEY, r"$10^{25}$"),
        ("russia", T("俄罗斯：美元的卢布价格", "Russia: roubles per dollar"), EXTERNAL,
         T(f"{S.factor['russia']:.2f} 倍；至 1999 年末 {S.factor['russia99']:.2f} 倍",
           f"{S.factor['russia']:.2f} times; to end-1999 {S.factor['russia99']:.2f}")),
        ("srilanka", T("斯里兰卡：美元的卢比价格", "Sri Lanka: rupees per dollar"), EXTERNAL,
         T(f"{S.factor['srilanka']:.2f} 倍", f"{S.factor['srilanka']:.2f} times")),
        ("japan", T("日本：消费价格水平", "Japan: consumer prices"), PRICE,
         T(f"{S.factor['japan']:.2f} 倍（35 年）", f"{S.factor['japan']:.2f} times (35 years)")),
    ]
    fig, ax = plt.subplots(figsize=(FIG_W, 2.55))
    ys = np.arange(len(rows))[::-1]
    for y, (k, name, col, txt) in zip(ys, rows):
        v = S.log10[k]
        ax.barh(y, v, height=0.62, color=col, zorder=3)
        if S.lower_bound[k]:
            arrow(ax, (v, y), (v + 1.6, y), color=col, lw=1.2, ms=8)
            v += 1.6
        ax.text(v + 0.35, y, txt, color=col, fontsize=7.8, va="center", ha="left")
    ax.set_yticks(ys)
    ax.set_yticklabels([r[1] for r in rows], fontsize=8.5)
    ax.set_xlim(0, 30.5)
    ax.set_xticks(range(0, 31, 5))
    ax.set_xticklabels([r"$10^{%d}$" % x if x else "1" for x in range(0, 31, 5)])
    ax.set_xlabel(T("贬值的倍数（对数刻度）", "times (log scale)"), fontsize=9)
    _grid(ax, axis="x")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    fig.subplots_adjust(left=0.29, right=0.985, top=0.97, bottom=0.17)
    return fig


# ---------------------------------------------------------------------------
@figure("intro_road")
def intro_road():
    R = C.routes()
    order = [("main", T("主线：危机—理论—检验", "crisis, theory, test"), ACCENT),
             ("money", T("钱为什么值钱", "why money has value"), MONEY),
             ("debt", T("政府能借多少", "how much to borrow"), FISCAL),
             ("fx", T("汇率与外债", "FX and foreign debt"), EXTERNAL),
             ("japan", T("日本", "Japan"), CASE)]
    fig, ax = plt.subplots(figsize=(FIG_W, 2.85))
    n_ch = len(structure.CHAPTERS)
    for k, (p, _key, _zh, _en, _per, a, b) in enumerate(structure.PARTS):
        if k % 2 == 0:
            ax.axvspan(a - 0.5, b + 0.5, color=tint(INK, 0.05), lw=0, zorder=0)
        ax.text((a + b) / 2, len(order) - 0.35, ZH_NUM[k] if ZH else ROMAN[k], ha="center", va="bottom",
                fontsize=8.0, color=MUTED)
    ys = np.arange(len(order))[::-1]
    for y, (key, name, col) in zip(ys, order):
        xs = [n for n, *_ in R[key]]
        ax.plot(xs, [y] * len(xs), color=tint(col, 0.5), lw=1.1, zorder=2)
        ax.plot(xs, [y] * len(xs), "o", color=col, ms=5.2, mec="white", mew=0.6, zorder=3)
        for i, x in enumerate(xs):
            ax.text(x, y + (0.2 if i % 2 == 0 else -0.2), str(x), ha="center", va="bottom" if i % 2 == 0 else "top",
                    fontsize=7.5, color=col)
    ax.set_yticks(ys)
    ax.set_yticklabels([o[1] for o in order], fontsize=8.5)
    for tl, (_k, _n, col) in zip(ax.get_yticklabels(), order):
        tl.set_color(col)
    ax.set_xlim(0.3, n_ch + 0.7)
    ax.set_ylim(-0.6, len(order) - 0.05)
    ax.set_xticks([])
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.text(-0.012, len(order) - 0.35, T("部分", "part"), transform=ax.get_yaxis_transform(), ha="right",
            va="bottom", fontsize=8.0, color=MUTED)
    fig.subplots_adjust(left=0.27, right=0.99, top=0.97, bottom=0.03)
    return fig
