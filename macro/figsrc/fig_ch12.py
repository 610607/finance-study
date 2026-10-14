"""Figures for Chapter 12 (宋元明：世界最早的纸币及其崩溃).

Style follows 610607/electromagnetics-study (see docs/STYLE.md §4): bold "(a) …" panel titles
that state the point, direct labels in the colour of their series instead of legends, a second
series in AMBER and dashed, thin leader lines, short explanatory notes inside the plot, and
roadmap-style rounded boxes for diagrams.

All numbers come from checks/check_ch12.py, which reads data/snapshots/yuanshi_suyinchao.csv and
data/snapshots/paper_money_facts.csv.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.ticker import FixedLocator, NullLocator

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch12 as C  # noqa: E402
from style import (ACCENT, AMBER, FIG_W, INK, LIGHT, MONEY, MUTED, ZH, T, canvas, clean_axes,  # noqa: E402
                   figure, label, rbox, tint)


# ---------------------------------------------------------------------------
@figure("songming_timeline")
def timeline():
    """Four note systems on one time axis, with the events discussed in the chapter."""
    W = 10.4
    H = 6.44
    fig, ax = canvas(FIG_W, FIG_W * H / W, xlim=(0, W), ylim=(0, H))
    y0, y1 = 1000, 1580
    X0, X1 = 2.05, W - 0.1

    def X(year):
        return X0 + (year - y0) * (X1 - X0) / (y1 - y0)

    # (period, name, start, end, light end, light text, events [(year, text, where)])
    rows = [
        (T("北宋", "N. Song"), T("交子 → 钱引", "jiaozi → qianyin"), 1023, 1127, 1250, T("南宋时仅行于四川", "Sichuan only"),
         [(1023, T("1023 益州交子务", "1023 Yizhou office"), "above"),
          (1107, T("1107 超发二十倍", "1107 20× the quota"), "below")]),
        (T("南宋", "S. Song"), T("会子", "huizi"), 1160, 1276, None, None,
         [(1168, T("1168 三年一界", "1168 3-year issues"), "above"),
          (1247, T("1247 不再分界", "1247 no more terms"), "below"),
          (1268, T("1268 一贯值 257 文", "1268 worth 257 wen"), "right")]),
        (T("元", "Yuan"), T("中统钞、至元钞", "chao notes"), 1260, 1356, 1368, None,
         [(1260, T("1260 中统钞", "1260 Zhongtong"), "above"),
          (1287, T("1287 至元钞，一当五", "1287 Zhiyuan, 1 = 5"), "below"),
          (1351, T("1351 至正交钞", "1351 Zhizheng"), "right")]),
        (T("明", "Ming"), T("大明宝钞", "baochao"), 1375, 1450, 1570, T("名存实亡", "nominal"),
         [(1375, T("1375 大明宝钞", "1375 baochao"), "above"),
          (1525, T("1525 一贯折银三厘", "1525 3 li of silver"), "below")]),
    ]
    rh, gap, top = 0.62, 0.74, H - 0.34
    for i, (period, name, a, b, light, light_txt, events) in enumerate(rows):
        y = top - (i + 1) * rh - i * gap
        rbox(ax, 0.05, y, 1.75, rh, fc=tint(ACCENT, 0.88), r=0.1)
        label(ax, 0.925, y + rh * 0.72, period, color="white", size=7.8)
        label(ax, 0.925, y + rh * 0.28, name, color="white", size=8.6 if ZH else 7.6, weight="bold")
        if light:
            rbox(ax, X(b), y + 0.06, X(light) - X(b), rh - 0.12, fc="white", ec=tint(MUTED, 0.75), lw=0.9,
                 r=0.08, ls=(0, (3, 2)))
            if light_txt:
                label(ax, X(b) + 0.1, y + rh / 2, light_txt, color=MUTED, size=7.6, ha="left")
        rbox(ax, X(a), y + 0.06, X(b) - X(a), rh - 0.12, fc=tint(MONEY, 0.16), ec=tint(MONEY, 0.6), lw=0.9, r=0.08)
        for yr, txt, where in events:
            ax.add_patch(Circle((X(yr), y + rh / 2), 0.075, fc=AMBER, ec="white", lw=0.8, zorder=6))
            if where == "right":
                label(ax, X(max(b, light or b)) + 0.12, y + rh / 2, txt, size=7.8, ha="left")
            else:
                up = where == "above"
                right_end = yr > 1500
                label(ax, X(yr) + (0.08 if right_end else -0.08), y + (rh + 0.07 if up else -0.07), txt, size=7.8,
                      ha="right" if right_end else "left", va="bottom" if up else "top")
    # time axis
    ya = top - len(rows) * rh - (len(rows) - 1) * gap - 0.42
    ax.plot([X0, X1], [ya, ya], color=MUTED, lw=0.8)
    for yr in range(1000, 1600, 100):
        ax.plot([X(yr), X(yr)], [ya, ya - 0.07], color=MUTED, lw=0.8)
        label(ax, X(yr), ya - 0.12, str(yr), size=7.8, color=MUTED, va="top")
    # legend
    yl = 0.1
    rbox(ax, 0.1, yl, 0.55, 0.26, fc=tint(MONEY, 0.16), ec=tint(MONEY, 0.6), lw=0.9, r=0.06)
    label(ax, 0.75, yl + 0.13, T("广泛流通", "in general use"), size=8.0, ha="left")
    rbox(ax, 2.75, yl, 0.55, 0.26, fc="white", ec=tint(MUTED, 0.75), lw=0.9, r=0.06, ls=(0, (3, 2)))
    label(ax, 3.4, yl + 0.13, T("仅局部流通或名存实亡", "regional or nominal only"), size=8.0, ha="left", color=MUTED)
    ax.add_patch(Circle((6.55, yl + 0.13), 0.075, fc=AMBER, ec="white", lw=0.8))
    label(ax, 6.72, yl + 0.13, T("正文讨论的事件", "event discussed in the text"), size=8.0, ha="left")
    return fig


# ---------------------------------------------------------------------------
@figure("yuan_issuance")
def yuan_issuance():
    """Notes printed each year, in ding of Zhongtong equivalent, log scale, with the two period means."""
    y = C.yuan_issuance().set_index("year")["zt_equiv_ding"]
    early, late = y.loc[1260:1275].mean(), y.loc[1276:1286].mean()
    fig, ax = plt.subplots(figsize=(FIG_W, 2.8))
    ax.axvspan(1286.5, 1330, color=tint(MONEY, 0.07), lw=0, zorder=0)
    ax.bar(y.index, y.values, width=0.72, color=MONEY, zorder=2)
    ax.hlines(early, 1259.6, 1275.4, color=AMBER, lw=1.5, ls=(0, (4, 2)), zorder=3)
    ax.hlines(late, 1275.6, 1286.4, color=AMBER, lw=1.5, ls=(0, (4, 2)), zorder=3)
    ax.text(1259.6, early * 1.35, T(f"1260—1275\n年均 {early / 1e4:.1f} 万锭", f"1260–75\nmean {early / 1e3:.0f}k ding"),
            fontsize=7.8, color=AMBER, ha="left", va="bottom", linespacing=1.3)
    ax.text(1260.5, late * 2.0, T(f"1276—1286 年均 {late / 1e4:.0f} 万锭\n约为前一时期的 {late / early:.0f} 倍",
                                  f"1276–86 mean {late / 1e3:,.0f}k ding\nabout {late / early:.0f}× the earlier mean"),
            fontsize=7.8, color=AMBER, ha="left", va="bottom", linespacing=1.3)
    ax.set_yscale("log")
    ax.set_ylim(1.5e4, 1.2e8)
    ax.yaxis.set_major_locator(FixedLocator([1e5, 1e6, 1e7, 1e8]))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.set_yticklabels([T("10 万", "100k"), T("100 万", "1m"), T("1000 万", "10m"), T("1 亿", "100m")])
    ax.set_xlim(1257, 1332)
    ax.set_xlabel(T("年份", "year"))
    ax.set_ylabel(T("每年印钞（锭，折合中统钞）", "notes printed (ding, Zhongtong equiv.)"))
    clean_axes(ax)
    ax.grid(True, axis="y", color=LIGHT, lw=0.7, zorder=0)
    for x, txt, (tx, ty) in [(1287, T("1287 至元钞", "1287 Zhiyuan notes"), (1290.5, 2.6e7)),
                             (1310, T("1310 至大银钞", "1310 Zhida silver notes"), (1313, T(6.0e7, 4.9e7)))]:
        ax.annotate(txt, xy=(x, y[x] * 1.08), xytext=(tx, ty), fontsize=7.8, color=INK, va="center",
                    arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
    ax.text(1288, 9.0e7, T("1287 年后按至元钞一贯 = 中统钞五贯折算", "after 1287: 1 Zhiyuan guan = 5 Zhongtong guan"),
            fontsize=7.6, color=MONEY, ha="left", va="center")
    fig.subplots_adjust(left=0.125, right=0.985, top=0.97, bottom=0.15)
    return fig


# ---------------------------------------------------------------------------
@figure("note_value")
def note_value():
    """Value of a note relative to its value at issue (=100), log scale; Yuan and Ming panels."""
    F = C.facts()
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(FIG_W, 2.85), sharey=True,
                                 gridspec_kw=dict(width_ratios=[1, 1.45]))
    fig.subplots_adjust(left=0.1, right=0.985, top=0.9, bottom=0.15, wspace=0.07)
    line = dict(lw=2.0, ms=5.5, zorder=4)

    # (a) Yuan, valued at the official silver price
    zt1287 = 100 * F["yuan_1260_parity"] / (F["yuan_1287_silver"] * F["yuan_1287_ratio"])
    zy1309 = 100 * F["yuan_1287_silver"] / F["yuan_1309_zhida"]
    g_zt = 100 * C.avg_rate(F["yuan_1260_parity"], F["yuan_1287_silver"] * F["yuan_1287_ratio"], 1287 - 1260)
    g_zy = 100 * C.avg_rate(F["yuan_1287_silver"], F["yuan_1309_zhida"], 1309 - 1287)
    a1.plot([1260, 1287], [100, zt1287], "-o", color=MONEY, **line)
    a1.plot([1287, 1309], [100, zy1309], "--s", color=AMBER, dashes=(4, 2), **line)
    a1.text(1285, zt1287 * 0.68, f"{zt1287:.0f}", fontsize=8.2, color=MONEY, ha="right", va="top")
    a1.text(1311, zy1309, f"{zy1309:.0f}", fontsize=8.2, color=AMBER, ha="left", va="center")
    a1.text(1259, 7.5, T(f"中统钞\n银价年均涨 {g_zt:.1f}%", f"Zhongtong\nsilver price\n+{g_zt:.1f}%/yr"),
            fontsize=7.8, color=MONEY, ha="left", va="top", linespacing=1.3)
    a1.text(1291, 26, T(f"至元钞\n银价年均涨 {g_zy:.1f}%", f"Zhiyuan\nsilver price\n+{g_zy:.1f}%/yr"),
            fontsize=7.8, color=AMBER, ha="left", va="top", linespacing=1.3)
    a1.set_xlim(1252, 1322)
    a1.xaxis.set_major_locator(FixedLocator([1260, 1287, 1309]))
    a1.set_title(T("(a) 元：按官定银价", "(a) Yuan: at the official silver price"), fontsize=9.0, weight="bold",
                 loc="left", pad=4)

    # (b) Ming baochao, in copper cash and in silver
    cu = [(1375, 100), (1393, 100 * F["ming_1393_copper"] / F["ming_1375_par"]),
          (1475, 100 * F["ming_chenghua"] / F["ming_1375_par"])]
    ag = [(1375, 100), (1525, 100 * F["ming_1525_silver"])]
    g_cu = 100 * C.avg_rate(F["ming_1393_copper"], F["ming_1375_par"], 1393 - 1375)
    g_ag = 100 * C.avg_rate(F["ming_1525_silver"], 1.0, 1525 - 1375)
    a2.plot(*zip(*cu), "-o", color=MONEY, **line)
    a2.plot(*zip(*ag), "--s", color=AMBER, dashes=(4, 2), **line)
    a2.annotate("", xy=(1475, 0.045), xytext=(1475, 0.095), arrowprops=dict(arrowstyle="-|>", color=MONEY, lw=1.2))
    a2.text(1389, cu[1][1], f"{cu[1][1]:.0f}", fontsize=8.2, color=MONEY, ha="right", va="center")
    a2.text(1469, cu[2][1], "<0.1", fontsize=8.2, color=MONEY, ha="right", va="center")
    a2.text(1525, ag[1][1] * 0.6, f"{ag[1][1]:.1f}", fontsize=8.2, color=AMBER, ha="center", va="top")
    a2.text(1380, 1.0, T("以铜钱计", "in copper cash"), fontsize=7.8, color=MONEY, ha="left", va="top")
    a2.text(1502, 3.0, T("以白银计", "in silver"), fontsize=7.8, color=AMBER, ha="center", va="bottom")
    a2.text(1532, 55, T(f"以钞计的价格，年均涨幅：\n铜钱 {g_cu:.1f}%（1375—1393）\n白银 {g_ag:.1f}%（1375—1525）",
                         f"price in notes, per year:\ncopper +{g_cu:.1f}% (1375–93)\nsilver +{g_ag:.1f}% (1375–1525)"),
            fontsize=7.6, color=INK, ha="right", va="top", linespacing=1.35)
    a2.set_xlim(1365, 1540)
    a2.xaxis.set_major_locator(FixedLocator([1375, 1425, 1475, 1525]))
    a2.set_title(T("(b) 明：大明宝钞", "(b) Ming: baochao"), fontsize=9.0, weight="bold", loc="left", pad=4)

    for a in (a1, a2):
        a.set_yscale("log")
        a.set_ylim(0.03, 200)
        a.yaxis.set_major_locator(FixedLocator([0.1, 1, 10, 100]))
        a.yaxis.set_minor_locator(NullLocator())
        a.axhline(100, color=MUTED, lw=0.6, ls=(0, (1, 2)), zorder=1)
        clean_axes(a)
        a.set_xlabel(T("年份", "year"))
    a1.set_yticklabels(["0.1", "1", "10", "100"])
    a1.set_ylabel(T("价值（发行时 = 100）", "value (at issue = 100)"))
    return fig
