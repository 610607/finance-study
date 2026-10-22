"""Chapter 29 (大萧条：世界与“金色枷锁”): every number and every quotation in zh/ch29_depressionworld.tex.

    python3 checks/check_ch29.py

Inputs:
  depressionworld_facts      quotations of Hansard of 21 September 1931 (Commons and Lords), the Gold Standard
                             (Amendment) Act 1931, Keynes's 'The End of the Gold Standard' (27 September 1931),
                             Hoover's statement of the moratorium (the American Presidency Project), the Federal
                             Reserve Bulletin (July-October 1931, December 1935, October 1936), the Silver Purchase
                             Act (48 Stat. 1178), Foreign Relations of the United States 1934 and 1935, Bernanke and
                             James (1991), Bernanke (1994/1995), Eichengreen and Sachs (1984), Brandt and Sargent
                             (1989), the abstract of Friedman (1992), Díaz Alejandro (1983), the BCRA, Wolf (2007)
                             and the authority records of the Library of Congress, the BnF and Historic Hansard
                             (checked by data/fetch/verify_web_quotes.py); the rows with an empty quotation are
                             values read on page images (Bernanke and James's Table 2.2, Eichengreen and Sachs's
                             adjusted R-squared, Díaz Alejandro's Tables 1.1 and 1.2)
  depressionworld_goldexits  Bernanke and James (1991), Table 2.1 (the dates of returning to and leaving gold) and
                             Tables 2.2 and 2.4 (log changes of wholesale prices and industrial production)
  depressionworld_es         the ten points of Eichengreen and Sachs's Figure 1, read on the page image
  depressionworld_silver     the New York price of silver (Historical Statistics M 270) and the yuan's annual
                             average in cents (Banking and Monetary Statistics, Table 173)
  depressionworld_yuan_monthly  the yuan in cents, monthly, 1929-1936 (the same table)
  depressionworld_china      Brandt and Sargent (1989), Tables 1, 2, 4 and 5
  maddison2023_interwar      GDP per head of 28 economies, 1929-1938 (Maddison Project Database 2023)
  boe_millennium_gb_1929_1936_monthly, boe_millennium_bank_rate_1929_1936
                             the dollar-sterling rate, the Sauerbeck index, the cost of living and Bank Rate
The figure module figsrc/fig_ch29.py imports its data from here.

What is checked here:
  1. readings   every number of the value column of depressionworld_facts is read from its quotation (digits,
                English number words, ordinals, fractions, and the OCR's misprints, each named in the note)
  2. the text   every “…” of the chapter is the chapter's Chinese rendering of a quotation (TRANSLATIONS), with
                the source's words listed in KEYWORDS
  3. numbers    every number of the text, section by section: said() finds the phrase and compares each number
                it prints (with its unit 万, 亿) with the value computed from the snapshots or with a teaching
                input stated in the text, within half a unit of the last printed digit; Chinese numerals are read
                by zh() and compared the same way
  4. coverage   every Arabic number of the text (outside labels, citations, cross-references, the key equations
                and math subscripts) lies inside a phrase checked by said()
  5. the book   identities of the table snapshots, second witnesses, life dates, what other chapters tell, the
                bibliography block of the chapter and its licence notices
  6. anchors    the paraphrase anchors `% 据: ...` name rows of depressionworld_facts

Models (the chapter's key equations):
    the fetters (eq:depressionworld-fetters): pi = dln e + pi^f (relative PPP for traded goods, Chapter 5) and
        M <= (G + F)/c (the inverted pyramid, Chapter 27): a loss of reserves dR cuts the ceiling by dR/c
    the cross-section (eq:depressionworld-es): IP_i = a + b ER_i + u_i, fitted by least squares on the ten points
    silver (eq:depressionworld-silver): s = 0.7553 p_s (the yuan's silver in dollars), e = 1/s, and
        pi = pi^f - dln p_s
"""
from __future__ import annotations

import math
import re
from datetime import date
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd
from common import ROOT, anchors, load_snapshot, quoted
from statsmodels.regression.linear_model import OLS

TEX = ROOT / "zh" / "ch29_depressionworld.tex"
GUIDE = "金本位怎样把萧条传到全世界？银本位的中国为什么被美国的白银政策拖累？"
PREV = "金本位怎样把萧条传到全世界？"          # Chapter 28's NEXT
NEXT = "纳粹德国、高桥财政下的日本和瑞典都较早走出了萧条，各自靠的是什么？代价记在了哪里？"   # Chapter 30's question
# Teaching inputs stated in the text
FET = {"c": 0.4, "R": 100, "fall": 10, "out": 10, "rise": 25}     # ex:depressionworld-fetters
SC1 = {"fall": 5, "rise": 10}                                    # self-check 1
SC2 = {"c": 25, "loss": 8}                                       # self-check 2
M6, B9 = 10 ** 6, 10 ** 9
B95 = 1995                       # Bernanke (1995): the year of the journal version (checked in witnesses())


def chk(what: str, value, expected=None, tol: float = 1e-9, rel: float = 0.0) -> float:
    """quoted() with a tolerance for floating-point error on exact values; a list is compared element by element."""
    if isinstance(value, (list, tuple, np.ndarray, pd.Series)):
        value = list(value)
        assert expected is not None and len(value) == len(expected), (what, value, expected)
        for i, (v, e) in enumerate(zip(value, expected)):
            quoted(f"{what} [{i + 1}]", float(v), e, tol=tol, rel=rel)
        return float(value[0])
    return quoted(what, float(value), expected, tol=tol, rel=rel)


# ---------------------------------------------------------------------------------------------------
# Loaders
def _rows() -> pd.DataFrame:
    df, m = load_snapshot("depressionworld_facts", dtype=str, keep_default_na=False)
    assert 29 in m["used_in"]
    assert df["id"].is_unique
    return df


def meta() -> dict:
    return load_snapshot("depressionworld_facts")[1]


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


def _table(name: str) -> tuple[pd.DataFrame, dict]:
    df, m = load_snapshot(name)
    assert 29 in m["used_in"], name
    assert "sources" not in m, name                                # table snapshots carry no 'sources' key
    return df, m


def goldexits() -> pd.DataFrame:
    """Bernanke and James's 24 countries (Table 2.1 dates, Tables 2.2 and 2.4 log changes), indexed by country; the
    four rows of averages are in averages()."""
    df, _ = _table("depressionworld_goldexits")
    df = df[df.group.notna()].copy()
    df["group"] = df.group.astype(int)
    assert len(df) == 24 and df.country.is_unique
    return df.set_index("country")


def averages() -> pd.DataFrame:
    df, _ = _table("depressionworld_goldexits")
    return df[df.group.isna()].set_index("country")


def es() -> pd.DataFrame:
    """The ten points of Eichengreen and Sachs's Figure 1: er1935 (gold value of the currency, 1929 parity = 100)
    and ip1935 (industrial production, 1929 = 100)."""
    df, _ = _table("depressionworld_es")
    assert len(df) == 10
    return df.set_index("country")


def silver() -> pd.DataFrame:
    """The New York price of silver, cents per fine ounce (1926-1937), and the yuan's annual average in cents
    (1929-1936), indexed by year."""
    df, _ = _table("depressionworld_silver")
    return df.set_index("year")


def yuan_monthly() -> pd.Series:
    """The yuan in US cents, monthly averages of daily rates, indexed by (year, month)."""
    df, _ = _table("depressionworld_yuan_monthly")
    assert len(df) == 96
    return df.set_index(["year", "month"]).cents_per_yuan


def china() -> pd.DataFrame:
    df, _ = _table("depressionworld_china")
    return df.set_index("year")


def maddison_meta() -> dict:
    return _table("maddison2023_interwar")[1]


def maddison() -> pd.DataFrame:
    """GDP per head (2011 international dollars), economies by ISO code x years 1929-1938."""
    df, _ = _table("maddison2023_interwar")
    return df.pivot(index="country", columns="year", values="gdppc_2011usd")


def ratio1935() -> pd.Series:
    """GDP per head in 1935, per cent of 1929."""
    M = maddison()
    return 100 * M[1935] / M[1929]


def boe_meta() -> dict:
    return _table("boe_millennium_gb_1929_1936_monthly")[1]


def boe() -> pd.DataFrame:
    """Britain, monthly 1929-1936: dollars per pound, the Sauerbeck index and the cost of living, by (year, month)."""
    df, _ = _table("boe_millennium_gb_1929_1936_monthly")
    assert len(df) == 96
    return df.set_index(["year", "month"])


def bank_rate() -> pd.Series:
    """Bank Rate on 1 January 1929 and on each day it changed, 1929-1936 (the new rate from that day)."""
    df, _ = _table("boe_millennium_bank_rate_1929_1936")
    s = df.set_index("date").bank_rate
    s.index = [date.fromisoformat(d) for d in s.index]
    return s


def rate_on(d: date) -> float:
    s = bank_rate()
    return float(s[[k for k in s.index if k <= d][-1]])


def ym(s: str) -> tuple[int, int]:
    """'1931-09' -> (1931, 9); of a two-step date '1927-03/1929-02' the first."""
    y, m = s.split("/")[0].split("-")
    return int(y), int(m)


ISO = {"Australia": "AUS", "New Zealand": "NZL", "Austria": "AUT", "Canada": "CAN", "Denmark": "DNK",
       "Finland": "FIN", "Germany": "DEU", "Greece": "GRC", "Hungary": "HUN", "Japan": "JPN", "Norway": "NOR",
       "Sweden": "SWE", "United Kingdom": "GBR", "Rumania": "ROU", "United States": "USA", "Italy": "ITA",
       "Belgium": "BEL", "France": "FRA", "Netherlands": "NLD", "Poland": "POL", "Spain": "ESP"}
NO_MADDISON = ["Czechoslovakia", "Estonia", "Latvia"]            # no figures for these years (the snapshot's notes)


def exit_dates() -> dict[str, tuple[int, int]]:
    """ISO code -> the month of leaving gold: the earliest of suspension, exchange control and devaluation (Bernanke
    and James, Table 2.1), and for Argentina and Switzerland their official devaluations (Bernanke 1995)."""
    G = goldexits()
    F, Q = facts(), quotes()
    assert "countries not on the gold standard at all (Spain)" in Q["bj_groups"]
    out = {}
    for c, r in G.iterrows():
        if c in NO_MADDISON or c == "Spain":                     # Spain: never on gold, so it never left
            continue
        out[ISO[c]] = min(ym(r[k]) for k in ("suspension", "exchange_control", "devaluation") if isinstance(r[k], str))
    assert "Argentina and Switzerland" in Q["b95_argch"] and "(December 1929 and October 1936" in Q["b95_argch"]
    out["ARG"], out["CHE"] = (int(F["b95_argch"][0]), 12), (int(F["b95_argch"][1]), 10)
    return out


def exit_groups() -> tuple[list[str], list[str]]:
    """The economies that left gold by the end of 1931 and those that left later."""
    E = exit_dates()
    early = sorted(k for k, d in E.items() if d <= (1931, 12))
    late = sorted(k for k, d in E.items() if d > (1931, 12))
    return early, late


def es_fit():
    """OLS of ip1935 on er1935 over the ten points (statsmodels)."""
    S = es()
    X = np.column_stack([np.ones(len(S)), S.er1935.values])
    return OLS(S.ip1935.values, X).fit()


def parity() -> float:
    """The pre-war parity of the pound in dollars, as Chapter 27's table prints it (checked in book())."""
    return 4.8665


def gbp_per_fine_oz(F) -> float:
    """The Bank's selling price of 1925, £3 17s 10½d an ounce troy of standard gold (11/12 fine), per fine ounce."""
    pounds, shillings, pence, half = F["hc_price"]
    return (pounds + shillings / 20 + (pence + half) / 240) * 12 / 11


# ---------------------------------------------------------------------------------------------------
# 1. Readings of the numbers
SMALL = {"a": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "seventeen": 17, "nineteen": 19, "twenty": 20, "thirty": 30}
MULT = {"hundred": 100, "thousand": 1000}
ORDINAL = {"half": 2, "third": 3, "quarters": 4, "quarter": 4, "fourth": 4}
NTH = {"eighteenth": 18}
# misprints of the OCR, each named in the note of its row
OCR = {"2 5": 25, "4}£": 4.5}


def cardinal(s: str) -> float:
    """An English cardinal: 'six', 'twenty-four', 'nineteen hundred and thirty-one'."""
    total, part = 0, 0
    for w in s.lower().replace("-", " ").split():
        if w == "and":
            continue
        if w in SMALL:
            part += SMALL[w]
        else:
            part = max(part, 1) * MULT[w]
            if MULT[w] >= 1000:
                total, part = total + part, 0
    return float(total + part)


def figure(s: str) -> float:
    """'200,000,000', '153.9', '.56'."""
    return float(s.replace(",", ""))


def read(word: str, how: str) -> list[float]:
    if how == "num":
        return [figure(word)]
    if how == "en":
        return [cardinal(word)]
    if how == "frac":                          # 'three-quarters', 'a third', 'one fourth', 'a quarter'
        a, b = re.split(r"[- ]", word.lower())
        return [float(Fraction(int(cardinal(a)), ORDINAL[b]))]
    if how == "half":                          # 'half', 'halfpenny'
        return [0.5]
    if how == "andhalf":                       # 'three and a half'
        return [cardinal(word.split()[0]) + 0.5]
    if how == "nth":
        return [float(NTH[word.lower()])]
    if how == "milliard":                      # '5 milliards' (French usage: a thousand million)
        return [figure(word.split()[0]) * 1e9]
    if how == "ocr":
        return [float(OCR[word])]
    raise ValueError(how)


FIGURES = re.compile(r"\d[\d,]*(?:\.\d+)?|\.\d+")
EN, NUM = "en", "num"
# id -> [(phrase, how)], in order. A phrase 'context|word' is searched as a whole and read from `word`. Rows not
# listed are read with all the figures of the quotation.
READINGS = {
    "hc_price": [("three", EN), ("seventeen", EN), ("ten", EN), ("half", "half")],
    "hc_bars": [("four hundred", EN)],
    "hc_letter2": [("$|200,000,000", NUM), ("5 milliards", "milliard")],
    "hc_threequarters": [("three-quarters", "frac")],
    "gsa_indemnity": [("eighteenth", "nth"), ("nineteen hundred and thirty-one", EN)],
    "gsa_six": [("six", EN)],
    "k_200m": [(",^|200,000,000", NUM), ("half", "half")],
    "k_tariff": [("2 5", "ocr")],
    "k_quarter": [("a quarter", "frac"), ("25", NUM), ("10", NUM)],
    "frb_bankrate": [("21", NUM), ("4}£", "ocr"), ("to |6", NUM)],
    "spa_fourth": [("one fourth", "frac")],
    "spa_purchase": [("one-fourth", "frac")],
    "fr34_three": [("three", EN)],
    "bj_seven": [("1932", NUM), ("1935", NUM), ("seven", EN)],
    "b95_copyright": [("1994", NUM), ("two", EN)],
    "es_eq": [("IPl935 = |153.9", NUM), ("0.69", NUM), ("ER|1935", NUM), ("10.06", NUM), ("3.51", NUM)],
    "es_data": [("1975", NUM), ("1938", NUM), ("1929", NUM), ("Nations (|1938", NUM)],
    "bs_july1934": [("three and a half", "andhalf"), ("1934", NUM), ("200", NUM)],
    "bs_third": [("1931", NUM), ("1935", NUM), ("a third", "frac"), ("four", EN)],
    "bs_shanghai": [("six", EN), ("1934", NUM), ("562.6", NUM), ("350.2", NUM)],
    "da_volume": [("Publication Date: |1983", NUM), ("(p. |5", NUM), ("40", NUM)],
    "hh_snowden": [("1864", NUM), ("May 15, |1937", NUM)],
    "bj_24": [("twenty-four", EN), ("into |four", EN)],
}
# the misprints of the OCR (and of the sources), each named in the note of its row and printed in the quotation
MISPRINTS = [("hc_third", "Amendmont"), ("gsa_date", "Septeml)er"), ("k_200m", ",^"), ("k_tariff", "2 5"),
             ("k_southamerica", "Anierica"), ("k_southamerica", "eflFort"), ("frb_bankrate", "4}£"),
             ("es_eq", "IPl935"), ("es_59", "141 percent"), ("es_timing", "preceeded"), ("b95_identity", "Ml"),
             ("b95_poland", "Ml"), ("b95_falling", "Mi")]
IMAGE_NOTE = "read on the page image"


def check_readings(df: pd.DataFrame) -> None:
    src = meta()["sources"]
    n = img = 0
    for r in df.itertuples():
        assert r.file in src, (r.id, r.file)
        if src[r.file]["format"] == "image":                 # a value read on a page image: no quotation
            assert not r.quote and IMAGE_NOTE in r.note and r.id not in READINGS, r.id
            img += 1
            continue
        assert r.quote, f"{r.id}: no quotation"
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
            got = [figure(x.rstrip(",")) for x in FIGURES.findall(q)]
        assert [round(g, 6) for g in got] == [round(v, 6) for v in vals], f"{r.id}: read {got}, value column {vals}"
        n += 1
    quoted("rows with values, each read from its quotation", n, 139)
    quoted("rows read on a page image (no quotation)", img, 5)
    N, Q = column("note"), quotes()
    for rid, word in MISPRINTS:
        assert word in N[rid], (rid, word)                  # every misprint is named in the note
        assert word in Q[rid], (rid, word)                  # and printed in the quotation
    assert "OCR misprint" in N["es_eq"] and "is a misprint" in N["es_59"] and "misprint 'preceeded'" in N["es_timing"]


# ---------------------------------------------------------------------------------------------------
# 2. Every “…” of the text against the snapshot
# the chapter's Chinese renderings of the quotations: rendering -> row (or rows)
TRANSLATIONS = {
    "金色枷锁": "b95_eich92",
    # opening
    "暂时修改 1925 年金本位法的议案": "hc_four",
    "来得骇人地突然": "hc_sudden",
    "别无选择，只能暂停通货兑换黄金": "hc_sudden",
    "很少有英国人不为挣断了我们的黄金枷锁而高兴。": "k_fetters",
    "英格兰银行付出了 2 亿英镑的黄金或等价物，约是外国人对伦敦全部债权的一半": "k_200m",
    "弥达斯的诅咒": "k_midas",
    # sec:depressionworld-world
    "恶性循环形成了，银行与投资者越来越不愿把资本借给可能的借款人": "hc_vicious",
    "投资市场上一场世界性的恐慌": "hc_panic",
    "美国与法国合起来，现在已经拿到世界全部黄金的四分之三，把它们埋在自己的金库里。": "hc_threequarters",
    "美国政府提议，一切政府间债务、赔款与救济借款的支付，本金与利息，一律推迟一年。": "hv_postpone",
    "有一股不正常的黄金流动正流进美国，降低了许多外国的信用稳定": "hv_gold",
    # sec:depressionworld-fetters
    "国际商品的价格必须到处都差不多": "k_same",
    "一场竞相通缩的运动，我们每个国家都想比别国更快地压低自己的物价": "k_campaign",
    "没有什么制裁": "bj_sanction",
    "一个重要的不对称": "b95_nominimum",
    "抢购黄金": "b95_scramble",
    "比如说 25\\%，对限制进口的作用与同样税率的关税一样大": "k_tariff",
    "不到四分之一": "k_quarter",
    # sec:depressionworld-1931
    "乐观的": "bj_optimistic",
    "冻结协定": "bj_standstill",
    "我们是被外汇危机逼着这样做的，并不是因为我们自己的国内财政出了什么乱子。": "hc_exchange",
    "印度与直辖殖民地，包括海峡殖民地，自动地跟着英镑走了": "k_followed",
    "德国如果迟迟不学我们的样子，我会感到吃惊": ("k_germany1", "k_germany2"),
    # sec:depressionworld-exits
    "放弃金本位": "bj_abandon",
    "不合理的竞争性汇率优势": "frb_advantage",
    "最不犹豫": "es_ironically",
    # sec:depressionworld-es
    "离群值": "es_outliers",
    "141 percent": "es_59",
    "内生变量": "es_endog",
    "吸进而不是流失黄金": "es_absorbing",
    "以邻为壑": "es_beggar",
    # sec:depressionworld-debate
    "宏观经济学的圣杯": "b95_grail",
    "严重的缺陷": "bj_flawed",
    "为什么有些国家比别的国家更愿意解开黄金的枷锁？": "wolf_fetters",
    # sec:depressionworld-silver
    "行不通": "hc_impracticable",
    "经济上不大、政治上很有力量的白银集团": "fr92_bloc",
    "最终的目标是，货币储备的价值有四分之一是白银，并保持下去": "spa_fourth",
    "1931 年以来，以外币计的银价上涨，给中国带来了严重的通缩与经济损失": "fr34_deflation",
    "银价再大涨，会给中国造成非常严重的伤害，可能引起严重的恐慌。": "fr34_panics",
    "不应当独自维持银本位": "fr34_alone",
    "政府之间拿出来商量交换一定数量的货币，不完全是正常的程序。": "fr34_hull",
    "还没有从中国政府得到数据，详细而确切地说明不利影响的性质与程度": "fr35_data",
    "一价定律": "bs_lawofone",
    "国内严重的通缩，失业增加，破产遍地": "bs_decreetext",
    "也许只是不大的": "fr92_modestly",
    "纯粹的好处": "bs_boon",
    "确实帮着造成了中国物价的下跌": "bs_undoubtedly",
    "并不特别萧条": "bs_notdepressed",
    # sec:depressionworld-latam
    "外国的货币医生": "da_doctors",
    "本国的货币政策": "bcra_national",
    # the 史料说明
    "不到 3\\%": "bs_farm",
    "2 5": "k_tariff",
    "Anierica": "k_southamerica",
    "Ml": "b95_identity",
    "Mi": "b95_falling",
    # the ending
    "翻开新的一章": "k_chapter",
}
# the words of the source that each rendering renders
KEYWORDS = {
    "b95_eich92": ["Golden Fetters: The Gold Standard and the Great Depression"],
    "hc_four": ["This is a Bill for the temporary Amendment of the Gold Standard Act, 1925"],
    "hc_sudden": ["with appalling suddenness", "we had no alternative but to suspend the gold convertibility of the "
                  "currency"],
    "k_fetters": ["There are few Englishmen who do not rejoice at the breaking of our gold fetters."],
    "k_200m": ["in gold or its equivalent, which was about half the total claims of foreigners on London"],
    "k_midas": ["the curse of Midas"],
    "hc_vicious": ["A vicious circle was set up, banks and investors becoming more and more reluctant to lend their "
                   "capital to potential borrowers"],
    "hc_panic": ["a world-wide panic on the part of the investment markets"],
    "hc_threequarters": ["America and France taken together have now acquired three-quarters of the entire gold in "
                         "the world and have buried it in their vaults"],
    "hv_postpone": ["The American Government proposes the postponement during 1 year of all payments on "
                    "intergovernmental debts, reparations, and relief debts, both principal and interest"],
    "hv_gold": ["there is an abnormal movement of gold into the United States which is lowering the credit stability "
                "of many foreign countries"],
    "k_same": ["the prices of international commodities must be much the same everywhere"],
    "k_campaign": ["a competitive campaign of deflation, each of us trying to get our prices down faster than the "
                   "others"],
    "bj_sanction": ["no sanction prevented"],
    "b95_nominimum": ["an important asymmetry"],
    "b95_scramble": ['"scramble for gold"'],
    "k_tariff": ["say, 2 5 per cent, this does as much to restrict our imports as a tariff of that amount"],
    "k_quarter": ["less than a quarter of our total consumption is represented by imports"],
    "bj_optimistic": ['"optimistic" financial statement'],
    "bj_standstill": ['"standstill agreements,"'],
    "hc_exchange": ["we are forced to do this by reason of an exchange crisis and not because of any disorder in our "
                    "own internal finances"],
    "k_followed": ["India and the Crown Colonies, including the Straits Settlements, have automatically followed "
                   "sterling."],
    "k_germany1": ["I shall be astonished if Germany"],
    "k_germany2": ["delays long before following our example."],
    "bj_abandon": ['"abandonment"'],
    "frb_advantage": ["an unreasonable competitive exchange advantage"],
    "es_ironically": ["showed the least hesitation to devalue"],
    "es_outliers": ["Germany and Belgium are outliers"],
    "es_59": ["a 141 percent depreciation"],
    "es_endog": ["endogenous variables"],
    "es_absorbing": ["were absorbing, not losing, gold"],
    "es_beggar": ["beggar—thy—neighbor effects"],
    "b95_grail": ["the Holy Grail of macroeconomics"],
    "bj_flawed": ["were badly flawed", "a major source of the fall in real output"],
    "wolf_fetters": ["why were some more inclined than others to release their gold fetters?"],
    "hc_impracticable": ["The suggestion seems to me impracticable."],
    "fr92_bloc": ["the economically small but politically potent silver bloc"],
    "spa_fourth": ["with the ultimate objective of having and maintaining, one fourth of the monetary value of such "
                   "stocks in silver"],
    "fr34_deflation": ["Since 1931 the rising of silver value in terms of foreign currency has involved severe "
                       "deflation and economic losses to China"],
    "fr34_panics": ["Further material silver price increase would cause very serious injury to China, possibly "
                    "severe panics."],
    "fr34_alone": ["China should not alone maintain the silver standard"],
    "fr34_hull": ["not exactly a normal procedure for governments to take up the question of specific exchanges of "
                  "given amounts of money"],
    "fr35_data": ["has not received from the Chinese Government data indicating in any detail and with any "
                  "particular exactness the character and the extent of the adverse effects"],
    "bs_lawofone": ["'law of one price'"],
    "bs_decreetext": ["severe internal deflation, with growing unemployment, widespread bankruptcies"],
    "fr92_modestly": ["though perhaps only modestly"],
    "bs_boon": ["a largely unalloyed boon"],
    "bs_undoubtedly": ["undoubtedly did help cause the fall in the Chinese price level"],
    "bs_notdepressed": ["not especially depressed"],
    "da_doctors": ["foreign money doctors"],
    "bcra_national": ["national monetary policy"],
    "bs_farm": ["output in the rest of the economy fell less than 3 percent"],
    "k_southamerica": ["South Anierica"],
    "b95_identity": ["Ml = (Ml/BASE)"],
    "b95_falling": ["Mi money supplies"],
    "k_chapter": ["may open a new chapter in the world's monetary history"],
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
        assert q in TRANSLATIONS, f"not listed: “{q}”"
        t = TRANSLATIONS[q]
        for rid in (t,) if isinstance(t, str) else t:
            assert rid in ids, rid
            assert rid in KEYWORDS, f"{rid}: no KEYWORDS"
            if q.isascii():
                assert q in Q[rid], (q, rid)
    stale = set(TRANSLATIONS) - used
    assert not stale, f"listed but not in the text: {sorted(stale)}"
    for rid, words in KEYWORDS.items():
        for w in words:
            assert w in Q[rid], f"{rid}: {w!r} not in the quotation"
    assert set(KEYWORDS) == {r for t in TRANSLATIONS.values() for r in ((t,) if isinstance(t, str) else t)}
    print(f"ok {n} quotations of the text found in the snapshot")


# ---------------------------------------------------------------------------------------------------
# 3. Numbers: said() and the parts of the text it does not read
UNITS = {"万亿": 10 ** 12, "亿": 10 ** 8, "万": 10 ** 4}
AMOUNT = re.compile(r"(\d[\d,]*(?:\.\d+)?)(?:\s*多?(万亿|亿|万))?")
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
        decimals = len(digits.split(".")[1]) if "." in digits else 0
        tol = (0.5 * 10 ** -decimals + slack) * scale
        quoted(f"{phrase[:60]!r}: {digits}{unit}", float(v), figure(digits) * scale, tol=tol + 1e-9 * scale)
    COVERED.append(phrase)


ZH_DIGITS = {"一": 1, "两": 2, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
ZH_UNITS = {"十": 10, "百": 100, "千": 1000, "万": 10 ** 4}


def zh(s: str) -> float:
    """A Chinese numeral of the text: '三', '十二', '四十', '三成', '九成', '三分之一', '一半'."""
    if "分之" in s:
        b, a = s.split("分之")
        return zh(a) / zh(b)
    if s.endswith("成"):                               # 三成 = three tenths
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


def fall(a: float, b: float) -> float:
    """The fall from a to b, per cent."""
    return 100 * (1 - b / a)


def rise(a: float, b: float) -> float:
    return 100 * (b / a - 1)


# ---------------------------------------------------------------------------------------------------
# 4. Numbers, section by section
def guide(F, Y, Q):
    t = TEX.read_text(encoding="utf-8")
    assert f"\\guidequestion{{{GUIDE}}}" in t and GUIDE.startswith(PREV)
    assert PREV in (ROOT / "zh" / "ch28_depressionus.tex").read_text(encoding="utf-8")       # 第 28 章交来的问题
    say("叙述 1931 年从维也纳到伦敦的危机，比较英国的贬值与德国的外汇管制")
    said("叙述 1931 年从维也纳到伦敦的危机", 1931)
    B = boe()
    yrs = sorted({y for y, _ in B.index})
    said("用 1929—1936 年的数据检验离开黄金越早、复苏越早的说法", yrs[0], yrs[-1])


def opening(F, Y, Q):
    d, y = F["gsa_date"]
    assert date(int(y), 9, int(d)).weekday() == 0                                           # 星期一
    said("1931 年 9 月 21 日是星期一", y, 9, d)
    four, act = F["hc_four"]
    assert Q["hc_four"].startswith("4.0 p.m.") and "four o'clock" in column("note")["hc_four"]
    chk("    four in the afternoon (下午四点)", four, told("下午四点，财政大臣", "下午", "点"))
    said("这是一项“暂时修改 1925 年金本位法的议案”", act)
    assert Q["hc_leave"].startswith("I beg to move, That leave be given to bring in a Bill")    # 动议准许提出议案
    assert F["hc_leave"][1] == act
    say("他动议准许政府提出一项议案")
    said("按 1925 年的法律，英格兰银行要按固定的价格卖出金块", act)
    pounds, shillings, pence, half = F["hc_price"]
    said("每盎司标准金 3 英镑 17 先令 10 便士半", pounds, shillings, pence)
    chk("    halfpenny (便士半)", half, 0.5)
    assert "per ounce troy of gold of the standard of fineness prescribed for gold coin" in Q["hc_price"]
    chk("    standard gold, eleven twelfths fine (十二分之十一; the 12/11 of gbp_per_fine_oz)", 11 / 12,
        told("含纯金十二分之十一", "含纯金"))
    say("一英镑合 20 先令，一先令合 12 便士，盎司是称金银的重量单位")
    said("一英镑合 20 先令，一先令合 12 便士", 20, 12)
    said("每根约含 400 盎司纯金", F["hc_bars"][0])
    chk("    six years before (六年以前): 1925 to 1931", y - act, told("六年以前，丘吉尔", "", "年以前"))
    said("8 月初，英格兰银行从美国与法国的中央银行借到 5,000 万英镑", 8, F["hc_50m"][0])
    said("政府又在纽约与巴黎借到 8,000 万英镑", F["hc_80m"][0])
    wed, thu, fri = F["hc_drain"]
    assert "Wednesday 16 to Friday 18 September 1931" in column("note")["hc_drain"] and "nearly £18,000,000" in Q[
        "hc_drain"]
    said("上星期三流出 500 万英镑，星期四 1,000 万，星期五将近 1,800 万", wed, thu, fri)
    assert "a half day, over £10,000,000" in Q["hc_saturday"]
    said("星期六只开半天，也流出了 1,000 多万", F["hc_saturday"][0])
    assert "during the last two months" in column("note")["hc_200m"] and "more than £200,000,000" in Q["hc_200m"]
    said("两个月里，英国损失的黄金与外汇超过 2 亿英镑", F["hc_200m"][0])
    assert F["hc_19th"][0] == d - 2 and date(int(y), 9, int(F["hc_19th"][0])).weekday() == 5      # 星期六
    say("星期六，英格兰银行写信给政府")
    usd, frf = F["hc_letter"]
    said("它在纽约与巴黎安排的 1.25 亿美元与 31 亿法郎贷款已经用完", usd, frf)
    usd2, frf2 = F["hc_letter2"]
    said("政府在纽约借的 2 亿美元、在巴黎谈妥的 50 亿法郎", usd2, frf2)
    assert "a drain of gold for Holland" in Q["hc_holland"]
    assert "at Eight o'Clock" in Q["hc_eight"]
    assert Q["hc_first"] == "presented accordingly, and read the First time"
    say("动议通过以后，议案提出，一读通过")
    chk("    eight in the evening (晚上八点)", 8, told("晚上八点，二读的辩论才开始", "晚上", "点"))
    ayes, noes = F["hc_closure"]
    assert "9.40 p.m." in column("note")["hc_closure"]
    chk("    9.40 p.m. (九点四十分)", [told("九点四十分", "", "点四十分"), told("九点四十分", "九点", "分")], [9, 40])
    said("下院以 271 票对 148 票结束辩论", ayes, noes)
    chk("    ten minutes later (十分钟以后)", 10, told("十分钟以后，下院", "", "分钟"))
    said("下院以 275 票对 112 票否决了一项修正动议", *F["hc_second"])
    assert "read the Third time, and passed" in Q["hc_third"]
    assert F["hl_passed"] == [1, 2, 3] and "Bill read 3a, and passed" in Q["hl_passed"]
    say("上院当晚一读、二读、三读一次走完")
    assert F["hc_assent"][0] == y and "reported the Royal Assent" in Q["hc_assent"]
    s1925 = F["gsa_long"]
    assert "subsection (2) of section one of the Gold Standard Act, 1925" in Q["gsa_long"]
    assert Q["gsa_short"].startswith("2. This Act may be cited") and F["gsa_short"][0] == 2
    chk("    two sections (两节)", F["gsa_short"][0], told("只有两节", "只有", "节"))
    said("这部《1931 年金本位（修正）法》只有两节", F["gsa_short"][1])
    said("1925 年法律第一节第二款停止生效", s1925[1])
    chk("    subsection (2) of section one (第一节第二款)", [told("1925 年法律第一节第二款", "第", "节"),
        told("1925 年法律第一节第二款", "节第", "款")], [1, s1925[0]])
    said("英格兰银行 9 月 18 日以后违反这一款的作为", 9, F["gsa_indemnity"][0])
    chk("    six months (六个月)", F["gsa_six"][0], told("这项权力以六个月为限", "以", "个月"))
    dk, yk = F["k_title"]
    said("9 月 27 日，凯恩斯（John Maynard Keynes，1883—1946）发表了《金本位的终结》", 9, dk, *F["keynes_life"])
    pound, frac = F["k_200m"]
    said("“英格兰银行付出了 2 亿英镑的黄金或等价物，约是外国人对伦敦全部债权的一半”", pound)
    chk("    about half (一半)", frac, told("约是外国人对伦敦全部债权的一半", "全部债权的"))
    assert "Australia and the whole of South Anierica had already abandoned" in Q["k_southamerica"]
    assert "Canada, Italy, Scandinavia have moved in our direction" in Q["k_followed"]
    assert "France and the United States" in Q["k_franceus"]
    assert "last May" in Q["hc_austria"]
    said("英国的危机始于 5 月奥地利一家主要银行的倒闭", 5)
    say("金本位怎样把萧条传到全世界？")


def world(F, Y, Q):
    G, A = goldexits(), averages()
    assert "three-quarters of the entire gold in the world" in Q["hc_threequarters"]
    pct, y0, y1 = F["bj_60"]
    said("按 Bernanke 与 James（1991）的估计，1928—1929 年两国合计持有世界货币黄金的近 60\\%", F["bj_volume"][0], y0,
         1900 + y1, pct)
    assert "close to 60%" in Q["bj_60"] and "took deflationary paths in 1928-29" in Q["bj_60"]
    said("两国正是在 1928—1929 年走上了通缩的路", y0, 1900 + y1)
    us = G.loc["United States"]
    said("1930—1932 年，美国批发物价每年的对数变化依次是$-0.10$、$-0.17$与$-0.12$", 1930, 1932,
         -us.wpi_1930, -us.wpi_1931, -us.wpi_1932)
    said("对数变化乘以 100，大约就是变动的百分数", 100)
    chk("    a log change of -0.10 is about -10% (exp(-0.10) - 1 = -9.5%)", 100 * (math.exp(-0.10) - 1), -10, tol=0.6)
    n24, n4 = F["bj_24"]
    assert len(G) == n24
    assert "Among countries on the gold standard as of 1931" in column("note")["bj_13"]
    said("在他们的 24 个国家里，1931 年还守着金本位的国家，1930 年与 1931 年的通缩相当一致，每年约 13\\%", n24, 1931,
         *F["bj_13"][1:], F["bj_13"][0])
    gold36 = A.loc["average gold 1936"]
    assert abs(abs(gold36.wpi_1930) - 0.13) <= 0.011 and abs(abs(gold36.wpi_1931) - 0.13) <= 0.011
    dh, yh, rel = F["hv_date"]
    said("1931 年 6 月 20 日，美国总统胡佛（Herbert Hoover，1874—1964）发表声明", yh, 6, dh, *F["bnf_hoover"])
    chk("    released the next day (第二天)", rel - dh, 1)
    say("白宫把公布的时间定在第二天")
    chk("    postponement during 1 year (一律推迟一年)", F["hv_postpone"][0], told("一律推迟一年。", "推迟", "年"))


def fetters(F, Y, Q):
    say("\\pi\\approx\\Delta\\ln e+\\pi^{f},\\qquad M\\le\\frac{G+F}{c}.\\label{eq:depressionworld-fetters}")
    said("$e$也就固定了，$\\Delta\\ln e=0$，于是$\\pi\\approx\\pi^{f}$", 0)
    said("货币的上限就要收缩$1/c$个单位", 1)
    said("照 Bernanke（1995）的说法，基础货币与储备之比通常没有法定的下限", B95)
    said("1931 年，倒金字塔的另一个弱点也露了出来", F["bj_enmasse"][0] + 1)
    said("Bernanke（1995）的分解把几层收缩放在一起", B95)
    assert Q["b95_identity"].startswith("(1.1) Ml = (Ml/BASE) x (BASE/RES) x (RES/GOLD) x PGOLD x QGOLD")
    factors = Q["b95_identity"].split("=")[1].split(" x ")
    chk("    five factors on the right (这五项)", len(factors), told("这五项里只要一项下降", "这", "项里"))
    N = column("note")
    assert "beneficiary of large gold inflows early in the Depression" in Q["b95_belgium"]
    assert all(k in N["b95_belgium2"] for k in ("M1/BASE", "RES/GOLD", "BASE/RES"))
    chk("    three ratios (三个比率): Belgium", 3, told("三个比率却一齐下降", "", "个比率"))
    say("比利时在萧条初期得到大量流入的黄金，三个比率却一齐下降，货币存量还是急剧收缩")
    said("本币贬值，$\\Delta\\ln e>0$", 0)
    pct, times = F["bj_25"]
    said("准备比率是 40\\% 时，黄金外流对货币的影响是外流额的 2.5 倍", pct, times)
    chk("    1/0.4 = 2.5", 1 / (pct / 100), times)
    said("“比如说 25\\%，对限制进口的作用与同样税率的关税一样大”", F["k_tariff"][0])
    assert Q["bj_sanction"].startswith("no sanction prevented surplus countries from sterilizing gold inflows")
    assert "en masse in the early 1930s" in Q["bj_enmasse"]
    said("照 Eichengreen（1987）的看法", F["bj_eich87"][0])


def ex_fetters(F, Y, Q):
    c, R, f, out, up = FET["c"], FET["R"], FET["fall"], FET["out"], FET["rise"]
    said("一国的发行准备比率$c=0.4$，储备 100，全是黄金，货币按上限发行。外国物价一年里跌了 10\\%", c, R, f)
    said("为保卫平价，黄金流出 10，货币的上限变成多少？（3）若本国让汇率$e$上升 25\\%", out, 3, up)
    B = boe()
    a, d = B.usd_per_gbp[(1931, 8)], B.usd_per_gbp[(1931, 12)]
    said("（4）1931 年 8 月，一英镑平均合 4.858 美元，12 月只合 3.374 美元", 4, 1931, 8, a, 12, d)
    said("（1）守着金本位，本国物价大约怎样变？（2）", 1, 2)
    pif = math.log(1 - f / 100)
    said("（1）$\\Delta\\ln e=0$，$\\pi\\approx\\pi^{f}=\\ln0.9\\approx-0.105$，本国物价也跌约 10\\%", 1, 0, 1 - f / 100,
         -pif, f)
    m0, m1 = R / c, (R - out) / c
    said("（2）上限从$100/0.4=250$降到$90/0.4=225$，少了 25，是流出额的 2.5 倍", 2, R, c, m0, R - out, c, m1, m0 - m1,
         (m0 - m1) / out)
    de = math.log(1 + up / 100)
    said("（3）$\\Delta\\ln e=\\ln1.25\\approx0.223$，$\\pi\\approx0.223-0.105=0.118$，物价不再下跌，反而上涨约 12.5\\%", 3,
         1 + up / 100, de, de, -pif, de + pif, 100 * (math.exp(de + pif) - 1))
    dln = math.log(a / d)
    said("（4）$e$是一美元值多少英镑，从$1/4.858$升到$1/3.374$，$\\Delta\\ln e=\\ln(4.858/3.374)\\approx0.365$，英国物价应当"
         "上涨约 44\\%", 4, 1, a, 1, d, a, d, dln, 100 * (math.exp(dln) - 1))
    s = B.sauerbeck_1867_77_100
    assert "1867-77 = 100" in boe_meta()["series"]
    said("索尔贝克的批发物价指数（1867—1877 年$=100$）从 79.1 只升到 85.4，1932 年 6 月又降到 77.0", 1867, 1877, 100,
         s[(1931, 8)], s[(1931, 12)], 1932, 6, s[(1932, 6)])
    assert s[(1931, 12)] == s.loc[1931].loc[9:12].max()
    assert s[(1932, 6)] < s[(1931, 8)]                                           # 比贬值以前还低
    say("1932 年 6 月又降到 77.0，比贬值以前还低")
    G = goldexits()
    uk, us = G.loc["United Kingdom"], G.loc["United States"]
    assert us.wpi_1932 < 0                                                        # 美国的物价还在跌
    said("英国批发物价的对数变化 1931—1933 年依次是$-0.18$、$-0.04$与$0.01$", 1931, 1933, -uk.wpi_1931, -uk.wpi_1932,
         uk.wpi_1933)
    assert uk.wpi_1931 < uk.wpi_1932 < 0 <= uk.wpi_1933                          # 放慢了，到 1933 年才停下来
    said("通缩放慢了，到 1933 年才停下来，远没有按贬值的幅度上涨", 1933)


def ex_keynes(F, Y, Q):
    q, dep, col = F["k_quarter"]
    said("照他的估计，英镑要贬值得比 25\\% 多得多，生活费用才会上涨 10\\%", dep, col)
    chk("    less than a quarter (不到四分之一)", q, told("进口的“不到四分之一”", "不到", "”"))
    said("（1）设进口品的英镑价格与贬值同幅度上涨", 1)
    said("英镑贬值 25\\%，生活费用最多涨多少？（2）要让生活费用涨 10\\%", dep, 2, col)
    said("一美元的英镑价格涨了多少？按（1）的算法，生活费用最多该涨多少？", 1)
    B = boe()
    L = B.cost_of_living_jul1914_100
    assert "July 1914 = 100" in boe_meta()["series"]
    said("（3）生活费用指数以 1914 年 7 月为 100，1931 年 8 月是 145，12 月是 148", 3, 1914, 7, 100, 1931, 8, L[(1931, 8)],
         12, L[(1931, 12)])
    a, d = B.usd_per_gbp[(1931, 8)], B.usd_per_gbp[(1931, 12)]
    said("（1）$0.25\\times25\\%=6.25\\%$，比 10\\% 少。（2）$10\\%/0.25=40\\%$，比 25\\% 多得多", 1, q, dep, q * dep, col, 2, col,
         q, col / q, dep)
    drop, up = fall(a, d), rise(1 / a, 1 / d)
    said("（3）英镑从 4.858 美元跌到 3.374 美元，价值跌了约 30.5\\%；一美元的英镑价格从$1/4.858$升到$1/3.374$英镑，涨了约 44\\%",
         3, a, d, drop, 1, a, 1, d, up)
    assert "a tariff of that amount" in Q["k_tariff"]           # Keynes's 25 per cent acts on the sterling price of imports
    said("进口品的美元价格不变时，它们的英镑价格涨的是 44\\%；凯恩斯把贬值 25\\% 比作 25\\% 的关税", up, F["k_tariff"][0],
         F["k_tariff"][0])
    said("按（1）的算法，生活费用最多涨约$0.25\\times44\\%\\approx11\\%$，实际只涨了$148/145-1\\approx2.1\\%$", 1, q, up,
         q * up, L[(1931, 12)], L[(1931, 8)], 1, rise(L[(1931, 8)], L[(1931, 12)]))
    assert rise(L[(1931, 8)], L[(1931, 12)]) < q * up and q * up > col             # Keynes's bound held, by a wide margin
    said("原因与\\exref{ex:depressionworld-fetters}的（4）相同，进口品的英镑价格远没有涨 44\\%", 4, up)


def crisis1931(F, Y, Q):
    said("\\section{1931 年}", F["bj_optimistic"][0])
    assert "in May 1931" in Q["bj_optimistic"]
    said("1931 年 5 月，奥地利信贷银行（Creditanstalt）的一位董事", F["bj_optimistic"][0], 5)
    d0, d1, gold = F["frb_reichsbank"]
    assert "During the period from May 31 to June 23" in column("note")["frb_reichsbank"]
    said("从 5 月 31 日到 6 月 23 日，德国的帝国银行失去了 2.3 亿美元的黄金与 2,000 万美元的外汇", 5, d0, 6, d1, gold,
         F["frb_reichsbank2"][0])
    d, a, b = F["frb_jul16"]
    d2, a2, b2 = F["frb_aug1"]
    assert b == a2
    said("7 月 16 日，帝国银行把贴现率从 7\\% 提到 10\\%，8 月 1 日又提到 15\\%", 7, d, a, b, 8, d2, b2)
    d3, a3, b3 = F["frb_aug12"]
    assert a3 == b2
    said("到 8 月 12 日，它才降回 10\\%", 8, d3, b3)
    assert "During July, 1931" in column("note")["frb_control"]
    said("7 月里，德国、匈牙利与智利对外汇交易实行了管制", 7)
    said("英国同意把 7,000 万英镑的资产冻结在德国", F["hc_200m"][1])
    tot, g = F["frb_billion"]
    N = column("note")
    assert "from the middle of July to September 19" in N["frb_billion"]
    assert "a loss of gold during the latter part of July" in N["frb_billion"]
    assert "the rest the loss of foreign exchange" in N["frb_billion"]
    said("从 7 月中旬到 9 月 19 日，资金几乎不停地从伦敦市场提走，共约 10 亿美元，其中约 1.6 亿美元是 7 月下旬流失的黄金，其余是外汇", 7,
         9, 19, tot, g, 7)
    usd, d4 = F["frb_125"]
    said("8 月 1 日，联邦储备银行给了英格兰银行 1.25 亿美元的信用", 8, d4, usd)
    r = bank_rate()
    j23, j30 = date(1931, 7, 23), date(1931, 7, 30)
    assert j23 in r.index and j30 in r.index and (j30 - j23).days == 7          # 一个星期以后
    said("英格兰银行的贴现率 7 月 23 日从 2.5\\% 提到 3.5\\%，一个星期以后又提到 4.5\\%", 7, 23, rate_on(date(1931, 7, 22)),
         r[j23], r[j30])
    ds = F["frb_sunday"][0]
    assert date(1931, 9, int(ds)).weekday() == 6                                 # 星期日
    said("9 月 20 日星期日，英国政府宣布，已经决定暂停金本位", 9, ds)
    d5, a5, b5 = F["frb_bankrate"]
    s21 = date(1931, 9, int(d5))
    assert r[s21] == b5 and rate_on(s21 - pd.Timedelta(days=1)) == a5
    said("第二天，英格兰银行把贴现率从 4.5\\% 提到 6\\%", a5, b5)
    B = boe()
    said("英镑对美元的汇价，8 月平均是 4.86 美元，12 月只有 3.37 美元", 8, B.usd_per_gbp[(1931, 8)], 12,
         B.usd_per_gbp[(1931, 12)])
    low = date(1932, 6, 30)
    assert r[low] == r.min() and r.index[-1] == low                              # 此后几年一直没变
    said("1932 年春天，贴现率一路降下来，6 月 30 日降到 2\\%", 1932, 6, 30, r[low])
    assert all(r[k] < r[date(1932, 2, 18)] or k == date(1932, 2, 18) for k in r.index if k > date(1932, 2, 18))
    said("1931 年放弃完整金本位的国家有 14 个", *F["bj_fourteen"])
    G = goldexits()
    de = G.loc["Germany"]
    assert de.group == 2 and de.exchange_control == "1931-07"
    assert not isinstance(de.suspension, str) and not isinstance(de.devaluation, str)      # no date in Table 2.1
    said("德国也算在里面，凭的是 1931 年 7 月的外汇管制", *ym(de.exchange_control))
    say("他们的表上，德国没有暂停金本位的日子，也没有贬值的日子")


def compare1931(F, Y, Q):
    said("\\begin{compare}{1931 年的两条路}", F["gsa_date"][1])
    G = goldexits()
    uk, de = G.loc["United Kingdom"], G.loc["Germany"]
    r = bank_rate()
    said("\\cmprow{做了什么}{9 月 21 日不再按固定价格卖出黄金", 9, F["gsa_date"][0])
    said("{7 月实行外汇管制", ym(de.exchange_control)[1])
    said("\\cmprow{利率}{贴现率先提到 6\\%，1932 年 6 月降到 2\\%}", F["frb_bankrate"][2], 1932, 6, r.min())
    said("帝国银行的贴现率 8 月 1 日提到 15\\%，8 月 12 日降回 10\\%", 8, F["frb_aug1"][0], F["frb_aug1"][2], 8,
         F["frb_aug12"][0], F["frb_aug12"][2])
    B = boe()
    drop = fall(B.usd_per_gbp[(1931, 8)], B.usd_per_gbp[(1931, 12)])
    chk("    about three tenths (约三成)", drop / 100, told("英镑对美元跌了约三成", "约"), tol=0.02)
    said("{到 1931 年 12 月，英镑对美元跌了约三成}", 1931, 12)
    said("\\cmprow{1932 年的批发物价}{对数变化$-0.04$}{对数变化$-0.14$\\cite{bernanke1991}}", 1932, -uk.wpi_1932,
         -de.wpi_1932)
    assert uk.wpi_1932 < 0 and de.wpi_1932 < 0 and de.ip_1932 < 0
    assert abs(uk.ip_1932) < 0.005 and "A '-.00' or '-0.00' is printed as in the table" in load_snapshot(
        "depressionworld_goldexits")[1]["notes"]                                 # 约为 0: the table's -.00
    said("\\cmprow{工业生产的对数变化}{1932 年约为 0，几乎没变；1933 年$0.05$}{1932 年$-0.24$；1933 年$0.13$\\cite{bernanke1991}}",
         1932, uk.ip_1932, 1933, uk.ip_1933, 1932, -de.ip_1932, 1933, de.ip_1933)
    assert uk.ip_1933 > 0 and de.ip_1933 > 0                                     # 都在 1933 年回升
    said("两国的工业生产都在 1933 年回升", 1933)


ZH_NAMES = {"Spain": "西班牙", "Australia": "澳大利亚", "New Zealand": "新西兰", "Austria": "奥地利", "Canada": "加拿大",
            "Czechoslovakia": "捷克斯洛伐克", "Denmark": "丹麦", "Estonia": "爱沙尼亚", "Finland": "芬兰", "Germany": "德国",
            "Greece": "希腊", "Hungary": "匈牙利", "Japan": "日本", "Latvia": "拉脱维亚", "Norway": "挪威", "Sweden": "瑞典",
            "United Kingdom": "英国", "Rumania": "罗马尼亚", "United States": "美国", "Italy": "意大利", "Belgium": "比利时",
            "France": "法国", "Netherlands": "荷兰", "Poland": "波兰"}
GROUP_HEADS = {1: "第一组：不在金本位上，或 1931 年以前离开", 2: "第二组：1931 年离开", 3: "第三组：1932—1935 年离开",
               4: "第四组：1936 年仍在金本位上"}


def zh_date(s) -> str:
    if not isinstance(s, str):
        return "—"
    return "／".join(f"{int(y)} 年 {int(m)} 月" for y, m in (p.split("-") for p in s.split("/")))


def exits_table(F, Y, Q):
    """tab:depressionworld-exits: every row as the snapshot gives it, in Bernanke and James's order and groups."""
    G = goldexits()
    t = tex_text()
    body = t[t.index("\\label{tab:depressionworld-exits}"):t.index("\\bottomrule")]
    rows = [l.strip() for l in body.splitlines() if l.strip().endswith("\\\\") and "&" in l and "国家 &" not in l]
    assert [r.split(" & ")[0] for r in rows] == [ZH_NAMES[c] for c in G.index]
    for c, r in G.iterrows():
        line = " & ".join([ZH_NAMES[c]] + [zh_date(r[k]) for k in ("return", "suspension", "exchange_control",
                                                                       "devaluation")]) + " \\\\"
        nums = [int(x) for k in ("return", "suspension", "exchange_control", "devaluation") if isinstance(r[k], str)
                for p in r[k].split("/") for x in p.split("-")]
        said(line, *nums)
    heads = re.findall(r"\\multicolumn\{5\}\{@\{\}l\}\{([^}]*)\}", body)
    assert heads == [GROUP_HEADS[g] for g in sorted(GROUP_HEADS)]
    assert list(G.group) == sorted(G.group)                                      # the table runs group by group
    mc = "\\multicolumn{5}{@{}l}{"
    said(mc + GROUP_HEADS[1], 5, 1931)
    said(mc + GROUP_HEADS[2], 5, 1931)
    said(mc + GROUP_HEADS[3], 5, 1932, 1935)
    said(mc + GROUP_HEADS[4], 5, 1936)
    for g, c in ((1, ["Spain", "Australia", "New Zealand"]), (4, ["France", "Netherlands", "Poland"])):
        assert list(G[G.group == g].index) == c
    assert list(G[G.group == 3].index) == ["Rumania", "United States", "Italy", "Belgium"]
    assert (G.group == 2).sum() == F["bj_fourteen"][1]
    for c in ("Australia", "New Zealand"):                                       # left before 1931
        r = G.loc[c]
        assert min(ym(r[k]) for k in ("suspension", "devaluation") if isinstance(r[k], str)) < (1931, 1)
    for c, r in G[G.group == 2].iterrows():                                      # left in 1931
        assert min(ym(r[k]) for k in ("suspension", "exchange_control", "devaluation") if isinstance(r[k], str))[0] \
            == 1931, c
    for c, r in G[G.group == 3].iterrows():                                      # left in 1932-1935
        assert 1932 <= min(ym(r[k]) for k in ("suspension", "exchange_control", "devaluation")
                           if isinstance(r[k], str))[0] <= 1935, c
    m = load_snapshot("depressionworld_goldexits")[1]
    assert "Tables 2.1 (p. 37)" in m["source"] and Q["bj_source"].startswith("League of Nations, Yearbook")
    said("\\datasource{Bernanke 与 James（1991）表 2.1（第 37 页），据扫描页核对", 1991, 2.1, 37)


def exits(F, Y, Q):
    G, A = goldexits(), averages()
    n24, four = F["bj_24"]
    said("按 Bernanke 与 James（1991）的分法，24 个国家依离开金本位的时间分成四组", 1991, n24)
    chk("    four groups (四组)", four, told("依离开金本位的时间分成四组", "分成", "组"))
    gr = F["bj_groups"]
    said("还有 1931 年以前就离开的澳大利亚与新西兰", gr[1])
    said("第二组在 1931 年离开，有 14 个国家", gr[3], gr[4])
    said("第三组在 1932—1935 年离开，依次是罗马尼亚、美国、意大利与比利时", gr[6], gr[7])
    said("第四组到 1936 年还守着完整的金本位，只剩法国、荷兰与波兰", gr[-1])
    gold, non = A.loc["grand average gold"], A.loc["grand average non-gold"]
    yrs = [1932, 1933, 1934, 1935]
    assert gr[8:12] == yrs
    gw = [gold[f"wpi_{y}"] for y in yrs]
    nw = [non[f"wpi_{y}"] for y in yrs]
    said("1932—1935 年，守着金本位的国家，批发物价每年的对数变化平均是$-0.13$、$-0.07$、$-0.04$与$-0.05$", 1932, 1935,
         *[-x for x in gw])
    assert all(x < 0 for x in gw)
    chk("    the image reading of 1933 (the text layer dropped the minus sign)", gold.wpi_1933, F["bj_t22_gold1933"][0])
    said("离开的国家是$-0.01$、$0.00$、$0.03$与$0.04$", -nw[0], *nw[1:])
    said("离开金本位的国家，物价到 1933 年已经稳住", F["bj_stabilized"][0])
    said("这一点 Choudhri 与 Kochin（1980）早已指出", F["bj_spain"][0])
    sp = G.loc["Spain"]
    assert max(abs(sp[f"wpi_{y}"]) for y in range(1930, 1937)) <= 0.05            # 躲过了普遍的通缩
    gi = np.mean([gold[f"ip_{y}"] for y in yrs])
    ni = np.mean([non[f"ip_{y}"] for y in yrs])
    y0, y1, seven = F["bj_seven"]
    chk("    the grand averages of Table 2.4: non-gold minus gold, 1932-1935 (percentage points)", 100 * (ni - gi), seven,
        tol=0.5)
    said("1932—1935 年，不在金本位上的国家，工业生产每年的增长平均比守着金本位的国家高约 7 个百分点", y0, y1, seven)
    early, late = exit_groups()
    R = ratio1935()
    say("离开的月份取暂停金本位、外汇管制与贬值三者中最早的一个，这是本书的取法")
    said("这样分，1931 年底以前离开的有 14 个经济体", 1931, len(early))
    said("它们 1935 年的人均 GDP 简单平均是 1929 年的 100.0\\%", 1935, 1929, R[early].mean())
    assert min(exit_dates()[k] for k in late) >= (1932, 1)                       # 1932 年或更晚
    said("1932 年或更晚才离开的 8 个，平均只有 89.6\\%", 1932, len(late), R[late].mean())
    G2 = [ISO[c] for c in G[G.group == 2].index if c not in NO_MADDISON]
    assert set(G2) < set(early) and set(early) - set(G2) == {"AUS", "NZL", "ARG"}  # not Bernanke and James's 14


def goldbloc(F, Y, Q):
    G = goldexits()
    it, be = G.loc["Italy"], G.loc["Belgium"]
    said("美国 1933 年离开", ym(G.loc["United States"].suspension)[0])
    said("意大利 1934 年 5 月实行外汇管制，比利时 1935 年 3 月贬值", *ym(it.exchange_control), *ym(be.devaluation))
    po = G.loc["Poland"]
    assert ym(po.exchange_control) == (int(F["wolf_poland"][0]), 4) and "until April 1936" in Q["wolf_poland"]
    assert "July 1933" in Q["wolf_july1933"]
    said("按 Wolf（2007）的说法，波兰 1933 年 7 月加入金集团，1936 年 4 月才离开", Y["wolf_dp"], F["wolf_july1933"][0], 7,
         F["wolf_poland"][0], 4)
    y, amt = F["frb_2100"]
    said("从 1935 年 3 月起，法兰西银行流失的黄金超过 21 亿美元", y, 3, amt)
    d = F["frb_sep25"][0]
    said("1936 年 9 月 25 日，美国财政部发表一份声明", Y["frb_sep25"], 9, d)
    chk("    the next day (第二天): Belgium on the 26th", F["frb_belgium"][0] - d, 1)
    say("第二天，比利时宣布赞同")
    said("9 月 27 日，荷兰禁止黄金出口；瑞士的法令 9 月 28 日生效", 9, F["frb_netherlands"][0], 9, F["frb_swiss28"][0])
    assert "an embargo on gold exports" in column("note")["frb_netherlands"]
    N = column("note")
    assert "the law of 1 October 1936" in N["frb_franc2"] and "the law of 25 June 1928" in N["frb_franc1"]
    said("法国在 10 月 1 日立法。1928 年的法律规定，一法郎含 65.5 毫克成色九成的黄金", 10, 1, 1928, F["frb_franc1"][0])
    assert "65.5 milligrams of gold .900 fine" in N["frb_franc1"]
    chk("    .900 fine (九成)", 0.9, told("毫克成色九成的黄金", "成色", "的黄金"))
    lo, hi = F["frb_franc2"]
    said("新法律让政府把它定在 43 毫克到 49 毫克之间", lo, hi)
    a, b = F["frb_franc3"]
    chk("    43/65.5 and 49/65.5 (per cent)", [100 * lo / F["frb_franc1"][0], 100 * hi / F["frb_franc1"][0]], [a, b],
        tol=0.05)
    said("按公报的计算，这约是旧平价的 65.6\\% 到 74.8\\%", a, b)
    years_on = 1936 - 1931
    chk("    five years and more (五年多): September 1931 to September 1936", years_on, told("法国守了五年多", "守了", "年多"))


def compare_france(F, Y, Q):
    G = goldexits()
    R = ratio1935()
    said("\\cmprow{1920 年代}{1925 年按战前的旧平价回到黄金", 1920, ym(G.loc["United Kingdom"]["return"])[0])
    fr = G.loc["France"]["return"].split("/")
    said("{1926 年事实上稳定、1928 年立法，新平价约是战前金价值的五分之一", ym(fr[0])[0], ym(fr[1])[0])
    said("{英国：1931 年离开}{法国：守到 1936 年}", F["gsa_date"][1], ym(G.loc["France"].devaluation)[0])
    said("照 Bernanke（1995）的说法，1928 年的法律促使法兰西银行把外汇换成黄金", B95, F["b95_france1928"][0])
    said("{照 Bernanke（1995）的看法，法国人把守住金本位与民族自豪感连在一起}", B95)
    said("\\cmprow{离开的方式}{9 月 21 日暂停按固定价格卖出黄金}{1936 年 10 月立法，把法郎的含金量降到原来的 65.6\\%—74.8\\%}", 9,
         F["gsa_date"][0], *ym(G.loc["France"].devaluation), *F["frb_franc3"])
    yrs = [1932, 1933, 1934, 1935]
    uk_w = [G.loc["United Kingdom"][f"wpi_{y}"] for y in yrs]
    fr_w = [G.loc["France"][f"wpi_{y}"] for y in yrs]
    said("\\cmprow{1932—1935 年的批发物价}{每年的对数变化在$-0.04$到$0.04$之间}", 1932, 1935, -min(uk_w), max(uk_w))
    assert all(x < 0 for x in fr_w)                                              # 每年都在跌
    said("{每年都在跌，对数变化在$-0.16$到$-0.06$之间\\cite{bernanke1991}}", -min(fr_w), -max(fr_w))
    said("\\cmprow{1935 年的人均 GDP}{1929 年的 105.4\\%}{1929 年的 86.7\\%}", 1935, 1929, R["GBR"], 1929, R["FRA"])
    said("为恢复战前平价出力最多的国家，到 1930 年代贬值时“最不犹豫”", 1930)
    assert "in the early 'twenties showed the least hesitation to devalue in the early 'thirties" in Q["es_ironically"]
    said("两国的选择，各有自己 1920 年代的来历", 1920)


def es_section(F, Y, Q):
    S = es()
    wp, yr = F["es_wp"]
    said("可以概括在 Eichengreen 与 Sachs（1984）的一张图里", yr)
    said("图上是欧洲的 10 个国家，横轴是 1935 年的汇率，纵轴是 1935 年的工业生产，都以 1929 年为 100", len(S),
         F["es_terminal"][0], F["es_terminal"][0], 1929, 100)
    assert Q["es_units"] == "Note: The exchange rate is in units of gold per unit of domestic currency."
    fr100, uk59, _ = F["es_59"]
    said("法国的值是 100，汇率没有变；英国是 59，即英镑的黄金价值只剩 1929 年的 59\\%", fr100, uk59, 1929, uk59)
    said("终点选 1935 年", F["es_terminal"][0])
    said("贬值的幅度与 1929—1935 年的增长之间看来有正的关系", *F["es_positive"])
    a, b, _, ta, tb = F["es_eq"]
    crit95, crit99, p95, p99 = F["es_critical"]
    assert abs(ta) > crit99 and abs(tb) > crit99                                  # both significant at 99%
    said("估计出的$a$是 153.9，$b$是$-0.69$，两个系数在 99\\% 的置信水平上都显著", a, b, p99)
    r2 = F["es_r2"][0]
    said("校正以后的$R^{2}$是 0.56，10 个国家工业生产的差别，直线解释了一半多", 2, r2, len(S))
    assert r2 > 0.5
    said("斜率的意思是，一国货币的黄金价值每低 10 个点，1935 年的工业生产大约高 7 个点", 10, 1935, b * 10)
    fit = es_fit()
    c0, c1 = fit.params
    assert abs(c0 - a) < 0.05 and abs(-c1 - b) < 0.01                          # the refit (the 史料说明, the caption)
    say("图上有两个点离直线最远")
    resid = pd.Series(fit.resid, index=S.index)
    assert set(resid.abs().sort_values().index[-2:]) == {"Germany", "Belgium"}   # 两个点离直线最远
    assert resid["Germany"] > 0 > resid["Belgium"]
    assert "devalued only at the end of the period" in Q["es_belgiumlate"]
    be = goldexits().loc["Belgium"]
    assert ym(be.devaluation) == (1935, 3)                                       # 到快结束时才贬值


def ex_es(F, Y, Q):
    S = es()
    fit = es_fit()
    c0, c1 = fit.params
    a, b, _, ta, tb = F["es_eq"]
    crit95, crit99, p95, p99 = F["es_critical"]
    said("用\\figref{fig:depressionworld_es}的点与拟合的直线，截距 153.9，斜率$-0.699$", c0, -c1)
    said("给出的$t$统计量是 10.06 与 3.51，95\\% 与 99\\% 置信水平上的临界值是 2.31 与 3.36", ta, tb, p95, p99, crit95, crit99)
    uk, fr, de = S.loc["United Kingdom"], S.loc["France"], S.loc["Germany"]
    said("英国的汇率是 59.9，工业生产 112.4；法国是 99.9 与 71.2；德国是 100.3 与 99.7", uk.er1935, uk.ip1935, fr.er1935,
         fr.ip1935, de.er1935, de.ip1935)
    gap = uk.ip1935 - fr.ip1935
    said("（1）按式~\\eqref{eq:depressionworld-es}，三国的拟合值各是多少？残差$u_i$呢？（2）英国与法国的工业生产相差 41.2 个点",
         1, 2, gap)
    said("（3）斜率显著吗？（4）英镑的黄金价值是 59.9，比 1929 年低了百分之几？", 3, 4, uk.er1935, 1929)
    A0, B1 = round(c0, 1), round(c1, 3)
    for name, row, phrase in (("UK", uk, "（1）英国$153.9-0.699\\times59.9\\approx112.0$，残差约$+0.4$"),
                              ("France", fr, "法国$153.9-0.699\\times99.9\\approx84.1$，残差约$-12.9$"),
                              ("Germany", de, "德国$153.9-0.699\\times100.3\\approx83.8$，残差约$+15.9$")):
        fitted = A0 + B1 * row.er1935
        res = row.ip1935 - fitted
        vals = ([1] if name == "UK" else []) + [A0, -B1, row.er1935, fitted, abs(res)]
        said(phrase, *vals)
        assert (res > 0) == ("+" in phrase.split("残差约")[1])
    explained = -B1 * (fr.er1935 - uk.er1935)
    said("（2）$0.699\\times(99.9-59.9)\\approx28.0$个点，约是差距的三分之二", 2, -B1, fr.er1935, uk.er1935, explained)
    chk("    about two thirds (三分之二)", explained / gap, told("约是差距的三分之二", "差距的"), tol=0.02)
    said("（3）斜率的$t$统计量 3.51 大于 99\\% 的临界值 3.36", 3, tb, p99, crit99)
    assert tb > crit99
    said("（4）低了$100-59.9=40.1\\%$", 4, 100, uk.er1935, 100 - uk.er1935)
    said("反过来算，黄金的英镑价格涨了$100/59.9-1\\approx67\\%$", 100, uk.er1935, 1, 100 * (100 / uk.er1935 - 1))
    said("两种算法的差别，与\\exref{ex:depressionworld-keynes}的 30.5\\% 与 44\\% 一样", fall(boe().usd_per_gbp[(1931, 8)],
         boe().usd_per_gbp[(1931, 12)]), rise(1 / boe().usd_per_gbp[(1931, 8)], 1 / boe().usd_per_gbp[(1931, 12)]))


def es_limits(F, Y, Q):
    assert "not just on economic pressures but on national attitudes" in Q["es_predetermined"]
    said("第三，1930 年代的汇率不只取决于经济上的压力，也取决于各国对本位的态度，这种态度在 1930 年代初的事件以前就已形成",
         *F["es_predetermined"])
    assert "devaluation preceeded the beginning of recovery, judged on the basis of annual data" in Q["es_timing"]
    say("第一，按年度数据判断，在他们的例子里，贬值都在复苏开始以前")
    said("10 个点也说明不了一国贬值对邻国的影响", len(es()))
    b = es_fit().params[1]
    said("\\figref{fig:depressionworld_es}的斜率是$-0.70$，并不等于说任何一国把汇率压低 10 个点，工业生产就会多 7 个点", -b,
         10, -b * 10)
    said("横截面只比较了各国 1935 年的位置", 1935)
    said("人人都贬值时，谁也得不到 7 个点", -b * 10)


def debate(F, Y, Q):
    said("Bernanke（1995）的第一句话是", B95)
    _, _, yb = F["b95_eich92"]
    assert Q["b95_eich92"].startswith("Golden Fetters: The Gold Standard and the Great Depression")
    say("这本书题为《金色枷锁》（\\emph{Golden Fetters}），本章的章名借用了它")
    assert "“金色枷锁”" in TEX.read_text(encoding="utf-8").split("\n")[2]      # the chapter title
    said("照 Bernanke（1995）的说法，去留的决定实际上在一定程度上是内生的", B95)
    said("可是 1929 年与 1930 年，1931 年离开黄金的国家与留下的国家", *F["b95_similar"])
    assert "endogenous to a degree" in Q["b95_endogenous"] and "should tend to strengthen" in Q["b95_strengthen"]
    say("校正以后，经济扩张与离开黄金的关联只会更强")
    yw, p23 = F["wolf_fetters"]
    said("Wolf（2007）的论文从 Eichengreen（1992）的一个问题出发", Y["wolf_dp"], yw)
    assert yb == yw                                                              # the same book
    assert "the very month when a country will exit gold" in Q["wolf_predict"]


def silver_section(F, Y, Q):
    say("s=0.7553\\,p_{s},\\qquad e=\\frac{1}{s},\\qquad \\pi\\approx\\pi^{f}-\\Delta\\ln p_{s}.\\label{eq:depressionworld-silver}")
    fine = F["bs_7553"][1]
    said("1933 年 3 月定下的标准银元，含纯银约 0.76 盎司", Y["bs_7553"], 3, fine)
    assert "the standard yuan of March 1933" in column("note")["bs_7553"]
    assert Q["bs_1914"].startswith("Bank notes were denominated in 'yuan'. Before 1933, bank notes were issued on the "
                                   "basis of the silver yuan coin")
    say("中国的钞票以元为单位，按银元兑现")
    y33, y14, grams, fine14 = F["bs_1914"]
    said("1933 年以前通用的银元按 1914 年的条例铸造，重 27 克，成色 88\\%", y33, y14, grams, fine14)
    TROY = 31.1035                                                               # grams in a troy ounce
    old_oz = grams * fine14 / 100 / TROY
    chk("    the yuan of 1914: 27 g x 0.88 / 31.1035 g (about 0.764 oz, the note)", old_oz, 0.764, tol=0.0005)
    assert "about 0.764 fine ounces" in column("note")["bs_1914"]
    assert fine < old_oz                                                         # 比旧银元略少
    said("含纯银约 0.76 盎司，比旧银元略少", fine)
    S, C = silver(), china()
    said("前一半发生在 1929—1931 年。纽约的银价从 1929 年每盎司 53.0 美分降到 1931 年的 28.7 美分", 1929, 1931, 1929,
         S.ny_silver_cents_per_oz[1929], 1931, S.ny_silver_cents_per_oz[1931])
    said("一元的价值从 41.9 美分降到 22.4 美分", S.yuan_cents_year[1929], S.yuan_cents_year[1931])
    said("上海的批发物价以 1926 年为 100，1929 年是 104.5，1931 年升到 126.7", 1926, 100, 1929,
         C.shanghai_wpi_1926_100[1929], 1931, C.shanghai_wpi_1926_100[1931])
    y0, y1, third, four = F["bs_third"]
    said("物价从 1931 年年中开始下跌，到 1935 年秋天见底，比四年以前低了三分之一以上", y0, y1)
    chk("    a third (三分之一)", third, told("比四年以前低了三分之一以上", "低了", "以上"), tol=1e-9)
    chk("    four years (四年以前)", four, told("比四年以前低了三分之一以上", "比", "年以前"))
    said("按年平均，上海的批发物价从 1931 年的 126.7 降到 1935 年的 96.4", 1931, C.shanghai_wpi_1926_100[1931], 1935,
         C.shanghai_wpi_1926_100[1935])
    assert fall(C.shanghai_wpi_1926_100[1931], C.shanghai_wpi_1926_100[1935]) < 100 * third   # the annual average:
    assert S.ny_silver_cents_per_oz.loc[1929:1936].idxmin() == 1932                           # less than a third
    said("银价在 1933 年以后回升，1935 年平均每盎司 64.3 美分", 1933, 1935, S.ny_silver_cents_per_oz[1935])
    said("在 1933 年底发起", F["fr92_bloc"][0])
    assert "in late 1933" in Q["fr92_bloc"]
    said("1934 年 6 月 19 日批准的白银收购法宣布，美国的政策是提高货币储备里白银对黄金的比例", F["spa_june"][1], 6,
         F["spa_june"][0])
    assert "proportion of silver to gold in the monetary stocks" in column("note")["spa_policy"]
    chk("    less than one-fourth (不到四分之一)", F["spa_purchase"][0], told("白银不到四分之一的时候", "不到", "的时候"))
    assert "authorized and directed to purchase silver, at home or abroad" in Q["spa_purchase"]
    chk("    one fourth (四分之一)", F["spa_fourth"][0], told("有四分之一是白银", "有", "是白银"))
    d, y = F["fr34_date"]
    said("9 月 24 日，中国驻美公使施肇基", 9, d)
    assert y == F["spa_june"][1]
    said("“1931 年以来，以外币计的银价上涨", F["fr34_deflation"][0])
    chk("    over three times (三倍多)", F["fr34_three"][0], told("已是以往任何一个整年的三倍多", "整年的", "倍多"))
    d2, y2 = F["fr34_hulldate"]
    said("10 月 2 日，施肇基应约来见", 10, d2)
    d3, y3 = F["fr35_date"]
    said("1935 年 1 月 26 日，美国国务院交给中国公使馆一份照会", y3, 1, d3)


def ex_silver(F, Y, Q):
    S, C = silver(), china()
    fine = F["bs_7553"][1]
    p = S.ny_silver_cents_per_oz
    said("标准银元含纯银 0.7553 盎司。纽约的银价，1929 年平均每盎司 52.99 美分，1931 年 28.70 美分，1935 年 64.27 美分", fine,
         1929, p[1929], 1931, p[1931], 1935, p[1935])
    yu = S.yuan_cents_year
    said("同年一元的实际汇价是 41.9、22.4 与 36.6 美分", yu[1929], yu[1931], yu[1935])
    said("（1）按式~\\eqref{eq:depressionworld-silver}，三年里一元各值多少美分？（2）Brandt 与 Sargent 的表 4", 1, 2, 4)
    r30, r34 = C.loc[1930], C.loc[1934]
    said("1929—1930 年，美国的批发物价变了$-9.3\\%$，一元的美元价格变了$-28.1\\%$，预测上海物价变多少？实际是$+9.9\\%$", 1929,
         1930, -r30.us_wpi_pct, -r30.usd_per_yuan_pct, r30.actual_shanghai_pct)
    said("（3）1933—1934 年，这两个数是$+13.7\\%$与$+28.1\\%$，预测是多少？实际是$-8.6\\%$", 3, 1933, 1934, r34.us_wpi_pct,
         r34.usd_per_yuan_pct, -r34.actual_shanghai_pct)
    said("（4）为什么 1935 年的实际汇价比（1）的值低得多？", 4, 1935, 1)
    v = {y: fine * p[y] for y in (1929, 1931, 1935)}
    said("（1）$0.7553\\times52.99\\approx40.0$，$0.7553\\times28.70\\approx21.7$，$0.7553\\times64.27\\approx48.5$", 1, fine,
         p[1929], v[1929], fine, p[1931], v[1931], fine, p[1935], v[1935])
    gaps = [abs(v[y] - yu[y]) for y in (1929, 1931)]
    assert max(gaps) < told("前两年与实际相差不到两个美分", "不到", "个美分")
    assert v[1935] - yu[1935] > 10                                                # 1935: much lower
    said("（2）$-9.3-(-28.1)=+18.8\\%$，实际只涨了 9.9\\%", 2, -r30.us_wpi_pct, -r30.usd_per_yuan_pct,
         r30.predicted_shanghai_pct, r30.actual_shanghai_pct)
    said("（3）$13.7-28.1=-14.4\\%$，实际是$-8.6\\%$", 3, r34.us_wpi_pct, r34.usd_per_yuan_pct, -r34.predicted_shanghai_pct,
         -r34.actual_shanghai_pct)
    for y in (1930, 1934):
        r = C.loc[y]
        assert np.sign(r.predicted_shanghai_pct) == np.sign(r.actual_shanghai_pct)   # 方向相同
    said("（4）1934 年 10 月，中国政府对出口白银课税", 4, F["frb_oct1934"][0], 10)


def casebox(F, Y, Q):
    C = china()
    ym_ = yuan_monthly()
    said("\\begin{case}{中国 · 白银 · 1934—1935}", 1934, 1935)
    said("1934 年 10 月，它动用三家大银行的资源", F["bs_oct1934"][0], 10)
    assert "three major banks" in Q["bs_oct1934"]
    chk("    three banks (三家)", 3, told("它动用三家大银行的资源", "动用", "家"))
    said("为了制止白银出口，政府同时对出口白银课征 10\\% 的税", F["frb_duty"][0])
    N = column("note")
    assert "in order to check the export of silver" in N["frb_equalization"]
    assert "difference between the exchange rate in London and the theoretical parity of the yuan as determined by the " \
           "value of its silver content in the London market" in N["frb_equalization"]
    say("平衡费等于伦敦的汇价与银元的理论平价之差，理论平价按银元的含银量在伦敦市场的价值算")
    assert "on November 2 of this year" in column("note")["frb_38"]
    said("1935 年 11 月 2 日，折价约有 38\\%", 1935, 11, 2, F["frb_38"][0])
    t35, y34, ex = F["bs_july1934"]
    said("据后来的法令，1934 年 7 月起的三个半月里，出口的白银超过 2 亿元", y34, 7, ex * M6)
    chk("    three and a half months (三个半月)", t35, told("1934 年 7 月起的三个半月里", "起的", "个半月") + 0.5)
    six, y, a, b = F["bs_shanghai"]
    said("1934 年下半年，上海各银行的存银从 5.63 亿元降到 3.50 亿元", y, a * M6, b * M6)
    assert six == 6 and "In the last six months of 1934" in Q["bs_shanghai"]
    said("净出口的白银，1934 年估计是 2.8 亿元，1935 年是 2.92 亿元", F["bs_exports34"][0], F["bs_exports34"][1] * M6,
         F["bs_exports35"][0], F["bs_exports35"][1] * M6)
    d, yd = F["bs_decree"]
    said("1935 年 11 月 3 日，中国政府发布紧急法令", yd, 11, d)
    said("新制度 11 月 4 日生效", 11, F["frb_nov4"][0])
    assert "Central Bank of China, and by the partially Government-owned Bank of China and Bank of Communications" in \
        column("note")["frb_legaltender"]
    G = goldexits()
    years_after = yd - ym(G.loc["United Kingdom"].suspension)[0]
    chk("    four years and more (四年多): September 1931 to November 1935", years_after,
        told("比英国离开金本位晚了四年多", "晚了", "年多"))
    m36 = ym_.loc[1936]
    said("改革以后，一元稳在 30 美分左右", 30)
    assert 29 < m36.min() and m36.max() < 31
    said("1936 年的 12 个月里，月平均的汇价最低 29.3 美分，最高 30.0 美分", 1936, len(m36), m36.min(), m36.max())
    said("上海的批发物价 1936 年回升到 108.5", 1936, C.shanghai_wpi_1926_100[1936])
    mon = C.money_6a_myuan
    said("货币存量增加到 90.1 亿元，一年里多了 16\\%", mon[1936] * M6, rise(mon[1935], mon[1936]))


def china_debate(F, Y, Q):
    said("照 Friedman（1992）摘要的说法，这项计划给中国", 1992)
    assert "wartime inflation and postwar hyperinflation" in Q["fr92_inflation"]
    assert "thereby contributed" in Q["fr92_modestly"]                          # the inflation is the link
    say("纸币本位又让后来战时的通胀与战后的恶性通胀来得更早、更猛")
    said("照 Friedman（1992）摘要的说法，美国的白银收购计划", 1992)
    y63, p490 = F["bs_fs490"]
    said("照 Friedman 与 Schwartz（1963）的说法", y63)
    said("在 Brandt 与 Sargent（1989）看来", Y["bs_copyright"])
    mon = china().money_6a_myuan
    said("货币存量从 1931 年的 63.6 亿元增加到 1935 年的 77.7 亿元", 1931, mon[1931] * M6, 1935, mon[1935] * M6)
    said("中国经济相当好地经受住了 1930 年代的外来冲击", F["bs_weathered"][0])
    C = china()
    g, ag = C.gdp_bn_1933yuan, C.agriculture_bn_1933yuan
    said("1934 年，实际 GDP 比上一年降了约 8.7\\%，农业产出降了近 12\\%", 1934, fall(g[1933], g[1934]), F["bs_farm"][0])
    assert F["bs_farm"][0] - 0.5 < fall(ag[1933], ag[1934]) < F["bs_farm"][0]      # 近 12%
    nonag = fall(g[1933] - ag[1933], g[1934] - ag[1934])
    said("其他部门降得不到 3\\%", F["bs_farm"][1])
    assert nonag < F["bs_farm"][1] + 0.05                                         # Table 5: 3.0% (the 史料说明)


def compare_china(F, Y, Q):
    S, A = silver(), averages()
    p = S.ny_silver_cents_per_oz
    said("\\cmprow{1929—1931 年}{银价跌了近一半，银元贬值，上海物价反而上涨}", 1929, 1931)
    assert 0.4 < fall(p[1929], p[1931]) / 100 < 0.5                              # 近一半
    said("{守着平价的国家每年约通缩 13\\%}", F["bj_13"][0])
    said("\\cmprow{1932—1935 年}{银价回升，银元升值，物价下跌，白银外流}", 1932, 1935)
    assert p[1935] > p[1932]
    said("\\cmprow{离开的方式}{1934 年 10 月课出口税，1935 年 11 月改行纸币}", F["frb_oct1934"][0], 10, F["bs_decree"][1], 11)


def latam(F, Y, Q):
    said("1920 年代，拉丁美洲也回到了黄金", 1920)
    said("照 Díaz Alejandro（1983）的描述", F["da_volume"][0])
    assert "sharp declines in the Latin American terms of trade and a milder fall of their export quantum" in Q[
        "da_terms"]
    say("萧条一来，拉丁美洲的贸易条件急剧恶化，出口量也跌了，只是跌得轻一些")
    arg, bra = F["da_t11"][:2]
    said("以 1928—1929 年与 1932—1933 年比较，出口的购买力，阿根廷降了 41.2\\%，巴西降了 42.3\\%", *F["da_quarter"], -arg,
         -bra)
    assert "Argentina, Brazil, Colombia, Cuba, Mexico" in column("note")["da_t11"]
    assert "around one-quarter" in Q["da_quarter"]
    say("以美元计的物价出乎意料地下跌了约四分之一")
    said("到 1934 年，除阿根廷、海地与多米尼加共和国以外", F["da_default"][0])
    said("英镑 1931 年 9 月贬值以后，许多国家实行了外汇管制", F["da_controls"][0], 9)
    y30, y32 = F["da_1932"]
    said("1930 年代工业扩张强劲的拉丁美洲国家，最晚到 1932 年都已放弃了兑换与金本位的其他规则", y30, y32)
    d, y = F["frb_argentina"]
    said("1929 年 12 月 16 日，它关闭了兑换局", y, 12, d)
    assert "closed its conversion office" in column("note")["frb_argentina"]
    assert exit_dates()["ARG"] == (y, 12)                                        # the date Bernanke (1995) uses
    assert "within the framework of an exchange control scheme" in Q["bcra_counter"]
    say("中央银行在外汇管制的框架下推行逆周期的政策")
    said("1935 年的货币与银行改革设立了阿根廷中央银行", F["bcra_mixed"][0])
    said("1935—1943 年，普雷维什（Raúl Prebisch，1901—1986）任总经理", *F["bcra_prebisch"], *F["bnf_prebisch"])
    said("约 35\\% 看来实际上是靠创造货币", F["da_coffee"][0])
    R, M = ratio1935(), maddison()
    said("智利 1932 年的人均 GDP 只有 1929 年的 51.9\\%", 1932, 1929, 100 * M.loc["CHL", 1932] / M.loc["CHL", 1929])
    assert M.loc["CHL"].loc[1929:1938].idxmin() == 1932
    said("到 1935 年，巴西回到 1929 年的 101.2\\%，哥伦比亚到 111.4\\%，阿根廷是 90.4\\%", 1935, 1929, R["BRA"], R["COL"],
         R["ARG"])
    a, b, c, m, u = F["da_t12a"]
    said("按 Díaz Alejandro 的表 1.2，1929—1933 年，阿根廷与墨西哥的实际总产出降了 9.7\\% 与 10.3\\%", 1.2, 1929, 1933, -a, -m)
    said("巴西与哥伦比亚反而增加了 7.6\\% 与 9.9\\%，美国降了 28.9\\%", b, c, -u)
    assert "Argentina, Brazil, Colombia, Mexico, United States" in column("note")["da_t12a"]
    assert all(x > 0 for x in F["da_t12b"]) and len(F["da_t12b"]) == 5           # 1933-37: all five grew


def check_section(F, Y, Q):
    P = parity()
    usd = F["hc_50m"][0] * P
    said("英格兰银行 8 月初借的 5,000 万英镑，按旧平价约合 2.4 亿美元", 8, F["hc_50m"][0], usd)
    share = F["frb_125"][0] / usd
    assert 0.45 < share < 0.55                                                    # 约占一半
    said("联邦储备银行 8 月 1 日给的信用约占一半", 8, F["frb_125"][1])
    said("斯诺登说两个月里流失了 2 亿多英镑，凯恩斯也说付出了 2 亿英镑", F["hc_200m"][0], F["k_200m"][0])
    said("按旧平价，2 亿英镑约合 9.7 亿美元，公报说从 7 月中旬起提走了约 10 亿美元", F["k_200m"][0], F["k_200m"][0] * P, 7,
         F["frb_billion"][0])
    said("Brandt 与 Sargent 的汇率据 Hsiao（1974）", F["bs_hsiao"][2])
    S, C = silver(), china()
    yu = S.yuan_cents_year
    diffs = [abs(rise(yu[y - 1], yu[y]) - C.usd_per_yuan_pct[y]) for y in (1930, 1931)]
    assert max(diffs) < 1.2, diffs                                                # 约一个百分点
    said("1929—1931 年，它的年变化与《银行与货币统计》的年平均相差约一个百分点", 1929, 1931)
    R, E = ratio1935(), exit_dates()
    assert E["CAN"][0] == E["AUT"][0] == 1931
    said("加拿大与奥地利 1931 年就离开了，1935 年的人均 GDP 仍只有 1929 年的 78.0\\% 与 78.6\\%", 1931, 1935, 1929, R["CAN"],
         R["AUT"])
    assert sorted(R[list(E)].sort_values().index[:3]) == ["AUT", "CAN", "POL"]     # the lowest three
    said("德国没有贬值，1935 年却已回到 101.7\\%", 1935, R["DEU"])
    assert "strong correspondence between gold standard membership and falling Mi money supplies" in Q["b95_falling"]
    say("守着金本位的国家，$M_1$几乎都在下降")
    said("照 Bernanke（1995）的说法，波兰是一个小小的例外，1932—1936 年", B95, *F["b95_poland"])


def deeper(F, Y, Q):
    assert F["hc_threequarters"][0] != F["bj_60"][0] / 100                       # 给的比例不同
    say("美国与法国手里的黄金，斯诺登与 Bernanke 和 James 给的比例不同，日子与口径也不同，正文两说并存")
    dh, _, rel = F["hv_date"]
    said("胡佛的声明，美国总统项目的说明写明 6 月 20 日记者会后发出，到 21 日才准发表", 6, dh, rel)
    said("孔祥熙的生年，美国国会图书馆规范档的标目作 1880 年，同一记录的异名作 1881 年", F["loc_kung"][0],
         F["loc_kung1881"][0])
    assert Q["loc_kung"].startswith("Kung, H. H. (Hsiang-hsi), 1880-1967")
    said("Wolf（2007）的摘要说模型预测波兰离开的时间比 1936 年 4 月还晚，结论一节却说预测在 1935 年年中", Y["wolf_dp"],
         F["wolf_later"][0], 4, F["wolf_mid1935"][0])
    assert "even later than April 1936" in Q["wolf_later"] and "mid-1935" in Q["wolf_mid1935"]
    em = load_snapshot("depressionworld_es")[1]
    err = float(re.search(r"reading error about \+-([\d.]+)", em["notes"]).group(1))
    S = es()
    said("Eichengreen 与 Sachs 的工作论文没有列出图 1 的数字，10 个点据图 1 的扫描页读出，读数误差约 0.5", 1, len(S), 1, err)
    said("正文说英国是 59，读出的是 59.9", F["es_59"][1], S.er1935["United Kingdom"])
    v59, m141 = F["es_59"][1], F["es_59"][2]
    said("正文又说 59 意味着贬值“141 percent”。按论文的定义，59 是低了 41\\%；按黄金的英镑价格算，是涨了约 69\\%，都不是 141", v59,
         m141, v59, 100 - v59, 100 * (100 / v59 - 1), m141)
    assert m141 not in (round(100 - v59), round(100 * (100 / v59 - 1)))
    early = exit_groups()[0]
    G = goldexits()
    G2 = [ISO[c] for c in G[G.group == 2].index if c not in NO_MADDISON]
    say("Bernanke 与 James 只按年分组，\\figref{fig:depressionworld_exits}的离开月份是本书按他们的定义取的")
    said("阿根廷与瑞士用 Bernanke（1995）的正式贬值月份", B95)
    said("这样算，1931 年底以前离开的 14 个经济体包括澳大利亚、新西兰与阿根廷", 1931, len(early))
    assert sorted(set(early) - set(G2)) == ["ARG", "AUS", "NZL"]
    assert sorted(c for c in G[G.group == 2].index if c in NO_MADDISON) == ["Czechoslovakia", "Estonia", "Latvia"]
    assert "Czechoslovakia, Estonia and Latvia (in Bernanke and James's table of exits) have none for these years" in \
        maddison_meta()["notes"]
    assert "ESP" not in exit_dates() and not any(isinstance(G.loc["Spain"][k], str) for k in ("suspension", "devaluation"))
    say("第二组里的捷克斯洛伐克、爱沙尼亚与拉脱维亚没有 Maddison 的数，西班牙不在金本位上，都没有画出")
    fit = es_fit()
    a, b, _, ta, tb = F["es_eq"]
    said("用读出的点重新回归，截距 153.89，斜率$-0.699$，两个$t$统计量 10.02 与 3.51，校正以后的$R^{2}$是 0.557，与注 12 的 153.9、"
         "$-0.69$、10.06、3.51 与 0.56 相合", fit.params[0], -fit.params[1], fit.tvalues[0], -fit.tvalues[1], 2,
         fit.rsquared_adj, 12, a, b, ta, tb, F["es_r2"][0])
    assert "note 12" in column("juan")["es_eq"]
    C = china()
    g = C.gdp_bn_1933yuan
    yy0, yy1 = F["bs_yeh"]
    growth = 100 * ((g[yy1] / g[yy0]) ** (1 / (yy1 - yy0)) - 1)
    said("据 Brandt 与 Sargent 转引的 K. C. Yeh 估计，实际 GDP 1931—1936 年平均每年增长 1.5\\%；按该文表 5 的数算是 1.6\\%", yy0, yy1, F["bs_15"][0], 5,
         growth)
    ag = C.agriculture_bn_1933yuan
    said("非农业部门 1934 年降了 3.0\\%，与“不到 3\\%”大致相合", 1934, fall(g[1933] - ag[1933], g[1934] - ag[1934]),
         F["bs_farm"][1])
    said("该文表 2 并列了 Rawski 的货币存量估计与修订的估计，1935 年分别是 88.3 亿元与 77.7 亿元", 2, 1935,
         C.money_5a_myuan[1935] * M6, C.money_6a_myuan[1935] * M6)
    said("Eichengreen（1992）的书没有取得，正文的问题据 Wolf（2007）的引文，书名据 Bernanke（1995）的参考文献", F["b95_eich92"][2],
         Y["wolf_dp"], B95)
    said("Eichengreen（1987）与 Choudhri 和 Kochin（1980）据 Bernanke 与 James 的转述", F["bj_eich87"][0], F["bj_spain"][0])
    y36, y37, p810 = F["bs_yearbook"]
    said("Friedman 与 Schwartz（1963）的“纯粹的好处”、1935 年法令的英文译文（据《中国年鉴》1936—1937 年版第 810 页）、标准银元的含银量"
         "（据 Tamagna 1942）", F["bs_fs490"][0], F["bs_decree"][1], y36, y37, p810, 1942)
    assert "Tamagna 1942" in column("note")["bs_7553"]
    said("巴西咖啡收购的 35\\%，据 Díaz Alejandro 转引 Silber（1977）", F["da_coffee"][0], F["da_coffee"][1])
    said("Eichengreen 与 Sachs 发表在《经济史杂志》1985 年第 45 卷第 4 期的正式版本没有取得，正文据 1984 年的工作论文", 1985, 45, 4,
         F["es_wp"][1])
    assert "Journal of Economic History 45(4), December 1985" in column("note")["es_wp"]
    said("Friedman（1992）的正文没有取得", F["fr92_copyright"][0])
    said("1935 年法令的中文原文没有取得", F["bs_decree"][1])
    said("麦克米伦委员会与梅委员会 1931 年的报告也没有读到", 1931)
    said("Bernanke 与 James 表 2.2 的文字层认错了希腊 1931 年的物价，又丢了金本位国家 1933 年平均值的负号", 2.2, 1931, 1933)
    gm = load_snapshot("depressionworld_goldexits")[1]
    assert "Table 2.2" in gm["source"] or "2.2" in gm["title"]
    said("凯恩斯文中的英镑符号、“2 5”与“Anierica”，Bernanke（1995）的“Ml”", 2, 5, B95)


def legacy(F, Y, Q):
    G = goldexits()
    said("1931 年，英国放弃了固定汇率，德国放弃了资本的自由流动，法国两样都守住，付出的是通缩", 1931)
    fr = G.loc["France"]
    assert all(fr[f"wpi_{y}"] < 0 for y in range(1930, 1936))                    # 法国：通缩
    said("1936 年的声明希望没有哪个国家谋求不合理的汇率优势", Y["frb_sep25"])


def takeaways(F, Y):
    said("9 月 21 日英国暂停按固定价格卖出黄金", 9, F["gsa_date"][0])
    said("1931 年的危机从奥地利信贷银行开始", F["bj_optimistic"][0])
    said("1932—1935 年，不在金本位上的国家工业生产每年平均多增长约 7 个百分点", F["bj_seven"][0], F["bj_seven"][1],
         F["bj_seven"][2])
    early, _ = exit_groups()
    R = ratio1935()
    assert abs(R[early].mean() - 100) < 0.5                                       # 回到 1929 年的水平
    said("1935 年的人均 GDP，早离开的 14 个经济体平均回到 1929 年的水平", 1935, len(early), 1929)
    said("Eichengreen 与 Sachs 的横截面斜率约$-0.70$", -es_fit().params[1])
    said("1935 年 11 月改行纸币", F["bs_decree"][1], 11)


def selfcheck(F, Y):
    f, up = SC1["fall"], SC1["rise"]
    said("外国物价一年里跌了 5\\%，本国守着金本位", f)
    said("若本国让$e$上升 10\\%，又怎样变", up)
    c, loss = SC2["c"], SC2["loss"]
    said("一国的发行准备比率是 25\\%，储备流失 8", c, loss)
    S = es()
    dk = S.loc["Denmark"]
    said("1935 年，丹麦货币的黄金价值是 1929 年平价的 48.5\\%", 1935, 1929, dk.er1935)
    said("实际是 124.1", dk.ip1935)
    p = silver().ny_silver_cents_per_oz
    said("纽约的银价从每盎司 52.99 美分跌到 28.70 美分", p[1929], p[1931])
    # answers
    said("$\\pi\\approx\\pi^{f}\\approx-5\\%$，物价也跌约 5\\%。让$e$上升 10\\%，$\\pi\\approx10\\%-5\\%=5\\%$，物价上涨约 5\\%", f, f, up,
         up, f, up - f, up - f)
    said("上限收缩$8/0.25=32$，是流失额的 4 倍", loss, c / 100, loss / (c / 100), 1 / (c / 100))
    fit = es_fit()
    A0, B1 = round(fit.params[0], 1), round(fit.params[1], 3)
    v = A0 + B1 * dk.er1935
    said("$153.9-0.699\\times48.5\\approx120.0$，实际 124.1，比直线高约 4 个点", A0, -B1, dk.er1935, v, dk.ip1935,
         dk.ip1935 - v)
    fine = F["bs_7553"][1]
    a, b = fine * p[1929], fine * p[1931]
    said("从约 40.0 美分降到约 21.7 美分，降了约 46\\%", a, b, fall(a, b))
    said("一种看政治与信条：照 Bernanke（1995）的看法", B95)
    said("1920 年代经历过通胀的国家最努力地守住新定的平价", 1920)
    said("另一种看经济：照 Wolf（2007）的估计", Y["wolf_dp"])


def ending(F, Y, Q):
    dk, yk = F["k_title"]
    assert "the great events of the last week" in Q["k_chapter"]
    said("1931 年 9 月 27 日，凯恩斯在文章的最后说", yk, 9, dk)
    G = goldexits()
    de, jp, se = G.loc["Germany"], G.loc["Japan"], G.loc["Sweden"]
    assert ym(jp.suspension) == ym(jp.devaluation) == (1931, 12)
    said("德国 1931 年 7 月实行外汇管制，瑞典 9 月、日本 12 月相继离开了金本位", *ym(de.exchange_control),
         ym(se.suspension)[1], ym(jp.suspension)[1])
    assert ym(de.exchange_control)[0] == ym(jp.suspension)[0] == ym(se.suspension)[0]
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 30's question"
    assert t.rstrip(NEXT).rstrip().endswith("\\cite{bernanke1991}。")
    assert t.index("\\end{answers}") < t.index("1931 年 9 月 27 日，凯恩斯在文章的最后说")


def frames(F, Y, Q):
    """The captions of the figures."""
    B, bm = boe(), boe_meta()
    yrs = sorted({y for y, _ in B.index})
    said("(a) 一英镑合多少美元，月平均，1929—1936 年；虚线是旧平价，约 4.87 美元。1933 年 4 月以后美元自己也离开了黄金", yrs[0],
         yrs[-1], parity(), 1933, 4)
    assert "From April 1933 the dollar itself was off gold" in bm["notes"]
    r = bank_rate()
    said("(b) 英格兰银行的贴现率，1929—1936 年，按调整的日子画成阶梯", r.index[0].year, yrs[-1])
    ver = re.search(r"\(version (\d\.\d)\)", bm["source"]).group(1)
    m15 = int(re.search(r"'M(\d+)\. Mthly \$-£", bm["source"]).group(1))
    rm = load_snapshot("boe_millennium_bank_rate_1929_1936")[1]
    d1 = int(re.search(r"'D(\d)\. Official Interest Rates'", rm["source"]).group(1))
    said("数据：英格兰银行，A Millennium of Macroeconomic Data for the UK（3.1 版），表 M15 与 D1", float(ver), m15, d1)
    early, late = exit_groups()
    said("离开黄金越早，1935 年的人均 GDP 越高，但例外不少", 1935)
    said("横轴是离开金本位的月份，按本书的取法，取 Bernanke 与 James（1991）表 2.1 里暂停金本位、外汇管制与贬值三者中最早的一个，"
         "阿根廷与瑞士取 Bernanke（1995）用的正式贬值月份", F["bj_volume"][0], 2.1, B95)
    assert "official devaluation dates" in Q["b95_argch"]
    said("纵轴是 1935 年的人均 GDP，以 1929 年$=100$。22 个经济体，橙色的 14 个在 1931 年底以前离开，与 Bernanke 和 James 第二组的 14 国"
         "不全相同", 1935, 1929, 100, len(early) + len(late), len(early), 1931, F["bj_fourteen"][1])
    mm = maddison_meta()
    said("数据：Maddison 项目数据库 2023 年版（Bolt 与 van Zanden 2024）", int(re.search(r"version (\d{4})", mm["source"]).group(1)),
         int(re.search(r"\((\d{4})\)", mm["citation"]).group(1)))
    fit = es_fit()
    said("汇率越低，1935 年的工业生产越高", 1935)
    said("横轴是 1935 年一单位本币的黄金价值，以 1929 年的平价$=100$；纵轴是 1935 年的工业生产，1929 年$=100$。10 个欧洲国家，琥珀色"
         "虚线是最小二乘拟合，截距 153.9，斜率$-0.70$", 1935, 1929, 100, 1935, 1929, 100, len(es()), fit.params[0],
         -fit.params[1])
    em = load_snapshot("depressionworld_es")[1]
    err = float(re.search(r"reading error about \+-([\d.]+)", em["notes"]).group(1))
    lon = int(re.search(r"from League of Nations \((\d{4})\)", Q["es_data"]).group(1))
    said("点的坐标据 Eichengreen 与 Sachs（1984）图 1 的扫描页读出，读数误差约 0.5。数据：Eichengreen 与 Sachs（1984），他们的来源是国际"
         "联盟（1938）、Mitchell（1975）与 Methorst（1938）", F["es_wp"][1], 1, err, F["es_wp"][1], lon, F["es_data"][0],
         F["es_data"][1])
    S, sm = silver(), load_snapshot("depressionworld_silver")[1]
    yu = S.yuan_cents_year.dropna()
    said("(a) 纽约的银价，每盎司纯银的美分，与一元的美分价值，年平均，1929—1936 年；虚线是按标准银元的含银量 0.7553 盎司算出的一元的"
         "白银价值", yu.index[0], yu.index[-1], F["bs_7553"][1])
    assert "In 1934 the official value of gold was changed" in sm["notes"]
    assert "From April 1933 the dollar was off gold" in load_snapshot("depressionworld_yuan_monthly")[1]["notes"]
    said("1933 年 4 月美元离开黄金，此后的美分不再是旧金元的美分", 1933, 4)
    ym_ = yuan_monthly()
    said("(b) 一元合多少美分，月平均，1929—1936 年", ym_.index[0][0], ym_.index[-1][0])
    t173 = int(re.search(r"Table (\d+)", sm["citation"]).group(1))
    m270 = int(re.search(r"series M (\d+)", sm["source"]).group(1))
    said("数据：《美国历史统计》（1975）系列 M 270；联邦储备委员会《银行与货币统计 1914—1941》表 173", 1975, m270, 1914, 1941,
         t173)


def models() -> None:
    """The key equations, and their arithmetic checked with numbers."""
    say("\\mathit{IP}_i=a+b\\,\\mathit{ER}_i+u_i.\\label{eq:depressionworld-es}")
    for c in (0.25, 1 / 3, 0.4):                       # the ceiling M = (G + F)/c falls by dR/c
        for G_, F_, dR in ((100, 0, 10), (40, 60, 8), (150, 0, 60)):
            chk(f"    eq:depressionworld-fetters: (G + F)/c - (G + F - dR)/c = dR/c ({c:.3f}, {G_}, {F_}, {dR})",
                (G_ + F_) / c - (G_ + F_ - dR) / c, dR / c, tol=1e-9)
    for pf, de in ((-0.105, 0.0), (-0.105, 0.223), (0.02, -0.05)):  # relative PPP: P = e P^f in logs
        P0, e0, Pf0 = 1.0, 1.0, 1.0
        e1, Pf1 = e0 * math.exp(de), Pf0 * math.exp(pf)
        chk(f"    eq:depressionworld-fetters: dln P = dln e + pi^f ({pf}, {de})", math.log((e1 * Pf1) / (e0 * Pf0)), de + pf,
            tol=1e-12)
    for ps0, ps1, pf in ((52.993, 28.700, 0.0), (28.700, 64.273, -0.05)):
        s0, s1 = 0.7553 * ps0, 0.7553 * ps1
        e0, e1 = 1 / s0, 1 / s1
        chk(f"    eq:depressionworld-silver: dln e = -dln p_s ({ps0}, {ps1})", math.log(e1 / e0), -math.log(ps1 / ps0),
            tol=1e-12)
        chk("    pi = dln e + pi^f = pi^f - dln p_s", math.log(e1 / e0) + pf, pf - math.log(ps1 / ps0), tol=1e-12)
    S = es()
    fit = es_fit()
    x, y = S.er1935.values, S.ip1935.values
    b = np.cov(x, y, bias=True)[0, 1] / np.var(x)
    chk("    eq:depressionworld-es: the OLS slope = cov/var", fit.params[1], b, tol=1e-10)
    chk("    the OLS line passes through the means", fit.params[0] + fit.params[1] * x.mean(), y.mean(), tol=1e-10)


def figures_data(F) -> None:
    """What the figures assert of their data."""
    B = boe()
    g = B.usd_per_gbp
    lo = g.loc[1931:1933].idxmin()
    before = g[[k for k in g.index if k < (1931, 9)]]
    assert lo == (1932, 11) and g[(1931, 8)] > 4.85 and before.max() < 4.89 and before.min() > 4.84   # at par
    r = bank_rate()
    assert r[date(1931, 9, 21)] == 6 and r.min() == 2
    early, late = exit_groups()
    assert len(early) == 14 and len(late) == 8
    E = exit_dates()
    assert set(E) <= set(maddison().index)
    R = ratio1935()
    dd = pd.Series({k: v[0] + (v[1] - 0.5) / 12 for k, v in E.items()})
    rho = np.corrcoef(dd[list(E)], R[list(E)])[0, 1]
    assert -0.6 < rho < -0.2, rho                                                 # a negative, loose relation
    S = silver()
    assert S.ny_silver_cents_per_oz.loc[1929:1936].idxmin() == 1932 and S.ny_silver_cents_per_oz.loc[1929:1936].idxmax() == 1935
    m = yuan_monthly()
    assert m.loc[1932:1936].idxmax() == (1935, 5) and m.loc[1935].loc[11] < 30


# ---------------------------------------------------------------------------------------------------
# 5. The book
# the life dates the chapter gives without a row of its own: the same words in an earlier chapter
LIVES = {"Winston Churchill，1874—1965": "ch27_interwar", "Franklin D. Roosevelt，1882—1945": "ch28_depressionus"}
# the life dates from rows of the snapshot: words -> (row, index of the birth year, index of the death year)
ROW_LIVES = {"Philip Snowden，1864—1937": ("hh_snowden", 0, 1),
             "John Maynard Keynes，1883—1946": ("keynes_life", 0, 1),
             "Herbert Hoover，1874—1964": ("bnf_hoover", 0, 1),
             "Ramsay MacDonald，1866—1937": ("loc_macdonald", 0, 1),
             "Sao-ke Alfred Sze，1877—1958": ("loc_sze", 0, 1),
             "H. H. Kung，1880—1967": ("loc_kung", 0, 1),
             "Cordell Hull，1871—1955": ("loc_hull", 0, 1),
             "Raúl Prebisch，1901—1986": ("bnf_prebisch", 0, 1)}
# what other chapters tell: (words of this chapter, chapter where it is told, words there)
EVENTS = [("六年以前，丘吉尔（Winston Churchill，1874—1965）就在这个下院宣布了回到黄金的决定（\\chref{ch:interwar}）",
           "ch27_interwar", "质询之后，财政大臣丘吉尔（Winston Churchill，1874—1965）提出预算"),
          ("汇率的对数变化等于两国通胀之差（式~\\eqref{eq:external-ppp}）", "ch05_external",
           "\\Delta\\ln e=\\pi-\\pi^{f}\\quad\\text{（相对）}.\\label{eq:external-ppp}"),
          ("那里的$e$是一单位外币值多少本币", "ch05_external", "本书一律用一单位外币折合多少本币，记作名义汇率 $e$"),
          ("货币$M$受黄金$G$与外汇$F$之和的约束，$c$是发行准备比率（式~\\eqref{eq:interwar-pyramid}）", "ch27_interwar",
           "R=G+F,\\qquad M\\le\\frac{R}{c}.\\label{eq:interwar-pyramid}"),
          ("逆差国却得独自收缩，这一点\\chref{ch:interwar}已经讲过", "ch27_interwar", "顺差国冲销流入的黄金，逆差国就得独自"),
          ("$G$没有增加，$F$却消失了，世界的储备随之缩小（\\exref{ex:interwar-pyramid}）", "ch27_interwar",
           "世界的储备少了 80，正是消失的外汇"),
          ("银行恐慌压低第一个比率，这是\\chref{ch:depressionus}的货币乘数", "ch28_depressionus", "货币乘数$m=M/H$"),
          ("美国的萧条，\\chref{ch:depressionus}已经讲过", "ch28_depressionus", "失业率从 3.2\\% 升到 24.9\\%"),
          ("美国 1933 年离开（\\chref{ch:depressionus}）", "ch28_depressionus", "可是美国要到这一年 4 月才离开黄金"),
          ("{1925 年按战前的旧平价回到黄金（\\chref{ch:interwar}）}", "ch27_interwar",
           "英国 & 1925 年 4 月 28 日宣布，5 月 13 日立法 & 战前平价，每英镑 4.8665 美元"),
          ("新平价约是战前金价值的五分之一（\\chref{ch:interwar}）", "ch27_interwar", "新平价，约为战前金价值的五分之一"),
          ("以黄金计的银价随市场涨落（\\chref{ch:periphery}）", "ch24_periphery", "银价从此往下走"),
          ("三者不能兼得，\\chref{ch:external}把它叫作不可能三角，它的理论在\\chref{ch:mundell}", "ch05_external",
           "这叫\\textbf{不可能三角}，是\\chref{ch:mundell}的主题")]
# the chapters this one hands on to (FORWARD_REFS rows opened by Chapter 29)
LATER = {"ch:alternatives": "ch30_alternatives", "ch:warfinance": "ch34_warfinance",
         "ch:brettonwoods": "ch36_brettonwoods", "ch:mundell": "ch37_mundell", "ch:euro": "ch60_euro"}


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
    assert "1881" in Q["loc_kung1881"] and "row loc_kung1881" in column("note")["loc_kung"]
    for here, ch, there in EVENTS:
        assert here in t, here
        assert there in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (ch, there)
    for label, ch in LATER.items():
        assert f"\\chref{{{label}}}" in t, label
        assert f"\\label{{{label}}}" in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (label, ch)
    # the old parity: Chapter 27's $4.8665, and the 1925 price of gold (£3 17s 10½d a standard ounce) against
    # Chapter 28's $20.67 a fine ounce
    assert "旧金价是每盎司 20.67 美元" in (ROOT / "zh" / "ch28_depressionus.tex").read_text(encoding="utf-8")
    chk("    the parity: $20.67 an ounce / £(3 17s 10.5d x 12/11) an ounce", 20.67 / gbp_per_fine_oz(F), parity(),
        tol=0.001)
    print(f"ok {len(LIVES) + len(ROW_LIVES)} life dates, {len(EVENTS)} statements of other chapters, {len(LATER)} later "
          "chapters")


def identities(F) -> None:
    """The table snapshots' identities, and the values read on page images against the totals they print."""
    G, A = goldexits(), averages()
    cols = [c for c in G.columns if c.startswith(("wpi_", "ip_"))]
    for grp, name in ((2, "average 1931"), (4, "average gold 1936")):
        gap = (G[G.group == grp][cols].mean() - A.loc[name, cols]).abs().max()
        chk(f"Table 2.2/2.4: the printed '{name}' row = the mean of its group (rounded to .01)", gap, 0, tol=0.0075)
    C = china()
    chk("Brandt and Sargent, Table 4: column 3 = column 1 - column 2, 1929-1936",
        (C.us_wpi_pct - C.usd_per_yuan_pct - C.predicted_shanghai_pct).abs().max(), 0, tol=0.051)
    assert "Column 3 of Table 4 is column 1 minus column 2" in load_snapshot("depressionworld_china")[1]["notes"]
    S, m = silver(), yuan_monthly()
    mean = m.groupby(level=0).mean()
    yrs = [y for y in mean.index if y != 1933]
    chk("Table 173: the year = the mean of its twelve months (not 1933: the new yuan from 10 April)",
        (mean[yrs] - S.yuan_cents_year[yrs]).abs().max(), 0, tol=0.1)
    assert "beginning April 10" in load_snapshot("depressionworld_yuan_monthly")[1]["notes"]
    fit = es_fit()
    a, b, _, ta, tb = F["es_eq"]
    chk("Figure 1 read on the page image: the refitted intercept = note 12's 153.9", fit.params[0], a, tol=0.5)
    chk("    the slope = note 12's -0.69", -fit.params[1], b, tol=0.015)
    chk("    the t-statistics = 10.06 and 3.51", [fit.tvalues[0], -fit.tvalues[1]], [ta, tb], tol=0.1)
    chk("    the adjusted R-squared = .56 (read on the page image)", fit.rsquared_adj, F["es_r2"][0], tol=0.01)
    S_ = es()
    chk("    France 100 and the United Kingdom 59 (the text) against the readings", [S_.er1935["France"],
        S_.er1935["United Kingdom"]], F["es_59"][:2], tol=1.0)
    # Chapter 27's snapshot of the same workbook overlaps 1929-1931
    old = load_snapshot("boe_millennium_interwar_monthly")[0].set_index(["year", "month"])
    B = boe()
    both = [k for k in B.index if k in old.index]
    assert len(both) == 36
    for c in ("usd_per_gbp", "sauerbeck_1867_77_100", "cost_of_living_jul1914_100"):
        chk(f"the Bank of England's {c}, 1929-1931: this snapshot = Chapter 27's", (B.loc[both, c] - old.loc[both, c]).abs()
            .max(), 0, tol=1e-9)
    R = ratio1935()
    E = exit_dates()
    early, late = exit_groups()
    assert len(E) == 22 and early == sorted(["ARG", "AUS", "AUT", "CAN", "DEU", "DNK", "FIN", "GBR", "GRC", "HUN", "JPN",
                                             "NOR", "NZL", "SWE"])
    bloc = ["CHE", "FRA", "NLD", "POL"]
    assert R[bloc].mean() < R[late].mean() < R[early].mean()


def witnesses(F, Q):
    """Second witnesses of statements of the text, and the bibliography block of the chapter."""
    N = column("note")
    chk("the Bank's credits: Snowden's £50 million at the old parity against the Federal Reserve's $125 million (half)",
        F["frb_125"][0] / (F["hc_50m"][0] * parity()), 0.5, tol=0.05)
    chk("the Bank's letter: $125 million of the credits (Hansard) = the Federal Reserve's $125 million (Bulletin)",
        F["hc_letter"][0], F["frb_125"][0])
    chk("£200 million lost (Snowden) = £200 million paid out (Keynes)", F["hc_200m"][0], F["k_200m"][0])
    chk("    = about $1 billion withdrawn from London (the Bulletin), at the old parity", F["hc_200m"][0] * parity(),
        F["frb_billion"][0], rel=0.05)
    chk("the suspension: the Act of 21 September (Royal Assent) = Keynes's editor's 21 September", F["gsa_date"],
        F["k_footnote"])
    chk("    = the Bulletin's Bank Rate change of 21 September", F["gsa_date"][0], F["frb_bankrate"][0])
    chk("    the British announcement on Sunday 20 September (the Bulletin), the day before", F["gsa_date"][0] -
        F["frb_sunday"][0], 1)
    chk("the Reichsbank's rate: the Bulletin's 15 per cent of 1 August, back to 10 on 12 August", [F["frb_aug1"][2],
        F["frb_aug12"][1]], [15, 15])
    chk("the decree of 3 November 1935 (Brandt and Sargent) and the reform effective 4 November (the Bulletin)",
        F["frb_nov4"][0] - F["bs_decree"][0], 1)
    chk("the yuan's silver: 0.7553 fine ounces = 0.8166 standard ounces x .925 (Brandt and Sargent)",
        F["bs_7553"][0] * 0.925, F["bs_7553"][1], tol=0.0005)
    chk("the standard yuan's 0.7553 oz against the market: 1929 and 1931 within two cents (BMS)",
        max(abs(0.7553 * silver().ny_silver_cents_per_oz[y] - silver().yuan_cents_year[y]) for y in (1929, 1931)) < 2, 1)
    assert "Wednesday 16 to Friday 18 September 1931" in N["hc_drain"]
    assert "the Creditanstalt" in N["hc_austria"]
    chk("Poland: left gold in April 1936 (Wolf) = exchange control of April 1936 (Bernanke and James)",
        ym(goldexits().loc["Poland"].exchange_control), (F["wolf_poland"][0], 4))
    # the licences and the bibliography
    m = meta()
    for words in ("'Contains Parliamentary information licensed under the Open Parliament Licence v3.0.'",
                  "'Contains public sector information licensed under the Open Government Licence v3.0.'",
                  "'Online by Gerhard Peters and John T. Woolley, The American Presidency Project'",
                  "'" + Q["b95_copyright"] + "'", "'" + Q["bs_copyright"] + "'", "'" + Q["fr92_copyright"] + "'",
                  "'Copyright © 2006-2025 | Central Bank of Argentina | All rights reserved'",
                  "'" + Q["wolf_copyright"] + "'", "Licence Ouverte (Open License)", "are public data",
                  "is CC BY-SA", "Keynes died in 1946"):
        assert words in m["license"], words
    assert Q["bcra_copyright"] == "Copyright © 2006-2025" and F["bcra_copyright"] == [2006, 2025]
    for name in ("depressionworld_silver", "depressionworld_yuan_monthly"):
        assert "Public domain" in load_snapshot(name)[1]["license"], name
    assert "CC BY 4.0" in maddison_meta()["license"] and "CONDITIONS UNDER WHICH ALL ORIGINAL PAPERS MUST BE CITED" in \
        maddison_meta()["license"]
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    start = bib.index("% ---- 第 29 章")
    following = re.search(r"^% ---- 第 \d+ 章", bib[start + 1:], re.MULTILINE)
    end = start + 1 + following.start() if following else bib.index("\\end{thebibliography}")
    block = bib[start:end]
    items = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", block)}
    for key in ("hansard1931", "hansardlords1931"):
        assert "Contains Parliamentary information licensed under the Open Parliament Licence v3.0." in items[key], key
    assert "Contains public sector information licensed under the Open Government Licence v3.0." in items["gsa1931"]
    assert "Online by Gerhard Peters and John T. Woolley, The American Presidency Project" in items["hoover1931"]
    assert Q["b95_copyright"] in items["bernanke1995"]
    assert Q["bs_copyright"] in items["brandt1989"] and Q["fr92_copyright"] in items["friedman1992"]
    assert "Copyright © 2006-2025 | Central Bank of Argentina | All rights reserved" in items["bcra2025"]
    assert Q["wolf_copyright"] in items["wolf2007"]
    for key in ("hoover1931", "frb1931", "frb1935", "frb1936", "stat1934", "frus1934", "frus1935", "bms1943",
                "census1975m"):
        assert "公有领域" in items[key], key
    for key in ("keynes1931", "bernanke1991", "eichengreen1984", "brandt1989", "friedman1992", "diaz1983", "bcra2025",
                "wolf2007"):
        assert "只引短句" in items[key], key
    wp, yr = F["b95_wp"]
    assert f"NBER Working Paper {wp:.0f}, August {yr:.0f}" in items["bernanke1995"]
    assert f"\\emph{{Journal of Money, Credit and Banking}}, 27(1): 1--28, {B95}." in items["bernanke1995"]
    assert f"NBER Working Paper {F['es_wp'][0]:.0f}, November {F['es_wp'][1]:.0f}" in items["eichengreen1984"]
    assert f"CEP Discussion Paper {F['wolf_dp'][0]:.0f}, November {F['wolf_dp'][1]:.0f}" in items["wolf2007"]
    assert f"{F['fr92_journal'][0]:.0f}({F['fr92_journal'][1]:.0f}): {F['fr92_journal'][2]:.0f}--" \
           f"{F['fr92_journal'][3]:.0f}" in items["friedman1992"]
    assert f"{F['da_volume'][1]:.0f}--{F['da_volume'][2]:.0f}" in items["diaz1983"]
    assert "48 Stat. 1178" in items["stat1934"] and f"Public No. {F['spa_public'][0]:.0f}" in items["stat1934"]
    assert "Licence Ouverte" in items["bnf29"] and "id.loc.gov" in items["loc29"]
    d, y, vol, c0, c1 = F["hc_title"]
    assert Q["hc_title"].startswith(f"HC Deb {d:.0f} September {y:.0f} vol {vol:.0f} cc{c0:.0f}-")
    assert f"HC Deb {d:.0f} September {y:.0f}, vol. {vol:.0f}, cc. {c0:.0f}--" in items["hansard1931"]
    mm = maddison_meta()
    used = sorted(set(exit_dates()) | {"CHL", "BRA", "COL"})
    for iso in used:                                                             # the original sources, as required
        for s in mm["sources_by_country"][iso]:
            head = s.split(":")[1].strip()[:25].replace("&", "\\&").replace("$", "\\$")
            assert head in items["mpd29src"], (iso, head)
    assert f"这 {len(used)} 个经济体" in items["mpd29src"]
    allitems = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", bib)}
    assert "第 29 章用表 M15" in allitems["boe2017"] and "boe\\_millennium\\_gb29.py" in allitems["boe2017"]
    assert "第 29 章用 28 个经济体" in allitems["mpd2023"]
    keys = set(allitems)
    cited = {k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", tex_text()) for k in c.split(",")}
    assert cited <= keys, sorted(cited - keys)
    assert set(items) <= cited, sorted(set(items) - cited)
    print(f"ok {len(cited)} works cited, {len(items)} of them in the bibliography block of Chapter 29")


def counts() -> None:
    """The editor's limits: “不能” at most about a dozen; no cited author as the subject of a sentence outside the
    史料说明."""
    t = tex_text()
    main = re.sub(r"\\begin\{deeper\}\[史料说明\].*?\\end\{deeper\}", "", t, flags=re.DOTALL)
    n = t.count("不能")
    print(f"ok “不能” {n} times")
    assert n <= 12, n
    verbs = "认为|写道|说|指出|记述|估计|承认|报道|记载|提到|列出|给出|发现|统计|算出|早有|看法|有类似"
    names = ("Bernanke|James|Eichengreen|Sachs|Brandt|Sargent|Friedman|Schwartz|Wolf|Díaz|Alejandro|Choudhri|Kochin|"
             "Hsiao|Yeh|Silber|Tamagna|Rawski|Maddison")
    subj = re.findall(r"(?:^|[。；：，\n])\s*(?:" + names + r")(?:（\d{4}）)?(?:" + verbs + ")", main)
    assert not subj, subj
    subj2 = re.findall(r"(?:^|[。；：，\n])\s*(?:" + names + r")(?: 与 (?:" + names + r"))?(?:（\d{4}）)?(?:" + verbs + ")",
                       main)
    assert not subj2, subj2
    narrative = re.sub(r"“[^”]*”", "", t)                                       # the quotations render the sources
    for bad in ("这一节回答", "不是因为", "而是", "详见", "\\textsc", "\\underline", "\\clearpage"):
        assert bad not in narrative, bad
    assert not re.search(r"(?<![意看])见\\(?:chref|secref|figref|tabref|exref|eqref)", t)


def main() -> None:
    df = _rows()
    F, Y, Q = facts(), years(), quotes()
    check_readings(df)
    check_text(df)
    identities(F)
    guide(F, Y, Q)
    opening(F, Y, Q)
    world(F, Y, Q)
    fetters(F, Y, Q)
    ex_fetters(F, Y, Q)
    ex_keynes(F, Y, Q)
    crisis1931(F, Y, Q)
    compare1931(F, Y, Q)
    exits(F, Y, Q)
    exits_table(F, Y, Q)
    goldbloc(F, Y, Q)
    compare_france(F, Y, Q)
    es_section(F, Y, Q)
    ex_es(F, Y, Q)
    es_limits(F, Y, Q)
    debate(F, Y, Q)
    silver_section(F, Y, Q)
    ex_silver(F, Y, Q)
    casebox(F, Y, Q)
    china_debate(F, Y, Q)
    compare_china(F, Y, Q)
    latam(F, Y, Q)
    check_section(F, Y, Q)
    deeper(F, Y, Q)
    models()
    frames(F, Y, Q)
    figures_data(F)
    legacy(F, Y, Q)
    takeaways(F, Y)
    selfcheck(F, Y)
    ending(F, Y, Q)
    book(F, Q)
    witnesses(F, Q)
    counts()
    coverage()
    anchors("zh/ch29_depressionworld.tex", df["id"], script=Path(__file__))


if __name__ == "__main__":
    main()
