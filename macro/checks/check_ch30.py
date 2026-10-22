"""Chapter 30 (1930 年代的另类出路：纳粹德国、高桥财政与瑞典): every number and every quotation in
zh/ch30_alternatives.tex.

    python3 checks/check_ch30.py

Inputs:
  alternatives_facts         quotations of Shizume (2009, Bank of Japan Review), Ide (2003, IMES Discussion Paper), the
                             Bank of Japan's chronology and terms of use, the portraits and the chronology of the
                             National Diet Library, the judgment of the International Military Tribunal and Nazi
                             Conspiracy and Aggression, vols. II and VII (the prosecution's brief on Schacht, Puhl's
                             deposition EC-436, the Reichsbank directors' memorandum EC-369), the BIS's annual report of
                             1937 and its terms, four Acts of the Statutes at Large, Berg and Jonung (1998), Eichengreen
                             and Sachs (1984), Bernanke and James (1991), the Neue Deutsche Biographie, the Riksbank's
                             history pages and the authority records of the Library of Congress (checked by
                             data/fetch/verify_web_quotes.py); the rows with an empty quotation are values and words read
                             on page images (the Bank of Japan's history of 1984; Historical Statistics, series Y 339-341),
                             with a transcription between « and » in the note where the chapter renders the words
  alternatives_reichsbank    the Reichsbank's reserves, bills and notes (Banking and Monetary Statistics, Table 167)
  alternatives_boj_sales     the bonds the Bank of Japan underwrote and sold, by half-year (its history, Table 1-17)
  alternatives_yen_monthly   the yen in cents, monthly, 1929-1938 (Banking and Monetary Statistics, Table 173)
  alternatives_fx_annual     the krona, the pound and the yen in cents, annual, 1929-1939 (the same table)
  riksbank_sweden_1925_1939, riksbank_sweden_monthly_1929_1939
                             Sweden's consumer price index (Edvinsson and Soederberg) and the Riksbank's discount rate
                             (Waldenstroem), from the Riksbank's site
  maddison2023_interwar      GDP per head, 1929-1938 (Maddison Project Database 2023)
The figure module figsrc/fig_ch30.py imports its data from here.

What is checked here:
  1. readings   every number of the value column of alternatives_facts is read from its quotation (digits, English
                number words, ordinals, '1s.2d.', German dates, a decimal comma and the OCR's misreadings, each named
                in the note)
  2. the text   every “…” of the chapter is the chapter's rendering of a quotation (TRANSLATIONS), with the source's
                words listed in KEYWORDS (for a row read on a page image, the words of its transcription)
  3. numbers    every number of the text, section by section: said() finds the phrase and compares each number it
                prints (with its unit 万, 亿) with the value computed from the snapshots or with a teaching input
                stated in the text, within half a unit of the last printed digit; Chinese numerals are read by zh()
  4. coverage   every Arabic number of the text (outside labels, citations, cross-references, the key equations and
                math subscripts) lies inside a phrase checked by said()
  5. the book   identities of the table snapshots, second witnesses, life dates, what other chapters tell, the
                bibliography block of the chapter and its licence notices
  6. anchors    the paraphrase anchors `% 据: ...` name rows of alternatives_facts

Models (the chapter's key equations):
    MEFO bills (eq:alternatives-mefo): G - T + iB = dB^n + dW^o + dH with H = W^c + X; a bill the Reichsbank
        discounts moves from W^o to W^c and adds to H, the deficit unchanged
    price-level and inflation targets (eq:alternatives-level): p*_t = p_0 + t pi* against p*_t = p_{t-1} + pi*;
        Wicksell's rule i_{t+1} = i_t + beta pi_t sums to i_t - i_0 = beta (p_t - p_0)
    a price ceiling: linear demand and supply, the shortage at the ceiling and the price at which the supply clears
"""
from __future__ import annotations

import math
import os
import re
from datetime import date
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from common import ROOT, anchors, load_snapshot, quoted

TEX = Path(os.environ.get("CH30_TEX", ROOT / "zh" / "ch30_alternatives.tex"))   # a scratch copy for mutation tests
GUIDE = "纳粹德国、高桥财政下的日本和瑞典都较早走出了萧条，各自靠的是什么？代价记在了哪里？"
PREV = GUIDE                                         # Chapter 29's NEXT
NEXT = "没有市场价格，经济能不能算清楚该生产什么？"      # Chapter 31's question
# Teaching inputs stated in the text
UW = {"deficit": 100, "sold": 90}                    # ex:alternatives-underwrite
MEFO = {"spend": 10, "disc1": 4, "disc2": 3}         # ex:alternatives-mefo
CEIL = {"a0": 120, "a1": 140, "months0": 24, "months1": 6}    # ex:alternatives-ceiling: Qd = a - P, Qs = P
PLT = {"p0": 0, "pi": 2, "shock": 3, "beta": 0.1}    # ex:alternatives-target
SC1 = {"spend": 50, "banks": 30, "disc": 20, "disc2": 10}     # self-check 1
SC2 = {"a": 100, "ceiling": 40}                      # self-check 2
SC3 = {"pi": 0, "low": 2}                            # self-check 3
M6, B9 = 10 ** 6, 10 ** 9
SIX = ["DEU", "JPN", "SWE", "USA", "GBR", "FRA"]     # fig:alternatives_gdp
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                      "September", "October", "November", "December"], 1)}


def chk(what: str, value, expected=None, tol: float = 1e-9, rel: float = 0.0) -> float:
    """quoted() with a tolerance for floating-point error on exact values; a list is compared element by element."""
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
    df, m = load_snapshot("alternatives_facts", dtype=str, keep_default_na=False)
    assert 30 in m["used_in"]
    assert df["id"].is_unique
    return df


@lru_cache(maxsize=None)
def meta() -> dict:
    return load_snapshot("alternatives_facts")[1]


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
    assert 30 in m["used_in"], name
    assert "sources" not in m, name                                # table snapshots carry no 'sources' key
    return df, m


def reichsbank() -> pd.DataFrame:
    """The Reichsbank at the end of each year 1929-1938 and on 28 February 1938, million reichsmarks: reserves of
    gold and foreign exchange, bills (and checks) including Treasury bills, note circulation; indexed by date."""
    df, _ = _table("alternatives_reichsbank")
    assert len(df) == 11
    return df.set_index("date")


def boj_sales() -> tuple[pd.DataFrame, pd.Series]:
    """The Bank of Japan's Table 1-17: bonds underwritten (A) and sold (B), thousand yen, by half-year from
    November 1932 to December 1936, and the printed total of 1933-1935."""
    df, _ = _table("alternatives_boj_sales")
    total = df.iloc[-1]
    assert (total["first"], total["last"]) == ("1933-01", "1935-12")
    halves = df.iloc[:-1].copy()
    assert len(halves) == 9
    return halves, total


def year_sum(halves: pd.DataFrame, y: int, col: str) -> float:
    return float(halves[halves["first"].str.startswith(str(y))][col].sum())


def yen_monthly() -> pd.Series:
    """The yen in US cents, monthly averages of daily rates, indexed by (year, month)."""
    df, _ = _table("alternatives_yen_monthly")
    assert len(df) == 120
    return df.set_index(["year", "month"]).cents_per_yen


def fx() -> pd.DataFrame:
    df, _ = _table("alternatives_fx_annual")
    return df.set_index("year")


def kronor_per_pound() -> pd.Series:
    X = fx()
    return X.cents_per_pound / X.cents_per_krona


def pence_per_yen() -> pd.Series:
    X = fx()
    return 240 * X.cents_per_yen / X.cents_per_pound


def cpi() -> pd.Series:
    """Sweden's consumer price index (Edvinsson and Soederberg, 1914 = 100), annual, 1925-1939."""
    df, _ = _table("riksbank_sweden_1925_1939")
    return df.set_index("year").cpi_1914_100


def cpi1931() -> pd.Series:
    """The same index on 1931 = 100 (the book's own calculation)."""
    c = cpi()
    return 100 * c / c[1931]


def discount() -> pd.Series:
    """The Riksbank's discount rate, monthly, 1929-1939, indexed by 'YYYY-MM'."""
    df, _ = _table("riksbank_sweden_monthly_1929_1939")
    assert len(df) == 132
    return df.set_index("month").discount_rate


def maddison_meta() -> dict:
    return _table("maddison2023_interwar")[1]


def maddison() -> pd.DataFrame:
    """GDP per head (2011 international dollars), economies by ISO code x years 1929-1938."""
    df, _ = _table("maddison2023_interwar")
    return df.pivot(index="country", columns="year", values="gdppc_2011usd")


def ratios() -> pd.DataFrame:
    """GDP per head, per cent of 1929, for the six economies of the figure."""
    M = maddison().loc[SIX]
    return 100 * M.div(M[1929], axis=0)


def goldexits() -> pd.DataFrame:
    """Chapter 29's Table 2.1 of Bernanke and James (the table tab:depressionworld-exits prints), by country."""
    df, m = load_snapshot("depressionworld_goldexits")
    assert 29 in m["used_in"]
    return df[df.group.notna()].set_index("country")


def ym(s: str) -> tuple[int, int]:
    """'1931-09' -> (1931, 9)."""
    y, m = s.split("/")[0].split("-")
    return int(y), int(m)


def pound_parity() -> float:
    """The pound's parity in cents, as Chapter 27's table prints it ($4.8665)."""
    assert "战前平价，每英镑 4.8665 美元" in (ROOT / "zh" / "ch27_interwar.tex").read_text(encoding="utf-8")
    return 486.65


def fall(a: float, b: float) -> float:
    """The fall from a to b, per cent."""
    return 100 * (1 - b / a)


def rise(a: float, b: float) -> float:
    return 100 * (b / a - 1)


# ---------------------------------------------------------------------------------------------------
# 1. Readings of the numbers
SMALL = {"a": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "twelve": 12}
MULT = {"hundred": 100, "thousand": 1000}
NTH = {"fifth": 5}
TIMES = {"twice": 2}
# misreadings of the OCR, each named in the note of its row
OCR = {"11": 2}                                           # 'Reichsgesetxblatt, 1924, 11': Part II


def cardinal(s: str) -> float:
    """An English cardinal: 'six', 'twelve'."""
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
    """'5,000,000', '924.8', '.5'."""
    return float(s.replace(",", ""))


def read(word: str, how: str) -> list[float]:
    if how == "num":
        return [figure(word)]
    if how == "en":
        return [cardinal(word)]
    if how == "nth":
        return [float(NTH[word.lower()])]
    if how == "times":
        return [float(TIMES[word.lower()])]
    if how == "half":                          # 'half the total'
        return [0.5]
    if how == "sd":                            # '1s.2d.': shillings and pence
        m = re.fullmatch(r"(\d+)s\.(\d+)d\.", word)
        return [float(m.group(1)), float(m.group(2))]
    if how == "dmy":                           # the German date '17.3.1933'
        return [float(x) for x in word.split(".")]
    if how == "comma":                         # '2,5': a decimal comma
        return [float(word.replace(",", "."))]
    if how == "ocr":
        return [float(OCR[word])]
    raise ValueError(how)


FIGURES = re.compile(r"\d[\d,]*(?:\.\d+)?|\.\d+")
EN, NUM = "en", "num"
# id -> [(phrase, how)], in order. A phrase 'context|word' is searched as a whole and read from `word`. Rows not
# listed are read with all the figures of the quotation.
READINGS = {
    "sz_dec13": [("13", NUM), ("1931", NUM), ("fifth", "nth")],
    "sz_four": [("four", EN), ("1936", NUM)],
    "sz_twice": [("twice", "times")],
    "sz_chatitle": [("[|2003", NUM), ("History |63", NUM), ("-|1", NUM), ("pp.|127", NUM), ("-|44", NUM)],
    "ide_tax": [("1936", NUM), ("924.8", NUM), ("half", "half")],
    "ide_t1_1933": [("2,011,600 |788,600", NUM)],
    "ide_t1_1934": [("1,410,900 |900,400", NUM)],
    "ide_t1_1935": [("1,416,000 |654,800", NUM)],
    "imt_schacht": [("March |17", NUM), (",|1933", NUM), ("1934", NUM), ("1935", NUM)],
    "imt_jan30": [("January |30", NUM), (",|1933", NUM)],
    "imt_resigned": [("November |16", NUM), (",|1937", NUM)],
    "imt_sauckel": [("March |1", NUM), (",|1944", NUM), ("5,000,000", NUM), ("200,000", NUM)],
    "nca2_capital": [("only |one", EN)],
    "nca2_six": [("six", EN), ("three", EN)],
    "nca2_rediscount": [("three", EN)],
    "nca2_100m": [("100", NUM), ("1924", NUM), (", |11", "ocr"), ("241", NUM)],
    "nca2_three": [("three", EN)],
    "puhl_life": [("six", EN), ("three", EN), ("four", EN)],
    "puhl_discount": [("three", EN)],
    "puhl_12": [("1938", NUM), ("twelve", EN)],
    "ec369_date": [("7", NUM), ("Jan.|1939", NUM)],
    "ec369_two": [("two", EN), ("requirements: |1", NUM), ("m a r k e t |2", NUM)],
    "bis_yen": [("four", EN), ("1s.2d.", "sd")],
    "bis_jan1937": [("1937", NUM), ("1s.2d.", "sd")],
    "ndb_17": [("17.3.1933", "dmy")],
    "ndb_minister": [("30.6.1934", "dmy")],
    "ndb_dismiss": [("26.11.1937", "dmy"), ("20.1.1939", "dmy")],
    "bj98_rate": [("six", EN), ("eight", EN)],
    "bj98_25": [("2,5", "comma"), ("1934", NUM)],
    "bj98_rooth": [("8", NUM), ("1931", NUM), ("three", EN)],
    "bj98_nov1931": [("1931", NUM), ("three", EN)],
    "rb_reserve": [("300", NUM), ("30", NUM), ("three", EN)],
}
# the misreadings of the OCR (and of the sources), each named in the note of its row and printed in the quotation
MISPRINTS = [("imt_backed", "nioney"), ("imt_oct1936", "mas"), ("imt_march31", "Schaclit"), ("imt_war", "consistellt"),
             ("imt_poland", "cgainst"), ("imt_daf", "worlrers"), ("imt_nurnberg", "tlie"), ("imt_unions", "a n"),
             ("imt_plunder", "t o"), ("imt_autumn1938", "i t"), ("nca2_rediscount", "a t"),
             ("nca2_100m", "Reichsgesetxblatt"), ("nca2_newplan", "Reichsgesetxblatt"), ("puhl_secrecy", "a s"),
             ("ec369_camouflage", "a t"), ("ec369_two", "o n"), ("ec369_6and6", "Millarden"), ("ec369_lagged", "o f"),
             ("ec369_currency", "O n"), ("ec369_full", "o f"), ("bj98_reflation", "preceeding"),
             ("sz_december", "Cabinet20")]
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
    quoted("rows with values, each read from its quotation", n, 163)
    quoted("rows read on a page image (no quotation)", img, 26)
    N, Q = column("note"), quotes()
    for rid, word in MISPRINTS:
        assert word in N[rid], (rid, word)                  # every misreading is named in the note
        assert word in Q[rid], (rid, word)                  # and printed in the quotation
    assert "'11' for II" in N["nca2_100m"] and "a decimal comma" in column("juan")["bj98_25"] + N["bj98_25"]


# ---------------------------------------------------------------------------------------------------
# 2. Every “…” of the text against the snapshot
# the chapter's Chinese renderings of the quotations: rendering -> row (or rows)
TRANSLATIONS = {
    # opening
    "金输出再禁止": "bh_1931",
    "急剧的通缩与经济活动的严重收缩": "sz_showa",
    "很快也会被迫跟着走": "sz_uk",
    "被军国主义者暗杀": "sz_four",
    # sec:alternatives-world
    "大概是所有大国里最严重的": "bjm_unemp",
    "满洲事变": "ndlc_mukden",
    "扩大创造就业的政策，并立即着手重整军备": "ndb_expansive",
    "协调行动": "imt_unions",
    "从殴打直到谋杀": "imt_murder",
    "自由": "bj98_free",
    "预算平衡的原则": "es_balanced",
    "作用类似于明确的贬值": "es_controls",
    # sec:alternatives-japan
    "宽松的货币政策": "sz_cuts",
    "高桥时期刺激性财政政策的全面开始": "sz_june18",
    "相信它能通过卖出承购的国债来控制货币": "ide_confident",
    "未必直接导致通货发行的扩张": "ide_hijikata",
    "实际上把日元钉住了英镑": "sz_peg",
    "仍是温和的": "sz_mild",
    "不利于日本": "bis_terms",
    "会特别危险": "bis_rising",
    "一举三得的妙手": "bj_sanchou",
    "一时的权宜之计": ("bj_benpou", "bj_oshikira"),
    "意味相当不同": "bj_omo",
    "即使承购的国债全部卖掉，中间这段时间也是放松银根的原因。卖不掉的那部分，相应的资金就留在市场上。": "bj_middle",
    "追认经济扩张的事后措施": "bj_tsuinin",
    "本行百年历史上最大的失败": "bj_failure",
    "最大的因素": "bj_military",
    "公债发行的限度，是国民消化公债的能力": "bj_tk1934",
    "推迟未来的财政负担，特别是军费的负担": "ide_postpone",
    "增加到了巨大的规模": "ide_hidden",
    "悲剧性的落幕": "bj_1935",
    # sec:alternatives-germany
    "其他一切都必须服从这个目标": "nca2_memo",
    "只是一个空壳组织": "nca2_capital",
    "这一条来自国家对票据的担保": "puhl_guarantee",
    "借一个托词": "nca2_subterfuge",
    "严守的国家机密": "nca2_secret",
    "立即、白手起家，而且在伪装之下": "ec369_camouflage",
    "引起流通中货币的通胀式增加": "ec369_present",
    "已经不存在了": "ec369_gold",
    "几乎翻了一番": "ec369_doubled",
    "尽可能地": "nca2_dedicated",
    "我们的军备，因此有一部分是用我们政治对手的资产来筹资的。": "nca2_opponents",
    "自主的价格机制": "nca2_price",
    "整个经济处于战争准备状态": "imt_oct1936",
    "实际上没有任何担保": "imt_backed",
    "现在付不出来": "ec369_3bn",
    "只能以战争为目的": "imt_war",
    "再军备本身并不是犯罪": "imt_notcrime",
    "最明白不过的侵略战争": "imt_poland",
    "自愿来的连 20 万都不到": "imt_sauckel",
    "把犹太人完全排除出德国生活": "imt_autumn1938",
    # sec:alternatives-repressed
    "不只管生活费用，还要监督全国的整个价格结构": "bis_price",
    "用次等材料代替而变相涨价": "bis_inferior",
    "完全散了架": "ec369_apart",
    "从前能穿好几年的童装、工装，现在只能穿几个月，价钱却和从前的好货一样，甚至更贵。": "ec369_clothes",
    "在政府通胀式的支出政策面前，没有哪家发行银行能维持币值。": "ec369_nobank",
    # sec:alternatives-sweden
    "用一切可用的手段": "bj98_means",
    "通胀与通缩都要对付": "rb_both",
    "国家银行的第一个消费物价指数": "rb_hamm_cpi",
    "其他物价指数也要考虑": "bj98_other",
    "要像通胀一样坚决地抵制": "bj98_resist",
    "太远的": "bj98_distant",
    "看作暂时的": "bj98_temporary",
    "出于对通胀的担心": "bj98_rate",
    "并不认为这违反稳定物价的目标": "rb_1933",
    "1931 年以来相对稳定": "bj98_1937",
    "批评了国家银行的政策": "bj98_wig1933",
    "再通胀政策": "bj98_reflation",
    "基数漂移": "bj98_drift",
    # sec:alternatives-newdeal
    "靠提高农业的购买力，缓解当前的国家经济紧急状态": "aaa_title",
    "公平竞争法规": "nira_codes",
    "通过自己选择的代表集体谈判": "nira_7a",
    "组织、参加或帮助工会": "nlra_7",
    "性质不同": "bj_newdeal",
    # sec:alternatives-debate
    "在许多方面很特殊": "es_special",
    "社会倾销、通货膨胀与经济的军事化": "bj_two",
    "所谓凯恩斯式政策取得成功的例子": "bj_two",
    "凯恩斯经济学的成功先驱": "sz_keynesian",
    "日本的凯恩斯": "sz_smethurst",
    "在多大程度上真把稳定物价当作首要目标": "bj98_question",
    "致命的通缩螺旋在瑞典避免了。": "bj98_ohlin",
    "前凯恩斯的世界": "bj98_prekeynes",
    # the 史料说明
    "托词": "nca2_subterfuge",
    "5-year notes": "imt_fiveyear",
    "a n": "imt_unions",
    "o f": "ec369_lagged",
    "nioney": "imt_backed",
    "Schaclit": "imt_march31",
    "consistellt": "imt_war",
    "Reichsgesetxblatt": "nca2_100m",
    "Milliarden": "ec369_6and6",
    "Millarden": "ec369_6and6",
    # sec:alternatives-legacy
    "一直在为政府提供资金": "ide_ww2",
    "最终丧失了财政纪律": "sz_discipline",
}
# the words of the source that each rendering renders (for a row read on a page image: of its transcription)
KEYWORDS = {
    "bh_1931": ["金輸出再禁止"],
    "sz_showa": ["abrupt deflation and a severe contraction of economic activities"],
    "sz_uk": ["Japan would also be forced to follow suit soon"],
    "sz_four": ["assassinated by militarists"],
    "bjm_unemp": ["probably the worst unemployment problem of any major country"],
    "ndlc_mukden": ["満洲事変"],
    "ndb_expansive": ["eine Ausweitung der Arbeitsbeschaffungspolitik sowie die sofortige Inangriffnahme der "
                      "Aufrüstung"],
    "imt_unions": ['"coordination action"', "Ley issued a n NSDAP directive"],
    "imt_murder": ["ranging from assault and battery to murder"],
    "bj98_free": ['a "free" standard'],
    "es_balanced": ["the principle of balanced budgets"],
    "es_controls": ["effects were analogous to an explicit depreciation"],
    "sz_cuts": ["an accommodative monetary policy"],
    "sz_june18": ["a full-fledged start of the stimulative fiscal policy of the Takahashi era"],
    "ide_confident": ["the BOJ was confident it could exert monetary control through the market operation of selling "
                      "underwritten government bonds"],
    "ide_hijikata": ["BOJ underwriting of government bonds need not lead directly to the expansion of a currency "
                     "issue"],
    "sz_peg": ["effectively pegging the yen to sterling"],
    "sz_discipline": ["resulted in an eventual loss of fiscal discipline"],
    "sz_mild": ["remained mild through 1936"],
    "bis_terms": ["has been unfavourable to Japan"],
    "bis_rising": ["would render a further devaluation of the yen particularly dangerous"],
    "bj_sanchou": ["一石三鳥の妙手"],
    "bj_benpou": ["一時の便法"],
    "bj_oshikira": ["一時の便法"],
    "bj_omo": ["かなり異なったニュアンスを持っていた"],
    "bj_middle": ["引受国債の全部が売れても中間に於ては金融緩和の原因となる。", "売れない部分に相当する資金は市場に残る。"],
    "bj_tsuinin": ["経済拡大を追認した事後的措置"],
    "bj_failure": ["本行百年の歴史における最大の失敗"],
    "bj_military": ["軍事費の増大が最大の要因"],
    "bj_tk1934": ["公債発行の限度といふのは、国民が公債を咀嚼する力である。"],
    "ide_postpone": ["postpone future fiscal burdens, especially those for military spending"],
    "ide_hidden": ["long-term government debt increased to an enormous level"],
    "bj_1935": ["悲劇的幕切れ"],
    "nca2_memo": ["everything else must be subordinated to this aim"],
    "nca2_capital": ["This company was merely a dummy organization"],
    "puhl_guarantee": ["(This provision results from a guarantee of the bill by the Reich.)"],
    "nca2_subterfuge": ["to lend by a subterfuge to the Government"],
    "nca2_secret": ["a guarded state secret"],
    "ec369_camouflage": ["a t once, out of nothing and furthermore under camouflage"],
    "ec369_present": ["will cause an inflationary increase of money in circulation"],
    "ec369_gold": ["are no more in existence"],
    "ec369_doubled": ["almost doubled"],
    "nca2_dedicated": ['"as far as possible"'],
    "nca2_opponents": ["Our armaments are, therefore, being financed partially with the assets of our political "
                       "opponents."],
    "nca2_price": ["the autonomous price mechanism"],
    "imt_oct1936": ['"the entire economy in a state of readiness for war"'],
    "imt_backed": ["backed, in effect, by nothing more than its position as a bank of issue",
                   "the short-term nioney market"],
    "ec369_3bn": ["cannot now be paid"],
    "imt_war": ["consistellt only with war as its object"],
    "imt_notcrime": ["rearmament of itself is not criminal"],
    "imt_poland": ["was most plainly an aggressive war"],
    "imt_sauckel": ["not even 200,000 came voluntarily"],
    "imt_autumn1938": ["the complete exclusion of Jews from German life"],
    "bis_price": ["not only of controlling costs of living but of supervising the whole national price structure"],
    "bis_inferior": ["any indirect increase in prices by the substitution of inferior materials"],
    "ec369_apart": ["wage- and price structure totally fell apart."],
    "ec369_clothes": ["Children clothes, workers clothes etc., which formerly lasted for years last now only months, "
                      "but cost the same or even more than the former good merchandise."],
    "ec369_nobank": ["N o note-issuing bank i s capable o f maintaining the currency standard against a n "
                     "inflationary policy o f expenditures b y t h e government."],
    "bj98_means": ['"using all means available"'],
    "rb_both": ["Both inflation and deflation would be combated."],
    "rb_hamm_cpi": ["the bank's first consumer price index"],
    "bj98_other": ['"other price indices besides the Riksbank\'s own index of consumer prices will also be taken into '
                   'consideration."'],
    "bj98_resist": ["should be resisted just as strongly as the inflation"],
    "bj98_distant": ['a "too distant" price level'],
    "bj98_temporary": ["initially viewed as a temporary one"],
    "bj98_rate": ["out of fear of inflation"],
    "rb_1933": ["not then considered to be in contravention of the price stability target"],
    "bj98_1937": ["relatively stable since 1931"],
    "bj98_wig1933": ["He was critical of the policy of the Riksbank."],
    "bj98_reflation": ['the "reflation policy"'],
    "bj98_drift": ['"base drift"'],
    "aaa_title": ["To relieve the existing national economic emergency by increasing agricultural purchasing power"],
    "nira_codes": ["a code or codes of fair competition"],
    "nira_7a": ["bargain collectively through representatives of their own choosing"],
    "nlra_7": ["to form, join, or assist labor organizations"],
    "bj_newdeal": ["その性格を異にするものであった"],
    "es_special": ["is in many ways special"],
    "bj_two": ["ソーシャル・ダンピングとインフレーションと経済の軍事化", "いわゆるケインズ的政策が成功を収めた例"],
    "sz_keynesian": ["a successful pioneer of Keynesian economics"],
    "sz_smethurst": ["Japan’s Keynes"],
    "bj98_question": ["to what extent the Riksbank was actually accepting price stabilization as the primary goal"],
    "bj98_ohlin": ['"The fatal spiral of deflation was avoided in Sweden."'],
    "bj98_prekeynes": ["a pre-Keynesian world"],
    "imt_fiveyear": ["5-year notes"],
    "ec369_lagged": ["the problem arose o f increased total wages"],
    "imt_march31": ["Schaclit discontinued the practice"],
    "nca2_100m": ["(Reichsgesetxblatt, 1924, 11, p. 241)"],
    "ec369_6and6": ["RM 6 Milliarden Mefo-acceptances", "RM 6 Millarden which"],
    "ide_ww2": ["the BOJ continued to provide money for the government"],
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
                assert q in quotes()[rid], (q, rid)
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
# and the subscripts of the math
MASKS = [re.compile(r"\\begin\{keyeq\}.*?\\end\{keyeq\}", re.DOTALL),
         re.compile(r"\\(?:label|cite|chref|secref|figref|tabref|exref|eqref|ref|nameref|url|fig)\{[^}]*\}"),
         re.compile(r"_\{[^}]*\}|_\d")]
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
    """A Chinese numeral of the text: '五', '十', '六成', '九成', '三分之一', '一半'."""
    if "分之" in s:
        b, a = s.split("分之")
        return zh(a) / zh(b)
    if s.endswith("成"):                               # 六成 = six tenths
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


# ---------------------------------------------------------------------------------------------------
# 4. Numbers, section by section
def guide(F, Y, Q):
    t = TEX.read_text(encoding="utf-8")
    assert f"\\guidequestion{{{GUIDE}}}" in t and GUIDE == PREV
    ch29 = (ROOT / "zh" / "ch29_depressionworld.tex").read_text(encoding="utf-8")
    assert ch29.rstrip().endswith(PREV) or PREV in ch29                         # 第 29 章交来的问题
    G = goldexits()
    exits = [ym(G.loc["Germany"].exchange_control), ym(G.loc["Japan"].suspension), ym(G.loc["Sweden"].suspension)]
    assert all(1930 <= y <= 1939 for y, _ in exits)
    said("\\chapter{1930 年代的另类出路", 1930)
    say("用 MEFO 票据为再军备融资、用外汇管制与物价管制压住公开通胀的机制")
    said("分析日本 1931 年脱离金本位与日本银行承购国债的效果", exits[1][0])
    said("解释瑞典 1931 年后的价格水平目标", exits[2][0])


def opening(F, Y, Q):
    d, y, fifth = F["sz_dec13"]
    assert date(int(y), 12, int(d)).weekday() == 6 and "On December 13, 1931" in Q["sz_dec13"]      # 星期日
    said("1931 年 12 月 13 日是星期日", y, 12, d)
    chk("    the fifth time (第五次)", fifth, told("第五次出任大藏大臣", "第", "次"))
    assert "on the day of his return to office" in Q["sz_embargo"]
    say("上任当天，高桥就下令禁止黄金出口")
    assert F["bh_1931"] == [y, 6, 12] and Q["bh_1931"].startswith("1931（昭和6）年12月")
    showa, yl, ml, dl = F["ndlc_1930"]
    assert yl == 1925 + showa and F["sz_lifted"][0] == yl and "January 1930" in Q["sz_lifted"]
    said("上一次解禁是在 1930 年 1 月 11 日", yl, ml, dl)
    assert "the return to the Gold Standard at the old parity" in Q["sz_oldparity"]
    said("一日元约合 49.8 美分", F["sz_parity"][0])
    said("照 Shizume（2009）的说法，接下来的两年", Y["sz_mechanism"])
    a, b = F["sz_showa"]
    chk("    two years (两年): 1930 and 1931", b - a + 1, told("接下来的两年是", "接下来的", "年"))
    said("1931 年 9 月英国离开金本位", F["sz_uk"][0], mon("sz_uk", "September"))
    said("日本银行在 10 月与 11 月两次提高贴现率", mon("sz_twice", "October"), mon("sz_twice", "November"))
    chk("    twice (两次)", F["sz_twice"][0], told("两次提高贴现率", "", "次"))
    said("一直到 12 月民政党的内阁倒台", mon("sz_december", "December"))
    yb, showa, mb = F["bh_1932"]
    assert yb == 1925 + showa and "管理通貨制に移行" in Q["bh_1932"]
    said("1932 年 1 月，停止金币兑换的紧急敕令施行", yb, mb)
    usd, gbp, y0, y1 = F["sz_60"]
    assert "from December 1931 to November 1932" in Q["sz_60"]
    said("从 1931 年 12 月到 1932 年 11 月，日元对美元贬值了 60\\%，对英镑贬值了 44\\%", y0, 12, y1, 11, usd, gbp)
    assert Q["sz_20c"].startswith("November 1932")
    said("到 1932 年 11 月，一日元只值 20 美分", F["sz_20c"][0], 11, F["sz_20c"][1])
    four, yd = F["sz_four"]
    chk("    four years (四年)", four, told("此后的四年里", "此后的", "年"))
    said("直到 1936 年 2 月“被军国主义者暗杀”", yd, mon("sz_four", "February"))
    G = goldexits()
    de, se, jp = G.loc["Germany"], G.loc["Sweden"], G.loc["Japan"]
    assert not isinstance(de.devaluation, str) and not isinstance(de.suspension, str)   # 平价没有改
    assert ym(jp.suspension) == (1931, 12)
    said("德国 1931 年 7 月实行外汇管制，帝国马克的平价没有改；瑞典 1931 年 9 月离开了金本位", *ym(de.exchange_control),
         *ym(se.suspension))
    R = ratios()
    said("到 1935 年，德国、日本与瑞典的人均 GDP 已是 1929 年的 101.7\\%、104.4\\% 与 110.6\\%", 1935, 1929,
         R.loc["DEU", 1935], R.loc["JPN", 1935], R.loc["SWE", 1935])
    said("同一年美国只有 81.0\\%", R.loc["USA", 1935])
    t = tex_text()
    para = t[t.index("同一年美国只有 81.0"):].split("\n")[0]
    assert para.endswith(GUIDE)                                                 # the opening ends with the question


def world(F, Y, Q):
    R = ratios()
    said("1932 年，德国的人均 GDP 只有 1929 年的 83.0\\%，美国更低，只有 70.1\\%", 1932, 1929, R.loc["DEU", 1932],
         R.loc["USA", 1932])
    said("照 Bernanke 与 James（1991）的说法", Y["bjm_unemp"])
    J, S = R.loc["JPN"], R.loc["SWE"]
    assert J.idxmin() == 1931 and S.idxmin() == 1932
    assert S.min() > max(R.loc[c].min() for c in SIX if c != "SWE")              # 瑞典跌得最少
    said("日本的谷底在 1931 年，是 90.6\\%", 1931, J[1931])
    said("瑞典跌得最少，1932 年还有 97.7\\%", 1932, S[1932])
    chk("    six economies (六个国家)", len(SIX), told("把六个国家画在一起", "把", "个国家"))
    mm = maddison_meta()
    said("人均 GDP，1929 年$=100$，1929—1938 年", 1929, 100, int(R.columns[0]), int(R.columns[-1]))
    said("数据：Maddison 项目数据库 2023 年版（Bolt 与 van Zanden 2024）",
         int(re.search(r"version (\d{4})", mm["source"]).group(1)), citation_year(mm["citation"]))
    showa, y, m, d = F["ndlc_mukden"]
    assert y == 1925 + showa
    said("1931 年 9 月 18 日，柳条湖事件发生", y, m, d)
    s7, y32, m3, d1, m5, d15, mark = F["ndlc_1932"]
    s8, y33, m3b, d27 = F["ndlc_league"]
    assert y32 == 1925 + s7 and y33 == 1925 + s8 and "満洲国建国宣言" in Q["ndlc_1932"]
    said("1932 年 3 月 1 日，伪满洲国宣布成立；1933 年 3 月 27 日，日本通告退出国际联盟", y32, m3, d1, y33, m3b, d27)
    by, bm, bd, dy, dm, dd = F["ndl_in_life"]
    assert "血盟団事件で暗殺" in Q["ndl_in_bio"]
    said("1932 年 2 月 9 日，井上准之助在血盟团事件中被暗杀", dy, dm, dd)
    assert F["ndl_ik_life"][3:] == [y32, m5, d15] and mark == 5.15 and "5・15事件で暗殺" in Q["ndl_ik_bio"]
    said("5 月 15 日，犬养毅在五一五事件中被暗杀", m5, d15)
    say("5 月 15 日，犬养毅在五一五事件中被暗杀")                                   # 五一五 = 5.15
    d30, y = F["imt_jan30"]
    said("1933 年 1 月 30 日，纳粹党上台", y, mon("imt_jan30", "January"), d30)
    d17 = F["imt_schacht"][0]
    assert F["ndb_17"] == [d17, 3, y] and mon("imt_schacht", "March") == 3
    said("3 月 17 日，他重新出任帝国银行行长", 3, d17)
    ch26 = (ROOT / "zh" / "ch26_weimar.tex").read_text(encoding="utf-8")
    k = ch26.index("12 月 22 日，沙赫特接替去世的哈芬施坦，出任帝国银行行长")
    y23, m23 = [int(x) for x in re.findall(r"(\d{4}) 年 (\d+) 月", ch26[:k])[-1]]
    said("他第一次当行长是在 1923 年 12 月", y23, m23)
    said("1933 年 4 月 1 日，纳粹的内阁批准抵制犹太人的企业", F["imt_boycott"][1], mon("imt_boycott", "April"),
         F["imt_boycott"][0])
    d21, y, d2 = F["imt_unions"]
    assert "the 21st April 1933" in Q["imt_unions"] and "the 2nd May" in Q["imt_unions"]
    said("4 月 21 日，纳粹党发出指示，要在 5 月 2 日对自由工会采取“协调行动”", 4, d21, 5, d2)
    said("1935 年的纽伦堡法剥夺了犹太人的德国国籍", F["imt_nurnberg"][0])
    y, d27, y2 = F["bj98_free"]
    assert y == y2 and "September 27th, 1931" in Q["bj98_free"]
    said("1931 年 9 月 27 日，财政大臣哈姆林", y, mon("bj98_free", "September"), d27)
    said("1932 年，社会民主党政府上台", F["bj98_wigforss"][0])
    said("照 Eichengreen 与 Sachs（1984）的概括", Y["es_controls"])
    said("英国 1931 年以后的低利率", F["es_central"][0])


def japan(F, Y, Q):
    assert "March, June, and August 1932" in Q["sz_cuts"]
    said("1932 年 3 月、6 月与 8 月，日本银行三次降低贴现率", F["sz_cuts"][0], 3, 6, 8)
    chk("    three cuts (三次)", 3, told("日本银行三次降低贴现率", "日本银行", "次"))
    said("6 月，银行券发行的规则也改了", mon("sz_fiduciary", "June"))
    a, b = F["sz_fiduciary"]
    assert "from 120 million yen to 1 billion yen" in Q["sz_fiduciary"]
    said("它的限额从 1.2 亿日元提高到 10 亿日元", a * M6, b * B9)
    d8, y = F["sz_march8"]
    said("1932 年 3 月 8 日，高桥在一次与金融界人士的会上", y, mon("sz_march8", "March"), d8)
    said("6 月 3 日，政府向议会提出发行赤字公债的法案", mon("sz_june3", "June"), F["sz_june3"][0])
    assert "on the same day" in Q["sz_announce"]
    said("法案与预算 6 月 18 日通过", mon("sz_june18", "June"), F["sz_june18"][0])
    d25, y = F["sz_nov25"]
    assert F["ide_nov25"] == [d25, y]
    said("1932 年 11 月 25 日，日本银行开始直接承购新发的赤字公债", y, mon("sz_nov25", "November"), d25)
    m11, m12 = F["bh_nov"]
    assert "対市中売却開始" in Q["bh_nov"]
    said("12 月，它开始把承购的国债卖给市场", m12)
    said("照 Ide（2003）的说法，日本银行“相信", Y["ide_confident"])
    said("1932 年 10 月，日本银行的总裁说过", F["ide_hijikata"][0], mon("ide_hijikata", "October"))
    said("从 1933 年 4 月起，日本的官方外汇银行横滨正金银行以英镑报价", F["sz_peg"][0], mon("sz_peg", "April"))
    four, s, d = F["bis_yen"]
    said("按国际清算银行 1937 年的年报，此后四年，日元一直维持在 1 先令 2 便士", Y["bis_yen"], s, d)
    chk("    four years (此后四年)", four, told("此后四年，日元", "此后", "年"))
    said("一英镑合 20 先令，一先令合 12 便士。1 先令 2 便士就是 14 便士", 20, 12, s, d, 12 * s + d)
    assert "1s. 2d. = 14 pence a yen" in column("note")["bis_yen"]
    said("按旧平价，一日元约合 24.6 便士，这是本书用两国对美元的平价换算的", 240 * F["sz_parity"][0] / pound_parity())
    ya, yb = F["sz_controls"]
    said("日本 1932 年 7 月有了《资本逃避防止法》，1933 年 5 月有了《外汇管理法》", ya, mon("sz_controls", "July"), yb,
         mon("sz_controls", "May"))
    assert F["bh_1933"] == [yb, 8, 5] and "外国為替管理法" in Q["bh_1933"]
    y0, y1, g, p = F["sz_gnp"]
    said("1932—1936 年，实际 GNP 平均每年增长 6.1\\%，GNP 平减指数每年只涨 1.5\\%", y0, 1900 + y1, g, p)
    yb, x = F["bis_terms"]
    said("1931 年离开金本位以后，对外贸易的价格“不利于日本”，出口的平均价格涨了约 50\\%", yb, x)
    assert "the prices of imports have more than doubled" in Q["bis_terms"]
    say("进口价格却涨了一倍多")
    y37, s2, d2 = F["bis_jan1937"]
    assert (s2, d2) == (s, d)
    said("1937 年 1 月，1 先令 2 便士的汇率得到官方承认", y37, mon("bis_jan1937", "January"), s2, d2)
    # fig:alternatives_japan
    Ym = yen_monthly()
    ym_meta = _table("alternatives_yen_monthly")[1]
    assert "From April 1933 the dollar was off gold" in ym_meta["notes"] and "49.845 cents" in ym_meta["notes"]
    said("(a) 一日元合多少美分，月平均，1929—1938 年；虚线是金平价，约 49.8 美分。1933 年 4 月以后美元自己也离开了黄金",
         Ym.index[0][0], Ym.index[-1][0], F["sz_parity"][0], 1933, 4)
    H, _ = boj_sales()
    first, last = ym(H["first"].iloc[0]), ym(H["last"].iloc[-1])
    said("(b) 日本银行承购的长期国债与它卖给市场的国债，每半年，亿日元，1932 年 11 月至 1936 年 12 月", *first, *last)
    a0, a1 = ym(H["first"].iloc[0]), ym(H["last"].iloc[0])
    chk("    the first period has two months (两个月)", a1[1] - a0[1] + 1, told("第一栏只有两个月", "只有", "个月"))
    bm = _table("alternatives_boj_sales")[1]
    vol = int(re.search(r"vol\. (\d+)", bm["source"]).group(1))
    t1, t2 = [int(x) for x in re.search(r"Table (\d+)-(\d+)", bm["citation"]).groups()]
    said("数据：联邦储备委员会《银行与货币统计 1914—1941》表 173；日本银行《日本银行百年史》第 4 卷（1984）表 1-17", 1914, 1941,
         int(re.search(r"Table (\d+)", ym_meta["citation"]).group(1)), vol, citation_year(bm["citation"]), t1, t2)
    assert "Source: Bank of Japan." in bm["license"]
    say("来源：日本银行。}{fig:alternatives_japan}")


def casebox(F, Y, Q):
    H, T = boj_sales()
    N = column("note")
    said("\\begin{case}{日本 · 1932—1936 · 日本银行承购国债}", ym(H["first"].iloc[0])[0], ym(H["last"].iloc[-1])[0])
    said("1932 年 11 月发行的四分半利国库债券", Y["bj_nov1932"], F["bj_nov1932"][0])
    rate = float(re.search(r"\((\d\.\d)% bonds", N["bj_nov1932"]).group(1))
    assert "四分半利" in transcription("bj_nov1932")
    said("四分半利，就是 4.5\\% 的年利率", rate)
    yb = citation_year(_table("alternatives_boj_sales")[1]["citation"])
    _, s12, m8 = F["bj_nov1932"]
    assert "昭和12年8月の1回分" in transcription("bj_nov1932") and "本行・預金部等の引受け" in transcription("bj_nov1932")
    assert "圧倒的な大きさ" in transcription("bj_nov1932")                     # 占了压倒性的比重
    said("按日本银行 1984 年的行史，此后新发的国债，除了 1937 年 8 月的一次", yb, 1925 + s12, m8)
    assert "高橋蔵相のイニシアチブ" in transcription("bj_initiative") and "思われる" in transcription("bj_oshikira")
    say("承购是高桥主动提出的", "行史推测，日本银行最后是被高桥的强力要求压倒")
    assert "persuaded" in Q["ide_expedient"] and "willingly accepted" in Q["ide_influence"]
    say("照 Ide 的研究，这种通行的说法站不住")
    assert "governor from 1935" in N["bj_sanchou"] and "then vice-governor" in N["bj_fukai_sell"]
    said("当时是副总裁，1935 年起任总裁", 1935)
    u, s = T.underwritten_kyen * 1000, T.sold_kyen * 1000
    said("1933—1935 年，日本银行承购了约 25.7 亿日元，卖出约 23.4 亿日元，卖出的占 91.3\\%", 1933, 1935, u, s, T.sold_pct)
    chk("    the printed B/A of 1933-1935 = B/A computed", 100 * s / u, T.sold_pct, tol=0.05)
    showa8, showa10, three, nine = F["bj_90"]
    assert (1925 + showa8, 1925 + showa10, three) == (1933, 1935, 3)
    chk("    nine tenths (九成)", nine / 10, told("卖出超过了承购的九成", "承购的"))
    assert s / u > nine / 10
    u36, s36 = year_sum(H, 1936, "underwritten_kyen") * 1000, year_sum(H, 1936, "sold_kyen") * 1000
    said("1936 年卖不动了", 1936)
    said("这一年日本银行承购约 15.8 亿日元，只卖出约 6.9 亿，卖出的占 43.4\\%", u36, s36, 100 * s36 / u36)
    assert "昭和7年秋に本行が国債の本行引受け方式の実施に同意したこと" in transcription("bj_failure")
    said("1932 年秋天同意承购，是日本银行失去中央银行职能的第一步", 1925 + F["bj_failure"][0])


def ex_underwrite(F, Y, Q):
    d, s = UW["deficit"], UW["sold"]
    H, T = boj_sales()
    u, so = T.underwritten_kyen * 1000, T.sold_kyen * 1000
    u36, s36 = year_sum(H, 1936, "underwritten_kyen") * 1000, year_sum(H, 1936, "sold_kyen") * 1000
    said("政府一年的赤字是 100，全部发行国债，由中央银行承购。中央银行再把其中的 90 卖给银行", d, s)
    said("（1）按式~\\eqref{eq:intro-budget}，赤字由哪两项来付？基础货币增加多少？（2）若中央银行一张也卖不出去，基础货币增加"
         "多少？（3）1933—1935 年，日本银行承购约 25.7 亿日元，卖出约 23.4 亿日元", 1, 2, 3, 1933, 1935, u, so)
    said("按（1）的算法，留在日本银行的约有多少？1936 年承购约 15.8 亿，卖出约 6.9 亿呢？", 1, 1936, u36, s36)
    said("（1）式里的$B$只算中央银行以外的人持有的国债。卖给银行的 90 是$\\Delta B=90$，留在中央银行的 10 变成$\\Delta H=10$，"
         "$100=90+10$", 1, s, s, d - s, d - s, d, s, d - s)
    said("（2）$\\Delta B=0$，$\\Delta H=100$，赤字全部变成基础货币", 2, 0, d)
    said("（3）1933—1935 年两者相差约 2.2 亿日元，只占承购额的 8.7\\%。1936 年相差约 9.0 亿日元，占 56.6\\%", 3, 1933, 1935,
         u - so, 100 * (u - so) / u, 1936, u36 - s36, 100 * (u36 - s36) / u36)


def military(F, Y, Q):
    yb = citation_year(_table("alternatives_boj_sales")[1]["citation"])
    said("照日本银行 1984 年的行史，支出里也有救济农村的时局匡救费", yb)
    showa, y, m = F["bj_tk1934"]
    assert y == 1925 + showa
    said("1934 年 4 月，高桥说，赤字公债年年增加不是好事", y, m)
    said("1936 年度的预算，大藏省在高桥的主持下想减少赤字", F["sz_fy1936"][0])
    said("国债的发行因此少了 9,100 万日元", F["ide_zengen"][0] * M6)
    tot, y1, bud, y2 = F["ide_total"]
    assert y1 == y2
    said("1936 年度的继续费总额约 14.3 亿日元，同年度的预算总额约 22.8 亿日元", y1, tot * M6, bud * M6)
    _, tax, half = F["ide_tax"]
    said("相当于这一年预计税收约 9.2 亿日元的一半", tax * M6)
    chk("    half (一半)", half, told("预计税收约 9.2 亿日元的一半", "的"))
    p70, y70 = F["ide_70"]
    said("1936 年度以后，陆海军两省约占全部继续费的 70\\%", y70, p70)
    showa10, showa11, m2, d26 = F["bj_1935"]
    said("1935 年，高桥与强行要求扩充军备的军部尖锐对立", 1925 + showa10)
    d, y = F["sz_feb26"]
    assert F["ndlc_226"][1:4] == [y, 2, d] and 1925 + showa11 == y and (m2, d26) == (2, d)
    assert F["ndl_tk_life"][3:] == [y, 2, d] and mon("sz_feb26", "February") == 2
    said("1936 年 2 月 26 日，一群军人发动政变未遂", y, 2, d)
    m, d = F["ndlc_1937"]
    assert F["sz_war"][0] == 1937 and "In July 1937" in Q["sz_war"] and m == 7
    said("1937 年 7 月 7 日，卢沟桥事变发生", F["sz_war"][0], m, d)
    y0, y1, _, g = F["sz_gnp37"]
    said("1937—1940 年，GNP 平减指数平均每年涨 11.9\\%", y0, 1900 + y1, g)


def germany(F, Y, Q):
    d, y = F["nca2_memodate"]
    said("1935 年 5 月 3 日，沙赫特给希特勒写了一份关于军备筹资的备忘录", y, mon("nca2_memodate", "May"), d)
    assert "In the early part of 1935" in Q["puhl_1935"]
    said("战后作证说，1935 年初", F["puhl_1935"][0])
    said("名义资本只有 100 万帝国马克", F["nca2_capital"][0] * M6)
    six, three = F["nca2_six"]
    assert F["puhl_life"][:2] == [six, three]
    chk("    six months (六个月)", six, told("票据的期限是六个月", "期限是", "个月"))
    chk("    three months each (每次三个月)", three, told("每次三个月", "每次", "个月"))
    assert F["nca2_rediscount"] == F["puhl_discount"] == [3]
    chk("    the last three months (最后三个月)", F["nca2_rediscount"][0], told("最后三个月里", "最后", "个月"))
    chk("    over four years (四年以上)", F["puhl_life"][2], told("有的票据流通了四年以上", "流通了", "年以上"))
    lim, y24 = F["nca2_100m"][:2]
    said("按 1924 年的法律，帝国银行直接借给政府的钱以 1 亿帝国马克为限", y24, lim * M6)
    d1, y, bn = F["nca2_12bn"]
    assert F["puhl_12"] == [y, bn]
    said("到 1938 年 4 月 1 日停用时，在外的 MEFO 票据有 120 亿帝国马克", y, mon("nca2_12bn", "April"), d1, bn * B9)


def ex_mefo(F, Y, Q):
    g, c1, c2 = MEFO["spend"], MEFO["disc1"], MEFO["disc2"]
    out, inside = F["ec369_6and6"]
    Rb = reichsbank()
    nfeb = Rb.notes_mrm["1938-02-28"]
    said("第 1 年，军备开支 10 全部用 MEFO 票据支付，预算上没有这笔钱。厂商把 4 拿到帝国银行贴现，银行与企业持有其余的 6。"
         "第 2 年没有新的开支，持票的人又把 3 拿去贴现", 1, g, c1, g - c1, 2, c2)
    said("（1）按式~\\eqref{eq:alternatives-mefo}，第 1 年的$\\Delta W^{o}$与$\\Delta H$各是多少？（2）第 2 年呢？赤字是多少？"
         "（3）按帝国银行董事们 1939 年的备忘录，帝国银行自己持有约 60 亿帝国马克的 MEFO 票据，银行与企业持有约 60 亿",
         1, 1, 2, 2, 3, F["ec369_date"][1], inside * B9, out * B9)
    said("1938 年 2 月底，流通的银行券是 52.8 亿", 1938, 2, nfeb * M6)
    said("（1）$G$里算上 10，$\\Delta W^{o}=6$，$\\Delta H=\\Delta W^{c}=4$，$10=6+4$", 1, g, g - c1, c1, g, g - c1, c1)
    said("（2）$\\Delta W^{o}=-3$，$\\Delta H=+3$，赤字是 0，基础货币仍增加了 3", 2, c2, c2, 0, c2)
    x = out * B9 / (nfeb * M6)
    assert x > 1                                                                 # 增加一倍多
    said("（3）基础货币最多增加约 60 亿，是原有银行券的$60/52.8\\approx1.1$倍", 3, out * B9, out * 10, nfeb / 100, x)
    say("这些钱若都以银行券的形式流出来，银行券就会增加一倍多")


def ec369(F, Y, Q):
    d7, y = F["ec369_date"]
    said("1939 年 1 月 7 日，帝国银行的董事们给希特勒写了一份备忘录", y, 1, d7)
    assert "Jan.1939" in Q["ec369_date"]
    out, inside = F["ec369_6and6"]
    assert "outside the Reichsbank" in Q["ec369_6and6"] and "carried in its portfolio" in Q["ec369_6and6"]
    said("帝国银行在自己的资产里放了约 60 亿帝国马克的 MEFO 票据，又把约 60 亿放到了帝国银行以外", inside * B9, out * B9)
    Rb = reichsbank()
    r, b, n = Rb.reserves_mrm, Rb.bills_mrm, Rb.notes_mrm
    said("它的黄金与外汇储备，1929 年底约 26.9 亿帝国马克，1934 年底只剩 8,400 万", 1929, r["1929-12-31"] * M6, 1934,
         r["1934-12-31"] * M6)
    said("它持有的票据与支票，连同国库券，1932 年底约 28.1 亿，1938 年底约 82.4 亿", 1932, b["1932-12-31"] * M6, 1938,
         b["1938-12-31"] * M6)
    n32, nfeb, n38 = n["1932-12-31"], n["1938-02-28"], n["1938-12-31"]
    said("流通的银行券 1932 年底约 35.6 亿，1938 年 2 月底约 52.8 亿，五年多里多了约 17.2 亿", 1932, n32 * M6, 1938, 2,
         nfeb * M6, (nfeb - n32) * M6)
    chk("    five years and more (五年多): 31 December 1932 to 28 February 1938",
        (date(1938, 2, 28) - date(1932, 12, 31)).days // 365, told("五年多里多了", "", "年多"))
    said("此后十个月，银行券跳到约 82.2 亿，又多了约 29.5 亿", n38 * M6, (n38 - nfeb) * M6)
    chk("    ten months (十个月): March to December 1938", 12 - 2, told("此后十个月", "此后", "个月"))
    said("帝国银行的账目，1929—1938 年。每年年底与 1938 年 2 月 28 日", 1929, 1938, 1938, 2, 28)
    rm = _table("alternatives_reichsbank")[1]
    said("数据：联邦储备委员会《银行与货币统计 1914—1941》表 167", 1914, 1941,
         int(re.search(r"Table (\d+)", rm["citation"]).group(1)))
    say("表上没有单列 MEFO 票据")
    assert "The table does not name the MEFO bills" in rm["notes"]
    said("1938 年的增加里，还没有算上吞并奥地利与苏台德地区所需的 20 亿帝国马克", 1938, F["ec369_austria"][0] * B9)
    d31, y32, d30, y38, a, b2 = F["nca2_funded"]
    assert "31 December 1932 to 30 June 1938" in Q["nca2_funded"]
    said("1932 年 12 月 31 日到 1938 年 6 月 30 日，帝国的长期债务从 104 亿帝国马克增加到 190 亿帝国马克", y32, 12, d31, y38,
         6, d30, a * B9, b2 * B9)
    assert "dated 3 May 1935" in Q["nca2_memodate"]
    said("1935 年 5 月的备忘录说", F["nca2_memodate"][1], 5)
    assert F["imt_schacht"][2] == F["ndb_minister"][2] == F["nca2_newplan"][0]       # 兼任经济部长 (1934)
    said("1934 年，兼任经济部长的沙赫特设计了一整套管制", F["nca2_newplan"][0])
    chk("    three features (三个要点)", F["nca2_three"][0], told("它有三个要点", "有", "个要点"))
    said("沙赫特的影响从 1936 年起变小。这一年 4 月", F["imt_april1936"][0], mon("imt_april1936", "April"))
    d16, y36, f1, f2 = F["imt_oct1936"]
    said("10 月 16 日，戈林又成为四年计划的全权代表", mon("imt_oct1936", "October"), d16)
    chk("    the Four-Year Plan (四年计划)", f1, told("戈林又成为四年计划", "成为", "年计划"))
    chk("    within four years (四年里)", f2, told("任务是在四年里使", "在", "年里"))
    said("沙赫特早在 1936 年就主张", F["imt_1936limit"][0])
    d, y = F["imt_resigned"]
    assert F["ndb_dismiss"][1:3] == [11, y] and mon("imt_resigned", "November") == 11
    said("1937 年 11 月，他辞去了经济部长与战争经济全权代表的职务", y, 11)
    d31, y = F["imt_march31"]
    said("1938 年 3 月 31 日，他停止发行", y, mon("imt_march31", "March"), d31)
    a, b3 = F["ec369_loan"]
    assert "the fourth Reich loan of 1938" in column("note")["ec369_loan"]
    said("1938 年的一笔国债，国债银团承接 15 亿帝国马克，其中 4.15 亿没能通过公开认购卖出去", 1938, a * M6, b3 * M6)
    d7, y = F["imt_jan7"]
    said("1939 年 1 月 7 日，沙赫特把董事们签名的备忘录交给希特勒", y, mon("imt_jan7", "January"), d7)
    assert (d7, y) == tuple(F["ec369_date"])
    bn, y = F["ec369_3bn"]
    said("1939 年到期的约 30 亿帝国马克 MEFO 票据", y, bn * B9)
    d20, y = F["imt_dismissed"]
    assert F["ndb_dismiss"][3:] == [d20, 1, y] and mon("imt_dismissed", "January") == 1
    said("1 月 20 日，希特勒解除了他的帝国银行行长职务", 1, d20)


def aggression(F, Y, Q):
    d1, y = F["imt_poland"]
    said("1939 年 9 月 1 日德国对波兰发动的战争", y, mon("imt_poland", "September"), d1)
    d, y, n, v = F["imt_sauckel"]
    said("1944 年 3 月 1 日说，到达德国的 500 万外国工人里，“自愿来的连 20 万都不到”", y, mon("imt_sauckel", "March"), d, n,
         v)
    said("到 1938 年秋天", F["imt_autumn1938"][0])
    said("犹太人被课以 10 亿帝国马克的集体罚款", F["imt_fine"][0] * B9)
    assert "extermination of the Jews" in Q["imt_extermination"]
    say("纳粹推行灭绝犹太人的政策")
    assert "Plenipotentiary-General for the Utilization of Labor" in Q["imt_sauckel_role"]
    say("绍克尔（Fritz Sauckel，1894—1946）是主管劳动力调配的全权总代表")
    said("约 600 万犹太人被杀害", F["imt_6m"][0] * M6)


def repressed(F, Y, Q):
    said("按国际清算银行 1937 年的年报，四年计划设了一位物价专员", Y["bis_price"])
    chk("    two requirements (两个条件)", F["ec369_two"][0], told("坚持两个条件", "坚持", "个条件"))
    a0, a1, m0, m1 = CEIL["a0"], CEIL["a1"], CEIL["months0"], CEIL["months1"]
    said("某种布的需求是$Q_d=120-P$，供给是$Q_s=P$。军备开支让人们手里的钱多了，需求变成$Q_d=140-P$", a0, a1)
    said("（1）原来的均衡价格与数量是多少？没有限价时，新的均衡是多少？（2）限价以后，市场上缺多少？（3）只有$Q_s$那么多的布",
         1, 2, 3)
    said("（4）一件衣服从前穿 24 个月，现在只能穿 6 个月", 4, m0, m1)
    p0, p1 = a0 / 2, a1 / 2                                                      # a - P = P
    said("（1）$120-P=P$，$P=60$，$Q=60$。没有限价时，$140-P=P$，$P=70$，$Q=70$，价格涨 16.7\\%", 1, a0, p0, p0, a1, p1,
         p1, rise(p0, p1))
    qd = a1 - p0
    said("（2）限价 60 时，$Q_s=60$，$Q_d=140-60=80$，缺 20。这 20 的需求只能排队", 2, p0, p0, a1, p0, qd, qd - p0,
         qd - p0)
    pb = a1 - p0                                                                 # the price at which a1 - P = Qs = p0
    said("（3）$140-P=60$，$P=80$。黑市的价格可以到 80，比限价高三分之一，比没有限价时的 70 还高", 3, a1, p0, pb, pb, p1)
    chk("    a third above the ceiling (三分之一)", (pb - p0) / p0, told("比限价高三分之一", "高"))
    assert pb > p1
    said("（4）每月的价格从$P/24$涨到$P/6$，是原来的 4 倍，涨了 300\\%。物价指数只看标价，显示的是 0", 4, m0, m1, m0 / m1,
         100 * (m0 / m1 - 1), 0)
    said("\\cmprow{德国 1936—1938 年}", F["imt_oct1936"][1], 1938)
    assert "which formerly lasted for years last now only months" in Q["ec369_clothes"]
    said("1936 年以后，德国的涨价要经特别批准", F["imt_oct1936"][1])
    assert "price increases if not specially authorised are forbidden" in Q["bis_price"]
    n = reichsbank().notes_mrm
    assert n["1938-12-31"] / n["1932-12-31"] > 2                                # 一倍多
    said("帝国银行的银行券从 1932 年底到 1938 年底增加了一倍多", 1932, 1938)


def sweden(F, Y, Q):
    said("1931 年，萧条的冲击全面打到瑞典", F["bj98_drain"][0])
    a, b, three = F["rb_reserve"]
    said("离开金本位使它的外汇储备在三个月里从 3 亿克朗降到 3,000 万克朗", a * M6, b * M6)
    chk("    three months (三个月)", three, told("外汇储备在三个月里", "在", "个月"))
    d26 = F["bj98_sat"][0]
    assert date(1931, 9, int(d26)).weekday() == 5 and "Saturday September 26" in Q["bj98_sat"]   # 星期六
    said("9 月 26 日是星期六", 9, d26)
    assert F["bj98_sentence"][0] - d26 == 1
    say("第二天的政府声明宣布离开金本位")
    said("照 Berg 与 Jonung（1998）的说法，把稳定物价写进政府声明的", Y["bj98_prekeynes"])
    said("克朗改为浮动，贬值了 30\\%", F["rb_30"][0])
    d8, y, three = F["bj98_rooth"]
    said("10 月 8 日，国家银行的董事会采纳行长的建议", mon("bj98_rooth", "October"), d8)
    chk("    three economists (三位)", three, told("请卡塞尔等三位著名的经济学家", "等", "位"))
    said("1932 年 2 月，国家银行的董事会说", F["bj98_other"][0], mon("bj98_other", "February"))
    said("1932 年 5 月，议会最后确认了这个计划", F["bj98_may1932"][0], mon("bj98_may1932", "May"))
    said("1933 年 6 月，议会通过了修订的计划", F["bj98_june1933"][0], mon("bj98_june1933", "June"))
    a, b = F["bj98_rate"]
    said("把贴现率从 6\\% 提到 8\\%", a, b)
    y, three = F["bj98_nov1931"]
    said("1931 年 11 月，它试过按旧的黄金平价把克朗钉住英镑，只维持了三天", y, mon("bj98_nov1931", "November"))
    chk("    three days (三天)", three, told("只维持了三天", "维持了", "天"))
    par, y = F["bj98_parity"]
    assert "'The pound rate" in column("note")["bj98_parity"]                   # kronor per pound fell below par
    said("1931 年秋天，一英镑一度换不到 18.15 克朗，低于两国黄金平价所定的比价", y, par)
    said("1933 年 7 月，国家银行把克朗钉住英镑", F["bj98_peg"][0], mon("bj98_peg", "July"))
    K = kronor_per_pound()
    k = K.loc[1934:1938]
    assert k.max() - k.min() < 0.05                                              # the peg
    said("1934—1938 年，一英镑合约 19.4 克朗，比 1929 年的约 18.1 克朗贵了约 7\\%", 1934, 1938, k.mean(), 1929, K[1929],
         rise(K[1929], k.mean()))
    # fig:alternatives_sweden
    C, D = cpi(), discount()
    said("(a) 消费物价指数，年度，1931 年$=100$，1925—1939 年", 1931, 100, C.index[0], C.index[-1])
    said("(b) 瑞典国家银行的贴现率，月度，1929—1939 年", int(D.index[0][:4]), int(D.index[-1][:4]))
    cm = _table("riksbank_sweden_1925_1939")[1]
    t_a = float(re.search(r"Table I\.A(\d\.\d)", cm["source"]).group(1))
    t_b = float(re.search(r"Table II\.A(\d\.\d)", cm["source"]).group(1))
    y_a, y_b = [int(x) for x in re.findall(r"\b(20\d\d)\)", cm["citation"])]
    r_y, r_m, r_d = [int(x) for x in cm["retrieved"].split("-")]
    assert f"Sveriges riksbank, {cm['retrieved']}" in cm["license"]
    said("数据：Edvinsson 与 Söderberg（2010）表 I.A8.1；Waldenström（2014）表 II.A6.9，据 Sveriges riksbank 网站，2026 年 10 月"
         " 22 日；1931 年$=100$的换算是本书的计算", y_a, t_a, y_b, t_b, r_y, r_m, r_d, 1931, 100)
    band, base, y0, _, y1, y37, five = F["bj98_band"]
    assert "for September 1931" in Q["bj98_band"]
    said("1931—1936 年，国家银行自己的消费物价指数以 1931 年 9 月为 100，上下不到 3 个百分点", y0, 1900 + y1, y0, 9, base,
         band)
    said("1937 年，消费物价涨了将近 5\\%", y37, five)
    R = cpi1931()
    assert R.loc[1931:1939].idxmin() == 1933
    said("以 1931 年为 100，1933 年最低，是 96.2，1936 年回到 100.0", 1931, 100, 1933, R[1933], 1936, R[1936])
    said("1938 年是 105.1", 1938, R[1938])
    y, a, b = F["bj98_1937"]
    said("1937 年的批发物价接近 1928 年底的水平，消费物价指数“1931 年以来相对稳定”", y, a, b)
    assert D["1933-12"] == 2.5 and D["1933-11"] > 2.5 and D["1939-12"] == 3
    assert (D.loc["1933-12":"1939-11"] == 2.5).all()                            # 此后一直没变
    said("贴现率在 1933 年 12 月降到 2.5\\%，此后一直没变，到 1939 年 12 月才提到 3\\%", 1933, 12, D["1933-12"], 1939, 12,
         D["1939-12"])
    s, y0, y1, us, ri, ru = F["bj98_ip"]
    said("1929—1932 年，瑞典的工业生产降了 21\\%，美国降了 46\\%", y0, 1900 + y1, s, us)
    said("实际收入分别降了 9\\% 与 22\\%", ri, ru)
    d, y = F["bj98_wig1933"]
    said("1933 年 5 月 26 日，财政大臣维格福斯在一份政府议案里第一次评价货币计划", y, mon("bj98_wig1933", "May"), d)
    a, b = F["bj98_fallen"]
    assert "between September 1931 and April 1933" in Q["bj98_fallen"]
    said("1931 年 9 月到 1933 年 4 月，批发物价与消费物价都下跌了", a, 9, b, 4)
    said("1937 年，他说近几年货币与汇率政策的特征是", Y["bj98_reflation"])


def level(F, Y, Q):
    said("记$p_t$为物价水平的对数乘以 100", 100)
    said("瑞典 1931 年的目标是物价不变，相当于$\\pi^{*}=0$", F["bj98_free"][0], 0)
    p0, pi, shock, beta = PLT["p0"], PLT["pi"], PLT["shock"], PLT["beta"]
    p1 = p0 + pi - shock
    said("设$p_0=0$，$\\pi^{*}=2$。第 1 年一次冲击让物价比目标低了 3，$p_1=-1$", p0, pi, 1, shock, -p1)
    said("（1）在物价水平目标下，第 2 年的通胀要是多少，物价才回到目标的路径上？（2）在通胀目标下，第 2 年的通胀目标是多少？第 2 "
         "年末的物价比原来的路径低多少？（3）", 1, 2, 2, 2, 2, 3)
    said("设$\\beta=0.1$，物价比$p_0$低 3 时，利率比$i_0$低多少？", beta, shock)
    p2 = p0 + 2 * pi
    said("（1）目标路径是$p^{*}_2=0+2\\times2=4$，要从$-1$涨到 4，通胀要有 5，比目标高 3", 1, p0, 2, pi, p2, -p1, p2,
         p2 - p1, p2 - p1 - pi)
    said("（2）通胀目标仍是 2，$p_2=-1+2=1$，比原来的路径低 3。这 3 就是基数漂移", 2, pi, -p1, pi, p1 + pi,
         p2 - (p1 + pi), shock)
    said("（3）低$0.1\\times3=0.3$个百分点", 3, beta, shock, beta * shock)
    said("就像$\\pi^{*}=0$的物价水平目标", 0)
    said("{瑞典 1931—1937 年：物价水平目标}", F["bj98_free"][0], 1900 + F["bj98_cassel37"][1])
    y, x = F["rb_1993"]
    said("{瑞典国家银行 1993 年定为每年 2\\%", y, x)
    said("{先浮动，1933 年 7 月起钉住英镑", F["bj98_peg"][0], mon("bj98_peg", "July"))


def newdeal(F, Y, Q):
    d, y = F["aaa_date"][:2]
    said("1933 年 5 月 12 日的农业调整法", y, mon("aaa_date", "May"), d)
    d, y = F["nira_date"][:2]
    said("6 月 16 日的国家工业复兴法", mon("nira_date", "June"), d)
    assert "For the purposes of this Act" in Q["nira_purposes"]
    said("为实施这部法律，国会授权拨款 33 亿美元", F["nira_sum"][0])
    sec = int(re.search(r"sec\. (\d+)\(a\)", column("juan")["nira_7a"]).group(1))
    said("按国家工业复兴法第 7 条（a）款", sec)
    d, y = F["nlra_date"][:2]
    said("1935 年 7 月 5 日的国家劳工关系法", y, mon("nlra_date", "July"), d)
    d, y, _ = F["era_date"]
    said("1935 年 4 月 8 日的紧急救济拨款法拨款 40 亿美元", y, mon("era_date", "April"), d, F["era_sum"][0])
    N = column("note")
    assert "fiscal year ending 30 June 1933" in N["cy_1933"] and "billion dollars" in N["cy_1933"]
    r, o, s = F["cy_1933"]
    assert abs(r - o - s) < 0.101
    said("1933 财年到 6 月 30 日为止，联邦收入 21 亿美元，支出 47 亿美元，赤字 26 亿美元", 1933, 6, 30, r * B9, o * B9,
         -s * B9)
    r, o, s = F["cy_1934"]
    said("1934 财年，收入 31 亿美元，支出 65 亿美元，赤字 33 亿美元，约是支出的一半", 1934, r * B9, o * B9, -s * B9)
    chk("    about half the outlays (一半)", -s / o, told("约是支出的一半", "支出的"), tol=0.05)
    said("到 1937 财年，赤字还有 28 亿美元", 1937, -F["cy_1937"][2] * B9)
    said("{1933 年 5 月被摧毁，工人被迫加入劳工阵线", F["imt_unions"][1], 5)
    said("{1933 年与 1935 年的法律保障组织工会与集体谈判的权利", F["nira_date"][1], F["nlra_date"][1])
    said("赤字公开，1934 财年 33 亿美元", 1934, -F["cy_1934"][2] * B9)
    said("{美元 1933—1934 年贬值（\\chref{ch:depressionus}）}", 1933, 1934)
    R = ratios()
    said("\\cmprow{1938 年的人均 GDP}{1929 年的 123.3\\%\\cite{mpd2023}}{1929 年的 88.1\\%\\cite{mpd2023}}", 1938, 1929,
         R.loc["DEU", 1938], 1929, R.loc["USA", 1938])
    assert R.loc["DEU", 1938] > R.loc["USA", 1938]                              # 德国的扩张更快
    yb = citation_year(_table("alternatives_boj_sales")[1]["citation"])
    said("日本银行 1984 年的行史也拿新政作比较", yb)


def debate(F, Y, Q):
    assert "used exclusively for financing rearmament" in Q["puhl_exclusive"]
    said("MEFO 票据全部用于再军备，1938 年停用时在外的有 120 亿帝国马克", F["puhl_12"][0], F["puhl_12"][1] * B9)
    said("1935 年 5 月的备忘录也说", F["nca2_memodate"][1], mon("nca2_memodate", "May"))
    assert "ermöglichte" in Q["ndb_geld"]                                       # enabled, not drove
    said("沙赫特 1933 年回到帝国银行，就让创造就业与重整军备同时起步", F["ndb_17"][2])
    said("为加速的再军备筹钱的需要，到 1935 年初才出现", F["puhl_1935"][0])
    R = ratios()
    said("1932—1934 年，德国的人均 GDP 已从 1929 年的 83.0\\% 回到 95.2\\%", 1932, 1934, 1929, R.loc["DEU", 1932],
         R.loc["DEU", 1934])
    yb = citation_year(_table("alternatives_boj_sales")[1]["citation"])
    said("日本银行 1984 年的行史列出两种评价", yb)
    said("照 Nanto 与 Takagi（1985）的研究", F["sz_nanto"][0])
    said("照 Cha（2003）的研究", F["sz_cha"][0])
    said("照 Umeda（2006）的估计", F["sz_umeda_year"][0])
    said("1933 年钉住英镑", F["bj98_question"][0])
    a, b = F["bj98_cassel37"]
    said("1936—1937 年英国的物价急涨", a, 1900 + b)
    said("俄林 1933 年说", F["bj98_ohlin"][0])
    said("按 Eichengreen 与 Sachs 对 Jonung（1981）的转述", F["es_jonung"][0])
    a, b = F["bj98_prekeynes"]
    said("瑞典 1931—1932 年的货币计划产生在一个“前凯恩斯的世界”里", a, 1900 + b)


def check_section(F, Y, Q):
    out, inside = F["ec369_6and6"]
    bn = F["nca2_12bn"][2]
    assert out + inside == bn == F["puhl_12"][1]
    said("董事们的备忘录都是 120 亿帝国马克，备忘录说的是帝国银行里外各约 60 亿", bn * B9, out * B9)
    d1, y33, n33, d1b, y38, n38 = F["ec369_currency"]
    assert "O n January 1, 1933" in Q["ec369_currency"] and "Up to March 1, 1938" in Q["ec369_currency"]
    said("备忘录里的银行券，1933 年 1 月 1 日是 35.6 亿，1938 年 3 月 1 日是 52.8 亿", y33, 1, d1, n33 * M6, y38, 3, d1b,
         n38 * M6)
    n = reichsbank().notes_mrm
    assert (n33, n38) == (n["1932-12-31"], n["1938-02-28"])                      # 完全相同
    said("这两个数与《银行与货币统计》里 1932 年底与 1938 年 2 月底的数完全相同", 1932, 1938, 2)
    assert F["ec369_8223"][3] == n["1938-12-31"]
    said("1938 年底的 82.2 亿也相同", 1938, F["ec369_8223"][3] * M6)
    T17 = F["bj_t17"]
    said("1933 年与 1934 年是约 11.2 亿与 7.0 亿日元", 1933, 1934, T17[1] * M6, T17[2] * M6)
    said("1935 年与 1936 年是约 7.5 亿与 15.8 亿日元", 1935, 1936, T17[3] * M6, T17[4] * M6)
    said("Ide 的表 1 列出的日本银行卖出的国债，与表 1-17 的半年数相同", F["ide_t1_head"][0], 1, 17)
    Ym = yen_monthly()
    a, b = Ym[(1931, 11)], Ym[(1932, 11)]
    said("按《银行与货币统计》，日元 1931 年 11 月平均是 49.3 美分，1932 年 11 月是 20.6 美分，跌了 58.2\\%", 1931, 11, a, 1932,
         11, b, fall(a, b))
    chk("    Shizume's 60 per cent: from the parity to 20 cents", fall(F["sz_parity"][0], F["sz_20c"][1]), F["sz_60"][0],
        tol=0.5)
    said("Shizume（2009）的 60\\%，是从约 49.8 美分的平价跌到 20 美分算的", Y["sz_keynesian"], F["sz_60"][0],
         F["sz_parity"][0], F["sz_20c"][1])
    P = pence_per_yen().loc[1934:1937]
    said("1934—1937 年，日元每年平均合 14.0 到 14.2 便士", 1934, 1937, P.min(), P.max())
    s, d = F["bis_yen"][1:]
    said("这与国际清算银行说的 1 先令 2 便士相合", s, d)
    assert abs(P.mean() - (12 * s + d)) < 0.2
    said("瑞典 1937 年的消费物价涨了将近 5\\%", F["bj98_band"][5], F["bj98_band"][6])
    say("德国的标价被命令压住，物价指数量不到被压抑的通胀")


def deeper(F, Y, Q):
    said("都据日本银行 1984 年的行史转引", citation_year(_table("alternatives_boj_sales")[1]["citation"]))
    said("高桥 1934 年 4 月的话", F["bj_tk1934"][1], F["bj_tk1934"][2])
    said("日本银行总裁 1932 年 10 月的话据 Ide（2003）转引日本银行的档案", F["ide_hijikata"][0], 10, Y["ide_confident"])
    said("沙赫特 1935 年 5 月 3 日的备忘录", F["nca2_memodate"][1], 5, F["nca2_memodate"][0])
    said("Cha（2003）、Nanto 与 Takagi（1985）、Umeda（2006）据 Shizume 的转述，Jonung（1981）据 Eichengreen 与 Sachs 的转述",
         F["sz_cha"][0], F["sz_nanto"][0], F["sz_umeda_year"][0], F["es_jonung"][0])
    d30, m6, y34 = F["ndb_minister"]
    assert F["imt_schacht"][2] == y34 and "Minister of Economics in August 1934" in Q["imt_schacht"]
    said("沙赫特出任经济部长的日子，判决书作 1934 年 8 月，《新德意志传记》作 1934 年 6 月 30 日", y34, 8, y34, m6, d30)
    d16, y37 = F["imt_resigned"]
    d26, m11 = F["ndb_dismiss"][:2]
    said("辞去经济部长的日子，判决书作 1937 年 11 月 16 日，传记作 11 月 26 日", y37, 11, d16, m11, d26)
    d20, y39 = F["imt_dismissed"]
    assert F["imt_jan19"] == [19] and Q["imt_jan19"].startswith("On January 19")
    said("被解除行长职务的日子，判决书一处作 1939 年 1 月 20 日，两段以后又作 1 月 19 日，传记作 1 月 20 日", y39, 1, d20, 1,
         F["imt_jan19"][0], F["ndb_dismiss"][4], F["ndb_dismiss"][3])
    said("判决书说是“5-year notes”", F["imt_fiveyear"][0])
    six, three, four = F["puhl_life"]
    chk("    Puhl: six months (六个月)", six, told("普尔说的是六个月的票据", "说的是", "个月"))
    chk("    three months each (展期三个月)", three, told("一次次展期三个月", "展期", "个月"))
    chk("    over four years (超过四年)", four, told("有的超过四年", "超过", "年"))
    chk("    the memorandum: five years (五年内)", F["ec369_5years"][0], told("董事们的备忘录说五年内赎回", "说", "年内"))
    D = discount()
    a, b = F["bj98_rate"]
    r25, y25 = F["bj98_25"]
    said("国家银行的贴现率，Berg 与 Jonung 说从 6\\% 提到 8\\%，月度的序列是 1931 年 8 月 4\\%、9 月 8\\%；他们说 1934 年降到 "
         "2.5\\%，月度的序列在 1933 年 12 月", a, b, 1931, 8, D["1931-08"], 9, D["1931-09"], y25, r25, 1933, 12)
    assert D["1933-12"] == r25 and D["1933-11"] > r25
    said("Ide 的表 1 把半年标作财政年度", F["ide_t1_head"][0])
    said("Shizume 给的日元旧平价以先令计，比用美分的平价与英镑的旧平价换算的少约 1\\%", fall(20 * F["sz_parity"][0] /
         pound_parity(), F["sz_parity"][1]))
    assert "the half-year rows are labelled fiscal years" in column("note")["ide_t1_head"]
    band, base = F["bj98_band"][:2]
    said("Berg 与 Jonung 说的不到 3 个百分点，是国家银行自己的周指数，以 1931 年 9 月为 100", band, 1931, 9, base)
    said("换算成 1931 年$=100$是本书的计算", 1931, 100)
    n57 = int(re.search(r"note (\d+)", column("juan")["ide_n57"]).group(1))
    fy, army, navy = F["ide_n57"]
    assert (army, navy) != (F["ide_army"][2], F["ide_navy"][1])                 # 对不上
    said("Ide 的注 57 列出的 1935 年度陆海军继续费", n57, fy)
    rnotes = _table("alternatives_reichsbank")[1]["notes"]
    dd, mm, yy = re.search(r"by decree of (\d+) (\w+) (\d{4}) the Austrian National Bank", rnotes).groups()
    said("1938 年 3 月 17 日起，帝国银行的账目包括了并入的奥地利国家银行", int(yy), MONTHS[mm], int(dd))
    notes = meta()["notes"]
    law = re.search(r"the law of (\d+) (\w+) (\d{4}) on unemployment, the price-stop decree of (\w+) (\d{4})", notes)
    said("物价冻结的法令（1936 年 11 月）与 1933 年 6 月莱因哈特的创造就业法", int(law.group(5)), MONTHS[law.group(4)],
         int(law.group(3)), MONTHS[law.group(2)])
    yrs = {k: int(v) for k, v in re.findall(r"(Ritschl|Woitek|Tooze) \((\d{4})\)", notes)}
    said("Ritschl（2002）与 Straumann 和 Woitek（2009）的论文、Tooze（2006）", yrs["Ritschl"], yrs["Woitek"], yrs["Tooze"])
    j79, j81 = [int(x) for x in re.search(r"Jonung \((\d{4}), (\d{4})\)", notes).groups()]
    said("Cha（2003）的原文、Smethurst（2007）的高桥传记、Jonung（1979，1981）也没有取得", F["sz_cha"][0],
         F["sz_smethurst"][0], j79, j81)
    assert "drops 'Million' after '8,223'" in notes
    said("又在 8,223 后面漏了百万这个单位", F["ec369_8223"][3])
    a, b, _ = F["rb_reserve"]
    said("外汇储备从 3 亿降到 3,000 万克朗只据瑞典国家银行的历史页", a * M6, b * M6)


def legacy(F, Y, Q):
    a5, y = F["sz_art5"]
    said("1947 年的《财政法》第 5 条禁止日本银行承购国债", y, a5)
    said("瑞典 1931 年的目标后来被通胀目标代替，1993 年，瑞典国家银行把稳定物价定为每年 2\\% 的通胀", F["bj98_free"][0],
         *F["rb_1993"])


def takeaways(F, Y, Q):
    H, T = boj_sales()
    said("日本 1931 年 12 月禁止黄金出口，日元一年里对美元贬值约六成。1932 年 11 月起日本银行直接承购国债，再卖给银行。1933—"
         "1935 年卖出了承购的九成以上，1936 年只卖出四成多", 1931, 12, 1932, 11, 1933, 1935, 1936)
    chk("    about six tenths (约六成)", F["sz_60"][0] / 100, told("日元一年里对美元贬值约六成", "约"))
    assert T.sold_pct / 100 > told("卖出了承购的九成以上", "承购的", "以上")
    s36 = year_sum(H, 1936, "sold_kyen") / year_sum(H, 1936, "underwritten_kyen")
    assert told("1936 年只卖出四成多", "卖出", "多") < s36 < 0.5
    d, y = F["sz_feb26"]
    said("1936 年 2 月 26 日被杀，此后日本转入战时财政", y, 2, d)
    said("到 1938 年在外的有 120 亿帝国马克", F["nca2_12bn"][1], F["nca2_12bn"][2] * B9)
    said("瑞典 1931 年把稳定国内物价定为货币政策的目标", F["bj98_free"][0])


def selfcheck(F, Y, Q):
    s, b, d, d2 = SC1["spend"], SC1["banks"], SC1["disc"], SC1["disc2"]
    assert s == b + d
    said("军备开支 50 全部用 MEFO 票据支付，银行持有 30，帝国银行贴现 20", s, b, d)
    said("第二年银行把 10 拿去贴现，又怎样？数字为教学输入", d2)
    a, c = SC2["a"], SC2["ceiling"]
    said("需求$Q_d=100-P$，供给$Q_s=P$，价格限定在 40", a, c)
    pi, low = SC3["pi"], SC3["low"]
    said("物价水平目标$\\pi^{*}=0$，第 1 年物价比目标低了 2。第 2 年的通胀要是多少？若是通胀目标$\\pi^{*}=0$呢", pi, 1, low, 2,
         pi)
    H, _ = boj_sales()
    u36, s36 = year_sum(H, 1936, "underwritten_kyen") * 1000, year_sum(H, 1936, "sold_kyen") * 1000
    said("1936 年，日本银行承购约 15.8 亿日元的国债，只卖出约 6.9 亿", 1936, u36, s36)
    Ym = yen_monthly()
    y0, y1 = round(Ym[(1931, 11)], 1), round(Ym[(1932, 11)], 1)
    said("日元从 49.3 美分跌到 20.6 美分", y0, y1)
    # answers
    said("$\\Delta W^{o}=30$，$\\Delta H=20$，$50=30+20$。第二年$\\Delta W^{o}=-10$，$\\Delta H=+10$，赤字是 0，基础货币仍增加 10",
         b, d, s, b, d, d2, d2, 0, d2)
    qd = a - c
    said("限价 40 时$Q_s=40$，$Q_d=60$，缺 20。$100-P=40$，黑市的价格可以到 60", c, c, qd, qd - c, a, c, a - c)
    said("要有 2 的通胀，把物价补回目标。通胀目标下仍是 0，物价停在比原来的路径低 2 的地方", pi + low, pi, low)
    said("卖不出去的约 9 亿日元留在日本银行", u36 - s36)
    said("跌了$1-20.6/49.3\\approx58\\%$。一美元的日元价格从$100/49.3\\approx2.03$日元涨到$100/20.6\\approx4.85$日元，涨了约 "
         "139\\%", 1, y1, y0, fall(y0, y1), 100, y0, 100 / y0, 100, y1, 100 / y1, rise(100 / y0, 100 / y1))


def ending(F, Y, Q):
    d, y, _ = F["sz_dec13"]
    said("1931 年 12 月 13 日，高桥上任当天就禁止了黄金出口", y, 12, d)
    said("1934 年 4 月，他说，公债发行的限度", F["bj_tk1934"][1], F["bj_tk1934"][2])
    said("1936 年 2 月他被杀", F["sz_feb26"][1], 2)
    assert "whose primary aim was to satisfy the needs of the conspirators' military economy" in Q["nca2_determined"]
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 31's question"
    assert t.index("\\end{answers}") < t.index("1931 年 12 月 13 日，高桥上任当天")
    ch31 = (ROOT / "zh" / "ch31_soviet.tex").read_text(encoding="utf-8")
    assert f"\\guidequestion{{{NEXT}}}" in ch31


def models() -> None:
    """The key equations, and their arithmetic checked with numbers."""
    say("G_t-T_t+i_{t-1}B_{t-1}=\\Delta B^{n}_t+\\Delta W^{o}_t+\\Delta H_t,\\qquad H_t=W^{c}_t+X_t "
        ".\\label{eq:alternatives-mefo}")
    say("p^{*}_t=p_0+t\\,\\pi^{*}\\quad\\text{（物价水平目标）},\\qquad p^{*}_t=p_{t-1}+\\pi^{*}\\quad\\text{（通胀目标）}"
        ".\\label{eq:alternatives-level}")
    # MEFO: bills paid out (outside the budget) and discounted; the identity holds each year with X = 0, no interest,
    # no ordinary debt
    for spend, disc in (([10, 0], [4, 3]), ([50, 0], [20, 10]), ([3, 5, 4], [1, 2, 6])):
        Wo = Wc = 0.0
        for g, x in zip(spend, disc):
            dWo, dWc = g - x, x
            Wo, Wc = Wo + dWo, Wc + dWc
            dH = dWc                                                             # H = W^c + X, X fixed
            chk(f"    eq:alternatives-mefo: G - T = dB^n + dW^o + dH ({g}, {x})", g, 0 + dWo + dH)
        chk("    the bills outstanding = W^o + W^c = what was spent", Wo + Wc, sum(spend))
    # price-level and inflation targets after a shock
    for p0, pi, shock in ((0, 2, 3), (0, 0, 2), (1, 1.5, -1)):
        p1 = p0 + pi - shock
        plt2 = p0 + 2 * pi                                                       # p*_2 = p_0 + 2 pi*
        it2 = p1 + pi                                                            # p*_2 = p_1 + pi*
        chk(f"    eq:alternatives-level: the price-level target makes up the shock ({p0}, {pi}, {shock})",
            (plt2 - p1) - pi, shock)
        chk("    the inflation target leaves it (base drift)", plt2 - it2, shock)
    # Wicksell's rule summed: i_t - i_0 = beta (p_t - p_0)
    rng = np.random.default_rng(30)
    p = np.cumsum(rng.normal(0, 2, 20))
    pi_t = np.diff(np.concatenate([[0.0], p]))
    i = 4 + 0.1 * np.cumsum(pi_t)
    chk("    Wicksell's rule: i_t - i_0 = beta (p_t - p_0)", float(np.max(np.abs((i - 4) - 0.1 * p))), 0, tol=1e-12)
    # the ceiling: Qd = a - P, Qs = P
    for a, ceiling in ((140, 60), (100, 40), (120, 60)):
        qs, qd = ceiling, a - ceiling
        black = a - qs
        chk(f"    the ceiling ({a}, {ceiling}): the shortage = a - 2 x ceiling", qd - qs, a - 2 * ceiling)
        chk("    the black-market price clears the supplied quantity", a - black, qs)


def figures_data(F) -> None:
    """What the figures assert of their data."""
    Ym = yen_monthly()
    assert Ym.idxmin() == (1932, 11) and Ym.loc[1931].loc[:11].min() > 49           # at par until November 1931
    assert abs(Ym.loc[1931].loc[:11].mean() - F["sz_parity"][0]) < 0.6
    H, _ = boj_sales()
    assert H.underwritten_kyen.idxmax() == 7 and H.sold_kyen.idxmax() == 3         # 1936 H1 and 1934 H1
    Rb = reichsbank()
    assert Rb.reserves_mrm.idxmax() == "1929-12-31" and Rb.notes_mrm.idxmax() == "1938-12-31"
    assert Rb.bills_mrm["1938-12-31"] > Rb.bills_mrm["1938-02-28"] > Rb.bills_mrm["1932-12-31"]
    C = cpi1931()
    assert C.idxmax() == 1925 and C.loc[1931:1936].max() - C.loc[1931:1936].min() < 4
    D = discount()
    assert D.idxmax() == "1931-09" and D.max() == 8


# ---------------------------------------------------------------------------------------------------
# 5. The book
# the life dates the chapter gives without a row of its own: the same words in an earlier chapter
LIVES = {"Hjalmar Schacht，1877—1970": "ch26_weimar"}
# the life dates from rows of the snapshot: words -> (row, index of the birth year, index of the death year)
ROW_LIVES = {"犬养毅（1855—1932）": ("ndl_ik_life", 0, 3),
             "高桥是清（1854—1936）": ("ndl_tk_life", 0, 3),
             "井上准之助（1869—1932）": ("ndl_in_life", 0, 3),
             "深井英五（1871—1945）": ("loc_fukai", 0, 1),
             "Adolf Hitler，1889—1945": ("loc_hitler", 0, 1),
             "Emil Puhl，1889—1962": ("loc_puhl", 0, 1),
             "Hermann Göring，1893—1946": ("loc_goring", 0, 1),
             "Felix Hamrin，1875—1937": ("loc_hamrin", 0, 1),
             "Ernst Wigforss，1881—1977": ("loc_wigforss", 0, 1),
             "Gustav Cassel，1866—1945": ("loc_cassel", 0, 1),
             "Dag Hammarskjöld，1905—1961": ("rb_hamm", 0, 1),
             "Bertil Ohlin，1899—1979": ("loc_ohlin", 0, 1),
             "Fritz Sauckel，1894—1946": ("loc_sauckel", 0, 1)}
# what other chapters tell: (words of this chapter, chapter where it is told, words there)
EVENTS = [("他第一次当行长是在 1923 年 12 月，马克刚刚稳定下来（\\chref{ch:weimar}）", "ch26_weimar",
           "12 月 22 日，沙赫特接替去世的哈芬施坦，出任帝国银行行长"),
          ("这正是\\chref{ch:weimar}里帝国银行贴现国库券、一张也不卖出的情形", "ch26_weimar",
           "从此政府缺钱，可以开一张国库券送进帝国银行，换回新印的银行券"),
          ("不用黄金作准备的发行叫信用发行（\\chref{ch:goldstandard}）", "ch23_goldstandard",
           "这部分叫作\\textbf{信用发行}"),
          ("式里的$B$只算中央银行以外的人持有的国债", "ch01_intro", "这里 $B$ 只算中央银行以外的人持有的政府债务"),
          ("$H$是基础货币，与\\chref{ch:money}的式~\\eqref{eq:money-base}相同", "ch04_money",
           "H=C+R,\\qquad M=C+D.\\label{eq:money-base}"),
          ("用\\chref{ch:intro}的合并预算约束看，MEFO 票据仍是政府的债。去掉那里的外币债", "ch01_intro",
           "\\underbrace{e_t\\,\\Delta B^{f}_t}_{\\text{借外币}}"),
          ("的规则$i_{t+1}=i_t+\\beta\\pi_t$逐年加起来，是$i_t-i_0=\\beta\\,(p_t-p_0)$", "ch25_wicksell",
           "把它逐年加起来，得到 $i_t-i_0=\\beta\\,(p_t-p_0)$"),
          ("瑞典由此成了第一个把稳定国内物价水平定为货币政策正式目标的国家（\\chref{ch:wicksell}）", "ch25_wicksell",
           "瑞典成了第一个把稳定国内物价水平定为货币政策正式目标的国家"),
          ("德国的资本管制“作用类似于明确的贬值”（\\chref{ch:depressionworld}）", "ch29_depressionworld",
           "德国的资本管制起了类似贬值的作用"),
          ("瑞典 1931 年 9 月离开了金本位（\\tabref{tab:depressionworld-exits}）", "ch29_depressionworld",
           "\\label{tab:depressionworld-exits}"),
          ("银行假日、存款保险与美元的贬值，\\chref{ch:depressionus}已经讲过", "ch28_depressionus", "联邦存款保险公司"),
          ("\\chref{ch:depressionus}说过，在 Romer 的估计里，美国的复苏主要靠货币的扩张，财政政策的作用很小", "ch28_depressionus",
           "Romer（1992）的模拟里，财政政策的作用很小"),
          ("{黄金流入变成基础货币（\\chref{ch:depressionus}）", "ch28_depressionus", "流入的黄金几乎一对一地变成了基础货币"),
          ("{美元 1933—1934 年贬值（\\chref{ch:depressionus}）}", "ch28_depressionus", "1934 年 1 月 31 日的公告把它定为"),
          ("\\chref{ch:depressionus}已经讲过", "ch28_depressionus", "新政的其他措施与别国的出路，在\\chref{ch:alternatives}里比较"),
          ("{维克塞尔的规则（\\chref{ch:wicksell}）}", "ch25_wicksell", "维克塞尔的规则后来在瑞典试过"),
          ("瑞典走的是\\chref{ch:wicksell}里的一条路，稳住本国货币对商品的价值，牺牲汇率的平价", "ch25_wicksell",
           "它可以设法让本国货币对商品的价值保持稳定，但那样就必然牺牲汇率的平价")]
# the chapters this one hands on to (FORWARD_REFS rows opened by Chapter 30)
LATER = {"ch:soviet": "ch31_soviet", "ch:generaltheory": "ch32_generaltheory", "ch:warfinance": "ch34_warfinance",
         "ch:planned": "ch43_planned", "ch:consensus": "ch55_consensus", "ch:zlb": "ch66_zlb",
         "ch:abenomics": "ch67_abenomics", "ch:fiscaldominance": "ch75_fiscaldominance"}


def book(F, Q):
    """Life dates and what other chapters tell."""
    t = tex_text()
    for words, ch in LIVES.items():
        assert words in t, words
        assert words in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (words, ch)
        COVERED.append(words)
    for words, (rid, i, j) in ROW_LIVES.items():
        assert words in t, words
        assert f"{F[rid][i]:.0f}—{F[rid][j]:.0f}" in words, (words, rid)
        COVERED.append(words)
    assert F["sz_life"] == [F["ndl_tk_life"][0], F["ndl_tk_life"][3]]           # Shizume's note 1 agrees
    assert Q["loc_rooth"] == "Rooth, Ivar, 1888-" and "Rooth" not in t          # no death year: not named
    for here, ch, there in EVENTS:
        assert here in t, here
        assert there in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (ch, there)
    for label, ch in LATER.items():
        assert f"\\chref{{{label}}}" in t, label
        assert f"\\label{{{label}}}" in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (label, ch)
    for label in ("ch:wicksell", "ch:weimar", "ch:depressionworld"):              # the prerequisites
        assert f"\\chref{{{label}}}\\enspace\\nameref{{{label}}}" in t, label
    print(f"ok {len(LIVES) + len(ROW_LIVES)} life dates, {len(EVENTS)} statements of other chapters, {len(LATER)} later "
          "chapters")


def identities(F) -> None:
    """The table snapshots' identities, and the values read on page images against the totals they print."""
    H, T = boj_sales()
    for c in ("underwritten_kyen", "sold_kyen"):
        chk(f"Table 1-17: the printed total of 1933-1935 = the sum of its six half-years ({c})",
            sum(year_sum(H, y, c) for y in (1933, 1934, 1935)), T[c])
    chk("Table 1-17: B/A (%) printed = computed, every half-year", float((100 * H.sold_kyen / H.underwritten_kyen
        - H.sold_pct).abs().max()), 0, tol=0.051)
    t17 = F["bj_t17"]
    chk("Table 1-7 (underwritten, million yen) = the yearly sums of Table 1-17, 1932-1936",
        [year_sum(H, y, "underwritten_kyen") / 1000 for y in range(1932, 1937)], t17, tol=0.5)
    tot = F["bj_t17_total"]
    assert all(a <= b for a, b in zip(t17, tot)) and t17[4] + F["bj_t17_public"][0] <= tot[4]   # other columns too
    chk("Ide's Table 1, GB sale by BOJ = the yearly sums of Table 1-17 (B), 1933-1935",
        [year_sum(H, y, "sold_kyen") for y in (1933, 1934, 1935)],
        [F["ide_t1_1933"][0], F["ide_t1_1934"][0], F["ide_t1_1935"][0]])
    Ym, X = yen_monthly(), fx()
    mean = Ym.groupby(level=0).mean()
    chk("Table 173: the yen's year = the mean of its twelve months, 1929-1938", float((mean - X.cents_per_yen.loc[1929:1938])
        .abs().max()), 0, tol=0.3)
    Rb = reichsbank()
    n = Rb.notes_mrm
    cur = F["ec369_currency"]
    chk("EC-369: currency on 1 January 1933 and 1 March 1938 = Table 167 on 31 December 1932 and 28 February 1938",
        [cur[2], cur[5]], [n["1932-12-31"], n["1938-02-28"]])
    chk("    and 8,223 on 31 December 1938", F["ec369_8223"][3], n["1938-12-31"])
    C = cpi()
    old = load_snapshot("riksbank_sweden_1870_1913")[0]
    assert old.year.max() < C.index.min()                                        # Chapter 25's years do not overlap
    cy = F["cy_1933"], F["cy_1934"], F["cy_1937"]
    for r, o, s in cy:
        chk("Historical Statistics Y 339-341: receipts - outlays = the deficit (billions, rounded)", r - o, s, tol=0.101)


def witnesses(F, Q):
    """Second witnesses of statements of the text, and the bibliography block of the chapter."""
    N = column("note")
    chk("the MEFO bills of 1938: 12 billion (the prosecution) = 12 billion (Puhl) = 6 + 6 (EC-369)",
        [F["nca2_12bn"][2], F["puhl_12"][1]], [sum(F["ec369_6and6"])] * 2)
    chk("the underwriting began on 25 November 1932: Shizume = Ide", F["sz_nov25"], F["ide_nov25"])
    chk("Takahashi's death: Shizume = the NDL's chronology = his portrait page", [F["sz_feb26"][0], F["ndlc_226"][3],
        F["ndl_tk_life"][5]], [26, 26, 26])
    Ym = yen_monthly()
    chk("the yen's fall, November 1931 to November 1932: BMS (58.2) and Shizume (60, from the parity)",
        fall(Ym[(1931, 11)], Ym[(1932, 11)]), F["sz_60"][0], tol=2.0)
    P = pence_per_yen().loc[1934:1937]
    chk("the yen at 1s. 2d. (BIS): BMS cross rates 1934-1937, pence", float(P.mean()), 12 * F["bis_yen"][1] +
        F["bis_yen"][2], tol=0.2)
    sh = 20 * F["sz_parity"][0] / pound_parity()
    chk("the yen's parity: 49.845 cents at the pound's parity of $4.8665 = 2.05 shillings (Shizume prints 2.0291)", sh,
        2.05, tol=0.005)
    assert abs(sh - F["sz_parity"][1]) > 0.01                                    # the two do not agree
    chk("the krona's parity: 18.15 kronor (Berg and Jonung) against BMS 1929", kronor_per_pound()[1929],
        F["bj98_parity"][0], tol=0.05)
    chk("the krona written down by 30 per cent (the Riksbank): BMS, the dollar value of 1932 against 1929 (at par)",
        fall(fx().cents_per_krona[1929], fx().cents_per_krona[1932]), F["rb_30"][0], tol=1.5)
    chk("Schacht back at the Reichsbank on 17 March 1933: the judgment = the NDB", F["imt_schacht"][:2],
        [F["ndb_17"][0], F["ndb_17"][2]])
    assert F["imt_dismissed"] == [20, 1939] and F["ndb_dismiss"][3:] == [20, 1, 1939]
    assert Q["rb_title"] == "1931 - First in the world with price stability target" and "the first country" in \
        Q["bj98_first"]                                                          # the Riksbank = Berg and Jonung
    assert "the opening paragraph of the same section says 20 January" in N["imt_jan19"]
    # the licences and the bibliography
    m = meta()
    lic = m["license"]
    for words in ("'" + Q["bjcr"] + "'", "'" + Q["ide_reprint"] + "'", "'" + Q["ndl_terms"] + "'",
                  "'The Library of Congress is not aware of any copyright restrictions in the Military Legal Resources "
                  "collection. Absent such restrictions, these materials are free to use and reuse.'",
                  "Credit line: Law Library of Congress, Military Legal Resources.",
                  "'" + Q["bis_reuse"] + "'", "'a statement that the translation is not an official BIS translation, "
                  "and that the BIS does not guarantee its accuracy or completeness.'",
                  "'The Riksbank's open data is freely available and may be further used without any special consent "
                  "or agreement being required. Enter source, Sveriges riksbank and date. If you have processed "
                  "statistics taken from the Riksbank's website, you may not state Sveriges Riksbank as the source.'",
                  "are public data", "in the public domain", "short phrases only"):
        assert words in lic, words
    assert Q["bis_translation"].endswith("that the translation is not an official BIS translation, and that the BIS "
                                         "does not guarantee its accuracy or completeness.")
    for name in ("alternatives_reichsbank", "alternatives_yen_monthly", "alternatives_fx_annual"):
        assert "Public domain" in _table(name)[1]["license"], name
    assert Q["bjcr"] in _table("alternatives_boj_sales")[1]["license"]
    assert "CC BY 4.0" in maddison_meta()["license"] and "CONDITIONS UNDER WHICH ALL ORIGINAL PAPERS MUST BE CITED" in \
        maddison_meta()["license"]
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    start = bib.index("% ---- 第 30 章")
    following = re.search(r"^% ---- 第 \d+ 章", bib[start + 1:], re.MULTILINE)
    end = start + 1 + following.start() if following else bib.index("\\end{thebibliography}")
    block = bib[start:end]
    items = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", block)}
    for key in ("shizume2009", "bojchron", "boj1984"):
        assert Q["bjcr"] in items[key] and "来源：日本银行" in items[key], key
    assert Q["ide_reprint"] in items["ide2003"] and "只引短句" in items["ide2003"]
    assert Q["ndl_terms"] in items["ndl2026"]
    assert Q["ndlc_terms"] == "あらかじめ国立国会図書館にお申込みください" and "(row ndlc_terms): the book takes only dates" \
        in lic and "本书只取其中事件的日子" in items["ndl2026"]
    for key in ("nca1947", "nca1946b", "nca1946g"):
        assert "The Library of Congress is not aware of any copyright restrictions" in items[key], key
        assert "Law Library of Congress, Military Legal Resources" in items[key] and "公有领域" in items[key], key
    assert Q["bis_reuse"] in items["bis1937"]
    assert "This translation is not an official BIS translation, and the BIS does not guarantee its accuracy or " \
           "completeness." in items["bis1937"]
    assert "不是国际清算银行的官方译文" in items["bis1937"]
    rb = items["riksbank2026d"]
    assert "The Riksbank's open data is freely available and may be further used without any special consent or " \
           "agreement being required." in rb and "来源：Sveriges riksbank，2026 年 10 月 22 日" in rb and "本书的计算" in rb
    for key in ("nira1933", "aaa1933", "nlra1935", "era1935", "census1975y"):
        assert "公有领域" in items[key], key
    for key, stat in (("aaa1933", "48 Stat. 31"), ("nira1933", "48 Stat. 195"), ("era1935", "49 Stat. 115"),
                      ("nlra1935", "49 Stat. 449")):
        assert stat in items[key], key
    for key, rid in (("aaa1933", "aaa_date"), ("nira1933", "nira_date"), ("nlra1935", "nlra_date")):
        assert f"Public No. {F[rid][3]:.0f}" in items[key], key
    assert "Y 339--341" in items["census1975y"] and "1105" in items["census1975y"]
    assert "id.loc.gov" in items["loc30"] and "公共数据" in items["loc30"]
    a, b, c, d, e = F["sz_chatitle"]
    assert f"Bank of Japan Review 2009-E-2" in items["shizume2009"]
    assert "IMES Discussion Paper No. 2003-E-10" in items["ide2003"]
    allitems = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", bib)}
    assert "第 30 章" in allitems["mpd2023"] and "第 29 章用 28 个经济体" in allitems["mpd2023"]
    assert "第 30 章" in allitems["bms1943"] and "表 167" in allitems["bms1943"] and "公有领域" in allitems["bms1943"]
    assert "No. 290" in allitems["berg1998"] and "第 30 章" in allitems["berg1998"]
    assert "22 (2005): 489--491" in allitems["schacht2005"]
    mm = maddison_meta()
    for iso in SIX:                                                               # the original sources, as required
        for s in mm["sources_by_country"][iso]:
            head = s.split(":")[1].strip()[:25].replace("&", "\\&").replace("$", "\\$")
            assert head in allitems["mpd29src"], (iso, head)
    keys = set(allitems)
    cited = {k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", tex_text()) for k in c.split(",")}
    assert cited <= keys, sorted(cited - keys)
    assert set(items) <= cited, sorted(set(items) - cited)
    print(f"ok {len(cited)} works cited, {len(items)} of them in the bibliography block of Chapter 30")


NAMES = ("Shizume|Ide|Berg|Jonung|Eichengreen|Sachs|Bernanke|James|Nanto|Takagi|Cha|Umeda|Smethurst|Ritschl|Straumann|"
         "Woitek|Tooze|Overy|Buchheim|Romer|Maddison|Bolt|Edvinsson|Söderberg|Waldenström")


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
    subj2 = re.findall(r"(?:^|[。；：，\n])\s*(?:" + NAMES + r")(?: 与 (?:" + NAMES + r"))?(?:（\d{4}）)?\s*(?:" + verbs + ")",
                       main)
    assert not subj2, subj2
    for words in ("本书没有找到", "没能取得", "没有取得"):
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
    japan(F, Y, Q)
    casebox(F, Y, Q)
    ex_underwrite(F, Y, Q)
    military(F, Y, Q)
    germany(F, Y, Q)
    ex_mefo(F, Y, Q)
    ec369(F, Y, Q)
    aggression(F, Y, Q)
    repressed(F, Y, Q)
    sweden(F, Y, Q)
    level(F, Y, Q)
    newdeal(F, Y, Q)
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
