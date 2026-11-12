"""Figures for Chapter 44 (自然率与附加预期的菲利普斯曲线).

Style as in fig_ch43.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the colour
of their series, no legends. The years of the stable menu (to 1969) are MONEY, the years after PRICE, neighbouring
years joined by a thin line; the slow disinflation MONEY, the fast one PRICE; reference lines MUTED. All numbers come
from checks/check_ch44.py: the American series of tables B-40 and B-62 (us()), the British series of the Bank of
England (uk()), the Japanese series of e-Stat (jp()) and the two paths of ex:naturalrate-disinflation (paths()).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch44 as C
from style import (
    FIG_W,
    LIGHT,
    MONEY,
    MUTED,
    PRICE,
    T,
    clean_axes,
    figure,
    halo,
    tint,
)

DOT = dict(marker="o", ms=4.4, mec="white", mew=0.6)


def _title(ax, s):
    ax.set_title(s, fontsize=9.0, weight="bold", loc="left", pad=4)


def _grid(ax, axis="both"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


def _text(ax, x, y, s, color, ha="left", va="center", weight="normal", size=7.6):
    lab = ax.text(x, y, s, color=color, fontsize=size, ha=ha, va=va, weight=weight, linespacing=1.3, zorder=8)
    halo(lab, 2.0)
    return lab


def _path(ax, u, p, split):
    """The yearly points joined in order: the years up to `split` MONEY, the later ones PRICE, the step between MUTED."""
    early, late = u.index <= split, u.index > split
    ax.plot(u[early], p[early], color=tint(MONEY, 0.35), lw=0.9, zorder=3)
    ax.plot(u[late], p[late], color=tint(PRICE, 0.35), lw=0.9, zorder=3)
    k = int(early.sum())
    ax.plot(u.iloc[k - 1:k + 1], p.iloc[k - 1:k + 1], color=MUTED, lw=0.8, ls=(0, (1, 2)), zorder=3)
    ax.plot(u[early], p[early], ls="none", color=MONEY, zorder=5, **DOT)
    ax.plot(u[late], p[late], ls="none", color=PRICE, zorder=5, **DOT)


def _years(ax, u, p, place, split):
    for y, (dx, dy, ha) in place.items():
        _text(ax, u[y] + dx, p[y] + dy, f"{y}", MONEY if y <= split else PRICE, ha=ha, size=7.6)


# ---------------------------------------------------------------------------------------------------
@figure("naturalrate_us")
def naturalrate_us():
    """The civilian unemployment rate (B-40) against the change of the yearly average CPI-U (B-62), 1960-1985,
    neighbouring years joined: 1960-1969 MONEY, 1970-1985 PRICE."""
    s = C.us().loc[1960:1985]
    u, p = s["unemp_pct"], s["cpi_year_pct"]
    fig, ax = plt.subplots(figsize=(FIG_W, 3.3))
    fig.subplots_adjust(left=0.085, right=0.985, top=0.9, bottom=0.13)
    _path(ax, u, p, 1969)
    place = {1960: (0.12, 0.45, "left"), 1961: (0.12, -0.4, "left"), 1965: (-0.12, 0.35, "right"),
             1966: (-0.12, 0.3, "right"), 1969: (-0.13, 0.25, "right"), 1970: (0.13, 0.3, "left"),
             1973: (-0.13, 0.1, "right"), 1974: (-0.13, -0.3, "right"), 1975: (0.13, 0.2, "left"),
             1976: (0.13, -0.35, "left"), 1979: (-0.1, 0.4, "right"), 1980: (0.0, 0.5, "center"),
             1981: (0.13, 0.25, "left"), 1982: (0.13, 0.35, "left"), 1983: (0.13, -0.35, "left"),
             1985: (-0.1, -0.5, "center")}
    _years(ax, u, p, place, 1969)
    _text(ax, 3.3, 0.55, T("1960—1969 年", "1960-1969"), MONEY, weight="bold")
    _text(ax, 9.95, 12.6, T("1970—1985 年", "1970-1985"), PRICE, ha="right", weight="bold")
    ax.set_xlim(3.0, 10.2)
    ax.set_ylim(0, 14.5)
    ax.set_xticks([3, 4, 5, 6, 7, 8, 9, 10])
    ax.set_yticks([0, 2, 4, 6, 8, 10, 12, 14])
    ax.set_xlabel(T("失业率（%）", "unemployment rate (%)"))
    ax.set_ylabel(T("消费物价的年涨幅（%）", "change of consumer prices (%)"))
    _grid(ax)
    _title(ax, T("1960 年代像一张菜单，1970 年以后的点绕着圈右移",
                 "The 1960s look like a menu; after 1970 the points loop to the right"))
    st = C.stats()
    assert st[(1960, 1969)]["corr"] < -0.8 and abs(st[(1970, 1985)]["corr"]) < 0.2
    assert u.between(3.0, 10.2).all() and p.between(0, 14.5).all()
    return fig


# ---------------------------------------------------------------------------------------------------
@figure("naturalrate_sim")
def naturalrate_sim():
    """ex:naturalrate-disinflation: (a) the unemployment of each year of the slow path (8 per cent for six years) and
    the fast one (12 per cent for two), bars from the natural rate; (b) inflation (solid) and expected inflation, last
    year's (dashed)."""
    P = C.paths()
    un, a = C.MODEL["un"], C.MODEL["alpha"]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.75), sharex=True)
    fig.subplots_adjust(left=0.075, right=0.985, top=0.87, bottom=0.16, wspace=0.24)
    for ax in (a1, a2):
        ax.set_xlim(-0.5, 9.5)
        ax.set_xticks(range(0, 10))
        ax.set_xlabel(T("年", "year"))
        _grid(ax, "y")

    # (a) unemployment: bars from the natural rate, side by side
    w = 0.36
    for name, col, dx in (("slow", MONEY, -w / 2), ("fast", PRICE, w / 2)):
        d = P[name]
        d = d[d["u"] != un]
        a1.bar(d["year"] + dx, d["u"] - un, bottom=un, width=w, color=tint(col, 0.25), edgecolor=col, lw=0.8,
               zorder=4)
    a1.axhline(un, color=MUTED, lw=0.9, ls=(0, (3, 2)), zorder=5)
    _text(a1, 9.4, un - 0.45, T("自然率 6%", "natural rate 6%"), MUTED, ha="right")
    _text(a1, 3.0, C.DIS["slow"] + 0.55, T("渐进：8%，6 年", "slow: 8%, 6 years"), MONEY, weight="bold")
    _text(a1, 2.45, C.DIS["fast"] - 0.3, T("急降：12%，2 年", "fast: 12%, 2 years"), PRICE, weight="bold")
    a1.set_ylim(4, 13)
    a1.set_yticks([4, 6, 8, 10, 12])
    a1.set_ylabel(T("失业率（%）", "unemployment rate (%)"))
    _title(a1, T("(a) 多出的失业都是 12 个百分点·年", "(a) Excess unemployment: 12 point-years"))
    for d in P.values():
        assert abs((d["u"] - un).sum() - 12) < 1e-9

    # (b) inflation and expected inflation
    for name, col in (("slow", MONEY), ("fast", PRICE)):
        d = P[name]
        a2.plot(d["year"], d["pi"], color=col, lw=1.8, zorder=5, marker="o", ms=3.6, mec="white", mew=0.5)
        a2.plot(d["year"], d["pi_e"], color=col, lw=1.1, ls=(0, (3, 2)), zorder=4)
    a2.axhline(C.DIS["end"], color=MUTED, lw=0.7, ls=(0, (1, 2)), zorder=2)
    _text(a2, 4.25, 7.2, T("渐进", "slow"), MONEY, weight="bold")
    _text(a2, 1.35, 5.1, T("急降", "fast"), PRICE, weight="bold")
    _text(a2, 9.4, 5.2, T("虚线：预期\n= 上一年的通胀", "dashed: expected\n= last year's"), MUTED, ha="right")
    a2.set_ylim(2, 11)
    a2.set_yticks([2, 4, 6, 8, 10])
    a2.set_ylabel(T("通胀率（%）", "inflation (%)"))
    _title(a2, T("(b) 急降 2 年到 4%，渐进要 6 年", "(b) 4% in 2 years or in 6"))
    assert list(P["slow"]["pi"]).index(4.0) == 6 and list(P["fast"]["pi"]).index(4.0) == 2
    assert a == 0.5
    return fig


# ---------------------------------------------------------------------------------------------------
@figure("naturalrate_jpuk")
def naturalrate_jpuk():
    """(a) Britain, 1955-1985: unemployment as a per cent of employment plus unemployment (A50) against CPI inflation
    (A47). (b) Japan, 1955-1985: the unemployment rate of the Labour Force Survey against the change of the CPI less
    imputed rent. The same scales; 1955-1969 MONEY, 1970-1985 PRICE, neighbouring years joined."""
    U = C.uk().loc[1955:1985]
    J = C.jp().loc[1955:1985]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 3.0), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.085, right=0.985, top=0.885, bottom=0.14, wspace=0.08)
    for ax in (a1, a2):
        ax.axhline(0, color=MUTED, lw=0.7, ls=(0, (1, 2)), zorder=2)
        ax.set_xlim(0, 12.6)
        ax.set_ylim(-2.5, 26)
        ax.set_xticks([0, 2, 4, 6, 8, 10, 12])
        ax.set_yticks([0, 5, 10, 15, 20, 25])
        ax.set_xlabel(T("失业率（%）", "unemployment rate (%)"))
        _grid(ax)
    a1.set_ylabel(T("消费物价的年涨幅（%）", "change of consumer prices (%)"))

    # (a) Britain
    u, p = U["unemp_pct"], U["cpi_infl_pct"]
    _path(a1, u, p, 1969)
    place = {1955: (0.25, 1.0, "left"), 1959: (0.0, -1.4, "center"), 1969: (0.3, 0.2, "left"),
             1971: (0.3, 0.0, "left"), 1974: (-0.3, 0.3, "right"), 1975: (0.3, 0.3, "left"),
             1980: (0.3, 0.6, "left"), 1981: (0.3, 0.3, "left"), 1983: (0.0, -1.5, "center"),
             1985: (0.25, 1.2, "left")}
    _years(a1, u, p, place, 1969)
    _text(a1, 5.0, 2.0, T("1955—1969 年", "1955-1969"), MONEY, weight="bold")
    _text(a1, 12.3, 18.5, T("1970—1985 年", "1970-1985"), PRICE, ha="right", weight="bold")
    _title(a1, T("(a) 英国：通胀与失业先后升高", "(a) Britain: inflation, then unemployment"))
    assert U.loc[1955:1969, "unemp_pct"].max() < U.loc[1975, "unemp_pct"] < U.loc[1983, "unemp_pct"]
    assert U.loc[1975, "cpi_infl_pct"] == U["cpi_infl_pct"].max()

    # (b) Japan
    u, p = J["unemp_pct"], J["cpi_less_rent_pct"]
    _path(a2, u, p, 1969)
    place = {1955: (0.3, -0.6, "left"), 1970: (-0.3, 0.6, "right"), 1973: (-0.3, 0.0, "right"),
             1974: (0.3, 0.0, "left"), 1975: (0.3, 0.0, "left"), 1985: (0.3, -0.6, "left")}
    _years(a2, u, p, place, 1969)
    _text(a2, 4.0, 9.0, T("所有的年份都挤在\n失业率 3% 以内", "every year within\n3% unemployment"), MUTED)
    _title(a2, T("(b) 日本：1974 年物价飞涨，失业不动", "(b) Japan, 1974: prices soar, jobs hold"))
    assert u.max() < 3 and J.loc[1974, "cpi_less_rent_pct"] == p.max()
    assert U["cpi_infl_pct"].between(-2.5, 26).all() and p.between(-2.5, 26).all() and U["unemp_pct"].max() < 12.6
    return fig
