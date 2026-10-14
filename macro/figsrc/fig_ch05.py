"""Figures for Chapter 5 (国际收支与汇率).

Style as in fig_ch04.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series, the second series of a panel in AMBER, dashed. Colours follow §7: reserves, the balance of
payments, exchange rates and price levels EXTERNAL, capital flows and other items INSTIT, prices PRICE; the PBoC
swap of Sri Lanka and the reserve entries of the teaching example, the items the text is about, are AMBER. Every
number comes from checks/check_ch05.py, which reads the snapshots external_facts, cbsl_reserves, bis_fx,
wb_external_annual, fred_us_external, wb_price_levels and wb_relppp. BIS series carry the notice that the Chinese
labels are not an official BIS translation (in the captions of the text).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch05 as C  # noqa: E402
from style import (ACCENT, AMBER, EXTERNAL, FIG_W, INK, INSTIT, LIGHT, MUTED, T, arrow, canvas, clean_axes,  # noqa: E402
                   figure, label, pill, rbox, tint)

DOT = dict(marker="o", ms=5.0, mec="white", mew=0.6)
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


def _thousands(v, _pos=None) -> str:
    return f"{v:,.0f}".replace("-", MINUS)


def _months(index) -> pd.DatetimeIndex:
    return pd.to_datetime(pd.Index(index) + "-01")


def _years(ax, years):
    ax.set_xticks([pd.Timestamp(f"{y}-01-01") for y in years])
    ax.set_xticklabels([str(y) for y in years])


# ---------------------------------------------------------------------------
@figure("ext_srilanka")
def ext_srilanka():
    LR, B = C.lk_reserves(), C.bis()
    r = LR.loc["2018-01":"2026-07"]
    t = _months(r.index)
    gor = r.official_reserve_assets / 100                      # 亿美元
    swap = r.pboc_swap_bn.dropna() * 10                        # US$ bn -> 亿美元
    ts = _months(swap.index)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIG_W, 2.9), gridspec_kw=dict(width_ratios=[1.25, 1], wspace=0.28))

    ax1.fill_between(ts, 0, swap.values, step="mid", color=tint(AMBER, 0.40), lw=0, zorder=2)
    ax1.plot(t, gor, color=EXTERNAL, lw=1.9, zorder=3)
    ax1.text(pd.Timestamp("2024-04-01"), 3.0, T("其中：中国人民银行\n的互换（受使用\n条件限制）",
                                               "of which:\nPBoC swap\n(conditions\non use)"),
             fontsize=7.6, color=AMBER, ha="left", va="bottom", linespacing=1.25)
    lo = gor.idxmin()
    ax1.plot([pd.Timestamp(lo + "-01")], [gor.min()], color=EXTERNAL, zorder=4, **DOT)
    ax1.annotate(T(f"{_num(gor.min())} 亿美元\n2021 年 11 月", f"{_num(gor.min())}\nNov 2021"),
                 xy=(pd.Timestamp(lo + "-01"), gor.min()), xytext=(pd.Timestamp("2019-07-01"), 22),
                 fontsize=7.6, color=EXTERNAL, ha="center", va="center", linespacing=1.25,
                 arrowprops=dict(arrowstyle="-", color=EXTERNAL, lw=0.6))
    end = r.index[-1]
    ax1.text(pd.Timestamp(end + "-01"), gor.iloc[-1] + 6, T(f"{_num(gor.iloc[-1])}\n{end[:4]} 年 {int(end[5:])} 月",
                                                         f"{_num(gor.iloc[-1])}\n{pd.Timestamp(end + '-01'):%b %Y}"),
             fontsize=7.6, color=EXTERNAL, ha="right", va="bottom", linespacing=1.25)
    ax1.text(pd.Timestamp("2018-03-01"), 104, T("官方储备资产，月末", "official reserve assets, end of month"),
             fontsize=7.6, color=EXTERNAL, ha="left", va="top")
    ax1.set_ylim(0, 108)
    ax1.set_ylabel(T("亿美元", "100 million US$"), fontsize=9)
    _grid(ax1)
    _years(ax1, range(2018, 2027, 2))
    _title(ax1, T("(a) 两年里储备几乎耗尽", "(a) Reserves almost ran out in two years"))

    e = B.loc["2020-01":"2026-09", "lkr_usd_eop"]
    te = _months(e.index)
    ax2.plot(te, e.values, color=EXTERNAL, lw=1.9, zorder=3)
    for m, at, ha in (("2022-02", ("2020-02-01", 250), "left"), ("2022-04", ("2023-03-01", 372), "left")):
        v = B.loc[m, "lkr_usd_eop"]
        ax2.plot([pd.Timestamp(m + "-01")], [v], color=EXTERNAL, zorder=4, **DOT)
        ax2.annotate(T(f"{_num(v)}\n{m[:4]} 年 {int(m[5:])} 月末", f"{_num(v)}\nend-{pd.Timestamp(m + '-01'):%b %Y}"),
                     xy=(pd.Timestamp(m + "-01"), v), xytext=(pd.Timestamp(at[0]), at[1]),
                     fontsize=7.6, color=EXTERNAL, ha=ha, va="center", linespacing=1.25,
                     arrowprops=dict(arrowstyle="-", color=EXTERNAL, lw=0.6))
    ax2.set_ylim(150, 400)
    ax2.set_ylabel(T("卢比 / 美元", "rupees per US$"), fontsize=9)
    _grid(ax2)
    _years(ax2, range(2020, 2027, 2))
    dep = 100 * (B.loc["2022-02", "lkr_usd_eop"] / B.loc["2022-04", "lkr_usd_eop"] - 1)
    ax2.text(pd.Timestamp("2022-10-01"), 190, T(f"两个月里卢比的美元价值\n下降 {abs(dep):.1f}%",
                                               f"in two months the rupee\nlost {abs(dep):.1f}% of its\ndollar value"),
             fontsize=7.6, color=MUTED, ha="left", va="center", linespacing=1.25)
    _title(ax2, T("(b) 汇率放开后两个月，卢比贬值四成", "(b) Floated, the rupee lost 40%"))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.9, bottom=0.12)
    return fig


# ---------------------------------------------------------------------------
@figure("ext_bop")
def ext_bop():
    acc = C.entries_accounts(C.ENTRIES)
    W, H = 10.4, 5.4
    fig, ax = canvas(FIG_W, FIG_W * H / W, xlim=(0, W), ylim=(0, H))
    xl, xc, xf = 0.05, 2.05, 5.75              # left edges: transaction, current account, financial account
    wc, wf = 3.0, 4.6
    label(ax, xc + wc / 2, H - 0.25, T("经常账户（贷方 +，借方 −）", "current account (credit +, debit −)"), size=8.6,
          weight="bold", color=EXTERNAL)
    label(ax, xf + wf / 2, H - 0.25, T("金融账户（资产的增加，负债的增加）", "financial account (assets up, liabilities up)"),
          size=8.6, weight="bold", color=INSTIT)
    rows = [
        ("a", T("(a) 茶叶出口", "(a) tea exports"), T("出口  +100", "exports  +100"),
         [(T("资产：出口商的国外存款  +100", "asset: exporter's deposit abroad  +100"), INSTIT)]),
        ("b", T("(b) 进口石油", "(b) oil imports"), T("进口  −150", "imports  −150"),
         [(T("资产：储备  −150", "asset: reserves  −150"), AMBER)]),
        ("c", T("(c) 侨汇", "(c) remittances"), T("二次收入  +30", "secondary income  +30"),
         [(T("资产：银行的国外存款  +30", "asset: bank's deposit abroad  +30"), INSTIT)]),
        ("d", T("(d) 政府发债", "(d) government bond"), "—",
         [(T("资产：储备  +80", "asset: reserves  +80"), AMBER),
          (T("负债：政府债券  +80", "liability: government bond  +80"), INSTIT)]),
    ]
    h, gap, y0 = 0.78, 0.22, H - 0.65
    for k, (key, name, ca_txt, fa_items) in enumerate(rows):
        y = y0 - (k + 1) * h - k * gap
        label(ax, xl + 0.05, y + h / 2, name, size=8.2, ha="left", color=INK)
        rbox(ax, xc, y, wc, h, fc=tint(EXTERNAL, 0.10), ec=tint(EXTERNAL, 0.6), lw=0.8, r=0.08)
        label(ax, xc + wc / 2, y + h / 2, ca_txt, size=8.2, color=EXTERNAL if ca_txt != "—" else MUTED)
        n = len(fa_items)
        sub = (h - 0.06 * (n - 1)) / n
        for j, (txt, col) in enumerate(fa_items):
            yy = y + h - (j + 1) * sub - j * 0.06
            rbox(ax, xf, yy, wf, sub, fc=tint(col, 0.12), ec=tint(col, 0.65), lw=0.8, r=0.08)
            label(ax, xf + wf / 2, yy + sub / 2, txt, size=7.9, color=col if col == AMBER else INK)
        if ca_txt != "—":
            arrow(ax, (xc + wc + 0.08, y + h / 2), (xf - 0.08, y + h / 2), color=MUTED, lw=1.0, style="<|-|>", ms=7)
        else:
            arrow(ax, (xf - 0.1, y + h * 0.75), (xf - 0.1, y + h * 0.25), color=MUTED, lw=1.0,
                  style="<|-|>", ms=7, connectionstyle="arc3,rad=0.6")
    yt = 0.12
    pill(ax, xc + wc / 2, yt + 0.25, T(f"CA = 100 − 150 + 30 = {_num(acc['ca'], '.0f')}",
                                       f"CA = 100 − 150 + 30 = {_num(acc['ca'], '.0f')}"), color=EXTERNAL, size=8.0)
    pill(ax, xf + wf / 2, yt + 0.25, T(f"FA = 资产 {acc['dA']:.0f} − 负债 {acc['dL']:.0f} = {_num(acc['fa'], '.0f')}；"
                                       f"储备 {_num(acc['reserves'], '.0f')}",
                                       f"FA = assets {acc['dA']:.0f} − liabilities {acc['dL']:.0f} = "
                                       f"{_num(acc['fa'], '.0f')}; reserves {_num(acc['reserves'], '.0f')}"),
         color=INSTIT, size=8.0)
    return fig


# ---------------------------------------------------------------------------
@figure("ext_us")
def ext_us():
    U = C.us_external()
    pos = U[["IIPUSASSQ", "IIPUSLIAQ", "IIPUSNETIQ"]].dropna() / 1000          # 万亿美元
    t = pd.to_datetime(pos.index)
    pi = C.primary_income_annual(U) * 10                                       # 亿美元
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIG_W, 2.9), gridspec_kw=dict(width_ratios=[1, 1.1], wspace=0.3))
    ax1.fill_between(t, pos.IIPUSASSQ, pos.IIPUSLIAQ, color=tint(INSTIT, 0.16), lw=0, zorder=1)
    ax1.plot(t, pos.IIPUSASSQ, color=EXTERNAL, lw=1.9, zorder=3)
    ax1.plot(t, pos.IIPUSLIAQ, color=AMBER, lw=1.9, dashes=(4, 2), zorder=3)
    ax1.text(pd.Timestamp("2013-06-01"), 34, T("负债", "liabilities"), color=AMBER, fontsize=7.8, ha="center")
    ax1.text(pd.Timestamp("2016-06-01"), 17.5, T("资产", "assets"), color=EXTERNAL, fontsize=7.8, ha="center")
    last = pos.iloc[-1]
    ax1.annotate(T(f"净负债\n{_num(-last.IIPUSNETIQ)} 万亿", f"net liabilities\n{_num(-last.IIPUSNETIQ)} tn"),
                 xy=(t[-1], (last.IIPUSASSQ + last.IIPUSLIAQ) / 2), xytext=(pd.Timestamp("2019-01-01"), 62),
                 fontsize=7.6, color=INK, ha="center", va="center", linespacing=1.25,
                 arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    ax1.set_ylim(0, 75)
    ax1.set_ylabel(T("万亿美元", "US$ trillion"), fontsize=9)
    _grid(ax1)
    _years(ax1, range(2006, 2027, 5))
    _title(ax1, T("(a) 负债比资产涨得快", "(a) Liabilities grew faster than assets"))

    cols = [EXTERNAL if v >= 0 else AMBER for v in pi.values]
    ax2.bar(pi.index, pi.values, width=0.75, color=cols, zorder=3)
    ax2.axhline(0, color=INK, lw=0.7, zorder=4)
    ax2.annotate(_thousands(pi[2019]), xy=(2019, pi[2019]), xytext=(2021.6, 2800), fontsize=7.6, color=EXTERNAL,
                 ha="center", va="center", arrowprops=dict(arrowstyle="-", color=EXTERNAL, lw=0.6))
    ax2.annotate(_thousands(pi[2023]), xy=(2023, pi[2023]), xytext=(2024.6, 900), fontsize=7.6, color=EXTERNAL,
                 ha="center", va="center", arrowprops=dict(arrowstyle="-", color=EXTERNAL, lw=0.6))
    ax2.text(2024, pi[2024] - 60, _thousands(pi[2024]), fontsize=7.6, ha="center", va="top", color=AMBER)
    ax2.set_xlim(1998.2, 2025.8)
    ax2.set_ylim(-1000, 3000)
    ax2.yaxis.set_major_formatter(FuncFormatter(_thousands))
    ax2.set_ylabel(T("亿美元", "100 million US$"), fontsize=9)
    ax2.set_xticks(range(2000, 2026, 5))
    _grid(ax2)
    ax2.text(1998.6, 2400, T(f"初次收入差额\n{pi.index[0]}—2023 年\n每年为正", f"primary income\npositive every\n"
                                                                  f"year, {pi.index[0]}–2023"),
             fontsize=7.6, color=MUTED, ha="left", va="top", linespacing=1.25)
    _title(ax2, T("(b) 净收益到 2024 年才变成净支出", "(b) Net income negative only from 2024"))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.9, bottom=0.12)
    return fig


# ---------------------------------------------------------------------------
def _stacked(ax, x, layers, width=0.8):
    """Bars stacked upward for positive and downward for negative values."""
    up, down = np.zeros(len(x)), np.zeros(len(x))
    for v, col in layers:
        v = np.asarray(v, dtype=float)
        pos, neg = np.where(v > 0, v, 0), np.where(v < 0, v, 0)
        ax.bar(x, pos, bottom=up, width=width, color=col, lw=0, zorder=3)
        ax.bar(x, neg, bottom=down, width=width, color=col, lw=0, zorder=3)
        up, down = up + pos, down + neg


@figure("ext_china")
def ext_china():
    W, B = C.wdi(), C.bis()
    cn = W.loc["CHN"].loc[2003:2025] * 10                                     # 亿美元
    x = cn.index.values
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIG_W, 3.1), gridspec_kw=dict(width_ratios=[1.2, 1], wspace=0.3))
    _stacked(ax1, x, [(cn.ca, EXTERNAL), (-cn.nrfa, INSTIT), (cn.eo, tint(INSTIT, 0.35))])
    ax1.plot(x, cn.res_bop, color=INK, lw=0, marker="D", ms=3.6, mec="white", mew=0.4, zorder=5)
    ax1.axhline(0, color=INK, lw=0.7, zorder=4)
    for y, colour, text in ((9700, EXTERNAL, T("经常账户", "current account")),
                            (8800, INSTIT, T("非储备性质的资本净流入", "non-reserve capital inflow")),
                            (7900, tint(INSTIT, 0.35), T("净误差与遗漏", "errors and omissions"))):
        ax1.plot([2003.5], [y], color=colour, lw=0, marker="s", ms=5.0, mec="none")
        ax1.text(2004.1, y, text, color=INK, fontsize=7.6, ha="left", va="center")
    ax1.plot([2003.5], [7000], color=INK, lw=0, marker="D", ms=3.6, mec="white", mew=0.4)
    ax1.text(2004.1, 7000, T("储备资产的交易 = 三者之和", "reserve transactions = their sum"), color=INK, fontsize=7.6,
             ha="left", va="center")
    st = W.loc["CHN"].reserves * 10
    ax1.text(2003.0, -5600, T(f"年末储备（含黄金）：\n2003 年 {_thousands(st[2003])} 亿\n2014 年 {_thousands(st[2014])} 亿\n"
                              f"2016 年 {_thousands(st[2016])} 亿",
                              f"reserves at year-end:\n2003 {_thousands(st[2003])}\n2014 {_thousands(st[2014])}\n"
                              f"2016 {_thousands(st[2016])}"),
             fontsize=7.6, color=MUTED, ha="left", va="center", linespacing=1.25)
    ax1.set_xlim(2002.4, 2025.6)
    ax1.set_ylim(-9000, 10300)
    ax1.yaxis.set_major_formatter(FuncFormatter(_thousands))
    ax1.set_ylabel(T("亿美元", "100 million US$"), fontsize=9)
    ax1.set_xticks(range(2005, 2026, 5))
    _grid(ax1)
    _title(ax1, T("(a) 2015—2016 年顺差仍在，储备在减", "(a) A surplus, and still reserves fell"))

    e = B.loc["2000-01":"2026-08", ["cn_reer", "cn_neer"]]
    te = _months(e.index)
    ax2.plot(te, e.cn_reer, color=EXTERNAL, lw=1.7, zorder=3)
    ax2.plot(te, e.cn_neer, color=AMBER, lw=1.7, dashes=(4, 2), zorder=3)
    ax2.text(pd.Timestamp("2001-06-01"), 63, T("实际有效汇率", "real effective"), color=EXTERNAL, fontsize=7.8, ha="left")
    ax2.text(pd.Timestamp("2000-03-01"), 91, T("名义有效\n汇率", "nominal\neffective"), color=AMBER, fontsize=7.8,
             ha="left", va="bottom", linespacing=1.25)
    r21, r25 = C.year_avg(B.cn_reer, 2021), C.year_avg(B.cn_reer, 2025)
    n21, n25 = C.year_avg(B.cn_neer, 2021), C.year_avg(B.cn_neer, 2025)
    ax2.axvspan(pd.Timestamp("2021-01-01"), pd.Timestamp("2025-12-31"), color=tint(EXTERNAL, 0.10), lw=0, zorder=1)
    ax2.text(pd.Timestamp("2020-10-01"), 124, T(f"2021—2025 年\n名义 {100 * (n25 / n21 - 1):+.1f}%\n实际 "
                                               f"{_num(100 * (r25 / r21 - 1), '.1f')}%",
                                               f"2021–2025\nnominal {100 * (n25 / n21 - 1):+.1f}%\nreal "
                                               f"{_num(100 * (r25 / r21 - 1), '.1f')}%"),
             fontsize=7.6, color=INK, ha="right", va="top", linespacing=1.25)
    ax2.set_ylim(55, 128)
    ax2.set_ylabel(T("2020 年 = 100", "2020 = 100"), fontsize=9)
    _grid(ax2)
    _years(ax2, range(2000, 2027, 5))
    _title(ax2, T("(b) 实际汇率离开了名义汇率", "(b) Real rate parted from nominal"))
    fig.subplots_adjust(left=0.125, right=0.985, top=0.9, bottom=0.11)
    return fig


# ---------------------------------------------------------------------------
@figure("ext_ppp")
def ext_ppp():
    PL, _ = C.price_levels()
    RP, _ = C.relppp()
    r0 = C.regress(PL.x, PL.y)
    r20 = C.regress(RP.dx_2001_2021, RP.dy_2001_2021)
    r1 = C.regress(RP.dx_2020_2021, RP.dy_2020_2021)
    fig = plt.figure(figsize=(FIG_W, 4.55))
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1], hspace=0.5, wspace=0.28)
    ax0 = fig.add_subplot(gs[0, :])
    ax1, ax2 = fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])

    inc, lv = np.exp(PL.x), np.exp(PL.y)
    ax0.scatter(inc, lv, s=10, color=tint(EXTERNAL, 0.55), lw=0, zorder=3)
    xs = np.linspace(PL.x.min(), PL.x.max(), 50)
    ax0.plot(np.exp(xs), np.exp(r0.intercept + r0.slope * xs), color=AMBER, lw=1.6, dashes=(4, 2), zorder=4)
    ax0.axhline(1, color=MUTED, lw=0.7, ls=(0, (1.5, 2)), zorder=2)
    k = PL.set_index("iso3")
    names = {"CHN": T("中国", "China"), "LKA": T("斯里兰卡", "Sri Lanka"), "CHE": T("瑞士", "Switzerland"),
             "USA": T("美国", "US")}
    off = {"CHN": (0.0, 0.12, "center", "bottom"), "LKA": (0.0, -0.06, "center", "top"),
           "CHE": (0.0, 0.10, "center", "bottom"), "USA": (0.08, -0.13, "left", "top")}
    for iso, nm in names.items():
        xi, yi = np.exp(k.loc[iso, "x"]), np.exp(k.loc[iso, "y"])
        ax0.plot([xi], [yi], color=EXTERNAL, zorder=5, **dict(DOT, ms=4.6))
        dx, dy, ha, va = off[iso]
        ax0.text(xi * np.exp(dx), yi * np.exp(dy), f"{nm} {yi:.2f}", fontsize=7.6, color=EXTERNAL, ha=ha, va=va)
    ax0.text(0.012, 1.08, T(f"拟合线：弹性 {r0.slope:.2f}，$R^2$ = {r0.rvalue ** 2:.2f}，{len(PL)} 个经济体",
                            f"fit: elasticity {r0.slope:.2f}, $R^2$ = {r0.rvalue ** 2:.2f}, {len(PL)} economies"),
             fontsize=7.6, color=AMBER, ha="left", va="bottom")
    ax0.set_xscale("log")
    ax0.set_yscale("log")
    ax0.set_xlim(0.012, 2.4)
    ax0.set_ylim(0.18, 1.6)
    ax0.xaxis.set_major_locator(FixedLocator([0.02, 0.05, 0.1, 0.2, 0.5, 1, 2]))
    ax0.xaxis.set_minor_locator(NullLocator())
    ax0.xaxis.set_major_formatter(FuncFormatter(lambda v, _p: f"{v:g}"))
    ax0.yaxis.set_major_locator(FixedLocator([0.2, 0.3, 0.5, 0.7, 1.0, 1.5]))
    ax0.yaxis.set_minor_locator(NullLocator())
    ax0.yaxis.set_major_formatter(FuncFormatter(lambda v, _p: f"{v:g}"))
    ax0.set_xlabel(T("按购买力平价计的人均 GDP（美国 = 1）", "GDP per head at PPP (US = 1)"), fontsize=9)
    ax0.set_ylabel(T("价格水平（美国 = 1）", "price level (US = 1)"), fontsize=9)
    _grid(ax0, axis="both")
    _title(ax0, T("(a) 2021 年：越富的国家，价格水平越高", "(a) 2021: the richer the country, the higher its prices"))

    panels = (
        (ax1, RP.dx_2001_2021, RP.dy_2001_2021, r20, T("(b) 2001—2021 年：汇率跟着通胀差走",
                                                      "(b) 2001–2021: rates follow inflation"), (-0.6, 3.0), (-0.8, 3.1)),
        (ax2, RP.dx_2020_2021, RP.dy_2020_2021, r1, T("(c) 2020—2021 年：一年里看不出",
                                                     "(c) 2020–2021: no pattern in one year"), (-0.08, 0.18),
         (-0.18, 0.40)))
    for ax, dx, dy, r, ttl, xl, yl in panels:
        inside = dy <= yl[1]
        ax.scatter(dx[inside], dy[inside], s=9, color=tint(EXTERNAL, 0.55), lw=0, zorder=3)
        for xi, yi, iso in zip(dx[~inside], dy[~inside], RP.iso3[~inside]):      # beyond the frame: mark the edge
            ax.plot([xi], [yl[1] - 0.012 * (yl[1] - yl[0])], marker="^", ms=4.6, color=EXTERNAL, lw=0, zorder=5,
                    clip_on=False)
            nm = {"LBY": T("利比亚", "Libya")}.get(iso, iso)
            ax.text(xi + 0.015 * (xl[1] - xl[0]), yl[1] - 0.04 * (yl[1] - yl[0]), f"{nm} {yi:.2f}",
                    fontsize=7.6, color=EXTERNAL, ha="left", va="top")
        lo, hi = max(xl[0], yl[0]), min(xl[1], yl[1])
        ax.plot((lo, hi), (lo, hi), color=MUTED, lw=0.8, ls=(0, (1.5, 2)), zorder=2)
        xs = np.linspace(*xl, 20)
        ax.plot(xs, r.intercept + r.slope * xs, color=AMBER, lw=1.6, dashes=(4, 2), zorder=4)
        ax.set_xlim(*xl)
        ax.set_ylim(*yl)
        top = ax is ax1                                  # (c): the top-left corner holds Libya's marker
        ax.text(xl[0] + 0.03 * (xl[1] - xl[0]) if top else xl[1] - 0.03 * (xl[1] - xl[0]),
                yl[1] - 0.04 * (yl[1] - yl[0]) if top else yl[0] + 0.04 * (yl[1] - yl[0]),
                T(f"斜率 {r.slope:.2f}，$R^2$ = {r.rvalue ** 2:.2f}\n点线：45 度线",
                  f"slope {r.slope:.2f}, $R^2$ = {r.rvalue ** 2:.2f}\ndotted: 45° line"),
                fontsize=7.6, color=AMBER, ha="left" if top else "right", va="top" if top else "bottom",
                linespacing=1.25)
        ax.set_xlabel(T("对美国的通胀差（对数）", "inflation gap with the US (log)"), fontsize=9)
        _grid(ax, axis="both")
        _title(ax, ttl)
    ax1.set_ylabel(T("对美元汇率的变化（对数）", "change in the dollar rate (log)"), fontsize=9)
    kk = RP.set_index("iso3")
    for iso, nm, at in (("CHN", T("中国", "China"), (0.55, -0.55)), ("LKA", T("斯里兰卡", "Sri Lanka"), (1.45, 0.25))):
        xi, yi = kk.loc[iso, "dx_2001_2021"], kk.loc[iso, "dy_2001_2021"]
        ax1.plot([xi], [yi], color=EXTERNAL, zorder=5, **dict(DOT, ms=4.4))
        ax1.annotate(nm, xy=(xi, yi), xytext=at, fontsize=7.6, color=EXTERNAL, ha="left", va="center",
                     arrowprops=dict(arrowstyle="-", color=EXTERNAL, lw=0.6))
    fig.subplots_adjust(left=0.1, right=0.985, top=0.95, bottom=0.09)
    return fig
