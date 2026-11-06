"""Chapter 40 (索洛增长模型): every number and every quotation in zh/ch40_solow.tex.

    python3 checks/check_ch40.py

Inputs:
  solow_facts                   quotations of the chapter's sources with their page: Solow's Nobel lecture of 1987 and
                                the Nobel page of the prize; Harrod (1939), Solow (1956, 1957), Phelps (1961) and
                                Baumol (1986), the JSTOR copies on Thomas Piketty's page at the Paris School of
                                Economics, the equations and tables of Harrod, Solow (1956) and Solow (1957) read on
                                the page images; Swan (1956) and the index of Econometrica 14 (1946), the microfilm
                                scans on archive.org; Abramovitz (1956, NBER); the NBER working papers of De Long
                                (1987), Barro (1989), Barro and Sala-i-Martin (1990) and Mankiw, Romer and Weil
                                (1990); Pritchett (1995) and Easterly and Fischer (1995), the World Bank's PDFs (the
                                tables of the latter read on the page images); the study of Soviet GNP printed for the
                                Joint Economic Committee (1990), the microfiche scan on archive.org; Part II of the
                                Survey of Current Business of May 1972 (Jorgenson and Griliches, Denison); the record of
                                Penn World Table 10.01; the authority records of the Library of Congress and the GND.
                                data/fetch/verify_web_quotes.py checks the quotations against the documents; the rows
                                with an empty quotation are read on page images, with a transcription between « and »
                                in the note; data/fetch/solow40.py fetches the documents
  pwt1001_convergence           Penn World Table 10.01: the countries with data for 1960 and 2019 and an investment
                                share in every year (the convergence tests of tab:solow-convergence and
                                fig:solow_convergence)
  pwt1001_usa                   Penn World Table 10.01: the United States, 1950-2019 (the stylised facts)

This script

1. reads the numbers of every row from its quotation (or from the transcription of a page image) by the rules of
   READINGS and compares them with the value column; the misreadings of the text layers are listed in MISPRINTS;
2. finds every “…” of the text among the renderings of TRANSLATIONS, and the words of the source each one renders
   (KEYWORDS) in the row; the quotations of copyrighted works stay short (FREE names the public-domain rows);
3. checks each number of the text with said(): the phrase is in the text and each number is the value of a row, a
   teaching input, or arithmetic on them (the accumulation equation eq:solow-accumulation, the steady state
   eq:solow-steady, the speed of convergence eq:solow-speed and a year-by-year simulation, the golden rule, growth
   accounting eq:solow-accounting with Solow's Table 1 and Easterly and Fischer's Table 1, the regressions on Penn World
   Table 10.01); every Arabic number of the text must lie in a phrase said() read (coverage());
4. checks the key equations as printed, the model's claims on random numbers, the data of the figures
   (figsrc/fig_ch40.py imports diagram(), transition(), convergence_points() and soviet() from here), the life dates
   against the authority records, what other chapters tell, the licences and the bibliography block of Chapter 40, and
   the editor's limits;
5. lists the rows no "% 据:" anchor of the text names (common.anchors).

Set CH40_TEX to a scratch copy of the chapter to run the checks on it (mutation tests).
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

TEX = Path(os.environ.get("CH40_TEX", ROOT / "zh" / "ch40_solow.tex"))   # a scratch copy for mutation tests
GUIDE = "长期增长为什么不能只靠多储蓄？"
PREV = GUIDE                                        # Chapter 39's NEXT
NEXT = "穷国怎样起飞？"                              # Chapter 41's question (its stub's guide box)
MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"], 1)}
FETCH = "data/fetch/solow40.py"
# works of the bibliography that other chapters' blocks hold and this chapter cites unchanged
REUSED_KEYS = {"loc33", "gnd34", "loc39", "gnd39"}
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
    df, m = load_snapshot("solow_facts", dtype=str, keep_default_na=False)
    assert 40 in m["used_in"] and m["fetch"] == FETCH
    assert df["id"].is_unique
    return df


@lru_cache(maxsize=None)
def meta() -> dict:
    return load_snapshot("solow_facts")[1]


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
    """The first page number of a row's juan column: 'p. 290 (PDF p. 9)' -> 290."""
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
WORDS = {"one-third": 1 / 3, "one-eighth": 1 / 8, "seven-eighths": 7 / 8, "quarter": 1 / 4, "doubling": 2,
         "double": 2, "quadrupled": 4, "tripled": 3, "sixfold": 6,
         "thirtyfive": 35,                       # De Long's 'thirtyfive' (MISPRINTS)
         "eight": 1 / 8}                          # the Nobel page's 'eight' for 'eighth' (MISPRINTS)


def cardinal(s: str) -> float:
    """An English cardinal: 'three', 'nine', 'twenty-two'."""
    return float(sum(SMALL.get(w, 0) + TENS.get(w, 0) for w in s.lower().replace("-", " ").split()))


def figure(s: str) -> float:
    """'1,000', '30.5', '.28', '-0.75', '−0.37'."""
    return float(s.replace(",", "").replace("−", "-"))


VULGAR = {"½": 1 / 2, "¼": 1 / 4, "¾": 3 / 4}


def frac(s: str) -> float:
    """A fraction: '½', '2½', '2¼', '87½', '9/10', '1/2', '-1/2', '2-1/2', '1/1'."""
    s = s.replace("−", "-")
    sign = -1 if s.startswith("-") else 1
    s = s.lstrip("-")
    if s[-1] in VULGAR:
        return sign * ((float(s[:-1]) if s[:-1] else 0.0) + VULGAR[s[-1]])
    whole, _, part = s.rpartition("-")
    n, d = part.split("/")
    return sign * ((float(whole) if whole else 0.0) + int(n) / int(d))


def lfrac(s: str) -> float:
    """A fraction whose 1 the text layer reads as 'l': 'l/3' -> 1/3."""
    return frac(s.replace("l", "1"))


def dot(s: str) -> float:
    """A decimal whose raised point (0·4) the text layer reads as a hyphen: '0-4' -> 0.4, '1-60' -> 1.60."""
    return float(s.replace("-", "."))


ZH_DIGITS = {"〇": 0, "零": 0, "一": 1, "两": 2, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
ZH_UNITS = {"十": 10, "百": 100, "千": 1000, "万": 10 ** 4, "亿": 10 ** 8}


def zh(s: str) -> float:
    """A Chinese numeral: '六', '十五', '三分之二', '一半', '二十多'."""
    if "分之" in s:
        b, a = s.split("分之")
        return zh(a) / zh(b)
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


FIGURES = re.compile(r"\d[\d,]*(?:\.\d+)?|\.\d+")
# on a page image a minus sign is a hyphen or a minus that follows no letter, digit or bracket
IMG_FIGURES = re.compile(r"((?<![\w)])[-−])?(\d[\d,]*(?:\.\d+)?|\.\d+)")
HOW = {"num": figure, "en": cardinal, "word": lambda w: WORDS[w], "frac": frac, "lfrac": lfrac, "dot": dot}
# id -> [(phrase, how)], in order. A phrase 'context|word' is searched as a whole and read from `word`. Rows not
# listed are read with all the figures of the quotation (a page image: of the transcription, with its signs). An empty
# list: the row prints no number of the story (labels of points, equations, page headers, a misreading quoted).
READINGS: dict[str, list[tuple[str, str]]] = {
    # the Nobel lecture and page
    "nb_education": [("|16", "num"), ("about |1/2", "frac")],
    "nb_misc": [("by |nine", "en"), ("of |3.1", "num"), ("under |0.3", "num")],
    "nb_eight": [("some |seven-eighths", "word"), ("remaining |eight", "word")],
    "nb_heldup": [("the |thirty", "en")],
    "nb_quarter": [("a |quarter", "word")],
    "nb_recipe": [("for |doubling", "word"), ("to |double", "word")],
    "nf_share": [("share: |1/1", "frac")],
    # Harrod (1939)
    "hr_numbers": [("if |10", "num"), ("to |4", "num"), ("be |2½", "frac")],
    "hr_save": [],
    # Solow (1956)
    "s56_three": [], "s56_lower": [],
    # Swan (1956)
    "sw_alpha": [("a = |0-4", "dot")],
    "sw_impact": [("only |0-4", "dot"), ("is |8", "num")],
    "sw_m": [("rate of |½", "frac")],
    "sw_m_ocr": [], "sw_cobb": [], "sw_speed": [], "sw_permanent": [], "sw_at1": [],
    "sw_thrift": [("from |5", "num"), ("to |10", "num")],
    # Solow (1957)
    "s57_t1_1909": [("|1909", "num"), ("income |.335", "num"), ("$|.623", "num"), ("$|2.06", "num"),
                    ("A(t) |1.000", "num")],
    "s57_t1_dollars": [("|1939", "num")],
    "s57_first21": [("first |21", "num"), ("about |9/10", "frac"), ("last |19", "num"), ("average |2¼", "frac")],
    "s57_doubled": [("the |40", "num"), ("about |80", "num")],
    "s57_eighth": [("about |one-eighth", "word"), ("remaining |seven-eighths", "word")],
    "s57_fn6": [("period, |1909", "num"), ("–|29", "num"), ("about |one-third", "word")],
    "s57_summary": [("with |87½", "frac"), ("remaining |12½", "frac")],
    "s57_neutral": [], "s57_curvature": [], "s57_eq1a": [], "s57_eq2a": [], "s57_ocr": [],
    # Abramovitz (1956)
    "ab_quadrupled": [("decade |1869", "num"), ("-|78", "num"), ("decade |1944", "num"), ("-|53", "num"),
                      ("approximately |quadrupled", "word"), ("than |tripled", "word")],
    # Baumol (1986), De Long (1987)
    "bm_eq": [("(|1870", "num"), ("-|1979", "num"), ("= |5.25", "num"), ("|-0.75", "num"), ("WorkHr, |1870", "num"),
              ("= |0.88", "num")],
    "bm_72": [("the |72", "num")],
    "dl_22": [('"once-rich |twenty-two', "en")],
    "dl_sd": [("in |1979", "num"), ("only |thirtyfive", "word"), ("its |1870", "num"), ("once-rich |twenty-two", "en"),
              ("as in |1870", "num")],
    "dl_halfvar": [],
    # Barro and Sala-i-Martin (1990), Mankiw, Romer and Weil (1990)
    "bs_states": [("about |2", "num"), ("to |2-1/2", "frac")],
    "bs_alpha1": [("a=|0.8", "num"), ("a=|1.0", "num"), ("life of |27", "num")],
    "mrw_third": [("about |1/3", "frac")],
    "mrw_lambda": [("a-$-|l/3", "lfrac"), ("6-|.06", "num"), ("equal |.02", "num"), ("about |35", "num")],
    "mrw_elasticity": [("of |1/3", "frac"), ("is |-1/2", "frac"), ("is |-2", "num")],
    "mrw_externalities": [],
    # Pritchett (1995), Easterly and Fischer (1995)
    "pr_sixfold": [("between |1870", "num"), ("and |1985", "num"), ("increased |sixfold", "word"),
                   ("between |60", "num"), ("and |100", "num")],
    "ef_t6_eq": [], "ef_entirely": [],
    "ef_t6_sigma": [("(c5) |−0.37", "num")],
    "ef_t6_tfp": [("(c1) |1.09", "num"), ("(c2) |1.10", "num"), ("(c3) |1.16", "num"), ("(c4) |1.09", "num")],
    "ef_doubled": [("between |1950", "num"), ("and |1975", "num")],
    # Jorgenson and Griliches (1967)
    "jg_160": [("from |1-60", "dot"), ("to |0-10", "dot")],
    "jg_1945": [("the |twenty", "en"), ("II, |1945", "num"), ("-|65", "num")],
    # the dataset record and the authority records
    "pwt_licence": [], "gnd_licence": [],
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
MISPRINTS = [("nb_eight", "remaining eight", "'eight' for 'eighth'"),
             ("hr_revolution", "approachindeed", "'approachindeed' for 'approach—indeed'"),
             ("hr_point", "equilibriumpoint", "'equilibriumpoint' without a space"),
             ("s56_three", "ri and r3", "'ri' for 'r1'"),
             ("s56_lower", "ratio ri or", "'ri' for 'r1'"),
             ("sw_alpha", "0-4", "'0-4' for '0·4'"),
             ("sw_impact", "0-4", "'0-4' for '0·4'"),
             ("sw_m_ocr", "rate of 4 per cent", "'4 per cent' for '½ per cent'"),
             ("sw_answers", "anwers", "'anwers' for 'answers'"),
             ("sw_solow", "AContribution", "'AContribution' without a space"),
             ("ph_theorem", "investmenetis", "'investmenetis' for 'investment is'"),
             ("ph_crowd", "dispersed,happy", "'dispersed,happy' without a space"),
             ("s57_ocr", "87'2", "'87'2' for '87½'"),
             ("bm_eq", "0.751n", "'0.751n' for '0.75 ln'"),
             ("dl_sd", "thirtyfive", "'thirtyfive' for 'thirty-five'"),
             ("dl_concede", "are are", "'are are' as printed"),
             ("bs_countries", "fl-coefficients", "'fl' for 'β'"),
             ("mrw_059", "the o implied", "'o' for 'α'"),
             ("mrw_third", "end intermediate", "'end' for 'and'"),
             ("mrw_textbook", "end the economy", "'end' for 'and'"),
             ("mrw_lambda", "a-$-l/3", "'a-$-l/3' for 'α = β = 1/3'"),
             ("mrw_textbook", "If -O", "'-O' for 'β = 0'"),
             ("mrw_direction", "the affects of", "'affects' for 'effects'"),
             ("pr_dominant", "modem", "'modem' for 'modern'"),
             ("pr_ratio", "countrieshas", "words run together"),
             ("ef_copyright", "C) 1995", "'C)' for '©'"),
             ("ef_caveats", "tp identify", "'tp' for 'to'"),
             ("jg_160", "1-60", "'1-60' and '0-10' for '1·60' and '0·10'"),
             ("loc_swan_born", "1818-01-14", "'1818' for '1918'")]
DOT_ROWS = ("sw_alpha", "sw_impact", "jg_160")          # the decimals the rule 'dot' reads


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
    for rid in DOT_ROWS:
        assert any(how == "dot" for _, how in READINGS[rid]), rid
    assert "read by the rule 'dot' of checks/check_ch40.py" in notes
    assert set(src) == set(df["file"]), sorted(set(src) ^ set(df["file"]))
    # the copies of the articles on third-party sites: address, date and hash recorded, the files not committed
    for key in ("harrod1939", "solow1956", "phelps1961", "solow1957", "baumol1986", "swan1956"):
        assert f"{key} {src[key]['url']} " in notes and src[key]["sha256"] in notes, key
        assert "read to verify, not committed" in src[key]["version"], key
    # a key another snapshot holds names the same document
    for name in ("consumption_facts", "phillips_facts", "islm_facts", "warfinance_facts"):
        other = load_snapshot(name)[1]["sources"]
        for key, s in src.items():
            if key in other:
                assert other[key]["url"] == s["url"] and other[key]["sha256"] == s["sha256"], (name, key)


N_QUOTED, N_IMAGE = 134, 51


# ---------------------------------------------------------------------------------------------------
# 2. Every “…” of the text against the snapshot
# the chapter's Chinese renderings of the quotations: rendering -> row (or rows)
TRANSLATIONS = {
    "某种不安": "nb_discomfort",
    "奇迹般的运气": "nb_luck",
    "思想上的革命": "hr_revolution",
    "基本方程": "hr_fundamental",
    "高度不稳定的": "hr_unstable",
    "刀刃": "s56_knife",
    "关键": "s56_crucial",
    "走钢丝": "s56_tightrope",
    "平衡": "s56_demand",
    "合理的": "sw_plausible",
    "合理": "sw_external",
    "给增长迷的寓言": "ph_title",
    "黄金律": "ph_golden",
    "技术变化": "s57_shorthand",
    "稻草人": "sw_scarecrow",
    "令人清醒": "ab_sobering",
    "我们无知的度量": ("ab_ignorance", "jg_labels"),
    "惊人的": "nb_startling",
    "收敛俱乐部": "bm_club",
    "莫斯科的优先次序看来变化很小": "jec_priorities",
    "计划者让投资的增长在 1975 年以后显著放慢": "jec_planners",
    "余量": "jg_labels",
    "赋予生产率大得多的作用": "scb_reply",
    # the misreadings of the text layers quoted in the 史料说明
    "½ per cent": "sw_m",
    "4 per cent": "sw_m_ocr",
    "87'2": "s57_ocr",
    "eighth": "nb_eight",
    "eight": "nb_eight",
}
# the words of the source each rendering renders, in the quotation (or the transcription of the page image)
KEYWORDS = {
    "nb_discomfort": ["a certain discomfort"],
    "nb_luck": ["a miraculous stroke of luck"],
    "hr_revolution": ["a mental revolution"],
    "hr_fundamental": ["the fundamental equation"],
    "hr_unstable": ["a highly unstable one"],
    "s56_knife": ["knife-edge"],
    "s56_crucial": ['"crucial"'],
    "s56_tightrope": ["the tightrope view"],
    "s56_demand": ['"balance."'],
    "sw_plausible": ["''plausible'' figuring"],
    "sw_external": ["''plausible'' figure based on common private experience"],
    "ph_title": ["A Fable for Growthmen"],
    "ph_golden": ["the golden rule of accumulation"],
    "s57_shorthand": ["“technical change”"],
    "sw_scarecrow": ["a scarecrow (as Joan Robinson calls it)"],
    "ab_sobering": ["sobering"],
    "ab_ignorance": ["measure of our ignorance"],
    "jg_labels": ["The Residual", "The Measure of Our Ignorance"],
    "nb_startling": ["startling"],
    "bm_club": ["a convergence club"],
    "jec_priorities": ["Moscow's priorities appeared to change little"],
    "jec_planners": ["Planners allowed the rate of investment growth to slow markedly after 1975"],
    "scb_reply": ["assign a much larger role to productivity"],
    "sw_m": ["½ per cent"],
    "sw_m_ocr": ["4 per cent"],
    "s57_ocr": ["87'2"],
    "nb_eight": ["seven-eighths", "remaining eight"],
}
# the sources that may be quoted at length: works of the United States government (the study printed for the Joint
# Economic Committee, the BEA's introduction)
FREE = ("jec_", "scb_")


def tex_text() -> str:
    return "\n".join(l for l in TEX.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("%"))


def text_quotations() -> list[str]:
    """The “…” of the text; the closing question is Chapter 41's and the chapter's own question is in the guide and at
    the end of the opening (both checked by guide() and opening())."""
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 41's question"
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
    for q in ("4 per cent", "87'2", "eight"):
        assert f"“{q}”" in deeper, q
        rid = TRANSLATIONS[q]
        assert any(m[0] == rid and q in m[1] for m in MISPRINTS), q
    # the quotations of the text are short phrases where the source is in copyright: at most 12 characters
    for q in used:
        t = TRANSLATIONS[q]
        rids = (t,) if isinstance(t, str) else t
        if not all(r.startswith(FREE) for r in rids):
            assert len(q) <= 12, f"a long quotation of a source that allows short phrases only: “{q}”"
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
    """The phrase is in the text, and each number it prints (with its unit 万, 亿, 万亿; a thousands separator of the
    math, {,}, read as a comma; a minus sign not read) is the value given, within half a unit of its last digit (plus
    `slack`, in the same units). None skips a number (one checked by an assertion)."""
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


def told(phrase: str, pre: str, post: str = "") -> float:
    """The phrase is in the text; the Chinese numeral it prints between `pre` and `post` (to the end of the phrase when
    post is empty), read by zh()."""
    say(phrase)
    m = re.search(re.escape(pre) + ("(.+?)" + re.escape(post) if post else "(.+)$"), phrase)
    assert m, (phrase, pre, post)
    return zh(m.group(1))


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


def wp_year(key: str) -> int:
    """The year of a working paper, from the version of its source ('NBER Working Paper 3541, December 1990')."""
    m = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December) "
                  r"(\d{4})", version(key))
    assert m, key
    return int(m.group(2))


def their(name: str, rid: str, *words: str) -> list[float]:
    """Row rid of another chapter's snapshot: the words are in its quotation; its values."""
    df = load_snapshot(name, dtype=str, keep_default_na=False)[0].set_index("id")
    q = " ".join(df.loc[rid, "quote"].split())
    for w in words:
        assert w in q, (name, rid, w)
    return [float(x) for x in df.loc[rid, "value"].split(";")] if df.loc[rid, "value"] else []


def their_year(name: str, rid: str) -> int:
    df = load_snapshot(name, dtype=str, keep_default_na=False)[0].set_index("id")
    return int(df.loc[rid, "year"])


# ---------------------------------------------------------------------------------------------------
# The model, with the teaching inputs of the examples and the self-check
ALPHA, N, G, DELTA = 1 / 3, 0.01, 0.02, 0.03        # ex:solow-double
NGD = N + G + DELTA
S0, S1 = 0.10, 0.20                                # the saving rate before and after
N_HIGH = 0.03                                      # population growth raised to 3%
SC_S = 0.15                                        # self-check 1
SC_ALPHA2 = 1 / 2                                  # self-check 2
SC_SPEED = (0.8, 0.09)                             # self-check 3: alpha, n+g+delta
SC_TFP = (3.0, 4.0, 0.35)                          # self-check 4: output and capital per worker (% a year), share
EF_ALPHA = 0.4                                     # ex:solow-soviet: Easterly and Fischer's capital share of Table 4
YEARS = 200                                        # the length of the simulations


def steady(s: float, a: float = ALPHA, ngd: float = NGD) -> tuple[float, float]:
    """eq:solow-steady (per effective worker): k*, y*."""
    k = (s / ngd) ** (1 / (1 - a))
    return k, k ** a


def path(s0: float, s1: float, years: int = YEARS, a: float = ALPHA, ngd: float = NGD) -> pd.DataFrame:
    """eq:solow-accumulation year by year (per effective worker), from the steady state of s0 with the saving rate s1
    from year 0 on: k, y, the share of the log gap to the new steady state closed, consumption, and output per worker
    (log, year 0 = 0) on the new and the old path."""
    k = steady(s0, a, ngd)[0]
    ks = [k]
    for _ in range(years):
        k = k + s1 * k ** a - ngd * k
        ks.append(k)
    k = np.array(ks)
    y = k ** a
    y0, y1 = steady(s0, a, ngd)[1], steady(s1, a, ngd)[1]
    t = np.arange(years + 1)
    return pd.DataFrame(dict(year=t, k=k, y=y, closed=np.log(y / y0) / np.log(y1 / y0), c=(1 - s1) * y,
                             lny=np.log(y / y0) + G * t, lny_old=G * t))


def growth(P: pd.DataFrame) -> np.ndarray:
    """The growth rate of output per worker from year t to t + 1 (log, per cent)."""
    return 100 * np.diff(P["lny"].to_numpy())


def consumption(s: float, a: float = ALPHA, ngd: float = NGD) -> float:
    """Steady-state consumption per effective worker, (1 - s) y*(s)."""
    return (1 - s) * steady(s, a, ngd)[1]


def speed(a: float, ngd: float) -> float:
    """eq:solow-speed."""
    return (1 - a) * ngd


def tfp(gy: float, gk: float, a: float) -> float:
    """eq:solow-accounting per worker: the residual."""
    return gy - a * gk


# ---------------------------------------------------------------------------------------------------
# Penn World Table 10.01
@lru_cache(maxsize=None)
def pwt() -> pd.DataFrame:
    """One row per country: ln y0 (rgdpe/pop 1960), g (growth of rgdpna/pop 1960-2019, log, per year), s (the mean
    investment share), n (growth of population, log, per year), hc (1960)."""
    df, m = load_snapshot("pwt1001_convergence", keep_default_na=False, na_values=[""])
    assert 40 in m["used_in"] and m["fetch"] == FETCH
    out = pd.DataFrame(dict(code=df["countrycode"], name=df["country"],
                            lny0=np.log(df["rgdpe_1960"] / df["pop_1960"]),
                            g=(np.log(df["rgdpna_2019"] / df["pop_2019"]) - np.log(df["rgdpna_1960"] / df["pop_1960"]))
                            / (PWT_LAST - PWT_FIRST),
                            s=df["csh_i_mean_1960_2019"],
                            n=(np.log(df["pop_2019"]) - np.log(df["pop_1960"])) / (PWT_LAST - PWT_FIRST),
                            hc=df["hc_1960"]))
    return out


PWT_FIRST, PWT_LAST = 1960, 2019
GD = 0.05                                           # g + delta in the regressions, as in Mankiw, Romer and Weil


def ols(X: list[np.ndarray], y: np.ndarray) -> tuple[np.ndarray, float]:
    A = np.column_stack([np.ones(len(y))] + X)
    b, *_ = np.linalg.lstsq(A, y, rcond=None)
    e = y - A @ b
    return b, float(1 - e @ e / ((y - y.mean()) @ (y - y.mean())))


def regressions() -> dict[str, dict[str, float]]:
    """tab:solow-convergence: the coefficient on ln y0 (percentage points), the implied speed (% a year), R2, N."""
    D = pwt()
    H = D.dropna(subset=["hc"])
    out = {}
    for name, d, X in (("absolute", D, lambda d: [d["lny0"].to_numpy()]),
                       ("conditional", D, lambda d: [d["lny0"].to_numpy(), np.log(d["s"].to_numpy()),
                                                     np.log(d["n"].to_numpy() + GD)]),
                       ("human", H, lambda d: [d["lny0"].to_numpy(), np.log(d["s"].to_numpy()),
                                               np.log(d["n"].to_numpy() + GD), np.log(d["hc"].to_numpy())])):
        b, r2 = ols(X(d), d["g"].to_numpy())
        T = PWT_LAST - PWT_FIRST
        lam = -math.log(1 + b[1] * T) / T
        out[name] = dict(b=100 * b[1], lam=100 * lam, r2=r2, n=len(d))
    return out


def quarters() -> tuple[float, float, int]:
    """The mean growth (% a year) of the poorest and the richest quarter (len // 4 countries) in 1960."""
    D = pwt().sort_values("lny0")
    q = len(D) // 4
    return 100 * D["g"].iloc[:q].mean(), 100 * D["g"].iloc[-q:].mean(), q


@lru_cache(maxsize=None)
def usa() -> pd.DataFrame:
    df, m = load_snapshot("pwt1001_usa")
    assert 40 in m["used_in"] and m["fetch"] == FETCH
    return df.set_index("year")


# the data of the figures (figsrc/fig_ch40.py)
def diagram(kmax: float = 8.0, n: int = 321) -> pd.DataFrame:
    """fig:solow_diagram: saving s k^alpha for the two saving rates and the investment needed, (n+g+delta) k."""
    k = np.linspace(0, kmax, n)
    return pd.DataFrame(dict(k=k, save0=S0 * k ** ALPHA, save1=S1 * k ** ALPHA, need=NGD * k))


def transition(years: int = 60) -> pd.DataFrame:
    """fig:solow_transition: log output per worker on the new and the old path, and its growth rate (%)."""
    P = path(S0, S1, years)
    g = np.append(growth(P), np.nan)
    return pd.DataFrame(dict(year=P["year"], lny=P["lny"], lny_old=P["lny_old"], growth=g))


def convergence_points() -> pd.DataFrame:
    """fig:solow_convergence: ln y0, the growth rate (%), and the growth rate net of the investment share and
    population growth (plus the sample mean), with the slopes."""
    D = pwt()
    Z = np.column_stack([np.log(D["s"]), np.log(D["n"] + GD)])
    Zc = Z - Z.mean(axis=0)
    b, _ = ols([D["lny0"].to_numpy(), Z[:, 0], Z[:, 1]], D["g"].to_numpy())
    net = D["g"].to_numpy() - Zc @ b[2:]
    return pd.DataFrame(dict(code=D["code"], name=D["name"], lny0=D["lny0"], g=100 * D["g"], net=100 * net,
                             slope=100 * b[1]))


def soviet() -> dict:
    """fig:solow_soviet: Easterly and Fischer's Table 1 (output and capital per worker by decade) and the JEC's Table 2."""
    F = facts()
    y, k = F["ef_t1_y"][2::3], F["ef_t1_k"][2::3]
    periods = ["1950–59", "1960–69", "1970–79", "1980–87"]
    t2 = ["1951–65", "1966–75", "1976–80", "1981–85", "1986", "1987"]
    return dict(periods=periods, y=y, k=k, t2=t2, gnp=F["jec_t2_gnp"], cons=F["jec_t2_cons"], inv=F["jec_t2_inv"])


def recovery_year(s0: float = S1, s1: float = ALPHA) -> tuple[float, int]:
    """Raising the saving rate from s0 to s1: the fall of consumption in the first year (a share) and the first year in
    which consumption per effective worker is back at its level before the rise."""
    P = path(s0, s1)
    c0 = consumption(s0)
    back = int(P.index[P["c"] >= c0][0])
    return 1 - P["c"].iloc[0] / c0, back


# ---------------------------------------------------------------------------------------------------
# 4. Numbers, section by section
def guide(F, Y, Q):
    t = TEX.read_text(encoding="utf-8")
    assert f"\\guidequestion{{{GUIDE}}}" in t and GUIDE == PREV
    assert chapter("ch39_consumption").rstrip().endswith(PREV)                   # 第 39 章交来的问题
    assert ("\\guideprereq{\\chref{ch:divergence}\\enspace\\nameref{ch:divergence}；"
            "\\chref{ch:accounts}\\enspace\\nameref{ch:accounts}}") in t
    assert F["s56_title"][2] == F["sw_issue"][0]
    said("推导索洛—斯旺模型（1956）的稳态与收敛速度", F["s56_title"][2])
    assert "\\chapterstub" not in t


def opening(F, Y, Q):
    _, y87 = F["nb_title"]
    has("nb_title", "Lecture to the memory of Alfred Nobel", "Growth Theory and After")
    has("nb_stockholm", "Stockholm")
    said("1987 年 12 月 8 日，索洛", y87, mon("nb_title", "December"), F["nb_title"][0])
    assert F["nb_stockholm"] == [y87]
    say("在斯德哥尔摩作纪念诺贝尔的演讲，题为《增长理论及以后》")
    has("nb_dream", "So I do not know if I have ever dreamt about giving this Lecture.")
    has("nb_room", "I have been in this room before", "in real life, and I was awake")
    say("他开场说，他不知道自己有没有梦见过作这次演讲；他知道自己来过这个大厅，不过那是在现实里，而且是醒着的")
    has("nb_notbegin", "did not begin with my articles", "did not end there")
    said("他说，增长理论不是从他 1956 年与 1957 年的文章开始的，也没有在那里结束", *F["nb_notbegin"])
    assert F["nb_notbegin"] == [F["s56_title"][2], F["s57_title"][2]]
    has("nb_trail", "a trail that had been marked out by Roy Harrod and by Evsey Domar",
        "also by Arthur Lewis in a slightly different context")
    said("1950 年代，他走的路是哈罗德", F["nb_trail"][0])
    say("刘易斯（W. Arthur Lewis，1915—1991）在稍有不同的背景下也标过这条路")
    has("nb_discomfort", "relieve a certain discomfort that I felt with their work")
    assert F["nf_share"] == [1] and F["nf_prize"] == [y87]                        # 1/1: the prize undivided
    has("nf_motivation", "for his contributions to the theory of economic growth")
    say("那一年的经济学奖只授给他一人，理由是他对经济增长理论的贡献")
    # the recipe
    has("nb_routes", "noticeably different routes", "a classically simple answer",
        "the product of the capital-output ratio and the rate of growth of the (effective) labor force")
    say("国民储蓄率必须等于资本—产出比乘以（有效）劳动力的增长率")
    has("nb_constants", "were given constants")
    has("nb_sporadic", "sporadically and more or less independently")
    say("三个量在他们那里都是给定的常数，各自偶尔变动")
    assert F["nb_recipe"] == [2, 2]
    has("nb_recipe", "a recipe for doubling the rate of growth in a labor surplus economy",
        "simply to double the savings rate, perhaps through the public budget")
    say("在劳动过剩的经济里，要让增长率翻一番，让储蓄率翻一番就行，也许通过政府预算来做")
    has("nb_notsimply", "doubling the ex ante saving rate would not double the ex post saving rate",
        "unless something were taking care of the ex ante investment rate at the same time")
    assert "Well, not simply:" in column("note")["nb_notsimply"]
    say("他随即补了一句，事情没有这样简单，计划中的储蓄率翻一番，要有别的力量让投资同时跟上，实际的储蓄率才会翻一番")
    has("nb_underdeveloped", "In underdeveloped countries", "the recipe looked usable")
    has("nb_writings", "I believe I remember", "a sustained rise in the savings rate")
    say("他相信自己记得，讨论经济发展的著作常说，从慢增长转到快增长，关键是持续提高储蓄率")
    has("nb_implausible", "The recipe sounded implausible to me", "I can no longer remember exactly why")
    has("nb_spirit", "tinkering with the theory of economic growth", "improve on the Harrod-Domar model")
    has("nb_whyfirst", "replacing the constant capital-output (and labor-output) ratio")
    has("nb_production", "drawn to the theory of production")
    has("nb_intensity", "aggregate factor-intensity must be much more variable")
    say("单个产品的技术也许不很灵活，可是整个经济能选择多生产资本密集或劳动密集的产品，总的要素密集度应当变化得多")
    say("这一章反过来，把储蓄率当作给定，问储蓄能把增长推到哪里")
    assert paragraph("\\chref{ch:consumption}问家庭为什么储蓄").endswith(GUIDE)   # the opening ends with the question


def world(F, Y, Q):
    vol, no, y39, p0, p1 = F["hr_title"]
    has("hr_title", "An Essay in Dynamic Theory", "The Economic Journal")
    said("哈罗德 1939 年 3 月在《经济学杂志》上发表《论动态理论》", y39, mon("hr_title", "Mar."))
    has("hr_static", "the static method will not suffice")
    has("hr_marriage", "the marriage of the acceleration principle and the multiplier theory")
    say("他的“基本方程”把加速原理与乘数理论结合在一起")
    has("hr_warranted", "leave all parties satisfied that they have produced neither more nor less than the right amount")
    has("hr_eq", "G_w = s/C", "the Fundamental Equation in its simplest form")
    has("hr_symbols", "the amount of capital per unit increment of output required by technological and other conditions")
    say("基本方程最简单的形式是$G_w=s/C$，$s$是储蓄占收入的比例，$C$是技术等条件要求的每增加一单位产出所需的资本")
    s, C, gw = F["hr_numbers"]
    assert s / C == gw
    said("他给的数字是，储蓄占收入的 10\\%，资本系数为 4，有保证的增长率就是每年 2.5\\%", s, C, gw)
    has("hr_point", "producers, if they remain on it, will be satisfied")
    has("hr_excess", "undue depletion of stock or shortage of equipment", "stimulated to further expansion")
    has("hr_diverge", "the farther it diverges, the greater the stimulus to expansion")
    has("hr_aggravating", "instead of being self-righting, will be self-aggravating")
    has("hr_redundance", "a redundance of capital goods", "a depressing influence will be exerted")
    has("hr_cycle", "trade-cycle analysis")
    has("hr_save", "an increase in the propensity to save", "a higher rate of warranted growth",
        "the immediate effect is to raise the warranted", "rate above the actual rate", "farther below the warranted rate")
    say("储蓄倾向提高，有保证的增长率随之提高，眼前的效果却是让它高于实际的增长率，由此产生的压抑把实际增长越拉越低")
    say("在他的框架里，多储蓄未必带来快增长，先来的可能是萧条（本书的解读）")
    has("hr_natural", "the maximum rate of growth allowed by the increase of population, accumulation of capital, "
        "technological improvement and the work/ leisure preference", "full employment in some sense")
    has("hr_coincide", "no inherent tendency for these two rates to coincide")
    has("hr_cannot", "cannot advance more quickly than the natural rate allows")
    has("hr_chronic", "a chronic tendency to depression", "only achieved by having chronic unemployment")
    has("hr_better", "There is much to be said for the view", "lower rather than higher than the natural rate")
    say("有保证的增长率高于它，经济就有长期萧条的倾向，萧条把有保证的增长率拉下来，代价是长期失业")
    # Domar (1946): the index of the volume only
    y46, v14 = F["dm_volume"]
    has("dm_index", "DOMAR, EVSEY D.: Capital Expansion, Rate of Growth, and Employment")
    has("dm_volume", "Econometrica 1946: Vol 14")
    said("多马 1946 年在《计量经济学》第 14 卷上发表《资本扩张、增长率与就业》，从第 137 页起", y46, v14, F["dm_index"][0])
    said("他 1944 年关于债务负担的文章", their_year("warfinance_facts", "dm_title"))
    # Solow (1956)
    has("s56_title", "A Contribution to the Theory of Economic Growth", "The Quarterly Journal of Economics")
    said("索洛 1956 年 2 月在《经济学季刊》上发表《对经济增长理论的一个贡献》", F["s56_title"][2], mon("s56_title", "Feb."))
    has("s56_assumptions", "All theory depends on assumptions which are not quite true.")
    has("s56_knife", "at best balanced on a knife-edge of equilibrium growth", "the Harrod-Domar line of thought")
    has("s56_slip", "either growing unemployment or prolonged inflation")
    has("s56_crucial", '"crucial" assumption')
    has("s56_fixed", "fixed proportions", "no possibility of substituting labor for capital")
    has("s56_abandon", "the knife-edge notion of unstable balance seems to go with it")
    has("s56_tools", "long-run problems with the usual short-run tools")
    has("s56_multiplier", "the multiplier, the accelerator")
    has("s56_accepts", "accepts all the Harrod-Domar assumptions except that of fixed proportions")
    # Swan (1956)
    y56, month, vol32, no63 = F["sw_issue"]
    has("sw_issue", "The Economic Record 1956-11")
    has("sw_anu", "Australian National University")
    has("sw_title", "AND CAPITAL ACCUMULATION")
    said("同一年 11 月，澳大利亚国立大学的斯旺", month)
    assert y56 == F["s56_title"][2]
    has("sw_aim", "illustrate with two diagrams", "Adam Smith, Mill, and Lewis",
        "the connexion between capital accumulation and the growth of the productive labour force")
    has("sw_cobb", "Y = K^α N^β", "With constant returns to scale, α + β = 1.")
    said("他的生产函数是$Y=K^{\\alpha}N^{\\beta}$，规模报酬不变，$\\alpha+\\beta=1$", 1)
    has("sw_solow", "A similar device is used by R. M. Solow", "February, 1956")
    said("他在脚注里提到，索洛 1956 年 2 月的文章用了类似的办法", F["sw_solow"][0], mon("sw_solow", "February"))
    say("两人各自把可替代的生产函数放进了哈罗德的框架（本书的解读）")


def model(F, Y, Q):
    has("s56_one", "only one commodity, output as a whole")
    has("s56_saving", "The fraction of output saved is a constant s")
    has("s56_identity", "the basic identity at every instant of time: K = sY.")
    has("s56_crs", "constant returns to scale")
    has("s56_labor", "exogenous population growth", "a constant relative rate n")
    has("s56_full", "full employment is perpetually maintained")
    has("s56_prices", "the real wage rate adjusts so that all available labor is employed")
    has("s56_rental", "the real rental per unit of time for the services of capital stock")
    has("s56_eq6", "(6) ṙ = sF(r,1) − nr.")
    assert F["s56_eq6"] == [6, 1]
    has("s56_net", "net output after making good the depreciation of capital")
    said("索洛自己的写法是$\\dot r=sF(r,1)-nr$，$r$是资本与劳动之比，产出按补足折旧以后的净产出计，所以没有$\\delta$", 1)
    said("$\\Delta k=0$时，资本与劳动按同一速度增长，人均产出不再变化，这就是稳态", 0)
    has("s56_stable", "the equilibrium value r* is stable")
    has("s56_never", "there never can be - any knife-edge", "adjust to any given rate of growth of the labor force")
    has("s56_ratio", "the equilibrium value of K/ Y is s/n")
    has("s56_luck", 'the natural rate equals "the" warranted rate, not as an odd piece of luck but as a consequence of '
        "demand-supply adjustments")
    say("稳态的资本—产出比是$s/n$，自然增长率等于有保证的增长率。他说，这不是偶然的运气，是供求调整的结果")
    has("s56_three", "r2 is not")
    has("s56_lower", "Depending on the initially observed capital-labor ratio")
    has("s56_unbounded", "so productive and saves so much", "beyond all limits")
    has("s56_fixedexample", "Example 1: Fixed Proportions. This is the Harrod-Domar case.")
    assert F["s56_fixedexample"] == [1]
    say("固定比例是他的第一个例子，即哈罗德—多马的情形")
    has("s56_labor_red", "labor becomes redundant, and the extent of the redundancy grows")
    has("s56_excess", "the absolute amount of excess capacity is growing, too")
    has("s56_neoclassical", "the neoclassical side of the coin", "full employment economics")
    has("s56_shunted", "shunted aside")
    has("s56_notcontend", "It is not my contention that these problems don't exist")
    has("s56_tightrope", "the tightrope view of economic growth")
    has("s56_demand", "deficient or excess aggregate demand")
    # the saving rate changes the level
    assert np.isclose(ALPHA / (1 - ALPHA), 0.5)
    said("$y^{*}$对$s$的弹性，即储蓄率提高 1\\% 时$y^{*}$提高的百分比，是$\\alpha/(1-\\alpha)$，资本份额为三分之一时是$1/2$"
         "（本书的计算）", 1, 1, 1, 2)
    assert np.isclose(told("资本份额为三分之一时是", "资本份额为", "时是"), ALPHA)
    y_up = 100 * (steady(S1)[1] / steady(S0)[1] - 1)
    said("储蓄率翻一番，稳态的人均产出只增加约 41\\%", y_up)
    has("nb_developing", "permanently increasing its saving (investment) rate", "must therefore grow faster for a while")
    has("nb_notpermanent", "it will not achieve a permanently higher rate of growth of output")
    said("索洛 1987 年说，一个发展中经济若能永久提高储蓄率", F["nb_title"][1])
    s, C, gw = F["hr_numbers"]
    assert S0 * 100 == s and (100 * S1 / C) / (100 * S0 / C) == 2
    said("按哈罗德的方程，资本系数为 4 时，储蓄率从 10\\% 提到 20\\%，有保证的增长率也翻一番（本书的计算）", C, 100 * S0,
         100 * S1)
    # Swan's numbers
    (n_sw,), (a_sw,), (s_sw,) = F["sw_n"], F["sw_alpha"], F["sw_s"]
    has("sw_n", "the rate of growth of the labour force", "n = 1 per cent")
    has("sw_alpha", "a = 0-4")
    said("斯旺的数字例子是，劳动力每年增长 1\\%，资本的份额 0.4", n_sw, a_sw)
    lo, hi = F["sw_thrift"]
    assert hi == s_sw and hi == 2 * lo
    has("sw_thrift", "a thrift campaign suddenly raises the saving ratio")
    said("他让一场节俭运动把储蓄率从 5\\% 提到 10\\%", lo, hi)
    has("sw_at1", "output per head and the wage rate are higher", "the output-capital ratio and the profit rate are lower")
    has("sw_permanent", "These are permanent changes", "faster only in the course of transition")
    has("sw_plausible", "the impact effect of a sharp rise in the saving ratio may be of minor importance")
    impact, yld = F["sw_impact"]
    has("sw_impact", "the thrift campaign doubles the saving ratio", "the yield on capital is 8 per cent")
    said("储蓄率翻一番，资本的收益率是 8\\%，增长率在过渡开始时最多只提高 0.4 个百分点", yld, impact)
    assert np.isclose((hi - lo) * yld / 100, impact)
    said("这个数来自$\\Delta s\\times8\\%=5\\%\\times8\\%=0.4\\%$（本书的计算）", yld, hi - lo, yld, (hi - lo) * yld / 100)
    has("sw_answers", "at least two possible")
    has("sw_external", "the true social yield of capital is greater")
    has("sw_smith", "appealed to Adam Smith", "will not be pursued here")
    has("sw_classical", "Second, the rate of growth of labour may")
    has("sw_classical2", "This is the distinctively classical answer.")
    has("sw_elastic", "a Malthusian interpretation", "disguised unemployment")
    has("sw_union", "Trade Union resistance", "a potential supply of migrant labour")
    has("sw_proportion", "almost in proportion", "in equilibrium as well")
    has("sw_wage", "will not be much improved")
    say("这正是索洛记得的那个处方所设想的劳动过剩的经济（本书的解读）")
    has("s56_neutral", "simply multiplies the production function by an increasing scale factor")
    has("sw_m", "an annual m per cent", "at an assumed rate of ½ per cent")
    said("斯旺设技术进步每年贡献$m$，取 0.5\\%", F["sw_m"][0])
    has("sw_rising", "not only permanently higher, but perpetually rising")
    # the first comparison
    (a8, a1, half) = F["bs_alpha1"]
    has("bs_alpha1", "diminishing returns set in not at all", "versus infinity in the latter")
    assert a1 == 1 and speed(a1, NGD) == 0                                       # no convergence: an infinite half-life
    said("资本份额为 1、报酬不递减时，经济不趋向稳态，半衰期无穷长", a1)
    has("nb_independent", "independent of the saving (investment) rate")
    has("s56_inelastic", "completely inelastically")
    # ex:solow-double
    said("教学输入：$\\alpha=1/3$，$n=1\\%$，$g=2\\%$，$\\delta=3\\%$，储蓄率从 10\\% 提到 20\\%", 1, 3, 100 * N, 100 * G,
         100 * DELTA, 100 * S0, 100 * S1)
    kr, yr = steady(S1)[0] / steady(S0)[0], steady(S1)[1] / steady(S0)[1]
    assert np.isclose(kr, (S1 / S0) ** (1 / (1 - ALPHA))) and np.isclose(yr, (S1 / S0) ** (ALPHA / (1 - ALPHA)))
    said("（1）$n+g+\\delta=6\\%$。资本是$2^{1.5}\\approx2.83$倍，产出是$2^{0.5}\\approx1.41$倍，即增加约 41\\%", 100 * NGD,
         S1 / S0, 1 / (1 - ALPHA), kr, S1 / S0, ALPHA / (1 - ALPHA), yr, 100 * (yr - 1))
    cr = consumption(S1) / consumption(S0)
    said("（2）消费是$(1-s)\\,y$，稳态的消费是$0.8\\times1.41/0.9\\approx1.26$倍，增加约 26\\%", 1, 1 - S1, yr, 1 - S0, cr,
         100 * (cr - 1))
    said("刚提高时产出还没变，消费降为原来的$0.8/0.9$，下降约 11\\%", 1 - S1, 1 - S0, 100 * (1 - (1 - S1) / (1 - S0)))
    P = path(S0, S1)
    g = growth(P)
    up = 100 * ALPHA * (S1 / S0 - 1) * NGD                                        # the first year, approximately
    assert np.isclose(S0 * steady(S0)[1] / steady(S0)[0], NGD) and abs(g[0] - (100 * G + up)) < 0.1
    said("（3）原来的稳态里$s\\,y/k=6\\%$，储蓄率翻一番，有效资本每年增长$12\\%-6\\%=6\\%$，产出增长率约提高$\\alpha\\times6\\%=2$ "
         "个百分点，每个工人的产出增长率从 2\\% 升到约 4\\%", 100 * NGD, 200 * NGD, 100 * NGD, 100 * NGD, 100 * NGD, up,
         100 * G, 100 * G + up)
    assert abs(g[-1] - 100 * G) < 1e-3 and np.all(np.diff(g) < 0)
    said("以后逐年回落，长期仍是 2\\%（本书的计算）", 100 * G)
    said("教学输入$\\alpha=1/3$，$n+g+\\delta=6\\%$）。曲线是每个有效工人的储蓄$s\\,k^{\\alpha}$，实线$s=10\\%$，虚线$s=20\\%$", 1,
         3, 100 * NGD, 100 * S0, 100 * S1)
    said("交点是稳态，储蓄率翻一番，交点右移，资本变为约 2.83 倍，产出只变为约 1.41 倍", kr, yr)
    # population growth
    said("$y^{*}$对$n+\\delta$的弹性是$-\\alpha/(1-\\alpha)$，资本份额三分之一时是$-1/2$（本书的计算）", 1, 1, 2)
    has("mrw_spread", "higher population growth lowers income", "spread more thinly over the population of workers")
    third, el_text, el_aug = F["mrw_elasticity"]
    assert np.isclose(third, ALPHA) and np.isclose(el_text, -ALPHA / (1 - ALPHA)) and el_aug == -2
    has("mrw_elasticity", "with respect to n+g+6 is -1/2", "In our augmented model, this elasticity is -2.")
    said("在 Mankiw、Romer 与 Weil 加上人力资本的模型里，人均收入对$n+g+\\delta$的弹性是$-2$，不是$-1/2$", -el_aug, 1, 2)
    y_n = 100 * (1 - steady(S0, ngd=N_HIGH + G + DELTA)[1] / steady(S0)[1])
    assert np.isclose(y_n, 100 * (1 - steady(S1, ngd=N_HIGH + G + DELTA)[1] / steady(S1)[1]))   # whatever the saving rate
    said("按\\exref{ex:solow-double}的教学输入，人口增长率从 1\\% 提到 3\\%，稳态的人均产出下降约 13\\%（本书的计算）",
         100 * N, 100 * N_HIGH, y_n)
    say("储蓄率与人口增长率的作用方向相反，大小由资本份额决定，这就是模型对各国人均收入差别的解释（本书的概括）")
    # the stylised facts
    has("ef_kaldor", "the famous Kaldor stylized fact", "long been thought to remain relatively stable")
    has("ef_contradicts", "recent research on capital accumulation in market economies contradicts the Kaldor stylized "
        "fact")
    has("s56_share", "the relative share of labor is constant at 1 - a")
    said("索洛指出，科布—道格拉斯函数的特性正是劳动的相对份额不变，等于$1-a$，他的$a$就是这里的$\\alpha$", F["s56_share"][0])
    said("\\chref{ch:marx}算过英国，雇员报酬占 GDP 的份额 1855 年是 52.9\\%，1913 年是 54.4\\%",
         *there("ch22_marx", "占 GDP 的份额，1855 年是 52.9\\%，1913 年是 54.4\\%"))
    U = usa()
    assert list(U.index) == list(range(1950, 2020))
    out = U["rgdpna"] / U["emp"]
    gy = 100 * math.log(out.loc[2019] / out.loc[1950]) / (2019 - 1950)
    has("pwt_title", "Penn World Table version 10.01")
    assert "Number of persons engaged" in load_snapshot("pwt1001_usa")[1]["series"]
    said("按 Penn World Table 10.01，美国每个就业者的实际 GDP 1950—2019 年每年增长约 1.7\\%（本书的计算）",
         F["pwt_title"][0], 1950, 2019, gy)
    said("劳动报酬占 GDP 的份额 1950 年约 63\\%，2019 年约 60\\%", 1950, 100 * U.loc[1950, "labsh"], 2019, 100 * U.loc[2019, "labsh"])
    ky = U["rnna"] / U["rgdpna"]
    series = load_snapshot("pwt1001_usa")[1]["series"]
    assert "rnna ('Capital stock at constant 2017 national prices" in series
    assert "rgdpna ('Real GDP at constant 2017 national prices" in series
    said("资本存量与 GDP 之比都按不变价格算，却从 4.3 降到了 3.4（本书的计算）", ky.loc[1950], ky.loc[2019])
    assert ky.max() / ky.min() > 1.2 and U["labsh"].max() - U["labsh"].min() < 0.1
    say("份额大致不变，资本—产出比并不那么稳定（本书的解读）")


def transition_(F, Y, Q):
    has("sw_speed", "(1) is reached only in infinity",
        "the speed of travel towards it being directly related to the distance remaining to be travelled")
    has("sw_centuries", "might be visible for centuries", "only extreme assumptions could produce such a result")
    said("差距缩小一半所需的年数叫半衰期，是$\\ln 2/\\lambda$（本书的推导）", 2)
    third, ngd, lam35, half35 = F["mrw_lambda"]
    lam, half = F["mrw_textbook"]
    assert np.isclose(third, ALPHA) and np.isclose(ngd, NGD) and np.isclose(speed(ALPHA, NGD), lam)
    assert np.isclose(math.log(2) / lam, half, atol=0.5) and np.isclose(math.log(2) / lam35, half35, atol=0.5)
    has("mrw_textbook", "the economy moves halfway to steady state in about 17 years")
    said("按 Mankiw、Romer 与 Weil（1990）的算法，资本份额三分之一、$n+g+\\delta=6\\%$时，$\\lambda$是 4\\%，经济约 17 年走完到稳态的"
         "一半路程", wp_year("mrw1990"), 100 * ngd, 100 * lam, half)
    say("资本份额越大，报酬递减越慢，收敛也越慢")
    P = path(S0, S1)
    g = growth(P)
    excess = g - 100 * G
    assert 1.9 < g[0] / (100 * G) < 2                                            # almost doubled
    assert 0.5 < excess[10] / excess[0] < 0.55
    said("多出来的部分随后逐年缩小，10 年以后只剩一半多一点", 10)
    assert np.all(P["lny"].iloc[1:] > P["lny_old"].iloc[1:])
    say("人均产出的水平却一直高于旧路径（本书的计算）")
    said("接\\exref{ex:solow-double}，储蓄率在第 0 年从 10\\% 提到 20\\%", 0, 100 * S0, 100 * S1)
    said("第 10 年、第 30 年每个有效工人的产出走完了多少路程", 10, 30)
    lam_ = speed(ALPHA, NGD)
    said("（1）$\\lambda=(2/3)\\times6\\%=4\\%$，半衰期$0.693/0.04\\approx17$ 年", 2, 3, 100 * NGD, 100 * lam_, math.log(2),
         lam_, math.log(2) / lam_)
    closed = P["closed"]
    halfway = int(P.index[closed >= 0.5][0])
    said("（2）逐年模拟，第 10 年走完约 41\\% 的对数差距，第 30 年约 77\\%，一半的差距约用 14 年（本书的计算）", 10,
         100 * closed[10], 30, 100 * closed[30], halfway)
    assert halfway < math.log(2) / lam_                                          # faster than the linear approximation
    say("比线性化的近似快，因为差距大时，储蓄超出维持所需的部分按比例也大。线性化只在稳态附近准确。")
    said("储蓄率从 10\\% 提到 20\\% 以后的过渡", 100 * S0, 100 * S1)
    said("每个工人的产出（对数，第 0 年为 0）", 0, 0)
    said("每个工人的产出增长率，提高的当年接近 4\\%，以后逐年回到 2\\%", g[0], 100 * G)
    # Solow's surprise
    has("nb_surprised", "the relatively minor part the model ascribed to capital formation")
    has("nb_quota", "independent of the investment quota")
    has("nb_shorter", "even in the shorter run increased investment would do very little for transitory growth")
    has("nb_leverage", "very little leverage for policy aimed at promoting investment")
    said("索洛 1987 年回顾，模型给资本形成的作用这样小，起初连他自己也很意外", F["nb_title"][1])
    # Phelps's fable
    has("ph_title", "The Golden Rule of Accumulation: A Fable for Growthmen", "The American Economic Review")
    has("ph_yale", "assistant professor of economics at Yale University")
    said("1961 年，耶鲁大学的经济学助理教授菲尔普斯", F["ph_title"][2])
    has("ph_kingdom", "the Kingdom of Solovia was gripped by a great debate")
    has("ph_faster_debate", "it can grow faster")
    has("ph_sustainable", "Sustainable growth is best")
    has("ph_natural", "can come only from natural forces")
    has("ph_task", "a task force")
    has("ph_prize", "a prize for the discovery of the optimum investment ratio")
    has("ph_peasant", "a brilliant peasant, Oiko Nomos")
    has("ph_theorem", "Along the optimal golden-age path", "the competitive rate of profits")
    has("ph_each", "each generation invests on behalf of future generations")
    has("ph_slowed", "our consumption must be slowed")
    has("ph_faster", "we must consume faster")
    has("ph_compact", "a solemn compact henceforth to invest by the golden rule")
    has("ph_nogeneration", "no generation in all the future of Solovia will ever wish")
    has("ph_crowd", "The crowd dispersed")
    has("ph_skeptics", "skeptics who reminded the King of Oiko's assumptions")
    has("ph_econometricians", "a team of econometricians")
    has("ph_cobb", "the Cobb-Douglas function")
    has("ph_share", "a was capital's share")
    has("ph_sa", "On the golden-rule path, s would equal a.")
    has("ph_pressed", "pressed the King for a program to attain the golden-rule path")
    has("ph_levies", "proclaimed golden-rule growth a national purpose and instituted special levies")
    drop, back = recovery_year()
    assert np.isclose(drop, 1 / 6)
    said("按\\exref{ex:solow-double}的教学输入，储蓄率从 20\\% 提到黄金律的三分之一，提高的那一年消费要减少六分之一，约 27 年以后"
         "，每个工人的消费才赶上储蓄率不变时的那条路径（本书的计算）", 100 * S1, back)
    phrase = "储蓄率从 20\\% 提到黄金律的三分之一，提高的那一年消费要减少六分之一"
    assert np.isclose(told(phrase, "黄金律的", "，"), ALPHA) and np.isclose(told(phrase, "减少", ""), drop)
    say("少消费的是过渡期间活着的人，多消费的是以后的人（本书的解读）")
    say("储蓄率高于黄金律时，少储蓄一点，现在与将来都能多消费，这样的经济积累过度了（本书的解读）")
    say("模型里的$s$是一个参数。在实际的经济里，它是家庭、企业与政府的选择加总起来的（\\chref{ch:consumption}）")
    say("索洛记得的那个处方，就是通过政府预算提高储蓄率")
    has("s56_policy", "via tax, expenditure, and monetary policies", "leaves the nation some leeway to choose",
        "relatively heavy capital formation, low consumption, rapid growth; or the reverse, or some mixture")
    has("s56_strains", "cheap money and a budget surplus", "without serious strains")
    assert page("s56_policy") == page("s56_strains") > page("s56_demand")                # the last section, Policy Implications
    said("他 1956 年在文末说，税收、支出与货币政策都能维持充分就业，国家因此有余地选择，是多积累、少消费、快增长，还是反过来，或者折中",
         F["s56_title"][2])
    say("他也说，这类政策，例如低利率加预算盈余，难免带来严重的紧张")
    say("在计划经济里，投资率由中央的计划者定，后面苏联的案例就是这样（\\secref{sec:solow-check}）")
    say("储蓄率由谁定，谁就决定了这笔账由哪几代人付（本书的解读）")
    # ex:solow-golden
    said("（1）稳态的每个有效工人的消费是$(1-s)\\bigl(s/(n+g+\\delta)\\bigr)^{\\alpha/(1-\\alpha)}$，它在什么储蓄率最大？", 1, 1)
    said("（2）储蓄率为 10\\%、20\\% 与三分之一时，稳态消费之比是多少？", 100 * S0, 100 * S1)
    grid = np.linspace(0.01, 0.99, 9801)
    assert abs(grid[np.argmax([consumption(s) for s in grid])] - ALPHA) < 1e-3
    said("（1）对$s$求导并令其为零，$s=\\alpha=1/3$", 1, 3)
    c = [(1 - s) * math.sqrt(s) for s in (S0, S1, ALPHA)]
    assert np.allclose(np.array(c) / c[0], [consumption(s) / consumption(S0) for s in (S0, S1, ALPHA)])
    said("（2）消费与$(1-s)\\sqrt{s}$成正比，三者分别是 0.285、0.358 与 0.385", 1, *c)
    said("黄金律的稳态消费比 20\\% 时多约 8\\%，比 10\\% 时多约 35\\%（本书的计算）", 100 * S1, 100 * (c[2] / c[1] - 1),
         100 * S0, 100 * (c[2] / c[0] - 1))


def accounting(F, Y, Q):
    has("s57_title", "Technical Change and the Aggregate Production Function", "The Review of Economics and Statistics")
    said("1957 年 8 月，索洛在《经济学与统计学评论》上发表《技术变化与总量生产函数》", F["s57_title"][2],
         mon("s57_title", "Aug."))
    has("s57_wrinkle", "segregating variations in output per head due to technical change")
    has("s57_price", "one new required time series, the share of labor or property in total income",
        "factors are paid their marginal products")
    has("s57_appeals", "Either this kind of aggregate economics appeals or it doesn't. Personally I belong to both schools.")
    has("s57_robinson", "profound difficulties", "the quantity of capital")
    has("s57_shorthand", "any kind of shift in the production function",
        "slowdowns, speed-ups, improvements in the education of the labor force")
    has("s57_eq1a", "Q = A(t)f(K,L) (1a)")
    has("s57_eq2a", "q̇/q = Ȧ/A + w_K k̇/k. (2a)")
    say("索洛按每个工时写成$\\dot q/q=\\dot A/A+w_K\\,\\dot k/k$，$q$与$k$是每个工时的产出与资本，$w_K$是资本的份额")
    y09, y49 = F["s57_t1_1909"][0], F["s57_t1_1949"][0]
    has("s57_data", "real private non-farm GNP per man hour, Kendrick's valuable work")
    has("s57_goldsmith", "Goldsmith's estimates")
    said("他用的是美国私人非农业部门 1909—1949 年的数据，产出用 Kendrick 的实际国民生产总值，资本用 Goldsmith 的估计", y09, y49)
    has("s57_unemployed", "reduced the Goldsmith figures by the fraction of the labor force unemployed",
        "This is undoubtedly wrong, but probably gets closer to the truth")
    years40, shift = F["s57_doubled"]
    assert years40 == y49 - y09 == F["s57_avg"][0]
    has("s57_doubled", "approximately doubled", "the cumulative upward shift in the production function was about 80")
    said("按他的计算，40 年里每个工时的产出大约翻了一番，生产函数累计上移约 80\\%", years40, shift)
    assert np.isclose(100 * (F["s57_t1_1949"][4] - 1), shift, atol=1)
    one8, seven8 = F["s57_eighth"]
    phrase = "他说，可以认为增长里约八分之一归于每个工时的资本增加，其余八分之七归于技术变化"
    assert np.isclose(told(phrase, "约", "归于"), one8) and np.isclose(told(phrase, "其余", "归于技术"), seven8)
    assert np.allclose([seven8, one8], [x / 100 for x in F["s57_summary"]])
    q09, q49, a49, _, _, net = F["s57_623"]
    assert q09 == F["s57_t1_1909"][2] and q49 == F["s57_t1_1949"][2] and a49 == F["s57_t1_1949"][4]
    assert abs(q49 / a49 - net) < 0.0005
    has("s57_t1_dollars", "1939 dollars")
    said("具体算法是，按 1939 年价格，每个工时的实际国民生产总值从 62.3 美分增加到 127.5 美分，除去技术变化以后只有 70.5 美分",
         F["s57_t1_dollars"][0], 100 * q09, 100 * q49, 100 * net)
    cents, rise = F["s57_cents"]
    assert abs(100 * (q49 - q09) - rise) < 0.5 and abs(100 * (net - q09) - cents) < 0.5
    said("65 美分的增加里，约 8 美分归于资本密集度的提高", rise, cents)
    said("整个时期生产函数平均每年上移约 1.5\\%", F["s57_avg"][1])
    has("s57_break", "there does seem to be a break at about 1930")
    said("他也看到时期之间的差别，大约在 1930 年似乎有一个转折", F["s57_break"][0])
    n21, r21, n19, r19 = F["s57_first21"]
    assert n21 + n19 == years40
    said("前 21 年的上移平均每年约 0.9\\%", n21, r21)
    said("后 19 年快得多，平均每年约 2.25\\%", n19, r19)
    has("s57_posthoc", "Such post hoc splitting-up of a period is always dangerous")
    said("有证据表明技术变化在 1929 年以后可能加快了", F["s57_posthoc"][0])
    y0, y1, frac3 = F["s57_fn6"]
    assert y0 == y09
    said("前半期的 1909—1929 年，资本密集度的提高能解释约三分之一", y0, 1900 + y1)
    assert np.isclose(told("资本密集度的提高能解释约三分之一", "约", ""), frac3)
    has("s57_embodied", "much, perhaps nearly all, innovation must be embodied in new plant and equipment")
    has("s57_neutral", "Technical change during that period was neutral on average.")
    has("s57_curvature", "a distinct impression of diminishing returns, but the curvature is not violent")
    # Swan's appendix
    has("sw_robinson_fn", "especially those raised by Joan Robinson")
    has("sw_units", "in the hope that he will forget to ask in what units C is measured")
    has("sw_meccano", "identical meccano sets, which never wear out")
    has("sw_deceive", "could be rigorously established in a form that would deceive nobody")
    has("sw_difficulties", "great difficulties in handling the concept of Capital in a process of change")
    # ex:solow-accounting
    _, w09, q09_, k09, a09 = F["s57_t1_1909"]
    _, w49, q49_, k49, a49_ = F["s57_t1_1949"]
    has("s57_t1_1909", "TABLE 1.")
    said("按索洛的表 1，1909 年每个工时的产出是 62.3 美分，每个工时的资本是 2.06 美元，财产的份额 0.335；1949 年三者是 127.5 美分、"
         "2.70 美元与 0.326", 1, y09, 100 * q09_, k09, w09, y49, 100 * q49_, k49, w49)
    gy = 100 * math.log(q49_ / q09_) / years40
    gk = 100 * math.log(k49 / k09) / years40
    said("（1）产出每年$\\ln(127.5/62.3)/40\\approx1.79\\%$，资本每年$\\ln(2.70/2.06)/40\\approx0.68\\%$", 100 * q49_, 100 * q09_,
         years40, gy, k49, k09, years40, gk)
    w = (w09 + w49) / 2
    said("（2）平均份额约 0.33，资本深化贡献$0.33\\times0.68\\%\\approx0.22$ 个百分点，余量约 1.57\\%", w, w, gk, w * gk,
         tfp(gy, gk, w))
    assert abs(w * gk / gy - 1 / 8) < 0.01
    say("资本的贡献约占八分之一（本书的计算）")
    ga = 100 * math.log(a49_) / years40
    assert ga < tfp(gy, gk, w)
    said("索洛逐年算的$A(t)$到 1949 年是 1.809，每年约 1.48\\%，比两端一次算的略低", y49, a49_, ga)
    # Abramovitz
    has("ab_title", "Resource and Output Trends in the United States Since 1870")
    has("ab_op52", "OCCASIONAL PAPER 52")
    n52, y56 = F["ab_op52"]
    said("1956 年在美国国民经济研究局发表第 52 号不定期论文", y56, n52)
    a0, a1_, b0, b1, quad, trip = F["ab_quadrupled"]
    has("ab_quadrupled", "net national product per capita in constant prices approximately quadrupled",
        "population more than tripled")
    said("他比较了 1869—1878 年与 1944—1953 年两个十年", a0, 1800 + a1_, b0, 1900 + b1)
    phrase = "按不变价格，人均净国民产值约增加到四倍，人口增加到三倍多"
    assert told(phrase, "约增加到", "倍") == quad and told(phrase, "人口增加到", "倍") == trip
    base0, base1 = F["ab_1919"]
    has("ab_14", "rises only some 14 per cent", "based on the twenties")
    has("ab_index", "had the productivity of resources remained constant at base period levels")
    said("他把人均的劳动与资本按基期 1919—1928 年的收入份额加成一个资源指数，它在这期间只上升约 14\\%", base0, 1900 + base1,
         F["ab_14"][0])
    assert abs(100 * (quad / (1 + F["ab_14"][0] / 100) - 1) - F["ab_250"][0]) < 5
    said("具有代表性的一单位资源，生产率因此必须提高约 250\\%", F["ab_250"][0])
    has("ab_base", "may arise in some part from our choice of a base period")
    fy0, fy1, fpct = F["s57_fabricant"]
    has("s57_fabricant", "Solomon Fabricant has estimated", "attributable to technical progress")
    has("nb_fabricant", "Solomon Fabricant at the National Bureau of Economic Research")
    # Solow's look back and Denison
    has("nb_startling", "the main result of that 1957 exercise was startling")
    has("nb_expected", "a larger role for straightforward capital formation than I actually found")
    said("索洛 1987 年回顾，1957 年的结果是“惊人的”", F["nb_title"][1], F["nb_startling"][0])
    (thirty,) = F["nb_heldup"]
    assert thirty == F["nb_title"][1] - F["nb_startling"][0]
    has("nb_heldup", "held up surprisingly well in the thirty years since then", "especially by Edward Denison")
    said("他说，这个大的结论在此后 30 年里站住了", thirty)
    has("nb_unpack", "various human-capital variables", '"technological change in the narrow sense"')
    d0, d1, g31 = F["nb_denison"]
    has("nb_denison", "real non-residential business output increased at an average rate of 3.1 percent a year")
    said("据索洛的转述，丹尼森估计，1929—1982 年美国非住宅企业的实际产出每年增长 3.1\\%", d0, d1, g31)
    quarter, (edu, half) = F["nb_quarter"][0], F["nb_education"]
    assert abs(edu / 100 * g31 - half) < 0.01
    has("nb_quarter", "increased labor input of constant educational level")
    said("受教育程度不变的劳动投入增加贡献四分之一，劳动者受教育程度的提高贡献 16\\%", edu)
    assert np.isclose(told("受教育程度不变的劳动投入增加贡献四分之一", "贡献", ""), quarter)
    cap, c0, c1 = F["nb_capital12"]
    assert (c0, c1) == (y09, y49) and abs(cap / 100 - one8) < 0.01
    said("资本只贡献 12\\%，索洛说，这恰好与他 1909—1949 年的结果几乎一样", cap, c0, c1)
    assert F["nb_allocation"] == F["nb_scale"]
    has("nb_scale", "a very insecure imputation")
    said("资源配置的改善与规模经济各贡献 11\\%，索洛说后一项的估算很不可靠", F["nb_scale"][0])
    said("知识的进步贡献 34\\%", F["nb_knowledge"][0])
    total = 100 * quarter + edu + cap + F["nb_allocation"][0] + F["nb_scale"][0] + F["nb_knowledge"][0]
    assert total == F["nb_109"][0]
    nine, g31b, misc = F["nb_misc"]
    assert nine == total - 100 and g31b == g31 and nine / 100 * g31 < misc
    said("各项加起来是 109\\%，其余因素使增长每年少了不到 0.3 个百分点", total, misc)
    # two-factor productivity
    said("若产出其实是$Y=A\\,K^{\\beta}X^{\\alpha}L^{1-\\alpha-\\beta}$", 1)
    say("人均资本增加时，两种要素的全要素生产率多出资本份额乘以人均资本的增长率，把资本深化也算进了技术")
    said("只要那几十年英格兰每个工人的资本有所增加，\\chref{ch:divergence}算出的 1800—1860 年每年约 0.8\\%，就高于按三种要素算的数"
         "（本书的推导）",
         *there("ch21_divergence", "1800—1860 年，全要素生产率每年增长 0.80\\%"))


def check(F, Y, Q):
    y86 = F["bm_title"][2]
    y0, y1, const, slope, y0b, r2 = F["bm_eq"]
    assert y0 == y0b and slope < 0
    has("bm_16", "the 16 industrialized leaders in Maddison's sample")
    said("Baumol（1986）用 Maddison 样本里的 16 个工业国，看 1870—1979 年", y86, F["bm_16"][0], y0, y1)
    said("按他的回归，1870 年每个工时的 GDP 越高，此后的增长越慢，斜率是$-0.75$，$R^{2}$为 0.88", y0, -slope, r2)
    said("$R^{2}$是回归能解释的增长率差别所占的比例，0.88 即 88\\%", r2, 100 * r2)
    has("bm_72", "R2 is virtually zero", "do not even yield a negatively sloping regression line")
    said("他也说明，换成 72 个国家，$R^{2}$几乎为零，回归线连负的斜率都没有", F["bm_72"][0])
    has("bm_spillover", "a plausible alternative interpretation", "the spillovers from leader economies to followers")
    has("bm_almost", "almost automatically")
    has("bm_public", "the nature of a public good")
    has("bm_club", "members of a convergence club of their own")
    has("bm_ldc", "shared by planned economies but not less developed countries")
    has("bm_cars", "may well be related to product mix and education", "a better car-producing robot in Japan")
    # De Long
    has("dl_title", "Working Paper No. 2419")
    said("按 De Long（1987）的工作论文", wp_year("delong1987"))
    has("dl_construction", "guaranteed by construction")
    has("dl_design", "by design of nations that have successfully developed")
    has("dl_selection", "sample selection bias")
    has("dl_japan", "does not provide a fair test of convergence")
    has("dl_finland", "The second poorest of Maddison's sixteen in 1870 was Finland")
    said("他以 Maddison 16 国里 1870 年第二穷的芬兰的收入为界，重选了 1870 年看来同样可能收敛的 22 国", F["bm_16"][0],
         F["dl_finland"][0], F["dl_finland"][1], F["dl_22"][0])
    has("dl_22", "Argentina, Chile, East Germany", "Ireland, New Zealand, Portugal and Spain are added")
    has("dl_finland", "Japan is removed")
    y79, pct, y70, n22, y70b = F["dl_sd"]
    assert y79 == y1 and y70 == y70b == y0 and n22 == F["dl_22"][0]
    said("他说，16 国对数收入的标准差 1979 年只有 1870 年的 35\\%，这 22 国却和 1870 年一样分散", F["bm_16"][0], y79, y70, pct,
         n22, y70)
    has("dl_error", "For the central case of equal variances, growth since 1870 is unrelated to income in 1870.")
    said("他又考虑 1870 年收入的测量误差，误差方差与回归扰动的方差相等时，1870 年以来的增长与 1870 年的收入无关", y0, y0, y0)
    has("dl_noconv", "There is no convergence.")
    # Barro
    has("br_uncorrelated", "per capita growth rates for about 100 countries", "uncorrelated with the starting level")
    said("按 Barro（1989）的工作论文，约 100 个国家战后的人均增长率与初始的人均产出无关", wp_year("barro1989"),
         F["br_uncorrelated"][0])
    has("br_school", "primary and secondary school-enrollment rates",
        "countries with lower per capita product tend to grow faster")
    has("br_government", "government consumption is inversely related to growth", "positively related to political stability")
    has("br_unexplained", "leaves unexplained", "sub- Saharan Africa and Latin America")
    has("br_africa", "The estimated coefficient on AFRICA is significantly negative")
    # Barro and Sala-i-Martin
    lo, hi = F["bs_states"]
    has("bs_states", "regardless of the time period")
    has("bs_1840", "data since 1840 from the U.S. states")
    said("按 Barro 与 Sala-i-Martin（1990）的估计，美国各州 1840 年以来的收敛速度无论哪个时期都约为每年 2\\% 到 2.5\\%",
         wp_year("bsm1990"), F["bs_1840"][0], lo, hi)
    b0, b1, n98 = F["bs_98"]
    has("bs_98", "indicate lack of convergence")
    has("bs_countries", "roughly 2% per year")
    said("98 个国家 1960—1985 年的简单回归看不出收敛，加上其他解释变量以后，速度也约为每年 2\\%", n98, b0, b1,
         F["bs_countries"][0])
    has("bs_alpha", "in the neighborhood of 0.8", "diminishing returns to capital set in slowly")
    said("他们说，新古典模型要配上这个速度，资本份额得在 0.8 左右", F["bs_alpha"][0])
    assert F["bs_alpha"][0] == F["bs_alpha1"][0]
    has("bs_lower", "imply a more rapid rate of convergence than that revealed by the data")
    has("bs_open", "poor economies catch up faster to rich ones")
    has("bs_higher", "becomes even higher if we allow for open-economy features")
    # Mankiw, Romer and Weil
    said("Mankiw、Romer 与 Weil（1990）的检验针对稳态的水平", wp_year("mrw1990"))
    has("mrw_direction", "correctly predicts the direction", "does not correctly predict the magnitudes")
    has("mrw_toolarge", "too large")
    has("mrw_059", "is .59")
    said("模型隐含的资本份额是 0.59，不是三分之一", F["mrw_059"][0])
    has("mrw_80", "about 80 percent of the international variation in income per capita")
    has("mrw_third", "are about 1/3")
    assert np.isclose(F["mrw_third"][0], ALPHA)
    said("加上人力资本以后，模型能解释各国人均收入差别的约 80\\%，物质资本与人力资本的份额都约为三分之一", F["mrw_80"][0])
    has("mrw_controlling", "After controlling for those variables that the Solow model says determine the steady state")
    has("mrw_converge", "at approximately the rate that the model predicts")
    said("他们说，控制了决定稳态的变量，人均收入有明显的收敛，速度约为模型预测的每年 2\\%", 100 * F["mrw_lambda"][2])
    say("储蓄率本身也随增长而变（\\chref{ch:consumption}），增长对储蓄率的回归不等于模型里储蓄的因果效应（本书的解读）")
    # Penn World Table 10.01: tab:solow-convergence
    R = regressions()
    A, Cn, H = R["absolute"], R["conditional"], R["human"]
    assert A["b"] < 0 and Cn["b"] < A["b"] and H["b"] < Cn["b"] and abs(A["lam"]) < 0.1   # '—': no speed to speak of
    said("收敛的检验：1960—2019 年（本书的计算）", PWT_FIRST, PWT_LAST)
    said("初始收入的系数（百分点） & $-0.05$ & $-0.76$ & $-1.22$", -A["b"], -Cn["b"], -H["b"])
    said("隐含的收敛速度（\\%） & — & 1.0 & 2.1", Cn["lam"], H["lam"])
    said("$R^{2}$ & 0.00 & 0.35 & 0.44", A["r2"], Cn["r2"], H["r2"])
    said("国家数 & 111 & 111 & 104", A["n"], Cn["n"], H["n"])
    assert A["n"] == len(pwt()) and H["n"] == pwt()["hc"].notna().sum()
    pwt_cite = "Penn World Table 10.01（Feenstra、Inklaar 与 Timmer 2015；CC BY 4.0）"
    assert words_of("pwt_licence") == "CC-BY-4.0"
    said(pwt_cite, F["pwt_title"][0], F["pwt_ref"][0], float(words_of("pwt_licence").rsplit("-", 1)[1]))
    series = load_snapshot("pwt1001_convergence")[1]["series"]
    for words in ("rgdpna_2019 ('Real GDP at constant 2017 national prices", "rgdpe_1960 ('Expenditure-side real GDP at "
                  "chained PPPs", "csh_i, 'Share of gross capital formation", "'Human capital index, based on years of "
                  "schooling and returns to education'"):
        assert words in series, words
    said("因变量是 1960—2019 年每年的人均实际 GDP 增长率（按本国的不变价格），初始收入是 1960 年人均实际 GDP", PWT_FIRST,
         PWT_LAST, PWT_FIRST)
    said("条件收敛加上 1960—2019 年平均投资份额的对数与$n+0.05$的对数，$n$是人口增长率；最后一列再加 1960 年人力资本指数的对数，"
         "有这个指数的国家少一些", PWT_FIRST, PWT_LAST, GD, PWT_FIRST)
    said("系数是对数初始收入增加 1 时增长率变化的百分点，收敛速度按 59 年换算", 1, PWT_LAST - PWT_FIRST)
    said("本书用 Penn World Table 10.01 做了同样的检验", F["pwt_title"][0])
    said("各国 1960 年的收入按购买力平价比较，即按同一篮子商品在各国的价格折算，不按市场汇率（\\chref{ch:external}）", PWT_FIRST)
    said("样本是 1960 年与 2019 年都有数据、每年都有投资份额（资本形成占 GDP 的比例）的国家", PWT_FIRST, PWT_LAST)
    assert A["r2"] < 0.01
    said("它们此后的人均增长率与 1960 年的人均收入几乎无关", PWT_FIRST)
    say("控制投资份额与人口增长以后，系数变负")
    assert abs(H["lam"] - 100 * F["mrw_lambda"][2]) < 0.25 and lo <= H["lam"] <= hi
    said("再加上 1960 年的人力资本指数，隐含的收敛速度与 Barro、Sala-i-Martin 和 Mankiw、Romer、Weil 的估计相近（本书的计算）",
         PWT_FIRST)
    say("这个指数按受教育的年数与教育的回报编制")
    poor, rich, q = quarters()
    assert q == 27
    said("1960 年最穷的四分之一国家，此后平均每年增长 2.3\\%，最富的四分之一是 2.0\\%（本书的计算）", PWT_FIRST, poor, rich)
    D = pwt().sort_values("lny0")
    top = D.iloc[-30:]
    b, _ = ols([top["lny0"].to_numpy()], top["g"].to_numpy())
    assert abs(100 * b[1]) < 0.1 and list(top.loc[top["g"] < 0, "code"]) == ["VEN"]
    said("只看 1960 年最富的 30 个国家，系数也几乎为零，其中的委内瑞拉此后人均收入下降（本书的计算）", PWT_FIRST, len(top))
    said("收敛的检验，111 个国家，1960—2019 年（本书的计算）", len(D), PWT_FIRST, PWT_LAST)
    said("横轴是 1960 年人均实际 GDP 的对数", PWT_FIRST)
    # Pritchett
    has("pr_title2", "Divergence, Big Time")
    has("pr_date", "Background paper for World Development Report 1995", "October 1995")
    r70, y70p, r60, y60, r85, y85 = F["pr_ratio"]
    said("按 Pritchett（1995）为世界银行写的工作论文，最富国与最穷国人均收入之比，1870 年是 8.7，1960 年是 38，1985 年是 51",
         F["pr_date"][1], y70p, r70, y60, r60, y85, r85)
    floor, y85b = F["pr_floor"]
    assert y85b == y85
    said("他假定穷国的人均 GDP 不会低于按 1985 年购买力平价计的 250 美元", y85, floor)
    s0, s1, six, sd0, sd1 = F["pr_sixfold"]
    assert (s0, s1) == (y70p, y85) and abs(r85 / r70 - six) < 0.5
    said("按他的估计，1870—1985 年这个比扩大到约六倍，各国对数人均收入的标准差增加了 60\\% 到 100\\%", s0, s1, sd0, sd1)
    assert told("这个比扩大到约六倍", "约", "倍") == six
    has("pr_dominant", "perhaps the dominantfeature of modem economichistory")
    has("pr_compatible", "absolutedivergenceis compatiblewith conditionalconvergence")
    # the second comparison and the pitfall
    said("1870 年生产率越高，此后增长越慢", y0)
    said("Maddison 的 16 个工业国", F["bm_16"][0])
    said("约 100 个国家，战后", F["br_uncorrelated"][0])
    said("斜率$-0.75$，$R^{2}$为 0.88", -slope, r2)
    said("每年约 2\\%\\cite{bsm1990,mrw1990}", F["bs_countries"][0])
    has("bm_seriously", "The high correlation should not be taken too seriously.")
    has("bm_backward", "the 1870 figures were calculated by Maddison using backward extrapolation of growth rates")
    has("bm_spurious", "both sides of the equation", "a spurious appearance of close relationship")
    assert F["bm_backward"] == [y0]
    said("1870 年的数是倒推的，高相关不必太当真；换成 72 国几乎无关", F["bm_backward"][0], F["bm_72"][0])
    said("Baumol 自己的保留是，高相关不必太当真，1870 年的数是 Maddison 用增长率倒推出来的，初始收入又同时出现在回归的两边",
         F["bm_backward"][0])
    said("按 Pritchett 的估计，1870—1985 年各国是发散的", s0, s1)
    # the Soviet Union
    has("ef_extensive", "defined by Ofer (1987) as growth mainly through input accumulation",
        "a key feature of extensive growth is a rising capitaloutput ratio")
    said("按他们的转述，这是 Ofer（1987）的说法，指主要靠积累投入、不靠提高生产率的增长，它的一个关键特征是资本—产出比上升",
         F["ef_extensive"][0])


def case(F, Y, Q):
    T = F["ef_t1_y"]
    K = F["ef_t1_k"]
    assert T[0::3] == K[0::3] and T[1::3] == K[1::3]
    has("ef_t1_head", "Growth Rates in the Soviet Economy", "Western data")
    said("苏联 · 1950—1987 · 高投资与增长放缓", T[0], 1900 + T[-2])
    say("苏联整个时期的三种增长估计在\\chref{ch:soviet}（\\tabref{tab:soviet-growth}），1932—1933 年的饥荒也在那里")
    say("这里按十年看每个工人的数")
    COVERED.append("1932—1933 年的饥荒也在那里")                                    # EVENTS: Chapter 31 tells it
    said("按 Easterly 与 Fischer（1995）用的西方数据，每个工人的产出 1950—1959 年每年增长 5.8\\%，1980—1987 年只有 1.4\\%",
         F["ef_title"][1], T[0], 1900 + T[1], T[2], T[9], 1900 + T[10], T[11])
    said("每个工人的资本同期每年增长 7.4\\% 与 4.0\\%", K[2], K[11])
    has("ef_doubled", "The Soviet investment share doubled", "the Western estimates")
    said("他们说，按西方的估计，苏联投资的份额 1950—1975 年翻了一番", *F["ef_doubled"])
    has("ef_unusual", "Soviet growth was declining while its investment was rising")
    has("ef_ky", "The K-Y ratio as measured by the Western GDP and total capital stock series was 4.9 in 1985")
    said("1985 年的资本—产出比是 4.9", F["ef_ky"][1], F["ef_ky"][0])
    # the study for the Joint Economic Committee
    has("jec_title", "Measures of Soviet Gross National Product in 1982 Prices",
        "A Study Prepared for the Use of the Joint Economic Committee")
    has("jec_date", "NOVEMBER 1990")
    has("jec_author", "Laurie Kurtzweg, an analyst with the CIA")
    has("jec_analysts", "prepared for the committee by analysts of the Central Intelligence Agency")
    assert F["jec_print"] == [101, 2]
    said("1990 年，美国国会联合经济委员会印行了该局分析员 Kurtzweg 按 1982 年价格估计苏联国民生产总值的研究",
         F["jec_date"][0], F["jec_title"][0])
    head = F["jec_t2_head"]
    assert head[0] == 2 and head[3] == F["jec_title"][0] and head[4:6] == [1951, 65]
    has("jec_t2_head", "Based on 1982 factor cost", "Average annual")
    said("按这项估计，1951—1965 年，国民生产总值每年增长 5.1\\%，消费 4.6\\%，投资 9.6\\%", head[4], 1900 + head[5],
         F["jec_t2_gnp"][0], F["jec_t2_cons"][0], F["jec_t2_inv"][0])
    has("jec_competition", "Competition intensified among the major claimants on GNP—investment, defense, and consumption",
        "after the mid-1970s")
    has("jec_priorities", "remained much the same", "in current prices")
    said("按 Kurtzweg 的研究，1970 年代中期以后增长放慢，投资、国防与消费争夺资源，“莫斯科的优先次序看来变化很小”，三者按当年价格"
         "在国民生产总值中的份额 1970 年以后大致不变", F["jec_competition"][0], F["jec_priorities"][1])
    has("jec_living", "The standard of living of the population continued to rise",
        "the rate of improvement slowed markedly after 1975")
    assert F["jec_planners"][0] == F["jec_living"][0]
    said("“计划者让投资的增长在 1975 年以后显著放慢”，居民的生活水平仍在提高，提高的速度却明显放慢", F["jec_planners"][0])
    c1, a0, a1, c0, b0, b1 = F["jec_percapita"]
    has("jec_percapita", "Annual growth of per capita consumption")
    said("人均消费的增长从 1966—1975 年的每年 3.3\\% 降到 1976—1987 年的 1.3\\%", b0, 1900 + b1, c0, a0, 1900 + a1, c1)
    say("投资与国防的份额由莫斯科定，消费的放慢由居民承受（本书的解读）")
    # Easterly and Fischer's reading
    has("ef_t4_alpha", "a capital share of 0.4 across economies")
    assert tfp(T[11], K[11], F["ef_t4_alpha"][0]) < 0
    said("资本份额取他们比较各国时用的 0.4，按科布—道格拉斯函数读，1980—1987 年全要素生产率的增长是负的", F["ef_t4_alpha"][0],
         T[9], 1900 + T[10])
    has("ef_ref_weitzman", "Soviet Postwar Economic Growth and Capital-Labor Substitution")
    has("ef_weitzman", "a CES production function with a low elasticity of substitution")
    (c5,) = F["ef_t6_sigma"]
    tf = F["ef_t6_tfp"]
    assert all(abs(x - 1.1) < 0.07 for x in tf)
    said("替代弹性衡量资本与劳动互相替代的难易，科布—道格拉斯函数的替代弹性是 1", 1)
    said("他们沿着 Weitzman（1970）的思路，估计替代弹性不变的生产函数，替代弹性只有 0.37，各个十年的全要素生产率都在每年 1.1\\% 左右",
         F["ef_ref_weitzman"][0], -c5, float(np.mean(tf)))
    has("ef_entirely", "extensive growth—diminishing returns to capital—accounts entirely for the growth slowdown")
    has("ef_best", "the best application of the Solow (1956) neoclassical model ever seen")
    said("按他们的转述，Weitzman（1990）把苏联的增长说成索洛（1956）的新古典模型见过的最好的应用", F["ef_best"][0],
         F["ef_best"][2])
    # the figure
    said("按 1982 年要素成本，即扣除间接税、加上补贴以后的价格", head[3])
    has("ef_t1_head", "Table 1.")
    said("数据：(a) Easterly 与 Fischer（1995）表 1；(b) 美国国会联合经济委员会（1990）表 2", F["ef_title"][1],
         F["ef_t1_head"][0], F["jec_date"][0], head[0])
    # ex:solow-soviet
    a = EF_ALPHA
    assert a == F["ef_t4_alpha"][0]
    said("用案例里 Easterly 与 Fischer 表 1 的数", F["ef_t1_head"][0])
    said("（1）资本份额取 0.4，按式~\\eqref{eq:solow-accounting}，1950—1959 年与 1980—1987 年的全要素生产率各增长多少？", a,
         T[0], 1900 + T[1], T[9], 1900 + T[10])
    said("（1）$5.8-0.4\\times7.4=2.84\\%$，$1.4-0.4\\times4.0=-0.2\\%$（本书的计算）", T[2], a, K[2], tfp(T[2], K[2], a),
         T[11], a, K[11], -tfp(T[11], K[11], a))
    gaps = [k - y for y, k in zip(T[2::3], K[2::3])]
    assert all(g > 0 for g in gaps)
    said("（2）两个时期资本都比产出每年快约 1.6 到 2.6 个百分点，资本—产出比一直上升", gaps[0], gaps[3])


def debate(F, Y, Q):
    say("第一个争论是索洛余量量的是什么。技术一方有索洛与阿布拉莫维茨")
    _, _, y67 = F["jg_reprint"]
    has("jg_reprint", "The Explanation of Productivity Change", "Reprinted with corrections from The Review of Economic "
        "Studies")
    said("1967 年提出相反的假说", y67)
    has("jg_hypothesis", "growth in total output is largely explained by growth in total input")
    has("jg_relabel", "Simply relabelling these changes as Technical Progress or Advance of Knowledge")
    has("jg_incorrect", "arise from incorrect aggregation")
    has("jg_investment", "an error in the measurement of the price of investment goods")
    e0, e1 = F["jg_economy"]
    t0, t1 = F["jg_160"]
    twenty, j0, j1 = F["jg_1945"]
    assert (e0, e1) == (j0, 1900 + j1) and e1 - e0 == twenty
    has("jg_economy", "U.S. PRIVATE DOMESTIC ECONOMY")
    said("按他们的估计，美国私人国内经济 1945—1965 年全要素生产率的增长，修正以后从每年 1.6\\% 降到 0.1\\%", e0, e1, t0, t1)
    has("dn_title", "An Examination of Estimates by Jorgenson and Griliches")
    has("dn_010", "only 0.10 percentage points", "much larger amounts obtained in virtually all other studies")
    assert F["dn_010"][0] == t1                                                  # the second witness of 0.1
    has("dn_1945", "Use of 1945 as a starting point minimizes their figure.")
    said("丹尼森 1969 年反驳说，他们修正以后的数与几乎所有别的研究得到的大得多的数相反，以 1945 年为起点也把这个数压到了最低",
         F["dn_1969"][0], F["dn_1945"][0])
    has("dn_137", "in Why Growth Rates Differ")
    has("dn_period", "refers to the period from 1950 to 1962", "For this timespan, Jorgenson and Griliches obtain 0.30",
        "the difference in time period is responsible for 0.20 points")
    p137, p0, p1, jg5062, jg4565, q0, q1, period = F["dn_period"]
    assert p137 == F["dn_137"][0] and jg4565 == t1 and (q0, 1900 + q1) == (e0, e1)
    assert np.isclose(jg5062 - jg4565, period)                                  # the period explains 0.20 of 1.27
    said("他自己在《增长率为什么不同》里得到的是 1.37 个百分点，那是 1950—1962 年的数", p137, p0, p1)
    said("他说，同一时期乔根森与格里利克斯得到 0.30，时期的不同只解释两人差距中的 0.20 个百分点", jg5062, period)
    has("jg_knowledge", "not that advances in knowledge are negligible", "governed by the same economic laws")
    has("jg_replytitle", "Issues in Growth Accounting: A Reply to Edward F. Denison")
    has("scb_reply", "come closer to the concepts and methodology advocated by Denison", "substantial differences remain")
    said("按美国经济分析局 1972 年的说明", Y["scb_reply"])
    has("nb_embodiment", "the embodiment model should have fit the facts significantly better", "But it did not.")
    has("nb_noexplanatory", "no explanatory value in the embodiment idea")
    has("nb_engine", "technology remains the dominant engine of growth, with human capital investment in second place")
    has("nb_believe", "One does not have to believe in the accuracy of these numbers")
    said("他 1987 年引丹尼森的估计说，技术仍是增长的主要动力，人力资本投资居第二", F["nb_title"][1])
    # the second debate
    said("Baumol 的 16 国收敛得很快", F["bm_16"][0])
    has("mrw_social", "capital receives approximately its social return")
    has("mrw_externalities", "there are not 27 substantial externalities to the accumulation of physical capital")
    has("dl_forces", "counterbalanced by forces making for \"divergence\"")
    has("dl_concede", "Convergence does sometimes happen. Technology is a public good.")
    # the third debate
    has("ef_causes2", "the defense burden", "the absence of appropriate incentives")
    has("ef_caveats", "conditional on assumptions")
    has("ef_khanin", "some support in the official data for the low-elasticity hypothesis but none in Khanin's data")
    has("ef_debated", "hotly debated")
    has("ef_bergson", "implausibly high estimates of the marginal product of capital in earlier years")
    said("Bergson（1983）的批评是，它隐含早年过高的资本边际产品", F["ef_bergson"][0])
    has("ef_rd", "spending increasing R&D resources and borrowing Western technology")
    said("他们认为，苏联在 1970 年代与 1980 年代投入的研发资源越来越多", *F["ef_rd"])
    has("ef_compelling", "We cannot see a compelling story")
    has("ef_why", "under an autocratically directed economic system", "a narrow rather than a broad range of capital goods")


def deeper(F, Y, Q):
    for key in ("solow1956", "solow1957", "harrod1939", "phelps1961", "baumol1986"):
        assert "Thomas Piketty" in version(key) and "read to verify, not committed" in version(key), key
    said("索洛（1956、1957）、哈罗德（1939）、菲尔普斯（1961）与 Baumol（1986）据皮凯蒂在巴黎经济学院网站上放的 JSTOR 本，只用来核对",
         F["s56_title"][2], F["s57_title"][2], F["hr_title"][2], F["ph_title"][2], F["bm_title"][2])
    assert "archive.org" in version("swan1956")
    said("斯旺（1956）据互联网档案馆的《经济纪录》缩微胶片扫描本", F["sw_issue"][0])
    said("阿布拉莫维茨（1956）据 NBER 网站上的第 52 号不定期论文", F["ab_op52"][1], F["ab_op52"][0])
    vol9, y95, no3, _ = F["ef_title"]
    said("Easterly 与 Fischer 据世界银行网站上《世界银行经济评论》1995 年第 9 卷第 3 期的 PDF", y95, vol9, no3)
    assert "May 1972" in version("scb1972")
    has("jg_reprint", "Reprinted with corrections")
    said("乔根森与格里利克斯（1967）与丹尼森（1969）据美国经济分析局网站上《当代商业概览》1972 年 5 月第二部分的重印本",
         F["jg_reprint"][2], F["dn_1969"][0], 1972, MONTHS["may"])
    has("dn_1969", "as published in the May 1969 SURVEY")
    said("“刀刃”是索洛（1956）对哈罗德—多马思路的概括，本书在哈罗德 1939 年的文章里没有找到这个词", F["s56_title"][2],
         F["hr_title"][2])
    said("“我们无知的度量”见于阿布拉莫维茨（1956），乔根森与格里利克斯（1967）说这是余量已有的名字之一", F["ab_op52"][1],
         F["jg_reprint"][2])
    said("斯旺的扫描本把技术进步的“½ per cent”读作“4 per cent”", 4)
    said("索洛（1957）的总结里，87.5\\% 读作“87'2”", F["s57_title"][2], F["s57_summary"][0], 87, 2)
    said("他的表 1 与 Easterly 与 Fischer 的表也有读错的数", 1)
    has("s56_ag", "The eventual rate of increase of real output is n + ag/b.")
    has("s56_kyg", "the capital coefficient K/Y grows at rate n + g/b - n - ag/b = g")
    said("索洛（1956）第 85—86 页说，加上中性技术进步以后，产出的增长率最终是$n+ag/b$，$b=1-a$，资本—产出比每年增长$g$",
         F["s56_title"][2], page("s56_ag"), page("s56_kyg"), 1)
    say("按他自己的生产函数，产出与资本都按$n+g/b$增长，资本—产出比不变，他的$n+ag/b$正好少了技术进步本身的$g$（本书的计算）")
    has("ef_t6_sigma", "Table 6.", "Elasticity of substitution (c5) −0.37")
    has("ef_t6_eq", "(6) ln(Y/L)")
    (c5,) = F["ef_t6_sigma"]
    said("Easterly 与 Fischer 的表 6 把$c_5$一行标作替代弹性，印的是$-0.37$；按他们的式 (6)，替代弹性是$-c_5$，即 0.37（本书的计算）",
         6, -c5, 6, -c5)
    r85, t85 = F["pr_ratio"][4], F["pr_t_1985"][-1]
    assert r85 != t85 and abs(r85 - t85) < 1
    has("pr_t_1985", "Ratio of GDP per capita of richest to poorest country")
    said("Pritchett 正文说 1985 年的比是 51，表里是 51.6", F["pr_ratio"][5], r85, t85)
    say("诺贝尔奖网站上的演讲稿把“eighth”写作“eight”")
    said("国会图书馆斯旺的记录，出生日期一栏写 1818 年，标目与来源注都是 1918 年", F["loc_swan_born"][0], F["loc_swan"][0])
    assert F["loc_swan_born"][0] + 100 == F["loc_swan"][0] == F["loc_swan_note"][1]
    said("索洛 1909—1949 年的数、斯旺的数字例子、哈罗德的方程与数字，都只有作者自己的文本", F["s57_t1_1909"][0],
         F["s57_t1_1949"][0])
    said("丹尼森 1929—1982 年的分解只据索洛的转述，《增长率为什么不同》里的数只据丹尼森 1969 年的文章", F["nb_denison"][0],
         F["nb_denison"][1], F["dn_1969"][0])
    has("ef_t1_source", "Gomulka and Schaffer (1991)")
    said("苏联的增长率有 Easterly 与 Fischer 和联合经济委员会两处，前者的表 1 引的是 Gomulka 与 Schaffer（1991）",
         F["ef_t1_head"][0], F["ef_t1_source"][0])
    said("多马（1946）的原文没有取得，只核对了《计量经济学》第 14 卷的目录", *F["dm_volume"])
    said("Weitzman（1970）的工作论文版本在耶鲁大学的网站上，网站要求通过 Cloudflare 的人机验证，本书没有取得",
         F["ef_ref_weitzman"][0])
    said("Pritchett 后来在《经济展望杂志》上的同名文章，网站拒绝访问，正文用 1995 年的工作论文", F["pr_date"][1])
    # the workbook's own flags (sheet Legend: i_outlier for pl_gdpe or pl_gdpo, i_xr estimated or market-based)
    raw = load_snapshot("pwt1001_convergence", keep_default_na=False)[0].set_index("countrycode")
    out = {c: [int(y) for y in v.split(";")] for c, v in raw["i_outlier_years"].items() if v}
    assert out["MLT"] == list(range(1960, 1965)) and out["VEN"] == list(range(2015, 2020))
    assert raw.loc["MLT", "csh_i_1960"] > 1 and raw.loc["MLT", "csh_i_1961"] > 1
    xr = raw[(raw["i_xr_1960"] == "Estimated") | (raw["i_xr_2019"] == "Estimated")]
    assert raw.loc["ROU", "i_xr_1960"] == "Estimated" and raw.loc["VEN", "i_xr_2019"] == "Estimated"
    assert set(raw["i_xr_1960"]) | set(raw["i_xr_2019"]) == {"Estimated", "Market-based"}
    said("样本里有 10 个国家的价格水平在某些年份被标为异常值，其中有马耳他 1960—1964 年与委内瑞拉 2015—2019 年",
         len(out), 1960, 1964, 2015, 2019)
    said("马耳他 1960 年与 1961 年的投资份额还高于 GDP", PWT_FIRST, PWT_FIRST + 1)
    said("有 5 个国家 1960 年或 2019 年的汇率是估计的，其中有罗马尼亚 1960 年与委内瑞拉 2019 年", len(xr), PWT_FIRST,
         PWT_LAST, PWT_FIRST, PWT_LAST)
    say("本书照用这些数，没有剔除。")


def legacy(F, Y, Q):
    has("ef_krugman", "a metaphor for the alleged future growth slowdown in East Asia")
    said("按 Easterly 与 Fischer 的转述，Krugman（1994）把苏联增长意外的放缓当作比喻，说的是所谓东亚将来的增长放缓",
         F["ef_krugman"][0])
    said("Barro 与 Sala-i-Martin 的资本份额 0.8 与 1 的差别就在这里", F["bs_alpha1"][0], F["bs_alpha1"][1])
    D = pwt().sort_values("lny0")
    fast = D[D["g"] > 0.04]
    assert set(fast["code"]) == {"TWN", "KOR", "BWA", "SGP", "MLT", "THA", "CHN", "HKG", "ROU"}
    assert list(fast.sort_values("g", ascending=False)["code"]) == ["TWN", "KOR", "BWA", "SGP", "MLT", "THA", "CHN",
                                                                    "HKG", "ROU"]
    said("1960—2019 年人均增长率每年超过 4\\% 的有 9 个经济体，即中国台湾、韩国、博茨瓦纳、新加坡、马耳他、泰国、中国大陆、中国香港与罗马尼亚"
         "（本书的计算）", PWT_FIRST, PWT_LAST, 4, len(fast))
    q = quarters()[2]
    poorest = D.iloc[:q]
    assert set(poorest.loc[poorest["g"] > 0.04, "code"]) == {"KOR", "THA", "CHN", "BWA"}
    behind = int((poorest["g"] < quarters()[1] / 100).sum())                      # slower than the richest quarter
    said("其中韩国、泰国、中国大陆与博茨瓦纳 1960 年在最穷的四分之一里，同一组的 27 个国家却有 13 个增长得比最富的四分之一的平均速度慢，"
         "差距反而拉大了", PWT_FIRST, q, behind)


def takeaways(F, Y, Q):
    said("索洛与斯旺 1956 年让资本与劳动可以替代，刀刃消失了", F["s56_title"][2])
    said("稳态附近的收敛速度约为$(1-\\alpha)(n+g+\\delta)$，资本份额三分之一时差距约 17 年缩小一半", 1,
         math.log(2) / speed(ALPHA, NGD))
    said("索洛（1957）算出美国 1909—1949 年每个工时的产出翻了一番，约八分之七归于技术变化", F["s57_title"][2],
         F["s57_t1_1909"][0], F["s57_t1_1949"][0])
    said("绝对收敛在长期与全世界的样本里不成立，条件收敛的速度每年约 2\\%", F["bs_countries"][0])
    say("余量、收敛与苏联放缓的原因，至今没有定论")


def selfcheck(F, Y, Q):
    said("用式~\\eqref{eq:solow-steady}，$\\alpha=1/3$，$n+g+\\delta=6\\%$，储蓄率 15\\% 时每个有效工人的资本与产出是多少？", 1, 3,
         100 * NGD, 100 * SC_S)
    said("按式~\\eqref{eq:solow-speed}，$\\alpha=0.8$、$n+g+\\delta=9\\%$时，半衰期是多少年？", SC_SPEED[0], 100 * SC_SPEED[1])
    gy, gk, a = SC_TFP
    said("某国每个工人的产出每年增长 3\\%，每个工人的资本每年增长 4\\%，资本份额 0.35", gy, gk, a)
    k, y = steady(SC_S)
    r = SC_S / NGD
    said("$k=(0.15/0.06)^{1.5}=2.5^{1.5}\\approx3.95$，$y=2.5^{0.5}\\approx1.58$", SC_S, NGD, 1 / (1 - ALPHA), r,
         1 / (1 - ALPHA), k, r, ALPHA / (1 - ALPHA), y)
    e2 = SC_ALPHA2 / (1 - SC_ALPHA2)
    assert np.isclose(told("资本份额从三分之一提高到二分之一", "提高到", ""), SC_ALPHA2)
    said("弹性从$1/2$变为 1，翻一番时产出从增加约 41\\% 变为增加 100\\%", 1, 2, e2,
         100 * (2 ** (ALPHA / (1 - ALPHA)) - 1), 100 * (2 ** e2 - 1))
    lam = speed(*SC_SPEED)
    said("$\\lambda=0.2\\times9\\%=1.8\\%$，半衰期$0.693/0.018\\approx39$ 年", 1 - SC_SPEED[0], 100 * SC_SPEED[1], 100 * lam,
         math.log(2), lam, math.log(2) / lam)
    said("$3\\%-0.35\\times4\\%=1.6\\%$", gy, a, gk, tfp(gy, gk, a))


def ending(F, Y, Q):
    said("回到 1987 年 12 月的斯德哥尔摩", F["nb_title"][1], mon("nb_title", "December"))
    say("多储蓄能把人均产出抬到更高的水平，却不能让它永远增长得更快，代价是眼前少消费")
    say("下一章的发展经济学从劳动过剩与二元经济讲起")
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 41's question"
    assert t.index("\\end{answers}") < t.index("回到 1987 年 12 月的斯德哥尔摩")
    assert f"\\guidequestion{{{NEXT}}}" in (ROOT / "zh" / "ch41_development.tex").read_text(encoding="utf-8")


def models() -> None:
    """The key equations as printed, and the claims the text makes of them, checked with random numbers."""
    t = TEX.read_text(encoding="utf-8")
    eqs = {lab: body.strip() for body, lab in re.findall(r"\\begin\{keyeq\}\n(.*?)\\label\{(eq:[^}]+)\}", t, re.DOTALL)}
    assert sorted(eqs) == ["eq:solow-accounting", "eq:solow-accumulation", "eq:solow-steady"], sorted(eqs)
    assert eqs["eq:solow-accumulation"] == "\\Delta k=s\\,k^{\\alpha}-(n+\\delta)\\,k .", eqs
    assert eqs["eq:solow-steady"] == ("k^{*}=\\Bigl(\\frac{s}{n+\\delta}\\Bigr)^{\\frac{1}{1-\\alpha}},\\qquad "
                                      "y^{*}=\\Bigl(\\frac{s}{n+\\delta}\\Bigr)^{\\frac{\\alpha}{1-\\alpha}} ."), eqs
    assert eqs["eq:solow-accounting"] == "g_Y=\\alpha\\,g_K+(1-\\alpha)\\,g_L+g_A ,", eqs
    eqn = {lab: body.strip() for body, lab in re.findall(r"\\begin\{equation\}\n(.*?)\\label\{(eq:[^}]+)\}", t, re.DOTALL)}
    assert eqn == {"eq:solow-speed": "\\lambda\\approx(1-\\alpha)(n+g+\\delta),"}, eqn
    # the transcriptions the text renders
    assert "G_w = s/C" in transcription("hr_eq") and "ṙ = sF(r,1) − nr" in transcription("s56_eq6")
    assert "Y = K^α N^β" in transcription("sw_cobb") and "Q = A(t)f(K,L)" in transcription("s57_eq1a")
    assert "q̇/q = Ȧ/A + w_K k̇/k" in transcription("s57_eq2a")
    assert "[c5/(1+c5)] ln[c6 (K/L)^((1+c5)/c5) + (1−c6)]" in transcription("ef_t6_eq")
    rng = np.random.default_rng(40)
    for _ in range(200):
        a, s, ngd = rng.uniform(0.1, 0.9), rng.uniform(0.02, 0.6), rng.uniform(0.02, 0.15)
        k, y = steady(s, a, ngd)
        # eq:solow-steady solves eq:solow-accumulation with Delta k = 0, and it is stable from both sides
        assert np.isclose(s * k ** a, ngd * k) and np.isclose(y, k ** a)
        for k0 in (0.5 * k, 1.5 * k):
            assert np.sign(s * k0 ** a - ngd * k0) == np.sign(k - k0)
        # the elasticities of y* with respect to s and n + g + delta: alpha/(1-alpha) and its negative
        e = a / (1 - a)
        assert np.isclose(math.log(steady(1.01 * s, a, ngd)[1] / y) / math.log(1.01), e)
        assert np.isclose(math.log(steady(s, a, 1.01 * ngd)[1] / y) / math.log(1.01), -e)
        # the golden rule: consumption (1 - s) y*(s) is largest at s = alpha; above it, less saving raises it
        assert consumption(a, a, ngd) >= max(consumption(x, a, ngd) for x in np.linspace(0.01, 0.99, 99)) - 1e-12
        if s > a + 0.01:
            assert consumption(s - 0.01, a, ngd) > consumption(s, a, ngd)
            assert (1 - (s - 0.01)) * y > (1 - s) * y                               # and at once, from the same output
        # eq:solow-speed: the linearised speed is the slope of the log gap near the steady state; a larger share,
        # a slower convergence
        kk = k * 1.001
        kn = kk + s * kk ** a - ngd * kk
        assert np.isclose(1 - math.log(kn / k) / math.log(kk / k), speed(a, ngd), rtol=0.02, atol=1e-4)
        assert speed(min(a + 0.05, 0.99), ngd) < speed(a, ngd)
    # growth accounting: with Q = A K^w L^(1-w), the residual of eq:solow-accounting is the growth of A
    for _ in range(100):
        w, ga, gk, gl = rng.uniform(0.1, 0.6), *rng.uniform(-0.02, 0.05, 3)
        gq = ga + w * gk + (1 - w) * gl
        assert np.isclose(gq - w * gk - (1 - w) * gl, ga)
        assert np.isclose(tfp(gq - gl, gk - gl, w), ga)                           # per worker, as the text writes it
    # two-factor productivity: Y = A K^b X^a L^(1-a-b) read as y = At (X/L)^a gives dln At = dln A + b dln k
    for _ in range(100):
        a, b = rng.uniform(0.05, 0.4, 2)
        A0, A1, K0, K1, X, L0, L1 = rng.uniform(0.5, 2, 7)
        y = [A * K ** b * X ** a * L ** (1 - a - b) / L for A, K, L in ((A0, K0, L0), (A1, K1, L1))]
        At = [yy / (X / L) ** a for yy, L in zip(y, (L0, L1))]
        assert np.isclose(math.log(At[1] / At[0]), math.log(A1 / A0) + b * math.log((K1 / L1) / (K0 / L0)))
    # Solow (1956), p. 85: with Y = e^{gt} K^a L^b, b = 1 - a, the balanced path has Y and K growing at n + g/b and a
    # constant K/Y, not n + ag/b
    a, gtech, n, s = 0.3, 0.015, 0.01, 0.2
    b = 1 - a
    K, L, dt = 1.0, 1.0, 0.05
    for i in range(int(800 / dt)):
        Y = math.exp(gtech * i * dt) * K ** a * L ** b
        K, L = K + s * Y * dt, L * math.exp(n * dt)
    T = 800
    Y1 = math.exp(gtech * T) * K ** a * L ** b
    K2, L2 = K + s * Y1 * dt, L * math.exp(n * dt)
    Y2 = math.exp(gtech * (T + dt)) * K2 ** a * L2 ** b
    gY, gK = math.log(Y2 / Y1) / dt, math.log(K2 / K) / dt
    assert abs(gY - (n + gtech / b)) < 1e-3 and abs(gK - gY) < 1e-3 and abs(gY - (n + a * gtech / b)) > 0.005
    # Easterly and Fischer's (6): the exponent (1 + c5)/c5 is rho of the CES function, the elasticity 1/(1 - rho) = -c5
    for c5 in (-0.37, -0.2, -0.8):
        rho = (1 + c5) / c5
        assert np.isclose(1 / (1 - rho), -c5)
    # with a low elasticity the marginal product of capital falls faster as K/L rises than with Cobb-Douglas
    c5, c6 = -0.37, 0.5
    rho = (1 + c5) / c5

    def ces(kl: float) -> float:
        return (c6 * kl ** rho + 1 - c6) ** (1 / rho)

    def mpk(f, kl: float) -> float:
        return (f(kl * 1.0001) - f(kl)) / (kl * 0.0001)

    cd = lambda kl: kl ** 0.5                                                    # noqa: E731
    assert mpk(ces, 2) / mpk(ces, 1) < mpk(cd, 2) / mpk(cd, 1)
    print("ok the key equations as printed; the steady state, the golden rule, the speed of convergence, growth "
          "accounting and the CES reading on random numbers")


def figures_data() -> None:
    """What the figures assert of their data."""
    D = diagram()
    k0, k1 = steady(S0)[0], steady(S1)[0]
    i0, i1 = np.argmin(abs(D["save0"] - D["need"]).iloc[1:]) + 1, np.argmin(abs(D["save1"] - D["need"]).iloc[1:]) + 1
    assert abs(D["k"].iloc[i0] - k0) < 0.1 and abs(D["k"].iloc[i1] - k1) < 0.1 and D["k"].max() > k1
    T = transition()
    assert np.isclose(T["lny"].iloc[0], 0) and np.isclose(T["lny_old"].iloc[0], 0)
    assert abs(T["growth"].iloc[0] - 4) < 0.1 and abs(T["growth"].iloc[-2] - 100 * G) < 0.1
    P = convergence_points()
    assert len(P) == len(pwt()) and np.isclose(P["net"].mean(), P["g"].mean())
    S = soviet()
    assert len(S["y"]) == len(S["k"]) == len(S["periods"]) == 4 and len(S["gnp"]) == len(S["t2"]) == 6
    assert all(k > y for y, k in zip(S["y"], S["k"])) and S["y"] == sorted(S["y"], reverse=True)


# ---------------------------------------------------------------------------------------------------
# 5. The book
# the life dates: words -> (row of the birth year, index), (row of the death year, index), row of the heading, heading
LIVES = {"Robert M. Solow，1924—2023": (("loc_solow_born", 1), ("gnd_solow_died", 0), "loc_solow", "Solow, Robert M."),
         "W. Arthur Lewis，1915—1991": (("loc_lewis", 0), ("loc_lewis", 1), "loc_lewis", "Lewis, W. Arthur"),
         "Trevor W. Swan，1918—1989": (("loc_swan", 0), ("loc_swan", 1), "loc_swan", "Swan, Trevor Winchester"),
         "Edmund S. Phelps，1933—2026": (("gnd_phelps_born", 0), ("gnd_phelps_died", 0), "loc_phelps",
                                        "Phelps, Edmund S."),
         "Joan Robinson，1903—1983": (("loc_robinson", 0), ("loc_robinson", 1), "loc_robinson", "Robinson, Joan"),
         "Moses Abramovitz，1912—2000": (("loc_abramovitz_note", 0), ("loc_abramovitz_note", 2), "loc_abramovitz",
                                        "Abramovitz, Moses"),
         "Edward F. Denison，1915—1992": (("loc_denison", 0), ("loc_denison", 1), "loc_denison", "Denison, Edward F."),
         "Zvi Griliches，1930—1999": (("loc_griliches", 0), ("loc_griliches", 1), "loc_griliches", "Griliches, Zvi")}
# the life dates other chapters' records give: words -> ((snapshot, row, index) of the birth year, of the death year)
THEIR_LIVES = {"Roy Harrod，1900—1978": (("islm_facts", "loc_harrod", 0), ("islm_facts", "loc_harrod", 1)),
               "Evsey D. Domar，1914—1997": (("warfinance_facts", "gnd_domar_born", 0),
                                            ("warfinance_facts", "gnd_domar_died", 0)),
               "Dale W. Jorgenson，1933—2022": (("consumption_facts", "loc_jorgenson", 0),
                                               ("consumption_facts", "gnd_jorgenson_died", 0))}
# where two records have a date, they agree: (row, index) pairs
AGREE = [(("gnd_solow_born", 0), ("loc_solow_born", 1)), (("gnd_solow_born", 2), ("loc_solow_born", 0)),
         (("nf_born", 0), ("loc_solow_born", 0)), (("nf_born", 1), ("loc_solow_born", 1)),
         (("nf_died", 0), ("gnd_solow_died", 2)), (("nf_died", 1), ("gnd_solow_died", 0)),
         (("loc_solow_died", 1), ("gnd_solow_died", 2)), (("loc_solow_wapo", 1), ("gnd_solow_died", 0)),
         (("gnd_swan_born", 0), ("loc_swan", 0)), (("gnd_swan_died", 0), ("loc_swan", 1)),
         (("loc_swan_note", 1), ("loc_swan", 0)), (("loc_swan_note", 2), ("loc_swan", 1)),
         (("loc_swan_born", 2), ("loc_swan_note", 0)),
         (("gnd_phelps_born", 1), ("loc_phelps_born", 0)), (("gnd_phelps_born", 2), ("loc_phelps_born", 1)),
         (("nf_phelps_born", 0), ("gnd_phelps_born", 2)), (("nf_phelps_born", 1), ("gnd_phelps_born", 0)),
         (("nf_phelps_died", 0), ("gnd_phelps_died", 2)), (("nf_phelps_died", 1), ("gnd_phelps_died", 0)),
         (("gnd_abramovitz_born", 0), ("loc_abramovitz_note", 0)), (("gnd_abramovitz_died", 0), ("loc_abramovitz_note", 2)),
         (("gnd_abramovitz_died", 2), ("loc_abramovitz_note", 1)),
         (("gnd_denison_born", 0), ("loc_denison", 0)),
         (("gnd_griliches_born", 0), ("loc_griliches", 0)), (("gnd_griliches_died", 0), ("loc_griliches", 1)),
         (("gnd_lewis_born", 0), ("loc_lewis", 0)), (("gnd_lewis_died", 0), ("loc_lewis", 1)),
         (("gnd_robinson_born", 0), ("loc_robinson", 0)), (("gnd_robinson_died", 0), ("loc_robinson", 1))]
# what other chapters tell: (words of this chapter, chapter where it is told, words there)
EVENTS = [("哈罗德（Roy Harrod，1900—1978）", "ch33_islm", "哈罗德（Roy Harrod，1900—1978）"),
          ("多马（Evsey D. Domar，1914—1997）", "ch34_warfinance", "多马（Evsey D. Domar，1914—1997）"),
          ("乔根森（Dale W. Jorgenson，1933—2022）", "ch39_consumption", "Dale W. Jorgenson，1933—2022"),
          ("他 1944 年关于债务负担的文章在\\chref{ch:warfinance}（\\exref{ex:warfinance-domar}）", "ch34_warfinance",
           "\\label{ex:warfinance-domar}"),
          ("按\\chref{ch:accounts}的式~\\eqref{eq:accounts-capital}积累", "ch02_accounts",
           "K_{t+1}=K_t+I_t-D_t,\\label{eq:accounts-capital}"),
          ("雇员报酬占 GDP 的份额 1855 年是 52.9\\%，1913 年是 54.4\\%（\\figref{fig:marx_uk}）", "ch22_marx",
           "占 GDP 的份额，1855 年是 52.9\\%，1913 年是 54.4\\%"),
          ("资本对产出之比在那半个世纪里没有持续上升", "ch22_marx", "资本对产出之比没有持续上升"),
          ("\\chref{ch:smith}把人均产出分成劳动生产率与有用劳动的比例（式~\\eqref{eq:smith-twofactors}）", "ch18_smith",
           "\\frac{Y}{N}=\\frac{Y}{L}\\cdot\\frac{L}{N} .\\label{eq:smith-twofactors}"),
          ("\\chref{ch:divergence}的模型只有土地与劳动，$y=\\tilde A(X/L)^{\\alpha}$", "ch21_divergence",
           "$y=\\tilde A(X/L)^{\\alpha}$"),
          ("1800—1860 年每年约 0.8\\%，就高于按三种要素算的数", "ch21_divergence",
           "比按资本、劳动与土地三种要素算的大"),
          ("苏联整个时期的三种增长估计在\\chref{ch:soviet}（\\tabref{tab:soviet-growth}）", "ch31_soviet",
           "\\caption{苏联经济增长的三种估计（每年 \\%）}\\label{tab:soviet-growth}"),
          ("各国 1960 年的收入按购买力平价比较", "ch05_external", "就是\\textbf{购买力平价}（purchasing power parity，PPP）"),
          ("1932—1933 年的饥荒也在那里", "ch31_soviet", "1932—1933 年的饥荒"),
          ("\\chref{ch:consumption}问家庭为什么储蓄，储蓄率怎样随增长变化", "ch39_consumption",
           "下一章索洛的增长模型把储蓄率当作给定，问的是储蓄能把增长推到哪里")]
# the chapters this one hands on to, and those it draws on
LATER = {"ch:consumption": "ch39_consumption", "ch:divergence": "ch21_divergence", "ch:accounts": "ch02_accounts",
         "ch:warfinance": "ch34_warfinance", "ch:development": "ch41_development", "ch:marx": "ch22_marx",
         "ch:smith": "ch18_smith", "ch:soviet": "ch31_soviet", "ch:planned": "ch43_planned",
         "ch:eastasia": "ch42_eastasia", "ch:endogenous": "ch56_endogenous", "ch:demography": "ch79_demography",
         "ch:transition": "ch59_transition", "ch:rbc": "ch53_rbc", "ch:heterogeneity": "ch71_heterogeneity",
         "ch:islm": "ch33_islm", "ch:external": "ch05_external"}
# the chapters that point here
POINTERS = ("ch11_medieval", "ch18_smith", "ch21_divergence", "ch22_marx", "ch41_development", "ch42_eastasia",
            "ch53_rbc", "ch56_endogenous")


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
        assert f"{their(nb, rb)[ib]:.0f}—{their(nd, rd)[id_]:.0f}" in words, words
        COVERED.append(words)
    for rid in ("loc_solow", "loc_phelps", "loc_abramovitz"):                     # the headings without years
        assert rid not in F and Q[rid] == {"loc_solow": "Solow, Robert M.", "loc_phelps": "Phelps, Edmund S.",
                                           "loc_abramovitz": "Abramovitz, Moses"}[rid]
    for (r1, i1), (r2, i2) in AGREE:
        assert F[r1][i1] == F[r2][i2], (r1, r2)
    assert mon("loc_solow_born", "Aug.") == mon("nf_born", "August") == F["gnd_solow_born"][1]
    assert mon("nf_died", "December") == mon("loc_solow_died", "Dec.") == F["gnd_solow_died"][1]
    assert mon("loc_swan_note", "January") == F["loc_swan_born"][1]
    assert 1900 + F["loc_phelps_born"][2] == F["gnd_phelps_born"][0] and mon("nf_phelps_died", "May") == F["gnd_phelps_died"][1]
    assert mon("loc_abramovitz_note", "Dec.") == F["gnd_abramovitz_died"][1]
    assert F["loc_abramovitz_note"][3] == F["loc_abramovitz_note"][2] - F["loc_abramovitz_note"][0]   # at age 88
    assert "gnd_denison_died" not in F                                           # the GND has no year of death
    assert "dateOfBirth" in column("juan")["gnd_swan_born"] and "dateOfDeath" in column("juan")["gnd_phelps_died"]
    for here, ch, there_ in EVENTS:
        assert here in t, here
        assert there_ in chapter(ch), (ch, there_)
    named = set(re.findall(r"\\chref\{(ch:[^}]+)\}", t))
    assert named == set(LATER), sorted(named ^ set(LATER))
    for label, ch in LATER.items():
        assert f"\\label{{{label}}}" in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (label, ch)
    for ch in POINTERS:
        assert re.search(r"\\(?:chref|ref)\{ch:solow\}", chapter(ch)), ch
    for lab, ch in (("fig:marx_uk", "ch22_marx"), ("tab:soviet-growth", "ch31_soviet"),
                    ("ex:warfinance-domar", "ch34_warfinance"), ("eq:smith-twofactors", "ch18_smith"),
                    ("eq:accounts-capital", "ch02_accounts")):
        defined = f"}}{{{lab}}}" if lab.startswith("fig:") else f"\\label{{{lab}}}"   # \fig{name}{caption}{label}
        assert f"{{{lab}}}" in t and defined in chapter(ch), lab
    print(f"ok {len(LIVES) + len(THEIR_LIVES)} life dates, {len(EVENTS)} statements of other chapters, {len(LATER)} "
          f"other chapters named")


# the bibliography item of each source of the snapshot (the authority records: loc40 and gnd40)
ITEM_OF = {"nobel_solow40": "solow1987", "nobel_facts40": "nobel1987", "nobel_phelps40": "nobel2006",
           "harrod1939img": "harrod1939", "econometrica1946img": "domar1946", "archive_idx40": "domar1946",
           "solow1956img": "solow1956", "swan1956img": "swan1956", "archive_swan40": "swan1956",
           "solow1957img": "solow1957", "ef1995img": "ef1995", "jec1990img": "jec1990", "archive_jec40": "jec1990"}


def pages(rids) -> str:
    """The printed pages of rows, as the bibliography lists them: '第 26、27、36、66 页', ranges joined by '—'."""
    ps = sorted({p for r in rids for p in range(page_span(r)[0], page_span(r)[1] + 1)})
    runs, out = [], []
    for p in ps:
        if runs and p == runs[-1][1] + 1:
            runs[-1][1] = p
        else:
            runs.append([p, p])
    for a, b in runs:
        out.append(f"{a}" if a == b else f"{a}{'、' if b == a + 1 else '—'}{b}")
    return "第 " + "、".join(out) + " 页"


def page_span(rid: str) -> tuple[int, int]:
    """The first and last printed (or PDF) page of a row's juan column."""
    j = column("juan")[rid]
    m = re.match(r"pp?\. (\d+)(?:[-–](\d+))?", j) or re.match(r"PDF pp?\. (\d+)(?:[-–](\d+))?", j)
    return int(m.group(1)), int(m.group(2) or m.group(1))


def witnesses(F, Q):
    """Second witnesses of statements of the text, the licences and the bibliography block of the chapter."""
    # the 1957 result in the lecture of 1987, and the 0.1 of Jorgenson and Griliches in Denison's article
    assert F["nb_eight"][0] == F["s57_eighth"][1] and abs(F["nb_capital12"][0] / 100 - F["s57_eighth"][0]) < 0.01
    assert F["dn_010"][0] == F["jg_160"][1]
    # the licences
    m = meta()
    lic = m["license"]
    for rid in ("nb_copyright", "ab_reprinted", "ef_copyright", "pr_series", "jec_analysts", "jec_author", "pwt_licence",
                "pwt_cite", "pwt_ref", "gnd_licence"):
        assert re.search(r"\brows? [^)]*\b" + rid + r"\b", lic), rid
        assert words_of(rid) in lic, rid
    for words in ("public domain", "Short phrases only", "the copies are not committed", "none of them prints a © notice",
                  "'© 1995 The International Bank for Reconstruction and Development / THE WORLD BANK'", "public data"):
        assert words in lic, words
    for name in ("pwt1001_convergence", "pwt1001_usa"):
        data = load_snapshot(name)[1]
        assert "'CC-BY-4.0'" in data["license"] and words_of("pwt_cite") in data["license"], name
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    start = bib.index("% ---- 第 40 章")
    following = re.search(r"^% ---- 第 \d+ 章", bib[start + 1:], re.MULTILINE)
    end = start + 1 + following.start() if following else bib.index("\\end{thebibliography}")
    block = bib[start:end]
    assert FETCH in block and bib.index("% ---- 第 39 章") < start
    items = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", block)}
    allitems = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", bib)}
    assert f"共 {len(items)} 条" in block
    for key in ("jec1990",):
        assert "公有领域" in items[key], key
    unescape = lambda s: re.sub(r"\\([$%&_#])", r"\1", s)                       # noqa: E731 - as LaTeX prints it
    assert "© The Nobel Foundation" in items["solow1987"]
    assert "© 1995 The International Bank for Reconstruction and Development / THE WORLD BANK" in items["ef1995"]
    assert words_of("pr_series") in unescape(items["pritchett1995"])
    assert words_of("gnd_licence") in unescape(items["gnd40"])
    assert "CC BY 4.0" in items["pwt1001"] and "Feenstra" in items["pwt1001"]
    for key in ("harrod1939", "solow1956", "phelps1961", "solow1957", "baumol1986", "swan1956"):
        assert "只用来核对，不随本书分发" in items[key], key
    for key in ("abramovitz1956", "delong1987", "barro1989", "bsm1990", "mrw1990"):
        assert "没有印版权声明" in items[key], key
    assert "公共数据" in items["loc40"]
    for words, (_, _, head_row, _) in LIVES.items():
        assert Q[head_row].replace("-", "--") in items["loc40"], head_row
    for rid in ("gnd_solow", "gnd_swan", "gnd_phelps", "gnd_abramovitz", "gnd_denison", "gnd_griliches", "gnd_lewis",
                "gnd_robinson"):
        assert Q[rid] in items["gnd40"], rid
    # the pages of each work, as the snapshot's rows have them
    df = _rows()
    for key, srcs in (("harrod1939", ("harrod1939", "harrod1939img")), ("solow1956", ("solow1956", "solow1956img")),
                      ("swan1956", ("swan1956", "swan1956img")), ("phelps1961", ("phelps1961",)),
                      ("solow1957", ("solow1957", "solow1957img")), ("abramovitz1956", ("abramovitz1956",)),
                      ("baumol1986", ("baumol1986",)), ("ef1995", ("ef1995", "ef1995img")),
                      ("jec1990", ("jec1990img",))):
        rids = [r.id for r in df.itertuples() if r.file in srcs and re.match(r"pp?\. \d", r.juan)]
        assert pages(rids) in items[key], (key, pages(rids))
    for key, srcs in (("delong1987", ("delong1987",)), ("barro1989", ("barro1989",)), ("bsm1990", ("bsm1990",)),
                      ("mrw1990", ("mrw1990",)), ("pritchett1995", ("pritchett1995",))):
        rids = [r.id for r in df.itertuples() if r.file in srcs and r.juan.startswith("PDF p")]
        assert "PDF " + pages(rids) in items[key], (key, "PDF " + pages(rids))
    for key, item in (("jg1967", "jg1967"), ("dn", "denison1969"), ("scb", "scb1972")):
        pass
    rids_jg = [r.id for r in df.itertuples() if r.file == "scb1972" and r.id.startswith("jg_") and r.id != "jg_replytitle"]
    rids_dn = [r.id for r in df.itertuples() if r.file == "scb1972" and r.id.startswith("dn_") and r.id != "dn_title"]
    assert "PDF " + pages(rids_jg) in items["jg1967"] and "PDF " + pages(rids_dn) in items["denison1969"]
    # every source of the snapshot, and the workbook of the data snapshots, is named by its URL in its item
    for key, s in m["sources"].items():
        if key == "scb1972":
            for item in ("jg1967", "denison1969"):
                assert s["url"] in unescape(allitems[item]), item
            continue
        item = "loc40" if key.startswith("loc_") else "gnd40" if key.startswith("gnd_") else ITEM_OF.get(key, key)
        assert s["url"] in unescape(allitems[item]), key
    assert "https://dataverse.nl/api/access/datafile/354095" in items["pwt1001"]
    keys = set(allitems)
    cited = {k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", tex_text()) for k in c.split(",")}
    assert cited <= keys, sorted(cited - keys)
    assert REUSED_KEYS <= cited and not REUSED_KEYS & set(items)
    assert set(items) == cited - REUSED_KEYS, sorted(set(items) ^ (cited - REUSED_KEYS))
    print(f"ok {len(cited)} works cited, {len(items)} in the bibliography block of Chapter 40, "
          f"{len(REUSED_KEYS)} in earlier blocks")


# the modern authors cited in Latin script
NAMES = ("Baumol|De Long|Barro|Sala-i-Martin|Mankiw|Romer|Weil|Pritchett|Easterly|Fischer|Weitzman|Bergson|Krugman|"
         "Kendrick|Goldsmith|Fabricant|Maddison|Ofer|Kurtzweg|Khanin|Kaldor|Gomulka|Schaffer|Feenstra|Inklaar|Timmer")


def counts() -> None:
    """The editor's limits: “不能” at most about a dozen; no cited modern author in Latin script as the subject of a
    sentence outside the 史料说明; the forbidden words; who chose and who paid stated; the three debates left open."""
    t = tex_text()
    main = re.sub(r"\\begin\{deeper\}\[史料说明\].*?\\end\{deeper\}", "", t, flags=re.DOTALL)
    n = t.count("不能")
    print(f"ok “不能” {n} times")
    assert n <= 12, n
    verbs = ("认为|写道|说|指出|记述|估计|承认|报道|记载|提到|列出|给出|发现|统计|算出|早有|看法|有类似|怀疑|强调|写作|推测|"
             "提出|回答|回应|证明|检验|研究|分析")
    subj = re.findall(r"(?:^|[。；：，）\n])\s*(?:按 |据 )?(?:" + NAMES + r")(?:\s*[、与和]\s*(?:" + NAMES +
                      r"))*(?: 等人| 等)?(?:（\d{4}）)?\s*(?:也|还|又|则)?(?:" + verbs + ")", main)
    assert not subj, subj
    for words in ("本书没有找到", "没能取得", "没有取得", "没有读到"):
        assert words not in main, words                                          # only in the 史料说明
    narrative = re.sub(r"“[^”]*”", "", t)                                       # the quotations render the sources
    for bad in ("这一节回答", "不是因为", "而是", "详见", "\\textsc", "\\underline", "\\clearpage"):
        assert bad not in narrative, bad
    assert not re.search(r"(?<![意看])见\\(?:chref|secref|figref|tabref|exref|eqref)", t)
    assert "\\chapterstub" not in t
    # the political character: a higher saving rate is paid for in consumption now; who chose the Soviet investment share
    # and who bore the forgone consumption
    for words in ("可多储蓄是用少消费换来的", "提高的那一年消费要减少六分之一", "少消费的是过渡期间活着的人，多消费的是以后的人",
                  "储蓄率由谁定，谁就决定了这笔账由哪几代人付", "在计划经济里，投资率由中央的计划者定",
                  "多投资由谁决定、代价由谁承担", "“莫斯科的优先次序看来变化很小”", "“计划者让投资的增长在 1975 年以后显著放慢”",
                  "居民的生活水平仍在提高，提高的速度却明显放慢", "投资与国防的份额由莫斯科定，消费的放慢由居民承受",
                  "在专制地指挥的经济里", "1932—1933 年的饥荒也在那里", "代价是眼前少消费"):
        assert words in main, words
    # the three debates of the editor's notes are left open
    for words in ("第一个争论", "第二个争论", "第三个争论"):
        assert main.count(words) == 1, words
    debates = main.split("\\subsubsection{")[-3:]
    debates[2] = debates[2][:debates[2].index("\\begin{deeper}") if "\\begin{deeper}" in debates[2] else
                            debates[2].index("\\section{")]
    for d in debates:
        assert d.rstrip().endswith("至今没有定论。"), d[-80:]
    # the inferences are marked
    assert main.count("本书的解读") >= 8 and "本书的计算" in main and "本书的概括" in main
    # sentences: one semicolon at most
    for s in re.split(r"(?<=[。？！])|\n", re.sub(r"“[^”]*”", "“”", main)):
        assert s.count("；") <= 1, s
    # the boxes the editor asks for
    assert 2 <= t.count("\\begin{compare}") <= 4 and t.count("\\begin{case}") == 1 and t.count("\\begin{pitfall}") == 1
    assert t.count("\\begin{deeper}[史料说明]") == 1 and 1 <= t.count("\\begin{keyeq}") <= 4


def main() -> None:
    df = _rows()
    F, Y, Q = facts(), years(), quotes()
    check_readings(df)
    check_text(df)
    guide(F, Y, Q)
    opening(F, Y, Q)
    world(F, Y, Q)
    model(F, Y, Q)
    transition_(F, Y, Q)
    accounting(F, Y, Q)
    check(F, Y, Q)
    case(F, Y, Q)
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
    anchors(str(TEX), set(df["id"]), script=Path(__file__))


if __name__ == "__main__":
    main()
