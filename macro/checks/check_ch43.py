"""Chapter 43 (成熟的计划经济：苏联、东欧、毛泽东时期的中国与南斯拉夫): every number and every quotation in
zh/ch43_planned.tex.

    python3 checks/check_ch43.py

Inputs:
  planned_facts                 quotations of the chapter's sources with their page: the appeal of the CC of the CPSU
                                and the USSR Council of Ministers in Заря Востока of 1 June 1962 and the resolution of
                                the plenum of 29 September 1965 in its issue of 1 October 1965 (read on the page
                                images: the text layer splits the words); the report of the Leningrad city committee of
                                1 June 1962 (istmat.org, with the archive scan); FRUS 1947 vol. IV doc. 436 and FRUS
                                1969-1976 vol. XXIX docs. 142 and 145; the CPC resolution of 27 June 1981; table A-1
                                of 新中国五十年统计资料汇编 (1999; a third-party scan, read to verify only) and table
                                4-2 of 中国统计年鉴 2000 with the terms of stats.gov.cn; Meng, Qian and Yared (2010),
                                NBER Working Paper 16361, with its table A8 (Li and Yang 2005); Smil (1999), BMJ;
                                Kornai (1980) vol. A and Kornai (1986), Kyklos (scans without a text layer: read on the
                                page images); Kornai, Maskin and Roland (2003), JEL; the World Bank's report 1615a-YU
                                (1978) and Yusuf (1977), with their landing pages; the authority records of the
                                Library of Congress and the GND. data/fetch/verify_web_quotes.py checks the quotations
                                against the documents; the rows with an empty quotation are read on page images, with a
                                transcription between « and » in the note; data/fetch/planned43.py fetches them
  zh/ch30, ch31, ch35, ch40, ch42    the statements of earlier chapters that this chapter repeats (EVENTS); the stubs
                                of Chapters 44, 52, 59, 72 and 81 for what is handed on (LATER)

This script

1. reads the numbers of every row from its quotation (or from the transcription of a page image) by the rules of
   READINGS and compares them with the value column; the misreadings of the text layers are listed in MISPRINTS;
2. finds every “…” of the text among the renderings of TRANSLATIONS, and the words of the source each one renders
   (KEYWORDS) in the row; the quotations of modern scholars stay short;
3. checks each number of the text with said(): the phrase is in the text and each number is the value of a row, a
   teaching input, or arithmetic on them (the overhang of eq:reconstruction-overhang, the refinancing conditions of
   eq:planned-sbc, the fixed quotas of eq:planned-quota, the Illyrian firm of eq:planned-illyria, the excess deaths
   computed from table A-1); every Arabic number of the text must lie in a phrase said() read (coverage());
4. checks the key equations as printed, the claims made of them on random numbers, the data of the figures
   (figsrc/fig_ch43.py imports vital() and grain() from here), the life dates against the authority records, what
   other chapters tell, the licences and the bibliography block of Chapter 43;
5. lists the rows no "% 据:" anchor of the text names (common.anchors).

Set CH43_TEX to a scratch copy of the chapter to run the checks on it (mutation tests).
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

TEX = Path(os.environ.get("CH43_TEX", ROOT / "zh" / "ch43_planned.tex"))   # a scratch copy for mutation tests
GUIDE = "计划经济里的“通胀”藏在哪里？"
PREV = GUIDE                                        # Chapter 42's NEXT
NEXT = "菲利普斯“菜单”为什么会漂移？"                    # Chapter 44's question (its stub)
FETCH = "data/fetch/planned43.py"
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
    df, m = load_snapshot("planned_facts", dtype=str, keep_default_na=False)
    assert 43 in m["used_in"] and m["fetch"] == FETCH
    assert df["id"].is_unique
    return df


@lru_cache(maxsize=None)
def meta() -> dict:
    return load_snapshot("planned_facts")[1]


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


def page(rid: str) -> int:
    """The first printed page number of a row's juan column: 'p. 155 (PDF p. 159)' -> 155."""
    return int(re.search(r"pp?\. (\d+)", column("juan")[rid]).group(1))


def pdfpage(rid: str) -> int:
    return int(re.search(r"PDF pp?\. (\d+)", column("juan")[rid]).group(1))


def chapter(name: str) -> str:
    """Another chapter's text without its comment lines."""
    t = (ROOT / "zh" / f"{name}.tex").read_text(encoding="utf-8")
    return "\n".join(l for l in t.splitlines() if not l.lstrip().startswith("%"))


# ---------------------------------------------------------------------------------------------------
# 1. Readings of the numbers (the same rules wrote the value column when the snapshot was built)
SMALL = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "seventeen": 17}
TENS = {"twenty": 20, "thirty": 30, "forty": 40}
WORDS = {"Half": 0.5, "third": 1 / 3}


def cardinal(s: str) -> float:
    """An English cardinal: 'three', 'seventeen', 'thirty'."""
    return float(sum(SMALL.get(w, 0) + TENS.get(w, 0) for w in s.lower().replace("-", " ").split()))


def figure(s: str) -> float:
    """'1,000', '30.5', '.28', '-0.15' and full-width digits."""
    return float(unicodedata.normalize("NFKC", s).replace(",", "").replace("−", "-"))


ZH_DIGITS = {"〇": 0, "零": 0, "一": 1, "两": 2, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
ZH_UNITS = {"十": 10, "百": 100, "千": 1000, "万": 10 ** 4, "亿": 10 ** 8}


def zh(s: str) -> float:
    """A Chinese numeral: '六', '十四', '二十七', '七千', '三分之一', '八成', '一成半', '一半', '三倍'."""
    if "分之" in s:
        b, a = s.split("分之")
        return zh(a) / zh(b)
    if s.endswith("成半"):
        return (zh(s[:-2]) + 0.5) / 10
    if s.endswith("成"):
        return zh(s[:-1]) / 10
    if s.endswith("半"):
        return 0.5 * (zh(s[:-1]) if s[:-1] else 1)
    s = s.rstrip("多倍")
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


def zh_year(s: str) -> float:
    """A year written digit by digit: '一九五三' -> 1953, '一九六〇' -> 1960."""
    return float("".join(str(ZH_DIGITS[c]) for c in s))


def zh_decimal(s: str) -> float:
    """'十九点六' -> 19.6, '四点八' -> 4.8."""
    a, b = s.split("点")
    return float(f"{int(zh(a))}.{''.join(str(ZH_DIGITS[c]) for c in b)}")


def typewriter(s: str) -> float:
    """The Leningrad typewriter's capital I for the digit 1: 'I' -> 1, 'I7' -> 17, '3I' -> 31."""
    return float(s.replace("I", "1"))


def semicolon(s: str) -> float:
    """The World Bank scan's ';964' for '1964' (checked on the page image)."""
    return float("1" + s.lstrip(";"))


# a figure with its sign: a minus that follows no letter, digit or bracket
FIGURES = re.compile(r"((?<![\w)])[-−])?(\d[\d,]*(?:\.\d+)?|\.\d+)")
HOW = {"num": figure, "en": cardinal, "word": lambda w: WORDS[w], "zh": zh, "zhyear": zh_year, "zhdec": zh_decimal,
       "typewriter": typewriter, "semicolon": semicolon}
# the rows whose decimal comma is read as a point (the Russian newspaper): '91,6' -> 91.6
DECIMAL_COMMA = "zv62_"
# the rows of table A-1 whose layout text spaces the decimals: '20. 86' -> 20.86
SPACED = "nbs_1"
# id -> [(phrase, how)], in order. A phrase 'context|word' is searched as a whole and read from `word`. Rows not
# listed are read with all the figures of the quotation (a page image: of the transcription), with their signs. An
# empty list: the row prints no number of the story (titles, licences, a garbled title).
EMPTY = "lk_licence nbst_data gnd_licence wb78_title".split()
READINGS: dict[str, list[tuple[str, str]]] = {rid: [] for rid in EMPTY}
READINGS.update({
    "lk_date": [("No75 |I", "typewriter"), ("июня |1962", "num")],
    "lk_dates": [("принято |I7", "typewriter"), ("лишь |3I", "typewriter")],
    "lk_scan_dates": [("принято |I7", "typewriter"), ("лишь |3I", "typewriter")],
    "fr70_scapegoats": [("and |four", "en")],
    "res_date": [("|一九八一", "zhyear"), ("年|六", "zh"), ("月|二十七", "zh"), ("第|十一", "zh"), ("委员会第|六", "zh")],
    "res_ffyp": [("从|一九五三", "zhyear"), ("到|一九五六", "zhyear"), ("百分之|十九点六", "zhdec"),
                 ("百分之|四点八", "zhdec")],
    "res_line": [("|一九五八", "zhyear")],
    "res_lushan_early": [("从|一九五八", "zhyear"), ("到|一九五九", "zhyear"), ("年|七", "zh")],
    "res_verdict": [("在|一九五九", "zhyear"), ("到|一九六一", "zhyear")],
    "res_winter": [("|一九六〇", "zhyear")],
    "res_7000": [("|一九六二", "zhyear"), ("年|一", "zh"), ("有|七千", "zh")],
    "res_recovery": [("从|一九六二", "zhyear"), ("到|一九六六", "zhyear")],
    "mqy_range": [("between |seventeen", "en"), ("and |thirty", "en")],
    "mqy_phases": [("in |three", "en"), ("in |1952", "num"), ("of |six", "en"), ("to |nine", "en")],
    "mqy_children": [("|Half", "word"), ("under |ten", "en")],
    "mqy_three": [("almost |three", "en")],
    "smil_spring2": [("of |1959", "num"), ("in a |third", "word")],
    "smil_three": [("nearly |three", "en")],
    "smil_germany": [("spent |two", "en")],
    "k80_names": [("introduced |two", "en")],
    "wb78_invest": [("first |two", "en"), ("than |30", "num")],
    "wb78_1965": [("of |1963", "num"), ("of |1965", "num"), ("between |;964", "semicolon"), ("and |1967", "num")],
    "yu_series": [("NO. |44", "num")],
})


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


def read_text(rid: str, text: str) -> list[float]:
    """The numbers of a quotation or of the transcription of a page image, by READINGS or by its figures."""
    if rid in READINGS:
        return read_rule(rid, text)
    text = unicodedata.normalize("NFKC", text)
    if rid.startswith(DECIMAL_COMMA):
        text = re.sub(r"(\d),(\d)", r"\1.\2", text)
    if rid.startswith(SPACED):
        text = re.sub(r"(\d)\. (\d)", r"\1.\2", text)
    return [(-1 if sign else 1) * figure(n.rstrip(",")) for sign, n in FIGURES.findall(text)]


# the misreadings of the text layers and the misprints, each printed in the quotation and named in the snapshot's
# notes with its row: (row, as printed in the quotation, the words of the notes that name it)
MISPRINTS = [("lk_number", "ПАТИЙНЫХ", "'ПАТИЙНЫХ' for 'ПАРТИЙНЫХ'"),
             ("lk_addressee", "Г.И,", "'Г.И,' for 'Г.И.'"),
             ("lk_date", "No75 I июня", "the typewriter's capital 'I' for the digit '1'"),
             ("lk_dates", "I7 мая", "the typewriter's capital 'I' for the digit '1'"),
             ("zv62_title", "иСовета", "'иСовета' for 'и Совета'"),
             ("zv62_output", "миллионов'800", "'миллионов'800' for 'миллионов 800'"),
             ("fr47_single", "rail products", "'rail' for 'retail'"),
             ("fr47_sacrifice", "geater", "'geater' for 'greater'"),
             ("mqy_weather", "bad can weather", "'bad can weather' for 'bad weather'"),
             ("nbs_1960", "20. 86", "'20. 86' for '20.86'"),
             ("wb78_title", "Challen1rs of Develonment", "'Challen1rs of Develonment' for 'Challenges of Development'"),
             ("wb78_restricted", "may hb used", "'hb' for 'be'"),
             ("wb78_purpose", "thpir", "'thpir' for 'their'"),
             ("wb78_state", "noliries, ramainpd", "'noliries, ramainpd' for 'policies, remained'"),
             ("wb78_1965", "between ;964", "'Tne' and ';964' for 'The' and '1964'"),
             ("yu_series", "FNANCE STUDI2S", "'FNANCE STUDI2S' for 'FINANCE STUDIES'"),
             ("nbs_1969", "8. 63 26. 08", "the death rate of 1969 is printed 8.63"),
             ("nbs_1957", "64653 33462", "'33462' for '33469'")]


def check_readings(df: pd.DataFrame) -> None:
    src = meta()["sources"]
    n = img = 0
    for r in df.itertuples():
        assert r.file in src, (r.id, r.file)
        vals = [float(x) for x in r.value.split(";")] if r.value else []
        if src[r.file]["format"] == "image":                 # read on a page image: no quotation
            assert not r.quote and IMAGE_NOTE in r.note, r.id
            img += 1
            got = read_text(r.id, transcription(r.id))
        else:
            assert r.quote and IMAGE_NOTE not in r.note, f"{r.id}: no quotation"
            got = read_text(r.id, " ".join(r.quote.split()))
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
    # the page images belong to the scans: the same address and file
    for img_key, key in (("zv1962_43img", "zv1962_43"), ("lenkomscan43img", "lenkomscan43")):
        assert src[img_key]["url"] == src[key]["url"] and src[img_key]["sha256"] == src[key]["sha256"], img_key
    for key in ("kornai1980_43img", "kornai1986_43img", "zv1965_43img"):
        assert src[key]["format"] == "image" and src[key]["url"].endswith(".pdf"), key


N_QUOTED, N_IMAGE = 210, 57


# ---------------------------------------------------------------------------------------------------
# 2. The quotations of the text: each “…” is a rendering of words of a row
TRANSLATIONS = {
    "不可取的措施": "zv62_undesirable",
    "临时的措施": "zv62_temporary",
    "共产主义我们建不成了，赶美国赶得太早了。": "lk_bogusov",
    "最后的牺牲": "fr47_sacrifice",
    "只会打乱生产": "zv62_disorganize",
    "短缺": "k80_shortage",
    "抽吸": "k80_names",
    "家长式": "k86_paternal",
    "被动的": "k86_passive",
    "原始利润": "k86_original",
    "一系列必要的措施": "res_tonggou",
    "忽视了客观的经济规律": "res_line2",
    "轻率地发动了": "res_rash",
    "共产风": "res_symptoms",
    "错误地发动了": "res_lushan",
    "反右倾": "res_lushan",
    "不灵活": "mqy_inflexible",
    "发生严重困难": "res_verdict",
    "调整、巩固、充实、提高": "res_winter",
    "统治者从来不挨饿": "smil_sen",
    "行政方法压倒了经济方法": "zv65_admin",
    "消费上相当大的牺牲": "wb78_savings",
    "越来越高的通胀": "wb78_inflation",
}
# the words of the source each rendering renders, in the quotation (or the transcription of the page image); the
# resolution of 1981 is quoted in its own words
KEYWORDS = {
    "zv62_undesirable": ["повышение цен - мера нежелатель"],
    "zv62_temporary": ["это мера временная"],
    "lk_bogusov": ["Коммунизм нам не построить, рано стали Америку догонять."],
    "fr47_sacrifice": ['"last sacrifice"'],
    "zv62_disorganize": ["только лишь дезорганизуют производство"],
    "k80_shortage": ["“shortage”"],
    "k80_names": ["“suction”"],
    "k86_paternal": ["paternalistic role"],
    "k86_passive": ["‘passive’"],
    "k86_original": ["Original profit"],
    "res_tonggou": ["一系列必要的措施"],
    "res_line2": ["忽视了客观的经济规律"],
    "res_rash": ["轻率地发动了"],
    "res_symptoms": ["“共产风”"],
    "res_lushan": ["错误地发动了", "“反右倾”"],
    "mqy_inflexible": ["inflexible"],
    "res_verdict": ["发生严重困难"],
    "res_winter": ["“调整、巩固、充实、提高”"],
    "smil_sen": ["The rulers never starve."],
    "zv65_admin": ["превалировали административные методы в ущерб экономическим"],
    "wb78_savings": ["a considerable sacrifice in consumption"],
    "wb78_inflation": ["high and rising rates of inflation"],
}
# the one sentence of a worker's words from the archival record (an official record of a CPSU body, not a modern
# scholar's text): the brief allows it; every other quotation is a short phrase
LONG = {"共产主义我们建不成了，赶美国赶得太早了。"}
CHINESE = ("res_",)                                   # quoted in the source's own words


def tex_text() -> str:
    return "\n".join(l for l in TEX.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("%"))


def text_quotations() -> list[str]:
    """The “…” of the text; the closing question is Chapter 44's and the chapter's own question is in the guide and at
    the end of the opening (both checked by guide() and opening())."""
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 44's question"
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
        rid = TRANSLATIONS[q]
        assert rid in ids and rid in KEYWORDS, rid
        if rid.startswith(CHINESE):
            assert q in words_of(rid), (q, rid)                                   # the source's own words
    stale = set(TRANSLATIONS) - used
    assert not stale, f"listed but not in the text: {sorted(stale)}"
    for rid, words in KEYWORDS.items():
        for w in words:
            assert w in words_of(rid), f"{rid}: {w!r} not in the quotation"
    assert set(KEYWORDS) == set(TRANSLATIONS.values())
    for q in used - LONG:
        assert len(q) <= 12, f"a long quotation: “{q}”"
    assert LONG <= used
    print(f"ok {n} quotations of the text found in the snapshot ({len(used)} distinct)")


# ---------------------------------------------------------------------------------------------------
# 3. Numbers: said() and the parts of the text it does not read
UNITS = {"万亿": 10 ** 12, "亿": 10 ** 8, "万": 10 ** 4}
AMOUNT = re.compile(r"(\d[\d,]*(?:\.\d+)?)(?:\s*(万亿|亿|万))?")
# what is not a number of the story: labels, citations, cross-references, the key equations (models() reads them), the
# sub- and superscripts of the math and the numbers of the parts of an example
MASKS = [re.compile(r"\\begin\{keyeq\}.*?\\end\{keyeq\}", re.DOTALL),
         re.compile(r"\\(?:label|cite|chref|secref|figref|tabref|exref|eqref|ref|nameref|url|fig)\{[^}]*\}"),
         re.compile(r"_\{[^}]*\}|_\d"),
         re.compile(r"\^\{\d+\}"),
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
    """The phrase is in the text, and each number it prints (with its unit 万 or 亿; a minus sign not read) is the
    value given, within half a unit of its last digit (plus `slack`, in the same units). None skips a number (one
    checked by an assertion)."""
    say(phrase)
    found = AMOUNT.findall(mask(phrase).replace("{,}", ","))                     # 66{,}601 in the math
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
    runs_ = list(re.finditer(r"\d+", m))
    bad = [(r.group(), t[max(0, r.start() - 25):r.end() + 10].replace("\n", " ")) for r in runs_
           if not all(covered[r.start():r.end()])]
    for b in bad[:80]:
        print("    not read:", b)
    assert not bad, f"{len(bad)} numbers of the text not read by said()"
    print(f"ok all {len(runs_)} numbers of the text are read by said() ({len(set(COVERED))} phrases)")


def paragraph(start: str) -> str:
    """The paragraph of the text that contains `start`, from `start` to its end."""
    t = tex_text()
    return t[t.index(start):].split("\n")[0]


def version(key: str) -> str:
    return meta()["sources"][key]["version"]


def month(rid: str, name: str) -> int:
    """The month a row prints by its name (Russian genitive or English)."""
    has(rid, name)
    ru = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября",
          "декабря"]
    en = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]
    return (ru.index(name) if name in ru else en.index(name)) + 1


# ---------------------------------------------------------------------------------------------------
# The teaching models (the inputs the text calls 教学用的假设 or 本书设的)
OVERHANG = dict(goods=1.50, meat_share=0.20, sc_goods=1.70)     # ex:planned-overhang and self-check 1
SBC = dict(Rp=0.6, Bp=0.2, Ep=0.5, RL=0.2, BL=-0.1)              # ex:planned-sbc
QUOTA = dict(need=100, YA=250, YB=150, QA=130, QB=30, cut=0.20, city2=120, sc_cut=0.10)   # ex:planned-quota
ILLYRIA = dict(a=10, R=100, p1=1.0, p2=1.25, sc_p=2.0)          # ex:planned-illyria: q(L) = a sqrt(L)
KOPECKS, CENTNER = 100, 100                                     # 100 kopecks a rouble; a centner is 100 kg
EQ_SBC = r"R_p+B_p+E_p-1>R_L+B_L ,\qquad R_p+B_p+E_p<2 .\label{eq:planned-sbc}"
EQ_QUOTA = r"C_i=Y_i-\bar Q_i .\label{eq:planned-quota}"
EQ_ILL = r"p\,q'(L)=y=\frac{pq(L)-R}{L} .\label{eq:planned-illyria}"


def hidden(income: float, goods: float) -> float:
    """eq:reconstruction-overhang with no overhang in the base year: P/P̄ = M/(k P̄ Y) = income growth / goods growth."""
    return income / goods


def refinance(Rp, Bp, Ep, RL, BL) -> bool:
    """The first condition of eq:planned-sbc: ex post, refinancing (inject 1 more) beats liquidation."""
    return Rp + Bp + Ep - 1 > RL + BL


def inefficient(Rp, Bp, Ep) -> bool:
    """The second condition of eq:planned-sbc: ex ante, two injections of 1 return less than 2."""
    return Rp + Bp + Ep < 2


def threshold(Bp, BL) -> float:
    """KMR: the manager submits a poor project iff s B_p + (1-s) B_L >= 0, i.e. s >= -B_L/(B_p - B_L)."""
    return -BL / (Bp - BL)


def left(Y: float, Q: float) -> float:
    """eq:planned-quota."""
    return Y - Q


def illyria(p: float, a: float, R: float) -> tuple[float, float, float]:
    """The Illyrian firm with q = a sqrt(L): sqrt(L) = 2R/(p a); members, output, income per member."""
    s = 2 * R / (p * a)
    L = s * s
    q = a * s
    return L, q, (p * q - R) / L


def excess(base: float) -> list[float]:
    """Excess deaths (万) of 1959, 1960 and 1961 from table A-1: midyear population x (death rate - base) / 1000."""
    pop = {y: facts()[f"nbs_{y}"][1] for y in range(1958, 1962)}
    cdr = {y: facts()[f"nbs_{y}"][7] for y in range(1959, 1962)}
    return [(pop[y - 1] + pop[y]) / 2 * (cdr[y] - base) / 1000 for y in (1959, 1960, 1961)]


def base(years_: range) -> float:
    """The mean official death rate of the years."""
    return float(np.mean([facts()[f"nbs_{y}"][7] for y in years_]))


def models() -> None:
    t = TEX.read_text(encoding="utf-8")
    assert EQ_SBC in t and EQ_QUOTA in t and EQ_ILL in t
    assert "\\label{eq:reconstruction-overhang}" in chapter("ch35_reconstruction")
    rng = np.random.default_rng(43)
    for _ in range(300):
        Rp, Bp, Ep, RL, BL = rng.uniform(-1, 2, 5)
        # eq:planned-sbc: the centre's payoff of refinancing (R_p+B_p+E_p less the new 1) against liquidation
        assert refinance(Rp, Bp, Ep, RL, BL) == ((Rp + Bp + Ep) - 1 > RL + BL)
        # the second condition is KMR's (2), 1 > R_p + B_p + E_p - 1: two injections of 1 return less than 2
        assert inefficient(Rp, Bp, Ep) == (1 > Rp + Bp + Ep - 1)
        # the manager's condition s B_p + (1-s) B_L >= 0 at the threshold (when B_p > 0 > B_L)
        if Bp > 0 > BL:
            s = threshold(Bp, BL)
            assert 0 < s < 1 and abs(s * Bp + (1 - s) * BL) < 1e-12
    for _ in range(300):
        # eq:planned-quota: a cut by the same share takes more grain from the region with the larger output
        YA, YB, c = rng.uniform(50, 500), rng.uniform(50, 500), rng.uniform(0.01, 0.5)
        QA, QB = rng.uniform(0, YA), rng.uniform(0, YB)
        dA = left(YA, QA) - left((1 - c) * YA, QA)
        dB = left(YB, QB) - left((1 - c) * YB, QB)
        assert np.isclose(dA, c * YA) and (dA > dB) == (YA > YB)
    for _ in range(300):
        # eq:planned-illyria: the income per member is greatest where p q'(L) = y; a higher price, fewer members
        p, a, R = rng.uniform(0.5, 3), rng.uniform(2, 20), rng.uniform(10, 500)
        L, q, y = illyria(p, a, R)
        grid = np.linspace(L * 0.5, L * 1.5, 2001)
        income = (p * a * np.sqrt(grid) - R) / grid
        assert abs(grid[income.argmax()] - L) <= grid[1] - grid[0]
        assert np.isclose(p * a / (2 * math.sqrt(L)), y)
        assert illyria(1.1 * p, a, R)[1] < q
    print("ok the key equations and the claims made of them on 900 random draws")


# ---------------------------------------------------------------------------------------------------
# 4. The text, section by section
def guide(F, Y, Q):
    t = TEX.read_text(encoding="utf-8")
    assert f"\\guidequestion{{{GUIDE}}}" in t and GUIDE == PREV
    assert chapter("ch42_eastasia").rstrip().endswith(PREV)                     # 第 42 章交来的问题
    assert "\\guideprereq{\\chref{ch:soviet}\\enspace\\nameref{ch:soviet}}" in t
    said("用科尔奈的短缺经济（1980）与软预算约束（1986）分析计划经济的宏观运行", F["k80_title"][0], F["k86_journal"][1])
    said("描述中国第一个五年计划与大跃进，并如实记录 1959—1961 年饥荒的规模与成因", *F["res_verdict"])
    said("比较苏联柯西金改革（1965）与南斯拉夫的自治模式", F["zv65_date"][1])
    say("解释排队、强制储蓄与货币过剩等被压抑的通胀")
    assert "\\chapterstub" not in t


def opening(F, Y, Q):
    d, y = F["zv62_date"]
    has("zv62_date", "Пятница")
    m = month("zv62_date", "июня")
    assert pd.Timestamp(int(y), m, int(d)).day_name() == "Friday"
    said("1962 年 6 月 1 日是星期五", y, m, d)
    said("那天，《东方曙光报》在第 1 版登出一封呼吁书", page("zv62_title"))
    has("zv62_masthead", "ЗАРЯ ВОСТОКА", "КОМПАРТИИ ГРУЗИИ", "СОВЕТОВ ДЕПУТАТОВ ТРУДЯЩИХСЯ ГРУЗИНСКОЙ ССР")
    say("这家报纸是格鲁吉亚共产党中央与格鲁吉亚劳动者代表苏维埃的机关报")
    has("zv62_title", "ОБРАЩЕНИЕ ЦК КПСС иСовета Министров СССР", "колхозникам", "советской интеллигенции",
        "ко всему советскому народу")
    say("呼吁书的署名是苏共中央委员会与苏联部长会议，写给工人、集体农庄庄员、国营农场职工、知识分子与全体苏联人民")
    has("zv62_procure", "закупочные цены на мясо крупного рогатого ско")
    has("zv62_35", "свиней, овец, коз и птицу в среднем на 35 процентов")
    said("国家收购牛、猪、绵羊、山羊与家禽的价格平均提高 35\\%", F["zv62_35"][0])
    has("zv62_retail", "повысить розничные цены на мясо")
    has("zv62_25", "ное в среднем на 25 процентов")
    said("肉与肉制品的零售价平均提高 30\\%，黄油平均提高 25\\%", F["zv62_30"][0], F["zv62_25"][0])
    has("zv62_sugar", "на сахар")
    has("zv62_viscose", "вискозной штапельной пряжи")
    said("同一版上，部长会议宣布糖的零售价平均降低 5\\%，粘胶纤维布平均降低 20\\%", F["zv62_sugar"][0],
         F["zv62_viscose"][0])
    assert page("zv62_sugar") == page("zv62_title") == page("zv62_viscose")
    # the Leningrad report of the same day
    assert F["lk_date"] == F["zv62_date"] and F["lk_number"][0] == 75
    has("lk_date", "No75 I июня 1962")
    said("同一天，列宁格勒市委党组织部的信息组写好第 75 号情况汇报", F["lk_number"][0])
    has("lk_number", "СЕКТОРА ИНФОРМАЦИИ ОТДЕЛА ПАТИЙНЫХ ОРГАНОВ ЛЕНИНГРАДСКОГО ГОРОДСКОГО КОМИТЕТА")
    has("lk_addressee", "СЕКРЕТАРЮ ЛЕНИНГРАДСКОГО ГОРКОМА КПСС тов. ПОПОВУ Г.И,")
    say("送市委书记波波夫（G. I. Popov，生卒年未详）")
    has("lk_bogusov", "Электрик ремонтно-строительного управления Кронштадта")
    say("喀琅施塔得修建管理处的一名电工说")
    has("lk_turner", "Токарь", "долго не приступал к работе")
    has("lk_skb", "кандидат в члены КПСС", "член КПСС", "профсоюзное собрание")
    has("lk_cuts", "правительственных дач")
    say("喀琅施塔得一个设计局的一名党员和一名预备党员要求马上开工会大会，主张削减机关开支和政府的别墅，不靠涨价")
    a, b = F["lk_dates"]
    assert F["lk_scan_dates"] == F["lk_dates"]                                  # the scan reads the same
    said("决定 5 月 17 日就作出了，为什么拖到 5 月 31 日才宣布", month("lk_dates", "мая"), a, 5, b)
    # the appeal's account
    said("1961 年劳动者的货币收入比 1953 年多 420 亿卢布，增加了 87\\%", F["zv62_income"][0], F["zv62_87"][0],
         F["zv62_87"][1] * 1e9, F["zv62_87"][2])
    has("zv62_87", "миллиарда рублей")
    m1, t1, y2, m2, t2 = F["zv62_meat"][:2] + F["zv62_meat"][2:]
    has("zv62_meat", "1 миллион 757 тысяч тонн", "4 миллиона 33 ты")
    said("国营商业卖出的肉与肉制品，1953 年是 175.7 万吨，1961 年是 403.3 万吨", F["zv62_sold"][0],
         m1 * 1e6 + t1 * 1e3, y2, m2 * 1e6 + t2 * 1e3)
    assert 0.8 <= F["zv62_87"][2] / 100 < 0.9
    assert told("收入多了八成多", "多了", "多") == 0.8
    say("上一章末尾说，计划经济的政府管着几乎所有的价格（\\chref{ch:eastasia}）")
    assert paragraph("两家机关在呼吁书里也算了一笔账").endswith(GUIDE)              # the opening ends with the question


def world(F, Y, Q):
    d, y, _ = F["fr47_date"]
    said("1947 年 12 月 14 日，苏联换了货币，取消了配给", y, month("fr47_date", "December"), d)
    has("fr47_radio", "money price changes derationing decree announced by radio")
    has("fr47_single", "Ration cards abolished", "except peasant markets and certain cooperative goods")
    assert F["fr47_cash"] == [10, 1]
    assert told("现金按十比一兑换", "按", "比") == F["fr47_cash"][0]
    said("政府没收了所有现金的 90\\%，受打击最重的是农民", F["fr47_expropriates"][0])
    has("fr47_expropriates", "hit peasants hardest")
    said("戈比是辅币单位，100 戈比合 1 卢布", KOPECKS, 1)
    yb, k0, k1, pct = F["fr47_bread"]
    assert yb == y - 1 and Y["fr47_bread"] == yb
    said("上一年 9 月配给的黑面包从 90 戈比提到 340 戈比", month("fr47_bread", "September"), k0, k1)
    said("那一年配给食品的价格平均提高了 180\\%，低工资阶层的工资却几乎没涨", F["fr47_180"][0])
    has("fr47_180", "last year", "insignificant wage rises in lower brackets")
    has("fr47_200", "Meat, vegetables, sugar, fats, cakes and fish remain at current ration prices")
    said("肉、蔬菜、糖、油脂与鱼都留在配给价上，比一年前平均约高 200\\%", F["fr47_200"][0])
    has("fr47_freeze", "freezes ration increases of last year")
    # the prices of 1961 against the costs
    said("此后标价由国家定下，很少再动，与成本也不相干（本书的概括）")
    _, _, y61, c88 = F["zv62_cattle88"]
    said("按两家机关的数，1961 年每公担活牛的生产成本是 88 卢布，国家的收购价只有 59.1 卢布", y61, c88,
         F["zv62_cattle59"][0])
    has("zv62_cattle", "Себестоимость 1 центнера крупного рогатого скота (в живом ве")
    said("公担是 100 公斤", CENTNER)
    said("活猪是 118 卢布对 82.3 卢布", *F["zv62_pigs"])
    said("家禽是 133.5 卢布对 82.2 卢布", F["zv62_poultry"][3], F["zv62_poultry2"][0])
    has("zv62_statecost", "в минувшем году затраты государства на закупку")
    cost, retail = F["zv62_beefcost"][0], F["zv62_beefretail"][0]
    said("1961 年，国家收购、加工与销售每公担牛肉（按屠宰重）花 138.6 卢布，牛肉的平均零售价是 110.8 卢布",
         F["zv62_date"][1] - 1, cost, retail)
    said("猪肉是 167.2 卢布对 155.6 卢布", F["zv62_porkcost"][0], F["zv62_pork"][0])
    sub = cost - retail
    said("每卖 1 公担牛肉，国家贴 27.8 卢布", 1, sub)
    assert abs(told("约为零售价的四分之一", "零售价的") - sub / retail) < 0.01
    has("zv62_losses", "на многие сотни миллионов рублей")
    new = retail * (1 + F["zv62_30"][0] / 100)
    said("零售价提高 30\\% 以后，牛肉每公担约 144 卢布，才略高于国家的花费（本书的计算）", F["zv62_30"][0], new)
    assert cost < new < cost * 1.05
    # demand against supply
    has("zv62_population0", "особенно городское, растет очень быстро. С 1953")
    said("1953—1961 年苏联人口增加了 2,900 万，其中城市人口增加了 2,800 万", F["zv62_population0"][0],
         F["zv62_population"][0], F["zv62_population"][1] * 1e6, F["zv62_urban"][0] * 1e6)
    has("zv62_slaughter", "Производство мяса (в убойном весе) за это же время")
    a, b, c, e = F["zv62_output"]
    said("同一时期，肉的产量（按屠宰重）从 580 万吨增加到 880 万吨", a * 1e6 + b * 1e3, c * 1e6 + e * 1e3)
    sold = (F["zv62_meat"][3] * 1e6 + F["zv62_meat"][4] * 1e3) / (F["zv62_meat"][0] * 1e6 + F["zv62_meat"][1] * 1e3)
    said("国营商业卖出的肉增加到原来的 2.3 倍，产量只增加到 1.5 倍（本书的计算）", sold, (c + e / 1000) / (a + b / 1000))
    # where the money is to come from
    has("zv62_where", "откуда взять их?")
    has("zv62_housing", "последние четыре года 50 миллионов")
    has("zv62_quarter", "почти четверть населения страны")
    said("它们又说，近四年有 5000 万人、差不多全国人口的四分之一住进了新房", F["zv62_housing"][0] * 1e6)
    assert told("近四年", "近", "年") == 4 and told("差不多全国人口的四分之一", "人口的") == 0.25
    has("zv62_vodka2", "табак")
    say("谁决定，谁承担，这里看得清楚")
    # Leningrad
    has("lk_war", "чтобы не было войны")
    has("lk_shirkov2", "снижение цен на штапель и сахар")
    has("lk_makarenko2", "дачи и автомашины")
    has("lk_panov", "Фрезеровщик", "Металлического завода", "ругают Н.С. Хрущева")
    has("lk_baltic", "На Балтийском заводе", "за 8 лет")
    said("波罗的海工厂有人问，赫鲁晓夫 8 年来为什么还没有把农业搞好", F["lk_baltic"][0])
    # Eastern Europe, China, Yugoslavia
    has("k80_scope", "small Eastern European countries")
    has("mqy_soviet", "similar to that of the Soviets")
    said("当时约 80\\% 的人口务农，政府把征购粮食看作发展的关键", F["mqy_agri"][0])
    has("wb78_invest", "first two years of the plan")
    assert told("战后第一个计划的头两年", "头", "年") == F["wb78_invest"][0]
    said("世界银行的考察团在 1978 年的报告里写道，战后第一个计划的头两年产出增长很快，投资率升到 30\\% 以上",
         F["wb78_date"][2], F["wb78_invest"][1])
    has("wb78_mission", "economic mission that visited Yugoslavia")
    said("1948 年年中以后，它与苏联和情报局各国决裂，计划无法完成", F["wb78_break"][0])
    has("wb78_break", "after mid-1948", "Cominform")
    said("1950 年起，它尝试以社会所有制与工人自治为基础建立新的经济秩序", F["wb78_1950a"][0])


def shortage(F, Y, Q):
    said("1928—2021）1980 年出版了《短缺经济学》", None, None, F["k80_title"][0])
    has("k80_title", "ECONOMICS OF SHORTAGE")
    has("k80_queue", "baker’s or the butcher’s shop", "installation of a telephone", "admission to a hospital")
    has("k80_production", "labor shortage, shortage of material, of parts, or of electric current")
    has("k80_names", "“repressed inflation”", "introduced two further expressions")
    said("他还说，匈牙利 1968 年改革以后，企业的自主权扩大了", F["k80_hungary"][0])
    has("k80_sign", "of the reverse sign", "underutilization", "“overheating”")
    has("k80_tourist", "“tourist’s experience”")
    # forced substitution
    q10, q11, q9, _ = F["k80_screw"]
    has("k80_screw", "steel of quality 10", "use quality 11 instead")
    said("工艺规定用 10 号钢，可这种钢用完了", q10)
    said("厂里可以改用更贵的 11 号钢，也可以改用 9 号钢，螺丝就不那么耐用", q11, q9)
    has("k80_ch4", "The buyer: Shopping process", "forced substitution")
    said("他在第 4 章讲买东西的过程，也用了这个说法", F["k80_ch4"][0])
    say("标价没有变，买到的东西变了，物价指数量不到（本书的解读）")
    # the overhang: ex:planned-overhang
    inc = 1 + F["zv62_87"][2] / 100
    g, share = OVERHANG["goods"], OVERHANG["meat_share"]
    said("设 1953 年苏联的消费品市场没有货币过剩", F["zv62_87"][0])
    said("到 1961 年，居民的货币与收入一样增加 87\\%（收入的增幅是呼吁书的数），按固定价格买得到的消费品只增加 50\\%（教学用的假设）",
         F["zv62_income"][0], F["zv62_87"][2], 100 * (g - 1))
    said("肉类占消费支出的 20\\%（教学用的假设），只把肉价提高 30\\%，平均标价提高多少？", 100 * share, F["zv62_30"][0])
    h = hidden(inc, g)
    said("$P/\\bar P=1.87/1.50\\approx1.25$，藏起来的价格水平比标价高约 25\\%", inc, g, h, 100 * (h - 1))
    said("$1-1.50/1.87\\approx0.20$，约两成", 1, g, inc, 1 - g / inc)
    assert told("约两成", "约") == round(1 - g / inc, 1)
    rise = share * F["zv62_30"][0]
    said("$0.20\\times30\\%=6\\%$，平均标价只提高 6\\%，离 25\\% 还远", share, F["zv62_30"][0], rise, rise, 100 * (h - 1))
    # the soft budget constraint
    said("1986 年，科尔奈在《Kyklos》上专门讨论了软预算约束", F["k86_journal"][1])
    has("k86_soft", "paid by some other institution, typically by the State", "with high probability")
    assert [F[r][0] for r in ("k86_subsidy", "k86_tax", "k86_credit", "k86_price")] == [1, 2, 3, 4]
    assert told("科尔奈列了四种软化的办法", "列了", "种") == 4
    has("k86_classical", "can survive indefinitely")
    say("\\chref{ch:solow}用替代弹性低来读苏联的增长放缓，把激励的解释留了下来")
    # Kornai, Maskin and Roland
    said("Kornai、Maskin 与 Roland 2003 年把它写成一个承诺问题", F["kmr_cite"][0])
    said("一个项目先要投入 1", F["kmr_setup"][0])
    has("kmr_poor", "zero monetary return by the beginning of period 2")
    said("国家也可以再投入 1，第二期得到$R_p$", F["kmr_refinance"][0])
    has("kmr_political", "political benefit of keeping project workers employed")
    has("kmr_exante", "ex ante criterion", "ex post criterion", "already been sunk")
    said("只要$sB_p+(1-s)B_L\\ge0$，经理就会把差项目报上来", 1, 0)
    # ex:planned-sbc
    S = SBC
    said("设$R_p=0.6$，$B_p=0.2$，$E_p=0.5$，$R_L=0.2$，$B_L=-0.1$（教学用的假设）", S["Rp"], S["Bp"], S["Ep"], S["RL"],
         -S["BL"])
    post, liq = S["Rp"] + S["Bp"] + S["Ep"] - 1, S["RL"] + S["BL"]
    assert refinance(**S) and inefficient(S["Rp"], S["Bp"], S["Ep"])
    said("事后$0.6+0.2+0.5-1=0.3$，大于清算的$0.2-0.1=0.1$，国家续贷", S["Rp"], S["Bp"], S["Ep"], 1, post, S["RL"],
         -S["BL"], liq)
    said("事前$0.6+0.2+0.5=1.3<2$，这个项目当初就不该做", S["Rp"], S["Bp"], S["Ep"], post + 1, 2)
    said("国家必然续贷，$s=1$，经理的所得是$B_p=0.2\\ge0$，他会报", 1, S["Bp"], 0)
    said("国家若能让人相信续贷的概率低于$0.1/0.3\\approx0.33$，他就不报（本书的计算）", -S["BL"], S["Bp"] - S["BL"],
         threshold(S["Bp"], S["BL"]))
    said("若国家不在乎工人的饭碗，$E_p=0$呢？", 0)
    no_e = S["Rp"] + S["Bp"] - 1
    assert not refinance(S["Rp"], S["Bp"], 0, S["RL"], S["BL"])
    said("事后$0.6+0.2-1=-0.2<0.1$，国家清算，约束是硬的", S["Rp"], S["Bp"], 1, -no_e, liq)
    said("软化约束的正是保饭碗的那$0.5$（本书的解读）", S["Ep"])
    # the case box: Hungary 1982
    yk, n = F["k86_firms"][1], F["k86_firms"][0]
    said("\\begin{case}{匈牙利 · 1982 · 利润的再分配}", yk)
    said("匈牙利 1968 年起改革，计划指令取消了，预算约束仍然是软的", F["k80_hungary"][0])
    has("k86_firms", "all State-owned enterprises")
    has("k86_team", "directed by the author and by A. Matits")
    said("科尔奈与 Matits 主持的研究组研究了 1982 年全部国有企业的财务状况，共 1755 家", yk, n)
    t1 = F["k86_t1"]
    assert t1[3] == yk
    said("1982 年，补贴总额相当于原始利润总额的 0.91 倍，税收总额相当于 1.27 倍", t1[3], t1[4], t1[5])
    said("经手的是 276 种税与补贴", F["k86_276"][0])
    loss, high = F["k86_t3_loss"], F["k86_t3_high"]
    assert np.isclose(sum(loss), 1) and np.isclose(sum(high), 1)
    said("原来亏损的企业，再分配以后只有 11\\% 仍然亏损，77\\% 变成低利润", 100 * loss[0], 100 * loss[1])
    said("原来高利润的企业，只有 11\\% 仍是高利润，46\\% 降到低利润", 100 * high[3], 100 * high[1])
    has("k86_t3_loss", "Loss-maker")
    has("k86_t3_high", "High profitability")
    has("k86_exit", "exit is not related to profitability")
    has("k86_invest", "not correlated with profitability at all")


def china(F, Y, Q):
    said("Meng、Qian 与 Yared 转引 Eckstein 说，1950 年代工业化占了政府支出的 43\\%", F["mqy_43"][1], F["mqy_43"][0])
    has("mqy_43", "(Eckstein, 1977")
    has("mqy_export", "mostly to the U.S.S.R.", "equipment and expertise")
    said("中共中央 1981 年的历史决议", F["res_date"][0])
    has("res_market", "市场繁荣，物价稳定")
    said("1953—1956 年，工业总产值平均每年增长 19.6\\%，农业总产值增长 4.8\\%", *F["res_ffyp"])
    # collectivization
    n3, y52, a, b = F["mqy_phases"]
    assert told("土地改革到集体化分三个阶段", "分", "个") == n3
    said("1952 年起，政府鼓励六到九户农民组成互助组", y52)
    assert told("政府鼓励六到九户", "鼓励", "到") == a and told("六到九户", "到", "户") == b
    said("1954 年前后是后来所说的初级合作社", F["mqy_lowlevel"][0])
    has("mqy_lowlevel", "began around 1954", "low level collectivization")
    has("mqy_quota", "a set low price")
    said("约 5\\% 的土地留作自留地，出产全归农户", F["mqy_plots"][0])
    y57, p83 = F["mqy_83"][:2]
    has("mqy_83", "(Spence, 1991")
    said("他们转引 Spence 说，1957 年，全国 83\\% 的猪与家禽出自自留地", y57, p83)
    has("mqy_marginal", "not rewarded for their marginal labor input")
    # 1958
    said("1958 年，决定换了方向", F["res_line"][0])
    has("res_haste", "急于求成")
    has("res_survey", "没有经过认真的调查研究和试点")
    y59, p93 = F["mqy_93"][:2]
    said("Meng 等人转引 Spence 说，到 1959 年，93\\% 的农地实行高级集体化，自留地取消了", y59, p93)
    has("mqy_markets", "(Fairbank, 1986")
    said("按他们转引 Becker 的说法，1958 年秋，村民被鼓励在公共食堂里想吃多少吃多少", F["mqy_eat"][0])
    has("mqy_eat", "in the fall of 1958", "(Becker, 1996")
    # Smil on the Leap
    has("smil_steel", "steel production the centrepiece")
    has("smil_iron", "tens of millions of peasants", "brittle cast iron")
    assert told("粮食当时提供中国人八成以上的食物热量", "提供中国人", "以上") == F["smil_grain"][0] / 100
    has("smil_grain", "more than 80%")
    y, third = F["smil_spring2"]
    said("到 1959 年春，三分之一的省份已经闹饥荒", y)
    assert np.isclose(told("三分之一的省份", "", "的省份"), third)
    # Lushan
    a, b, m = F["res_lushan_early"]
    said("1959 年 7 月，中共中央政治局在庐山开会", b, m)
    said("从 1958 年底到庐山会议前期", a)
    has("mqy_peng", "spring of 1959")
    has("mqy_letter", "reduced incentives to work, a diversion of labor away from agriculture, and over-procurement")
    has("mqy_purge", "purge Peng as a rightist at the historic Lushan conference in July of 1959")
    assert F["mqy_purge"][0] == b and month("mqy_purge", "July") == m
    # procurement: table A8
    A = grain().set_index("year")
    said("粮食产量从 1958 年的 2 亿吨降到 1959 年的 1.7 亿吨", 1958, A.loc[1958, "production"] * 1e6, 1959,
         A.loc[1959, "production"] * 1e6)
    yl, ym, nprov = F["a8_source"]
    said("原始来源是农业部 1989 年的资料", ym)
    has("a8_source", "Ministry of Agriculture (1989)")
    said("征购量从 5200 万吨增加到 6400 万吨", A.loc[1958, "procurement"] * 1e6, A.loc[1959, "procurement"] * 1e6)
    said("征购占产量的比例从 26\\% 升到约 38\\%", A.loc[1958, "share"], A.loc[1959, "share"])
    assert F["mqy_38"][0] == round(A.loc[1959, "share"])                         # the text of the paper agrees
    assert A["procurement"].idxmax() == 1959 and (A["procurement"] == A["procurement"].max()).sum() == 1
    said("1959 年的征购量是 1952—1976 年各年里最多的（本书的计算）", 1959, A.index.min(), A.index.max())
    y, r4, p32, p26, y58 = F["mqy_32"]
    assert p26 == A.loc[1958, "share"] and y58 == 1958
    said("若 1959 年的产量照前几年每年 4\\% 的速度增长，征购只占产量的 32\\%", y, r4, p32)
    yj = F["mqy_janfeb"][0]
    has("mqy_janfeb", "January and February of 1960", "two to three months")
    said("饥荒的死亡大多发生在 1960 年 1 月和 2 月，是粮食征走以后的两三个月", yj, month("mqy_janfeb", "January"),
         month("mqy_janfeb", "February"))
    said("每个农业劳动者留下的粮食，从 268 公斤降到 193 公斤", A.loc[1958, "retained"], A.loc[1959, "retained"])
    said("1959 年出口到苏联的粮食约 430 万吨，约为当年产量的 2.3\\%", F["mqy_fn13"][0], F["mqy_fn13"][1] * 1e6,
         F["mqy_fn13b"][0])
    has("mqy_fn13", "exported to the U.S.S.R.")
    # the figure's caption
    said("中国的粮食产量与征购，1952—1976 年", A.index.min(), A.index.max())
    said("(b) 征购占产量的比例（\\%），1959 年最高", A["share"].idxmax())
    has("a8_title", "Table A8", "Li and Yang (2005)")
    said("数据：Li 与 Yang（2005），据 Meng、Qian 与 Yared（2010）附表 A8 的转引，原始来源是农业部（1989），24 个省的样本",
         yl, F["mqy_date"][0], F["a8_title"][0], ym, nprov)
    # ex:planned-quota
    Qt = QUOTA
    has("mqy_model", "three regions: two rural regions (A and B) and a city")
    has("mqy_movement", "restricts population movements")
    city = Qt["QA"] + Qt["QB"]
    said("甲、乙两个地区各需要 100 单位粮食才能活下去", Qt["need"])
    said("正常年景甲产 250，乙产 150，定额按正常年景定为甲 130、乙 30，两地各留 120，城里得 160", Qt["YA"], Qt["YB"],
         Qt["QA"], Qt["QB"], left(Qt["YA"], Qt["QA"]), city)
    assert left(Qt["YA"], Qt["QA"]) == left(Qt["YB"], Qt["QB"])
    said("这一年两地都减产 20\\%，定额不变，两地各留多少？", 100 * Qt["cut"])
    said("若城里只拿 120，两地能不能都留够 100？", Qt["city2"], Qt["need"])
    ya, yb = Qt["YA"] * (1 - Qt["cut"]), Qt["YB"] * (1 - Qt["cut"])
    said("甲产 200，留$200-130=70$；乙产 120，留$120-30=90$", ya, ya, Qt["QA"], left(ya, Qt["QA"]), yb, yb, Qt["QB"],
         left(yb, Qt["QB"]))
    assert ya - Qt["need"] + yb - Qt["need"] == Qt["city2"]
    said("甲交 100、乙交 20，正好 120，两地各留 100（本书的计算）", ya - Qt["need"], yb - Qt["need"], Qt["city2"],
         Qt["need"])
    # the official vital rates (table A-1)
    V = vital().set_index("year")
    said("全国的死亡率 1957 年是每千人 10.8 人，1960 年是每千人 25.4 人", 1957, V.loc[1957, "cdr"], 1960,
         V.loc[1960, "cdr"])
    said("出生率从 1957 年的每千人 34.0 人降到 1961 年的每千人 18.0 人", 1957, V.loc[1957, "cbr"], 1961,
         V.loc[1961, "cbr"])
    said("1960 年的自然增长率是每千人 $-4.6$ 人，人口减少了", 1960, -V.loc[1960, "ngr"])
    assert V.loc[1960, "ngr"] < 0 and V.loc[1960, "pop"] < V.loc[1959, "pop"]
    said("年底的总人口从 1959 年的 67,207 万降到 1961 年的 65,859 万", 1959, V.loc[1959, "pop"] * 1e4, 1961,
         V.loc[1961, "pop"] * 1e4)
    has("nbs_table", "全国人口状况", "年底总人口(万人)")
    said("中国的官方出生率与死亡率，1949—1970 年（每千人）", V.index.min(), V.index.max())
    said("阴影是 1959—1961 年", 1959, 1961)
    agree = [y for y in V.index if f"nb2_{y}" in F]
    assert agree == [1952, 1957, 1962, 1965, 1970]
    said("国家统计局国民经济综合统计司编《新中国五十年统计资料汇编》（1999）表 A-1；1952、1957、1962、1965 与 1970 年与《中国统计年鉴 2000》表 4-2 相同",
         F["nbs_edition"][0], F["nbs_table"][0], *agree, 2000, *F["nb2_title"])
    has("nbs_compiler", "国家统计局国民经济综合统计司编")
    # ex:planned-excess
    b57, b5658 = base(range(1957, 1958)), base(range(1956, 1959))
    e1, e2 = excess(b57), excess(b5658)
    said("以 1957 年的每千人 10.8 人为正常的死亡率，1959—1961 年多死了多少人？", 1957, b57, 1959, 1961)
    said("以 1956—1958 年的平均每千人 11.4 人为正常呢？", 1956, 1958, b5658)
    pop = {y: V.loc[y, "pop"] for y in range(1958, 1962)}
    mid = [(pop[y - 1] + pop[y]) / 2 for y in (1959, 1960, 1961)]
    said("1959 年$66{,}601\\text{万}\\times(14.59-10.80)/1000\\approx252$万", 1959, mid[0], V.loc[1959, "cdr"], b57, 1000,
         e1[0])
    said("1960 年$66{,}707\\text{万}\\times14.63/1000\\approx976$万", 1960, mid[1], V.loc[1960, "cdr"] - b57, 1000,
         e1[1])
    said("1961 年$66{,}033\\text{万}\\times3.44/1000\\approx227$万", 1961, mid[2], V.loc[1961, "cdr"] - b57, 1000,
         e1[2])
    said("合计约 1,460 万", sum(e1) * 1e4, slack=5)
    said("三年依次约 213 万、936 万与 188 万，合计约 1,340 万（本书的计算）", *(x * 1e4 for x in e2), sum(e2) * 1e4, slack=3)
    say("这只是登记了的死亡")
    # the scholars' estimates
    said("Smil 说，1982 年第一次可靠的人口普查公布了分年龄的人口，才能估计 1959—1961 年的超额死亡", F["smil_census"][0],
         F["smil_30m"][0], F["smil_30m"][1])
    has("smil_census", "first highly reliable population census")
    said("美国人口学者最初算出 1,650 万到 2,300 万", *(x * 1e6 for x in F["smil_first"]))
    said("后来更细的研究是 2,300 万到 3,000 万", *(x * 1e6 for x in F["smil_later"][:2]))
    said("他说，未发表的中国材料暗示接近 4,000 万", F["smil_later"][2] * 1e6)
    said("Meng、Qian 与 Yared 在正文里给的范围是 1,700 万到 3,000 万", *(x * 1e6 for x in F["mqy_range"]))
    five = F["mqy_five"]
    said("从 Coale（1981）的 1,650 万到 Banister（1987）的 3,000 万", five[1], five[0] * 1e6, five[3], five[2] * 1e6)
    names = set(re.findall(r"\b(Coale|Banister|Yao|Peng|Ashton)\b", Q["mqy_five"]))
    assert told("他们在附录里列了五家的估计", "列了", "家") == len(names) == 5
    assert min(five[0::2]) == five[0] and max(five[0::2]) == five[2]           # Coale's the lowest, Banister's the highest
    # the table
    said("1959—1961 年中国饥荒的超额死亡：几种估计（万人）", 1959, 1961)
    said("约 1,460 & 官方死亡率，以 1957 年为正常", sum(e1), 1957, slack=5)
    said("约 1,340 & 官方死亡率，以 1956—1958 年的平均为正常", sum(e2), 1956, 1958, slack=3)
    said("1,650—2,300 & 1982 年普查的分年龄人口，美国人口学者最初的计算 & Smil（1999）", F["smil_first"][0] * 100,
         F["smil_first"][1] * 100, F["smil_census"][0], F["smil_cite"][0])
    said("2,300—3,000 & 更细的人口重建 & Smil（1999）", F["smil_later"][0] * 100, F["smil_later"][1] * 100,
         F["smil_cite"][0])
    said("接近 4,000 & 未发表的中国材料 & Smil（1999）", F["smil_later"][2] * 100, F["smil_cite"][0])
    said("1,650—3,000 & 五家的估计（Coale、Yao、Peng、Ashton 等与 Banister），方法各不相同 & Meng、Qian 与 Yared（2010）附录",
         five[0] * 100, five[2] * 100, F["mqy_date"][0])
    said("国家统计局国民经济综合统计司编《新中国五十年统计资料汇编》表 A-1", F["nbs_table"][0])
    said("Smil（1999）；Meng、Qian 与 Yared（2010）数据附录", F["smil_cite"][0], F["mqy_date"][0])
    has("mqy_five", "due to different estimation methods")
    # why they differ
    has("smil_underestimate", "greatly underestimate both the fall in fertility and the rise in mortality")
    has("mqy_understated", "understated the severity of mortality")
    said("\\exref{ex:planned-excess}里换一个基准就差约 120 万", (sum(e1) - sum(e2)) * 1e4, slack=2)
    said("Smil 说，饿死的约 3,000 万，少生或推迟出生的也差不多这么多", F["smil_30m"][2] * 1e6)
    # the verdict and the causes
    said("官方的结论写在 1981 年的决议里", F["res_date"][0])
    said("国民经济在 1959 年到 1961 年“发生严重困难”", *F["res_verdict"])
    has("res_verdict", "自然灾害和苏联政府背信弃义地撕毁合同", "国家和人民遭到重大损失")
    said("Meng 等人说，政府曾把饥荒归于 1959 年的坏天气与低产量，学者估计天气至多能解释饥荒的 14\\% 到 50\\%",
         F["mqy_weather_claim"][0], *F["mqy_weather"][:2])
    said("以及 Lin（1990）说的农民失去了退出公社的权利", F["mqy_lin"][0])
    a, b = F["mqy_liyang2"]
    said("过度征购又让 1960—1961 年的产量进一步下降", a, 1900 + b)
    has("mqy_liyang", "over-procurement and the diversion of labor away from agriculture", "rural industrialization")
    # Meng, Qian and Yared's own findings
    said("他们算出，1959 年的粮食产量差不多是全国人口维持生存所需的三倍", F["mqy_205"][0])
    assert told("差不多是全国人口维持生存所需的三倍", "所需的", "倍") == F["mqy_three"][0]
    said("他们估计，一个人一天约要 804 卡热量才不致饿死", F["mqy_804"][0])
    k = F["mqy_82"]
    assert round(k[1] * F["mqy_804"][0] / k[2]) == k[0] and k[2] == F["mqy_3587"][0]
    said("按每公斤粮食供 3,587 卡算，合每人每年 82 公斤粮食", F["mqy_3587"][0], k[0])
    has("mqy_sample", "our sample of 27 provinces")
    said("按 27 个省的人口，1959 年维持生存要 4,800 万吨粮食，产量多出 9,900 万吨", F["mqy_sample"][0], 1959,
         F["mqy_99"][1] * 1e6, F["mqy_99"][0] * 1e6)
    assert abs((F["mqy_99"][0] + F["mqy_99"][1]) / F["mqy_99"][1] - 3) < 0.1                  # 'almost three times'
    has("mqy_reversal", "reversal of a typically negative correlation")
    has("mqy_urban", "never experienced extreme famine or mass starvation")
    # the winter
    assert told("据信死者有一半是十岁以下的孩子", "据信死者有", "是") == F["mqy_children"][0]
    assert told("一半是十岁以下的孩子", "是", "岁") == F["mqy_children"][1]
    said("1960 年春，政府减了城市的口粮，等于默认了饥荒", F["mqy_spring"][0])
    has("mqy_spring", "implicitly acknowledged the famine by reducing food rations for urban areas")
    # Smil's verdict
    assert told("政府差不多三年才采取行动", "差不多", "年") == F["smil_three"][0]
    assert told("德国花了两代人", "花了", "代") == F["smil_germany"][0]
    say("决定的是毛泽东与中央，付出生命的主要是农村的人（本书的概括）")
    # the correction
    said("纠正从 1960 年冬开始", F["res_winter"][0])
    p30, g0, g1 = F["mqy_gittings"][:3]
    said("Meng 等人转引 Gittings 说，1959—1960 年政府在工业与军事上的开支减少了 30\\%", g0, g1, p30)
    said("Smil 说，1961 年以后回到比较理性的政策", F["smil_imports"][0])
    y, mo, n = F["res_7000"]
    said("1962 年 1 月，七千人参加的扩大的中央工作会议初步总结了大跃进的教训", y, mo)
    assert told("七千人参加", "", "人参加") == n
    said("全会说，1962 年到 1966 年，国民经济得到了比较顺利的恢复和发展", *F["res_recovery"])
    # the pitfall
    p15, y58 = F["mqy_15"]
    has("mqy_15", "per capita production had fallen by 15%")
    said("1959 年中国的人均粮食产量比前一年少了 15\\%，Meng、Qian 与 Yared 算出，产量仍比避免死亡所需的多出至少 205\\%",
         F["mqy_205"][0], p15, F["mqy_205"][1])
    assert y58 + 1 == F["mqy_205"][0]


def reform(F, Y, Q):
    d, y = F["zv65_date"]
    said("1965 年 9 月 29 日，苏共中央全会通过关于改进工业管理、完善计划工作、加强经济刺激的决议", y,
         month("zv65_date", "сентября"), d)
    has("zv65_title", "ОБ УЛУЧШЕНИИ УПРАВЛЕНИЯ ПРОМЫШЛЕННОСТЬЮ", "ЭКОНОМИЧЕСКОГО СТИМУЛИРОВАНИЯ")
    has("zv65_kosygin", "Председателя Совета Министров СССР тов. Косыгина")
    has("zv65_formal", "формальный характер")
    has("zv65_fewer", "сократить число плановых показателей")
    has("zv65_levers", "прибыль, цена, премия, кредит")
    has("zv65_unified", "цен, оплаты труда и финансов")
    say("这次改革没有放开价格，预算约束也没有变硬（本书的解读）")
    # Yugoslavia
    said("1954—1974 年它的实际社会产品平均每年增长 7.2\\%，人口每年增长 1.1\\%，1975 年人均收入达到 1,480 美元",
         *F["wb78_gmp"], F["wb78_gmp2"][0], F["wb78_pop"][0], F["wb78_1480"][1], F["wb78_1480"][0])
    said("早些年的国内储蓄约占国内生产总值的 30\\%", F["wb78_savings"][0])
    said("社会部门的就业每年增长 3.7\\%，私人农业的劳力份额从 1953 年的 66\\% 降到 1975 年的 33\\%",
         F["wb78_employment"][0], F["wb78_agri2"][0], F["wb78_agri"][0], F["wb78_agri2"][1], F["wb78_agri"][1])
    said("考察团说，自治始于 1950 年", F["wb78_law"][0])
    said("1963 年的宪法与 1965 年的改革（实际是 1964—1967 年的一系列措施）改了这一点", *F["wb78_1965"])
    has("wb78_1965", "Constitution of 1963")
    # the Illyrian firm
    said("Yusuf 转述说，Ward 1958 年的模型表明", F["yu_ward0"][0])
    has("yu_ward", "income maximization by the members of a self-managed firm would discourage investment")
    has("yu_hire", "disinclined to amalgamate or expand employment")
    I = ILLYRIA
    said("设$q(L)=10\\sqrt L$，$R=100$（教学用的假设）", I["a"], I["R"])
    said("$p=1$时，自治企业有多少成员？", I["p1"])
    said("$p=1.25$呢？", I["p2"])
    assert np.isclose(2 / I["a"], 1 / 5)
    said("$5p\\sqrt L=10p\\sqrt L-R$，$\\sqrt L=R/(5p)$", I["a"] / 2, I["a"], I["a"] / 2)
    L1, q1, y1 = illyria(I["p1"], I["a"], I["R"])
    L2, q2, y2 = illyria(I["p2"], I["a"], I["R"])
    said("$\\sqrt L=20$，$L=400$，产量 200，每人收入$(200-100)/400=0.25$", math.sqrt(L1), L1, q1, I["p1"] * q1, I["R"],
         L1, y1)
    said("$\\sqrt L=16$，$L=256$，产量 160，每人收入$(200-100)/256\\approx0.39$（本书的计算）", math.sqrt(L2), L2, q2,
         I["p2"] * q2, I["R"], L2, y2)
    assert q2 < q1 and y2 > y1
    # the mission's record
    said("他们说，1965 年以后社会部门的就业增长比以前慢，1965—1967 年企业为了提高劳动生产率，就业一度下降",
         F["wb78_slower"][0], *F["wb78_rationalize"])
    has("wb78_rationalize", "once-and-for-all decline in employment")
    said("1965 年放宽了出国的条件，出国做工吸收的劳力与社会部门差不多一样多", F["wb78_migration"][0])
    said("到 1970 年代初，尽管每年有大批劳力离开农业、出国，公开的失业仍明显增加", F["wb78_unemployment"][0])
    has("wb78_unemployment", "by the early 1970s")
    has("yu_horvat", "During the sixties")
    said("按 Horvat 的研究，1960 年代投资不足从来不是问题", 1960)
    # inflation
    said("1960 年代初以前，价格受国家相当严格的管制，很稳定", F["wb78_controlled"][0])
    has("wb78_controlled", "Until the early 1960s")
    said("价格放开以后，尤其是 1965 年以后", F["wb78_after1965"][0])
    has("wb78_markup", "cost mark-up pricing")
    has("wb78_liquidation", "building up credits among themselves", "rarely forced into liquidation")
    # the compare box
    said("\\begin{compare}{柯西金改革与南斯拉夫的自治}{柯西金改革（1965）}{南斯拉夫的自治}", y)
    said("{1950 年起另建新的经济秩序", F["wb78_1950a"][0])
    said("{1960 年代初以后放开", F["wb78_controlled"][0])
    said("{1965 年以后出国做工，公开失业增加", F["wb78_migration"][0])


def data_check(F, Y, Q):
    V = vital().set_index("year")
    for y in (1952, 1957, 1962, 1965, 1970):
        assert F[f"nb2_{y}"] == [y, V.loc[y, "cbr"], V.loc[y, "cdr"], V.loc[y, "ngr"]], y        # 本书的核对
    said("《中国统计年鉴 2000》表 4-2 的出生率与死亡率，1952、1957、1962、1965 与 1970 年，与 1999 年的汇编一致（本书的核对）",
         2000, *F["nb2_title"], 1952, 1957, 1962, 1965, 1970, F["nbs_edition"][0])
    assert "The famine years 1958-1961 are not in table 4-2" in meta()["notes"]
    said("这张表没有列 1958—1961 年", 1958, 1961)
    has("mqy_csdm50", "Comprehensive Statistical Data and Materials on 50 years of New China")
    has("mqy_revised", "retrospectively corrected by the National Bureau of Statistics")
    has("mqy_methods_unknown", "have not been documented")
    d, y, kg, ha = F["mqy_hubei"]
    has("mqy_hubei", "The People's Daily (August 1, 1958)", "a county in Hubei province")
    said("1958 年 8 月 1 日的《人民日报》说，湖北一个县的水稻亩产超过 7,500 公斤", y, month("mqy_hubei", "August"), d, kg)
    said("亩是中国的面积单位，15 亩约合 1 公顷（本书的计算）", 15, round(15 * ha))
    assert abs(15 * ha - 1) < 0.01
    said("修正后的统计给出，那个省的粮食实际亩产接近 120 公斤", F["mqy_120"][0])
    has("mqy_understate_pop", "may still understate population losses")
    y60, r22, _, y50, _, _ = F["mqy_fn18"]
    said("他们的数据里，1960 年的死亡率将近每千人 22 人，约为 1950 年代最低点的两倍", y60, r22, y50)
    said("汇编的全国数是每千人 25.4 人", V.loc[1960, "cdr"])
    has("mqy_fn17", "27 provinces", "all except Tibet, Hainan and Sichuan")
    said("他们的分省数据只有 27 个省，四川、西藏与海南不在其内", F["mqy_fn17"][0])
    # Poland 1970
    y, m, d = F["fr70_date"][1], 12, F["fr70_announce"][0]
    has("fr70_date", "Warsaw , December 16, 1970")
    has("fr70_announce", "December 13 public announcement of price changes (both up and down)")
    said("1970 年 12 月 13 日，波兰政府宣布调整物价，有升有降", y, month("fr70_date", "December"), d)
    said("美国驻华沙大使馆在 16 日的电报里说", F["fr70_date"][0])
    a, b = F["fr70_cut"]
    assert told("购买力减少一成到一成半", "减少", "到") == a / 100 and told("一成到一成半", "到") == b / 100
    lo, hi, d14 = F["fr70_workers"]
    said("据瑞典驻格但斯克领事的报告，14 日下午", d14)
    assert told("八百到一千名工人示威", "", "到") == lo and told("八百到一千名", "到", "名") == hi
    said("据报约有 300 人受伤，其中有民警", F["fr70_injured"][0])
    has("fr70_injured", "cannot confirm reports of deaths from independent sources")
    assert told("哥穆尔卡和四名亲信成了替罪羊", "和", "名") == F["fr70_scapegoats"][0]
    said("美国总统的国家安全事务助理 20 日在给总统的备忘录里说", F["fr70_memo"][1])
    has("fr70_memo", "Kissinger", "President Nixon")


def debate(F, Y, Q):
    for words in ("\\subsubsection{短缺是不是货币过剩}", "\\subsubsection{饥荒的机制}", "\\subsubsection{自治企业会不会少投资}"):
        say(words)
    said("Meng、Qian 与 Yared 的发现与 Lin（1990）的解释侧重不同", F["mqy_lin"][0])
    said("Horvat 的研究说 1960 年代企业反倒投资过多", 1960)
    has("yu_critique", "no weight to future income")
    has("yu_single", "single factor assumption")


def deeper(F, Y, Q):
    said("1962 年 6 月 1 日的呼吁书与 1965 年 9 月 29 日的全会决议", F["zv62_date"][1], 6, F["zv62_date"][0],
         F["zv65_date"][1], 9, F["zv65_date"][0])
    said("1965 年那期的词里还夹着空格", F["zv65_date"][1])
    said("中共 1981 年的决议据共产党员网转载的中国政府网版本", F["res_date"][0])
    has("res_source", "来源：中国政府网")
    said("Meng、Qian 与 Yared（2010）用的是 NBER 第 16361 号工作论文", F["mqy_date"][0], F["mqy_wp"][0])
    said("科尔奈 1980 年的书只读了第一卷", F["k80_title"][0])
    has("k80_title", "Volume A")
    said("Lin（1990）没有读", F["mqy_lin"][0])
    said("Ward（1958）与 Horvat 的研究只据 Yusuf（1977）的转述", F["yu_ward0"][0], F["yu_date"][0])
    said("1958 年《人民日报》的亩产数", F["mqy_hubei"][1])
    said("新切尔卡斯克 1962 年 6 月的事件", F["zv62_date"][1], 6)
    # the works named as not obtained, with the years by which the editor's brief names them
    said("Portes 与 Winter（1980）对短缺的计量", 1980)
    said("Coale（1984）需要登记电子邮件才能下载", 1984)
    a, ret = F["a8_1959"][0], F["a8_1959"][-3]
    said("Meng 等人的附表 A8 给 1959 年每个农业劳动者的留粮是 193 公斤", F["a8_title"][0], a, ret)
    has("mqy_fn19", "223 kg per person")
    said("说 1959 年人均留粮 223 公斤", F["mqy_fn19"][0], F["mqy_fn19"][1])
    said("Meng 等人在第 1 页说死于饥荒的有 1,700 万到 3,000 万人，附录列的最低一家是 1,650 万", page("mqy_range"),
         *(x * 1e6 for x in F["mqy_range"]), F["mqy_five"][0] * 1e6)
    n49 = F["nbs_1949"]
    said("国家统计局汇编的表 A-1 里，1949 年的农业人口印作 9441 万，非农业人口印作 44726 万", F["nbs_table"][0], n49[0],
         n49[4] * 1e4, n49[5] * 1e4)
    assert n49[4] + n49[5] == n49[1] and n49[4] < n49[5]
    v69 = F["nbs_1969"]
    said("同一张表印的 1969 年死亡率是每千人 8.63 人，按同一行的出生率 34.11 与自然增长率 26.08 算应是 8.03（本书的计算）",
         v69[0], v69[7], v69[6], v69[8], v69[6] - v69[8])
    assert v69[0] == MISPRINTED_CDR
    yb, k0, k1, pct = F["fr47_bread"]
    said("代办 1947 年说黑面包从 90 戈比提到 340 戈比是涨了 275\\%，按这两个数算是约 278\\%（本书的计算）",
         F["fr47_date"][1], k0, k1, pct, 100 * (k1 / k0 - 1))
    assert round(100 * (k1 / k0 - 1)) != pct


def legacy(F, Y, Q):
    said("有 1970 年代波兰的诺瓦胡塔，也有英法之间的海峡隧道", F["kmr_examples"][0])
    has("kmr_examples", "Nowa Huta in Poland in the 1970s", "Eurotunnel")
    say("问题不在政府追求社会主义的目标")
    lo, hi = min(F["smil_first"][0], F["mqy_five"][0]), F["smil_later"][2]
    assert hi / lo > 2                                                            # 相差一倍以上
    say("学者的估计相差一倍以上（\\tabref{tab:planned-toll}）")


def takeaways(F, Y, Q):
    said("1953—1961 年苏联劳动者的货币收入增加 87\\%", F["zv62_87"][0], F["zv62_income"][0], F["zv62_87"][2])
    e1, e2 = excess(base(range(1957, 1958))), excess(base(range(1956, 1959)))
    said("1959—1961 年的中国饥荒，用官方死亡率算出的超额死亡约 1,340 万到 1,460 万，学者的估计从 1,650 万到 3,000 万，最高的接近 4,000 万",
         1959, 1961, sum(e2) * 1e4, sum(e1) * 1e4, F["mqy_five"][0] * 1e6, F["mqy_five"][2] * 1e6,
         F["smil_later"][2] * 1e6, slack=5)


def selfcheck(F, Y, Q):
    inc = 1 + F["zv62_87"][2] / 100
    g = OVERHANG["sc_goods"]
    said("按\\exref{ex:planned-overhang}，消费品若增加 70\\%，藏起来的价格水平比标价高多少？", 100 * (g - 1))
    h = hidden(inc, g)
    said("\\item $1.87/1.70=1.10$，高约 10\\%", inc, g, h, 100 * (h - 1))
    S = SBC
    lim = S["RL"] + S["BL"] + 1 - S["Rp"] - S["Bp"]
    said("\\item $0.6+0.2+E_p-1>0.1$，$E_p>0.3$", S["Rp"], S["Bp"], 1, S["RL"] + S["BL"], lim)
    Qt = QUOTA
    said("按\\exref{ex:planned-quota}，两地都减产 10\\%，定额不变，甲、乙各留多少？", 100 * Qt["sc_cut"])
    ya, yb = Qt["YA"] * (1 - Qt["sc_cut"]), Qt["YB"] * (1 - Qt["sc_cut"])
    said("\\item 甲产 225，留 95；乙产 135，留 105", ya, left(ya, Qt["QA"]), yb, left(yb, Qt["QB"]))
    I = ILLYRIA
    said("按\\exref{ex:planned-illyria}，$p=2$时自治企业有多少成员，产量多少？", I["sc_p"])
    L, q, _ = illyria(I["sc_p"], I["a"], I["R"])
    said("\\item $\\sqrt L=10$，$L=100$，产量 100", math.sqrt(L), L, q)
    b = base(range(1962, 1966))
    said("以 1962—1965 年平均的每千人 10.3 人为正常的死亡率", 1962, 1965, b)
    e = excess(b)
    said("\\item 三年依次约 288 万、1,012 万与 262 万，合计约 1,560 万", *(x * 1e4 for x in e), sum(e) * 1e4, slack=3)
    said("\\item 1959 年的产量约为维持生存所需的三倍", 1959)


def ending(F, Y, Q):
    d, y = F["zv62_date"]
    said("回到 1962 年 6 月 1 日的列宁格勒", y, month("zv62_date", "июня"), d)
    has("lk_loan", "обратиться к народу за займом", "Адмиралтейского, Балтийского", "Водоканалпроект")
    say("两家工厂和一个设计院的人问")
    has("zv62_jobs", "снята проблема безработи")
    said("1960 年，萨缪尔森与索洛把通胀与失业画成一张可以挑选的菜单，每一个点是一种失业率配一种通胀率（\\chref{ch:phillips}）",
         *there("ch38_phillips", "解释萨缪尔森与索洛（1960）怎样把它变成政策菜单"))
    assert "菜单上的每一个点，都是一种失业率配一种通胀率" in chapter("ch38_phillips")
    assert tex_text().rstrip().endswith("（\\chref{ch:phillips}）。" + NEXT)
    assert f"\\guidequestion{{{NEXT}}}" in chapter("ch44_naturalrate")


def vital() -> pd.DataFrame:
    """Table A-1 of the 1999 compilation, 1949-1970: year-end population (万), crude birth, death and natural
    growth rates (per thousand). figsrc/fig_ch43.py draws it."""
    out = []
    for y in range(1949, 1971):
        v = facts()[f"nbs_{y}"]
        assert v[0] == y and len(v) == 9
        out.append(dict(year=y, pop=v[1], cbr=v[6], cdr=v[7], ngr=v[8]))
    return pd.DataFrame(out)


def grain() -> pd.DataFrame:
    """Table A8 of Meng, Qian and Yared (2010), from Li and Yang (2005), 1952-1976: production and procurement
    (million tonnes), the grain retained per agricultural labourer (kg) and the procurement share (%)."""
    out = []
    for y in range(1952, 1977):
        v = facts()[f"a8_{y}"]
        assert v[0] == y and len(v) in (5, 6, 7)
        out.append(dict(year=y, production=v[1], retained=v[-3], procurement=v[-2], share=v[-1]))
    return pd.DataFrame(out)


MISPRINTED_CDR = 1969                    # table A-1 prints 8.63; 34.11 - 26.08 = 8.03 (the 史料说明 and the notes)


def figures_data() -> None:
    """What the figures and their captions assert of their data."""
    V = vital()
    assert (V["pop"].diff().dropna() < 0).sum() == 2                              # 1960 and 1961 only
    assert set(V.loc[V["pop"].diff() < 0, "year"]) == {1960, 1961}
    ok = abs(V["cbr"] - V["cdr"] - V["ngr"]) < 0.015
    assert list(V.loc[~ok, "year"]) == [MISPRINTED_CDR]                          # the misprint of 1969
    r = V.set_index("year").loc[MISPRINTED_CDR]
    assert np.isclose(r["cbr"] - r["ngr"], 8.03) and r["cdr"] == 8.63
    for y in range(1949, 1971):
        v = facts()[f"nbs_{y}"]
        men = 33469 if y == 1957 else v[2]                                        # the text layer's '33462' (MISPRINTS)
        assert men + v[3] == v[1] and v[4] + v[5] == v[1], y                      # men + women, the two other columns
    assert V.loc[V["cdr"].idxmax(), "year"] == 1960 and V.loc[V["cbr"].idxmin(), "year"] == 1961
    A = grain()
    assert (abs(100 * A["procurement"] / A["production"] - A["share"]) < 0.35).all()
    assert A.loc[A["share"].idxmax(), "year"] == 1959
    print(f"ok the data of the figures: {len(V)} years of table A-1, {len(A)} years of table A8")


# ---------------------------------------------------------------------------------------------------
# 5. The book
# the life dates: words -> (row of the birth year, index), (row of the death year, index), row of the heading, heading
LIVES = {"János Kornai，1928—2021": (("gnd_kornai", 1), ("gnd_kornai", 0), "gnd_name", "Kornai, János"),
         "Nikita Khrushchev，1894—1971": (("loc_khrushchev", 0), ("loc_khrushchev", 1), "loc_khrushchev",
                                         "Khrushchev, Nikita Sergeevich"),
         "毛泽东（1893—1976）": (("loc_mao", 0), ("loc_mao", 1), "loc_mao", "Mao, Zedong"),
         "彭德怀（1898—1974）": (("loc_peng", 0), ("loc_peng", 1), "loc_peng", "Peng, Dehuai"),
         "Aleksey Kosygin，1904—1980": (("loc_kosygin", 0), ("loc_kosygin", 1), "loc_kosygin",
                                       "Kosygin, Aleksey Nikolayevich"),
         "Władysław Gomułka，1905—1982": (("loc_gomulka", 0), ("loc_gomulka", 1), "loc_gomulka", "Gomułka, Władysław"),
         "Edward Gierek，1913—2001": (("loc_gierek", 0), ("loc_gierek", 1), "loc_gierek", "Gierek, Edward")}
# what other chapters tell: (words of this chapter, chapter where it is told, words there)
EVENTS = [("1947 年 12 月 14 日，苏联换了货币，取消了配给，这在\\chref{ch:reconstruction}已经讲过", "ch35_reconstruction",
           "1947 年 12 月 14 日，苏联部长会议与联共（布）中央委员会作出决定，实行货币改革，取消配给卡"),
          ("上一章末尾说，计划经济的政府管着几乎所有的价格（\\chref{ch:eastasia}）", "ch42_eastasia",
           "计划经济的政府管着几乎所有的价格"),
          ("被压抑的通胀是其中之一（\\chref{ch:alternatives}）", "ch30_alternatives",
           "\\section{被压抑的通胀}\\label{sec:alternatives-repressed}"),
          ("物资平衡表要在纸面上让每种物资的供给与需求相等（\\chref{ch:soviet}）", "ch31_soviet", "\\label{eq:soviet-balance}"),
          ("这与\\chref{ch:greekroman}的式~\\eqref{eq:greek-ceiling}是同一个逻辑", "ch07_greekroman",
           "\\label{eq:greek-ceiling}"),
          ("被压抑的通胀可以用\\chref{ch:reconstruction}的式~\\eqref{eq:reconstruction-overhang}来量", "ch35_reconstruction",
           "\\label{eq:reconstruction-overhang}"),
          ("\\chref{ch:soviet}讲过，Gregory 与 Harrison 把软预算约束追溯到斯大林的工业化", "ch31_soviet",
           "软预算约束起源于斯大林的工业化"),
          ("\\chref{ch:solow}用替代弹性低来读苏联的增长放缓，把激励的解释留了下来", "ch40_solow", "种种激励问题"),
          ("康托罗维奇说过，计划经济要分散决策，就得有一套合理的价格体系（\\chref{ch:soviet}）", "ch31_soviet",
           "计划经济要分散决策，就得有一套合理的价格体系"),
          ("统计能信多少，在\\chref{ch:datareliability}", "ch81_datareliability", "毛泽东时期和纳粹时期的统计能信多少"),
          ("毛泽东时期的统计能信多少，在\\chref{ch:datareliability}", "ch81_datareliability", "毛泽东时期"),
          ("苏联末期的货币过剩与价格放开，在\\chref{ch:transition}", "ch59_transition",
           "苏联末期的货币过剩与 1992 年价格放开后的高通胀"),
          ("转轨中的国有企业与银行怎样硬化预算约束，在\\chref{ch:transition}", "ch59_transition", "从计划到市场"),
          ("中国的信贷在\\chref{ch:chinacredit}", "ch72_chinacredit", "中国：信贷、资本管制与有管理的汇率"),
          ("公开的通胀走到极端是恶性通胀，在\\chref{ch:hyperinflation}", "ch52_hyperinflation", "恶性通胀怎样开始、怎样结束")]
# the chapters this one names, and where their labels are
LATER = {"ch:alternatives": "ch30_alternatives", "ch:chinacredit": "ch72_chinacredit",
         "ch:datareliability": "ch81_datareliability", "ch:eastasia": "ch42_eastasia", "ch:greekroman": "ch07_greekroman",
         "ch:hyperinflation": "ch52_hyperinflation", "ch:phillips": "ch38_phillips",
         "ch:reconstruction": "ch35_reconstruction", "ch:solow": "ch40_solow", "ch:soviet": "ch31_soviet",
         "ch:transition": "ch59_transition"}
# the chapters that point here
POINTERS = ("ch07_greekroman", "ch08_qinhan", "ch22_marx", "ch30_alternatives", "ch31_soviet", "ch35_reconstruction",
            "ch40_solow", "ch41_development", "ch59_transition", "ch81_datareliability")


def book(F, Q):
    """Life dates and what other chapters tell."""
    t = tex_text()
    for words, ((rb, ib), (rd, id_), head_row, head) in LIVES.items():
        assert words in t, words
        assert f"{F[rb][ib]:.0f}—{F[rd][id_]:.0f}" in words, (words, rb, rd)
        assert Q[head_row].startswith(head), (head_row, Q[head_row])             # the person of the record
        COVERED.append(words)
    # Kornai: the GND gives both years, the LoC heading none and its source note the birth ('b. 1-21-28')
    has("gnd_kornai", "2021 1928")
    assert Q["loc_kornai"] == Q["gnd_name"] == "Kornai, János"
    assert 1900 + F["loc_kornai_note"][2] == F["gnd_kornai"][1]
    assert t.count("生卒年未详") == 1 and "G. I. Popov，生卒年未详" in t
    for here, ch, there_ in EVENTS:
        assert here in t, here
        assert there_ in chapter(ch), (ch, there_)
    named = set(re.findall(r"\\chref\{(ch:[^}]+)\}", t)) | set(re.findall(r"\\nameref\{(ch:[^}]+)\}", t))
    assert named == set(LATER), sorted(named ^ set(LATER))
    for label, ch in LATER.items():
        assert f"\\label{{{label}}}" in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (label, ch)
    for ch in POINTERS:
        assert re.search(r"\\(?:chref|ref|nameref)\{ch:planned\}", chapter(ch)), ch
    print(f"ok {len(LIVES)} life dates, {len(EVENTS)} statements of other chapters, {len(LATER)} other chapters named")


# the bibliography item of each source of the snapshot (the authority records: loc43 and gnd43)
ITEM_OF = {"zv1962_43": "zv1962", "zv1962_43img": "zv1962", "lenkom43": "lenkom1962", "lenkomscan43": "lenkom1962",
           "lenkomscan43img": "lenkom1962", "frus1947_43": "frus1947", "frus1970_43": "frus1970",
           "frus1970b_43": "frus1970", "res1981_43": "res1981", "nbs50_43": "nbs1999", "nbs2000_43": "nbs2000",
           "nbsterms43": "nbs2000", "mqy2010_43": "mqy2010", "smil1999_43": "smil1999",
           "kornai1980_43img": "kornai1980", "kornai1986_43img": "kornai1986", "kmr2003_43": "kmr2003",
           "zv1965_43img": "zv1965", "wb1978_43": "worldbank1978yu", "wbland1978_43": "worldbank1978yu",
           "yusuf1977_43": "yusuf1977", "wblandyusuf43": "yusuf1977"}
# a third-party copy, read to verify only and never committed
VERIFY_ONLY = {"nbs1999": ("nbs50_43",)}


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
    return "、".join(out)


def printed(srcs) -> str:
    """The printed (Arabic) pages of the rows of these sources (their juan columns begin 'p. N' or 'pp. N-M')."""
    ps = []
    for r in _rows().itertuples():
        if r.file in srcs:
            m = re.match(r"pp?\. (\d+)(?:-(\d+))?\b", r.juan)
            if m:
                ps += range(int(m.group(1)), int(m.group(2) or m.group(1)) + 1)
    return runs(ps)


def pdf(srcs) -> str:
    """The PDF pages of the rows of these sources."""
    ps = []
    for r in _rows().itertuples():
        if r.file in srcs:
            for a, b in re.findall(r"PDF pp?\. (\d+)(?:-(\d+))?", r.juan):
                ps += range(int(a), int(b or a) + 1)
    return runs(ps)


def witnesses(F, Q):
    """Second witnesses of statements of the text, the licences and the bibliography block of the chapter."""
    # the Leningrad report: the transcription and the scan agree where the text uses them
    has("lk_scan", "ОТДЕЛА ПАРТИЙНЫХ ОРГАНОВ")
    has("lk_scan2", "ПОПОВУ Г.И.")
    has("lk_scan3", "Коммунизм нам не построить, рано стали Америку до")
    assert F["lk_scan_dates"] == F["lk_dates"]
    # the 1999 compilation and the 2000 yearbook agree (data_check); MQY's text and its table A8 agree on 1959
    assert F["mqy_38"][0] == round(F["a8_1959"][-1]) and F["mqy_32"][3] == F["a8_1958"][-1]
    assert F["a8_1959"][2] == -F["mqy_15"][0] / 100                               # the production growth of 1959
    # the licences
    m = meta()
    lic = m["license"]
    for rid in ("lk_archive", "lk_licence", "res_source", "res_copyright", "nbs_rights", "nbst_date", "mqy_copyright",
                "smil_copyright", "k80_copyright", "k86_copyright", "wb78_disclosure", "yu_disclosure", "wb78_restricted",
                "wb78_landing", "yu_landing", "gnd_licence"):
        assert re.search(r"\brows? [^)]*\b" + rid + r"\b", lic), rid
    for rid in ("lk_archive", "lk_licence", "res_source", "res_copyright", "nbs_rights", "nbst_reprint", "nbst_copyright",
                "nbst_fair", "nbst_data", "mqy_copyright", "smil_copyright", "k80_copyright", "k86_copyright",
                "wb78_restricted", "gnd_licence"):
        assert words_of(rid) in lic, rid
    assert "1259(6)" in lic and "17 U.S.C. § 105" in lic and "No photographs are used" in lic
    # the bibliography block of the chapter
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    start = bib.index("% ---- 第 43 章")
    following = re.search(r"^% ---- 第 \d+ 章", bib[start + 1:], re.MULTILINE)
    end = start + 1 + following.start() if following else bib.index("\\end{thebibliography}")
    block = bib[start:end]
    assert FETCH in block and bib.index("% ---- 第 42 章") < start
    items = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", block)}
    allitems = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", bib)}
    assert f"共 {len(items)} 条" in block
    unescape = lambda s: re.sub(r"\\([$%&_#~])", r"\1", s).replace("--", "-")     # noqa: E731 - as LaTeX prints it
    for rid, key in (("lk_licence", "lenkom1962"), ("lk_archive", "lenkom1962"), ("res_source", "res1981"),
                     ("res_copyright", "res1981"), ("nbs_rights", "nbs1999"), ("nbst_reprint", "nbs2000"),
                     ("nbst_data", "nbs2000"), ("mqy_copyright", "mqy2010"), ("smil_copyright", "smil1999"),
                     ("k80_copyright", "kornai1980"), ("k86_copyright", "kornai1986"), ("wb78_restricted", "worldbank1978yu"),
                     ("gnd_licence", "gnd43")):
        assert words_of(rid) in unescape(items[key]), (rid, key)
    for key in ("zv1962", "zv1965"):
        assert "1259 条第 6 款" in items[key], key
    assert "公有领域" in items["frus1947"] and "公有领域" in items["frus1970"] and "公共数据" in items["loc43"]
    assert "www.stats.gov.cn" in items["nbs2000"] and "引自国家统计局网站" in items["nbs2000"]
    for key, srcs in VERIFY_ONLY.items():
        assert "只用来核对" in items[key] and "不随本书分发" in items[key], key
    # every source of the snapshot is named by its URL and SHA-256 in its item (an image by its PDF)
    for key, s in m["sources"].items():
        item = "loc43" if key.startswith("loc_") else "gnd43" if key.startswith("gnd_") else ITEM_OF[key]
        assert unescape(s["url"]) in unescape(items[item]), key
        if not key.startswith(("loc_", "gnd_")):
            assert s["sha256"] in items[item], key
    # the pages of each work, as the snapshot's rows have them
    for key, srcs in (("mqy2010", ("mqy2010_43",)), ("kornai1980", ("kornai1980_43img",)),
                      ("kornai1986", ("kornai1986_43img",)), ("kmr2003", ("kmr2003_43",)),
                      ("worldbank1978yu", ("wb1978_43",)), ("yusuf1977", ("yusuf1977_43",))):
        assert f"第 {printed(srcs)} 页" in items[key] or printed(srcs) in items[key], (key, printed(srcs))
        assert f"PDF 第 {pdf(srcs)} 页" in items[key], (key, pdf(srcs))
    for words, (_, _, head_row, _) in LIVES.items():
        if head_row.startswith("loc_"):
            assert Q[head_row].replace("-", "--") in items["loc43"], head_row
    assert Q["loc_kornai_note"] in items["loc43"] and "115604685" in items["gnd43"]
    # the titles of the works as the documents print them
    for rid, key, words in (("k86_title", "kornai1986", "The Soft Budget Constraint"),
                            ("kmr_title", "kmr2003", "Understanding the Soft Budget Constraint"),
                            ("mqy_title", "mqy2010", "The Institutional Causes of China's Great Famine, 1959-61"),
                            ("smil_title", "smil1999", "China's great famine: 40 years later"),
                            ("wb78_number", "worldbank1978yu", "Report No. 1615a-YU"),
                            ("yu_title", "yusuf1977", "Understanding Self-Management in Yugoslavia")):
        has(rid, words)
        assert words in unescape(items[key]), (rid, key)
    # the Leningrad report: the department that signed it, and the scan's stamp
    has("lk_signature", "Зав. отделом парторганов горкома КПСС")
    has("lk_declassified", "рассекречено")
    keys = set(allitems)
    cited = {k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", tex_text()) for k in c.split(",")}
    assert cited <= keys, sorted(cited - keys)
    assert set(items) == cited, sorted(set(items) ^ cited)
    print(f"ok {len(cited)} works cited, {len(items)} in the bibliography block of Chapter 43")


def counts() -> None:
    """The editor's limits: “不能” at most about a dozen; the forbidden words; who decided and who paid stated; the three
    debates left open; the boxes."""
    t = tex_text()
    main_ = re.sub(r"\\begin\{deeper\}\[史料说明\].*?\\end\{deeper\}", "", t, flags=re.DOTALL)
    n = t.count("不能")
    print(f"ok “不能” {n} times")
    assert n <= 12, n
    for words in ("本书没有找到", "没能取得", "没有取得", "没有读到"):
        assert words not in main_, words                                          # only in the 史料说明
    narrative = re.sub(r"“[^”]*”", "", t)
    for bad in ("这一节回答", "不是因为", "而是", "详见", "\\textsc", "\\underline", "\\clearpage", "值得注意", "如前所述"):
        assert bad not in narrative, bad
    assert not re.search(r"(?<![意看])见\\(?:chref|secref|figref|tabref|exref|eqref)", t)
    # who decided and who paid
    for words in ("谁决定，谁承担，这里看得清楚", "定价的是党中央与部长会议", "付钱的是城里买肉的人（本书的概括）",
                  "决定补谁、税谁的是国家的各个机关，付账的是赚钱的企业（本书的概括）",
                  "决定的是毛泽东与中央，付出生命的主要是农村的人（本书的概括）",
                  "账就算到了决定涨价的人头上（本书的解读）", "两样都是让居民付账（本书的解读）"):
        assert words in main_, words
    # documents are not the subjects of sentences: the author is named
    for bad in ("报告说", "电报说", "备忘录说", "决议说", "呼吁书说", "汇报说", "论文说", "书里说", "表说"):
        assert bad not in main_, bad
    # at most one source frame (按……的说法、转述……) in a sentence
    frame = re.compile(r"按[^，。；“”]{0,40}?的(?:说法|转述|解释|估计|叙述|描述|判断|概括|统计|数|记录)")
    for s in re.split(r"(?<=[。？！])|\n", re.sub(r"“[^”]*”", "“”", main_)):
        assert len(frame.findall(s)) <= 1, s
    # the three debates are left open
    part = main_[main_.index("\\section{争论}"):main_.index("\\section{今天还剩什么}")]
    debates = part.split("\\subsubsection{")[1:]
    assert len(debates) == 3
    for d in debates:
        assert d.rstrip().endswith("至今没有定论。"), d[-80:]
    # the inferences are marked
    assert main_.count("本书的解读") >= 8 and main_.count("本书的计算") >= 10 and "本书的概括" in main_ \
        and "本书的推导" in main_ and "本书的核对" in main_, main_.count("本书的解读")
    # sentences: one semicolon at most (a table's list of sources is not a sentence)
    prose = re.sub(r"\\datasource\{[^\n]*", "", main_)
    for s in re.split(r"(?<=[。？！])|\n", re.sub(r"“[^”]*”", "“”", prose)):
        assert s.count("；") <= 1, s
    # the boxes the editor asks for
    assert t.count("\\begin{compare}") == 2 and t.count("\\begin{case}") == 1 and t.count("\\begin{pitfall}") == 1
    assert t.count("\\begin{deeper}[史料说明]") == 1 and t.count("\\begin{keyeq}") == 3
    assert "\\begin{compare}{公开通胀与被压抑的通胀}" not in t                     # Chapter 30's box
    assert t.count(GUIDE) == 2
    # the neighbours' topics: a clause or a sentence each
    for label in ("ch:transition", "ch:hyperinflation", "ch:chinacredit", "ch:phillips"):
        assert t.count(f"\\chref{{{label}}}") <= 2, label
    # Novocherkassk: no toll, and only in the 史料说明
    assert "新切尔卡斯克" not in main_


def main() -> None:
    df = _rows()
    F, Y, Q = facts(), years(), quotes()
    check_readings(df)
    check_text(df)
    for part in (guide, opening, world, shortage, china, reform, data_check, debate, deeper, legacy, takeaways,
                 selfcheck, ending):
        part(F, Y, Q)
    models()
    figures_data()
    book(F, Q)
    witnesses(F, Q)
    counts()
    coverage()
    anchors(str(TEX), set(df["id"]), script=Path(__file__))


if __name__ == "__main__":
    main()
