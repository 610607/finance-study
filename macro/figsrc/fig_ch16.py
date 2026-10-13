"""Figures for Chapter 16 (重商主义、约翰·劳与重农学派).

Style as in fig_ch15.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series, the second series in AMBER and dashed with square markers, the period of the share-price peg
tinted. All numbers come from checks/check_ch16.py, which reads the snapshots merc_facts, fgr2009_1720_shares (run
data/fetch/fgr2009_1720_shares.py first: the share prices are not kept in the repository) and finrev_facts.
merc_system redraws Velde (2003), Fig. 6; merc_tableau draws the flows of check_ch16.tableau().
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch16 as C  # noqa: E402
from style import (ACCENT, AMBER, EXTERNAL, FIG_W, FISCAL, INK, INSTIT, LIGHT, MONEY, MUTED, OUTPUT, PRICE, ZH, T,  # noqa: E402
                   arrow, canvas, card, clean_axes, figure, halo, label, rbox, tint)

PEG = tuple(pd.Timestamp(d) for d in C.PEG_DATES)
SQUARE = dict(marker="s", ms=3.6, mfc=AMBER, mec="white", mew=0.5)


def _title(ax, s):
    ax.set_title(s, fontsize=8.8, weight="bold", loc="left", pad=4)


def _grid(ax, axis="y"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


def _months(ax, ticks):
    ts = [pd.Timestamp(t) for t in ticks]
    ax.set_xticks(ts)
    ax.set_xticklabels([T(f"{t.year} 年 {t.month} 月", t.strftime("%b %Y")) for t in ts])


def _peg_band(ax, y, txt=True):
    ax.axvspan(*PEG, color=tint(PRICE, 0.08), lw=0, zorder=1)
    if txt:
        ax.text(PEG[0] + (PEG[1] - PEG[0]) / 2, y, T("钉住\n股价", "share\npeg"), fontsize=7.6, color=PRICE,
                ha="center", va="top", linespacing=1.15)


# ---------------------------------------------------------------------------
@figure("merc_shares")
def merc_shares():
    """(a) the Mississippi share in livres and in 1719 silver livres; (b) South Sea and East India, Gregorian dates."""
    S, Tb = C.shares(), C.table4()
    m = S["mississippi"].dropna()
    sp = C.silver_price(S, Tb).loc[PEG[0]:]
    ss, eic = S["south_sea"].dropna(), S["old_east_india"].dropna()
    x0, x1 = pd.Timestamp("1718-07-15"), pd.Timestamp("1721-01-10")
    ticks = ["1719-01-01", "1719-07-01", "1720-01-01", "1720-07-01", "1721-01-01"]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(FIG_W, 4.75), sharex=True)
    fig.subplots_adjust(left=0.1, right=0.975, top=0.94, bottom=0.07, hspace=0.32)

    # (a) Paris
    _peg_band(a1, 11_300)
    a1.plot(m.index, m.values, color=PRICE, lw=1.3, zorder=3)
    line, = a1.plot(sp.index, sp.values, color=AMBER, lw=1.3, zorder=4, **SQUARE)
    line.set_dashes((4, 2))
    first = m.iloc[0]
    a1.axhline(first, color=MUTED, lw=0.7, ls=(0, (1, 2)), zorder=2)
    a1.text(pd.Timestamp("1718-08-10"), first + 250, T(f"1718 年 8 月：{first:g}", f"Aug 1718: {first:g}"),
            fontsize=7.6, color=MUTED, ha="left", va="bottom")
    top, when = m.max(), m.idxmax()
    halo(a1.annotate(T(f"1720 年 1 月 8 日最高：{top:,.0f}", f"8 Jan 1720 peak: {top:,.0f}"), (when, top),
                     xytext=(pd.Timestamp("1719-10-20"), 10_750), fontsize=7.6, color=PRICE, ha="right",
                     va="center", arrowprops=dict(arrowstyle="-", color=PRICE, lw=0.6, shrinkB=2), zorder=6))
    a1.text(pd.Timestamp("1719-08-25"), 6200, T("股价（当时的里弗尔）", "price in livres of the day"), fontsize=7.6,
            color=PRICE, ha="right", va="center")
    d331 = pd.Timestamp("1720-03-31")
    halo(a1.annotate(T(f"按 1719 年白银计：\n3 月底 {sp.loc[d331]:,.0f}", f"in 1719 silver livres:\n{sp.loc[d331]:,.0f} at end-March"),
                     (d331, sp.loc[d331]), xytext=(pd.Timestamp("1720-07-20"), 6400), fontsize=7.6, color=AMBER,
                     ha="left", va="center", linespacing=1.2,
                     arrowprops=dict(arrowstyle="-", color=AMBER, lw=0.6, shrinkB=2), zorder=6))
    last = sp.index[-1]
    halo(a1.annotate(T(f"11 月 25 日约 {sp.iloc[-1]:,.0f}", f"25 Nov: about {sp.iloc[-1]:,.0f}"), (last, sp.iloc[-1]),
                     xytext=(pd.Timestamp("1721-01-05"), 1750), fontsize=7.6, color=AMBER, ha="right", va="bottom",
                     arrowprops=dict(arrowstyle="-", color=AMBER, lw=0.6, shrinkB=2), zorder=6))
    a1.set_ylim(0, 11_500)
    a1.set_yticks(range(0, 11_000, 2000))
    a1.set_yticklabels([f"{v:,}" for v in range(0, 11_000, 2000)])
    a1.set_ylabel(T("每股（里弗尔）", "per share (livres)"))
    _grid(a1)
    _title(a1, T("(a) 印度公司：钉住期间名义股价不变，按白银计却一路下跌",
                 "(a) Mississippi Company: the pegged price held in livres but fell in silver"))

    # (b) London
    a2.plot(ss.index, ss.values, color=PRICE, lw=1.3, zorder=3)
    line, = a2.plot(eic.index, eic.values, color=AMBER, lw=1.2, zorder=2)
    line.set_dashes((4, 2))
    top, when = ss.max(), ss.idxmax()
    halo(a2.annotate(T(f"1720 年 7 月 {when.day} 日：{top:g}", f"{when.day} Jul 1720: {top:g}"), (when, top),
                     xytext=(8, -2), textcoords="offset points", fontsize=7.6, color=PRICE, ha="left", va="center",
                     zorder=6))
    a2.text(pd.Timestamp("1720-03-20"), 470, T("南海公司", "South Sea Company"), fontsize=7.6, color=PRICE,
            ha="right", va="center")
    a2.text(ss.index[0] - pd.Timedelta(days=8), ss.iloc[0], T(f"1719 年 8 月：{ss.iloc[0]:g}", f"Aug 1719: {ss.iloc[0]:g}"),
            fontsize=7.6, color=PRICE, ha="right", va="center")
    dec = C.last_on_or_before(ss, "1720-12-06")
    a2.text(pd.Timestamp("1721-01-08"), 120, T(f"12 月初 {dec:g}", f"early Dec: {dec:g}"), fontsize=7.6,
            color=PRICE, ha="right", va="top")
    e_top = eic.max()
    a2.text(pd.Timestamp("1719-11-01"), 240, T(f"东印度公司（最高 {e_top:g}）", f"East India Company (peak {e_top:g})"),
            fontsize=7.6, color=AMBER, ha="center", va="bottom")
    a2.set_ylim(0, 1050)
    a2.set_ylabel(T("每 100 英镑面值（英镑）", "per £100 of stock (£)"))
    a2.set_xlim(x0, x1)
    _months(a2, ticks)
    _grid(a2)
    _title(a2, T("(b) 伦敦：南海公司的涨跌远大于东印度公司（格里历日期）",
                 "(b) London: South Sea rose and fell far more than East India (Gregorian dates)"))
    return fig


# ---------------------------------------------------------------------------
@figure("merc_notes")
def merc_notes():
    """Velde (2003) Table 4: notes issued less burned (col. 1) and their value in 1719 silver livres (col. 4)."""
    Tb = C.table4()
    k = 100 if ZH else 1000                                   # 亿里弗尔 (100 mL) or bn livres
    unit = T("亿里弗尔", "bn livres")
    fig, ax = plt.subplots(figsize=(FIG_W, 2.95))
    fig.subplots_adjust(left=0.085, right=0.975, top=0.9, bottom=0.12)
    _peg_band(ax, 2480 / k)
    ax.plot(Tb.index, Tb["col1"] / k, color=MONEY, lw=1.7, marker="o", ms=3.8, mec="white", mew=0.5, zorder=3)
    line, = ax.plot(Tb.index, Tb["col4"] / k, color=AMBER, lw=1.4, zorder=4, **SQUARE)
    line.set_dashes((4, 2))
    d1, v1 = Tb["col1"].idxmax(), Tb["col1"].max()
    ax.annotate(T(f"6 月底 {v1 / k:.2f} 亿", f"end-June {v1 / k:.2f} bn"), (d1, v1 / k), xytext=(6, 4),
                textcoords="offset points", fontsize=7.6, color=MONEY, ha="left", va="bottom")
    ax.text(pd.Timestamp("1720-11-01"), 2150 / k, T("发出减去销毁的纸币", "notes issued less burned"), fontsize=7.6,
            color=MONEY, ha="center", va="bottom")
    d4, v4 = Tb["col4"].idxmax(), Tb["col4"].max()
    halo(ax.annotate(T(f"5 月底 {v4 / k:.3f} 亿", f"end-May {v4 / k:.2f} bn"), (d4, v4 / k),
                     xytext=(pd.Timestamp("1720-07-05"), 1700 / k), fontsize=7.6, color=AMBER, ha="left",
                     va="center", arrowprops=dict(arrowstyle="-", color=AMBER, lw=0.6, shrinkB=2), zorder=6))
    ax.text(pd.Timestamp("1720-07-25"), 1150 / k, T("按 1719 年白银里弗尔计的价值", "value in 1719 silver livres"),
            fontsize=7.6, color=AMBER, ha="left", va="bottom")
    dl, vl = Tb.index[-1], Tb["col4"].iloc[-1]
    ax.annotate(T(f"1721 年 1 月 8 日\n{vl * 100:,.0f} 万",
                  f"8 Jan 1721\n{vl:.1f} m"), (dl, vl / k), xytext=(8, 0), textcoords="offset points", fontsize=7.6,
                color=AMBER, ha="left", va="bottom", linespacing=1.2)
    m5 = pd.Timestamp("1720-03-05")
    ax.annotate(T("3 月 5 日：金属里弗尔\n贬值三分之一", "5 Mar: metallic livre\ndevalued by a third"),
                (pd.Timestamp("1720-03-31"), Tb.loc["1720-03-31", "col4"] / k),
                xytext=(m5 - pd.Timedelta(days=120), 1500 / k), fontsize=7.6, color=INK, ha="center", va="center",
                linespacing=1.2, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6, shrinkB=2))
    ax.set_xlim(pd.Timestamp("1719-03-20"), pd.Timestamp("1721-04-25"))
    _months(ax, ["1719-07-01", "1720-01-01", "1720-07-01", "1721-01-01"])
    ax.set_ylim(0, 2550 / k)
    ax.set_ylabel(unit)
    _grid(ax)
    _title(ax, T("纸币越来越多，按白银计的价值 1720 年 5 月以后迅速下降",
                 "more and more notes, worth less and less in silver after May 1720"))
    return fig


# ---------------------------------------------------------------------------
def _party(ax, x, y, w, h, title, sub, color, title_size=8.2):
    rbox(ax, x, y, w, h, fc=tint(color, 0.14), ec=tint(color, 0.6), lw=0.9, r=0.1, z=3)
    if sub:
        label(ax, x + w / 2, y + h * 0.66, title, size=title_size, weight="bold", color=color, z=4)
        label(ax, x + w / 2, y + h * 0.3, sub, size=7.6, color=INK, z=4)
    else:
        label(ax, x + w / 2, y + h / 2, title, size=title_size, weight="bold", color=color, z=4)


@figure("merc_system")
def merc_system():
    """French public finance before and under Law's System, after Velde (2003), Fig. 6."""
    F = C.facts()
    before, after = F["velde_fig6_90"][0], F["velde_fig6_48"][0]
    b_txt = T(f"{before * 100:,.0f} 万", f"{before:.0f}m")
    a_txt = T(f"{after * 100:,.0f} 万", f"{after:.0f}m")
    W, H = 10.4, 6.3
    fig, ax = canvas(FIG_W, FIG_W * H / W, xlim=(0, W), ylim=(0, H))
    bh, gap = 0.82, 1.05
    ws = dict(tax=1.1, farm=1.45, state=1.1, right=1.55)
    xs, x = {}, 1.95
    for key in ws:
        xs[key] = x
        x += ws[key] + gap

    def mid(key):
        return xs[key] + ws[key] / 2

    def row_head(y, h, top, sub):
        rbox(ax, 0.05, y, 1.6, h, fc=tint(ACCENT, 0.88), r=0.1)
        label(ax, 0.85, y + h / 2 + 0.2, top, color="white", size=8.6, weight="bold")
        label(ax, 0.85, y + h / 2 - 0.22, sub, color="white", size=7.6)

    def flow(p, q, txt, where="above", dy=0.08):
        arrow(ax, p, q, color=INK, lw=1.2, ms=9)
        mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        if where == "above":
            label(ax, mx, my + dy, txt, size=7.6, va="bottom")
        elif where == "right":
            label(ax, mx + 0.1, my, txt, size=7.6, ha="left")
        elif where == "left":
            label(ax, mx - 0.12, my, txt, size=7.6, ha="right")

    def across(a, b, y, txt):
        flow((xs[a] + ws[a], y), (xs[b], y), txt)

    def down(key, y1, y2, txt):
        flow((mid(key), y1), (mid(key), y2), txt, where="right")

    g_box = lambda y: _party(ax, xs["state"] - 0.2, y, ws["state"] + 0.4, bh, T("政府支出", "spending"), "$g$", FISCAL)

    # before the System
    y0, yh = 3.3, 2.9
    rbox(ax, 1.75, y0, W - 1.8, yh, fc=tint(MUTED, 0.05), ec=tint(MUTED, 0.3), lw=0.7, r=0.12, z=1)
    row_head(y0, yh, T("体系以前", "before Law"), T("1715—1718 年", "1715–1718"))
    yt, yb = y0 + 1.75, y0 + 0.22
    _party(ax, xs["tax"], yt, ws["tax"], bh, T("纳税人", "taxpayers"), None, INSTIT)
    _party(ax, xs["farm"], yt, ws["farm"], bh, T("包税人与收税官", "tax farmers"), T("征税 $\\tau$", "collect $\\tau$"),
           INSTIT, title_size=7.8)
    _party(ax, xs["state"], yt, ws["state"], bh, T("国家", "the State"), None, FISCAL)
    _party(ax, xs["right"], yt, ws["right"], bh, T("债主", "creditors"), T("年金、官职、债券", "all kinds of debt"),
           MONEY)
    g_box(yb)
    across("tax", "farm", yt + bh / 2, r"$\tau$")
    across("farm", "state", yt + bh / 2, T("$\\bar\\tau$\n（固定）", "$\\bar\\tau$\n(fixed)"))
    across("state", "right", yt + bh / 2, T(f"约 {b_txt}\n（固定）", f"about {b_txt}\n(fixed)"))
    down("state", yt, yb + bh, T(f"$g\\leq\\bar\\tau-$ {b_txt}", f"$g\\leq\\bar\\tau-{before:.0f}$m"))

    # under the System
    y0, yh = 0.1, 3.0
    rbox(ax, 1.75, y0, W - 1.8, yh, fc=tint(MUTED, 0.05), ec=tint(MUTED, 0.3), lw=0.7, r=0.12, z=1)
    row_head(y0, yh, T("体系之下", "Law's System"), T("1719—1720 年", "1719–1720"))
    yt, yb = y0 + 1.9, y0 + 0.3
    _party(ax, xs["tax"], yt, ws["tax"], bh, T("纳税人", "taxpayers"), None, INSTIT)
    _party(ax, xs["tax"], yb, ws["tax"], bh, T("海外贸易", "overseas\ntrade"), None, EXTERNAL)
    _party(ax, xs["farm"], yt, ws["farm"], bh, T("印度公司", "the Company"), T("征收全部的税", "collects all taxes"),
           ACCENT)
    _party(ax, xs["farm"], yb, ws["farm"], bh, T("股东", "shareholders"), T("原来的债主", "former creditors"), MONEY)
    _party(ax, xs["state"], yt, ws["state"], bh, T("国家", "the State"), None, FISCAL)
    g_box(yb)
    across("tax", "farm", yt + bh / 2, r"$\tau$")
    flow((xs["tax"] + ws["tax"], yb + bh / 2), (xs["farm"] + 0.2, yt), T("利润", "profits"), where="left")
    across("farm", "state", yt + bh / 2, T(f"$\\bar\\tau-$\n{a_txt}", f"$\\bar\\tau-{after:.0f}$m"))
    down("farm", yt, yb + bh, T(f"股息不少于\n{a_txt}（可变）", f"dividend ≥ {a_txt}\n(variable)"))
    down("state", yt, yb + bh, T(f"$g\\leq\\bar\\tau-$\n{a_txt}", f"$g\\leq\\bar\\tau-{after:.0f}$m"))
    xn, wn = xs["right"] - 0.25, ws["right"] + 0.3
    rbox(ax, xn, yb, wn, yt + bh - yb, fc="white", ec=tint(FISCAL, 0.6), lw=0.8, r=0.1, z=3, ls=(0, (3, 2)))
    label(ax, xn + wn / 2, yb + (yt + bh - yb) / 2,
          T(f"国家欠公司的利息\n16 亿 × 3%\n= {a_txt}\n从 $\\bar\\tau$ 里扣除\n\n国家付出的利息\n从约 {b_txt}\n降到 {a_txt}",
            f"the State owes\nthe Company\n1.6bn × 3% = {a_txt},\ndeducted from $\\bar\\tau$\n\ninterest paid by\nthe State: about\n{b_txt} → {a_txt}"),
          size=7.6, color=FISCAL, z=4)
    return fig


# ---------------------------------------------------------------------------
@figure("merc_tableau")
def merc_tableau():
    """The money flows of Quesnay's Analyse (1766), billion livres; arrows point to the receiver."""
    Tf = C.tableau()
    F = C.facts()
    A, X = F["ques_avances"][0], F["ques_avances"][1]
    W, H = 10.4, 5.0
    fig, ax = canvas(FIG_W, FIG_W * H / W, xlim=(0, W), ylim=(0, H))
    bw, bh = 3.0, 1.5
    P = (0.25, 0.35)                   # productive class, bottom left
    R = ((W - 2.6) / 2, H - 1.45)      # proprietors, top centre
    St = (W - 0.25 - bw, 0.35)          # sterile class, bottom right
    names = dict(productive=T("生产阶级", "productive class"), proprietors=T("地主", "proprietors"),
                 sterile=T("不生产阶级", "sterile class"))

    def io(k):
        r, p = C.receipts(Tf, k), C.payments(Tf, k)
        return T(f"收入 {r:g} = 支出 {p:g}", f"receipts {r:g} = payments {p:g}")

    card(ax, P[0], P[1], bw, bh, names["productive"],
         [T(f"产出 {X:g} = 卖出 {C.receipts(Tf, 'productive'):g} + 年预付 {A:g}",
            f"output {X:g} = sales {C.receipts(Tf, 'productive'):g} + advances {A:g}"), io("productive")],
         color=ACCENT, fill=tint(OUTPUT, 0.13), title_size=8.6, body_size=7.6)
    card(ax, R[0], R[1], 2.6, 1.3, names["proprietors"],
         [T(f"上一年的地租 {Tf['productive']['proprietors']:g}", f"last year's rent {Tf['productive']['proprietors']:g}"),
          io("proprietors")], color=ACCENT, fill=tint(INSTIT, 0.15), title_size=8.6, body_size=7.6)
    card(ax, St[0], St[1], bw, bh, names["sterile"],
         [T("预付 1，卖出制品 2", "advances 1, sells wares for 2"), io("sterile")],
         color=ACCENT, fill=tint(EXTERNAL, 0.13), title_size=8.6, body_size=7.6)

    def flow(p, q, txt, tx, ty, ha="center"):
        arrow(ax, p, q, color=MONEY, lw=1.3, ms=10)
        label(ax, tx, ty, txt, size=7.6, color=MONEY, ha=ha)

    # productive <-> proprietors
    flow((1.35, P[1] + bh), (R[0], R[1] + 0.85), T(f"地租 {Tf['productive']['proprietors']:g}", "rent 2"), 2.45, 3.3,
         ha="right")
    flow((R[0] + 0.35, R[1]), (2.3, P[1] + bh), T(f"食物 {Tf['proprietors']['productive']:g}", "food 1"), 3.6, 2.75,
         ha="left")
    # proprietors -> sterile
    flow((R[0] + 2.25, R[1]), (St[0] + 1.1, St[1] + bh), T(f"制品 {Tf['proprietors']['sterile']:g}", "wares 1"),
         7.55, 2.95, ha="left")
    # productive <-> sterile
    x_a, x_b = P[0] + bw, St[0]
    mid = (x_a + x_b) / 2
    for y, p, q, txt in [
        (P[1] + 1.15, (x_b, P[1] + 1.15), (x_a, P[1] + 1.15), T("原料 1（用预付）", "raw materials 1 (advances)")),
        (P[1] + 0.7, (x_b, P[1] + 0.7), (x_a, P[1] + 0.7), T("食物 1", "food 1")),
        (P[1] + 0.25, (x_a, P[1] + 0.25), (x_b, P[1] + 0.25), T("制品 1（维持原预付）", "wares 1 (upkeep of capital)")),
    ]:
        arrow(ax, p, q, color=MONEY, lw=1.3, ms=10)
        label(ax, mid, y + 0.06, txt, size=7.6, color=MONEY, va="bottom")
    label(ax, 0.25, H - 0.2, T("单位：十亿里弗尔；箭头指向收钱的一方", "billion livres; arrows point to the receiver"),
          size=7.6, color=MUTED, ha="left", va="top")
    return fig
