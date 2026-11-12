"""Chapter 45 (货币主义): every number and every quotation in zh/ch45_monetarism.tex.

    python3 checks/check_ch45.py

Inputs:
  monetarism_facts              quotations of the chapter's sources with their page: Friedman and Schwartz, 'Money and
                                Business Cycles', with Minsky's comment (NBER's PDF); Friedman (AER, March 1968); Poole
                                and Lieberman (BPEA 1972:2), Modigliani and Papademos (BPEA 1975:1), Goldfeld (BPEA
                                1976:3); the records of policy actions of the FOMC of 6 October 1979, 1-2 February 1982
                                and 5 October 1982; the Budget statements of 1980, 1986 and 1987 (historic Hansard); the
                                Bank of England's Quarterly Bulletin of March 1981 and the Governor's lecture of October
                                1986; Bouey's two statements of 1982 (the Bank of Canada's open archive); Moses (RBA RDP
                                8301); Rich (ECB WP 236); Gerberding, Worms and Seitz (Bundesbank DP 25/2004); tables B-1
                                and B-67 of the Economic Report of the President of 2000; the terms of the AEA, Brookings,
                                the Bank of England, the Bank of Canada and the RBA; the authority records of the Library
                                of Congress and the GND. data/fetch/verify_web_quotes.py checks the quotations against the
                                documents; data/fetch/monetarism45.py fetches them
  monetarism_us_1959_1999       GDP (B-1) and the December averages of M1 and M2 (B-67), billions of dollars
  zh/ch04, ch08, ch13, ch19,    the statements of other chapters that this chapter repeats (EVENTS); the stubs of
  ch28, ch29, ch33, ch44        Chapters 46-50 and 55 for what is handed on (LATER)

This script

1. reads the numbers of every row from its quotation by the rules of READINGS and compares them with the value
   column; the misreadings of the text layers are listed in MISPRINTS;
2. finds every “…” of the text among the renderings of TRANSLATIONS, and the words of the source each one renders
   (KEYWORDS) in the rows; the quotations stay short;
3. checks each number of the text with said(): the phrase is in the text and each number is the value of a row, a
   teaching input, or arithmetic on them (the target of eq:monetarism-target, Poole's variances of
   eq:monetarism-poole, the velocity of the American series, the misses of the Bundesbank's targets); every Arabic
   number of the text must lie in a phrase said() read (coverage()); every chain a = b of plain arithmetic in the
   text's math holds (arithmetic());
4. checks the key equations as printed, the claims made of them on random numbers, the data of the figures
   (figsrc/fig_ch45.py imports us(), gwz(), rich(), poole_var() and the teaching inputs from here), the life dates
   against the authority records, what other chapters tell, the licences and the bibliography block of Chapter 45;
5. lists the rows no "% 据:" anchor of the text names (common.anchors).

Set CH45_TEX to a scratch copy of the chapter to run the checks on it (mutation tests).
"""
from __future__ import annotations

import os
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from common import ROOT, anchors, load_snapshot, quoted

TEX = Path(os.environ.get("CH45_TEX", ROOT / "zh" / "ch45_monetarism.tex"))   # a scratch copy for mutation tests
GUIDE = "控制货币数量就能控制通胀吗？"
PREV = GUIDE                                        # Chapter 44's NEXT
NEXT = "美元与黄金为什么脱钩？浮动汇率为什么会“超调”？"      # Chapter 46's question (its stub)
FETCH = "data/fetch/monetarism45.py"


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
    df, m = load_snapshot("monetarism_facts", dtype=str, keep_default_na=False)
    assert 45 in m["used_in"] and m["fetch"] == FETCH
    assert df["id"].is_unique
    return df


@lru_cache(maxsize=None)
def meta() -> dict:
    return load_snapshot("monetarism_facts")[1]


@lru_cache(maxsize=None)
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
    """Each of the words is in what row rid says."""
    for w in words:
        assert w in words_of(rid), (rid, w)


def page(rid: str) -> int:
    """The first printed page number of a row's juan column: 'p. 18 (PDF p. 19)' -> 18."""
    return int(re.search(r"pp?\. (\d+)", column("juan")[rid]).group(1))


def chapter(name: str) -> str:
    """Another chapter's text without its comment lines."""
    t = (ROOT / "zh" / f"{name}.tex").read_text(encoding="utf-8")
    return "\n".join(l for l in t.splitlines() if not l.lstrip().startswith("%"))


def year_in(key: str, pattern: str) -> int:
    """A year the version of a source names: the issue of the Brookings Papers, of the Quarterly Bulletin, the ERP."""
    return int(re.search(pattern, meta()["sources"][key]["version"]).group(1))


@lru_cache(maxsize=None)
def us() -> pd.DataFrame:
    """B-1 and B-67 of the ERP 2000, 1959-1999: GDP and the December averages of M1 and M2 (billions of dollars), with
    the velocities v1 = GDP/M1 and v2 = GDP/M2. figsrc/fig_ch45.py draws them."""
    df, m = load_snapshot("monetarism_us_1959_1999")
    assert 45 in m["used_in"] and m["fetch"] == FETCH and set(m["documents"]) == {"erpb1_45", "erpb67_45"}
    assert "17 U.S.C. § 105" in m["license"]
    df = df.set_index("year")
    assert list(df.index) == list(range(1959, 2000))
    F = facts()
    n = 0
    for rid, v in F.items():                                  # the quoted lines of the two tables agree with the series
        mt = re.fullmatch(r"erp_b(1|67)_(\d{4})", rid)
        if mt:
            y = int(mt.group(2))
            assert v[0] == y, rid
            if mt.group(1) == "1":
                assert v[1] == df.loc[y, "gdp_bn"], rid
            else:
                assert (v[1], v[2]) == (df.loc[y, "m1_dec_bn"], df.loc[y, "m2_dec_bn"]), rid
            n += 1
    assert n == 14, n
    df["v1"] = df["gdp_bn"] / df["m1_dec_bn"]
    df["v2"] = df["gdp_bn"] / df["m2_dec_bn"]
    return df


def velocity(y: int) -> float:
    return float(us().loc[y, "v1"])


def growth(y: int) -> float:
    """The change of the velocity of M1 over the year, per cent."""
    return 100 * (velocity(y) / velocity(y - 1) - 1)


def gwz(y: int) -> dict[str, float]:
    """Table 10 of Gerberding, Worms and Seitz: the target (lo, hi; a point target has lo == hi) and the actual growth.
    1975: the target 8, December over December; 1976-1978: the annual average target and the annual average growth
    (1977 and 1978 print the course of the year in brackets); 1989: a point target ('about 5'); 1991: the range was
    changed at the midyear review (rev)."""
    v = facts()[f"gwz_t{y}"]
    assert v[0] == y
    if y in (1975, 1976):
        return dict(lo=v[1], hi=v[1], actual=v[-1])
    if y in (1977, 1978):
        return dict(lo=v[3], hi=v[3], actual=v[-1], course=(v[1], v[2]))
    if y == 1989:
        return dict(lo=v[1], hi=v[1], actual=v[-1])
    out = dict(lo=v[1], hi=v[2], actual=v[-1])
    if y == 1991:
        out["rev"] = (v[5], v[6])
    return out


GWZ_YEARS = range(1975, 1999)
RICH_YEARS = [y for y in range(1975, 1991) if y != 1979]


def rich(y: int) -> dict[str, float]:
    """Table 1 of Rich: the target and the outcome of the year, per cent (no target in 1979)."""
    v = facts()[f"rich_t{y}"]
    assert v[0] == y
    return dict(target=v[1], outcome=v[2])


def misses() -> list[int]:
    """The years 1979-1998 whose actual growth lies outside the target (the range announced in December)."""
    return [y for y in range(1979, 1999) if not gwz(y)["lo"] <= gwz(y)["actual"] <= gwz(y)["hi"]]


def votes(rid: str) -> tuple[list[str], list[str]]:
    """The names of the votes for and against of an FOMC record."""
    yes, no = words_of(rid).split("Votes against this action:")

    def names(s: str) -> list[str]:
        s = re.sub(r"\b(?:Messrs|Mrs|Mr)\.", "", s.replace("Votes for this action:", "")).strip().rstrip(".")
        return [p.strip() for p in re.split(r",|\band\b", s) if p.strip() and p.strip() != "None"]

    return names(yes), names(no)


# ---------------------------------------------------------------------------------------------------
# 1. Readings of the numbers (the same rules wrote the value column when the snapshot was built)
SMALL = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "twenty": 20}


def cardinal(s: str) -> float:
    """An English cardinal: 'two', 'Twenty-one'."""
    return float(sum(SMALL.get(w, 0) for w in s.lower().replace("-", " ").split()))


def figure(s: str) -> float:
    """'1,000', '30.5', '.28', '-0.15' and full-width digits."""
    return float(unicodedata.normalize("NFKC", s).replace(",", "").replace("−", "-"))


def gap(s: str) -> float:
    """A figure the text layer splits: '197 1' for 1971."""
    return figure(s.replace(" ", ""))


def io(s: str) -> float:
    """The scan's 'IO' for 10."""
    return float(s.replace("I", "1").replace("O", "0"))


FRACTIONS = {"½": ".5", "¼": ".25", "¾": ".75"}


def prepare(text: str) -> str:
    """A quotation ready for its figures: '5½', '5 ½' and '4¾' (GWZ's Table 10, the page images) as decimals; the
    names of the aggregates (M1, M-1, M₃, PSL2) without their digits; the Federal Reserve's '4-1/2' and '1/2' as
    decimals."""
    s = re.sub(r"(\d) ?([½¼¾])", lambda m: m.group(1) + FRACTIONS[m.group(2)], text)
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\b(?:M|PSL)-?\d\b", "M", s)
    s = re.sub(r"\b(\d+)-([13])/([24])\b", lambda m: f"{int(m.group(1)) + int(m.group(2)) / int(m.group(3)):g}", s)
    s = re.sub(r"(?<![\d/.])\b([13])/([24])\b(?![\d/])", lambda m: f"{int(m.group(1)) / int(m.group(2)):g}", s)
    return s


# a figure with its sign: a minus that follows no letter, digit, bracket, per cent sign or point
FIGURES = re.compile(r"((?<![\w)%.,])[-−])?(\d[\d,]*(?:\.\d+)?|\.\d+)")
HOW = {"num": figure, "card": cardinal, "gap": gap, "io": io}
# id -> [(phrase, how)], in order. A phrase 'context|word' is searched as a whole and read from `word`. Rows not
# listed are read with all the figures of the prepared quotation, with their signs.
READINGS: dict[str, list[tuple[str, str]]] = {
    "lp86_rose": [("interruption in |197 1", "gap"), ("-|73", "num")],
    "qb81_target": [("growth of |6", "num"), ("%-|IO", "io")],
    "mk_cycles": [("|Twenty-one", "card"), ("between |1870", "num"), ("and |1960", "num"), ("which |six", "card")],
    "moses_minsky": [("Minsky, |1957", "num"), ("p.|171", "num")],
    "fs_props": [], "gwz_three": [], "pl_eq1": [], "pl_eq5": [], "pl_loss": [], "qb81_garble": [], "lp86_facile": [],
}


def read_rule(rid: str, text: str) -> list[float]:
    got, pos = [], 0
    for phrase, how in READINGS[rid]:
        context, _, word = phrase.rpartition("|")
        k = text.find(context + word, pos)
        assert k >= 0, f"{rid}: {phrase!r} not found (in order)"
        pos = k + len(context + word)
        got.append(HOW[how](word))
    return got


def read_text(rid: str, text: str) -> list[float]:
    """The numbers of a quotation, by READINGS or by its figures."""
    if rid in READINGS:
        return read_rule(rid, text)
    return [(-1 if sign else 1) * figure(n.rstrip(",")) for sign, n in FIGURES.findall(prepare(text))]


# the misreadings of the text layers and the misprints, each printed in the quotation and named in the snapshot's
# notes with its row: (row, as printed in the quotation, the words of the notes that name it)
ML = ("bou_1975", "bou_reliable", "bou_shifts", "boud_stable", "boud_1975", "boud_pilot", "fomc82f_ml", "gf_clearly",
      "moses_three")
MISPRINTS = [("law86_broad", "MO", "'MO' for 'M0'"),
             ("law86_narrow", "braod", "'braod' as printed"),
             ("lp86_velocity", "has/allen", "'has/allen' for 'has fallen'"),
             ("lp86_facile", "nee1s", "'nee1s' for 'needs'"),
             ("lp86_lecture", "(I)", "'(I)' for the footnote mark 1"),
             ("lp86_peak2", "inMarch", "'inMarch' for 'in March'"),
             ("lp86_rose", "197 1-73", "'197 1-73' for '1971-73'"),
             ("qb81_garble", "17!-", "'17!-' for '17½'"),
             ("qb81_target", "IO", "'IO' for '10'"),
             ("qb81_real", "tenns", "'tenns' for 'terms'"),
             ("qb81_mlr", "from14% to12 %", "'from14% to12 %' for 'from 14% to 12%'"),
             ("qb81_25", "to20%", "'to20%' for 'to 20%'"),
             *[(rid, "Ml", "'Ml' for 'M1'") for rid in ML],
             ("f68_total", "guLideor", "'guLideor' for 'guide or'"),
             ("pl_superior", "tnough", "'tnough' for 'though'"),
             ("pl_eq1", "bo+ biY", "'bo+ biY' for 'b0 + b1Y'"),
             ("pl_qje2", "Jourlial", "'Jourlial' for 'Journal'"),
             ("pl_qje2", "Econtomics", "'Econtomics' for 'Economics'"),
             ("moses_credit", "GOP", "'GOP' for 'GDP'"),
             ("rich_80", "Swissfranc", "'Swissfranc' for 'Swiss franc'")]
N_QUOTED = 192


def check_readings(df: pd.DataFrame) -> None:
    src = meta()["sources"]
    n = 0
    for r in df.itertuples():
        assert r.file in src, (r.id, r.file)
        assert r.quote, f"{r.id}: no quotation"
        vals = [float(x) for x in r.value.split(";")] if r.value else []
        got = read_text(r.id, " ".join(r.quote.split()))
        n += bool(vals)
        assert [round(g, 6) for g in got] == [round(v, 6) for v in vals], f"{r.id}: read {got}, value column {vals}"
    quoted("rows with values, each read from its quotation", n, N_QUOTED)
    Q, notes = quotes(), meta()["notes"]
    for rid, word, named in MISPRINTS:
        assert word in Q[rid], (rid, word)                                      # printed in the quotation
        found = False
        for m in re.finditer(re.escape(named), notes):
            g = re.match(r"[^(]{0,80}\(([^)]*)\)", notes[m.end():])
            found |= bool(g) and rid in re.split(r",\s*", g.group(1))
        assert found, (rid, named)                                                # and named, with its row
    for rid in READINGS:
        assert f"({rid}" in notes or f" {rid}" in notes, rid                     # the notes say how it is read
    assert set(src) == set(df["file"]), sorted(set(src) ^ set(df["file"]))
    # the rows read on page images name the image source, and their PDF is the same file
    for key, s in src.items():
        if s["format"] == "image":
            pdf_ = key.replace("img_", "_")
            assert (src[pdf_]["url"], src[pdf_]["sha256"]) == (s["url"], s["sha256"]), key
    print(f"ok {len(df)} rows; {len(MISPRINTS)} misreadings named in the notes")


# ---------------------------------------------------------------------------------------------------
# 2. The quotations of the text: each “…” is a rendering of words of rows
TRANSLATIONS = {
    "红皮书": ("h80_red",),
    "货币主义": ("h80_monetarism", "h80_abuse"),
    "紧身衣": ("h80_corset", "qb81_175"),
    "美元之舞": ("fs_dance",),
    "有序市场": ("mp_orderly",),
    "相当失败": ("gf_failure",),
    "古德哈特定律": ("moses_credit",),
    "明显": ("rich_80",),
    "不可避免": ("gwz_unavoidable",),
    "根本无关紧要": ("gwz_cgg",),
    "超出 10 个百分点以上": ("rich_explosive",),
    "Ml": ("fomc82f_ml",),
    "17!-\\%": ("qb81_garble",),
}
# the words of the source each rendering renders, in the quotation
KEYWORDS = {
    "h80_red": ["the Red Book"],
    "h80_monetarism": ['"monetarism"'],
    "h80_abuse": ['the word "monetarism"', "political abuse"],
    "h80_corset": ['"corset"'],
    "qb81_175": ["'corset'"],
    "fs_dance": ['"a dance of the dollar,"'],
    "mp_orderly": ['"orderlymarkets"'],
    "gf_failure": ["rathera failure"],
    "moses_credit": ["Goodhart's law"],
    "rich_80": ['"clearly"'],
    "gwz_unavoidable": ['"unavoidable"'],
    "gwz_cgg": ['"the money aggregate just does not matter"'],
    "rich_explosive": ["by over 10 percentage points"],
    "fomc82f_ml": ["Ml-B"],
    "qb81_garble": ["17!-%"],
}
OWN = {"Ml", "17!-\\%"}                       # quoted in the source's own words (misreadings, the 史料说明)


def tex_text() -> str:
    return "\n".join(l for l in TEX.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("%"))


def text_quotations() -> list[str]:
    """The “…” of the text; the closing question is Chapter 46's and the chapter's own question is in the guide and at
    the end of the opening (both checked by guide() and opening())."""
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 46's question"
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
        for rid in TRANSLATIONS[q]:
            assert rid in ids and rid in KEYWORDS, rid
            if q in OWN:
                assert q.replace("\\%", "%") in words_of(rid), (q, rid)          # the source's own words
    stale = set(TRANSLATIONS) - used
    assert not stale, f"listed but not in the text: {sorted(stale)}"
    for rid, words in KEYWORDS.items():
        for w in words:
            assert w in words_of(rid), f"{rid}: {w!r} not in the quotation"
    assert set(KEYWORDS) == {r for rs in TRANSLATIONS.values() for r in rs}
    for q in used:
        assert len(q) <= 12, f"a long quotation: “{q}”"
    print(f"ok {n} quotations of the text found in the snapshot ({len(used)} distinct)")


# ---------------------------------------------------------------------------------------------------
# 3. Numbers: said() and the parts of the text it does not read
UNITS = {"万亿": 10 ** 12, "亿": 10 ** 8, "万": 10 ** 4}
AMOUNT = re.compile(r"(\d[\d,]*(?:\.\d+)?)(?:\s*(万亿|亿|万))?")
# what is not a number of the story: labels, citations, cross-references, the key equations (models() reads them), the
# sub- and superscripts of the math, the numbers of the parts of an example, the names of the aggregates (M0-M3, M1-A,
# M1-B, £M3) and of the ERP's tables (B-1, B-67), and the column specifications of the table
MASKS = [re.compile(r"\\begin\{keyeq\}.*?\\end\{keyeq\}", re.DOTALL),
         re.compile(r"\\(?:label|cite|chref|secref|figref|tabref|exref|eqref|ref|nameref|url|fig)\{[^}]*\}"),
         re.compile(r"_\{[^}]*\}|_\d"),
         re.compile(r"\^\{\d+\}"),
         re.compile(r"（\d）"),
         re.compile(r"£?\bM[0-3](?:-[AB])?\b"),
         re.compile(r"\bB-\d+\b"),
         re.compile(r"\{(?:fig|tab):[^}]*\}|\\multicolumn\{\d+\}"),             # the label of a figure, column spans
         re.compile(r"\\begin\{tabularx\}\{\\linewidth\}\{[^\n]*"),              # the column widths of the table
         re.compile(r"\\cmidrule(\([^)]*\))?\{[^}]*\}")]
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
    """The phrase is in the text, and each number it prints (with its unit 万, 亿 or 万亿; a minus sign not read) is the
    value given, within half a unit of its last digit (plus `slack`, in the same units). None skips a number (one
    checked by an assertion)."""
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


def arithmetic() -> None:
    """Every chain a = b (or a ≈ b) of the text's math whose parts are plain arithmetic holds, to the rounding of the
    printed result."""
    n = 0
    for m in re.finditer(r"\$([^$]*)\$", tex_text()):
        vals = []
        for part in re.split(r"=|\\approx", m.group(1)):
            e = part.replace("\\%", "").replace("^{2}", "**2").strip()
            if re.fullmatch(r"[\d.+\-*/() ]+", e) and re.search(r"\d", e):
                vals.append((e, eval(e)))                                       # noqa: S307 - digits and operators only
        for (_, v1), (e2, v2) in zip(vals, vals[1:]):
            decimals = len(e2.split(".")[1]) if re.fullmatch(r"-?\d+\.\d+", e2) else 0
            assert abs(v1 - v2) <= 0.5 * 10 ** -decimals + 1e-9, m.group(1)
            n += 1
    assert n >= 10, n
    print(f"ok {n} equalities of plain arithmetic in the text")


def paragraph(start: str) -> str:
    """The paragraph of the text that contains `start`, from `start` to its end."""
    t = tex_text()
    return t[t.index(start):].split("\n")[0]


MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]


def month(rid: str, name: str) -> int:
    """The month a row prints by its English name (in capitals on Bouey's cover)."""
    has(rid, name)
    return [m.lower() for m in MONTHS].index(name.lower()) + 1


def day(y: float, m: int, d: float) -> str:
    return pd.Timestamp(int(y), m, int(d)).day_name()


# ---------------------------------------------------------------------------------------------------
# Teaching inputs and models
EX = dict(pi=2.0, y=2.5, v=-1.0, v_fast=-4.0)                 # ex:monetarism-target
SC = dict(pi=2.0, y=3.0, v=-1.0, v_fast=-3.0, sv=3.0)       # self-checks 1-3
POOLE = dict(a1=-1.0, b1=1.0, b2=-0.5, su=1.0, sv=(1.0, 4.0))  # ex:monetarism-poole and Figure monetarism_poole
VLINES = (1979, 1982, 1986)                                 # the vertical lines of Figure monetarism_velocity

EQ_TARGET = r"m^{*}=\pi^{*}+y^{*}-v^{*} .\label{eq:monetarism-target}"
EQ_POOLE = (r"\sigma^{2}_{Y,r}=\sigma^{2}_{u},\qquad" "\n"
            r"\sigma^{2}_{Y,M}=\frac{b_2^{2}\,\sigma^{2}_{u}+a_1^{2}\,\sigma^{2}_{v}}{(a_1b_1+b_2)^{2}} ."
            r"\label{eq:monetarism-poole}")


def target(pi: float, y: float, v: float) -> float:
    """eq:monetarism-target: the money growth that gives inflation pi with output growth y and velocity change v."""
    return pi + y - v


def inflation(m: float, y: float, v: float) -> float:
    """The identity m + v = pi + y solved for inflation."""
    return m + v - y


def poole_var(a1: float, b1: float, b2: float, su: float, sv: float, suv: float = 0.0) -> float:
    """The variance of output under a money-stock policy: Poole's loss (6) as Poole and Lieberman print it; with
    suv = 0 it is eq:monetarism-poole."""
    return (a1 ** 2 * sv - 2 * a1 * b2 * suv + b2 ** 2 * su) / (a1 * b1 + b2) ** 2


def threshold(a1: float, b1: float, b2: float, su: float) -> float:
    """The variance of the monetary disturbance at which the two instruments give the same variance of output."""
    return ((a1 * b1 + b2) ** 2 - b2 ** 2) * su / a1 ** 2


def solve(a1, b1, b2, a0, b0, money, u, v) -> tuple[float, float]:
    """Output and the interest rate with the money stock fixed: L = b0 + b1 Y + b2 r + v = money, Y = a0 + a1 r + u."""
    A = np.array([[b1, b2], [1.0, -a1]])
    rhs = np.array([money - b0 - v, a0 + u])
    Y, r = np.linalg.solve(A, rhs)
    return float(Y), float(r)


def models() -> None:
    t = TEX.read_text(encoding="utf-8")
    assert EQ_TARGET in t and EQ_POOLE in t
    # Poole and Lieberman's equations as the page image prints them
    has("pl_eq1", "(1) L = bo+ biY + b2r + v, b1 > O, b2 < 0;")
    has("pl_eq5", "(5) Y = a0 + a1r + u, a1 < 0,")
    has("pl_loss", "(6) LM = (a1b1 + b2)^-2 (a1^2 σv^2 - 2a1b2σuv + b2^2 σu^2)")
    has("pl_earlier", "loss from following a money stock policy")
    has("pl_lr", "under an interest rate policy")
    rng = np.random.default_rng(45)
    for _ in range(300):
        a1, b1, b2 = -rng.uniform(0.1, 3), rng.uniform(0.1, 3), -rng.uniform(0.1, 3)
        a0, b0, money = rng.uniform(-5, 5, 3)
        su, sv = rng.uniform(0.1, 5, 2)
        suv = rng.uniform(-1, 1) * np.sqrt(su * sv)
        # the reduced form: output moves by (b2 u - a1 v)/(a1 b1 + b2) under the money target
        Y0, r0 = solve(a1, b1, b2, a0, b0, money, 0.0, 0.0)
        u, v = rng.normal(size=2)
        Y1, r1 = solve(a1, b1, b2, a0, b0, money, u, v)
        D = a1 * b1 + b2
        assert np.isclose(Y1 - Y0, (b2 * u - a1 * v) / D)
        cu, cv = b2 / D, -a1 / D
        # Poole's loss (6) is the variance of that output; eq:monetarism-poole when the disturbances are uncorrelated
        assert np.isclose(cu ** 2 * su + cv ** 2 * sv + 2 * cu * cv * suv, poole_var(a1, b1, b2, su, sv, suv))
        # a demand shock: the money target lets the rate rise and passes on only part of it (0 < cu < 1); the rate
        # target passes it on whole
        assert 0 < cu < 1
        Yd, rd = solve(a1, b1, b2, a0, b0, money, 1.0, 0.0)
        assert rd > r0
        # a shift of money demand moves output under the money target and leaves it under the rate target
        assert not np.isclose(cv, 0)
        # the larger the monetary disturbance, the worse the money target; the larger the real one, the worse the
        # rate target (its variance su rises faster than the money target's)
        assert poole_var(a1, b1, b2, su, sv + 1) > poole_var(a1, b1, b2, su, sv)
        assert (su + 1) - poole_var(a1, b1, b2, su + 1, sv) > su - poole_var(a1, b1, b2, su, sv)
        # the two are equal at the threshold
        s = threshold(a1, b1, b2, su)
        assert np.isclose(poole_var(a1, b1, b2, su, s), su)
    for _ in range(300):
        pi, y, v = rng.uniform(-5, 10, 3)
        m = target(pi, y, v)
        assert np.isclose(inflation(m, y, v), pi)                               # the target gives the inflation wanted
        assert np.isclose(inflation(m, y, v - 1) - inflation(m, y, v), -1)       # velocity falls faster: inflation lower
    print("ok the key equations and the claims made of them on 600 random draws")


# ---------------------------------------------------------------------------------------------------
# 4. The text, section by section
def guide(F, Y, Q):
    t = TEX.read_text(encoding="utf-8")
    assert f"\\guidequestion{{{GUIDE}}}" in t and GUIDE == PREV
    assert chapter("ch44_naturalrate").rstrip().endswith(PREV)                  # 第 44 章交来的问题
    assert "\\guideprereq{\\chref{ch:naturalrate}\\enspace\\nameref{ch:naturalrate}；\\chref{ch:money}\\enspace" \
           "\\nameref{ch:money}}" in t
    has("fs_press", "in press, 1963")
    said("说明弗里德曼与施瓦茨（1963）的货币史证据在论证中的作用", F["fs_press"][2])
    has("loc_thatcher", "Prime Minister", "1979 general election")
    said("分析撒切尔政府（1979 年起）与美联储 1979—1982 年货币目标制的实践", F["loc_thatcher"][0],
         F["fomc79_date"][1], F["fomc82o_date"][1])
    say("概括货币主义的核心命题：货币需求稳定、单一规则、长期中性", "解释货币需求不稳定为什么让各国最终放弃货币目标制")
    assert "\\chapterstub" not in t


def opening(F, Y, Q):
    d, y = F["h80_date"]
    m = month("h80_date", "March")
    assert day(y, m, d) == "Wednesday"
    said("1980 年 3 月 26 日是星期三", y, m, d)
    has("h80_speaker", "Chancellor of the Exchequer (Sir Geoffrey Howe)")
    has("h80_red", "part II of the Financial Statement and Budget Report", "Red Book")
    has("h80_heart", "a target for a steadily declining growth of the money supply")
    has("h80_monetarism", "accommodated by an excessive expansion of money and credit")
    has("law86_broad", "sterling M3")
    has("h80_months", "mid-February this year")
    feb = month("h80_months", "February")
    has("h80_range", "mid-April 1981", "at an annual rate")
    assert (F["h80_range"][0] - y) * 12 + month("h80_range", "April") - feb == F["h80_months"][0]   # 14 个月
    said("豪宣布，从 1980 年 2 月中旬起的 14 个月里，它按年率增长 7\\% 到 11\\%", y, feb, F["h80_months"][0],
         F["h80_range"][1], F["h80_range"][2])
    S = F["h80_six"]
    has("h80_six", "just half the rate of growth over the past year")
    said("到 1983—1984 财政年度，目标要降到 6\\% 左右", S[0], 1900 + S[1], S[2])
    has("h80_laugh", "Members may laugh")
    has("h80_plan", "a national plan—Opposition")
    qy, qm = year_in("qb1981_45", r"March (\d{4})"), MONTHS.index("March") + 1
    assert qy == y + 1                                                           # 一年以后
    said("一年以后，英格兰银行在 1981 年 3 月的季刊里交了账", qy, qm)
    G = F["qb81_20"]
    said("到 1981 年 2 月中旬，£M3 一年里增长了约 20\\%", G[3], month("qb81_20", "February"), G[2])
    has("qb81_20", "mid-February 1981")
    said("也有约 17.5\\%，远在 7\\% 到 11\\% 的目标之上", *F["qb81_175"][:3])
    assert F["qb81_175"][1:3] == F["h80_range"][1:3]
    has("h80_corset", "supplementary special deposit scheme", '"corset"', "mid-June")
    said("豪在演说里宣布它 6 月中旬到期后不再延续", month("h80_corset", "June"))
    has("qb81_m1", "less than half as fast")
    said("同期只增长 8.5\\%", F["qb81_m1"][0])
    has("loc_leighpemberton", "appointed governor of the Bank of England in 1983")
    assert F["loc_leighpemberton"][4] <= F["lp86_issue"][0] < F["loc_leighpemberton"][4] + F["loc_leighpemberton"][5]
    said("1986 年回顾说，通胀的高峰超过 20\\%", F["lp86_issue"][0], F["lp86_peak"][0])
    has("lp86_peak2", "of this year")
    said("1982 年 4 月，通胀降到 10\\% 以下，1986 年 3 月又降到 5\\% 以下", F["lp86_peak2"][0],
         month("lp86_peak", "April"), F["lp86_peak"][1], F["lp86_issue"][0], month("lp86_peak2", "March"),
         F["lp86_peak2"][1])
    assert F["qb81_20"][2] > F["h80_range"][2]                                   # the money ran far above the target
    assert paragraph("物价却降了下来").endswith(GUIDE)                            # the opening ends with the question


def world(F, Y, Q):
    has("fs_title", "MONEY AND BUSINESS CYCLES")
    has("fs_authors", "Milton Friedman and Anna J. Schwartz")
    said("那时两人的《美国货币史》正在付印，注明 1963 年", F["fs_press"][2])
    has("fs_dance", "Irving Fisher", "a dance of the dollar")
    has("fs_samuelson", "best selling textbook", "is investment")
    has("fs_passive", "purely passive role")
    has("fs_revival", "concern about inflation")
    has("fs_money", "currency plus adjusted deposits in commercial banks (both demand and time)")
    said("1867—1960 年，美国的货币存量在经济扩张时增长", *F["fs_money"])
    has("fs_rise", "rise during both cyclical expansions and cyclical contractions")
    S = F["fs_six"]
    six = [(S[i], S[i] - S[i] % 100 + S[i + 1], S[i + 2]) for i in range(0, len(S), 3)]
    assert len(six) == 6 and all(a < b for a, b, _ in six)                       # 六次
    lo, hi = min(six, key=lambda x: x[2]), max(six, key=lambda x: x[2])
    said("重大的例外只有六次，下降最少的是 1937—1938 年，降了 2.4\\%", *lo)
    said("下降最多的是 1929—1933 年，降了 35.2\\%", *hi)
    has("fs_major", "major as judged by other indicators")
    has("fs_props", "necessary and sufficient condition", "long secular changes",
        "periods roughly the length of business cycles")
    has("fs_conjecture", "longer-period changes in money income")
    has("fs_open", "leaves open the reasons for the change")
    said("\\chref{ch:naturalrate}讲过他 1967 年 12 月的会长演说", F["f68_date"][1], month("f68_date", "December"))
    has("f68_star", "a space vehicle that has taken a fix on the wrong star")
    has("f68_three", "exchange rates, the price level", "the quantity of a monetary total")
    has("f68_matters", "it matters much less which particular total is chosen than that one be chosen")
    has("f68_toolate", "Too late and too much")
    has("f68_lags", "six or nine or twelve or fifteen months later")
    has("f68_moderate", "moderate inflation or moderate deflation")
    for rid in ("bou_1975", "rich_1974", "gwz_1975"):
        assert F[rid][0] // 10 * 10 == 1970, rid
    said("1970 年代，各国央行陆续公布了货币目标", 1970)
    said("\\chref{ch:naturalrate}讲过，联邦储备 1974 年想把 M1 的增长控制在 6\\% 以内",
         *there("ch44_naturalrate", "一是把 M1 的增长大致控制在经济顾问委员会 1974 年报告预示的 6\\% 以内"))
    has("mp_squeeze", "mid-1974")
    assert F["mp_squeeze"][0] == 1974
    has("mp_explicit", "explicitlystatedtargetsfor real output andemployment")
    has("bou_1975", "explicit monetary aggregate target")
    said("加拿大银行从 1975 年起以 M1 为明确的目标", F["bou_1975"][0])
    has("rich_1974", "At the end of 1974", "the following year", "M1 by 6 percent")
    said("瑞士国家银行在 1974 年底宣布了 1975 年的目标", F["rich_1974"][0], F["rich_1974"][0] + 1)
    has("gwz_1975", "since 1975")
    said("联邦德国的联邦银行也从 1975 年起每年公布货币目标", F["gwz_1975"][0])


def theory(F, Y, Q):
    has("h80_abuse", "term of political abuse")
    gy = year_in("gf1976_45", r"Activity (\d{4})\(3\)")
    has("gf_few", "at leastpriorto 1974", "essentiallyincome and interest rates", "lags")
    said("Goldfeld 1976 年总结说，至少在 1974 年以前", gy, F["gf_few"][0])
    has("gwz_three", "three benchmark figures")
    said("2008 年以后，美联储处在地板体系，准备金有利息",
         *there("ch04_money", "2008 年以后，美联储处在地板体系，准备金有利息"))
    has("h80_green", "monetary base control", "last week")
    has("h80_views", "The Governor and I hope to hear a wide range of views")
    said("豪在 1980 年的演说里提到", F["h80_date"][1])
    # ex:monetarism-target
    m = target(EX["pi"], EX["y"], EX["v"])
    pi_fast = inflation(m, EX["y"], EX["v_fast"])
    m_need = target(EX["pi"], EX["y"], EX["v_fast"])
    said("设央行能容忍的通胀是 2\\%，潜在产出每年增长 2.5\\%，流通速度每年下降 1\\%", EX["pi"], EX["y"], -EX["v"])
    said("若流通速度实际每年下降 4\\%", -EX["v_fast"])
    said("要得到 2\\% 的通胀", EX["pi"])
    said("$m^{*}=2+2.5-(-1)=5.5\\%$", EX["pi"], EX["y"], -EX["v"], m)
    assert pi_fast < 0                                                           # 物价反而下降
    said("$\\pi=5.5+(-4)-2.5=-1\\%$", m, -EX["v_fast"], EX["y"], -pi_fast)
    said("$m=2+2.5+4=8.5\\%$，比原来的目标高 3 个百分点", EX["pi"], EX["y"], -EX["v_fast"], m_need, m_need - m)
    # the pitfall: the Governor's velocity is the example's
    has("lp86_facile", "too facile", "frequently adjusted or overridden")
    has("lp86_relax", "mistaken by those with an over-simple approach to these questions for a policy relaxation")
    said("利-彭伯顿 1986 年说，货币规则若太简单", F["lp86_issue"][0])
    has("lp86_velocity", "Since 1980", "an average of 4% a year")
    said("按他的说法，1980 年以来英国广义货币的流通速度每年下降 4\\%", *F["lp86_velocity"])
    assert F["lp86_velocity"][1] == -EX["v_fast"]
    has("law86_faster", "Throughout the 1980s", "broad money has grown far faster than money GDP")
    has("law86_threat", "has not posed a threat to inflation")
    said("劳森 1986 年也说，整个 1980 年代广义货币的增长远快于货币 GDP", F["law86_date"][1], F["law86_faster"][0])


def poole(F, Y, Q):
    py = year_in("pl1972_45", r"Activity (\d{4})\(2\)")
    has("pl_authors", "WILLIAM POOLE", "Board of Governorsof the Federal Reserve System")
    said("1972 年，联邦储备理事会的普尔", py)
    has("pl_moved", "the money stock as their principal instrument")
    has("pl_before", "before 1970 they controlled interest rates")
    said("1970 年以前，他们控制利率，看着货币存量", F["pl_before"][0])
    said("1970 年以后，他们控制货币存量，看着利率", F["pl_before"][0])
    has("pl_monthly", "standard error of less than 1 percent")
    said("月度的货币水平能控制到 1\\% 以内的标准误差", F["pl_monthly"][0])
    has("pl_three", "annual rate of as much as 5.6 percent for the growth rate over three months")
    said("误差却可能达到 5.6\\%", F["pl_three"][0])
    has("pl_responses", "Three major responses")
    has("pl_r2", "abandon attempts to control the money stock")
    has("pl_doctrine", "no more closely related to monetarist doctrine")
    has("pl_superior", "optimal interest rate policy superior to an optimal money stock policy")
    has("pl_qje2", "(May 1970)")
    said("普尔 1970 年的回答", F["pl_qje2"][1])
    has("pl_poole0", "originate primarily in the IS function")
    has("pl_poole", "the money stock is the proper control instrument", "the interest rate is the proper co")
    said("其中$b_1>0$，$a_1<0$，$b_2<0$", 0, 0, 0)
    # ex:monetarism-poole and the figure
    P = POOLE
    a1, b1, b2, su = P["a1"], P["b1"], P["b2"], P["su"]
    D2 = (a1 * b1 + b2) ** 2
    v1, v4, s = poole_var(a1, b1, b2, su, P["sv"][0]), poole_var(a1, b1, b2, su, P["sv"][1]), threshold(a1, b1, b2, su)
    said("设$a_1=-1$，$b_1=1$，$b_2=-0.5$，实体扰动的方差$\\sigma^{2}_{u}=1$", -a1, b1, -b2, su)
    said("货币扰动的方差$\\sigma^{2}_{v}=1$时", P["sv"][0])
    said("$\\sigma^{2}_{v}=4$时呢？", P["sv"][1])
    said("$(a_1b_1+b_2)^{2}=(-1.5)^{2}=2.25$", -(a1 * b1 + b2), D2)
    assert v1 < su < v4
    said("$\\sigma^{2}_{Y,M}=(0.25+1)/2.25\\approx0.56$，小于盯利率的 1", b2 ** 2 * su, P["sv"][0], D2, v1, su)
    said("$\\sigma^{2}_{Y,M}=(0.25+4)/2.25\\approx1.89$，大于 1", b2 ** 2 * su, P["sv"][1], D2, v4, su)
    said("令$(0.25+\\sigma^{2}_{v})/2.25=1$，得$\\sigma^{2}_{v}=2$", b2 ** 2 * su, D2, su, s)
    said("实体扰动的方差固定为 1", su)
    said("两线在$\\sigma^{2}_{v}=2$处相交", s)
    said("参数$a_1=-1$，$b_1=1$，$b_2=-0.5$是教学用的假设", -a1, b1, -b2)
    # Goldfeld
    gy = year_in("gf1976_45", r"Activity (\d{4})\(3\)")
    has("gf_overpredict", "pre1974 data", "consistently and significan")
    said("Goldfeld 1976 年发现，用 1974 年以前的数据拟合得很好的货币需求方程", gy, F["gf_overpredict"][0])
    has("gf_13", "ten-quarterperiod", "overpredicts")
    has("gf_13b", "an averageof $13 billion in 1972 prices")
    said("平均高估 130 亿美元（1972 年价格）", F["gf_13b"][0] * 1e9, F["gf_13b"][1])
    has("gf_98", "1976:2", "whopping9.8 percent", "nearly$30 billionin currentprices")
    said("1976 年第二季度的误差达 9.8\\%，按当年价格近 300 亿美元", F["gf_98"][1], F["gf_98"][3], F["gf_98"][4] * 1e9)
    has("gf_title", "The Case of the Missing Money")
    has("gf_poole", "tilt policy in the direction of an interest-ratepolicy")
    has("gf_clearly", "interest-ratepolicy over an Ml policy")
    has("gf_ratchet", "ratcheteffect")
    has("moses_three", "Since the mid 1970s")
    said("1970 年代中期以后货币需求不再稳定", F["moses_three"][0])


def america(F, Y, Q):
    said("美国：1979—1982 年", F["fomc79_date"][1], F["fomc82o_date"][1])
    d, y = F["fomc79_date"]
    m = month("fomc79_date", "October")
    assert day(y, m, d) == "Saturday"
    said("1979 年 10 月 6 日是星期六", y, m, d)
    has("fomc79_called", "called by the Chairman")
    has("loc_volcker2", "chairman of the Federal Reserve from 1979 to 1987")
    assert F["loc_volcker2"][0] <= y < F["loc_volcker2"][1] and F["gnd_volcker_fed"] == F["loc_volcker2"]
    has("fomc79_feb", "established in February")
    said("1978 年第四季度到 1979 年第四季度 M1 增长 1.5\\% 到 4.5\\%", *F["fomc79_period"], *F["fomc79_ranges"][:2])
    M = F["fomc79_m1q"]
    has("fomc79_m1q", "decline at a rate of about 2 percent in the first quarter")
    said("第一季度按年率下降约 2\\%，第二、第三季度却按年率增长约 7.5\\% 与 9.5\\%", M[2], M[0], M[1])
    has("fomc79_shift", "supplying the volume of bank reserves")
    has("fomc79_few", "A few members")
    has("fomc79_directive", "from September to December")
    said("1979 年的转向是谁定的？委员会指示，9 月到 12 月 M1 按年率增长约 4.5\\%", y,
         month("fomc79_directive", "September"), month("fomc79_directive", "December"), F["fomc79_directive"][0])
    has("fomc79_weekly", "weekly averages")
    said("联邦基金利率的周平均大体留在 11.5\\% 到 15.5\\% 之间", *F["fomc79_funds"])
    yes, no = votes("fomc79_vote")
    assert yes[0] == "Volcker" and no == [] and "None" in words_of("fomc79_vote")
    said("投赞成票的是沃尔克等 12 人，没有反对票", len(yes))
    has("fomc79_after", "after the meeting of the Committee")
    has("fomc79_marginal", "managed liabilities")
    said("会后，理事会把贴现率从 11\\% 提到 12\\%，对管理负债的增加额设了 8\\% 的边际准备金要求",
         *F["fomc79_board"], F["fomc79_marginal"][0])
    has("fomc79_confidence", "increase confidence at home and abroad")
    # February 1982
    y82, feb = F["fomc82f_date"][2], month("fomc82f_date", "February")
    B = F["fomc82f_m1b"]
    has("fomc82f_m1b", "adjusted for shifts into NOW accounts", "below the lower end")
    said("委员会在 1982 年 2 月回顾 1981 年时说", y82, feb, B[1])
    said("M1-B 只增长约 2.25\\%，比目标下限低约 1.25 个百分点", B[2], B[3])
    has("fomc82f_def2", "negotiable orders of withdrawal (NOW)", "automatic transfer service (ATS)")
    has("fomc82f_m2m3", "above")
    said("其中 M2 增长约 9.5\\%", F["fomc82f_m2m3"][0])
    has("fomc82f_why", "financial innovations and high interest rates")
    has("fomc82f_drop", "abandon the compilation of M1-A and the shift-adjusted M1-B")
    said("从 1982 年起，M1-A 与按转移调整的 M1-B 不再编制", F["fomc82f_drop"][0])
    has("fomc82f_ml", "formerly labeled Ml-B", "the total amount of NOW accounts")
    R = F["fomc82f_range82"]
    has("fomc82f_range82", "tentatively established in mid-1981")
    said("委员会重申了 1981 年年中暂定的 1982 年区间，M1 是 2.5\\% 到 5.5\\%", R[1], R[0], R[4], R[5])
    has("fomc82f_aberration", "temporary aberration")
    # October 1982
    d, y = F["fomc82o_date"]
    oc = month("fomc82o_date", "October")
    said("1982 年 10 月 5 日，委员会又退了一步", y, oc, d)
    said("10 月初有大批全民储蓄存单（all savers certificates）到期", month("fomc82o_savers", "October"))
    has("fomc82o_didc", "Depository Institutions Deregulation Committee")
    has("fomc82o_basis", "no basis existed for predicting its magnitude")
    has("fomc82o_weight", "much less than the usual weight")
    said("联邦基金利率若持续落在 7\\% 到 10.5\\% 之外", *F["fomc82o_funds"])
    yes, no = votes("fomc82o_vote")
    assert no == ["Black", "Ford", "Horn"] and yes[0] == "Volcker"
    said("这次表决 9 票对 3 票", len(yes), len(no))
    has("fomc82o_horn", "Mrs. Horn dissented", "specific objective for growth of M1")
    has("fomc82o_dissent", "Mr. Black dissented")
    has("fomc82o_ford", "Mr. Ford dissented")
    has("fomc82o_fiscal", "misinterpreted", "highly expan")
    # who paid
    has("fomc82f_gnp", "real gross national product had declined")
    has("fomc82f_jobs", "more than 700,000 in the fourth quarter")
    said("代价落在谁身上？委员会 1982 年 2 月的记录写道，1981 年第四季度实际国民生产总值按年率下降约 5.25\\%，"
         "制造业减少了 70 多万个工作", y82, feb, F["fomc82f_gnp"][1], F["fomc82f_gnp"][0], F["fomc82f_jobs"][0] / 1e4)
    said("12 月的失业率又升了 0.5 个百分点，到了 8.9\\%", month("fomc82f_unemp", "December"), *F["fomc82f_unemp"])
    has("fomc82o_unemp", "unchanged")
    has("fomc82o_claims", "mid-September", "new high")
    said("10 月的记录写道，8 月的失业率仍是 9.8\\%，9 月中旬首次申领失业保险的人数创了新高", oc,
         month("fomc82o_aug", "August"), F["fomc82o_unemp"][0], month("fomc82o_claims", "September"))
    has("fomc82o_staff", "unemployment would remain at a high level")
    has("fomc82o_staff0", "1983")
    # the velocity: Figure monetarism_velocity and the paragraph after it
    U = us()
    v1, v2 = U["v1"], U["v2"]
    said("美国 M1 与 M2 的流通速度，1959—1999 年", U.index[0], U.index[-1])
    dec = month("erp_b67_december", "December")
    has("erp_b67_note", "from December to December")
    has("erp_b67_dec", "Averages of daily figures")
    said("流通速度是当年的名义 GDP 除以 12 月的货币存量", dec)
    rises = [y for y in range(1960, 1982) if v1[y] > v1[y - 1]]
    assert len(rises) >= 20                                                      # 大体一直上升 (one fall, 1967)
    assert all(growth(y) < -4 for y in (1982, 1985, 1986))                       # 急降
    said("M1 的流通速度到 1981 年大体一直上升，1982 年与 1985—1986 年急降", 1981, 1982, 1985, 1986)
    assert v2.loc[1959:1990].max() - v2.loc[1959:1990].min() < 0.25            # 窄的范围
    assert v2.loc[1991:1999].max() > v2.loc[1959:1990].max() + 0.2             # 1990 年代上升
    said("M2 的流通速度直到 1990 年都在一个窄的范围里，1990 年代上升", 1990, 1990)
    assert VLINES[:2] == (F["fomc79_date"][1], F["fomc82o_date"][1])
    assert VLINES[2] == min(range(1960, 2000), key=growth)                       # the largest fall
    said("竖线标出 1979、1982 与 1986 年", *VLINES)
    has("erp_b1_title", "Gross domestic product")
    has("erp_b67_title", "Money stock and debt measures")
    said("数据：《总统经济报告》（2000）表 B-1 与 B-67", year_in("erpb1_45", r"February (\d{4})"))
    said("用当年的名义 GDP 除以 12 月的 M1", dec)
    said("1959 年它约为 3.6，1981 年约为 7.2", 1959, velocity(1959), 1981, velocity(1981))
    g = 100 * ((velocity(1981) / velocity(1959)) ** (1 / 22) - 1)
    said("22 年里平均每年上升约 3.2\\%", 1981 - 1959, g)
    said("1982 年它下降 4.3\\%，1986 年又下降 9.6\\%", 1982, -growth(1982), 1986, -growth(1986))
    said("M1 的流通速度若照 1981 年以前的趋势走", 1981)


def britain(F, Y, Q):
    has("h80_priority", "the first priority")
    has("h80_illusion", "It is an illusion")
    has("h80_path", "a four-year path for monetary growth, public spending and tax policies")
    has("h80_governor", "the Governor of the Bank of England. We have agreed")
    has("h80_swollen", "sterling M3 will be swollen")
    has("h80_signal", "will not, however, signal a change in underlying monetary conditions")
    has("lp86_exchange", "towards the end of 1979", "direct domestic monetary controls")
    said("利-彭伯顿 1986 年解释，1979 年底英国取消了外汇管制", F["lp86_issue"][0], F["lp86_exchange"][0])
    has("lp86_1976", "under a different government")
    said("现行货币政策的基础其实是 1976 年在另一届政府手里打下的", F["lp86_1976"][0])
    c = there("ch44_naturalrate", "1976 年 9 月 28 日在工党大会上的话")
    assert c[0] == F["lp86_1976"][0]                                             # 同年
    said("同年 9 月，工党的首相在党的大会上已经改了口", c[1])
    qy, qm = year_in("qb1981_45", r"March (\d{4})"), MONTHS.index("March") + 1
    has("qb81_25", "nearly 25% in the autumn")
    said("英格兰银行 1981 年 3 月说，£M3 的年增长率秋天接近 25\\%", qy, qm, F["qb81_25"][0])
    P = F["qb81_psbr"]
    has("qb81_psbr", "£13½ billion", "public sector borrowing requirement (PSBR)", "by £5 billion")
    said("1980—1981 年度的公共部门借款需求（PSBR）估计是 135 亿英镑，比 1980 年 3 月的预测多 50 亿英镑", P[1],
         1900 + P[2], P[0] * 1e9, P[3], month("qb81_psbr", "March"), P[4] * 1e9)
    L = F["qb81_plan"]
    has("qb81_plan", "PSBR of £10½ billion in 1981/82")
    said("1981 年 3 月的预算把 PSBR 定在 105 亿英镑左右", L[0], month("qb81_plan", "March"), L[1] * 1e9)
    assert F["qb81_target"] == L[5:7]
    said("£M3 的新目标定为 6\\% 到 10\\%", *F["qb81_target"])
    has("qb81_mlr", "minimum lending rate (MLR)")
    said("英格兰银行的最低贷款利率同时从 14\\% 降到 12\\%", *F["qb81_mlr"])
    has("h80_tough", "unnecessarily tough policies")
    has("h80_tough2", "tough policies inescapable")
    has("h80_relaxed", "simply fuel fresh inflation")
    has("h80_crisis", "destroy jobs")
    has("qb81_q4", "manufacturing production in the year to the fourth quarter of 1980", "the largest recorded")
    has("qb81_war", "period since the war")
    said("截至 1980 年第四季度的一年里，制造业产出下降约 15\\%", F["qb81_q4"][1], F["qb81_q4"][0])
    has("qb81_labour", "reduced stocks and labour particularly sharply in the fourth quarter", "fixed investment")
    has("qb81_real", "High interest rates in real")
    has("qb81_mortgage", "BSA recommended mortgage rate")
    said("建筑协会建议的住房抵押贷款利率先降到 14\\%，后来又降到 13\\%", *F["qb81_mortgage"])
    said("英国的失业率 1981 年是 9.6\\%，1983 年到了 11.5\\%",
         *there("ch44_naturalrate", "1981 年是 9.6\\%，1983 年到了 11.5\\%"))
    # Lawson, 1986 and 1987
    d, y = F["law86_date"]
    has("loc_lawson2", "Chancellor of the Exchequer since June 1983")
    assert F["loc_lawson2"][0] <= y
    said("1986 年 3 月 18 日，财政大臣劳森", y, month("law86_date", "March"), d)
    has("law86_heart", "GDP in cash terms")
    has("law86_halved", "has been halved")
    has("law86_low", "the range was set too low")
    said("新的范围提高到 11\\% 到 15\\%", *F["law86_range"])
    has("law86_rates", "the essential instrument of monetary policy")
    has("law86_m0", "as foreshadowed in last year's MTFS")
    said("劳森给狭义货币 M0 定的区间是 2\\% 到 6\\%", *F["law86_m0"])
    has("law86_narrow", "reasonably quick and direct effect on narrow money")
    has("law86_essence", "no change whatever in the essence")
    has("lp86_date", "On 22 October.")
    has("lp86_lecture", "Loughborough University Banking Centre Lecture in Finance")
    said("同年 10 月 22 日，利-彭伯顿在拉夫堡大学的演讲里讲了原因", month("lp86_date", "October"), F["lp86_date"][0])
    has("lp86_rose1", "From the end of the war until 1979")
    has("lp86_rose", "brief, though sharp, interruption", "its velocity of circulation rose")
    said("从二战结束到 1979 年，除了 1971—1973 年短暂而剧烈的中断", F["lp86_rose1"][0], F["lp86_rose"][0],
         1900 + F["lp86_rose"][1])
    said("1980 年以后，它平均每年下降 4\\%", *F["lp86_velocity"])
    has("lp86_twoofsix", "Only two of the past six annual target rates of growth for £M3 have been achieved")
    has("lp86_marksman", "marksman")
    has("lp86_adjust", "severe injury on the economy")
    has("lp86_success", "a good deal more successful in achieving our ultimate objective")
    d, y = F["law87_date"]
    said("1987 年 3 月 17 日，劳森说", y, month("law87_date", "March"), d)
    has("law87_central", "squeeze inflation out of the system")
    has("law87_rates", "short-term interest rates", "monetary conditions")
    has("law87_eschew", "Loughborough lecture")
    # Canada
    d, y = F["bou_date"]
    has("bou_date", "CANADIAN CLUB TORONTO")
    said("1982 年 11 月 29 日，加拿大银行行长 Bouey", y, month("bou_date", "NOVEMBER"), d)
    has("bou_reliable", "more than a year", "less reliable guide")
    has("bou_drop", "no longer has a target range for it")
    has("bou_regret", "I regret this development")
    has("bou_strains", "high unemployment", "many business failures")
    has("bou_why", "systematically related to the trend of total spending")
    has("bou_dollar", "the exchange rate")
    said("Bouey 在 12 月说", month("boud_date", "December"))
    has("boud_1975", "Annual Report for 1975")
    said("他引了自己在 1975 年年报里的话", F["boud_1975"][0])
    has("boud_habits", "innovations in payments technology")


def goodhart(F, Y, Q):
    has("moses_title", "Research Discussion Paper 8301")
    has("moses_three", "Three related problems", "slower growth in Ml than its historical relation with GDP")
    said("1983 年，澳大利亚储备银行的 Moses 在一篇讨论稿里列出美国 1970 年代中期以来的三个问题", F["moses_title"][1],
         F["moses_three"][0])
    has("moses_goodhart", "Charles Goodhart, of the Bank of England", "rule-of-thumb")
    has("moses_rule", "tend to collapse once pressure is placed upon it for control purposes", "(Goodhart, 1975")
    assert F["moses_rule"][0] == F["moses_ref"][0]
    said("照古德哈特 1975 年的经验法则", F["moses_rule"][0])
    has("moses_credit", "Goodhart's law")
    has("moses_islm", "IS-LM framework")
    has("moses_slope", "altered the slope of the LM curve")
    has("moses_shift", "shifting the relevant LM curve to the right")
    has("moses_redefine", "such redefinitions cannot")
    has("moses_range", "a range of financial variables")
    has("moses_minsky", "Minsky, 1957")
    said("Moses 还引了明斯基 1957 年的话", F["moses_minsky"][0])
    has("law86_reasons", "innovation and liberalisation in the financial system")


def test(F, Y, Q):
    has("lp86_pace", "over the past five years or so", "United States and the United Kingdom")
    has("lp86_given", "Canada and Australia, for example, have both given up this approach")
    has("lp86_swiss", "Switzerland and Germany", "universal banks")
    said("利-彭伯顿 1986 年说，过去五年左右", F["lp86_issue"][0])
    # the table
    said("联邦银行与瑞士国家银行的货币目标与实际增长（\\%），1975—1998 年", GWZ_YEARS[0], GWZ_YEARS[-1])
    rows = (1975, 1978, 1980, 1983, 1986, 1987, 1988, 1990, 1992, 1995, 1998)
    for y in rows:
        g = gwz(y)
        gt = f"{g['lo']:g}" if g["lo"] == g["hi"] else f"{g['lo']:g}—{g['hi']:g}"
        vals = [y, g["lo"]] + ([] if g["lo"] == g["hi"] else [g["hi"]]) + [g["actual"]]
        if y in RICH_YEARS:
            r = rich(y)
            printed_ = words_of(f"rich_t{y}").split()[3]                       # the outcome as the table prints it
            assert float(printed_) == r["outcome"]
            out = printed_ if r["outcome"] >= 0 else f"${printed_}$"
            line = f"{y} & {gt} & {g['actual']:g} & {r['target']:g} & {out}\\\\"
            vals += [r["target"], abs(r["outcome"])]
        else:
            assert y > max(RICH_YEARS)
            line = f"{y} & {gt} & {g['actual']:g} & — & —\\\\"
        said(line, *vals)
    has("gwz_t10", "Monetary targets and their implementation")
    has("gwz_t10head", "central bank money stock")
    has("gwz_t10m3", "money stock M3 (from 1988)")
    said("联邦银行：Gerberding、Worms 与 Seitz（2004）表 10，1987 年以前是中央银行货币存量，1988 年起是 M3",
         F["gwz_series"][1], F["gwz_t10"][0], *F["gwz_t10m3"])
    has("gwz_t1978", "1978 (5-7) 8")
    has("gwz_t10n2", "Annual Reports for 1977 and 1978")
    said("1978 年是年平均的目标与实际", 1978)
    has("gwz_t10n1", "fourth quarter of the previous year and the fourth quarter of the current year", "1975: Dec. 1974")
    said("其余年份是第四季度对上年第四季度（1975 年为 12 月对 12 月）", 1975, 12, 12)
    has("rich_t1", "Annual Monetary Targets of the SNB")
    has("rich_t1note", "annual averages of year-on-year monthly rates of change")
    said("瑞士国家银行：Rich（2003）表 1，一般是月度同比增长率的年平均", F["ecb_copy"][0], F["rich_t1"][0])
    has("rich_t1980", "over November 1979 level")
    has("rich_t1990", "Year-on-year rate of change in the fourth-quarter level")
    said("1980 年相对 1979 年 11 月的水平，1990 年是第四季度水平的同比", 1980, 1979, month("rich_t1980", "November"), 1990)
    kinds = {y: words_of(f"rich_t{y}").split()[1] for y in RICH_YEARS}
    assert [y for y in RICH_YEARS if kinds[y] == "M1*"] == [1975, 1976, 1977, 1978]
    assert [y for y in RICH_YEARS if kinds[y] == "MBA"] == list(range(1980, 1989))
    assert [y for y in RICH_YEARS if kinds[y] == "MBS"] == [1989, 1990]
    has("rich_t1m1", "M1 according to the definition of 1975")
    has("rich_mba", "adjusted monetary base (MBA), which excluded the month-end bulge in bank reserves")
    has("rich_mbsa_def", "the seasonally adjusted monetary base (MBSA)")
    said("1975—1978 年是 M1，1980—1988 年是剔除月末准备金突增的调整后基础货币，1990 年是经季节调整的基础货币",
         1975, 1978, 1980, 1988, 1990)
    has("rich_t1979", "Temporary exchange rate target")
    assert "rich_t1979" not in F and "rich_t1991" not in F
    said("1979 年没有货币目标，表 1 只列到 1990 年", 1979, F["rich_t1"][0], max(RICH_YEARS))
    r = meta()["retrieved"]
    said("2026 年 11 月 12 日下载", *[int(x) for x in r.split("-")])
    # Figure monetarism_targets
    assert all(f"gwz_t{y}" in F for y in GWZ_YEARS) and "gwz_t1999" not in F
    said("(a) 联邦银行，1979—1998 年", 1979, GWZ_YEARS[-1])
    assert [y for y in range(1979, 1999) if gwz(y)["lo"] == gwz(y)["hi"]] == [1989]
    said("1989 年是 5\\% 的点目标", 1989, gwz(1989)["lo"])
    said("(b) 瑞士国家银行，1975—1990 年", RICH_YEARS[0], RICH_YEARS[-1])
    said("1979 年没有目标", 1979)
    said("数据：Gerberding、Worms 与 Seitz（2004）表 10，Rich（2003）表 1", F["gwz_series"][1], F["gwz_t10"][0],
         F["ecb_copy"][0], F["rich_t1"][0])
    # who decided
    has("gwz_council", "Central Bank Council")
    has("gwz_december", "announced in December")
    said("目标通常在 12 月公布", month("gwz_december", "December"))
    has("rich_three", "three members of the SNB's Governing Board")
    has("rich_decided", "the Governing Board that ultimately took the policy decisions")
    said("理事会通常在 11 月开会，12 月由行长在记者会上宣布", month("rich_board", "November"),
         month("rich_president", "December"))
    # the misses
    G = F["gwz_missed"]
    has("gwz_missed", "missed 7 out of 20 times", "In six of these seven instances", "above target")
    miss = misses()
    above = [y for y in miss if gwz(y)["actual"] > gwz(y)["hi"]]
    below = [y for y in miss if gwz(y)["actual"] < gwz(y)["lo"]]
    assert len(miss) == G[3] and G[0] == G[4] == 1998 - 1979 + 1 and (G[1], G[2]) == (1979, 1998)
    said("1979—1998 年的 20 年里，目标落空 7 次，其中 6 次是实际增长高于目标", G[1], G[2], G[0], G[3], len(above))
    assert len(above) == 6 and len(below) == 1
    said("本书按表 10 数了一遍，落空的是 1986、1987、1988、1992、1993、1995 与 1996 年，只有 1995 年低于目标",
         F["gwz_t10"][0], *miss, *below)
    A = F["gwz_average"]
    has("gwz_average", "just below 6%", "trend rate of output growth of 2.1%", "trend decline of velocity of 1.1%")
    said("1979—1998 年货币的平均增长略低于 6\\%，产出的趋势增长率是 2.1\\%", G[1], G[2], A[0], A[1])
    said("同期流通速度的趋势下降率是 1.1\\%，平均通胀是 2.8\\%", A[2], A[3])
    assert np.isclose(inflation(A[0], A[1], -A[2]), A[3])                        # eq:monetarism-target backwards
    said("$6-2.1-1.1=2.8$", *A)
    N = F["gwz_norm"]
    said("1975—1998 年它从 5\\% 降到 1.75\\%", N[2], N[3], N[0], N[1])
    has("gwz_unavoidable", "Until 1984", "From 1985")
    said("到 1984 年为止，这个数代表", F["gwz_unavoidable"][0])
    said("1985 年起改为中期里能容忍的最大涨幅", F["gwz_unavoidable"][1])
    has("gwz_tolerated", "did not try to achieve its monetary targets at all cost")
    # the case
    has("gwz_midyear", "only once (in 1991)")
    assert gwz(1991)["rev"] != (gwz(1991)["lo"], gwz(1991)["hi"])
    said("复核以后改过目标区间的只有 1991 年一次", F["gwz_midyear"][0])
    C = F["gwz_corridor"]
    widths = {gwz(y)["hi"] - gwz(y)["lo"] for y in range(1979, 1999) if y != 1989}
    assert widths == {C[0], C[1]} and C[3] == 1989 and C[2] == gwz(1989)["lo"]
    said("目标是 2 到 3 个百分点宽的走廊，只有 1989 年是 5\\% 的点目标", C[0], C[1], C[3], C[2])
    assert rich(1975)["target"] == F["rich_1975"][0] == F["rich_1974"][1]
    said("瑞士国家银行在 1974 年底定下 1975 年 M1 增长 6\\% 的目标", F["rich_1974"][0], F["rich_1975"][1],
         F["rich_1975"][0])
    has("rich_gradual", "did not wish to apply a shock therapy")
    has("rich_drop", "by far the sharpest decline recorded after World War II")
    said("1975 年，石油冲击加上紧缩的货币政策，使产出下降 7.5\\%", F["rich_drop"][1], F["rich_drop"][0])
    has("rich_never", "levels never seen before")
    has("rich_pressure", "export sector, the federal government and the general public")
    said("1978 年，瑞士法郎升到前所未见的高度", F["rich_80"][0])
    has("rich_80", "beginning of October 1978", "temporary exchange rate target", "price of the DM")
    said("10 月初，瑞士国家银行宣布临时的汇率目标", month("rich_80", "October"))
    said("的瑞士法郎价格“明显”高于 80", F["rich_80"][1])
    has("rich_explosive", "explosive expansion in the monetary base and the aggregate M1")
    assert rich(1978)["outcome"] - rich(1978)["target"] > F["rich_explosive"][1]
    said("1978 年的目标超出 10 个百分点以上", *F["rich_explosive"])
    has("rich_1988", "massive reduction in the demand for base money")
    has("rich_sic", "world's first real-time gross settlement system")
    said("1988 年，瑞士的银行与央行推出世界上第一个实时全额结算系统", F["rich_1988"][0])
    assert all(rich(y)["outcome"] < 0 for y in (1988, 1989, 1990))
    said("表中 1988—1990 年的负增长就是这样来的", 1988, 1990)
    said("联邦德国与瑞士 · 1975—1999 · 守着货币目标的两家央行", GWZ_YEARS[0], F["rich_1999"][0])
    has("rich_formerly", "head of the economic division of the Swiss National Bank")
    has("rich_trend", "reduce the inflation trend to low levels")
    has("rich_preemptive", "did not call for a sufficiently preemptive pol")
    has("rich_1999", "At the end of 1999", "inflation forecasts")
    said("1999 年底，瑞士国家银行放弃货币目标", F["rich_1999"][0])
    said("联邦银行的年度目标公布到 1998 年为止", GWZ_YEARS[-1])


def debate(F, Y, Q):
    has("fs_tests", "two tests")
    has("fs_ignorance", "different factors may from time to time produce large movements in income")
    has("fs_variety", "a variety of sources")
    has("fs_runs", "vulnerability of the system to runs on banks")
    has("fs_notall", "largely irrelevant for the rises")
    has("fs_china", "how is it that China escaped the early years of the Great Depression")
    has("mk_comment", "HYMAN P. MINSKY")
    K = F["mk_cycles"]
    said("1870—1960 年记录在案的 21 个周期里有 6 个是深度萧条", K[1], K[2], K[0], K[3])
    A = F["mk_administered"]
    has("mk_administered", "specific actions by the Federal Reserve")
    said("其中 1919—1920 年与 1937—1938 年的两次货币下降", A[0], 1900 + A[1], A[2], 1900 + A[3])
    has("mk_crisis", "In the other four deep depression cycles")
    assert K[3] - 2 == 4                                                         # 另外四次
    has("mk_endogenous", "endogenous rather than exogenous")
    d, y = F["boud_date"]
    has("boud_date", "Wednesday, December 8, 1982", "Standing Senate Committee")
    assert day(y, month("boud_date", "December"), d) == "Wednesday"
    said("Bouey 在 1982 年 12 月 8 日对参议院的委员会说", y, month("boud_date", "December"), d)
    has("boud_technical", "solely for these technical reasons")
    has("boud_pilot", "automatic pilot")
    has("gwz_cgg_challenge", "Clarida and Gertler (1997)")
    has("gwz_cgg_test", "gap between the actual money stock and the announced target path")
    has("gwz_realtime", "highly sig")
    has("rich_cycle", "reluctant to admit")
    R = F["rich_1980"]
    has("rich_1980", "from the middle of November 1979 to the middle of November 1980")
    assert rich(1980)["target"] == R[0]
    said("它 1980 年的基础货币目标是增长 4\\%，起点定在 1979 年 11 月", R[2], R[0], R[1], month("rich_1980", "November"))
    has("rich_negative", "a negative target")
    has("rich_omitted", "November 1979 as a starting point")
    has("rich_omitted2", "very few instances")
    has("moses_credit", "credit aggregate")
    said("Moses 1983 年设想", F["moses_title"][1])
    has("lp86_unwise", "just as unwise to pay insufficient regard to the behaviour of broad money")
    said("利-彭伯顿 1986 年却说", F["lp86_issue"][0])
    has("law87_account", "broad money will continue to be taken into account")
    said("劳森 1987 年不再为广义货币设目标", F["law87_date"][1])
    has("rich_m3", "the money stock M3, still play an important role as policy indicators")


def deeper(F, Y, Q):
    said("豪、劳森 1986 年与 1987 年的预算演说据英国议会的历史议事录网站", F["law86_date"][1], F["law87_date"][1])
    fd, fy = F["fomc79_date"]
    said("联邦公开市场委员会 1979 年 10 月 6 日、1982 年 2 月 1—2 日与 10 月 5 日的政策记录", fy,
         month("fomc79_date", "October"), fd, F["fomc82f_date"][2], month("fomc82f_date", "February"),
         F["fomc82f_date"][0], F["fomc82f_date"][1], month("fomc82o_date", "October"), F["fomc82o_date"][0])
    said("英格兰银行 1981 年 3 月的季报", year_in("qb1981_45", r"March (\d{4})"), MONTHS.index("March") + 1)
    has("qb81_garble", "about17!-%")
    said("如 17.5\\% 读成“17!-\\%”", F["qb81_175"][0], 17)
    has("fs_pubdate", "Publication Date: 1965")
    said("美国国民经济研究局 1965 年出版的文集的扫描本", F["fs_pubdate"][0])
    said("文中说两人的《美国货币史》正在付印，注明 1963 年，本书因此把这篇文章记作 1963 年", F["fs_press"][2],
         F["fs_press"][2])
    has("moses_ref", "Problems of Monetary Management: the U.K. Experience")
    said("古德哈特 1975 年的论文没有读", F["moses_ref"][0])
    said("普尔 1970 年的论文也没有读", F["pl_qje2"][1])
    said("按 Moses（1983）的转引", F["moses_title"][1])
    said("按普尔与 Lieberman（1972）的复述", year_in("pl1972_45", r"Activity (\d{4})\(2\)"))
    said("Rich 的表 1 在印刷页第 18 页，Gerberding 等人的表 10 在印刷页第 45 页", F["rich_t1"][0], page("rich_t1"),
         F["gwz_t10"][0], page("gwz_t10"))
    said("表 B-67 的 M1 是 12 月的日平均数", month("erp_b67_december", "December"))
    said("流通速度因此用 12 月的 M1 计算", month("erp_b67_december", "December"))
    said("联邦银行为什么在 1998 年以后不再公布目标", GWZ_YEARS[-1])
    has("rba_licence", "CC BY 4.0")
    has("rba_attrib", "Source : Reserve Bank of Australia [year]")
    said("按 CC BY 4.0 使用，来源：Reserve Bank of Australia 1983", F["rba_licence"][1], F["moses_title"][1])
    said("弗里德曼 1968 年的文章与布鲁金斯学会的三篇文章也只引短语", year_in("f1968_45", r"March (\d{4})"))
    has("hansard_copyright", "© UK Parliament")


def legacy(F, Y, Q):
    said("货币需求稳定这一条，1970 年代中期以后在美国、英国与加拿大都没有守住", F["moses_three"][0])
    has("rich_communicate", "inflation forecasts were easier to communicate to the public")
    said("1970 年代各国央行管的，正是不兑现的纸币", 1970)
    said("Moses 1983 年主张看一系列金融变量", F["moses_title"][1])
    said("劳森 1987 年按狭义货币、广义货币与汇率定利率", F["law87_date"][1])
    has("f68_known", "stated and known rate")
    said("弗里德曼 1968 年要的是一个公布出来、人所共知的增长率", year_in("f1968_45", r"March (\d{4})"))


def takeaways(F, Y, Q):
    said("美国 1979 年 10 月改为控制准备金，1982 年 10 月不再为 M1 定具体目标", F["fomc79_date"][1],
         month("fomc79_date", "October"), F["fomc82o_date"][1], month("fomc82o_date", "October"))
    said("英国 1980 年的£M3 目标一再超出，1987 年放弃", F["h80_date"][1], F["law87_date"][1])
    said("加拿大 1982 年 11 月放弃 M1 目标", F["bou_date"][1], month("bou_date", "NOVEMBER"))
    said("1970 年代中期以后美国的货币需求移动了", F["moses_three"][0])


def selfcheck(F, Y, Q):
    m = target(SC["pi"], SC["y"], SC["v"])
    pi = inflation(m, SC["y"], SC["v_fast"])
    said("能容忍的通胀是 2\\%，潜在产出增长 3\\%，流通速度每年下降 1\\%", SC["pi"], SC["y"], -SC["v"])
    said("流通速度实际每年下降 3\\%", -SC["v_fast"])
    said("货币扰动的方差是 3 时", SC["sv"])
    U = us()
    gdp, m1 = U.loc[1981, "gdp_bn"], U.loc[1981, "m1_dec_bn"]
    said("表 B-1 中 1981 年的名义 GDP 是 31313 亿美元，表 B-67 中 1981 年 12 月的 M1 是 4362 亿美元", 1981, gdp * 1e9,
         1981, month("erp_b67_december", "December"), m1 * 1e9)
    r = rich(1978)
    said("瑞士国家银行 1978 年的 M1 目标是 5\\%，实际增长 16.2\\%", 1978, r["target"], r["outcome"])
    said("$2+3-(-1)=6\\%$", SC["pi"], SC["y"], -SC["v"], m)
    said("$6+(-3)-3=0$", m, -SC["v_fast"], SC["y"], pi)
    P = POOLE
    v3 = poole_var(P["a1"], P["b1"], P["b2"], P["su"], SC["sv"])
    assert v3 > P["su"] and SC["sv"] > threshold(P["a1"], P["b1"], P["b2"], P["su"])
    said("$\\sigma^{2}_{Y,M}=(0.25+3)/2.25\\approx1.44$，大于 1", P["b2"] ** 2 * P["su"], SC["sv"],
         (P["a1"] * P["b1"] + P["b2"]) ** 2, v3, P["su"])
    said("$31313/4362\\approx7.18$", gdp * 10, m1 * 10, velocity(1981))
    said("11.2 个百分点，与 Rich 说的“超出 10 个百分点以上”相符", r["outcome"] - r["target"], F["rich_explosive"][1])


def ending(F, Y, Q):
    d, y = F["h80_date"]
    said("回到 1980 年 3 月 26 日的下院", y, month("h80_date", "March"), d)
    has("h80_us", "similar remedies", "the United States a fortnight ago")
    has("rich_floatdate", "January 1973", "float the Swiss franc")
    has("rich_float", "gained full control of the money supply")
    said("瑞士 1973 年让法郎浮动以后", F["rich_floatdate"][0])
    said("1978 年法郎涨得太猛", F["rich_80"][0])
    assert tex_text().rstrip().endswith("（本书的解读）。" + NEXT)
    assert f"\\guidequestion{{{NEXT}}}" in chapter("ch46_floating")


def figures_data() -> None:
    """What the figures and their captions assert of their data."""
    U = us()
    assert U[["v1", "v2"]].notna().all().all() and len(U) == 41
    G = [gwz(y) for y in range(1979, 1999)]
    assert all(g["lo"] <= g["hi"] for g in G)
    R = [rich(y) for y in RICH_YEARS]
    assert len(R) == 15
    P = POOLE
    s = threshold(P["a1"], P["b1"], P["b2"], P["su"])
    xs = np.linspace(0, 5, 51)
    ym = [poole_var(P["a1"], P["b1"], P["b2"], P["su"], x) for x in xs]
    assert ym[0] < P["su"] < ym[-1] and np.isclose(poole_var(P["a1"], P["b1"], P["b2"], P["su"], s), P["su"])
    print(f"ok the data of the figures: {len(U)} American years, {len(G)} Bundesbank years, {len(R)} SNB years; "
          f"Poole's lines cross at {s:g}")


# ---------------------------------------------------------------------------------------------------
# 5. The book
# the life dates: words -> (row of the birth year, index), (row of the death year, index), row of the heading, heading
LIVES = {"Geoffrey Howe，1926—2015": (("loc_howe", 0), ("loc_howe", 1), "loc_howe", "Howe, Geoffrey"),
         "Robin Leigh-Pemberton，1927—2013": (("loc_leighpemberton", 1), ("loc_leighpemberton", 3),
                                             "loc_leighpemberton_head", "Leigh-Pemberton, Robin"),
         "Milton Friedman，1912—2006": (("loc_friedman", 0), ("loc_friedman", 1), "loc_friedman", "Friedman, Milton"),
         "Anna J. Schwartz，1915—2012": (("loc_schwartz", 0), ("loc_schwartz", 1), "loc_schwartz", "Schwartz, Anna J."),
         "Irving Fisher，1867—1947": (("loc_fisher", 0), ("loc_fisher", 1), "loc_fisher", "Fisher, Irving"),
         "Paul A. Samuelson，1915—2009": (("loc_samuelson", 0), ("loc_samuelson", 1), "loc_samuelson",
                                         "Samuelson, Paul A."),
         "Franco Modigliani，1918—2003": (("loc_modigliani", 0), ("loc_modigliani_d", 0), "loc_modigliani_head",
                                         "Modigliani, Franco"),
         "Paul A. Volcker，1927—2019": (("loc_volcker_b", 0), ("loc_volcker_d", 0), "loc_volcker_head", "Volcker, Paul A."),
         "Nigel Lawson，1932—2023": (("gnd_lawson_b", 0), ("gnd_lawson_d", 0), "loc_lawson_head", "Lawson, Nigel"),
         "Gerald K. Bouey，1920—2004": (("loc_bouey", 0), ("loc_bouey", 1), "loc_bouey_head", "Bouey, Gerald K."),
         "Hyman P. Minsky，1919—1996": (("gnd_minsky_b", 0), ("gnd_minsky_d", 0), "loc_minsky_head", "Minsky, Hyman P.")}
# born only (no death date in the record): words -> (row of the birth year, index), row of the heading, heading
BORN = {"William Poole，1937 年生": (("loc_poole", 0), "loc_poole", "Poole, William"),
        "Charles Goodhart，1936 年生": (("loc_goodhart", 2), "loc_goodhart_head", "Goodhart, C. A. E.")}
# what other chapters tell: (words of this chapter, chapter where it is told, words there)
EVENTS = [("钱多则物贵，这个道理在《管子》里已经有了（\\chref{ch:qinhan}）", "ch08_qinhan",
           "两者都看到钱多则物贵；《管子》"),
          ("就是\\chref{ch:depressionus}讲过的那次收缩（\\secref{sec:depressionus-money}）", "ch28_depressionus",
           "1930 年秋天到 1933 年冬天，货币存量下降了近 30\\%"),
          ("就是\\chref{ch:depressionus}讲过的那次收缩（\\secref{sec:depressionus-money}）", "ch28_depressionus",
           "\\label{sec:depressionus-money}"),
          ("\\chref{ch:naturalrate}讲过他 1967 年 12 月的会长演说", "ch44_naturalrate", "1967 年 12 月 29 日是星期五"),
          ("他提议的数字在\\chref{ch:naturalrate}的结尾已经讲过", "ch44_naturalrate",
           "现金加全部商业银行存款每年约要增长 3\\% 到 5\\%"),
          ("\\chref{ch:naturalrate}讲过，联邦储备 1974 年想把 M1 的增长控制在 6\\% 以内", "ch44_naturalrate",
           "一是把 M1 的增长大致控制在经济顾问委员会 1974 年报告预示的 6\\% 以内"),
          ("第三个命题就是\\chref{ch:naturalrate}的长期竖线", "ch44_naturalrate", "长期的曲线是$u^{n}$处的竖线"),
          ("长期中性那一条留了下来，成了\\chref{ch:naturalrate}的长期竖线", "ch44_naturalrate",
           "长期的曲线是$u^{n}$处的竖线"),
          ("\\chref{ch:naturalrate}讲过，同年 9 月，工党的首相在党的大会上已经改了口", "ch44_naturalrate",
           "1976 年 9 月 28 日在工党大会上的话"),
          ("\\chref{ch:naturalrate}讲过，英国的失业率 1981 年是 9.6\\%，1983 年到了 11.5\\%", "ch44_naturalrate",
           "1981 年是 9.6\\%，1983 年到了 11.5\\%"),
          ("\\chref{ch:silver}的式~\\eqref{eq:silver-qty}写的是$g_P\\approx g_M+g_V-g_Y$", "ch13_silver",
           "g_P\\approx g_M+g_V-g_Y .\\label{eq:silver-qty}"),
          ("\\chref{ch:bullion}的交易方程式~\\eqref{eq:bullion-exchange}是一个恒等式", "ch19_bullion",
           "交易方程是恒等式"),
          ("货币存量还要经过式~\\eqref{eq:money-mult}的乘数（\\chref{ch:money}）", "ch04_money",
           "\\label{eq:money-mult}"),
          ("\\chref{ch:money}讲过，在准备金稀缺、不付利息的年代，乘数变得慢得多", "ch04_money",
           "在准备金稀缺、不付利息的年代，乘数变得慢得多"),
          ("2008 年以后，美联储处在地板体系，准备金有利息", "ch04_money", "2008 年以后，美联储处在地板体系，准备金有利息"),
          ("写成\\chref{ch:islm}的 IS–LM", "ch33_islm", "IS–LM"),
          ("这几年的利率、衰退与反通胀的总账，是\\chref{ch:credibility}的题目", "ch49_credibility",
           "用沃尔克反通胀（1979—1982）估算牺牲率"),
          ("它与货币目标的关系是\\chref{ch:budget}的题目", "ch50_budget", "用萨金特与华莱士（1981）说明，在财政主导下货币紧缩"),
          ("这条法则有一个近亲，就是\\chref{ch:ratex}的卢卡斯批判", "ch48_ratex", "说明卢卡斯批判（1976）"),
          ("石油冲击是\\chref{ch:oil}的题目", "ch47_oil", "用总供给冲击分析 1973 年与 1979 年的油价冲击"),
          ("汇率目标的来龙去脉在\\chref{ch:floating}", "ch46_floating", "1973 年主要货币转向浮动的过程"),
          ("\\chref{ch:depressionworld}讲过，对中国的这段经历另有不同的看法（\\secref{sec:depressionworld-silver}）",
           "ch29_depressionworld", "美国的白银政策该负多大的责任，看法并不一致"),
          ("\\chref{ch:depressionworld}讲过，对中国的这段经历另有不同的看法（\\secref{sec:depressionworld-silver}）",
           "ch29_depressionworld", "\\label{sec:depressionworld-silver}"),
          ("\\chref{ch:silver}留下了数量论的两个老问题，一是流通速度是否稳定，二是货币与物价谁先谁后", "ch13_silver",
           "价格革命还留下了数量论的两个老问题，一是流通速度是否稳定，二是货币与物价谁先谁后"),
          ("\\chref{ch:bullion}讲过，在可兑换的金本位下货币是物价的结果，在不兑现的纸币下它可以是原因", "ch19_bullion",
           "在可兑换的金本位下，货币是物价的结果；在不兑现的纸币下，它可以是原因"),
          ("取代货币目标的通胀目标制与泰勒规则，在\\chref{ch:consensus}", "ch55_consensus", "泰勒规则（1993）"),
          ("取代货币目标的通胀目标制与泰勒规则，在\\chref{ch:consensus}", "ch55_consensus", "通胀目标制")]
# the chapters this one names, and where their labels are
LATER = {"ch:budget": "ch50_budget", "ch:bullion": "ch19_bullion", "ch:consensus": "ch55_consensus",
         "ch:credibility": "ch49_credibility", "ch:depressionus": "ch28_depressionus",
         "ch:depressionworld": "ch29_depressionworld", "ch:floating": "ch46_floating", "ch:islm": "ch33_islm",
         "ch:money": "ch04_money", "ch:naturalrate": "ch44_naturalrate", "ch:oil": "ch47_oil",
         "ch:qinhan": "ch08_qinhan", "ch:ratex": "ch48_ratex", "ch:silver": "ch13_silver"}
# the chapters that point here
POINTERS = ("ch01_intro", "ch04_money", "ch08_qinhan", "ch13_silver", "ch19_bullion", "ch38_phillips",
            "ch44_naturalrate", "ch49_credibility")


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
        assert f"{F[rb][ib]:.0f} 年生" in words, (words, rb)
        assert Q[head_row].startswith(head), (head_row, Q[head_row])
        COVERED.append(words)
    # the second witnesses: the full dates of the LoC and the GND, the GND's heading for Lawson
    assert F["loc_howe_b"][0] == F["loc_howe"][0] and F["loc_howe_d"][0] == F["loc_howe"][1]
    has("loc_leighpemberton", "b. 5 Jan. 1927", "d. 24 Nov. 2013")
    assert F["gnd_volcker_b"] == F["loc_volcker_b"] and F["gnd_volcker_d"] == F["loc_volcker_d"]
    assert F["gnd_minsky_b"] == [1900 + F["loc_minsky"][2], F["loc_minsky"][0], F["loc_minsky"][1]]
    assert Q["gnd_lawson_head"] == Q["loc_lawson_head"] == "Lawson, Nigel"
    has("loc_bouey", "Bouey, Gerald K., 1920-2004")
    has("loc_poole", "1937 June 19-")
    has("loc_goodhart", "b. 10-23-1936")
    for here, ch, there_ in EVENTS:
        assert here in t, here
        assert there_ in chapter(ch), (ch, there_)
    named = set(re.findall(r"\\chref\{(ch:[^}]+)\}", t)) | set(re.findall(r"\\nameref\{(ch:[^}]+)\}", t))
    assert named == set(LATER), sorted(named ^ set(LATER))
    for label, ch in LATER.items():
        assert f"\\label{{{label}}}" in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (label, ch)
    for ch in POINTERS:
        assert re.search(r"\\(?:chref|ref|nameref)\{ch:monetarism\}", chapter(ch)), ch
    print(f"ok {len(LIVES) + len(BORN)} life dates, {len(EVENTS)} statements of other chapters, "
          f"{len(LATER)} other chapters named")


# the bibliography item of each source of the snapshots (the authority records: loc45 and gnd45; the AEA's terms are
# named in the block's comment, beside the shared item friedman1968)
ITEM_OF = {"bocterms_45": "bouey1982a", "boelegal_45": "boe1981", "bouey1982d_45": "bouey1982b",
           "bouey1982n_45": "bouey1982a", "brookingsterms_45": "poolelieberman1972", "erpb1_45": "erp2000b",
           "erpb67_45": "erp2000b", "f1968_45": "friedman1968", "fomc1979_45": "fomc1979",
           "fomc1982f_45": "fomc1982a", "fomc1982o_45": "fomc1982b", "fs1963_45": "friedmanschwartz1963",
           "fs1963img_45": "friedmanschwartz1963", "gf1976_45": "goldfeld1976", "gwz2004_45": "gerberding2004",
           "hansard1980_45": "hansard1980", "hansard1980r_45": "hansard1980", "hansard1986_45": "hansard1986",
           "hansard1986b_45": "hansard1986", "hansard1987_45": "hansard1987", "hansard1987b_45": "hansard1987",
           "lp1986_45": "leighpemberton1986", "moses1983_45": "moses1983", "mp1975_45": "modigliani1975",
           "pl1972_45": "poolelieberman1972", "pl1972img_45": "poolelieberman1972", "qb1981_45": "boe1981",
           "qb1981img_45": "boe1981", "rbacopyright_45": "moses1983", "rich2003_45": "rich2003"}
# the items shared with Chapter 44, outside the block: Friedman (1968) and Modigliani and Papademos (1975); the copies
# read for Chapter 45 have the same hashes, and the block's comment names the pages of Chapter 45
SHARED = {"friedman1968", "modigliani1975"}
# the sources of each item whose pages it names
PAGES = {"friedmanschwartz1963": ("fs1963_45", "fs1963img_45"), "poolelieberman1972": ("pl1972_45", "pl1972img_45"),
         "goldfeld1976": ("gf1976_45",), "boe1981": ("qb1981_45", "qb1981img_45"),
         "leighpemberton1986": ("lp1986_45",), "bouey1982a": ("bouey1982n_45",), "bouey1982b": ("bouey1982d_45",),
         "moses1983": ("moses1983_45",), "rich2003": ("rich2003_45",), "gerberding2004": ("gwz2004_45",)}
PDF_ONLY = {"fomc1979": ("fomc1979_45",), "fomc1982a": ("fomc1982f_45",), "fomc1982b": ("fomc1982o_45",)}
COLUMNS = {"hansard1980": ("hansard1980_45", "hansard1980r_45"), "hansard1986": ("hansard1986_45", "hansard1986b_45"),
           "hansard1987": ("hansard1987_45", "hansard1987b_45")}


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
    """The printed pages of the rows of these sources (their juan columns begin 'p. N')."""
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


def cols(srcs) -> str:
    """The columns of Hansard of the rows of these sources ('c. 1442')."""
    return runs(int(m.group(1)) for r in _rows().itertuples() if r.file in srcs
                for m in [re.match(r"c\. (\d+)$", r.juan)] if m)


def block() -> tuple[str, dict[str, str], dict[str, str]]:
    """The bibliography block of Chapter 45, its items and all items of the bibliography."""
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    start = bib.index("% ---- 第 45 章")
    following = re.search(r"^% ---- 第 \d+ 章", bib[start + 1:], re.MULTILINE)
    end = start + 1 + following.start() if following else bib.index("\\end{thebibliography}")
    text = bib[start:end]
    assert bib.index("% ---- 第 44 章") < start
    items = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", text)}
    allitems = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", bib)}
    return text, items, allitems


def witnesses(F, Q):
    """The licences and the bibliography block of the chapter."""
    m = meta()
    lic = m["license"]
    lic_rows = ("aea_terms", "fs_cover", "brookings_terms", "bundesbank_repro", "ecb_copy", "ecb_repro", "rba_licence",
                "rba_attrib", "boe_legal_copyright", "boe_legal_permission", "boc_permit", "boc_attrib",
                "hansard_copyright")
    for rid in lic_rows:
        assert re.search(r"\brows? [^)]*\b" + rid + r"\b", lic), rid
        assert words_of(rid) in lic, rid
    for words in ("17 U.S.C. § 105", "no photographs are used", "CC0 1.0", "Open Parliament Licence v3.0",
                  "(row moses_rule) is third-party material"):
        assert words in lic, words
    # the bibliography block of the chapter
    text, items, allitems = block()
    assert FETCH in text and "monetarism_facts" in text and "monetarism_us_1959_1999" in text
    assert f"共 {len(items)} 条" in text
    unescape = lambda s: re.sub(r"\\([$%&_#~])", r"\1", s).replace("--", "-")     # noqa: E731 - as LaTeX prints it
    for rid, keys in (("brookings_terms", ("poolelieberman1972", "goldfeld1976")),
                      ("bundesbank_repro", ("gerberding2004",)), ("ecb_copy", ("rich2003",)),
                      ("ecb_repro", ("rich2003",)), ("rba_licence", ("moses1983",)), ("rba_attrib", ("moses1983",)),
                      ("boe_legal_copyright", ("boe1981", "leighpemberton1986")),
                      ("boe_legal_permission", ("boe1981", "leighpemberton1986")),
                      ("boc_permit", ("bouey1982a", "bouey1982b")), ("boc_attrib", ("bouey1982a", "bouey1982b")),
                      ("fs_cover", ("friedmanschwartz1963",)),
                      ("hansard_copyright", ("hansard1980", "hansard1986", "hansard1987"))):
        for key in keys:
            assert words_of(rid) in unescape(items[key]), (rid, key)
    for key in ("hansard1980", "hansard1986", "hansard1987"):
        assert "Contains Parliamentary information licensed under the Open Parliament Licence v3.0" in items[key]
    for key in ("fomc1979", "fomc1982a", "fomc1982b", "erp2000b"):
        assert "公有领域" in items[key] and "17 U.S.C. § 105" in items[key], key
    assert "公共数据" in items["loc45"] and "CC0" in items["gnd45"]
    assert "Source: Reserve Bank of Australia 1983" in items["moses1983"]
    assert "来源：加拿大银行" in items["bouey1982a"] and "来源：加拿大银行" in items["bouey1982b"]
    # every source is named by its URL and SHA-256 (the authority records by their URLs)
    for key, s in documents().items():
        if key == "aeaterms_45":
            assert s["url"] in text and s["sha256"] in text, key                  # the block's comment
            continue
        item = "loc45" if key.startswith("loc_") else "gnd45" if key.startswith("gnd_") else ITEM_OF[key]
        assert unescape(s["url"]) in unescape(allitems[item]), key
        if item in SHARED:
            assert s["sha256"] in allitems[item], key                             # the same copy as Chapter 44's
        elif not key.startswith(("loc_", "gnd_")):
            assert s["sha256"] in items[item], key
        if key.startswith("gnd_"):
            assert re.search(r"gnd/(\d+)\.json", s["url"]).group(1) in items["gnd45"], key
    # the pages of each work, as the snapshot's rows have them
    for key, srcs in PAGES.items():
        assert f"第 {printed(srcs)} 页" in items[key] or f"与第 {printed(srcs)} 页" in items[key], (key, printed(srcs))
        assert f"PDF 第 {pdf(srcs)} 页" in items[key], (key, pdf(srcs))
    for key, srcs in PDF_ONLY.items():
        assert f"PDF 第 {pdf(srcs)} 页" in items[key], (key, pdf(srcs))
    for key, srcs in COLUMNS.items():
        assert f"第 {cols(srcs)} 栏" in items[key], (key, cols(srcs))
    for key, src in (("friedman1968", "f1968_45"), ("modigliani1975", "mp1975_45")):
        assert f"{key} 的第 {printed((src,))} 页（PDF 第 {pdf((src,))} 页）" in text, key
    assert "第 306—307 页" in items["erp2000b"] and "第 385 页" in items["erp2000b"]
    assert page("erp_b1_title") == 306 and page("erp_b67_title") == 385
    for words, (_, _, head_row, _) in LIVES.items():
        if head_row.startswith("loc_"):
            assert re.sub(r"(\d)-(\d)", r"\1--\2", Q[head_row]) in items["loc45"], head_row
    for words, (_, head_row, _) in BORN.items():
        assert Q[head_row].split(",")[0] in items["loc45"], head_row
    # the titles of the works as the documents print them
    for rid, key, words in (("fs_title", "friedmanschwartz1963", "MONEY AND BUSINESS CYCLES"),
                            ("gf_title", "goldfeld1976", "The Case of the Missing Money"),
                            ("lp86_title", "leighpemberton1986", "Financial change and broad money"),
                            ("qb81_title", "boe1981", "Economic commentary"),
                            ("gwz_title", "gerberding2004", "How the Bundesbank really conducted monetary policy"),
                            ("rich_title", "rich2003", "SWISS MONETARY TARGETING 1974-1996"),
                            ("moses_title", "moses1983", "Research Discussion Paper 8301"),
                            ("erp_b1_title", "erp2000b", "Gross domestic product"),
                            ("erp_b67_title", "erp2000b", "Money stock and debt measures"),
                            ("fomc79_date", "fomc1979", "Meeting held on October 6, 1979"),
                            ("fomc82f_date", "fomc1982a", "Meeting held on February 1-2, 1982"),
                            ("fomc82o_date", "fomc1982b", "Meeting Held on October 5, 1982"),
                            ("h80_date", "hansard1980", "HC Deb 26 March 1980"),
                            ("law86_date", "hansard1986", "HC Deb 18 March 1986"),
                            ("law87_date", "hansard1987", "HC Deb 17 March 1987"),
                            ("bou_date", "bouey1982a", "NOVEMBER 29, 1982"),
                            ("boud_date", "bouey1982b", "December 8, 1982")):
        has(rid, words)
        assert words.lower() in unescape(items[key]).lower(), (rid, key)
    keys = set(allitems)
    cited = {k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", tex_text()) for k in c.split(",")}
    assert cited <= keys, sorted(cited - keys)
    assert set(items) == cited - SHARED and SHARED <= cited, sorted(set(items) ^ (cited - SHARED))
    print(f"ok {len(cited)} works cited, {len(items)} in the bibliography block of Chapter 45")


def documents() -> dict[str, dict]:
    """Every document of the two snapshots of data/fetch/monetarism45.py."""
    out = dict(meta()["sources"])
    for key, src in load_snapshot("monetarism_us_1959_1999")[1]["documents"].items():
        assert key not in out or out[key]["sha256"] == src["sha256"], key
        out[key] = src
    return out


def counts() -> None:
    """The editor's limits: “不能” at most about a dozen; the forbidden words; who decided and who paid stated; the three
    debates left open; the boxes."""
    t = tex_text()
    main_ = re.sub(r"\\begin\{deeper\}\[史料说明\].*?\\end\{deeper\}", "", t, flags=re.DOTALL)
    n = t.count("不能")
    print(f"ok “不能” {n} times")
    assert n <= 12, n
    for words in ("本书没有找到", "没能取得", "没有取得", "没有读到", "没有读"):
        assert words not in main_, words                                          # only in the 史料说明
    narrative = re.sub(r"“[^”]*”", "", t)
    for bad in ("这一节回答", "不是因为", "而是", "详见", "\\textsc", "\\underline", "\\clearpage", "值得注意", "如前所述"):
        assert bad not in narrative, bad
    assert not re.search(r"(?<![意看])见\\(?:chref|secref|figref|tabref|exref|eqref)", t)
    # who decided and who paid
    for words in ("1979 年的转向是谁定的？", "投赞成票的是沃尔克等 12 人", "英国的目标是谁定的？", "演说是财政大臣豪作的",
                  "他说是与英格兰银行行长商定的", "财政大臣劳森", "他宣布，加拿大银行不再为 M1 设目标区间",
                  "两家央行的目标由谁定？", "联邦银行的货币政策由中央银行理事会决定", "瑞士国家银行的决策由三人组成的理事会作出",
                  "代价落在谁身上？委员会", "代价落在谁身上？豪", "制造业减少了 70 多万个工作", "住房抵押贷款利率",
                  "高失业、大量闲置的设备、低利润与许多企业倒闭", "出口部门、联邦政府与公众都向央行施加巨大的压力"):
        assert words in main_, words
    assert main_.count("代价落在谁身上？") == 2
    # documents are not the subjects of sentences: the author is named
    for bad in ("报告说", "演讲说", "演说说", "论文说", "书里说", "表说", "网页说"):
        assert bad not in main_, bad
    # at most one source frame (按……的说法、转述……) in a sentence
    frame = re.compile(r"按[^，。；“”]{0,40}?的(?:说法|转述|解释|估计|叙述|描述|判断|概括|统计|数|记录|计算|整理)")
    for s in re.split(r"(?<=[。？！])|\n", re.sub(r"“[^”]*”", "“”", main_)):
        assert len(frame.findall(s)) <= 1, s
    # the three debates are left open
    part = main_[main_.index("\\section{争论}"):main_.index("\\section{今天还剩什么}")]
    debates = part.split("\\subsubsection{")[1:]
    assert len(debates) == 3
    for d in debates:
        assert d.rstrip().endswith("至今没有定论。"), d[-80:]
    # the inferences are marked
    for words, k in (("本书的解读", 12), ("本书的计算", 6), ("本书的概括", 5), ("本书的推导", 5), ("本书的核对", 3)):
        assert main_.count(words) >= k, (words, main_.count(words))
    # sentences: one semicolon at most
    prose = re.sub(r"\\datasource\{[^\n]*", "", main_)
    for s in re.split(r"(?<=[。？！])|\n", re.sub(r"“[^”]*”", "“”", prose)):
        assert s.count("；") <= 1, s
    # the boxes the editor asks for
    assert t.count("\\begin{compare}") == 1 and t.count("\\begin{case}") == 1 and t.count("\\begin{pitfall}") == 1
    assert t.count("\\begin{deeper}[史料说明]") == 1 and t.count("\\begin{keyeq}") == 2
    assert t.count("\\begin{example}") == 2 and t.count("\\fig{") == 3 and t.count("\\begin{table}") == 1
    assert t.count(GUIDE) == 2
    # the neighbours' topics: a clause or a sentence each
    for label in ("ch:floating", "ch:oil", "ch:ratex", "ch:credibility", "ch:budget", "ch:consensus",
                  "ch:depressionworld", "ch:depressionus", "ch:qinhan", "ch:islm", "ch:silver", "ch:bullion"):
        assert t.count(f"\\chref{{{label}}}") <= 2, label
    # the lines the brief rules out
    for bad in ("M1 abandoned us", "抛弃了我们", "when a measure becomes a target", "一项指标一旦成为目标"):
        assert bad not in t, bad


def main() -> None:
    df = _rows()
    F, Y, Q = facts(), years(), quotes()
    check_readings(df)
    check_text(df)
    for part in (guide, opening, world, theory, poole, america, britain, goodhart, test, debate, deeper, legacy,
                 takeaways, selfcheck, ending):
        part(F, Y, Q)
    models()
    arithmetic()
    figures_data()
    book(F, Q)
    witnesses(F, Q)
    counts()
    coverage()
    anchors(str(TEX), set(df["id"]), script=Path(__file__))


if __name__ == "__main__":
    main()
