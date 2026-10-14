"""Figures for Chapter 8 (先秦与秦汉：轻重之术、盐铁与常平仓).

Style as in fig_ch07.py (docs/STYLE.md §7): bold "(a) …" panel titles that state the point, direct labels in the
colour of their series, the second series of a panel in AMBER. Colours follow §7: prices PRICE, the state's granary
FISCAL, the 五铢 coin MONEY. Every number comes from checks/check_ch08.py, which reads the snapshot qinhan_facts;
qinhan_band draws the teaching model eq:qinhan-band with the inputs of ex:qinhan-band.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
import check_ch08 as C  # noqa: E402
from style import AMBER, FIG_W, FISCAL, INK, LIGHT, MONEY, MUTED, PRICE, T, clean_axes, figure, tint  # noqa: E402

DOT = dict(marker="o", ms=5.0, mec="white", mew=0.6)
SQ = dict(marker="s", ms=4.8, mec="white", mew=0.6)


def _title(ax, s):
    ax.set_title(s, fontsize=9.0, weight="bold", loc="left", pad=4)


def _grid(ax, axis="y"):
    clean_axes(ax)
    ax.grid(True, axis=axis, color=LIGHT, lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=8.5)


def _year(y: int) -> str:
    if y < 0:
        return T(f"前 {-y}", f"{-y} BC")
    return T(f"{y}", f"AD {y}") if y > 0 else ""


# ---------------------------------------------------------------------------
@figure("qinhan_band")
def qinhan_band():
    sim = C.simulate()
    cfg = C.BAND_FIG
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIG_W, 2.9), gridspec_kw=dict(width_ratios=[1.35, 1], wspace=0.30))
    t = sim["year"].to_numpy()

    ax1.axhspan(C.P_L, C.P_H, color=tint(FISCAL, 0.12), lw=0, zorder=1)
    for p, s, x, dy, va in ((C.P_L, T(f"买价 {C.P_L:.0f}", f"buy at {C.P_L:.0f}"), 19.4, -0.8, "top"),
                            (C.P_H, T(f"卖价 {C.P_H:.0f}", f"sell at {C.P_H:.0f}"), 8.2, 0.8, "bottom")):
        ax1.axhline(p, color=FISCAL, lw=1.0, ls=(0, (4, 2)), zorder=2)
        ax1.text(x, p + dy, s, fontsize=7.6, color=FISCAL, ha="left", va=va)
    ax1.plot(t, sim["free"], color=MUTED, lw=1.2, ls=":", marker="o", ms=2.4, zorder=3)
    ax1.plot(t, sim["price"], color=PRICE, lw=1.8, zorder=4)
    fy = cfg["famine_year"]
    f = sim.loc[sim["year"] == fy].iloc[0]
    ax1.annotate(T("大饥：仓里没粮了", "great famine:\nthe granary is empty"), xy=(fy, f["price"]), xytext=(15.2, 57),
                 fontsize=7.6, color=PRICE, ha="right", va="center", linespacing=1.2,
                 arrowprops=dict(arrowstyle="-|>", color=PRICE, lw=0.8, shrinkA=1, shrinkB=3))
    ax1.text(1.2, 50.5, T("没有常平仓", "without the granary"), fontsize=7.6, color=MUTED, ha="left", va="center")
    ax1.text(9.0, 16.5, T("有常平仓：粮价被托在 24", "with the granary: held at 24"), fontsize=7.6, color=PRICE,
             ha="left", va="center")
    ax1.set_xlim(0.5, 30.5)
    ax1.set_ylim(14, 64)
    ax1.set_xticks([1, 5, 10, 15, 20, 24, 30])
    ax1.set_xlabel(T("年", "year"), fontsize=9)
    ax1.set_ylabel(T("粮价（钱/石）", "grain price (qian per shi)"), fontsize=9)
    _grid(ax1)
    _title(ax1, T("(a) 底每次都守住，顶常常守不住", "(a) The floor holds; the ceiling often fails"))

    ax2.fill_between(t, 0, sim["stock"], step="mid", color=tint(FISCAL, 0.45), lw=0, zorder=2)
    ax2.step(t, sim["stock"], where="mid", color=FISCAL, lw=1.4, zorder=3)
    k = int(sim["stock"].idxmax())
    ax2.text(t[k], sim["stock"].iloc[k] + 0.012, T(f"最多 {sim['stock'].max():.2f}", f"peak {sim['stock'].max():.2f}"),
             fontsize=7.6, color=FISCAL, ha="center", va="bottom")
    need = float(C.demand(C.P_H)) - cfg["famine"]
    ax2.axhline(need, color=PRICE, lw=1.0, ls=":", zorder=2)
    ax2.text(1.0, need - 0.012, T(f"守住大饥要 {need:.1f}", f"needed in a great famine: {need:.1f}"), fontsize=7.6,
             color=PRICE, ha="left", va="top")
    ax2.set_xlim(0.5, 30.5)
    ax2.set_ylim(0, 0.44)
    ax2.set_xticks([1, 10, 20, 24, 30])
    ax2.set_xlabel(T("年", "year"), fontsize=9)
    ax2.set_ylabel(T("库存（平常收成 = 1）", "stock (normal harvest = 1)"), fontsize=9)
    _grid(ax2)
    _title(ax2, T("(b) 库存积得慢，用得快", "(b) Stocks build slowly, go fast"))
    return fig


# ---------------------------------------------------------------------------
@figure("qinhan_wangmang")
def qinhan_wangmang():
    D = C.coins()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(FIG_W, 3.4), gridspec_kw=dict(width_ratios=[1.1, 1], wspace=0.42))

    w = np.array([0.7, 40])
    for k, ls, s, xy in ((1, (0, (4, 2)), T("五铢钱的比例", "the wuzhu standard"), (30, 6.0)),
                         (20, ":", T("20 倍", "20 times"), (1.05, 7.0)),
                         (200, ":", T("200 倍", "200 times"), (1.05, 70))):
        ax1.plot(w, k * w / C.WUZHU_ZHU, color=MUTED if k > 1 else MONEY, lw=0.9, ls=ls, zorder=2)
        ax1.text(*xy, s, fontsize=7.4, color=MUTED if k > 1 else MONEY, ha="right" if k == 1 else "left", va="bottom")
    g = {"钱货": (PRICE, DOT), "布货": (AMBER, SQ), "五铢": (MONEY, DOT), "天凤": (MUTED, SQ)}
    for grp, (col, mk) in g.items():
        d = D[D["group"] == grp]
        if grp == "天凤":
            d = d[d["name"] == "货布"]          # 货泉 has the weight and value of the 五铢 coin
        ax1.plot(d["weight"], d["face"], ls="none", color=col, zorder=4, **mk)
    lab = {"小钱": (1.25, 1.25, "left", PRICE), "大钱": (11.2, 62, "right", PRICE), "小布": (13.8, 112, "right", AMBER),
           "大布": (20.5, 1000, "right", AMBER), "货布": (27, 18, "left", MUTED)}
    q = D.set_index("name")
    for n, (x, y, ha, col) in lab.items():
        ax1.text(x, y, T(n, {"小钱": "small coin", "大钱": "large coin", "小布": "small spade", "大布": "large spade",
                             "货布": "huobu"}[n]), fontsize=7.4, color=col, ha=ha, va="center")
    ax1.text(5.7, 0.78, T("五铢、货泉", "wuzhu, huoquan"), fontsize=7.4, color=MONEY, ha="left", va="center")
    ax1.text(1.0, 2600, T("钱货（圆）", "coins (dots)"), fontsize=7.4, color=PRICE, ha="left", va="center")
    ax1.text(1.0, 1500, T("布货（方块）", "spades (squares)"), fontsize=7.4, color=AMBER, ha="left", va="center")
    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.set_xlim(0.8, 32)
    ax1.set_ylim(0.6, 4000)
    ax1.set_xticks([1, 3, 5, 10, 24])
    ax1.set_xticklabels(["1", "3", "5", "10", "24"])
    ax1.set_yticks([1, 10, 100, 1000])
    ax1.set_yticklabels(["1", "10", "100", "1000"])
    ax1.minorticks_off()
    ax1.set_xlabel(T("重量（铢）", "weight (zhu)"), fontsize=9)
    ax1.set_ylabel(T("面值（钱）", "face value (qian)"), fontsize=9)
    _grid(ax1, axis="both")
    _title(ax1, T("(a) 宝货与货布都在五铢钱的比例线以上", "(a) All above the wuzhu line"))

    order = ["五铢", "小钱", "幺钱", "幼钱", "中钱", "壮钱", "大钱", "小布", "幺布", "幼布", "厚布", "差布", "中布", "壮布",
             "弟布", "次布", "大布", "货布", "货泉"]
    en = {"五铢": "wuzhu", "小钱": "xiao qian", "幺钱": "yao qian", "幼钱": "you qian", "中钱": "zhong qian",
          "壮钱": "zhuang qian", "大钱": "da qian", "小布": "xiao bu", "幺布": "yao bu", "幼布": "you bu", "厚布": "hou bu",
          "差布": "cha bu", "中布": "zhong bu", "壮布": "zhuang bu", "弟布": "di bu", "次布": "ci bu", "大布": "da bu",
          "货布": "huobu", "货泉": "huoquan"}
    col = {"五铢": MONEY, "钱货": PRICE, "布货": AMBER, "天凤": MUTED}
    y = np.arange(len(order))[::-1]
    m = [q.loc[n, "multiple"] for n in order]
    ax2.barh(y, m, height=0.66, color=[tint(col[q.loc[n, "group"]], 0.25) for n in order], zorder=3)
    for yy, n, v in zip(y, order, m):
        if n in ("五铢", "小钱", "大钱", "小布", "大布", "货布", "货泉"):
            ax2.text(v * 1.12, yy, f"{v:.1f}" if v < 100 else f"{v:.0f}", fontsize=7.6, color=INK, ha="left",
                     va="center")
    ax2.set_yticks(y)
    ax2.set_yticklabels([T(n, en[n]) for n in order], fontsize=7.2)
    ax2.set_xscale("log")
    ax2.set_xlim(0.7, 600)
    ax2.set_xticks([1, 10, 100])
    ax2.set_xticklabels(["1", "10", "100"])
    ax2.minorticks_off()
    ax2.set_ylim(-0.7, len(order) - 0.3)
    ax2.set_xlabel(T("面值是铜值的几倍", "face value / copper value"), fontsize=9)
    _grid(ax2, axis="x")
    ax2.tick_params(axis="y", length=0)
    _title(ax2, T("(b) 大钱 20.8 倍，大布 208 倍", "(b) Large coin 20.8×, large spade 208×"))
    return fig


# ---------------------------------------------------------------------------
@figure("qinhan_prices")
def qinhan_prices():
    P = C.price_records()
    Y = C.years()
    fig, ax = plt.subplots(figsize=(FIG_W, 2.9))
    ax.axvspan(Y["xd_cpg"], Y["yd_abolish"], color=tint(FISCAL, 0.18), lw=0, zorder=1)
    ax.text((Y["xd_cpg"] + Y["yd_abolish"]) / 2, 30000, T("常平仓", "granary"), fontsize=7.6, color=FISCAL,
            ha="center", va="center")
    for yr, s in ((Y["wu_wuzhu"], T("五铢钱", "wuzhu coin")), (Y["wm_baohuo"], T("王莽宝货", "Wang Mang's coins"))):
        ax.axvline(yr, color=MUTED, lw=0.8, ls=":", zorder=2)
        ax.text(yr + 3, 2.6, s, fontsize=7.4, color=MUTED, ha="left", va="center")
    for _, r in P.iterrows():
        rice = r["grain"] == "米"
        style = dict(DOT) if rice else dict(SQ)
        colr = PRICE if rice else AMBER
        if r["id"] == "hhs_gold":
            style.update(mfc="white", mec=AMBER, mew=1.2)
        ax.plot(r["year"], r["price"], ls="none", color=colr, zorder=4, **style)
    lab = [("gz_famine", 0, (-198, 10000), "left", T("关中，米 1 万", "Guanzhong, rice 10,000")),
           ("wd_cheap", 0, (-164, 10), "left", T("文帝时，粟十余", "under Wendi, millet 10+")),
           ("xd_5", 0, (-62, 3.6), "center", T("谷 5", "grain 5")),
           ("zcg_8", 0, (-55, 8), "left", T("金城 8", "Jincheng 8")),
           ("cpg_famine", 0, (-56, 300), "right", T("齐地 300 余", "Qi 300+")),
           ("fsf_42", 2, (-36, 500), "left", T("前 42 年：200 余 / 400 / 500", "42 BC: 200+ / 400 / 500")),
           ("wm_famine", 0, (14, 2000), "right", T("雒阳以东，米 2000", "east of Luoyang, rice 2,000")),
           ("hhs_gold", 0, (29, 10000), "left", T("一斤金换一斛粟", "a jin of gold\nfor a hu of millet"))]
    for i, k, (x, y), ha, s in lab:
        r = P[P["id"] == i].iloc[k]
        colr = PRICE if r["grain"] == "米" else AMBER
        ax.text(x, y, s, fontsize=7.4, color=colr, ha=ha, va="center", linespacing=1.15)
    ax.set_yscale("log")
    ax.set_yticks([1, 10, 100, 1000, 10000])
    ax.set_yticklabels(["1", "10", "100", "1000", "10000"])
    ax.minorticks_off()
    ax.set_ylim(2, 60000)
    ax.set_xlim(-215, 55)
    ticks = [-200, -150, -100, -50, 1, 50]
    ax.set_xticks(ticks)
    ax.set_xticklabels([_year(t) for t in ticks])
    ax.set_xlabel(T("年份", "year"), fontsize=9)
    ax.set_ylabel(T("钱/石（斛）", "qian per shi (hu)"), fontsize=9)
    ax.text(-150, 2500, T("圆点：米", "dots: rice"), fontsize=7.6, color=PRICE, ha="left", va="center")
    ax.text(-150, 1300, T("方块：谷、粟", "squares: unhusked grain"), fontsize=7.6, color=AMBER, ha="left",
            va="center")
    ax.text(-150, 680, T("空心：按金价折算", "hollow: converted at the gold price"), fontsize=7.6, color=AMBER,
            ha="left", va="center")
    _grid(ax)
    return fig
