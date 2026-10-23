"""Chapter 33 (IS–LM): every number and every quotation in zh/ch33_islm.tex.

    python3 checks/check_ch33.py

Inputs:
  islm_facts    quotations of the report of the Oxford meeting of the Econometric Society (September 1936) and the
                list of those who attended, of Hicks, 'Mr. Keynes and the "Classics"' (Econometrica, April 1937), of
                Keynes's General Theory (1936), of the Federal Reserve Bulletin (August 1936, January and February
                1937, March and May 1938), of the headnotes of Banking and Monetary Statistics 1914-1941 (1943), of
                Velde (2009), Romer (NBER Working Paper 3829), Roosevelt's press conference of 2 April 1937 and
                message of 14 April 1938 (The American Presidency Project), Eggertsson and Pugsley (2006), the Bank of
                Japan's statements of 1999 and 2001, Hansen (1939), Pigou (1943), Modigliani's Nobel biography and the
                Econometric Society's page of his article of 1944, the U.S. Treasury's page on Morgenthau, the
                authority records of the Library of Congress and the Bibliotheque nationale de France, and the terms
                of the sites used (checked by data/fetch/verify_web_quotes.py); the rows with an empty quotation are
                values and words read on page images (Hicks's equations, Hansen's pp. 2, 4 and 14, the table of
                federal finances in Historical Statistics), with a transcription between « and » in the note
  bms_member_reserves_1935_1939        member bank reserve balances, required and excess, monthly (BMS Table 105)
  bms_reserve_requirements_1917_1941   reserve requirements of member banks, per cent (BMS Table 107)
  bms_rates_1936_1940                  Treasury bills and long-term Government bonds, monthly (BMS Tables 122, 128)
  frb_g17_ip_1929_1941                 industrial production, 2017 = 100 (the Federal Reserve Board's G.17)
  depressionus_annual, bea_nipa_annual Chapter 28's and Chapter 2's annual tables: unemployment, M1, bill rate and
                                       excess reserves; real GDP and gross private investment
The figure module figsrc/fig_ch33.py imports its data and the teaching model from here.

What is checked here:
  1. readings   every number of the value column of islm_facts is read from its quotation (digits, English number
                words, 'tenfold', 'twice', 'one-half', the OCR's '331,' for 33⅓); a row read on a page image is read
                from its transcription
  2. the text   every “…” of the chapter is the chapter's rendering of a quotation (TRANSLATIONS), with the source's
                words listed in KEYWORDS (for a row read on a page image, the words of its transcription)
  3. numbers    every number of the text, section by section: said() finds the phrase and compares each number it
                prints with the value read from the snapshots or computed from the teaching model, within half a unit
                of the last printed digit; Chinese numerals are read by zh()
  4. coverage   every Arabic number of the text (outside labels, citations, cross-references, the key equations,
                math sub- and superscripts and the numbers of the parts of an example) lies inside a phrase checked
                by said()
  5. the book   the model's equations, life dates, what other chapters tell, second witnesses, the bibliography block
                of the chapter and its licence notices
  6. anchors    the paraphrase anchors `% 据: ...` name rows of islm_facts

The teaching model M2 (IS–LM, added to Chapter 32's Keynesian cross M1):
    IS:  Y = (a - cT + I0 + G - b i)/(1 - c)                                        (eq:islm-is)
    LM:  M/P = kY - h i                                                             (eq:islm-lm)
    Y* = (hA + b M/P)/(h(1 - c) + bk),  i* = (kA - (1 - c) M/P)/(h(1 - c) + bk)     (eq:islm-solution)
    with a = 26, c = 0.6 (Chapter 32), I = 14 - 2i, G = T = 0, k = 0.2, h = 4, M = 10, P = 1: Y = 90, i = 2, I = 10,
    C = 80, Chapter 32's numbers; the two equations are solved with numpy.linalg.solve. docs/PLAN.md asks for the
    parameters in checks/teaching_params.py, a shared file this chapter may not create (requested in the report).
"""
from __future__ import annotations

import datetime
import os
import re
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from check_ch32 import M1 as M1_CROSS
from common import ROOT, anchors, load_snapshot, quoted

TEX = Path(os.environ.get("CH33_TEX", ROOT / "zh" / "ch33_islm.tex"))   # a scratch copy for mutation tests
GUIDE = "一张图装下了多少凯恩斯，又丢掉了什么？"
PREV = GUIDE                                          # Chapter 32's NEXT
NEXT = "战争证明政府“付得起”，和平时期也一样吗？"       # the first half of Chapter 34's question
# Teaching inputs stated in the text (M2: IS-LM in the cloth economy of Chapters 2 and 32)
M2 = {"a": M1_CROSS["a"], "c": M1_CROSS["c"], "I0": 14, "b": 2, "G": 0, "T": 0, "k": 0.2, "h": 4, "M": 10, "P": 1}
POLICY = {"dG": 4, "dM": 4}                           # ex:islm-policy
SHOCK37 = {"dM": -2, "dG": -2}                        # ex:islm-1937 (assumed sizes; only the directions are 1937's)
SC1 = {"h": 8}                                        # self-check 1
MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"], 1)}


def chk(what: str, value, expected=None, tol: float = 1e-6, rel: float = 0.0) -> float:
    """quoted() with a tolerance for floating-point error and for the six decimals of the value column (1/3 is
    0.333333); a list is compared element by element."""
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
    df, m = load_snapshot("islm_facts", dtype=str, keep_default_na=False)
    assert 33 in m["used_in"] and m["fetch"] == "data/fetch/islm33.py"
    assert df["id"].is_unique
    return df


@lru_cache(maxsize=None)
def meta() -> dict:
    return load_snapshot("islm_facts")[1]


def facts() -> dict[str, list[float]]:
    """id -> the numbers of the value column (several are separated by ';')."""
    return {r.id: [float(x) for x in r.value.split(";")] for r in _rows().itertuples() if r.value}


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


def words_of(rid: str) -> str:
    """What a row says: its quotation, or the transcription of a page image."""
    return quotes()[rid] or transcription(rid)


def mon(rid: str, name: str) -> int:
    """The month `name` (or its abbreviation), asserted to be in what row rid says."""
    assert name.lower() in words_of(rid).lower(), (rid, name)
    key = name.lower().rstrip(".-")
    return next(i for m, i in MONTHS.items() if m.startswith(key))


def page(rid: str) -> int:
    """The first page number of a row's juan column: 'p. 148 (PDF p. 152)' -> 148."""
    return int(re.search(r"pp?\. (\d+)", column("juan")[rid]).group(1))


def issue(rid: str) -> tuple[int, int]:
    """The issue of the Federal Reserve Bulletin a row quotes, from its juan column: 'Aug. 1936, p. 613' -> (1936, 8)."""
    m = re.match(r"([A-Z][a-z]+)\.? (\d{4})", column("juan")[rid])
    return int(m.group(2)), next(i for k, i in MONTHS.items() if k.startswith(m.group(1).lower()))


def _table(name: str, fetch: str) -> tuple[pd.DataFrame, dict]:
    df, m = load_snapshot(name)
    assert 33 in m["used_in"] and m["fetch"].startswith(fetch), name
    return df, m


BMS = "data/fetch/islm33.py"


@lru_cache(maxsize=None)
def reserves() -> pd.DataFrame:
    """Member bank reserve balances, required and excess, monthly averages of daily figures, million dollars, indexed
    by (year, month); total = required + excess within 1 (the parts are rounded separately)."""
    df, _ = _table("bms_member_reserves_1935_1939", BMS)
    assert len(df) == 60 and list(df.columns) == ["year", "month", "total_m", "required_m", "excess_m"]
    assert quotes()["bms_t105u"] == "[Monthly averages of daily figures. In millions of dollars]"
    assert ((df.total_m - df.required_m - df.excess_m).abs() <= 1).all()
    return df.set_index(["year", "month"])


@lru_cache(maxsize=None)
def requirements() -> pd.DataFrame:
    """Reserve requirements, per cent: the periods in force and the four columns of Table 107."""
    df, _ = _table("bms_reserve_requirements_1917_1941", BMS)
    df = df.copy()
    df["start"], df["end"] = pd.to_datetime(df["start"]), pd.to_datetime(df["end"])
    assert (df.start.iloc[1:].values == (df.end.iloc[:-1] + pd.Timedelta(days=1)).values).all()   # no gaps
    return df


COLS = ["central_reserve_city", "reserve_city", "country", "time"]


@lru_cache(maxsize=None)
def rates() -> tuple[pd.DataFrame, pd.Series]:
    """The monthly Treasury bill and Government bond yields (per cent), indexed by (year, month), and Table 122's
    yearly averages of the bill rate; the yearly averages of 1936-1939 equal the means of the months within 0.0005."""
    df, _ = _table("bms_rates_1936_1940", BMS)
    yearly = df[df.month.isna()].set_index("year").tbill_pct
    m = df.dropna(subset=["month"]).astype({"month": int}).set_index(["year", "month"])
    assert len(m) == 60 and list(yearly.index) == list(range(1936, 1941))
    assert ((m.tbill_negative == 1) == m.tbill_pct.isna()).all()
    for y in range(1936, 1940):
        assert abs(m.loc[y].tbill_pct.mean() - yearly[y]) < 0.0005, y
    return m, yearly


@lru_cache(maxsize=None)
def ip() -> pd.Series:
    """Industrial production, total index, 2017 = 100, seasonally adjusted, indexed by (year, month)."""
    df, _ = _table("frb_g17_ip_1929_1941", "data/fetch/frb_g17_ip33.py")
    assert len(df) == 156
    return df.set_index(["year", "month"]).ip_2017_100


@lru_cache(maxsize=None)
def annual() -> pd.DataFrame:
    """Chapter 28's annual table (Historical Statistics and the Federal Reserve Bulletin), indexed by year."""
    df, m = load_snapshot("depressionus_annual")
    assert "X 414 currency plus demand deposits (M1)" in m["series"] and "D 85-86" in m["series"]
    return df.set_index("year")


@lru_cache(maxsize=None)
def nipa() -> pd.DataFrame:
    df, m = load_snapshot("bea_nipa_annual")
    assert "A191RX gdp_real_2017" in m["series"] and "A006RC gross_private_investment" in m["series"]
    return df.set_index("year")


def budget() -> pd.DataFrame:
    """Historical Statistics, Y 339-341: receipts, outlays, surplus or deficit, billion dollars, fiscal years
    1935-1941; receipts - outlays = surplus within 0.1 (each rounded separately)."""
    F = facts()
    rows = [F[f"cy_{y}"] for y in range(1935, 1942)]
    df = pd.DataFrame(rows, columns=["year", "receipts", "outlays", "surplus"]).astype({"year": int}).set_index("year")
    assert list(df.index) == list(range(1935, 1942))
    assert ((df.receipts - df.outlays - df.surplus).abs() <= 0.1 + 1e-9).all()
    return df


def Y_of(rid: str) -> int:
    """The year of a row (its year column)."""
    return years()[rid]


def fall(a: float, b: float) -> float:
    return 100 * (1 - b / a)


def rise(a: float, b: float) -> float:
    return 100 * (b / a - 1)


# ---------------------------------------------------------------------------------------------------
# The teaching model
def islm(**change: float) -> dict[str, float]:
    """The equilibrium of M2 with some parameters changed: IS (1 - c)Y + b i = A and LM kY - h i = M/P, solved as a
    linear system with numpy.linalg.solve."""
    p = {**M2, **change}
    a, c, I0, b, G, T, k, h, M, P = (p[x] for x in ("a", "c", "I0", "b", "G", "T", "k", "h", "M", "P"))
    A = a - c * T + I0 + G
    Y, i = np.linalg.solve(np.array([[1 - c, b], [k, -h]]), np.array([A, M / P]))
    den = h * (1 - c) + b * k
    return dict(Y=float(Y), i=float(i), I=I0 - b * float(i), C=a + c * (float(Y) - T), A=A, den=den,
                fiscal=h / den, monetary=b / den, cross=1 / (1 - c), is0=A / (1 - c), is1=b / (1 - c),
                lm1=k / h, lm0=M / (h * P))


def model() -> dict[str, dict[str, float]]:
    """The numbers of the examples, the figures and the self-check."""
    base = islm()
    fiscal = islm(G=M2["G"] + POLICY["dG"])
    money = islm(M=M2["M"] + POLICY["dM"])
    both = islm(M=M2["M"] + SHOCK37["dM"], G=M2["G"] + SHOCK37["dG"])
    m37 = islm(M=M2["M"] + SHOCK37["dM"])
    g37 = islm(G=M2["G"] + SHOCK37["dG"])
    sc1 = islm(h=SC1["h"])
    return dict(base=base, fiscal=fiscal, money=money, both=both, m37=m37, g37=g37, sc1=sc1)


# ---------------------------------------------------------------------------------------------------
# 1. Readings of the numbers
SMALL = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "twelve": 12}
TENS = {"ten": 10, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80,
        "ninety": 90}
MULT = {"thousand": 10 ** 3, "million": 10 ** 6, "billion": 10 ** 9, "billions": 10 ** 9}
WORDS = {"tenfold": 10, "twice": 2, "one-half": 0.5, "three-quarters of a billion": 0.75e9, "half": 0.5,
         "a third": 1 / 3}


def cardinal(s: str) -> float:
    """An English cardinal: 'three', 'sixty-eight billion', 'one billion four hundred million'."""
    total, part = 0.0, 0.0
    for w in s.lower().replace("-", " ").split():
        if w == "and":
            continue
        if w in SMALL:
            part += SMALL[w]
        elif w in TENS:
            part += TENS[w]
        elif w == "hundred":
            part = max(part, 1) * 100
        else:
            total += max(part, 1) * MULT[w]
            part = 0
    return total + part


def figure(s: str) -> float:
    """'1,400,000,000', '10.5', '.1'."""
    return float(s.replace(",", ""))


def read(word: str, how: str) -> list[float]:
    if how == "num":
        return [figure(word)]
    if how == "en":
        return [cardinal(word)]
    if how == "word":
        return [WORDS[word]]
    if how == "third":                         # '331,': the OCR's reading of 33⅓
        return [100 / 3]
    raise ValueError(how)


FIGURES = re.compile(r"\d[\d,]*(?:\.\d+)?|\.\d+")
EN, NUM = "en", "num"
# id -> [(phrase, how)], in order. A phrase 'context|word' is searched as a whole and read from `word`. Rows not
# listed are read with all the figures of the quotation.
READINGS = {
    "ox_attend_head": [("SEPTEMBER |25", NUM), ("29", NUM), ("1936", NUM)],
    "fa_tenfold": [("tenfold", "word")],
    "fb_331": [("331,", "third")],
    "fb_twice": [("twice", "word"), ("section |19", NUM)],
    "fm_14bn": [("December |24", NUM), ("1936", NUM), ("tember |11", NUM), ("1937", NUM), ("1,400,000,000", NUM)],
    "vd_bonus": [("three", EN), ("1936", NUM)],
    "rom92_steps": [("three", EN), ("1936", NUM), ("1937", NUM)],
    "ap38_desterilize": [("one billion four hundred million", EN), ("three-quarters of a billion", "word")],
    "ap38_income": [("1928", NUM), ("eighty billion", EN), ("1932", NUM), ("forty billion", EN)],
    "ap38_income37": [("1937", NUM), ("sixty-eight billion", EN)],
    "ap38_running": [("thirty-eight billions", EN), ("1932", NUM), ("sixty-eight billions", EN), ("1937", NUM),
                     ("fifty-six billions", EN)],
    "hn_half": [("one-half", "word")],
    "hk_dotted": [("Figure |2", NUM)],
    "nb_first": [("Vol. |12", NUM), ("No. |1", NUM), ("1944", NUM)],
    "es_modigliani": [("1944", NUM), ("Volume |12", NUM), ("Issue |1", NUM), ("45", NUM), ("88", NUM)],
    "loc_modigliani": [("1918", NUM), ("2003", NUM)],
}
# a page image: signed figures ('-.1'), read after the words named here
IMG_FIGURES = re.compile(r"(-?)(\d[\d,]*(?:\.\d+)?|\.\d+)")
IMG_READINGS = {"hn_population": [("16,000,000", NUM), ("half", "word"), ("a third", "word")]}
# the misreadings of the OCR, each named in the note of its row and printed in the quotation
MISPRINTS = [("hk_is", "JS"), ("hk_monetary", "JS"), ("hk_directly", "J"), ("hk_invest", "C(z)"),
             ("ox_dependent", "pz"), ("ox_dependent", "Py"), ("ox_refs", "zbid."), ("ox_attend", "Wiirzburg"),
             ("ox_attend", "Géteborg"), ("fb_331", "331,"), ("fa_deposits", "diminsh"), ("fm_apr16", "approxiimately"),
             ("fm_14bn", "FEDERAL RESERVE BULLETIN May 1938"), ("rom92_hansen", "Cordon"), ("hn_regimented", "+"),
             ("hn_few", "rdle"), ("fa_gold", "cess")]
IMAGE_NOTE = "read on the page image"


def read_rule(rid: str, text: str) -> list[float]:
    got, pos = [], 0
    for phrase, how in (READINGS.get(rid) or IMG_READINGS[rid]):
        context, _, word = phrase.rpartition("|")
        k = text.find(context + word, pos)
        assert k >= 0, f"{rid}: {phrase!r} not found (in order)"
        pos = k + len(context + word)
        got += read(word, how)
    return got


def read_image(rid: str) -> list[float]:
    text = transcription(rid)
    if rid in IMG_READINGS:
        return read_rule(rid, text)
    return [(-1 if sign else 1) * figure(num) for sign, num in IMG_FIGURES.findall(text)]


def check_readings(df: pd.DataFrame) -> None:
    src = meta()["sources"]
    n = img = 0
    for r in df.itertuples():
        assert r.file in src, (r.id, r.file)
        vals = [float(x) for x in r.value.split(";")] if r.value else []
        if src[r.file]["format"] == "image":                 # read on a page image: no quotation
            assert not r.quote and IMAGE_NOTE in r.note and r.id not in READINGS, r.id
            img += 1
            if vals:
                got = read_image(r.id)
                assert [round(g, 6) for g in got] == [round(v, 6) for v in vals], f"{r.id}: read {got}, {vals}"
            continue
        assert r.quote, f"{r.id}: no quotation"
        if not vals:
            assert r.id not in READINGS, r.id
            continue
        q = " ".join(r.quote.split())
        got = read_rule(r.id, q) if r.id in READINGS else [figure(x.rstrip(",")) for x in FIGURES.findall(q)]
        assert [round(g, 6) for g in got] == [round(v, 6) for v in vals], f"{r.id}: read {got}, value column {vals}"
        n += 1
    quoted("rows with values, each read from its quotation", n, 90)
    quoted("rows read on a page image (no quotation)", img, 21)
    N, Q = column("note"), quotes()
    for rid, word in MISPRINTS:
        assert word in N[rid], (rid, word)                  # every misreading is named in the note
        assert word in Q[rid], (rid, word)                  # and printed in the quotation
    assert "33⅓" in N["fb_331"] and "'JS' is the OCR's reading of IS" in N["hk_is"]
    assert "350 THE ECONOMIC JOURNAL [DEC," in Q["pg_vanish"] and "running head of p. 350" in N["pg_vanish"]


# ---------------------------------------------------------------------------------------------------
# 2. Every “…” of the text against the snapshot
# the chapter's Chinese renderings of the quotations: rendering -> row (or rows)
TRANSLATIONS = {
    # opening
    "凯恩斯先生的体系": "ox_first",
    "古典学派": "hk_title",
    "引起了有趣的讨论": "hk_oxford",
    "还是整件事只是一场假打？": "hk_sham",
    # sec:islm-world
    "趁这些多余的准备还没有用，先冻结其中一部分，要比让人在上面建起一座信用的大厦、再抽掉大厦的地基好得多。":
        "fa_sterilize",
    "几乎全部来自国外流入的黄金": "fa_gold",
    "这一宽松的货币政策不变，并将继续下去": "fa_easy",
    "确信这一行动不会影响眼下宽松的货币状况": "fa_19bn",
    "主要是由于个人与机构投资者手里积累了大量闲置的资金": "fa_longtime",
    "不会减少这些银行为客户持有的存款，因而也不会减少可以用于投资的资金": "fa_deposits",
    # sec:islm-hicks
    "可以看作给定的": "hk_wage",
    "惊人的结论": "hk_startling",
    "特殊理论": "hk_special",
    "财政部观点": "hk_fn4",
    "就业通论": "hk_fn4",
    "向马歇尔的正统退回了一大步": "hk_marshall",
    # sec:islm-lm
    "一起决定": "hk_together",
    "左边接近水平，右边接近垂直": "hk_shape",
    # sec:islm-trap
    "实际上绝对的": "gt_absolute",
    "这种极限的情形将来在实际中也许会变得重要，但我至今不知道有过例子": "gt_noexample",
    "不能降到很接近零": "hk_nearzero",
    "非常不可能": "hk_fn6",
    "萧条经济学": "hk_depression",
    "很惯例的": "gt_conventional",
    "在公众看来带有试验性质、或者容易改变的货币政策，可能达不到大幅压低长期利率的目的": "gt_experimental",
    "尽可能低": "bj99a_low",
    "只会让超额资金在这些机构里积得更多": "bj99b_only",
    "稳定地为零或上升": "bj01_cpi",
    # sec:islm-1937
    "将由向公众卖出等额的美国政府债券、并把买进的黄金放进财政部一个不活动的账户来抵消": "fj_inactive",
    "黄金就被挡在国家的信用基础之外": "fj_inactive",
    "联邦储备体系收紧了银行信用，财政部开始‘冻结’黄金，作为对人们所担心的可能失控的通胀的又一道刹车": "ap38_brake",
    "可是，单靠货币措施，不足以让我们开始持续的上升。": "ap38_insufficient",
    # sec:islm-debate
    "同样重要": "vd_fs544",
    "混乱的沟通": "ep_confusing",
    "我担心，我们都担心，某些主要用于耐用品的原料的涨价": "ap37_concerned",
    "钢桥与大型永久建筑这类用到某些原料的东西，那些原料的价格一涨再涨": "ap37_slow",
    "现在或将来的一切需要都是多余的": "fa_superfluous",
    "推绳子": "vd_string",
    "多余": "fa_superfluous",
    "合理可行、符合公众利益、出于坚定的信念，又由一个不大可能被撤换的当局推行": "gt_successful",
    # sec:islm-hansen
    "单靠低利率的充裕可贷资金，就足以带来旺盛的实际投资": "hn_few",
    "停止": "hn_cessation",
    "病态的复苏": "hn_sick",
    "危险也就在这里": "hn_easiest",
    "1928 年的国民收入是 800 亿美元，1932 年已经降到不足 400 亿美元": "ap38_income",
    "我们公民的收入总额已经升到 680 亿美元": "ap38_income37",
    "否认的对，肯定的错": "pg_right",
    "总是可能的": "pg_possible",
    "基本上也是我的博士论文": "nb_first",
    "革命": "nb_integrate",
    # 史料说明
    "JS": "hk_is",
    "从 7 月的高点": "vd_julypeak",
    # sec:islm-legacy
    "粗糙": "hk_rough",
    "但它既不是动态经济学的开端，也不是它的终结": "hk_end",
    "骨架": "hk_skeleton",
}
# the words of the source that each rendering translates
KEYWORDS = {
    "ox_first": ["Mr. Keynes' System."],
    "hk_title": ['"CLASSICS"'],
    "hk_oxford": ["called forth an interesting discussion"],
    "hk_sham": ["or is the whole thing a sham fight?"],
    "fa_sterilize": ["It is far better to sterilize a part of these superfluous reserves while they are still unused",
                     "a credit structure to be erected upon them and then to withdraw the foundation of the structure"],
    "fa_gold": ["almost entirely from the inflow of gold from abroad"],
    "fa_easy": ["This easy money policy remains unchanged and will be continued."],
    "fa_19bn": ["the Board is convinced that this action will not affect easy money conditions now prevailing"],
    "fa_longtime": ["has been due principally to the large accumulations of idle funds in the hands of individual and "
                    "institutional investors"],
    "fa_deposits": ["will not diminsh the volume of deposits held by these banks for their customers and will, "
                    "therefore, not diminish the volume of funds available for investment"],
    "gt_experimental": ["a monetary policy which strikes public opinion as being experimental in character or easily "
                        "liable to change may fail in its objective of greatly reducing the long-term rate of interest"],
    "gt_successful": ["reasonable and practicable and in the public interest, rooted in strong conviction, and promoted "
                      "by an authority unlikely to be superseded"],
    "ap37_slow": ["steel bridges and great permanent structures that use certain materials, the prices of which are "
                  "going up and up and up"],
    "hn_few": ["an abundance of loanable funds at low rates of interest is alone adequate to produce a vigorous flow of "
               "real investment"],
    "ap38_income": ["In 1928 the national income was eighty billion dollars; in 1932 it had fallen to less than forty "
                    "billion dollars."],
    "ap38_income37": ["the total of our citizens' income had risen to sixty-eight billion dollars"],
    "pg_possible": ["is always possible"],
    "nb_first": ["which is also, substantially, my doctoral dissertation"],
    "hk_wage": ["can be taken as given"],
    "hk_startling": ["the startling conclusion"],
    "hk_special": ["Mr. Keynes' special theory"],
    "hk_fn4": ['"Treasury View."', 'Liquidity Preference transports us from the "Treasury View" to the "General Theory '
               'of Employment."'],
    "hk_marshall": ["takes a big step back to Marshallian orthodoxy"],
    "hk_together": ["They are determined together"],
    "hk_shape": ["nearly horizontal on the left, and nearly vertical on the right"],
    "gt_absolute": ["virtually absolute"],
    "gt_noexample": ["But whilst this limiting case might become practically important in future, I know of no "
                     "example of it hitherto."],
    "hk_nearzero": ["cannot fall very near zero"],
    "hk_fn6": ["but it is very unlikely"],
    "hk_depression": ["the Economics of Depression"],
    "gt_conventional": ["a highly conventional"],
    "bj99a_low": ["as low as possible"],
    "bj99b_only": ["would only result in further accumulation of excess funds at institutions such as Tanshi companies"],
    "bj01_cpi": ["registers stably a zero percent or an increase year on year"],
    "fj_inactive": ["will be offset by the sale to the public of an equivalent amount of United States Government "
                    "obligations and by the setting aside of the purchased gold in an inactive account in the Treasury",
                    "In this way the gold will be kept out of the country's credit base."],
    "ap38_brake": ['The Federal Reserve System curtailed banking credit, and the Treasury commenced to "sterilize" gold '
                   "as a further brake on what it was feared might turn into a runaway inflation."],
    "ap38_insufficient": ["By themselves, however, monetary measures are insufficient to start us on a sustained "
                          "upward movement."],
    "vd_fs544": ['"no less important,"'],
    "ep_confusing": ["confusing communications"],
    "ap37_concerned": ["I am concerned-we are all concerned- over the price rise in certain materials that go into "
                       "durable goods primarily."],
    "vd_string": ['"pushing on a string"'],
    "fa_superfluous": ["is superfluous for all present or prospective needs of commerce, industry, and agriculture"],
    "hn_cessation": ["It is the cessation of growth"],
    "hn_sick": ["sick recoveries"],
    "pg_right": ["right in what he denies but wrong in what he affirms"],
    "hn_easiest": ["therein lies its danger"],
    "nb_integrate": ['the Keynesian "revolution"'],
    "hk_is": ["The curve JS"],
    "vd_julypeak": ["From its peak in July 1937"],
    "hk_rough": ["a terribly rough and ready sort of affair"],
    "hk_end": ["but it is neither the beginning nor the end of Dynamic Economics."],
    "hk_skeleton": ["our skeleton apparatus"],
}


def tex_text() -> str:
    return "\n".join(l for l in TEX.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("%"))


def text_quotations() -> list[str]:
    """The “…” of the text; the closing question is Chapter 34's (checked by ending())."""
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 34's question"
    return re.findall(r"“([^”]*)”", t[:-len(NEXT)])


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
    stale = set(TRANSLATIONS) - used
    assert not stale, f"listed but not in the text: {sorted(stale)}"
    for rid, words in KEYWORDS.items():
        for w in words:
            assert w in words_of(rid), f"{rid}: {w!r} not in the quotation"
    assert set(KEYWORDS) == {r for t in TRANSLATIONS.values() for r in ((t,) if isinstance(t, str) else t)}
    img = sorted(r for r in KEYWORDS if not quotes()[r])
    print(f"ok {n} quotations of the text found in the snapshot ({len(img)} rows by their transcriptions)")


# ---------------------------------------------------------------------------------------------------
# 3. Numbers: said() and the parts of the text it does not read
UNITS = {"万亿": 10 ** 12, "亿": 10 ** 8, "万": 10 ** 4}
AMOUNT = re.compile(r"(\d[\d,]*(?:\.\d+)?)(?:\s*(万亿|亿|万))?")
# what is not a number of the story: labels, citations, cross-references, the key equations (models() reads them),
# the sub- and superscripts of the math and the numbers of the parts of an example
MASKS = [re.compile(r"\\begin\{keyeq\}.*?\\end\{keyeq\}", re.DOTALL),
         re.compile(r"\\(?:label|cite|chref|secref|figref|tabref|exref|eqref|ref|nameref|url|fig)\{[^}]*\}"),
         re.compile(r"_\{[^}]*\}|_\d"),
         re.compile(r"\^\{\d\}"),
         re.compile(r"（\d）"),
         re.compile(r"\{(?:fig|tab):[^}]*\}|\\multicolumn\{\d+\}"),             # the label of a figure, column spans
         re.compile(r"\\begin\{tabularx\}\{\\linewidth\}\{[^\n]*")]                # the column widths of the tables
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
    """The phrase is in the text, and each number it prints (with its unit 万, 亿, 万亿) is the value given, within half
    a unit of its last digit (plus `slack`, in the same units). None skips a number (one checked by an assertion)."""
    say(phrase)
    found = AMOUNT.findall(mask(phrase))
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
    """A Chinese numeral of the text: '六', '十五', '三分之一', '一半', '七成' (seven tenths, as a per cent: 70)."""
    if "分之" in s:
        b, a = s.split("分之")
        return zh(a) / zh(b)
    if s.endswith("成"):
        return 10 * zh(s[:-1])
    if s.endswith("半"):                                                       # '一半': one half
        return 0.5 * (zh(s[:-1]) if s[:-1] else 1)
    total, part = 0, 0
    for ch in s:
        if ch in ZH_DIGITS:
            part = ZH_DIGITS[ch]
        else:
            total += max(part, 1) * ZH_UNITS[ch]
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


def paragraph(start: str) -> str:
    """The paragraph of the text that contains `start`, from `start` to its end."""
    t = tex_text()
    return t[t.index(start):].split("\n")[0]


# ---------------------------------------------------------------------------------------------------
# 4. Numbers, section by section
def ip_peak() -> dict[str, float]:
    """The peak of 1937 and the trough of 1938 in the G.17 index, and the falls from May and from July 1937."""
    s = ip()
    peak, trough = s.loc[1937].idxmax(), s.loc[1938].idxmin()
    rec = s.loc[(1933, 1):(1937, 12)]
    assert rec.idxmax() == (1937, peak)                                       # the high of the recovery
    assert s.loc[(1937, peak):(1939, 12)].idxmin() == (1938, trough)
    return dict(peak=peak, trough=trough, fall=fall(s[(1937, peak)], s[(1938, trough)]),
                fall7=fall(s[(1937, 7)], s[(1938, trough)]))


def guide(F, Y, Q):
    t = TEX.read_text(encoding="utf-8")
    assert f"\\guidequestion{{{GUIDE}}}" in t and GUIDE == PREV
    ch32 = (ROOT / "zh" / "ch32_generaltheory.tex").read_text(encoding="utf-8")
    ch32 = "\n".join(l for l in ch32.splitlines() if not l.lstrip().startswith("%"))
    assert ch32.rstrip().endswith(PREV)                                       # 第 32 章交来的问题
    for label in ("ch:generaltheory", "ch:depressionus"):                      # the prerequisites (PLAN: 32, 28)
        assert f"\\chref{{{label}}}\\enspace\\nameref{{{label}}}" in t, label
    m, _ = rates()
    said("用 1936—1940 年美国的利率与准备金核对", m.index[0][0], m.index[-1][0])
    said("用这张图读 1937—1938 年美国的衰退", 1937, 1938)
    said("概括汉森（1939）的长期停滞论与庇古（1943）的回答", Y["hn_title"], Y["pg_masthead"])
    assert "MARCH" in meta()["sources"]["hansen1939"]["version"].upper()


def opening(F, Y, Q):
    d25, d29, y36 = F["ox_report"][:3]
    d26 = F["ox_first"][0]
    said("1936 年 9 月 26 日是个星期六", y36, mon("ox_report", "SEPTEMBER"), d26)
    assert datetime.date(int(y36), 9, int(d26)).weekday() == 5 and "on Saturday morning the 26th" in Q["ox_first"]
    assert "THE SIXTH EUROPEAN MEETING" in Q["ox_report"] and "New College, Oxford" in Q["ox_report"]
    chk("    the sixth European meeting (第六次)", 6, told("计量经济学会的第六次欧洲会议", "第", "次"))
    said("会期从 25 日到 29 日", d25, d29)
    assert "The first session" in Q["ox_first"]
    chk("    the first session (第一场)", 1, told("这天上午的第一场讨论会", "第", "场"))
    assert Q["ox_meade"].startswith("Mr. J. E. Meade") and "A Simplified Model of Mr. Keynes' System." in Q["ox_meade"]
    assert "only two industries, one making consumption goods and the other capital goods" in Q["ox_closed"]
    chk("    two industries (两个产业)", 2, told("只有两个产业", "只有", "个产业"))
    dep = re.search(r"and (.*?), and N are dependent", Q["ox_dependent"]).group(1).split(", ") + ["N"]
    assert "M, w, and s are regarded as independent variables" in Q["ox_dependent"]
    assert "given the quantity of money, the money wage-rate, and the proportion of income saved" in Q["ox_dependent"]
    chk("    eight dependent variables (其余八个变量)", len(dep), told("其余八个变量都由模型决定", "其余", "个变量"))
    names = [x.strip() for x in Q["ox_attend"].split(":", 1)[1].split(";")]
    said("出席会议的共 62 人", len(names))
    assert not any("Keynes" in x for x in names)                              # 名单上没有凯恩斯本人
    for who in ("J. E. Meade, Oxford", "R. F. Harrod, Oxford", "J. R. Hicks, Cambridge", "Dr. J. Tinbergen, Geneva",
                "Prof. Ragnar Frisch, Oslo"):
        assert who in names, who
    assert "Contributions to the symposium by R. F. Harrod" in Q["ox_published"]
    said("希克斯的文章 1937 年 4 月发表", F["ox_refs"][5], mon("ox_refs", "Apr."))
    assert F["ox_refs"][6:] == [page("hk_title"), page("hk_end")]              # pp. 147-159
    assert "Oxford meeting of the Econometric Society (September, 1936)" in Q["hk_oxford"]
    assert "three fundamental equations" in transcription("hk_classical")
    chk("    three equations (三个方程)", 3, told("他把两边都写成三个方程", "写成", "个方程"))
    chk("    two curves (两条曲线)", 2, told("再把方程画成两条曲线", "画成", "条曲线"))
    assert "the curves LL and IS" in Q["hk_together"]
    assert paragraph("希克斯开头就说").endswith(GUIDE)                          # the opening ends with the question


def world(F, Y, Q):
    d14, _ = F["fa_decided"]
    p50, d15, y36 = F["fa_raise"]
    said("1936 年 7 月 14 日，联邦储备委员会决定把会员银行的法定准备金率提高 50\\%，8 月 15 日营业结束后生效", y36,
         mon("fa_decided", "July"), d14, p50, mon("fa_raise", "August"), d15)
    assert "after the close of business" in Q["fa_raise"]
    said("当时的超额准备约有 30 亿美元", F["fa_3bn"][0])
    assert "almost entirely from the inflow of gold from abroad" in Q["fa_gold"]
    assert "the System’s policy of encouraging full recovery" in Q["fa_gold"]                  # 用宽松的货币状况鼓励全面的复苏
    chk("    tenfold (十倍)", F["fa_tenfold"][0], told("十倍甚至更大的信用扩张", "", "倍"))
    assert "injurious credit expansion" in Q["fa_tenfold"]
    y, p84, p126, _, _, r12, r8 = F["fa_84"]
    said("1936 年 3 月，会员银行的法定准备平均是存款的 8.4\\%，每 1 美元法定准备支撑约 12 美元存款", y,
         mon("fa_84", "March"), p84, 1, r12)
    said("新规定生效以后，这个比例约为 12.6\\%，每 1 美元只能支撑 8 美元", p126, 1, r8)
    chk("    $1 of reserves supports about $12 (100/8.4)", 100 / p84, r12, tol=0.5)
    chk("    and $8 (100/12.6)", 100 / p126, r8, tol=0.5)
    chk("    12.6/8.4 = 1.5, the increase by 50 per cent", p126 / p84, 1 + p50 / 100, tol=1e-9)
    assert F["fa_ratio"] == [r12, 1, r8, 1]
    said("委员会估计，提高以后会员银行仍有约 19 亿美元的超额准备", F["fa_19bn"][0])
    m, yearly = rates()
    b36 = m.loc[1936].govt_bond_pct
    said("按联邦储备委员会 1943 年编的《银行与货币统计》，1936 年新发行的国库券平均收益率只有 0.14\\%，长期政府债券的收益率在 "
         "2.5\\% 到 2.8\\% 之间", Y["bms_t105"], 1936, yearly[1936], b36.min(), b36.max())
    assert "average rate on new issues" in Q["bms_bills"]
    twelve = cardinal(re.search(r"callable after (\w+) years\.", Q["bms_bonddef"]).group(1))
    said("这里的长期政府债券，指 12 年以后才到期或可赎回的部分免税联邦政府债券", twelve)
    assert "unweighted averages of yields of all outstanding partially tax-exempt Government bonds" in Q["bms_bonddef"]
    assert "idle funds in the hands of individual and institutional investors" in Q["fa_longtime"]
    said("复苏还没有完成，1936 年的失业率仍有 16.9\\%", 1936, annual().loc[1936, "unemployment_pct"])


def hicks(F, Y, Q):
    assert "in two ways" in Q["hk_differ"]
    chk("    two differences (两处不同)", 2, told("两处不同。", "", "处不同"))
    said("$1/k$相当于", 1)
    # the three systems of equations, as the page images print them
    systems = {"hk_classical": "M = kI, Ix = C(i), Ix = S(i, I)", "hk_special_eq": "M = L(i), Ix = C(i), Ix = S(I)",
               "hk_fn4": "M = kI, Ix = C(i), Ix = S(I)", "hk_general_eq": "M = L(I, i), Ix = C(i), Ix = S(I)"}
    for rid, eqs in systems.items():
        assert eqs in transcription(rid), rid
        say("，".join("$" + e.replace(" ", "").replace("Ix", "I_x") + "$" for e in re.split(r", (?=Ix)", eqs)))
    assert "M = L(i), Ix = C(i), Ix = S(I)" in transcription("hk_special_eq")
    assert "the speculative motive" in Q["hk_transactions"].replace('"', "")


def is_curve(F, Y, Q):
    M = model()["base"]
    a, c, I0, b = M2["a"], M2["c"], M2["I0"], M2["b"]
    said("斜率是$-(1-c)/b$", 1)
    said("平移的距离是支出的变化乘以\\chref{ch:generaltheory}的乘数$1/(1-c)$", 1, 1)
    said("接\\exref{ex:generaltheory-cross}的数，$a=26$，$c=0.6$，$G=T=0$。设投资$I=14-2i$", a, c, M2["G"], I0, b)
    i_q, i_0 = 2, 0
    said("（2）利率为 2\\% 时", i_q)
    said("（3）利率降到 0 呢？", i_0)
    said("（1）$Y=(26+14-2i)/(1-0.6)=100-5i$", a, I0, b, 1, c, M["is0"], M["is1"])
    Yq, Iq = M["is0"] - M["is1"] * i_q, I0 - b * i_q
    said("（2）$I=14-2\\times2=10$，$Y=100-5\\times2=90$，消费$26+0.6\\times90=80$", I0, b, i_q, Iq, M["is0"], M["is1"],
         i_q, Yq, a, c, Yq, a + c * Yq)
    chk("    the cross of Chapter 32: investment 10, income 90, consumption 80", [Iq, Yq, a + c * Yq],
        [M1_CROSS["I"], 90, 80])
    said("（3）$I=14$，$Y=100$。\\chref{ch:generaltheory}里投资从 10 增加到 14，在这里相当于利率从 2\\% 降到 0", I0,
         M["is0"], M1_CROSS["I"], M1_CROSS["I2"], i_q, i_0)
    assert I0 - b * i_0 == M1_CROSS["I2"]
    # Tinbergen and Frisch at Oxford
    assert Q["ox_afternoon"].startswith("On Saturday afternoon") and Q["ox_tinbergen"].startswith("At the same session")
    said("用约 12 个方程描述战后美国经济周期的尝试", F["ox_twelve"][0])
    assert "American cycles after the war" in Q["ox_twelve"]
    assert "the influence of interest rates on the volume of investment activity seems to have been very small" in Q["ox_interest"]
    ten, fifteen = F["ox_frisch"]
    chk("    ten to fifteen systems (十到十五个)", [told("已经有十到十五个说得通的数学体系", "已经有", "到"),
                                          told("已经有十到十五个说得通的数学体系", "到", "个")], [ten, fifteen])
    assert "to test different systems against the facts" in Q["ox_frisch"]


def lm(F, Y, Q):
    M = model()["base"]
    k, h, Mn, P = M2["k"], M2["h"], M2["M"], M2["P"]
    assert "slope upwards" in Q["hk_slope"]
    said("接\\exref{ex:islm-is}，设$k=0.2$，$h=4$，$M=10$，$P=1$", k, h, Mn, P)
    said("（1）$10=0.2Y-4i$，即$i=0.05Y-2.5$", Mn, k, h, M["lm1"], M["lm0"])
    said("（2）代入 IS 曲线$Y=100-5i$，得$Y=100-5(0.05Y-2.5)$，$1.25Y=112.5$，$Y=90$，$i=0.05\\times90-2.5=2$", M["is0"],
         M["is1"], M["is0"], M["is1"], M["lm1"], M["lm0"], 1 + M["is1"] * M["lm1"], M["is0"] + M["is1"] * M["lm0"], M["Y"],
         M["lm1"], M["Y"], M["lm0"], M["i"])
    A, c, b = M["A"], M2["c"], M2["b"]
    said("（3）$A=40$，分母$4\\times0.4+2\\times0.2=2$，$Y^{*}=(4\\times40+2\\times10)/2=90$，$i^{*}=(0.2\\times40-0.4"
         "\\times10)/2=2$", A, h, 1 - c, b, k, M["den"], h, A, b, Mn, M["den"], (h * A + b * Mn / P) / M["den"], k, A,
         1 - c, Mn, M["den"], (k * A - (1 - c) * Mn / P) / M["den"])
    chk("    eq:islm-solution against linalg.solve: Y*", (h * A + b * Mn / P) / M["den"], M["Y"], tol=1e-9)
    chk("    i*", (k * A - (1 - c) * Mn / P) / M["den"], M["i"], tol=1e-9)
    assert "nearly horizontal on the left" in Q["hk_shape"]
    # fig:islm_curves
    Mf, Mm = model()["fiscal"], model()["money"]
    cross_Y = M["Y"] + M["cross"] * POLICY["dG"]                              # the cross at an unchanged rate
    said("(a) IS 曲线$Y=100-5i$与 LM 曲线$i=0.05Y-2.5$交于收入 90、利率 2\\%", M["is0"], M["is1"], M["lm1"], M["lm0"],
         M["Y"], M["i"])
    said("(b) 政府支出增加 4，IS 右移，收入增加 8、利率升到 2.4\\%；货币增加 4，LM 右移，收入增加 4、利率降到 1.2\\%",
         POLICY["dG"], Mf["Y"] - M["Y"], Mf["i"], POLICY["dM"], Mm["Y"] - M["Y"], Mm["i"])
    said("虚线是凯恩斯交叉在利率不变时给出的收入 100", cross_Y)


def policy(F, Y, Q):
    M, Mf, Mm = model()["base"], model()["fiscal"], model()["money"]
    said("\\frac{\\Delta Y}{\\Delta G}=\\frac{h}{h(1-c)+bk},\\qquad \\frac{\\Delta Y}{\\Delta (M/P)}=\\frac{b}{h(1-c)+bk}",
         1, 1)
    said("与凯恩斯交叉的乘数$1/(1-c)$相比", 1, 1)
    said("（1）政府支出$G$从 0 增加到 4。（2）货币数量$M$从 10 增加到 14", M2["G"], M2["G"] + POLICY["dG"], M2["M"],
         M2["M"] + POLICY["dM"])
    dG, dM = POLICY["dG"], POLICY["dM"]
    crowd = (M["I"] - Mf["I"]) * M["cross"]
    said("（1）IS 变成$Y=110-5i$，与 LM 联立得$Y=98$，$i=2.4$，$I=14-2\\times2.4=9.2$。财政乘数是$8/4=2$。凯恩斯交叉给的是"
         "$2.5\\times4=10$，少了的 2，是投资减少 0.8 再乘以 2.5", Mf["is0"], Mf["is1"], Mf["Y"], Mf["i"], M2["I0"], M2["b"],
         Mf["i"], Mf["I"], Mf["Y"] - M["Y"], dG, (Mf["Y"] - M["Y"]) / dG, M["cross"], dG, M["cross"] * dG,
         M["cross"] * dG - (Mf["Y"] - M["Y"]), M["I"] - Mf["I"], M["cross"])
    chk("    the crowding out: 0.8 x 2.5 = 10 - 8", crowd, M["cross"] * dG - (Mf["Y"] - M["Y"]), tol=1e-9)
    said("（2）LM 变成$14=0.2Y-4i$，即$i=0.05Y-3.5$，与$Y=100-5i$联立得$Y=94$，$i=1.2$，$I=14-2\\times1.2=11.6$。货币乘数是"
         "$4/4=1$。用两个乘数的公式验算，分母是 2，$h/2=2$，$b/2=1$", M2["M"] + dM, M2["k"], M2["h"], Mm["lm1"], Mm["lm0"],
         M["is0"], M["is1"], Mm["Y"], Mm["i"], M2["I0"], M2["b"], Mm["i"], Mm["I"], Mm["Y"] - M["Y"], dM,
         (Mm["Y"] - M["Y"]) / dM, M["den"], M["den"], M["fiscal"], M["den"], M["monetary"])
    chk("    the fiscal multiplier of the formula", M["fiscal"], (Mf["Y"] - M["Y"]) / dG, tol=1e-9)
    chk("    the monetary multiplier of the formula", M["monetary"], (Mm["Y"] - M["Y"]) / dM, tol=1e-9)
    said("\\cmprow{\\exref{ex:islm-policy}的数}{$G$增加 4，收入增加 8}{$M$增加 4，收入增加 4}", dG, Mf["Y"] - M["Y"], dM,
         Mm["Y"] - M["Y"])
    said("\\cmprow{陷阱里，$h\\to\\infty$}{乘数趋于$1/(1-c)=2.5$，没有挤出}{乘数趋于 0}", 1, 1, M["cross"], 0)
    said("\\cmprow{投资不看利率，$b\\to0$}{乘数趋于$1/(1-c)$}{乘数趋于 0}", 0, 1, 1, 0)
    said("\\cmprow{LM 垂直，$h\\to0$}{乘数趋于 0，全部挤出}{乘数趋于$1/k=5$，古典的情形}", 0, 0, 1, 1 / M2["k"])


def trap(F, Y, Q):
    M = model()
    said("货币乘数$b/[h(1-c)+bk]$趋于 0，财政乘数$h/[h(1-c)+bk]$趋于$1/(1-c)$", 1, 0, 1, 1, 1)
    assert "the horizontal parts of the curve are almost the same" in Q["hk_dotted"]
    # fig:islm_trap (b)
    assert M["m37"]["i"] > M["base"]["i"] > M["g37"]["i"]
    said("(b) 1937 年的两种冲击在教学模型里的方向：货币减少 2，LM 左移，利率上升；政府支出减少 2，IS 左移，利率下降", 1937,
         -SHOCK37["dM"], -SHOCK37["dG"])
    m, yearly = rates()
    said("1930 年代末的美国，利率的样子与这幅图相合", 1930)
    said("新发行国库券的平均收益率 1937 年约 0.45\\%，1938 年与 1939 年都不到 0.1\\%", 1937, yearly[1937], 1938, 1939, None)
    assert max(yearly[1938], yearly[1939]) < 0.1
    neg = m[m.tbill_negative == 1]
    assert set(neg.index.get_level_values(0)) == {1940} and len(neg) >= 2 and Q["bms_negative"] == "Negative yield."
    said("1940 年有几个月是负收益", 1940)
    bond = m.loc[1936:1939].govt_bond_pct
    low = bond.idxmin()
    below = m[m.govt_bond_pct < 2].index[0]
    said("长期政府债券的收益率却在 1936—1939 年一直高于 2\\%，最低是 1939 年 6 月的 2.1\\%，到 1940 年 11 月才降到 2\\% 以下",
         1936, 1939, None, low[0], low[1], bond.min(), below[0], below[1], 2)
    assert bond.min() > 2
    ex = reserves().excess_m
    top = ex.idxmax()
    said("会员银行的超额准备在 1939 年 10 月达到约 55 亿美元", top[0], top[1], ex[top] * 1e6)
    said("短期利率到了零附近，长期利率好几年停在 2\\% 以上", 2)
    # the pitfall
    b3839 = m.loc[1938:1939]
    assert b3839.govt_bond_pct.min() > 2 and max(yearly[1938], yearly[1939]) < 0.06
    said("1938—1939 年的美国，国库券收益率接近零，长期政府债券的收益率仍在 2\\% 以上", 1938, 1939, 2)
    said("日本银行 1999 年说的又是另一种机制", Y["bj99b_title"])
    assert "70 to 80 percent of excess funds" in Q["bj99b_tanshi"]
    # the case box: Japan 1999-2001
    said("\\begin{case}{日本 · 1999—2001 · 流动性陷阱的回声}", Y["bj99a_title"], Y["bj01_title"])
    d12, y99 = F["bj99a_title"]
    said("1999 年 2 月 12 日，日本银行的政策委员会以多数票决定", y99, mon("bj99a_title", "February"), d12)
    assert Q["bj99a_vote"].startswith("By majority vote, the Policy Board")
    assert "Masaru Hayami ( Chairman, Governor )" in Q["bj99a_hayami"]
    said("拆借利率先引导到 0.15\\% 左右", F["bj99a_015"][0])
    d21, _ = F["bj99b_title"]
    said("同年 9 月 21 日，日本银行决定继续实行零利率政策", mon("bj99b_title", "September"), d21)
    tn, _ = F["bj99b_trillion"]
    said("它供给的资金比法定准备多出约 1 万亿日元", tn * 1e12)
    assert "1 trillion yen more than the required reserve" in Q["bj99b_trillion"]
    lo, hi = F["bj99b_tanshi"]
    chk("    70 to 80 per cent (七成到八成)", [told("七成到八成积在短资公司那里", "", "到"),
                                      told("七成到八成积在短资公司那里", "到", "积在")], [lo, hi])
    d19, y01 = F["bj01_title"]
    five, one, four, _ = F["bj01_5tn"]
    said("2001 年 3 月 19 日，日本银行把操作目标从拆借利率改为金融机构在它那里的经常账户余额，暂定增加到 5 万亿日元左右，比 2 月的"
         "平均余额 4 万亿日元多 1 万亿", y01, mon("bj01_title", "March"), d19, five * 1e12, mon("bj01_5tn", "February"),
         four * 1e12, one * 1e12)
    chk("    5 = 4 + 1 trillion yen", five, four + one)
    assert "the past decade" in Q["bj01_decade"]
    chk("    the past decade (过去十年)", 10, told("声明回顾说，过去十年", "过去", "年"))


def recession(F, Y, Q):
    P = ip_peak()
    s = ip()
    said("\\section{1937—1938 年的衰退}", 1937, 1938)
    said("\\caption{1936—1938 年美国的主要货币与财政措施}", Y["fa_decided"], Y["ap38_title"])
    said("1937 年 5 月，美国的工业生产到了复苏以来的高点", 1937, P["peak"])
    chk("    about a third (约三分之一)", P["fall"] / 100, told("一年以后少了约三分之一", "约", ""), tol=0.02)
    chk("    a year later (一年以后): May 1937 to May 1938, months", 12 * (1938 - 1937) + P["trough"] - P["peak"], 12)
    said("1937 年 5 月到 1938 年 5 月，产量下降了 32.5\\%", 1937, P["peak"], 1938, P["trough"], P["fall"])
    A = annual()
    said("失业率从 1937 年的 14.3\\% 升到 1938 年的 19.0\\%", 1937, A.loc[1937, "unemployment_pct"], 1938,
         A.loc[1938, "unemployment_pct"])
    u37, u38 = A.loc[1937, "unemployed_thousands"] * 1e3, A.loc[1938, "unemployed_thousands"] * 1e3
    said("失业的人从 770 万增加到 1,039 万，多了约 269 万", u37, u38, u38 - u37)
    N = nipa()
    said("1938 年的实际 GDP 比上一年少了 3.3\\%，私人总投资按当年价格少了 38.7\\%", 1938,
         -rise(N.loc[1937, "gdp_real_2017"], N.loc[1938, "gdp_real_2017"]),
         -rise(N.loc[1937, "gross_private_investment"], N.loc[1938, "gross_private_investment"]))
    said("照 Velde（2009）的比较，工业生产收缩的速度比大萧条时还快", Y["vd_conclusion"])
    # the measures
    y, s19 = F["fb_twice"]
    assert "not more than twice the amount prescribed" in Q["fb_twice"]
    said("1936—1937 年，联邦储备委员会两次提高法定准备金率", Y["fa_decided"], Y["fb_jan30"])
    chk("    two increases (两次)", 2, told("联邦储备委员会两次提高法定准备金率", "委员会", "次提高"))
    chk("    twice (两倍)", y, told("即联邦储备法规定的两倍", "规定的", "倍"))
    R = requirements()
    for col in COLS:
        assert R.iloc[3][col] == 2 * R.iloc[0][col], col                       # the ceiling reached in May 1937
    d21 = F["fj_dec21"][0]
    said("1936 年 12 月 21 日，财政部长摩根索", Y["fj_dec21"], mon("fj_dec21", "December"), d21)
    assert "the Secretary of the Treasury announced" in Q["fj_dec21"]
    said("从 24 日起，新增黄金对准备金的影响", F["fb_dec24"][0])
    assert "an inactive account in the Treasury" in Q["fj_inactive"]
    d24, y36, d11, y37, bn14 = F["fm_14bn"]
    said("到 1937 年 9 月 11 日，这个账户里的黄金积到约 14 亿美元", y37, mon("fm_14bn", "Sep-"), d11, bn14)
    assert d24 == F["fb_dec24"][0] and y36 == F["fb_dec24"][1]
    table_1937(F, Y, Q)
    # Table 107
    chk("    three classes of member banks (三类)", 3, told("\\tabref{tab:islm-reserves}是三类会员银行", "是", "类"))
    r37 = R.iloc[3]
    said("1937 年 5 月以后，活期存款的准备金率分别是 26\\%、20\\% 与 14\\%，是 1936 年 8 月以前的两倍", 1937,
         r37.start.month, r37.central_reserve_city, r37.reserve_city, r37.country, R.iloc[0].end.year, R.iloc[0].end.month)
    chk("    twice (两倍)", r37.country / R.iloc[0].country, told("是 1936 年 8 月以前的两倍", "以前的", "倍"))
    table_reserves(F, Y, Q)
    ex = reserves().excess_m
    said("超额准备 1936 年 7 月约 29 亿美元，1937 年 8 月降到约 7.5 亿美元", 1936, 7, ex[(1936, 7)] * 1e6, 1937, 8,
         ex[(1937, 8)] * 1e6)
    assert ex.loc[1937].idxmin() == 8
    said("1938 年 4 月准备金率降低以后，它在 6 月回到约 28 亿美元，1939 年 12 月约 50 亿美元", 1938, 4, 6,
         ex[(1938, 6)] * 1e6, 1939, 12, ex[(1939, 12)] * 1e6)
    # 超额准备减少的那几个月，正是工业生产到顶、开始下滑的时候
    assert ex[(1937, 2)] > ex[(1937, 5)] > ex[(1937, 8)] and 2 < P["peak"] < 8 and s[(1937, 9)] < s[(1937, 8)]
    # fig:islm_1937
    g17 = int(re.search(r"G\.(\d+) ", load_snapshot("frb_g17_ip_1929_1941")[1]["source"]).group(1))
    retrieved = load_snapshot("frb_g17_ip_1929_1941")[1]["retrieved"]
    nos = [int(re.search(r"NO\. (\d+)", Q[r]).group(1)) for r in ("bms_t105", "bms_t107", "bms_t122", "bms_t128")]
    said("1935—1939 年的美国。(a) 会员银行的法定准备与超额准备", reserves().index[0][0], reserves().index[-1][0])
    said("(b) 工业生产指数，2017 年 = 100，季节调整；1937 年 5 月是高点，1938 年 5 月是低点", 2017, 100, 1937, P["peak"],
         1938, P["trough"])
    said("数据：《银行与货币统计》表 105、107、122 与 128；联邦储备委员会 G.17 工业生产指数（2026 年 10 月的版本）", *nos,
         g17, int(retrieved[:4]), int(retrieved[5:7]))
    # the budget
    B = budget()
    assert "For years ending June 30" in transcription("cy_head") and "consolidated cash statement" in transcription("cy_head")
    said("联邦政府的赤字在 1936 财政年度是 35 亿美元，1938 财政年度只有 1 亿美元", 1936, -B.surplus[1936] * 1e9, 1938,
         -B.surplus[1938] * 1e9)
    said("财政年度到 6 月 30 日为止", 6, 30)
    said("这两年里，收入从 42 亿美元增加到 70 亿美元", B.receipts[1936] * 1e9, B.receipts[1938] * 1e9)
    said("支出则从 76 亿美元降到 72 亿美元", B.outlays[1936] * 1e9, B.outlays[1938] * 1e9)
    p66, y1, y2, y3 = F["vd_income"]
    said("照 Velde（2009）的分析，收入增加最主要的原因是 1936 年 6 月的税法大幅提高了所得税率，所得税收入 1936—1937 年增加了 66\\%",
         Y["vd_conclusion"], y3, mon("vd_income", "June"), y1, y2, p66)
    assert "The most important one is the increase in income tax revenue" in Q["vd_income"]
    two, _, y37, p105, _ = F["vd_ss"]
    said("其次是 1937 年 1 月开始征收的社会保障税，它占当年联邦税收的 10.5\\%", y37, mon("vd_ss", "January"), p105)
    assert "The second factor" in Q["vd_ss"]
    said("\\tabref{tab:islm-budget}列出 1935—1941 财政年度的数", B.index[0], B.index[-1])
    table_budget(F, Y, Q)
    ex1937(F, Y, Q)
    m, _ = rates()
    bond, bill = m.govt_bond_pct, m.tbill_pct
    said("长期政府债券的收益率从 1937 年 2 月的约 2.5\\% 升到 4 月的 2.8\\%，1938 年 12 月又回到约 2.5\\%", 1937, 2,
         bond[(1937, 2)], 4, bond[(1937, 4)], 1938, 12, bond[(1938, 12)])
    assert bond.loc[1937].idxmax() == 4                                       # 先升后降
    said("国库券的收益率 1937 年 4 月是 0.7\\%，1938 年 6 月只有 0.02\\%", 1937, 4, bill[(1937, 4)], 1938, 6,
         bill[(1938, 6)])
    said("按\\exref{ex:islm-1937}的读法，1937 年上半年 LM 左移的作用大", 1937)
    # Roosevelt, 14 April 1938
    d14, y38 = F["ap38_title"]
    said("1938 年春天，政策转了向。4 月 14 日，罗斯福", y38, mon("ap38_title", "April"), d14)
    gold, rr = F["ap38_desterilize"]
    said("新的计划包括解冻约 14 亿美元的黄金，由联邦储备委员会把准备金要求降低约 7.5 亿美元", gold, rr)
    spend, loans = F["ap38_spend"], F["ap38_loans"]
    chk("    the items of the work programme add up to $2,062,000,000", sum(spend[:-1]), spend[-1])
    chk("    the loans add up to $950,000,000", sum(loans[:-1]), loans[-1])
    said("计划里由财政部支出的工作项目共约 20.6 亿美元，贷款 9.5 亿美元", spend[-1], loans[-1])
    assert "monetary measures are insufficient" in Q["ap38_insufficient"]


def table_1937(F, Y, Q):
    """tab:islm-1937, row by row."""
    R = requirements()
    _, sp = F["vd_spike"], F["vd_spike"][0]
    assert "second quarter of 1936" in Q["vd_spike"] and "Congress decided to accelerate" in Q["vd_bonus"]
    said("1936 年第二季度 & 联邦政府 & 支付国会决定提前发放的一战退伍军人补偿金", sp)
    chk("    the second quarter (第二季度)", 2, told("1936 年第二季度 & 联邦政府", "第", "季度"))
    said("1936 年 6 月 & 国会 & 通过税法，大幅提高所得税率", F["vd_income"][3], mon("vd_income", "June"))
    assert "Revenue Act passed in June 1936" in Q["vd_income"]
    up1 = R.iloc[1].start
    said("1936 年 7 月 14 日 & 联邦储备委员会 & 法定准备金率提高 50\\%，8 月 16 日起执行", Y["fa_decided"],
         mon("fa_decided", "July"), F["fa_decided"][0], F["fa_raise"][0], up1.month, up1.day)
    assert (up1.month, up1.day - 1) == (mon("fa_raise", "August"), F["fa_raise"][1])   # after the close of business on 15 Aug.
    said("1936 年 12 月 21 日 & 财政部 & 宣布冻结新增的黄金，24 日起实行", Y["fj_dec21"], mon("fj_dec21", "December"),
         F["fj_dec21"][0], F["fb_dec24"][0])
    two, _, y37, _, _ = F["vd_ss"]
    said("1937 年 1 月 & 联邦政府 & 开始征收社会保障税，税率 2\\%，一半由雇主支付", y37, mon("vd_ss", "January"), two)
    assert "with half paid by the employer" in Q["vd_ss"]
    chk("    half (一半)", 0.5, told("一半由雇主支付", "", "由雇主"))
    say("33⅓")
    chk("    33⅓ per cent (fb_331)", F["fb_331"][0], 100 / 3)
    chk("    the second increase: 26/19.5 - 1 = 1/3", R.iloc[3].central_reserve_city / R.iloc[1].central_reserve_city - 1,
        1 / 3)
    d1, _, d1b = F["fb_halves"]
    assert R.iloc[2].start == pd.Timestamp(1937, 3, int(d1)) and R.iloc[3].start == pd.Timestamp(1937, 5, int(d1b))
    said("1937 年 1 月 30 日 & 联邦储备委员会 & 再提高 33⅓\\%，3 月 1 日与 5 月 1 日各执行一半", Y["fb_jan30"],
         mon("fb_jan30", "January"), F["fb_jan30"][0], None, mon("fb_halves", "March"), d1, mon("fb_halves", "May"), d1b)
    d2, y37b = F["ap37_title"]
    assert "steel bridges and great permanent structures" in Q["ap37_slow"]
    said("1937 年 4 月 2 日 & 罗斯福 & 担心耐用品原料涨价，要放慢钢桥等永久建筑的开支", y37b, mon("ap37_title", "April"), d2)
    y, m300 = F["fm_300m"]
    assert "at the request of the Board of Governors" in Q["fm_300m"]
    said("1937 年 9 月 & 财政部 & 应委员会的要求，从不活动账户放出 3 亿美元黄金", y, mon("fm_300m", "September"), m300)
    d14, m100 = F["fr_feb14"]
    said("1938 年 2 月 14 日 & 财政部 & 每季度 1 亿美元以内的新增黄金不再冻结", Y["fr_feb14"], 2, d14, m100)
    assert issue("fr_feb14") == (1938, 3) and "in any one quarter of the year" in Q["fr_feb14"]
    d14b, y38 = F["ap38_title"]
    said("1938 年 4 月 14 日 & 罗斯福 & 致国会咨文：解冻约 14 亿美元黄金，增加支出与贷款", y38, mon("ap38_title", "April"),
         d14b, F["ap38_desterilize"][0])
    gold, rr, d16 = F["fm_apr16"]
    down = R.iloc[4].start
    assert (down.year, down.month, down.day) == (1938, mon("fm_apr16", "April"), d16)
    said("1938 年 4 月 16 日 & 联邦储备委员会 & 法定准备金率降低，约合 7.5 亿美元", down.year, down.month, down.day, rr)
    # the sources of the table
    nos = int(re.search(r"NO\. (\d+)", Q["bms_t107"]).group(1))
    (a1, a2), (b1, b2), (c1, c2), (d1_, d2_), (e1, e2) = (issue(r) for r in ("fa_decided", "fj_dec21", "fb_jan30",
                                                                              "fr_feb14", "fm_apr16"))
    assert a1 == 1936 and b1 == c1 == 1937 and d1_ == e1 == 1938
    said("\\datasource{《联邦储备公报》1936 年 8 月、1937 年 1 月与 2 月、1938 年 3 月与 5 月；《银行与货币统计》表 107；美国总统"
         "项目所录罗斯福 1937 年 4 月 2 日的记者会与 1938 年 4 月 14 日的咨文；退伍军人补偿金、所得税与社会保障税据 Velde（2009）",
         a1, a2, b1, b2, c2, d1_, d2_, e2, nos, y37b, mon("ap37_title", "April"), d2, y38, mon("ap38_title", "April"), d14b,
         Y["vd_conclusion"])


FRACTIONS = {0.5: "½", 0.25: "¼", 0.75: "¾"}


def pct(x: float) -> str:
    """A reserve requirement as Table 107 prints it: 19½, 22¾, 13."""
    whole, part = int(x), round(x - int(x), 2)
    return f"{whole}{FRACTIONS[part]}" if part else f"{whole}"


def table_reserves(F, Y, Q):
    """tab:islm-reserves: the first five periods of Table 107, as printed."""
    R = requirements()
    t = tex_text()
    for r in R.iloc[:5].itertuples():
        line = (f"{r.start.year}.{r.start.month}.{r.start.day}—{r.end.year}.{r.end.month}.{r.end.day} & "
                + " & ".join(pct(getattr(r, c)) for c in COLS) + " \\\\")
        assert line in t, line
        COVERED.append(line)
    assert Q["bms_t107u"] == "[Per cent of deposits" and "JUNE 21, 1917- DECEMBER 31, 1941" in Q["bms_t107"]
    said("\\datasource{《银行与货币统计》（1943）表 107，第 400 页，据扫描页读出", Y["bms_t107"],
         int(re.search(r"NO\. (\d+)", Q["bms_t107"]).group(1)), page("bms_t107"))


def table_budget(F, Y, Q):
    """tab:islm-budget, as Historical Statistics prints it (one decimal)."""
    B = budget()
    t = tex_text()
    said("\\caption{联邦政府的收支（十亿美元，财政年度到 6 月 30 日）", 6, 30)
    head = "财政年度 & " + " & ".join(str(y) for y in B.index) + " \\\\"
    rows = ["收入 & " + " & ".join(f"{v:.1f}" for v in B.receipts) + " \\\\",
            "支出 & " + " & ".join(f"{v:.1f}" for v in B.outlays) + " \\\\",
            "盈余或赤字（$-$） & " + " & ".join(f"$-${-v:.1f}" for v in B.surplus) + " \\\\"]
    assert (B.surplus < 0).all()
    for line in [head] + rows:
        assert line in t, line
        COVERED.append(line)
    tr = transcription("cy_head")
    assert "Receipts 339" in tr and "Surplus or deficit (-) 341" in tr and "Data for 1929-1953 are consolidated cash" in tr
    said("\\datasource{《美国历史统计》（1975）系列 Y 339—341，第 1105 页，1929—1953 年为合并现金报表的数", Y["cy_head"],
         339, 341, page("cy_head"), 1929, 1953)


def ex1937(F, Y, Q):
    M = model()
    base, both, m37, g37 = M["base"], M["both"], M["m37"], M["g37"]
    dM, dG = SHOCK37["dM"], SHOCK37["dG"]
    said("\\begin{example}{用 IS–LM 读 1937 年}", 1937)
    said("设准备金率的提高与黄金的冻结相当于货币数量减少 2，财政的收紧相当于政府支出减少 2", -dM, -dG)
    di_m, di_g = m37["i"] - base["i"], g37["i"] - base["i"]
    said("（1）分母仍是 2。收入变化$1\\times(-2)+2\\times(-2)=-6$，降到 84。利率变化$-0.4/2\\times(-2)+0.2/2\\times(-2)"
         "=0.4-0.2=0.2$，升到 2.2\\%", base["den"], base["monetary"], -dM, base["fiscal"], -dG, base["Y"] - both["Y"],
         both["Y"], 1 - M2["c"], base["den"], -dM, M2["k"], base["den"], -dG, di_m, -di_g, both["i"] - base["i"],
         both["i"])
    chk("    the two parts add up (linear model)", di_m + di_g, both["i"] - base["i"], tol=1e-9)
    said("（2）货币的部分让收入减少 2、利率上升 0.4；财政的部分让收入减少 4、利率下降 0.2", base["Y"] - m37["Y"], di_m,
         base["Y"] - g37["Y"], -di_g)
    said("这里的 2 与 2 是假设的，只有方向与 1937 年的措施相同", -dM, -dG, 1937)


def debate(F, Y, Q):
    said("\\subsubsection{是什么造成了 1937—1938 年的衰退}", 1937, 1938)
    assert "rose sharply in early 1937" in Q["rom92_rates"] and "plummeted in late 1937" in Q["rom92_rates"]
    _, _, y37, y38 = F["rom92_fs678"]
    said("据 Romer（1992）的转述，在弗里德曼与施瓦茨看来，1937—1938 年货币存量的下降", 1992, y37, 1900 + y38)
    assert "policy actions of the Federal Reserve System" in Q["rom92_fs678"]
    three, y36, y37b = F["rom92_steps"]
    said("是 1936 年 7 月到 1937 年 5 月分三步把法定准备金率提高一倍", y36, mon("rom92_steps", "July"), y37b,
         mon("rom92_steps", "May"))
    chk("    three steps (三步)", three, told("分三步把法定准备金率提高一倍", "分", "步"))
    assert "the doubling of reserve requirements" in Q["rom92_steps"]
    chk("    doubled (提高一倍)", 1, told("分三步把法定准备金率提高一倍", "提高", "倍"))
    said("照 Velde（2009）的转述，他们认为准备金率的提高", Y["vd_conclusion"])
    assert "intensified the severity of the decline and also probably caused it to occur earlier" in Q["vd_fs544"]
    said("支持的证据是利率在 1937 年初急升，对利率敏感的建筑支出在 1937 年末骤降", *F["rom92_rates"])
    A = annual()
    said("M1 的年平均从 1937 年的 309.1 亿美元降到 1938 年的 305.2 亿美元", 1, 1937, A.loc[1937, "m1_bn"] * 1e9, 1938,
         A.loc[1938, "m1_bn"] * 1e9)
    assert "do not explain the timing of the downturn" in Q["vd_conclusion"]
    assert Q["vd_currie"] == "such as Currie (1980), Calomiris and Wheelock (1998)," and "did not cause" in Q["vd_cause"]
    y38h = F["rom92_hansen"][0]
    said("照 Romer 的转述，汉森（1938）与后来的一些研究", y38h)
    said("1936 年第二季度，联邦支出出现一个很大的尖峰", F["vd_spike"][0])
    chk("    the second quarter (第二季度)", 2, told("1936 年第二季度，联邦支出", "第", "季度"))
    q3, y36b = F["vd_bonus"]
    said("按 Velde 的估计，它让 1936 年后三个季度的需求高出不少", y36b)
    chk("    the last three quarters (后三个季度)", q3, told("1936 年后三个季度的需求", "后", "个季度"))
    assert "in the last three quarters of 1936" in Q["vd_bonus"] and "on its own" in Q["vd_bonus"]
    said("1937 年初财政收紧，靠增税短暂地回到了预算平衡", F["vd_tighter"][0])
    assert "fiscal policy became tighter in early 1937" in Q["vd_tighter"]
    said("1936 年下半年投资大增，各类投资要到 1937 年末才一齐下降", *F["vd_surge"])
    assert "unionization" in Q["rom92_wages"]
    y1, y2, p94 = F["rom92_wpi"]
    said("1937—1938 年批发物价却跌了 9.4\\%", y1, y2, p94)
    assert "Wages explain little of the downturn and none of the recovery." in Q["vd_conclusion"]
    said("按 Eggertsson 与 Pugsley（2006）的分析", Y["ep_abstract"])
    assert "sticky prices and rational expectations" in Q["ep_abstract"]
    assert "much larger at low interest rates" in Q["ep_larger"]
    d2, y37c = F["ep_fdr"]
    said("罗斯福 1937 年 4 月 2 日在记者会上说", y37c, mon("ep_fdr", "April"), d2)
    assert "over the price rise in certain materials." in Q["ep_fdr"] and (y37c, d2) == (F["ap37_title"][1], F["ap37_title"][0])
    assert "consumers of consumer goods rather than consumers of durable goods" in Q["ap37_bottom"]
    # the trap
    said("凯恩斯 1936 年说他不知道有过例子，希克斯 1937 年把陷阱画进了图里", Y["gt_noexample"], Y["hk_depression"])
    said("1937 年的经验对两边都有话说", 1937)
    m, yearly = rates()
    assert m.loc[1938:1939].govt_bond_pct.min() > 2
    below = m[m.govt_bond_pct < 2].index[0]
    said("一边的证据是，1938—1939 年国库券收益率接近零，超额准备越积越多，长期政府债券的收益率却一直在 2\\% 以上，到 1940 年 11 月"
         "才降到 2\\% 以下", 1938, 1939, 2, below[0], below[1], 2)
    ex = reserves().excess_m
    assert ex[(1939, 12)] > ex[(1938, 12)] > ex[(1938, 1)]
    said("联邦储备委员会 1936 年提高准备金率时", Y["fa_superfluous"])
    assert "could have no effect on the banking sector's lending activities" in Q["vd_string"]
    assert "Marriner Eccles, Chairman of the Board of Governors" in Q["vd_string"]
    said("日本银行 1999 年的说法与此相近", Y["bj99b_title"])
    bond = m.govt_bond_pct
    assert bond[(1937, 4)] > bond[(1937, 2)]                                   # 长期利率在 1937 年春天上升
    said("另一边的证据是，冻结“多余”的准备之后，长期利率在 1937 年春天上升，对利率敏感的建筑支出在 1937 年末骤降", 1937,
         F["rom92_rates"][1])
    said("日本银行 2001 年改以经常账户余额为目标", Y["bj01_title"])


def hansen(F, Y, Q):
    d28, y38 = F["hn_address"]
    said("1938 年 12 月 28 日，汉森", y38, mon("hn_address", "December"), d28)
    assert "Detroit, Michigan" in Q["hn_address"] and "Presidential address" in Q["hn_address"]
    P = ip_peak()
    months = 12 - P["trough"]
    assert 6 < months < 12                                                    # 谷底刚过去半年多
    say("这时衰退的谷底刚过去半年多")
    assert "few there are who believe" in Q["hn_few"] and "Less agreement can be claimed" in Q["hn_few"]
    pop, half, third = F["hn_population"]
    tr = transcription("hn_population")
    assert "nineteen-twenties" in tr and "In the current decade" in tr
    said("1920 年代美国人口增加了 1,600 万", 1920, pop)
    chk("    half (只增加一半)", half, told("眼下这个十年只增加一半", "只增加", ""))
    chk("    a third (降到三分之一)", third, told("下一个十年预计降到三分之一", "降到", ""))
    chk("    nineteenth century (十九世纪)", 19, told("他估计，十九世纪新资本形成", "他估计，", "世纪"))
    assert "in the nineteenth" in Q["hn_half"] and "possibly somewhere near one-half" in Q["hn_half"]
    chk("    near one-half (接近一半)", F["hn_half"][0], told("可能接近一半", "接近", ""))
    assert "rapidly being closed" in Q["hn_closed"]
    y29, bn80 = F["hn_1929"]
    a80, a40 = F["hn_80bn"]
    said("汉森说，1929 年的国民收入约 800 亿美元，大萧条的谷底降到 400 亿美元", y29, bn80, a40)
    assert a80 == bn80
    f65, f60 = F["hn_floor"]
    said("他建议不要让国民收入明显低于 650 亿美元，或者说最低 600 亿美元；收入接近 700 亿美元时", f65, f60,
         F["hn_taper"][0])
    assert "tapered off" in transcription("hn_taper") and "as a minimum" in transcription("hn_floor")
    assert "by an indirect route and a slower process" in Q["hn_regimented"]
    y, m4 = F["ap38_title"][1], mon("ap38_title", "April")
    said("罗斯福 1938 年 4 月的咨文用的也是国民收入的数", y, m4)
    y28, i28, y32, i32 = F["ap38_income"]
    said("1928 年的国民收入是 800 亿美元，1932 年已经降到不足 400 亿美元", y28, i28, y32, i32)
    assert "less than forty billion" in Q["ap38_income"]
    i32b, _, i37b, _, run = F["ap38_running"]
    y37, i37 = F["ap38_income37"]
    assert i37 == i37b and i32b < i32                                         # 38 < 'less than forty'
    said("1937 年，“我们公民的收入总额已经升到 680 亿美元”，眼下的速度只有约 560 亿美元", y37, i37, run)
    # Pigou
    no, y43 = F["pg_masthead"]
    said("庇古在 1943 年 12 月的《经济学杂志》上", y43, mon("pg_masthead", "DECEMBER"))
    assert "In his Fiscal Policy and Business Cycles Professor Hansen writes" in Q["pg_title"]
    # Modigliani
    v12, n1, y44 = F["nb_first"]
    said("1944 年 1 月在《计量经济学》上发表", y44, mon("nb_first", "January"))
    assert F["es_modigliani"][:3] == [y44, v12, n1] and "Liquidity Preference and the Theory of Interest and Money" in Q["es_modigliani"]
    said("照他自己 1985 年的回顾", F["nb_copyright"][0])
    assert "My first published article in English" in Q["nb_first"] and "substantially, my doctoral dissertation" in Q["nb_first"]
    chk("    his first article in English (第一篇)", 1, told("这是他的第一篇英文论文", "第", "篇"))


def deeper(F, Y, Q):
    said("据 archive.org 上《计量经济学》1937 年第 5 卷的识别文本", F["ox_refs"][1], F["ox_refs"][0])
    pages = sorted({page(r) for r in column("file") if column("file")[r] == "hicks1937img"})
    said("希克斯的记号与三组方程按同一扫描本的页面图像读出（第 148、149、152、153 页）", *pages)
    hp = sorted({page(r) for r in column("file") if column("file")[r] == "hansen1939img"})
    said("汉森的演说据《美国经济评论》1939 年 3 月号的识别文本与扫描页，第 2、4、14 页的数与句子按图像读出", Y["hn_title"], 3,
         *hp)
    chk("    three disagreements (三处不一致)", 3, told("\\textbf{三处不一致。}", "{", "处"))
    (yj, mj), (ym, mm), (yf, mf) = issue("fj_dec21"), issue("fr_dec22"), issue("fb_dec24")
    said("财政部冻结黄金的声明，1937 年 1 月的公报写 12 月 21 日宣布，1938 年 3 月的公报写 12 月 22 日；2 月的公报说计划从 12 月 24 日"
         "起实行。正文用 21 日与 24 日", yj, mj, 12, F["fj_dec21"][0], ym, mm, 12, F["fr_dec22"][0], mf, 12,
         F["fb_dec24"][0], F["fj_dec21"][0], F["fb_dec24"][0])
    assert yf == yj and F["fr_dec22"][1] == F["fb_dec24"][1] == 1936
    P = ip_peak()
    y37, y38, p32 = F["vd_julypeak"]
    assert "peaked in May 1937" in Q["vd_peakmay"]
    said("工业生产的高点，Velde（2009）先说联邦储备委员会的指数在 1937 年 5 月到顶，后面又说“从 7 月的高点”到 1938 年 5 月下降了 "
         "32\\%", Y["vd_conclusion"], F["vd_peakmay"][0], mon("vd_peakmay", "May"), mon("vd_julypeak", "July"), y38,
         mon("vd_julypeak", "May"), p32)
    assert y37 == F["vd_peakmay"][0]
    g17 = int(re.search(r"G\.(\d+) ", load_snapshot("frb_g17_ip_1929_1941")[1]["source"]).group(1))
    s = ip()
    assert s[(1937, 5)] - s[(1937, 7)] < 0.01 * s[(1937, 5)]                    # 7 月略低
    said("按今天的 G.17 指数，5 月最高，7 月略低，从 5 月算降 32.5\\%，从 7 月算降 32.0\\%", g17, P["peak"], 7, P["peak"],
         P["fall"], 7, P["fall7"])
    chk("    Velde's 32 per cent from July", P["fall7"], p32, tol=0.5)
    y, m700, _ = F["fm_700m"][0], F["fm_700m"][0], F["fm_700m"][1]
    ex = reserves().excess_m
    assert "declined in August to $700,000,000" in Q["fm_700m"] and issue("fm_700m") == (1938, 5)
    said("超额准备 1937 年 8 月的数，1938 年 5 月的公报说降到 7 亿美元，《银行与货币统计》的月平均是 7.5 亿美元", 1937, 8, 1938, 5,
         m700, ex[(1937, 8)] * 1e6)
    R = reserves()
    gap = (R.total_m - R.required_m - R.excess_m).abs().max()
    said("每个月的法定准备加超额准备都等于总准备，误差不超过 100 万美元", max(gap, 1) * 1e6)
    notes = load_snapshot("bms_member_reserves_1935_1939")[1]["notes"]
    assert "The scan prints 6 and 9 much like 0" in notes and "The two disagree in three cells" in notes
    said("扫描页上的 6、9 与 0 不易分辨", 6, 9, 0)
    chk("    three cells (两者不同的三格)", 3, told("两者不同的三格", "不同的", "格"))
    A = annual()
    _, yearly = rates()
    said("1936 年超额准备的年平均与第 28 章所用公报的数相合", 1936, 28)
    chk("    excess reserves 1936: BMS mean against Chapter 28's Bulletin average", R.loc[1936].excess_m.mean(),
        A.loc[1936, "excess_reserves_m"], tol=1)
    chk("    the bill rate 1936: BMS against Chapter 28", yearly[1936], A.loc[1936, "tbill_rate"], tol=0.005)
    said("与第 30 章读出的 1937 财政年度相同", 30, 1937)
    say("Romer（1992）与 Velde（2009）的引述")
    _, p678 = F["rom92_severe"]
    _, p544 = F["vd_fs544"]
    said("弗里德曼与施瓦茨（1963）的结论据 Romer（1992）与 Velde（2009）的引述，两处所引页码不同（第 678 页与第 544 页）",
         F["rom92_severe"][0], 1992, Y["vd_conclusion"], p678, p544)
    assert F["vd_fs544"][0] == F["rom92_severe"][0]
    said("汉森 1938 年对衰退的解释据 Romer 的转述", F["rom92_hansen"][0])
    said("Velde 转引自 Meltzer（2003）", F["vd_string"][0])
    said("莫迪利亚尼 1944 年的论文本身没有取得", F["es_modigliani"][0])
    said("以及凯恩斯 1937 年在《经济学季刊》上的文章", 1937)
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    assert "Quarterly Journal of Economics}, 51" not in bib                     # not in the bibliography


def legacy(F, Y, Q):
    said("\\begin{compare}{凯恩斯本人与 IS–LM}{凯恩斯本人（1936）}{IS–LM（希克斯 1937 与本章的教学模型）}", Y["gt_animal"],
         Y["hk_title"])
    assert "the concept of 'Income' is worked monstrously hard" in Q["hk_rough"]
    assert "the distribution of Income as well as its magnitude" in Q["hk_rough"]
    assert "a little apparatus" in Q["hk_apparatus"]


def takeaways(F, Y, Q):
    P = ip_peak()
    A = annual()
    said("希克斯 1937 年把古典理论与凯恩斯写成三组方程", Y["hk_title"])
    said("财政乘数是$h/[h(1-c)+bk]$，因为挤出而小于$1/(1-c)$；货币乘数是$b/[h(1-c)+bk]$", 1, 1, 1, 1)
    said("1938—1939 年美国的国库券收益率接近零，长期政府债券的收益率仍在 2\\% 以上", 1938, 1939, 2)
    said("1937—1938 年，法定准备金率翻倍、黄金冻结与财政收紧之后，工业生产下降了 32.5\\%，失业率升到 19.0\\%", 1937, 1938,
         P["fall"], A.loc[1938, "unemployment_pct"])
    said("汉森 1938 年提出长期停滞论", F["hn_address"][1])
    said("庇古 1943 年回答", Y["pg_masthead"])


def selfcheck(F, Y, Q):
    M = model()
    base, sc = M["base"], M["sc1"]
    said("把$h$从 4 改成 8", M2["h"], SC1["h"])
    said("联邦储备委员会 1936 年认为冻结多余的准备", Y["fa_superfluous"])
    said("若货币减少 2 而政府支出不变，利率怎样变化？这与 1937 年春天的长期利率相合吗？", -SHOCK37["dM"], 1937)
    said("庇古 1943 年的论证", Y["pg_masthead"])
    said("日本银行 1999 年说，再多供给资金", Y["bj99b_title"])
    # the answers
    c, b, k = M2["c"], M2["b"], M2["k"]
    said("分母$8\\times0.4+2\\times0.2=3.6$。财政乘数$8/3.6\\approx2.22$，货币乘数$2/3.6\\approx0.56$。$h$越大，财政乘数越接近 2.5",
         SC1["h"], 1 - c, b, k, sc["den"], SC1["h"], sc["den"], sc["fiscal"], b, sc["den"], sc["monetary"], sc["cross"])
    assert base["fiscal"] < sc["fiscal"] < sc["cross"] and sc["monetary"] < base["monetary"]
    m37 = M["m37"]
    m, _ = rates()
    bond = m.govt_bond_pct
    said("利率变化$0.2\\times2=0.4$，上升到 2.4\\%，收入减少 2。长期政府债券的收益率从 1937 年 2 月的 2.46\\% 升到 4 月的 2.80\\%",
         (1 - c) / base["den"], -SHOCK37["dM"], m37["i"] - base["i"], m37["i"], base["Y"] - m37["Y"], 1937, 2,
         bond[(1937, 2)], 4, bond[(1937, 4)])


def ending(F, Y, Q):
    said("1936 年 9 月的牛津，米德、哈罗德与希克斯把凯恩斯的书写成了方程", F["ox_report"][2], mon("ox_report", "SEPTEMBER"))
    B = budget()
    A = annual()
    said("联邦政府的支出从 1938 财政年度的 72 亿美元增加到 1941 财政年度的 140 亿美元，1941 年的失业率降到 9.9\\%", 1938,
         B.outlays[1938] * 1e9, 1941, B.outlays[1941] * 1e9, 1941, A.loc[1941, "unemployment_pct"])
    say("汉森说，公共支出最容易，危险也在这里。")
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 34's question"
    assert t.index("\\end{answers}") < t.index("1936 年 9 月的牛津")
    ch34 = (ROOT / "zh" / "ch34_warfinance.tex").read_text(encoding="utf-8")
    assert f"\\guidequestion{{{NEXT}" in ch34                                 # the first half of its question


def models() -> None:
    """The key equations, and their arithmetic checked with numbers."""
    rng = np.random.default_rng(33)
    for _ in range(30):
        a, I0, G, T = rng.uniform(5, 50), rng.uniform(5, 30), rng.uniform(0, 20), rng.uniform(0, 20)
        c, b, k, h = rng.uniform(0.1, 0.9), rng.uniform(0.1, 5), rng.uniform(0.05, 1), rng.uniform(0.1, 20)
        Mn, P = rng.uniform(5, 50), rng.uniform(0.5, 2)
        p = dict(a=a, c=c, I0=I0, b=b, G=G, T=T, k=k, h=h, M=Mn, P=P)
        s = islm(**p)
        A = a - c * T + I0 + G
        # eq:islm-is and eq:islm-lm hold at the solution
        chk("    eq:islm-is: Y = (A - b i)/(1 - c)", s["Y"], (A - b * s["i"]) / (1 - c), tol=1e-8)
        chk("    eq:islm-is: i = A/b - (1 - c)Y/b", s["i"], A / b - (1 - c) / b * s["Y"], tol=1e-8)
        chk("    Y = C + I + G", s["Y"], a + c * (s["Y"] - T) + I0 - b * s["i"] + G, tol=1e-8)
        chk("    eq:islm-lm: i = (k/h)Y - M/(hP)", s["i"], k / h * s["Y"] - Mn / (h * P), tol=1e-8)
        # eq:islm-solution
        den = h * (1 - c) + b * k
        chk("    eq:islm-solution: Y*", s["Y"], (h * A + b * Mn / P) / den, tol=1e-8)
        chk("    eq:islm-solution: i*", s["i"], (k * A - (1 - c) * Mn / P) / den, tol=1e-8)
        # the multipliers: dY/dG = h/den, dY/d(M/P) = b/den; crowding out bk/h in the denominator
        d = rng.uniform(0.1, 3)
        chk("    dY/dG = h/[h(1-c) + bk]", (islm(**{**p, "G": G + d})["Y"] - s["Y"]) / d, h / den, tol=1e-7)
        chk("    dY/d(M/P) = b/[h(1-c) + bk]", (islm(**{**p, "M": Mn + d * P})["Y"] - s["Y"]) / d, b / den, tol=1e-7)
        assert h / den < 1 / (1 - c)                                         # crowding out
        chk("    the fiscal multiplier is 1/[(1 - c) + bk/h]", h / den, 1 / ((1 - c) + b * k / h), tol=1e-9)
        # the slopes: IS falls, LM rises; a larger b makes IS flatter
        assert -(1 - c) / b < 0 < k / h
    # the limits of the compare box: h -> infinity, b -> 0, h -> 0
    c, k, b = M2["c"], M2["k"], M2["b"]
    big = islm(h=1e9)
    chk("    h -> infinity: fiscal multiplier -> 1/(1 - c)", big["fiscal"], 1 / (1 - c), tol=1e-6)
    chk("    h -> infinity: monetary multiplier -> 0", big["monetary"], 0, tol=1e-6)
    flat = islm(b=1e-9)
    chk("    b -> 0: fiscal multiplier -> 1/(1 - c)", flat["fiscal"], 1 / (1 - c), tol=1e-6)
    chk("    b -> 0: monetary multiplier -> 0", flat["monetary"], 0, tol=1e-6)
    steep = islm(h=1e-9)
    chk("    h -> 0: fiscal multiplier -> 0", steep["fiscal"], 0, tol=1e-6)
    chk("    h -> 0: monetary multiplier -> 1/k", steep["monetary"], 1 / k, tol=1e-6)
    # Chapter 4's money multiplier falls as R/D rises (eq:money-mult); Chapter 3's Fisher relation with no inflation
    for cm in (0.1, 0.3, 0.5):
        ms = [1 / (cm + rd - cm * rd) for rd in (0.084, 0.126)]
        assert ms[1] < ms[0]
    chk("    eq:prices-fisher with pi = 0: r = i", (1 + 0.02) / (1 + 0.0) - 1, 0.02, tol=1e-12)
    # eq:bullion-exchange: with M = kY the income velocity Y/M is 1/k
    chk("    1/k = the velocity Y/M of M = kY", M2["M"] / M2["k"] / M2["M"], 1 / M2["k"], tol=1e-12)


def figures_data() -> None:
    """What the figures assert of their data."""
    R = reserves()
    assert R.index[0] == (1935, 1) and R.index[-1] == (1939, 12) and (R.excess_m > 0).all()
    m, _ = rates()
    assert m.govt_bond_pct.notna().all() and m.govt_bond_pct.between(1.5, 3.5).all()
    s = ip()
    assert s.loc[1935:1939].between(4, 10).all()
    M = model()
    assert M["fiscal"]["Y"] > M["money"]["Y"] > M["base"]["Y"] > M["both"]["Y"]


# ---------------------------------------------------------------------------------------------------
# 5. The book
# the life dates from rows of the snapshot: words -> (row, index of the birth year, index of the death year)
ROW_LIVES = {"James Edward Meade，1907—1995": ("loc_meade", 0, 1),
             "Roy Harrod，1900—1978": ("loc_harrod", 0, 1),
             "John Hicks，1904—1989": ("loc_hicks", 0, 1),
             "Jan Tinbergen，1903—1994": ("loc_tinbergen", 0, 1),
             "Ragnar Frisch，1895—1973": ("loc_frisch", 0, 1),
             "Henry Morgenthau Jr.，1891—1967": ("loc_morgenthau", 0, 1),
             "Hayami Masaru，1925—2009": ("loc_hayami", 0, 1),
             "Franklin D. Roosevelt，1882—1945": ("bnf_roosevelt", 0, 1),
             "Marriner Eccles，1890—1977": ("loc_eccles", 0, 1),
             "Alvin H. Hansen，1887—1975": ("loc_hansen", 0, 1),
             "Franco Modigliani，1918—2003": ("loc_modigliani", 0, 1)}
# the beginning of each record's heading
HEADS = {"loc_meade": "Meade, J. E. (James Edward)", "loc_harrod": "Harrod, Roy", "loc_hicks": "Hicks, John",
         "loc_tinbergen": "Tinbergen, Jan", "loc_frisch": "Frisch, Ragnar", "loc_morgenthau": "Morgenthau, Henry",
         "loc_hayami": "Hayami, Masaru", "bnf_roosevelt": "Franklin D. Roosevelt", "loc_eccles": "Eccles, Marriner S.",
         "loc_hansen": "Hansen, Alvin H.", "loc_modigliani": "Franco Modigliani; born"}
# what other chapters tell: (words of this chapter, chapter where it is told, words there)
EVENTS = [("\\chref{ch:depressionus}讲过，流入的黄金几乎一对一地变成了基础货币", "ch28_depressionus",
           "流入的黄金几乎一对一地变成了基础货币"),
          ("按\\chref{ch:money}的式~\\eqref{eq:money-mult}，准备金比率$R/D$上升，乘数$m$就下降", "ch04_money",
           "m=\\frac{1}{C/M+R/D-(C/M)(R/D)}"),
          ("名义利率就等于实际利率（式~\\eqref{eq:prices-fisher}）", "ch03_prices",
           "1+r^{\\text{事后}}_t=\\frac{1+i_t}{1+\\pi_{t+1}}"),
          ("$1/k$相当于\\chref{ch:bullion}的式~\\eqref{eq:bullion-exchange}里的流通速度", "ch19_bullion", "MV\\equiv PT"),
          ("接\\exref{ex:generaltheory-cross}的数，$a=26$，$c=0.6$", "ch32_generaltheory", "\\label{ex:generaltheory-cross}"),
          ("（式~\\eqref{eq:generaltheory-liquidity}）", "ch32_generaltheory", "M=M_1+M_2=L_1(Y)+L_2(r)"),
          ("庇古认为在现实的银行政策下削减货币工资会增加就业，凯恩斯认为灵活的工资政策维持不了充分就业", "ch32_generaltheory",
           "庇古"),
          ("与第 30 章读出的 1937 财政年度相同", "ch30_alternatives", "到 1937 财年，赤字还有 28 亿美元")]
# the chapters this one hands on to (new FORWARD_REFS rows opened by Chapter 33)
LATER = {"ch:mundell": "ch37_mundell", "ch:phillips": "ch38_phillips", "ch:naturalrate": "ch44_naturalrate",
         "ch:ratex": "ch48_ratex", "ch:minsky": "ch63_minsky", "ch:zlb": "ch66_zlb", "ch:abenomics": "ch67_abenomics",
         "ch:stagnation": "ch70_stagnation"}


def book(F, Q):
    """Life dates and what other chapters tell."""
    t = tex_text()
    for words, (rid, i, j) in ROW_LIVES.items():
        assert words in t, words
        assert f"{F[rid][i]:.0f}—{F[rid][j]:.0f}" in words, (words, rid)
        assert Q[rid].startswith(HEADS[rid]), (rid, Q[rid])                      # the person of the record
        COVERED.append(words)
    assert Q["loc_modigliani_head"] == "Modigliani, Franco" and F["loc_hayami_kanji"] == F["loc_hayami"]
    assert Q["loc_hayami_kanji"].startswith("速水優") and "总裁速水优（Hayami Masaru" in t
    for here, ch, there in EVENTS:
        assert here in t, here
        assert there in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (ch, there)
    assert F["cy_1937"][3] == -2.8                                             # Chapter 30's 28 亿美元
    for label, ch in LATER.items():
        assert f"{{{label}}}" in t, label
        assert f"\\label{{{label}}}" in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (label, ch)
    print(f"ok {len(ROW_LIVES)} life dates, {len(EVENTS)} statements of other chapters, {len(LATER)} later chapters")


def witnesses(F, Q):
    """Second witnesses of statements of the text, and the bibliography block of the chapter."""
    # life dates: Morgenthau also on the Treasury's page, Modigliani's death also in his Nobel biography
    assert F["tr_morgenthau"][:2] == F["loc_morgenthau"] and "Henry Morgenthau Jr." in meta()["sources"]["treasury_morgenthau"]["version"]
    assert F["nb_died"] == [25, F["loc_modigliani"][1]] and "Franco Modigliani died on September 25" in Q["nb_died"]
    assert "Wikipedia" in meta()["sources"]["loc_modigliani33"]["version"] or "Wikipedia" in column("note")["loc_modigliani"]
    # the reserve requirements of Table 107 against the Bulletin (the same Board: consistency)
    R = requirements()
    for col in COLS:
        chk(f"    16 Aug. 1936: {col} raised by 50 per cent", R.iloc[1][col] / R.iloc[0][col], 1 + F["fa_raise"][0] / 100)
    # excess reserves: the Bulletin's round numbers against Table 105
    ex = reserves().excess_m
    chk("    'approximately $3,000,000,000' (July 1936) against Table 105, million", ex[(1936, 7)], F["fa_3bn"][0] / 1e6,
        rel=0.05)
    chk("    excess reserves August 1937: the Bulletin's $700 million against Table 105's $750 million", ex[(1937, 8)],
        F["fm_700m"][0] / 1e6, tol=50)
    chk("    the gold released in April 1938: the message's 1.4 billion against the Bulletin's $1,392,000,000",
        F["fm_apr16"][0], F["ap38_desterilize"][0], tol=1e7)
    chk("    and the reduction of requirements, $750,000,000", F["fm_apr16"][1], F["ap38_desterilize"][1])
    # the gold programme: the three dates, and 'adopted at the end of 1936' in the Bulletin of May 1938
    assert F["fj_dec21"][0] + 1 == F["fr_dec22"][0] and F["fb_dec24"][0] == F["fm_14bn"][0]
    assert F["fm_sterilization"][0] == F["fb_dec24"][1] and 'The Treasury\'s "gold sterilization" program' in Q["fm_sterilization"]
    # the Board expected excess reserves of about $500 million after May 1937; Table 105 prints more
    assert F["fb_500m"][0] == 5e8 and ex[(1937, 5)] > F["fb_500m"][0] / 1e6
    # industrial production: the G.17 file today against Velde
    P = ip_peak()
    assert P["peak"] == mon("vd_peakmay", "May") and P["trough"] == mon("vd_julypeak", "May")
    # the Oxford meeting: the report and the list of those who attended
    assert F["ox_attend_head"] == F["ox_report"][:3]
    # unemployment and output (Historical Statistics, BEA)
    A = annual()
    assert A.loc[1938, "unemployment_pct"] > A.loc[1937, "unemployment_pct"]
    # the licences and the bibliography
    m = meta()
    lic = m["license"]
    for rid in ("hk_copyright", "vd_copyright", "vd_terms", "ep_copyright", "ep_reprint", "bj_terms", "fed_terms",
                "nb_copyright"):
        assert Q[rid] in lic and f"row {rid}" in lic, rid
    for words in ("Online by Gerhard Peters and John T. Woolley, The American Presidency Project", "short phrases only",
                  "may still be in copyright in the United States", "public data", "Licence Ouverte", "bj_imes"):
        assert words in lic, words
    assert "Online by Gerhard Peters and John T. Woolley, The American Presidency Project" in Q["ap37_credit"]
    assert "Online by Gerhard Peters and John T. Woolley, The American Presidency Project" in Q["ap38_credit"]
    for name in ("bms_member_reserves_1935_1939", "bms_reserve_requirements_1917_1941", "bms_rates_1936_1940"):
        assert load_snapshot(name)[1]["license"].startswith("Public domain"), name
    assert Q["fed_terms"] in load_snapshot("frb_g17_ip_1929_1941")[1]["license"]
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    start = bib.index("% ---- 第 33 章")
    following = re.search(r"^% ---- 第 \d+ 章", bib[start + 1:], re.MULTILINE)
    end = start + 1 + following.start() if following else bib.index("\\end{thebibliography}")
    block = bib[start:end]
    items = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", block)}
    allitems = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", bib)}
    for key in ("oxford1937", "hicks1937"):
        assert Q["hk_copyright"] in items[key] and "只引短语" in items[key], key
    assert Q["vd_copyright"] in items["velde2009"] and "只引短语" in items["velde2009"]
    assert Q["vd_title"].replace("-", "---") in items["velde2009"] and str(Y_of("vd_title")) in items["velde2009"]
    assert Q["ep_mistake"] == "Poor communication policy is the mistake of 1937." and "The Mistake of 1937" in items["eggertsson2006"]
    assert Q["ep_copyright"] in items["eggertsson2006"] and Q["ep_reprint"] in items["eggertsson2006"]
    assert Q["bj_terms"] in items["boj1999a"] and Q["fed_terms"] in items["frb2026ip"]
    assert Q["nb_copyright"] in items["nobel1985"]
    for key in ("app1937", "app1938"):
        assert "Online by Gerhard Peters and John T. Woolley, The American Presidency Project" in items[key], key
    for key in ("frb1936aug", "frb1937jan", "frb1938mar", "frb1938may", "bms1943b", "treasury33"):
        assert "公有领域" in items[key], key
    for key in ("hansen1939", "pigou1943"):
        assert "只引短语" in items[key], key
    assert "公共数据" in items["loc33"] and "Licence Ouverte" in allitems["bnf28"]
    assert "弗里德曼与施瓦茨的估计" in allitems["census1975x"] and "D 85--86" in allitems["census1975a"]
    for words, (rid, _, _) in ROW_LIVES.items():
        url = m["sources"][column("file")[rid]]["url"]
        if rid.startswith("loc_"):
            head = Q["loc_modigliani_head"] if rid == "loc_modigliani" else Q[rid]
            assert head.replace("-", "--") in items["loc33"], rid
            assert url in items["loc33"], rid
        else:
            assert Q[rid].split(" (")[0] in allitems["bnf28"] and url in allitems["bnf28"], rid
    assert Q["loc_hayami_kanji"].replace("-", "--") in items["loc33"]
    # every source of the snapshot is named by its URL in its item (the page images with the text they belong to)
    item_of = {"hicks1937img": "hicks1937", "census_y33": "census1975y", "chicagofedlegal": "velde2009",
               "nberw3829": "romer1992", "eggertsson2006pdf": "eggertsson2006", "bojterms": "boj1999a",
               "hansen1939img": "hansen1939", "es1944": "modigliani1944", "fedterms": "frb2026ip",
               "treasury_morgenthau": "treasury33", "frb1937feb": "frb1937a", "bnf_roosevelt28": "bnf28"}
    for key, s in m["sources"].items():
        item = "loc33" if key.startswith("loc_") else item_of.get(key, key)
        assert s["url"] in allitems[item].replace("\\%", "%").replace("\\_", "_"), key
    for name in ("bms_member_reserves_1935_1939", "bms_reserve_requirements_1917_1941", "bms_rates_1936_1940"):
        assert load_snapshot(name)[1]["url"] in items["bms1943b"], name
    g = load_snapshot("frb_g17_ip_1929_1941")[1]
    assert g["url"] in items["frb2026ip"] and "B50001" in items["frb2026ip"]
    keys = set(allitems)
    cited = {k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", tex_text()) for k in c.split(",")}
    assert cited <= keys, sorted(cited - keys)
    assert set(items) <= cited, sorted(set(items) - cited)
    srcs = set(m["sources"])
    for key in items:                                                              # every work of the block is a source
        assert key in srcs or key in item_of.values() or key == "loc33", key
    print(f"ok {len(cited)} works cited, {len(items)} of them in the bibliography block of Chapter 33")


NAMES = ("Velde|Romer|Eggertsson|Pugsley|Currie|Calomiris|Wheelock|Telser|Meltzer|Smithies|Gordon|弗里德曼|施瓦茨")


def counts() -> None:
    """The editor's limits: “不能” at most about a dozen; no cited modern author as the subject of a sentence outside
    the 史料说明; the forbidden words."""
    t = tex_text()
    main = re.sub(r"\\begin\{deeper\}\[史料说明\].*?\\end\{deeper\}", "", t, flags=re.DOTALL)
    n = t.count("不能")
    print(f"ok “不能” {n} times")
    assert n <= 12, n
    verbs = "认为|写道|说|指出|记述|估计|承认|报道|记载|提到|列出|给出|发现|统计|算出|早有|看法|有类似|怀疑|强调"
    subj = re.findall(r"(?:^|[。；：，\n])\s*(?:" + NAMES + r")(?:[、与和] ?(?:" + NAMES + r"))*(?: 等人)?(?:（\d{4}）)?\s*"
                      r"(?:" + verbs + ")", main)
    assert not subj, subj
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
    guide(F, Y, Q)
    opening(F, Y, Q)
    world(F, Y, Q)
    hicks(F, Y, Q)
    is_curve(F, Y, Q)
    lm(F, Y, Q)
    policy(F, Y, Q)
    trap(F, Y, Q)
    recession(F, Y, Q)
    debate(F, Y, Q)
    hansen(F, Y, Q)
    deeper(F, Y, Q)
    legacy(F, Y, Q)
    takeaways(F, Y, Q)
    selfcheck(F, Y, Q)
    ending(F, Y, Q)
    models()
    figures_data()
    book(F, Q)
    witnesses(F, Q)
    counts()
    coverage()
    anchors(str(TEX), df["id"], script=Path(__file__))


if __name__ == "__main__":
    main()
