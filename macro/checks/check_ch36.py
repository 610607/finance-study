"""Chapter 36 (布雷顿森林体系的运行): every number and every quotation in zh/ch36_brettonwoods.tex.

    python3 checks/check_ch36.py

The snapshot data/snapshots/brettonwoods_facts.csv holds the quotations of the chapter's sources, each with its page
(the rows read on a page image carry no quotation and transcribe the words in their note); the quotations are
checked against the documents by data/fetch/verify_web_quotes.py, and data/fetch/brettonwoods36.py fetches the
documents. This script

1. reads the numbers of every row from its quotation (or transcription) by the rules of READINGS and compares them
   with the value column; the tables read on page images (Bordo's Table 1.2, Garber's Table 9.1, the tables of the
   Statistical Abstract) are read again from their transcriptions;
2. finds every “…” of the text among the renderings of TRANSLATIONS, and the words of the source each one renders
   (KEYWORDS) in the row;
3. checks each number of the text with said(): the phrase is in the text and each number is the value of a row, a
   teaching input, or arithmetic on them (the reserve arithmetic of eq:brettonwoods-triffin, the cover ratios of the
   Statistical Abstract, the sterling example); every Arabic number of the text must lie in a phrase said() read
   (coverage());
4. checks the key equation with random numbers, the data of the figures (figsrc/fig_ch36.py imports gold_series()
   and parities()), the life dates against the authority records, what other chapters tell, the licences and the
   bibliography block of Chapter 36, and the editor's limits;
5. lists the rows no "% 据:" anchor of the text names (common.anchors).

Set CH36_TEX to a scratch copy of the chapter to run the checks on it (mutation tests).
"""
from __future__ import annotations

import datetime
import os
import re
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from common import ROOT, anchors, load_snapshot, quoted

TEX = Path(os.environ.get("CH36_TEX", ROOT / "zh" / "ch36_brettonwoods.tex"))   # a scratch copy for mutation tests
GUIDE = "美元为什么既是体系的支柱，又是它的隐患？"
PREV = GUIDE                                        # Chapter 35's NEXT
NEXT = "固定汇率、资本自由流动、独立的货币政策，为什么只能三选二？哪些地区适合共用一种货币？"   # Chapter 37's question
MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"], 1)}
MOIS = {m: i for i, m in enumerate(["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
                                    "septembre", "octobre", "novembre", "décembre"], 1)}


def chk(what: str, value, expected=None, tol: float = 1e-6, rel: float = 0.0) -> float:
    """quoted() with a tolerance for floating-point error; a list is compared element by element."""
    if isinstance(value, (list, tuple)):
        assert expected is not None and len(value) == len(expected), (what, value, expected)
        for i, (v, e) in enumerate(zip(value, expected)):
            quoted(f"{what} [{i + 1}]", float(v), e, tol=tol, rel=rel)
        return float(value[0])
    return quoted(what, float(value), expected, tol=tol, rel=rel)


# ---------------------------------------------------------------------------------------------------
# Loaders
@lru_cache(maxsize=None)
def _rows() -> pd.DataFrame:
    df, m = load_snapshot("brettonwoods_facts", dtype=str, keep_default_na=False)
    assert 36 in m["used_in"] and m["fetch"] == "data/fetch/brettonwoods36.py"
    assert df["id"].is_unique
    return df


@lru_cache(maxsize=None)
def meta() -> dict:
    return load_snapshot("brettonwoods_facts")[1]


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


def has(rid: str, *words: str) -> None:
    """Each of the words is in what row rid says."""
    for w in words:
        assert w in words_of(rid), (rid, w)


def mon(rid: str, name: str) -> int:
    """The month `name` (English, an English abbreviation such as 'Nov.', or French), asserted to be in what row rid
    says."""
    has(rid, name)
    key = name.lower()
    if key in MONTHS:
        return MONTHS[key]
    if key in MOIS:
        return MOIS[key]
    return next(i for m, i in MONTHS.items() if m.startswith(key.rstrip(".")))


def page(rid: str) -> int:
    """The first page number of a row's juan column: 'p. 15 (PDF p. 24)' -> 15."""
    return int(re.search(r"pp?\. (\d+)", column("juan")[rid]).group(1))


def url_date(key: str) -> tuple[int, int, int]:
    """The date in a Historic Hansard URL: .../commons/1967/nov/20/... -> (1967, 11, 20)."""
    y, m, d = re.search(r"/(\d{4})/([a-z]{3})/(\d\d)/", meta()["sources"][key]["url"]).groups()
    return int(y), next(i for k, i in MONTHS.items() if k.startswith(m)), int(d)


def bis_year(key: str) -> int:
    """The year of a BIS Annual Report, from the place and date of its version line ('Basle, 12th June 1950')."""
    return int(re.search(r"Basle, \d+(?:st|nd|rd|th) [A-Z][a-z]+ (\d{4})", meta()["sources"][key]["version"]).group(1))


def edition(key: str) -> int:
    """The edition of the Statistical Abstract: 'Statistical Abstract of the United States 1964' -> 1964."""
    return int(re.search(r"Statistical Abstract of the United States (\d{4})", meta()["sources"][key]["version"])[1])


def table_no(key: str) -> str:
    """'Table 1211' -> '1211'; 'Table 1.2' -> '1.2'."""
    return re.search(r"Table (\d+(?:\.\d+)?)", meta()["sources"][key]["version"]).group(1)


def src_year(key: str) -> int:
    """The year of publication in the version line of source `key`: '(eds.), ..., 1993'."""
    return int(re.search(r"(?:Press for the NBER, |\(eds\.\) )(\d{4})", meta()["sources"][key]["version"]).group(1))


def chapter(name: str) -> str:
    """Another chapter's text without its comment lines."""
    t = (ROOT / "zh" / f"{name}.tex").read_text(encoding="utf-8")
    return "\n".join(l for l in t.splitlines() if not l.lstrip().startswith("%"))


# ---------------------------------------------------------------------------------------------------
# 1. Readings of the numbers (the same rules as the script that wrote the snapshot)
SMALL = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "eleven": 11, "twelve": 12, "fourteen": 14, "fifteen": 15, "seventeen": 17}
TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
WORDS = {"two-thirds": 2 / 3, "a quarter": 0.25, "half": 0.5, "one-half": 0.5, "one-third": 1 / 3}


def cardinal(s: str) -> float:
    """An English cardinal: 'three', 'thirty-two', 'twenty-one'."""
    return float(sum(SMALL.get(w, 0) + TENS.get(w, 0) for w in s.lower().replace("-", " ").split()))


def figure(s: str) -> float:
    """'1,665', '30.5', '.18'."""
    return float(s.replace(",", ""))


ZH_DIGITS = {"〇": 0, "零": 0, "一": 1, "两": 2, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
ZH_UNITS = {"十": 10, "百": 100, "千": 1000, "万": 10 ** 4, "亿": 10 ** 8}


def zh(s: str) -> float:
    """A Chinese numeral: '六', '十五', '三分之二', '一半', '三成'."""
    if "分之" in s:
        b, a = s.split("分之")
        return zh(a) / zh(b)
    if s.endswith("半"):                                                       # '一半': one half
        return 0.5 * (zh(s[:-1]) if s[:-1] else 1)
    if s.endswith("成"):                                                       # '三成': three tenths
        return zh(s[:-1]) / 10
    big, total, part = 0, 0, 0
    for ch in s:
        if ch in ZH_DIGITS:
            part = ZH_DIGITS[ch]
        elif ch in "万亿":
            big += max(total + part, 1) * ZH_UNITS[ch]
            total, part = 0, 0
        else:
            total += max(part, 1) * ZH_UNITS[ch]
            part = 0
    return float(big + total + part)


FIGURES = re.compile(r"\d[\d,]*(?:\.\d+)?|\.\d+")
EN, NUM, WD = "en", "num", "word"
# id -> [(phrase, how)], in order. A phrase 'context|word' is searched as a whole and read from `word`. Rows not
# listed are read with all the figures of the quotation (or of the transcription of a page image). An empty list: the
# row prints no number of the story (or only a misreading of one, named in MISPRINTS).
READINGS: dict[str, list[tuple[str, str]]] = {
    'b66_table': [('end-|1965', 'num'), ('- |1,665', 'num'), ('|13,806', 'num')],
    'b66_speculation': [],
    'b66_pool': [('a quarter', 'word')],
    'b66_recouped': [],
    'b66_control': [],
    'bo_twothirds': [('two-thirds', 'word')],
    'bo_parvalues': [('twelve', 'en'), ('thirty-two', 'en'), ('December |1946', 'num')],
    'bo_oeec': [('of |1946', 'num'), ('a |1947', 'num'), ('$|9', 'num')],
    'bo_censure': [('IV, section |5', 'num')],
    'bo_notice': [('twenty-four', 'en'), ('section |5', 'num'), ('than |10', 'num'), ('seventy-two', 'en')],
    'bo_loan_year': [('within |one', 'en')],
    'b62_gab': [('December |1961', 'num'), ('ten', 'en'), ('$|6', 'num')],
    'bo_cripps': [('Two', 'en'), ('On |18', 'num'), ('September |1949', 'num'), ('twenty-four', 'en'), ('by |30.5', 'num'), ('$|2.80', 'num'), ('twenty-three', 'en')],
    'b50_exports': [],
    'b50_unclear': [],
    'b50_materials': [],
    'b50_setback': [('of |1949', 'num'), ('since |1947', 'num')],
    'b50_trade': [('From |1947', 'num'), ('of |1950', 'num'), ('one-half', 'word'), ('one-third', 'word')],
    'b68_5056': [('years |1950', 'num'), ('about $|1.2', 'num')],
    'b68_indicator': [],
    'b68_constructive': [],
    'b68_defence50s': [],
    'b68_newgold': [('about $|400', 'num'), ('averaged $|440', 'num')],
    'b68_distribution': [],
    'b68_suez': [],
    'bo_epu_month': [],
    'b59_straitjacket': [],
    'b59_winding': [],
    'bo_eight': [('eight', 'en'), ('on |27', 'num'), ('December |1958', 'num')],
    'ga_t91': [('1958', 'num'), ('1961', 'num'), ('1962', 'num'), ('1965', 'num'), ('1967', 'num'), ('$|2.80', 'num'), ('$|2.40', 'num'), ('1968', 'num'), ('1969', 'num'), ('from |.18', 'num'), ('to |.16', 'num'), ('$|0.25', 'num'), ('$|0.273', 'num'), ('1970', 'num')],
    'b59_fr_prices': [('In |1958', 'num'), ('of |8.9', 'num'), ('and |6.5', 'num')],
    'b61_art8': [('15', 'num'), ('1961', 'num'), ('ten', 'en')],
    'b61_art8b': [],
    'b61_art8c': [],
    'b61_drawings': [('$|131', 'num'), ('nearly |half', 'word')],
    'b61_repaid': [('twenty-one', 'en')],
    'bo_preconv': [],
    'bo_whywell': [],
    'bo_art8': [('until |1961', 'num')],
    'b61_1960': [],
    'b61_cuts': [('January |1961', 'num')],
    'b61_three': [('three', 'en')],
    'b61_dm4': [('is |0.222168', 'num'), ('D M |4', 'num')],
    'b61_inner': [],
    'b61_onceforall': [('four', 'en')],
    'b61_substitute': [],
    'b61_inflows': [('$|200', 'num'), ('$|250', 'num')],
    'bo_tr_gold': [],
    'bo_tr_rest': [],
    'bo_tr_crisis': [],
    'bo_tr_solution': [],
    'ga_identification': [('1960', 'num')],
    'ga_gab': [],
    'ga_alleviate': [],
    'ga_accelerate': [],
    'sa72_head': [('No. |1271', 'num'), ('|1955', 'num'), ('to |1972', 'num'), ('in |1', 'num')],
    'sa72_official': [('Official |3', 'num'), ('1955 |6,953', 'num'), ('1960 |10,212', 'num'), ('1965 |13,066', 'num'), ('1967 |14,027', 'num'), ('1968 |11,318', 'num'), ('1969 |11,077', 'num'), ('1970 |19,333', 'num'), ('1971 |39,001', 'num'), ('1972', 'num'), ('(prel.) |41,030', 'num')],
    'sa68_official': [('Official |2', 'num'), ('1955 |6,953', 'num'), ('1960 |10,212', 'num'), ('1964 |13,220', 'num'), ('1965 |13,066', 'num'), ('1966 |12,539', 'num'), ('1967', 'num'), ('March |12,365', 'num'), ('1967', 'num'), ('Dec. |14,069', 'num'), ('1968', 'num'), ('(prel.) |12,961', 'num')],
    'sa64_foreign': [('1955 |11,720', 'num'), ('1959 |16,231', 'num'), ('1960 |17,260', 'num'), ('1961', 'num'), ('2 |18,781', 'num'), ('1962 |19,874', 'num'), ('1963', 'num'), ('March |20,189', 'num'), ('1963', 'num'), ('Dec. |21,307', 'num'), ('1964', 'num'), ('March |21,192', 'num')],
    'sa64_official': [('Official |4', 'num'), ('1955 |6,953', 'num'), ('1959 |9,154', 'num'), ('1960 |10,212', 'num'), ('1961 |10,940', 'num'), ('1962 |11,963', 'num'), ('1963', 'num'), ('March |11,785', 'num'), ('1963', 'num'), ('Dec. |12,467', 'num'), ('1964', 'num'), ('March |11,988', 'num')],
    'sa64_fn4': [('4', 'num')],
    'sa64_total': [('1955', 'num'), ('|13,601', 'num'), ('1959', 'num'), ('1 |19,389', 'num'), ('1960', 'num'), ('|21,272', 'num')],
    'bo_kennedy': [('68', 'num'), ('on |31', 'num'), ('October |1960', 'num')],
    'b62_threat': [],
    'bo_pool_nov': [('November |1961', 'num'), ('seven', 'en'), ('$|35.00', 'num')],
    'bo_pool40': [('seven', 'en'), ('|40', 'num')],
    'bo_pool60': [('seven', 'en'), ('|60', 'num'), ('Schwartz |1989', 'num'), ('|342', 'num')],
    'ga_pool50': [('|50', 'num'), ('seven', 'en')],
    'b68_twist': [],
    'b68_mix': [],
    'b68_1961_65': [('years |1961', 'num'), ('in |1958', 'num')],
    'b68_reluctant': [],
    'b68_jan1968': [('January |1968', 'num')],
    'b68_programme': [('January |1968', 'num')],
    'b68_dangerous': [('fifteen', 'en')],
    'b68_peace': [],
    'b68_limits': [],
    'b68_france_pool': [],
    'b68_tons': [('three', 'en'), ('four', 'en')],
    'b68_q4': [('$|1.4', 'num'), ('|1967', 'num')],
    'b68_paris': [('Friday, |15', 'num'), ('$|44', 'num')],
    'fr191_meeting': [('March |16', 'num'), ('and |17', 'num'), ('seven', 'en')],
    'fr191_ukall': [],
    'fr191_replace': [],
    'fr191_two': [('two', 'en'), ('$|35', 'num')],
    'b68_closed': [('two', 'en'), ('$|38', 'num')],
    'bo_sdr_def': [('One', 'en'), ('one', 'en')],
    'bo_sdr_95': [('$|9.5', 'num'), ('three', 'en')],
    'fr193_date': [('March |29', 'num'), ('and |30', 'num'), ('1968', 'num')],
    'bo_uk_problem': [('G|10', 'num'), ('Tew |1988', 'num'), ('chap. |10', 'num'), ('in the |1950', 'num'), ('IMF in |1957', 'num')],
    'bo_shocks': [],
    'bo_basle68': [('Basle in |1968', 'num'), ('excess of |10', 'num')],
    'bo_fn52': [('in |1964', 'num'), ('until |1967', 'num'), ('dollar in |1968', 'num')],
    'h67_claims': [],
    'h67_productivity': [],
    'h67_dividends': [],
    'h67_vulnerable': [],
    'h67_loan': [],
    'h67_exportled': [],
    'h67_winter': [],
    'h_copyright': [],
    'im_rueff': [],
    'im_notice': [],
    'bo_convert': [('|1965', 'num'), ('since |1934', 'num')],
    'ga_france2': [],
    'ga_buyback': [('$|1', 'num')],
    'b70_fr_wages': [('of |1968', 'num'), ('mid|1969', 'num')],
    'b70_fr_measures': [('in |1968', 'num')],
    'b70_outside': [('during |1969', 'num')],
    'b70_eurodollar': [],
    'ei_consensus': [('six', 'en')],
    'bo_us_lower': [('|1968', 'num'), ('G|7', 'num')],
    'bo_asym': [],
    'bo_exporting': [],
    'bo_fn58': [],
    'ga_bank': [],
    'ga_french': [],
    'ga_cheap': [],
    'ga_predicted': [],
    'nber_cover': [],
    'bis_reuse': [],
    'bis_translation': [],
    'bis_original': [],
    'gnd_triffin': [],
    'gnd_triffin_born': [('1911', 'num'), ('-|10', 'num'), ('-|05', 'num')],
    'gnd_triffin_died': [('1993', 'num'), ('-|02', 'num'), ('-|23', 'num')],
    'gnd_rueff': [],
    'gnd_licence': [],
}
IMAGE_NOTE = "read on the page image"


def read(word: str, how: str) -> list[float]:
    if how == NUM:
        return [figure(word)]
    if how == EN:
        return [cardinal(word)]
    if how == WD:
        return [WORDS[word]]
    raise ValueError(how)


def read_rule(rid: str, text: str) -> list[float]:
    got, pos = [], 0
    for phrase, how in READINGS[rid]:
        context, _, word = phrase.rpartition("|")
        k = text.find(context + word, pos)
        assert k >= 0, f"{rid}: {phrase!r} not found (in order)"
        pos = k + len(context + word)
        got += read(word, how)
    return got


def read_row(rid: str, text: str) -> list[float]:
    """The numbers of a row's words, by READINGS or by its figures."""
    if rid in READINGS:
        return read_rule(rid, text)
    return [figure(x.rstrip(",")) for x in FIGURES.findall(text)]


# the misreadings of the text layers, each printed in the quotation and named in the snapshot's notes with its row
# (row, the misreading as printed in the quotation, the words of the notes that name it)
MISPRINTS = [("bo_twothirds", "World War 11", "'World War 11' for 'World War II'"),
             ("bo_kennedy", "F'resident", "'F'resident' for 'President'"),
             ("bo_tr_rest", "Tiiffin", "'Tiiffin' for 'Triffin'"),
             ("bo_preconv", "194658", "'194658' for '1946-58'"),
             ("bo_whywell", "wellwhether", "'wellwhether' for 'well-whether'"),
             ("bo_scarce", "scare currency", "prints 'scare' for 'scarce'"),
             ("ga_accelerate", "e ~ p a n s i o n", "'e ~ p a n s i o n' for 'expansion'"),
             ("b68_jan1968", "ist January", "reads 'ist' for '1st'"),
             ("b68_programme", "ist January", "reads 'ist' for '1st'"),
             ("b68_closed", "ist April", "reads 'ist' for '1st'"),
             ("b70_fr_measures", "io per cent", "'io' for '10'"),
             ("b61_cuts", "November i960", "'i960' for '1960'"),
             ("b70_may9", "anouncement", "prints 'anouncement'"),
             ("b68_mix", "- 36 -", "the page number '- 36 -'"),
             ("b59_conv", "c u r r e n t - a c c o u n t", "letter-spaces some words")]


def check_readings(df: pd.DataFrame) -> None:
    src = meta()["sources"]
    n = img = 0
    for r in df.itertuples():
        assert r.file in src, (r.id, r.file)
        vals = [float(x) for x in r.value.split(";")] if r.value else []
        if src[r.file]["format"] == "image":                 # read on a page image: no quotation
            assert not r.quote and IMAGE_NOTE in r.note, r.id
            img += 1
            text = transcription(r.id)
        else:
            assert r.quote and IMAGE_NOTE not in r.note, f"{r.id}: no quotation"
            text = " ".join(r.quote.split())
        got = read_row(r.id, text)
        assert [round(g, 6) for g in got] == [round(v, 6) for v in vals], f"{r.id}: read {got}, value column {vals}"
        n += bool(vals)
    quoted("rows with values, each read from its quotation or transcription", n, 196)
    quoted("rows read on a page image (no quotation)", img, 25)
    Q, notes = quotes(), meta()["notes"]
    for rid, word, named in MISPRINTS:
        assert word in Q[rid], (rid, word)                                      # printed in the quotation
        k = notes.find(named)
        m = re.match(r"[^(]{0,80}\(([^)]*)\)", notes[k + len(named):]) if k >= 0 else None
        assert m and rid in re.split(r",\s*|;\s*also\s*", m.group(1)), (rid, named)  # and named, with its row
    assert "i960" in Q["b61_1960"] and "also b61_1960" in notes
    assert "0 1993 by" in Q["nber_ocr"] and "reads '0' for '\u00a9', row nber_ocr" in meta()["license"]
    # the source keys the chapter cites for its sources
    assert set(src) == set(df["file"]), sorted(set(src) ^ set(df["file"]))


# ---------------------------------------------------------------------------------------------------
# Data of the figures (figsrc/fig_ch36.py imports them)
EDITIONS = {"census1964img": ("sa64_gold", "sa64_foreign", "sa64_official"),
            "census1968img": ("sa68_gold", "sa68_foreign", "sa68_official"),
            "census1972img": ("sa72_gold", "sa72_foreign", "sa72_official")}
# the year-end figures that a later edition revised: (series, year) -> (earlier edition's value, later value)
REVISED = {("foreign", 1967): (29250, 29232), ("official", 1967): (14069, 14027)}


def year_ends(rid: str) -> dict[int, float]:
    """A row of the Statistical Abstract as transcribed: 'Gold stock, U.S.: 1955 21,753; ...; 1967 March 13,184; 1967
    Dec. 12,065; 1968 March (prel.) 10,703' -> the year-end figures {1955: 21753, ..., 1967: 12065} (the March
    figures dropped; a footnote mark between the year and the figure, '1961 2 18,781', skipped)."""
    out = {}
    for seg in transcription(rid).split(": ", 1)[1].split("; "):
        m = re.fullmatch(r"(\d{4})( Dec\.| March(?: \(prel\.\))?)?(?: \d)? ([\d,]+)", seg)
        assert m, (rid, seg)
        if m[2] and "March" in m[2]:
            continue
        out[int(m[1])] = figure(m[3])
    return out


@lru_cache(maxsize=None)
def gold_series() -> pd.DataFrame:
    """The US gold stock, the short-term liabilities to foreigners and those to foreign official institutions, end of
    year, million dollars, from the 1964, 1968 and 1972 editions of the Statistical Abstract (Tables 1211, 1204 and
    1271); where two editions give a year, the later edition's figure (two revisions, REVISED)."""
    rows: dict[int, dict[str, float]] = {}
    revised = {}
    for key in sorted(EDITIONS, key=edition):                                   # the later edition last
        for name, rid in zip(("gold", "foreign", "official"), EDITIONS[key]):
            assert column("file")[rid] == key
            for y, v in year_ends(rid).items():
                old = rows.setdefault(y, {}).get(name)
                if old is not None and old != v:
                    revised[(name, y)] = (old, v)
                rows[y][name] = v
    assert revised == REVISED, revised
    df = pd.DataFrame(rows).T.sort_index()
    df = df.loc[df.index <= 1971]                                               # 1972: March, preliminary
    assert list(df.index) == [1955] + list(range(1959, 1972)) and not df.isna().any().any()
    return df


def crossing(S: pd.DataFrame, name: str) -> int:
    """The first year in which the liabilities `name` exceeded the gold stock."""
    return int(S.index[S[name] > S["gold"]][0])


def steps() -> dict[str, list[tuple[datetime.date, float]]]:
    """The dollar parities of Table 1.2, as (date of the change, units of the currency per dollar), from the first
    post-1949 parity to August 1971; the pound by its dollar price (2.80, 2.40) of Bordo's text and Hansard."""
    F = facts()
    uk, de, fr, jp = F["bt_uk"], F["bt_de"], F["bt_fr"], F["bt_jp"]
    out = {"英国": [(datetime.date(int(uk[2]), int(uk[3]), int(uk[4])), 1 / F["bo_cripps"][5]),
                    (datetime.date(int(uk[12]), int(uk[13]), int(uk[14])), 1 / F["bo_1967"][4])],
           "法国": [(datetime.date(int(fr[5]), int(fr[6]), int(fr[7])), fr[8]),
                    (datetime.date(int(fr[9]), int(fr[10]), int(fr[11])), fr[12]),
                    (datetime.date(int(fr[13]), int(fr[14]), int(fr[15])), fr[16]),
                    (datetime.date(int(fr[24]), int(fr[25]), int(fr[26])), fr[27] * fr[20])],     # new francs
           "西德": [(datetime.date(int(de[4]), int(de[5]), int(de[6])), de[7]),
                    (datetime.date(int(de[15]), int(de[16]), int(de[17])), de[18]),
                    (datetime.date(int(de[21]), int(de[22]), int(de[23])), de[24])],
           "日本": [(datetime.date(int(jp[2]), int(jp[3]), int(jp[4])), jp[5])]}
    has("bt_uk", "Devaluation to 0.357 £/$", "Devaluation to 0.417 £/$")
    assert round(1 / F["bo_cripps"][5], 3) == uk[5] and round(1 / F["bo_1967"][4], 3) == uk[15]
    has("bt_fr", "New Fr (= 100 old Fr)", "Devaluation to 5.55 Fr/$")
    return out


def floats() -> list[tuple[datetime.date, datetime.date | None]]:
    """The mark's floats: 29 September to 26 October 1969 (note c of Table 1.2) and from 9 May 1971."""
    F = facts()
    de, c = F["bt_de"], F["bt_de_c"]
    has("bt_de_c", "September", "October", "was floating")
    has("bt_de", "1971 5/9, Float")
    return [(datetime.date(int(de[21]), 9, int(c[0])), datetime.date(int(de[21]), 10, int(c[1]))),
            (datetime.date(int(de[25]), int(de[26]), int(de[27])), None)]


START, END = datetime.date(1949, 10, 1), datetime.date(1971, 8, 31)


def parities() -> dict[str, pd.Series]:
    """The dollar value of each currency, monthly (end of month), October 1949 to August 1971, with its parity of
    October 1949 = 100; NaN while the mark floated."""
    months = pd.date_range(START, END, freq="ME")
    fl = floats()
    out = {}
    for cur, st in steps().items():
        assert st[0][0] < START, cur                                            # each parity set by September 1949
        vals = []
        for m in months:
            d = m.date()
            p = [u for when, u in st if when <= d][-1]
            if any(a <= d and (b is None or d < b) for a, b in fl) and cur == "西德":
                vals.append(np.nan)
            else:
                vals.append(100 * st[0][1] / p)
        out[cur] = pd.Series(vals, index=months)
    return out


# ---------------------------------------------------------------------------------------------------
# The teaching models
TRIFFIN = {"R0": 40, "G0": 30, "D0": 10, "GUS": 20, "g": 0.05, "dG": 0.5, "dG2": 1.5, "g_sc": 0.04}   # the example
STERLING = {"X": 100, "M_usd": 280, "dx": 0.15, "dm": 0.10}                                       # ex:...-sterling


def triffin(R0: float, G0: float, GUS: float, g: float, dG: float, T: int) -> dict[str, np.ndarray]:
    """eq:brettonwoods-triffin: reserves R_t = R0 (1+g)^t, gold G_t = G0 + dG t, dollars D_t = R_t - G_t, and the
    cover c_t = GUS / D_t of the dollars by the US gold stock (held constant)."""
    t = np.arange(T + 1)
    R = R0 * (1 + g) ** t
    G = G0 + dG * t
    D = R - G
    return dict(t=t, R=R, G=G, D=D, c=GUS / D)


def first_below(m: dict[str, np.ndarray]) -> int:
    """The first year in which the dollars exceed the US gold (c < 1 with D > 0)."""
    return int(m["t"][(m["D"] > 0) & (m["c"] < 1)][0])


def sterling(rate0: float, rate1: float, X: float, M_usd: float, dx: float = 0.0, dm: float = 0.0) -> dict:
    """The sterling example: exports priced in pounds, imports in dollars; the balance in pounds after the
    devaluation from rate0 to rate1 dollars a pound, with the export volume up dx and the import volume down dm."""
    M0, M1 = M_usd / rate0, M_usd / rate1
    return dict(M0=M0, M1=M1, bal0=X - M0, bal1=X - M1, X2=X * (1 + dx), M2=M1 * (1 - dm),
                bal2=X * (1 + dx) - M1 * (1 - dm), usd_per_pound_drop=(rate0 - rate1) / rate0,
                pound_per_usd_rise=rate0 / rate1 - 1, exports_usd=X * rate1)


# ---------------------------------------------------------------------------------------------------
# 2. Every “…” of the text against the snapshot
# the chapter's Chinese renderings of the quotations: rendering -> row (or rows)
TRANSLATIONS = {
    # the opening
    "唯一无可置疑的、不带任何一国印记的货币基础": "fr36_gold",
    "崩溃": "fr36_treasury",
    "179 种商品指数": "b59_fr_index",
    "无力为世界贸易的巨大增长提供资金": "fr36_treasury",
    "随后是大量投机性的买金": "b66_speculation",
    # sec:brettonwoods-world
    "美国持续的顺差显然让世界其他地方处境难以为继": "b68_turn",
    "经济结构与金融结构都还没有充分平衡，不足以恢复经常交易的完全可兑换": "b48_structure",
    "战前从未见过的": "b48_dollarneeds",
    "虽然幅度不尽相同": "b50_devalued",
    "等于用间接的办法降低实际工资": "b50_wages",
    "比利时的大部分工人至少要失去一部分加薪的好处": "b50_wages",
    "只要生活费用不超过一定的限度，就接受工资率不变": "b50_unions",
    "一次暂时的挫折": "b50_setback",
    "美国行情的下跌，带动了世界市场的下行": "b50_slump",
    "回头看，1949 年外国货币的大批贬值，是美元的一个关键转折点": "b68_turn",
    # sec:brettonwoods-convertibility
    "双边主义的紧身衣": "b59_straitjacket",
    "一国赚到的另一国货币，一般只能在那个国家花": "b59_straitjacket",
    "每月完全结清的简单机制": "b59_epu",
    "世界主要外汇市场的统一": "b59_winding",
    "避免限制经常的对外支付，避免多重汇率与歧视性的货币做法": "b61_art8c",
    "全盛期": "ga_heyday",
    "洞太大了": "b61_holes",
    "实际上承认了": "b61_admission",
    "步子并不大": "b61_admission",
    "越来越难": "b61_inner",
    "毫不奇怪地反映了颇为不同的看法": "b61_onceforall",
    "从国外输入的通胀": "bo_de_resist",
    "没有告诉我们": "bo_whywell",
    # sec:brettonwoods-triffin
    "大体上被看作建设性的，确实大大帮助了欧洲在迅速重建的同时积累储备": "b68_constructive",
    "暴风雨前的一阵阳光": "b68_1957",
    "不能指望": "bo_triffin",
    "黄金存量上升是实力的标志，下降至少应该引起疑问": "b68_indicator",
    "与官方负债的上升合起来看，黄金的流失不是好兆头": "b68_distribution",
    "存在美国以外银行的美元储备必定大大增加了": "b70_outside",
    # sec:brettonwoods-defence
    "如果当选总统，我不会让美元从现在的汇率上贬值": "bo_kennedy",
    "可能威胁国际货币体系": "b62_threat",
    "能够轻易地控制市场": "b66_control",
    "去帮助本集团里货币受到短期资本外逃威胁的成员": "b62_gab",
    "临时搭起来的": "ga_gab",
    "一条危险的路，可能让世界离开过去十五年左右达到的自由的贸易与支付做法": "b68_dangerous",
    "和平回来以后，管制就能拆掉吗？": "b68_peace",
    "在当时的国际政治形势下被认为行不通": "b68_limits",
    "扭转操作": "b68_twist",
    "本可以更早取得明显的效果": "b68_1966",
    "我们从国外买的东西要多花钱，我们卖到国外的东西对外国人会便宜": "h67_prices",
    "白白浪费": "h67_claims",
    "保护社会上最脆弱的人群免受困苦": "h67_vulnerable",
    "很大的、不可接受的": "h67_consumption",
    "这是我们必须付出的代价": "h67_price",
    "不是给我们的贷款，不是让我们靠它过日子的": "h67_loan",
    "我们要的是出口带动的增长": "h67_exportled",
    "这个国家每一个工人阶级成员的工资水平与实际工资": "h67_july",
    "多花钱": "h67_prices",
    "今后只应用于货币当局之间的转移": "fr191_communique",
    "不再把黄金卖给货币当局，去补它们在私人市场上卖掉的黄金": "fr191_replace",
    "做一切必要的事": "fr191_ukall",
    "鼓励国内扩张、又与经济稳定相容的": "fr191_ukall",
    "由供求自由决定": "fr191_two",
    "过度特权": ("im_giscard", "le_tokyo"),
    "回旋镖货币": "im_rueff",
    # sec:brettonwoods-debate
    "最准确、最普遍地被预言的": "ga_predicted",
    "政治上的困难似乎是一个障碍": "b68_mix",
    "政治层面": "ga_identification",
    "外国的资产被便宜地买走了": "ga_cheap",
    "资产的重新包装，这是任何金融中介的生意": "ga_repackage",
    "因为它对信心的影响": "bo_confidence",
    "替代": "b61_substitute",
    # the 史料说明: the misreadings of the text layers, as printed
    "T h e": "b66_sold",
    "ist": "b68_jan1968",
    "io": "b70_fr_measures",
    "i960": "b61_cuts",
    "World War 11": "bo_twothirds",
    "F'resident": "bo_kennedy",
    "Tiiffin": "bo_tr_rest",
    "scare": "bo_scarce",
    # the ending
    "黑色星期五": "b70_blackfriday",
}
# a “…” of the 史料说明 that names a source not obtained (none in this chapter)
NOT_OBTAINED: dict[str, str] = {}
# the words of the source that each rendering translates
KEYWORDS = {
    "fr36_gold": ['"unquestionable monetary basis which did not bear the mark of any individual country,"'],
    "fr36_treasury": ['"collapsed"', '"incapable of financing the huge increase of world trade"'],
    "b66_speculation": ["heavy speculative gold-buying ensued"],
    "b59_fr_index": ['"index of 179 articles"'],
    "b68_turn": ["It was evident that persistent U S surpluses made an untenable situation for the rest of the world.",
                 "devaluation of foreign currencies in 1949 was, in retrospect, a crucial turning-point for the dollar"],
    "b48_structure": ["neither the economic nor the financial structure was sufficiently in equilibrium to permit a "
                      "return to full convertibility for current transactions"],
    "b48_dollarneeds": ["on a scale unknown in pre-war days"],
    "b50_devalued": ["although not always to the same degree"],
    "b50_wages": ["devaluation is equivalent to an indirect way of reducing real wages",
                  "the bulk of the Belgian workers would have been deprived of at least a part of the advantage of "
                  "higher wages"],
    "b50_unions": ["the acceptance of unchanged wage rates as long as the cost of living did not rise beyond a certain "
                   "point"],
    "b50_setback": ["a temporary setback"],
    "b50_slump": ["a decline in American quotations leading to a downward movement on the world markets"],
    "b59_straitjacket": ["the straitjacket of bilateralism",
                         "balances earned by one country in the currency of another could, as a rule, only be spent "
                         "in the country in whose currency they were expressed"],
    "b59_epu": ["a simple mechanism for the complete settlement every month"],
    "b59_winding": ["the unification of the world's principal foreign exchange markets"],
    "b61_art8c": ["to avoid restrictions on current external payments, multiple exchange rates and discriminatory "
                  "currency practices"],
    "ga_heyday": ["The heyday of Bretton Woods"],
    "b61_holes": ["the holes in the net were too large"],
    "b61_admission": ["an admission was in effect made", "was not a great step"],
    "b61_inner": ["was becoming more and more difficult"],
    "b61_onceforall": ["not surprisingly, reflected a rather different view of events"],
    "bo_de_resist": ["inflation imported from abroad"],
    "bo_whywell": ["they do not tell us why it did so well"],
    "b68_constructive": ["deficits on the whole were considered constructive and, indeed, they helped Europe "
                         "enormously to build up reserves while pursuing reconstruction rapidly"],
    "b68_1957": ["the burst of sunshine before the storm"],
    "bo_triffin": ["cannot be relied upon"],
    "b68_indicator": ["a rise in the gold stock is a sign of strength, while a fall should, at least, raise questions"],
    "b68_distribution": ["Taken in conjunction with the rise in official liabilities, however, the gold loss was not a "
                         "good sign."],
    "b70_outside": ["a marked increase in dollar reserves held with banks outside the United States"],
    "bo_kennedy": ["If elected F'resident, I shall not devalue the dollar from the present rate.", "F'resident"],
    "b62_threat": ["could threaten the international monetary system"],
    "b66_control": ["can readily keep control over the market"],
    "b62_gab": ["to aid a member of the group whose currency is threatened by a flight of short-term capital"],
    "ga_gab": ["jerry-built"],
    "b68_dangerous": ["a dangerous path, which could lead the world away from the liberal trade and payments practices "
                      "achieved over the past fifteen years or so"],
    "b68_peace": ["But would the return of peace allow the controls to be dismantled?"],
    "b68_limits": ["was considered impracticable in the prevailing international political situation"],
    "b68_twist": ['"operation twist"'],
    "b68_1966": ["a significant result could have been achieved earlier"],
    "h67_prices": ["the things we buy from abroad will cost us more and things we sell abroad will become cheaper for "
                   "people overseas to buy"],
    "h67_claims": ["frittered away"],
    "h67_vulnerable": ["to protect the most vulnerable sections of the community from hardship"],
    "h67_consumption": ["substantial-and unacceptable"],
    "h67_price": ["This is the price we shall have to pay."],
    "h67_loan": ["These facilities are not a loan to us. They are not intended for us to live on"],
    "h67_exportled": ["We are out for export-led growth."],
    "h67_july": ["the wage levels and the real wage standards of every member of the working class of this country"],
    "fr191_communique": ["henceforth officially held gold should be used only to effect transfers among monetary "
                         "authorities"],
    "fr191_replace": ["they will not sell gold to monetary authorities to replace gold sold in private markets"],
    "fr191_ukall": ['"to do all that is necessary"', "encourage domestic expansion consistent with economic stability"],
    "fr191_two": ["the price freely determined by supply and demand"],
    "im_giscard": ['"exorbitant privilege"'],
    "le_tokyo": ["« privilège exorbitant »"],
    "im_rueff": ['"boomerang currency"'],
    "ga_predicted": ["one of the most accurately and generally predicted of major economic events"],
    "b68_mix": ["political difficulties, it would seem, were an obstacle"],
    "ga_identification": ["political dimension"],
    "ga_cheap": ["foreign assets were being bought cheaply"],
    "ga_repackage": ["the repackaging of assets that is the business of any financial intermediary"],
    "bo_confidence": ["because of its effect on confidence"],
    "b61_substitute": ["a substitute for measures"],
    "b66_sold": ["T h e United States"],
    "b68_jan1968": ["ist January 1968"],
    "b70_fr_measures": ["io per cent"],
    "b61_cuts": ["November i960"],
    "bo_twothirds": ["World War 11"],
    "bo_tr_rest": ["Tiiffin dilemma"],
    "bo_scarce": ["a scare currency"],
    "b70_blackfriday": ['"black Friday"'],
}


def tex_text() -> str:
    return "\n".join(l for l in TEX.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("%"))


def text_quotations() -> list[str]:
    """The “…” of the text; the closing question is Chapter 37's and the chapter's own question is in the guide and at
    the end of the opening (both checked by guide() and ending())."""
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 37's question"
    t = t[:-len(NEXT)]
    assert t.count(GUIDE) == 2, "the question is not in the guide and at the end of the opening"
    return re.findall(r"“([^”]*)”", t.replace(GUIDE, ""))


def check_text(df: pd.DataFrame) -> None:
    ids = set(df["id"])
    used, n = set(), 0
    for q in text_quotations():
        n += 1
        used.add(q)
        if q in NOT_OBTAINED:
            continue
        assert q in TRANSLATIONS, f"not listed: “{q}”"
        t = TRANSLATIONS[q]
        for rid in (t,) if isinstance(t, str) else t:
            assert rid in ids, rid
            assert rid in KEYWORDS, f"{rid}: no KEYWORDS"
    stale = (set(TRANSLATIONS) | set(NOT_OBTAINED)) - used
    assert not stale, f"listed but not in the text: {sorted(stale)}"
    for rid, words in KEYWORDS.items():
        for w in words:
            assert w in words_of(rid), f"{rid}: {w!r} not in the quotation"
    assert set(KEYWORDS) == {r for t in TRANSLATIONS.values() for r in ((t,) if isinstance(t, str) else t)}
    # the misreadings quoted in the 史料说明 are those of MISPRINTS
    deeper = re.search(r"\\begin\{deeper\}\[史料说明\].*?\\end\{deeper\}", tex_text(), re.DOTALL).group(0)
    for q in ("T h e", "ist", "io", "i960", "World War 11", "F'resident", "Tiiffin", "scare"):
        assert f"“{q}”" in deeper, q
    print(f"ok {n} quotations of the text found in the snapshot ({len(set(used))} distinct)")


# ---------------------------------------------------------------------------------------------------
# 3. Numbers: said() and the parts of the text it does not read
UNITS = {"万亿": 10 ** 12, "亿": 10 ** 8, "万": 10 ** 4}
AMOUNT = re.compile(r"(\d[\d,]*(?:\.\d+)?)(?:\s*(万亿|亿|万))?")
# what is not a number of the story: labels, citations, cross-references, the key equation (models() reads it),
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


def ocr(rid: str, printed: str) -> float:
    """A number that a BIS text layer prints with letters for digits ('i960', 'io', 'ist'), asserted to be printed so in
    row rid, read with 'i' for 1 and 'o' for 0."""
    has(rid, printed)
    return float(re.match(r"\d+", printed.translate(str.maketrans("io", "10"))).group(0))


def i960(rid: str) -> int:
    """The year that a BIS text layer prints as 'i960'."""
    return int(ocr(rid, "i960"))


# ---------------------------------------------------------------------------------------------------
# 4. Numbers, section by section
def guide(F, Y, Q):
    t = TEX.read_text(encoding="utf-8")
    assert f"\\guidequestion{{{GUIDE}}}" in t and GUIDE == PREV
    assert chapter("ch35_reconstruction").rstrip().endswith(PREV)              # 第 35 章交来的问题
    for label in ("ch:warfinance", "ch:external"):                             # the prerequisites
        assert f"\\chref{{{label}}}\\enspace\\nameref{{{label}}}" in t, label
    said("解释 1958 年西欧恢复经常账户可兑换以后的变化", F["b59_conv"][0])
    said("推导特里芬难题（1960）", F["bo_ref_triffin"][0])
    has("bo_ref_triffin", "Gold and the Dollar Crisis")
    said("分析伦敦黄金总库与 1960 年代的美元危机", F["ga_identification"][0])
    has("ga_identification", "1960s")
    assert "\\chapterstub" not in t


def opening(F, Y, Q):
    d4, y65 = F["fr36_date"]
    feb = mon("fr36_date", "February")
    said("1965 年 2 月 4 日，法国总统戴高乐", y65, feb, d4)
    has("fr36_date", "press conference", "French President Charles de Gaulle")
    say("照美国国务院外交文件的概括")
    d4b, y31, _ = F["fr36_treasury"]
    has("fr36_treasury", "A February 4 Treasury Department statement")
    assert d4b == d4                                                            # 同一天
    said("那样的货币体系 1931 年已经“崩溃”", y31)
    y, sold, france = F["b66_table"][0], *F["b66_sold"]
    assert page("b66_table") == page("b66_sold") and F["b66_table"][1] == F["b66_decline"][0]
    said("1965 年，美国向西欧净售出近 13 亿美元的黄金，其中卖给法国 8.8 亿美元", y, sold * 1e6, france * 1e6)
    us, europe = F["b66_decline"]
    said("美国的黄金存量这一年减少了约 17 亿美元，西欧的黄金储备增加了约 19 亿美元", us * 1e6, europe * 1e6)
    has("b66_france", "early in the year that French external surpluses would henceforth be taken in gold")
    said("在平价上下 1\\% 以内干预汇率", F["bo_pegged"][0])
    said("1946 年起，金价是每盎司 35 美元", F["bt_us"][0], F["bt_us"][1])
    has("bt_us", "1946 $35/oz. gold")
    assert paragraph("法国能这样做").endswith(GUIDE)                             # the opening ends with the question


def world(F, Y, Q):
    y44 = int(re.search(r"说明 (\d{4}) 年体系的最终设计", chapter("ch34_warfinance")).group(1))
    said("1944 年议定的协定", y44)
    n12, n32, y46 = F["bo_parvalues"]
    said("1946 年 12 月，32 国宣布了官方平价", y46, mon("bo_parvalues", "December"), n32)
    chk("    two-thirds (三分之二)", F["bo_twothirds"][0], told("美国握有世界货币黄金的三分之二", "黄金的", ""))
    said("用了 12 年", n12)
    y46b, y47, bn = F["bo_oeec"]
    has("bo_oeec", "1946-47")
    assert y47 == y46b + 1
    said("因 1946—1947 年冬天的严寒而加重，1947 年高达 90 亿美元", y46b, y46b + 1, y47, bn * 1e9)
    said("美国借给英国 37.5 亿美元，加拿大另借 12.5 亿美元", F["bo_loan"][0] * 1e9, F["bo_loan"][1] * 1e9)
    has("bo_loan", "promised to restore current")
    chk("    within one year (一年以内)", F["bo_loan_year"][0], told("并答应在一年以内恢复经常账户的可兑换", "在", "年以内"))
    d15, y47b, d6, y45, d21 = F["b48_dates"]
    said("1945 年 12 月 6 日签订的美英贷款协定，1946 年 7 月 15 日获得批准", y45, mon("b48_dates", "December"), d6,
         F["bo_loan_ratified"][1], mon("bo_loan_ratified", "July"), F["bo_loan_ratified"][0])
    d15b, y47c, bn1, d20, _ = F["bo_1947"]
    said("1947 年 7 月 15 日，英镑按约定恢复了经常账户交易的可兑换", y47c, mon("bo_1947", "July"), d15b)
    assert (d15, y47b) == (d15b, y47c)                                          # the BIS: the same day
    # 按约定: one year after the loan was ratified on 15 July 1946
    assert (d15b, y47c) == (F["bo_loan_ratified"][0], F["bo_loan_ratified"][1] + F["bo_loan_year"][0])
    said("挤兑在一个月内耗掉英国 10 亿美元的储备，8 月 20 日可兑换就中止了", bn1 * 1e9, mon("bo_1947", "August"), d20)
    said("照国际清算银行 1948 年年报的解释，根本的原因在于", bis_year("bis1948"))
    has("b48_structure", "the fundamental reason was that")
    said("英国自己 1947 年的国际收支逆差还有近 7 亿英镑", F["b48_deficit"][1], F["b48_deficit"][0] * 1e6)
    say("英镑是英国的货币单位")
    say("成员国用本币向基金组织买外汇，叫提款")
    said("1952 年以前虽有少量提款", F["bo_drawings"][0])
    has("bt_fr_b", "Multiple exchange rates were in effect from January 1948")
    said("法国 1948 年起实行多重汇率，基本进口按每美元约 214 法郎的官价，旅游与金融交易用浮动汇率，硬通货的实际汇率约 260 法郎",
         F["bt_fr_b"][0], F["bo_france48"][0], F["bo_france48"][1])
    has("bo_censure", "Article IV, section 5", "broken cross rates between the dollar and the pound")
    say("在巴黎套算出来的美元与英镑的比价偏离了两者的平价")
    said("基金组织因此按协定第四条第 5 节谴责了法国，1952 年以前不许它动用基金的资源", F["bo_censure"][0], F["bo_denied"][0])
    # 1949
    r570, y49 = F["b50_reserves"]
    said("1949 年，危机又回到英镑", y49)
    has("b50_slump", "raw materials and foodstuffs then fell sharply")
    assert "In the spring of 1949" in column("note")["b50_slump"] and years()["b50_slump"] == y49   # 那年春天
    say("那年春天，一些原料与食品的价格大跌")
    said("从 4 月初到 9 月中减少了约 5.7 亿美元", mon("b50_reserves", "April"), mon("b50_reserves", "September"), r570 * 1e6)
    two, d18, y49b, h24, pct, usd, n23 = F["bo_cripps"]
    chk("    two weeks (两个星期)", two, told("贬值以前两个星期", "以前", "个星期"))
    said("9 月 18 日，英镑贬值 30.5\\%，降到 2.80 美元", mon("bo_cripps", "September"), d18, pct, usd)
    said("英国却只提前 24 小时通知了基金组织", h24)
    assert F["b50_devalued"] == [pct, d18] and y49b == y49
    old = 1 / F["bt_uk"][1]                                                     # £0.248 a dollar in 1946
    said("原来的平价约合 4.03 美元（本书据 Bordo 表 1.2 的换算）", old, float(table_no("bordo1993img")))
    chk("    2.80 / 4.03 - 1 (30.5%)", 100 * (1 - usd / old), pct, tol=0.1)
    said("随后降低平价的有 23 国", n23)
    h24b, sec5, ten, h72 = F["bo_notice"]
    assert h24b == h24 and sec5 == F["bo_censure"][0]                           # 24 hours; Article IV, section 5
    has("bo_notice", "the Fund staff had earlier advised the British to devalue", "larger than suggested",
        "Article IV, section 5")
    said("按协定第四条第 5 节，贬值超过 10\\% 要先与基金组织商量，给它 72 小时以上表示同意或反对", sec5, ten, h72)
    # who paid
    b123, y49c = F["b50_belgium"]
    said("比利时法郎 1949 年 9 月只贬了 12.3\\%", y49c, mon("b50_belgium", "September"), b123)
    said("国际清算银行 1950 年的年报说得直白", bis_year("bis1950"))
    butter, marg, bread, y50, kr, _ = F["b50_norway"]
    said("1950 年 4 月，挪威的黄油涨价 23\\%，人造黄油涨 125\\%，面包涨了 40\\% 以上", y50, mon("b50_norway", "April"),
         butter, marg, bread)
    has("b50_norway", "over 40 per cent, for bread", "N . Kr. 600 million", "before the devaluation in September 1949")
    said("把生活费用补贴的总额压在 6 亿克朗以内", kr * 1e6)
    say("克朗是挪威的货币单位")
    r560, y49d, y50b = F["b50_recovered"]
    said("英国的储备 1949 年 9 月底到 1950 年 3 月底增加了 5.6 亿美元", y49d, mon("b50_recovered", "September"), y50b,
         mon("b50_recovered", "March"), r560 * 1e6)
    said("在它看来，1949 年的危机虽然惊人，只是 1947 年以来靠马歇尔计划", *F["b50_setback"])
    # the turning point
    y49e, aid = F["b68_turn"]
    said("1949 年也是美元的转折点", y49e)
    said("国际清算银行 1968 年的年报写道，“回头看，1949 年外国货币的大批贬值", bis_year("bis1968"), y49e)
    said("平均每年有 55 亿美元", aid * 1e9)
    has("bo_oneway", "they lose only the interest")
    has("bo_delay", "delay adjustment until they were sure it was necessary", "speculators would also be sure")
    de, jp = F["bt_de"], F["bt_jp"]
    said("德国马克是西德 1948 年起的货币单位，1949 年 9 月 19 日贬到每美元 4.20 马克", de[0], de[4], de[5], de[6], de[7])
    said("日元是日本的货币单位，1949 年 4 月 25 日定为每美元 360 日元", jp[2], jp[3], jp[4], jp[5])
    assert de[8] == jp[6]
    said("两国的官方平价都到 1953 年才正式定下", de[8])
    has("bt_de", "1953 1/30, Official par value set at 4.20 DM/$")
    has("bt_jp", "1953 5/11, Official par value set at 360 ¥/$")
    # tab:brettonwoods-parities
    us, uk, fr = F["bt_us"], F["bt_uk"], F["bt_fr"]
    said("几种主要货币的平价与变动，1946—1971 年", us[0], us[8])
    said("1946 年起每盎司黄金 35 美元；1961 年 11 月成立伦敦黄金总库；1968 年 3 月 17 日起黄金分成两个市场；1971 年 8 月 15 日停止黄金兑换",
         us[0], us[1], us[2], mon("bt_us", "Nov."), us[3], us[6], us[7], us[8], us[9], us[10])
    has("bt_us", "3/17, two-tier gold market instituted", "8/15, Suspension of gold")
    said("1946 年每美元 0.248 英镑；1949 年 9 月 18 日贬到 0.357 英镑；1958 年 12 月 27 日事实上可兑换；1961 年 2 月 15 日按第八条可兑换；"
         "1967 年 11 月 18 日贬到 0.417 英镑", *uk)
    has("bt_uk", "Convertible de facto", "Convertible under Article VIII")
    said("1946 年每美元 119.1 法郎；1948 年 1 月 26 日起平价中止；1949 年 9 月 20 日 350 法郎；1957 年 8 月 11 日 420 法郎；"
         "1958 年 12 月 29 日 493.7 法郎；1960 年起新法郎 1 元合旧法郎 100 元；1969 年 8 月 10 日贬到 5.55 新法郎",
         *fr[:17], fr[19], 1, fr[20], *fr[24:28])
    has("bt_fr", "Par value (note b) suspended", "New Fr (= 100 old Fr)")
    said("1948 年 6 月 20 日发行德国马克，每美元 3.33 马克；1949 年 9 月 19 日贬到 4.20 马克；1961 年 3 月 6 日升到 4 马克；"
         "1969 年 10 月 26 日升到 3.66 马克；1971 年 5 月 9 日浮动", *de[:8], *de[15:19], *de[21:28])
    said("1949 年 4 月 25 日定为每美元 360 日元；1953 年 5 月 11 日定为官方平价；1964 年 4 月 1 日按第八条可兑换", *jp[2:9],
         *jp[10:13])
    has("bt_jp", "¥ becomes convertible under Article VIII")
    said("Bordo（1993）表 1.2，据页面图像读出", src_year("bordo1993"), float(table_no("bordo1993img")))
    has("bt_source", "Various IMF publications")


def convertibility(F, Y, Q):
    said("1947 年 11 月，几个欧洲国家签订了多边抵消的协定", F["b59_nov47"][0], mon("b59_nov47", "November"))
    y47, y50, half, third = F["b50_trade"]
    said("1947 年到 1950 年初，西欧各国之间的贸易量增加了近一半，西欧对世界其他地方的出口增加了约三分之一", y47, y50)
    chk("    nearly one-half (近一半)", half, told("贸易量增加了近一半", "近", ""))
    chk("    about one-third (约三分之一)", third, told("出口增加了约三分之一", "约", ""))
    said("从 1950 年 7 月起，欧洲支付同盟", F["b59_epu"][0], mon("b59_epu", "July"))
    has("bo_epu_month", "At the end of each month", "The unit of account for these clearings was the U.S. dollar")
    said("美国提供了 3.5 亿美元的初始周转资金", F["bo_epu350"][0] * 1e6)
    said("1958 年 12 月底，同盟的成员除希腊、冰岛与土耳其以外，连同芬兰", F["b59_conv"][0], mon("b59_conv", "December"))
    has("b59_conv", "except Greece, Iceland and Turkey and by Finland")
    said("同盟的协定在 12 月 27 日营业结束时终止", mon("b59_end", "December"), F["b59_end"][0])
    d15, y61, n10 = F["b61_art8"]
    names = "比利时、法国、西德、爱尔兰、意大利、卢森堡、荷兰、秘鲁、瑞典与英国"
    said(f"1961 年 2 月 15 日，{names} 10 国接受了协定第八条的义务", y61, mon("b61_art8", "February"), d15, n10)
    assert len(re.split("、|与", names)) == n10 == len(quotes()["b61_art8"].split(" - ")[1].split(", ")) + 1
    jp = F["bt_jp"]
    said("日本到 1964 年 4 月 1 日才接受", *jp[10:13])
    said("只有 1959—1968 年", *F["ga_heyday"])
    q50, y60, q25, y66 = F["bo_quotas"]
    said("1960 年各国的份额增加 50\\%，1966 年又增加 25\\%", y60, q50, y66, q25)
    said("国际清算银行 1961 年的年报记载", bis_year("bis1961"))
    m131, half = F["b61_drawings"]
    said("共 1.31 亿美元", m131 * 1e6)
    assert half == 0.5 and "nearly half" in quotes()["b61_drawings"]
    say("将近一半的新提款")
    said("受第八条约束的成员已有 21 个", F["b61_repaid"][0])
    said("西德 1959 年取消了资本管制，1960 年又重新限制资本流入", *F["bo_controls_de"])
    said("1960 年，西德在提高短期利率，美国却在降低", i960("b61_1960"))
    has("b61_rates", "Germany was raising short-term interest rates while the United States was doing the opposite")
    has("b61_shift", "to those in low interest rate centres abroad")
    has("b61_influx", "in search of high yields", "acceleration of export receipts and retardation of import payments")
    assert page("b61_shift") == page("b61_influx") == page("b61_holes")
    say("西德的企业转到利率低的外国去借钱，外国资本为了高收益流进来，出口的货款提前收，进口的货款推迟付")
    y61b = F["b61_cuts"][0]
    assert i960("b61_cuts") == y61b - 1
    said("1960 年 11 月与 1961 年 1 月", i960("b61_cuts"), mon("b61_cuts", "November"), y61b, mon("b61_cuts", "January"))
    chk("    three kinds (三类办法)", F["b61_three"][0], told("国际清算银行列出了西德当局可以采取的三类办法", "采取的", "类"))
    pct, d6, d7, y61c = F["b61_reval"]
    said("1961 年 3 月 6 日与 7 日，马克与荷兰盾先后升值 5\\%，马克升到每美元 4 马克", y61c, mon("b61_reval", "March"), d6, d7,
         pct, F["b61_dm4"][1])
    chk("    4.20 / 4.00 - 1 (5%)", 100 * (F["bt_de"][7] / F["bt_de"][18] - 1), pct, tol=1e-9)
    say("荷兰盾是荷兰的货币单位")
    chk("    four months (此前四个月)", F["b61_onceforall"][0], told("此前四个月", "此前", "个月"))
    de2, ch25 = F["b61_inflows"]
    said("3 月的第二周，西德的货币储备又增加了 2 亿多美元，瑞士增加了近 2.5 亿美元", mon("b61_inflows", "March"), de2 * 1e6,
         ch25 * 1e6)
    has("b61_inflows", "In the second week of March", "by over $200 million", "by almost $250 million")
    has("bo_preconv", "194658")
    said("1946—1958 年可兑换以前的时期", int("194658"[:4]), 1900 + int("194658"[4:]))


def triffin_section(F, Y, Q):
    y50, avg = F["b68_5056"]
    has("b68_5056", "1950-56")
    said("1950 年代的美国逆差", y50)
    said("国际清算银行 1968 年回顾说", bis_year("bis1968"))
    said("1950—1956 年，按官方储备交易计算，美国的逆差平均每年约 12 亿美元", y50, 1956, avg * 1e9)
    a49, y49, a56, y56 = F["b68_aid"]
    said("对外援助从 1949 年的 56 亿美元减到 1956 年的 24 亿美元", y49, a49 * 1e9, y56, a56 * 1e9)
    said("1957 年中东打仗", F["b68_1957y"][0])
    tr, y49b, bp, y58, d58 = F["b68_1957"]
    said("美国这一年的贸易顺差有 60 亿美元，国际收支顺差 11 亿美元", tr * 1e9, bp * 1e9)
    said("1958 年，美国的国际收支转为 29 亿美元的逆差", y58, d58 * 1e9)
    said("1960 年，特里芬", F["bo_ref_triffin"][0])
    say("出版了《黄金与美元危机》")
    has("bo_triffin", "(Triffin 1960, 63)")
    # the explanation of eq:brettonwoods-triffin and ex:brettonwoods-triffin
    said("$c$大于 1，所有的美元都换得到黄金；$c$小于 1", 1, 1)
    said("$c$跌破 1 就越早", 1)
    P = TRIFFIN
    said("设第 0 年各国的储备$R_0=40$，其中黄金$G_0=30$，美元$D_0=10$；美国的黄金$G^{\\mathrm{US}}=20$不变", 0, P["R0"],
         P["G0"], P["D0"], P["GUS"])
    assert P["R0"] == P["G0"] + P["D0"]
    said("储备的需要每年增长 5\\%，黄金每年只增加 0.5", 100 * P["g"], P["dG"])
    said("（1）第 1 年美元要增加多少？", 1)
    said("（4）若黄金每年增加 1.5 呢？", P["dG2"])
    said("哪一年$c$跌破 1？", 1)                                                  # the example and the self-check
    a = triffin(P["R0"], P["G0"], P["GUS"], P["g"], P["dG"], 12)
    b = triffin(P["R0"], P["G0"], P["GUS"], P["g"], P["dG2"], 12)
    dD1 = P["g"] * P["R0"] - P["dG"]
    said("（1）$R_1=40\\times1.05=42$，$\\Delta D_1=0.05\\times40-0.5=1.5$，$D_1=11.5$，$c_1=20/11.5\\approx1.74$",
         P["R0"], 1 + P["g"], a["R"][1], P["g"], P["R0"], P["dG"], dD1, a["D"][1], P["GUS"], a["D"][1], a["c"][1])
    assert abs(a["D"][1] - (P["D0"] + dD1)) < 1e-12
    said("（2）$R_t=40\\times1.05^t$，$G_t=30+0.5t$，所以$D_t=40\\times1.05^t-30-0.5t$", P["R0"], 1 + P["g"], P["G0"],
         P["dG"], P["R0"], 1 + P["g"], P["G0"], P["dG"])
    ta = first_below(a)
    said("（3）第 5 年$D_5\\approx51.05-32.5=18.55$，$c_5\\approx1.08$；第 6 年$D_6\\approx53.60-33=20.60$，$c_6\\approx0.97$，"
         "第 6 年跌破 1", ta - 1, a["R"][5], a["G"][5], a["D"][5], a["c"][5], ta, a["R"][6], a["G"][6], a["D"][6], a["c"][6],
         ta, 1)
    tb = first_below(b)
    said("（4）$G_t=30+1.5t$。第 9 年$D_9\\approx62.05-43.5=18.55$，$c_9\\approx1.08$；第 10 年$D_{10}\\approx65.16-45=20.16$，"
         "$c_{10}\\approx0.99$，推迟到第 10 年", P["G0"], P["dG2"], tb - 1, b["R"][9], b["G"][9], b["D"][9], b["c"][9], tb,
         b["R"][10], b["G"][10], b["D"][10], b["c"][10], tb)
    assert ta == 6 and tb == 10
    said("$c$大于 1 时，兑换反而让覆盖率上升；$c$小于 1 时，兑换让它跌得更快", 1, 1)       # models() checks the sign
    # the numbers of the 1950s
    dec, new = F["b68_newgold"]
    has("b68_newgold", "During the same period")
    assert page("b68_newgold") == page("b68_5056")
    said("1950—1956 年，美国的黄金平均每年减少约 4 亿美元", y50, 1956, dec * 1e6)
    said("新增的货币黄金平均每年 4.4 亿美元", new * 1e6)
    has("b68_newgold", "little more than half of the net demand", "This was not because of doubts")
    y65, supply = F["b66_record"]
    priv, off = F["b66_private"]
    said("到 1965 年，新黄金的供应创下近 20 亿美元的纪录，私人买走了约 16 亿美元，留给官方的只有 4 亿美元", y65, supply * 1e6,
         priv * 1e6, off * 1e6)
    assert supply - priv == off
    # ex:brettonwoods-us, from the Statistical Abstract
    S = gold_series()
    hundred = lambda v: v / 100                                                  # million dollars -> 亿美元
    said("1955 年 217.53、117.20、69.53；1960 年 178.04、172.60、102.12；1967 年 120.65、292.32、140.27",
         *[x for y in (1955, 1960, 1967) for x in (y, *(hundred(S.loc[y, k]) for k in ("gold", "foreign", "official")))])
    say("数据来自联邦储备委员会与《联邦储备公报》")
    has("sa68_source", "Board of Governors of the Federal Reserve System; Federal Reserve Bulletin")
    said("（3）1955—1967 年，黄金减少了多少", 1955, 1967)
    r = {y: (S.loc[y, "gold"] / S.loc[y, "foreign"], S.loc[y, "gold"] / S.loc[y, "official"]) for y in S.index}
    g = {y: hundred(S.loc[y, "gold"]) for y in S.index}
    fo = {y: hundred(S.loc[y, "foreign"]) for y in S.index}
    of = {y: hundred(S.loc[y, "official"]) for y in S.index}
    said("（1）1955 年$217.53/117.20\\approx1.86$，$217.53/69.53\\approx3.13$；1960 年$178.04/172.60\\approx1.03$，"
         "$178.04/102.12\\approx1.74$；1967 年$120.65/292.32\\approx0.41$，$120.65/140.27\\approx0.86$",
         *[x for y in (1955, 1960, 1967) for x in (y, g[y], fo[y], r[y][0], g[y], of[y], r[y][1])])
    cf, co = crossing(S, "foreign"), crossing(S, "official")
    said("1961 年底对外国的负债是 187.81 亿美元，黄金 169.47 亿美元，覆盖率约 0.90，第一次低于 1", cf, S.loc[cf, "foreign"] * 1e6,
         S.loc[cf, "gold"] * 1e6, r[cf][0], 1)
    said("1966 年底对官方的负债是 125.39 亿美元，黄金 132.35 亿美元，覆盖率约 1.06，1967 年降到约 0.86", co - 1,
         S.loc[co - 1, "official"] * 1e6, S.loc[co - 1, "gold"] * 1e6, r[co - 1][1], co, r[co][1])
    dg, dfo = S.loc[1955, "gold"] - S.loc[1967, "gold"], S.loc[1967, "foreign"] - S.loc[1955, "foreign"]
    said("（3）黄金减少了约 96.9 亿美元，对外国的负债增加了约 175.1 亿美元", dg * 1e6, dfo * 1e6)
    assert 1.7 < dfo / dg < 2.1                                                  # 差不多是两倍
    say("美元增加的差不多是黄金减少的两倍")
    # the crossings
    said("到 1959 年，美国的货币黄金已与对外美元负债的总额相等", F["bo_1959"][0])
    y55, t55, y59, t59, y60, t60 = F["sa64_total"]
    said("按《统计摘要》1964 年版，1959 年底包括国际组织在内的对外短期负债约 194 亿美元，黄金约 195 亿美元",
         edition("census1964img"), y59, t59 * 1e6, S.loc[1959, "gold"] * 1e6)
    assert abs(t59 / S.loc[1959, "gold"] - 1) < 0.01                             # 两者确实差不多
    assert "international organizations" in column("note")["sa64_total"]
    said("照 Bordo 的说法是 1964 年，照 Garber 的说法是 1960 年代后半期，《统计摘要》的数字是 1967 年底", F["bo_1964"][0],
         F["ga_wrong"][0], co)
    has("ga_wrong", "in the latter half of the 1960s")
    y50g, y68g, g246, g107, imf, o4, o15 = F["b68_gold"]
    has("b68_gold", "From the beginning of 1950 to the end of April 1968", "owed to the I M F", "somewhat under $4",
        "to over $15 milliard")
    said("国际清算银行 1968 年的年报算过整段时期的账", bis_year("bis1968"))
    said("从 1950 年初到 1968 年 4 月底，美国的黄金储备从 246 亿美元降到 107 亿美元，后者还包括欠基金组织的 10 亿美元",
         y50g, y68g, mon("b68_gold", "April"), g246 * 1e9, g107 * 1e9, imf * 1e9)
    said("同一时期，对外国官方机构的负债从不到 40 亿美元增加到 150 亿美元以上", o4 * 1e9, o15 * 1e9)
    assert abs(S.loc[1968, "gold"] / 1e3 - g107) < 0.5                            # end-1968: 108.92 亿美元
    has("sa64_fn4", "foreign central banks, foreign central governments and their agencies, Bank for International "
                    "Settlements, and European Fund")
    has("ga_citizens", "gold ownership by U.S. citizens was illegal",
        "such claims could have been shifted abroad and quickly used to run the system",
        "These claims were ignored in the discussions at the time")
    said("国际清算银行 1970 年指出", bis_year("bis1970"))
    has("b70_eurodollar", "held with banks in the United States")
    said("1969 年“存在美国以外银行的美元储备必定大大增加了”", F["b70_outside"][0])
    assert S.loc[1969, "official"] < S.loc[1968, "official"]                     # 图上那一年的官方负债减少了
    # fig:brettonwoods_gold
    said("美国的黄金与对外国的美元负债，1955—1971 年（年底，亿美元）", S.index[0], S.index[-1])
    said("画出了 1955—1971 年的数字", S.index[0], S.index[-1])
    said("(b) 黄金对两种负债的覆盖率，虚线是 1。1956—1958 年缺数", 1, 1956, 1958)
    assert set(range(1956, 1959)).isdisjoint(S.index)
    said("对外国的负债 1961 年、对官方的负债 1967 年超过了黄金；1969 年对官方的负债减少", cf, co, 1969)
    keys = sorted(EDITIONS, key=edition)
    said("数据：美国《统计摘要》1964、1968、1972 年版，表 1211、1204、1271", *[edition(k) for k in keys],
         *[float(table_no(k)) for k in keys])
    said("国际清算银行 1970 年年报", bis_year("bis1970"))
    # the compare box and the pitfall
    said("只有美元，每盎司 35 美元，只对外国的货币当局", F["bt_us"][1])
    y25 = int(re.search(r"英国 (\d{4}) 年按战前平价回到黄金", chapter("ch27_interwar")).group(1))
    said("英国 1925 年按战前的平价恢复", y25)
    said("能按 35 美元换黄金的", F["bt_us"][1])
    y60b = F["bo_oct60b"][0]
    said("1960 年秋天金价上涨以后", y60b)
    has("b62_measures", "the United States made it illegal for its citizens to buy or hold gold abroad")
    said("那里的价格可以离开 35 美元，1960 年 10 月就涨到过 40 美元", F["bt_us"][1], y60b, mon("bo_oct60b", "October"),
         F["bo_oct60"][1])
    said("黄金总库卖出黄金，就是为了把这个市场的价格钉在 35 美元", F["bo_pool_nov"][2])
    said("1968 年 3 月以后，官方持有的黄金只在货币当局之间转移", F["bo_disbanded"][1], mon("fr191_meeting", "March"))


def defence(F, Y, Q):
    y60 = F["bo_oct60b"][0]
    p35, p40 = F["bo_oct60"]
    said("1960 年秋天，伦敦的金价离开了美国的官价", y60)
    said("美国财政部卖出黄金的价格约为每盎司 35.09 美元", F["b61_selling"][0])
    has("b61_selling", "U.S. selling price of $35.0875")
    d13, top, cents, y59p, lo, hi = F["b61_london"]
    has("b61_london", "13th September", "mid-October", "ship it to London and resell it there")
    said("9 月中到 10 月中，伦敦的报价却在 35.20 到 35.25 美元之间", mon("b61_london", "September"),
         mon("b61_london", "October"), lo, hi)
    say("比从纽约买进黄金、运到伦敦转卖的保本价还高几美分")
    said("10 月，伦敦的自由价格涨到了 40 美元", mon("bo_oct60b", "October"), p40)
    has("bo_oct60", "the U.S. Treasury's buying price")                          # Bordo's reading of $35.20 (史料说明)
    assert p35 == lo
    fn, d31, y60k = F["bo_kennedy"]
    assert y60k == y60
    said("10 月 31 日，总统候选人肯尼迪", mon("bo_kennedy", "October"), d31)
    said("国际清算银行 1962 年说", bis_year("bis1962"))
    has("b62_monthly", "the central banks which meet monthly at the B.I.S.")
    has("b62_measures", "the group of central banks agreed informally not to purchase on the market when the latter was "
                        "under pressure")
    say("每月在国际清算银行开会的各国中央银行也非正式地约定，市场有压力时不去买黄金")
    assert F["bo_g10_3520"] == [10, p35]                                         # G10, $35.20
    y61, n7, p = F["bo_pool_nov"]
    said("伦敦黄金总库 1961 年 11 月正式成立。美国与另外 7 家中央银行约定买卖黄金，把价格钉在每盎司 35 美元", y61,
         mon("bo_pool_nov", "November"), n7, p)
    said("按约定，美国提供 50\\% 的黄金", F["ga_pool50"][0])
    has("ga_pool50", "The United States was to provide 50 percent of the gold")
    said("按 Bordo 引的数字，实际卖出的黄金有 60\\% 来自美国", F["bo_pool60"][1])
    has("bo_pool60", "(Schwartz 1989, 342)", "with the United States supplying 60% of the gold sold")
    said("另外 7 家虽然提供了稳定金价所需黄金的 40\\%", *F["bo_pool40"])
    assert F["bo_pool40"][1] == 100 - F["bo_pool60"][1]                          # 40% = 100% - 60%
    y61b, _ = F["b68_1961_65"]
    has("b68_1961_65", "1961-65")
    said("1961—1965 年美国黄金减少得较少", y61b, 1965)
    has("b68_reluctant", "reluctant to convert dollar reserves into gold")
    assert page("b66_pool") == page("b66_record") and "in 1965" in quotes()["b66_record"]
    said("1965 年私人买金最多的时候，总库暂时投入市场的黄金约 2.5 亿美元", F["b66_record"][0], F["b66_pool"][0] * 1e9)
    said("1961 年起，美国与其他中央银行签订互换协定", F["bo_swaps"][0])
    y63, y65 = F["b68_iet"]
    has("b68_iet", "effective from mid-1963", "voluntary programmes")
    said("1963 年年中起，美国对本国居民购买外国证券征收利息平衡税。1965 年又推出自愿计划", y63, y65)
    d2, y64, *_, d31a, y67, d31b, y69 = F["fr135_first"]
    said("利息平衡税 1964 年 9 月 2 日才正式立法，1967 年 7 月 31 日又延长到 1969 年 7 月 31 日", y64,
         mon("fr135_first", "September"), d2, y67, mon("fr135_first", "July"), d31a, y69, 7, d31b)
    assert F["fr135_iet"][:2] == [d31a, y67]                                     # signed on 31 July 1967
    t91 = transcription("ga_t91")
    y62 = F["ga_t91"][2]
    assert t91.index(f"{y62:.0f} Jan.") < t91.index("Oct. Beginning of the GAB") < t91.index("1965 Feb.")
    y61g, ten, bn6 = F["b62_gab"]
    said("1961 年 12 月，十个工业国议定，基金组织可以向它们借入 60 亿美元", y61g, mon("b62_gab", "December"), bn6 * 1e9)
    chk("    ten industrial countries (十个工业国)", ten, told("十个工业国议定", "", "个工业国"))
    has("b62_gab", "to borrow supplementary resources under Article VII")
    assert "the General Arrangements to Borrow" in column("note")["b62_gab"]
    say("这十国就是后来的十国集团")
    said("安排 1962 年 10 月开始运作", y62, mon("ga_t91", "Oct."))
    assert y62 == y61g + 1
    y68 = F["b68_jan1968"][0]
    has("b68_jan1968", "ist January 1968")
    said("1968 年 1 月 1 日美国又宣布了更广、更严的管制", y68, mon("b68_jan1968", "January"), 1)
    has("b68_programme", "Mandatory controls were imposed on direct investment outflows")
    chk("    fifteen years (十五年)", F["b68_dangerous"][0], told("可能让世界离开过去十五年左右", "过去", "年"))
    said("照国际清算银行 1968 年的概括", bis_year("bis1968"))
    said("年报指出，1966 年为抑制国内通胀实行紧的货币政策", F["b68_1966"][0])
    said("1965 年起，美国的货币增长加快", F["bo_vietnam"][0])
    # sterling
    said("1957 年就有过一次大的危机与基金组织的救援", F["bo_uk_problem"][4])
    d16, y64b, d26 = F["bo_uk1964"]
    said("1964 年 10 月 16 日工党当选时", y64b, mon("bo_uk1964", "October"), d16)
    said("10 月 26 日宣布对进口加征附加税", mon("bo_uk1964", "October"), d26)
    d25, bn4, _ = F["bo_rescue64"]
    said("11 月 25 日，十国集团与基金组织为英镑安排了 40 亿美元的救援", mon("bo_rescue64", "November"), d25, bn4 * 1e9)
    d20, y67b = F["bo_uk1966"]
    said("1966 年 7 月 20 日，英国实行大规模的紧缩，1967 年初产出下降", F["bo_1966"][0], mon("bo_uk1966", "July"), d20, y67b)
    has("bo_uk1966", "in early 1967")
    said("10 月又有码头罢工，11 月英镑遭到投机冲击", mon("bo_shocks", "October"), mon("bo_shocks", "November"))
    bn3, d18, y67c, pct, usd = F["bo_1967"]
    said("30 亿美元的救援没能挡住潮流，11 月 18 日英镑贬值 14.3\\%，降到 2.40 美元", bn3 * 1e9,
         mon("bo_1967", "November"), d18, pct, usd)
    chk("    2.40 / 2.80 - 1 (14.3%)", 100 * (1 - usd / F["bo_cripps"][5]), pct, tol=0.05)
    hy, hm, hd = url_date("hansard1967")
    assert hy == y67c and hm == 11
    said("11 月 20 日，财政大臣卡拉汉", hm, hd)
    has("h67_speaker", "Mr. James Callaghan")
    has("h67_cabinet", "I recommended the Cabinet to devalue. It accepted my advice.")
    say("贬值是他向内阁提议、内阁接受的")
    said("银行利率提高到 8\\%", F["h67_measures"][0])
    said("让国际收支得到持久而可观的改善，每年至少 5 亿英镑", F["h67_500"][0] * 1e6)
    has("h67_500", "lasting and substantial improvement in its balance of payments")
    said("不贬值的话，1968 年的个人消费会增加 3\\%", F["h67_1968"][0], F["h67_consumption"][0])
    said("公共支出的预期增长削减 4 亿英镑，明年预算里的防务削减 1 亿英镑", F["h67_cuts"][0] * 1e6, F["h67_defence"][0] * 1e6)
    has("h67_defence", "in the Budget planned for next year")
    d24, y67d, _, _ = F["h67_july"]
    assert int(y67d) == hy and column("juan")["h67_meant"] == column("juan")["h67_july"]   # July 1967, read again
    has("h67_meant", "This is what I meant in July when I said", "I will read again what I said")
    said("他说这正是他 7 月的意思，并把当时在下院的话重念了一遍", mon("h67_meant", "July"))
    assert mon("h67_july", "July") == mon("h67_meant", "July")
    y68b, y69 = F["b70_uk_tight"]
    said("1968 年 11 月与 1969 年 4 月，紧缩又两次收紧", y68b, mon("b70_uk_tight", "November"), y69,
         mon("b70_uk_tight", "April"))
    y68c, p10 = F["bo_basle68"]
    said("1968 年在巴塞尔达成协议", y68c)
    said("超过总储备 10\\% 的英镑的美元担保", p10)
    # ex:brettonwoods-sterling
    r0, r1 = F["h67_rate"]
    St = STERLING
    said("1967 年 11 月，英镑从 2.80 美元降到 2.40 美元", hy, hm, r0, r1)
    assert (r0, r1) == (F["bo_cripps"][5], F["bo_1967"][4])
    e = sterling(r0, r1, St["X"], St["M_usd"], St["dx"], St["dm"])
    said("设英国一年出口按英镑计价 100 英镑，进口按美元计价 280 美元，贬值以前也合 100 英镑", St["X"], St["M_usd"], e["M0"])
    said("（3）若出口的数量增加 15\\%，进口的数量减少 10\\%", 100 * St["dx"], 100 * St["dm"])
    said("（1）一美元从$1/2.80\\approx0.357$英镑变成$1/2.40\\approx0.417$英镑，贵了约 16.7\\%；"
         "英镑的美元价值降了$(2.80-2.40)/2.80\\approx14.3\\%$", 1, r0, 1 / r0, 1, r1, 1 / r1, 100 * e["pound_per_usd_rise"],
         r0, r1, r0, 100 * e["usd_per_pound_drop"])
    assert round(1 / r0, 3) == F["bt_uk"][5] and round(1 / r1, 3) == F["bt_uk"][15]
    said("（2）出口仍收 100 英镑，在外国只卖$100\\times2.40=240$美元；进口要付$280/2.40\\approx116.7$英镑，差额从 0 变成约$-16.7$英镑",
         St["X"], St["X"], r1, e["exports_usd"], St["M_usd"], r1, e["M1"], e["bal0"], -e["bal1"])
    has("b70_uk", "the volume of imports had risen sharply", "despite a substantial increase in exports")
    said("国际清算银行看到的却是，1967 年 11 月贬值以后进口的数量急剧上升", F["b70_uk"][0], mon("b70_uk", "November"))
    said("（3）出口$100\\times1.15=115$英镑，进口$116.7\\times0.9\\approx105$英镑，顺差约 10 英镑", St["X"], 1 + St["dx"],
         e["X2"], e["M1"], 1 - St["dm"], e["M2"], e["bal2"])
    # the gold rush
    said("英国若在 1964 年而不是 1967 年贬值，1968 年对黄金与美元的投机冲击", *F["bo_fn52"])
    has("bo_fn52", "According to Johnson (1968)")
    said("照 Bordo 引的 Johnson（1968）的看法", int(re.search(r"Johnson \((\d{4})\)", Q["bo_fn52"]).group(1)))
    has("b68_tons", "three or four tons a day", "twice that size")
    has("b68_france_pool", "France had since June ceased to participate")
    said("人们这时才知道，法国从 6 月起已不再参加总库", mon("b68_france_pool", "June"))
    d26, y67e = F["b68_frankfurt"]
    said("11 月 26 日，总库的活跃成员在法兰克福开会", mon("b68_frankfurt", "November"), d26)
    said("这一年第四季度，西方的货币黄金减少了 14 亿美元", F["b68_q4"][0] * 1e9)
    assert F["b68_q4"][1] == y67e
    y67f, y68d, bn3b, us22, *_ = F["bo_pool_lost"]
    said("1967 年 12 月到 1968 年 3 月，总库卖掉了 30 亿美元的黄金，其中美国 22 亿美元", y67f, mon("bo_pool_lost", "December"),
         y68d, mon("bo_pool_lost", "March"), bn3b * 1e9, us22 * 1e9)
    said("约占 73\\%（本书的计算）", 100 * us22 / bn3b)
    g3, m400, d14, g22 = F["ga_march"]
    assert (g3, g22) == (bn3b, us22)
    said("3 月 14 日一天就卖出 4 亿美元", mon("ga_march", "March"), d14, m400 * 1e6)
    d15, p44 = F["b68_paris"]
    said("3 月 15 日星期五，伦敦的黄金市场关闭，巴黎市场的金价超过了 44 美元", mon("b68_paris", "March"), d15, p44)
    assert datetime.date(int(y68d), 3, int(d15)).weekday() == 4 and "Friday" in quotes()["b68_paris"]
    d16, d17, n7b = F["fr191_meeting"]
    said("3 月 16 日与 17 日，总库 7 国的中央银行行长在华盛顿开会", mon("fr191_meeting", "March"), d16, d17, n7b)
    assert n7b == n7 and F["bo_disbanded"][0] == d17 == F["bt_us"][7]
    has("fr191_buy", "Special Drawing Rights", "they no longer feel it necessary to buy gold from the market")
    say("既然特别提款权就要设立，他们认为现有的货币黄金已经够用，也不再从市场买黄金")
    said("增加到 40 亿美元", F["fr191_uk"][0] * 1e9)
    said("官方交易的价格固定在每盎司 35 美元", F["fr191_two"][1])
    two, p38 = F["b68_closed"]
    chk("    two weeks (关闭了两周)", two, told("伦敦市场关闭了两周", "关闭了", "周"))
    has("b68_closed", "ist April")
    said("4 月 1 日重开时金价是 38 美元，5 月下半月超过了 42 美元", mon("b68_closed", "April"), 1, p38,
         mon("b68_42", "May"), F["b68_42"][0])
    y68n, y69m, p39, p44b = F["b70_gold39"]
    said("1968 年 11 月到 1969 年 3 月，金价又从约 39 美元涨到将近 44 美元", y68n, mon("b70_gold39", "November"), y69m,
         mon("b70_gold39", "March"), p39, p44b)
    p42, p35b, y69n = F["ga_42"]
    has("ga_42", "gold sales by South Africa", "by the end of 1969")
    said("南非卖出黄金以后，到 1969 年底，私人市场的金价才回到 35 美元左右", y69n, p35b)
    assert p42 == F["b68_42"][0] and y69n == y69m
    # the SDR
    d29, y67g = F["fr193_rio"]
    said("1967 年 9 月 29 日，基金组织在里约热内卢的年会批准了特别提款权方案的纲要", y67g, mon("fr193_rio", "September"), d29)
    assert F["bo_sdr_rio"][0] == y67g and "September 1967" in quotes()["bo_sdr_rio"]
    d29b, d30, y68e = F["fr193_date"]
    said("1968 年 3 月 29 日与 30 日，十国集团在斯德哥尔摩开会", y68e, mon("fr193_date", "March"), d29b, d30)
    assert F["bo_sdr_def"] == [1, 1]
    say("一个特别提款权定义为等于一个黄金美元")
    has("bo_sdr_quota", "in proportion to their quotas", "it was not backed by gold")
    say("特别提款权由基金组织按份额记给各成员，没有黄金作后盾")
    said("按每盎司 35 美元的金价，就是三十五分之一盎司黄金（本书的换算）", F["bt_us"][1])
    chk("    one thirty-fifth of an ounce (三十五分之一)", 1 / F["bt_us"][1], told("就是三十五分之一盎司黄金", "就是", "盎司"))
    has("fr193_debre", "more of a reserve account than a supplementary credit")
    y69b = F["ga_t91"][8]
    assert "1969 July SDR amendments are in force" in t91
    said("修正案 1969 年 7 月生效", y69b, mon("ga_t91", "July"))
    d1, y70, y68f, y69c = F["bo_sdr_1970"]
    bn95, three = F["bo_sdr_95"]
    said("美国 1968 年与 1969 年都是国际收支顺差，方案在 1970 年 1 月 1 日启动，三年分配 95 亿美元", y68f, y69c, y70,
         mon("bo_sdr_1970", "January"), d1, bn95 * 1e9)
    chk("    three years (三年)", three, told("三年分配 95 亿美元", "", "年"))
    # the French case
    said("法国 · 1958—1968 · 把美元换成黄金", F["b59_fr_end58"][0], F["bo_disbanded"][1])
    d21, y58, y57, p20 = F["b59_fr57"]
    said("1957 年 8 月，它对原来的汇率加上 20\\% 的溢价或附加费，事实上贬了值，1958 年 6 月 21 日正式化", y57,
         mon("b59_fr57", "August"), p20, y58, mon("b59_fr57", "June"), d21)
    said("1958 年底又贬值将近 15\\%，同时放开 90\\% 的进口", F["b59_fr_end58"][0], *F["b59_fr58"])
    has("b59_fr_end58", "at the end of 1958")
    d29c, y58b, d26b, y48 = F["b59_fr_imf"]
    said("这一次的代价，国际清算银行 1959 年的年报也记了下来", bis_year("bis1959"))
    has("b59_fr_cuts", "removal of a large number of subsidies")
    said("1958 年底的措施主要靠取消大量补贴来压预算赤字", F["b59_fr_end58"][0])
    has("b59_fr_food", "certain foodstuffs being totally abolished", "nationalised enterprises were increased")
    say("有些食品的补贴全部取消，几种农产品的补贴部分取消，国有企业的收费也提高了")
    has("b59_fr_index", "whether referring to wages or to agricultural prices, were cancelled",
        "Only the guaranteed minimum wage")
    said("所有把工资或农产品价格与物价指数挂钩的协议都取消了，只有最低工资仍与“179 种商品指数”挂钩", F["b59_fr_index"][0])
    y58f, fr89, _ = F["b59_fr_prices"]
    has("b59_fr_prices", "F r a n c e and N o r w a y , where food prices rose sharply owing to the reduction in food "
                         "subsidies")
    assert page("b59_fr_prices") == page("b59_fr_food") and y58f == F["b59_fr_end58"][0]
    said("1958 年，食品价格因补贴减少而急剧上涨，法国的生活费用涨了 8.9\\%", y58f, fr89)
    y57x, y58x = F["b59_fr_expected"]
    has("b59_fr_expected", "price rises were naturally to be expected", "a more realistic price structure")
    assert page("b59_fr_expected") == page("b59_fr_prices") and y58x == y58f
    said("照年报的说法，1957 年与 1958 年为理顺价格结构采取的各项措施，本来就会推高物价", y57x, y58x)
    said("新的美元平价是 493.706 法郎，12 月 29 日正式向基金组织申报；在那以前，法国自 1948 年 1 月 26 日起",
         F["b59_fr_parity"][0], mon("b59_fr_imf", "December"), d29c, y48, mon("b59_fr_imf", "January"), d26b)
    fr = F["bt_fr"]
    assert round(F["b59_fr_parity"][0], 1) == fr[16] and (fr[2], fr[3], fr[4]) == (y48, 1, d26b)
    said("1960 年起，1 新法郎合 100 旧法郎", fr[19], 1, fr[20])
    y62b, b168, b33, y66, b28 = F["ga_france"]
    said("法国 1962 年第一季度开始买黄金时，美国的黄金存量是 168 亿美元；到 1966 年第三季度减少的 33 亿美元里，28 亿美元是法国直接买走的",
         y62b, b168 * 1e9, y66, b33 * 1e9, b28 * 1e9)
    has("ga_france", "in the first quarter of 1962", "through the third quarter of 1966")
    has("ga_france2", "purchased directly by France")
    y67h = F["ga_t91"][4]
    assert "1967 Oct. End of persistent French gold purchases" in t91
    said("法国持续的购买到 1967 年 10 月才停止", y67h, mon("ga_t91", "Oct."))
    y65b, y34 = F["bo_convert"]
    said("1965 年起法国有计划地把美元负债换成黄金", y65b)
    said("1965 年创造了“过度特权”这个说法", F["im_giscard"][0])
    has("im_rueff", "not matched by commensurate gold losses", "reinvested the dollar gained")
    say("照 Gourinchas 等人的解释，美国的大笔逆差没有带来相应的黄金流失，因为债权国又把赚到的美元投回了美国")
    said("他 1964 年 9 月在东京的基金组织年会上就用过它", F["le_tokyo"][0], mon("le_tokyo", "septembre"))
    has("le_tokyo", "Tokyo")
    said("这正是 1934 年以来黄金实际价格下降的幅度", y34)
    has("bo_convert", "double the price of gold")
    said("照 Bordo 对吕夫（1967）的概括", F["bo_rueff"][0])
    said("买进了将近 10 亿美元的法国黄金", F["ga_buyback"][0] * 1e9)
    has("ga_buyback", "almost $1 billion of French gold during the next year")


def debate(F, Y, Q):
    chk("    six explanations (六种解释)", F["ei_consensus"][0], told("至少提出了六种解释", "提出了", "种"))
    y68, g7 = F["bo_us_lower"]
    said("1968 年以前，美国的通胀率还低于除美国以外七国集团", y68)
    chk("    G7 (七国集团)", g7, told("除美国以外七国集团", "以外", "国集团"))
    said("构成了 1960 年代货币争论的“政治层面”", F["ga_identification"][0])
    said("国际清算银行 1968 年也提到", bis_year("bis1968"))
    said("在 Despres、Kindleberger 与 Salant（1966）看来", F["bo_dks"][0])
    said("银行的类比出自 Kindleberger（1965），特里芬（1966）写文章反驳过", *F["ga_bank_fn"])
    has("bo_dks2", "U.S. capital markets were deeper", "because of a higher return")
    y59c, y70c = F["bo_current"]
    said("除 1959 年以外，美国到 1970 年一直有经常账户的顺差", y59c, y70c)
    has("bo_current", "capital outflows exceeded the current account surplus")
    has("bo_fn58", "largely transferred to Europe by the interest paid on dollar holdings")
    has("bo_believed", "that they believed")
    say("以及他们认为美国得到的铸币税")
    has("ga_bank_fn", "Kindleberger (1965)", "Triffin (1966a)")
    de = F["bt_de"]
    said("西德的马克 1961 年升值 5\\%，1969 年升值 9.3\\%", F["b61_reval"][3], F["b61_reval"][0], de[21],
         F["b70_de_reval"][1])
    chk("    4.00 / 3.66 - 1 (9.3%)", 100 * (de[18] / de[24] - 1), F["b70_de_reval"][1], tol=0.05)
    _, y57, _, y46, y47 = F["bo_scarce"]
    said("照 Bordo 转述的特里芬（1957）的看法，基金组织 1946 年没有宣布美元为稀缺货币是一个错误，否则 1947 年英镑可兑换的灾难本可避免",
         y57, y46, y47)
    y49, y67, _ = F["bo_few"]
    said("1949—1967 年，十国集团国家的平价很少变动", y49, y67)
    said("照国际清算银行 1961 年的说法，西德与荷兰的升值", bis_year("bis1961"))
    has("b61_substitute", "In neither case were they primarily intended as, nor will they function as, a substitute")
    # fig:brettonwoods_parities
    P = parities()
    said("四种货币的美元价值，1949 年 10 月—1971 年 8 月（各自 1949 年 10 月的平价为 100）", START.year, START.month,
         END.year, END.month, START.year, START.month, 100)
    assert all(abs(s.iloc[0] - 100) < 1e-9 for s in P.values())
    c = F["bt_de_c"]
    said("马克 1969 年 9 月 29 日到 10 月 26 日浮动，1971 年 5 月 9 日起又浮动", de[21], mon("bt_de_c", "September"), c[0],
         mon("bt_de_c", "October"), c[1], de[25], de[26], de[27])
    said("数据：Bordo（1993）表 1.2", src_year("bordo1993"), float(table_no("bordo1993img")))
    say("英镑与法郎降低平价，马克两次升值，日元不变")


def deeper(F, Y, Q):
    src = meta()["sources"]
    notes = meta()["notes"]
    said("Bordo 与 Eichengreen 合编的《布雷顿森林体系回顾》（1993）", src_year("garber1993"))
    assert "A Retrospective on the Bretton Woods System" in src["bordo1993"]["version"]
    said("Bordo 的表 1.2 与 Garber 的表 9.1", float(table_no("bordo1993img")), float(table_no("garber1993img")))
    has("b68_closed", "ist April")
    said("把 1st 读作“ist”、10 读作“io”、1960 读作“i960”", ocr("b68_closed", "ist"), ocr("b70_fr_measures", "io"),
         i960("b61_cuts"), None)
    has("b70_fr_measures", "io per cent")
    said("World War II 读作“World War 11”", float(re.search(r"World War (\d+)", Q["bo_twothirds"]).group(1)))
    has("bo_twothirds", "World War 11")
    said("注 40 把 scarce 印作“scare”", F["bo_scarce"][0])
    keys = sorted(EDITIONS, key=edition)
    said("美国《统计摘要》1964、1968 与 1972 年版的表", *[edition(k) for k in keys])
    d4, y65 = F["fr36_date"]
    vol = re.search(r"vol\. (VIII),", src["frus1965_d36"]["version"]).group(1)
    doc = int(re.search(r"document (\d+)", src["frus1965_d36"]["version"]).group(1))
    said("戴高乐 1965 年 2 月 4 日的话，据美国国务院外交文件第 8 卷第 36 号文件的编者按", y65, mon("fr36_date", "February"), d4,
         {"VIII": 8}[vol], doc)
    # the disagreements
    d15, y47, _, d20, y47b = F["bo_1947"]
    said("英镑可兑换的中止，Bordo 写作 1947 年 8 月 20 日，国际清算银行写作自 8 月 21 日起", y47b, mon("bo_1947", "August"), d20,
         mon("b48_dates", "August"), F["b48_dates"][4])
    d19, y50 = F["bo_epu"]
    said("欧洲支付同盟，Bordo 说 1950 年 9 月 19 日成立，国际清算银行说 7 月开始运转", y50, mon("bo_epu", "September"), d19,
         mon("b59_epu", "July"))
    fourteen = cardinal(re.search(r"Dec\. (\w+) European countries", transcription("ga_t91")).group(1))
    said("1958 年 12 月底恢复可兑换的国家，Bordo 说 8 国，Garber 的表说 14 个欧洲国家", F["b59_conv"][0],
         mon("b59_conv", "December"), F["bo_eight"][0], fourteen)
    t91 = transcription("ga_t91")
    assert "1961 Oct. Establishment of the London Gold Pool" in t91
    said("黄金总库，Bordo 的表写作 1961 年 11 月，Garber 的表写作 10 月", F["bt_us"][2], mon("bt_us", "Nov."),
         mon("ga_t91", "Oct."))
    said("美国的份额，Garber 的 50\\% 是约定的份额，Bordo 引 Schwartz（1989）的 60\\% 是实际卖出的份额", F["ga_pool50"][0],
         F["bo_pool60"][2], F["bo_pool60"][1])
    d13, _, _, _, lo, hi = F["b61_london"]
    said("1960 年秋天的金价，Bordo 把 35.20 美元写作美国财政部的买价；国际清算银行记下的是伦敦 9 月中到 10 月中 35.20 至 35.25 美元的报价，"
         "美国财政部的卖价则是 35.0875 美元", F["bo_oct60b"][0], F["bo_oct60"][0], mon("b61_london", "September"),
         mon("b61_london", "October"), lo, hi, F["b61_selling"][0])
    has("bo_g10_3520", "the monetary authorities of the G10")
    said("十国的借款总安排 1961 年 12 月才议定", F["b62_gab"][0], mon("b62_gab", "December"))
    assert F["b62_gab"][0] > F["bo_oct60b"][0]                                   # the G10 came after October 1960
    said("美国的经常账户，Bordo 说除 1959 年以外到 1970 年都是顺差，Garber 说一直顺差到 1971 年", *F["bo_current"],
         F["ga_repackage"][0])
    assert t91.index("1962 Jan.") < t91.index("Feb. Beginning of the swap") < t91.index("Oct. Beginning of the GAB")
    said("互换，Bordo 说 1961 年开始，Garber 的表说 1962 年 2 月", F["bo_swaps"][0], F["ga_t91"][2], mon("ga_t91", "Feb."))
    said("吉斯卡尔·德斯坦的说法，Gourinchas 等人系于 1965 年，Lelart 系于 1964 年 9 月", F["im_giscard"][0], F["le_tokyo"][0],
         mon("le_tokyo", "septembre"))
    S = gold_series()
    said("外国官方的美元负债超过美国的黄金，Bordo 说 1964 年，Garber 说 1960 年代后半期，《统计摘要》在 1967 年底",
         F["bo_1964"][0], F["ga_wrong"][0], crossing(S, "official"))
    has("sa72_head", "liabilities maturing in 1 year or less as reported by U.S. banks")
    say("后者只包括美国银行报告的一年以内的负债")
    said("法国开始换黄金，Garber 说 1962 年第一季度，Bordo 说 1965 年", F["ga_france"][0], F["bo_convert"][0])
    fr, de = F["bt_fr"], F["bt_de"]
    said("法郎的贬值，Bordo 的表写作 8 月 10 日，国际清算银行写作 8 月 8 日；马克的新平价，表写作 10 月 26 日，国际清算银行写作 10 月 27 日生效",
         fr[25], fr[26], mon("b70_fr_deval", "August"), F["b70_fr_deval"][0], de[22], de[23], mon("b70_de_reval", "October"),
         F["b70_de_reval"][0])
    has("ga_42", "reaching as high as $42.00 per ounce")
    said("两级市场开张以后私人市场金价的高点，Garber 说最高到 42 美元，国际清算银行记下 1969 年 3 月将近 44 美元",
         F["ga_42"][0], F["b70_gold39"][1], mon("b70_gold39", "March"), F["b70_gold39"][3])
    o68, o72 = REVISED[("official", 1967)]
    assert F["sa68_official"][9] == o68 and F["sa72_official"][4] == o72
    said("1967 年 12 月对外国官方的负债，1968 年版是 140.69 亿美元，1972 年版是 140.27 亿美元", 1967, 12,
         edition("census1968img"), o68 * 1e6, edition("census1972img"), o72 * 1e6)
    for words in ("Disagreements between the sources", "(bo_1947, b48_dates)", "(bo_epu, b59_epu)",
                  "(ga_pool50, bo_pool60), not a disagreement", "(bo_oct60, b61_london, b61_selling)",
                  "(bo_g10_3520, b62_measures, b62_gab)", "(bo_current, ga_repackage)",
                  "(bo_eight, ga_t91, b59_conv)", "(im_giscard, le_tokyo)", "(ga_france, bo_convert)",
                  "(bt_fr, b70_fr_deval)", "(bt_de, b70_de_reval)", "(ga_42, b70_gold39)", "(sa68_official, sa72_official)"):
        assert words in notes, words
    # indirect testimony
    said("特里芬 1957、1960 与 1966 年的论证", F["bo_scarce"][1], F["bo_ref_triffin"][0], F["ga_bank_fn"][1])
    fn, d31, y60 = F["bo_kennedy"]
    said("肯尼迪 1960 年 10 月 31 日的话，据 Bordo 的注 68", y60, mon("bo_kennedy", "October"), d31, fn)
    said("吕夫（1967）的方案与 Despres、Kindleberger 与 Salant（1966）的看法", F["bo_rueff"][0], F["bo_dks"][0])
    fn52 = int(re.match(r"(\d+)\. According to Johnson", Q["bo_fn52"]).group(1))
    said("英国早些贬值或可免去 1968 年的冲击，是 Johnson（1968）的看法，据 Bordo 的注 52", F["bo_fn52"][2],
         int(re.search(r"Johnson \((\d{4})\)", Q["bo_fn52"]).group(1)), fn52)
    say("Bordo、Garber 与 Eichengreen 是同一本书的三章")
    for words in ("Indirect testimony", "through the editorial note of FRUS", "Kennedy's statement of 31 October 1960 "
                  "through Bordo's footnote 68", "are three chapters of one volume and cite one another",
                  "Johnson (1968) through Bordo's footnote 52 (bo_fn52)"):
        assert words in notes, words
    # single witnesses
    said("1946—1949 年欧洲的逆差", F["bo_oeec"][0], F["bo_denied"][2])
    said("1950 年代美国的逆差与黄金只据国际清算银行", F["b68_5056"][0])
    y67c, y68c, *_ = F["bo_pool_lost"]
    sol = F["bo_pool_lost"][4]
    said("总库 1967—1968 年卖出的黄金，Bordo 引 Solomon（1976）", y67c, y68c, sol)
    has("bo_pool_lost", "(Solomon 1976, 119)")
    # not obtained
    h, v = (int(x) for x in re.search(r"Horsefield (\d{4}), de Vries (\d{4})", notes).groups())
    said("基金组织自己的历史（Horsefield 1969，de Vries 1976）", h, v)
    assert "imf.org refused access" in notes
    t59 = int(re.search(r"Triffin's testimony of (\d{4})", notes).group(1))
    said("特里芬 1959 年在国会联合经济委员会的证词", t59)
    y65b, p219, p221 = F["fr36_text"]
    said("（《美国外交政策：现行文件，1965》第 219—221 页）", y65b, p219, p221)
    r67 = int(re.search(r"Rueff's book of (\d{4})", notes).group(1))
    assert r67 == F["bo_rueff"][0]
    said("吕夫 1967 年的书", r67)
    a, b, c, d = (int(x) for x in re.search(r"no figures for (\d{4})-(\d{4}) and (\d{4})-(\d{4})", notes).groups())
    said("1950—1954 年与 1956—1958 年美国的黄金与负债，本书读到的《统计摘要》各版没有，所以图从 1955 年开始，1956—1958 年空缺",
         a, b, c, d, S.index[0], c, d)
    assert S.index[0] == b + 1 and S.index[1] == d + 1
    for words in ("Not obtained", "Triffin's testimony of 1959", "the full text of de Gaulle's press conference",
                  "Federal Reserve Bulletin and Banking and Monetary Statistics"):
        assert words in notes, words


def legacy(F, Y, Q):
    us = F["bt_us"]
    said("1971 年 8 月 15 日，美国停止了黄金的兑换", us[8], us[9], us[10])
    say("“过度特权”的争论延续到今天")


def takeaways(F, Y, Q):
    S = gold_series()
    said("只有美元按每盎司 35 美元对外国货币当局兑换黄金", F["bt_us"][1])
    said("1947 年英镑恢复可兑换，一个多月就中止了", F["bo_1947"][1])
    assert (mon("bo_1947", "August"), F["bo_1947"][3]) > (mon("bo_1947", "July"), F["bo_1947"][0])   # 15/7 to 20/8
    said("1949 年 9 月英镑贬值 30.5\\%，降到 2.80 美元", F["b50_reserves"][1], 9, F["bo_cripps"][4], F["bo_cripps"][5])
    said("1958 年底主要货币恢复经常账户的可兑换，1961 年接受第八条的义务", F["b59_conv"][0], F["b61_art8"][1])
    said("西德 1961 年 3 月把马克升值 5\\%", F["b61_reval"][3], mon("b61_reval", "March"), F["b61_reval"][0])
    said("对外国的负债 1961 年、对官方的负债 1967 年超过了美国的黄金", crossing(S, "foreign"), crossing(S, "official"))
    said("1967 年 11 月英镑贬值 14.3\\%，1968 年 3 月黄金分成两个市场，特别提款权 1970 年启动", F["bo_1967"][2],
         mon("bo_1967", "November"), F["bo_1967"][3], F["bt_us"][3], F["bt_us"][6], F["bo_sdr_1970"][1])


def selfcheck(F, Y, Q):
    P, S = TRIFFIN, gold_series()
    said("若储备的需要每年增长 4\\%", 100 * P["g_sc"])
    said("1960 年底，美国的黄金是 178.04 亿美元，对外国官方的负债是 102.12 亿美元", 1960, S.loc[1960, "gold"] * 1e6,
         S.loc[1960, "official"] * 1e6)
    say("若外国官方把一半的美元换成黄金")
    m = triffin(P["R0"], P["G0"], P["GUS"], P["g_sc"], P["dG"], 12)
    t = first_below(m)
    said("$D_t=40\\times1.04^t-30-0.5t$。第 7 年$D_7\\approx52.64-33.5=19.14$，$c_7\\approx1.05$；"
         "第 8 年$D_8\\approx54.74-34=20.74$，$c_8\\approx0.96$，第 8 年跌破 1，比 5\\% 时晚两年",
         P["R0"], 1 + P["g_sc"], P["G0"], P["dG"], t - 1, m["R"][7], m["G"][7], m["D"][7], m["c"][7], t, m["R"][8],
         m["G"][8], m["D"][8], m["c"][8], t, 1, 100 * P["g"])
    a = triffin(P["R0"], P["G0"], P["GUS"], P["g"], P["dG"], 12)
    chk("    two years later (晚两年)", t - first_below(a), told("比 5\\% 时晚两年", "时晚", "年"))
    g, o = S.loc[1960, "gold"] / 100, S.loc[1960, "official"] / 100
    left = g - o / 2
    said("换走$102.12/2=51.06$亿美元，黄金剩$178.04-51.06=126.98$亿美元；官方负债剩 51.06 亿美元，覆盖率约 2.49", o, 2, o / 2,
         g, o / 2, left, o / 2 * 1e8, left / (o / 2))
    chk("    nearly three tenths of the gold (近三成)", (o / 2) / g, told("可美国的黄金少了近三成", "近", ""), tol=0.03)
    said("挪威 1950 年 4 月只好让黄油、人造黄油与面包涨价", F["b50_norway"][3], mon("b50_norway", "April"))
    r0, r1 = F["h67_rate"]
    e = sterling(r0, r1, STERLING["X"], STERLING["M_usd"])
    said("以英镑计的差额才回到 0", e["bal0"])
    said("出口要收 116.7 英镑，数量要增加约 16.7\\%", e["M1"], 100 * (e["M1"] / STERLING["X"] - 1))
    chk("    the same as the dollar's rise", e["M1"] / STERLING["X"] - 1, e["pound_per_usd_rise"], tol=1e-12)
    bn3, us22 = F["bo_pool_lost"][2:4]
    said("另外 7 家中央银行在总库以外把美元换成黄金，补回自己卖出的黄金；1967 年 12 月到 1968 年 3 月，总库卖掉 30 亿美元的黄金，美国出了 22 亿美元。"
         "1968 年 3 月的公报", F["bo_pool40"][0], F["bo_pool_lost"][0], mon("bo_pool_lost", "December"),
         F["bo_pool_lost"][1], mon("bo_pool_lost", "March"), bn3 * 1e9, us22 * 1e9,
         F["bo_pool_lost"][1], mon("fr191_meeting", "March"))


def ending(F, Y, Q):
    said("1965 年要求回到黄金的戴高乐，1969 年 4 月辞职", F["fr36_date"][1], F["b70_degaulle"][0], mon("b70_degaulle", "April"))
    has("b70_degaulle", "General de Gaulle's resignation")
    said("1968 年过度扩张的政策正在收回，可它的效果加上工资与其他收入的大幅增加，到 1969 年年中需求仍很旺", *F["b70_fr_wages"])
    m1700, y69 = F["b70_fr_flight"]
    said("上半年国际收支的逆差达 17 亿美元", m1700 * 1e6)
    has("b70_fr_flight", "in the first half of 1969", "capital flight and gold-buying")
    d8, pct, bn1 = F["b70_fr_deval"]
    said("8 月 8 日，法国政府把法郎贬值 11.1\\%，有基金组织 10 亿美元的备用安排支持", mon("b70_fr_deval", "August"), d8, pct,
         bn1 * 1e9)
    fr = F["bt_fr"]
    chk("    493.7 / 555 - 1 (11.1%)", 100 * (1 - fr[16] / (fr[27] * fr[20])), pct, tol=0.1)
    has("b70_fr_measures", "io per cent, investment tax credit introduced in 1968")
    said("提前取消 1968 年推出的 10\\% 的投资税收抵免", F["b70_fr_measures"][0], ocr("b70_fr_measures", "io"))
    said("法兰西银行的贴现率 6 月是 7\\%，10 月提到 8\\%", mon("b70_fr_rate", "June"), F["b70_fr_rate"][0],
         mon("b70_fr_rate", "October"), F["b70_fr_rate"][1])
    has("b70_de_inflow", "In the final days of April and the first days of May", "just over $4 milliard")
    said("4 月底 5 月初，流入西德的资金略多于 40 亿美元，5 月 9 日政府宣布马克的平价不变", mon("b70_de_inflow", "April"),
         mon("b70_de_inflow", "May"), F["b70_de_inflow"][0] * 1e9, mon("b70_may9", "May"), F["b70_may9"][0])
    d25 = F["b70_blackfriday"][0]
    said("9 月 25 日，为了避免“黑色星期五”，法兰克福市场关闭", mon("b70_blackfriday", "September"), d25)
    assert datetime.date(int(y69), 9, int(d25)).weekday() == 3                  # a Thursday: the market closed before Friday
    c = F["bt_de_c"]
    said("9 月 29 日到 10 月 26 日，联邦银行停止在干预上限买进美元，马克的汇率浮动，马上升了约 5\\%", mon("bt_de_c", "September"),
         c[0], mon("bt_de_c", "October"), c[1], F["b70_at_once"][0])
    has("b70_de_float", "suspend its purchases of dollars at the upper intervention limit")
    d27, p93 = F["b70_de_reval"]
    said("10 月 27 日，新的平价生效，马克升值 9.3\\%", mon("b70_de_reval", "October"), d27, p93)
    say("法国有外汇管制，资本照样外逃；西德钉住汇率，又挡不住流进来的钱。")
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 37's question"
    assert t.index("\\end{answers}") < t.index("1965 年要求回到黄金的戴高乐")
    ch37 = (ROOT / "zh" / "ch37_mundell.tex").read_text(encoding="utf-8")
    assert f"\\guidequestion{{{NEXT}}}" in ch37, "Chapter 37's question"


def models() -> None:
    """The key equation, and its arithmetic checked with numbers."""
    rng = np.random.default_rng(36)
    for _ in range(30):
        R0, share, GUS = rng.uniform(10, 200), rng.uniform(0.3, 0.95), rng.uniform(5, 100)
        g, dG, T = rng.uniform(0.005, 0.12), rng.uniform(0, 3), int(rng.integers(5, 60))
        G0 = share * R0
        m = triffin(R0, G0, GUS, g, dG, T)
        # eq:brettonwoods-triffin: R = G + D; dD_t = g R_{t-1} - dG; c = GUS / D
        chk("    R = G + D", m["R"][-1], m["G"][-1] + m["D"][-1], tol=1e-9, rel=1e-12)
        dD = np.diff(m["D"])
        assert np.allclose(dD, g * m["R"][:-1] - dG, rtol=1e-12, atol=1e-9)
        assert np.allclose(m["c"] * m["D"], GUS)
        # converting dollars into gold lowers G^US and D together: the cover rises when it is above 1, falls below 1
        D, x = m["D"][-1], rng.uniform(0, 0.5) * min(m["D"][-1], GUS) if m["D"][-1] > 0 else 0.0
        if D > 0 and x > 0 and abs(GUS - D) > 1e-9:
            assert ((GUS - x) / (D - x) > GUS / D) == (GUS > D)
        # more growth, earlier crossing; more gold, later (when the cover falls below 1 at all)
        m2 = triffin(R0, G0, GUS, g * 1.5, dG, 400)
        m3 = triffin(R0, G0, GUS, g, dG * 0.5, 400)
        base = triffin(R0, G0, GUS, g, dG, 400)
        if ((base["D"] > 0) & (base["c"] < 1)).any():
            assert first_below(m2) <= first_below(base) and first_below(m3) <= first_below(base)
        # the sterling example: the devaluation raises the price of the dollar by rate0/rate1 - 1
        r0, r1 = rng.uniform(1, 5), rng.uniform(0.5, 1) * rng.uniform(1, 5)
        e = sterling(r0, r1, 100, 100 * r0)
        chk("    the import bill rises by the price of the dollar", e["M1"] / e["M0"] - 1, e["pound_per_usd_rise"],
            tol=1e-9, rel=1e-12)
    t = TEX.read_text(encoding="utf-8")
    eqs = {lab: body.strip() for body, lab in re.findall(r"\\begin\{keyeq\}\n(.*?)\\label\{(eq:[^}]+)\}", t,
                                                         re.DOTALL)}
    assert sorted(eqs) == ["eq:brettonwoods-triffin"], sorted(eqs)
    assert eqs["eq:brettonwoods-triffin"] == ("R_t=G_t+D_t,\\qquad \\Delta D_t=gR_{t-1}-\\Delta G_t,\\qquad "
                                              "c_t=\\frac{G^{\\mathrm{US}}_t}{D_t}."), eqs
    # the same account as Chapter 27's gold-exchange pyramid R = G + F
    ch27 = (ROOT / "zh" / "ch27_interwar.tex").read_text(encoding="utf-8")
    assert "\\label{eq:interwar-pyramid}" in ch27 and "记一国中央银行的黄金为$G$，外汇为$F$" in ch27
    # the balance of payments of Chapter 5, used in the sterling example
    assert "\\label{eq:external-bop}" in (ROOT / "zh" / "ch05_external.tex").read_text(encoding="utf-8")
    assert "\\eqref{eq:external-bop}" in t


def figures_data() -> None:
    """What the figures assert of their data."""
    S = gold_series()
    assert S["gold"].is_monotonic_decreasing is False and S["gold"].iloc[0] > 2 * S["gold"].iloc[-1]
    assert S["foreign"].is_monotonic_increasing and (S["official"] <= S["foreign"]).all()
    assert crossing(S, "foreign") == 1961 and crossing(S, "official") == 1967
    P = parities()
    assert sorted(P) == sorted(["英国", "法国", "西德", "日本"])
    assert abs(P["英国"].iloc[-1] - 100 * 2.40 / 2.80) < 1e-9 and (P["日本"] == 100).all()
    assert P["法国"].min() < 65 and P["西德"].max() > 114 and P["西德"].isna().sum() == 1 + 4
    return None


# ---------------------------------------------------------------------------------------------------
# 5. The book
# the life dates from rows of the snapshot: words -> (row, index of the birth year, index of the death year)
ROW_LIVES = {"Charles de Gaulle，1890—1970": ("loc_degaulle", 0, 1),
             "Stafford Cripps，1889—1952": ("loc_cripps", 0, 1),
             "Robert Triffin，1911—1993": ("gnd_triffin_born", 0, None),
             "John Maynard Keynes，1883—1946": ("loc_keynes", 0, 1),
             "John F. Kennedy，1917—1963": ("loc_kennedy", 0, 1),
             "James Callaghan，1912—2005": ("loc_callaghan", 0, 1),
             "Michel Debré，1912—1996": ("loc_debre", 0, 1),
             "Valéry Giscard d'Estaing，1926—2020": ("loc_giscard", 0, 1),
             "Jacques Rueff，1896—1978": ("gnd_rueff_born", 0, None)}
DEATHS = {"gnd_triffin_born": "gnd_triffin_died", "gnd_rueff_born": "gnd_rueff_died"}
# the beginning of each record's heading
HEADS = {"loc_degaulle": "Gaulle, Charles de", "loc_cripps": "Cripps, Richard Stafford, Sir",
         "loc_keynes": "Keynes, John Maynard", "loc_kennedy": "Kennedy, John F.", "loc_callaghan": "Callaghan, James",
         "loc_debre": "Debré, Michel", "loc_giscard": "Giscard d'Estaing, Valéry", "gnd_triffin_born": "1911-10-05",
         "gnd_rueff_born": "1896"}
# what other chapters tell: (words of this chapter, chapter where it is told, words there)
EVENTS = [("在\\secref{sec:warfinance-plans}", "ch34_warfinance", "\\label{sec:warfinance-plans}"),
          ("在\\secref{sec:warfinance-bw}", "ch34_warfinance", "\\label{sec:warfinance-bw}"),
          ("协定允许各国管制（\\secref{sec:warfinance-bw}）", "ch34_warfinance", "资本管制写进了第六条第三节"),
          ("叫提款（\\secref{sec:warfinance-bw}）", "ch34_warfinance", "成员国用本币向基金买外汇"),
          ("叫可调整的钉住（\\chref{ch:depressionworld}）", "ch29_depressionworld",
           "战后的布雷顿森林体系仍然钉住汇率，却留下了调整平价的余地"),
          ("盎司是称量黄金的重量单位（\\chref{ch:goldstandard}）", "ch23_goldstandard", "盎司是称金银的重量单位"),
          ("英镑当时可以按固定的价格兑换黄金（\\chref{ch:goldstandard}）", "ch23_goldstandard",
           "英镑当时可以按固定的价格兑换黄金"),
          ("伦敦用高利率向世界要黄金（\\chref{ch:goldstandard}）", "ch23_goldstandard", "伦敦用这样高的利率向世界要黄金"),
          ("印度等地把储备存在伦敦（\\chref{ch:periphery}）", "ch24_periphery", "印度存在伦敦"),
          ("第二次世界大战以后，各国把美元当作储备，正是\\chref{ch:periphery}讲过的", "ch24_periphery",
           "第二次世界大战以后，各国把美元当作储备，布雷顿森林体系就建立在这个安排上"),
          ("英国 1925 年按战前的平价恢复（\\chref{ch:interwar}）", "ch27_interwar", "英国 1925 年按战前平价回到黄金"),
          ("式~\\eqref{eq:interwar-pyramid}里的$R=G+F$", "ch27_interwar", "记一国中央银行的黄金为$G$，外汇为$F$"),
          ("马歇尔计划与美国的其他援助（\\chref{ch:reconstruction}）", "ch35_reconstruction", "\\label{ch:reconstruction}"),
          ("德国马克与日元也有了对美元的固定汇率（\\chref{ch:reconstruction}）", "ch35_reconstruction",
           "到 1949 年，德国马克与日元都有了对美元的固定汇率"),
          ("那一章讲过，凯恩斯要债权国分担，最后的协定对顺差国只有稀缺货币条款", "ch34_warfinance",
           "凯恩斯要债权国分担。最后的协定向长期使用基金资源的国家收费，对顺差国则有稀缺货币条款。"),
          ("\\chref{ch:external}讲过，有人把亚洲钉住美元的固定汇率外围看作布雷顿森林体系的再现", "ch05_external",
           "亚洲出现了一个固定汇率的外围，使美国重新成为布雷顿森林国际货币体系的中心国家")]
# the chapters this one hands on to
LATER = {"ch:mundell": "ch37_mundell", "ch:floating": "ch46_floating", "ch:moderation": "ch62_moderation",
         "ch:hierarchy": "ch76_hierarchy"}


def book(F, Q):
    """Life dates and what other chapters tell."""
    t = tex_text()
    for words, (rid, i, j) in ROW_LIVES.items():
        assert words in t, words
        died = F[rid][j] if j is not None else F[DEATHS[rid]][0]
        assert f"{F[rid][i]:.0f}—{died:.0f}" in words, (words, rid)
        assert Q[rid].startswith(HEADS[rid]), (rid, Q[rid])                      # the person of the record
        COVERED.append(words)
    assert Q["gnd_triffin"] == "Triffin, Robert" and Q["gnd_rueff"] == "Rueff, Jacques"
    assert "dateOfBirth" in column("juan")["gnd_triffin_born"] and "dateOfDeath" in column("juan")["gnd_rueff_died"]
    for here, ch, there in EVENTS:
        assert here in t, here
        assert there in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (ch, there)
    for label, ch in LATER.items():
        assert f"{{{label}}}" in t, label
        assert f"\\label{{{label}}}" in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (label, ch)
    # the chapters that point here
    for ch in ("ch05_external", "ch24_periphery", "ch29_depressionworld"):
        assert "\\chref{ch:brettonwoods}" in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), ch
    print(f"ok {len(ROW_LIVES)} life dates, {len(EVENTS)} statements of other chapters, {len(LATER)} later chapters")


def witnesses(F, Q):
    """Second witnesses of statements of the text, the licences and the bibliography block of the chapter."""
    S = gold_series()
    # the BIS's gold table of 1965 against the Statistical Abstract: the stock at the end of 1965 and its fall
    assert F["b66_table"][2] == S.loc[1965, "gold"] and S.loc[1964, "gold"] - S.loc[1965, "gold"] == F["b66_table"][1]
    # the devaluations: Bordo, the BIS and Hansard
    assert F["b50_devalued"][0] == F["bo_cripps"][4] and F["h67_rate"] == [F["bo_cripps"][5], F["bo_1967"][4]]
    assert F["ga_t91"][5:7] == F["h67_rate"]
    # the gold pool: the seven other central banks; the losses of 1967-68 (Bordo after Solomon, Garber)
    assert F["bo_pool_nov"][1] == F["bo_pool40"][0] == F["ga_pool50"][1] == F["fr191_meeting"][2] == 7
    assert F["bo_pool_lost"][2:4] == [F["ga_march"][0], F["ga_march"][3]]
    # the gold price: Bordo's $35.20 ('the U.S. Treasury's buying price') is the low end of the London quotations of the
    # BIS (b61_london), above the Treasury's selling price; $35 the pool's peg and the official price of 1968
    assert F["bo_g10_3520"][1] == F["bo_oct60"][0] == F["b61_london"][4] > F["b61_selling"][0] > F["bt_us"][1]
    assert F["fr191_35"][1] == F["fr191_two"][1] == F["bt_us"][1]
    # the franc: Table 1.2 against the BIS (493.7, 26 January 1948); Garber's gold content of the franc of 1969
    assert round(F["b59_fr_parity"][0], 1) == F["bt_fr"][16]
    chk("    0.16/0.18 - 1 against 493.7/555 - 1 (the franc of 1969)", F["ga_t91"][10] / F["ga_t91"][9] - 1,
        F["bt_fr"][16] / (F["bt_fr"][27] * 100) - 1, tol=0.01)
    # the mark of 1969: Garber's $0.25 -> $0.273 against Table 1.2's 4.00 -> 3.66
    chk("    1/0.273 (Garber) against 3.66 (Table 1.2)", 1 / F["ga_t91"][12], F["bt_de"][24], tol=0.01)
    # the US gold stock of 1962 (Garber: $16.8 billion at the start of the French purchases)
    chk("    the gold stock of 1961-62 (Garber 16.8 billion)", S.loc[1961, "gold"] / 1e3, F["ga_france"][1], tol=0.2)
    # 1959: the gold stock and the total short-term liabilities about equal (Bordo; the Statistical Abstract)
    assert abs(F["sa64_total"][3] / S.loc[1959, "gold"] - 1) < 0.01
    # the SDR: Rio in September 1967 (FRUS, Bordo); the pool's end on 17 March 1968 (FRUS, Bordo, Table 1.2)
    assert F["fr193_rio"][1] == F["bo_sdr_rio"][0] and F["bo_disbanded"][0] == F["fr191_35"][0] == F["bt_us"][7]
    # the licences
    m = meta()
    lic = m["license"]
    for rid in ("nber_copyright", "nber_ocr", "nber_cover", "bis_reuse", "bis_translation", "bis_original",
                "h_copyright", "im_notice", "gnd_licence"):
        assert re.search(r"\(rows? [^)]*\b" + rid + r"\b", lic), rid
        if rid != "nber_ocr":
            assert words_of(rid) in lic, rid
    for words in ("Contains Parliamentary information licensed under the Open Parliament Licence v3.0.",
                  "short phrases only", "public domain", "the PDF prints no copyright notice", "public data",
                  "reads '0' for '\u00a9'"):
        assert words in lic, words
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    start = bib.index("% ---- 第 36 章")
    following = re.search(r"^% ---- 第 \d+ 章", bib[start + 1:], re.MULTILINE)
    end = start + 1 + following.start() if following else bib.index("\\end{thebibliography}")
    block = bib[start:end]
    assert "data/fetch/brettonwoods36.py" in block and bib.index("% ---- 第 35 章") < start
    items = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", block)}
    allitems = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", bib)}
    hansard = "“Contains Parliamentary information licensed under the Open Parliament Licence v3.0.”"
    assert hansard in items["hansard1967"]
    nber = words_of("nber_copyright")
    for key in ("bordo1993", "garber1993", "eichengreen1993"):
        assert nber in items[key] and "只引短语，其余转述" in items[key], key
    bis = items["bis36"]
    assert "不是国际清算银行的官方译文" in bis and "the original content can be found at" in bis
    assert ("This translation is not an official BIS translation, and the BIS does not guarantee its accuracy or "
            "completeness.") in bis and "provided the BIS is cited as the source." in bis
    for key in ("frus36", "statab36"):
        assert "公有领域" in items[key], key
    assert Q["im_notice"] in items["gourinchas2010"] and "只引两个说法" in items["gourinchas2010"]
    assert "没有印版权说明" in items["lelart2018"]
    assert Q["gnd_licence"] in items["gnd36"] and "公共数据" in items["loc36"]
    for rid, _, _ in ROW_LIVES.values():
        if rid.startswith("loc_"):
            assert Q[rid].replace("-", "--") in items["loc36"], rid
    # every source of the snapshot is named by its URL in its item (the page images with the text they belong to)
    item_of = {"bordo1993img": "bordo1993", "garber1993img": "garber1993", "nber1993fm": "bordo1993",
               "nber1993fmimg": "bordo1993", "bisterms36": "bis36", "hansard1967": "hansard1967"}
    for key, s in m["sources"].items():
        if key.startswith("bis1"):
            item = "bis36"
        elif key.startswith("frus"):
            item = "frus36"
        elif key.startswith("census"):
            item = "statab36"
        elif key.startswith("loc_"):
            item = "loc36"
        elif key.startswith("gnd_"):
            item = "gnd36"
        else:
            item = item_of.get(key, key)
        assert s["url"] in allitems[item].replace("\\%", "%").replace("\\_", "_"), key
    keys = set(allitems)
    cited = {k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", tex_text()) for k in c.split(",")}
    assert cited <= keys, sorted(cited - keys)
    assert set(items) == cited, sorted(set(items) ^ cited)                        # the block holds the chapter's works
    print(f"ok {len(cited)} works cited, all in the bibliography block of Chapter 36")


NAMES = ("Bordo|Garber|Eichengreen|Gourinchas|Lelart|Solomon|Schwartz|Kindleberger|Despres|Salant|Johnson|Horsefield|"
         "de Vries")


def counts() -> None:
    """The editor's limits: “不能” at most about a dozen; no cited modern author as the subject of a sentence outside
    the 史料说明; the forbidden words; who paid stated."""
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
    # who paid: wages, unemployment, controls, the austerity of 1966-69; and the two interests in the dollar
    for words in ("贬值的代价由谁承担", "实际工资", "失业", "工资率不变", "资本管制", "紧缩", "两边的利益都摆在明处",
                  "也都在替自己说话"):
        assert words in main, words
    # the three debates of the editor's notes are left open
    for words in ("第一个争论", "第二个争论", "第三个争论", "至今没有共识", "至今没有定论"):
        assert words in t, words


def main() -> None:
    df = _rows()
    F, Y, Q = facts(), years(), quotes()
    check_readings(df)
    check_text(df)
    guide(F, Y, Q)
    opening(F, Y, Q)
    world(F, Y, Q)
    convertibility(F, Y, Q)
    triffin_section(F, Y, Q)
    defence(F, Y, Q)
    debate(F, Y, Q)
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
