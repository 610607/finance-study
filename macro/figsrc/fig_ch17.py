"""Figures for Chapter 17 (德川日本与清代中国：东亚的前现代市场).

Style as in fig_ch16.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series, the second series in AMBER and dashed with square markers, the worst years of the coinage
(1711-1718) tinted. All numbers come from checks/check_ch17.py, which reads the snapshots toku_facts,
gpih_iwahashi_rice and gpih_gamble_beijing. toku_dojima is a schematic after Schaede (1989), Fig. 1 and sections 4-5.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, NullLocator

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch17 as C  # noqa: E402
from style import (ACCENT, AMBER, FIG_W, FISCAL, INK, INSTIT, LIGHT, MONEY, MUTED, OUTPUT, PRICE, ZH, T,  # noqa: E402
                   arrow, canvas, clean_axes, figure, halo, label, rbox, tint)

SQUARE = dict(marker="s", ms=4.6, mfc=AMBER, mec="white", mew=0.6)
WORST = (1710.5, 1718.5)


def _title(ax, s):
    ax.set_title(s, fontsize=9.0, weight="bold", loc="left", pad=4)


def _grid(ax, axis="y"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)


# ---------------------------------------------------------------------------
def _box(ax, x, y, w, h, title, sub, color, title_size=8.2):
    rbox(ax, x, y, w, h, fc=tint(color, 0.14), ec=tint(color, 0.6), lw=0.9, r=0.1, z=3)
    if sub:
        label(ax, x + w / 2, y + h - 0.27, title, size=title_size, weight="bold", color=color, z=4)
        label(ax, x + w / 2, y + (h - 0.45) / 2, sub, size=7.6, color=INK, z=4)
    else:
        label(ax, x + w / 2, y + h / 2, title, size=title_size, weight="bold", color=color, z=4)


@figure("toku_dojima")
def toku_dojima():
    """The three stages of a rice bill (Schaede 1989, Fig. 1 and sections 4-5)."""
    F = C.facts()
    pay, bal, days = F["sch_tonya30"]
    koku = F["sch_100koku"][0]
    ten = F["sch_tenday"][0]
    W, H = 10.4, 5.5
    fig, ax = canvas(FIG_W, FIG_W * H / W, xlim=(0, W), ylim=(0, H))
    cols = [(0.1, 3.25), (3.5, 3.95), (7.7, 2.6)]
    heads = [T("第一阶段 · 仓库拍卖（远期）", "Stage 1 · auction (forward)"),
             T("第二阶段 · 堂岛（远期与期货）", "Stage 2 · Dojima (forward, futures)"),
             T("第三阶段 · 提米（现货）", "Stage 3 · delivery (spot)")]
    yh = H - 0.55
    for (x, w), s in zip(cols, heads):
        rbox(ax, x, yh, w, 0.48, fc=tint(ACCENT, 0.88), r=0.1)
        label(ax, x + w / 2, yh + 0.24, s, color="white", size=8.2, weight="bold")

    # stage 1
    x1, w1 = cols[0][0] + 0.15, cols[0][1] - 0.3
    bh = 1.0
    yw, yt = 3.25, 0.9
    _box(ax, x1, yw, w1, bh, T("各藩仓库（藏屋敷）", "domain warehouses"), T("拍卖存米", "auction the stored rice"),
         FISCAL)
    _box(ax, x1, yt, w1, bh, T("问屋（tonya）", "wholesalers (tonya)"), T("拍卖的买主", "buyers at the auction"),
         INSTIT)
    xl, xr = x1 + 0.55, x1 + w1 - 0.55
    arrow(ax, (xl, yt + bh), (xl, yw), color=INK, lw=1.1, ms=9)
    label(ax, xl - 0.1, (yt + bh + yw) / 2,
          T(f"先付 {pay:.0f}%\n{days:.0f} 天内\n付清 {bal:.0f}%", f"{pay:.0f}% at once,\n{bal:.0f}% within\n{days:.0f} days"),
          size=7.6, ha="right", color=INK)
    arrow(ax, (xr, yw), (xr, yt + bh), color=INK, lw=1.1, ms=9)
    label(ax, xr + 0.1, (yt + bh + yw) / 2, T("银切手，\n付清后\n换成米票", "silver bill,\nthen the\nrice bill"),
          size=7.6, ha="left", color=INK)

    # stage 2
    x2, w2 = cols[1][0] + 0.1, cols[1][1] - 0.2
    ym, hm = 2.45, 1.95
    rbox(ax, x2, ym, w2, hm, fc=tint(MONEY, 0.05), ec=tint(MONEY, 0.4), lw=0.8, r=0.12, z=1)
    label(ax, x2 + w2 / 2, ym + hm - 0.22, T("堂岛米市", "Dojima rice market"), size=8.2, weight="bold", color=MONEY)
    iw = (w2 - 0.45) / 2
    _box(ax, x2 + 0.15, ym + 0.2, iw, 1.2, T("正米：米票", "rice bills"),
         T("转手买卖\n（远期）", "resold\n(forward)"), MONEY)
    _box(ax, x2 + 0.3 + iw, ym + 0.2, iw, 1.2, T("帐合米", "book rice"),
         T(f"{koku:.0f} 石一张\n标准米（期货）", f"{koku:.0f}-koku lots\n(futures)"), MONEY)
    yc, hc = 0.2, 1.55
    _box(ax, x2, yc, w2, hc, T("清算所（米方两替）", "clearinghouses"),
         T(f"收至多三分之一的保证金\n每 {ten:.0f} 天结算一次盈亏\n担保合约的履行",
           f"take a margin of up to one third,\nsettle gains and losses every {ten:.0f} days,\nguarantee the contracts"),
         ACCENT)
    xm = x2 + w2 / 2
    arrow(ax, (xm, yc + hc), (xm, ym), color=INK, lw=1.1, ms=9, style="<|-|>")
    label(ax, xm + 0.12, (yc + hc + ym) / 2, T("保证金与盈亏", "margin, gains, losses"), size=7.6, ha="left")
    arrow(ax, (x1 + w1, yt + bh * 0.75), (x2 + 0.15 + iw * 0.45, ym + 0.2), color=INK, lw=1.1, ms=9)
    label(ax, x2 + 0.45, 2.0, T("卖出米票", "sell bills"), size=7.6, ha="left")

    # stage 3
    x3, w3 = cols[2][0] + 0.15, cols[2][1] - 0.3
    _box(ax, x3, yw, w3, bh, T("批发商", "merchants"), T("需要实物米的人", "who want the rice"), INSTIT)
    _box(ax, x3, yt, w3, bh, T("各藩仓库", "domain warehouses"), T("凭票交米", "deliver against bills"), FISCAL)
    arrow(ax, (x2 + w2, ym + 1.25), (x3, yw + bh / 2), color=INK, lw=1.1, ms=9)
    label(ax, (x2 + w2 + x3) / 2, ym + 1.55, T("买下\n米票", "buy\nbills"), size=7.6)
    xd = x3 + w3 / 2
    arrow(ax, (xd, yw), (xd, yt + bh), color=INK, lw=1.1, ms=9)
    label(ax, xd + 0.12, (yt + bh + yw) / 2, T("凭米票提米", "rice against\nthe bill"), size=7.6, ha="left")
    return fig


# ---------------------------------------------------------------------------
def _rice_panel(ax, actual, t, years, color):
    ax.axvspan(*WORST, color=tint(PRICE, 0.08), lw=0, zorder=0)
    s = actual.loc[years[0]:years[-1]].dropna()
    ax.plot(s.index, s.values, color=color, lw=1.7, zorder=3)
    pred = C.step(t, range(max(years[0], int(s.index[0])), years[-1] + 1))
    line, = ax.step(pred.index, pred.values, where="mid", color=AMBER, lw=1.5, zorder=4)
    line.set_dashes((4, 2))
    ax.set_yscale("log")
    ax.yaxis.set_minor_locator(NullLocator())
    ax.set_xlim(years[0] - 1, years[-1] + 1)
    _grid(ax)
    return pred


@figure("toku_rice")
def toku_rice():
    """(a) Edo rice price against the content prediction from the koban; (b) Osaka against the chogin."""
    F, R = C.facts(), C.rice()
    E, O = C.edo_test(F, R), C.osaka_test(F, R)
    years = list(range(1680, 1761))
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(FIG_W, 4.3), sharex=True)
    fig.subplots_adjust(left=0.1, right=0.975, top=0.94, bottom=0.085, hspace=0.34)

    # (a) Edo
    _rice_panel(a1, R["edo_ryo_per_koku"], E, years, PRICE)
    a1.set_ylim(0.5, 2.9)
    ticks = [0.5, 0.75, 1, 1.5, 2, 2.5]
    a1.yaxis.set_major_locator(FixedLocator(ticks))
    a1.set_yticklabels([f"{v:g}" for v in ticks])
    a1.set_ylabel(T("两 / 石", "ryo per koku"))
    a1.text(1714.5, 0.53, T("钱币最差\n的年份", "worst\ncoins"), fontsize=7.6, color=PRICE, ha="center", va="bottom",
            linespacing=1.15)
    a1.text(1681, 1.62, T("江户米价", "Edo price"), fontsize=7.8, color=PRICE, ha="left", va="center")
    a1.text(1681, 0.62, T("按小判纯金的预测", "predicted from the gold per ryo"), fontsize=7.8, color=AMBER, ha="left",
            va="center")
    g, k = E.loc["genroku"], E.loc["genbun"]
    halo(a1.annotate(T(f"1696—1710：预测 {g['pred']:.3f}，实际 {g['actual']:.3f}",
                       f"1696–1710: predicted {g['pred']:.3f}, actual {g['actual']:.3f}"),
                     (1703, g["pred"]), xytext=(1696, 2.35), fontsize=7.6, color=INK, ha="center", va="center",
                     arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6, shrinkB=2), zorder=6))
    halo(a1.annotate(T(f"1737—1750：预测 {k['pred']:.3f}，实际 {k['actual']:.3f}",
                       f"1737–1750: predicted {k['pred']:.3f}, actual {k['actual']:.3f}"),
                     (1744, k["pred"]), xytext=(1747, 2.15), fontsize=7.6, color=INK, ha="center", va="center",
                     arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6, shrinkB=2), zorder=6))
    for key, x, y in (("genroku", 1706.5, 1.19), ("kenji", 1714.5, 1.3), ("kyoho", 1727.5, 0.89), ("genbun", 1755, 1.48)):
        name = {"genroku": T("元禄", "Genroku"), "kenji": T("乾字", "Kenji"), "kyoho": T("享保", "Kyoho"),
                "genbun": T("元文", "Genbun")}[key]
        a1.text(x, y, name, fontsize=7.6, color=AMBER, ha="center", va="bottom")
    _title(a1, T("(a) 江户：元禄小判时期米价跟着纯金走，元文以后低于预测",
                 "(a) Edo: the price followed the gold content under Genroku, not after Genbun"))

    # (b) Osaka
    _rice_panel(a2, R["osaka_monme_per_koku"], O, years, PRICE)
    a2.set_ylim(23, 330)
    ticks = [30, 50, 100, 200, 300]
    a2.yaxis.set_major_locator(FixedLocator(ticks))
    a2.set_yticklabels([str(v) for v in ticks])
    a2.set_ylabel(T("匁 / 石", "momme per koku"))
    a2.text(1709.8, 132, T("大阪米价", "Osaka price"), fontsize=7.8, color=PRICE, ha="right", va="center")
    a2.text(1690.5, 70, T("按银币成色\n的预测", "predicted from\nthe silver\nfineness"), fontsize=7.8, color=AMBER,
            ha="center", va="center", linespacing=1.2)
    y4 = O.loc["yotsu"]
    halo(a2.annotate(T(f"1711—1718：预测 {y4['pred']:.1f}，实际 {y4['actual']:.1f}",
                       f"1711–18: predicted {y4['pred']:.1f}, actual {y4['actual']:.1f}"),
                     (1712, y4["pred"]), xytext=(1695.5 if ZH else 1694.5, 250), fontsize=7.6, color=INK, ha="center", va="center",
                     arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6, shrinkB=2), zorder=6))
    o = R["osaka_monme_per_koku"]
    halo(a2.annotate(T(f"1718 年 {o.loc[1718]:g} → 1719 年 {o.loc[1719]:g}", f"1718: {o.loc[1718]:g} → 1719: {o.loc[1719]:g}"),
                     (1719, o.loc[1719]), xytext=(1733, 26), fontsize=7.6, color=PRICE, ha="center", va="center",
                     arrowprops=dict(arrowstyle="-", color=PRICE, lw=0.6, shrinkB=2), zorder=6))
    a2.set_xticks(range(1680, 1761, 10))
    a2.set_xlabel(T("年份", "year"))
    _title(a2, T("(b) 大阪：按银币成色的预测，每个时期都偏高",
                 "(b) Osaka: the prediction from the silver is too high in every period"))
    return fig


# ---------------------------------------------------------------------------
@figure("qing_cash")
def qing_cash():
    """(a) cash per tael near Beijing (Gamble) with the rates said by contemporaries; (b) wage indices."""
    F, G = C.facts(), C.gamble()
    e = G["cash_per_tael"].dropna()
    idx = C.wage_index(G)
    W = C.wages(G)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(FIG_W, 4.3), sharex=True)
    fig.subplots_adjust(left=0.1, right=0.975, top=0.94, bottom=0.085, hspace=0.34)

    # (a)
    a1.axhline(1000, color=MUTED, lw=0.7, ls=(0, (1, 2)), zorder=1)
    a1.text(1828, 975, T("官定：钱千准银一两", "official: 1,000 cash = 1 tael"), fontsize=7.6, color=MUTED, ha="center",
            va="top")
    a1.plot(e.index, e.values, color=MONEY, lw=1.8, marker="o", ms=4.2, mec="white", mew=0.5, zorder=3)
    pts = C.contemporaries(F)
    a1.plot([p[0] for p in pts], [p[1] for p in pts], ls="none", zorder=4, **SQUARE)
    names = {"黄爵滋": T("黄爵滋", "Huang Juezi"), "包世臣": T("包世臣", "Bao Shichen"),
             "刘良驹（京中）": T("刘良驹：京中", "Liu Liangju: Beijing"), "刘良驹（外省）": T("刘良驹：外省", "Liu: provinces")}
    for (yr, v, who), (dx, dy, ha, va) in zip(pts, ((-0.7, 0, "right", "center"), (0.0, 70, "center", "bottom"),
                                                   (-0.7, 0, "right", "center"), (-0.7, 0, "right", "center"))):
        halo(a1.text(yr + dx, v + dy, f"{names[who]} {v:,.0f}", fontsize=7.6, color=AMBER, ha=ha, va=va,
                     zorder=6))
    for yr in (1807, 1824, 1853):
        v = e.loc[yr]
        a1.text(yr, v - 95 if yr == 1807 else v + 70, f"{yr}: {v:,.0f}", fontsize=7.6, color=MONEY,
                ha="left" if yr == 1807 else ("center" if yr == 1824 else "right"), va="top" if yr == 1807 else "bottom")
    a1.text(1828, 1480, T("北京郊区的比价（Gamble）", "near Beijing (Gamble)"), fontsize=7.8, color=MONEY, ha="right",
            va="center")
    a1.set_ylim(700, 2450)
    a1.set_ylabel(T("文 / 两", "cash per tael"))
    _grid(a1)
    _title(a1, T("(a) 一两银子换的铜钱：从 1,000 文附近涨到 2,000 文以上",
                 "(a) Copper cash per tael: from about 1,000 to over 2,000"))

    # (b)
    a2.axhline(100, color=MUTED, lw=0.7, ls=(0, (1, 2)), zorder=1)
    a2.axvspan(GAMBLE_SPAN[0], GAMBLE_SPAN[1], color=tint(MUTED, 0.07), lw=0, zorder=0)
    a2.plot(idx.index, idx["copper"], color=PRICE, lw=1.8, marker="o", ms=4.2, mec="white", mew=0.5, zorder=3)
    line, = a2.plot(idx.index, idx["silver"], color=AMBER, lw=1.6, zorder=4, **SQUARE)
    line.set_dashes((4, 2))
    cw = 100 * W["w_late"] / W["w_base"]
    sw = 100 * W["ws_late"] / W["ws_base"]
    a2.text(1832, 125, T(f"铜钱工资\n1845—1850 年平均 {cw:.1f}", f"copper wage\n1845–50 mean: {cw:.1f}"), fontsize=7.6,
            color=PRICE, ha="center", va="bottom", linespacing=1.2)
    a2.text(1832, 63, T(f"折成银两\n1845—1850 年平均 {sw:.0f}", f"in silver\n1845–50 mean: {sw:.0f}"), fontsize=7.6,
            color=AMBER, ha="center", va="top", linespacing=1.2)
    a2.text(1808, 44, T("1807—1813 年平均 = 100", "1807–1813 mean = 100"), fontsize=7.6, color=MUTED, ha="left",
            va="center")
    a2.set_ylim(35, 145)
    a2.set_xlim(1805, 1855)
    a2.set_xticks(range(1810, 1851, 10))
    a2.set_xlabel(T("年份", "year"))
    a2.set_ylabel(T("指数", "index"))
    _grid(a2)
    _title(a2, T(f"(b) 日工资：铜钱工资几乎不变，折成银两跌了 {100 - sw:.0f}%",
                 f"(b) Daily wage: flat in copper, down {100 - sw:.0f}% in silver"))
    return fig


GAMBLE_SPAN = (C.GAMBLE_LATE[0] - 0.5, C.GAMBLE_LATE[1] + 0.5)
