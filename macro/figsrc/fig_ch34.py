"""Figures for Chapter 34 (战争财政、功能财政与布雷顿森林的设计).

Style as in fig_ch33.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series, no legends. Government spending, receipts and debt are FISCAL (receipts, the second series of a
panel, AMBER, dashed); output and capacity OUTPUT; the inflationary gap PRICE; the charges of the two plans MONEY (the
debtor AMBER); quotas and votes EXTERNAL (votes a lighter shade); the two world wars a light tint; reference lines
MUTED. All numbers come from checks/check_ch34.py: the teaching model of the gap (model(), cross()), the Bank of
England's workbook (boe()), Historical Statistics (budget(), debt_ratio()), the charges of ex:warfinance-bancor
(keynes_charge(), white_charge()) and Schedule A of the Final Act (quotas(), votes()).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch34 as C
from check_ch32 import M1
from style import (
    AMBER,
    EXTERNAL,
    FIG_W,
    FISCAL,
    INK,
    LIGHT,
    MONEY,
    MUTED,
    OUTPUT,
    PRICE,
    ZH,
    T,
    clean_axes,
    figure,
    halo,
    tint,
)

DOT = dict(marker="o", ms=5, mec="white", mew=0.6)
SQUARE = dict(marker="s", ms=4.4, mec="white", mew=0.5)
WARS = ((1914, 1918), (1939, 1945))


def _title(ax, s):
    ax.set_title(s, fontsize=9.0, weight="bold", loc="left", pad=4)


def _grid(ax, axis="y"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


def _text(ax, x, y, s, color, ha="left", va="center", weight="normal", size=7.8):
    lab = ax.text(x, y, s, color=color, fontsize=size, ha=ha, va=va, weight=weight, linespacing=1.3, zorder=8)
    halo(lab, 2.0)
    return lab


def _wars(ax, top):
    """The two world wars (calendar years), a light tint with their names at the top."""
    for (a, b), name in zip(WARS, (T("一战", "WWI"), T("二战", "WWII"))):
        ax.axvspan(a - 0.5, b + 0.5, color=tint(MUTED, 0.1), lw=0, zorder=0)
        _text(ax, (a + b) / 2, top, name, MUTED, ha="center", va="top", size=7.6)


def _fmt(x: float) -> str:
    return f"{x:.0f}" if abs(x - round(x)) < 1e-9 else f"{x:.1f}"


@figure("warfinance_gap")
def warfinance_gap():
    """The cross of ex:warfinance-cross turned round at capacity: the spending lines of peace (= war with deferred pay),
    of war and of war with taxes at 30; the gaps at capacity (PRICE) are 20 and 8."""
    M = C.model()
    pe, wa, ta, de = M["peace"], M["war"], M["taxed"], M["deferred"]
    Yb, c = C.GAP["Ybar"], M1["c"]
    assert abs(de["b0"] - pe["b0"]) < 1e-9 and abs(wa["gap"] - 20) < 1e-9 and abs(ta["gap"] - 8) < 1e-9
    fig, ax = plt.subplots(figsize=(FIG_W, 3.1))
    fig.subplots_adjust(left=0.09, right=0.78 if ZH else 0.76, top=0.97, bottom=0.14)
    Y = np.linspace(60, 130, 200)
    ax.plot(Y, Y, color=INK, lw=1.0, zorder=3)
    _text(ax, 77, 75, T("产出 = 支出", "output = spending"), INK, va="top", size=7.6)
    ax.axvline(Yb, color=OUTPUT, lw=1.2, ls=(0, (1, 2)), zorder=2)
    _text(ax, Yb + 1, 62, T(f"产能 {Yb}", f"capacity {Yb}"), OUTPUT, va="bottom", size=7.6)
    lines = ((wa, FISCAL, 2.0, None, T("战时", "war")),
             (ta, AMBER, 1.8, (4, 2), T(f"税收加到 {C.GAP['Tw']}", f"taxes {C.GAP['Tw']}")),
             (pe, tint(FISCAL, 0.5), 1.6, None, T("和平时期", "peace")))
    for m, col, lw, dash, name in lines:
        kw = dict(dashes=dash) if dash else {}
        ax.plot(Y, m["b0"] + c * Y, color=col, lw=lw, zorder=5, **kw)
        _text(ax, 131.5, m["b0"] + c * 130, f"{name}：{_fmt(m['b0'])}+{c}$Y$" if ZH else
              f"{name}: {_fmt(m['b0'])}+{c}$Y$", col if m is not pe else tint(FISCAL, 0.75), size=7.6,
              weight="bold" if m is wa else "normal")
    # the gaps at capacity
    for m, x, col in ((wa, Yb - 2.2, PRICE), (ta, Yb + 2.2, PRICE)):
        ax.annotate("", xy=(x, m["at"]), xytext=(x, Yb), zorder=6,
                    arrowprops=dict(arrowstyle="<->", color=col, lw=1.0, shrinkA=0, shrinkB=0, mutation_scale=7))
    _text(ax, Yb - 3.4, (Yb + wa["at"]) / 2, T(f"缺口 {_fmt(wa['gap'])}", f"gap {_fmt(wa['gap'])}"), PRICE, ha="right",
          size=7.6, weight="bold")
    _text(ax, Yb + 3.4, (Yb + ta["at"]) / 2 - 1.5, T(f"缺口 {_fmt(ta['gap'])}", f"gap {_fmt(ta['gap'])}"), PRICE,
          size=7.6, weight="bold")
    for m, col in ((wa, FISCAL), (ta, AMBER)):
        ax.plot([Yb], [m["at"]], color=col, zorder=7, ls="none", **(DOT if col == FISCAL else SQUARE))
    ax.plot([Yb], [Yb], color=INK, zorder=7, ls="none", **DOT)
    D = M["D"]["D"]
    _text(ax, 62, 140, T(f"税收 {C.GAP['Tw']} 之外再加延期支付 {D:.1f}，\n支出线回到和平时期的位置",
                         f"with taxes at {C.GAP['Tw']}, deferred pay of {D:.1f}\nreturns the line to peace"),
          tint(FISCAL, 0.75), va="top", size=7.6)
    ax.set_xlim(60, 130)
    ax.set_ylim(60, 142)
    ax.set_xticks([60, 80, 100, 120])
    ax.set_yticks([60, 80, 100, 120])
    ax.set_xlabel(T("收入 $Y$", "income $Y$"))
    ax.set_ylabel(T("计划的支出", "planned spending"))
    _grid(ax)
    return fig


@figure("warfinance_budgets")
def warfinance_budgets():
    """(a) British central government expenditure and receipts, per cent of GDP, calendar years 1913-1950 (BoE A27);
    (b) US federal outlays and receipts, billion dollars, fiscal years 1939-1950 (Historical Statistics Y 339-340)."""
    B = C.boe()
    U = C.budget()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 3.0))
    fig.subplots_adjust(left=0.08, right=0.985, top=0.86, bottom=0.15, wspace=0.26)
    x = B.index.values
    _wars(a1, 69)
    a1.plot(x, B.cy_expenditure_pct_gdp, color=FISCAL, lw=2.0, zorder=5)
    a1.plot(x, B.cy_receipts_pct_gdp, color=AMBER, lw=1.6, dashes=(4, 2), zorder=5)
    pk = int(B.cy_expenditure_pct_gdp.loc[1939:1945].idxmax())
    a1.plot([pk], [B.cy_expenditure_pct_gdp[pk]], color=FISCAL, zorder=7, ls="none", **DOT)
    _text(a1, pk + 1.2, B.cy_expenditure_pct_gdp[pk] + 1, f"{B.cy_expenditure_pct_gdp[pk]:.1f}%", FISCAL, va="bottom",
          size=7.6)
    a1.plot([pk], [B.cy_receipts_pct_gdp[pk]], color=AMBER, zorder=7, ls="none", **SQUARE)
    _text(a1, pk - 1.0, B.cy_receipts_pct_gdp[pk] + 1.0, f"{B.cy_receipts_pct_gdp[pk]:.1f}%", AMBER, ha="right",
          va="bottom", size=7.6)
    _text(a1, 1925, 30, T("支出", "expenditure"), FISCAL, ha="center", weight="bold", size=7.6)
    _text(a1, 1928, 13, T("收入", "receipts"), AMBER, ha="center", size=7.6)
    a1.set_xlim(1912, 1951)
    a1.set_ylim(0, 70)
    a1.set_xticks([1915, 1925, 1935, 1945])
    a1.set_yticks([0, 20, 40, 60])
    a1.set_ylabel(T("占 GDP 的 %", "% of GDP"))
    a1.set_xlabel(T("年份", "year"))
    _grid(a1)
    _title(a1, T("(a) 英国：二战时收入跟得更紧", "(a) UK: receipts kept closer in WWII"))
    assert 55 < B.cy_expenditure_pct_gdp[pk] < 65 and B.cy_receipts_pct_gdp[pk] < 40
    assert C.fy_share(1939, 1945) > C.fy_share(1914, 1918) + 20

    y = U.index.values
    a2.set_xlim(1938.4, 1950.6)
    a2.plot(y, U.outlays, color=FISCAL, lw=2.0, zorder=5, **DOT)
    a2.plot(y, U.receipts, color=AMBER, lw=1.6, dashes=(4, 2), zorder=5, **SQUARE)
    top = int(U.outlays.idxmax())
    _text(a2, top + 0.4, U.outlays[top] + 1, f"{U.outlays[top]:.1f}", FISCAL, va="bottom", size=7.6)
    _text(a2, 1946.8, 63, T("支出", "outlays"), FISCAL, weight="bold", size=7.6)
    _text(a2, 1946.8, 30, T("收入", "receipts"), AMBER, size=7.6)
    a2.set_ylim(0, 105)
    a2.set_xticks([1940, 1943, 1946, 1949])
    a2.set_yticks([0, 25, 50, 75, 100])
    a2.set_ylabel(T("十亿美元", "billion dollars"))
    a2.set_xlabel(T("财政年度", "fiscal year"))
    _grid(a2)
    _title(a2, T("(b) 美国：收入只付了战时支出的一半弱", "(b) US: receipts paid under half"))
    w = U.loc[1942:1945]
    assert 0.4 < w.receipts.sum() / w.outlays.sum() < 0.5 and top == 1945
    return fig


@figure("warfinance_debt")
def warfinance_debt():
    """(a) The British national debt, per cent of GDP, 1913-1950 (BoE A29); (b) the US federal debt at the end of the
    fiscal year over the GDP of the calendar year, 1939-1950 (the book's calculation)."""
    B = C.boe()
    R = C.debt_ratio()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 3.0))
    fig.subplots_adjust(left=0.095, right=0.985, top=0.86, bottom=0.15, wspace=0.26)
    d = B.debt_pct_gdp
    _wars(a1, 290)
    a1.plot(d.index.values, d.values, color=FISCAL, lw=2.0, zorder=5)
    marks = ((1913, 1913.9, d[1913], "left", "center"), (1919, 1919, d[1919] + 10, "center", "bottom"),
             (1938, 1938, d[1938] - 12, "center", "top"), (1946, 1946.6, d[1946] + 6, "left", "bottom"))
    for yr, x, y, ha, va in marks:
        a1.plot([yr], [d[yr]], color=FISCAL, zorder=7, ls="none", **DOT)
        _text(a1, x, y, f"{yr}\n{d[yr]:.0f}%", FISCAL, ha=ha, va=va, size=7.6)
    a1.set_xlim(1912, 1951)
    a1.set_ylim(0, 290)
    a1.set_xticks([1915, 1925, 1935, 1945])
    a1.set_yticks([0, 100, 200])
    a1.set_ylabel(T("占 GDP 的 %", "% of GDP"))
    a1.set_xlabel(T("年份", "year"))
    _grid(a1)
    _title(a1, T("(a) 英国：两次大战各抬高一大截", "(a) UK: each war added a step"))
    assert d.idxmax() == 1946 and d[1919] > 4 * d[1913]

    a2.set_xlim(1938.4, 1950.6)
    a2.plot(R.index.values, R.values, color=FISCAL, lw=2.0, zorder=5, **DOT)
    _text(a2, 1939.25, R[1939] + 5, f"{R[1939]:.0f}%", FISCAL, va="bottom", size=7.6)
    _text(a2, 1946.45, R[1946] + 1, f"{R[1946]:.0f}%", FISCAL, va="center", size=7.6)
    a2.set_ylim(0, 130)
    a2.set_xticks([1940, 1943, 1946, 1949])
    a2.set_yticks([0, 40, 80, 120])
    a2.set_ylabel(T("占 GDP 的 %", "% of GDP"))
    a2.set_xlabel(T("财政年度末", "end of fiscal year"))
    _grid(a2)
    _title(a2, T("(b) 美国：联邦债务超过了 GDP", "(b) US: federal debt above GDP"))
    assert R.idxmax() == 1946 and R[1946] > 100
    return fig


@figure("warfinance_plans")
def warfinance_plans():
    """(a) The charges of ex:warfinance-bancor (quota 400, balances 250, the Fund's excess holdings 150): the creditor
    MONEY, the debtor AMBER; (b) the quotas of Schedule A and the votes (250 + 1 per $100,000) of the six largest
    members and of the other 38, per cent of the 44."""
    q, bal, ex = C.BANCOR["quota"], C.BANCOR["balance"], C.BANCOR["excess"]
    kc, kd = C.keynes_charge(bal, q), C.keynes_charge(-bal, q)
    wc, wd = C.white_charge(0), C.white_charge(ex)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 3.4), gridspec_kw=dict(width_ratios=[0.8, 1.2]))
    fig.subplots_adjust(left=0.08, right=0.985, top=0.86, bottom=0.15, wspace=0.62 if ZH else 0.7)
    xs = np.array([0, 1])
    h = 0.34
    a1.bar(xs - h / 2, [kc, wc], h, color=MONEY, zorder=4)
    a1.bar(xs + h / 2, [kd, wd], h, color=AMBER, zorder=4)
    for x0, v, col in ((0 - h / 2, kc, MONEY), (0 + h / 2, kd, AMBER), (1 - h / 2, wc, MONEY), (1 + h / 2, wd, AMBER)):
        _text(a1, x0, v + 0.06, f"{v:.1f}", col, ha="center", va="bottom", size=7.6)
    _text(a1, 0.62, 2.6, T("顺差国甲", "creditor"), MONEY, weight="bold", size=7.6)
    _text(a1, 0.62, 2.35, T("逆差国乙", "debtor"), AMBER, weight="bold", size=7.6)
    a1.set_xticks(xs)
    a1.set_xticklabels([T("凯恩斯方案", "Keynes plan"), T("怀特方案", "White plan")])
    a1.set_xlim(-0.6, 1.6)
    a1.set_ylim(0, 2.8)
    a1.set_yticks([0, 1, 2])
    a1.set_ylabel(T("每年的费用", "charge a year"))
    _grid(a1)
    _title(a1, T("(a) 凯恩斯也向顺差国收费", "(a) Keynes also charged creditors"))
    assert kc == kd > wd > wc == 0

    Qs = C.quotas()
    names = ["United States", "United Kingdom", "Union of Soviet Socialist Republics", "China", "France", "India"]
    zh = {"United States": "美国", "United Kingdom": "英国", "Union of Soviet Socialist Republics": "苏联",
          "China": "中国", "France": "法国", "India": "印度"}
    en = {"United States": "US", "United Kingdom": "UK", "Union of Soviet Socialist Republics": "USSR",
          "China": "China", "France": "France", "India": "India"}
    tq = sum(Qs.values())
    tv = sum(C.votes(v) for v in Qs.values())
    rest = [k for k in Qs if k not in names]
    qs = [100 * Qs[k] / tq for k in names] + [100 * sum(Qs[k] for k in rest) / tq]
    vs = [100 * C.votes(Qs[k]) / tv for k in names] + [100 * sum(C.votes(Qs[k]) for k in rest) / tv]
    labels = [T(zh[k], en[k]) for k in names] + [T(f"其余 {len(rest)} 国", f"other {len(rest)}")]
    yi = np.arange(len(labels))[::-1]
    hh = 0.44
    a2.barh(yi + hh / 2, qs, hh, color=EXTERNAL, zorder=4)
    a2.barh(yi - hh / 2, vs, hh, color=tint(EXTERNAL, 0.45), zorder=4)
    for y0, qv, vv in zip(yi, qs, vs):
        _text(a2, qv + 0.6, y0 + hh / 2 + 0.05, f"{qv:.1f}", EXTERNAL, va="center", size=7.6)
        _text(a2, vv + 0.6, y0 - hh / 2 - 0.05, f"{vv:.1f}", tint(EXTERNAL, 0.8), va="center", size=7.6)
    a2.set_yticks(yi)
    a2.set_yticklabels(labels)
    a2.set_xlim(0, 40)
    a2.set_xticks([0, 10, 20, 30])
    a2.set_xlabel(T("占 44 国合计的 %", "% of the 44 members"))
    _text(a2, 39, yi[1] + 0.3, T("份额", "quota"), EXTERNAL, ha="right", weight="bold", size=7.6)
    _text(a2, 39, yi[1] - 0.3, T("票数", "votes"), tint(EXTERNAL, 0.8), ha="right", weight="bold", size=7.6)
    _grid(a2, axis="x")
    _title(a2, T("(b) 每国 250 票使小国的票数多于份额", "(b) Basic votes favour small members"))
    assert len(rest) == 38 and vs[-1] > qs[-1] and vs[0] < qs[0]
    assert abs(vs[0] - 28.0) < 0.05
    return fig
