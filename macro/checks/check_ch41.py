"""Chapter 41 (发展经济学：二元经济、进口替代与大推进): every number and every quotation in zh/ch41_development.tex.

    python3 checks/check_ch41.py

Inputs:
  development_facts             quotations of the chapter's sources with their page: Lewis (1954), the scan of The
                                Manchester School 22 on archive.org; Lewis's autobiography and Nobel lecture, Schultz's
                                Nobel lecture and the facts of the prize of 1979 (NobelPrize.org); Prebisch (1950), the
                                United Nations document E/CN.12/89/Rev.1 on archive.org (Table 1, page 12 and the back
                                of the title page read on the page images); the World Development Report 1987 (Figure
                                5.1 read on the page image); Easterly (1997), World Bank Policy Research Working Paper
                                1807 (three passages read on the page images); Murphy, Shleifer and Vishny (1988), NBER
                                Working Paper 2708 (the equations read on the page images); the Indian Planning
                                Commission's draft outline of the Second Plan (1956), its reappraisal (1958, paragraph
                                2 read on the page image) and the Third Plan (1961, page 51 read on the page image), the
                                Ghanaian outline of the Seven-Year
                                Plan (1963), all microfilm scans on archive.org; two World Bank reports on Ghana (1967,
                                1970); the terms of use of the United Nations, the Indian and Ghanaian copyright acts; the
                                authority records of the Library of Congress and the GND. data/fetch/verify_web_quotes.py
                                checks the quotations against the documents; the rows with an empty quotation are read
                                on page images, with a transcription between « and » in the note;
                                data/fetch/development41.py fetches the documents
  maddison2023_development      Maddison Project Database 2023: GDP per head of Argentina, Brazil, Mexico, India, Ghana
                                and Korea, 1950-2022 (tab:development-paths and fig:development_paths)

This script

1. reads the numbers of every row from its quotation (or from the transcription of a page image) by the rules of
   READINGS and compares them with the value column; the misreadings of the text layers are listed in MISPRINTS;
2. finds every “…” of the text among the renderings of TRANSLATIONS, and the words of the source each one renders
   (KEYWORDS) in the row; the quotations stay short (all the sources are in copyright or allow short phrases only);
3. checks each number of the text with said(): the phrase is in the text and each number is the value of a row, a
   teaching input, or arithmetic on them (Lewis's two sectors eq:development-lewis simulated year by year, the
   effective rate of protection eq:development-erp, the two equilibria of the big push eq:development-push, the
   financing gap eq:development-gap, the growth rates of the Maddison table); every Arabic number of the text must lie
   in a phrase said() read (coverage());
4. checks the key equations as printed, the model's claims on random numbers, the data of the figures
   (figsrc/fig_ch41.py imports lewis_path(), lewis_diagram(), terms() and paths() from here), the life dates against the
   authority records, what other chapters tell, the licences and the bibliography block of Chapter 41, and the editor's
   limits;
5. lists the rows no "% 据:" anchor of the text names (common.anchors).

Set CH41_TEX to a scratch copy of the chapter to run the checks on it (mutation tests).
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
from common import ROOT, anchors, load_snapshot, quoted

TEX = Path(os.environ.get("CH41_TEX", ROOT / "zh" / "ch41_development.tex"))   # a scratch copy for mutation tests
GUIDE = "穷国怎样起飞？"
PREV = GUIDE                                        # Chapter 40's NEXT
NEXT = "日本和东亚“四小龙”的高速增长，是生产率的奇迹，还是要素积累的结果？"   # Chapter 42's question (its stub)
MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"], 1)}
FETCH = "data/fetch/development41.py"
# works of the bibliography that other chapters' blocks hold and this chapter cites unchanged
REUSED_KEYS = {"loc40", "gnd40", "bnf29", "maddison1971", "dell2010", "cggt2013", "pwt1001", "mpd2023",
               "boltvanzanden2024"}
# rows of other chapters' snapshots the anchors of this chapter name
OTHER_ROWS = {"periphery_facts": ("md_quarter",), "depressionworld_facts": ("bnf_prebisch",),
              "africa_money_facts": ("dell_25", "dell_6", "dell_channels")}
IMAGE_NOTE = "read on the page image"


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
    df, m = load_snapshot("development_facts", dtype=str, keep_default_na=False)
    assert 41 in m["used_in"] and m["fetch"] == FETCH
    assert df["id"].is_unique
    return df


@lru_cache(maxsize=None)
def meta() -> dict:
    return load_snapshot("development_facts")[1]


def facts() -> dict[str, list[float]]:
    """id -> the numbers of the value column (several are separated by ';')."""
    return {r.id: [float(x) for x in r.value.split(";")] for r in _rows().itertuples() if r.value}


def years() -> dict[str, int]:
    return {r.id: int(r.year) for r in _rows().itertuples() if r.year.isdigit()}


@lru_cache(maxsize=None)
def quotes() -> dict[str, str]:
    """id -> the quotation, with the line breaks of the source joined (empty for a row read on a page image)."""
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
    """The month `name` (English, or its abbreviation), asserted to be in what row rid says."""
    has(rid, name)
    key = name.lower().rstrip(".")
    return MONTHS[key] if key in MONTHS else [i for m, i in MONTHS.items() if m.startswith(key)][0]


def page(rid: str) -> int:
    """The first page number of a row's juan column: 'p. 155 (PDF p. 159)' -> 155."""
    return int(re.search(r"pp?\. (\d+)", column("juan")[rid]).group(1))


def chapter(name: str) -> str:
    """Another chapter's text without its comment lines."""
    t = (ROOT / "zh" / f"{name}.tex").read_text(encoding="utf-8")
    return "\n".join(l for l in t.splitlines() if not l.lstrip().startswith("%"))


# ---------------------------------------------------------------------------------------------------
# 1. Readings of the numbers (the same rules wrote the value column when the snapshot was built)
SMALL = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "eleven": 11, "twelve": 12}
TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50}
WORDS = {"twice": 2, "quarter": 1 / 4, "sixties": 1960, "seventies": 1970, "eighteen seventies": 1870,
         "nineteen thirties": 1930}


def cardinal(s: str) -> float:
    """An English cardinal: 'three', 'Six', 'forty-one'."""
    return float(sum(SMALL.get(w, 0) + TENS.get(w, 0) for w in s.lower().replace("-", " ").split()))


def figure(s: str) -> float:
    """'1,000', '30.5', '.28', '-0.75', '−0.37'."""
    return float(s.replace(",", "").replace("−", "-"))


def frac(s: str) -> float:
    """A fraction: '1/2', '2 1/2'."""
    whole, _, part = s.rpartition(" ")
    n, d = part.split("/")
    return (float(whole) if whole else 0.0) + int(n) / int(d)


def mdot(s: str) -> float:
    """A decimal with a raised point, as the Indian plans print it: '11·5' -> 11.5."""
    return float(s.replace("·", "."))


def ocr(s: str) -> float:
    """A figure the text layer misreads (MISPRINTS): 'I860' -> 1860, '1. 40' -> 1.40."""
    return float(s.replace("I", "1").replace(". ", "."))


FIGURES = re.compile(r"\d[\d,]*(?:\.\d+)?|\.\d+")
# on a page image a minus sign is a hyphen or a minus that follows no letter, digit or bracket
IMG_FIGURES = re.compile(r"((?<![\w)])[-−])?(\d[\d,]*(?:\.\d+)?|\.\d+)")
HOW = {"num": figure, "en": cardinal, "word": lambda w: WORDS[w], "frac": frac, "mdot": mdot, "ocr": ocr}
# id -> [(phrase, how)], in order. A phrase 'context|word' is searched as a whole and read from `word`. Rows not
# listed are read with all the figures of the quotation (a page image: of the transcription, with its signs). An empty
# list: the row prints no number of the story (the numbers of the items of a summary, page headers, equations, report
# numbers, a misreading quoted).
READINGS: dict[str, list[tuple[str, str]]] = {
    # Lewis (1954): the numbers of the items of the summary and the running head
    "lw_pages": [], "lw_poor": [], "lw_share": [], "lw_catchup": [], "lw_immigration": [], "lw_credit": [],
    "lw_inflation": [], "lw_tropical": [],
    # Lewis's autobiography and lecture (1979)
    "lb_britain": [("first |fifty", "en")],
    "lb_debate": [("succeeding |25", "num"), ("written |five", "en")],
    "lb_ghana": [("of |six", "en"), ("years, |1957", "num"), ("-|1963", "num")],
    "ll_theories": [("the |40", "num"), ("and |50", "num"), ("at |eight", "en")],
    "ll_recognised": [("half of the |sixties", "word")],
    "ll_eight": [("through |two", "en"), ("growing |twice", "word"), ("about |eight", "en")],
    "ll_1873": [("than |four", "en"), ("between |1873", "num"), ("and |1913", "num")],
    "ll_target60": [("the |1950", "num"), ("fixed |five", "en"), ("for the |sixties", "word")],
    "ll_surprise": [("showed |five", "en"), ("middle |sixties", "word")],
    "ll_target70": [("to |six", "en"), ("for the |70", "num"), ("showed |six", "en"), ("early |seventies", "word")],
    "ll_target80": [("fix |seven", "en"), ("the |1980", "num"), ("in |1974", "num")],
    "ll_five": [("the |quarter", "word"), ("in |1973", "num"), ("about |five", "en")],
    "ll_perhead": [("about |four", "en"), ("against |2 1/2", "frac")],
    "ll_machinery": [("is |15", "num"), ("least |eight", "en")],
    "nf_share": [("share: |1/2", "frac")],
    # Prebisch (1950)
    "pb_spanish": [],
    "pb_symbol": [("E/CN.|12", "num"), ("/|89", "num"), ("Rev.|1", "num"), ("* |27", "num"), ("April |1950", "num")],
    "pb_t1_title": [("TABLE |1", "num"), ("Base: |1876", "num"), ("-|80", "num"), ("= |100", "num")],
    "pb_t1_all": [("1876-80 |100", "num"), ("1881-85 |102.4", "num"), ("1886-90 |96.3", "num"), ("1891-95 |90.1", "num"),
                  ("1896-1900 |87.1", "num"), ("1901-05 |84.6", "num"), ("1906-10 |85.8", "num"),
                  ("1911-13 |85.8", "num"), ("1921-25 |67.3", "num"), ("1926-30 |73.3", "num"),
                  ("1931-35 |62.0", "num"), ("1936-38 |64.1", "num"), ("1946-47 |68.7", "num")],
    "pb_t1_source": [("W.5, |23", "num"), ("February |1949", "num")],
    "pb_63": [("only |63", "num"), ("in the |I860", "ocr"), ("in the |1930", "num"), ("of |58.6", "num")],
    "pb_365": [("of |36.5", "num"), ("the |eighteen seventies", "word"), ("the |nineteen thirties", "word")],
    "pb_365_ocr": [],
    # the World Development Report 1987
    "wd_groups": [("forty-one", "en"), ("orientation, |1963", "num"), ("–|73", "num"), ("and |1973", "num"),
                  ("–|85", "num")],
    "wd_41": [("the |forty-one", "en"), ("periods, |1963", "num"), ("-|73", "num"), ("and |1973", "num"), ("-|85", "num")],
    # Easterly (1997)
    "ea_takeoff": [("from |5", "num"), ("to |10", "num"), ("said |six", "en")],
    "ea_example": [("rate of |four", "en"), ("ICOR of |4", "num"), ("growth of |one", "en"), ("say, |two", "en")],
    "ea_gap12": [("number of |twelve", "en"), ("growth of |three", "en")],
    "ea_kamarck": [("Kamarck (|1967", "num"), ("surpass |seven", "en")],
    "ea_six": [("Just |6", "num"), ("the |88", "num"), ("to |one", "en")],
    "ea_fn6": [("Lewis |1954", "num"), ("p. |139", "num")],
    # Murphy, Shleifer and Vishny (1988): the equations
    "ms_wage": [], "ms_profit": [], "ms_eq8": [], "ms_eq9": [], "ms_eq10": [],
    "ms_unique": [],
    # India
    "in_crore": [("signify |100,000", "num"), (": |10,000,000", "num")],
    "in_targets": [("about |25", "num"), ("of |five", "en"), ("to |10", "num"), ("to |12", "num")],
    "in_percapita": [("Rs. |280", "num"), ("Rs. |330", "num")],
    "i3_growth": [("over |5", "num"), ("than |14", "num"), ("about |11·5", "mdot")],
    "i3_savings": [("about |8·5", "mdot"), ("about |11·5", "mdot")],
    "i3_ocr": [],
    "i8_ocr": [],
    # Ghana
    "gh_six": [("|Six", "en"), ("every |ten", "en")],
    "gh_split": [("£6|476", "num"), ("£G|540", "num")],
    # the World Bank's reports on Ghana and the laws
    "wc_number": [], "ws_number": [], "wd_krueger": [("|1974", "num")],
    "ms_rr_ref": [("September |1943", "num")], "gnd_licence": [], "il_title": [("Section |52", "num"), ("Act, |1957", "num")],
    "ws_newcedi": [("February |23", "num"), (", |1967", "num"), ("US $|1. 40", "ocr")],
    "ws_date": [("March |14", "num"), (", |1967", "num")],
}


def read(word: str, how: str) -> list[float]:
    return [HOW[how](word)]


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
    """The numbers of a quotation, by READINGS or by its figures."""
    if rid in READINGS:
        return read_rule(rid, text)
    return [figure(x.rstrip(",")) for x in FIGURES.findall(text)]


def read_image_text(rid: str, text: str) -> list[float]:
    """The numbers of the transcription of a page image, by READINGS or by its figures with their signs."""
    if rid in READINGS:
        return read_rule(rid, text)
    return [(-1 if sign else 1) * figure(n.rstrip(",")) for sign, n in IMG_FIGURES.findall(text)]


def read_image(rid: str) -> list[float]:
    return read_image_text(rid, transcription(rid))


# the misreadings of the text layers and the misprints, each printed in the quotation and named in the snapshot's
# notes with its row: (row, as printed in the quotation, the words of the notes that name it)
MISPRINTS = [("lw_central", "converts itseli", "'itseli' for 'itself'"),
             ("lw_grow", "proportion,of", "'proportion,of' without a space"),
             ("pb_spanish", "Spani1h", "'Spani1h' for 'Spanish'"),
             ("pb_63", "I860's", "'I860's' for '1860's'"),
             ("pb_rigid", "resiotance", "'resiotance' for 'resistance'"),
             ("pb_365_ocr", "86.5", "'86.5' for '36.5'"),
             ("wd_icor73", "groupsincremental", "'groupsincremental' for 'groups—incremental'"),
             ("ea_kamarck", "modem", "'modem' for 'modern'"),
             ("in_crore", "respettively", "'respettively' for 'respectively'"),
             ("in_crore", "and : 10,000,000", "a stray ':'"),
             ("in_savings", "end of. the", "a stray '.'"),
             ("in_percapita", "1055-56", "'1055-56' for '1955-56'"),
             ("i8_areas", "tke", "'tke' for 'the'"),
             ("i3_ocr", "11:5", "'11:5' for '11·5'"),
             ("i3_ocr", "8°5", "'8°5' for '8·5'"),
             ("i8_ocr", "4600", "'4600' for '4500'"),
             ("gh_savings", "@conomy", "'@conomy' for 'economy'"),
             ("gh_split", "£6476", "'£6476' for '£G476'"),
             ("gh_deficit", "es es", "'.. es es' for the leaders of the table"),
             ("ws_newcedi", "$1. 40", "'$1. 40' for '$1.40'")]


def check_readings(df: pd.DataFrame) -> None:
    src = meta()["sources"]
    n = img = 0
    for r in df.itertuples():
        assert r.file in src, (r.id, r.file)
        vals = [float(x) for x in r.value.split(";")] if r.value else []
        if src[r.file]["format"] == "image":                 # read on a page image: no quotation
            assert not r.quote and IMAGE_NOTE in r.note, r.id
            img += 1
            got = read_image(r.id)
        else:
            assert r.quote and IMAGE_NOTE not in r.note, f"{r.id}: no quotation"
            got = read_row(r.id, " ".join(r.quote.split()))
            n += bool(vals)
        assert [round(g, 6) for g in got] == [round(v, 6) for v in vals], f"{r.id}: read {got}, value column {vals}"
    quoted("rows with values, each read from its quotation", n, N_QUOTED)
    quoted("rows read on a page image (no quotation)", img, N_IMAGE)
    Q, notes = quotes(), meta()["notes"]
    for rid, word, named in MISPRINTS:
        assert word in Q[rid], (rid, word)                                      # printed in the quotation
        found = False
        for m in re.finditer(re.escape(named), notes):
            g = re.match(r"[^(]{0,80}\(([^)]*)\)", notes[m.end():])
            found |= bool(g) and rid in re.split(r",\s*", g.group(1))
        assert found, (rid, named)                                                # and named, with its row
    assert set(src) == set(df["file"]), sorted(set(src) ^ set(df["file"]))
    # the page images belong to the documents of the snapshot: the same address and file
    for key, s in src.items():
        if s["format"] == "image" and key not in ("india1961img41", "india1958img41"):    # the PDF of a scan
            base = key.replace("img", "")
            assert src[base]["url"] == s["url"] and src[base]["sha256"] == s["sha256"], key
    # a key another snapshot holds names the same document
    for name in ("solow_facts", "depressionworld_facts", "periphery_facts", "africa_money_facts"):
        other = load_snapshot(name)[1]["sources"]
        for key, s in src.items():
            if key in other:
                assert other[key]["url"] == s["url"] and other[key]["sha256"] == s["sha256"], (name, key)


N_QUOTED, N_IMAGE = 136, 24


# ---------------------------------------------------------------------------------------------------
# 2. Every “…” of the text against the snapshot
# the chapter's Chinese renderings of the quotations: rendering -> row (or rows)
TRANSLATIONS = {
    "无限的劳动供给": "lb_unlimited",
    "起飞": "ea_rostow_gap",
    "资金缺口": "ea_rostow_gap",
    "不是目的": "pb_means",
    "计划框架": "in_planframe2",
    "基础与重工业": "in_heavy",
    "核心": "i8_core",
    "珍玩": "sc_curiosities",
    "好处": "ll_virtues",
    # the misreadings of the text layers quoted in the 史料说明
    "I860's": "pb_63",
    "11:5": "i3_ocr",
    "8°5": "i3_ocr",
    "4600": "i8_ocr",
}
# the words of the source each rendering renders, in the quotation (or the transcription of the page image)
KEYWORDS = {
    "lb_unlimited": ["An “unlimited supply of labour”"],
    "ea_rostow_gap": ["“takeoff.”", "the “financing gap”"],
    "pb_means": ["not an end in itself"],
    "in_planframe2": ["'plan-frame'"],
    "in_heavy": ["'basic and heavy industries"],
    "i8_core": ["'core' projects"],
    "sc_curiosities": ["intellectual curiosities"],
    "ll_virtues": ["the virtues of exporting"],
    "pb_63": ["I860's"],
    "i3_ocr": ["11:5", "8°5"],
    "i8_ocr": ["4600"],
}


def tex_text() -> str:
    return "\n".join(l for l in TEX.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("%"))


def text_quotations() -> list[str]:
    """The “…” of the text; the closing question is Chapter 42's and the chapter's own question is in the guide and at
    the end of the opening (both checked by guide() and opening())."""
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 42's question"
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
    # the misreadings quoted in the 史料说明 are those of MISPRINTS
    deeper = re.search(r"\\begin\{deeper\}\[史料说明\].*?\\end\{deeper\}", tex_text(), re.DOTALL).group(0)
    for q in ("I860's", "11:5", "8°5", "4600"):
        assert f"“{q}”" in deeper, q
        rid = TRANSLATIONS[q]
        assert any(m[0] == rid and q in m[1] for m in MISPRINTS), q
    # every source of the chapter is in copyright or allows short phrases only: at most 12 characters
    for q in used:
        assert len(q) <= 12, f"a long quotation: “{q}”"
    print(f"ok {n} quotations of the text found in the snapshot ({len(used)} distinct)")


# ---------------------------------------------------------------------------------------------------
# 3. Numbers: said() and the parts of the text it does not read
UNITS = {"万亿": 10 ** 12, "亿": 10 ** 8, "万": 10 ** 4}
AMOUNT = re.compile(r"(\d[\d,]*(?:\.\d+)?)(?:\s*(万亿|亿|万))?")
# what is not a number of the story: labels, citations, cross-references, the key equations (models() reads them), the
# sub- and superscripts of the math and the numbers of the parts of an example
MASKS = [re.compile(r"\\begin\{keyeq\}.*?\\end\{keyeq\}", re.DOTALL),
         re.compile(r"\\begin\{equation\}.*?\\end\{equation\}", re.DOTALL),
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
    """The phrase is in the text, and each number it prints (with its unit 万, 亿, 万亿; a minus sign not read) is the
    value given, within half a unit of its last digit (plus `slack`, in the same units). None skips a number (one
    checked by an assertion)."""
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


ZH_DIGITS = {"〇": 0, "零": 0, "一": 1, "两": 2, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
ZH_UNITS = {"十": 10, "百": 100, "千": 1000, "万": 10 ** 4, "亿": 10 ** 8}


def zh(s: str) -> float:
    """A Chinese numeral: '六', '十五', '三分之二', '一半', '二十五', '七成'."""
    if "分之" in s:
        b, a = s.split("分之")
        return zh(a) / zh(b)
    if s.endswith("成"):
        return zh(s[:-1]) / 10
    if s.endswith("半"):
        return 0.5 * (zh(s[:-1]) if s[:-1] else 1)
    s = s.rstrip("多")
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


def there(ch: str, words: str) -> list[float]:
    """The words are in another chapter's text; the numbers they print."""
    assert words in chapter(ch), (ch, words)
    return [figure(d) * UNITS.get(u, 1) for d, u in AMOUNT.findall(mask(words))]


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


def version(key: str) -> str:
    return meta()["sources"][key]["version"]


def their(name: str, rid: str, *words: str) -> list[str]:
    """Row rid of another chapter's snapshot: the words are in its quotation; its values as printed (';'-separated)."""
    df = load_snapshot(name, dtype=str, keep_default_na=False)[0].set_index("id")
    q = " ".join(df.loc[rid, "quote"].split())
    for w in words:
        assert w in q, (name, rid, w)
    return df.loc[rid, "value"].split(";") if df.loc[rid, "value"] else []


def span(note: str) -> tuple[int, int, int, int]:
    """'1955-56 to 1960-61' -> (1955, 1956, 1960, 1961)."""
    a, b, c, d = (int(x) for x in re.findall(r"\d+", note))
    return a, a // 100 * 100 + b, c, c // 100 * 100 + d


# ---------------------------------------------------------------------------------------------------
# The models, with the teaching inputs of the examples and the self-check
LAB, SUBS, WBAR, ALPHA, KY = 100, 1.0, 1.3, 1 / 3, 3.0    # ex:development-lewis
LC0, LCMAX = 8, 24                                        # the capitalist sector at first, and its limit at WBAR
SC_LC = 16                                                # self-check 1
ERP_PRICE, ERP_INPUT, ERP_TF = 100, 60, 0.20              # ex:development-erp (the World Bank's sweater)
ERP_TM = (0.10, 0.40)                                     # the duties on the inputs of parts (2) and (3)
SC_ERP = (0.30, 0.5, 0.30)                                # self-check 2: tariff, input share, duty on the inputs
PUSH_L, PUSH_A, PUSH_V, PUSH_F = 100, 1.5, 0.2, 18        # ex:development-push
SC_F = 15                                                 # self-check 3
SC_GAP = (3, 0.06, 0.12)                                  # self-check 4: ICOR, target growth, domestic saving


def lewis(lc: float) -> dict:
    """The economy of ex:development-lewis with lc workers in the capitalist sector: eq:development-lewis with the
    marginal product equal to the fixed wage, the profit alpha Y_c all saved, the rest of the labour force earning SUBS."""
    yc = WBAR * lc / (1 - ALPHA)
    profit = yc - WBAR * lc
    y = yc + SUBS * (LAB - lc)
    return dict(lc=lc, yc=yc, profit=profit, y=y, s=profit / y)


def growth_rate() -> float:
    """The yearly growth of capital (profit / capital = alpha / (K/Y_c)), and of employment at the fixed wage."""
    return ALPHA / KY


def turning_year() -> float:
    return math.log(LCMAX / LC0) / math.log(1 + growth_rate())


def lewis_path(step: float = 0.1) -> pd.DataFrame:
    """Year by year (in steps of `step` years), from LC0 workers to the turning point: capital grows by the profit, and
    the employment of the capitalist sector with it."""
    T = turning_year()
    rows = []
    for t in np.arange(0, T + step / 2, step):
        lc = min(LC0 * (1 + growth_rate()) ** t, LCMAX)
        rows.append(dict(year=t, **lewis(lc)))
    rows.append(dict(year=T, **lewis(LCMAX)))
    return pd.DataFrame(rows).drop_duplicates("year")


def mpl(L: np.ndarray, K: float) -> np.ndarray:
    """The marginal product of labour of Y_c = K^alpha L^(1-alpha) (A = 1)."""
    return (1 - ALPHA) * K ** ALPHA * L ** (-ALPHA)


def capital_for(lc: float) -> float:
    """The capital at which the marginal product of lc workers is the wage."""
    return lc * (WBAR / (1 - ALPHA)) ** (1 / ALPHA)


def lewis_diagram(n: int = 400) -> pd.DataFrame:
    """Lewis's figure: the marginal product of labour for the capital that employs LC0, 2*LC0 and LCMAX at the wage."""
    L = np.linspace(2, LAB, n)
    return pd.DataFrame({"L": L, **{f"mpl{lc}": mpl(L, capital_for(lc)) for lc in (LC0, 2 * LC0, LCMAX)}})


def erp(tf: float, a: float, tm: float) -> float:
    """eq:development-erp."""
    return (tf - a * tm) / (1 - a)


def profit_alone(L: float, a: float, v: float, F: float) -> float:
    """MSV (9): the profit of one factory when no other sector industrialises (income L)."""
    return L * (1 - (1 + v) / a) - F * (1 + v)


def profit_all(L: float, a: float, v: float, F: float) -> float:
    """MSV (10): the profit of each factory when all sectors industrialise."""
    return a * (L - F) - L * (1 + v)


def f_range(L: float, a: float, v: float) -> tuple[float, float]:
    """The fixed costs F for which both equilibria exist: (9) for F above the first, (10) for F below the second."""
    return L * (1 - (1 + v) / a) / (1 + v), L - L * (1 + v) / a


def terms() -> pd.DataFrame:
    """Prebisch's Table 1: period, its first and last year, its midpoint and the ratio (1876-80 = 100)."""
    rows = []
    for a, b, v in re.findall(r"(\d{4})-(\d{2,4}) (\d+(?:\.\d)?)", transcription("pb_t1_all")):
        a, b = int(a), int(b)
        b = b if b > 100 else a // 100 * 100 + b
        rows.append(dict(period=f"{a}-{b}", first=a, last=b, mid=(a + b) / 2, ratio=float(v)))
    D = pd.DataFrame(rows)
    assert list(D["ratio"]) == facts()["pb_t1_all"]
    return D


@lru_cache(maxsize=None)
def paths() -> pd.DataFrame:
    """The Maddison Project Database 2023: GDP per head (2011 international dollars), year x economy."""
    df, m = load_snapshot("maddison2023_development")
    assert 41 in m["used_in"] and m["fetch"] == "data/fetch/maddison2023_development41.py"
    return df.pivot(index="year", columns="country", values="gdppc_2011usd")


def cagr(code: str, a: int, b: int) -> float:
    P = paths()
    return 100 * ((P.loc[b, code] / P.loc[a, code]) ** (1 / (b - a)) - 1)


def wd_periods() -> list[dict[str, list[str]]]:
    """Figure 5.1 of the World Development Report 1987, as transcribed: for 1963-73 and 1973-85, group -> economies."""
    t = transcription("wd_groups")
    parts = re.split(r"\. 19\d\d–\d\d, ", t)[1:]
    assert len(parts) == 2 and "1963–73, «Strongly" in t and "1973–85, «Strongly" in t
    return [{g: m.split(" / ") for g, m in re.findall(r"«([^»]+)»: «([^»]+)»", p)} for p in parts]


def groups_of(name: str) -> list[str]:
    """The group of an economy in each of the two periods of Figure 5.1."""
    out = [[g for g, members in period.items() if name in members] for period in wd_periods()]
    assert all(len(g) == 1 for g in out), (name, out)
    return [g[0] for g in out]


NAMES_ZH = {"ARG": "阿根廷", "BRA": "巴西", "MEX": "墨西哥", "IND": "印度", "GHA": "加纳", "KOR": "韩国"}


# ---------------------------------------------------------------------------------------------------
# 4. Numbers, section by section
def guide(F, Y, Q):
    t = TEX.read_text(encoding="utf-8")
    assert f"\\guidequestion{{{GUIDE}}}" in t and GUIDE == PREV
    assert chapter("ch40_solow").rstrip().endswith(PREV)                          # 第 40 章交来的问题
    assert ("\\guideprereq{\\chref{ch:solow}\\enspace\\nameref{ch:solow}；"
            "\\chref{ch:periphery}\\enspace\\nameref{ch:periphery}}") in t
    said("推导刘易斯（1954）的二元经济模型", F["lw_issue"][0])
    said("概括普雷维什（1950）的贸易条件论", F["pb_date"][1])
    assert "\\chapterstub" not in t


def opening(F, Y, Q):
    y52 = F["lb_bangkok"][0]
    has("lb_bangkok", "One day in August, 1952, walking down the road in Bangkok",
        "it came to me suddenly that both problems have the same solution")
    said("1952 年 8 月的一天，刘易斯", y52, mon("lb_bangkok", "August"))
    say("走在曼谷的路上", "那天他忽然想到，两个问题有同一个答案")
    has("lb_steel", "what determines the relative prices of steel and coffee")
    say("一个是钢与咖啡的相对价格由什么决定")
    has("lb_britain", "Apparently, during", "real wages in Britain remained more or less constant while profits and savings soared")
    assert told("另一个是英国工业革命的头五十年里", "头", "年") == F["lb_britain"][0]
    say("实际工资看来大致不变，利润与储蓄却猛增")                                # 'Apparently'
    has("lb_neoclassical", "could not be squared with the neoclassical framework",
        "a rise in investment should raise wages and depress the rate of return on capital")
    say("按新古典的框架，投资增加应当抬高工资、压低资本的收益率，英国的经验与此对不上")
    has("lb_unlimited", "Throw away the neoclassical assumption that the quantity of labour is fixed",
        "will keep wages down, producing cheap coffee in the first case and high profits in the second case")
    say("扔掉劳动数量固定的新古典假定，“无限的劳动供给”会压住工资，在前一个问题里带来便宜的咖啡，在后一个问题里带来高额的利润")
    has("lw_issue", "May, 1954.")
    has("lw_title", "ECONOMIC DEVELOPMENT WITH UNLIMITED SUPPLIES OF LABOUR")
    said("1954 年 5 月，《曼彻斯特学派》刊出他的文章《劳动无限供给条件下的经济发展》", F["lw_issue"][0],
         mon("lw_issue", "May"))
    has("lw_classical", "written in the classical tradition, making the classical assumption, and asking the classical question")
    say("他说，文章按古典的传统写成，作古典的假定，问古典的问题")
    has("lw_central", "The central problem in the theory of economic development")
    has("lw_why", "why saving increased relatively to national income")
    say("经济发展理论的中心问题，是理解储蓄怎样相对于国民收入提高起来")
    a, b, c, d = F["lw_central"]
    has("lw_central", "to understand the process by which a community which was previously saving",
        "converts itseli into an economy where voluntary saving is running at about 12 to 15 per cent")
    said("一个社会原先只把国民收入的 4\\% 或 5\\% 甚至更少用于储蓄和投资", a, b)
    said("要理解的是，它怎样变成自愿储蓄约占国民收入 12\\% 到 15\\% 甚至更多的经济", c, d)    # a process, not events
    has("lb_applause", "greeted equally with applause and with cries of outrage")
    assert F["lb_applause"] == [F["lw_issue"][0]]
    say("他说，文章发表以后，掌声与愤怒的叫声一样多")
    say("上一章的索洛模型回答的是，一个穷国如果像富国那样储蓄和投资，会走到哪里（\\chref{ch:solow}）。它把储蓄率当作给定。")
    has("nf_share", "Prize share: 1/2")
    assert F["nf_share"] == [0.5]
    said("1979 年，他与舒尔茨（Theodore W. Schultz，1902—1998）各得一半诺贝尔经济学奖", Y["nf_share"], None, None)
    has("nf_motivation", "pioneering research into economic development research",
        "with particular consideration of the problems of developing countries")
    say("获奖的理由是他们在经济发展上的开创性研究，特别考虑了发展中国家的问题")
    assert paragraph("上一章的索洛模型回答的是").endswith(GUIDE)                  # the opening ends with the question


def world(F, Y, Q):
    born, y15 = F["lb_born"]
    has("lb_born", "St. Lucia")
    y48, age = F["lb_professor"]
    assert y48 - y15 in (age, age + 1)
    has("lb_professor", "full professor at the University of Manchester")
    said("刘易斯生在圣卢西亚，1948 年 33 岁时成了曼彻斯特大学的正教授", y48, age)
    has("lb_students", "the throng of Asian and African students at Manchester",
        "lecturing systematically on development economics from about 1950")
    said("使他约从 1950 年起系统地讲授发展经济学", F["lb_students"][0])
    say("那几年，亚洲与非洲的许多国家刚刚独立或正在走向独立（本书的概括）")
    has("wd_copyright", "1987")
    has("wd_wars", "during the turbulent years spanning the world wars",
        "access to export markets and to manufactured imports reduced", "Their terms of trade fell drastically.")
    say("两次世界大战前后的动荡年代里，出口初级产品的国家先吃了苦头",
        "贸易条件，即出口品与进口品的价格之比，急剧恶化")
    said("按世界银行《1987 年世界发展报告》的回顾", F["wd_copyright"][0])
    has("wd_argentina", "Argentina and others", "the protective import substitution course in the 1930s")
    said("阿根廷等国因此在 1930 年代走上保护性的进口替代", F["wd_argentina"][0])
    has("wd_secular", "predictions of a secular decline in the")
    has("wd_secular2", "terms of trade against primary products were com-")
    has("wd_newly", "many of the newly independent countries thought it sensible to shift quickly to industries")
    assert told("世界银行说，战后头二十年", "头", "年") == 20
    has("wd_colonial", "previous colonial status", "breaking away from the colonial economic system")
    has("wd_protection", "the early industrialization of Europe, North America, and Japan")
    has("wd_soviet", "the Soviet Union's rapid industrialization", "government ownership, planning, and production")
    has("wd_domestic", "governments sought to restrict domestic trade", "the easing of restrictions on domestic trade")
    say("许多新国家把专门生产初级产品同殖民地的身份连在一起，独立就要脱离殖民地的经济体系",
        "欧洲与日本的早期工业化却得益于国内贸易限制的放松")
    # Maddison's quarter (Chapter 24)
    assert their("periphery_facts", "md_quarter", "about a quarter of Indian savings") == ["1/4"]
    has("lw_poor", "is not that the people are poor, but that capitalist profits are low relatively to national income")
    has("lw_savers", "Practically all saving is done by people who receive profits or rents.")
    top, share, nearer = F["lw_top10"]
    has("lw_top10", "in countries with surplus labour receive up to 40 per cent.", "nearer 30 per cent. in more developed")
    said("要问的只是收入最高的那 10\\% 的人，在剩余劳动的国家，他们拿到国民收入的 40\\% 之多", top, share)
    said("在较发达的国家，这个比例接近 30\\%", nearer)
    y40, y50, eight = F["ll_theories"]
    has("ll_theories", "balanced growth, regional integration, the two-gap model, structural inflation",
        "make sense if world trade is stagnant")
    has("ll_theories", "in the 40s and 50s we created a whole set of theories")
    said("刘易斯 1979 年回顾，1940 与 1950 年代，包括他在内的经济学家造了一整套理论", F["ll_title"][1], 1900 + y40,
         1900 + y50)
    has("ll_inwards", "oriented inwards mainly towards import substitution")
    rate, a, b = F["ll_trade"]
    said("他说，1913—1939 年世界贸易每年只增长 0.9\\%", a, b, rate)
    has("ll_recognised", "not universally recognised until the second half of the sixties")
    said("这一点要到 1960 年代后半期才被普遍承认", F["ll_recognised"][0])
    y50b, five, y60 = F["ll_target60"]
    has("ll_target60", "something that was unattainable but inspirational")
    said("联合国在 1950 年代末把每年增长 5\\% 定为 1960 年代的目标", y50b, five, y60)
    has("ll_surprise", "to everybody's surprise")
    said("到 1960 年代中期，平均增长率已经是 5\\%", F["ll_surprise"][1], F["ll_surprise"][0])
    six, y70, six2, y70b = F["ll_target70"]
    assert six == six2 and 1900 + y70 == y70b
    said("1970 年代的目标提到 6\\%，1970 年代初又已经达到", y70b, six, y70b)
    seven, y80, y74 = F["ll_target80"]
    said("联合国正准备把 1980 年代的目标定为 7\\%，1974 年的衰退开始了", y80, seven, y74)
    two, twice, eight2 = F["ll_eight"]
    assert eight2 == eight
    has("ll_eight", "two decades of unprecedented growth", "in real terms")
    said("刘易斯 1979 年说，刚过去的二十年里，世界贸易每年实际增长约 8\\%", F["ll_title"][1], eight)
    assert told("刚过去的二十年里", "过去的", "年") == 10 * two
    assert told("速度是以前最快时的两倍", "时的", "倍") == twice
    four, a, b = F["ll_1873"]
    said("1873—1913 年，它每年的增长不到 4\\%", a, b, four)
    # Rostow (by Easterly)
    has("ea_stages", "W.W. Rostow published his best-selling The Stages of Economic Growth")
    (y60r,) = F["ea_stages"]
    lo, hi, six_years = F["ea_takeoff"]
    has("ea_takeoff", "The only determinant of output takeoff that Rostow cited",
        "investment increasing from 5 to 10 percent of income", "Sir Arthur Lewis had said six years earlier")
    assert y60r - six_years == F["lw_issue"][0]
    said("按 Easterly 的转述，罗斯托 1960 年的《经济增长的阶段》为起飞只举出一个决定因素，即投资从收入的 5\\% 提到 10\\%",
         y60r, lo, hi)
    assert told("几乎就是刘易斯六年前的说法", "刘易斯", "年前") == six_years
    has("ea_rostow_gap", "Rostow used the Harrod Domar growth model", "aid to fill the “financing gap”")
    say("在他的转述里，罗斯托用哈罗德—多马模型算起飞需要的投资，再让西方的援助填上它与国民储蓄之间的“资金缺口”")


def lewis_model(F, Y, Q):
    has("lw_casual", "the workers on the docks", "carry your bag", "the jobbing gardener", "a multiple of the number")
    has("lw_unlimited", "the marginal productivity of labour is negligible, zero, or even negative")
    has("lw_capitalist", "uses reproducible capital, and pays capitalists for the use thereof")
    has("lw_subsistence", "not using reproducible capital", "Output per head is lower")
    has("lw_notfundamental", "not, however, of fundamental importance", "a wage at the subsistence level")
    has("lw_floor", "set a floor to wages in the capitalist sector")
    (gap,) = F["lw_gap"]
    said("他说，实际上两者之间通常差 30\\% 或更多", gap)
    has("lw_several", "This gap may be explained in several ways.")
    assert "higher cost of living" in column("note")["lw_explain"]
    say("这可以有几种解释，其中有城里的生活更贵，也有离开轻松的生活方式、进入更有纪律的城市环境的心理代价")
    assert np.isclose(WBAR - SUBS, gap / 100)                                     # the teaching wage: the gap of 30%
    has("lw_explain", "the psychological cost of transferring from the easy going way of life")
    has("lw_margin", "up to the point where the marginal productivity of labour equals the current wage")
    has("lw_farmer", "set by the average product of the farmer")
    has("lw_farm", "if the wage is worth less than they would be able to consume if they remained at home")
    has("lw_women", "one of the most notable features of economic development")
    said("资本主义部门的产出是$Y_c=A\\,K^{\\alpha}L_c^{1-\\alpha}$", 1)
    say("刘易斯本人用的是图，没有写这个函数")
    has("lw_process", "taking more people into capitalist employment out of the subsistence sector")
    has("lw_continue", "the process continues until the labour surplus disappears")
    has("lw_share", "not in raising wages, but in raising the share of profits in the national income")
    has("lw_grow", "profits grow relatively", "re-invested")
    has("lw_fact", "the distribution of incomes is altered in favour of the saving class")
    has("lw_political", "of immense political importance")
    has("lw_catchup", "wages begin to rise above the subsistence level")
    has("lw_noclosed", "our model of the closed economy no longer holds")
    has("lw_immigration", "mass immig")
    has("lw_credit", "The real cost of capital created by inflation is zero in this model")
    has("lw_inflation", "may be cumulative", "creating productive capital is s")
    has("lw_tropical", "the inefficiency of tropical food p")
    has("lw_foreign", "goes to the foreign consumer")
    has("lw_diagram", "OS is as before average subsistence earnings, and OW the capitalist wage.")
    has("lw_raised", "Both the surplus and capitalist employment are now larger.")
    say("本书把这个时点叫作转折点")
    # the path of the example
    s0, sT = lewis(LC0)["s"], lewis(LCMAX)["s"]
    said("资本主义部门开始只雇 8\\% 的劳动力，全社会的储蓄率不到 5\\%", 100 * LC0 / LAB, None)
    assert s0 < 0.05
    said("资本主义部门每年扩大约 11\\%，约 10 年后吸收完剩余劳动，储蓄率升到约 13\\%（本书的计算）", 100 * growth_rate(),
         turning_year(), 100 * sT)
    d = lewis(LCMAX)["y"] - lewis(LC0)["y"]
    dp = lewis(LCMAX)["profit"] - lewis(LC0)["profit"]
    assert dp / d > 2 / 3 and told("国民收入增加的部分，三分之二以上是利润", "部分，", "以上") == 2 / 3
    # ex:development-lewis
    said("教学输入：劳动力 100 人，维持生计部门每人生产并挣得 1，资本主义部门的工资$\\bar w=1.3$（刘易斯说的差距 30\\%），"
         "$\\alpha=1/3$，资本主义部门的资本—产出比为 3，利润全部再投资", LAB, SUBS, WBAR, gap, 1, 3, KY)
    said("资本主义部门开始雇 8 人，能按这个工资招到的人以 24 人为限", LC0, LCMAX)
    e0, eT = lewis(LC0), lewis(LCMAX)
    said("$Y_c=\\bar w L_c/(1-\\alpha)=1.95\\times8=15.6$，利润$5.2$，$Y=15.6+92=107.6$，储蓄率约 4.8\\%", 1,
         WBAR / (1 - ALPHA), LC0, e0["yc"], e0["profit"], e0["yc"], LAB - LC0, e0["y"], 100 * e0["s"])
    said("资本每年增加$\\alpha/3=1/9$，雇用的人数同比例增加", KY, 1, 1 / growth_rate())
    said("从 8 人到 24 人，要$\\ln3/\\ln(10/9)\\approx10.4$ 年，即第 11 年到达", LC0, LCMAX, LCMAX / LC0, 10, 9,
         turning_year(), math.ceil(turning_year()))
    assert np.isclose((1 + growth_rate()), 10 / 9)
    said("$Y_c=46.8$，利润$15.6$，$Y=46.8+76=122.8$，储蓄率约 12.7\\%", eT["yc"], eT["profit"], eT["yc"],
         LAB - LCMAX, eT["y"], 100 * eT["s"])
    said("国民收入增加 15.2，其中利润增加 10.4，约占 68\\%；换到资本主义部门的 16 人每人多挣 0.3，共 4.8（本书的计算）",
         d, dp, 100 * dp / d, LCMAX - LC0, WBAR - SUBS, (LCMAX - LC0) * (WBAR - SUBS))
    assert np.isclose(dp + (LCMAX - LC0) * (WBAR - SUBS), d)                     # the rest of the rise is the wages
    has("sc_title", "December 8, 1979")
    has("sc_finetuning", "fine-tuning entrepreneurs", "many experts fail to recognize how efficient they are")
    said("舒尔茨在 1979 年的演讲里说，农民在自己小小的配置范围里是精于微调的企业家", F["sc_title"][1])
    has("sc_1964", "I first presented an analysis of this entrepreneurial behaviour in Transforming Traditional Agriculture")
    said("他说，这种企业家行为他最早是在 1964 年的《改造传统农业》里分析的", F["sc_1964"][0])
    has("lw_petty", "Petty retail trading")
    has("lw_domestic", "domestic service")


def isi(F, Y, Q):
    day, y49 = F["pb_letter"]
    has("pb_letter", "Santiago, Chile 9 October 1949")
    has("pb_essay", "I have the honour to transmit to you herewith an essay entitled")
    has("pb_secretary", "Secretary-General of the United Nations")
    has("pb_author", "Professor Raul Prebisch")
    for rid in ("pb_letter", "pb_essay", "pb_author", "pb_secretary", "pb_signer", "pb_purpose"):
        assert column("juan")[rid] == "p. v (PDF p. 4)", rid                     # the letter is on p. v
    has("pb_signer", "GUSTAVO MARTINEZ CABANAS Executive Secretary")
    name = "Gustavo Martínez Cabañas"
    plain = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    assert plain.upper() == "GUSTAVO MARTINEZ CABANAS"                           # the signature, printed without accents
    said("1949 年 10 月 9 日，马丁内斯·卡瓦尼亚斯", y49, mon("pb_letter", "October"), day)
    say("他是联合国拉丁美洲经济委员会的执行秘书，随信转交一篇论文")
    say(f"马丁内斯·卡瓦尼亚斯（{name}，生卒年未详）在智利圣地亚哥写信给联合国秘书长")   # no dates found (STYLE §3)
    their("depressionworld_facts", "bnf_prebisch", "Raúl Prebisch (1901-1986)")
    day50, y50 = F["pb_date"]
    has("pb_lake", "DEPARTMENT OF ECONOMIC AFFAIRS Lake Success")
    assert column("juan")["pb_lake"] == "title page (PDF p. 1)"
    has("pb_spanish", "Original text: Spani1h")
    has("pb_symbol", "E/CN.12/89/Rev.1* 27 April 1950", "Original text: Spanish")
    said("英文本的文件日期是 1950 年 4 月 27 日", y50, mon("pb_date", "April"), day50)
    say("书名页署的是联合国经济事务部与纽约成功湖，原文是西班牙文")
    has("pb_purpose", "one of its main purposes")
    has("pb_schema", "the out-dated schema of the international division of labour")
    has("pb_periphery", "as part of the periphery of the world economic system",
        "producing food and raw materials for the great industrial centres")
    has("pb_assumption", "either by the lowering of prices or the corresponding raising of incomes")
    has("pb_false", "conclusively proved false by facts")
    has("pb_benefits", "have not reached the periphery in a measure comparable")
    has("pb_means", "Industrialization is not an end in itself, but the principal means")
    say("普雷维什开头就说，拉丁美洲的现实正在瓦解过时的国际分工图式")
    say("在他看来，工业化本身“不是目的”，是这些国家分享技术进步的好处、逐步提高大众生活水平的主要手段")
    # Table 1
    D = terms()
    t1, base_a, base_b, hundred = F["pb_t1_title"]
    has("pb_t1_title", "Ratio of prices of primary commodities to those of manufactured goods",
        "according to data of the Board of trade")
    assert D.iloc[0]["ratio"] == hundred and D.iloc[0]["first"] == base_a and D.iloc[0]["last"] == 1800 + base_b
    said("普雷维什的表 1 用英国贸易部的进出口平均价格指数，以 1876—1880 年为 100", t1, base_a, 1800 + base_b, hundred)
    r = D.set_index("period")["ratio"]
    said("这个比到 1936—1938 年降到 64.1，1946—1947 年回到 68.7", 1936, 1938, r["1936-1938"], 1946, 1947, r["1946-1947"])
    s63, y1860, y1930, more = F["pb_63"]
    assert np.isclose(100 / s63 - 1, more / 100, atol=0.002)                     # 63 per cent, 58.6 per cent more
    said("同样多的初级产品，1930 年代只能买到 1860 年代工业品的 63\\%，平均要多 58.6\\% 的初级产品才买得到同样多的工业品",
         y1930, y1860, s63, more)
    has("pb_quality", "do not reflect the differences in quality of finished products")
    pct, y1870, y1930b = F["pb_365"]
    said("他在第 12 页又说，从 1870 年代到 1930 年代，价格之比恶化了 36.5\\%", page("pb_365"), y1870, y1930b, pct)
    top = D.loc[D["ratio"].idxmax()]
    low = D.loc[D["ratio"].idxmin()]
    assert top["period"] == "1881-1885" and low["period"] == "1931-1935"
    said("表里的比值在 1880 年代前半期最高，为 102.4", 1880, top["ratio"])
    say("为 102.4，此后再没有回到这个高度")
    said("1921—1925 年是 67.3", 1921, 1925, r["1921-1925"])
    said("1931—1935 年最低，为 62.0", low["first"], low["last"], low["ratio"])
    assert (D["ratio"].iloc[2:] < D["ratio"].iloc[1]).all()                        # 此后再没有回到这个高度
    assert (D["ratio"].diff().iloc[2:] > 0).any()                                  # though not falling all the way
    has("pb_upswing", "competition between entrepreneurs and by the pressure of trade unions")
    has("pb_rigid", "well-known resiotance to a lowering of wages", "The pressure then moves toward the periphery")
    has("pb_organization", "lack of organization among the workers employed in primary production")
    has("pb_cycles", "the gap between prices of the two is progressively widened")
    said("普雷维什报告表 1：初级产品与工业品的价格之比（1876—1880 年＝100）", t1, base_a, 1800 + base_b, hundred)
    has("pb_t1_1938", "The figures for the thirties go only as far as 1938 inclusive.")
    said("数据是英国贸易部的进出口平均价格指数，1930 年代只到 1938 年", 1930, F["pb_t1_1938"][0])
    # the tools and the effective rate of protection
    say("进口许可是进口要先得到政府逐笔批准，高估的汇率是把本币的官价定得比市场愿意出的更高，进口因此变便宜，"
        "出口挣到的本币却变少（本书的概括）")
    said("世界银行在 1987 年的报告里说，进口替代的国家通常先生产最终工业品来替代进口", F["wd_copyright"][0])
    has("wd_final", "typically started by producing final manufactures", "initial bursts in the growth of manufacturing")
    has("wd_foreign", "sustained industrial growth depended on the expansion of exports")
    has("wd_tools", "import licensing and quantitative restrictions, to tariffs")
    has("wd_hidden", "stamp taxes, port duties, and advance deposit requirements")
    has("wd_public", "Publicly owned firms or industries have expanded rapidly")
    has("wd_multinationals", "trade policies that restricted imports of final manufactures")
    has("wd_erp_def", "the difference between value added (per unit of output) in domestic prices and value added in world "
        "prices", "expressed as a percentage of the latter")
    say("要看增加值，即产品的价值减去所用投入品的价值（本书的概括）",
        "世界银行把有效保护率定义为按国内价格算的单位增加值与按世界价格算的单位增加值之差，以后者的百分比表示",
        "投入品的关税越低，有效保护越高。最终产品的关税高于投入品的关税时，增加值所占的比例越小，同样的名义关税给的有效保护也越高")
    price, inputs, va = F["wd_sweater60"][0] + F["wd_sweater60"][1], F["wd_sweater60"][0], F["wd_sweater60"][1]
    assert F["wd_sweater"] == [ERP_PRICE] and inputs == ERP_INPUT and price == ERP_PRICE
    tf, p120 = F["wd_sweater20"]
    assert tf / 100 == ERP_TF and p120 == ERP_PRICE * (1 + ERP_TF)
    said("一件毛衣卖 100 美元，羊毛与纽扣按世界价格值 60 美元，增加值 40 美元", ERP_PRICE, ERP_INPUT, va)
    said("（1）毛衣征 20\\% 的关税，投入品免税，有效保护率是多少？", tf)
    said("（2）投入品也征 10\\% 的关税呢？（3）投入品的关税提到 40\\% 呢？", 100 * ERP_TM[0], 100 * ERP_TM[1])
    dom, dom2, world_, e50, t20 = F["wd_sweaterdom"][0], *F["wd_sweater50"]
    assert dom == dom2 == p120 - ERP_INPUT and world_ == va and t20 == tf and e50 == 100 * (dom - va) / va
    a = ERP_INPUT / ERP_PRICE
    said("国内的增加值是$120-60=60$，有效保护率$(60-40)/40=50\\%$", p120, ERP_INPUT, dom, dom, va, va,
         100 * erp(ERP_TF, a, 0))
    t10, in66, e35 = F["wd_sweater35"]
    assert t10 == 100 * ERP_TM[0] and in66 == ERP_INPUT * (1 + ERP_TM[0]) and np.isclose(e35, 100 * erp(ERP_TF, a, ERP_TM[0]))
    said("投入品值 66 美元，增加值 54，有效保护率 35\\%，与式~\\eqref{eq:development-erp}的$(0.2-0.6\\times0.1)/0.4$相同",
         in66, p120 - in66, e35, ERP_TF, a, ERP_TM[0], 1 - a)
    said("$(0.2-0.6\\times0.4)/0.4=-10\\%$，保护变成了负的（本书的计算）", ERP_TF, a, ERP_TM[1], 1 - a,
         -100 * erp(ERP_TF, a, ERP_TM[1]))
    assert erp(ERP_TF, a, ERP_TM[1]) < 0
    said("在第（1）问里，毛衣的买主每件多付 20 美元，毛衣厂的增加值多出一半", p120 - ERP_PRICE)
    assert (dom - va) / va == told("毛衣厂的增加值多出一半", "多出", "")
    # the bias
    has("wd_bias", "bias against exports in all countries for which")
    has("wd_singapore", "Singapore and the Republic of Korea")
    has("wd_agri", "favoring the manufacturing sector in every country considered except Korea",
        "the rising price support for rice production")
    has("wd_inward", "more conspicuous in the inward-oriented sample")
    p9, y69, p229, y67 = F["wd_range"]
    has("wd_range", "9 percentage points for Colombia (1969)", "229 percentage points for Chile (1967)")
    said("专栏里不利于出口的偏向最小的是哥伦比亚，1969 年为 9 个百分点", y69, p9)
    said("最大的是智利，1967 年达 229 个百分点", y67, p229)
    has("sc_priority", "top priority to industry, which includes keeping food grains cheap")
    has("sc_politics", "favor the urban population at the expense of rural people")
    said("舒尔茨在 1979 年的演讲里说，政策把最高的优先给了工业", F["sc_title"][1])
    say("关税向买进口品与国产品的消费者征税，高估的汇率向出口者征税，这里的出口者多是农民与矿山（本书的概括）")
    # the compare box
    has("wd_foreign", "since production usually required imported intermediate and capital goods")
    has("wd_foreign", "sustained industrial growth depended on the expansion of exports to provide the necessary foreign exchange")
    said("生产要用进口的中间品与资本品，工业要持续增长，就要靠扩大出口挣外汇（世界银行 1987 年的回顾）", F["wd_copyright"][0])
    has("wd_inward_def", "The average rate of effective protection for home markets is high")
    has("wd_controls", "Direct controls and licensing disincentives to the traditional export sector are pervasive")
    has("wd_overvalued", "the exchange rate is significantly overvalued")
    has("wd_outward_def", "Trade controls are either nonexistent or very low")
    has("wd_parity", "the effective exchange rates for importables and exportables are roughly equal")
    for name in ("Argentina", "Ghana", "India"):
        assert groups_of(name) == ["Strongly inward oriented"] * 2, name
    for name in ("Hong Kong", "Korea, Republic of", "Singapore"):
        assert groups_of(name) == ["Strongly outward oriented"] * 2, name
    assert all(len(sum(g.values(), [])) == F["wd_groups"][0] for g in wd_periods())   # 41 economies in each period
    n41, y63, y73, y73b, y85 = F["wd_groups"]
    said("\\cmprow{1963—1985 年的成员}", y63, 1900 + y85)
    g63, g73_ = F["wd_gnp63"]
    out63, in63 = F["wd_gnp63b"]
    has("wd_gnp63", "real per capita income for 1963-73")
    said("\\cmprow{1963—1973 年每年的人均 GNP 增长}{1.6\\%\\cite{wdr1987}}{6.9\\%\\cite{wdr1987}}", g63, 1900 + g73_, in63, out63)
    y73c, y85c, out73 = F["wd_gnp73a"]
    (in73,) = F["wd_gnp73b"]
    has("wd_gnp73b", "it fell on average by 0.1 percent a year")
    said("\\cmprow{1973—1985 年}{平均每年下降 0.1\\%\\cite{wdr1987}}{5.9\\%\\cite{wdr1987}}", y73c, 1900 + y85c, in73, out73)
    has("wd_unclear", "The links between trade strategy and macroeconomic performance are not entirely clear.")


def push(F, Y, Q):
    has("ms_rr", "introduced by Rosenstein-Rodan (1943)")
    has("ms_rr2", "they could each create income that becomes a source of demand for goods in other sectors")
    has("ms_simultaneous", "even when no sector can break even industrializing alone")
    has("ms_doctrine", "into a doctrine of balanced growth or the big push")
    has("ms_date", "September 1988")
    said("按 Murphy、Shleifer 与 Vishny 的说法，这是罗森斯坦—罗丹（Paul N. Rosenstein-Rodan，1902—1985）1943 年的想法",
         F["gnd_rr_born"][0], F["gnd_rr"][0], F["ms_rr"][0])                    # their attribution
    said("在他们 1988 年工作论文的转述里，各部门同时采用规模报酬递增的技术", F["ms_date"][0])
    has("ms_cottage", "the cottage technology for each good yields 1 unit of output for each unit of labor input")
    has("ms_irs", "a fixed cost of F units of labor to set up a factory", "α > 1 units of output for 1 unit of labor input")
    say("每种商品可以用手工生产，一单位劳动出一单位产品")
    said("工厂先要投入$F$单位劳动的固定成本，此后一单位劳动出$\\theta>1$单位产品，工资要比手工多出补偿$v$", 1)
    has("ms_wage", "w = 1 + v > 1. (6)")
    has("ms_profit", "π = y(1 − (1+v)/α) − F(1+v) (7)")
    said("总收入为$y$时，一家工厂的利润是$y\\,(1-(1+v)/\\theta)-F\\,(1+v)$", 1, 1, 1)
    has("ms_eq8", "α − 1 > v. (8)")
    said("模型要有意思，生产率的提高必须超过补偿，即$\\theta-1>v$", 1)
    has("ms_premium", "pays a wage premium", "even if its investment loses money")
    has("ms_pareto", "the Pareto superiority of the equilibrium with industrialization")
    has("ms_coordination", "Such spillovers give rise to the possibility that coordination of investments across sectors",
        "which the government can promote", "is essential for industrialization")
    say("他们说，这样的外溢使协调各部门的投资有可能成为工业化必不可少的条件，而这种协调是政府可以推动的")
    has("ms_dynamic", "A two-period model suffices to illustrate the big push in a dynamic context.")
    has("ms_railroad", "a railroad or other shared infrastructure", "defray the fixed cost of building the railroad")
    has("ms_relevance", "of some relevance for less developed countries")
    has("i8_areas", "The National Development Council also expressed the view", "the less developed areas",
        "high priority was given to social services")
    said("按它 1958 年的摘要，国家发展委员会认为，分配项目时要照顾欠发达地区的需要", F["i8_date"][0])
    # ex:development-push
    lo, hi = f_range(PUSH_L, PUSH_A, PUSH_V)
    said("教学输入：$L=100$，$\\theta=1.5$，$v=0.2$", PUSH_L, PUSH_A, PUSH_V)
    said("（2）取$F=18$，没人建厂时单独建厂的利润是多少？", PUSH_F)
    alone = PUSH_L * (1 - (1 + PUSH_V) / PUSH_A)
    said("第一式要$100\\times(1-1.2/1.5)=20<1.2F$，即$F>16.7$", PUSH_L, 1, 1 + PUSH_V, PUSH_A, alone, 1 + PUSH_V, lo)
    said("第二式要$1.5\\times(100-F)>120$，即$F<20$", PUSH_A, PUSH_L, PUSH_L * (1 + PUSH_V), hi)
    said("单独建厂：$20-1.2\\times18=-1.6$，亏本", alone, 1 + PUSH_V, PUSH_F, -profit_alone(PUSH_L, PUSH_A, PUSH_V, PUSH_F))
    said("大家都建厂：$1.5\\times82-120=3$，每家都赚（本书的计算）", PUSH_A, PUSH_L - PUSH_F, PUSH_L * (1 + PUSH_V),
         profit_all(PUSH_L, PUSH_A, PUSH_V, PUSH_F))
    assert lo < PUSH_F < hi and PUSH_A - 1 > PUSH_V
    assert profit_alone(PUSH_L, PUSH_A, PUSH_V, PUSH_F) < 0 < profit_all(PUSH_L, PUSH_A, PUSH_V, PUSH_F)
    # the financing gap
    say("增量资本产出比（ICOR）是投资与由它带来的产出增量之比，即每多产出一单位要投入几单位资本（本书的概括）")
    i2, i5 = F["ea_icor"]
    has("ea_icor", "somewhere between 2 and 5")
    said("当时的经济学家认为 ICOR 在 2 到 5 之间", i2, i5)
    inv, icor, g, pop = F["ea_example"]
    assert inv / icor == g
    said("他的例子是，投资率 4\\%、ICOR 为 4 时，增长率每年只有 1\\%", inv, icor, g)
    said("这赶不上 2\\% 的人口增长", pop)
    i12, g3 = F["ea_gap12"]
    has("ea_gap12", "the Lewis magic number of twelve percent of GDP")
    assert i12 / icor == g3 and i12 == F["lw_central"][2]
    said("投资提到刘易斯说的 12\\%，增长率是 3\\%", i12, g3)
    s4, gap8, _, _, _ = F["ea_gap"]
    assert i12 - s4 == gap8
    has("ea_gap", "So Western donors should fill the \"Financing Gap\" with foreign aid")
    said("国民储蓄仍是 4\\%，差的 8 个百分点由西方的援助去填", s4, gap8)
    has("ea_chenery", "Chenery and Strout (1966)")
    said("Chenery 与 Strout 1966 年的著名应用更强调国民储蓄", F["ea_chenery"][0])
    has("ea_rmsm", "chief economic adviser to Bank President Robert McNamara")
    said("1971 年，世界银行把 Chenery 版本的哈罗德—多马模型编成了计算机程序", F["ea_rmsm"][0])
    # ex:development-gap
    g5, i14, i115 = F["i3_growth"]
    s85, s115 = F["i3_savings"]
    has("i3_growth", "over 5 per cent per annum", "more than 14 per cent of the national income")
    said("印度计划委员会 1961 年说，要每年增长 5\\% 以上，净投资要超过国民收入的 14\\%，当时约是 11.5\\%", Y["i3_growth"],
         g5, i14, i115)
    said("国内储蓄要从约 8.5\\% 提到计划末的约 11.5\\%，其余靠外援", s85, s115)
    y73, y85, *icors = F["wd_icor73"]
    said("（3）ICOR 若是世界银行报告里强内向型国家 1973—1985 年的 8.7，14\\% 的投资能带来多少增长？", y73, 1900 + y85,
         icors[3], i14)
    said("（1）$14/5=2.8$。（2）$14-11.5=2.5$个百分点，约为国民收入的 2.5\\%。（3）$14/8.7\\approx1.6\\%$", i14, g5, i14 / g5,
         i14, s115, i14 - s115, i14 - s115, i14, icors[3], i14 / icors[3])
    # the World Bank's ICOR is of gross investment, the plan's 14 per cent net investment: the growth is understated
    has("wd_icor_def", "the ratio of gross investment")
    has("wd_icor_def2", "to the increase in GDP.")
    assert "net investment to the extent of more than 14 per cent" in transcription("i3_growth")
    said("世界银行的 ICOR 按总投资算，计划的 14\\% 是净投资，用前者去除后者，增长会算低，这里只看量级（本书的解读）", i14)
    say("ICOR 并不是常数，每个工人的资本越多，同样的投资带来的增长越少")
    # Easterly's tests
    n88, y65, y95 = F["ea_88"]
    (p60,) = F["ea_60"]
    has("ea_60", "60 percent of the countries show a negative relationship between foreign aid and investment")
    said("Easterly 的检验用了 88 个国家 1965—1995 年的数据，其中 60\\% 的国家，援助与投资呈负相关", n88, y65, 1900 + y95,
         p60)
    n6, n88b, one = F["ea_six"]
    assert n88b == n88 and one == 1
    has("ea_six", "a positive and significant coefficient greater than or equal to one")
    said("只有 6 个国家通过检验，即援助至少一对一地变成投资，而且统计上显著", n6)
    has("ea_tunisia", "fits one country: Tunisia", "is likely to have occurred by chance")
    s1, n138 = F["ea_tunisia"]
    has("ea_tunisia", "1 success out of 138 countries is likely to have occurred by chance",
        "even if the model made no empirical sense")
    said("在他看来，资金缺口模型只适合突尼斯一国，而即使模型毫无经验依据，138 国里也很可能偶然出现 1 个成功", n138, s1)
    has("ea_zambia", "Zambia would today be an industrialized country")
    has("ea_mineral", "mineral resources gave them a pool of savings")
    y67, seven = F["ea_kamarck"]
    has("ea_kamarck", "Ghana", "Nigeria", "Zambia")
    said("Kamarck 1967 年预测，加纳、尼日利亚与赞比亚等矿产给了它们储蓄的国家，增长率很可能达到或超过 7\\%", y67, seven)
    a, b, med = F["ea_median"]
    said("这些国家 1967—1992 年增长率的中位数只有 2.8\\%", a, 1900 + b, med)
    t4, y50t, y92t, g7, i35 = F["ea_table4"]
    has("ea_table4", "nine-tenths or more of the sample violate the “necessary” condition", "over 1950-92")
    said("在他的表 4 里，1950—1992 年增长达到 7\\% 以上的年份，按通常的 3.5 的 ICOR 算", t4, y50t, 1900 + y92t, g7, i35)
    assert told("九成以上没有达到所谓必要的投资率", "", "以上") == 0.9


def cases(F, Y, Q):
    (y55,) = F["in_planframe"]
    has("in_planframe2", "Professor P. C. Mahalanobis's Draft Recommendations for the Formulation of the Second Five Year Plan")
    said("1955 年 3 月，马哈拉诺比斯教授", y55, mon("in_planframe", "March"))              # 'Professor', as the outline
    has("in_date", "February 1956")
    said("按计划委员会 1956 年 2 月的草案大纲，国家发展委员会 1955 年 5 月初大体同意它的思路", F["in_date"][0],
         mon("in_date", "February"), F["in_ndc"][0], mon("in_ndc", "May"))
    has("in_agreed", "generally agreed with the basic approach of the 'plan-frame'")
    p25, five, m10, m12 = F["in_targets"]
    said("委员会要求计划能在五年里让国民收入增加约 25\\%，给 1,000 万到 1,200 万人提供就业", p25, m10 * 1e6, m12 * 1e6)
    assert told("委员会要求计划能在五年里", "能在", "年里") == five
    has("in_socialistic", "the socialistic pattern of society")
    r280, r330 = F["in_percapita"]
    a, b, c, d = span(column("year_note")["in_percapita"])
    said("人均收入要从 1955—1956 年度的 280 卢比提到 1960—1961 年度的 330 卢比", a, b, r280, c, d, r330)
    say("卢比是印度的货币")
    has("in_steel", "comparative cost advantage")
    has("in_capital", "requires a great deal of capital but it absorbs comparatively little manpower")
    has("in_demand", "does not enlarge the supply of consumer goods in the short run")
    has("in_sacrifice", "a measure of sacrifice in the matter of consumption")
    say("它说，印度在钢这样的部门可能有比较成本优势", "它的结论是，在从基础加强经济的时候，消费上作出一定的牺牲不可避免")
    has("in_diminishes", "The sacrifice diminishes as more power, more transport")
    has("in_returns", "increasingly large returns")
    has("in_balanced", "a well-organised effort to utilise labour for increasing the supplies of much-needed consumer goods")
    has("in_unemployment", "alleviates the immediate problem of unemployment")
    say("计划委员会自己的回答是，电力、运输与机器多起来以后，牺牲会减少，长远看社会得到越来越大的回报；"
        "眼下则组织劳动多产急需的消费品，缓解失业")
    i7, i12 = F["in_investment"]
    s7, s10 = F["in_savings"]
    said("计划委员会要把投资从国民收入的约 7\\% 提到第二个计划末的近 12\\%", i7, i12)
    said("国内储蓄要从约 7\\% 提到 10\\% 以上，其余靠外部资源", s7, s10)
    _, y63, _, _, y85 = F["wd_groups"]
    said("按世界银行 1987 年的分类，印度 1963—1985 年属于强内向型", F["wd_copyright"][0], y63, 1900 + y85)
    # the reappraisal of 1958
    has("i8_date", "SEPTEMBER, 1958")
    has("i8_memo", "early in May 1958, a Memorandum on the Appraisal and Prospects of the Second Five Year Plan")
    has("i8_parliament", "to the National Development Council and to Parliament")
    has("i8_parts", "divided into two parts")
    said("按计划委员会 1958 年 9 月的摘要，它在当年 5 月向国家发展委员会和议会提交备忘录", F["i8_date"][0],
         mon("i8_date", "SEPTEMBER"), mon("i8_memo", "May"))
    lakh, crore = F["in_crore"]
    (outlay,) = F["i8_ceiling"]
    (resources,) = F["i8_resources"]
    ceiling, part_a, part_b = F["i8_resolution"]                                 # para. 2, read on the page image
    assert part_a == outlay and part_a + part_b == ceiling and resources < part_a
    has("i8_resources", "for the five years at Rs. 4,260 crores")
    has("i8_resolution", "The National Development Council adopted a resolution", "divided into two parts",
        "Part 'A' of the Plan involving a total outlay of Rs. 4500 crores", "Part 'B' of the Plan")
    has("i8_ceiling", "Part 'A' of the Plan was proposed to be limited to a total outlay of Rs. 4,500 crores")
    said("估计五年的财政资源只有 4,260 克罗尔卢比", resources)
    said("克罗尔是印度的计数单位，1 克罗尔等于 1,000 万", 1, crore)
    said("国家发展委员会随后通过决议，在 4,800 克罗尔的上限内把计划分成两部分", ceiling)
    said("A 部分的总支出限于 4,500 克罗尔，除了与农业增产直接相关的项目，还有“核心”项目", part_a)
    said("其余 300 克罗尔的项目归 B 部分，有了更多资源才做", part_b)
    has("i8_reserves", "The decline in foreign exchange reserves")
    has("i8_licensing", "to curtail import licensing")
    assert "decline in foreign exchange reserves" in column("note")["i8_licensing"]
    has("i8_corelist", "the 'core' projects i.e., steel plants, coal mining, railways, and certain power projects")
    say("外汇储备下降以后，进口许可被削减，外汇主要留给钢厂、煤矿、铁路与部分电力这些核心项目")
    has("i3_ambition", "as much in five years as has been realised in the ten years of the")
    said("计划委员会 1961 年在第三个计划里说，国家要在五年里做到前两个计划十年里做到的那么多", Y["i3_ambition"])
    m14, m17 = F["i3_employment"]
    said("它估计，计划里的项目可以提供约 1,400 万个新增就业，同期劳动力却要增加约 1,700 万", m14 * 1e6, m17 * 1e6)
    assert m14 < m17                                                               # 就业仍跟不上
    has("i3_balance", "large-scale rural works programmes, village and")
    # Ghana
    y57, y66, y57b, y60 = F["loc_nkrumah_pm"]
    said("加纳 1957 年独立，恩克鲁玛（Kwame Nkrumah，1909—1972）领导它，直到 1966 年被政变推翻", y57, None, None, y66)
    six, a, b = F["lb_ghana"]
    assert b - a == six and a == y57
    has("lb_ghana", "UN Economic Adviser to the Prime Minister of Ghana", "Deputy Managing Director of the UN Special Fund",
        "Vice-Chancellor (= President) of the University of the West Indies")
    said("1957—1963 年，刘易斯先后做过加纳总理的联合国经济顾问、联合国特别基金的副总干事与西印度大学的校长", a, b)
    said("恩克鲁玛 1957 年 3 月出任总理，1960 年加纳成为共和国，他改任总统", y57b, mon("loc_nkrumah_pm", "Mar."), y60)
    y63g, y64, y69, y70 = F["gh_title"]
    has("gh_date", "December, 1963")
    said("1963 年 12 月，计划委员会办公室印出 1963/64—1969/70 年七年发展计划的简要大纲", F["gh_date"][0],
         mon("gh_date", "December"), y63g, y64, y69, y70)
    assert told("七年发展计划", "", "年发展") == y69 - y63g + 1 == 7
    has("gh_foreword", "President of the Republic of Ghana")
    has("gh_science", "based on the use of science and technology to revolutionize our agriculture and industry")
    six_, ten = F["gh_six"]
    assert told("按大纲，十个就业的加纳人里有六个在农业", "大纲，", "个就业") == ten
    assert told("十个就业的加纳人里有六个在农业", "有", "个在") == six_
    has("gh_six", "more than half of the national income")
    has("gh_savings", "a home market for the manufactured goods", "a substantial part of the savings")
    has("gh_burden", "Therefore a great burden and responsibility")
    say("计划委员会办公室写道，劳动从土地转向工厂的时候", "它接着说，经济发展成败的重担因此落在从事农业的人身上",
        "计划委员会办公室说，可可涨价会增加政府收入")
    has("gh_prerequisite", "an essential pre-requisite for that sustained growth in national income")
    total, depreciation = F["gh_total"]
    public, private = F["gh_split"]
    assert public + private == total
    said("七年的总投资估计为 10.16 亿加纳镑，其中政府 4.76 亿，私人 5.40 亿", total * 1e6, public * 1e6, private * 1e6)
    (y65,) = F["ws_pound"]
    said("加纳镑（£G）是 1965 年 7 月以前的加纳货币", y65, mon("ws_pound", "July"))
    deficit, public2 = F["gh_deficit"]
    assert public2 == public
    said("政府的部分有 8,700 万靠短期借款，即赤字财政", deficit * 1e6)
    (cocoa,) = F["gh_cocoa"]
    said("可可价格按每吨 190 加纳镑的平均数估计", cocoa)
    has("gh_residual", "which is a residual element.")
    # the case box
    said("\\begin{case}{加纳 · 1947—1970 · 可可销售局}", F["wc_cmb"][0], F["wc_date"][1])
    say("付账的是种可可的农民（本书的解读）")
    has("wc_monopoly", "owned monopoly, the Cocoa Marketing Board (CMB)")
    said("按世界银行农业项目局 1970 年的项目报告，可可销售局是国营的独家收购者，按 1947 年的条例设立", F["wc_date"][1],
         F["wc_cmb"][0])
    has("wc_cmb", "permitted it to fix producer prices for cocoa")
    has("wc_support", "at times of low world prices")
    nc90, y57c = F["wc_reserve"]
    has("wc_noncocoa", "used by the Government for non-cocoa purposes")
    said("按报告用新塞地计的数，它的价格稳定储备 1957 年约有 9,000 万", y57c, nc90 * 1e6)
    day, y67, usd = F["ws_newcedi"]
    said("新塞地（NC）是 1967 年 2 月起的加纳货币", y67, mon("ws_newcedi", "February"))
    y65b, _ = F["wc_1965"]
    has("wc_1965", "prohibited CMB from accumulating reserves", "transfer operating surpluses to the Government")
    said("1965 年的新法律禁止销售局积累储备", y65b)
    # para. 3.01: the authors put the decline down to four decisions of the Government, and list three results
    has("wc_early", "taken in the early 1960's to:")
    assert "Government decisions" in column("note")["wc_early"]
    said("报告的作者把产量下降主要归于政府 1960 年代初的几项决定", F["wc_early"][0])
    has("wc_noncocoa", "used by the Government for non-cocoa purposes")
    has("wc_reduce", "reduce producer prices in line with falling world prices")
    has("wc_marketing", "establish a new system of cocoa marketing")
    has("wc_disband", "disband, for all practical purposes, the Ministry")
    assert "cocoa extension and disease control services" in column("note")["wc_disband"]
    say("除了动用销售局的资金，政府还随世界价格下跌一路压低收购价，另建可可的销售体系，"
        "并实际上解散了农业部的可可推广与病虫害防治服务")                          # (a) is the paragraph before
    (c12,) = F["wc_1959"]
    y59, c67, y65c = F["wc_1965price"]
    (grams,) = F["wc_lb"]
    said("收购价从 1959 年的每磅 12 美分降到 1965 年的 6.7 美分，1 磅约合 0.45 公斤", y59, c12, y65c, c67, 1, grams / 1000)
    has("wc_plantings", "the neglect of farm upkeep for the same reason")
    assert "through inadequate producer prices" in column("note")["wc_plantings"]
    has("wc_pests", "of pest and disease attack")
    say("新种植与农场的管理都因价格太低而减少，病虫害也卷土重来")
    g312, y62, g27, y66b = F["wc_pesticide"]
    said("可可农药的用量从 1962 年最多的 31.2 万加仑降到 1966 年的 2.7 万加仑", y62, g312, y66b, g27)
    y64c, y65d, crop = F["wc_crop"]
    (t400,) = F["wc_400"]
    said("收成在 1964/65 年度达到 568,032 吨，此后下降，近年平均约 40 万吨", y64c, y65d, crop, t400)
    (y66c,) = F["wc_change"]
    c13, _ = F["wc_13"]
    said("1966 年政府更迭以后，收购价提到每磅 13 美分", y66c, c13)
    c27, c13b, c15 = F["wc_split"]
    c77, _ = F["wc_duty"]
    assert c13b == c13
    # the report 'may not be ... quoted as representing their views' (wc_rights2): its authors, not the Bank
    assert "世界银行按" not in tex_text()
    said("报告的作者按每磅 27 美分的长期价格算，农民得 13 美分，销售局的盈余 1.5 美分，出口税 7.7 美分", c27, c13b, c15, c77)
    nc80, t400b = F["wc_80"]
    assert t400b == t400
    said("收成若是 40 万吨，政府每年留下约 8,000 万新塞地", t400b, nc80 * 1e6)
    has("wc_80", "is justifiable only in the light of Ghana's present overall difficult economic and financial position",
        "and if the Government is prepared to actively help farmers")
    say("他们认为，政府留下这么大的份额，要加纳眼下的经济与财政确实困难，政府又愿意积极帮农民把生产率提到种可可有利可图的"
        "水平，才说得过去")
    said("按世界银行 1987 年的分类，加纳与印度 1963—1985 年都属于强内向型", F["wd_copyright"][0], y63, 1900 + y85)
    said("计划委员会的草案大纲，1956 年 2 月", F["in_date"][0], mon("in_date", "February"))
    said("计划委员会办公室的简要大纲，1963 年 12 月", F["gh_date"][0], mon("gh_date", "December"))
    has("gh_title", "SEVEN-YEAR DEVELOPMENT PLAN")


def data_check(F, Y, Q):
    P = paths()
    kg60, kg80 = P.loc[1960, "KOR"] / P.loc[1960, "GHA"], P.loc[1980, "KOR"] / P.loc[1980, "GHA"]
    said("1960 年，韩国的人均 GDP 约为加纳的七成，1980 年已是加纳的三倍多", 1960, 1980)
    assert abs(kg60 - told("约为加纳的七成", "加纳的", "")) < 0.05 and 3 < kg80 < 3.5
    said("这二十年里，韩国每年增长约 7.1\\%，加纳每年下降约 0.9\\%（本书的计算）", cagr("KOR", 1960, 1980),
         -cagr("GHA", 1960, 1980))
    assert cagr("GHA", 1960, 1980) < 0
    _, y63, _, _, y85 = F["wd_groups"]
    said("世界银行把韩国 1963—1985 年归入强外向型，把加纳归入强内向型", y63, 1900 + y85)
    assert groups_of("Korea, Republic of") == ["Strongly outward oriented"] * 2
    said("国际元是按 2011 年购买力平价折算的记账单位", 2011)
    ak = P.loc[1950, "ARG"] / P.loc[1950, "KOR"]
    said("1950 年，阿根廷的人均 GDP 约是韩国的八倍，1990 年韩国已经超过阿根廷", 1950, 1990)
    assert abs(ak - 8) < 0.5 and P.loc[1990, "KOR"] > P.loc[1990, "ARG"]
    import check_ch40                                                              # the poorest quarter of Chapter 40
    _, _, q = check_ch40.quarters()
    D = check_ch40.pwt().sort_values("lny0")
    behind = int((D.iloc[:q]["g"] < check_ch40.quarters()[1] / 100).sum())
    said("上一章的检验里，1960 年最穷的四分之一共 27 个国家，有 13 个此后增长得比最富的四分之一的平均速度慢",
         check_ch40.PWT_FIRST, q, behind)
    # the table
    said("\\caption{六个经济体的人均 GDP（2011 年国际元）与每年的增长率（本书的计算）}", 2011)
    said(" & 1950 & 1980 & 2000 & 1950—1980（\\%） & 1980—2000（\\%） \\\\", 1950, 1980, 2000, 1950, 1980, 1980, 2000)
    for code, name in NAMES_ZH.items():
        v = [P.loc[y, code] for y in (1950, 1980, 2000)]
        line = (f"{name} & " + " & ".join(f"{x:,.0f}" for x in v) + f" & {cagr(code, 1950, 1980):.1f} & "
                f"{cagr(code, 1980, 2000):.1f} \\\\")
        said(line, *v, cagr(code, 1950, 1980), cagr(code, 1980, 2000))
    said("\\datasource{Maddison Project Database 2023（Bolt 与 van Zanden 2024，CC BY 4.0），工作簿 mpd2023\\_web.xlsx 的 Full data 表",
         2023, 2024, 4.0, 2023)
    assert "2024" in load_snapshot("maddison2023_development")[1]["citation"]
    say("增长率是两端年份之间的年均复合增长率")                                  # cagr(): compound, between the end years
    said("1950—1980 年每年分别约 4.4\\% 与 3.5\\%（本书的计算）", 1950, 1980, cagr("BRA", 1950, 1980), cagr("MEX", 1950, 1980))
    assert groups_of("Brazil") == ["Moderately outward oriented"] * 2
    assert groups_of("Mexico") == ["Moderately inward oriented"] * 2
    _, y63, _, _, y85 = F["wd_groups"]
    said("世界银行把巴西 1963—1985 年归入中等外向型", y63, 1900 + y85)
    said("账在后来才来，1980 年以后，三个拉美国家都增长得很慢", 1980)
    assert all(cagr(c, 1980, 2000) < 1.5 for c in ("ARG", "BRA", "MEX"))
    said("又怎样在 1982 年收场", there("ch51_latamdebt", "1982 年墨西哥危机")[0])
    said("债务怎样为 1970 年代的进口替代付账", 1970)
    said("印度 1950—1980 年每年只增长约 1.4\\%，1980 年以后加快", 1950, 1980, cagr("IND", 1950, 1980), 1980)
    assert cagr("IND", 1980, 2000) > cagr("IND", 1950, 1980)
    g = P["GHA"]
    peak = int(g[g.index <= 1990].idxmax())
    said("加纳的人均 GDP 在 1971 年以后下降", peak)
    said("到 1983 年，它只有 1,487 国际元，比 1950 年还低", 1983, g[1983], 1950)
    assert g[1983] < g[1950] and int(g[g.index > 1950].idxmin()) == 1983
    q25, y73, five = F["ll_five"]
    has("ll_five", "just about the same in LDCs and in MDCs")
    said("刘易斯 1979 年说，到 1973 年为止的四分之一个世纪里，发展中国家与发达国家的 GDP 每年都增长约 5\\%",
         F["ll_title"][1], y73, five)
    assert told("的四分之一个世纪里", "的", "个世纪") == q25
    four, two5 = F["ll_perhead"]
    said("人均增长每年约 2.5\\%，发达国家约 4\\%", two5, four)
    has("ll_remarkable", "continued to widen rapidly")
    has("ll_industry", "industrial production grew faster in LDCs than in MDCs")
    said("刘易斯 1979 年说，发展中国家的工业生产增长得比发达国家快", F["ll_title"][1])
    p15, n8 = F["ll_machinery"]
    said("至少八个发展中国家的机器已占制造业产出的 15\\% 以上", p15)
    assert told("至少八个发展中国家", "至少", "个") == n8
    has("ll_machinery", "(India, Brazil, Singapore, Chile, Korea, Argentina, Mexico and Israel)")
    say("即印度、巴西、新加坡、智利、韩国、阿根廷、墨西哥与以色列")
    y63s, s13 = F["wd_saving"]
    y85s, s31 = F["wd_saving85"]
    has("wd_saving", "was exceeded by all other groups in 1963")
    said("强外向型经济 1963 年的国内储蓄只占 GDP 的 13.0\\%，是四组里最低的", y63s, s13)
    said("到 1985 年，它升到 31.4\\%", y85s, s31)
    a, b, i25 = F["wd_icor63"]
    i33, i52 = F["wd_icor63b"]
    y73b, y85b, o1, o2, n1, n2 = F["wd_icor73"]
    said("1963—1973 年外向型两组的增量资本产出比平均是 2.5", a, 1900 + b, i25)
    said("中等内向型与强内向型分别是 3.3 与 5.2", i33, i52)
    said("1973—1985 年各组都明显变差", y73b, 1900 + y85b)
    said("外向型两组是 4.5 与 5.0。内向型两组是 6.2 与 8.7", o1, o2, n1, n2)
    said("六个经济体的人均 GDP，1950—2022 年（2011 年国际元，对数刻度）", 1950, P.index.max(), 2011)
    said("(a) 三个拉美国家 1980 年以前增长，此后停滞。(b) 印度、加纳与韩国 1960 年的起点相差不到一倍，此后分开。", 1980, 1960)
    v60 = [P.loc[1960, c] for c in ("IND", "GHA", "KOR")]
    assert max(v60) / min(v60) < 2                                                 # 相差不到一倍
    said("虚线标出 1980 年。数据：Maddison 项目数据库 2023 年版（Bolt 与 van Zanden 2024，CC BY 4.0）", 1980, 2023, 2024, 4.0)
    assert "axvline(1980" in (ROOT / "figsrc" / "fig_ch41.py").read_text(encoding="utf-8")


def debate(F, Y, Q):
    has("sc_calculating", "are calculating economic agents")
    said("站在另一边的是舒尔茨（本书的概括）。他在 1979 年的演讲里说，农民是计算成本、收益与风险的经济人", F["sc_title"][1])
    said("按世界银行工作人员 1970 年的报告，加纳可可的新种植减少、农场疏于管理，原因是收购价太低", F["wc_date"][1])
    assert "少喷农药" not in tex_text()                                             # the pesticides fell with the services
    has("sc_mistake", "standard economic theory is inadequate for understanding low income countries")
    has("sc_curiosities", "at best intellectual curiosities")
    has("sc_prospects", "provided they are not dissipated by politics and governmental policies that discriminate against agriculture")
    has("lb_debate", "five books and numerous articles", "The debate continues.")
    y25, b5 = F["lb_debate"]
    assert told("刘易斯说，二十五年里其他学者写了五本书", "说，", "年里") == y25
    assert told("其他学者写了五本书", "写了", "本书") == b5
    _, base_a, base_b, _ = F["pb_t1_title"]
    said("普雷维什的表从 1876—1880 年算起，用的是英国一国的进出口价格，1930 年代只算到 1938 年", base_a, 1800 + base_b, 1930,
         F["pb_t1_1938"][0])
    has("wd_chapter2", "The data in Chapter 2 do show a long-term decline in")
    has("wd_caution", "they take no account of quality improvements in manufactures")
    said("世界银行 1987 年说，它第 2 章的数据也显示初级产品的贸易条件长期下降", F["wd_copyright"][0], F["wd_chapter2"][0])
    has("wd_maywell", "it may well be true that the relative price of primary commodities is in long-term decline")
    has("wd_response", "whether an inward-oriented strategy is the right response")
    has("ll_terms", "though that did not happen this time")
    has("ll_slower", "the terms of trade will move against them")
    said("刘易斯 1979 年也说，贸易增长快时", F["ll_title"][1])
    n41, *_ = F["wd_41"]
    assert n41 == F["wd_groups"][0] == 41
    said("世界银行把 41 个经济体按贸易战略分组", n41)
    has("wd_superior", "The figures suggest", "broadly superior to that of the")
    assert "in almost all respects" in column("note")["wd_superior"]
    say("认为数字显示外向型经济的表现几乎在各方面都大体更好", "它也承认，分类的中间两组可能有争议")
    has("wd_intermediate", "there may be scope for disagreement over the two intermediate subgroups")
    has("wd_korea", "the Republic of Korea, sustained their industrial")
    has("lw_protection", "an equally valid foundation of arguments for protection")
    said("刘易斯 1954 年的总结里说", F["lw_issue"][0])
    said("巴西与墨西哥 1980 年以前的增长", 1980)
    has("ms_unique", "equilibrium can be unique")
    assert "没有找到支持大推进理论的证据" in chapter("ch31_soviet")
    for d in ("第一个争论", "第二个争论", "第三个争论", "第四个争论"):
        say(d)


def deeper(F, Y, Q):
    assert "22 (2), May 1954" in version("lewis1954ms41") and "archive.org" in version("lewis1954ms41")
    said("刘易斯（1954）据互联网档案馆《曼彻斯特学派》第 22 卷的扫描本", F["lw_issue"][0], 22)
    _, n89, rev, _, y50 = F["pb_symbol"]
    said("普雷维什（1950）据互联网档案馆上的联合国文件 E/CN.12/89/Rev.1 扫描本，表 1 与第 12 页的数字按页面图像读", y50,
         F["pb_symbol"][0], n89, rev, F["pb_t1_title"][0], page("pb_365"))
    assert column("file")["pb_365"] == column("file")["pb_t1_all"] == "prebisch41img"
    has("ms_number", "Working Paper No. 2708")
    has("ea_number", "POLICY RESEARCH WORKING PAPER 1807")
    has("ea_date", "August 1997")
    said("Murphy、Shleifer 与 Vishny 用的是 NBER 第 2708 号工作论文（1988 年 9 月），Easterly 用的是世界银行第 1807 号政策研究工作论文（1997 年 8 月）",
         F["ms_number"][0], F["ms_date"][0], mon("ms_date", "September"), F["ea_number"][0], Y["ea_date"],
         mon("ea_date", "August"))
    said("印度的第二个计划草案大纲（1956）、1958 年的重新评估摘要、第三个五年计划（1961）与加纳的七年计划大纲（1963）"
         "据互联网档案馆的缩微胶片扫描本，1958 年摘要的第 2 段按页面图像读", F["in_date"][0], F["i8_date"][0], Y["i3_title"],
         F["gh_date"][0], F["i8_date"][0], 2)
    assert column("file")["i8_resolution"] == "india1958img41" and column("juan")["i8_resolution"].startswith("para. 2 ")
    say("舒尔茨的演讲没有提到刘易斯，第一个争论把两人放在一起，是本书的安排")
    said("罗森斯坦—罗丹（1943）、罗斯托（1960）、Nurkse（1953）、舒尔茨（1964）、Krueger（1974）与 Little、Scitovsky 和 Scott（1970）",
         F["ms_rr_ref"][0], F["ea_stages"][0], F["ms_doctrine"][0], F["sc_1964"][0], F["wd_krueger"][0], F["wd_lss"][0])
    say("Singer 与 Hirschman 的著作")
    for zh_name in ("辛格", "赫希曼", "纳克斯"):                                    # named in Latin script, without dates
        assert zh_name not in tex_text(), zh_name
    said("舒尔茨（1964）只按他本人演讲里的一句话提到", F["sc_1964"][0])
    say("送达信的署名者马丁内斯·卡瓦尼亚斯的生卒年没有找到")
    has("ms_rr_ref", "Problems of Industrialization of Eastern and South-Eastern Europe")
    has("wd_krueger", "The Political Economy of the Rent-Seeking Society")
    has("sc_1964", "Transforming Traditional Agriculture")
    said("联合国 1949 年的价格文件没有取得", F["pb_t1_source"][1])
    has("pb_t1_source", "Post War Price Relations in Trade Between Under-developed and Industrialized Countries")
    assert "pb_365_ocr" not in F and page("pb_365_ocr") == page("pb_365")      # the misreading: no value of its own
    misread = float(re.search(r"deterioration of (\d+\.\d) per cent", words_of("pb_365_ocr")).group(1))
    assert misread - F["pb_365"][0] == 50                                         # a 3 read as an 8
    y1860 = F["pb_63"][1]
    has("pb_63", f"I{y1860 - 1000:.0f}'s")
    said("普雷维什第 12 页的文字层把 36.5\\% 读作 86.5\\%，第 8 页把 1860 年代读作“I860's”", page("pb_365"), F["pb_365"][0],
         misread, page("pb_63"), y1860, y1860 - 1000)
    ocr_read = re.findall(r"\d+", " ".join(q for q in TRANSLATIONS if q in ("11:5", "8°5")))
    assert all(q in words_of("i3_ocr") for q in ("11:5", "8°5"))
    said("印度第三个计划的文字层把 11.5 与 8.5 读作“11:5”“8°5”，按页面图像读", F["i3_growth"][2], F["i3_savings"][0],
         *[float(x) for x in ocr_read])
    assert [float(x) for x in ocr_read] == [math.floor(F["i3_growth"][2]), 5, math.floor(F["i3_savings"][0]), 5]
    misread8 = float(re.search(r"Rs\. (\d+) crores", words_of("i8_ocr")).group(1))
    assert misread8 - F["i8_resolution"][1] == 100                                # a 5 read as a 6
    said("1958 年摘要的文字层漏了第 2 段的第一行，又把其中的 4500 读作“4600”", F["i8_date"][0], 2, F["i8_resolution"][1],
         misread8)
    D = terms()
    fall = 100 - D.set_index("period")["ratio"]["1936-1938"]
    r = D.set_index("period")["ratio"]
    mean30 = (r["1931-1935"] + r["1936-1938"]) / 2                                # the two periods of the 1930's
    assert round(mean30) == F["pb_63"][0] and abs(100 * (100 / mean30 - 1) - F["pb_63"][3]) < 0.05
    said("普雷维什第 8 页说 1930 年代只能买到 1860 年代的 63\\%，表 1 却从 1876—1880 年算起", page("pb_63"), 1930, 1860,
         F["pb_63"][0], 1, 1876, 1880)
    said("表里 1931—1935 年与 1936—1938 年这两期的平均是 63.05，与第 8 页的 63\\% 和 58.6\\% 都相合", 1931, 1935, 1936, 1938, mean30,
         page("pb_63"), F["pb_63"][0], F["pb_63"][3])
    said("1936—1938 年一期的 64.1 对应的却是下降 35.9\\%", 1936, 1938, 100 - fall, fall)
    assert min(abs(100 - mean30 - F["pb_365"][0]), abs(fall - F["pb_365"][0])) > 0.3
    said("第 12 页说从 1870 年代到 1930 年代恶化 36.5\\%，与这几个数都不完全一致", page("pb_365"), 1870, 1930, F["pb_365"][0])
    say("他用的是哪种比较，文中没有说（本书的计算）")
    has("ea_fn6", "W.A. Lewis 1954,p. 139")
    has("ea_lewisquote", "the central fact of economic development is rapid capital accumulation")
    has("lw_rapid", "the central fact of economic development is rapid capital accumulation")
    assert page("lw_classical") == F["ea_fn6"][1] == 139                           # the first page of the article
    said("注的是文章首页第 139 页，这句话在第 155 页", F["ea_fn6"][1], page("lw_rapid"))
    yd, md, dd = F["loc_rostow_d"]
    yg, mg, dg = F["gnd_rostow_d"]
    assert yd == yg and md == mg and dd - dg == 1
    said("国会图书馆罗斯托的记录写他 2003 年 2 月 14 日去世，GND 写 13 日，年份相同，正文只写年份", yd, md, dd, dg)
    assert "loc_rr" not in F and Q["loc_rr"] == "Rosenstein-Rodan, P. N."
    say("罗森斯坦—罗丹的生卒年只见于 GND")


def legacy(F, Y, Q):
    has("lb_demographic", "a phase in the demographic cycle")
    mita = there("ch14_africa", "1573—1812 年，秘鲁与玻利维亚实行")
    assert 190 <= 2010 - mita[1] < 200                                            # Dell (2010): nearly two centuries
    said("米塔制是 1573—1812 年西班牙人在秘鲁与玻利维亚推行的强迫采矿劳役", *mita)
    say("收购价与出口税由谁定，决定了农民能拿到世界价格的多少（本书的解读）")
    assert their("africa_money_facts", "dell_25", "around 25%") == ["25"]
    assert their("africa_money_facts", "dell_6", "around 6 percentage points") == ["6"]
    their("africa_money_facts", "dell_channels", "land tenure and public goods provision")
    said("受影响地区的家庭消费仍低约 25\\%，儿童发育迟缓的比例高约 6 个百分点", 25, 6)
    (y40,) = F["ea_answer"]
    has("ea_ghost", "The Harrod-Domar growth model supposedly died long ago.")
    has("ea_answer", "the 40 years of data that have accumulated during its use")
    said("这个模型活下来，靠的是它与 40 年的数据相符吗？", y40)


def takeaways(F, Y, Q):
    said("刘易斯（1954）把经济分成资本主义部门与维持生计的部门。工资定在维持生计的收入之上约 30\\%", F["lw_issue"][0],
         F["lw_gap"][0])
    D = terms().set_index("period")["ratio"]
    said("普雷维什（1950）用英国的进出口价格说明，初级产品与工业品的价格之比从 1876—1880 年到 1936—1938 年降了约三分之一",
         F["pb_date"][1], 1876, 1880, 1936, 1938)
    assert abs((100 - D["1936-1938"]) / 100 - told("降了约三分之一", "约", "")) < 0.03
    say("剩余劳动、贸易条件、进口替代与大推进四个问题，至今没有定论")


def selfcheck(F, Y, Q):
    said("按\\exref{ex:development-lewis}的教学输入，资本主义部门雇 16 人时，全社会的储蓄率是多少？", SC_LC)
    tf, a, tm = SC_ERP
    said("一种产品的名义关税 30\\%，投入品按世界价格占产品价格的一半，投入品免税，有效保护率是多少？投入品征 30\\% 呢？",
         100 * tf, 100 * tm)
    assert told("投入品按世界价格占产品价格的一半", "价格的", "") == a
    said("$L=100$，$\\theta=1.5$，$v=0.2$，$F=15$ 时", PUSH_L, PUSH_A, PUSH_V, SC_F)
    icor, g, s = SC_GAP
    said("某国的 ICOR 为 3，目标增长率 6\\%，国内储蓄率 12\\%", icor, 100 * g, 100 * s)
    e = lewis(SC_LC)
    said("$Y_c=31.2$，利润$10.4$，$Y=31.2+84=115.2$，储蓄率约 9.0\\%", e["yc"], e["profit"], e["yc"], LAB - SC_LC, e["y"],
         100 * e["s"])
    said("$(0.3-0)/0.5=60\\%$；$(0.3-0.5\\times0.3)/0.5=30\\%$，与名义关税相同", tf, 0, 1 - a, 100 * erp(tf, a, 0), tf, a, tm,
         1 - a, 100 * erp(tf, a, tm))
    lo, _ = f_range(PUSH_L, PUSH_A, PUSH_V)
    alone = PUSH_L * (1 - (1 + PUSH_V) / PUSH_A)
    said("$20<1.2\\times15=18$不成立", alone, 1 + PUSH_V, SC_F, (1 + PUSH_V) * SC_F)
    assert profit_alone(PUSH_L, PUSH_A, PUSH_V, SC_F) > 0 and profit_all(PUSH_L, PUSH_A, PUSH_V, SC_F) > 0 and SC_F < lo
    said("$3\\times6\\%=18\\%$，缺口$18\\%-12\\%=6\\%$", icor, 100 * g, 100 * icor * g, 100 * icor * g, 100 * s,
         100 * (icor * g - s))


def ending(F, Y, Q):
    said("回到 1952 年 8 月曼谷的那条路", F["lb_bangkok"][0], mon("lb_bangkok", "August"))
    said("1957 年起，他做过加纳总理的联合国经济顾问", F["lb_ghana"][1])
    said("到 1979 年，他说许多国家曾经向内，主要靠进口替代，后来几乎每个国家都发现了出口的“好处”", F["ll_title"][1])
    say("下一章讲的是最早转向出口的那几个经济体。")
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 42's question"
    assert t.index("\\end{answers}") < t.index("回到 1952 年 8 月曼谷的那条路")
    stub = (ROOT / "zh" / "ch42_eastasia.tex").read_text(encoding="utf-8")
    assert f"\\guidequestion{{{NEXT}}}" in stub


# ---------------------------------------------------------------------------------------------------
# 5. The models
def models() -> None:
    """The key equations as printed, and the claims the text makes of them, checked with random numbers."""
    t = TEX.read_text(encoding="utf-8")
    eqs = {lab: body.strip() for body, lab in re.findall(r"\\begin\{keyeq\}\n(.*?)\\label\{(eq:[^}]+)\}", t, re.DOTALL)}
    assert eqs == {
        "eq:development-lewis": ("(1-\\alpha)\\,A\\,K^{\\alpha}L_c^{-\\alpha}=\\bar w ,\\qquad \\Pi=Y_c-\\bar w L_c=\\alpha\\,Y_c ,"
                                 "\\qquad \\frac{S}{Y}=\\frac{\\alpha\\,Y_c}{Y_c+Y_s} ."),
        "eq:development-erp": "\\text{ERP}=\\frac{V'-V}{V}=\\frac{t_f-a\\,t_m}{1-a} ,",
        "eq:development-push": ("L\\Bigl(1-\\frac{1+v}{\\theta}\\Bigr)-F\\,(1+v)<0 ,\\qquad \\theta\\,(L-F)-L\\,(1+v)>0 ."),
        "eq:development-gap": "\\frac{I}{Y}=\\text{ICOR}\\times g ,\\qquad \\text{缺口}=\\frac{I}{Y}-\\frac{S}{Y} .",
    }, eqs
    assert "\\begin{equation}" not in t
    # the transcriptions of Murphy, Shleifer and Vishny the text renders (their alpha is the text's a)
    assert "π = y(1 − (1+v)/α) − F(1+v)" in transcription("ms_profit") and "w = 1 + v" in transcription("ms_wage")
    assert "α − 1 > v" in transcription("ms_eq8")
    rng = np.random.default_rng(41)
    for _ in range(300):
        al, A, K, w = rng.uniform(0.15, 0.6), rng.uniform(0.5, 2), rng.uniform(1, 50), rng.uniform(0.5, 2)
        # the first equation: the employment at which the marginal product is the wage; it is proportional to K
        lc = ((1 - al) * A / w) ** (1 / al) * K
        assert np.isclose((1 - al) * A * K ** al * lc ** (-al), w)
        assert np.isclose(((1 - al) * A / w) ** (1 / al) * 2 * K, 2 * lc)
        yc = A * K ** al * lc ** (1 - al)
        assert np.isclose(yc - w * lc, al * yc)                                   # the second: the profit is alpha Y_c
        # the third: with the wage fixed, the saving rate rises with the capitalist sector (from the example's wage)
        ys = rng.uniform(10, 100)
        assert al * yc / (yc + ys) < al * (1.1 * yc) / (1.1 * yc + ys - 0.1 * ys * rng.uniform(0, 1))
    S = [lewis(lc)["s"] for lc in np.linspace(LC0, LCMAX, 50)]
    assert all(np.diff(S) > 0) and S[-1] < ALPHA
    assert np.isclose(lewis(LC0)["profit"] / KY / capital_for(LC0) * capital_for(LC0), growth_rate() * lewis(LC0)["yc"])
    # eq:development-erp: the rate of the definition, from the value added at world and domestic prices
    for _ in range(300):
        a, tf, tm = rng.uniform(0.05, 0.9), rng.uniform(0, 1), rng.uniform(0, 1)
        v, v2 = 1 - a, (1 + tf) - a * (1 + tm)
        assert np.isclose((v2 - v) / v, erp(tf, a, tm))
        assert erp(tf, a, max(tm - 0.05, 0)) >= erp(tf, a, tm)                     # a lower duty on the inputs: more
        if tf > tm:
            assert erp(tf, min(a + 0.05, 0.95), tm) > erp(tf, a, tm)               # a smaller value added: more
            assert erp(tf, a, tm) > tf                                             # above the nominal tariff
    assert np.isclose(erp(SC_ERP[0], SC_ERP[1], SC_ERP[2]), SC_ERP[0])            # the same duty on all: the tariff
    # eq:development-push from MSV (7): the profit of a factory with income y, at y = L (no factory) and at
    # y = a (L - F) (every sector with a factory)
    for _ in range(300):
        L, a, v, F = rng.uniform(50, 200), rng.uniform(1.05, 3), rng.uniform(0, 1), rng.uniform(0, 60)
        pi = lambda y: y * (1 - (1 + v) / a) - F * (1 + v)                        # noqa: E731
        assert np.isclose(pi(L), profit_alone(L, a, v, F)) and np.isclose(pi(a * (L - F)), profit_all(L, a, v, F))
        lo, hi = f_range(L, a, v)
        both = profit_alone(L, a, v, F) < 0 < profit_all(L, a, v, F)
        assert both == (lo < F < hi)
        if a - 1 <= v:
            assert not both                                                        # no factory pays without a - 1 > v
    # eq:development-gap: Harrod-Domar, and the ICOR of a Cobb-Douglas economy rises with the capital
    for _ in range(100):
        icor, g, s = rng.uniform(2, 9), rng.uniform(0.01, 0.08), rng.uniform(0.02, 0.3)
        assert np.isclose(icor * g - s, icor * g - s) and np.isclose((icor * g) / icor, g)
    al = 1 / 3
    icors = [1 / (al * k ** (al - 1)) for k in (1, 2, 4, 8)]
    assert all(np.diff(icors) > 0)
    print("ok the key equations as printed; the Lewis economy, the effective rate of protection, the two equilibria "
          "and the financing gap on random numbers")


def figures_data() -> None:
    """What the figures assert of their data."""
    P = lewis_path()
    assert np.isclose(P["lc"].iloc[0], LC0) and np.isclose(P["lc"].iloc[-1], LCMAX)
    assert np.isclose(P["year"].iloc[-1], turning_year()) and all(np.diff(P["s"]) >= -1e-12)
    D = lewis_diagram()
    for lc in (LC0, 2 * LC0, LCMAX):                                               # each curve meets the wage at lc
        k = int(np.argmin(abs(D["L"] - lc)))
        assert abs(D[f"mpl{lc}"].iloc[k] - WBAR) < 0.05, lc
        assert (D[f"mpl{lc}"].diff().iloc[1:] < 0).all()
    T = terms()
    assert len(T) == 13 and T["mid"].is_monotonic_increasing
    gap = T[(T["first"] > 1912) & (T["last"] < 1922)]
    assert gap.empty                                                               # the years of the First War: none
    Pm = paths()
    assert set(NAMES_ZH) == set(Pm.columns) and Pm.index.min() == 1950 and Pm.index.max() == 2022
    assert not Pm.isna().any().any()


# ---------------------------------------------------------------------------------------------------
# 6. The book
# the life dates: words -> (row of the birth year, index), (row of the death year, index), row of the heading, heading
LIVES = {"Theodore W. Schultz，1902—1998": (("loc_schultz", 0), ("loc_schultz", 1), "loc_schultz", "Schultz, Theodore W."),
         "W. W. Rostow，1916—2003": (("loc_rostow", 0), ("loc_rostow", 1), "loc_rostow", "Rostow, W. W."),
         "Paul N. Rosenstein-Rodan，1902—1985": (("gnd_rr_born", 0), ("gnd_rr", 0), "loc_rr", "Rosenstein-Rodan, P. N."),
         "P. C. Mahalanobis，1893—1972": (("loc_mahalanobis", 0), ("loc_mahalanobis", 1), "loc_mahalanobis",
                                          "Mahalanobis, P. C."),
         "Kwame Nkrumah，1909—1972": (("loc_nkrumah", 0), ("loc_nkrumah", 1), "loc_nkrumah", "Nkrumah, Kwame")}
# the life dates other chapters' records give: words -> ((snapshot, row, index) of the birth year, of the death year)
THEIR_LIVES = {"W. Arthur Lewis，1915—1991": (("solow_facts", "loc_lewis", 0), ("solow_facts", "loc_lewis", 1)),
               "Raúl Prebisch，1901—1986": (("depressionworld_facts", "bnf_prebisch", 0),
                                           ("depressionworld_facts", "bnf_prebisch", 1))}
# where two records have a date, they agree: (row, index) pairs
AGREE = [(("gnd_schultz", 0), ("loc_schultz", 0)), (("gnd_schultz_d", 0), ("loc_schultz", 1)),
         (("gnd_rostow", 0), ("loc_rostow", 0)), (("gnd_rostow_d", 0), ("loc_rostow", 1)),
         (("loc_rostow_d", 0), ("loc_rostow", 1)),
         (("gnd_mahalanobis_born", 0), ("loc_mahalanobis", 0)), (("gnd_mahalanobis_died", 0), ("loc_mahalanobis", 1)),
         (("gnd_nkrumah", 0), ("loc_nkrumah", 0)), (("gnd_nkrumah_d", 0), ("loc_nkrumah", 1)),
         (("loc_nkrumah_pm", 0), ("loc_nkrumah_pm", 2)), (("loc_nkrumah_pm", 0), ("lb_ghana", 1)),
         (("ll_title", 0), ("sc_title", 0)), (("ll_title", 1), ("sc_title", 1))]
# what other chapters tell: (words of this chapter, chapter where it is told, words there)
EVENTS = [("按 Maddison 的估计，殖民统治把印度四分之一左右的储蓄转出了国（\\chref{ch:periphery}）", "ch24_periphery",
           "Maddison 估计，殖民统治把印度四分之一左右的储蓄转出了国"),
          ("他在\\chref{ch:depressionworld}里做过阿根廷中央银行的总经理", "ch29_depressionworld",
           "1935—1943 年，普雷维什（Raúl Prebisch，1901—1986）任总经理"),
          ("阿根廷等国因此在 1930 年代走上保护性的进口替代（\\chref{ch:depressionworld}）", "ch29_depressionworld",
           "1930 年代工业扩张强劲的拉丁美洲国家"),
          ("苏联工业化的代价与那场饥荒在\\chref{ch:soviet}", "ch31_soviet", "并如实记录集体化与饥荒的代价"),
          ("那里引的研究没有找到支持大推进理论的证据\\cite{cggt2013}", "ch31_soviet", "没有找到支持大推进理论的证据"),
          ("这是\\chref{ch:divergence}末尾反过来问的 Allen 的问题", "ch21_divergence",
           "Allen 的问题也可以反过来问：工资低的国家为什么要用发达国家为高工资设计的技术？"),
          ("米塔制结束将近两百年后", "ch14_africa", "米塔制结束将近两百年后"),
          ("米塔制是 1573—1812 年西班牙人在秘鲁与玻利维亚推行的强迫采矿劳役（\\chref{ch:africa}）", "ch14_africa",
           "1573—1812 年，秘鲁与玻利维亚实行“一种大规模的强迫采矿劳役制度”，即米塔制（mita）"),
          ("上一章的检验里，1960 年最穷的四分之一共 27 个国家", "ch40_solow",
           "同一组的 27 个国家却有 13 个增长得比最富的四分之一的平均速度慢"),
          ("刘易斯（W. Arthur Lewis，1915—1991）", "ch40_solow", "刘易斯（W. Arthur Lewis，1915—1991）"),
          ("又怎样在 1982 年收场，在\\chref{ch:latamdebt}", "ch51_latamdebt", "1982 年墨西哥危机"),
          ("成熟的计划经济与中国的大跃进及其饥荒在\\chref{ch:planned}", "ch43_planned", "大跃进，并如实记录 1959—1961 年饥荒"),
          ("这个模型在\\chref{ch:solow}", "ch40_solow", "哈罗德（Roy Harrod，1900—1978）与多马（Evsey D. Domar，1914—1997）"),
          ("东亚的证据在\\chref{ch:eastasia}", "ch42_eastasia", NEXT)]
# the chapters this one hands on to, and those it draws on
LATER = {"ch:solow": "ch40_solow", "ch:periphery": "ch24_periphery", "ch:depressionworld": "ch29_depressionworld",
         "ch:soviet": "ch31_soviet", "ch:hyperinflation": "ch52_hyperinflation", "ch:eastasia": "ch42_eastasia",
         "ch:divergence": "ch21_divergence", "ch:latamdebt": "ch51_latamdebt", "ch:demography": "ch79_demography",
         "ch:africa": "ch14_africa", "ch:endogenous": "ch56_endogenous", "ch:heterogeneity": "ch71_heterogeneity",
         "ch:fragmentation": "ch78_fragmentation", "ch:emcrises": "ch61_emcrises", "ch:planned": "ch43_planned"}
# the chapters that point here
POINTERS = ("ch14_africa", "ch21_divergence", "ch24_periphery", "ch40_solow", "ch42_eastasia")


def book(F, Q):
    """Life dates and what other chapters tell."""
    t = tex_text()
    for words, ((rb, ib), (rd, id_), head_row, head) in LIVES.items():
        assert words in t, words
        assert f"{F[rb][ib]:.0f}—{F[rd][id_]:.0f}" in words, (words, rb, rd)
        assert Q[head_row].startswith(head), (head_row, Q[head_row])             # the person of the record
        COVERED.append(words)
    for words, ((nb, rb, ib), (nd, rd, id_)) in THEIR_LIVES.items():
        assert words in t, words
        assert f"{float(their(nb, rb)[ib]):.0f}—{float(their(nd, rd)[id_]):.0f}" in words, words
        COVERED.append(words)
    assert float(their("solow_facts", "loc_lewis")[0]) == F["lb_born"][1]
    assert float(their("solow_facts", "loc_lewis")[1]) == F["lb_died"][1] == years()["lb_died"]
    assert mon("lb_died", "June") == 6 and mon("lb_born", "January") == 1
    for (r1, i1), (r2, i2) in AGREE:
        assert F[r1][i1] == F[r2][i2], (r1, r2)
    assert "gnd_mahalanobis" not in F and Q["gnd_mahalanobis"] == "Mahalanobis, Prasanta C."
    assert mon("loc_nkrumah_pm", "Mar.") == 3 and Q["loc_nkrumah_pm"].startswith("headed Ghana")
    for here, ch, there_ in EVENTS:
        assert here in t, here
        assert there_ in chapter(ch), (ch, there_)
    named = set(re.findall(r"\\chref\{(ch:[^}]+)\}", t))
    assert named == set(LATER), sorted(named ^ set(LATER))
    for label, ch in LATER.items():
        assert f"\\label{{{label}}}" in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (label, ch)
    for ch in POINTERS:
        assert re.search(r"\\(?:chref|ref)\{ch:development\}", chapter(ch)), ch
    assert "\\figref{fig:solow_convergence}" in t and "}{fig:solow_convergence}" in chapter("ch40_solow")
    print(f"ok {len(LIVES) + len(THEIR_LIVES)} life dates, {len(EVENTS)} statements of other chapters, {len(LATER)} "
          f"other chapters named")


# the bibliography item of each source of the snapshot (the authority records: loc41 and gnd41)
ITEM_OF = {"lewis1954ms41": "lewis1954", "lewisbio41": "lewisbio1979", "lewis1979_41": "lewis1979",
           "nobelfacts41": "nobel1979", "schultz1979_41": "schultz1979", "prebisch41": "prebisch1950",
           "prebisch41img": "prebisch1950", "untou41": "prebisch1950", "uncopyright41": "prebisch1950",
           "wdr1987_41": "wdr1987", "wdr1987_41img": "wdr1987", "easterly41": "easterly1997",
           "easterly41img": "easterly1997", "msv41": "msv1988", "msv41img": "msv1988", "india1956_41": "india1956",
           "india1958_41": "india1958", "india1958img41": "india1958", "india1961_41": "india1961", "india1961img41": "india1961",
           "indialaw41": "india1956", "ghana1963_41": "ghana1963", "ghanalaw41": "ghana1963",
           "wbcocoa41": "wbcocoa1970", "wbcocoa41img": "wbcocoa1970", "wbstab41": "wbstab1967"}


def runs(ps) -> str:
    """'第 2、7、8、25、26 页' from page numbers: ranges joined by '—', two neighbours by '、'."""
    out, rs = [], []
    for p in sorted(set(ps)):
        if rs and p == rs[-1][1] + 1:
            rs[-1][1] = p
        else:
            rs.append([p, p])
    for a, b in rs:
        out.append(f"{a}" if a == b else f"{a}{'、' if b == a + 1 else '—'}{b}")
    return "第 " + "、".join(out) + " 页"


def printed(srcs) -> str:
    """The printed pages of the rows of these sources (their juan columns begin 'p. N')."""
    return runs(int(m.group(1)) for r in _rows().itertuples() if r.file in srcs
                for m in [re.match(r"pp?\. (\d+)\b", r.juan)] if m)


def pdf(srcs) -> str:
    """The PDF pages of the rows of these sources."""
    return "PDF " + runs(int(p) for r in _rows().itertuples() if r.file in srcs
                         for p in re.findall(r"PDF pp?\. (\d+)", r.juan))


def witnesses(F, Q):
    """Second witnesses of statements of the text, the licences and the bibliography block of the chapter."""
    # Lewis's 12 per cent in Easterly; his professorship and the year of his article in the autobiography
    assert F["ea_gap12"][0] == F["lw_central"][2] and F["lb_applause"][0] == F["lw_issue"][0]
    assert F["nf_share"] == [0.5] and Y_of("nf_share") == F["ll_title"][1] == F["sc_title"][1]
    # the licences
    m = meta()
    lic = m["license"]
    for rid in ("lb_copyright", "ll_copyright", "sc_copyright", "pb_symbol", "un_terms", "un_copyright", "wd_copyright",
                "wd_rights", "ea_series", "wc_rights", "wc_rights2", "ws_rights", "ms_opinions", "il_title", "il_q3",
                "gl_act", "gl_s3", "gl_s8", "gl_s19", "gl_fair", "gnd_licence"):
        assert re.search(r"\brows? [^)]*\b" + rid + r"\b", lic), rid
    for rid in ("un_terms", "wd_rights", "ea_series", "ws_rights", "ms_opinions", "il_q3", "gnd_licence"):
        assert words_of(rid) in lic, rid
    for rid in ("lb_copyright", "ll_copyright", "sc_copyright"):
        assert words_of(rid) == "Copyright © The Nobel Foundation 1979", rid
    for words in ("Short phrases only", "not committed", "prints no © notice", "public data", "prints no copyright notice",
                  "'Copyright © The Nobel Foundation 1979'"):
        assert words in lic, words
    data = load_snapshot("maddison2023_development")[1]
    assert "CC BY 4.0" in data["license"] and "CONDITIONS UNDER WHICH ALL ORIGINAL PAPERS MUST BE CITED" in data["license"]
    # the bibliography block of the chapter
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    start = bib.index("% ---- 第 41 章")
    following = re.search(r"^% ---- 第 \d+ 章", bib[start + 1:], re.MULTILINE)
    end = start + 1 + following.start() if following else bib.index("\\end{thebibliography}")
    block = bib[start:end]
    assert FETCH in block and bib.index("% ---- 第 40 章") < start
    items = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", block)}
    allitems = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", bib)}
    assert f"共 {len(items)} 条" in block
    unescape = lambda s: re.sub(r"\\([$%&_#])", r"\1", s).replace("--", "-")     # noqa: E731 - as LaTeX prints it
    for key in ("lewisbio1979", "lewis1979", "schultz1979"):
        assert "Copyright © The Nobel Foundation 1979" in items[key], key
    assert "© 1987 by the International Bank for Reconstruction and Development / The World Bank" in items["wdr1987"]
    assert words_of("wd_rights") in unescape(items["wdr1987"])
    assert words_of("ea_series") in unescape(items["easterly1997"])
    for key in ("wbcocoa1970", "wbstab1967"):
        assert words_of("ws_rights") in unescape(items[key]), key
    assert words_of("wc_rights") in unescape(items["wbcocoa1970"]) and words_of("wc_rights2") in unescape(items["wbcocoa1970"])
    assert words_of("ms_opinions") in unescape(items["msv1988"]) and "没有印版权声明" in items["msv1988"]
    assert words_of("un_terms") in unescape(items["prebisch1950"]) and "没有印版权声明" in items["prebisch1950"]
    assert words_of("un_copyright") in unescape(items["prebisch1950"])
    for key in ("india1956", "india1958", "india1961"):
        assert "52(1)(q)(iii)" in items[key], key
    assert words_of("il_q3") in unescape(items["india1956"])
    assert "Act 690" in items["ghana1963"] and words_of("gl_s8") in unescape(items["ghana1963"])
    for key in ("lewis1954", "prebisch1950"):
        assert "只用来核对，不随本书分发" in items[key], key
        sha = m["sources"][{"lewis1954": "lewis1954ms41", "prebisch1950": "prebisch41"}[key]]["sha256"]
        assert sha in items[key], key
    assert "公共数据" in items["loc41"] and words_of("gnd_licence") in unescape(items["gnd41"])
    # the titles of the documents, as their title pages and covers print them
    for rid, key in (("lw_title", "lewis1954"), ("ms_title", "msv1988"), ("in_title", "india1956"),
                     ("wc_report", "wbcocoa1970"), ("gh_title", "ghana1963")):
        norm = lambda x: re.sub(r"[^a-z]", "", x.lower())                     # noqa: E731
        assert norm(words_of(rid).split(" 19")[0]) in norm(unescape(items[key])), (rid, key)
    assert "'STABILIZATION AND DEVELOPMENT IN GHANA'" in column("note")["ws_date"]
    assert "Stabilization and Development in Ghana" in items["wbstab1967"]
    assert f"{words_of('ws_number')}, March 14, 1967" in items["wbstab1967"]
    assert F["ws_date"] == [14, 1967] and mon("ws_date", "March") == 3
    assert f"{words_of('wc_number')}, June 3, 1970" in items["wbcocoa1970"] and F["wc_date"] == [3, 1970]
    assert f"Working Paper {F['ea_number'][0]:.0f}" in items["easterly1997"] and mon("ea_date", "August") == 8
    assert f"Working Paper {F['ms_number'][0]:.0f}, September 1988" in items["msv1988"]
    for words, (_, _, head_row, _) in LIVES.items():
        assert Q[head_row].replace("-", "--") in items["loc41"] or Q[head_row] in items["loc41"], head_row
    for rid in ("gnd_schultz", "gnd_schultz_d", "gnd_rostow", "gnd_rostow_d", "gnd_rr", "gnd_nkrumah", "gnd_nkrumah_d"):
        assert Q[rid] in items["gnd41"], rid
    assert Q["gnd_mahalanobis"] in items["gnd41"]
    # the pages of each work, as the snapshot's rows have them
    for key, srcs in (("lewis1954", ("lewis1954ms41",)), ("prebisch1950", ("prebisch41", "prebisch41img")),
                      ("wdr1987", ("wdr1987_41", "wdr1987_41img")), ("msv1988", ("msv41", "msv41img")),
                      ("wbcocoa1970", ("wbcocoa41", "wbcocoa41img"))):
        assert printed(srcs) in items[key] and pdf(srcs) in items[key], (key, printed(srcs), pdf(srcs))
    for key, srcs in (("easterly1997", ("easterly41", "easterly41img")), ("wbstab1967", ("wbstab41",))):
        assert pdf(srcs) in items[key], (key, pdf(srcs))
    for key, srcs in (("india1956", ("india1956_41",)), ("india1961", ("india1961_41", "india1961img41")),
                      ("ghana1963", ("ghana1963_41",))):
        assert printed(srcs) in items[key], (key, printed(srcs))
    # every source of the snapshot, and the workbook of the data snapshot, is named by its URL in its item
    for key, s in m["sources"].items():
        item = "loc41" if key.startswith("loc_") else "gnd41" if key.startswith("gnd_") else ITEM_OF[key]
        assert unescape(s["url"]) in unescape(items[item]), key
    assert data["url"] in items["mpd41src"] and "data/fetch/maddison2023\\_development41.py" in items["mpd41src"]
    for code, srcs in data["sources_by_country"].items():
        for s in srcs:
            assert unescape(s.replace("--", "-")) in unescape(items["mpd41src"]), code
    assert data["sources_all"][0] in unescape(items["mpd41src"])
    keys = set(allitems)
    cited = {k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", tex_text()) for k in c.split(",")}
    assert cited <= keys, sorted(cited - keys)
    assert REUSED_KEYS <= cited and not REUSED_KEYS & set(items)
    assert set(items) == cited - REUSED_KEYS, sorted(set(items) ^ (cited - REUSED_KEYS))
    print(f"ok {len(cited)} works cited, {len(items)} in the bibliography block of Chapter 41, "
          f"{len(REUSED_KEYS)} in earlier blocks")


def Y_of(rid: str) -> int:
    return years()[rid]


# the modern authors cited in Latin script
NAMES = "Easterly|Murphy|Shleifer|Vishny|Chenery|Strout|Kamarck|Krueger|Little|Scitovsky|Scott|Dell|Maddison|Allen|Bolt"


def counts() -> None:
    """The editor's limits: “不能” at most about a dozen; no cited modern author in Latin script as the subject of a
    sentence outside the 史料说明; the forbidden words; who decided and who paid stated; the four debates left open."""
    t = tex_text()
    main = re.sub(r"\\begin\{deeper\}\[史料说明\].*?\\end\{deeper\}", "", t, flags=re.DOTALL)
    n = t.count("不能")
    print(f"ok “不能” {n} times")
    assert n <= 12, n
    verbs = ("认为|写道|说|指出|记述|估计|承认|报道|记载|提到|列出|给出|发现|统计|算出|早有|看法|有类似|怀疑|强调|写作|推测|"
             "提出|回答|回应|证明|检验|研究|分析|预测|引")
    subj = re.findall(r"(?:^|[。；：，）\n])\s*(?:据 )?(?:" + NAMES + r")(?:\s*[、与和]\s*(?:" + NAMES +
                      r"))*(?: 等人| 等)?(?:（\d{4}）)?\s*(?:也|还|又|则)?(?:" + verbs + ")", main)
    assert not subj, subj
    for words in ("本书没有找到", "没能取得", "没有取得", "没有读到"):
        assert words not in main, words                                          # only in the 史料说明
    narrative = re.sub(r"“[^”]*”", "", t)
    for bad in ("这一节回答", "不是因为", "而是", "详见", "\\textsc", "\\underline", "\\clearpage"):
        assert bad not in narrative, bad
    assert not re.search(r"(?<![意看])见\\(?:chref|secref|figref|tabref|exref|eqref)", t)
    assert "\\chapterstub" not in t
    # the coordinator's names of economies
    for bad in ("中国台湾", "中国香港"):
        assert bad not in t, bad
    # the political character: who decided and who paid
    for words in ("关税与许可由政府定，账由谁付", "这有时有巨大的政治意义",
                  "按这个图式，拉丁美洲作为世界经济体系的外围", "原因是国内政治通常偏向城市人口，牺牲人数多得多的农村人口",
                  "计划委员会知道这条路的代价", "消费上作出一定的牺牲不可避免", "代价由眼前的消费与没被吸收的人力承担",
                  "付账的是种可可的农民", "这笔钱和后来积累的资金都被政府用于可可以外的用途",
                  "按世界价格卖可可的是国家，决定差价用在哪里的也是国家，少收的是农民",
                  "决定投资率与优先次序的是计划委员会与政府，付账的是消费者与种可可的农民",
                  "\\section{印度与加纳：谁决定，谁承担}", "直到 1966 年被政变推翻", "苏联工业化的代价与那场饥荒",
                  "中国的大跃进及其饥荒"):
        assert words in main, words
    # documents are not the subjects of sentences: the author is named (part6_notes, editor's round on Chapter 38)
    for bad in ("报告说", "报告还", "报告把", "报告承认", "同一份报告", "大纲说", "大纲要", "摘要说", "演讲说", "第三个计划说"):
        assert bad not in main, bad
    # at most one source frame (按……的说法、转述……) in a sentence
    frame = re.compile(r"按[^，。；“”]{0,40}?的(?:说法|转述|解释|估计|检验|算法|回顾|分类|数字|自述|定义|项目报告|报告|摘要|"
                       r"草案大纲|工作论文|模型)")
    for s in re.split(r"(?<=[。？！])|\n", re.sub(r"“[^”]*”", "“”", main)):
        assert len(frame.findall(s)) <= 1, s
    # Ghana's one-party state and the Preventive Detention Act: no source read
    for words in ("一党", "预防性拘留", "Preventive Detention"):
        assert words not in t, words
    # the four debates are left open
    for words in ("第一个争论", "第二个争论", "第三个争论", "第四个争论"):
        assert main.count(words) == 1, words
    part = main[main.index("\\section{四个争论}"):main.index("\\section{今天还剩什么}")]
    debates = part.split("\\subsubsection{")[1:]
    assert len(debates) == 4
    for d in debates:
        assert d.rstrip().endswith("至今没有定论。"), d[-80:]
    # the inferences are marked
    assert main.count("本书的解读") >= 8 and "本书的计算" in main and "本书的概括" in main, main.count("本书的解读")
    # sentences: one semicolon at most
    for s in re.split(r"(?<=[。？！])|\n", re.sub(r"“[^”]*”", "“”", main)):
        assert s.count("；") <= 1, s
    # the boxes the editor asks for
    assert 2 <= t.count("\\begin{compare}") <= 4 and t.count("\\begin{case}") == 1 and t.count("\\begin{pitfall}") == 1
    assert t.count("\\begin{deeper}[史料说明]") == 1 and 1 <= t.count("\\begin{keyeq}") <= 4
    assert t.count(GUIDE) == 2


def main() -> None:
    df = _rows()
    F, Y, Q = facts(), years(), quotes()
    check_readings(df)
    check_text(df)
    for part in (guide, opening, world, lewis_model, isi, push, cases, data_check, debate, deeper, legacy, takeaways,
                 selfcheck, ending):
        part(F, Y, Q)
    models()
    figures_data()
    book(F, Q)
    witnesses(F, Q)
    counts()
    coverage()
    others = {rid for rids in OTHER_ROWS.values() for rid in rids}
    for name, rids in OTHER_ROWS.items():
        ids = set(load_snapshot(name, dtype=str, keep_default_na=False)[0]["id"])
        assert set(rids) <= ids, name
    anchors(str(TEX), set(df["id"]) | others, script=Path(__file__))


if __name__ == "__main__":
    main()
