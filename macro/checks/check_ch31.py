"""Chapter 31 (苏联工业化与社会主义核算论战): every number and every quotation in zh/ch31_soviet.tex.

    python3 checks/check_ch31.py

Inputs:
  soviet_facts        quotations of Stalin's report of 7 January 1933 (Works, vol. 13, Marxists Internet Archive), the
                      State Planning Commission's plan in its English edition of 1929 and its report on the fulfilment
                      of the plan (Moscow, 1933), the Soviet Union Information Bureau's handbook of 1929, Mises (1920,
                      in Hayek's collection of 1935), Lange (1938), Hayek (1945), Markevich, Naumenko and Qian (NBER WP
                      29089), Rudnytskyi et al. (2015), Cameron (2016), Werth (2016), Davies (2004), Cheremukhin,
                      Golosov, Guriev and Tsyvinski (NBER WP 19425), Gregory and Harrison (2005), Harrison (1980, 2017),
                      Markevich and Harrison (2011), Harrison and Markevich (2018), the Nobel press releases of 1973 and
                      1975 and the authority records of the Library of Congress (checked by
                      data/fetch/verify_web_quotes.py); the rows with an empty quotation are values and words read on
                      page images (the tables of the Gosplan report of 1933, the budget table of Socialist Construction
                      in the U.S.S.R., 1936, Table A.2 of Markevich, Naumenko and Qian, Harrison 1993), with a
                      transcription between « and » in the note
  soviet_grain        the USSR's grain harvest (official, revised by Markevich, Naumenko and Qian, and the range of
                      Davies and Wheatcroft) and the state's procurement, 1927-1939, million tons (their Table A.2)
  maddison2023_ussr   GDP per head of the USSR and six other economies, 1913-1940 (Maddison Project Database 2023)
The figure module figsrc/fig_ch31.py imports its data from here.

What is checked here:
  1. readings   every number of the value column of soviet_facts is read from its quotation (digits, English number
                words, ordinals, fractions, a decimal comma and the OCR's misreadings, each named in the note)
  2. the text   every “…” of the chapter is the chapter's rendering of a quotation (TRANSLATIONS), with the source's
                words listed in KEYWORDS (for a row read on a page image, the words of its transcription)
  3. numbers    every number of the text, section by section: said() finds the phrase and compares each number it
                prints (with its unit 万, 亿) with the value computed from the snapshots or with a teaching input
                stated in the text, within half a unit of the last printed digit; Chinese numerals are read by zh()
  4. coverage   every Arabic number of the text (outside labels, citations, cross-references, the key equations and
                math sub- and superscripts) lies inside a phrase checked by said()
  5. the book   identities of the table snapshots, second witnesses, life dates, what other chapters tell, the
                bibliography block of the chapter and its licence notices
  6. anchors    the paraphrase anchors `% 据: ...` name rows of soviet_facts

Models (the chapter's key equations):
    material balances (eq:soviet-balance): x = Ax + f, solved and expanded as f + Af + A^2 f + ...; one round of
        corrections leaves a gap of A^2 times the change
    Lange's trial and error (eq:soviet-lange): p_{t+1} = p_t + lambda [D(p_t) - S(p_t)]; with linear D and S the gap
        to the equilibrium price is multiplied by 1 - lambda (b + d) each round
    index numbers (eq:soviet-index): Laspeyres and Paasche quantity indices, the Fisher index between them; growth at
        early-year prices exceeds growth at late-year prices when the fastest-growing good becomes cheaper
"""
from __future__ import annotations

import math
import os
import re
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from common import ROOT, anchors, load_snapshot, quoted

TEX = Path(os.environ.get("CH31_TEX", ROOT / "zh" / "ch31_soviet.tex"))   # a scratch copy for mutation tests
GUIDE = "没有市场价格，经济能不能算清楚该生产什么？"
PREV = GUIDE                                         # Chapter 30's NEXT
NEXT = "如果人人都想多储蓄，总储蓄为什么可能反而减少？"   # Chapter 32's question
# Teaching inputs stated in the text
BAL = {"a12": 0.1, "a21": 2.0, "f": (8.0, 20.0), "steel2": 10.0}       # ex:soviet-balance: 1 = steel, 2 = coal
LANGE = {"a": 100, "b": 2, "c": 10, "d": 1, "p0": 10, "lam": 0.2, "lam2": 0.8}   # ex:soviet-lange: D = a - bp, S = c + dp
IDX = {"m": (2, 10), "pm": (10, 4), "g": (80, 80), "pg": (1, 1.2)}    # ex:soviet-index: machines and grain, years 0, 1
SC1 = {"coal": 25}                                   # self-check 1: coal's final use 20 -> 25
SC3 = {"d": 3}                                       # self-check 3: S = 10 + 3p
SC6 = {"years": 12}                                  # self-check 6
M4, Y8, M6, B9 = 10 ** 4, 10 ** 8, 10 ** 6, 10 ** 9
SIX = ["SUN", "USA", "GBR", "DEU", "JPN", "ARG", "IND"]                # fig:soviet_gdp
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                      "September", "October", "November", "December"], 1)}


def chk(what: str, value, expected=None, tol: float = 1e-6, rel: float = 0.0) -> float:
    """quoted() with a tolerance for floating-point error and for the six decimals of the value column (2/3 is
    0.666667); a list is compared element by element."""
    if isinstance(value, (list, tuple, np.ndarray, pd.Series)):
        value = list(value)
        assert expected is not None and len(value) == len(expected), (what, value, expected)
        for i, (v, e) in enumerate(zip(value, expected)):
            quoted(f"{what} [{i + 1}]", float(v), e, tol=tol, rel=rel)
        return float(value[0])
    return quoted(what, float(value), expected, tol=tol, rel=rel)


# ---------------------------------------------------------------------------------------------------
# Loaders
@lru_cache(maxsize=None)
def _rows() -> pd.DataFrame:
    df, m = load_snapshot("soviet_facts", dtype=str, keep_default_na=False)
    assert 31 in m["used_in"]
    assert df["id"].is_unique
    return df


@lru_cache(maxsize=None)
def meta() -> dict:
    return load_snapshot("soviet_facts")[1]


def num(x: str) -> float:
    return float(x)


def facts() -> dict[str, list[float]]:
    """id -> the numbers of the value column (several are separated by ';')."""
    return {r.id: [num(x) for x in r.value.split(";")] for r in _rows().itertuples() if r.value}


def years() -> dict[str, int]:
    return {r.id: int(r.year) for r in _rows().itertuples() if r.year.isdigit()}


@lru_cache(maxsize=None)
def quotes() -> dict[str, str]:
    """id -> the quotation, with the line breaks of the source joined."""
    return {r.id: " ".join(r.quote.split()) for r in _rows().itertuples()}


@lru_cache(maxsize=None)
def column(name: str) -> dict[str, str]:
    return {r.id: getattr(r, name) for r in _rows().itertuples()}


def transcription(rid: str) -> str:
    """The words of a row read on a page image, as its note transcribes them between « and »."""
    m = re.search(r"«(.*)»", column("note")[rid])
    assert m, f"{rid}: no transcription in the note"
    return m.group(1)


def mon(rid: str, name: str) -> int:
    """The month `name`, asserted to be in the quotation (or the note) of row rid."""
    text = quotes()[rid] or column("note")[rid]
    assert name in text, (rid, name)
    return MONTHS[name]


def _table(name: str) -> tuple[pd.DataFrame, dict]:
    df, m = load_snapshot(name)
    assert 31 in m["used_in"], name
    assert "sources" not in m, name                                # table snapshots carry no 'sources' key
    return df, m


def grain() -> pd.DataFrame:
    """Markevich, Naumenko and Qian, Table A.2, panel II: the USSR's grain, million tons, indexed by year."""
    df, _ = _table("soviet_grain")
    assert list(df.year) == [1927, 1928, 1929, 1930, 1931, 1932, 1933, 1937, 1939]
    return df.set_index("year")


def maddison_meta() -> dict:
    return _table("maddison2023_ussr")[1]


def maddison() -> pd.DataFrame:
    """GDP per head (2011 international dollars), economies by ISO code x years 1913-1940."""
    df, _ = _table("maddison2023_ussr")
    return df.pivot(index="country", columns="year", values="gdppc_2011usd")


def ussr() -> pd.Series:
    return maddison().loc["SUN"]


def ratio(y: int, base: int = 1913) -> float:
    """The USSR's GDP per head in year y, per cent of the base year."""
    U = ussr()
    return 100 * U[y] / U[base]


def cagr(a: float, b: float, n: int) -> float:
    return 100 * ((b / a) ** (1 / n) - 1)


def fall(a: float, b: float) -> float:
    """The fall from a to b, per cent."""
    return 100 * (1 - b / a)


def rise(a: float, b: float) -> float:
    return 100 * (b / a - 1)


def hm_prices() -> dict[tuple[str, int], float]:
    """Harrison and Markevich, Table 2: the price level as a multiple of 1913, on the first day of each month named."""
    Q = quotes()
    heads = re.findall(r"(January|February|March|April|May|June|July|August|September|October|November|December) "
                       r"(\d{4})", Q["hm_head"])
    body = Q["hm_prices"].split("1913", 1)[1]
    scale = {"thousand": 10 ** 3, "million": 10 ** 6, "billion": 10 ** 9}
    vals = [float(x) * scale.get(u, 1) for x, u in re.findall(r"(\d+(?:\.\d+)?)(?: (thousand|million|billion))?",
                                                                 body)]
    assert len(heads) == len(vals) == 8, (heads, vals)
    return {(m, int(y)): v for (m, y), v in zip(heads, vals)}


def plan_items() -> list[tuple[str, float, float, float]]:
    """fig:soviet_plan: (item, output of 1927/28, output of 1932, the plan for 1932/33), in the plan's units (billion
    rubles at the prices of 1926/27, million tons). Gross output: 1928 for 1927/28 (the report's text, p. 11); pig iron
    and steel: 1927/28 from the text (p. 108), 1932 from the table of p. 112; coal and oil: the table of p. 99."""
    F = facts()
    out = [("gross", F["gp33_gross"][0], F["gp33_gross"][2], F["gp33_937"][2]),
           ("pig", F["gp33_pig28"][2] / M6, F["gp33i_world"][1], F["gp33_task"][2]),
           ("steel", F["gp33_steel28"][0] / M6, F["gp33i_world"][3], F["gp33_task"][3]),
           ("coal", F["gp33i_coal"][1], F["gp33i_coal"][3], F["gp33i_coal"][2]),
           ("oil", F["gp33i_oil"][1], F["gp33i_oil"][3], F["gp33i_oil"][2])]
    assert out[1][3] == F["gp29_pig"][1] and out[3][3] == F["gp29_targets"][1] and out[4][3] == F["gp29_oil"][3]
    return out


def table1() -> dict[str, list[float]]:
    """Harrison (1993), Table 1, as transcribed: period -> TsSU, CIA, Khanin."""
    out = {}
    for rid in ("h93_t1_2840", "h93_t1_4050", "h93_t1_2850", "h93_t1_5087", "h93_t1_2887"):
        m = re.match(r"(\d{4})–(\d{2}) (\d+\.\d) (\d+\.\d) (\d+\.\d)", transcription(rid))
        assert m, rid
        a, b = int(m.group(1)), int(m.group(2))
        assert [float(m.group(i)) for i in (3, 4, 5)] == facts()[rid], rid
        out[f"{a}-{a // 100 * 100 + b}"] = facts()[rid]
    return out


# ---------------------------------------------------------------------------------------------------
# 1. Readings of the numbers
SMALL = {"a": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "twelve": 12, "thirteen": 13, "twenty": 20, "thirty": 30, "fifty": 50, "ninety": 90}
MULT = {"hundred": 100, "thousand": 1000}
NTH = {"first": 1, "second": 2, "fifth": 5, "sixth": 6, "tenth": 10}
FRAC = {"one fifth": 0.2, "two fifths": 0.4, "four fifths": 0.8, "two-thirds": 2 / 3, "a quarter": 0.25,
        "one quarter": 0.25, "a third": 1 / 3, "three quarters": 0.75, "half": 0.5}
TIMES = {"twice": 2}


def cardinal(s: str) -> float:
    """An English cardinal: 'six', 'twenty-five', 'a' (in 'more than a million')."""
    total, part = 0, 0
    for w in s.lower().replace("-", " ").split():
        if w == "and":
            continue
        if w in SMALL:
            part += SMALL[w]
        else:
            part = max(part, 1) * MULT[w]
            if MULT[w] >= 1000:
                total, part = total + part, 0
    return float(total + part)


def figure(s: str) -> float:
    """'3,283,000', '93.7', '.5'."""
    return float(s.replace(",", ""))


def read(word: str, how: str) -> list[float]:
    if how == "num":
        return [figure(word)]
    if how == "en":
        return [cardinal(word)]
    if how == "nth":
        return [float(NTH[word.lower()])]
    if how == "frac":
        return [FRAC[word.lower()]]
    if how == "times":
        return [float(TIMES[word.lower()])]
    if how == "comma":                         # '11,6': a decimal comma of the OCR
        return [float(word.replace(",", "."))]
    raise ValueError(how)


FIGURES = re.compile(r"\d[\d,]*(?:\.\d+)?|\.\d+")
EN, NUM = "en", "num"
# id -> [(phrase, how)], in order. A phrase 'context|word' is searched as a whole and read from `word`. Rows not
# listed are read with all the figures of the quotation.
READINGS = {
    "st_fouryears": [("four", EN), ("in |four", EN), ("three", EN)],
    "st_937": [("five", EN), ("93.7", NUM)],
    "st_telegraph": [("1932", NUM)],
    "gp29_metal": [("10", NUM), ("1932", NUM), ("-|33", NUM), ("three", EN), ("1927", NUM), ("-|28", NUM)],
    "gp29_oil": [("11,6", "comma"), ("1927", NUM), ("-|28", NUM), ("21.7", NUM), ("1932", NUM), ("-|33", NUM)],
    "gp33_937": [("1932", NUM), ("-|33", NUM), ("36.6", NUM), ("in |1932", NUM), ("34.3", NUM), ("1926", NUM),
                 ("-|27", NUM), ("four", EN), ("a quarter", "frac"), ("93.7", NUM)],
    "su_bank": [("1921", NUM), ("ten", EN)],
    "su_two": [("two", EN)],
    "mi_note": [("April, |1920", NUM)],
    "la_reprint": [("1936", NUM), ("1937", NUM)],
    "la_second": [("second", "nth")],
    "hy_derision": [("twenty-five", EN)],
    "mnq_half": [("half", "frac")],
    "mnq_kulaks": [("two", EN)],
    "mnq_lose": [("11", NUM), ("1932", NUM), ("fifty", EN)],
    "mnq_1921": [("1921", NUM), ("-|22", NUM), ("Approximately |5", NUM)],
    "ca_15": [("1.5", NUM), ("a quarter", "frac")],
    "ca_kazakhs": [("1.5", NUM), ("1.3", NUM), ("a third", "frac")],
    "ca_1930": [("1930", NUM)],
    "ca_concession": [("17", NUM), ("1932", NUM), ("three", EN)],
    "ca_ninety": [("ninety", EN)],
    "we_total": [("6.5", NUM), ("7", NUM), ("4.2", NUM), ("1.3", NUM), ("1.5", NUM), ("than |a", EN)],
    "we_fled": [("twelve", EN), ("thirteen", EN)],
    "we_arrests": [("200,000", NUM), ("1932", NUM), ("-|33", NUM)],
    "dv_fate": [("37", NUM)],
    "dv_double": [("1930", NUM), ("1928", NUM)],
    "cg_black": [("twice", "times"), ("1929", NUM), ("1930", NUM), ("4.5", NUM), ("1931", NUM), ("7", NUM),
                 ("1932", NUM), ("28", NUM)],
    "gr_balances": [("thirty", EN), ("eight", EN), ("four", EN)],
    "gr_fifty": [("fifty", EN), ("1925", NUM)],
    "gr_courage": [("1929", NUM)],
    "h17_cliff": [("one fifth", "frac"), ("three", EN), ("two fifths", "frac"), ("1918", NUM)],
    "h17_1921": [("1921", NUM), ("five", EN)],
    "h17_breathing": [("Tenth", "nth"), ("1921", NUM)],
    "h17_gosplan": [("two", EN)],
    "h17_envisaged": [("two-thirds", "frac")],
    "h17_famine": [("1932", NUM), ("six", EN), ("1921", NUM)],
    "h17_feb1930": [("1930", NUM), ("two", EN)],
    "h17_half90": [("half", "frac"), ("1930", NUM), ("90", NUM), ("1936", NUM)],
    "h17_fourfifths": [("four fifths", "frac"), ("four", EN), ("1934", NUM), ("1937", NUM)],
    "h17_better": [("1935", NUM)],
    "mh_trend": [("1913", NUM), ("1.74", NUM), ("1920", NUM), ("one quarter", "frac")],
    "mh_allen": [("1930", NUM)],
    "mh_threequarters": [("three quarters", "frac"), ("five", EN), ("1933", NUM), ("1937", NUM)],
    "hm_13m": [("13", NUM), ("one", EN), ("ten", EN)],
    "hm_forces": [("1921", NUM)],
    "loc_stalin": [("1878", NUM), ("-|1953", NUM)],
    "loc_lenin": [("1870", NUM), ("-|1924", NUM)],
    "loc_mises": [("1881", NUM), ("-|1973", NUM)],
    "loc_lange": [("1904", NUM), ("-|1965", NUM)],
    "loc_hayek": [("1899", NUM), ("-|1992", NUM)],
    "loc_preobrazhensky": [("1886", NUM), ("-|1937", NUM)],
    "loc_bukharin": [("1888", NUM), ("-|1938", NUM)],
    "loc_kantorovich": [("1912", NUM), ("-|1986", NUM)],
    "loc_trotsky": [("1879", NUM), ("-|1940", NUM)],
}
# the misreadings of the OCR, each named in the note of its row and printed in the quotation
MISPRINTS = [("gp33_gross", "incr@ised"), ("gp33_216", "inicreased"), ("gp33_oil", "thé"), ("gp33_oil", "tons_"), ("gp33_937", "34.3."),
             ("gp29_oil", "11,6"), ("gp29_copyright", "Livericut"), ("gp29_pig", "pig tron"),
             ("mi_note", "Sozialzvissenschaften"), ("la_copyright", "hoo\\"), ("la_reprint", "Nos. i and 2")]
IMAGE_NOTE = "read on the page image"


def check_readings(df: pd.DataFrame) -> None:
    src = meta()["sources"]
    n = img = 0
    for r in df.itertuples():
        assert r.file in src, (r.id, r.file)
        if src[r.file]["format"] == "image":                 # a value read on a page image: no quotation
            assert not r.quote and IMAGE_NOTE in r.note and r.id not in READINGS, r.id
            img += 1
            continue
        assert r.quote, f"{r.id}: no quotation"
        if not r.value:
            assert r.id not in READINGS, r.id
            continue
        vals = [num(x) for x in r.value.split(";")]
        q = " ".join(r.quote.split())
        if r.id in READINGS:
            got, pos = [], 0
            for phrase, how in READINGS[r.id]:
                context, _, word = phrase.rpartition("|")
                k = q.find(context + word, pos)
                assert k >= 0, f"{r.id}: {phrase!r} not found (in order) in the quotation"
                pos = k + len(context + word)
                got += read(word, how)
        else:
            got = [figure(x.rstrip(",")) for x in FIGURES.findall(q)]
        assert [round(g, 6) for g in got] == [round(v, 6) for v in vals], f"{r.id}: read {got}, value column {vals}"
        n += 1
    quoted("rows with values, each read from its quotation", n, 162)
    quoted("rows read on a page image (no quotation)", img, 19)
    N, Q = column("note"), quotes()
    for rid, word in MISPRINTS:
        assert word in N[rid], (rid, word)                  # every misreading is named in the note
        assert word in Q[rid], (rid, word)                  # and printed in the quotation
    assert "a decimal comma" in N["gp29_oil"] and "Davis and Wheatcroft" in transcription("mnq_table")


# ---------------------------------------------------------------------------------------------------
# 2. Every “…” of the text against the snapshot
# the chapter's Chinese renderings of the quotations: rendering -> row (or rows)
TRANSLATIONS = {
    # opening
    "严格地说，如果加上特别季度，是四年零三个月": "st_fouryears",
    "我们没有钢铁工业，这是国家工业化的基础。现在有了。我们没有拖拉机工业。现在有了。我们没有汽车工业。现在有了。": "st_iron",
    "在沉默与彻底的被遗弃中": "we_daily",
    "挤到了背后，挤进了地下": "h17_squeezed",
    "只有在黑暗中摸索": "mi_groping",
    # sec:soviet-world
    "废除了所有主要的资本主义制度": "cg_1917",
    "战时共产主义": "cg_requisition",
    "多种力量的产物": "hm_forces",
    "喘息的时机": "h17_breathing",
    "为农业与小规模制造业重新引入了市场经济": "mnq_nep",
    "等于十个金卢布": "su_bank",
    "以黄金与稳定的外币作准备": "su_bank",
    "一种稳定的货币，与一种严重膨胀、灾难性地贬值的货币并行流通": "su_two",
    "剪刀差": "h80_scissors",
    "商品荒": "h80_goods",
    "把小商品生产部门的剩余产品转给社会化的工业": "h80_redistribute",
    "乌拉尔—西伯利亚方法": ("we_ural", "dv_ural"),
    "大转变": "cg_greatturn",
    # sec:soviet-plan
    "最优": "mh_april",
    "五年计划四年完成": "st_slogan",
    "基本": "gp29_variants",
    "最高": "gp29_variants",
    "这些是要靠强攻夺取的堡垒。": "gp29_assault",
    "实现这些目标的巨大困难，必须坦率地正视。": "gp29_faced",
    "一般物价水平有步骤地降低": "gp29_prices",
    "保证切尔文的购买力提高 20\\%": "gp29_chervonets",
    "失业仍将是苏联生活中不利的一面": "gp29_unemp",
    "为高速度站着": "gr_courage",
    "谈论现实的计划之类": "h17_thrash",
    "其实不是计划，是一场赌博": "st_gamble",
    "这就是一部分资产阶级报刊的意见。那些发表这些意见的人，几乎不值得批评。": "st_section",
    "落在了五年计划给它定的数字后面": "gp33_lagged",
    "在五年计划期间，我们的工业整体平均每年增长 21.6\\%": "gp33_216",
    "1926/27 年度不变价格": "h93_unchanged",
    "在第一个五年计划期间，工业产值平均每年增长 22\\%。": "st_22",
    "我想，在第二个五年计划里，我们必须采取工业产值平均每年至少增长 13\\%—14\\% 的速度。": "st_22",
    # sec:soviet-balances
    "物资平衡": "h17_balances",
    "紧绷": ("h80_hunter", "h80_taut"),
    "一种珍贵的商品": "gr_money",
    "在工人为食物付的价格与农民得到的价格之间打进了一个楔子": "cg_salestax",
    # sec:soviet-famine
    "一揽子政策": "mnq_bundle",
    "取消私有财产，把农民组织进政府能直接控制的大型集体农庄": "mnq_bundle",
    "是的，完全正确，尽管在这个过程中有过一些过火的行为。": "st_tempo",
    "富农": ("mnq_kulaks", "st_remnants"),
    "饥饿的消息传到了莫斯科，但政府没有降低征购": "mnq_1931",
    "藏起来的粮食": "we_search",
    "可能失去乌克兰": "mnq_lose",
    "集体化运动当然是一场可怕的失败。它已经把俄国带到了饥荒的边缘。": "st_nyt",
    "垂死阶级的最后残余": "st_remnants",
    "他们放火烧仓库，破坏机器。他们组织怠工。": "st_wreck",
    "阻止农民从这些地区大批外流": "mnq_border",
    "关于防止饥饿的农民大批外逃": "ru_directive",
    "已经够骇人了": "dv_10m",
    "1933 年死亡人数的巨大差别，与那一年净迁移的估计很不相同有关": "ru_related",
    "迁出的人越多，重建出来的死亡就越少": "ru_larger",
    "以传闻为根据，值得怀疑": "ru_anecdotal",
    "乌克兰（苏联）生产的粮食足以避免乌克兰（苏联）的饥荒": "mnq_enough",
    "对迁移的限制加重了死亡": "mnq_restrict",
    "乌克兰民族主义": "we_arrests",
    "在定居基础上的全盘集体化": "ca_sedent",
    # sec:soviet-calculation
    "理性经济的废除": "mi_abolition",
    "没有市场关系，经济核算是不可想象的": "hy_trotsky",
    "魔鬼代言人": "la_devil",
    "随意选定的一套价格": "la_random",
    "第二道防线": "la_second",
    "关于特定时间与地点的具体情况的知识": "hy_time",
    "现场的人": "hy_spot",
    "几根指针的移动": "hy_telecom",
    # sec:soviet-growth
    "Gerschenkron 效应": "h93_gersch",
    "生活变得更好了": "h17_better",
    # sec:soviet-debate
    "对核算并不在意": "gr_indifferent",
    "资本主义与斯大林主义之外真正的另一种选择": "dv_alternative",
    "想必抬高了幸存者的平均消费": "mh_survivors",
    "难以接受": "mh_swallow",
    "斯大林政策下福利损失的下限": "cg_lower",
    "没有找到支持大推进理论的证据": "cg_bigpush",
    # the note on sources
    "1921 年 4 月": "su_april",
    "直到 1923 年才实现": "h17_stab",
    "increased": "gp33_means",
    "incr@ised": "gp33_gross",
    "the": "gp33_oil",
    "thé": "gp33_oil",
    "11,6": "gp29_oil",
    "Livericut": "gp29_copyright",
    "pig tron": "gp29_pig",
    "Sozialzvissenschaften": "mi_note",
    "Davis": "mnq_table",
    # sec:soviet-legacy and the ending
    "资源最优配置理论": "nb75_prize",
    "我们消灭了失业，使苏联的工人摆脱了失业的恐怖。": "st_unemp",
}
# the words of the source that each rendering renders (for a row read on a page image: of its transcription)
KEYWORDS = {
    "st_fouryears": ["strictly speaking, in four years and three months, if the special quarter be added"],
    "st_iron": ["We did not have an iron and steel industry, the basis for the industrialisation of the country. Now "
                "we have one."],
    "we_daily": ["in silence and total abandonment"],
    "h17_squeezed": ["squeezed private ownership and trade into the background and the underground"],
    "mi_groping": ["There is only groping in the dark."],
    "cg_1917": ["abolished all major capitalist institutions"],
    "cg_requisition": ["War Communism"],
    "hm_forces": ["a product of many forces"],
    "h17_breathing": ["'breathing space'"],
    "mnq_nep": ["re-introduced a market economy for agriculture and small-scale manufacturing"],
    "su_bank": ["(equal to ten gold rubles)", "backed by a reserve of gold and stable foreign currencies"],
    "su_two": ["a stable currency circulating side by side with a highly inflated and catastrophically depreciating "
               "currency"],
    "h80_scissors": ["scissors crisis"],
    "h80_goods": ["'goods famine'"],
    "h80_redistribute": ["redistribute the surplus product of the petty commodity sector towards socialized industry"],
    "we_ural": ['"Ural-Siberian method."'],
    "dv_ural": ['"Ural-Siberian method"'],
    "cg_greatturn": ["Great Turn"],
    "mh_april": ['"optimal" variant'],
    "st_slogan": ['"The Five-Year Plan in Four Years."'],
    "gp29_variants": ['"basic" and "maximum" variants'],
    "gp29_assault": ["They are strongholds which will literally have to be taken by assault."],
    "gp29_faced": ["The great difficulties in the way of attaining these objectives must be frankly faced."],
    "gp29_prices": ["a systematic reduction in the general level of prices"],
    "gp29_chervonets": ["to guarantee a 20 per cent increase in the purchasing power of the chervonetz"],
    "gp29_unemp": ["unemployment, which will still remain one of the adverse aspects of Soviet life"],
    "gr_courage": ["prefer to stand up . . . for high rates of expansion"],
    "h17_thrash": ["who talk to you about realistic plans and so on"],
    "st_gamble": ["is really not a plan. It is a gamble."],
    "st_section": ["Such are the opinions of one section of the bourgeois press. It is hardly worth while to "
                   "criticise those who gave utterance to these opinions."],
    "gp33_lagged": ["lagged behind the figures set for it by the Five-Year Plan"],
    "gp33_216": ["During the Five-Year Plan period, our industry as a whole - inicreased on the average 21.6 per cent per "
                 "annum"],
    "h93_unchanged": ["'unchanged prices of 1926/27'"],
    "st_22": ["In the period of the First Five-Year Plan the average annual increase in industrial output was 22 per "
              "cent.", "I think that in the Second Five-Year Plan we will have to adopt a 13-14 per cent average annual "
              "increase in industrial output as a minimum."],
    "h17_balances": ["'material balances'"],
    "h80_hunter": ["excessive 'tautness'"],
    "h80_taut": ["'Taut' planning"],
    "gr_money": ["money remained a prized commodity"],
    "cg_salestax": ["drove a wedge between what workers paid for food and what farmers received"],
    "mnq_bundle": ["a bundle of policies", "the removal of private property and organizing peasants into large "
                   "collective farms that the government could control directly"],
    "st_tempo": ["Yes, it was absolutely right, even though certain excesses were committed in the process."],
    "mnq_kulaks": ["(kulaks)"],
    "st_remnants": ["the kulaks and kulak agents"],
    "mnq_1931": ["News of starvation traveled to Moscow, but the government did not lower procurement."],
    "we_search": ['"hidden grain"'],
    "mnq_lose": ['"could lose Ukraine"'],
    "st_nyt": ["The collectivisation campaign is of course a ghastly failure. It has brought Russia to the verge of "
               "famine."],
    "st_wreck": ["They set fire to warehouses and wreck machinery. They organise sabotage."],
    "mnq_border": ["to prevent a mass migration of peasants out of these areas"],
    "ru_directive": ['"On the prevention of a mass exodus of starving peasants,"'],
    "dv_10m": ["horrendous enough"],
    "ru_related": ["the large difference in 1933 deaths is related to very different estimates of net migration for "
                   "that year"],
    "ru_larger": ["the larger the number of net out-migrants, the smaller the number of reconstructed deaths"],
    "ru_anecdotal": ["are based on anecdotal evidence and are questionable"],
    "mnq_enough": ["Ukraine (the Soviet Union) produced enough food in 1932 to avoid famine in Ukraine (the Soviet "
                   "Union)"],
    "mnq_restrict": ["migration restrictions exacerbated mortality"],
    "we_arrests": ['"Ukrainian nationalism,"'],
    "ca_sedent": ['"full collectivization on the basis of sedentarization,"'],
    "mi_abolition": ["Socialism is the abolition of rational economy."],
    "hy_trotsky": ['"economic accounting is unthinkable without market relations"'],
    "la_devil": ["the great advocatus diaboli of their cause"],
    "la_random": ["a given set of prices chosen at random"],
    "la_second": ["a second line of defense"],
    "hy_time": ["the knowledge of the particular circumstances of time and place"],
    "hy_spot": ['"man on the spot."'],
    "hy_telecom": ["to watch merely the movement of a few pointers"],
    "h93_gersch": ["'Gerschenkron effect'"],
    "h17_better": ["'Life has become better, comrades,'"],
    "gr_indifferent": ["This regime was indifferent to calculation"],
    "dv_alternative": ["offered a genuine alternative to both capitalism and Stalinism"],
    "mh_survivors": ["Presumably, their absence helped to lift the average consumption of the survivors."],
    "mh_swallow": ["This assessment is hard for us to swallow."],
    "cg_lower": ["a lower bound on welfare losses under Stalin's policies"],
    "cg_bigpush": ["we find no evidence supporting theories of the Big Push"],
    "su_april": ["April, 1921"],
    "h17_stab": ["Stabilization was achieved only in 1923."],
    "gp33_means": ["increased 2.6 fold"],
    "gp33_gross": ["incr@ised"],
    "gp33_oil": ["thé", "the output of oil and gas"],
    "gp29_oil": ["11,6"],
    "gp29_copyright": ["Livericut"],
    "gp29_pig": ["pig tron"],
    "mi_note": ["Sozialzvissenschaften"],
    "mnq_table": ["Davis and Wheatcroft"],
    "nb75_prize": ["the theory of optimum allocation of resources"],
    "st_unemp": ["we have abolished unemployment and have saved the workers of the U.S.S.R. from its horrors"],
}


def tex_text() -> str:
    return "\n".join(l for l in TEX.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("%"))


def text_quotations() -> list[str]:
    return re.findall(r"“([^”]*)”", tex_text())


def source_words(rid: str) -> str:
    """What a row's KEYWORDS are checked against: the quotation, or the transcription of a page image."""
    return quotes()[rid] or transcription(rid)


def check_text(df: pd.DataFrame) -> None:
    ids = set(df["id"])
    used, n = set(), 0
    for q in text_quotations():
        n += 1
        used.add(q)
        assert q in TRANSLATIONS, f"not listed: “{q}”"
        t = TRANSLATIONS[q]
        for rid in (t,) if isinstance(t, str) else t:
            assert rid in ids, rid
            assert rid in KEYWORDS, f"{rid}: no KEYWORDS"
            if q.isascii():
                assert q in source_words(rid), (q, rid)
    stale = set(TRANSLATIONS) - used
    assert not stale, f"listed but not in the text: {sorted(stale)}"
    for rid, words in KEYWORDS.items():
        for w in words:
            assert w in source_words(rid), f"{rid}: {w!r} not in the quotation"
    assert set(KEYWORDS) == {r for t in TRANSLATIONS.values() for r in ((t,) if isinstance(t, str) else t)}
    img = sorted(r for r in KEYWORDS if not quotes()[r])
    print(f"ok {n} quotations of the text found in the snapshot ({len(img)} rows by their transcriptions)")


# ---------------------------------------------------------------------------------------------------
# 3. Numbers: said() and the parts of the text it does not read
UNITS = {"万亿": 10 ** 12, "亿": 10 ** 8, "万": 10 ** 4}
AMOUNT = re.compile(r"(\d[\d,]*(?:\.\d+)?)(?:\s*多?(万亿|亿|万))?")
# what is not a number of the story: labels, citations, cross-references, the key equations (models() reads them)
# and the sub- and superscripts of the math
MASKS = [re.compile(r"\\begin\{keyeq\}.*?\\end\{keyeq\}", re.DOTALL),
         re.compile(r"\\(?:label|cite|chref|secref|figref|tabref|exref|eqref|ref|nameref|url|fig)\{[^}]*\}"),
         re.compile(r"_\{[^}]*\}|_\d"),
         re.compile(r"\^\{\(?\d\)?\}|\^\{-1\}|\^\{12\}"),
         re.compile(r"\\begin\{tabularx\}\{\\linewidth\}\{[^\n]*")]                # the column widths of the table
COVERED: list[str] = []                    # the phrases said() has read


def mask(s: str) -> str:
    """The string with the parts that print no number of the story blanked out (same length)."""
    for p in MASKS:
        s = p.sub(lambda m: " " * len(m.group(0)), s)
    return s


def say(*phrases: str) -> None:
    """The phrases are in the text."""
    t = tex_text()
    for s in phrases:
        assert s in t, f"not in the text: {s!r}"


def said(phrase: str, *values: float | None, slack: float = 0.0) -> None:
    """The phrase is in the text, and each number it prints (with its unit 万, 亿) is the value given, within half a
    unit of its last digit (plus `slack`, in the same units). None skips a number (one checked by an assertion)."""
    say(phrase)
    found = AMOUNT.findall(mask(phrase).replace("{,}", ","))
    assert len(found) == len(values), f"{phrase!r}: {len(found)} numbers {found}, {len(values)} values"
    for (digits, unit), v in zip(found, values):
        if v is None:
            continue
        scale = UNITS.get(unit, 1)
        decimals = len(digits.split(".")[1]) if "." in digits else 0
        tol = (0.5 * 10 ** -decimals + slack) * scale
        quoted(f"{phrase[:60]!r}: {digits}{unit}", float(v), figure(digits) * scale, tol=tol + 1e-9 * scale)
    COVERED.append(phrase)


ZH_DIGITS = {"一": 1, "两": 2, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
ZH_UNITS = {"十": 10, "百": 100, "千": 1000, "万": 10 ** 4}


def zh(s: str) -> float:
    """A Chinese numeral of the text: '五', '十', '二十五', '九成', '三分之一', '一半'."""
    if "分之" in s:
        b, a = s.split("分之")
        return zh(a) / zh(b)
    if s.endswith("成"):                               # 九成 = nine tenths
        return zh(s[:-1]) / 10
    if s == "一半":
        return 0.5
    total, part = 0, 0
    for ch in s:
        if ch in ZH_DIGITS:
            part = ZH_DIGITS[ch]
        else:
            unit = ZH_UNITS[ch]
            total += max(part, 1) * unit
            part = 0
    return float(total + part)


def told(phrase: str, pre: str, post: str = "") -> float:
    """The phrase is in the text; the Chinese numeral it prints between `pre` and `post` (to the end of the phrase when
    post is empty), read by zh()."""
    say(phrase)
    m = re.search(re.escape(pre) + ("(.+?)" + re.escape(post) if post else "(.+)$"), phrase)
    assert m, (phrase, pre, post)
    return zh(m.group(1))


def coverage() -> None:
    """Every Arabic number of the text lies inside a phrase read by said()."""
    t = tex_text()
    m = mask(t)
    covered = bytearray(len(t))
    for s in set(COVERED):
        k = t.find(s)
        while k >= 0:
            covered[k:k + len(s)] = b"\x01" * len(s)
            k = t.find(s, k + 1)
    runs = list(re.finditer(r"\d+", m))
    bad = [(r.group(), t[max(0, r.start() - 25):r.end() + 10].replace("\n", " ")) for r in runs
           if not all(covered[r.start():r.end()])]
    for b in bad:
        print("    not read:", b)
    assert not bad, f"{len(bad)} numbers of the text not read by said()"
    print(f"ok all {len(runs)} numbers of the text are read by said() ({len(set(COVERED))} phrases)")


def citation_year(s: str) -> int:
    return int(re.search(r"\((\d{4})\)", s).group(1))


def allen_year() -> int:
    """The year of Allen's Farm to Factory, as Davies's review names it: '(Princeton, 2003)'."""
    return int(re.search(r"Farm to Factory: .*?\(Princeton, (\d{4})\)", meta()["sources"]["davies2004"]["version"])
               .group(1))


# ---------------------------------------------------------------------------------------------------
# 4. Numbers, section by section
def guide(F, Y, Q):
    t = TEX.read_text(encoding="utf-8")
    assert f"\\guidequestion{{{GUIDE}}}" in t and GUIDE == PREV
    ch30 = (ROOT / "zh" / "ch30_alternatives.tex").read_text(encoding="utf-8")
    ch30 = "\n".join(l for l in ch30.splitlines() if not l.lstrip().startswith("%"))
    assert ch30.rstrip().endswith(PREV)                                       # 第 30 章交来的问题
    said("描述战时共产主义、新经济政策与 1928 年起的五年计划", F["gp29_period"][0])
    said("概括米塞斯（1920）、兰格（1936—1937）与哈耶克（1945）", F["mi_note"][0], *F["la_reprint"], Y["hy_notice"])


def opening(F, Y, Q):
    d7, y33 = F["st_date"]
    assert "January 7, 1933" in Q["st_date"] and Q["st_plenum"].startswith("Joint Plenum")
    said("1933 年 1 月 7 日，斯大林", y33, mon("st_date", "January"), d7)
    four, four2, three = F["st_fouryears"]
    chk("    four years (四年)", four, told("而用四年完成这个计划", "而用", "年"))
    chk("    four years and three months (四年零三个月)", [four2, three],
        [told("是四年零三个月", "是", "年零"), told("是四年零三个月", "年零", "个月")])
    assert "last quarter of 1930" in Q["gp33_special"]
    said("特别季度是 1930 年的最后一个季度", F["gp33_special"][0])
    five, p937 = F["st_937"]
    said("为五年制订的工业总产值计划完成了 93.7\\%，重工业的计划完成了 108\\%", p937, F["st_108"][0])
    chk("    five years (为五年制订)", five, told("为五年制订的", "为", "年"))
    d22, y = F["we_telegram"]
    said("1933 年 1 月 22 日，斯大林发出一封秘密电报", y, mon("we_telegram", "January"), d22)
    y, a, b = F["we_daily"]
    assert "between January and July 1933" in Q["we_daily"]
    said("在饥荒最重的 1933 年 1 月到 7 月，那里每天有 1.5 万到 2 万人死去", y, 1, mon("we_daily", "July"), a, b)
    said("照 Werth（2016）的说法", Y["we_daily"])
    said("与 1921 年的饥荒不同", F["h17_famine"][2])
    assert "no official acknowledgement" in Q["h17_famine"]
    said("照 Harrison（2017）的概括", Y["h17_squeezed"])
    said("1920 年 4 月，米塞斯", F["mi_note"][0], mon("mi_note", "April"))
    t = tex_text()
    para = t[t.index("1920 年 4 月，米塞斯"):].split("\n")[0]
    assert para.endswith(GUIDE)                                                 # the opening ends with the question


def world(F, Y, Q):
    said("1917 年，布尔什维克掌握了政权", F["cg_1917"][0])
    fifth, three, two5, y18 = F["h17_cliff"]
    said("照 Harrison（2017）的估计，俄国的国民产出在三年的世界大战里下降了五分之一，1918 年一年又下降了五分之二", Y["h17_cliff"],
         y18)
    chk("    three years of war (三年)", three, told("在三年的世界大战里", "在", "年的"))
    chk("    one fifth (五分之一)", fifth, told("世界大战里下降了五分之一", "下降了"))
    chk("    two fifths (五分之二)", two5, told("一年又下降了五分之二", "又下降了"))
    _, y18b, p50, y13 = F["cg_1918"]
    assert y18b == y18
    said("按 Cheremukhin 等人（2013）转述的估计，1918 年的 GDP 比 1913 年低了一半", Y["cg_1918"], y18b, y13)
    chk("    half (低了一半)", p50 / 100, told("比 1913 年低了一半", "低了"))
    said("内战期间的“战时共产主义”，要征收农业产出的 70\\%", F["cg_requisition"][0])
    m13, one, ten = F["hm_13m"]
    said("照 Harrison 与 Markevich（2018）的估计，到经济开始恢复的时候，已有 1,300 万人过早地死去", Y["hm_13m"], m13 * M6)
    chk("    nearly one in ten (将近十分之一)", one / ten, told("将近战前人口的十分之一", "人口的"))
    P = hm_prices()
    assert Q["hm_prices"].startswith("Price level as a multiple of 1913")
    said("1917 年 11 月的物价是 1913 年的 10.2 倍", 1917, 11, 1913, P[("November", 1917)])
    said("到 1921 年 7 月是 8.07 万倍，到 1924 年 2 月是 163 亿倍", 1921, 7, P[("July", 1921)], 1924, 2,
         P[("February", 1924)])
    y21, five = F["h17_1921"]
    said("1921 年，南部与东部的收成失败，超过 500 万人死去", y21, five * M6)
    assert "southern and eastern regions" in Q["h17_1921"] and F["hm_forces"] == [y21]
    # the New Economic Policy
    tenth, y21 = F["h17_breathing"]
    said("1921 年 3 月，在第十次党代表大会上", y21, mon("h17_breathing", "March"))
    chk("    the Tenth Congress (第十次)", tenth, told("在第十次党代表大会上", "第", "次"))
    chk("    two months before (两个月前)", F["h17_gosplan"][0], told("宣布新经济政策的两个月前", "政策的", "个月前"))
    said("按 Gregory 与 Harrison（2005）的说法，国家计委 1921 年 2 月成立，到 1925 年还只有 50 名专家", Y["gr_feb1921"],
         F["gr_feb1921"][0], mon("gr_feb1921", "February"), F["gr_fifty"][1], F["gr_fifty"][0])
    # the chervonets
    y21, ten = F["su_bank"]
    said("1921 年 11 月，国家银行成立", y21, mon("su_bank", "November"))
    assert "A year later it was empowered to issue its own note" in Q["su_bank"]
    say("一年以后，它获准发行自己的银行券")
    chk("    ten gold rubles (十个金卢布)", ten, told("等于十个金卢布", "等于", "个金卢布"))
    chk("    two years (此后两年)", F["su_two"][0], told("此后两年", "此后", "年"))
    r, y23, old, y22 = F["su_rate"]
    said("1924 年 3 月，币制改革的法令通过，旧卢布按 5 万个 1923 年版换一个新卢布收回", F["su_reform"][0],
         mon("su_reform", "March"), r, y23)
    said("5 万个 1923 年版的卢布，等于 1922 年以前发行的 500 亿卢布", r, y23, y22, old)
    said("德国的恶性通胀在 1923 年 11 月止住", 1923, 11)                         # ch26_weimar (EVENTS)
    # 1928
    g10, y28, y13, p14, _, p3 = F["mh_1928"]
    said("到 1928 年，经济大体恢复了", y28)
    said("照 Markevich 与 Harrison（2011）的估计，1928 年的实际总产出比 1913 年多将近 10\\%", Y["mh_1928"], y28, y13, g10)
    said("人口多了约 14\\%，人均国民收入仍比战前低约 3\\%", p14, p3)
    said("1928 年苏联的人均 GDP 是 1913 年的 96.9\\%", 1928, 1913, ratio(1928))
    a, g, b, q = F["mh_trend"]
    said("人均 GDP 若沿着 1913 年以前每年 1.74\\% 的趋势增长，1920 年代末的实际水平还比这条趋势低约四分之一", a, g, b)
    chk("    about one quarter (约四分之一)", q, told("这条趋势低约四分之一", "低约"))
    a, b = F["h80_scissors"]
    said("1922—1923 年有过一次“剪刀差”危机", a, a // 100 * 100 + b)
    said("到 1920 年代后期，工业品长期供不应求", F["h80_goods"][0])
    assert "By the latter 1920s" in Q["h80_goods"]
    said("1926/27 年度，国家又压低了粮食的收购价格", *F["h80_lowered"])
    said("这里的年度是苏联当时的经济年度，从当年 10 月到次年 9 月", mon("mh_econyear", "October"),
         mon("mh_econyear", "September"))
    assert "the economic year (October to September)" in Q["mh_econyear"]
    said("照 Harrison（1980）的概括，后来的研究认为，1928 年与 1929 年的粮食收购危机至少有一部分是计划者自己引起的", Y["h80_crises"],
         *F["h80_crises"])
    assert "provoked by the planners themselves" in Q["h80_crises"] and "three main revisions" in column("note")["h80_crises"]
    said("照 Harrison（1980）的转述", Y["h80_redistribute"])
    said("1927 年，斯大林把托洛茨基", F["cg_expelled"][0])
    said("1928 年 1 月，斯大林等人恢复了", F["we_ural"][0], mon("we_ural", "January"))
    y28, y29 = F["h17_urals"]
    assert y28 == F["we_ural"][0] and "outside the law in the Urals and Siberia" in Q["h17_urals"]
    said("照 Harrison（2017）的说法，这个办法先在乌拉尔与西伯利亚法外施行，1929 年才以法律推行到全国", Y["h17_urals"], y29)
    d6, y28 = F["we_ration"]
    said("1928 年 12 月 6 日，联共（布）中央政治局批准了", y28, mon("we_ration", "December"), d6)
    said("斯大林在 1928 年用“大转变”结束了新经济政策", F["cg_greatturn"][0])


def plan(F, Y, Q):
    said("1929 年 4 月在党的代表会议上获得批准", F["h17_april"][0], mon("h17_april", "April"))
    a, b, c, d = F["gp29_period"]
    said("计划的期限从 1928/29 年度到 1932/33 年度", a, b, c, d)
    assert F["mh_april"][0] == F["h17_april"][0] and "April 1929" in Q["mh_april"]
    said("照 Markevich 与 Harrison（2011）的说法，批准的是“最优”方案", Y["mh_april"])
    assert '"The Five-Year Plan in Four Years."' in Q["st_slogan"]
    chk("    in four years (用四年完成)", 4, told("党决定用四年完成它", "用", "年"))
    assert "NEW YORK" in Q["gp29_title"] and Y["gp29_title"] == 1929
    i0, i1 = F["gp29_invest"]
    said("基本方案（英译本在这里叫最低方案）的五年投资是 574 亿卢布，通过的方案是 646 亿卢布", i0 * B9, i1 * B9)
    assert Q["gp29_invest"].startswith("In the minimum plan") and "for the minimum plan" in Q["gp29_growth"]
    g0, g1, a0, a1 = F["gp29_growth"]
    said("工业生产的增长，基本方案是 108\\%，最高方案是 136\\%", g0, g1)
    said("农业生产的增长，两个方案分别是 44\\% 与 55\\%", a0, a1)
    chk("    consumption per head up two thirds (提高三分之二)", F["h17_envisaged"][0], told("人均消费提高三分之二", "提高"))
    assert "doubling national income and trebling the output of investment goods" in Q["h17_envisaged"]
    say("计划要让国民收入翻一番，投资品的产量增加到三倍")
    said("照 Harrison（2017）的概括，计划要让国民收入翻一番", Y["h17_envisaged"])
    y, y2, kwh = F["gp29_power"]
    said("1927/28 年度的发电量是 51 亿千瓦时，计划到期末每年发电 220 亿千瓦时", y, y2, kwh * B9, F["gp29_targets"][0] * B9)
    assert "kilowatt-hours" in Q["gp29_power"] and "22 billion kilowatt-hours a year" in Q["gp29_targets"]
    said("煤要产 7,500 万吨，生铁要产 1,000 万吨", F["gp29_targets"][1] * M6, F["gp29_pig"][1] * M6)
    t10, _, _, three, y0, y1 = F["gp29_metal"]
    assert t10 == F["gp29_pig"][1]
    said("生铁的指标将近 1927/28 年度产量的三倍", y0, y1)
    chk("    nearly three times (将近三倍)", three, told("产量的三倍", "产量的", "倍"))
    o0, _, _, o1, _, _ = F["gp29_oil"]
    said("石油要从 1,160 万吨增加到 2,170 万吨", o0 * M6, o1 * M6)
    said("保证切尔文的购买力提高 20\\%", F["gp29_chervonets"][0])
    said("它要让小手工业增加 90 万工人", F["gp29_unemp"][0])
    said("照 Gregory 与 Harrison（2005）的说法，1929 年，斯大林表明", Y["gr_1929"], F["gr_1929"][0])
    assert F["gr_courage"] == F["gr_1929"]                                     # 同一年
    assert Q["gr_courage"].startswith("The purge of Gosplan that followed") and "admitting in the corridors" in \
        Q["gr_courage"]                                                       # the official speaks of other specialists
    say("随后国家计委遭到清洗。同一年，一位计划官员说，有些专家已经在走廊里承认")
    said("1931 年，斯大林号召党痛打", F["h17_thrash"][0])
    said("照 Harrison（2017）的判断", Y["h17_blueprint"])
    assert "At the end of November 1932" in Q["st_gamble"] and "at the end of November 1932" in Q["st_telegraph"]
    said("1932 年 11 月底，《纽约时报》说", F["st_gamble"][0], mon("st_gamble", "November"))
    # the report of 1933
    said("1933 年，国家计委在莫斯科出版了计划完成情况的总结", F["gp33_title"][0])
    assert "MOSCOW" in Q["gp33_title"]
    a, y28, b, y32, p0, p1, pct, _ = F["gp33_gross"]
    said("按 1926/27 年度的价格计算，工业总产值从 1928 年的 157 亿卢布增加到 1932 年的 343 亿卢布", p0, p1, y28, a * B9, y32,
         b * B9)
    said("1932 年是 1928 年的 218.5\\%", y32, y28, pct)
    chk("    218.5 per cent = 34.3 / 15.7", 100 * b / a, pct, tol=0.15)
    _, _, plan_, _, out, _, _, four, quarter, p937 = F["gp33_937"]
    said("计划给 1932/33 年度定的是 366 亿卢布，所以计划在四年零一个季度里完成了 93.7\\%", 1932, 33, plan_ * B9, p937)
    chk("    93.7 per cent = 34.3 / 36.6", 100 * out / plan_, p937, tol=0.05)
    chk("    four and a quarter years (四年零一个季度)", four + quarter, told("在四年零一个季度里", "在", "年零") + 0.25)
    say("总结把工业分成两类，甲类生产生产资料，乙类生产消费品")
    assert "means of production" in Q["gp33_defa"] and "articles of consumption" in Q["gp33_defb"]
    said("甲类工业的计划完成了 103.4\\%，重工业人民委员部管辖的工业完成了 109.6\\%", *F["gp33_groupa"])
    y28, x26, _ = F["gp33_means"]
    said("生产资料的生产，1932 年是 1928 年的 2.6 倍", 1932, y28, x26)
    said("乙类工业只完成了计划的 84.9\\%", F["gp33_groupb"][0])
    assert "light industries did not fulfil the Plan" in Q["gp33_light"]
    # fig:soviet_plan
    said("各项在 1927/28 年度与 1932 年的产量，以 1932/33 年度的计划指标为 100\\%", 1927, 28, 1932, 1932, 33, 100)
    said("工业总产值按 1926/27 年度的价格计算，1927/28 年度一栏用 1928 年的数", 1926, 27, 1927, 28, 1928)
    said("生铁与钢的 1932 年数和煤与石油的数取自总结里的表，1927/28 年度的生铁与钢取自正文", 1932, 1927, 28)
    said("数据：国家计委（1929，1933）", Y["gp29_title"], Y["gp33_title"])
    # physical output
    y0, y1, pig, pre, y13 = F["gp33_pig28"]
    said("1927/28 年度，生铁的产量是 328.3 万吨，1913 年是 420 万吨", y0, y1, pig, y13, pre * M6)
    _, _, tp, ts, _ = F["gp33_task"]
    said("在 1932/33 年度达到 1,000 万吨；钢要达到 1,030 万吨", 1932, 33, tp * M6, ts * M6)
    assert "to treble the output of pig iron" in Q["gp33_task"]
    chk("    treble (增加到三倍)", 3, told("计划要它增加到三倍", "增加到", "倍"))
    _, p32, _, s32 = F["gp33i_world"]
    said("1932 年，生铁只产了 620 万吨，钢产了 590 万吨", 1932, p32 * M6, s32 * M6)
    _, _, c_plan, c32 = F["gp33i_coal"]
    said("煤产了 6,437 万吨，计划是 7,500 万吨", c32 * M6, c_plan * M6)
    assert c_plan == F["gp29_targets"][1]
    y, o32, oplan = F["gp33_oil"]
    said("石油与天然气超额完成，1932 年产 2,220 万吨，计划是 2,170 万吨", y, o32 * M6, oplan * M6)
    # the pitfall
    said("[工业总产值是 1928 年的 218.5\\%，工业生产就翻了一番多]", 1928, pct)
    said("这个数按的是“1926/27 年度不变价格”", *F["h93_unchanged"])
    said("照 Harrison（1993）的说明，用早年的价格加权，即使没有隐蔽的通胀", Y["h93_unchanged"])
    said("何况所谓不变的价格，在 1930 年代随着机械工业新产品的加入逐年上涨", 1930)
    for words in ("than indices using weighting schemes based on later years, even without any element of hidden "
                  "inflation", "through the 1930s", "the nomenklatura of the engineering industry"):
        assert words in transcription("h93_unchanged"), words
    said("1932 年的生铁只有计划的 62\\%", 1932, 100 * p32 / tp)
    # the second plan
    said("第二个五年计划从 1933 年开始", F["st_second"][0])
    g22, a, b = F["st_22"]
    said("工业产值平均每年增长 22\\%", g22)
    said("至少增长 13\\%—14\\% 的速度", a, b)


def ex_balance() -> None:
    a12, a21, (f1, f2), s2 = BAL["a12"], BAL["a21"], BAL["f"], BAL["steel2"]
    A = np.array([[0, a12], [a21, 0]])
    f = np.array([f1, f2])
    x = np.linalg.solve(np.eye(2) - A, f)
    L = np.linalg.inv(np.eye(2) - A)
    ds = s2 - f1
    dx = L @ np.array([ds, 0])
    said("每产 1 吨钢要用 2 吨煤，每产 1 吨煤要用 0.1 吨钢", 1, a21, 1, a12)
    said("（1）计划要钢 8、煤 20 供最终使用", 1, f1, f2)
    said("（2）钢的最终使用提高到 10，两种物资各要多产多少？（3）计划人员只算了一轮：钢多产 2，煤多产 4", 2, s2, 3, ds, a21 * ds)
    said("（1）$A=\\begin{pmatrix}0&0.1\\\\2&0\\end{pmatrix}$，$f=(8,\\,20)'$", 1, 0, a12, a21, 0, f1, f2)
    said("$x=(12.5,\\,45)'$。检验：钢$12.5=0.1\\times45+8$，煤$45=2\\times12.5+20$", x[0], x[1], x[0], a12, x[1], f1, x[1],
         a21, x[0], f2)
    chk("    the balance of steel", a12 * x[1] + f1, x[0])
    chk("    the balance of coal", a21 * x[0] + f2, x[1])
    said("（2）$(I-A)^{-1}=\\begin{pmatrix}1.25&0.125\\\\2.5&1.25\\end{pmatrix}$", 2, L[0, 0], L[0, 1], L[1, 0], L[1, 1])
    said("钢的最终使用多 2，钢要多产$1.25\\times2=2.5$，煤要多产$2.5\\times2=5$", ds, L[0, 0], ds, dx[0], L[1, 0], ds, dx[1])
    r1c, r1s, r2c = a21 * ds, a12 * a21 * ds, a21 * a12 * a21 * ds
    said("多 2 吨钢要 4 吨煤，4 吨煤要 0.4 吨钢，0.4 吨钢又要 0.8 吨煤", ds, r1c, r1c, r1s, r1s, r2c)
    said("钢合计$2+0.4+0.08+\\cdots=2.5$，煤合计$4+0.8+0.16+\\cdots=5$", ds, r1s, r1s * a12 * a21, dx[0], r1c, r2c,
         r2c * a12 * a21, dx[1])
    chk("    the geometric series of steel", ds / (1 - a12 * a21), dx[0])
    xs, xc = x[0] + ds, x[1] + a21 * ds
    use = a12 * xc + s2
    said("（3）钢产$12.5+2=14.5$，煤产$45+4=49$。钢的用途是$0.1\\times49+10=14.9$，比产量多 0.4", 3, x[0], ds, xs, x[1],
         a21 * ds, xc, a12, xc, s2, use, use - xs)
    said("这 0.4 吨钢又要 0.8 吨煤", use - xs, a21 * (use - xs))
    chk("    the gap of one round = a12 a21 ds", use - xs, a12 * a21 * ds)


def balances(F, Y, Q):
    say("x=Ax+f", "x=f+Af+A^{2}f+\\cdots")
    said("照 Gregory 与 Harrison（2005）的说法，1930 年代初，国家计委的方法还很原始", Y["gr_primitive"], F["gr_primitive"][0])
    assert "in the early 1930s" in Q["gr_primitive"]
    say("国家计委早期的工作，大多是把各工业部门之间的供应一项一项地对上")
    assert "detailed matching problems of inter-industry supply" in Q["h17_matching"]
    said("照 Harrison（2017）的说法，著名的“物资平衡”方法就是这样来的", Y["h17_balances"])
    say("只要投入一轮比一轮少，即$A^{k}$随$k$增大趋于零")
    said("只包括 30 种原材料、8 种能源和 4 类机器", *F["gr_balances"])
    said("照 Harrison（1980）转述的 Hunter 的说法", Y["h80_hunter"])
    ex_balance()
    # turnover tax
    tr0, tt0, tr1, tt1 = F["sc_budget"]
    tr = transcription("sc_budget")
    assert "Total revenue" in tr and "Turnover tax (chiefly industry turnover)" in tr
    assert "the columns are 1928-29" in column("note")["sc_budget"] and ", 1934" in column("note")["sc_budget"]
    said("按 1936 年出版的统计汇编", Y["sc_budget"])
    said("1928/29 年度，预算收入是 66.5 亿卢布，周转税是 31.5 亿", 1928, 29, tr0 * M6, tt0 * M6)
    said("周转税占了 47.3\\%", 100 * tt0 / tr0)
    said("1934 年，预算收入是 507.6 亿卢布，周转税是 302.4 亿，占 59.6\\%", 1934, tr1 * M6, tt1 * M6, 100 * tt1 / tr1)
    # food prices
    two, y29, y30, x45, y31, x7, y32, x28 = F["cg_black"]
    said("1929 年已是国家收购价格的两倍多，1930 年是 4.5 倍，1931 年是 7 倍", y29, y30, x45, y31, x7)
    chk("    twice (两倍多)", two, told("国家收购价格的两倍多", "价格的", "倍多"))
    said("1932 年是 28 倍", y32, x28)
    assert F["cg_markets"] == [y32]
    said("按 Gregory 与 Harrison 对 Bergson（1964）等早期研究的概括", F["gr_scarcity"][0])
    # the comparison box
    said("\\cmprow{1930 年代初的苏联}{集中平衡只有 30 种原材料、8 种能源与 4 类机器", 1930, *F["gr_balances"])
    said("1932 年黑市的粮价是收购价的 28 倍", y32, x28)


def famine(F, Y, Q):
    G = grain()
    y29, y32, p60, p70 = F["mnq_collect"]
    said("强制集体化从 1929 年底开始", y29)
    assert "began in late 1929" in Q["mnq_collect"]
    said("照 Markevich、Naumenko 与 Qian（2021）的说法", Y["mnq_bundle"])
    half, y30, p90, y36 = F["h17_half90"]
    said("照 Harrison（2017）的说法，1930 年初集体化已经覆盖了一半的农户，之后一度后退，到 1936 年覆盖了 90\\%", Y["h17_half90"], y30,
         y36, p90)
    chk("    half (一半)", half, told("覆盖了一半", "覆盖了", ""))
    said("到 1932 年夏，住在集体农庄里的农户在全苏联超过 60\\%，在乌克兰将近 70\\%", y32, p60, p70)
    said("斯大林在 1933 年的报告里说的也是 60\\% 以上", Y["st_collective"], F["st_collective"][0])
    y, n, m = F["cg_riots"]
    said("仅 1930 年 3 月就发生了 6,500 多起骚乱，参加的农民有 140 万", y, mon("cg_riots", "March"), n, m * M6)
    y, two = F["h17_feb1930"]
    said("按 1930 年 2 月的一项法令，最终有 200 万人被迁走或关押", y, mon("h17_feb1930", "February"), two * M6)
    said("1929—1932 年，马减少了 42\\%，牛减少了 40\\%", *F["mnq_livestock"])
    # fig:soviet_grain
    dw = G[G.dw_min_mt.notna()].index
    said("苏联的粮食产量与国家征购，1927—1933 年与 1937、1939 年", G.index[0], G.index[6], G.index[7], G.index[8])
    assert list(G.index[:7]) == list(range(1927, 1934))
    said("（阴影，1930—1933 年）", dw[0], dw[-1])
    said("1930—1932 年，收成连年减少，征购仍比 1928 年多得多", 1930, 1932, 1928)
    R = G.loc[1930:1932, "revised_mt"]
    assert R.is_monotonic_decreasing and R.is_unique
    assert G.loc[1930:1932, "procurement_mt"].min() > 1.7 * G.loc[1928, "procurement_mt"]
    say("收成在减少，征购却没有跟着减少")
    said("1931 年的收成比前几年低，“饥饿的消息传到了莫斯科，但政府没有降低征购”", F["mnq_1931"][0])
    assert "the government did not lower procurement" in Q["mnq_1931"]
    said("1932 年收成不及预期，斯大林一面削减了最初的指标，一面强调要尽量多征购", F["mnq_curtailed"][0])
    assert "curtailed the initial targets and emphasized the need to maximize procurement" in Q["mnq_curtailed"]
    said("数据：Markevich、Naumenko 与 Qian（2021）附表 A.2", Y["mnq_table"], 2)
    assert "Appendix Table A.2" in column("juan")["mnq_table"]
    r28, p28 = G.loc[1928, "revised_mt"], G.loc[1928, "procurement_mt"]
    r32, p32 = G.loc[1932, "revised_mt"], G.loc[1932, "procurement_mt"]
    said("1928 年的粮食产量是 7,340 万吨，国家征购了 1,080 万吨，约占 14.7\\%", 1928, r28 * M6, p28 * M6, 100 * p28 / r28)
    said("1932 年的产量降到 5,710 万吨，征购还有 1,900 万吨", 1932, r32 * M6, p32 * M6)
    third = told("征购还有 1,900 万吨，约占三分之一", "约占")
    assert abs(p32 / r32 - third) < 0.01
    said("官方公布的 1932 年产量是 6,990 万吨，Davies 与 Wheatcroft 的修正在 5,500 万到 6,000 万吨之间", 1932,
         G.loc[1932, "official_mt"] * M6, G.loc[1932, "dw_min_mt"] * M6, G.loc[1932, "dw_max_mt"] * M6)
    d11, y, fifty = F["mnq_lose"]
    said("1932 年 8 月 11 日，斯大林在给副手的信里提到，乌克兰约 50 个区的党委", y, mon("mnq_lose", "August"), d11, fifty)
    said("斯大林在报告里引了《纽约时报》1932 年 11 月的话", F["st_nyt"][0], mon("st_nyt", "November"))
    said("1933 年 1 月，莫斯科下令封闭乌克兰与北高加索的边界", F["mnq_border"][0], mon("mnq_border", "January"))
    n65, d22, y = F["ru_directive"]
    said("照 Rudnytskyi 等人（2015）的说法，那是 1 月 22 日中央的第 65 号指令", Y["ru_directive"], mon("ru_directive", "January"),
         d22, n65)
    a, b = F["we_fled"]
    said("有 1,200 万到 1,300 万农民逃进了城市", a * M6, b * M6)
    said("政府在 1933 年上半年实行了国内护照与居住登记制度", F["we_passport"][0])
    assert "in the first half of 1933" in Q["we_passport"]
    a, b, y0, y1 = F["we_meat"]
    said("1927—1933 年，肉、奶、黄油、蛋与油脂的消费下降了 75\\%—90\\%", y0, y1, a, b)
    assert "industrial workers' budgets" in Q["we_meat"]
    # deaths
    y, six, _ = F["h17_famine"]
    said("照 Harrison（2017）的说法，1932 年开始的饥荒死了约 600 万人", Y["h17_famine"], y, six * M6)
    w = F["we_total"]
    assert "the early 1930s" in Q["we_early"]
    said("照 Werth 对已有研究的概括，1930 年代初的几场饥荒，死者有 650 万到 700 万", 1930, w[0] * M6, w[1] * M6)
    assert "historians have been able to reconstruct" in Q["we_reconstruct"]
    said("其中乌克兰与库班约 420 万，哈萨克斯坦 130 万到 150 万", w[2] * M6, w[3] * M6, w[4] * M6)
    said("苏联其他地方还有 100 多万", w[5] * M6)
    d = F["dv_10m"]
    said("照 Davies（2004）的估计，1930—1933 年的全部超额死亡，算上更早的哈萨克饥荒，大概是 550 万到 600 万", Y["dv_10m"], d[6],
         1900 + d[7], d[8] * M6, d[9] * M6)
    lo, hi = F["mnq_range"]
    said("从 500 万到 1,080 万不等", lo * M6, hi * M6)
    t, ex, births, rural, urban, y33 = F["ru_total"]
    said("照 Rudnytskyi 等人（2015）的估计，乌克兰的超额死亡是 390 万，加上少出生的 60 万，总损失是 450 万", Y["ru_total"], ex * M6,
         births * M6, t * M6)
    chk("    3.9 + 0.6 = 4.5", ex + births, t)
    said("分别相当于 1933 年人口的 16.5\\% 与 4.0\\%", y33, rural, urban)
    said("Meslé 与 Vallin 重建的超额死亡是 260 万", F["ru_mesle"][0] * M6)
    said("“1933 年死亡人数的巨大差别", F["ru_related"][0])
    y, ru, mv = F["ru_migration"]
    assert "−52,000" in Q["ru_migration"] and "−1.4 million" in Q["ru_migration"]
    said("那一年净迁出 5.2 万人；按 Meslé 与 Vallin 的估计，是 140 万人", ru, mv * M6)
    ten, _, a, b = F["ru_anecdotal"]
    said("高达 1,000 万的直接损失", ten * M6)
    said("在 260 万到 500 万之间", a * M6, b * M6)
    said("多达 70 万人", F["we_volga"][0])
    said("全国的死亡率到 1934 年才回到趋势", F["mnq_1934"][0])
    said("照 Harrison（2017）的说法，是 1932 年的坏天气触发了饥荒", Y["h17_famine"], F["h17_famine"][0])
    said("照 Werth 的说法，1932 年秋天以后，斯大林的领导层为了明确的政治目的，有意加剧了乌克兰与库班的普遍短缺与局部饥荒",
         F["we_trajectory"][0])
    assert "after the autumn of 1932" in Q["we_trajectory"] and "purposefully aggravated" in Q["we_trajectory"]
    said("照 Markevich、Naumenko 与 Qian 的结论，1932 年", F["mnq_enough"][0])
    said("最多能解释乌克兰饥荒死亡的 92\\%，在乌克兰、俄罗斯与白俄罗斯三地合计是 77\\%", *F["mnq_bias"])
    chk("    about half (约有一半)", F["mnq_half"][0], told("这个作用约有一半", "约有"))
    n, y0, y1 = F["we_arrests"]
    said("在 1932—1933 年逮捕了约 20 万人", y0, 1900 + y1, n)
    said("1930 年成立", F["h17_gulag1930"][0])
    a, y0, b, y1 = F["h17_gulag"]
    said("人数从 1930 年的不到 20 万，增加到 1941 年的 190 万", y0, a, y1, b * M6)
    assert "less than 200,000" in Q["h17_gulag"]


def casebox(F, Y, Q):
    a, b = [int(x) for x in re.search(r"Kazakh Famine of (\d{4})-(\d{2})", meta()["sources"]["cameron2016"]["version"])
            .groups()]
    said("\\begin{case}{哈萨克斯坦 · 1930—1933 · 游牧的终结}", a, a // 100 * 100 + b)
    said("占人口的 57.1\\%", F["ca_571"][0])
    said("饥荒在 1930 年冬天开始，比苏联其他地方早一年", F["ca_1930"][0])
    assert "a year earlier than in other parts of the Soviet Union" in Q["ca_1930"]
    chk("    nine tenths (约九成)", F["ca_ninety"][0] / 100, told("共和国约九成", "约"))
    y, p, y0 = F["ca_908"]
    said("1932 年 10 月的一份秘密警察报告算出，牲畜的数目比 1929 年减少了 90.8\\%", y, mon("ca_908", "October"), y0, p)
    y0, y1, n = F["ca_fled"]
    said("1931—1933 年，110 多万人离开了共和国", y0, 1900 + y1, n * M6)
    d, y, three = F["ca_concession"]
    said("1932 年 9 月 17 日，共和国已经熬过了将近三年的苦难", y, mon("ca_concession", "September"), d)
    chk("    nearly three years (将近三年)", three, told("将近三年的苦难", "将近", "年"))
    said("饥荒一直持续到 1934 年", F["ca_1934"][0])
    n, q = F["ca_15"]
    said("照 Cameron（2016）的估计，150 多万人死去", Y["ca_15"], n * M6)
    chk("    a quarter (四分之一)", q, told("当时人口的四分之一", "人口的"))
    _, k, third = F["ca_kazakhs"]
    said("其中约 130 万是哈萨克人", k * M6)
    chk("    more than a third (三分之一以上)", third, told("全体哈萨克人有三分之一以上", "有", "以上"))
    w = F["we_total"]
    said("Werth 是 130 万到 150 万，Markevich、Naumenko 与 Qian 是 100 万到 150 万", w[3] * M6, w[4] * M6,
         F["mnq_kazakh"][0] * M6, F["mnq_kazakh"][1] * M6)


def calculation(F, Y, Q):
    said("米塞斯 1920 年的文章发表在德国的《社会科学与社会政策文库》上，1935 年译成英文", F["mi_note"][0], Y["mi_note"])
    assert "Die Wirtschaftsrechnung im sozialistischen Gemeinwesen" in Q["mi_note"]
    said("照哈耶克 1945 年的回忆", Y["hy_derision"])
    chk("    twenty-five years (二十五年前)", F["hy_derision"][0], told("米塞斯二十五年前", "米塞斯", "年前"))
    chk("    1920 + 25 = 1945", F["mi_note"][0] + F["hy_derision"][0], Y["hy_derision"])
    a, b = F["la_reprint"]
    said("发表在 1936 年 10 月与 1937 年 2 月的《经济研究评论》上", a, mon("la_reprint", "October"), b,
         mon("la_reprint", "February"))
    said("是 1945 年 9 月发表在《美国经济评论》上的《知识在社会中的运用》", Y["hy_notice"], mon("hy_notice", "September"))
    said("\\begin{compare}{兰格与哈耶克}{兰格（1936—1937）}{哈耶克（1945）}", a, b, Y["hy_notice"])
    ex_lange()


def ex_lange() -> None:
    a, b, c, d, p0, lam, lam2 = (LANGE[k] for k in ("a", "b", "c", "d", "p0", "lam", "lam2"))
    p_star = (a - c) / (b + d)
    q_star = a - b * p_star
    D = lambda p: a - b * p                                                     # noqa: E731
    S = lambda p: c + d * p                                                     # noqa: E731
    step = lambda p, l_: p + l_ * (D(p) - S(p))                                 # noqa: E731
    p1, p2 = step(p0, lam), step(step(p0, lam), lam)
    k = 1 - lam * (b + d)
    said("一种商品的需求是$D=100-2p$，供给是$S=10+p$", a, b, c)
    said("（1）均衡价格是多少？（2）计划局从$p_0=10$开始", 1, 2, p0)
    said("调价，$\\lambda=0.2$", lam)
    said("（3）$\\lambda$大到多少，试错就收敛不了？$\\lambda=0.8$时会怎样", 3, lam2)
    said("（1）$100-2p=10+p$，$p^{*}=30$，数量是 40", 1, a, b, c, p_star, q_star)
    chk("    S(p*) = D(p*)", S(p_star), q_star)
    said("（2）$p_1=10+0.2\\times(80-20)=22$，$p_2=22+0.2\\times(56-32)=26.8$", 2, p0, lam, D(p0), S(p0), p1, p1, lam, D(p1),
         S(p1), p2)
    said("$p_{t+1}-p^{*}=\\bigl[1-\\lambda(2+1)\\bigr](p_t-p^{*})$，差距每轮乘以$1-0.6=0.4$：20、8、3.2", 1, b, d, 1,
         lam * (b + d), k, p_star - p0, k * (p_star - p0), k * k * (p_star - p0))
    chk("    the gap after one round", p_star - p1, k * (p_star - p0))
    chk("    the gap after two rounds", p_star - p2, k * k * (p_star - p0), tol=1e-9)
    said("（3）收敛要求$\\lvert1-3\\lambda\\rvert<1$，也就是$0<\\lambda<2/3$", 3, 1, b + d, 1, 0, 2, b + d)
    k2 = 1 - lam2 * (b + d)
    pp = step(p0, lam2)
    said("$\\lambda=0.8$时，每轮乘以$1-2.4=-1.4$", lam2, 1, lam2 * (b + d), -k2)
    said("$p_1=10+0.8\\times60=58$，已经比均衡高了 28", p0, lam2, D(p0) - S(p0), pp, pp - p_star)
    assert abs(k2) > 1 and abs(k) < 1
    chk("    convergence below lambda = 2 / (b + d)", 2 / (b + d), 2 / 3)


def growth(F, Y, Q):
    T = table1()
    ts, cia, kh = F["h93_t1_2840"]
    said("按中央统计局的数，1928—1940 年苏联的国民收入每年增长 13.9\\%", 1928, 1940, ts)
    said("国民生产总值每年增长 6.1\\%", cia)
    said("哈宁（Girsh Khanin，1937 年生）", F["h93_khanin"][1])
    assert "Born in Latvia in 1937" in transcription("h93_khanin")
    said("只有每年 3.2\\%", kh)
    notes = {"a": "1928–41", "b": "1941–50"}
    for x, y_ in notes.items():
        assert f"note {x}: «{y_}»" in " ".join(column("note")[r] for r in ("h93_t1_2840", "h93_t1_4050")), x
    said("1928—1940 年 & 13.9 & 6.1 & 3.2（1928—1941 年）", 1928, 1940, *T["1928-1940"], 1928, 1941)
    said("1940—1950 年 & 4.8 & 2.0 & 1.6（1941—1950 年）", 1940, 1950, *T["1940-1950"], 1941, 1950)
    said("1928—1950 年 & 10.1 & 4.2 & 2.5", 1928, 1950, *T["1928-1950"])
    said("1950—1987 年 & 6.6 & 3.8 & 3.8", 1950, 1987, *T["1950-1987"])
    said("1928—1987 年 & 7.9 & 3.9 & 3.3", 1928, 1987, *T["1928-1987"])
    page = int(re.search(r"p\. (\d+), Table (\d)", column("juan")["h93_t1_2840"]).group(1))
    said("Harrison（1993）表 1（第 146 页）", Y["h93_t1_2840"], 1, page)
    said("1987 年，哈宁与改革派记者 Vasilii Selyunin（生卒年未详）在《新世界》杂志上合写发表文章《狡猾的数字》", F["h93_khanin"][0])
    assert "written jointly with the reforming journalist Vasilii Selyunin, in Novyi mir" in transcription("h93_khanin")
    assert "nr91022528" in column("note")["h93_khanin"]
    y85, off, y28, kh66 = F["h93_sensation"]
    said("照 Harrison（1993）的转述，哈宁的结论是，到 1985 年苏联的国民收入只是 1928 年的 6.6 倍，官方的统计却是 84.4 倍",
         Y["h93_sensation"], y85, y28, kh66, off)
    said("只增加到 1.5 倍", F["h93_doubled"][1])
    assert F["h93_doubled"][0] == 2                                             # 翻了一番
    first = F["h93_first"]
    said("第一个五年计划期间产出下降了 20\\%，战前的增长全部集中在第二个五年计划的 1933—1937 年", first[2], first[5],
         1900 + first[6])
    say("哈宁对战前几个五年计划的估计，比 Bergson、Moorsteen 与 Powell 的低得多，他的工业数字却与 Moorsteen 和 Powell 的相近",
        "照 Harrison 的推测，原因在哈宁合并各部门指数时用的权数，农业的权数被放大了")
    for words in ("so far below those of Bergson, Moorsteen and Powell", "close to Moorsteen & Powell's",
                  "agriculture, in particular, must attract an enlarged weight"):
        assert words in transcription("h93_doubt"), words
    said("照 Harrison（1993）的说明，长得最快的产品", Y["h93_gersch"])
    say("\\chref{ch:prices}讲过，用哪一年的价格给产品加权，增长率可以差很多")
    said("设两种产品在第 0 年与第 1 年的价格是", 0, 1)
    ex_index()
    n = F["h93_nutter"]
    said("按 Nutter 的估计，1928—1940 年苏联的工业生产按 1928 年的价格每年增长 19.3\\%，按 1955 年的价格只有 8.7\\%", n[0],
         1900 + n[1], n[3], n[2], n[5], n[4])
    said("按 Bergson 的估计，1928—1937 年的国民生产总值按 1928 年的价格每年增长 11.9\\%，按 1937 年的价格只有 5.5\\%", n[6],
         1900 + n[9], n[8], n[7], n[11], n[10])
    said("官方的指数用所谓“1926/27 年度不变价格”", *F["h93_unchanged"])
    # fig:soviet_gdp and the text
    U, M = ussr(), maddison()
    assert U.loc[1913:1940].idxmin() == 1921
    mm = maddison_meta()
    said("苏联的人均 GDP 在 1921 年跌到谷底，1930 年代中期跃升。人均 GDP，2011 年国际元", 1921, 1930, 2011)
    said("对数坐标，1913—1940 年", M.columns[0], M.columns[-1])
    sun = mm["sources_by_country"]["SUN"]
    assert any("1928-40: R. Moorsteen and R.P. Powell" in s for s in sun)
    said("1928 年以后的苏联数字是 Moorsteen 与 Powell 的重估", 1928)
    said("数据：Maddison 项目数据库 2023 年版（Bolt 与 van Zanden 2024）",
         int(re.search(r"version (\d{4})", mm["source"]).group(1)), citation_year(mm["citation"]))
    said("苏联的人均 GDP 在 1921 年跌到谷底，只有 1913 年的 37.2\\%", 1921, 1913, ratio(1921))
    said("1928 年回到 1913 年的 96.9\\%，1940 年是 1913 年的 151.6\\%", 1928, 1913, ratio(1928), 1940, 1913, ratio(1940))
    y40, p50, y13 = F["h17_1940"]
    said("这与 Harrison（2017）说的 1940 年人均产出比 1913 年高 50\\% 相合", Y["h17_1940"], y40, y13, p50)
    assert abs(ratio(1940) - 100 - p50) < 2
    said("1928—1940 年，人均 GDP 平均每年增长 3.8\\%", 1928, 1940, cagr(U[1928], U[1940], 12))
    mp = re.search(r"1928-40: R\. Moorsteen and R\.P\. Powell, .*?(\d{4}), p\. \d+", " ".join(sun)).group(1)
    mh = re.search(r"1913-1928: Markevich, A\. and M\. Harrison \((\d{4})\)", " ".join(sun)).group(1)
    said("数据库 1928 年以后的苏联数字来自 Moorsteen 与 Powell（1966）的重估，1913—1928 年来自 Markevich 与 Harrison（2011）",
         1928, int(mp), 1913, 1928, int(mh))
    share = (U[1937] - U[1933]) / (U[1940] - U[1928])
    said("1928—1940 年人均 GDP 的增加，85.7\\% 出现在 1934—1937 年这四年里", 1928, 1940, 100 * share, 1934, 1937)
    chk("    four years (这四年)", 1937 - 1934 + 1, told("1934—1937 年这四年里", "年这", "年里"))
    _, y04, y39, p75 = F["mh_75"]
    tq, five, y33, y37 = F["mh_threequarters"]
    said("照 Markevich 与 Harrison 的计算，1904—1939 年收入增加了约 75\\%，其中四分之三是在 1933—1937 年这五年里取得的", y04,
         y39, p75, y33, y37)
    chk("    three quarters (四分之三)", tq, told("其中四分之三是在", "其中", "是在"))
    chk("    five years (这五年)", five, told("1933—1937 年这五年里", "年这", "年里"))
    ff, four, y34, y37 = F["h17_fourfifths"]
    said("照 Harrison（2017）的计算，国民收入的增加有五分之四来自 1934—1937 年的四年", Y["h17_fourfifths"], y34, y37)
    chk("    four fifths (五分之四)", ff, told("增加有五分之四来自", "增加有", "来自"))
    chk("    four years (四年)", four, told("1934—1937 年的四年", "年的", "年"))
    said("1930 年代中期收成恢复，食物不那么短缺了，斯大林在 1935 年说", 1930, F["h17_better"][0])
    assert "In the mid-1930s the harvest recovered" in Q["h17_better"]
    # the comparison box
    said("所谓 1926/27 年度不变价格，实际随新产品逐年上涨", *F["h93_unchanged"])
    said("例如 1928、1937 或 1955 年", n[0], n[11], n[5])
    said("\\cmprow{1928—1940 年每年}{国民收入 13.9\\%", 1928, 1940, ts)
    said("{国民生产总值 6.1\\%（Moorsteen 与 Powell）", cia)
    said("Bergson：1928—1937 年按 1928 年价格 11.9\\%，按 1937 年价格 5.5\\%", n[6], 1900 + n[9], n[8], n[7], n[11], n[10])
    assert n[7] / n[10] > 2 and n[2] / n[4] > 2                                 # 差一倍多


def ex_index() -> None:
    (m0, m1), (pm0, pm1), (g0, g1), (pg0, pg1) = IDX["m"], IDX["pm"], IDX["g"], IDX["pg"]
    v00, v01 = m0 * pm0 + g0 * pg0, m1 * pm0 + g1 * pg0                         # sum p0 q0, sum p0 q1
    v10, v11 = m0 * pm1 + g0 * pg1, m1 * pm1 + g1 * pg1
    L, P = v01 / v00, v11 / v10
    F_ = math.sqrt(L * P)
    said("第 0 年，机器 2 台，每台 10；粮食 80 吨，每吨 1。第 1 年，机器 10 台，每台 4；粮食仍是 80 吨，每吨 1.2", 0, m0, pm0, g0,
         pg0, 1, m1, pm1, g1, pg1)
    said("（1）按式~\\eqref{eq:soviet-index}，用第 0 年与第 1 年的价格，产量各增长多少？（2）两者的几何平均是多少？（3）", 1, 0,
         1, 2, 3)
    said("（1）按第 0 年的价格：$\\sum p_0q_0=2\\times10+80\\times1=100$，$\\sum p_0q_1=10\\times10+80\\times1=180$，增长 80\\%", 1,
         0, m0, pm0, g0, pg0, v00, m1, pm0, g1, pg0, v01, 100 * (L - 1))
    said("按第 1 年的价格：$\\sum p_1q_0=2\\times4+80\\times1.2=104$，$\\sum p_1q_1=10\\times4+80\\times1.2=136$，增长$136/104-1"
         "\\approx30.8\\%$", 1, m0, pm1, g0, pg1, v10, m1, pm1, g1, pg1, v11, v11, v10, 1, 100 * (P - 1))
    said("（2）$\\sqrt{1.8\\times1.308}\\approx1.534$，增长 53.4\\%", 2, L, P, F_, 100 * (F_ - 1))
    said("（3）机器从 2 台增加到 10 台，价格从 10 降到 4", 3, m0, m1, pm0, pm1)
    said("Nutter 与 Bergson 的数字方向相同：按 1928 年的价格算", 1928)
    assert L > P                                                               # Gerschenkron


def debate(F, Y, Q):
    said("照 Gregory 与 Harrison（2005）的说法，这场论战设想", Y["gr_technocratic"])
    say("苏联意外解体以后，西方与俄国的历史学家重新评价苏联的过去，评价变低了")
    assert "reassessed the Soviet past less favorably" in Q["dv_reassess"]
    said("Allen（2003）的结论却正面得多", allen_year())
    assert Q["dv_positive"] == "Allen's conclusions are much more positive."
    said("下面据 Davies（2004）的书评与 Markevich 与 Harrison（2011）的转述", Y["dv_fate"], Y["mh_allen"])
    M = maddison()
    said("1940 年苏联的人均 GDP 是 3,417 国际元，阿根廷是 6,633，印度是 1,093", 1940, M.loc["SUN", 1940], M.loc["ARG", 1940],
         M.loc["IND", 1940])
    assert "between India's and Argentine's" in Q["dv_fate"]
    assert M.loc["IND", 1940] < M.loc["SUN", 1940] < M.loc["ARG", 1940]
    say("实际的苏联也落在两者之间")
    assert "perversely accelerate industrialization by driving people off the land" in Q["dv_perverse"]
    assert "relatively uncontroversial" in Q["dv_perverse"]
    p30, y0, y1, _ = F["dv_cons"]
    said("1928—1937 年人均消费增加了多达 30\\%", y0, y1, p30)
    said("1927/28 年粮食危机以前", *F["dv_alternative"])
    assert "with some justice" in Q["mh_justice"]
    said("可是 Allen 对 1937 年农民收入的估计，在他们看来大概太高了", F["mh_toohigh"][0])
    assert F["mh_survivors"] == F["mh_toohigh"] and "millions of citizens" in Q["mh_survivors"]
    say("软预算约束是说，亏损的企业总能得到救助")
    assert "soft-budget constraint" in Q["dv_sbc"] and "soft budget constraint" in Q["mh_allen"]
    said("Allen 主张，1930 年代最好的发展道路", F["mh_allen"][0])
    said("农产品价格提高 10\\%，上市量才增加 7\\%", *F["dv_elastic"])
    said("1930 年代末的城市人口比 1928 年多一倍以上", *F["dv_double"])
    said("从 1925 年起投资动员加紧", F["mh_swallow"][0])
    w = F["cg_welfare"]
    said("照 Cheremukhin 等人（2013）的模型，1928—1940 年斯大林的政策造成的福利损失，相当于消费的 24\\%，1941 年以后有相当于消费 "
         "16\\% 的福利收益", Y["cg_welfare"], w[1], w[2], w[0], w[4], w[3])
    said("1928 年出生的一个代表性消费者，福利损失相当于消费的 1\\%", w[5], w[6])
    said("会有 20\\% 的福利收益", F["cg_nep20"][0])
    assert "reallocation from rural to urban sector did contribute to growth" in Q["cg_realloc"]
    say("分歧最后落在上面那个问题上：不靠强制，农民的市场能不能交出多一倍的农产品")
    assert "without the use of compulsion" in Q["dv_compulsion"]


def check_section(F, Y, Q):
    said("93.7\\% 这个数", F["st_937"][1])
    assert F["gp33_937"][-1] == F["st_937"][1]
    y32, s219, y28 = F["st_219"][:3]
    said("斯大林说 1932 年的工业产值是 1928 年的 219\\%，国家计委的数是 218.5\\%", y32, y28, s219, F["gp33_gross"][6])
    said("219\\% 的四年，平均每年增长约 21.6\\%，与他说的 22\\% 相合", s219, cagr(100, s219, 4), F["st_22"][0])
    chk("    four years (四年)", y32 - y28, told("219\\% 的四年", "的", "年"))
    said("总结自己也说，“在五年计划期间，我们的工业整体平均每年增长 21.6\\%”", F["gp33_216"][0])
    say("这些都是计划机关自己的数，相合只说明官方的说法前后一致")
    p, y, _ = F["gp33_newworks"]
    assert p == F["gp33i_world"][1]
    said("生铁在 1932 年是 620 万吨", y, p * M6)
    said("1928 年的人均 GDP，Maddison 的数比 1913 年低 3.1\\%，Markevich 与 Harrison 的是低约 3\\%", 1928, 1913,
         100 - ratio(1928), F["mh_1928"][5])
    sun = " ".join(maddison_meta()["sources_by_country"]["SUN"])
    a, b = re.search(r"(\d{4})-(\d{4}): Markevich, A\. and M\. Harrison", sun).groups()
    said("数据库 1913—1928 年的苏联数字本来就取自 Markevich 与 Harrison", int(a), int(b))   # not a second witness
    d22, y33 = F["we_telegram"]
    assert F["ru_directive"][1:] == [d22, y33]
    said("1933 年 1 月 22 日封锁边界的命令", y33, 1, d22)
    assert F["h17_feb1930"][1] == F["mnq_kulaks"][0]
    said("约 200 万“富农”被流放", F["mnq_kulaks"][0] * M6)
    assert F["h17_1921"][1] == F["mnq_1921"][2]
    said("1921 年的饥荒死了约 500 万人", F["mnq_1921"][0], F["mnq_1921"][2] * M6)
    said("切尔文的购买力提高 20\\%", F["gp29_chervonets"][0])
    said("到 1932 年，粮食的黑市价格是国家收购价格的 28 倍", F["cg_black"][6], F["cg_black"][7])
    said("计划要让农业生产增长 55\\%", F["gp29_growth"][3])
    G = grain()
    said("1932 年的粮食产量比 1928 年少了 22.2\\%", 1932, 1928, fall(G.loc[1928, "revised_mt"], G.loc[1932, "revised_mt"]))
    chk("    two thirds (三分之二)", F["h17_envisaged"][0], told("计划要让人均消费提高三分之二", "提高"))
    a, b, y0, y1 = F["we_meat"]
    said("1927—1933 年却少了 75\\%—90\\%", y0, y1, a, b)
    chk("    four years earlier (四年前)", Y["st_unemp"] - Y["gp29_unemp"], told("计划在四年前却预计", "计划在", "年前"))


def deeper(F, Y, Q):
    said("Allen（2003）的书没有取得", allen_year())
    assert "Princeton UP answered 403" in meta()["sources"]["davies2004"]["version"]
    said("哈宁的文章、Moorsteen 与 Powell（1966）", 1966)
    said("都据 Harrison（1993）的转述", Y["h93_sensation"])
    said("Conquest（1986）", F["mnq_conquest"][0])
    said("《纽约时报》与《每日电讯报》1932 年 11 月的话", F["st_telegraph"][0], mon("st_telegraph", "November"))
    d22, y33 = F["we_telegram"]
    d6, y28 = F["we_ration"]
    said("1933 年 1 月 22 日的电报据 Werth，1928 年 12 月 6 日政治局的决定也据 Werth", y33, 1, d22, y28, 12, d6)
    said("普列奥布拉任斯基的主张据 Harrison（1980），Hunter 的“紧绷”的计划也据 Harrison（1980）", Y["h80_preo"], Y["h80_hunter"])
    said("托洛茨基的话据哈耶克（1945）的转述", Y["hy_trotsky"])
    said("Harrison（2017）、Markevich 与 Harrison、Harrison 与 Markevich 都作 1921 年 3 月，苏联情报局 1929 年的手册作“1921 年 "
         "4 月”", Y["h17_breathing"], F["mh_nep"][0], mon("mh_nep", "March"), F["su_first"][0], F["su_april"][0],
         mon("su_april", "April"))
    assert "in March 1921" in Q["hm_nep"]
    said("卢布的稳定，Harrison（2017）说“直到 1923 年才实现”，手册把币制改革记在 1924 年 3 月", Y["h17_stab"], F["h17_stab"][0],
         F["su_reform"][0], mon("su_reform", "March"))
    y28, y27 = F["dv_ural"][:2]
    said("Werth 作 1928 年 1 月，Davies 说是 1928 年而不是 1927 年的收成以后", F["we_ural"][0], mon("we_ural", "January"), y28,
         y27)
    said("Harrison（2017）只说 1928 年先在乌拉尔与西伯利亚法外施行，1929 年推行到全国", Y["h17_urals"], *F["h17_urals"])
    P = hm_prices()
    assert ("November", 1917) in P and ("February", 1924) in P
    rs = int(re.search(r"Rostowski and Shapiro \((\d{4})\)", column("note")["hm_prices"]).group(1))
    said("1917—1924 年的物价倍数据 Harrison 与 Markevich 的表，表中的数取自 Rostowski 与 Shapiro（1991）", 1917, 1924, rs)
    say("Selyunin 的生卒年，国会图书馆的规范档没有记载，法国国家图书馆的数据里也没有找到")
    said("斯大林说 108\\%，国家计委的总结分成甲类 103.4\\% 与重工业人民委员部 109.6\\%", F["st_108"][0], *F["gp33_groupa"])
    _, _, _, o_tab = F["gp33i_oil"]
    said("1932 年的石油与天然气，总结的正文是 2,220 万吨，表是 2,229 万吨；计划的指标在计划书里一处作 2,170 万吨，一处作 2,200 万吨",
         1932, F["gp33_oil"][1] * M6, o_tab * M6, F["gp29_oil"][3] * M6, F["gp29_pig"][0] * M6)
    _, trusts = F["gp33i_trusts"]
    assert "under the authority of the People's Commissariat of Heavy Industry" in transcription("gp33i_trusts")
    said("1932 年的煤，总结的表是 6,437 万吨，按地区分的表只算重工业人民委员部的托拉斯，是 6,298.3 万吨", 1932,
         F["gp33i_coal"][3] * M6, trusts * 1000)
    said("计划的方案，1929 年的英译本", Y["gp29_variants"])
    said("Harrison 的约 600 万，说的是 1932 年开始的饥荒", F["h17_famine"][1] * M6, F["h17_famine"][0])
    w, d = F["we_total"], F["dv_10m"]
    said("Werth 的 650 万到 700 万，说的是 1930 年代初的几场饥荒", w[0] * M6, w[1] * M6, 1930)
    said("Davies 的 550 万到 600 万，算的是 1930—1933 年的全部超额死亡", d[8] * M6, d[9] * M6, d[6], 1900 + d[7])
    said("Allen 书里的 1,000 万夸大了，Allen 自己在另一页改成了 730 万", d[0] * M6, d[4] * M6)
    said("乌克兰的 390 万是 Rudnytskyi 等人的超额死亡，不含少出生的 60 万", F["ru_total"][1] * M6, F["ru_total"][2] * M6)
    said("哈萨克斯坦的估计在 100 万到 150 万以上之间", F["mnq_kazakh"][0] * M6, F["ca_15"][0] * M6)
    said("1927/28 年度一栏，工业总产值用的是 1928 年的数", 1927, 28, 1928)
    said("1932 年用的是日历年", 1932)
    said("每年的增长率与 85.7\\%", 100 * (ussr()[1937] - ussr()[1933]) / (ussr()[1940] - ussr()[1928]))
    assert "«Special quarter of 1930»" in column("note")["sc_budget"]
    said("苏联的统计年度在 1930 年以前按经济年度计，正文写作 1928/29 年度", 1930, 1928, 29)
    said("1929 年的计划书把 11.6 印成“11,6”", Y["gp29_oil"], F["gp29_oil"][0], None)   # the misprint itself:
    assert "11,6" in Q["gp29_oil"] and read("11,6", "comma") == [F["gp29_oil"][0]]
    said("战时共产主义征收农业产出的 70\\%", F["cg_requisition"][0])
    said("1930 年 3 月的骚乱", F["cg_riots"][0], mon("cg_riots", "March"))
    said("国家计委的 50 名专家", F["gr_fifty"][0])
    said("乌克兰每天的死亡人数与 1932—1933 年的逮捕人数", F["we_arrests"][1], 1900 + F["we_arrests"][2])
    said("哈宁的生年据 Harrison（1993）", Y["h93_khanin"])


def legacy(F, Y, Q):
    said("早在 1939 年，他就写了一篇论文", F["nb75_1939"][0])
    said("1975 年的诺贝尔经济学奖", Y["nb75_prize"])
    said("1973 年的颁奖公告说", Y["nb73_planning"])
    ts, cia, kh = F["h93_t1_2840"]
    assert ts / cia > told("官方的增长率是西方重估的两倍多", "重估的", "倍多")
    chk("    Khanin about half the Western estimate (一半左右)", kh / cia, told("哈宁的估计又只有西方重估的一半左右", "重估的", "左右"),
        tol=0.05)


def takeaways(F, Y, Q):
    said("1921 年 3 月起的新经济政策恢复了农业与小工业的市场，1924 年 3 月的币制改革收回了旧卢布", F["h17_breathing"][1], 3,
         F["su_reform"][0], 3)
    _, p32, _, _ = F["gp33i_world"]
    said("第一个五年计划 1929 年 4 月获得批准。按 1926/27 年度的价格，工业总产值的计划完成了 93.7\\%；生铁只到了指标的 62\\%",
         F["h17_april"][0], 4, 1926, 27, F["gp33_937"][-1], 100 * p32 / F["gp33_task"][2])
    said("苏联 1930 年代初的集中平衡只有几十种物资", 1930)
    assert sum(F["gr_balances"]) < 100
    w, d = F["we_total"], F["dv_10m"]
    said("强制集体化、200 万人被迁走或关押、1932—1933 年的饥荒", F["h17_feb1930"][1] * M6, 1932, 1933)
    lo = min(d[8], F["h17_famine"][1], w[0])
    hi = max(d[9], F["h17_famine"][1], w[1])
    said("各家的估计多在 550 万到 700 万之间，汇总的范围是 500 万到 1,080 万", lo * M6, hi * M6, F["mnq_range"][0] * M6,
         F["mnq_range"][1] * M6)
    ts, cia, kh = F["h93_t1_2840"]
    said("官方说 1928—1940 年每年增长 13.9\\%，西方的重估是 6.1\\%，哈宁是 3.2\\%", 1928, 1940, ts, cia, kh)


def selfcheck(F, Y, Q):
    a12, a21, (f1, f2), _ = BAL["a12"], BAL["a21"], BAL["f"], BAL["steel2"]
    A = np.array([[0, a12], [a21, 0]])
    L = np.linalg.inv(np.eye(2) - A)
    dc = SC1["coal"] - f2
    said("煤的最终使用从 20 提高到 25", f2, SC1["coal"])
    dx = L @ np.array([0, dc])
    said("钢要多产$0.125\\times5=0.625$，煤要多产$1.25\\times5=6.25$", L[0, 1], dc, dx[0], L[1, 1], dc, dx[1])
    said("若$a_{12}a_{21}\\geq1$", 1)
    said("$\\det(I-A)=1-a_{12}a_{21}\\leq0$", 1, 0)
    for k12, k21 in ((0.5, 2.5), (1, 1.5), (0.1, 2), (0.4, 2)):                 # a12 a21 > 1: no positive solution
        det = np.linalg.det(np.eye(2) - np.array([[0, k12], [k21, 0]]))
        chk(f"    det(I - A) = 1 - a12 a21 ({k12}, {k21})", det, 1 - k12 * k21)
        x = np.linalg.solve(np.eye(2) - np.array([[0, k12], [k21, 0]]), np.array([1.0, 1.0]))
        assert (k12 * k21 > 1) == (x.min() < 0), (k12, k21, x)
    a, b, c, d = LANGE["a"], LANGE["b"], LANGE["c"], SC3["d"]
    ps = (a - c) / (b + d)
    said("供给改成$S=10+3p$，需求不变。均衡价格是多少？$\\lambda=0.2$时收敛吗", c, d, LANGE["lam"])
    said("$100-2p=10+3p$，$p^{*}=18$。$1-0.2\\times(2+3)=0$", a, b, c, d, ps, 1, LANGE["lam"], b, d, 1 - LANGE["lam"] * (b + d))
    G = grain()
    r28, p28, r32, p32 = (G.loc[1928, "revised_mt"], G.loc[1928, "procurement_mt"], G.loc[1932, "revised_mt"],
                          G.loc[1932, "procurement_mt"])
    said("1928 年征购 1,080 万吨，产量 7,340 万吨；1932 年征购 1,900 万吨，产量 5,710 万吨", 1928, p28 * M6, r28 * M6, 1932,
         p32 * M6, r32 * M6)
    said("1928 年留下$73.4-10.8=62.6$百万吨，1932 年留下$57.1-19.0=38.1$百万吨，少了约 39\\%", 1928, r28, p28, r28 - p28, 1932,
         r32, p32, r32 - p32, fall(r28 - p28, r32 - p32))
    (m0, m1), (pm0, pm1), (g0, g1), (pg0, pg1) = IDX["m"], IDX["pm"], IDX["g"], IDX["pg"]
    L0 = (m1 * pm0 + g1 * pg0) / (m0 * pm0 + g0 * pg0)
    L1 = (m1 * pm1 + g1 * pg1) / (m0 * pm1 + g0 * pg1)
    said("例题里机器从 2 台增加到 10 台，按第 0 年的价格增长 80\\%，按第 1 年的价格只有 30.8\\%", m0, m1, 0, 100 * (L0 - 1), 1,
         100 * (L1 - 1))
    ts, kh = F["h93_t1_2840"][0], F["h93_t1_2840"][2]
    n = SC6["years"]
    said("官方说每年增长 13.9\\%，哈宁说 3.2\\%。按这两个速度，12 年后的产出各是开始时的几倍", ts, kh, n)
    assert n == 1940 - 1928
    said("$1.139^{12}\\approx4.77$，$1.032^{12}\\approx1.46$", 1 + ts / 100, (1 + ts / 100) ** n, 1 + kh / 100,
         (1 + kh / 100) ** n)


def ending(F, Y, Q):
    d7, y33 = F["st_date"]
    said("1933 年 1 月 7 日，斯大林在报告里拿苏联与资本主义国家比较", y33, 1, d7)
    y32, s219, y28, us, uk, de = F["st_219"]
    assert "in the U.S.A. dropped during this same period to 56 per cent, in Britain to 80 per cent, in Germany to 55" \
        in Q["st_219"]
    said("到 1932 年底，苏联的工业产值是 1928 年的 219\\%，美国跌到了 56\\%，英国是 80\\%，德国是 55\\%", y32, y28, s219, us, uk, de)
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 32's question"
    assert t.index("\\end{answers}") < t.index("1933 年 1 月 7 日，斯大林在报告里拿苏联")
    ch32 = (ROOT / "zh" / "ch32_generaltheory.tex").read_text(encoding="utf-8")
    assert f"\\guidequestion{{{NEXT}}}" in ch32


def models() -> None:
    """The key equations, and their arithmetic checked with numbers."""
    say("x_i+m_i+s_{i,0}=\\sum_j a_{ij}\\,x_j+c_i+e_i+s_{i,1}.\\label{eq:soviet-balance}")
    say("p_{t+1}=p_t+\\lambda\\,\\bigl[D(p_t)-S(p_t)\\bigr],\\qquad \\lambda>0.\\label{eq:soviet-lange}")
    say("Q^{(0)}=\\frac{\\sum_j p_{j,0}\\,q_{j,1}}{\\sum_j p_{j,0}\\,q_{j,0}},\\qquad\nQ^{(1)}=\\frac{\\sum_j p_{j,1}\\,q_{j,1}}"
        "{\\sum_j p_{j,1}\\,q_{j,0}}.\\label{eq:soviet-index}")
    rng = np.random.default_rng(31)
    # material balances: x = Ax + f = f + Af + A^2 f + ... for a productive A; with imports, exports and stocks
    for _ in range(5):
        n = 4
        A = rng.uniform(0, 0.2, (n, n))
        f = rng.uniform(1, 10, n)
        x = np.linalg.solve(np.eye(n) - A, f)
        series = sum(np.linalg.matrix_power(A, k) @ f for k in range(200))
        chk("    eq:soviet-balance: (I - A)^{-1} f = f + Af + A^2 f + ...", float(np.max(np.abs(x - series))), 0,
            tol=1e-9)
        m, e, s0, s1 = (rng.uniform(0, 2, n) for _ in range(4))
        c = f + m - e - s1 + s0                                                 # f = c + e - m + s1 - s0
        chk("    sources = uses, good by good", float(np.max(np.abs(x + m + s0 - (A @ x + c + e + s1)))), 0, tol=1e-9)
        dx = np.linalg.solve(np.eye(n) - A, np.eye(n)[0])
        one_round = np.eye(n)[0] + A @ np.eye(n)[0]
        chk("    one round leaves A^2 times the change uncovered", float(np.max(np.abs(
            (A @ (np.eye(n)[0] + A @ np.eye(n)[0]) + np.eye(n)[0]) - one_round - A @ A @ np.eye(n)[0]))), 0, tol=1e-12)
        assert np.all(dx >= one_round - 1e-12)
    # Lange: the gap is multiplied by 1 - lambda (b + d)
    for a, b, c, d, lam, p0 in ((100, 2, 10, 1, 0.2, 10), (50, 1, 5, 2, 0.5, 30), (80, 3, 0, 1, 0.1, 5)):
        ps = (a - c) / (b + d)
        p = p0
        for t in range(1, 6):
            p = p + lam * ((a - b * p) - (c + d * p))
            chk(f"    eq:soviet-lange ({a}, {b}, {c}, {d}, {lam}): the gap after round {t}", p - ps,
                (1 - lam * (b + d)) ** t * (p0 - ps), tol=1e-9)
    # index numbers: the Fisher index lies between the two; Laspeyres > Paasche when the fast good gets cheaper
    for _ in range(20):
        q0, q1 = rng.uniform(1, 10, 2), rng.uniform(1, 10, 2)
        p0, p1 = rng.uniform(1, 10, 2), rng.uniform(1, 10, 2)
        L, P = (p0 @ q1) / (p0 @ q0), (p1 @ q1) / (p1 @ q0)
        assert min(L, P) - 1e-12 <= math.sqrt(L * P) <= max(L, P) + 1e-12
        g, r = q1 / q0, p1 / p0
        if (g[0] - g[1]) * (r[0] - r[1]) < 0:                                   # the faster-growing good became cheaper
            assert L >= P - 1e-12, (q0, q1, p0, p1)


def figures_data(F) -> None:
    """What the figures assert of their data."""
    G = grain()
    assert G.official_mt.idxmax() == 1937 and G.revised_mt.idxmin() == 1932       # the harvest's low point
    assert G.procurement_mt.loc[1927:1933].idxmax() == 1933 and G.procurement_mt[1932] > 1.7 * G.procurement_mt[1928]
    assert (G.dw_min_mt.dropna() <= G.dw_max_mt.dropna()).all()
    U = ussr()
    assert U.loc[1913:1940].idxmin() == 1921 and U.loc[1913:1940].idxmax() == 1939
    M = maddison()
    assert set(SIX) == set(M.index) and (M[1940] > 0).all()
    P = {k: (100 * a / c, 100 * b / c) for k, a, b, c in plan_items()}
    chk("fig:soviet_plan: gross output 1932, per cent of the plan (93.7 in the text)", P["gross"][1], 93.7, tol=0.05)
    chk("fig:soviet_plan: pig iron 1932, per cent of the plan (62 in the text)", P["pig"][1], 62, tol=0.5)
    assert P["oil"][1] > 100 > max(P[k][1] for k in ("gross", "pig", "steel", "coal"))   # only oil beat its plan
    assert all(P[k][0] < P[k][1] for k in P)
    assert M.loc["IND", 1940] < M.loc["SUN", 1940] < M.loc["ARG", 1940]            # between India and Argentina


# ---------------------------------------------------------------------------------------------------
# 5. The book
# the life dates from rows of the snapshot: words -> (row, index of the birth year, index of the death year)
ROW_LIVES = {"Joseph Stalin，1878—1953": ("loc_stalin", 0, 1),
             "Ludwig von Mises，1881—1973": ("loc_mises", 0, 1),
             "Vladimir Lenin，1870—1924": ("loc_lenin", 0, 1),
             "Evgenii Preobrazhensky，1886—1937": ("loc_preobrazhensky", 0, 1),
             "Nikolai Bukharin，1888—1938": ("loc_bukharin", 0, 1),
             "Leon Trotsky，1879—1940": ("loc_trotsky", 0, 1),
             "Oskar Lange，1904—1965": ("loc_lange", 0, 1),
             "Friedrich Hayek，1899—1992": ("loc_hayek", 0, 1),
             "Leonid Kantorovich，1912—1986": ("loc_kantorovich", 0, 1)}
# the beginning of each authority record's heading (the Library of Congress romanizes Russian names with diacritics)
LOC_HEADS = {"loc_stalin": "Stalin, Joseph", "loc_mises": "Von Mises, Ludwig", "loc_lenin": "Lenin, Vladimir",
             "loc_preobrazhensky": "Preobrazhenskiĭ, E. A. (Evgeniĭ", "loc_bukharin": "Bukharin, Nikolaĭ",
             "loc_trotsky": "Trotsky, Leon", "loc_lange": "Lange, Oskar", "loc_hayek": "Hayek, Friedrich",
             "loc_kantorovich": "Kantorovich, L. V. (Leonid"}
# what other chapters tell: (words of this chapter, chapter where it is told, words there)
EVENTS = [("德国的恶性通胀在 1923 年 11 月止住（\\chref{ch:weimar}）", "ch26_weimar",
           "1923 年 11 月 20 日，柏林交易所把美元的官价定在 4.2 万亿纸马克"),
          ("就是$x=Ax+f$。这正是\\chref{ch:marx}里里昂惕夫的方程（\\exref{ex:marx-io}）", "ch22_marx",
           "解 $(I-A)x=f$（\\texttt{numpy.linalg.solve}）"),
          ("\\chref{ch:prices}讲过，用哪一年的价格给产品加权，增长率可以差很多", "ch03_prices",
           "用旧价格给它更大的权数，增长率就更高"),
          ("里昂惕夫的投入产出方法既用于分散的市场经济，也用于中央计划经济的预测与计划", "ch22_marx",
           "公告说，这个方法在分散的市场经济与中央计划经济里，都用于预测与计划"),
          ("今天的国民核算里还有它的骨架（\\chref{ch:accounts}）", "ch22_marx",
           "部门之间的收支相抵，是今天国民核算的骨架（\\chref{ch:accounts}）"),
          ("物资平衡表是计划人员版本的投入产出表", "ch22_marx", "计划经济的物资平衡表是\\chref{ch:soviet}与\\chref{ch:planned}的题目")]
# the chapters this one hands on to (FORWARD_REFS rows opened by Chapter 31)
LATER = {"ch:planned": "ch43_planned", "ch:transition": "ch59_transition", "ch:datareliability": "ch81_datareliability",
         "ch:warfinance": "ch34_warfinance", "ch:hyperinflation": "ch52_hyperinflation",
         "ch:generaltheory": "ch32_generaltheory"}


def book(F, Q):
    """Life dates and what other chapters tell."""
    t = tex_text()
    for words, (rid, i, j) in ROW_LIVES.items():
        assert words in t, words
        assert f"{F[rid][i]:.0f}—{F[rid][j]:.0f}" in words, (words, rid)
        assert Q[rid].startswith(LOC_HEADS[rid]), (rid, Q[rid])               # the person of the record
        COVERED.append(words)
    for here, ch, there in EVENTS:
        assert here in t, here
        assert there in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (ch, there)
    for label, ch in LATER.items():
        assert f"\\chref{{{label}}}" in t, label
        assert f"\\label{{{label}}}" in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (label, ch)
    for label in ("ch:marx", "ch:depressionworld"):                            # the prerequisites
        assert f"\\chref{{{label}}}\\enspace\\nameref{{{label}}}" in t, label
    print(f"ok {len(ROW_LIVES) + 1} life dates, {len(EVENTS)} statements of other chapters, {len(LATER)} later chapters")


def identities(F) -> None:
    """The table snapshots' identities, and the values read on page images against the text and the other table."""
    G = grain()
    chk("Table A.2, 1932: the row mnq_table = the table snapshot (revised, official, DW min, DW max, procurement)",
        F["mnq_table"], [G.loc[1932, c] for c in ("revised_mt", "official_mt", "dw_min_mt", "dw_max_mt",
                                                  "procurement_mt")])
    chk("Gosplan 1933, p. 99: the coal plan in the table = the plan of 1929", F["gp33i_coal"][2], F["gp29_targets"][1])
    chk("Gosplan 1933, p. 99: the oil plan in the table = the text of p. 104 = the plan of 1929 (21.7)",
        [F["gp33i_oil"][2], F["gp33_oil"][2]], [F["gp29_oil"][3]] * 2)
    chk("    the oil of 1932: text 22.2, table 22.29", F["gp33i_oil"][3], F["gp33_oil"][1], tol=0.1)
    chk("Gosplan 1933: pig iron 1928 3.4 (table) against 3.283 million in 1927-28 (text)", F["gp33i_world"][0],
        F["gp33_pig28"][2] / M6, tol=0.15)
    chk("    steel 1928 4.3 (table) against 4.176 million in 1927-28 (text)", F["gp33i_world"][2],
        F["gp33_steel28"][0] / M6, tol=0.15)
    chk("    the coal of the trusts (62,983 thousand tons) < the total (64.37 million)",
        float(F["gp33i_trusts"][1] < F["gp33i_coal"][3] * 1000), 1)
    tr0, tt0, tr1, tt1 = F["sc_budget"]
    assert tt0 < tr0 and tt1 < tr1
    M = maddison()
    assert (M.columns == list(range(1913, 1941))).all()
    chk("Maddison: the USSR's 1928 / 1913 (96.9) against Markevich and Harrison's 'around 3 percent' short",
        100 - ratio(1928), F["mh_1928"][5], tol=0.5)


def witnesses(F, Q):
    """Second witnesses of statements of the text, and the bibliography block of the chapter."""
    chk("93.7 per cent: Stalin = Gosplan 1933", F["st_937"][1], F["gp33_937"][-1])
    chk("1932 = 219 (Stalin) and 218.5 (Gosplan) per cent of 1928", F["st_219"][1], F["gp33_gross"][6], tol=0.5)
    chk("22 per cent a year (Stalin) against 219 per cent in four years", cagr(100, F["st_219"][1], 4), F["st_22"][0],
        tol=0.5)
    chk("21.6 per cent a year (Gosplan) against 218.5 per cent in four years", cagr(100, F["gp33_gross"][6], 4),
        F["gp33_216"][0], tol=0.05)
    chk("pig iron 1932: Gosplan's text (p. 60) = its table (p. 112)", F["gp33_newworks"][0], F["gp33i_world"][1])
    chk("the telegram of 22 January 1933: Werth = Rudnytskyi et al.", F["we_telegram"], F["ru_directive"][1:])
    chk("two million kulaks: Harrison = Markevich, Naumenko and Qian", F["h17_feb1930"][1], F["mnq_kulaks"][0])
    chk("the famine of 1921, five million: Harrison = Markevich, Naumenko and Qian", F["h17_1921"][1], F["mnq_1921"][2])
    chk("the pig-iron target of 10 million tons: the plan (1929) = the report (1933)", F["gp29_pig"][1],
        F["gp33_task"][2])
    chk("the Kazakh famine: Cameron 1.5 million = Werth's upper bound = MNQ's upper bound",
        [F["we_total"][4], F["mnq_kazakh"][1]], [F["ca_15"][0]] * 2)
    assert F["mh_nep"][0] == F["hm_nep"][0] == F["h17_breathing"][1] != F["su_april"][0] or "April" in Q["su_april"]
    # the licences and the bibliography
    m = meta()
    lic = m["license"]
    for rid in ("st_pd", "su_copyleft", "gp29_copyright", "la_copyright", "hy_notice", "mnq_copyright",
                "cg_copyright", "csp_licence", "ca_copyright", "dv_eha", "nb75_copyright"):
        assert Q[rid] in lic, rid
    assert Q["ewjus_licence220"] == Q["ewjus_licence217"] and Q["ewjus_licence220"] in lic
    for words in ("short phrases only", "are public data", "its United States term of 95 years ended with 2024"):
        assert words in lic, words
    assert "CC BY 4.0" in maddison_meta()["license"] and "CONDITIONS UNDER WHICH ALL ORIGINAL PAPERS MUST BE CITED" in \
        maddison_meta()["license"]
    assert Q["mnq_copyright"] in _table("soviet_grain")[1]["license"]
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    start = bib.index("% ---- 第 31 章")
    following = re.search(r"^% ---- 第 \d+ 章", bib[start + 1:], re.MULTILINE)
    end = start + 1 + following.start() if following else bib.index("\\end{thebibliography}")
    block = bib[start:end]
    items = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", block)}
    tex = lambda s: s.replace("\\", "\\textbackslash{}").replace("&", "\\&").replace("_", "\\_")   # noqa: E731
    assert "Public Domain: Marxists Internet Archive (2008)." in items["stalin1933"]
    assert "公有领域" in items["stalin1933"] and "Foreign Languages Publishing House" in items["stalin1933"]
    assert "GNU Free Documentation License" in items["suib1929"]
    assert "Horace Liveright" in items["gosplan1929"] and "只引短句" in items["gosplan1929"]
    for key, rid in (("mnq2021", "mnq_copyright"), ("cggt2013", "cg_copyright")):
        assert Q[rid] in items[key], key                                     # the © notice as printed
    assert "NBER Working Paper 29089" in items["mnq2021"] and "NBER Working Paper 19425" in items["cggt2013"]
    assert "Creative Commons Attribution 4.0 International License" in items["rudnytskyi2015"]
    for key in ("cameron2016", "werth2016"):
        assert "Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License" in items[key], key
        assert "不作改编" in items[key], key
    for key in ("mises1935", "lange1938", "hayek1945", "davies2004", "gregory2005", "harrison1980", "harrison1993",
                "harrison2017", "markevich2011", "harrison2018", "nobel1975"):
        assert "只引短语" in items[key] or "只引短句" in items[key], key
    assert tex(Q["la_copyright"])[:60] in items["lange1938"]
    assert Q["hy_notice"] in items["hayek1945"]
    assert "© Nobel Prize Outreach 2026" in items["nobel1975"]
    assert "id.loc.gov" in items["loc31"] and "公共数据" in items["loc31"]
    # the publication facts of the bibliography, from the title pages and page headers
    assert Q["st_source"] == "Publisher: Foreign Languages Publishing House, Moscow, 1954"
    assert "Moscow: Foreign Languages Publishing House, 1954" in items["stalin1933"]
    assert Q["su_first"] == "First Published: 1929" and f"Washington, {F['su_first'][0]:.0f}" in items["suib1929"]
    assert Q["dv_pub"] == "Published by EH.NET (June 2004)" and "EH.Net, June 2004" in items["davies2004"]
    assert Q["gp33_printed"] == "Printed in the Union of Soviet Socialist Republics" and "MOSCOW" in Q["gp33_title"]
    assert f"Moscow: Cooperative Publishing Society of Foreign Workers in the U.S.S.R., {F['gp33_title'][0]:.0f}" in \
        items["gosplan1933"]
    assert "HORACE LIVERIGHT - - NEW YORK" == Q["gp29_title"] and "New York: Horace Liveright, 1929" in items["gosplan1929"]
    for rid in ("loc_stalin", "loc_lenin", "loc_mises", "loc_lange", "loc_hayek", "loc_preobrazhensky", "loc_bukharin",
                "loc_kantorovich", "loc_trotsky"):
        assert Q[rid].split(",")[0] in items["loc31"], rid
    allitems = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", bib)}
    mm = maddison_meta()
    for iso in SIX:                                                               # the original sources, as required
        for s in mm["sources_by_country"][iso]:
            head = s.split(":", 1)[1].strip()[:25].replace("&", "\\&").replace("$", "\\$")
            assert head in items["mpd31src"], (iso, head)
    keys = set(allitems)
    cited = {k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", tex_text()) for k in c.split(",")}
    assert cited <= keys, sorted(cited - keys)
    assert set(items) <= cited, sorted(set(items) - cited)
    srcs = set(m["sources"])
    for key in items:                                                              # every work of the block is a source
        assert key in srcs or key in ("loc31", "mpd31src", "gosplan1933"), key
    print(f"ok {len(cited)} works cited, {len(items)} of them in the bibliography block of Chapter 31")


NAMES = ("Harrison|Markevich|Naumenko|Qian|Gregory|Davies|Wheatcroft|Allen|Werth|Cameron|Rudnytskyi|Meslé|Vallin|"
         "Cheremukhin|Bergson|Chapman|Nutter|Moorsteen|Powell|Hunter|Kondrashin|Conquest|Maddison|Bolt|Gerschenkron")


def counts() -> None:
    """The editor's limits: “不能” at most about a dozen; no cited author as the subject of a sentence outside the
    史料说明; the forbidden words."""
    t = tex_text()
    main = re.sub(r"\\begin\{deeper\}\[史料说明\].*?\\end\{deeper\}", "", t, flags=re.DOTALL)
    n = t.count("不能")
    print(f"ok “不能” {n} times")
    assert n <= 12, n
    verbs = "认为|写道|说|指出|记述|估计|承认|报道|记载|提到|列出|给出|发现|统计|算出|早有|看法|有类似|怀疑|强调"
    subj = re.findall(r"(?:^|[。；：，\n])\s*(?:" + NAMES + r")(?:（\d{4}）)?\s*(?:" + verbs + ")", main)
    assert not subj, subj
    subj2 = re.findall(r"(?:^|[。；：，\n])\s*(?:" + NAMES + r")(?:[、与和] ?(?:" + NAMES + r"))*(?: 等人)?(?:（\d{4}）)?\s*"
                       r"(?:" + verbs + ")", main)
    assert not subj2, subj2
    for words in ("本书没有找到", "没能取得", "没有取得", "没有读到"):
        assert words not in main, words                                          # only in the 史料说明
    narrative = re.sub(r"“[^”]*”", "", t)                                       # the quotations render the sources
    for bad in ("这一节回答", "不是因为", "而是", "详见", "\\textsc", "\\underline", "\\clearpage"):
        assert bad not in narrative, bad
    assert not re.search(r"(?<![意看])见\\(?:chref|secref|figref|tabref|exref|eqref)", t)
    assert "\\chapterstub" not in t


def main() -> None:
    df = _rows()
    F, Y, Q = facts(), years(), quotes()
    check_readings(df)
    check_text(df)
    identities(F)
    guide(F, Y, Q)
    opening(F, Y, Q)
    world(F, Y, Q)
    plan(F, Y, Q)
    balances(F, Y, Q)
    famine(F, Y, Q)
    casebox(F, Y, Q)
    calculation(F, Y, Q)
    growth(F, Y, Q)
    debate(F, Y, Q)
    check_section(F, Y, Q)
    deeper(F, Y, Q)
    legacy(F, Y, Q)
    takeaways(F, Y, Q)
    selfcheck(F, Y, Q)
    ending(F, Y, Q)
    models()
    figures_data(F)
    book(F, Q)
    witnesses(F, Q)
    counts()
    coverage()
    anchors(str(TEX), df["id"], script=Path(__file__))


if __name__ == "__main__":
    main()
