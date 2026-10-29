"""Chapter 37 (蒙代尔–弗莱明与最优货币区): every number and every quotation in zh/ch37_mundell.tex.

    python3 checks/check_ch37.py

Inputs:
  mundell_facts            quotations of the chapter's sources with their page (Powell's history of the Canadian dollar
                           and the Annual Reports of the Bank of Canada for 1961 and 1962; the headings and rows of
                           Historical Statistics of Canada and of the Economic Report of the President 1964; Fleming
                           1962, Boughton 2003, Mundell 1963, the Nobel press release of 1999, Obstfeld, Shambaugh and
                           Taylor 2004, Rey 2015, Mongelli 2002, the Central Bank of Sri Lanka; the authority records of
                           the Library of Congress and the GND; the licences), checked against the documents by
                           data/fetch/verify_web_quotes.py; data/fetch/mundell37.py fetches the documents
  canada_float_1946_1965   the yearly high, low and average of the Canadian-dollar price of the US dollar and the
                           3-month treasury bill yields of Canada and the United States (the same script)
  intro_facts, external_facts, brettonwoods_facts, bis_fx
                           the rows of Chapters 1, 5 and 36 that this chapter uses again (Russia 1997-98, Sri Lanka
                           2022, West Germany 1961-69, the band of the Bretton Woods parities)

This script

1. reads the numbers of every row from its quotation by the rules of READINGS and compares them with the value column;
2. finds every “…” of the text among the renderings of TRANSLATIONS, and the words of the source each one renders
   (KEYWORDS) in the row;
3. checks each number of the text with said(): the phrase is in the text and each number is the value of a row, a
   teaching input, or arithmetic on them (the open-economy IS-LM of eq:mundell-is to eq:mundell-solution with the
   numbers of Chapter 33, the BP curve, the Canadian series); every Arabic number of the text must lie in a phrase
   said() read (coverage());
4. checks the key equations with random numbers (open_economy() against the closed forms of eq:mundell-solution, the
   rule kappa >< mh/k of the BP curve), the data of the figures (figsrc/fig_ch37.py imports canada(), open_economy()
   and the dates), the life dates against the authority records, what other chapters tell, the licences and the
   bibliography block of Chapter 37, and the editor's limits;
5. lists the rows no "% 据:" anchor of the text names (common.anchors).

Set CH37_TEX to a scratch copy of the chapter to run the checks on it (mutation tests).
"""
from __future__ import annotations

import datetime
import os
import re
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from check_ch33 import M2, POLICY, islm
from common import ROOT, anchors, load_snapshot, quoted

TEX = Path(os.environ.get("CH37_TEX", ROOT / "zh" / "ch37_mundell.tex"))   # a scratch copy for mutation tests
GUIDE = "固定汇率、资本自由流动、独立的货币政策，为什么只能三选二？哪些地区适合共用一种货币？"
PREV = GUIDE                                        # Chapter 36's NEXT
NEXT = "通胀与失业真是一张可以点菜的菜单吗？"            # Chapter 38's question
MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"], 1)}
# the rows of other chapters' snapshots that this chapter uses (each snapshot lists 37 in its used_in)
REUSED = {"intro_facts": ("co_band", "co_gko30", "co_twice", "co_depleted", "co_aug17", "co_sep2"),
          "external_facts": ("lk_adjust", "lk_float"),
          "brettonwoods_facts": ("bo_pegged", "b59_conv", "b61_reval", "b70_de_inflow", "b70_de_float", "bt_de_c",
                                 "b70_fr_flight", "bo_controls_de")}
# works of the bibliography that other chapters' blocks hold and this chapter cites unchanged
REUSED_KEYS = {"cbsl2023ar", "chiodo2002", "bis2026", "bis36", "bordo1993"}


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
    df, m = load_snapshot("mundell_facts", dtype=str, keep_default_na=False)
    assert 37 in m["used_in"] and m["fetch"] == "data/fetch/mundell37.py"
    assert df["id"].is_unique
    return df


@lru_cache(maxsize=None)
def meta() -> dict:
    return load_snapshot("mundell_facts")[1]


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


def words_of(rid: str) -> str:
    return quotes()[rid]


def has(rid: str, *words: str) -> None:
    """Each of the words is in the quotation of row rid."""
    for w in words:
        assert w in words_of(rid), (rid, w)


def mon(rid: str, name: str, said_by=None) -> int:
    """The month `name` (English), asserted to be in what row rid says."""
    (said_by or has)(rid, name)
    return MONTHS[name.lower()]


def page(rid: str) -> int:
    """The first page number of a row's juan column: 'p. 58 (PDF p. 64)' -> 58."""
    return int(re.search(r"pp?\. (\d+)", column("juan")[rid]).group(1))


def chapter(name: str) -> str:
    """Another chapter's text without its comment lines."""
    t = (ROOT / "zh" / f"{name}.tex").read_text(encoding="utf-8")
    return "\n".join(l for l in t.splitlines() if not l.lstrip().startswith("%"))


@lru_cache(maxsize=None)
def other(name: str) -> tuple[dict[str, list[float]], dict[str, str], dict[str, int]]:
    """(values, words, years) of the rows of another chapter's snapshot that this chapter uses; the words are the
    quotation, or the transcription of a page image between « and » in the note."""
    df, m = load_snapshot(name, dtype=str, keep_default_na=False)
    assert 37 in m["used_in"], f"{name}: 37 not in used_in"
    df = df[df["id"].isin(REUSED[name])]
    assert set(df["id"]) == set(REUSED[name]), name
    F = {r.id: [float(x) for x in r.value.split(";")] for r in df.itertuples() if r.value}
    Q = {}
    for r in df.itertuples():
        q = " ".join(r.quote.split())
        if not q:
            q = re.search(r"«(.*)»", r.note).group(1)
        Q[r.id] = q
    Y = {r.id: int(r.year) for r in df.itertuples() if r.year.isdigit()}
    return F, Q, Y


def their(name: str, rid: str, *words: str) -> None:
    """Each of the words is in what row rid of another snapshot says."""
    Q = other(name)[1]
    for w in words:
        assert w in Q[rid], (name, rid, w)


def their_mon(name: str, rid: str, month: str) -> int:
    their(name, rid, month)
    return MONTHS[month.lower()]


@lru_cache(maxsize=None)
def lkr() -> dict[str, float]:
    """The rupee per US dollar at the end of each month (BIS, the snapshot of Chapter 5)."""
    df, m = load_snapshot("bis_fx")
    assert 37 in m["used_in"]
    return dict(zip(df["month"], df["lkr_usd_eop"]))


@lru_cache(maxsize=None)
def canada() -> pd.DataFrame:
    """canada_float_1946_1965 by year: the Canadian-dollar price of the US dollar (high, low, average; e in the book)
    and the 3-month bill yields of Canada and the United States (per cent)."""
    df, m = load_snapshot("canada_float_1946_1965")
    assert 37 in m["used_in"] and m["fetch"].startswith("data/fetch/mundell37.py")
    df = df.set_index("year")
    assert list(df.index) == list(range(1946, 1966))
    return df


def cents(year: int, col: str = "cad_per_usd_avg") -> float:
    """The US-cent price of the Canadian dollar: 100 divided by e."""
    return 100 / canada().loc[year, col]


def bill_spread() -> pd.Series:
    """Canada's 3-month bill yield minus that of the United States, 1946-1963 (percentage points)."""
    C = canada()
    return (C["ca_tbill_3m"] - C["us_tbill_3m"]).dropna()


def dates() -> dict[str, datetime.date]:
    """The dates of the figure: the devaluation of 20 September 1949, the float of 30 September 1950 and the par value
    of 2 May 1962."""
    F = facts()
    d20, y49 = F["pw_sep20"]
    d30, y50, _ = F["pw_abbott"]
    d2, y62 = F["pw_may62"][:2]
    return {"dev49": datetime.date(int(y49), mon("pw_sep20", "September"), int(d20)),
            "float": datetime.date(int(y50), mon("pw_abbott", "September"), int(d30)),
            "par62": datetime.date(int(y62), mon("pw_may62", "May"), int(d2))}


def pars() -> dict[str, float]:
    """The US-cent prices of the two parities: 1949 (US$0.9091) and 1962 (US$0.925)."""
    F = facts()
    return {"1949": 100 * F["pw_1949"][2], "1962": 100 * F["pw_may62"][2]}


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
# listed are read with all the figures of the quotation. An empty list: the row prints no number of the story.
READINGS: dict[str, list[tuple[str, str]]] = {
    'pw_edition': [],
    'pw_images': [],
    'pw_untenable': [],
    'pw_oct2': [('in |1949', 'num'), ('on |2', 'num'), ('October |1950', 'num'), ('rising |five', 'en'), ('US$|0.95', 'num')],
    'pw_letter': [('late |1960', 'num'), ('|twenty-nine', 'en')],
    'pw_consult': [('than |one', 'en'), ('(Abbott |1950', 'num')],
    'pw_ar1960': [('Report |1960', 'num')],
    'pw_sep20': [('|20', 'num'), ('September |1949', 'num')],
    'bc_permit': [],
    'bc_attrib': [],
    'bc_notes': [],
    'bc_logo': [],
    'ar61_principles': [],
    'hs560_title': [('Series J|560', 'num'), ('-|567', 'num'), ('rates, |1913', 'num'), ('to |1977', 'num')],
    'hs560_cols': [],
    'hs560_1949': [(',|1949', 'num'), (',|1.1050', 'num'), (',|1.0000', 'num'), (',|1.0308', 'num')],
    'hs560_1952': [(',|1952', 'num'), (',|1.0113', 'num'), (',|0.9588', 'num'), (',|0.9789', 'num')],
    'hs560_1955': [(',|1955', 'num'), (',|1.0006', 'num'), (',|0.9647', 'num'), (',|0.9863', 'num')],
    'hs560_1957': [(',|1957', 'num'), (',|0.9863', 'num'), (',|0.9422', 'num'), (',|0.9588', 'num')],
    'hs560_1959': [(',|1959', 'num'), (',|0.9819', 'num'), (',|0.9456', 'num'), (',|0.9590', 'num')],
    'hs560_1960': [(',|1960', 'num'), (',|0.9981', 'num'), (',|0.9494', 'num'), (',|0.9697', 'num')],
    'hs471_title': [('Series J|471', 'num'), ('-|480', 'num'), ('averages, |1934', 'num'), ('to |1977', 'num')],
    'hs471_1959': [(',|1959', 'num'), (',|4.81', 'num')],
    'hs471_head': [(',,|3', 'num')],
    'erp_head': [('|3', 'num')],
    'sl_a': [],
    'sl_b': [],
    'erp_1959': [('|1959', 'num'), ('- - |3.405', 'num')],
    'erp_title': [('C-|48', 'num'), ('rates, |1929', 'num'), ('-|63', 'num')],
    'fl_volume': [],
    'bg_dm': [('DM/|61', 'num'), ('/|28', 'num'), ('(November |8', 'num')],
    'os_wp': [('Working Paper |10396', 'num'), ('March |2004', 'num')],
    'os_bwzero': [('only |0.02', 'num')],
    'os_t1': [],
    'os_t1_bw': [('observations |227', 'num'), ('|208', 'num'), ('b a |-.20', 'num'), (' |-.26', 'num'),
                 ('std error |.11', 'num'), (' |.11', 'num'), ('R2 |.02', 'num'), (' |.04', 'num')],
    'ry_wp': [('Working Paper |21162', 'num'), ('May |2015', 'num'), ('February |2018', 'num')],
    'mg_ref_1973': [('(|1973', 'num'), ('pp.|114', 'num'), ('-|32', 'num')],
    'cs_range': [('Rs.|200', 'num'), ('-|203', 'num'), ('early |2022', 'num')],
    'gnd_licence': [],
}


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


# the misreadings of the text layers and the misprints, each printed in the quotation and named in the snapshot's
# notes with its row: (row, as printed in the quotation, the words of the notes that name it)
MISPRINTS = [("bg_dornbusch", "Dornbuseh", "'Dornbuseh' for 'Dornbusch'"),
             ("bg_before", "Mundeil", "'Mundeil' for 'Mundell'"),
             ("bg_vernacular", "Mundelfs", "'Mundelfs' for 'Mundell's'"),
             ("pw_friedman3", "Milton's Friedman's", "Powell prints 'Milton's Friedman's'"),
             ("pw_imfstaff", "recomm e n d e d m o r e", "letter-spaces 'recommended more vigorous foreign exchange'"),
             ("ry_certainly", "cross‐border", "'cross-border' with the Unicode hyphen U+2010")]


def check_readings(df: pd.DataFrame) -> None:
    src = meta()["sources"]
    n = 0
    for r in df.itertuples():
        assert r.file in src, (r.id, r.file)
        assert r.quote, f"{r.id}: no quotation"
        vals = [float(x) for x in r.value.split(";")] if r.value else []
        got = read_row(r.id, " ".join(r.quote.split()))
        assert [round(g, 6) for g in got] == [round(v, 6) for v in vals], f"{r.id}: read {got}, value column {vals}"
        n += bool(vals)
    quoted("rows with values, each read from its quotation", n, 158)
    Q, notes = quotes(), meta()["notes"]
    for rid, word, named in MISPRINTS:
        assert word in Q[rid], (rid, word)                                      # printed in the quotation
        k = notes.find(named)
        m = re.match(r"[^(]{0,80}\(([^)]*)\)", notes[k + len(named):]) if k >= 0 else None
        assert m and rid in re.split(r",\s*", m.group(1)), (rid, named)        # and named, with its row
    # the source keys the chapter cites for its sources
    assert set(src) == set(df["file"]), sorted(set(src) ^ set(df["file"]))
    # the hashes of the documents of the Canadian series are those of the sources of this snapshot
    cm = load_snapshot("canada_float_1946_1965")[1]
    for key in ("hsc_j560", "hsc_j471", "erp1964"):
        assert f"{key} {src[key]['url']}" in cm["notes"] and src[key]["sha256"] in cm["notes"], key


# ---------------------------------------------------------------------------------------------------
# The teaching models
OPEN = {**M2, "m": 0.4, "x": 36, "i_f": 2, "e0": 1.0}          # ex:mundell-fiscal: Chapter 33's M2 opened
SC1 = {"m": 0.2, "x": 18}                                      # self-check 1
SC3 = {"kappa": 4}                                             # self-check 3
CANADA_M = 8                                                   # ex:mundell-canada (3): the money cut from 10 to 8
FIG_BILLS = (1950, 1963)                                       # fig:mundell_canada (b): the years of the bills
OCA = {"N": 100, "shift": 10}                                  # ex:mundell-oca


def open_economy(regime: str, kappa: float | None = None, **change: float) -> dict[str, float]:
    """The open-economy IS-LM of eq:mundell-is with the parameters OPEN (some changed), solved as a linear system in
    (Y, i, e, M) with numpy.linalg.solve:
        IS   (1-c+m) Y + b i - x e = A,      LM   k Y - h i - M/P = 0,
    and, for regime 'peg' (e = e0) or 'float' (M given), the external condition: i = i^f (kappa None, perfect
    mobility, eq:mundell-mobility) or the BP curve x e - m Y + kappa (i - i^f) = 0. Regime 'sterilized': e and M
    both given (a peg in the short run, before the reserves move the money), the balance of payments left open."""
    p = {**OPEN, **change}
    s = 1 - p["c"] + p["m"]
    A = p["a"] - p["c"] * p["T"] + p["I0"] + p["G"]
    rows = [[s, p["b"], -p["x"], 0.0], [p["k"], -p["h"], 0.0, -1 / p["P"]]]
    rhs = [A, 0.0]
    if regime in ("peg", "float"):
        if kappa is None:
            rows.append([0.0, 1.0, 0.0, 0.0])
            rhs.append(p["i_f"])
        else:
            rows.append([-p["m"], kappa, p["x"], 0.0])
            rhs.append(kappa * p["i_f"])
        rows.append([0.0, 0.0, 1.0, 0.0] if regime == "peg" else [0.0, 0.0, 0.0, 1.0])
        rhs.append(p["e0"] if regime == "peg" else p["M"])
    elif regime == "sterilized":
        rows += [[0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]
        rhs += [p["e0"], p["M"]]
    else:
        raise ValueError(regime)
    Y, i, e, M = (float(v) for v in np.linalg.solve(np.array(rows), np.array(rhs)))
    NX = p["x"] * e - p["m"] * Y
    bal = NX + (kappa * (i - p["i_f"]) if kappa is not None else 0.0)
    return dict(Y=Y, i=i, e=e, M=M, NX=NX, bal=bal, s=s, A=A, mult=1 / s, lm_slope=p["k"] / p["h"],
                threshold=p["m"] * p["h"] / p["k"])


def closed_forms(regime: str, **change: float) -> dict[str, float]:
    """eq:mundell-solution: the peg and the float under perfect mobility, in closed form."""
    p = {**OPEN, **change}
    s = 1 - p["c"] + p["m"]
    A = p["a"] - p["c"] * p["T"] + p["I0"] + p["G"]
    if regime == "peg":
        Y = (A + p["x"] * p["e0"] - p["b"] * p["i_f"]) / s
        return dict(Y=Y, M=p["P"] * (p["k"] * Y - p["h"] * p["i_f"]), e=p["e0"])
    Y = (p["M"] / p["P"] + p["h"] * p["i_f"]) / p["k"]
    return dict(Y=Y, e=(s * Y - A + p["b"] * p["i_f"]) / p["x"], M=p["M"])


@lru_cache(maxsize=None)
def model() -> dict[str, dict[str, float]]:
    """The numbers of the examples, the figure and the self-check."""
    dG, dM = POLICY["dG"], POLICY["dM"]
    out = dict(base_peg=open_economy("peg"), base_float=open_economy("float"),
               fiscal_peg=open_economy("peg", G=OPEN["G"] + dG), fiscal_float=open_economy("float", G=OPEN["G"] + dG),
               money_float=open_economy("float", M=OPEN["M"] + dM), canada=open_economy("float", M=CANADA_M),
               sc1_base=open_economy("peg", **SC1), sc1_peg=open_economy("peg", G=OPEN["G"] + dG, **SC1),
               sc1_float=open_economy("float", G=OPEN["G"] + dG, **SC1),
               sc3_ster=open_economy("sterilized", kappa=SC3["kappa"], G=OPEN["G"] + dG),
               sc3_float=open_economy("float", kappa=SC3["kappa"], G=OPEN["G"] + dG),
               sc3_long=open_economy("peg", kappa=SC3["kappa"], G=OPEN["G"] + dG),
               sc3_base=open_economy("sterilized", kappa=SC3["kappa"]))
    # the peg after the open-market purchase: money and income go back; the reserves fall by the purchase
    out["money_peg"] = dict(open_economy("peg"), reserves=-dM / OPEN["e0"])
    return out


# ---------------------------------------------------------------------------------------------------
# 2. Every “…” of the text against the snapshot
# the chapter's Chinese renderings of the quotations: rendering -> row (or rows)
TRANSLATIONS = {
    # the opening
    "此时不为加拿大元确定任何新的固定平价": "pw_abbott2",
    "供求情况": "pw_abbott2",
    "有一个自然的汇率，随经济情况的需要时升时降": "pw_natural",
    "高度的相关性": "mu_canada",
    "庞大的纽约市场": "mu_canada",
    # sec:mundell-world
    "严重受损、十分难堪": "pw_gravely",
    "不那么负责的成员": "pw_gravely",
    "至少起初，浮动被看作临时的措施": "pw_temporary",
    "有点特立独行": "pw_maverick",
    "我得出的结论是，我们最好不要依赖外汇限制": "pw_abbott51",
    # sec:mundell-origins
    "学术上的好奇": "nb_curiosity",
    "蒙代尔–弗莱明模型": "bg_dornbusch",
    "占主导": "nb_depth",
    # sec:mundell-model
    "根本不会增加": "fl_infinite",
    "被动地": "nb_passive",
    "没有实际意义的学术珍品": "fl_curiosum",
    # sec:mundell-canada
    "又因强势的加元而加重，而加元一直有大量的资本流入支撑": "pw_late50s",
    "着眼于避免国内需求过度、控制通胀、减少加拿大对外国储蓄的依赖": ("pw_coyne55", "pw_coyne55b"),
    "不健全而危险的办法": "pw_ar1960",
    "在失业较高、通胀较低的时候实行紧缩的货币政策": "pw_restrictive",
    "决心推行扩张政策的政府，认为自己得不到行长的支持": "pw_expansionary",
    "争执变得越来越尖刻、越来越个人化": "pw_pension",
    "在通常情况下，货币政策由银行负责": "ar61_principles",
    "政府若不赞成银行正在执行的货币政策，它有权利也有责任指示银行执行什么政策": "ar61_principles",
    "顶得住来自任何方面的压力": "ar61_pressures",
    "让位给持不同看法的人": "ar61_resign",
    "很可能大于现在的 3\\%": "pw_weaken",
    "在某种意义上是对基金组织的妥协": "pw_managed",
    "给从事国际交易的人一个汇率稳定的切实保证": "pw_assurance",
    "官员们自然给不了这个保证，尽管他们相信均衡的汇率远在这个水平以上": "pw_officials",
    "人们仍然怀疑新汇率守不守得住，政治的不确定更是如此": "pw_doubts",
    "守住汇率的能力与决心": "ar62_objective",
    "足以带来资本的净流入，弥补国际收支经常账户的逆差，并重建耗减了的外汇储备": "ar62_rates",
    "仍有相当多的失业人力与闲置的生产能力": "ar62_slack",
    "把恢复加拿大的对外地位放在第一位": "ar62_priority",
    "人们普遍担心，加拿大的利率若不相应地提高（大约每年 1 个百分点），来自美国的资本流入就会停止": "pw_iet_fear",
    # sec:mundell-trilemma
    "不相容的三位一体": "nb_trinity",
    "把货币政策用于维持固定的汇率": "pw_fn78",
    "不管美国利率的变化是否适合加拿大的情况": "pw_fn78",
    "基本上关掉了": "os_bwzero",
    "角点解": "os_corner",
    "灰色市场汇率": "cs_spread",
    # sec:mundell-oca
    "不对称冲击": "nb_oca_adv",
    "重新发现": "mg_1973",
    # sec:mundell-debate
    "加拿大 1950 年代大部分时间里成功的浮动汇率试验，激发了大量研究浮动汇率制度优点的早期学术工作": "pw_model",
    "得到许多学院派经济学家的支持，被看作让国内经济免受外来冲击的办法，不论冲击是通胀性的还是通缩性的": "pw_academics",
    "一般就是这样": "fl_equilibrating",
    "极力主张加拿大实行浮动汇率，不要依靠一套外汇管制来平衡贸易": "pw_friedman2",
    "占尽了好处，贸易没有歧视，资本市场开放，汇率也相当稳定": "pw_best",
    "不符合基金组织的惯例，结果却肯定与它的目标一致": "pw_goals",
    "走上了一条反常的路": "pw_fn80",
    "不再逆周期地变动": "pw_fn80b",
    "货币政策、财政政策与债务管理政策相互依赖，某种程度上可以互相替代，必须高度协调，让这些政策的搭配有目的地指向"
    "整个社会的总体经济目标": "ar61_mix",
    "两难": "ry_dilemma",
    "持久而至今仍很相关的约束": "os_strong",
    # the 史料说明: a misreading of the text layer, as printed
    "Dornbuseh": "bg_dornbusch",
    # sec:mundell-legacy and the ending
    "超调": "nb_overshoot",
    "自然的汇率": "pw_natural",
}
# the words of the source that each rendering translates
KEYWORDS = {
    "pw_abbott2": ["not to establish any new fixed parity for the Canadian dollar at this time",
                   "conditions of supply and demand"],
    "pw_natural": ["have a natural rate which could move up or down from time to time as economic conditions might "
                   "require."],
    "mu_canada": ["a high degree of relevance", "the vast New York market"],
    "pw_gravely": ['"gravely compromised and embarrassed"', '"less responsible members"'],
    "pw_temporary": ["At least initially, floating was viewed as a temporary measure."],
    "pw_maverick": ["something of a maverick"],
    "pw_abbott51": ["The conclusion I have come to is that we would be better advised not to rely on exchange "
                    "restrictions"],
    "nb_curiosity": ["an academic curiosity"],
    "bg_dornbusch": ["what he called the Mundell-Fleming model", "Rudiger Dornbuseh"],
    "nb_depth": ["Mundell's contribution predominates"],
    "fl_infinite": ["National income would not increase at all"],
    "nb_passive": ["passively adjusts to the demand for money"],
    "fl_curiosum": ["an academic curiosum without practical significance"],
    "pw_late50s": ["aggravated by its strong dollar, which continued to be supported by substantial capital inflows"],
    "pw_coyne55": ["focused monetary policy on avoiding excessive domestic"],
    "pw_coyne55b": ["demand, keeping inflation in check, and reducing Canada's reliance on foreign savings"],
    "pw_ar1960": ["an unsound and dangerous approach"],
    "pw_restrictive": ["Restrictive monetary policy at a time of relatively high unemployment and low inflation"],
    "pw_expansionary": ["Determined to pursue an expansionary policy, the government did not believe that it had the "
                        "support of the Governor."],
    "pw_pension": ["The dispute, which became increasingly acrimonious and personal"],
    "ar61_principles": ["in the ordinary course of events, the Bank has the responsibility for monetary policy",
                        "if the Government disapproves of the monetary policy being carried out by the Bank it has the "
                        "right and the responsibility to direct the Bank as to the policy which the Bank is to carry "
                        "out"],
    "ar61_pressures": ["to withstand day-to-day pressures from any source"],
    "ar61_resign": ["to make way for someone who took a different view"],
    "pw_weaken": ['"might well turn out to be greater than the present 3 per cent"'],
    "pw_managed": ["was in some ways a compromise with the IMF."],
    "pw_assurance": ["to give those engaged in international transactions firm assurance of stability with regard to "
                     "the exchange rate"],
    "pw_officials": ["Naturally, officials could not give this assurance, despite their belief that an equilibrium "
                     "rate was well above that level."],
    "pw_doubts": ["Doubts remained about the viability of the new rate, particularly given the prevailing political "
                  "uncertainty."],
    "ar62_objective": ["ability and determination to maintain the exchange rate"],
    "ar62_rates": ["help in establishing a net inflow of capital large enough to cover the current account deficit in "
                   "the balance of international payments and rebuild the depleted foreign exchange reserves"],
    "ar62_slack": ["there remained an appreciable amount of unemployed manpower and idle plant capacity"],
    "ar62_priority": ["giving immediate priority to the restoration of Canada\u2019s external position"],
    "pw_iet_fear": ["there was a general fear that unless Canadian interest rates rose by an offsetting amount "
                    "(roughly 1 percentage point per year), capital inflows from the United States would cease."],
    "nb_trinity": ["This incompatible trinity"],
    "pw_fn78": ["to direct monetary policy to maintaining the fixed rate",
                "regardless of whether those interest rate changes were appropriate to Canadian circumstances"],
    "os_bwzero": ["essentially shut down"],
    "os_corner": ['"corner solutions."'],
    "cs_spread": ["'grey market rate,'"],
    "nb_oca_adv": ['"asymmetric shocks"'],
    "mg_1973": ['"rediscovers"'],
    "pw_model": ["Canada's successful experiment with a flexible exchange rate regime through much of the 1950s "
                 "inspired considerable early academic work on the merits of a flexible exchange rate system."],
    "pw_academics": ["was supported by many academic economists as a means of insulating the domestic economy from "
                     "external shocks, either inflationary or deflationary."],
    "fl_equilibrating": ["as was generally the case"],
    "pw_friedman2": ["argued strongly that Canada should introduce a flexible exchange rate rather than relying on a "
                     "system of exchange controls to balance trade."],
    "pw_best": ["the best of all worlds-a non-discriminatory trading system, an open capital market, and a reasonably "
                "stable exchange rate."],
    "pw_goals": ["were not consistent with the IMF's practices, the outcome was certainly in line with its goals."],
    "pw_fn80": ['"domestic monetary policy itself began in these years to follow a perverse road."'],
    "pw_fn80b": ['"ceased to behave in an anti-cyclical manner,'],
    "ar61_mix": ["monetary policy, fiscal policy and debt management policy are interdependent and to some extent "
                 "inter-changeable, there has to be a high degree of coordination to ensure that the blend or "
                 "\u201cmix\u201d of these policies is purposefully directed towards attaining the over-all economic "
                 "objectives of the community."],
    "ry_dilemma": ['"dilemma"'],
    "os_strong": ["a long enduring and still very relevant constraint"],
    "nb_overshoot": ['"overshoot"'],
}


# the third-party content that Powell quotes (Abbott, Coyne's memorandum, Donald Fleming and his office, The Economist,
# Goforth): one clause at most
THIRD_PARTY = {"pw_abbott2", "pw_abbott51", "pw_natural", "pw_weaken", "pw_assurance", "pw_fn80", "pw_fn80b",
               "pw_gravely"}


def tex_text() -> str:
    return "\n".join(l for l in TEX.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("%"))


def text_quotations() -> list[str]:
    """The “…” of the text; the closing question is Chapter 38's and the chapter's own question is in the guide and at
    the end of the opening (both checked by guide() and opening())."""
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 38's question"
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
    # the misreading quoted in the 史料说明 is one of MISPRINTS
    deeper = re.search(r"\\begin\{deeper\}\[史料说明\].*?\\end\{deeper\}", tex_text(), re.DOTALL).group(0)
    assert "“Dornbuseh”" in deeper and ("bg_dornbusch", "Dornbuseh", "'Dornbuseh' for 'Dornbusch'") in MISPRINTS
    # the quotations of the text are short phrases where the source is not the Bank of Canada's (IMF, Cambridge,
    # NobelPrize.org, NBER, ECB, CBSL): at most 12 characters; the Bank's content may be quoted at length
    bank = {r for r in ids if r.startswith(("pw_", "ar61_", "ar62_"))} - THIRD_PARTY
    for q in used:
        t = TRANSLATIONS[q]
        rids = (t,) if isinstance(t, str) else t
        if not set(rids) <= bank:
            limit = 22 if set(rids) <= THIRD_PARTY else 12
            assert len(q) <= limit, f"a long quotation of a source that allows short phrases only: “{q}”"
    print(f"ok {n} quotations of the text found in the snapshot ({len(used)} distinct)")


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


def noted(pattern: str) -> list[int]:
    """The numbers that a pattern of the snapshot's notes captures."""
    m = re.search(pattern, meta()["notes"])
    assert m, pattern
    return [int(g) for g in m.groups()]


def version(key: str) -> str:
    return meta()["sources"][key]["version"]


# ---------------------------------------------------------------------------------------------------
# 4. Numbers, section by section
def guide(F, Y, Q):
    t = TEX.read_text(encoding="utf-8")
    assert f"\\guidequestion{{{GUIDE}}}" in t and GUIDE == PREV
    assert chapter("ch36_brettonwoods").rstrip().endswith(PREV)               # 第 36 章交来的问题
    for label in ("ch:islm", "ch:brettonwoods"):                               # the prerequisites
        assert f"\\chref{{{label}}}\\enspace\\nameref{{{label}}}" in t, label
    said("用它读加拿大 1950—1962 年的浮动汇率", F["pw_abbott"][1], F["pw_may62"][1])
    m61, m63, k69 = F["mg_start"][:3]
    has("mg_start", "Mundell (1961), McKinnon (1963), and Kenen (1969)")
    said("概括蒙代尔（1961）的最优货币区标准，以及麦金农（1963）与凯南（1969）的补充", m61, m63, k69)
    say("把模型用于第一章的俄罗斯与斯里兰卡问题")
    assert "\\chapterstub" not in t


def opening(F, Y, Q):
    d30, y50, d19 = F["pw_abbott"]
    sep = mon("pw_abbott", "September")
    said("1950 年 9 月 30 日是个星期六", y50, sep, d30)
    floated = datetime.date(int(y50), sep, int(d30))
    assert floated.weekday() == 5 and "a Saturday" in column("note")["pw_abbott"]
    has("pw_abbott", "cancelled the official rates of exchange which had been in effect since September 19th of last year")
    said("政府取消了前一年 9 月 19 日起实行的官方汇率", sep, d19)
    _, d2, y50b, five, usd95 = F["pw_oct2"]
    has("pw_oct2", "when markets opened on 2 October 1950")
    opened = datetime.date(int(y50b), mon("pw_oct2", "October"), int(d2))
    assert opened.weekday() == 0                                                 # the Monday
    chk("    two days later (两天以后)", (opened - floated).days, told("两天以后市场开盘", "", "天以后"))
    said("加元很快升到约 95 美分", 100 * usd95)
    # the inflows, the options
    said("1950 年第三季度，人们猜加元又要升值，短期资本的流入急剧增加", F["pw_inflows"][0])
    has("pw_inflows", "particularly through the third quarter of 1950", "speculation regarding a Canadian-dollar revaluation")
    said("放宽上下 1\\% 的波动幅度", F["pw_options"][0])
    has("pw_options", "permitted ±1 per cent fluctuation band", "dismissed as impractical")
    has("pw_revalue", "how much of a revaluation would be required")
    has("pw_bands", "how wide the bands would have to be")
    has("pw_untenable", "for a country dependent on foreign capital")
    # Coyne's memorandum
    said("浮动的主意，1949 年初就有人讨论", F["pw_early49"][0])
    has("pw_early49", "as early as the beginning of 1949")
    said("那年 1 月写了一份当时保密的备忘录", mon("pw_coyne49", "January"))
    has("pw_coyne49", "then-secret memorandum", "while retaining exchange controls")
    has("pw_inertia", "government inertia")
    # Mundell, and the question
    assert Y["mu_assume"] == F["mu_issue"][2] == F["mu_presented"][1]
    said("他 1963 年的论文假定资本完全流动", Y["mu_assume"])
    has("mu_assume", "cannot maintain an interest rate different from the general level prevailing abroad")
    has("nb_born", "born in Canada in 1932")
    d14, y51 = F["pw_dec51"]
    revoked = datetime.date(int(y51), mon("pw_dec51", "December"), int(d14))
    chk("    a little over a year later (一年多以后)", (revoked - floated).days // 365,
        told("一年多以后又取消了外汇管制", "", "年多以后"))
    assert (revoked - floated).days > 365
    _, _, Y36 = other("brettonwoods_facts")
    chk("    nineteen years later (十九年以后的西德)", Y36["b70_de_inflow"] - floated.year,
        told("十九年以后的西德钉住了汇率，就挡不住流进来的钱", "", "年以后"))
    assert paragraph("蒙代尔（Robert Mundell").endswith(GUIDE)                  # the opening ends with the question


def world(F, Y, Q):
    F36, _, Y36 = other("brettonwoods_facts")
    their("brettonwoods_facts", "bo_pegged", "within 1% of parity with the dollar")
    said("在平价上下 1\\% 以内维持汇率", F36["bo_pegged"][0])
    d19, y49, pct = F["pw_fn75"]
    has("pw_fn75", "excluding Pakistan")
    said("1949 年 9 月 19 日，英镑与巴基斯坦以外的英镑区货币对美元贬值 30.5\\%", y49, mon("pw_fn75", "September"), d19,
         pct)
    y46, cad110, usd9091 = F["pw_1949"][:3]
    has("pw_dev49a", "following a major realignment of the pound sterling", "against its U.S. counterpart on")
    said("加元随着贬值约 9.1\\%，回到 1946 年 7 月以前的比价，每美元 1.10 加元", F["pw_dev49a"][0], y46,
         mon("pw_1949", "July"), cad110)
    chk("    1 - 1/1.10 (about 9.1%)", 100 * (1 - 1 / cad110), F["pw_dev49a"][0], tol=0.05)
    chk("    US$0.9091 = 1/1.10", 1 / cad110, usd9091, tol=5e-5)
    assert F["pw_par49"][:2] == [y49, usd9091]
    said("这个平价在基金组织登记，波动的幅度也是上下 1\\%", F["pw_par49"][2])
    # the Fund
    has("pw_imfstaff", "over the opposition of IMF staff", "the imposition of controls on capital inflows (IMF 1950)")
    has("pw_gravely", "(Goforth 1950)", "set a bad example")
    has("pw_fn79", "close relationship with the IMF", "the economic argument in favour of a float was sound")
    has("ar61_ed", "over the past years in my capacity of Executive Director of the International Monetary Fund")
    said("1961 年以前多年任基金组织与世界银行的执行董事", Y["ar61_ed"])
    y30, y99, _ = F["pw_fn79b"]
    has("pw_fn79b", "inflation not deflation", "no tendency towards competitive devaluations")
    said("据 Powell 引述的 Muirhead（1999），与 1930 年代不同", y99, y30)
    # Abbott's assurance; almost twelve years
    one, y50 = F["pw_consult"]
    has("pw_consult", "ultimately to conform to the provisions of the Fund's Articles of Agreement")
    said("最终遵守协定里汇率不得偏离平价 1\\% 以上的规定", one)
    said("可加拿大将近 12 年以后才重新钉住汇率", F["pw_almost12"][0])
    D = dates()
    span = (D["par62"] - D["float"]).days / 365.25
    assert F["pw_almost12"][0] - 1 < span < F["pw_almost12"][0]                # almost 12 years
    chk("    the twelve years of the section title", told("\\section{加拿大的十二年}", "的", "年"), F["pw_almost12"][0])
    # the controls go
    assert "December 1951" in column("note")["pw_abbott51"]
    said("1951 年 12 月，阿博特在演说里说", Y["pw_abbott51"], MONTHS["december"])
    said("同月 14 日，外汇管制条例被撤销", F["pw_dec51"][0])
    has("pw_dec51", "on 14 December 1951, the Foreign Exchange Control Regulations were revoked")
    said("《外汇管制法》本身 1952 年 10 月废止", F["pw_repealed"][1], mon("pw_repealed", "October"))
    # the opening world
    say("蒙代尔 1963 年写道")
    COVERED.append("蒙代尔 1963 年写道")
    assert Y["mu_closed"] == 1963
    has("mu_closed", "The world is still a closed economy")
    said("以及 1914 年以来从未有过的汇率稳定", F["mu_stability"][0])
    has("mu_stability", "unparalleled since 1914")
    their("brettonwoods_facts", "b59_conv", "at the end of December 1958")
    said("西欧 1958 年底恢复了经常账户的可兑换", F36["b59_conv"][0])


def origins(F, Y, Q):
    said("1954 年进入国际货币基金组织的研究部", F["bg_fleming54"][0])
    has("bg_fleming54", "Advisor in charge of the Sp")
    said("在基金组织工作到 1976 年去世", F["bg_death"][0])
    assert F["nb_fleming"][0] == F["bg_death"][0] == F["loc_fleming_jm"][1]
    said("蒙代尔 1961 年 8 月正式加入研究部", F["bg_mundell61"][0], mon("bg_mundell61", "August"))
    has("bg_mundell61", "until mid-September", "from Italy (where he had been teaching)")
    said("9 月中才从任教的意大利到任", mon("bg_mundell61", "September"))
    has("nb_imf", "apparently stimulated Mundell's choice of research problems")
    dm61, dm28, d8 = F["bg_dm"]
    assert F["bg_draft"][0] == 1900 + dm61 and dm28 == 28
    has("bg_dm", "Internal Financial Policies Under Fixed and Floating Exchange Rates")
    said("1961 年 11 月 8 日，弗莱明在基金组织内部印发了论文的初稿", F["bg_draft"][0], mon("bg_draft", "November"), d8)
    y62, vol9, _, _ = F["bg_ref_fleming"]
    has("bg_ref_fleming", "Domestic Financial Policies Under Fixed and Under Floating Exchange Rates", "( November ,)")
    has("fl_volume", "Volume 1962: Issue 003")
    said("1962 年 11 月发表在基金组织的《工作人员论文》上", y62, mon("bg_ref_fleming", "November"))
    has("bg_before", "substantially completed before he and Mundeil met")
    has("bg_evidence", "derived independently and approximately contemporaneously")
    has("mu_title", "Capital Mobility and Stabilization Policy Under Fixed and Flexible Exchange Rates")
    d6, y63 = F["mu_presented"]
    has("mu_presented", "in Quebec on June 6, 1963")
    said("它 1963 年 6 月 6 日在魁北克的加拿大政治学会年会上宣读，同年 11 月发表", y63, mon("mu_presented", "June"), d6,
         mon("mu_issue", "November"))
    has("mu_presented", "It was written while the autho")
    # the Nobel's curiosity
    has("nb_almost", "Almost all countries were linked together by fixed exchange rates")
    has("nb_curtailed", "extensive capital and exchange rate controls")
    has("nb_relevant", "over the next ten years", "the Bretton Woods System broke down")
    chk("    the next ten years (此后十年)", told("此后十年，国际资本市场开放", "此后", "年"), cardinal("ten"))
    said("1950 年代就让加元对美元浮动", F["nb_canada"][0])
    has("nb_canada", "had allowed its currency to float against the US dollar")
    # the name
    said("1976 年，这些贡献在 Dornbusch 的一系列论文里被归纳为", F["bg_dornbusch"][0])
    has("bg_vernacular", "Fleming's equations combined with Mundelfs policy analysis")
    has("bg_equally", "at least equally justified")
    d13, y99, _ = F["nb_date"]
    said("1999 年，蒙代尔因为分析不同汇率制度下的货币政策与财政政策、分析最优货币区，获得诺贝尔经济学奖", y99)
    has("nb_citation", "monetary and fiscal policy under different exchange rate regimes", "optimum currency areas")
    has("nb_same", "At approximately the same time as Mundell, Fleming presented similar research")
    said("\\begin{compare}{弗莱明（1962）与蒙代尔（1963）}{弗莱明（1962）}{蒙代尔（1963）}", y62, y63, y62, y63)
    has("fl_infinite", "infinitely elastic with respect to the interest rate")
    has("fl_insensitive", "entirely insensitive to the rise in the rate of interest")
    has("fl_money", "will always be greater if the country has a floating exchange rate than if it has a fixed rate")
    has("mu_fiscal", "financed by government bond issues with no change in the money supply")
    has("mu_omo", "which only temporarily changes the money supply")
    has("fl_rhomberg", "an econometric model of the Canadian economy", "over a large part of the postwar period")
    has("mu_rhomberg", "the applicability of the conclusions to the Canadian case")


def model_section(F, Y, Q):
    m, p = model(), OPEN
    b0, fp, ff, mf, mp = m["base_peg"], m["fiscal_peg"], m["fiscal_float"], m["money_float"], m["money_peg"]
    dG, dM = POLICY["dG"], POLICY["dM"]
    said("乘数从$1/(1-c)$降到$1/(1-c+m)$", 1, 1, 1, 1)
    # Law's peg (Chapter 16)
    y1720, m3, d5, liv = there("ch16_mercantilism", "1720 年 3 月 5 日起，公司按 9,000 里弗尔钉住股价")
    b1671, d1729 = there("ch16_mercantilism", "约翰·劳（John Law，1671—1729）")
    said("1720 年 3 月 5 日起，约翰·劳（John Law，1671—1729）让印度公司按每股 9,000 里弗尔买卖自己的股份", y1720, m3, d5,
         b1671, d1729, liv)
    # ex:mundell-fiscal
    said("接\\exref{ex:islm-equilibrium}，$a=26$，$c=0.6$，$I=14-2i$，$k=0.2$，$h=4$，$M=10$，$P=1$。再设$m=0.4$，$x=36$，"
         "$i^{f}=2$，汇率起初$e=1$，数字为教学输入", p["a"], p["c"], p["I0"], p["b"], p["k"], p["h"], p["M"], p["P"],
         p["m"], p["x"], p["i_f"], p["e0"])
    said("（1）验证起初$Y=90$，净出口为 0", b0["Y"], b0["NX"])
    said("（2）钉住$\\bar e=1$，政府支出$G$从 0 增加到 4", p["e0"], p["G"], p["G"] + dG)
    s = b0["s"]
    said("IS 是$0.8\\times90=72=40+36-2\\times2$，LM 是$10=0.2\\times90-4\\times2$，$\\mathit{NX}=36-0.4\\times90=0$",
         s, b0["Y"], s * b0["Y"], b0["A"], p["x"] * p["e0"], p["b"], p["i_f"], p["M"], p["k"], b0["Y"], p["h"],
         p["i_f"], p["x"], p["m"], b0["Y"], b0["NX"])
    assert abs(s * b0["Y"] - (b0["A"] + p["x"] - p["b"] * p["i_f"])) < 1e-9
    said("$0.8Y=44+36-4=76$，$Y=95$，乘数$5/4=1.25$", s, fp["A"], p["x"], p["b"] * p["i_f"], s * fp["Y"], fp["Y"],
         fp["Y"] - b0["Y"], dG, fp["mult"])
    chk("    the multiplier 1/(1-c+m) = dY/dG", (fp["Y"] - b0["Y"]) / dG, fp["mult"], tol=1e-9)
    said("货币需求$0.2\\times95-4\\times2=11$，中央银行按$\\bar e$买进 1 单位外汇，货币从 10 增加到 11", p["k"], fp["Y"],
         p["h"], p["i_f"], fp["M"], (fp["M"] - b0["M"]) / p["e0"], b0["M"], fp["M"])
    said("净出口$36-0.4\\times95=-2$", p["x"], p["m"], fp["Y"], -fp["NX"])
    closed = islm(G=M2["G"] + dG)
    said("与\\exref{ex:islm-policy}的 98 相比", closed["Y"])
    assert closed["i"] > p["i_f"]                                              # the closed economy's rate rose
    said("$M=10$不变，由式~\\eqref{eq:mundell-solution}，$Y=(10+4\\times2)/0.2=90$", p["M"], p["M"], p["h"], p["i_f"],
         p["k"], ff["Y"])
    said("$36e=0.8\\times90-44+2\\times2=32$，$e=8/9\\approx0.89$，本币升值约 11\\%", p["x"], s, ff["Y"], ff["A"], p["b"],
         p["i_f"], p["x"] * ff["e"], 8, 9, ff["e"], 100 * (1 - ff["e"]))
    chk("    e = 8/9", ff["e"], 8 / 9, tol=1e-12)
    said("净出口$32-36=-4$，正好抵消政府多花的 4", p["x"] * ff["e"], ff["Y"] * p["m"], -ff["NX"], dG)
    assert abs(ff["NX"] + dG) < 1e-9
    # ex:mundell-money
    said("接\\exref{ex:mundell-fiscal}的起点，$G=0$。中央银行买进 4 的国债，货币从 10 增加到 14", p["G"], dM, p["M"],
         p["M"] + dM)
    said("（2）钉住$\\bar e=1$呢", p["e0"])
    said("$Y=(14+8)/0.2=110$", mf["M"], p["h"] * p["i_f"], p["k"], mf["Y"])
    said("$36e=0.8\\times110-40+4=52$，$e=13/9\\approx1.44$，本币贬值约 44\\%", p["x"], s, mf["Y"], mf["A"],
         p["b"] * p["i_f"], p["x"] * mf["e"], 13, 9, mf["e"], 100 * (mf["e"] - 1))
    chk("    e = 13/9", mf["e"], 13 / 9, tol=1e-12)
    said("净出口$52-0.4\\times110=8$", p["x"] * mf["e"], p["m"], mf["Y"], mf["NX"])
    closed_m = islm(M=M2["M"] + dM)
    said("收入增加 20，等于$\\Delta M/k=4/0.2$，比\\exref{ex:islm-policy}的 4 大得多", mf["Y"] - b0["Y"], dM, p["k"],
         closed_m["Y"] - islm()["Y"])
    chk("    dY = dM/k", (mf["Y"] - b0["Y"]) * p["k"], dM, tol=1e-9)
    said("货币需求仍是$0.2\\times90-4\\times2=10$，多出的 4 全部换走，储备减少 4 单位外汇，货币回到 10，收入仍是 90", p["k"],
         mp["Y"], p["h"], p["i_f"], mp["M"], dM, -mp["reserves"], mp["M"], mp["Y"])
    said("$\\Delta M=\\bar e\\,\\Delta R=-4$，抵消了买国债的 4", -p["e0"] * mp["reserves"], dM)
    v60, v6, v10 = there("ch01_intro", "储备减少 $60/6=10$ 亿美元")
    said("\\exref{ex:intro-peg}里多发的 60 亿本币换走了 10 亿美元的储备", v60 * 1e8, v10 * 1e8)
    assert v60 / v6 == v10
    # the Nobel's summary, Mundell's definitions
    has("nb_result", "monetary policy becomes powerful and fiscal policy powerless")
    has("mu_money", "cannot in any meaningful sense be defined as an alteration in the interest rate",
        "the central bank has no power over the money supply either")
    said("蒙代尔 1963 年说得更绝", Y["mu_money"])
    # the compare box
    said("\\cmprow{汇率}{不变，中央银行按$\\bar e$买进外汇}{本币升值，例中约 11\\%}", 100 * (1 - ff["e"]))
    said("\\cmprow{货币数量}{跟着需求增加，例中从 10 到 11}", b0["M"], fp["M"])
    said("\\cmprow{收入}{增加，乘数是$1/(1-c+m)$，例中 1.25}", 1, 1, fp["mult"])
    said("\\cmprow{净出口}{随进口增加而减少，例中为$-2$}{减少 4，正好抵消多花的支出}", -fp["NX"], -ff["NX"])
    # the pitfall
    has("mu_fn5", "both monetary and fiscal policies are more effective under flexible exchange rates")
    has("mu_fn5_1961", "Employment Policy Under Flexible Exchange Rates")
    assert "November 1961" in column("note")["mu_fn5_1961"] and F["mu_fn5_1961"][1:3] == [11, 1961]
    said("蒙代尔自己 1961 年 11 月的论文还说过", F["mu_fn5_1961"][2], F["mu_fn5_1961"][1])
    assert column("file")["mu_fn5"] == "mundell1963"                           # footnote 5 of the paper of 1963
    said("照他 1963 年的解释", F["mu_issue"][2])
    has("mu_earlier", "with interest rates maintained constant by the central bank")
    # the BP curve
    said("国际收支平衡要求$\\mathit{NX}+\\kappa\\,(i-i^{f})=0$", 0)
    said("LM 的斜率是$k/h$，例中是 0.05，所以$\\kappa$大于$mh/k=8$时 BP 比 LM 平", b0["lm_slope"], b0["threshold"])
    has("fl_appreciation", "it will, with a floating rate, lead to an exchange appreciation")
    has("fl_greater", "will be greater with a floating exchange rate than with a fixed exchange rate")
    # the figure
    said("水平线是$i=i^{f}=2$。(a) 钉住汇率，政府支出增加 4，IS 右移，货币跟着增加，LM 也右移，收入从 90 到 95。(b) 浮动汇率，"
         "同样增加支出，本币升值约 11\\%，IS 回到原处，收入仍是 90。(c) 浮动汇率，货币增加 4，LM 右移，本币贬值约 44\\%，IS 也"
         "右移，收入到 110。(d) 钉住汇率，同样增加货币，储备减少 4，LM 回到原处", p["i_f"], dG, b0["Y"], fp["Y"],
         100 * (1 - ff["e"]), ff["Y"], dM, 100 * (mf["e"] - 1), mf["Y"], -mp["reserves"])
    chk("    the IS of (b) back in place: A + x e", ff["A"] + p["x"] * ff["e"], b0["A"] + p["x"] * p["e0"], tol=1e-9)
    chk("    four panels (四种情形)", told("画出了资本完全流动时的四种情形", "的", "种情形"), 4)


def canada_section(F, Y, Q):
    C, S = canada(), bill_spread()
    two, y52, y60, lo, hi, peak, d20, y57 = F["pw_premium"]
    said("到 1952 年，加元对美元有了约 2\\% 的溢价", y52, two)
    has("pw_premium", "a small premium of about 2 per cent")
    c = {y: cents(y) for y in range(int(y52), int(y60) + 1)}
    said("1952—1960 年 1 加元合 101.4 到 104.3 美分", y52, y60, 1, min(c.values()), max(c.values()))
    said("最高是 1957 年 8 月 20 日的约 106 美分", y57, mon("pw_premium", "August"), d20, 100 * peak)
    has("pw_efa", "limited to smoothing short-run fluctuations")
    # the inflows and the bill spread
    said("1950 年代后期", F["pw_late50s"][0])
    has("pw_late50s", "During the late 1950s")
    last = dates()["par62"].year                                               # to the year of the peg
    first = last
    while S.loc[first - 1] > 0:                                                # the run of years above the US
        first -= 1
    sp = S.loc[first:last]
    said("1956—1962 年，加拿大 3 个月国库券的年均收益率每年都高于美国，高出约 0.3 到 1.4 个百分点", first, last,
         F["hs471_head"][0], sp.min(), sp.max(), slack=0.05)
    assert F["erp_head"][0] == F["hs471_head"][0] == 3
    # Coyne
    d1, y55 = F["pw_coyne55"]
    said("科因 1955 年 1 月 1 日起任加拿大银行行长", y55, mon("pw_coyne55", "January"), d1)
    has("pw_boom", "After the investment boom of the mid-1950s")
    said("1950 年代中期的投资热潮过后", F["pw_boom"][0])
    u56, y56, u61, y61 = F["pw_unemp"]
    said("失业率从 1956 年的 3.4\\% 升到 1961 年的 7.2\\%，翻了一番还多", y56, u56, y61, u61)
    assert u61 / u56 > 2 and "more than doubled" in Q["pw_unemp"]
    has("pw_unemp", "the government sought to ease policy")
    said("科因在 1960 年的年报里说", F["pw_ar1960"][0])
    has("pw_ar1960", "(Bank of Canada Annual Report 1960, 22)")
    has("pw_restrictive2", "Bank and the academic community.")
    y60b, n29 = F["pw_letter"]
    said("1960 年底，29 位知名的加拿大经济学家联名写信，要求撤换科因", y60b, n29)
    has("pw_letter", "In late 1960", "calling for the dismissal of Governor Coyne")
    has("pw_diefgov", "relations with the Diefenbaker government were also deteriorating")
    # ex:mundell-canada
    e57, e59, e60 = (C.loc[y, "cad_per_usd_avg"] for y in (1957, 1959, 1960))
    ca59, us59 = C.loc[1959, "ca_tbill_3m"], C.loc[1959, "us_tbill_3m"]
    said("加元的年均汇率 1957 年是每美元 0.9588 加元，1959 年是 0.9590，1960 年是 0.9697", 1957, e57, 1959, e59, 1960, e60)
    said("1959 年 3 个月国库券的年均收益率，加拿大是 4.81\\%，美国是 3.405\\%", 1959, F["hs471_head"][0], ca59, us59)
    said("（1）1957 年 1 加元合多少美元", 1957, 1)
    said("1959 年的利差意味着人们预期加元贬值多少？1960 年加元实际贬了多少", 1959, 1960)
    m = model()["canada"]
    said("若中央银行把货币从 10 减到 8", OPEN["M"], CANADA_M)
    said("$1/0.9588\\approx1.043$，溢价约 4.3\\%，在 Powell 说的 102 到 106 美分以内", 1, e57, 1 / e57, 100 * (1 / e57 - 1),
         100 * lo, 100 * hi)
    assert lo < 1 / e57 < hi
    g = (1 + ca59 / 100) / (1 + us59 / 100)
    said("$\\E_t e_{t+1}/e_t=1.0481/1.03405\\approx1.014$，预期$e$上升约 1.4\\%", 1 + ca59 / 100, 1 + us59 / 100, g,
         100 * (g - 1))
    said("1960 年$0.9697/0.9590\\approx1.011$，加元贬了约 1.1\\%", 1960, e60, e59, e60 / e59, 100 * (e60 / e59 - 1))
    has("hs471_note", "Twelve-month average of last Thursday in each month", "Prior to 1954, average of weekly tenders")
    has("erp_fn1", "Rate on new issues within period")
    s = m["s"]
    said("$Y=(8+8)/0.2=80$。$36e=0.8\\times80-40+4=28$，$e=7/9\\approx0.78$，本币升值约 22\\%；净出口$28-0.4\\times80=-4$",
         CANADA_M, OPEN["h"] * OPEN["i_f"], OPEN["k"], m["Y"], OPEN["x"], s, m["Y"], m["A"], OPEN["b"] * OPEN["i_f"],
         OPEN["x"] * m["e"], 7, 9, m["e"], 100 * (1 - m["e"]), OPEN["x"] * m["e"], OPEN["m"], m["Y"], -m["NX"])
    chk("    e = 7/9", m["e"], 7 / 9, tol=1e-12)
    said("正是 1950 年代末加拿大的抱怨", F["pw_late50s"][0])
    # fig:mundell_canada
    D, P = dates(), pars()
    said("加拿大的浮动汇率，1946—1965 年。(a) 1 加元合多少美分（年均汇率的倒数），浅色的竖条是当年的最高价与最低价；虚线是 1949 年"
         " 9 月的官价与 1962 年 5 月 2 日的平价 92.5 美分，灰色的区间是 1950 年 9 月 30 日到 1962 年 5 月 2 日的浮动。(b) 3 个月"
         "国库券的年均收益率，加拿大与美国，1950—1963 年（\\%）；灰色的柱是两者之差。两国的口径不同，加拿大是每月最后一个星期四的平均"
         "（1954 年以前是每周投标的平均），美国是新发行的利率。数据：《加拿大历史统计》表 J560—567、J471—480（加拿大统计局）；"
         "美国《总统经济报告》1964 年表 C-48", C.index[0], C.index[-1], 1, F["pw_fn75"][1], mon("pw_fn75", "September"), D["par62"].year,
         D["par62"].month, D["par62"].day, P["1962"], D["float"].year, D["float"].month, D["float"].day, D["par62"].year,
         D["par62"].month, D["par62"].day, F["hs471_head"][0], FIG_BILLS[0], FIG_BILLS[1], F["hs471_note"][2],
         *F["hs560_title"][:2], *F["hs471_title"][:2], Y["erp_title"], F["erp_title"][0])
    assert FIG_BILLS[1] == int(S.index[-1]) and FIG_BILLS[0] == D["float"].year and F["hs471_note"][0] == 1954
    # 1961: the quarrel
    d30, y61b = F["pw_pension"]
    said("冲突在 1961 年变成了个人的", y61b)
    said("5 月 30 日，政府要求科因辞职，他拒绝了", mon("pw_pension", "May"), d30)
    has("pw_pension", "with the government requesting the resignation of Governor Coyne. The Governor refused.")
    d20b = F["pw_budget61"][0]
    said("6 月 20 日，财政部长唐纳德·弗莱明（Donald Fleming，1905—1986）提出扩张性的预算", mon("pw_budget61", "June"), d20b,
         F["loc_fleming_dm"][0], F["loc_fleming_dm"][1])
    has("pw_budget61", "take steps to lower the value of the Canadian dollar", "purchasing substantial amounts of U.S. dollars")
    assert "Donald Fleming's budget speech" in column("note")["pw_budget61"]
    COVERED.append("Donald Fleming，1905—1986")
    # the bill, the Senate, the resignation
    has("pw_bill", "to declare the position of Governor vacant", "passed the House of Commons on 7 July")
    said("法案 7 月 7 日在下院通过，参议院的委员会听了科因的证词，7 月 12 日认定他没有失职", mon("pw_bill", "July"),
         F["pw_bill"][1], mon("pw_senate", "July"), F["pw_senate"][0])
    has("pw_senate", "there had been no misconduct")
    has("pw_resigned", "The following day, the full Senate confirmed", "as a vindication of his conduct")
    d24, y61c, d13 = F["ar61_coyne"]
    has("ar61_coyne", "On July 24, 1961", "who resigned on July 13")
    said("7 月 24 日，加拿大银行的董事会宣布拉斯明斯基继任行长", mon("ar61_coyne", "July"), d24)
    # Rasminsky's statement
    d1b, y61d = F["ar61_statement"]
    said("8 月 1 日，拉斯明斯基发表声明，提出两条原则", mon("ar61_statement", "August"), d1b)
    has("ar61_principles", "(1) in the ordinary course of events", "and (2) if the Government")
    assert told("提出两条原则", "提出", "条") == 2 and "(3)" not in Q["ar61_principles"]
    has("ar61_known", "made known to the Directors and to the Government")
    has("ar61_first", "The first principle is designed to ensure")
    has("ar61_conflict", "a serious and persistent conflict", "after prolonged and conscientious efforts on both sides")
    has("ar61_instruct", "formally to instruct the Bank", "direct responsibility for the monetary policy")
    has("ar61_resign", "his duty would be to resign")
    has("ar61_harmony", "are in harmony with those of the Government")
    # the exchange rate follows the policy
    a101, a97, y61e, a96, three, y61f = F["pw_weaken"]
    said("预算以前 1 加元约合 101 美分，预算以后很快跌到 97 美分", 1, 100 * a101, 100 * a97)
    said("10 月，唐纳德·弗莱明宣布，加元对美元合适的折价“很可能大于现在的 3\\%”，加元又跌到 96 美分以下",
         mon("pw_weaken", "October"), three, 100 * a96)
    chk("    the discount of 3 per cent: 100 - 97", 100 - 100 * a97, three, tol=0.5)
    has("pw_managed", "was in some ways a compromise with the IMF")
    has("pw_fundfix", "to return to a fixed exchange rate regime")
    u95, y61g, y62 = F["pw_stab"]
    said("1961 年 11 月到 1962 年 3 月，加元稳定在约 95 美分", y61g, mon("pw_stab", "November"), y62, mon("pw_stab", "March"),
         100 * u95)
    has("pw_stab", "despite significant intervention by the Bank of Canada on behalf of the government")
    # 2 May 1962
    d2, y62b, par, band = F["pw_may62"]
    said("1962 年 5 月 2 日，政府经基金组织同意，把加元钉在 92.5 美分，波动幅度上下 1\\%", y62b, mon("pw_may62", "May"), d2,
         100 * par, band)
    has("ar62_band", "within one per cent on either side of the par value")
    has("pw_assurance", "the Government has concluded that it would be desirable")
    p925, p95, p90 = F["pw_fn84"][:3]
    said("选这个数，是因为它在 95 与 90 美分的正中", 100 * p95, 100 * p90)
    chk("    halfway between 95 and 90", (p95 + p90) / 2, p925, tol=1e-12)
    has("pw_fn84", "halfway between US$0.95 and US$0.90 (Helliwell 2005-06)")
    said("唐纳德·弗莱明要的是加元即使自由浮动也不会跌破 90 美分的保证", 100 * F["pw_fn84a"][0])
    has("pw_fn84a", "It has been reported that Fleming wanted assurances")
    has("pw_pressure", "did not, however, relieve the pressure")
    has("pw_heavy", "Heavy official intervention was therefore required")
    d18, y62c = F["pw_fn85"]
    said("6 月 18 日的大选，保守党只赢得少数派政府", mon("pw_fn85", "June"), d18)
    has("pw_fn85", "a minority Conservative government was elected")
    # the case: June 1962
    said("\\begin{case}{加拿大 · 1962 · 六月的紧急方案}", y62c)
    chk("    June (六月)", told("加拿大 · 1962 · 六月的紧急方案", "1962 · ", "月的"), mon("ar62_jun24", "June"))
    r1100, d24b, r2056 = F["ar62_reserves"]
    has("ar62_reserves", "on June 24 compared with $U.S. 2,056 million at the beginning of the year")
    said("年初是 20.56 亿美元，6 月 24 日只剩约 11 亿美元", r2056 * 1e6, mon("ar62_reserves", "June"), d24b, r1100 * 1e6)
    assert F["ar62_jun24"][0] == d24b
    chk("    the sixth day after the election (第六天)", d24b - d18, told("这一天是大选以后的第六天", "第", "天"))
    has("ar62_jun24", "the Prime Minister issued a statement", "at the level established in May")
    said("政府决心把加元的对外价值守在 5 月定下的水平", mon("ar62_jun24", "May"))
    assert mon("ar62_jun24", "May") == mon("pw_may62", "May")
    said("加拿大银行同日把银行利率定为 6\\%", F["ar62_bankrate"][0])
    has("ar62_bankrate", "the minimum rate at which the Bank of Canada makes advances to chartered banks")
    has("ar62_duty", "to protect the external value of the national monetary unit")
    m250, m1050 = F["ar62_measures"]
    has("ar62_measures", "reductions in Government expenditure amounting to $250 million in a full fiscal year")
    said("在一个完整的财政年度里削减政府支出 2.5 亿加元", m250 * 1e6)
    said("合计 10.5 亿美元", m1050 * 1e6)
    imf300 = F["ar62_parts"][0]
    exim, fed, boe = F["ar62_parts2"]
    said("其中向基金组织提款 3 亿美元，美国进出口银行给了 4 亿美元的信贷额度", imf300 * 1e6, exim * 1e6)
    said("与美联储的互惠货币安排是 2.5 亿美元，与英格兰银行的是 1 亿美元", fed * 1e6, boe * 1e6)
    assert imf300 + exim + fed + boe == m1050 == F["ar62_credits"][0]
    has("pw_restored", "during the second half of 1962", "gradually ease the emergency measures")
    dec2539, dec300 = F["ar62_dec"]
    said("12 月底，官方的黄金与美元储备是 25.39 亿美元，其中 3 亿美元是向基金组织提款所得", mon("ar62_dec", "December"),
         dec2539 * 1e6, dec300 * 1e6)
    assert dec300 == imf300
    said("欠基金组织的，1964 年全部还清", F["pw_repaid"][0])
    has("pw_repaid", "excluding that of the IMF, was repaid by the end of the year")
    # after the case: the monetary policy of 1962
    said("人们怀疑 92.5 美分守不住", 100 * par)
    has("ar62_spread", "the spread between interest rates in Canada and the United States widened substantially")
    said("经济从 1961 年初起已在周期性地扩张", F["ar62_expansion"][0])
    has("ar62_expansion", "since early in 1961")
    has("ar62_contraction", "a temporary but sharp contraction in total chartered bank assets and in the total money supply",
        "came to an end in early September")
    said("到 9 月初才停止", mon("ar62_contraction", "September"))
    said("到 9 月，储备与信心恢复得够了，货币政策才开始放松", mon("ar62_sept", "September"))
    has("ar62_sept", "permit some relaxation of monetary policy")
    p5, d12, p4, d13b = F["ar62_cuts"]
    said("银行利率 10 月 12 日降到 5\\%，11 月 13 日降到 4\\%", mon("ar62_cuts", "October"), d12, p5,
         mon("ar62_cuts", "November"), d13b, p4)
    assert F["ar62_bankrate"][0] > p5 > p4
    # who paid
    say("谁付了代价，从措施本身就看得出来（本书的解读）")
    said("6\\% 的银行利率与收缩的货币落在借款人身上", F["ar62_bankrate"][0])
    said("这时为了守住政府自己定下的汇率，银行利率定在了 6\\%", F["ar62_bankrate"][0])
    assert told("一年以前，政府为了放松货币同科因相争", "", "年以前") == y62c - y61b
    # the interest equalization tax
    said("1963 年 7 月 18 日，美国宣布对外国人在美国资本市场的借款征收利息平衡税", F["pw_iet_summer"][0],
         mon("pw_iet_tax", "July"), F["pw_iet_tax"][0])
    has("pw_iet_tax", '"Interest Equalization Tax" on foreign borrowings in U.S. capital markets')
    said("人们普遍担心，加拿大的利率若不相应地提高（大约每年 1 个百分点）", F["pw_iet_fear"][0])
    said("7 月 31 日，美国同意加拿大免税", mon("pw_iet_exempt", "July"), F["pw_iet_exempt"][0])
    has("pw_iet_exempt", "would not increase its foreign international reserves through the proceeds of bor")


def trilemma(F, Y, Q):
    has("nb_trinity", "self-evident for academic economists")
    y1931 = there("ch29_depressionworld", "1931 年，英国放弃了固定汇率，德国放弃了资本的自由流动，法国两样都守住，付出的是通缩。")
    said("1931 年，英国放弃了固定汇率，德国放弃了资本的自由流动，法国两样都守住，付出的是通缩", *y1931)
    said("加拿大 1950 年选了浮动，1962 年回到钉住", dates()["float"].year, dates()["par62"].year)
    has("pw_fn78", "it could not pursue an independent monetary policy")
    # West Germany (Chapter 36's rows)
    F36, Q36, Y36 = other("brettonwoods_facts")
    five, _, _, y61 = F36["b61_reval"]
    said("它 1961 年 3 月把马克升值 5\\%", y61, their_mon("brettonwoods_facts", "b61_reval", "March"), five)
    their("brettonwoods_facts", "b70_de_inflow", "In the final days of April and the first days of May",
          "just over $4 milliard")
    d29, d26 = F36["bt_de_c"]
    said("1969 年 4 月底 5 月初，流入西德的资金略多于 40 亿美元；9 月 29 日到 10 月 26 日，联邦银行停止在干预上限买进美元",
         Y36["b70_de_inflow"], their_mon("brettonwoods_facts", "b70_de_inflow", "April"),
         their_mon("brettonwoods_facts", "b70_de_inflow", "May"), F36["b70_de_inflow"][0] * 1e9,
         their_mon("brettonwoods_facts", "bt_de_c", "September"), d29, their_mon("brettonwoods_facts", "bt_de_c", "October"),
         d26)
    their("brettonwoods_facts", "b70_de_float", "to suspend its purchases of dollars at the upper intervention limit")
    their("brettonwoods_facts", "b70_fr_flight", "despite the exchange controls", "capital flight")
    assert Y36["bt_de_c"] == Y36["b70_de_inflow"] == F36["b70_fr_flight"][1]
    said("\\cmprow{例子}{加拿大 1950—1962 年}{布雷顿森林时期的多数国家；西德 1960 年又限制资本流入}", dates()["float"].year,
         dates()["par62"].year, F36["bo_controls_de"][1])
    their("brettonwoods_facts", "bo_controls_de", "only to impose restrictions on capital inflows again in 1960")
    said("\\cmprow{代价}{汇率波动；紧的货币让本币升值（\\exref{ex:mundell-canada}）}{管制有漏洞，1969 年法国的资本照样外逃}",
         F36["b70_fr_flight"][1])
    has("os_onenonpeg", "19 pegs and only one nonpeg (Brazil)")
    # the test of Obstfeld, Shambaugh and Taylor
    y04 = F["os_wp"][1]
    said("Obstfeld、Shambaugh 与 Taylor（2004）的检验，用 130 多年的数据", y04, F["os_abstract"][0])
    has("os_abstract", "over more than 130 years")
    said("系数为 1 就是完全跟着走", 1)
    d = F["os_t1_defacto"]
    post = F["os_t1_post"]
    has("os_t1_defacto", "Gold Standard de facto classification pool peg nonpeg")
    said("金本位时期，钉住国的系数约 0.5，不钉住国接近 0", d[5], d[6])
    said("布雷顿森林以后，钉住国仍约 0.5，不钉住国约 0.3", post[5], post[6], slack=0.01)
    has("os_bw", "a clear by-product of widespread capital controls")
    said("两个时期的系数都远不到 1", 1)
    has("os_neither", "In neither era do we see slope coefficients or R")
    has("os_not1", "no exchange rate bands, costless arbitrage, and perfect regime credibility")
    said("钉住完全可信，系数才会是 1", 1)
    assert "close to 1" in column("note")["os_neither"]
    has("os_goldpoints", "within the gold points")
    say("黄金输送点是运送黄金有利可图的汇率界限（\\chref{ch:bullion}）")
    # tab:mundell-ost
    g0, g1 = F["os_gold"]
    bw0, bw1 = F["os_bwyears"]
    p0, p1 = F["os_postbw"]
    bw = F["os_t1_bw"]
    said("\\caption{利率跟不跟基准国走，1870—2000 年}", g0, p1)
    said("金本位，1870—1913 年 & 0.52 & 0.05", g0, g1, d[5], d[6])
    said("布雷顿森林，1959—1970 年 & $-0.26$ & —", bw0, 1900 + bw1, -bw[3])
    said("布雷顿森林以后，1973—2000 年 & 0.46 & 0.27", p0, p1, post[5], post[6])
    has("os_t1_bw", "Bretton Woods pool peg nonpeg pool # observations 227 208 na na")
    assert re.search(r"\bTable 1\b", Q["os_t1"])
    said("Obstfeld、Shambaugh 与 Taylor（2004）表 1，年度数据的差分回归，金本位按事实上的汇率制度分类。表中是本国利率的变化对基准国"
         "利率变化的系数，1 表示完全跟着走", y04, 1, 1)
    has("os_t1", "Differences regressions on annual data")
    # the corners: Russia and Sri Lanka
    has("os_corner", "vacillating between these two")
    F1, Q1, Y1 = other("intro_facts")
    said("1997 年，俄罗斯用一条窄幅的汇率带，把汇率管在每美元 5 到 6 卢布之间", Y1["co_band"], *F1["co_band"])
    said("短期国债市场约 30\\% 在非居民手里", F1["co_gko30"][0])
    r30, r150, y98 = F1["co_twice"]
    their("intro_facts", "co_twice", "twice increasing the lending rate", "Both rate hikes occurred in May 1998")
    said("1998 年 5 月中央银行两次加息，把贷款利率从 30\\% 提到 150\\%", y98, their_mon("intro_facts", "co_twice", "May"),
         r30, r150)
    assert told("中央银行两次加息", "中央银行", "次加息") == 2
    their("intro_facts", "co_depleted", "Defending the ruble depleted Russia's foreign reserves")
    said("8 月 17 日卢布贬值，9 月 2 日开始浮动", their_mon("intro_facts", "co_aug17", "August"), F1["co_aug17"][0],
         their_mon("intro_facts", "co_sep2", "September"), F1["co_sep2"][0])
    their("intro_facts", "co_sep2", "The ruble is floated")
    said("2022 年初，中央银行靠干预与道义劝告，把汇率管在每美元 200 到 203 卢比之间", F["cs_range"][2], F["cs_range"][0],
         F["cs_range"][1])
    has("cs_range", "moral suasion")
    their("external_facts", "lk_adjust", "in early March 2022")
    said("3 月初只好让汇率调整", their_mon("external_facts", "lk_adjust", "March"))
    their("external_facts", "lk_float", "the subsequent floating of the exchange rate")
    L = lkr()
    said("2 月末一美元折合 201 卢比，4 月末是 345 卢比", 2, L["2022-02"], 4, L["2022-04"])
    v201, v345 = there("ch05_external", "一美元在 2022 年 2 月末折合 201.00 卢比，4 月末折合 345.27 卢比")[2::2]
    assert (v201, v345) == (L["2022-02"], L["2022-04"])


def oca(F, Y, Q):
    said("蒙代尔 1961 年问了一个更激进的问题", F["nb_oca_q"][0])
    said("1960 年代初固定汇率占主导", F["nb_oca_must"][0])
    has("nb_oca_must", "fixed exchange rates predominated in the early 1960s", "a national currency was considered a must")
    has("nb_oca_q", "to relinquish their monetary sovereignty in favor of a common currency")
    has("nb_oca_adv", "lower transaction costs in trade and less uncertainty about relative prices",
        "The disadvantages are described in greater detail")
    has("nb_oca_def", "the propensity to migrate is high enough to ensure full employment")
    has("mg_factor", "High factor market integration")
    has("nb_oca_others", "a common tax and transfer system")
    m61, m63, k69 = F["mg_start"][:3]
    said("麦金农（Ronald McKinnon，1935—2014）1963 年看开放的程度", F["gnd_mckinnon_born"][0], F["gnd_mckinnon_died"][0], m63)
    has("mg_open", "the more changes in international prices of tradables are likely to be transmitted",
        "money and/or exchange rate illusion by wage earners")
    has("mg_open2", "the nominal exchange rate would be less useful as an adjustment instrument")
    said("凯南（Peter Kenen，1932—2012）1969 年看生产的多样化", F["loc_kenen"][0], F["loc_kenen"][1], k69)
    has("mg_divers", "dilutes the possible impact of shocks specific to any particular sector")
    has("mg_fiscal", "a supra-national fiscal transfer system")
    has("mg_ref_kenen", "The Optimum Currency Area: An Eclectic View")
    y01, y73 = F["mg_1973"]
    said("蒙代尔（1961） & 劳动力的流动", m61)
    said("麦金农（1963） & 开放的程度", m63)
    said("凯南（1969） & 生产的多样化，财政转移", k69)
    said("蒙代尔（1973） & 金融一体化", y73)
    said("Mongelli（2002）的概括；诺贝尔奖新闻稿（1999）", F["mg_ecb"][0], F["nb_date"][1])
    # ex:mundell-oca (teaching numbers)
    N, sh = OCA["N"], OCA["shift"]
    said("甲、乙两个地区各有 100 个工人，起初都充分就业。需求从甲的产品转向乙的产品，甲少要 10 个工人，乙多要 10 个", N, sh, sh)
    said("（3）若 10 个工人从甲迁到乙呢", sh)
    said("甲有 10 人失业", sh)
    said("两地各少要 5 个、多要 5 个工人", sh / 2, sh / 2)
    assert told("若两地各生产两种产品，各占一半", "各占", "") == 0.5             # half of each region's 10
    # the later arguments
    has("mg_inconsistency", "according to some of their characteristics but not according to others")
    said("蒙代尔 1973 年又提出一个论证，后来被麦金农（2001）“重新发现”", y73, y01)
    has("mg_1973", "cross-country asset holding, for international risk sharing")
    has("mg_1973b", "similarity of shocks is not a strict prerequisite")
    said("他 1961 年讲的是汇率能替地区调整，1973 年讲的是共用货币也能分担风险", m61, y73)
    has("mg_ref_1973", "Uncommon Arguments for Common Currencies")


def debate(F, Y, Q):
    y50, y70 = F["pw_model"]
    said("加拿大 1950 年代大部分时间里成功的浮动汇率试验，激发了大量研究浮动汇率制度优点的早期学术工作", y50)
    said("1970 年代初布雷顿森林体系崩溃以后", y70)
    has("pw_model", "provide a model for the rest of the world", "during the early 1970s")
    has("pw_academics", "generally unpopular in business circles")
    said("弗莱明 1962 年也说", Y["fl_equilibrating"])
    said("1950 年代的加拿大“一般就是这样”", F["fl_equilibrating"][0])
    has("fl_equilibrating", "to mitigate the exchange rate variations resulting from variations in internal financial policy")
    said("弗里德曼（Milton Friedman，1912—2006）1948 年在芝加哥大学与加拿大银行的副行长辩论", F["loc_friedman"][0],
         F["loc_friedman"][1], F["pw_friedman"][0])
    has("pw_friedman", "University of Chicago debate with Donald Gordon, Deputy Governor of the Bank of Canada")
    has("pw_friedman3", "there is no evidence directly linking", "undoubtedly had an impact on the internal thinking")
    y46, y49 = F["pw_mistake"]
    said("似乎是怕重犯 1946 年的错误。那一年加元升值，第二年就受到很大的贬值压力，1949 年又贬了值", y46, y49)
    has("pw_mistake", "revalued upwards only to come under significant downward pressure the next year")
    d12, y62, y50b, y57 = F["pw_fn80"]
    said("另一方看 1950 年代后半期", y50b)
    said("《经济学人》1962 年 5 月 12 日的一篇文章", y62, mon("pw_fn80", "May"), d12)
    has("pw_fn80", "The Economist", "Inquest on a Floating Exchange Rate")
    said("说浮动汇率在 1950—1957 年也许对加拿大有益", y50b, 1900 + y57)
    has("pw_fn80b", "With interest rates remaining very high")
    said("推动了蒙代尔 1962 年关于内外平衡下货币与财政政策搭配的论文", F["pw_fn82"][0])
    has("pw_fn82", "The Appropriate Use of Monetary and Fiscal Pol")
    assert F["mu_fn5_1962"][2] == F["pw_fn82"][0]
    has("nb_assign", "monetary policy is linked to external balance and fiscal policy to internal balance")
    has("ar61_boom", "intolerably high interest rates and disorganization in capital markets")
    has("pw_edition", "this expanded History of the Canadian Dollar")
    # the second debate
    has("ry_cycle", "co moves with the VIX, a measure of uncertainty and risk aversion")
    has("ry_centre", "monetary policy in the centre country")
    has("ry_directly", "if and only if the capital account is managed")
    has("ry_certainly", "countries with fixed exchange rates cannot have independent monetary policies")
    has("ry_options", "( a) targeted capital controls")
    said("不钉住的国家无论 1914 年以前还是现在", F["os_nonpegs"][0])
    said("对基准国利率的反应比 1914 年以前的更强", F["os_stronger"][0])
    has("os_stronger", "to respond more strongly to changes in the base")


def deeper(F, Y, Q):
    notes = meta()["notes"]
    assert "December 2005 (the expanded edition" in version("powell2005")
    said("Powell 的《加元史》（加拿大银行，2005 年 12 月的增订版）", Y["pw_edition"], 12)
    has("pw_images", "Image protected by copyright")
    r61, r62 = (int(re.search(r"for the Year (\d{4})", version(k)).group(1)) for k in ("boc1961", "boc1962"))
    said("拉斯明斯基的声明与 1962 年的货币政策，据加拿大银行开放档案馆里 1961 年与 1962 年年报的扫描本", r62, r61, r62)
    assert Y["ar61_statement"] == r61 and Y["ar62_cuts"] == r62
    said("据加拿大统计局网站上 1983 年第二版《加拿大历史统计》的表", F["hs_edition"][0])
    has("hs_edition", "The second edition of Historical statistics of Canada")
    said("据 1964 年《总统经济报告》的表 C-48", Y["erp_title"], F["erp_title"][0])
    said("弗莱明（1962）与 Boughton（2003）据基金组织电子图书馆网页上的全文", Y["fl_bearing"], Y["bg_evidence"])
    said("蒙代尔（1963）只读到剑桥大学出版社网页上的首页摘录与脚注", Y["mu_closed"])
    # the disagreements
    said("1949 年的官价，阿博特说 9 月 19 日起实行，Powell 写作 9 月 20 日", F["pw_sep20"][1], 9, F["pw_abbott"][2],
         mon("pw_sep20", "September"), F["pw_sep20"][0])
    assert page("pw_sep20") == page("pw_dev49a") + 1 and "(pw_dev49a)" in notes and "(pw_sep20)" in notes
    rise = 100 * (F["pw_oct2"][4] - F["pw_par49"][1])
    said("1950 年 10 月的升值，Powell 说加元升了 5 美分，到约 95 美分，从 90.91 美分的平价算只有 4 美分多", F["pw_oct2"][2],
         mon("pw_oct2", "October"), F["pw_oct2"][3], 100 * F["pw_oct2"][4], 100 * F["pw_par49"][1], int(rise))
    assert 4 < rise < 5
    C = canada()
    y52, y60 = (int(v) for v in F["pw_premium"][1:3])
    lows = {y: 100 / C.loc[y, "cad_per_usd_high"] for y in range(y52, y60 + 1)}
    said("1952—1960 年的汇率，Powell 说 1 加元一直在 102 到 106 美分之间", y52, y60, 1, 100 * F["pw_premium"][3],
         100 * F["pw_premium"][4])
    assert all(v < 100 * F["pw_premium"][3] for v in lows.values())
    below = sorted(y for y, v in lows.items() if v < 100)
    said("每年的最低价都不到 102 美分，1952 年与 1955 年还不到 100 美分", 100 * F["pw_premium"][3], *below, 100)
    assert len(below) == 2 and "below US$1.00 in 1952 and 1955" in notes
    b44, b49, b50, b54 = F["gnd_coyne_bank"]
    has("pw_coyne49", "then Deputy Governor of the Bank of Canada")
    said("科因 1949 年 1 月的职位，Powell 写作副行长，德国国家图书馆的规范档说他 1944—1949 年是行长的助理，1950—1954 年才任副行长",
         F["pw_early49"][0], mon("pw_coyne49", "January"), b44, b49, b50, b54)
    has("os_bwzero", "the β coefficient is indistinguishable from zero")
    bw = F["os_t1_bw"]
    has("os_t1_bw", "β b a -.20 -.26")
    p99, p95, p90 = F["os_t1_legend"]
    has("os_t1_legend", "a at 95%, and b at 90%")
    said("表 1 却把 $-0.20$ 与 $-0.26$ 分别标为在 90\\% 与 95\\% 的水平上显著", 1, -bw[2], -bw[3], p90, p95)
    # the indirect testimony
    said("科因 1949 年的备忘录与 1960 年的年报、弗里德曼 1948 年的辩论、《经济学人》1962 年的文章", F["pw_early49"][0],
         F["pw_ar1960"][0], F["pw_friedman"][0], F["pw_fn80"][1])
    said("Goforth（1950）、Muirhead（1999）与 Helliwell 的说法", F["pw_gravely"][0], F["pw_fn79b"][1])
    said("1962 年 6 月的数字，Powell 引的是 1962 年的年报", Y["ar62_jun24"], mon("ar62_jun24", "June"), F["pw_ar62cite"][0])
    has("pw_ar62cite", "(Bank of Canada Annual Report 1962, 8)")
    has("pw_jun24", "US$1,050 million in financial support")
    said("蒙代尔（1961、1973）、麦金农（1963）与凯南（1969）据 Mongelli（2002）", F["mg_start"][0], F["mg_1973"][1],
         F["mg_start"][1], F["mg_start"][2], F["mg_ecb"][0])
    # single witnesses
    said("加元 1950 年代的溢价、1961—1962 年的汇率与加拿大的失业率只据 Powell", F["pw_late50s"][0], F["pw_weaken"][2],
         F["pw_stab"][2])
    said("储备、国际信贷与 1962 年秋的银行利率只据 1962 年的年报", Y["ar62_cuts"], r62)
    assert "Single witnesses" in notes and "rests on the Annual Report 1962 alone" in notes
    said("俄罗斯的加息只据 Chiodo 与 Owyang（第 1 章）", 1)
    assert "the rate rises of May 1998 rest on Chiodo and Owyang alone" in notes
    said("斯里兰卡的 200 到 203 卢比只据中央银行的年报", F["cs_range"][0], F["cs_range"][1])
    # not obtained (the snapshot's notes)
    mun61, mck63 = noted(r"Not obtained: Mundell \((\d{4})\) and McKinnon \((\d{4})\)")
    assert "JSTOR answered with a bot check, not passed" in notes
    said("蒙代尔（1961）与麦金农（1963）在 JSTOR 上", mun61, mck63)
    k69, f53, mk04, m62, r13 = noted(r"Kenen \((\d{4})\); Friedman \((\d{4})\); McKinnon \((\d{4})\); Mundell \((\d{4})\), "
                                     r"IMF Staff Papers; Rey's Jackson Hole paper of (\d{4})")
    said("凯南（1969）、弗里德曼（1953）、麦金农（2004）、蒙代尔 1962 年在《工作人员论文》上的论文与 Rey 2013 年在杰克逊霍尔会议上的原稿",
         k69, f53, mk04, m62, r13)
    assert F["mg_start"][3] == f53
    has("ry_jh", "This paper was presented in the Jackson Hole Symposium.")
    i50, i62 = noted(r"the IMF's Annual Reports of (\d{4}) and (\d{4}) \(imf\.org refused access\)")
    said("基金组织 1950 年与 1962 年的年报，imf.org 拒绝访问", i50, i62)
    assert "the House of Commons Debates (no terms of use found for the site, not quoted)" in notes
    said("Mongelli 的参考文献把麦金农（1963）印作《美国经济评论》第 52 卷", F["mg_ref_mckinnon"][0], F["mg_ref_mckinnon"][1])
    assert "(mg_ref_mckinnon) is not checked" in notes
    # the life dates
    said("拉斯明斯基，美国国会图书馆的规范档只有 1908 年的生年", F["loc_rasminsky"][0])
    assert Q["loc_rasminsky"].endswith("1908-") and "'生卒年未详'" in notes
    say("德国国家图书馆与法国国家图书馆都没有找到记录，所以写作生卒年未详")


def legacy(F, Y, Q):
    said("加拿大 1950 年代的浮动，后来成了布雷顿森林体系崩溃以后各国的样板", F["pw_model"][0])
    has("nb_limits", "highly simplified assumptions about expectations", "gradual price adjustment and rational expectations")
    has("nb_overshoot", "temporarily")
    has("nb_independence", "independent responsibility for price stability")
    said("拉斯明斯基 1961 年的两条原则", F["ar61_statement"][1])


def takeaways(F, Y, Q):
    said("这个模型由弗莱明（1962）与蒙代尔（1963）各自独立、大约同时提出，1976 年才被叫作蒙代尔–弗莱明模型",
         F["bg_ref_fleming"][0], Y["mu_assume"], F["bg_dornbusch"][0])
    D, C = dates(), canada()
    below_par = [y for y in range(1950, 1962) if C.loc[y, "cad_per_usd_avg"] < 1]
    assert below_par == list(range(1952, 1961))                                  # 9 of the 11 full years: 多在
    said("加拿大 1950 年 9 月 30 日放开汇率，1950 年代加元多在美元之上。1961 年政府与科因为紧的货币闹翻，1962 年 5 月 2 日加元钉在 "
         "92.5 美分。6 月的紧急方案用 6\\% 的银行利率", D["float"].year, D["float"].month, D["float"].day, F["pw_model"][0],
         F["pw_pension"][1], D["par62"].year, D["par62"].month, D["par62"].day, pars()["1962"],
         mon("ar62_jun24", "June"), F["ar62_bankrate"][0])
    say("代价由进口商、消费者、旅客、借款人、靠政府开支的人与失业的人分担")


def selfcheck(F, Y, Q):
    m = model()
    said("若$m=0.2$，$x=18$，其余不变，起初的净出口仍是 0 吗？两种汇率下政府支出增加 4 的结果各是什么", SC1["m"], SC1["x"],
         m["sc1_base"]["NX"], POLICY["dG"])
    said("若$\\kappa=4$，固定汇率下增加政府支出", SC3["kappa"])
    C = canada()
    said("1960 年加元的年均汇率是每美元 0.9697 加元，1962 年 5 月的平价是 92.5 美分", 1960, C.loc[1960, "cad_per_usd_avg"],
         dates()["par62"].year, dates()["par62"].month, pars()["1962"])
    said("俄罗斯 1998 年与斯里兰卡 2022 年各想守住三角的哪两个角", other("intro_facts")[0]["co_twice"][2],
         F["cs_range"][2])
    # the answers
    b, pg, fl = m["sc1_base"], m["sc1_peg"], m["sc1_float"]
    s1 = b["s"]
    said("是，$18-0.2\\times90=0$，乘数变成$1/0.6$。钉住时$0.6Y=58$，$Y\\approx96.67$，增加约 6.67，乘数约 1.67。浮动时收入仍是 90，"
         "$18e=0.6\\times90-44+4=14$，$e\\approx0.78$，净出口$14-18=-4$", SC1["x"], SC1["m"], b["Y"], b["NX"], 1, s1, s1,
         s1 * pg["Y"], pg["Y"], pg["Y"] - b["Y"], pg["mult"], fl["Y"], SC1["x"], s1, fl["Y"], fl["A"],
         OPEN["b"] * OPEN["i_f"], SC1["x"] * fl["e"], fl["e"], SC1["x"] * fl["e"], SC1["m"] * fl["Y"], -fl["NX"])
    assert pg["mult"] > m["fiscal_peg"]["mult"]                                 # a smaller m: a larger multiplier
    said("浮动时净出口仍要减少 4，$x$小了，汇率就要升得更多", -fl["NX"])
    assert (1 - fl["e"]) > (1 - m["fiscal_float"]["e"])
    say("储备会一直减少，直到用完。这就是\\exref{ex:intro-peg}的第（2）问，储备耗尽以后只能放弃钉住")
    st, fk, lg = m["sc3_ster"], m["sc3_float"], m["sc3_long"]
    said("$mh/k=8$，$\\kappa=4$小于它，BP 比 LM 陡", st["threshold"], SC3["kappa"])
    assert SC3["kappa"] < st["threshold"] and st["bal"] < 0 and fk["e"] > OPEN["e0"]
    assert st["Y"] > OPEN["G"] and fk["Y"] > max(st["Y"], lg["Y"]) and st["i"] > OPEN["i_f"]
    say("进口增加得比资本流入多，国际收支是逆差；浮动汇率下本币贬值，刺激比固定汇率下更大")
    par = F["ar62_par"]
    e62 = 100 / par[2]
    e60 = C.loc[1960, "cad_per_usd_avg"]
    c60 = 100 / e60
    said("按年报，92.5 美分约合每美元 1.081 加元，$e$从 0.9697 升到约 1.081，上升约 11.5\\%；1 加元从约 103.1 美分降到 92.5 美分，"
         "下降约 10.3\\%", par[2], e62, e60, e62, 100 * (e62 / e60 - 1), 1, c60, par[2], 100 * (1 - par[2] / c60))
    chk("    the report's 108.1 cents", 100 * e62, par[3], tol=0.05)


def ending(F, Y, Q):
    said("回到 1950 年", dates()["float"].year)
    chk("    eleven years later (十一年以后)", told("十一年以后，科因为紧的货币与政府闹翻", "", "年以后"),
        F["pw_pension"][1] - dates()["float"].year)
    said("1956—1961 年失业率翻了一番还多", F["pw_unemp"][1], F["pw_unemp"][3])
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 38's question"
    assert t.index("\\end{answers}") < t.index("回到 1950 年")
    assert f"\\guidequestion{{{NEXT}}}" in (ROOT / "zh" / "ch38_phillips.tex").read_text(encoding="utf-8")


def models() -> None:
    """The key equations, and the claims the text makes of them, checked with random numbers."""
    rng = np.random.default_rng(37)
    n = 0
    for _ in range(60):
        ch = dict(a=rng.uniform(5, 60), c=rng.uniform(0.3, 0.9), I0=rng.uniform(5, 30), b=rng.uniform(0.5, 5),
                  G=rng.uniform(0, 20), T=rng.uniform(0, 20), k=rng.uniform(0.1, 0.6), h=rng.uniform(1, 10),
                  M=rng.uniform(5, 40), P=rng.uniform(0.5, 2), m=rng.uniform(0.05, 0.5), x=rng.uniform(5, 60),
                  i_f=rng.uniform(0.5, 6), e0=rng.uniform(0.5, 2))
        for regime in ("peg", "float"):                                        # eq:mundell-solution
            sol, cf = open_economy(regime, **ch), closed_forms(regime, **ch)
            assert all(np.isclose(sol[v], cf[v], rtol=1e-9, atol=1e-9) for v in ("Y", "e", "M")), regime
            assert np.isclose(sol["i"], ch["i_f"])                              # eq:mundell-mobility
        dG, dM = rng.uniform(0.5, 10), rng.uniform(0.5, 10)
        up = {**ch, "G": ch["G"] + dG}
        f0, f1 = open_economy("float", **ch), open_economy("float", **up)
        # the float: spending moves only the exchange rate; net exports fall by the spending, e by dG/x
        assert np.isclose(f1["Y"], f0["Y"]) and np.isclose(f1["NX"] - f0["NX"], -dG)
        assert np.isclose(f1["e"] - f0["e"], -dG / ch["x"])
        # the peg: the multiplier 1/(1-c+m); the money follows the demand for it
        p0, p1 = open_economy("peg", **ch), open_economy("peg", **up)
        assert np.isclose(p1["Y"] - p0["Y"], dG / (1 - ch["c"] + ch["m"]))
        assert np.isclose(p1["M"] - p0["M"], ch["P"] * ch["k"] * (p1["Y"] - p0["Y"]))
        # money: dY = dM/(kP) and a depreciation under the float; under the peg the stock stays what demand sets
        g1 = open_economy("float", **{**ch, "M": ch["M"] + dM})
        assert np.isclose(g1["Y"] - f0["Y"], dM / (ch["k"] * ch["P"])) and g1["e"] > f0["e"]
        assert np.isclose(open_economy("peg", **{**ch, "M": ch["M"] + dM})["M"], p0["M"])
        # imperfect mobility: the rule kappa >< mh/k (BP flatter or steeper than LM)
        kappa, thr = rng.uniform(0.1, 60), ch["m"] * ch["h"] / ch["k"]
        if abs(kappa / thr - 1) > 1e-3:
            flatter = kappa > thr
            assert (ch["m"] / kappa < ch["k"] / ch["h"]) == flatter
            s0, s1 = open_economy("sterilized", kappa, **ch), open_economy("sterilized", kappa, **up)
            fl0, fl1 = open_economy("float", kappa, **ch), open_economy("float", kappa, **up)
            l0, l1 = open_economy("peg", kappa, **ch), open_economy("peg", kappa, **up)
            assert (s1["bal"] > s0["bal"]) == flatter                         # a surplus at the fixed rate
            assert (fl1["e"] < fl0["e"]) == flatter                           # an appreciation under the float
            dYf, dYs, dYl = fl1["Y"] - fl0["Y"], s1["Y"] - s0["Y"], l1["Y"] - l0["Y"]
            assert (dYf < dYs) == flatter and (dYf < dYl) == flatter            # the stimulus discounted, or larger
            assert np.isclose(fl1["bal"], 0, atol=1e-8) and np.isclose(l1["bal"], 0, atol=1e-8)
            n += 1
        # a very large kappa: the float tends to perfect mobility
        assert np.isclose(open_economy("float", 1e10, **up)["Y"], f1["Y"], rtol=1e-6)
    print(f"ok the open-economy model on 60 random parameter sets ({n} with the BP rule)")
    # kappa = 0 (Fleming's insensitive capital): the float restores the trade balance and the stimulus is that of
    # the closed economy of Chapter 33 (Example islm-policy: 90 -> 98)
    z0, z1 = open_economy("float", 0.0), open_economy("float", 0.0, G=OPEN["G"] + POLICY["dG"])
    assert np.isclose(z1["NX"], z0["NX"]) and np.isclose(z1["NX"], 0)
    chk("    kappa = 0: the closed economy's stimulus", z1["Y"] - z0["Y"], islm(G=M2["G"] + POLICY["dG"])["Y"] - islm()["Y"],
        tol=1e-9)
    # the key equations as printed
    t = TEX.read_text(encoding="utf-8")
    eqs = {lab: body.strip() for body, lab in re.findall(r"\\begin\{keyeq\}\n(.*?)\\label\{(eq:[^}]+)\}", t, re.DOTALL)}
    assert sorted(eqs) == ["eq:mundell-is", "eq:mundell-mobility", "eq:mundell-solution"], sorted(eqs)
    assert eqs["eq:mundell-is"] == "(1-c+m)\\,Y=A+x\\,e-b\\,i,\\qquad \\mathit{NX}=x\\,e-mY.", eqs
    assert eqs["eq:mundell-mobility"] == "i=i^{f}.", eqs
    assert eqs["eq:mundell-solution"] == (
        "\\begin{aligned}\n"
        "\\text{钉住}\\quad Y&=\\frac{A+x\\,\\bar e-b\\,i^{f}}{1-c+m},\\qquad M=P\\,(kY-h\\,i^{f});\\\\\n"
        "\\text{浮动}\\quad Y&=\\frac{M/P+h\\,i^{f}}{k},\\qquad e=\\frac{(1-c+m)\\,Y-A+b\\,i^{f}}{x}.\n"
        "\\end{aligned}"), eqs
    # the notation of Chapter 33 (A, the LM curve) and Chapter 5 (q, the uncovered parity)
    ch33 = (ROOT / "zh" / "ch33_islm.tex").read_text(encoding="utf-8")
    assert "\\label{eq:islm-lm}" in ch33 and "\\frac{M}{P}=kY-h\\,i" in ch33
    say("消费$C=a+c(Y-T)$，投资$I=I_0-b\\,i$，记$A=a-cT+I_0+G$")
    ch05 = (ROOT / "zh" / "ch05_external.tex").read_text(encoding="utf-8")
    assert "q=\\frac{e\\,P^{f}}{P},\\label{eq:external-real}" in ch05
    assert "\\frac{\\E_t e_{t+1}}{e_t}=\\frac{1+i}{1+i^{f}} .\\label{eq:external-uip}" in ch05
    say("若人们预期汇率不变，即$\\E_t e_{t+1}=e_t$，本国利率就必须等于外国利率")
    assert "\\Delta M=\\bar p\\,\\Delta S .\\label{eq:merc-peg}" in (ROOT / "zh" / "ch16_mercantilism.tex").read_text(
        encoding="utf-8")


def figures_data() -> None:
    """What the figures assert of their data."""
    F, C, P, D = facts(), canada(), pars(), dates()
    assert ((C["cad_per_usd_low"] <= C["cad_per_usd_avg"]) & (C["cad_per_usd_avg"] <= C["cad_per_usd_high"])).all()
    c = 100 / C["cad_per_usd_avg"]
    assert (c.loc[1952:1960] > 100).all() and (c.loc[1963:1965] < 100).all()
    band = F["pw_may62"][3] / 100                                              # within ±1 per cent of 92.5 cents
    assert all(abs(c.loc[y] / P["1962"] - 1) < band for y in (1963, 1964, 1965))
    assert C.loc[1949, "cad_per_usd_high"] == F["pw_1949"][3]                  # the selling rate of 1949, Can$1.105
    assert C.loc[1946:1948, "cad_per_usd_low"].eq(1).all()                     # the par of July 1946
    S = bill_spread()
    assert list(S.index) == list(range(1946, 1964)) and S.loc[1959] == S.loc[1950:1963].max()
    assert D["dev49"] < D["float"] < D["par62"] and P["1949"] < P["1962"]
    m = model()
    assert m["fiscal_peg"]["Y"] > m["base_peg"]["Y"] and np.isclose(m["fiscal_float"]["Y"], m["base_peg"]["Y"])
    assert m["money_float"]["Y"] > m["fiscal_peg"]["Y"] and np.isclose(m["money_peg"]["M"], OPEN["M"])


# ---------------------------------------------------------------------------------------------------
# 5. The book
# the life dates: words -> (row of the birth year, index), (row of the death year, index), row of the heading, heading
LIVES = {"Douglas Abbott，1899—1987": (("gnd_abbott_born", 0), ("gnd_abbott_died", 0), "gnd_abbott",
                                       "Abbott, Douglas Charles"),
         "James Coyne，1910—2012": (("gnd_coyne_born", 0), ("gnd_coyne_died", 0), "gnd_coyne", "Coyne, James E."),
         "Robert Mundell，1932—2021": (("gnd_mundell_born", 0), ("gnd_mundell_died", 0), "gnd_mundell",
                                       "Mundell, Robert A."),
         "J. Marcus Fleming，1911—1976": (("loc_fleming_jm", 0), ("loc_fleming_jm", 1), "loc_fleming_jm",
                                          "Fleming, J. Marcus (John Marcus)"),
         "Donald Fleming，1905—1986": (("loc_fleming_dm", 0), ("loc_fleming_dm", 1), "loc_fleming_dm",
                                       "Fleming, Donald M. (Donald Methuen)"),
         "John Diefenbaker，1895—1979": (("loc_diefenbaker", 0), ("loc_diefenbaker", 1), "loc_diefenbaker",
                                         "Diefenbaker, John G."),
         "Milton Friedman，1912—2006": (("loc_friedman", 0), ("loc_friedman", 1), "loc_friedman", "Friedman, Milton"),
         "Ronald McKinnon，1935—2014": (("gnd_mckinnon_born", 0), ("gnd_mckinnon_died", 0), "gnd_mckinnon",
                                        "McKinnon, Ronald I."),
         "Peter Kenen，1932—2012": (("loc_kenen", 0), ("loc_kenen", 1), "loc_kenen", "Kenen, Peter B.")}
# where both authorities have a record, they agree: (row, index) pairs
AGREE = [(("gnd_mundell_born", 0), ("loc_mundell_born", 0)), (("gnd_mundell_died", 0), ("loc_mundell_died", 0)),
         (("gnd_kenen_born", 0), ("loc_kenen", 0)), (("gnd_kenen_died", 0), ("loc_kenen", 1)),
         (("gnd_fleming_jm_born", 0), ("loc_fleming_jm", 0)), (("gnd_fleming_jm_died", 0), ("loc_fleming_jm", 1)),
         (("gnd_coyne_born", 0), ("loc_coyne", 0)), (("nb_born", 0), ("gnd_mundell_born", 0))]
# what other chapters tell: (words of this chapter, chapter where it is told, words there)
EVENTS = [("在平价上下 1\\% 以内维持汇率（\\chref{ch:brettonwoods}）", "ch36_brettonwoods", "在平价上下 1\\% 以内干预汇率"),
          ("西欧 1958 年底恢复了经常账户的可兑换（\\chref{ch:brettonwoods}）", "ch36_brettonwoods",
           "1958 年底主要货币恢复经常账户的可兑换"),
          ("资本账户仍可管制，这是协定留给成员国的权利（\\secref{sec:warfinance-bw}）", "ch34_warfinance",
           "资本管制写进了第六条第三节"),
          ("十九年以后的西德钉住了汇率，就挡不住流进来的钱（\\chref{ch:brettonwoods}）", "ch36_brettonwoods",
           "西德钉住汇率，又挡不住流进来的钱"),
          ("约翰·劳（John Law，1671—1729）", "ch16_mercantilism", "约翰·劳（John Law，1671—1729）"),
          ("按每股 9,000 里弗尔买卖自己的股份", "ch16_mercantilism", "按每股 9,000 里弗尔的固定价格买卖股份"),
          ("持股人想要多少纸币，银行就得印多少，式~\\eqref{eq:merc-peg}", "ch16_mercantilism", "他们想要多少现钱，银行就得印多少"),
          ("钉住的道理，\\chref{ch:mercantilism}已经见过", "ch16_mercantilism",
           "钉住汇率的央行必须按固定价格买卖外汇，于是放弃了对货币数量的控制（\\chref{ch:mundell}）"),
          ("\\exref{ex:intro-peg}里多发的 60 亿本币换走了 10 亿美元的储备", "ch01_intro", "公众不愿持有的 60 亿本币"),
          ("这就是\\exref{ex:intro-peg}的第（2）问，储备耗尽以后只能放弃钉住", "ch01_intro", "储备耗尽之前"),
          ("与\\exref{ex:islm-policy}的 98 相比", "ch33_islm", "与 LM 联立得$Y=98$"),
          ("比\\exref{ex:islm-policy}的 4 大得多", "ch33_islm", "{$M$增加 4，收入增加 4}"),
          ("接\\exref{ex:islm-equilibrium}，$a=26$，$c=0.6$", "ch33_islm", "\\label{ex:islm-equilibrium}"),
          ("（\\chref{ch:depressionworld}）。布雷顿森林协定把资本管制留给成员国", "ch29_depressionworld",
           "1931 年，英国放弃了固定汇率，德国放弃了资本的自由流动，法国两样都守住，付出的是通缩。"),
          ("\\chref{ch:external}把它叫作不可能三角", "ch05_external", "这叫\\textbf{不可能三角}"),
          ("黄金输送点是运送黄金有利可图的汇率界限（\\chref{ch:bullion}）", "ch19_bullion", "这一点叫\\textbf{黄金输送点}"),
          ("1997 年，俄罗斯用一条窄幅的汇率带", "ch01_intro", "1997 年，俄罗斯的汇率由一条窄幅的汇率带管着"),
          ("9 月 2 日开始浮动", "ch01_intro", "9 月 2 日，卢布开始浮动"),
          ("4 月末是 345 卢比（\\chref{ch:external}）", "ch05_external", "4 月末折合 345.27 卢比"),
          ("借款征收利息平衡税（\\chref{ch:brettonwoods}）", "ch36_brettonwoods", "征收利息平衡税"),
          ("它 1961 年 3 月把马克升值 5\\%", "ch36_brettonwoods", "西德 1961 年 3 月把马克升值 5\\%"),
          ("马克浮动（\\chref{ch:brettonwoods}）", "ch36_brettonwoods", "马克的汇率浮动")]
# the chapters this one hands on to
LATER = {"ch:floating": "ch46_floating", "ch:euro": "ch60_euro", "ch:emcrises": "ch61_emcrises",
         "ch:hierarchy": "ch76_hierarchy", "ch:chinacredit": "ch72_chinacredit", "ch:credibility": "ch49_credibility"}
# the chapters that point here
POINTERS = ("ch05_external", "ch16_mercantilism", "ch29_depressionworld", "ch33_islm", "ch34_warfinance",
            "ch36_brettonwoods")


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
    assert "dateOfBirth" in column("juan")["gnd_abbott_born"] and "dateOfDeath" in column("juan")["gnd_coyne_died"]
    assert "Finanzminister" in Q["gnd_abbott_job"]                               # Abbott, the minister of finance
    has("loc_diefenbaker_pm", "prime minister 1957-63")
    # Rasminsky: no year of death anywhere
    assert "拉斯明斯基（Louis Rasminsky，生卒年未详）" in t and len(F["loc_rasminsky"]) == 1
    for here, ch, there_ in EVENTS:
        assert here in t, here
        assert there_ in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (ch, there_)
    for label, ch in LATER.items():
        assert f"{{{label}}}" in t, label
        assert f"\\label{{{label}}}" in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (label, ch)
    for ch in POINTERS:
        assert "\\chref{ch:mundell}" in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), ch
    print(f"ok {len(LIVES)} life dates, {len(EVENTS)} statements of other chapters, {len(LATER)} later chapters")


def witnesses(F, Q):
    """Second witnesses of statements of the text, the licences and the bibliography block of the chapter."""
    C = canada()
    # the par value of 2 May 1962: Powell and the Annual Report (92.5 cents = about 108.1 Canadian cents)
    assert F["pw_may62"][:2] == F["ar62_par"][:2] and 100 * F["pw_may62"][2] == F["ar62_par"][2]
    chk("    100/0.925 (the report's 108.1)", 100 / F["pw_may62"][2], F["ar62_par"][3], tol=0.05)
    # Coyne's resignation (the day after 12 July) and Rasminsky's appointment on 24 July
    assert F["pw_senate"][0] + 1 == F["ar61_coyne"][2] and "The following day" in Q["pw_resigned"]
    assert F["pw_rasminsky"][:2] == F["ar61_coyne"][:2]
    # the US$1,050 million of June 1962 (Powell citing the report: one witness)
    assert F["pw_jun24"][0] == F["ar62_measures"][1] == F["ar62_credits"][0]
    assert "one witness" in column("note")["pw_ar62cite"]
    # the peak of 20 August 1957 against the yearly low of Historical Statistics
    chk("    1/0.9422 against Powell's US$1.0614", 1 / F["hs560_1957"][2], F["pw_premium"][5], tol=2e-4)
    # the rows of Historical Statistics and of the Economic Report against the series
    for rid in ("hs560_1949", "hs560_1952", "hs560_1955", "hs560_1957", "hs560_1959", "hs560_1960"):
        y, hi, lo, avg = F[rid]
        assert [C.loc[int(y), c] for c in ("cad_per_usd_high", "cad_per_usd_low", "cad_per_usd_avg")] == [hi, lo, avg], rid
    assert C.loc[1959, "ca_tbill_3m"] == F["hs471_1959"][1] and C.loc[1959, "us_tbill_3m"] == F["erp_1959"][1]
    # 1949: Powell's buying rate and the yearly high
    assert F["pw_1949"][3] == F["hs560_1949"][1]
    # Diefenbaker, Prime Minister in 1962
    lo_pm, hi_pm = F["loc_diefenbaker_pm"]
    assert lo_pm <= F["pw_may62"][1] <= 1900 + hi_pm and "the Prime Minister" in Q["ar62_jun24"]
    # the licences
    m = meta()
    lic = m["license"]
    for rid in ("bc_permit", "bc_attrib", "bc_notes", "bc_logo", "bc_third", "sl_a", "sl_b", "fl_copyright",
                "mu_copyright", "nb_copyright", "os_copyright", "ry_copyright", "mg_ecb", "mg_notice", "gnd_licence"):
        assert re.search(r"(?:\(|; )rows? [^)]*\b" + rid + r"\b", lic), rid
        assert words_of(rid) in lic, rid
    assert re.search(r"\(rows [^)]*\bcs_range\b", lic) and "a derived extract only" in lic
    for words in ("Short phrases only", "public domain", "public data", "says that they are translated into Chinese",
                  "Adapted from Statistics Canada, Historical Statistics of Canada, 11-516-X, Section J, Series J560-567 "
                  "and J471-480, 1983. This does not constitute an endorsement by Statistics Canada of this product.",
                  "read on 2026-10-29 at https://www.bankofcanada.ca/terms/"):
        assert words in lic, words
    cm = load_snapshot("canada_float_1946_1965")[1]
    assert ("Source: Statistics Canada, Historical Statistics of Canada, 11-516-X, Section J, Series J560-567 and "
            "J471-480, 1983. Reproduced and distributed on an \"as is\" basis with the permission of Statistics Canada."
            ) in cm["license"]
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    start = bib.index("% ---- 第 37 章")
    following = re.search(r"^% ---- 第 \d+ 章", bib[start + 1:], re.MULTILINE)
    end = start + 1 + following.start() if following else bib.index("\\end{thebibliography}")
    block = bib[start:end]
    assert "data/fetch/mundell37.py" in block and bib.index("% ---- 第 36 章") < start
    items = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", block)}
    allitems = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", bib)}
    for key in ("powell2005", "boc1961", "boc1962"):
        assert "来源：加拿大银行（Bank of Canada）" in items[key] and "有改动" in items[key], key
    assert "Bank of Canada Terms and Conditions" in items["powell2005"] and "钞票图像" in items["powell2005"]
    hsc = items["hsc1983"]
    assert words_of("sl_b").split("notice: ")[1].startswith("Adapted from Statistics Canada")
    assert ("Adapted from Statistics Canada, Historical Statistics of Canada, 11-516-X, Section J, Series J560-567 and "
            "J471-480, 1983. This does not constitute an endorsement by Statistics Canada of this product.") in hsc
    assert "Statistics Canada Open Licence" in hsc
    assert "公有领域" in items["erp1964"]
    for key, rid in (("fleming1962", "fl_copyright"), ("boughton2003", "fl_copyright"), ("mundell1963", "mu_copyright"),
                     ("nobel1999", "nb_copyright"), ("ost2004", "os_copyright"), ("rey2015", "ry_copyright"),
                     ("mongelli2002", "mg_ecb")):
        assert words_of(rid) in items[key], (key, rid)
    assert words_of("mg_notice") in items["mongelli2002"]
    assert Q["gnd_licence"] in items["gnd37"] and "公共数据" in items["loc37"]
    for words, ((rb, _), _, head_row, _) in LIVES.items():
        if head_row.startswith("loc_"):
            assert Q[head_row].replace("-", "--") in items["loc37"], head_row
    for rid in ("loc_coyne", "loc_rasminsky"):
        assert Q[rid].replace("-", "--") in items["loc37"], rid
    # every source of the snapshot is named by its URL in its item
    item_of = {"bocterms37": "powell2005", "hsc_j560": "hsc1983", "hsc_j471": "hsc1983", "hsc_sectionj37": "hsc1983",
               "hsc_cat37": "hsc1983", "statcanlicence37": "hsc1983", "cbsl_ar2022": "cbsl2023ar"}
    for key, s in m["sources"].items():
        item = "loc37" if key.startswith("loc_") else "gnd37" if key.startswith("gnd_") else item_of.get(key, key)
        assert s["url"] in allitems[item].replace("\\%", "%").replace("\\_", "_"), key
    keys = set(allitems)
    cited = {k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", tex_text()) for k in c.split(",")}
    assert cited <= keys, sorted(cited - keys)
    assert REUSED_KEYS <= cited and not REUSED_KEYS & set(items)
    assert set(items) == cited - REUSED_KEYS, sorted(set(items) ^ (cited - REUSED_KEYS))
    print(f"ok {len(cited)} works cited, {len(items)} in the bibliography block of Chapter 37, "
          f"{len(REUSED_KEYS)} in earlier blocks")


NAMES = ("Powell|Boughton|Mongelli|Rey|Obstfeld|Shambaugh|Taylor|Rhomberg|Helliwell|Dornbusch|Chiodo|Owyang|Muirhead|"
         "Goforth")


def counts() -> None:
    """The editor's limits: “不能” at most about a dozen; no cited modern author as the subject of a sentence outside
    the 史料说明; the forbidden words; who paid stated; the two debates left open."""
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
    # who paid for the defence of the peg in 1962, and the quarrel that cost Coyne his post
    for words in ("谁付了代价", "进口商", "消费者", "出国的旅客", "靠政府开支的人", "借款人", "失业的人",
                  "参议院认定他没有失职，他还是辞了职", "银行利率定在了 6\\%，货币收紧了"):
        assert words in main, words
    # the two debates of the editor's notes are left open
    for words in ("第一个争论", "第二个争论"):
        assert main.count(words) == 1, words
    first, second = main.split("\\subsubsection{")[1:3]
    second = second[:second.index("\\section{")]
    assert first.rstrip().endswith("至今没有定论。") and second.rstrip().endswith("至今没有定论。")
    # the inferences are marked
    assert main.count("本书的解读") >= 8 and "本书的计算" in main and "本书的概括" in main


def main() -> None:
    df = _rows()
    F, Y, Q = facts(), years(), quotes()
    check_readings(df)
    check_text(df)
    guide(F, Y, Q)
    opening(F, Y, Q)
    world(F, Y, Q)
    origins(F, Y, Q)
    model_section(F, Y, Q)
    canada_section(F, Y, Q)
    trilemma(F, Y, Q)
    oca(F, Y, Q)
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
    reused = {rid for ids in REUSED.values() for rid in ids}
    anchors(str(TEX), set(df["id"]) | reused, script=Path(__file__))


if __name__ == "__main__":
    main()
