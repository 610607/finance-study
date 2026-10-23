"""Chapter 32 (凯恩斯《通论》): every number and every quotation in zh/ch32_generaltheory.tex.

    python3 checks/check_ch32.py

Inputs:
  generaltheory_facts    quotations of Keynes's General Theory (Macmillan, 1936; the Digital Library of India's copy on
                         archive.org), of his broadcast 'Saving and Spending' (January 1931) and of 'A Programme of
                         Expansion' (May 1929, from the pamphlet written with H. D. Henderson) in Essays in Persuasion
                         (1931), of the Commons debates of 15 April 1929 (Churchill's Budget speech) and 4 November 1936
                         (Jarrow), of the Macmillan Committee's Minutes of Evidence (1930), of Kahn (1931), Pigou (1936),
                         Ohlin (1937, I and II), Keynes (1937), Kalecki (1935), Mill (1844), Berg and Jonung (1998),
                         Shizume (2009), Baumol (1999) and Velde (2003), the people pages of Historic Hansard and the
                         authority records of the Library of Congress and the Bibliotheque nationale de France (checked by
                         data/fetch/verify_web_quotes.py); the rows with an empty quotation are values and words read on
                         page images (Kahn's equations, assumptions and table, the table of Kuznets's estimates on p. 103
                         of the General Theory, the pages of the General Theory and of Essays in Persuasion whose OCR is
                         garbled or loses the pound signs), with a transcription between « and » in the note
  boe_millennium_unemp_1919_1938_monthly   Britain's administrative unemployment rate, month by month (BoE M5)
  boe_millennium_gb_1919_1938              real GDP, consumption, investment, exports and imports; Feinstein's
                                           unemployed and unemployment rate, 1919-1938 (BoE A1 and A50)
  boe_millennium_bank_rate_1929_1939       Bank Rate on 1 January 1929 and on every day it changed (BoE D1)
The figure module figsrc/fig_ch32.py imports its data and the teaching model from here.

What is checked here:
  1. readings   every number of the value column of generaltheory_facts is read from its quotation (digits, English
                number words, fractions, '2-5' for 2.5); a row read on a page image is read from its transcription
                (fractions such as 3/7, '·94' and '2½')
  2. the text   every “…” of the chapter is the chapter's rendering of a quotation (TRANSLATIONS), with the source's
                words listed in KEYWORDS (for a row read on a page image, the words of its transcription)
  3. numbers    every number of the text, section by section: said() finds the phrase and compares each number it
                prints with the value read from the snapshots or computed from the teaching model, within half a unit
                of the last printed digit; Chinese numerals are read by zh()
  4. coverage   every Arabic number of the text (outside labels, citations, cross-references, the key equations and
                math sub- and superscripts) lies inside a phrase checked by said()
  5. the book   the model's equations, life dates, what other chapters tell, second witnesses, the bibliography block
                of the chapter and its licence notices
  6. anchors    the paraphrase anchors `% 据: ...` name rows of generaltheory_facts

The teaching model M1 (docs/PLAN.md §1: the Keynesian cross, added to Chapter 2's cloth economy):
    Y = C + I, C = a + cY  =>  Y* = (a + I)/(1 - c), dY = dI/(1 - c)        (eq:generaltheory-cross)
    with a = 26, c = 0.6, I = 10: Y = 90 and C = 80, Chapter 2's accounts; the paradox of thrift lowers a to 16, with I
    fixed and with I = 1 + 0.1Y. Kahn's multiplier (eq:generaltheory-kahn) is computed in fractions. The parameters
    are defined in M1 below; docs/PLAN.md asks for them in checks/teaching_params.py, a shared file this chapter may
    not create (the move is requested in the chapter's report).
"""
from __future__ import annotations

import os
import re
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from check_ch02 import CHAIN, CONSUMPTION, THRIFT_CONSUMPTION
from common import ROOT, anchors, load_snapshot, quoted

TEX = Path(os.environ.get("CH32_TEX", ROOT / "zh" / "ch32_generaltheory.tex"))   # a scratch copy for mutation tests
GUIDE = "如果人人都想多储蓄，总储蓄为什么可能反而减少？"
PREV = GUIDE                                          # Chapter 31's NEXT
NEXT = "一张图装下了多少凯恩斯，又丢掉了什么？"          # Chapter 33's question
# Teaching inputs stated in the text (M1, the Keynesian cross in the cloth economy of Chapter 2)
M1 = {"a": 26, "c": 0.6, "I": 10, "I2": 14, "a2": 16, "i0": 1, "i1": 0.1}
SC1 = {"c": 0.75}                                     # self-check 1
KAHN_MEN = 100                                        # ex:generaltheory-kahn: 100 men on the roads
SHILLINGS, PENCE = 20, 12                             # a pound = 20 shillings, a shilling = 12 pence
WHITE_PAPER = 3331                                    # Cmd. 3331, named in docs/agent_prompts/part5_notes.md, not obtained
MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"], 1)}


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
    df, m = load_snapshot("generaltheory_facts", dtype=str, keep_default_na=False)
    assert 32 in m["used_in"]
    assert df["id"].is_unique
    return df


@lru_cache(maxsize=None)
def meta() -> dict:
    return load_snapshot("generaltheory_facts")[1]


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
    key = name.lower().rstrip(".")
    return next(i for m, i in MONTHS.items() if m.startswith(key))


def page(rid: str) -> int:
    """The first page (or column) number of a row's juan column: 'p. 186 (PDF p. 14)' -> 186."""
    return int(re.search(r"(?:pp?|cc?)\. (\d+)", column("juan")[rid]).group(1))


def src_year(key: str) -> int:
    """The year of a source as its 'version' prints it (the last year named)."""
    return int(re.findall(r"(?<!\d)(1[89]\d\d|20\d\d)(?!\d)", meta()["sources"][key]["version"])[-1])


def _table(name: str) -> tuple[pd.DataFrame, dict]:
    df, m = load_snapshot(name)
    assert 32 in m["used_in"], name
    assert m["fetch"] == "data/fetch/boe_millennium_gb32.py", name
    return df, m


@lru_cache(maxsize=None)
def monthly() -> pd.DataFrame:
    """The administrative unemployment rate (per cent) and its seasonally adjusted series, January 1919 - December
    1938, indexed by (year, month)."""
    df, _ = _table("boe_millennium_unemp_1919_1938_monthly")
    assert len(df) == 240 and list(df.columns) == ["year", "month", "unemp_admin", "unemp_sa"]
    return df.set_index(["year", "month"])


def admin(y: int, m: int) -> float:
    return float(monthly().loc[(y, m), "unemp_admin"])


def admin_span(y0: int, y1: int) -> pd.Series:
    s = monthly().unemp_admin
    return s[(s.index.get_level_values(0) >= y0) & (s.index.get_level_values(0) <= y1)]


@lru_cache(maxsize=None)
def annual() -> pd.DataFrame:
    df, _ = _table("boe_millennium_gb_1919_1938")
    assert list(df.year) == list(range(1919, 1939))
    return df.set_index("year")


@lru_cache(maxsize=None)
def bank_rate() -> pd.DataFrame:
    df, _ = _table("boe_millennium_bank_rate_1929_1939")
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    return df


def table_meta(name: str) -> dict:
    return _table(name)[1]


def change(col: str, y0: int, y1: int) -> float:
    """The change of an annual series from y0 to y1, per cent."""
    A = annual()
    return 100 * (A.loc[y1, col] / A.loc[y0, col] - 1)


def index_1929(col: str) -> pd.Series:
    A = annual().loc[1929:1938, col]
    return 100 * A / A.loc[1929]


GDP, CONS, INV, EXP, IMP = ("real_gdp_gbp_mn_2013", "real_consumption_gbp_mn_2013", "real_investment_gbp_mn_2013",
                            "exports_gbp_mn_2013", "imports_gbp_mn_2013")


def fall(a: float, b: float) -> float:
    return 100 * (1 - b / a)


def rise(a: float, b: float) -> float:
    return 100 * (b / a - 1)


# ---------------------------------------------------------------------------------------------------
# The teaching model
def cross(a: float, c: float, i0: float, i1: float = 0.0) -> tuple[float, float, float]:
    """Equilibrium of Y = C + I with C = a + cY and I = i0 + i1 Y, solved as a linear system: (Y, C, I)."""
    A = np.array([[1.0, -1.0, -1.0], [-c, 1.0, 0.0], [-i1, 0.0, 1.0]])
    Y, C, I = np.linalg.solve(A, np.array([0.0, a, i0]))
    return float(Y), float(C), float(I)


def model() -> dict[str, float]:
    """The numbers of ex:generaltheory-cross, ex:generaltheory-thrift and fig:generaltheory_cross."""
    a, c, I, I2, a2, i0, i1 = (M1[k] for k in ("a", "c", "I", "I2", "a2", "i0", "i1"))
    Y, C, _ = cross(a, c, I)
    Y2, C2, _ = cross(a, c, I2)
    Y3, C3, _ = cross(a2, c, I)                              # thrift, investment fixed
    Yi, Ci, Ii = cross(a, c, i0, i1)                         # investment induced, before
    Y4, C4, I4 = cross(a2, c, i0, i1)                        # and after
    return dict(Y=Y, C=C, k=1 / (1 - c), Y2=Y2, C2=C2, Y3=Y3, C3=C3, S3=Y3 - C3, Yi=Yi, Ii=Ii, Y4=Y4, C4=C4, I4=I4,
                S4=Y4 - C4)


def cloth() -> dict[str, float]:
    """Chapter 2's cloth economy (checks/check_ch02.py): income, consumption, investment, and the thrifty year."""
    Y = sum(f["output"] - f["inputs"] for f in CHAIN.values())
    return dict(Y=Y, C=CONSUMPTION, I=Y - CONSUMPTION, cut=CONSUMPTION - THRIFT_CONSUMPTION, S=Y - THRIFT_CONSUMPTION)


def kahn_rows() -> list[dict[str, Fraction]]:
    """Kahn (1931), p. 186: the four rows of his table, as transcribed, and recomputed from equation (1) with the
    shares of p. 185 (R, W, P) and m' = 5/6."""
    tr = transcription("ka_table")
    head, body = tr.split("k/(1 - k) |", 1)
    assert "W/(W + P + R) = 7/10, P/(W + P + R) = 1/5, m' = 5/6." in head
    cells = [c.strip() for c in body.split("|")]
    assert len(cells) == 20, cells
    _, r, w, p = (Fraction(x).limit_denominator(100) for x in facts()["ka_shares"])
    mprime = Fraction(facts()["ka_mprime"][1]).limit_denominator(100)
    assert (r, w, p, mprime) == (Fraction(1, 10), Fraction(7, 10), Fraction(1, 5), Fraction(5, 6))
    assert r + w + p == 1                                      # the three shares of the retail price
    out = []
    for i in range(4):
        uw, n, m, k, ratio = cells[5 * i:5 * i + 5]
        frac, printed = ratio.split(" = ")
        row = dict(uw=Fraction(uw), n=Fraction(n), m=Fraction(m), k=Fraction(k), ratio=Fraction(frac),
                   printed=float(printed.replace("·", "0.")))
        assert row["m"] == mprime * (1 - row["uw"]), row                      # m = m'(1 - U/W)
        assert row["k"] == row["m"] * w + row["n"] * p, row                  # equation (1), shares of W + P + R
        assert row["ratio"] == row["k"] / (1 - row["k"]), row                # equation (2)
        assert abs(float(row["ratio"]) - row["printed"]) <= 0.005 + 1e-9, row   # the two decimals as printed (7/8 = ·88)
        out.append(row)
    return out


def fr(x: float) -> tuple[int, int]:
    """A value of the value column as numerator and denominator: 0.428571 -> (3, 7)."""
    f = Fraction(x).limit_denominator(200)
    return f.numerator, f.denominator


def kuznets() -> pd.DataFrame:
    """The General Theory, p. 103: Kuznets's gross capital formation, maintenance and net capital formation, million
    dollars, 1925-1933, read on the page image."""
    tr = transcription("gt_kuz_gross")
    yrs = [int(y) for y in re.findall(r"\b(19\d\d)\b", tr.split("Gross")[0])]
    assert yrs == list(range(1925, 1934)) and "(Millions of Dollars)" in tr
    F = facts()
    df = pd.DataFrame({"gross": F["gt_kuz_gross"], "maint": F["gt_kuz_maint"], "net": F["gt_kuz_net"]}, index=yrs)
    assert (df.gross - df.maint == df.net).all()              # net = gross - maintenance, year by year
    return df


# ---------------------------------------------------------------------------------------------------
# 1. Readings of the numbers
SMALL = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10}
MULT = {"hundred": 100, "thousand": 1000, "million": 10 ** 6}
FRAC = {"one-tenth": 0.1, "nine-tenths": 0.9}


def cardinal(s: str) -> float:
    """An English cardinal: 'five', 'one million'."""
    total, part = 0, 0
    for w in s.lower().replace("-", " ").split():
        if w in SMALL:
            part += SMALL[w]
        else:
            part = max(part, 1) * MULT[w]
            total, part = total + part, 0
    return float(total + part)


def figure(s: str) -> float:
    """'12,000,000', '2.5'."""
    return float(s.replace(",", ""))


def read(word: str, how: str) -> list[float]:
    if how == "num":
        return [figure(word)]
    if how == "en":
        return [cardinal(word)]
    if how == "frac":
        return [FRAC[word.lower()]]
    if how == "dot":                          # '2-5': the OCR's reading of 2·5
        a, b = word.split("-")
        return [float(f"{a}.{b}")]
    raise ValueError(how)


FIGURES = re.compile(r"\d[\d,]*(?:\.\d+)?|\.\d+")
EN, NUM = "en", "num"
# id -> [(phrase, how)], in order. A phrase 'context|word' is searched as a whole and read from `word`. Rows not
# listed are read with all the figures of the quotation.
READINGS = {
    "ss_five": [("five", EN)],
    "pe_tenth": [("1924", NUM), ("one-tenth", "frac"), ("eight", EN)],
    "pe_million": [("one million", EN), ("1923", NUM)],
    "gt_ninetenths": [("nine-tenths", "frac")],
    "gt_tentimes": [("ten", EN)],
    "gt_pairs": [("less than |3", NUM), ("2-5", "dot"), ("60", NUM), ("70", NUM)],
    "oh_1931": [("four", EN), ("1931", NUM)],
    "oh_published": [("four", EN), ("1933", NUM), ("1934", NUM)],
}
# a page image: fractions '3/7', the two decimals '·94', '2½' and figures; read after the words named here
IMG_FIGURES = re.compile(r"(\d+)/(\d+)|·(\d+)|(\d[\d,]*(?:\.\d+)?)(½)?")
IMG_START = {"gt_kuz_gross": "inventories)", "gt_kuz_maint": "depletion", "gt_kuz_net": "definition)",
             "ka_table": "k/(1 - k) |"}
# the misreadings of the OCR, each named in the note of its row and printed in the quotation
MISPRINTS = [("ss_listener", "Listener^"), ("ss_12m", "in¬ dustrial"), ("ss_wrong", "un¬ luckily"),
             ("ss_surplus", "sur¬ plus"), ("ss_housewives", "adver¬ tised"), ("pe_lg", "per¬ spective"),
             ("pe_three", "re¬ duction"), ("pe_inflation", "In¬ flation"), ("pe_slack", "In¬ flation"),
             ("pe_bank", "deflation¬ ary"), ("pe_title", "4-"), ("mc_date", "Jostan"), ("ka_sign", "Kaun"),
             ("pg_title", "Picou"), ("k37_sign", "Kreynzs"), ("kc_toc", "Katecki"), ("kc_toc", "Macrodynemic"),
             ("gt_pairs", "2-5"), ("gt_liqfalls", "liquiditypreferences"), ("gt_reduce", "investmentdemand")]
IMAGE_NOTE = "read on the page image"


def read_image(rid: str) -> list[float]:
    text = transcription(rid)
    if rid in IMG_START:
        text = text.split(IMG_START[rid], 1)[1]
    out = []
    for a, b, dec, num, half in IMG_FIGURES.findall(text):
        if a:
            out.append(int(a) / int(b))
        elif dec:
            out.append(float("0." + dec))
        else:
            out.append(figure(num) + (0.5 if half else 0))
    return out


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
    quoted("rows with values, each read from its quotation", n, 72)
    quoted("rows read on a page image (no quotation)", img, 20)
    N, Q = column("note"), quotes()
    for rid, word in MISPRINTS:
        assert word in N[rid], (rid, word)                  # every misreading is named in the note
        assert word in Q[rid], (rid, word)                  # and printed in the quotation
    assert "cf raw" in N["ka_r"] and "2·5" in N["gt_pairs"] and "'io'" in N["gt_tentimes"]


# ---------------------------------------------------------------------------------------------------
# 2. Every “…” of the text against the snapshot
# the chapter's Chinese renderings of the quotations: rendering -> row (or rows)
TRANSLATIONS = {
    # the chapter guide and the section on expectations
    "动物精神": "gt_animal",
    # opening
    "在某些情况下，这些都完全对；可是在眼下的情况下，很不幸，它完全错了。": "ss_wrong",
    "我能做的最好的估计是，你每储蓄五先令，就让一个人失业一天。": "ss_five",
    "所以，爱国的主妇们，明天一早就上街去，到那些到处都在登广告的美妙的大减价里去吧。": "ss_housewives",
    "没有一个人会因此多一个便士": "ss_penny",
    "每一次这样靠减少消费来多储蓄的尝试，都会影响收入，使这种尝试必然自我挫败。": "gt_defeats",
    # sec:generaltheory-world
    "这在我们的历史上前所未有": "pe_tenth",
    "什么也没有换回来": "pe_fund",
    "结果确实令人失望": "hc29_meagre",
    "事实上，一般来说，只能创造很少的额外就业，不能创造持久的额外就业": "hc29_doctrine",
    "转移": "mc_alternative",
    "不管对不对，人们叫作财政部观点的东西": "mc_stamp",
    "银行体系的明智合作": "ka_banking",
    # sec:generaltheory-demand
    "一种更一般的理论": "gt_general",
    "供给创造自己的需求": ("gt_say", "oh_say"),
    "并没有说得很准确": "bm_keynes",
    "就像宗教裁判所征服西班牙一样彻底": "gt_inquisition",
    "另一种看法完全消失了": "gt_ceased",
    # sec:generaltheory-multiplier
    "人们通常而平均地倾向于随着收入的增加而增加消费，但增加得没有收入那么多。": "gt_psychlaw",
    "也许还是低估了": "ka_threequarters",
    "就不必再有失业": "gt_nomore",
    "盖房子之类的事要明智得多": "gt_houses",
    # sec:generaltheory-expectations
    "通常很少，而且往往微不足道": "gt_precarious",
    "一种想要行动而不是不行动的自发冲动": "gt_animal",
    "一个国家的资本发展，若成了赌场活动的副产品，这件事多半会做得很糟。": "gt_casino",
    "统计也许多少夸大了投资的下降": "gt_overstate",
    # sec:generaltheory-thrift
    "决定今天不吃晚饭": "gt_dinner",
    "我们越有美德，越是决心节俭，在国家与个人的财政上越是顽固地守旧，利率相对于资本的边际效率上升时，我们的收入就越要下降。":
        "gt_virtuous",
    "在某些情况下": "ss_wrong",
    # sec:generaltheory-liquidity
    "利率是在一段特定的时间里放弃流动性的报酬。": "gt_reward",
    "价格": "gt_notprice",
    "宁愿持有货币，而不愿持有任何别的商品": "jm_possess",
    "实际上绝对的": "gt_absolute",
    "我至今不知道有过例子": "gt_noexample",
    "只是信用的价格": "oh2_price",
    "完全是同一个东西": "k37_same",
    "可能会有好几次失手": "gt_slips",
    "只要还有失业，就业就与货币数量同比例变化；到了充分就业，物价就与货币数量同比例变化。": "gt_qt",
    # sec:generaltheory-parallel
    "两次独立的进攻": "oh_two",
    "摩擦性": "oh_frictional",
    "斯德哥尔摩学派": "oh_school",
    "循环就这样闭合了": "kc_circle",
    "一支失业的后备军": "kc_reserve",
    "前凯恩斯的世界": "bj_prekeynes",
    # sec:generaltheory-debate
    "大量的通缩性闲置": "pe_slack",
    "只能是愚蠢的人": "gt_foolish",
    "必然降低实际工资、增加就业": "pg_must",
    "向月亮射箭": "pg_arrows",
    # sec:generaltheory-check
    "全镇历史上从未有过的工业萧条": "hc36_15",
    "它的造船厂关了门": "hc36_shipyard",
    "虽然还远不能令人满意，最近几个月已有改善": "hc36b_improved",
    # the note on sources
    "正统的财政部教条": "pe_dogma",
    "正统的财政部学说": "hc29_doctrine",
    "卡那封自治市选出的议员": "hc29_lg",
    "不少于 95\\%": "gt_95",
    # the ending
    "而在于摆脱旧的想法": "gt_difficulty",
}
# the words of the source that each rendering renders (for a row read on a page image: of its transcription)
KEYWORDS = {
    "gt_animal": ["animal spirits", "of a spontaneous urge to action rather than inaction"],
    "ss_wrong": ["in certain circumstances all this would be quite right, but in present circumstances, un¬ luckily, "
                 "it is quite wrong."],
    "ss_five": ["The best guess I can make is that whenever you save five shillings, you put a man out of work for a "
                "day."],
    "ss_housewives": ["Therefore, oh patriotic housewives, sally out to-morrow early into the streets and go to the "
                      "wonderful sales which are everywhere adver¬ tised."],
    "ss_penny": ["No one would be a penny the richer"],
    "gt_defeats": ["Every such attempt to save more by reducing consumption will so affect incomes that the attempt "
                   "necessarily defeats itself."],
    "pe_tenth": ["a fact unprecedented in our history"],
    "pe_fund": ["have got literally nothing for it"],
    "hc29_meagre": ["the results have certainly been disappointing"],
    "hc29_doctrine": ["very little additional employment and no permanent additional employment can in fact and as a "
                      "general rule be created", "the orthodox Treasury doctrine"],
    "mc_alternative": ["the alternative between transfer and inflation"],
    "mc_stamp": ["What has been known, rightly or wrongly, as the Treasury view"],
    "ka_banking": ["the intelligent co-operation of the banking system is being taken for granted"],
    "gt_general": ["a more general theory"],
    "gt_say": ["supply creates its own demand"],
    "oh_say": ["the Say doctrine that supply creates its own demand"],
    "bm_keynes": ["Keynes did not get it quite right"],
    "gt_inquisition": ["Ricardo conquered England as completely as the Holy Inquisition conquered Spain."],
    "gt_ceased": ["the other point of view completely disappeared"],
    "gt_psychlaw": ["men are disposed, as a rule and on the average, to increase their consumption as their income "
                    "increases, but not by as much as the increase in their income."],
    "ka_threequarters": ["be erring in the direction of under-statement"],
    "gt_nomore": ["there need be no more unemployment"],
    "gt_houses": ["It would, indeed, be more sensible to build houses and the like"],
    "gt_precarious": ["is usually very slight and often negligible"],
    "gt_casino": ["When the capital development of a country becomes a by-product of the activities of a casino, the "
                  "job is likely to be ill-done."],
    "gt_overstate": ["it is possible that the statistics somewhat overstate the decline in investment"],
    "gt_dinner": ["a decision not to have dinner to-day"],
    "gt_virtuous": ["The more virtuous we are, the more determinedly thrifty, the more obstinately orthodox in our "
                    "national and personal finance, the more our incomes will have to fall when interest rises "
                    "relatively to the marginal efficiency of capital."],
    "gt_reward": ["the rate of interest is the reward for parting with liquidity for a specified period."],
    "gt_notprice": ['the "price" which brings into equilibrium'],
    "jm_possess": ["liked better to possess money than any other commodity"],
    "gt_absolute": ["may become virtually absolute"],
    "gt_noexample": ["I know of no example of it hitherto."],
    "oh2_price": ["the rate of interest is simply the price of credit"],
    "k37_same": ["is exactly the same thing as the quantity of saving"],
    "gt_slips": ["there may be several slips between the cup and the lip."],
    "gt_qt": ["So long as there is unemployment, employment will change in the same proportion as the quantity of "
              "money; and when there is full employment, prices will change in the same proportion as the quantity "
              "of money"],
    "oh_two": ["two independent attacks on the same set of problems"],
    "oh_frictional": ["frictional"],
    "oh_school": ["a Stockholm school of thought"],
    "kc_circle": ["Thus, the circle will close itself."],
    "kc_reserve": ["a reserve army of unemployed"],
    "bj_prekeynes": ["a pre-Keynesian world"],
    "pe_slack": ["A large amount of deflationary slack"],
    "gt_foolish": ["it can only be a foolish person"],
    "pg_must": ["must lower real wage rates and increase employment."],
    "pg_arrows": ["an artist firing arrows at the moon"],
    "hc36_15": ["a period of industrial depression without parallel in the town's history"],
    "hc36_shipyard": ["Its shipyard is closed."],
    "hc36b_improved": ["while still far from satisfactory, has improved during recent months"],
    "pe_dogma": ["the orthodox Treasury dogma"],
    "hc29_lg": ["the Member for Carnarvon Boroughs"],
    "gt_95": ["no less than 95 per cent"],
    "gt_difficulty": ["but in escaping from the old ones"],
}


def tex_text() -> str:
    return "\n".join(l for l in TEX.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("%"))


def text_quotations() -> list[str]:
    return re.findall(r"“([^”]*)”", tex_text())


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
UNITS = {"亿": 10 ** 8, "万": 10 ** 4}
AMOUNT = re.compile(r"(\d[\d,]*(?:\.\d+)?)(?:\s*(亿|万))?")
# what is not a number of the story: labels, citations, cross-references, the key equations (models() reads them)
# and the sub- and superscripts of the math
MASKS = [re.compile(r"\\begin\{keyeq\}.*?\\end\{keyeq\}", re.DOTALL),
         re.compile(r"\\(?:label|cite|chref|secref|figref|tabref|exref|eqref|ref|nameref|url|fig)\{[^}]*\}"),
         re.compile(r"_\{[^}]*\}|_\d"),
         re.compile(r"\^\{\d\}"),
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
    """The phrase is in the text, and each number it prints (with its unit 万, 亿) is the value given, within half a
    unit of its last digit (plus `slack`, in the same units). None skips a number (one checked by an assertion)."""
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
    """A Chinese numeral of the text: '五', '十', '三分之一'."""
    if "分之" in s:
        b, a = s.split("分之")
        return zh(a) / zh(b)
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
def guide(F, Y, Q):
    t = TEX.read_text(encoding="utf-8")
    assert f"\\guidequestion{{{GUIDE}}}" in t and GUIDE == PREV
    ch31 = (ROOT / "zh" / "ch31_soviet.tex").read_text(encoding="utf-8")
    ch31 = "\n".join(l for l in ch31.splitlines() if not l.lstrip().startswith("%"))
    assert ch31.rstrip().endswith(PREV)                                       # 第 31 章交来的问题
    for label in ("ch:say", "ch:depressionus"):                                # the prerequisites (PLAN: 20, 28)
        assert f"\\chref{{{label}}}\\enspace\\nameref{{{label}}}" in t, label


def opening(F, Y, Q):
    assert "(Jan. 1931)" in Q["ss_toc"] and "(Broadcast, Jan. 1931)" in Q["ss_listener"]
    said("1931 年 1 月，凯恩斯（", F["ss_toc"][0], mon("ss_toc", "Jan."))
    _, d14, y31, _ = F["ss_listener"]
    said("讲稿登在 1 月 14 日的《听众》周刊上", mon("ss_listener", "Jan."), d14)
    assert y31 == F["ss_toc"][0] and Q["ss_broadcast"] == "A Broadcast Address."
    said("大概有 1,200 万产业工人没有工作", F["ss_12m"][0])
    assert "the three chief industrial countries of the world, Great Britain, Germany, and the United States" in Q["ss_12m"]
    chk("    three countries (三个主要的工业国)", 3, told("美国这三个主要的工业国", "美国这", "个"))
    said("英国那个月的失业率是 21.1\\%", admin(1931, 1))
    chk("    five shillings (每储蓄五先令)", F["ss_five"][0], told("你每储蓄五先令", "每储蓄", "先令"))
    chk("    one man for a day (一个人失业一天)", 1, told("就让一个人失业一天", "失业", "天"))
    said("一镑合 20 先令，一先令合 12 便士", SHILLINGS, PENCE)
    chk("    a pound, a shilling (一镑、一先令)", 1, told("一镑合 20 先令", "", "镑"))
    chk("    five shillings = a quarter of a pound (四分之一镑)", F["ss_five"][0] / SHILLINGS,
        told("五先令就是四分之一镑", "就是", "镑"))
    chk("    five years later (五年以后)", Y["gt_title"] - F["ss_toc"][0], told("五年以后，凯恩斯", "", "年以后"))
    d13, y35 = F["gt_preface"]
    said("书的序言署 1935 年 12 月 13 日，书 1936 年在伦敦出版", y35, mon("gt_preface", "December"), d13, F["gt_title"][0])
    assert "LONDON" in Q["gt_title"]
    assert paragraph("他还设想了一个极端的情形").endswith(GUIDE)               # the opening ends with the question


def world(F, Y, Q):
    said("1921 年 5 月，英国的行政失业率升到 23.4\\%", 1921, 5, admin(1921, 5))
    assert admin_span(1919, 1938).idxmax() == (1921, 5)
    assert admin_span(1925, 1938).loc[(1925, 5):].min() >= 8.7                  # after the return to gold (April 1925)
    lo = admin_span(1921, 1929)
    said("1921—1929 年，这个失业率没有一个月低于 8.7\\%", 1921, 1929, lo.min())
    hi = admin_span(1932, 1933)
    said("萧条来了以后，它在 1932—1933 年最高到了 23.0\\%", 1932, 1933, hi.max())
    assert admin_span(1930, 1938).max() == hi.max()
    feinstein = int(re.search(r"Feinstein (\d{4})", table_meta("boe_millennium_gb_1919_1938")["series"]).group(1))
    said("数据集里另有 Feinstein（1972）的年度估计", feinstein)
    A = annual()
    said("1932 年有 340 万人失业，占 15.6\\%", 1932, A.loc[1932, "unemployed_000"] * 1000, A.loc[1932, "unemp_rate_civilian"])
    assert A.loc[1932, "unemp_rate_civilian"] < admin_span(1932, 1932).mean()  # 数字低一些
    # fig:generaltheory_unemp
    yearly = monthly().unemp_admin.groupby(level=0).mean()
    assert yearly.loc[1921:].min() > 9 and A.unemp_rate_civilian.idxmax() == 1932
    assert yearly.loc[1922:].idxmax() == 1932                                  # 1932 年最重 (1921: the peak month)
    said("英国的失业从 1921 年起一直居高不下，1932 年最重", 1921, 1932)
    missing = [k for k, v in monthly().unemp_admin.items() if np.isnan(v)]
    assert missing == [(1919, m) for m in range(1, 11)] + [(1920, 10)], missing
    said("1919 年 1—10 月与 1920 年 10 月缺数", 1919, 1, 10, 1920, 10)
    said("琥珀色虚线是 Feinstein（1972）的年度失业率", feinstein)
    said("圆点标出凯恩斯 1931 年 1 月的广播，竖线标出《通论》出版的 1936 年", F["ss_toc"][0], 1, Y["gt_title"])
    src = table_meta("boe_millennium_unemp_1919_1938_monthly")
    version = float(re.search(r"version (\d\.\d)", src["source"]).group(1))
    dm = int(re.search(r"Denman and Macdonald (\d{4})", src["series"]).group(1))
    assert "M5. Administrative unemp" in src["source"] and "A50. Employment" in table_meta(
        "boe_millennium_gb_1919_1938")["source"]
    said("数据：英格兰银行《千年宏观数据》（3.1 版）表 M5（Denman 与 Macdonald 1996）与 A50", version, 5, dm, 50)
    # 1929: the election, Can Lloyd George Do It?
    said("1929 年 5 月英国举行大选", F["pe_title"][1], mon("pe_title", "May"))
    assert "General Election, May 1929" in Q["pe_title"] and F["hh_lloydgeorge_pm"][3] < 1929   # 前首相
    said("凯恩斯 1931 年编《劝说集》时", F["ep_copyright"][0])
    y24, tenth, eight = F["pe_tenth"]
    said("除了 1924 年回到金本位以前短暂的恢复", y24)
    chk("    one tenth (十分之一)", tenth, told("这个国家有十分之一或更多", "有", "或更多"))
    chk("    eight years (八年)", eight, told("已经失业了八年", "失业了", "年"))
    said("自 1923 年开始统计以来从没有少于 100 万", F["pe_million"][1], F["pe_million"][0])
    y29, today = F["pe_today"]
    said("1929 年 4 月，失业的工人有 114 万", y29, mon("pe_today", "April"), today)
    # the cost of unemployment
    a, y21, b = F["pe_fund"]
    said("失业基金每年要付出约 5,000 万镑的现金，1921 年以来已经付出约 5 亿镑", a, y21, b)
    y24, w, y21, waste = F["pe_220"]
    said("按 1924 年的生产普查，一个英国工人一年的净产值约 220 镑", y24, w)
    said("照这个数算，1921 年以来失业白白浪费的产出约有 20 亿镑", y21, waste)
    pa, men = F["pe_500k"]
    said("劳合·乔治估计，每年 1 亿镑的开发计划能让 50 万人重新就业", pa, men)
    p5, y21, p25 = F["pe_25"]
    said("这笔钱只相当于 1921 年以来失业损失的 5\\%，约合国民收入的 2.5\\%", y21, p5, p25)
    chk("    100 million is 5 per cent of 2,000 million", 100 * pa / waste, p5)
    # the Treasury view
    d15, y29, *_ = F["hc29_chancellor"]
    assert "The CHANCELLOR of the EXCHEQUER (Mr. Churchill)" in Q["hc29_chancellor"]
    said("1929 年 4 月 15 日，财政大臣丘吉尔", y29, mon("hc29_chancellor", "April"), d15)
    said("他的政府在这一届议会里花掉或承诺的开发支出已有 4 亿多镑", F["hc29_400m"][0])
    said("劳合·乔治要花 2 亿镑、主要用来修路的计划", F["hc29_lg"][0])
    assert "mainly on road construction" in Q["hc29_lg"]
    # the Macmillan Committee
    d28, y29 = F["mc_first"]
    said("1929 年 11 月 28 日，金融与工业委员会", y29, mon("mc_first", "November"), d28)
    assert Q["mc_keynes"] == "Mr. J. M. KEYNES, C.B."
    d4, y30 = F["mc_date"]
    said("1930 年 4 月 4 日，斯坦普", y30, mon("mc_date", "April"), d4)
    assert F["mc_keynesq"][0] == 4003 and "Q. 4002" in column("note")["mc_alternative"]
    # Kahn
    said("在 1931 年 6 月的《经济学杂志》上提出的", F["ka_june"][0], mon("ka_june", "JUNE"))


def demand(F, Y, Q):
    assert column("juan")["gt_special"] == "p. 3"                              # 第一章只有一段 (p. 3)
    chk("    chapter 1 (第一章)", 1, told("《通论》的第一章只有一段", "的第", "章"))
    assert "including (for example) J. S. Mill, Marshall, Edgeworth and Prof. Pigou" in Q["gt_pigou"]
    said("照 Baumol（1999）的说法，现在一般认为", src_year("baumol1999"))
    assert "Say's law" in transcription("gt_saylaw") and "no obstacle to full employment" in transcription("gt_saylaw")


def multiplier(F, Y, Q):
    say("Y=C+I,\\quad C=a+cY\\qquad\\Longrightarrow\\qquad Y^{*}=\\frac{a+I}{1-c},\\qquad \\Delta Y^{*}=\\frac{\\Delta I}"
        "{1-c}.\\label{eq:generaltheory-cross}")
    said("其中$0<c<1$", 0, 1)
    said("$1/(1-c)$叫作\\textbf{投资乘数}", 1, 1)
    said("合计是$1+c+c^{2}+\\cdots=1/(1-c)$", 1, 1, 1)
    said("$45^{\\circ}$线上产出等于支出", 45)
    ex_cross(F)
    say("k=\\frac{mW+nP}{W+P+R},\\qquad m=m'\\Bigl(1-\\frac{U}{W}\\Bigr),\\qquad \\frac{\\text{次级就业}}{\\text{初级就业}}"
        "=k+k^{2}+\\cdots=\\frac{k}{1-k}.\\label{eq:generaltheory-kahn}")
    assert Q["ka_m"] == "Then m'(W - U) = mW"                                   # m = m'(1 - U/W)
    assert "k + k^2 + k^3 + . . . = k/(1 - k)" in transcription("ka_eq")
    chk("    four leakages (四处)", 4, told("漏出有四处", "有", "处"))
    ex_kahn(F)
    said("若假定实际的比例是 3/4", *fr(F["ka_threequarters"][0]))
    m9 = F["gt_ninetenths"][0]
    said("若边际消费倾向是 0.9，乘数就是 10，公共工程带来的总就业会是初级就业的 10 倍", m9, 1 / (1 - m9),
         F["gt_tentimes"][0])
    chk("    the multiplier of nine-tenths = ten times", 1 / (1 - m9), F["gt_tentimes"][0])


def ex_cross(F) -> None:
    a, c, I, I2 = M1["a"], M1["c"], M1["I"], M1["I2"]
    M, K = model(), cloth()
    said("沿用\\exref{ex:accounts-thrift}的棉布经济，收入 90，家庭买布 80，投资 10", K["Y"], K["C"], K["I"])
    said("设消费函数是$C=26+0.6Y$", a, c)
    said("边际消费倾向取 0.6，落在凯恩斯估计的范围之内", c)
    chk("    0.6 = 1 - 1/2.5, the MPC of Keynes's multiplier", 1 - 1 / F["gt_pairs"][1], c)
    said("（1）均衡收入是多少？（2）乘数是多少？（3）投资从 10 增加到 14", 1, 2, 3, I, I2)
    said("（1）$Y^{*}=(26+10)/(1-0.6)=90$，消费$26+0.6\\times90=80$", 1, a, I, 1, c, M["Y"], a, c, M["Y"], M["C"])
    chk("    the cross reproduces Chapter 2's accounts (Y, C)", [M["Y"], M["C"]], [K["Y"], K["C"]])
    said("（2）乘数$1/(1-0.6)=2.5$", 2, 1, 1, c, M["k"])
    dI, dY = I2 - I, M["Y2"] - M["Y"]
    said("（3）$\\Delta Y=2.5\\times4=10$，收入到 100；消费到$26+0.6\\times100=86$，增加 6", 3, M["k"], dI, dY, M["Y2"],
         a, c, M["Y2"], M["C2"], M["C2"] - M["C"])
    said("多出的 4 先成为收入，花掉 2.4，再花掉 1.44，合计$4+2.4+1.44+\\cdots=10$", dI, c * dI, c * c * dI, dI, c * dI,
         c * c * dI, sum(dI * c ** j for j in range(200)))
    chk("    the rounds add up to the multiplier", sum(dI * c ** j for j in range(200)), dY)


def ex_kahn(F) -> None:
    T = kahn_rows()
    _, r, w, p = F["ka_shares"]
    said("进口的原料与半成品占 1/10，工资占 7/10，利润占 1/5", *fr(r), *fr(w), *fr(p))
    imp, mp = F["ka_mprime"]
    chk("    1/6 imported, so m' = 5/6", imp + mp, 1, tol=1e-5)
    said("有 1/6 花在进口的成品上，即$m'=5/6$", *fr(imp), *fr(mp))
    said("他认为救济与工资之比$U/W$略低于 1/2，$n$不会低到 1/3", *fr(F["ka_uw"][0]), *fr(F["ka_n"][0]))
    assert "rather less than 1/2" in transcription("ka_uw") and "as small a proportion as 1/3" in transcription("ka_n")
    t0 = T[0]
    said("表~\\ref{tab:generaltheory-kahn}的第一行取$U/W=3/7$、$n=3/4$", *fr(t0["uw"]), *fr(t0["n"]))
    assert t0["uw"] < Fraction(F["ka_uw"][0]) and t0["n"] > Fraction(F["ka_n"][0]).limit_denominator(10)
    said("（1）$m$与$k$各是多少？（2）每 100 人修路", 1, 2, KAHN_MEN)
    mp_ = Fraction(mp).limit_denominator(10)
    said("（1）$m=\\frac{5}{6}\\times\\bigl(1-\\frac{3}{7}\\bigr)=\\frac{10}{21}$", 1, mp_.numerator, mp_.denominator, 1,
         t0["uw"].numerator, t0["uw"].denominator, t0["m"].numerator, t0["m"].denominator)
    wf, pf = Fraction(w).limit_denominator(10), Fraction(p).limit_denominator(10)
    mw, np_ = t0["m"] * wf, t0["n"] * pf
    said("$k=\\frac{10}{21}\\times\\frac{7}{10}+\\frac{3}{4}\\times\\frac{1}{5}=\\frac{1}{3}+\\frac{3}{20}=\\frac{29}{60}$",
         t0["m"].numerator, t0["m"].denominator, wf.numerator, wf.denominator, t0["n"].numerator, t0["n"].denominator,
         pf.numerator, pf.denominator, mw.numerator, mw.denominator, np_.numerator, np_.denominator,
         t0["k"].numerator, t0["k"].denominator)
    second = KAHN_MEN * float(t0["ratio"])
    said("（2）次级就业与初级就业之比是$k/(1-k)=29/31\\approx0.94$，100 人修路，另有约 94 人就业，合计约 194 人", 2, 1,
         t0["ratio"].numerator, t0["ratio"].denominator, t0["printed"], KAHN_MEN, second, KAHN_MEN + second)
    mult = 1 / (1 - t0["k"])
    said("乘数是$1/(1-k)=60/31\\approx1.94$，比\\exref{ex:generaltheory-cross}的 2.5 小", 1, 1, mult.numerator,
         mult.denominator, float(mult), model()["k"])
    chk("    1/(1 - k) = 1 + k/(1 - k)", float(mult), 1 + float(t0["ratio"]))
    # tab:generaltheory-kahn, row by row as printed
    for t in T:
        cells = " & ".join(f"{f.numerator}/{f.denominator}" for f in (t["uw"], t["n"], t["m"], t["k"]))
        said(f"{cells} & {t['ratio'].numerator}/{t['ratio'].denominator} = {t['printed']:.2f}", *fr(t["uw"]),
             *fr(t["n"]), *fr(t["m"]), *fr(t["k"]), *fr(t["ratio"]), t["printed"])
    said("Kahn（1931）第 186 页的表", Y_of("kahn1931"), page("ka_table"))
    said("$U/W$ & $n$ & $m=m'(1-U/W)$ & $k$ & $k/(1-k)$", 1, 1)               # the head of the table
    said("共同的假定是$W/(W+P+R)=7/10$，$P/(W+P+R)=1/5$，$m'=5/6$", *fr(w), *fr(p), *fr(mp))


def Y_of(key: str) -> int:
    return src_year(key)


def expectations(F, Y, Q):
    K = kuznets()
    g, n = K.gross, K.net
    said("1929—1932 年美国的毛资本形成下降了 77.4\\%，净资本形成下降了 95.1\\%", 1929, 1932, fall(g[1929], g[1932]),
         fall(n[1929], n[1932]))
    said("美国的资本形成，1925—1933 年（百万美元）", K.index[0], K.index[-1])
    for y, r in K.iterrows():
        said(f"{y} & {r.gross:,.0f} & {r.maint:,.0f} & {r.net:,.0f}", y, r.gross, r.maint, r.net)
    said("Keynes（1936）第 103 页的表", Y["gt_title"], page("gt_kuz_gross"))
    said("凯恩斯说这些数取自美国国家经济研究局第 52 号公报", F["gt_bulletin"][0])
    assert "Gross capital formation (after allowing for net change in business inventories)" in transcription(
        "gt_kuz_gross") and "on Mr. Kuznets' definition" in transcription("gt_kuz_net")
    # ex:generaltheory-kuznets
    p3, p25, lo, hi = F["gt_pairs"]
    said("（1）1929—1932 年，毛资本形成与净资本形成各下降了百分之几？（2）1932 年的净资本形成，比 1925—1929 年的平均数低百分之几？"
         "（3）凯恩斯说，把年份两两合在一起看，乘数小于 3，大概稳定在 2.5 附近", 1, 1929, 1932, 2, 1932, 1925, 1929, 3, p3, p25)
    assert "grouped in pairs" in Q["gt_pairs"]
    said("（1）毛资本形成从 34,491 降到 7,780，下降 77.4\\%；净资本形成从 25,481 降到 1,237，下降 95.1\\%", 1, g[1929],
         g[1932], fall(g[1929], g[1932]), n[1929], n[1932], fall(n[1929], n[1932]))
    o75, y32, y29, o95 = F["gt_overstate"]
    said("凯恩斯说，投资据说下降了 75\\% 以上，净资本形成下降了 95\\% 以上", o75, o95)
    assert fall(g[1929], g[1932]) > o75 and fall(n[1929], n[1932]) > o95 and (y29, y32) == (1929, 1932)
    avg = n.loc[1925:1929].mean()
    said("（2）1925—1929 年的平均数是 24,434.4，1932 年比它低 94.9\\%", 2, 1925, 1929, avg, 1932, fall(avg, n[1932]))
    said("（3）$1-1/2.5=0.6$；乘数小于 3，即边际消费倾向小于$1-1/3\\approx0.67$", 3, 1, 1, p25, 1 - 1 / p25, p3, 1, 1, p3,
         1 - 1 / p3)
    said("边际消费倾向不超过 60\\%—70\\%", lo, hi)
    assert lo <= 100 * (1 - 1 / p25) and 100 * (1 - 1 / p3) <= hi + 0.5


def thrift(F, Y, Q):
    a, c, I, a2, i0, i1 = (M1[k] for k in ("a", "c", "I", "a2", "i0", "i1"))
    M, K = model(), cloth()
    said("\\exref{ex:accounts-thrift}里，家庭决定少买 10 的布", K["cut"])
    said("设家庭在每一个收入水平上都少消费 10，$a$从 26 降到 16", a - a2, a, a2)
    said("投资仍是 10。按式", I)
    said("新的均衡收入是$(16+10)/0.4=65$，消费是 55，储蓄是$65-55=10$", a2, I, 1 - c, M["Y3"], M["C3"], M["Y3"], M["C3"],
         M["S3"])
    said("家庭想多储蓄 10，储蓄却一点也没有增加", a - a2)
    chk("    saving unchanged with investment fixed", M["S3"], I)
    said("收入少了 25，正好是 10 乘以乘数 2.5", M["Y"] - M["Y3"], a - a2, M["k"])
    said("设投资是$I=1+0.1Y$，收入为 90 时投资仍是 10", i0, i1, M["Yi"], M["Ii"])
    chk("    the induced-investment economy starts at Chapter 2's accounts", [M["Yi"], M["Ii"]], [K["Y"], K["I"]])
    said("家庭同样少消费 10，收入降到约 56.7，投资与储蓄都降到约 6.7", a - a2, M["Y4"], M["I4"])
    chk("    saving = investment in the new equilibrium", M["S4"], M["I4"])
    assert M["S4"] < M["S3"] == I                                               # 总储蓄反而减少了
    # fig:generaltheory_cross
    said("(a) 支出线$C+I$与$45^{\\circ}$线相交于收入 90；投资从 10 增加到 14，支出线上移 4，收入增加 10，乘数是 2.5", 45,
         M["Y"], I, M1["I2"], M1["I2"] - I, M["Y2"] - M["Y"], M["k"])
    said("家庭在每个收入上都想多储蓄 10", a - a2)
    said("投资固定在 10 时，收入从 90 降到 65，储蓄仍是 10", I, M["Y"], M["Y3"], M["S3"])
    said("投资随收入变化（$I=1+0.1Y$，琥珀色虚线）时，收入降到约 56.7，储蓄降到约 6.7", i0, i1, M["Y4"], M["S4"])
    said("数字为教学输入，$C=26+0.6Y$", a, c)
    # ex:generaltheory-thrift
    said("消费函数从$C=26+0.6Y$变成$C=16+0.6Y$", a, c, a2, c)
    said("（1）投资固定在 10，新的收入、消费与储蓄各是多少？（2）投资是$I=1+0.1Y$", 1, I, 2, i0, i1)
    said("（3）\\exref{ex:accounts-thrift}里第一年的储蓄是 20，这与（1）（2）的结果矛盾吗", 3, K["S"], 1, 2)
    said("（1）$Y=(16+10)/(1-0.6)=65$，$C=16+0.6\\times65=55$，$S=65-55=10$", 1, a2, I, 1, c, M["Y3"], a2, c, M["Y3"],
         M["C3"], M["Y3"], M["C3"], M["S3"])
    said("（2）原来$Y=(26+1)/(1-0.6-0.1)=90$", 2, a, i0, 1, c, i1, M["Yi"])
    said("新的$Y=(16+1)/0.3\\approx56.7$，$I=1+0.1\\times56.7\\approx6.7$，$C=16+0.6\\times56.7=50$，$S=56.7-50\\approx6.7$",
         a2, i0, 1 - c - i1, M["Y4"], i0, i1, M["Y4"], M["I4"], a2, c, M["Y4"], M["C4"], M["Y4"], M["C4"], M["S4"])
    said("（3）不矛盾。第一年的 20 里有 10 是卖不掉的布", 3, K["S"], K["cut"])
    chk("    the year of Chapter 2: saving 20 = planned 10 + unsold cloth 10", K["S"], K["I"] + K["cut"])
    said("投资固定时是 10，投资随收入下降时只有约 6.7", I, M["I4"])
    said("凯恩斯 1931 年的广播并没有这样说", F["ss_toc"][0])
    assert "capital-goods such as houses, factories, roads, machines" in column("note")["ss_object"]
    chk("    two conditions (两个条件)", 2, told("要有两个条件", "要有", "个条件"))


def liquidity(F, Y, Q):
    say("M=M_1+M_2=L_1(Y)+L_2(r).\\label{eq:generaltheory-liquidity}")
    assert "Thus M = M1 + M2 = L1(Y) + L2(r)" in transcription("gt_l1l2")
    assert "(i) the transactions-motive" in Q["gt_motives"] and "(ii)the precautionary-motive" in Q["gt_motives"]
    chk("    three motives (三个动机)", 3, told("凯恩斯举了三个动机", "举了", "个动机"))
    chk("    two parts (两部分)", 2, told("分成两部分", "分成", "部分"))
    said("1937 年 6 月，俄林", F["oh2_june"][0], mon("oh2_june", "JUNE"))
    assert F["oh2_june"] == [Y["k37_title"]] and "J. M. Kreynzs" in Q["k37_sign"]   # 同一期
    said("\\begin{compare}{可贷资金与流动性偏好}{可贷资金（俄林，1937）}{流动性偏好（凯恩斯，1936）}", F["oh2_june"][0],
         Y["gt_title"])
    said("1705 年的主张", 1705)
    said("照 Velde（2003）的说法，劳的名声在 1930 年代上升了", src_year("velde2003"), F["velde_1930s"][0])
    assert "a rise in Law's reputation" in Q["velde_1930s"]
    chk("    three slips (几道关口: three)", 3, sum(1 for r in ("gt_liqfalls", "gt_mecfalls", "gt_propensityfalls")
                                                  if Q[r].startswith("this ")))
    assert "Quantity Theory of Money" in Q["gt_simplify"] and Q["gt_wageunit"].startswith("(4)")


def parallel(F, Y, Q):
    said("\\begin{case}{瑞典 · 1931—1937 · 斯德哥尔摩学派}", F["oh_1931"][1], Y["oh_title"])
    said("1937 年 3 月，俄林在《经济学杂志》上", Y["oh_title"], mon("oh_march", "MARCH"))
    four, y31 = F["oh_1931"]
    said("照俄林的说法，1931 年底，瑞典的失业委员会请四位经济学家写专题报告", y31)
    assert "late in 1931" in Q["oh_1931"]
    chk("    four economists (四位)", four, told("请四位经济学家", "请", "位"))
    four2, y33, y34 = F["oh_published"]
    said("四份报告在 1933 年底到 1934 年初出版", y33, y34)
    chk("    four reports (四份)", four2, told("四份报告在", "", "份报告"))
    said("照 Berg 与 Jonung（1998）的说法，缪尔达尔还为财政大臣维格福斯", src_year("berg1998"))
    said("1933 年的预算写了一份报告", F["bj_myrdal"][0])
    said("委员会 1935 年的总结报告", F["oh_1935"][0])
    y33 = F["kc_leyden"][0]
    said("1933 年 10 月在莱顿的计量经济学会会议上宣读，1935 年刊在《计量经济学》上", y33, mon("kc_leyden", "October"),
         F["kc_copyright"][0])
    a, b = F["bj_prekeynes"]
    said("瑞典 1931—1932 年的货币计划", a, 1900 + b)
    said("照 Shizume（2009）的记述", src_year("shizume30"))


def debate(F, Y, Q):
    said("\\subsubsection{1929 年的财政部观点错了吗}", Y["hc29_ref"])
    said("4 亿多镑的开发支出", F["hc29_400m"][0])
    said("1845 年前后的铁路热里", F["hc29_railway"][0])
    assert "round about 1845" in Q["hc29_railway"]
    chk("    three answers (三层)", 3, told("回答有三层", "有", "层"))
    assert all(w in Q["pe_three"] for w in ("The first source", "The second source", "The third source"))
    chk("    three sources (三个来源)", 3, told("有三个来源", "有", "个来源"))
    said("卡恩 1931 年的估计", Y["ka_june"])
    said("庇古的回答在 1936 年 5 月的《经济学刊》上", Y["pg_title"], mon("pg_may", "MAY"))
    said("像英国 1925—1929 年那样失业严重的时候", *F["pg_case"])
    said("1925—1929 年削减货币工资的理由", *F["pg_stronger"])
    assert "England experienced from 1925 to 1929" in Q["pg_case"]


def check_section(F, Y, Q):
    said("1929—1932 年英国的实际 GDP 下降了 5.3\\%", 1929, 1932, -change(GDP, 1929, 1932))
    said("实际投资下降了 14.1\\%，出口量下降了 32.2\\%", -change(INV, 1929, 1932), -change(EXP, 1929, 1932))
    said("实际消费反而增加了 2.1\\%", change(CONS, 1929, 1932))
    # fig:generaltheory_uk
    said("英国的萧条与复苏，1929—1938 年", 1929, 1938)
    idx = {c: index_1929(c) for c in (GDP, CONS, INV, EXP)}
    assert idx[EXP].idxmin() == 1932 and idx[CONS].min() >= 100 - 1e-9
    gains = {c: idx[c][1937] / idx[c][1932] for c in idx}
    assert max(gains, key=gains.get) == INV                                     # 投资领先回升
    said("1929 年$=100$。1932 年出口量最低，消费一直没有低于 1929 年；1932 年以后投资领先回升", 1929, 100, 1932, 1929, 1932)
    R = bank_rate()
    cut = R[R.bank_rate == 2.0].iloc[0]
    nxt = R[R.date > cut.date].iloc[0]
    assert (cut.date.year, cut.date.month, cut.date.day) == (1932, 6, 30) and nxt.bank_rate > 2.0
    said("(b) 英格兰银行的贴现率，1932 年 6 月 30 日降到 2\\%，一直保持到 1939 年 8 月", cut.date.year, cut.date.month,
         cut.date.day, cut.bank_rate, nxt.date.year, nxt.date.month)
    am = table_meta("boe_millennium_gb_1919_1938")
    version = float(re.search(r"version (\d\.\d)", am["source"]).group(1))
    assert "A1. Headline series" in am["source"] and "D1" in table_meta("boe_millennium_bank_rate_1929_1939")["source"]
    said("数据：英格兰银行《千年宏观数据》（3.1 版）表 A1 与 D1", version, 1, 1)
    T = kahn_rows()
    said("他对英国的估计，次级就业是初级就业的 0.56 到 0.94\\cite{kahn1931}", T[-1]["printed"], T[0]["printed"])
    said("凯恩斯对美国估计的乘数是 2.5 左右", F["gt_pairs"][1])
    said("1932 年 6 月 30 日，英格兰银行把贴现率降到 2\\%，一直保持到 1939 年 8 月", cut.date.year, cut.date.month,
         cut.date.day, cut.bank_rate, nxt.date.year, nxt.date.month)
    said("1932—1937 年，英国的实际投资增加了 47.7\\%，实际 GDP 增加了 22.9\\%", 1932, 1937, change(INV, 1932, 1937),
         change(GDP, 1932, 1937))
    A = annual()
    said("按 Feinstein 的口径，失业率从 1932 年的 15.6\\% 降到 1937 年的 7.8\\%", 1932, A.loc[1932, "unemp_rate_civilian"],
         1937, A.loc[1937, "unemp_rate_civilian"])
    said("1938 年它又升到 9.3\\%", 1938, A.loc[1938, "unemp_rate_civilian"])
    # Jarrow
    d4, y36, *_ = F["hc36_ref"]
    said("1936 年 11 月 4 日，贾罗选出的议员威尔金森", y36, mon("hc36_ref", "November"), d4)
    d14, y35 = F["hh_wilkinson_jarrow"]
    assert (y35, mon("hh_wilkinson_jarrow", "November"), d14) < (y36, 11, d4)  # the member for Jarrow since 1935
    assert "(Miss Wilkinson)" in Q["hc36b_member"] and "Member for Jarrow" in Q["hc36b_member"]
    said("过去 15 年", F["hc36_15"][0])
    said("从前雇用 8,000 人的地方，现在只有 100 人在一个临时项目上做工", *F["hc36_8000"])
    assert "temporary scheme" in Q["hc36_8000"]
    d28, a, b = F["hc36b_1185"]
    said("9 月 28 日贾罗有 1,185 名失业的造船工人，另有 818 名普通劳工失业", mon("hc36b_1185", "September"), d28, a, b)
    said("他又转述首相 10 月 29 日的答复", mon("hc36b_member", "October"), F["hc36b_member"][0])
    b0, b1 = F["hh_runciman_bt"]
    assert b0 <= y36 <= b1 and "The PRESIDENT of the BOARD of TRADE (Mr. Runciman)" == Q["hc36b_runciman"]
    assert admin_span(1921, 1938).min() >= 8.7 and 11 <= 1938 - 1921 + 1 <= 19   # 十几年居高不下
    say("失业率连续十几年居高不下")


def deeper(F, Y, Q):
    said("1936 年麦克米伦公司初版", Y["gt_title"])
    assert "MACMILLAN AND CO., LIMITED" in Q["gt_title"]
    pages = [page(r) for r in ("gt_effdemand", "gt_saylaw", "gt_kuz_gross", "gt_reward", "gt_l1l2", "gt_qt")]
    said("第 25—26 页的总需求与总供给、第 103 页的表、第 167 页利率的定义、第 199 页的式子与第 296 页数量论的改写", *pages)
    assert page("gt_partly") == pages[-1]
    chk("    the price, five shillings (五先令)", F["gt_price"][0], told("书的定价五先令", "定价", "先令"))
    said("正文只写 1936 年", Y["gt_title"])
    said("都据 1931 年《劝说集》的识别文本", F["ep_copyright"][0])
    m6, d14, y31, _ = F["ss_listener"]
    said("前者注明 1931 年 1 月广播，讲稿登在 1 月 14 日的《听众》上", y31, mon("ss_listener", "Jan."), 1, d14)
    four, y29 = F["pe_ref"]
    said("后者注明出自与亨德森合写的小册子（1929 年 5 月）", y29, mon("pe_ref", "May"))
    assert "jointly with H. D. Henderson" in Q["pe_ref"] and four == 4 and m6 == 6
    said("丘吉尔说劳合·乔治要花 2 亿镑，凯恩斯与亨德森说的是每年 1 亿镑", F["hc29_lg"][0], F["pe_500k"][0])
    _, _, _, c27, _ = F["hc29_chancellor"]
    _, _, _, c53, c6 = F["hc29_ref"]
    said("丘吉尔的名字只出现在演说的第一页（第 27 栏），引文在第 53—56 栏", c27, c53, 50 + c6)
    assert "no speaker is named" in column("note")["hc29_ref"]
    notes = (ROOT / "docs" / "agent_prompts" / "part5_notes.md").read_text(encoding="utf-8")
    assert f"Cmd. {WHITE_PAPER}" in notes
    said("1929 年的白皮书（Cmd. 3331）没有取得", Y["hc29_ref"], WHITE_PAPER)
    said("美国国家经济研究局第 52 号公报没有取得", F["gt_bulletin"][0])
    n = kuznets().net
    y29, y32, p95, y25, y29b = F["gt_95"]
    said("凯恩斯说 1932 年的净资本形成比 1925—1929 年的平均数低“不少于 95\\%”，按表算是 94.9\\%", y32, y25, y29b, p95,
         fall(n.loc[1925:1929].mean(), n[1932]))
    said("缪尔达尔 1933 年给预算写的报告", F["bj_myrdal"][0])
    said("斯德哥尔摩学派的四份报告与 1935 年的总结报告，据俄林 1937 年的介绍", F["oh_1935"][0], Y["oh_title"])


def legacy(F, Y, Q):
    said("\\begin{compare}{凯恩斯本人与凯恩斯交叉}{凯恩斯本人（1936）}", Y["gt_title"])


def takeaways(F, Y, Q):
    said("1921—1938 年，英国的行政失业率没有一个月低于 8.7\\%", 1921, 1938, admin_span(1921, 1938).min())
    said("1929 年，财政部认为国家借钱只能创造很少的额外就业", Y["hc29_ref"])
    T = kahn_rows()
    said("投资变动$\\Delta I$，收入变动$\\Delta I/(1-c)$", 1)
    said("他对英国的估计，次级就业是初级就业的 0.56 到 0.94。", T[-1]["printed"], T[0]["printed"])
    chk("    three gates (三道关口)", 3, told("要过利率、投资与消费倾向三道关口", "消费倾向", "道关口"))


def selfcheck(F, Y, Q):
    a, c, I = M1["a"], M1["c"], M1["I"]
    c2 = SC1["c"]
    said("边际消费倾向从 0.6 提高到 0.75", c, c2)
    T = kahn_rows()
    said("验算$k=43/120$", T[-1]["k"].numerator, T[-1]["k"].denominator)
    M = model()
    said("的（1）里，家庭少消费 10，收入却下降了 25", 1, M1["a"] - M1["a2"], M["Y"] - M["Y3"])
    said("1929—1932 年，英国的实际消费增加了 2.1\\%，实际 GDP 下降了 5.3\\%", 1929, 1932, change(CONS, 1929, 1932),
         -change(GDP, 1929, 1932))
    said("1929 年财政部与凯恩斯争论的是什么", Y["hc29_ref"])
    # the answers
    Y2, _, _ = cross(a, c2, I)
    said("$Y^{*}=(26+10)/(1-0.75)=144$，乘数$1/(1-0.75)=4$", a, I, 1, c2, Y2, 1, 1, c2, 1 / (1 - c2))
    t = T[-1]
    _, _, w, p = F["ka_shares"]
    mp = Fraction(F["ka_mprime"][1]).limit_denominator(10)
    wf, pf = Fraction(w).limit_denominator(10), Fraction(p).limit_denominator(10)
    one = 1 - t["uw"]
    mw, np_ = t["m"] * wf, t["n"] * pf
    assert (mw + np_) == t["k"] and mw.denominator == 24 and np_.denominator == 15          # 35/120 and 8/120
    said("$m=\\frac{5}{6}\\times\\frac{1}{2}=\\frac{5}{12}$。$k=\\frac{5}{12}\\times\\frac{7}{10}+\\frac{1}{3}\\times"
         "\\frac{1}{5}=\\frac{35}{120}+\\frac{8}{120}=\\frac{43}{120}$，$k/(1-k)=43/77\\approx0.56$", mp.numerator,
         mp.denominator, one.numerator, one.denominator, t["m"].numerator, t["m"].denominator, t["m"].numerator,
         t["m"].denominator, wf.numerator, wf.denominator, t["n"].numerator, t["n"].denominator, pf.numerator,
         pf.denominator, mw * 120, 120, np_ * 120, 120, t["k"].numerator, t["k"].denominator, 1, t["ratio"].numerator,
         t["ratio"].denominator, t["printed"])
    said("又少花其中的 0.6。合计是$10\\times2.5=25$", c, M1["a"] - M1["a2"], M["k"], M["Y"] - M["Y3"])
    chk("    two grounds (两条)", 2, told("庇古概括的常见理由有两条", "有", "条"))
    assert "on the familiar grounds" in Q["pg_strong"]


def ending(F, Y, Q):
    said("1931 年 1 月，凯恩斯在广播里说，每储蓄五先令", F["ss_toc"][0], 1)
    chk("    five shillings (每储蓄五先令)", F["ss_five"][0], told("每储蓄五先令，就让一个人失业一天。五年", "每储蓄", "先令"))
    chk("    five years (五年以后出版)", Y["gt_title"] - F["ss_toc"][0], told("五年以后出版的《通论》", "", "年以后"))
    chk("    five shillings (定价也是五先令)", F["gt_price"][0], told("定价也是五先令", "也是", "先令"))
    assert "5s." in Q["gt_price"]
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 33's question"
    assert t.index("\\end{answers}") < t.index("1931 年 1 月，凯恩斯在广播里说")
    ch33 = (ROOT / "zh" / "ch33_islm.tex").read_text(encoding="utf-8")
    assert f"\\guidequestion{{{NEXT}}}" in ch33


def models() -> None:
    """The key equations, and their arithmetic checked with numbers."""
    rng = np.random.default_rng(32)
    # eq:generaltheory-cross: Y* = (a + I)/(1 - c); dY = dI/(1 - c) = dI (1 + c + c^2 + ...)
    for _ in range(20):
        a, c, I, dI = rng.uniform(5, 50), rng.uniform(0.05, 0.95), rng.uniform(1, 30), rng.uniform(-5, 5)
        Y, C, _ = cross(a, c, I)
        chk("    eq:generaltheory-cross: Y* = (a + I)/(1 - c)", Y, (a + I) / (1 - c), tol=1e-9)
        chk("    Y = C + I", Y, C + I, tol=1e-9)
        Y2, _, _ = cross(a, c, I + dI)
        chk("    dY = dI/(1 - c) = the sum of the rounds", Y2 - Y, sum(dI * c ** j for j in range(2000)), tol=1e-7)
        # the paradox of thrift: a lower a leaves saving unchanged with I fixed, lowers it with I = i0 + i1 Y
        _, _, I0 = cross(a, c, I, 0.0)
        Y3, C3, _ = cross(a - 5, c, I)
        chk("    thrift, I fixed: S = I", Y3 - C3, I0, tol=1e-9)
        i1 = rng.uniform(0.01, 0.9) * (1 - c)
        Ya, Ca, _ = cross(a, c, I, i1)
        Yb, Cb, Ib = cross(a - 5, c, I, i1)
        assert Yb - Cb < Ya - Ca and abs((Yb - Cb) - Ib) < 1e-9                # saving falls with income
    # eq:generaltheory-kahn: for each man in primary employment k + k^2 + ... = k/(1 - k) men in secondary employment
    for _ in range(20):
        W, P, R = rng.uniform(1, 10, 3)
        U, mp, n = rng.uniform(0, W), rng.uniform(0, 1), rng.uniform(0, 1)
        m = mp * (1 - U / W)
        chk("    m'(W - U) = mW", mp * (W - U), m * W, tol=1e-9)
        k = (m * W + n * P) / (W + P + R)
        assert 0 <= k < 1
        chk("    k + k^2 + ... = k/(1 - k)", sum(k ** j for j in range(1, 3000)), k / (1 - k), tol=1e-6)


def figures_data(F) -> None:
    """What the figures assert of their data."""
    M = monthly()
    assert M.unemp_admin.dropna().between(0, 30).all() and M.index[0] == (1919, 1) and M.index[-1] == (1938, 12)
    A = annual()
    assert A.unemp_rate_civilian.dropna().index[0] == 1920
    idx = {c: index_1929(c) for c in (GDP, CONS, INV, EXP)}
    assert all(abs(s[1929] - 100) < 1e-9 for s in idx.values())
    R = bank_rate()
    assert R.date.is_monotonic_increasing and R.date.iloc[0] == pd.Timestamp("1929-01-01")
    mm = model()
    assert mm["Y4"] < mm["Y3"] < mm["Y"] < mm["Y2"]


# ---------------------------------------------------------------------------------------------------
# 5. The book
# the life dates from rows of the snapshot: words -> (row, index of the birth year, index of the death year)
ROW_LIVES = {"John Maynard Keynes，1883—1946": ("loc_keynes", 0, 1),
             "David Lloyd George，1863—1945": ("hh_lloydgeorge", 0, 2),
             "Hubert Henderson，1890—1952": ("loc_henderson", 0, 1),
             "Winston Churchill，1874—1965": ("hh_churchill", 0, 2),
             "Josiah Stamp，1880—1941": ("loc_stamp", 0, 1),
             "Richard Kahn，1905—1989": ("bnf_kahn", 0, 1),
             "David Ricardo，1772—1823": ("loc_ricardo", 0, 1),
             "John Stuart Mill，1806—1873": ("loc_mill", 0, 1),
             "Arthur Cecil Pigou，1877—1959": ("loc_pigou", 0, 1),
             "Jean-Baptiste Say，1767—1832": ("loc_say", 0, 1),
             "Thomas Robert Malthus，1766—1834": ("loc_malthus", 0, 1),
             "Simon Kuznets，1901—1985": ("loc_kuznets", 0, 1),
             "Adam Smith，1723—1790": ("loc_smith", 0, 1),
             "John Law，1671—1729": ("loc_law", 0, 1),
             "Bertil Ohlin，1899—1979": ("loc_ohlin", 0, 1),
             "Knut Wicksell，1851—1926": ("loc_wicksell", 0, 1),
             "Gunnar Myrdal，1898—1987": ("loc_myrdal", 0, 1),
             "Ernst Wigforss，1881—1977": ("loc_wigforss", 0, 1),
             "Michał Kalecki，1899—1970": ("bnf_kalecki", 0, 1),
             "高桥是清（1854—1936": ("loc_takahashi", 0, 1),
             "Ellen Wilkinson，1891—1947": ("hh_wilkinson", 0, 2),
             "Walter Runciman，1870—1949": ("hh_runciman", 0, 2)}
# the beginning of each record's heading
HEADS = {"loc_keynes": "Keynes, John Maynard", "hh_lloydgeorge": "Mr David Lloyd George",
         "loc_henderson": "Henderson, Hubert Douglas", "hh_churchill": "Mr Winston Churchill",
         "loc_stamp": "Stamp, Josiah", "bnf_kahn": "Richard Ferdinand Kahn", "loc_ricardo": "Ricardo, David",
         "loc_mill": "Mill, John Stuart", "loc_pigou": "Pigou, A. C. (Arthur Cecil)", "loc_say": "Say, Jean Baptiste",
         "loc_malthus": "Malthus, T. R. (Thomas Robert)", "loc_kuznets": "Kuznets, Simon", "loc_smith": "Smith, Adam",
         "loc_law": "Law, John", "loc_ohlin": "Ohlin, Bertil", "loc_wicksell": "Wicksell, Knut",
         "loc_myrdal": "Myrdal, Gunnar", "loc_wigforss": "Wigforss, Ernst", "bnf_kalecki": "Michał Kalecki",
         "loc_takahashi": "Takahashi, Korekiyo", "hh_wilkinson": "Miss Ellen Wilkinson",
         "hh_runciman": "Mr Walter Runciman"}
# what other chapters tell: (words of this chapter, chapter where it is told, words there)
EVENTS = [("\\chref{ch:interwar}讲过，1921 年 5 月，英国的行政失业率升到 23.4\\%", "ch27_interwar",
           "1921 年 5 月升到 23.4\\%"),
          ("沿用\\exref{ex:accounts-thrift}的棉布经济，收入 90，家庭买布 80，投资 10", "ch02_accounts",
           "家庭消费 $C=80$；留在仓库里的纱是存货的增加，算作投资 $I=10$；$C+I=90$"),
          ("\\exref{ex:accounts-thrift}里，家庭决定少买 10 的布", "ch02_accounts", "只买 70"),
          ("\\exref{ex:accounts-thrift}里第一年的储蓄是 20", "ch02_accounts", "储蓄 $S=20$"),
          ("一镑合 20 先令，一先令合 12 便士", "ch27_interwar", "一英镑是 240 便士"),
          ("\\chref{ch:say}里，穆勒说过人们在某些时候“宁愿持有货币，而不愿持有任何别的商品”", "ch20_say",
           "“宁愿持有货币，而不愿持有任何别的商品”"),
          ("照\\chref{ch:say}的区分，凯恩斯的写法更像萨伊恒等式，他真正要质疑的却是均衡版", "ch20_say",
           "区分萨伊定律的几种表述（恒等式版与均衡版）"),
          ("每年省下的东西照常被消费掉，只是消费的人不同（\\chref{ch:smith}）", "ch18_smith",
           "每年省下来的，和每年花掉的一样，照常被消费掉"),
          ("这是\\chref{ch:mercantilism}里约翰·劳（John Law，1671—1729）1705 年的主张", "ch16_mercantilism",
           "劳在 1705 年说，货币的多少决定了能雇多少人"),
          ("第一个等式就是\\chref{ch:marx}的式~\\eqref{eq:marx-kalecki}，即毛利润等于毛投资加资本家的消费", "ch22_marx",
           "\\text{毛利润}=\\text{毛投资}+\\text{资本家的消费}"),
          ("\\chref{ch:alternatives}讲过，瑞典、日本与德国的扩张政策，都在《通论》出版以前开始", "ch30_alternatives",
           "三国的这些政策，都在凯恩斯的《通论》出版以前就开始了"),
          ("\\chref{ch:intro}的主线说，大萧条让萨伊定律失去了说服力", "ch01_intro", "大萧条让它失去了说服力"),
          ("前凯恩斯的世界", "ch30_alternatives", "“前凯恩斯的世界”")]
# the chapters this one hands on to (new FORWARD_REFS rows opened by Chapter 32)
LATER = {"ch:islm": "ch33_islm", "ch:budget": "ch50_budget", "ch:naturalrate": "ch44_naturalrate",
         "ch:phillips": "ch38_phillips", "ch:consumption": "ch39_consumption", "ch:multipliers": "ch68_multipliers",
         "ch:warfinance": "ch34_warfinance"}


def book(F, Q):
    """Life dates and what other chapters tell."""
    t = tex_text()
    for words, (rid, i, j) in ROW_LIVES.items():
        assert words in t, words
        assert f"{F[rid][i]:.0f}—{F[rid][j]:.0f}" in words, (words, rid)
        assert Q[rid].startswith(HEADS[rid]), (rid, Q[rid])                      # the person of the record
        COVERED.append(words)
    assert "Prof. Pigou" in Q["gt_pigou"] and "Mr. R. F. Kahn" in Q["gt_kahnhelp"]
    for here, ch, there in EVENTS:
        assert here in t, here
        assert there in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (ch, there)
    chk("    20 shillings of 12 pence = 240 pence (Chapter 27)", SHILLINGS * PENCE, 240)
    for label, ch in LATER.items():
        assert f"{{{label}}}" in t, label
        assert f"\\label{{{label}}}" in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (label, ch)
    print(f"ok {len(ROW_LIVES)} life dates, {len(EVENTS)} statements of other chapters, {len(LATER)} later chapters")


def witnesses(F, Q):
    """Second witnesses of statements of the text, and the bibliography block of the chapter."""
    # the Treasury view: Churchill in Hansard ('doctrine'), as Keynes and Henderson quote him ('dogma'), and Stamp
    assert "orthodox Treasury doctrine which has steadfastly held" in Q["hc29_doctrine"]
    assert "orthodox Treasury dogma, steadfastly held" in Q["pe_dogma"]
    assert "the Treasury view" in Q["mc_stamp"] and "The orthodox Treasury view" in Q["hc29_view"]
    # Kuznets: the table of p. 103 against Keynes's words on pp. 104 and 128
    n, g = kuznets().net, kuznets().gross
    chk("net capital formation 1932 below the 1925-1929 average: table 94.9 against Keynes's 'no less than 95'",
        fall(n.loc[1925:1929].mean(), n[1932]), F["gt_95"][2], tol=0.2)
    assert fall(g[1929], g[1932]) > F["gt_overstate"][0] and fall(n[1929], n[1932]) > F["gt_overstate"][3]
    # Kahn: the table of p. 186 against equation (1) and the assumptions of p. 185 (kahn_rows asserts each row)
    assert len(kahn_rows()) == 4
    # dates of the people pages against Hansard
    assert F["hh_lloydgeorge_seat"][1] <= 1929 <= F["hh_lloydgeorge_seat"][3]  # the member for Caernarvon in 1929
    assert "Carnarvon Boroughs" in Q["hc29_lg"] and Q["hh_lloydgeorge_seat"].startswith("Caernarvon District of Boroughs")
    assert F["hh_runciman_bt"][0] <= 1936 <= F["hh_runciman_bt"][1]
    # the broadcast: the contents and the list of sources of Essays in Persuasion
    assert F["ss_toc"][0] == F["ss_listener"][2] == F["ss_listener"][3]
    # Kalecki: presented in 1933, published in 1935
    assert F["kc_leyden"][0] < F["kc_copyright"][0]
    # the licences and the bibliography
    m = meta()
    lic = m["license"]
    for rid in ("gt_copyright", "ep_copyright", "kc_copyright"):
        assert Q[rid] in lic or f"row {rid}" in lic, rid
    assert Q["kc_copyright"] in lic
    for words in ("Contains Parliamentary information licensed under the Open Parliament Licence v3.0.",
                  "may still be in copyright in the United States", "short phrases only", "Licence Ouverte",
                  "public data", "out of Crown copyright", "Project Gutenberg"):
        assert words in lic, words
    for name in ("boe_millennium_unemp_1919_1938_monthly", "boe_millennium_gb_1919_1938",
                 "boe_millennium_bank_rate_1929_1939"):
        assert "please cite this source" in table_meta(name)["license"], name
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    start = bib.index("% ---- 第 32 章")
    following = re.search(r"^% ---- 第 \d+ 章", bib[start + 1:], re.MULTILINE)
    end = start + 1 + following.start() if following else bib.index("\\end{thebibliography}")
    block = bib[start:end]
    items = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", block)}
    opl = "“Contains Parliamentary information licensed under the Open Parliament Licence v3.0.”"
    for key in ("hansard1929", "hansard1936", "hansardpeople32"):
        assert opl in items[key], key
    assert "© UK Parliament" in items["hansardpeople32"]
    assert Q["kc_copyright"] in items["kalecki1935"]
    assert "Katecki, M.: A Macrodynemic Theory of Business Cycles" == Q["kc_toc"] and Q["kc_toc"] in items["kalecki1935"]
    for key in ("keynes1936", "keynes1931b", "keynes1929c"):
        assert "公有领域" in items[key] and "只引短句" in items[key], key
    assert "在美国可能仍受版权保护" in items["keynes1936"] and "in.ernet.dli.2015.115101" in items["keynes1936"]
    assert "generaltheoryofe0000unse" not in bib                                    # the lending copy is not used
    for key in ("kahn1931", "pigou1936", "ohlin1937", "ohlin1937b", "kalecki1935", "keynes1937"):
        assert "只引短语" in items[key], key
    assert "公共数据" in items["loc32"] and "Licence Ouverte" in items["bnf32"]
    for rid in [r for r in ROW_LIVES.values()]:
        r = rid[0]
        if r.startswith("loc_"):
            assert Q[r].rsplit(",", 1)[0].replace("-", "--") in items["loc32"].replace("--", "--"), r
            assert m["sources"][column("file")[r]]["url"].split("/")[-1].split(".")[0] in items["loc32"], r
        if r.startswith("bnf_"):
            assert Q[r] in items["bnf32"], r
            assert m["sources"][column("file")[r]]["url"] in items["bnf32"], r
        if r.startswith("hh_"):
            assert m["sources"][column("file")[r]]["url"] in items["hansardpeople32"], r
    # every source of the snapshot is named by its URL in its item (the page images with the text they belong to)
    item_of = {"keynes1936img": "keynes1936", "keynes1929cimg": "keynes1929c", "kahn1931img": "kahn1931",
               "hansard1929a": "hansard1929", "hansard1936b": "hansard1936", "shizume30": "shizume2009"}
    for key, s in m["sources"].items():
        item = item_of.get(key, key)
        if key.startswith(("loc_", "bnf_", "hh_")) or item not in items:
            continue
        if key == "keynes1929c":                                       # the same text file as keynes1931b
            assert s["url"] == m["sources"]["keynes1931b"]["url"] and "识别文本同上条" in items[key]
            continue
        assert s["url"] in items[item].replace("\\%", "%").replace("\\_", "_"), key
    for key in ("keynes1931b", "keynes1937", "kahn1931", "pigou1936", "ohlin1937", "ohlin1937b", "kalecki1935",
                "hansard1929", "hansard1936"):
        assert any(item_of.get(k, k) == key for k in m["sources"]), key
    allitems = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", bib)}
    keys = set(allitems)
    cited = {k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", tex_text()) for k in c.split(",")}
    assert cited <= keys, sorted(cited - keys)
    assert set(items) <= cited, sorted(set(items) - cited)
    srcs = set(m["sources"])
    for key in items:                                                              # every work of the block is a source
        assert key in srcs or key in ("loc32", "bnf32", "hansardpeople32"), key
    print(f"ok {len(cited)} works cited, {len(items)} of them in the bibliography block of Chapter 32")


NAMES = "Feinstein|Baumol|Velde|Berg|Jonung|Shizume|Denman|Macdonald|Kuznets|Moggridge|Skidelsky"


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
    demand(F, Y, Q)
    multiplier(F, Y, Q)
    expectations(F, Y, Q)
    thrift(F, Y, Q)
    liquidity(F, Y, Q)
    parallel(F, Y, Q)
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
