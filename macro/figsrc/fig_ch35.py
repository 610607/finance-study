"""Figures for Chapter 35 (战后重建：马歇尔计划、德国货币改革与道奇路线).

Style as in fig_ch34.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series, no legends. Industrial production and unemployment are OUTPUT (the French zone, the second
series of its panel, AMBER, dashed); Japan's wholesale prices PRICE; Marshall aid EXTERNAL (the other recipients a
lighter shade); the dates of the reforms MUTED. All numbers come from checks/check_ch35.py: Ritschl's Tab. I (ipb(),
ipf()), the table on p. 57 of the Monatsberichte (unemployment()), the Bank of Japan's prewar-base index (wpi()) and De
Long and Eichengreen's amounts (marshall_aid()).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch35 as C
from style import (
    AMBER,
    EXTERNAL,
    FIG_W,
    LIGHT,
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

DOT = dict(marker="o", ms=4.6, mec="white", mew=0.6)


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


def _t(month: str) -> float:
    """'1948-06' -> the middle of June 1948 on a time axis in years."""
    y, m = (int(x) for x in month.split("-"))
    return y + (m - 0.5) / 12


def _x(s):
    return np.array([_t(m) for m in s.index])


def _event(ax, month: str, label: str, y: float, ha="left"):
    x = _t(month)
    ax.axvline(x, color=MUTED, lw=1.0, ls=(0, (1, 2)), zorder=2)
    _text(ax, x + (0.08 if ha == "left" else -0.08), y, label, MUTED, ha=ha, va="top")


@figure("reconstruction_germany")
def reconstruction_germany():
    """(a) The official index of industrial production (1936 = 100) of the Bizone and of the French zone, monthly
    (Ritschl, Tab. I), with the currency reform of June 1948; (b) the unemployed of the Bundesgebiet, thousands, March
    1948 to February 1950 (Monatsberichte, February 1950, p. 57)."""
    B, Fz, U = C.ipb(), C.ipf(), C.unemployment()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 3.0))
    fig.subplots_adjust(left=0.09, right=0.985, top=0.86, bottom=0.15, wspace=0.28)
    _event(a1, "1948-06", T("货币改革", "reform"), 97, ha="right")
    a1.plot(_x(B), B.values, color=OUTPUT, lw=2.0, zorder=5)
    a1.plot(_x(Fz), Fz.values, color=AMBER, lw=1.6, dashes=(4, 2), zorder=5)
    for m, dx, dy, ha, va in (("1948-06", 0.08, -3, "left", "top"), ("1948-12", -0.1, 2, "right", "bottom")):
        a1.plot([_t(m)], [B[m]], color=OUTPUT, zorder=7, ls="none", **DOT)
        _text(a1, _t(m) + dx, B[m] + dy, f"{B[m]:.0f}", OUTPUT, ha=ha, va=va)
    _text(a1, 1946.05, 48, T("联合经济区", "Bizone"), OUTPUT, weight="bold")
    _text(a1, 1947.1, 61, T("法国占领区", "French zone"), AMBER, weight="bold")
    a1.set_xlim(1945.9, 1949.8)
    a1.set_ylim(20, 100)
    a1.set_xticks([1946, 1947, 1948, 1949])
    a1.set_yticks([20, 40, 60, 80, 100])
    a1.set_ylabel(T("1936 年 = 100", "1936 = 100"))
    _grid(a1)
    _title(a1, T("(a) 改革以后生产加快回升", "(a) Output rose faster after the reform"))
    assert B["1948-12"] / B["1948-06"] > 1.5 and B["1948-06"] > B["1947-06"]
    assert Fz.index[0] == "1947-01" and Fz["1948-12"] > Fz["1948-06"]

    a2.plot(_x(U), U.values, color=OUTPUT, lw=2.0, zorder=5)
    for m, dx, dy, ha, va in (("1948-06", 0.06, 40, "left", "bottom"), ("1949-12", -0.06, 40, "right", "bottom"),
                              ("1950-02", 0.0, 60, "center", "bottom")):
        a2.plot([_t(m)], [U[m]], color=OUTPUT, zorder=7, ls="none", **DOT)
        _text(a2, _t(m) + dx, U[m] + dy, f"{U[m]:.0f}" if ZH else f"{U[m]:,.0f}", OUTPUT, ha=ha, va=va)
    _event(a2, "1948-06", T("货币改革", "reform"), 2380)
    a2.set_xlim(1948.1, 1950.3)
    a2.set_ylim(0, 2400)
    a2.set_xticks([1949, 1950])
    a2.set_xticklabels(["1949", "1950"])
    a2.set_yticks([0, 500, 1000, 1500, 2000])
    a2.set_ylabel(T("千人", "thousands"))
    _grid(a2)
    _title(a2, T("(b) 失业也在增加", "(b) Unemployment rose too"))
    assert U.idxmax() == "1950-02" and U["1950-02"] > 4 * U["1948-06"]
    return fig


@figure("reconstruction_japan")
def reconstruction_japan():
    """The Bank of Japan's prewar-base wholesale price index (1934-36 average = 1), monthly, 1944-1952, on a log scale,
    with the Dodge budget and the single rate of April 1949 and the outbreak of the Korean War in June 1950."""
    W = C.wpi()
    fig, ax = plt.subplots(figsize=(FIG_W, 2.9))
    fig.subplots_adjust(left=0.1, right=0.985, top=0.97, bottom=0.12)
    ax.set_yscale("log")
    _event(ax, "1949-04", T("道奇预算、\n360 日元", "Dodge budget,\n360 yen"), 700, ha="right")
    _event(ax, "1950-06", T("朝鲜战争", "Korean War"), 700)
    ax.plot(_x(W), W.values, color=PRICE, lw=2.0, zorder=5)
    marks = (("1944-01", 0.08, 1.0, "left", "bottom", 1.25), ("1945-12", 0.08, 1.0, "left", "top", 0.8),
             ("1947-12", -0.08, 1.0, "right", "bottom", 1.2), ("1949-04", 0.1, 1.0, "left", "top", 0.8),
             ("1950-06", 0.1, 1.0, "left", "top", 0.82), ("1951-04", 0.1, 1.0, "left", "top", 0.84))
    for m, dx, _, ha, va, f in marks:
        ax.plot([_t(m)], [W[m]], color=PRICE, zorder=7, ls="none", **DOT)
        v = W[m]
        _text(ax, _t(m) + dx, v * f, f"{v:.1f}" if v < 10 else f"{v:.0f}", PRICE, ha=ha, va=va)
    ax.set_xlim(1943.9, 1953.1)
    ax.set_ylim(1, 900)
    ax.set_xticks(range(1944, 1954, 2))
    ax.set_yticks([1, 3, 10, 30, 100, 300])
    ax.set_yticklabels(["1", "3", "10", "30", "100", "300"])
    ax.minorticks_off()
    ax.set_ylabel(T("1934—1936 年平均 = 1（对数刻度）", "1934-36 average = 1 (log scale)"))
    _grid(ax)
    # 1948: the prices more than doubled; from the single rate to the war, about a tenth; after it, a quarter in half a
    # year
    assert W["1948-12"] / W["1947-12"] > 2
    assert W["1950-06"] / W["1949-04"] < 1.15 and W["1950-12"] / W["1950-06"] > 1.2
    assert W.idxmax() < "1952-12"
    return fig


@figure("reconstruction_marshall")
def reconstruction_marshall():
    """Marshall aid 1948-1951: the United Kingdom, France, Italy and the Western-occupied zones of Germany, and the
    other recipients (the total less the four), in hundred million dollars (zh) or billion dollars (en)."""
    A = C.marshall_aid()
    names = ["英国", "法国", "意大利", "西德", "其他"]
    zh = {"其他": "其余受援国"}
    en = {"英国": "United Kingdom", "法国": "France", "意大利": "Italy", "西德": "West Germany",
          "其他": "other recipients"}
    scale = 10 if ZH else 1
    vals = [A[k] * scale for k in names]
    fig, ax = plt.subplots(figsize=(FIG_W, 2.3))
    fig.subplots_adjust(left=0.2 if not ZH else 0.15, right=0.97, top=0.97, bottom=0.17)
    yi = np.arange(len(names))[::-1]
    cols = [EXTERNAL] * 4 + [tint(EXTERNAL, 0.45)]
    ax.barh(yi, vals, 0.62, color=cols, zorder=4)
    for y0, v, c in zip(yi, vals, cols):
        _text(ax, v + (0.6 if ZH else 0.06), y0, f"{v:.0f}" if ZH else f"{v:.1f}",
              EXTERNAL if c == EXTERNAL else tint(EXTERNAL, 0.8), va="center")
    ax.set_yticks(yi)
    ax.set_yticklabels([T(zh.get(k, k), en[k]) for k in names])
    ax.set_xlim(0, 50 if ZH else 5)
    ax.set_xticks([0, 10, 20, 30, 40] if ZH else [0, 1, 2, 3, 4])
    ax.set_xlabel(T("亿美元", "billion dollars"))
    total = A["total"] * scale
    _text(ax, 49 if ZH else 4.9, yi[1], T(f"合计 {total:.0f} 亿美元", f"total ${total:.1f} billion"), EXTERNAL,
          ha="right", weight="bold")
    _grid(ax, axis="x")
    assert abs(sum(vals) - total) < 1e-9 and A["其他"] > A["英国"]
    return fig
