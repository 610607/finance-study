"""Chapter 38 (菲利普斯曲线与宏观计量模型): every number and every quotation in zh/ch38_phillips.tex.

    python3 checks/check_ch38.py

Inputs:
  phillips_facts                quotations of the chapter's sources with their page: Phillips (Economica 1958) and
                                Samuelson and Solow (AER 1960), the JSTOR scans on two university course pages; Okun
                                (1962, Cowles Foundation Paper 190) and Klein (1950, Cowles Commission Monograph 11),
                                scans without a text layer, read on the page images; the Economic Reports of the
                                President of January 1962 and February 1971 (Tables C-24 and C-45); Historical Statistics
                                of Canada (series D491-497 and K8-18) and the Statistics Canada Open Licence; Friedman's
                                Nobel lecture (1976); Fisher in the International Labour Review (1926) and the ILO's terms;
                                the Nobel pages of 1980 on Klein; the Science Museum Group's pages on Phillips's machine;
                                the Cowles Foundation's pages; the authority records of the Library of Congress, the GND
                                and the BnF. data/fetch/verify_web_quotes.py checks the quotations against the documents;
                                the rows with an empty quotation are read on page images, with a transcription between «
                                and » in the note; data/fetch/phillips38.py fetches the documents
  menu_us_canada_1946_1969      the yearly unemployment rates and consumer price indexes of the United States (ERP 1971,
                                Tables C-24 and C-45) and of Canada (Historical Statistics of Canada, D491 and K8), read
                                from the same documents by the same script
  boe_millennium_uk_1860_1958   British unemployment (the trade-union rate to 1920, Feinstein's civilian rate from 1920)
                                and Feinstein's average weekly wage earnings (Bank of England, A millennium of
                                macroeconomic data, tables A50 and A47; data/fetch/boe_millennium_gb38.py)

This script

1. reads the numbers of every row from its quotation (or from the transcription of a page image) by the rules of
   READINGS and compares them with the value column; the misreadings of the text layers are listed in MISPRINTS;
2. finds every “…” of the text among the renderings of TRANSLATIONS, and the words of the source each one renders
   (KEYWORDS) in the row;
3. checks each number of the text with said(): the phrase is in the text and each number is the value of a row, a
   teaching input, or arithmetic on them (Phillips's curve eq:phillips-curve, the price rule eq:phillips-prices, Okun's
   rule eq:phillips-okun, Klein's Model I eq:phillips-klein, the six crosses recomputed from the Bank of England's
   series, the American and Canadian series); every Arabic number of the text must lie in a phrase said() read
   (coverage());
4. checks the key equations as printed, Model I against its own closed forms on random coefficients, the data of the
   figures (figsrc/fig_ch38.py imports crosses(), menu(), klein_path() and the curve from here), the life dates
   against the authority records, what other chapters tell, the licences and the bibliography block of Chapter 38,
   and the editor's limits;
5. lists the rows no "% 据:" anchor of the text names (common.anchors).

Set CH38_TEX to a scratch copy of the chapter to run the checks on it (mutation tests).
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

TEX = Path(os.environ.get("CH38_TEX", ROOT / "zh" / "ch38_phillips.tex"))   # a scratch copy for mutation tests
GUIDE = "通胀与失业真是一张可以点菜的菜单吗？"
PREV = GUIDE                                        # Chapter 37's NEXT
NEXT = "政府一次性发钱，人们会花掉多少？企业凭什么决定投资？"   # Chapter 39's question
MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"], 1)}
FETCH = "data/fetch/phillips38.py"
# works of the bibliography that other chapters' blocks hold and this chapter cites unchanged
REUSED_KEYS = {"oxford1937", "boe2017"}
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
    df, m = load_snapshot("phillips_facts", dtype=str, keep_default_na=False)
    assert 38 in m["used_in"] and m["fetch"] == FETCH
    assert df["id"].is_unique
    return df


@lru_cache(maxsize=None)
def meta() -> dict:
    return load_snapshot("phillips_facts")[1]


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
    """The month `name` (English), asserted to be in what row rid says."""
    has(rid, name)
    return MONTHS[name.lower()]


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
         "ten": 10, "eleven": 11, "twelve": 12, "fourteen": 14, "fifteen": 15}
TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
WORDS = {"one fifth": 0.2, "two months out of three": 2 / 3, "Seventy-second": 72}


def cardinal(s: str) -> float:
    """An English cardinal: 'three', 'twenty-five', 'fourteen'."""
    return float(sum(SMALL.get(w, 0) + TENS.get(w, 0) for w in s.lower().replace("-", " ").split()))


def figure(s: str) -> float:
    """'1,000', '30.5', '.28', '0·900' (the raised decimal point of Economica)."""
    return float(s.replace(",", "").replace("·", "."))


def frac(s: str) -> float:
    """'7-1/2' (Okun's typescript) -> 7.5."""
    whole, part = s.split("-")
    n, d = part.split("/")
    return int(whole) + int(n) / int(d)


def ocr(s: str) -> float:
    """A figure of the text layer of a JSTOR scan whose decimal point is lost or read as '*' or '-': '12 5' -> 12.5,
    '14*3' -> 14.3, '17 *5' -> 17.5, '12- 5' -> 12.5, '10 94' -> 10.94, '- 0 *60' -> -0.60."""
    digits = re.findall(r"\d+", s)
    assert len(digits) == 2, s
    return (-1 if s.lstrip().startswith("-") else 1) * float(f"{digits[0]}.{digits[1]}")


def ocrhalf(s: str) -> float:
    """A figure with ½ as the text layer reads it: '2Y2', "2'2", '512', '412' -> the first digit and a half."""
    return int(s[0]) + 0.5


ZH_DIGITS = {"〇": 0, "零": 0, "一": 1, "两": 2, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
ZH_UNITS = {"十": 10, "百": 100, "千": 1000, "万": 10 ** 4, "亿": 10 ** 8}


def zh(s: str) -> float:
    """A Chinese numeral: '六', '十五', '三分之二', '一半', '二十多'."""
    if "分之" in s:
        b, a = s.split("分之")
        return zh(a) / zh(b)
    if s.endswith("半"):
        return 0.5 * (zh(s[:-1]) if s[:-1] else 1)
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
IMG_FIGURES = re.compile(r"(-?)(\d[\d,]*(?:[.·]\d+)?|\.\d+)")
HOW = {"num": figure, "en": cardinal, "word": lambda w: WORDS[w], "frac": frac, "ocr": ocr, "ocrhalf": ocrhalf,
       "half": lambda w: figure(w[:-1]) + 0.5, "neg": lambda w: -figure(w)}
SEVERAL = {"fields": lambda w: [figure(x) for x in w.split(",") if x]}   # the fields of a line of a CSV file
# id -> [(phrase, how)], in order. A phrase 'context|word' is searched as a whole and read from `word`. Rows not
# listed are read with all the figures of the quotation (a page image: of the transcription, with its signs). An empty
# list: the row prints no number of the story.
READINGS: dict[str, list[tuple[str, str]]] = {
    # Phillips (1958)
    'ph_jstor': [], 'ph_unemp': [], 'ph_curve_text': [], 'ph_fig4': [], 'ph_sliding': [], 'ph_t1_cost': [],
    'ph_stable_text': [], 'ph_wages5_text': [], 'ph_t1_head': [],
    'ph_fifth': [('|one fifth', 'word')],
    'ph_crosses': [('between |0', 'num'), (' and |2', 'num'), (', |2', 'num'), (' and |3', 'num'), (', |3', 'num'),
                   (' and |4', 'num'), ('. |4', 'num'), (' and |5', 'num'), (', |5', 'num'), (' and |7', 'num'),
                   (', and |7', 'num'), (' and |11', 'num')],
    'ph_fit': [('the |four', 'en'), ('between |0', 'num'), ('and |5', 'num'), ('remaining |two', 'en'),
               ('between |5', 'num'), ('and |11', 'num')],
    'ph_1862': [('increasein |1862', 'num'), ('increasein |1863', 'num'), ('the |12*5', 'ocr'), ('between |1861', 'num'),
                ('and |1862', 'num')],
    'ph_wood': [('From |1880', 'num'), ('for |1881', 'num'), ('to |1886', 'num')],
    'ph_1893': [('from |1893', 'num'), ('to |1896', 'num'), ('during |1897', 'num'), ('from |1894', 'num'),
                ('to |1896', 'num'), ('in |1897', 'num')],
    'ph_eight': [('During the |1890', 'num'), ('from |1895', 'num'), ('to |1897', 'num'), ('an |eight', 'en'),
                 ('January |1898', 'num')],
    'ph_1912': [('in |1912', 'num'), ('from |2 8', 'ocr'), ('February |1912', 'num'), ('to |11.3', 'num'),
                ('to |3 -6', 'ocr'), ('and |2 -7', 'ocr')],
    'ph_1912adj': [('during |1912', 'num'), ('about |0 8', 'ocr')],
    'ph_narrow': [('be |two', 'en')],
    'ph_1921src': [('From |1921', 'num'), ('to |1948', 'num'), ('years |1921', 'num'), ('-|1945', 'num')],
    'ph_1921': [('from |2 6', 'ocr'), ('in |1920', 'num'), ('to |17 0', 'ocr'), ('in |1921', 'num'), ('of |22 2', 'ocr'),
                ('in |1921', 'num')],
    'ph_1921b': [('of |12 8', 'ocr')],
    'ph_1922': [('In |1922', 'num'), ('was |14*3', 'ocr'), ('by |19*1', 'ocr')],
    'ph_1922b': [('of |17 *5', 'ocr'), ('betwveen|1921', 'num'), ('and |1922', 'num')],
    'ph_1925': [('between |9 7', 'ocr'), ('and |12- 5', 'ocr'), ('from |1925', 'num'), ('to |1929', 'num')],
    'ph_1925avg': [('these |five', 'en'), ('was |10 94', 'ocr'), ('was |- 0 *60', 'ocr')],
    'ph_1925curve': [('the |1861', 'num'), ('-|1913', 'num'), ('of |10 94', 'ocr'), ('is |- 0*56', 'ocr')],
    'ph_war': [('in |1940', 'num'), ('and |1941', 'num')],
    'ph_reverse': [('for |1950', 'num'), ('points for |1953', 'num'), ('to |1957', 'num')],
    'ph_lag': [('lagged |seven', 'en')],
    'ph_t1_def': [('years |1948', 'num'), ('-|1957', 'num'), ('lagged |seven', 'en')],
    'ph_1948cost': [('in |1948', 'num')],
    'ph_demand_infl': [('In |1953', 'num'), ('years |1954', 'num'), ('to |1957', 'num'), ('these |five', 'en'),
                       ('in |1950', 'num')],
    'ph_stable': [('of |2', 'num'), ('under |2½', 'half')],
    'ph_wages5': [('about |5½', 'half')],
    # Samuelson and Solow (1960)
    'ss_jstor': [], 'ss_fig2': [], 'ss_longer': [],
    'ss_issue': [('Vol. |50', 'num'), ('No. |2', 'num'), ('the |Seventy-second', 'word'), ('(May, |1960', 'num'),
                 ('pp. |177', 'num'), ('|194', 'num')],
    'ss_phillips5': [('with |5', 'num'), ('the |2', 'num'), ('-|3', 'num'), ('about |2Y2', 'ocrhalf')],
    'ss_point1': [("the |2'2", 'ocrhalf'), ('somethinglike |5', 'num'), ('to |6', 'num')],
    'ss_point2': [('than |3', 'num'), ('as |4', 'num'), ('to |5', 'num')],
    'ss_pointA': [('about |512', 'ocrhalf')],
    'ss_pointB': [('to |3', 'num'), ('about |412', 'ocrhalf')],
    'ss_fig2cap': [('last |twenty-five', 'en')],
    # the Economic Reports of the President
    'erp_transmitted': [('January |20', 'num'), (',|1962', 'num')],
    'erp_cea': [('Report, January |1962', 'num'), ('Act of |1946', 'num')],
    'erp_twothirds': [('by |four', 'en'), ('past |fifteen', 'en'), ('of |seven', 'en'),
                      ('In |two months out of three', 'word'), (', |4', 'num')],
    'erp_reasons': [('are |three', 'en')],
    'erp_gap49': [('of |1961', 'num'), ('$|51', 'num'), ('(|1961', 'num'), ('$|28', 'num')],
    'erp_gap50': [('For |1961', 'num'), ('$|40', 'num')],
    'erp_jobs': [('in |1961', 'num'), ('was |4.8', 'num'), ('actual |1961', 'num'), ('of |71.6', 'num'), (', |2', 'num'),
                 ('of |4', 'num')],
    'erp_table2': [],
    'e71_c24_cols': [('Both sexes |16', 'num'), ('-|19', 'num')],
    'e71_c45_1968': [('1958 |104.2', 'num')],
    'e71_c45_1969': [('1989 |109.8', 'num')],
    # Historical Statistics of Canada
    'hs_d491_title': [('D|491', 'num'), ('-|497', 'num'), ('averages, |1946', 'num'), ('to |1975', 'num')],
    'hs_d491_cols': [], 'hs_d491_fn1': [],
    'hs_d491_fn2': [('in |1950', 'num'), ('October |1949', 'num')],
    **{rid: [('|' + line, 'fields')] for rid, line in (
        ('hs_d491_1956', ',1956,,3.4,6.0,5.0,2.4,2.2,2.8,'), ('hs_d491_1957', ',1957,,4.6,8.4,6.0,3.4,2.6,5.0,9.0,'),
        ('hs_d491_1958', ',1958,,7.0,12.5,8.8,5.4,4.1,8.6,18.5,'), ('hs_d491_1961', ',1961,,7.1,11.2,9.2,5.5,4.6,8.5,19.5,'),
        ('hs_k8_1956', ',1956,68.5,'), ('hs_k8_1957', ',1957,70.7,'), ('hs_k8_1960', ',1960,74.3,'),
        ('hs_k8_1961', ',1961,75.0,'))},
    # Friedman (1976), Fisher (1926)
    'fr_shortcircuit': [], 'fr_busied': [],
    'fi_fixed': [('only |79', 'num'), ('for |four', 'en')],
    # Okun (1962), on the page images
    'ok_grade': [('from |5-1/2', 'frac'), ('to |4', 'num'), ('from |94-1/2', 'frac'), ('to |96', 'num')],
    'ok_answer': [('above |four', 'en'), ('about a |three', 'en')],
    'ok_three': [('from |three', 'en')],
    'ok_first': [('to |55', 'num'), ('from |1947', 'num'), ('to |1960', 'num')],
    'ok_trial': [], 'ok_method3': [],
    'ok_weighted': [('approximate |3', 'num'), ('-to-|1', 'num'), ('is |3.2', 'num')],
    'ok_five': [('is |four', 'en'), ('a |five', 'en'), ('is |3.2', 'num')],
    'ok_range': [('about |3', 'num'), ('to |7-1/2', 'frac'), ('the |3.2', 'num'), ('either |1', 'num'),
                 ('or |15', 'num')],
    # Klein (1950), on the page images
    'kl_cfm': [('No. |11', 'num'), (', |1921', 'num'), ('-|1941', 'num'), ('KLEIN. |1950', 'num'), ('. |174', 'num'),
               ('$|4.00', 'num')],
    'kl_title': [('STATES |1921', 'num'), ('-|1941', 'num')],
    'kl_preface': [('period |1944', 'num'), ('-|1947', 'num')],
    'kl_trend': [], 'kl_investment': [], 'kl_real': [], 'kl_nodistinguish': [], 'kl_ml': [], 'kl_wagebill': [],
    'kl_identities': [],
    'kl_est_c': [('= |16.78', 'num'), ('+ |0.02', 'num'), ('+ |0.23', 'num'), ('+ |0.80', 'num')],
    'kl_est_i': [('= |17.79', 'num'), ('+ |0.23', 'num'), ('+ |0.55', 'num'), ('- |0.15', 'neg')],
    'kl_est_w': [('= |1.60', 'num'), ('+ |0.42', 'num'), ('+ |0.16', 'num'), ('+ |0.13', 'num'), ('(t - |1931', 'num')],
    'kl_data': [('year |1921', 'num'), ('-|1941', 'num')],
    'ar_kg': [('Robert |1964', 'num')],
    # the web pages and the authority records
    'smg_fourteen': [('Approximately |fourteen', 'en')],
    'gnd_licence': [],
}


def read(word: str, how: str) -> list[float]:
    return SEVERAL[how](word) if how in SEVERAL else [HOW[how](word)]


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
MISPRINTS = [("ph_predict", "accura ely", "'accura ely' for 'accurately'"),
             ("ph_stable_text", "2~", "'2~' for 2½"),
             ("ph_wages5_text", "about 51 per", "'51' for 5½"),
             ("ph_curve_text", "9*638x-1394", "'9*638' and '1394' for 9·638 and 1·394"),
             ("ph_example", "Iate", "'Iate' for 'rate'"),
             ("ph_gold", "decisionl", "'decisionl' for 'decision'"),
             ("ph_1948src", "tbp", "'tbp' for 'the'"),
             ("ph_1922b", "betwveen", "'betwveen' for 'between'"),
             ("ss_mit", "Tcchnology", "'Tcchnology' for 'Technology'"),
             ("ss_mobility", "miobility", "'miobility' for 'mobility'"),
             ("ss_phillips5", "2Y2", "'2Y2' for 2½"),
             ("ss_point1", "2'2", "\"2'2\" for 2½"),
             ("ss_pointA", "512", "'512' for 5½"),
             ("ss_pointB", "412", "'412' for 4½"),
             ("e71_c45_1968", "1958 104.2", "'1958' for 1968"),
             ("e71_c45_1969", "1989 109.8", "'1989' for 1969"),
             ("erp_transmitted", "B.C.", "'B.C.' for 'D.C.'"),
             ("nbb_reviving", "Tinbergen 's", "'Tinbergen 's' with a space")]
# the rows whose figures the rule 'ocr' reads (the decimal point lost or read as '*' or '-'), named in the notes
OCR_ROWS = ("ph_1862", "ph_1912", "ph_1912adj", "ph_1921", "ph_1921b", "ph_1922", "ph_1922b", "ph_1925", "ph_1925avg",
            "ph_1925curve")


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
    quoted("rows with values, each read from its quotation", n, 165)
    quoted("rows read on a page image (no quotation)", img, 69)
    Q, notes = quotes(), meta()["notes"]
    for rid, word, named in MISPRINTS:
        assert word in Q[rid], (rid, word)                                      # printed in the quotation
        k = notes.find(named)
        m = re.match(r"[^(]{0,80}\(([^)]*)\)", notes[k + len(named):]) if k >= 0 else None
        assert m and rid in re.split(r",\s*", m.group(1)), (rid, named)        # and named, with its row
    for rid in OCR_ROWS:
        assert any(how == "ocr" for _, how in READINGS[rid]) and f"({rid})" in notes, rid
    # the source keys the chapter cites for its sources
    assert set(src) == set(df["file"]), sorted(set(src) ^ set(df["file"]))
    # the documents of the menu snapshot are sources of this one, with the same hashes
    mm = load_snapshot("menu_us_canada_1946_1969")[1]
    for key in ("erp1971", "hsc_d491", "hsc_k8"):
        assert f"{key} {src[key]['url']}" in mm["notes"] and src[key]["sha256"] in mm["notes"], key
    # the course pages' copies of the two articles: address, date and hash recorded, the files not committed
    for key in ("phillips1958", "samuelson1960", "okun1962"):
        assert f"{key} {src[key]['url']} " in notes and src[key]["sha256"] in notes, key
    assert "not committed" in notes and "read to verify, not committed" in src["phillips1958"]["version"]


# ---------------------------------------------------------------------------------------------------
# Data of the text and the figures
@lru_cache(maxsize=None)
def boe() -> pd.DataFrame:
    df, m = load_snapshot("boe_millennium_uk_1860_1958")
    assert 38 in m["used_in"] and m["fetch"] == "data/fetch/boe_millennium_gb38.py"
    return df.set_index("year")


@lru_cache(maxsize=None)
def menu() -> pd.DataFrame:
    df, m = load_snapshot("menu_us_canada_1946_1969")
    assert 38 in m["used_in"] and m["fetch"] == FETCH
    df = df.set_index("year")
    df["us_infl"] = 100 * df["us_cpi_1967_100"].pct_change()
    df["ca_infl"] = 100 * df["ca_cpi_1971_100"].pct_change()
    return df


def curve_pars() -> tuple[float, float, float]:
    """a, b, c of Phillips's curve y + a = b x^c, from the page image of p. 290."""
    a, b, c, a2, logb, c2 = facts()["ph_curve"]
    assert a == a2 and c == -c2 and abs(math.log10(b) - logb) < 5e-4      # the log form agrees: log 9.638 = 0.984
    return a, b, c


def curve(x):
    """Phillips's curve, eq:phillips-curve: the rate of change of money wage rates (% a year) at unemployment x (%)."""
    a, b, c = curve_pars()
    return b * np.asarray(x, dtype=float) ** c - a


def curve_inverse(y: float) -> float:
    """The unemployment rate at which the curve gives y."""
    a, b, c = curve_pars()
    return ((y + a) / b) ** (1 / c)


def wage_change(col: str = "weekly_earnings_1913_100") -> pd.Series:
    """Phillips's rate of change: the first central difference of the index as a percentage of the index of the same
    year (rows ph_central, ph_1861), applied to Feinstein's average weekly earnings."""
    e = boe()[col]
    return (100 * (e.shift(-1) - e.shift(1)) / 2 / e).dropna()


def bins() -> list[tuple[float, float]]:
    """Phillips's intervals, the upper bound included (rows ph_crosses, ph_upper)."""
    v = facts()["ph_crosses"]
    assert "the upper bound being included" in quotes()["ph_upper"]
    return list(zip(v[0::2], v[1::2]))


@lru_cache(maxsize=None)
def crosses() -> list[dict]:
    """The six crosses of 1861-1913 recomputed from the revised series (tab:phillips-crosses)."""
    lo_y, hi_y = facts()["ph_periods"][:2]
    y = wage_change().loc[lo_y:hi_y]
    u = boe()["union_unemp_pct"].loc[lo_y:hi_y]
    assert len(y) == len(u) == hi_y - lo_y + 1
    out = []
    for lo, hi in bins():
        sel = (u > lo) & (u <= hi)
        out.append(dict(lo=lo, hi=hi, n=int(sel.sum()), u=float(u[sel].mean()), y=float(y[sel].mean()),
                        curve=float(curve(u[sel].mean()))))
    assert sum(c["n"] for c in out) == len(u)                                  # every year in one interval
    return out


def scatter_1861_1913() -> pd.DataFrame:
    lo_y, hi_y = facts()["ph_periods"][:2]
    return pd.DataFrame({"u": boe()["union_unemp_pct"].loc[lo_y:hi_y], "y": wage_change().loc[lo_y:hi_y]})


def scatter_1948_1957() -> pd.DataFrame:
    lo_y, hi_y = facts()["ph_periods"][4:6]
    return pd.DataFrame({"u": boe()["civilian_unemp_pct"].loc[lo_y:hi_y], "y": wage_change().loc[lo_y:hi_y]})


def table1() -> pd.DataFrame:
    """Phillips's Table 1, columns (1) to (3), read on the page image of p. 298."""
    F = facts()
    rows = [F[f"ph_t1_{y}"] for y in range(1948, 1958)]
    df = pd.DataFrame(rows, columns=["year", "actual", "demand", "cost"]).set_index("year")
    assert list(df.index) == list(range(1948, 1958))
    return df


# Klein's Model I (eq:phillips-klein) in deviations from a baseline: T and W2 fixed, G raised by dG from year 1
def klein_coef() -> dict[str, float]:
    F = facts()
    c0, c_p, c_p1, c_w = F["kl_est_c"]
    i0, i_p, i_p1, i_k = F["kl_est_i"]
    w0, w_x, w_x1, w_t, t0 = F["kl_est_w"]
    return dict(c_p=c_p, c_p1=c_p1, c_w=c_w, i_p=i_p, i_p1=i_p1, i_k=i_k, w_x=w_x, w_x1=w_x1)


def klein_path(years: int = 30, dG: float = 1.0, coef: dict | None = None) -> pd.DataFrame:
    """The simulation of ex:phillips-klein: each year the five equations C, I, W1, X = C + I + G and Pi = X - W1 are
    solved together (numpy), given last year's Pi, X and K."""
    k = coef or klein_coef()
    out, prev = [], dict(P=0.0, X=0.0, K=0.0)
    for t in range(1, years + 1):
        # unknowns C, I, W1, X, P
        A = np.array([[1, 0, -k["c_w"], 0, -k["c_p"]],
                      [0, 1, 0, 0, -k["i_p"]],
                      [0, 0, 1, -k["w_x"], 0],
                      [-1, -1, 0, 1, 0],
                      [0, 0, 1, -1, 1]], dtype=float)
        b = np.array([k["c_p1"] * prev["P"], k["i_p1"] * prev["P"] + k["i_k"] * prev["K"], k["w_x1"] * prev["X"],
                      dG, 0.0])
        C, I, W1, X, P = np.linalg.solve(A, b)
        K = prev["K"] + I
        out.append(dict(t=t, C=C, I=I, W1=W1, X=X, P=P, K=K))
        prev = dict(P=P, X=X, K=K)
    return pd.DataFrame(out).set_index("t")


def klein_closed(coef: dict | None = None) -> dict[str, float]:
    """The multipliers of ex:phillips-klein in closed form."""
    k = coef or klein_coef()
    impact = 1 / (1 - (k["c_p"] * (1 - k["w_x"]) + k["c_w"] * k["w_x"]) - k["i_p"] * (1 - k["w_x"]))
    w = k["w_x"] + k["w_x1"]
    long = 1 / (1 - ((k["c_p"] + k["c_p1"]) * (1 - w) + k["c_w"] * w))
    capital = (k["i_p"] + k["i_p1"]) * (1 - w) * long / -k["i_k"]
    return dict(impact=impact, long=long, capital=capital)


# ---------------------------------------------------------------------------------------------------
# 2. Every “…” of the text against the snapshot
# the chapter's Chinese renderings of the quotations: rendering -> row (or rows)
TRANSLATIONS = {
    "生在新西兰、由工程师转行的经济学家": "smg_engineer",
    "以看得见的方式": "smg_circular",
    "选择的菜单": ("ss_menu", "ss_fig2cap"),
    "失业从前几乎完全被看作个人自己的责任，现在则被承认是国家良心上的一项负担。": "erp_conscience",
    "最大限度的生产、就业与购买力": "erp_maximum",
    "爬行的通胀": "ss_creeping",
    "理论结构的一个空缺": "fr_gap",
    "一个方程": "fr_gap",
    "劳动服务的价格": "ph_price",
    "高度非线性": "ph_nonlinear",
    "一阶中心差分": "ph_fn_central",
    "证实了这个猜测": "ph_suspicion",
    "无疑": ("ph_1921b", "ph_restraint49"),
    "相当准确地": "ph_predict",
    "需求拉动": "ph_t1_def",
    "成本推动": "ph_t1_cost",
    "成本通胀的明显例子": "ph_cost",
    "似乎是纯粹的需求通胀": "ph_demand_infl",
    "大致不变的加成": "fr_markup",
    "略低于 2.5\\%": "ph_stable",
    "当然是初步的": "ph_tentative",
    "绕过了工资这一中间步骤": "fr_shortcircuit",
    "同样仔细的研究": "ss_careful",
    "自成一类": "ss_suigeneris",
    "更像是 8\\%": "ss_8pct",
    "以失业支付的代价": "ss_price",
    "负责": "ss_restraint",
    "似乎就是物价稳定的代价": "ss_cost",
    "拔河": "ss_tug",
    "永远": "ss_forever",
    "记得的经验": "ss_forever",
    "巨大的实验": "ss_vast",
    "不必要的社会痛苦": "ss_pain",
    "固定收入": "ss_fixed",
    "黑人及其他种族": "e71_c24_cols",
    "与妻子同住的已婚男子": "e71_c24_married",
    "可以容忍的物价表现": "ok_criterion",
    "简单而直接": "ok_answer",
    "主观加权": "ok_weighted",
    "分数": "ok_grade",
    "战胜失业不是经济政策唯一的目的，但它一定是不可缺少的开端。": "erp_conquest",
    "我们承担不起满足于任何规定的失业水平。但为了工作的需要，我们把 4\\% 的失业率看作一个临时的目标。": "erp_target",
    "非自愿的失业是经济浪费的一个标志，但失业根本的恶，在于它是对人的尊严的冒犯。": "erp_dignity",
    "任何实际的失业目标都只是一时的折中，达到它绝不能成为松懈的理由，而应当激励人们去找出把失业率降得更低的办法。":
        "erp_compromise",
    "以经济现有的结构，以及物价与工资决定的过程，认真地把失业推到接近零，会造成很高的物价上涨率。": "erp_zero_infl",
    "任意地重新分配": "erp_redistribution",
    "消除总需求不足造成的失业，又不造成需求引起的通胀": "erp_fullemp",
    "选定稳定政策的某个目标，并不使政策承诺一个不可更改的、与充分就业相应的失业率定义。情况可能改变失业率与物价水平对总需求"
    "数量的反应程度。因此，当前的经验必须是向导。": "erp_commit",
    "稳定政策一个合理而审慎的充分就业目标": "erp_reasonable",
    "4\\% 的失业是一个不高的目标，但必须强调，这是一个应当只靠稳定政策就能达到的目标。": "erp_modest",
    "持久的、系统的特征": "erp_notpermanent",
    "并没有一个确切的失业率，到了那里，总需求的扩张就突然不再影响就业，只影响一般物价水平。": "erp_noprecise",
    "这类估计当然不可能精确": "erp_precise",
    "失业的水平是经济浪费的晴雨表。失业率每向 4\\% 前进 1 个百分点，在战后的扩张时期意味着总产出约增加 3\\%。": "erp_3pct",
    "代价极高的药": "erp_expensive",
    "公平会被牺牲，因为整个经济，尤其是失业者，会因少数个人与集团行使经济权力的方式而受罪。": ("erp_equity", "erp_equity2"),
    "自由而进步的经济在增长中不可避免的一部分": "erp_displacement",
    "进步的牺牲品；他们被迫长期失业，这对谁都没有好处，却把不公正的惩罚加在任意挑出的少数人身上": "erp_victims",
    "约 8\\%": "erp_magnified",
    "约 3\\%": "erp_3pct",
    "复兴": "nbb_reviving",
    "初步的、试探性的": "kl_tentative",
    "简单的三方程体系": "kl_running",
    "劳工日益增强的谈判力量": "kl_trend",
    "纯粹是一个实物体系": "kl_real",
    "无法区分": "kl_nodistinguish",
    "没有给出可靠性的量度": "kl_reliability",
    "太过加总": "kl_aggregative",
    "最为著名": "nb_famous",
    "稳定的交替": "fr_causal",
    "正确的": "fr_busied",
    "欣然": "fr_alacrity",
    "临时的目标": "erp_target",
    "高达 90\\%": "fi_90",
    "可以设想": "fi_causal",
    "在很大程度上": "fi_effects",
    # the misreadings of the text layers quoted in the 史料说明
    "accura ely": "ph_predict",
    "2~": "ph_stable_text",
    "5.5\\% 左右": "ph_wages5",
    "51": "ph_wages5_text",
    "9*638": "ph_curve_text",
    "1394": "ph_curve_text",
    "512": "ss_pointA",
    "412": "ss_pointB",
    "2Y2": "ss_phillips5",
    "2'2": "ss_point1",
    "1958": "e71_c45_1968",
    "1989": "e71_c45_1969",
    "经济": "nb_citation",
    "计量经济": "nbf_motivation",
    "滞胀": "fr_stagflation",
}
# the words of the source each rendering renders, in the quotation (or the transcription of the page image)
KEYWORDS = {
    "smg_engineer": ["New Zealand-born engineer turned economist"],
    "smg_circular": ["in a visual way"],
    "ss_menu": ["menu of choice"], "ss_fig2cap": ["menu of choice"],
    "erp_conscience": ["almost solely the personal responsibility of the individual",
                       "a charge on the conscience of the Nation"],
    "erp_maximum": ["maximum production, employment, and purchasing power"],
    "ss_creeping": ["creeping inflation"],
    "fr_gap": ["a gap in Keynes' theoretical structure", '"one equation"'],
    "ph_price": ["the price of labourservices"],
    "ph_nonlinear": ["highlynon-linear"],
    "ph_fn_central": ["first central differenceis"],
    "ph_suspicion": ["confirms this suspicion"],
    "ph_1921b": ["no doubt"], "ph_restraint49": ["no doubt"],
    "ph_predict": ["fairly accura ely", "accura ely"],
    "ph_t1_def": ['" demand pull "'],
    "ph_t1_cost": ['" cost push"'],
    "ph_cost": ["a clearcase of cost inflation"],
    "ph_demand_infl": ["seemsto have been puredemandinflation"],
    "fr_markup": ["a roughly constant mark-up factor"],
    "ph_stable": ["a little under 2½ per cent"],
    "ph_tentative": ["of course tentative"],
    "fr_shortcircuit": ["short-circuiting the intermediate step through wages"],
    "ss_careful": ["comparably careful study"],
    "ss_suigeneris": ["sui generis"],
    "ss_8pct": ["more like 8 per cent"],
    "ss_price": ["the price in unemploymentthat must be paid"],
    "ss_restraint": ['"responsible"'],
    "ss_cost": ["would appear to be the cost of price stability"],
    "ss_tug": ["tug of war"],
    "ss_forever": ["forever", "remembered experience"],
    "ss_vast": ["a vast experiment"],
    "ss_pain": ["needless social pain"],
    "ss_fixed": ["squeeze on fixed incomes"],
    "e71_c24_cols": ["Negro and other races"],
    "e71_c24_married": ["Married men living with their wives"],
    "ok_criterion": ["tolerable price behavior"],
    "ok_answer": ["simple and direct"],
    "ok_weighted": ["subjectively weighted"],
    "ok_grade": ['"grade"'],
    "erp_conquest": ["The conquest of unemployment is not the sole end of economic policy", "indispensable beginning"],
    "erp_target": ["We cannot afford to settle for any prescribed level of unemployment", "a temporary target"],
    "erp_dignity": ["a sign of economic waste", "an affront to human dignity"],
    "erp_compromise": ["only a temporary compromise", "a still lower rate"],
    "erp_zero_infl": ["push unemployment close to zero", "a high rate of price inflation"],
    "erp_redistribution": ["an arbitrary redistribution"],
    "erp_fullemp": ["eliminate the unemployment which results from inadequate aggregate demand",
                    "demand-induced inflation"],
    "erp_commit": ["does not commit policy to an unchangeable definition", "Current experience must therefore be the guide"],
    "erp_reasonable": ["a reasonable and prudent full employment target for stabilization policy"],
    "erp_modest": ["Unemployment of 4 percent is a modest goal", "achievable by stabilization policy alone"],
    "erp_notpermanent": ["a permanent and systematic feature"],
    "erp_noprecise": ["There is no precise unemployment rate", "affect solely the general price level"],
    "erp_precise": ["cannot, of course, be precise"],
    "erp_3pct": ["a barometer of economic waste", "roughly 3 percent in total output"],
    "erp_expensive": ["an extremely expensive cure"],
    "erp_equity": ["Equity would be sacrificed", "the unemployed in particular"],
    "erp_equity2": ["exercise their economic power"],
    "erp_displacement": ["an inevitable part of the growth of a free and progressive economy"],
    "erp_victims": ["victims of progress", "an unjust penalty on an arbitrarily selected few"],
    "erp_magnified": ["about 8 percent"],
    "nbb_reviving": ["reviving"],
    "kl_tentative": ["preliminary and tentative"],
    "kl_running": ["A SIMPLE THREE-EQUATION SYSTEM"],
    "kl_trend": ["the growing bargaining strength of labor"],
    "kl_real": ['purely a "real" system'],
    "kl_nodistinguish": ["no way of distinguishing"],
    "kl_reliability": ["No measures of reliability are given here"],
    "kl_aggregative": ["too aggregative"],
    "nb_famous": ["became the most famous"],
    "fr_causal": ["a stable trade-off"],
    "fr_busied": ['"right"'],
    "fr_alacrity": ["with alacrity"],
    "fi_90": ["as high as 90 per cent"],
    "fi_causal": ["might conceivably not be causal"],
    "fi_effects": ["in large measure"],
    "ph_stable_text": ["2~"],
    "ph_wages5": ["about 5½ per cent"],
    "ph_wages5_text": ["about 51 per cent"],
    "ph_curve_text": ["9*638", "1394"],
    "ss_pointA": ["512"], "ss_pointB": ["412"], "ss_phillips5": ["2Y2"], "ss_point1": ["2'2"],
    "e71_c45_1968": ["1958 104.2"], "e71_c45_1969": ["1989 109.8"],
    "nb_citation": ["economic models"], "nbf_motivation": ["econometric models"],
    "fr_stagflation": ['"stagflation"'],
}
# the sources that may be quoted at length: the works of the United States government (the Economic Reports), the
# Science Museum Group's descriptions (CC BY 4.0) and Statistics Canada's tables (Open Licence)
FREE = ("erp_", "e71_", "smg_", "hs_")


def tex_text() -> str:
    return "\n".join(l for l in TEX.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("%"))


def text_quotations() -> list[str]:
    """The “…” of the text; the closing question is Chapter 39's and the chapter's own question is in the guide and at
    the end of the opening (both checked by guide() and opening())."""
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 39's question"
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
    for q in ("accura ely", "2~", "51", "9*638", "1394", "512", "412", "2Y2", "2'2", "1958", "1989"):
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
# what is not a number of the story: labels, citations, cross-references, the key equations and Model I (models()
# reads them), the sub- and superscripts of the math and the numbers of the parts of an example
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


def printed(rid: str, words: str) -> list[float]:
    """The words are in the quotation of row rid; the figures they print (a misreading of a text layer)."""
    assert words in quotes()[rid], (rid, words)
    return [figure(x) for x in FIGURES.findall(words)]


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


def noted(pattern: str, notes: str | None = None) -> list[int]:
    """The numbers that a pattern of the snapshot's notes captures."""
    m = re.search(pattern, meta()["notes"] if notes is None else notes)
    assert m, pattern
    return [int(g) for g in m.groups()]


def version(key: str) -> str:
    return meta()["sources"][key]["version"]


def their(name: str, rid: str, *words: str) -> list[float]:
    """Row rid of another chapter's snapshot: the words are in its quotation; its values."""
    df = load_snapshot(name, dtype=str, keep_default_na=False)[0].set_index("id")
    q = " ".join(df.loc[rid, "quote"].split())
    for w in words:
        assert w in q, (name, rid, w)
    return [float(x) for x in df.loc[rid, "value"].split(";")]


# ---------------------------------------------------------------------------------------------------
# Teaching inputs of the examples and the self-check
READ_X = (2, 5)                      # ex:phillips-read (1)
READ_DROPS = ((5, 4), (2, 1))        # ex:phillips-read (3)
STABLE_U = 3                         # ex:phillips-stable (2)
STABLE_SWING = (1, 5)                # ex:phillips-stable (3)
PENSION = 1000                       # ex:phillips-menu (2): dollars a year, fixed in money
PENSION_YEARS = 5
DG = 1.0                             # ex:phillips-klein: G up by 1 (billions of 1934 dollars) for good
SC_U = (3, 8)                        # self-check 1
SC_G = 3                             # self-check 2: productivity growth
SC_OKUN = 5.5                        # self-check 4
SC_WX = 0.30                         # self-check 5: the coefficient of current output in the wage equation


def y_of(x: float) -> float:
    return float(curve(x))


def power(x: float) -> float:
    """x^{1.394}, the power the examples print."""
    return x ** -curve_pars()[2]


# ---------------------------------------------------------------------------------------------------
# 4. Numbers, section by section
def guide(F, Y, Q):
    t = TEX.read_text(encoding="utf-8")
    assert f"\\guidequestion{{{GUIDE}}}" in t and GUIDE == PREV
    assert chapter("ch37_mundell").rstrip().endswith(PREV)                     # 第 37 章交来的问题
    assert "\\guideprereq{\\chref{ch:islm}\\enspace\\nameref{ch:islm}}" in t
    said("复现菲利普斯（1958）的工资—失业关系", F["ph_source"][2])
    said("解释萨缪尔森与索洛（1960）怎样把它变成政策菜单，奥肯（1962）怎样把失业与产出缺口连起来", F["ss_issue"][3],
         F["ok_reprint"][0])
    said("用克莱因的模型 I（1950）说明宏观计量模型的结构、乘数与模拟", F["kl_imprint"][0])
    assert "\\chapterstub" not in t


def opening(F, Y, Q):
    vol, no, y58, p0, p1 = F["ph_source"]
    has("ph_source", "Economica, New Series", "(Nov., 1958)")
    said("1958 年 11 月，伦敦经济学院的《经济学刊》（Economica）登出一篇 17 页的论文", y58, 11, p1 - p0 + 1)
    has("ph_publisher", "on behalf of The London School of Economics and Political Science")
    has("ph_lse", "The London School of Economics.")
    a, b = F["ph_title"]
    has("ph_title", "The Relation between Unemployment and the Rate of Change of Money Wage Rates in the United Kingdom")
    said("题目叫《英国 1861—1957 年的失业与货币工资率变动率的关系》", a, b)
    chk("    almost a hundred years (将近一百年)", told("他把将近一百年的工资涨跌与失业画在一起", "将近", "年"), 100)
    assert 90 < b - a < 100
    has("smg_engineer", "a New Zealand-born engineer turned economist")
    said("他 1946 年进伦敦经济学院读社会学与经济学，1949 年在那里做出一台叫 MONIAC 的模拟计算机", F["smg_lse46"][0],
         F["smg_moniac49"][0])
    has("smg_lse46", "attended the London School of Economics studying sociology and economics")
    has("smg_title", "known as MONIAC")
    said("大约造了 14 台", F["smg_fourteen"][0])
    has("smg_fourteen", "Approximately")
    # Chapter 37's Canada
    u56, u61 = F["hs_d491_1956"][1], F["hs_d491_1961"][1]
    said("加拿大 1956—1961 年的失业率翻了一番还多", F["hs_d491_1956"][0], F["hs_d491_1961"][0])
    assert u61 > 2 * u56
    has("ph_purpose", "except in or immediately after those years in which there was a very rapid rise in import prices")
    # a year and a half later: November 1958 to May 1960
    has("ss_issue", "(May, 1960)")
    assert (F["ss_issue"][3] - y58) * 12 + 5 - 11 == 18
    say("一年半以后，这条曲线到了美国")
    has("ss_menu", "menu of choice")
    assert paragraph("一年半以后").endswith(GUIDE)                               # the opening ends with the question


def world(F, Y, Q):
    said("1962 年美国《总统经济报告》所附的顾问委员会年度报告回顾说", F["erp_title"][0])
    has("erp_title", "TOGETHER WITH THE ANNUAL REPORT OF THE COUNCIL OF ECONOMIC ADVISERS")
    has("erp_depression", "assume national responsibility", "involuntary")
    said("美国 1946 年的《就业法》要求总统向国会提交经济报告", F["erp_act"][0])
    has("erp_act", "as required under the Employment Act of 1946")
    said("1962 年 1 月的报告说，复苏只把经济带到了", F["erp_title"][0], mon("erp_title", "January"))
    has("erp_maximum", "only part of the way")
    B = boe()["civilian_unemp_pct"].loc[1948:1957]
    lo_y, hi_y = F["ph_periods"][4:6]
    assert list(B.index) == list(range(int(lo_y), int(hi_y) + 1))
    said("英国 1948—1957 年的失业率，按 Feinstein 的估计在 1.0\\% 到 1.6\\% 之间", lo_y, hi_y, B.min(), B.max())
    T = table1()
    has("ph_t1_head", "TABLE 1")
    said("菲利普斯的表 1 里，这十年的工资率每年涨 1.9\\% 到 10.5\\%", 1, T["actual"].min(), T["actual"].max())
    assert len(T) == 10
    has("ss_wrongwar", "economists have been accused of fighting the wrong inflation")
    a, b = F["ss_1946"]
    said("1946—1948 年美国物价上涨时，人们盯着集体谈判带来的一轮轮加薪", a, 1900 + b)
    has("ss_1946", "successive rounds of wage increases resulting from collective bargaining")
    a, b = F["ss_creep"]
    said("1955—1958 年物价又缓慢爬升，后期似乎是在产能日益过剩", a, 1900 + b)
    has("ss_causations", "demand-pull versus cost-push")
    has("ss_accelerate", "we do not draw the firm conclusion")
    # the theory
    said("1976 年在诺贝尔奖演讲里回顾了失业与通胀之间有稳定关系的假说", F["fr_lecture"][1])
    has("fr_alacrity", "a stable relation between the level of unemployment and the rate of inflation")
    has("ss_hume", "as Hume had early recognized", "fixed-income")
    say("萨缪尔森与索洛在注里也提到休谟")


def curve_section(F, Y, Q):
    has("ph_demand", "the greaterthe excess demand")
    has("ph_bid", "bid wage rates up quite rapidly")
    p = F["ph_periods"]
    said("他把 1861—1957 年分成三段分别处理", p[0], p[5])
    chk("    three periods (三段)", told("分成三段分别处理", "分成", "段"), len(p) / 2)
    said("1861—1913 年的工资用 Phelps Brown 与 Sheila Hopkins 编的小时工资率指数", p[0], p[1])
    has("ph_pbh", "indexof hourlywage rates", "Sheila Hopkins")
    has("ph_unemp", "Board of Trade and the Ministry of Labour", "from trade union returns")
    has("ph_central", "first centraldifference")
    a, b, c = F["ph_1861"]
    said("比如 1861 年的数，用的是 1860 年与 1862 年的指数", a, c, b)
    assert b - c == 2 and a == p[0]
    # the six crosses
    B = bins()
    chk("    six intervals (六组)", told("他按失业率把这些年分成六组", "分成", "组"), len(B))
    said("最低的一组失业在 2\\% 及以下，最高的一组在 7\\% 以上、11\\% 及以下", B[0][1], B[-1][0], B[-1][1])
    has("ph_cancel", "Since each interval includes years in which unemployment was increasing")
    four, lo, hi, two, lo2, hi2 = F["ph_fit"]
    said("$b$与$c$用失业在 5\\% 及以下的四个十字以最小二乘法估计，$a$靠反复试算，让曲线尽量靠近 5\\% 到 11\\% 之间的另两个十字",
         hi, lo2, hi2)
    chk("    four crosses (四个十字)", told("失业在 5\\% 及以下的四个十字", "以下的", "个"), four)
    chk("    two crosses (另两个十字)", told("之间的另两个十字", "另", "个"), two)
    assert four + two == len(B) and sum(1 for l, h in B if h <= hi) == four
    has("ph_form", "y + a = bxc or log (y + a) = log b + c log x")
    a_, b_, c_ = curve_pars()
    said("取对数，就是$\\log(y+0.900)=0.984-1.394\\log x$", a_, math.log10(b_), -c_)
    say("失业越少，工资涨得越快，而且越往左越陡")
    said("失业再多，$y$也只是趋近于$-0.9$，工资每年跌不到 1\\%", a_, 1)
    assert a_ < 1
    has("ph_loops", "during the upswing of a trade cycle")
    y62, _, imp, f61, f62 = F["ph_1862"]
    said("1862 年工资涨得特别多。他归因于这一年进口价格比上一年涨了 12.5\\%", y62, imp)
    assert (f61, f62) == (y62 - 1, y62)
    has("ph_1862", "outbreakof the Americancivil war")
    a, b = F["ph_fig4a"][:2]
    said("1879—1886 年的周期几乎看不出关系", a, b)
    has("ph_fig4", "the relationhardlyappearsat all in the cycle shown in Figure4")
    has("ph_fig4a", "1879-1886, using Bowley's wage index for the years 1881 to 1886")
    _, a, b = F["ph_wood"]
    said("他改用 Bowley 的指数计算 1881—1886 年，通常的关系就出现了", a, b)
    has("ph_wood", "based on Wood's earlier index", "giving the typical relation")
    a, b, c = F["ph_1893"][:3]
    said("1893—1896 年景气回升，工资却涨得比平常慢", a, b)
    said("1897 年终于酿成劳资冲突", F["ph_1893"][5])
    has("ph_1893", "exceptional resistance by employers to wage increases", "culminating in industrial strife")
    _, _, _, eight, y98 = F["ph_eight"]
    chk("    eight hours (八小时)", told("那几年雇主联合会抵制工会八小时工作日的要求", "工会", "小时"), eight)
    said("一直到 1898 年 1 月", y98, mon("ph_eight", "January"))
    has("ph_eight", "Amalgamated Society of Engineers", "lock-out")
    y12, _, _, peak, _, _ = F["ph_1912"]
    said("1912 年煤矿全面停工，工会的失业率 3 月一度升到 11.3\\%", y12, mon("ph_1912", "March"), peak)
    has("ph_1912", "general stoppage of work in coal mining", "trade unions")
    has("ph_1912adj", "restoring the typical pattern")
    chk("    two explanations (两种)", told("他给了两种可能的解释", "给了", "种"), F["ph_narrow"][0])
    has("ph_sliding", "sliding scale")
    has("ph_timelag", "collectivebargaining", "arbitration")
    # 1913-1948
    y21, y48, a, b = F["ph_1921src"]
    said("1913—1948 年的工资，1921 年起用劳工部的小时工资率指数，失业率 1921—1945 年用劳工部的英国数字", p[2], p[3], y21,
         a, b)
    assert y48 == p[3]
    has("ph_1921src", "index of hourlywage rates", "the United Kingdom")
    said("1915—1918 年失业很少", *F["ph_1915"])
    has("ph_1915", "automaticcost of livingadjustments")
    u20, y20, u21, y21, w21, _ = F["ph_1921"]
    said("1920 年的失业率是 2.6\\%，1921 年升到 17.0\\%，工资率跌了 22.2\\%", y20, u20, y21, u21, w21)
    has("ph_1921", "a fall of 22 2 per cent. in wage rates")
    said("生活费用跌了 12.8\\%", F["ph_1921b"][0])
    has("ph_1921b", "largelya result of falling importprices")
    y22, u22, w22 = F["ph_1922"]
    said("1922 年的失业率是 14.3\\%，正在下降，工资率却跌了 19.1\\%", y22, u22, w22)
    assert u22 < u21
    said("他把大部分跌幅归因于这一年生活费用指数下跌 17.5\\%", F["ph_1922b"][0])
    assert F["ph_1922b"][1:] == [y21, y22]
    has("ph_agreements", "less enthusiastic")
    has("ph_gold", "restore the gold standard at the pre-war parity")
    lo, hi, a, b = F["ph_1925"]
    said("1925—1929 年的失业停在 9.7\\% 到 12.5\\% 之间", a, b, lo, hi)
    five, avg_u, avg_y = F["ph_1925avg"]
    said("五年平均失业 10.94\\%，工资平均每年变动$-0.60\\%$", avg_u, -avg_y)
    chk("    five years (五年)", told("五年平均失业", "", "年"), five)
    assert b - a + 1 == five and avg_y < 0
    a, b, u, yc = F["ph_1925curve"]
    said("按 1861—1913 年的曲线，这个失业率对应$-0.56\\%$", a, b, -yc)
    chk("    the curve at 10.94 per cent (-0.56)", y_of(u), yc, tol=0.005)
    has("ph_view", "the evidence does not support the view")
    said("1935—1937 年工资的涨幅", F["ph_1935"][0], F["ph_1935"][2])
    said("1940 年与 1941 年的加薪", *F["ph_war"])
    has("ph_war", "the effectiveness of the economic controls")
    said("1946 年的复员与 1947 年的煤炭危机让失业上升，1948 年又几乎正好回到", *F["ph_1948return"])
    has("ph_1948return", "demobilisation", "the coal crisis", "almost exactly")
    # 1948-1957
    said("1948—1957 年的失业率是劳工部公布的大不列颠月度百分比的平均", p[4], p[5])
    has("ph_1948src", "monthly unemployment percentages in Great Britain")
    has("ph_1948wage", "weeklywage rates")
    said("1950 年的点很贴近曲线，1953—1957 年的点绕着曲线成一个窄圈", *F["ph_reverse"])
    has("ph_reverse", "the reverse of the direction of the loops")
    lag = F["ph_lag"][0]
    said("他把失业率滞后 7 个月，即用上一年 6 月到当年 5 月的平均", lag, mon("ph_lag", "June"), mon("ph_lag", "May"))
    assert 12 - mon("ph_lag", "June") + mon("ph_lag", "May") + 1 == 12
    said("1950 年与 1953—1957 年的点落在一条光滑的曲线上，与 1861—1913 年的曲线几乎完全重合", *F["ph_lagloop"],
         *F["ph_lagloop2"])
    has("ph_lagloop", "The loop has now disappeared")
    T = table1()
    said("他的表 1 列出这十年工资率的实际变动", 1)
    has("ph_t1_def", "column (1)", "column (2)", "lagged seven months")
    assert F["ph_t1_def"][2] == lag
    has("ph_t1_cost", "retail price index")
    # 1948 and 1949
    said("1948 年成本推动远大于需求拉动，工资的实际涨幅只略高于需求拉动", F["ph_1948cost"][0])
    r = T.loc[1948]
    assert r["cost"] > 2 * r["demand"] and 0 < r["actual"] - r["demand"] < 0.5
    has("ph_1948cost", "considerably greater than the demand pull element", "a little greater")
    said("若不是工会配合 1948 年春开始的工资限制政策", F["ph_cripps48"][0])
    has("ph_cripps48", "in the spring of 1948")
    has("ph_restraint", "the co-operation of the trade unions")
    said("1949 年工资涨得比需求拉动少得多", F["ph_1949less"][0])
    assert T.loc[1949, "actual"] < T.loc[1949, "demand"] / 2
    a, b, dv, kw = F["ph_devaluation"]
    said("1949 年 9 月英镑贬值，1950 年朝鲜战争爆发，1950 与 1951 年的进口价格涨得很快", dv,
         mon("ph_devaluation", "September"), kw, a, b)
    c1, c2 = F["ph_cost"]
    said("1951 与 1952 年，成本推动与工资的实际涨幅都大大超过需求拉动", c1, c2)
    for y in (c1, c2):
        assert T.loc[y, "cost"] > T.loc[y, "demand"] + 3 and T.loc[y, "actual"] > T.loc[y, "demand"] + 1.5, y
    y53, y54, y57, five, y50 = F["ph_demand_infl"]
    said("1950 年与 1953—1957 年，实际涨幅几乎等于需求拉动", y50, y53, y57)
    pure = [y50] + list(range(int(y53), int(y57) + 1))
    assert len(pure) == five + 1 and all(abs(T.loc[y, "actual"] - T.loc[y, "demand"]) <= 0.2 + 1e-9 for y in pure)
    assert F["ph_1950eq"][0] == y50
    # the book's recomputation
    C = crosses()
    has("ph_upper", "the upper bound being included")
    say("按菲利普斯的分组复算，六组的平均点仍顺着他的曲线往下走（本书的计算）")
    assert all(C[i]["y"] > C[i + 1]["y"] for i in range(len(C) - 1))
    said("失业最低的一组 7 年，工资平均每年涨 4.0\\%。最高的一组 8 年，平均每年跌 0.5\\%", C[0]["n"], C[0]["y"], C[-1]["n"],
         -C[-1]["y"])
    assert C[-1]["y"] < 0
    S = scatter_1861_1913()
    mad = float((S["y"] - curve(S["u"])).abs().mean())
    said("各年的点却很散，与曲线平均差约 1.5 个百分点", mad)
    # the table
    said("菲利普斯的分组，用修订数据复算，1861—1913 年", p[0], p[1])
    t = tex_text()
    for c in C:
        line = re.search(rf"^{c['lo']:g} 到 {c['hi']:g} & .*\\\\$", t, re.MULTILINE).group(0)
        said(line, c["lo"], c["hi"], c["n"], c["u"], abs(c["y"]), abs(c["curve"]))
        assert line.count("$-") == (c["y"] < 0) + (c["curve"] < 0), line
    vers = re.search(r"\(version (\d+\.\d+)\)", load_snapshot("boe_millennium_uk_1860_1958")[1]["source"]).group(1)
    bm = load_snapshot("boe_millennium_uk_1860_1958")[1]
    a50, a47 = (int(x) for x in re.search(r"'A(\d+)\. Employment & unemployment' and 'A(\d+)\. Wages and prices'",
                                           bm["source"]).groups())
    f72 = noted(r"Feinstein \((\d{4})\) and the Board of Trade \(adjusted\)", bm["series"])[0]
    said("区间与曲线据菲利普斯（1958），区间含上限", F["ph_source"][2])
    said("失业率是工会的失业率（Feinstein 1972 与贸易部的数据，经调整）", f72)
    said("都据英格兰银行《千年宏观数据》第 3.1 版表 A50 与 A47", float(vers), a50, a47)
    # the figure
    said("(a) 1861—1913 年每年的工资变动率与失业率（浅色圆点，修订数据）", p[0], p[1])
    said("方块是 1948—1957 年的修订数据", p[4], p[5])
    u0 = int(re.search(r"(\d{4})-1920 \(A50, column", bm["series"]).group(1))
    assert u0 < p[0] and "blank from 1921" in bm["series"] and "blank before 1920" in bm["series"]
    said("修订数据据英格兰银行《千年宏观数据》表 A50（1913 年以前是工会的失业率，1948 年起是 Feinstein 按占平民劳动人口的百分比估计的失业率）"
         "与表 A47", a50, p[1], p[4], a47)
    said("(b) 菲利普斯表 1 的 1948—1957 年，横轴是按滞后 7 个月的失业率从曲线算出的需求拉动", 1, p[4], p[5], lag)


def read_example(F, Y, Q):
    x1, x2 = READ_X
    said("（1）失业率是 2\\% 与 5\\% 时，工资每年变动多少？", x1, x2)
    (d1, d2), (d3, d4) = READ_DROPS
    said("（3）失业率从 5\\% 降到 4\\%，与从 2\\% 降到 1\\%，工资涨幅各多出多少？", d1, d2, d3, d4)
    a, b, c = curve_pars()
    e = -c
    said("$2^{1.394}\\approx2.628$，$y=9.638/2.628-0.9\\approx2.77$，工资每年涨约 2.8\\%", x1, e, power(x1), b, power(x1),
         a, y_of(x1), y_of(x1))
    said("$5^{1.394}\\approx9.43$，$y\\approx1.02-0.9\\approx0.12$，工资几乎不动", x2, e, power(x2), b / power(x2), a,
         y_of(x2))
    zero = curve_inverse(0)
    said("令$y=0$，$x^{1.394}=9.638/0.9\\approx10.71$，$x\\approx5.48$，约 5.5\\%，与菲利普斯说的 5.5\\% 左右相合", 0, e, b, a,
         b / a, zero, zero, F["ph_wages5"][0])
    said("（3）$y(4)\\approx0.50$，$y(1)=9.638-0.9\\approx8.74$", d2, y_of(d2), d4, b, a, y_of(d4))
    said("从 5\\% 降到 4\\%，涨幅多出约 0.37 个百分点；从 2\\% 降到 1\\%，多出约 5.97 个百分点", d1, d2, y_of(d2) - y_of(d1),
         d3, d4, y_of(d4) - y_of(d3))
    said("同样少 1 个百分点的失业", d1 - d2)
    assert d1 - d2 == d3 - d4


def prices(F, Y, Q):
    g, u = F["ph_example"]
    said("生产率每年提高 2\\%，总需求同样增长，失业保持在 2\\%", g, u)
    w, m = F["ph_example2"]
    said("这时雇主竞价让工资每年涨 3\\%，进口价格与其他要素的价格也每年涨 3\\%", w, m)
    said("零售物价就每年平均约涨 1\\%", F["ph_retail"][0])
    assert w - g == F["ph_retail"][0]
    has("ph_retail", "(the rate of change of factor costs minus the rate of change of productivity)")
    has("fr_markup", "allowing for the secular increase in productivity")
    imp, retail = F["ph_13"]
    share = F["ph_fifth"][0]
    said("进口价格每年要涨 13\\% 以上，才会抵消生产率提高的作用，让零售物价涨得比 3\\% 还快", imp, retail)
    chk("    retail prices with imports at 13 per cent (the factor costs weighted, less productivity)",
        (1 - share) * w + share * imp - g, retail, tol=1e-9)
    say("进口占国民收入的五分之一时")
    has("ph_spiral", "a further increase in retail prices", "initiating a wageprice spiral")
    p = F["ph_periods"]
    said("他认为 1861—1913 年只有 1862 年的进口价格上涨", p[0], p[1], F["ph_mild"][0])
    has("ph_support", "seems in general to support")
    g2, u_stable = F["ph_stable"]
    said("假定生产率每年提高 2\\%，要让产品价格稳定，失业率要“略低于 2.5\\%”", g2, u_stable)
    said("要让工资率稳定，失业率要在 5.5\\% 左右", F["ph_wages5"][0])
    has("ph_curvature", "strongcurvature")
    # the example
    a, b, c = curve_pars()
    e = -c
    said("生产率每年提高 2\\%，与菲利普斯的假定相同", g2)
    said("（2）失业率保持在 3\\%，物价怎样变？", STABLE_U)
    lo, hi = STABLE_SWING
    said("（3）失业率一年 1\\%、一年 5\\%，交替出现，平均也是 3\\%，工资的平均涨幅是多少？", lo, hi, (lo + hi) / 2)
    assert (lo + hi) / 2 == STABLE_U
    xs = curve_inverse(g2)
    said("（1）物价稳定要$y=g=2$，$x^{1.394}=9.638/2.9\\approx3.32$，$x\\approx2.37$，略低于 2.5\\%", g2, e, b, g2 + a,
         b / (g2 + a), xs, u_stable)
    assert xs < u_stable
    y3 = y_of(STABLE_U)
    said("（2）$y(3)\\approx1.18$，$\\pi\\approx1.18-2=-0.82$，物价每年约跌 0.8\\%", STABLE_U, y3, y3, g2, g2 - y3,
         g2 - y3)
    avg = (y_of(lo) + y_of(hi)) / 2
    said("（3）$y(1)\\approx8.74$，$y(5)\\approx0.12$，平均约 4.43\\%，比失业稳定在 3\\% 时的 1.18\\% 高得多", lo, y_of(lo),
         hi, y_of(hi), avg, STABLE_U, y3)
    # the pitfall
    has("ss_translate", "When we translate the Phillips' diagram")
    said("弗里德曼 1976 年画这条曲线时也说明", F["fr_lecture"][1])
    has("fr_shortcircuit", "relating unemployment directly to price change")


def menu_section(F, Y, Q):
    vol, no, ann, y60, p0, p1 = F["ss_issue"]
    has("ss_mit", "Massachusetts Institute of")
    has("ss_title", "Analytical Aspects of Anti-Inflation Policy")
    said("登在 1960 年 5 月的《美国经济评论》上，那一期是美国经济学会第 72 届年会的论文集", y60, mon("ss_issue", "May"), ann)
    has("ss_session", "PROBLEM OF ACHIEVING AND MAINTAINING A STABLE PRICE LEVEL")
    w5, g_lo, g_hi, u25 = F["ss_phillips5"]
    said("照他们的读法，失业 5\\% 时货币工资就会稳定", w5)
    said("失业约 2.5\\% 时，工资的涨幅能压到 2\\% 到 3\\% 的生产率增长", u25, g_lo, g_hi)
    said("这与原文的 5.5\\% 和 2\\% 略有出入", F["ph_wages5"][0], F["ph_stable"][0])
    assert w5 != F["ph_wages5"][0]
    has("ss_rees", "average hourly earnings in manufacturing", "(Rees's data)")
    said("1933—1941 年“自成一类”", *F["ss_suigeneris"])
    has("ss_suigeneris", "money wages rose or failed to fall in the face of massive unemployment")
    p20, y34 = F["ss_1934"]
    said("1934 年工资涨了 20\\%", y34, p20)
    said("到 1933 年许多失业已成为结构性的", F["ss_structural"][0])
    century = int(y60) // 100 + 1
    has("ss_early", "the first decade of the century and the twenties")
    said("20 世纪头十年与 1920 年代，失业 4\\% 或 5\\% 时制造业工资似乎就完全稳定", century, (century - 1) * 100 + 20,
         *F["ss_early"])
    said("1946 年以后的点相当一致", F["ss_postwar"][0])
    u53, y53, u58, y58 = F["ss_range"]
    said("失业率只在 1953 年的 2.5\\% 到 1958 年的 6.2\\% 之间", y53, u53, y58, u58)
    said("他们判断，现在要失业“更像是 8\\%”", F["ss_8pct"][0])
    has("ss_shift", "in the forties and fifties")
    said("这条关系在 1940 与 1950 年代略微但明显地向上移了", 1940, 1950)
    has("ss_compact", "geographicalcompactness")
    has("ss_mobility", "geographical and industrial")
    g, lo, hi = F["ss_point1"]
    said("要让工资只按 2.5\\% 的生产率增长上涨，美国似乎要有 5\\% 到 6\\% 的平民劳动力失业", g, lo, hi)
    has("ss_point1", "civilian labor force")
    u3, plo, phi = F["ss_point2"]
    said("要把失业压到 3\\%，物价每年可能要涨 4\\% 到 5\\%", u3, plo, phi)
    has("ss_fig2", "Figure 2")
    said("他们的图 2 把这些画成一条曲线", 2)
    uA, (uB, pB) = F["ss_pointA"][0], F["ss_pointB"]
    said("A 点物价稳定，失业约 5.5\\%；B 点失业 3\\%，物价每年涨约 4.5\\%", uA, uB, pB)
    assert lo <= uA <= hi and plo <= pB <= phi and uB == u3
    said("大致据过去 25 年美国的数据估计", F["ss_fig2cap"][0])
    has("ss_tug", "somewherein between these selected points")
    has("ss_down", "shift the curve downwardin the longer run")
    has("ss_up", "more and more unemployment being needed just to keep prices stable")
    said("他们提到，美国也许要 8\\% 到 10\\% 的失业才能稳住货币工资", *F["ss_810"])
    assert F["ss_forever"] == F["ss_810"]
    has("ss_bias", "inflationary bias")
    has("ss_experiment", "deliberate policy")
    has("ss_teachers", "schoolteachers, pensioners")
    # the compare box
    p = F["ph_periods"]
    said("\\begin{compare}{菲利普斯（1958）与萨缪尔森、索洛（1960）}{菲利普斯（1958）}{萨缪尔森与索洛（1960）}", F["ph_source"][2],
         y60, F["ph_source"][2], y60)
    said("\\cmprow{数据}{英国 1861—1957 年，分三段处理\\cite{phillips1958}}{美国 20 世纪以来，菜单大致据过去 25 年估计",
         p[0], p[5], century, F["ss_fig2cap"][0])
    said("\\cmprow{工资稳定的失业率}{5.5\\% 左右\\cite{phillips1958}}{战后要更像是 8\\%", F["ph_wages5"][0], F["ss_8pct"][0])
    said("\\cmprow{物价稳定的失业率}{略低于 2.5\\%，生产率增长按 2\\%\\cite{phillips1958}}{5\\% 到 6\\%，生产率增长按 2.5\\%",
         F["ph_stable"][1], F["ph_stable"][0], lo, hi, g)
    # Table C-24
    has("e71_c24_cols", "All workers", "Both sexes 16-19 years", "White Negro and other races",
        "Experienced wage and salary workers Married men")
    row = F["e71_c24_1961"]
    a16, b19 = F["e71_c24_cols"]
    cols = ["year", "all", "16-19", "men20", "women20", "white", "negro", "experienced", "married"]
    R = dict(zip(cols, row))
    said("按 1971 年《总统经济报告》的表 C-24，1961 年全体劳动者的失业率是 6.7\\%", F["e71_title"][0], F["e71_c24_title"][0],
         R["year"], R["all"])
    said("16 到 19 岁的人是 16.8\\%", a16, b19, R["16-19"])
    said("“黑人及其他种族”是 12.4\\%，“与妻子同住的已婚男子”只有 4.6\\%", R["negro"], R["married"])
    assert R["all"] == F["erp_magnified"][1]                                     # the 1962 Report's 6.7 per cent
    # the example
    said("A 点失业 5.5\\%、物价不变，B 点失业 3\\%、物价每年涨 4.5\\%", uA, uB, pB)
    said("（2）一位退休教师每年领 1,000 美元的养老金", PENSION)
    said("在 B 点过 5 年", PENSION_YEARS)
    y61, lab = F["erp_labor"]
    said("（3）1961 年美国的劳动力约 7,160 万人", y61, lab * 1e6)
    said("失业率低 2.5 个百分点，大约多少人有了工作？", uA - uB)
    said("（1）失业率低 2.5 个百分点，通胀率高 4.5 个百分点", uA - uB, pB)
    f = (1 + pB / 100) ** PENSION_YEARS
    said("$1{,}000/1.045^{5}\\approx1{,}000/1.246\\approx802$，约 802 美元，购买力少了约五分之一", PENSION, 1 + pB / 100,
         PENSION, f, PENSION / f, PENSION / f)
    assert abs(1 - 1 / f - 0.2) < 0.01
    said("（3）$7{,}160\\times2.5\\%\\approx179$，约 179 万人", lab * 100, uA - uB, lab * 100 * (uA - uB) / 100,
         lab * 1e6 * (uA - uB) / 100)
    # the record
    M = menu()
    said("\\figref{fig:phillips_menu}(a) 把 1948—1969 年美国的失业率与消费物价的年涨幅画在一起", F["e71_c24_title"][1],
         FIG_US[1])
    u69, i69 = M.loc[1969, "us_unemp_pct"], M.loc[1969, "us_infl"]
    said("1969 年的失业率是 3.5\\%，消费物价涨了约 5.4\\%，两项都比 B 点差", 1969, u69, i69)
    assert u69 > uB and i69 > pB
    assert u69 == F["e71_c24_1969"][1]
    chk("    1969 against 1968 (Table C-45)", 100 * (F["e71_c45_1969"][0] / F["e71_c45_1968"][0] - 1), i69, tol=1e-9)
    S = M.loc[1960:1964]
    said("1960—1964 年失业在 5.2\\% 到 6.7\\% 之间。这几年物价每年只涨 1.0\\% 到 1.6\\%", 1960, 1964,
         S["us_unemp_pct"].min(), S["us_unemp_pct"].max(), S["us_infl"].min(), S["us_infl"].max())
    # the figure
    said("(a) 美国 1948—1969 年的失业率（横轴，\\%）与城市工薪劳动者消费物价指数的年涨幅（纵轴，\\%），数据据 1971 年《总统经济报告》"
         "表 C-24 与 C-45；A、B 是萨缪尔森与索洛（1960）图 2 上的两个点", F["e71_c24_title"][1], FIG_US[1],
         F["e71_title"][0], F["e71_c24_title"][0], F["e71_c45_title"][0], y60, 2)
    has("e71_c45_title", "For city wage earners and clerical workers")
    d1, d2 = F["hs_d491_title"][:2]
    k1, k2 = F["hs_k8_title"][:2]
    said("(b) 加拿大 1950—1969 年的失业率与消费物价指数的年涨幅，1956—1961 年的点按年份连线并标出年份，数据据《加拿大历史统计》表 D491—497 与 "
         "K8—18", FIG_CA[0], FIG_CA[1], F["hs_d491_1956"][0], F["hs_d491_1961"][0], d1, d2, k1, k2)
    assert FIG_CA[0] == F["hs_d491_fn2"][0]                                      # Newfoundland included from 1950


FIG_US = (1948, 1969)                # fig:phillips_menu (a): Table C-24 begins in 1948; the 1970s are Chapter 44's
FIG_CA = (1950, 1969)                # fig:phillips_menu (b): Newfoundland in Canada's total from 1950


def case(F, Y, Q):
    said("\\begin{case}{加拿大 · 1956—1961 · 菜单的另一边}", F["hs_d491_1956"][0], F["hs_d491_1961"][0])
    D = {y: F[f"hs_d491_{y}"] for y in (1956, 1957, 1958, 1961)}
    said("加拿大的失业率 1956 年是 3.4\\%，1957 年是 4.6\\%，1958 年升到 7.0\\%", 1956, D[1956][1], 1957, D[1957][1], 1958,
         D[1958][1])
    has("hs_d491_cols", "Year,, Canada total2,Atlantic region2,Quebec,Ontario,Prairie region,British Columbia,Newfoundland")
    powell = their("mundell_facts", "pw_unemp", "7.2 per cent in 1961")
    said("1961 年是 7.1\\%，比 Powell 书里的 7.2\\% 低一点（\\chref{ch:mundell}）", 1961, D[1961][1], powell[2])
    assert powell[3] == 1961 and powell[2] > D[1961][1]
    K = {y: F[f"hs_k8_{y}"][1] for y in (1956, 1957, 1960, 1961)}
    M = menu()
    for y in K:
        assert M.loc[y, "ca_cpi_1971_100"] == K[y], y
    for y in D:
        assert M.loc[y, "ca_unemp_pct"] == D[y][1], y
    said("同一时期的消费物价，1957 年涨了约 3.2\\%，1961 年只涨约 0.9\\%", 1957, 100 * (K[1957] / K[1956] - 1), 1961,
         100 * (K[1961] / K[1960] - 1))
    cols = ["year", "canada", "atlantic", "quebec", "ontario", "prairie", "bc", "newfoundland"]
    R = dict(zip(cols, D[1961]))
    said("1961 年，安大略的失业率是 5.5\\%，大西洋地区是 11.2\\%，纽芬兰是 19.5\\%", 1961, R["ontario"], R["atlantic"],
         R["newfoundland"])
    has("hs_d491_fn1", "Excludes the Yukon Territory, the Northwest Territories and Indians on reserves.")
    say("这些数字不含育空、西北地区与保留地上的印第安人")
    ca = M.loc[1956:1961]
    assert ca["ca_unemp_pct"].iloc[-1] > ca["ca_unemp_pct"].iloc[0] and ca["ca_infl"].iloc[-1] < ca["ca_infl"].iloc[1]
    said("1947 年夏天他在渥太华，帮加拿大政府建了一系列计量模型里的第一个", F["nbb_ottawa"][0])
    has("nbb_ottawa", "summer of 1947 in Ottawa", "the first of a series of econometric models for the Canadian government")


def gap(F, Y, Q):
    said("\\section{产出缺口与 4\\% 的目标}", F["erp_target"][0])
    said("凯恩斯 1940 年用计划的支出与产能之差判断通胀的压力", there("ch34_warfinance", "1940 年 2 月，凯恩斯")[0])
    chk("    twenty-odd years later (二十多年后)", F["erp_title"][0] - 1940, 22)
    say("二十多年后，美国总统经济顾问委员会算的是另一种缺口")
    has("erp_gap49", "between actual gross national product (GNP) and the output obtainable at full employment")
    said("1962 年的论文问，充分就业时经济能生产多少", F["ok_reprint"][0])
    has("ok_question", "How much output can the economy produce under conditions of full employment?")
    has("ok_staff", "while I served on the Staff of the Council of Economic Advisers")
    has("ok_balance", "a point of balance between more output and greater stability")
    four = cardinal("four")
    has("ok_agreement", "a four percent unemployment rate is a reasonable target")
    said("经济学家对 4\\% 是合理目标的共识", four)
    has("ok_target", "the four percent unemployment rate", "only the numbers would be changed")
    said("他把 4\\% 定为论文计算潜在产出所用的目标", four)
    u4, three = F["ok_answer"]
    has("ok_answer", "each extra percentage point in the unemployment rate above four percent")
    said("战后平均而言，失业率在 4\\% 以上每多 1 个百分点，实际国民生产总值就少约 3\\%", u4, 1, three)
    chk("    three methods (三种方法)", told("他用了三种方法", "用了", "种"), F["ok_three"][0])
    n, y47, y60 = F["ok_first"]
    has("ok_first", "55 quarterly observations from 1947-II to 1960-IV")
    said("第一种用季度的变动，1947 年第二季度到 1960 年第四季度共 55 个观测，失业率高 1 个百分点，产出少 3.3\\%", y47, y60,
         n, 1, F["ok_33"][0])
    has("ok_33", "one percentage point more in the unemployment rate means 3.3 percent less GNP")
    said("第二种试算潜在产出的几条路径，失业率对缺口的斜率在 0.28 到 0.38 之间", *F["ok_slopes"])
    has("ok_trial", "Trial gaps")
    said("第三种同时估计趋势与弹性，弹性在 0.35 到 0.40 之间", *F["ok_elastic"][:2])
    has("ok_method3", "Fitted trend and elasticity")
    said("他把这些系数“主观加权”平均，得到 3.2，写成", F["ok_weighted"][2])
    one, k, u0 = F["ok_rule"]
    five = F["ok_five"]
    said("失业 4\\% 时，潜在产出等于实际产出；失业 5\\% 时，缺口是 GNP 的 3.2\\%", five[0], five[1], five[2])
    chk("    the rule at 5 per cent", 100 * k * (five[1] - u0), five[2], tol=1e-9)
    assert k * 100 == F["ok_weighted"][2] and u0 == five[0]
    lo, hi, k3, e1, e15 = F["ok_range"]
    said("样本里的失业率只在约 3\\% 到 7.5\\% 之间", lo, hi)
    said("失业若是 1\\% 或 15\\%，他说没有理由指望 3.2 的系数还适用", e1, e15, k3)
    g0, g1, s0, s1 = F["ok_grade"]
    said("把失业率降低 1.5 个百分点，就业的“分数”只是从 94.5 提到 96", g0 - g1, s0, s1)
    assert (100 - g0, 100 - g1) == (s0, s1)
    # the Report of January 1962
    said("1962 年 1 月，《总统经济报告》把 4\\% 写成了目标", F["erp_title"][0], mon("erp_title", "January"),
         F["erp_target"][0])
    has("erp_conquest", "it is surely an indispensable beginning")
    has("erp_signature", "John F. Kennedy")
    four_, fifteen, seven, twothirds, u4b = F["erp_twothirds"]
    said("战后有三分之二的月份，能工作、愿意工作、也在找工作的人当中有 4\\% 以上找不到工作", u4b)
    assert abs(twothirds - 2 / 3) < 1e-9
    has("erp_twothirds", "4 percent or more of those able, willing, and seeking to work")
    said("为了工作的需要，我们把 4\\% 的失业率看作一个临时的目标", F["erp_target"][0])
    said("他说这个目标 1963 年可以达到，复苏也必须不危及过去 4 年的物价稳定", F["erp_1963"][0], F["erp_price"][0])
    has("erp_dignity", "Involuntary unemployment")
    chk("    three reasons (三条理由)", told("报告列出关心失业的三条理由", "的", "条理由"), F["erp_reasons"][0])
    has("erp_reasons", "the human obligation to prevent and to relieve economic distress", "choose freely how to use his time",
        "the economic waste of leaving productive resources idle")
    has("erp_zero", "But zero unemployment is unattainable.", "A feasible interim goal")
    has("erp_partial", "is only partial")
    said("在当时的情况下，约 4\\% 的失业率是“稳定政策一个合理而审慎的充分就业目标”", F["erp_reasonable"][0])
    said("4\\% 的失业是一个不高的目标，但必须强调", F["erp_modest"][0])
    u4c, y55, y57, lo, hi = F["erp_1955"]
    said("经济上一次处在 4\\% 左右，是 1955 年 5 月到 1957 年 8 月，失业率在 3.9\\% 到 4.4\\% 之间", u4c, y55,
         mon("erp_1955", "May"), y57, mon("erp_1955", "August"), lo, hi)
    has("erp_competitive", "impaired the competitiveness of some U.S. products in world markets")
    has("erp_sobering", "sobering")
    said("报告认为，这样的压力并不是经济在 4\\% 附近运行时", F["erp_notpermanent"][0])
    has("erp_notpermanent", "when it is operating in the neighborhood of 4 percent unemployment")
    y61, g51, _, g28 = F["erp_gap49"]
    said("1961 年第一季度，实际 GNP 比充分就业时的产出少 510 亿美元，按 1961 年价格的年率计", y61, g51 * 1e9, y61)
    has("erp_gap49", "In the first quarter of 1961", "(1961 prices, annual rate)", "By the last quarter of the year")
    said("到第四季度，缺口缩小到约 280 亿美元，全年平均低于潜在产出 400 亿美元", g28 * 1e9, F["erp_gap50"][1] * 1e9)
    said("失业率每向 4\\% 前进 1 个百分点，在战后的扩张时期意味着总产出约增加 3\\%", F["erp_3pct"][0], 1, F["erp_3pct"][1])
    has("erp_restrict", "keeping the economy far below full employment")
    has("erp_pool", "vocational training and retraining")
    has("erp_resistance", "resistance to technological progress")
    # the example
    _, un, _, lab, two, u4d = F["erp_jobs"]
    said("\\begin{example}{1961 年的缺口}", F["erp_jobs"][0])
    u61 = F["erp_magnified"][1]
    said("1961 年美国的失业率是 6.7\\%，失业 480 万人，劳动力 7,160 万人", y61, u61, un * 1e6, lab * 1e6)
    chk("    4.8/71.6 (6.7 per cent)", 100 * un / lab, u61, tol=0.05)
    said("与报告“约 8\\%”的说法比较", F["erp_magnified"][4])
    said("（2）失业率若是 4\\%，失业的人有多少？", u4d)
    gap_ = k * (u61 - u0)
    said("（1）$0.032\\times(6.7-4)=0.0864$，高约 8.6\\%", k, u61, u0, gap_, 100 * gap_)
    rule = F["erp_3pct"][1]
    said("报告用“约 3\\%”的经验关系，$2.7\\times3\\%\\approx8.1\\%$，与“约 8\\%”相合", rule, u61 - u0, rule,
         rule * (u61 - u0), F["erp_magnified"][4])
    at4 = lab * 100 * u4d / 100
    said("（2）$7{,}160\\times4\\%\\approx286$万人，$480-286=194$万人，约 200 万人", lab * 100, u4d, at4, un * 100,
         round(at4), un * 100 - round(at4), two * 1e6)
    emp = lab * 100 - un * 100
    jobs = un * 100 - round(at4)
    said("实际就业是$7{,}160-480=6{,}680$万人，$194/6{,}680\\approx2.9\\%$，即报告说的约 3\\%", lab * 100, un * 100, emp, jobs,
         emp, 100 * jobs / emp, F["erp_magnified"][3])
    said("就业只多 3\\%，产出却多约 8\\%", F["erp_magnified"][3], F["erp_magnified"][4])
    has("erp_favorable", "a number of other favorable effects on output")
    has("erp_table2", "Larger labor force", "Longer hours of work", "Greater productivity per man-hour")


def models_section(F, Y, Q):
    said("1936 年 9 月的牛津会议上", *there("ch33_islm", "1936 年 9 月的牛津"))
    said("介绍了他用约 12 个方程描述战后美国经济周期的尝试（\\chref{ch:islm}）",
         *there("ch33_islm", "介绍了他用约 12 个方程描述战后美国经济周期的尝试"))
    has("nbb_samuelson", "my dissertation under Paul Samuelson", "the Cowles Commission of the University of Chicago")
    has("nbb_reviving", "early attempts at econometric model building for the United States")
    a, b = F["kl_title"]
    no, a2, b2, y50 = F["kl_cfm"][:4]
    said("1950 年，他出版了《美国的经济波动，1921—1941》，是考尔斯委员会的一本专著", F["kl_imprint"][0], a, b)
    assert (a, b, y50) == (a2, b2, F["kl_imprint"][0]) and no == F["kl_page"][0]
    has("kl_cfm", "Economic Fluctuations in the United States, 1921-1941, by LAWRENCE R. KLEIN")
    said("序言说，这本书出自 1944—1947 年考尔斯委员会里经济学家与数理统计学家的密切合作", *F["kl_preface"])
    has("kl_preface", "great mutual cooperation among economists and mathematical statisticians")
    has("kl_tentative", "a relatively small number of annual observations", "another strong reason")
    has("kl_running", "MODEL I, A SIMPLE THREE-EQUATION SYSTEM")
    has("kl_definitional", "three definitional equations that are not subject to random error",
        "have no unknown parameters")
    chk("    three definitional equations (三个定义式)", told("再加三个不含随机误差", "再加", "个"), cardinal("three"))
    has("kl_investment", "the rate of change of the capital stock")
    has("kl_inventories", "The net change in inventories (whether desired or not) is included in I")
    has("kl_wagebill", "W2, the government wage bill", "The private wage bill will be represented by W1")
    has("kl_tax", "business taxes, represented by the symbol T")
    has("kl_est_c", "0.23Π-1")
    said("下标$-1$指上一年", 1)
    has("kl_g", "goods demanded by the government and foreigners (G)")
    has("kl_g_fn", "The foreign demand is net of imports.")
    said("除时间$t$以外，所有变量都按 1934 年的美元计，单位是十亿美元", F["kl_units"][0])
    has("kl_units", "All variables except t are measured in billions of 1934 dollars.")
    has("kl_real", 'purely a "real" system', "the quantity of money plays no role")
    has("kl_simplify", "simplifying assumption")
    said("他的工资方程决定的是以 1934 年美元计的工资总额", F["kl_units"][0])
    has("kl_identify", "the conditions for identifiability")
    has("kl_special", "all government variables are identically zero", "no lags or trends")
    has("kl_insure", "the lags and trends actually insure the identification here")
    said("他用 1921—1941 年每一年的数据，以最大似然法估计，并假定各方程的扰动互不相关", *F["kl_data"])
    has("kl_ml", "The method of maximum likelihood")
    has("kl_rho", "no correlation between the disturbances")
    has("kl_reasonable", "all have the signs that we should expect")
    p = F["ph_periods"]
    said("\\cmprow{例子}{菲利普斯 1861—1913 年的曲线\\cite{phillips1958}}{克莱因的模型 I，1921—1941 年", p[0], p[1], a, b)
    # the example
    k = klein_coef()
    cf = klein_closed()
    said("政府对产品的需求$G$从某一年起永久增加 1（十亿 1934 年美元）", DG, F["kl_units"][0])
    wx = k["w_x"]
    said("$\\Delta X$中工资占$0.42$，利润$\\Delta\\Pi=\\Delta X-\\Delta W_1=0.58\\,\\Delta X$", wx, 1 - wx)
    cons = k["c_p"] * (1 - wx) + k["c_w"] * wx
    inv = k["i_p"] * (1 - wx)
    said("消费增加$0.02\\times0.58+0.80\\times0.42\\approx0.348$倍的$\\Delta X$，投资增加$0.23\\times0.58\\approx0.133$倍",
         k["c_p"], 1 - wx, k["c_w"], wx, cons, k["i_p"], 1 - wx, inv)
    said("$\\Delta X=0.348\\,\\Delta X+0.133\\,\\Delta X+1$，$\\Delta X=1/0.519\\approx1.93$", cons, inv, DG, DG,
         1 - cons - inv, cf["impact"])
    chk("    the impact multiplier, closed form = the first year of the path", cf["impact"], klein_path(1)["X"].iloc[0],
        tol=1e-12)
    w = wx + k["w_x1"]
    consL = (k["c_p"] + k["c_p1"]) * (1 - w) + k["c_w"] * w
    said("工资占$0.42+0.16=0.58$，利润占$0.42$，消费增加$0.25\\times0.42+0.80\\times0.58\\approx0.569$倍", wx, k["w_x1"], w,
         1 - w, k["c_p"] + k["c_p1"], 1 - w, k["c_w"], w, consL)
    said("$\\Delta X=1/0.431\\approx2.32$", DG, 1 - consL, cf["long"])
    said("投资方程给出$0.78\\times0.42\\times2.32=0.15\\,\\Delta K$，$\\Delta K\\approx5.07$", k["i_p"] + k["i_p1"], 1 - w,
         cf["long"], -k["i_k"], cf["capital"])
    path = klein_path(400)
    chk("    the path converges to the long-run multiplier", path["X"].iloc[-1], cf["long"], tol=1e-6)
    chk("    and the capital stock to its long-run change", path["K"].iloc[-1], cf["capital"], tol=1e-6)
    X = path["X"]
    peak = int(X.loc[:10].idxmax())
    trough = int(X.loc[peak:20].idxmin())
    said("第 4 年$X$升到约 5.5", peak, X.loc[peak])
    said("第 11 年回落到约 1.4，再慢慢趋近 2.32", trough, X.loc[trough], cf["long"])
    assert (X.loc[2:peak].diff().dropna() > 0).all() and X.loc[trough] < cf["long"]
    say("利润上升，第二年投资更多")
    assert path["I"].loc[2] > path["I"].loc[1]
    # the figure
    said("政府对产品的需求从第 1 年起永久增加 1，单位是十亿 1934 年美元", 1, DG, F["kl_units"][0])
    said("虚线是冲击乘数 1.93 与长期乘数 2.32", cf["impact"], cf["long"])
    said("虚线是长期的 5.07。系数据克莱因（1950）", cf["capital"], F["kl_imprint"][0])
    # the cycle; the Nobel pages
    say("投资取决于利润，利润随产出走，资本积累起来又压低投资，产出于是一起一伏")
    said("瑞典皇家科学院 1980 年的新闻稿说", F["nb_date"][1])
    has("nb_tinbergen", "the analysis of business conditions and price movements")
    has("nb_aim", "an instrument for forecasting", "studying the effects of economic-political measures")
    has("nb_famous", "in collaboration with Arthur Goldberger")
    has("nbb_goldberger", "my student, Arthur Goldberger", "a series of generations of the Michigan Model")
    said("新闻稿说，到 1950 年代，他的美国模型已成为短期预测的成功工具", F["nb_forecasts"][0])
    has("nb_forecasts", "In the course of the 1950s", "a successful instrument for short-term forecasts")
    said("1980 年他获得诺贝尔经济学奖，理由是建立计量经济模型", F["nbf_name"][0])
    has("nbf_motivation", "the application to the analysis of economic fluctuations and economic policies")


def debate(F, Y, Q):
    y60 = F["ss_issue"][3]
    said("\\subsubsection{1960 年代的经济学家相信稳定的菜单吗}", y60)
    said("第一个争论是 1960 年代的经济学家是否相信有一张稳定、可以利用的菜单", y60)
    said("弗里德曼 1976 年回顾，这条关系当时被普遍理解为因果关系", F["fr_lecture"][1])
    has("fr_causal", "widely interpreted as a causal relation")
    has("fr_busied", "from evidence for different countries and periods")
    has("fr_tool", "a reliable tool for economic policy")
    has("fr_sceptical", "Some of us were sceptical from the outset", "primarily on theoretical rather than empirical grounds")
    has("fr_dissenters", "a few dissenters questioned its validity")
    has("ss_shortrun", "in short-run terms")
    has("ss_nojudge", "we shall not attempt to give judgment on them")
    said("1962 年的报告说，失业率目标不是不可更改的定义，4\\% 只是“临时的目标”", F["erp_title"][0], F["erp_target"][0])
    said("报告也确实按 4\\% 算了缺口", F["erp_magnified"][0])
    has("erp_magnified", "An unemployment rate of 4.0 percent instead of 6.7 percent for 1961")
    # Fisher
    no, y26 = F["fi_issue"]
    said("1926 年 6 月在国际劳工组织的《国际劳工评论》上发表《失业与物价变动的统计关系》", y26, mon("fi_issue", "JUNE"))
    has("fi_title", "A Statistical Relation between Unemployment and Price Changes")
    has("fi_author", "Professor Irving FISHER", "Yale University")
    said("在 1915—1925 年这段重要的时期，美国美元价值的变动率与失业的相关系数“高达 90\\%”", *F["fi_90"])
    has("fi_90", "the significant period", "Pearsonian correlation")
    has("fi_distributed", "the method of distributed lag")
    has("fi_spread", "about three per cent. of the effect will be felt in a month")
    said("用固定的滞后，相关最高只有 79\\%，是滞后 4 个月时的", *F["fi_fixed"])
    a, b = F["fi_violent"]
    said("这些数都来自 1915 年 9 月到 1924 年 12 月", a, mon("fi_violent", "September"), b, mon("fi_violent", "December"))
    has("fi_violent", "violent price changes", "the correlation is less")
    has("fi_third", "some third influence", "a forecast of good or bad business", "I have little doubt")
    has("fi_contract", "contractually fixed", "interest on bonds", "salaries")
    has("fi_costliving", "it raises the cost of living against him")
    p = F["ph_periods"]
    chk("    almost a hundred years (将近一百年)", told("菲利普斯量的是货币工资率，跨了将近一百年", "将近", "年"), 100)
    assert 90 < p[5] - p[0] < 100
    said("费雪量的是物价，主要靠 1915—1924 年的月度数据", a, b)


def deeper(F, Y, Q):
    src = meta()["sources"]
    notes = meta()["notes"]
    hosts = {k: re.match(r"https://([^/]+)/", src[k]["url"]).group(1) for k in src}
    assert hosts["phillips1958"].endswith(".it") and hosts["samuelson1960"].endswith(".it")
    assert hosts["phillips1958"] != hosts["samuelson1960"]
    has("ph_jstor", "http://www.jstor.org/stable/")
    has("ss_jstor", "http://www.jstor.org/stable/")
    said("菲利普斯（1958）与萨缪尔森、索洛（1960）据两所意大利大学课程网页上的 PDF，都是 JSTOR 的扫描本", F["ph_source"][2],
         F["ss_issue"][3])
    say("文字层把许多词连在一起，数字也常读错，引文照文字层原样核对，数字按页面图像读")
    assert src["phillips1958img"]["format"] == "image" and src["phillips1958img"]["url"] == src["phillips1958"]["url"]
    assert src["okun1962"]["format"] == src["klein1950"]["format"] == "image"
    assert hosts["klein1950"] == hosts["cowles_okun38"] == "cowles.yale.edu"
    has("ok_page", "Publication Link Potential GNP: Its Measurement and Significance")
    said("奥肯（1962）是考尔斯基金会网页链到的扫描本，克莱因（1950）是考尔斯基金会网站上的全书扫描", F["ok_reprint"][0],
         F["kl_imprint"][0])
    assert "a blank page: the scan has no copyright page" in column("note")["kl_nocopyright"]
    assert hosts["erp1962"] == hosts["erp1971"] == "presidency.ucsb.edu"
    said("1962 年与 1971 年的《总统经济报告》据美国总统资料项目网站上的 PDF", F["erp_title"][0], F["e71_title"][0])
    assert "the President's handwritten signature under the letter of transmittal and under his report" in column(
        "note")["erp_signature"]
    assert hosts["friedman1976"] == "www.nobelprize.org" and src["friedman1976"]["format"] == "pdf"
    assert "/public/libdoc/" in src["fisher1926ilr"]["url"] and hosts["fisher1926ilr"].endswith("ilo.org")
    said("费雪（1926）据国际劳工组织图书馆的扫描本", F["fi_issue"][1])
    # the misreadings (check_text() has the quotations)
    said("他的“略低于 2.5\\%”读作“2~”，“5.5\\% 左右”读作“51”，曲线的系数读作“9*638”与“1394”", F["ph_stable"][1],
         *printed("ph_stable_text", "2~"), F["ph_wages5"][0], *printed("ph_wages5_text", "about 51 per"),
         *printed("ph_curve_text", "9*638"), *printed("ph_curve_text", "1394"))
    said("萨缪尔森与索洛的 5.5\\% 与 4.5\\% 读作“512”与“412”，2.5\\% 读作“2Y2”与“2'2”", F["ss_pointA"][0],
         F["ss_pointB"][1], *printed("ss_pointA", "512"), *printed("ss_pointB", "412"), F["ss_phillips5"][3],
         *printed("ss_phillips5", "2Y2"), *printed("ss_point1", "2'2"))
    said("1971 年报告表 C-45 的 1968 年与 1969 年两行，年份读作“1958”与“1989”，本书按行的位置读", F["e71_title"][0],
         F["e71_c45_title"][0], 1968, 1969, *printed("e71_c45_1968", "1958 104.2")[:1],
         *printed("e71_c45_1969", "1989 109.8")[:1])
    # the disagreements
    w5, g_lo, g_hi, _ = F["ss_phillips5"]
    said("萨缪尔森与索洛说菲利普斯的工资在失业 5\\% 时稳定，生产率增长是 2\\% 到 3\\%；菲利普斯自己写的是 5.5\\% 左右与 2\\%", w5, g_lo,
         g_hi, F["ph_wages5"][0], F["ph_stable"][0])
    assert "(ss_phillips5)" in notes and "(ph_wages5)" in notes and "(ph_stable)" in notes
    assert "(nb_citation)" in notes and "(nbf_motivation)" in notes
    powell = their("mundell_facts", "pw_unemp", "7.2 per cent in 1961")
    said("加拿大 1961 年的失业率，Powell 写作 7.2\\%，《加拿大历史统计》是 7.1\\%", 1961, powell[2], F["hs_d491_1961"][1])
    assert "(hs_d491_1961)" in notes
    said("1948 年以后的失业率，本书用的是占平民劳动人口的百分比", F["ph_periods"][4])
    # single witnesses
    for rid in ("ph_curve", "ph_fit", "ss_pointA", "ss_pointB", "ok_weighted", "erp_gap49", "erp_jobs", "kl_est_c"):
        assert rid in notes.split("Single witnesses:")[1].split("Indirect testimony")[0], rid
    said("菲利普斯的曲线、分组与表 1，萨缪尔森与索洛的两个点，奥肯的系数，1962 年报告的缺口与劳动力", 1, F["erp_title"][0])
    said("诺贝尔奖的新闻稿与获奖信息页把克莱因 1950 年的研究说成一篇论文", F["nb_paper1950"][0])
    assert F["nbf_paper1950"][0] == F["nb_paper1950"][0]
    has("nb_paper1950", "publishing a paper in 1950")
    has("nbf_paper1950", "publishing a paper in 1950")
    # not obtained
    nl = notes.split("Not obtained:")[1].split("Life dates:")[0]
    (lip,) = noted(r"Lipsey \((\d{4})\)", nl)
    said("Lipsey（1960）关于菲利普斯曲线的理论", lip)
    has("ph_ack", "Dr. R. G. Lipsey for comments on an earlierdraft")
    said("archive.org 只有 1964 年北荷兰出版社印本的借阅本", F["ar_kg"][0])
    has("ar_kg_pub", "North Holland")
    has("ar_kg_lending", "inlibrary")
    k39, h44, m44, a59, f73, f14 = noted(r"Keynes's review of Tinbergen \((\d{4})\) and Tinbergen's reply; Haavelmo "
                                         r"\((\d{4})\); Modigliani \((\d{4})\); Adelman and Adelman \((\d{4})\); the reprint "
                                         r"of Fisher \(1926\) in the Journal of Political Economy \((\d{4})\); Forder "
                                         r"\((\d{4})\)", nl)
    said("凯恩斯 1939 年对丁伯根的评论与丁伯根的回答、Haavelmo（1944）、莫迪利亚尼（1944）、Adelman 与 Adelman（1959）、费雪 1973 "
         "年的重印本与 Forder（2014）也没有取得", k39, h44, m44, a59, f73, f14)
    assert "the American Economic Association's pages did not open" in nl and "the Hansard website refused access" in nl
    say("萨缪尔森与索洛宣读论文的日期，美国经济学会的网页没有打开", "英国下院议事录的网站拒绝访问，正文不写英国后来时紧时松的需求政策")
    # the life dates
    said("奥肯，德国国家图书馆与法国国家图书馆都只有 1928 年的生年", F["gnd_okun_born"][0])
    assert F["bnf_okun"] == F["gnd_okun_born"] == F["bnf_okun_born"] and "gnd_okun_died" not in F
    assert Q["loc_okun"] == "Okun, Arthur M." and "loc_okun" not in F
    assert Q["loc_solow"] == "Solow, Robert M." and F["loc_goldberger"] == [1930]
    say("国会图书馆的记录里，索洛没有年份，戈德伯格只有生年")


def legacy(F, Y, Q):
    has("fr_rise", "did not remain fixed", "it tended in any one country to rise over time")
    has("fr_stagflation", "simultaneous high inflation and high unemployment", '"stagflation"')
    has("nb_brookings", "The Brookings-SSRC Project")
    has("nb_wharton", "The Wharton Econometric Forecasting Model")
    has("nb_link", '"LINK"')
    said("2021—2023 年的通胀又让人重新讨论它（\\chref{ch:inflation21}）", *there("ch74_inflation21",
                                                                         "\\chapter{2021—2023 年通胀}"))
    say("1962 年的报告把 4\\% 叫作临时的目标，说当前的经验必须是向导")
    said("1962 年的报告把 4\\% 叫作临时的目标", F["erp_title"][0], F["erp_target"][0])
    has("erp_commit", "Current experience must therefore be the guide")


def takeaways(F, Y, Q):
    a, b, c = curve_pars()
    p = F["ph_periods"]
    said("菲利普斯（1958）用 1861—1913 年英国的工资率与工会失业率，按失业率分组取平均，拟合出$y+0.900=9.638\\,x^{-1.394}$",
         F["ph_source"][2], p[0], p[1], a, b, -c)
    said("工资稳定的失业率约 5.5\\%", F["ph_wages5"][0])
    said("菲利普斯据此推出，生产率每年提高 2\\% 时，物价稳定的失业率略低于 2.5\\%", *F["ph_stable"])
    said("萨缪尔森与索洛（1960）把曲线搬到美国、换成物价，画成“选择的菜单”，物价稳定要失业约 5.5\\%，失业 3\\% 要物价每年涨约 4.5\\%",
         F["ss_issue"][3], F["ss_pointA"][0], *F["ss_pointB"])
    said("奥肯（1962）估计，失业率在 4\\% 以上每多 1 个百分点，产出约少 3\\%。1962 年的《总统经济报告》把 4\\% 当作临时的目标",
         F["ok_reprint"][0], F["ok_answer"][0], 1, F["ok_answer"][1], F["erp_title"][0], F["erp_target"][0])
    say("并说失业的代价由整个经济、尤其是失业者承担")
    has("erp_equity", "the economy as a whole, and the unemployed in particular, would suffer")
    cf = klein_closed()
    said("克莱因的模型 I 用三个行为方程与三个定义式描述 1921—1941 年的美国，冲击乘数约 1.93，长期乘数约 2.32",
         *F["kl_data"], cf["impact"], cf["long"])
    said("1960 年代的经济学家是否相信稳定的菜单", F["ss_issue"][3])


def selfcheck(F, Y, Q):
    a, b, c = curve_pars()
    e = -c
    u1, u2 = SC_U
    said("用式~\\eqref{eq:phillips-curve}，失业率是 3\\% 时工资每年变动多少？是 8\\% 时呢？", u1, u2)
    said("若生产率每年提高 3\\%，按式~\\eqref{eq:phillips-prices}，物价稳定的失业率约是多少？比生产率提高 2\\% 时高还是低？", SC_G,
         F["ph_stable"][0])
    said("按式~\\eqref{eq:phillips-okun}，失业率是 5.5\\% 时，缺口是多少？", SC_OKUN)
    k = klein_coef()
    said("若工资方程里当年产出的系数从 0.42 降到 0.30", k["w_x"], SC_WX)
    # the answers
    said("$3^{1.394}\\approx4.62$，$y\\approx2.08-0.9\\approx1.18$，每年约涨 1.2\\%", u1, e, power(u1), b / power(u1), a,
         y_of(u1), y_of(u1))
    said("$8^{1.394}\\approx18.15$，$y\\approx0.53-0.9\\approx-0.37$，每年约跌 0.4\\%", u2, e, power(u2), b / power(u2), a,
         -y_of(u2), -y_of(u2))
    assert y_of(u2) < 0
    xs, x2 = curve_inverse(SC_G), curve_inverse(F["ph_stable"][0])
    said("物价稳定要$y=3$，$x^{1.394}=9.638/3.9\\approx2.47$，$x\\approx1.91$，约 1.9\\%，比生产率提高 2\\% 时的 2.37\\% 低", SC_G, e,
         b, SC_G + a, b / (SC_G + a), xs, xs, F["ph_stable"][0], x2)
    assert xs < x2
    one, kk, u0 = F["ok_rule"]
    said("$0.032\\times(5.5-4)=0.048$，潜在产出比实际产出高约 4.8\\%", kk, SC_OKUN, u0, kk * (SC_OKUN - u0),
         100 * kk * (SC_OKUN - u0))
    spend_p = k["c_p"] + k["i_p"]
    said("而 1 元工资带来 0.80 元消费，1 元当年利润只带来$0.02+0.23=0.25$元支出", 1, k["c_w"], 1, k["c_p"], k["i_p"], spend_p)
    sc = {**k, "w_x": SC_WX}
    share = k["c_w"] * SC_WX + spend_p * (1 - SC_WX)
    imp = klein_closed(sc)["impact"]
    said("消费与投资增加$0.80\\times0.30+0.25\\times0.70=0.415$倍的$\\Delta X$，冲击乘数是$1/0.585\\approx1.71$，比 1.93 小",
         k["c_w"], SC_WX, spend_p, 1 - SC_WX, share, 1, 1 - share, imp, klein_closed()["impact"])
    chk("    1/(1 - 0.415) = the impact multiplier of the closed form", 1 / (1 - share), imp, tol=1e-12)
    chk("    and the first year of the path", klein_path(1, coef=sc)["X"].iloc[0], imp, tol=1e-12)
    say("本来会失业的人更喜欢 B 点，收入以货币固定的人更喜欢 A 点")


def ending(F, Y, Q):
    y58, y60, y62 = F["ph_source"][2], F["ss_issue"][3], F["erp_title"][0]
    said("回到 1958 年", y58)
    say("两年以后，这条曲线成了菜单；再过两年，失业 4\\% 成了美国的临时目标")
    said("再过两年，失业 4\\% 成了美国的临时目标", F["erp_target"][0])
    assert y60 - y58 == 2 and y62 - y60 == 2
    say("克莱因的模型 I 里，三个行为方程有两个是消费与投资，乘数与周期都从它们来")
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 39's question"
    assert t.index("\\end{answers}") < t.index("回到 1958 年")
    assert f"\\guidequestion{{{NEXT}}}" in (ROOT / "zh" / "ch39_consumption.tex").read_text(encoding="utf-8")


def models() -> None:
    """The key equations and Model I as printed, and the claims the text makes of them, checked with random numbers."""
    F = facts()
    a, b, c = curve_pars()
    t = TEX.read_text(encoding="utf-8")
    eqs = {lab: body.strip() for body, lab in re.findall(r"\\begin\{keyeq\}\n(.*?)\\label\{(eq:[^}]+)\}", t, re.DOTALL)}
    assert sorted(eqs) == ["eq:phillips-curve", "eq:phillips-okun", "eq:phillips-prices"], sorted(eqs)
    assert eqs["eq:phillips-curve"] == f"y+{a:.3f}={b:.3f}\\,x^{{{c:.3f}}}.", eqs
    assert eqs["eq:phillips-prices"] == "\\pi\\approx y-g.", eqs
    one, k, u0 = F["ok_rule"]
    assert eqs["eq:phillips-okun"] == f"P=A\\,[{one:g}+{k:.3f}\\,(U-{u0:g})],", eqs
    has("ok_rule", "P = A [1 + .032 (U - 4)]")
    # Model I as printed: the estimates of eq. (3.1.23)-(3.1.25) and the identities (3.1.19)-(3.1.21)
    c0, cp, cp1, cw = F["kl_est_c"]
    i0, ip, ip1, ik = F["kl_est_i"]
    w0, wx, wx1, wt, t0 = F["kl_est_w"]
    body = ("\\begin{aligned}\n"
            f"C&={c0:.2f}+{cp:.2f}\\,\\Pi+{cp1:.2f}\\,\\Pi_{{-1}}+{cw:.2f}\\,(W_1+W_2),\\\\\n"
            f"I&={i0:.2f}+{ip:.2f}\\,\\Pi+{ip1:.2f}\\,\\Pi_{{-1}}-{-ik:.2f}\\,K_{{-1}},\\\\\n"
            f"W_1&={w0:.2f}+{wx:.2f}\\,X+{wx1:.2f}\\,X_{{-1}}+{wt:.2f}\\,(t-{t0:.0f}),\\\\\n"
            "X&\\equiv Y+T-W_2,\\qquad Y+T=C+I+G,\\qquad Y=\\Pi+W_1+W_2,\\qquad \\Delta K=I.\n"
            "\\end{aligned}")
    m = re.search(r"\\begin\{equation\}\n(.*?)\\label\{eq:phillips-klein\}\n\\end\{equation\}", t, re.DOTALL)
    assert m and m.group(1).strip() == body, m.group(1) if m else None
    has("kl_est_w", "0.42(Y + T - W2) + 0.16(Y + T - W2)-1")                    # X = Y + T - W2
    has("kl_identities", "Y + T = C + I + G", "Y = Π + W1 + W2", "ΔK = I")
    assert t.count("\\begin{equation}") == 1
    # X = Y + T - W2 and Y + T = C + I + G give X = C + I + G - W2 (the text's shorthand)
    say("$X$是本书为了简写记的，即$C+I+G-W_2$")
    # the closed forms of ex:phillips-klein against the simulation and the steady state, on random coefficients
    rng = np.random.default_rng(38)
    n = 0
    for _ in range(200):
        co = dict(c_p=rng.uniform(0, 0.3), c_p1=rng.uniform(0, 0.4), c_w=rng.uniform(0.5, 0.95), i_p=rng.uniform(0, 0.4),
                  i_p1=rng.uniform(0, 0.7), i_k=-rng.uniform(0.05, 0.4), w_x=rng.uniform(0.2, 0.7),
                  w_x1=rng.uniform(0, 0.25))
        cf = klein_closed(co)
        if not (0 < 1 - (co["c_p"] * (1 - co["w_x"]) + co["c_w"] * co["w_x"]) - co["i_p"] * (1 - co["w_x"])):
            continue
        chk("    random coefficients: impact", klein_path(1, coef=co)["X"].iloc[0], cf["impact"], tol=1e-9)
        # the steady state: Pi = Pi_-1, X = X_-1, I = 0; C = c_p Pi + c_p1 Pi + c_w W1; 0 = (i_p + i_p1) Pi + i_k K
        # unknowns C, W1, X, Pi, K: C = c..., W1 = w X, X = C + G (I = 0), Pi = X - W1, investment zero
        A = np.array([[1, -co["c_w"], 0, -(co["c_p"] + co["c_p1"]), 0],
                      [0, 1, -(co["w_x"] + co["w_x1"]), 0, 0],
                      [-1, 0, 1, 0, 0],
                      [0, 1, -1, 1, 0],
                      [0, 0, 0, co["i_p"] + co["i_p1"], co["i_k"]]], dtype=float)
        C_, W1_, X_, P_, K_ = np.linalg.solve(A, np.array([0, 0, DG, 0, 0], dtype=float))
        assert np.isclose(X_, cf["long"], rtol=1e-9) and np.isclose(K_, cf["capital"], rtol=1e-9)
        n += 1
    assert n > 100, n
    print(f"ok Model I: the closed forms against the simulation and the steady state on {n} random coefficient sets")
    # Phillips's curve: the inverse, falling, convex, and the average of a swing above the curve at the average
    for x in rng.uniform(0.5, 12, 50):
        assert np.isclose(curve_inverse(y_of(x)), x)
    for lo, hi in rng.uniform(0.5, 12, (50, 2)):
        if abs(hi - lo) > 1e-6:
            assert (y_of(lo) + y_of(hi)) / 2 > y_of((lo + hi) / 2)
    # Okun's rule: the gap at U is 3.2 (U - 4) per cent of actual output
    for U in rng.uniform(3, 7.5, 20):
        A_ = rng.uniform(100, 1000)
        assert np.isclose((A_ * (1 + k * (U - u0)) / A_ - 1) * 100, 100 * k * (U - u0))
    # the price rule: with a constant mark-up, prices grow at (1 + y)/(1 + g) - 1, close to y - g for small rates
    for y_, g_ in rng.uniform(0, 0.06, (20, 2)):
        assert abs(((1 + y_) / (1 + g_) - 1) - (y_ - g_)) < y_ * g_ + g_ * g_ + 1e-12
    print("ok Phillips's curve, Okun's rule and the price rule on random numbers")
    # Chapter 33's notation, Chapter 34's gap
    assert "\\label{eq:warfinance-gap}" in chapter("ch34_warfinance")


def figures_data() -> None:
    """What the figures assert of their data."""
    F = facts()
    M = menu()
    assert list(M.index) == list(range(1946, 1970))
    assert M.loc[:1947, "us_unemp_pct"].isna().all() and M.loc[1948:, "us_unemp_pct"].notna().all()
    assert M.loc[1961, "us_unemp_pct"] == F["e71_c24_1961"][1] and M.loc[1969, "us_unemp_pct"] == F["e71_c24_1969"][1]
    assert M.loc[1968, "us_cpi_1967_100"] == F["e71_c45_1968"][0] and M.loc[1969, "us_cpi_1967_100"] == F["e71_c45_1969"][0]
    assert M.loc[1967, "us_cpi_1967_100"] == 100.0 and M["ca_cpi_1971_100"].lt(100).all()       # the bases
    S = scatter_1861_1913()
    assert len(S) == 53 and S.notna().all().all()
    L = scatter_1948_1957()
    assert len(L) == 10 and L.notna().all().all()
    T = table1()
    assert (T["demand"] > 0).all()
    P = klein_path(30)
    assert len(P) == 30 and P["K"].idxmax() == 8


# ---------------------------------------------------------------------------------------------------
# 5. The book
# the life dates: words -> (row of the birth year, index), (row of the death year, index), row of the heading, heading
LIVES = {"A. W. H. Phillips，1914—1975": (("loc_phillips", 0), ("loc_phillips", 1), "loc_phillips", "Phillips, A. W. H."),
         "James Coyne，1910—2012": (("gnd_coyne_born", 0), ("gnd_coyne_died", 0), "gnd_coyne", "Coyne, James E."),
         "Paul Samuelson，1915—2009": (("loc_samuelson", 0), ("loc_samuelson", 1), "loc_samuelson", "Samuelson, Paul A."),
         "Robert Solow，1924—2023": (("gnd_solow_born", 0), ("gnd_solow_died", 0), "gnd_solow", "Solow, Robert M."),
         "Milton Friedman，1912—2006": (("loc_friedman", 0), ("loc_friedman", 1), "loc_friedman", "Friedman, Milton"),
         "John Maynard Keynes，1883—1946": (("loc_keynes", 0), ("loc_keynes", 1), "loc_keynes", "Keynes, John Maynard"),
         "David Hume，1711—1776": (("loc_hume", 0), ("loc_hume", 1), "loc_hume", "Hume, David"),
         "Lawrence Klein，1920—2013": (("loc_klein", 0), ("loc_klein", 1), "loc_klein", "Klein, Lawrence R."),
         "John F. Kennedy，1917—1963": (("loc_kennedy", 0), ("loc_kennedy", 1), "loc_kennedy", "Kennedy, John F."),
         "Jan Tinbergen，1903—1994": (("loc_tinbergen", 0), ("loc_tinbergen", 1), "loc_tinbergen", "Tinbergen, Jan"),
         "Arthur Goldberger，1930—2009": (("gnd_goldberger_born", 0), ("gnd_goldberger_died", 0), "gnd_goldberger",
                                         "Goldberger, Arthur Stanley"),
         "Irving Fisher，1867—1947": (("loc_fisher", 0), ("loc_fisher", 1), "loc_fisher", "Fisher, Irving")}
# where two authorities have a year, they agree: (row, index) pairs
AGREE = [(("gnd_phillips_born", 0), ("loc_phillips", 0)), (("gnd_phillips_died", 0), ("loc_phillips", 1)),
         (("smg_engineer", 0), ("loc_phillips", 0)), (("smg_engineer", 1), ("loc_phillips", 1)),
         (("smg_life", 0), ("loc_phillips", 0)), (("smg_life", 1), ("loc_phillips", 1)),
         (("gnd_samuelson_born", 0), ("loc_samuelson", 0)), (("gnd_samuelson_died", 0), ("loc_samuelson", 1)),
         (("gnd_klein_born", 0), ("loc_klein", 0)), (("gnd_klein_died", 0), ("loc_klein", 1)),
         (("nbf_born", 1), ("gnd_klein_born", 0)), (("nbf_born", 0), ("gnd_klein_born", 2)),
         (("nbf_born", 3), ("gnd_klein_died", 0)), (("nbf_born", 2), ("gnd_klein_died", 2)),
         (("nbb_died", 0), ("gnd_klein_died", 2)), (("nbb_died", 1), ("gnd_klein_died", 0)),
         (("loc_goldberger", 0), ("gnd_goldberger_born", 0)), (("bnf_okun", 0), ("gnd_okun_born", 0))]
# what other chapters tell: (words of this chapter, chapter where it is told, words there)
EVENTS = [("上一章的模型假定物价不动", "ch37_mundell", "本章的模型假定物价不动"),
          ("加拿大 1956—1961 年的失业率翻了一番还多", "ch37_mundell", "1956—1961 年失业率翻了一番还多"),
          ("政府与他为此闹翻（\\chref{ch:mundell}）", "ch37_mundell", "科因为紧的货币与政府闹翻"),
          ("失业与通胀之间要不要取舍、取舍的代价多大，那个模型不回答", "ch37_mundell",
           "可失业与通胀之间要不要取舍，取舍的代价有多大，模型并不回答"),
          ("比 Powell 书里的 7.2\\% 低一点（\\chref{ch:mundell}）", "ch37_mundell", "升到 1961 年的 7.2\\%"),
          ("科因要的是管住通胀，政府要的是支持需求、减少闲置（\\chref{ch:mundell}）", "ch37_mundell",
           "政府想放松政策，支持需求，减少经济里的闲置"),
          ("\\chref{ch:islm}的 IS–LM 把货币工资当作给定（\\secref{sec:islm-legacy}）", "ch33_islm", "希克斯先把货币工资固定下来"),
          ("1936 年 9 月的牛津会议上", "ch33_islm", "1936 年 9 月的牛津"),
          ("介绍了他用约 12 个方程描述战后美国经济周期的尝试（\\chref{ch:islm}）", "ch33_islm",
           "介绍了他用约 12 个方程描述战后美国经济周期的尝试"),
          ("在物价追上来以前，增加的货币刺激了产业（\\secref{sec:bullion-hume}）", "ch19_bullion",
           "因为在物价追上来以前，增加的货币刺激了产业"),
          ("凯恩斯 1940 年用计划的支出与产能之差判断通胀的压力（式~\\eqref{eq:warfinance-gap}）", "ch34_warfinance",
           "在产能处，计划的支出减去产能，就是\\textbf{通胀缺口}"),
          ("为了按战前平价恢复金本位，英国决定压住需求、压低物价（\\chref{ch:interwar}）", "ch27_interwar",
           "英国 1925 年按战前平价回到黄金"),
          ("2021—2023 年的通胀又让人重新讨论它（\\chref{ch:inflation21}）", "ch74_inflation21",
           "\\chapter{2021—2023 年通胀}")]
# the chapters this one hands on to
LATER = {"ch:naturalrate": "ch44_naturalrate", "ch:monetarism": "ch45_monetarism", "ch:oil": "ch47_oil",
         "ch:ratex": "ch48_ratex", "ch:newkeynesian": "ch54_newkeynesian", "ch:inflation21": "ch74_inflation21",
         "ch:interwar": "ch27_interwar", "ch:warfinance": "ch34_warfinance", "ch:mundell": "ch37_mundell",
         "ch:islm": "ch33_islm"}
# the chapters that point here
POINTERS = ("ch19_bullion", "ch32_generaltheory", "ch33_islm", "ch34_warfinance", "ch44_naturalrate", "ch48_ratex")


def book(F, Q):
    """Life dates and what other chapters tell."""
    t = tex_text()
    for words, ((rb, ib), (rd, id_), head_row, head) in LIVES.items():
        assert words in t, words
        assert f"{F[rb][ib]:.0f}—{F[rd][id_]:.0f}" in words, (words, rb, rd)
        assert Q[head_row].startswith(head), (head_row, Q[head_row])             # the person of the record
        COVERED.append(words)
    for (r1, i1), (r2, i2) in AGREE:
        assert F[r1][i1] == F[r2][i2], (r1, r2)
    assert "dateOfBirth" in column("juan")["gnd_solow_born"] and "dateOfDeath" in column("juan")["gnd_coyne_died"]
    assert "奥肯（Arthur Okun，生卒年未详）" in t
    assert "Okun" in Q["gnd_okun"] and "Okun" in Q["bnf_okun"] and "gnd_okun_died" not in Q
    has("smg_life", "Bill Phillips 1914 - 1975", "Nationality: New Zealander")
    for here, ch, there_ in EVENTS:
        assert here in t, here
        assert there_ in chapter(ch), (ch, there_)
    for label, ch in LATER.items():
        assert f"{{{label}}}" in t, label
        assert f"\\label{{{label}}}" in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (label, ch)
    for ch in POINTERS:
        assert re.search(r"\\(?:chref|ref)\{ch:phillips\}", chapter(ch)), ch
    for lab, ch in (("sec:islm-legacy", "ch33_islm"), ("sec:bullion-hume", "ch19_bullion"),
                    ("eq:warfinance-gap", "ch34_warfinance")):
        assert f"{{{lab}}}" in t and f"\\label{{{lab}}}" in chapter(ch), lab
    print(f"ok {len(LIVES)} life dates, {len(EVENTS)} statements of other chapters, {len(LATER)} other chapters named")


# the bibliography item of each source of the snapshot (the authority records: loc38 and gnd38)
ITEM_OF = {"phillips1958img": "phillips1958", "erp1962img": "erp1962", "nobel1976lec": "friedman1976",
           "fisher1926ilr": "fisher1926", "ilorights38": "fisher1926", "cowles_okun38": "okun1962",
           "cowles_cfm11": "klein1950", "nobel1980pr": "nobel1980", "nobel1980facts": "nobel1980",
           "smg_moniac38": "smg38", "smg_phillips38": "smg38", "hsc_d491": "hsc38", "hsc_k8": "hsc38",
           "hsc_sectiond38": "hsc38", "hsc_sectionk38": "hsc38", "statcanlicence38": "hsc38",
           "archive_kg38": "archivekg38", "bnf_okun38": "gnd38"}
ADAPTED = ("Adapted from Statistics Canada, Historical Statistics of Canada, 11-516-X, Section D and Section K, Series "
           "D491-497 and K8-18, 1983. This does not constitute an endorsement by Statistics Canada of this product.")


def witnesses(F, Q):
    """Second witnesses of statements of the text, the licences and the bibliography block of the chapter."""
    # the unemployment rate of 1961: the Report of 1962 and Table C-24 of 1971; the labour force twice in 1962
    assert F["erp_magnified"][1] == F["e71_c24_1961"][1] and F["erp_labor"] == [F["erp_jobs"][2], F["erp_jobs"][3]]
    # Phillips's years: the Science Museum Group and the LoC; the curve on two pages (the text layer and the image)
    has("ph_curve_text", "log (y + 0 900) = 0.984")
    assert "9*638" in Q["ph_curve_text"] and F["ph_1925curve"][3] == round(y_of(F["ph_1925curve"][2]), 2)
    # Samuelson and Solow's two points against their own text: 5 to 6 and 4 to 5 per cent
    assert F["ss_point1"][1] <= F["ss_pointA"][0] <= F["ss_point1"][2]
    # the licences
    m = meta()
    lic = m["license"]
    for rid in ("cw_copyright", "nl_copyright", "nb_copyright", "nbb_copyright", "nbb_copyright05", "il_copyright",
                "il_prior", "il_request", "smg_rights", "sl_a", "sl_b", "gnd_licence"):
        assert re.search(r"(?:\(|; )rows? [^)]*\b" + rid + r"\b", lic), rid
        assert words_of(rid) in lic, rid
    for words in ("Short phrases only", "public domain", "public data", "the copies are not committed", ADAPTED,
                  "read on 2026-10-29 at https://www.ilo.org/rights-and-permissions", "have no terms of use"):
        assert words in lic, words
    assert "Creative Commons Attribution 4.0" in Q["smg_rights"] and "Value-added Product" in Q["sl_b"]
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    start = bib.index("% ---- 第 38 章")
    following = re.search(r"^% ---- 第 \d+ 章", bib[start + 1:], re.MULTILINE)
    end = start + 1 + following.start() if following else bib.index("\\end{thebibliography}")
    block = bib[start:end]
    assert "data/fetch/phillips38.py" in block and bib.index("% ---- 第 37 章") < start
    items = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", block)}
    allitems = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", bib)}
    assert ADAPTED in items["hsc38"] and "Statistics Canada Open Licence" in items["hsc38"]
    for key in ("erp1962", "erp1971"):
        assert "公有领域" in items[key], key
    for key, rid in (("friedman1976", "nl_copyright"), ("nobel1980", "nb_copyright"), ("nobel1980bio", "nbb_copyright"),
                     ("nobel1980bio", "nbb_copyright05"), ("okun1962", "cw_copyright"), ("klein1950", "cw_copyright"),
                     ("fisher1926", "il_copyright"), ("smg38", "smg_rights"), ("gnd38", "gnd_licence")):
        assert words_of(rid) in items[key], (key, rid)
    assert "公共数据" in items["loc38"]
    for key in ("phillips1958", "samuelson1960"):
        assert "JSTOR" in items[key] and "不随本书分发" in items[key], key
    for words, ((rb, _), _, head_row, _) in LIVES.items():
        if head_row.startswith("loc_"):
            assert Q[head_row].replace("-", "--") in items["loc38"], head_row
    for rid in ("loc_solow", "loc_okun", "loc_goldberger"):
        assert Q[rid].replace("-", "--") in items["loc38"], rid
    # every source of the snapshot is named by its URL in its item
    for key, s in m["sources"].items():
        item = "loc38" if key.startswith("loc_") else "gnd38" if key.startswith("gnd_") else ITEM_OF.get(key, key)
        assert s["url"] in allitems[item].replace("\\%", "%").replace("\\_", "_").replace("\\#", "#"), key
    # the Bank of England's workbook, cited by Chapter 19's item
    bm = load_snapshot("boe_millennium_uk_1860_1958")[1]
    assert bm["url"] in allitems["boe2017"]
    keys = set(allitems)
    cited = {k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", tex_text()) for k in c.split(",")}
    assert cited <= keys, sorted(cited - keys)
    assert REUSED_KEYS <= cited and not REUSED_KEYS & set(items)
    assert set(items) == cited - REUSED_KEYS, sorted(set(items) ^ (cited - REUSED_KEYS))
    print(f"ok {len(cited)} works cited, {len(items)} in the bibliography block of Chapter 38, "
          f"{len(REUSED_KEYS)} in earlier blocks")


NAMES = "Feinstein|Phelps Brown|Hopkins|Bowley|Wood|Rees|Powell|Lipsey|Forder|Haavelmo|Adelman"


def counts() -> None:
    """The editor's limits: “不能” at most about a dozen; no cited modern author in Latin script as the subject of a
    sentence outside the 史料说明; the forbidden words; who pays stated; the two debates left open."""
    t = tex_text()
    main = re.sub(r"\\begin\{deeper\}\[史料说明\].*?\\end\{deeper\}", "", t, flags=re.DOTALL)
    n = t.count("不能")
    print(f"ok “不能” {n} times")
    assert n <= 12, n
    verbs = "认为|写道|说|指出|记述|估计|承认|报道|记载|提到|列出|给出|发现|统计|算出|早有|看法|有类似|怀疑|强调|写作"
    subj = re.findall(r"(?:^|[。；：，\n])\s*(?:" + NAMES + r")(?:\s*[、与和]\s*(?:" + NAMES + r"))*(?: 等人)?(?:（\d{4}）)?\s*"
                      r"(?:" + verbs + ")", main)
    assert not subj, subj
    for words in ("本书没有找到", "没能取得", "没有取得", "没有读到"):
        assert words not in main, words                                          # only in the 史料说明
    narrative = re.sub(r"“[^”]*”", "", t)                                       # the quotations render the sources
    for bad in ("这一节回答", "不是因为", "而是", "详见", "\\textsc", "\\underline", "\\clearpage"):
        assert bad not in narrative, bad
    assert not re.search(r"(?<![意看])见\\(?:chref|secref|figref|tabref|exref|eqref)", t)
    assert "\\chapterstub" not in t
    # who pays: the unemployed, or those whose incomes are fixed in money, in the sources' words where they exist
    for words in ("菜单上的每一个点，都在决定谁来付代价", "A 点的代价是失业，B 点的代价落在收入以货币固定的人身上", "“固定收入”",
                  "尤其是失业者", "选哪一点，就是选谁来付代价", "得到好处的是本来会失业的人，付出代价的是收入固定的人",
                  "“黑人及其他种族”是 12.4\\%"):
        assert words in main, words
    # the two debates of the editor's notes are left open
    for words in ("第一个争论", "第二个争论"):
        assert main.count(words) == 1, words
    first, second = main.split("\\subsubsection{")[1:3]
    second = second[:second.index("\\section{")]
    assert first.rstrip().endswith("至今没有定论。") and second.rstrip().endswith("至今没有定论。")
    # the inferences are marked
    assert main.count("本书的解读") >= 8 and "本书的计算" in main and "本书的概括" in main
    # sentences: a colon only before a quotation or a list, one semicolon at most
    for s in re.split(r"(?<=[。？！])|\n", re.sub(r"“[^”]*”", "“”", main)):
        assert s.count("；") <= 1, s


def main() -> None:
    df = _rows()
    F, Y, Q = facts(), years(), quotes()
    check_readings(df)
    check_text(df)
    guide(F, Y, Q)
    opening(F, Y, Q)
    world(F, Y, Q)
    curve_section(F, Y, Q)
    read_example(F, Y, Q)
    prices(F, Y, Q)
    menu_section(F, Y, Q)
    case(F, Y, Q)
    gap(F, Y, Q)
    models_section(F, Y, Q)
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
