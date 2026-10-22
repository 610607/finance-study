"""Chapter 28 (大萧条：美国): every number and every quotation in zh/ch28_depressionus.tex.

    python3 checks/check_ch28.py

Inputs:
  depressionus_facts    quotations of Roosevelt's fireside chat of 12 March 1933, Proclamations 2039, 2040 and 2072,
                        Executive Order 6102 and the White House statement of 31 January 1934 (the American
                        Presidency Project), the Statutes at Large (47 Stat. 56, 48 Stat. 1, 162, 337), the Federal
                        Reserve Bulletin (February 1933, February and September 1937), Fisher (1933), Bernanke (NBER
                        Working Paper 1054, 1983; the remarks of 8 November 2002), Romer (NBER Working Papers 2639
                        and 3829), Bordo, Redish and Rockoff (NBER Working Paper 17312), Federal Reserve History, the
                        Canada Year Book 1934-35 and the authority records of the BnF and the Library of Congress
                        (checked by data/fetch/verify_web_quotes.py); the rows with an empty quotation are values
                        read on page images (Bernanke's Table 2; the Bulletin's Tables 1 and 12)
  depressionus_annual   the United States 1921-1941: bank suspensions and their deposits (Bulletin, September 1937),
                        the consumer price index (Historical Statistics E 135), the money stock and its parts (X
                        410-417), unemployment (D 85-86), and the Federal Reserve's accounts, interest rates and
                        indexes (Bulletin, February 1937, p. 112)
  bea_nipa_annual       Chapter 2's snapshot: nominal GDP and real GDP in chained 2017 dollars
The figure module figsrc/fig_ch28.py imports annual(), bea(), output_index() and cpi_years() from here.

What is checked here:
  1. readings   every number of the value column of depressionus_facts is read from its quotation (digits, English
                number words, ordinals, fractions, mixed numbers, and the OCR's misprints, each named in the note);
                the values read on page images are named as such in their notes and tied by identities (section 5)
  2. the text   every “…” of the chapter is the chapter's Chinese rendering of a quotation (TRANSLATIONS:
                rendering -> row or rows), with the source's words listed in KEYWORDS
  3. numbers    every number of the text, section by section: said() finds the phrase in the text and compares each
                number it prints (with its unit 万, 亿) with the value computed from the snapshots or with a teaching
                input stated in the text, within half a unit of the last printed digit; Chinese numerals (三成,
                三分之一, 九折 ...) are read by zh() and compared the same way
  4. coverage   every Arabic number of the text (outside labels, citations, cross-references, the key equations and
                math subscripts) lies inside a phrase checked by said(), so that changing any of them fails
  5. the book   identities of the annual snapshot, second witnesses, life dates, what other chapters tell, the
                bibliography block of the chapter and its licence notices
  6. anchors    the paraphrase anchors `% 据: ...` name rows of depressionus_facts

Models (the chapter's key equations):
    the fire sale (eq:depressionus-firesale): to raise W - R the bank sells book value (W - R)/(1 - delta); the loss
        is delta/(1 - delta) (W - R), and the bank is insolvent when the loss exceeds its capital E = R + A - D
    the real debt (eq:depressionus-debt): (D_1/P_1)/(D_0/P_0) = (1 - x)/(1 + pi)
    the money multiplier (Chapter 4's eq:money-mult): m = 1/(c + r - c r), c = C/M, r = R/D, M = m H, H = C + R
    the gold dollar: the dollar price of an ounce of gold is inversely proportional to the gold in a dollar
"""
from __future__ import annotations

import math
import re
from datetime import date
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd
from common import ROOT, anchors, load_snapshot, quoted

TEX = ROOT / "zh" / "ch28_depressionus.tex"
GUIDE = "一次股市崩盘为什么会变成持续数年、产出与物价同时坍塌的萧条？"
NEXT = "金本位怎样把萧条传到全世界？"           # the first half of Chapter 29's guide question
# Teaching inputs stated in the text
RUN = {"R": 10, "A": 90, "D": 92, "W": 30}       # ex:depressionus-run (九折, 七折 are read from the text)
SC1 = {"R": 5, "A": 95, "D": 94, "W": 25}        # self-check 1 (八折; the answer's 七折)
LOAN = {"D": 1000, "i": 5, "fall": 10, "repay": 20}   # ex:depressionus-debt
SC2 = {"repay": 10, "fall": 10}                  # self-check 2
DECADE20 = 1920                                  # "1920 年代的过度负债" (the compare box)
M6, B9 = 10 ** 6, 10 ** 9                        # a million, a billion (American)


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
def _rows() -> pd.DataFrame:
    df, m = load_snapshot("depressionus_facts", dtype=str, keep_default_na=False)
    assert 28 in m["used_in"]
    assert df["id"].is_unique
    return df


def meta() -> dict:
    return load_snapshot("depressionus_facts")[1]


def num(x: str) -> float:
    return float(x)


def facts() -> dict[str, list[float]]:
    """id -> the numbers of the value column (several are separated by ';')."""
    return {r.id: [num(x) for x in r.value.split(";")] for r in _rows().itertuples() if r.value}


def years() -> dict[str, int]:
    return {r.id: int(r.year) for r in _rows().itertuples() if r.year.isdigit()}


def quotes() -> dict[str, str]:
    """id -> the quotation, with the line breaks of the source joined."""
    return {r.id: " ".join(r.quote.split()) for r in _rows().itertuples()}


def column(name: str) -> dict[str, str]:
    return {r.id: getattr(r, name) for r in _rows().itertuples()}


def annual_meta() -> dict:
    return load_snapshot("depressionus_annual")[1]


def annual() -> pd.DataFrame:
    """The United States 1921-1941, indexed by year (NaN where a source has no figure)."""
    df, m = load_snapshot("depressionus_annual")
    assert 28 in m["used_in"]
    df = df.set_index("year")
    assert list(df.index) == list(range(1921, 1942))
    return df


def bea_meta() -> dict:
    return load_snapshot("bea_nipa_annual")[1]


def bea() -> pd.DataFrame:
    """Chapter 2's NIPA snapshot, 1929-1941: nominal GDP and real GDP (millions of current and of chained 2017
    dollars) and the implicit GDP deflator (2017 = 100)."""
    df, m = load_snapshot("bea_nipa_annual")
    assert "Millions of current dollars; gdp_real_2017 in millions of chained 2017 dollars" in m["notes"]
    df = df.set_index("year").loc[1929:1941, ["gdp", "gdp_real_2017"]].astype(float)
    df["deflator"] = 100 * df.gdp / df.gdp_real_2017
    return df


def base_year() -> int:
    """The base year of BEA's chained dollars."""
    return int(re.search(r"chained (\d{4}) dollars", bea_meta()["notes"]).group(1))


def cpi_years() -> list[int]:
    """The years from 1929 on for which the CPI has a figure without a gap (1937 is left empty: its misprint)."""
    cpi = annual().cpi_1967_100
    out = []
    for y in range(1929, 1942):
        if pd.isna(cpi[y]):
            break
        out.append(y)
    return out


def output_index() -> pd.DataFrame:
    """Real GDP, the GDP deflator and the CPI, 1929 = 100, 1929-1941 (the CPI only for cpi_years())."""
    B, A = bea(), annual()
    out = pd.DataFrame({"real": 100 * B.gdp_real_2017 / B.gdp_real_2017[1929],
                        "deflator": 100 * B.deflator / B.deflator[1929]})
    cpi = A.cpi_1967_100.loc[cpi_years()]
    out["cpi"] = 100 * cpi / cpi[1929]
    return out


def money_table() -> pd.DataFrame:
    """tab:depressionus-money, billions of dollars: C currency held by the public (X 410), D commercial bank deposits
    (X 411), M = C + D, R = vault cash (X 416) + member bank reserve balances (Bulletin), H = C + R, the ratios
    c = C/M and r = R/D and the multiplier m = M/H; the years with a Bulletin figure for the reserve balances."""
    A = annual()
    yrs = [y for y in range(1929, 1937) if not pd.isna(A.member_reserves_m[y])]
    a = A.loc[yrs]
    T = pd.DataFrame({"C": a.currency_bn, "D": a.deposits_bn})
    T["M"] = T.C + T.D
    T["R"] = a.vault_cash_bn + a.member_reserves_m / 1000
    T["H"] = T.C + T.R
    T["c"], T["r"] = T.C / T.M, T.R / T.D
    T["m"] = T.M / T.H
    return T


def mult(c: float, r: float) -> float:
    """Chapter 4's eq:money-mult."""
    return 1 / (c + r - c * r)


def unemployment_rule() -> tuple[int, int]:
    """D 85-86: before 1947 the labour force counts persons 14 years old and over."""
    m = re.search(r"prior to (\d{4}), (\d+) years old and over", annual_meta()["series"])
    return int(m.group(1)), int(m.group(2))


def hsus_year() -> int:
    return int(re.search(r"Colonial Times to 1970 \((\d{4})\)", annual_meta()["source"]).group(1))


def series_no(letter: str, what: str) -> int:
    """The number of a Historical Statistics series named in the annual snapshot's description."""
    return int(re.search(re.escape(letter) + r" (\d+) " + re.escape(what), annual_meta()["series"]).group(1))


# ---------------------------------------------------------------------------------------------------
# 1. Readings of the numbers
SMALL = {"a": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "twelve": 12, "fifteen": 15, "nineteen": 19, "twenty": 20, "thirty": 30, "fifty": 50}
MULT = {"hundred": 100, "thousand": 1000}
ORDINAL = {"half": 2, "third": 3, "thirds": 3, "tenths": 10}
NTH = {"first": 1, "fourth": 4, "sixth": 6, "eighth": 8, "ninth": 9, "ninetieth": 90}
# misprints of the OCR, each named in the note of its row
OCR = {"11.1": 4.1, "11.2": 4.2, "19761": 1976}


def cardinal(s: str) -> float:
    """An English cardinal: 'twelve', 'thirty-seven', 'Nineteen Hundred and Thirty-three'."""
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
    """'1,015,000,000', '59.06', '.88'."""
    return float(s.replace(",", ""))


def read(word: str, how: str) -> list[float]:
    if how == "num":
        return [figure(word)]
    if how == "en":
        return [cardinal(word)]
    if how == "frac":                          # 'one-third', 'two-thirds', 'nine-tenths'
        a, b = word.lower().split("-")
        return [float(Fraction(int(cardinal(a)), ORDINAL[b]))]
    if how == "half":
        return [0.5]
    if how == "nth":                           # 'the fourth-largest bank', 'the Sixth District'
        return [float(NTH[word.lower()])]
    if how == "mixed":                         # '15 5/21', '25 8/10', '2-1/2'
        whole, frac = re.split(r"[ -]", word)
        a, b = frac.split("/")
        return [float(int(whole) + Fraction(int(a), int(b)))]
    if how == "hm":                            # '3.10 o'clock': hours and minutes
        h, m = word.split(".")
        return [float(h), float(m)]
    if how == "bn":                            # 'two billion'
        return [cardinal(word.split()[0]) * 1e9]
    if how == "gap":                           # '1,- 028,347,000': a line break inside the number
        return [float(re.sub(r"\D", "", word))]
    if how == "ocr":
        return [float(OCR[word])]
    raise ValueError(how)


FIGURES = re.compile(r"\d[\d,]*(?:\.\d+)?|\.\d+")
EN, NUM = "en", "num"
# id -> [(phrase, how)], in order. A phrase 'context|word' is searched as a whole and read from `word`. Rows not
# listed are read with all the figures of the quotation.
READINGS = {
    "fdr_tomorrow": [("twelve", EN)],
    "fdr_newcurrency": [("twelve", EN)],
    "app_2039_dates": [("Sixth", "nth"), ("Ninth", "nth"), ("Nineteen Hundred and Thirty-three", EN)],
    "app_2040_date": [("9", NUM), ("One Thousand Nine Hundred and Thirty three", EN)],
    "p2072_old": [("25.8", NUM), ("nine-tenths", "frac")],
    "p2072_weight": [("15 5/21", "mixed"), ("nine-tenths", "frac")],
    "p2072_time": [("3.10", "hm"), ("31", NUM)],
    "wh_5906": [("59.06", NUM), ("25 8/10", "mixed"), ("nine-tenths", "frac")],
    "wh_fund": [("two billion", "bn")],
    "frh_poised": [("1930", NUM), ("three", EN), ("1920", NUM), ("1923", NUM), ("1926", NUM), ("fifteen", EN)],
    "frh_fifteen": [("1929", NUM), ("fifteen", EN)],
    "frh_cascade": [("one-third", "frac"), ("2007", NUM)],
    "frh_bus": [("11", NUM), ("fourth", "nth")],
    "frh_outcomes": [("Sixth", "nth"), ("Eighth", "nth")],
    "frh_hoarding": [("1964", NUM)],
    "frh_gsprov": [("Two", EN)],
    "frh_mar4": [("4", NUM), ("twelve", EN), ("thirty-seven", EN)],
    "frh_mar13": [("13", NUM), ("four", EN)],
    "frh_178": [("1.78", NUM), ("four", EN), ("8", NUM)],
    "frh_twothirds": [("two-thirds", "frac")],
    "bern_title": [("8", NUM), ("2002", NUM), ("Ninetieth", "nth")],
    "bern_four": [("four", EN), ("Three", EN), ("one", EN)],
    "bern_oct1931": [("9", NUM), ("1931", NUM), ("2-1/2", "mixed"), ("16", NUM), ("3-1/2", "mixed")],
    "bern_26": [("twenty-six", EN)],
    "bern_fs1963": [("1963", NUM)],
    "bern83_pct": [("1930", NUM), ("1933", NUM), ("5.6", NUM), ("10.5", NUM), ("7.8", NUM), ("12.9", NUM),
                   ("1933", NUM), ("half", "half"), ("1929", NUM)],
    "bern83_half_output": [("(|11.1", "ocr"), ("(|11.2", "ocr"), ("mid-|1930", NUM), ("1933", NUM), ("half", "half")],
    "bern83_march": [("1933", NUM), ("seven", EN)],
    "bern83_mse": [("fifty", EN)],
    "rom92_m1": [("10", NUM), ("1933", NUM), ("1937", NUM)],
    "rom92_dr": [("8.86", NUM), ("1933", NUM), ("6.67", NUM), ("1942", NUM)],
    "rom92_darby": [("19761", "ocr")],
    "brr_copyright": [("2011", NUM), ("two", EN)],
    "fis_dominant": [("two", EN)],
    "fis_diseases": [("two", EN)],
    "fis_links": [("nine", EN), ("(|1", NUM), ("(|2", NUM)],
    "frb_june30": [("30", NUM), ("1933", NUM), ("985", NUM), ("$|1,- 028,347,000", "gap"), ("114", NUM),
                   ("239,268,000", NUM), ("1,983", NUM), ("1,063,984,000", NUM)],
    "loc_bernanke": [("|53", NUM)],
}
# the misprints of the OCR, each named in the note of its row (and printed in the quotation)
MISPRINTS = [("bern83_half_output", "(11.1)"), ("bern83_mse", "(p.1)"), ("bern83_mse", "(p.3)"),
             ("bern83_mse", "(U.14)"), ("bern83_squeeze", "of'"), ("rom92_darby", "(19761"), ("rom92_m1", "Ml"),
             ("rom92_33pct", "CUP"), ("rom92_fed", ")"), ("rom90_later", "FrIedman"), ("fis_title", "FIsHEer"),
             ("fis_dominant", "réle"), ("frb_14948", "14,948"), ("frb_june30", "$1,- 028,347,000")]
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
    quoted("rows with values, each read from its quotation", n, 173)
    quoted("rows read on a page image (no quotation)", img, 6)
    N, Q = column("note"), quotes()
    for rid, word in MISPRINTS:
        assert word in N[rid], (rid, word)                  # every misprint is named in the note
        assert word in Q[rid], (rid, word)                  # and printed in the quotation


# ---------------------------------------------------------------------------------------------------
# 2. Every “…” of the text against the snapshot
# the chapter's Chinese renderings of the quotations: rendering -> row (or rows)
TRANSLATIONS = {
    # opening
    "银行并不把钱放进保险库": "fdr_vault",
    "只是全部银行存款的一小部分": "fdr_fraction",
    "明天，星期一": "fdr_tomorrow",
    "没有一家健全的银行，比它上星期一关门时少了一块钱": "fdr_lastmonday",
    "把钱存在重新开门的银行里，比放在床垫底下安全": "fdr_mattress",
    # sec:depressionus-world, sec:depressionus-panics
    "自由黄金": "frh_freegold",
    "短期内最急的一次加息": "bern_sharpest",
    "不再负这个责任": "frh_responsibility",
    "远低于真实价值": "fdr_panicprices",
    # sec:depressionus-fisher
    "债务病": "fis_diseases",
    "美元病": "fis_diseases",
    "胀大": "fis_link3",
    "债务人还得越多，欠得越多。": "fis_paradox",
    "不必要的、残酷的破产、失业与饥饿": "fis_needless",
    "只有债务病，没有美元病，只是重感冒，不是肺炎": "fis_strong2",
    "愚蠢而不道德的": "fis_silly",
    # sec:depressionus-money
    "悲剧性地证明了货币力量的重要": "bern_tragic",
    # sec:depressionus-fed
    "清算派": "frh_liquidationist",
    "维持相当数量的会员银行超额准备": "frb_policy",
    "也许可以避免": "frh_meltzer",
    # sec:depressionus-credit
    "信贷紧缩": "bern83_squeeze",
    "对少数安全的借款人是松的，对其他所有人都很难借": "bern83_easy",
    "添了一笔": "bern_embellish",
    # sec:depressionus-recovery
    "严重的紧急状态已经存在": "eba_emergency",
    "利润": "wh_fund",
    "59.06\\% 多一点": "wh_5906",
    "不是因为它不起作用，而是因为没有试过": "rom92_brown",
    # the 史料说明
    "3 月 3d": "fdr_march3d",
    "上个星期": "frh_lastweek",
    "上星期一": "fdr_lastmonday",
    "清算论": "bern_mellon",
    "(11.1)": "bern83_half_output",
    # the legacy and the takeaways
    "稍稍滥用一下": "bern_abusing",
    "关于大萧条，你们是对的，是我们造成的。我们非常抱歉。但是多亏了你们，我们不会再犯了。": "bern_sorry",
    "债务人还得越多，欠得越多": "fis_paradox",
    # the ending
    "比通货更重要，比黄金更重要，那就是人民的信心": "fdr_confidence",
    "我们齐心，就不会失败。": "fdr_together",
}
# the words of the source that each rendering renders
KEYWORDS = {
    "fdr_vault": ["the bank does not put the money into a safe deposit vault"],
    "fdr_fraction": ["is only a small fraction of the total deposits in all of the banks"],
    "fdr_tomorrow": ["we start tomorrow, Monday"],
    "fdr_mattress": ["it is safer to keep your money in a reopened bank than under the mattress"],
    "frh_freegold": ['Bankers called the excess "free gold."'],
    "bern_sharpest": ["the sharpest rise within so brief a period in the whole history of the System"],
    "frh_responsibility": ['"no longer take responsibility"', '"with deficient reserves"'],
    "fdr_panicprices": ["at panic prices far below their real value"],
    "fis_diseases": ["the debt disease", "(or dollar disease)"],
    "fis_link3": ["a swelling of the dollar"],
    "fis_paradox": ["The more the debtors pay, the more they owe."],
    "fis_strong2": ["We would have had the debt disease, but not the dollar disease", "the bad cold but not the pneumonia"],
    "fis_needless": ["the so-called \u2018\u2018natural\u2019\u2019 way out of a depression",
                     "via needless and cruel bankruptcy, unemployment, and starvation"],
    "bern_tragic": ["a tragic testimonial to the importance of monetary forces"],
    "frb_policy": ["of maintaining a substantial amount of excess member bank reserves"],
    "bern83_easy": ["money was easy for a few safe borrowers but difficult for everyone else"],
    "fis_silly": ["as silly and immoral"],
    "frh_liquidationist": ['labeled "liquidationist."'],
    "frh_meltzer": ["might have been avoided"],
    "bern83_squeeze": ["this credit squeeze"],
    "bern_embellish": ["is simply an embellishment of the Friedman-Schwartz story"],
    "eba_emergency": ["a serious emergency exists"],
    "wh_fund": ['Of this "profit"'],
    "wh_5906": ["59.06 plus percent"],
    "rom92_brown": ["not because it did not work, but because it was not tried"],
    "fdr_march3d": ['"March 3d"'],
    "frh_lastweek": ["when it closed its doors last week"],
    "fdr_lastmonday": ["No sound bank is a dollar worse off than it was when it closed its doors last Monday."],
    "bern_mellon": ["Andrew Mellon's infamous 'liquidationist' thesis"],
    "bern83_half_output": ["equations (11.1) and (11.2)"],
    "bern_abusing": ["abusing slightly my status as an official representative of the Federal Reserve"],
    "fdr_confidence": ["more important than currency, more important than gold, and that is the confidence of the people"],
    "fdr_together": ["Together we cannot fail."],
    "bern_sorry": ["Regarding the Great Depression. You're right, we did it. We're very sorry. But thanks to you, "
                   "we won't do it again."],
}


def tex_text() -> str:
    return "\n".join(l for l in TEX.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("%"))


def text_quotations() -> list[str]:
    return re.findall(r"“([^”]*)”", tex_text())


def check_text(df: pd.DataFrame) -> None:
    ids = set(df["id"])
    Q = quotes()
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
                assert q in Q[rid], (q, rid)
    stale = set(TRANSLATIONS) - used
    assert not stale, f"listed but not in the text: {sorted(stale)}"
    for rid, words in KEYWORDS.items():
        for w in words:
            assert w in Q[rid], f"{rid}: {w!r} not in the quotation"
    assert set(KEYWORDS) == {r for t in TRANSLATIONS.values() for r in ((t,) if isinstance(t, str) else t)}
    print(f"ok {n} quotations of the text found in the snapshot")


# ---------------------------------------------------------------------------------------------------
# 3. Numbers: said() and the parts of the text it does not read
UNITS = {"万亿": 10 ** 12, "亿": 10 ** 8, "万": 10 ** 4}
AMOUNT = re.compile(r"(\d[\d,]*(?:\.\d+)?)(?:\s*多?(万亿|亿|万))?")
# what is not a number of the story: labels, citations, cross-references, the key equations (models() reads them),
# the column specification of the table, and the subscripts of the math
MASKS = [re.compile(r"\\begin\{keyeq\}.*?\\end\{keyeq\}", re.DOTALL),
         re.compile(r"\\(?:label|cite|chref|secref|figref|tabref|exref|eqref|ref|nameref|url|fig)\{[^}]*\}"),
         re.compile(r"\\begin\{tabularx\}[^\n]*"),
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
    """A Chinese numeral of the text: '三', '十二', '九十', '三成', '九折', '三分之一', '十分之九', '一半'."""
    if "分之" in s:
        b, a = s.split("分之")
        return zh(a) / zh(b)
    if s.endswith("成") or s.endswith("折"):           # 三成 = three tenths; 九折 = sold at nine tenths of the price
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
    post is empty), read by zh(). The numeral is taken from the phrase, so a check against it fails when the text
    changes it."""
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


# ---------------------------------------------------------------------------------------------------
# 4. Numbers, section by section
def fall(a: float, b: float) -> float:
    """The fall from a to b, per cent."""
    return 100 * (1 - b / a)


def rise(a: float, b: float) -> float:
    return 100 * (b / a - 1)


def guide(F, Y, Q):
    t = TEX.read_text(encoding="utf-8")
    assert f"\\guidequestion{{{GUIDE}}}" in t
    assert GUIDE in (ROOT / "zh" / "ch27_interwar.tex").read_text(encoding="utf-8")      # 第 27 章交来的问题
    y0, y1 = F["bern_together"]
    said("用数据描述 1929—1933 年美国的产出、物价、失业与银行倒闭", y0, y1)
    works = {"Fisher": F["fis_copyright"][0], "Friedman and Schwartz": F["bern_fs1963"][0],
             "Bernanke": F["bern83_wp"][1]}
    said("比较费雪的债务—通缩（1933）、弗里德曼—施瓦茨的货币紧缩（1963）与伯南克的信贷渠道（1983）三种解释", *works.values())
    chk("    three explanations (三种解释)", len(works), told("与伯南克的信贷渠道（1983）三种解释", "（1983）", "种解释"))
    said("评估 1933 年以后复苏的原因", F["frh_trough"][0])


def opening(F, Y, Q):
    d, y = F["fdr_title"]
    assert "March 12, 1933" in Q["fdr_title"] and "[First Fireside Chat]" in Q["fdr_title"]
    assert date(int(y), 3, int(d)).weekday() == 6                                           # 星期日
    said("1933 年 3 月 12 日是星期日", y, 3, d)
    d4, y4 = F["frh_inaug"]
    assert "March 4, 1933" in Q["frh_inaug"] and y4 == y
    chk("    eight days in office (就任总统才八天)", d - d4, told("就任总统才八天", "才", "天"))
    say("这是他的第一次炉边谈话")
    assert "last few days of February and the first few days of March" in Q["fdr_febmar"]
    said("他从 2 月底与 3 月初讲起", 2, 3)
    assert "By the afternoon of March 3d" in Q["fdr_march3"]
    said("到 3 月 3 日下午，全国几乎没有一家银行还在营业", 3, F["fdr_march3"][0])
    assert "issued by the Governors in almost all the States" in Q["fdr_governors"]
    say("几乎每个州的州长都已发布公告，让银行全部或部分暂时关门")
    d6, h = F["app_2039_done"]
    a, b, y39 = F["app_2039_dates"]
    h1, m1, d1, _ = F["frh_1am"]
    assert d6 == a == d1 and h == h1 and m1 == 0 and y39 == y and "March-1 A.M." in Q["app_2039_done"]
    said("3 月 6 日凌晨 1 点，罗斯福宣布，从 6 日到 9 日全国的银行一律休假", 3, d6, h, a, b)
    assert date(int(y), 3, int(d) + 1).weekday() == 0                                       # 明天，星期一
    assert "on first examination by the Treasury have already been found to be all right" in Q["fdr_firstexam"]
    said("“明天，星期一”，12 个联邦储备银行所在城市里经财政部初查合格的银行先开门", F["fdr_tomorrow"][0])
    assert "on Tuesday" in Q["fdr_250"]
    said("星期二轮到有票据交换所的城市，约 250 个", F["fdr_250"][0])
    crash = F["bern_1928"][1]
    assert "the stock market crash of October 1929" in Q["bern_1928"]
    months = (y - crash) * 12 + (3 - 10)
    chk("    three and a half years (三年半), October 1929 to March 1933", months / 12,
        told("三年半以前", "", "年半") + 0.5, tol=0.25)
    said("三年半以前，1929 年 10 月，纽约股市崩盘", crash, 10)
    B, A = bea(), annual()
    said("按 2017 年的美元计，美国的实际 GDP 从 1929 年到 1933 年降了 26.3\\%，GDP 平减指数降了 25.8\\%", base_year(), 1929,
         1933, fall(B.gdp_real_2017[1929], B.gdp_real_2017[1933]), fall(B.deflator[1929], B.deflator[1933]))
    said("失业率从 3.2\\% 升到 24.9\\%", A.unemployment_pct[1929], A.unemployment_pct[1933])
    said("1930—1933 年停业的银行共 9,096 家", 1930, 1933, A.susp_banks.loc[1930:1933].sum())


def world(F, Y, Q):
    B, A = bea(), annual()
    said("名义 GDP 从 1929 年的 1,046 亿美元降到 1933 年的 572 亿美元", 1929, B.gdp[1929] * M6, 1933, B.gdp[1933] * M6)
    said("实际 GDP 按 2017 年的美元计，1929 年是 11,911 亿美元，1933 年只有 8,774 亿美元", base_year(), 1929,
         B.gdp_real_2017[1929] * M6, 1933, B.gdp_real_2017[1933] * M6)
    lo, hi = map(int, re.search(r"ip_(\d{4})_(\d{2})_100", "ip_1923_25_100").groups())
    assert "industrial production, adjusted for seasonal variation" in annual_meta()["series"]
    said("联邦储备委员会的工业生产指数以 1923—1925 年的平均为 100", lo, 1900 + hi, 100)
    ip = A.ip_1923_25_100
    said("1929 年它是 119，1932 年只有 64，差不多少了一半", 1929, ip[1929], 1932, ip[1932])
    chk("    almost half (差不多少了一半)", fall(ip[1929], ip[1932]) / 100, told("差不多少了一半", "少了"), tol=0.05)
    assert "hit bottom in March 1933" in Q["frh_trough"]
    said("谷底在 1933 年 3 月", F["frh_trough"][0], 3)
    cpi, w = A.cpi_1967_100, A.wpi_1926_100
    said("劳工统计局的消费物价指数以 1967 年为 100，1929 年是 51.3，1933 年是 38.8", 1967, 100, 1929, cpi[1929], 1933,
         cpi[1933])
    chk("    four years (四年里)", 1933 - 1929, told("四年里它降了 24.4\\%", "", "年里"))
    said("四年里它降了 24.4\\%，每年都在降", fall(cpi[1929], cpi[1933]))
    assert (cpi.loc[1929:1933].diff().iloc[1:] < 0).all()                                 # 每年都在降
    said("批发物价跌得更多，以 1926 年为 100，1929 年是 95，1932 年是 65", 1926, 100, 1929, w[1929], 1932, w[1932])
    assert w[1932] / w[1929] < cpi[1932] / cpi[1929] and w[1932] / w[1929] < cpi[1933] / cpi[1929]   # 跌得更多
    O = output_index()
    said("1929—1933 年它们一起往下走，1933 年以后又一起回升", 1929, 1933, 1933)
    for col in ("real", "deflator", "cpi"):
        assert (O[col].loc[1929:1933].diff().iloc[1:] < 0).all(), col                     # 一起往下走
        assert (O[col].loc[1933:1936].diff().iloc[1:] > 0).all(), col                     # 一起回升
    U, P = A.unemployed_thousands * 1000, A.unemployment_pct
    said("1929 年失业的有 155 万人，占民用劳动力的 3.2\\%", 1929, U[1929], P[1929])
    said("1933 年有 1,283 万人，占 24.9\\%", 1933, U[1933], P[1933])
    chk("    one worker in four (四个工人里就有一个)", P[1933] / 100, 1 / told("四个工人里就有一个找不到工作", "", "个工人"),
        tol=0.005)
    said("1947 年以前，劳动力按 14 岁以上的人统计", *unemployment_rule())
    said("复苏以后失业率仍然很高，1937 年是 14.3\\%，1938 年又升到 19.0\\%", 1937, P[1937], 1938, P[1938])
    assert P[1938] > P[1937]
    # bank suspensions
    S, SD = A.susp_banks, A.susp_deposits_thousands * 1000
    said("1921—1929 年，停业的银行每年少则 366 家，多则 976 家", 1921, 1929, S.loc[1921:1929].min(),
         S.loc[1921:1929].max())
    said("1930 年有 1,350 家停业，1931 年有 2,293 家", 1930, S[1930], 1931, S[1931])
    said("1932 年有 1,453 家，1933 年有 4,000 家", 1932, S[1932], 1933, S[1933])
    said("停业银行的存款，1930 年是 8.4 亿美元，1931 年是 16.9 亿美元，1933 年是 36.0 亿美元", 1930, SD[1930], 1931,
         SD[1931], 1933, SD[1933])
    say("这里的停业，指银行因为财务困难被监管者或董事会关闭，不论暂时还是永久，也不论后来是否重开")
    assert "unless the closing was under a special bank holiday declared by civil authorities" in Q["frb_definition"]
    assert "Banks which were reopened" in Q["frb_reopened"]
    # the Federal Reserve System
    assert "When the crises began" in Q["frh_8000"] and Y["frh_8000"] == 1930
    said("1930 年秋天，加入联邦储备体系的商业银行有 8,000 多家，没有加入的近 16,000 家", Y["frh_8000"], *F["frh_8000"])
    said("联邦储备体系本身有 12 家联邦储备银行", F["frh_mar4"][1])
    y13, cover, price = F["frh_40pct"]
    said("法律还要求联邦储备银行为发出的钞票保有 40\\% 的黄金，并按每盎司纯金 20.67 美元兑换黄金", cover, price)
    said("其中 40\\% 的黄金准备写在 1913 年的联邦储备法里", cover, y13)
    _, y00, p00 = F["frh_1900"]
    assert "the value set by the Gold Act of 1900, which equaled $20.67 per ounce" in Q["frh_1900"] and p00 == price
    said("20.67 美元的金价则来自 1900 年金本位法规定的金元含金量", p00, y00)


def panics(F, Y, Q):
    y30, three, *starts, months = F["frh_poised"]
    said("1930 年秋天，经济看上去快要复苏了", y30)
    chk("    three contractions (三次衰退)", three, told("此前的三次衰退", "此前的", "次衰退"))
    said("此前的三次衰退，分别从 1920、1923 与 1926 年开始，平均持续 15 个月", *starts, months)
    y29, n = F["frh_fifteen"]
    assert "summer of 1929" in Q["frh_fifteen"]
    said("这一次从 1929 年夏天算起，也已经 15 个月", y29, n)
    d7, _, _ = F["frh_caldwell"]
    assert "On November 7" in Q["frh_caldwell"] and "largest financial holding company in the South" in Q[
        "frh_caldwell_south"]
    said("11 月，南方最大的金融控股公司 Caldwell 出了事", 11)
    assert "one of Caldwell's principal subsidiaries" in Q["frh_caldwell"]
    said("它的一家主要子公司田纳西银行 11 月 7 日关门", 11, d7)
    chk("    about one-third reopened (约三分之一)", F["frh_cascade"][0], told("其中约三分之一几个月后重开", "其中约", "几个月"))
    d, nth = F["frh_bus"]
    assert "December 11" in Q["frh_bus"]
    said("12 月 11 日，纽约市第四大的银行", 12, d)
    chk("    the fourth-largest bank (第四大)", nth, told("纽约市第四大的银行", "第", "大"))
    assert "June 1931" in Q["frh_chicago"]
    said("1931 年 6 月，芝加哥又起风波", F["frh_chicago"][0], 6)
    d, y, _ = F["frh_britain"]
    assert "September 21, 1931" in Q["frh_britain"]
    said("9 月 21 日，英国放弃了金本位", 9, d)
    d9, _, r1, d16, r2 = F["bern_oct1931"]
    said("纽约联储 10 月 9 日把贴现率提到 2.5\\%，10 月 16 日再提到 3.5\\%", 10, d9, r1, 10, d16, r2)
    said("单是 10 月就有 522 家商业银行关门", 10, F["bern_522"][0])
    # 1932
    assert "in January 1932" in Q["frh_rfc"]
    said("1932 年 1 月，国会设立复兴金融公司", F["frh_rfc"][0], 1)
    d27, _ = F["stat_feb27"]
    m3, y33 = F["stat_until"]
    assert "February 27, 1932" in Q["stat_feb27"] and "until March 3, 1933" in Q["stat_until"]
    said("2 月 27 日的格拉斯—斯蒂格尔法又规定，到 1933 年 3 月 3 日为止", 2, d27, y33, 3, m3)
    _, _, _, d34, y34 = F["frb_extended"]
    assert column("juan")["frb_extended"] == "Feb. 1933" and "and now until March 3, 1934" in Q["frb_extended"]
    said("到 1933 年 2 月，这一期限已经延长到 1934 年 3 月 3 日", Y["frb_extended"], 2, y34, 3, d34)
    w0, w1 = F["frh_freegoldworry"][:2]
    assert "in the latter part of 1931 and early 1932" in Q["frh_freegoldworry"]
    said("1931 年下半年到 1932 年初，好几家联邦储备银行一再担心自己的自由黄金不够", w0, w1)
    a, b, c = F["frh_weekly"]                                     # million, million, billion
    said("3 月每周买进近 2,500 万美元的政府证券，4 月每周近 1 亿美元，到 6 月已经买了 10 亿美元以上", 3, a * M6, 4, b * M6, 6,
         c * B9)
    assert "occurred in April 1932, when the Congress began to exert considerable pressure" in Q["bern_april1932"]
    assert F["bern_april1932"][0] == Y["frh_weekly"]
    said("4 月起，国会也向美联储施加很大的压力，要它大量买进证券", 4)
    d0, y0, d1, y1 = F["frb_period"]
    said("从 1932 年 2 月 3 日到 1933 年 2 月 1 日", y0, 2, d0, y1, 2, d1)
    bought, repaid, reserves = F["frb_1015"]
    assert repaid < 6e8                                                                    # 近 6 亿
    said("联邦储备银行买进约 10 亿美元的政府证券，会员银行因此还掉近 6 亿美元的借款", bought, repaid)
    assert "the whole of this increase being held as reserves in excess of legal requirements" in Q["frb_1015"]
    said("准备金余额增加了约 5 亿美元，增加的全是超额准备", reserves)
    said("1932 年夏天，通缩停了下来，工业生产开始回升", F["frh_summer1932"][0])
    d, _ = F["bern_july16"]
    assert "July 16, 1932" in Q["bern_july16"]
    said("7 月 16 日国会休会，购买实际上也就停了", 7, d)
    # the winter of 1932-33
    d, y = F["frh_nevada"]
    assert "October 31, 1932" in Q["frh_nevada"] and "Nevada was first" in Q["frh_nevada"]
    said("内华达州 1932 年 10 月 31 日第一个宣布全州银行休假", y, 10, d)
    assert "February 14" in Q["frh_michigan"]
    said("密歇根州 1933 年 2 月 14 日跟上", Y["frh_michigan"], 2, F["frh_michigan"][0])
    said("联邦储备银行像 1931 年秋天那样提高了贴现率", F["frh_feb1933"][1])
    amt, weeks, d8 = F["frh_178"]
    chk("    four weeks (四个星期)", weeks, told("截至 3 月 8 日的四个星期里", "日的", "个星期"))
    said("截至 3 月 8 日的四个星期里，公众手中的通货增加了 17.8 亿美元", 3, d8, amt * B9)
    d, y = F["frh_mar1"][:2]
    said("3 月 1 日，纽约联储行长哈里森", 3, d)
    said("3 月 3 日，联邦储备委员会暂停了黄金准备的要求", 3, F["frh_mar3"][0])
    d4, n12, n37 = F["frh_mar4"]
    assert "Saturday, March 4" in Q["frh_mar4"] and date(int(y), 3, int(d4)).weekday() == 5
    said("3 月 4 日是星期六，12 家联邦储备银行都没有开门，37 个州的银行或者全关，或者限制提款", 3, d4, n12, n37)


def run(F, Y, Q):
    """The bank run of the subsubsection and ex:depressionus-run."""
    say("资本$E=R+A-D$")
    said("得卖掉账面价值$(W-R)/(1-\\delta)$的资产", 1)
    R, A, D, W = RUN["R"], RUN["A"], RUN["D"], RUN["W"]
    E = R + A - D
    said("一家银行有准备金 10，其他资产 90，存款 92，资本 8", R, A, D, E)
    good = told("资产可以按九折卖掉时", "按", "卖掉")
    bad = told("（2）只能按七折卖掉时呢？", "按", "卖掉")
    said("（1）存款人取走 30。资产可以按九折卖掉时", 1, W)
    said("（2）只能按七折卖掉时呢？（3）折扣多大时，这家银行恰好资不抵债？（4）它倒闭以后", 2, 3, 4)
    need = W - R
    sold, loss = need / good, need / good - need
    said("（1）要凑足$30-10=20$，得卖掉账面$20/0.9\\approx22.2$的资产，损失约 2.2，资本还剩约 5.8", 1, W, R, need, need, good,
         sold, loss, E - loss)
    assert loss < E
    loss2 = need / bad - need
    said("（2）得卖掉$20/0.7\\approx28.6$，损失约 8.6，大于资本 8，资不抵债", 2, need, bad, need / bad, loss2, E)
    assert loss2 > E
    delta = E / (need + E)
    said("（3）令$\\delta\\times20/(1-\\delta)=8$，得$\\delta=8/28\\approx28.6\\%$", 3, need, 1, E, E, need + E, 100 * delta)
    chk("    eq:depressionus-firesale at delta = 8/28: the loss equals the capital", delta / (1 - delta) * need, E)
    said("（4）存款人会少存多取", 4)


def fisher(F, Y, Q):
    said("1929 年秋天还说股价低", F["bern_1928"][1])                          # Chapter 27's headline (EVENTS)
    assert "THE DEBT-DEFLATION THEORY OF GREAT DEPRESSIONS" in Q["fis_title"]
    said("1933 年，他在《计量经济学》第 1 卷上发表了《大萧条的债务—通缩理论》", F["fis_copyright"][0], F["fis_volume"][0])
    chk("    two dominant factors (两个主导的因素)", F["fis_dominant"][0], told("大繁荣与大萧条有两个主导的因素", "有", "个主导"))
    chk("    nine links (共九环)", F["fis_links"][0], told("一环扣一环，共九环", "共", "环"))
    assert "a fall in the nominal, or money, rates and a rise in the real, or commodity, rates" in Q["fis_link9"]
    say("最后一环是利率，名义利率下降，实际利率上升")
    said("$\\pi$是负数时，分母小于 1", 1)
    y, a, b, c = F["fis_march1933"][:4]
    assert "By March, 1933" in Q["fis_march1933"]
    said("到 1933 年 3 月，清偿把债务减少了约 20\\%，美元的价值却提高了约 75\\%", y, 3, a, b)
    real = (1 - a / 100) * (1 + b / 100)
    chk("    Fisher's product (100%-20%) X (100%+75%) = 140%", 100 * real, F["fis_march1933"][-1], tol=1e-9)
    said("按商品计算的实际债务增加了约 40\\%，即$0.8\\times1.75=1.40$", c, 1 - a / 100, 1 + b / 100, real)
    said("$1+r=(1+i)/(1+\\pi)$", 1, 1, 1)
    yc, s0, y0, s1, y1, y1b = F["bern_clark"]
    said("按 Clark（1933）的估算，美国还本付息占国民收入的比例，从 1929 年的 9\\% 升到 1932—1933 年的 19.8\\%", yc, y0, s0, y1,
         1900 + y1b, s1)
    A = annual()
    cpi, cp = A.cpi_1967_100, A.cp_rate
    p32 = rise(cpi[1931], cpi[1932])
    said("1932 年，商业票据的年利率平均约 2.7\\%，消费物价却降了 10.3\\%", 1932, cp[1932], -p32)
    r32 = 100 * ((1 + cp[1932] / 100) / (1 + p32 / 100) - 1)
    said("按费雪关系，借款人付的实际利率约 14.5\\%", r32)
    assert cpi[1929] == cpi[1928]                                                          # 消费物价没有变
    said("1929 年，名义利率约 5.9\\%，消费物价没有变，实际利率也就是这么高", 1929, cp[1929])
    # ex:depressionus-debt
    D, i, f, x = LOAN["D"], LOAN["i"], LOAN["fall"], LOAN["repay"]
    n = told("设此后三年物价每年下跌 10\\%", "此后", "年物价")
    said("一位农场主 1929 年借了 1,000 美元，年利率 5\\%，每年只付利息", 1929, D, i)
    said("设此后三年物价每年下跌 10\\%", f)
    actual = fall(cpi[1929], cpi[1933])
    said("（1）每年的实际利率是多少？（2）三年以后，这笔债按 1929 年的物价算值多少？（3）实际的消费物价 1929—1933 年降了 "
         "24.4\\%，同一笔名义债务的实际负担增加了多少？（4）按式~\\eqref{eq:depressionus-debt}，还掉 20\\% 的债务，物价降多少，"
         "实际债务就不变？", 1, 2, 1929, 3, 1929, 1933, actual, 4, x)
    chk("    three years (三年以后)", n, told("（2）三年以后", "（2）", "年以后"))
    g, P = 1 + i / 100, 1 - f / 100
    said("（1）$1.05/0.9-1\\approx16.7\\%$", 1, g, P, 1, 100 * (g / P - 1))
    burden = D / P ** n
    said("（2）$1{,}000/0.9^3\\approx1{,}372$美元，实际负担增加约 37\\%", 2, D, P, n, burden, rise(D, burden))
    said("他每年付的 50 美元利息，按 1929 年的物价算也越来越多", D * i / 100, 1929)
    s = actual / 100
    said("（3）$1/(1-0.244)-1\\approx32\\%$", 3, 1, 1, s, 1, 100 * (1 / (1 - s) - 1))
    pi = (1 - x / 100) / 1 - 1                                                              # eq:depressionus-debt = 1
    said("（4）令$(1-0.2)/(1+\\pi)=1$，得$\\pi=-20\\%$。物价降得比 20\\% 多", 4, 1, x / 100, 1, 1, -100 * pi, x)
    said("费雪估计的是物价降得多得多的情形，实际债务因此增加了约 40\\%", c)
    assert fall(1, 1 / (1 + b / 100)) > 2 * x                                              # 物价降得多得多
    assert "from May to September 1932" in Q["fis_reflation"]
    said("1932 年 5—9 月，联邦储备银行在公开市场上的购买曾让物价与生意回升", F["fis_reflation"][0], 5, 9)


def money(F, Y, Q):
    A, T = annual(), money_table()
    chk("    thirty years (三十年后)", F["bern_fs1963"][0] - F["fis_copyright"][0], told("三十年后，又有了另一种解释", "", "年后"))
    y0, y1 = F["bern_together"]
    said("货币存量、产出与物价在 1929—1933 年一起下降", y0, y1)
    said("1930 年秋天到 1933 年冬天，货币存量下降了近 30\\%", *F["frh_30pct"])
    m2 = A.m2_bn
    said("按年平均，广义货币 1929 年是 466 亿美元，1933 年是 322 亿美元，降了 30.9\\%", 1929, m2[1929] * B9, 1933,
         m2[1933] * B9, fall(m2[1929], m2[1933]))
    said("同一时期，公众手中的通货从 39.0 亿美元增加到 50.9 亿美元", A.currency_bn[1929] * B9, A.currency_bn[1933] * B9)
    said("存款从 427 亿美元降到 271 亿美元", A.deposits_bn[1929] * B9, A.deposits_bn[1933] * B9)
    said("1929—1933 年，$H$增加了 14.0\\%，$M$却减少了 30.9\\%。货币乘数从约 6.5 降到约 4", 1929, 1933,
         rise(T.H[1929], T.H[1933]), fall(T.M[1929], T.M[1933]), T.m[1929], T.m[1933])
    assert T.c[1933] > T.c[1929] and T.r[1933] > T.r[1929]                                 # 两个比率都上升了
    # tab:depressionus-money
    chk("    three determinants (三个决定因素)", 3, told("美国的货币存量与它的三个决定因素", "它的", "个决定"))
    said("美国的货币存量与它的三个决定因素，1929—1936 年", T.index[0], T.index[-1])
    said("年平均 & 1929 & 1932 & 1933 & 1934 & 1935 & 1936", *T.index)
    said("通货$C$（亿美元） & 39.0 & 49.2 & 50.9 & 46.3 & 48.0 & 52.3", *(10 * T.C))
    said("存款$D$（亿美元） & 427.0 & 311.3 & 271.3 & 297.3 & 342.7 & 382.5", *(10 * T.D))
    said("广义货币$M=C+D$ & 466.0 & 360.5 & 322.2 & 343.6 & 390.7 & 434.8", *(10 * T.M))
    said("准备金$R$（亿美元） & 32.6 & 28.6 & 30.7 & 44.6 & 58.4 & 69.4", *(10 * T.R))
    said("基础货币$H=C+R$ & 71.6 & 77.8 & 81.6 & 90.9 & 106.4 & 121.7", *(10 * T.H))
    said("通货比率$C/M$ & 0.084 & 0.136 & 0.158 & 0.135 & 0.123 & 0.120", *T.c)
    said("准备金比率$R/D$ & 0.076 & 0.092 & 0.113 & 0.150 & 0.170 & 0.181", *T.r)
    said("货币乘数$m=M/H$ & 6.51 & 4.63 & 3.95 & 3.78 & 3.67 & 3.57", *T.m)
    chk("    m = M/H is Chapter 4's 1/(c + r - cr)", list(T.m), [mult(c, r) for c, r in zip(T.c, T.r)], tol=1e-12)
    am = annual_meta()
    assert "February 1937, p. 112" in am["source"]
    said("通货、存款与库存现金：《美国历史统计》（1975）系列 X 410—416，弗里德曼与施瓦茨的估计", hsus_year(),
         series_no("X", "currency held by the public"), series_no("X", "bank vault cash"))
    said("会员银行的准备金余额：《联邦储备公报》1937 年 2 月，第 112 页", 1937, 2, 112)
    assert A.member_reserves_m.loc[[1930, 1931]].isna().all()
    said("1930 与 1931 年缺准备金余额的年平均", 1930, 1931)
    # ex:depressionus-mult
    said("（1）验证 1929 与 1933 年的货币乘数。（2）设两个比率都停在 1929 年的水平，只有$H$变到 1933 年的数，$M$是多少？"
         "（3）$H$停在 1929 年，只让$C/M$变到 1933 年的水平呢？只让$R/D$变呢？（4）三个因素各起了什么作用？", 1, 1929, 1933, 2,
         1929, 1933, 3, 1929, 1933, 4)
    c29, r29, c33, r33, m29 = T.c[1929], T.r[1929], T.c[1933], T.r[1933], T.m[1929]
    said("（1）1929 年，$m=1/(0.0837+0.0763-0.0837\\times0.0763)\\approx6.51$，$6.51\\times71.6\\approx466$亿美元", 1, 1929, 1,
         c29, r29, c29, r29, mult(c29, r29), m29, 10 * T.H[1929], 10 * T.M[1929])
    said("1933 年，$m=1/(0.158+0.113-0.158\\times0.113)\\approx3.95$，$3.95\\times81.6\\approx322$亿美元", 1933, 1, c33, r33,
         c33, r33, mult(c33, r33), T.m[1933], 10 * T.H[1933], 10 * T.M[1933])
    said("（2）$6.51\\times81.6\\approx531$亿美元，比 1929 年多 14\\%", 2, m29, 10 * T.H[1933], 10 * m29 * T.H[1933], 1929,
         rise(T.H[1929], T.H[1933]))
    mc, mr = mult(c33, r29), mult(c29, r33)
    said("（3）只变$C/M$，乘数降到约 4.50，$M\\approx322$亿美元，少 31\\%", 3, mc, 10 * mc * T.H[1929], fall(m29, mc))
    said("只变$R/D$，乘数降到约 5.33，$M\\approx382$亿美元，少 18\\%", mr, 10 * mr * T.H[1929], fall(m29, mr))
    said("（4）基础货币增加了，货币存量却少了三成", 4)
    chk("    three tenths less money (少了三成)", fall(T.M[1929], T.M[1933]) / 100, told("货币存量却少了三成", "少了"),
        tol=0.05)
    chk("    the currency ratio alone: three tenths (少三成)", fall(m29, mc) / 100, told("单这一项就足以让$M$少三成", "$M$少"),
        tol=0.05)
    two = told("又让它少了近两成", "少了近")
    assert two - 0.03 < fall(m29, mr) / 100 < two                                         # 近两成: a little less
    four = told("两项一起让乘数降了约四成", "降了约")
    chk("    both ratios: about four tenths (约四成)", fall(m29, T.m[1933]) / 100, four, tol=0.05)
    assert fall(m29, T.m[1933]) < fall(m29, mc) + fall(m29, mr)                            # 比两项之和小
    # the natural experiments
    n, k, one = F["bern_four"]
    chk("    four episodes (四次)", n, told("他们找到的自然实验有四次", "有", "次"))
    chk("    three tightenings (三次收紧)", k, told("三次收紧", "", "次收紧"))
    chk("    one loosening (一次放松)", one, told("一次放松", "", "次放松"))
    a, b = F["bern_1928"]
    assert "began in the spring of 1928" in Q["bern_1928"]
    said("第一次是 1928 年春天到 1929 年 10 月的收紧", a, b, 10)
    said("第二次是 1931 年 10 月为保卫美元而加息", F["bern_oct1931"][1], 10)
    assert "between April and June 1932" in Q["bern_1932"]
    said("第三次是 1932 年 4—6 月的大量购买", F["bern_1932"][0], 4, 6)
    assert "from January 1933 to the banking holiday in March" in Q["bern_1933"]
    said("第四次是 1933 年 1 月到银行休假", F["bern_1933"][0], 1)
    # the compare box 萧条从哪里来
    said("1920 年代的过度负债", DECADE20)
    said("美联储 1928—1929 年的收紧与此后的被动", a, b)
    said("1933 年 3 月实际债务约增加四成", F["fis_march1933"][0], 3)
    chk("    about four tenths more real debt (约增加四成)", F["fis_march1933"][3] / 100,
        told("1933 年 3 月实际债务约增加四成", "约增加"))
    say("还本付息占国民收入的比例翻了一倍多")
    assert 2 < F["bern_clark"][3] / F["bern_clark"][1] < 3
    chk("    four natural experiments (四次自然实验)", n, told("四次自然实验，产出与物价每次都跟着货币走", "", "次自然"))


def fed(F, Y, Q):
    A = annual()
    said("它在 1930—1933 年没有做到", 1930, 1933)
    views = ["第一种说法看人", "第二种说法看理论", "第三种说法看利率", "第四种说法看黄金"]
    say(*views)
    chk("    four views (四种说法)", len(views), told("四种说法并不互相排斥", "", "种说法"))
    said("斯特朗 1928 年去世", 1928)                                     # Strong 1872—1928 (LIVES, Chapter 27)
    said("费雪 1933 年也认为，斯特朗在世，萧条几乎可以避免", F["fis_copyright"][0])
    assert "power became diffused" in Q["bern_diffused"] and "well-established chain of command" in Q["bern_vacuum"]
    assert "Larger, stronger banks would then take the lead" in Q["bern_clearing"]
    assert "was no longer their responsibility" in Q["bern_bigbanks"]
    say("美联储成立以前，恐慌通常由银行自己对付", "有了美联储，大银行觉得保护小同行已经不是自己的责任")
    assert "Federal Reserve Board" in Q["frh_mellon"]
    assert column("juan")["frb_88m"] == "Feb. 1933" and F["frb_policy"] == [4, 25]
    said("1933 年 1 月，它把持有的政府证券减少了 8,800 万美元", Y["frb_88m"], 1, F["frb_88m"][0])
    said("当时会员银行的超额准备约 5 亿美元", F["frb_500m"][0])
    ex, tb = A.excess_reserves_m * M6, A.tbill_rate
    said("超额准备的年平均，1929 年只有 4,300 万美元，1932 年约 2.6 亿美元", 1929, ex[1929], 1932, ex[1932])
    assert tb[1932] < 0.9                                                                  # 不到 0.9%
    said("国库券的收益率 1932 年平均不到 0.9\\%，1933 年只有约 0.5\\%", 1932, tb[1932], 1933, tb[1933])
    # the pitfall
    assert max(tb[1932], tb[1933]) < 1
    said("1932—1933 年，国库券的收益率不到 1\\%", 1932, 1933, 1)
    cpi, cp = A.cpi_1967_100, A.cp_rate
    falls = [fall(cpi[y - 1], cpi[y]) for y in (1932, 1933)]
    said("可是同一时期物价每年降 5\\%—10\\%", min(falls), max(falls))
    for y in (1932, 1933):
        real = 100 * ((1 + cp[y] / 100) / (cpi[y] / cpi[y - 1]) - 1)
        assert real > cp[1929], y                                                         # 比 1929 年还高
    said("按费雪关系，借款人付的实际利率比 1929 年还高", 1929)
    # gold
    said("按法律，联邦储备券要有 40\\% 的黄金", F["frh_40pct"][1])
    assert "February 1933, as it had during the fall of 1931" in Q["frh_feb1933"]
    said("1931 年 10 月的加息是为了保卫黄金，1933 年 2 月又加了一次", F["bern_oct1931"][1], 10, F["frh_feb1933"][0], 2)
    said("1932 年的格拉斯—斯蒂格尔法允许拿政府债券充当钞票的抵押", Y["stat_feb27"])
    said("可是到 1933 年 3 月，纽约联储的黄金准备还是跌破了下限", F["frh_mar1"][1], 3)
    ch23 = (ROOT / "zh" / "ch23_goldstandard.tex").read_text(encoding="utf-8")
    days = int(re.search(r"一次不超过 (\d+) 天", ch23).group(1))
    said("1913 年的联邦储备法让联邦储备委员会可以暂停准备金的要求，一次不超过 30 天", F["frh_40pct"][0], days)
    said("这扇门直到 1933 年 3 月 3 日才打开", F["frh_mar1"][1], 3, F["frh_mar3"][0])
    said("约束美联储的是 40\\% 的黄金准备", F["frh_40pct"][1])
    said("1932 年的购买说明", Y["frh_weekly"])
    yw, ym = F["frh_meltzer"][:2]
    said("照 Meltzer（2003）的判断，购买如果继续下去，1933 年冬天货币体系的崩溃“也许可以避免”", ym, yw)


def credit(F, Y, Q):
    said("伯南克（Ben Bernanke，1953— ）1983 年的论文", 1900 + F["loc_bernanke"][0], F["bern83_wp"][1])
    y0, y1, a, b, c, d, y2, half, y29 = F["bern83_pct"]
    assert "from 1930 to 1933 inclusive" in Q["bern83_pct"]
    said("1930 年倒闭的银行占营业银行的 5.6\\%，1931 年占 10.5\\%", y0, a, y0 + 1, b)
    said("1932 年占 7.8\\%，1933 年占 12.9\\%", y0 + 2, c, y1, d)
    said("到 1933 年底，营业的银行只比 1929 年的一半多一点", y2, y29)
    chk("    just above half (一半多一点)", half, told("到 1933 年底，营业的银行只比 1929 年的一半多一点", "年的", "多一点"))
    y, y30 = F["bern83_squeeze"]
    said("把 1929—1930 年严重但并非空前的衰退", y, 1900 + y30)
    s0, b0, b1, s1, y32 = F["bern83_baa"]
    assert "nearly 8% in mid-1932" in Q["bern83_baa"]
    said("1929—1930 年是 2.5 个百分点，1932 年年中升到近 8 个百分点", b0, 1900 + b1, s0, y32, s1)
    _, _, h0, h1, half = F["bern83_half_output"]
    assert "the bank holiday of March 1933" in Q["bern83_half_output"]
    said("模拟出的 1930 年年中到 1933 年 3 月的产出下降，至多只有实际下降的一半", h0, h1, 3)
    chk("    no more than half (至多只有一半)", half, told("至多只有实际下降的一半", "实际下降的"))
    chk("    about half (约一半)", F["bern83_mse"][0] / 100, told("模拟的误差减少了约一半", "减少了约"))
    # the deeper box
    N = column("note")
    key = N["bern83_key"]
    for words in ("relative to exponential trend", "DBANKS and DFAILS are first differences",
                  "deflated by the wholesale price index", "Data are monthly"):
        assert words in key, words
    m1 = int(re.search(r"rate of growth of M(\d), nominal", key).group(1))
    said("即 M1 的增长率减去用前期数据预测的增长率", m1)
    said("式 (4.3) 再加上 DBANKS 与 DFAILS 的当期与前一期", 4.3)
    t1, t3 = F["bern83_t41"], F["bern83_t43"]
    s1 = re.search(r"sample (\d+)/(\d+)-(\d+)/(\d+)", N["bern83_t41"]).groups()
    s3 = re.search(r"sample (\d+)/(\d+)-(\d+)/(\d+)", N["bern83_t43"]).groups()
    assert (t1[14], t1[15]) == (1900 + int(s1[1]), 1900 + int(s1[3]))
    assert (t3[22], t3[23]) == (1900 + int(s3[1]), 1900 + int(s3[3]))
    said("只有货币冲击的式 (4.1)，1919 年 1 月到 1941 年 12 月，当期货币冲击的系数是 0.407（$t=3.42$），回归标准误是 0.0272",
         4.1, t1[14], int(s1[0]), t1[15], int(s1[2]), t1[4], t1[5], t1[12])
    chk("    two financial variables (两个金融变量)", 2, told("加上两个金融变量的式 (4.3)", "加上", "个金融"))
    said("加上两个金融变量的式 (4.3)，1921 年 1 月到 1941 年 12 月，当期货币冲击的系数是 0.332，DBANKS 的当期系数是"
         "$-0.869\\times10^{-4}$（$t=-4.24$），DFAILS 的当期与前一期系数是$-0.258\\times10^{-3}$与$-0.325\\times10^{-3}$"
         "（$t=-1.95$与$-2.47$），回归标准误降到 0.0249", 4.3, t3[22], int(s3[0]), t3[23], int(s3[2]), t3[4],
         -t3[12] * 1e4, 10, 4, -t3[13], -t3[16] * 1e3, 10, 3, -t3[18] * 1e3, 10, 3, -t3[17], -t3[19], t3[20])
    assert all(v < 0 for v in t3[12:20])                                                  # 符号都是负的
    assert t3[20] < t1[12]                                                                 # 回归标准误降到
    said("加上它们以后，当期货币冲击的系数从 0.407 降到 0.332（$t=2.92$），仍然显著", t1[4], t3[4], t3[5])
    assert t3[4] < t1[4] and t3[5] > 1.96                                                  # 降到, 仍然显著
    assert s1[1] != s3[1]                                                                  # 两式的样本起点不同
    say("两式的样本起点不同，这个比较只是大致的")
    assert "had never previous to this time been a necessary result of declines in output" in Q["bern83_never"]
    assert "important sources of bank runs" in Q["bern83_events"] and "Kreditanstalt in Austria" in Q["bern83_kredit"]
    assert "scandal at the Bank of the United States" in Q["bern83_scandal"]
    y33, seven = F["bern83_march"]
    said("1933 年 3 月倒闭银行的存款，是第二多那个月的七倍", y33, 3)
    chk("    seven times (七倍)", seven, told("是第二多那个月的七倍", "月的", "倍"))
    _, p15, _, y31 = F["bern83_15pct"]
    assert "the events of October 1931" in Q["bern83_15pct"]
    said("伯南克在回归中只按 15\\% 计入，相当于 1931 年 10 月那次危机的规模", p15, y31, 10)
    said("它解释不了 1929—1930 年", y, 1900 + y30)
    # the case: Canada
    said("加拿大 · 1929—1933 · 没有银行倒闭的萧条", 1929, 1933)
    n13, y13, n31, y31 = F["cyb_banks"]
    said("1913 年有 25 家特许银行，1931 年只剩 10 家", y13, n13, y31, n31)
    _, n30, _, y30b, n34, _, _, y34 = F["cyb_branches"]
    assert "at Dec. 31, 1930" in Q["cyb_branches"] and "as at Dec. 31, 1934" in Q["cyb_branches"]
    said("分支行 1930 年底有 4,083 家，此后关掉一些不赚钱的，1934 年底还有 3,527 家", y30b, n30, y34, n34)
    y, v = F["cyb_netvalue"]
    p = F["cyb_47pct"]
    assert p[5] == 1929
    assert "by the Dominion Bureau of Statistics" in Q["cyb_netvalue"]
    assert "the net production of commodities" in Q["cyb_commodities"]
    said("按自治领统计局的估计，1932 年商品生产的净值只有 21.05 亿加元，比 1929 年少了 47\\%", y, v, p[5], p[4])
    assert "did not decline to anything like the same extent" in Q["cyb_volume"]
    p32, y32, p29, y29 = F["cyb_6670"]
    said("按官方的批发物价指数，1932 年的 66.70 加元在商品上的购买力，相当于 1929 年的 95.60 加元", y32, p32, y29, p29)
    real = (1 - p[4] / 100) * p29 / p32
    chk("    about a quarter less in real terms (约少了四分之一)", 1 - real,
        told("用它折算，生产的实际价值约少了四分之一", "约少了"), tol=0.02)
    B = bea()
    said("美国的实际 GDP 1929—1932 年少了 25.4\\%", 1929, 1932, fall(B.gdp_real_2017[1929], B.gdp_real_2017[1932]))
    _, y31b, _ = F["frh_britain"]
    d19, y19 = F["cyb_apr19"]
    assert "depreciated also and fluctuated broadly with sterling" in Q["cyb_sterling"]
    assert "departed from the gold standard on April 19, 1933" in Q["cyb_apr19"]
    said("1931 年 9 月以后，加元也跟着贬值，大体随英镑起落，直到 1933 年 4 月美元离开金本位", y31b, 9, y19, 4)
    assert "premium on United States dollars at Montreal" in Q["cyb_premium"]
    said("此后美元在蒙特利尔的升水才从约 20\\% 逐渐缩小", F["cyb_premium"][0])
    assert "like Canada, that went only part way with Britain" in Q["bern_partway"]
    said("未必能代表 1930 年代的各国", F["bern_canada_reply"][0])
    said("他用 26 个国家的样本", F["bern_26"][0])
    said("照 Kryzanowski 与 Roberts（1993）的看法", F["brr_forbearance"][0])
    # the spending side
    say("另一种解释从支出入手\\cite{romer1990}")
    v = F["rom90_ip"]
    for words in ("between August 1929 and October 1929", "between October 1929 and December 1929",
                  "between December 1929 and December 1930"):
        assert words in Q["rom90_ip"], words
    said("季节调整后的工业生产，1929 年 8 月到 10 月降了 1.8\\%，10 月到 12 月降了 9.8\\%", v[1], 8, 10, v[0], 10, 12, v[3])
    said("1929 年 12 月到 1930 年 12 月，它又降了 23.9\\%", v[7], 12, v[8], 12, v[6])
    assert "On November 7" in Q["frh_caldwell"] and Y["frh_caldwell"] == 1930              # the first panic
    said("1930 年的大部分时间，第一次银行恐慌还没有来", Y["frh_caldwell"])
    said("大萧条最主要的谜，是产出为什么在 1929 年底与整个 1930 年跌得这么厉害", *F["rom90_mystery"])
    assert "in late 1929 and all of 1930" in Q["rom90_mystery"]
    said("照 Temin（1976）的看法", F["rom90_temin"][0])
    assert "could not be the main explanation for the real decline in this period" in Q["rom90_temin"]
    said("按 Romer（1990）的论点", Y["rom90_abstract"])
    h87, y29h = F["rom90_hamilton"]
    assert "in the late summer of 1929" in Q["rom90_hamilton"]
    said("这一解释也承认，1929 年夏末产量最初的下降，货币紧缩是一个重要原因，这是 Hamilton（1987）的结论", y29h, h87)
    said("1931 年以后的下降，另有银行恐慌的原因", F["rom90_later"][2])


def recovery(F, Y, Q):
    A, B = annual(), bea()
    d, y = F["frh_mar9"]
    assert F["eba_title"] == [d, y] and "It passed later that evening" in Q["frh_mar9"]
    said("1933 年 3 月 9 日，国会在一天之内通过了紧急银行法", y, 3, d)
    said("最多发到估值的 90\\%", F["eba_notes"][0])
    d9, _ = F["app_2040_date"]
    said("3 月 9 日，罗斯福宣布休假继续，直到另行公告", 3, d9)
    d13, four = F["frh_mar13"]
    assert d13 - four == d9                                         # only four days after the emergency legislation
    said("3 月 13 日，联邦储备银行所在城市的会员银行先开门", 3, d13)
    d15, p90 = F["frh_90pct"]
    said("到 3 月 15 日，掌握全国 90\\% 银行资源的银行已经恢复营业", 3, d15, p90)
    chk("    about two-thirds redeposited (约三分之二)", F["frh_twothirds"][0],
        told("公众把挤兑时提走的通货存回了约三分之二", "存回了约"))
    assert "By the end of March" in Q["frh_twothirds"]
    said("到 3 月底，公众把挤兑时提走的通货存回了约三分之二", 3)
    v = F["frb_mar15"]
    assert v[0] == d15                                                     # the close of the holiday, 15 March
    said("休假结束时，还有 1,400 家国民银行与 225 家州立会员银行没有领到营业执照", v[2], v[6])
    v = F["frb_june30"]
    said("到 6 月 30 日，没有执照的国民银行、州立会员银行与非会员银行，分别还有 985 家、114 家与 1,983 家", 6, v[0], v[2], v[4],
         v[6])
    assert "to be rehabilitated and reopened or to be placed in liquidation or receivership" in Q["frb_june30"]
    say("它们或者整顿后重开，或者清理")
    # gold
    src = meta()["sources"]
    eo = int(re.search(r"Executive Order (\d+)", src["app6102"]["version"]).group(1))
    p72 = int(re.search(r"Proclamation (\d+)", src["app2072"]["version"]).group(1))
    d5, _ = F["eo_date"]
    d1, _ = F["eo_deliver"]
    assert "April 5, 1933" in Q["eo_date"] and "on or before May 1, 1933" in Q["eo_deliver"]
    said("4 月 5 日的第 6102 号行政命令要求，每个人在 5 月 1 日以前把金币、金块与金券交给联邦储备银行或会员银行", 4, d5, eo, 5,
         d1)
    assert "an equivalent amount of any other form of coin or currency" in Q["eo_equivalent"]
    say("换回等额的其他铸币或通货")
    said("每人只可以留 100 美元以内的金币与金券", F["eo_100"][0])
    said("4 月 20 日的公告正式中止了金本位", 4, F["frh_apr20"][0])
    said("6 月 5 日，国会的决议废除了一切合同里的黄金条款", 6, F["frh_june5"][0])
    d16, _ = F["frh_gs_signed"]
    said("6 月 16 日的银行法把商业银行与投资银行分开", 6, d16)
    mo, y34 = F["ba_operative"]
    said("法律规定的临时存款保险基金从 1934 年 1 月 1 日起运作，每个存款人最多赔付 2,500 美元", y34, 1, mo, F["ba_2500"][0])
    _, _, y7, cap = F["frh_5000"]
    assert "the limit was raised to $5,000" in Q["frh_5000"]
    said("1934 年 7 月，上限提高到 5,000 美元", y7, 7, cap)
    d16, y16, d1, y35 = F["fdic_postponed"]
    assert "the permanent plan was postponed one year" in Q["fdic_postponed"]
    assert F["fdic_5000"] == [1, y7, 2500, cap]                       # the FDIC's history agrees on the limit and the month
    said("同年 6 月，国会延长了临时基金，永久的方案推迟一年，到 1935 年 7 月才生效", 6, y35, 7)
    assert y16 == y7 and d1 == 1 and y35 == y16 + 1
    said("1934 年停业的银行只有 57 家", 1934, A.susp_banks[1934])
    assert "to factors other than deposit insurance" in Q["fdic_1934report"]
    said("它在 1934 年的年报里，把领到执照的银行倒闭得少归于存款保险以外的原因", F["fdic_1934report"][0])
    assert "RFC" in Q["fdic_reasons"] and "weeded out many weak banks" in Q["fdic_reasons"]
    said("1933 年的风波已经淘汰了不少弱银行，经济也好转了", F["fdic_reasons"][0])
    assert "remove penalties for bad management" in Q["fdic_penalties"]
    say("反对的人当时就说，有了保险，经营不善就不再受罚")
    # the Gold Reserve Act and Proclamation 2072
    y, d30 = F["wh_tuesday"]
    assert "Tuesday, January 30th" in Q["wh_tuesday"] and date(int(y), 1, int(d30)).weekday() == 1
    said("1934 年 1 月 30 日，罗斯福签署了黄金储备法", y, 1, d30)
    h, _, d31 = F["p2072_time"]
    assert d31 == d30 + 1 and "in the afternoon" in Q["p2072_time"]                       # 第二天下午
    old, fine = F["p2072_old"]
    new, fine2 = F["p2072_weight"]
    w = Fraction(new).limit_denominator(100)
    whole, part = divmod(w.numerator, w.denominator)
    said("第二天下午，他发布第 2072 号公告，把金元的重量从 25.8 格令定为$15\\frac{5}{21}$格令，成色都是十分之九", p72, old, whole,
         part, w.denominator)
    chk("    nine-tenths fine (十分之九)", [fine, fine2], [told("成色都是十分之九", "成色都是")] * 2)
    six = told("新的重量不到原来的六成", "原来的")
    assert six - 0.05 < new / old < six                                                    # 不到六成
    m1, _, price = F["wh_35"]
    said("财政部从 2 月 1 日起按每盎司纯金 35 美元收购黄金", 2, m1, price)
    # ex:depressionus-gold
    P0 = F["frh_40pct"][2]
    G = A.gold_stock_m * M6
    said("1900 年的金本位法规定，金元含 25.8 格令、成色十分之九的黄金", F["frh_1900"][1], old)
    chk("    nine-tenths fine (十分之九)", fine, told("成色十分之九的黄金", "成色", "的黄金"))
    said("1934 年 1 月 31 日的公告把它定为$15\\frac{5}{21}$格令，成色不变", y, 1, d31, whole, part, w.denominator)
    said("旧的金价是每盎司纯金 20.67 美元。（1）新金元的含金量是旧金元的百分之几？（2）新的金价是多少？（3）1933 年货币黄金存量的"
         "年平均是 40.6 亿美元", P0, 1, 2, 3, 1933, G[1933])
    said("按新价重估，账面上多出多少？（4）这笔“利润”里，20 亿美元成了财政部的外汇平准基金", 4, F["wh_fund"][0])
    ratio = new / old
    said("（1）$15\\frac{5}{21}=320/21\\approx15.238$，$15.238/25.8\\approx59.06\\%$，与白宫声明的“59.06\\% 多一点”相合", 1,
         whole, part, w.denominator, w.numerator, w.denominator, new, new, old, 100 * ratio, F["wh_5906"][0])
    assert 100 * ratio > F["wh_5906"][0]                                                   # 多一点
    said("（2）金价与含金量成反比，$20.67/0.5906\\approx35.00$美元", 2, P0, ratio, P0 / ratio)
    chk("    20.67 / 0.5906 = the White House's $35.00", P0 / ratio, price, tol=0.005)
    g33, up = G[1933] / 1e8, price / P0 - 1
    said("（3）$40.6\\times(35/20.67-1)\\approx40.6\\times0.693\\approx28.1$亿美元", 3, g33, price, P0, 1, g33, up, g33 * up)
    said("（4）别的国家的货币对黄金的价值不变时", 4)
    chk("    about four tenths (美元贬值约四成)", 1 - ratio, told("美元贬值约四成", "贬值约"), tol=0.05)
    # the gold inflows
    said("货币黄金存量的年平均，1933 年是 40.6 亿美元，1934 年是 75.1 亿美元，1936 年是 105.8 亿美元", 1933, G[1933], 1934,
         G[1934], 1936, G[1936])
    assert G[1933] * up > (G[1934] - G[1933]) / 2                                         # 大半来自重估
    said("1934 年的增加，大半来自重估", 1934)
    said("1934—1936 年金价没有再变，黄金存量多了 30.7 亿美元", 1934, 1936, G[1936] - G[1934])
    base = (A.money_in_circulation_m + A.member_reserves_m) * M6
    said("同一时期，流通中的货币加上会员银行的准备金余额，从 90.8 亿美元增加到 120.9 亿美元，多了 30.1 亿美元", base[1934],
         base[1936], base[1936] - base[1934])
    say("流入的黄金几乎一对一地变成了基础货币")
    chk("    one for one (几乎一对一)", (base[1936] - base[1934]) / (G[1936] - G[1934]), 1, tol=0.05)
    assert "adding an equal amount to the reserves of member banks" in Q["frb_goldnote"]
    # money and output
    m2, R = A.m2_bn, B.gdp_real_2017
    said("广义货币从 1933 年的 322 亿美元增加到 1937 年的 457 亿美元", 1933, m2[1933] * B9, 1937, m2[1937] * B9)
    assert R[1936] >= R[1929] > R[1935]                                                    # 1936 年回到了 1929 年的水平
    said("实际 GDP 从 1933 年到 1937 年增长了 43.2\\%，1936 年回到了 1929 年的水平", 1933, 1937, rise(R[1933], R[1937]),
         1936, 1929)
    g, g0, g1 = F["rom92_m1"]
    m1 = int(re.search(r"'Ml' for M(\d)", column("note")["rom92_m1"]).group(1))
    said("1933—1937 年，M1 每年平均增长近 10\\%", g0, g1, m1, g)
    said("按 Romer（1992）的一个简单计算，1942 年以前的复苏几乎全部来自货币的扩张", Y["rom92_abstract"],
         F["rom92_abstract"][0])
    p25, y37 = F["rom92_25pct"][:2]
    said("货币如果按历史上的平均速度增长，1937 年的实际 GNP 会低约 25\\%", y37, p25)
    assert "Friedman and Schwartz (1963, p. 511) as quoted by Romer" in column("note")["rom92_fed"]
    assert "high-powered money" in Q["rom92_fed"]
    said("照弗里德曼与施瓦茨的说法，1933—1941 年，美联储几乎没有主动改变基础货币", *F["rom92_fed"])
    d, y = F["frb_goldinflow"]
    assert "July 15, 1936" in Q["frb_goldinflow"]
    said("联邦储备委员会 1936 年 7 月也说", y, 7)
    a, y0, b, y1 = F["rom92_dr"]
    assert "from 8.86 in January 1933 to 6.67 in December 1942" in Q["rom92_dr"]
    said("存款与准备金之比从 1933 年 1 月的约 8.9 降到 1942 年 12 月的约 6.7", y0, 1, a, y1, 12, b)
    said("Romer（1992）的模拟里，财政政策的作用很小", Y["rom92_fiscal"])
    assert "His often-cited conclusion" in Q["rom92_brown"] and "unsuccessful recovery device in the 'thirties" in Q[
        "rom92_brown"]
    brown = int(re.search(r"Brown \((\d{4})\) as quoted by Romer", column("note")["rom92_brown"]).group(1))
    said("用 Brown（1956）常被引用的话说，1930 年代的财政政策看来没能带来复苏", brown, F["rom92_abstract"][1])
    said("1937—1938 年复苏又一次中断，失业率回升到 19.0\\%", 1937, 1938, A.unemployment_pct[1938])


def deeper(F, Y, Q):
    """The 史料说明."""
    m, src, N = meta(), meta()["sources"], column("note")
    A, T, B = annual(), money_table(), bea()
    procl = [int(re.search(r"Proclamation (\d+)", src[k]["version"]).group(1)) for k in ("app2039", "app2040", "app2072")]
    eo = int(re.search(r"Executive Order (\d+)", src["app6102"]["version"]).group(1))
    said("罗斯福的谈话、第 2039、2040 号公告、第 6102 号行政命令、第 2072 号公告与白宫的说明", procl[0], procl[1], eo, procl[2])
    said("1932 年的格拉斯—斯蒂格尔法、紧急银行法、1933 年的银行法与黄金储备法", Y["stat_feb27"], Y["ba_approved"])
    _, mo, d = F["fdr_march3d"]
    assert 'printed as "March 3d"' in Q["fdr_march3d"]
    said("谈话里的“3 月 3d”是原刊的写法", mo, d)
    d1, _, ey = F["frh_mar1"][:3]
    said("哈里森 3 月 1 日的急电，据联邦储备历史网站对 Eccles（1982）的转述", 3, d1, ey)
    assert "Hoover's memoirs (1952, p. 117)" in N["frh_hoover"]
    said("回忆 1932 年的法律时", Y["frh_hoover"])
    said("也只见于同一网站对他 1952 年回忆录的转引", F["frh_hoover1952"][0])
    brown = int(re.search(r"Brown \((\d{4})\) as quoted by Romer", N["rom92_brown"]).group(1))
    said("Meltzer（2003）、Chandler（1971）、Wicker（1996）、Temin（1976）、Hamilton（1987）、Clark（1933）与 Brown（1956）都是转引",
         F["frh_meltzer"][1], F["frh_freegoldworry"][2], F["frh_mar3"][1], F["rom90_temin"][0], F["rom90_hamilton"][0],
         F["bern_clark"][0], brown)
    assert "Hamilton (1987) as summarized by Romer" in N["rom90_hamilton"]
    said("Kryzanowski 与 Roberts（1993）对加拿大银行的看法，据 Bordo、Redish 与 Rockoff（2011）的转述", F["brr_forbearance"][0],
         F["brr_copyright"][0])
    said("他们的论证据伯南克 2002 年的讲话", F["bern_title"][1])
    for rid in ("bern_tragic", "bern_partway"):
        assert "as quoted by Bernanke" in N[rid], rid
    said("美联储 1933—1941 年几乎没有主动改变基础货币，是 Romer（1992）转引他们的话", *F["rom92_fed"], Y["rom92_fed"])
    d19, y19 = F["cyb_apr19"]
    said("美国离开金本位的日子，加拿大年鉴作 1933 年 4 月 19 日，联邦储备历史网站说罗斯福 4 月 20 日的公告正式中止了金本位", y19,
         4, d19, 4, F["frh_apr20"][0])
    y7 = F["frh_5000"][2]
    assert "became permanent in July 1934" in Q["frh_5000"] and "the FDIC's own history" in N["frh_5000"]
    said("联邦储备历史网站还说，存款保险基金在 1934 年 7 月改为永久", y7, 7)
    y98 = int(re.search(r"September (\d{4})", m["sources"]["fdic1998"]["version"]).group(1))
    said("这与联邦存款保险公司 1998 年的《存款保险简史》不合，正文据后者", y98)
    wheelock = int(re.search(r"Wheelock \((\d{4})\) could not be downloaded", m["notes"]).group(1))
    said("Wheelock（1992）对美联储信条的研究没有取得", wheelock)
    am = annual_meta()
    x0, x1 = map(int, re.search(r"X (\d+)-(\d+) \(Friedman and Schwartz", am["source"]).groups())
    said("转引自《美国历史统计》系列 X 410—417", x0, x1)
    assert "Banking and Monetary Statistics 1914-1941 (FRASER) could not be downloaded" in am["notes"]
    said("准备金余额取自《联邦储备公报》，1930 与 1931 年缺年平均", 1930, 1931)
    g, g0, g1 = F["rom92_m1"]
    m1 = A.m1_bn
    growth = 100 * ((m1[g1] / m1[g0]) ** (1 / (g1 - g0)) - 1)
    said("M1 的增长，照 Romer（1992）的说法，1933—1937 年每年平均近 10\\%", 1, Y["rom92_m1"], g0, g1, g)
    said("按《美国历史统计》系列 X 414 的年平均算，M1 从 199 亿美元增加到 309 亿美元，每年约增长 11.6\\%，比这还高",
         series_no("X", "currency plus demand deposits"), 1, m1[g0] * B9, m1[g1] * B9, growth)
    assert growth > g
    bul = A.money_in_circulation_m + A.member_reserves_m
    said("按公报自己的口径，流通中的货币加准备金余额，1929—1933 年也增加了 15.9\\%，与\\tabref{tab:depressionus-money}的 "
         "14.0\\% 方向一致", 1929, 1933, rise(bul[1929], bul[1933]), rise(T.H[1929], T.H[1933]))
    d86 = int(re.search(r"series D \d+-(\d+)", am["source"]).group(1))
    said("失业率据《美国历史统计》系列 D 86，1932 年是 23.6\\%", d86, 1932, A.unemployment_pct[1932])
    said("Romer（1992）用 Darby（1976）的失业序列，1932 年的高点是 23\\%，与之相近", Y["rom92_23pct"], F["rom92_darby"][0],
         F["rom92_23pct"][1], F["rom92_23pct"][0])
    assert abs(A.unemployment_pct[1932] - F["rom92_23pct"][0]) < 1                         # 与之相近
    misprint = re.search(r"E 135 prints (\d+\.\d) for (\d{4})", am["notes"])
    assert pd.isna(A.cpi_1967_100[int(misprint.group(2))])
    said("消费物价表上 1937 年印作 48.0", int(misprint.group(2)), float(misprint.group(1)))
    said("实际 GDP 1933—1937 年的增长，按美国经济分析局今天的数是 43.2\\%，Romer（1992）用旧的估计，是 33\\%", 1933, 1937,
         rise(B.gdp_real_2017[1933], B.gdp_real_2017[1937]), Y["rom92_33pct"], F["rom92_33pct"][5])
    said("公报 1937 年 9 月号的识别文本，把 1921—1936 年停业银行的总数 14,943 识别成 14,948，正文据扫描页与表 1 的合计", 1937, 9,
         *F["frb_14948"][:2], F["frb_table1"][0], F["frb_14948"][2], 1)
    assert "Table 1" in column("juan")["frb_table1"]
    assert "(p.3)" in Q["bern83_mse"] and "(U.14)" in Q["bern83_mse"] and "(11.1)" in Q["bern83_half_output"]
    said("伯南克 1983 年工作论文的识别文本把式 (4.1)—(4.4) 的编号多处认错，如“(11.1)”，表 2 的系数据扫描页读出",
         F["bern83_wp"][1], 4.1, 4.4, 11.1, 2)
    assert "Table 2" in column("juan")["bern83_t41"]
    said("1932 年每周的购买额、37 个州的银行关门", Y["frh_weekly"], F["frh_mar4"][2])
    cyb = int(re.search(r"\(Ottawa, (\d{4})\)", src["cyb1935"]["version"]).group(1))
    said("加拿大的数字只据它 1935 年的年鉴", cyb)


def models() -> None:
    """The key equations as the text writes them, and their arithmetic checked with numbers."""
    say("\\text{损失}=\\frac{\\delta}{1-\\delta}\\,(W-R),\\qquad \\text{资不抵债}\\iff \\frac{\\delta}{1-\\delta}\\,(W-R)>E."
        "\\label{eq:depressionus-firesale}",
        "\\frac{D_1/P_1}{D_0/P_0}=\\frac{1-x}{1+\\pi}.\\label{eq:depressionus-debt}")
    for W, R, delta in [(30, 10, 0.1), (30, 10, 0.3), (25, 5, 0.2), (50, 0, 0.5)]:
        sold = (W - R) / (1 - delta)
        chk(f"    eq:depressionus-firesale: sold x (1 - delta) raises W - R, and the loss is sold - (W - R) ({W}, {R}, "
            f"{delta})", sold - (W - R), delta / (1 - delta) * (W - R), tol=1e-12)
    for x, pi in [(0.2, 0.75 ** -1 - 1), (0.1, -0.1), (0.0, -0.1), (0.2, -0.2)]:
        D0, P0 = 100.0, 1.0
        D1, P1 = D0 * (1 - x), P0 * (1 + pi)
        chk(f"    eq:depressionus-debt ({x}, {pi:.3f})", (D1 / P1) / (D0 / P0), (1 - x) / (1 + pi), tol=1e-12)
    for C, D, R in [(3.9, 42.7, 3.258), (5.09, 27.13, 3.073), (1.0, 9.0, 0.9)]:
        M, H = C + D, C + R
        chk(f"    eq:money-mult: M/H = 1/(c + r - cr) ({C}, {D}, {R})", M / H, mult(C / M, R / D), tol=1e-12)


def frames(F, Y, Q):
    """The captions of the figures."""
    O, A = output_index(), annual()
    cy = cpi_years()
    said("(a) 美国的实际 GDP、GDP 平减指数与消费物价指数，都以 1929 年$=100$，1929—1941 年；消费物价只画到 1936 年", O.index[0],
         100, O.index[0], O.index[-1], cy[-1])
    u = A.unemployment_pct.dropna()
    said("(b) 失业率，占民用劳动力的百分比，1929—1941 年，1947 年以前按 14 岁以上的人统计", u.index[0], u.index[-1],
         *unemployment_rule())
    rel = re.search(r"last modified (\d{4})-(\d{2})-\d{2} \(the BEA release of that date\)", bea_meta()["notes"])
    am = annual_meta()
    d86 = int(re.search(r"series D \d+-(\d+)", am["source"]).group(1))
    e = int(re.search(r"E (\d+) \(BLS consumer price index", am["source"]).group(1))
    said("数据：美国经济分析局，国民收入与产品账户（2026 年 9 月的发布）；《美国历史统计》（1975）系列 D 86 与 E 135",
         int(rel.group(1)), int(rel.group(2)), hsus_year(), d86, e)
    S = A.susp_banks.dropna()
    assert sorted(S.sort_values().index[-4:]) == [1930, 1931, 1932, 1933]                  # 集中在 1930—1933 年
    said("银行停业集中在 1930—1933 年", 1930, 1933)
    assert "mutual savings banks excluded" in am["series"] and "mutual savings banks" in Q["frb_mutual"]
    said("(a) 每年停业的银行家数，1921—1936 年，不含互助储蓄银行", S.index[0], S.index[-1])
    said("1933 年包括银行假日以后没有领到营业执照、后来清理或改组的银行", F["frb_1933incl"][0])
    t = re.search(r"September 1937, 'Bank Suspensions, 1921-1936', Table (\d) \(p\. (\d+)\) and Table (\d) \(p\. (\d+)\)",
                  am["source"]).groups()
    said("数据：《联邦储备公报》1937 年 9 月，第 868 页表 1 与第 873 页表 2", 1937, 9, int(t[1]), int(t[0]), int(t[3]),
         int(t[2]))


def legacy(F, Y, Q):
    A = annual()
    d, y, ninety = F["bern_title"]
    assert "November 8, 2002" in Q["bern_title"]
    said("2002 年 11 月 8 日，弗里德曼九十岁生日的会上", y, 11, d)
    assert "Let me end my talk by abusing slightly" in Q["bern_abusing"]
    say("时任联邦储备理事的伯南克在讲话的最后说")
    chk("    the ninetieth birthday (九十岁)", [ninety, y - F["bnf_friedman"][0]], [told("弗里德曼九十岁生日的会上", "弗里德曼", "岁")] * 2)
    S = A.susp_banks
    assert S.loc[1934:1936].max() < S.loc[1921:1929].min()                                 # 一下子少了
    said("1934 年以后，美国的银行停业一下子少了", 1934)
    assert S.loc[1930:1933].sum() > 2000                                                   # 几千家
    said("1930—1933 年，美联储没有当好最后贷款人，几千家银行倒下", 1930, 1933)
    _, y7, y9 = F["frh_2007"]
    said("2007—2009 年的金融危机里", y7, 2000 + y9)
    said("1930 年代的名义利率已经很低", F["rom92_abstract"][1])


def takeaways(F, Y):
    A, B = annual(), bea()
    cpi, P, R = A.cpi_1967_100, A.unemployment_pct, B.gdp_real_2017
    said("1929—1933 年，美国的实际 GDP 降了 26.3\\%，消费物价降了 24.4\\%，失业率从 3.2\\% 升到 24.9\\%", 1929, 1933,
         fall(R[1929], R[1933]), fall(cpi[1929], cpi[1933]), P[1929], P[1933])
    said("1930—1933 年停业的银行共 9,096 家，谷底在 1933 年 3 月的银行休假", 1930, 1933, A.susp_banks.loc[1930:1933].sum(),
         F["frh_trough"][0], 3)
    said("复苏从 1933 年 3 月开始", 1933, 3)
    said("1933—1937 年实际 GDP 增长了 43.2\\%", 1933, 1937, rise(R[1933], R[1937]))


def selfcheck(F, Y):
    A, T = annual(), money_table()
    R, A_, D, W = SC1["R"], SC1["A"], SC1["D"], SC1["W"]
    E = R + A_ - D
    said("一家银行有准备金 5，其他资产 95，存款 94，资本 6，数字为教学输入", R, A_, D, E)
    said("存款人取走 25，资产只能按八折卖掉", W)
    p = told("资产只能按八折卖掉", "按", "卖掉")
    x, f = SC2["repay"], SC2["fall"]
    said("一年里还掉 10\\% 的名义债务，物价降 10\\%", x, f)
    cpi, cp = A.cpi_1967_100, A.cp_rate
    p32 = rise(cpi[1931], cpi[1932])
    said("1932 年商业票据的年利率是 2.73\\%，消费物价降了 10.3\\%", 1932, cp[1932], -p32)
    said("为什么基础货币增加了 14\\%，广义货币却减少了三成", rise(T.H[1929], T.H[1933]))
    old, new, P0 = F["p2072_old"][0], F["p2072_weight"][0], F["frh_40pct"][2]
    said("新金元含金$15\\frac{5}{21}$格令，旧金元 25.8 格令。旧金价是每盎司 20.67 美元", 15, 5, 21, old, P0)
    chk("    15 5/21 = the proclamation's weight", 15 + 5 / 21, new, tol=1e-6)
    # answers
    need = W - R
    sold = need / p
    loss = sold - need
    said("要凑足$25-5=20$，得卖掉$20/0.8=25$的资产，损失 5，小于资本 6，还有 1 的资本", W, R, need, need, p, sold, loss, E,
         E - loss)
    assert loss < E
    q = told("折扣再大一点，比如七折", "比如")
    said("折扣再大一点，比如七折，损失约 8.6，就资不抵债了", need / q - need)
    assert need / q - need > E
    said("$(1-0.1)/(1-0.1)=1$，实际债务不变。物价不变时，实际债务减少 10\\%", 1, x / 100, 1, f / 100,
         (1 - x / 100) / (1 - f / 100), x)
    r32 = 100 * ((1 + cp[1932] / 100) / (1 + p32 / 100) - 1)
    said("$1.0273/(1-0.103)-1\\approx14.5\\%$", 1 + cp[1932] / 100, 1, -p32 / 100, 1, r32)
    said("乘数$m=1/[C/M+R/D-(C/M)(R/D)]$", 1)
    said("通货比率从 0.084 升到 0.158，准备金比率从 0.076 升到 0.113，乘数从 6.51 降到 3.95", T.c[1929], T.c[1933], T.r[1929],
         T.r[1933], T.m[1929], T.m[1933])
    four = told("降了近四成", "降了近")
    assert four - 0.05 < fall(T.m[1929], T.m[1933]) / 100 < four                          # 近四成
    ratio = new / old
    said("含金量之比约 0.5906，金价约$20.67/0.5906\\approx35$美元", ratio, P0, ratio, P0 / ratio)


def ending(F, Y, Q):
    d, y = F["fdr_title"]
    assert "more important than currency, more important than gold, and that is the confidence of the people" in Q[
        "fdr_confidence"]
    said("1933 年 3 月 12 日，罗斯福在谈话的最后说", y, 3, d)
    d15, pts, close, gain = F["frh_dow"]
    chk("    8.26 points to 62.10 is a gain of 15.34%", 100 * pts / (close - pts), gain, tol=0.005)
    said("3 月 15 日股市重新开盘，道琼斯指数一天涨了 15.34\\%", 3, d15, gain)
    assert "On April 20" in Q["frh_apr20"]
    said("可是美国要到这一年 4 月才离开黄金", 4)
    said("英国早在 1931 年 9 月就离开了", F["frh_britain"][1], 9)
    assert "remained on the gold standard as long as possible" in Q["bern_goldbloc"]
    say("法国与所谓金集团的其他国家还要尽可能久地守着它")
    assert Q["fdr_together"] == "Together we cannot fail."
    say("他的最后一句是：“我们齐心，就不会失败。”")
    q29 = re.search(r"\\guidequestion\{([^}]*)\}", (ROOT / "zh" / "ch29_depressionworld.tex").read_text(encoding="utf-8"))
    assert q29 and q29.group(1).startswith(NEXT), "Chapter 29's guide question does not begin with NEXT"
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 29's question"


# the life dates the chapter gives without a row of its own: the same words in an earlier chapter
LIVES = {"Irving Fisher，1867—1947": "ch25_wicksell", "Benjamin Strong，1872—1928": "ch27_interwar"}
# the life dates from rows of the snapshot: words -> (row, index of the birth year, index of the death year)
ROW_LIVES = {"Franklin D. Roosevelt，1882—1945": ("bnf_roosevelt", 0, 1),
             "Eugene Meyer，1875—1959": ("loc_meyer", 0, 1),
             "Milton Friedman，1912—2006": ("bnf_friedman", 0, 1),
             "Anna J. Schwartz，1915—2012": ("bnf_schwartz", 0, 1),
             "Andrew Mellon，1855—1937": ("bnf_mellon", 0, 1),
             "Herbert Hoover，1874—1964": ("bnf_hoover", 0, 1),
             "George Leslie Harrison（1887—1958）": ("loc_harrison", 0, 1)}
# people whose dates were not found (the 史料说明 says so)
UNKNOWN = ["George Harrison，生卒年未详"]
# what other chapters tell: (words of this chapter, chapter where it is told, words there)
EVENTS = [("美国的实际 GDP 从 1929 年到 1933 年降了 26.3\\%，GDP 平减指数降了 25.8\\%（\\exref{ex:accounts-depression}）",
           "ch02_accounts", "到 1933 年下降 26.3\\%；平减指数同期下降 25.8\\%"),
          ("三年半以前，1929 年 10 月，纽约股市崩盘（\\chref{ch:interwar}）", "ch27_interwar", "1929 年 10 月 28 日"),
          ("其中 40\\% 的黄金准备写在 1913 年的联邦储备法里（\\chref{ch:goldstandard}）", "ch23_goldstandard",
           "对流通中的联邦储备券至少要有 40\\% 的黄金准备"),
          ("亚特兰大联储认为，最后贷款人的责任及于整个银行体系（\\chref{ch:goldstandard}）", "ch23_goldstandard",
           "\\textbf{最后贷款人}"),
          ("挤兑的力量，可以在\\chref{ch:money}的资产负债表上看清", "ch04_money", "资产负债表"),
          ("两者都会让货币存量收缩（式~\\eqref{eq:money-mult}）", "ch04_money",
           "m=\\frac{1}{C/M+R/D-(C/M)(R/D)}.\\label{eq:money-mult}"),
          ("\\chref{ch:money}的式~\\eqref{eq:money-mult}把货币存量$M$分成基础货币$H$与两个比率，通货比率$C/M$与准备金比率$R/D$",
           "ch04_money", "$C/M$ 叫通货比率，$R/D$ 叫准备金比率"),
          ("1929 年秋天还说股价低（\\chref{ch:interwar}）", "ch27_interwar", "1929 年 10 月 22 日，《纽约时报》的一条标题是“费雪说股价低”"),
          ("实际利率由\\chref{ch:prices}的费雪关系给出，$1+r=(1+i)/(1+\\pi)$（式~\\eqref{eq:prices-fisher}）", "ch03_prices",
           "1+r^{\\text{事后}}_t=\\frac{1+i_t}{1+\\pi_{t+1}}.\\label{eq:prices-fisher}"),
          ("\\chref{ch:tokugawa}讲过，元文改铸用新币还旧债，减轻了大名与武士的债务，银贵又让以银计的债务与税额变重", "ch17_tokugawa",
           "元文改铸用新币还旧债，减轻了大名与武士的债务；银贵让以银计的债务与税额变重"),
          ("第一次是 1928 年春天到 1929 年 10 月的收紧（\\chref{ch:interwar}）", "ch27_interwar", "1928—1929 年又收紧"),
          ("斯特朗 1928 年去世（\\chref{ch:interwar}）", "ch27_interwar", "Benjamin Strong，1872—1928"),
          ("真实票据论主张，生产与贸易扩张时多供应资金，收缩时少供应（\\chref{ch:smith}）", "ch18_smith", "\\textbf{真实票据}"),
          ("\\chref{ch:goldstandard}问过，发行的限额有了弹性以后，纪律靠什么", "ch23_goldstandard", "弹性有了，纪律靠什么"),
          ("一次不超过 30 天，不足的部分缴累进的税（\\chref{ch:goldstandard}）", "ch23_goldstandard", "一次不超过 30 天"),
          ("1900 年的金本位法规定，金元含 25.8 格令、成色十分之九的黄金（\\chref{ch:goldstandard}）", "ch23_goldstandard",
           "1900 年美国以法律确立金本位"),
          ("格令是比盎司小得多的重量单位（\\chref{ch:goldstandard}）", "ch23_goldstandard", "格令是比盎司小得多的重量单位"),
          ("大银行带头，先查明受挤兑的银行其实健全，再借现金给它们（\\chref{ch:goldstandard}）", "ch23_goldstandard",
           "这一次，挑选救谁的不是中央银行，是银行家们自己")]


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
    born = 1900 + F["loc_bernanke"][0]
    assert "(b. 12-13-53)" in Q["loc_bernanke"] and "1953-12-13" in column("note")["loc_bernanke"]
    assert f"Ben Bernanke，{born:.0f}— " in t
    assert "Harrison, George Leslie" in Q["loc_harrison"] and "a candidate only" in column("note")["loc_harrison"]
    assert "George L. Harrison President New York Fed" in Q["frh_harrison"]
    for words in UNKNOWN:
        assert words in t, words
    say("哈里森的生卒年没有查到", "记录没有写他的职务，正文不用")
    for here, ch, there in EVENTS:
        assert here in t, here
        assert there in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (ch, there)
    print(f"ok {len(LIVES) + len(ROW_LIVES) + 1} life dates, {len(UNKNOWN)} unknown, {len(EVENTS)} statements of other "
          "chapters")


def identities(F) -> None:
    """The annual snapshot's identities, and its values read on page images against the totals they print."""
    A = annual()
    am = annual_meta()
    x = A.loc[1929:1941]
    chk("deposits = demand + time (X 411 = X 412 + X 413), 1929-1941",
        (x.deposits_bn - x.demand_deposits_bn - x.time_deposits_bn).abs().max(), 0, tol=0.0101)
    chk("M1 = currency + demand deposits (X 414)", (x.m1_bn - x.currency_bn - x.demand_deposits_bn).abs().max(), 0,
        tol=0.0101)
    chk("M2 = currency + deposits (X 415)", (x.m2_bn - x.currency_bn - x.deposits_bn).abs().max(), 0, tol=0.0101)
    banks, dep = re.search(r"printed totals ([\d,]+) banks and \$([\d,]+) thousand", am["notes"]).groups()
    chk("suspensions 1921-1936 add up to Table 1's total", A.susp_banks.loc[1921:1936].sum(), figure(banks))
    chk("    = the total read on the page image (frb_table1)", F["frb_table1"][0], figure(banks))
    chk("deposits of suspended banks 1921-1936 add up to Table 2's total (thousands)",
        A.susp_deposits_thousands.loc[1921:1936].sum(), figure(dep))
    yrs = [1929, 1932, 1933, 1934, 1935, 1936]
    b = A.loc[yrs]
    sources = b.rb_credit_m + b.gold_stock_m + b.treasury_currency_m
    uses = (b.money_in_circulation_m + b.treasury_cash_m + b.treasury_deposits_m + b.nonmember_deposits_m +
            b.member_reserves_m)
    chk("p. 112: sources = uses of member bank reserve funds, each year (millions)", (sources - uses).abs().max(), 0,
        tol=1)
    assert (b.excess_reserves_m < b.member_reserves_m).all()
    col, oct_ = F["frb_t12_1931"], F["frb_oct1931"]
    chk("Table 12: the twelve months of 1931 add up to the year", sum(col[:12]), col[12])
    chk("    = Table 1's 1931", col[12], A.susp_banks[1931])
    chk("Table 12: October 1921-1936 adds up to its total", sum(oct_[1:]), oct_[0])
    chk("    October 1931: the row = the column = Bernanke's 522", [oct_[1 + 1931 - 1921], col[9]], [F["bern_522"][0]] * 2)
    assert F["frb_14948"][2] != F["frb_table1"][0] and "14,943" in column("note")["frb_14948"]   # the OCR's misprint


def witnesses(F, Q):
    """Second witnesses of statements of the text, and the bibliography block of the chapter."""
    N = column("note")
    chk("the Emergency Banking Act: the Statutes = Federal Reserve History (9 March 1933)", F["eba_title"], F["frh_mar9"])
    chk("the Banking Act of 1933 approved = signed (16 June 1933)", F["ba_approved"][:2], F["frh_gs_signed"])
    chk("the Gold Reserve Act: the Statutes = Federal Reserve History = the White House (30 January 1934)",
        [F["gra_title"][0], F["frh_gra_title"][0]], [F["wh_tuesday"][1]] * 2)
    chk("    the proclamation the day after (Federal Reserve History; Proclamation 2072 of the 31st)",
        F["p2072_time"][2] - F["wh_tuesday"][1], 1)
    assert "the day after he signed the act" in Q["frh_nextday"]
    chk("the deposit insurance limit: the Statutes = Federal Reserve History ($2,500)", F["ba_2500"][0], F["frh_5000"][1])
    chk("the stabilization fund: the White House = Federal Reserve History ($2 billion)", F["wh_fund"][0],
        F["frh_fund"][1] * B9)
    chk("the gold cover: 40% (Federal Reserve History, two essays)", F["frh_40pct"][1], F["frh_40reserve"][0])
    chk("the old price of gold: $20.67 (Federal Reserve History, two essays)", F["frh_40pct"][2], F["frh_1900"][2])
    chk("the day the United States left gold: 19 April (Canada Year Book) and the proclamation of 20 April (Federal "
        "Reserve History)", F["frh_apr20"][0] - F["cyb_apr19"][0], 1)
    chk("the new dollar at 59 per cent of the old (Federal Reserve History) and 59.06 plus (the White House)",
        F["frh_1900"][0], F["wh_5906"][0], tol=0.5)
    chk("the old gold content: Proclamation 2072 = the White House (25.8 grains)", F["p2072_old"], F["wh_5906"][1:])
    chk("the Gold Standard Act of 1900: the White House and Proclamation 2072 agree on the year", F["wh_1900"][1],
        F["p2072_1900"][1])
    assert F["wh_1900"][0] != F["p2072_1900"][0] and "approved March 14, 1900" in N["wh_1900"]   # 4 vs 14 March
    chk("the Federal Reserve Board's holdings: purchases of 1932 (FRH 'over $1 billion' = the Bulletin's $1,015 million)",
        F["frh_weekly"][2] * B9, F["frb_1015"][0], tol=0.05 * B9)
    chk("excess reserves at the end of January 1933 (Bulletin, $500 million) and the 1933 average (p. 112)",
        F["frb_500m"][0], annual().excess_reserves_m[1933] * M6, tol=0.1 * B9)
    chk("Harrison in office in March 1933 (Federal Reserve History, 1928-1940)",
        F["frh_harrison"][0] <= 1933 <= F["frh_harrison"][1], 1)
    chk("Meyer governor of the Board in 1932-33 (Federal Reserve History, 1930-1933)",
        F["frh_meyerdates"][0] <= 1932 <= F["frh_meyerdates"][1], 1)
    assert "Friedman and Schwartz '1964'" in N["frh_hoarding"] and F["frh_hoarding"][0] == 1964
    assert "1863-1960" in Q["bern_fs1963"] and "'1863-1960'" in N["bern_fs1963"]
    assert "Bernanke quoting Friedman and Schwartz (1963)" in N["bern_oct1931"]
    # the licences and the bibliography
    m = meta()
    for words in ("Online by Gerhard Peters and John T. Woolley, The American Presidency Project",
                  "'Copyright 1933 by the Econometric Society.'",
                  ("'© 2011 by Michael D. Bordo, Angela Redish, and Hugh Rockoff. All rights reserved. Short sections "
                   "of text, not to exceed two paragraphs, may be quoted without explicit permission provided that full "
                   "credit, including © notice, is given to the source.'"),
                  "print no copyright line", "out of Crown copyright", "Licence Ouverte (Open License)",
                  "are public data", "are in the public domain"):
        assert words in m["license"], words
    assert Q["fdr_credit"] == "Online by Gerhard Peters and John T. Woolley, The American Presidency Project"
    assert Q["fis_copyright"] == "Copyright 1933 by the Econometric Society."
    assert Q["brr_copyright"].startswith("© 2011 by Michael D. Bordo, Angela Redish, and Hugh Rockoff.")
    assert "Public domain" in annual_meta()["license"]
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    start = bib.index("% ---- 第 28 章")
    following = re.search(r"^% ---- 第 \d+ 章", bib[start + 1:], re.MULTILINE)
    end = start + 1 + following.start() if following else bib.index("\\end{thebibliography}")
    block = bib[start:end]
    items = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", block)}
    for key in ("fdr1933", "app1933", "app1934"):
        assert "Online by Gerhard Peters and John T. Woolley, The American Presidency Project" in items[key], key
        assert "公有领域" in items[key], key
    assert "Copyright 1933 by the Econometric Society（只引短句）" in items["fisher1933"]
    assert Q["brr_copyright"] in items["brr2011"]
    wp, yr = F["bern83_wp"]
    assert f"NBER Working Paper {wp:.0f}, January {yr:.0f}" in items["bernanke1983"]
    assert f"NBER Working Paper {F['rom90_wp'][0]:.0f}, June 1988" in items["romer1990"]
    assert "June 1988" in m["sources"]["nberw2639"]["version"]
    assert f"NBER Working Paper {F['rom92_wp'][0]:.0f}, September 1991" in items["romer1992"]
    assert "September 1991" in m["sources"]["nberw3829"]["version"]
    for key in ("bernanke1983", "romer1990", "romer1992", "frhgd", "frhpanic1", "frhpanic2", "frhba32", "frhholiday",
                "frheba", "frhba33", "frhgold", "frhgra"):
        assert "只引短句" in items[key], key
    for key in ("stat1932", "eba1933", "ba1933", "gra1934", "frb1933", "frb1937a", "frb1937b", "census1975a",
                "census1975x", "bernanke2002"):
        assert "公有领域" in items[key], key
    assert "王室版权已过期" in items["cyb1935"]
    assert "Licence Ouverte" in items["bnf28"] and "id.loc.gov" in items["loc28"]
    assert "公有领域" in items["fdic1998"] and m["sources"]["fdic1998"]["format"] == "pdf"
    keys = set(re.findall(r"\\bibitem\{([^}]+)\}", bib))
    cited = {k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", tex_text()) for k in c.split(",")}
    assert cited <= keys, sorted(cited - keys)
    assert set(items) <= cited, sorted(set(items) - cited)
    print(f"ok {len(cited)} works cited, {len(items)} of them in the bibliography block of Chapter 28")


def counts() -> None:
    """The editor's limits: “不能” at most about a dozen; no cited author as the subject of a sentence outside the
    史料说明 (Fisher, Friedman and Schwartz and Bernanke are the chapter's actors)."""
    t = tex_text()
    main = re.sub(r"\\begin\{deeper\}\[史料说明\].*?\\end\{deeper\}", "", t, flags=re.DOTALL)
    n = t.count("不能")
    print(f"ok “不能” {n} times")
    assert n <= 12, n
    verbs = "认为|写道|说|指出|记述|估计|承认|报道|记载|提到|列出|给出|发现|统计|算出"
    names = ("Romer|Temin|Meltzer|Clark|Kryzanowski|Roberts|Bordo|Redish|Rockoff|Wheelock|Chandler|Wicker|Brown|Darby|"
             "Eccles|Hamilton|联邦储备历史网站")
    subj = re.findall(r"(?:^|[。；：，\n])\s*(?:" + names + r")(?:（\d{4}）)?(?:" + verbs + ")", main)
    assert not subj, subj
    assert "这一节回答" not in t and "不能据此断言" not in t


def main() -> None:
    df = _rows()
    F, Y, Q = facts(), years(), quotes()
    check_readings(df)
    check_text(df)
    identities(F)
    guide(F, Y, Q)
    opening(F, Y, Q)
    world(F, Y, Q)
    panics(F, Y, Q)
    run(F, Y, Q)
    fisher(F, Y, Q)
    money(F, Y, Q)
    fed(F, Y, Q)
    credit(F, Y, Q)
    recovery(F, Y, Q)
    deeper(F, Y, Q)
    models()
    frames(F, Y, Q)
    legacy(F, Y, Q)
    takeaways(F, Y)
    selfcheck(F, Y)
    ending(F, Y, Q)
    book(F, Q)
    witnesses(F, Q)
    counts()
    coverage()
    anchors("zh/ch28_depressionus.tex", df["id"], script=Path(__file__))


if __name__ == "__main__":
    main()
