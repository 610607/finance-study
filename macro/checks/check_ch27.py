"""Chapter 27 (两次大战之间的金本位): every number and every quotation in zh/ch27_interwar.tex.

    python3 checks/check_ch27.py

Inputs:
  interwar_facts                      quotations of Hansard (the Commons, 28 April 1925; the Lords, 11 May 1925; the
                                      people pages), the Gold Standard Act 1925, Keynes (A Tract on Monetary Reform
                                      1923; The Economic Consequences of Mr. Churchill 1925), the Macmillan
                                      Committee's Minutes of Evidence, Brown (1940), Nurkse (1944), Dulles (1929),
                                      De Long and Shleifer (1990), McGrattan and Prescott (2003), Federal Reserve
                                      History, the Riksbank and Wikisource (checked by data/fetch/verify_web_quotes.py)
  boe_millennium_interwar_monthly     the Bank of England's millennium workbook, July 1914 - December 1931: the $/£
                                      rate, the Sauerbeck index, the cost of living, weekly wages, unemployment
  boe_millennium_bank_rate_1919_1931  the days on which Bank Rate changed
  boe_millennium_prices_1913_1931     the consumer prices of the UK and the US, annual
The figure module figsrc/fig_ch27.py imports monthly(), bank_rate(), ppp(), gold_reserves() and fx_shares() from here.

What is checked here:
  1. readings   every number of the value column of interwar_facts is read from its quotation (digits, English
                number words, ordinals, fractions, and the OCR's misprints, each named in the note)
  2. the text   every “…” of the chapter is the chapter's Chinese rendering of a quotation (TRANSLATIONS:
                rendering -> row or rows), with the source's words listed in KEYWORDS
  3. numbers    every number of the text, section by section: said() finds the phrase in the text and compares each
                number it prints (with its unit 万, 亿) with the value computed from the snapshots or with a teaching
                input stated in the text, within half a unit of the last printed digit; Chinese numerals (三成,
                三分之一, 十二 ...) are read by zh() and compared the same way
  4. coverage   every Arabic number of the text (outside labels, citations, cross-references, the key equations and
                math subscripts) lies inside a phrase checked by said(), so that changing any of them fails
  5. the book   life dates, what other chapters tell, the bibliography block of the chapter and its licence notices
  6. anchors    the paraphrase anchors `% 据: ...` name rows of interwar_facts

Models (the chapter's key equations):
    the real exchange rate (eq:interwar-parity, Chapter 5's eq:external-real): q = e P^f / P,
        q_1 / q_0 = (e_1 / e_0) (P^f_1 / P^f_0) / (P_1 / P_0); at the old parity (e_1 = e_0) the British price level that
        keeps the pre-war real rate is P_0 P^f_1 / P^f_0, and the PPP rate is 4.8665 (P^f_1/P^f_0) / (P_1/P_0) $/£
    the inverted pyramid (eq:interwar-pyramid): R = G + F, M <= R / c
    sterilization (eq:interwar-sterilize): H = A + R, Delta H = Delta A + Delta R; sterilized: Delta A = -Delta R
    the margin account: equity = position - loan; a fall of m wipes out a margin of m
"""
from __future__ import annotations

import math
import re
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd
from common import ROOT, anchors, load_snapshot, quoted

TEX = ROOT / "zh" / "ch27_interwar.tex"
# Teaching inputs stated in the text
SHILLINGS, PENCE = 20, 12                   # a pound is twenty shillings, a shilling twelve pence (Chapter 23)
PYRAMID = {"GA": 150, "GB": 40, "FB": 60, "c": Fraction(1, 3)}   # ex:interwar-pyramid
EQUITY, SMALL_LOAN = 1000, 1000             # ex:interwar-margin: own money; the loan of question (4)
SC2 = {"uk": 80, "us": 50}                  # self-check 2: price rises since before the war, per cent
SC4 = {"G": 20, "F": 80, "c": Fraction(1, 4)}   # self-check 4
SC5 = {"dR": 50, "sold": 50}                # self-check 5
SC7 = 25                                    # self-check 7: the margin, per cent
DECADE = 1920                               # "1920 年代"
GUIDE = "英国 1925 年按战前平价回到黄金，代价是什么？1920 年代的繁荣建立在什么之上？"
MONTHS = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10,
          "nov": 11, "dec": 12}


def chk(what: str, value, expected=None, tol: float = 1e-9, rel: float = 0.0) -> float:
    """quoted() with a tolerance for floating-point error on exact values; a list is compared element by element."""
    if isinstance(value, (list, tuple, np.ndarray, pd.Series)):
        value = list(value)
        assert expected is not None and len(value) == len(expected), (what, value, expected)
        for i, (v, e) in enumerate(zip(value, expected)):
            quoted(f"{what} [{i + 1}]", float(v), e, tol=tol, rel=rel)
        return float(value[0])
    return quoted(what, float(value), expected, tol=tol, rel=rel)


def pct(what: str, value: float, expected: float, digits: int = 1) -> float:
    """A number printed with `digits` decimals (half a unit of the last digit, plus room for binary rounding)."""
    return quoted(what, float(value), expected, tol=0.5 * 10 ** -digits + 1e-9)


# ---------------------------------------------------------------------------------------------------
# Loaders
def _rows() -> pd.DataFrame:
    df, meta = load_snapshot("interwar_facts", dtype=str, keep_default_na=False)
    assert 27 in meta["used_in"]
    assert df["id"].is_unique
    return df


def meta() -> dict:
    return load_snapshot("interwar_facts")[1]


def num(x: str) -> float:
    return float(x)


def facts() -> dict[str, list[float]]:
    """id -> the numbers of the value column (several are separated by ';')."""
    return {r.id: [num(x) for x in r.value.split(";")] for r in _rows().itertuples() if r.value}


def years() -> dict[str, int]:
    return {r.id: int(r.year) for r in _rows().itertuples() if r.year.isdigit()}


def quotes() -> dict[str, str]:
    """id -> the quotation, with the line breaks of the source joined."""
    return {r.id: " ".join(r.quote.split()) for r in _rows().itertuples()}


def column(name: str) -> dict[str, str]:
    return {r.id: getattr(r, name) for r in _rows().itertuples()}


def page(rid: str) -> int:
    """The page of a row: 'p. 615' -> 615, 'p. 240, Table 2' -> 240."""
    return int(re.match(r"p\. (\d+)", column("juan")[rid]).group(1))


def _boe(name: str) -> tuple[pd.DataFrame, dict]:
    df, m = load_snapshot(name)
    assert 27 in m["used_in"] and m["fetch"] == "data/fetch/boe_millennium_gb27.py"
    assert "4c23dd392a498691eac92659aec283fb43f28118bd80511dc87fc595974195eb" in m["notes"]
    assert "please cite this source" in m["license"]
    return df, m


def monthly() -> pd.DataFrame:
    """The monthly British series, July 1914 - December 1931, indexed by 'YYYY-MM' (NaN where the sheet is empty)."""
    df, m = _boe("boe_millennium_interwar_monthly")
    df.index = [f"{y}-{mo:02d}" for y, mo in zip(df.year, df.month)]
    assert df.index.is_unique and len(df) == 210 and df.index[0] == "1914-07" and df.index[-1] == "1931-12"
    assert df.usd_per_gbp.notna().all() and df.sauerbeck_1867_77_100.notna().all()
    assert df.cost_of_living_jul1914_100.notna().all() and df.wages_jan1939_100.loc["1919-01":].notna().all()
    assert "use unemp_admin" in m["notes"]
    return df


def bank_rate() -> pd.DataFrame:
    """Bank Rate: 1 January 1919 and every day on which it changed (ISO dates), with the new rate."""
    df, _ = _boe("boe_millennium_bank_rate_1919_1931")
    assert df.date.is_monotonic_increasing and df.date.iloc[0] == "1919-01-01"
    assert (df.bank_rate.diff().iloc[1:] != 0).all()
    return df


def rate_on(day: str) -> float:
    """Bank Rate on a day (the last change on or before it)."""
    b = bank_rate()
    return float(b[b.date <= day].bank_rate.iloc[-1])


def annual() -> pd.DataFrame:
    df, _ = _boe("boe_millennium_prices_1913_1931")
    df = df.set_index("year")
    assert list(df.index) == list(range(1913, 1932))
    return df


def mint_par() -> float:
    """Brown, p. 708: the mint par, dollars per pound."""
    return facts()["br_mintpar"][0]


def ppp() -> pd.Series:
    """The purchasing-power parity of each year 1913-1931, dollars per pound: the mint par times US consumer prices
    over UK consumer prices, both relative to 1913 (eq:interwar-parity; the book's own calculation)."""
    A = annual()
    uk = A.uk_cpi_2015_100 / A.uk_cpi_2015_100[1913]
    us = A.us_cpi_1982_84_100 / A.us_cpi_1982_84_100[1913]
    return mint_par() * us / uk


def rebased(col: str, base: str = "1924-01") -> pd.Series:
    """A monthly series of monthly() with base month = 100."""
    s = monthly()[col]
    return 100 * s / s[base]


def gold_reserves() -> tuple[list[int], dict[str, list[float]]]:
    """Nurkse, Appendix IV, Table 2: central gold reserves at the end of 1913, 1918, 1923 and 1928, million dollars of
    the old parity, for the United States, France, the United Kingdom and Germany."""
    F = facts()
    yrs = [int(y) for y in F["nu_t2head"][1:]]
    rows = {"us": F["nu_t2us"], "fr": F["nu_t2fr"], "uk": F["nu_t2uk"], "de": F["nu_t2de"]}
    return yrs, rows


def fx_shares() -> tuple[list[int], list[float], list[int]]:
    """Nurkse, p. 29: the share of foreign exchange in the reserves of the European central banks (per cent), with
    the number of banks: 1913 (fifteen banks), 1925 and 1928 (twenty-four)."""
    y0, n0, s0, y1, n1, s1, y2, s2 = facts()["nu_12_42"]
    return [int(y0), int(y1), int(y2)], [s0, s1, s2], [int(n0), int(n1), int(n1)]


def hansard_day(key: str) -> tuple[int, int, int]:
    """The sitting of a Hansard source from its URL: '.../commons/1925/apr/28/...' -> (1925, 4, 28)."""
    m = re.search(r"/(\d{4})/([a-z]{3})/(\d+)/", meta()["sources"][key]["url"])
    return int(m.group(1)), MONTHS[m.group(2)], int(m.group(3))


# ---------------------------------------------------------------------------------------------------
# 1. Readings of the numbers
SMALL = {"a": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "twelve": 12, "fifteen": 15, "seventeen": 17, "twenty": 20, "thirty": 30, "sixty": 60}
MULT = {"hundred": 100, "thousand": 1000}
ORDINAL = {"half": 2, "third": 3, "thirds": 3, "fifth": 5}
NTH = {"first": 1, "third": 3}
# misprints of the OCR, each named in the note of its row
OCR = {"10-1,-": 10.5, ",^1,000,000,000": 1e9, ",^750,000,000": 7.5e8, "i": 1, "9/to": 0.9, "31/2": 3.5, "i8": 18,
       "i888": 1888, "twentysix": 26, "i6s": 165, "III": 111, "ii 1.5": 111.5}


def cardinal(s: str) -> float:
    """An English cardinal: 'twelve', 'twenty-seven', 'four hundred'."""
    total, part = 0, 0
    for w in s.lower().replace("-", " ").split():
        if w in SMALL:
            part += SMALL[w]
        else:
            part = max(part, 1) * MULT[w]
            if MULT[w] >= 1000:
                total, part = total + part, 0
    return float(total + part)


def figure(s: str) -> float:
    """'1,290', '4.8665', '10½'."""
    s = s.replace(",", "")
    return float(s[:-1]) + 0.5 if s.endswith("½") else float(s)


def read(word: str, how: str) -> list[float]:
    if how == "num":
        return [figure(word)]
    if how == "en":
        return [cardinal(word)]
    if how == "frac":                          # 'one-third', 'two-thirds'
        a, b = word.lower().split("-")
        return [float(Fraction(int(cardinal(a)), ORDINAL[b]))]
    if how == "half":                          # '3½'; 'half'
        return [float(word[:-1]) + 0.5] if word.endswith("½") and len(word) > 1 else [0.5]
    if how == "nth":                           # 'the third quarter'
        return [float(NTH[word])]
    if how == "hm":                            # '4.30 P. m.': hours and minutes
        h, m = word.split(".")
        return [float(h), float(m)]
    if how == "pence":                         # 'tenpence halfpenny'
        return [10.5]
    if how == "fold":                          # 'six-fold', 'threefold'
        return [cardinal(word.replace("-fold", "").replace("fold", ""))]
    if how == "twice":
        return [2.0]
    if how == "years":                         # '1922-1938'
        a, b = word.split("-")
        return [float(a), float(b)]
    if how == "gap":                           # '12 1': a space inside the number
        return [float(re.sub(r"\D", "", word))]
    if how == "ocrpct":                        # '8%>'
        return [float(word.rstrip("%>"))]
    if how == "ocr":
        return [float(OCR[word])]
    raise ValueError(how)


FIGURES = re.compile(r"\d[\d,]*(?:\.\d+)?|\.\d+")
EN, NUM = "en", "num"
# id -> [(phrase, how)], in order. A phrase 'context|word' is searched as a whole and read from `word`. Rows not
# listed are read with all the figures of the quotation.
READINGS = {
    "hc_expires": [("31", NUM)],
    "hc_430": [("4.30", "hm")],
    "hc_400oz": [("400", NUM), ("£|3", NUM), ("17", NUM), ("10-1,-", "ocr")],
    "hc_credits": [("300", NUM)],
    "hc_exchange": [("two", EN)],
    "hl_threeres": [("three", EN)],
    "hl_threefour": [("three", EN), ("four", EN)],
    "hl_475": [("4.75", NUM), ("two", EN)],
    "hl_hunsdon_twelve": [("twelve", EN)],
    "hh_churchill": [("1874", NUM), ("1965", NUM)],
    "hh_pethick": [("1871", NUM), ("1961", NUM), ("1923", NUM)],
    "hh_norman": [("1871", NUM), ("1950", NUM)],
    "hh_bradbury": [("1872", NUM), ("1950", NUM), ("1925", NUM)],
    "hh_hunsdon": [("May 14, |1854", NUM), ("May 22, |1935", NUM), ("July 24, |1923", NUM)],
    "hh_chamberlain": [("1863", NUM), ("1937", NUM)],
    "hh_snowden": [("1864", NUM), ("1937", NUM)],
    "hh_clarendon": [("June 7, |1877", NUM), ("December 13, |1955", NUM), ("Earl of Clarendon October 2, |1914", NUM)],
    "hh_cunliffe": [("1920", NUM), ("1914", NUM)],
    "act_price": [("three", EN), ("seventeen", EN), ("tenpence halfpenny", "pence")],
    "act_bars": [("four hundred", EN)],
    "k23_genoa": [("1922", NUM)],
    "k23_oct": [("1923", NUM)],
    "k25_twothirds": [("two-thirds", "frac")],
    "k25_rentiers": [("10", NUM), (",^1,000,000,000", "ocr"), (",^750,000,000", "ocr")],
    "k25_billrate": [("i", "ocr")],
    "mc_kinderdate": [("6", NUM), ("1930", NUM)],
    "fbi_coal": [("1925", NUM), ("11.7", NUM), ("1924", NUM)],
    "fbi_subsidy": [("nine", EN)],
    "fbi_wpi": [("165.0", NUM), ("third", "nth"), ("1924", NUM), ("first", "nth"), ("1925", NUM), ("13", NUM),
                ("144.0", NUM), ("first", "nth"), ("1926", NUM), ("two", EN), ("173", NUM), ("third", "nth"),
                ("1924", NUM), ("171", NUM), ("first", "nth"), ("1926", NUM)],
    "br_copyright": [("1940", NUM)],
    "br_unpegged": [("1919", NUM)],
    "br_sergent": [("July |3", NUM), ("three", EN)],
    "br_caisse": [("two", EN)],
    "br_vigorous": [("31/2", "ocr"), ("4", NUM)],
    "br_125": [("125", NUM)],
    "br_655": [("25", NUM), ("1928", NUM), ("65.5", NUM), ("9/to", "ocr"), ("2", NUM)],
    "br_parisinterview": [("1927", NUM)],
    "br_trust": [("1923", NUM)],
    "br_aug5": [("5", NUM), ("4", NUM), ("3½", "half")],
    "br_1928up": [("25", NUM), ("3", NUM), ("1928", NUM), ("31/2", "ocr"), ("4", NUM)],
    "br_may18": [("i8", "ocr"), ("4½", "half")],
    "br_prewarpar": [("twenty-seven", EN), ("i888", "ocr"), ("1914", NUM), ("four", EN)],
    "br_mintpar": [("4.8665", NUM), ("84", NUM), ("11.4545", NUM)],
    "br_brokers": [("8", NUM), ("one", EN)],
    "br_june1928": [("1928", NUM)],
    "br_lendny": [("between |8", NUM), ("and |9", NUM)],
    "br_volume": [("1925", NUM), ("ii 1.5", "ocr"), ("1913", NUM), ("76.0", NUM), ("1913", NUM)],
    "br_coal1926": [("1926", NUM), ("£|43", NUM), ("£|34", NUM), ("1925", NUM), ("£|80", NUM), ("£|150", NUM)],
    "nu_third": [("one-third", "frac"), ("1915", NUM), ("1922", NUM)],
    "nu_12_42": [("1913", NUM), ("fifteen", EN), ("12", NUM), ("1925", NUM), ("twenty-four", EN), ("27", NUM),
                 ("1928", NUM), ("42", NUM)],
    "nu_receipt": [("33", NUM)],
    "nu_ratio33": [("33", NUM)],
    "nu_threefold": [("threefold", "fold")],
    "nu_26": [("twentysix", "ocr"), ("1922-1938", "years")],
    "nu_382": [("382", NUM), ("12 1", "gap"), ("32", NUM), ("232", NUM), ("60", NUM)],
    "nu_us46": [("1924", NUM), ("46", NUM), ("twice", "twice"), ("1914", NUM), ("23", NUM)],
    "nu_1925_28": [("four", EN), ("1925", NUM), ("-|28", NUM)],
    "nu_france8": [("8%>", "ocrpct"), ("1926", NUM), ("1931", NUM), ("24", NUM)],
    "nu_t2head": [("$|20.67", NUM), ("1913", NUM), ("1918", NUM), ("1923", NUM), ("1928", NUM)],
    "nu_t2uk": [("i6s", "ocr"), ("521", NUM), ("746", NUM), ("748", NUM)],
    "nu_t2de": [("279", NUM), ("539", NUM), ("III", "ocr"), ("650", NUM)],
    "du_onefifth": [("1926", NUM), ("one-fifth", "frac")],
    "du_copyright": [("1929", NUM)],
    "frh_dow": [("six-fold", "fold"), ("sixty-three", EN), ("1921", NUM), ("381", NUM), ("1929", NUM)],
    "frh_crash": [("28", NUM), ("1929", NUM), ("13", NUM), ("12", NUM), ("half", "half")],
    "dl_64": [("sixty-four", EN), ("1928", NUM), ("1929", NUM), ("thirty-three", EN), ("1929", NUM), ("1929", NUM)],
    "dl_half": [("one-half", "frac")],
    "ws_poincare": [("1860", NUM), ("1934", NUM)],
}
# the misprints of the OCR, each named in the note of its row
MISPRINTS = [("hc_400oz", "10-1,-"), ("k25_billrate", "'i per cent'"), ("br_655", "9/to"), ("br_vigorous", "31/2"),
             ("br_1928up", "31/2"), ("br_may18", "i8"), ("br_prewarpar", "i888"), ("nu_26", "twenty-six"),
             ("nu_t2uk", "i6s"), ("nu_t2de", "III"), ("br_volume", "ii 1.5"), ("nu_france8", "8%>"),
             ("nu_382", "12 1"), ("k25_rentiers", ",^"), ("act_coin", "botuid"), ("mc_play", "Kach"),
             ("hc_genoa", "airs"), ("nu_res9", "geld"), ("br_honor", "beefl"), ("br_coalgeneral", "2eneral"),
             ("hl_hunsdon_city", "Lad"), ("nu_statutes", "dl"), ("du_fifth", "france"), ("du_onefifth", "france")]


def check_readings(df: pd.DataFrame) -> None:
    n = 0
    for r in df.itertuples():
        if not r.value:
            assert r.id not in READINGS, r.id
            continue
        vals = [num(x) for x in r.value.split(";")]
        q = " ".join(r.quote.split())
        if r.id in READINGS:
            got, pos = [], 0
            for phrase, how in READINGS[r.id]:
                context, _, word = phrase.rpartition("|")
                k = q.find(context + word, pos)
                assert k >= 0, f"{r.id}: {phrase!r} not found (in order) in the quotation"
                pos = k + len(context + word)
                got += read(word, how)
        else:
            got = [figure(x) for x in FIGURES.findall(q)]
        assert [round(g, 6) for g in got] == [round(v, 6) for v in vals], f"{r.id}: read {got}, value column {vals}"
        n += 1
    quoted("rows with values, each read from its quotation", n, 142)
    N, Q = column("note"), quotes()
    for rid, word in MISPRINTS:
        assert word in N[rid], (rid, word)                  # every misprint is named in the note
        assert word.strip("'").replace("twenty-six", "twentysix") in Q[rid] or word == "'i per cent'", (rid, word)


# ---------------------------------------------------------------------------------------------------
# 2. Every “…” of the text against the snapshot
ALLOW = {"bound"}                          # the word the OCR misreads ('botuid', act_coin), named in the 史料说明
# the chapter's Chinese renderings of the quotations: rendering -> row (or rows)
TRANSLATIONS = {
    # opening
    "打算把一切相关的事实都考虑在内": "hc_relevant",
    "有点像题外话，却是我们财政政策必不可少的一部分": "hc_digression",
    "现在正是时候。": "hc_appointed",
    # sec:interwar-world
    "明确建议": "hl_cunliffe",
    "权威的表述": "nu_cunliffe",
    "把币值稳定在当前价值附近，不管它战前的价值": "k23_devaluation",
    "因为在一个贫穷的世界里，引起失业比让食利者失望更坏": "k23_worse",
    "我们都选了汇率稳定，不选物价稳定": "k23_plumped",
    "说实话，金本位已经是野蛮的遗物。": "k23_relic",
    "先是靠人们预期恢复金本位，再是靠恢复金本位这件事本身，而不是靠英镑内在价值的提高": "k25_october",
    # sec:interwar-parity
    "有条有理地列出了说服政府的论据": "hc_marshalling",
    "眼下还很坚挺": "hc_buoyant",
    "像港湾里的船，舷梯相连，随潮水一起升降": "hc_ships",
    "并不意味着我们要发行金币": "hc_nocoin",
    "为回到金本位提供便利": "act_title",
    "必要时连同贴现率一起": "hc_153m",
    "黄金储备、贴现率与外国信贷": "hl_threeres",
    "后果是严重的通缩": "rb_prewar",
    "这个国家没有别的路可走": "hl_nocourse",
    "都是自杀": "hl_trade",
    "它的好处是检验是自动的": "hl_automatic",
    "在这个意义上是人为的": "hl_artificial",
    "再用十二个月检验一下": "hl_hunsdon_twelve",
    "在几乎到达目标的时候掉头，是不可想象的": "hl_hunsdon_goal",
    # sec:interwar-keynes
    "要么外国买主得用他的钱多付 10\\%，要么我们得用我们的钱少收 10\\%": "k25_ten",
    "也许是最大的统计权威": "hl_475",
    "至少有三分之二是国际贸易的原料": "k25_twothirds",
    "用编法不同的指数作比较，想得出精确的结论是不安全的": "hl_para15",
    "第一批被要求接受 10\\% 削减的人": "k25_first",
    "直到经济上最弱的人被打倒在地": "k25_war",
    "通缩不会‘自动’降低工资。它靠制造失业来降低工资。": "k25_automatic",
    "可以有意把失业加剧到任何需要的程度，直到工资真的降下来": "k25_intensify",
    "必然带来失业和劳资纠纷": "k25_certain",
    "我会挑煤炭，它比谁都更是我们货币政策的牺牲品": "k25_coal",
    "经济巨轮的牺牲品": "k25_juggernaut",
    "他为什么做了这样一件蠢事？": "k25_silly",
    # sec:interwar-cost
    "前所未有的局面": "k25_billrate",
    "名义工资必须降低 10\\%，会造成严重的产业混乱": "fbi_warn",
    "1925 年决定性的因素是鲁尔区恢复了生产": "br_norman_ruhr",
    "其实是人为的": "br_norman_franc",
    "后来果然如此": "hl_hunsdon_wages",
    # sec:interwar-exchange
    "以外国存款的形式保有储备，节省黄金的使用": "nu_res9",
    "会立下大功": "k23_boldly",
    "根本算不上国际通货": "nu_notintl",
    "禁止英格兰银行把绝大部分黄金用在持有它的唯一用途上": "nu_fiduciary",
    "金本位游戏的全部规则": "k25_game",
    "某种共同的游戏规则": "mc_rules",
    "每个国家都应当守规则；不守，这套东西就运转不了。": "mc_play",
    "几乎是跪着求": "mc_bendedknees",
    "把国际局面置于自己的国内局面之下": "mc_domestic",
    # sec:interwar-gold
    "代别国保管的": "br_trust",
    "财政混乱已经把法国推到了革命的边缘": "br_poincare",
    "低估法郎的汇率": "br_undervalued",
    # sec:interwar-boom
    "新一轮投机的信号": "br_yield",
    "付价款的一部分，通常是 10\\%，其余借来": "frh_margin",
    "直接行动": "frh_direct",
    "完全是因为美国的对外贷款像洪水一样涌来": "br_flood",
    "至少比基本面高出 30\\%": "dl_30",
    "股市并没有被高估": "mp_opposite",
    "基本面很强，股市被低估了": "mp_fisher",
    "费雪说股价低": "mp_headline",
    # the 史料说明: Fisher's plateau (not quoted in the text), and the OCR's readings of Table 2
    "永久的高原": "frh_fisherquote",
    "i6s": "nu_t2uk",
    "III": "nu_t2de",
    # the ending
    "现在正是时候": "hc_appointed",
}
# the words of the source that each rendering renders
KEYWORDS = {
    "hc_relevant": ["proposes to take all relevant facts into consideration"],
    "hc_digression": ["something in the nature of a digression", "an essential part of our financial policy"],
    "hc_appointed": ["Now is the appointed time."],
    "hl_cunliffe": ["definitely recommended"],
    "nu_cunliffe": ["given authoritative expression"],
    "k23_devaluation": ["stabilising the value of the currency somewhere near its present value",
                        "without regard to its pre-war value"],
    "k23_worse": [("because it is worse, in an impoverished world, to provoke unemployment than to disappoint the "
                   "rentier")],
    "k23_plumped": ["we had all plumped for stability of exchange as against stability of prices"],
    "k23_relic": ["In truth, the gold standard is already a barbarous relic."],
    "k25_october": ["brought about first by the anticipation, and then by the fact, of the restoration of gold",
                    "not by an improvement in the intrinsic value of sterling"],
    "hc_marshalling": ["a reasoned marshalling of the arguments which have convinced His Majesty's Government"],
    "hc_buoyant": ["is at the moment buoyant"],
    "hc_ships": ["like ships in a harbour whose gangways are joined and who rise and fall together with the tide"],
    "hc_nocoin": ["does not mean that we are going to issue gold coinage"],
    "act_title": ["An Act to facilitate the return to a gold standard"],
    "hc_153m": ["if necessary with the Bank Rate"],
    "hl_threeres": ["The gold reserve, the bank rate and foreign credits"],
    "rb_prewar": ["The consequences were strong deflation"],
    "hl_nocourse": ["no other course is open to this country"],
    "hl_trade": ["would, in my opinion, have been suicidal"],
    "hl_automatic": ["The great advantage of the free market for gold is that the test is automatic"],
    "hl_artificial": ["in that sense the rise in sterling was artificial"],
    "hl_hunsdon_twelve": ["another twelve months in which to test the position"],
    "hl_hunsdon_goal": ["to turn back when we had practically reached the goal was unthinkable"],
    "k25_ten": ["either the foreign buyer has to pay 10 per cent more in his money",
                "or we have to accept 10 per cent less in our money"],
    "hl_475": ["perhaps the greatest statistical authority"],
    "k25_twothirds": ["made up to the extent of at least two-thirds from the raw materials of international commerce"],
    "hl_para15": [("it is not safe to attempt to draw precise conclusions from a comparison of index figures compiled "
                   "upon different bases")],
    "k25_first": ["the first to be asked to accept the 10 per cent reduction"],
    "k25_war": ["until those who are economically weakest are beaten to the ground"],
    "k25_automatic": ['Deflation does not reduce wages "automatically." It reduces them by causing unemployment.'],
    "k25_intensify": ["you can deliberately intensify unemployment to any required degree until wages do fall"],
    "k25_certain": ["It is certain to involve unemployment and industrial disputes."],
    "k25_coal": ["I should pick out coal as being above all others a victim of our monetary policy."],
    "k25_juggernaut": ["the victims of the economic Juggernaut"],
    "k25_silly": ["Why did he do such a silly thing?"],
    "k25_billrate": ["the unprecedented situation"],
    "fbi_warn": ["A serious industrial dislocation due to the necessity of reducing money wages by 10 per cent."],
    "br_norman_ruhr": ["It was the return of the Ruhr to production which was the decisive factor in 1925."],
    "br_norman_franc": ["which was really artificial"],
    "hl_hunsdon_wages": ["as indeed there has been"],
    "nu_res9": ["economizing the use of gold by maintaining reserves in the form of foreign balances"],
    "k23_boldly": ["a considerable service will be rendered"],
    "nu_notintl": ["the cover reserves were not really international currency at all"],
    "nu_fiduciary": [("to forbid the Bank of England to use by far the greater part of its gold for the only purpose "
                      "for which it is held or could be used")],
    "k25_game": ["by all the rules of the gold standard game"],
    "mc_rules": ["some sort of common rules of the game"],
    "mc_play": ["should play the game; if they do not, the thing cannot work."],
    "mc_bendedknees": ["America went on her bended knees, almost"],
    "mc_domestic": ["she had subjected the international situation to her domestic situation"],
    "br_trust": ["held in trust for other nations"],
    "br_poincare": ["financial chaos had brought France to the brink of revolution"],
    "br_undervalued": ["a rate that undervalued the franc"],
    "br_yield": ["a signal for renewed speculative activity on the New York Stock Exchange"],
    "frh_margin": ["Purchasers put down a fraction of the price, typically 10 percent, and borrowed the rest."],
    "frh_direct": ["a policy of direct action"],
    "br_flood": ["was due wholly to a flood of American foreign lending"],
    "dl_30": ["priced at least 30 percent above fundamentals"],
    "mp_opposite": ["the stock market was not overvalued"],
    "mp_fisher": ["fundamentals were strong and the stock market was undervalued"],
    "mp_headline": ['"Fisher Says Prices of Stocks Are Low,"'],
    "frh_fisherquote": ["what looks like a permanently high plateau"],
    "nu_t2uk": ["United Kingdom i6s"],
    "nu_t2de": ["Germany 279 539 III"],
}


def tex_text() -> str:
    return "\n".join(l for l in TEX.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("%"))


def text_quotations() -> list[str]:
    return re.findall(r"“([^”]*)”", tex_text())


def check_text(df: pd.DataFrame) -> None:
    ids = set(df["id"])
    Q = quotes()
    used, n = set(), 0
    for q in text_quotations():
        n += 1
        used.add(q)
        if q in ALLOW:
            continue
        assert q in TRANSLATIONS, f"not listed: “{q}”"
        t = TRANSLATIONS[q]
        for rid in (t,) if isinstance(t, str) else t:
            assert rid in ids, rid
            assert rid in KEYWORDS, f"{rid}: no KEYWORDS"
            if q.isascii():
                assert q in Q[rid], (q, rid)
    stale = (set(ALLOW) | set(TRANSLATIONS)) - used
    assert not stale, f"listed but not in the text: {sorted(stale)}"
    for rid, words in KEYWORDS.items():
        for w in words:
            assert w in Q[rid], f"{rid}: {w!r} not in the quotation"
    assert set(KEYWORDS) == {r for t in TRANSLATIONS.values() for r in ((t,) if isinstance(t, str) else t)}
    assert "botuid" in Q["act_coin"] and "'bound'" in column("note")["act_coin"]
    print(f"ok {n} quotations of the text found in the snapshot (or listed as exceptions)")


# ---------------------------------------------------------------------------------------------------
# 3. Numbers: said() and the parts of the text it does not read
UNITS = {"万亿": 10 ** 12, "亿": 10 ** 8, "万": 10 ** 4}
AMOUNT = re.compile(r"(\d[\d,]*(?:\.\d+)?½?)(?:\s*多?(万亿|亿|万))?")
# what is not a number of the story: labels, citations, cross-references, the key equations (models() reads them),
# the column specification of the table, and the subscripts of the math
MASKS = [re.compile(r"\\begin\{keyeq\}.*?\\end\{keyeq\}", re.DOTALL),
         re.compile(r"\\(?:label|cite|chref|secref|figref|tabref|exref|eqref|ref|nameref|url|fig)\{[^}]*\}"),
         re.compile(r"\\begin\{tabularx\}[^\n]*"),
         re.compile(r"_\{[^}]*\}|_\d")]
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
    """The phrase is in the text, and each number it prints (with its unit 万, 亿) is the value given, within half a
    unit of its last digit (plus `slack`, in the same units). None skips a number (one checked by an assertion)."""
    say(phrase)
    found = AMOUNT.findall(mask(phrase).replace("{,}", ","))
    assert len(found) == len(values), f"{phrase!r}: {len(found)} numbers {found}, {len(values)} values"
    for (digits, unit), v in zip(found, values):
        if v is None:
            continue
        scale = UNITS.get(unit, 1)
        d = digits.rstrip("½")
        decimals = len(d.split(".")[1]) if "." in d else (1 if digits.endswith("½") else 0)
        tol = (0.5 * 10 ** -decimals + slack) * scale
        quoted(f"{phrase[:60]!r}: {digits}{unit}", float(v), figure(digits) * scale, tol=tol + 1e-9 * scale)
    COVERED.append(phrase)


ZH_DIGITS = {"一": 1, "两": 2, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
ZH_UNITS = {"十": 10, "百": 100, "千": 1000, "万": 10 ** 4}


def zh(s: str) -> float:
    """A Chinese numeral of the text: '三', '十二', '二十', '三成', '三分之一', '十二分之十一', '百分之一'."""
    if "分之" in s:
        b, a = s.split("分之")
        return zh(a) / zh(b)
    if s.endswith("成"):
        return zh(s[:-1]) / 10
    if s == "一半":
        return 0.5
    total, part = 0, 0
    for ch in s:
        if ch in ZH_DIGITS:
            part = ZH_DIGITS[ch]
        else:
            unit = ZH_UNITS[ch]
            total += max(part, 1) * unit
            part = 0
    return float(total + part)


def told(phrase: str, pre: str, post: str = "") -> float:
    """The phrase is in the text; the Chinese numeral it prints between `pre` and `post` (to the end of the phrase when
    post is empty), read by zh(). The numeral is taken from the phrase, so a check against it fails when the text
    changes it."""
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


# ---------------------------------------------------------------------------------------------------
# 4. Numbers, section by section
M8, B9 = 10 ** 6, 10 ** 9                    # a million, a billion (American)


def guide(F, Y, Q):
    t = TEX.read_text(encoding="utf-8")
    assert f"\\guidequestion{{{GUIDE}}}" in t
    assert GUIDE in (ROOT / "zh" / "ch26_weimar.tex").read_text(encoding="utf-8")        # 第 26 章交来的问题
    said(GUIDE, hansard_day("hansard1925a")[0], DECADE)
    said("用凯恩斯《丘吉尔先生的经济后果》（1925）分析", Y["k25_ten"])
    said("概括 1920 年代美国的信贷扩张与 1929 年股市崩盘", DECADE, F["frh_crash"][1])


def opening(F, Y, Q):
    y, mo, d = hansard_day("hansard1925c")
    assert hansard_day("hansard1925a") == hansard_day("hansard1925b") == hansard_day("hansard1925d") == (y, mo, d)
    said("1925 年 4 月 28 日，英国下院照例先回答议员的质询", y, mo, d)
    assert "Leicester West" in Q["hh_pethick"]                                           # 代表莱斯特西区
    d1, y1, d2, y2 = F["hc_wpiask"]
    assert "1st April, 1914, and 1st April, 1925" in Q["hc_wpiask"]
    said("从 1914 年 4 月 1 日到 1925 年 4 月 1 日各涨了多少", y1, 4, d1, y2, 4, d2)
    y1, y0, uk, _, _ = F["hc_wpi71"]
    assert "for March, 1925" in Q["hc_wpi71"] and "March, 1914, of 71 per cent" in Q["hc_wpi71"]
    said("英国的指数 1925 年 3 月比 1914 年 3 月高 71\\%", y1, 3, y0, 3, uk)
    y1, y0, us = F["hc_wpi62"]
    assert "February, 1925" in Q["hc_wpi62"] and "February, 1914" in Q["hc_wpi62"]
    said("美国劳工统计局的指数，1925 年 2 月比 1914 年 2 月高 62\\%", y1, 2, y0, 2, us)
    said("讲 1925 年的前景以前", F["hc_digression"][0])
    said("1919 年春天以来，金币与金块没有许可证就不准运出英国", F["hc_since1919"][0])
    assert "Spring of 1919" in Q["hc_since1919"]
    said("管制的法律当年 12 月 31 日到期", 12, F["hc_expires"][0])
    assert "31st December" in Q["hc_expires"]
    h, mi = F["hc_430"]
    chk("    half past four in the afternoon (下午四点半)", [h, mi], [told("议事录在这句话后面记下了时间，下午四点半", "下午", "点半"), 30])
    assert "P. m." in Q["hc_430"]
    say("议事录在这句话后面记下了时间，下午四点半")
    m = meta()
    asked = [k for k in ("hansard1925a", "hansard1925b", "hansard1925c", "hansard1925d")
             if "private notice question of Mr. Pethick-Lawrence" in m["sources"][k]["version"]]
    chk("    the two questions of the morning (两个质询)", len(asked), told("上午的两个质询，问的正是这个平价", "上午的", "个质询"))
    par = mint_par()
    common = math.floor(par * 100) / 100                                               # 4.8665 is written 4.86
    said("一英镑合 4.86 美元，与大战以前一样", common)
    said("同一年，凯恩斯（John Maynard Keynes，1883—1946）说英镑的价值高了 10\\% 左右", None, None,
         F["k25_toohigh"][0])                                                         # life dates: book()
    assert Y["k25_toohigh"] == hansard_day("hansard1925a")[0]                           # 同一年
    a, b, _, _ = F["k25_gap"]
    q = "财政部的专家却以为只差两三个百分点"
    chk("    two or three points (两三个百分点)", [a, b], [told(q, "只差", "三个"), told(q, "只差两", "个百分点")])


def world(F, Y, Q):
    M, par = monthly(), mint_par()
    said("1919 年 3 月，英镑对美元的汇价不再由政府钉住", F["br_unpegged"][0], 3)
    assert "In March 1919" in Q["br_unpegged"]
    war = M.usd_per_gbp.loc["1916-01":"1918-12"]
    chk("    the war peg, 1916-1918: 36 months between 4.75 and 4.78", [war.min() > 4.75, war.max() < 4.78], [1, 1])
    said("它一直钉在比战前平价低 2\\% 左右的地方", 100 * (1 - war.mean() / par))
    said("后来靠 1920 年的金银出口管制法", F["hc_since1919"][1])
    rate, y = F["br_318"]
    said("英镑随即下跌，1920 年 2 月跌到 3.18 美元", y, 2, rate)
    assert "February 1920" in Q["br_318"]
    pct("    the monthly mean of February 1920, below par (三成)", 1 - M.usd_per_gbp["1920-02"] / par,
        told("按月平均，那个月的汇价比战前的平价低了三成", "低了"), 1)
    said("1918 年，人称坎利夫委员会的一个委员会研究了战后的通货问题", F["hl_cunliffe"][0])
    died, baron = F["hh_cunliffe"]
    said("坎利夫勋爵（Walter Cunliffe，卒于 1920），他 1914 年封为男爵", died, baron)
    assert "Baron Cunliffe December 14, 1914" in Q["hh_cunliffe"]
    said("1920 年 4 月 15 日，英格兰银行把贴现率提到 7\\%", 1920, 4, 15, rate_on("1920-04-15"))
    assert rate_on("1920-04-14") < rate_on("1920-04-15")
    S = M.sauerbeck_1867_77_100
    assert S.loc["1919-01":].idxmax() == "1920-04"                                       # 批发物价随即掉头
    said("索尔贝克指数（\\chref{ch:wicksell}）1920 年 4 月是 266，1922 年 12 月只有 129，跌掉了一半还多", 1920, 4,
         S["1920-04"], 1922, 12, S["1922-12"])
    v = told("1922 年 12 月只有 129，跌掉了一半还多", "跌掉了", "还多")
    assert v < 1 - S["1922-12"] / S["1920-04"] < v + 0.05                              # 一半还多: a little more
    C = M.cost_of_living_jul1914_100
    assert C["1914-07"] == 100 and C.idxmax() == "1920-11"
    said("生活费用指数以 1914 年 7 月为 100，从 1920 年 11 月的 276 降到 1922 年 12 月的 180", 1914, 7, C["1914-07"],
         1920, 11, C["1920-11"], 1922, 12, C["1922-12"])
    U = M.unemp_admin
    said("1920 年 6 月只有 2.6\\%，1921 年 5 月升到 23.4\\%", 1920, 6, U["1920-06"], 1921, 5, U["1921-05"])
    assert U.loc["1921-01":"1921-12"].idxmax() == "1921-05"
    W = M.wages_jan1939_100
    assert W.idxmax() == "1921-01"
    said("周工资指数从 1921 年 1 月的 147 降到 1922 年 12 月的 95，降了三分之一还多", 1921, 1, W["1921-01"], 1922, 12,
         W["1922-12"])
    v = told("降了三分之一还多", "降了", "还多")
    assert v < 1 - W["1922-12"] / W["1921-01"] < v + 0.05                              # 三分之一还多: a little more
    pct("    December 1922: the rate as a share of par (per cent)", 100 * M.usd_per_gbp["1922-12"] / par, 95, 0)
    said("到 1922 年 12 月，英镑已经回到战前平价的 95\\%", 1922, 12, 100 * M.usd_per_gbp["1922-12"] / par)
    said("凯恩斯在 1923 年的《货币改革论》里把两条路分开", Y["k23_deflation"])
    said("直到 1922 年 4 月的热那亚会议", 1922, 4)
    chk("    April 1922", F["k23_genoa"], [1922])
    assert "Genoa Conference of April 1922" in Q["k23_genoa"]
    said("到 1923 年 10 月，几乎没有哪个欧洲国家的当局讲明", F["k23_oct"][0], 10)
    assert "(October 1923)" in Q["k23_oct"]
    said("1924 年，英镑开始往上走。那年 1 月，一英镑还不到 4.3 美元，到 1925 年 4 月已接近 4.8 美元", 1924, 1,
         math.ceil(M.usd_per_gbp["1924-01"] * 10) / 10, 1925, 4, M.usd_per_gbp["1925-04"])
    assert M.usd_per_gbp["1924-01"] < 4.3 and M.usd_per_gbp["1925-04"] < 4.8
    assert M.usd_per_gbp["1924-01"] == M.usd_per_gbp.loc["1924-01":"1925-04"].min()
    said("凯恩斯把偏离均衡的起点定在 1924 年 10 月", F["k25_october"][0], 10)
    assert "began in October last (1924)" in Q["k25_october"]


def parity(F, Y, Q):
    par = mint_par()
    common = math.floor(par * 100) / 100
    said("\\section{回到 4.86 美元}", common)
    said("前任财政大臣斯诺登（Philip Snowden，1864—1937）1924 年在任时", *F["hh_snowden"], F["hh_snowden_office"][0])
    assert F["hh_snowden_office"][:2] == [1924, 1924]
    assert "Lord Bradbury" in Q["hc_chamberlain"] and "then a private Member" in Q["hc_chamberlain"]
    issues = re.search(r"amalgamation of (.+?) Note Issues", Q["hc_snowden"]).group(1).split(" and ")
    chk("    two note issues (两种钞票): " + " and ".join(issues), len(issues),
        told("研究财政部与英格兰银行两种钞票的合并", "英格兰银行", "种钞票"))
    q = "英国两边最大的两个制造业国家，美国和德国"
    assert "the United States and Germany" in Q["hc_exchange"]
    chk("    the two greatest manufacturing countries (两个)", F["hc_exchange"] + [len(["美国", "德国"])],
        [told(q, "最大的", "个制造业")] * 2)
    d, y = F["act_title"]
    said("5 月 13 日，《1925 年金本位法》生效", 5, d, y)
    assert "[13th May 1925.]" in Q["act_title"]
    said("一块约含 400 盎司纯金", F["act_bars"][0])
    chk("    the bars: the Act's 'four hundred' = Churchill's '400 fine ounces'", F["act_bars"][0], F["hc_400oz"][0])
    lsd = F["act_price"]
    chk("    the price: the Act = Churchill (£3 17s. 10½d.)", lsd, F["hc_400oz"][1:])
    said("价格是每盎司标准金 3 英镑 17 先令 10½ 便士", *lsd)
    q = "一英镑合二十先令，一先令合十二便士（\\chref{ch:goldstandard}）"
    chk("    a pound is twenty shillings (二十), a shilling twelve pence (十二)", [SHILLINGS, PENCE],
        [told(q, "一英镑合", "先令"), told(q, "一先令合", "便士")])
    # ex:interwar-parity
    standard = lsd[0] * SHILLINGS * PENCE + lsd[1] * PENCE + lsd[2]
    _, s, dd = F["br_mintpar"]
    fine = s * PENCE + dd
    usd = F["nu_t2head"][0]
    said("英格兰银行的黄金输出点，按每盎司 84 先令 11.4545 便士的金价计算", s, dd)
    said("美国的金价是每盎司纯金 20.67 美元\\cite{nurkse1944}。（1）", usd, 1)
    said("（2）一英镑能买多少纯金，在美国值多少美元？（3）最少一次买约 400 盎司纯金，要付多少英镑？", 2, 3,
         F["act_bars"][0])
    chk("    two British prices (两个英国的价格): the Act's and Brown's", len([lsd, F["br_mintpar"]]),
        told("（1）两个英国的价格各是多少便士", "（1）", "个英国"))
    said("（1）$3\\times240+17\\times12+10.5=934.5$便士，$84\\times12+11.4545=1019.4545$便士", 1, lsd[0],
         SHILLINGS * PENCE, lsd[1], PENCE, lsd[2], standard, s, PENCE, dd, fine)
    ratio = fine / standard
    said("$1019.4545/934.5\\approx1.0909=12/11$", fine, standard, ratio, 12, 11)
    chk("    = 12/11 exactly", ratio, 12 / 11, tol=1e-6)
    chk("    standard gold is eleven-twelfths fine (十二分之十一)", standard / fine,
        told("所以后一个是每盎司纯金的价格，标准金含纯金十二分之十一", "含纯金"), tol=1e-6)
    oz = SHILLINGS * PENCE / fine
    said("（2）一英镑是 240 便士，能买$240/1019.4545\\approx0.2354$盎司纯金，在美国值$0.2354\\times20.67\\approx4.866$美元",
         2, SHILLINGS * PENCE, SHILLINGS * PENCE, fine, oz, round(oz, 4), usd, oz * usd)
    pct("    the mint par computed = Brown's 4.8665 (four decimals)", oz * usd, par, 3)
    said("铸币平价是 4.8665 美元\\cite{brown1940}，通常写作 4.86", par, common)
    bars = F["act_bars"][0]
    said("（3）$400\\times1019.4545/240\\approx1{,}699$英镑，约 1,700 英镑", 3, bars, fine, SHILLINGS * PENCE,
         bars * fine / (SHILLINGS * PENCE), round(bars * fine / (SHILLINGS * PENCE), -2))
    pct("    about 1,700 (约 1,700, to the nearest hundred)", bars * fine / (SHILLINGS * PENCE) / 100, 17, 0)
    # the reserves
    said("英国已经积累了 1.53 亿英镑的黄金", F["hc_153m"][0])
    chk("    Clarendon's figure: the same 153 million", F["hl_153"], F["hc_153m"])
    assert "considered necessary by the Cunliffe Committee" in Q["hc_153m"]
    said("财政部为自己发行的钞票存着 2,700 万英镑黄金", F["hc_27m"][0])
    said("必要时可以在美国得到不少于 3 亿美元的信贷", F["hc_credits"][0] * M8)
    assert "not less than 300 million dollars" in Q["hc_credits"]
    said("克拉伦登伯爵（George Villiers，1877—1955）说，保卫汇价有三样东西", *F["hh_clarendon"][:2])
    chk("    who moved the second reading (二读)", 2, told("在上院提出二读的克拉伦登伯爵", "提出", "读的"))
    assert "second reading (the Earl of Clarendon" in meta()["sources"]["hansard1925e"]["version"]
    chk("    three resources (三样)", F["hl_threeres"], [told("保卫汇价有三样东西", "汇价有", "样东西")])
    # the others
    said("南非已经通知，从 7 月 1 日起回到旧本位", 7, F["hc_canada"][0])
    assert "as from 1st July" in Q["hc_canada"]
    said("瑞典更早，1924 年 3 月就回到了金本位", F["br_sweden"][0], 3)
    assert "in March 1924 Sweden" in Q["br_sweden"]
    # tab:interwar-returns
    it, fr = F["br_italy"], F["br_france"]
    said("\\caption{1924—1928 年回到黄金的几个国家}", F["br_sweden"][0], fr[1])
    said("瑞典 & 1924 年 3 月 & 战前对克朗的旧汇率", F["br_sweden"][0], 3)
    said("德国 & 1924 年 10 月 & 帝国马克是德国 1924 年定下的新货币单位", F["br_reichsmark"][0], 10, F["br_reichsmark"][0])
    assert "in October 1924" in Q["br_reichsmark"]
    dd, yy = F["br_aug23"]
    said("法律上是金汇兑本位，每美元 4.20 帝国马克，钉到 1926 年 8 月 23 日", F["br_420"][1], yy, 8, dd)
    assert "August 23, 1926" in Q["br_aug23"] and "4.20 reichsmarks" in Q["br_420"]
    said("英国 & 1925 年 4 月 28 日宣布，5 月 13 日立法 & 战前平价，每英镑 4.8665 美元", *hansard_day("hansard1925a"), 5,
         F["act_title"][0], par)
    said("荷兰与荷属东印度 & 1925 年 4 月 28 日 & 与英国同一天", *hansard_day("hansard1925a"))
    assert "simultaneously with us to-day" in Q["hc_holland"]
    said("澳大利亚 & 1925 年 4 月 28 日 & 当天取消黄金出口的限制", *hansard_day("hansard1925a"))
    assert "from to-day to abolish" in Q["hc_australia"]
    said("南非 & 1925 年 7 月 1 日 & 回到旧本位", hansard_day("hansard1925a")[0], 7, F["hc_canada"][0])
    said("意大利 & 1926 年 8 月事实上稳定，1927 年 12 月立法", it[0], 8, it[1], 12)
    assert "de facto in August 1926 and de jure in December 1927" in Q["br_italy"]
    said("法国 & 1926 年 12 月事实上稳定，1928 年 6 月 25 日立法 & 新平价，约为战前金价值的五分之一", fr[0], 12, fr[1], 6,
         F["br_655"][0])
    assert "de facto in December 1926 and de jure in June 1928" in Q["br_france"]
    chk("    one-fifth (五分之一)", F["du_onefifth"][1], told("新平价，约为战前金价值的五分之一", "金价值的"))
    for r in ("br_italy", "br_france"):
        chk(f"    {r}: two dates (两个日子), de facto and de jure", len(re.findall(r"de (?:facto|jure) in", Q[r])),
            told("意大利与法国按事实上的稳定与法律上的稳定分列两个日子", "分列", "个日子"))
    pages = [page(r) for r in ("br_sweden", "br_italy", "br_france", "br_655", "br_reichsmark", "br_aug23",
                               "br_mintpar")]
    said("Brown（1940）第 323、399—400、459、469、486、708 页；1925 年 4 月 28 日的下院议事录；《1925 年金本位法》",
         F["br_copyright"][0], *pages, *hansard_day("hansard1925a"), F["act_title"][1])
    said("Dulles（1929）第 297 页", F["du_copyright"][0], page("du_onefifth"))
    # Bradbury and Hunsdon
    born, died, baron = F["hh_bradbury"]
    said("布拉德伯里勋爵（John Bradbury，1872—1950）。他那年 1 月刚封男爵", born, died, 1)
    assert "Baron Bradbury January 28, 1925" in Q["hh_bradbury"] and baron == hansard_day("hansard1925a")[0]
    said("可是政府若宣布英镑不值 4.8 美元、大概只值 4.6 美元", *F["hl_460"])
    said("亨斯登勋爵（Herbert Gibbs，1854—1935）也签过坎利夫委员会的报告", *F["hh_hunsdon"][:2])
    assert "sign the Cunliffe Report" in Q["hl_hunsdon_sign"]
    chk("    twelve months (十二个月)", F["hl_hunsdon_twelve"], [told("再用十二个月检验一下", "再用", "个月")])


def keynes(F, Y, Q):
    ten, a, b = F["k25_ten"]
    said("回到黄金以前，英镑比战前的金价值低 10\\% 左右", ten)
    said("“要么外国买主得用他的钱多付 10\\%，要么我们得用我们的钱少收 10\\%”", a, b)
    t, s = F["k25_two_s"]
    said("这等于迟早把每个人的工资每英镑减掉 2 先令", s)
    chk("    10 per cent of a pound is 2 shillings", t / 100 * SHILLINGS, s)
    said("2 先令是一英镑的十分之一", s)
    chk("    a tenth (十分之一)", s / SHILLINGS, told("2 先令是一英镑的十分之一", "一英镑的"))
    said("他的文章叫《丘吉尔先生的经济后果》，1925 年发表", Y["k25_ten"])
    said("下标 0 表示战前，1 表示 1925 年", 0, 1, Y["k25_ten"])
    par = mint_par()
    said("每英镑$4.8665\\times(P^{f}_1/P^{f}_0)/(P_1/P_0)$美元", par)
    uk, us = F["hc_wpi71"][2], F["hc_wpi62"][2]
    over_w = (1 + uk / 100) / (1 + us / 100) - 1
    said("用当天上午贸易部给的批发物价，英国涨了 71\\%，美国涨了 62\\%，英镑约高估 5.6\\%", uk, us, 100 * over_w)
    A = annual()
    cuk = A.uk_cpi_2015_100[1925] / A.uk_cpi_2015_100[1913]
    cus = A.us_cpi_1982_84_100[1925] / A.us_cpi_1982_84_100[1913]
    over_c = cuk / cus - 1
    said("用英格兰银行汇编的消费物价，1913—1925 年英国涨了 95\\%，美国涨了 83\\%，英镑约高估 6.6\\%", 1913, 1925,
         100 * (cuk - 1), 100 * (cus - 1), 100 * over_c)
    q = "美国物价大概还比英国低三四个百分点"
    chk("    three or four points (三四个百分点)", F["hl_threefour"], [told(q, "英国低", "四个"), told(q, "英国低三", "个百分点")])
    said("两国的物价相当于一英镑合 4.75 美元，差距只有 2\\% 左右", *F["hl_475"])
    pct("    4.8665 / 4.75 - 1 is about 2 per cent (约 2%)", 100 * (par / F["hl_475"][0] - 1), F["hl_475"][1], 0)
    said("凯恩斯的数字是 10\\% 到 12\\%", *F["k25_gap"][2:])
    # ex:interwar-index
    y1, y0 = F["hc_wpi71"][:2]
    said("用式~\\eqref{eq:interwar-parity}估算 1925 年英镑高估了多少，战前的平价是每英镑 4.8665 美元", y1, par)
    said("（1）英国的批发物价，1925 年 3 月比 1914 年 3 月高 71\\%；美国的，1925 年 2 月比 1914 年 2 月高 62\\%", 1, y1, 3,
         y0, 3, uk, y1, 2, y0, 2, us)
    said("（2）英格兰银行汇编的消费物价，1925 年英国是 1913 年的 1.946 倍，美国是 1.826 倍", 2, 1925, 1913, cuk, cus)
    said("（3）统计权威的 4.75 美元对应高估百分之几？（4）按凯恩斯的 10\\%，购买力平价是多少？", 3, F["hl_475"][0], 4,
         F["k25_toohigh"][0])
    W1, W0 = 1 + uk / 100, 1 + us / 100
    said("（1）$4.8665\\times1.62/1.71\\approx4.61$美元。$1.71/1.62-1\\approx5.6\\%$，英镑约高估 5.6\\%", 1, par, W0, W1,
         par * W0 / W1, W1, W0, 1, 100 * over_w, 100 * over_w)
    said("英国物价要降$1-1.62/1.71\\approx5.3\\%$", 1, W0, W1, 100 * (1 - W0 / W1))
    r = round(cuk, 3) / round(cus, 3)
    said("（2）$1.946/1.826\\approx1.066$，约高估 6.6\\%", 2, cuk, cus, r, 100 * (r - 1))
    said("购买力平价约$4.8665/1.066\\approx4.57$美元，英国物价要降约 6.2\\%", par, r, par / r, 100 * (1 - 1 / r))
    said("（3）$4.8665/4.75-1\\approx2.5\\%$，与布拉德伯里转述的约 2\\% 相去不远", 3, par, F["hl_475"][0], 1,
         100 * (par / F["hl_475"][0] - 1), F["hl_475"][1])
    said("（4）$4.8665/1.10\\approx4.42$美元。四种算法从 2\\% 到 12\\%", 4, par, 1 + F["k25_toohigh"][0] / 100,
         par / (1 + F["k25_toohigh"][0] / 100), F["hl_475"][1], F["k25_gap"][3])
    reckonings = [100 * over_w, 100 * (r - 1), 100 * (par / F["hl_475"][0] - 1), F["k25_toohigh"][0]]
    chk("    four reckonings (四种): wholesale, consumer prices, the authority, Keynes", len(reckonings),
        told("四种算法从", "", "种算法"))
    chk("    at least two-thirds (三分之二)", F["k25_twothirds"], [told("至少有三分之二是国际贸易的原料", "至少有", "是国际")],
        tol=1e-6)
    assert "paragraph 15" in Q["hl_para15"]
    said("1925 年春天，英美两国的批发物价只差几个百分点，看上去 4.86 美元并不离谱", Y["hc_wpi71"],
         math.floor(par * 100) / 100)
    t, bn, dbt = F["k25_rentiers"]
    said("英镑升值 10\\%，大约把 10 亿英镑从其余人的口袋转进食利者的口袋，国债的实际负担增加约 7.5 亿英镑", t, bn, dbt)
    said("因为它们是“第一批被要求接受 10\\% 削减的人”", F["k25_first"][0])
    said("按黄金计，英国的工资一年里涨了 15\\%，比利时、法国、意大利与德国的工人，金工资低 30\\% 也不损失实际工资",
         F["k25_fifteen"][0], F["k25_thirty"][0])
    assert "a year ago" in Q["k25_fifteen"]
    said("结论是英国的工资与物价大约高了 10\\%", F["k25_toohigh"][0])


def cost(F, Y, Q):
    M, B, par = monthly(), bank_rate(), mint_par()
    said("1925 年 3 月 5 日，英格兰银行把贴现率从 4\\% 提到 5\\%", 1925, 3, 5, rate_on("1925-03-04"), rate_on("1925-03-05"))
    chk("    = the FBI's 'an increase of the Bank Rate to 5 per cent' in March 1925", F["fbi_rate"], [1925, 5])
    assert "then in March the bank-rate was raised" in Q["k25_march"]
    y25 = B[(B.date > "1925-03-05") & (B.date < "1926-01-01")]
    chk("    the changes after March 1925: two cuts (两次), the first in August, then back to 5 in December",
        [len(y25), y25.bank_rate.iloc[0] < 5, y25.bank_rate.iloc[1] < y25.bank_rate.iloc[0], int(y25.date.iloc[0][5:7]),
         int(y25.date.iloc[2][5:7]), y25.bank_rate.iloc[2]], [3, 1, 1, 8, 12, 5])
    said("8 月以后，贴现率降了两次，12 月又回到 5\\%", 8, 12, rate_on("1925-12-31"))
    said("伦敦的票据利率比纽约高出 1 个百分点", F["k25_billrate"][0])
    n, y0, y1, k = F["br_prewarpar"]
    said("1888—1914 年的 27 年里，英镑的年平均汇价只有 4 年低于平价", y0, y1, n, k)
    chk("    1888-1914 is twenty-seven years", y1 - y0 + 1, n)
    a, b, y, avg, _ = F["br_par"]
    said("1925—1931 年，年平均汇价高于平价的只有 1928 年，也只高出一点", a, b, y)
    pct("    Brown's 1928 average above par (four decimals)", avg - par, 0.0001, 4)
    U = M.unemp_admin
    said("1925 年 4 月，行政失业率是 10.9\\%，是 1914 年 7 月的三倍", 1925, 4, U["1925-04"], 1914, 7)
    pct("    three times July 1914 (三倍)", U["1925-04"] / U["1914-07"], told("是 1914 年 7 月的三倍", "月的", "倍"), 0)
    five = U.loc["1925-05":"1930-04"]
    chk("    the five years after April 1925 (五年): 60 months, none below 8", [len(five), five.min() >= 8],
        [12 * told("此后五年，它没有一个月低于", "此后", "年"), 1])
    for q in ("失业率五年里没有低于", "代价是五年没有降下来的失业"):
        chk(f"    {q}", len(five) / 12, told(q, "失业率" if q.startswith("失业率") else "代价是", "年"))
    said("此后五年，它没有一个月低于 8\\%", math.floor(five.min()))
    said("最低的是 1927 年 5 月的 8.7\\%，1929 年 10 月仍有 10.3\\%", 1927, 5, five.min(), 1929, 10, U["1929-10"])
    assert five.idxmin() == "1927-05"
    said("“名义工资必须降低 10\\%，会造成严重的产业混乱”", F["fbi_warn"][0])
    w = F["fbi_wpi"]
    said("1924 年第三季度与 1925 年第一季度都是 165.0。到 1926 年第一季度末，它降了 13\\%，只有 144.0", w[2], w[4], w[0],
         w[8], w[5], w[6])
    q = "1924 年第三季度与 1925 年第一季度都是 165.0。到 1926 年第一季度末"
    chk("    the third quarter (第三), the first (第一)", [w[1], w[3], w[7]],
        [told(q, "1924 年第", "季度"), told(q, "1925 年第", "季度"), told(q, "1926 年第", "季度末")])
    pct("    144.0 / 165.0 - 1 (per cent)", 100 * (1 - w[6] / w[0]), w[5], 0)
    said("劳工部的生活费用指数只降了两点，从 173 降到 171", w[10], w[13])
    two = told("劳工部的生活费用指数只降了两点", "只降了", "点")
    chk("    two points (两点)", [w[9], w[10] - w[13]], [two, two])
    W = M.wages_jan1939_100
    said("英格兰银行汇编的周工资指数，1924 年 1 月是 92，1929 年 10 月是 94，几乎没有动", 1924, 1, W["1924-01"], 1929, 10,
         W["1929-10"])
    C = M.cost_of_living_jul1914_100
    gw, gc = W["1929-10"] / W["1924-01"] - 1, C["1929-10"] / C["1924-01"] - 1
    said("1924 年 1 月到 1929 年 10 月，周工资指数涨了约 2.5\\%，生活费用指数降了约 6.8\\%", 1924, 1, 1929, 10, 100 * gw,
         -100 * gc)
    pct("    real wages up about a tenth (一成)", (1 + gw) / (1 + gc) - 1, told("有工作的人，实际工资约升了一成", "约升了"), 2)
    said("按凯恩斯的算法，得到了 10 亿英镑", F["k25_rentiers"][1])
    y, im, base, ex, _ = F["br_volume"]
    said("1925 年英国的进口量是 1913 年的 111.5\\%，出口量只有 76\\%", y, base, im, ex)
    assert "According to the Midland Bank" in Q["br_volume"]
    y, c, _ = F["fbi_coal"]
    said("1925 年第二、三季度，英国的产煤量比上年同期少 11.7\\%", y, c)
    assert "second and third quarters of 1925" in Q["fbi_coal"] and F["fbi_coal"][2] == y - 1     # 上年同期
    said("政府答应在 9 个月里补贴矿主按现行工资付薪的亏损", F["fbi_subsidy"][0])
    said("1926 年，劳资冲突发展成了总罢工", F["mc_general"][0])
    said("行政失业率从 1926 年 4 月的 9.1\\% 跳到 5 月的 14.3\\%", 1926, 4, U["1926-04"], 5, U["1926-05"])
    y, ci, ce, y0, ti, te = F["br_coal1926"]
    said("1926 年，英国第一次进口煤，进口额达 4,300 万英镑，出口额比 1925 年少了 3,400 万英镑", y, ci * M8, y0, ce * M8)
    said("这一年总进口减少了 8,000 万英镑，总出口却减少了 1.5 亿英镑", ti * M8, te * M8)
    assert "For the first time England imported coal" in Q["br_coal1926"]
    said("诺曼（Montagu Norman，1871—1950）不认为回到黄金是祸根", *F["hh_norman"])
    a, b = F["br_norman_ruhr"]
    said("不管回不回黄金，1926 年都会有煤矿停工，“1925 年决定性的因素是鲁尔区恢复了生产”", a, b)
    said("鲁尔区在 1923 年被法国与比利时占领", 1923)                              # Chapter 26 (EVENTS)
    said("他还说，1925 年要是不回到黄金，情形会越来越糟", F["br_norman_worse"][0])
    said("他也承认，1926 年法郎贬值，曾让英镑显得很强", F["br_norman_franc"][0])
    common = math.floor(par * 100) / 100
    said("\\begin{compare}{4.86 美元是不是错了}", common)
    said("\\cmprow{差距多大}{10\\%—12\\%，看生活费用、工资与制成品出口的价格}{三四个百分点，统计权威说约 2\\%", *F["k25_gap"][2:],
         F["hl_475"][1])
    said("\\cmprow{后来的证据}{失业率五年里没有低于 8\\%；批发物价降了 13\\%，生活费用只降两点}{诺曼说，1926 年的煤矿停工另有原因",
         math.floor(five.min()), w[5], F["br_norman_ruhr"][0])


def exchange(F, Y, Q):
    third, y0, y1 = F["nu_third"]
    said("1915—1922 年，世界的黄金产量下降了约三分之一", y0, y1)
    chk("    about one-third (三分之一)", third, told("世界的黄金产量下降了约三分之一", "下降了约"), tol=1e-6)
    said("1922 年的热那亚会议，最主要的建议就是尽量推广金汇兑本位", F["nu_genoa"][0])
    assert "The chief recommendation of the Genoa Conference" in Q["nu_genoa"]
    res = int(re.search(r"Resolution (\d+)", column("note")["nu_res9"]).group(1))
    said("会议的第 9 项决议说", res)
    y0, n0, s0, y1, n1, s1, y2, s2 = F["nu_12_42"]
    said("1913 年，欧洲 15 家中央银行的储备里，外汇约占 12\\%", y0, n0, s0)
    said("1925 年，24 家欧洲中央银行的黄金与外汇储备里，外汇占 27\\%，1928 年升到 42\\%", y1, n1, s1, y2, s2)
    said("帝国马克是德国 1924 年定下的新货币单位，银行券不兑换黄金", F["br_reichsmark"][0])
    dd, yy = F["br_aug23"]
    said("帝国银行按每美元 4.2 帝国马克的价格买卖外汇，一直钉到 1926 年 8 月 23 日", F["br_420"][1], yy, 8, dd)
    chk("    4.20 on p. 469 and p. 486", F["br_420end"], [F["br_420"][1]])
    said("\\cmprow{国内流通的钱}{金币与可兑换的银行券（\\chref{ch:goldstandard}）}{钞票；英国 1925 年以后只卖 400 盎司的金块}",
         F["act_title"][1], F["act_bars"][0])
    said("\\cmprow{1913 年与 1928 年的欧洲}{外汇约占储备的 12\\%}{外汇占 42\\%}", y0, y2, s0, s2)
    r33 = F["nu_ratio33"][0]
    said("准备比率是 33\\% 时，黄金每增减一个单位，信用的基础就要扩张或收缩三倍", r33)
    k = told("信用的基础就要扩张或收缩三倍", "收缩", "倍")
    chk("    threefold (三倍) = 1 / 33%", [F["nu_threefold"][0], round(100 / r33)], [k, k])
    chk("    every third note (每三张)", round(100 / F["nu_receipt"][0]), told("每三张钞票就有一张", "每", "张钞票"))
    said("按 33\\% 的准备比率，每三张钞票就有一张实际上是黄金的仓单", F["nu_receipt"][0])
    assert "every third bank note" in Q["nu_receipt"]
    said("1920 年代各国稳定币值时，信心像是头等大事", DECADE)
    assert "during the 'twenties" in Q["nu_confidence"]
    said("1920 年代后半期，这样的事已经开始", DECADE)
    sh = F["nu_shift"]
    assert all(y >= DECADE + 5 for y in sh)                                              # 后半期
    said("1925 年德国把大部分外汇储备换成黄金，1926 年匈牙利也这样做，1928 年意大利和波兰又把一部分外汇换成了黄金", *sh)
    y1, lo, hi, y0 = F["nu_reichsbank"]
    said("1924 年是 61\\%，1928 年降到 16\\%", y0, hi, y1, lo)
    # ex:interwar-pyramid
    GA, GB, FB, c = PYRAMID["GA"], PYRAMID["GB"], PYRAMID["FB"], PYRAMID["c"]
    said("设储备中心国 A 有黄金 150。外围国 B 有黄金 40，另有存在 A 的外汇 60。两国的发行准备比率都是$c=1/3$", GA, GB, FB,
         c.numerator, c.denominator)
    said("（1）两国的储备与货币上限各是多少？世界的储备有多少？（2）B 把 60 的外汇全部向 A 换成黄金", 1, 2, FB)
    said("（3）世界的黄金变了没有？储备变了多少？", 3)
    RB = GB + FB
    said("（1）B 的储备$R_B=40+60=100$，货币上限$100/(1/3)=300$。A 的储备 150，货币上限 450", 1, GB, FB, RB, RB,
         c.numerator, c.denominator, RB / c, GA, GA / c)
    said("世界的储备$150+100=250$，其中黄金 190", GA, RB, GA + RB, GA + GB)
    said("（2）B 的储备仍是 100，全是黄金，货币上限仍是 300。A 的黄金降到 90，货币上限降到 270，少了 180", 2, GB + FB,
         (GB + FB) / c, GA - FB, (GA - FB) / c, FB / c)
    said("（3）黄金仍是 190，只是从 A 搬到了 B。世界的储备从 250 降到 190，少掉的 60 正是消失的外汇", 3, GA + GB, GA + RB,
         GA + GB, FB)
    said("A 要守住准备比率，货币就要收缩 180，是兑换额的三倍", FB / c)
    chk("    three times (三倍)", 1 / c, told("是兑换额的三倍", "兑换额的", "倍"))
    # the rules of the game
    said("1925 年，凯恩斯写道，按照“金本位游戏的全部规则”", Y["k25_game"])
    d, y = F["mc_kinderdate"]
    said("1930 年 2 月 6 日，英格兰银行的董事金德斯利", y, 2, d)
    assert "6 February, 1930" in Q["mc_kinderdate"]
    n, y0, y1 = F["nu_26"]
    said("按年度数据，1922—1938 年 26 个国家共有 382 个观察值", y0, y1, n, F["nu_382"][0])
    obs, plus, pp, minus, pm = F["nu_382"]
    said("国内资产与国际资产同向变动的有 121 个，占 32\\%", plus, pp)
    pct("    121 / 382 (per cent)", 100 * plus / obs, pp, 0)
    said("反向变动的有 232 个，占 60\\%", minus, pm)
    assert 60 < 100 * minus / obs < 61                                                    # Nurkse prints 60%
    said("按 Bloomfield 对 1880—1914 年的统计，遵守的比例是 34\\%，违反的是 60\\%", 1880, 1914, 34, 60)  # Chapter 23


def gold(F, Y, Q):
    y1, s1, twice, y0, s0 = F["nu_us46"]
    said("1914 年，美国持有世界中央黄金储备的 23\\%。1924 年，这个比例是 46\\%，翻了一番", y0, s0, y1, s1)
    chk("    twice (翻了一番)", [twice, s1 / s0], [2, 2])
    y0, y1 = F["nu_neutralized"]
    said("1921—1924 年流进美国的黄金被冲销了", y0, 1900 + y1)
    said("美联储 1923 年的年报说", F["br_trust"][0])
    assert "Tenth Annual Report of the Federal Reserve Board" in Q["br_trust"]
    four, y0, y1 = F["nu_1925_28"]
    said("1925—1928 年，美国的黄金存量没有再增加", y0, 1900 + y1)
    chk("    the next four years", 1900 + y1 - y0 + 1, four)
    said("到了 1920 年代，三条都打了折扣", DECADE)
    pct("    the European reserves, four-tenths foreign exchange in 1928 (四成)", F["nu_12_42"][7] / 100,
        told("欧洲各国的储备四成是外汇", "储备", "是外汇"), 1)
    said("英国只卖 400 盎司的金块，欧洲各国的储备四成是外汇", F["act_bars"][0])
    # the case box
    fr, cents, d = F["br_243"]
    said("1926 年 7 月，法郎还在往下掉。7 月 21 日，一英镑要 243 法郎，一法郎只值 2.05 美分", Y["br_243"], 7, 7, d, fr, cents)
    assert "on July 21" in Q["br_243"]
    chk("    a cent is a hundredth of a dollar (百分之一)", 0.01, told("美分是美元的百分之一", "美元的"))
    said("战前一法郎值 20 美分左右", F["du_fifth"][0])
    said("6 月 26 日才上任", 6, F["br_moreau"][0])
    assert "On June 26" in Q["br_moreau"]
    d, y = F["br_poincare"]
    said("7 月 24 日，普恩加莱（Raymond Poincaré，1860—1934）出面组成全国联合政府", 7, d, *F["ws_poincare"])
    assert "July 24, 1926" in Q["br_poincare"]
    d, three = F["br_sergent"]
    said("方案在 7 月 3 日提出，分三步走", 7, d)
    chk("    three stages (三步)", three, told("分三步走", "分", "步走"))
    chk("    two methods (一是……二是)", F["br_caisse"], [told("二是设立偿债基金", "", "是设立")])
    chk("    the latter two (两位董事)", 2, told("法兰西银行有两位董事反对", "有", "位董事"))
    said("11 月在纽约值 3.5 美分，12 月约 4 美分", 11, F["br_vigorous"][0], 12, F["br_vigorous"][1])
    assert "By November it was 31/2 cents and by December approximately 4 cents" in Q["br_vigorous"]
    said("1926 年 12 月，法郎事实上稳定下来", F["br_france"][0], 12)
    c4, p122 = F["br_4cents"]
    said("每法郎不超过 4 美分；买进英镑，每英镑不少于 122 法郎", c4, p122)
    said("事实上的汇率是一英镑合 125 法郎", F["br_125"][0])
    said("1928 年 5 月的大选以后", int(re.search(r"elections of 1 May (\d{4})", column("note")["br_honor"]).group(1)), 5)
    said("法兰西银行有两位董事反对按 125 法郎立法稳定", F["br_125"][0])
    assert "The latter two were opposed" in Q["br_125"]
    d, y, mg, fine, _ = F["br_655"]
    said("1928 年 6 月 25 日的法律把一法郎定为 65.5 毫克成色十分之九的黄金", y, 6, d, mg)
    chk("    nine-tenths fine (十分之九)", fine, told("成色十分之九的黄金", "成色", "的黄金"))
    said("不得低于钞票与存款负债的 35\\%", F["br_35"][0])
    chk("    Dulles: the same 35 per cent", F["du_cover"], F["br_35"])
    pre, post = F["du_fifth"]
    said("新法郎值 3.93 美分，约为战前的五分之一", post)
    pct("    3.93 / 20 is about a fifth", post / pre, told("新法郎值 3.93 美分，约为战前的五分之一", "战前的"), 2)
    d, y, fx, fwd = F["br_26529"]
    said("到 1928 年 6 月 25 日，外汇已有 265 亿法郎，另有 98 亿法郎的远期合约", y, 6, d, fx * M8, fwd * M8)
    chk("    p. 448: 26.5 milliard on the same day", [F["br_bis265"][2] * B9, F["br_bis265"][0]], [fx * M8, d], tol=1e8)
    said("1928 年起，法国才开始大规模积累黄金", F["nu_1928fr"][0])
    said("1927 年 5 月，它开始在伦敦买黄金", F["br_parisinterview"][0], 5)
    assert "in May 1927" in Q["br_parisinterview"]
    said("1925 年丘吉尔说过，英国要靠约 1.5 亿英镑的黄金储备", Y["hc_150m"], F["hc_150m"][0])
    # the compare box
    par = mint_par()
    said("\\begin{compare}{按战前平价回去，还是贬值以后回去}{英国 1925 年}{法国 1926—1928 年}", hansard_day("hansard1925a")[0], F["br_france"][0],
         F["br_france"][1])
    said("\\cmprow{平价}{战前平价，每英镑 4.8665 美元}{约为战前金价值的五分之一，一英镑合 125 法郎}", par, F["br_125"][0])
    said("\\cmprow{汇率的位置}{高估，凯恩斯说约 10\\%}", F["k25_toohigh"][0])
    chk("    four-fifths not returned (五分之四)", 1 - F["du_onefifth"][1], told("五分之四的金价值没有回来", "", "的金价值"))
    # Nurkse's Table 2
    yrs, R = gold_reserves()
    assert yrs == [1913, 1918, 1923, 1928]
    said("按旧美元计，美国的中央黄金储备 1913 年底是 12.9 亿，1928 年底是 37.5 亿", yrs[0], R["us"][0] * M8, yrs[3],
         R["us"][3] * M8)
    said("法国从 6.8 亿增加到 12.5 亿", R["fr"][0] * M8, R["fr"][3] * M8)
    said("英国 1928 年底是 7.5 亿，与 1923 年底差不多", yrs[3], R["uk"][3] * M8, yrs[2])
    assert abs(R["uk"][3] / R["uk"][2] - 1) < 0.01                                        # 差不多
    said("旧美元按每盎司纯金 20.67 美元计", F["nu_t2head"][0])
    s8, y, _, _ = F["nu_france8"]
    said("到 1926 年底，法国持有世界黄金储备的 8\\%", y, s8)
    assert "at the end of 1926" in Q["nu_france8"]


def boom(F, Y, Q):
    said("1927 年 7 月，四位中央银行家在纽约开会", F["br_newyork"][0], 7)
    assert "July 1927" in Q["br_newyork"]
    names = ["Montagu Norman", "Hjalmar Schacht", "Charles Rist", "Benjamin Strong"]
    assert all(n in Q["br_newyork"] for n in names)
    chk("    four central bankers (四位)", len(names), told("四位中央银行家在纽约开会", "", "位中央"))
    chk("    the fourth (第四位) is Strong", names.index("Benjamin Strong") + 1, told("第四位是纽约联邦储备银行的斯特朗", "第", "位是"))
    d, r0, r1 = F["br_aug5"]
    said("8 月 5 日，纽约联储把贴现率从 4\\% 降到 3.5\\%", 8, d, r0, r1)
    assert "on August 5" in Q["br_aug5"]
    d1, d2, y, r0, r1 = F["br_1928up"]
    said("1928 年初，联储开始收紧。1 月 25 日到 2 月 3 日，各联储银行的贴现率普遍从 3.5\\% 提到 4\\%", y, 1, d1, 2, d2, r0, r1)
    d, r = F["br_may18"]
    said("5 月 18 日纽约提到 4.5\\%，7 月再提到 5\\%", 5, d, r, 7, F["br_july5"][0])
    d, bn = F["br_brokers"]
    said("到 1928 年 6 月 8 日，经纪人贷款的总额比一年前多了 10 亿美元", Y["br_brokers"], 6, d, bn * B9)
    said("“付价款的一部分，通常是 10\\%，其余借来”", F["frh_margin"][0])
    six, lo, y0, hi, y1 = F["frh_dow"]
    said("道琼斯工业平均指数从 1921 年 8 月的 63 点涨到 1929 年 9 月的 381 点，涨到原来的六倍", y0, 8, lo, y1, 9, hi)
    assert "in August 1921 to 381 in September 1929" in Q["frh_dow"]
    pct("    381 / 63 = six (六倍)", hi / lo, six, 0)
    chk("    six (六)", six, told("涨到原来的六倍", "原来的", "倍"))
    g, y0, y1 = F["dl_64"][:3]
    said("标准普尔综合指数从 1928 年 1 月到 1929 年 9 月涨了 64\\%", y0, 1, y1, 9, g)
    assert "from January 1928 to September 1929" in Q["dl_64"]
    # ex:interwar-margin
    m = F["frh_margin"][0] / 100
    pos, loan = EQUITY / m, EQUITY / m - EQUITY
    said("一个人有 1,000 美元，按 10\\% 的保证金买了 10,000 美元的股票，其余 9,000 美元向经纪人借入", EQUITY, 100 * m, pos,
         loan)
    _, y, crash, _, _ = F["frh_crash"]
    said("（1）股价涨 10\\%，他的自有资金变成多少，收益率是多少？（2）股价跌 10\\% 呢？（3）1929 年 10 月 28 日道琼斯指数跌了近 13\\%",
         1, 100 * m, 2, 100 * m, 3, y, 10, F["frh_crash"][0], crash)
    said("按 13\\% 的跌幅，他还欠多少？（4）若他只借 1,000 美元，买 2,000 美元的股票，跌 13\\% 时损失多少？", crash, 4, SMALL_LOAN,
         EQUITY + SMALL_LOAN, crash)
    up, down = pos * (1 + m), pos * (1 - m)
    said("（1）股票值 11,000，减去欠款 9,000，自有资金 2,000，收益率 100\\%", 1, up, loan, up - loan,
         100 * (up - loan - EQUITY) / EQUITY)
    said("（2）股票值 9,000，正好够还债，自有资金归零", 2, down)
    chk("    nothing left (归零)", down - loan, 0)
    c = pos * (1 - crash / 100)
    said("（3）股票值 8,700，欠 9,000，资不抵债 300，这 300 要由放款的经纪人承担", 3, c, loan, loan - c, loan - c)
    small = (EQUITY + SMALL_LOAN) * (1 - crash / 100)
    said("（4）股票值 1,740，还掉 1,000，剩 740，损失 26\\%，是跌幅的两倍", 4, small, SMALL_LOAN, small - SMALL_LOAN,
         100 * (1 - (small - SMALL_LOAN) / EQUITY))
    chk("    twice the fall (两倍)", (1 - (small - SMALL_LOAN) / EQUITY) / (crash / 100), told("是跌幅的两倍", "跌幅的", "倍"))
    # the Federal Reserve
    d, y = F["frh_feb2"]
    said("委员会 1929 年 2 月 2 日发出了有名的信", y, 2, d)
    assert "February 2, 1929" in Q["frh_feb2"]
    said("1929 年，纽约一再要求加息，委员会驳回了好几次", F["frh_denied"][0])
    said("8 月，委员会终于同意，纽约的贴现率提到 6\\%", 8, F["frh_six"][0])
    assert "In August the Board finally acquiesced" in Q["frh_six"] and Y["frh_six"] == 1929
    said("1928 年 10—12 月，大量黄金从伦敦流向德国", Y["br_flood"], 10, 12)
    assert "in October, November, and December" in Q["br_flood"]
    said("这股洪水从 1928 年 6 月开始", F["br_june1928"][0], 6)
    assert "began in June 1928" in Q["br_june1928"]
    lo, hi = F["br_lendny"]
    said("1929 年 4—6 月，纽约的定期与通知贷款利率在 8\\% 到 9\\% 之间", Y["br_lendny"], 4, 6, lo, hi)
    assert "In April, May, and June" in Q["br_lendny"]
    said("英格兰银行 1929 年 2 月把贴现率提到 5.5\\%，9 月 26 日又提到 6.5\\%", 1929, 2, rate_on("1929-02-28"), 9, 26,
         rate_on("1929-09-26"))
    assert rate_on("1929-01-31") < rate_on("1929-02-28") and rate_on("1929-09-25") < rate_on("1929-09-26")
    # bubble or fundamentals
    views = ["一种说是泡沫", "另一种说是基本面"]
    for v in views:
        say(v)
    for q, pre in (("繁荣靠的是什么，至今有两种看法", "至今有"), ("两种看法都不只看股价", "")):
        chk(f"    {q}", len(views), told(q, pre, "种看法"))
    p30, y = F["dl_30"]
    said("1929 年夏天，标准普尔综合指数的成分股“至少比基本面高出 30\\%”", y, p30)
    assert "in the summer of 1929" in Q["dl_30"]
    chk("    overvalued by one-half (一半)", F["dl_half"], [told("股市高估了一半", "高估了")])
    said("1929 年美国企业的基本价值至少是税后利润的 21 倍", Y["mp_21"], F["mp_21"][0])
    said("当年股票市值最高的估计，却只有税后利润峰值的 19 倍", F["mp_19"][0])
    assert F["mp_19"][1] == Y["mp_21"]                                                   # 当年
    said("照这个算法，1929 年秋天的股价并不高", Y["mp_21"])
    said("这一方也承认，只算有形资本，1929 年的股市高估了近 30\\%", Y["mp_tangible"], F["mp_tangible"][0])
    assert "close to 30 percent overvalued" in Q["mp_tangible"]
    said("前一种证据离 1929 年的投资者更近", Y["dl_30"])
    said("费雪（Irving Fisher，1867—1947）当时就站在第二种看法一边", None, None)                # life dates: book()
    d, y = F["mp_headline"]
    said("1929 年 10 月 22 日，《纽约时报》的一条标题是“费雪说股价低”", y, 10, d)
    assert "October 22, 1929" in Q["mp_headline"]
    d28, y, a, b, half = F["frh_crash"]
    chk("    six days later (六天以后)", d28 - d, told("六天以后的 10 月 28 日", "", "天以后"))
    said("六天以后的 10 月 28 日是黑色星期一，道琼斯指数跌了近 13\\%。第二天是黑色星期二，又跌了近 12\\%", 10, d28, a, b)
    chk("    almost half (近一半)", half, told("已经跌掉了近一半", "跌掉了近"))
    said("到 11 月中，道琼斯指数已经跌掉了近一半", 11)
    assert "By mid-November" in Q["frh_crash"]


def deeper(F, Y, Q):
    m, J = meta(), column("juan")
    said("1925 年 4 月 28 日下院的两个质询、丘吉尔的预算演说，以及 5 月 11 日上院的二读辩论", *hansard_day("hansard1925b"),
         *hansard_day("hansard1925e")[1:])
    assert "second reading" in m["sources"]["hansard1925e"]["version"]
    asked = [k for k in ("hansard1925a", "hansard1925b", "hansard1925c", "hansard1925d")
             if "private notice question" in m["sources"][k]["version"]]
    chk("    the two questions (两个质询)", len(asked), told("1925 年 4 月 28 日下院的两个质询", "下院的", "个质询"))
    chk("    the second reading (二读)", 2, told("以及 5 月 11 日上院的二读辩论", "上院的", "读辩论"))
    cmd = int(re.search(r"Cmd\. (\d+)", m["notes"]).group(1))
    said("张伯伦委员会 1925 年的报告（Cmd. 2393）没有取得，正文用的是克拉伦登在上院宣读的第 15 段", 1925, cmd,
         F["hl_para15"][0])
    said("坎利夫委员会 1918 年的报告也没有取得，它的建议与 1.53 亿英镑的储备", F["hl_cunliffe"][0], F["hc_153m"][0])
    nurkse = int(re.search(r"League of Nations, Economic, Financial and Transit Department, (\d{4})",
                           m["sources"]["nurkse1944"]["version"]).group(1))
    said("它对调整机制的描述据 Nurkse（1944）的概括", nurkse)
    q0, q1 = re.search(r"Q\. (\d+)-(\d+)", m["notes"]).groups()
    norman = ["br_norman_ruhr", "br_norman_worse", "br_norman_franc"]
    assert {J[r] for r in norman} == {"p. 615"}
    chk("    three sentences (三句话)", len(norman), told("三句话都转引自", "", "句话"))
    said("诺曼对麦克米伦委员会的答问（第 3353—3363 问）所在的那一卷没有取得，三句话都转引自 Brown（1940）第 615 页", int(q0),
         int(q0[:2] + q1), F["br_copyright"][0], page("br_norman_ruhr"))
    said("美联储 1923 年年报的话", F["br_trust"][0])
    d, y, p = F["frh_plateau"]
    said("《纽约时报》的标题转引自 McGrattan 与 Prescott（2003）；同一年费雪那句“永久的高原”，联邦储备历史网站注明见 1929 年 10 月 16 日的《纽约时报》第 8 版",
         F["mp_report"][1], y, 10, d, p)
    assert "October 16, 1929, p. 8" in Q["frh_plateau"] and y == F["mp_headline"][1]    # 同一年
    v31, v23 = m["sources"]["keynes1931"]["version"], m["sources"]["keynes1923"]["version"]
    pop = int(re.search(r"popular edition (\d{4})", v31).group(1))
    rep = int(re.search(r"reprint of (\d{4})", v23).group(1))
    said("凯恩斯 1925 年的文章据《劝说集》1933 年普及本，1923 年的书据 1929 年重印本", Y["k25_ten"], pop, Y["k23_relic"], rep)
    assert "Appendix IV, Table 2" in m["sources"]["nurkse1944"]["version"]
    yrs = gold_reserves()[0]
    said("附录四表 2 的数字对照过扫描页，英国 1913 年的 165 被识别成“i6s”，德国 1923 年的 111 被识别成“III”", 2, yrs[0],
         F["nu_t2uk"][0], None, yrs[2], F["nu_t2de"][2])                     # the 6 of 'i6s': check_text()
    appendix = re.search(r"Appendix ([IVX]+), Table", m["sources"]["nurkse1944"]["version"]).group(1)
    chk("    Appendix IV (附录四)", {"IV": 4}[appendix], told("附录四表 2", "附录", "表"))
    chk("    two pound signs read ',^' (两个)", Q["k25_rentiers"].count(",^"), told("凯恩斯文中的两个英镑符号", "文中的", "个英镑"))
    _, s, dd = F["br_mintpar"]
    said("英格兰银行的黄金输出点按每盎司 84 先令 11.4545 便士计", s, dd)
    lsd = F["act_price"]
    standard = lsd[0] * SHILLINGS * PENCE + lsd[1] * PENCE + lsd[2]
    chk("    12/11 times the price of standard gold", (s * PENCE + dd) / standard, 12 / 11, tol=1e-6)
    said("它正好是标准金价格的 12/11 倍，与标准金含金十二分之十一相合", 12, 11)
    M = monthly()
    m28 = M.usd_per_gbp.loc["1928-01":"1928-12"].mean()
    _, _, _, avg, table = F["br_par"]
    said("按英格兰银行工作簿的月平均，1928 年的汇价是 4.8662 美元，略低于平价，Brown 的年平均是 4.8666 美元", 1928, m28, avg)
    assert m28 < mint_par() < avg and abs(avg - m28) / mint_par() < 1e-4                  # 相差不到万分之一
    assert "(Table 49)" in Q["br_par"] and table == 49
    _, mm = _boe("boe_millennium_interwar_monthly")
    ver = float(re.search(r"\(version (\d\.\d)\)", mm["source"]).group(1))
    said("月度的汇率、物价、工资与失业都据英格兰银行《千年宏观数据》3.1 版", ver)
    w = re.search(r"Index of (\d+) Weekly Wage Rates (\d{4})-(\d{4})", mm["series"]).groups()
    said("工资指数 1919—1925 年是 11 种周工资率", int(w[1]), int(w[2]), int(w[0]))
    wages = re.search(r"wages_jan1939_100: '([^']+)'", mm["series"]).group(1).split("; ")
    chk("    two segments (两段): " + " | ".join(wages), len(wages), told("两段在工作簿里接好", "", "段在"))
    papers = {"bubble": "delong1990", "fundamentals": "mcgrattan2003"}
    assert all(k in m["sources"] for k in papers.values())
    chk("    two estimates (两种估算), one paper each", len(papers), told("泡沫与基本面两种估算各只有一篇论文", "基本面", "种估算"))
    said("布拉德伯里引的统计权威没有名字，4.75 美元只此一处", F["hl_475"][0])
    assert "the authority is not named" in column("note")["hl_475"]
    said("法兰西银行董事的反对与莫罗以辞职相争、1927 年纽约会议的商定、1928 年 6 月 8 日的经纪人贷款", F["br_newyork"][0],
         Y["br_brokers"], 6, F["br_brokers"][0])


def models() -> None:
    """The key equations as the text writes them, and their arithmetic checked with numbers."""
    say("\\frac{q_1}{q_0}=\\frac{e_1}{e_0}\\cdot\\frac{P^{f}_1/P^{f}_0}{P_1/P_0},\\qquad\n"
        "\\bar P_1=P_0\\,\\frac{P^{f}_1}{P^{f}_0}\\quad (e_1=e_0).\\label{eq:interwar-parity}",
        "实际汇率$q=eP^{f}/P$是美国货与英国货的比价",
        "R=G+F,\\qquad M\\le\\frac{R}{c}.\\label{eq:interwar-pyramid}",
        "H=A+R,\\qquad \\Delta H=\\Delta A+\\Delta R;\\qquad \\text{冲销：}\\ \\Delta A=-\\Delta R,\\ \\Delta H=0."
        "\\label{eq:interwar-sterilize}")
    for e0, e1, p0, p1, f0, f1 in [(1 / 4.8665, 1 / 4.8665, 1.0, 1.71, 1.0, 1.62), (0.2, 0.25, 100, 180, 100, 150)]:
        q0, q1 = e0 * f0 / p0, e1 * f1 / p1
        chk(f"    eq:interwar-parity: q1/q0 = (e1/e0)(Pf1/Pf0)/(P1/P0) ({e1 / e0:.3g}, {p1 / p0:.3g}, {f1 / f0:.3g})",
            q1 / q0, (e1 / e0) * (f1 / f0) / (p1 / p0), tol=1e-12)
        pbar = p0 * f1 / f0
        chk("        at P1 = Pbar and e1 = e0 the real rate is the pre-war one", e0 * f1 / pbar, q0, tol=1e-12)
        rate = 4.8665 * (f1 / f0) / (p1 / p0)                                         # dollars per pound
        chk("        the PPP rate keeps q0 (e = 1 / dollars per pound)", (1 / rate) * f1 / p1, (1 / 4.8665) * f0 / p0,
            tol=1e-12)
    for G, Fx, c in [(150, 0, Fraction(1, 3)), (40, 60, Fraction(1, 3)), (20, 80, Fraction(1, 4))]:
        R = G + Fx
        chk(f"    eq:interwar-pyramid: M <= R / c ({G}, {Fx}, {c})", R / c, R * c.denominator / c.numerator)
    for dA, dR in [(-50, 50), (30, 30), (0, -20)]:
        chk(f"    eq:interwar-sterilize: Delta H = Delta A + Delta R ({dA}, {dR})", dA + dR, dA + dR)
    chk("    sterilized: Delta A = -Delta R gives Delta H = 0", -SC5["dR"] + SC5["dR"], 0)


def frames(F, Y):
    """The captions of the figures."""
    M, (_, mm) = monthly(), _boe("boe_millennium_interwar_monthly")
    _, ma = _boe("boe_millennium_prices_1913_1931")
    nums = [int(n) for n in re.findall(r"'M(\d+)\. ", mm["source"])]
    a47 = int(re.search(r"'A(\d+)\. Wages and prices'", ma["source"]).group(1))
    m15, m6, m5 = nums
    y0, m0 = map(int, M.index[0].split("-"))
    y1, m1 = map(int, M.index[-1].split("-"))
    par = mint_par()
    said("(a) 每月的美元—英镑汇价，1914 年 7 月至 1931 年 12 月，细点线是 4.8665 美元的铸币平价；圆点是按英美消费物价算出的购买力平价，每年一点，以 1913 年为基期",
         y0, m0, y1, m1, par, annual().index[0])
    said("(b) 三种英国价格，都以 1924 年 1 月$=100$：索尔贝克批发物价指数、生活费用指数与周工资指数，竖线标出 1925 年 4 月", 1924, 1,
         100, 1925, 4)
    said("数据：英格兰银行《千年宏观数据》表 M15、M6 与 A47", m15, m6, a47)
    gaps = [k for k in M.index if "1919-01" <= k <= "1931-12" and pd.isna(M.unemp_admin[k])]
    assert gaps == [f"1919-{i:02d}" for i in range(1, 11)] + ["1920-10"], gaps
    said("(a) 英国每月的行政失业率，1919—1931 年，1919 年 1—10 月与 1920 年 10 月缺数，竖线标出 1925 年 4 月与 1926 年 5 月", 1919,
         1931, 1919, 1, 10, 1920, 10, 1925, 4, 1926, 5)
    dm = int(re.search(r"Denman and Macdonald (\d{4})", mm["license"]).group(1))
    d1 = int(re.search(r"'D(\d+)\. Official Interest Rates'", _boe("boe_millennium_bank_rate_1919_1931")[1]["source"])
             .group(1))
    said("数据：英格兰银行《千年宏观数据》表 M5（Denman 与 Macdonald 1996）与 D1", m5, dm, d1)
    yrs, _ = gold_reserves()
    fy, _, banks = fx_shares()
    nurkse = int(re.search(r", (\d{4}); Series", meta()["sources"]["nurkse1944"]["version"]).group(1))
    said("(a) 美国、法国、英国与德国的中央黄金储备，1913、1918、1923 与 1928 年底，单位是百万旧美元（每盎司纯金 20.67 美元）", *yrs,
         F["nu_t2head"][0])
    said("(b) 欧洲中央银行的储备里外汇所占的比例，1913 年是 15 家银行，1925 与 1928 年是 24 家", fy[0], banks[0], fy[1], fy[2],
         banks[1])
    said("数据：Nurkse（1944）第 29 页与附录四表 2；表 2 的数字核对过扫描页", nurkse, page("nu_12_42"), 2, 2)


def legacy(F, Y):
    said("1925 年的英国让工资与就业去迁就平价，1928 年的法国让平价去迁就物价", hansard_day("hansard1925a")[0],
         F["br_655"][1])
    said("1925 年布拉德伯里的回答是自由的黄金市场，1930 年金德斯利的回答是各国一起守的规则", Y["hl_automatic"],
         F["mc_kinderdate"][1])
    said("这个不对称怎样在 1931 年压垮体系", 1931)                                     # Chapter 29's year


def takeaways(F, Y):
    par = mint_par()
    said("1925 年 4 月 28 日，英国按战前平价回到黄金，一英镑合 4.86 美元。这是金块本位，英格兰银行只卖 400 盎司左右的金块",
         *hansard_day("hansard1925a"), math.floor(par * 100) / 100, F["act_bars"][0])
    uk, us = F["hc_wpi71"][2], F["hc_wpi62"][2]
    A = annual()
    over_c = (A.uk_cpi_2015_100[1925] / A.uk_cpi_2015_100[1913]) / (A.us_cpi_1982_84_100[1925] /
                                                                     A.us_cpi_1982_84_100[1913]) - 1
    said("批发物价约 5.6\\%，消费物价约 6.6\\%，凯恩斯按生活费用与工资算是 10\\% 到 12\\%",
         100 * ((1 + uk / 100) / (1 + us / 100) - 1), 100 * over_c, *F["k25_gap"][2:])
    chk("    France at a fifth (五分之一) of the pre-war gold value", F["du_onefifth"][1],
        told("法国按战前五分之一的金价值稳定法郎", "按战前", "的金价值"))
    U = monthly().unemp_admin.loc["1925-05":"1930-04"]
    said("失业率五年里没有低于 8\\%。1925 年的煤炭危机与 1926 年的总罢工", math.floor(U.min()), F["fbi_coal"][0],
         F["mc_general"][0])
    said("1927 年纽约放松银根，股价与经纪人贷款随之上升，1928—1929 年又收紧", F["br_newyork"][0], F["br_1928up"][2],
         F["frh_denied"][0])
    d, y, a, b, _ = F["frh_crash"]
    two = 1 - (1 - a / 100) * (1 - b / 100)
    v = told("两天跌了近四分之一", "跌了近")
    assert v - 0.05 < two < v                                                          # 近四分之一: a little less
    said("1929 年 10 月 28 日与 29 日，道琼斯指数两天跌了近四分之一", y, 10, d, d + 1)


def selfcheck(F, Y):
    lsd, usd = F["act_price"], F["nu_t2head"][0]
    said("英国的金价是每盎司标准金 3 英镑 17 先令 10½ 便士，标准金含纯金十二分之十一，美国的金价是每盎司纯金 20.67 美元", *lsd, usd)
    said("设战前以来，英国物价涨了 80\\%，美国涨了 50\\%，汇率不变", SC2["uk"], SC2["us"])
    c = SC4["c"]
    said("外围国有黄金 20、外汇 80，准备比率为 1/4", SC4["G"], SC4["F"], c.numerator, c.denominator)
    said("一国中央银行的国际储备增加 50，同时卖出 50 的政府证券", SC5["dR"], SC5["sold"])
    said("法国 1928 年为什么不按战前平价回去", F["br_655"][1])
    said("保证金是 25\\% 时，股价跌多少", SC7)
    # answers
    standard = lsd[0] * SHILLINGS * PENCE + lsd[1] * PENCE + lsd[2]
    fine = standard * 12 / 11
    p = SHILLINGS * PENCE
    said("每盎司纯金合$934.5\\times12/11=1019.45$便士，一英镑 240 便士可买$240/1019.45$盎司纯金", standard, 12, 11, fine, p, p,
         fine)
    said("值$20.67\\times240/1019.45\\approx4.87$美元，即通常说的 4.86 美元平价", usd, p, fine, usd * p / fine,
         math.floor(mint_par() * 100) / 100)
    uk, us = 1 + SC2["uk"] / 100, 1 + SC2["us"] / 100
    said("$q_1/q_0=1.5/1.8\\approx0.83$，实际汇率下降约 17\\%，英国货相对贵了", us, uk, us / uk, 100 * (1 - us / uk))
    said("要回到战前，英国物价要降到$1.5$，即降$1-1.5/1.8\\approx16.7\\%$", us, 1, us, uk, 100 * (1 - us / uk))
    say("凯恩斯说，批发物价至少三分之二是国际原料")
    R = SC4["G"] + SC4["F"]
    said("储备仍是 100，货币上限不变，仍是 400。中心国少了 80 的黄金，世界的储备少了 80，正是消失的外汇", R, R / c, SC4["F"],
         SC4["F"])
    dA = -SC5["sold"]
    said("$\\Delta H=-50+50=0$，基础货币不变", -dA, SC5["dR"], dA + SC5["dR"])
    say("国内资产与储备反向变动，这是冲销，违反了游戏规则")
    said("1927 年法兰西银行在伦敦买黄金", F["br_parisinterview"][0])
    said("跌 25\\%。股票的价值降到借款的数额", SC7)
    chk("    at a margin m, a fall of m leaves the position equal to the loan", 100 * (1 - SC7 / 100), 100 - SC7)


def ending(F, Y, Q):
    y, mo, d = hansard_day("hansard1925a")
    said("1925 年 4 月 28 日下午，丘吉尔说“现在正是时候”，英镑回到了战前的平价", y, mo, d)
    d2, y2, a, b, _ = F["frh_crash"]
    months = (y2 - y) * 12 + (10 - mo)
    chk("    four and a half years (四年半), 28 April 1925 to 28 October 1929", [months / 12, d2], [told("四年半以后", "", "年半") + 0.5, d])
    said("四年半以后，1929 年 10 月 28 日，纽约的道琼斯指数一天跌了近 13\\%，第二天又跌了近 12\\%", y2, 10, d2, a, b)
    say("英镑守住了平价，代价是五年没有降下来的失业")
    q28 = re.search(r"\\guidequestion\{([^}]*)\}", (ROOT / "zh" / "ch28_depressionus.tex").read_text(encoding="utf-8"))
    assert q28, "Chapter 28 has no guide question"
    t = tex_text().rstrip()
    assert t.endswith(q28.group(1)), "the last words are not Chapter 28's question"
    assert not re.search(r"\d", q28.group(1))
    say(q28.group(1))


# the life dates the chapter gives without a row of its own: the same words in an earlier chapter
LIVES = {"John Maynard Keynes，1883—1946": "ch20_say", "Hjalmar Schacht，1877—1970": "ch26_weimar",
         "Irving Fisher，1867—1947": "ch25_wicksell", "Robert Kindersley，生卒年未详": "ch23_goldstandard"}
# the life dates from rows of the snapshot: words -> (row, index of the birth year, index of the death year)
ROW_LIVES = {"Frederick Pethick-Lawrence，1871—1961": ("hh_pethick", 0, 1),
             "Winston Churchill，1874—1965": ("hh_churchill", 0, 1),
             "Philip Snowden，1864—1937": ("hh_snowden", 0, 1),
             "Austen Chamberlain，1863—1937": ("hh_chamberlain", 0, 1),
             "George Villiers，1877—1955": ("hh_clarendon", 0, 1),
             "John Bradbury，1872—1950": ("hh_bradbury", 0, 1),
             "Herbert Gibbs，1854—1935": ("hh_hunsdon", 0, 1),
             "Montagu Norman，1871—1950": ("hh_norman", 0, 1),
             "Raymond Poincaré，1860—1934": ("ws_poincare", 0, 1)}
# people whose dates were not found (the 史料说明 says so)
UNKNOWN = ["Émile Moreau，生卒年未详", "Charles Rist，生卒年未详", "Benjamin Strong，生卒年未详", "George Harrison，生卒年未详"]
# what other chapters tell: (words of this chapter, chapter where it is told, words there)
EVENTS = [("购买力平价是让两国物价折成同一种货币以后相等的汇率（\\chref{ch:external}）", "ch05_external",
           "\\subsubsection{购买力平价}"),
          ("实际汇率$q=eP^{f}/P$是美国货与英国货的比价", "ch05_external", "q=\\frac{e\\,P^{f}}{P},\\label{eq:external-real}"),
          ("贴现率是英格兰银行贴现票据、借钱给市场的利率（\\chref{ch:goldstandard}）", "ch23_goldstandard",
           "英格兰银行用\\textbf{贴现率}（Bank Rate）调节借款的价格"),
          ("一英镑合二十先令，一先令合十二便士（\\chref{ch:goldstandard}）", "ch23_goldstandard",
           "3 英镑 17 先令 9 便士"),
          ("索尔贝克指数（\\chref{ch:wicksell}）", "ch25_wicksell", "索尔贝克表上那个规律"),
          ("克朗是瑞典的货币单位（\\chref{ch:bullion}）", "ch19_bullion", "瑞典克朗"),
          ("\\chref{ch:bullion}说，休谟的机制要求物价有弹性、金银自由流动、中央银行不把流入的黄金锁起来", "ch19_bullion",
           "它要求物价有弹性、金银自由流动、中央银行不把流入的黄金锁起来"),
          ("\\chref{ch:bullion}讲过，按哪个平价回去，决定了由谁承担战时的通胀与战后的通缩", "ch19_bullion",
           "按哪个平价回去，决定了由谁承担战时的通胀与战后的通缩"),
          ("\\chref{ch:goldstandard}讲过，游戏规则是战后才有的说法", "ch23_goldstandard",
           "第一次世界大战以前的国际调整分析里没有这个说法，它是战后才有的"),
          ("遵守的比例是 34\\%，违反的是 60\\%（\\chref{ch:goldstandard}）", "ch23_goldstandard",
           "Bloomfield 用 1880—1914 年的年度数据检验，各国央行遵守的比例是 34\\%，违反的是 60\\%"),
          ("\\chref{ch:goldstandard}问过，发行的限额有了弹性以后，纪律靠什么", "ch23_goldstandard", "弹性有了，纪律靠什么"),
          ("这里的$R$是中央银行对外的储备，不是\\chref{ch:money}里商业银行的准备金", "ch04_money",
           "公众手中的通货与银行的准备金，合起来叫\\textbf{基础货币}"),
          ("\\chref{ch:money}从负债一边写基础货币$H$", "ch04_money", "合起来叫\\textbf{基础货币}"),
          ("帝国马克是德国 1924 年定下的新货币单位（\\chref{ch:weimar}）", "ch26_weimar",
           "一帝国马克合一万亿纸马克，含金量与战前的旧马克相同"),
          ("\\chref{ch:weimar}说它实际上是美元汇兑本位", "ch26_weimar", "实际上是美元汇兑本位"),
          ("鲁尔区在 1923 年被法国与比利时占领（\\chref{ch:weimar}）", "ch26_weimar",
           "1923 年 1 月 11 日，法国与比利时又派军队开进鲁尔区"),
          ("\\chref{ch:weimar}讲过，凯恩斯认为德国这几年的赔款其实是借来的", "ch26_weimar",
           "凯恩斯认为，德国这几年的赔款其实是借来的")]


def book(F, Q):
    """Life dates and what other chapters tell."""
    t = tex_text()
    for words, ch in LIVES.items():
        assert words in t, words
        assert words in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (words, ch)
        COVERED.append(words)
    for words, (rid, i, j) in ROW_LIVES.items():
        assert words in t, words
        assert f"{F[rid][i]:.0f}—{F[rid][j]:.0f}" in words, (words, rid)
        COVERED.append(words)
    for words in UNKNOWN:
        assert words in t, words
    for here, ch, there in EVENTS:
        assert here in t, here
        assert there in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (ch, there)
    assert "Earl of Clarendon" in Q["hh_clarendon"] and "Baron Hunsdon" in Q["hh_hunsdon"]
    print(f"ok {len(LIVES) + len(ROW_LIVES)} life dates, {len(UNKNOWN)} unknown, {len(EVENTS)} statements of other "
          "chapters")


def witnesses(F, Q):
    """Second witnesses of statements of the text, and the bibliography block of the chapter."""
    N = column("note")
    chk("the gold reserve: Churchill (Commons) = Clarendon (Lords)", F["hc_153m"], F["hl_153"])
    chk("the price of gold: the Act = Churchill", F["act_price"], F["hc_400oz"][1:])
    chk("the French cover: Brown = Dulles", F["br_35"], F["du_cover"])
    chk("the Reichsmark peg: Brown pp. 469 and 486", F["br_420"][1:], F["br_420end"])
    chk("the franc's foreign exchange: Brown p. 458 (26,529 million) > Nurkse's 'over 26,000 million'",
        F["br_26529"][2] > F["nu_bdf26000"][0], 1)
    chk("the franc at about a fifth: Dulles p. 297 (one-fifth) and p. 437 (3.93 of 20 cents)",
        F["du_fifth"][1] / F["du_fifth"][0], F["du_onefifth"][1], tol=0.01)
    chk("the mint par: Brown 4.8665 = 240 / (84s. 11.4545d.) x 20.67", 240 / (84 * 12 + 11.4545) * 20.67,
        F["br_mintpar"][0], tol=5e-4)
    assert "Kindersley" in N["mc_kinderdate"] and "Federation of British Industries" in N["fbi_wpi"]
    assert "rise and fall together" in Q["hc_ships"] and "rise and fall together" in Q["hl_ships"]   # Bradbury, too
    # the licences and the bibliography
    m = meta()
    for words in ("Open Parliament Licence v3.0", "Open Government Licence v3.0", "public domain in the United Kingdom",
                  "Copyright, 1940, by National Bureau of Economic Research, Inc. ... All Rights Reserved",
                  "'All rights reserved'", "Enter source, Sveriges riksbank and date.", "CC BY-SA",
                  "out of Crown copyright"):
        assert words in m["license"], words
    assert Q["br_copyright"].startswith("Copyright, 1940, by National Bureau of Economic Research")
    assert Q["du_copyright"].startswith("CoryricHt, 1929")
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    start = bib.index("% ---- 第 27 章")
    following = re.search(r"^% ---- 第 \d+ 章", bib[start + 1:], re.MULTILINE)
    end = start + 1 + following.start() if following else bib.index("\\end{thebibliography}")
    block = bib[start:end]
    items = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", block)}
    for key in ("hansard1925", "hansardlords1925"):
        assert "© UK Parliament，按 Open Parliament Licence 转载。" in items[key], key
    assert "© UK Parliament。" in items["hansardpeople27"] and "坎利夫的人物页只有卒年" in items["hansardpeople27"]
    assert "Crown copyright，Open Government Licence v3.0" in items["gsa1925"]
    assert "Copyright, 1940, by National Bureau of Economic Research, Inc. All Rights Reserved（只引短句）" in items["brown1940"]
    assert "王室版权已过期" in items["macmillan1931"] and "All rights reserved（只引短句）" in items["dulles1929"]
    assert "来源：Sveriges riksbank，2026 年 10 月 22 日" in items["riksbank2026c"]
    assert "CC BY-SA" in items["poincarelife2026"]
    wp, yr = F["dl_wp"]
    assert f"NBER Working Paper {wp:.0f}, November {yr:.0f}" in items["delong1990"]
    rep, yr = F["mp_report"]
    assert f"Staff Report {rep:.0f}, revised December {yr:.0f}" in items["mcgrattan2003"]
    for key in ("nurkse1944", "frh2013", "delong1990", "mcgrattan2003"):
        assert "只引短句" in items[key], key
    k25 = bib[bib.index("\\bibitem{keynes1925}"):].split("\n")[0]
    k23 = bib[bib.index("\\bibitem{keynes1923}"):].split("\n")[0]
    boe = bib[bib.index("\\bibitem{boe2017}"):].split("\n")[0]
    assert "第 27 章用第 244—261 页" in k25 and "公有领域" in k25
    assert "第 27 章另用第 40、142—143、155、172 页" in k23 and "1929 年重印本" in k23
    assert "第 27 章用表 M15" in boe and "boe\\_millennium\\_gb27.py" in boe
    keys = set(re.findall(r"\\bibitem\{([^}]+)\}", bib))
    cited = {k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", tex_text()) for k in c.split(",")}
    assert cited <= keys, sorted(cited - keys)
    assert set(items) <= cited, sorted(set(items) - cited)
    print(f"ok {len(cited)} works cited, {len(items)} of them in the bibliography block of Chapter 27")


def counts() -> None:
    """The editor's limits: “不能” at most about a dozen; no source as the subject of a sentence outside the 史料说明."""
    t = tex_text()
    main = re.sub(r"\\begin\{deeper\}.*?\\end\{deeper\}", "", t, flags=re.DOTALL)
    n = t.count("不能")
    print(f"ok “不能” {n} times")
    assert n <= 12, n
    verbs = "认为|写道|说|指出|记述|估计|承认|报道|记载|提到|列出|给出|发现|统计|算出"
    names = "Brown|Nurkse|Dulles|De Long|Shleifer|McGrattan|Prescott|Bloomfield|Moggridge|联邦储备历史网站|米德兰银行"
    subj = re.findall(r"(?:^|[。；：，\n])\s*(?:" + names + r")(?:（\d{4}）)?(?:" + verbs + ")", main)
    assert not subj, subj
    assert "这一节回答" not in t and "不能据此断言" not in t


def main() -> None:
    df = _rows()
    F, Y, Q = facts(), years(), quotes()
    check_readings(df)
    check_text(df)
    guide(F, Y, Q)
    opening(F, Y, Q)
    world(F, Y, Q)
    parity(F, Y, Q)
    keynes(F, Y, Q)
    cost(F, Y, Q)
    exchange(F, Y, Q)
    gold(F, Y, Q)
    boom(F, Y, Q)
    deeper(F, Y, Q)
    models()
    frames(F, Y)
    legacy(F, Y)
    takeaways(F, Y)
    selfcheck(F, Y)
    ending(F, Y, Q)
    book(F, Q)
    witnesses(F, Q)
    counts()
    coverage()
    anchors("zh/ch27_interwar.tex", df["id"], script=Path(__file__))


if __name__ == "__main__":
    main()
