"""Chapter 44 (自然率与附加预期的菲利普斯曲线): every number and every quotation in zh/ch44_naturalrate.tex.

    python3 checks/check_ch44.py

Inputs:
  naturalrate_facts             quotations of the chapter's sources with their page: Friedman's presidential address of
                                29 December 1967 (AER 58(1), March 1968, the AEA's scan) and his Nobel lecture of 13
                                December 1976; Phelps's Nobel lecture of 8 December 2006; Modigliani and Papademos (BPEA
                                1975:1) with its erratum slip; Gordon and King (BPEA 1982:1, with the discussion); tables
                                B-40 and B-62 of the Economic Report of the President of 2000; the Economic Planning
                                Agency's annual economic report of 1974 (the Cabinet Office's online edition); the
                                e-Stat listings and terms, the Cabinet Office's terms and the Public Data License 1.0;
                                the terms of the AEA and of Brookings; the Nobel pages; the authority records of the
                                Library of Congress and the GND. data/fetch/verify_web_quotes.py checks the quotations
                                against the documents; data/fetch/naturalrate44.py fetches them
  naturalrate_us_1959_1985      the civilian unemployment rate and the change of the CPI-U (B-40, B-62)
  naturalrate_japan_1953_1986   the unemployment rate of the Labour Force Survey and the change of the CPI (e-Stat)
  boe_millennium_uk_1954_1986   British unemployment and CPI inflation (Bank of England, tables A50 and A47;
                                data/fetch/boe_millennium_gb44.py)
  zh/ch25, ch32, ch33, ch38     the statements of earlier chapters that this chapter repeats (EVENTS); the stubs of
                                Chapters 45, 47, 48, 49, 54, 55 and 57 for what is handed on (LATER)

This script

1. reads the numbers of every row from its quotation by the rules of READINGS and compares them with the value
   column; the misreadings of the text layers are listed in MISPRINTS;
2. finds every “…” of the text among the renderings of TRANSLATIONS, and the words of the source each one renders
   (KEYWORDS) in the rows; the quotations stay short;
3. checks each number of the text with said(): the phrase is in the text and each number is the value of a row, a
   teaching input, or arithmetic on them (the curves of eq:naturalrate-curve and eq:naturalrate-accel, the sum of
   eq:naturalrate-sacrifice, Okun's coefficient of eq:phillips-okun, the statistics of the American series); every
   Arabic number of the text must lie in a phrase said() read (coverage());
4. checks the key equations as printed, the claims made of them on random numbers, the data of the figures
   (figsrc/fig_ch44.py imports us(), uk(), jp() and paths() from here), the life dates against the authority
   records, what other chapters tell, the licences and the bibliography block of Chapter 44;
5. lists the rows no "% 据:" anchor of the text names (common.anchors).

Set CH44_TEX to a scratch copy of the chapter to run the checks on it (mutation tests).
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

TEX = Path(os.environ.get("CH44_TEX", ROOT / "zh" / "ch44_naturalrate.tex"))   # a scratch copy for mutation tests
GUIDE = "菲利普斯“菜单”为什么会漂移？"
PREV = GUIDE                                        # Chapter 43's NEXT
NEXT = "控制货币数量就能控制通胀吗？"                    # Chapter 45's question (its stub)
FETCH = "data/fetch/naturalrate44.py"
UK_FETCH = "data/fetch/boe_millennium_gb44.py"


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
    df, m = load_snapshot("naturalrate_facts", dtype=str, keep_default_na=False)
    assert 44 in m["used_in"] and m["fetch"] == FETCH
    assert df["id"].is_unique
    return df


@lru_cache(maxsize=None)
def meta() -> dict:
    return load_snapshot("naturalrate_facts")[1]


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
    """The first printed page number of a row's juan column: 'p. 155 (PDF p. 159)' -> 155."""
    return int(re.search(r"pp?\. (\d+)", column("juan")[rid]).group(1))


def chapter(name: str) -> str:
    """Another chapter's text without its comment lines."""
    t = (ROOT / "zh" / f"{name}.tex").read_text(encoding="utf-8")
    return "\n".join(l for l in t.splitlines() if not l.lstrip().startswith("%"))


def year_in(key: str, pattern: str) -> int:
    """A year the version of a source names: the issue of the Brookings Papers, the edition of the ERP."""
    return int(re.search(pattern, meta()["sources"][key]["version"]).group(1))


@lru_cache(maxsize=None)
def us() -> pd.DataFrame:
    """B-40 and B-62 of the ERP 2000, 1959-1985: unemployment (all civilian workers) and the CPI-U (Dec. to Dec. and
    year to year), per cent. figsrc/fig_ch44.py draws 1960-1985."""
    df, m = load_snapshot("naturalrate_us_1959_1985")
    assert 44 in m["used_in"] and m["fetch"] == FETCH and set(m["documents"]) == {"erpb40_44", "erpb62_44"}
    assert "17 U.S.C. § 105" in m["license"]
    df = df.set_index("year")
    assert list(df.index) == list(range(1959, 1986))
    return df


@lru_cache(maxsize=None)
def uk() -> pd.DataFrame:
    """Tables A47 and A50 of the Bank of England's millennium workbook, 1954-1986: CPI inflation and unemployment
    as a per cent of employment plus unemployment."""
    df, m = load_snapshot("boe_millennium_uk_1954_1986")
    assert 44 in m["used_in"] and m["fetch"] == UK_FETCH
    df = df.set_index("year")
    assert list(df.index) == list(range(1954, 1987))
    rate = 100 * df["unemployed_000s"] / (df["unemployed_000s"] + df["employment_000s"])
    assert (abs(rate - df["unemp_pct"]) < 1e-4).all()
    return df


@lru_cache(maxsize=None)
def jp() -> pd.DataFrame:
    """The Labour Force Survey (with Okinawa from 1973; without it to 1973) and the CPI less imputed rent (from 1948)
    and all items (from 1971), change over the year, per cent."""
    df, m = load_snapshot("naturalrate_japan_1953_1986")
    assert 44 in m["used_in"] and m["fetch"] == FETCH
    assert set(m["documents"]) == {"estatlt02_44", "estatcpixr44", "estatcpizny44"}
    df = df.set_index("year")
    assert list(df.index) == list(range(1953, 1987))
    return df


# ---------------------------------------------------------------------------------------------------
# 1. Readings of the numbers (the same rules wrote the value column when the snapshot was built)
SMALL = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10}


def cardinal(s: str) -> float:
    """An English cardinal: 'two', 'nine'."""
    return float(sum(SMALL.get(w, 0) for w in s.lower().replace("-", " ").split()))


def figure(s: str) -> float:
    """'1,000', '30.5', '.28', '-0.15' and full-width digits."""
    return float(unicodedata.normalize("NFKC", s).replace(",", "").replace("−", "-"))


ZH_DIGITS = {"〇": 0, "零": 0, "一": 1, "两": 2, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
ZH_UNITS = {"十": 10, "百": 100, "千": 1000, "万": 10 ** 4, "亿": 10 ** 8}


def zh(s: str) -> float:
    """A Chinese numeral: '九', '十六', '二十', '四成', '四分之一'."""
    if "分之" in s:
        b, a = s.split("分之")
        return zh(a) / zh(b)
    if s.endswith("成"):
        return zh(s[:-1]) / 10
    total, part = 0, 0
    for ch in s:
        if ch in ZH_DIGITS:
            part = ZH_DIGITS[ch]
        else:
            total += max(part, 1) * ZH_UNITS[ch]
            part = 0
    return float(total + part)


def fraction(s: str) -> float:
    """The Brookings scan's '51/2' and '53/4' for 5 1/2 and 5 3/4."""
    whole, num, den = s[:-3], s[-3], s[-1]
    return int(whole) + int(num) / int(den)


def dotted(s: str) -> float:
    """The web edition's '7・4' for 7.4."""
    return float(s.replace("・", "."))


# a figure with its sign: a minus that follows no letter, digit or bracket
FIGURES = re.compile(r"((?<![\w)])[-−])?(\d[\d,]*(?:\.\d+)?|\.\d+)")
HOW = {"num": figure, "frac": fraction, "dot": dotted}
# id -> [(phrase, how)], in order. A phrase 'context|word' is searched as a whole and read from `word`. Rows not
# listed are read with all the figures of the quotation (NFKC), with their signs.
READINGS: dict[str, list[tuple[str, str]]] = {
    "mp_55": [("over |51/2", "frac")],
    "mp_admin": [("for |1974", "num"), ("of |1", "num"), ("end of |1973", "num"), ("end of |1974", "num"),
                 ("from |4.9", "num"), ("around |53/4", "frac"), ("at |7", "num")],
    "wp_capacity": [("伸びは|40", "num"), ("前半の|12.1", "num"), ("後半には|7・4", "dot")],
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
    text = unicodedata.normalize("NFKC", text)
    return [(-1 if sign else 1) * figure(n.rstrip(",")) for sign, n in FIGURES.findall(text)]


# the misreadings of the text layers and the misprints, each printed in the quotation and named in the snapshot's
# notes with its row: (row, as printed in the quotation, the words of the notes that name it)
MISPRINTS = [("f68_accelerating", "onalyby", "'onalyby' for 'only by'"),
             ("f68_scan", "onalyby", "'onalyby' for 'only by'"),
             ("f68_accelerating", "acceleratin(ginflation", "'acceleratin(ginflation' for 'accelerating inflation'"),
             ("f68_wicksell", "Tlhanks", "'Tlhanks' for 'Thanks'"),
             ("f68_inflation2", "mnakethe", "'mnakethe' for 'make the'"),
             ("f68_minimum", "WalshHealy", "'WalshHealy' for 'Walsh-Healey'"),
             ("f68_peg_nominal", "motneyby", "'motneyby' for 'money by'"),
             ("f68_topic", "instrument-monetary", "'instrument-monetary' for 'instrument—monetary'"),
             ("f68_issue", "VolumeLVIII", "'VolumeLVIII' for 'Volume LVIII'"),
             ("mp_m1target", "Ml", "'Ml' for 'M1'"),
             ("mp_revised", "Ml", "'Ml' for 'M1'"),
             ("gk_control", "MI", "'MI' for 'M1'"),
             ("mp_55", "51/2", "'51/2' for '5 1/2'"),
             ("mp_admin", "53/4", "'53/4' for '5 3/4'"),
             ("mp_title", "Targets for in the Monetary Policy Coming Year",
              "'Targets for in the Monetary Policy Coming Year'"),
             ("gk_copyright", "C)Brookinigs", "'C)Brookinigs' for '© Brookings'"),
             ("f76_workers", "Roth they", "'Roth they' for 'Both they'"),
             ("f76_error", "seriousIy", "'seriousIy' for 'seriously'"),
             ("f76_t1head", "Unemployement", "'Unemployement' as printed in Friedman's Table 1"),
             ("wp_354", "基づものく", "'基づものく' as printed for '基づくもの'"),
             ("wp_capacity", "7・4", "'7・4' as printed for '7.4'")]


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
    # the erratum slip: its own row and an unnumbered page between printed pp. 148 and 149
    has("mp_erratum", "Figure 1 on page 148", "Change in the inflation rate")
    assert column("juan")["mp_erratum"].startswith("erratum, unnumbered (PDF p. 9)")
    assert page("mp_1956") + 1 == 148 and page("mp_five") == 149


N_QUOTED = 151


# ---------------------------------------------------------------------------------------------------
# 2. The quotations of the text: each “…” is a rendering of words of rows
TRANSLATIONS = {
    "充分就业": ("f76_rise",),
    "滞胀": ("f76_stagflation",),
    "有序市场": ("mp_orderly",),
    "自然失业率": ("f68_natural", "f76_un", "f76_un2"),
    "自然": ("f68_immutable", "f68_reason_natural"),
    "暂时": ("f68_howlong",),
    "正常": ("f76_normal", "f76_groups"),
    "不引起通胀的失业率": ("mp_niru",),
    "极小": ("wp_wages",),
    "通胀心理": ("wp_psychology",),
    "两种不同的现象": ("ph_distinct",),
    "基づものく": ("wp_354",),
    "自然利率": ("f76_wicksell",),
}
# the words of the source each rendering renders, in the quotation
KEYWORDS = {
    "f76_rise": ["“full employment”"],
    "f76_stagflation": ["“stagflation”"],
    "mp_orderly": ['"orderlymarkets"'],
    "f68_natural": ['The "natural rate of unemployment,"'],
    "f76_un": ["“natural rate"],
    "f76_un2": ["of unemployment”"],
    "f68_immutable": ['"natural"rate of unemployment', "immutable"],
    "f68_reason_natural": ['the term "natural"'],
    "f68_howlong": ['"temporary"'],
    "f76_normal": ["“normal” price level"],
    "f76_groups": ["“normal” price level"],
    "mp_niru": ["noninflationary rate of unemployment (NIRU)"],
    "wp_wages": ["きわめて小さかつた"],
    "wp_psychology": ["インフレ心理"],
    "ph_distinct": ["two distinct phenomena"],
    "wp_354": ["基づものく"],
    "f76_wicksell": ["“natural rate of interest”"],
}
OWN = {"基づものく"}                                  # quoted in the source's own words (a misprint, 史料说明)


def tex_text() -> str:
    return "\n".join(l for l in TEX.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("%"))


def text_quotations() -> list[str]:
    """The “…” of the text; the closing question is Chapter 45's and the chapter's own question is in the guide and at
    the end of the opening (both checked by guide() and opening())."""
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 45's question"
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
                assert q in words_of(rid), (q, rid)                               # the source's own words
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
# sub- and superscripts of the math, the numbers of the parts of an example and the names M1 and M2
MASKS = [re.compile(r"\\begin\{keyeq\}.*?\\end\{keyeq\}", re.DOTALL),
         re.compile(r"\\(?:label|cite|chref|secref|figref|tabref|exref|eqref|ref|nameref|url|fig)\{[^}]*\}"),
         re.compile(r"_\{[^}]*\}|_\d"),
         re.compile(r"\^\{\d+\}"),
         re.compile(r"（\d）"),
         re.compile(r"\bM[12]\b"),
         re.compile(r"\{(?:fig|tab):[^}]*\}|\\multicolumn\{\d+\}"),             # the label of a figure, column spans
         re.compile(r"\\begin\{tabularx\}\{\\linewidth\}\{[^\n]*")]                # the column widths of the table
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


MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]


def month(rid: str, name: str) -> int:
    """The month a row prints by its English name (in capitals on the cover of the AER)."""
    has(rid, name)
    return [m.lower() for m in MONTHS].index(name.lower()) + 1


def showa(n: float) -> int:
    """昭和 n 年 (and the fiscal year that begins in it) -> the Western year."""
    return 1925 + int(n)


def b40(year: int) -> dict[str, float]:
    """The row of table B-40 for a year, by column. The columns 'Black' (from 1972) and 'Women who maintain families'
    (from 1960) are dots in the earlier years."""
    v = facts()[f"b40_{year}"]
    assert v[0] == year
    cols = ["all", "males", "males1619", "males20", "females", "females1619", "females20", "youth", "white",
            "blackother", "black", "wage", "married", "families"]
    if len(v) == 14:
        cols.remove("black")
    elif len(v) == 13:
        cols.remove("black")
        cols.remove("families")
    assert len(v) == len(cols) + 1, (year, v)
    out = dict(zip(cols, v[1:]))
    assert out["all"] == us().loc[year, "unemp_pct"]                             # the series is the same table
    return out


def b62(year: int) -> dict[str, float]:
    """The row of table B-62 for a year: all items (CPI-U), December to December and year to year."""
    v = facts()[f"b62_{year}"]
    assert v[0] == year and len(v) == 15
    assert (v[1], v[2]) == (us().loc[year, "cpi_dec_dec_pct"], us().loc[year, "cpi_year_pct"])
    return dict(dec=v[1], year=v[2])


# ---------------------------------------------------------------------------------------------------
# The teaching models (the inputs the text calls 教学用的假设)
MODEL = dict(alpha=0.5, un=6.0, pi0=2.0, u=3.0, after=4, sc_u=4.0)          # ex:naturalrate-accel, self-check 1
DIS = dict(start=10.0, end=4.0, slow=8.0, fast=12.0, sc_u=9.0)              # ex:naturalrate-disinflation, self-check 2
SC = dict(ratio=5.0, u=8.0)                                                 # self-checks 3 and 4

EQ_CURVE = r"\pi_t=\pi^{e}_t-\alpha\,(u_t-u^{n}) .\label{eq:naturalrate-curve}"
EQ_ACCEL = r"\pi_t-\pi_{t-1}=-\alpha\,(u_t-u^{n}) .\label{eq:naturalrate-accel}"
EQ_SACRIFICE = r"\sum_{t=1}^{T}(u_t-u^{n})=\frac{\pi_0-\pi_T}{\alpha} .\label{eq:naturalrate-sacrifice}"


def curve(pi_e: float, u: float, un: float, alpha: float) -> float:
    """eq:naturalrate-curve."""
    return pi_e - alpha * (u - un)


def accelerate(pi0: float, us_: list[float], un: float, alpha: float) -> list[float]:
    """eq:naturalrate-accel: adaptive expectations, pi^e_t = pi_{t-1}; the inflation of each year of the path us_."""
    out, p = [], pi0
    for u in us_:
        p = curve(p, u, un, alpha)
        out.append(p)
    return out


def sacrifice(pi0: float, piT: float, alpha: float) -> float:
    """eq:naturalrate-sacrifice: the cumulative unemployment above the natural rate, point-years."""
    return (pi0 - piT) / alpha


def okun() -> float:
    """Okun's coefficient of eq:phillips-okun, P = A[1 + 0.032 (U - 4)]: 3.2 per cent of output a point."""
    one, c, four = there("ch38_phillips", "P=A\\,[1+0.032\\,(U-4)]")
    assert (one, four) == (1, 4)
    return 100 * c


def disinflation(u: float) -> list[float]:
    """The inflation of each year of ex:naturalrate-disinflation, holding unemployment at u until it reaches the end."""
    a, un = MODEL["alpha"], MODEL["un"]
    n = sacrifice(DIS["start"], DIS["end"], a) / (u - un)
    assert n == int(n)
    return accelerate(DIS["start"], [u] * int(n), un, a)


def paths(after: int = 3) -> dict[str, pd.DataFrame]:
    """Fig. naturalrate_sim: the slow and fast paths of ex:naturalrate-disinflation, from year 0 to `after` years
    after the slower one ends: unemployment, inflation and expected inflation (last year's)."""
    a, un = MODEL["alpha"], MODEL["un"]
    T = len(disinflation(DIS["slow"])) + after
    out = {}
    for name in ("slow", "fast"):
        k = len(disinflation(DIS[name]))
        u = [un] + [DIS[name]] * k + [un] * (T - k)
        pi = [DIS["start"]] + accelerate(DIS["start"], u[1:], un, a)
        out[name] = pd.DataFrame(dict(year=range(T + 1), u=u, pi=pi, pi_e=[DIS["start"]] + pi[:-1]))
    return out


@lru_cache(maxsize=None)
def stats() -> dict:
    """The statistics of the American series the text quotes (本书的计算): correlations and means of the two periods,
    the regressions of the change of inflation on unemployment."""
    s = us()
    u, p = s["unemp_pct"], s["cpi_year_pct"]
    d = p.diff()
    out = {}
    for a, b in ((1960, 1969), (1970, 1985)):
        out[(a, b)] = dict(corr=float(np.corrcoef(u.loc[a:b], p.loc[a:b])[0, 1]), u=float(u.loc[a:b].mean()),
                           p=float(p.loc[a:b].mean()), n=b - a + 1)
    for a, b in ((1960, 1985), (1960, 1969), (1970, 1985)):
        slope, const = np.polyfit(u.loc[a:b], d.loc[a:b], 1)
        out[("reg", a, b)] = dict(const=float(const), slope=float(slope), un=float(-const / slope))
    out["u"], out["d"] = u.loc[1960:1985], d.loc[1960:1985]
    return out


def models() -> None:
    t = TEX.read_text(encoding="utf-8")
    assert EQ_CURVE in t and EQ_ACCEL in t and EQ_SACRIFICE in t
    assert "\\label{eq:phillips-okun}" in chapter("ch38_phillips")
    rng = np.random.default_rng(44)
    for _ in range(300):
        a, un, pe, u, x = rng.uniform(0.1, 2), rng.uniform(2, 10), rng.uniform(-5, 20), rng.uniform(0, 15), \
            rng.uniform(-5, 5)
        # eq:naturalrate-curve: a higher expectation moves the whole curve up by the same amount
        assert np.isclose(curve(pe + x, u, un, a) - curve(pe, u, un, a), x)
        # lower unemployment, higher inflation on a given curve; at u = u^n inflation equals the expectation
        assert curve(pe, u - 1, un, a) > curve(pe, u, un, a) and np.isclose(curve(pe, un, un, a), pe)
        # adaptive expectations give eq:naturalrate-accel
        assert np.isclose(accelerate(pe, [u], un, a)[0] - pe, -a * (u - un))
    for _ in range(300):
        # eq:naturalrate-sacrifice: on any path the cumulative excess unemployment is (pi_0 - pi_T)/alpha
        a, un, p0 = rng.uniform(0.1, 2), rng.uniform(2, 10), rng.uniform(-5, 20)
        path = list(rng.uniform(0, 15, rng.integers(1, 12)))
        pT = accelerate(p0, path, un, a)[-1]
        assert np.isclose(sum(u - un for u in path), sacrifice(p0, pT, a))
        # the long run: inflation is constant only where unemployment equals the natural rate
        assert np.isclose(accelerate(p0, [un] * 5, un, a)[-1], p0)
    print("ok the key equations and the claims made of them on 600 random draws")


# ---------------------------------------------------------------------------------------------------
# 4. The text, section by section
def guide(F, Y, Q):
    t = TEX.read_text(encoding="utf-8")
    assert f"\\guidequestion{{{GUIDE}}}" in t and GUIDE == PREV
    assert chapter("ch43_planned").rstrip().endswith(PREV)                      # 第 43 章交来的问题
    assert "\\guideprereq{\\chref{ch:phillips}\\enspace\\nameref{ch:phillips}}" in t
    said("解释菲尔普斯（1967）与弗里德曼（1968）为什么预言长期菲利普斯曲线是垂直的", F["ph_1967"][0], F["f68_issue"][0])
    said("用 1970 年代的数据检验这一预言", 1970)
    say("推导附加预期的菲利普斯曲线与加速论假说", "用适应性预期模拟反通胀的产出代价")
    assert "\\chapterstub" not in t


def opening(F, Y, Q):
    d, y = F["f68_date"]
    m = month("f68_date", "December")
    assert pd.Timestamp(int(y), m, int(d)).day_name() == "Friday"
    said("1967 年 12 月 29 日是星期五", y, m, d)
    has("f68_date", "Presidential address", "Eightieth Annual Meeting of the American Economic Association",
        "Washington, D.C.")
    say("在华盛顿美国经济学会的第八十届年会上发表会长演说")
    has("f68_issue", "MARCH 1968", "Number 1")
    assert F["f68_issue"][0] == y + 1                                            # 次年
    said("演说登在次年 3 月的《美国经济评论》上", month("f68_issue", "MARCH"))
    has("f68_title", "THE ROLE OF MONETARY POLICY")
    has("f68_topic", "My topic for tonight")                                   # 那天晚上，当晚
    say("那天晚上，弗里德曼", "他当晚只讲其中的一件工具")
    has("f68_goals", "high employment, stable prices, and rapid growth")
    has("f68_limits", "peg interest rates", "peg the rate of unemployment")
    said("比如失业 3\\%，失业低于目标就收紧", F["f68_target"][0])
    said("那几年美国的失业离 3\\% 不远", F["f68_target"][0])
    said("1967 年的失业率是 3.8\\%，消费物价比上年涨 3.1\\%", 1967, b40(1967)["all"], b62(1967)["year"])
    said("1969 年失业降到 3.5\\%，物价涨了 5.5\\%", 1969, b40(1969)["all"], b62(1969)["year"])
    ss = there("ch38_phillips", "萨缪尔森与索洛（1960）")[0]
    said("萨缪尔森与索洛 1960 年画的菜单上，失业 3\\% 对应物价每年涨约 4.5\\%", ss,
         *there("ch38_phillips", "B 点失业 3\\%，物价每年涨约 4.5\\%"))
    said("到了 1975 年，失业升到 8.5\\%，物价仍涨 9.1\\%", 1975, b40(1975)["all"], b62(1975)["year"])
    said("1980 年，失业 7.1\\%，物价涨 13.5\\%", 1980, b40(1980)["all"], b62(1980)["year"])
    # 1967 is near Samuelson and Solow's menu (the straight line from A to B of Ch 38's figure), the later points are not
    ua, ub, pb = there("ch38_phillips", "A 点物价稳定，失业约 5.5\\%；B 点失业 3\\%，物价每年涨约 4.5\\%")
    menu = lambda u: pb * (ua - u) / (ua - ub)
    said("1967 年的点还在菜单附近，后面几个点都不在菜单上（本书的解读）", 1967)
    assert abs(b62(1967)["year"] - menu(b40(1967)["all"])) < 0.5
    assert all(b62(y)["year"] - menu(b40(y)["all"]) > 1.5 for y in (1969, 1975, 1980))
    assert paragraph("那几年美国的失业离 3\\% 不远").endswith(GUIDE)              # the opening ends with the question


def world(F, Y, Q):
    d, y = F["f76_date"]
    assert F["f76_title"] == F["f76_date"]                                       # the lecture's head and its web page
    said("演讲是 1976 年 12 月 13 日作的", y, month("f76_date", "December"), d)
    assert told("九年以后，弗里德曼在诺贝尔奖的演讲里", "", "年以后") == y - F["f68_date"][1]
    has("f76_stages", "two stages", "entering a third")
    say("经过了两个阶段，正在进入第三个")
    said("弗里德曼 1967 年的演说也描述了当时的风气", F["f68_date"][1])
    has("f68_twenties", "late 'twenties")
    said("他拿 1920 年代末与当时对照", 1920)
    said("1962 年，肯尼迪把 4\\% 的失业率定为美国的临时目标",
         *there("ch38_phillips", "1962 年，肯尼迪把 4\\% 叫作临时的目标"))
    has("gk_controls", "Nixon-era")
    said("这些管制把物价水平压低了 1.5 个百分点，取消管制又把它推高 2.5 个百分点", *F["gk_controls"])
    said("1974 年的紧缩是谁定的？", F["mp_squeeze"][0])
    said("在 1975 年的《布鲁金斯经济活动论文》上作了分析", year_in("mp1975_44", r"Activity (\d{4})\(1\)"))
    has("mp_squeeze", "mid-1974")
    said("特别是 1974 年年中的严厉紧缩", F["mp_squeeze"][0])
    said("联邦储备 1974 年的政策混合了两个目标", F["mp_blend"][0])
    has("mp_m1target", "Council of Economic Advisers")
    said("一是把 M1 的增长大致控制在经济顾问委员会 1974 年报告预示的 6\\% 以内", F["mp_m1target"][1],
         F["mp_m1target"][0])
    A = F["mp_admin"]
    said("政府为 1974 年定的目标是实际收入增长 1\\%，物价上涨约 7\\%，两者合起来要求货币收入增长约 8\\%",
         A[0], A[1], A[6], F["mp_income8"][0])
    assert round(100 * ((1 + A[1] / 100) * (1 + A[6] / 100) - 1)) == F["mp_income8"][0]
    said("6\\% 的货币增长远远不够", F["mp_toosmall"][0])
    said("第二季度的紧缩让联邦基金利率从 3 月初的不到 9\\% 升到 7 月初的 13.5\\%", month("mp_funds", "March"),
         F["mp_funds"][0], month("mp_funds", "July"), F["mp_funds"][1])
    has("mp_funds", "second quarter", "below 9 percent in early March")
    said("后来修订，2 月到 5 月 M1 的年增长率从 9.7\\% 改成了 7.6\\%", month("mp_revised", "February"),
         month("mp_revised", "May"), *F["mp_revised"])
    said("他们不相信决策者有意要 9\\% 的失业", F["mp_nine"][0])
    cd, cy = F["f76_callaghan_date"]
    said("1976 年 9 月 28 日在工党大会上的话", cy, month("f76_callaghan_date", "September"), cd)
    has("f76_callaghan_date", "Labour Party Conference")
    # who decided: the Federal Reserve's squeeze of 1974, the administration's targets
    say("1974 年的紧缩是谁定的？", "谁让通胀升高？")


def friedman(F, Y, Q):
    # the basic problem of a natural-rate target (editor, after the review)
    has("f68_basic", "the basic problem", "determinate policy")
    has("f68_reasons", "reasons other than monetary policy")
    has("f68_random", "random walk")
    assert page("f68_basic") == page("f68_reasons") == 10 and page("f68_random") == 11
    say("他说，根本的问题还不在这里。即使知道自然率，想把市场的失业率钉在那里，也得不出一个确定的政策",
        "货币增长就会像随机游走一样被推来推去")
    said("假如人人都预期物价每年涨 75\\% 以上", F["f68_brazil75"][0])
    said("巴西把物价的涨幅压到每年约 45\\% 时", F["f68_brazil45"][0])
    said("弗里德曼 1976 年回忆", F["f76_date"][1])
    said("萨缪尔森与索洛 1960 年猜过", there("ch38_phillips", "萨缪尔森与索洛（1960）")[0])
    said("\\subsubsection{为什么守不住 3\\%}", F["f68_target"][0])
    said("回到 3\\% 的目标。设自然率高于 3\\%，开头物价稳定，失业高于 3\\%", *F["f68_suppose"])
    said("要把失业守在 3\\%，货币当局只能让货币增长得更快", F["f68_more"][0])
    has("f68_years", "two to five years")
    assert told("个人判断最初的效果持续两到五年", "持续", "到") == cardinal("two")
    assert told("个人判断最初的效果持续两到五年", "到", "年") == cardinal("five")
    has("f68_decades", "a couple of decades")
    assert told("就业完全调整到新的通胀率，大约要二十年", "大约要", "年") == 20
    has("f68_south", "South American countries")


def model(F, Y, Q):
    M = MODEL
    y76 = F["f76_date"][1]
    said("$\\alpha>0$记失业对通胀的影响", 0)
    said("弗里德曼 1976 年把自然失业率记作", y76)
    has("f76_un2", "(U N )")
    said("设预期是 2\\%，自然率是 6\\%（教学用的假设），失业 3\\% 时通胀是$2+3\\alpha$", M["pi0"], M["un"], M["u"],
         M["pi0"], M["un"] - M["u"])
    p1 = curve(M["pi0"], M["u"], M["un"], 1.0)                                    # 2 + 3 alpha, at alpha = 1
    assert p1 == M["pi0"] + (M["un"] - M["u"])
    said("同一个 3\\% 的失业配的通胀就多出$3\\alpha$", M["u"], M["un"] - M["u"])
    said("弗里德曼 1976 年说，这个假说也叫自然率假说或加速论", y76)
    has("f76_names", "“natural-rate”", "“accelerationist”")
    said("弗里德曼 1976 年把理由讲得更直白", y76)
    said("如果人人都预期物价每年涨 20\\%", F["f76_twenty"][0])
    said("20\\% 的通胀也就没有理由对应另一个失业水平", F["f76_twenty2"][0])
    said("弗里德曼 1976 年用一张图讲同一个过程", y76)
    has("f76_fig2_start", "Start from point E")
    said("弗里德曼 1976 年讲过英美的经验", y76)
    has("f76_centuries", "two centuries", "a century and a half")
    said("弗里德曼 1976 年列举了经济学家当时的几种态度", y76)
    # ex:naturalrate-accel
    a, un, pi0, u = M["alpha"], M["un"], M["pi0"], M["u"]
    assert u == F["f68_target"][0]                                                # 弗里德曼举例的 3%
    said("{守住 3\\% 的失业}", u)
    said("设$\\alpha=0.5$，$u^{n}=6\\%$（教学用的假设），通胀原来稳定在 2\\%。货币当局从第 1 年起把失业守在弗里德曼举例的 3\\%",
         a, un, pi0, 1, u)
    said("若人们的预期一直停在 2\\%，结果怎样？", pi0)
    said("第 4 年以后放手，失业回到 6\\%，通胀停在哪里？", M["after"], un)
    path = accelerate(pi0, [u] * M["after"], un, a)
    step = -a * (u - un)
    said("每年上升$0.5\\times(6-3)=1.5$个百分点，依次是 3.5\\%、5\\%、6.5\\% 与 8\\%", a, un, u, step, *path)
    said("每年都是$2+1.5=3.5\\%$，这就是菜单上的一个点", pi0, step, curve(pi0, u, un, a))
    assert accelerate(path[-1], [un] * 3, un, a) == [path[-1]] * 3
    said("停在 8\\%（本书的计算）", path[-1])


def cost(F, Y, Q):
    a, un = MODEL["alpha"], MODEL["un"]
    c = okun()
    said("把式~\\eqref{eq:naturalrate-accel}从第 1 年加到第$T$年", 1)
    said("失业率每高出 1 个百分点，产出约少 3.2\\%", 1, c)
    said("下面把奥肯式子里的 4\\% 换成$u^{n}$", there("ch38_phillips", "P=A\\,[1+0.032\\,(U-4)]")[2])
    said("通胀每降 1 个百分点，累计要少生产一年产出的$3.2/\\alpha$个百分点", 1, c)
    # ex:naturalrate-disinflation
    D = DIS
    said("仍设$\\alpha=0.5$，$u^{n}=6\\%$。通胀原来稳定在 10\\%，要降到 4\\%。", a, un, D["start"], D["end"])
    said("渐进：失业守在 8\\%，要几年？", D["slow"])
    said("急降：失业守在 12\\%，要几年？", D["fast"])
    said("按奥肯的系数 3.2，累计少生产多少？", c)
    slow, fast = disinflation(D["slow"]), disinflation(D["fast"])
    said("每年降$0.5\\times(8-6)=1$个百分点，要 6 年，依次是 9\\%、8\\%、7\\%、6\\%、5\\% 与 4\\%", a, D["slow"], un,
         a * (D["slow"] - un), len(slow), *slow)
    said("每年降$0.5\\times(12-6)=3$个百分点，要 2 年，依次是 7\\% 与 4\\%", a, D["fast"], un, a * (D["fast"] - un),
         len(fast), *fast)
    s = sacrifice(D["start"], D["end"], a)
    assert len(slow) * (D["slow"] - un) == len(fast) * (D["fast"] - un) == s
    said("都是$(10-4)/0.5=12$个百分点·年", D["start"], D["end"], a, s)
    said("累计少生产的产出是一年产出的$3.2\\times12=38.4\\%$，牺牲率是$38.4/6=6.4$", c, s, c * s, c * s,
         D["start"] - D["end"],
         c * s / (D["start"] - D["end"]))
    said("$\\alpha=0.5$，$u^{n}=6\\%$，通胀从 10\\% 降到 4\\%，预期按上一年的通胀形成", a, un, D["start"], D["end"])
    said("两种办法累计多出的失业都是 12 个百分点·年", s)
    # Okun (1978) as Gordon and King report it
    gk = year_in("gk1982_44", r"Activity (\d{4})\(1\)")
    has("gk_okun", "Four years ago")
    assert gk - 4 == F["gk_fn1"][2]
    said("1978 年，奥肯", F["gk_fn1"][2])
    said("他认为通胀每永久降低 1 个百分点，累计要牺牲一年 GNP 的 10\\%", F["gk_okun"][1], F["gk_okun"][0])
    said("他算出的代价在一年 GNP 的 6\\% 到 18\\% 之间，平均是 10\\%", *F["gk_okun_range"])
    r = F["gk_okun_range"][2]
    said("按上面的模型，牺牲率是 10，$\\alpha$约为 0.32", r, c / r)
    said("他们自己模拟了 1981—1992 年的两条路径", *F["gk_simulate"][1:])
    said("对照的路径让 M1 每年增长 6.6\\%", F["gk_control"][0])
    v, v2 = F["gk_volcker"], F["gk_volcker2"]
    said("减速的路径让它 1981 年增长 5.0\\%，1982 年增长 4.0\\%", v[1], v[0], v[3], v[2])
    said("此后每年减 0.5 个百分点，1986—1992 年保持 2.0\\%", v2[0], v2[2], v2[3], v2[1])
    assert v[2] - (v2[2] - v[3]) * v2[0] == v2[1]                                 # 4.0 less 0.5 a year to 1986
    has("gk_official", "current official policy of the Federal Reserve Board")
    said("累计的产出损失是一年 GNP 的 13.4\\%，通胀平均每年降 4.4 个百分点", *F["gk_basic"])
    said("不贴现的牺牲率是 3.0，贴现以后是 4.3", *F["gk_ratios"])
    assert abs(F["gk_basic"][0] / F["gk_basic"][1] - F["gk_ratios"][0]) < 0.05
    said("只算到 1992 年", F["gk_over"][0])
    said("以及 1981—1985 年萧条中投资减少的损失", F["gk_under"][1], 1900 + F["gk_under"][2])
    # who paid: table B-40
    has("b40_cols", "Both sexes 16–19 years", "Black", "Married men, spouse present")
    has("b40_title", "Civilian unemployment rate")
    r75, r79, r82 = b40(1975), b40(1979), b40(1982)
    said("按表 B-40，1975 年全体劳动者的失业率是 8.5\\%，黑人是 14.8\\%", F["b40_title"][0], 1975, r75["all"],
         r75["black"])
    said("16—19 岁的青年是 19.9\\%", *F["b40_cols"], r75["youth"])
    said("1982 年全体升到 9.7\\%，黑人是 18.9\\%，与妻子同住的已婚男子只有 6.5\\%", 1982, r82["all"], r82["black"],
         r82["married"])
    said("青年是 23.2\\%", r82["youth"])
    said("从 1979 年到 1982 年，全体的失业率升了 3.9 个百分点，黑人升了 6.6 个", 1979, 1982, r82["all"] - r79["all"],
         r82["black"] - r79["black"])
    said("青年升了 7.1 个", r82["youth"] - r79["youth"])
    assert r82["black"] - r79["black"] > r82["all"] - r79["all"] < r82["youth"] - r79["youth"]
    said("沃尔克 1979—1982 年的反通胀实际付出了多少", *there("ch49_credibility", "用沃尔克反通胀（1979—1982）估算牺牲率"))


def test(F, Y, Q):
    S = stats()
    said("\\section{1970 年代的检验}", 1970)
    said("\\figref{fig:naturalrate_us}把 1960—1985 年美国的失业率", 1960, 1985)
    e1, e2 = S[(1960, 1969)], S[(1970, 1985)]
    assert e1["corr"] < 0 and e2["corr"] < 0
    said("1960—1969 年的点像一张菜单，失业低的年份通胀高，相关系数约为$-0.84$", 1960, 1969, -e1["corr"])
    said("1970—1985 年的点散开了，相关系数只有约$-0.11$", 1970, 1985, -e2["corr"])
    assert told("这十六年平均失业", "这", "年") == e2["n"] and told("前十年只有", "前", "年") == e1["n"]
    said("这十六年平均失业 6.9\\%，通胀 7.0\\%", e2["u"], e2["p"])
    said("前十年只有 4.8\\% 与 2.4\\%", e1["u"], e1["p"])
    said("顺着年份看，1970 年代的点在图上绕圈", 1970)
    said("1974 年通胀跳到 11.0\\%，失业还只有 5.6\\%", 1974, b62(1974)["year"], b40(1974)["all"])
    said("1975 年失业升到 8.5\\%，次年通胀降到 5.8\\%", 1975, b40(1975)["all"], b62(1976)["year"])
    said("1980 年通胀升到 13.5\\%，失业是 7.1\\%", 1980, b62(1980)["year"], b40(1980)["all"])
    said("1982 年失业升到 9.7\\%，次年通胀降到 3.2\\%", 1982, b40(1982)["all"], b62(1983)["year"])
    said("美国的失业率与通胀率，1960—1985 年", 1960, 1985)
    said("蓝点是 1960—1969 年，橙点是 1970—1985 年", 1960, 1969, 1970, 1985)
    has("b40_source", "Bureau of Labor Statistics")
    has("b62_urban", "For all urban consumers")
    said("数据：《总统经济报告》（2000）表 B-40 与 B-62", year_in("erpb40_44", r"February (\d{4})"),
         F["b40_title"][0], F["b62_title"][0])
    R = S[("reg", 1960, 1985)]
    assert R["slope"] < 0
    said("1960—1985 年得$\\pi_t-\\pi_{t-1}=4.64-0.74\\,u_t$", 1960, 1985, R["const"], -R["slope"])
    said("通胀不变时失业率约为 6.3\\%", R["un"])
    u, d = S["u"], S["d"]
    low = list(u[u < 5].index)
    assert low == [1965, 1966, 1967, 1968, 1969, 1970, 1973] and (d[u < 5] > 0).all()
    said("失业低于 5\\% 的 7 年里，即 1965—1970 年与 1973 年，通胀年年上升", 5, len(low), low[0], low[5], low[6])
    falling = d[d < 0].index
    said("通胀下降的 9 年，失业都在 5.6\\% 以上", len(falling), u[falling].min())
    high = u[u >= 7].index
    rising = [y for y in high if d[y] > 0]
    said("可是失业在 7\\% 以上的 9 年里，1977、1980 与 1984 年的通胀仍在上升", 7, len(high), *rising)
    # Friedman's Table 1
    t1 = {q: F[f"f76_t{q}"] for q in (1956, 1961, 1966, 1971)}
    names = ["法国", "德国", "意大利", "日本", "瑞典", "英国", "美国", "七国平均"]
    for i, name in enumerate(names):
        row = " & ".join(f"{t1[q][2 + 2 * i]:.1f} & {t1[q][3 + 2 * i]:.1f}" for q in t1)
        said(f"{name} & {row} \\\\", *[x for q in t1 for x in (t1[q][2 + 2 * i], t1[q][3 + 2 * i])])
    for q in t1:
        assert t1[q][1] == q + 4
        dp, un_ = t1[q][2:16:2], t1[q][3:16:2]
        assert abs(np.mean(dp) - t1[q][16]) < 0.05 and abs(np.mean(un_) - t1[q][17]) < 0.05    # the simple mean
    said(" & \\multicolumn{2}{c}{1956—1960} & \\multicolumn{2}{c}{1961—1965} & \\multicolumn{2}{c}{1966—1970} & "
         "\\multicolumn{2}{c@{}}{1971—1975} \\\\", *[x for q in t1 for x in t1[q][:2]])
    said("七国的通胀与失业，1956—1975 年", F["f76_table"][1], F["f76_table"][2])
    said("弗里德曼（1976）表 1。通胀是消费物价的年复合涨幅，按 1955—1960 年、1960—1965 年等五年计算", F["f76_date"][1],
         F["f76_table"][0], *F["f76_t1note"][:4])
    has("f76_t1note", "compounded annually", "DP is dated one-half year prior to associated U")
    say("七国平均等于七国的简单平均（本书的核对）")
    # the counts of countries whose inflation and unemployment moved in opposite directions
    opposite = []
    for q0, q1 in ((1956, 1961), (1961, 1966), (1966, 1971)):
        opposite.append([names[i] for i in range(7)
                         if (t1[q1][2 + 2 * i] - t1[q0][2 + 2 * i]) * (t1[q1][3 + 2 * i] - t1[q0][3 + 2 * i]) < 0])
    assert [len(o) for o in opposite] == [5, 4, 1] and opposite[2] == ["意大利"]
    has("f76_five", "five out of seven countries")
    has("f76_four", "only four out of seven countries")
    has("f76_one", "only one out of seven countries")
    say("七国中有五国的通胀与失业反向变动", "第二与第三个五年之间只剩四国", "最后两个五年之间只剩一国，就是意大利")
    it = (t1[1966][6], t1[1966][7], t1[1971][6], t1[1971][7])
    assert it[3] < it[1] and it[2] > 3 * it[0]                                     # 略低；三倍多
    said("1971—1975 年它的失业比前五年略低，通胀却增加到原来的三倍多，1973 年以后两者都急剧上升", *F["f76_italy"])
    has("f76_italy", "a more than tripling", "since 1973")
    said("预期的通胀若是每年 20\\%，长期工资合同会让工资每年比零通胀时多涨 20\\%，长期贷款的利率高出 20 个百分点",
         *F["f76_index20"][:3])
    said("20\\% 的通胀若持续几十年", F["f76_longlong"][0])
    has("f76_longlong", "for many decades", "long-long-run vertical Phillips curve")


def niru(F, Y, Q):
    said("按他们的说法，1953—1971 年的数据与一个界定清楚", F["mp_stable"][0], 1900 + F["mp_stable"][1])
    said("横轴是经济顾问委员会按 1956 年的劳动力构成调整过的失业率", F["mp_1956"][0])
    has("mp_1956", "Councilof EconomicAdvisers")
    has("mp_five", "In eight of the years")
    said("调整后的失业率高于 5\\% 的 8 年里，除了 1962 年，通胀都下降了，他们推断这个失业率的 NIRU 至多是 5\\%",
         F["mp_five"][1], cardinal("eight"), F["mp_five"][2], F["mp_five"][3])
    has("mp_43", "In nine years", "all but two")
    said("等于或低于 4.3\\% 的 9 年里，除了两年，通胀都明显上升", F["mp_43"][0], cardinal("nine"))
    has("mp_488", "\"negligible\"rate of inflation", "we use 2 percent")
    said("他们先取 2\\% 作为可以忽略的通胀率，再用回归解出 4.88\\%", F["mp_488"][0], F["mp_488"][2])
    said("按当时的劳动力构成，还要加 0.8 个百分点", F["mp_08"][0])
    assert round(F["mp_488"][2] + F["mp_08"][0], 1) == F["mp_08"][2]
    said("按官方的失业率，NIRU 当时估计略高于 5.5\\%", F["mp_55"][0])
    assert F["mp_55"][0] < F["mp_08"][2]                                          # 略高于 5 1/2
    has("mp_terms", "over the last two decades")
    said("把 1977 年年中的失业目标稳妥地定在 6\\%，为此产出在今后两年至少要增长 17\\%", *F["mp_target"], F["mp_17"][0])
    said("头一年货币收入的年增长要超过 15\\%", F["mp_income15"][0])
    said("货币供给也要有一段时间增长 10\\% 以上", F["mp_money10"][0])
    said("守着 1974 年那样的货币增长目标", F["mp_sluggish"][0])
    said("{自然失业率（弗里德曼，1968）}{NIRU（莫迪利亚尼与 Papademos，1975）}", F["f68_issue"][0],
         year_in("mp1975_44", r"Activity (\d{4})\(1\)"))
    said("{按官方失业率略高于 5.5\\%", F["mp_55"][0])
    said("{1953—1971 年稳定，前提是按劳动力构成调整", F["mp_stable"][0], 1900 + F["mp_stable"][1])


def britain_japan(F, Y, Q):
    U = uk()
    e = U.loc[1955:1969]
    said("1955—1969 年英国的失业率在 1.6\\% 到 3.5\\% 之间", 1955, 1969, e["unemp_pct"].min(), e["unemp_pct"].max())
    said("消费物价每年涨 0.6\\% 到 5.2\\%", e["cpi_infl_pct"].min(), e["cpi_infl_pct"].max())
    for y, words in ((1971, "1971 年物价涨了 9.4\\%，失业是 4.1\\%"), (1974, "1974 年物价涨了 15.7\\%，失业只有 3.6\\%"),
                     (1975, "1975 年物价涨了 22.7\\%，失业是 4.5\\%")):
        said(words, y, U.loc[y, "cpi_infl_pct"], U.loc[y, "unemp_pct"])
    assert U.loc[1979:1984, "unemp_pct"].is_monotonic_increasing                  # 1980 年以后失业急升
    said("1980 年以后失业急升，1981 年是 9.6\\%，1983 年到了 11.5\\%", 1980, 1981, U.loc[1981, "unemp_pct"], 1983,
         U.loc[1983, "unemp_pct"])
    said("物价的涨幅 1980 年仍有 15.2\\%，1983 年降到 4.9\\%", 1980, U.loc[1980, "cpi_infl_pct"], 1983,
         U.loc[1983, "cpi_infl_pct"])
    said("卡拉汉 1976 年的那番话，正说在这两段之间", F["f76_callaghan_date"][1])
    m = load_snapshot("boe_millennium_uk_1954_1986")[1]
    assert "LFS/claimant-count discrepancy in female unemployment" in m["series"]
    say("女性失业按劳动力调查与申领人数之差调整过")
    assert "version 3.1" in m["source"] and "A47" in m["source"] and "A50" in m["source"]
    for words in ("1997 edition", "from 1971 the ONS Labour Force Survey series MGRZ", "series MGSC",
                  "'1949-2014 CPI (ONS)'", "to 1970 the mid-year estimates"):
        assert words in m["series"], words
    said("(a) 英国，1955—1985 年", 1955, 1985)
    said("数据据英格兰银行《英国千年宏观经济数据》（3.1 版）表 A50 与 A47", 3.1, 50, 47)
    said("1970 年以前据《经济趋势年度增刊》（1997 年版）的年中估计", 1970, 1997)
    said("1971 年起是英国国家统计局劳动力调查的 MGRZ 与 MGSC 序列", 1971)
    said("消费物价 1949 年以后是英国国家统计局的 CPI", 1949)
    said("(b) 日本，1955—1985 年", 1955, 1985)
    J = jp()
    jm = load_snapshot("naturalrate_japan_1953_1986")[1]
    assert "沖縄の本土復帰により、1972年７月以降、沖縄県も調査の範囲に含まれた。" in jm["notes"]
    assert J.loc[1953:1972, "unemp_excl_okinawa_pct"].equals(J.loc[1953:1972, "unemp_pct"])
    assert J.loc[1974:, "unemp_excl_okinawa_pct"].isna().all()
    said("1973 年以前的失业率不含冲绳，1973 年取含冲绳的数", 1973, 1973)
    say("出典：「労働力調査」（総務省統計局）、「消費者物価指数」（総務省統計局）を加工して作成")
    has("estat_edit_example", "を加工して作成")
    e = J.loc[1955:1972]
    said("1955—1972 年日本的完全失业率在 1.1\\% 到 2.5\\% 之间", 1955, 1972, e["unemp_pct"].min(), e["unemp_pct"].max())
    assert e["cpi_less_rent_pct"].min() < 0                                       # 最低是负的
    said("最高到 7.7\\%", e["cpi_less_rent_pct"].max())
    said("失业率最高与最低只差 1.4 个百分点", e["unemp_pct"].max() - e["unemp_pct"].min())
    said("1974 年物价飞涨，失业却几乎没动", 1974)
    has("lfs_table", "完全失業率", "1953年～")
    has("cpi_xr_table", "持家の帰属家賃を除く総合指数 前年比（1948年～最新年）")
    has("cpi_all_table", "中分類指数 前年比（1971年～最新年）")
    said("{日本 · 1973—1974 · 物价飞涨，失业不动}", 1973, 1974)
    e = J.loc[1960:1973]
    said("1960—1973 年日本的完全失业率在 1.1\\% 到 1.7\\% 之间，1974 年是 1.4\\%", 1960, 1973, e["unemp_pct"].min(),
         e["unemp_pct"].max(), 1974, J.loc[1974, "unemp_pct"])
    assert e["unemp_excl_okinawa_pct"].between(1.1, 1.7).all()                    # the figure without Okinawa too
    said("不含自有住房估算房租的消费物价，1973 年涨 11.7\\%，1974 年涨 24.5\\%", 1973, J.loc[1973, "cpi_less_rent_pct"],
         1974, J.loc[1974, "cpi_less_rent_pct"])
    said("含这一项的综合指数，1974 年涨 23.2\\%", 1974, J.loc[1974, "cpi_all_pct"])
    # the Economic Planning Agency's report of 1974
    has("wp_date", "経済企画庁")
    has("wp_fight", "激しい物価騰貴")                     # the foreword: the past year was a fight against soaring prices
    has("wp_title", "年次経済報告", "成長経済を超えて")
    assert F["wp_title"][1:] == F["wp_date"]
    said("经济企划厅在 1974 年 8 月的年度经济报告里分析了原因", showa(F["wp_date"][0]), F["wp_date"][1])
    wh, co = F["wp_wholesale"], F["wp_consumer"]
    said("批发物价从 1972 年 8 月起急涨，消费物价从 1973 年 3 月起急涨", showa(wh[0]), wh[1], showa(co[0]), co[1])
    w = F["wp_354"]
    said("1973 年度批发物价涨 35.4\\%", showa(w[0]), w[4])
    assert told("约四成来自国内供需的紧张", "约", "来自") == w[5] / 10
    assert told("约六成来自原油等初级产品价格暴涨", "约", "来自") == w[6] / 10
    has("wp_354", "国内需給ひつ迫", "原油やその他一次産品市況高騰など海外要因")
    said("它把昭和 40 年代（1965 年开始的十年）分成前后两半来比，后一半民间设备投资的实际增长从 16.1\\% 降到 10.4\\%",
         F["wp_halves"][0], showa(F["wp_halves"][0]), *F["wp_invest"][1:])
    assert F["wp_invest"][0] == F["wp_capacity"][0] == F["wp_halves"][0]
    said("制造业生产能力的增长从 12.1\\% 降到 7.4\\%", *F["wp_capacity"][1:])
    said("名义的需求却从 16.5\\% 加快到 17.4\\%", *F["wp_demand"])
    has("wp_m2", "(M 2 )")
    said("货币供给（M2）的增长从 16.6\\% 升到 21.9\\%，1971—1972 年的汇率调整期增势更强", *F["wp_m2"][1:],
         showa(F["wp_m2b"][0]), showa(F["wp_m2b"][1]))
    said("企划厅说，1973 年度的政策以总需要抑制为轴", showa(F["wp_axis"][0]))
    said("公定贴现率从 4 月到 12 月提高 5 次，从 4.25\\% 升到 9\\%", *F["wp_discount"])
    said("过去紧缩时，提高的幅度只在 1 个百分点左右", F["wp_past"][0])                # a rate: 1％ is a point
    r = F["wp_reserve"]
    assert (showa(r[2]) - showa(r[0])) * 12 + r[3] - r[1] == 12                   # 一年里
    said("存款准备率也在一年里提高了 5 次", r[4])
    has("wp_window", "相互銀行や上位信用金庫")
    said("收入低的阶层进入 1974 年以后", showa(F["wp_classes"][0]))
    # the paper is of August 1974 (昭和49年) and speaks of fiscal 1973 (48年度): its October is October 1973
    assert F["wp_assistance"][0] > F["wp_date"][1]
    said("1973 年 10 月又决定把生活扶助的标准提高 5\\%", showa(F["wp_date"][0]) - 1, *F["wp_assistance"])
    say("决定压住需求的是日本银行与政府（本书的概括）", "代价更重地落在收入低的家庭身上")
    said("1975—1978 年，通胀从 11.8\\% 降到 3.8\\%", 1975, 1978, J.loc[1975, "cpi_less_rent_pct"],
         J.loc[1978, "cpi_less_rent_pct"])
    said("失业只从 1.9\\% 升到 2.2\\%", J.loc[1975, "unemp_pct"], J.loc[1978, "unemp_pct"])


def debate(F, Y, Q):
    for words in ("\\subsubsection{是不是同一个发现}", "\\subsubsection{自然率会不会变}", "\\subsubsection{反通胀要付多大代价}"):
        say(words)
    y76 = F["f76_date"][1]
    said("从 1960 年代中期起研究失业怎样决定", F["ph_mid1960s"][0])
    has("ph_mid1960s", "mid-1960s")
    said("他在 2006 年的诺贝尔奖演讲里说", F["ph_title"][1])
    said("是他 1967 年为最优的通胀政策建的模型", F["ph_1967"][0])
    said("这篇论文 1966 年初写于伦敦经济学院", F["ph_lse"][0])
    has("ph_lse", "early months of 1966")
    said("弗里德曼 1976 年说，区分意外的需求变动", y76)
    has("f76_phelps", "E. S. Phelps and myself")
    said("弗里德曼 1976 年的说法是，需求意外加速", y76)
    # Phelps's velocity shock, neutral once expectations are correct (editor, after the review)
    has("ph_velocity", "velocity of money", "correspondingly higher paths")
    has("ph_neutral", "neutral for quantities and relative prices", "correct expectations")
    has("ph_perceive", "no way of perceiving such neutrality at the start")
    assert page("ph_velocity") == page("ph_neutral") == page("ph_perceive") == 347
    say("这个冲击对产量与相对价格就是中性的", "可是开头他们无从察觉这种中性",
        "预期追上来以后，需求的增加不再改变就业，长期的曲线也就是竖直的（本书的解读）")
    said("在菲尔普斯从 1968 年起建的几个模型里", F["ph_1968"][0])           # his note 13: 1968 fused with Phelps-Winter 1970
    said("他的模型常被看作与弗里德曼 1968 年的模型基本相同", F["ph_identical"][0])
    said("NIRU 在 1953—1971 年是稳定的", F["mp_stable"][0], 1900 + F["mp_stable"][1])
    said("据 Gordon 与 King 的注，Gordon 检验了按构成加权的自然失业率在 1970 年代上移的假说", F["gk_fn20"][0])
    has("gk_fn20", "tests and rejects")
    said("大约 1950—1970 年，日本与英国的平均失业都很低", *F["f76_japan_uk"])
    S = stats()
    said("用本章的回归，1960—1969 年估出的自然率约为 5.8\\%，1970—1985 年约为 6.8\\%", 1960, 1969,
         S[("reg", 1960, 1969)]["un"], 1970, 1985, S[("reg", 1970, 1985)]["un"])
    said("奥肯的估计在一年 GNP 的 6\\% 到 18\\% 之间，平均 10\\%", *F["gk_okun_range"])
    has("gk_ratio_def", "one point of inflation")
    said("Gordon 与 King 1982 年把牺牲率定义为永久消除 1 个百分点的通胀", year_in("gk1982_44", r"Activity (\d{4})\(1\)"),
         cardinal("one"))
    has("gk_half", "roughly half")
    assert F["gk_43"][1] == F["gk_ratios"][1] == F["gk_prefer"][0]
    said("他们的基本模型给出的贴现牺牲率是 4.3", F["gk_ratios"][1])
    has("gk_channels", "relative price of importsand", "food and energy", "appreciationin the effective exchange rate")
    assert page("gk_channels") == page("gk_43") == 236
    say("还压低进口品与食品、能源的相对价格，让美元的有效汇率升值")
    said("切断这些渠道，牺牲率依次升到 5.8、7.2 与 9.9", F["gk_43"][2], F["gk_72"][0], F["gk_99"][0])
    assert F["gk_99"][1] == F["gk_okun_range"][2]                                  # 接近奥肯的平均数
    has("gk_prefer", "which we prefer")
    said("他们偏爱 5.8 这个数", F["gk_prefer"][1])
    T = F["gk_trillion"]
    said("按它，通胀长期降低 5 个百分点，要放弃现值约为一年自然 GNP 29\\% 的产出，按当时的价格将近 1 万亿美元", T[0], T[1],
         T[2] * 1e9)
    six = F["gk_six"]
    said("他们说，牺牲率若是 6，代价就相当于一年自然 GNP 的 30\\%，平均每人约 4000 美元", six[0], six[2], six[4])
    said("1 万亿美元的产出损失减为约 8600 亿美元", F["gk_leisure"][0] * 1e9, F["gk_leisure"][1] * 1e9)
    said("Fischer 估计通胀降低 5 个百分点，每年的收益约为 GNP 的 0.30\\%", *F["gk_fischer"])
    said("收益可以高到 GNP 的 1\\%", F["gk_saving"][0])
    has("gk_saving", "tax reformis infeasible")
    said("贴现的福利收益不大可能接近 1 万亿美元", F["gk_welfare"][1] * 1e9)
    said("比这 1 万亿美元还多", F["gk_world"][0] * 1e9)
    said("与 1970 年代油价冲击、生产率放慢", F["gk_aversion"][0])
    # credibility in the discussion (editor, after the review)
    has("gk_fellner", "not a credible policy")
    has("gk_accommodated", "will be accommodated")
    has("gk_commit", "commitmentto reducethe rateof inflation")
    has("gk_reply", "Gordon responded", "feasible policy", "randomshocks")
    has("gk_steadfast", "steadfastpursuitof disinflation", "reduce the real costs of disinflation")
    for rid in ("gk_fellner", "gk_accommodated", "gk_commit", "gk_reply", "gk_steadfast", "gk_sims"):
        assert page(rid) == 243, rid
    say("Fellner 说，把通胀稳在当时的水平不是可信的政策", "Gordon 回答，只要当局表明不再容忍通胀继续上升",
        "坚定地反通胀能让人相信将来与过去不同")
    has("gk_sims", "muchhigherthanthat estimatedby Gordonand King")
    has("gk_sims2", "ignores fiscal policy", "Federal Reserve", "growingdeficits")


def deeper(F, Y, Q):
    y76 = F["f76_date"][1]
    mp, gk = year_in("mp1975_44", r"Activity (\d{4})\(1\)"), year_in("gk1982_44", r"Activity (\d{4})\(1\)")
    said("弗里德曼 1968 年的演说据美国经济学会网站的 PDF", F["f68_issue"][0])
    has("f68_scan", "onalyby")
    said("莫迪利亚尼与 Papademos（1975）、Gordon 与 King（1982）据布鲁金斯学会网站上的扫描本", mp, gk)
    said("GovInfo 上 2000 年《总统经济报告》的表 B-40 与 B-62", year_in("erpb62_44", r"February (\d{4})"),
         F["b40_title"][0], F["b62_title"][0])
    said("与 2015 年基准消费物价指数的长期时间序列", F["cpi_list"][0])
    said("经济企划厅 1974 年的报告据内阁府网站的网页版", showa(F["wp_title"][0]))
    said("奥肯（1978）没有读", F["gk_fn1"][2])
    said("菲尔普斯 1967 年与 1968 年的论文没有读，只按他 2006 年的演讲与弗里德曼 1976 年的演讲", F["ph_1967"][0],
         F["ph_1968"][0], F["ph_title"][1], y76)
    ry, rm, rd = (int(x) for x in meta()["retrieved"].split("-"))
    said("奥肯（1978）在圣路易斯联邦储备银行的 FRASER 上，2026 年 11 月 12 日那里没有应答", F["gk_fn1"][2], ry, rm, rd)
    assert "FRASER did not answer on 2026-11-12" in meta()["notes"]
    said("莫迪利亚尼 1944 年的论文仍然没有取得", *there("ch33_islm", "莫迪利亚尼 1944 年的论文本身没有取得"))
    w38 = there("ch38_phillips", "1969 年的失业率是 3.5\\%，消费物价涨了约 5.4\\%")
    assert "城市工薪劳动者消费物价指数" in chapter("ch38_phillips")
    said("1969 年美国的消费物价，\\chref{ch:phillips}按城市工薪劳动者的消费物价指数算是涨了约 5.4\\%，本章用全体城市消费者的指数，表 B-62 印的是 5.5\\%",
         w38[0], w38[2], F["b62_title"][0], b62(1969)["year"])
    J = jp()
    said("日本 1974 年的消费物价，不含自有住房估算房租的指数涨 24.5\\%，综合指数涨 23.2\\%", 1974,
         J.loc[1974, "cpi_less_rent_pct"], J.loc[1974, "cpi_all_pct"])
    link = re.search(r"figures for (\d{4})-(\d{4}) are the values for linking the series \(時系列接続用数値\)",
                     load_snapshot("naturalrate_japan_1953_1986")[1]["notes"])
    said("劳动力调查 1953—1977 年的数是为衔接后来的系列而调整过的数，与当年公布的年报不同", *map(int, link.groups()))
    said("日本 1973 年的失业率，表里有不含冲绳与含冲绳两个数，1.2\\% 与 1.3\\%", 1973,
         J.loc[1973, "unemp_excl_okinawa_pct"], J.loc[1973, "unemp_pct"])
    one, t71 = F["f76_one"], F["f76_t1971"]
    said("弗里德曼的正文说最后两个五年是 1966—1970 年与 1970—1975 年，他的表 1 写作 1971—1975 年", one[0], 1900 + one[1],
         one[2], 1900 + one[3], F["f76_table"][0], t71[0], t71[1])
    say("企划厅的网页版有个别排印的错字，如“基づものく”，引文照原样核对")


def legacy(F, Y, Q):
    said("弗里德曼 1976 年说，“自然失业率”这个说法", F["f76_date"][1])
    has("f76_wicksell", "a term I introduced to parallel")
    has("f68_minimum", "legal minimum wage rates", "labor unions")
    has("f76_insurance", "unemployment insurance")


def takeaways(F, Y, Q):
    said("弗里德曼 1967 年 12 月说", F["f68_date"][1], month("f68_date", "December"))
    said("奥肯估计牺牲率平均是 10", F["gk_okun_range"][2])
    has("gk_half", "roughly half")
    say("Gordon 与 King 认为只有约一半", "代价更重地落在青年与黑人等本来就最容易失业的人身上（本书的概括）")
    r79, r82 = b40(1979), b40(1982)
    assert min(r82["youth"] - r79["youth"], r82["black"] - r79["black"]) > r82["all"] - r79["all"]
    said("1970—1985 年美国的通胀与失业几乎不再相关", 1970, 1985)
    J = jp()
    said("日本 1974 年物价涨了约四分之一，失业只有 1.4\\%", 1974, J.loc[1974, "unemp_pct"])
    assert abs(told("日本 1974 年物价涨了约四分之一", "约", "") - J.loc[1974, "cpi_less_rent_pct"] / 100) < 0.01


def selfcheck(F, Y, Q):
    M, D = MODEL, DIS
    a, un = M["alpha"], M["un"]
    said("把失业守在 4\\%，前三年的通胀各是多少？", M["sc_u"])
    p = accelerate(M["pi0"], [M["sc_u"]] * 3, un, a)
    said("\\item 每年上升$0.5\\times(6-4)=1$个百分点，依次是 3\\%、4\\% 与 5\\%。", a, un, M["sc_u"],
         a * (un - M["sc_u"]), *p)
    said("通胀从 10\\% 降到 4\\%，失业守在 9\\%，要几年？", D["start"], D["end"], D["sc_u"])
    q = disinflation(D["sc_u"])
    said("\\item 每年降$0.5\\times3=1.5$个百分点，要 4 年；累计多出 12 个百分点·年。", a, D["sc_u"] - un,
         a * (D["sc_u"] - un), len(q), len(q) * (D["sc_u"] - un))
    c = okun()
    said("按奥肯的系数 3.2 算出的牺牲率是 5？", c, SC["ratio"])
    said("\\item $3.2/\\alpha=5$，$\\alpha=0.64$。", c, SC["ratio"], c / SC["ratio"])
    R = stats()[("reg", 1960, 1985)]
    said("失业率是 8\\% 的那一年，通胀约变动多少？", SC["u"])
    pred = R["const"] + R["slope"] * SC["u"]
    assert pred < 0 and abs(round(R["const"], 2) + round(R["slope"], 2) * SC["u"] - pred) < 0.05
    said("\\item $4.64-0.74\\times8\\approx-1.3$，约降 1.3 个百分点。", R["const"], -R["slope"], SC["u"], -pred, -pred)
    t61, t66 = F["f76_t1961"], F["f76_t1966"]
    said("弗里德曼的表 1 里，美国从 1961—1965 年到 1966—1970 年", F["f76_table"][0], *t61[:2], *t66[:2])
    assert (t66[14] - t61[14]) * (t66[15] - t61[15]) < 0                           # 反向变动
    said("\\item 通胀从 1.3\\% 升到 4.2\\%，失业从 5.5\\% 降到 3.9\\%，两者反向变动，符合。", t61[14], t66[14], t61[15],
         t66[15])
    has("ph_participation", "natural rate of labor force participation")


def ending(F, Y, Q):
    d, y = F["f68_date"]
    said("回到 1967 年 12 月 29 日的华盛顿", y, month("f68_date", "December"), d)
    has("f68_topic", "tonight")
    say("那天晚上，弗里德曼讲完货币政策做不到的事")
    has("f68_prescription", "steady rate of growth in a specified monetary total")
    has("f68_3to5", "currency plus all commercialbank deposits")
    has("f68_3to5b", "rough stability in the level of prices of final products")
    said("现金加全部商业银行存款每年约要增长 3\\% 到 5\\%", *F["f68_3to5"])
    assert tex_text().rstrip().endswith("（本书的解读）。" + NEXT)
    assert f"\\guidequestion{{{NEXT}}}" in chapter("ch45_monetarism")


def figures_data() -> None:
    """What the figures and their captions assert of their data."""
    s = us().loc[1960:1985]
    assert s.notna().all().all() and len(s) == 26
    U = uk().loc[1955:1985]
    assert U.notna().all().all() and len(U) == 31
    J = jp().loc[1955:1985, ["unemp_pct", "cpi_less_rent_pct"]]
    assert J.notna().all().all() and len(J) == 31
    # the rows of tables B-40 and B-62 quoted in the snapshot agree with the series (b40() and b62() compare them); the
    # first and last rows: 1959 gives the change of inflation in 1960, 1985 ends the figure
    quoted_years = sorted(int(k[4:]) for k in facts() if re.fullmatch(r"b(?:40|62)_\d{4}", k))
    for y in quoted_years:
        for name, f in (("b40", b40), ("b62", b62)):
            if f"{name}_{y}" in facts():
                f(y)
    assert {"b40_1959", "b62_1959", "b40_1985", "b62_1985"} <= set(facts())
    P = paths()
    for name, df in P.items():
        assert df["u"].iloc[0] == MODEL["un"] and df["pi"].iloc[-1] == DIS["end"]
        assert np.isclose((df["u"] - MODEL["un"]).sum(), sacrifice(DIS["start"], DIS["end"], MODEL["alpha"]))
        assert (df["pi_e"].iloc[1:].values == df["pi"].iloc[:-1].values).all()
    print(f"ok the data of the figures: {len(s)} American years, {len(U)} British, {len(J)} Japanese; two paths")


# ---------------------------------------------------------------------------------------------------
# 5. The book
# the life dates: words -> (row of the birth year, index), (row of the death year, index), row of the heading, heading
LIVES = {"Milton Friedman，1912—2006": (("loc_friedman", 0), ("loc_friedman", 1), "loc_friedman", "Friedman, Milton"),
         "Franco Modigliani，1918—2003": (("loc_modigliani", 1), ("loc_modigliani", 3), "loc_modigliani",
                                         "Franco Modigliani"),
         "James Callaghan，1912—2005": (("loc_callaghan", 0), ("loc_callaghan", 1), "loc_callaghan", "Callaghan, James"),
         "Knut Wicksell，1851—1926": (("loc_wicksell", 0), ("loc_wicksell", 1), "loc_wicksell", "Wicksell, Knut"),
         "Arthur Okun，1928—1980": (("loc_okun", 1), ("loc_okun", 3), "loc_okun_head", "Okun, Arthur M."),
         "Edmund S. Phelps，1933—2026": (("gnd_phelps_b", 0), ("gnd_phelps", 0), "loc_phelps", "CIP t.p. (Edmund S. Phelps)")}
# what other chapters tell: (words of this chapter, chapter where it is told, words there)
EVENTS = [("萨缪尔森与索洛 1960 年画的菜单上，失业 3\\% 对应物价每年涨约 4.5\\%（\\chref{ch:phillips}）", "ch38_phillips",
           "B 点失业 3\\%，物价每年涨约 4.5\\%"),
          ("1962 年，肯尼迪把 4\\% 的失业率定为美国的临时目标（\\chref{ch:phillips}）", "ch38_phillips",
           "1962 年，肯尼迪把 4\\% 叫作临时的目标"),
          ("维克塞尔区分了自然利率与市场利率（\\chref{ch:wicksell}）", "ch25_wicksell", "维克塞尔区分了自然利率与市场利率"),
          ("萨缪尔森与索洛 1960 年猜过，过去的经验会养成通胀的倾向", "ch38_phillips", "通胀的倾向由此养成"),
          ("他们没有判断菜单在长期里往哪个方向移（\\chref{ch:phillips}）", "ch38_phillips", "往哪个方向移动他们不下判断"),
          ("\\chref{ch:phillips}讲过休谟的看法，增加的货币在物价追上来以前刺激了产业", "ch38_phillips",
           "在物价追上来以前，增加的货币刺激了产业"),
          ("\\chref{ch:generaltheory}的争论问的是，工资与物价若能完全灵活，经济会不会自己回到充分就业",
           "ch32_generaltheory", "凯恩斯认为灵活的工资政策维持不了充分就业"),
          ("\\chref{ch:islm}的 IS–LM 把货币工资当作给定的", "ch33_islm", "希克斯先把货币工资固定下来"),
          ("制度怎样影响失业，在\\chref{ch:labor}", "ch57_labor", "讨论失业保险、雇佣保护与工会等制度和失业的关系"),
          ("预期的通胀不变，它就是\\chref{ch:phillips}的菜单", "ch38_phillips", "菜单上的每一个点，都是一种失业率配一种通胀率"),
          ("人们若会预期政策本身，结论还要更进一步，这是\\chref{ch:ratex}的理性预期", "ch48_ratex",
           "区分适应性预期与理性预期"),
          ("失业率每高出 1 个百分点，产出约少 3.2\\%（式~\\eqref{eq:phillips-okun}）", "ch38_phillips",
           "\\label{eq:phillips-okun}"),
          ("沃尔克 1979—1982 年的反通胀实际付出了多少，在\\chref{ch:credibility}", "ch49_credibility",
           "用沃尔克反通胀（1979—1982）估算牺牲率"),
          ("通胀的变动不只取决于失业，油价的冲击是\\chref{ch:oil}的题目", "ch47_oil",
           "用总供给冲击分析 1973 年与 1979 年的油价冲击"),
          ("货币数量与通胀的关系，是\\chref{ch:monetarism}的题目", "ch45_monetarism", "控制货币数量就能控制通胀吗？"),
          ("莫迪利亚尼 1944 年的论文仍然没有取得（\\chref{ch:islm}）", "ch33_islm", "莫迪利亚尼 1944 年的论文本身没有取得"),
          ("\\chref{ch:phillips}按城市工薪劳动者的消费物价指数算是涨了约 5.4\\%", "ch38_phillips",
           "1969 年的失业率是 3.5\\%，消费物价涨了约 5.4\\%"),
          ("今天的中央银行讲的中性利率，是维克塞尔的自然利率的后代（\\chref{ch:wicksell}）", "ch25_wicksell",
           "今天的中央银行讲的\\textbf{中性利率} $r^{*}$，是同一个想法的后代"),
          ("泰勒规则按通胀与产出缺口调整利率（\\chref{ch:consensus}）", "ch25_wicksell",
           "泰勒规则：按通胀与产出缺口调整（\\chref{ch:consensus}）"),
          ("泰勒规则按通胀与产出缺口调整利率（\\chref{ch:consensus}）", "ch55_consensus", "泰勒规则（1993）"),
          ("这是理性预期与卢卡斯批判（\\chref{ch:ratex}）", "ch48_ratex", "说明卢卡斯批判（1976）对宏观计量模型的含义"),
          ("降通胀的代价能不能靠可信的承诺减小，在\\chref{ch:credibility}", "ch49_credibility", "讨论可信度的作用"),
          ("名义刚性的新凯恩斯版本的曲线，在\\chref{ch:newkeynesian}", "ch54_newkeynesian", "新凯恩斯菲利普斯曲线"),
          ("这种滞后效应与欧洲的失业是\\chref{ch:labor}的题目", "ch57_labor", "的滞后效应分析欧洲失业")]
# the chapters this one names, and where their labels are
LATER = {"ch:phillips": "ch38_phillips", "ch:wicksell": "ch25_wicksell", "ch:generaltheory": "ch32_generaltheory",
         "ch:islm": "ch33_islm", "ch:labor": "ch57_labor", "ch:ratex": "ch48_ratex", "ch:credibility": "ch49_credibility",
         "ch:oil": "ch47_oil", "ch:consensus": "ch55_consensus", "ch:newkeynesian": "ch54_newkeynesian",
         "ch:monetarism": "ch45_monetarism"}
# the chapters that point here
POINTERS = ("ch01_intro", "ch25_wicksell", "ch32_generaltheory", "ch33_islm", "ch38_phillips", "ch45_monetarism",
            "ch47_oil", "ch48_ratex", "ch57_labor")


def book(F, Q):
    """Life dates and what other chapters tell."""
    t = tex_text()
    for words, ((rb, ib), (rd, id_), head_row, head) in LIVES.items():
        assert words in t, words
        assert f"{F[rb][ib]:.0f}—{F[rd][id_]:.0f}" in words, (words, rb, rd)
        assert Q[head_row].startswith(head), (head_row, Q[head_row])             # the person of the record
        COVERED.append(words)
    # the second witnesses: the GND for Modigliani, the Nobel pages and the LoC's source note for Phelps
    assert F["gnd_modigliani_b"] == [F["loc_modigliani"][1], 6, F["loc_modigliani"][0]]
    assert F["gnd_modigliani"] == [F["loc_modigliani"][3], 9, F["loc_modigliani"][2]]
    has("loc_modigliani", "born 18 June 1918", "died 25 September 2003")
    assert F["gnd_phelps_b"] == [1900 + F["loc_phelps"][2], F["loc_phelps"][0], F["loc_phelps"][1]]
    assert F["nobel_phelps_born"] == [F["gnd_phelps_b"][2], F["gnd_phelps_b"][0]]
    assert F["nobel_phelps_died"] == [F["gnd_phelps"][2], F["gnd_phelps"][0]] and F["gnd_phelps"][1] == 5
    has("nobel_phelps_died", "15 May 2026")
    assert Q["gnd_okun"] == Q["loc_okun_head"] == "Okun, Arthur M."
    has("loc_okun", "b. Nov. 28, 1928", "d. May 23, 1980")
    for here, ch, there_ in EVENTS:
        assert here in t, here
        assert there_ in chapter(ch), (ch, there_)
    named = set(re.findall(r"\\chref\{(ch:[^}]+)\}", t)) | set(re.findall(r"\\nameref\{(ch:[^}]+)\}", t))
    assert named == set(LATER), sorted(named ^ set(LATER))
    for label, ch in LATER.items():
        assert f"\\label{{{label}}}" in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (label, ch)
    for ch in POINTERS:
        assert re.search(r"\\(?:chref|ref|nameref)\{ch:naturalrate\}", chapter(ch)), ch
    print(f"ok {len(LIVES)} life dates, {len(EVENTS)} statements of other chapters, {len(LATER)} other chapters named")


# the bibliography item of each source of the snapshots (the authority records: loc44 and gnd44)
ITEM_OF = {"f1968_44": "friedman1968", "aeacopyright44": "friedman1968", "f1976_44": "friedman1976",
           "nobelfriedman44": "friedman1976", "phelps2006_44": "phelps2006", "nobelphelps44": "phelps2006",
           "nobelphelpsfacts44": "phelps2006", "mp1975_44": "modigliani1975", "brookingsterms44": "modigliani1975",
           "gk1982_44": "gordon1982", "erpb40_44": "erp2000", "erpb62_44": "erp2000", "estatlfs44": "estatlfs",
           "estatlt02_44": "estatlfs", "estatterms44": "estatlfs", "estatcpi44": "estatcpi",
           "estatcpixr44": "estatcpi", "estatcpizny44": "estatcpi", "wp74i1_44": "epa1974", "wp74m1_44": "epa1974",
           "wp7401201_44": "epa1974", "wp7401202_44": "epa1974", "wp7401203_44": "epa1974",
           "wp7401401_44": "epa1974", "caorules44": "epa1974", "pdl44": "epa1974"}
# the items shared with earlier chapters, outside the block: Friedman (1976) with Chapter 38, Okun (1962) with
# Chapter 38, the Bank of England's workbook with Chapters 18-38; the block names the hash of the copy read
SHARED = {"friedman1976", "okun1962", "boe2017"}


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


def block() -> tuple[str, dict[str, str], dict[str, str]]:
    """The bibliography block of Chapter 44, its items and all items of the bibliography."""
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    start = bib.index("% ---- 第 44 章")
    following = re.search(r"^% ---- 第 \d+ 章", bib[start + 1:], re.MULTILINE)
    end = start + 1 + following.start() if following else bib.index("\\end{thebibliography}")
    text = bib[start:end]
    assert bib.index("% ---- 第 43 章") < start
    items = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", text)}
    allitems = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", bib)}
    return text, items, allitems


def witnesses(F, Q):
    """Second witnesses of statements of the text, the licences and the bibliography block of the chapter."""
    # the address's date: the AER's own line; the lecture's date: its first page and the Nobel page
    assert F["f76_title"] == F["f76_date"]
    # Phelps and Friedman name each other: the lecture of 2006 and the lecture of 1976
    has("ph_identical", "Milton Friedman (1968)")
    has("f76_phelps", "E. S. Phelps")
    # the licences
    m = meta()
    lic = m["license"]
    lic_rows = ("aea_terms", "nobel_f76_copyright", "nobel_ph_copyright", "gk_copyright", "brookings_terms",
                "estat_free", "estat_numbers", "estat_source", "estat_example", "estat_edit", "estat_edit_example",
                "estat_standard", "cao_rule", "pdl_numbers", "pdl_source", "pdl_edit")
    for rid in lic_rows:
        assert re.search(r"\brows? [^)]*\b" + rid + r"\b", lic), rid
        assert words_of(rid) in lic or words_of(rid).lstrip("…") in lic, rid
    has("cao_date", "令和7年3月25日現在")
    assert "17 U.S.C. § 105" in lic and "no photographs are used" in lic and "CC0 1.0" in lic
    for rid in ("nobel_f76_book", "nobel_ph_book", "lfs_date", "estat_example"):
        assert rid in column("id"), rid
    # the bibliography block of the chapter
    text, items, allitems = block()
    assert FETCH in text and UK_FETCH in text
    assert f"共 {len(items)} 条" in text
    unescape = lambda s: re.sub(r"\\([$%&_#~])", r"\1", s).replace("--", "-")     # noqa: E731 - as LaTeX prints it
    for rid, key in (("aea_terms", "friedman1968"), ("nobel_ph_copyright", "phelps2006"),
                     ("brookings_terms", "modigliani1975"), ("brookings_terms", "gordon1982"),
                     ("estat_numbers", "estatlfs"), ("estat_source", "estatlfs"), ("estat_edit", "estatlfs"),
                     ("estat_standard", "estatlfs"), ("estat_numbers", "estatcpi"), ("estat_source", "estatcpi"),
                     ("estat_edit", "estatcpi"), ("estat_standard", "estatcpi"), ("cao_rule", "epa1974"),
                     ("pdl_numbers", "epa1974"), ("pdl_source", "epa1974"), ("pdl_edit", "epa1974")):
        assert words_of(rid) in unescape(items[key]), (rid, key)
    assert "公有领域" in items["erp2000"] and "17 U.S.C. § 105" in items["erp2000"] and "公共数据" in items["loc44"]
    assert "CC0" in items["gnd44"]
    for key in ("estatlfs", "estatcpi"):
        assert "を加工して作成" in items[key], key
    # every source is named by its URL and SHA-256 (the authority records by their URLs)
    for key, s in documents().items():
        item = "loc44" if key.startswith("loc_") else "gnd44" if key.startswith("gnd_") else ITEM_OF[key]
        assert unescape(s["url"]) in unescape(allitems[item]), key
        if item in SHARED:
            assert s["sha256"] in allitems[item], key                             # merged into the shared item
        elif not key.startswith(("loc_", "gnd_")):
            assert s["sha256"] in items[item], key
    # the pages of each work, as the snapshot's rows have them
    for key, srcs in (("friedman1968", ("f1968_44",)), ("phelps2006", ("phelps2006_44",)),
                      ("modigliani1975", ("mp1975_44",)), ("gordon1982", ("gk1982_44",))):
        assert f"第 {printed(srcs)} 页" in items[key], (key, printed(srcs))
        assert f"PDF 第 {pdf(srcs)} 页" in items[key], (key, pdf(srcs))
    assert f"第 44 章用第 {printed(('f1976_44',))} 页" in allitems["friedman1976"]    # Chapter 44's pages of the lecture
    assert "勘误" in items["modigliani1975"]
    for words, (_, _, head_row, _) in LIVES.items():
        if head_row.startswith("loc_") and head_row != "loc_phelps":
            assert Q[head_row].split(";")[0].replace("-", "--") in items["loc44"], head_row
    for gnd in ("124719414", "122147987", "121179613"):
        assert gnd in items["gnd44"], gnd
    # the titles of the works as the documents print them
    for rid, key, words in (("f68_title", "friedman1968", "THE ROLE OF MONETARY POLICY"),
                            ("ph_title", "phelps2006", "Macroeconomics for a Modern Economy"),
                            ("gk_title", "gordon1982", "Vector"),
                            ("b40_title", "erp2000", "Civilian unemployment rate"),
                            ("wp_title", "epa1974", "成長経済を超えて")):
        has(rid, words)
        assert words.lower() in unescape(items[key]).lower(), (rid, key)
    keys = set(allitems)
    cited = {k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", tex_text()) for k in c.split(",")}
    assert cited <= keys, sorted(cited - keys)
    assert set(items) == cited - SHARED and SHARED <= cited, sorted(set(items) ^ (cited - SHARED))
    print(f"ok {len(cited)} works cited, {len(items)} in the bibliography block of Chapter 44")


def documents() -> dict[str, dict]:
    """Every document of the three snapshots of data/fetch/naturalrate44.py."""
    out = dict(meta()["sources"])
    for name in ("naturalrate_us_1959_1985", "naturalrate_japan_1953_1986"):
        for key, src in load_snapshot(name)[1]["documents"].items():
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
    for words in ("1974 年的紧缩是谁定的？", "谁让通胀升高？",
                  "决定紧缩的是货币当局，失业升得最多的是本来就最容易失业的人（本书的概括）",
                  "决定压住需求的是日本银行与政府（本书的概括）", "代价更重地落在收入低的家庭身上",
                  "代价落在失业的人身上"):
        assert words in main_, words
    # documents are not the subjects of sentences: the author is named
    for bad in ("报告说", "演讲说", "演说说", "论文说", "书里说", "表说", "网页说"):
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
    for words, k in (("本书的解读", 8), ("本书的计算", 10), ("本书的概括", 3), ("本书的推导", 3), ("本书的核对", 3)):
        assert main_.count(words) >= k, (words, main_.count(words))
    # sentences: one semicolon at most
    prose = re.sub(r"\\datasource\{[^\n]*", "", main_)
    for s in re.split(r"(?<=[。？！])|\n", re.sub(r"“[^”]*”", "“”", prose)):
        assert s.count("；") <= 1, s
    # the boxes the editor asks for
    assert t.count("\\begin{compare}") == 2 and t.count("\\begin{case}") == 1 and t.count("\\begin{pitfall}") == 1
    assert t.count("\\begin{deeper}[史料说明]") == 1 and t.count("\\begin{keyeq}") == 3
    assert t.count("\\begin{example}") == 2 and t.count("\\fig{") == 3 and t.count("\\begin{table}") == 1
    assert t.count(GUIDE) == 2
    # the neighbours' topics: a clause or a sentence each
    for label in ("ch:ratex", "ch:credibility", "ch:labor", "ch:oil", "ch:monetarism", "ch:consensus",
                  "ch:newkeynesian", "ch:wicksell", "ch:islm", "ch:generaltheory"):
        assert t.count(f"\\chref{{{label}}}") <= 2, label
    # the debt the Brookings authors and Friedman name is the one the chapter names: NIRU, not the later NAIRU
    assert "NAIRU" not in main_


def main() -> None:
    df = _rows()
    F, Y, Q = facts(), years(), quotes()
    check_readings(df)
    check_text(df)
    for part in (guide, opening, world, friedman, model, cost, test, niru, britain_japan, debate, deeper, legacy,
                 takeaways, selfcheck, ending):
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
