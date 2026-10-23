"""Figures for Chapter 33 (IS–LM).

Style as in fig_ch32.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series, no legends. The IS curve and output are OUTPUT, the LM curve, reserves and interest rates
MONEY (a second series of a panel AMBER, dashed), a shift by fiscal policy FISCAL; reference lines MUTED.
All numbers come from checks/check_ch33.py: the teaching model M2 (islm(), model()), Banking and Monetary Statistics
(reserves(), requirements(), rates()) and the G.17 index of industrial production (ip(), ip_peak()).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch33 as C
from style import (
    AMBER,
    FIG_W,
    FISCAL,
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
SQUARE = dict(marker="s", ms=4.4, mec="white", mew=0.5)
ARROW = dict(arrowstyle="-|>", lw=0.9, mutation_scale=8)


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


def _is(m, Y):
    """The IS curve of an equilibrium dict as i(Y)."""
    return (m["is0"] - Y) / m["is1"]


def _lm(m, Y):
    return m["lm1"] * Y - m["lm0"]


def _point(ax, m, color, marker=DOT):
    ax.plot([m["Y"]], [m["i"]], color=color, zorder=7, ls="none", **marker)


def _fmt(x: float) -> str:
    return f"{x:.0f}" if abs(x - round(x)) < 1e-9 else f"{x:.1f}"


@figure("islm_curves")
def islm_curves():
    """(a) The IS and LM curves of ex:islm-equilibrium and their intersection; (b) government spending +4 shifts IS
    (FISCAL), money +4 shifts LM (MONEY, dashed); the cross at an unchanged rate (dotted) gives income 100."""
    M = C.model()
    base, fis, mon = M["base"], M["fiscal"], M["money"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 3.0))
    fig.subplots_adjust(left=0.08, right=0.985, top=0.86, bottom=0.15, wspace=0.24)
    Y = np.linspace(70, 112, 200)
    for ax in (a1, a2):
        ax.set_xlim(70, 112)
        ax.set_ylim(0, 4.8)
        ax.set_xticks([70, 80, 90, 100, 110])
        ax.set_yticks([0, 1, 2, 3, 4])
        ax.set_xlabel(T("收入 $Y$", "income $Y$"))
        _grid(ax)
    a1.set_ylabel(T("利率 $i$（%）", "interest rate $i$ (%)"))

    # (a) the equilibrium
    a1.plot(Y, _is(base, Y), color=OUTPUT, lw=2.0, zorder=5)
    a1.plot(Y, _lm(base, Y), color=MONEY, lw=2.0, zorder=5)
    a1.plot([base["Y"], base["Y"]], [0, base["i"]], color=MUTED, lw=0.7, ls=(0, (1, 2)), zorder=3)
    a1.plot([70, base["Y"]], [base["i"], base["i"]], color=MUTED, lw=0.7, ls=(0, (1, 2)), zorder=3)
    _point(a1, base, INK)
    _text(a1, base["Y"] + 1.2, base["i"] - 0.12, f"({base['Y']:.0f}, {base['i']:.0f}%)", INK, va="top", size=7.6)
    _text(a1, 96.5, _is(base, 96.5), "IS", OUTPUT, weight="bold")
    _text(a1, 71.5, 2.55, T("产品市场：\n储蓄等于投资", "goods market:\nS = I"), OUTPUT, size=7.6)
    _text(a1, 108.5, _lm(base, 108.5) - 0.15, "LM", MONEY, ha="left", va="top", weight="bold")
    _text(a1, 111, 4.45, T("货币市场：\n需求等于供给", "money market:\nL = M/P"), MONEY, ha="right",
          va="top", size=7.6)
    _title(a1, T("(a) 两条曲线一起决定收入与利率", "(a) Two curves fix income and the rate"))

    # (b) the two policies
    a2.plot(Y, _is(base, Y), color=tint(OUTPUT, 0.55), lw=1.4, zorder=4)
    a2.plot(Y, _lm(base, Y), color=tint(MONEY, 0.55), lw=1.4, zorder=4)
    a2.plot(Y, _is(fis, Y), color=FISCAL, lw=2.0, zorder=5)
    a2.plot(Y, _lm(mon, Y), color=MONEY, lw=2.0, dashes=(4, 2), zorder=5)
    cross_Y = base["Y"] + base["cross"] * C.POLICY["dG"]
    a2.plot([base["Y"], cross_Y], [base["i"], base["i"]], color=MUTED, lw=0.9, ls=(0, (1, 2)), zorder=3)
    a2.plot([cross_Y], [base["i"]], color=MUTED, zorder=6, ls="none", marker="o", ms=4.2, mfc="white", mec=MUTED,
            mew=0.9)
    _text(a2, cross_Y + 0.8, base["i"] + 0.12, T(f"交叉：{cross_Y:.0f}", f"cross: {cross_Y:.0f}"), MUTED,
          va="bottom", size=7.6)
    _point(a2, base, INK)
    _point(a2, fis, FISCAL)
    _point(a2, mon, MONEY, SQUARE)
    _text(a2, base["Y"] - 1.0, base["i"] + 0.1, f"{base['Y']:.0f}", INK, ha="right", va="bottom", size=7.6)
    _text(a2, fis["Y"] + 0.9, fis["i"] + 0.12, f"{fis['Y']:.0f}, {_fmt(fis['i'])}%", FISCAL, va="bottom", size=7.6)
    _text(a2, mon["Y"] + 0.9, mon["i"] - 0.12, f"{mon['Y']:.0f}, {_fmt(mon['i'])}%", MONEY, va="top", size=7.6)
    _text(a2, 96.5, 3.9, f"$G$ +{C.POLICY['dG']}", FISCAL, weight="bold", size=7.6)
    _text(a2, 111.5, 1.6, f"$M$ +{C.POLICY['dM']}", MONEY, ha="right", va="top", weight="bold", size=7.6)
    _title(a2, T("(b) 财政政策抬高利率，货币政策压低利率", "(b) Spending raises i, money lowers it"))
    assert fis["i"] > base["i"] > mon["i"] and fis["Y"] < cross_Y
    return fig


def hicks_ll(Ymax: float, floor: float = 1.0, s: float = 1.4):
    """A curve LL of the shape Hicks describes, as (Y, i): Y = Ymax (1 - exp(-(i - floor)/s)): nearly horizontal at
    the floor on the left, nearly vertical at the most income the money can finance on the right."""
    i = np.linspace(floor + 1e-4, floor + 9, 400)
    return Ymax * (1 - np.exp(-(i - floor) / s)), i


@figure("islm_trap")
def islm_trap():
    """(a) Hicks's LL, nearly horizontal on the left and vertical on the right, before and after an increase of money
    (dashed), with an IS on the left and one on the right; (b) the two shocks of ex:islm-1937 in M2."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 3.0))
    fig.subplots_adjust(left=0.08, right=0.985, top=0.86, bottom=0.15, wspace=0.24)
    # (a) the shape of LL
    floor, s = 1.0, 1.4
    Y0, i0 = hicks_ll(100, floor, s)
    Y1, i1 = hicks_ll(130, floor, s)
    a1.plot(Y0, i0, color=MONEY, lw=2.0, zorder=5)
    a1.plot(Y1, i1, color=MONEY, lw=1.6, dashes=(4, 2), zorder=5)
    a1.axhline(floor, color=MUTED, lw=0.8, ls=(0, (1, 2)), zorder=2)
    # two IS curves: i = q - Y/r
    for q, r, col, name in ((2.2, 40, tint(OUTPUT, 0.2), T("IS（左）", "IS (left)")),
                            (9.0, 14, OUTPUT, T("IS（右）", "IS (right)"))):
        y = np.linspace(0, 140, 200)
        a1.plot(y, q - y / r, color=col, lw=1.6, zorder=4)
        for Ym in (100, 130):
            # the intersection with LL
            ii = np.linspace(floor + 1e-4, floor + 9, 4000)
            yy = Ym * (1 - np.exp(-(ii - floor) / s))
            k = np.argmin(np.abs(ii - (q - yy / r)))
            a1.plot([yy[k]], [ii[k]], color=col if Ym == 100 else MONEY, zorder=7, ls="none",
                    **(DOT if Ym == 100 else SQUARE))
        _text(a1, 3 if q < 5 else 46, q - (3 if q < 5 else 46) / r + 0.25, name, col, va="bottom", weight="bold",
              size=7.6)
    _text(a1, 138, floor - 0.12, T("利率的下限", "floor of the rate"), MUTED, ha="right", va="top", size=7.6)
    _text(a1, 96, 7.6, "LL", MONEY, ha="right", weight="bold")
    _text(a1, 106, 2.4, T("货币增加后的 LL", "LL with\nmore money"), MONEY, size=7.6)
    a1.set_xlim(0, 140)
    a1.set_ylim(0, 8.5)
    a1.set_xticks([])
    a1.set_yticks([])
    a1.set_xlabel(T("收入", "income"))
    a1.set_ylabel(T("利率", "interest rate"))
    _grid(a1)
    _title(a1, T("(a) 货币增加，水平段几乎不动", "(a) More money barely moves the flat part"))

    # (b) 1937 in the teaching model
    M = C.model()
    base, both, m37, g37 = M["base"], M["both"], M["m37"], M["g37"]
    Y = np.linspace(74, 100, 200)
    a2.plot(Y, _is(base, Y), color=tint(OUTPUT, 0.55), lw=1.4, zorder=4)
    a2.plot(Y, _lm(base, Y), color=tint(MONEY, 0.55), lw=1.4, zorder=4)
    a2.plot(Y, _is(g37, Y), color=FISCAL, lw=2.0, zorder=5)
    a2.plot(Y, _lm(m37, Y), color=MONEY, lw=2.0, dashes=(4, 2), zorder=5)
    _point(a2, base, INK)
    _point(a2, both, INK, SQUARE)
    a2.plot([m37["Y"]], [m37["i"]], color=MONEY, zorder=6, ls="none", marker="o", ms=4.2, mfc="white", mec=MONEY,
            mew=0.9)
    a2.plot([g37["Y"]], [g37["i"]], color=FISCAL, zorder=6, ls="none", marker="o", ms=4.2, mfc="white", mec=FISCAL,
            mew=0.9)
    a2.annotate("", xy=(m37["Y"], m37["i"]), xytext=(base["Y"], base["i"]), arrowprops=dict(color=MONEY, **ARROW),
                zorder=6)
    a2.annotate("", xy=(g37["Y"], g37["i"]), xytext=(base["Y"], base["i"]), arrowprops=dict(color=FISCAL, **ARROW),
                zorder=6)
    _text(a2, base["Y"] + 0.6, base["i"] - 0.06, f"{base['Y']:.0f}, {base['i']:.0f}%", INK, va="top", size=7.6)
    _text(a2, both["Y"] - 0.7, both["i"] + 0.04, f"{both['Y']:.0f}, {_fmt(both['i'])}%", INK, ha="right", va="bottom",
          size=7.6)
    _text(a2, m37["Y"] + 0.4, m37["i"] + 0.05, T(f"只减货币\n{_fmt(m37['i'])}%", f"money only\n{_fmt(m37['i'])}%"),
          MONEY, va="bottom", size=7.6)
    _text(a2, g37["Y"] + 0.5, g37["i"] - 0.06, T(f"只减支出 {_fmt(g37['i'])}%", f"spending only {_fmt(g37['i'])}%"),
          FISCAL, va="top", size=7.6)
    _text(a2, 75, _lm(m37, 75) + 0.1, f"$M$ −{-C.SHOCK37['dM']}", MONEY, va="bottom", weight="bold", size=7.6)
    _text(a2, 91.2, 0.92, f"$G$ −{-C.SHOCK37['dG']}", FISCAL, weight="bold", size=7.6)
    a2.set_xlim(74, 100)
    a2.set_ylim(0.8, 3.4)
    a2.set_xticks([75, 80, 85, 90, 95])
    a2.set_yticks([1, 1.5, 2, 2.5, 3])
    a2.set_xlabel(T("收入 $Y$", "income $Y$"))
    a2.set_ylabel(T("利率 $i$（%）", "interest rate $i$ (%)"))
    _grid(a2)
    _title(a2, T("(b) LM 左移抬高利率，IS 左移压低利率", "(b) LM left raises the rate, IS left lowers it"))
    assert m37["i"] > base["i"] > g37["i"] and both["Y"] < min(m37["Y"], g37["Y"])
    return fig


def _x(year: int, month: int) -> float:
    return year + (month - 0.5) / 12


def _xd(ts) -> float:
    return ts.year + (ts.dayofyear - 1) / 365.25


@figure("islm_1937")
def islm_1937():
    """The United States, 1935-1939: (a) required and excess reserves of member banks, monthly, with the dates of the
    changes of reserve requirements; (b) industrial production (G.17, 2017 = 100); (c) the yields of new Treasury bills
    and of long-term Government bonds."""
    R = C.reserves()
    Q = C.requirements()
    P = C.ip_peak()
    s = C.ip()
    m, _ = C.rates()
    fig, (a1, a2, a3) = plt.subplots(3, 1, figsize=(FIG_W, 4.55), sharex=True)
    fig.subplots_adjust(left=0.1, right=0.86 if ZH else 0.84, top=0.95, bottom=0.08, hspace=0.42)
    changes = list(Q.start.iloc[1:5])                       # 1936-08-16, 1937-03-01, 1937-05-01, 1938-04-16
    for ax in (a1, a2, a3):
        for d in changes:
            ax.axvline(_xd(d), color=MUTED, lw=0.7, ls=(0, (1, 2)), zorder=2)
        _grid(ax)
        ax.set_xlim(1935, 1940)
    x = np.array([_x(y, mm) for y, mm in R.index])
    a1.plot(x, R.required_m / 100, color=tint(MONEY, 0.5), lw=1.6, zorder=4)
    a1.plot(x, R.excess_m / 100, color=MONEY, lw=2.0, zorder=5)
    end = R.index[-1]
    _text(a1, 1940.08, R.required_m[end] / 100, T("法定准备", "required"), tint(MONEY, 0.7), size=7.6)
    _text(a1, 1940.08, R.excess_m[end] / 100, T("超额准备", "excess"), MONEY, weight="bold", size=7.6)
    lo = R.excess_m.loc[1937].idxmin()
    _text(a1, _x(1937, lo), R.excess_m[(1937, lo)] / 100 + 3, f"{R.excess_m[(1937, lo)] / 100:.1f}", MONEY,
          ha="center", va="bottom", size=7.6)
    marks = [T("+50%", "+50%"), "", T("+33⅓%", "+33⅓%"), T("降低", "cut")]
    for d, lab in zip(changes, marks):
        if lab:
            _text(a1, _xd(d) + 0.04, 79, lab, MUTED, va="top", size=7.6)
    a1.set_ylim(0, 80)
    a1.set_yticks([0, 20, 40, 60])
    a1.set_ylabel(T("亿美元", "$100 million"))
    _title(a1, T(f"(a) 准备金率翻倍，超额准备在 1937 年 {lo} 月降到最低", "(a) Requirements doubled; excess reserves fell"))

    xi = np.array([_x(y, mm) for y, mm in s.loc[1935:1939].index])
    a2.plot(xi, s.loc[1935:1939].values, color=OUTPUT, lw=2.0, zorder=5)
    pk, tr = (1937, P["peak"]), (1938, P["trough"])
    for key, va, dy in ((pk, "bottom", 0.15), (tr, "top", -0.15)):
        a2.plot([_x(*key)], [s[key]], color=OUTPUT, zorder=7, ls="none", **DOT)
    _text(a2, _x(*pk), s[pk] + 0.15, T(f"1937 年 {P['peak']} 月", f"May 1937"), OUTPUT, ha="center", va="bottom",
          size=7.6)
    _text(a2, _x(*tr) + 0.1, s[tr] - 0.1, T(f"1938 年 {P['trough']} 月，−{P['fall']:.1f}%",
                                            f"May 1938, −{P['fall']:.1f}%"), OUTPUT, va="top", size=7.6)
    a2.set_ylim(4.5, 9.5)
    a2.set_yticks([5, 6, 7, 8, 9])
    a2.set_ylabel(T("2017 年 = 100", "2017 = 100"))
    _title(a2, T(f"(b) 工业生产一年下降 {P['fall']:.1f}%", f"(b) Industrial production fell {P['fall']:.1f}% in a year"))

    mm = m.loc[1936:1939]
    xr = np.array([_x(y, k) for y, k in mm.index])
    a3.plot(xr, mm.govt_bond_pct.values, color=MONEY, lw=2.0, zorder=5)
    a3.plot(xr, mm.tbill_pct.values, color=AMBER, lw=1.5, dashes=(4, 2), zorder=5)
    e = mm.index[-1]
    _text(a3, 1940.08, mm.govt_bond_pct[e], T("长期政府债券", "long-term bonds"), MONEY, weight="bold", size=7.6)
    _text(a3, 1940.08, mm.tbill_pct[e] + 0.1, T("国库券", "Treasury bills"), AMBER, size=7.6)
    a3.axhline(2, color=MUTED, lw=0.7, ls=(0, (1, 2)), zorder=2)
    a3.set_ylim(0, 3.2)
    a3.set_yticks([0, 1, 2, 3])
    a3.set_ylabel(T("%", "%"))
    a3.set_xticks([1935, 1936, 1937, 1938, 1939])
    a3.set_xlabel(T("年份", "year"))
    _title(a3, T("(c) 短期利率近乎零，长期利率停在 2% 以上", "(c) Bills near zero, bonds above 2%"))
    assert mm.govt_bond_pct.min() > 2
    return fig
