"""Chapter 34 (战争财政、功能财政与布雷顿森林的设计): every number and every quotation in zh/ch34_warfinance.tex.

    python3 checks/check_ch34.py

Inputs:
  warfinance_facts   quotations of Keynes, How to Pay for the War (1940; the Digital Library of India's copy on
                     archive.org) and its metadata, of the Commons debate of 7 April 1941 (Sir Kingsley Wood's Budget
                     speech) and the Lords debate of 23 May 1944 (International Monetary Fund), of Lerner (Social
                     Research, February 1943), Kalecki (The Political Quarterly, October-December 1943) and Domar
                     (American Economic Review, December 1944), of the Federal Reserve Bulletin of June 1943 (the White
                     and Keynes plans) and September 1944 (Goldenweiser and Bourneuf), of the Senate hearings of June
                     1945, the Annual Report of the Board of Governors for 1942, Harrison (1992, 1998), the Famine
                     Inquiry Commission's Report on Bengal (1945), the judgment of the International Military Tribunal
                     and Nazi Conspiracy and Aggression vol. II, Shizume (2009), Ide (2003), the Bank of Japan's
                     chronology and the authority records of the Library of Congress, the Bibliotheque nationale de
                     France and the Deutsche Nationalbibliothek (checked by data/fetch/verify_web_quotes.py); the rows
                     with an empty quotation are values and words read on page images (Keynes's pp. vi, 15, 16, 23, 28
                     and 32, Domar's pp. 799, 803, 810 and 811, the Final Act, p. 14 of the Annual Report, p. 110 of the
                     Famine Inquiry Commission's report, the table of federal finances in Historical Statistics), with a
                     transcription between « and » in the note
  boe_millennium_gb_1913_1950   British central government expenditure and receipts (financial and calendar years),
                                the national debt and consumer prices (BoE A27, A29, A47)
  bea_nipa_annual, depressionus_annual   Chapter 2's and Chapter 28's annual tables: US nominal and real GDP; the
                                         unemployment rate of 1941
  islm_facts   Chapter 33's reading of series Y 339-341, a second reading of fiscal years 1939-1941
The figure module figsrc/fig_ch34.py imports its data and the teaching models from here.

What is checked here:
  1. readings   every number of the value column of warfinance_facts is read from its quotation (digits, English
                number words, vulgar fractions, 'twice', 'trebled', 'one-half', 'goo' for 900, '3*5' for 3·5); a row
                read on a page image is read from its transcription
  2. the text   every “…” of the chapter is the chapter's rendering of a quotation (TRANSLATIONS), with the source's
                words listed in KEYWORDS (for a row read on a page image, the words of its transcription)
  3. numbers    every number of the text, section by section: said() finds the phrase and compares each number it
                prints with the value read from the snapshots or computed from the teaching models, within half a unit
                of the last printed digit; Chinese numerals are read by zh()
  4. coverage   every Arabic number of the text (outside labels, citations, cross-references, the key equations,
                math sub- and superscripts and the numbers of the parts of an example) lies inside a phrase checked
                by said()
  5. the book   the models' equations, life dates, what other chapters tell, second witnesses, the bibliography block
                of the chapter and its licence notices
  6. anchors    the paraphrase anchors `% 据: ...` name rows of warfinance_facts

The teaching models:
  the inflationary gap (eq:warfinance-gap), Chapter 32's cross M1 (a = 26, c = 0.6, I = 10) turned round at capacity
      gap = a + c(Ybar - T - D) + I + G - Ybar,   gap = 0 <=> T + D = Ybar - (Ybar - a - I - G)/c
      with Ybar = 100 and peace G = T = 10 (gap 0, Y = 100); war G = 30; self-check G = 25
  Domar's limits (eq:warfinance-domar), with income Y0 e^{rt} and debt D0 + a Y0 (e^{rt} - 1)/r:
      D/Y -> a/r, tax rate iD/(Y + iD) -> i/(r/a + i); Domar's a = 6%, i = 2%, r = 2% and 3%, D0 = 300, Y0 = 130
  the charges of the two plans (ex:warfinance-bancor): Keynes 1% above a quarter and 1% above a half of the quota on
      a credit or debit balance; White 1% in gold on the Fund's holdings above the quota; quota 400, balances 250
  the votes of Bretton Woods: 250 + 1 per $100,000 of quota, Schedule A
The cross's parameters are Chapter 32's M1, imported from check_ch32.py as check_ch33.py does (the shared
checks/teaching_params.py of docs/PLAN.md is deferred by the editor).
"""
from __future__ import annotations

import math
import os
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from check_ch32 import M1, PENCE, SHILLINGS
from common import ROOT, anchors, load_snapshot, quoted

TEX = Path(os.environ.get("CH34_TEX", ROOT / "zh" / "ch34_warfinance.tex"))   # a scratch copy for mutation tests
GUIDE = "战争证明政府“付得起”，和平时期也一样吗？战后的国际货币体系应该怎样设计？"
PREV = "战争证明政府“付得起”，和平时期也一样吗？"       # Chapter 33's NEXT, the first half of the question
NEXT = "被压抑的通胀怎样一夜消失？"                      # Chapter 35's question
# Teaching inputs stated in the text
GAP = {"Ybar": 100, "G0": 10, "T0": 10, "Gw": 30, "Tw": 30, "Gs": 25}       # ex:warfinance-cross, self-check 1
DOMAR_SC = {"a": 0.06, "i": 0.03, "r": 0.02}                                 # self-check 4
BANCOR = {"quota": 400, "balance": 250, "excess": 150, "sc": 150}            # ex:warfinance-bancor, self-check 6
VOTES = {"base": 250, "per": 100_000}                                        # Articles of Agreement, as Bulletin
MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"], 1)}


def chk(what: str, value, expected=None, tol: float = 1e-6, rel: float = 0.0) -> float:
    """quoted() with a tolerance for floating-point error and for the six decimals of the value column; a list is
    compared element by element."""
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
    df, m = load_snapshot("warfinance_facts", dtype=str, keep_default_na=False)
    assert 34 in m["used_in"] and m["fetch"] == "data/fetch/warfinance34.py"
    assert df["id"].is_unique
    return df


@lru_cache(maxsize=None)
def meta() -> dict:
    return load_snapshot("warfinance_facts")[1]


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
    """The month `name`, asserted to be in what row rid says (or in its source's version)."""
    assert name.lower() in words_of(rid).lower(), (rid, name)
    return MONTHS[name.lower()]


def src_mon(key: str, name: str) -> int:
    """The month `name`, asserted to be in the version line of source `key`."""
    assert name in meta()["sources"][key]["version"], (key, name)
    return MONTHS[name.lower()]


def page(rid: str) -> int:
    """The first page number of a row's juan column: 'p. 15 (PDF p. 24)' -> 15."""
    return int(re.search(r"pp?\. (\d+)", column("juan")[rid]).group(1))


def url_date(key: str) -> tuple[int, int, int]:
    """The date in a Historic Hansard URL: .../commons/1941/apr/07/... -> (1941, 4, 7)."""
    y, m, d = re.search(r"/(\d{4})/([a-z]{3})/(\d\d)/", meta()["sources"][key]["url"]).groups()
    return int(y), next(i for k, i in MONTHS.items() if k.startswith(m)), int(d)


def rise(a: float, b: float) -> float:
    return 100 * (b / a - 1)


@lru_cache(maxsize=None)
def boe() -> pd.DataFrame:
    """British central government finance, the national debt and consumer prices, 1913-1950, indexed by year (the row
    of year y carries the financial year y/y+1 and the calendar year y)."""
    df, m = load_snapshot("boe_millennium_gb_1913_1950")
    assert 34 in m["used_in"] and m["fetch"] == "data/fetch/boe_millennium_gb34.py"
    assert list(df.year) == list(range(1913, 1951)) and df.notna().all().all()
    assert (df.fy == [f"{y}/{(y + 1) % 100:02d}" for y in df.year]).all()
    return df.set_index("year")


def fy_share(first: int, last: int) -> float:
    """Receipts as a per cent of expenditure, summed over the financial years first/first+1 .. last/last+1."""
    b = boe().loc[first:last]
    return 100 * b.fy_receipts_gbp_mn.sum() / b.fy_expenditure_gbp_mn.sum()


@lru_cache(maxsize=None)
def nipa() -> pd.DataFrame:
    df, m = load_snapshot("bea_nipa_annual")
    assert "A191RC gdp" in m["series"] and "A191RX gdp_real_2017" in m["series"]
    return df.set_index("year")


@lru_cache(maxsize=None)
def annual() -> pd.DataFrame:
    df, m = load_snapshot("depressionus_annual")
    assert "D 85-86" in m["series"]
    return df.set_index("year")


CY = ("cy_1939", "cy_1940", "cy_1941", "cy_1942", "cy_1943", "cy_1944", "cy_1945", "cy_1946", "cy_1947", "cy_1948",
      "cy_1949", "cy_1950")                                                   # Y 339-342, one row a fiscal year


def budget() -> pd.DataFrame:
    """Historical Statistics, Y 339-342: receipts, outlays, surplus or deficit and total gross federal debt, billion
    dollars, fiscal years 1939-1950 (ending June 30); receipts - outlays = surplus within 0.1 (each rounded)."""
    F = facts()
    rows = [F[k] for k in CY]
    df = pd.DataFrame(rows, columns=["year", "receipts", "outlays", "surplus", "debt"]).astype({"year": int})
    df = df.set_index("year")
    assert list(df.index) == list(range(1939, 1951))
    assert ((df.receipts - df.outlays - df.surplus).abs() <= 0.1 + 1e-9).all()
    for y in df.index:
        assert transcription(f"cy_{y}").startswith(f"{y} |")
    return df


def debt_ratio() -> pd.Series:
    """The federal debt at the end of each fiscal year over the GDP of that calendar year, per cent (the book's
    calculation); BEA GDP is in million dollars."""
    B, N = budget(), nipa()
    return 100 * B.debt * 1e3 / N.gdp.loc[B.index]


def quotas() -> dict[str, float]:
    """Schedule A of the Final Act: member -> quota, million dollars (Denmark '*', no figure)."""
    tr = transcription("fa_quotas")
    out = {}
    for item in tr.split("dollars)", 1)[1].split("|"):
        name, q = item.strip().rsplit(" ", 1)
        if q != "*":
            out[name] = float(q)
    assert list(out.values()) == facts()["fa_quotas"], "Schedule A: the transcription and the value column differ"
    assert "Denmark *" in tr and len(out) == 44
    return out


def votes(q_mn: float) -> float:
    """Votes of a member with a quota of q_mn million dollars: 250 plus one for each $100,000."""
    return VOTES["base"] + q_mn * 1e6 / VOTES["per"]


# ---------------------------------------------------------------------------------------------------
# The teaching models
def gap(G: float, T: float, D: float = 0.0, Ybar: float = GAP["Ybar"], a: float = M1["a"], c: float = M1["c"],
        I: float = M1["I"]) -> float:
    """eq:warfinance-gap: planned spending at capacity minus capacity."""
    return a + c * (Ybar - T - D) + I + G - Ybar


def closing(G: float, Ybar: float = GAP["Ybar"], a: float = M1["a"], c: float = M1["c"], I: float = M1["I"]) -> float:
    """T + D that closes the gap (eq:warfinance-gap)."""
    return Ybar - (Ybar - a - I - G) / c


def cross(G: float, T: float, D: float = 0.0) -> dict[str, float]:
    """The spending line a + c(Y - T - D) + I + G = intercept + cY, and its equilibrium."""
    a, c, I = M1["a"], M1["c"], M1["I"]
    b0 = a - c * (T + D) + I + G
    return dict(b0=b0, c=c, Y=b0 / (1 - c), at=b0 + c * GAP["Ybar"], gap=gap(G, T, D))


def model() -> dict[str, dict[str, float]]:
    """The numbers of ex:warfinance-cross, the figure and the self-check."""
    G0, T0, Gw, Tw, Gs = GAP["G0"], GAP["T0"], GAP["Gw"], GAP["Tw"], GAP["Gs"]
    peace, war, taxed = cross(G0, T0), cross(Gw, T0), cross(Gw, Tw)
    D = gap(Gw, Tw) / M1["c"]
    deferred = cross(Gw, Tw, D)
    Ts = closing(Gw)
    sc = cross(Gs, T0)
    return dict(peace=peace, war=war, taxed=taxed, deferred=deferred, D=dict(D=D), Ts=dict(T=Ts), sc=sc,
                scD=dict(D=gap(Gs, T0) / M1["c"], TD=closing(Gs)))


def domar(a: float, i: float, r: float, t: float = math.inf, D0: float = 300, Y0: float = 130) -> dict[str, float]:
    """Domar's model in continuous time: income Y0 e^{rt}, the government borrows a Y; debt D0 + aY0(e^{rt} - 1)/r. At
    t = inf the limits a/r and i/(r/a + i). Billions of dollars and fractions."""
    if math.isinf(t):
        ratio = a / r
    else:
        g = math.exp(r * t)
        ratio = (D0 + a * Y0 * (g - 1) / r) / (Y0 * g)
    return dict(ratio=ratio, tax=i * ratio / (1 + i * ratio))


def keynes_charge(balance: float, quota: float) -> float:
    """The Clearing Union: 1% on the average balance (credit or debit) above a quarter of the quota, another 1% above
    a half."""
    b = abs(balance)
    return 0.01 * max(0.0, b - quota / 4) + 0.01 * max(0.0, b - quota / 2)


def white_charge(excess: float) -> float:
    """The Stabilization Fund: 1% a year in gold on the Fund's holdings of a member's currency above its quota."""
    return 0.01 * max(0.0, excess)


# ---------------------------------------------------------------------------------------------------
# 1. Readings of the numbers (the same rules as the script that wrote the snapshot)
SMALL = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "twelve": 12, "fifteen": 15}
TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
MULT = {"thousand": 10 ** 3, "million": 10 ** 6, "billion": 10 ** 9}
WORDS = {"twice": 2, "double": 2, "trebled": 3, "tenfold": 10, "one-half": 0.5, "half": 0.5, "a third": 1 / 3,
         "one third": 1 / 3, "one quarter": 0.25, "three quarters": 0.75, "two-fifths": 0.4, "four-fifths": 0.8,
         "one-fourth": 0.25, "three-fourths": 0.75, "half a million": 5e5, "three quarters of a million": 7.5e5,
         "goo": 900, "a quarter": 0.25}


def cardinal(s: str) -> float:
    """An English cardinal: 'three', 'forty-four', 'seventy-two'."""
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
    """'1,600,000,000', '10.5', '.5'."""
    return float(s.replace(",", ""))


def frac(s: str) -> float:
    """'17½', '1⅛', '⅜': an integer part and a vulgar fraction."""
    whole = s[:-1]
    return (float(whole) if whole else 0.0) + unicodedata.numeric(s[-1])


FIGURES = re.compile(r"\d[\d,]*(?:\.\d+)?|\.\d+")
EN, NUM, WD, FR = "en", "num", "word", "frac"
# id -> [(phrase, how)], in order. A phrase 'context|word' is searched as a whole and read from `word`. Rows not
# listed are read with all the figures of the quotation.
READINGS = {
    "k_times": [("three", EN)],
    "k_unemp": [("six", EN)],
    "km_date": [("1940", NUM)],
    "h41_short": [("1⅛", FR), ("2", NUM)],
    "h41_third": [("a third", WD)],
    "h41_1600": [("1,600,000,000", NUM), ("one-half", WD)],
    "h41_double": [("double", WD)],
    "h41_half": [("250,000,000", NUM), ("one-half", WD)],
    "h41_halftax": [("half", WD)],
    "hl44_motion": [("6519", NUM)],
    "ln_four": [("four", EN)],
    "ln_twice": [("twice", WD)],
    "ln_guess": [("100", NUM), ("goo", WD)],
    "kl_three": [("three", EN)],
    "kl_masthead": [("No. |4", NUM), ("1943", NUM)],
    "fj_april6": [("April |6", NUM), ("1943", NUM)],
    "fw_votes": [("100", NUM), ("plus |1", NUM), ("100,000", NUM), ("(|1", NUM)],
    "fw_fourth": [("one-fourth", WD)],
    "fk_quota": [("three", EN), ("75", NUM)],
    "fk_charge": [("1", NUM), ("1", NUM)],
    "fs_44": [("forty-four", EN)],
    "fs_1pct": [("one", EN)],
    "fs_votes": [("250", NUM), ("one", EN), ("100,000", NUM)],
    "fs_halfus": [("one-half", WD)],
    "hw_germany": [("one quarter", WD)],
    "hw_japan": [("1944", NUM), ("three quarters", WD)],
    "hu_money": [("trebled", WD)],
    "hu_supply": [("1943", NUM), ("one third", WD)],
    "hu_kolkhoz": [("ten", EN), ("1943", NUM)],
    "hu_weapons": [("1943", NUM), ("17", NUM), ("40", NUM), ("tenfold", WD)],
    "hu_wage": [("1945", NUM), ("half", WD)],
    "hu_nkvd": [("three quarters of a million", WD), ("1940", NUM), ("half a million", WD), ("1943", NUM)],
    "hu_goskomstat": [("26", NUM), ("27", NUM)],
    "hu_leningrad": [("one million", EN), ("two-fifths", WD)],
    "hf_three": [("three", EN)],
    "hf_70": [("70", NUM), ("half", WD)],
    "hf_short": [("one third", WD), ("5", NUM), ("1956", NUM), ("223", NUM)],
    "hf_imports": [("1940", NUM), ("one third", WD), ("one quarter", WD)],
    "hf_ww1": [("doubled", "twice"), ("trebled", WD)],
    "fm_between": [("one", "million"), ("two million", EN)],
    "fm_prices": [("five", EN), ("six", EN), ("1942", NUM)],
    "fm_35": [("1943", NUM), ("3*|5", "ocr35")],
    "sn_taft": [("2,750,000,000", NUM), ("half", WD), ("30", NUM)],
    # rows whose value the snapshot's script gave by hand: read here as the words of the source say them
    "fw_rates": [("four-fifths", WD)],
    "fw_unitas": [("137", "seventh"), ("$|10", NUM)],
    "fk_quarter": [("a quarter", WD)],
    "fs_service": [("three-fourths", WD)],
    "imt_sauckel": [("March |1", NUM), (",|1944", NUM), ("5,000,000", NUM), ("200,000", NUM)],
}
IMG_FIGURES = re.compile(r"(-?)(\d[\d,]*(?:\.\d+)?|\.\d+)")
IMG_READINGS = {
    "k_output": [("15", NUM), ("20", NUM), ("17½", FR), ("£|825", NUM), ("£|150", NUM), ("£|300", NUM),
                 ("£|450", NUM), ("£|350", NUM)],
    "k_allowance": [("5", NUM), ("fifteen", EN), ("100,000,000", NUM)],
    "fa_change": [("ten", EN), ("ten", EN), ("seventy-two", EN)],
    "ar_bills": [("twelve", EN), ("⅜", FR)],
    "fm_15": [("1·5", "middot")],
    "dm_3and2": [("approach |3", NUM), ("r = |2", NUM), ("and |2", NUM), ("r = |3", NUM), ("5.7", NUM), ("3.9", NUM)],
}
# the misreadings of the OCR, each named in the note of its row and printed in the quotation
MISPRINTS = [("h41_gapdef", "inedaquacy"), ("h41_halftax", "practicaly"), ("h41_45s", "45s. a. week"),
             ("h41_short", "1⅛per"), ("ln_guess", "goo"), ("ln_rejects", "“‘sound finance”"), ("ln_nations", "r owed"),
             ("kl_byline", "Kaveckt"), ("kl_lecture", "toa"), ("kl_confidence", "finance ”"),
             ("kl_cycle", "“ political"), ("fw_unitas", "137 |"), ("fk_ultimate", "ha/f"), ("fs_65", "unti]"),
             ("fm_35", "3*5"), ("fm_unsound", "cannot he"), ("imt_clearing", "account7'"),
             ("imt_poland", "rnthlessness"), ("imt_food", "Genera1"), ("imt_east", "mas not"),
             ("imt_quotas", "thein"), ("imt_plunder", "t o enlarge")]
NAMED = {"ln_rejects": "doubles the opening quotation mark", "kl_confidence": "space before the closing",
         "kl_cycle": "space after the opening", "fm_unsound": "'he'", "imt_east": "'mas'", "imt_plunder": "'t o'",
         "ln_nations": "'r'"}
IMAGE_NOTE = "read on the page image"


def read(word: str, how: str) -> list[float]:
    if how == NUM:
        return [figure(word)]
    if how == EN:
        return [cardinal(word)]
    if how == WD:
        return [WORDS[word]]
    if how == FR:
        return [frac(word)]
    if how == "twice":                          # 'doubled'
        return [2.0]
    if how == "ocr35":                          # '3*5': the OCR's reading of 3·5
        return [3.5]
    if how == "million":                        # 'one' of 'one and two million'
        return [cardinal(word) * 1e6]
    if how == "middot":                         # '1·5', the decimal point of the report
        return [1.5]
    if how == "seventh":                        # '137 |': the OCR's reading of 137 1/7 (named in the row's note)
        return [figure(word) + 1 / 7]
    raise ValueError(how)


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
    quoted("rows with values, each read from its quotation", n, 123)
    quoted("rows read on a page image (no quotation)", img, 37)
    N, Q = column("note"), quotes()
    for rid, word in MISPRINTS:
        assert word in Q[rid], (rid, word)                  # printed in the quotation
        named = NAMED.get(rid, word)
        assert named in N[rid], (rid, named)                # and named in the note
    # the misreadings of the pages read on images, as their notes name them
    for rid, ocr in (("k_output", "'16'"), ("k_output", "'£160'"), ("k_spending", "'£226'"), ("k_money", "'£1,360'"),
                     ("k_taxes", "'£600'"), ("k_allowance", "'Sa.'"), ("ar_bills", "'Vs'"), ("fm_15", "'15'")):
        assert ocr in N[rid], (rid, ocr)


# ---------------------------------------------------------------------------------------------------
# 2. Every “…” of the text against the snapshot
# the chapter's Chinese renderings of the quotations: rendering -> row (or rows)
TRANSLATIONS = {
    # opening
    "强制储蓄": "k_times",
    "一个自由的社会要为战争组织起来，并不容易。": "k_free",
    "蛋糕的大小是固定的": "k_cake",
    "已经不是需求不足造成的": "k_nolonger",
    # sec:warfinance-world
    "借同样一笔钱，纳税人的总成本大约是上一次大战时的三分之一": "h41_third",
    "百分之三的战争": "hf_three",
    "就像洪水足够大时会冲垮堤坝一样": "h41_torrent",
    "要避开这个威胁，我们必须有一道结实、造得好的坝": "h41_dam",
    # sec:warfinance-gap
    "要反复敲打的结论": "k_hammer",
    "让通胀来当收税人": "k_taxgatherer",
    "是空想": "k_taxes",
    "格外不公平、低效，又惹人恼火": "k_shortage",
    "自然的补救": "k_nature",
    "支配推迟消费的权利": "k_wealth",
    "采取延期支付的形式": "k_deferred",
    "只有在自由的社会里，政府的任务才因为社会公正的要求而复杂起来。": "k_justice",
    "在一个奴隶国家，生产是唯一的问题。": "k_slave",
    # sec:warfinance-budget
    "头等重要的是避免任何通胀缺口，我指的是财政措施达不到避免严重而持续的通胀所需要的那部分": "h41_gapdef",
    "借款本身既不一定、通常也不会带来通胀": "h41_borrowing",
    "在 5 亿英镑的量级": "h41_500",
    "限制各种可买物资数量的种种办法，本身就应当有利于每个有收入的人真正地多储蓄": "h41_limit",
    "这些建议首要的目的，不在于为征税而征税，也不在于为收入而收入，而在于在战时大大削减购买力": "h41_purpose",
    "战争继续期间，纳税人不得要求或动用他的抵免": "h41_noclaim",
    "中途站": "hf_halfway",
    "我今年要靠税收筹集差不多一半": "h41_halftax",
    # sec:warfinance-us
    "在战争期间让政府债券的价格与收益率保持在接近现有的水平": "ar_peg",
    "尽可能少地依靠新增的银行信用": "ar_aim",
    # sec:warfinance-compare
    "特别移民": "hu_nkvd_who",
    "2600 万到 2700 万": "hu_goskomstat",
    "征用的方式与这些国家的经济资源完全不成比例，结果是饥荒、通胀与活跃的黑市": "imt_requisition",
    "蓄意的掠夺": "imt_deliberate",
    "无论如何不会是在德国": "imt_famine",
    "千百万人会被饿死": "imt_starved",
    "公共与私人的财产被有计划地抢掠，以欧洲其余地方为代价扩大德国的资源": "imt_plunder",
    "自愿来的连 20 万都不到": "imt_sauckel",
    "1943 年稻米供应的短缺是饥荒的根本原因之一": "fm_rice",
    "本来是可以防止的": "fm_prevented",
    "所用的调查方法，无法认为在统计上是可靠的": "fm_unsound",
    # sec:warfinance-lerner
    "功能财政": "ln_name",
    "什么特别的好坏": "ln_neither",
    "征税决不应该只因为政府需要付钱": "ln_tax",
    "健全财政": "ln_rejects",
    "合理的": "ln_hansen",
    "完全荒唐的夸张": "ln_exaggeration",
    "不管谁来拉操纵杆": "ln_levers",
    # sec:warfinance-debate
    "绥靖": "ln_appeasement",
    "私人企业的经济崩溃": "ln_collapse",
    "非常粗略地": "ln_guess",
    "债务负担": "dm_title",
    "前景相当暗淡": "dm_picture",
    "信心的状态": "kl_confidence",
    "解雇": "kl_sack",
    "在法西斯主义下，没有下一届政府": "kl_nonext",
    "军备经济": "kl_armament",
    "政治的商业周期": "kl_cycle",
    # sec:warfinance-plans
    "两国政府都没有承诺接受本国专家提出的建议": "fj_committed",
    "比如说，叫班科": "fk_bancor",
    "开辟新的领域": "fk_new",
    "并不是绝对必要的": "fk_notessential",
    "用的是同样挑剔的眼光": "fk_critical",
    "但最后的决定权留在自己手里": "fk_ultimate",
    "只有在纠正根本性的失衡所必需时，才考虑改变": "fw_rates",
    "不论份额多大，任何国家都无权投出超过总票数四分之一的票": "fw_fourth",
    # sec:warfinance-bw
    "清算同盟方案里某些优雅、清晰与合乎逻辑的特点，确实已经不见了": "hl44_elegance",
    "死掉的是那条狗": "hl44_dog",
    "一份铁的配给": "hl44_iron",
    "明确地放在了债权国身上": "hl44_creditor",
    "英镑的对外价值要服从由我们自己的国内政策决定的对内价值，而不是反过来": "hl44_sterling",
    "过去的异端，如今被认可为正统": "hl44_heresy",
    "黄金是野蛮的遗物": "hl44_relic",
    "我们将在它的重压下蹒跚而行": "hl44_stagger",
    "丹麦驻美国公使以个人身份出席": "fs_denmark",
    "根本性的失衡": "fa_change",
    "不得因为提议改变的成员国国内的社会或政治政策而反对": "fa_policies",
    "稳定不等于僵硬，过去的僵硬造成了极端的不稳定": "fs_rigidity",
    "成员国可以实行管制国际资本流动所必需的管制": "fa_capital",
    "异端": "hl44_heresy",
    "严重的威慑": "fs_deterrent",
    "归根到底，这种稀缺只能靠那个国家恢复出口与进口之间的平衡来消除": "fs_end",
    "英联邦的投票权与美国的投票权预计会大致相等": "hl44_voting",
    "我们的投票权与我们拿出的钱正好成比例": "sn_acheson",
    "你的整个态度，在经济上、政治上，在我看来都是错的": "sn_wrong",
    "不附任何条件": ("sn_string", "sn_white"),
    "每一方其实都是另一方不可避免的伴随物": "fk_critical",
    "我想象不到这项制裁真会被允许生效": "hl44_sanction",
    "随时能够帮助任何成员国应付国际收支的暂时赤字，给它时间纠正失调": "fs_purpose",
    # the ending
    "双重的福分": "k_twice",
}
# the words of the source that each rendering translates
KEYWORDS = {
    "k_times": ["“Compulsory Savings”"],
    "k_free": ["It is not easy for a free community to organise for war."],
    "k_cake": ["But in war time the size of the cake is fixed."],
    "k_nolonger": ["It is no longer caused by a deficiency of demand."],
    "h41_third": ["the gross cost to the taxpayer of borrowing a given sum has been about a third of what it was in the "
                  "last war"],
    "hf_three": ["“three per cent war.”"],
    "h41_torrent": ["just as a torrent will sweep away a dam if it develops sufficient force"],
    "h41_dam": ["To avert that menace, it is vital for us to possess a stout and well-constructed dam."],
    "k_hammer": ["That is the conclusion to hammer home."],
    "k_taxgatherer": ["the use of inflation as a tax-gatherer"],
    "k_taxes": ["by voluntary savings without any aid from inflation is chimerical"],
    "k_shortage": ["a singularly unfair, inefficient and irritating method of restricting consumption"],
    "k_nature": ["nature’s remedy"],
    "k_wealth": ["command of the right to postponed consumption"],
    "k_deferred": ["must take the form of deferred pay"],
    "k_justice": ["it is only in a free community that the task of government is complicated by the claims of social "
                  "justice"],
    "k_slave": ["In a slave state production is the only problem."],
    "h41_gapdef": ["What is of the first importance is the avoidance of any inflationary gap, by which I mean any "
                   "inedaquacy in our financial measures below what is required to enable us to avoid serious and "
                   "continuing inflation."],
    "h41_borrowing": ["Borrowing as such is neither necessarily nor normally inflationary."],
    "h41_500": ["is of the order of £500,000,000"],
    "h41_limit": ["to limit the quantity of supplies of various kinds available for purchase should in itself be "
                  "favourable to genuine increased saving by every recipient of income"],
    "h41_purpose": ["the primary object of these proposals is not to obtain taxation for taxation sake, nor to raise "
                    "Revenue for the sake of Revenue, but to make a considerable cut in purchasing power during the war"],
    "h41_noclaim": ["the taxpayer cannot claim or use his credit while the war continues."],
    "hf_halfway": ["halfway house between pure taxation and voluntary lending to government"],
    "h41_halftax": ["I shall be raising this year practicaly half by taxation"],
    "ar_peg": ["to maintain prices and yields on Government securities close to existing levels for the duration of "
               "the war"],
    "ar_aim": ["to depend as little as possible on the creation of additional bank credit"],
    "hu_nkvd_who": ["“special settlers”"],
    "hu_goskomstat": ['"26-27 million"'],
    "imt_requisition": ["out of all proportion to the economic resources of those countries, and resulted in famine, "
                        "inflation, and an active black market"],
    "imt_deliberate": ["economic exploitation became deliberate plunder."],
    "imt_famine": ["it shall in no case be in Germany"],
    "imt_starved": ["even if \"many millions of people will be starved to death.\""],
    "imt_plunder": ["Public and private property was systematically plundered and pillaged", "Germany a t the expense "
                    "of the rest of Europe"],
    "imt_sauckel": ["not even 200,000 came voluntarily"],
    "fm_rice": ["Shortage in the supply of rice in 1943 was one of the basic causes of the famine."],
    "fm_prevented": ["could have been prevented"],
    "fm_unsound": ["The method of investigation followed cannot he accepted as statisti"],
    "ln_name": ["we may call Functional Finance"],
    "ln_neither": ["anything especially good or bad"],
    "ln_tax": ["taxing is never to be undertaken merely because the government needs to make money payments."],
    "ln_rejects": ["sound finance"],
    "ln_hansen": ["as long as there is a reasonable"],
    "ln_exaggeration": ["A completely fantastic exaggeration"],
    "ln_levers": ["no matter who pulls the levers"],
    "ln_appeasement": ["This unnecessary “appeasement”"],
    "ln_collapse": ["the private enterprise economy collapses"],
    "ln_guess": ["in the very roughest manner"],
    "dm_title": ["“BURDEN OF THE DEBT”"],
    "dm_picture": ["The picture is rather dismal."],
    "kl_confidence": ["“state of confidence.”"],
    "kl_sack": ["“the sack”"],
    "kl_nonext": ["Under Fascism there is no next Government."],
    "kl_armament": ["“armament economy”"],
    "kl_cycle": ["political business cycle”"],
    "fj_committed": ["neither Government is committed to the proposals put forward by its experts."],
    "fk_bancor": ["called (let us say) bancor"],
    "fk_new": ["would be breaking new ground"],
    "fk_notessential": ["These charges are not absolutely essential to the scheme."],
    "fk_critical": ["with as critical an eye as on excessive debit balances",
                    "each being, indeed, the inevitable concomitant of the other"],
    "fk_ultimate": ["but shall retain the ultimate decision in its own hands"],
    "fw_rates": ["shall be considered only when essential to correction of a fundamental disequilibrium"],
    "fw_fourth": ["no country shall be entitled to cast more than one-fourth of the aggregate votes regardless of its "
                  "quota."],
    "hl44_elegance": ["There were, it is true, certain features of elegance, clarity and logic in the Clearing Union "
                      "plan which have disappeared."],
    "hl44_dog": ["it has been the dog that died"],
    "hl44_iron": ["are an iron ration"],
    "hl44_creditor": ["is squarely placed on the creditor countries"],
    "hl44_sterling": ["the external value of sterling shall conform to its internal value as set by our own domestic "
                      "policies, and not the other way round."],
    "hl44_heresy": ["What used to be a heresy is now endorsed as orthodox."],
    "hl44_relic": ["Gold is a barbarous relic"],
    "hl44_stagger": ["beneath which we shall stagger"],
    "fs_denmark": ["the Danish Minister to the United States was present in his personal capacity."],
    "fa_change": ["except to correct a fundamental disequilibrium"],
    "fa_policies": ["it shall not object to a proposed change because of the domestic social or political policies of "
                    "the member proposing the change."],
    "fs_rigidity": ["Stability does not mean rigidity and rigidity in the past has resulted in extreme instability."],
    "fa_capital": ["Members may exercise such controls as are necessary to regulate international capital movements"],
    "fs_deterrent": ["intended to act as serious deterrents"],
    "fs_end": ["in the end, such a scarcity can be eliminated only by the re-establishment of balance between the "
               "country’s exports and its imports."],
    "hl44_voting": ["The voting power of the British Commonwealth and that of the United States are expected to be "
                    "approximately equal."],
    "sn_acheson": ["We have voting power which is directly proportioned to the money which we put up."],
    "sn_wrong": ["Your whole attitude seems to me to be wrong, both from an economic point of view and a political point "
                 "of view."],
    "sn_string": ["without a string of any kind"],
    "sn_white": ["has no strings attached to it"],
    "hl44_sanction": ["I cannot imagine that this sanction would ever be allowed to come into effect."],
    "fs_purpose": ["to be in a position at all times to help any member to meet a temporary deficit in its balances of "
                   "payments and give it time to correct maladjustments."],
    "k_twice": ["Thus the system of deferment will be twice blessed"],
}


def tex_text() -> str:
    return "\n".join(l for l in TEX.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("%"))


def text_quotations() -> list[str]:
    """The “…” of the text; the closing question is Chapter 35's and the chapter's own question (with its “付得起”) is
    Chapter 33's (both checked by guide() and ending())."""
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 35's question"
    t = t[:-len(NEXT)]
    assert t.count(GUIDE) == 2, "the question is not in the guide and at the end of the opening"
    return re.findall(r"“([^”]*)”", t.replace(GUIDE, ""))


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
    """A Chinese numeral of the text: '六', '十', '三分之一', '五分之二', '一半', '百分之百'."""
    if "分之" in s:
        b, a = s.split("分之")
        return zh(a) / zh(b)
    if s.endswith("半"):                                                       # '一半': one half
        return 0.5 * (zh(s[:-1]) if s[:-1] else 1)
    big, total, part = 0, 0, 0
    for ch in s:
        if ch in ZH_DIGITS:
            part = ZH_DIGITS[ch]
        elif ch == "万":                                                       # 万 multiplies all before it
            big += max(total + part, 1) * ZH_UNITS[ch]
            total, part = 0, 0
        else:
            total += max(part, 1) * ZH_UNITS[ch]
            part = 0
    return float(big + total + part)


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
    assert f"\\guidequestion{{{GUIDE}}}" in t and GUIDE.startswith(PREV)
    ch33 = (ROOT / "zh" / "ch33_islm.tex").read_text(encoding="utf-8")
    ch33 = "\n".join(l for l in ch33.splitlines() if not l.lstrip().startswith("%"))
    assert ch33.rstrip().endswith(PREV)                                       # 第 33 章交来的问题
    for label in ("ch:islm", "ch:alternatives"):                               # the prerequisites (PLAN: 33, 30)
        assert f"\\chref{{{label}}}\\enspace\\nameref{{{label}}}" in t, label
    said("用凯恩斯《如何筹措战费》（1940）分析", Y["km_date"])
    said("概括勒纳（1943）功能财政的规则与卡莱茨基（1943）的政治经济学批评", Y["ln_masthead"], F["kl_masthead"][1])
    said("说明 1944 年体系的最终设计", F["fa_title"][2])
    assert "\\chapterstub" not in t


def opening(F, Y, Q):
    y40 = F["k_sign"][0]
    said("1940 年 2 月，凯恩斯", y40, mon("k_sign", "February"))
    assert "King's College, Cambridge" in transcription("k_sign")
    say("在剑桥国王学院为一本小书写完了序言")
    assert "dc.publisher: London, Macmillan" in Q["km_publisher"] and F["km_date"][0] == y40
    said("序言说，前一年 11 月", 11)
    assert "last November" in Q["k_times"] and "The Times" in Q["k_times"] and column("juan")["k_times"] == "p. iii"
    chk("    three articles (三篇文章)", F["k_times"][0], told("他在《泰晤士报》上发表了三篇文章", "发表了", "篇文章"))
    assert "universal family allowances in cash" in Q["k_family_cash"] and "a capital levy" in Q["k_levy"]
    assert page("k_free") == 1                                                # 正文的第一页
    say("他在正文的第一页写道")
    chk("    nearly six months of war (开战已近六个月)", F["k_unemp"][0], told("开战已近六个月", "已近", "个月"))
    assert "after nearly six months of war" in Q["k_unemp"] and "failure of organisation" in Q["k_unemp"]
    assert "Age of Plenty to the Age of Scarcity" in Q["k_scarcity"]
    B = boe()
    said("1946 年末英国的国债是 GDP 的 2.6 倍", 1946, B.debt_pct_gdp[1946] / 100)
    Bu = budget()
    said("美国联邦政府的债务到 1946 财政年度末有 2710 亿美元，比这一年的 GDP 还多", 1946, Bu.debt[1946] * 1e9)
    assert Bu.debt[1946] * 1e3 > nipa().gdp[1946]
    assert paragraph("开战已近六个月").endswith(GUIDE)                          # the opening ends with the question


def table_mobilization(F, Y, Q):
    """tab:warfinance-mobilization, as Harrison's Table 1-8 prints it."""
    t = tex_text()
    head = F["hw_table_head"]
    assert head[:2] == [1, 8] and head[2] == 1939 and head[3] == 44
    cur, axis, su = F["hw_current"], F["hw_axis"], F["hw_ussr"]
    us, uk = cur[:6], cur[6:]
    de, it, jp = axis[:5], axis[5:10], axis[10:]
    years_ = list(range(1939, 1945))
    lines = [" & " + " & ".join(str(y) for y in years_) + " \\\\"]

    def row(name, vals, lead=0, tail=0):
        cells = ["—"] * lead + [f"{v:.0f}" for v in vals] + ["—"] * tail
        assert len(cells) == 6
        return f"{name} & " + " & ".join(cells) + " \\\\"

    lines += [row("美国", us), row("英国", uk), row("德国", de, tail=1), row("意大利", it, tail=1), row("日本", jp),
              row("苏联（不变价格）", su, lead=1)]
    assert Q["hw_axis"].count("..") == 2 and Q["hw_ussr"].startswith("USSR ..")
    for line in lines:
        assert line in t, line
        COVERED.append(line)
    said("\\caption{六个大国的军费，1939—1944 年（占国民收入的百分比）", 1939, 1900 + head[3])
    assert "per cent of national income" in Q["hw_table_head"]
    said("\\datasource{Harrison（1998）表 1-8。苏联按 1937 年要素成本计算", Y["hw_table_head"], head[0], head[1],
         F["hw_sources_su"][0])
    assert "1937 factor cost" in Q["hw_sources_su"] and "net national expenditure" in Q["hw_sources"]
    assert "GNP" in Q["hw_sources_us"] and "GNP" in Q["hw_sources_de"] and "GDP" in Q["hw_sources_it"]
    assert "GDP" in Q["hw_sources_jp"]
    return us, uk, de, jp, su


def world(F, Y, Q):
    us, uk, de, jp, su = table_mobilization(F, Y, Q)
    chk("    six great powers (六个大国)", 6, told("列出六个大国的军费占国民收入的比例", "列出", "个大国"))
    said("1939 年，美国的军费只占 1\\%，英国已占 15\\%，德国占 23\\%", 1939, us[0], uk[0], de[0])
    said("1943 年，英国是 55\\%，德国是 70\\%，苏联按不变价格计是 61\\%", 1943, uk[4], de[4], su[3])
    said("到 1944 年，日本是 76\\%，美国是 42\\%", 1944, jp[5], us[5])
    B = boe()
    exp, rec = B.cy_expenditure_pct_gdp, B.cy_receipts_pct_gdp
    assert exp.loc[1939:1945].idxmax() == 1944
    said("英国中央政府的支出 1938 年相当于 GDP 的 18.2\\%，1944 年到了 61.3\\%", 1938, exp[1938], 1944, exp[1944])
    said("收入只从 18.4\\% 升到 33.2\\%", rec[1938], rec[1944])
    Bu = budget()
    said("联邦支出从 1940 财政年度的 96 亿美元增加到 1945 财政年度的 952 亿美元", 1940, Bu.outlays[1940] * 1e9, 1945,
         Bu.outlays[1945] * 1e9)
    assert "For years ending June 30" in transcription("cy_head")
    said("美国的财政年度到当年 6 月 30 日为止", 6, 30)
    # Wood
    y, m, d = url_date("hc1941fs")
    said("1941 年 4 月 7 日，财政大臣金斯利·伍德", y, m, d)
    assert Q["h41_speaker"] == "The Chancellor of the Exchequer (Sir Kingsley Wood)"
    y16, p5, p6 = F["h41_1916"]
    said("他回顾说，1916 年政府借款的一般下限是 5\\%，那年 7 月连国库券都到了 6\\%", y16, p5, mon("h41_1916", "July"), p6)
    assert "as a general minimum" in Q["h41_1916"] and "even Treasury bills" in Q["h41_1916"]
    short, avg = F["h41_short"]
    said("现在短期借款的成本是 1⅛\\% 或更低，平均利率不到 2\\%", short, avg)
    assert short == 1.125 and "or less" in Q["h41_short"]
    chk("    about a third (三分之一)", F["h41_third"][0],
        told("纳税人的总成本大约是上一次大战时的三分之一", "大战时的", ""))
    said("《经济学人》1940 年 1 月就说", Y["hf_three"], 1)
    assert "The Economist, 20 January 1940" in column("note")["hf_three"]
    chk("    'three per cent war' (百分之三)", F["hf_three"][0] / 100, told("这是一场“百分之三的战争”", "一场“", "的战争"))
    # Kalecki and the dam
    said("1943 年写道，预算赤字大得惊人，利率却从 1940 年初以来没有上升", F["kl_masthead"][1], F["kl_norise"][0])
    assert "since the beginning of 1940" in Q["kl_norise"] and "astronomical budget deficits" in Q["kl_norise"]
    assert "in particular on that of the Central Bank" in Q["kl_banking"]
    assert "a corresponding amount of purchasing power" in Q["h41_huge"]
    assert "price control, rationing" in Q["h41_dam"]


def gap_section(F, Y, Q):
    lo, hi, mid, out, dep, inv, both, abroad = F["k_output"]
    said("他估计，组织得当的话，产出可以增加 15\\% 到 20\\%", lo, hi)
    said("取一个略低于中间的数 17½\\%，按战前价格约合 8.25 亿英镑", mid, out * 1e6)
    assert "17½" in tex_text() and mid == 17.5 and "just under" in transcription("k_output")
    said("折旧基金可以腾出 1.5 亿英镑，正常的新投资可以腾出 3 亿英镑，两项共 4.5 亿英镑", dep * 1e6, inv * 1e6, both * 1e6)
    chk("    150 + 300 = 450", dep + inv, both)
    said("从国外的资产与借款里，一年最多能安全地拿到 3.5 亿英镑", abroad * 1e6)
    assert "the maximum contribution which we can safely take from this source in a year" in transcription("k_output")
    assert "earnings will be increased, consumption must be diminished" in Q["k_hammer"]
    g, dep2, ab2, rest, vol = F["k_money"]
    said("凯恩斯把政府增加的支出定为 18.5 亿英镑，其中 1.5 亿来自国内没有补上的折旧，3.5 亿来自国外", g * 1e6, dep2 * 1e6,
         ab2 * 1e6)
    said("剩下的 13.5 亿英镑，要靠新增的税收与新的储蓄", rest * 1e6)
    chk("    1850 - 150 - 350 = 1350", g - dep2 - ab2, rest)
    said("自愿的储蓄至少能指望 4 亿英镑", vol * 1e6)
    priv, tax, _, _, _, gap_, vol2 = F["k_taxes"]
    chk("    the voluntary savings of p. 28 are those of p. 23", vol2, vol)
    said("私人手里还有约 9.5 亿英镑的收入不许花掉", priv * 1e6)
    chk("    1350 - 400 = 950", rest - vol, priv)
    said("其中大约一半，即 5 亿英镑，他认为可以靠征税", tax * 1e6)
    chk("    one half (一半)", told("其中大约一半", "大约", ""), 0.5)
    assert "one half of this, namely £500 million" in transcription("k_taxes")
    assert "with due regard" not in Q["k_taxgatherer"] and page("k_taxgatherer") == 28
    said("余下的 4.5 亿英镑若不靠一点通胀", gap_ * 1e6)
    chk("    950 - 500 = 450", priv - tax, gap_)
    said("工人的实际收入可能损失 20\\%", F["k_20pct"][0])
    assert "the most burdensome alternative" in Q["k_20pct"] and "entrepreneur class" in Q["k_20pct"]
    assert "a shortage of supplies rather than a runaway price level" in Q["k_shortage"]
    # the model: eq:warfinance-gap and ex:warfinance-cross
    said("每增加 1，缺口减少$c$", 1)
    M = model()
    pe, wa, ta, de = M["peace"], M["war"], M["taxed"], M["deferred"]
    a, c, I = M1["a"], M1["c"], M1["I"]
    Yb, G0, T0, Gw, Tw = GAP["Ybar"], GAP["G0"], GAP["T0"], GAP["Gw"], GAP["Tw"]
    said("接\\exref{ex:generaltheory-cross}的棉布经济，$a=26$，$c=0.6$，$I=10$。设产能$\\bar Y=100$，和平时期$G=T=10$，"
         "$D=0$", a, c, I, Yb, G0, 0)
    assert T0 == G0
    said("（1）验证和平时期的均衡收入正好是 100", pe["Y"])
    said("（2）战时政府支出增加到 30", Gw)
    said("（4）税收加到 30", Tw)
    said("（1）支出线是$26+0.6(Y-10)+10+10=40+0.6Y$，均衡$Y=40/0.4=100$", a, c, T0, I, G0, pe["b0"], c, pe["b0"],
         1 - c, pe["Y"])
    chk("    the peace: Y = capacity, gap 0", [pe["Y"], pe["gap"]], [Yb, 0], tol=1e-9)
    said("（2）支出线变成$60+0.6Y$，在产能处计划的支出是 120，缺口是 20", wa["b0"], c, wa["at"], wa["gap"])
    said("（3）由式~\\eqref{eq:warfinance-gap}，$T=100-(100-26-10-30)/0.6\\approx43.3$，比和平时期多 33.3，预算有 13.3 的盈余",
         Yb, Yb, a, I, Gw, c, M["Ts"]["T"], M["Ts"]["T"] - T0, M["Ts"]["T"] - Gw)
    chk("    taxes only: the gap closes", gap(Gw, M["Ts"]["T"]), 0, tol=1e-9)
    said("（4）支出线是$48+0.6Y$，缺口$48+60-100=8$", ta["b0"], c, ta["b0"], c * Yb, Yb, ta["gap"])
    said("延期支付$D=8/0.6\\approx13.3$，支出线回到$40+0.6Y$", ta["gap"], c, M["D"]["D"], de["b0"], c)
    chk("    deferment returns the line to peace", [de["b0"], de["gap"]], [pe["b0"], 0], tol=1e-9)
    said("$T+D\\approx43.3$", Tw + M["D"]["D"])
    chk("    T + D the same as taxes only", Tw + M["D"]["D"], M["Ts"]["T"], tol=1e-9)
    said("竖线是产能 100。和平时期的支出线$40+0.6Y$在产能处与斜线相交", Yb, pe["b0"], c)
    said("战时政府支出增加到 30，支出线升到$60+0.6Y$，缺口是 20；税收加到 30，支出线是$48+0.6Y$，缺口还有 8；再加上 13.3 的延期支付",
         Gw, wa["b0"], c, wa["gap"], Tw, ta["b0"], c, ta["gap"], M["D"]["D"])
    keynes_account(F, Y, Q)
    # deferred pay
    assert "command of the right to postponed consumption" in Q["k_wealth"]
    five, fifteen, cost = F["k_allowance"]
    said("他建议为每个孩子直到 15 岁每周发 5 先令的家庭津贴", fifteen, five)
    assert "5s. per week" in transcription("k_allowance") and "paid in cash" in transcription("k_allowance")
    said("先令是英国的货币单位，一镑合 20 先令", SHILLINGS)
    said("他估计这一项的净成本是 1 亿英镑", cost)
    assert "an iron ration as it has been called" in Q["k_iron"]
    assert "No criticism could be more misdirected." in Q["k_charged"]


def keynes_account(F, Y, Q):
    """ex:warfinance-keynes: Keynes's account on pp. 15, 16, 23 and 28 (read on the page images)."""
    pages = [page(r) for r in ("k_output", "k_spending", "k_money", "k_taxes")]
    said("按《如何筹措战费》第 15、16、23、28 页的数", *pages)
    _, _, _, out, _, _, both, abroad = F["k_output"]
    y39, rate, more, cut = F["k_spending"]
    g, dep, ab, rest, vol = F["k_money"]
    priv, tax, simon, ept, other, gap_, _ = F["k_taxes"]
    said("（1）产出增加 825，折旧与新投资腾出 450，国外拿到 350", out, both, abroad)
    said("政府多花 1850", g)
    said("（2）钱的一面，1850 减去折旧的 150 与国外的 350，再减去 400 的自愿储蓄", g, dep, ab, vol)
    said("一整年也许能提供 400，其中超额利润税至少 100；别的税再找 100", simon, ept, other)
    assert "Sir John Simon's emergency budget" in transcription("k_taxes")
    assert "at least £100 million from Excess Profits Tax" in transcription("k_taxes")
    res = out + both + abroad
    said("（1）$825+450+350=1625$。$1850-1625=225$，消费要比战前少 225", out, both, abroad, res, g, res, g - res, cut)
    chk("    the OCR text of p. 16: £1,625 (£825+£450+£350)", F["k_1625"], [res, out, both, abroad])
    said("1850 是 1939 年秋天约 1500 的支出水平，再加上第二年的 350", g, y39, rate, more)
    chk("    1500 + 350 = 1850", rate + more, g)
    said("（2）$1850-150-350=1350$，$1350-400=950$", g, dep, ab, rest, rest, vol, priv)
    said("（3）税收合计$400+100=500$，约为 950 的一半，$950-500=450$", simon, other, tax, priv, priv, tax, gap_)
    chk("    the half (一半)", told("约为 950 的一半", "的", ""), 0.5)
    chk("    500/950 is about a half", tax / priv, 0.5, tol=0.05)
    said("这 450 若不用延期支付", gap_)
    said("单位是百万英镑", )


def budget41(F, Y, Q):
    assert "inflationary gap" in Q["h41_gapdef"] and "sterling balances" in Q["h41_sterling"]
    said("\\section{1941 年的英国预算}", url_date("hc1941fs")[0])
    m18, spent, taxed, overseas, left = F["h41_18m"]
    said("他先回顾了开战后的 18 个月", m18)
    said("政府支出约 46.5 亿英镑，税收付了约 20 亿英镑", spent, taxed)
    said("海外的资源约 10 亿英镑，余下约 16.5 亿英镑", overseas, left)
    chk("    4650 - 2000 - 1000 = 1650 (million)", spent - taxed - overseas, left)
    dom, rev = F["h41_3700"]
    said("对 1941—1942 财政年度，他估计国内支出约 37 亿英镑，按现有税制，收入是 16.36 亿英镑", 1941, 1942, dom, rev)
    sav, half = F["h41_1600"]
    said("财政部从储蓄与借款里最多只能指望 16 亿英镑", sav)
    chk("    rather less than one-half (不到一半)", half, told("会占不到一半", "不到", ""))
    said("三项相减，还差约 4.6 亿英镑", dom - rev - sav)
    assert "of the order of £500,000,000" in Q["h41_500"]
    chk("    'of the order of £500,000,000' against 3700 - 1636 - 1600 (million)", (dom - rev - sav) / 1e6,
        F["h41_500"][0] / 1e6, tol=50)
    say("“在 5 亿英镑的量级”")
    COVERED.append("“在 5 亿英镑的量级”")
    said("在 5 亿英镑的量级", F["h41_500"][0])
    chk("    nearly double (两倍)", F["h41_double"][0], told("差不多是开战第一年的两倍", "第一年的", "倍"))
    assert "nearly double the rate in the first year of the war" in Q["h41_double"]
    chk("    the first year (第一年)", 1, told("差不多是开战第一年的两倍", "开战第", "年"))
    lo, hi = F["h41_200_300"]
    said("一年里也还能再多筹到 2 亿到 3 亿英镑", lo, hi)
    said("余下的缺口，也不能估得少于 2 亿到 3 亿英镑", *F["h41_gapremains"])
    new, aim = F["h41_250"]
    said("所以新税在全面实行时不得少于 2 亿英镑；为了留有余地，他要在一整年里新征 2.5 亿英镑左右", new, aim)
    s, d, std = F["h41_10s"]
    said("标准税率提高 1 先令 6 便士，达到每镑 10 先令，也就是一半", s, d, std)
    chk("    10s. in the £ is a half (一半)", std / SHILLINGS, told("达到每镑 10 先令，也就是一半", "也就是", ""))
    said("便士也是英国的货币单位，一先令合 12 便士", PENCE)
    said("交所得税的人多了 200 万以上", F["h41_2m"][0])
    assert "by over 2,000,000" in Q["h41_2m"]
    assert "Post Office Savings Bank" in Q["h41_credit"]
    w45, w2 = F["h41_45s"]
    said("一个每周挣 45 先令的单身汉，去年不交所得税，今年每周要交 2 先令", w45, w2)
    assert "A single man" in Q["h41_45s"] and "the whole of which will be treated as a post-war credit" in Q["h41_45s"]
    amt, half2 = F["h41_half"]
    said("所得税的这些变化，一整年共增加 2.5 亿英镑", amt)
    chk("    one-half as a credit (一半)", half2, told("其中一半作为抵免", "其中", "作为"))
    chk("    the income tax changes are the new taxation of about £250,000,000", amt, aim)
    assert "deferred pay" in Q["hf_postwar"] and "postwar credits" in Q["hf_postwar"]
    tot, more, prewar = F["h41_1860"]
    said("伍德预计一整年的税收合计 18.6 亿英镑，比上一年多 5 亿英镑，比战前最后一个财政年度多将近 10 亿英镑", tot, more, prewar)
    assert "nearly £1,000,000,000 more than in the last pre-war financial year" in Q["h41_1860"]
    chk("    practically half by taxation (差不多一半)", F["h41_halftax"][0],
        told("我今年要靠税收筹集差不多一半", "差不多", ""))
    # Harrison's account of the whole war
    p70, half3 = F["hf_70"]
    said("英国的政府支出平均是 GDP 的 70\\%", p70)
    chk("    half out of general taxation (一半)", half3, told("一半靠一般税收", "", "靠一般"))
    third, p5, y56, _ = F["hf_short"]
    chk("    one third by short-term borrowing (三分之一)", third, told("累计的赤字只有三分之一靠短期借款", "只有", "靠短期"))
    said("按他转引的 Sayers（1956），高能货币只占赤字融资的 5\\% 多一点", y56, p5)
    assert "little more than 5%" in Q["hf_short"]
    assert "no more than doubled" in Q["hf_cash"]
    y40, t1, q1 = F["hf_imports"]
    said("1940—1941 年，预算赤字最多有三分之一靠净进口来弥补，后来稳定在四分之一", y40, 1941)
    assert "in 1940-1" in Q["hf_imports"]
    chk("    up to one third (三分之一)", t1, told("预算赤字最多有三分之一靠净进口", "最多有", "靠净进口"))
    chk("    one quarter (四分之一)", q1, told("后来稳定在四分之一", "稳定在", ""))
    compare_box(F, Y, Q)


def compare_box(F, Y, Q):
    """The compare box of the two world wars (the shares, debt ratios and price rises are the book's calculations from
    the Bank of England's workbook)."""
    B = boe()
    ww1, ww2 = fy_share(1914, 1918), fy_share(1939, 1945)
    said("1914/15—1918/19 财政年度合计 28.5\\%", 1914, 15, 1918, 19, ww1)
    said("1939/40—1945/46 财政年度合计 52.4\\%", 1939, 40, 1945, 46, ww2)
    assert B.fy[1914] == "1914/15" and B.fy[1945] == "1945/46"
    y16, p5, p6 = F["h41_1916"]
    said("1916 年的一般下限 5\\%，国库券到 6\\%", y16, p5, p6)
    said("1941 年短期借款 1⅛\\% 或更低，平均不到 2\\%", 1941, F["h41_short"][0], F["h41_short"][1])
    d = B.debt_pct_gdp
    said("1913 年末 28\\%，1919 年末 140\\%", 1913, d[1913], 1919, d[1919])
    said("1938 年末 153\\%，1946 年末 259\\%", 1938, d[1938], 1946, d[1946])
    cpi = B.cpi_2015_100
    said("1913—1918 年上涨 108\\%", 1913, 1918, rise(cpi[1913], cpi[1918]))
    said("1938—1945 年上涨 56\\%", 1938, 1945, rise(cpi[1938], cpi[1945]))
    two, three = F["hf_ww1"]
    assert "trebled or quadrupled in Germany" in Q["hf_ww1"] and "doubled in the UK" in Q["hf_ww1"]
    chk("    Germany trebled or quadrupled (三四倍)", [three, 4], [told("德国增加到三四倍", "增加到", "四倍"),
                                                         told("德国增加到三四倍", "三", "倍")])
    chk("    the UK doubled (翻了一番)", two, 2)
    say("英国的货币存量翻了一番", "现金存量至多翻了一番")
    assert ww2 > 50 > ww1                                                       # 一半多
    assert rise(cpi[1938], cpi[1945]) < rise(cpi[1913], cpi[1918]) / 1.5       # 慢得多


def us(F, Y, Q):
    B = budget()
    w = B.loc[1942:1945]
    said("1942—1945 财政年度，联邦收入合计 1382 亿美元，支出合计 3026 亿美元", 1942, 1945, w.receipts.sum() * 1e9,
         w.outlays.sum() * 1e9)
    said("收入只付了支出的 45.7\\%", 100 * w.receipts.sum() / w.outlays.sum())
    said("联邦债务从 1939 财政年度末的 482 亿美元增加到 1946 财政年度末的 2710 亿美元", 1939, B.debt[1939] * 1e9, 1946,
         B.debt[1946] * 1e9)
    R = debt_ratio()
    said("这相当于从 GDP 的 52\\% 升到 119\\%", R[1939], R[1946])
    table_us(F, Y, Q)
    lo, hi = F["k_output"][:2]
    said("凯恩斯估计英国的产出只能增加 15\\% 到 20\\%", lo, hi)
    A = annual()
    said("1941 年的失业率仍有 9.9\\%", 1941, A.loc[1941, "unemployment_pct"])
    N = nipa()
    said("1939—1944 年美国的实际 GDP 增加了 92\\%", 1939, 1944, rise(N.gdp_real_2017[1939], N.gdp_real_2017[1944]))
    said("凯恩斯 1940 年的前提", Y["km_date"])
    said("联邦储备委员会 1942 年的年报说", Y["ar_peg"])
    assert "Another joint aim of the Treasury and the Federal Reserve" in Q["ar_peg"]
    assert "rates of interest known in advance" in Q["ar_market"]
    twelve, eighth = F["ar_bills"]
    tr = transcription("ar_bills")
    said("4 月底，联邦公开市场委员会指示 12 家联邦储备银行，按 ⅜\\% 的年贴现率买进所有送来的国库券", mon("ar_bills", "April"),
         twelve)
    assert "At the end of April" in tr and "purchase all Treasury bills offered" in tr and eighth == 0.375
    say("⅜\\%")
    # the figures
    said("1913—1950 年，日历年，灰底是两次世界大战。(b) 美国联邦政府的支出与收入，十亿美元，1939—1950 财政年度（到 6 月 30 日）",
         boe().index[0], boe().index[-1], B.index[0], B.index[-1], 6, 30)
    say("二战时英国的收入跟得更紧")
    assert fy_share(1939, 1945) > fy_share(1914, 1918)
    said("《英国千年宏观经济数据》表 A27；《美国历史统计》系列 Y 339—340", 27, 339, 340)
    said("(a) 英国，1913—1950 年，年末的估计，灰底是两次世界大战。(b) 美国，1939—1950 财政年度末的联邦债务总额", boe().index[0],
         boe().index[-1], B.index[0], B.index[-1])
    said("《英国千年宏观经济数据》表 A29；《美国历史统计》系列 Y 342", 29, 342)
    assert "A27. Central govt borrowing" in load_snapshot("boe_millennium_gb_1913_1950")[1]["source"]
    assert "A29. The National Debt" in load_snapshot("boe_millennium_gb_1913_1950")[1]["source"]


def table_us(F, Y, Q):
    """tab:warfinance-us, as Historical Statistics prints it (one decimal)."""
    B = budget()
    t = tex_text()
    said("\\caption{美国联邦政府的收支与债务（十亿美元，财政年度到 6 月 30 日）", 6, 30)

    def sgn(v):
        return f"$-${-v:.1f}" if v < 0 else f"{v:.1f}"

    for y, r in B.iterrows():
        line = f"{y} & {r.receipts:.1f} & {r.outlays:.1f} & {sgn(r.surplus)} & {r.debt:.1f} \\\\"
        assert line in t, line
        COVERED.append(line)
    tr = transcription("cy_head")
    assert "Receipts 339" in tr and "Total gross Federal debt 342" in tr and "Data for 1929-1953 are consolidated" in tr
    said("\\datasource{《美国历史统计》（1975）系列 Y 339—342，第 1105 页，1929—1953 年为合并现金报表的数", Y["cy_head"],
         339, 342, page("cy_head"), 1929, 1953)


def soviet(F, Y, Q):
    said("\\begin{case}{苏联 · 1941—1945 · 计划下的战时财政}", 1941, 1945)
    assert "planning, procurement, and rationing worked effectively" in Q["hu_planning"]
    r40, y40, r44, y44 = F["hu_rubles"]
    said("国防支出从 1940 年的 570 亿卢布增加到 1944 年的 1380 亿卢布", y40, r40 * 1e9, y44, r44 * 1e9)
    say("卢布是苏联的货币单位")
    y43, gov, nmp = F["hu_burden"]
    said("按当年价格的公布数字，国防负担在 1943 年最重，占政府支出的 60\\%，占物质生产部门净产值的 30\\%", y43, gov, nmp)
    assert "published figures at current prices" in Q["hu_burden"]
    assert "semi-compulsory bond sales" in Q["hu_taxes"]
    p20, a, b = F["hu_deficit"]
    said("1942—1945 年，事前的赤字约为物质生产部门净产值的 20\\%", a, b, p20)
    chk("    the money stock trebled (三倍)", F["hu_money"][0], told("战争期间，货币存量增加到三倍", "增加到", "倍"))
    y, third = F["hu_supply"]
    said("1943 年，官方与非官方两个部门的实际供给合起来", y)
    chk("    little more than one third (三分之一)", third, told("只比战前的三分之一多一点", "战前的", "多一点"))
    ten, y43b = F["hu_kolkhoz"]
    said("集体农庄市场的价格，到 1943 年短缺最严重时涨到战前的十倍", y43b)
    chk("    ten times (十倍)", ten, told("涨到战前的十倍", "战前的", "倍"))
    y43c, _, p40, tenfold = F["hu_weapons"]
    said("到 1943 年，武器价格跌了 40\\%", y43c, p40)
    chk("    tenfold (十倍)", tenfold, told("集体农庄市场的价格却涨了十倍", "涨了", "倍"))
    y45, half = F["hu_wage"]
    said("直到 1945 年，公共部门的实际工资大约只有战前的一半", y45)
    chk("    roughly half (一半)", half, told("大约只有战前的一半", "战前的", ""))
    m, frac_ = F["hu_leningrad"]
    said("饥饿与饥饿引起的疾病夺去了 100 万人的生命", m)
    chk("    two-fifths (五分之二)", frac_, told("占全城战前人口的五分之二", "人口的", ""))
    k75, y1, k50, y2 = F["hu_nkvd"]
    said("他们 1940—1941 年约有 75 万人，1943—1945 年约有 50 万人", y1, 1941, k75, y2, 1945, k50)
    assert "in 1940-1, falling to half a million in 1943-5" in Q["hu_nkvd"]
    assert "maintenance costs incurred by the labour camps" in Q["hu_forced"]
    lo, hi = F["hu_goskomstat"]
    said("“2600 万到 2700 万”，点估计是 2660 万", lo * 1e6, hi * 1e6, F["hu_266"][0] * 1e6)
    e266, e27 = F["hu_emigration"]
    said("这个数没有明确扣去战时与战后约 270 万的净移民；照 Harrison 的说法，即使只有 2390 万人", e27 * 1e6,
         F["hu_239"][0] * 1e6)
    chk("    26.6 - 2.7 = 23.9 million", e266 - e27, F["hu_239"][0], tol=1e-9)
    assert e266 == F["hu_266"][0]
    said("军人的死亡据报为 870 万", F["hu_military"][0] * 1e6)
    assert "normal mortality of several hundred thousand" in Q["hu_normal"]


def germany_japan_bengal(F, Y, Q):
    d1, y38, bn = F["nca2_12bn"]
    said("到 1938 年 4 月 1 日停用时，流通在外的有 120 亿帝国马克", y38, mon("nca2_12bn", "April"), d1, bn * 1e9)
    say("帝国马克是当时德国的货币单位")
    said("德国战时的政府支出平均超过国民收入的 80\\%", F["hf_germany"][0])
    assert "While precise comparisons have not been attempted" in Q["hf_germany"]
    assert "on monetary emission" in Q["hf_germany"] and "short-term borrowing at higher interest rates" in Q["hf_germany"]
    assert "from the occupied territories" in Q["hf_foreign"]
    assert "the pretense of paying for all the property" in Q["imt_pretense"]
    assert "paid for by the occupied countries themselves" in Q["imt_disguised"]
    assert "excessive occupation costs or by forced loans" in Q["imt_clearing"] and "merely in name" in Q["imt_clearing"]
    assert "Government-Genera1 to Germany" in Q["imt_food"] and "widespread starvation" in Q["imt_poland"]
    assert "defendant Goering" in column("note")["imt_famine"]
    assert "slave labor upon defense works, armament production" in Q["imt_deported"]
    d, y44, five, two = F["imt_sauckel"]
    said("他 1944 年 3 月 1 日说，来到德国的 500 万外国工人里，“自愿来的连 20 万都不到”", y44, mon("imt_sauckel", "March"),
         d, five, two)
    assert "substantially accurate" in Q["imt_accurate"]
    said("约 600 万犹太人被杀害", F["imt_6m"][0] * 1e6)
    assert "Jews were murdered" in Q["imt_6m"]
    # Japan
    said("1936 年以后日本的军费迅速增加", Y["ide_after"])
    assert "shifted to wartime finance" in Q["ide_after"]
    a, b, _, p = F["sz_gnp37"]
    said("1937—1940 年 GNP 平减指数平均每年涨 11.9\\%", a, 1900 + b, p)
    y41, _, m4 = F["bjh_1941"]
    said("1941 年 4 月，兑换银行券条例的临时特例法施行", y41, m4)
    assert "兌換銀行券条例の臨時特例に関する法律" in Q["bjh_1941"] and "最高発行額屈伸制限制度" in Q["bjh_1941"]
    said("1942 年 5 月，日本银行按新的《日本银行法》重新成立", Y["bjh_1942"], 5)
    assert Q["bjh_1942"].startswith("5月") and "新発足" in Q["bjh_1942"]
    y44j, tq = F["hw_japan"]
    said("到 1944 年，照 Harrison 的估计", y44j)
    chk("    three quarters of GDP (四分之三)", tq, told("日本已把 GDP 的四分之三用于战争", "GDP 的", "用于"))
    chk("    and Table 1-8 prints 76 per cent", 100 * tq, F["hw_axis"][-1], tol=1.5)
    chk("    World War II (二次大战)", 2, told("二次大战期间与战后", "", "次大战"))
    assert "during and after World War II, the BOJ continued to provide money" in Q["ide_ww2"]
    # Bengal
    said("1945 年，饥荒调查委员会发表了关于孟加拉的报告", F["fm_date"][0])
    assert Q["fm_title"] == "Famine Inquiry Commission Report On Bengal"
    said("“1943 年稻米供应的短缺是饥荒的根本原因之一”", F["fm_rice"][0])
    said("1942 年初缅甸陷落以后", F["fm_burma"][0])
    assert "early in 1942, imports from that country ceased" in Q["fm_burma"]
    assert "proximity to the fighting zone" in Q["fm_war"]
    f5, f6, y42 = F["fm_prices"]
    said("物价涨到 1942 年头几个月的五到六倍", y42)
    chk("    five to six times (五到六倍)", [f5, f6], [told("头几个月的五到六倍", "个月的", "到"),
                                            told("头几个月的五到六倍", "到", "倍")])
    lo, hi = F["fm_between"]
    chk("    one to two million (一百万到二百万)", [lo, hi], [told("死了一百万到二百万人", "死了", "到"),
                                                    told("死了一百万到二百万人", "到", "人")])
    said("饥荒与随后的流行病直接造成约 150 万人死亡", F["fm_15"][0] * 1e6)
    assert lo <= F["fm_15"][0] * 1e6 <= hi
    y43, m35 = F["fm_35"]
    said("加尔各答大学一位教授估计 1943 年死了 350 万人", y43, m35 * 1e6)
    assert "Calcutta University" in column("note")["fm_35"]


def lerner(F, Y, Q):
    said("1943 年 2 月，勒纳", F["ln_masthead"][0], mon("ln_masthead", "February"))
    assert Q["ln_title"] == "FUNCTIONAL FINANCE AND THE FEDERAL DEBT"
    assert "neither greater nor less than that rate" in Q["ln_first"]
    chk("    the first law (第一条)", 1, told("第一条规律关于总支出", "第", "条"))
    chk("    the second law (第二条)", 2, told("第二条规律关于借款", "第", "条"))
    assert Q["ln_second"].startswith("The second law of Functional Finance")
    chk("    the third (第三条)", 3, told("第三条是，为执行前两条", "第", "条是"))
    chk("    the first two (前两条)", 2, told("第三条是，为执行前两条", "前", "条"))
    assert "third, the printing, hoarding or destruction of money" in Q["ln_third"]
    assert "over a solar year or any other arbitrary period" in Q["ln_rejects"]
    chk("    three laws (三条规律)", 3, told("可以把三条规律写在一起", "把", "条规律"))
    said("{功能财政（勒纳 1943）}", Y["ln_masthead"])
    assert "does not" in Q["ln_size1"] and "matter at all" in Q["ln_size2"]
    # the pitfall
    i300, y150 = F["ln_fantastic"]
    said("设国债大到每年的利息有 3000 亿美元，而充分就业时的实际国民收入只有 1500 亿美元", i300 * 1e9, y150 * 1e9)
    chk("    twice the real national income (两倍)", F["ln_twice"][0], told("利息就是国民收入的两倍", "收入的", "倍"))
    chk("    300/150 = 2", i300 / y150, F["ln_twice"][0])
    assert "The interest can be paid by borrowing still" in Q["ln_interest"]
    assert "not r owed to other nations" in Q["ln_nations"]
    assert "communist society" in Q["ln_communist"] and "fascist society" in Q["ln_communist"]


def debate(F, Y, Q):
    said("1938 年的警告，公共支出是最容易的办法", 1938)
    assert "for example by Alvin Hansen" in Q["ln_hansen"]
    said("1942 年 7 月登在《哈泼斯》杂志上的文章", F["ln_flynn"][0], mon("ln_flynn", "July"))
    assert "Harper’s Magazine for July 1942" in Q["ln_flynn"] and "An excellent example" in Q["ln_flynn"]
    assert "one penny in the pound" in Q["ln_penny"]
    chk("    one penny (一便士)", 1, told("第一部所得税法提出每镑征一便士时", "每镑征", "便士"))
    chk("    four major errors (四个大错)", F["ln_four"][0], told("这个论证有四个大错", "有", "个大错"))
    p6, d600 = F["ln_investor"]
    d240, p6b, d4000 = F["ln_240"]
    said("一位投资者 6\\% 的收益本来是 600 美元，交了所得税只剩 240 美元", p6, d600, d240)
    said("扣除抵税以后的净损失也只有 4000 美元，240 美元正好是它的 6\\%", d4000, d240, p6b)
    chk("    240 is 6 per cent of 4000", 100 * d240 / d4000, p6b)
    chk("    one hundred per cent (百分之百)", F["ln_strictly"][0] / 100, told("这只在亏损能百分之百从应税收入里扣除时", "亏损能",
                                                                          "从应税"))
    for k, ch in (("ln_err2", "In the second place"), ("ln_err3", "In the third place"), ("ln_err4", "Finally")):
        assert Q[k].startswith(ch), k
    lo, hi = F["ln_guess"]
    said("他猜在 1000 亿到 9000 亿美元之间", lo * 1e9, hi * 1e9)
    # Domar
    said("1944 年 12 月，他在《美国经济评论》上发表", Y["dm_title"], src_mon("domar1944", "December"))
    assert "Mr. Domar is with the Board of Governors of the Federal Reserve System" in Q["dm_fed"]
    assert "can be raised to any desired level" in transcription("dm_raised")
    assert "the tax rate will rise is far from evident" in transcription("dm_burden")
    assert "excluding interest paid on the public debt" in Q["dm_national"]
    said("税率趋近 100\\%", F["dm_dismal"][0])
    assert "grow without limit" in Q["dm_dismal"]
    assert "lies not in deficit financing as such" in Q["dm_lies"]
    D0, Y0, i = F["dm_start"]
    said("设开始时债务是 3000 亿美元，国民收入是 1300 亿美元，利率是 2\\%", D0 * 1e9, Y0 * 1e9, i)
    assert "an illustration only and do not represent any attempt to forecast" in transcription("dm_300y")
    s12, a6 = F["dm_a6"]
    said("社会想储蓄收入的 12\\%，政府与私人投资各吸收一半，所以$a=6\\%$", s12, a6)
    chk("    a half each (一半)", a6 / s12, told("政府与私人投资各吸收一半", "各吸收", ""))
    r2lim, r2, r3lim, r3, t2, t3 = F["dm_3and2"]
    said("收入每年增长 2\\% 时，债务与收入之比趋于 3，税率趋于 5.7\\%", r2, r2lim, t2)
    said("增长 3\\% 时，两者趋于 2 与 3.9\\%", r3, r3lim, t3)
    for r, lim, tax in ((r2, r2lim, t2), (r3, r3lim, t3)):
        d = domar(a6 / 100, i / 100, r / 100)
        chk(f"    r = {r:.0f}%: D/Y -> a/r", d["ratio"], lim, tol=1e-9)
        # the text rounds Table III's limits (5.71, 3.85) half up to one decimal
        chk(f"    r = {r:.0f}%: the tax rate's limit, per cent", 100 * d["tax"], tax, tol=0.055)
    p12, l2, l3, rr2, rr3 = F["dm_reasonable"]
    said("即使私人的净投资完全消失，政府要借走全部 12\\%，税率也只趋于 10.7\\% 与 7.4\\%", p12, l2, l3)
    chk("    a = 12%, r = 2%", 100 * domar(p12 / 100, i / 100, rr2 / 100)["tax"], l2, tol=0.05)
    chk("    a = 12%, r = 3%", 100 * domar(p12 / 100, i / 100, rr3 / 100)["tax"], l3, tol=0.05)
    assert "approaches a fairly reasonable limit" in transcription("dm_reasonable")
    domar_example(F, Y, Q)
    # Kalecki
    _, y43 = F["kl_masthead"]
    said("登在《政治季刊》1943 年 10—12 月号，大体是他 1942 年春天在剑桥马歇尔学会的一次演讲", y43,
         MONTHS["october"], MONTHS["december"], F["kl_lecture"][0])
    assert "OCTOBER-DECEMBER" in Q["kl_masthead"] and "Spring of 1942" in Q["kl_lecture"]
    assert "Marshall Society in Cambridge" in Q["kl_lecture"]
    assert "even in a capitalist system" in Q["kl_majority"] and "in exchange for exports" in Q["kl_majority"]
    assert "annual capital tax" in Q["kl_capitaltax"] and "rationing and direct taxation" in Q["kl_rationing"]
    chk("    three categories (三类)", F["kl_three"][0], told("实现充分就业的理由分成三类", "分成", "类"))
    for words in ("一是不喜欢政府干预就业问题本身", "二是不喜欢政府支出的方向", "三是不喜欢持久的充分就业"):
        say(words)
    assert "the self assurance and class consciousness of the working class would grow" in Q["kl_boss"]
    assert "as typified by the Nazi system" in Q["kl_fascism"]
    a37, b38, c37 = F["kl_1937"]
    said("1937—1938 年的美国就发生过很像这样的事，1937 年下半年繁荣的破裂", a37, b38, c37)
    assert "the second half of 1937" in Q["kl_1937"] and "drastic reduction of the budget deficit" in Q["kl_1937"]
    said("他举的例子是 1937 年", c37)
    assert "a fundamental reform" in Q["kl_reform"] and "the recurrence of fascism" in Q["kl_fight"]


def domar_example(F, Y, Q):
    """ex:warfinance-domar: the limits of eq:warfinance-domar against Domar's text and Table III."""
    D0, Y0, i = F["dm_start"]
    _, a6 = F["dm_a6"]
    t3 = F["dm_table3"]
    assert t3[:4] == [D0, Y0, a6, i] and t3[4:6] == [2, 3]
    y0, t0a, t0b, y300, t300a, t300b, lima, limb = t3[6:]
    a, ii = a6 / 100, i / 100
    d2, d3 = domar(a, ii, 0.02), domar(a, ii, 0.03)
    said("（1）$a=6\\%$，$i=2\\%$，$r=2\\%$与$r=3\\%$时", a6, i, 2, 3)
    said("（2）$a=12\\%$呢？（3）开始时债务 3000 亿美元、收入 1300 亿美元", F["dm_reasonable"][0], D0 * 1e9, Y0 * 1e9)
    said("（1）$r=2\\%$时，$a/r=3$，税率$0.02/(0.02/0.06+0.02)=0.02/0.3533\\approx5.66\\%$", 2, d2["ratio"], ii, 0.02, a,
         ii, ii, 0.02 / a + ii, 100 * d2["tax"])
    said("$r=3\\%$时，$a/r=2$，税率$0.02/(0.5+0.02)\\approx3.85\\%$", 3, d3["ratio"], ii, 0.03 / a, ii, 100 * d3["tax"])
    said("多马的正文四舍五入为 5.7\\% 与 3.9\\%", *F["dm_3and2"][4:])
    said("他的表 III 在$r=2\\%$一栏的极限印作 5.71\\%，第 300 年一行印作 5.66\\%", 2, lima, y300, t300a)
    chk("    Table III, year 300, r = 2%: the continuous model", 100 * domar(a, ii, 0.02, t=y300, D0=D0, Y0=Y0)["tax"],
        t300a, tol=0.005)
    chk("    Table III, year 300, r = 3%", 100 * domar(a, ii, 0.03, t=y300, D0=D0, Y0=Y0)["tax"], t300b, tol=0.005)
    chk("    Table III, the limit for r = 3%", 100 * d3["tax"], limb, tol=0.005)
    assert abs(100 * d2["tax"] - lima) > 0.04                                   # the misprint of the limit (5.71)
    chk("    r/a = 0.02/0.12 = 1/6", 0.02 / 0.12, 1 / 6, tol=1e-12)
    s2 = domar(0.12, ii, 0.02)
    s3 = domar(0.12, ii, 0.03)
    said("（2）$r=2\\%$时税率$0.02/(1/6+0.02)\\approx10.71\\%$，$r=3\\%$时$0.02/(0.25+0.02)\\approx7.41\\%$，与正文的 10.7\\% 与 "
         "7.4\\% 相合", 2, ii, 1, 6, ii, 100 * s2["tax"], 3, ii, 0.03 / 0.12, ii, 100 * s3["tax"], F["dm_reasonable"][1],
         F["dm_reasonable"][2])
    t0 = 100 * ii * D0 / (Y0 + ii * D0)
    said("（3）以十亿美元计，$iD/(Y+iD)=6/(130+6)\\approx4.41\\%$，与表 III 第 0 年的 4.41\\% 相同", ii * D0, Y0, ii * D0, t0,
         y0, t0a)
    chk("    year 0 is the same for both rates", t0a, t0b)
    chk("    year 0 of the continuous model", 100 * domar(a, ii, 0.02, t=0, D0=D0, Y0=Y0)["tax"], t0a, tol=0.005)


def plans(F, Y, Q):
    d6, y43 = F["fj_april6"]
    said("1943 年 4 月 6 日，美国财政部公布了", y43, mon("fj_april6", "April"), d6)
    assert "The next day the British Government issued in London" in Q["fj_april6"]
    assert "the White plan and the Keynes plan" in Q["fj_names"]
    said("《联邦储备公报》6 月号刊出两份全文", src_mon("frb1943jun", "June"))
    assert "fixed (but not unalterably) in terms of gold" in Q["fk_bancor"]
    three, p75 = F["fk_quota"]
    said("初始的份额可以参照每个国家战前三年平均的进出口之和，比如定为它的 75\\%", p75)
    chk("    three pre-war years (三年)", three, told("战前三年平均的进出口之和", "战前", "年平均"))
    assert "do not exceed their quota" in Q["fk_overdraw"]
    c1, c2 = F["fk_charge"]
    said("超过份额四分之一的部分每年交 1\\% 的费用，超过一半的部分再交 1\\%", c1, c2)
    assert "in excess of a quarter of its quota" in Q["fk_charge"] and "in excess of a half of its quota" in Q["fk_charge"]
    chk("    a quarter (四分之一)", 0.25, told("超过份额四分之一的部分", "份额", "的部分"))
    assert "remit the charges on credit balances" in Q["fk_remit"]
    chk("    a quarter of its quota within a year (四分之一)", F["fk_quarter"][0],
        told("成员国一年里增加的借方余额不得超过份额的四分之一", "份额的", ""))
    chk("    within a year (一年里)", 1, told("成员国一年里增加的借方余额", "成员国", "年里"))
    chk("    two years (两年)", 2, told("借方余额两年平均超过份额四分之一的国家", "余额", "年平均"))
    assert "on the average of at least two years" in Q["fk_twoyears"]
    said("降幅不超过 5\\% 时不必经理事会同意", F["fk_5pct"][0])
    chk("    a year (一年)", 1, told("贷方余额一年平均超过份额一半的国家", "余额", "年平均"))
    assert "exceeded ha/f of its quota on the average of at least a year" in Q["fk_ultimate"]
    # White
    said("各国份额的总和至少相当于 50 亿美元", F["fw_5bn"][0] * 1e9)
    assert "at least 5 billion dollars" in Q["fw_5bn"]
    said("成员国要向基金缴纳份额的 50\\%", F["fw_50"][0])
    chk("    four-fifths (五分之四)", F["fw_rates"][0], told("而且要五分之四的票数批准", "要", "的票数"))
    p150, p200 = F["fw_200"]
    said("头两年不超过份额的 150\\%，以后不超过 200\\%", p150, p200)
    chk("    the first year (第一年)", 1, told("第一年不超过它的份额", "第", "年"))
    chk("    the first two years (头两年)", 2, told("头两年不超过份额的", "头", "年"))
    said("那个国家每年要用黄金交 1\\% 的费用", F["fw_charge"][0])
    assert "payable in gold" in Q["fw_charge"] and "in excess of the quota" in Q["fw_charge"]
    grains, usd = F["fw_unitas"]
    said("每单位含纯金 137 又七分之一格令，合 10 美元", int(grains), usd)
    chk("    137 1/7 grains (又七分之一)", grains - int(grains), told("137 又七分之一格令", "又", "格令"))
    chk("    and 1/7 of the value column", grains, 137 + 1 / 7, tol=1e-6)
    say("格令是英美的重量单位")
    v100, one, per, one2 = F["fw_votes"]
    said("每个国家有 100 票。份额每 10 万尤尼塔斯，也就是 100 万美元，再加 1 票", v100, per, per * usd, one)
    assert "(1 million dollars)" in Q["fw_votes"] and one2 == 1
    chk("    one-fourth of the votes (四分之一)", F["fw_fourth"][0],
        told("任何国家都无权投出超过总票数四分之一的票", "总票数", "的票"))
    # the compare box
    said("{稳定基金，成员国缴纳份额的 50\\%", F["fw_50"][0])
    said("{比如说，战前三年平均进出口之和的 75\\%", p75)
    said("{总和至少 50 亿美元，按储备、收支波动与国民收入定", F["fw_5bn"][0] * 1e9)
    said("{尤尼塔斯，含纯金 137 又七分之一格令，合 10 美元", int(grains), usd)
    said("{贷方与借方余额同样收费，超过份额四分之一与一半的部分各 1\\%", c1)
    said("{基金持有的本币超过份额的部分，以黄金交 1\\%", F["fw_charge"][0])
    said("{借方余额长期过大时可以自行贬值，不超过 5\\%", F["fk_5pct"][0])
    bancor_example(F, Y, Q)


def bancor_example(F, Y, Q):
    q, bal, ex = BANCOR["quota"], BANCOR["balance"], BANCOR["excess"]
    said("设两个国家的份额都是 400，单位任意。一年平均下来，甲国有 250 的贷方余额，乙国有 250 的借方余额", q, bal, bal)
    said("基金持有的乙国货币比份额多出 150", ex)
    k1, k2 = 0.01 * (bal - q / 4), 0.01 * (bal - q / 2)
    said("（1）份额的四分之一是 100，一半是 200。超过 100 的 150 交 1\\%，得 1.5；超过 200 的 50 再交 1\\%，得 0.5。两国各交 2.0",
         q / 4, q / 2, q / 4, bal - q / 4, 1, k1, q / 2, bal - q / 2, 1, k2, keynes_charge(bal, q))
    chk("    Keynes: creditor and debtor pay the same", keynes_charge(bal, q), keynes_charge(-bal, q))
    said("（2）只有乙国要交，$150\\times1\\%=1.5$", ex, 1, white_charge(ex))
    chk("    the parts add up", k1 + k2, keynes_charge(bal, q))
    assert 0.01 * F["fk_charge"][0] == 0.01 and F["fw_charge"][0] == 1


def bw(F, Y, Q):
    y, m, d = url_date("hl1944")
    said("1944 年 5 月 23 日，上院辩论 Cmd. 6519 号文件里的原则声明", y, m, d, F["hl44_motion"][0])
    assert "almost exactly a year since the proposals for a Clearing Union" in Q["hl44_year"]
    chk("    a year (一年)", 1, told("差不多正好是一年以前", "正好是", "年以前"))
    assert "new-fangled international monetary unit" in Q["hl44_unit"]
    assert Q["hl44_names"] == "bancor, unitas, dolphin, bezant, daric"
    said("全世界的份额暂定为 25 亿英镑，英国连同皇家殖民地分到 3.25 亿英镑", F["hl44_aggregate"][0], F["hl44_325"][0])
    assert "for ourselves and the Crown Colonies" in Q["hl44_colonies"]
    assert "not intended as daily food" in Q["hl44_daily"]
    chk("    four years before (四年前)", y - Y["k_iron"], told("四年前，他在小书里也用过这个词", "", "年前"))
    assert "iron ration" in Q["k_iron"] and "iron ration" in Q["hl44_iron"]
    chk("    three things (三条)", 3, told("凯恩斯说，英国要的有三条", "有", "条"))
    assert "flights of hot money" in Q["hl44_interest"] and "we will not accept deflation" in Q["hl44_deflation"]
    assert "the explicit right to control all capital movements" in Q["hl44_heresy"]
    assert "the disabilities of the former gold standard" in Q["hl44_question"]
    assert "the exact opposite of it" in Q["hl44_opposite"] and "policy of full employment" in Q["hl44_framework"]
    assert "deferred indebtedness" in Q["hl44_stagger"]
    d1, d22, y44 = F["fa_title"][:3]
    said("1944 年 7 月 1 日到 22 日，联合国货币与金融会议在新罕布什尔州的布雷顿森林举行", y44, mon("fa_title", "July"), d1, d22)
    said("有 44 个联合国家与联系国的代表出席", F["fs_44"][0])
    tr = transcription("fa_title")
    said("8 月，最后议定书由财政大臣提交议会，编号 Cmd. 6546", mon("fa_title", "August"), F["fa_title"][-1])
    assert "Presented by the Chancellor of the Exchequer to Parliament" in tr
    _, y1944 = F["fa_par"]
    said("按国际货币基金协定第四条", )
    chk("    Article IV (第四条)", 4, told("按国际货币基金协定第四条", "第", "条"))
    assert "Art. IV" in column("juan")["fa_par"] and "Art. VI" in column("juan")["fa_capital"]
    said("或者以 1944 年 7 月 1 日的重量与成色的美元来表示", y1944, mon("fa_par", "July"), F["fa_par"][0])
    p10, p10b, h72 = F["fa_change"]
    said("改变不超过初始平价 10\\% 时，基金不得反对；再改变不超过 10\\% 时，基金可以同意或反对，但成员国要求时要在 72 小时内表态",
         p10, p10b, h72)
    chk("    the Bulletin prints the same (10, 10, 72)", F["fs_10pct"], [p10, p10b, h72])
    said("即期外汇交易的汇率只能在平价上下 1\\% 的范围内", F["fs_1pct"][0])
    said("\\chref{ch:depressionworld}讲过 1936 年英、美、法三国的声明", 1936)
    chk("    three countries (三国)", 3, told("1936 年英、美、法三国的声明", "法", "国"))
    chk("    Article VI, section 3 (第六条第三节)", [6, 3], [told("资本管制写进了第六条第三节", "第", "条第"),
                                                     told("资本管制写进了第六条第三节", "条第", "节")])
    assert "Art. VI, sec. 3" in column("juan")["fa_capital"]
    said("凯恩斯 5 月在上院说的“异端”，到 7 月成了协定的条文", m, mon("fa_title", "July"))
    assert "Each member has a right to control international capital movements" in Q["fs_capital"]
    Qs = quotas()
    said("附表 A 列出 45 个国家的份额", len(Qs) + 1)
    assert "Denmark shall be determined by the Fund after the Danish Government" in transcription("fa_denmark")
    total = sum(Qs.values())
    said("其余 44 国的份额合计 88 亿美元", len(Qs), total * 1e6)
    chk("    the Bulletin: 'totaling 8.8 billion dollars'", F["fs_88"][0] * 1e3, total)
    big = {k: Qs[k] for k in ("United States", "United Kingdom", "Union of Soviet Socialist Republics", "China", "France",
                              "India")}
    said("美国 27.5 亿美元，英国 13 亿美元，苏联 12 亿美元", *(v * 1e6 for v in list(big.values())[:3]))
    said("中国 5.5 亿美元，法国 4.5 亿美元，印度 4 亿美元", *(v * 1e6 for v in list(big.values())[3:]))
    assert sorted(Qs, key=Qs.get, reverse=True)[:6] == ["United States", "United Kingdom",
                                                       "Union of Soviet Socialist Republics", "China", "France", "India"]
    g25, g10 = F["fs_gold"]
    said("至少是份额的 25\\% 或该国官方黄金与美元净持有量的 10\\%，取两者中较小的一个", g25, g10)
    assert Q["fs_smaller"] == "whichever is the smaller."
    said("每次要交 0.75\\% 的手续费", F["fs_service"][0])
    assert "three-fourths of 1 per cent" in Q["fs_service"] and "large or prolonged use" in Q["fs_deterrent"]
    assert "limited to its original subscription" in Q["fs_notobliged"]
    assert "apportion its supply among member countries" in Q["fs_scarce"]
    # the votes
    base, one, per = F["fs_votes"]
    assert (base, per) == (VOTES["base"], VOTES["per"]) and one == 1
    said("票数按份额分配，每个成员国 250 票，份额每 10 万美元再加 1 票", base, per, one)
    us_v = votes(Qs["United States"])
    tot_v = sum(votes(q) for q in Qs.values())
    said("按附表 A 算，美国有 27,750 票。44 国合计 99,000 票，美国占 28.0\\%", us_v, len(Qs), tot_v, 100 * us_v / tot_v)
    p315, p28 = F["fs_315"]
    said("公报给的也是 28\\%", p28)
    chk("    the Bulletin's 28 per cent against 27,750/99,000", 100 * us_v / tot_v, p28, tol=0.5)
    assert "whether or not to waive any of the conditions" in Q["fs_waive"]
    chk("    one-half of the US quota (一半)", F["fs_halfus"][0], told("若基金卖出的美元达到美国份额的一半", "份额的", ""))
    said("美国的比例会是 31.5\\%", p315)
    said("英帝国合计占 25.3\\%", F["fs_empire"][0])
    assert "the British Empire controls 25.3 per cent" in Q["fs_empire"]
    said("(b) 布雷顿森林协定附表 A 的份额，与按每国 250 票、每 10 万美元再加 1 票算出的票数，占全部 44 个国家的百分比", base, per,
         one, len(Qs))
    say("凯恩斯方案向顺差国与逆差国同样收费；布雷顿森林的基本票让小国的票数多于份额")
    small = [k for k in Qs if Qs[k] < 100]                                       # the members below $100 million
    assert sum(votes(Qs[k]) for k in small) / tot_v > sum(Qs[k] for k in small) / total
    said("数据：《联邦储备公报》1943 年 6 月与 1944 年 9 月；最后议定书（Cmd. 6546）附表 A", src_year("frb1943jun"),
         src_mon("frb1943jun", "June"), src_year("frb1944sep"), src_mon("frb1944sep", "September"), F["fa_title"][-1])
    # the Senate
    said("1945 年 6 月，参议院银行与货币委员会举行听证", Y["sn_taft"], src_mon("senate1945", "June"))
    put, half, p30 = F["sn_taft"]
    said("美国拿出 27.5 亿美元", put)
    chk("    more than half (一半)", half, told("超过基金里真正的钱的一半", "钱的", ""))
    said("却只有 30\\% 的投票权", p30)
    chk("    $2,750,000,000 is the US quota of Schedule A", put / 1e6, Qs["United States"])
    said("在基金这边，美国交出 27.5 亿美元", F["sn_string"][0])
    assert "we have a veto on the loans and dollars" in Q["sn_bank"]
    assert "agrees that it will put no such restrictions" in Q["sn_norestrict"]
    assert "better than the same currency in anybody else’s hands" in Q["sn_better"]
    assert column("note")["sn_white"] == "Harry D. White" and column("note")["sn_string"] == "Senator Taft"
    # who adjusts
    assert "the main cause of deflation during the inter-war years" in Q["hl44_formula"]
    assert "release other countries from any obligation to take its exports" in Q["hl44_clause"]
    assert "temporary deficit" in Q["fs_purpose"]


def src_year(key: str) -> int:
    """The first year in the version line of source `key`."""
    return int(re.search(r"\b((?:19|20)\d\d)\b", meta()["sources"][key]["version"]).group(1))



def deeper(F, Y, Q):
    src = meta()["sources"]
    said("扫描本（麦克米伦，1940）", Y["km_date"])
    assert "Copyright permitted" in Q["km_rights"]
    _, _, _, rest, _ = F["k_money"]
    said("如把第 23 页的 1,350 百万英镑认作 1,360 百万英镑", page("k_money"), rest, 1360)
    assert "'£1,360'" in column("note")["k_money"]
    imgpages = re.search(r"pp\. vi, ([\d, and]+) \(PDF", src["keynes1940img"]["version"]).group(1)
    nums = [int(x) for x in re.findall(r"\d+", imgpages)]
    said("所以第 vi、15、16、23、28、32 页的数与句子按页面图像读出", *nums)
    assert sorted({page(r) for r in column("file") if column("file")[r] == "keynes1940img"}) == nums
    said("伍德 1941 年的预算演说与凯恩斯 1944 年的上院演说", url_date("hc1941fs")[0], url_date("hl1944")[0])
    dp = sorted({page(r) for r in column("file") if column("file")[r] == "domar1944img"})
    said("多马第 799、803、810、811 页的式子与数按页面图像读出", *dp)
    said("《联邦储备公报》1943 年 6 月号刊出的全文", src_year("frb1943jun"), src_mon("frb1943jun", "June"))
    said("布雷顿森林的最后议定书据 Cmd. 6546 的扫描页", F["fa_title"][-1])
    chk("    three disagreements (三处不一致)", 3, told("\\textbf{三处不一致。}", "{", "处"))
    B = boe()
    e = B.cy_expenditure_pct_gdp.loc[1942:1945]
    said("Harrison（1992）说平均是 70\\%，英格兰银行的日历年数据 1942—1945 年在 59\\% 到 61\\% 之间", 1992, F["hf_70"][0], 1942,
         1945, e.min(), e.max())
    assert e.max() < F["hf_70"][0] - 5
    t3 = F["dm_table3"]
    said("多马的表 III 把$r=2\\%$时税率的极限印作 5.71\\%，第 300 年一行与他的公式都是 5.66\\%，正文四舍五入为 5.7\\%", 2, t3[12],
         t3[9], t3[10], F["dm_3and2"][4])
    chk("    the formula: 5.66", 100 * domar(0.06, 0.02, 0.02)["tax"], t3[10], tol=0.005)
    Qs = quotas()
    us_v, tot_v = votes(Qs["United States"]), sum(votes(q) for q in Qs.values())
    said("塔夫脱说美国只有 30\\% 的投票权，按附表 A 与投票的公式算是 28.0\\%，公报也说 28\\%", F["sn_taft"][2],
         100 * us_v / tot_v, F["fs_315"][1])
    said("《经济学人》1940 年 1 月的“百分之三的战争”与 Sayers（1956）的数据，据 Harrison（1992）的引述", 1940, 1,
         F["hf_short"][2], 1992)
    said("据 Harrison（1998）的转述", Y["hu_goskomstat"])
    chk("    six great powers (六国)", 6, told("六国军费占国民收入的比例", "", "国军费"))
    said("日本的 GNP 平减指数只据 Shizume（2009）的引用", src_year("shizume30"))
    notes = meta()["notes"]
    for words in ("Cmd. 6437, April 1943", "Cmd. 6519, April 1944", "Department of State, 1948",
                  "Flynn's article of July 1942", "Sayers (1956)", "The Economist of 20 January 1940", "Steil",
                  "Skidelsky"):
        assert words in notes, words
    said("英国 1943 年 4 月的清算同盟白皮书（Cmd. 6437）与 1944 年 4 月的原则声明（Cmd. 6519）", 1943, 4, 6437, 1944, 4,
         F["hl44_motion"][0])
    said("Cmd. 6519 只见于上院的动议", F["hl44_motion"][0])
    said("会议的《文件与记录》（美国国务院，1948）、弗林 1942 年 7 月的文章、Sayers（1956）、1940 年 1 月的《经济学人》、Steil（2013）",
         1948, F["ln_flynn"][0], 7, F["hf_short"][2], 1940, 1, 2013)
    assert "dateOfBirth" in column("juan")["gnd_domar_born"]
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    assert "Steil" not in bib.split("% ---- 第 34 章")[1] and "Skidelsky" not in bib.split("% ---- 第 34 章")[1]


def legacy(F, Y, Q):
    said("凯恩斯 1940 年的账，用计划的支出与产能之差来判断通胀的压力", Y["km_date"])
    say("苏联增加到三倍的货币")
    chk("    trebled (三倍)", F["hu_money"][0], told("苏联增加到三倍的货币", "增加到", "倍"))


def takeaways(F, Y, Q):
    B = budget()
    said("凯恩斯 1940 年把凯恩斯交叉倒过来用", Y["km_date"])
    said("1941 年英国的预算按缺口来编，伍德估计缺口在 5 亿英镑的量级", url_date("hc1941fs")[0], F["h41_500"][0])
    said("借款的利率不到 2\\%", F["h41_short"][1])
    said("美国的联邦债务从 1939 财政年度末的 482 亿美元增加到 1946 财政年度末的 2710 亿美元", 1939, B.debt[1939] * 1e9, 1946,
         B.debt[1946] * 1e9)
    N = nipa()
    said("美国的实际 GDP 增加了 92\\%", rise(N.gdp_real_2017[1939], N.gdp_real_2017[1944]))
    said("约 150 万人死亡", F["fm_15"][0] * 1e6)
    said("1944 年的协定采用可以调整的钉住", F["fa_title"][2])
    Qs = quotas()
    said("美国的票数约占 28\\%", 100 * votes(Qs["United States"]) / sum(votes(q) for q in Qs.values()))
    chk("    trebled (三倍)", F["hu_money"][0], told("货币存量增加到三倍；德国", "增加到", "倍"))


def selfcheck(F, Y, Q):
    M = model()
    sc, scD = M["sc"], M["scD"]
    a, c, I = M1["a"], M1["c"], M1["I"]
    Yb, T0, Gs = GAP["Ybar"], GAP["T0"], GAP["Gs"]
    said("若战时的政府支出只增加到 25，税收仍是 10", Gs, T0)
    said("伍德估计的缺口是 5 亿英镑，他的新税是 2.5 亿英镑左右", F["h41_500"][0], F["h41_250"][1])
    ds = DOMAR_SC
    said("$a=6\\%$，$i=3\\%$，$r=2\\%$时", 100 * ds["a"], 100 * ds["i"], 100 * ds["r"])
    said("若甲国的贷方余额只有 150", BANCOR["sc"])
    # the answers
    said("支出线在产能处是$26+0.6\\times90+10+25=115$，缺口 15。延期支付$D=15/0.6=25$", a, c, Yb - T0, I, Gs, sc["at"],
         sc["gap"], sc["gap"], c, scD["D"])
    said("$T+D=100-(100-26-10-25)/0.6=35$，$T=10$，所以$D=25$", Yb, Yb, a, I, Gs, c, scD["TD"], T0, scD["TD"] - T0)
    chk("    the two ways agree", scD["TD"] - T0, scD["D"], tol=1e-9)
    said("工人的实际收入可能损失 20\\%", F["k_20pct"][0])
    lo, hi = F["h41_200_300"]
    said("他判断储蓄还能再多筹到 2 亿到 3 亿英镑，余下的缺口也不能估得少于 2 亿到 3 亿英镑，所以新税不少于 2 亿英镑，再留些余地，定在 "
         "2.5 亿英镑左右", lo, hi, *F["h41_gapremains"], F["h41_250"][0], F["h41_250"][1])
    d = domar(ds["a"], ds["i"], ds["r"])
    said("税率趋于$0.03/(0.02/0.06+0.03)=0.03/0.3633\\approx8.26\\%$，比$i=2\\%$时的 5.66\\% 高", ds["i"], ds["r"], ds["a"],
         ds["i"], ds["i"], ds["r"] / ds["a"] + ds["i"], 100 * d["tax"], 2, 100 * domar(0.06, 0.02, 0.02)["tax"])
    q, b = BANCOR["quota"], BANCOR["sc"]
    said("按凯恩斯方案，150 只比份额的四分之一多 50，交$50\\times1\\%=0.5$", b, b - q / 4, b - q / 4, 1, keynes_charge(b, q))
    assert b < q / 2 and white_charge(0) == 0                                   # 甲国是顺差国：怀特方案不收


def ending(F, Y, Q):
    said("1940 年 2 月，凯恩斯写下他的方案时", F["k_sign"][0], mon("k_sign", "February"))
    assert "at the onset of the first post-war slump" in Q["k_release"]
    chk("    the first slump (第一次萧条)", 1, told("到战后第一次萧条开始的时候", "战后第", "次萧条"))
    assert "a capacity to produce in excess of the current demand" in Q["k_reversed"]
    assert "preventing deflation" in Q["k_twice"]
    said("1941 年的英国只照着做了一部分", url_date("hc1941fs")[0])
    chk("    trebled (三倍)", F["hu_money"][0], told("苏联的货币存量在战争中增加到三倍", "增加到", "倍"))
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 35's question"
    assert t.index("\\end{answers}") < t.index("1940 年 2 月，凯恩斯写下他的方案时")
    ch35 = (ROOT / "zh" / "ch35_reconstruction.tex").read_text(encoding="utf-8")
    assert f"\\guidequestion{{{NEXT}}}" in ch35                               # Chapter 35's question


def models() -> None:
    """The key equations, and their arithmetic checked with numbers."""
    rng = np.random.default_rng(34)
    for _ in range(30):
        a, c, I, G = rng.uniform(5, 40), rng.uniform(0.1, 0.9), rng.uniform(5, 30), rng.uniform(0, 60)
        Yb, T, D = rng.uniform(80, 200), rng.uniform(0, 50), rng.uniform(0, 30)
        g = gap(G, T, D, Yb, a, c, I)
        # eq:warfinance-gap: the gap is spending at capacity minus capacity; T and D lower it by c each
        chk("    gap = C + I + G - Ybar", g, a + c * (Yb - T - D) + I + G - Yb, tol=1e-9)
        h = rng.uniform(0.1, 5)
        chk("    d gap / dT = -c", (gap(G, T + h, D, Yb, a, c, I) - g) / h, -c, tol=1e-9)
        chk("    d gap / dD = -c", (gap(G, T, D + h, Yb, a, c, I) - g) / h, -c, tol=1e-9)
        # the closing condition
        TD = closing(G, Yb, a, c, I)
        chk("    gap = 0 at T + D = Ybar - (Ybar - a - I - G)/c", gap(G, TD - D, D, Yb, a, c, I), 0, tol=1e-8)
        # at a zero gap the cross is in equilibrium at capacity: Y = (a - c(T + D) + I + G)/(1 - c) = Ybar
        chk("    zero gap: equilibrium at capacity", (a - c * TD + I + G) / (1 - c), Yb, tol=1e-8)
        # Domar: the continuous model converges to the limits
        aa, ii, rr = rng.uniform(0.01, 0.2), rng.uniform(0.005, 0.06), rng.uniform(0.005, 0.06)
        lim = domar(aa, ii, rr)
        far = domar(aa, ii, rr, t=5000 / rr / 10)
        chk("    D/Y -> a/r", far["ratio"], lim["ratio"], tol=1e-6, rel=1e-6)
        chk("    tax -> i/(r/a + i)", lim["tax"], ii / (rr / aa + ii), tol=1e-12)
        assert domar(aa, ii, 2 * rr)["tax"] < lim["tax"] < domar(aa, 2 * ii, rr)["tax"]   # 增长越快负担越轻，利率越高越重
        # the charges: Keynes symmetric, White only above the quota
        q, b = rng.uniform(100, 1000), rng.uniform(-1000, 1000)
        chk("    Keynes: credit and debit pay the same", keynes_charge(b, q), keynes_charge(-b, q), tol=1e-12)
        assert keynes_charge(q / 4, q) == 0 and white_charge(-1) == 0
    # r = 0: the ratio grows without limit, the tax rate tends to 100 per cent (Domar's 'dismal' case)
    big = (300 + 0.06 * 130 * 1000) / 130
    chk("    r = 0: tax rate -> 1", 0.02 * big * 1e3 / (1 + 0.02 * big * 1e3), 1, tol=1e-3)
    # the key equations as the text prints them
    t = TEX.read_text(encoding="utf-8")
    eqs = {lab: body.strip() for body, lab in re.findall(r"\\begin\{keyeq\}\n(.*?)\\label\{(eq:[^}]+)\}", t,
                                                         re.DOTALL)}
    assert sorted(eqs) == ["eq:warfinance-domar", "eq:warfinance-gap", "eq:warfinance-laws"], sorted(eqs)
    assert eqs["eq:warfinance-gap"] == ("\\text{缺口}=a+c(\\bar Y-T-D)+I+G-\\bar Y,\\qquad \\text{缺口}=0\\iff "
                                         "T+D=\\bar Y-\\frac{\\bar Y-a-I-G}{c}."), eqs["eq:warfinance-gap"]
    assert eqs["eq:warfinance-domar"] == ("\\frac{D}{Y}\\;\\longrightarrow\\;\\frac{a}{r},\\qquad \\text{税率}="
                                           "\\frac{iD}{Y+iD}\\;\\longrightarrow\\;\\frac{i}{r/a+i}."), eqs["eq:warfinance-domar"]
    # Domar's own words for the limits (p. 810, read on the page image)
    assert "a/r" in transcription("dm_limit") and "i/(r/a + i)" in transcription("dm_limit")
    # eq:warfinance-laws is Chapter 1's eq:intro-budget without the foreign-currency debt, with its three terms marked
    # as the three laws
    laws = eqs["eq:warfinance-laws"]
    intro = (ROOT / "zh" / "ch01_intro.tex").read_text(encoding="utf-8")
    end = intro.index("\\label{eq:intro-budget}")
    intro = intro[intro.rindex("\\begin{keyeq}", 0, end):end]
    for term in ("G_t-T_t", "i_{t-1}B_{t-1}", "\\Delta B_t", "\\Delta H_t"):
        assert term in laws and term in intro, term
    assert "B^{f}" in intro and "B^{f}" not in laws
    for law in ("第一条", "第二条", "第三条"):
        assert f"\\text{{{law}}}" in laws, law


def figures_data() -> None:
    """What the figures assert of their data."""
    B = boe()
    assert B.cy_expenditure_pct_gdp.between(5, 70).all() and B.cy_receipts_pct_gdp.between(5, 40).all()
    assert B.debt_pct_gdp.between(20, 270).all()
    U = budget()
    assert (U.outlays > 0).all() and (U.receipts > 0).all()
    R = debt_ratio()
    assert R.idxmax() == 1946 and R.between(40, 125).all()
    M = model()
    assert M["war"]["b0"] > M["taxed"]["b0"] > M["deferred"]["b0"] == M["peace"]["b0"]
    Qs = quotas()
    assert len(Qs) == 44 and all(v > 0 for v in Qs.values())


# ---------------------------------------------------------------------------------------------------
# 5. The book
# the life dates from rows of the snapshot: words -> (row, index of the birth year, index of the death year)
ROW_LIVES = {"John Maynard Keynes，1883—1946": ("loc_keynes", 0, 1),
             "Kingsley Wood，1881—1943": ("loc_wood", 0, 1),
             "Michał Kalecki，1899—1970": ("bnf_kalecki", 0, 1),
             "John Simon，1873—1954": ("loc_simon", 0, 1),
             "Hermann Göring，1893—1946": ("loc_goring", 0, 1),
             "Fritz Sauckel，1894—1946": ("loc_sauckel", 0, 1),
             "Abba P. Lerner，1903—1982": ("loc_lerner", 0, 1),
             "Alvin H. Hansen，1887—1975": ("loc_hansen", 0, 1),
             "John T. Flynn，1882—1964": ("loc_flynn", 0, 1),
             "Harry Dexter White，1892—1948": ("loc_white", 0, 1),
             "Robert A. Taft，1889—1953": ("loc_taft", 0, 1),
             "Dean Acheson，1893—1971": ("loc_acheson", 0, 1)}
# the beginning of each record's heading
HEADS = {"loc_keynes": "Keynes, John Maynard", "loc_wood": "Wood, Kingsley", "bnf_kalecki": "Michał Kalecki",
         "loc_simon": "Simon, John Allsebrook Simon", "loc_goring": "Göring, Hermann", "loc_sauckel": "Sauckel, Fritz",
         "loc_lerner": "Lerner, Abba P.", "loc_hansen": "Hansen, Alvin H.", "loc_flynn": "Flynn, John T.",
         "loc_white": "White, Harry Dexter", "loc_taft": "Taft, Robert A.", "loc_acheson": "Acheson, Dean"}
# what other chapters tell: (words of this chapter, chapter where it is told, words there)
EVENTS = [("\\chref{ch:islm}讲过汉森（Alvin H. Hansen，1887—1975）1938 年的警告，公共支出是最容易的办法，危险也在这里",
           "ch33_islm", "公共支出是所有复苏办法里最容易的一种，“危险也就在这里”"),
          ("\\chref{ch:islm}讲过这次衰退的几种解释，卡莱茨基的说法属于财政的解释", "ch33_islm", "\\textbf{财政的解释。}"),
          ("\\chref{ch:alternatives}讲过 MEFO 票据，到 1938 年 4 月 1 日停用时", "ch30_alternatives",
           "到 1938 年 4 月 1 日停用时，在外的 MEFO 票据有 120 亿帝国马克"),
          ("\\chref{ch:alternatives}讲过，1936 年以后日本的军费迅速增加，财政转入战时财政，1937—1940 年 GNP 平减指数平均每年涨 "
           "11.9\\%", "ch30_alternatives", "1937—1940 年，GNP 平减指数平均每年涨 11.9\\%"),
          ("\\secref{sec:alternatives-repressed}已经讲过", "ch30_alternatives", "\\label{sec:alternatives-repressed}"),
          ("\\chref{ch:interwar}讲过，战间期的金汇兑本位节省了黄金，却让各国的储备依赖对储备中心国的信心", "ch27_interwar",
           "金汇兑本位节省的是黄金，增加的是对储备中心国的信心"),
          ("\\chref{ch:depressionworld}讲过 1936 年英、美、法三国的声明，希望没有哪个国家谋求不合理的竞争性汇率优势",
           "ch29_depressionworld", "三国政府希望，没有哪个国家会谋求“不合理的竞争性汇率优势”"),
          ("接\\exref{ex:generaltheory-cross}的棉布经济，$a=26$，$c=0.6$，$I=10$", "ch32_generaltheory",
           "沿用\\exref{ex:accounts-thrift}的棉布经济，收入 90，家庭买布 80，投资 10。设消费函数是$C=26+0.6Y$"),
          ("用\\chref{ch:intro}的式~\\eqref{eq:intro-budget}", "ch01_intro", "\\label{eq:intro-budget}"),
          ("物质生产部门的净产值是计划经济的产出口径（\\chref{ch:soviet}）", "ch31_soviet", "物质生产部门的净产值"),
          ("那是\\chref{ch:weimar}的故事", "ch26_weimar", "\\label{ch:weimar}")]
# the chapters this one hands on to
LATER = {"ch:reconstruction": "ch35_reconstruction", "ch:brettonwoods": "ch36_brettonwoods", "ch:mundell": "ch37_mundell",
         "ch:phillips": "ch38_phillips", "ch:budget": "ch50_budget", "ch:moderation": "ch62_moderation",
         "ch:minsky": "ch63_minsky", "ch:abenomics": "ch67_abenomics", "ch:stagnation": "ch70_stagnation",
         "ch:fiscaldominance": "ch75_fiscaldominance"}


def book(F, Q):
    """Life dates and what other chapters tell."""
    t = tex_text()
    for words, (rid, i, j) in ROW_LIVES.items():
        assert words in t, words
        assert f"{F[rid][i]:.0f}—{F[rid][j]:.0f}" in words, (words, rid)
        assert Q[rid].startswith(HEADS[rid]), (rid, Q[rid])                      # the person of the record
        COVERED.append(words)
    # Domar: the GND record (dateOfBirth, dateOfDeath)
    words = f"Evsey D. Domar，{F['gnd_domar_born'][0]:.0f}—{F['gnd_domar_died'][0]:.0f}"
    assert words in t and Q["gnd_domar"] == "Domar, Evsey D.", words
    COVERED.append(words)
    for here, ch, there in EVENTS:
        assert here in t, here
        assert there in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (ch, there)
    for label, ch in LATER.items():
        assert f"{{{label}}}" in t, label
        assert f"\\label{{{label}}}" in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (label, ch)
    print(f"ok {len(ROW_LIVES) + 1} life dates, {len(EVENTS)} statements of other chapters, {len(LATER)} later chapters")


def witnesses(F, Q):
    """Second witnesses of statements of the text, and the bibliography block of the chapter."""
    # Keynes's account: the OCR text of p. 16 and the image of p. 15
    assert F["k_1625"][1:] == [F["k_output"][3], F["k_output"][6], F["k_output"][7]]
    # the Bulletin of September 1944 and the Final Act: the bands of par changes, the 44 members, the quotas
    assert F["fs_10pct"] == F["fa_change"] and F["fs_44"][0] == len(quotas())
    assert F["fs_88"][0] * 1e3 == sum(quotas().values())
    # Taft's $2,750,000,000 is the US quota (twice in the hearings)
    assert F["sn_taft"][0] == F["sn_string"][0] == quotas()["United States"] * 1e6
    # Domar: his text rounds his table and his formula
    t3 = F["dm_table3"]
    assert round(t3[10], 1) == F["dm_3and2"][4] and round(t3[11], 1) == F["dm_3and2"][5]
    # the deaths in Bengal: the commission's own figure lies inside the range of its first page
    assert F["fm_between"][0] <= F["fm_15"][0] * 1e6 <= F["fm_between"][1]
    # the US federal budget: Historical Statistics (Y 339-342) against Chapter 33's reading of the same table
    I = load_snapshot("islm_facts", dtype=str, keep_default_na=False)[0].set_index("id")
    for y in (1939, 1940, 1941):
        old = [float(x) for x in I.loc[f"cy_{y}", "value"].split(";")]
        assert old == F[f"cy_{y}"][:4], y
    # unemployment in 1941: Chapter 28's table and Chapter 33's ending
    assert annual().loc[1941, "unemployment_pct"] == 9.9
    # the Bank of England's financial and calendar years agree on the war's peak
    B = boe()
    assert B.fy_expenditure_gbp_mn.loc[1939:1945].idxmax() == B.cy_expenditure_pct_gdp.loc[1939:1945].idxmax() == 1944
    # the licences
    m = meta()
    lic = m["license"]
    for rid in ("ln_copyright", "bjcr", "ide_reprint", "gnd_licence", "km_rights"):
        assert Q[rid] in lic and f"row {rid}" in lic, rid
    for words in ("Contains Parliamentary information licensed under the Open Parliament Licence v3.0.",
                  "may still be in copyright in the United States", "short phrases only", "public domain",
                  "out of Crown copyright", "The Library of Congress is not aware of any copyright restrictions",
                  "Licence Ouverte", "public data"):
        assert words in lic, words
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    start = bib.index("% ---- 第 34 章")
    following = re.search(r"^% ---- 第 \d+ 章", bib[start + 1:], re.MULTILINE)
    end = start + 1 + following.start() if following else bib.index("\\end{thebibliography}")
    block = bib[start:end]
    assert "data/fetch/warfinance34.py" in block and "data/fetch/boe_millennium_gb34.py" in block
    items = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", block)}
    allitems = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", bib)}
    hansard = "“Contains Parliamentary information licensed under the Open Parliament Licence v3.0.”"
    assert hansard in items["hansard1941"] and hansard in items["hansard1944"]
    assert Q["ln_copyright"] in items["lerner1943"] and "只引短语" in items["lerner1943"]
    assert "dc.rights: Copyright permitted" in items["keynes1940"] and "可能仍受版权保护" in items["keynes1940"]
    for key in ("kalecki1943", "domar1944", "harrison1998a", "harrison1998b", "harrison1992"):
        assert "只引短语，其余转述" in items[key], key
    for key in ("frb1943", "frb1944", "senate1945", "arfr1942", "census1975y34"):
        assert "公有领域" in items[key], key
    assert "已不受王室版权保护" in items["bw1944"] and "保护期已过" in items["famine1945"]
    assert Q["gnd_licence"] in items["gnd34"] and "公共数据" in items["loc34"]
    assert Q["bjcr"] in allitems["bojchron"] and Q["ide_reprint"] in allitems["ide2003"]
    assert "The Library of Congress is not aware of any copyright restrictions" in allitems["nca1947"]
    assert "The Library of Congress is not aware of any copyright restrictions" in allitems["nca1946b"]
    assert "Licence Ouverte" in allitems["bnf32"]
    for rid in ROW_LIVES.values():
        r = rid[0]
        if r.startswith("loc_"):
            head = Q[r].replace("-", "--")
            assert any(head in allitems[k] for k in ("loc34", "loc30", "loc32", "loc33")), r
    # every source of the snapshot is named by its URL in its item (the page images with the text they belong to)
    item_of = {"keynes1940img": "keynes1940", "keynes1940meta": "keynes1940",
               "hc1941fs": "hansard1941", "hc1941wp": "hansard1941", "hc1941gap": "hansard1941",
               "hc1941sav": "hansard1941", "hc1941tax": "hansard1941", "hc1941end": "hansard1941",
               "hl1944": "hansard1944", "domar1944img": "domar1944", "frb1943jun": "frb1943", "frb1944sep": "frb1944",
               "finalact1944": "bw1944", "arfr1942img": "arfr1942", "famine1945img": "famine1945",
               "famine1945meta": "famine1945", "census_y34": "census1975y34", "imtj30": "nca1947",
               "nca2_30": "nca1946b", "shizume30": "shizume2009", "ide30": "ide2003", "bojhist30": "bojchron",
               "bojcr30": "bojchron", "loc_goring30": "loc30", "loc_sauckel30": "loc30", "loc_keynes32": "loc32",
               "bnf_kalecki32": "bnf32", "loc_hansen33": "loc33", "gnd_domar34": "gnd34"}
    for key, s in m["sources"].items():
        item = "loc34" if key.startswith("loc_") and key.endswith("34") else item_of.get(key, key)
        assert s["url"] in allitems[item].replace("\\%", "%").replace("\\_", "_"), key
    assert load_snapshot("boe_millennium_gb_1913_1950")[1]["url"] in allitems["boe2017"] or "Millennium" in allitems["boe2017"]
    keys = set(allitems)
    cited = {k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", tex_text()) for k in c.split(",")}
    assert cited <= keys, sorted(cited - keys)
    assert set(items) <= cited, sorted(set(items) - cited)
    srcs = set(m["sources"])
    for key in items:                                                              # every work of the block is a source
        assert key in srcs or key in item_of.values() or key == "loc34", key
    print(f"ok {len(cited)} works cited, {len(items)} of them in the bibliography block of Chapter 34")


NAMES = ("Harrison|Goldenweiser|Bourneuf|Sayers|Ide|Shizume|Balderston|Ellman|Maksudov|Steil|Skidelsky")


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
    # the human cost is stated (forced labour, plunder, famine), and repressed inflation is left to Chapter 30
    for words in ("强迫劳动", "奴隶劳工", "掠夺", "饥荒", "饿死"):
        assert words in main, words
    assert "\\secref{sec:alternatives-repressed}" in main


def main() -> None:
    df = _rows()
    F, Y, Q = facts(), years(), quotes()
    check_readings(df)
    check_text(df)
    guide(F, Y, Q)
    opening(F, Y, Q)
    world(F, Y, Q)
    gap_section(F, Y, Q)
    budget41(F, Y, Q)
    us(F, Y, Q)
    soviet(F, Y, Q)
    germany_japan_bengal(F, Y, Q)
    lerner(F, Y, Q)
    debate(F, Y, Q)
    plans(F, Y, Q)
    bw(F, Y, Q)
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
