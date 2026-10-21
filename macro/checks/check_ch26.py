"""Chapter 26 (一战、赔款与魏玛恶性通胀): every number and every quotation in zh/ch26_weimar.tex.

    python3 checks/check_ch26.py

Inputs:
  weimar_facts              quotations of Keynes (1919, A Tract on Monetary Reform 1923, 1925, 1929 and the
                            rejoinder), Ohlin (1929), Bresciani-Turroni (1937), Sargent (1982) and the NBER volume,
                            Fischer, Sahay and Vegh (2002), Koech (2011), Fisher (1930), the Rentenbank decree (1923),
                            the London Schedule (1921), the Bundesarchiv, the Neue Deutsche Biographie (Havenstein,
                            Helfferich, Rathenau, Luther, Schacht), NobelPrize.org and Wikisource (checked by
                            data/fetch/verify_web_quotes.py)
  weimar_prices_1914_1919   Sargent's Table G1: the German wholesale price index (1913 = 100), monthly, 1914-1919
  weimar_prices_1920_1924   the same table, January 1920 - June 1924 (paper marks throughout)
  weimar_budget_1923_1924   Sargent's Table G5: ordinary revenue, taxes and expenditure of the Reich (million gold
                            marks)
  weimar_notes_1923_1924    Bresciani-Turroni, p. 337: old notes (in million rentenmarks) and rentenmarks, three month
                            ends
When the NBER PDF of Sargent's chapter is in the web cache, Tables G1 and G5 are parsed from it and compared with the
snapshots month by month.
The figure module figsrc/fig_ch26.py imports prices(), notes(), budget() and inflation_multiples() from here.

What is checked here:
  1. readings   every number of the value column of weimar_facts is read from its quotation (digits, English and
                German number words, ordinals, fractions, and the OCR's misprints, each named)
  2. the text   every “…” of the chapter is the chapter's Chinese rendering of a quotation (TRANSLATIONS:
                rendering -> row or rows), with the source's words listed in KEYWORDS
  3. numbers    every number of the text, section by section: said() finds the phrase in the text and compares each
                number it prints (with its unit 万, 亿, 万亿) with the value computed from the snapshots, within half a
                unit of the last printed digit; Chinese numerals (八分之一, 三倍, 六成 ...) are read by zh() and
                compared the same way
  4. the book   life dates, what other chapters tell, the bibliography block of the chapter and its licence notices
  5. anchors    the paraphrase anchors `% 据: ...` name rows of weimar_facts

Models (the chapter's key equations):
    the transfer (eq:weimar-transfer): R^f = (P_X^f X - P_I^f Q) + K^f (superscript f: in foreign money, Appendix B)
    seigniorage (eq:weimar-budget): Delta H / P = Delta h + pi / (1 + pi) h_{t-1}, with h = H / P
    money demand (eq:weimar-demand): M / P = k Y, V = 1 / k
    Fisher's relation (Chapter 3, eq:prices-fisher): 1 + r = (1 + i) / (1 + pi)
    the doubling time of a monthly ratio x, at a constant daily rate over 30 days: d = 30 ln 2 / ln x
"""
from __future__ import annotations

import math
import os
import re
import subprocess
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd

from common import ROOT, anchors, load_snapshot, quoted

TEX = ROOT / "zh" / "ch26_weimar.tex"
CACHE = Path(os.environ.get("WEB_CACHE", Path.home() / ".cache" / "finance-study" / "web"))
MONTH = 30                                  # days in a month, for the doubling times
# Teaching inputs stated in the text
SHARE = 0.20                                # ex:weimar-transfer: 20% of the spending on imports / German goods
LAG = 14                                    # ex:weimar-taxlag: the tax is paid two weeks late
LOAN = 1.00                                 # ex:weimar-realrate (3): a loan at 100% a month
SC1 = {"R": 100, "surplus": 40}             # self-check 1
SC3 = {"H0": 100, "P0": 100, "H1": 300, "P1": 500}  # self-check 3
GUIDE = "一个国家为什么会印钞印到物价每天翻倍？恶性通胀又是怎样一夜止住的？"


def chk(what: str, value, expected=None, tol: float = 1e-9, rel: float = 0.0) -> float:
    """quoted() with a tolerance for floating-point error on exact values; a list is compared element by element."""
    if isinstance(value, (list, tuple, np.ndarray, pd.Series)):
        value = list(value)
        assert expected is not None and len(value) == len(expected), (what, value, expected)
        for i, (v, e) in enumerate(zip(value, expected)):
            quoted(f"{what} [{i + 1}]", float(v), e, tol=tol, rel=rel)
        return float(value[0])
    return quoted(what, float(value), expected, tol=tol, rel=rel)


def pct(what: str, value: float, expected: float, digits: int = 1) -> float:
    """A number printed with `digits` decimals (half a unit of the last digit, plus room for binary rounding)."""
    return quoted(what, float(value), expected, tol=0.5 * 10 ** -digits + 1e-9)


# ---------------------------------------------------------------------------------------------------
# Loaders
def _rows() -> pd.DataFrame:
    df, meta = load_snapshot("weimar_facts", dtype=str, keep_default_na=False)
    assert 26 in meta["used_in"]
    assert df["id"].is_unique
    return df


def num(x: str) -> float:
    """'5', '1/8', '58.5'."""
    if "/" in x:
        a, b = x.split("/")
        return float(a) / float(b)
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


def _prices(name: str, first: str, last: str, n: int) -> pd.DataFrame:
    df, m = load_snapshot(name)
    assert 26 in m["used_in"] and "© 1982 by The National Bureau of Economic Research" in m["license"]
    p = df.set_index("date")
    assert p.index.is_unique and p.index.is_monotonic_increasing and len(p) == n
    assert p.index[0] == first and p.index[-1] == last and (p.source == "sargent1982").all()
    return p


def prices() -> pd.DataFrame:
    """Germany, wholesale prices (1913 = 100, paper marks), monthly, January 1920 - June 1924, indexed by 'YYYY-MM'."""
    return _prices("weimar_prices_1920_1924", "1920-01", "1924-06", 54)


def prices_war() -> pd.DataFrame:
    """The same index, January 1914 - December 1919."""
    return _prices("weimar_prices_1914_1919", "1914-01", "1919-12", 72)


def notes() -> pd.DataFrame:
    """Old Reichsbank notes (paper marks / 10^12, i.e. million rentenmarks) and rentenmarks (million), month ends."""
    df, m = load_snapshot("weimar_notes_1923_1924")
    assert 26 in m["used_in"] and "ALL RIGHTS RESERVED" in m["license"]
    assert list(df.date) == ["1923-12", "1924-03", "1924-07"]
    return df


def budget() -> pd.DataFrame:
    """The ordinary budget of the Reich, December 1923 - June 1924 (million gold marks)."""
    df, m = load_snapshot("weimar_budget_1923_1924")
    assert 26 in m["used_in"] and "© 1982 by The National Bureau of Economic Research" in m["license"]
    assert list(df.date) == ["1923-12", "1924-01", "1924-02", "1924-03", "1924-04", "1924-05", "1924-06"]
    return df


def inflation_multiples() -> tuple[np.ndarray, np.ndarray]:
    """Sargent, p. 82: the factors by which wholesale prices and Reichsbank notes rose from January 1922 to July and
    to August 1923 (fig:weimar_balances (a))."""
    F = facts()
    p = np.array([F["s_ratio1"][2], F["s_ratio2"][2]])
    n = np.array([F["s_ratio1"][3], F["s_ratio2"][3]])
    return p, n


def index_all() -> pd.Series:
    """The whole monthly index of the snapshots, January 1914 - June 1924."""
    return pd.concat([prices_war().wpi_1913_100, prices().wpi_1913_100])


# ---------------------------------------------------------------------------------------------------
# The arithmetic of the chapter
def ratio(month: str) -> float:
    """The index of a month divided by the index of the month before."""
    s = index_all()
    k = list(s.index).index(month)
    return float(s.iloc[k] / s.iloc[k - 1])


def doubling(x: float, days: int = MONTH) -> float:
    """The days in which prices double if they rise by the factor x in `days` days at a constant daily rate."""
    return days * math.log(2) / math.log(x)


def seigniorage(H0: float, P0: float, H1: float, P1: float) -> tuple[float, float, float]:
    """eq:weimar-budget: (Delta H / P, Delta h, the inflation tax pi / (1 + pi) h_{t-1}), in baskets."""
    h0, h1, pi = H0 / P0, H1 / P1, P1 / P0 - 1
    return (H1 - H0) / P1, h1 - h0, pi / (1 + pi) * h0


def months_between(a: str, b: str) -> int:
    """The months from a to b inclusive, both 'YYYY-MM'."""
    ya, ma = map(int, a.split("-"))
    yb, mb = map(int, b.split("-"))
    return (yb - ya) * 12 + mb - ma + 1


# ---------------------------------------------------------------------------------------------------
# Sargent's Tables G1 and G5, parsed from the NBER PDF when it is in the cache
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]


def _sargent_text() -> str | None:
    pdf = CACHE / "sargent1982.pdf"
    if not pdf.exists():
        return None
    return subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, check=True).stdout


def table_g1(raw: str) -> dict[str, int]:
    """'YYYY-MM' -> the index of Table G1 (two columns of months on each page; a year opens a run of months)."""
    start = raw.index("Table Gl         German Wholesale Prices")
    block = raw[start:raw.index("surely understated by the reparations")]
    pat = re.compile(r"(?:(19\d{2})\s+)?(" + "|".join(MONTHS) + r")\s+([\d,]+)")
    year = [None, None]
    out = {}
    for line in block.splitlines():
        for side, m in enumerate(pat.finditer(line)):
            y, mon, v = m.groups()
            if y:
                year[side] = int(y)
            if year[side]:
                out[f"{year[side]}-{MONTHS.index(mon) + 1:02d}"] = int(v.replace(",", ""))
    return out


def table_g5(raw: str) -> dict[str, list[float]]:
    """'YYYY-MM' -> [revenue, of which taxes, expenditure, balance] of Table G5 (November 1923 has two numbers)."""
    block = raw[raw.index("Table G5"):raw.index("Source: Young [36, vol. 1, p. 422]")]
    out, year = {}, None
    for line in block.splitlines():
        y = re.match(r"\s*(19\d\d):", line)
        if y:
            year = int(y.group(1))
            continue
        m = re.match(r"\s*(" + "|".join(MONTHS) + r")\s+(.*)$", line)
        if m and year:
            vals = [float(v.replace(" ", "")) for v in re.findall(r"[+-]?\s?\d+\.\d", m.group(2))]
            out[f"{year}-{MONTHS.index(m.group(1)) + 1:02d}"] = vals
    return out


def check_tables() -> None:
    raw = _sargent_text()
    if raw is None:
        print("note: sargent1982.pdf is not in the web cache; Tables G1 and G5 not compared with the PDF")
        return
    g1 = table_g1(raw)
    chk("Table G1: months parsed, 1914-01 to 1924-12", len(g1), 132)
    s = index_all()
    for k, v in s.items():
        assert g1[k] == v, (k, g1[k], v)
    print(f"ok Table G1 = the two price snapshots, {len(s)} months")
    # 7 月起表中改用新单位: July-December 1924 are printed with the footnote mark 1 ('1151' = 115 and the mark)
    assert "On basis of prices in reichsmarks. (1 reichsmark = 1 trillion" in raw
    new = {k: int(str(v)[:-1]) for k, v in g1.items() if k >= "1924-07"}
    assert len(new) == 6 and all(str(g1[k]).endswith("1") and 100 < v < 140 for k, v in new.items())
    assert abs(g1["1924-06"] / 10 ** 12 - new["1924-07"]) < 2
    g5 = table_g5(raw)
    b = budget().set_index("date")
    for k, r in b.iterrows():
        rev, tax, exp, bal = g5[k]
        chk(f"Table G5 {k}: revenue, taxes, expenditure", [r.revenue_million_goldmark, r.taxes_million_goldmark,
                                                           r.expenditure_million_goldmark], [rev, tax, exp], tol=1e-9)
        pct("    the balance printed in G5 (revenue - expenditure)", rev - exp, bal, 1)
    chk("Table G5 November 1923: revenue, taxes (no expenditure)", g5["1923-11"], [68.1, 63.2])
    surplus = [k for k, v in g5.items() if k >= "1924-03"]
    assert surplus[-1] == "1924-10" and all(g5[k][3] > 0 for k in surplus)   # 3 月以后月月有盈余
    print(f"ok Table G5: surpluses in every month from March to October 1924 ({len(surplus)} months)")


# ---------------------------------------------------------------------------------------------------
# 1. Readings of the numbers
SMALL = {"a": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "twenty": 20, "thirty": 30}
MULT = {"hundred": 100, "thousand": 1000, "millions": 10 ** 6}
ORDINAL = {"half": 2, "eighth": 8}
NTH = {"ninth": 9, "third": 3}
GERMAN = {"einer": 1, "eine": 1}
OCR = {"r,2oo": 1200, "nth": 11, "1485,014": 1485014, "12 1": 12.5}       # misprints of the OCR, each named in the note


def cardinal(s: str) -> float:
    """An English cardinal: 'thirty', 'twenty-four', 'a hundred', 'two thousand', 'two millions'."""
    total, part = 0, 0
    for w in s.lower().replace("-", " ").split():
        if w in SMALL:
            part += SMALL[w]
        else:
            part = max(part, 1) * MULT[w]
            if MULT[w] >= 1000:
                total, part = total + part, 0
    return float(total + part)


def fraction(s: str) -> float:
    """'one-eighth'."""
    a, b = s.lower().replace("-", " ").split()
    return float(Fraction(int(cardinal(a)), ORDINAL[b]))


def figure(s: str) -> float:
    return float(s.replace(",", ""))


def read(phrase: str, how: str) -> list[float]:
    if how == "num":
        return [figure(phrase)]
    if how == "en":
        return [cardinal(phrase)]
    if how == "frac":
        return [fraction(phrase)]
    if how == "half":                         # 'half a trillion'
        return [0.5]
    if how == "nth":                          # 'the ninth war loan'
        return [float(NTH[phrase])]
    if how == "fortnight":                    # 'about a fortnight'
        return [14.0]
    if how == "range":                        # '1914-18', '1908-23': the second year in two digits
        a, b = phrase.split("-")
        return [float(a), float(a[:2] + b)]
    if how == "dmy":                          # '10.3.1857': day, month, year
        return [float(x) for x in phrase.split(".")]
    if how == "de":                           # '3.200': German thousands
        return [float(phrase.replace(".", ""))]
    if how == "decomma":                      # '3,2': a German decimal comma
        return [float(phrase.replace(",", "."))]
    if how == "deword":                       # 'einer Billion'
        return [float(GERMAN[phrase])]
    if how == "star":                         # '14*5': the OCR prints the decimal point as '*'
        return [float(phrase.replace("*", "."))]
    if how == "dash":                         # '58-5': ... or as '-'
        return [float(phrase.replace("-", "."))]
    if how == "gap":                          # '41 1', '1 5th': a space inside the number
        return [float(re.sub(r"\D", "", phrase))]
    if how == "ocr":
        return [float(OCR[phrase])]
    raise ValueError(how)


FIGURES = re.compile(r"\d[\d,]*(?:\.\d+)?|\.\d+")
EN, NUM = "en", "num"
# id -> [(phrase, how)], in order. A phrase 'context|word' is searched as a whole and read from `word`. Rows not
# listed are read with all the figures of the quotation.
READINGS = {
    "bt_warloans": [("98", NUM), ("one-eighth", "frac"), ("1914-18", "range")],
    "bt_warshort": [("1916", NUM), ("1918", NUM), ("ninth", "nth"), ("48", NUM)],
    "bt_1920counter": [("89", NUM), ("176*6", "star"), ("54,456", NUM), ("81,735", NUM)],
    "bt_wagetax": [("1923", NUM), ("about a fortnight", "fortnight")],
    "bt_goldmark": [("160", NUM), ("1922", NUM), ("41 1", "gap")],
    "bt_presses": [("1923", NUM), ("thirty", EN), ("a hundred", EN), ("a thousand", EN)],
    "bt_memodemand": [("about |a", EN)],
    "bt_memohope": [("half", "half")],
    "bt_nov1": [("1", NUM), ("1923", NUM), ("130", NUM), ("twenty-four", EN)],
    "bt_occupied": [("two millions", EN)],
    "bt_wages": [("three", EN)],
    "bt_onegold": [("one", EN)],
    "bt_oldcirculation": [("93", NUM), ("400", NUM), ("496", NUM), ("690", NUM), ("927", NUM), ("1,211", NUM)],
    "bt_newcirculation": [("501", NUM), ("1,049", NUM), ("1,760", NUM), ("1,803", NUM)],
    "bt_emergency": [("1923", NUM), ("two thousand", EN)],
    "bt_tenfold15": [("ten", EN), ("1 5th", "gap"), ("1923", NUM)],
    "bt_limit24": [("2,400", NUM), ("r,2oo", "ocr")],
    "bt_credits": [("364", NUM), ("600", NUM), ("1,102", NUM), ("1,482", NUM)],
    "bt_debtannul": [("58-5", "dash")],
    "bt_receipts": [("14*5", "star"), ("1923", NUM)],
    "bt_receipts2": [("14*5", "star"), ("1923", NUM), ("63*2", "star"), ("312*3", "star"), ("1923", NUM),
                     ("503*5", "star"), ("1924", NUM)],
    "bt_borrow1560": [("1923", NUM), ("1,560", NUM), ("1924", NUM), ("1*9", "star")],
    "bt_lottery": [("thirty", EN), ("1926", NUM), ("five", EN), ("12 1", "ocr")],
    "bt_rentenwithdraw": [("30", NUM), ("1924", NUM), ("ten", EN), ("2,070", NUM)],
    "bt_reichsmark24": [("30", NUM), ("1924", NUM), ("a thousand", EN)],
    "bt_law1924": [("30", NUM), ("1924", NUM), ("nth", "ocr"), ("1924", NUM), ("1", NUM)],
    "bt_unemployed": [("1", NUM), ("1923", NUM), ("249,192", NUM), ("15", NUM), ("696,922", NUM), ("15", NUM),
                      ("1,265,218", NUM), ("15", NUM), ("1485,014", "ocr")],
    "k29_two": [("two", EN)],
    "k29_borrow": [("two", EN), ("three", EN)],
    "k29_three": [("three", EN)],
    "s_three": [("three", EN)],
    "s_ausaug": [("1922", NUM), ("three", EN), ("2", NUM), ("1922", NUM)],
    "law_capital": [("3.200", "de")],
    "law_credit": [("1.200", "de")],
    "law_private": [("1.200", "de")],
    "ndb_havenstein_life": [("10.3.1857", "dmy"), ("20.11.1923", "dmy")],
    "ndb_havenstein_office": [("1908-23", "range")],
    "ndb_havenstein_blame": [("1918-23", "range")],
    "ndb_schacht_life": [("22.1.1877", "dmy"), ("3.6.1970", "dmy")],
    "ndb_schacht_1923": [("12.11.1923", "dmy"), ("22", NUM)],
    "ndb_rathenau_life": [("29.9.1867", "dmy"), ("24.6.1922", "dmy")],
    "ndb_helfferich_life": [("22.7.1872", "dmy"), ("23.4.1924", "dmy")],
    "ndb_helfferich_1915": [("31.1.1915", "dmy")],
    "ndb_luther_6oct": [("6.10.1923", "dmy")],
    "ndb_luther_combined": [("15.10.1923", "dmy")],
    "ndb_luther_15oct": [("13.10.1923", "dmy"), ("15.10.1923", "dmy")],
    "ndb_luther_backing": [("3,2", "decomma")],
    "ndb_luther_gold": [("30.8.1924", "dmy")],
    "ndb_luther_rate": [("einer", "deword"), ("eine", "deword")],
}


def check_readings(df: pd.DataFrame) -> None:
    n = 0
    for r in df.itertuples():
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
            got = [figure(x) for x in FIGURES.findall(q)]
        assert [round(g, 9) for g in got] == [round(v, 9) for v in vals], f"{r.id}: read {got}, value column {vals}"
        n += 1
    quoted("rows with values, each read from its quotation", n, 184)
    N = column("note")
    for rid, word in [("bt_limit24", "r,2oo"), ("bt_law1924", "nth"), ("bt_unemployed", "1485,014"),
                      ("bt_goldmark", "41 1"), ("bt_tenfold15", "1 5th"), ("bt_debtannul", "58-5"),
                      ("bt_1920counter", "176*6"), ("bt_receipts", "14*5"), ("bt_borrow1560", "1*9"),
                      ("bt_lottery", "12 1")]:
        assert word in N[rid], (rid, word)                 # every misprint is named in the note


# ---------------------------------------------------------------------------------------------------
# 2. Every “…” of the text against the snapshot
ALLOW: set[str] = set()                    # quotation marks that quote no source (none in this chapter)
# the chapter's Chinese renderings of the quotations: rendering -> row (or rows)
TRANSLATIONS = {
    # opening
    "主犯": "ndb_havenstein_blame",
    "突然停止上涨，马克也停止贬值": "s_stopped",
    # sec:weimar-transfer
    "一开始对德国期望的数额，比它最后付得出的多得多。": "s_reparationuncertainty",
    "德国的全部义务有多大、要按什么时间表付款，很长时间里都不确定，一直在谈判": "s_reparationuncertainty",
    "以 100 亿美元了结全部赔款，不再逐项审查": "k19_settle",
    "德国劳动每年能为国内资本改良生产的剩余，无论在理论上还是在实际上，都不是它每年能向国外缴纳多少贡赋的尺度。":
        "k19_investexport",
    "财政筹措问题取决于德国人民的财富与繁荣，转移问题取决于德国工业在国际市场上的竞争地位。": "k29_wages",
    "过去两三年，转移问题暂时靠德国在国外借钱解决，借来的钱用于国内的资本用途，并没有以进口的形式运回国内。": "k29_borrow",
    "要么德国的实业家比别处的实业家更快地提高效率，要么德国的利率比别处低，要么按黄金计的效率工资比别处降低。": "k29_three",
    "转移问题要求降低德国现行的、按黄金计的效率工资，使它相对于别处的效率工资下降": "k29_goldwages",
    "几乎肯定": "o29_wageconcession",
    "看不出有什么理由认为这种反馈会很大": "k29_repercussion",
    "有组织的实物交付能克服我所顾虑的困难": "k29_inkind",
    # sec:weimar-fiscal
    "直接向罢工的工人付钱，钱靠向帝国银行贴现国库券筹来": "s_ruhrpayments",
    "几乎 100\\% 的支出靠发钞来支付": "s_virtually100",
    "一个政府可以活很久，即使是德国政府或俄国政府": "tr_live",
    "公众最难逃避的一种税，最软弱的政府在别的什么都征不上来的时候，也征得上来": "tr_hardest",
    "等于对所有持钞人按持有量征了 25\\% 的税": "tr_tax25",
    # sec:weimar-demand
    "狂热地抢购外汇": "bt_feverish",
    "每小时都在贬值的钱": "bt_deserted",
    "唯恐手里的钱太多，连实际上必需的最低数量也没有备足": "tr_scarcity",
    "减少柜台里和口袋里留的钱，缩短留钱的平均时间，哪怕个人很不方便": "tr_remedies",
    "以为涨价一定是暂时的，往往把钱囤起来、推迟购买，结果以货币形式持有的实际价值比以前还多": "tr_wrongway",
    "同一个父母的孩子": "bt_helfferichparent",
    "所谓的通胀": "bt_havensteinabroad",
    "3 月 28 日，对外汇市场的进攻开始了。": "bt_attack",
    "似乎支持": "bt_admit",
    # sec:weimar-test
    "重估": "bt_marketgap",
    # sec:weimar-stabilization
    "黑麦马克": "ndb_helfferich_rye",
    "地租银行一开始发行地租银行券，帝国银行就不得再贴现国库券。": "law_stop",
    "在各公共收款处都要作为支付手段收下": "law_taxes",
    "盖房子，从屋顶盖起": "bt_lutherroof",
    "跳过一道深谷，对岸被云遮住了": "bt_ravine",
    "价值稳定": "bt_constantvalue",
    "清楚表明，它要履行义务，把政府借款限制在法令规定的数额以内": "s_tested",
    "首要的、根本的": "bt_limitation",
    "地租马克的奇迹": "bt_miracle",
    "马克的救星": "ndb_schacht_myth",
    "只是一项装点门面的措施": "s_cosmetic",
    "赔款暂时停付，道威斯计划给德国定了一份容易应付得多的付款时间表": "s_dawes",
    "三件事同时而且突然地发生了：政府不再向中央银行追加借款，预算转为平衡，通胀停止": "s_three",
    # sec:weimar-cost
    "实际上等于政府给借款人的转移支付": "s_commercial",
    "接近负 100\\%": "f30_germany",
}
# the words of the source that each rendering renders
KEYWORDS = {
    "ndb_havenstein_blame": ["Hauptschuldiger an der Inflation", "Meinungen geteilt"],
    "s_stopped": ["prices suddenly stopped rising and the mark stopped depreciating"],
    "s_reparationuncertainty": ["considerably larger sums were initially expected of Germany",
                                "than it ever was eventually able to pay",
                                "the extent of Germany's total obligation and the required schedule of payments",
                                "for a long time uncertain and under negotiation"],
    "k29_wages": ["The Budgetary Problem depends on the wealth and prosperity of the German people",
                  "on the competitive position of her industries on the international market"],
    "k29_three": ["Either German industrialists must increase their efficiency faster than industrialists elsewhere",
                  "or the rate of interest in Germany must be lower than elsewhere",
                  "or the gold-rates of efficiency-wages must be reduced compared with elsewhere"],
    "k29_inkind": ["Organised deliveries in kind would get over the difficulties I have in view",
                   "practical obstacles"],
    "s_ruhrpayments": ["making direct payments to striking workers",
                       "financed by discounting treasury bills with the Reichsbank"],
    "bt_feverish": ["feverish purchases of foreign exchange"],
    "tr_remedies": ["reduce the amount of till-money and pocket-money that they keep",
                    "the average length of time for which they keep it",
                    "even at the cost of great personal inconvenience"],
    "tr_wrongway": ["believing that the rise must be temporary",
                    "they tend to hoard their money and to postpone purchases",
                    "they hold in monetary form a larger aggregate of real value than before"],
    "law_taxes": ["an den öffentlichen Kassen als Zahlungsmittel anzunehmen"],
    "s_dawes": ["Reparations payments were temporarily suspended",
                "the Dawes plan assigned Germany a much more manageable schedule of payments"],
    "k19_settle": ["$10,000,000,000 in final settlement", "without further examination of particulars"],
    "k19_investexport": ["The annual surplus which German labor can produce for capital improvements at home",
                         "either theoretically or practically", "the annual tribute which she can pay abroad"],
    "k29_borrow": ["For the last two or three years", "temporarily solved by Germany borrowing abroad",
                   "for capital purposes at home", "does not bring home in the shape of imports"],
    "k29_goldwages": ["requires a reduction in the present gold-rates of efficiency-wages in Germany",
                      "relatively to efficiency-wages elsewhere"],
    "o29_wageconcession": ["almost certainly", "deflate wages and prices to some extent"],
    "k29_repercussion": ["I see no reason to suppose that this repercussion would be large"],
    "s_virtually100": ["virtually 100% of its expenditures by means of note issue"],
    "tr_live": ["A Government can live for a long time, even the German Government or the Russian Government"],
    "tr_hardest": ["the form of taxation which the public find hardest to evade",
                   "even the weakest Government can enforce, when it can enforce nothing else"],
    "tr_tax25": ["a tax of 25 per cent on all holders of notes in proportion to their holdings"],
    "bt_deserted": ["a money which depreciated from hour to hour"],
    "tr_scarcity": ["in their anxiety not to hold too much money",
                    "fail to provide themselves even with the minimum which they will require in practice"],
    "bt_helfferichparent": ["children of the same parent"],
    "bt_havensteinabroad": ["“so-called inflation,”", "had always come from abroad"],
    "bt_attack": ["On the 28th March began the attack on the foreign exchange market."],
    "bt_admit": ["seem to give support to those who deny that the inflation was at the root of the matter"],
    "bt_marketgap": ["“revaluation”"],
    "ndb_helfferich_rye": ["„Roggenmark“", "durch Roggen"],
    "law_stop": ["Sobald die Deutsche Rentenbank mit der Ausgabe von Rentenbankscheinen begonnen hat",
                 "dürfen bei der Reichsbank Schatzanweisungen nicht mehr diskontiert werden"],
    "bt_lutherroof": ["“who builds a house, beginning with the roof.”"],
    "bt_ravine": ["“leap over a ravine the other edge of which was obscured by clouds.”"],
    "bt_constantvalue": ["‘constant value’"],
    "s_tested": ["effectively made clear its intent to meet its obligation",
                 "to limit government borrowing to within the amount decreed"],
    "bt_limitation": ["of primary and fundamental importance"],
    "bt_miracle": ["“The miracle of the rentenmark” became a common expression."],
    "ndb_schacht_myth": ["seinen eigenen Mythos", "„Retter der Mark“"],
    "s_cosmetic": ["only a cosmetic measure"],
    "s_three": ["Simultaneously and abruptly three things happened",
                "additional government borrowing from the central bank stopped",
                "the government budget swung into balance, and inflation stopped"],
    "s_commercial": ["amounted virtually to government transfer payments to the recipients of the loans"],
    "f30_germany": ["nearly minus 100 per cent in Germany"],
}


def tex_text() -> str:
    return "\n".join(l for l in TEX.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("%"))


def say(*phrases: str) -> None:
    """The phrases are in the text (the numbers of a check are the numbers the text prints)."""
    t = tex_text()
    for s in phrases:
        assert s in t, f"not in the text: {s!r}"


UNITS = {"万亿": 10 ** 12, "亿": 10 ** 8, "万": 10 ** 4}
AMOUNT = re.compile(r"(\d[\d,]*(?:\.\d+)?)(?:\s*多?(万亿|亿|万))?")      # '6,000 多万': more than 6,000 万


def said(phrase: str, *values: float | None, slack: float = 0.0) -> None:
    """The phrase is in the text, and each number it prints (with its unit 万, 亿, 万亿) is the value given, within
    half a unit of its last digit (plus `slack`, in the same units). None skips a number (a year told elsewhere)."""
    say(phrase)
    found = AMOUNT.findall(phrase)
    assert len(found) == len(values), f"{phrase!r}: {len(found)} numbers, {len(values)} values"
    for (digits, unit), v in zip(found, values):
        if v is None:
            continue
        scale = UNITS.get(unit, 1)
        decimals = len(digits.split(".")[1]) if "." in digits else 0
        tol = (0.5 * 10 ** -decimals + slack) * scale
        quoted(f"{phrase!r}: {digits}{unit}", float(v), figure(digits) * scale, tol=tol + 1e-9 * scale)


ZH_DIGITS = {"一": 1, "两": 2, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
ZH_UNITS = {"十": 10, "百": 100, "千": 1000, "万": 10 ** 4}


def zh(s: str) -> float:
    """A Chinese numeral of the text: '八分之一', '四十分之一', '三', '十', '二十', '两千', '六成', '一倍半'."""
    if "分之" in s:
        b, a = s.split("分之")
        return zh(a) / zh(b)
    if s.endswith("成"):
        return zh(s[:-1]) / 10
    if s.endswith("倍半"):
        return zh(s[:-2]) + 0.5
    total, part = 0, 0
    for ch in s:
        if ch in ZH_DIGITS:
            part = ZH_DIGITS[ch]
        else:
            unit = ZH_UNITS[ch]
            total += max(part, 1) * unit
            part = 0
    return float(total + part)


def text_quotations() -> list[str]:
    return re.findall(r"“([^”]*)”", tex_text())


def check_text(df: pd.DataFrame) -> None:
    ids = set(df["id"])
    Q = quotes()
    used, n = set(), 0
    for q in text_quotations():
        n += 1
        used.add(q)
        if q in ALLOW:
            continue
        assert q in TRANSLATIONS, f"not listed: “{q}”"
        t = TRANSLATIONS[q]
        for rid in (t,) if isinstance(t, str) else t:
            assert rid in ids, rid
            assert rid in KEYWORDS, f"{rid}: no KEYWORDS"
            if q.isascii():
                assert q in Q[rid], (q, rid)
    stale = (set(ALLOW) | set(TRANSLATIONS)) - used
    assert not stale, f"listed but not in the text: {sorted(stale)}"
    for rid, words in KEYWORDS.items():
        for w in words:
            assert w in Q[rid], f"{rid}: {w!r} not in the quotation"
    assert set(KEYWORDS) == {r for t in TRANSLATIONS.values() for r in ((t,) if isinstance(t, str) else t)}
    print(f"ok {n} quotations of the text found in the snapshot (or listed as exceptions)")


# ---------------------------------------------------------------------------------------------------
# 3. Numbers, section by section
T12, B9, M8 = 10 ** 12, 10 ** 9, 10 ** 6       # a trillion (American, 万亿), a milliard, a million


def guide(F, Y):
    t = TEX.read_text(encoding="utf-8")
    assert f"\\guidequestion{{{GUIDE}}}" in t
    assert GUIDE in (ROOT / "zh" / "ch25_wicksell.tex").read_text(encoding="utf-8")       # 第 25 章交来的问题
    said("1922—1923 年物价为什么越涨越快", 1922, 1923)
    said("1923—1924 年的稳定", 1923, 1924)


def opening(F, Y, Q):
    d, y, usd, gm = F["bt_stablelevel"]
    said("1923 年 11 月 20 日，柏林交易所把美元的官价定在 4.2 万亿纸马克", y, 11, d, usd * B9)
    chk("    the same rate in the table of p. 24", F["bt_berlin20"], [d, y, usd])
    assert "November 20th" in Q["bt_stablelevel"] and "for a dollar" in Q["bt_stablelevel"]
    chk("    one gold mark in paper marks: 'a trillion' (一万亿)", gm * B9, zh("一") * T12)
    say("从这天起，一万亿纸马克合一个战前的金马克")
    chk("five days before: the issue of 15 November", d - F["arch_issue"][0], zh("五"))
    say("五天前，地租银行开始发行一种新钱")
    chk("    one rentenmark = one gold mark", F["bt_onegold"], [zh("一")])
    say("一地租马克也值一金马克")
    said("4.2 万亿去掉 12 个零，正是", usd * B9, math.log10(T12))
    pct("    4.2 x 10^12 / 10^12 = the pre-war parity", usd * B9 / T12, 100 / F["s_g4unit"][0], 1)
    pct("    the pre-war parity: 100 / 23.82 cents (marks per dollar)", 100 / F["s_g4unit"][0], 4.20, 2)
    said("正是战前一美元换 4.20 马克的老比价", 100 / F["s_g4unit"][0])
    # Havenstein
    _, _, born, dd2, mm2, died = F["ndb_havenstein_life"]
    chk("Havenstein died on 20 November 1923, the day of the rate", [dd2, mm2, died], [d, 11, y])
    assert "Berlin" in Q["ndb_havenstein_life"] and "Reichsbankpräsident" in Q["ndb_havenstein_life"]
    said("帝国银行行长哈芬施坦（Rudolf Havenstein，1857—1923）在柏林去世", born, died)
    said("他从 1908 年起执掌帝国银行", F["ndb_havenstein_office"][0])
    assert F["ndb_havenstein_office"][1] == died
    said("1918—1923 年这场通胀的“主犯”", *F["ndb_havenstein_blame"])
    # Cologne and the days of November
    cologne, cd = F["bt_cologne20"]
    said("一美元要 11.7 万亿纸马克", cologne * B9)
    chk("    Cologne / Berlin on 20 November", cd, d)
    r = cologne / usd
    assert r < 3, r                                                                    # 差不多（稍少于）三倍
    phrase = "差不多是柏林的三倍"
    say(phrase)
    pct("    almost three times Berlin (the numeral read from the phrase)", r, zh(phrase[-2]), 0)
    said("11 月 13 日一美元合 8,400 亿纸马克，14 日是 1.26 万亿，15 日是 2.52 万亿", 11, F["bt_berlin13"][0],
         F["bt_berlin13"][2] * B9, F["bt_berlin14"][0], F["bt_berlin14"][2] * B9, F["bt_berlin15"][0],
         F["bt_berlin15"][2] * B9)
    chk("    one day, the 14th to the 15th: the dollar doubled", F["bt_berlin15"][2] / F["bt_berlin14"][2], 2)
    say("一天之内，美元的价钱翻了一倍")
    assert "late November 1923" in Q["s_stopped"]
    say("可是到了 11 月下旬")
    # the question
    x = ratio("1923-10")
    said("1923 年 10 月是 9 月的 296 倍", 1923, 10, 9, x)
    assert doubling(x) < 4
    say("物价不到四天就翻一番")
    chk("Cagan's threshold: 50% a month (two witnesses)", [F["fsv_cagan"][0], F["ko_cagandef"][0]], [50, 50])
    said("把物价每月上涨 50\\% 以上的时期叫作", F["fsv_cagan"][0])
    g = F["fsv_seven"]
    assert "Germany, August 1922–November 1923" in Q["fsv_seven"]
    said("德国的恶性通胀从 1922 年 8 月算到 1923 年 11 月", g[4], 8, g[5], 11)


def world(F, Y, Q):
    dd, y, dd2, back = F["bt_stopgold"]
    said("1914 年 7 月 31 日下午", y, 7, dd)
    assert "July 31st, 1914" in Q["bt_stopgold"] and "August 4th" in Q["bt_stopgold"]
    said("8 月 4 日的法律追认了停兑", 8, dd2)
    assert "afternoon" in Q["bt_stopgold"] and back == dd
    # Helfferich
    a = F["ndb_helfferich_life"]
    chk("Helfferich 1872-1924 (NDB and DNB)", [a[2], a[5]], F["helfferich_life"])
    said("1915 年 1 月 31 日，他出任帝国财政部的国务秘书", *F["ndb_helfferich_1915"][::-1])
    assert "Großbritannien" in Q["ndb_helfferich_loans"] and "Anleihen" in Q["ndb_helfferich_loans"]
    loans, share, y0, y1 = F["bt_warloans"]
    said("战争公债的认购额约有 980 亿马克", loans * B9)
    chk("    scarcely one-eighth (不到八分之一)", share, zh("八分之一"))
    said("1914—1918 年的开支只有不到八分之一来自普通收入", y0, y1)
    said("从 1916 年秋天起", F["ndb_helfferich_1916"][0])
    assert F["bt_warshort"][0] == F["ndb_helfferich_1916"][0] and "autumn of 1916" in Q["bt_warshort"]
    _, y, nth, debt = F["bt_warshort"]
    said("1918 年 9 月底，第九次战争公债发完以后，短期债务仍有 480 亿马克", y, 9, debt * B9)
    chk("    the ninth war loan (第九次)", nth, zh("九"))
    P = prices_war()
    said("这个指数以 1913 年为 100", 1913, 100)
    said("它从 1914 年 7 月的 99 涨到 1918 年 11 月停战时的 234", 1914, 7, P.wpi_1913_100["1914-07"], 1918, 11,
         P.wpi_1913_100["1918-11"])
    assert 2 < P.wpi_1913_100["1918-11"] / P.wpi_1913_100["1914-07"] < 3                # 涨了一倍多
    said("从 1914 年到 1918 年 10 月，国内物价涨得比货币数量少", *F["bt_warprices"][:1], *F["bt_warprices"][1:], 10)
    assert "October 1918" in Q["bt_warprices"]
    said("1918 年 11 月革命以后的混乱", F["bt_postwar"][0], 11)
    assert "revolution of November 1918" in Q["bt_postwar"]
    assert P.wpi_1913_100["1919-12"] > 3 * P.wpi_1913_100["1918-11"]                    # 1919 年，物价追了上来
    say("1919 年，物价追了上来")
    Q20 = prices().wpi_1913_100
    said("1920 年 2 月，批发物价指数到了 1,690", 1920, 2, Q20["1920-02"])
    r = Q20["1920-02"] / P.wpi_1913_100["1918-11"]
    assert 7 < r < 8, r                                                                # 是停战时的七倍多
    say("是停战时的七倍多")
    said("从 1920 年 2 月到 1921 年 5 月", *F["bt_period2"][:1], 2, F["bt_period2"][1], 5)
    assert "February 1920-May 1921" in Q["bt_period2"] and "improvement of the dollar rate" in Q["bt_period2"]
    d0, d1, n0, n1 = F["bt_1920counter"]
    said("帝国的短期债务从 890 亿马克增加到 1,766 亿", d0 * B9, d1 * B9)
    said("流通的钞票也从 545 亿增加到 817 亿", n0 * M8, n1 * M8)
    assert "fairly constant level" in Q["bt_1920counter"] and "cost of living rose" in Q["bt_1920counter"]
    plateau = Q20["1920-02":"1921-05"]
    assert plateau.max() / plateau.min() < 1.35 and plateau.iloc[-1] < plateau.iloc[0]  # 批发物价却大体稳住
    said("1921 年 5 月，指数是 1,310", 1921, 5, Q20["1921-05"])


def transfer(F, Y, Q):
    said("1921 年 5 月 5 日，赔款委员会按《凡尔赛和约》第 233 条", F["london_date"][1], 5, F["london_date"][0],
         F["london_commission"][0])
    assert "Reparation Commission" in Q["london_commission"]
    said("总额是 1,320 亿金马克", F["london_total"][0] * B9)
    assert "less:" in Q["london_total"]                                               # 再扣除已经付过和应当抵免的部分
    one, _, kg = F["law_goldmark"]
    said("一金马克是 1/2790 千克纯金的价值，合 23.82 美分", one, kg, F["s_g4unit"][0])
    a, b, c = F["london_a"][0], F["london_b"][0], F["london_c82"][0]
    said("A 类 120 亿，B 类 380 亿，C 类 820 亿", a * B9, b * B9, c * B9)
    chk("    A + B + C = the total (milliard gold marks)", a + b + c, F["london_total"][0])
    n1, base, n2, exp1 = F["london_annual"]
    n3, exp2 = F["london_annual2"]
    chk("    the list of Article 4: 1., 2., 3.", [n1, n2, n3], [1, 2, 3])
    said("一笔固定的 20 亿金马克，加上德国出口值的 25\\%，再加上出口值的 1\\%", base * B9, exp1, exp2)
    assert "considerably larger sums were initially expected" in Q["s_reparationuncertainty"]
    # Keynes 1919
    chk("Keynes 1883-1946 (Wikisource)", F["keynes_life"], [1883, 1946])
    dd, y = F["k19_resign"]
    said("到 6 月 7 日为止，他是英国财政部在巴黎和会的正式代表", 6, dd)
    said("早在 1919 年就说这笔账算不下去", y)
    usd = F["k19_settle"][0]
    said("以 100 亿美元了结全部赔款", usd)
    gm = usd / (F["s_g4unit"][0] / 100)
    said("按上面的比价算，100 亿美元约合 420 亿金马克", usd, gm)
    assert gm / (F["london_total"][0] * B9) < 1 / zh("三")                                # 不到伦敦总额的三分之一
    say("不到伦敦总额的三分之一")
    said("比 A、B 两类债券合计的 500 亿也少", (a + b) * B9)
    assert gm < (a + b) * B9                                                            # 比 A、B 两类合计的也少
    # Keynes 1929
    chk("the Economic Journal, 1929", Y["k29_two"], 1929)
    said("1929 年，凯恩斯在《经济学杂志》上撰文，沿用道威斯委员会的划分，把付赔款分成两道关", Y["k29_two"])
    assert Q["k29_two"].startswith("THE Dawes Committee divided the problem")          # 划分出自道威斯委员会
    said("讨论的是 1924 年道威斯计划重新安排的赔款", F["ndb_luther_gold"][2])
    assert "Dawes-Plans" in Q["ndb_luther_gold"] and "Dawes plan" in Q["s_dawes"]
    chk("    two parts (两道关)", F["k29_two"], [zh("两")])
    chk("    'two or three years' (两三年)", F["k29_borrow"], [zh("两"), zh("三")])
    p, v, v2, v3 = F["k29_demand"]
    said("价格降低 10\\%，销量增加 20\\%。出口值并不随之增加 20\\%，只增加 8\\%", p, v, v2, v3)
    pct("    (1 - 10%)(1 + 20%) - 1 (%)", 100 * ((1 - p / 100) * (1 + v / 100) - 1), v3, 0)
    chk("    three ways (三条路)", F["k29_three"], [zh("三")])
    say("降低德国按黄金计的成本有三条路")
    # Ohlin
    _, born, _, died = F["ohlin_life"]
    said("俄林（Bertil Ohlin，1899—1979）那年三十岁", born, died)
    chk("    thirty in 1929 (born in April, the article in June)", Y["o29_imports"] - born, zh("三十"))
    m, direct = F["o29_direct"]
    said("一国每年借入 1 亿马克，由此直接引起的进口超额可能是 2,000 万马克", m * M8, direct * M8)
    T = 1e8
    said("设德国每年向外国转移 1 亿金马克的购买力", T)
    said("再设德国人少花的钱有 20\\% 原本用于进口，收款国多花的钱也有 20\\% 用于买德国货", 100 * SHARE, 100 * SHARE)
    chk("    the teaching share equals Ohlin's 20 of 100", SHARE, direct / m)
    said("德国进口减少 2,000 万，出口增加 2,000 万，贸易余额直接改善 4,000 万金马克", SHARE * T, SHARE * T, 2 * SHARE * T)
    said("还差 6,000 万", T * (1 - 2 * SHARE))
    said("这个算术证明不了最后一定能补上 6,000 万", T * (1 - 2 * SHARE))
    assert "Dawes annuities" in Q["o29_concession"] and "protection" in Q["o29_concession"]
    assert "home market industries" in Q["o29_wageconcession"]
    # Rathenau
    a = F["ndb_rathenau_life"]
    said("拉特瑙（Walther Rathenau，1867—1922）是工业家，1921 年 5 月入阁任重建部长", a[2], a[5], F["ndb_rathenau_1921"][0], 5)
    assert "im Mai 1921" in Q["ndb_rathenau_1921"] and "Industrieller" in Q["ndb_rathenau_life"]
    assert "Wiesbadener Abkommen" in Q["ndb_rathenau_1921"] and "Sachlieferungen" in Q["ndb_rathenau_1921"]


def fiscal(F, Y, Q):
    said("1922 年 12 月，赔款委员会认定德国拖欠了对法国的赔款", F["chron_default"][0], 12)
    dd, y = F["chron_ruhr"]
    said("1923 年 1 月 11 日，法国与比利时又派军队开进鲁尔区", y, 1, dd)
    assert "Januar 1923" in Q["chron_ruhr"]
    assert all(w in Q["bt_ruhr"] for w in ("tax on coal", "export duties", "custom-house dues", "railway receipts"))
    y, sep, _, _ = F["bt_borrow1560"]
    said("1923 年 9 月，帝国靠贴现国库券借了 15.6 亿金马克", y, 9, sep * M8)
    assert "September 1923" in Q["bt_borrow1560"]
    oct_, y = F["bt_receipts"]
    said("10 月，它的普通收入只剩 1,450 万金马克", 10, oct_ * M8)
    said("几乎 100\\% 的支出靠发钞来支付", F["s_virtually100"][0])
    chk("Keynes's Tract, 1923", Y["tr_live"], 1923)
    said("凯恩斯 1923 年写道", Y["tr_live"])
    # ex:weimar-seigniorage
    n0, v0 = F["tr_notes"]
    add, n1 = F["tr_print"]
    each0, each1 = F["tr_each"]
    said("流通中有 900 万张钞票，合计值 3,600 万金美元", n0, v0)
    said("政府再印 300 万张，钞票变成 1,200 万张", add, n1)
    chk("    the notes add up", n0 + add, n1)
    said("设公众持有的实际价值仍是 3,600 万金美元", v0)
    said("每张从 4 美元降到 3 美元", v0 / n0, v0 / n1)
    chk("    $4 and $3 (Keynes)", [v0 / n0, v0 / n1], [each0, each1])
    gain = add * each1
    said("新印的 300 万张值 900 万美元", add, gain)
    chk("    = Keynes's $9,000,000", gain, F["tr_gain"][0])
    said("原有的 900 万张从 3,600 万美元降到 2,700 万美元", n0, v0, n0 * each1)
    S, dh, tax = seigniorage(n0, 1 / each0, n1, 1 / each1)
    chk("    eq:weimar-budget in gold dollars: seigniorage, delta h, inflation tax", [S, dh, tax], [gain, 0, gain],
        tol=1e-6)
    pi = each0 / each1 - 1
    chk("    pi = 4/3 - 1 = 1/3", pi, 1 / 3)
    say("$\\pi=4/3-1=1/3$，$\\Delta h=0$，通胀税为$\\frac{1/3}{1+1/3}\\times3600=\\frac14\\times3600=900$万，税率 25\\%")
    chk("    the tax rate (%) = Keynes's 25 per cent", 100 * pi / (1 + pi), F["tr_tax25"][0])
    add2 = F["tr_further4"][0]
    n2, each2, _ = F["tr_again"]
    said("（3）共 1,600 万张，每张值 2.25 美元", 3, n1 + add2, v0 / n2)
    chk("    the notes, 16,000,000 (Keynes)", n1 + add2, n2)
    chk("    $2.25 (Keynes)", v0 / n2, each2)
    said("政府又得到 900 万美元，税率仍是$1-2.25/3=25\\%$", add2 * each2, 1, each2, each1, 100 * (1 - each2 / each1))
    v20, v36 = F["tr_economise"]
    chk("    $36,000,000 again", v36, v0)
    said("若公众把持有的实际价值压到 2,000 万金美元，政府要再取得 900 万", v20, gain)
    rate = gain / v20
    said("税率要有$900/2000=45\\%$", gain / 1e4, v20 / 1e4, 100 * rate)
    pi2 = rate / (1 - rate)
    said("由$\\pi/(1+\\pi)=0.45$得$\\pi\\approx0.82$，物价要涨约 82\\%", 1, rate, pi2, 100 * pi2)
    # the tax lag
    y, days = F["bt_wagetax"]
    said("1923 年夏天马克跌得飞快", y)
    chk("    about a fortnight (两个星期左右)", days, 2 * 7)
    say("工资税却平均要在雇主手里留两个星期左右")
    said("到 1923 年 10 月，政府才规定拖欠的税款", F["bt_valorize"][0], 10)
    assert "October nth, 1923" in Q["bt_valorize"]
    said("12 月 19 日的命令，才让整个税制改用金马克", 12, F["bt_finaltax"][0])
    # ex:weimar-taxlag
    aug = ratio("1923-08")
    said("1923 年 8 月的批发物价指数是 7 月的 12.6 倍", 1923, 8, 7, aug)
    said("设一个月里物价每天按同样的比例上涨，一个月按 30 天算。一笔税在纳税义务发生时值 100 篮商品", MONTH, 100)
    said("一笔税在纳税义务发生时值 100 篮商品", 100)
    chk("    two weeks (两周)", LAG, zh("两") * 7)
    say("两周后才缴进国库")
    f = 12.6 ** (LAG / MONTH)
    said("（1）两周里物价涨到$12.6^{14/30}\\approx3.26$倍，税款只能买$100/3.26\\approx31$篮", 1, 12.6, LAG, MONTH, f, 100,
         f, 100 / f)
    chk("    with the index itself: the same 31 baskets", round(100 / aug ** (LAG / MONTH)), 31)
    assert 1 - (100 / f) / 100 > 2 / 3                                                 # 三分之二以上在路上没了
    say("三分之二以上在路上没了")
    oct_ = ratio("1923-10")
    said("（2）按 10 月的速度（是 9 月的 296 倍）呢", 2, 10, 9, oct_)
    g = 296 ** (LAG / MONTH)
    said("（2）$296^{14/30}\\approx14.2$倍，只剩约 7 篮", 2, 296, LAG, MONTH, g, 100 / g)
    chk("    with the index itself: about 7 baskets", round(100 / oct_ ** (LAG / MONTH)), 7)
    # the feedback since 1922
    y, _, sep, nov = F["bt_fiscalfeedback"]
    said("这个循环在 1922 年夏天就转起来了", y)
    assert "after July 1922" in Q["bt_fiscalfeedback"]
    said("7 月以后，马克的贬值又把财政打乱了", 7)
    said("帝国的收入那年 9 月已不到 1 亿金马克，11 月只剩 6,000 多万", 9, sep * M8, 11, nov * M8)
    assert "In September of that year" in Q["bt_fiscalfeedback"]                     # 那年: 1922
    assert "less than 100 millions" in Q["bt_fiscalfeedback"]
    assert "little more than 60 millions" in Q["bt_fiscalfeedback"]


def demand(F, Y, Q):
    assert "Ende Jan. 1922" in Q["ndb_rathenau_fm"]
    a = F["ndb_rathenau_life"]
    said("那年 1 月底，拉特瑙当上外交部长，6 月 24 日在柏林遇刺身亡", 1, a[4], a[3])
    assert "(ermordet)" in Q["ndb_rathenau_life"] and "1922" in Q["ndb_rathenau_fm"]
    assert "assassination of Rathenau" in Q["bt_rathenau"] and "summer of 1922" in Q["bt_feverish"]
    said("转折发生在 1922 年夏天", F["bt_feverish"][0])
    said("批发物价 7 月涨了约 45\\%，8 月涨了 89\\%", 7, 100 * (ratio("1922-07") - 1), 8, 100 * (ratio("1922-08") - 1))
    said("德国的恶性通胀，就从这个 8 月算起", 8)
    # the compare box
    _, _, h0, h1 = F["fsv_ranges"]
    said("每年涨 50\\%—100\\% 算高通胀，超过 100\\% 算很高", h0, h1, F["fsv_veryhigh"][0])
    assert h1 == F["fsv_veryhigh"][0] and '"high" (for the 50-100 percent range)' in Q["fsv_ranges"]
    assert "no agreed convention" in Q["fsv_convention"]
    say("每月涨 50\\% 以上\\cite{cagan1956}，一年就是约 130 倍")
    said("每月涨 50\\% 以上", F["fsv_cagan"][0])
    said("一年就是约 130 倍", (1 + F["fsv_cagan"][0] / 100) ** 12, slack=1)
    g = F["fsv_seven"]
    said("1922 年 8 月到 1923 年 11 月，共 16 个月", g[4], 8, g[5], 11, months_between("1922-08", "1923-11"))
    assert "Cagan seven" in Q["fsv_ten"]
    said("卡甘研究的七次恶性通胀，没有一次短于 10 个月", F["fsv_ten"][0])
    chk("    the seven (七次): Cagan's list", zh("七"), 7)
    # scenes
    said("1922 年夏天，主要的行业一个接一个改用美元、瑞士法郎、荷兰盾或金马克报价", F["bt_payments"][0])
    assert all(w in Q["bt_payments"] for w in ("dollars", "Swiss francs", "Dutch florins", "gold marks"))
    said("1923 年夏天，工资先在星期二预付一部分", Y["bt_wages"])
    assert "Tuesday" in Q["bt_wages"] and "Friday" in Q["bt_wages"] and "or even daily" in Q["bt_wages"]
    chk("    three times a week (一周发三次)", F["bt_wages"], [zh("三")])
    say("后来有些工厂一周发三次工资，甚至天天发")
    dd, y, rate1, hours = F["bt_nov1"]
    said("1923 年 11 月 1 日，柏林交易所的美元官价是 1,300 亿纸马克，此后 24 小时里卖货都要以它为准", y, 11, dd,
         rate1 * B9, hours)
    rate2, lost = F["bt_nov2"]
    said("11 月 2 日上午，商店照它标好了价钱", 11, F["bt_nov2morning"][0])
    said("店主们沮丧地得知美元已经涨到 3,200 亿", rate2 * B9)
    chk("    lost 60 per cent (六成)", lost / 100, zh("六成"))
    pct("    1 - 130 / 320 (%)", 100 * (1 - rate1 / rate2), lost, -1)
    say("上午收进的钞票已经失去六成价值")
    said("1923 年夏天钱荒最严重的时候", F["bt_summer1923"][0])
    y, mills, presses, women = F["bt_presses"]
    said("1923 年 10 月底，印钞用的特种纸由 30 家造纸厂生产", y, 10, mills)
    said("约有 100 家私人印刷厂", presses)
    said("1,000 名妇女和女孩专门清点每包钞票的张数", women)
    s0, y0, s1, y1 = F["s_reichsbankstaff"]
    said("从 1922 年底的约 1.3 万人增加到 1923 年底的约 2.3 万人", y0, s0, y1, s1)
    top = F["bt_onesided"][-1]
    said("面额最大的钞票是 100 万亿马克", top * B9)
    assert "These last were the highest issued" in Q["bt_onesided"] and "one side only" in Q["bt_onesided"]
    dd, y, stamped = F["bt_memo"]
    said("1923 年 10 月 25 日，帝国银行在报上发表了一份声明", y, 10, dd)
    supply, need = stamped * T12, F["bt_memodemand"][0] * 10 ** 18          # British billion 10^12, trillion 10^18
    say("面值合计$1.2\\times10^{17}$纸马克，可是当天的需求约为$10^{18}$纸马克")
    chk("    1.2 x 10^17", supply, 1.2e17, rel=1e-12)
    chk("    10^18", need, 1e18, rel=1e-12)
    pct("    about one-eighth of the demand (八分之一左右)", supply / need, zh("八分之一"), 2)
    say("印出来的只有需求的八分之一左右")
    chk("    half the demand (一半)", F["bt_memohope"][0], zh("二分之一"))
    say("把每天的产量提高到需求的一半")
    # Keynes's three ways and the first phase
    chk("Keynes's list: (1), (2), (3)", F["tr_remedies1"] + F["tr_remedies"][:1] + F["tr_remedies"][2:], [1, 2, 3])
    say("凯恩斯列了人们少持有本币的三种办法。一是", "二是“减少柜台里和口袋里留的钱", "三是在许多交易里改用外币")
    assert "durable objects, jewellery" in Q["tr_remedies1"] and "household goods" in Q["tr_remedies"]
    said("1920—1921 年的平台就有这样的味道", *F["bt_period2"])
    # Havenstein and Helfferich
    dd, y = F["bt_havenstein1922"]
    said("1922 年 8 月 28 日，哈芬施坦在帝国银行中央委员会上明确表示", y, 8, dd)
    assert "Central Committee of the Reichsbank" in Q["bt_havenstein1922"] and "moratorium" in Q["bt_havenstein1922"]
    said("1923 年 2 月，它出手支撑马克", F["bt_support"][0], 2)
    assert "February 1923" in Q["bt_support"]
    said("批发物价指数 3 月下降约 17\\%，4 月只涨约 7\\%", 3, -100 * (ratio("1923-03") - 1), 4,
         100 * (ratio("1923-04") - 1))
    said("3 月 28 日，对外汇市场的进攻开始了。", 3, F["bt_attack"][0])
    a, b, dd = F["bt_dam"]
    said("帝国银行每天要卖出约 2,000 万金马克的外汇，需求很快升到 7,000 万。4 月 18 日", a * M8, b * M8, 4, dd)
    s = index_all()
    said("到 6 月，物价已是 4 月的 3.7 倍", 6, 4, s["1923-06"] / s["1923-04"])
    said("那时赔款并没有解决", )
    assert "gar keine andere Lösung möglich" in Q["ndb_havenstein_fear"]               # 大概认定别无出路
    say("不过他大概一心认定，当时的处境下别无出路")
    said("黑尔弗里希自己在 1923 年 9 月提出了新币方案", Y["ndb_helfferich_rye"], 9)
    assert "September 1923" in Q["ndb_helfferich_rye"]
    said("1923 年 11 月停止贴现国库券以后，汇率与物价随即稳住，赔款要到 1924 年才重新安排", 1923, 11, Y["s_dawes"])
    said("1922 年以后，两条因果链咬在一起", 1922)


def test(F, Y, Q):
    y0, y1, p1, n1 = F["s_ratio1"]
    _, _, p2, n2 = F["s_ratio2"]
    said("1922 年 1 月到 1923 年 7 月，批发物价涨到原来的 2,038 倍，帝国银行券只增加到 378 倍", y0, 1, y1, 7, p1, n1)
    said("到 8 月，两者分别是 25,723 倍与 5,748 倍", 8, p2, n2)
    said("银行券的实际余额 7 月只剩 1922 年 1 月的约 19\\%，8 月约 22\\%", 7, y0, 1, 100 * n1 / p1, 8, 100 * n2 / p2)
    for r in (n1 / p1, n2 / p2):
        pct("    about one-fifth (五分之一左右)", r, zh("五分之一"), 1)
    assert 100 <= n1 < 1000 <= n2 < 10000                                             # 几百倍到几千倍
    say("银行券按面值多了几百倍到几千倍，能买的东西却只剩五分之一左右")
    y, gm = F["bt_150"]
    said("1923 年 10 月底，德国发行的全部纸马克只值不到 1.5 亿金马克", y, 10, gm * M8)
    pre = F["tr_prewar"][0]
    said("战前，德国的通货约有 60 亿金马克", pre * B9)
    chk("    one-fortieth (四十分之一)", gm * M8 / (pre * B9), zh("四十分之一"))
    say("前者只是后者的四十分之一")
    y, p, d = F["s_99"]
    say("新钞也几乎淹没了旧钞。按面值算，10 月底流通的帝国银行券")
    said("10 月底流通的帝国银行券，99\\% 以上是此前 30 天里才发出来的", 10, p, d)
    # tab:weimar-doubling and its paragraph
    s = index_all()
    said("6 月要 24 天，8 月要 8 天，10 月不到 4 天", 6, doubling(ratio("1923-06")), 8, doubling(ratio("1923-08")), 10,
         None)
    assert doubling(ratio("1923-10")) < 4
    said("11 月的指数还是 10 月的约 100 倍", 11, 10, ratio("1923-11"), slack=5)
    quoted("    December: only three-quarters more (多四分之三, to a quarter's tenth)", ratio("1923-12") - 1,
           zh("四分之三"), tol=0.025)
    say("12 月就只比 11 月多四分之三")
    rows = [("6 月 & 193.9 万 & 2.37 & 24.1", "1923-06"), ("7 月 & 747.9 万 & 3.86 & 15.4", "1923-07"),
            ("8 月 & 9,440 万 & 12.6 & 8.2", "1923-08"), ("9 月 & 23.9 亿 & 25.4 & 6.4", "1923-09"),
            ("10 月 & 7,095 亿 & 296 & 3.7", "1923-10"), ("11 月 & 72.6 万亿 & 102 & 4.5", "1923-11"),
            ("12 月 & 126.2 万亿 & 1.74 & 37.6", "1923-12")]
    for line, k in rows:
        x = ratio(k)
        said(line, int(k[-2:]), s[k], x, doubling(x))
    said("翻番天数按一个月 30 天", MONTH)
    # ex:weimar-double
    sep, oct_ = s["1923-09"], s["1923-10"]
    say(f"1923 年 9 月的批发物价指数是 {sep:,.0f}，10 月是 {oct_:,.0f}（1913 年$=100$）")
    x = oct_ / sep
    say("$709{,}480{,}000{,}000/2{,}394{,}889{,}300\\approx296.25$倍")
    pct("    the ratio", x, 296.25, 2)
    said("涨幅约 29,525\\%", 100 * (x - 1))
    k = F["ko_germany"][2]
    said("\\chref{ch:intro}引的德国最高月通胀率是 29,525.71\\%", k)
    assert abs(k - 100 * (x - 1)) < 1                                                  # 相差不到 1 个百分点
    said("与这里相差不到 1 个百分点", 1)
    said("令$2^{30/d}=296.25$", 2, MONTH, x)
    said("得$d=30\\ln2/\\ln296.25\\approx3.65$天，约 3.7 天", MONTH, 2, x, doubling(x), doubling(x))
    said("（3）$2^{30}=1{,}073{,}741{,}824$，约 10.7 亿倍，比 296 倍大得多", 3, 2, MONTH, None, None, None, None,
         2 ** 30, x)
    chk("    2^30", 2 ** MONTH, 1073741824)
    r1, r2 = F["bt_nov1"][2], F["bt_nov2"][0]
    said("11 月 1 日柏林的美元官价是 1,300 亿纸马克，2 日下午是 3,200 亿", 11, F["bt_nov1"][0], r1 * B9,
         F["bt_nov2morning"][0], r2 * B9)
    said("$3200/1300\\approx2.46$", r2 * B9 / 1e8, r1 * B9 / 1e8, r2 / r1)
    pct("    an increase of one and a half (一倍半)", r2 / r1 - 1, zh("一倍半"), 0)
    say("一天多就涨了一倍半")
    said("11 月 14 日到 15 日，美元官价也翻了一倍", 11, F["bt_berlin14"][0], F["bt_berlin15"][0])
    # the official rate
    assert "much higher rates" in Q["bt_official"] and "foreign quotations moved bath" in Q["bt_marketgap"]
    said("11 月把美元定在 4.2 万亿纸马克，给马克的价值比国外的报价高", 11, F["bt_marketgap"][0] * B9)
    said("说 1923 年的改革“重估”了纸马克", F["bt_marketgap"][2])
    # the pitfall
    assert gm * M8 / (pre * B9) < 1 / 10                                               # 实际余额缩到了战前的几十分之一
    say("实际余额缩到了战前的几十分之一", "帝国银行 10 月拼命多印")
    said("1923 年的钱荒是真的", 1923)


def stabilization(F, Y, Q):
    said("1923 年 9 月，总理施特雷泽曼（Gustav Stresemann，1878—1929）领导的政府号召结束消极抵抗",
         F["chron_endpassive"][0], 9, F["stresemann_life"][1], F["stresemann_life"][3])
    assert "September 1923" in Q["chron_endpassive"] and "Reichskanzler Stresemann" in Q["chron_endpassive"]
    dd, mm, y = F["ndb_luther_6oct"]
    said("10 月 6 日内阁改组，路德（Hans Luther，1879—1962）接任财政部长", mm, dd, *F["luther_life"])
    said("黑尔弗里希 9 月提议，发行一种用黑麦担保的新币", 9)
    a = F["ndb_luther_15oct"]
    said("10 月 13 日的授权法让政府可以用命令处理财政与经济问题。10 月 15 日", a[1], a[0], a[4], a[3])
    chk("    the decree signed 15 October 1923 by Stresemann and Luther", F["law_signed"], [a[3], a[5]])
    assert "Stresemann" in Q["law_signed"] and "Luther" in Q["law_signed"]
    cap = F["law_capital"][0]
    said("它的资本与基本准备金合计 32 亿地租马克", cap * M8)
    assert Q["law_capital"].startswith("Das Kapital und die Grundrücklage")             # 资本与基本准备金合计
    said("总共抵押了 32 亿金马克", F["ndb_luther_backing"][0] * B9)
    chk("    Sargent: 3.2 billion and 1.2 billion", F["s_limits"], [cap / 1000, F["law_credit"][0] / 1000])
    rm, gm = F["law_convert"]
    said("拿 500 地租马克去换一张面值 500 金马克、有利息的地租债券", rm, gm)
    chk("    the bond of 500 gold marks (§12) and Bresciani-Turroni's 500 for 500", F["law_bond"] + F["bt_convert"],
        [gm, rm, gm])
    said("今后两年，地租银行最多借给政府 12 亿地租马克，年息 6\\%", F["law_credit"][0] * M8, F["law_rate"][0])
    chk("    two years (两年)", F["law_twoyears"], [zh("两")])
    p16, abs2, free = F["law_debt"]
    chk("    counted against §16(2)", [p16, abs2], [16, 2])
    said("其中 3 亿无息", free * M8)
    said("另有 12 亿，可以通过帝国银行和私人发钞银行贷给私人企业", F["law_private"][0] * M8)
    said("最要紧的是第 19 条", int(column("juan")["law_stop"].removeprefix("§")))
    assert column("juan")["law_rollover"] == "§19" and "Prolongationen" in Q["law_rollover"]   # 仍准许展期
    say("已经贴现的国库券，仍准许展期")
    said("这 32 亿与 12 亿，就是", cap * M8, F["law_credit"][0] * M8)
    said("11 月 16 日以前的那几天", 11, F["bt_lutherfood"][0])
    y, kinds = F["bt_emergency"]
    said("据说 1923 年秋天，流通着两千种不同的应急货币", y)
    chk("    two thousand (两千)", kinds, zh("两千"))
    assert Q["bt_emergency"].startswith("It is said")                                 # 据说
    assert "Goldmark lautende Grundschuld" in Q["law_collateral"] and "Rentenmark" in Q["ndb_helfferich_renten"]
    dd, mm, y, dec = F["ndb_schacht_1923"]
    a = F["ndb_schacht_life"]
    said("11 月 12 日，沙赫特（Hjalmar Schacht，1877—1970）被任命为帝国货币专员", mm, dd, a[2], a[5])
    chk("    three days later (三天以后): the issue", F["arch_issue"][0] - dd, zh("三"))
    say("三天以后，地租马克开始发行，柏林的发行点前排起了队")
    assert "Berlin, Nov. 1923" in Q["arch_queue"]
    d, y, usd, gm = F["bt_stablelevel"]
    said("11 月 20 日，纸马克的价值稳定在一美元 4.2 万亿纸马克", 11, d, usd * B9)
    chk("    one gold mark, a trillion paper marks (一万亿)", gm * B9, zh("一") * T12)
    need, red = F["bt_need1200"]
    said("政府需要 12 亿金马克，其中 3 亿用来赎回国库券", need * M8, red * M8)
    chk("    = the decree: 1,200 and 300 million", [need, red], [F["law_credit"][0], free])
    rms, pms = F["bt_indifferent"]
    said("印 12 亿张一地租马克的钞票，与印 12 亿张一万亿纸马克的钞票", rms * M8, rms * M8)
    chk("    1,200 British trillions = 1,200 million x 10^12 paper marks", pms * 10 ** 18, rms * M8 * T12, rel=1e-12)
    ten, dd, _ = F["bt_tenfold15"]
    said("相当于 11 月 15 日流通总额约十倍的纸马克", 11, dd)
    chk("    about ten times (约十倍)", ten, zh("十"))
    said("1923 年 12 月，政府试图突破法令的约束", F["bt_decembertest"][0], 12)
    assert "December 1923" in Q["bt_decembertest"] and "December 1923" in Q["s_tested"]
    said("12 月 22 日，沙赫特接替去世的哈芬施坦", 12, dec)
    assert "nach dem Tode Havensteins" in Q["ndb_schacht_1923"]
    assert "Direktorium und vom Zentralausschuß" in Q["ndb_helfferich_refused"]
    said("反对过 10 月以来的稳定办法", 10)
    assert "seit dem Okt. 1923" in Q["ndb_schacht_myth"]
    say("新旧两种钞票并行，按一万亿比一结算")
    said("信贷与新的金平价要到 1924 年", 1924)
    # tab:weimar-stages
    B = budget().set_index("date")
    y, sep, _, jan = F["bt_borrow1560"]
    said("1923 年 9 月 & 政府号召结束消极抵抗 & 当月靠贴现国库券借了 15.6 亿金马克", y, 9, sep * M8)
    said("10 月 15 日 & 地租银行法令：发行上限 32 亿，政府信贷 12 亿 & 当月普通收入只有 1,450 万金马克", 10, 15, cap * M8,
         F["law_credit"][0] * M8, F["bt_receipts"][0] * M8)
    dd, y, cut = F["s_personnel"]
    said("10 月 27 日 & 人事法令：政府雇员裁减 25\\% & 纸马克的总值不到 1.5 亿金马克", 10, dd, cut, F["bt_150"][1] * M8)
    said("11 月 12 日 & 沙赫特任帝国货币专员 & 次日柏林的美元官价是 8,400 亿纸马克", 11, F["ndb_schacht_1923"][0],
         F["bt_berlin13"][2] * B9)
    chk("    the next day (次日): the 13th", F["bt_berlin13"][0] - F["ndb_schacht_1923"][0], 1)
    said("11 月 15 日 & 地租马克开始发行，帝国银行停止贴现国库券 & 美元官价 2.52 万亿纸马克", 11, F["s_g4stop"][0],
         F["bt_berlin15"][2] * B9)
    said("11 月 20 日 & 美元官价定在 4.2 万亿纸马克 & 科隆的自由市场是 11.7 万亿", 11, d, usd * B9,
         F["bt_cologne20"][0] * B9)
    dec_def = B.revenue_million_goldmark["1923-12"] - B.expenditure_million_goldmark["1923-12"]
    said("12 月 & 地租银行拒绝政府追加借款；19 日起税制改用金马克 & 帝国普通预算仍有 3.3 亿金马克赤字", 12,
         F["bt_finaltax"][0], -dec_def * M8)
    said("12 月 22 日 & 沙赫特任帝国银行行长", 12, F["ndb_schacht_1923"][3])
    said("1924 年 1 月 & 收支自开战以来第一次平衡 & 当月借款只有 190 万金马克", F["bt_balanced"][0], 1, jan * M8)
    said("4 月 7 日 & 帝国银行把贷款总额冻结在 3 月底的水平 & 2—3 月汇率的稳定再度告急", 4, F["bt_april7"][0], 3, 2, 3)
    assert "February and March 1924" in Q["bt_danger"] and "end of March" in Q["bt_april7"]
    said("8 月 30 日 & 货币法定下帝国马克，配合道威斯计划 & 10 月 11 日生效，含金量与旧马克相同", 8,
         F["bt_reichsmark24"][0], 10, F["bt_law1924"][2])
    J = column("juan")
    stage_rows = ["bt_borrow1560", "bt_receipts", "bt_150", "bt_berlin13", "bt_berlin15", "bt_stablelevel",
                  "bt_cologne20", "bt_finaltax", "bt_decembertest", "bt_balanced", "bt_april7", "bt_danger",
                  "bt_reichsmark24", "bt_law1924"]
    pages = {int(J[r].removeprefix("p. ")) for r in stage_rows}
    assert pages <= {24, 73} | set(range(335, 357)) and {24, 73, 335, 356} <= pages, sorted(pages)
    said("Bresciani-Turroni（1937）第 24、73、335—356 页", 1937, 24, 73, 335, 356)
    spages = {int(J[r].split(",")[0].removeprefix("p. ")) for r in ("s_g4stop", "s_tested", "s_personnel")}
    assert spages == {82, 83, 84}, spages
    said("Sargent（1982）第 82—84 页", 1982, 82, 84)
    said("开始发行与停止贴现的日期，不同文本有 15 日与 16 日之别", F["arch_issue"][0], F["bt_stop16"][0])
    # the budget
    rev, exp = B.revenue_million_goldmark["1923-12"], B.expenditure_million_goldmark["1923-12"]
    said("帝国普通预算 1923 年 12 月收入约 3.3 亿，支出约 6.7 亿，赤字仍有 3.3 亿", 1923, 12, rev * M8, exp * M8,
         (exp - rev) * M8)
    assert B.revenue_million_goldmark["1924-01"] > B.expenditure_million_goldmark["1924-01"]
    said("1924 年 1 月，收支自战争爆发以来第一次平衡", F["bt_balanced"][0], 1)
    assert "for the first time since the outbreak of the war" in Q["bt_balanced"]
    said("这个月的借款只有 190 万金马克，1923 年 9 月却是 15.6 亿", jan * M8, 1923, 9, sep * M8)
    feb = B.revenue_million_goldmark["1924-02"] - B.expenditure_million_goldmark["1924-02"]
    said("2 月又出现了 1,780 万的小赤字，3 月以后才月月有盈余", 2, -feb * M8, 3)
    assert all(B.revenue_million_goldmark[k] > B.expenditure_million_goldmark[k] for k in B.index if k >= "1924-03")
    assert "raise taxes and eliminate expenditures" in Q["s_budgetscope"]
    o, y, n, d12, _, j, y3 = F["bt_receipts2"]
    said("税收 1923 年 10 月只有 1,450 万金马克，11 月是 6,320 万", y, 10, o * M8, 11, n * M8)
    said("12 月涨到 3.1 亿，1924 年 1 月是 5.0 亿", 12, d12 * M8, y3, 1, j * M8)
    chk("    = G5's taxes, December and January", [d12, j], list(B.taxes_million_goldmark[["1923-12", "1924-01"]]))
    chk("    October: the ordinary receipts of 14.5 million", o, F["bt_receipts"][0])
    chk("    three tax emergency decrees (三道)", F["ndb_luther_taxes"], [zh("三")])
    say("路德靠三道税收紧急命令增加收入")
    cut, months, base = F["ndb_luther_cuts"]
    chk("    within four months (四个月)", months, zh("四"))
    said("帝国机关在四个月里裁员近 25\\%，冻结升迁，薪水重新定在比 1913 年还低的水平", cut, base)
    assert "fast 25 %" in Q["ndb_luther_cuts"]                                         # 近 25%
    chk("    three things (三件事)", F["s_three"], [zh("三")])
    chk("    the budget a month or two after the rate (一两个月): November to January", months_between("1923-11",
                                                                                                    "1924-01") - 1, 2)
    say("按月看，预算的平衡比汇率与物价晚了一两个月", "预算再晚一两个月")
    # prices in the new unit
    P = prices().wpi_1913_100
    said("1923 年 12 月，批发物价指数是 126.2 万亿（1913 年$=100$）", 1923, 12, P["1923-12"], 1913, 100)
    said("去掉 12 个零就是 126", math.log10(T12), P["1923-12"] / T12)
    pct("    about a quarter above 1913 (约四分之一)", P["1923-12"] / T12 / 100 - 1, zh("四分之一"), 1)
    say("比战前高约四分之一")
    _, bread, _, _ = F["bt_bread"]
    said("11 月底的柏林，一公斤面包要 4,280 亿纸马克，折成新钱还不到半个地租马克", 11, bread * B9)
    assert bread * B9 / T12 < zh("二分之一")
    assert "end of November 1923" in Q["bt_bread"] and "Berlin" in Q["bt_bread"]
    # credit in 1924
    c0, _, _, c3 = F["bt_credits"]
    said("它的短期贷款从 1923 年 11 月底的 3.6 亿金马克，增加到 1924 年 2 月底的 14.8 亿", 1923, 11, c0 * M8, 1924, 2,
         c3 * M8)
    assert "November 30th, 1923, 364" in Q["bt_credits"] and "February 29th, 1,482" in Q["bt_credits"]
    pct("    four times (四倍)", c3 / c0, zh("四"), 0)
    say("涨到四倍")
    said("2 月和 3 月，汇率的稳定又一次告急", 2, 3)
    said("4 月 7 日，帝国银行认定新一轮通胀正在逼近，决定把贷款总额冻结在 3 月底的水平", 4, F["bt_april7"][0], 3)
    dd, y = F["bt_june3"]
    said("6 月 3 日，它才在 1924 年第一次满足了全部贷款申请", 6, dd, y)
    assert "restriktive Kreditpolitik" in Q["ndb_luther_why"] and "Hauptquelle der Inflation" in Q["ndb_luther_why"]
    say("过渡货币能稳住，靠的是两条")
    # the notes after the stabilization
    N = notes().set_index("date")
    o, r = N.old_notes_million_newunit["1923-12"], N.new_rentenmarks_million["1923-12"]
    chk("    the snapshot = Bresciani-Turroni: 31 December", [o, r],
        [F["bt_oldcirculation"][2], F["bt_newcirculation"][1]])
    chk("    31 March and 31 July 1924", [N.old_notes_million_newunit["1924-03"], N.new_rentenmarks_million["1924-03"],
                                         N.old_notes_million_newunit["1924-07"], N.new_rentenmarks_million["1924-07"]],
        [F["bt_oldcirculation"][3], F["bt_newcirculation"][2], F["bt_oldcirculation"][5], F["bt_newcirculation"][3]])
    said("1923 年底，旧纸马克折合约 5.0 亿地租马克，加上 10.5 亿地租马克，共约 15.5 亿", 1923, o * M8, r * M8,
         (o + r) * M8)
    tot = N.old_notes_million_newunit["1924-07"] + N.new_rentenmarks_million["1924-07"]
    said("到 1924 年 7 月底，两者合计约 30 亿", 1924, 7, tot * M8)
    # the Reichsmark
    said("1924 年 8 月 30 日，配合道威斯计划生效", F["ndb_luther_gold"][2], F["ndb_luther_gold"][1],
         F["ndb_luther_gold"][0])
    chk("    30 August 1924 in both", F["bt_reichsmark24"][:2], [F["ndb_luther_gold"][0], F["ndb_luther_gold"][2]])
    _, _, eleven, _, one = F["bt_law1924"]
    said("货币法 10 月 11 日生效，一帝国马克合一万亿纸马克", 10, eleven)
    chk("    a thousand milliard = a trillion (一万亿), and Bresciani-Turroni's '1 billion' (British)",
        [F["bt_reichsmark24"][2] * B9, one * T12], [zh("一") * T12, zh("一") * T12])
    chk("    and the NDB: einer Billion Mark gegen eine Rentenmark", F["ndb_luther_rate"], [1, 1])
    say("一帝国马克合一万亿纸马克，含金量与战前的旧马克相同")
    assert "fine gold content of the reichsmark was the same" in Q["bt_finegold"]
    assert "dollar exchange standard" in Q["bt_dollarstandard"]
    dd, y = F["bt_legaltender"]
    said("旧纸马克到 1925 年 6 月 5 日才不再是法偿货币", y, 6, dd)
    say("德国以帝国马克为新的本位货币，回到了金本位")
    dd, y, ten, out = F["bt_rentenwithdraw"]
    chk("    the liquidation law of the same day (同一天), 30 August 1924", [dd, y], F["bt_reichsmark24"][:2])
    assert "August 30th" in Q["bt_rentenwithdraw"] and "liquidation of the Rentenbank" in Q["bt_rentenwithdraw"]
    chk("    within ten years (十年)", ten, zh("十"))
    said("按同一天的清理地租银行的法律，最迟十年内收回，当时流通的约有 20.7 亿", out * M8)


def cost(F, Y, Q):
    u = F["bt_unemployed"]
    said("1923 年 9 月 1 日约有 25 万人，10 月 15 日约 70 万", u[1], 9, u[0], u[2], 10, u[3], u[4])
    said("11 月 15 日增加到约 127 万，12 月 15 日约 149 万", 11, u[5], u[6], 12, u[7], u[8])
    said("从 9 月 1 日到 11 月 15 日增加了约 100 万", 9, u[0], 11, u[5], u[6] - u[2], slack=5)
    assert 95e4 < u[6] - u[2] < 105e4                                                  # 约 100 万
    say("通胀的最后几个月，失业猛增")
    said("被占领地区的失业工人，估计还有 200 万", F["bt_occupied"][0])
    said("1924 年对德国企业不算好年景，却比 1923 年好得多", *F["s_outputcomparison"])
    gain = u[8] - u[6]
    assert 20e4 < gain < 30e4, gain                                                  # 又添了二十多万
    chk("    twenty (二十)", zh("二十") * 1e4, 2e5)
    say("稳定以后的头一个月又添了二十多万")
    dd, y, cut = F["s_personnel"]
    said("10 月 27 日的人事法令把政府雇员裁减了 25\\%", 10, dd, cut)
    a, y1, b, y2 = F["s_cost"]
    said("1923 年裁掉了 12 万人，1924 年又裁了 6 万人", y1, a, y2, b)
    said("邮政裁减了 6.5 万人", F["s_postal"][0])
    said("薪水定在比 1913 年还低的水平", F["ndb_luther_cuts"][2])
    debt = F["bt_debtannul"][0]
    said("帝国的长期债务有 585 亿金马克（1918 年 3 月底的数）", debt * B9, 1918, 3)
    assert "End of March 1918" in column("note")["bt_debtannul"]
    a, dd, y, rm = F["bt_floating197"]
    said("1923 年 11 月 15 日，帝国的短期债务折成新钱只有 1.97 亿地租马克", y, 11, dd, a * 10 ** 18 / T12)
    chk("    borrowed the same amount (同样数额) from the Rentenbank", rm, a)
    say("政府从地租银行借来同样数额交给帝国银行")
    y, ds, tot, p = F["bt_debtservice"]
    said("1924 年的预算里，公债的利息与还本只有约 1.6 亿金马克，占普通支出约 49.4 亿的 3\\% 多一点", y, ds * M8, tot * M8,
         None)
    assert p < 100 * ds / tot < p + 1                                                  # 3% 多一点
    # the revaluation (重估), Bresciani-Turroni pp. 322-325 and 335
    chk("    the third decree (第三道)", NTH["third"], zh("三"))
    assert "third extraordinary fiscal decree" in Q["bt_debtrevaluation"]
    assert "Dritte" in Q["bt_reval1924"] and "Steuernotverordnung" in column("note")["bt_reval1924"]
    dd, y = F["bt_reval1924"]
    said("1924 年 2 月 14 日的第三道紧急税收命令", y, 2, dd)
    assert "February 14th" in Q["bt_reval1924"]
    said("把工业债券和抵押贷款大约按原来金价值的 15\\% 重估", F["bt_reval15"][0])
    assert "industrial debentures and mortgages" in Q["bt_reval15"]
    dd, y, r25 = F["bt_reval25"]
    said("1925 年 7 月 16 日的法律把抵押贷款的通常重估率提高到 25\\%", y, 7, dd, r25)
    assert "July 16th" in Q["bt_reval25"] and "normal rate of revaluation of mortgages" in Q["bt_reval25"]
    said("本金却要到 1932 年以后才能要求偿付", F["bt_reval1932"][1])
    _, _, dd2, y2, new, old = F["bt_publoan"]
    chk("    the same day (同一天): the law on public loans of 16 July 1925", [dd2, y2], [dd, y])
    assert Q["bt_publoan"].count("July 16th") == 1 and "public loans" in Q["bt_publoan"]
    said("把每 1,000 马克的旧公债换成 25 马克的新债券", old, new)
    dd, y = F["bt_oldholders"]
    said("1920 年 7 月 1 日以前就买进公债的老持有人，另得一份抽签权", y, 7, dd)
    assert "July 1st" in Q["bt_oldholders"] and "lottery right" in Q["bt_oldholders"]
    years30, _, times, share = F["bt_lottery"]
    said("抽签在 30 年里分批进行，中签的债券按新面值的五倍偿还，也就是旧面值的 12.5\\%", years30, share)
    chk("    five times (五倍)", times, zh("五"))
    pct("    5 x 25 / 1,000 (%)", 100 * times * new / old, share, 1)
    # the real rate
    r7, y, r8 = F["bt_discount"]
    said("1922 年 7 月底是 6\\%，8 月底才提到 7\\%", y, 7, r7, 8, r8)
    g7, y, g8 = F["bt_goldmark"]
    said("一金马克从值 160 纸马克涨到值 411 纸马克", g7, g8)
    repay = g7 * (1 + r7 / 100 / 12)
    assert repay / g8 < 0.5                                                            # 不到借钱时的一半
    say("还钱时的购买力不到借钱时的一半")
    said("1923 年，帝国银行又大量贴现商业票据", F["s_commercial"][0])
    assert "commercial bills" in Q["s_commercial"] and "transfer payments" in Q["s_commercial"]
    # ex:weimar-realrate
    said("1922 年 7 月底，帝国银行的贴现率是年息 6\\%，一金马克值 160 纸马克", y, 7, r7, g7)
    said("8 月底，一金马克值 411 纸马克", 8, g8)
    said("（1）要还$160\\times(1+0.06/12)=160.8$纸马克，值$160.8/411\\approx0.39$金马克", 1, g7, 1, r7 / 100, 12, repay,
         repay, g8, repay / g8)
    real = repay / g8 - 1
    said("实际利率约$-61\\%$", -100 * real)
    said("借来的是 1 金马克，还回去的不到 0.4 金马克", 1, 0.4)
    assert repay / g8 < 0.4
    said("（2）$1+i=1.005$，$1+\\pi=411/160\\approx2.57$，$1+r=1.005/2.57\\approx0.39$，$r\\approx-61\\%$", 2, 1,
         1 + r7 / 1200, 1, g8, g7, g8 / g7, 1, 1 + r7 / 1200, 2.57, repay / g8, -100 * real)
    pct("    Fisher: (1 + i) / (1 + pi) - 1 = the gold reckoning", (1 + r7 / 1200) / (g8 / g7) - 1, real, 12)
    x = ratio("1923-10")
    said("（3）1923 年 10 月，物价是 9 月的 296 倍。设一笔一个月的贷款月息 100\\%", 3, 1923, 10, 9, x, 100 * LOAN)
    said("（3）$1+r=2/296.25\\approx0.0068$，$r\\approx-99.3\\%$", 3, 1, 1 + LOAN, x, (1 + LOAN) / x,
         -100 * ((1 + LOAN) / x - 1))
    said("即使月息高到 100\\%", 100 * LOAN)
    said("这就是费雪说的“接近负 100\\%”", F["f30_germany"][0])
    assert "minus" in Q["f30_germany"] and "most rapid inflation" in Q["f30_germany"]


def case(F, Y, Q):
    g = F["fsv_seven"]
    assert "Austria, October 1921–August 1922" in Q["fsv_seven"]
    assert "Hungary I, March 1923–February 1924" in Q["fsv_seven"]
    said("它的恶性通胀从 1921 年 10 月到 1922 年 8 月", g[0], 10, g[1], 8)
    assert "Vienna" in column("note")["tr_vienna"] and "second bock" in Q["tr_vienna"]
    said("1922 年 8 月下旬，国际联盟理事会答应认真谈判", F["s_ausaug"][0], 8)
    assert "late August 1922" in Q["s_ausaug"] and "League of Nations" in Q["s_ausaug"]
    chk("    three protocols (三份)", F["s_ausaug"][1], zh("三"))
    said("10 月初签了三份议定书，安排了一笔 6.5 亿金克朗的国际贷款", 10, F["s_ausloan"][0] * M8)
    assert "2 October 1922" in Q["s_ausaug"]
    assert "August 1922" in Q["s_ausabrupt"] and "abruptly" in Q["s_ausabrupt"]
    said("克朗的汇率在 8 月就突然稳住了", 8)
    y, unit = F["s_ausunit"]
    said("到 1924 年底，奥地利才改用新单位先令，一先令合一万纸克朗", y)
    chk("    ten thousand (一万)", unit, zh("一万"))
    a, y1, b, _ = F["s_auscost"]
    said("到 1923 年 3 月升到 16.7 万，11 月才回落到 7.6 万", y1, 3, a, 11, b)
    assert "March 1923" in Q["s_auscost"] and "November 1923" in Q["s_auscost"]
    said("匈牙利的恶性通胀从 1923 年 3 月到 1924 年 2 月", g[8], 3, g[9], 2)
    loan, y = F["s_hungary"]
    said("1924 年 7 月，一笔 2.5 亿金克朗的重建贷款在国外发行成功", y, 7, loan * M8)
    assert "July 1924" in Q["s_hungary"]
    said("德国在 1923 年借不到这样的外债", 1923)
    assert "Austria, and later of Hungary" in Q["bt_noforeignloan"]


def deeper(F, Y, Q):
    J, N = column("juan"), column("note")
    said("凯恩斯 1919 年的书据古登堡电子本，1923 年的《货币改革论》据 1929 年的重印本，1929 年的论文", Y["k19_settle"],
         Y["tr_live"], F["tr_edition"][0], Y["k29_two"])
    said("Bresciani-Turroni 1937 年的英译修订本", F["bt_edition"][0])
    assert "Schacht's book of 1926" in N["bt_cologne20"]
    said("该书取自沙赫特 1926 年的书", 1926)
    said("Fischer、Sahay 与 Végh（2002）的转述", F["fsv_notice"][0])
    said("Young（1925）与德国统计局 1925 年的《德国货币贬值数字》", 1925, 1925)
    assert "Young" in N["s_99"] and "Young" in N["s_personnel"]
    said("联邦档案馆把地租马克的发行记在 11 月 15 日", 11, F["arch_issue"][0])
    said("Sargent 表 G4 的注把停止贴现国库券的法令记在 15 日", 4, F["s_g4stop"][0])
    assert J["s_g4stop"].startswith("p. 82, Table G4")
    said("Bresciani-Turroni 第 23 页也说 15 日停止贴现、通胀结束", int(J["bt_nov15end"].split()[-1]), 15)
    assert "November 15th, 1923" in N["bt_nov15end"]
    said("同书第 337 页却说新币从 16 日起发行，16 日停止贴现", int(J["bt_issue16"].split()[-1]), F["bt_issue16"][0],
         F["bt_stop16"][0])
    assert J["bt_stop16"] == J["bt_issue16"] == "p. 337"
    said("正文用 15 日", F["arch_issue"][0])
    said("法令第 2、14 条的发行上限是 32 亿，第 16 条给政府 12 亿、给私人 12 亿信贷",
         int(J["law_capital"].removeprefix("§")), int(J["law_limit"][1:3]), F["law_capital"][0] * M8,
         int(J["law_credit"][1:3]), F["law_credit"][0] * M8, F["law_private"][0] * M8)
    mx, gov = F["bt_limit24"]
    said("Bresciani-Turroni 第 348 页的注说最大发行额是 24 亿", int(J["bt_limit24"].split()[1]), mx * M8)
    chk("    = the two credit quotas of §16", mx, F["law_credit"][0] + F["law_private"][0])
    chk("    the government's share in the note", gov, F["law_credit"][0])
    said("正文用法令的 32 亿", F["law_capital"][0] * M8)
    said("1937 年的英文本用英国旧制，milliard 是$10^9$，billion 是$10^{12}$，trillion 是$10^{18}$", 1937, 10, 9, 10, 12,
         10, 18)
    U = column("unit")
    assert "milliard = 10^9" in U["bt_nov1"] and "British billion = 10^12" in U["bt_memo"]
    assert "British trillion = 10^18" in U["bt_oldcirculation"]
    said("Sargent 表 G2 的注把一地租马克写成 1 billion 纸马克，同一章的正文与表 G4 的注却都写$10^{12}$", 2, 1, 4, 10, 12)
    assert "1 billion former paper marks" in Q["s_uniterror"] and "10^12" in N["s_g4unit"]
    said("11 月 16 日流通的旧钞是 93 个英制 trillion，即$9.3\\times10^{19}$纸马克，折合 9,300 万地租马克", 11, 16,
         F["bt_oldcirculation"][0], F["bt_oldcirculation"][0] * 10 ** 18 / 10 ** 19, 10, 19,
         F["bt_oldcirculation"][0] * 10 ** 18 / T12)
    assert "November 16th, 1923" in N["bt_oldcirculation"]
    said("表 G1 没有说指数取的是月中哪一天", 1)
    said("序列取到 1924 年 6 月，7 月起表中改用新单位", 1924, int(prices().index[-1][-2:]), 7)
    said("表 G5 只是帝国普通账户（Sargent 的表题称作联邦政府），其中的税收一栏与 Bresciani-Turroni 第 356 页的税收数字相同", 5,
         int(J["bt_receipts2"].split()[-1]))
    said("帝国马克的含金量据 Bresciani-Turroni 第 24、354 页、Sargent 表 G4 的注与地租银行法令第 6 条的金马克定义，1924 年货币法",
         int(J["bt_reichsmark24"].split()[-1]), int(J["bt_finegold"].split()[-1]), 4, int(J["law_goldmark"][1]), 1924)
    said("11 月 2 日商店的一幕、印钞厂与 10 月 25 日的声明", 11, F["bt_nov2morning"][0], 10, F["bt_memo"][0])
    dd, mm, y = F["bt_finegold"][0], 3, F["bt_finegold"][1]
    assert "March 14th, 1875" in Q["bt_finegold"]
    said("Bresciani-Turroni 第 354 页说这个含金量是 1875 年 3 月 14 日的银行法给旧马克定的",
         int(J["bt_finegold"].split()[-1]), y, mm, dd)
    say("正文只说与战前的旧马克相同")
    a = F["s_ausaug"]
    assert "2 October 1922" in Q["s_ausaug"]
    said("奥地利三份议定书的签字日，Sargent 记作 1922 年 10 月 2 日", a[3], 10, a[2])
    chk("    three protocols (三份)", a[1], zh("三"))
    said("通常的记载是 10 月 4 日", 10, 4)
    assert "4 October 1922" in column("note")["s_ausaug"]
    say("正文只写 10 月初")
    y, sep, _, _ = F["bt_borrow1560"]
    said("1923 年 9 月靠贴现国库券借到的 15.6 亿金马克据同书第 356 页", y, 9, sep * M8,
         int(J["bt_borrow1560"].split()[-1]))
    aug, y, sep2, oct_ = F["bt_float1506"]
    said("第 336 页说这个月流动债务增加了 15.06 亿", int(J["bt_float1506"].split()[-1]), sep2 * M8)
    assert sorted(str(int(sep))) == sorted(str(int(sep2))) and sep != sep2     # 两位数字颠倒
    say("也许是同一个数的两位数字颠倒了，正文用第 356 页的数")


def models() -> None:
    """The key equations as the text writes them, and the identity of eq:weimar-budget checked with numbers."""
    say("R^{f}=\\underbrace{P_X^{f}X-P_I^{f}Q}_{\\text{贸易顺差}}+K^{f}.\\label{eq:weimar-transfer}",
        "上标$f$表示都用同一种外币计价，与\\chref{ch:external}相同",
        "$\\pi_t=P_t/P_{t-1}-1$为通胀率",
        "\\frac{\\Delta H_t}{P_t}=h_t-\\frac{h_{t-1}}{1+\\pi_t}\n"
        "=\\Delta h_t+\\frac{\\pi_t}{1+\\pi_t}h_{t-1}.\\label{eq:weimar-budget}",
        "$\\frac{\\pi_t}{1+\\pi_t}h_{t-1}$是旧钞因物价上涨而失去的购买力",
        "\\frac{M_t}{P_t}=k_tY_t,\\qquad P_t=\\frac{M_t}{k_tY_t},\\qquad V_t=\\frac1{k_t}.\\label{eq:weimar-demand}")
    for H0, P0, H1, P1 in [(100, 100, 300, 500), (9e6, 0.25, 12e6, 1 / 3), (5.0, 2.0, 5.0, 7.0)]:
        h0, h1, pi = H0 / P0, H1 / P1, P1 / P0 - 1
        chk(f"    eq:weimar-budget: h_t - h_(t-1)/(1+pi) = Delta H/P ({H0:g}, {P0:g}, {H1:g}, {P1:g})",
            h1 - h0 / (1 + pi), (H1 - H0) / P1, tol=1e-6)
        chk("        = Delta h + pi/(1+pi) h_(t-1)", (h1 - h0) + pi / (1 + pi) * h0, (H1 - H0) / P1, tol=1e-6)


def frames(F, Y):
    """The numbers outside the sentences of the story: the lines of evidence, the captions of the figures and tables,
    the headers of the boxes and the questions of the examples."""
    said("多出自 Bresciani-Turroni（1937）对这场通胀的研究", F["bt_edition"][0])
    said("经 Young（1925）汇编，由 Sargent（1982）转录", 1925, F["s_copyright"][0])
    P = prices().wpi_1913_100
    said("(a) 1920—1922 年的月度批发物价，先有一段平台，再加速上升。(b) 1923 年的陡升与 1924 年的平台，虚线标出 1923 年 11 月",
         int(P.index[0][:4]), 1922, 1923, int(P.index[-1][:4]), 1923, 11)
    said("纵轴为对数，单位始终是旧纸马克，指数以 1913 年$=100$。数据：Sargent（1982）表 G1，转录自 Young（1925）汇编的官方统计", 1913,
         100, F["s_copyright"][0], 1, 1925)
    y0, y1, _, _ = F["s_ratio1"]
    said("(a) 以 1922 年 1 月$=1$，1923 年 7 月与 8 月的批发物价与帝国银行券的倍数", y0, 1, 1, y1, 7, 8)
    N = notes()
    chk("    (b) three month ends (三个月末)", len(N), zh("三"))
    said("旧纸马克除以$10^{12}$，与地租马克相加，单位为百万地租马克", 10, 12)
    said("数据：Sargent（1982）第 82 页；Bresciani-Turroni（1937）第 337 页", 1982, int(column("juan")["s_ratio1"][3:5]),
         1937, int(column("juan")["bt_oldcirculation"][3:]))
    (y0, m0), (y1, m1) = (map(int, d.split("-")) for d in budget().date.iloc[[0, -1]])
    said("单位为百万金马克，1923 年 12 月至 1924 年 6 月。只含帝国普通账户；11 月的支出空缺，不画。数据：Sargent（1982）表 G5，转引 Young（1925）",
         y0, m0, y1, m1, 11, 1982, 5, 1925)
    said("物价翻一番的时间在 1923 年越来越短", 1923)
    said("\\caption{1923 年的月度批发物价与折合的翻番天数}", 1923)
    said("月份 & 批发物价指数（1913 年$=100$）", 1913, 100)
    said("\\datasource{Sargent（1982）表 G1 的月度指数", 1982, 1)
    said("翻番天数按一个月 30 天、月内匀速上涨换算，$d=30\\ln2/\\ln(\\text{倍数})$", MONTH, MONTH, 2)
    said("\\datasource{地租银行法令（1923）", 1923)
    said("把 1923 年以前就存在的难处讲清楚了", 1923)
    said("{只换货币的名字}{1923 年的一揽子改革}", 1923)
    said("新的金平价要到 1924 年才定下", F["bt_law1924"][1])
    said("（3）政府再印 400 万张呢？（4）若公众把持有的实际价值压到 2,000 万金美元，政府要再取得 900 万", 3,
         F["tr_further4"][0], 4, F["tr_economise"][0], F["tr_gain"][0])
    said("（1）10 月是 9 月的多少倍？涨幅是百分之几？（2）设月内每天按同样的比例上涨，一个月按 30 天算", 1, 10, 9, 2, MONTH)
    said("（3）如果物价真的每天翻一番，30 天会涨到多少倍？（4）11 月 1 日柏林的美元官价是 1,300 亿纸马克，2 日下午是 3,200 亿", 3, MONTH,
         4, 11, F["bt_nov1"][0], F["bt_nov1"][2] * B9, F["bt_nov2morning"][0], F["bt_nov2"][0] * B9)
    said("倍数减 1 再乘 100，才是涨幅", 1, 100)
    said("\\begin{example}{负 100\\% 的实际利率}", 100)
    r7, _, _ = F["bt_discount"]
    said("（1）7 月底借入 160 纸马克，一个月后按年息 6\\% 连本带利还钱", 1, 7, F["bt_goldmark"][0], r7)


def legacy(F):
    said("1923 年的物价与钞票没有固定的比例", 1923)
    said("中间隔着 12 个零", math.log10(T12))


def takeaways(F):
    said("1914 年停兑以后", F["bt_stopgold"][1])
    say("普通收入只付了不到八分之一的开支")
    said("1922 年夏天以后，汇率、物价、税收滞后与赤字互相推动。1923 年 10 月，月度物价折合不到四天翻一番", 1922, 1923, 10)
    said("发行有上限的地租马克，把美元定在 4.2 万亿纸马克", F["bt_stablelevel"][2] * B9)
    said("1924 年 1 月平衡预算，4 月收紧信贷，8 月定下帝国马克", F["bt_balanced"][0], 1, 4, 8)


def selfcheck(F):
    R, sur = SC1["R"], SC1["surplus"]
    said("赔款为 100，贸易顺差为 40，须净借入多少外币", R, sur)
    said("净借款为$100-40=60$", R, sur, R - sur)
    p, v, _, v3 = F["k29_demand"]
    said("价格降低 10\\%，销量增加 20\\%，出口值为什么只增加 8\\%", p, v, v3)
    said("$0.9\\times1.2=1.08$，出口值只多 8\\%", 1 - p / 100, 1 + v / 100, (1 - p / 100) * (1 + v / 100), v3)
    H0, P0, H1, P1 = SC3["H0"], SC3["P0"], SC3["H1"], SC3["P1"]
    said("上期的基础货币与物价都是 100，本期基础货币为 300，物价为 500", H0, H1, P1)
    S, dh, tax = seigniorage(H0, P0, H1, P1)
    said("铸币税为$(300-100)/500=0.4$篮", H1, H0, P1, S)
    said("实际余额由 1 降为 0.6，变化为$-0.4$", H0 / P0, H1 / P1, -dh)
    pi = P1 / P0 - 1
    said("通胀率为 4，通胀税为$4/5\\times1=0.8$。$-0.4+0.8=0.4$", pi, pi, 1 + pi, H0 / P0, tax, -dh, tax, S)
    chk("    the identity holds", dh + tax, S, tol=1e-12)
    sep = ratio("1923-09")
    said("1923 年 9 月的批发物价指数是 8 月的约 25.4 倍", 1923, 9, 8, sep)
    said("$d=30\\ln2/\\ln25.4\\approx6.4$天", MONTH, 2, 25.4, doubling(25.4))
    pct("    with the index itself", doubling(sep), 6.4, 1)
    B = budget().set_index("date")
    dec = B.expenditure_million_goldmark["1923-12"] - B.revenue_million_goldmark["1923-12"]
    said("1923 年 12 月，帝国普通预算仍有约 3.3 亿金马克的赤字", 1923, 12, dec * M8)
    said("1 月起预算已经平衡，3 月以后月月盈余", 1, 3)


def ending(F, Y, Q):
    d, y, usd, _ = F["bt_stablelevel"]
    said("1923 年 11 月 20 日，哈芬施坦死在柏林的时候，美元刚刚停在 4.2 万亿纸马克", y, 11, d, usd * B9)
    assert F["ndb_havenstein_life"][3:] == [d, 11, y]
    assert F["bt_law1924"][3] - y == 1 and (10, F["bt_law1924"][2]) < (11, d)          # 不到一年（1924 年 10 月 11 日）
    say("不到一年，德国的帝国马克就回到了他上任时那个马克的含金量，只是隔着 12 个零")
    assert F["ndb_havenstein_office"][0] > F["bt_finegold"][1]                         # 1908 年上任时，马克仍是 1875 年的含金量
    chk("    twelve zeros", math.log10(F["bt_reichsmark24"][2] * B9), 12)
    chk("Britain, 1925", Y["k25_prewar"], 1925)
    assert "up to its pre-war value in gold" in Q["k25_prewar"]
    said("英国走了另一条路，1925 年把英镑提回到战前的黄金价值", Y["k25_prewar"])
    q27 = re.search(r"\\guidequestion\{([^}]*)\}", (ROOT / "zh" / "ch27_interwar.tex").read_text(encoding="utf-8"))
    assert q27, "Chapter 27 has no guide question"
    t = tex_text().rstrip()
    assert t.endswith(q27.group(1)), "the last words are not Chapter 27's question"
    said(q27.group(1), 1925, 1920)


# the life dates the chapter gives without a row of its own: the same words in an earlier chapter
LIVES = {"John Maynard Keynes，1883—1946": "ch20_say", "Phillip Cagan, 1927—2012": "ch01_intro"}
# the life dates from rows of the snapshot: words -> (row, index of the birth year, index of the death year)
ROW_LIVES = {"Rudolf Havenstein，1857—1923": ("ndb_havenstein_life", 2, 5),
             "Karl Helfferich，1872—1924": ("ndb_helfferich_life", 2, 5),
             "Walther Rathenau，1867—1922": ("ndb_rathenau_life", 2, 5),
             "Hans Luther，1879—1962": ("luther_life", 0, 1),
             "Hjalmar Schacht，1877—1970": ("ndb_schacht_life", 2, 5),
             "Gustav Stresemann，1878—1929": ("stresemann_life", 1, 3),
             "Bertil Ohlin，1899—1979": ("ohlin_life", 1, 3)}
# what other chapters tell: (words of this chapter, chapter where it is told, words there)
EVENTS = [("正是战前一美元换 4.20 马克的老比价（\\chref{ch:intro}）", "ch01_intro", "按平价，一美元合 4.20 马克"),
          ("贴现就是在到期以前按低于面值的价钱把它买下（\\chref{ch:intro}）", "ch01_intro",
           "贴现，就是中央银行在到期以前按低于面值的价钱把国库券买下"),
          ("\\chref{ch:wicksell}讲到，大战一来，纸币就没有了黄金的约束", "ch25_wicksell", "再没有黄金替人把关"),
          ("\\chref{ch:periphery}讲过 1895 年与 1901 年的赔款", "ch24_periphery", "1895 年与 1901 年的赔款"),
          ("1920 年的通胀率是 66.5\\%（\\chref{ch:intro}）", "ch01_intro", "1920 年德国的通胀率是 66.5\\%"),
          ("一年就是约 130 倍（\\chref{ch:songming}）", "ch12_songming", "$1.5^{12}\\approx129.7$ 倍"),
          ("\\chref{ch:intro}引的德国最高月通胀率是 29,525.71\\%", "ch01_intro", "德国 1920—1923 年最高的月通胀率是 29,525.71\\%"),
          ("就是\\chref{ch:intro}引过的联邦储备委员会公报里的数字", "ch01_intro", "资本 32 亿地租马克"),
          ("就是\\chref{ch:intro}引过的联邦储备委员会公报里的数字", "ch01_intro", "12 亿地租马克的贷款"),
          ("中世纪的铸币厂从送来的金银里扣下一部分", "ch11_medieval", "送金属的人得到的纯金属，总是比送来的少"),
          ("这就是费雪说的“接近负 100\\%”", "ch25_wicksell", "接近负 100\\%"),
          ("1925 年把英镑提回到战前的黄金价值", "ch23_goldstandard", "1925 年，他反对把英镑提回战前的黄金价值")]


def book(F, Q):
    """Life dates and what other chapters tell."""
    t = tex_text()
    for words, ch in LIVES.items():
        assert words in t, words
        assert words in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (words, ch)
    for words, (rid, i, j) in ROW_LIVES.items():
        assert words in t, words
        assert f"{F[rid][i]:.0f}—{F[rid][j]:.0f}" in words, (words, rid)
    for here, ch, there in EVENTS:
        assert here in t, here
        assert there in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (ch, there)
    chk("Keynes 1883-1946 (Wikisource) = Chapter 20", F["keynes_life"], [1883, 1946])
    chk("Koech's Germany 1920-23 (the row Chapter 1 cites)", F["ko_germany"][:2], [1920, 23])
    print(f"ok {len(LIVES) + len(ROW_LIVES)} life dates, {len(EVENTS)} statements of other chapters")


def witnesses(F, Q):
    """Second witnesses of statements of the text, and the bibliography block of the chapter."""
    N = column("note")
    # 15 or 16 November
    chk("the issue: 15 November (Bundesarchiv) / 16 November (Bresciani-Turroni p. 337)",
        [F["arch_issue"][0], F["bt_issue16"][0]], [15, 16])
    chk("the end of the discounting: 15 (Sargent G4) / 16 (Bresciani-Turroni p. 337)",
        [F["s_g4stop"][0], F["bt_stop16"][0]], [15, 16])
    assert "Compare bt_stop16" in N["bt_nov15end"]
    assert "almost immediately to all prices" in Q["bt_closeconnection"]                 # 国际收支说最强的证据
    # the limits: 3.2 milliard (the decree, the NDB, Sargent, Chapter 1) and Bresciani-Turroni's 2.4
    chk("3.2 milliard: decree, NDB, Sargent",
        [F["law_capital"][0] / 1000, F["ndb_luther_backing"][0], F["s_limits"][0]], [3.2, 3.2, 3.2])
    assert "not the cap" in N["bt_limit24"]
    # the conversion: a trillion paper marks to a rentenmark (three witnesses)
    chk("1,000 milliard per gold mark (Bresciani-Turroni) = 1 Billion (NDB) = 10^12 (Sargent)",
        F["bt_stablelevel"][3] * B9, T12)
    assert "1 trillion (10^12)" in N["s_g4unit"]
    # the gold content of the Reichsmark (two passages and the gold mark of the decree)
    assert "equal to that of the old mark" in Q["bt_reichsmark24"]
    assert "same as that fixed for the old mark" in Q["bt_finegold"]
    # the taxes of the stabilization (Bresciani-Turroni and Sargent's G5)
    assert "Table G5" in N["bt_receipts2"]
    # Cagan's definition (Fischer, Sahay and Vegh; Koech)
    assert "Phillip Cagan" in Q["ko_cagandef"] and "Cagan defined a hyperinflation" in Q["fsv_cagan"]
    # the licences and the bibliography
    _, m = load_snapshot("weimar_facts")
    gmpi = ("Articles may be reprinted on the condition that the source is credited and a copy is provided to the "
            "Globalization and Monetary Policy Institute")
    notices = ("© 1982 by The National Bureau of Economic Research. All rights reserved.",
               "© 2002 by Stanley Fischer, Ratna Sahay and Carlos A. Végh. All rights reserved. Short sections of text",
               gmpi, "ALL RIGHTS RESERVED", "public domain in the United Kingdom")
    for words in notices:
        assert words in m["license"], words
    assert Q["s_copyright"].startswith("© 1982 by The National Bureau of Economic Research")
    assert Q["fsv_notice"] in m["license"] and Q["ko_terms"] in m["license"]
    assert "oldid 3802395" in m["sources"]["renten1923"]["version"]
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    start = bib.index("% ---- 第 26 章")
    following = re.search(r"^% ---- 第 \d+ 章", bib[start + 1:], re.MULTILINE)
    end = start + 1 + following.start() if following else bib.index("\\end{thebibliography}")
    block = bib[start:end]
    items = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", block)}
    assert "© 1982 by The National Bureau of Economic Research. All rights reserved" in items["sargent1982"]
    assert Q["fsv_notice"].removesuffix(".") in items["fischer2002"]
    assert "ALL RIGHTS RESERVED" in items["bresciani1937"] and "只引短语" in items["bresciani1937"]
    assert "只引短语" in items["ohlin1929"] and "1979" in items["ohlin1929"]
    assert "公有领域" in items["keynes1919"] and "公有领域" in items["keynes1923"] and "1929 年重印本" in items["keynes1923"]
    assert "oldid=3802395" in items["renten1923"] and "CC BY-SA" in items["renten1923"]
    for key, page in [("havenstein1969", "8 (1969): 137"), ("helfferich1969", "8 (1969): 470--472"),
                      ("rathenau2003", "21 (2003): 174--176"), ("luther1987", "15 (1987): 544--547"),
                      ("schacht2005", "22 (2005): 489--491")]:
        assert page in items[key], key
    assert "Bild 183-H29263" in items["bundesarchiv1923"] and "Bild 183-H29263" in N["arch_queue"]
    keys = set(re.findall(r"\\bibitem\{([^}]+)\}", bib))
    cited = {k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", tex_text()) for k in c.split(",")}
    assert cited <= keys, sorted(cited - keys)
    assert set(items) <= cited, sorted(set(items) - cited)
    assert "Articles may be reprinted" in bib[bib.index("\\bibitem{koech2011}"):].split("\n")[0]
    print(f"ok {len(cited)} works cited, {len(items)} of them in the bibliography block of Chapter 26")


def counts() -> None:
    """The editor's limits: “不能” at most about a dozen; no source as the subject of a sentence outside the 史料说明."""
    t = tex_text()
    main = re.sub(r"\\begin\{deeper\}.*?\\end\{deeper\}", "", t, flags=re.DOTALL)
    n = t.count("不能")
    print(f"ok “不能” {n} times")
    assert n <= 12, n
    verbs = "认为|写道|说|指出|记述|估计|承认|报道|记载|提到|列出|给出"
    subj = re.findall(r"(?:^|[。；：，\n])\s*(?:Bresciani-Turroni|萨金特|Sargent|Young|公报)(?:（\d{4}）)?(?:" + verbs + ")",
                      main)
    assert not subj, subj
    assert "不能据此断言" not in t


def main() -> None:
    df = _rows()
    F, Y, Q = facts(), years(), quotes()
    check_readings(df)
    check_tables()
    check_text(df)
    guide(F, Y)
    opening(F, Y, Q)
    world(F, Y, Q)
    transfer(F, Y, Q)
    fiscal(F, Y, Q)
    demand(F, Y, Q)
    test(F, Y, Q)
    stabilization(F, Y, Q)
    cost(F, Y, Q)
    case(F, Y, Q)
    deeper(F, Y, Q)
    models()
    frames(F, Y)
    legacy(F)
    takeaways(F)
    selfcheck(F)
    ending(F, Y, Q)
    book(F, Q)
    witnesses(F, Q)
    counts()
    anchors("zh/ch26_weimar.tex", df["id"], script=Path(__file__))


if __name__ == "__main__":
    main()
