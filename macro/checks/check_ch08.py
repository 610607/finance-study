"""Chapter 8 (先秦与秦汉：轻重之术、盐铁与常平仓): every number and every quotation in zh/ch08_qinhan.tex.

    python3 checks/check_ch08.py

Input is one snapshot:
  qinhan_facts  quotations from 史记, 汉书 and 后汉书 (checked against the daizhigev20 corpus by
                data/fetch/verify_quotes.py), from 管子 and 盐铁论 (checked against the corpus here, since
                verify_quotes.py reads only 史藏/), and five phrases of Kanaya (1984) with two numbers
                (checked by data/fetch/verify_web_quotes.py)
The figure module figsrc/fig_ch08.py imports the functions defined here.

What is checked here:
  1. corpus     the 管子 and 盐铁论 rows occur verbatim (whitespace ignored) in the corpus, when it is present
                ($CORPUS or ~/.cache/finance-study/daizhigev20; tools/setup_env.sh prepares it)
  2. readings   every number of the value column is read from the classical numeral in its quotation
                (data/fetch/classical_numerals.py, plus 亿 = 万万, 半 and the reading of 二百八十亿万 argued in the
                text); the snapshot's .json explains the readings
  3. the text   every “…” in the chapter is part of a quotation of the snapshot after punctuation and the
                corpus's annotations 【…】 are removed and its variant forms are mapped (VARIANTS); exceptions
                are listed in ALLOW (terms and headings), WITNESS (readings of Wikisource, listed in the
                snapshot's notes), ANNOTATIONS (notes of the corpus quoted in the text) and TRANSLATIONS
                (the Chinese renderings of Kanaya's English)
  4. numbers    every number of the text, with quoted()

Notation of the chapter:
    price band       p~ = min{max{p, p_L}, p_H}, x = max{0, Q - D(p_L)}, y = min{S, max{0, D(p_H) - Q}}
                     S_{t+1} = (1 - delta) (S_t + x_t - y_t)                                   (eq:qinhan-band)
                     the stock as in eq:africa-store (Chapter 14), with this year's purchases also kept a year
    teaching demand  D(p) = Qbar [1 + (P0 - p) / SLOPE], P0 = 30 qian per shi, SLOPE = 60
    quantity         M V = P Y (eq:silver-qty, Chapter 13)
    coin             v = c + tau (vbar - c) (eq:greek-value, Chapter 7); seigniorage 1 - MP/ME (eq:medieval-seigniorage)
                     a 五铢 coin weighs 5 zhu and is worth 1 qian: copper value of a coin = weight / 5 qian
Units (律历志): 1 liang = 24 zhu, 1 jin = 16 liang, 1 jun = 30 jin, 1 shi (weight) = 4 jun; 1 dou = 10 sheng,
1 hu = 10 dou. The grain records use 石 and 斛 as measures of volume; the chapter treats them as one unit.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from common import ROOT, load_snapshot, quoted

sys.path.insert(0, str(ROOT / "data" / "fetch"))
from classical_numerals import checked  # noqa: E402

TEX = ROOT / "zh" / "ch08_qinhan.tex"
GZ, YT = "子藏/法家/管子.txt", "儒藏/语录/盐铁论.txt"

# ---------------------------------------------------------------------------------------------------
# Reign years (first year of each era; negative = BC). The snapshot's notes list the same conversions.
ERA = {"汉": -206, "文帝": -179, "元狩": -122, "元鼎": -116, "元封": -110, "始元": -86, "元康": -65, "神爵": -61,
       "五凤": -57, "初元": -48, "永光": -43, "元始": 1, "居摄": 6, "始建国": 9, "天凤": 14, "地皇": 20, "建武": 25}


def year(era: str, n: int) -> int:
    """The n-th year of an era (no year 0 is crossed by any era used here)."""
    y = ERA[era] + n - 1
    assert (ERA[era] < 0) == (y < 0) or ERA[era] > 0
    return y


# Teaching inputs stated in the text
P0, SLOPE = 30.0, 60.0          # ex:qinhan-band: normal price 30 qian per shi; D(p) = Qbar [1 + (30 - p) / 60]
P_L, P_H = 24.0, 36.0           # the granary's buying and selling prices
DELTA = 0.10                    # losses of the stock per year
QBAR_WAN = 100                  # ex:qinhan-band (2): a normal harvest of 100 wan shi
BAND_FIG = dict(years=30, sd=0.12, seed=8, famine_year=24, famine=0.5, s0=0.0, clip=(0.7, 1.3))
CAST_END = 3                    # ex:qinhan-cast: 元始中 taken as AD 3
MID_YUANDI = -40                # ex:qinhan-cast (3): the middle of 元帝's reign taken as 40 BC
WUZHU_ZHU = 5                   # a 五铢 coin: 5 zhu, worth 1 qian
SC = dict(price=35, share=0.8, harvest_low=0.9, harvest=0.7)


def chk(what: str, value: float, expected: float | None = None, tol: float = 1e-9, rel: float = 0.0) -> float:
    """quoted() with a tolerance for floating-point error on exact values."""
    return quoted(what, float(value), expected, tol=tol, rel=rel)


# ---------------------------------------------------------------------------------------------------
# Loaders
def rows() -> pd.DataFrame:
    df, meta = load_snapshot("qinhan_facts", dtype=str, keep_default_na=False)
    assert 8 in meta["used_in"]
    assert df["id"].is_unique
    return df


def meta() -> dict:
    return load_snapshot("qinhan_facts", dtype=str, keep_default_na=False)[1]


def facts() -> dict[str, list[float]]:
    """id -> the numbers of the value column (several are separated by ';')."""
    return {r.id: [float(x) for x in r.value.split(";")] for r in rows().itertuples() if r.value}


def years() -> dict[str, int]:
    return {r.id: int(r.year) for r in rows().itertuples() if r.year}


# ---------------------------------------------------------------------------------------------------
# 1. The 管子 and 盐铁论 rows against the corpus
def corpus_dir() -> Path | None:
    for c in (os.environ.get("CORPUS"), Path.home() / ".cache" / "finance-study" / "daizhigev20"):
        if c and (Path(c) / GZ).exists() and (Path(c) / YT).exists():
            return Path(c)
    return None


def check_corpus(df: pd.DataFrame) -> None:
    sub = df[df["file"].isin([GZ, YT])]
    c = corpus_dir()
    if c is None:
        print(f"corpus not found: the {len(sub)} 管子 and 盐铁论 quotations are not checked (run tools/setup_env.sh)")
        return
    texts = {f: re.sub(r"\s+", "", (c / f).read_text(encoding="utf-8")) for f in (GZ, YT)}
    for r in sub.itertuples():
        q = re.sub(r"\s+", "", r.quote)
        n = texts[r.file].count(q)
        assert n >= 1, f"{r.id}: quotation not found in {r.file}"
        if r.numeral:
            assert r.numeral in q and float(checked(r.numeral)) == float(r.value), r.id
    quoted("管子 and 盐铁论 quotations found in the corpus", len(sub), 35)


# ---------------------------------------------------------------------------------------------------
# 2. Readings of the numbers: id -> [(context in the quotation, numeral in the context, factor)], in order
def read(s: str) -> float:
    """A numeral of the histories: classical_numerals.checked, plus 亿 (= 万万), a final 万万, 万 alone, 什 and 半."""
    if s.endswith("半"):
        return read(s[:-1]) + 0.5
    if s == "什":
        return 10
    if s == "万":
        return 10_000
    if "亿" in s:
        hi, lo = s.split("亿")
        return read(hi) * 1e8 + (read(lo) if lo else 0)
    if s.endswith("万万"):
        return read(s[:-2]) * 1e8
    return checked(s)


LIANG = 24   # zhu per liang (unit_weight)
READINGS = {
    "lk_grain": [("挟五口", "五"), ("治田百亩", "百"), ("亩一石半", "一半"), ("为粟百五十石", "百五十"),
                 ("税十五石", "十五"), ("余百三十五石", "百三十五")],
    "lk_food": [("人月一石半", "一半"), ("五人", "五"), ("为粟九十石", "九十"), ("余有四十五石", "四十五")],
    "lk_money": [("石三十", "三十"), ("为钱千三百五十", "千三百五十"), ("用钱三百", "三百"), ("余千五十", "千五十")],
    "lk_cloth": [("用钱三百", "三百"), ("五人", "五"), ("用千五百", "千五百"), ("不足四百五十", "四百五十")],
    "gsc_canal": [("谷四百万斛", "四百万"), ("用卒六万人", "六万")],
    "xwz_object": [("费值二万万余", "二万万")],
    "gz_famine": [("米斛万钱", "万")],
    "han_jia": [("米至石万钱", "万"), ("马至匹百金", "百")],
    "fsf_42": [("京师谷石二百余", "二百"), ("边郡四百", "四百"), ("关东五百", "五百")],
    "gz_lianshan": [("什倍之利", "什")],
    "gz_nine": [("之九在上", "九"), ("一在下", "一"), ("万物重十倍", "十")],
    "gz_attr": [("管子二十四卷", "二十四")],
    "jy_fourth": [("货物必平四矣", "四")],
    "wu_baijin": [("值三千", "三千"), ("值五百", "五百"), ("值三百", "三百")],
    "wu_sanzhu": [("更铸三铢钱", "三")],
    "wu_wuzhu": [("铸五铢钱", "五")],
    # 二百八十亿万: read as 280 亿 (the text argues the reading; 亿万 also means 'countless', row gx_yiwan)
    "total_cast": [("成钱二百八十亿万余", "二百八十亿")],
    "lv_zhongri": [("一亿三千四百八万二千二百九十七", "一亿三千四百八万二千二百九十七")],
    "wj_treasury": [("都内钱四十万万", "四十万万"), ("水衡钱二十五万万", "二十五万万"), ("少府钱十八万万", "十八万万")],
    "pz_result": [("漕益岁六百万石", "六百万"), ("帛五百万匹", "五百万")],
    "ytl_tiyao_huan": [("为书凡六十篇", "六十")],
    "wm_daqian": [("重十二铢", "十二"), ("大钱五十", "五十")],
    "wm_dao": [("契刀五百", "五百"), ("一刀直五千", "五千")],
    "wm_qian": [("重一铢", "一"), ("小钱直一", "一"), ("三铢", "三"), ("幺钱一十", "一十"), ("五铢", "五"),
                ("幼钱二十", "二十"), ("七铢", "七"), ("中钱三十", "三十"), ("九铢", "九"), ("壮钱四十", "四十"),
                ("钱货六品", "六")],
    "wm_gold": [("直钱万", "万")],
    "wm_silver": [("直一千五百八十", "一千五百八十"), ("直千", "千"), ("银货二品", "二")],
    "wm_turtle": [("直二千一百六十", "二千一百六十"), ("大贝十朋", "十"), ("直五百", "五百"), ("壮贝十朋", "十"),
                  ("直三百", "三百"), ("幺贝十朋", "十"), ("直百", "百"), ("小贝十朋", "十"), ("龟宝四品", "四")],
    "wm_shell": [("直二百一十六", "二百一十六"), ("直五十", "五十"), ("直三十", "三十"), ("直十", "十"),
                 ("率枚直钱三", "三"), ("贝货五品", "五")],
    "wm_bu": [("重十五铢", "十五"), ("小布一百", "一百"), ("直各加一百", "一百"), ("重一两", "一", LIANG),
              ("而直千钱", "千"), ("布货十品", "十")],
    "wm_two": [("小钱直一", "一"), ("大钱五十", "五十")],
    "wm_wujun": [("过平一钱", "一")],
    "wm_huobu_spec": [("重二十五铢", "二十五"), ("直货泉二十五", "二十五"), ("重五铢", "五"), ("枚直一", "一")],
    "wm_daqian_one": [("俱枚直一", "一"), ("并行尽六年", "六")],
    "wmz_penalty": [("一家铸钱", "一"), ("五家坐之", "五")],
    "unit_weight": [("二十四铢为两", "二十四"), ("十六两为斤", "十六"), ("三十斤为钧", "三十"), ("四钧为石", "四")],
    "unit_volume": [("十升为斗", "十"), ("十斗为斛", "十")],
}
ENGLISH = {"kn_16": [("these 16 sections", 16)], "kn_three": [("into three major parts", 3)]}


def check_readings(df: pd.DataFrame) -> None:
    n = 0
    for r in df.itertuples():
        if not r.value:
            continue
        vals = [float(x) for x in r.value.split(";")]
        q = re.sub(r"[\s，。、；：“”‘’（）]|【[^】]*】", "", r.quote)
        if r.id in ENGLISH:
            got = [v for ctx, v in ENGLISH[r.id] if ctx in r.quote]
        elif r.id in READINGS:
            got, pos = [], 0
            for item in READINGS[r.id]:
                ctx, num, factor = (item + (1,))[:3]
                k = q.find(ctx, pos)
                assert k >= 0, f"{r.id}: {ctx!r} not found (in order) in the quotation"
                assert num.replace("半", "") in ctx.replace("石", "")
                pos = k + len(ctx)
                got.append(read(num) * factor)
        else:
            assert r.numeral, f"{r.id}: a value without a numeral or a reading"
            got = [float(checked(r.numeral))]
        assert got == vals, f"{r.id}: read {got}, value column {vals}"
        n += 1
    quoted("rows with values, each read from its quotation", n, 57)


# ---------------------------------------------------------------------------------------------------
# 3. Every “…” of the text against the snapshot
VARIANTS = str.maketrans({"凖": "准", "鐡": "铁", "嵗": "岁", "徃": "往", "煑": "煮", "鼔": "鼓", "絶": "绝", "乗": "乘",
                          "夲": "本", "寛": "宽", "説": "说", "馀": "余", "硃": "朱",
                          "\ue511": "榷", "\ue3e7": "弊", "\uea5b": "傅"})
PUNCT = re.compile(r"[\s，。、；：！？“”‘’（）《》·…—]")
# terms, headings and phrases of the text that are not quotations
ALLOW = {"深入一步", "劣币驱逐良币", "先秦的", "《管子》说", "管仲说"}
# Wikisource readings the text gives beside the corpus's (each must be listed in the snapshot's notes)
WITNESS = {"淡食", "真工", "五物", "坐市列贩物求利", "贩卖", "以重差小", "所转贩者", "委府于京师"}
# notes of the corpus's annotations 【…】 quoted in the text (each must occur inside 【】 in a quotation)
ANNOTATIONS = {"音谈"}
# the chapter's Chinese renderings of Kanaya's English summary
TRANSLATIONS = {"可以肯定不是一个人、一时写成的": "kn_notone", "是在汉代编成的": "kn_han", "到武帝末年": "kn_wu",
                "基本上与战国时期的原始材料相同": "kn_source",
                "在一定程度上反映了汉代直到武帝时的经济状况": "kn_reflects"}


def norm(s: str) -> str:
    return PUNCT.sub("", re.sub(r"【[^】]*】", "", s).translate(VARIANTS))


def text_quotations() -> list[str]:
    tex = "\n".join(l for l in TEX.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("%"))
    out = re.findall(r"“([^”]*)”", tex)
    out += [q.strip() for q in re.findall(r"\\begin\{quote\}(.*?)\\cite", tex, re.S)]
    return out


def check_text(df: pd.DataFrame) -> None:
    corpus_quotes = [norm(q) for q in df["quote"]]
    ids = set(df["id"])
    notes = meta()["notes"]
    n = 0
    for q in text_quotations():
        for part in q.split("……"):
            if not norm(part):
                continue
            n += 1
            if part in ALLOW:
                continue
            if part in WITNESS:
                assert part in notes, f"Wikisource reading {part!r} is not in the snapshot's notes"
                continue
            if part in ANNOTATIONS:
                assert any(f"【{part}】" in q for q in df["quote"]), part
                continue
            if part in TRANSLATIONS:
                assert TRANSLATIONS[part] in ids
                continue
            assert any(norm(part) in c for c in corpus_quotes), f"not in the snapshot: “{part}”"
    print(f"ok {n} quotations of the text found in the snapshot (or listed as exceptions)")


# ---------------------------------------------------------------------------------------------------
# The models
def demand(p, qbar: float = 1.0):
    return qbar * (1 + (P0 - np.asarray(p, dtype=float)) / SLOPE)


def free_price(q, qbar: float = 1.0):
    """Price at which demand equals the harvest q."""
    return P0 + SLOPE * (1 - np.asarray(q, dtype=float) / qbar)


def band_year(q: float, s: float, p_l: float = P_L, p_h: float = P_H, delta: float = DELTA) -> dict:
    """One year of eq:qinhan-band: purchases x, sales y, the market price, next year's stock and the cash flow."""
    x = max(0.0, q - float(demand(p_l)))
    y = min(s, max(0.0, float(demand(p_h)) - q))
    price = float(free_price(q - x + y))
    return dict(x=x, y=y, price=price, s_next=(1 - delta) * (s + x - y), cash=p_h * y - p_l * x)


def harvests(cfg: dict = BAND_FIG) -> np.ndarray:
    rng = np.random.default_rng(cfg["seed"])
    q = np.clip(rng.normal(1.0, cfg["sd"], cfg["years"]), *cfg["clip"])
    q[cfg["famine_year"] - 1] = cfg["famine"]
    return q


def simulate(cfg: dict = BAND_FIG) -> pd.DataFrame:
    q, s, out = harvests(cfg), cfg["s0"], []
    for t, qt in enumerate(q, start=1):
        r = band_year(qt, s)
        out.append(dict(year=t, harvest=qt, free=float(free_price(qt)), stock=s, **r))
        s = r["s_next"]
    return pd.DataFrame(out)


def metal_value(weight_zhu: float) -> float:
    """Copper of a coin in qian, at the 五铢 standard (5 zhu = 1 qian)."""
    return weight_zhu / WUZHU_ZHU


def coins() -> pd.DataFrame:
    """Wang Mang's copper coins and spades (and the 五铢, 货布, 货泉): weight in zhu, face value in qian."""
    F = facts()
    q, d, b, h = F["wm_qian"], F["wm_daqian"], F["wm_bu"], F["wm_huobu_spec"]
    out = [("五铢", "wuzhu", WUZHU_ZHU, 1, "五铢")]
    names = ["小钱", "幺钱", "幼钱", "中钱", "壮钱"]
    out += [(n, "qian", q[2 * i], q[2 * i + 1], "钱货") for i, n in enumerate(names)]
    out.append(("大钱", "qian", d[0], d[1], "钱货"))
    names_row = rows().set_index("id").loc["wm_bu_names", "quote"]
    bu = names_row.rstrip("。").split("、")[::-1]                     # listed from the largest to the smallest
    w0, v0, step_v, w1, v1, n_bu = b
    for i, n in enumerate(bu):
        out.append((n, "bu", w0 + i, v0 + i * step_v, "布货"))
    assert out[-1][2] == w1 and out[-1][3] == v1 and len(bu) == n_bu
    out += [("货布", "huobu", h[0], h[1] * h[3], "天凤"), ("货泉", "huoquan", h[2], h[3], "天凤")]
    df = pd.DataFrame(out, columns=["name", "kind", "weight", "face", "group"])
    df["metal"] = metal_value(df["weight"])
    df["multiple"] = df["face"] / df["metal"]
    df["seigniorage"] = 1 - df["metal"] / df["face"]
    return df


def price_records() -> pd.DataFrame:
    """The grain prices of the chapter (qian per shi or hu): year, value, grain, lower bound, place."""
    F, Y = facts(), years()
    recs = [("gz_famine", 0, "米", False, "关中"), ("wd_cheap", 0, "粟", True, "天下"), ("xd_5", 0, "谷", False, "天下"),
            ("zcg_8", 0, "谷", False, "金城、湟中"), ("cpg_famine", 0, "谷", True, "齐地"),
            ("fsf_42", 0, "谷", True, "京师"), ("fsf_42", 1, "谷", False, "边郡"), ("fsf_42", 2, "谷", False, "关东"),
            ("wm_famine", 0, "米", False, "雒阳以东")]
    out = [dict(id=i, year=Y[i], price=F[i][k], grain=g, lower=lo, place=pl) for i, k, g, lo, pl in recs]
    # 黄金一斤易粟一斛 at the official 黄金重一斤，直钱万: a derived point
    out.append(dict(id="hhs_gold", year=Y["hhs_gold"], price=F["wm_gold"][0], grain="粟", lower=False, place="天下"))
    return pd.DataFrame(out)


# ---------------------------------------------------------------------------------------------------
# 4. The text, section by section
def opening(F, Y):
    chk("始元六年 (BC)", -year("始元", 6), 81)
    assert Y["ytl_edict"] == Y["debate_81"] == -81
    chk("宣帝: grain at (qian per shi)", F["xd_5"][0], 5)
    chk("初元二年 (BC)", -year("初元", 2), 47)
    chk("    grain at, more than", F["cpg_famine"][0], 300)
    chk("    years between 62 and 47 BC", Y["cpg_famine"] - Y["xd_5"], 15)
    chk("    ratio", F["cpg_famine"][0] / F["xd_5"][0], 60)
    chk("元狩五年 (BC)", -year("元狩", 5), 118)
    chk("元始 from (AD)", year("元始", 1), 1)
    chk("    to", year("元始", 5), 5)
    chk("coins cast (read as)", F["total_cast"][0], 2.8e10)
    chk("宝货 品", F["wm_total"][0], 28)
    chk("大钱: zhu", F["wm_daqian"][0], 12)
    chk("    face", F["wm_daqian"][1], 50)
    chk("王莽: 始建国元年", year("始建国", 1), 9)
    chk("    地皇四年", year("地皇", 4), 23)


def roadmap(F):
    chk("zhu per liang", F["unit_weight"][0], 24)
    chk("liang per jin", F["unit_weight"][1], 16)
    chk("jin per jun", F["unit_weight"][2], 30)
    chk("jun per shi", F["unit_weight"][3], 4)
    chk("sheng per dou", F["unit_volume"][0], 10)
    chk("dou per hu", F["unit_volume"][1], 10)
    chk("耿寿昌: hu a year", F["gsc_canal"][0], 4e6)
    chk("桑弘羊: shi a year", F["pz_result"][0], 6e6)


def world(F, Y, ids):
    chk("半两 in zhu", F["unit_weight"][0] / 2, 12)
    chk("荚钱: rice per shi", F["han_jia"][0], 10000)
    chk("高帝二年 (BC)", -year("汉", 2), 205)
    assert Y["gz_famine"] == -205
    chk("    rice per hu", F["gz_famine"][0], 10000)
    chk("文帝: millet, more than", F["wd_cheap"][0], 10)
    chk("管子: juan", F["gz_attr"][0], 24)
    chk("    sections called 管子轻重", F["gz_tiyao_19"][0], 19)
    lost = [i for i in ids if i.startswith("gz_lost")]
    chk("    lost", len(lost), 3)
    chk("    extant", F["gz_tiyao_19"][0] - len(lost), F["kn_16"][0])
    chk("    Kanaya: extant sections", F["kn_16"][0], 16)
    chk("    parts", F["kn_three"][0], 3)
    chk("盐铁论: chapters", F["ytl_tiyao_huan"][0], 60)
    chk("元始二年 (AD)", year("元始", 2), 2)
    assert Y["pop_households"] == Y["pop_people"] == 2
    chk("households", F["pop_households"][0], 12_233_062)
    chk("people", F["pop_people"][0], 59_594_978)
    chk("    per household", F["pop_people"][0] / F["pop_households"][0], 4.87, tol=0.005)


def qingzhong(F):
    nine, one, times = F["gz_nine"]
    chk("山国轨: tenths held by the state", nine, 9)
    chk("    by the people", one, 1)
    chk("    prices x", times, 10)
    m = (nine + one) / one
    chk("ex:qinhan-nine (1): money in the people's hands x", m, 10)
    chk("    prices x (V, Y fixed)", m, times)
    chk("(2) Y halved: prices x", m / 0.5, 20)
    chk("(3) gross profit / outlay", times - 1, 9)
    chk("什倍之利", F["gz_lianshan"][0], 10)


def granary(F, Y):
    _, _, _, harvest, tax, left = F["lk_grain"]
    _, people, food, sell = F["lk_food"]
    price, revenue, rites, cash = F["lk_money"]
    per, _, cloth, gap = F["lk_cloth"]
    chk("李悝: people", F["lk_grain"][0], 5)
    chk("    mu", F["lk_grain"][1], 100)
    chk("    harvest (shi)", harvest, 150)
    chk("    tax", tax, harvest / 10)
    chk("    food", food, 90)
    chk("    to sell", harvest - tax - food, sell)
    chk("    = 45", sell, 45)
    chk("    price", price, 30)
    chk("    revenue", sell * price, revenue)
    chk("    = 1350", revenue, 1350)
    chk("    rites", rites, 300)
    chk("    left", revenue - rites, cash)
    chk("    = 1050", cash, 1050)
    chk("    clothes", per * people, cloth)
    chk("    = 1500", cloth, 1500)
    chk("    shortfall", cloth - cash, gap)
    chk("    = 450", gap, 450)
    need = rites + cloth
    chk("ex:qinhan-budget (1): cash needed", need, 1800)
    be = need / sell
    chk("    break-even price", be, 40)
    chk("    above 30 by", be / price - 1, 1 / 3, tol=1e-12)
    chk("(2) shortfall in shi", gap / price, 15)
    chk("    = the tax", gap / price, tax)
    chk("    without the tax: revenue", (sell + tax) * price, need)
    chk("(3) a city household's extra outlay", food * (be - price), 900)
    chk("宣帝: 谷至石五钱", F["xd_cheap"][0], 5)
    chk("耿寿昌: soldiers", F["gsc_canal"][1], 60000)
    chk("    海租 x", F["gsc_haizu"][0], 3)
    chk("萧望之: cost, more than (qian)", F["xwz_object"][0], 2e8)
    chk("五凤四年 (BC)", -year("五凤", 4), 54)
    assert Y["gsc_cpg"] == Y["xd_cpg"] == -54
    chk("初元五年 (BC)", -year("初元", 5), 44)
    assert Y["yd_abolish"] == -44
    chk("常平仓 lasted (years, by 元帝纪)", Y["yd_abolish"] - Y["xd_cpg"], 10)


def band_example():
    chk("ex:qinhan-band: elasticity at 30", -(-1 / SLOPE) * P0 / float(demand(P0)), 0.5)
    for q, p in ((1.2, 18), (0.8, 42), (0.5, 60)):
        chk(f"    free price at harvest {q}", float(free_price(q)), p)
    chk("    D(24)", float(demand(P_L)), 1.1)
    chk("    D(36)", float(demand(P_H)), 0.9)
    good = band_year(1.2, 0.0, delta=0.0)
    bad = band_year(0.8, good["s_next"], delta=0.0)
    chk("(2) bought (wan shi)", good["x"] * QBAR_WAN, 10)
    chk("    cost (wan qian)", -good["cash"] * QBAR_WAN, 240)
    chk("    sold", bad["y"] * QBAR_WAN, 10)
    chk("    revenue", bad["cash"] * QBAR_WAN, 360)
    chk("    profit", (good["cash"] + bad["cash"]) * QBAR_WAN, 120)
    chk("    / cost", (good["cash"] + bad["cash"]) / -good["cash"], 0.5)
    chk("    prices", good["price"], P_L)
    chk("    ", bad["price"], P_H)
    good = band_year(1.2, 0.0)
    bad = band_year(0.8, good["s_next"])
    chk("(3) stock after a year (wan shi)", good["s_next"] * QBAR_WAN, 9)
    chk("    market supply", 0.8 + bad["y"], 0.89)
    chk("    price", bad["price"], 36.6)
    chk("    revenue (wan qian)", bad["cash"] * QBAR_WAN, 324)
    chk("    profit", (good["cash"] + bad["cash"]) * QBAR_WAN, 84)
    need = float(demand(P_H)) - 0.5
    chk("(4) stock to hold 36 in a great famine", need, 0.4)
    chk("    wan shi", need * QBAR_WAN, 40)
    chk("    / one good year's purchase", need / 0.1, 4)


def band_figure():
    sim = simulate()
    cfg = BAND_FIG
    chk("qinhan_band: years", len(sim), 30)
    chk("    sd of harvests", cfg["sd"], 0.12)
    chk("    clipped at", cfg["clip"][0], 0.7)
    chk("    and", cfg["clip"][1], 1.3)
    chk("    famine year", cfg["famine_year"], 24)
    chk("    famine harvest", cfg["famine"], 0.5)
    chk("    losses", DELTA, 0.10)
    chk("    initial stock", cfg["s0"], 0)
    low, high = sim["free"] < P_L - 1e-9, sim["free"] > P_H + 1e-9
    chk("    years below the buying price, held", (sim.loc[low, "price"] >= P_L - 1e-9).sum(), low.sum())
    chk("    years above the selling price", high.sum(), 9)
    chk("        held", (sim.loc[high, "price"] <= P_H + 1e-9).sum(), 2)
    f = sim.loc[sim["year"] == cfg["famine_year"]].iloc[0]
    before = sim.loc[sim["year"] == cfg["famine_year"] - 1].iloc[0]
    assert before["y"] > 0 and before["s_next"] < 1e-3 and f["stock"] < 1e-3 and f["price"] > P_H + 20   # almost used up
    chk("    famine: price with the granary", f["price"], None)
    chk("    maximum stock", sim["stock"].max(), None)
    split = 10                                   # 头十年 and 后二十年 of the text
    mc = monte_carlo(split=split)
    chk("1000 paths: share of years above the selling price (%)", 100 * mc["need_high"], 20, tol=0.5)
    chk("    held (%)", 100 * mc["held_high"], 35, tol=0.5)
    chk("    share below the buying price (%)", 100 * mc["need_low"], 20, tol=0.5)
    chk("    held (%)", 100 * mc["held_low"], 100)
    chk("    first 10 years (the granary starts empty): selling price held (%, 约四分之一)", 100 * mc["held_high_early"],
        25, tol=2)
    chk("    years 11-30: held (%, 约四成)", 100 * mc["held_high_late"], 40, tol=2.5)
    chk("    the first (头十年) and the later (后二十年) years", split, 10)
    chk("    ", cfg["years"] - split, 20)


def monte_carlo(n: int = 1000, cfg: dict = BAND_FIG, split: int = 10) -> dict:
    """The band of ex:qinhan-band on n paths of the figure's harvests without the famine (seeds 0..n-1).

    held_high_early / held_high_late: the share of years above the selling price that are held, in the first
    `split` years of each path (the granary starts empty) and in the remaining years."""
    need_h = held_h = need_l = held_l = 0
    need_e = held_e = 0
    for seed in range(n):
        q = np.clip(np.random.default_rng(seed).normal(1.0, cfg["sd"], cfg["years"]), *cfg["clip"])
        s = cfg["s0"]
        for t, qt in enumerate(q, start=1):
            r = band_year(qt, s)
            p = float(free_price(qt))
            if p > P_H + 1e-9:
                need_h += 1
                held_h += r["price"] <= P_H + 1e-9
                if t <= split:
                    need_e += 1
                    held_e += r["price"] <= P_H + 1e-9
            if p < P_L - 1e-9:
                need_l += 1
                held_l += r["price"] >= P_L - 1e-9
            s = r["s_next"]
    years = n * cfg["years"]
    return dict(need_high=need_h / years, held_high=held_h / need_h, need_low=need_l / years, held_low=held_l / need_l,
                held_high_early=held_e / need_e, held_high_late=(held_h - held_e) / (need_h - need_e))


def monopoly(F, Y):
    chk("元狩四年 (BC)", -year("元狩", 4), 119)
    assert Y["wd_need"] == Y["si_ban"] == -119
    chk("元封元年 (BC)", -year("元封", 1), 110)
    assert Y["pz_sang"] == -110
    chk("漕益岁 (shi)", F["pz_result"][0], 6e6)
    chk("帛 (pi)", F["pz_result"][1], 5e6)
    chk("    / 耿寿昌's 4 million hu", F["pz_result"][0] / F["gsc_canal"][0], 1.5)


def debate(F, Y):
    chk("元帝: years without the salt and iron offices", F["yuandi_salt"][0], 3)
    chk("81 BC to 初元二年", Y["debate_81"] - Y["cpg_famine"], None)
    for y in (Y["cpg_famine"], Y["yd_abolish"]):
        assert 30 < y - Y["debate_81"] < 40      # 三十多年后
    assert 30 < Y["debate_81"] - Y["wu_sanguan"] < 40   # 三官专铸到盐铁之议：三十多年后
    assert Y["ytl_qx_ban"] == Y["debate_81"] == -81


def mint(F, Y):
    chk("文帝五年 (BC)", -year("文帝", 5), 175)
    assert Y["wd_free"] == -175
    chk("    四铢", F["wd_free"][0], 4)
    chk("皮币 (qian)", F["wu_pibi"][0], 400000)
    chk("白金", F["wu_baijin"][0], 3000)
    chk("    ", F["wu_baijin"][1], 500)
    chk("    ", F["wu_baijin"][2], 300)
    chk("三铢", F["wu_sanzhu"][0], 3)
    chk("五铢", F["wu_wuzhu"][0], 5)
    chk("    元狩五年", Y["wu_wuzhu"], -118)
    chk("赤仄: one for", F["wu_chize_coin"][0], 5)
    chk("amnesty: 5 years after 119 BC", Y["wu_amnesty"], Y["wu_pibi"] + 5)
    chk("元鼎二年 (BC)", -year("元鼎", 2), 115)
    assert Y["wd_tang"] == Y["wu_chize"] == -115
    chk("三官 (BC): two years later", -(Y["wd_tang"] + 2), 113)
    assert Y["wu_sanguan"] == -113
    zr, yr = F["lv_zhongri"][0], F["lv_yueri"][0]
    chk("律历志: 见中日法", zr, 134_082_297)
    chk("    见月日法", yr, 44_694_099)
    chk("    ratio", zr / yr, 3)
    cast = F["total_cast"][0]
    literal = 280e8 * 1e4
    chk("literal reading", literal, 2.8e14)
    chk("    per person (wan)", literal / F["pop_people"][0] / 1e4, 470, tol=0.5)
    t = F["wj_treasury"]
    chk("王嘉传: 都内 (qian)", t[0], 4e9)
    chk("    水衡", t[1], 2.5e9)
    chk("    少府", t[2], 1.8e9)
    tot = sum(t)
    chk("    total (亿)", tot / 1e8, 83)
    n = CAST_END - Y["wu_wuzhu"] - 1          # no year 0
    chk("ex:qinhan-cast (1): years", n, 120)
    chk("    a year (亿)", cast / n / 1e8, 2.33, tol=0.005)
    chk("(2) per person", cast / F["pop_people"][0], 470, tol=0.5)
    chk("    per household", cast / F["pop_households"][0], 2289, tol=0.5)
    chk("(3) treasuries / total (%)", 100 * tot / cast, 29.6, tol=0.05)
    m = MID_YUANDI - Y["wu_wuzhu"]
    chk("    years to 40 BC", m, 78)
    chk("    cast by then (亿)", cast / n * m / 1e8, 182, tol=0.5)
    chk("    treasuries / cast by then (%)", 100 * tot / (cast / n * m), 46, tol=0.5)
    chk("贡禹: workers", F["gongyu_cost"][0], 100000)
    per_day = cast / n / F["gongyu_cost"][0] / 365
    chk("    coins per worker per day", per_day, 6.4, tol=0.05)
    chk("    literal reading", literal / n / F["gongyu_cost"][0] / 365 / 1e4, 6.4, tol=0.05)
    chk("    literal: total / treasuries (wan)", literal / tot / 1e4, 3.37, tol=0.005)


def wangmang(F, Y):
    chk("居摄二年 (AD)", year("居摄", 2), 7)
    assert Y["wm_daqian"] == Y["wmz_7"] == 7
    chk("契刀", F["wm_dao"][0], 500)
    chk("错刀", F["wm_dao"][1], 5000)
    chk("始建国二年", year("始建国", 2), 10)
    assert Y["wmz_10"] == Y["wm_baohuo"] == 10
    per_kind = {"钱货": 6, "金货": 1, "银货": F["wm_silver"][2], "龟宝": F["wm_turtle"][8], "贝货": F["wm_shell"][5],
                "布货": F["wm_bu"][5]}
    chk("钱货 品", F["wm_qian"][10], 6)
    chk("银货 品", per_kind["银货"], 2)
    chk("龟宝 品", per_kind["龟宝"], 4)
    chk("贝货 品", per_kind["贝货"], 5)
    chk("布货 品", per_kind["布货"], 10)
    chk("    sum", sum(per_kind.values()), F["wm_total"][0])
    chk("    names", len(per_kind), 6)
    chk("    copper 品", per_kind["钱货"] + per_kind["布货"], 16)
    chk("金: a jin", F["wm_gold"][0], 10000)
    chk("银: 朱提", F["wm_silver"][0], 1580)
    chk("    other", F["wm_silver"][1], 1000)
    tu, sh = F["wm_turtle"], F["wm_shell"]
    for k, (turtle, shell) in enumerate(((tu[0], sh[0]), (tu[2], sh[1]), (tu[4], sh[2]), (tu[6], sh[3]))):
        assert tu[2 * k + 1] == 10 and turtle == 10 * shell, (turtle, shell)
    chk("元龟", tu[0], 2160)
    chk("    = 10 x 大贝", tu[0] / sh[0], 10)
    chk("公龟, 侯龟, 子龟", tu[2], 500)
    chk("    ", tu[4], 300)
    chk("    ", tu[6], 100)
    chk("贝: 大, 壮, 幺, 小, single", sh[0], 216)
    chk("    ", sh[1], 50)
    chk("    ", sh[2], 30)
    chk("    ", sh[3], 10)
    chk("    ", sh[4], 3)
    # sizes and weights printed in tab:qinhan-coins: (row, form in the quotation, form in the table); the table
    # writes the leading 一 that the quotation omits, so both forms are read and compared
    tex = TEX.read_text(encoding="utf-8")
    quote = rows().set_index("id")["quote"]

    def length_fen(s: str) -> int:
        """尺二寸 -> 120, 寸五分 -> 15, 二寸四分 -> 24 (1 尺 = 10 寸 = 100 分; a unit without a numeral counts one)."""
        return sum((checked(n) if n else 1) * {"尺": 100, "寸": 10, "分": 1}[u]
                   for n, u in re.findall(r"([一二三四五六七八九十]?)([尺寸分])", s))

    sizes = [("wm_turtle", "元龟岠冉长尺二寸", "元龟长一尺二寸", 120), ("wm_turtle", "公龟九寸", "公龟九寸", 90),
             ("wm_turtle", "侯龟七寸以上", "侯龟七寸以上", 70), ("wm_turtle", "子龟五寸以上", "子龟五寸以上", 50),
             ("wm_bu", "小布长寸五分", "小布长一寸五分", 15), ("wm_bu", "各相长一分", "每品长一分", 1),
             ("wm_bu", "长二寸四分", "大布长二寸四分", 24)]
    for rid, in_quote, in_table, fen in sizes:
        assert in_quote in quote[rid] and in_table in tex, (rid, in_quote, in_table)
        chk(f"tab:qinhan-coins: {in_table} (fen)", length_fen(in_table), length_fen(in_quote))
        chk("    ", length_fen(in_table), fen)
    chk("    小布 + 9 steps of 1 fen = 大布 (fen)", length_fen("寸五分") + (F["wm_bu"][5] - 1) * length_fen("一分"),
        length_fen("二寸四分"))
    for rid, in_quote, in_table, numeral, value in (("wm_gold", "黄金重一斤", "黄金一斤", "一", 1),
                                                    ("wm_silver", "重八两为一流", "朱提银八两为一流", "八", 8)):
        assert in_quote in quote[rid] and in_table in tex and numeral in in_quote and numeral in in_table
        chk(f"tab:qinhan-coins: {in_table}", float(checked(numeral)), value)
    C = coins()
    q = C.set_index("name")
    for n, w, v in (("小钱", 1, 1), ("幺钱", 3, 10), ("幼钱", 5, 20), ("中钱", 7, 30), ("壮钱", 9, 40), ("大钱", 12, 50),
                    ("小布", 15, 100), ("大布", 24, 1000), ("货布", 25, 25), ("货泉", 5, 1)):
        assert (q.loc[n, "weight"], q.loc[n, "face"]) == (w, v), n
    chk("大布: one liang in zhu", q.loc["大布", "weight"], F["unit_weight"][0])
    chk("ex:qinhan-wm (1) 大钱 copper (qian)", q.loc["大钱", "metal"], 2.4)
    chk("    multiple", q.loc["大钱", "multiple"], 20.8, tol=0.05)
    chk("    seigniorage (%)", 100 * q.loc["大钱", "seigniorage"], 95.2, tol=0.05)
    chk("(2) 大布 copper", q.loc["大布", "metal"], 4.8)
    chk("    multiple", q.loc["大布", "multiple"], 208, tol=0.5)
    chk("    seigniorage (%)", 100 * q.loc["大布", "seigniorage"], 99.5, tol=0.05)
    small = q.loc["小钱", "face"] * q.loc["大钱", "weight"] / q.loc["小钱", "weight"]
    chk("(3) twelve 小钱", small, 12)
    chk("    gain", q.loc["大钱", "face"] - small, 38)
    chk("    (%)", 100 * (q.loc["大钱", "face"] - small) / small, 317, tol=0.5)
    chk("(4) 天凤元年", year("天凤", 1), 14)
    assert Y["wm_daqian_one"] == 14
    chk("    大钱 to", F["wm_daqian_one"][0], 1)
    chk("    loss (%)", 100 * (1 - F["wm_daqian_one"][0] / q.loc["大钱", "face"]), 98)
    chk("figure: lines at multiples", 20, None)
    chk("    ", 200, None)
    chk("    multiples from", C["multiple"].min(), 1)
    chk("    to", C["multiple"].max(), 208, tol=0.5)
    qian = C[(C["group"] == "钱货") & (C["name"] != "小钱")]["multiple"]
    chk("figure (b): 钱货 except 小钱 from", qian.min(), 17, tol=0.5)
    chk("    to", qian.max(), 22, tol=0.5)
    bu = C[C["group"] == "布货"]["multiple"]
    chk("    布货 from", bu.min(), 33, tol=0.5)
    chk("    to", bu.max(), 208, tol=0.5)
    chk("小钱 multiple", q.loc["小钱", "multiple"], 5)
    chk("货泉 multiple", q.loc["货泉", "multiple"], 1)
    chk("货布 multiple", q.loc["货布", "multiple"], 5)
    chk("五均: cities besides 长安", F["wm_wudu"][0], 5)
    chk("六斡", F["wm_liuwo"][0], 6)
    chk("五均: over the 市平 by (qian)", F["wm_wujun"][0], 1)
    chk("    interest a year at most (%)", 10, None)
    chk("    王莽传中: a month (%)", 3, None)
    chk("货布: zhu", F["wm_huobu_spec"][0], 25)
    chk("    worth 货泉", F["wm_huobu_spec"][1], 25)
    chk("货泉: zhu", F["wm_huobu_spec"][2], 5)
    chk("    worth", F["wm_huobu_spec"][3], 1)
    chk("大钱 circulates for (years)", F["wm_daqian_one"][1], 6)
    chk("地皇元年", year("地皇", 1), 20)
    assert Y["wmz_20"] == 20
    chk("    食货志 vs 王莽传下 (years)", Y["wmz_20"] - Y["wm_huobu"], 6)
    chk("一家, 五家", F["wmz_penalty"][0], 1)
    chk("    ", F["wmz_penalty"][1], 5)
    chk("地皇二年", year("地皇", 2), 21)
    assert Y["wmz_100k"] == 21
    wmz10 = rows().set_index("id").loc["wmz_10", "quote"]
    assert "但行小大钱二品而已" in wmz10
    chk("王莽传中, 始建国二年: coins still in use (小大钱二品)", len(F["wm_two"]), 2)
    chk("雒阳以东: rice per shi", F["wm_famine"][0], 2000)
    chk("建武十六年", year("建武", 16), 40)
    assert Y["hhs_wuzhu"] == 40


def test(F, Y):
    P = price_records()
    chk("records in the figure", len(P), 10)
    chk("highest / lowest", P["price"].max() / P["price"].min(), 2000)
    chk("永光二年 (BC)", -year("永光", 2), 42)
    assert Y["fsf_42"] == -42
    chk("京师, 边郡, 关东", F["fsf_42"][0], 200)
    chk("    ", F["fsf_42"][1], 400)
    chk("    ", F["fsf_42"][2], 500)
    chk("    highest / lowest", F["fsf_42"][2] / F["fsf_42"][0], 2.5)
    upper = F["fsf_42"][0] + 100            # 二百余: at least 200, below 300
    chk("    二百余 below", upper, 300)
    chk("    关东 / 京师 at least", F["fsf_42"][2] / upper, 1.7, tol=0.05)
    chk("赵充国: grain per hu", F["zcg_8"][0], 8)
    chk("神爵元年 (BC)", -year("神爵", 1), 61)
    chk("元康四年 (BC)", -year("元康", 4), 62)
    g = (F["cpg_famine"][0] / F["xd_5"][0]) ** (1 / (Y["cpg_famine"] - Y["xd_5"])) - 1
    chk("62 to 47 BC as a yearly rate (%)", 100 * g, 31, tol=0.5)
    chk("gold: a jin of gold = qian", F["wm_gold"][0], 10000)
    chk("文帝: plotted at (BC)", -Y["wd_cheap"], 170)
    chk("常平仓 shading from", -Y["xd_cpg"], 54)
    chk("    to", -Y["yd_abolish"], 44)


def legacy_and_takeaways(F):
    chk("takeaways: 40 qian, 450 = the tax", F["lk_cloth"][3] / F["lk_money"][0], F["lk_grain"][4])


def selfcheck(F):
    sell = F["lk_food"][3]
    chk("SC1: revenue at 35", sell * SC["price"], 1575)
    chk("    short of 1800 by", F["lk_money"][2] + F["lk_cloth"][2] - sell * SC["price"], 225)
    chk("SC2: money x", 1 / (1 - SC["share"]), 5)
    chk("SC3: free price at 0.9", float(free_price(SC["harvest_low"])), 36)
    chk("    at 0.7", float(free_price(SC["harvest"])), 48)
    chk("    stock needed", float(demand(P_H)) - SC["harvest"], 0.2)
    w, v = 12, 50
    chk("SC4: 大钱 at the 小钱 standard: multiple", v / (w * 1), 4.17, tol=0.005)
    chk("    seigniorage (%)", 100 * (1 - w / v), 76)


def main():
    df = rows()
    F, Y, ids = facts(), years(), set(df["id"])
    check_corpus(df)
    check_readings(df)
    check_text(df)
    for k in ("淡食", "所转贩者"):
        assert k in meta()["notes"]
    opening(F, Y)
    roadmap(F)
    world(F, Y, ids)
    qingzhong(F)
    granary(F, Y)
    band_example()
    band_figure()
    monopoly(F, Y)
    debate(F, Y)
    mint(F, Y)
    wangmang(F, Y)
    test(F, Y)
    legacy_and_takeaways(F)
    selfcheck(F)
    print("all Chapter 8 checks passed")


if __name__ == "__main__":
    main()
