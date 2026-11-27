"""Chapter 46 (布雷顿森林解体与浮动汇率): every number and every quotation in zh/ch46_floating.tex.

    python3 checks/check_ch46.py

Inputs:
  floating_facts                quotations of the chapter's sources with their page: Nixon's address of 15 August 1971
                                and remarks of 18 December 1971 (Public Papers, American Presidency Project); FRUS
                                1969-1976 vol. III documents 164, 165, 168, 211, 221 and vol. XXXI documents 12, 14, 33,
                                35 (history.state.gov); the BIS Annual Reports of 1972, 1973, 1974 and 1976 (text layers
                                and page images); Dornbusch (JPE 1976) and Meese and Rogoff (JIE 1983), third-party
                                copies read to verify only; IFDP 184 (cover); the Bank of Japan's history, vol. 6 (page
                                images); the Economic Planning Agency's white paper of 1972; the Council resolution of
                                21 March 1972 (OJ C 38, French); Rich (ECB WP 236); Powell (Bank of Canada, 2005); five
                                series of the BIS Data Portal; the terms of the BIS, the Bank of Japan, the Cabinet
                                Office, EUR-Lex, the ECB and the Bank of Canada; the authority records of the Library of
                                Congress. data/fetch/verify_web_quotes.py checks the quotations against the documents;
                                data/fetch/floating46.py fetches them
  floating_bis_1959_1985        monthly averages of the yen, the mark (from the euro series), the Swiss franc and
                                sterling against the dollar, and the consumer prices of the five countries (BIS)
  zh/ch05, ch36, ch37, ch42,    the statements of other chapters that this chapter repeats (EVENTS); the stubs of
  ch45                          Chapters 47-49, 58 and 60 for what is handed on (LATER)

This script

1. reads the numbers of every row from its quotation by the rules of READINGS and compares them with the value
   column; the misreadings of the text layers are listed in MISPRINTS;
2. finds every “…” of the text among the renderings of TRANSLATIONS, and the words of the source each one renders
   (KEYWORDS) in the rows; the quotations stay short;
3. checks each number of the text with said(): the phrase is in the text and each number is the value of a row, a
   teaching input, or arithmetic on them (the example of eq:floating-overshoot, the volatilities of the BIS series);
   every Arabic number of the text must lie in a phrase said() read (coverage()); every chain a = b of plain
   arithmetic in the text's math holds (arithmetic());
4. checks the key equations as printed, the claims made of them on random numbers, the data of the figures
   (figsrc/fig_ch46.py imports series(), volatility(), path() and the teaching inputs from here), the life dates
   against the authority records, what other chapters tell, the licences and the bibliography block of Chapter 46;
5. lists the rows no "% 据:" anchor of the text names (common.anchors).

Set CH46_TEX to a scratch copy of the chapter to run the checks on it (mutation tests).
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

TEX = Path(os.environ.get("CH46_TEX", ROOT / "zh" / "ch46_floating.tex"))   # a scratch copy for mutation tests
GUIDE = "美元与黄金为什么脱钩？浮动汇率为什么会“超调”？"
PREV = GUIDE                                        # Chapter 45's NEXT
NEXT = "油价冲击为什么同时推高通胀和失业？产油国为什么会被“资源诅咒”？"   # Chapter 47's question (its stub)
FETCH = "data/fetch/floating46.py"


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
    df, m = load_snapshot("floating_facts", dtype=str, keep_default_na=False)
    assert 46 in m["used_in"] and m["fetch"] == FETCH
    assert df["id"].is_unique
    return df


@lru_cache(maxsize=None)
def meta() -> dict:
    return load_snapshot("floating_facts")[1]


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
    """A year the version of a source names."""
    return int(re.search(pattern, meta()["sources"][key]["version"]).group(1))




@lru_cache(maxsize=None)
def series() -> pd.DataFrame:
    """The BIS monthly series: month, the four exchange rates (units of currency per dollar; the mark from the euro
    series) and the five consumer price indices."""
    df, m = load_snapshot("floating_bis_1959_1985")
    assert 46 in m["used_in"] and m["fetch"] == FETCH
    df["month"] = pd.PeriodIndex(df["month"], freq="M")
    return df.set_index("month")


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


def french(s: str) -> float:
    """A French decimal comma: '2,25'."""
    return float(s.replace(",", "."))


def negative(s: str) -> float:
    """A figure after the BIS table's minus sign, printed as a dash with a space ('— 1.0')."""
    return -figure(s)


# the misreadings of the text layers that stand for a number, with the number they stand for
MISREAD = {"2%": 2.25, "2 %": 2.25, "414": 4.5, "n t h": 11, "ist": 1}


def misread(s: str) -> float:
    return float(MISREAD[s])


FRACTIONS = {"½": ".5", "¼": ".25", "¾": ".75"}


def prepare(text: str) -> str:
    """A quotation ready for its figures: '2¼' and '4½' (the page images of the BIS) as decimals; then the Unicode
    compatibility forms."""
    s = re.sub(r"(\d) ?([½¼¾])", lambda m: m.group(1) + FRACTIONS[m.group(2)], text)
    return unicodedata.normalize("NFKC", s)


# a figure with its sign: a minus that follows no letter, digit, bracket, per cent sign or point
FIGURES = re.compile(r"((?<![\w)%.,])[-−])?(\d[\d,]*(?:\.\d+)?|\.\d+)")
HOW = {"num": figure, "card": cardinal, "fr": french, "neg": negative, "ml": misread}
# id -> [(phrase, how)], in order. A phrase 'context|word' is searched as a whole and read from `word`. Rows not
# listed are read with all the figures of the prepared quotation, with their signs.
READINGS: dict[str, list[tuple[str, str]]] = {
    "f211_11": [("of |eleven", "card")],
    "b72_margins": [("from |1", "num"), ("to |2%", "ml"), ("spread of |414", "ml")],
    "b73_margin": [("margin of |2 %", "ml")],
    "b73_denmark": [("on |n t h", "ml")],
    "b73_emcf": [("on |ist", "ml")],
    "oj_225": [("le |1", "num"), ("juillet |1972", "num"), ("excéder |2,25", "fr")],
    "b72t_ats": [("+ |5.1", "num"), ("+ |11.6", "num"), (" |23.30", "num"), (" |23.82", "num"), ("- |22.78", "num")],
    "b72t_itl": [("— |1.0", "neg"), ("+ |7.5", "num"), (" |581.50", "num"), (" |594.6", "num"), ("- |568.4", "num")],
    "b72t_sek": [("— |1.0", "neg"), ("+ |7.5", "num"), (" |4.8129", "num"), (" |4.920", "num"), ("- |4.705", "num")],
    "b72t_usd": [("— |7.9", "neg")],
    "db_eq15": [("(|15", "num")],
    "b72_exporters": [], "nxs_most": [],
    "bisdata_jpy": [("|1971", "num"), ("-|07", "num"), (",|357.404286", "num")],
    "bisdata_jpy7301": [("|1973", "num"), ("-|01", "num"), (",|301.788182", "num")],
    "bisdata_jpy7303": [("|1973", "num"), ("-|03", "num"), (",|261.901364", "num")],
    "bisdata_jpy7810": [("|1978", "num"), ("-|10", "num"), (",|183.800748", "num")],
    "bisdata_jpy8210": [("|1982", "num"), ("-|10", "num"), (",|270.898628", "num")],
    "bisdata_jpy8502": [("|1985", "num"), ("-|02", "num"), (",|260.390059", "num")],
    "bisdata_chf": [("|1978", "num"), ("-|10", "num"), (",|1.538908", "num")],
    "bisdata_gbp": [("|1985", "num"), ("-|02", "num"), (",|0.912924", "num")],
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
MISPRINTS = [("b72_margins", "2%", "'2%' for '2¼'"),
             ("b72_margins", "414", "'414' for '4½'"),
             ("b73_margin", "2 %", "'2 %' for '2¼'"),
             ("b73_denmark", "n t h", "'n t h' for '11th'"),
             ("b73_emcf", "ist", "'ist' for '1st'"),
             ("b72t_ats", "schillin9", "'schillin9' for 'schilling'"),
             ("b72t_units", "pet\"", "'pet\"' for 'per'"),
             ("b72_weak", "was , very", "'was , very' for 'was very'"),
             ("db_copyright", "()", "'()' for '©'"),
             ("db_eq16", "1/,W", "'1/,W' for '1/λθ'"),
             ("mr_models", "flexible-price(FrenkelBilson)", "'flexible-price(FrenkelBilson)' for 'flexible-price "
                                                             "(Frenkel-Bilson)'"),
             ("oj_225", "1 e r", "'1 e r' for '1er'"),
             ("oj_225", "°/o", "'°/o' for '%'")]
N_QUOTED = 190


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
        assert f"{rid}:" in notes or f"{rid}," in notes, rid                     # the notes say how it is read
    assert set(src) == set(df["file"]), sorted(set(src) ^ set(df["file"]))
    # the rows read on page images name the image source: the same PDF as the text-layer source, or a scan without
    # a text layer
    for key, s in src.items():
        if s["format"] == "image":
            pdf_ = key.replace("img_", "_")
            if pdf_ in src:
                assert (src[pdf_]["url"], src[pdf_]["sha256"]) == (s["url"], s["sha256"]), key
            else:
                assert "without a text layer" in s["version"] or "a scan without" in s["version"], key
    print(f"ok {len(df)} rows; {len(MISPRINTS)} misreadings named in the notes")


# ---------------------------------------------------------------------------------------------------
# 2. The quotations of the text: each “…” is a rendering of words of rows
TRANSLATIONS = {
    "蛇形浮动": ("b76_return",),
    "不公平的汇率": ("nx_unfair",),
    "明天和今天一样值钱": ("nx_tomorrow",),
    "非常紧张": ("f165_nervous",),
    "正在失去主动": ("f165_initiative",),
    "中心汇率": ("b72_central",),
    "中间汇率": ("b72_middle",),
    "历史上最重要的货币协定": ("nxs_most",),
    "不会再有一次贬值": ("f14_nodeval",),
    "稳定但可调整的平价": ("b74_c20",),
    "隧道里的蛇": ("b73i_snake",),
    "动态": ("db_title",),
    "与任何估计的模型一样好": ("mr_asgood",),
    "不现实的拒绝": ("b73i_unrealistic",),
    "致命伤": ("boj_fatal",),
    "完全出于政治": ("f33_political",),
    "尽可能难以运转": ("f35_hard",),
    "2\\%": ("b72_margins",),
    "414": ("b72_margins",),
}
# the words of the source each rendering renders, in the quotation
KEYWORDS = {
    "b76_return": ['"snake"'],
    "nx_unfair": ["unfair exchange rates"],
    "nx_tomorrow": ["worth just as much tomorrow as it is today"],
    "f165_nervous": ["very nervous"],
    "f165_initiative": ["losing the initiative"],
    "b72_central": ['"central" rates'],
    "b72_middle": ['"middle" rates'],
    "nxs_most": ["the most significant monetary agreement", "in the history of the world"],
    "f14_nodeval": ["there will not be another devaluation"],
    "b74_c20": ['"stable but adjustable par values"'],
    "b73i_snake": ['"the snake in the tunnel"'],
    "db_title": ["Exchange Rate Dynamics"],
    "mr_asgood": ["as well as any estimated model"],
    "b73i_unrealistic": ["unrealistic refusal"],
    "boj_fatal": ["命取り"],
    "f33_political": ["entirely political"],
    "f35_hard": ["as hard to work as possible"],
    "b72_margins": ["2%", "414"],
}
OWN = {"2\\%", "414"}                          # quoted in the source's own words (the misreadings, the 史料说明)


def tex_text() -> str:
    return "\n".join(l for l in TEX.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("%"))


def text_quotations() -> list[str]:
    """The “…” of the text; the closing question is Chapter 47's and the chapter's own question is in the guide and at
    the end of the opening (both checked by guide() and opening())."""
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 47's question"
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
# sub- and superscripts of the math, the numbers of the parts of the example ((1)-(3), not Dornbusch's equations
# 式（1）至（3）), the figures' and tables' labels and the column specifications of the tables
MASKS = [re.compile(r"\\begin\{keyeq\}.*?\\end\{keyeq\}", re.DOTALL),
         re.compile(r"\\begin\{equation\}.*?\\end\{equation\}", re.DOTALL),
         re.compile(r"\\(?:label|cite|chref|secref|figref|tabref|exref|eqref|ref|nameref|url|fig)\{[^}]*\}"),
         re.compile(r"_\{[^}]*\}|_\d"),
         re.compile(r"\^\{\d+\}"),
         re.compile(r"(?<![式至])（\d）"),
         re.compile(r"\{(?:fig|tab):[^}]*\}|\\multicolumn\{\d+\}"),
         re.compile(r"\\begin\{tabularx\}\{\\linewidth\}\{[^\n]*"),
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


def day(y: float, m: int, d: float) -> str:
    return pd.Timestamp(int(y), int(m), int(d)).day_name()


def report(key: str) -> int:
    """The year in which a BIS Annual Report's year ends (its title: '1st April 1972-31st March 1973')."""
    return year_in(key, r"31st March (\d{4})")


def showa(n: float) -> int:
    """昭和 n 年 as a year of the Western calendar."""
    return int(1925 + n)


# ---------------------------------------------------------------------------------------------------
# The teaching model, the series and the figures' data
EX = dict(lam=2.0, delta=0.5, sigma=1.0, pi=0.8, dm=10.0)     # ex:floating-overshoot and Figure floating_paths
SC = dict(lam=4.0, theta=1.0, dm=8.0)                          # self-check 1
MARK = 1.95583                                                  # Deutsche Mark per euro: the BIS's series in euro
RATES = {"jpy": "cpi_jp", "deu_eur": "cpi_de", "chf": "cpi_ch", "gbp": "cpi_gb"}
FIXED, FLOAT = ("1959-12", "1970-12"), ("1973-12", "1985-12")  # the months whose changes are compared
SPAN, BASE = ("1965-01", "1985-12"), ("1970-01", "1970-12")    # Figure floating_rates: its months and its base year
VLINES = ("1971-08-15", "1971-12-18", "1973-03-19")             # the vertical lines of Figure floating_rates

EQ_OVERSHOOT = ("e=\\bar e-\\frac{1}{\\lambda\\theta}\\,(p-\\bar p),\\qquad\n"
                "\\frac{\\mathrm{d}e}{\\mathrm{d}m}=1+\\frac{1}{\\lambda\\theta} .\\label{eq:floating-overshoot}")
EQ_THETA = ("\\theta=\\frac{\\pi}{2}\\Bigl(\\frac{\\sigma}{\\lambda}+\\delta\\Bigr)+\\sqrt{\\frac{\\pi^{2}}{4}"
            "\\Bigl(\\frac{\\sigma}{\\lambda}+\\delta\\Bigr)^{2}+\\frac{\\pi\\delta}{\\lambda}} .\\label{eq:floating-theta}")


def theta(lam: float, delta: float, sigma: float, pi: float) -> float:
    """eq:floating-theta (Dornbusch's (15)): the expectations coefficient that the model's own path bears out."""
    a = sigma / lam + delta
    return pi * a / 2 + np.sqrt(pi ** 2 * a ** 2 / 4 + pi * delta / lam)


def speed(th: float, lam: float, delta: float, sigma: float, pi: float) -> float:
    """The rate at which p - pbar shrinks when e follows Dornbusch's (6) with coefficient th and prices follow (8):
    dp/dt = pi (delta ((e - ebar) - (p - pbar)) - sigma (i - i^f)), e - ebar = -(p - pbar)/(lam th),
    i - i^f = (p - pbar)/lam."""
    return pi * (delta * (1 + 1 / (lam * th)) + sigma / lam)


def jump(lam: float, th: float) -> float:
    """eq:floating-overshoot (right): de/dm."""
    return 1 + 1 / (lam * th)


def path(t, lam=EX["lam"], delta=EX["delta"], sigma=EX["sigma"], pi=EX["pi"], dm=EX["dm"]) -> dict:
    """After money rises by dm (per cent) at t = 0 from an equilibrium at 0: the exchange rate and the price level (per
    cent from their old levels) and the interest differential i - i^f (percentage points); all 0 before t = 0."""
    th = theta(lam, delta, sigma, pi)
    t = np.asarray(t, float)
    gap = np.where(t < 0, 0.0, -dm * np.exp(-th * np.clip(t, 0, None)))   # p - pbar
    after = (t >= 0).astype(float)
    return {"e": after * dm - gap / (lam * th), "p": after * dm + gap, "i": gap / lam, "theta": th}


def changes(col: str, months: tuple[str, str], what: str = "nominal") -> pd.Series:
    """100 x the monthly changes of the logarithm of the nominal rate, the real rate (the nominal rate times the American
    CPI over the home CPI, eq:external-real) or the ratio of the two price levels, over the changes of these months
    (the first month is the base of the first change)."""
    S = series().loc[months[0]:months[1]]
    e, pu, ph = np.log(S[col]), np.log(S["cpi_us"]), np.log(S[RATES[col]])
    x = {"nominal": e, "real": e + pu - ph, "relp": pu - ph}[what]
    return x.diff().dropna() * 100


def volatility(col: str, months: tuple[str, str]) -> dict[str, float]:
    """The standard deviations (ddof = 1) of the three kinds of monthly change."""
    return {w: float(changes(col, months, w).std(ddof=1)) for w in ("nominal", "real", "relp")}


def without(col: str, months: tuple[str, str], drop: list[str]) -> float:
    """The standard deviation of the nominal changes without the changes of some months."""
    x = changes(col, months)
    return float(x.drop([pd.Period(m, freq="M") for m in drop]).std(ddof=1))


def index(col: str) -> pd.Series:
    """Figure floating_rates: the rate over SPAN as an index of its BASE average = 100."""
    S = series()
    return 100 * S.loc[SPAN[0]:SPAN[1], col] / S.loc[BASE[0]:BASE[1], col].mean()


def models() -> None:
    t = TEX.read_text(encoding="utf-8")
    assert EQ_OVERSHOOT in t and EQ_THETA in t
    # Dornbusch's equations as the page images print them
    has("db_eq1", "r = r* + x. (1)")
    has("db_eq2", "x = θ(ē − e). (2)")
    has("db_eq3", "−λr + φy = m − p, (3)")
    has("db_eq5", "p̄ = m + (λr* − φy). (5)")
    has("db_eq6", "e = ē − (1/λθ)(p − p̄). (6)")
    has("db_eq7", "ln D = u + δ(e − p) + γy − σr, (7)")
    has("db_eq8", "ṗ = π ln (D/Y) = π[u + δ(e − p) + (γ − 1)y − σr]. (8)")
    has("db_eq15", "θ̃(λ, δ, σ, π) = π(σ/λ + δ)/2 + [π²(σ/λ + δ)²/4 + πδ/λ]^1/2. (15)")
    has("db_eq16i", "de/dm = 1 + 1/λθ. (16)")
    rng = np.random.default_rng(46)
    for _ in range(500):
        lam, delta, sigma, pi = rng.uniform(0.1, 5, 4)
        th = theta(lam, delta, sigma, pi)
        assert th > 0
        # (15) is the root that makes expectations consistent: the path shrinks at the rate th people expect
        assert np.isclose(speed(th, lam, delta, sigma, pi), th)
        assert np.isclose(th ** 2 - pi * (sigma / lam + delta) * th - pi * delta / lam, 0)
        # the moment money rises: p is fixed, the rate from (3), the expected change from (1), e from (2)
        dm, k, ifor, m0 = rng.uniform(0.1, 20), *rng.uniform(-3, 3, 3)
        p0 = m0 - k + lam * ifor                                   # (5): the old long-run price
        ebar0, m1 = p0, m0 + dm                                    # the real rate e - p at 0, foreign prices at 0
        pbar1, ebar1 = m1 - k + lam * ifor, ebar0 + dm             # neutrality: both rise by dm
        i = (k - m1 + p0) / lam                                    # (3): m - p = k - lambda i
        e = ebar1 - (i - ifor) / th                                # (1) and (2)
        assert np.isclose(e, ebar1 - (p0 - pbar1) / (lam * th))     # eq:floating-overshoot (left)
        assert np.isclose(e - ebar0, dm * jump(lam, th))           # (right)
        assert np.isclose(i - ifor, -dm / lam) and jump(lam, th) > 1
        # db_dampen: the more money demand responds to the rate, the smaller the overshooting; db_faster: the economy
        # converges faster the lower lambda and the higher sigma and delta
        assert jump(lam * 1.05, theta(lam * 1.05, delta, sigma, pi)) < jump(lam, th)
        assert theta(lam * 1.05, delta, sigma, pi) < th
        assert theta(lam, delta, sigma * 1.05, pi) > th and theta(lam, delta * 1.05, sigma, pi) > th
        # along the path the exchange rate falls at the expected rate and prices move by (8)
        t0, h = 0.7 / th, 1e-6 / th                                 # about half the way back
        P = path([t0, t0 + h], lam, delta, sigma, pi, dm)
        de, dp = (P["e"][1] - P["e"][0]) / h, (P["p"][1] - P["p"][0]) / h
        assert np.isclose(de, th * (dm - P["e"][0]), rtol=1e-4)          # x = theta (ebar - e) is the actual change
        gap_e, gap_p = P["e"][0] - dm, P["p"][0] - dm
        assert np.isclose(dp, pi * (delta * (gap_e - gap_p) - sigma * P["i"][0]), rtol=1e-4)
        assert P["e"][0] > dm > P["p"][0] and P["i"][0] < 0            # the currency appreciates while prices rise
        # flexible prices: p rises by dm at once, the rate does not move, e rises by dm only
        assert np.isclose((k - m1 + (p0 + dm)) / lam, ifor)
    print("ok the key equations and the claims made of them on 500 random draws")


# ---------------------------------------------------------------------------------------------------
# 4. The text, section by section
def guide(F, Y, Q):
    t = TEX.read_text(encoding="utf-8")
    assert f"\\guidequestion{{{GUIDE}}}" in t and GUIDE == PREV
    assert chapter("ch45_monetarism").rstrip().endswith(PREV)                  # 第 45 章交来的问题
    assert "\\guideprereq{\\chref{ch:brettonwoods}\\enspace\\nameref{ch:brettonwoods}；\\chref{ch:mundell}\\enspace" \
           "\\nameref{ch:mundell}}" in t
    said("追踪 1971 年 8 月美元停止兑换黄金到 1973 年主要货币转向浮动的过程", F["nx_date"][1],
         month("nx_date", "August"), F["f35_paris"][1])
    said("推导多恩布什（1976）的汇率超调模型", F["db_journal"][2])
    said("说明浮动以后汇率波动大于基本面的现象（Meese \\& Rogoff 1983）", F["mr_journal"][1])
    say("描述欧洲的“蛇形浮动”与早期汇率合作")
    assert "\\chapterstub" not in t


def opening(F, Y, Q):
    d, y = F["nx_date"]
    m = month("nx_date", "August")
    assert day(y, m, d) == "Sunday"
    has("nx_sunday", "this Sunday evening")
    said("1971 年 8 月 15 日是星期日", y, m, d)
    has("nx_note", "p.m.", "Oval Office", "broadcast live on radio and television")
    said("晚上 9 点，尼克松", F["nx_note"][0])
    has("nx_fronts", "three fronts", "more and better jobs", "the cost of living", "international money speculators")
    has("nx_freeze", "a freeze on all prices and wages")
    said("他宣布冻结全国的物价与工资 90 天，削减 10\\% 的对外经济援助", F["nx_freeze"][0], F["nx_aid"][0])
    has("nx_seven", "one international monetary crisis every year")
    said("他说，过去 7 年里平均每年有一次国际货币危机", F["nx_seven"][0])
    has("nx_suspend", "suspend temporarily the convertibility of the dollar into gold or other reserve assets")
    has("nx_surcharge", "goods imported into the United States")
    said("他还宣布对进口商品加征 10\\% 的附加税", F["nx_surcharge"][0])
    has("nx_abroad", "buy slightly less")
    y73 = F["f35_paris"][1]
    has("b73_reopen", "19th March")
    assert day(y73, 3, F["b73_reopen"][0]) == "Monday"
    has("b73_joint", "six of the EEC countries")
    said("1973 年 3 月 19 日外汇市场重新开放，欧洲共同体的 6 个国家对美元共同浮动", y73,
         month("b73_reopen", "March"), F["b73_reopen"][0], cardinal("six"))
    has("b73_others", "Canada, Japan and Switzerland")
    assert (y73 - y) * 12 + 3 - m == 19                                         # 一年半以后
    assert paragraph("一年半以后").endswith(GUIDE)                               # the opening ends with the question


def world(F, Y, Q):
    said("1946 年起，金价是每盎司 35 美元", *there("ch36_brettonwoods", "1946 年起，金价是每盎司 35 美元"))
    assert F["b72_smithsonian"][1] == 35
    said("并在平价上下 1\\% 以内干预汇率", F["b72i_margins"][0])
    assert there("ch36_brettonwoods", "并在平价上下 1\\% 以内干预汇率") == [F["b72i_margins"][0]]
    yb72 = report("bis1972_46")
    D = F["b72_deficit"]
    has("b72_deficit", "net short-term outflow", "unprecedented overall deficit")
    said("国际清算银行（BIS）在 1972 年的年报里回顾说，1970 年美国的短期资本净流出 76 亿美元，官方结算差额出现了史无"
         "前例的 98 亿美元赤字", yb72, D[0], D[1] * 1e9, D[2] * 1e9)
    assert F["b72_settlements"][1:] == D[2:0:-1][:1] + [D[0]]                   # the same deficit of 1970
    said("美国的货币政策在 1969—1970 年由紧转松", *F["b72_swing"])
    has("b72_germany", "raising its discount rate") if "raising its discount rate" in words_of("b72_germany") else \
        has("b72_germany", "discount rate")
    said("1970 年 3 月，美联储正在放松，联邦银行却提高了贴现率", F["b72_germany"][0], month("b72_germany", "March"))
    has("b72_reserves70", "last nine months")
    said("1970 年的后 9 个月，联邦德国的储备增加了 58 亿美元", F["b72_reserves70"][0], cardinal("nine"),
         F["b72_reserves70"][1] * 1e9)
    said("到 1970 年底，美国的基本收支已经很弱", F["b72_weak"][0])
    has("b72_outflows", "further outflows of funds")
    said("1969 年 8 月到 1970 年 6 月", F["b72_franc"][0], month("b72_franc", "August"), F["b72_franc"][1],
         month("b72_franc", "June"))
    said("\\chref{ch:brettonwoods}讲过它 1969 年的浮动", F["b72_franc"][0])
    has("b72_mark", "float as from 10th May")
    has("b73_floats", "the Deutsche Mark and the guilder between May and December 1971")
    said("1971 年 5 月，马克又一次浮动，荷兰盾也一起浮动", F["b73_floats"][0], month("b72_mark", "May"))
    said("8 月又起了风浪", month("b72_august", "August"))
    said("8 月的危机始于 6 日", month("b72_august", "August"), F["b72_august"][0])
    has("b72_flight", "into Swiss francs", "the largest single flight")
    said("逃离美元的资金使其他国家的储备增加 37 亿美元，流进瑞士法郎的最多，有 17 亿美元", F["b72_flight"][0] * 1e9,
         F["b72_flight"][1] * 1e9)
    said("BIS 说，1971 年的官方结算赤字主要靠对外国官方机构的负债增加 274 亿美元来弥补", F["b72_liabilities"][0],
         F["b72_liabilities"][1] * 1e9)
    has("b72_losses", "declared formally inconvertible on 15 th August")
    # the decision
    d2, y71 = F["f164_aug2"]
    assert y71 == F["nx_date"][1]
    said("8 月 2 日，尼克松几次会见康纳利", month("f164_aug2", "August"), d2)
    has("f164_architect", "primary architect")
    said("他那天几乎讲全了 8 月 15 日要宣布的要点", month("f164_elements", "August"), F["f164_elements"][0])
    said("让美元浮动、加征 10\\% 的进口附加税", F["f164_intl"][0])
    said("他认为兑换维持不到 1972 年的大选", F["f164_election"][0])
    said("每年能给预算带来 40 亿美元", F["f164_budget"][0] * 1e9)
    said("尼克松倾向于必要时 8 月就行动", month("f164_leaning", "August"))
    has("f164_state", "Under no circumstances was the State Department to be consulted")
    has("f165_aug11", "Wednesday")
    assert day(y71, 8, F["f165_aug11"][0]) == "Wednesday"
    said("8 月 11 日，尼克松对舒尔茨说", month("f165_aug11", "August"), F["f165_aug11"][0])
    has("f165_aug12", "At noon")
    said("8 月 12 日中午", month("f165_aug12", "August"), F["f165_aug12"][0])
    said("舒尔茨汇报了 8 月 2 日以来各国拿美元兑换的规模", month("f165_conversions", "August"),
         F["f165_conversions"][0])
    assert day(y71, 8, F["f165_aug12"][0]) == "Thursday" and day(y71, 8, F["f165_aug12"][0] + 4) == "Monday"
    has("f165_monday", "by Monday")
    said("他仍觉得全部方案最好 9 月 7 日宣布", month("f165_sept7", "September"), F["f165_sept7"][0])
    has("f165_burns", "only two or three choices")
    T = F["f168_time"]
    has("f168_time", "Camp David", "economic advisers", "White House staff")
    said("8 月 13 日下午，尼克松在戴维营与经济顾问及白宫幕僚开会", month("f168_time", "August"), T[3])
    # the editor's round: the meeting detailed a programme already agreed on 2 and 12 August (Documents 164, 165)
    said("会是为尼克松 8 月 2 日与 12 日已经同意的新经济政策定下细节", month("f168_detail", "August"), *F["f168_detail"])
    assert tuple(F["f168_detail"]) == (F["f164_aug2"][0], F["f165_aug12"][0]), (F["f164_aug2"], F["f165_aug12"])
    assert T[0] == 3 and T[2] == 7                                              # 3:15 to 7 p.m.: the afternoon
    names = [n.strip() for n in re.split(r",|\band\b", words_of("f168_diary").split("August 13,")[1]
                                         .replace("attended", "")) if n.strip()]
    assert len(names) == 10 and {"Connally", "Burns", "Volcker", "Stein", "Shultz"} <= set(names), names
    said("按总统日志，到会的有 10 人", len(names))
    U = F["f168_until"]
    has("f168_until", "11:30 a.m. on August 15")
    said("会议断断续续开到 15 日上午 11 点半", U[2], U[0])
    assert U[1] == 30
    said("斯坦 1998 年接受编者访谈时说", F["f168_stein"][1])
    said("到 8 月 14 日，尼克松才说要通知国务卿，问他是否同意削减 10\\% 的对外援助",
         month("f168_rogers", "August"), *F["f168_rogers"])
    assert F["f168_rogers"][1] == F["nx_aid"][0]
    # Canada
    said("\\chref{ch:mundell}讲过加拿大 1950 年代的浮动", *there("ch37_mundell", "加拿大 1950 年代的浮动"))
    said("1970 年 5 月 31 日，加拿大的财政部长宣布", F["pw_may31"][1], month("pw_may31", "May"), F["pw_may31"][0])
    has("pw_may31", "cease purchasing sufficient U.S. dollars")                 # 不再买入足以守住平价的美元


def smithsonian(F, Y, Q):
    y71 = F["nx_date"][1]
    has("b72_reopen", "Monday, 23 rd August")
    assert day(y71, 8, F["b72_reopen"][0]) == "Monday"
    said("8 月 23 日是星期一", month("b72_reopen", "August"), F["b72_reopen"][0])
    has("b72_japan", "for two weeks", "upper intervention limit")
    has("b72_reserves", "between the end of August and the end of December")
    said("8 月底到 12 月底，联邦德国与日本的总储备分别增加 17 亿与 28 亿美元", month("b72_reserves", "August"),
         month("b72_reserves", "December"), F["b72_reserves"][0] * 1e9, F["b72_reserves"][1] * 1e9)
    has("b72_exporters", "exporters")
    said("美国认为它的国际收支需要改善 130 亿美元，国际货币基金组织与经济合作与发展组织算出来是 90 亿美元左右",
         F["b72_13"][0] * 1e9, F["b72_9"][0] * 1e9)
    said("11 月 30 日，康纳利从罗马给白宫发电报", month("f211_date", "November"), F["f211_date"][0])
    said("方案要求以 1971 年 5 月 1 日为基点，其他经合组织国家的货币对美元加权平均至少升值 11\\%", F["f211_base"][1],
         month("f211_base", "May"), F["f211_base"][0], F["f211_11"][0])
    has("f211_11", "weighted average appreciation")
    has("f211_deficit", "first nine months")
    said("1971 年头 9 个月，美国的基本赤字按年率估计在 100 亿美元以上", F["f211_deficit"][0], cardinal("nine"),
         F["f211_deficit"][1] * 1e9)
    has("f211_tradedef", "For seven months", "at an annual rate")
    said("过去 7 个月，连贸易也出现了逆差，按年率约 30 亿美元", cardinal("seven"), F["f211_tradedef"][0] * 1e9)
    said("美国在会上同意考虑一个改善不到 130 亿美元的调整", F["b72_rome"][0] * 1e9)
    has("b72_rome", "less than $13 milliard", "a possible devaluation of the dollar")
    said("12 月 17—18 日，十国集团的部长在华盛顿的史密森学会达成协议", month("f221_date", "December"),
         F["f221_date"][0], F["f221_date"][1])
    assert -F["b72t_usd"][0] == F["b72_smithsonian"][0]
    said("美元对黄金贬值 7.9\\%，日元对美元升值 16.9\\%，马克升值 13.6\\%", F["b72_smithsonian"][0], F["b72t_jpy"][1],
         F["b72t_dem"][1])
    M = F["b72i_margins"]
    assert M == F["b72_margins"] and M[2] == 2 * M[1]
    said("对美元的波动幅度从平价上下各 1\\% 放宽到各 2.25\\%，上下限之间的距离达到 4.5\\%", *M)
    said("汇率离开中心 1\\% 时央行还不必入市", M[0])
    J = F["b72t_jpy"]
    assert np.isclose(J[2] * (1 - M[1] / 100), J[4], atol=0.005)               # the lower limit: 308 less 2.25%
    said("按表中日元的中心汇率 308 日元，上下各 2.25\\%，下限约是 301.1 日元", J[2], M[1], J[4])
    S = series()
    assert (S.loc["1972-02":"1973-01", "jpy"] < J[2]).all()                      # 站到了升值的一边
    late = S.loc["1972-07":"1973-01", "jpy"]
    assert late.between(300.5, 302).all() and late.max() == F["bisdata_jpy7301"][2]
    said("1972 年 7 月到 1973 年 1 月，日元的月平均都在 301 日元上下", F["b73_sterling"][1], 7,
         F["bisdata_jpy7301"][0], F["bisdata_jpy7301"][1], late.mean())
    # the table
    for words, rid in (("日元 & $+7.7$ & $+16.9$ & 308.00", "b72t_jpy"), ("瑞士法郎 & $+7.1$ & $+13.9$ & 3.84", "b72t_chf"),
                       ("奥地利先令 & $+5.1$ & $+11.6$ & 23.30", "b72t_ats"),
                       ("德国马克 & $+4.6$ & $+13.6$ & 3.2225", "b72t_dem"),
                       ("比利时法郎 & $+2.8$ & $+11.6$ & 44.8159", "b72t_bef"),
                       ("荷兰盾 & $+2.8$ & $+11.6$ & 3.2447", "b72t_nlg")):
        said(words, *F[rid][:3])
    for words, rid in (("英镑 & — & $+8.6$ & 2.60571", "b72t_gbp"), ("法国法郎 & — & $+8.6$ & 5.1157", "b72t_frf")):
        assert len(F[rid]) == 4                                                  # no change against gold
        said(words, *F[rid][:2])
    for words, rid in (("意大利里拉 & $-1.0$ & $+7.5$ & 581.50", "b72t_itl"),
                       ("瑞典克朗 & $-1.0$ & $+7.5$ & 4.8129", "b72t_sek")):
        assert F[rid][0] < 0
        said(words, -F[rid][0], *F[rid][1:3])
    said("美元 & $-7.9$ & — & —", -F["b72t_usd"][0])
    assert round((360 / J[2] - 1) * 100, 1) == J[1]
    has("b72t_note", "Dollars per pound sterling")
    has("b72t_head", "New central or")
    has("b72t_title", "Realignment of leading currencies")
    said("1971 年 12 月 18 日的汇率调整", F["b72t_title"][2], month("b72t_title", "December"), F["b72t_title"][1])
    said("国际清算银行 1972 年年报第 30 页的表 Realignment of leading currencies，1971 年 5 月 5 日到 12 月 18 日的变化", yb72 := report("bis1972_46"),
         page("b72t_title"), F["b72t_title"][2], month("b72t_title", "May"), F["b72t_title"][0],
         month("b72t_title", "December"), F["b72t_title"][1])
    assert yb72 == 1972
    said("美元对其他经合组织国家的货币平均贬值 12\\%，政府将请国会授权把黄金价格提高到每盎司 38 美元",
         F["f221_12"][0], F["f221_38"][0])
    assert F["f221_38"][0] == F["b72_smithsonian"][2]
    has("nxs_note", "p.m.", "Smithsonian Institution")
    said("下午 5 点 48 分", *F["nxs_note"])
    has("nxs_free", "the whole free world has won")
    said("法国 12 月 21 日宣布了经常账户交易的新平价", month("f221_france", "December"), F["f221_france"][0])
    has("f221_france", "financial franc would not be bound")
    assert day(F["b72_bill"][1], 5, F["b72_imf"][0]) == "Friday"
    has("b72_imf", "Friday, 5 th May")
    # the BIS dates the signing 3 April 1972; the statute (Public Law 92-268, 86 Stat. 116) is approved March 31,
    # 1972 (its margin date and last line, read on the page image): the text follows the statute and names the BIS date
    has("b72_bill", "signed the bill authorising and directing the promised change in the par value of the dollar",
        "3rd April")
    has("pvma_date", "March")
    has("pvma_38", "$1 equals one thirty-eighth of a fine troy ounce")      # $38 an ounce, Connally's 38
    assert F["pvma_date"][1] == F["b72_bill"][1] and F["pvma_38"][0] == 1
    assert day(F["pvma_date"][1], 3, F["pvma_date"][0]) == "Friday"
    said("1972 年 3 月 31 日，尼克松签署了国会通过的《平价修改法》，授权财政部长把美元的平价定为每盎司黄金 38 美元",
         F["pvma_date"][1], month("pvma_date", "March"), F["pvma_date"][0], F["f221_38"][0])
    said("美国 5 月 5 日正式通知国际货币基金组织", month("b72_imf", "May"), F["b72_imf"][0])
    said("BIS 1972 年的年报把尼克松签署平价法案的日子记作 4 月 3 日，法律文本记作 3 月 31 日", report("bis1972_46"), 4,
         F["b72_bill"][0], 3, F["pvma_date"][0])
    say("这个序列在浮动以前多半记的是平价，前一个数因此偏小（本书的核对）",
        "英国的倍数最小，部分是因为英国早年的物价指数取整较粗，浮动以前的波动被放大了（本书的核对）")
    said("1972 年 6 月 23 日起，英国停止按固定的价格买卖美元", F["b73_sterling"][1], month("b73_sterling", "June"),
         F["b73_sterling"][0])
    yb73 = report("bis1973_46")
    said("BIS 1973 年回顾说", yb73)
    has("b73i_swiss", "On the same day", "upper limit against the dollar", "that day and the next day",
        "anti-inflationary aims")
    said("1973 年 1 月 22 日，瑞士法郎升到对美元的上限", F["b73i_jan22"][1], month("b73i_jan22", "January"),
         F["b73i_jan22"][0])
    has("b73i_feb", "first seven working days of February", "nearly $6 milliard", "Japan for half of the rest")
    said("2 月的头 7 个交易日，十国集团的货币当局买入约 80 亿美元，其中联邦德国近 60 亿", month("b73i_feb", "February"),
         cardinal("seven"), F["b73i_feb"][0] * 1e9, F["b73i_feb"][1] * 1e9)
    y73 = F["f35_paris"][1]
    assert day(y73, 2, F["b73i_untenable"][0]) == "Friday"
    has("b73i_untenable", "By Friday, 9th February")
    said("到 2 月 9 日星期五", month("b73i_untenable", "February"), F["b73i_untenable"][0])
    said("美元第二次贬值 10\\%", F["b73i_devalue"][0])
    has("b73i_yen", "the yen and the commercial lira were set free to float")
    said("2 月 14 日市场重开以后，日元在美元贬值之外又很快升值 5\\%", month("b73i_yen5", "February"), *F["b73i_yen5"])
    said("FRUS 记作 2 月 12 日晚上，日本银行的行史也记作 12 日，BIS 记作 13 日", month("f12_evening", "February"),
         F["f12_evening"][0], F["boj_feb12"][1], F["b73i_devalue"][1])
    assert F["boj_feb12"][0] == 2 and F["f12_evening"][1] == F["b73i_devalue"][0] == F["boj_feb12"][2]
    has("f12_evening", "On the evening of February 12", "Secretary of the Treasury George Shultz")
    said("提醒要强调 1971 年 8 月 15 日讲过的那一点", F["f12_note"][1], month("f12_note", "August"), F["f12_note"][0])
    has("f12_home", "does not reduce value", "American dollar at home")
    said("3 月 2 日，尼克松在记者会上说", month("f14_date", "March"), F["f14_date"][0])
    assert F["b73i_march1"][0] == F["f14_date"][0] - 1                          # 前一天
    said("前一天，联邦银行一天就买进 27 亿美元", F["b73i_march1"][1] * 1e9)
    said("联邦德国 2 月头 7 个交易日买入近 60 亿美元，3 月 1 日又买 27 亿美元", 2, cardinal("seven"),
         F["b73i_feb"][1] * 1e9, month("b73i_march1", "March"), F["b73i_march1"][0], F["b73i_march1"][1] * 1e9)
    has("b73_dollar", "to be determined by the market")
    has("b73_joint", "six of the EEC countries")
    said("欧洲共同体的 6 国随后商定", cardinal("six"))
    said("彼此的汇率维持在名义交叉汇率上下 2.25\\% 以内", F["b73_margin"][0])
    said("马克另外升值 3\\%", F["b73_revalue"][0])
    said("BIS 的年报一处说 3 月 12 日作出决定，另一处说 11 日达成安排，FRUS 与日本银行的行史都记作 11 日",
         month("b73_joint", "March"), F["b73_joint"][0], F["b73i_concluded"][0], F["f35_march11"][0])
    assert F["boj_march11"][:2] == [3, F["f35_march11"][0]]
    has("f35_paris", "Denmark, Ireland, Luxembourg, Switzerland")
    said("3 月 16 日，十国集团的部长与丹麦、爱尔兰、卢森堡、瑞士及几个国际组织的代表在巴黎开会，认可了共同体 3 月 11 日"
         "的安排", month("b73_g10", "March"), F["f35_paris"][0], 3, F["f35_march11"][0])
    assert F["b73_g10"][0] == F["f35_paris"][0]
    has("b73i_futile", "futile to return to fixed rates")
    has("f35_evening", "The previous evening")
    has("f35_simon", "six of them are now floating jointly")
    said("3 月 15 日晚上，西蒙在电话里对基辛格说，6 个国家共同浮动", 3, F["f35_paris"][0] - 1, cardinal("six"))
    yb74 = report("bis1974_46")
    said("BIS 1974 年说", yb74)
    has("b74_dollar", "about six months")
    said("美元对欧洲货币先跌得远远超过 10\\% 的贬值", F["b74_dollar"][0])
    assert F["b74_dollar"][0] == F["b73i_devalue"][0]
    has("b74_satisfactory", "hardly satisfactory")
    said("BIS 1974 年把油价的猛涨列为过去一年最引人注目的事", yb74)
    has("b74_oil", "eruption of the price of oil")
    said("1976 年 1 月，国际货币基金组织理事会的临时委员会在牙买加完成协议", F["b76_jamaica"][0],
         month("b76_jamaica", "January"))
    has("b76_gold", "The official price will be abolished")
    has("b76_article4", "The new Article IV will allow")                         # 将让……也将取消
    said("日本守着 360 日元", F["boj_360"][2])


def japan(F, Y, Q):
    B = F["boj_tokyo"]
    assert showa(B[0]) == B[1] == F["nx_date"][1]
    said("日本 · 1971—1973 · 360 日元的终结", B[1], F["boj_75"][1], F["boj_360"][2])
    assert day(B[1], B[2], B[3]) == "Monday"
    # 9 p.m. of the 15th in Washington (UTC-4 in August) is 10 a.m. of the 16th in Tokyo (UTC+9)
    assert (B[3] - F["nx_date"][0]) * 24 + B[4] - (12 + F["nx_note"][0]) == 9 + 4
    said("是日本时间 8 月 16 日（星期一）上午 10 点", B[2], B[3], B[4])
    said("17 日以后照常开市", F["boj_decision"][0])
    K = F["boj_11days"]
    has("boj_11days", "平衡買い")
    said("8 月 16 日到 27 日的 11 天里（星期日除外），当局为守住平价买入的美元近 40 亿美元，约相当于当时 4 个月的进口，外汇储备"
         "从不到 80 亿美元猛增到 120 亿美元", K[0], K[1], K[2], K[3], K[4] * 1e8, K[5], K[6] * 1e8, K[7] * 1e8)
    assert sum(day(B[1], 8, d_) != "Sunday" for d_ in range(int(K[1]), int(K[2]) + 1)) == K[3]
    assert np.isclose(F["b72_4bn"][0] * 1e9, K[4] * 1e8) and F["b72_4bn"][1] == F["boj_float"][3]   # BIS: $4 milliard
    has("boj_sellers", "輸出業者", "比較的少額")
    has("boj_341", "28日（土曜日）341円30銭")
    assert day(B[1], 8, F["boj_341"][0]) == "Saturday"
    said("8 月 28 日（星期六）日元转向浮动，当天升到 341.30 日元", F["boj_float"][2], F["boj_float"][3],
         F["boj_341"][1] + F["boj_341"][2] / 100)
    said("按经济企画厅 1972 年白皮书的统计", showa(F["epa_title"][0]))
    E = F["epa_120"]
    said("输出比率超过 10\\% 的中小企业产地全国有 120 处，其中对美国的出口占 50.6\\%", E[0], E[1], E[7])
    has("epa_workers", "家庭婦人", "農業従事者")
    said("花 11 天大量买进美元", F["boj_criticism"][0])
    has("boj_pessimism", "極度に悲観的")
    y73 = F["boj_75"][1]
    assert day(y73, 2, F["boj_feb10"][1]) == "Saturday"
    has("boj_feb10", "2月10日（土曜日）")
    said("1973 年 2 月 10 日（星期六）", y73, *F["boj_feb10"])
    said("日本时间 2 月 13 日各国达成协议", *F["boj_feb13"])
    has("boj_aichi", "固定相場に復帰したい")
    has("boj_263", "フロート移行後も", "一時的ながら")
    said("日元浮动以后继续走强，一度升到 263 日元台", F["boj_263"][0])


def europe(F, Y, Q):
    yb73, yb76 = report("bis1973_46"), report("bis1976_46")
    said("欧洲 · 1972—1976 · 蛇形浮动", F["oj_date"][1], yb76)
    has("oj_date", "21 mars 1972")
    said("1972 年 3 月 21 日理事会的决议要求", F["oj_date"][1], 3, F["oj_date"][0])
    has("oj_225", "juillet")
    has("oj_first", "premier pas")
    said("到 1972 年 7 月 1 日不超过 2.25\\%", F["oj_225"][1], 7, F["oj_225"][0], F["oj_225"][2])
    said("4 月 24 日起，计划付诸实施", month("b73i_snake", "April"), F["b73i_snake"][0])
    assert F["b73i_snake"][1] == F["oj_date"][1]
    said("即 4.5\\% 与 2.25\\%", *F["b73i_rule"])
    assert F["b73i_rule"] == [F["b72i_margins"][2], F["b72i_margins"][1]]
    said("英国与丹麦 5 月 1 日加入，挪威 5 月 23 日加入", month("b73i_join", "May"), F["b73i_join"][0], 5,
         F["b73i_join"][1])
    has("b73i_leave", "When sterling left the snake", "Denmark also withdrew")
    said("英镑 6 月离开，丹麦同时退出，10 月 11 日又回来", month("b73_sterling", "June"), month("b73_denmark", "October"),
         F["b73_denmark"][0])
    has("b73i_italy", "Italy then withdrew")
    said("1973 年 3 月以后，蛇对美元共同浮动", F["f35_paris"][1], 3)
    said("欧洲货币合作基金 1973 年 4 月成立，6 月 1 日开始运作", yb73, month("b73_emcf", "April"),
         month("b73_emcf", "June"), F["b73_emcf"][0])
    has("b73_emcf", "April this year")
    said("它 1974 年 1 月 21 日退出共同浮动", F["b74_france"][1], month("b74_france", "January"), F["b74_france"][0])
    said("1975 年 7 月按原来的中心汇率回来，1976 年 3 月 15 日在储备累计损失 30 亿美元以后再次退出",
         F["b76_return"][0], month("b76_return", "July"), yb76, month("b76_leave", "March"), F["b76_leave"][0],
         F["b76_leave"][1] * 1e9)
    has("b76_return", "same central rates")
    said("按 Rich 的叙述，1973 年 1 月新的投机攻击逼近", F["rich_float73"][0], month("rich_float73", "January"))
    has("rich_float73", "reluctantly")
    Z = F["rich_zone84"]
    has("rich_zone84", "CHF/100DEM")
    said("1978 年法郎升得太猛，瑞士国家银行在 9 月考虑过一个目标区，马克的价格在每 100 马克 84 到 100 瑞士法郎之间",
         F["rich_zone"][0], month("rich_zone", "September"), Z[2], Z[0], Z[1])
    said("10 月初改为临时的汇率目标", month("rich_80", "October"))
    has("rich_80", "at the beginning of October 1978")
    has("rich_depreciate", "more realistic levels")
    said("瑞士国家银行在 1979 年的年报里说", F["rich_return"][0])


def model(F, Y, Q):
    said("1976 年的论文给了一个解释", F["db_journal"][2])
    has("db_abstract", "initial overshooting", "differential adjustment speed of markets")
    said("他的式（1）至（3）与这里的三个式子相同", F["db_eq1"][0], F["db_eq3"][0])
    said("即多恩布什的式（5）", F["db_eq5"][0])
    said("左式是多恩布什的式（6），右式是他的式（16）", F["db_eq6"][1], F["db_eq16i"][2])
    assert F["db_eq16i"] == F["db_eq16"]
    said("$e$ 却上升 $(1+1/\\lambda\\theta)\\,\\mathrm{d}m$", F["db_eq16i"][0], F["db_eq16i"][1])
    said("多恩布什说，他对式（16）的解释还没有用到预期理性的限制", F["db_notyet"][0])
    has("db_partv", "no longer a necessary feature")
    has("db_less", "less than proportionately")
    # the example
    th = theta(EX["lam"], EX["delta"], EX["sigma"], EX["pi"])
    j = jump(EX["lam"], th)
    a = EX["sigma"] / EX["lam"] + EX["delta"]
    said("\\begin{example}{货币增加 10\\%}", EX["dm"])
    said("设 $\\lambda=2$，$\\delta=0.5$，$\\sigma=1$，$\\pi=0.8$，时间以年计", EX["lam"], EX["delta"], EX["sigma"],
         EX["pi"])
    said("货币一次增加 10\\%，汇率当时上升多少", EX["dm"])
    said("（1）$\\sigma/\\lambda+\\delta=1$，$\\theta=0.4+\\sqrt{0.16+0.2}=0.4+0.6=1.0$", a, EX["pi"] * a / 2,
         EX["pi"] ** 2 * a ** 2 / 4, EX["pi"] * EX["delta"] / EX["lam"], EX["pi"] * a / 2,
         np.sqrt(EX["pi"] ** 2 * a ** 2 / 4 + EX["pi"] * EX["delta"] / EX["lam"]), th)
    over = (j - 1) * EX["dm"]
    said("（2）$\\mathrm{d}e/\\mathrm{d}m=1+1/(2\\times1)=1.5$，汇率上升 15\\%，比长期的 10\\% 多 5 个百分点", 1, 1,
         EX["lam"], th, j, j * EX["dm"], EX["dm"], over)
    said("利率降 $10/2=5$ 个百分点，人们预期本币每年升值 $1\\times5=5\\%$，正好抵消利差", EX["dm"], EX["lam"],
         EX["dm"] / EX["lam"], th, over, th * over)
    assert np.isclose(th * over, EX["dm"] / EX["lam"])                         # the expected appreciation = the gap
    P1 = path(1.0)
    said("（3）$\\mathrm{e}^{-1}\\approx0.368$，汇率还高出长期水平 $5\\times0.368\\approx1.84\\%$，物价还低 "
         "$10\\times0.368\\approx3.68\\%$，利率还低 1.84 个百分点", th * 1, np.exp(-th), over, np.exp(-th),
         P1["e"] - EX["dm"], EX["dm"], np.exp(-th), EX["dm"] - P1["p"], -P1["i"])
    said("离长期水平的距离每 $\\ln2/\\theta\\approx0.69$ 年减半", 2, np.log(2) / th)
    P0, Pend = path(0.0), path(60.0)
    said("货币在第 0 年一次增加 10\\% 以后汇率、物价与利率的路径", 0, EX["dm"])
    said("以原来的水平为 0", 0)
    said("汇率先跳到 15\\%，再回落到 10\\%，物价从 0 慢慢升到 10\\%", P0["e"], Pend["e"], P0["p"], Pend["p"])
    said("参数$\\lambda=2$，$\\delta=0.5$，$\\sigma=1$，$\\pi=0.8$是教学用的假设", EX["lam"], EX["delta"], EX["sigma"],
         EX["pi"])
    said("第 0 年，汇率从 0 跳到 15\\%，物价不动，利率差跳到 $-5$ 个百分点", 0, path(-0.5)["e"], P0["e"], -P0["i"])
    assert np.exp(-3 * th) < 0.06                                               # 两三年里接近新的长期水平
    # the compare box
    K = F["boj_11days"]
    said("日本 11 天买入近 40 亿美元", K[3], K[4] * 1e8)
    said("瑞士 1973 年浮动以后才完全控制货币供给", F["rich_float73"][0])
    has("rich_control", "gained full control of the money supply")
    said("1971—1973 年各国一再买入美元", F["nx_date"][1], F["f35_paris"][1])


def test(F, Y, Q):
    S = series()
    pre = S.loc[:"1971-07", "jpy"]
    said("1971 年 8 月以前，四条线大体是平的", F["nx_date"][1], month("nx_date", "August"))
    said("日元的月平均一直在 357 到 360 日元之间", pre.min(), pre.max())
    steps = {c: int((changes(c, ("1959-12", "1971-07")).abs() > 1).sum()) for c in RATES}
    assert steps["jpy"] == 0 and all(steps[c] > 0 for c in ("deu_eur", "chf", "gbp")), steps   # 几次台阶
    said("1973 年 3 月以后，它们天天在变", F["f35_paris"][1], 3)
    said("日元从 1971 年 7 月的 357.4 日元升到 1973 年 3 月的 261.9 日元，1985 年 2 月又回到 260.4 日元",
         *F["bisdata_jpy"], *F["bisdata_jpy7303"], *F["bisdata_jpy8502"])
    for rid, col in (("bisdata_jpy", "jpy"), ("bisdata_jpy7301", "jpy"), ("bisdata_jpy7303", "jpy"),
                     ("bisdata_jpy7810", "jpy"), ("bisdata_jpy8210", "jpy"), ("bisdata_jpy8502", "jpy"),
                     ("bisdata_chf", "chf"), ("bisdata_gbp", "gbp")):
        y_, m_, v_ = F[rid]
        assert S.loc[f"{y_:.0f}-{m_:02.0f}", col] == v_, rid                     # the row is a line of the series
    has("bisdata_title", "Japan - Yen - Monthly - Average")
    has("bisdata_dem", "Germany - Euro - Monthly")
    has("bisdata_cpi", "United States", "Index, 2010 = 100")
    said("1965—1985 年，月平均，对数刻度，以 1970 年平均为 100", int(SPAN[0][:4]), int(SPAN[1][:4]), int(BASE[0][:4]),
         100)
    said("三条竖线是 1971 年 8 月 15 日、1971 年 12 月 18 日与 1973 年 3 月 19 日",
         *[int(x) for v in VLINES for x in v.split("-")])
    assert VLINES == (f"{F['nx_date'][1]:.0f}-08-{F['nx_date'][0]:.0f}",
                      f"{F['b72t_title'][2]:.0f}-12-{F['b72t_title'][1]:.0f}",
                      f"{F['f35_paris'][1]:.0f}-03-{F['b73_reopen'][0]:.0f}")
    said("马克按欧元序列乘以 1.95583 换算", MARK)
    said("比较的是 1960—1970 年与 1974—1985 年", int(FIXED[0][:4]) + 1, int(FIXED[1][:4]), int(FLOAT[0][:4]) + 1,
         int(FLOAT[1][:4]))
    said("每月的对数变化乘以 100", 100)
    V = {c: (volatility(c, FIXED), volatility(c, FLOAT)) for c in RATES}
    assert len(changes("jpy", FIXED)) == 132 and len(changes("jpy", FLOAT)) == 144
    jp0, jp1 = V["jpy"]
    assert jp0["nominal"] < 0.1
    said("1960—1970 年，日元名义汇率每月变化的标准差不到 0.1 个百分点，1974—1985 年是 2.8 个百分点", 1960, 1970, 0.1,
         1974, 1985, jp1["nominal"])
    said("实际汇率从 0.8 升到 2.9，两国物价之比前后都是 0.8 左右", jp0["real"], jp1["real"], jp0["relp"])
    assert abs(jp1["relp"] - 0.8) < 0.05
    said("马克名义汇率的标准差从 0.7 升到 2.7", V["deu_eur"][0]["nominal"], V["deu_eur"][1]["nominal"])
    said("瑞士法郎从 0.2 升到 3.2", V["chf"][0]["nominal"], V["chf"][1]["nominal"])
    said("英镑从 0.9 升到 2.6", V["gbp"][0]["nominal"], V["gbp"][1]["nominal"])
    said("它在 1960 年代的数字大", int(FIXED[0][:4]) + 1)
    said("是因为 1967 年 11 月贬了值", *there("ch36_brettonwoods", "1967 年 11 月"))
    said("去掉 1967 年 11 月与 12 月这两个月，英镑只有 0.1", 1967, 11, 12, without("gbp", FIXED, ["1967-11", "1967-12"]))
    R = [V[c][1]["real"] / V[c][0]["real"] for c in RATES]
    said("四种货币实际汇率的波动是此前的 2.5 到 6.5 倍", min(R), max(R))
    assert all(abs(V[c][1]["nominal"] / V[c][1]["real"] - 1) < 0.05 for c in RATES)   # 几乎一样大
    assert all(0.75 < V[c][1]["relp"] / V[c][0]["relp"] < 1.25 for c in RATES)        # 变化不大
    said("1960—1970 年与 1974—1985 年（本书的计算）", 1960, 1970, 1974, 1985)
    said("两国的通胀率在 1970 年代都升高了", 1970)
    for col in ("cpi_us", *RATES.values()):                                     # the average inflation of the decades
        g60 = (S.loc["1969-12", col] / S.loc["1959-12", col]) ** 0.1
        g70 = (S.loc["1979-12", col] / S.loc["1969-12", col]) ** 0.1
        assert g70 > g60 > 1, col
    said("日元 1978 年 10 月升到 183.8 日元，是这十几年里的最高点，1982 年 10 月又跌到 270.9 日元",
         *F["bisdata_jpy7810"], *F["bisdata_jpy8210"])
    flo = S.loc["1971-08":"1985-12"]
    assert flo["jpy"].idxmin() == pd.Period("1978-10", freq="M")
    assert flo["chf"].idxmin() == pd.Period("1978-10", freq="M") and flo["gbp"].idxmax() == pd.Period("1985-02", freq="M")
    assert F["bisdata_jpy8210"][0] - F["bisdata_jpy7810"][0] == 4
    said("这四年里美元涨了约 47\\%", (F["bisdata_jpy8210"][2] / F["bisdata_jpy7810"][2] - 1) * 100)
    said("瑞士法郎 1978 年 10 月升到 1.54 法郎", *F["bisdata_chf"])
    dm = flo["deu_eur"] * MARK
    lo = dm.idxmin()
    assert lo > pd.Period("1978-10", freq="M")                                   # 来得晚一些
    said("马克的最高点来得晚一些，1980 年 1 月是每美元 1.72 马克", lo.year, lo.month, dm[lo])
    assert F["bisdata_chf"][:2] == [F["rich_80"][0], month("rich_80", "October")]   # 正是改盯汇率的时候
    said("英镑 1985 年 2 月跌到每英镑约合 1.10 美元", F["bisdata_gbp"][0], F["bisdata_gbp"][1], 1 / F["bisdata_gbp"][2])
    said("美元 1980 年代前期的上涨在\\chref{ch:credibility}", 1980)
    de_up = there("ch36_brettonwoods", "1961 年 3 月 6 日升到 4 马克；1969 年 10 月 26 日升到 3.66 马克")
    said("马克 1961 年与 1969 年升值", de_up[0], de_up[4])
    said("去掉 1961 年 3 月、1969 年 10 月与 11 月，马克只有 0.2", de_up[0], de_up[1], de_up[4], de_up[5], 11,
         without("deu_eur", FIXED, ["1961-03", "1969-10", "1969-11"]))
    big = {c: [int((changes(c, P).abs() > 1).sum()) for P in (FIXED, FLOAT)] for c in RATES}
    said("1960—1970 年的 132 个月里，四种货币月度变动超过 1\\% 的最多只有 3 个月", 1960, 1970,
         len(changes("jpy", FIXED)), 1, max(b[0] for b in big.values()))
    said("1974—1985 年的 144 个月里，这样的月份有 99 到 109 个", 1974, 1985, len(changes("jpy", FLOAT)),
         min(b[1] for b in big.values()), max(b[1] for b in big.values()))
    # Meese and Rogoff
    said("Meese 与 Rogoff 1983 年比较了各种汇率模型的样本外预测", F["mr_journal"][1])
    said("他们用 1973 年 3 月到 1981 年 6 月的月度数据，从 1976 年 11 月起逐月预测", F["mr_sample"][0],
         month("mr_sample", "March"), F["mr_sample"][1], month("mr_sample", "June"), F["mr_first"][0],
         month("mr_first", "November"))
    has("mr_asgood", "one to twelve month horizons", "dollar/pound, dollar/mark")
    said("在 1 到 12 个月的期限上", cardinal("one"), cardinal("twelve"))
    has("mr_models", "Dornbusch-Frankel", "FrenkelBilson")
    said("\\tabref{tab:floating-mr}列出他们表 1 里 12 个月的预测误差，三个结构模型都比随机游走大", F["mr_t1"][0],
         F["mr_t1_dem"][0])
    has("mr_t1_title", "Random walk Forward rate Univariate autoregression Vector autoregression Frenkel-Bilson "
                       "Dornbusch-Frankel Hooper-Morton")
    cols = (1, 2, 5, 6, 7)                       # random walk, forward rate, the three structural models
    for cur, rid in (("美元/马克", "mr_t1_dem"), ("美元/日元", "mr_t1_jpy"), ("美元/英镑", "mr_t1_gbp")):
        v = F[rid]
        assert v[0] == 12 and all(v[k] > v[1] for k in (3, 4, 5, 6, 7))       # every model worse than the random walk
        assert (v[2] < v[1]) == (rid == "mr_t1_dem")                            # but the forward rate for the mark
        said(f"{cur} & " + " & ".join(f"{v[k]:.2f}" for k in cols), *[v[k] for k in cols])
    has("mr_fwdmark", "dollar/mark rate at twelve month horizons")
    said("表里唯一胜过随机游走的，是马克 12 个月的远期汇率", F["mr_t1_dem"][0])
    has("mr_rw", "dollar/yen rate", "one month", "twelve months")
    assert F["mr_rw"][1] == round(F["mr_t1_jpy"][1], 1)
    said("随机游走的误差以美元对日元最大，一个月是 3.7\\%，12 个月是 18.3\\%", F["mr_rw"][0], F["mr_t1_jpy"][0],
         F["mr_rw"][1])
    assert F["mr_t1_jpy"][1] == max(F[r][1] for r in ("mr_t1_dem", "mr_t1_jpy", "mr_t1_gbp"))
    has("mr_t1", "November 1976 through June 1981")
    said("12 个月的均方根误差（\\%），1976 年 11 月—1981 年 6 月", F["mr_t1_dem"][0], F["mr_t1"][1],
         month("mr_t1", "November"), F["mr_t1"][2], month("mr_t1", "June"))
    said("Meese 与 Rogoff（1983）第 13 页的表 1 中 12 个月的数字", F["mr_journal"][1], page("mr_t1_title"),
         F["mr_t1"][0], F["mr_t1_dem"][0])
    said("表 1 的单变量自回归与向量自回归两列没有列出", F["mr_t1"][0])           # columns 3 and 4: checked above


def debate(F, Y, Q):
    y71, y73 = F["nx_date"][1], F["f35_paris"][1]
    assert (y73 - y71) * 12 + 2 - 12 == 14                                      # 十四个月: December 1971 to February 1973
    say("\\subsubsection{史密森汇率为什么只维持了十四个月}")
    has("boj_defect", "円滑な通貨調整メカニズムの欠如")
    yb73 = report("bis1973_46")
    said("BIS 1973 年批评美国在 1971 年 8 月 15 日以后", yb73, F["b73i_unrealistic"][1],
         month("b73i_unrealistic", "August"), F["b73i_unrealistic"][0])
    has("nxs_doomed", "doomed to fail")
    has("boj_weak", "交換性を回復するコミットメント", "金価格の引上げ")
    said("它还说，1972 年一开年，投机者就发起了攻击", showa(F["boj_attack"][0]))
    has("boj_avoid", "円再切上げ絶対回避")
    assert showa(F["boj_75"][0]) == F["boj_75"][1]
    said("到 1973 年 2 月，当局在外汇市场上买入的美元共达 75 亿美元", F["boj_75"][1], F["boj_75"][2],
         F["boj_75"][3] * 1e8)
    said("美国要的改善是 130 亿美元，国际组织算的是 90 亿美元", F["b72_13"][0] * 1e9, F["b72_9"][0] * 1e9)
    has("db_backing", "lacks theoretical backing")
    has("db_facts", "the facts clearly point in this direction")
    has("mr_bias", "simultaneous equation bias, sampling error")
    has("mr_noconclusion", "without arriving at any definite conclusions")
    has("mr_oil", "oil price shocks")
    said("BIS 1972 年列举的理由", report("bis1972_46"))
    has("b72_reasons", "unwilling to allow completely free floating")
    said("1973 年 3 月 16 日，十国集团同意必要时由央行干预来管理浮动", y73, month("b73_g10", "March"), F["b73_g10"][0])
    has("b73_g10", "if judged necessary")
    said("3 月 14 日，基辛格在电话里对财政部副部长西蒙", month("f33_date", "March"), F["f33_date"][0])
    assert F["f33_date"][1] == y73
    has("f33_simon", "Deputy Secretary of the Treasury William Simon")
    has("f33_prevent", "to prevent a united European position", "without showing our hand")
    said("15 日晚上，他又说", F["f35_paris"][0] - 1)
    yb76 = report("bis1976_46")
    said("BIS 1976 年说，1975—1976 年央行的干预", yb76, F["b76_intervention"][0], 1900 + F["b76_intervention"][1])
    has("b76_intervention", "reminiscent of the old days of pegged rates")
    said("瑞士国家银行 1978 年回头盯住过汇率", F["rich_80"][0])
    assert 1994 <= F["rich_1995"][0] <= 1996                                    # 1990 年代中期
    said("1990 年代中期，它记着 1978—1981 年的难处", F["rich_1995"][0] // 10 * 10, *F["rich_conflict"])
    has("rich_admit", "with hindsight")


def deeper(F, Y, Q):
    said("尼克松 1971 年 8 月 15 日的讲话与 12 月 18 日对十国集团部长的讲话", F["nx_date"][1], month("nx_date", "August"),
         F["nx_date"][0], month("nxs_date", "December"), F["nxs_date"][0])
    docs: dict[int, list[int]] = {}
    for key, s in meta()["sources"].items():
        m_ = re.search(r"frus1969-76v(\d+)/d(\d+)$", s["url"])
        if m_:
            docs.setdefault(int(m_.group(1)), []).append(int(m_.group(2)))
    assert sorted(docs) == [3, 31]
    said("本章读了 1969—1976 年第 3 卷的第 164、165、168、211、221 号与第 31 卷的第 12、14、33、35 号文件", 1969, 1976, 3,
         *sorted(docs[3]), 31, *sorted(docs[31]))
    assert year_in("frus3d164_46", r"States, (\d{4})-") == 1969 and year_in("frus3d164_46", r"-(\d{4}), Vol") == 1976
    yrs = sorted(int(re.search(r"report-(\d{4})\.pdf", s["url"]).group(1)) for k, s in meta()["sources"].items()
                 if re.fullmatch(r"bis\d{4}_46", k))
    said("BIS 的年报读的是 1972、1973、1974 与 1976 年的扫描本", *yrs)
    has("b72_margins", "2%", "414")
    M = F["b72i_margins"]
    assert MISREAD["2%"] == M[1] and MISREAD["414"] == M[2]
    said("如把 2¼ 认成“2\\%”，把 4½ 认成“414”", int(M[1]), 2, int(M[2]), 414)
    said("1973 年年报的几页文字层字母间夹着空格", report("bis1973_46"))
    said("第 136 页的 4½ 与 2¼ 又认错了", page("b73i_rule"), int(F["b73i_rule"][0]), int(F["b73i_rule"][1]))
    said("日本银行的《日本银行百年史》第 6 卷", year_in("boj612img_46", r"第(\d)巻"))
    said("共同浮动的窄幅，BIS 1973 年的年报说是名义交叉汇率上下各 2.25\\%，日本银行的行史说是上下各 1.125\\%",
         report("bis1973_46"), F["b73_margin"][0], F["boj_march11"][3])
    assert 2 * F["boj_march11"][3] == F["b73_margin"][0]                         # half the spread on either side
    said("每种货币离共同的中线都不超过 1.125\\%，任何两种货币之间的差距就不超过 2.25\\%", F["boj_march11"][3],
         F["b73_margin"][0])
    has("loc_mizuta", "Mizuta, Mikio")
    has("db_copyright", "1976 by The University of Chicago. All rights reserved.")
    has("mr_publisher", "North-Holland")
    has("ifdp_cover", "References")
    said("Meese 与 Rogoff 1981 年的讨论稿", F["ifdp_date"][0])
    assert F["ifdp_title"] == [184, F["ifdp_date"][0]]
    said("结果都取自 1983 年发表的版本。表 1 的数字按页面图像读出", F["mr_journal"][1], F["mr_t1"][0])
    said("欧洲共同体理事会 1972 年 3 月 21 日的决议", F["oj_date"][1], 3, F["oj_date"][0])
    said("本书乘以 1.95583 还原成马克", MARK)
    S = series()
    band = S.loc["1972-01":"1973-01", "deu_eur"] * MARK
    dem = F["b72t_dem"]
    assert band.between(dem[4], dem[3]).all()                                    # 与中心汇率及幅度相合
    assert abs((S.loc["1970-01":"1970-12", "deu_eur"] * MARK).mean() / there("ch36_brettonwoods",
               "1969 年 10 月 26 日升到 3.66 马克")[3] - 1) < 0.01
    zeros = int((changes("gbp", FIXED, "relp") == 0).sum()) if False else \
        int((np.log(S.loc[FIXED[0]:FIXED[1], "cpi_gb"]).diff().dropna() == 0).sum())
    said("1960 年代各国的消费者价格指数常常几个月不变，英国 1960—1970 年的 132 个月度变化里有 76 个是零", 1960, 1960,
         1970, len(changes("gbp", FIXED)), zeros)
    steps = {}
    for c in ("cpi_us", *RATES.values()):                                       # the smallest change, % of the level
        x = S.loc[FIXED[0]:FIXED[1], c]
        d_ = (x.diff() / x.shift()).dropna().abs() * 100
        steps[c] = float(d_[d_ > 0].min())
    assert steps["cpi_gb"] > 0.75 and max(v for c, v in steps.items() if c != "cpi_gb") < 0.35, steps
    said("英国的指数一动至少约 0.8\\%，看来源头的数字取整较粗，1960 年代英国物价之比与实际汇率的标准差因此偏大",
         steps["cpi_gb"], 1960, slack=0.05)
    # rounding a smooth index to that step inflates the standard deviation of its monthly changes
    gb = np.log(S.loc[FIXED[0]:FIXED[1], "cpi_gb"])
    t_ = np.arange(len(gb))
    smooth = np.exp(np.polyval(np.polyfit(t_, gb.values, 3), t_))
    rough = np.round(smooth / (smooth[0] * steps["cpi_gb"] / 100)) * smooth[0] * steps["cpi_gb"] / 100
    assert np.diff(np.log(rough)).std(ddof=1) > 2 * np.diff(np.log(smooth)).std(ddof=1)   # 因此偏大
    V = {c: (volatility(c, FIXED), volatility(c, FLOAT)) for c in RATES}
    assert min(RATES, key=lambda c: V[c][1]["real"] / V[c][0]["real"]) == "gbp"      # the smallest 倍数 is sterling's
    yen = S["jpy"]
    at = yen[yen == 360].index
    assert len(at) == at[-1].ordinal - at[0].ordinal + 1 and at[0] == yen.index[0]   # one run, from the first month
    assert (yen.loc[at[-1] + 1:FIXED[1]] < 360).all()
    said("日元 1959 年 12 月到 1969 年 11 月的 120 个月都正好是 360 日元", at[0].year, at[0].month, at[-1].year,
         at[-1].month, len(at), F["boj_360"][2])
    said("1960 年代日元名义汇率的标准差因此偏小", 1960)


def legacy(F, Y, Q):
    has("b76_article4", "exchange rate arrangements of their choice")
    said("1985 年的广场协议在\\chref{ch:japanbubble}", *there("ch58_japanbubble", "追踪广场协议（1985）"))
    said("BIS 1976 年看到的就是这样一种局面", report("bis1976_46"))
    has("rich_7", "about 7 percent early in 1973")
    said("并用它来对付 1973 年初已升到约 7\\% 的通胀", F["rich_7"][1], F["rich_7"][0])
    said("1971 年日本的出口产地靠压价与加班消化升值", F["nx_date"][1])


def takeaways(F, Y, Q):
    d, y = F["nx_date"]
    said("1971 年 8 月 15 日，美国停止美元兑换黄金，加征 10\\% 的进口附加税", y, month("nx_date", "August"), d,
         F["nx_surcharge"][0])
    # the decision was not made at Camp David (FRUS: the meeting detailed a programme agreed on 2 and 12 August)
    say("方案的主要设计者是康纳利，国务院与国家安全委员会都没有参与")
    has("f164_architect", "primary architect")
    has("f168_absent", "were not represented at the Camp David meeting")
    said("史密森协定让美元对黄金贬值 7.9\\%，波动幅度放宽到平价上下各 2.25\\%", F["b72_smithsonian"][0],
         F["b72i_margins"][1])
    said("1973 年 3 月主要货币转向浮动，1976 年的牙买加协议承认了这个局面", F["f35_paris"][1], 3, F["b76_jamaica"][0])
    said("$\\mathrm{d}e/\\mathrm{d}m=1+1/\\lambda\\theta$", F["db_eq16i"][0], F["db_eq16i"][1])
    V = {c: (volatility(c, FIXED), volatility(c, FLOAT)) for c in RATES}
    ratios = [V[c][1][w] / V[c][0][w] for c in RATES for w in ("nominal", "real")]
    assert 2 < min(ratios) < 10 and max(ratios) > 20                            # 几倍到几十倍


def selfcheck(F, Y, Q):
    said("若 $\\lambda=4$ 而 $\\theta=1$，货币增加 8\\%", SC["lam"], SC["theta"], SC["dm"])
    said("日元对美元的中心汇率是 308 日元，比原来的 360 日元升值多少", F["b72t_jpy"][2], F["boj_360"][2])
    said("美元对黄金贬值 7.9\\%，黄金的美元价格上升多少", F["b72_smithsonian"][0])
    said("1971 年 12 月到 1973 年 2 月是几个月", F["nx_date"][1], 12, F["f35_paris"][1], 2)
    j2 = jump(SC["lam"], SC["theta"])
    said("$1+1/(4\\times1)=1.25$，汇率上升 $8\\times1.25=10\\%$，利率降 $8/4=2$ 个百分点", 1, 1, SC["lam"], SC["theta"],
         j2, SC["dm"], j2, j2 * SC["dm"], SC["dm"], SC["lam"], SC["dm"] / SC["lam"])
    th = theta(EX["lam"], EX["delta"], EX["sigma"], EX["pi"])
    over = (jump(EX["lam"], th) - 1) * EX["dm"]
    said("$5\\times\\mathrm{e}^{-2}\\approx0.68\\%$", over, 2 * th, path(2.0)["e"] - EX["dm"])
    J = F["b72t_jpy"]
    said("$360/308-1\\approx16.9\\%$，与表中对美元的升值相同", F["boj_360"][2], J[2], 1, (F["boj_360"][2] / J[2] - 1) * 100)
    assert round((F["boj_360"][2] / J[2] - 1) * 100, 1) == J[1]
    g = F["b72_smithsonian"]
    said("$1/(1-0.079)-1\\approx8.6\\%$，即从每盎司 35 美元升到 38 美元", 1, 1, g[0] / 100, 1,
         (1 / (1 - g[0] / 100) - 1) * 100, g[1], g[2])
    assert np.isclose(g[1] / (1 - g[0] / 100), g[2], atol=0.05)
    said("\\item 14 个月。", (F["f35_paris"][1] - F["nx_date"][1]) * 12 + 2 - 12)


def ending(F, Y, Q):
    d, y = F["nx_date"]
    said("回到 1971 年 8 月 15 日的晚上", y, month("nx_date", "August"), d)
    has("nx_tomorrow", "worth just as much tomorrow as it is today")
    said("他在 1973 年 2 月还提醒部下强调这一点", year_in("frus31d12_46", r"Policy, (\d{4})-"),
         month("f12_evening", "February"))
    J3 = F["bisdata_jpy7303"]
    assert 260 < J3[2] < 270
    said("到 1973 年 3 月，同样一美元在东京只能换 260 多日元，而不是 360 日元", J3[0], J3[1], 260, F["boj_360"][2])
    has("boj_oil", "産油国", "ドルを売却")
    assert tex_text().rstrip().endswith("（本书的解读）。" + NEXT)
    assert f"\\guidequestion{{{NEXT}}}" in chapter("ch47_oil")


def figures_data() -> None:
    """What the figures and their captions assert of their data."""
    S = series()
    assert len(S) == 313 and S.notna().all().all()
    for col in RATES:
        x = index(col)
        assert len(x) == 21 * 12 and np.isclose(100 * S.loc[BASE[0]:BASE[1], col].mean() / S.loc[BASE[0]:BASE[1], col]
                                                .mean(), 100)
    for v in VLINES:
        assert SPAN[0] <= v[:7] <= SPAN[1]
    t = np.linspace(-1, 5, 121)
    P = path(t)
    assert np.isclose(P["e"].max(), 15) and np.isclose(P["e"][-1], 10, atol=0.1) and np.isclose(P["p"][-1], 10, atol=0.1)
    assert np.isclose(P["i"].min(), -5) and (P["e"][t < 0] == 0).all()
    V = {c: (volatility(c, FIXED), volatility(c, FLOAT)) for c in RATES}
    assert all(V[c][1]["real"] > 2 * V[c][0]["real"] for c in RATES)
    print(f"ok the data of the figures: {len(S)} months; the example's theta {path(0)['theta']:.2f}; "
          f"{len(V)} currencies x 2 periods x 3 measures")


# ---------------------------------------------------------------------------------------------------
# 5. The book
# the life dates: words -> (row of the birth year, index), (row of the death year, index), row of the heading, heading
LIVES = {"Richard Nixon，1913—1994": (("loc_nixon", 0), ("loc_nixon", 1), "loc_nixon", "Nixon, Richard M."),
         "John B. Connally，1917—1993": (("loc_connally", 0), ("loc_connally", 1), "loc_connally",
                                        "Connally, John Bowden"),
         "George P. Shultz，1920—2021": (("loc_shultz", 0), ("loc_shultz", 1), "loc_shultz", "Shultz, George P."),
         "Henry Kissinger，1923—2023": (("loc_kissinger", 0), ("loc_kissinger", 1), "loc_kissinger", "Kissinger, Henry"),
         "Arthur F. Burns，1904—1987": (("loc_burns", 0), ("loc_burns", 1), "loc_burns", "Burns, Arthur F."),
         "Paul A. Volcker，1927—2019": (("loc_volcker", 1), ("loc_volcker_obit", 1), "loc_volcker_head",
                                       "Volcker, Paul A."),
         "Herbert Stein，1916—1999": (("loc_stein", 0), ("loc_stein", 1), "loc_stein", "Stein, Herbert"),
         "William E. Simon，1927—2000": (("loc_simon", 0), ("loc_simon", 1), "loc_simon", "Simon, William E."),
         "Rudiger Dornbusch，1942—2002": (("loc_dornbusch", 1), ("loc_dornbusch", 3), "loc_dornbusch_head",
                                         "Dornbusch, Rudiger"),
         "水田三喜男（1905—1976）": (("loc_mizuta", 0), ("loc_mizuta", 1), "loc_mizuta", "Mizuta, Mikio"),
         "爱知揆一（1907—1973）": (("loc_aichi", 0), ("loc_aichi", 1), "loc_aichi", "Aichi, Kiichi")}
# what other chapters tell: (words of this chapter, chapter where it is told, words there)
EVENTS = [("1946 年起，金价是每盎司 35 美元，盎司是称黄金用的重量单位", "ch36_brettonwoods", "盎司是称量黄金的重量单位"),
          ("美国是唯一按黄金钉住本国货币、买卖黄金的国家，其他国家都对美元定下平价", "ch36_brettonwoods",
           "美国是唯一按黄金钉住本国货币、买卖黄金的国家，其他国家都对美元定下平价"),
          ("\\chref{ch:brettonwoods}讲过它 1969 年的浮动", "ch36_brettonwoods", "马克的汇率浮动"),
          ("是因为 1967 年 11 月贬了值", "ch36_brettonwoods", "1967 年 11 月，英镑从 2.80 美元降到 2.40 美元"),
          ("马克 1961 年与 1969 年升值", "ch36_brettonwoods",
           "1961 年 3 月 6 日升到 4 马克；1969 年 10 月 26 日升到 3.66 马克"),
          ("日本守着 360 日元", "ch36_brettonwoods", "1949 年 4 月 25 日定为每美元 360 日元"),
          ("\\chref{ch:mundell}讲过加拿大 1950 年代的浮动", "ch37_mundell", "加拿大 1950 年代的浮动"),
          ("即\\chref{ch:mundell}的三选二", "ch37_mundell", "\\textbf{三选二。}"),
          ("这正是\\chref{ch:mundell}的三选二", "ch37_mundell", "\\textbf{三选二。}"),
          ("这个模型与蒙代尔—弗莱明模型问的不是一件事。那里物价固定", "ch37_mundell", "又假定短期里价格不动"),
          ("下面沿用\\chref{ch:external}的记号", "ch05_external", "汇率 $e$"),
          ("即式~\\eqref{eq:external-real}取对数", "ch05_external", "q=\\frac{e\\,P^{f}}{P},\\label{eq:external-real}"),
          ("式~\\eqref{eq:external-uip}取对数并略去小项，就是 $i=i^{f}+x$", "ch05_external",
           "\\frac{\\E_t e_{t+1}}{e_t}=\\frac{1+i}{1+i^{f}} .\\label{eq:external-uip}"),
          ("购买力平价成立", "ch05_external", "\\label{eq:external-ppp}"),
          ("\\chref{ch:external}讲过非抛补利率平价的失败（\\secref{sec:external-test}）", "ch05_external",
           "非抛补利率平价的失灵更彻底"),
          ("\\chref{ch:external}讲过非抛补利率平价的失败（\\secref{sec:external-test}）", "ch05_external",
           "\\label{sec:external-test}"),
          ("本书的 $r^{*}$ 留给中性利率", "ch25_wicksell", "今天的中性利率 $r^{*}$"),
          ("10 月初改为临时的汇率目标（\\chref{ch:monetarism}）", "ch45_monetarism", "10 月初，瑞士国家银行宣布临时的汇率目标"),
          ("瑞士国家银行 1978 年回头盯住过汇率（\\chref{ch:monetarism}）", "ch45_monetarism",
           "10 月初，瑞士国家银行宣布临时的汇率目标"),
          ("\\chref{ch:monetarism}讲的货币目标，就是在这个前提下定的", "ch45_monetarism",
           "控制货币数量就能控制通胀吗？"),
          ("货币长期中性", "ch45_monetarism", "长期中性"),
          ("油价在\\chref{ch:oil}", "ch47_oil", "用总供给冲击分析 1973 年与 1979 年的油价冲击"),
          ("理性预期在\\chref{ch:ratex}", "ch48_ratex", "区分适应性预期与理性预期"),
          ("美元 1980 年代前期的上涨在\\chref{ch:credibility}", "ch49_credibility", "用沃尔克反通胀（1979—1982）估算牺牲率"),
          ("后来走到了欧元，在\\chref{ch:euro}", "ch60_euro", "描述欧洲货币体系与汇率机制（1979）的运作"),
          ("1985 年的广场协议在\\chref{ch:japanbubble}", "ch58_japanbubble", "追踪广场协议（1985）")]
# the chapters this one names, and where their labels are
LATER = {"ch:brettonwoods": "ch36_brettonwoods", "ch:credibility": "ch49_credibility", "ch:euro": "ch60_euro",
         "ch:external": "ch05_external", "ch:japanbubble": "ch58_japanbubble", "ch:monetarism": "ch45_monetarism",
         "ch:mundell": "ch37_mundell", "ch:oil": "ch47_oil", "ch:ratex": "ch48_ratex"}
# the chapters that point here
POINTERS = ("ch05_external", "ch36_brettonwoods", "ch37_mundell", "ch42_eastasia", "ch45_monetarism", "ch47_oil")


def book(F, Q):
    """Life dates and what other chapters tell."""
    t = tex_text()
    for words, ((rb, ib), (rd, id_), head_row, head) in LIVES.items():
        assert words in t, words
        assert f"{F[rb][ib]:.0f}—{F[rd][id_]:.0f}" in words, (words, rb, rd)
        assert Q[head_row].startswith(head), (head_row, Q[head_row])             # the person of the record
        COVERED.append(words)
    # the second witnesses: Dornbusch's and Volcker's full dates
    has("loc_dornbusch", "b. June 8, 1942", "d. July 25, 2002")
    has("loc_volcker", "born September 5, 1927")
    has("loc_volcker_d", "died Dec. 8", "He was 92.")
    assert F["loc_volcker_obit"][1] - F["loc_volcker"][1] == F["loc_volcker_d"][1]   # born in September, died in December
    for here, ch, there_ in EVENTS:
        assert here in t, here
        assert there_ in chapter(ch), (ch, there_)
    named = set(re.findall(r"\\chref\{(ch:[^}]+)\}", t)) | set(re.findall(r"\\nameref\{(ch:[^}]+)\}", t))
    assert named == set(LATER), sorted(named ^ set(LATER))
    for label, ch in LATER.items():
        assert f"\\label{{{label}}}" in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (label, ch)
    for ch in POINTERS:
        assert re.search(r"\\(?:chref|ref|nameref)\{ch:floating\}", chapter(ch)), ch
    print(f"ok {len(LIVES)} life dates, {len(EVENTS)} statements of other chapters, {len(LATER)} other chapters named")


# the bibliography item of each source of the snapshots (the authority records: loc46)
ITEM_OF = {"nixon1971_46": "nixon1971", "nixon1971b_46": "nixon1971b",
           **{f"frus3d{n}_46": "frus46a" for n in (164, 165, 168, 211, 221)},
           **{f"frus31d{n}_46": "frus46b" for n in (12, 14, 33, 35)},
           "bis1972_46": "bis1972", "bis1972img_46": "bis1972", "bis1973_46": "bis1973", "bis1973img_46": "bis1973",
           "bis1974_46": "bis1974", "bis1976_46": "bis1976", "bisterms_46": "bis1972", "bislegal_46": "bisdata46",
           **{k: "bisdata46" for k in ("bisxrujp_46", "bisxrude_46", "bisxruch_46", "bisxrugb_46", "biscpius_46",
                                       "biscpijp_46", "biscpide_46", "biscpich_46", "biscpigb_46")},
           "pvma1972_46": "pvma1972", "pvma1972img_46": "pvma1972", "dornbusch1976_46": "dornbusch1976", "dornbusch1976img_46": "dornbusch1976",
           "meeserogoff1983_46": "meeserogoff1983", "meeserogoff1983img_46": "meeserogoff1983",
           "ifdp184img_46": "meese1981", "ifdp184land_46": "meese1981",
           "boj612img_46": "boj1986", "boj613img_46": "boj1986", "bojcopyright_46": "boj1986",
           "epa1972_46": "epa1972", "caorule_46": "epa1972", "pdl_46": "epa1972",
           "ojc38_46": "ojc1972", "eurlexlegal_46": "ojc1972",
           "rich2003_46": "rich2003", "powell2005_46": "powell2005", "bocterms_46": "powell2005"}
# the items shared with Chapters 37 and 45, outside the block: Powell (2005) and Rich (2003); the copies read for
# Chapter 46 have the same hashes as those of Chapters 37 and 45; the block asks the editor to merge the pages
SHARED = {"powell2005": ("mundell_facts", "powell2005"), "rich2003": ("monetarism_facts", "rich2003_45")}
SHARED_COPY = {"powell2005": "powell2005_46", "rich2003": "rich2003_46"}       # the copies of the other chapters
# the sources of each item whose pages it names (printed pages and PDF pages), by PDF
PAGES = {"bis1972": (("bis1972_46", "bis1972img_46"),), "bis1973": (("bis1973_46", "bis1973img_46"),),
         "bis1974": (("bis1974_46",),), "bis1976": (("bis1976_46",),), "pvma1972": (("pvma1972_46", "pvma1972img_46"),),
         "dornbusch1976": (("dornbusch1976_46", "dornbusch1976img_46"),),
         "meeserogoff1983": (("meeserogoff1983_46", "meeserogoff1983img_46"),),
         "boj1986": (("boj612img_46",), ("boj613img_46",)), "ojc1972": (("ojc38_46",),),
         "meese1981": (("ifdp184img_46",),)}


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
    """The bibliography block of Chapter 46, its items and all items of the bibliography."""
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    start = bib.index("% ---- 第 46 章")
    following = re.search(r"^% ---- 第 \d+ 章", bib[start + 1:], re.MULTILINE)
    end = start + 1 + following.start() if following else bib.index("\\end{thebibliography}")
    text = bib[start:end]
    assert bib.index("% ---- 第 45 章") < start
    items = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", text)}
    allitems = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", bib)}
    return text, items, allitems


def documents() -> dict[str, dict]:
    """Every document of the two snapshots of data/fetch/floating46.py."""
    out = dict(meta()["sources"])
    for key, src in load_snapshot("floating_bis_1959_1985")[1]["documents"].items():
        assert key not in out or out[key]["sha256"] == src["sha256"], key
        out[key] = src
    return out


def witnesses(F, Q):
    """The licences and the bibliography block of the chapter."""
    m = meta()
    lic = m["license"]
    lic_rows = ("bis_reuse", "bis_translation", "bis_original", "bisdata_terms", "db_copyright", "mr_publisher",
                "ifdp_cover", "boj_terms", "cao_rule", "cao_date", "pdl_numbers", "pdl_source", "pdl_edit",
                "eurlex_copy", "eurlex_policy", "eurlex_reuse", "eurlex_ack", "ecb_copy", "ecb_repro", "boc_permit",
                "boc_attrib")
    for rid in lic_rows:
        assert re.search(r"\brows? [^)]*\b" + rid + r"\b", lic), rid
        assert words_of(rid) in lic, rid
    for words in ("17 U.S.C. § 105", "no photographs are used"):
        assert words in lic, words
    assert words_of("bisdata_terms") in load_snapshot("floating_bis_1959_1985")[1]["license"]
    # the bibliography block of the chapter
    text, items, allitems = block()
    assert FETCH in text and "floating_facts" in text and "floating_bis_1959_1985" in text
    assert f"共 {len(items)} 条" in text
    unescape = lambda s: re.sub(r"\\([$%&_#~])", r"\1", s).replace("--", "-")     # noqa: E731 - as LaTeX prints it
    for rid, keys in (("bis_reuse", ("bis1972",)), ("bis_translation", ("bis1972",)), ("bis_original", ("bis1972",)),
                      ("bisdata_terms", ("bisdata46",)), ("boj_terms", ("boj1986",)),
                      ("cao_rule", ("epa1972",)), ("pdl_numbers", ("epa1972",)), ("pdl_source", ("epa1972",)),
                      ("pdl_edit", ("epa1972",)), ("eurlex_reuse", ("ojc1972",)), ("eurlex_ack", ("ojc1972",)),
                      ("db_copyright", ("dornbusch1976",)), ("ifdp_cover", ("meese1981",))):
        for key in keys:
            assert words_of(rid) in unescape(items[key]), (rid, key)
    for key in ("bis1972", "bis1973", "bis1974", "bis1976"):
        assert "the original content can be found at" in items[key], key
        assert "不是国际清算银行的官方译文" in items[key] and "This translation is not an official BIS translation" \
            in items[key], key
        assert "以国际清算银行为来源" in items[key], key
    assert "不是国际清算银行的官方译文" in items["bisdata46"] and "来源：国际清算银行" in items["bisdata46"]
    for key in ("nixon1971", "nixon1971b", "frus46a", "frus46b", "pvma1972"):
        assert "公有领域" in items[key] and "17 U.S.C. § 105" in items[key], key
    assert "Decision 2011/833/EU" in items["ojc1972"] and "本书据法文本翻译" in items["ojc1972"]
    assert "来源：日本银行" in items["boj1986"] and "出典：経済企画庁" in items["epa1972"]
    assert "只用来核对，不随本书分发" in items["dornbusch1976"] and "只用来核对，不随本书分发" in items["meeserogoff1983"]
    assert "公共数据" in items["loc46"]
    # every source is named by its URL and SHA-256 (the authority records by their URLs)
    for key, s in documents().items():
        item = "loc46" if key.startswith("loc_") else ITEM_OF[key]
        assert unescape(s["url"]) in unescape(allitems[item]), key
        if key in SHARED_COPY.values():
            snap, other = SHARED[item]
            assert load_snapshot(snap)[1]["sources"][other]["sha256"] == s["sha256"], key   # the copy of Ch 37 / 45
        elif item in SHARED:
            assert s["sha256"] in text, key                                     # named in the block's note
        elif not key.startswith("loc_"):
            assert s["sha256"] in items[item], key
    # the pages of each work, as the snapshot's rows have them
    for key, groups in PAGES.items():
        for srcs in groups:
            words = (f"第 {printed(srcs)} 页（PDF 第 {pdf(srcs)} 页）" if printed(srcs) else f"（PDF 第 {pdf(srcs)} 页）")
            assert words in items[key], (key, words)
    assert {k for g in PAGES.values() for s in g for k in s} == {k for k, s in meta()["sources"].items()
                                                                 if s["format"] in ("pdf", "image")} - set(SHARED_COPY.values())
    for key, src in SHARED_COPY.items():                                        # the editor merges them
        assert f"{key}：第 46 章用第 {printed((src,))} 页（PDF 第 {pdf((src,))} 页）" in text, (key, printed((src,)))
    for words, (_, _, head_row, _) in LIVES.items():
        assert Q[head_row].split(",")[0] in items["loc46"], head_row
    # the titles of the works as the documents print them
    has("oj_issue", "n° C 38", "18 avril 1972")
    for rid, key, words in (("db_title", "dornbusch1976", "Expectations and Exchange Rate Dynamics"),
                            ("oj_issue", "ojc1972", "Journal officiel des Communautés européennes"),
                            ("ifdp_land", "meese1981", "Empirical Exchange Rate Models of the Seventies: Are Any Fit "
                                                       "to Survive?"),
                            ("epa_title", "epa1972", "新しい福祉社会の建設"),
                            ("oj_date", "ojc1972", "21 mars 1972"),
                            ("b72t_title", "bis1972", "Realignment of leading currencies")):
        has(rid, words)
        assert words.lower() in unescape(items[key]).lower(), (rid, key)
    keys = set(allitems)
    cited = {k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", tex_text()) for k in c.split(",")}
    assert cited <= keys, sorted(cited - keys)
    assert set(items) == cited - set(SHARED) and set(SHARED) <= cited, sorted(set(items) ^ (cited - set(SHARED)))
    print(f"ok {len(cited)} works cited, {len(items)} in the bibliography block of Chapter 46")


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
    for words in ("谁作的决定？", "康纳利是这套方案的主要设计者", "他还说在任何情况下都不要与国务院商量",
                  "国务院与国家安全委员会没有派人", "最后由大藏大臣裁断", "大藏大臣爱知揆一（1907—1973）裁断",
                  "代价落在谁身上？附加税落在向美国出口的国家身上", "代价落在谁身上？首先是外汇储备",
                  "其次是出口产地", "再靠压低计件工钱、延长劳动时间来消化", "产地的工人多是家庭主妇与农民",
                  "他的理由“完全出于政治”", "这些美元按马克计都缩了水"):
        assert words in main_, words
    assert main_.count("代价落在谁身上？") == 2
    # documents are not the subjects of sentences: the author is named
    for bad in ("报告说", "演讲说", "演说说", "论文说", "书里说", "表说", "网页说", "年报说"):
        assert bad not in main_.replace("在报告里", ""), bad
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
    for words, k in (("本书的解读", 12), ("本书的计算", 6), ("本书的概括", 5), ("本书的推导", 5), ("本书的核对", 1)):
        assert main_.count(words) >= k, (words, main_.count(words))
    # sentences: one semicolon at most
    prose = re.sub(r"\\datasource\{[^\n]*", "", main_)
    for s in re.split(r"(?<=[。？！])|\n", re.sub(r"“[^”]*”", "“”", prose)):
        assert s.count("；") <= 1, s
    # the boxes the editor asks for
    assert t.count("\\begin{compare}") == 1 and t.count("\\begin{case}") == 2 and t.count("\\begin{pitfall}") == 1
    assert t.count("\\begin{deeper}[史料说明]") == 1 and t.count("\\begin{keyeq}") == 1
    assert t.count("\\begin{example}") == 1 and t.count("\\fig{") == 3 and t.count("\\begin{table}") == 2
    assert t.count(GUIDE) == 2
    # the neighbours' topics: a clause or a sentence each
    for label in ("ch:oil", "ch:ratex", "ch:credibility", "ch:euro", "ch:japanbubble"):
        assert t.count(f"\\chref{{{label}}}") <= 2, label
    # what Chapter 36 owns is not retold: Triffin and the gold pool
    for bad in ("特里芬", "Triffin", "黄金总库"):
        assert bad not in t, bad


def main() -> None:
    df = _rows()
    F, Y, Q = facts(), years(), quotes()
    check_readings(df)
    check_text(df)
    for part in (guide, opening, world, smithsonian, japan, europe, model, test, debate, deeper, legacy, takeaways,
                 selfcheck, ending):
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
