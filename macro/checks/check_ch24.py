"""Chapter 24 (第一次全球化中的边缘): every number and every quotation in zh/ch24_periphery.tex.

    python3 checks/check_ch24.py

Inputs:
  periphery_facts                      quotations of Hansard (26 June 1893) and its people pages, the reports of the
                                       Indian Currency Committees of 1893 (Herschell) and 1898 (Fowler, with the
                                       minute of dissent of Campbell and Muir), Keynes (1913), Naoroji (1901),
                                       Maddison (1971), the Indian Famine Commissions (1880, 1901), the NBER working
                                       papers of Obstfeld and Taylor (2002), Meissner (2002), Mitchener and
                                       Weidenmier (2007), Mitchener, Shizume and Weidenmier (2009), Reinhart and
                                       Rogoff (2008), Atwell (2008), Irigoin (2013), the treaties of Shimonoseki
                                       (1895) and the Boxer Protocol (1901), Wikisource's author pages (checked by
                                       data/fetch/verify_web_quotes.py) and the 清史稿 (data/fetch/verify_quotes.py)
  gpih_silver_market_1850_1914         Lindert (GPIH, after Jastram 1981): the London market price of standard silver
  boe_millennium_external_1850_1913    Bank of England, A Millennium of Macroeconomic Data: the UK current account and
                                       net external assets (A46), nominal GDP (A9) and the consol yield (A31)
  boe_millennium_bank_rate_1888_1892   Bank Rate, 1888-1892 (sheet D1)
The figure module figsrc/fig_ch24.py imports the functions defined here.

What is checked here:
  1. readings   every number of the value column of periphery_facts is read from its quotation (digits, English
                number words, fractions, shillings and pence, the numerals of the 清史稿) or, where the OCR garbles
                the figure and the note gives the source's own figure, from the note
  2. the text   every “…” in the chapter is the chapter's Chinese rendering of a quotation (TRANSLATIONS:
                rendering -> row or rows) or a term of the text (ALLOW)
  3. numbers    every number of the text, section by section, with quoted()
  4. anchors    the paraphrase anchors `% 据: ...` name rows of periphery_facts

Models (the chapter's key equations):
    the silver rupee         x ~ s P,  s = (3/8 x 11/12) / 0.925 standard ounces;  e = 240 / x       (eq:periph-silver)
                             (x pence per rupee, P pence per standard ounce in London, e rupees per pound)
    the gold-exchange band   16 - c_back <= x <= 16 + c_out,  c_out ~ 1/8, c_back ~ 3/32 (pence)        (eq:periph-band)
    Naoroji's drain          H = X - M + dL,  D_N = (1 + pi) X + dL - M = H + pi X                     (eq:periph-drain)
"""
from __future__ import annotations

import math
import re
import sys
from datetime import date
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd

from common import ROOT, anchors, load_snapshot, quoted

sys.path.insert(0, str(ROOT / "data" / "fetch"))
from classical_numerals import checked  # noqa: E402

TEX = ROOT / "zh" / "ch24_periphery.tex"
WAN = 1e4                                  # 万
YI = 1e8                                   # 亿
MILL = 1e6

FINE = Fraction(11, 12)                    # the rupee's fineness (Keynes)
STANDARD = 0.925                           # the fineness of standard silver, whose London price GPIH gives
PAR = 16.0                                 # pence per rupee from 1898
# Reinhart and Rogoff's two clusters of defaults, in the years the text rounds their words to
# ('the late 1860s up to the mid-1870s', 'the mid-1880s through the early 1890s'): the shading of fig:periph_world
RR_CLUSTERS = [(1867, 1875), (1885, 1893)]
# Teaching inputs stated in the text
REMIT = 16e6                               # ex:periph-rupee (3): £16 m a year, inside Keynes's £15-18 m
BAND_RUPEES = 150_000                      # ex:periph-band (1)-(2)
BID = 16 + Fraction(3, 16)                 # ex:periph-band (1): the Secretary of State's price, pence
SC2_RUPEES = 100_000                       # self-check 2
SC3 = dict(X=100, M=90, dL=5, pi=0.10)     # self-check 3
YEARS_NAOROJI = 1872 - 1835 + 1            # 1835-1872, 38 years


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


def rnd(what: str, value: float, expected: float, step: float) -> float:
    """A number printed rounded to `step` (e.g. 10 for '约 470 万' in units of 万)."""
    return quoted(what, float(value), expected, tol=0.5 * step + 1e-9)


# ---------------------------------------------------------------------------------------------------
# Loaders
def _rows() -> pd.DataFrame:
    df, meta = load_snapshot("periphery_facts", dtype=str, keep_default_na=False)
    assert 24 in meta["used_in"]
    assert df["id"].is_unique
    return df


def num(x: str) -> float:
    """'5', '1/3', '25.8', '-0.30', and mixed numbers '16+1/8'."""
    if "+" in x:
        a, b = x.split("+")
        return float(a) + num(b)
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


def silver() -> pd.Series:
    """The London market price of standard silver, pence per troy ounce, 1850-1914 (Lindert, GPIH)."""
    df, m = load_snapshot("gpih_silver_market_1850_1914")
    assert 24 in m["used_in"]
    s = df.set_index("year")
    assert (s.pence_per_oz_standard - 240 * s.gbp_per_oz_standard_market).abs().max() < 1e-6
    assert (s.gbp_per_oz_pure_market * STANDARD - s.gbp_per_oz_standard_market).abs().max() < 1e-4
    return s.pence_per_oz_standard


def external() -> pd.DataFrame:
    """UK current account and net external assets (£ m and % of GDP) and the consol yield (%), 1850-1913."""
    df, m = load_snapshot("boe_millennium_external_1850_1913")
    assert 24 in m["used_in"]
    assert "Bank of England" in m["license"] or "Bank of England" in m["source"]
    e = df.set_index("year")
    e["ca_gdp"] = 100 * e.ca_surplus / e.gdp_market_prices
    e["nea_gdp"] = 100 * e.net_external_assets / e.gdp_market_prices
    return e


def bank_rate() -> pd.Series:
    """Bank Rate at the end of 1887 and on each day it changed, 1888-1892."""
    df, m = load_snapshot("boe_millennium_bank_rate_1888_1892", parse_dates=["date"])
    assert 24 in m["used_in"]
    s = df.set_index("date").bank_rate
    assert s.index.is_monotonic_increasing and (s.diff().dropna() != 0).all()
    return s


# ---------------------------------------------------------------------------------------------------
# The arithmetic of the chapter
S_RUPEE = float(Fraction(3, 8) * FINE) / STANDARD     # standard ounces of silver in a rupee (eq:periph-silver)


def rupee_silver(P):
    """eq:periph-silver: the silver value of a rupee in pence, P the price of standard silver in pence per ounce."""
    return S_RUPEE * P


def per_pound(x):
    """e = 240 / x: rupees per pound for x pence per rupee."""
    return 240 / x


def rate_on(s: pd.Series, day: str) -> float:
    return float(s.loc[:pd.Timestamp(day)].iloc[-1])


def herschell() -> pd.Series:
    """The average rate of the bills on India in the Herschell report's table (pence per rupee, official years)."""
    F, Y = facts(), years()
    return pd.Series({Y[i]: F[i][0] for i in F if i.startswith("hr_x")}).sort_index()


def adoptions() -> pd.Series:
    """Meissner's Table 1: the first year in which each country adopted gold (Argentina and Chile by the first of
    their years); the countries marked '---' are left out."""
    F = facts()
    U = column("unit")
    return pd.Series({i[3:]: F[i][0] for i in F if i.startswith("me_") and U[i] == "year of adoption"}).sort_values()


def not_adopted() -> list[str]:
    Q = quotes()
    return sorted(i[3:] for i in Q if i.startswith("me_") and Q[i].endswith("---"))


def drain(X: float, M: float, dL: float, pi: float) -> tuple[float, float]:
    """eq:periph-drain: H = X - M + dL and Naoroji's D_N = (1 + pi) X + dL - M."""
    return X - M + dL, (1 + pi) * X + dL - M


# ---------------------------------------------------------------------------------------------------
# 1. Readings of the numbers
SMALL = {"a": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
         "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
         "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
SCALE = {"thousand": 1e3, "million": 1e6, "millions": 1e6}
ORDINAL = {"half": 2, "third": 3, "thirds": 3, "quarter": 4, "fourth": 4, "fifth": 5, "twelfths": 12}
ORDINAL_WORD = {"fifth": 5}
VULGAR = {"⅛": Fraction(1, 8), "⅜": Fraction(3, 8), "⅓": Fraction(1, 3), "¼": Fraction(1, 4)}


def cardinal(s: str) -> float:
    """An English cardinal: 'forty', 'two millions', 'four hundred and fifty million'."""
    total, cur = 0.0, 0.0
    for w in s.lower().replace("-", " ").replace("–", " ").split():
        if w == "and":
            continue
        if w in SMALL:
            cur += SMALL[w]
        elif w == "hundred":
            cur *= 100
        elif w in SCALE:
            total += cur * SCALE[w]
            cur = 0.0
        else:
            raise ValueError(w)
    return total + cur


def fraction(s: str) -> float:
    """'one-fifth', 'a third', 'a quarter', 'eleven–twelfths'."""
    a, b = s.lower().replace("-", " ").replace("–", " ").split()
    return float(Fraction(int(cardinal(a)), ORDINAL[b]))


def figure(s: str) -> float:
    return float(s.replace(",", ""))


def vulgar(s: str) -> float:
    """'⅜', '33⅓', '59¼'."""
    if s[-1] in VULGAR:
        return float((int(s[:-1]) if s[:-1] else 0) + VULGAR[s[-1]])
    return figure(s)


def pence(s: str) -> float:
    """Shillings and pence as pence: '1s. 4d.', 'Is. 3d.' (the OCR's I for 1), '1s. 4⅛d.', '1s. 3–29/32d.'."""
    m = re.fullmatch(r"([1I])s\. (\d+)(?:–(\d+)/(\d+)|([⅛⅜⅓¼]))?d\.", s)
    assert m, s
    d = Fraction(int(m.group(2)))
    if m.group(3):
        d += Fraction(int(m.group(3)), int(m.group(4)))
    if m.group(5):
        d += VULGAR[m.group(5)]
    return float(12 + d)


def zh(s: str) -> float:
    """A numeral of the 清史稿: classical_numerals.checked; 兆 after a numeral of money is a million here (四百五十兆
    is the 450 million taels of the Boxer Protocol, row bx_450)."""
    if s.endswith("兆"):
        return float(checked(s[:-1])) * 1e6
    return float(checked(s))


def read(phrase: str, how: str) -> list[float]:
    if how == "num":
        return [figure(phrase)]
    if how == "en":
        return [cardinal(phrase)]
    if how == "frac":
        return [fraction(phrase)]
    if how == "slash":                        # '3/32'
        a, b = phrase.split("/")
        return [float(a) / float(b)]
    if how == "vulgar":
        return [vulgar(phrase)]
    if how == "mil":                          # '115 million', '30 million pounds', '5¼' (with the note's millions)
        return [vulgar(phrase.split()[0].lstrip("£₤¥")) * MILL]
    if how == "deg":                          # the OCR's ° for the decimal point: '22°35'
        return [figure(phrase.replace("°", "."))]
    if how == "ord":                          # '26th', '1st'
        return [float(re.match(r"\d+", phrase).group())]
    if how == "ordword":                      # 'fifth'
        return [float(ORDINAL_WORD[phrase])]
    if how == "sd":
        return [pence(phrase)]
    if how == "range":                        # '1900–14': the second year written with two digits
        a, b = re.split(r"[–-]", phrase)
        return [figure(a), figure(a[:2] + b)]
    if how == "quarter":                      # 'one million and a quarter'
        return [cardinal(phrase.replace(" and a quarter", "")) * 1.25]
    if how == "zh":
        return [zh(phrase)]
    raise ValueError(how)


FIGURES = re.compile(r"\d[\d,]*(?:\.\d+)?")
EN, NUM, NOTE, ZH = "en", "num", "note", "zh"
# id -> [(phrase, how[, NOTE])], in order. A third element NOTE means the phrase is read from the note column (the
# source's own figure, which the OCR garbles). Rows not listed are read with all the figures of the quotation.
READINGS = {
    "hc_ref": [("26", NUM), ("1893", NUM), ("14", NUM)],                # the columns 59-61 are not values
    "fw_notif": [("26th", "ord"), ("1893", NUM), ("16", NUM)],          # 'Nos. 2662-4' are the notifications
    "fw_five": [("five", EN)],
    "fw_1s3d": [("16", NUM), ("15", NUM)],
    "fw_opium_chests": [("75,381", NUM), ("1892", NUM), ("56,069", NUM), ("1897", NUM)],
    "hr_ratio": [("1s. 4d.", "sd")],
    "hr_silver": [("59¼", "vulgar", NOTE), ("1873", NUM), ("51¼", "vulgar", NOTE)],
    "hr_karachi": [("1st", "ord", NOTE), ("1892", NUM)],
    "hr_karachi_fall": [("60", NUM), ("38", NUM), ("39", NUM), ("35", NUM), ("24", NUM), ("14°65", "deg")],
    "ky_1899": [("1899", NUM), ("1s. 4d.", "sd")],
    "ky_limits": [("1s. 4⅛d.", "sd"), ("1s. 3–29/32d.", "sd")],
    "ky_calcutta": [("1s. 3–29/32d.", "sd")],
    "ky_15": [("15", NUM)],                                             # '£1 to 15 rupees'
    "ky_dates1899": [("1899", NUM), ("1s. 4d.", "sd")],
    "ky_dates1904": [("1904", NUM), ("1s. 4⅛d.", "sd")],
    "ky_dates1908": [("1908", NUM), ("1s. 3–29/32d.", "sd")],
    "ky_1898": [("1898", NUM), ("1s. 4d.", "sd")],
    "ky_ceiling": [("1s. 4d.", "sd")],
    "ky_eighth": [("⅛", "vulgar")],
    "ky_back": [("3/32", "slash")],
    "ky_contains": [("⅜", "vulgar"), ("eleven–twelfths", "frac")],
    "ky_tea": [("115 million", "mil"), ("1909", NUM)],
    "ky_silver40": [("40", NUM), ("33⅓", "vulgar"), ("29", NUM)],
    "ky_yarn91": [("161 million", "mil")],
    "ky_yarn92": [("189 million", "mil"), ("134 millions", "mil"), ("159 millions", "mil")],
    "ky_yarn05": [("298 millions", "mil")],
    "ky_yarn08": [("235 millions", "mil")],
    "nr_forty": [("forty", EN), ("thirty", EN)],
    "nr_shillings": [("two", EN)],
    "nr_a1835": [("1835", NUM), ("1839", NUM), ("5,347,000", NUM, NOTE)],
    "nr_45": [("11", NUM, NOTE), ("16", NUM, NOTE), ("45", NUM)],
    "md_1856": [("3.5 million", "mil"), ("1856", NUM)],
    "md_third": [("a third", "frac")],
    "md_quarter": [("a quarter", "frac")],
    "md_t3554": [("4.5", NUM)],
    "md_t5574": [("7.3", NUM), ("50.0", NUM), ("0.21", NUM)],
    "md_t7594": [("13.4", NUM), ("80.0", NUM), ("0.30", NUM)],
    "md_t9513": [("16.8", NUM), ("77.6", NUM), ("0.26", NUM)],
    "md_t33": [("1835", NUM), ("1967", NUM)],                           # 'Table 3-3'
    "f80_excess": [("190 millions", "mil"), ("5¼", "mil", NOTE)],
    "f80_births": [("two millions", EN)],
    "f80_seven": [("seven millions", EN)],
    "f01_quarter": [("one million and a quarter", "quarter")],
    "f01_one": [("one million", EN)],
    "f01_cholera": [("one-fifth", "frac")],
    "ot_7": [("1870", NUM), ("7", NUM), ("20", NUM), ("1900–14", "range")],
    "ot_t4": [("1870", NUM), ("1913", NUM)],                            # 'Table 4'
    "ot_gs": [("-0.30", NUM), ("0.06", NUM), ("-0.57", NUM), ("0.08", NUM)],
    "mw_fifth": [("fifth", "ordword")],
    "mw_30m": [("1890", NUM), ("30 million", "mil")],
    "mw_48": [("₤48 million", "mil"), ("1890", NUM), ("60", NUM)],
    "ms_30bp": [("30", NUM)],                                           # '(Obstfeld and Taylor, 2003)'
    "ms_eleven": [("eleven", EN)],
    "ms_votes": [("15", NUM), ("seven", EN), ("six", EN), ("two", EN)],
    "ms_60": [("60", NUM)],                                             # 'the late 1890s'
    "ms_rates30": [("30", NUM), ("six", EN)],
    "ms_1899": [("1899", NUM), ("¥100 million", "mil"), ("90", NUM), ("4.45", NUM)],
    "at_back": [("1850", NUM)],                                         # 'the mid-1850s'
    "ir_70000": [("70,000", NUM)],                                      # 'the 1850s'
    "ir_63000": [("63,000", NUM)],
    "ir_1892": [("70,000", NUM), ("1892", NUM)],                        # 'During the 1870'
    "sh_eight": [("eight", EN)],
    "bx_450": [("four hundred and fifty million", EN)],
    "bx_sterling": [("3", NUM)],                                        # '0 3s. 0d.'
    "bx_39": [("thirty-nine", EN)],
    "bx_1940": [("1902", NUM), ("1940", NUM)],                          # 'the 1st of January'
    "qs_opium58": [("三十", ZH)],                                        # 每百斤纳税银三十两
    "qs_110": [("一百一十", ZH)],
    "qs_india70": [("七十万", ZH)],
    "qs_three": [("三", ZH)],
    "qs_boxer450": [("四百五十兆", ZH)],
    "qs_argue": [("四百五十兆", ZH)],
    "qs_1906": [("十", ZH)],                                             # 命限十年
}
for _i in [k for k in ("hr_x1873", "hr_x1876", "hr_x1882", "hr_x1885", "hr_x1886", "hr_x1887", "hr_x1888",
                       "hr_x1890", "hr_x1892")]:
    READINGS[_i] = None                       # filled in check_readings: the third figure of the table's row


def check_readings(df: pd.DataFrame) -> None:
    n = 0
    for r in df.itertuples():
        if not r.value:
            assert r.id not in READINGS, r.id
            continue
        vals = [num(x) for x in r.value.split(";")]
        texts = {"quote": " ".join(r.quote.split()), NOTE: " ".join(r.note.split())}
        if r.id in READINGS and READINGS[r.id] is None:
            # a row of the Herschell table: year, Vienna on London, India (the value), the two indices
            cells = re.findall(r"\d+°\d+", texts["quote"])
            assert texts["quote"].startswith(r.year) and len(cells) >= 2, r.id
            got = read(cells[1], "deg")
            assert "第三个数是印度汇率" in r.note
        elif r.id in READINGS:
            got, pos = [], {"quote": 0, NOTE: 0}
            for item in READINGS[r.id]:
                phrase, how = item[0], item[1]
                where = item[2] if len(item) > 2 else "quote"
                k = texts[where].find(phrase, pos[where])
                assert k >= 0, f"{r.id}: {phrase!r} not found (in order) in the {where}"
                pos[where] = k + len(phrase)
                got += read(phrase, how)
        else:
            got = [figure(x) for x in FIGURES.findall(texts["quote"])]
        assert [round(g, 9) for g in got] == [round(v, 9) for v in vals], f"{r.id}: read {got}, value column {vals}"
        n += 1
    quoted("rows with values, each read from its quotation (or its note)", n, 245)


# ---------------------------------------------------------------------------------------------------
# 2. Every “…” of the text against the snapshot
ALLOW = {
    "财富外流",                 # the guide box's name of Naoroji's 'drain' (rows nr_bleeding, md_controversy)
}
# the chapter's Chinese renderings of the quotations: rendering -> row (or rows)
TRANSLATIONS = {
    # opening
    "打算在印度实行金本位，但黄金目前不作法偿货币。": "hc_intended",
    "他实际上是不是要让整个印度帝国都用代用币？": "hc_token",
    # sec:periph-world
    "世界的银行家": "ot_bankers",
    "明显的视觉相关": "rr_corr",
    # sec:periph-india
    "本国费用": "md_homecharges",
    "比如 1 先令 4 便士": "hr_ratio",
    "垄断的卢比": "fw_monopoly",
    "没有金币的金本位完全不可能": "ky_rothschild",
    "放血": "nr_bleeding",
    "肯定是往低里算的": "nr_mark",
    "被英国留下": "nr_500",
    "唯一真正的争议是统计上的": "md_statistical",
    "不能为印度的纳税人省下一个法寻": "nr_farthing",
    "变相多征 45\\% 的税": "nr_45",
    # sec:periph-china
    "向来洋药不准通商，现稍宽其禁，听商贸易。每百斤纳税银三十两": "qs_opium58",
    "洋药流毒多年，自应设法禁止。": "qs_poison",
    "外洋金镑值价日昂，比初定机器时，价高过半": "qs_zhang",
    "出口的价格跌了，进口的价格涨了。": "ms_shib_price",
    "金债": "bx_gold",
    "各国赔款欲改银为金，以金价算": "qs_gold",
    # sec:periph-baring
    "到 1887 年底，病人还有救；到了 1888 年，已经没救了。": "mw_terry",
    "帮助很少": "mw_little",
    # sec:periph-test
    "认可的印章": "ot_seal",
    "茶叶业彻底而无可挽回的毁灭": "ky_ruin",
    "我相信会的": "hr_tea",
    "经验断然地支持了理论。": "ky_experience",
    "是对的": "ms_correct",
    # the ending
    "实际上是印在银子上的钞票": "ky_token",
}
# the renderings that are kept literally close to the source: words of the source that must be there
KEYWORDS = {
    "hc_intended": ["intended to introduce a gold standard", "not be made a legal tender at present"],
    "hc_token": ["practically", "token coinage for the whole Indian Empire"],
    "ot_bankers": ["bankers to the world"],
    "rr_corr": ["marked visual correlation"],
    "md_homecharges": ["Home Charges"],
    "hr_ratio": ["say 1s. 4d."],
    "fw_monopoly": ["monopoly rupee"],
    "ky_rothschild": ["gold standard without a gold currency", "utter impossibility"],
    "nr_bleeding": ["bleeding"],
    "nr_mark": ["quite under the mark"],
    "nr_500": ["England has kept back"],
    "md_statistical": ["only real grounds for controversy are statistical"],
    "nr_farthing": ["cannot save a single farthing to the Indian taxpayers"],
    "nr_45": ["covert exaction of 45 per cent"],
    "ms_shib_price": ["price of exports has fallen", "price of imports has risen"],
    "bx_gold": ["gold debt"],
    "mw_terry": ["until the end of 1887", "save the patient", "1888", "no longer possible"],
    "mw_little": ["did little to help"],
    "ot_seal": ["seal of approval"],
    "ky_ruin": ["entire and irretrievable ruin of the tea industry"],
    "hr_tea": ["I am sure it would"],
    "ky_experience": ["experience has decisively supported theory"],
    "ms_correct": ["were correct"],
    "ky_token": ["virtually a note printed on silver"],
}
CHINESE = {"qs_opium58", "qs_poison", "qs_zhang", "qs_gold"}   # the rendering is the source's own words


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
        if q in ALLOW:
            continue
        assert q in TRANSLATIONS, f"not listed: “{q}”"
        t = TRANSLATIONS[q]
        for rid in (t,) if isinstance(t, str) else t:
            assert rid in ids, rid
            if rid in CHINESE:
                assert q in Q[rid], (q, rid)
            else:
                assert rid in KEYWORDS, rid
    stale = (set(ALLOW) | set(TRANSLATIONS)) - used
    assert not stale, f"listed but not in the text: {sorted(stale)}"
    for rid, words in KEYWORDS.items():
        for w in words:
            assert w in Q[rid], f"{rid}: {w!r} not in the quotation"
    assert "drain" in Q["nr_bleeding"] and "'drain'" in Q["md_controversy"]          # “财富外流”
    print(f"ok {n} quotations of the text found in the snapshot (or listed as exceptions)")


# ---------------------------------------------------------------------------------------------------
# 3. Numbers, section by section
def opening(F, Y, Q, P, E):
    chk("26 June 1893 was a Monday (weekday 0)", date(1893, 6, 26).weekday(), 0)
    chk("Hansard: 26 June 1893", F["hc_ref"][:2], [26, 1893])
    assert "to-day" in Q["hc_telegram"] and "GLADSTONE" in Q["hc_gladstone"] and "FIRST LORD" in Q["hc_gladstone"]
    chk("Gladstone 1809-1898", F["hp_gladstone"], [1809, 1898])
    a, b, c, d = F["hp_gladstone_pm"]
    assert (b, a) <= (1893, 6) and "Prime Minister" in Q["hp_gladstone_pm"] and d >= 1893   # 首相
    chk("Herschell 1837-1899", [F["hp_herschell"][0], F["hp_herschell"][2]], [1837, 1899])
    assert "Baron Herschell" in Q["hp_herschell_baron"]                                   # 赫歇尔勋爵
    assert "Herschell's Committee" in Q["hc_act"] and "takes effect at once" in Q["hc_act"]
    assert "free coinage of silver" in Q["hc_close"]
    chk("16d. a rupee", F["hc_16d"], [PAR])
    chk("    = 1s. 4d.", 12 + 4, PAR)
    chk("    15 rupees to the pound", per_pound(PAR), 15)
    assert "half-sovereigns" in Q["hc_dues"] and "same rate" not in Q["hc_dues"]          # the rate: the note
    assert "同一比价" in column("note")["hc_dues"]
    chk("Goschen 1831-1907", [F["hp_goschen"][0], F["hp_goschen"][2]], [1831, 1907])
    chk("    Chancellor of the Exchequer 1887-1892", F["hp_goschen_ce"], [1887, 1892])
    chk("the silver of the natives (亿英镑)", F["hc_100m"][0] / YI, 1)
    assert "legal tender" in Q["hc_legal"] and "inherent value" in Q["hc_inherent"]
    assert "caution and reserve" in Q["hc_caution"]
    # twenty-seven years earlier: Chancellor in 1866, the 10% of Chapter 23
    a, b = F["hp_gladstone_cx"]
    assert a <= 1866 <= b
    chk("    twenty-seven years", 1893 - 1866, 27)
    D23, _ = load_snapshot("boe_millennium_bank_rate_1844_1914", parse_dates=["date"])
    chk("    Bank Rate 1866 (Chapter 23's snapshot)", D23.set_index("date").bank_rate.loc["1866"].max(), 10)
    pct("standard silver 1873 (pence)", P[1873], 59.3)
    pct("    1892", P[1892], 39.8)
    chk("standard silver: fine (%)", STANDARD * 100, 92.5)


def world(F, Y, Q, P, E):
    chk("foreign assets / world GDP: 1870 7%; 1900-14 just below 20%", F["ot_7"], [1870, 7, 20, 1900, 1914])
    assert "just below 20 percent" in Q["ot_7"]
    chk("the British share almost (%)", F["ot_80"], [80])
    assert "almost 80 percent" in Q["ot_80"]
    ca = E.ca_gdp.loc[1850:1913]
    assert (E.ca_surplus.loc[1850:1913] > 0).all() and len(ca) == 64                       # 每年都是顺差
    for y, x in [(1872, 8.1), (1877, 0.7), (1890, 7.1), (1902, 0.8), (1913, 9.7)]:
        pct(f"UK current account {y} (% of GDP)", ca[y], x)
    pct("UK net external assets 1870 (% of GDP)", E.nea_gdp[1870], 70, 0)
    pct("    1913", E.nea_gdp[1913], 170, 0)
    # the two peaks of the surplus fall inside Reinhart and Rogoff's two clusters
    assert ca.loc[1850:1880].idxmax() == 1872 and ca.loc[1878:1900].idxmax() == 1890
    for y, (a, b) in zip((1872, 1890), RR_CLUSTERS):
        assert a <= y <= b
    assert "late 1860s up to the mid-1870s" in Q["rr_cluster"] and "mid-1880s through the early 1890s" in Q["rr_cluster"]
    assert "United Kingdom and the United States" in Q["rr_center"] and "precipitously" in Q["rr_sensitive"]
    # the start of the fall of silver
    chk("Karachi, 1 September 1892", F["hr_karachi"], [1, 1892])
    chk("Germany 1872", F["hr_karachi_germany"], [1872])
    assert "France" in Q["hr_karachi_germany"] and "restricted the coinage" in Q["hr_karachi_germany"]
    chk("Giffen: 3 December 1892", F["hr_day8"], [3, 1892])
    chk("    the United States 1873 and 1874", F["hr_giffen"], [1873, 1874])
    assert "Giffen" in Q["hr_giffen_who"] and "Robert Giffen" in column("note")["hr_giffen_who"]
    pre = P.loc[1850:1872]
    assert pre.min() >= 60 and pre.max() < 62.5, (pre.min(), pre.max())                    # 一直值 60 到 62 便士
    chk("Karachi: 60 -> 38-39d; over 35%; 24 -> 14.65d", F["hr_karachi_fall"], [60, 38, 39, 35, 24, 14.65])
    assert "over 35 per cent" in Q["hr_karachi_fall"]
    chk("    24d = two shillings (Naoroji's old basis)", F["nr_shillings"][0] * 12, 24)
    pct("    London 1892 (pence)", P[1892], 39.8)
    # Meissner
    A = adoptions()
    for c, y in [("germany", 1872), ("sweden", 1873), ("denmark", 1873), ("norway", 1873), ("netherlands", 1875),
                 ("france", 1878), ("belgium", 1878), ("switzerland", 1878), ("unitedstates", 1879),
                 ("japan", 1897), ("russia", 1897), ("india", 1899), ("mexico", 1905)]:
        chk(f"Meissner: {c}", A[c], y)
    na = not_adopted()
    chk("    not adopted before 1913", len(na), 13)
    assert {"china", "spain", "austriahungary"} <= set(na)
    assert "exclusively into gold" in Q["me_note"] and "before 1913" in Q["me_dash"]
    assert "sooner" in Q["me_trade"] and "later transition" in Q["me_debt"]


def silver_sec(F, Y, Q, P, E):
    chk("Keynes 1883-1946", F["ws_keynes"], [1883, 1946])
    chk("the rupee: 3/8 oz, 11/12 fine", F["ky_contains"], [3 / 8, 11 / 12])
    chk("    until 1893", F["ky_until"], [1893])
    chk("    fine silver 3/8 x 11/12 = 11/32 oz", float(Fraction(3, 8) * FINE), 11 / 32)
    pct("s (standard ounces)", S_RUPEE, 0.372, 3)
    # data check
    pct("rupee silver value 1873 (pence)", rupee_silver(P[1873]), 22.0)
    pct("    1892", rupee_silver(P[1892]), 14.8)
    H = herschell()
    chk("Herschell: 1873, 1892 (pence)", [H[1873], H[1892]], [22.35, 14.98])
    pct("    above the silver value 1873 (%)", 100 * (H[1873] / rupee_silver(P[1873]) - 1), 1.5)
    pct("    1892 (%)", 100 * (H[1892] / rupee_silver(P[1892]) - 1), 1.2)
    assert "Exchange on Bills on India" in Q["hr_heading"] and "财政年度" in column("note")["hr_heading"]
    chk("Herschell's silver: 59 1/4 (1873), 51 1/4 (1879)", F["hr_silver"], [59.25, 1873, 51.25])
    assert "in 1879" in column("note")["hr_silver"]
    chk("    Lindert 1873, 1879: the same to a hundredth of a penny", [P[1873], P[1879]], [59.25, 51.25], tol=0.01)
    assert "gravely disturbed" in Q["ky_finance"]
    chk("Home charges £19 m or £20 m (万)", [x / WAN for x in F["ky_home"]], [1900, 2000])
    chk("    remitted £15-18 m (万)", [x / WAN for x in F["ky_remit"]], [1500, 1800])
    # ex:periph-rupee
    pct("(1) 1898 silver (pence)", P[1898], 26.93, 2)
    pct("    silver value of the rupee", 0.372 * 26.93, 10.0)
    pct("(2) e 1873", per_pound(H[1873]), 10.74, 2)
    pct("    e 1892", per_pound(H[1892]), 16.02, 2)
    assert min(F["ky_remit"]) <= REMIT <= max(F["ky_remit"])
    pct("(3) rupees 1873 (亿)", REMIT * 10.74 / YI, 1.72, 2)
    pct("    rupees 1892 (亿)", REMIT * 16.02 / YI, 2.56, 2)
    pct("    more (%)", 100 * (16.02 / 10.74 - 1), 49, 0)
    pct("(4) 16 / 10.0 - 1 (%)", 100 * (PAR / 10.0 - 1), 60, 0)
    chk("    'nearly four tenths' not from silver", 1 - 10.0 / PAR, 0.375)
    # the United States
    chk("Sherman Act 1890: oz a year (万)", [F["hr_sherman"][0], F["hr_sherman"][1] / WAN], [1890, 5400])
    pct("world production 1890 (亿 oz)", F["hr_world"][0] / YI, 1.48, 2)
    assert F["hr_sherman"][1] / F["hr_world"][0] > 1 / 3                                    # 三分之一以上
    pct("silver 1889 (pence)", P[1889], 42.7)
    pct("    1890", P[1890], 47.4)
    pct("exchange 1888 (pence)", H[1888], 16.4)
    pct("    1890", H[1890], 18.1)
    pct("    1892: about 15", H[1892], 15, 0)
    # the compare box
    chk("Shibusawa: 1878-1893, exports +260%, imports +70%", F["ms_shib1"], [260, 1878, 1893, 70])
    chk("India 1893, Japan 1897", F["ky_until"] + F["me_japan"], [1893, 1897])


def india(F, Y, Q, P, E, D):
    assert '"Home Charges"' in Q["md_homecharges"] and "railway equipment" in Q["md_items"]
    chk("1911-12: pensions, debt, military (万英镑)", [x / WAN for x in F["ky_1911"]], [500, 1100, 225])
    assert "every Wednesday morning" in Q["ky_wednesday"] and "Bank of England" in Q["ky_wednesday"]
    assert "largest dealers in foreign exchange" in Q["ky_dealer"] and "always positive" in Q["md_positive"]
    chk("Jackson: 26 November 1892", F["hr_day7"], [26, 1892])
    assert "Hong Kong and Shanghai Bank" in Q["hr_jackson"] and "Thomas" in column("note")["hr_jackson"]
    assert "taels" in Q["hr_mexican"] and "Mexican dollars in the South" in Q["hr_mexican"]
    assert "paralyse" in Q["hr_paralyse"]
    J = column("juan")
    assert J["hr_155"].endswith("para. 155") and J["hr_156"].endswith("para. 156")
    chk("the notification: 26 June 1893, 16d.", F["fw_notif"], [26, 1893, PAR])
    # Campbell and Muir
    assert "ROBT. CAMPBELL" in Q["fw_signed"]
    chk("public on 26 June; summary on 7 June", F["fw_public"] + F["fw_purport"], [26, 7])
    assert "continental newspaper" in Q["fw_purport"]
    chk("31 May - 6 June: Rx (万)", [F["fw_bills"][0], F["fw_bills"][1], F["fw_bills"][2] / WAN], [31, 6, 378])
    chk("    bar silver (万英镑)", F["fw_barsilver"][0] / WAN, 118)
    assert "Rx. 1 = 10 卢比" in column("note")["fw_bills"]
    chk("touched 16d. for a day: 27 June", F["fw_27"], [27])
    # Keynes on 1892-1895
    chk("silver 1892-93 nearly 40; 33 1/3; about 29", F["ky_silver40"], [40, 100 / 3, 29])
    assert "what he could get" in Q["ky_unfav"]
    chk("five years", F["fw_five"], [5])
    chk("stable at 16d. by January 1898", F["ky_1898"], [1898, PAR])
    chk("Bank of Bengal: 10% on 6 January 1898, 12% on 24 February", F["fw_bengal"], [10, 6, 1898, 24, 12])
    chk("1s. 3d. = Rs 16 a sovereign instead of 15", F["fw_1s3d"], [16, 15])
    chk("    240 / 15 = 16", per_pound(15), 16)
    chk("the report: 7 July 1899", F["fw_date"], [7, 1899])
    chk("the Act of 1899: the sovereign at 16d.", F["ky_dates1899"], [1899, PAR])
    assert "inconvertible" in Q["ky_inconvertible"] and "unlimited legal tender" in Q["ky_inconvertible"]
    chk("Rothschild before the committee of 1898", [Y["ky_alfred"]], [1898])
    assert "Lindsay scheme" in Q["ky_lindsay"] and "Deputy-Secretary of the Bank of Bengal" in Q["ky_lindsay_who"]
    chk("Lindsay 1876 and 1878", F["ky_lindsay1876"], [1876, 1878])
    # the four provisions and the band
    chk("£1 to 15 rupees", F["ky_15"] + F["ky_convertible"], [15, 15, 1])
    assert "sometimes suspended" in Q["ky_third"] and "vital one" in Q["ky_fourth"]
    chk("Calcutta: not below 15 29/32d.", F["ky_calcutta"], [15 + 29 / 32])
    chk("the ceiling: 16d.; cost seldom over 1/8", F["ky_ceiling"] + F["ky_eighth"], [PAR, 1 / 8])
    chk("1904: 16 1/8 without limit", F["ky_dates1904"], [1904, 16 + 1 / 8])
    chk("1900: the Gold Standard Reserve", F["ky_dates1900"], [1900])
    chk("1908: 15 29/32 in Calcutta", F["ky_dates1908"], [1908, 15 + 29 / 32])
    chk("cost of bringing gold back 3/32", F["ky_back"], [3 / 32])
    c_out, c_back = F["ky_eighth"][0], F["ky_back"][0]
    chk("eq:periph-band: 16 + 1/8", PAR + c_out, 16 + 1 / 8)
    chk("    16 - 3/32 = 15 29/32", PAR - c_back, 15 + 29 / 32)
    chk("    Keynes's extreme limits", F["ky_limits"], [PAR + c_out, PAR - c_back])
    # ex:periph-band
    gold = BAND_RUPEES * (PAR + c_out)
    bill = BAND_RUPEES * float(BID)
    chk("(1) gold: pence", gold, 2_418_750)
    rnd("    £", gold / 240, 10_078, 1)
    chk("    the bill at 16 3/16: pence", bill, 2_428_125)
    chk("    saving (pence)", bill - gold, 9_375)
    rnd("    saving (£)", (bill - gold) / 240, 39, 1)
    low = BAND_RUPEES * (PAR - c_back) / 240
    rnd("(2) at the floor (£)", low, 9_941, 1)
    chk("    at 16d. (£)", BAND_RUPEES * PAR / 240, 10_000)
    pct("    loss (%)", 100 * (1 - low / 10_000), 0.6)
    pct("(3) 1908 silver (pence)", P[1908], 24.38, 2)
    pct("    0.372 x 24.38", 0.372 * 24.38, 9.1)
    assert 0.372 * 24.38 < 0.6 * PAR                                                      # 不到 16 便士的六成
    # the spread of the system
    chk("the Philippines 1903", F["ky_philippines"], [1903])
    assert "Straits Settlements" in Q["ky_westafrica"] and "West African Colonies" in Q["ky_westafrica"]
    assert "prevailing monetary system of Asia" in Q["ky_asia"]
    assert "Great Britain and France" in Q["ky_creditor"] and "Russia and Austria" in Q["ky_russia"]
    chk("Japan 1912: (万英镑)", [Y["ky_japan37"], F["ky_japan37"][0] / WAN], [1912, 3700])
    # Naoroji
    chk("Naoroji 1825-1917", [F["hp_naoroji"][0], F["hp_naoroji"][2]], [1825, 1917])
    chk("    MP for Finsbury Central 1892-1895", [F["hp_naoroji_mp"][1], F["hp_naoroji_mp"][3]], [1892, 1895])
    chk("    the paper of 1876; the draft of 1873", F["nr_1876"] + F["nr_1873"], [1876, 1873])
    chk("    nearly £30 m (万)", F["nr_bleeding"][0] / WAN, 3000)
    chk("    nearer 40 (万)", F["nr_forty"][0] * MILL / WAN, 4000)
    chk("UK 1858-1870: imports above exports by more than (%)", F["nr_uk"] + F["nr_uk25"], [1858, 1870, 25])
    chk("profits 15%", F["nr_mark"], [15])
    X, prof, should = F["nr_exports"][2], F["nr_exports"][4], F["nr_exports"][5]
    debt, rail = F["nr_loans"]
    printed, M = F["nr_imports"]
    chk("X; 15% of X; (1 + pi) X (£ m)", [X / MILL, prof / MILL, should / MILL], [1120, 168, 1288])
    chk("    should be (亿英镑): printed", printed / YI, 14.3)
    rnd("    actual (亿英镑)", M / YI, 9.4, 0.1)
    chk("    kept back (亿英镑)", F["nr_500"][0] / YI, 5)
    rnd("    opium from China (亿英镑)", F["nr_opium"][0] / YI, 1.4, 0.1)
    # ex:periph-naoroji
    H_, DN = drain(X / MILL, M / MILL, (debt + rail) / MILL, 0.15)
    chk("(1) D_N (£ m)", DN, 495)
    chk("    the imports that should have been", (should + debt + rail) / MILL, 1438)
    chk("    printed 1,430: short by", (should + debt + rail - printed) / MILL, 8)
    chk("(2) H", H_, 327)
    chk("    pi X", DN - H_, 168)
    pct("    pi X / D_N (%)", 100 * 168 / 495, 34, 0)
    chk("(3) X - M", (X - M) / MILL, 177)
    rnd("    a year over 38 years (万英镑)", (X - M) / YEARS_NAOROJI / WAN, 470, 10)
    chk("    Maddison 1835-54, 1855-74 (£ m a year)", F["md_t3554"] + F["md_t5574"][:1], [4.5, 7.3])
    chk("(4) railway interest as business (£ m)", F["nr_business"][0] / MILL, 453)
    chk("    1835-39 a year (万英镑)", F["nr_a1835"][2] / WAN, 534.7)
    chk("    1870-72 a year (万英镑)", F["nr_a1870"][1] / WAN, 2740)
    r = F["nr_a1870"][1] / F["nr_a1835"][2]
    assert 5 < r < 5.2, r                                                                  # 增长到原来的 5 倍多
    # the controversy
    chk("Maddison: 190 years", F["md_190"], [190])
    chk("    1.5% of national income, 1921-1938", F["md_15"], [1.5, 1921, 1938])
    assert "a little larger before that" in Q["md_15"]
    chk("    a quarter of savings; a third of private profits", F["md_quarter"] + F["md_third"], [1 / 4, 1 / 3])
    chk("    biggest around the 1880s", F["md_1880s"], [1880])
    chk("    Table 3-3: 1835-54 and 1895-1913 (£ m a year)", F["md_t3554"] + F["md_t9513"][:1], [4.5, 16.8])
    assert "c.i.f." in Q["md_cif"] and "f.o.b." in Q["md_cif"]
    assert "Australia, Canada, the United States" in Q["nr_young"]
    # the letter of 1898
    chk("the letter: 29 May; printed 3 June 1898", F["nr_may29"] + F["nr_times"], [29, 1898, 3, 1898])
    chk("    £20 m (万)", F["nr_20m"][0] / WAN, 2000)
    assert "not an ounce less" in Q["nr_produce"]
    chk("    11d. -> 16d.: 45%", F["nr_45"], [11, PAR, 45])
    pct("    16 / 11", PAR / 11, 1.45, 2)
    chk("    the rayat's Rs 10; 45% more produce", F["nr_rayat"] + F["nr_produce45"], [10, 45])
    chk("    a farthing = 1/4 penny", 1 / 4, 0.25)
    chk("Keynes: the change of 1893", F["ky_prices"], [1893])
    # the famines
    chk("1880: 1877 and 1878", F["f80_period"], [1877, 1878])
    chk("    population (亿); excess deaths (万)", [F["f80_excess"][0] / YI, F["f80_excess"][1] / WAN], [1.9, 525])
    chk("    births fewer (万); total (万)", [F["f80_births"][0] / WAN, F["f80_seven"][0] / WAN], [200, 700])
    chk("    the report of 7 July 1880", F["f80_date"], [7, 1880])
    assert "British Administration" in Q["f80_british"]
    chk("1901: deaths of 1900 more than double", F["f01_double"], [1900])
    d0, d1, ex = F["f01_total"]
    assert d0 / d1 > 2
    chk("    the OCR's total row does not add up: difference", d0 - d1, 1_232_855)
    chk("    printed excess", ex, 1_236_855)
    chk("    the commission: about a million and a quarter (万)", F["f01_quarter"][0] / WAN, 125)
    chk("    one million among British subjects (万)", F["f01_one"][0] / WAN, 100)
    chk("    at least a fifth cholera", F["f01_cholera"], [1 / 5])
    assert "Native States" in Q["f01_immigrants"] and "1876-8 and 1899-1900" in Q["md_famine"]


def china(F, Y, Q, P, E):
    chk("silver back after the mid-1850s", F["at_back"], [1850])
    assert "mid-1850s" in Q["at_back"] and "Daoguang" in Q["ir_returned"] and "Shanghai" in Q["ir_mexican"]
    chk("咸丰八年 = 1858; 30 两 a 百斤", [Y["qs_opium58"], F["qs_opium58"][0]], [1858, 30])
    assert "咸丰八年" in column("year_note")["qs_opium58"] and "与法定约" in Q["qs_opium58"]
    chk("opium imports: 1850s; 1860s; to 1892 (piculs)", F["ir_70000"] + F["ir_63000"] + F["ir_1892"],
        [70000, 63000, 70000, 1892])
    assert "almost doubled every decade" in Q["ir_70000"]
    chk("home grown: 1847 9,000; 1866 16,500; 1876 27,500; 30,000", F["ir_home"],
        [9000, 1847, 16500, 1866, 27500, 1876, 30000])
    chk("光绪九年 = 1883", Y["qs_poison"], 1883)
    assert "光绪九年" in column("year_note")["qs_poison"] and "戒烟会" in Q["qs_society"]
    chk("Naoroji: opium (亿英镑)", F["nr_opium"][0] / YI, 1.41)
    chk("税釐并徵 110 两", F["qs_110"], [110])
    assert "税釐并徵" in Q["qs_combined"] and "进口时输纳" in Q["qs_110"] and "曾纪泽" in Q["qs_zengjize"]
    chk("three years", F["qs_three"], [3])
    chk("光绪十一年 = 1885", Y["qs_reduce"], 1885)
    assert "印度部尚书坚执不允" in Q["qs_reduce"] and "逐年递减" in Q["qs_reduce"]
    chk("India loses over (万英镑) a year", F["qs_india70"][0] / WAN, 70)
    assert "陆续议加税" in Q["qs_raise"]
    chk("光绪三十二年 = 1906; ten years", [Y["qs_1906"], F["qs_1906"][0]], [1906, 10])
    # Campbell and Muir on opium
    chk("Shanghai: 397 taels (1893) -> 556 (1897)", F["fw_opium_tael"], [397, 1893, 556, 1897])
    chk("India: Rs 1,202 -> 1,114 a chest", F["fw_opium_rs"], [1202, 1114])
    chk("exports 1892-93 -> 1897-98 (chests)", F["fw_opium_chests"], [75381, 1892, 56069, 1897])
    assert "enhanced rupee" in Q["fw_opium_rupee"]
    # 张之洞
    chk("光绪二十年 = 1894", Y["qs_zhang"], 1894)
    assert "湖广总督张之洞" in column("note")["qs_zhang_who"] and "铁厂" in Q["qs_zhang_who"]
    pct("1890-1894: silver per pound up (%)", 100 * (P[1890] / P[1894] - 1), 64, 0)
    assert "海防紧急" in Q["qs_zhang_war"]
    # Shimonoseki
    chk("Shimonoseki: 17 April 1895", F["sh_signed"], [17, 1895])
    chk("    2 亿 Kuping taels; eight; 5%", [F["sh_200"][0] / YI, F["sh_eight"][0], F["sh_5pct"][0]], [2, 8, 5])
    assert "silver taels" in Q["ms_sterling2"] and "gold reserves" in Q["ms_reserves"]
    chk("Matsukata 1835-1924", F["ws_matsukata"], [1835, 1924])
    # the case box
    chk("the yen 1871; national banks 1872, notes 1876", F["ms_yen"] + F["ms_1872"], [1871, 1872, 1876])
    chk("the Bank of Japan 1882", F["ms_boj"], [1882])
    chk("silver May 1885, convertible by January 1886", F["ms_silver"], [1885, 1886])
    assert "May 1885" in Q["ms_silver"] and "January 1886" in Q["ms_silver"]
    chk("eleven years", F["ms_eleven"], [11])
    chk("preparations from 1893", F["ms_1893"], [1893])
    chk("the report: 3 July 1895", F["ms_report"], [3, 1895])
    chk("15 members: 7, 6, 2", F["ms_votes"], [15, 7, 6, 2])
    chk("    7 + 6 + 2 = 15", 7 + 6 + 2, 15)
    chk("Shibusawa 1840-1931; left in 1873", F["ms_shib_dates"] + F["ms_shib_bio"], [1840, 1931, 1873])
    assert "First National Bank" in Q["ms_shib_bio"] and "Business leaders" in Q["ms_business"]
    chk("    1878-1893: +260%, +70%", F["ms_shib1"], [260, 1878, 1893, 70])
    chk("March 1897; PM and FM since September 1896", F["ms_march"], [1897, 1896])
    assert "March of 1897" in Q["ms_march"] and "September 1896" in Q["ms_pm"]
    chk("14 to 12; law on 29 March; in force 1 October 1897", F["ms_14"] + F["ms_law"] + F["ms_oct1"],
        [14, 12, 29, 1, 1897])
    chk("nearly 60% of trade with gold countries", F["ms_60"], [60])
    assert "virtually the same" in Q["ky_japan_virtually"]
    # the Boxer Protocol
    chk("signed 7 September 1901", F["bx_signed"], [7, 1901])
    chk("4.5 亿 Haikwan taels", F["bx_450"][0] / YI, 4.5)
    chk("    the 清史稿: 四百五十兆", [F["qs_boxer450"][0], F["qs_argue"][0]], [F["bx_450"][0]] * 2)
    chk("3s. a tael; 39 years; 1902-1940", F["bx_sterling"] + F["bx_39"] + F["bx_1940"], [3, 39, 1902, 1940])
    chk("    1902 to 1940 inclusive", 1940 - 1902 + 1, 39)
    assert "1st of January" in Q["bx_1940"] and "payable in gold" in Q["bx_payable"]
    assert "美旋允" in Q["qs_us"] and "与用金付给无异" in Q["qs_argue"]
    # ex:periph-boxer
    chk("(1) 4.5 亿 x 3s / 20 (万英镑)", F["bx_450"][0] * F["bx_sterling"][0] / 20 / WAN, 6750)
    pct("(2) silver 1901, 1902 (pence)", P[1901], 27.19, 2)
    pct("    ", P[1902], 24.07, 2)
    pct("    fall (%)", 100 * (24.07 / 27.19 - 1), -11.5)
    pct("    more silver for the same gold (%)", 100 * (27.19 / 24.07 - 1), 13.0)
    assert "not yet been carried through" in Q["ky_china"] and Q["me_china"].endswith("---")


def baring(F, Y, Q, P, E, D):
    assert "most famous sovereign debt crisis" in Q["mw_famous"]
    chk("fifth largest", F["mw_fifth"], [5])
    chk("11% of London issues 1884-1890; 40-50% of lending outside the UK 1889", F["mw_11"],
        [11, 1884, 1890, 40, 50, 1889])
    chk("current account deficit 20% of GDP 1884-1889", F["mw_ca"], [20, 1884, 1889])
    assert "totally unprecedented" in Q["mw_taylor"] and "Taylor" in column("note")["mw_taylor"]
    assert "paper standard" in Q["mw_paper"] and "currency mismatch" in Q["mw_mismatch"]
    chk("the Free Banking Law 1887", F["mw_freebanking"], [1887])
    assert "full" in Q["mw_freebanking"] and "amount of the notes issued" in Q["mw_freebanking2"]
    assert "not redeemable in gold" in Q["mw_notred"]
    chk("provincial banks by 1890: more than (万英镑)", [F["mw_30m"][0], F["mw_30m"][1] / WAN], [1890, 3000])
    chk("base 18%, inflation 17%, depreciation 19%, 1884-1890", F["mw_macro"], [18, 17, 19, 1884, 1890])
    chk("40% to debt service; premium 94%", F["mw_debtservice"] + F["mw_94"], [40, 94])
    chk("Terry: 1887, 1888", F["mw_terry"], [1887, 1888])
    assert "former finance minister" in Q["mw_terry_who"] and "Fishlow" in column("note")["mw_terry_who"]
    chk("1889: paid in paper", F["mw_1889"], [1889])
    # London
    chk("Bank Rate 15 March 1888", [rate_on(D, "1888-03-15"), D.loc["1888"].min()], [2, 2])
    chk("    end of 1889", rate_on(D, "1889-12-31"), 6)
    chk("    17 April 1890", rate_on(D, "1890-04-17"), 3)
    chk("    7 November 1890", rate_on(D, "1890-11-07"), 6)
    assert rate_on(D, "1890-11-06") < 6
    D23, _ = load_snapshot("boe_millennium_bank_rate_1844_1914", parse_dates=["date"])
    d23 = D23.set_index("date").bank_rate.loc["1888":"1892"]
    assert d23.equals(D.loc["1888":"1892"]), "Chapter 23's snapshot differs"
    assert "Water Supply and Drainage Loan" in Q["mw_water"] and "early November 1890" in Q["mw_nov"]
    assert "Bank of France" in Q["mw_rescue"] and "Russia" in Q["mw_rescue"]
    chk("default 1890 (万英镑); 60% of the 1890s", [F["mw_48"][0] / WAN, F["mw_48"][1], F["mw_48"][2]],
        [4800, 1890, 60])
    assert "Nathan Rothschild" in Q["mw_rothschild"]
    chk("banking crisis January 1891", F["mw_1891"], [1891])
    chk("real GDP -11% 1890-1891", F["mw_gdp"], [11, 1890, 1891])
    assert "turn of the century" in Q["mw_recover"]
    chk("the president resigned 6 August 1890", F["mw_celman"], [6, 1890])
    assert "current yield on a sterling bond" in Q["mw_spread"]
    chk("a basis point = 0.01 point", 1 / 100, 0.01)
    chk("risk premium 1,400 (1892) -> 800 (1896)", F["mw_1400"], [1400, 1892, 800, 1896])
    # contagion
    chk("more than 15,000 bond prices", F["mw_15000"], [15000])
    assert "Economist" in Q["mw_15000"]
    chk("Latin America: +844, +759, +1,608 bp", F["mw_844"], [844, 759, 1608])
    assert "generally flat" in Q["mw_flat"] and "non-Latin emerging markets" in Q["mw_shift"]
    assert "Barings crisis of 1890" in Q["rr_baring"]
    chk("more than 200 bp higher", F["mw_200"], [200])
    assert "not very important" in Q["mw_fund"] and "trading more with the UK" in Q["mw_ukrisk"]
    assert "safe haven" in Q["mw_haven"]
    # ex:periph-peso
    chk("(1) 100 x 1.94", 100 * (1 + F["mw_94"][0] / 100), 194)
    pct("(2) consol 1892, 1896 (%)", E.consol_yield[1892], 2.67, 2)
    pct("    ", E.consol_yield[1896], 2.30, 2)
    pct("    1892: 2.67 + 14", 2.67 + F["mw_1400"][0] / 100, 16.7)
    pct("    1896: 2.30 + 8", 2.30 + F["mw_1400"][2] / 100, 10.3)
    chk("(3) 844 bp in points", F["mw_844"][0] / 100, 8.44)
    chk("    Bank Rate 17 April -> 7 November 1890 (points)", rate_on(D, "1890-11-07") - rate_on(D, "1890-04-17"), 3)


def test(F, Y, Q, P, E):
    assert "Bordo and Rockoff (1996)" in Q["ot_seal"]
    chk("Obstfeld and Taylor: 1870-1913, 13 countries", F["ot_t4"] + F["ot_13"], [1870, 1913, 13])
    chk("    -57 bp before 1914", F["ot_57"], [1914, 57])
    assert "−57 basis points" in Q["ot_57"]
    chk("    Table 4: OLS -0.30, AR1 -0.57 (points)", [F["ot_gs"][0], F["ot_gs"][2]], [-0.30, -0.57])
    chk("    in basis points", [-100 * F["ot_gs"][0], -100 * F["ot_gs"][2]], [30, 57], tol=1e-6)
    chk("    debt/GDP +10% -> +7.2 bp", F["ot_debt"], [10, 7.2])
    chk("    the consol about 3%", F["ot_consol"], [3])
    chk("Flandreau et al.: 35-55 bp", F["ot_flandreau"], [35, 55])
    chk("Mitchener et al. (citing Obstfeld and Taylor 2003): about 30 bp", F["ms_30bp"], [30])
    assert "Obstfeld and Taylor, 2003" in Q["ms_30bp"]
    assert "no statistically significant" in Q["ot_clemens"]
    chk("Clemens and Williamson (2001): 1870-1913", F["ot_clemens2"], [1870, 1913])
    assert "Clemens and Williamson (2001)" in Q["ot_clemens"] and "skeptical" in Q["ot_skeptical"]
    # Japan
    assert "little evidence" in Q["ms_little"]
    chk("Japan: +30 bp in six months", F["ms_rates30"], [30, 6])
    chk("the Economist 1897: 5 per cent loans", [Y["ms_economist"], F["ms_economist"][0]], [1897, 5])
    chk("1899: ¥1 亿 at 90, 4.45%", [F["ms_1899"][0], F["ms_1899"][1] / YI, F["ms_1899"][2], F["ms_1899"][3]],
        [1899, 1, 90, 4.45])
    chk("less than 10% in London; nearly 45% by the government", F["ms_tepid"] + F["ms_45"], [10, 45])
    assert "Bank of Japan" in Q["ms_45"] and "underwriters" in Q["ms_underwriters"]
    chk("bought back at 86, 4.65%; about 4.8%", F["ms_86"] + F["ms_48"], [86, 4.65, 4.8])
    # ex:periph-yen
    pct("(1) coupon 0.90 x 4.45 (%)", 0.90 * 4.45, 4.0)
    pct("(2) 4 / 86 (%)", 100 * 4 / 86, 4.65, 2)
    pct("(3) consol 1899 (%)", E.consol_yield[1899], 2.38, 2)
    pct("    4.45 - 2.38 (points)", 4.45 - 2.38, 2.07, 2)
    rnd("    = basis points", 100 * (4.45 - 2.38), 207, 1)
    assert 3 < 207 / 57 < 4                                                                # 三倍多
    # the bounty
    assert "bounty to exporters" in Q["ky_bounty"] and "tea, corn, and manufactured cotton" in Q["ky_injure"]
    chk("Darjeeling 1892", F["ky_darjeeling"], [1892])
    assert "expense of other members" in Q["ky_theorists"] and "temporary" in Q["ky_temporary"]
    chk("tea: 115 million lb (亿); doubled by 1909", [F["ky_tea"][0] / YI, F["ky_tea"][1]], [1.15, 1909])
    assert "a little more than doubled" in Q["ky_tea"]
    (y92, y93, y94), y05 = F["ky_yarn92"], F["ky_yarn05"][0]
    rnd("yarn 1892-93 (亿磅)", y92 / YI, 1.9, 0.1)
    rnd("    1893-94 (亿磅)", y93 / YI, 1.3, 0.1)
    rnd("    record 1905-06 (亿磅)", y05 / YI, 3.0, 0.1)
    assert y94 > y93 and "record" in Q["ky_yarn05"] and "inflated year" in Q["ky_yarn92"]
    assert "marked improvement" in Q["ky_yarn08"] and "began very quickly" in Q["ky_china_adjust"]
    assert "wage-paying medium" in Q["fw_cash_wage"]
    chk("copper cash +15% in five or six years", F["fw_cash"], [15])
    assert "five or six years" in Q["fw_cash"] and "less than half" in Q["fw_cash_half"]
    assert "glut of the Chinese market" in Q["ky_glut"] and "Bombay mill" in Q["ky_mill"]
    chk("MSW: silver Japan, gold partner +860%", F["ms_860"], [860])
    assert "luck" in Q["ms_also"]


def legacy_and_box(F, Y, Q, P, E):
    # the deeper box
    a, b = F["nr_exports"][5], sum(F["nr_loans"])
    chk("Naoroji: 1,288 + 150 (£ m)", (a + b) / MILL, 1438)
    chk("    printed 1,430", F["nr_imports"][0] / MILL, 1430)
    chk("the report of 1880: 5 1/4 millions", F["f80_excess"][1], 5.25e6)
    assert "5^" in Q["f80_excess"] and "5¼" in column("note")["f80_excess"]
    chk("the 1901 table: printed total row", F["f01_total"], [2_301_951, 1_069_096, 1_236_855])
    chk("    the commission's words (万)", F["f01_quarter"][0] / WAN, 125)
    chk("the Investors' Monthly Manual: 19 November 1890", F["mw_t1"], [19, 1890])
    assert "1985" in column("note")["ms_shib1"] and "1895" in column("note")["ms_shib1"]
    chk("the Sherman Act and world production: one appendix", [F["hr_sherman"][1], F["hr_world"][0]],
        [54e6, 148_237_091])
    assert column("juan")["hr_sherman"] == column("juan")["hr_world"]
    # the takeaways
    pct("silver in the 1890s below 30d. (1894)", P[1894], 28.9, 1)
    assert P.loc[1873] > 59 and P.loc[1894] < 30
    pct("UK net external assets 1913 (% of GDP)", E.nea_gdp[1913], 170, 0)
    chk("the famines: 525 万 and 125 万", [F["f80_excess"][1] / WAN, F["f01_quarter"][0] / WAN], [525, 125])
    chk("opium: 6-7 万 担 from the 1850s", [F["ir_63000"][0] / WAN, F["ir_70000"][0] / WAN], [6.3, 7])
    chk("Argentina: 4,800 万英镑, -11%", [F["mw_48"][0] / WAN, F["mw_gdp"][0]], [4800, 11])
    chk("the seal: 30 to 57 bp", [F["ms_30bp"][0], F["ot_57"][1]], [30, 57])


def selfcheck(F, P):
    x = rupee_silver(P[1885])
    pct("SC1 silver 1885 (pence)", P[1885], 48.62, 2)
    pct("    0.372 x 48.62", 0.372 * 48.62, 18.1)
    pct("    e", 240 / 18.1, 13.3)
    H = herschell()
    chk("    Herschell 1885", H[1885], 18.25)
    pct("    above the silver value (%)", 100 * (H[1885] / x - 1), 1, 0)
    hi = SC2_RUPEES * (PAR + F["ky_eighth"][0]) / 240
    lo = SC2_RUPEES * (PAR - F["ky_back"][0]) / 240
    rnd("SC2 at 16 1/8 (£)", hi, 6_719, 1)
    rnd("    at 15 29/32 (£)", lo, 6_628, 1)
    rnd("    difference (£)", round(hi) - round(lo), 91, 1)
    pct("    (%)", 100 * (hi - lo) / hi, 1.4)
    pct("    the width of the band (%)", 100 * (F["ky_eighth"][0] + F["ky_back"][0]) / PAR, 1.4)
    Hs, Ds = drain(SC3["X"], SC3["M"], SC3["dL"], SC3["pi"])
    chk("SC3 H; D_N; pi X", [Hs, Ds, Ds - Hs], [15, 25, 10], tol=1e-9)
    t, r = F["fw_opium_tael"], F["fw_opium_rs"]
    pct("SC4 taels up", t[2] / t[0], 1.40, 2)
    pct("    rupees down", r[1] / r[0], 0.93, 2)
    pct("    the rupee against the tael (%)", 100 * ((t[2] / t[0]) / (r[1] / r[0]) - 1), 51, 0)
    pct("SC5 0.372 x 26.93", 0.372 * P[1898], 10.0)
    pct("    16 / 10.0 - 1 (%)", 100 * (PAR / 10.0 - 1), 60, 0)
    assert "non-Latin emerging markets" in quotes()["mw_shift"]


def ending(F, Y, Q, P, E):
    assert "token coin" in Q["ky_token"]
    chk("twenty years later: 1913 - 1893", 1913 - 1893, 20)
    pct("1898: silver (pence)", P[1898], 26.9)
    pct("    the rupee's silver (pence)", rupee_silver(P[1898]), 10, 0)
    chk("    stable at 16d.", F["ky_1898"], [1898, PAR])
    pct("the consol 1873 (%)", E.consol_yield[1873], 3.3)
    pct("    1897 (%)", E.consol_yield[1897], 2.3)
    assert E.consol_yield.loc[1873:1913].idxmin() == 1897


# the life dates the chapter gives without a row of its own, and the same words in an earlier chapter
LIVES = {"John Maynard Keynes，1883—1946": "ch23_goldstandard", "William Ewart Gladstone，1809—1898": "ch23_goldstandard"}
# the cross-references: (words of this chapter, chapter where the event is told, words there)
EVENTS = [("英格兰银行把贴现率提到 10\\%", "ch23_goldstandard", "英格兰银行把贴现率提到 10\\%"),
          ("前财政大臣戈申", "ch23_goldstandard", "戈申"),
          ("英国的物价却在 1873—1896 年跌了下去", "ch23_goldstandard", "1873—1896 年跌了 45\\%"),
          ("1896 年的复本位之争", "ch23_goldstandard", "1896 年：金与银"),
          ("用西非镑这样的新货币取代了它", "ch14_africa", "殖民政府最终用西非镑这样的新货币取代了它"),
          ("印度的手工纺纱败给了英国的机器", "ch21_divergence", "机器是原因"),
          ("道光年间的比价动荡也平息了", "ch17_tokugawa", "道光"),
          ("两是称银子的重量单位", "ch17_tokugawa", "银子按重量称"),
          ("19 世纪 20 年代的违约与独立战争", "ch20_say", "1825")]


def book(F, Q):
    """Life dates, the cross-references, the sources named in tables and captions."""
    t = tex_text()
    for words, ch in LIVES.items():
        assert words in t, words
        assert words in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (words, ch)
    for here, ch, there in EVENTS:
        assert here in t, here
        assert there in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (ch, there)
    J = column("juan")
    # tab:periph-seal: Obstfeld and Taylor pp. 46, 49, 52-53, 55 and Table 4; MW p. 33; MSW pp. 1, 17, abstract
    pages = {J[i] for i in ("ot_seal", "ot_flandreau", "ot_57", "ot_t4", "ot_skeptical", "ot_clemens")}
    assert {re.search(r"p\. (\d+)", p).group(1) for p in pages} == {"46", "49", "52", "53", "55"}, pages
    assert "第 46、49、52—53、55 页与表 4" in t
    assert J["mw_haven"].endswith("p. 33") and "Mitchener 与 Weidenmier（2007）第 33 页" in t
    assert J["ms_30bp"].endswith(", p. 1") and J["ms_rates30"].endswith(", p. 17") and J["ms_little"].endswith("abstract")
    assert "Mitchener、Shizume 与 Weidenmier（2009）第 1、17 页与摘要" in t
    # fig:periph_council
    assert "ch. I §6" in J["ky_calcutta"] and "ch. V §7" in J["ky_ceiling"] and "第一章与第五章" in t
    # fig:periph_world: Meissner Table 1 has no UK
    assert "unitedkingdom" not in adoptions().index and "表里没有英国" in t
    # the people with no dates: written 生卒年未详
    for name in ("Robert Giffen", "Thomas Jackson", "Robert Campbell", "John Muir",
                 "Alfred de Rothschild", "A. M. Lindsay", "José Terry", "Nathan Rothschild"):
        assert f"{name}，生卒年未详" in t, name


def witnesses(F, Q):
    """The notices of the bibliography, and every cited work in it."""
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    start = bib.index("% ---- 第 24 章")
    nxt = bib.find("% ---- 第", start + 1)                   # the next chapter's block, if any
    block = bib[start:nxt if nxt > 0 else bib.index("\\end{thebibliography}")]
    items = {m.group(1): m.group(2) for m in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", block)}
    for key, row in (("obstfeld2002", "ot_notice"), ("meissner2002", "me_notice"),
                     ("mitchener2007", "mw_notice"), ("mitchener2009", "ms_notice")):
        notice = Q[row]
        assert notice.startswith("©") and "All rights reserved" in notice, row
        assert notice.split(".")[0] in items[key], key
        assert "All rights reserved" in items[key], key
    rr = re.search(r"\\bibitem\{reinhart2008tid\}(.*)", bib).group(1)                  # the shared entry
    assert Q["rr_notice"].split(".")[0] in rr
    assert "Institute for Monetary and Economic Studies" in Q["ms_boj_affil"]
    assert "日本银行金融研究所" in items["mitchener2009"]                                  # credit: Bank of Japan
    keys = set(re.findall(r"\\bibitem\{([^}]+)\}", bib))
    cited = {k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", tex_text()) for k in c.split(",")}
    assert cited <= keys, sorted(cited - keys)
    assert set(items) <= cited, sorted(set(items) - cited)
    print(f"ok {len(cited)} works cited, {len(items)} of them in the bibliography block of Chapter 24")


def main() -> None:
    df = _rows()
    F, Y, Q = facts(), years(), quotes()
    P, E, D = silver(), external(), bank_rate()
    check_readings(df)
    check_text(df)
    opening(F, Y, Q, P, E)
    world(F, Y, Q, P, E)
    silver_sec(F, Y, Q, P, E)
    india(F, Y, Q, P, E, D)
    china(F, Y, Q, P, E)
    baring(F, Y, Q, P, E, D)
    test(F, Y, Q, P, E)
    legacy_and_box(F, Y, Q, P, E)
    selfcheck(F, P)
    ending(F, Y, Q, P, E)
    book(F, Q)
    witnesses(F, Q)
    anchors("zh/ch24_periphery.tex", df["id"], script=Path(__file__))


if __name__ == "__main__":
    main()
