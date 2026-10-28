"""Figures for Chapter 36 (布雷顿森林体系的运行).

Style as in fig_ch35.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series, no legends. The US gold stock is EXTERNAL; the dollar liabilities to foreigners are MONEY, those
to foreign official institutions a lighter shade of it, dashed; the cover ratios take the colour of their liabilities;
the line at 1 and at the parity of 1949 MUTED. The dollar values of the four currencies are EXTERNAL (exchange rates),
one small panel each, with the mark's floats in a light tint. All numbers come from checks/check_ch36.py: the
Statistical Abstract's tables (gold_series(), crossing()) and Bordo's Table 1.2 (parities(), floats()).
"""
from __future__ import annotations

import datetime
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch36 as C
from style import (
    EXTERNAL,
    FIG_W,
    LIGHT,
    MONEY,
    MUTED,
    ZH,
    T,
    clean_axes,
    figure,
    halo,
    tint,
)

DOT = dict(marker="o", ms=4.4, mec="white", mew=0.6)
OFFICIAL = tint(MONEY, 0.55)


def _title(ax, s):
    ax.set_title(s, fontsize=9.0, weight="bold", loc="left", pad=4)


def _grid(ax, axis="y"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


def _text(ax, x, y, s, color, ha="left", va="center", weight="normal", size=7.6):
    lab = ax.text(x, y, s, color=color, fontsize=size, ha=ha, va=va, weight=weight, linespacing=1.3, zorder=8)
    halo(lab, 2.0)
    return lab


def _line(ax, S, col, **kw):
    """A series of gold_series(): 1955 as a lone point, 1959-1971 as a line (the editions give no 1956-1958)."""
    later = S.loc[S.index >= 1959]
    ax.plot(later.index, later.values, zorder=5, **kw)
    style = {k: v for k, v in kw.items() if k in ("color",)}
    ax.plot([S.index[0]], [S.iloc[0]], ls="none", zorder=6, **style, **DOT)


@figure("brettonwoods_gold")
def brettonwoods_gold():
    """(a) The US gold stock, the short-term liabilities to foreigners and those to foreign official institutions, end
    of year, 1955 and 1959-1971, in hundred million dollars (zh) or billion dollars (en); (b) the cover ratios gold /
    liabilities, with the line at 1. Statistical Abstract of the United States 1964, 1968, 1972."""
    S = C.gold_series()
    scale = 100 if ZH else 1000
    G, Fo, Of = S["gold"] / scale, S["foreign"] / scale, S["official"] / scale
    cf, co = C.crossing(S, "foreign"), C.crossing(S, "official")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 3.0))
    fig.subplots_adjust(left=0.09, right=0.985, top=0.86, bottom=0.12, wspace=0.27)

    _line(a1, Fo, MONEY, color=MONEY, lw=2.0)
    _line(a1, Of, OFFICIAL, color=OFFICIAL, lw=1.7, dashes=(4, 2))
    _line(a1, G, EXTERNAL, color=EXTERNAL, lw=2.0)
    for v, col, dx, dy in ((G, EXTERNAL, 0.35, 0), (Fo, MONEY, 0.35, 0), (Of, OFFICIAL, 0.6, -0.05)):
        f = f"{v.iloc[-1]:.0f}" if ZH else f"{v.iloc[-1]:.1f}"
        _text(a1, 1971 + dx, v.iloc[-1] * (1 + dy), f, col, size=7.4)
    top = 560 if ZH else 56
    _text(a1, 1960.0, 0.53 * top, T("对外国的负债", "liabilities to\nforeigners"), MONEY, ha="right", weight="bold")
    _text(a1, 1966.2, 0.10 * top, T("其中对官方", "to official\ninstitutions"), OFFICIAL, ha="right", weight="bold")
    _text(a1, 1956.0, 0.30 * top, T("黄金", "gold"), EXTERNAL, weight="bold")
    gap = [y for y in range(S.index[0] + 1, S.index[1])]
    _text(a1, (S.index[0] + S.index[1]) / 2, 0.80 * top,
          T(f"{gap[0]}—{gap[-1]}\n缺数", f"{gap[0]}-{gap[-1]}\nmissing"), MUTED, ha="center", size=7.4)
    a1.set_xlim(1954.2, 1973.6)
    a1.set_ylim(0, top)
    a1.set_xticks([1955, 1960, 1965, 1970])
    a1.set_yticks([0, 100, 200, 300, 400, 500] if ZH else [0, 10, 20, 30, 40, 50])
    a1.set_ylabel(T("亿美元", "billion dollars"))
    _grid(a1)
    _title(a1, T("(a) 美元负债越来越多", "(a) Dollar liabilities piled up"))
    assert Fo.iloc[-1] > 5 * G.iloc[-1] and G.iloc[0] > 2 * G.iloc[-1] and Fo.iloc[-1] < top

    rf, ro = S["gold"] / S["foreign"], S["gold"] / S["official"]
    a2.axhline(1, color=MUTED, lw=0.8, ls=(0, (1, 2)), zorder=2)
    _line(a2, rf, MONEY, color=MONEY, lw=2.0)
    _line(a2, ro, OFFICIAL, color=OFFICIAL, lw=1.7, dashes=(4, 2))
    for r, y, col, dx, dy, ha in ((rf, cf, MONEY, -0.4, -0.13, "right"), (ro, co, OFFICIAL, 0.0, 0.55, "center")):
        a2.plot([y], [r[y]], color=col, ls="none", zorder=7, **DOT)
        if r is ro:                                                              # above the curves, with a leader
            a2.plot([y, y], [r[y] + 0.07, r[y] + dy - 0.08], color=col, lw=0.6, zorder=6)
        _text(a2, y + dx, r[y] + dy, f"{y} 年 {r[y]:.2f}" if ZH else f"{y}: {r[y]:.2f}", col, ha=ha)
    for r, col, dy in ((rf, MONEY, -0.13), (ro, OFFICIAL, 0.13)):
        _text(a2, S.index[0] + 0.35, r.iloc[0] + dy * 0.6, f"{r.iloc[0]:.2f}", col)
    _text(a2, 1962.6, 2.15, T("黄金 / 对官方的负债", "gold / official\nliabilities"), OFFICIAL, weight="bold")
    _text(a2, 1955.6, 0.3, T("黄金 / 对外国的负债", "gold / liabilities\nto foreigners"), MONEY, weight="bold")
    a2.set_xlim(1954.2, 1972.2)
    a2.set_ylim(0, 3.4)
    a2.set_xticks([1955, 1960, 1965, 1970])
    a2.set_yticks([0, 1, 2, 3])
    _grid(a2)
    _title(a2, T("(b) 覆盖率跌破 1", "(b) The cover fell below 1"))
    assert rf[cf] < 1 <= rf[cf - 1] and ro[co] < 1 <= ro[co - 1] and ro[1969] > ro[1968]
    return fig


NAMES = {"英国": ("英镑", "Pound sterling"), "法国": ("法郎", "French franc"), "西德": ("马克", "Deutsche mark"),
         "日本": ("日元", "Yen")}


def _m(d: datetime.date) -> float:
    return d.year + (d.month - 1 + (d.day - 1) / 31) / 12


# where the value of each change is written: (currency, change) -> (dx, dy, ha, va)
PLACE = {("英国", 0): (0.3, -4, "left", "top"),
         ("法国", 0): (-0.4, 0, "right", "center"), ("法国", 1): (0.4, -3, "left", "top"),
         ("法国", 2): (-0.4, -1, "right", "top"),
         ("西德", 0): (0.3, 4, "left", "bottom"), ("西德", 1): (-0.4, 2, "right", "bottom")}


@figure("brettonwoods_parities")
def brettonwoods_parities():
    """The dollar value of the pound, the franc, the mark and the yen at their parities, October 1949 to August 1971,
    each with its parity of October 1949 = 100, one panel each (Bordo 1993, Table 1.2); the mark's floats tinted."""
    P, steps, fl = C.parities(), C.steps(), C.floats()
    fig, axes = plt.subplots(2, 2, figsize=(FIG_W, 3.5), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.085, right=0.985, top=0.92, bottom=0.08, wspace=0.08, hspace=0.42)
    end = _m(C.END) + 1 / 12
    for ax, cur in zip(axes.flat, ["英国", "法国", "西德", "日本"]):
        s = P[cur]
        x = np.array([_m(d.date()) for d in s.index])
        ax.axhline(100, color=MUTED, lw=0.7, ls=(0, (1, 2)), zorder=2)
        if cur == "西德":
            for a, b in fl:
                ax.axvspan(_m(a), _m(b) if b else end, color=tint(EXTERNAL, 0.14), lw=0, zorder=1)
            _text(ax, _m(fl[1][0]) - 0.15, 72, T("浮动", "float"), EXTERNAL, ha="right")
        ax.step(x, s.values, where="post", color=EXTERNAL, lw=2.0, zorder=5)
        first = steps[cur][0][1]
        for k, (when, units) in enumerate(steps[cur][1:]):
            v = 100 * first / units
            xv = _m(when)
            ax.plot([xv], [v], color=EXTERNAL, ls="none", zorder=7, **DOT)
            dx, dy, ha, va = PLACE[(cur, k)]
            _text(ax, xv + dx, v + dy, f"{v:.1f}", EXTERNAL, ha=ha, va=va)
        ax.set_xlim(1949.3, 1972.4)
        ax.set_ylim(50, 130)
        ax.set_yticks([60, 80, 100, 120])
        ax.set_xticks([1950, 1955, 1960, 1965, 1970])
        _grid(ax)
        zh, en = NAMES[cur]
        drop = 100 * first / steps[cur][-1][1]
        if cur == "日本":
            u = steps[cur][0][1]
            title = T(f"(d) {zh}：始终每美元 {u:.0f}", f"(d) {en}: {u:.0f} to the dollar throughout")
        elif drop < 100:
            title = T(f"({'abcd'[['英国', '法国'].index(cur)]}) {zh}：降到 {drop:.0f}",
                      f"({'abcd'[['英国', '法国'].index(cur)]}) {en}: down to {drop:.0f}")
        else:
            title = T(f"(c) {zh}：升到 {drop:.0f}", f"(c) {en}: up to {drop:.0f}")
        _title(ax, title)
    for ax in axes[:, 0]:
        ax.set_ylabel(T("1949 年 10 月 = 100", "Oct. 1949 = 100"), fontsize=8.5)
    assert abs(P["英国"].iloc[-1] - 100 * 2.40 / 2.80) < 1e-9 and (P["日本"] == 100).all()
    assert P["法国"].iloc[-1] < 65 and np.nanmax(P["西德"].values) > 114
    assert steps["日本"][0][1] == 360
    return fig
