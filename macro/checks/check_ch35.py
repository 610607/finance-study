"""Chapter 35 (战后重建：马歇尔计划、德国货币改革与道奇路线): every number and every quotation in
zh/ch35_reconstruction.tex.

    python3 checks/check_ch35.py

The snapshot data/snapshots/reconstruction_facts.csv holds the quotations of the chapter's sources, each with its
page (the rows read on a page image carry no quotation and transcribe the words in their note); the quotations are
checked against the documents by data/fetch/verify_web_quotes.py, and data/fetch/reconstruction35.py fetches the
documents. This script

1. reads the numbers of every row from its quotation (or transcription) by the rules of READINGS and compares them
   with the value column; the tables read on page images (Ritschl's Tab. I, p. 57 of the Monatsberichte) are read
   again from their transcriptions;
2. finds every “…” of the text among the renderings of TRANSLATIONS, and the words of the source each one renders
   (KEYWORDS) in the row;
3. checks each number of the text with said(): the phrase is in the text and each number is the value of a row, a
   teaching input, or arithmetic on them (the conversion of a household by the rules of the laws, the overhang of
   eq:reconstruction-overhang, the yen example); every Arabic number of the text must lie in a phrase said() read
   (coverage());
4. checks the key equation with random numbers, the data of the figures (figsrc/fig_ch35.py imports ipb(), ipf(),
   unemployment(), employment(), wpi() and marshall_aid()), the life dates against the authority records, what other
   chapters tell, the licences and the bibliography block of Chapter 35, and the editor's limits;
5. lists the rows no "% 据:" anchor of the text names (common.anchors).

Set CH35_TEX to a scratch copy of the chapter to run the checks on it (mutation tests).
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

TEX = Path(os.environ.get("CH35_TEX", ROOT / "zh" / "ch35_reconstruction.tex"))   # a scratch copy for mutation tests
GUIDE = "被压抑的通胀怎样一夜消失？"
PREV = GUIDE                                        # Chapter 34's NEXT
NEXT = "美元为什么既是体系的支柱，又是它的隐患？"     # Chapter 36's question
MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"], 1)}
MONATE = {m: i for i, m in enumerate(["januar", "februar", "märz", "april", "mai", "juni", "juli", "august",
                                      "september", "oktober", "november", "dezember"], 1)}
# the sources written in German: their numbers have a decimal comma and a thousands point (9,50; 1.450)
GERMAN = {"buchheim1988", "ritschl1985", "ritschl1985img", "abelshauser1981", "waehrungsgesetz1948",
          "umstellungsgesetz1948", "festkontogesetz1948", "bdlgesetz1948", "bdl1950", "bbkterms35"}


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
    df, m = load_snapshot("reconstruction_facts", dtype=str, keep_default_na=False)
    assert 35 in m["used_in"] and m["fetch"] == "data/fetch/reconstruction35.py"
    assert df["id"].is_unique
    return df


@lru_cache(maxsize=None)
def meta() -> dict:
    return load_snapshot("reconstruction_facts")[1]


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
    """The month `name` (English or German), asserted to be in what row rid says."""
    has(rid, name)
    return MONTHS.get(name.lower()) or MONATE[name.lower()]


def page(rid: str) -> int:
    """The first page number of a row's juan column: 'p. 15 (PDF p. 24)' -> 15."""
    return int(re.search(r"pp?\. (\d+)", column("juan")[rid]).group(1))


def url_date(key: str) -> tuple[int, int, int]:
    """The date in a Historic Hansard URL: .../commons/1959/apr/15/... -> (1959, 4, 15)."""
    y, m, d = re.search(r"/(\d{4})/([a-z]{3})/(\d\d)/", meta()["sources"][key]["url"]).groups()
    return int(y), next(i for k, i in MONTHS.items() if k.startswith(m)), int(d)


# ---------------------------------------------------------------------------------------------------
# 1. Readings of the numbers (the same rules as the script that wrote the snapshot)
SMALL = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "eleven": 11, "twelve": 12, "fourteen": 14, "fifteen": 15, "seventeen": 17}
TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
MULT = {"thousand": 10 ** 3, "million": 10 ** 6, "billion": 10 ** 9}
WORDS = {"half": 0.5, "one-half": 0.5, "a third": 1 / 3, "two-thirds": 2 / 3, "three or four": 3.5,
         "drei": 3, "zwei": 2, "ein Zehntel": 0.1, "Dreifache": 3, "die Hälfte": 0.5, "Zehntel": 0.1,
         "три": 3, "один": 1, "два": 2, "десять": 10, "zwanzig": 20, "Drei": 3, "2 Drittel": 2 / 3,
         "hundert": 100, "sechzig": 60, "vierzig": 40, "zehn": 10, "eine": 1, "jede": 1, "Sieben": 7, "Zwei": 2,
         "nfhundertvierzig": 540, "a fifth": 0.2, "two and a half": 2.5, "sixth": 6, "achtzehnte": 18}                         # '(fü)nfhundertvierzig' of a page read without its umlauts


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


def german(s: str) -> float:
    """'9,50', '1.450', '4,4'."""
    return float(s.replace(".", "").replace(",", "."))


ZH_DIGITS = {"〇": 0, "零": 0, "一": 1, "两": 2, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
ZH_UNITS = {"十": 10, "百": 100, "千": 1000, "万": 10 ** 4, "萬": 10 ** 4, "亿": 10 ** 8, "億": 10 ** 8}


def zh(s: str) -> float:
    """A Chinese numeral: '六', '十', '二十億', '三分之一', '五分之二', '一半', '七成'."""
    if "分之" in s:
        b, a = s.split("分之")
        return zh(a) / zh(b)
    if s.endswith("半"):                                                       # '一半': one half
        return 0.5 * (zh(s[:-1]) if s[:-1] else 1)
    if s.endswith("成"):                                                       # '七成': seven tenths
        return zh(s[:-1]) / 10
    big, total, part = 0, 0, 0
    for ch in s:
        if ch in ZH_DIGITS:
            part = ZH_DIGITS[ch]
        elif ch in "万萬亿億":                                                 # 万, 亿 multiply all before them
            big += max(total + part, 1) * ZH_UNITS[ch]
            total, part = 0, 0
        else:
            total += max(part, 1) * ZH_UNITS[ch]
            part = 0
    return float(big + total + part)


def ja(s: str) -> float:
    """Arabic figures with 億 and 万: '1億9136万' -> 191360000."""
    return sum(float(n.replace(",", "")) * {"億": 10 ** 8, "万": 10 ** 4, "": 1}[u]
               for n, u in re.findall(r"([\d,.]+)(億|万|)", s))


FIGURES = re.compile(r"\d[\d,]*(?:\.\d+)?|\.\d+")
FIGURES_DE = re.compile(r"\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?")
EN, NUM, DE, WD, ZH, JA = "en", "num", "de", "word", "zh", "ja"
# id -> [(phrase, how)], in order. A phrase 'context|word' is searched as a whole and read from `word`. Rows not
# listed are read with all the figures of the quotation (or of the transcription of a page image), in the German
# manner for the sources in GERMAN.
READINGS: dict[str, list[tuple[str, str]]] = {
    "ab_99": [("knapp |99", DE), ("nur |22", DE), ("über |2 Drittel", WD)],
    "wg_unit": [("hundert", WD)],
    "wg_s6": [("sechzig", WD)],
    "wg_s6b": [("vierzig", WD), ("zwei", WD)],
    "wg_s17": [("sechzig", WD)],
    "ug_family": [("21", DE), ("1948", DE), ("achtzehnte", WD)],
    "ug_s2": [("zehn", WD), ("eine", WD)],
    "ug_s4": [("nfhundertvierzig", WD)],
    "ug_s11": [("drei", WD)],
    "ug_s14": [],
    "ug_s16": [("zehn", WD), ("eine", WD)],
    "ug_s18": [("jede", WD), ("eine", WD)],
    "fk_s1a": [("Sieben", WD), ("zehn", WD)],
    "fk_s1b": [("Zwei", WD), ("zehn", WD)],
    "wg_number": [("61", DE)],
    "ug_number": [("63", DE)],
    "fk_number": [("65", DE)],
    "bdl_date": [("1948", DE), ("1", DE)],
    "de_share": [("three", EN), ("1948", NUM), ("1951", NUM), ("a fifth", WD)],
    "de_two": [("1951", NUM), ("two", EN)],
    "de_gap": [("seven", EN), ("eight", EN)],
    "de_hpm": [("eight", EN)],
    "de_aid25": [("two and a half", WD)],
    "de_four_years": [("four", EN), ("sixth", WD), ("eight", EN)],
    "f6_rate": [("three", EN)],
    "fc_col": [("at |810", NUM), ("August |19", NUM)],
    "mof_wagerules": [],                                                      # '- 30 -' is the page number
    "bj_notes": [("（|1946", NUM), ("3月|12", NUM), ("には|152", NUM), ("9月|16", NUM), ("には|618", NUM),
                 ("2月|16", NUM), ("の|615", NUM), ("10月末には|706", NUM), ("12月末には|934", NUM)],
    "bj_endmarch": [("銀行券発行高 |23,322", NUM)],
    "bj_surplus": [("昭和|24", NUM), ("において|3", NUM), ("においても|1567", NUM)],
    "bj_tokuju": [("、|26", NUM), ("年|1", NUM), ("月|7", NUM), ("累計|1億9136万", JA), ("支払い高|7593万", JA)],
    "bj_ipindex": [("6月 |93.6", NUM), ("12月 |116.7", NUM)],
    "bj_retail": [("6月 − |7.9", NUM)],
    "bj_wpi": [("+|23.5", NUM)],
    "h59_unease": [("fourteen", EN), ("half", WD)],
    "h59_two": [("two", EN)],
    "zv_title": [("Понедельник |15", NUM), ("декабря |1947", NUM), ("№ |247", NUM)],
    "zv_cash": [("десять", WD), ("один", WD)],
    "zv_dep_a": [("до |3.000", DE)],
    "zv_dep_b": [("до |10.000", DE), ("первые |3.000", DE), ("три", WD), ("два", WD)],
    "zv_dep_c": [("свыше |10.000", DE), ("первые |10.000", DE), ("два", WD), ("один", WD)],
    "zv_bonds": [("из |2", NUM), ("в |1948", NUM), ("три", WD), ("один", WD)],
    "ww_reserve": [("合|二億", ZH), ("資產値|三億", ZH), ("兩共|五億", ZH), ("美元|四", ZH), ("對|一", ZH),
                   ("金圓券|二十億", ZH)],
    "ww_limit": [("為|二十億", ZH)],
    "ww_budget": [("減至|九億", ZH), ("金圓|三十六億", ZH)],
    "ww_income": [("金圓|二十四億六千萬", ZH)],
    "ww_gap": [("為|十一億四千萬", ZH), ("|百分之三十", ZH)],
}
IMAGE_NOTE = "read on the page image"


def read(word: str, how: str) -> list[float]:
    if how == NUM:
        return [figure(word)]
    if how == DE:
        return [german(word)]
    if how == EN:
        return [cardinal(word)]
    if how == WD:
        return [WORDS[word]]
    if how == ZH:
        return [zh(word)]
    if how == JA:
        return [ja(word)]
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


def read_row(rid: str, text: str, key: str) -> list[float]:
    """The numbers of a row's words, by READINGS or by its figures."""
    if rid in READINGS:
        return read_rule(rid, text)
    if key in GERMAN:
        return [german(x) for x in FIGURES_DE.findall(text)]
    return [figure(x.rstrip(",")) for x in FIGURES.findall(text)]


# the rows whose numbers the snapshot does not read (each with the reason)
UNREAD = {"mof_table_head": "the number of the table, 1-9", "mof_terms": "the version 1.0 of the licence",
          "gnd_licence": "the version 1.0 in the licence's URL",
          "h72w_speaker": "the financial years 1941-42 to 1945-46 of the credits, not used"}
# the tables read on page images: their value column is re-read here from the transcription
TABLES = ("ri_ipb", "ri_ipf", "bdl_unemp", "bdl_emp")
# the misreadings of the text layers, each printed in the quotation and named in the note of its row (or in NOTES)
# (row, the misreading as printed in the quotation, the words of the snapshot's notes that name it)
MISPRINTS = [("bdl_stall", "~st", "'~st' for 'ist'"), ("bdl_kfw", "V er kehr", "'V er kehr'"),
             ("mof_rfbbuy", "JuneAugust", "runs 'June' and 'August' together"),
             ("mof_wagerules", "- 30 -", "the page number '- 30 -'")]


def ri_table(rid: str) -> dict[str, float]:
    """Ritschl's Tab. I as transcribed: 'IPB, J F M A M J J A S O N D: 1946: 27 28 ... | 1947: ...' -> {'1946-01': 27,
    ...}."""
    head, body = transcription(rid).split(": ", 1)
    assert head.endswith("J F M A M J J A S O N D"), rid
    out = {}
    for seg in body.split(" | "):
        y, nums = seg.split(": ")
        vals = [float(x) for x in nums.split()]
        assert len(vals) <= 12, (rid, y)
        out.update({f"{y}-{m:02d}": v for m, v in enumerate(vals, 1)})
    return out


def bdl_table(rid: str) -> dict[str, float]:
    """The labour-market table of the Monatsberichte (p. 57) as transcribed: thousands, the decimal comma and a space
    between the thousands ('1 068,9'); the months from the head of the column."""
    head, body = transcription(rid).split(": ", 1)
    vals = [german(x.replace(" ", "")) for x in re.findall(r"\d{1,3}(?: \d{3})*,\d+", body.split(" |")[0])]
    span = re.search(r"(\d{4}) \d+\. (\w+) bis (\d{4}) \d+\. (\w+)", head)
    if span:                                                                # monthly: the first and the last month
        y0, m0, y1, m1 = int(span[1]), MONATE[span[2].lower()], int(span[3]), MONATE[span[4].lower()]
        months = [f"{y}-{m:02d}" for y in range(y0, y1 + 1) for m in range(1, 13)
                  if (y, m) >= (y0, m0) and (y, m) <= (y1, m1)]
    else:                                                                   # quarter ends, year by year
        months = [f"{seg[:4]}-{MONATE[name.lower()]:02d}" for seg in head.split(" | ")[1].split("; ")
                  for name in re.findall(r"\d+\. (\w+)", seg)]
    assert len(months) == len(vals), (rid, len(months), len(vals))
    return dict(zip(months, vals))


def table(rid: str) -> dict[str, float]:
    return ri_table(rid) if rid.startswith("ri_") else bdl_table(rid)


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
        if r.id in UNREAD:
            assert not vals and r.id not in READINGS and FIGURES.search(text), r.id
            continue
        got = list(table(r.id).values()) if r.id in TABLES else read_row(r.id, text, r.file)
        assert [round(g, 6) for g in got] == [round(v, 6) for v in vals], f"{r.id}: read {got}, value column {vals}"
        n += bool(vals)
    quoted("rows with values, each read from its quotation or transcription", n, 227)
    quoted("rows read on a page image (no quotation)", img, 41)
    N, Q = column("note"), quotes()
    notes = meta()["notes"]
    for rid, word, named in MISPRINTS:
        assert word in Q[rid], (rid, word)                                      # printed in the quotation
        k = notes.find(named)
        assert k >= 0 and notes.find(f"({rid})", k) - k < 120, (rid, named)    # and named, with its row
    assert "w II" not in Q["h59_newages"] and "ages w II become" in N["h59_newages"] and "'w II' for 'will' (h59_newages)" in notes


# ---------------------------------------------------------------------------------------------------
# Data of the figures (figsrc/fig_ch35.py imports them)
def series(rid: str) -> pd.Series:
    s = pd.Series(table(rid))
    assert list(s.index) == sorted(s.index)
    return s


def ipb() -> pd.Series:
    """Ritschl's Tab. I, IPB: the official index of industrial production of the Bizone (1936 = 100), monthly,
    January 1946 to July 1949."""
    s = series("ri_ipb")
    assert s.index[0] == "1946-01" and s.index[-1] == "1949-07" and len(s) == 43
    assert facts()["ri_ipb_span"] == [1946, 1949] and "bis Mitte 1949" in quotes()["ri_ipb_span"]
    return s


def ipf() -> pd.Series:
    """Tab. I, IPF: the French zone, January 1947 to August 1949 (1947: Manz's deflated value series)."""
    s = series("ri_ipf")
    assert s.index[0] == "1947-01" and s.index[-1] == "1949-08" and len(s) == 32
    return s


def unemployment() -> pd.Series:
    """The unemployed of the Bundesgebiet at the end of each month, thousands, March 1948 to February 1950."""
    s = series("bdl_unemp")
    assert s.index[0] == "1948-03" and s.index[-1] == "1950-02" and len(s) == 24
    return s


def employment() -> pd.Series:
    """The employed at the end of each quarter, thousands, June 1948 to December 1949."""
    s = series("bdl_emp")
    assert list(s.index) == ["1948-06", "1948-09", "1948-12", "1949-03", "1949-06", "1949-09", "1949-12"]
    return s


@lru_cache(maxsize=None)
def wpi() -> pd.Series:
    """The Bank of Japan's prewar-base wholesale price index (1934-36 average = 1), monthly, 1944-1952."""
    df, m = load_snapshot("boj_prewar_wpi_1944_1952", dtype={"month": str})
    assert 35 in m["used_in"] and m["fetch"] == "data/fetch/boj_wpi35.py"
    assert "1934-36 average = 1" in m["title"] and "Bank of Japan" in m["license"]
    assert list(df.month) == [f"{y}-{k:02d}" for y in range(1944, 1953) for k in range(1, 13)]
    return df.set_index("month")["index"]


def marshall_aid() -> dict[str, float]:
    """De Long and Eichengreen, p. 14: aid 1948-1951, billion dollars; the rest is the total less the four."""
    y0, y1, total, uk, fr, it, de = facts()["de_amounts"]
    assert (y0, y1) == (1948, 1951)
    has("de_amounts", "to the United Kingdom", "to France", "to Italy", "Western-occupied zones of Germany")
    return {"英国": uk, "法国": fr, "意大利": it, "西德": de, "其他": total - (uk + fr + it + de), "total": total}


def showa(year: float) -> int:
    """A year of the Showa era, by the Centennial History's own '昭和21年（1946年）'."""
    tr = transcription("bj_notes")
    m = re.search(r"昭和(\d+)年（(\d{4})年）", tr)
    return int(year) + int(m[2]) - int(m[1])


def sect(rid: str) -> int:
    """The section of a law named in a row's juan column: '§ 18 (1)' -> 18."""
    return int(re.search(r"§ (\d+)", column("juan")[rid]).group(1))


def src_year(key: str) -> int:
    """The year of publication in the version line of source `key`: '33 (1985)', '(November 1991)'."""
    return int(re.search(r"\((?:[A-Z][a-z]+ )?((?:19|20)\d\d)\)", meta()["sources"][key]["version"]).group(1))


def chapter(name: str) -> str:
    """Another chapter's text without its comment lines."""
    t = (ROOT / "zh" / f"{name}.tex").read_text(encoding="utf-8")
    return "\n".join(l for l in t.splitlines() if not l.lstrip().startswith("%"))


# ---------------------------------------------------------------------------------------------------
# The teaching models
OVERHANG = {"Y": 100, "Pbar": 1, "k": 0.3, "M": 90, "ratio": 3, "Y2": 120, "k_sc": 0.45}   # ex:reconstruction-overhang
HOUSEHOLD = {"persons": 4, "children": 2, "cash": 240, "deposit": 10000, "debt": 500, "wage": 300}
SINGLE = {"persons": 1, "cash": 360, "deposit": 3000}                                 # self-check 2
YEN = {"old": 420, "new": 360, "sales": 10_000, "importer": 330}                      # ex:reconstruction-yen


def overhang(M: float, k: float, Y: float, Pbar: float = 1.0, ratio: float = 1.0) -> dict[str, float]:
    """eq:reconstruction-overhang: the money people wish to hold at the controlled price, k Pbar Y; the overhang
    M - k Pbar Y; the price level once the controls go, P = M/(kY), after a conversion of the money at ratio : 1."""
    Mr = M / ratio
    return dict(desired=k * Pbar * Y, excess=M - k * Pbar * Y, M=Mr, P=Mr / (k * Y), rise=Mr / (k * Pbar * Y))


@lru_cache(maxsize=None)
def rules() -> dict[str, float]:
    """The rules of tab:reconstruction-conversion, from the words of the laws."""
    F = facts()
    has("ug_s2b", "die andere H")                                            # one half free, the other half frozen
    has("ug_s2c", "Festkonto")
    has("fk_s1c2", "Der Restbetrag")
    cancel, of = F["fk_s1a"]
    free, of2 = F["fk_s1b"]
    assert of == of2
    rm, dm = F["ug_s2"]
    return dict(head=F["wg_s6"][0], first=F["wg_s6b"][0], months=F["wg_s6b"][1], firm=F["wg_s17"][0],
                per=F["ug_s4"][0], rate=dm / rm, free_half=0.5, cancel=cancel / of, freed=free / of,
                invest=1 - cancel / of - free / of, debt=F["ug_s16"][1] / F["ug_s16"][0],
                wage=F["ug_s18"][1] / F["ug_s18"][0], equal=F["ug_s11"][0])


def convert(cash: float, deposit: float, persons: int) -> dict[str, float]:
    """A household's money through the reform: the notes up to the per capita amount (60 a person) 1 : 1, the rest of
    the notes deposited; from the deposits 540 RM a member deducted, the rest 10 : 1, half free and half frozen; of the
    frozen 7/10 cancelled, 2/10 freed and the rest for investment (Festkontogesetz)."""
    R = rules()
    kopf = min(cash, R["head"] * persons)
    dep = deposit + cash - kopf
    base = max(0.0, dep - R["per"] * persons)
    dm = base * R["rate"]
    free = frozen = dm * R["free_half"]
    out = dict(kopf=kopf, dep=dep, deducted=R["per"] * persons, base=base, dm=dm, free=free, frozen=frozen,
               cancel=frozen * R["cancel"], freed=frozen * R["freed"], invest=frozen * R["invest"])
    out["total"] = kopf + free + out["freed"] + out["invest"]
    out["share"] = out["total"] / (cash + deposit)
    return out


# ---------------------------------------------------------------------------------------------------
# 2. Every “…” of the text against the snapshot
# the chapter's Chinese renderings of the quotations: rendering -> row (or rows)
TRANSLATIONS = {
    # the opening
    "自 1948 年 6 月 21 日起，实行德国马克货币制度": "wg_s1",
    "放开价格优先于官方定价": "bu_annex",
    # sec:reconstruction-world
    "也许夸大了": "bu_exaggerated",
    "人们对本国货币的信心受到了严重的动摇": "ms_confidence",
    "把农产品卖了换回用不上的钱，在他看来是一笔不合算的买卖": "ms_farmer",
    "只是杯水车薪，失业更严重了": "mof_drop",
    "政府是赤字，企业是赤字，家庭也是赤字": "mof_red",
    # the compare box and sec:reconstruction-germany
    "对照试验": "bu_ropke",
    "不在于防止通胀的管制崩溃，而在于它们变得毫无意义": "bu_cdg_quote",
    "不能再改": "bu_conclave",
    "消除国家社会主义造成的货币崩坏的后果": "wg_purpose",
    # sec:reconstruction-cost
    "被剥夺的感觉": "bu_enteignung",
    "紧迫的、必须在 1948 年 12 月 31 日以前解决的任务": "wg_lastenausgleich",
    "分摊在许多年里、数额较小的付款": "bu_notoffset",
    "示威、骚乱与抵制的号召": "bu_protest",
    "市场经济还是计划经济": "bu_election",
    "失业在最近几个月大大增加": "bdl_stall",
    # sec:reconstruction-marshall
    "补救的办法在于打破恶性循环，恢复欧洲人民对本国以及整个欧洲经济前途的信心": "ms_remedy",
    "不针对任何国家或主义，针对的是饥饿、贫困、绝望与混乱": "ms_doctrine",
    "让世界的经济恢复运转，使自由制度得以存在的政治与社会条件能够出现": "ms_purpose",
    "主动权，我想，必须来自欧洲": "ms_initiative",
    "持续的组织": "eca_organization",
    "促进恢复或维持欧洲货币、预算与财政的健全": "eca_purpose",
    "稳定本国的货币，建立或维持有效的汇率，尽快平衡政府预算，总的来说恢复或维持人们对本国货币制度的信心": "eca_budget",
    "按相当的数额，把本国货币存进一个特别账户": ("eca_special", "eca_special2"),
    "机器与车辆": "de_machinery",
    "强大动力": "de_incentive",
    "很可能提早了财政稳定的日子": "de_advanced",
    "匿名地": "ab_britain",
    "已经有了一个可行的稳定方案": "de_inflation",
    # sec:reconstruction-japan
    "除了存入银行以外": "mof_void",
    "市场上的通胀倾向仍然是个问题": "mof_bias",
    "倾斜生产": "mof_priority",
    "主要靠日本银行承购的债券": "mof_bonds",
    "复金通胀": "mof_rfbinfl",
    "立即实行一项国内经济稳定的计划": "f6_program",
    "实现综合预算的真正平衡": "f6_budget",
    "加强现有的物价管制计划，必要时扩大它的范围": "f6_prices",
    "一个健全的日本经济稳定计划": "f6_lovett",
    "全力支持": "f6_lovett",
    "必须把塞子塞上的也是政府": "bj_stopper",
    "必须只限于以能够征收的税为财源的部分": "bj_taxes",
    "超平衡": "mof_overbalanced",
    "在经济领域几乎被赋予了全部的权力": "f9_authority",
    "完全扭转了": "f9_reversed",
    "必须警惕": "bj_ichimada",
    "作为缓解道奇计划通缩效果的一种办法": "mof_relief",
    "首先是工会的领袖与积极分子": "f9_soviet_quote",
    "但那肯定不是解雇的标准": "f9_criterion",
    "创造了大量新的工作岗位，大大刺激了国内生产": "mof_jobs",
    # sec:reconstruction-others
    "尽早": "h59_soon",
    "我想，我们谁也不能安心": "h59_unease",
    "通胀普遍": "h59_reason",
    "让全国都很高兴": "h72_repay",
    "要求发行大量的货币": "su_preamble",
    "不受改革的影响": "zv_wages",
    "何况这将是最后一次牺牲": "zv_sacrifice",
    "首先打击的，是积攒了大量的钱、把钱藏在储钱罐里的投机分子": "zv_speculators",
    "我们这里没有，也不会有失业": "zv_nounemp",
    "改革币制而不能平衡预算，纵可收效一时，断难维持永久": "ww_warning",
    "我们用政治的力量压制投机，用经济的力量引导游资": "fc_force",
    "我情愿做这样的强盗": "fc_robber",
    "虚构": "fc_fictions",
    # sec:reconstruction-debate
    "似乎无法直接驳倒": "ri_french_concede",
    "并不完全令人信服": "bu_abelshauser",
    "大规模而非常成功的结构调整计划": "de_structural",
    "至多是推了一把": "de_tipped",
    "大幅收紧了货币供给，产生了足以很快压住通胀、稳定经济的通缩效果": "mof_tightening",
    # the 史料说明
    "法律文献": "su_section",
    "几天以后": "bu_soviet",
    # the self-check and the ending
    "什么也没有得到": "bu_empty",
    "纵可收效一时，断难维持永久": "ww_warning",
    "远远超过它眼下的支付能力": "ms_ability",
}
# a “…” of the 史料说明 that names a source not obtained
NOT_OBTAINED = {"踩高跷": "道奇“踩高跷”的说法（1949 年 3 月），中央情报局的阅览室拒绝访问，没有取得"}
# the words of the source that each rendering translates
KEYWORDS = {
    "wg_s1": ["Mit Wirkung vom 21. Juni 1948 gilt die Deutsche-Mark-W"],
    "bu_annex": ["Der Freigabe der Preise ist vor der behördlichen Festsetzung der Vorzug zu geben."],
    "bu_exaggerated": ["Das mag übertrieben sein"],
    "ms_confidence": ["confidence in the local currency has been severely shaken"],
    "ms_farmer": ["So the sale of his farm produce for money which he cannot use seems to him an unprofitable "
                  "transaction."],
    "mof_drop": ["But this was only a drop in the ocean, and unemployment worsened."],
    "mof_red": ['"Government in the red, companies in the red, and households in the red, too."'],
    "bu_ropke": ["Art von Kontrollversuch"],
    "bu_cdg_quote": ["Die unmittelbare Gefahr in Deutschland besteht nicht darin, daß die Inflationskontrollen "
                     "zusammenbrechen, sondern daß sie bedeutungslos werden."],
    "bu_conclave": ["nicht mehr veränderbaren Grundzüge des Währungsplanes"],
    "wg_purpose": ["die Folgen der durch den Nationalsozialismus herbeigef"],
    "bu_enteignung": ["ein Gefühl der Enteignung"],
    "wg_lastenausgleich": ["als vordringliche, bis zum 31. Dezember 1948 zu"],
    "bu_notoffset": ["die über Jahre verteilten, relativ geringen Zahlungen zum Lastenausgleich"],
    "bu_protest": ["in Form von Demonstrationen, Tumulten und Boykottaufrufen"],
    "bu_election": ["Markt- oder Planwirtschaft"],
    "bdl_stall": ["die Arbeitslosigkeit in den letzten Monaten stark zugenommen hat"],
    "ms_remedy": ["The remedy lies in breaking the vicious circle and restoring the confidence of the European people "
                  "in the economic future of their own countries and of Europe as a whole."],
    "ms_doctrine": ["Our policy is directed not against any country or doctrine but against hunger, poverty, "
                    "desperation, and chaos."],
    "ms_purpose": ["the revival of a working economy in the world so as to permit the emergence of political and "
                   "social conditions in which free institutions can exist"],
    "ms_initiative": ["The initiative, I think, must come from Europe."],
    "eca_organization": ["a continuing organization"],
    "eca_purpose": ["furthering the restoration or maintenance of the soundness of European currencies, budgets, and "
                    "finances"],
    "eca_budget": ["bilize its currency, establish or maintain a valid rate of exchange, to balance its governmental "
                   "budget as soon as practicable, and generally to restore or maintain confidence in its monetary "
                   "system"],
    "eca_special": ["placing in a special account a deposit in the currency of"],
    "eca_special2": ["in commensurate amounts"],
    "de_machinery": ['"machinery and vehicles"'],
    "de_incentive": ["a powerful incentive"],
    "de_advanced": ["the Plan in all likelihood advanced the date of financial stabilization"],
    "ab_britain": ['„anonym"'],
    "de_inflation": ["they had achieved a workable stabilization program"],
    "mof_void": ["except for deposits"],
    "mof_bias": ["The inflationary bias in the market remained a problem"],
    "mof_priority": ['"priority production,"'],
    "mof_bonds": ["rely mostly on bonds underwritten by the BOJ"],
    "mof_rfbinfl": ["“Reconstruction Finance Bank inflation.”"],
    "f6_program": ["immediately to put into effect a program of domestic economic stabilization"],
    "f6_budget": ["Achieve a true balance in the consolidated budget"],
    "f6_prices": ["Strengthen and, if necessary, expand the coverage of existing price control programs."],
    "f6_lovett": ['"a sound program of economic stabilization in Japan."', '"full support"'],
    "bj_stopper": ["その「せん」を閉めねばならぬのもまた政府である"],
    "bj_taxes": ["政府の支出は徴収可能な税金を財源とするものだけに限定されなければならない"],
    "mof_overbalanced": ['"over balanced"'],
    "f9_authority": ["almost complete authority in the economic field"],
    "f9_reversed": ['"completely reversed this policy"'],
    "bj_ichimada": ["警戒を要する"],
    "mof_relief": ["as a means of providing relief from the deflationary effects of the Dodge Plan"],
    "f9_soviet_quote": ["first of all leaders and active members of trade unions"],
    "f9_criterion": ["but that certainly was not the criterion for discharge"],
    "mof_jobs": ["created large numbers of new jobs and proved a major stimulus for domestic production"],
    "h59_soon": ["so soon as may be after the termination of hostilities"],
    "h59_unease": ["none of us, I think, can feel at ease"],
    "h59_reason": ["the prevalence of inflation"],
    "h72_repay": ["delighted the country"],
    "su_preamble": ["потребовали выпуска в обращение большого количества денег"],
    "zv_wages": ["не затрагиваются реформой"],
    "zv_sacrifice": ["тем более, что это будет последняя жертва"],
    "zv_speculators": ["ударит прежде всего по спекулятивным элементам, накопившим крупные запасы денег и держащим их "
                       "в «кубышках»"],
    "zv_nounemp": ["У нас нет и не будет безработицы."],
    "ww_warning": ["改革幣制而不能平衡預算,縱可收效一時,斷難維持永久"],
    "fc_force": ["we have used political force to suppress speculation and utilized economic force to guide idle "
                 "funds"],
    "fc_robber": ["then I would be willing to be such a robber"],
    "fc_fictions": ["prices are fictions"],
    "ri_french_concede": ["Hier scheint die Unterschätzungsthese nicht direkt widerlegbar zu sein."],
    "bu_abelshauser": ["seine Argumentation, wie gezeigt, nicht voll"],
    "de_structural": ["a large and highly successful structural adjustment program"],
    "de_tipped": ["The Marshall Plan at most tipped the balance."],
    "mof_tightening": ["a sharp tightening of the money supply, which produced a sufficient deflationary effect to "
                       "overcome inflation quickly and stabilize the economy"],
    "su_section": ["Памятники права"],
    "bu_soviet": ["Einige wenige Tage später"],
    "bu_empty": ["ganz leer ausging"],
    "ms_ability": ["so much greater than her present ability to pay"],
}


def tex_text() -> str:
    return "\n".join(l for l in TEX.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("%"))


def text_quotations() -> list[str]:
    """The “…” of the text; the closing question is Chapter 36's and the chapter's own question is in the guide and at
    the end of the opening (both checked by guide() and ending())."""
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 36's question"
    t = t[:-len(NEXT)]
    assert t.count(GUIDE) == 2, "the question is not in the guide and at the end of the opening"
    return re.findall(r"“([^”]*)”", t.replace(GUIDE, ""))


def check_text(df: pd.DataFrame) -> None:
    ids = set(df["id"])
    used, n = set(), 0
    deeper = re.search(r"\\begin\{deeper\}\[史料说明\].*?\\end\{deeper\}", tex_text(), re.DOTALL).group(0)
    for q in text_quotations():
        n += 1
        used.add(q)
        if q in NOT_OBTAINED:
            assert NOT_OBTAINED[q] in deeper, q
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
    img = sorted(r for r in KEYWORDS if not quotes()[r])
    print(f"ok {n} quotations of the text found in the snapshot ({len(img)} rows by their transcriptions, "
          f"{len(NOT_OBTAINED)} not obtained, named in the 史料说明)")


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
    assert chapter("ch34_warfinance").rstrip().endswith(PREV)                 # 第 34 章交来的问题
    for label in ("ch:warfinance", "ch:weimar"):                               # the prerequisites
        assert f"\\chref{{{label}}}\\enspace\\nameref{{{label}}}" in t, label
    said("分析 1948 年德国货币改革与价格放开同时进行的效果", F["wg_s1"][1])
    said("描述 1949 年道奇路线与 1 美元兑 360 日元的固定汇率", F["mof_dodgeplan"][0], *F["bjc_360"])
    assert "\\chapterstub" not in t


def opening(F, Y, Q):
    d20, y48 = F["bu_sunday"]
    jun = mon("bu_sunday", "Juni")
    said("1948 年 6 月 20 日是星期日", y48, jun, d20)
    assert "Sonntag" in Q["bu_sunday"] and datetime.date(int(y48), jun, int(d20)).weekday() == 6
    assert "Befehlshaber der amerikanischen, der britischen und der franz" in Q["wg_governors"]
    say("法律由美、英、法三个占领区的军政长官颁布")
    d21, y = F["wg_s1"]
    said("第 1 条说，“自 1948 年 6 月 21 日起，实行德国马克货币制度”", sect("wg_s1"), y, mon("wg_s1", "Juni"), d21)
    assert d21 == d20 + 1
    said("一马克合 100 芬尼", F["wg_unit"][0])
    has("wg_unit", "Deutsche Pfennige")
    y24 = int(re.search(r"(\d{4}) 年 8 月 30 日，配合道威斯计划生效，德国以帝国马克为新的本位货币",
                        chapter("ch26_weimar")).group(1))
    said("被换掉的帝国马克，是 1924 年以来德国的货币单位", y24)
    said("每个居民可以用同样面额的旧钞换到至多 60 德国马克的现金", F["wg_s6"][0])
    has("wg_s6", "desselben Nennbetrages", "(Kopfbetrag)")
    said("其中至多 40 马克当场付给", F["wg_s6b"][0])
    chk("    two months (两个月)", F["wg_s6b"][1], told("其余在两个月内付清", "在", "个月"))
    # the law of 18 June and the price order of 25 June
    d18, _ = F["bu_leitsatz"]
    has("bu_leitsatz", "am 18. Juni 1948", "unmittelbar vor der Währungsreform")
    chk("    two days before (两天前)", d20 - d18, told("两天前，美英两区合成的联合经济区", "", "天前"))
    said("6 月 25 日，经济管理局局长凭这项法律的授权发布命令", mon("bu_june25", "Juni"), F["bu_june25"][0])
    has("bu_june25", "der Direktor der Verwaltung für Wirtschaft", "fast aller gewerblich hergestellten Fertigwaren")
    has("ab_erhard", "Rede des Direktors für Wirtschaft vor dem Wirtschaftsrat")
    said("4 月 21 日他就以这个身份在经济委员会演说过", mon("ab_erhard", "April"), F["ab_erhard"][1])
    assert F["ab_erhard"][2] == y48
    said("6 月 30 日，大部分配给管制的规定自动失效", mon("bu_june30", "Juni"), F["bu_june30"][0])
    # before the reform
    said("1948 年 5 月，汉堡黑市上一公斤黑麦面包要 9.5 帝国马克，一个鸡蛋要 8 帝国马克", F["bu_bread"][0],
         mon("bu_bread", "Mai"), F["bu_bread"][1], F["bu_egg"][0])
    has("bu_bread", "Ein Kilogramm Roggenbrot", "Schwarzen Markt in Hamburg")
    said("一个熟练工人干 8 小时，工资只有 10 帝国马克", *F["bu_wage"])
    has("bu_wage", "Facharbeiters")
    assert paragraph("改革以前，钱多，东西少").endswith(GUIDE)                  # the opening ends with the question


def world(F, Y, Q):
    tax, pct, debt = F["bu_taxes"]
    said("德国的税收与关税约 1850 亿帝国马克，只相当于新增债务 3350 亿帝国马克的 55\\%", tax * 1e9, debt * 1e9, pct)
    chk("    185/335", 100 * tax / debt, pct, tol=0.5)
    n39, y39, n45, d, m, y45 = F["bu_notes"]
    said("帝国银行的钞票流通额，从 1939 年的不到 120 亿帝国马克增加到 1945 年 3 月 7 日的 560 多亿", y39, n39 * 1e9, y45, m,
         d, n45 * 10)                                                         # '560 多亿': 560 (亿)
    has("bu_notes", "knapp 12", "über 56")
    d39, y, d44, y44 = F["bu_deposits"]
    said("银行的存款从 1939 年末的 510 亿增加到 1944 年秋的 1600 亿", y, d39 * 1e9, y44, d44 * 1e9)
    has("bu_deposits", "Ende 1939", "im Herbst 1944")
    chk("    up to a half (多达一半)", F["bu_barter"][0] / 100, told("多达一半甚至更多的交易是以货易货", "多达", "甚至"))
    has("bu_barter", "bis zu 50% oder mehr")
    said("官方规定的仍是每周 48 小时，改革以前实际多半只干 40 小时或更少", *F["bu_hours"])
    has("bu_hours", "meist nur 40 Stunden oder weniger")
    said("改革前三个月，联合经济区每工时的产量只有 1936 年的不到 60\\%", F["bu_productivity"][1], F["bu_productivity"][0])
    has("bu_productivity", "in den drei Monaten vor der Währungsreform", "knapp 60%")
    chk("    three months (三个月)", 3, told("改革前三个月", "改革前", "个月"))
    d5, y47 = F["ms_occasion"]
    said("1947 年 6 月 5 日，美国国务卿马歇尔", y47, mon("ms_occasion", "June"), d5)
    has("ms_occasion", "commencement exercises at Harvard University")
    has("ms_title", "REMARKS BY THE SECRETARY OF STATE")
    soldiers, workers, women = F["mof_demob"]
    said("战败以后 761 万军人复员，军需工业的 400 万工人失去了工作，其中有 75 万妇女", soldiers * 1e6, workers * 1e6, women)
    said("又有 150 万人从旧殖民地遣返", F["mof_repat"][0] * 1e6)
    said("日本面临就业人口的 17\\% 突然失业的局面", F["mof_17"][0])
    said("1944—1948 年，日本银行券的平均发行额增加到 20 倍，批发物价涨到 55.1 倍", *F["mof_20fold"])
    has("mof_20fold", "average outstanding Bank of Japan notes increased 20 fold", "wholesale prices rose 55.1 fold")
    said("日本银行以 1934—1936 年平均为 1 编的批发物价指数", 1934, 1936, 1)
    W = wpi()                                                                # its title: 1934-36 average = 1
    # fig:reconstruction_japan
    said("日本的批发物价，1944—1952 年（1934—1936 年平均为 1，对数刻度）", 1944, 1952, 1934, 1936, 1)
    assert W.index[0] == "1944-01" and W.index[-1] == "1952-12"
    m4, d20, _ = F["bj_budget49"]
    said("1949 年 4 月的道奇预算与 360 日元的单一汇率以后，涨势大大放慢", F["mof_dodgeplan"][0], m4, F["mof_360"][0])
    assert mon("mof_memo", "April") == m4
    m6, _ = F["bj_korea"]
    said("1950 年 6 月朝鲜战争爆发以后，又快涨了一阵", showa(25), m6)
    before = W["1948-12"] / W["1947-12"] - 1                               # 1948: the prices more than doubled
    slow = W["1950-06"] / W["1949-04"] - 1                                 # 14 months from the Dodge budget
    war = W["1950-12"] / W["1950-06"] - 1                                  # half a year of the war
    assert before > 1 and slow < 0.12 and war > 0.2
    # the national index and the Bank's history ('東京卸売物価 25年7月～12月 +23.5'): the same rise
    chk("    WPI December/June 1950 (Tokyo, BoJ history: 23.5%)", 100 * war, F["bj_wpi"][0], tol=0.1)


def overhang_section(F, Y, Q):
    O = OVERHANG
    said("设实际产出$Y=100$，管制价格$\\bar P=1$，$k=0.3$，人们手里的货币$M=90$", O["Y"], O["Pbar"], O["k"], O["M"])
    said("（3）先按 3 比 1 换算货币", O["ratio"], 1)
    said("（4）若放开价格以后产出增加到 120", O["Y2"])
    a = overhang(O["M"], O["k"], O["Y"], O["Pbar"])
    r = overhang(O["M"], O["k"], O["Y"], O["Pbar"], O["ratio"])
    b = overhang(O["M"], O["k"], O["Y2"], O["Pbar"])
    said("（1）愿意持有的货币是$0.3\\times1\\times100=30$，过剩货币$90-30=60$", O["k"], O["Pbar"], O["Y"], a["desired"],
         O["M"], a["desired"], a["excess"])
    said("（2）$P=90/(0.3\\times100)=3$，价格涨到 3 倍", O["M"], O["k"], O["Y"], a["P"], a["rise"])
    chk("    a third of its value (三分之一)", 1 / a["P"], told("每一单位货币只值原来的三分之一", "原来的", ""))
    said("（3）换算以后$M=30$，$P=30/30=1$，价格不变，砍掉的是 60 单位货币", r["M"], r["M"], r["desired"], r["P"],
         O["M"] - r["M"])
    assert r["P"] == O["Pbar"]                                                # 价格不变
    said("（4）$P=90/(0.3\\times120)=2.5$", O["M"], O["k"], O["Y2"], b["P"])
    assert O["Pbar"] < b["P"] < a["P"] and b["excess"] > 0                     # 少涨了一些，过剩远没有消掉
    # the German numbers
    said("改革时非银行部门缴存与申报的旧货币共 1450 亿帝国马克", F["bu_145"][0] * 1e9)
    said("（1）12 月末的新货币相当于旧货币的百分之几", 12)
    said("以工业生产代表产出，6 月到 12 月价格水平该涨多少", 6, 12)
    jun, y48, dec = F["bu_newmoney"]
    has("bu_newmoney", "Ende Juni", "bis Ende Dezember 1948 auf rund 12 Mrd. DM")
    said("新创造的货币 6 月末是 44 亿德国马克，1948 年 12 月末约 120 亿德国马克", 6, jun * 1e9, y48, 12, dec * 1e9)
    I = ipb()
    said("联合经济区 1948 年 6 月是 51，12 月是 79", 1948, 6, I["1948-06"], 12, I["1948-12"])
    assert "Index 1936 = 100" in transcription("ri_ipb_def") and "IPB" in transcription("ri_ipb_def")
    old = F["bu_145"][0]
    said("（1）$120/1450\\approx8.3\\%$", dec * 10, old * 10, 100 * dec / old)
    chk("    a twelfth (十二分之一)", 1 / 12, told("不到旧货币的十二分之一", "旧货币的", ""))
    assert dec / old < 1 / 12
    mg, yg = dec / jun, I["1948-12"] / I["1948-06"]
    said("（2）货币增加到$120/44\\approx2.73$倍，产出增加到$79/51\\approx1.55$倍，$P$应增加到$2.73/1.55\\approx1.76$倍，即涨 76\\%",
         dec * 10, jun * 10, mg, I["1948-12"], I["1948-06"], yg, mg, yg, mg / yg, 100 * (mg / yg - 1))
    _, _, ind = F["bu_prices"]
    food = F["bu_prices2"][0]
    said("6—12 月工业品的生产者价格涨了 14\\%，食品涨了 18\\%", 6, 12, ind, food)
    has("bu_prices", "zwischen Juni und Dezember 1948", "die Erzeugerpreise gewerblicher Produkte um 14%")
    has("bu_prices2", "Ernährung im Rahmen des Lebenshaltungskostenindex")
    assert max(ind, food) < 100 * (mg / yg - 1) / 4                              # 涨得少得多
    # the compare box
    said("存款与债务大体按 10 比 1 换算", *F["ug_s2"])
    said("1948 年秋天加快的回升几乎没有波及那里", F["ri_autumn"][0])
    has("ri_autumn", "im Herbst 1948 weitgehend unberührt")
    said("里价格涨到 3 倍", a["rise"])
    chk("    two thirds lost (三分之二)", 1 - 1 / a["rise"], told("货币的持有者损失三分之二", "损失", ""))
    said("工资与租金按 1 比 1 不变", *F["ug_s18"])
    said("6 月 20 日的《货币法》与一周以后公布的《换算法》", mon("wg_date", "Juni"), F["wg_date"][0])
    has("bu_week", "eine Woche nach dem Erlaß des Währungsgesetzes")
    said("6 月 25 日的价格命令，6 月 30 日配给规定失效", 6, F["bu_june25"][0], 6, F["bu_june30"][0])
    said("\\cmprow{1948 年的西德}", y48)
    said("1948 年 10 月在《新苏黎世报》上说", F["bu_ropke"][0], mon("bu_ropke", "Oktober"))
    d, m, yy = F["bu_ropke_nzz"]
    assert (m, 1900 + yy) == (10, F["bu_ropke"][0]) and "Neue Zürcher Zeitung" in Q["bu_ropke_nzz"]
    has("bu_ropke_french", "in der französischen Zone die Währungsreform ohne")


def germany(F, Y, Q):
    d, m, yy = F["bu_clay_date"]
    chk("    two years before (两年前)", F["wg_s1"][1] - (1900 + yy), told("方案两年前就有了雏形", "方案", "年前"))
    said("1946 年 5 月，美国军政长官克莱", 1900 + yy, m)
    has("bu_clay_date", "Clay to AGWAR")
    has("bu_cdg", "Colm-Dodge-Goldsmith (CDG)-Plan", "Hauptautoren", "Clays Finanzberater Joseph Dodge")
    chk("    three authors (三位)", len("Colm-Dodge-Goldsmith".split("-")), told("方案按三位主要作者", "按", "位"))
    said("它主张货币债权债务一律按 10 比 1 贬值", *F["bu_cdg_terms"])
    has("bu_cdg_terms", "Löhne, Mieten und Steuern unberührt")
    said("到 1948 年 3 月中", F["bu_march"][0], mon("bu_march", "März"))
    has("bu_march", "Mitte März 1948")
    said("4 月末，盟国把要点告诉了", 4)
    has("bu_conclave", "Ende April", "Konklave von Rothwesten bei Kassel")
    said("旧存款的 70\\% 勾销，20\\% 冻结，10\\% 换成新钱", *F["bu_principles"])
    has("bu_principles", "Annullierung der Reichsschuld")
    has("bu_lastenausgleich_hands", "in deutsche Hände")
    chk("    four laws (四项)", 4, told("最后由军政府颁布了四项基本法律", "颁布了", "项"))
    has("bu_four", "Vier grundlegende Gesetze")
    said("6 月 20 日先生效的是《发行法》与《货币法》", mon("bu_sunday", "Juni"), F["bu_sunday"][0])
    assert Q["bdl_date"].startswith("rz 1948 vom 1. M")                      # '(Mä)rz 1948 vom 1. M(ärz)'
    said("这家中央银行是军政府 1948 年 3 月 1 日的法律设立的", F["bdl_date"][0], 3, F["bdl_date"][1])
    said("10 月 4 日的《冻结账户法》", mon("fk_date", "Oktober"), F["fk_date"][0])
    assert F["bu_fk_date"] == [F["fk_date"][0], 10, F["fk_date"][1]]           # Buchheim: 4. 10. 1948
    table_conversion(F, Y, Q)
    said("较大的帝国马克存款最终按 100 比 6.5 换成了德国马克", *F["bu_65"])
    said("到 1957 年才按面额的 10\\% 换成新的债权", F["bu_1957"][0], F["bu_1957b"][0])
    has("bu_reich", "Reichsbahn und Reichspost, der NSDAP")
    said("德国专家原想让私人的长期债务按 1 比 1 换算", *F["bu_debtors11"])
    has("bu_debtors", "Sachwertbesitzer")
    y23 = int(re.search(r"(\d{4}) 年 11 月 20 日，柏林交易所把美元的官价定在", chapter("ch26_weimar")).group(1))
    said("这和 1923 年的稳定不一样", y23)
    said("1948 年的物价被管制压着", F["wg_s1"][1])
    household(F, Y, Q)


def table_conversion(F, Y, Q):
    """tab:reconstruction-conversion, as the laws word it."""
    t = tex_text()
    R = rules()
    fk7, fk10 = F["fk_s1a"]
    lines = [
        f"人头额 & 每个居民以同样面额的旧钞换至多 {R['head']:.0f} 德国马克，先付至多 {R['first']:.0f} & 货币法第 "
        f"{sect('wg_s6')} 条 \\\\",
        f"企业的周转额 & 每个雇员 {R['firm']:.0f} 德国马克 & 货币法第 {sect('wg_s17')} 条 \\\\",
        f"存款 & 先为每个家庭成员扣除 {R['per']:.0f} 帝国马克，抵消人头额；余下的每 {F['ug_s2'][0]:.0f} 帝国马克记 "
        f"{F['ug_s2'][1]:.0f} 德国马克，一半记入自由账户，一半记入冻结账户 & 换算法第 {sect('ug_s2')}、{sect('ug_s4')} 条 \\\\",
        f"冻结账户 & 每 {fk10:.0f} 德国马克勾销 {fk7:.0f} 马克，{F['fk_s1b'][0]:.0f} 马克转入自由账户，余下的只能投资于中长期证券 "
        f"& 冻结账户法第 {sect('fk_s1a')} 条 \\\\",
        f"私人债务 & 每 {F['ug_s16'][0]:.0f} 帝国马克还 {F['ug_s16'][1]:.0f} 德国马克 & 换算法第 {sect('ug_s16')} 条 \\\\",
        f"工资、租金、养老金 & {mon('ug_s18d', 'Juni')} 月 {F['ug_s18d'][0]:.0f} 日以后到期的，{F['ug_s18'][0]:.0f} 帝国马克付 "
        f"{F['ug_s18'][1]:.0f} 德国马克 & 换算法第 {sect('ug_s18')} 条 \\\\",
        f"帝国与纳粹党的债务 & 不适用换算的规定 & 换算法第 {sect('ug_s14')} 条 \\\\",
        f"银行之间的债务 & 一律消灭；资产不够抵偿存款的银行，得到年息 {R['equal']:.0f}\\% 的平衡债权 & 换算法第 "
        f"{sect('ug_s11')}、{sect('ug_s18c')} 条 \\\\"]
    for line in lines:
        assert line in t, line
        COVERED.append(line)
    has("ug_s4b", "r jede Person, die zu seiner Familie geh")
    has("ug_s18w", "Miet- und Pachtzinsen", "Renten, Pensionen")
    has("fk_s1c", "mittel- oder langfristigen Wertpapieren")
    has("ug_s14", "Verbindlichkeiten des Reichs", "Verbindlichkeiten der NSDAP")
    has("ug_s18c", "ltnissen zwischen Geldinstituten")
    has("ug_s11c", "verzinsliche Ausgleichsforderung")
    assert "j" + Q["ug_s11c"][:5] not in Q["ug_s11"] and Q["ug_s11"] == "eine mit drei vom Hundert"
    said("\\caption{西德货币改革的换算规则（1948 年）", F["wg_s1"][1])
    said("\\datasource{《货币法》（第 61 号法律）、《换算法》（第 63 号法律）与《冻结账户法》（第 65 号法律）",
         F["wg_number"][0], F["ug_number"][0], F["fk_number"][0])


def household(F, Y, Q):
    """ex:reconstruction-household and self-check 2, by the rules of the table."""
    H, S = HOUSEHOLD, SINGLE
    chk("    four persons (四口之家)", H["persons"], told("设一个四口之家", "一个", "口之家"))
    chk("    two children (两个)", H["children"], told("父母与两个未满 18 岁的孩子", "父母与", "个未满"))
    assert H["persons"] == 2 + H["children"]
    said("父母与两个未满 18 岁的孩子", F["ug_family"][2])
    has("ug_family", "das achtzehnte Lebensjahr nicht vollendet haben")
    said("改革前手里有 240 帝国马克的现钞，银行里有 10000 帝国马克的存款，欠别人 500 帝国马克，父亲的月工资是 300 帝国马克",
         H["cash"], H["deposit"], H["debt"], H["wage"])
    said("（2）存款到 6 月末记入两个账户的各是多少", mon("wg_s1", "Juni"))
    said("（3）10 月以后呢", mon("fk_date", "Oktober"))
    R = rules()
    c = convert(H["cash"], H["deposit"], H["persons"])
    said("（1）每人至多 60 马克，四人 240 马克，现钞按 1 比 1 全部换成德国马克", R["head"], c["kopf"], 1, 1)
    assert c["kopf"] == H["cash"] == R["head"] * H["persons"]
    said("（2）存款先扣除$4\\times540=2160$帝国马克，余下 7840 帝国马克，按 10 比 1 得 784 德国马克，自由账户与冻结账户各 392 马克",
         H["persons"], R["per"], c["deducted"], c["base"], 1 / R["rate"], 1, c["dm"], c["free"])
    said("（3）冻结的 392 马克里，勾销 274.4 马克，78.4 马克转入自由账户，39.2 马克只能投资", c["frozen"], c["cancel"],
         c["freed"], c["invest"])
    said("家庭最后有$240+392+78.4+39.2=749.6$德国马克，原来的 10240 帝国马克只剩 7.3\\%", c["kopf"], c["free"], c["freed"],
         c["invest"], c["total"], H["cash"] + H["deposit"], 100 * c["share"])
    said("（4）债务只需还 50 德国马克，6 月 20 日以后的工资按 300 德国马克照发", H["debt"] * R["debt"], 6, F["ug_s18d"][0],
         H["wage"] * R["wage"])
    chk("    more than nine tenths lost (九成以上)", 0.9, told("持有货币的家庭损失了九成以上", "损失了", "以上"))
    assert 1 - c["share"] > 0.9
    # self-check 2
    s = convert(S["cash"], S["deposit"], S["persons"])
    said("一个单身的人改革前有 360 帝国马克的现钞与 3000 帝国马克的存款", S["cash"], S["deposit"])
    said("到 10 月以后他一共有多少德国马克", 10)
    said("现钞里的 60 马克换成 60 德国马克，余下的 300 帝国马克存入银行，存款共 3300 帝国马克", s["kopf"], s["kopf"],
         S["cash"] - s["kopf"], s["dep"])
    said("扣除 540 帝国马克，余下 2760 帝国马克，得 276 德国马克，自由与冻结账户各 138 马克", s["deducted"], s["base"],
         s["dm"], s["free"])
    said("10 月以后冻结的 138 马克里，27.6 马克转入自由账户，13.8 马克只能投资", 10, s["frozen"], s["freed"], s["invest"])
    said("他一共有$60+138+27.6+13.8=239.4$德国马克", s["kopf"], s["free"], s["freed"], s["invest"], s["total"])
    # self-check 3: a deposit below 540 RM a member converts to nothing
    said("每个家庭成员要先扣除 540 帝国马克。一个人的存款若不到 540 帝国马克", R["per"], R["per"])
    assert convert(R["head"], R["per"] - 1, 1)["dm"] == 0 < convert(R["head"], R["per"] + 10, 1)["dm"]
    said("人头额已经按 1 比 1 换过", 1, 1)


def cost(F, Y, Q):
    said("单是金融机构的储蓄存款就有 700 多亿帝国马克", F["bu_savings"][0] * 10)
    has("bu_savings", "über 70 Mrd. RM")
    said("到 1948 年末，记入自由账户的却只有 53 亿德国马克", F["bu_newmoney"][1], F["bu_freikonto"][0] * 1e9)
    has("bu_freikonto", "Davon waren 5,3 Mrd. DM Gutschriften auf Freikonto")
    said("许多储户的存款不到人头额的 10 倍", 10)
    has("bu_empty", "als ein Zehntel ihrer RM-Bestände")
    said("10 月的冻结账户决定又让人们对德国马克的信心一度大大减弱", mon("bu_confidence", "Oktober"))
    has("bu_confidence2", "Schwächung des Vertrauens in die D-Mark")
    has("bu_expellees", "Vertriebenen", "arbeitslos", "bankrott", "Lebensmittelrationen")
    has("bu_welfare", "kirchlicher Wohlfahrtsorganisationen")
    said("自有资本总体上保住了 96\\%", F["bu_equity"][0])
    d31, y = F["wg_lastenausgleich"]
    said("“紧迫的、必须在 1948 年 12 月 31 日以前解决的任务”", y, mon("wg_lastenausgleich", "Dezember"), d31)
    has("bu_soforthilfe", "Soforthilfegesetz")
    d8, y49 = F["bu_soforthilfe2"]
    said("头一项办法《紧急救助法》1949 年 8 月 8 日才生效，正式的《负担平衡法》1952 年 8 月才通过", y49,
         mon("bu_soforthilfe2", "August"), d8, F["bu_lag"][0], mon("bu_lag", "August"))
    said("负担平衡的财产税原则上按 50\\% 征收", F["bu_levy50"][0])
    y79, levy = F["bu_levy42"]
    _, y48, wealth = F["bu_wealth300"]
    said("到 1979 年征收期结束，它一共只收了 420 亿德国马克；1948 年的财产单是可再生产的部分，就估计在 3000 亿德国马克以上",
         y79, levy * 1e9, y48, wealth * 1e9)
    has("bu_wealth300", "über 300 Mrd. DM")
    a, b, d1, m1, y40 = F["bu_altsparer2"]
    assert (d1, m1) == (1, 1)                                                  # 1940 年初: am 1.1. 1940
    said("1953 年的《老储户法》也只把一部分储蓄的换算率提高到 10 比 2，条件是 1940 年初就已持有", F["bu_altsparer"][2], a, b, y40)
    y, raw, ind = F["bu_prices"]
    food, cloth = F["bu_prices2"]
    said("1948 年 6 月到 12 月，工业原料的价格涨了 26\\%，生活费用指数里的食品涨了 18\\%，衣着涨了 35\\%", y, 6, 12, raw, food,
         cloth)
    has("bu_prices", "Die Preise industrieller Grundstoffe")
    has("bu_wagestop", "Lohnstopp")
    said("1948 年 12 月的一次民意调查里，70\\% 的受访者认为应当恢复价格管制", F["bu_poll"][0], mon("bu_poll", "Dezember"),
         F["bu_poll"][1])
    has("bu_pressure", "Wiedereinführung von Elementen staatlicher Bewirtschaftung und Preiskontrolle")
    said("12 月，物价的趋势掉了头", mon("bu_turn", "Dezember"))
    q4, y = F["bu_surplus"]
    said("公共预算从 1948 年第四季度起有了盈余", y)
    chk("    the fourth quarter (第四季度)", q4, told("公共预算从 1948 年第四季度起", "第", "季度"))
    has("bu_surplus", "Kreditrestriktion")
    has("bu_hoarding", "Marshallplan-Einfuhren", "Hortung")
    said("1949 年，基督教民主联盟", F["bu_election"][0])
    has("bu_election", "ersten Bundestagswahlkampfes")
    chk("    the first Bundestag (第一届)", 1, told("赢得了第一届联邦议院的选举", "第", "届"))
    # unemployment
    U, E = unemployment(), employment()
    said("按德意志各邦银行 1950 年 2 月的月报", F["bdl_report"][0], mon("bdl_report", "Februar"))
    said("联邦地区的失业人数 1948 年 6 月是 45 万，1949 年 12 月是 156 万，1950 年 2 月到了 198 万", 1948, 6, U["1948-06"] * 1e3,
         1949, 12, U["1949-12"] * 1e3, 1950, 2, U["1950-02"] * 1e3)
    said("就业人数大体不变，1948 年 6 月是 1347 万，1949 年 12 月是 1356 万", 1948, 6, E["1948-06"] * 1e3, 1949, 12,
         E["1949-12"] * 1e3)
    assert E.max() / E.min() < 1.02 and U["1950-02"] > 4 * U["1948-06"]          # 大体不变；失业增加
    assert "Arbeitslose in 1000" in transcription("bdl_unemp") and "Beschäftigte in 1000" in transcription("bdl_emp")
    has("bdl_credit", "Programm zur Bekämpfung der Arbeitslosigkeit", "Kredithilfe zugesagt")
    parts = F["bdl_parts"]
    said("政府有一个 9.5 亿德国马克的特别计划", F["bdl_950"][0] * 1e6)
    has("bdl_950", "Sonderprogramm")
    chk("    four parts (四项)", len(parts), told("中央银行答应为其中的四项提供再融资", "其中的", "项"))
    said("联邦铁路 2.5 亿，小额投资的工业信贷 0.5 亿", parts[0] * 1e6, parts[1] * 1e6)
    said("失业特别严重的州的投资与出口融资，各 3 亿", parts[2] * 1e6)
    assert parts[2] == parts[3]
    has("bdl_parts", "Bundesbahn", "Kleininvestitionen", "besonders hoher Arbeitslosigkeit",
        "Exportfinanzierungsprogramm")
    said("剩下邮政的 0.5 亿", F["bdl_post"][0] * 1e6)
    chk("    250 + 50 + 300 + 300 + 50 = 950", sum(parts) + F["bdl_post"][0], F["bdl_950"][0])
    said("住房建设计划在这一个建筑季里至少要投入 25 亿德国马克", F["bdl_housing"][0] * 1e9)
    has("bdl_housing", "in der bevorstehenden Bausaison", "mindestens 2,5 Mrd. DM")
    has("bu_westberlin", "unter Ausschluß Westberlins")
    has("bu_soviet", "die totale Berlin-Blockade begann")
    # fig:reconstruction_germany
    _, _, y36, base = F["ri_ipb_def"]
    said("(a) 官方的工业生产指数（1936 年为 100）", y36, base)
    said("竖线是 1948 年 6 月的货币改革", 1948, 6)
    said("法国占领区 1947 年的数是 Manz 按产值平减的估计", F["ri_ipf_def"][1])
    has("ri_ipf_def", "den deflationierten Wertreihen nach M a n z für 1947", "der offiziellen ab Januar 1948")
    said("(b) 联邦地区的失业人数（千人），1948 年 3 月到 1950 年 2 月", 1948, 3, 1950, 2)
    assert U.index[0] == "1948-03" and U.index[-1] == "1950-02"
    said("数据：Ritschl（1985）表 1；德意志各邦银行 1950 年 2 月月报第 57 页", src_year("ritschl1985"), 1, 1950, 2,
         page("bdl_unemp"))
    assert transcription("ri_ipb_def").startswith("Tab. I |")


def marshall(F, Y, Q):
    say("欧洲今后三四年需要从国外、主要是从美国买的粮食与必需品")
    has("ms_ability", "the next three or four years", "principally from America")
    d3, y48 = F["eca_approved"]
    said("1948 年 4 月 3 日，《经济合作法》获得批准", y48, mon("eca_approved", "April"), d3)
    assert F["eca_title"][0] == y48 and "Economic Cooperation Act of 1948" in Q["eca_title"]
    d22, y47 = F["eca_pledges"]
    said("依据的是 1947 年 9 月 22 日在巴黎签署的欧洲经济合作委员会报告", y47, mon("eca_pledges", "September"), d22)
    has("eca_organization", "multilateral undertakings")
    has("eca_43", "for the period of one year following the date of enactment")
    said("法律为生效以后的一年授权至多 43 亿美元的拨款；拨款以前，复兴金融公司先垫付至多 10 亿美元", F["eca_43"][0],
         F["eca_rfc"][0])
    has("eca_bilateral", "shall conclude an agreement with the United States")
    has("eca_special2", "on a grant basis")
    y0, y1, total, uk, fr, _, _ = F["de_amounts"]
    said("1948—1951 年美国为欧洲复兴提供了 132 亿美元，其中英国 32 亿美元，法国 27 亿美元", y0, y1, total * 1e9, uk * 1e9,
         fr * 1e9)
    three, _, _, fifth = F["de_share"]
    said("这些援助不到受援国国民收入合计的 3\\%", three)
    chk("    a fifth of investment (五分之一)", fifth, told("不到它们总投资的五分之一", "总投资的", ""))
    said("只有 17\\% 的援助美元花在", F["de_machinery"][0])
    has("de_materials", "industrial materials, semi-finished products and agricultural commodities")
    said("援助只让西欧 1951 年以后的国民收入高了约 2\\%", *F["de_two"])
    has("de_two", "Eichengreen and Uzan's estimates")
    has("de_attrition", "war of attrition", "a deficit in the government's budget")
    said("这样的冲突很容易让总需求超过供给 7\\% 到 8\\%", *F["de_gap"])
    said("基础货币每年就得增加相当于国内生产总值的 8\\%", F["de_hpm"][0])
    said("相当于国民产出 2.5\\% 的援助", F["de_aid25"][0])
    four, six, eight = F["de_four_years"]
    chk("    four years (四年)", four, told("二战以后各国国内的物价稳定用了四年", "用了", "年"))
    chk("    the sixth year (第六年)", six, told("德国的恶性通胀发生在第六年", "第", "年"))
    chk("    eight years (八年)", eight, told("法国的通胀持续了八年", "持续了", "年"))
    said("受援国每得到 1 美元援助", 1)
    has("de_counterpart", "For every dollar of Marshall Plan aid received")
    has("de_britain", "to retire public debt")
    has("ab_counterpart_name", "Gegenwertmittel")
    goods, ind, two3 = F["ab_99"]
    said("到 1948 年末，运到联合经济区的物资总值不到 9900 万美元，其中工业品只有 2200 万美元", 1948, goods * 1e6, ind * 1e6)
    has("ab_99", "bis zum Jahresende", "knapp 99 Mio. Dollar", "Baumwolle")
    chk("    two thirds (三分之二以上)", two3, told("三分之二以上是棉花", "", "以上"))
    said("到那时为止答应的援助，只有 27\\% 真的到了", F["ab_27"][0])
    has("ab_political", "der politische Gewinn")
    said("照德意志各邦银行 1950 年的月报", F["bdl_report"][0])
    has("bdl_kfw", "der bei weitem größte Teil der westdeutschen Counterpart funds")
    has("de_offered", "ostensibly offered to Eastern Europe, and even to the U.S.S.R.")
    has("de_moscow", "central planning")
    said("1950 年，西欧各国谈成了欧洲支付同盟", F["de_epu"][0])
    # fig:reconstruction_marshall
    A = marshall_aid()
    four_ = A["英国"] + A["法国"] + A["意大利"] + A["西德"]
    said("马歇尔计划的援助，1948—1951 年（亿美元）。英、法、意与西方占领的德国四国合计 88 亿美元，其余受援国合计 44 亿美元，是总数 "
         "132 亿美元减去四国之和", y0, y1, four_ * 1e9, A["其他"] * 1e9, A["total"] * 1e9)
    said("数据：De Long and Eichengreen（1991）第 14 页", F["de_wp"][1], page("de_amounts"))


def japan(F, Y, Q):
    chk("    two years earlier (早两年)", F["wg_s1"][1] - F["mof_ordinances"][1], told("日本比西德早两年动手", "早", "年"))
    d17, y46 = F["mof_ordinances"]
    said("1946 年 2 月 17 日，日本政府发布《金融紧急措施令》与《日本银行券存入令》", y46, mon("mof_ordinances", "February"), d17)
    has("mof_ordinances", "effective immediately")
    assert F["bjc_1946"][0] == 2 and "金融緊急措置令・日本銀行券預入令" in Q["bjc_1946"]
    has("mof_frozen", "all individuals and corporations")
    said("到 3 月 2 日一律作废", mon("mof_void", "March"), F["mof_void"][0])
    said("户主 300 日元，其他家庭成员每人 100 日元", *F["mof_withdraw"])
    said("企业发工资，每个雇员每月至多取 500 日元", F["mof_wages"][0])
    _, m12, n12, s16, n916, f16, n216, oct_, dec = F["bj_notes"]
    has("bj_notes", "3月12日には152億円", "9月16日には618億円", "2月16日の615億円", "12月末には934億円")
    said("日本银行券的发行额在 2 月 16 日是 615 亿日元，3 月 12 日缩到 152 亿日元", 2, f16, n216 * 1e8, 3, m12, n12 * 1e8)
    said("9 月 16 日，它回到 618 亿日元，超过了措施实施以前的水平；12 月末达到 934 亿日元", 9, s16, n916 * 1e8, 12, dec * 1e8)
    assert n916 > n216
    _, total, free, frozen, special = F["mof_table46"]
    has("mof_table46", "March 1946")
    said("1946 年 3 月末，全国银行的第一类冻结账户余额是 944.5 亿日元，自由账户只有 145.2 亿日元，各类存款合计 1357.5 亿日元",
         1946, 3, frozen * 1e6, free * 1e6, total * 1e6)
    has("mof_leak", "to settle their bills", "for living expenses")
    y48, f48, free48 = F["mof_frozen48"]
    said("到 1948 年 6 月，冻结账户只剩 298.4 亿日元，自由账户却有 2627 亿日元", y48, mon("mof_frozen48", "June"), f48 * 1e6,
         free48 * 1e6)
    cls, y = F["mof_erased"]
    said("1948 年 2 月，第二类冻结存款被勾销了一部分", y, mon("mof_erased", "February"))
    chk("    Class 2 (第二类)", cls, told("第二类冻结存款被勾销了一部分", "第", "类"))
    has("mof_losses", "losses for depositholders")
    said("7 月 21 日，冻结存款的制度结束", mon("mof_end", "July"), F["mof_end"][0])
    d19, y = F["mof_indemnity_law"]
    said("1946 年 10 月 19 日通过的《战时补偿特别措施法》，对向政府的请求权征收税率 100\\% 的特别税", y,
         mon("mof_indemnity_law", "October"), d19, F["mof_tax100"][0])
    has("mof_endpay", "effectively put an end to the payments")
    # the budget and the Reconstruction Finance Bank
    _, fy, final, debt, pct = F["bj_budget"]
    said("1946 年度一般会计的最终预算是 1191 亿日元，靠公债与借款筹来的 445 亿日元占了 37.4\\%", showa(fy), final * 1e8,
         debt * 1e8, pct)
    chk("    445/1191", 100 * debt / final, pct, tol=0.05)
    has("bj_ishibashi", "石橋蔵相の主張する生産再開・増強のための積極政策", "占領軍経費の負担")
    said("1946 年 12 月，内阁决定实行“倾斜生产”", F["mof_priority"][0], mon("mof_priority", "December"))
    has("mof_priority", "increases in coal production would be used to increase steel production")
    _, _, d24, y47, cap = F["mof_rfb"]
    said("这家政府金融机构 1947 年 1 月 24 日成立，政府出资 40 亿日元", y47, mon("mof_rfb", "January"), d24, cap * 1e9)
    said("到 1947 年度末，煤炭业占了它全部贷款的 33\\%", F["mof_coal"][1], F["mof_coal"][0])
    has("mof_coal", "as of the end of fiscal 1947")
    # the United States
    d10, y48 = F["f6_date"]
    assert F["f6_sent"][0] == d10 and "December 10" in Q["f6_sent"]            # the second date of the statement
    said("1948 年 12 月 10 日，美国政府发表声明", y48, mon("f6_date", "December"), d10)
    has("f6_title", "Economic Stabilization in Japan")
    has("f6_aims", "fiscal, monetary, price, and wage stability, and maximum production for export")
    has("f6_measures", "tax collection", "limitation of credit extension", "wage stability")
    letters = [Q["f6_budget"][0], Q["f6_last"][0]]
    assert letters == ["a", "i"] and "c ." in Q["f6_measures"] and "d ." in Q["f6_measures"]
    chk("    nine measures a-i (九项)", ord(letters[1]) - ord(letters[0]) + 1, told("声明列出九项措施", "列出", "项措施"))
    has("f6_ration", "allocation and rationing system")
    chk("    three months (三个月)", F["f6_rate"][0], told("至迟三个月内要定下单一汇率", "至迟", "个月"))
    _, _, m, d = F["bj_truman"]
    assert showa(F["bj_truman"][0]) == F["bj_truman"][1] == y48
    said("12 月 11 日，杜鲁门", m, d)
    has("bj_truman", "デトロイト銀行のジョセフ・M・ドッジ（Joseph M. Dodge）頭取", "財政顧問（Financial Adviser）")
    said("12 月 14 日国务院致电道奇", 12, F["f6_lovett"][0])
    has("f6_lovett", "December 14 telegraphed Mr. Dodge")
    has("bj_dodge_germany", "軍政部財政部長", "通貨改革・銀行改革")
    n7, sy, m2, d1 = F["bj_mission"]
    said("包括他在内 7 个人的调查团，1949 年 2 月 1 日到了日本", n7, showa(sy), m2, d1)
    said("3 月 7 日，道奇发表声明", *F["bj_march7"])
    has("bj_germany", "ドラスティックな通貨の切捨て")
    has("bj_aid", "アメリカの市民や企業に課せられた税金", "いつまでも続くものではない")
    m4, d20, sy = F["bj_budget49"]
    sy2, gen, net = F["bj_surplus"]
    assert sy == sy2
    said("1949 年度的预算 4 月 20 日通过，一般会计有 3 亿日元的盈余，整个财政的净计预算盈余 1567 亿日元", showa(sy), m4, d20,
         gen * 1e8, net * 1e8)
    sy3, m3, bonds = F["bj_rfbbonds"]
    said("到 1949 年 3 月末，复兴金融债券的余额是 1091 亿日元", showa(sy3), m3, bonds * 1e8)
    has("bj_rfbbonds", "年度中に全額償還")
    has("bj_rfbstop", "復興金融金庫が新規融資業務を停止")
    said("1949 年度实行的这套政策叫作道奇计划", F["mof_dodgeplan"][0])
    # the single rate
    y49, lo, hi = F["mof_range"]
    said("1949 年 1 月，出口用的汇率从 1 美元兑 160 日元到 600 日元不等", y49, mon("mof_range", "January"), 1, lo, hi)
    share, *rates = F["mof_textiles"]
    said("纺织品占出口的 60\\%", share)
    chk("    three rates (三种)", len(rates), told("它的汇率就有三种", "就有", "种"))
    has("mof_textiles", "There were three rates in place for textiles")
    said("三种汇率是 420、350 与 330 日元", *rates)
    said("盟军总部考虑过 300 日元或 400 日元，最后定为 360 日元", *F["mof_300"], F["mof_360"][0])
    d23, _, d25 = F["mof_memo"]
    said("汇率由 4 月 23 日的盟军总部备忘录确定，4 月 25 日生效", mon("mof_memo", "April"), d23, 4, d25)
    assert F["bjc_360"][1] == F["mof_360"][0] and "April 1949" in column("note")["bjc_360"]
    m4, loss = F["bj_silk"]
    said("制丝业者的损失估计约 14 亿日元", loss * 1e8)
    assert m4 == 4 and "単一為替相場設定" in transcription("bj_silk")
    yen_example(F, Y, Q)
    # the occupation's hand
    d2, y49 = F["f9_date"]
    said("1949 年 5 月 2 日，国务院东北亚司的一份备忘录写道", y49, mon("f9_date", "May"), d2)
    has("f9_memo", "Division of Northeast Asian Affairs")
    has("f9_role", "has been negative")
    said("去年 12 月的稳定指令", mon("f9_reversed", "December"))
    has("f9_reversed", "stabilization directive of last December")
    assert F["f9_date"][1] - 1 == F["f6_date"][1]                              # 'last December': December 1948
    occ, a, b = F["f9_occupation"]
    said("新年度预算里的占领费用是 1250 亿日元", occ * 1e9)
    chk("    five sevenths (七分之五)", a / b, told("约为预计的美国援助的七分之五", "援助的", ""))
    has("f9_occupation", "125 billion yen", "roughly 5/7 of the value of anticipated GARIOA and EROA aid")
    said("1949 年 5 月，夏普", F["mof_shoup"][0], mon("mof_shoup", "May"))
    m5, d17, _ = F["bj_ichimada"]
    said("同月 17 日，日本银行总裁一万田尚登", d17)
    assert m5 == 5 and "全国銀行大会" in transcription("bj_ichimada")
    has("bj_rerelease", "財政償還金を適当に再放出")
    said("1950 年 1—6 月，东京的零售物价跌了 7.9\\%", showa(25), 1, 6, F["bj_retail"][0])
    has("bj_retail", "東京小売物価 | 25年1月～6月 − 7.9")
    said("1949 年 6 到 8 月，日本银行开始买进复兴金融债券", F["mof_rfbbuy"][0], 6, 8)
    has("mof_rfbbuy", "during the JuneAugust period of 1949")
    y, amount = F["mof_321"]
    said("到 1949 年末，为弥补道奇计划造成的资金短缺，它累计买进了 321 亿日元", y, amount * 1e9)
    _, l48, y1, l49, y2, l50, y3 = F["mof_bojlending"]
    said("日本银行对商业银行的贷款，1948 年末是 493 亿日元，1949 年末 842 亿日元，1950 年末 2556 亿日元", y1, l48 * 1e6, y2,
         l49 * 1e6, y3, l50 * 1e6)
    has("mof_bojlending", "BOJ lending to commercial banks")
    said("1950 年 3 月前后，道奇开始批评货币政策", F["mof_dodge_critical"][0], mon("mof_dodge_critical", "March"))
    # the dismissals
    said("1949 年 10 月 27 日，苏联代表在远东委员会指责", F["f9_sebald"][1], 10, F["f9_soviet"][0])
    has("f9_soviet", "FEC 27 October meeting")
    said("11 月 11 日，美国驻日代理政治顾问西博尔德", mon("f9_sebald", "November"), F["f9_sebald"][0])
    has("f9_sebald", "The Acting Political Adviser in Japan")
    n126, y = F["f9_law126"]
    p20, p10 = F["f9_cuts"]
    said("按国会 1949 年 5 月通过的第 126 号法律，政府职员总共削减约 20\\%，夏天解雇了正式在册人员的约 10\\%", y,
         mon("f9_law126", "May"), n126, p20, p10)
    has("f9_cuts", "during the summer months", "regular government payroll")
    # Korea
    m6, d25 = F["bj_korea"]
    said("1950 年 6 月 25 日，朝鲜战争爆发", showa(25), m6, d25)
    assert "1950 (Showa 25)" in column("note")["bj_korea"]
    sy, m1, d7, contracts, paid = F["bj_tokuju"]
    said("到 1951 年 1 月 7 日的约半年里，特需的合同累计 1.91 亿美元", showa(sy), m1, d7, contracts)
    has("bj_tokuju", "約半年間に累計")
    said("1950 年下半年，矿工业生产指数升了 24.7\\%，东京的批发物价涨了 23.5\\%", showa(F["bj_mining"][0]), F["bj_mining"][1],
         F["bj_wpi"][0])
    has("bj_mining", "25年下期中に24.7%上昇")
    has("bj_wpi", "東京卸売物価 | 25年7月～12月")
    p25, y51, p35, y52 = F["mof_tokuju"]
    said("1951 年相当于出口的 25\\%，1952 年相当于 35\\%", y51, p25, y52, p35)
    # the compare box
    said("{西德（1948）}{日本（1949）}", F["wg_s1"][1], F["mof_dodgeplan"][0])
    said("\\cmprow{货币}{存款与债务按 10 比 1 换算", *F["ug_s2"])
    chk("    seven tenths (十分之七)", F["fk_s1a"][0] / F["fk_s1a"][1], told("冻结账户十分之七勾销", "冻结账户", "勾销"))
    said("1946 年冻结存款，发新钞", y46)
    said("6 月 25 日放开大部分工业品的价格", 6, F["bu_june25"][0])
    said("公共预算从 1948 年第四季度起有盈余", F["bu_surplus"][1])
    said("1949 年度净计预算盈余 1567 亿日元", showa(sy2), net * 1e8)
    said("合 30 美分", F["bu_30cents"][0])
    said("1 美元兑 360 日元", 1, F["mof_360"][0])
    U = unemployment()
    said("失业增加到 1950 年初的近 200 万", 1950, None)
    assert 190 <= U["1950-02"] / 10 < 200 and U.index[-1] == "1950-02"
    said("政府职员削减约 20\\%", p20)


def yen_example(F, Y, Q):
    """ex:reconstruction-yen: the textile rates of 1949 and the single rate."""
    Yn = YEN
    assert Yn["old"] in F["mof_textiles"] and Yn["importer"] in F["mof_textiles"] and Yn["new"] == F["mof_360"][0]
    said("设一家棉纺织品出口商按 1 美元兑 420 日元结汇，一年卖出 1 万美元的货", 1, Yn["old"], Yn["sales"])
    said("（1）改按 360 日元以后", Yn["new"])
    said("（3）一家按 330 日元结汇的进口商呢", Yn["importer"])
    a, b = Yn["old"] * Yn["sales"], Yn["new"] * Yn["sales"]
    said("（1）收入从 420 万日元降到 360 万日元，少了 60 万日元，即$60/420\\approx14.3\\%$", a, b, a - b,
         Yn["old"] - Yn["new"], Yn["old"], 100 * (a - b) / a)
    said("（2）售价要提高$420/360-1\\approx16.7\\%$", Yn["old"], Yn["new"], 1, 100 * (Yn["old"] / Yn["new"] - 1))
    d = Yn["new"] - Yn["importer"]
    said("（3）进口 1 美元的货，要多付 30 日元，成本高了$30/330\\approx9.1\\%$", 1, d, d, Yn["importer"],
         100 * d / Yn["importer"])


def others(F, Y, Q):
    y, m, d = url_date("hansard1959")
    said("1959 年 4 月 15 日，财政大臣希思科特·埃默里", y, m, d)
    assert Q["h59_speaker"] == "The Chancellor of the Exchequer (Mr. Derick Heathcoat Amory)"
    said("1941 年的财政法原定在敌对行动结束以后", F["h59_1941"][0])
    has("h59_1941", "in the words of the 1941 Finance Act")
    y46, y47, men, women = F["h59_ages"]
    said("按 1946 与 1947 年的财政法，男子到 65 岁、女子到 60 岁才能领", y46, y47, men, women)
    orig, setoff, y, repaid = F["h59_765"]
    said("最初的抵免约 7.65 亿英镑，1946 年抵了 2500 万英镑的欠税，已经还了 3.1 亿英镑", orig * 1e6, y, setoff * 1e6,
         repaid * 1e6)
    out, rate = F["h59_430"]
    said("还欠约 4.3 亿英镑，每年约还 1800 万英镑", out * 1e6, rate * 1e6)
    chk("    765 - 25 - 310 = 430", orig - setoff - repaid, out)
    fourteen, half = F["h59_unease"]
    chk("    nearly fourteen years (将近十四年)", fourteen, told("战争结束将近十四年", "将近", "年"))
    chk("    more than half (一半以上)", half, told("最初的抵免还有一半以上没有还", "还有", "以上"))
    assert out / orig > half
    chk("    two years lower (两岁)", F["h59_two"][0], told("他把领取的年龄降低两岁", "降低", "岁"))
    said("男子 63 岁，女子 58 岁", *F["h59_newages"])
    assert F["h59_newages"] == [men - F["h59_two"][0], women - F["h59_two"][0]]
    has("h59_weapon", "boom and slump")
    y, m, _ = url_date("hansard1972a")
    said("1972 年 1 月，财政部财务秘书詹金", y, m)
    assert Q["h72w_speaker"].startswith("Mr. Patrick Jenkin") and Q["h72_fs"].startswith("The Financial Secretary")
    _, y71, owed = F["h72w_137"]
    has("h72w_137", "By 31st December, 1971")
    said("1971 年末还欠 1.37 亿英镑，按抵免发出时的购买力只值 4500 万英镑", y71, owed * 1e6, F["h72w_45"][0] * 1e6)
    said("1946 年攒下 100 英镑抵免的人，到 1971 年 11 月要拿到 275 英镑才保得住购买力", F["h72w_275"][1], F["h72w_275"][0],
         F["h72w_275"][3], mon("h72w_275", "November"), F["h72w_275"][2])
    y59, interest, per = F["h72w_38"]
    said("1959 年 10 月以来加的利息，每 100 英镑只合 38 英镑", y59, mon("h72w_38", "October"), per, interest)
    y2, m2, d2 = url_date("hansard1972b")
    said("照詹金 3 月 9 日在下院的说法，财政大臣已在 1971 年 12 月 14 日宣布，从 4 月起", m2, d2, y2 - 1, 12,
         F["h72_repay"][0], 4)
    has("h72_repay", "on 14th December last", "beginning in April")
    # the Soviet Union
    d14, y47, num = F["su_title"]
    said("1947 年 12 月 14 日，苏联部长会议与联共（布）中央委员会作出决定", y47, 12, d14)
    has("su_title", "от 14 декабря 1947 г.", "О проведении денежной реформы и отмене карточек")
    has("su_signers", "И. СТАЛИН", "А. ЖДАНОВ")
    said("现金按 10 个旧卢布换 1 个新卢布兑换", *F["zv_cash"])
    a3 = F["zv_dep_a"][0]
    b10, b3, three, two = F["zv_dep_b"]
    c10, c10b, two_, one = F["zv_dep_c"]
    assert a3 == b3 and b10 == c10 == c10b
    has("zv_dep_a", "рубль за рубль")
    said("储蓄存款 3000 卢布以内的部分一卢布换一卢布，3000 到 1 万卢布的部分三换二", a3, b3, b10)
    said("1 万卢布以上的部分二换一", c10)
    assert (three, two, two_, one) == (3, 2, 2, 1)
    say("三换二", "二换一")
    pct, y48, r3, r1 = F["zv_bonds"]
    said("1947 年以前发行的大部分公债，按 3 卢布换 1 卢布，换成 1948 年发行、年息 2\\% 的转换公债", y47, r3, r1, y48, pct)
    assert "the loan of 1947 is not converted" in column("note")["zv_bonds"]
    d16, _ = F["su_ration"]
    said("从 12 月 16 日起，配给制与商业高价一并取消", 12, d16)
    has("su_ration", "отменить карточную систему", "отменить высокие цены по коммерческой торговле")
    ten, one = F["zv_cash"]
    said("可现金按 10 比 1 兑换", ten, one)
    chk("    nine tenths lost (九成)", 1 - one / ten, told("手里有现钞的人同样损失了九成", "损失了", ""))
    has("zv_capitalist", "увеличением армии безработных")
    # China
    _, y48, m8, d19 = F["ww_title"]
    said("\\begin{case}{中国 · 1948 · 金圆券}", y48)
    said("1948 年 8 月 19 日，西德改革两个月以后，中国政府改行金圆券", y48, m8, d19)
    chk("    two months after (两个月)", m8 - mon("wg_s1", "Juni"), told("西德改革两个月以后", "改革", "个月"))
    has("ww_issuer", "財政部部長王雲五")
    gold, assets, both, usd, one, issue = F["ww_reserve"]
    said("照他的说法，金圆券按 4 圆合 1 美元发行 20 亿圆，以金银外汇 2 亿美元与可靠的资产 3 亿美元作十足准备", usd, one,
         issue, gold, assets)
    chk("    (2 + 3) x 4 = 20 (亿)", (gold + assets) * usd, issue)
    assert both == gold + assets and F["fc_usd"][0] == usd                     # 美国总领事馆：gold yuan 4 to US dollar
    y35 = int(re.search(r"(\d{4}) 年 11 月 3 日，中国政府发布紧急法令，把货币白银收归国有，改行纸币",
                        chapter("ch29_depressionworld")).group(1))
    said("旧的法币是 1935 年改革以后的纸币", y35)
    one, mn = F["fc_cnc"]
    said("300 万元法币换 1 圆金圆券", mn * 1e6, one)
    has("fc_cnc", "1 to 3 million present CN dollars")
    has("fc_announce", "reconversion to gold yuan currency")
    has("fc_surrender", "surrender all gold and silver bullion and all foreign currencies")
    has("fc_strikes", "strikes be prohibited")
    d19b, _ = F["fc_freeze"]
    said("物价冻结在 8 月 19 日的水平", mon("fc_freeze", "August"), d19b)
    assert F["fc_reform"][0] == d19b == d19
    usd9, gy36 = F["ww_budget"]
    inc = F["ww_income"][0]
    gap, thirty = F["ww_gap"]
    said("全年的支出若能压到 36 亿圆，收入约 24.6 亿圆", gy36, inc)
    assert gy36 == usd9 * usd                                                  # 九亿美元之等值
    said("短缺的 11.4 亿圆约当总支出的 30\\% 弱", gap, 100 * thirty)
    chk("    36 - 24.6 = 11.4", gy36 - inc, gap, tol=1e3)
    has("fc_chiang", "Son of Generalissimo Chiang Kai-shek", "Shanghai Economic Supervisory Office")
    d13, _ = F["fc_date343"]
    said("按上海的美国总领事馆 9 月 13 日转引的英文报道", mon("fc_date343", "September"), d13)
    has("fc_speech", "North China Daily News")
    has("fc_robbing", "confiscating hoarded goods is equivalent robbing", "protect law abiding merchants")
    d15, _ = F["fc_stuart"]
    gy, times, d19c = F["fc_issue"]
    said("南京的美国大使馆 10 月 15 日报告，钞票发行约 12.5 亿圆，约为 8 月 19 日流通额的 5 倍", mon("fc_stuart", "October"),
         d15, gy * 1e9, mon("fc_issue", "August"), d19c, times)
    said("11 月 1 日，生活必需品的价格冻结取消", mon("fc_unfreeze_date", "November"), F["fc_unfreeze_date"][0])
    has("fc_unfreeze", "unfrozen")
    rate, per = F["fc_devalue"]
    has("fc_devalue", "Government yesterday announced")
    said("11 月 11 日，金圆券贬到 20 圆兑 1 美元", mon("fc_devalue_date", "November"), F["fc_devalue_date"][0] - 1, rate, per)
    d15b, _ = F["fc_col_date"]
    pct810, d19d = F["fc_col"]
    said("11 月 15 日，上海的总领事馆报告，新公布的生活费用指数比 8 月 19 日高出 810\\%", mon("fc_col_date", "November"), d15b,
         mon("fc_col", "August"), d19d, pct810)
    # the pitfall
    said("日本 1946 年的冻结", y46_of(F))
    said("1946 年度一般会计有 37.4\\% 靠公债与借款", showa(F["bj_budget"][1]), F["bj_budget"][4])
    chk("    two years later (两年后)", y48 - y46_of(F), told("两年后的中国", "", "年后"))


def y46_of(F) -> float:
    return F["mof_ordinances"][1]


def debate(F, Y, Q):
    said("西德的回升是不是从 1948 年 6 月开始的", F["wg_s1"][1], 6)
    a, b, c, d = F["ri_manz"]
    said("法国占领区的实际产量比官方数字高 6\\% 到 10\\%", a, b)
    said("联合经济区的实际产量高 10\\% 到 13\\%", c, d)
    has("ri_manz", "(Manz)", "(Abelshauser)")
    said("低估之说，Wallich 1955 年就提出过", F["ri_wallich"][0])
    said("改革以前的产量一直在缓慢上升，5 月最高", mon("ri_steady", "Mai"))
    has("ri_steady", "arbeitstäglich bereinigten")
    has("ri_noblack", "schwarze Produktion")
    has("ri_stocks", "Lagerbestände")
    has("ri_lagerabbau", "Lagerabbau", "liquider Mittel")
    has("bu_compensation", "zu den legalen Preisen abgerechnet")
    has("bu_hiding", "keineswegs notwendig")
    has("bu_miracle", "Wirtschaftswunder ausschließlich")
    said("Milward（1984）的论证是", F["de_milward"][0])
    has("de_complete", "reconstruction was largely complete")
    has("de_environment", "altering the environment in which economic policy was made")
    has("de_dismantling", "dismantling of controls", "price and exchange rate stability")
    has("de_overstated", "Milward's revisionism is overstated")
    said("一万田尚登在 1949 年 5 月就警告过", showa(24), F["bj_ichimada"][0])
    said("1950 年上半年零售物价下跌", showa(25))
    said("1950 年 6 月以后的特需结束了这段紧缩", showa(25), F["bj_korea"][0])


def deeper(F, Y, Q):
    src = meta()["sources"]
    notes = meta()["notes"]
    for key in ("waehrungsgesetz1948", "umstellungsgesetz1948", "festkontogesetz1948", "bdlgesetz1948"):
        assert "verfassungen.de" in src[key]["version"] and "ISO-8859-1" in src[key]["version"], key
    assert "encoded in ISO-8859-1 and read as UTF-8" in notes
    said("网站用 ISO-8859-1 编码，核对脚本按 UTF-8 读取", 8859, 1, 8)
    d15, y47, n247 = F["zv_title"]
    said("《东方曙光报》1947 年 12 月 15 日第 247 号第 1 版", y47, 12, d15, n247, page("zv_title"))
    assert "декабря" in transcription("zv_title") and "National Parliamentary Library of Georgia" in meta()["license"]
    said("并以 2025 年《库塔芬大学学报》", Y["su_section"])
    assert "2025" in src["ussr1947msal"]["version"]
    said("日本银行百年史第 5 卷没有文字层", 5)
    assert "published 1982-86" in src["boj1985a"]["version"] and "vol. 5, second part" in src["boj1985a"]["version"]
    assert "(no text layer)" in src["boj1985a"]["version"]
    chk("    four disagreements (四处不一致)", 4, told("\\textbf{四处不一致。}", "{", "处"))
    d20, y = F["ug_title"]
    d27, m6, _ = F["bu_ug_date"]
    said("《换算法》的日期，verfassungen.de 印作 1948 年 6 月 20 日，Buchheim 写作 6 月 27 日", y, mon("ug_title", "Juni"), d20,
         m6, d27)
    assert d27 == F["wg_date"][0] + 7                                          # 一周以后
    said("朝鲜战争的爆发，财务省的政策史写作 1950 年 7 月，日本银行百年史写作 6 月 25 日", F["mof_korea"][0],
         mon("mof_korea", "July"), *F["bj_korea"])
    _, total, free, frozen, special = F["mof_table46"]
    t1, t9 = (int(x) for x in re.search(r"Table (\d+)-(\d+)", Q["mof_table_head"]).groups())
    said("1946 年 3 月末的存款，政策史的正文说自由账户是 1357.5 亿日元，同一页的表 1-9 却把这个数列为合计，自由账户只有 145.2 亿日元",
         1946, 3, F["mof_frozen46"][2] * 1e6, t1, t9, free * 1e6)
    has("mof_frozen46", "as compared to ¥ 135,751 million in free accounts")
    assert F["mof_frozen46"][2] == total and page("mof_frozen46") == page("mof_table46")
    said("与合计只差 1 百万日元", total - (free + frozen + special))
    _, gy36 = F["ww_budget"]
    gap, thirty = F["ww_gap"]
    said("王云五说短缺的 11.4 亿圆约当总支出的 30\\% 弱，按他自己的 36 亿圆算是 32\\%", gap, 100 * thirty, gy36,
         100 * gap / gy36)
    assert gap / gy36 > thirty                                                 # '30% 弱' 是不到 30%
    said("1948 年 5 月汉堡的黑市价格与工资", F["bu_bread"][0], mon("bu_bread", "Mai"))
    assert "Mendershausen" in notes
    said("Manz、Abelshauser 1975 年的估计", F["ri_refs"][-1])
    has("ri_refs", "W.Abelshauser, Wirtschaft in Westdeutschland 1945-1948, Stuttgart 1975")
    said("道奇 3 月 7 日的声明", *F["bj_march7"])
    said("艾哈德是 6 月 25 日命令的发布者", mon("bu_june25", "Juni"), F["bu_june25"][0])
    said("蒋经国 9 月的演说", mon("fc_date343", "September"))
    said("Abelshauser 注 74 的演说标题", F["ab_erhard"][0])
    assert Q["ab_erhard"].startswith("74 L. Erhard")
    said("日本 1946 年的钞票、预算与 1949 年度的预算只据日本银行百年史", y46_of(F), showa(F["bj_surplus"][0]))
    said("日本银行券 1946 年 3 月末的数 23,322 百万日元", 1946, 3, F["bj_endmarch"][0])
    assert F["bj_endmarch"][0] == F["mof_notes"][2] and "the end of March" in Q["mof_notes"]
    has("bj_endmarch", "昭和21年3月末")
    said("日本银行 1949—1950 年的放款", F["mof_bojlending"][4], F["mof_bojlending"][6])
    said("道奇“踩高跷”的说法（1949 年 3 月）", showa(24), F["bj_march7"][0])
    said("Wallich（1955）、Milward（1984）、Abelshauser（1975）与 Manz（1968）的著作", F["ri_wallich"][0], F["de_milward"][0],
         F["ri_refs"][-1], F["ri_refs"][2])
    for words in ("'stilts'", "Wallich (1955)", "Milward (1984)", "Abelshauser (1975)", "Manz's thesis",
                  "cigarette money", "Berlin blockade", "Jenkin's dates"):
        assert words in notes, words


def legacy(F, Y, Q):
    said("1949 年的稳定从预算的盈余开始", F["mof_dodgeplan"][0])
    said("到 1949 年，德国马克与日元都有了对美元的固定汇率", F["mof_360"][2])


def takeaways(F, Y, Q):
    R = rules()
    said("1948 年 6 月，西德先换货币，人头额 60 德国马克，存款与债务大体按 10 比 1 换算", F["wg_s1"][1], 6, R["head"],
         *F["ug_s2"])
    said("较大的存款最终按 100 比 6.5 换算，工资与租金按 1 比 1", *F["bu_65"], *F["ug_s18"])
    U = unemployment()
    said("1948 年下半年物价上涨，抗议不断；1949 年底失业人数到了 156 万", F["wg_s1"][1], 1949, U["1949-12"] * 1e3)
    y0, y1, total = F["de_amounts"][:3]
    said("马歇尔计划 1948—1951 年提供了 132 亿美元，不到受援国国民收入的 3\\%", y0, y1, total * 1e9, F["de_share"][0])
    said("1949 年道奇计划带来预算的盈余与 360 日元的单一汇率", F["mof_dodgeplan"][0], F["mof_360"][0])
    said("英国到 1972 年 4 月才开始把余下的战后抵免全部偿还，它的购买力已被通胀吃掉大半", url_date("hansard1972b")[0], 4)
    has("h72_repay", "all outstanding post-war credits would be repaid beginning in April")
    assert F["h72w_45"][0] / F["h72w_137"][2] < 0.5                           # 大半: £45m of £137m
    said("苏联把现金按 10 比 1 换算", *F["zv_cash"])
    said("中国 1948 年的金圆券冻结物价而不平衡预算", F["ww_title"][1])


def selfcheck(F, Y, Q):
    O = OVERHANG
    said("若$k=0.45$，其余不变", O["k_sc"])
    said("冻结存款为什么没有止住日本 1946 年的通胀", y46_of(F))
    a = overhang(O["M"], O["k_sc"], O["Y"], O["Pbar"])
    said("愿意持有的货币是$0.45\\times100=45$，过剩货币$90-45=45$；放开价格以后$P=90/45=2$", O["k_sc"], O["Y"], a["desired"],
         O["M"], a["desired"], a["excess"], O["M"], a["desired"], a["P"])
    said("到 1948 年 6 月只剩 298.4 亿日元", F["mof_frozen48"][0], 6, F["mof_frozen48"][1] * 1e6)
    said("1946 年度的预算有 37.4\\% 靠公债与借款", showa(F["bj_budget"][1]), F["bj_budget"][4])
    gy36, inc = F["ww_budget"][1], F["ww_income"][0]
    chk("    about seven tenths (约七成)", inc / gy36, told("王云五自己算出全年收入只有支出的约七成", "约", ""), tol=0.05)
    gy, times, d19 = F["fc_issue"]
    rate, per = F["fc_devalue"]
    said("发行限额是 20 亿圆，到 10 月中已发行约 12.5 亿圆，为 8 月 19 日的 5 倍；11 月物价冻结取消，金圆券贬到 20 圆兑 1 美元",
         F["ww_limit"][0], mon("fc_stuart", "October"), gy * 1e9, 8, d19, times, mon("fc_unfreeze_date", "November"),
         rate, per)
    assert F["ww_limit"][0] == F["ww_reserve"][5]


def ending(F, Y, Q):
    said("1948 年 6 月 20 日换到手的 40 德国马克", F["wg_s1"][1], 6, F["bu_sunday"][0], F["wg_s6b"][0])
    said("改革以前帝国马克的折算率已定为 30 美分", F["bu_30cents"][0])
    has("bu_30cents", "für die D-Mark zunächst beibehalten")
    chk("    a year later (一年以后)", F["mof_360"][2] - F["wg_s1"][1], told("一年以后，日元也定在了", "", "年以后"))
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 36's question"
    assert t.index("\\end{answers}") < t.index("1948 年 6 月 20 日换到手的 40 德国马克")
    ch36 = (ROOT / "zh" / "ch36_brettonwoods.tex").read_text(encoding="utf-8")
    assert f"\\guidequestion{{{NEXT}}}" in ch36 or "\\chapterstub" in ch36, "Chapter 36's question"


def models() -> None:
    """The key equation, and its arithmetic checked with numbers."""
    rng = np.random.default_rng(35)
    for _ in range(30):
        M, k, Y, Pb = rng.uniform(10, 500), rng.uniform(0.05, 1.5), rng.uniform(20, 400), rng.uniform(0.2, 5)
        o = overhang(M, k, Y, Pb)
        # eq:reconstruction-overhang: the overhang, the free price and the rise
        chk("    overhang = M - k Pbar Y", o["excess"], M - k * Pb * Y, tol=1e-9)
        chk("    at P = M/(kY) people hold all of M", k * o["P"] * Y, M, tol=1e-9, rel=1e-12)
        chk("    P/Pbar = M/(k Pbar Y)", o["P"] / Pb, M / (k * Pb * Y), tol=1e-9, rel=1e-12)
        # a conversion at the ratio of the money to the money people wish to hold leaves the price where it was
        ratio = M / (k * Pb * Y)
        chk("    conversion at M/(k Pbar Y): P = Pbar", overhang(M, k, Y, Pb, ratio)["P"], Pb, tol=1e-9, rel=1e-12)
        # more output, less rise; no overhang, no rise
        assert overhang(M, k, 2 * Y, Pb)["P"] < o["P"]
        assert abs(overhang(k * Pb * Y, k, Y, Pb)["rise"] - 1) < 1e-12
        # the conversion of a household: never more than the money it had, at most 1 : 1 for the notes
        cash, dep, n = rng.uniform(0, 2000), rng.uniform(0, 50000), int(rng.integers(1, 7))
        c = convert(cash, dep, n)
        assert 0 <= c["total"] <= cash + dep and c["kopf"] <= cash
        chk("    cancel + freed + invest = frozen", c["cancel"] + c["freed"] + c["invest"], c["frozen"], tol=1e-9)
    R = rules()
    # Buchheim's 100 : 6.5 for larger balances: a tenth, half free, of the frozen half three tenths kept
    chk("    100 x 1/10 x (1/2 + 1/2 x 3/10) = 6.5", 100 * R["rate"] * (R["free_half"] + R["free_half"] *
                                                                          (R["freed"] + R["invest"])),
        facts()["bu_65"][1], tol=1e-9)
    t = TEX.read_text(encoding="utf-8")
    eqs = {lab: body.strip() for body, lab in re.findall(r"\\begin\{keyeq\}\n(.*?)\\label\{(eq:[^}]+)\}", t,
                                                         re.DOTALL)}
    assert sorted(eqs) == ["eq:reconstruction-overhang"], sorted(eqs)
    assert eqs["eq:reconstruction-overhang"] == ("\\text{过剩货币}=M-k\\bar PY,\\qquad \\text{放开价格以后}\\;P=\\frac{M}{kY},"
                                                 "\\qquad \\frac{P}{\\bar P}=\\frac{M}{k\\bar PY}."), eqs
    # k is the inverse of the velocity of the equation of exchange (Chapter 19)
    ch19 = chapter("ch19_bullion")
    assert "交易方程" in ch19 and "$V$ 是流通速度" in ch19


def figures_data() -> None:
    """What the figures assert of their data."""
    I, Fz, U = ipb(), ipf(), unemployment()
    assert I.between(25, 95).all() and Fz.between(30, 90).all() and U.between(400, 2000).all()
    assert I["1948-12"] > I["1948-06"] and U.idxmax() == "1950-02"
    W = wpi()
    assert W.index[0] == "1944-01" and W.is_monotonic_increasing is False and W.max() < 400
    A = marshall_aid()
    assert all(v > 0 for v in A.values()) and A["其他"] > A["英国"]


def wpi_check(F) -> None:
    """The Bank of Japan's series against the Ministry of Finance's '55.1 fold' of 1944-1948 (annual averages)."""
    W = wpi()
    r = W[W.index.str.startswith("1948")].mean() / W[W.index.str.startswith("1944")].mean()
    chk("    WPI 1948/1944, annual averages (MOF: 55.1 fold)", r, F["mof_20fold"][3], tol=0.2)


# ---------------------------------------------------------------------------------------------------
# 5. The book
# the life dates from rows of the snapshot: words -> (row, index of the birth year, index of the death year)
ROW_LIVES = {"George C. Marshall，1880—1959": ("loc_marshall", 0, 1),
             "Lucius D. Clay，1897—1978": ("loc_clay", 0, 1),
             "Joseph M. Dodge，1890—1964": ("loc_dodge", 0, 1),
             "Gerhard Colm，1897—1968": ("loc_colm", 0, 1),
             "Raymond W. Goldsmith，1904—1988": ("loc_goldsmith", 0, 1),
             "Edward A. Tenenbaum，1921—1975": ("loc_tenenbaum", 0, 1),
             "Wilhelm Röpke，1899—1966": ("loc_ropke", 0, 1),
             "Harry S. Truman，1884—1972": ("loc_truman", 0, 1),
             "Carl S. Shoup，1902—2000": ("loc_shoup", 0, 1),
             "William J. Sebald，1901—1980": ("loc_sebald", 0, 1),
             "Joseph Stalin，1878—1953": ("loc_stalin", 0, 1),
             "Andrei Zhdanov，1896—1948": ("loc_zhdanov", 0, 1),
             "王云五（1888—1979）": ("loc_wang", 0, 1),
             "蒋经国（1910—1988）": ("loc_chiang", 0, 1),
             "石桥湛山（1884—1973）": ("loc_ishibashi", 0, 1),
             "一万田尚登（1893—1984）": ("loc_ichimada", 0, 1),
             "Ludwig Erhard，1897—1977": ("gnd_erhard_born", 0, None),
             "Derick Heathcoat Amory，1899—1981": ("gnd_amory_born", 0, None)}
DEATHS = {"gnd_erhard_born": "gnd_erhard_died", "gnd_amory_born": "gnd_amory_died"}
# the beginning of each record's heading
HEADS = {"loc_marshall": "Marshall, George C.", "loc_clay": "Clay, Lucius D.", "loc_dodge": "Dodge, Joseph M.",
         "loc_colm": "Colm, Gerhard", "loc_goldsmith": "Goldsmith, Raymond W.", "loc_tenenbaum": "Tenenbaum, Edward A.",
         "loc_ropke": "Röpke, Wilhelm", "loc_truman": "Truman, Harry S.", "loc_shoup": "Shoup, Carl S.",
         "loc_sebald": "Sebald, William J.", "loc_stalin": "Stalin, Joseph", "loc_zhdanov": "Zhdanov, Andreĭ",
         "loc_wang": "Wang, Yunwu", "loc_chiang": "Chiang, Ching-kuo", "loc_ishibashi": "Ishibashi, Tanzan",
         "loc_ichimada": "Ichimada, Hisato", "gnd_erhard_born": "1897-02-04", "gnd_amory_born": "1899"}
# what other chapters tell: (words of this chapter, chapter where it is told, words there)
EVENTS = [("被换掉的帝国马克，是 1924 年以来德国的货币单位（\\chref{ch:weimar}）", "ch26_weimar",
           "1924 年 8 月 30 日，配合道威斯计划生效，德国以帝国马克为新的本位货币"),
          ("\\chref{ch:weimar}讲过，那时一万亿纸马克合一个战前的金马克", "ch26_weimar",
           "从这天起，一万亿纸马克合一个战前的金马克"),
          ("地租马克发行的同一天，帝国银行停止贴现国库券", "ch26_weimar",
           "三天以后，地租马克开始发行，柏林的发行点前排起了队\\cite{bundesarchiv1923}。同一天，帝国银行停止贴现国库券"),
          ("这套机制\\secref{sec:alternatives-repressed}讲过", "ch30_alternatives", "\\label{sec:alternatives-repressed}"),
          ("$k$相当于\\chref{ch:bullion}交易方程里流通速度的倒数", "ch19_bullion", "$V$ 是流通速度"),
          ("\\chref{ch:warfinance}讲过，战后抵免在战争期间动用不了", "ch34_warfinance", "战后抵免在战争期间动用不了"),
          ("旧的法币是 1935 年改革以后的纸币（\\secref{sec:depressionworld-silver}）", "ch29_depressionworld",
           "1935 年 11 月 3 日，中国政府发布紧急法令，把货币白银收归国有，改行纸币")]
# the chapters this one hands on to
LATER = {"ch:brettonwoods": "ch36_brettonwoods", "ch:eastasia": "ch42_eastasia", "ch:planned": "ch43_planned",
         "ch:budget": "ch50_budget", "ch:hyperinflation": "ch52_hyperinflation", "ch:transition": "ch59_transition"}


def book(F, Q):
    """Life dates and what other chapters tell."""
    t = tex_text()
    for words, (rid, i, j) in ROW_LIVES.items():
        assert words in t, words
        died = F[rid][j] if j is not None else F[DEATHS[rid]][0]
        assert f"{F[rid][i]:.0f}—{died:.0f}" in words, (words, rid)
        assert Q[rid].startswith(HEADS[rid]), (rid, Q[rid])                      # the person of the record
        COVERED.append(words)
    assert Q["gnd_erhard"] == "Erhard, Ludwig" and Q["gnd_amory"] == "Amory, Derick Heathcoat"
    assert "dateOfBirth" in column("juan")["gnd_erhard_born"] and "dateOfDeath" in column("juan")["gnd_amory_died"]
    assert "by his name and dates" in column("note")["gnd_amory_born"]
    assert "Patrick Jenkin，生卒年未详" in t and "詹金在两处规范档里都没有找到" in t
    for here, ch, there in EVENTS:
        assert here in t, here
        assert there in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (ch, there)
    for label, ch in LATER.items():
        assert f"{{{label}}}" in t, label
        assert f"\\label{{{label}}}" in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (label, ch)
    print(f"ok {len(ROW_LIVES)} life dates, {len(EVENTS)} statements of other chapters, {len(LATER)} later chapters")


def witnesses(F, Q):
    """Second witnesses of statements of the text, the licences and the bibliography block of the chapter."""
    # the notes of the Bank of Japan: its history's table and the Ministry of Finance
    assert F["bj_endmarch"][0] == F["mof_notes"][2]
    # Table 1-9: the columns add up to the total within the rounding of a million yen; the prose of p. 31
    _, total, free, frozen, special = F["mof_table46"]
    assert abs(total - (free + frozen + special)) <= 1
    _, total48, free48, frozen48 = F["mof_table48"]
    assert abs(total48 - (free48 + frozen48)) <= 1 and F["mof_frozen48"][1:] == [frozen48, free48]
    assert F["mof_frozen46"][0] == frozen
    # the single rate: the Ministry and the Bank's chronology; the date of the ordinances
    assert F["bjc_360"][1] == F["mof_360"][0] == 360
    # Buchheim's three dates of the laws (20 June; the Umstellungsgesetz a week later; 4 October)
    assert F["bu_westberlin"][0] == F["bu_sunday"][0] == F["wg_date"][0]
    # the first plans: CDG 10 : 1 and the principles of Rothwesten (10% into new money) are the law's 10 : 1
    assert F["bu_cdg_terms"] == F["ug_s2"] and F["bu_principles"][2] / 100 == rules()["rate"]
    # Wang's statement and the consulate general: 4 gold yuan to the dollar, 19 August
    assert F["fc_usd"][0] == F["ww_reserve"][3] and F["fc_freeze"][0] == F["ww_title"][3]
    # the Soviet decision: dated 14 December, printed on the 15th
    assert F["zv_title"][0] == F["su_title"][0] + 1 and F["zv_title"][1] == F["su_title"][1]
    # the industrial production of 1950: the Bank's table against its text (24.7 per cent)
    lo, hi = F["bj_ipindex"]
    chk("    the index of SCAP 116.7/93.6 - 1 (24.7%)", 100 * (hi / lo - 1), F["bj_mining"][1], tol=0.05)
    # the Ministry's '55.1 fold' against the Bank of Japan's own index
    wpi_check(F)
    # the post-war credits: 765 - 25 - 310 = 430 in 1959; less outstanding in 1971
    assert F["h72w_137"][2] < F["h59_430"][0]
    # the licences
    m = meta()
    lic = m["license"]
    for rid in ("bu_copyright", "ri_copyright", "ab_copyright", "bbk_terms", "bbk_unaltered", "mof_terms",
                "mof_copyright", "bojcr_terms", "ww_pd", "h_copyright", "gnd_licence"):
        assert Q[rid] in lic and re.search(r"\(rows? [^)]*\b" + rid + r"\b", lic), rid
    for words in ("Contains Parliamentary information licensed under the Open Parliament Licence v3.0.",
                  "short phrases only", "public domain", "amtliche Werke", "the PDF prints no copyright notice",
                  "public data", "credit: Bank of Japan", "short quotations only", "official act of state"):
        assert words in lic, words
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    start = bib.index("% ---- 第 35 章")
    following = re.search(r"^% ---- 第 \d+ 章", bib[start + 1:], re.MULTILINE)
    end = start + 1 + following.start() if following else bib.index("\\end{thebibliography}")
    block = bib[start:end]
    assert "data/fetch/reconstruction35.py" in block and "data/fetch/boj_wpi35.py" in block
    items = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", block)}
    allitems = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", bib)}
    hansard = "“Contains Parliamentary information licensed under the Open Parliament Licence v3.0.”"
    for key in ("hansard1959", "hansard1972a", "hansard1972b"):
        assert hansard in items[key], key
    for key in ("buchheim1988", "ritschl1985", "abelshauser1981"):
        assert Q["bu_copyright"] in items[key] and "只引短语，其余转述" in items[key], key
    assert "只引短语" in items["delong1991"] and "没有印版权说明" in items["delong1991"]
    for key in ("waehrungsgesetz1948", "umstellungsgesetz1948", "festkontogesetz1948", "bdlgesetz1948"):
        assert "官方作品" in items[key] and "§5" in items[key], key
    assert Q["bbk_terms"].replace("\"", "”") in items["bdl1950"].replace("\"", "”") or Q["bbk_terms"] in items["bdl1950"]
    assert Q["bbk_unaltered"] in items["bdl1950"]
    for key in ("marshall1947", "eca1948", "frus1948jp", "frus1948cn", "frus1949jp"):
        assert "公有领域" in items[key], key
    assert Q["mof_terms"] in items["mof2010"] and Q["mof_copyright"] in items["mof2010"]
    for key in ("boj1985", "bojwpi"):
        assert Q["bojcr_terms"] in items[key] and "来源：日本银行" in items[key], key
    assert "只引短句" in items["boj1985"] and Q["bojcr_terms"] in allitems["bojchron"]
    assert "官方文件" in items["ussr1947"] and Q["ww_pd"] in items["wang1948"]
    assert Q["gnd_licence"] in items["gnd35"] and "公共数据" in items["loc35"]
    for rid, _, _ in ROW_LIVES.values():
        if rid.startswith("loc_"):
            assert Q[rid].replace("-", "--") in items["loc35"], rid
    # every source of the snapshot is named by its URL in its item (the page images with the text they belong to)
    item_of = {"ritschl1985img": "ritschl1985", "bdl1950img": "bdl1950", "bbkterms35": "bdl1950",
               "frus1948v06_d696": "frus1948jp", "frus1949v07p2_d67": "frus1949jp", "frus1949v07p2_d161": "frus1949jp",
               "mof2010ch1": "mof2010", "mof2010ch2": "mof2010", "mofterms35": "mof2010", "boj1985a": "boj1985",
               "boj1985b": "boj1985", "boj1985c": "boj1985", "boj1985d": "boj1985", "bojcr30": "boj1985",
               "bojchron35": "bojchron", "ussr1947zv": "ussr1947", "ussr1947msal": "ussr1947",
               "gnd_erhard35": "gnd35", "gnd_amory35": "gnd35"}
    for key, s in m["sources"].items():
        if key.startswith("frus1948v08"):
            item = "frus1948cn"
        elif key.startswith("loc_"):
            item = "loc35"
        else:
            item = item_of.get(key, key)
        assert s["url"] in allitems[item].replace("\\%", "%").replace("\\_", "_"), key
    assert load_snapshot("boj_prewar_wpi_1944_1952")[1]["url"] in items["bojwpi"], "bojwpi"
    keys = set(allitems)
    cited = {k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", tex_text()) for k in c.split(",")}
    assert cited <= keys, sorted(cited - keys)
    assert set(items) <= cited, sorted(set(items) - cited)
    srcs = set(m["sources"])
    for key in items:                                                              # every work of the block is a source
        assert key in srcs or key in item_of.values() or key in ("frus1948cn", "loc35", "bojwpi"), key
    print(f"ok {len(cited)} works cited, {len(items)} of them in the bibliography block of Chapter 35")


NAMES = ("Buchheim|Ritschl|Abelshauser|De Long|Eichengreen|Milward|Manz|Wallich|Uzan|Mendershausen")


def counts() -> None:
    """The editor's limits: “不能” at most about a dozen; no cited modern author as the subject of a sentence outside
    the 史料说明; the forbidden words; the human cost stated."""
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
    # the human cost (savers, expellees, the unemployed, the blockade, the dismissals) and the repressed inflation of
    # Chapter 30
    for words in ("失业", "封锁", "储户", "被驱逐者", "裁员", "损失了九成"):
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
    overhang_section(F, Y, Q)
    germany(F, Y, Q)
    cost(F, Y, Q)
    marshall(F, Y, Q)
    japan(F, Y, Q)
    others(F, Y, Q)
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
