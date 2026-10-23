"""Figures for Chapter 32 (凯恩斯《通论》).

Style as in fig_ch27.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series, no legends. Unemployment, output, consumption and investment are OUTPUT (a second series of a
panel AMBER, dashed; a third a lighter shade of OUTPUT), exports EXTERNAL, Bank Rate MONEY; reference lines MUTED.
All numbers come from checks/check_ch32.py: the Bank of England's millennium workbook (monthly(), annual(),
index_1929(), bank_rate()) and the teaching model M1 (cross(), model()).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch32 as C
from style import (
    AMBER,
    EXTERNAL,
    FIG_W,
    INK,
    LIGHT,
    MONEY,
    MUTED,
    OUTPUT,
    ZH,
    T,
    clean_axes,
    figure,
    halo,
    tint,
)

DOT = dict(marker="o", ms=5, mec="white", mew=0.6)
SQUARE = dict(marker="s", ms=4.2, mec="white", mew=0.5)


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


@figure("generaltheory_unemp")
def generaltheory_unemp():
    """Britain's administrative unemployment rate, monthly, 1919-1938 (gaps where the sheet is empty), with Feinstein's
    annual rate dashed, the broadcast of January 1931 as a dot and 1936 as a vertical line."""
    M = C.monthly()
    x = np.array([y + (m - 0.5) / 12 for y, m in M.index])
    u = M.unemp_admin.values
    A = C.annual()
    fe = A.unemp_rate_civilian.dropna()
    floor = C.admin_span(1921, 1938).min()
    peak = C.admin_span(1919, 1938).idxmax()
    top = C.admin_span(1932, 1933).idxmax()
    assert peak == (1921, 5) and top[0] == 1932
    fig, ax = plt.subplots(figsize=(FIG_W, 2.75))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.97, bottom=0.15)
    ax.axhline(floor, color=MUTED, lw=0.8, ls=(0, (1, 2)), zorder=2)
    ax.plot(x, u, color=OUTPUT, lw=2.0, zorder=5)
    ax.plot(fe.index + 0.5, fe.values, color=AMBER, lw=1.4, dashes=(4, 2), zorder=4, **SQUARE)
    # the broadcast and the book
    b = C.admin(1931, 1)
    ax.plot([1931 + 0.5 / 12], [b], color=INK, zorder=7, ls="none", **DOT)
    ax.annotate(T(f"凯恩斯的广播\n1931 年 1 月，{b:.1f}%", f"Keynes's broadcast\nJan 1931, {b:.1f}%"),
                xy=(1931 + 0.5 / 12, b), xytext=(1927.6, 26.2), fontsize=7.6, color=INK, ha="center", va="center",
                linespacing=1.3, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7), zorder=8)
    ax.axvline(1936, color=MUTED, lw=0.8, ls=(0, (1, 2)), zorder=2)
    _text(ax, 1936.15, 26.2, T("《通论》\n1936 年", "General Theory\n1936"), INK)
    # the peaks and the floor
    for (yy, mm), dy in ((peak, 0.5), (top, 0.5)):
        v = C.admin(yy, mm)
        _text(ax, yy + (mm - 0.5) / 12, v + dy, f"{v:.1f}", OUTPUT, ha="center", va="bottom", size=7.6)
    _text(ax, 1935.8, floor - 0.4, T(f"1921—1938 年最低的月份 {floor:.1f}%", f"lowest month of 1921-38: {floor:.1f}%"),
          MUTED, ha="right", va="top", size=7.6)
    _text(ax, 1922.6, 15.6, T("行政失业率\n（每月）", "administrative rate\n(monthly)"), OUTPUT, ha="left",
          weight="bold")
    _text(ax, 1923.8, 5.0, T("Feinstein 的年度失业率", "Feinstein's annual rate"), AMBER, ha="left")
    ax.set_xlim(1919, 1939)
    ax.set_ylim(0, 29)
    ax.set_xticks([1919, 1921, 1925, 1929, 1931, 1933, 1936, 1938])
    ax.set_xlabel(T("年份", "year"))
    ax.set_ylabel(T("失业率（%）", "unemployment rate (%)"))
    _grid(ax)
    return fig


@figure("generaltheory_cross")
def generaltheory_cross():
    """(a) The Keynesian cross of M1: spending C + I against the 45-degree line, investment 10 and 14; (b) saving
    S = Y - C before and after households cut consumption by 10 at every income, with investment fixed at 10 and with
    I = 1 + 0.1Y (amber, dashed)."""
    P, R = C.M1, C.model()
    a, c, I, I2, a2, i0, i1 = (P[k] for k in ("a", "c", "I", "I2", "a2", "i0", "i1"))
    fig, (a1, a2_) = plt.subplots(1, 2, figsize=(FIG_W, 2.95))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.86, bottom=0.15, wspace=0.27)

    y = np.linspace(0, 130, 200)
    a1.plot(y, y, color=MUTED, lw=0.9, ls=(0, (1, 2)), zorder=2)
    a1.plot(y, a + I + c * y, color=tint(OUTPUT, 0.5), lw=1.6, zorder=4)
    a1.plot(y, a + I2 + c * y, color=OUTPUT, lw=2.0, zorder=5)
    for Y0, col in ((R["Y"], tint(OUTPUT, 0.5)), (R["Y2"], OUTPUT)):
        a1.plot([Y0], [Y0], color=col, zorder=7, ls="none", **DOT)
        a1.plot([Y0, Y0], [0, Y0], color=col, lw=0.7, ls=(0, (1, 2)), zorder=3)
        _text(a1, Y0, 3, f"{Y0:.0f}", col, ha="center", va="bottom", size=7.6)
    _text(a1, 64, 58, T("45° 线", "45° line"), MUTED, va="top", size=7.6)
    _text(a1, 2, a + I2 + c * 18 + 2, f"$C+I$\n$I={I2}$", OUTPUT, va="bottom", size=7.6)
    _text(a1, 2, a + I + c * 2 - 4, f"$C+I$\n$I={I}$", tint(OUTPUT, 0.65), va="top", size=7.6)
    # the shift of 4 and the rise of income of 10
    xs = 112
    a1.annotate("", xy=(xs, a + I2 + c * xs), xytext=(xs, a + I + c * xs),
                arrowprops=dict(arrowstyle="-|>", color=OUTPUT, lw=0.9, mutation_scale=8), zorder=6)
    _text(a1, xs, a + I + c * xs - 3, f"+{I2 - I}", OUTPUT, ha="center", va="top", size=7.6)
    a1.annotate("", xy=(R["Y2"], 26), xytext=(R["Y"], 26),
                arrowprops=dict(arrowstyle="-|>", color=OUTPUT, lw=0.9, mutation_scale=8), zorder=6)
    _text(a1, R["Y2"] + 1.5, 26, T(f"收入\n+{R['Y2'] - R['Y']:.0f}", f"income\n+{R['Y2'] - R['Y']:.0f}"), OUTPUT,
          size=7.6)
    a1.set_xlim(0, 125)
    a1.set_ylim(0, 125)
    a1.set_xticks([0, 30, 60, 90, 120])
    a1.set_yticks([0, 30, 60, 90, 120])
    a1.set_xlabel(T("收入 $Y$", "income $Y$"))
    a1.set_ylabel(T("支出", "spending"))
    _grid(a1)
    _title(a1, T(f"(a) 投资增加 {I2 - I}，收入增加 {R['Y2'] - R['Y']:.0f}",
                 f"(a) Investment +{I2 - I}, income +{R['Y2'] - R['Y']:.0f}"))

    ax = a2_
    y = np.linspace(40, 120, 200)
    ax.plot(y, y - (a + c * y), color=tint(OUTPUT, 0.5), lw=1.6, zorder=4)
    ax.plot(y, y - (a2 + c * y), color=OUTPUT, lw=2.0, zorder=5)
    ax.plot(y, np.full_like(y, I), color=INK, lw=1.2, zorder=4)
    ax.plot(y, i0 + i1 * y, color=AMBER, lw=1.4, dashes=(4, 2), zorder=4)
    pts = ((R["Y"], R["Y"] - R["C"], INK, "below"), (R["Y3"], R["S3"], OUTPUT, "above"),
           (R["Y4"], R["S4"], AMBER, "below"))
    for Y0, S0, col, where in pts:
        ax.plot([Y0], [S0], color=col, zorder=7, ls="none", **(SQUARE if col == AMBER else DOT))
        ax.plot([Y0, Y0], [0, S0], color=col, lw=0.7, ls=(0, (1, 2)), zorder=3)
        _text(ax, Y0, 0.4, f"{Y0:.0f}" if abs(Y0 - round(Y0)) < 1e-9 else f"{Y0:.1f}", col, ha="center",
              va="bottom", size=7.6)
    _text(ax, R["Y4"] - 1.5, R["S4"] + 0.2, f"{R['S4']:.1f}", AMBER, ha="right", va="bottom", size=7.6)
    _text(ax, R["Y3"] - 1.5, R["S3"] + 0.3, f"{R['S3']:.0f}", OUTPUT, ha="right", va="bottom", size=7.6)
    _text(ax, 96, 16, T("原来的\n储蓄线", "saving\nbefore"), tint(OUTPUT, 0.65), ha="right", size=7.6)
    _text(ax, 79, 79 - (a2 + c * 79) + 1.2, T("更节俭的\n储蓄线", "saving,\nthriftier"), OUTPUT, ha="right",
          va="bottom", weight="bold", size=7.6)
    _text(ax, 119, I - 0.35, f"$I={I}$", INK, ha="right", va="top", size=7.6)
    _text(ax, 119, i0 + i1 * 119 + 0.4, f"$I={i0}+{i1}Y$", AMBER, ha="right", va="bottom", size=7.6)
    ax.set_xlim(40, 120)
    ax.set_ylim(0, 22)
    ax.set_xticks([40, 60, 80, 100])
    ax.set_xlabel(T("收入 $Y$", "income $Y$"))
    ax.set_ylabel(T("储蓄、投资", "saving, investment"))
    _grid(ax)
    _title(ax, T("(b) 想多储蓄，储蓄没有增加", "(b) More thrift, no more saving"))
    assert R["S3"] == I and R["S4"] < R["S3"]
    return fig


# the series of panel (a): column, names, colour, width, dashes, marker, label offset at 1938
UK = ((C.INV, ("投资", "investment"), OUTPUT, 2.0, None, DOT, 0),
      (C.CONS, ("消费", "consumption"), AMBER, 1.5, (4, 2), SQUARE, 0),
      (C.GDP, ("GDP", "GDP"), tint(OUTPUT, 0.55), 1.4, None, None, 0),
      (C.EXP, ("出口量", "exports"), EXTERNAL, 1.4, None, None, 0))


@figure("generaltheory_uk")
def generaltheory_uk():
    """(a) Britain's real GDP, consumption, investment and export volume, 1929 = 100, 1929-1938; (b) Bank Rate,
    1929-1939, as steps."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.9), gridspec_kw={"width_ratios": [1.35, 1]})
    fig.subplots_adjust(left=0.085, right=0.985, top=0.86, bottom=0.16, wspace=0.3)
    idx = {col: C.index_1929(col) for col, *_ in UK}
    a1.axhline(100, color=MUTED, lw=0.8, ls=(0, (1, 2)), zorder=2)
    a1.axvline(1932, color=MUTED, lw=0.8, ls=(0, (1, 2)), zorder=2)
    for col, names, colour, lw, dashes, mk, _ in UK:
        s = idx[col]
        kw = dict(color=colour, lw=lw, zorder=6 if col == C.INV else 4)
        if dashes:
            kw["dashes"] = dashes
        a1.plot(s.index, s.values, **kw, **(mk or {}))
    end = {col: idx[col][1938] for col, *_ in UK}
    # labels right of 1938, spread where the lines end close together
    order = sorted(end, key=end.get)
    ys, last = {}, -1e9
    for col in order:
        ys[col] = max(end[col], last + 6.5)
        last = ys[col]
    for col, names, colour, lw, *_ in UK:
        _text(a1, 1938.3, ys[col], T(*names), colour if colour != tint(OUTPUT, 0.55) else tint(OUTPUT, 0.75),
              weight="bold" if col == C.INV else "normal", size=7.6)
    lo = idx[C.EXP].idxmin()
    _text(a1, lo, idx[C.EXP][lo] - 2, f"{idx[C.EXP][lo]:.1f}", EXTERNAL, ha="center", va="top", size=7.6)
    lo_i = idx[C.INV].loc[1930:1934].idxmin()
    _text(a1, lo_i, idx[C.INV][lo_i] - 2, f"{idx[C.INV][lo_i]:.1f}", OUTPUT, ha="center", va="top", size=7.6)
    a1.set_xlim(1928.6, 1940.6 if ZH else 1941.4)
    a1.set_ylim(60, 135)
    a1.set_xticks([1929, 1932, 1935, 1938])
    a1.set_ylabel(T("1929 年 = 100", "1929 = 100"))
    _grid(a1)
    _title(a1, T("(a) 消费没有降，投资领先回升", "(a) Consumption held; investment led"))

    R = C.bank_rate()
    xs = np.array([d.year + (d.dayofyear - 1) / 365.25 for d in R.date] + [1940.0])
    ys_ = list(R.bank_rate) + [R.bank_rate.iloc[-1]]
    a2.step(xs, ys_, where="post", color=MONEY, lw=2.0, zorder=4)
    cut = R[R.bank_rate == 2.0].iloc[0]
    xc = cut.date.year + (cut.date.dayofyear - 1) / 365.25
    _text(a2, xc + 0.25, 2.0 + 0.35, T(f"{cut.bank_rate:g}%\n{cut.date.year} 年 {cut.date.month} 月 {cut.date.day} 日起",
                                         f"{cut.bank_rate:g}%\nfrom {cut.date.day} {cut.date:%b %Y}"), MONEY,
          va="bottom", size=7.6)
    peak = R.loc[R.date < "1930-01-01", "bank_rate"].max()
    _text(a2, 1929.85, peak + 0.25, f"{peak:g}%", MONEY, va="bottom", size=7.6)
    a2.set_xlim(1929, 1940)
    a2.set_ylim(0, 7.6)
    a2.set_xticks([1929, 1932, 1935, 1938])
    a2.set_ylabel(T("贴现率（%）", "Bank Rate (%)"))
    _grid(a2)
    end = R[R.date > cut.date].iloc[0].date
    _title(a2, T(f"(b) 贴现率 2%，保持到 {end.year} 年", f"(b) Bank Rate at 2% until {end.year}"))
    for ax in (a1, a2):
        ax.set_xlabel(T("年份", "year"))
    return fig
