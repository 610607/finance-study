"""Chapter 39 (消费与投资理论): every number and every quotation in zh/ch39_consumption.tex.

    python3 checks/check_ch39.py

Inputs:
  consumption_facts             quotations of the chapter's sources with their page: Ford's address and the Tax
                                Reduction Act of 1975 (Statutes at Large, vol. 89); the Economic Report of the President
                                of January 1962 (reused from Chapter 38); Friedman's A Theory of the Consumption Function
                                (NBER 1957) and Kuznets's Uses of National Income in Peace and War (NBER 1942);
                                Modigliani's (1985) and Tobin's (1981) Nobel lectures and the Nobel pages; Hall (JPE 1978)
                                and Hall and Jorgenson (AER 1967), the scans on Hall's Stanford page, and Modigliani and
                                Steindel (BPEA 1977), read on the page images; Blinder (JPE 1981, the reprint NBER posts);
                                the NBER working papers of Johnson, Parker and Souleles (2004), Parker et al. (2011),
                                Fazzari, Hubbard and Petersen (1987), Kaplan and Zingales (2000) and Horioka (2024);
                                Hayashi (NBER Macroeconomics Annual 1986); the terms of Brookings, ESRI, the Cabinet
                                Office and the Digital Agency (PDL 1.0); the authority records of the Library of Congress
                                and the GND. data/fetch/verify_web_quotes.py checks the quotations against the documents;
                                the rows with an empty quotation are read on page images, with a transcription between «
                                and » in the note; data/fetch/consumption39.py fetches the documents
  esri_household_saving_1955_2024
                                Japan's household saving rate and real growth: ESRI's 1998 annual report (1990 base,
                                68SNA; 1955-1998) and its 2024 annual report (2020 base, 2008SNA; 1994-2024), read
                                from the workbooks by the same script

This script

1. reads the numbers of every row from its quotation (or from the transcription of a page image) by the rules of
   READINGS and compares them with the value column; the misreadings of the text layers are listed in MISPRINTS;
2. finds every “…” of the text among the renderings of TRANSLATIONS, and the words of the source each one renders
   (KEYWORDS) in the row; the quotations of copyrighted works stay short (FREE names the public-domain rows);
3. checks each number of the text with said(): the phrase is in the text and each number is the value of a row, a
   teaching input, or arithmetic on them (the life-cycle budget eq:consumption-lifecycle, Friedman's c = k y_p
   eq:consumption-permanent, Hall's Euler equation eq:consumption-euler, the user cost of capital
   eq:consumption-usercost, Tobin's q eq:consumption-q, Kuznets's Table 2, the rebates of 1975, 2001 and 2008, the
   Japanese series); every Arabic number of the text must lie in a phrase said() read (coverage());
4. checks the key equations as printed, the life cycle, the Euler equation and the user cost on random numbers, the
   data of the figures (figsrc/fig_ch39.py imports lifecycle_path(), growth_curve(), windfall_paths(), rebate_bars()
   and esri() from here), the life dates against the authority records, what other chapters tell, the licences and
   the bibliography block of Chapter 39, and the editor's limits;
5. lists the rows no "% 据:" anchor of the text names (common.anchors).

Set CH39_TEX to a scratch copy of the chapter to run the checks on it (mutation tests).
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

TEX = Path(os.environ.get("CH39_TEX", ROOT / "zh" / "ch39_consumption.tex"))   # a scratch copy for mutation tests
GUIDE = "政府一次性发钱，人们会花掉多少？企业凭什么决定投资？"
PREV = GUIDE                                        # Chapter 38's NEXT
NEXT = "长期增长为什么不能只靠多储蓄？"                  # Chapter 40's question
MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"], 1)}
FETCH = "data/fetch/consumption39.py"
# works of the bibliography that other chapters' blocks hold and this chapter cites unchanged
REUSED_KEYS = {"erp1962"}
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
    df, m = load_snapshot("consumption_facts", dtype=str, keep_default_na=False)
    assert 39 in m["used_in"] and m["fetch"] == FETCH
    assert df["id"].is_unique
    return df


@lru_cache(maxsize=None)
def meta() -> dict:
    return load_snapshot("consumption_facts")[1]


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
    return MONTHS[name.lower().rstrip(".")] if name.lower().rstrip(".") in MONTHS else \
        [i for m, i in MONTHS.items() if m.startswith(name.lower().rstrip("."))][0]


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
WORDS = {"one-seventh": 1 / 7, "one-fourth": 1 / 4, "one-third": 1 / 3, "two-thirds": 2 / 3, "third": 1 / 3,
         "sixth": 6}


def cardinal(s: str) -> float:
    """An English cardinal: 'three', 'Eleven', 'twenty-five'."""
    return float(sum(SMALL.get(w, 0) + TENS.get(w, 0) for w in s.lower().replace("-", " ").split()))


def figure(s: str) -> float:
    """'1,000', '30.5', '.28'."""
    return float(s.replace(",", ""))


def lfrac(s: str) -> float:
    """A fraction whose 1 the text layer reads as 'l': '3 l/4' -> 3.25, '4 l/3' -> 4.333..."""
    whole, part = s.split()
    n, d = part.replace("l", "1").split("/")
    return int(whole) + int(n) / int(d)


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
IMG_FIGURES = re.compile(r"(-?)(\d[\d,]*(?:\.\d+)?|\.\d+)")
HOW = {"num": figure, "en": cardinal, "word": lambda w: WORDS[w], "lfrac": lfrac}
SEVERAL: dict = {}
# id -> [(phrase, how)], in order. A phrase 'context|word' is searched as a whole and read from `word`. Rows not
# listed are read with all the figures of the quotation (a page image: of the transcription, with its signs). An empty
# list: the row prints no number of the story.
READINGS: dict[str, list[tuple[str, str]]] = {
    # Ford, the Act, the Economic Report of 1962
    "ford_request": [("|Eleven", "en"), ("simple $|16", "num")],
    "ford_note": [], "ford_note_law": [("H.R. |2166", "num"), ("Law |94", "num"), ("-|12", "num")],
    "erp_six": [("and (|6", "num")],
    # Friedman (1957)
    "fr_title": [("Publication Date: |1957", "num")],
    "fr_typescript": [("a |four", "en"), ("June |8", "num"), (", |1951", "num")],
    "fr_twokinds": [("from |two", "en")],
    "fr_payday2": [("that |one-seventh", "word")],
    "fr_horizon": [("about |three", "en")],
    # Kuznets (1942)
    "ku_t2_head": [("TABLE |2", "num"), ("Decades, |1879", "num"), ("–|1938", "num"), ("; |1929", "num")],
    # Modigliani (1985)
    "md_three": [("the '|40", "num"), ("s |three", "en")],
    "md_purpose": [("Fisher [|1930", "num")],
    "md_numbers": [("ρ = |2", "num"), ("w = |4", "num"), ("s = |8", "num"), ("ρ = |4", "num"), ("w = |3 l/4", "lfrac"),
                   ("s = |13", "num")],
    "md_three_pct": [("ratio, |4", "num"), ("to |5", "num"), ("a |3", "num"), ("namely |4 l/3", "lfrac"),
                     ("and |13", "num")],
    "md_wealth_series": [("early |60", "num"), ("Solow [|1963", "num"), ("Modigliani [ |1963", "num")],
    # Hall (1978), Hall and Jorgenson (1967)
    "ha_issue": [("Economy, |1978", "num"), ("vol. |86", "num"), ("no. |6", "num"), ("© |1978", "num")],
    "ha_lags": [("zero is |1.7", "num"), ("of |2.7", "num"), ("the |5", "num")],
    "ha_exclusion": [("is |0.1", "num"), ("F of |3.9", "num")],
    "ha_lags4": [("all |four", "en"), ("is |2.0", "num"), ("of |2.4", "num"), ("the |5", "num")],
    "to_dk": [],
    "hj_credit7": [("during |1962", "num"), ("a |seven", "en"), ("Act of |1962", "num")],
    "hj_1964": [("In |1964", "num"), ("around |ten", "en")],
    # Modigliani and Steindel (1977), Blinder (1981)
    "ms_fourth": [("(row |4", "num"), ("than |one-fourth", "word"), ("first |three", "en"), ("to |one-third", "word")],
    "ms_sixth": [("the |sixth", "word")],
    "ms_models": [("the |1975", "num"), ("on |three", "en"), ("and |one", "en")],
    "ms_three": [("one of |three", "en")],
    "bl_jpe": [("Economy, |1981", "num"), ("vol. |89", "num"), ("no. |1", "num")],
    # Johnson, Parker and Souleles (2004); Parker et al. (2011)
    "jps_mailed": [("typically $|300", "num"), ("or $|600", "num"), ("about |two-thirds", "word"), ("a |ten", "en"),
                   ("September, |2001", "num")],
    "jps_spent": [("about |20", "num"), ("-|40", "num"), ("the |three", "en"), ("another |third", "word"),
                  ("subsequent |three", "en")],
    "jps_twothirds": [("Roughly |two-thirds", "word"), ("subsequent |three", "en")],
    "pa_phase": [("by |five", "en"), ("$|75,000", "num"), ("$|150,000", "num")],
    "pa_digits": [("final |two", "en")],
    # Hayashi (1986), Horioka (2024)
    "hy_title": [("Annual |1986", "num"), ("Volume |1", "num"), ("(p. |147", "num"), (" - |234", "num")],
    "hy_simplistic": [("last |fifteen", "en"), ("in the |1960", "num")],
    "ho_t1_head": [],
    # the authority records
    "gnd_licence": [],
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
MISPRINTS = [("fr_postwar", "World War IL", "'IL' for 'II'"),
             ("fr_rise", "rate of use in", "'use' for 'rise'"),
             ("fr_define", "on bow", "'bow' for 'how'"),
             ("fr_keynes", "pro. portion", "'pro. portion' for 'proportion'"),
             ("fr_fn12", "FrancoModigliani", "'FrancoModigliani' without a space"),
             ("md_numbers", "3 l/4", "'3 l/4' for 3¼"),
             ("md_lit", "to lit the", "'lit' for 'fit'"),
             ("md_three_pct", "4 l/3", "'4 l/3' for 4⅓"),
             ("md_wealth_series", "[ 19631)", "'[ 19631)' for '[1963])'"),
             ("md_ref_steindel", "Pagers on Economics Activity", "'Pagers on Economics Activity' for 'Papers on "
                                                                  "Economic Activity'"),
             ("hy_accounting", "ol,served", "'ol,served' for 'observed'")]
LFRAC_ROWS = ("md_numbers", "md_three_pct")          # the fractions the rule 'lfrac' reads


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
    quoted("rows with values, each read from its quotation", n, 182)
    quoted("rows read on a page image (no quotation)", img, 124)
    Q, notes = quotes(), meta()["notes"]
    for rid, word, named in MISPRINTS:
        assert word in Q[rid], (rid, word)                                      # printed in the quotation
        k = notes.find(named)
        m = re.match(r"[^(]{0,80}\(([^)]*)\)", notes[k + len(named):]) if k >= 0 else None
        assert m and rid in re.split(r",\s*", m.group(1)), (rid, named)        # and named, with its row
    for rid in LFRAC_ROWS:
        assert any(how == "lfrac" for _, how in READINGS[rid]), rid
    assert "read by the rule 'lfrac' of checks/check_ch39.py" in notes
    # the source keys the chapter cites for its sources
    assert set(src) == set(df["file"]), sorted(set(src) ^ set(df["file"]))
    # the copies of the articles on third-party sites: address, date and hash recorded, the files not committed
    for key in ("hall1978img", "hj1967img", "blinder1981"):
        assert f"{key} {src[key]['url']} " in notes and src[key]["sha256"] in notes, key
    assert "not committed" in notes and "read to verify, not committed" in src["hall1978img"]["version"]
    # a key another snapshot holds names the same document
    for key, s in src.items():
        for name in ("phillips_facts",):
            other = load_snapshot(name)[1]["sources"]
            if key in other:
                assert other[key]["url"] == s["url"] and other[key]["sha256"] == s["sha256"], (name, key)


# ---------------------------------------------------------------------------------------------------
# Data of the text and the figures
@lru_cache(maxsize=None)
def esri() -> pd.DataFrame:
    """Japan's household saving rates and real growth rates on the two bases (ESRI's workbooks)."""
    df, m = load_snapshot("esri_household_saving_1955_2024")
    assert 39 in m["used_in"] and m["fetch"] == FETCH
    return df.set_index("year")


def compound(g: pd.Series) -> float:
    """The average yearly growth rate (%) of a run of yearly growth rates (%)."""
    return float(100 * (np.prod(1 + g.to_numpy() / 100) ** (1 / len(g)) - 1))


def stationary(L: float, N: float) -> dict[str, float]:
    """The stripped-down life cycle (eq:consumption-lifecycle with A_0 = 0, income 1 a year): consumption, saving,
    the wealth at retirement, and the wealth-income ratio of a stationary economy with one person of each age."""
    c = N / L
    peak = N * (1 - c)
    wealth = N * peak / 2 + (L - N) * peak / 2                         # two triangles
    return dict(c=c, save=1 - c, peak=peak, wealth=wealth, income=N, w=wealth / N,
                saving=N * (1 - c) - (L - N) * c)


def lifecycle_growth(n: float, L: float = 50, N: float = 40) -> dict[str, float]:
    """The same model when each cohort is larger than the one before by the rate n (continuous ages, cohort weight
    e^{-n a} at age a): the wealth-income ratio w and the aggregate saving rate s; s = n w (eq. (2) of the lecture)."""
    from scipy.integrate import quad
    c = N / L

    def A(a):                                       # wealth at age a
        return (1 - c) * a if a <= N else c * (L - a)
    Y = quad(lambda a: math.exp(-n * a), 0, N)[0]
    C = c * quad(lambda a: math.exp(-n * a), 0, L)[0]
    W = quad(lambda a: A(a) * math.exp(-n * a), 0, L, points=[N])[0]
    return dict(w=W / Y, s=(Y - C) / Y, sw=n * W / Y)


def usercost(q: float, r: float, d: float, u: float, z: float, k: float) -> float:
    """eq:consumption-usercost."""
    return q * (r + d) * (1 - k) * (1 - u * z) / (1 - u)


def euler2(y1: float, y2: float, r: float, delta: float) -> tuple[float, float]:
    """Two periods, log utility: c2 = (1 + r)/(1 + delta) c1 and the budget c1 + c2/(1 + r) = y1 + y2/(1 + r)."""
    pv = y1 + y2 / (1 + r)
    c1 = pv / (1 + 1 / (1 + delta))
    return c1, c1 * (1 + r) / (1 + delta)


def first_year(x: float, mpc: float, r: float, k: float, years: float) -> dict[str, float]:
    """ex:consumption-windfall: what a windfall x adds to the first year's consumption under the three rules."""
    return dict(keynes=mpc * x, pih=k * r * x, lch=x / years)


def rebate75(liability: float, agi: float) -> float:
    """The refund of 1974 taxes, section 6428 of the Act (a single return; a joint return counts as one individual):
    10 per cent of the liability, at least the lesser of the liability and $100, at most $200; the excess over that
    minimum shrinks in proportion to the adjusted gross income above $20,000, to nothing at $30,000."""
    F = facts()
    lo, hi, rate = F["pl_min"][3], F["pl_max"][0], F["pl_rebate"][0] / 100
    a, step = F["pl_phase"]
    minimum = min(liability, lo)
    amount = max(min(rate * liability, hi), minimum)
    return minimum + (amount - minimum) * (1 - min(max(agi - a, 0) / step, 1))


def eitc75(earned: float, agi: float | None = None) -> float:
    """The earned income credit of section 43 (1975): 10 per cent of the earned income up to $4,000, reduced (not
    below zero) by 10 per cent of the adjusted gross income (or, if greater, the earned income) above $4,000."""
    F = facts()
    pct, cap = F["pl_eitc"]
    agi = earned if agi is None else agi
    cut = F["pl_eitc_limit"][0] / 100 * max(max(agi, earned) - F["pl_eitc_limit2"][0], 0)
    return max(pct / 100 * min(earned, cap) - cut, 0)


# ---------------------------------------------------------------------------------------------------
# 2. Every “…” of the text against the snapshot
# the chapter's Chinese renderings of the quotations: rendering -> row (or rows)
TRANSLATIONS = {
    "足以帮助购买新汽车、家用电器或其他改善": "ford_refund",
    "所有商人和农民": "ford_credits",
    "数以百万计的中等收入纳税人": "ford_middle",
    "严重的证据冲突": "fr_conflict",
    "极其简单": "md_three",
    "永久的": "md_reid",
    "精简版": "md_stripped",
    "几乎违反直觉": "md_prop_intro",
    "共同的学术环境": "fr_common",
    "高度试探性": "fr_tentative",
    "挥霍": "fr_windfall",
    "简化": "md_pih",
    "截然相反": "md_opposite",
    "这些提案的核心，是对可折旧的机器设备的总投资给予 8\\% 的税收抵免。": "erp_centerpiece",
    "信条": "hj_faith",
    "相当惊人": "hj_startling",
    "永久税": "ms_dichotomy",
    "强有力但并不一致的证据": "ms_conclusion",
    "过度敏感": "fhp_excess",
    # the misreadings of the text layers quoted in the 史料说明
    "IL": "fr_postwar",
    "use": "fr_rise",
    "bow": "fr_define",
    "3 l/4": "md_numbers",
    "lit": "md_lit",
}
# the words of the source each rendering renders, in the quotation (or the transcription of the page image)
KEYWORDS = {
    "ford_refund": ["enough to assist in the purchase of new cars, home appliances, or other improvements"],
    "ford_credits": ["all businessmen and farmers"],
    "ford_middle": ["the millions of middle-income taxpayers"],
    "fr_conflict": ["a serious conflict of evidence"],
    "md_three": ["extraordinarily simple"],
    "md_reid": ["'permanent'"],
    "md_stripped": ['"stripped down"'],
    "md_prop_intro": ["almost counter intuitive"],
    "fr_common": ["a common intellectual environment"],
    "fr_tentative": ["a highly tentative conclusion"],
    "fr_windfall": ['"riotous living,"'],
    "md_pih": ['"simplifying"'],
    "md_opposite": ["diametrically opposite"],
    "erp_centerpiece": ["The centerpiece of these proposals is the 8 percent tax credit against tax for gross investment "
                        "in depreciable machinery and equipment."],
    "hj_faith": ["an article of faith"],
    "hj_startling": ["quite startling"],
    "ms_dichotomy": ["“permanent tax” equation"],
    "ms_conclusion": ["strong, though not uniform, evidence"],
    "fhp_excess": ['"excess sensitivity"'],
    "fr_postwar": ["World War IL"],
    "fr_rise": ["rate of use in income"],
    "fr_define": ["on bow"],
    "md_numbers": ["3 l/4"],
    "md_lit": ["to lit the"],
}
# the sources that may be quoted at length: the works of the United States government (Ford's address, the Act, the
# Economic Report of 1962)
FREE = ("ford_", "pl_", "erp_")


def tex_text() -> str:
    return "\n".join(l for l in TEX.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("%"))


def text_quotations() -> list[str]:
    """The “…” of the text; the closing question is Chapter 40's and the chapter's own question is in the guide and at
    the end of the opening (both checked by guide() and opening())."""
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 40's question"
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
    for q in ("IL", "use", "bow", "3 l/4", "lit"):
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
LC = (50, 40)                        # ex:consumption-lifecycle: a life of L = 50 years, N = 40 of them at work
LC_N = 0.02                          # ex:consumption-lifecycle (4): population growth
LC_N2 = 0.04
KU_ROWS = ("ku_t2_1879", "ku_t2_1884", "ku_t2_1889", "ku_t2_1894", "ku_t2_1899", "ku_t2_1904", "ku_t2_1909",
           "ku_t2_1914", "ku_t2_1919", "ku_t2_1924", "ku_t2_1929")       # Kuznets (1942) Table 2, decade by decade
HO_ROWS = ("ho_t1_1955", "ho_t1_1961", "ho_t1_1963", "ho_t1_1967", "ho_t1_1974", "ho_t1_1976", "ho_t1_1986",
           "ho_t1_1994", "ho_t1_1995", "ho_t1_1996", "ho_t1_1997", "ho_t1_1998", "ho_t1_2014", "ho_t1_2020",
           "ho_t1_2024")                                                  # Horioka (2024) Table S-1, the years used
WINDFALL = 200                       # ex:consumption-windfall: the dollars of the rebate (the Act's maximum)
MPC = 0.6                            # Chapter 32's teaching marginal propensity to consume
RATE = 0.03                          # the rate of interest of the permanent-income rule
K_PIH = 0.9                          # k, the lower bound of Friedman's range for wage earners
YEARS_LEFT = (40, 10)                # the years left to live of the life-cycle rule: a head of household, a retiree
QUARTER = 4                          # ex:consumption-mpc: a quarter is a fourth of a year
EULER = dict(y=100, r=0.05, delta=0.05, extra=10)    # ex:consumption-euler
UC = dict(q=1, r=0.10, d=0.15, u=0.5, z=0.6)         # ex:consumption-usercost
SC_LC = (60, 45)                     # self-check 1
SC_REBATE, SC_YEARS = 600, 30        # self-check 2
SC_R, SC_DELTA = 0.04, 0.02          # self-check 3
SC_K = (0.07, 0.10)                  # self-check 4: the credit of 1962 and that of 1975


def kuznets() -> dict[int, list[float]]:
    """Kuznets's Table 2, by the first year of the decade: [first, last, NNP, NCF, share, NNP, NCF, share] (current
    prices, then 1929 prices; millions of dollars a year). The decades begin every five years and overlap."""
    F = facts()
    out = {}
    assert [f"ku_t2_{y}" for y in range(1879, 1930, 5)] == list(KU_ROWS)
    for y in range(1879, 1930, 5):
        v = F[f"ku_t2_{y}"]
        assert v[0] == y and v[1] == y + 9, y
        assert abs(100 * v[3] / v[2] - v[4]) < 0.051 and abs(100 * v[6] / v[5] - v[7]) < 0.051, y   # the shares
        out[y] = v
    return out


def table6() -> tuple[list[float], list[float]]:
    """Modigliani and Steindel's Table 6: the rebate spent, cumulated, per cent, 1975:2 to 1976:3, without and with the
    correction for autocorrelation (rows 3 and 4)."""
    v = facts()["ms_table6"]
    assert v[:6] == [6, 1975, 1975, 1, 1976, 3] and v[6] == 3 and v[13] == 4
    raw, corr = v[7:13], v[14:20]
    assert all(np.diff(raw) > 0) and all(np.diff(corr) > 0)
    return raw, corr


def lifecycle_path(L: float = 50, N: float = 40, n: int = 501) -> pd.DataFrame:
    """fig:consumption_lifecycle (a): income, consumption and wealth by age in the stripped-down model."""
    a = np.linspace(0, L, n)
    c = N / L
    return pd.DataFrame(dict(age=a, income=np.where(a < N, 1.0, 0.0), consumption=c,
                             wealth=np.where(a <= N, (1 - c) * a, c * (L - a))))


def growth_curve(rates=None) -> pd.DataFrame:
    """fig:consumption_lifecycle (b): the aggregate saving rate of the stripped-down model against population growth."""
    rates = np.linspace(0, 0.05, 26) if rates is None else rates
    return pd.DataFrame([dict(n=n, w=g["w"], s=g["s"]) for n in rates for g in [lifecycle_growth(n)]])


def windfall_paths(years: int = 40) -> pd.DataFrame:
    """fig:consumption_windfall (a): the share of a windfall spent, cumulated, year by year, under the rules of
    ex:consumption-windfall (Keynes: the first year only; the permanent-income rule: the interest, k r, every year; the
    life cycle: x / (years left) a year until it is spent)."""
    t = np.arange(0, years + 1)
    R = first_year(1.0, MPC, RATE, K_PIH, YEARS_LEFT[0])
    return pd.DataFrame(dict(year=t, keynes=np.where(t >= 1, R["keynes"], 0.0), pih=R["pih"] * t,
                             lch=np.minimum(t / YEARS_LEFT[0], 1.0), retiree=np.minimum(t / YEARS_LEFT[1], 1.0)))


def rebate_bars() -> dict:
    """fig:consumption_windfall (b): the estimates of the share spent in the three months of receipt (per cent), and
    the three rules' first quarter (ex:consumption-mpc)."""
    F = facts()
    x = F["jps_typical"][0]
    R = first_year(x, MPC, RATE, K_PIH, YEARS_LEFT[0])
    return dict(bars=[("2001 nondurables", *F["jps_spent"][:2]), ("2008 nondurables", *F["pa_spent"][:2]),
                      ("2008 total", *F["pa_spent"][2:4])],
                rules=dict(keynes=100 * MPC, pih=100 * R["pih"] / QUARTER / x, lch=100 * R["lch"] / QUARTER / x))


# ---------------------------------------------------------------------------------------------------
# 4. Numbers, section by section
def guide(F, Y, Q):
    t = TEX.read_text(encoding="utf-8")
    assert f"\\guidequestion{{{GUIDE}}}" in t and GUIDE == PREV
    assert chapter("ch38_phillips").rstrip().endswith(PREV)                     # 第 38 章交来的问题
    assert ("\\guideprereq{\\chref{ch:generaltheory}\\enspace\\nameref{ch:generaltheory}；"
            "\\chref{ch:prices}\\enspace\\nameref{ch:prices}}") in t
    said("用欧拉方程说明跨期消费平滑，以及霍尔（1978）的随机游走含义", F["ha_issue"][0])
    said("推导资本的使用成本与霍尔—乔根森（1967）的投资模型", F["hp_hj"][0])
    assert "\\chapterstub" not in t


def opening(F, Y, Q):
    y75, day, _ = F["ford_title"]
    h, m = F["ford_time"]
    has("ford_time", "p.m.", "from the Oval Office at the White House")
    said("1975 年 3 月 29 日晚上 7 点半刚过", y75, mon("ford_title", "March"), day, h)
    assert 30 < m < 40                                                           # 7:31 p.m.
    has("ford_broadcast", "broadcast live on radio and television")
    say("在白宫椭圆形办公室发表了一篇电台与电视直播的讲话")
    (hr,) = F["ford_signed"]
    assert F["ford_note_law"] == [hr, 94, 12] and F["pl_header"][:2] == [94, 12] and F["pl_header"][-1] == hr
    has("ford_note_law", "(89 Stat. 26)")
    said("他签署了国会送来的 H.R. 2166，即《1975 年减税法》", hr, F["pl_title"][0])
    weeks, bn = F["ford_request"]
    has("ford_request", "in mid-January", "the new Congress", "as its first priority", "Federal income taxes")
    said("他说，11 周以前，他请新国会先通过一项简单的减税，把联邦所得税减少 160 亿美元", weeks, bn * 1e9)
    y74, cap = F["ford_refund"]
    has("ford_refund", "a one-time refund to individual 1974 taxpayers")
    said("他要的是给 1974 年的个人纳税人一次性退税，每人最多 1,000 美元", y74, cap)
    has("ford_credits", "bigger investment credits", "expand and make more jobs")
    say("他还要更大的投资抵免，即让企业按买进新设备的价款的一定比例抵减所得税（本书的解读）")
    has("ford_jobs", "my main concern")
    has("ford_temporary", "temporary tax incentives to charge up our free enterprise system",
        "not by government handouts and make-work programs")
    # what Congress gave
    lo, hi = F["ford_compromise"]
    (total,) = F["ford_within"]
    said("减税总额 230 亿美元，介于他 1 月提出的 160 亿与参议院通过的 320 亿之间", total * 1e9,
         mon("ford_compromise", "January"), lo * 1e9, hi * 1e9)
    assert lo == bn and lo < total < hi
    has("ford_within", "within reason")
    said("按这项法律，每个纳税人退还 1974 年所得税的 10\\%，夫妇合并申报的算作一个人", F["pl_refund_title"][0],
         F["pl_rebate"][0])
    has("pl_rebate", "10 percent of the amount of his liability for tax")
    has("pl_joint", "joint return", "both spouses shall be treated as one individual")       # per return, not per person
    has("pl_refund_title", "REFUND OF 1974 INDIVIDUAL INCOME TAXES")
    mn = F["pl_min"][3]
    has("pl_min", "shall not be less than the lesser of", "the amount of the taxpayer's liability for tax")
    said("退款不少于 100 美元，税额不到 100 美元的就全部退还，退款至多 200 美元", mn, mn, F["pl_max"][0])
    a, step = F["pl_phase"]
    has("pl_excess", "the applicable minimum payment")
    has("pl_phase", "(but not below zero)", "adjusted gross income for the taxable year in excess of $20,000")
    said("调整后总收入超过 2 万美元的，退款高出最低额的部分按比例递减", a)
    said("到 3 万美元，退款只剩 100 美元，收入再高也是这个数（本书的计算）", a + step, rebate75(10 ** 4, a + step))
    assert rebate75(10 ** 4, a + step) == rebate75(10 ** 4, 10 ** 5) == mn                # the minimum from $30,000 on
    assert rebate75(2000, a + step / 2) == mn + (F["pl_max"][0] - mn) / 2                  # half way down at $25,000
    assert rebate75(60, 5000) == 60 and rebate75(800, 9000) == mn and rebate75(1500, 15000) == 150
    has("pl_50", "for the month of March, 1975", "monthly insurance benefit payable under title II of the Social "
        "Security Act", "Railroad Retirement Act", "supplemental security income")
    has("pl_50once", "only one such $50 payment")
    said("1975 年 3 月领取社会保障、铁路退休金或补充保障收入的人，每人另得 50 美元，领几种也只得一份", F["pl_50"][2],
         mon("pl_50", "March"), F["pl_50"][1])
    assert F["pl_50once"][-1] == F["pl_50"][1]
    has("pl_credit7", "7 percent of the qualified investment")
    said("企业的投资抵免，按这项法律一般是 7\\%", F["pl_credit7"][1])
    T = F["pl_transition"]
    has("pl_transition", "after January 21, 1975", "and before January 1, 1977", "acquired by the taxpayer",
        "construction, reconstruction, or erection")
    has("pl_credit10", "10 percent of the qualified investment")
    said("1975 年 1 月 21 日以后到 1977 年以前购置或建造的资产，抵免提到 10\\%", T[1], mon("pl_transition", "January"),
         T[0], T[5], F["pl_credit10"][0])
    assert T[4] == 1                                                             # before January 1, 1977
    # who receives it, who pays
    say("钱发给谁、由谁来付，国会写进了法律，福特也在讲话里说了")
    said("退税按 1974 年交的所得税算，那一年不交所得税的人拿不到退税，领上面三种给付的人不论交没交税，都另有 50 美元（本书的解读）",
         F["pl_refund_title"][0], F["pl_50"][1])
    # the earned income credit of section 204: 10 per cent of earned income up to $4,000, less 10 per cent of the
    # income above $4,000, refunded where it exceeds the tax, for 1975 only (section 209 (b))
    has("pl_eitc_title", "CREDIT FOR CERTAIN EARNED INCOME")
    sec, _, y74e = F["pl_eitc_year"]
    pct, cap = F["pl_eitc"]
    assert sec == 204 and y74e == F["pl_refund_title"][0] and F["pl_eitc_limit"] == [pct] and F["pl_eitc_limit2"] == [cap]
    has("pl_eitc", "of the earned income for the taxable year as does not exceed")
    has("pl_eitc_limit", "of the adjusted gross income")
    has("pl_eitc_child", "a child of that individual")
    has("pl_eitc_refund", "CREDIT EXCEEDS LIABILITY FOR TAX")
    has("pl_eitc_year", "taxable years beginning after December 31, 1974")
    said("法律还为 1975 年度新设了劳动所得抵免，家里养着孩子的劳动者按劳动收入的 10\\% 抵税，收入只算到 4,000 美元，再高就递减",
         y74e + 1, pct, cap)
    say("抵免超过应交税款的差额照样退还，没有交税的低收入家庭因此也能拿到（本书的解读）")
    assert eitc75(cap) == pct / 100 * cap and eitc75(2 * cap) == 0 and eitc75(cap / 2) == pct / 100 * cap / 2
    has("ford_middle", "fails to give adequate tax relief", "who already contribute the biggest share of Federal taxes")
    say("联邦税的最大份额本来就是他们交的")
    (more,) = F["ford_more7"]
    fy, deficit = F["ford_deficit60"]
    has("ford_deficit60", "fiscal year 1976 deficit", "and other changes")
    said("他说，减税比他提的多了约 70 亿美元，加上其他变化，1976 财年的联邦赤字估计会到约 600 亿美元", more * 1e9, fy,
         deficit * 1e9)
    assert total - lo == more
    say("退出去的钱眼下是政府借来的，将来要由纳税人偿还（本书的解读）")
    # Chapter 38's Model I
    c0, cp, cp1, cw = their("phillips_facts", "kl_est_c")
    said("消费是工资总额的 0.80 倍，再加当年与上年利润的 0.02 倍与 0.23 倍（\\secref{sec:phillips-models}）", cw, cp, cp1)
    _, ip, ip1, ik = their("phillips_facts", "kl_est_i")
    assert ip > 0 and ip1 > 0 and ik < 0
    say("投资随利润与资本存量变，乘数与周期都从这两个方程来")
    assert paragraph("福特设想").endswith(GUIDE)                                   # the opening ends with the question


def world(F, Y, Q):
    has("fr_keynes", "saved as real income increases")
    say("照弗里德曼引的凯恩斯的话，实际收入增加时，收入里储蓄的比例更大")
    said("教学例子里边际消费倾向取 0.6，乘数是 2.5（\\exref{ex:generaltheory-cross}）", MPC, 1 / (1 - MPC))
    said("只要$a>0$，收入越高，储蓄占收入的比例就越高", 0)
    # Friedman's review
    said("1957 年回顾，消费函数是用两类数据估计的", F["fr_title"][0])
    chk("    two kinds of data (两类)", told("消费函数是用两类数据估计的", "是用", "类"), F["fr_twokinds"][0])
    has("fr_twokinds", "time series on consumption")
    has("fr_budget", "budget data")
    has("fr_confirm", "seemed at first to confirm Keynes's hypothesis")
    has("fr_mpc", "highly correlated with income", "less than unity", "less than the average propensity")
    said("边际消费倾向小于 1，也小于平均消费倾向", 1)
    has("fr_conflict", "a serious conflict of evidence arose")
    has("fr_kuznets1", "made by Kuznets", "no rise in the percentage")
    has("fr_kuznets2", "during the past half-century despite a substantial rise in real income")
    said("对美国 1899 年以来储蓄的估计显示，半个世纪里实际收入大幅增加，储蓄的比例却没有上升", F["fr_kuznets1"][0])
    has("fr_postwar", "sharply lower", "in the interwar period")
    # Kuznets (1942)
    said("1942 年他在美国国民经济研究局（NBER）的报告里，按十年一段", F["ku_date"][0])
    assert F["ku_paper"] == [6, F["ku_date"][0]]
    has("ku_decades", "relate to decades")
    has("ku_two", "Net capital formation is one component of the net national product", "the other is consumers' outlay")
    has("ku_durables", "includes residential construction", "passenger cars, furniture")
    K = kuznets()
    shares = [K[y][7] for y in range(1879, 1920, 5)]
    said("按 1929 年价格，从 1879—1888 年到 1919—1928 年，净国民产值增加到约 4.5 倍，资本形成的份额却在 10\\% 到 15\\% 之间起落",
         F["ku_t2_head"][3], 1879, 1888, 1919, 1928, K[1919][5] / K[1879][5], min(shares), max(shares))
    assert 10 <= min(shares) and max(shares) <= 15
    has("ku_why", "did not the propensity to consume weaken and that to save become stronger")
    has("ku_stable", "secular stability")
    # the table
    has("ku_t2_head", "per Year, by Decades, 1879–1938", "in millions of dollars", "1929 PRICES")
    said("\\caption{库兹涅茨的十年平均：美国的净国民产值与净资本形成，1879—1938 年}", *F["ku_t2_head"][1:3])
    say("十年 & 净国民产值 & 净资本形成 & 份额（\\%） & 当年价格的份额（\\%）")
    said("前三列按 1929 年价格，份额是净资本形成占净国民产值的比例", F["ku_t2_head"][3])
    for y in range(1879, 1930, 10):                                              # every other row of the table
        v = K[y]
        said(f"{v[0]:.0f}—{v[1]:.0f} & {v[5]:,.0f} & {v[6]:,.0f} & {v[7]:.1f} & {v[4]:.1f} \\\\", v[0], v[1], v[5],
             v[6], v[7], v[4])
    said("\\datasource{库兹涅茨（1942）表 2，每年的平均数，百万美元。", F["ku_date"][0], F["ku_t2_head"][0])
    say("原表每五年起一段、十年相叠，这里每隔一行取一行。}")
    # Modigliani's lecture
    said("大萧条的十年里，这个份额才跌到 2.3\\%", K[1929][7])
    assert K[1929][7] == min(v[7] for v in K.values())
    said("1985 年在诺贝尔奖演讲里回顾了这段历史", F["md_lecture"][1])
    forty, three = F["md_three"]
    has("md_three", "In the second half of the '40s", "dealt a fatal blow")
    said("他说，1940 年代后半期的三项经验研究", 1900 + forty)
    chk("    three contributions (三项)", told("1940 年代后半期的三项经验研究", "后半期的", "项"), three)
    has("md_kuznets", "since the middle of the 19th century, despite the large rise in per capita income")
    say("第一项就是上面库兹涅茨等人的证据")
    has("fr_brady_fn", "Dorothy S. Brady and Rose D. Friedman")
    has("fr_brady", "depends not on its absolute income but on its position in the distribution of income")  # 2nd witness
    has("md_brady", "a reconciliation of Kuznets' results with budget study evidence")
    said("第二项是 Dorothy Brady 与 Rose Friedman（1947）的研究", F["md_brady"][0])
    has("md_relative", "relative to overall mean income")
    has("md_reid", "Margaret Reid [not published]", "normal or 'permanent', rather than current, income")
    has("md_inspiration", "both for the Life Cycle and for the roughly contemporaneous Permanent Income Hypothesis")


def lifecycle(F, Y, Q):
    a, b, c, d = F["md_essays"]
    has("md_essays", "Richard Brumberg and I wrote two essays", "Cross Section Data", "Aggregate Consumption Function")
    said("据莫迪利亚尼 1985 年的回顾，1952—1954 年，他与布伦伯格（Richard Brumberg，生卒年未详）写了两篇论文",
         F["md_lecture"][1], a, b)
    chk("    two essays (两篇)", told("写了两篇论文", "写了", "篇"), 2)
    said("一篇讲横截面数据，1954 年发表，一篇讲总量消费函数，到 1979 年才印出来", c, d)
    has("md_purpose", "rational, utility maximizing, consumers", "in the spirit of Irving Fisher")
    has("md_resources", "the present value of labor income plus bequests received")
    has("md_stripped", '"stripped down" version')
    has("md_assumptions", "income constant until retirement, zero thereafter; zero interest rate",
        "constant consumption over life, no bequests")
    has("md_hump", "humped-shaped age path of wealth holding")
    said("刚开始工作时$A_0=0$", 0)
    assert "C(T) = (N/L)Ȳ" in transcription("md_fig1") and "falling to zero at L" in column("note")["md_fig1"]
    said("这正是莫迪利亚尼图 1 里的那条消费线", F["md_fig1"][0])
    # the propositions
    has("md_prop_intro", "almost counter intuitive")
    chk("    six propositions (六条)", told("这个精简的模型推出六条命题", "推出", "条"), F["md_prop6"][0])
    has("md_prop1", "entirely independent of its per capita income")
    has("md_prop2", "not simply the result of differential thrift", "consistent with an identical individual")
    has("md_prop3", "the higher the long run growth rate of the economy. It will be zero for zero growth.")
    has("md_prop4", "a decreasing function of the growth rate, thus being largest at zero growth")
    has("md_prop5s", "even if no wealth is passed on by bequests")
    has("md_prop6", "the prevailing length of retirement")
    assert [F[f"md_prop{i}"][0] for i in (1, 2, 4, 6)] == [1, 2, 4, 6] and F["md_prop5s"] == [5]   # all six named
    say("各国储蓄率不同，未必因为国民节俭的程度不同，个人行为完全一样，国家的储蓄率也可以不一样",
        "财富收入比却随增长率提高而下降，零增长时最大", "即使不留遗产，一国也能积累起相对收入相当可观的财富")
    has("md_prop5", "without any appeal to the bequest process", "a quite radical departure from conventional wisdom")
    say("照这个数，不靠遗产，也差不多能解释美国的全部财富，他说这是对传统看法相当激进的背离")
    # the stationary economy and growth
    has("md_stationary", "just offsets the accumulation of the active population in view of retirement")
    has("md_single", "W/Y depends on a single parameter, the length of retirement")
    assert transcription("md_wy").startswith("W/Y = M/2")
    ten, five = F["md_ten"]
    said("他们取退休 10 年，财富是收入的 5 倍，与 Goldsmith 研究美国储蓄的初步估计相近", ten, five)
    chk("    W/Y = M/2 with M = 10", ten / 2, five)
    has("md_goldsmith", "preliminary estimates of Goldsmith's [1956] monumental study of U.S. savings")
    assert "s ≡ S/Y = (ΔW/W)(W/Y) = ρw" in transcription("md_growth_eq")
    say("经济增长时，储蓄率等于增长率乘以财富收入比")
    r2, w2, s2, r4, w4, s4 = F["md_numbers"]
    said("增长率 2\\% 时，财富收入比是 4，储蓄率是 8\\%", r2, w2, s2)
    said("增长率 4\\% 时，两者分别是 3.25 与 13\\%", r4, w4, s4)
    chk("    s = rho w at 2 per cent", r2 * w2, s2)
    chk("    s = rho w at 4 per cent", r4 * w4, s4)
    has("md_neisser", "the source of growth is population", "the Neisser effect")
    has("md_bentzel", "the growth is due to productivity", "the Bentzel [1959] effect")
    # the aggregate consumption function
    assert "C = αYL + δW (3)" in transcription("md_eq3")
    L_, M_, rho, delta = F["md_delta"]
    said("他取的标准假设是一生 50 年、退休 10 年、增长率 3\\%", L_, M_, 100 * rho)
    said("照这些假设，财富的系数约为$\\delta=0.07$", delta)
    sixty, _, y63 = F["md_wealth_series"]
    has("md_wealth_series", "It was found to fit the data quite well", "Ando and Modigliani")
    said("据他的回顾，1960 年代初美国有了私人财富的年度序列，安藤（Albert Ando，1929—2002）与他 1963 年检验了这个方程",
         1900 + sixty, None, None, y63)
    has("md_many", "estimated for many countries and periods")
    has("md_lower", "Y is typically defined as total rather than just labor income")
    said("这个方程后来在许多国家与时期都估计过，财富的系数常常低于 0.07", F["md_lower"][0])
    assert F["md_lower"][0] == delta
    # ex:consumption-lifecycle
    L, N = LC
    assert (L, L - N) == (L_, M_)
    said("取莫迪利亚尼的标准假设，一生$L=50$年，退休 10 年，即$N=40$；每年收入$\\bar Y=1$", L, L - N, N, 1)
    said("（4）若人口每年增长 2\\%，储蓄率是多少？", 100 * LC_N)
    said("（3）每个年龄各有 1 人、经济静止时，总财富是总收入的几倍？", 1)
    S = stationary(L, N)
    said("（1）$C=40/50=0.8$，每年存$1-0.8=0.2$。", N, L, S["c"], 1, S["c"], S["save"])
    said("（2）$40\\times0.2=8$，是 8 年的收入，够退休后 10 年每年花 0.8。", N, S["save"], S["peak"], S["peak"], L - N, S["c"])
    chk("    the wealth at retirement pays for the retirement", S["peak"], (L - N) * S["c"])
    said("（3）总收入是在职的 40 人的收入，即 40。", N, S["income"])
    said("财富在工作期从 0 升到 8，退休期从 8 降到 0，总财富是两个三角形的面积，$40\\times8/2+10\\times8/2=200$，是总收入的 5 倍，"
         "等于退休年数的一半。", 0, S["peak"], S["peak"], 0, N, S["peak"], 2, L - N, S["peak"], 2, S["wealth"], S["w"])
    chk("    W/Y = M/2", S["w"], (L - N) / 2)
    said("40 个在职者每年存$40\\times0.2=8$，10 个退休者每年花掉$10\\times0.8=8$，总储蓄为零。", N, N, S["save"],
         N * S["save"], L - N, L - N, S["c"], (L - N) * S["c"])
    assert abs(S["saving"]) < 1e-12
    g2, g4 = lifecycle_growth(LC_N), lifecycle_growth(LC_N2)
    said("按连续的年龄把各组的人数以每年 2\\% 递减加权，财富收入比约 4.08，储蓄率约$0.02\\times4.08\\approx8.2\\%$（本书的计算），"
         "与莫迪利亚尼的 4 与 8\\% 相合", 100 * LC_N, g2["w"], LC_N, g2["w"], 100 * g2["s"], w2, s2)
    chk("    s = n w (2 per cent)", g2["s"], g2["sw"], tol=1e-9)
    said("人口增长 4\\% 时，算出来是约 3.33 与 13.3\\%。", 100 * LC_N2, g4["w"], 100 * g4["s"])
    chk("    s = n w (4 per cent)", g4["s"], g4["sw"], tol=1e-9)
    assert LC_N == r2 / 100 and LC_N2 == r4 / 100
    # fig:consumption_lifecycle
    said("(a) 莫迪利亚尼与布伦伯格的精简模型：一生 50 年，工作 40 年，收入每年 1，利率为零，消费每年 0.8，财富在退休时最多，是 8。",
         L, N, 1, S["c"], S["peak"])
    said("方块是莫迪利亚尼在演讲里给出的 2\\% 时的 8\\% 与 4\\% 时的 13\\%。", r2, s2, r4, s4)


def permanent(F, Y, Q):
    has("fr_title", "A Theory of the Consumption Function", "Princeton University Press")
    has("fr_nber", "A STUDY BY THE NATIONAL BUREAU OF ECONOMIC RESEARCH")
    said("弗里德曼的《消费函数理论》1957 年作为 NBER 的研究出版", F["fr_title"][0])
    has("fr_preface_kept", "my wife's occasional interest in the field", "our joint friendship with Dorothy Brady")
    has("fr_preface_group", "a series of conversations on the interpretation of consumption data", "Margaret Reid "
        "subsequently joined")
    has("fr_reid_test", "put to a critical test the hypothesis")
    has("fr_pressed", "she pressed me to write up the underlying theory", "This book is the result")
    has("fr_joint", "though my hand held the pen", "a joint product of the group")
    four, day, y51 = F["fr_typescript"]
    has("fr_typescript", "The earliest written version of the hypothesis I can find in my files")
    said("他能找到的最早的书面稿，是 1951 年 6 月 8 日的一份 4 页打字稿", y51, mon("fr_typescript", "June"), day, four)
    has("fr_fn12", "After completing an earlier draft", "two recent papers by FrancoModigliani and Richard Brumberg")
    has("fr_common", "a common intellectual environment")
    # the hypothesis
    has("fr_split", "the sum of two")
    has("fr_permanent_def", "determining its capital value or wealth", "the nonhuman wealth it owns")
    has("fr_transitory_def", 'all "other"')
    assert transcription("fr_eq") == "(2.6) c_p = k(i, w, u)y_p, (3.1) y = y_p + y_t, (3.2) c = c_p + c_t."
    has("fr_k", "independent of the size of permanent income")
    has("fr_i", "the rate of interest (i)")
    has("fr_w", "the ratio of nonhuman wealth to income (w)")
    has("fr_u", "the portmanteau variable u", "the number of members of the consumer unit", "their ages")
    has("fr_empty", "no empirical data could contradict it")
    has("fr_uncorrelated", "uncorrelated with one another and with the corresponding permanent components")
    assert "ρ_{y_t y_p} = ρ_{c_t c_p} = ρ_{y_t c_t} = 0" in transcription("fr_corr")
    # the paydays: the opening of the last chapter, IX
    has("fr_theme", "central theme of this monograph", "a simple hypothetical example")
    assert page("fr_theme") == page("fr_payday") == 220 and "chapter IX" in column("note")["fr_theme"]
    say("弗里德曼在最后一章开头说，全书的中心思想可以用一个假想的例子说明")
    a, b = F["fr_payday"]
    said("一群人每周挣 100 美元、花 100 美元，发薪日错开，每天有七分之一的人领工资", a, b)
    chk("    one-seventh (七分之一)", told("每天有七分之一的人领工资", "每天有", "的人"), F["fr_payday2"][0])
    has("fr_payday3", "the fraction of income saved would rise with income")
    has("fr_year", "a year does not render the error in actual data negligible")
    say("测得的收入高的家庭里，暂时收入为正的多，测得的储蓄率自然高（本书的概括）")
    # the estimates
    has("fr_horizon", "A horizon of about three years")
    said("消费者的视野看来大约是 3 年", F["fr_horizon"][0])
    has("fr_tentative", "three or more years", "a highly tentative conclusion")
    k1, k2, k3, k4 = F["fr_k_groups"]
    has("fr_k_groups", "for wage earners", "for entrepreneurs")
    said("工资收入者的$k$在$0.90$到$0.95$之间，企业主在$0.80$到$0.90$之间", k1, k2, k3, k4)
    has("fr_k_uncertain", "the greater uncertainty of income prospects")
    has("fr_kstar", "more than half a century", "excludes expenditures on major consumer durable goods")
    said("美国总消费与总收入之比半个多世纪大致不变，约为$0.88$", F["fr_kstar"][0])
    has("fr_mult", "the multiplier of personal disposable income with respect to autonomous expenditures")
    said("照他估计的消费函数，个人可支配收入对自主支出的乘数只有约 1.4", F["fr_mult"][0])
    has("fr_conditional", "conditional assertions", "the prior acceptance of the income-expenditure theory")
    # the windfall
    has("fr_windfall", "an unexpected windfall")
    has("fr_define", '"consumption" is defined')
    has("fr_reclassified", "is reclassified as savings")
    has("fr_durables", "the purchase of durable goods")
    has("fr_expected", "already have been allowed for in permanent income")
    has("fr_borrow", "inability to borrow in advance on the strength of the inheritance")
    has("fr_unexpected", "only the excess of the windfall over this element of permanent income")
    # growth
    has("md_pih", "life is indefinitely long")
    has("fr_rise", "a rapid rate of use in income")
    has("fr_reason", "a rise expected to continue tends to raise permanent income relative to measured income")
    has("fr_source", "the source of the rise in real income")
    has("fr_offset", "financed at least in part from domestic capital", "an offset")
    assert F["md_opposite"] == [F["fr_title"][0], page("fr_rise")]                 # Friedman [1957, p. 234]
    has("md_opposite", "diametrically opposite")
    has("md_infinite", "if life is infinite, there cannot be a Bentzel effect")
    # the compare box
    said("{他的估计里，消费者的视野看来约 3 年\\cite{friedman1957}}", F["fr_horizon"][0])
    has("fr_assets", "show up primarily in changes in the consumer units' assets and liabilities")
    has("fr_level", "the savings ratio is independent of the level of income")
    has("md_few", "one of the very few of any significance")
    # ex:consumption-windfall
    said("1975 年的退税每人至多 200 美元", F["pl_title"][0], F["pl_max"][0])
    said("一笔 200 美元的退税", F["pl_max"][0])
    assert WINDFALL == F["pl_max"][0]
    said("设一个家庭收到 200 美元，以下都是教学输入", WINDFALL)
    said("边际消费倾向 0.6，当年多花多少？", MPC)
    said("（2）按永久收入假说，利率 3\\%，$k=0.9$，取弗里德曼给工资收入者的下限", 100 * RATE, K_PIH)
    assert K_PIH == k1
    said("（3）按生命周期假说，利率为零，户主还有 40 年可活，当年多花多少？若是还有 10 年可活的退休者呢？", *YEARS_LEFT)
    R = first_year(WINDFALL, MPC, RATE, K_PIH, YEARS_LEFT[0])
    said("（1）$0.6\\times200=120$，花掉六成。", MPC, WINDFALL, R["keynes"])
    chk("    六成", told("花掉六成", "花掉", "成") / 10, MPC)
    said("（2）永久收入增加$0.03\\times200=6$，消费每年增加$0.9\\times6=5.4$，当年花掉 2.7\\%，以后年年如此。", RATE, WINDFALL,
         RATE * WINDFALL, K_PIH, RATE * WINDFALL, R["pih"], 100 * R["pih"] / WINDFALL)
    said("6 美元是这笔钱按 3\\% 每年生出的利息，即它的年金值（本书的解读）", RATE * WINDFALL, 100 * RATE)
    assert R["pih"] < RATE * WINDFALL         # at most the annuity value (pa_inconsistent): k < 1 spends less
    said("（3）$200/40=5$，每年多花 5，当年花掉 2.5\\%。", WINDFALL, YEARS_LEFT[0], R["lch"], R["lch"],
         100 * R["lch"] / WINDFALL)
    old = WINDFALL / YEARS_LEFT[1]
    said("退休者每年多花$200/10=20$，即 10\\%。", WINDFALL, YEARS_LEFT[1], old, 100 * old / WINDFALL)
    lo_, hi_ = R["keynes"] / R["pih"], R["keynes"] / R["lch"]
    assert 20 < lo_ < hi_ < 30, (lo_, hi_)
    chk("    二十多倍", told("三条规则对第一年的预测，相差二十多倍", "相差", "倍"), 20)
    say("永久收入与生命周期两种规则的差别，主要在于剩下的年数，年纪越大，花得越快")
    # fig:consumption_windfall
    said("横条是 Johnson、Parker 与 Souleles（2004）对 2001 年退税、Parker 等（2011）对 2008 年刺激款的估计区间",
         F["jps_wp"][1], F["jps_title"][0], F["pa_revised"][1], F["pa_title"][0])
    said("数据：Johnson 等（2004），Parker 等（2011）。", F["jps_wp"][1], F["pa_revised"][1])


def euler(F, Y, Q):
    y78, vol, no, _ = F["ha_issue"]
    assert F["hp_hall"][:3] == [y78, vol, no]
    has("hp_hall", "Journal of Political Economy")
    assert "Stochastic Implications of the Life Cycle–Permanent Income Hypothesis" in transcription("ha_title")
    said("1978 年，霍尔（Robert E. Hall，1943 年生）在《政治经济学杂志》第 86 卷第 6 期上发表", y78, None, vol, no)
    has("hj_authors", "Robert E. Hall is a graduate student at Massachusetts Institute of Technology")
    said("11 年前，他还是麻省理工学院的研究生，与乔根森合写过一篇讲税收与投资的论文", y78 - F["hp_hj"][0])
    has("ha_view", "set current consumption to the appropriate fraction of that estimate")
    has("ha_problem", "relates current and past observed income to expected future income")
    has("ha_lucas", "a fixed distributed lag", "Robert Lucas (1976)")
    # two periods
    said("$c_1+c_2/(1+r)=y_1+y_2/(1+r)$", 1, 1)
    said("今天少花 1 元，明天能多花$1+r$元", 1, 1)
    said("$u'(c_1)=\\frac{1+r}{1+\\delta}\\,u'(c_2)$", 1, 1)
    has("ha_et", "conditional on all information available in t", "rate of subjective time preference",
        "(r ≥ δ), assumed constant over time")
    say("$\\delta$是主观的时间偏好率，即消费者把明天的效用看得比今天轻多少", "实际利率$r$假定不随时间变，也不低于$\\delta$")
    assert "E_t u′(c_{t+1}) = [(1 + δ)/(1 + r)]u′(c_t)" in transcription("ha_theorem")
    has("ha_cor1", "income or wealth in periods t or earlier are irrelevant")
    has("ha_cor3", "quadratic", "no variable observed in period t or earlier will have a nonzero coefficient")
    has("ha_abstract", "random walk with trend", "consumption itself should evolve in the same way")
    say("消费本身因此近似一个带趋势的随机游走",
        "也就是说，消费在趋势之外的变动，事先都预测不到（本书的解读）")
    # the evidence
    T1 = F["ha_table1"]
    has("ha_table1", "REGRESSION RESULTS FOR THE BASIC MODEL, 1948–77")
    has("ha_data", "nondurables and services in 1972 dollars", "divided by the population", "quarterly")
    said("霍尔用 1948—1977 年美国按季度、按人头的非耐用品与服务消费检验，单位是 1972 年美元", T1[1], 1900 + T1[2],
         F["ha_data"][0])
    has("ha_durables", "Dropping durables altogether")
    said("效用取二次函数，只用上一季的消费做回归，系数是$1.011$", T1[6])
    assert T1[3:5] == [1.3, -1] and "quadratic" in column("note")["ha_table1"]            # equation 1.3, sigma = -1
    f1, crit, pct = F["ha_lags"]
    assert "c_{t−2}, c_{t−3}, and c_{t−4} are all zero" in transcription("ha_lags")
    said("再加三个更早季度的消费，$F$统计量是 1.7，5\\% 显著水平的临界值是 2.7", f1, pct, crit)
    chk("    three earlier quarters (三个)", told("再加三个更早季度的消费", "再加", "个"), 3)
    say("$F$统计量衡量新加的几个变量一起多解释了多少，超过临界值才算有预测力（本书的解读）")
    has("ha_refuted", "If lagged income has substantial predictive power beyond that of lagged consumption")
    has("ha_income", "a single lagged level of disposable income has essentially no predictive value at all")
    has("ha_confirmed", "It is confirmed for real disposable income")
    f0, crit0 = F["ha_exclusion"]
    assert "all but the constant and c_{t−1}" in transcription("ha_exclusion") and F["ha_income"] == [3.1]
    said("只加上一季的可支配收入，$F$统计量是 0.1，远低于临界值 3.9，它几乎没有预测力", f0, crit0)
    four, f4, crit4, pct4 = F["ha_lags4"]
    assert f4 < crit4 and pct4 == pct and "somewhat less than" in transcription("ha_lags4")
    has("ha_lags4", "Equation 3.2 tries a year-long distributed lag")
    said("加上前四个季度的收入，$F$统计量是 2.0，也略低于临界值 2.4", f4, crit4)
    chk("    four lagged incomes (四个)", told("加上前四个季度的收入", "前", "个"), four)
    has("ha_stock", "lagged by a single quarter", "refutes the simple random-walk hypothesis")
    has("ha_rejected", "is rejected by the data")
    has("ha_modified", "some part of consumption takes time to adjust to a change in permanent income")
    has("ha_little", "there seems little reason to doubt")
    has("ha_policy", "For policy analysis, the pure life cycle–permanent income hypothesis supports the modern view",
        "only unexpected changes in policy affect consumption")
    say("他说，就政策分析而言，纯粹的假说支持一种现代的看法，只有出乎意料的政策变化才影响消费")
    has("ha_transitory", "incapable of having a transitory effect on consumption")
    has("ha_noeffect", "none of the findings of the paper implies")
    has("ha_permanent_tax", "a permanent tax reduction generates an immediate increase in permanent income")
    # ex:consumption-euler
    E = EULER
    said("两期，收入$y_1=y_2=100$", E["y"])
    said("（1）利率$r=5\\%$，$\\delta=5\\%$，两期各消费多少？", 100 * E["r"], 100 * E["delta"])
    said("（2）第一期意外多得 10", E["extra"])
    said("（3）若$\\delta=0$，利率仍是 5\\%", 0, 100 * E["r"])
    said("对数效用下$u'(c)=1/c$，欧拉方程化为$c_2=\\frac{1+r}{1+\\delta}\\,c_1$。", 1, 1, 1)
    said("（1）$\\frac{1+r}{1+\\delta}=1$，$c_1=c_2$。", 1, 1, 1)
    c1, c2 = euler2(E["y"], E["y"], E["r"], E["delta"])
    pv = E["y"] + E["y"] / (1 + E["r"])
    said("收入的现值是$100+100/1.05\\approx195.24$，$c_1(1+1/1.05)=195.24$，$c_1=c_2=100$。", E["y"], E["y"], 1 + E["r"],
         pv, 1, 1, 1 + E["r"], pv, c1)
    assert np.isclose(c1, c2) and np.isclose(c1, E["y"])
    d1, d2 = euler2(E["y"] + E["extra"], E["y"], E["r"], E["delta"])
    said("（2）现值增加到约 205.24，$c_1=c_2\\approx105.12$，第一期多花约 5.12", pv + E["extra"], d1, d1 - c1)
    assert np.isclose(d1, d2)
    chk("    五成", told("第一期多花约 5.12，约五成", "，约", "成") / 10, (d1 - c1) / E["extra"], tol=0.05)
    say("另外五成存到第二期花")
    said("期数越多，第一期花掉的比例越小，若利率为零、分 40 年平摊，就只剩 2.5\\%（本书的计算）。", YEARS_LEFT[0],
         100 / YEARS_LEFT[0])
    f1_, f2_ = euler2(E["y"], E["y"], E["r"], 0)
    said("（3）$c_2=1.05\\,c_1$，代入预算约束，$c_1+c_1=195.24$，$c_1\\approx97.62$，$c_2\\approx102.50$。", 1 + E["r"], pv,
         f1_, f2_)
    # Hall's Table 1, equation 1.2: sigma = 1 (log utility), the regression of 1/c_t on 1/c_{t-1}, gamma = (1+δ)/(1+r)
    LG = F["ha_table1_log"]
    assert LG[:4] == T1[:3] + [1.2] and LG[4] == 1 and "1/c_t on 1/c_{t−1}" in column("note")["ha_table1_log"]
    assert LG[5] < 1                                       # r > δ: consumption rises, as in (3) of the example
    said("霍尔的表 1 里，对数效用下$\\frac{1+\\delta}{1+r}$的估计是 0.996，略小于 1，即人均消费每季约增长 0.4\\%（本书的计算）",
         T1[0], 1, 1, LG[5], 1, 100 * (1 / LG[5] - 1))


def investment(F, Y, Q):
    y62 = F["erp_title"][0]
    has("erp_urge", "the earliest possible enactment of the tax proposals")
    assert page("erp_urge") <= page("erp_end") < page("erp_cea")                  # the President's own report
    said("1962 年 1 月，肯尼迪（John F. Kennedy，1917—1963）在《总统经济报告》里请国会尽早通过他的税收提案", y62,
         mon("erp_title", "January"), None, None)
    said("这些提案的核心，是对可折旧的机器设备的总投资给予 8\\% 的税收抵免。", F["erp_centerpiece"][0])
    d, y = F["erp_retro"]
    said("他要抵免追溯到 1962 年 1 月 1 日", y, mon("erp_retro", "January"), d)
    has("erp_profit", "by reducing the net cost of acquiring new equipment")
    has("erp_selffinance", "in part self-financing")
    has("erp_revenues", "favorable effects on the level of economic activity", "add to Federal revenues")
    say("它还部分地自己为自己筹资，刺激起来的新投资会提高当年的经济活动，进而增加联邦的收入")
    has("erp_six", "improve the equity and efficiency of the tax system", "(6) Revision")
    has("erp_offset", "offset the remaining net revenue loss")
    chk("    six reforms (六项)", told("他提议用六项改革抵补", "用", "项"), F["erp_six"][0])
    assert F["erp_withholding"] == [1] and F["erp_dividend"][0] == 2 and F["erp_expense"] == [3]
    has("erp_withholding", "withholding principle to dividend and interest income")
    has("erp_dividend", "dividend exclusion", "dividend credit")
    has("erp_expense", "business deductions for entertainment")
    said("前三项是对股息与利息所得实行源泉扣缴，取消 50 美元的股息免税额与 4\\% 的股息抵免，限制招待费、礼品等业务开支的扣除",
         *F["erp_dividend"][1:])
    has("erp_expense", "entertainment, gifts, and other expenses")
    assert F["erp_capgains"] == [4] and F["erp_mutuals"] == [5] and F["erp_foreign"] == [6] == F["erp_six"]
    has("erp_capgains", "capital gains from the sale of depreciable property")
    has("erp_mutuals", "to cooperatives", "mutual fire and casualty insurance companies",
        "mutual savings banks and savings and loan associations")
    has("erp_foreign", "the tax treatment of foreign income")
    say("后三项是取消出售可折旧财产的资本利得优惠，取消合作社、互助保险公司、互助储蓄银行与储蓄贷款协会的优惠，修改境外所得的课税")
    chk("    the first three and the last three (前三项、后三项)",
        told("前三项是对股息与利息所得实行源泉扣缴", "前", "项") + told("后三项是取消出售可折旧财产的资本利得优惠", "后", "项"),
        F["erp_six"][0])
    say("得到抵免的是购置机器设备的企业。补上收入缺口的，是股息与利息的收入者、扣除招待费的企业、出售可折旧财产的人、合作社与互助金融机构，"
        "以及有境外所得的纳税人（本书的解读）")
    has("erp_cea_credit", "raise significantly the after-tax return on new investment")
    assert page("erp_cea_credit") >= page("erp_cea")
    said("顾问委员会的年度报告也说，8\\% 的抵免会显著提高新投资的税后回报", F["erp_cea_credit"][0])
    has("erp_cea_sign", "WALTER W. HELLER, Chairman.")
    members = 1 + len(Q["erp_cea_sign2"].split()) // 2                           # Heller, Gordon, Tobin
    chk("    three members (三位)", told("在年度报告上署名的三位委员", "署名的", "位"), members)
    day, y61 = F["erp_tobin_office"]
    has("erp_tobin_office", "took office as a member of the Council")
    said("他 1961 年 1 月 27 日就任", y61, mon("erp_tobin_office", "January"), day)
    y62a, seven, y62b = F["hj_credit7"]
    assert y62a == y62b == y62
    said("国会最后通过的《1962 年收入法》，对机器设备实行 7\\% 的投资抵免", y62b, seven)
    _, eff = F["hj_effective"]
    has("hj_effective", "inapplicable to very short-lived assets")
    said("抵免对寿命很短的资产不适用，他们说抵免的有效比率因此约为 6.6\\%", eff)
    has("hj_effective", "reduce its effective rate to about")                        # the rate of the credit
    # Hall and Jorgenson
    has("hp_hj", "American Economic Review", "(with Dale W. Jorgenson)")
    said("霍尔与乔根森 1967 年在《美国经济评论》上回答", F["hp_hj"][0])
    has("hj_faith", "an article of faith among both policy makers and economists")
    has("hj_noattempt", "no attempt has been made to estimate the magnitude")
    has("hj_jorgenson", "studied previously by D. W. Jorgenson")
    has("hj_rent", "supply capital services to itself")
    assert "(3) c = q(r + δ)" in transcription("hj_eq3") and "static expectations" in transcription("hj_eq3")
    say("企业可以在以后各年把折旧从应税所得里分年扣除")
    said("这些扣除折成的现值，按每 1 美元投资计，记作$z$", 1)
    say("再加上营业所得的税率$u$与抵免率$k$，就是")
    assert "one dollar's investment" in transcription("hj_eq6")
    has("hj_fn6", "This assumption is valid for 1962 and 1963")
    said("这里假定折旧的基数要扣掉抵免，霍尔与乔根森说这只适用于 1962 年与 1963 年", *F["hj_fn6"][1:3])
    has("hj_1964", "on the cost before rather than after the tax credit")
    said("1964 年起折旧按抵免以前的成本计算，他们说抵免的有效比率因此提到约 10\\%", *F["hj_1964"])
    has("hj_1964", "its effective rate was raised")
    assert F["hj_fn6"][3] == F["hj_1964"][0]
    assert "(12) K+ = α pQ/c" in transcription("hj_eq12") and "Cobb-Douglas" in transcription("hj_eq12")
    has("hj_lag", "funds appropriated, orders and contracts let")
    has("hj_eq13", "a weighted average of past changes in desired capital and replacement investment")
    has("hj_accelerator", "the familiar flexible accelerator theory of investment")
    said("照这个式子，租金低 1\\%，意愿资本大约多 1\\%（本书的解读）", 1, 1)
    y, before, after, _, _ = F["hj_rental"]
    has("hj_rental", "Manufacturing equipment .286 .267")
    has("hj_since1962", "Since 1962 a tax credit for expenditure on equipment")
    said("他们算出，1962 年的抵免把制造业设备的租金从$0.286$降到$0.267$", y, before, after)
    pct, y63, _ = F["hj_net"]
    has("hj_startling", "quite startling")
    has("hj_net", "net investment in manufacturing equipment in 1963")
    said("他们说，7\\% 的抵免效果“相当惊人”，1963 年制造业设备的净投资有 40.9\\% 可归于它", F["hj_startling"][0], y63, pct)
    has("hj_less", "less startling", "this impact is also quite dramatic")
    say("按总投资算，作用没有那么惊人，他们说也相当显著")
    bn, y63b, share = F["hj_gross"]
    said("1963 年制造业设备的总投资 84.6 亿美元，10.2\\% 来自抵免", y63b, bn * 1e9, share)
    has("hj_potent", "a potent stimulus to investment expenditure")
    has("hj_shift", "the adoption in 1962 of new guidelines and the investment tax credit",
        "a shift of investment from structures to equipment")
    said("按他们的计算，1962 年的抵免与折旧新规使投资转向设备", F["hj_shift"][1])
    # ex:consumption-usercost
    U = UC
    said("资本品价格$q=1$，$r=0.10$，$\\delta=0.15$，税率$u=0.5$，折旧扣除的现值$z=0.6$", U["q"], U["r"], U["d"], U["u"],
         U["z"])
    said("（3）加上 7\\% 的抵免呢？", seven)
    c0 = U["q"] * (U["r"] + U["d"])
    said("（1）$c=1\\times(0.10+0.15)=0.25$。", U["q"], U["r"], U["d"], c0)
    c1 = usercost(**U, k=0)
    said("（2）$c=0.25\\times(1-0.5\\times0.6)/(1-0.5)=0.25\\times0.7/0.5=0.35$。", c0, 1, U["u"], U["z"], 1, U["u"], c0,
         1 - U["u"] * U["z"], 1 - U["u"], c1)
    k7 = seven / 100
    c2 = usercost(**U, k=k7)
    said("（3）$c=0.35\\times(1-0.07)=0.3255$，低了 7\\%。", c1, 1, k7, c2, 100 * (1 - c2 / c1))
    assert np.isclose(c2, 0.3255)                                                # exact, so 0.35/0.3255 - 1 is 7.5%
    said("意愿资本增加$0.35/0.3255-1\\approx7.5\\%$。", c1, c2, 1, 100 * (c1 / c2 - 1))
    said("（4）租金从 0.286 降到 0.267，意愿资本增加$0.286/0.267-1\\approx7.1\\%$（本书的计算）", before, after, before,
         after, 1, 100 * (before / after - 1))
    # Tobin
    d, y81 = F["to_lecture"]
    assert F["nb_tobin_page"] == [d, y81]
    said("托宾 1981 年 12 月 8 日的诺贝尔奖演讲，从资产的市场估值讲投资", y81, mon("to_lecture", "December"), d)
    has("to_market", "differ, up or down, from their replacement costs")
    has("to_replacement", "installing at a normal pace")
    has("to_margin", "the margin above replacement cost induces investors to speed up capital accumulation")
    has("to_qdef", "normal replacement cost", "Its normal value is 1")
    said("他把市场估值与正常重置成本之比记作$q$，它的正常值是 1", F["to_qdef"][0])
    has("to_adjust", "adjustment costs", "can and do arise and persist")
    said("这种调整成本使$q$可以长期偏离 1", 1)
    has("to_net", "an equation for net investment")
    assert "I_t = q_t^K ΔK_t = q_t^K K_{t−1} f(q_t^K)" in transcription("to_eq3")
    assert "where ΔK_t + δK_{t−1} ≥ 0, f(1) = g, f′(q_t^K) ≥ 0, 0 < f^{−1}(−δ) < 1" in transcription("to_eq3")
    has("to_kstock", "valued at normal replacement cost, at the beginning of")
    assert transcription("to_dk") == "ΔK_t is the addition of K_{t−1} occurring in period t."
    has("to_depr", "the rate of depreciation of capital")
    say("$q_t^K$就是$t$期的$q$，$K_{t-1}$是$t$期期初按正常重置成本计的资本存量，$\\Delta K_t$是它在$t$期的增加，$\\delta$是资本的"
        "折旧率，$g$是经济的自然增长率")
    has("to_valued", "valued at asset market prices rather than normal replacement costs")
    say("他说明，这里的投资按资产的市场价格计，不按正常重置成本计", "所以资本存量的增加要乘以$q$（本书的解读）")
    has("to_zero", "the value that induces zero gross investment")
    said("使总投资为零的那个$q$值在 0 与 1 之间", 0, 1)
    has("to_g", "the natural rate of growth of the economy")
    has("to_normal", "keeps the capital stock growing at the trend of the economy")
    said("$q=1$时资本存量按自然增长率增长，$q$越高，积累得越快（本书的解读）", 1)
    has("to_footnote", 'The so-called "q" theory of investment was introduced as such in Tobin and Brainard (1968)')
    said("托宾说，$q$理论是他与 Brainard 1968 年的论文正式提出的，他 1969 年的论文又作了讨论与应用", *F["to_footnote"])
    has("to_precursors", "a straightforward application of the neoclassical theory of the firm")
    # the compare box
    said("\\begin{compare}{乔根森的投资模型与托宾的 $q$}{乔根森（霍尔与乔根森 1967）}{托宾（1981 年的演讲）}", F["hp_hj"][0], y81)
    said("{$q=1$时资本按自然增长率增长，$q$高时加快\\cite{tobin1981}}", 1)
    said("{投资过快带来调整成本，$q$因而可以长期偏离 1\\cite{tobin1981}}", 1)
    has("hj_conclusion", "the level and timing of investment expenditures")
    say("\\cmprow{政策怎样影响投资}{税收改变使用成本，非常有效地改变投资的水平与时间\\cite{hj1967}}")
    has("to_classical", "The classical variant.", "the roles of p and Y interchanged")
    has("to_monetary", "Monetary expansion is not neutral but lowers real interest rates",
        "shifts the composition of output from consumption to investment")
    assert page("to_monetary") == page("to_classical") + 1                       # the classical variant, after Table 3
    say("{在他模型的古典变体里，货币扩张压低实际利率，使产出从消费转向投资\\cite{tobin1981}}")
    # 1975 again
    T = F["pl_transition"]
    said("1975 年，国会把抵免暂时提到 10\\%，到 1977 年为止", F["pl_title"][0], F["pl_credit10"][0], T[5])
    (d100,) = F["ford_100"]
    has("ford_100", "the enormous total of $100 billion")
    said("福特在同一篇讲话里警告，若赤字涨到 1,000 亿美元", d100 * 1e9)
    has("ford_rates", "would again climb", "borrowed from the private money market")
    has("ford_delay", "despite the increased tax credit, would delay investments and expansions")


def check(F, Y, Q):
    a, b, gdp = there("ch32_generaltheory", "1929—1932 年英国的实际 GDP 下降了 5.3\\%")
    cons = there("ch32_generaltheory", "实际消费反而增加了 2.1\\%")[0]
    said("1929—1932 年，英国的实际 GDP 下降了 5.3\\%，实际消费反而增加了 2.1\\%，简单的消费函数解释不了"
         "（\\secref{sec:generaltheory-check}）", a, b, gdp, cons)
    has("fr_assets", "that is, in his measured savings")
    say("这只说明新理论容许这样的结果，它并没有检验这件事")
    # 1975
    has("ms_title", "CHARLES STEINDEL", "Is a Tax Rebate an Effective Tool for Stabilization Policy?")
    has("ms_bpea", "Brookings Papers on Economic Activity, 1977, No. 1")
    said("1975 年的退税是第一次检验", F["pl_title"][0])
    said("莫迪利亚尼与斯坦德尔（Charles Steindel，1951 年生）1977 年在《布鲁金斯经济活动论文》上分析了它", None,
         F["ms_bpea"][0])
    has("ms_criterion", "per dollar of tax revenue lost by the government", "concentrated in a short time span")
    said("政府每少收 1 美元税", 1)
    eight, ann = F["ms_paid"]
    has("ms_paid", "during the second quarter under the rebate program")
    said("按他们的数，第二季度退税发出 80 亿美元，折合年率 320 亿", eight * 1e9, ann * 1e9)
    chk("    the annual rate of a quarter", ann / eight, 4)
    has("ms_three", "one of three changes in tax and transfer programs")
    chk("    two more changes (两项)", told("同时还有两项变化", "还有", "项"), F["ms_three"][0] - 1)
    w12, _ = F["ms_withholding"]
    has("ms_withholding", "at an annual rate starting in May 1975")
    said("5 月起预扣的税按年率减少 120 亿美元", mon("ms_withholding", "May"), w12 * 1e9)
    j17, _ = F["ms_june"]
    has("ms_june", "paid out in June to social security recipients")
    said("6 月向社会保障的领取者发出 17 亿美元", mon("ms_june", "June"), j17 * 1e9)
    has("ms_ssrecip", "promptly and fully", "we do not treat any of these payments to them as part of")
    has("ms_equation", "on the assumption that there was no tax rebate at all")
    raw, corr = table6()
    four, q, three, third = F["ms_fourth"]
    has("ms_fourth", "less than one-fourth of the rebate was spent in the first three quarters", "only to one-third")
    chk("    the first three quarters (头三个季度)", told("头三个季度花掉的不到退税的四分之一", "头", "个"), three)
    chk("    one-fourth (四分之一)", told("头三个季度花掉的不到退税的四分之一", "退税的", ""), q)
    chk("    one-third (三分之一)", told("不校正也只到三分之一", "只到", ""), third)
    assert four == 4 and corr[2] < 100 * q and abs(raw[2] - 100 * third) < 1.5     # Table 6, 1975:4
    has("ms_sixth", "nearly all the rebate was spent by the end of the sixth quarter", "a most improbable pattern")
    chk("    the sixth quarter (第六个季度)", told("到第六个季度末几乎全部花掉", "到第", "个"), F["ms_sixth"][0])
    assert len(raw) == F["ms_sixth"][0] and raw[-1] > 95 and corr[-1] > 85
    has("ms_nosurge", "no prompt surge of expenditure was caused by the rebate")
    has("ms_saving", "the huge rise in saving in the second quarter")
    y, n3, n1 = F["ms_models"]
    has("ms_models", "three existing models of consumer demand and one especially constructed")
    chk("    three models (三个)", told("他们用了三个现成的消费模型和一个专门构建的模型", "用了", "个"), n3)
    chk("    and one (一个)", told("他们用了三个现成的消费模型和一个专门构建的模型", "和", "个"), n1)
    has("ms_dichotomy", "a single equation", "the MPS model", "DRI and Michigan")
    said("估计 1975 年进入支出的只是退税的一小部分", F["ms_dichotomy"][0])
    said("估计到 1975 年底已花掉一大部分", F["ms_dichotomy"][1])
    has("ms_blurs", "the furniture equation")
    has("ms_carter", "concentrated in lower-income groups, including beneficiaries of transfer payments")
    has("ms_1977", "proposed by the Carter administration in early 1977 but was subsequently withdrawn")
    said("他们推测，1977 年初卡特政府提出、后来撤回的那次退税，钱集中发给包括转移支付领取者在内的低收入者，可能会比 1975 年的稍有效",
         *F["ms_carter"])
    has("ms_differential", "consumers respond differently to different types of tax changes")
    has("md_transitory", "transitory income taxes (or rebates) can be expected to have small")   # the prediction
    has("ms_conclusion", "a rebate is not a particularly effective way of producing a prompt and temporary stimulus")
    has("ms_cannot", "either that by the end of the first year the proportion spent was negligible")
    # Blinder
    has("bl_title", "Temporary Income Taxes and Consumer Spending")
    assert F["bl_blend"] == [50, 50]
    has("bl_blend", "a 50-50 blend of a normal income tax change and a pure windfall")
    said("按 Blinder（1981）的估计，暂时的减税被当作一半正常的减税、一半纯粹的意外之财", F["bl_jpe"][0])
    one, p38 = F["bl_38"]
    has("bl_38", "Over a 1-year planning horizon", "a rebate is estimated to have only about 38 percent of the impact")
    chk("    a 1-year horizon (一年)", told("在一年的计划期里", "在", "年"), one)
    said("退税的作用只有同样大小的永久减税的约 38\\%", p38)
    has("bl_se", "unavoidably large")
    y75, s0, s1, _, q2 = F["bl_saving"]
    has("bl_saving", "just prior to the rebate", "in the quarter of the rebate (1975:2)")
    said("按他的记述，1975 年的储蓄率从退税前的 6.4\\% 跳到退税那个季度的 9.7\\%", y75, s0, s1)
    # 2001
    has("jps_title", "THE INCOME TAX REBATES OF 2001")
    said("2001 年的退税成了一次近乎随机的实验", F["jps_title"][0])
    t300, t600, two3, ten, y01 = F["jps_mailed"]
    has("jps_mailed", "from late July to the end of September, 2001")
    said("按 Johnson、Parker 与 Souleles（2004）的工作论文，2001 年 7 月下旬到 9 月底，约三分之二的美国家庭收到退税支票，通常是 300 "
         "或 600 美元", F["jps_wp"][1], y01, mon("jps_mailed", "July"), mon("jps_mailed", "September"), t300, t600)
    chk("    two-thirds (三分之二)", told("约三分之二的美国家庭收到退税支票", "约", "的"), two3)
    a15, a10, _ = F["jps_advance"]
    has("jps_advance", "the lowest income tax bracket", "an advance payment of this tax cut")
    said("退税是把最低一档税率从 15\\% 降到 10\\% 的预付款", a15, a10)
    (y00,) = F["jps_irs"]
    has("jps_irs", "based on his or her year 2000 tax return")
    has("jps_smaller", "could receive smaller rebates")
    said("国税局按每个纳税人 2000 年的纳税申报确定金额，2000 年税额不到 300 或 600 美元的，退得也少", y00, *F["jps_smaller"])
    said("照这个规则，2000 年没有所得税的家庭拿不到退税（本书的解读）", y00)
    got, notgot, nofile = F["jps_treasury"]
    has("jps_treasury", "tax returns received a rebate", "did not file and so also did not receive rebates")
    assert "Treasury estimates" in column("note")["jps_treasury"]
    said("他们转述财政部未公布的估计，约 8,950 万份纳税申报拿到退税，2,350 万份没有拿到", got * 1e6, notgot * 1e6)
    said("另有约 2,290 万户没有申报，也没有拿到", nofile * 1e6)
    has("jps_digit", "the second-to-last digit of the taxpayer's Social Security number", "effectively randomly assigned")
    p20, p40, _, third2, _ = F["jps_spent"]
    has("jps_spent", "on non-durable goods during the three-month period", "roughly another third")
    said("他们估计，家庭在收到退税的三个月里把 20\\%—40\\% 花在非耐用品上，下一个三个月又花掉约三分之一", p20, p40)
    chk("    another third (约三分之一)", told("下一个三个月又花掉约三分之一", "花掉约", ""), third2)
    has("jps_twothirds", "the quarter of receipt and subsequent three-month period")
    has("jps_liquidity", "low levels of liquid assets and low income", "consistent with their facing liquidity constraints")
    say("流动性约束是说，家庭想按将来的收入借钱却借不到，只能按手头的钱花（本书的解读）")
    # 2008
    _, y08, bn, mil = F["pa_esa"]
    has("pa_esa", "enacted in February 2008", "consisted primarily of a 100 billion dollar program",
        "approximately 130 million U.S. tax filers")
    said("2008 年的刺激款更大，发得也更宽", y08)
    said("按 Parker、Souleles、Johnson 与 McClelland（2011）的工作论文，《2008 年经济刺激法》2 月通过", F["pa_revised"][1],
         y08, mon("pa_esa", "February"))
    said("法案的主体是一项约 1,000 亿美元的计划，向约 1.3 亿个纳税申报单位发款，约占全部纳税单位的 85\\%", bn * 1e9, mil * 1e6,
         F["pa_85"][0])
    has("pa_85", 'roughly 85% of "tax units"')
    has("pa_noliability", "Households without tax liability received basic payments")
    has("pa_qualifying", "at least $3,000 of qualifying income", "earned income and Social Security benefits")
    has("pa_eligible", "a household needed to have positive net income tax liability, or at least sufficient")
    said("要拿到基本款，家庭要有正的所得税额，或者有至少 3,000 美元的合格收入，合格收入包括劳动收入与社会保障金",
         F["pa_qualifying"][0])
    (y07,) = F["pa_filers"]
    has("pa_filers", "only those filing 2007 returns received the payments")
    said("款项按 2007 年的纳税申报计算，没有申报 2007 年所得税的家庭拿不到", y07, y07)
    assert y07 == y08 - 1
    has("pa_phase", "being reduced by five percent of the amount by which adjusted gross income exceeded $75,000")
    has("pa_targeted", "more targeted to lower-income households than were the 2001 tax rebates")
    five, single, couple = F["pa_phase"]
    said("调整后总收入超过 7.5 万美元（夫妇 15 万）的，超出部分的 5\\% 从款项里扣掉，所以比 2001 年的退税更偏向低收入家庭"
         "（\\tabref{tab:consumption-rebates}）", single, couple, five, F["pa_targeted"][0])
    lo, hi, tlo, thi = F["pa_spent"]
    has("pa_spent", "on nondurable expenditures during the three-month period", "in particular vehicles")
    said("他们估计，三个月里花在非耐用品上的约占刺激款的 12\\%—30\\%", lo, hi)
    said("算上汽车等耐用品，总支出约占 50\\%—90\\%", tlo, thi)
    has("pa_inconsistent", "inconsistent with both Ricardian equivalence",
        "consume at most the annuitized value of a transitory increase in income")
    # tab:consumption-rebates
    said("1975 & 1974 年个人所得税的 10\\%，至少 100 美元（税额更少的全退），至多 200 美元；社会保障、铁路退休金与补充保障收入的领取者"
         "每人 50 美元 & 第二季度发出 80 亿美元，6 月发给社会保障领取者 17 亿美元 & 头三个季度不到四分之一（校正自相关）到三分之一（不校正）"
         " \\\\",
         F["pl_title"][0], F["pl_refund_title"][0], F["pl_rebate"][0], F["pl_min"][3], F["pl_max"][0], F["pl_50"][1],
         eight * 1e9, mon("ms_june", "June"), j17 * 1e9)
    said("2001 & 约三分之二的家庭，通常 300 或 600 美元 & 7 月下旬到 9 月底，按社会保障号码倒数第二位 & 三个月内非耐用品 20\\%—40\\%，"
         "下三个月约再三分之一 \\\\", y01, t300, t600, mon("jps_mailed", "July"), mon("jps_mailed", "September"), p20, p40)
    am = F["pa_amounts"]
    has("pa_amounts", "single individuals received $300-$600 and couples received $600-$1200", "$300 per child")
    assert F["pa_child"] == [am[4]] and F["pa_basic"] == am[:4]
    has("pa_digits", "the final two digits of the recipient's Social Security number")
    chk("    the last two digits (最后两位)", told("按社会保障号码最后两位", "最后", "位"), F["pa_digits"][0])
    said("2008 & 约 1.3 亿个纳税申报单位；单身 300 到 600 美元，夫妇 600 到 1,200 美元，每个孩子 300 美元 & 按社会保障号码最后两位 & "
         "三个月内非耐用品 12\\%—30\\%，含汽车等共 50\\%—90\\% \\\\", y08, mil * 1e6, *am, lo, hi, tlo, thi)
    said("\\datasource{1975 年据《1975 年减税法》与莫迪利亚尼、斯坦德尔（1977）表 6，2001 年据 Johnson、Parker 与 Souleles（2004），"
         "2008 年据 Parker、Souleles、Johnson 与 McClelland（2011）。", F["pl_title"][0], F["pl_title"][0], F["ms_bpea"][0],
         F["ms_table6"][0], y01, F["jps_wp"][1], y08, F["pa_revised"][1])
    # ex:consumption-mpc
    x = F["jps_typical"][0]
    has("jps_typical", "most received rebates of $300 or $600")
    said("2001 年的典型退税是 300 美元", F["jps_title"][0], x)
    said("（2）按 Johnson、Parker 与 Souleles 的估计，三个月里非耐用品花掉 20\\%—40\\%", p20, p40)
    R = first_year(x, MPC, RATE, K_PIH, YEARS_LEFT[0])
    said("（1）按边际消费倾向 0.6，当期花掉$0.6\\times300=180$，即 60\\%。", MPC, MPC, x, R["keynes"], 100 * MPC)
    pih_q, lch_q = 100 * R["pih"] / QUARTER / x, 100 * R["lch"] / QUARTER / x
    said("按永久收入假说，每年多花$0.9\\times0.03\\times300=8.1$，一个季度约 2.0，约 0.7\\%。", K_PIH, RATE, x, R["pih"],
         R["pih"] / QUARTER, pih_q)
    said("按生命周期假说，还有 40 年可活，每年多花$300/40=7.5$，一个季度约 1.9，约 0.6\\%。", YEARS_LEFT[0], x, YEARS_LEFT[0],
         R["lch"], R["lch"] / QUARTER, lch_q)
    lo6, hi6 = p20 + 100 * third2, p40 + 100 * third2
    said("（2）下一个三个月又花掉约三分之一，六个月里非耐用品一共约 53\\%—73\\%（本书的计算）", lo6, hi6)
    chk("    约三分之二 (Roughly two-thirds)", (lo6 + hi6) / 200, F["jps_twothirds"][0], tol=0.05)
    ratios = [p20 / pih_q, p40 / pih_q, p20 / lch_q, p40 / lch_q]
    assert 29 < min(ratios) < 31 and 60 < max(ratios) < 70, ratios
    said("（3）20\\%—40\\% 是永久收入与生命周期规则预测的约三十到六十多倍，又低于凯恩斯式的 60\\%（本书的计算）", p20, p40, 100 * MPC)
    assert p40 < 100 * MPC
    say("这还只算非耐用品")
    # the pitfall
    has("ms_opponents", "temporary changes in taxes will promptly and substantially affect consumer expenditures")
    has("ms_serviceflow", "the service-flow concept of consumption")
    has("ms_mps", "consumer expenditures on nondurable goods and services plus an estimate of the imputed flow of services")
    has("ms_hence", "a temporary tax cut might stimulate consumer spending")
    said("2008 年算上汽车以后花掉的比例，比只算非耐用品高出一倍以上（\\tabref{tab:consumption-rebates}）", F["pa_title"][0])
    assert tlo > 2 * lo and thi > 2 * hi


def case(F, Y, Q):
    E = esri()
    s68, s08, g68 = (E[c].dropna() for c in ("saving_68sna_pct", "saving_08sna_pct", "growth_68sna_pct"))
    said("\\begin{case}{日本 · 1955—2024 · 家庭储蓄率的升与降}", s68.index.min(), s08.index.max())
    has("esri_h10_household", "家計(個人企業を含む)")
    assert "貯蓄率＝貯蓄÷可処分所得" in load_snapshot("esri_household_saving_1955_2024")[1]["notes"]
    said("1955 年是 11.9\\%", 1955, s68[1955])
    g = compound(g68.loc[1956:1973])
    said("高速增长期的 1956—1973 年，实际国内总支出平均每年增长约 9.2\\%（本书的计算）", 1956, 1973, g)
    assert g68.loc[1956:1973].min() > 4 and g68[1974] < 0                       # the high growth ends in 1974
    said("家庭储蓄率在 1974 年与 1976 年都到了 23.2\\%，以后总体下降，1998 年是 13.4\\%", 1974, 1976, s68[1974], 1998, s68[1998])
    assert s68[1974] == s68[1976] == s68.max() and list(s68[s68 == s68.max()].index) == [1974, 1976]
    assert s68.loc[1977:1998].max() < s68[1976] and s08.loc[1999:].max() < s68[1976]
    said("这些数按 1968 年的国民账户体系，以 1990 年为基准", 1900 + F["esri_h10_title"][2], F["esri_h10_title"][1])
    has("esri_h10_title", "(1990基準・68SNA)")
    has("esri2024_title", "(2020年基準・2008SNA)")
    said("现行的统计按 2008 年的国民账户体系，以 2020 年为基准", F["esri2024_title"][2], F["esri2024_title"][1])
    assert "年金受給権の変動調整" in load_snapshot("esri_household_saving_1955_2024")[1]["notes"]
    say("储蓄率的分母加上了养老金权益的变动调整")
    said("按它，1994 年是 12.3\\%，2014 年降到$-1.6\\%$", 1994, s08[1994], 2014, -s08[2014])
    assert s08[2014] == s08.min() < 0 and s08.index.min() == 1994
    said("疫情中的 2020 年升到 10.2\\%，2024 年是 1.1\\%", 2020, s08[2020], 2024, s08[2024])
    assert s08[2020] == s08.loc[1999:].max()
    diff = (s68 - s08).dropna()
    assert list(diff.index) == list(range(1994, 1999))
    said("两个基准在重叠的 1994—1998 年相差 1.0 到 4.3 个百分点（本书的计算）", 1994, 1998, diff.min(), diff.max())
    # Horioka's Table S-1 prints the same figures
    assert sorted(r for r in F if r.startswith("ho_t1_") and r != "ho_t1_head") == list(HO_ROWS)
    for y in (1955, 1961, 1963, 1967, 1974, 1976):
        assert F[f"ho_t1_{y}"] == [y, s68[y]], y
    assert F["ho_t1_1986"][:2] == [1986, s68[1986]]
    for y in range(1994, 1999):
        v = F[f"ho_t1_{y}"]
        assert v[0] == y and v[1] == s68[y] and v[3] == s08[y], y
    for y in (2014, 2020, 2024):
        assert F[f"ho_t1_{y}"] == [y, s08[y]], y
    assert F["ho_latest"] == [2024, s08[2024]]
    # Modigliani's Figure 2 and Horioka's survey
    note = column("note")["md_fig2"]
    assert "the point of Japan is at the top right" in note and "the point of the U.S. near 3 per cent growth" in note
    said("莫迪利亚尼演讲的图 2 里，日本在右上角，储蓄率与增长都最高，美国靠近左下角", F["md_fig2"][0])
    has("md_us_low", "by far the richest country in the world, was rather low")
    has("md_puzzle", "through a relatively modest growth rate")
    has("ho_notalways", "has not always been high either absolutely or relative to other countries")
    has("ho_peak", "until the mid-1970s, when it peaked at 23.2%", "a downward trend since then")
    said("按 Horioka（2024）的综述，日本的家庭储蓄率并非一直很高，它在 1970 年代中期达到 23.2\\% 的峰值", F["ho_wp"][1],
         F["ho_peak"][0], F["ho_peak"][1])
    assert F["ho_peak"][1] == s68.max()
    has("ho_culture_expect", "to have always been high and to be stable or declining")
    has("ho_culture", "low or even negative during many periods", "from the mid-1950s until the mid-1970s",
        "not a major determinant")
    said("1950 年代中期到 1970 年代中期还明显上升过", *F["ho_culture"][3:5])
    has("ho_exclude", "we can exclude culture, tradition, and national character")
    # fig:consumption_japan
    said("(a) 家庭（含个人企业）的储蓄率，实线按 1968 年国民账户体系（1990 年基准，储蓄除以可支配收入），虚线按 2008 年国民账户体系"
         "（2020 年基准，分母加上养老金权益的变动调整），两者在 1994—1998 年重叠。", 1900 + F["esri_h10_title"][2],
         F["esri_h10_title"][1], F["esri2024_title"][2], F["esri2024_title"][1], 1994, 1998)
    said("横线是 1956—1973 年的平均，约 9.2\\%（本书的计算）", 1956, 1973, compound(esri()["growth_68sna_pct"].loc[1956:1973]))
    said("数据：内阁府经济社会综合研究所《1998 年度国民经济计算》与《2024 年度国民经济计算》，本书据其表格加工。",
         F["esri_h10_title"][0], F["esri2024_title"][0])


def debate(F, Y, Q):
    has("ha_income", "essentially no predictive value")
    has("ms_nosurge", "no prompt surge of expenditure")
    said("莫迪利亚尼与斯坦德尔发现，1975 年的退税没有引起支出的迅速增加", F["pl_title"][0])
    said("另一方的证据来自 2001 年与 2008 年近乎随机的发款时间，花掉的比例远高于永久收入假说的预测（\\exref{ex:consumption-mpc}）",
         F["jps_title"][0], F["pa_title"][0])
    said("也不能排除 1975 年的退税第一年几乎全被花掉", F["pl_title"][0])
    has("ms_cannot", "or that it was nearly as large as the rebate")
    has("ms_rationing", "constrained by credit rationing to be below optimum", "rapidly spend them")
    has("ms_tobin_dolde", "This view has been emphasized by, for example, James Tobin and Walter Dolde")
    has("jps_high", "While not statistically significant", "high levels of liquid assets and high income")
    # Japan
    has("md_growth_source", "growth is a major source of cross country differences in the saving rate")
    has("ho_age", "changes in the age structure of her population", "retired elderly households")
    said("按 Horioka（2024）的综述，人口年龄结构的变化能解释日本家庭储蓄率过去与未来的大部分趋势", F["ho_wp"][1])
    has("ho_oecd", "the highest among the OECD countries in the mid-1970s", "near the bottom of the OECD countries")
    said("他说，OECD 的国民账户显示，日本的家庭储蓄率 1970 年代中期在 OECD 国家里最高，近年已接近末位", F["ho_oecd"][0])
    has("ho_other", "the unavailability of consumer credit", "tax breaks for saving", "high and rising land and housing")
    has("hy_notasmuch", "however defined-is indeed higher than the comparable U.S. saving rate")
    said("按 Hayashi（1986）的估计，日本的储蓄率不论怎样定义，确实高于美国可比的储蓄率，只是没有通常以为的那么高", F["hy_title"][0])
    has("hy_accounting", "conceptual differences between U.S. and Japanese national accounting")
    has("hy_reject", "After rejecting the life-cycle explanations")
    has("hy_taxes", "probably not the main factor", "saving does not appear to be responsive to interest rates")
    say("他提出一个自己称为简单化的看法，前提是接受王朝式的观点")
    has("hy_dynastic", "the dynastic view of Barro (1974) and Becker (1981)")
    has("hy_horizon", "a significant flow of bequests", "the infinite horizon assumption may be a good approximation")
    say("他说，大量遗产的存在意味着，把寿命当作无限长可能是很好的近似")
    has("hy_growthmodel", "the economy's response to the low initial wealth is a high saving rate",
        "gradually stabilizes to a lower level as wealth approaches its steady-state value")
    say("日本的财富起点又很低，按无限期的最优增长模型，储蓄率先高，再随财富接近稳态而降下来")
    assert page("hy_dynastic") == page("hy_horizon") == page("hy_notest") < page("hy_growthmodel") == page("hy_children")
    has("hy_children", "in order for their children to live as well as Americans do")
    say("照这个看法，日本人积累财富，是为了让子女过得和美国人一样好")
    fifteen, y60 = F["hy_simplistic"]
    has("hy_simplistic", "this simplistic view", "(though not in the 1960s")
    said("他说，这个看法与日本近 15 年的经历相符，1960 年代则不然", fifteen, y60)
    has("hy_notest", "no direct and formal test of the dynastic model")
    # investment
    has("fhp_assumption", "prices set in centralized securities markets")
    has("fhp_access", "do not have sufficient access to external capital markets")
    has("fhp_excess", '"excess sensitivity" to movements in cash flow')
    has("fhp_finding", "more sensitive to cash flow for the group of firms")
    has("fhp_q", "q values remain very high for significant periods of time for firms paying no dividends",
        "relative to those for mature firms")
    say("不发股息的企业$q$值比成熟企业高，而且长期如此")
    said("按 Fazzari、Hubbard 与 Petersen（1987）的工作论文", F["fhp_title"][1])
    has("kz_notgood", "are not good indicators of financing constraints")
    said("按 Kaplan 与 Zingales（2000）的回应", F["kz_wp"][1])
    has("kz_admit", "FHP [1999] admit")
    has("kz_empirical", "The only disagreement", "how pervasive the non-monotonicity result is", "ultimately an empirical question")
    say("双方剩下的分歧只在于，敏感度不随约束加重而一直上升的现象有多普遍，这最终是一个经验问题")


def deeper(F, Y, Q):
    src = meta()["sources"]
    notes = meta()["notes"]

    def host(k):
        return re.match(r"https://([^/]+)/", src[k]["url"]).group(1)
    assert host("ford1975").endswith("presidency.ucsb.edu") and host("erp1962").endswith("presidency.ucsb.edu")
    assert host("pl9412") == "www.govinfo.gov"
    vol, p0, p1 = noted(r"vol\. (\d+), pp\. (\d+)-(\d+)", version("pl9412"))
    has("ford_note_law", f"({vol} Stat. {p0})")
    assert all(p0 <= page(r) <= p1 for r in _rows()["id"] if r.startswith("pl_"))
    said("《1975 年减税法》据政府出版局网站上《美国法律大全》第 89 卷第 26—67 页的扫描本", F["pl_title"][0], vol, p0, p1)
    said("1962 年的《总统经济报告》据美国总统资料项目网站上的 PDF，都是美国政府的作品", F["erp_title"][0])
    said("1962 年的报告到第 27 页是肯尼迪的报告，从第 31 页起是顾问委员会的年度报告", F["erp_title"][0], page("erp_end"),
         page("erp_cea"))
    has("erp_end", "I ask the support of the Congress and the American people")
    for rid in ("erp_urge", "erp_centerpiece", "erp_retro", "erp_profit", "erp_selffinance", "erp_revenues", "erp_six",
                "erp_capgains", "erp_mutuals", "erp_foreign"):
        assert page(rid) <= page("erp_end"), rid
    for rid in ("erp_cea_credit", "erp_cea_sign", "erp_tobin_office"):
        assert page(rid) >= page("erp_cea"), rid
    has("fr_indian", "Indian Edition 1970")
    has("fr_copyright", "Copyright 1957 by Princeton University Press")
    assert all(src[f"friedman1957{x}"]["url"].startswith("https://www.nber.org/system/files/chapters/") for x in "abcd")
    said("弗里德曼（1957）据 NBER 网站上各章的 PDF，扫描的是 1970 年的印度版，版权页印着 1957 年普林斯顿大学出版社的版权",
         F["fr_title"][0], F["fr_indian"][0], F["fr_copyright"][0])
    said("库兹涅茨（1942）是 NBER 的第 6 号不定期论文", F["ku_date"][0], F["ku_paper"][0])
    assert host("modigliani1985") == host("tobin1981") == "www.nobelprize.org"
    assert host("hall1978img") == host("hj1967img") == "web.stanford.edu"
    assert src["hall1978img"]["format"] == src["hj1967img"]["format"] == "image"
    said("霍尔（1978）与霍尔、乔根森（1967）据霍尔在斯坦福大学网站上的扫描本", F["ha_issue"][0], F["hp_hj"][0])
    assert host("ms1977img") == "www.brookings.edu" and "no spaces between" in version("ms1977img")
    said("莫迪利亚尼与斯坦德尔（1977）据布鲁金斯学会网站上的 PDF", F["ms_bpea"][0])
    (wp,) = noted(r"/w0*(\d+)\.pdf", src["blinder1981"]["url"])
    assert "the reprint that the NBER posts as its working paper" in version("blinder1981")
    said("Blinder（1981）读的是 NBER 网站上第 283 号工作论文的文件，它是《政治经济学杂志》的重印本", F["bl_jpe"][0], wp)
    has("pa_revised", "January 2011, Revised March 2013")
    said("Johnson 等（2004）与 Parker 等（2011）读的是 NBER 工作论文，后者是 2013 年 3 月的修订稿", F["jps_wp"][1],
         F["pa_revised"][1], F["pa_revised"][2], mon("pa_revised", "March"))
    has("pa_ref_jps", "American Economic Review, 96")
    said("据 Parker 等的参考文献，前者 2006 年发表在《美国经济评论》上", F["pa_ref_jps"][0])
    has("kz_ref_fhp", "Brookings Papers on Economic Activity (1988)")
    said("Fazzari 等（1987）是 NBER 第 2387 号工作论文，据 Kaplan 与 Zingales 的参考文献，它 1988 年发表在《布鲁金斯经济活动论文》上",
         F["fhp_title"][1], F["fhp_title"][0], F["kz_ref_fhp"][0])
    said("日本的储蓄率据内阁府经济社会综合研究所网站上 1998 年度与 2024 年度国民经济计算的表格", F["esri_h10_title"][0],
         F["esri2024_title"][0])
    # the misreadings (check_text() has the quotations)
    assert "Table 2 of Kuznets (1942), whose figures the text layer misreads" in notes
    said("库兹涅茨表 2 的数字，文字层多处读错，本书按页面图像读", F["ku_t2_head"][0])
    said("莫迪利亚尼演讲里，3 又四分之一读作“3 l/4”", 3, *printed("md_numbers", "3 l/4"))
    chk("    3¼", lfrac("3 l/4"), F["md_numbers"][4])
    # the disagreements
    _, _, c3, w3, s3 = F["md_three_pct"]
    said("莫迪利亚尼说，当年他们对美国的预测，按 3\\% 的增长率是财富收入比 4 又三分之一、储蓄率 13\\%", c3, int(w3), s3)
    chk("    4⅓", told("财富收入比 4 又三分之一", "4 又", "") + 4, w3)
    L_, M_, rho, _ = F["md_delta"]
    g3 = lifecycle_growth(rho, L=L_, N=L_ - M_)
    said("照同一个精简模型，3\\% 时约是 3.69 与 11.1\\%（本书的计算）", 100 * rho, g3["w"], 100 * g3["s"])
    assert c3 == 100 * rho and "(md_three_pct)" in notes
    said("莫迪利亚尼在正文里引的是 1971 年的莫迪利亚尼与斯坦德尔，参考文献里写的是 1977 年", F["md_steindel"][0],
         F["md_ref_steindel"][0])
    assert "(md_steindel)" in notes and "(md_ref_steindel)" in notes
    a25, y61, y86, fifteen = F["ho_period"]
    has("ho_period", "it was only during the 25-year period from 1961 to 1986 that it exceeded 15%")
    said("Horioka（2024）说战后只有 1961—1986 年的家庭储蓄率超过 15\\%，他自己的表 S-1 里 1963 年是 14.9\\%，1967 年是 14.1\\%",
         F["ho_wp"][1], y61, y86, fifteen, 1, *F["ho_t1_1963"], *F["ho_t1_1967"])
    assert y86 - y61 == a25 and F["ho_t1_1963"][1] < fifteen and F["ho_t1_1967"][1] < fifteen
    assert esri().loc[y61:y86, "saving_68sna_pct"].lt(fifteen).sum() == 2
    has("ho_fig_note", "the base year for the 2008SNA data is 2015")
    assert "Column (1)" in transcription("ho_table_note")
    said("他的表 S-1 说 2008 年体系的数以 2020 年为基准，图 1 的注写的是 2015 年", 1, *F["ho_table_note"][7:9], 1,
         F["ho_fig_note"][5])
    assert "(ho_table_note)" in notes and "(ho_fig_note)" in notes and "of Horioka's Figure 1" in notes
    eight, ann = F["ms_paid"]
    said("莫迪利亚尼与斯坦德尔在第 179 页说第二季度发出 80 亿美元，折合年率 320 亿；第 198 页说退税将近 260 亿美元，没有说明口径",
         page("ms_paid"), eight * 1e9, ann * 1e9, page("ms_26"), F["ms_26"][0] * 1e9)
    has("ms_26", "nearly $26 billion")
    assert "(ms_paid)" in notes and "(ms_26)" in notes
    # single witnesses
    sw = notes.split("Single witnesses:")[1].split("Indirect testimony")[0]
    for rid in ("ku_t2_1879", "ku_t2_1929", "fr_k_groups", "fr_horizon", "fr_mult", "ha_table1", "ha_lags",
                "ha_exclusion", "hj_rental", "hj_net", "hj_gross", "ms_table6", "bl_38", "jps_spent", "pa_spent"):
        assert rid in sw, rid
    said("霍尔与乔根森的租金与 40.9\\%，莫迪利亚尼与斯坦德尔表 6 的比例", F["hj_net"][0], F["ms_table6"][0])
    has("ho_table_note", "Source: Economic and Social Research Institute, Cabinet Office, Government of Japan")
    assert "they agree" in sw
    said("日本的储蓄率有经济社会综合研究所的表格与 Horioka（2024）的表 S-1 两处", F["ho_wp"][1], 1)
    said("本书没有读到 Fazzari 等 1999 年的原文", F["kz_admit"][0])
    it = notes.split("Indirect testimony:")[1].split("Not obtained:")[0]
    assert "unpublished Treasury estimates" in it and "(jps_treasury)" in it
    said("2001 年拿到与没拿到退税的申报数，是 Johnson 等转述的财政部未公布估计", F["jps_title"][0])
    assert "ha_table1_log" in sw and "ha_lags4" in sw
    assert F["kz_admit"] == F["kz_empirical"]
    # not obtained
    nl = notes.split("Not obtained:")[1].split("Life dates:")[0]
    said("安藤与莫迪利亚尼（1963）、乔根森（1963）、Tobin（1969）与 Brainard 与 Tobin（1968）都没有读到",
         *noted(r"Ando and Modigliani \((\d{4})\); Jorgenson \((\d{4})\); Tobin \((\d{4})\); Brainard and Tobin "
                r"\((\d{4})\)", nl))
    assert F["md_wealth_series"][2] == 1963 and F["to_footnote"] == [1968, 1969]
    said("Hayashi（1982）关于边际$q$与平均$q$的论文、Flavin（1981）关于消费对收入过度敏感的论文、Hsieh、Shimizutani 与 Hori（2010）",
         *noted(r"Hayashi \((\d{4})\); Flavin \((\d{4})\); Hsieh, Shimizutani and Hori \((\d{4})\)", nl))
    y97, w67 = noted(r"Kaplan and Zingales \((\d{4})\): only the scan of NBER Working Paper (\d+)", nl)
    assert y97 == F["kz_notgood"][0]
    said("Kaplan 与 Zingales（1997）的论文，本书只取得 NBER 网站上第 5267 号工作论文的扫描本", y97, w67)
    y96, w62 = noted(r"response of January (\d{4}), NBER Working Paper (\d+)", nl)
    said("Fazzari 等人 1996 年的回应（第 5462 号）也是这样，正文只用 Kaplan 与 Zingales 2000 年的回应", y96, w62, F["kz_wp"][1])
    # the life dates
    has("loc_ando_note", "(d. 2002)")
    said("国会图书馆的安藤记录只在来源注里写着卒于 2002 年", F["loc_ando_note"][0])
    _, _, d_loc, _ = F["loc_kuznets_died"]
    has("loc_kuznets_died", "July 8, 1985")
    said("库兹涅茨的卒日，国会图书馆写 7 月 8 日，德国国家图书馆写 7 月 9 日", mon("loc_kuznets_died", "July"), d_loc,
         *F["gnd_kuznets_died"][1:])
    assert d_loc != F["gnd_kuznets_died"][2] and "(loc_kuznets_died)" in notes and "(gnd_kuznets_died)" in notes
    assert "Brumberg: no record found in the LoC or the GND" in notes


def legacy(F, Y, Q):
    assert page("ha_lucas") == page("ha_title")                                   # the first page
    said("他在论文开头引了卢卡斯 1976 年的批评", F["ha_lucas"][0])
    has("md_barro", "the so called Ricardian Equivalence Proposition (Barro [1974])")
    said("莫迪利亚尼的演讲已经讨论巴罗 1974 年的李嘉图等价命题", F["md_barro"][0])
    has("ho_peak", "the Covid-19 pandemic period of 2020-21")
    said("2020 年疫情中的转移支付在\\chref{ch:pandemic}", F["ho_peak"][3])
    said("1975 年主要按交的税发，2008 年也发给没有所得税、但有合格收入的家庭（本书的概括）", F["pl_title"][0], F["pa_title"][0])
    said("投资对融资条件的依赖，在 2008 年以后的金融摩擦模型里重新受到重视（\\chref{ch:frictions}）", F["pa_title"][0])


def takeaways(F, Y, Q):
    r2, _, s2, r4, _, s4 = F["md_numbers"]
    said("莫迪利亚尼算出增长 2\\% 时约 8\\%、4\\% 时约 13\\%", r2, s2, r4, s4)
    k1, k2, _, _ = F["fr_k_groups"]
    said("工资收入者的$k$在$0.90$到$0.95$之间，乘数只有约 1.4", k1, k2, F["fr_mult"][0])
    said("霍尔（1978）推出消费是带趋势的随机游走", F["ha_issue"][0])
    said("霍尔与乔根森（1967）估计 1962 年的 7\\% 抵免带来 1963 年制造业设备净投资的 40.9\\%", F["hp_hj"][0], F["hj_credit7"][0],
         F["hj_credit7"][1], F["hj_net"][1], F["hj_net"][0])
    said("1975 年、2001 年与 2008 年的一次性发钱检验了这些理论，2001 年与 2008 年的估计远高于永久收入假说的预测", F["pl_title"][0],
         F["jps_title"][0], F["pa_title"][0], F["jps_title"][0], F["pa_title"][0])
    items = re.search(r"\\begin\{takeaways\}(.*?)\\end\{takeaways\}", tex_text(), re.DOTALL).group(1).count("\\item")
    assert 4 <= items <= 6, items


def selfcheck(F, Y, Q):
    L2, N2 = SC_LC
    said("一生 60 年，工作 45 年，每年收入 1，利率为零", L2, N2, 1)
    assert SC_REBATE == F["jps_typical"][1]
    said("2001 年的典型退税是 600 美元的家庭", F["jps_title"][0], SC_REBATE)
    said("生命周期规则取还有 30 年可活", SC_YEARS)
    said("两期模型，对数效用，$r=4\\%$，$\\delta=2\\%$", 100 * SC_R, 100 * SC_DELTA)
    assert SC_K == (F["hj_credit7"][1] / 100, F["pl_credit10"][0] / 100)
    said("仍照 1962—1963 年的规则把折旧的基数扣掉抵免，抵免从 7\\% 提到 10\\%，使用成本降低百分之几？", F["hj_fn6"][1],
         F["hj_fn6"][2], 100 * SC_K[0], 100 * SC_K[1])
    assert F["hj_fn6"][3] > F["hj_fn6"][2]           # after 1963 the base was not reduced: the question keeps the rule
    said("2008 年的刺激款，非耐用品与总支出的两组估计差得很多", F["pa_title"][0])
    items = re.search(r"\\begin\{selfcheck\}(.*?)\\end\{selfcheck\}", tex_text(), re.DOTALL).group(1).count("\\item")
    answers = re.search(r"\\begin\{answers\}(.*?)\\end\{answers\}", tex_text(), re.DOTALL).group(1).count("\\item")
    assert 4 <= items <= 7 and items == answers, (items, answers)
    # the answers
    S2 = stationary(L2, N2)
    said("$C=45/60=0.75$，每年存 0.25；退休时财富$45\\times0.25=11.25$，够退休后 15 年每年花 0.75。财富收入比等于退休年数的一半，"
         "即 7.5。", N2, L2, S2["c"], S2["save"], N2, S2["save"], S2["peak"], L2 - N2, S2["c"], S2["w"])
    chk("    W/Y = M/2", S2["w"], (L2 - N2) / 2)
    R2 = first_year(SC_REBATE, MPC, RATE, K_PIH, SC_YEARS)
    said("凯恩斯式：$0.6\\times600=360$。永久收入：$0.9\\times0.03\\times600=16.2$。生命周期：$600/30=20$。", MPC, SC_REBATE,
         R2["keynes"], K_PIH, RATE, SC_REBATE, R2["pih"], SC_REBATE, SC_YEARS, R2["lch"])
    ratio = (1 + SC_R) / (1 + SC_DELTA)
    c1, c2 = euler2(1, 1, SC_R, SC_DELTA)
    chk("    c2/c1 of the two-period model", c2 / c1, ratio, tol=1e-12)
    said("$c_2/c_1=1.04/1.02\\approx1.02$，第二期多消费约 2\\%。", 1 + SC_R, 1 + SC_DELTA, ratio, 100 * (ratio - 1))
    c0 = usercost(**UC, k=0)
    u7, u10 = usercost(**UC, k=SC_K[0]), usercost(**UC, k=SC_K[1])
    said("7\\% 时$c=0.35\\times0.93=0.3255$，10\\% 时$c=0.35\\times0.90=0.315$，降低约 3.2\\%；意愿资本与$c$成反比，增加"
         "$0.3255/0.315-1\\approx3.3\\%$。", 100 * SC_K[0], c0, 1 - SC_K[0], u7, 100 * SC_K[1], c0, 1 - SC_K[1], u10,
         100 * (1 - u10 / u7), u7, u10, 1, 100 * (u7 / u10 - 1))
    say("两组估计的消费定义不同")


def ending(F, Y, Q):
    said("回到 1975 年 3 月 29 日的椭圆形办公室", F["ford_title"][0], mon("ford_title", "March"), F["ford_title"][1])
    say("福特盼着退税去买汽车与家电，盼着抵免让企业扩张")
    say("照永久收入与生命周期的理论，一次性的退税多半会被存起来；后来的研究发现，钱少的家庭花得多")
    E = esri()["saving_68sna_pct"].dropna()
    assert np.polyfit(E.loc[1955:1973].index, E.loc[1955:1973].to_numpy(), 1)[0] > 0
    assert E.idxmax() == 1974 and esri().loc[1974, "growth_68sna_pct"] < 0
    say("日本的家庭储蓄率在高速增长的年代里总体走高，到增长放慢时才达到顶峰")
    say("下一章索洛的增长模型把储蓄率当作给定，问的是储蓄能把增长推到哪里")
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 40's question"
    assert t.index("\\end{answers}") < t.index("回到 1975 年 3 月 29 日")
    assert f"\\guidequestion{{{NEXT}}}" in (ROOT / "zh" / "ch40_solow.tex").read_text(encoding="utf-8")


def models() -> None:
    """The key equations as printed, and the claims the text makes of them, checked with random numbers."""
    t = TEX.read_text(encoding="utf-8")
    eqs = {lab: body.strip() for body, lab in re.findall(r"\\begin\{keyeq\}\n(.*?)\\label\{(eq:[^}]+)\}", t, re.DOTALL)}
    assert sorted(eqs) == ["eq:consumption-euler", "eq:consumption-lifecycle", "eq:consumption-usercost"], sorted(eqs)
    assert eqs["eq:consumption-lifecycle"] == "C=\\frac{A_t+(N-t)\\,\\bar Y}{L-t},\\qquad 0\\le t\\le N.", eqs
    assert eqs["eq:consumption-euler"] == "E_t\\,u'(c_{t+1})=\\frac{1+\\delta}{1+r}\\,u'(c_t).", eqs
    assert eqs["eq:consumption-usercost"] == "c=q\\,(r+\\delta)\\,\\frac{(1-k)(1-uz)}{1-u}.", eqs
    assert "E_t u′(c_{t+1}) = [(1 + δ)/(1 + r)]u′(c_t)" in transcription("ha_theorem")
    assert "(6) c = q(r + δ)(1 − k)(1 − uz)/(1 − u)" in transcription("hj_eq6")
    eqn = {lab: body.strip() for body, lab in re.findall(r"\\begin\{equation\}\n(.*?)\\label\{(eq:[^}]+)\}", t, re.DOTALL)}
    assert eqn == {"eq:consumption-permanent": "c_p=k(i,w,u)\\,y_p,\\qquad y=y_p+y_t,\\qquad c=c_p+c_t,",
                   "eq:consumption-q": "\\begin{gathered}\nI_t=q_t^K\\,\\Delta K_t=q_t^K\\,K_{t-1}\\,f(q_t^K),\\\\\n"
                                       "\\Delta K_t+\\delta K_{t-1}\\ge0,\\qquad f(1)=g,\\qquad f'(q_t^K)\\ge0,\\qquad "
                                       "0<f^{-1}(-\\delta)<1,\n\\end{gathered}"}, eqn
    # Tobin's (3) as printed (to_eq3), condition by condition
    for tex, printed in (("I_t=q_t^K\\,\\Delta K_t=q_t^K\\,K_{t-1}\\,f(q_t^K)", "I_t = q_t^K ΔK_t = q_t^K K_{t−1} f(q_t^K)"),
                         ("\\Delta K_t+\\delta K_{t-1}\\ge0", "ΔK_t + δK_{t−1} ≥ 0"), ("f(1)=g", "f(1) = g"),
                         ("f'(q_t^K)\\ge0", "f′(q_t^K) ≥ 0"), ("0<f^{-1}(-\\delta)<1", "0 < f^{−1}(−δ) < 1")):
        assert tex in eqn["eq:consumption-q"] and printed in transcription("to_eq3"), (tex, printed)
    rng = np.random.default_rng(39)
    # C = a + cY: with a > 0 the saving ratio rises with income
    for a, c in rng.uniform(0.01, 0.95, (50, 2)):
        y = np.linspace(1, 100, 60)
        assert np.all(np.diff(1 - (a + c * y) / y) > 0)
    # eq:consumption-lifecycle: on the plan, consumption is (N/L) Ybar at every age and wealth is zero at L
    for _ in range(200):
        L = rng.uniform(30, 70)
        N = rng.uniform(0.4, 0.95) * L
        yb = rng.uniform(0.5, 2)
        c0 = N / L * yb
        for tt in rng.uniform(0, N, 5):
            A = (yb - c0) * tt
            C = (A + (N - tt) * yb) / (L - tt)
            assert np.isclose(C, c0) and np.isclose(A + (N - tt) * yb - (L - tt) * C, 0)
            # a windfall x at age t raises consumption by x/(L - t) a year (the rule of ex:consumption-windfall)
            x = rng.uniform(0, 5)
            assert np.isclose((A + x + (N - tt) * yb) / (L - tt) - C, x / (L - tt))
        S = stationary(L, N)
        assert np.isclose(S["w"], (L - N) / 2) and abs(S["saving"]) < 1e-9 and np.isclose(S["peak"], (L - N) * N / L)
    # the growing economy: s = n w, rising with n, and the stationary ratio at n -> 0 (Propositions 3 and 6)
    s_prev = -1.0
    for n in np.linspace(0.0, 0.06, 13):
        g = lifecycle_growth(n)
        assert np.isclose(g["s"], g["sw"], atol=1e-9) and g["s"] > s_prev
        s_prev = g["s"]
    assert abs(lifecycle_growth(0.0)["s"]) < 1e-9 and np.isclose(lifecycle_growth(0.0)["w"], stationary(*LC)["w"])
    for L, M in ((50, 5), (50, 15)):                                            # longer retirement, higher ratio
        assert lifecycle_growth(0.02, L=L, N=L - M)["w"] < lifecycle_growth(0.02, L=L, N=L - M - 1)["w"]
    # the two-period Euler equation: the solution satisfies the budget and the first-order condition, and is the best
    # of nearby feasible plans
    for _ in range(200):
        y1, y2 = rng.uniform(50, 150, 2)
        r, d = rng.uniform(0, 0.1, 2)
        c1, c2 = euler2(y1, y2, r, d)
        assert np.isclose(c1 + c2 / (1 + r), y1 + y2 / (1 + r))
        assert np.isclose(1 / c1, (1 + r) / (1 + d) / c2)                        # u'(c1) = (1+r)/(1+δ) u'(c2)
        U = math.log(c1) + math.log(c2) / (1 + d)
        for e in (-1.0, -0.1, 0.1, 1.0):
            assert math.log(c1 + e) + math.log(c2 - e * (1 + r)) / (1 + d) < U
        if r > d:
            assert c2 > c1
    # the user cost: no taxes, q(r + δ); expensing at once (z = 1) leaves it unchanged; a larger z, a larger credit lower it
    for _ in range(200):
        q, r, d, u = rng.uniform(0.5, 2), rng.uniform(0, 0.15), rng.uniform(0.02, 0.3), rng.uniform(0.1, 0.6)
        z, k = rng.uniform(0, 1), rng.uniform(0, 0.15)
        assert np.isclose(usercost(q, r, d, 0, z, 0), q * (r + d)) and np.isclose(usercost(q, r, d, u, 1, 0), q * (r + d))
        assert usercost(q, r, d, u, z, 0) >= q * (r + d) - 1e-12
        assert usercost(q, r, d, u, min(z + 0.1, 1), k) <= usercost(q, r, d, u, z, k) + 1e-12
        assert usercost(q, r, d, u, z, k + 0.01) < usercost(q, r, d, u, z, k)
        assert usercost(q, r + 0.01, d, u, z, k) > usercost(q, r, d, u, z, k)    # the rate and the credit pull apart
    # the desired capital alpha p Q / c: proportional to 1/c
    for c, c2 in rng.uniform(0.1, 0.5, (20, 2)):
        assert np.isclose((0.3 / c2) / (0.3 / c) - 1, c / c2 - 1)
    # Tobin's (3) with a linear f: at q = 1 the stock grows at g, faster with q; gross investment is zero at
    # q = f^{-1}(-delta), between 0 and 1 when the slope exceeds g + delta
    for _ in range(200):
        g, d = rng.uniform(0, 0.05), rng.uniform(0.02, 0.15)
        a = rng.uniform(g + d + 0.01, 1.0)
        f = lambda q: g + a * (q - 1)                                            # noqa: E731
        q0 = 1 - (g + d) / a
        assert np.isclose(f(1), g) and 0 < q0 < 1 and np.isclose(f(q0) + d, 0)
        for q in rng.uniform(0.5, 2, 5):
            K = rng.uniform(1, 10)
            assert (K * f(q) + d * K >= 0) == (q >= q0 - 1e-12) and (f(q) > g) == (q > 1)
    # Friedman's paydays: on any one day the measured saving ratio rises with measured income
    week, days = facts()["fr_payday"][0], round(1 / facts()["fr_payday2"][0])
    income = np.array([week] + [0] * (days - 1), dtype=float)
    spent = np.full(days, week / days)
    assert income[0] - spent[0] > 0 and np.all(income[1:] - spent[1:] < 0)
    print("ok the key equations as printed; the life cycle, the Euler equation and the user cost on random numbers")


def figures_data() -> None:
    """What the figures assert of their data."""
    P = lifecycle_path(*LC)
    assert np.isclose(P["wealth"].max(), stationary(*LC)["peak"]) and np.isclose(P.loc[P["wealth"].idxmax(), "age"], LC[1])
    assert np.isclose(P["wealth"].iloc[-1], 0) and P["consumption"].nunique() == 1
    G = growth_curve()
    assert np.isclose(G["s"].iloc[0], 0, atol=1e-9) and G["s"].is_monotonic_increasing
    W = windfall_paths()
    assert np.isclose(W.loc[YEARS_LEFT[0], "lch"], 1) and np.isclose(W.loc[YEARS_LEFT[1], "retiree"], 1)
    assert np.isclose(W.loc[1, "keynes"], MPC) and np.isclose(W.loc[1, "pih"], K_PIH * RATE)
    B = rebate_bars()
    assert len(B["bars"]) == 3 and B["rules"]["pih"] < B["rules"]["lch"] + 0.1 < B["rules"]["keynes"]
    E = esri()
    assert list(E.index) == list(range(1955, 2025))
    assert E["saving_68sna_pct"].notna().sum() == 44 and E["saving_08sna_pct"].notna().sum() == 31


# ---------------------------------------------------------------------------------------------------
# 5. The book
# the life dates: words -> (row of the birth year, index), (row of the death year, index), row of the heading, heading
LIVES = {"Gerald R. Ford，1913—2006": (("loc_ford", 0), ("loc_ford", 1), "loc_ford", "Ford, Gerald R."),
         "John Maynard Keynes，1883—1946": (("loc_keynes", 0), ("loc_keynes", 1), "loc_keynes", "Keynes, John Maynard"),
         "Milton Friedman，1912—2006": (("loc_friedman", 0), ("loc_friedman", 1), "loc_friedman", "Friedman, Milton"),
         "Simon Kuznets，1901—1985": (("loc_kuznets", 0), ("loc_kuznets", 1), "loc_kuznets", "Kuznets, Simon"),
         "Franco Modigliani，1918—2003": (("loc_modigliani_note", 1), ("loc_modigliani_note", 3), "loc_modigliani",
                                         "Modigliani, Franco"),
         "Margaret G. Reid，1896—1991": (("loc_reid", 0), ("loc_reid", 1), "loc_reid", "Reid, Margaret G."),
         "Irving Fisher，1867—1947": (("loc_fisher", 0), ("loc_fisher", 1), "loc_fisher", "Fisher, Irving"),
         "Albert Ando，1929—2002": (("gnd_ando_born", 0), ("gnd_ando_died", 0), "gnd_ando", "Ando, Albert"),
         "John F. Kennedy，1917—1963": (("loc_kennedy", 0), ("loc_kennedy", 1), "loc_kennedy", "Kennedy, John F."),
         "James Tobin，1918—2002": (("loc_tobin", 0), ("loc_tobin", 1), "loc_tobin", "Tobin, James"),
         "Dale W. Jorgenson，1933—2022": (("loc_jorgenson", 0), ("gnd_jorgenson_died", 0), "loc_jorgenson",
                                         "Jorgenson, Dale W.")}
# the living, and the one without a record: words -> (row of the birth year, index), row of the heading, heading
BORN = {"Robert E. Hall，1943 年生": (("loc_hall", 0), "loc_hall", "Hall, Robert E."),
        "Charles Steindel，1951 年生": (("loc_steindel_born", 2), "loc_steindel", "Steindel, Charles")}
# where two records have a date, they agree: (row, index) pairs
AGREE = [(("gnd_ford_born", 0), ("loc_ford", 0)), (("gnd_ford_died", 0), ("loc_ford", 1)),
         (("gnd_kuznets_born", 0), ("loc_kuznets", 0)), (("gnd_kuznets_died", 0), ("loc_kuznets", 1)),
         (("loc_kuznets_died", 1), ("loc_kuznets", 0)), (("loc_kuznets_died", 3), ("loc_kuznets", 1)),
         (("loc_kuznets_died", 0), ("gnd_kuznets_born", 2)),
         (("gnd_reid_born", 0), ("loc_reid", 0)), (("gnd_reid_died", 0), ("loc_reid", 1)),
         (("gnd_tobin_born", 0), ("loc_tobin", 0)), (("gnd_tobin_died", 0), ("loc_tobin", 1)),
         (("gnd_hall_born", 0), ("loc_hall", 0)), (("gnd_jorgenson_born", 0), ("loc_jorgenson", 0)),
         (("gnd_modigliani_born", 0), ("loc_modigliani_note", 1)), (("gnd_modigliani_born", 2), ("loc_modigliani_note", 0)),
         (("gnd_modigliani_died", 0), ("loc_modigliani_note", 3)), (("gnd_modigliani_died", 2), ("loc_modigliani_note", 2)),
         (("gnd_ando_died", 0), ("loc_ando_note", 0)), (("loc_tobin_cea", 0), ("erp_tobin_office", 1))]
# what other chapters tell: (words of this chapter, chapter where it is told, words there)
EVENTS = [("\\chref{ch:generaltheory}把它写成$C=a+cY$", "ch32_generaltheory", "$C=a+cY$"),
          ("教学例子里边际消费倾向取 0.6，乘数是 2.5（\\exref{ex:generaltheory-cross}）", "ch32_generaltheory",
           "乘数$1/(1-0.6)=2.5$"),
          ("\\chref{ch:islm}把投资写成利率的减函数$I=I_0-bi$", "ch33_islm", "投资$I=I_0-b\\,i$"),
          ("\\chref{ch:generaltheory}讲的是资本边际效率与动物精神", "ch32_generaltheory",
           "\\section{投资、预期与“动物精神”}\\label{sec:generaltheory-expectations}"),
          ("投资随利润与资本存量变，乘数与周期", "ch38_phillips",
           "I&=17.79+0.23\\,\\Pi+0.55\\,\\Pi_{-1}-0.15\\,K_{-1}"),
          ("实际消费反而增加了 2.1\\%，简单的消费函数解释不了", "ch32_generaltheory", "要用别的原因解释"),
          ("按\\chref{ch:prices}的折现", "ch03_prices", "按某个利率折现的现值"),
          ("\\chref{ch:phillips}的模型 I 里，消费是工资总额的 0.80 倍", "ch38_phillips",
           "C&=16.78+0.02\\,\\Pi+0.23\\,\\Pi_{-1}+0.80\\,(W_1+W_2)")]
# the chapters this one hands on to, and those it draws on
LATER = {"ch:ratex": "ch48_ratex", "ch:budget": "ch50_budget", "ch:heterogeneity": "ch71_heterogeneity",
         "ch:pandemic": "ch73_pandemic", "ch:multipliers": "ch68_multipliers", "ch:japanbubble": "ch58_japanbubble",
         "ch:demography": "ch79_demography", "ch:frictions": "ch65_frictions", "ch:eastasia": "ch42_eastasia",
         "ch:rbc": "ch53_rbc", "ch:generaltheory": "ch32_generaltheory", "ch:prices": "ch03_prices",
         "ch:phillips": "ch38_phillips", "ch:islm": "ch33_islm"}
# the chapters that point here
POINTERS = ("ch32_generaltheory", "ch71_heterogeneity")


def book(F, Q):
    """Life dates and what other chapters tell."""
    t = tex_text()
    for words, ((rb, ib), (rd, id_), head_row, head) in LIVES.items():
        assert words in t, words
        assert f"{F[rb][ib]:.0f}—{F[rd][id_]:.0f}" in words, (words, rb, rd)
        assert Q[head_row].startswith(head), (head_row, Q[head_row])             # the person of the record
        COVERED.append(words)
    for words, ((rb, ib), head_row, head) in BORN.items():
        assert words in t, words
        assert f"{F[rb][ib]:.0f} 年生" in words and Q[head_row].startswith(head), words
        COVERED.append(words)
    assert Q["loc_hall"].endswith("1943-") and "gnd_hall_died" not in Q             # no year of death
    assert Q["loc_steindel"] == "Steindel, Charles" and "b. 17/11/1951" in Q["loc_steindel_born"]
    assert "布伦伯格（Richard Brumberg，生卒年未详）" in t and t.count("生卒年未详") == 2   # the text and the 史料说明
    assert "loc_brumberg" not in Q and "gnd_brumberg" not in Q
    assert Q["loc_modigliani"] == "Modigliani, Franco" and "loc_modigliani" not in F       # the heading has no years
    has("loc_modigliani_note", "born 18 June 1918 in Rome", "died 25 September 2003")
    assert Q["loc_ando"] == "Ando, Albert" and "loc_ando" not in F
    assert Q["loc_jorgenson"].endswith("1933-")
    for (r1, i1), (r2, i2) in AGREE:
        assert F[r1][i1] == F[r2][i2], (r1, r2)
    assert "dateOfBirth" in column("juan")["gnd_ando_born"] and "dateOfDeath" in column("juan")["gnd_jorgenson_died"]
    for here, ch, there_ in EVENTS:
        assert here in t, here
        assert there_ in chapter(ch), (ch, there_)
    for label, ch in LATER.items():
        assert f"{{{label}}}" in t, label
        assert f"\\label{{{label}}}" in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (label, ch)
    for ch in POINTERS:
        assert re.search(r"\\(?:chref|ref)\{ch:consumption\}", chapter(ch)), ch
    for lab, ch in (("sec:generaltheory-check", "ch32_generaltheory"), ("ex:generaltheory-cross", "ch32_generaltheory"),
                    ("sec:phillips-models", "ch38_phillips")):
        assert f"{{{lab}}}" in t and f"\\label{{{lab}}}" in chapter(ch), lab
    print(f"ok {len(LIVES) + len(BORN)} life dates, {len(EVENTS)} statements of other chapters, {len(LATER)} other "
          f"chapters named")


# the bibliography item of each source of the snapshot (the authority records: loc39 and gnd39)
ITEM_OF = {"pl9412img": "pl9412", "friedman1957a": "friedman1957", "friedman1957b": "friedman1957",
           "friedman1957c": "friedman1957", "friedman1957d": "friedman1957", "friedman1957img": "friedman1957",
           "kuznets1942img": "kuznets1942", "modigliani1985img": "modigliani1985", "nobel_mod39": "modigliani1985",
           "hall1978img": "hall1978", "hall_pubs39": "hall1978", "hj1967img": "hj1967", "tobin1981img": "tobin1981",
           "nobel_tob39": "tobin1981", "ms1977img": "ms1977", "bpea_ms39": "ms1977", "brookings_terms39": "ms1977",
           "blinder1981img": "blinder1981", "horioka2024img": "horioka2024", "esri_h10": "esri68",
           "esri_goriyou39": "esri2024", "cao_notice39": "esri2024", "cao_rules39": "esri2024",
           "digital_pdl39": "esri2024"}


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
    # the 1975 Act: the President's address and the Statutes; Tobin's office: the Report and the LoC
    assert F["ford_note_law"][0] == F["pl_header"][-1] and F["ford_title"][::2] == [F["pl_header"][4]] * 2
    assert F["loc_tobin_cea"] == [F["erp_tobin_office"][1], F["erp_title"][0]]
    # the rebate of 2001 and the stimulus of 2008 in the later paper's account
    assert F["pa_ref_jps"][1] == F["jps_title"][0] and F["pa_targeted"] == F["jps_title"]
    # the licences
    m = meta()
    lic = m["license"]
    for rid in ("ford_copyright", "fr_copyright", "jps_copyright", "pa_copyright", "kz_copyright", "ho_copyright",
                "ha_issue", "bl_jpe", "bt_licence", "bt_commercial", "bt_property", "md_copyright", "to_copyright",
                "esri_terms", "cao_terms", "cao_rules", "cao_rules_date", "pdl_commercial", "pdl_numbers", "pdl_source",
                "pdl_example", "pdl_edit", "pdl_edit_example", "pdl_notraw", "pdl_ccby", "gnd_licence"):
        assert re.search(r"\brows? [^)]*\b" + rid + r"\b", lic), rid
        assert words_of(rid) in lic, rid
    for words in ("public domain", "Short quotations only", "Short phrases only", "the copies are not committed",
                  "read on 2026-10-29 at https://www.brookings.edu/terms-of-use/", "public data",
                  "Fazzari, Hubbard and Petersen (1987) prints none"):
        assert words in lic, words
    data = load_snapshot("esri_household_saving_1955_2024")[1]
    for rid in ("esri_terms", "cao_terms", "cao_rules", "cao_rules_date", "pdl_commercial", "pdl_numbers", "pdl_source",
                "pdl_example", "pdl_edit", "pdl_edit_example", "pdl_notraw", "pdl_ccby"):
        assert words_of(rid) in data["license"], rid
    assert "を加工して作成" in data["license"] and "出典:" in data["license"]
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    start = bib.index("% ---- 第 39 章")
    following = re.search(r"^% ---- 第 \d+ 章", bib[start + 1:], re.MULTILINE)
    end = start + 1 + following.start() if following else bib.index("\\end{thebibliography}")
    block = bib[start:end]
    assert "data/fetch/consumption39.py" in block and bib.index("% ---- 第 38 章") < start
    items = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", block)}
    allitems = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", bib)}
    assert f"共 {len(items)} 条" in block
    for key in ("ford1975", "pl9412"):
        assert "公有领域" in items[key], key
    assert "公有领域" in allitems["erp1962"]
    for key, rid in (("modigliani1985", "md_copyright"), ("tobin1981", "to_copyright"), ("jps2004", "jps_copyright"),
                     ("parker2011", "pa_copyright"), ("kz2000", "kz_copyright"), ("horioka2024", "ho_copyright"),
                     ("hall1978", "ha_issue"), ("blinder1981", "bl_jpe"), ("friedman1957", "fr_copyright"),
                     ("gnd39", "gnd_licence"), ("esri2024", "cao_rules"), ("esri2024", "pdl_source"),
                     ("esri2024", "pdl_edit")):
        assert words_of(rid) in re.sub(r"\\([$%&_#])", r"\1", items[key]), (key, rid)       # as LaTeX prints it
    for key, rid in (("modigliani1985", "md_title"), ("tobin1981", "to_title"), ("horioka2024", "ho_title")):
        assert words_of(rid).casefold() in items[key].replace("--", "-").casefold(), (key, rid)   # the titles
    assert F["fr_series"][0] == 63 and "General Series 63" in items["friedman1957"]
    for key in ("hall1978", "hj1967"):
        assert "只用来核对，不随本书分发" in items[key], key
    assert "只用来核对，不随本书分发" in items["blinder1981"]
    assert "公共数据" in items["loc39"] and "加工" in items["esri68"] and "加工" in items["esri2024"]
    for words, ((rb, _), _, head_row, _) in LIVES.items():
        if head_row.startswith("loc_"):
            assert Q[head_row].replace("-", "--") in items["loc39"], head_row
    for rid in ("loc_hall", "loc_steindel", "loc_modigliani", "loc_ando"):
        assert Q[rid].replace("-", "--") in items["loc39"], rid
    for rid in ("gnd_ando", "gnd_jorgenson", "gnd_modigliani"):
        assert Q[rid] in items["gnd39"], rid
    # the pages of each work, as the snapshot's rows have them
    df = _rows()
    for key, srcs in (("pl9412", ("pl9412", "pl9412img")), ("modigliani1985", ("modigliani1985", "modigliani1985img")),
                      ("tobin1981", ("tobin1981", "tobin1981img")), ("hall1978", ("hall1978img",)),
                      ("hj1967", ("hj1967img",)), ("ms1977", ("ms1977img",)), ("blinder1981", ("blinder1981",
                                                                                              "blinder1981img")),
                      ("kuznets1942", ("kuznets1942", "kuznets1942img")), ("hayashi1986", ("hayashi1986",))):
        rids = [r.id for r in df.itertuples() if r.file in srcs and re.match(r"pp?\. \d", r.juan)]
        assert pages(rids) in items[key], (key, pages(rids))
    for key in ("jps2004", "parker2011", "fhp1987", "kz2000", "horioka2024"):
        rids = [r.id for r in df.itertuples() if r.file == key and r.juan.startswith("PDF p")]
        assert "PDF " + pages(rids) in items[key], (key, "PDF " + pages(rids))
    # every source of the snapshot, and every workbook of the data snapshot, is named by its URL in its item
    for key, s in m["sources"].items():
        item = "loc39" if key.startswith("loc_") else "gnd39" if key.startswith("gnd_") else ITEM_OF.get(key, key)
        assert s["url"] in allitems[item].replace("\\%", "%").replace("\\_", "_").replace("\\#", "#"), key
    for url in re.findall(r"https://\S+?\.xlsx?", data["notes"]):
        item = items["esri68"] if "/h10/" in url else items["esri2024"]
        assert url in item.replace("\\_", "_"), url
    keys = set(allitems)
    cited = {k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", tex_text()) for k in c.split(",")}
    assert cited <= keys, sorted(cited - keys)
    assert REUSED_KEYS <= cited and not REUSED_KEYS & set(items)
    assert set(items) == cited - REUSED_KEYS, sorted(set(items) ^ (cited - REUSED_KEYS))
    print(f"ok {len(cited)} works cited, {len(items)} in the bibliography block of Chapter 39, "
          f"{len(REUSED_KEYS)} in earlier blocks")


# the modern authors cited in Latin script
NAMES = ("Brady|Rose Friedman|Goldsmith|Blinder|Johnson|Parker|Souleles|McClelland|Fazzari|Hubbard|Petersen|Kaplan|"
         "Zingales|Hayashi|Horioka|Dolde|Brainard|Neisser|Bentzel|Flavin|Hsieh|Shimizutani|Hori")


def counts() -> None:
    """The editor's limits: “不能” at most about a dozen; no cited modern author in Latin script as the subject of a
    sentence outside the 史料说明; the forbidden words; who receives and who pays stated; the three debates left open."""
    t = tex_text()
    main = re.sub(r"\\begin\{deeper\}\[史料说明\].*?\\end\{deeper\}", "", t, flags=re.DOTALL)
    n = t.count("不能")
    print(f"ok “不能” {n} times")
    assert n <= 12, n
    verbs = ("认为|写道|说|指出|记述|估计|承认|报道|记载|提到|列出|给出|发现|统计|算出|早有|看法|有类似|怀疑|强调|写作|推测|"
             "提出|回答|回应|证明|检验|研究|分析")
    subj = re.findall(r"(?:^|[。；：，）\n])\s*(?:Dorothy |按 |据 )?(?:" + NAMES + r")(?:\s*[、与和]\s*(?:" + NAMES +
                      r"))*(?: 等人| 等)?(?:（\d{4}）)?\s*(?:也|还|又|则)?(?:" + verbs + ")", main)
    assert not subj, subj
    for words in ("本书没有找到", "没能取得", "没有取得", "没有读到"):
        assert words not in main, words                                          # only in the 史料说明
    narrative = re.sub(r"“[^”]*”", "", t)                                       # the quotations render the sources
    for bad in ("这一节回答", "不是因为", "而是", "详见", "\\textsc", "\\underline", "\\clearpage"):
        assert bad not in narrative, bad
    assert not re.search(r"(?<![意看])见\\(?:chref|secref|figref|tabref|exref|eqref)", t)
    assert "\\chapterstub" not in t
    # who receives the money and who pays, in the sources' words where they exist
    for words in ("钱发给谁、由谁来付，国会写进了法律", "夫妇合并申报的算作一个人",
                  "那一年不交所得税的人拿不到退税，领上面三种给付的人不论交没交税，都另有 50 美元",
                  "没有交税的低收入家庭因此也能拿到", "“数以百万计的中等收入纳税人”", "联邦税的最大份额本来就是他们交的",
                  "退出去的钱眼下是政府借来的，将来要由纳税人偿还", "得到抵免的是购置机器设备的企业。补上收入缺口的，是股息与利息的收入者、"
                  "扣除招待费的企业、出售可折旧财产的人、合作社与互助金融机构，以及有境外所得的纳税人",
                  "进而增加联邦的收入", "“所有商人和农民”", "照这个规则，2000 年没有所得税的家庭拿不到退税",
                  "2,350 万份没有拿到", "没有申报 2007 年所得税的家庭拿不到", "比 2001 年的退税更偏向低收入家庭",
                  "一次性发钱该发给谁，每一次都要重新决定"):
        assert words in main, words
    # the three debates of the editor's notes are left open
    for words in ("第一个争论", "第二个争论", "第三个争论"):
        assert main.count(words) == 1, words
    debates = main.split("\\subsubsection{")[1:4]
    debates[2] = debates[2][:debates[2].index("\\begin{deeper}") if "\\begin{deeper}" in debates[2] else
                            debates[2].index("\\section{")]
    for d in debates:
        assert d.rstrip().endswith("至今没有定论。"), d[-80:]
    # the inferences are marked
    assert main.count("本书的解读") >= 8 and "本书的计算" in main and "本书的概括" in main
    # sentences: a colon only before a quotation or a list, one semicolon at most
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
    lifecycle(F, Y, Q)
    permanent(F, Y, Q)
    euler(F, Y, Q)
    investment(F, Y, Q)
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
