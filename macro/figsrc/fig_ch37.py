"""Figures for Chapter 37 (蒙代尔–弗莱明与最优货币区).

Style as in fig_ch33.py and fig_ch36.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct
labels in the colour of their series, no legends. The IS curve is OUTPUT, the LM curve and the interest rates MONEY
(a second series of a panel AMBER, dashed), a shift by fiscal policy FISCAL, the world rate i = i^f and the exchange
rate EXTERNAL; the curves before a change are a light tint, a shift that is undone is dashed; reference lines MUTED.
All numbers come from checks/check_ch37.py: the teaching model OPEN (open_economy(), model()) and the Canadian
series (canada(), bill_spread(), dates(), pars(), FIG_BILLS).
"""
from __future__ import annotations

import datetime
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch37 as C
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
    SHADE,
    T,
    clean_axes,
    figure,
    halo,
    tint,
)

DOT = dict(marker="o", ms=4.8, mec="white", mew=0.6)
HOLLOW = dict(marker="o", ms=4.4, mfc="white", mew=1.0)
ARROW = dict(arrowstyle="-|>", lw=0.9, mutation_scale=8)


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


def _arrow(ax, p, q, color):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(color=color, shrinkA=2, shrinkB=2, **ARROW), zorder=6)


# ---------------------------------------------------------------------------------------------------
# The open-economy IS-LM
def _is(Y, G=0.0, e=None):
    """The IS curve of eq:mundell-is as i(Y): (1-c+m) Y + b i - x e = A, with government spending G and the exchange
    rate e (e0 if None)."""
    p = C.OPEN
    s = 1 - p["c"] + p["m"]
    A = p["a"] - p["c"] * p["T"] + p["I0"] + p["G"] + G
    return (A + p["x"] * (p["e0"] if e is None else e) - s * Y) / p["b"]


def _lm(Y, M):
    """The LM curve as i(Y): k Y - h i = M/P."""
    p = C.OPEN
    return (p["k"] * Y - M / p["P"]) / p["h"]


YLIM, ILIM = (74, 118), (0, 4.6)


@figure("mundell_model")
def mundell_model():
    """The four cases of ex:mundell-fiscal and ex:mundell-money under perfect capital mobility, each with the line
    i = i^f: (a) a peg, G +4: IS and LM both move right, income 90 -> 95; (b) a float, G +4: the currency appreciates
    (e = 8/9), IS goes back, income stays 90; (c) a float, M +4: LM moves right, the currency depreciates (e = 13/9) and
    IS follows, income 110; (d) a peg, M +4: the reserves fall by 4, LM goes back."""
    M = C.model()
    p, dG, dM = C.OPEN, C.POLICY["dG"], C.POLICY["dM"]
    b0, fp, ff, mf, mp = M["base_peg"], M["fiscal_peg"], M["fiscal_float"], M["money_float"], M["money_peg"]
    i_f = p["i_f"]
    fig, axes = plt.subplots(2, 2, figsize=(FIG_W, 4.7), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.08, right=0.985, top=0.94, bottom=0.09, wspace=0.08, hspace=0.30)
    Y = np.linspace(*YLIM, 300)
    for ax in axes.flat:
        ax.set_xlim(*YLIM)
        ax.set_ylim(*ILIM)
        ax.set_xticks([80, 90, 100, 110])
        ax.set_yticks([0, 1, 2, 3, 4])
        _grid(ax)
        ax.axhline(i_f, color=EXTERNAL, lw=1.3, zorder=3)
    for ax in axes[1]:
        ax.set_xlabel(T("收入 $Y$", "income $Y$"))
    for ax in axes[:, 0]:
        ax.set_ylabel(T("利率 $i$（%）", "interest rate $i$ (%)"))
    _text(axes[0, 0], YLIM[1] - 0.5, i_f - 0.12, "$i = i^{f}$", EXTERNAL, ha="right", va="top", weight="bold")
    soft = dict(lw=1.4, zorder=4)
    full = dict(lw=2.0, zorder=5)
    undone = dict(lw=1.6, dashes=(4, 2), zorder=4)

    def lab_is(ax, y_at, text, color, G=0.0, e=None):
        _text(ax, y_at + 0.6, _is(y_at, G, e), text, color, weight="bold")

    def lab_lm(ax, y_at, Mv, text, color, above=True):
        """A label above the right end of an LM curve, or below it further left."""
        if above:
            _text(ax, y_at, _lm(y_at, Mv) + 0.13, text, color, ha="right", va="bottom", weight="bold")
        else:
            _text(ax, y_at, _lm(y_at, Mv) - 0.16, text, color, ha="left", va="top", weight="bold")

    def drop(ax, Yv, color, left=True):
        """A dotted line from an equilibrium down to the income axis, the income written beside its foot."""
        ax.plot([Yv, Yv], [0, i_f], color=MUTED, lw=0.7, ls=(0, (1, 2)), zorder=3)
        _text(ax, Yv - 0.6 if left else Yv + 0.6, 0.3, f"{Yv:.0f}", color, ha="right" if left else "left")

    def start(ax):
        """The equilibrium before the change: a hollow point."""
        ax.plot([b0["Y"]], [i_f], color=INK, ls="none", zorder=7, mec=INK, **HOLLOW)
        drop(ax, b0["Y"], INK)

    def end(ax, m, color, left=True):
        ax.plot([m["Y"]], [i_f], color=color, ls="none", zorder=7, **DOT)
        drop(ax, m["Y"], color, left)

    def shift(ax, y, x0, x1, text, color=EXTERNAL):
        """An arrow from x0 to x1 at the rate y, its text above the arrow."""
        _arrow(ax, (x0, y), (x1, y), color)
        _text(ax, (x0 + x1) / 2, y + 0.14, text, color, ha="center", va="bottom")

    faint = dict(OUTPUT=tint(OUTPUT, 0.7), MONEY=tint(MONEY, 0.7))

    # (a) a peg, spending +4: the money follows, IS and LM both move right
    a = axes[0, 0]
    a.plot(Y, _is(Y), color=tint(OUTPUT, 0.55), **soft)
    a.plot(Y, _lm(Y, p["M"]), color=tint(MONEY, 0.55), **soft)
    a.plot(Y, _is(Y, dG), color=FISCAL, **full)
    a.plot(Y, _lm(Y, fp["M"]), color=MONEY, **full)
    lab_is(a, 84.6, "IS", faint["OUTPUT"])
    lab_is(a, 90.4, "IS′", FISCAL, G=dG)
    lab_lm(a, 117.5, p["M"], "LM", faint["MONEY"])
    lab_lm(a, 110.0, fp["M"], "LM′", MONEY, above=False)
    start(a)
    end(a, fp, FISCAL, left=False)
    _text(a, 75.0, 4.25, f"$G$ +{dG}", FISCAL, weight="bold")
    _title(a, T(f"(a) 钉住：增加支出，收入到 {fp['Y']:.0f}", f"(a) Peg, spending: income to {fp['Y']:.0f}"))

    # (b) a float, spending +4: the currency appreciates and IS goes back
    a = axes[0, 1]
    a.plot(Y, _is(Y, dG), color=FISCAL, **undone)
    a.plot(Y, _is(Y, dG, ff["e"]), color=OUTPUT, **full)
    a.plot(Y, _lm(Y, p["M"]), color=MONEY, **full)
    lab_is(a, 90.4, "IS′", FISCAL, G=dG)
    lab_is(a, 84.6, "IS", OUTPUT, G=dG, e=ff["e"])
    lab_lm(a, 117.5, p["M"], "LM", MONEY)
    yb = 3.2
    _arrow(a, (_is_inv(yb, dG) - 0.3, yb), (_is_inv(yb, dG, ff["e"]) + 0.3, yb), EXTERNAL)
    _text(a, _is_inv(yb, dG) + 0.9, yb, T(f"升值，$e$ = {ff['e']:.2f}", f"appreciation,\n$e$ = {ff['e']:.2f}"),
          EXTERNAL)
    end(a, ff, OUTPUT)
    _text(a, 75.0, 4.25, f"$G$ +{dG}", FISCAL, weight="bold")
    _title(a, T(f"(b) 浮动：增加支出，收入仍是 {ff['Y']:.0f}", f"(b) Float, spending: income stays {ff['Y']:.0f}"))
    assert ff["e"] / p["e0"] - 1 < -0.1 and np.isclose(_is(ff["Y"], dG, ff["e"]), i_f)

    # (c) a float, money +4: LM moves right, the currency depreciates and IS follows
    a = axes[1, 0]
    a.plot(Y, _is(Y), color=tint(OUTPUT, 0.55), **soft)
    a.plot(Y, _lm(Y, p["M"]), color=tint(MONEY, 0.55), **soft)
    a.plot(Y, _is(Y, 0.0, mf["e"]), color=OUTPUT, **full)
    a.plot(Y, _lm(Y, mf["M"]), color=MONEY, **full)
    lab_is(a, 84.6, "IS", faint["OUTPUT"])
    lab_is(a, 111.4, "IS′", OUTPUT, e=mf["e"])
    lab_lm(a, 117.5, p["M"], "LM", faint["MONEY"])
    lab_lm(a, 98.0, mf["M"], "LM′", MONEY, above=False)
    yc = 3.7
    shift(a, yc, _is_inv(yc) + 0.3, _is_inv(yc, 0.0, mf["e"]) - 0.3,
          T(f"贬值，$e$ = {mf['e']:.2f}", f"depreciation\n$e$ = {mf['e']:.2f}"))
    start(a)
    end(a, mf, MONEY, left=False)
    _text(a, 75.0, 4.25, f"$M$ +{dM}", MONEY, weight="bold")
    _title(a, T(f"(c) 浮动：增加货币，收入到 {mf['Y']:.0f}", f"(c) Float, money: income to {mf['Y']:.0f}"))

    # (d) a peg, money +4: the reserves fall by as much and LM goes back
    a = axes[1, 1]
    a.plot(Y, _is(Y), color=OUTPUT, **full)
    a.plot(Y, _lm(Y, p["M"] + dM), color=MONEY, **undone)
    a.plot(Y, _lm(Y, mp["M"]), color=MONEY, **full)
    lab_is(a, 84.6, "IS", OUTPUT)
    lab_lm(a, 117.5, mp["M"], "LM", MONEY)
    lab_lm(a, 98.0, p["M"] + dM, "LM′", MONEY, above=False)
    xd = 113.0
    lo_, hi_ = _lm(xd, p["M"] + dM), _lm(xd, mp["M"])
    _arrow(a, (xd, lo_ + 0.05), (xd, hi_ - 0.05), MONEY)
    _text(a, xd - 0.4, _lm(xd - 0.4, mp["M"]) + 0.14,
          T(f"储备减少 {-mp['reserves']:.0f}", f"reserves fall by {-mp['reserves']:.0f}"), MONEY, ha="right", va="bottom")
    end(a, mp, OUTPUT)
    _text(a, 75.0, 4.25, f"$M$ +{dM}", MONEY, weight="bold")
    _title(a, T(f"(d) 钉住：增加货币，收入仍是 {mp['Y']:.0f}", f"(d) Peg, money: income stays {mp['Y']:.0f}"))
    assert lo_ < i_f < hi_ or lo_ > i_f

    assert np.isclose(_is(fp["Y"], dG), i_f) and np.isclose(_lm(fp["Y"], fp["M"]), i_f)
    assert np.isclose(_is(mf["Y"], 0.0, mf["e"]), i_f) and np.isclose(_lm(mf["Y"], mf["M"]), i_f)
    assert np.isclose(_lm(b0["Y"], p["M"]), i_f) and mp["reserves"] == -dM and mf["e"] > 1.4
    return fig


def _is_inv(i, G=0.0, e=None):
    """The income on the IS curve at the rate i."""
    p = C.OPEN
    s = 1 - p["c"] + p["m"]
    A = p["a"] - p["c"] * p["T"] + p["I0"] + p["G"] + G
    return (A + p["x"] * (p["e0"] if e is None else e) - p["b"] * i) / s


def _lm_inv(i, M):
    """The income on the LM curve at the rate i."""
    p = C.OPEN
    return (p["h"] * i + M / p["P"]) / p["k"]


# ---------------------------------------------------------------------------------------------------
# Canada
def _m(d: datetime.date) -> float:
    return d.year + (d.timetuple().tm_yday - 1) / 365


@figure("mundell_canada")
def mundell_canada():
    """(a) The US-cent price of the Canadian dollar, 1946-1965: 100 / the yearly average (a line at mid-year) with the
    year's highest and lowest prices (100 / low, 100 / high) as a bar; the par values of September 1949 and 2 May 1962
    as dashed segments; the float of 30 September 1950 to 2 May 1962 shaded. (b) The 3-month bill yields of Canada and
    the United States, FIG_BILLS, yearly averages, and the difference as bars. Historical Statistics of Canada, tables
    J560-567 and J471-480; Economic Report of the President 1964, table C-48."""
    D, P, S = C.canada(), C.pars(), C.bill_spread()
    when = C.dates()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 3.0))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.86, bottom=0.12, wspace=0.26)
    years = np.array(D.index)
    mid = years + 0.5
    avg = 100 / D["cad_per_usd_avg"]
    hi, lo = 100 / D["cad_per_usd_low"], 100 / D["cad_per_usd_high"]
    f0, f1 = _m(when["float"]), _m(when["par62"])

    a1.axvspan(f0, f1, color=SHADE, lw=0, zorder=1)
    a1.bar(mid, hi - lo, bottom=lo, width=0.55, color=tint(EXTERNAL, 0.6), lw=0, zorder=3)
    a1.plot(mid, avg, color=EXTERNAL, lw=2.0, zorder=5, marker="o", ms=3.0, mec="white", mew=0.4)
    a1.axhline(100, color=MUTED, lw=0.7, ls=(0, (1, 2)), zorder=2)
    sep49 = _m(when["dev49"])
    a1.plot([sep49, f0], [P["1949"]] * 2, color=INK, lw=1.0, dashes=(3, 2), zorder=4)
    a1.plot([f1, years[-1] + 1], [P["1962"]] * 2, color=INK, lw=1.0, dashes=(3, 2), zorder=4)
    _text(a1, (sep49 + f0) / 2, P["1949"] - 0.7, f"{P['1949']:.2f}", INK, ha="center", va="top")
    _text(a1, f1 + 0.2, P["1962"] - 1.4, f"{P['1962']:.1f}", INK, va="top")
    _text(a1, f0 + 0.3, 109.6, T("浮动", "float"), MUTED, weight="bold")
    peak = int(hi.idxmax())
    _text(a1, peak + 0.5, hi[peak] + 0.5, f"{hi[peak]:.1f}", EXTERNAL, ha="center", va="bottom")
    above = [y for y in years if avg[y] > 100]
    assert above == list(range(above[0], above[-1] + 1))
    a1.set_xlim(1946, 1966)
    a1.set_ylim(86, 111)
    a1.set_xticks([1946, 1950, 1955, 1960, 1965])
    a1.set_yticks([90, 95, 100, 105, 110])
    a1.set_ylabel(T("1 加元合美分", "US cents per Canadian dollar"))
    _grid(a1)
    _title(a1, T(f"(a) {above[0]}—{above[-1]} 年加元贵过美元", f"(a) Above the US dollar, {above[0]}-{above[-1] % 100}"))
    assert avg.loc[1952:1960].min() > 100 and avg.loc[1963:1965].max() < 100 and hi.max() < 109

    y0, y1 = C.FIG_BILLS
    B = D.loc[y0:y1]
    s = S.loc[y0:y1]
    a2.bar(s.index, s.values, width=0.6, color=tint(INK, 0.32), lw=0, zorder=3)
    a2.axhline(0, color=MUTED, lw=0.7, zorder=2)
    a2.plot(B.index, B["ca_tbill_3m"], color=MONEY, lw=2.0, zorder=5)
    a2.plot(B.index, B["us_tbill_3m"], color=AMBER, lw=1.7, dashes=(4, 2), zorder=5)
    _text(a2, 1956.6, 4.2, T("加拿大", "Canada"), MONEY, ha="right", weight="bold")
    _text(a2, 1952.6, 2.45, T("美国", "United States"), AMBER, ha="center", weight="bold")
    _text(a2, 1950.0, -0.95, T("加拿大减美国", "Canada minus US"), MUTED, va="top")
    top = int(s.idxmax())
    _text(a2, top, s[top] + 0.12, f"{s[top]:.1f}", MUTED, ha="center", va="bottom")
    a2.set_xlim(y0 - 0.7, y1 + 0.7)
    a2.set_ylim(-1.6, 5.4)
    a2.set_xticks([1950, 1955, 1960])
    a2.set_yticks([-1, 0, 1, 2, 3, 4, 5])
    a2.set_ylabel(T("年均收益率（%）", "yearly average yield (%)"))
    _grid(a2)
    _title(a2, T("(b) 1956 年起加拿大的利率更高", "(b) Canada's rates higher from 1956"))
    assert (s.loc[1956:1962] > 0).all() and (s.loc[y0:1953] < 0).all() and B["ca_tbill_3m"].max() < 5.4
    return fig
