"""Chapter 47 (石油危机与滞胀): every number and every quotation in zh/ch47_oil.tex.

    python3 checks/check_ch47.py

Inputs:
  oil_facts                     quotations of the chapter's sources with their page: FRUS 1969-1976 vol. XXXVI documents
                                209, 216, 220, 223, 271, 273, 277 and the volume's list of persons (history.state.gov);
                                the BIS Annual Reports of 1974, 1975 and 1980 (text layers); Hutchison (BIS Working Paper
                                13, page images); Gordon (BPEA 1975:1) and Bernanke, Gertler and Watson (BPEA 1997:1);
                                Hamilton (NBER WP 16790) and Blanchard and Gali (NBER WP 13368) (text layers); Barsky and
                                Kilian (NBER WP 8389) and Sachs and Warner (NBER WP 5398) (page images); Corden and Neary
                                (IIASA CP-82-58: paraphrased, the rows say where, they quote nothing but the cover);
                                Mehlum, Moene and Torvik (Oslo memorandum 29/2002); Budina, Pang and van Wijnbergen (World
                                Bank PRWP 4256); Rich (ECB WP 236); the Bank of Japan's history, vol. 6 (page images); the
                                indicator names of the World Development Indicators and the Pink Sheet's page; the terms of
                                the BIS, the Bank of Japan and the World Bank; the records of the persons named (Library
                                of Congress, Deutsche Nationalbibliothek, NDL). data/fetch/verify_web_quotes.py checks the
                                quotations against the documents; data/fetch/oil47.py fetches them
  oil_pinksheet                 the World Bank's annual crude-oil price, nominal and real 2010 dollars a barrel, 1960-2025
  oil_wdi                       World Development Indicators: consumer-price inflation of the G7 and Switzerland; fuel,
                                food and agricultural raw materials (% of merchandise exports) and manufacturing (% of
                                GDP) of Nigeria, the Netherlands, Norway and the United Kingdom; natural-resource rents
                                (% of GDP) of every economy in 1970 and 1990
  oil_pwt                       Penn World Table 10.01: rgdpe, rgdpna and pop in 1970, 1990 and 2019, and of the G7 and
                                Switzerland in 1969-1985
  zh/ch05, ch38, ch42, ch44,    the statements of other chapters that this chapter repeats (EVENTS); the stubs of
  ch45, ch46 ...                Chapters 48-51, 55, 57, 74 and 78 for what is handed on (LATER)

This script

1. reads the numbers of every row from its quotation by the rules of READINGS and compares them with the value
   column; the misreadings of the text layers are listed in MISPRINTS;
2. finds every “…” of the text among the renderings of TRANSLATIONS, and the words of the source each one renders
   (KEYWORDS) in the rows; the quotations stay short;
3. checks each number of the text with said(): the phrase is in the text and each number is the value of a row, a
   value of the data snapshots, a teaching input, or arithmetic on them (the two examples, the regressions of the
   resource test); every Arabic number of the text must lie in a phrase said() read (coverage()); every chain a = b of
   plain arithmetic in the text's math holds (arithmetic());
4. checks the key equations as printed, the claims made of them on random numbers, the data of the figures
   (figsrc/fig_ch47.py imports the series, the paths and the regressions from here), the life dates against the
   authority records, what other chapters tell, the licences and the bibliography block of Chapter 47;
5. lists the rows no "% 据:" anchor of the text names (common.anchors).

Set CH47_TEX to a scratch copy of the chapter to run the checks on it (mutation tests).
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

TEX = Path(os.environ.get("CH47_TEX", ROOT / "zh" / "ch47_oil.tex"))   # a scratch copy for mutation tests
GUIDE = "油价冲击为什么同时推高通胀和失业？产油国为什么会被“资源诅咒”？"
PREV = GUIDE                                        # Chapter 46's NEXT
NEXT = "人们会预期政策时，政策还有效吗？用历史数据估计的模型，为什么会在政策改变后失效？"   # Chapter 48's question (its stub)
FETCH = "data/fetch/oil47.py"


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
    df, m = load_snapshot("oil_facts", dtype=str, keep_default_na=False)
    assert 47 in m["used_in"] and m["fetch"] == FETCH
    assert df["id"].is_unique
    return df


@lru_cache(maxsize=None)
def meta() -> dict:
    return load_snapshot("oil_facts")[1]


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
    """What a row says: its quotation, or for the rows of Corden and Neary (paraphrased, never quoted) its note."""
    return quotes()[rid] or column("note")[rid]


def has(rid: str, *words: str) -> None:
    """Each of the words is in what row rid says."""
    for w in words:
        assert w in words_of(rid), (rid, w)


def page(rid: str) -> int:
    """The first printed page number of a row's juan column: 'p. 18 (PDF p. 19)' -> 18; 'PDF p. 7' -> 7."""
    return int(re.search(r"pp?\. (\d+)", column("juan")[rid]).group(1))


def pdf_page(rid: str) -> int:
    """The PDF page of a row: 'p. 18 (PDF p. 19)' -> 19."""
    return int(re.search(r"PDF pp?\. (\d+)", column("juan")[rid]).group(1))


def chapter(name: str) -> str:
    """Another chapter's text without its comment lines."""
    t = (ROOT / "zh" / f"{name}.tex").read_text(encoding="utf-8")
    return "\n".join(l for l in t.splitlines() if not l.lstrip().startswith("%"))


@lru_cache(maxsize=None)
def data(name: str) -> pd.DataFrame:
    df, m = load_snapshot(name)
    assert 47 in m["used_in"] and m["fetch"] == FETCH, name
    return df


@lru_cache(maxsize=None)
def data_meta(name: str) -> dict:
    return load_snapshot(name)[1]


# ---------------------------------------------------------------------------------------------------
# 1. Readings of the numbers (the same rules wrote the value column when the snapshot was built)
SMALL = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "eleven": 11, "twelve": 12}


def cardinal(s: str) -> float:
    """An English cardinal: 'eleven'."""
    return float(sum(SMALL.get(w, 0) for w in s.lower().replace("-", " ").split()))


def figure(s: str) -> float:
    """'1,000', '30.5', '.28', '-0.15' and full-width digits."""
    return float(unicodedata.normalize("NFKC", s).replace(",", "").replace("−", "-"))


def negative(s: str) -> float:
    """A figure after a minus sign printed apart from it (the Bank of Japan's table: '− 1.2')."""
    return -figure(s)


# the misreadings of the text layers that stand for a number, with the number they stand for
MISREAD = {"ist": 1}


def misread(s: str) -> float:
    return float(MISREAD[s])


def prepare(text: str) -> str:
    """A quotation ready for its figures: the Unicode compatibility forms (full-width digits)."""
    return unicodedata.normalize("NFKC", text)


# a figure with its sign: a minus that follows no letter, digit, bracket, per cent sign or point
FIGURES = re.compile(r"((?<![\w)%.,])[-−])?(\d[\d,]*(?:\.\d+)?|\.\d+)")
HOW = {"num": figure, "card": cardinal, "neg": negative, "ml": misread}
# id -> [(phrase, how)], in order. A phrase 'context|word' is searched as a whole and read from `word`. Rows not
# listed are read with all the figures of the prepared quotation, with their signs.
READINGS: dict[str, list[tuple[str, str]]] = {
    "f223_date": [("October |19", "num"), (", |1973", "num")],
    "f223_bills": [("about $|3", "num"), ("approach $|8", "num")],
    "f277_date": [("January |1974", "num")],
    "f277_receipts": [("about $|14", "num"), ("; $|14", "num"), ("; $|8", "num"), ("about $|5", "num")],
    "f273_date": [("December |28", "num"), (", |1973", "num")],
    "b74_1165": [("on |23", "num"), ("to $|11.65", "num"), ("from |ist", "ml"), ("January |1974", "num")],
    "bj_t35": [("昭和|48", "num"), ("昭和|49", "num"), ("昭和|50", "num"), ("昭和|53", "num"), ("昭和|54", "num"),
               ("昭和|55", "num"), ("実質国民総支出 |8.8", "num"), ("− |1.2", "neg"), (" |2.4", "num"), (" |5.1", "num"),
               (" |5.2", "num"), (" |4.8", "num")],
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




# the misreadings of the text layers, each printed in the quotation and named in the snapshot's notes with its row:
# (row, as printed in the quotation, the words of the notes that name it)
MISPRINTS = [("b74_1165", "P e r", "'P e r' for 'per'"),
             ("b74_1165", "ist", "'ist' for '1st'"),
             ("b74t_head", "c o u n t r i e s", "'c o u n t r i e s' for 'countries'"),
             ("b75_banks", "D u r i n g", "'D u r i n g' for 'During'"),
             ("b75_banks", "t o", "'t o' for 'to'"),
             ("b75_fiscal", "last , year", "'last , year' for 'last year'"),
             ("gd_title", "Alternative Responses of External Policy Supply to Shocks",
              "'Alternative Responses of External Policy Supply to Shocks' for 'Alternative Responses of Policy to "
              "External Supply Shocks'")]
N_QUOTED = 145
PARAPHRASED = "cordenneary1982_47"                # its cover forbids quotation: the rows say in their notes what is used


def check_readings(df: pd.DataFrame) -> None:
    src = meta()["sources"]
    n = 0
    for r in df.itertuples():
        assert r.file in src, (r.id, r.file)
        if r.file == PARAPHRASED and r.id != "cn_cover" and r.id != "cn_date":
            assert not r.quote and r.note.startswith("paraphrase: "), f"{r.id}: Corden and Neary are not quoted"
            assert re.fullmatch(r"PDF p\. \d+", r.juan), r.id
            continue
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
        assert f"{rid}:" in notes or f"{rid}," in notes or f"{rid} and" in notes, rid   # the notes say how it is read
    assert set(src) == set(df["file"]), sorted(set(src) ^ set(df["file"]))
    # the rows read on page images name a scan without a (usable) text layer
    for key, s in src.items():
        if s["format"] == "image":
            assert "without a text layer" in s["version"] or "a scan without" in s["version"], key
    print(f"ok {len(df)} rows; {len(MISPRINTS)} misreadings named in the notes")


# ---------------------------------------------------------------------------------------------------
# 2. The quotations of the text: each “…” is a rendering of words of rows
TRANSLATIONS = {
    "总有该抵抗的时候吧": ("f220_twenty",),
    "多半很小": ("f223_slight",),
    "非常高": ("f209_high",),
    "痛心": ("f216_pained",),
    "强烈反对": ("f271_opposed",),
    "剧烈而毫无道理": ("f273_tehran",),
    "简直是狂乱状态": ("bj_kyoran",),
    "狂乱物价": ("bj_kyoran",),
    "昭和 46—47 年的失败": ("bj_failure",),
    "过于乐观": ("bj_amaki",),
}
# the words of the source each rendering renders, in the quotation
KEYWORDS = {
    "f220_twenty": ["Is there some point at which they have to resist?"],
    "f223_slight": ["will probably be slight"],
    "f209_high": ['"very high."'],
    "f216_pained": ['"pained"'],
    "f271_opposed": ['"strongly opposed"'],
    "f273_tehran": ["drastic and unjustifiable"],
    "bj_kyoran": ["「まさに狂乱状態だ」", "狂乱物価"],
    "bj_failure": ["昭和46年～47年の失敗"],
    "bj_amaki": ["甘きに失し"],
}


def tex_text() -> str:
    return "\n".join(l for l in TEX.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("%"))


def text_quotations() -> list[str]:
    """The “…” of the text; the closing question is Chapter 48's and the chapter's own question is in the guide and at
    the end of the opening (both checked by guide() and opening())."""
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 48's question"
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
            assert column("file")[rid] != PARAPHRASED, rid                       # Corden and Neary are not quoted
    stale = set(TRANSLATIONS) - used
    assert not stale, f"listed but not in the text: {sorted(stale)}"
    for rid, words in KEYWORDS.items():
        for w in words:
            assert w in words_of(rid), f"{rid}: {w!r} not in the quotation"
    assert set(KEYWORDS) == {r for rs in TRANSLATIONS.values() for r in rs}
    for q in used:
        assert len(q.replace(" ", "")) <= 12, f"a long quotation: “{q}”"
    print(f"ok {n} quotations of the text found in the snapshot ({len(used)} distinct)")


# ---------------------------------------------------------------------------------------------------
# 3. Numbers: said() and the parts of the text it does not read
UNITS = {"万亿": 10 ** 12, "亿": 10 ** 8, "万": 10 ** 4}
AMOUNT = re.compile(r"(\d[\d,]*(?:\.\d+)?)(?:\s*(万亿|亿|万))?")
# what is not a number of the story: labels, citations, cross-references, the key equations (models() reads them), the
# sub- and superscripts of the math, the numbers of the parts of the examples ((1)-(3)), the figures' and tables' labels
# and the column specification of the table
MASKS = [re.compile(r"\\begin\{keyeq\}.*?\\end\{keyeq\}", re.DOTALL),
         re.compile(r"\\begin\{equation\}.*?\\end\{equation\}", re.DOTALL),
         re.compile(r"\\(?:label|cite|chref|secref|figref|tabref|exref|eqref|ref|nameref|url|fig)\{[^}]*\}"),
         re.compile(r"_\{[^}]*\}|_\d"),
         re.compile(r"\^\{\d+\}"),
         re.compile(r"（\d）"),
         re.compile(r"\{(?:fig|tab):[^}]*\}"),
         re.compile(r"\\begin\{tabularx\}\{\\linewidth\}\{[^\n]*")]
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
        quoted(f"{phrase[:60]!r}: {digits}{unit}", abs(float(v)), figure(digits) * scale, tol=tol + 1e-9 * scale)
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
    printed result (a result printed with \\% may be the left side in per cent)."""
    n = 0
    for m in re.finditer(r"\$([^$]*)\$", tex_text()):
        vals = []
        for part in re.split(r"=|\\approx", m.group(1)):
            e = part.replace("\\times", "*").replace("\\%", "").replace("^{2}", "**2").strip()
            if re.fullmatch(r"[\d.+\-*/() ]+", e) and re.search(r"\d", e):
                vals.append((e, eval(e), "\\%" in part))                     # noqa: S307 - digits and operators only
        for (_, v1, _), (e2, v2, pct) in zip(vals, vals[1:]):
            decimals = len(e2.split(".")[1]) if re.fullmatch(r"-?\d+\.\d+", e2) else 0
            tol = 0.5 * 10 ** -decimals + 1e-9
            assert abs(v1 - v2) <= tol or (pct and abs(100 * v1 - v2) <= tol), m.group(1)
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
    """The month a row prints by its English name."""
    has(rid, name)
    return [m.lower() for m in MONTHS].index(name.lower()) + 1


def year_in(key: str, pattern: str) -> int:
    return int(re.search(pattern, meta()["sources"][key]["version"]).group(1))


def report(key: str) -> int:
    """The year in which a BIS Annual Report's year ends (its title: '1st April 1973-31st March 1974')."""
    return year_in(key, r"31st March (\d{4})")


def showa(n: float) -> int:
    """昭和 n 年 as a year of the Western calendar."""
    return int(1925 + n)


def meiji(n: float) -> int:
    """明治 n 年 as a year of the Western calendar."""
    return int(1867 + n)


ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50}


def roman(s: str) -> int:
    v = [ROMAN[c] for c in s]
    return sum(-a if a < b else a for a, b in zip(v, v[1:] + [0]))


# ---------------------------------------------------------------------------------------------------
# The data: the Pink Sheet, the World Development Indicators, Penn World Table
G8 = ("USA", "JPN", "DEU", "FRA", "GBR", "ITA", "CAN", "CHE")          # the G7 and Switzerland, as Figure oil_g7
GULF = ("SAU", "KWT", "ARE", "QAT", "BHR", "OMN")                     # the triangles of Figure oil_curse
CPI, FUEL, FOOD, AGRI, MANF, RENTS = ("FP.CPI.TOTL.ZG", "TX.VAL.FUEL.ZS.UN", "TX.VAL.FOOD.ZS.UN", "TX.VAL.AGRI.ZS.UN",
                                      "NV.IND.MANF.ZS", "NY.GDP.TOTL.RT.ZS")
SPAN = (1970, 1985)                                                   # Figure oil_g7
SHOCKS = ((1973, 1974), (1979, 1980))                                 # the shading of Figures oil_price and oil_g7
PERIODS = ((1970, 1990), (1990, 2019))                                # Figure oil_curse


@lru_cache(maxsize=None)
def crude() -> pd.DataFrame:
    """year -> crude_nominal, crude_real (dollars a barrel; real: 2010 dollars)."""
    df = data("oil_pinksheet").set_index("year")
    assert df.index.is_unique and df.notna().all().all()
    return df


def nominal(y: int) -> float:
    return float(crude().loc[y, "crude_nominal"])


def real(y: int) -> float:
    return float(crude().loc[y, "crude_real"])


@lru_cache(maxsize=None)
def wdi_values() -> dict[tuple[str, str, int], float]:
    df = data("oil_wdi")
    out = {(r.indicator, r.countrycode, int(r.year)): float(r.value) for r in df.itertuples()}
    assert len(out) == len(df)
    return out


def wdi(ind: str, c: str, y: int) -> float:
    return wdi_values()[(ind, c, y)]


def cpi(c: str, y: int) -> float:
    return wdi(CPI, c, y)


@lru_cache(maxsize=None)
def pwt_rows() -> dict[tuple[str, int], tuple[float, float, float]]:
    """(country, year) -> (rgdpe, rgdpna, pop)."""
    df = data("oil_pwt")
    return {(r.countrycode, int(r.year)): (float(r.rgdpe), float(r.rgdpna), float(r.pop)) for r in df.itertuples()}


def growth(c: str, y: int) -> float:
    """The growth of real GDP at constant national prices (rgdpna) from y - 1 to y, per cent."""
    P = pwt_rows()
    return 100 * (P[(c, y)][1] / P[(c, y - 1)][1] - 1)


def per_head(c: str, a: int, b: int) -> float:
    """The log growth of rgdpna per head from a to b, per cent a year."""
    P = pwt_rows()
    return 100 * (np.log(P[(c, b)][1] / P[(c, b)][2]) - np.log(P[(c, a)][1] / P[(c, a)][2])) / (b - a)


def rent(c: str, y: int) -> float:
    return wdi(RENTS, c, y)


@lru_cache(maxsize=None)
def regression(a: int, b: int, drop: tuple[str, ...] = ()) -> dict:
    """Growth of real GDP per head from a to b (per cent a year) on the rents in a (% of GDP) and the log of rgdpe per
    head in a: every economy with all of them, OLS, classical and HC1 standard errors."""
    P, W = pwt_rows(), wdi_values()
    codes, X, y = [], [], []
    for (c, yr), (e0, n0, p0) in sorted(P.items()):
        if yr != a or c in drop or (RENTS, c, a) not in W or (c, b) not in P:
            continue
        if np.isnan([e0, n0, p0, P[(c, b)][1], P[(c, b)][2]]).any():
            continue
        codes.append(c)
        X.append([1.0, W[(RENTS, c, a)], np.log(e0 / p0)])
        y.append(per_head(c, a, b))
    X, y = np.array(X), np.array(y)
    n, k = X.shape
    XtXi = np.linalg.inv(X.T @ X)
    beta = XtXi @ X.T @ y
    res = y - X @ beta
    V = res @ res / (n - k) * XtXi
    meat = (X * res[:, None]).T @ (X * res[:, None])
    V1 = XtXi @ meat @ XtXi * n / (n - k)
    sd = X[:, 1].std(ddof=1)
    return dict(codes=codes, x=X[:, 1], y=y, lny=X[:, 2], beta=beta, n=n, b=beta[1], se=np.sqrt(V[1, 1]),
                se1=np.sqrt(V1[1, 1]), t=beta[1] / np.sqrt(V[1, 1]), t1=beta[1] / np.sqrt(V1[1, 1]),
                r2=1 - res @ res / ((y - y.mean()) @ (y - y.mean())), sd=sd, onesd=beta[1] * sd)


def fit_line(a: int, b: int, rents_: np.ndarray) -> np.ndarray:
    """The regression line of Figure oil_curse: at the mean log income of the start."""
    R = regression(a, b)
    return R["beta"][0] + R["beta"][1] * rents_ + R["beta"][2] * R["lny"].mean()


# ---------------------------------------------------------------------------------------------------
# The teaching models
EX = dict(alpha=0.5, beta=0.5, un=6.0, gbar=3.0, x=7.0, pi0=4.0, s1=4.0)   # ex:oil-paths and Figure oil_paths
EQ_CURVE = "\\pi_t=\\pi^{e}_t-\\alpha\\,(u_t-u^{n})+s_t .\\label{eq:oil-curve}"
EQ_CHOICE = ("\\sum_{t=1}^{T}(u_t-u^{n})=\\frac{\\pi_0-\\pi_T+\\sum_{t=1}^{T}s_t}{\\alpha} .\\label{eq:oil-choice}")
EQ_TOT = "\\frac{\\Delta Y}{Y}\\approx-\\omega\\,\\frac{\\Delta p_{o}}{p_{o}} ,\\label{eq:oil-tot}"
OKUN = "$u_t-u_{t-1}=-\\beta\\,(x_t-\\pi_t-\\bar g)$"


def paths(T: int, s1: float = EX["s1"], accommodate: bool = False, alpha: float = EX["alpha"],
          beta: float = EX["beta"], un: float = EX["un"], gbar: float = EX["gbar"], x: float = EX["x"],
          pi0: float = EX["pi0"]) -> dict[str, np.ndarray]:
    """Years 0..T of eq:oil-curve with adaptive expectations and the demand side of the text: nominal demand grows by x
    (not accommodating) or by inflation plus the trend (accommodating, unemployment held at its natural rate)."""
    pi, u, xs = [pi0], [un], [x]
    for t in range(1, T + 1):
        s = s1 if t == 1 else 0.0
        if accommodate:
            u.append(un)
            pi.append(pi[-1] + s)
            xs.append(pi[-1] + gbar)
        else:
            # pi_t = pi_{t-1} - alpha (u_t - un) + s, u_t = u_{t-1} - beta (x - pi_t - gbar), solved for pi_t
            p = (pi[-1] - alpha * (u[-1] - un) + alpha * beta * (x - gbar) + s) / (1 + alpha * beta)
            u.append(u[-1] - beta * (x - p - gbar))
            pi.append(p)
            xs.append(x)
    return dict(pi=np.array(pi), u=np.array(u), x=np.array(xs))


def dutch(pe: float, ps2: float | None = None, share: float = 0.5) -> dict[str, float]:
    """ex:oil-dutch: X_i = A_i sqrt(L_i), A_M = A_S = 1, one unit of labour, the wage equal in the three sectors,
    manufactures the numeraire; `share` of income spent on services. pe = p_E A_E. With ps2 given (p_S^2 held), only
    the resource movement effect."""
    if ps2 is None:
        ps2 = share / (1 - share) * (pe ** 2 + 1.0)
    tot = pe ** 2 + 1.0 + ps2
    L = dict(E=pe ** 2 / tot, M=1.0 / tot, S=ps2 / tot)
    return dict(**L, ps=np.sqrt(ps2), ps2=ps2, w=0.5 / np.sqrt(L["M"]), XM=np.sqrt(L["M"]))


def models() -> None:
    t = TEX.read_text(encoding="utf-8")
    assert EQ_CURVE in t and EQ_CHOICE in t and EQ_TOT in t and OKUN in t
    rng = np.random.default_rng(47)
    for _ in range(500):
        a, b, un, g, x, p0 = rng.uniform(0.1, 1.5), rng.uniform(0.1, 1.5), *rng.uniform(2, 8, 2), \
            *rng.uniform(1, 10, 2)
        s1 = rng.uniform(0.5, 8)
        P = paths(40, s1, False, a, b, un, g, x, p0)
        T = int(rng.integers(1, 40))
        s = np.r_[0, s1, np.zeros(39)]
        # eq:oil-curve holds every year with pi^e = pi_{t-1}; the demand side holds
        assert np.allclose(P["pi"][1:], P["pi"][:-1] - a * (P["u"][1:] - un) + s[1:])
        assert np.allclose(P["u"][1:] - P["u"][:-1], -b * (P["x"][1:] - P["pi"][1:] - g))
        # eq:oil-choice: the sum of unemployment above the natural rate, for any T
        assert np.isclose((P["u"][1:T + 1] - un).sum(), (p0 - P["pi"][T] + s[1:T + 1].sum()) / a)
        # accommodation: unemployment stays, inflation keeps the shock
        A = paths(10, s1, True, a, b, un, g, x, p0)
        assert np.allclose(A["u"], un) and np.allclose(A["pi"][1:], p0 + s1) and np.isclose(A["x"][1], p0 + s1 + g)
        # not accommodating, from a steady state (x = pi_0 + g): the year of the shock both rise (stagflation)
        S = paths(5, s1, False, a, b, un, g, p0 + g, p0)
        assert S["pi"][1] > p0 and S["u"][1] > un
        # eq:oil-tot: the import volume fixed, the extra payment over income is omega times the rise of the price
        po, dpo, M, Y = rng.uniform(1, 50), rng.uniform(0.1, 50), rng.uniform(1, 10), rng.uniform(100, 1000)
        assert np.isclose(-(po + dpo) * M / Y + po * M / Y, -(po * M / Y) * dpo / po)
        # ex:oil-dutch: the equilibrium conditions hold, and the two effects act as the text says
        pe0, pe1, sh = rng.uniform(0.2, 1), rng.uniform(1, 3), rng.uniform(0.2, 0.8)
        for pe_ in (pe0, pe1):
            D = dutch(pe_, share=sh)
            L = np.array([D["E"], D["M"], D["S"]])
            assert np.isclose(L.sum(), 1)
            p = np.array([pe_, 1.0, D["ps"]])                                    # p_i A_i
            assert np.allclose(0.5 * p / np.sqrt(L), D["w"])                     # one wage
            assert np.isclose(D["ps"] * np.sqrt(D["S"]), sh * (p * np.sqrt(L)).sum())   # the share spent on services
        D0, D1, R = dutch(pe0, share=sh), dutch(pe1, share=sh), dutch(pe1, ps2=dutch(pe0, share=sh)["ps2"], share=sh)
        assert R["M"] < D0["M"] and R["S"] < D0["S"] and R["E"] > D0["E"]       # resource movement: both lose labour
        assert D1["M"] < R["M"] and D1["S"] > R["S"] and D1["ps"] > D0["ps"]     # spending: services gain, M shrinks
        assert np.isclose(D1["S"], sh) and np.isclose(D0["S"], sh)                # this form: L_S back to the share
        assert np.isclose(D1["w"] / D0["w"], D1["ps"] / D0["ps"])                 # the wage rises with p_S
    print("ok the key equations and the claims made of them on 500 random draws")


# ---------------------------------------------------------------------------------------------------
# 4. The text, section by section
def guide(F, Y, Q):
    t = TEX.read_text(encoding="utf-8")
    assert f"\\guidequestion{{{GUIDE}}}" in t and GUIDE == PREV
    assert chapter("ch46_floating").rstrip().endswith(PREV)                     # 第 46 章交来的问题
    assert "\\guideprereq{\\chref{ch:naturalrate}\\enspace\\nameref{ch:naturalrate}；\\chref{ch:floating}\\enspace" \
           "\\nameref{ch:floating}}" in t
    said("用总供给冲击分析 1973 年与 1979 年的油价冲击", Y["f209_war"], showa(F["bj_7812"][6]))
    say("比较各国的政策应对（迁就或不迁就）与结果", "解释石油美元回流怎样埋下拉美债务危机")
    said("推导荷兰病模型（Corden \\& Neary 1982）", F["cn_date"][0])
    assert "\\chapterstub" not in t


def opening(F, Y, Q):
    T = F["f220_time"]
    m = month("f220_time", "October")
    assert T[2] == 12 and 0 < T[3] < 30 and T[4:] == T[2:4]                    # 12:10 p.m.: just after noon
    has("f220_time", "p.m.", "Secretary Kissinger presiding")
    said("1973 年 10 月 18 日中午刚过 12 点", T[1], m, T[0], T[2])
    W = F["f209_war"]
    assert month("f209_war", "October") == m and W[1] == T[1]
    has("f209_war", "Egypt and Syria", "surprise attack on Israel")
    said("12 天前，埃及与叙利亚突然进攻以色列", T[0] - W[0])
    has("fp_sisco", "Assistant Secretary of State for Near Eastern and South Asian Affairs")
    has("f220_sisco", "a little over $5 a barrel")
    said("油价从每桶 3 美元涨到 5 美元出头", *F["f220_sisco"])
    has("f220_accept", "no alternative but to really go along")
    has("f220_ten", "the next year")
    said("明年涨到 10 美元", F["f220_ten"][0])
    said("涨到 20 美元呢", F["f220_twenty"][0])
    has("fp_rush", "Deputy Secretary of State")
    has("f220_coal", "Coal", "cheaper")
    has("f220_early", "better to have a confrontation early")
    has("fp_casey", "Under Secretary of State for Economic Affairs")
    has("f220_casey", "what does a confrontation mean?", "Nobody in this Government")
    D = F["f223_date"]
    assert month("f223_date", "October") == m and D == [T[0] + 1, T[1]]          # 第二天
    has("f223_date", "Office of Economic Research")
    has("f223_cut", "not less than 5% a month")
    has("f223_us", "million b/d")
    said("阿拉伯产油国每月至少减产 5\\%，美国每天只从它们那里得到约 160 万桶石油", F["f223_cut"][0],
         F["f223_us"][0] * 1e6)
    said("西欧的石油消费有 70\\% 靠阿拉伯国家，日本的供给有 40\\% 靠它们", *F["f223_dep"])
    has("f223_bills", "billion", "approach $8 billion")
    said("美国与日本的石油进口账单各要增加约 30 亿美元，西欧接近 80 亿美元", F["f223_bills"][0] * 1e9,
         F["f223_bills"][1] * 1e9)
    has("f223_jobs", "no initial offsetting loss in jobs")
    B = F["bj_1223"]
    assert B[1] - m >= 2 and B[4] / B[3] > 2                                     # 两个多月后；一倍多
    has("bj_1223", "ペルシア湾岸6か国", "2倍以上")
    assert F["f273_tehran"][0] == B[2]
    has("f273_tehran", "announced in Tehran on December 23")
    said("12 月 23 日，海湾产油国在德黑兰宣布，把原油的公示价格再提高一倍多，到每桶 11.65 美元，1974 年 1 月起实行",
         B[1], B[2], B[4], B[6], B[7])
    has("f277_70", "Free World oil bill")
    said("1974 年 1 月，CIA 估计 1974 年自由世界的石油账单要多出 700 亿美元", F["f277_date"][0],
         month("f277_date", "January"), F["f277_70"][1], F["f277_70"][0] * 1e9)
    has("f277_loss", "Western Europe and Japan")
    said("在西欧与日本约合国民生产总值的 3\\%", F["f277_loss"][0])
    has("f277_cautious", "already high rates of inflation")
    assert paragraph("两个多月后").endswith(GUIDE)                              # the opening ends with the question


def world(F, Y, Q):
    S = F["f209_wsag"]
    assert S[1] == F["f209_war"][0]                                              # 开战当天
    has("f209_wsag", "9 a.m.", "Secretary of Defense", "possibility of an oil embargo")
    said("10 月 6 日开战当天上午 9 点", month("f209_wsag", "October"), S[1], S[0])
    has("fp_atherton", "Deputy Assistant Secretary of State for Near Eastern and South Asian Affairs")
    has("f209_key", "the key to the oil problem")
    has("f209_noplans", "no plans in the event of an embargo")
    has("f209_fix", "as would the Europeans and the Japanese")
    O = F["f209_oct7"]
    assert O[0] == S[1] + 1 and O[1] == 6                                         # 第二天傍晚（6:06 p.m.）
    has("f209_oct7", "p.m.")
    has("f209_nibble", "nibble us to death", "a helluva time to teach them the limits")
    B = F["bj_1016"]
    has("bj_1016", "ペルシア湾岸6か国", "突如", "アラビアン・ライト")
    said("10 月 16 日，海湾的 6 个产油国突然宣布提高阿拉伯轻质原油的公示价格", B[1], B[2], B[0])
    assert B[3] == 1 and round((B[5] / B[4] - 1) * 100) == B[6]
    said("每桶从 3.01 美元提到 5.12 美元，一下提高 70\\%", B[4], B[5], B[6])
    C = F["bj_1017"]
    assert C[0] == B[2] + 1                                                      # 第二天
    has("bj_1017", "緊急会議", "毎月5%ずつ")
    said("决定以 9 月的产量为基准，从 10 月起每月减产 5\\%", C[1], C[2], C[3])
    said("1972 年底 OAPEC 国家的石油产量约占全世界的 32\\%，出口占 55\\%", *F["bj_32"])
    has("f216_yamani", "over the course of one year by 5 percent per month", "informed the French")
    said("沙特会在一年里每月减产 5\\%", F["f216_yamani"][0])
    has("fp_yamani", "Saudi Petroleum Minister")
    A = F["f216_airlift"]
    has("f216_airlift", "wrote King Faisal")
    said("10 月 14 日，基辛格写信给费萨尔国王", month("f216_airlift", "October"), A[0])
    has("f216_pained", "October 16 reply")
    said("16 日，国王回信", F["f216_pained"][0])
    has("bj_embargo", "アメリカ、オランダ", "全面的に停止")
    said("从 10 月 20 日起", *F["bj_embargo"])
    said("11 月 4 日，OAPEC 宣布 11 月的产量比 9 月减少 25\\%，12 月再减 5\\%", *F["bj_1104"])
    H = F["hm_cut"]
    has("hm_cut", "mb/d")
    said("11 月阿拉伯产油国的产量比 9 月每天少了 440 万桶，相当于全世界产量的 7.5\\%", month("hm_cut", "November"),
         month("hm_cut", "September"), H[0] * 1e6, H[1])
    has("hm_defiance", "in defiance of the Arab states", "increased its oil production during the 1973-74 embargo")
    has("hm_offset", "offset only a small part")
    has("b74_85", "two days later", "85 per cent")
    said("12 月底提价两天以后，阿拉伯产油国决定把产量恢复到 9 月的 85\\%", month("b74_85", "December"),
         month("b74_85", "September"), F["b74_85"][0])
    has("b74_price", "price rather than quantity")
    has("fp_helms", "U.S. Ambassador to Iran from February 1973")
    has("f271_changed", "changed dramatically during this year")
    has("f271_staggered", "last spring", "keeping oil prices down", "this past summer", "doubling",
        "inflation in Iran")
    has("f271_shah", "I cannot get less for my oil than other countries")
    O = F["f271_opposed"]
    has("f271_opposed", "led by the Shah", "the Tehran meeting")
    said("其余的 OPEC 成员在国王带领下要每桶 10 到 14 美元", O[1], O[2])
    has("f271_faisal", "chewed Yamani out", "would hurt the world")
    has("f271_press", "same day", "sympathy for developing nations", "developed")
    M = F["f273_more"]
    assert F["f273_dec25"][0] - F["bj_1223"][2] == 2 and F["b74_85"][0] == 85     # 两天以后
    has("f273_more", "United Kingdom, France, Japan, Spain", "continue the embargo on the United States")
    said("两天以后，阿拉伯产油国又宣布，1974 年 1 月增产 10\\%", M[1], month("f273_more", "January"), M[0])
    has("fp_akins", "U.S. Ambassador to Saudi Arabia from October 1973")
    has("f271_akins", "Tehran was a catastrophe and Kuwait was an insult")
    has("f271_kuwait", "OAPEC meeting in Kuwait")
    has("fp_saqqaf", "Minister of State for Foreign Affairs")
    said("12 月 28 日，基辛格写信给沙特的外交国务大臣", month("f273_date", "December"), F["f273_date"][0])
    has("f273_nixon", "single out the United States for a continuing embargo", "puts President Nixon in an impossible "
                                                                              "position")
    has("bj_dollar", "ドル切下げ", "目減り")
    T = F["b74_take"]
    has("b74_take", '"take"')
    said("每桶所得从 1.75 美元升到 7 美元", *T)
    has("b74_cif", "c.i.f. price", "in Europe")
    said("同一种油运到欧洲的到岸价，从 3.65 美元升到 8.9 美元", *F["b74_cif"])
    cif = F["b74_cif"][1] / F["b74_cif"][0]
    assert T[1] / T[0] == 4 and 2 < cif < 3                                       # 翻了两番；一倍多
    said("日本是 70\\%，西欧平均约 60\\%，美国只有 10\\%", *F["b74_dep"], F["b74_dep_us"][0])
    has("b74_cpi", "nearly 4 per cent")
    said("在多数欧洲国家是 2\\% 到 3\\%，在日本接近 4\\%", *F["b74_cpi"])
    has("b74_cpi_us", "United States and Canada", "domestic energy")
    # the Pink Sheet
    D = {d["cell"] + d["sheet"]: d["text"] for d in data_meta("oil_pinksheet")["definitions"]}
    assert "Brent, Dubai and West Texas" in D["B7Description"]
    say("\\figref{fig:oil_price}画出世界银行的原油年均价，是布伦特、迪拜与西得克萨斯三种原油的平均")
    said("名义价格 1973 年是每桶 2.8 美元，1974 年是 11.0 美元", 1973, nominal(1973), 1974, nominal(1974))
    assert "real 2010 US dollars" in D["A2Annual Prices (Real)"]
    said("实际价格按 2010 年的美元计，从 9.1 美元升到 29.2 美元", 2010, real(1973), real(1974))
    assert "Manufacturers Unit Value Index (MUV)" in D["A4Definitions"] and "fifteen countries" in D["A6Definitions"]
    said("这个指数记的是 15 个国家出口的制造品", 15)
    said("第一次冲击使油价一年里涨到原来的 3 倍多", 3)
    assert 3 < real(1974) / real(1973) < 4
    assert all(real(1978) <= real(y) <= real(1974) for y in range(1974, 1979))     # 此后几年慢慢回落
    said("1978 年是 24.3 美元，第二次又从这里涨到 1980 年的 56.5 美元", 1978, real(1978), 1980, real(1980))
    said("原油的年均价，1960—2025 年，每桶美元，对数刻度", crude().index.min(), crude().index.max())
    said("名义价格与按 2010 年美元计的实际价格", 2010)
    said("阴影是 1973—1974 年与 1979—1980 年", *SHOCKS[0], *SHOCKS[1])
    # the second shock
    X = F["bj_7812"]
    has("bj_7812", "アブダビ", "54年中平均10%")
    said("1978 年 12 月，OPEC 在阿布扎比开会，决定 1979 年把标准油价从每桶 12.70 美元平均提高 10\\%", showa(X[0]), X[1],
         showa(X[6]), X[5], X[7])
    I = F["hm_iran"]
    has("hm_iran", "fall of 1978", "October 1978 and January 1979")
    said("1978 年秋天罢工蔓延到伊朗的石油业，到 1979 年 1 月伊朗的产量每天减少 480 万桶，约占当时世界产量的 7\\%", I[0],
         I[4], month("hm_iran", "January"), I[1] * 1e6, I[2])
    has("hm_third", "About a third", "Saudi Arabia")
    G = F["bj_geneva"]
    has("bj_june", "同月下旬に開かれるOPEC総会")
    assert G[0] > 20 and page("bj_june") == page("bj_geneva") and Y["bj_geneva"] == showa(X[6])   # 6 月下旬
    said("1979 年 6 月，OPEC 在日内瓦把标准油价从每桶 14.55 美元提到 18 美元", Y["bj_geneva"], F["bj_june"][0], G[3], G[4])
    K = F["bj_34"]
    assert round(K[2] / X[5], 1) == K[3]
    said("到 1981 年底，标准油价是每桶 34 美元，约为 1978 年底的 2.7 倍", showa(K[0]), K[2], showa(X[0]), K[3])
    has("b80_real", "in real terms", "same order of magnitude")
    said("BIS 1980 年说，这一次油价的实际涨幅与 1973—1974 年是同一个量级", report("bis1980_47"), F["b80_real"][0],
         1900 + F["b80_real"][1])
    said("按世界银行的年均价，1980 年是每桶 36.9 美元", 1980, nominal(1980))
    assert nominal(1986) < nominal(1980) / 2
    said("1986 年油价跌回 14.4 美元", 1986, nominal(1986))


def model(F, Y, Q):
    said("每让通胀多留 1 个百分点，累计的失业就少 $1/\\alpha$ 个百分点·年", 1, 1)
    has("b80_tax", "levies a tax on the oil-importing countries", "diminishes their real income")
    has("b74t_head", "Oil i m p o r t s in relation to GNP")
    de = F["b74t_de"][5]                                                         # the column of net oil imports in % of GNP
    said("油价上涨还有一层损失，与曲线无关。BIS 1980 年说", report("bis1980_47"))
    said("按 BIS 的表，1973 年这个比例在联邦德国是 1.6\\%", F["b74t_head"][0], de)
    cif = F["b74_cif"][1] / F["b74_cif"][0] - 1
    said("欧洲的到岸价涨了约 144\\%，多付的钱约合国民生产总值的 $1.6\\times1.44\\approx2.3\\%$", 100 * cif, de, cif, de * cif)
    said("CIA 估计西欧与日本约 3\\%", F["f277_loss"][0])
    J = F["bj_transfer"]
    has("bj_transfer", "124億ドル", "国民総支出のおおむね3%")
    said("1974 年日本进口原油多付了 124 亿美元，约合当时国民总支出的 3\\%", showa(J[0]), J[1] * 1e8, J[2])
    has("b80_painful", "how much to accommodate and how much to resist", "recapture")
    said("BIS 1980 年说，私人部门要夺回被油价侵蚀的实际收入", report("bis1980_47"))
    v = there("ch44_naturalrate", "可是失业在 7\\% 以上的 9 年里，1977、1980 与 1984 年的通胀仍在上升")
    said("失业在 7\\% 以上的 1977、1980 与 1984 年，美国的通胀仍在上升", v[0], *v[2:])
    said("1980 年油价比上年涨了约 19\\%，1977 年只涨了约 9\\%", 1980, 100 * (nominal(1980) / nominal(1979) - 1), 1977,
         100 * (nominal(1977) / nominal(1976) - 1))
    assert real(1977) == real(1976) and nominal(1984) < nominal(1983)             # 实际价格没有变；1984 年还跌了
    said("实际价格没有变，1984 年油价还跌了", 1984)
    said("油价只说明得了 1980 年", 1980)
    said("约合 GNP 的 2\\% 到 3\\%", F["bj_ratio"][1], F["f277_loss"][0])
    said("CIA 1973 年 10 月认为就业起初不受影响", F["f223_date"][1], month("f223_date", "October"))
    said("CIA 1974 年 1 月担心产出下降与失业增加", F["f277_date"][0], month("f277_date", "January"))
    has("f277_unless", "declining output", "increased unemployment")
    said("只有在 $s_t=0$ 时", 0)
    said("$s_t>0$ 时通胀与失业一起上升", 0)
    # ex:oil-paths
    E, P, A = EX, paths(80), paths(10, accommodate=True)
    assert E["x"] == E["pi0"] + E["gbar"]                                       # inflation steady at 4%
    said("设 $\\alpha=0.5$，$\\beta=0.5$，$u^{n}=6\\%$，$\\bar g=3\\%$，名义需求原来每年增长 7\\%，通胀稳定在 4\\%",
         E["alpha"], E["beta"], E["un"], E["gbar"], E["x"], E["pi0"])
    said("第 1 年来了一次冲击，$s_1=4$，以后 $s_t=0$", 1, E["s1"], 0)
    said("不迁就，名义需求仍增长 7\\%，头两年的通胀与失业是多少", E["x"])
    said("只让通胀最后停在 6\\%，又是多少", 6)
    said("第 1 年 $\\pi_1=4-0.5\\,(u_1-6)+4$，$u_1=6+0.5\\,(\\pi_1-4)$，解得 $\\pi_1=7.2$，$u_1=7.6$", 1, E["pi0"],
         E["alpha"], E["un"], E["s1"], E["un"], E["beta"], E["x"] - E["gbar"], P["pi"][1], P["u"][1])
    said("第 2 年同样解得 $\\pi_2=5.92$，$u_2=8.56$", 2, P["pi"][2], P["u"][2])
    assert abs(P["u"][-1] - E["un"]) < 0.01 and abs(P["pi"][-1] - E["pi0"]) < 0.01
    said("此后通胀继续回落，失业慢慢回到 6\\%", E["un"])
    said("失业守在 6\\%，通胀从 4\\% 升到 $4+4=8\\%$ 并停在那里，名义需求要增长 $8+3=11\\%$", E["un"], E["pi0"], E["pi0"],
         E["s1"], A["pi"][-1], A["pi"][-1], E["gbar"], A["x"][1])
    cum = (P["u"][1:] - E["un"]).sum()
    said("不迁就是 $(4-4+4)/0.5=8$ 个百分点·年，迁就是 0", E["pi0"], E["pi0"], E["s1"], E["alpha"], cum,
         (A["u"] - E["un"]).sum())
    said("通胀停在 6\\% 时是 $(4-6+4)/0.5=4$ 个百分点·年", 6, E["pi0"], 6, E["s1"], E["alpha"],
         (E["pi0"] - 6 + E["s1"]) / E["alpha"])
    said("蓝色实线是不迁就，名义需求每年增长 7\\%；琥珀色虚线是完全迁就，失业守在自然率 6\\%。第 1 年的供给冲击 $s_1=4$", E["x"],
         E["un"], 1, E["s1"])
    said("不迁就，第 1 年通胀升到 7.2\\%，失业升到 7.6\\%", 1, P["pi"][1], P["u"][1])
    assert int(np.argmax(P["u"])) == 3
    said("第 3 年失业最高，约 8.8\\%", 3, P["u"][3])
    k = int(np.argmax(P["pi"][2:] < E["pi0"])) + 2                              # the first year inflation is below 4%
    assert k == 4 and (P["u"][k:] < E["un"]).any() and (P["u"][k:] > E["un"]).any()
    said("此后通胀降到 4\\% 以下，失业在 6\\% 上下摆动着回来", E["pi0"], E["un"])
    said("迁就，失业一直是 6\\%，通胀从此是 8\\%", E["un"], A["pi"][-1])
    for t in range(1, 60):                                                       # inflation below 4%: unemployment falls
        if P["pi"][t] < E["pi0"]:
            assert E["x"] - P["pi"][t] > E["gbar"] and P["u"][t] < P["u"][t - 1]
    said("通胀降到 4\\% 以下以后，名义需求仍增长 7\\%", E["pi0"], E["x"])
    # the pitfall: Gordon
    has("gd_level", "but not the rate of inflation", "adaptivenonfarmexpectations")
    has("gd_cartel", "unbreakableoil cartel", "permanentreductionin supply")
    said("不一定。Gordon 1975 年分析了几种情形", Y["gd_level"])


def policy(F, Y, Q):
    y80, y75 = report("bis1980_47"), report("bis1975_47")
    has("b80_choice", "restraining demand", "sustain domestic demand and thus fuel price inflation")
    said("进口国面对两难。BIS 1980 年说", y80)
    U = F["b80_unanimous"]
    has("b80_unanimous", "far from unanimous", "for a while at least", "supporting domestic demand")
    said("BIS 说，1973—1974 年主要工业国远没有一致把对付通胀放在首位", U[0], 1900 + U[1])
    has("b80_restrictive", "Over the past year")
    has("b80_us", "even in the United States, where the need was greatest")
    has("b80_fiscal", "more restrictive")
    has("f277_choose", "balance of payments to worsen")
    said("CIA 1974 年 1 月也预料", F["f277_date"][0], month("f277_date", "January"))
    has("b75_fiscal", "the Netherlands and Sweden", "Canada and the United Kingdom")
    said("BIS 1975 年的年报记下了第一次的做法。1974 年，荷兰与瑞典先给了一些财政刺激", y75, y75 - 1)
    has("b75_eased", "Germany and the United States")
    has("b75_caution", "prompted caution")
    said("失业不变，通胀从 4\\% 升到 8\\% 并停住", EX["pi0"], EX["pi0"] + EX["s1"])
    said("累计多出 8 个百分点·年的失业", (paths(80)["u"][1:] - EX["un"]).sum())
    said("1973—1974 年多数主要工业国至少一度支持国内需求", U[0], 1900 + U[1])
    assert y80 == 1980                                                           # the year to March 1980
    said("1979—1980 年各国的货币政策明显偏紧", y80 - 1, y80)
    has("gd_unnatural", "food", "oil", "U.S. nonfarmworkers", "raisedthe rate of inflation")
    said("Gordon 1975 年说，1973—1974 年粮食与石油的减产", Y["gd_unnatural"], *F["gd_unnatural"])
    has("gd_garden", "differentfromthe traditionaltonic of demandrestriction")
    has("gd_rigid", "absolutelyrigid")
    has("gd_optimal", "accommodateboth the higher externalprice level and the originallevel of internaloutput")
    has("b80_growth", "going for growth", "stagflation trap")
    has("b80_tradeoff", "no long-run trade-off between growth and inflation")
    said("到了 1980 年，BIS 的看法很明确。它说，1970 年代想靠追求增长走出滞胀的陷阱", y80, F["b80_growth"][0])
    has("b80_wages", "with very few exceptions", "first half of the 1970s")
    said("除了很少几个例外，1979 年的货币工资与实际工资都比 1970 年代前半期涨得慢", *F["b80_wages"])
    said("工资与物价普遍螺旋上升的危险，比 1973—1974 年小", F["b80_spiral"][0], 1900 + F["b80_spiral"][1])
    # the G7 and Switzerland
    said("\\figref{fig:oil_g7}画出七国集团与瑞士 1970—1985 年的通胀与增长", *SPAN)
    c74 = sorted(G8, key=lambda c: -cpi(c, 1974))
    assert c74[:2] == ["JPN", "ITA"] and c74[-1] == "DEU"
    said("1974 年消费物价涨得最多的是日本，23.2\\%，其次是意大利的 19.2\\%", 1974, cpi("JPN", 1974), cpi("ITA", 1974))
    said("联邦德国只有 7.0\\%，瑞士是 9.8\\%", cpi("DEU", 1974), cpi("CHE", 1974))
    panel = {(c, y): cpi(c, y) for c in G8 for y in range(SPAN[0], SPAN[1] + 1)}
    assert max(panel, key=panel.get) == ("GBR", 1975)                            # 英国 1975 年最高
    said("英国 1975 年最高，是 24.2\\%", 1975, cpi("GBR", 1975))
    assert all(growth(c, 1974) < 0 for c in ("JPN", "GBR", "USA"))
    said("增长按 Penn World Table 的实际 GDP 计，1974 年日本下降 1.2\\%，英国下降 2.5\\%，美国下降 0.5\\%", 1974,
         growth("JPN", 1974), growth("GBR", 1974), growth("USA", 1974))
    said("七国集团与瑞士的消费物价涨幅与实际 GDP 增长率（\\%），1970—1985 年", *SPAN)
    said("虚线是 Penn World Table 10.01 按不变本国价格计的实际 GDP 的增长率", F["pwt_rgdpna"][0])
    assert "constant 2017 national prices" in data_meta("oil_pwt")["definitions"]["rgdpna"]
    assert cpi("JPN", 1980) < cpi("JPN", 1974) / 2                               # 日本的通胀低得多
    said("日本的通胀低得多，1979 年是 3.7\\%，1980 年是 7.8\\%", 1979, cpi("JPN", 1979), 1980, cpi("JPN", 1980))
    said("意大利与英国 1980 年仍有 21.1\\% 与 18.0\\%", 1980, cpi("ITA", 1980), cpi("GBR", 1980))
    for c in ("DEU", "CHE"):
        assert max(range(1976, SPAN[1] + 1), key=lambda y: cpi(c, y)) == 1981, c
    said("联邦德国与瑞士的通胀，最高分别是 1981 年的 6.3\\% 与 6.5\\%，美国 1980 年是 13.5\\%", 1981, cpi("DEU", 1981),
         cpi("CHE", 1981), 1980, cpi("USA", 1980))
    said("两国从 1975 年起公布货币增长的目标", 1975)
    said("按 Penn World Table，美国 1982 年下降 1.8\\%，加拿大下降 3.2\\%", 1982, growth("USA", 1982), growth("CAN", 1982))
    G = {(c, y): growth(c, y) for c in G8 for y in range(SPAN[0], SPAN[1] + 1)}
    assert min(G, key=G.get) == ("CHE", 1975)                                    # 瑞士下降得最急
    said("瑞士 1975 年的实际 GDP 下降 7.3\\%", 1975, growth("CHE", 1975))
    has("rich_drop", "oil price shock", "restrictive monetary policy", "by far the sharpest decline")
    said("\\chref{ch:monetarism}引 Rich 说产出下降 7.5\\%", F["rich_drop"][0])
    assert there("ch45_monetarism", "使产出下降 7.5\\%") == [F["rich_drop"][0]]
    said("Penn World Table 用的是按 2017 年不变本国价格计的实际 GDP", 2017)
    assert cpi("CHE", 1975) < cpi("CHE", 1974)
    said("瑞士的通胀 1975 年降到 6.7\\%，1979 年是 3.6\\%", 1975, cpi("CHE", 1975), 1979, cpi("CHE", 1979))
    K = there("ch42_eastasia", "1973 年以前的十年里日本实际 GDP 每年增长 8.9\\%")
    K2 = there("ch42_eastasia", "Krugman 说 1973—1992 年日本的人均 GDP 每年只增长 3\\%")
    said("\\chref{ch:eastasia}引 Krugman 的数，1973 年以前的十年里日本实际 GDP 每年增长 8.9\\%，1973—1992 年人均 GDP 每年只增长 3\\%",
         *K, *K2)
    R = F["bj_1221"]
    said("日本银行却在 1973 年 12 月把公定利率一次提高 2 个百分点", Y["bj_1221"], R[0], R[2])
    assert F["bj_0416"][1] < F["bj_june"][0]
    said("第二次，它在 1979 年 4 月就提高利率，比 6 月日内瓦的提价还早", showa(F["bj_0416"][0]), F["bj_0416"][1],
         F["bj_june"][0])
    has("f271_india", "developing world will be hardest hit", "trash barrel")
    said("\\cmprow{BIS 1980 年的说法}", y80)
    said("CIA 在 1974 年 1 月就预料到失业会增加", F["f277_date"][0], month("f277_date", "January"))
    has("f277_unless", "increased unemployment")


def japan(F, Y, Q):
    said("日本 · 1973—1980 · 两次石油危机", Y["bj_1221"], showa(F["bj_cpi89"][0]))
    has("bj_aichi", "愛知蔵相の急死")
    has("bj_fukuda", "前月下旬の内閣改造", "引締め強化", "貯蓄の優遇")
    assert page("bj_fukuda") == page("bj_1221") and Y["bj_fukuda"] == F["loc_aichi"][1]   # the month before December
    said("1973 年，大藏大臣爱知揆一（1907—1973）猝死，11 月下旬内阁改组", Y["bj_fukuda"], *F["loc_aichi"],
         F["bj_1221"][0] - 1)
    said("12 月 21 日，日本银行开临时政策委员会，决定把公定利率提高 2 个百分点，商业票据贴现率从年 7\\% 提到 9\\%，22 日实行",
         *F["bj_1221"])
    M = F["bj_meiji"]
    said("贴现率到 9\\%，是明治 19 年（1886 年）以后的第一次", M[0], M[1], meiji(M[1]))
    said("一次提高 2 个百分点也是从来没有过的", F["bj_never"][0])
    T = F["bj_toyokawa"]
    assert showa(T[0]) == Y["bj_1221"]
    has("bj_toyokawa", "取付け騒ぎ")
    said("12 月 14 日，爱知县的丰川信用金库发生挤兑", T[1], T[2])
    K = F["bj_kyoran"]
    has("bj_kyoran", "大阪市", "記者会見")
    said("1974 年 1 月 12 日，福田在大阪对记者说", showa(K[0]), K[1], K[2])
    assert page("bj_wpiavg") == page("bj_cpi")                                   # the same year, 昭和 49 年
    said("批发物价到 2 月比上年同月上涨 37.0\\%，1974 年平均上涨 31.3\\%", F["bj_wpi"][0], F["bj_wpi"][1],
         showa(F["bj_cpi"][0]), F["bj_wpiavg"][0])
    said("消费物价 1974 年平均上涨 24.5\\%", showa(F["bj_cpi"][0]), F["bj_cpi"][2])
    assert F["bj_t35"][7] == -F["bj_gne"][1]                                    # the table of p. 520 agrees
    said("实际国民总支出比上年减少 1.2\\%，是 1947 年以来第一次负增长", F["bj_gne"][1], showa(F["bj_gne"][2]))
    has("bj_transfer", "交易条件の悪化", "産油国")
    W = F["bj_wage"]
    has("bj_easy", "安易に応じた")
    said("1974 年的春季工资谈判，基本工资提高 32.9\\%，主要企业的夏季奖金比上年多 47\\%", showa(W[0]), W[1], W[2])
    U = F["bj_unemp"]
    said("完全失业者原来是 60 万到 70 万人，1975 年起急增到 100 万人上下", U[1] * 1e4, U[2] * 1e4, showa(U[3]), U[4] * 1e4)
    G = F["bj_governor"]
    assert G[3] == G[2] + 1                                                      # 次日
    said("1974 年 12 月 16 日，总裁任满退任，次日森永贞一郎（1910—1986）接任", showa(G[0]), G[1], G[2], *F["ndl_morinaga"])
    A = F["bj_apr78"]
    has("bj_apr78", "4月初め")
    said("1978 年 4 月初，它定下方针", showa(A[0]), A[3])
    has("bj_failure", "「不況」下であっても", "引締めの方向に転換")
    said("不重犯“昭和 46—47 年的失败”", *F["bj_failure"])
    has("bj_morinaga", "森永総裁", "これ以上緩和を加速しない")
    said("1979 年 1 月 23 日，森永说今后不再加大放松的力度", Y["bj_morinaga"], *F["bj_morinaga"])
    has("bj_amaki", "強い反省", "政策対応が遅れた")
    O = F["bj_0417"]
    assert np.isclose(O[1] - O[0], F["bj_0416"][3]) and O[2] == F["bj_0416"][2] + 1
    said("4 月 16 日，它把公定利率从 3.5\\% 提到 4.25\\%", F["bj_0416"][1], F["bj_0416"][2], O[0], O[1])
    has("bj_ms20", "比較的モデレート")
    said("上一次货币供给比上年增长 20\\% 多", F["bj_ms20"][0])
    C = F["bj_cpi89"]
    said("消费物价的涨幅，1974 年 2 月的高峰是 26.3\\%，这一次的高峰是 1980 年 9 月的 8.9\\%", showa(C[3]), C[4], C[5],
         showa(C[0]), C[1], C[2])
    T35 = F["bj_t35"]
    said("实际国民总支出 1979 年增长 5.2\\%，1980 年增长 4.8\\%", showa(T35[4]), T35[10], showa(T35[5]), T35[11])
    has("bj_initial", "初期条件")
    has("bj_early", "早めに金融政策")
    has("bj_wages", "労働生産性のすう勢")
    R = F["bj_ratio"]
    assert abs(R[3] - R[1]) < 0.5                                                # 冲击的规模差不多
    said("第一次是 2.0\\%，第二次是 2.2\\%", R[1], R[3])


def recycling(F, Y, Q):
    has("f277_95", "three and a half times as much as last year")
    said("CIA 1974 年 1 月估计，产油国这一年的石油收入约 950 亿美元，是上一年的 3.5 倍", F["f277_date"][0],
         month("f277_date", "January"), F["f277_95"][0] * 1e9, 3.5)
    A = F["f277_assume"]
    has("f277_assume", "current levels throughout 1974", "million barrels per day")
    said("世界石油出口与 1973 年差不多，约每天 3200 万桶", A[2], A[3] * 1e6)
    R = F["f277_receipts"]
    assert R[0] == R[1]
    has("f277_receipts", "Saudi Arabia", "Iran", "Venezuela", "each for Kuwait and Libya")
    said("沙特与伊朗各多收约 140 亿美元，委内瑞拉约 80 亿美元，科威特与利比亚各约 50 亿美元", R[0] * 1e9, R[2] * 1e9,
         R[3] * 1e9)
    has("f277_spend", "far exceed their spending capability")
    T, V = F["b75_ton"], F["b75_value"]
    has("b75_value", "milliard")
    said("BIS 1975 年的数字相近，OPEC 原油出口的平均价格从 1973 年的每吨约 20 美元升到 1974 年的 77 美元，石油出口额从约 320 亿美元升到 "
         "1150 亿美元", report("bis1975_47"), T[1], T[0], T[3], T[2], V[0] * 1e9, V[1] * 1e9)
    S = F["b75_surplus"]
    said("OPEC 国家的经常账户盈余 1974 年约 700 亿美元，上一年不到 50 亿美元", S[1], S[0] * 1e9, S[2] * 1e9)
    has("b75_ldc", "non-oil developing countries", "much more onerous")
    said("不产油的发展中国家的经常账户赤字从约 80 亿美元升到 250 亿美元以上", F["b75_ldc"][0] * 1e9, F["b75_ldc"][1] * 1e9)
    said("1974 年产油国的储备增加 364 亿美元", F["b75_reserves"][2], F["b75_reserves"][1] * 1e9)
    has("b75_placement", "dollar reserves in the United States", "sterling reserves", "Euro-currency market")
    said("它们在美国的美元储备增加约 100 亿美元，在英国的英镑储备增加约 50 亿美元", F["b75_placement"][0] * 1e9,
         F["b75_placement"][1] * 1e9)
    has("b75_controls", "late January 1974", "removal of controls on US capital outflows")
    said("1974 年 1 月下旬，美国取消了对资本流出的管制", F["b75_controls"][0], month("b75_controls", "January"))
    has("b75_banks", "loans to foreigners soared", "from surplus to deficit areas")
    said("这一年美国银行对外国的贷款猛增 177 亿美元", F["b75_banks"][1] * 1e9)
    y80 = report("bis1980_47")
    has("b80_harder", "more difficult")
    said("BIS 1980 年警告，通过国际银行业的回流可能比 1973 年提价以后更难", y80, F["b80_harder"][0])
    has("b80_burdened", "clean sheets", "third-world risks")
    said("它说，与 1974 年相比，银行不再是从干净的账本开始", F["b80_burdened"][0])
    said("1974 年以后，几类国家对国际金融市场的债务负担大大加重了", F["b80_debt"][0])
    has("b80_private", "one-third", "about one-half")
    said("从 1973 年的三分之一升到 1978 年的约一半", *F["b80_private"])
    has("b80_keen", "less keen")
    said("对 1974 年以来风险暴露增长很快的一些国家", F["b80_keen"][0])
    said("又怎样走到 1982 年的墨西哥危机", *there("ch51_latamdebt", "1982 年墨西哥危机"))


def dutch_disease(F, Y, Q):
    said("Corden 与 Neary 1982 年的模型把一国的经济分成三个部门", F["cn_date"][0])
    has("cn_three", "three sectors", "world prices", "non-traded")
    has("cn_rer", "relative price of non-traded to traded goods")
    has("cn_cases", "Australia", "Netherlands", "Britain, Norway")
    has("cn_effects", "resource movement effect", "spending effect")
    has("cn_direct", "direct de-industrialisation")
    has("cn_indirect", "indirect de-industrialisation")
    has("cn_hinges", "hinges")
    has("cn_britain", "spending effect")
    has("cn_trend", "falling for other reasons")
    has("cn_taxes", "taxes", "government")
    said("英国燃料出口占商品出口的比例从 1970 年的 2.6\\% 升到 1982 年的 20.3\\%", 1970, wdi(FUEL, "GBR", 1970), 1982,
         wdi(FUEL, "GBR", 1982))
    assert not any((MANF, "GBR", y) in wdi_values() for y in range(1970, 1983))
    say("这些年英国制造业的比例，世界发展指标没有数")
    H = {c: F[f"hu_t4_{c}"] for c in ("nl", "no", "uk")}
    assert max(H, key=lambda c: H[c][1]) == "uk"                                  # 三国里最多的
    # ex:oil-dutch and tab:oil-dutch
    D0, D1 = dutch(0.5), dutch(1.0)
    R = dutch(1.0, ps2=D0["ps2"])
    said("劳动总量为 1", 1)
    said("$A_M=A_S=1$，能源的价值生产率 $p_EA_E$ 从 0.5 升到 1", 1, 0.5, 1)
    said("可以解出 $L_S=0.5$", D0["S"])
    said("繁荣前，$p_S^{2}=0.25+1=1.25$，$L_E=0.25/2.5=0.1$，$L_M=1/2.5=0.4$", 0.25, 1, D0["ps2"], 0.25,
         0.25 + 1 + D0["ps2"], D0["E"], 1, 0.25 + 1 + D0["ps2"], D0["M"])
    said("繁荣后，$p_S^{2}=1+1=2$，$L_E=L_M=0.25$", 1, 1, D1["ps2"], D1["E"])
    said("$p_S$ 从 1.118 升到 1.414，升了约 26.5\\%", D0["ps"], D1["ps"], 100 * (D1["ps"] / D0["ps"] - 1))
    said("$p_S^{2}$ 仍是 1.25，三项之和是 $1.25+1+1=3.25$，$L_E=L_M=1/3.25\\approx0.308$，$L_S=1.25/3.25\\approx0.385$",
         R["ps2"], R["ps2"], 1, 1, 1 / R["M"], 1, 1 / R["M"], R["M"], R["ps2"], 1 / R["M"], R["S"])
    assert np.isclose(R["E"], R["M"])
    said("设物价指数里服务的权重是一半，$q$ 与 $p_S^{-0.5}$ 成正比，$q$ 降 $1-1/\\sqrt{1.265}\\approx11.1\\%$", 0.5, 1, 1,
         D1["ps"] / D0["ps"], 100 * (1 - (D0["ps"] / D1["ps"]) ** 0.5))
    said("繁荣前 & 0.100 & 0.400 & 0.500 & 1.118 & 0.791 & 0.632", D0["E"], D0["M"], D0["S"], D0["ps"], D0["w"], D0["XM"])
    said("只有资源转移效应 & 0.308 & 0.308 & 0.385 & 1.118 & 0.901 & 0.555", R["E"], R["M"], R["S"], R["ps"], R["w"], R["XM"])
    said("再加上支出效应 & 0.250 & 0.250 & 0.500 & 1.414 & 1.000 & 0.500", D1["E"], D1["M"], D1["S"], D1["ps"], D1["w"],
         D1["XM"])
    said("服务业的劳动最后回到 0.5", D1["S"])
    said("资源转移效应把制造业的劳动从 0.4 减到约 0.3", D0["M"], R["M"])
    assert np.isclose(D1["M"], 0.25)                                             # 再减到四分之一
    share_rm = (D0["XM"] - R["XM"]) / (D0["XM"] - D1["XM"])
    assert 0.5 < share_rm < 1                                                    # 一半多来自资源转移效应
    said("制造业的产出共减少约 21\\%", 100 * (1 - D1["XM"] / D0["XM"]))
    said("工资从约 0.8 升到 1，涨了约 26.5\\%", D0["w"], D1["w"], 100 * (D1["w"] / D0["w"] - 1))
    assert D1["E"] + D1["M"] + D1["S"] == 1 and 0.5 * (1.0 * D1["XM"] + D1["ps"] * np.sqrt(D1["S"])) > 0
    # the Netherlands
    said("荷兰 · 1959—1982 · 格罗宁根的天然气", F["hu_slochteren"][0], 1982)
    has("hu_slochteren", "Slochteren", "Groningen province", "a decade later", "North Sea")
    said("荷兰 1959 年在格罗宁根省发现了巨大的斯洛赫特伦天然气田", F["hu_slochteren"][0])
    has("hu_cover", "BIS WORKING PAPERS No. 13")
    has("bu_named", "Holland's poor record", "natural gas wealth")
    said("荷兰病得名于荷兰在 1960 年代管理天然气财富的不良记录", F["bu_named"][0])
    said("荷兰的制造业增加值占 GDP 的比例从 1970 年的 21.6\\% 降到 1982 年的 14.9\\%，燃料出口占商品出口的比例从 10.7\\% 升到 23.9\\%",
         1970, wdi(MANF, "NLD", 1970), 1982, wdi(MANF, "NLD", 1982), wdi(FUEL, "NLD", 1970), wdi(FUEL, "NLD", 1982))
    said("挪威的制造业比例从 17.8\\% 降到 11.9\\%，燃料出口从 0.9\\% 升到 52.3\\%", wdi(MANF, "NOR", 1970),
         wdi(MANF, "NOR", 1982), wdi(FUEL, "NOR", 1970), wdi(FUEL, "NOR", 1982))
    has("hu_t4", "variance decompositions", "Real energy price")
    for c, v in H.items():
        assert v[0] == 10 and sum(v[1:]) == 100, c                              # 10 quarters ahead; the shares add up
    said("10 个季度后，能源价格的冲击在荷兰解释 9\\%，在挪威解释 5\\%，在英国解释 23\\%", H["nl"][0], H["nl"][1], H["no"][1],
         H["uk"][1])
    has("hu_weak", "only weak support", "Most support", "is found in Norway")
    has("hu_nl", "very little systematic and long-term net adverse consequences")
    has("hu_episodic", "initial stages", "episodic and transitory", "vary widely")
    # Nigeria
    Dbt = F["bu_debt"]
    said("尼日利亚 · 1962—1983 · 石油繁荣", 1962, Dbt[6])
    said("燃料占商品出口的比例 1962 年是 10.3\\%，1970 年是 58.1\\%，1974 年是 93.0\\%", 1962, wdi(FUEL, "NGA", 1962), 1970,
         wdi(FUEL, "NGA", 1970), 1974, wdi(FUEL, "NGA", 1974))
    said("食品的比例从 1962 年的 64.5\\% 降到 1974 年的 5.1\\%，农业原料从 16.6\\% 降到 1.0\\%", 1962, wdi(FOOD, "NGA", 1962),
         1974, wdi(FOOD, "NGA", 1974), wdi(AGRI, "NGA", 1962), wdi(AGRI, "NGA", 1974))
    has("bu_lag", "saved and invested abroad", "absorbed the entire oil windfall")
    said("1973 与 1974 年的大笔盈余先存在了国外，此后政府的开支迅速增加，到 1976 年吃掉了全部的石油横财", *F["bu_lag"])
    has("bu_sixfold", "six fold", "federation and states capital expenditure")
    said("1977 年联邦与各州的资本开支是 1970 年的 6 倍", *F["bu_sixfold"], 6)
    has("bu_waste", "too hastily", "waste and corruption")
    said("1980 年代初油价下跌，债务随之而来", Dbt[0])
    has("bu_debt", "public and publicly guaranteed external debt", "almost exhausted")
    said("1981—1983 年，公共与公共担保的外债从 43 亿美元增加到 112 亿美元，外汇储备从 100 亿美元降到 12.3 亿美元", Dbt[5],
         Dbt[6], Dbt[1] * 1e9, Dbt[2] * 1e9, Dbt[3] * 1e9, Dbt[4] * 1e9)
    has("bu_shift", "non-tradeables", "(agriculture)", "services sectors", "decline in traditional export industries")


def test(F, Y, Q):
    has("sw_period", "1970 and 1989")
    said("Sachs 与 Warner 1995 年用 1970—1989 年各国的数据作了回归", Y["sw_coef"], F["sw_period"][1], F["sw_period"][2])
    has("sw_sxp", "primary-product exports to GDP in 1970")
    said("系数是 $-6.920$，t 值是 $-3.28$", *F["sw_coef"])
    assert np.isclose(F["sw_coef"][0] * F["sw_sd"][2], F["sw_093"][0], atol=0.005)
    said("这个比例的标准差约是 13 个百分点，高出一个标准差，人均增长每年约低 0.9 个百分点", 100 * F["sw_sd"][2],
         F["sw_093"][0])
    has("wdi_rents_def", "the sum of oil rents")
    R1, R2 = regression(*PERIODS[0]), regression(*PERIODS[1])
    R1g, R2g = regression(*PERIODS[0], GULF), regression(*PERIODS[1], GULF)
    said("1970—1990 年有 114 个经济体，租金比例每高 1 个百分点，人均增长每年低约 0.1 个百分点，t 值约是 $-4.1$", *PERIODS[0],
         R1["n"], 1, R1["b"], R1["t"])
    assert abs(R1["onesd"] - F["sw_093"][0]) < 0.1                               # 与 Sachs 和 Warner 的结果相近
    said("租金比例的标准差约 8.0 个百分点，高一个标准差，增长每年低约 0.9 个百分点", R1["sd"], R1["onesd"])
    assert abs(R1["t1"]) > 1.96                                                  # 仍然显著
    said("改用对异方差稳健的标准误，t 值约是 $-2.2$", R1["t1"])
    said("可这个回归只解释了各国增长差异的约 13\\%", 100 * R1["r2"])
    said("1990—2019 年有 159 个经济体，系数只有约 $-0.02$，高一个标准差只低约 0.3 个百分点", *PERIODS[1], R2["n"], R2["b"],
         R2["onesd"])
    assert set(GULF) <= set(R2["codes"]) and abs(R2g["t"]) < 1.96 < abs(R2["t"])   # 不再显著
    said("去掉 6 个海湾国家，t 值降到约 $-1.6$", len(GULF), R2g["t"])
    rents90 = [rent(c, 1990) for c in GULF]
    g90 = [per_head(c, *PERIODS[1]) for c in GULF]
    assert min(rents90) >= 36 > min(rents90) - 1
    said("1990 年海湾 6 国的租金都在 GDP 的 36\\% 以上，此后人均增长每年在 $-1.5\\%$ 到 1.7\\% 之间", 1990, len(GULF), None,
         min(g90), max(g90))
    in70 = [c for c in GULF if c in R1["codes"]]
    assert abs(R1g["b"] - R1["b"]) < 0.01                                        # 系数几乎不变
    said("1970—1990 年的样本里只有 4 个海湾国家", *PERIODS[0], len(in70))
    top = sorted(R1["codes"], key=lambda c: -rent(c, 1970))[:10]
    assert np.median([per_head(c, *PERIODS[0]) for c in top]) < np.median(R1["y"])   # 多半长得慢
    assert any(per_head(c, *PERIODS[0]) > 3 for c in top)                       # 也有长得快的
    said("赞比亚 1970 年的租金约占 GDP 的 36.5\\%，此后 20 年人均每年下降约 2.1\\%", 1970, rent("ZMB", 1970), 20,
         per_head("ZMB", *PERIODS[0]))
    said("沙特约 25.6\\%，人均每年下降约 1.0\\%", rent("SAU", 1970), per_head("SAU", *PERIODS[0]))
    said("(a) 1970—1990 年；(b) 1990—2019 年", *PERIODS[0], *PERIODS[1])
    said("数据：世界发展指标（NY.GDP.TOTL.RT.ZS）与 Penn World Table 10.01", F["pwt_rgdpna"][0])
    E = F["sw_exceptions"]
    has("sw_exceptions", "Malaysia and Mauritius", "top quartile", "Botswana would also probably be included")
    said("1970—1992 年资源依赖最高的四分之一里，只有马来西亚与毛里求斯人均增长每年在 2\\% 以上", E[3], 1900 + E[4], E[2])
    has("sw_manufacturing", "manufacturing exports rather than resource-led growth")
    said("马来西亚 1970 年的租金约占 GDP 的 17\\%，此后 20 年人均每年增长约 4.8\\%", 1970, rent("MYS", 1970), 20,
         per_head("MYS", *PERIODS[0]))
    said("博茨瓦纳 1970 年的租金只占 GDP 的约 3\\%，此后 20 年人均每年增长约 9.0\\%", 1970, rent("BWA", 1970), 20,
         per_head("BWA", *PERIODS[0]))
    assert rent("NOR", 1970) < 1
    said("挪威 1970 年的租金不到 GDP 的 1\\%", 1970, 1)
    said("到 1990 年，挪威的租金是 8.0\\%，此后人均每年增长约 1.5\\%", 1990, rent("NOR", 1990), per_head("NOR", *PERIODS[1]))
    assert real(1980) > 3 * real(1970) and real(1990) < real(1980) / 1.5 and real(2019) > real(1990)
    said("1970—1990 年包含了油价的暴涨与暴跌，1990—2019 年的油价大体在上涨", *PERIODS[0], *PERIODS[1])


def debate(F, Y, Q):
    has("bk_abstract", "not nearly as essential", "neither a theoretical presumption", "even in the absence of supply "
                                                                                        "shocks")
    said("Barsky 与 Kilian 2001 年说，油价大涨在 1970 年代滞胀的因果机制里", Y["bk_abstract"], F["bk_abstract"][0])
    said("弗里德曼 1976 年也说光凭石油危机解释不了通胀与失业一起上升", 1976)
    assert "friedman1976" in TEX_OF("ch44_naturalrate")
    said("Hamilton 2011 年说", F["hm_copyright"][0])
    has("hm_geo", "geopolitical events")
    has("hm_eleven", "All but one of the 11 postwar recessions")
    said("战后美国的 11 次衰退，除 1960 年的一次以外", *F["hm_eleven"])
    has("hm_some", "at least some postwar recessions")
    has("bgw_perse", "per se, were not a major cause")
    has("bgw_policy", "in some cases, nearly all")
    has("bgw_both", "nonmoney, nonoil disturbances")
    said("Bernanke、Gertler 与 Watson 1997 年认为", Y["bgw_perse"])
    said("2000 年代的经验又添了一层", 2000)
    assert real(2008) > real(1980)
    said("2008 年的油价是每桶 94.3 美元，高过 1980 年的 56.5 美元", 2008, real(2008), 1980, real(1980))
    said("那几年却没有 1970 年代那样的滞胀", 1970)
    has("bg_define", "cumulative change in the (log) price of oil above 50 percent", "more than four quarters")
    said("把对数油价累计上涨 50\\% 以上、持续四个季度以上的情形算作大的石油冲击，得到 1973、1979、1999 与 2002 年开始的四次",
         F["bg_define"][0], *F["bg_episodes"])
    has("bg_part", "only account for a fraction")
    said("他们说，油价只解释了 1970 年代波动的一部分", F["bg_part"][0])
    has("bg_smaller", "decreased considerably over time", "no smaller")
    has("bg_four", "good luck", "smaller share of oil in production", "more flexible labor markets",
        "improvements in monetary policy")
    has("bg_all", "all four have played an important role")
    said("他们给出 2000 年代不同的四个原因", 2000)
    said("本书在 1970—1990 年的数据里也看到了，1990—2019 年就弱得多", *PERIODS[0], *PERIODS[1])
    has("mmt_grabber", "grabber friendly", "producer friendly")
    said("Mehlum、Moene 与 Torvik 2002 年认为，关键在制度", Y["mmt_grabber"])
    has("mmt_losers", "Nigeria, Zambia, Sierra Leone, Angola, Saudi Arabia, and Venezuela", "Korea, Taiwan, Hong Kong "
                                                                                             "and Singapore")
    has("mmt_winners", "Botswana, Canada, Australia, and Norway")
    has("mmt_jump", "jump directly to the conclusion")
    has("bu_volatility", "rather than Dutch Disease effects")
    has("bu_third", "third most volatile", "out of 90 countries")
    has("bu_tax", "acts as a tax on investment in traded goods production")
    said("他们说，在 90 个国家里，尼日利亚的贸易条件波动排第三", F["bu_third"][0])


def TEX_OF(name: str) -> str:
    return (ROOT / "zh" / f"{name}.tex").read_text(encoding="utf-8")


def deeper(F, Y, Q):
    src = meta()["sources"]
    docs = sorted(int(m_.group(1)) for k in src for m_ in [re.fullmatch(r"frus36d(\d+)_47", k)] if m_)
    vol = roman(re.search(r"Volume ([IVXL]+)", src["frus36d209_47"]["version"]).group(1))
    has("fp_list", "1969-1976, Volume XXXVI")
    said("本章读了 1969—1976 年第 36 卷的第 209、216、220、223、271、273、277 号文件与人名表", *F["fp_list"][:2], vol, *docs)
    assert "omits parts" in src["frus36d223_47"]["version"] and "summary and the introduction only" in \
        src["frus36d277_47"]["version"]
    said("CIA 1973 年 10 月的备忘录与 1974 年 1 月的文件都只收了节录", F["f223_date"][1], month("f223_date", "October"),
         F["f277_date"][0], month("f277_date", "January"))
    has("b74_posted", "70 per cent.", "$5.11")
    said("10 月 16 日的公示价格，日本银行记作 5.12 美元，BIS 1974 年的年报记作 5.11 美元", F["bj_1016"][1],
         F["bj_1016"][2], F["bj_1016"][5], report("bis1974_47"), F["b74_posted"][2])
    assert F["bj_1223"][4] == F["b74_1165"][1] and F["f271_1160"][0] == F["bj_1223"][2]
    said("12 月 23 日的价格，日本银行与 BIS 都记作 11.65 美元，FRUS 的编者注记作 11.60 美元", F["bj_1223"][1],
         F["bj_1223"][2], F["b74_1165"][1], F["f271_1160"][1])
    K, X = F["bj_34"], F["bj_7812"]
    has("bj_34", "約2.7倍")
    said("日本银行算出第二次冲击使油价涨了约 2.7 倍，指的是 34 美元与 12.70 美元之比，即涨到原来的 2.7 倍", K[3], K[2], X[5],
         K[2] / X[5])
    said("BIS 的年报读的是 1974、1975 与 1980 年的扫描本", report("bis1974_47"), report("bis1975_47"),
         report("bis1980_47"))
    assert "第6巻" in src["boj614img_47"]["version"]
    said("日本银行的《日本银行百年史》第 6 卷也没有", 6)
    said("Sachs 与 Warner 的起点年，摘要与正文一处说是 1971 年，另一处说是 1970 年，正文用 1970 年", F["sw_abstract"][0],
         F["sw_sxp"][0], F["sw_period"][1])
    assert F["sw_sd"][0] == F["sw_abstract"][0]
    has("cn_cover", "NOT FOR QUOTATION WITHOUT PERMISSION OF THE AUTHOR")
    said("Rich 说瑞士 1975 年的产出下降 7.5\\%，Penn World Table 是 7.3\\%", F["rich_drop"][1], F["rich_drop"][0],
         growth("CHE", 1975))
    u74 = there("ch44_naturalrate", "1974 年通胀跳到 11.0\\%")
    assert round(cpi("USA", 1974), 2) == 11.05 and round(cpi("USA", 1974), 1) != u74[1]
    said("美国 1974 年的通胀，世界发展指标是 11.1\\%，\\chref{ch:naturalrate}按总统经济报告写作 11.0\\%，四舍五入以前是 11.05\\%",
         1974, cpi("USA", 1974), u74[1], cpi("USA", 1974))
    said("日本银行的行史只写了 1974 年底退任的总裁的姓", showa(F["bj_governor"][0]))
    D = {d["cell"] + d["sheet"]: d["text"] for d in data_meta("oil_pinksheet")["definitions"]}
    upd = re.fullmatch(r"Updated on (\w+) (\d+), (\d{4})", D["A4Annual Prices (Nominal)"])
    has("ps_link", "November 2026")
    said("世界银行的年度工作簿印的更新日期是 2026 年 9 月 2 日，网页上的链接却写作 2026 年 11 月", int(upd.group(3)),
         MONTHS.index(upd.group(1)) + 1, int(upd.group(2)), F["ps_link"][0], MONTHS.index("November") + 1)
    said("数值与 1974 年等年份的通行数字相合", 1974)
    has("wdi_rents_def", "oil rents, natural gas rents, coal rents", "mineral rents, and forest rents")


def legacy(F, Y, Q):
    assert "\\chapter{2021—2023 年通胀}" in TEX_OF("ch74_inflation21")
    m62 = there("ch62_moderation", "用数据描述 1984—2007 年产出与通胀波动的下降")
    assert m62[0] < 2000 < m62[1]
    said("2000 年代产油国的巨额盈余在\\chref{ch:moderation}，2021—2023 年的能源冲击在\\chref{ch:inflation21}", 2000, 2021,
         2023)
    said("按世界银行的实际价格，1998 年每桶只有 15.9 美元，2012 年是 95.3 美元，2020 年又跌到 42.1 美元", 1998, real(1998),
         2012, real(2012), 2020, real(2020))
    assert real(1998) == min(real(y) for y in range(1986, 2026))                # 1986 年以后最低
    said("它自己把这归于记取了 1971—1972 年的教训", showa(F["bj_failure"][0]), showa(F["bj_failure"][1]))
    said("BIS 1980 年也说，靠追求增长走不出滞胀", report("bis1980_47"))
    has("bu_more", "more volatile than oil income")


def takeaways(F, Y, Q):
    B = F["bj_1016"]
    said("1973 年 10 月，海湾产油国把公示价格提高 70\\%，OAPEC 宣布每月减产 5\\%。12 月 23 日的德黑兰会议又把价格提到 11.65 美元",
         Y["f209_war"], B[1], B[6], F["bj_1017"][3], F["bj_1223"][1], F["bj_1223"][2], F["bj_1223"][4])
    say("沙特反对，伊朗国王带头")
    said("BIS 说，1973—1974 年多数工业国至少一度支持需求", F["b80_unanimous"][0], 1900 + F["b80_unanimous"][1])
    said("日本第二次先紧缩，通胀高峰从 26.3\\% 降到 8.9\\%", F["bj_cpi89"][5], F["bj_cpi89"][2])
    said("1974 年产油国的经常账户盈余约 700 亿美元", F["b75_surplus"][1], F["b75_surplus"][0] * 1e9)
    said("BIS 1980 年警告，银行已经背着沉重的第三世界风险", report("bis1980_47"))
    said("资源诅咒在 1970—1990 年的数据里明显，在 1990—2019 年弱得多", *PERIODS[0], *PERIODS[1])


def selfcheck(F, Y, Q):
    said("若冲击是 $s_1=2$，不迁就时累计多出多少失业", 2)
    said("净石油进口占 GNP 的 2\\%，油价涨 150\\%", 2, 150)
    said("若 $p_EA_E$ 从 0.5 升到 1.5，繁荣后 $L_M$ 是多少", 0.5, 1.5)
    said("Sachs 与 Warner 的系数是 $-6.920$，资源依赖高出 0.05，人均增长每年约低多少", F["sw_coef"][0], 0.05)
    said("1973 年的公示价格从 3.01 美元提到 5.12 美元，涨了多少", Y["f209_war"], F["bj_1016"][4], F["bj_1016"][5])
    P2, A2 = paths(80, s1=2), paths(10, s1=2, accommodate=True)
    said("\\item $(4-4+2)/0.5=4$ 个百分点·年，通胀停在 $4+2=6\\%$。", EX["pi0"], EX["pi0"], 2, EX["alpha"],
         (P2["u"][1:] - EX["un"]).sum(), EX["pi0"], 2, A2["pi"][-1])
    said("\\item $2\\times1.5=3\\%$ 的 GNP。", 2, 1.5, 100 * 0.02 * 1.5)                # eq:oil-tot
    D = dutch(1.5)
    said("\\item $p_S^{2}=2.25+1=3.25$，$L_M=1/6.5\\approx0.154$。", 2.25, 1, D["ps2"], 1, 1 / D["M"], D["M"])
    said("\\item $6.920\\times0.05\\approx0.35$ 个百分点。", -F["sw_coef"][0], 0.05, -F["sw_coef"][0] * 0.05)
    said("\\item $5.12/3.01-1\\approx70\\%$。", F["bj_1016"][5], F["bj_1016"][4], 1, F["bj_1016"][6])


def ending(F, Y, Q):
    T = F["f220_time"]
    said("回到 1973 年 10 月 18 日的例会", T[1], month("f220_time", "October"), T[0])
    has("f220_twenty", "Is there some point at which they have to resist?")
    assert tex_text().rstrip().endswith("（本书的解读）。" + NEXT)
    assert f"\\guidequestion{{{NEXT}}}" in chapter("ch48_ratex")


def figures_data() -> None:
    """What the figures and their captions assert of their data."""
    C = crude()
    assert C.index.min() == 1960 and C.index.max() == 2025 and len(C) == 66
    assert (C["crude_nominal"] > 0).all() and (C["crude_real"] > 0).all()        # a log scale
    for c in G8:
        for y in range(SPAN[0], SPAN[1] + 1):
            cpi(c, y), growth(c, y)                                              # every point of Figure oil_g7
    P = paths(12)
    assert len(P["pi"]) == 13
    for a, b in PERIODS:
        R = regression(a, b)
        assert len(R["codes"]) == R["n"] and np.isfinite(fit_line(a, b, np.array([0.0, 50.0]))).all()
    print(f"ok the data of the figures: {len(C)} years of the oil price; {len(G8)} economies x "
          f"{SPAN[1] - SPAN[0] + 1} years; samples of {regression(*PERIODS[0])['n']} and {regression(*PERIODS[1])['n']}")


# ---------------------------------------------------------------------------------------------------
# 5. The book
# the life dates: words -> (row of the birth year, index), (row of the death year, index), row of the name, name
LIVES = {"Henry Kissinger，1923—2023": (("loc_kissinger", 0), ("loc_kissinger", 1), "loc_kissinger", "Kissinger, Henry"),
         "Ahmad Zaki Yamani，1930—2021": (("gnd_yamani_born", 0), ("gnd_yamani", 0), "gnd_yamani_name",
                                         "Yamani, Ahmad Zaki"),
         "Faisal，1906—1975": (("loc_faisal", 0), ("loc_faisal", 1), "loc_faisal", "Faisal, King of Saudi Arabia"),
         "Mohammad Reza Pahlavi，1919—1980": (("loc_shah", 0), ("loc_shah", 1), "loc_shah",
                                             "Mohammad Reza Pahlavi, Shah of Iran"),
         "爱知揆一（1907—1973）": (("loc_aichi", 0), ("loc_aichi", 1), "loc_aichi", "Aichi, Kiichi"),
         "福田赳夫（1905—1995）": (("loc_fukuda", 0), ("loc_fukuda", 1), "loc_fukuda", "Fukuda, Takeo"),
         "森永贞一郎（1910—1986）": (("ndl_morinaga", 0), ("ndl_morinaga", 1), "ndl_morinaga", "森永,貞一郎")}
# what other chapters tell: (words of this chapter, chapter where it is told, words there)
EVENTS = [("先回到\\chref{ch:naturalrate}的式~\\eqref{eq:naturalrate-curve}", "ch44_naturalrate",
           "\\pi_t=\\pi^{e}_t-\\alpha\\,(u_t-u^{n}) .\\label{eq:naturalrate-curve}"),
          ("这就是\\textbf{滞胀}（stagflation），\\chref{ch:phillips}讲过这个名字的来历", "ch38_phillips",
           "高通胀与高失业并存的现象得了“滞胀”这个难听的名字"),
          ("仿照\\chref{ch:phillips}里奥肯的经验关系", "ch38_phillips", "奥肯的经验关系至今用来把失业与产出缺口连起来"),
          ("预期沿用\\chref{ch:naturalrate}的适应性预期，$\\pi^{e}_t=\\pi_{t-1}$", "ch44_naturalrate",
           "按去年的通胀预期今年，$\\pi^{e}_t=\\pi_{t-1}$"),
          ("与式~\\eqref{eq:naturalrate-sacrifice}相比", "ch44_naturalrate",
           "\\sum_{t=1}^{T}(u_t-u^{n})=\\frac{\\pi_0-\\pi_T}{\\alpha} .\\label{eq:naturalrate-sacrifice}"),
          ("\\chref{ch:naturalrate}发现，失业在 7\\% 以上的 1977、1980 与 1984 年，美国的通胀仍在上升", "ch44_naturalrate",
           "可是失业在 7\\% 以上的 9 年里，1977、1980 与 1984 年的通胀仍在上升"),
          ("\\chref{ch:naturalrate}讲过，弗里德曼 1976 年也说光凭石油危机解释不了通胀与失业一起上升", "ch44_naturalrate",
           "石油危机同时冲击了七国，可他说，五年的平均与逐年的数据都表明，光凭它解释不了这个现象"),
          ("美国 1974 年的通胀，世界发展指标是 11.1\\%，\\chref{ch:naturalrate}按总统经济报告写作 11.0\\%", "ch44_naturalrate",
           "1974 年通胀跳到 11.0\\%，失业还只有 5.6\\%\\cite{erp2000}"),
          ("\\chref{ch:floating}的结尾讲过，以美元收款的产油国，美元贬值就等于油卖得便宜了", "ch46_floating",
           "产油国若以美元收款，美元贬值就等于石油卖得便宜了（本书的解读）"),
          ("两国从 1975 年起公布货币增长的目标，这是\\chref{ch:monetarism}的题目", "ch45_monetarism",
           "联邦德国的联邦银行也从 1975 年起每年公布货币目标"),
          ("两国从 1975 年起公布货币增长的目标，这是\\chref{ch:monetarism}的题目", "ch45_monetarism",
           "瑞士国家银行在 1974 年底定下 1975 年 M1 增长 6\\% 的目标"),
          ("\\chref{ch:monetarism}引 Rich 说产出下降 7.5\\%，那是石油冲击加上紧缩的货币政策的结果", "ch45_monetarism",
           "1975 年，石油冲击加上紧缩的货币政策，使产出下降 7.5\\%，是二战以后最急的下降"),
          ("\\chref{ch:eastasia}引 Krugman 的数", "ch42_eastasia", "Krugman 给的数相近，1973 年以前的十年里日本实际 GDP 每年增长 8.9\\%"),
          ("它对应\\chref{ch:external}的式~\\eqref{eq:external-real}里 $q$ 的下降", "ch05_external",
           "q=\\frac{e\\,P^{f}}{P},\\label{eq:external-real}"),
          ("（3）按\\chref{ch:external}的实际汇率，$q$ 降多少？", "ch05_external", "\\label{eq:external-real}"),
          ("又怎样走到 1982 年的墨西哥危机，在\\chref{ch:latamdebt}", "ch51_latamdebt",
           "追踪石油美元回流、浮动利率银团贷款与 1982 年墨西哥危机"),
          ("美联储这几年的紧缩在\\chref{ch:credibility}", "ch49_credibility", "用沃尔克反通胀（1979—1982）估算牺牲率"),
          ("紧缩靠的是让人们相信通胀会降下来，这是\\chref{ch:credibility}的题目", "ch49_credibility", "并讨论可信度的作用"),
          ("实际经济周期理论把衰退看作对技术冲击的反应，在\\chref{ch:rbc}", "ch53_rbc", "衰退会不会只是经济对技术冲击的最优反应？"),
          ("三方程模型里的供给冲击在\\chref{ch:consensus}", "ch55_consensus", "用模型分析需求冲击与供给冲击下的政策取舍"),
          ("2000 年代产油国的巨额盈余在\\chref{ch:moderation}", "ch62_moderation", "全球储蓄过剩论与全球失衡之争"),
          ("2021—2023 年的能源冲击在\\chref{ch:inflation21}", "ch74_inflation21", "分解需求、能源与供应链、劳动市场对通胀的贡献"),
          ("央行该不该看穿供给冲击，在\\chref{ch:fragmentation}", "ch78_fragmentation", "供给冲击频繁时，货币政策“看穿冲击”的条件"),
          ("\\chref{ch:greekroman}讲过雅典的劳里昂银矿，横财是分掉还是投资", "ch07_greekroman", "劳里昂的白银是分掉还是造船"),
          ("\\chref{ch:silver}讲过西班牙王室靠忽多忽少的白银过日子", "ch13_silver", "西班牙王室依赖一种忽多忽少、来自地下的收入"),
          ("人们会预期政策时，政策还有效吗？用历史数据估计的模型，为什么会在政策改变后失效？", "ch48_ratex",
           "\\guidequestion{人们会预期政策时，政策还有效吗？用历史数据估计的模型，为什么会在政策改变后失效？}")]
# the chapters this one names, and where their labels are
LATER = {"ch:naturalrate": "ch44_naturalrate", "ch:floating": "ch46_floating", "ch:phillips": "ch38_phillips",
         "ch:credibility": "ch49_credibility", "ch:monetarism": "ch45_monetarism", "ch:eastasia": "ch42_eastasia",
         "ch:latamdebt": "ch51_latamdebt", "ch:external": "ch05_external", "ch:rbc": "ch53_rbc",
         "ch:consensus": "ch55_consensus", "ch:moderation": "ch62_moderation", "ch:inflation21": "ch74_inflation21",
         "ch:fragmentation": "ch78_fragmentation", "ch:greekroman": "ch07_greekroman", "ch:silver": "ch13_silver"}
# the chapters that point here
POINTERS = ("ch07_greekroman", "ch13_silver", "ch38_phillips", "ch42_eastasia", "ch44_naturalrate", "ch45_monetarism",
            "ch46_floating", "ch51_latamdebt")


def book(F, Q):
    """Life dates and what other chapters tell."""
    t = tex_text()
    for words, ((rb, ib), (rd, id_), name_row, name) in LIVES.items():
        assert words in t, words
        assert f"{F[rb][ib]:.0f}—{F[rd][id_]:.0f}" in words, (words, rb, rd)
        assert name in Q[name_row], (name_row, Q[name_row])                     # the person of the record
        assert column("file")[rb] == column("file")[rd] == column("file")[name_row], words   # one record
        COVERED.append(words)
    has("gnd_yamani", "Männlich")
    has("fp_yamani", "Yamani, Ahmad Zaki")                                       # FRUS spells the name the same way
    for here, ch, there_ in EVENTS:
        assert here in t, here
        assert there_ in chapter(ch), (ch, there_)
    named = set(re.findall(r"\\chref\{(ch:[^}]+)\}", t)) | set(re.findall(r"\\nameref\{(ch:[^}]+)\}", t))
    assert named == set(LATER), sorted(named ^ set(LATER))
    for label, ch in LATER.items():
        assert f"\\label{{{label}}}" in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (label, ch)
    for ch in POINTERS:
        assert re.search(r"\\(?:chref|ref|nameref)\{ch:oil\}", chapter(ch)), ch
    print(f"ok {len(LIVES)} life dates, {len(EVENTS)} statements of other chapters, {len(LATER)} other chapters named")


# the bibliography item of each document of the four snapshots (the authority records: loc47)
ITEM_OF = {**{f"frus36d{n}_47": "frus47" for n in (209, 216, 220, 223, 271, 273, 277)}, "frus36persons_47": "frus47",
           "bis1974_47": "bis1974", "bis1975_47": "bis1975", "bis1980_47": "bis1980", "bisterms_47": "bis1975",
           "hutchison1990img_47": "hutchison1990", "gordon1975_47": "gordon1975", "bgw1997_47": "bgw1997",
           "hamilton2011_47": "hamilton2011", "blanchardgali2007_47": "blanchardgali2007",
           "barskykilian2001img_47": "barskykilian2001", "sachswarner1995img_47": "sachswarner1995",
           "cordenneary1982_47": "cordenneary1982", "mmt2002_47": "mmt2002", "budina2007_47": "budina2007",
           "okrbudina_47": "budina2007", "rich2003_47": "rich2003",
           "boj614img_47": "boj1986b", "boj621img_47": "boj1986b", "boj63img_47": "boj1986b",
           "bojcopyright_47": "boj1986b",
           **{k: "wdi47" for k in ("wdicpi_47", "wdifuel_47", "wdifood_47", "wdiagri_47", "wdimanf_47", "wdirents_47",
                                   "wdimeta_47", "wdicountries_47")},
           "wbcommodity_47": "pinksheet2026", "wblicenses_47": "pinksheet2026", "pinksheet_47": "pinksheet2026",
           "pwtrecord_47": "pwt1001", "pwt1001_xlsx": "pwt1001"}
# the items of other chapters, outside the block: the same copies (the same SHA-256); the block asks the editor to add
# the pages of Chapter 47
SHARED = {"bis1974": "第 46 章", "rich2003": "第 45 章", "pwt1001": "第 40 章"}
SHARED_COPY = {"bis1974": "bis1974_47", "rich2003": "rich2003_47"}        # the PDFs whose pages the block's note lists
# the sources of each item whose pages it names (printed pages and PDF pages), by PDF
PAGES = {"bis1975": (("bis1975_47",),), "bis1980": (("bis1980_47",),), "hutchison1990": (("hutchison1990img_47",),),
         "gordon1975": (("gordon1975_47",),), "bgw1997": (("bgw1997_47",),), "hamilton2011": (("hamilton2011_47",),),
         "blanchardgali2007": (("blanchardgali2007_47",),), "barskykilian2001": (("barskykilian2001img_47",),),
         "sachswarner1995": (("sachswarner1995img_47",),), "cordenneary1982": (("cordenneary1982_47",),),
         "mmt2002": (("mmt2002_47",),), "budina2007": (("budina2007_47",),),
         "boj1986b": (("boj614img_47",), ("boj621img_47",), ("boj63img_47",))}


def runs(ps) -> str:
    """'2、7、8、25、26' from page numbers: ranges joined by '—', two neighbours by '、'; a page with a letter
    ('34a', a page the paper inserts) stands apart, after the page of its number."""
    keys = sorted(set(ps), key=lambda p: (int(re.match(r"\d+", str(p)).group()), str(p)))
    out, rs = [], []
    for p in keys:
        if isinstance(p, int) and rs and isinstance(rs[-1][1], int) and p == rs[-1][1] + 1:
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
            m_ = re.match(r"pp?\. (\d+)([a-z]?)(?:-(\d+))?\b", r.juan)
            if m_ and m_.group(2):
                ps.append(m_.group(1) + m_.group(2))                            # 'p. 34a'
            elif m_:
                ps += range(int(m_.group(1)), int(m_.group(3) or m_.group(1)) + 1)
    return runs(ps)


def pdf(srcs) -> str:
    """The PDF pages of the rows of these sources."""
    ps = []
    for r in _rows().itertuples():
        if r.file in srcs:
            for a, b in re.findall(r"PDF pp?\. (\d+)(?:-(\d+))?", r.juan):
                ps += range(int(a), int(b or a) + 1)
    return runs(ps)


def pages_words(srcs) -> str:
    return f"第 {printed(srcs)} 页（PDF 第 {pdf(srcs)} 页）" if printed(srcs) else f"PDF 第 {pdf(srcs)} 页"


def block() -> tuple[str, dict[str, str], dict[str, str]]:
    """The bibliography block of Chapter 47, its items and all items of the bibliography."""
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    start = bib.index("% ---- 第 47 章")
    following = re.search(r"^% ---- 第 \d+ 章", bib[start + 1:], re.MULTILINE)
    end = start + 1 + following.start() if following else bib.index("\\end{thebibliography}")
    text = bib[start:end]
    assert bib.index("% ---- 第 46 章") < start
    items = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", text)}
    allitems = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", bib)}
    return text, items, allitems


def documents() -> dict[str, dict]:
    """Every document of the four snapshots of data/fetch/oil47.py."""
    out = dict(meta()["sources"])
    for name in ("oil_pinksheet", "oil_wdi", "oil_pwt"):
        for key, src in data_meta(name)["documents"].items():
            assert key not in out or out[key]["sha256"] == src["sha256"], key
            out[key] = src
    return out


def witnesses(F, Q):
    """The licences and the bibliography block of the chapter."""
    lic = meta()["license"]
    lic_rows = ("bis_reuse", "bis_translation", "bis_original", "boj_terms", "hm_copyright", "bg_copyright",
                "sw_copyright", "bk_copyright", "cn_cover", "okr_license", "rich_repro", "ps_using", "wb_cc", "wb_attr",
                "wdi_license", "pwt_license", "pwt_cite")
    for rid in lic_rows:
        assert re.search(r"\(rows? [^)]*\b" + rid + r"\b", lic), rid
        assert words_of(rid) in lic, rid
    for words in ("17 U.S.C. § 105", "no photographs are used", "CC0"):
        assert words in lic, words
    for name, rows in (("oil_pinksheet", ("wb_cc", "wb_attr")), ("oil_wdi", ("wb_cc", "wb_attr", "wdi_license")),
                       ("oil_pwt", ("pwt_license", "pwt_cite"))):
        for rid in rows:                                                         # the data snapshots quote them too
            assert words_of(rid) in data_meta(name)["license"].replace("\\\"", "\""), (name, rid)
    # the NBER notices: "© year by the authors" of the first page
    for rid, src, year in (("hm_copyright", "hamilton2011_47", 2011), ("bg_copyright", "blanchardgali2007_47", 2007),
                           ("sw_copyright", "sachswarner1995img_47", 1995), ("bk_copyright", "barskykilian2001img_47",
                                                                               2001)):
        assert Q[rid].startswith(f"© {year} by ") and "All rights reserved. Short sections of text, not to exceed two " \
            "paragraphs" in Q[rid] and column("file")[rid] == src, rid
        assert pdf_page(rid) <= 2, rid
    # the bibliography block of the chapter
    text, items, allitems = block()
    assert FETCH in text and all(n in text for n in ("oil_facts", "oil_pinksheet", "oil_wdi", "oil_pwt"))
    assert f"共 {len(items)} 条" in text
    unescape = lambda s: re.sub(r"\\([$%&_#~])", r"\1", re.sub(r"\\url\{([^}]*)\}", r"\1", s)).replace("--", "-")  # noqa: E731
    for rid, keys in (("bis_reuse", ("bis1975",)), ("bis_translation", ("bis1975",)), ("bis_original", ("bis1975",)),
                      ("boj_terms", ("boj1986b",)), ("hm_copyright", ("hamilton2011",)),
                      ("bg_copyright", ("blanchardgali2007",)), ("sw_copyright", ("sachswarner1995",)),
                      ("bk_copyright", ("barskykilian2001",)), ("cn_cover", ("cordenneary1982",)),
                      ("okr_license", ("budina2007",)), ("wb_cc", ("pinksheet2026",)), ("wb_attr", ("pinksheet2026",)),
                      ("wdi_license", ("wdi47",))):
        for key in keys:
            assert words_of(rid) in unescape(items[key]), (rid, key)
    for key in ("bis1975", "bis1980", "hutchison1990"):
        assert "the original content can be found at" in items[key], key
        assert "不是国际清算银行的官方译文" in items[key] and "This translation is not an official BIS translation" \
            in items[key], key
        assert "以国际清算银行为来源" in items[key], key
    assert "公有领域" in items["frus47"] and "17 U.S.C. § 105" in items["frus47"]
    assert "来源：日本银行" in items["boj1986b"] and "CC BY 3.0 IGO" in items["budina2007"]
    for key in ("pinksheet2026", "wdi47"):
        assert "CC BY 4.0" in items[key] and "本书" in items[key], key
    assert "只转述，不引原文" in items["cordenneary1982"] and "Economic Journal" in items["cordenneary1982"]
    assert "公共数据" in items["loc47"] and "CC0" in items["loc47"]
    # every document is named by its URL and SHA-256 (the authority records by their URLs)
    for key, s in documents().items():
        auth = key.startswith(("loc_", "gnd_", "ndl_"))
        item = "loc47" if auth else ITEM_OF[key]
        assert unescape(s["url"]) in unescape(allitems[item]), key
        if auth:
            continue
        if item in SHARED:
            assert s["sha256"] in allitems[item] or s["sha256"] in text, key    # the same copy, or named in the note
        else:
            assert s["sha256"] in items[item], key
    assert set(ITEM_OF) == {k for k in documents() if not k.startswith(("loc_", "gnd_", "ndl_"))}
    # the pages of each work, as the snapshot's rows have them
    for key, groups in PAGES.items():
        for srcs in groups:
            assert pages_words(srcs) in items[key], (key, pages_words(srcs))
    assert {k for g in PAGES.values() for s in g for k in s} == {k for k, s in meta()["sources"].items()
                                                                 if s["format"] in ("pdf", "image")} - set(SHARED_COPY.values())
    for key, src in SHARED_COPY.items():                                        # the editor adds them
        assert f"% {key}：第 47 章用{pages_words((src,))}" in text, (key, pages_words((src,)))
    for key, ch in SHARED.items():
        assert f"共用条目 {key} 见{ch}" in text or f"{key} 见{ch}" in text, key
    for words, (_, _, name_row, name) in LIVES.items():
        assert name.split(",")[0] in items["loc47"], name_row
    # the titles of the works as the documents print them
    for rid, key, words in (("hu_cover", "hutchison1990", "BIS WORKING PAPERS No. 13"),
                            ("fp_list", "frus47", "Volume XXXVI, Energy Crisis, 1969-1974"),
                            ("bu_series", "budina2007", "Policy Research Working Paper 4256"),
                            ("cn_date", "cordenneary1982", "CP-82-58"),
                            ("cn_date", "cordenneary1982", "September 1982")):
        has(rid, words)
        assert words.lower() in unescape(items[key]).lower(), (rid, key)
    keys = set(allitems)
    cited = {k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", tex_text()) for k in c.split(",")}
    assert cited <= keys, sorted(cited - keys)
    assert set(items) == cited - set(SHARED) and set(SHARED) <= cited, sorted(set(items) ^ (cited - set(SHARED)))
    print(f"ok {len(cited)} works cited, {len(items)} in the bibliography block of Chapter 47")


def counts() -> None:
    """The editor's limits: “不能” at most about a dozen; the forbidden words; who decided and who paid stated; the two
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
    for words in ("谁作的决定？10 月 16 日，海湾的 6 个产油国突然宣布", "德黑兰的提价是谁定的？",
                  "谁作的决定？两次冲击的选择不同", "代价落在谁身上？首先是进口国的消费者", "其次是失业的人",
                  "再次是不产油的发展中国家", "代价落在谁身上？日本银行说，石油提价恶化了贸易条件",
                  "代价落在谁身上？不产油的发展中国家的经常账户赤字", "谁作的决定？Budina、Pang 与 van Wijnbergen 说",
                  "代价落在谁身上？他们说，开支的压力", "花多少、花在哪里、什么时候花，是政府的决定"):
        assert words in main_, words
    assert main_.count("代价落在谁身上？") == 4 and main_.count("谁作的决定？") == 3
    # documents are not the subjects of sentences: the author is named
    for bad in ("报告说", "演讲说", "演说说", "论文说", "书里说", "表说", "网页说", "年报说", "备忘录说", "电报说"):
        assert bad not in main_, bad
    # at most one source frame (按……的说法、转述……) in a sentence
    frame = re.compile(r"按[^，。；“”]{0,40}?的(?:说法|转述|解释|估计|叙述|描述|判断|概括|统计|数|记录|计算|整理|表)")
    for s in re.split(r"(?<=[。？！])|\n", re.sub(r"“[^”]*”", "“”", main_)):
        assert len(frame.findall(s)) <= 1, s
    # the two debates are left open
    part = main_[main_.index("\\section{争论}"):main_.index("\\section{今天还剩什么}")]
    debates = part.split("\\subsubsection{")[1:]
    assert len(debates) == 2
    for d in debates:
        assert d.rstrip().endswith("至今没有定论。"), d[-80:]
    # the inferences are marked
    for words, k in (("本书的解读", 40), ("本书的计算", 25), ("本书的推导", 12), ("本书的核对", 6), ("本书的概括", 2)):
        assert main_.count(words) >= k, (words, main_.count(words))
    # sentences: one semicolon at most
    prose = re.sub(r"\\datasource\{[^\n]*", "", main_)
    for s in re.split(r"(?<=[。？！])|\n", re.sub(r"“[^”]*”", "“”", prose)):
        assert s.count("；") <= 1, s
    # the boxes the editor asks for
    assert t.count("\\begin{compare}") == 2 and t.count("\\begin{case}") == 3 and t.count("\\begin{pitfall}") == 1
    assert t.count("\\begin{deeper}[史料说明]") == 1 and t.count("\\begin{keyeq}") == 2
    assert t.count("\\begin{equation}") == 1 and t.count("\\begin{example}") == 2 and t.count("\\fig{") == 4
    assert t.count("\\begin{table}") == 1
    assert t.count(GUIDE) == 2
    # the neighbours' topics: a clause or a sentence each
    for label in ("ch:ratex", "ch:credibility", "ch:latamdebt", "ch:rbc", "ch:consensus", "ch:moderation",
                  "ch:inflation21", "ch:fragmentation", "ch:monetarism"):
        assert t.count(f"\\chref{{{label}}}") <= 2, label
    # what other chapters own is not retold: the Volcker disinflation, the debt crisis, the Plaza
    for bad in ("牺牲率", "布雷迪", "广场协议", "沃尔克"):
        assert bad not in t, bad


def main() -> None:
    df = _rows()
    F, Y, Q = facts(), years(), quotes()
    check_readings(df)
    check_text(df)
    for part in (guide, opening, world, model, policy, japan, recycling, dutch_disease, test, debate, deeper, legacy,
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
