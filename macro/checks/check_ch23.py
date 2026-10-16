"""Chapter 23 (金本位、挤兑与最后贷款人): every number and every quotation in zh/ch23_goldstandard.tex.

    python3 checks/check_ch23.py

Inputs:
  goldstandard_facts                   quotations of Hansard (11 and 17 May 1866) and its people pages, the Bank
                                       Charter Act 1844 (legislation.gov.uk), Bagehot (1873, and the 1874 edition),
                                       Andreades (1909), the NBER volume of Bordo and Schwartz (1984: Bordo with
                                       White's discussion, Dutton with Moggridge's comment, McGouldrick, Dornbusch
                                       and Frenkel), the National Monetary Commission's Reichsbank (1910) and Sprague
                                       (1910), the Federal Reserve Act (1913), the Gold Standard Act (1900, in
                                       Huntington and Mawhinney 1910), Bryan (1896), Menger (1892), Knapp (1924),
                                       Fisher (1896), Rockoff (2009), Tacitus (Gordon) and Wikisource's author pages
                                       (checked by data/fetch/verify_web_quotes.py)
  boe_millennium_weekly_1844_1914      Bank of England, A Millennium of Macroeconomic Data: the weekly returns of the
                                       Issue Department (sheet W1) and the Banking Department (sheet W2)
  boe_millennium_bank_rate_1844_1914   the days on which Bank Rate changed (sheet D1)
  boe_millennium_prices_1821_1913      UK consumer and wholesale prices and the US CPI (sheet A47)
The figure module figsrc/fig_ch23.py imports the functions defined here.

What is checked here:
  1. readings   every number of the value column of goldstandard_facts is read from its quotation (digits,
                English number words and fractions) or, where the source's own words are given in the note, from
                the note
  2. the text   every “…” in the chapter is the chapter's Chinese rendering of a quotation (TRANSLATIONS:
                rendering -> row or rows) or a term of the text (ALLOW)
  3. numbers    every number of the text, section by section, with quoted()
  4. anchors    the paraphrase anchors `% 据: ...` name rows of goldstandard_facts

Models (the chapter's key equations):
    the two departments   N = F + G,  R_n = N - C = F + G - C                                    (eq:gold-issue)
    Goschen's arithmetic  (i - i^f) tau/12 >= c,  i.e.  i - i^f >= 12 c / tau                  (eq:gold-goschen)
                          (i London's rate, i^f the foreign rate, as in Appendix B and Chapter 5)
    the rules of the game Bloomfield (1959): a year complies when the central bank's international and domestic
                          assets change in the same direction. International = gold and silver of the Issue
                          Department + coin of the Banking Department; domestic = government securities and
                          'discounts, advances and other securities' of the Banking Department + the fiduciary
                          issue; changes from one year-end (the last return of the year) to the next, or of the
                          annual means of the weekly returns
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

TEX = ROOT / "zh" / "ch23_goldstandard.tex"
WAN = 1e4                                  # 万
YI = 1e8                                   # 亿
MILL = 1e6

# The three Treasury letters (Hansard; Andreades; Evans via Chapter 22) and the window of the figure and table
LETTERS = {1847: "1847-10-25", 1857: "1857-11-12", 1866: "1866-05-11"}
WINDOW = 10                                # weeks before and after the letter
# Teaching inputs stated in the text
GOSCHEN = dict(c=0.5, tau=3, tau_short=1)  # ex:gold-goschen (1): c and tau are Goschen's own example
DEBT_I = 6.0                               # ex:gold-debt (3): a nominal rate of 6%, a teaching assumption
SC2 = dict(c=0.25, tau=2, paris=3.0)       # self-check 2
WEEKS = 52                                 # self-check 5: a week is 1/52 of the yearly tax


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
    df, meta = load_snapshot("goldstandard_facts", dtype=str, keep_default_na=False)
    assert 23 in meta["used_in"]
    assert df["id"].is_unique
    return df


def num(x: str) -> float:
    """'5', '1/3', '25.8'."""
    if "/" in x:
        a, b = x.split("/")
        return float(a) / float(b)
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


def weekly() -> pd.DataFrame:
    """The weekly returns, 1844-1914, £ m, indexed by the date of the return."""
    df, m = load_snapshot("boe_millennium_weekly_1844_1914", parse_dates=["date"])
    assert 23 in m["used_in"]
    assert "Bank of England" in m["license"]
    w = df.set_index("date")
    assert w.index.is_monotonic_increasing and w.index.is_unique
    return w


def bank_rate() -> pd.Series:
    """Bank Rate on 2 January 1844 and on each day it changed, 1844-1914."""
    df, m = load_snapshot("boe_millennium_bank_rate_1844_1914", parse_dates=["date"])
    assert 23 in m["used_in"]
    s = df.set_index("date").bank_rate
    assert s.index.is_monotonic_increasing and (s.diff().dropna() != 0).all()
    return s


def prices() -> pd.DataFrame:
    """Annual price indices, 1821-1913: UK CPI (2015 = 100), UK wholesale (2010 = 100), US CPI (1982-84 = 100)."""
    df, m = load_snapshot("boe_millennium_prices_1821_1913")
    assert 23 in m["used_in"]
    return df.set_index("year")


# ---------------------------------------------------------------------------------------------------
# The arithmetic of the chapter
def rate_on(s: pd.Series, day: str) -> float:
    """Bank Rate in force on a day."""
    return float(s.loc[:pd.Timestamp(day)].iloc[-1])


def departments(w: pd.DataFrame, day: str) -> dict:
    """eq:gold-issue on one weekly return: F, G (coin and bullion of the Issue Department), N = F + G, C, R_n and the
    Banking Department's reserve R (notes + coin)."""
    r = w.loc[pd.Timestamp(day)]
    F, G, C, Rn = r.fiduciary_issue, r.issue_coin_bullion, r.notes_circulation, r.notes_in_banking_dept
    return dict(F=F, G=G, N=F + G, C=C, Rn=Rn, R=r.bd_reserve, coin=r.bd_coin, loans=r.bd_other_securities,
                govt=r.bd_govt_securities, other_dep=r.other_deposits, bankers=r.bankers_deposits,
                gold=r.issue_gold, silver=r.issue_silver)


def goschen(c: float, tau: float) -> float:
    """eq:gold-goschen: the least yearly difference of interest (points) that pays the cost c (%) of moving gold
    for a bill of tau months."""
    return 12 * c / tau


def assets(w: pd.DataFrame) -> pd.DataFrame:
    """International and domestic assets of the Bank of England (£ m), weekly."""
    out = pd.DataFrame(index=w.index)
    out["intl"] = w.issue_gold + w.issue_silver.fillna(0) + w.bd_coin
    out["dom"] = w.bd_govt_securities + w.bd_other_securities + w.fiduciary_issue
    return out


def changes(w: pd.DataFrame, how: str = "end", first: int = 1880, last: int = 1913) -> pd.DataFrame:
    """Yearly changes of the two classes of assets: from year-end to year-end ('end', the last return of each year)
    or of the annual means ('mean')."""
    a = assets(w)
    g = a.groupby(a.index.year)
    lv = g.last() if how == "end" else g.mean()
    return lv.loc[first - 1:last].diff().dropna()


def classify(d: pd.DataFrame) -> pd.Series:
    """Bloomfield's rule: 'comply' when the two changes have the same sign, 'violate' when opposite, else 'none'."""
    s = np.sign(d.intl) * np.sign(d.dom)
    return s.map({1.0: "comply", -1.0: "violate"}).fillna("none")


def shares(d: pd.DataFrame) -> dict:
    c = classify(d).value_counts()
    n = len(d)
    return {k: int(c.get(k, 0)) for k in ("comply", "violate", "none")} | {"n": n}


def aligned(w: pd.DataFrame, col: str, letter: str, weeks: int = WINDOW) -> pd.Series:
    """A weekly series around a Treasury letter, indexed by weeks since the letter (the return of the letter's week
    or the first after it is week 0)."""
    t0 = pd.Timestamp(letter)
    s = w[col].loc[t0 - pd.Timedelta(weeks=weeks + 1): t0 + pd.Timedelta(weeks=weeks + 1)]
    x = (s.index - t0).days / 7.0
    keep = (x >= -weeks) & (x <= weeks)
    return pd.Series(s.values[keep], index=x[keep])


def rate_aligned(D: pd.Series, letter: str, weeks: int = WINDOW) -> pd.Series:
    """Bank Rate as a step function around a letter: the rate in force at the start of the window and every change
    inside it, indexed by weeks since the letter."""
    t0 = pd.Timestamp(letter)
    a, b = t0 - pd.Timedelta(weeks=weeks), t0 + pd.Timedelta(weeks=weeks)
    s = pd.concat([pd.Series([rate_on(D, str(a.date()))], index=[a]), D.loc[a:b]])
    s = s[~s.index.duplicated(keep="last")]
    s = pd.concat([s, pd.Series([s.iloc[-1]], index=[b])])
    return pd.Series(s.values, index=(s.index - t0).days / 7.0)


def window_min(w: pd.DataFrame, col: str, letter: str) -> tuple[pd.Timestamp, float]:
    t0 = pd.Timestamp(letter)
    s = w[col].loc[t0 - pd.Timedelta(weeks=WINDOW): t0 + pd.Timedelta(weeks=WINDOW)]
    return s.idxmin(), float(s.min())


def rises(D: pd.Series, a: int, b: int) -> pd.Series:
    """The sizes of the rises of Bank Rate in the years a..b (points) and how often each occurred."""
    ch = D.diff().dropna()
    up = ch[(ch > 0) & (ch.index.year >= a) & (ch.index.year <= b)]
    return up.round(2).value_counts()


def truncated(x: float) -> float:
    """£ m truncated to the thousand pounds, as Bagehot prints the returns."""
    return math.floor(x * 1000 + 1e-9) / 1000


# ---------------------------------------------------------------------------------------------------
# 1. Readings of the numbers
SMALL = {"a": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
         "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
         "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
SCALE = {"thousand": 1e3, "million": 1e6}
ORDINAL = {"half": 2, "third": 3, "thirds": 3, "fourth": 4, "tenths": 10}


def cardinal(s: str) -> float:
    """An English cardinal: 'forty-three', 'Fourteen million', 'one hundred and fifty million', 'a hundred thousand'."""
    total, cur = 0.0, 0.0
    for w in s.lower().replace("-", " ").split():
        if w == "and":
            continue
        if w in SMALL:
            cur += SMALL[w]
        elif w == "hundred":
            cur *= 100
        elif w in SCALE:
            total += cur * SCALE[w]
            cur = 0.0
        else:
            raise ValueError(w)
    return total + cur


def fraction(s: str) -> float:
    """'One Fourth', 'Two Thirds', 'one-third', 'nine-tenths', 'one-half'."""
    a, b = s.lower().replace("-", " ").split()
    return float(Fraction(int(cardinal(a)), ORDINAL[b]))


def figure(s: str) -> float:
    return float(s.replace(",", ""))


def read(phrase: str, how: str) -> list[float]:
    if how == "num":
        return [figure(phrase)]
    if how == "en":
        return [cardinal(phrase)]
    if how == "frac":
        return [fraction(phrase)]
    if how == "slash":                        # '1/2'
        a, b = phrase.split("/")
        return [float(a) / float(b)]
    if how == "mixed":                        # 'thirty-two and one-half', 'twenty-five and eight-tenths'
        whole, part = phrase.rsplit(" and ", 1)
        return [cardinal(whole) + fraction(part)]
    if how == "double":
        return [2.0]
    raise ValueError(how)


FIGURES = re.compile(r"\d[\d,]*(?:\.\d+)?")
EN, NUM, NOTE = "en", "num", "note"
# id -> [(phrase, how[, NOTE])], in order. A third element NOTE means the phrase is read from the note column (the
# source's own words, which the OCR garbles or which fall outside the quotation). Rows not listed are read with all
# the figures of the quotation.
READINGS = {
    "hq_ref": [("11", NUM), ("1866", NUM), ("183", NUM)],               # the column numbers are not values
    "hs_ref": [("11", NUM), ("1866", NUM), ("183", NUM)],
    "hm_ref": [("17", NUM), ("1866", NUM), ("183", NUM)],
    "hp_goschen": [("1831", NUM), ("1907", NUM)],
    "ac_14m": [("Fourteen million", EN)],
    "ac_silver": [("One Fourth", "frac")],
    "ac_price": [("Three", EN), ("Seventeen", EN), ("Nine", EN)],       # 'Ninepence'
    "ac_twothirds": [("Two Thirds", "frac")],
    "bg_goschen": [("1/2", "slash"), ("2", NUM), ("1/2", "slash")],
    "bg_steps1860": [("1860", NUM), ("1/2", "slash")],
    "bg_three_panics": [("1844", NUM), ("1847", NUM), ("1857", NUM), ("1866", NUM)],
    "an_refused": [("400,000", NUM, NOTE)],
    "an_929": [("929,000", NUM, NOTE)],
    "an_43days": [("forty-three", EN)],
    "an_12days": [("twelve", EN)],
    "df_peel": [("1847", NUM, NOTE)],
    "rb_raise": [("5", NUM, NOTE)],
    "rb_third": [("one-third", "frac")],
    "rb_1881": [("1881", NUM), ("1885", NUM), ("five", EN)],
    "rb_1886": [("ten", EN), ("six", EN), ("1890", NUM)],
    "rb_1891": [("four", EN)],
    "sp_run3h": [("three", EN), ("8,000,000", NUM)],
    "sp_110m": [("10,800,000", NUM), ("60,700,000", NUM), ("38,900,000", NUM), ("110,000,000", NUM)],
    "fr_reserve": [("thirty-five", EN), ("forty", EN)],
    "fr_tax": [("one", EN), ("thirty-two and one-half", "mixed")],
    "fr_suspend": [("thirty", EN)],
    "gs_grains": [("twenty-five and eight-tenths", "mixed", NOTE), ("nine-tenths", "frac", NOTE)],
    "gs_reserve": [("one hundred and fifty million", EN)],
    "br_votes": [("6,511,073", NUM)],                                   # 'my vote in 1896 was ...'
    "rk_notice": [("2009", NUM), ("two", EN)],
    "ta_loan": [("a hundred thousand", EN)],
    "ta_terms": [("three", EN), ("double", "double")],
    "ta_small": [("a thousand", EN), ("8", NUM, NOTE), ("6", NUM, NOTE), ("8", NUM, NOTE)],
    "ta_great": [("a thousand", EN), ("8333", NUM, NOTE)],
}


def check_readings(df: pd.DataFrame) -> None:
    n = 0
    for r in df.itertuples():
        if not r.value:
            assert r.id not in READINGS, r.id
            continue
        vals = [num(x) for x in r.value.split(";")]
        texts = {"quote": " ".join(r.quote.split()), NOTE: " ".join(r.note.split())}
        if r.id in READINGS:
            got, pos = [], {"quote": 0, NOTE: 0}
            for item in READINGS[r.id]:
                phrase, how = item[0], item[1]
                where = item[2] if len(item) > 2 else "quote"
                k = texts[where].find(phrase, pos[where])
                assert k >= 0, f"{r.id}: {phrase!r} not found (in order) in the {where}"
                pos[where] = k + len(phrase)
                got += read(phrase, how)
        else:
            got = [figure(x) for x in FIGURES.findall(texts["quote"])]
        assert [round(g, 9) for g in got] == [round(v, 9) for v in vals], f"{r.id}: read {got}, value column {vals}"
        n += 1
    quoted("rows with values, each read from its quotation (or its note)", n, 102)


# ---------------------------------------------------------------------------------------------------
# 2. Every “…” of the text against the snapshot
# terms of the text and names of columns, which are not quotations of the snapshot
ALLOW = {
    "游戏规则",                 # the term (rows du_phrase, mo_kindersley)
    "弄垮",                     # a word of the quotation of row bg_letgo, explained in the text
    "违反",                     # a class of Bloomfield's count (ex:gold-rules)
    "贴现、放款与其他证券",     # the heading of sheet W2 ('Discounts, advances and other securities')
    "私人证券",                 # Bagehot's heading of his table (note of row bg_loans1847)
    "据说",                     # Andreades's 'It is said' (note of row an_cheques)
}
# the chapter's Chinese renderings of the quotations: rendering -> row (or rows)
TRANSLATIONS = {
    # opening
    "在人们的记忆里找不到先例": "hq_parallel",
    "英格兰最受信任的私人商号": "bg_overend",
    "正当商业的需要": "hs_legitimate",
    "不要犹豫": "hs_issue",
    "明天早上我开两张支票，就能叫你们关门。": "an_cheques",
    "明天早上我开两张支票": "an_cheques",
    # sec:gold-world
    "确信钱借得到，就没有人再想要钱了。": "an_magical",
    "它 1844 年才设立，此后已经失灵三次。": "bg_failed3",
    # sec:gold-1844
    "银行券的流通额随英格兰银行持有的黄金一对一地变化": "bo_onefor1",
    "自然的制度，也就是政府对银行业放任不管时会自发产生的制度，是许多大小相等或相差不大的银行。": "bg_natural_ii",
    "我提议保留这个制度，因为我十分确信，提议改变它没有任何用处。": "bg_retain",
    "出现恐慌，这种状态法律无法预见，也无法预防，又讲不通道理，政府就必须承担起一种权力，防止可能出现的后果。": "df_peel",
    # sec:gold-bagehot
    "恐慌就是一种神经痛，按科学的规矩，不能让它挨饿。": "bg_neuralgia",
    "以很高的利率放出很多的贷款，是治疗货币市场这种最坏的病的最好办法": ("bg_remedy", "b74_remedy"),
    "只要让人觉得钱借不到，或者出什么价都借不到，惊慌就会变成恐慌，恐慌又会变成疯狂。": "bg_madness",
    "钱虽然贵，还是借得到": "bg_impression",
    "用尽了一切可能的办法，用了从来没有用过的方式": "bg_harman",
    "第一，这些贷款只能按很高的利率放出。这对不合理的胆怯是一笔重罚。": ("bg_first", "b74_first"),
    "第二，按这个利率，凡是好的银行抵押品都要接受，公众要借多少就借多少。": ("bg_second", "b74_second"),
    "新的借款人没有别的放款人。": "bg_nolender",
    "几乎总是": "bg_steps1860",
    "降到了零": "bg_13m",
    "奥弗伦家 1866 年弄垮了英格兰银行，是因为它倒了；1857 年弄垮了英格兰银行，是因为没有让它倒。": "bg_letgo",
    # sec:gold-rules
    "金本位游戏的规则": "du_phrase",                          # in the deeper box
    "你这样处理自己的事务，使你既不会大量得到黄金，也不会大量失去黄金": "mo_meaning",
    "英格兰银行按金本位游戏的一切规则，不得不紧缩信用": "ke_game",
    "一个被管理的、而不是近乎自动的体系": "bo_managed",
    "轻声的否定": "du_softno",
    "令人困惑的是商品流动之快，几乎是同时的。黄金流动与物价变化这个本该有的中间阶段很难看出来，即使有，也极其短暂。":
        "bo_taussig",
    "不过是世界乐队里的第二小提琴手，甚至只是敲三角铁的": "bo_violinist",
    "钱不会自己管理自己，伦巴第街却有大量的钱要管。": "bg_manage",
    # sec:gold-state
    "不是偶然，不是国家强制的结果，也不是商人自愿约定的结果": "me_noaccident",
    "是一种社会的制度，而不是国家的制度": "me_social",
    "货币是法律的创造物。所以，一种货币理论必须研究法律的历史。": "kn_creature",
    "复本位之争的核心问题，是债务人与债权人之间的公正。": "fi_opening",
    "你们不能把这顶荆棘的冠冕压在劳动者的额头上，你们不能把人类钉死在黄金的十字架上。": "br_cross",
    # sec:gold-test
    "英格兰银行并不是要把人人要的都给人人，它仍要遵守它一向遵循的审慎规则": "hm_caution",
    "对英格兰的挤兑": "an_runengland",
    "1866 年以后，英格兰再没有发生银行危机。": "rk_schwartz",
    "一群银行很像一排砖，倒了一块，就危及其余的。": "sp_bricks",
    "整个信用结构的基础已经受到威胁": "sp_endangered",
    "偶像，健全银行政策的一切准则都盲目地为它牺牲": "sp_fetich",
    "有弹性的通货": "fr_preamble",
    # sec:gold-legacy and the ending
    "必须放手借出": ("b74_lendfreely",),
    "需要这些措施的，总是商业上较弱的国家。": "kn_weaker",
}
# the renderings that are kept literally close to the source: words of the source that must be there
KEYWORDS = {
    "hq_parallel": ["without parallel in the recollection"],
    "bg_overend": ["the most trusted private firm in England"],
    "hs_legitimate": ["wants of legitimate commerce"],
    "hs_issue": ["should not hesitate"],
    "an_cheques": ["a couple of cheques to-morrow morning", "shut you up"],
    "an_magical": ["certainty that money could be got", "all desire to have it"],
    "bg_failed3": ["only created in 1844", "failed three times"],
    "bo_onefor1": ["one-for-one", "holdings of gold"],
    "bg_natural_ii": ["natural system", "let banking alone", "equal or not altogether unequal size"],
    "bg_retain": ["I propose to retain this system", "of no manner of use"],
    "df_peel": ["cannot be foreseen or provided against by law", "cannot be reasoned with", "must assume a power"],
    "bg_neuralgia": ["species of neuralgia", "must not starve it"],
    "bg_remedy": ["Very large loans at very high rates", "worst malady of the money market"],
    "b74_remedy": ["Very large loans at very high rates"],
    "bg_madness": ["money is not to be had", "panic to madness"],
    "bg_impression": ["though money may be dear, still money is to be had"],
    "bg_harman": ["every possible means", "never adopted before"],
    "bg_first": ["very high rate of interest", "heavy fine on unreasonable timidity"],
    "b74_first": ["very high rate of interest"],
    "bg_second": ["all good banking securities", "as largely as the public ask for them"],
    "b74_second": ["all good banking securities", "as largely as the public ask for them"],
    "bg_nolender": ["no other lender to new borrowers"],
    "bg_steps1860": ["almost always"],
    "bg_13m": ["went down to nothing"],
    "du_phrase": ["rules of the gold standard game"],
    "bg_letgo": ["because it went", "because it was not let go"],
    "mo_meaning": ["neither to gain nor to lose large quantities of gold"],
    "ke_game": ["compelled to curtail credit", "rules of the gold standard game"],
    "bo_managed": ["managed and not a quasi-automatic"],
    "du_softno": ["soft-spoken no"],
    "bo_taussig": ["rapidity, almost simultaneity", "extremely short"],
    "bo_violinist": ["second violinist", "triangle player"],
    "bg_manage": ["Money will not manage itself"],
    "me_noaccident": ["No accident", "state compulsion", "voluntary conven"],
    "me_social": ["social, and not a state"],
    "kn_creature": ["creature of law", "legal history"],
    "fi_opening": ["bimetallic controversy", "justice between debtor and creditor"],
    "br_cross": ["crown of thorns", "cross of gold"],
    "hm_caution": ["not to give to everybody everything that was asked", "prudent rules of caution"],
    "an_runengland": ["a run upon England"],
    "rk_schwartz": ["no banking crises in England after 1866"],
    "sp_bricks": ["row of bricks"],
    "sp_endangered": ["entire credit structure was endangered"],
    "sp_fetich": ["fetich", "blindly sacrificed"],
    "fr_preamble": ["elastic currency"],
    "b74_lendfreely": ["must lend freely"],
    "kn_weaker": ["commercially weaker State"],
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
    stale = (set(ALLOW) | set(TRANSLATIONS)) - used
    assert not stale, f"listed but not in the text: {sorted(stale)}"
    for rid, words in KEYWORDS.items():
        for w in words:
            assert w in Q[rid], f"{rid}: {w!r} not in the quotation"
    N = column("note")
    assert "private securities" in N["bg_loans1847"]                      # “私人证券”
    assert "It is said" in N["an_cheques"]                                 # “据说”
    print(f"ok {n} quotations of the text found in the snapshot (or listed as exceptions)")


# ---------------------------------------------------------------------------------------------------
# 3. Numbers, section by section
def opening(F, Y, Q, W):
    chk("11 May 1866 was a Friday (weekday 4)", date(1866, 5, 11).weekday(), 4)
    chk("the question and the answer: 11 May 1866", F["hq_ref"][:2], [11, 1866])
    chk("    the statement in the evening", F["hs_ref"][:2], [11, 1866])
    chk("Disraeli 1804-1881", F["hp_disraeli"], [1804, 1881])
    chk("Gladstone 1809-1898", F["hp_gladstone"], [1809, 1898])
    a, b = F["hp_gladstone_cx"]
    assert a <= 1866 <= b and "Chancellor of the Exchequer" in Q["hp_gladstone_cx"]       # 财政大臣
    chk("the Act of 1844", F["hq_noauth"], [1844])
    assert "Towards evening of May" in column("note")["an_news"]                           # 前一天傍晚
    assert "bill brokers" in Q["bg_countydeposits"] and "Overends" in Q["bg_1857brokers"]   # 票据经纪商
    chk("loans and discounts that day: more than (万英镑)", F["hs_4m"][0] / WAN, 400)
    chk("the reserve: nearly ... to a little over (万英镑)", [x / WAN for x in F["hs_reserve"]], [600, 300])
    assert "approaching" in Q["hs_reserve"] and "a little exceeding" in Q["hs_reserve"]
    chk("the letters of 1847 and 1857", F["hs_letter"], [1847, 1857])
    assert "First Minister" in Q["hm_signed"] and "to-morrow" in Q["hs_tomorrow"]
    assert "not announced before midnight" in Q["an_midnight"]
    assert "lodged their reserve with it" in Q["bg_lodged"]
    chk("Lombard Street, seven years later", Y["bg_limited"] - 1866, 7)
    # the 1857 letter is the one of the three that took the fiduciary issue beyond the limit
    f = W.fiduciary_issue
    over = {y: bool((f.loc[f"{y}"] > f.loc[:f"{y - 1}"].iloc[-1] + 1e-9).any() and
                    (f.loc[f"{y}"].diff().fillna(0) < -1e-9).any()) for y in LETTERS}
    assert over == {1847: False, 1857: True, 1866: False}, over


def world(F, Y, Q, W, D):
    assert "freely coined" in Q["bo_freely"] and "import or export of gold" in Q["bo_freely"]
    assert "Cunliffe report" in column("juan")["bo_freely"]                       # 坎利夫委员会的报告
    chk("Germany: 4 December 1871; 9 July 1873", F["rb_1871"] + F["rb_1873"], [4, 1871, 9, 1873])
    chk("the US: March 1900", F["rb_us1900"], [1900])
    assert Y["rb_1871"] > 1866 and F["rb_us1900"][0] > 1866                    # 1866 年，德国与美国都还没有
    chk("fiduciary issue at most (万英镑)", F["ac_14m"][0] / WAN, 1400)
    chk("silver: at most a quarter of the gold", F["ac_silver"], [0.25])
    chk("£3 17s 9d an ounce", F["ac_price"], [3, 17, 9])
    chk("two-thirds of the lapsed issues", F["ac_twothirds"], [2 / 3])
    f = W.fiduciary_issue
    chk("the fiduciary issue in May 1866 (万英镑)", f.loc["1866-05"].unique() * 100, [1500])
    g = f.loc["1858":]
    assert g[g >= 15.0 - 1e-9].index[0] == pd.Timestamp("1866-02-21")             # 到 1866 年
    chk("    from 1844 to 1866 it rose by (万英镑)", (f.loc["1866-05"].iloc[0] - f.iloc[0]) * 100, 100)
    assert "weekly" in Q["ac_weekly"]
    chk("the three panics", F["bg_three_panics"], [1844, 1847, 1857, 1866])
    chk("the letter of 25 October 1847", F["an_oct25"], [25, 1847])
    chk("    the rate not less than (%)", F["an_8pct"], [8])
    assert "profits" in Q["an_profits"]
    chk("the letters sufficed in", F["an_letters_enough"], [1847, 1866])
    # 1857: the only excess
    s = f.loc["1857-01":"1858-01"]
    hi = s[s > s.iloc[0] + 1e-9]
    chk("1857: the fiduciary issue before (万英镑)", s.iloc[0] * 100, 1447.5)
    chk("    raised to (万英镑)", hi.max() * 100, 1647.5)
    chk("    from 18 November", [hi.index[0].month, hi.index[0].day], [11, 18])
    chk("    to 23 December", [hi.index[-1].month, hi.index[-1].day], [12, 23])
    chk("Andreades: suspended in fact (days); in law (days)", F["an_43days"] + F["an_12days"], [43, 12])
    assert "the Act of 1844" not in Q["bg_failed3"] and "created in 1844" in Q["bg_failed3"]


def sec1844(F, Y, Q, W):
    assert "one-for-one" in Q["bo_onefor1"] and "pure specie standard" in Q["bo_mixed"]
    assert "external drain" in Q["bo_drains"] and "internal drain" in Q["bo_drains"]
    # eq:gold-issue holds on every weekly return
    gap = (W.fiduciary_issue + W.issue_coin_bullion - W.notes_circulation - W.notes_in_banking_dept).abs()
    chk("eq:gold-issue on every return, largest gap (£ m)", gap.max(), 0, tol=0.01)
    # ex:gold-week1866 and tab:gold-week1866
    a, b = departments(W, "1866-05-09"), departments(W, "1866-05-16")
    assert math.isnan(a["silver"]) and math.isnan(b["silver"])                  # 这时发行部已经没有白银
    for k, x, y in [("F", 15.00, 15.00), ("G", 12.29, 11.85), ("N", 27.29, 26.85), ("C", 22.34, 26.12),
                    ("Rn", 4.95, 0.73), ("R", 5.81, 1.20), ("loans", 20.84, 30.94), ("govt", 10.89, 10.84),
                    ("other_dep", 13.52, 18.62)]:
        pct(f"tab:gold-week1866 {k}, 9 May", a[k], x, 2)
        pct(f"    {k}, 16 May", b[k], y, 2)
    pct("    bankers' deposits, 9 May (5.085, printed 5.09)", a["bankers"], 5.09, 2)
    pct("    bankers' deposits, 16 May", b["bankers"], 7.92, 2)
    for d in (a, b):
        chk("    F + G - C = R_n", d["F"] + d["G"] - d["C"], d["Rn"], tol=1e-6)
    pct("(1) 15.00 + 12.29 - 22.34", 15.00 + 12.29 - 22.34, 4.95, 2)
    pct("    15.00 + 11.85 - 26.12", 15.00 + 11.85 - 26.12, 0.73, 2)
    dRn, dG, dC = b["Rn"] - a["Rn"], b["G"] - a["G"], b["C"] - a["C"]
    pct("(2) change of R_n", dRn, -4.22, 2)
    pct("    gold out", dG, -0.44, 2)
    pct("    notes taken by the public", dC, 3.78, 2)
    chk("    -0.44 - 3.78", -0.44 - 3.78, -4.22, tol=1e-9)
    pct("    coin of the Banking Department", b["coin"] - a["coin"], -0.39, 2)
    pct("(3) discounts, advances and other securities", b["loans"] - a["loans"], 10.10, 2)
    pct("    other deposits", b["other_dep"] - a["other_dep"], 5.11, 2)
    assert b["R"] - a["R"] > -(b["loans"] - a["loans"])                         # 准备金没有减少同样多
    assert a["bankers"] < a["R"] and a["bankers"] / a["R"] > 0.85               # 准备金几乎就空了
    assert "convertibility into gold and free competition" in Q["bo_bankingschool"]
    assert "insufficiently automatic" in Q["bo_automatic"] and "Thomas Tooke" in Q["bo_tooke"]
    assert "centralize the right of note issue" in Q["bo_white"]
    assert "profit-maximizing" in Q["bo_profitmax"]
    assert "Scottish" in Q["rk_scottish"] and "Scotland" in Q["bg_scotland"]
    chk("Peel, 1847", F["df_peel"], [1847])


def bagehot(F, Y, Q, W, D):
    assert "foreign drain is added to a domestic drain" in Q["bg_remedy"]
    assert "stop the foreign export" in Q["bg_foreign"]
    assert "in particular cases it should be lent" in Q["bg_treasure"]
    chk("Harman: 1825", [Y["bg_harman"]], [1825])
    assert "Mr. Harman" in Q["bg_harman_who"] and "a day or two" in Q["bg_calm"]
    chk("Bank Rate 1866: 10%", D.loc["1866"].max(), 10)
    assert "refuse some one who has good security" in Q["bg_refuse"] and "ultimately lose" in Q["bg_nolose"]
    assert "except for foreign payments" in Q["bg_whoever"]
    chk("1866: not even (万英镑) of fresh money", F["bg_50000"], [1866, 50000])
    chk("    = 5 万", F["bg_50000"][1] / WAN, 5)
    assert "Consols" in Q["bg_50000"]
    # Goschen
    chk("Goschen 1831-1907", F["hp_goschen"], [1831, 1907])
    c, tau = GOSCHEN["c"], GOSCHEN["tau"]
    chk("Goschen: cost 1/2%, a yearly difference of 2%, 1/2% on three months", F["bg_goschen"], [c, 2, c])
    chk("eq:gold-goschen with Goschen's numbers (%)", goschen(c, tau), F["bg_goschen"][1])
    chk("    the profit on three months (%)", goschen(c, tau) * tau / 12, F["bg_goschen"][2])
    assert "divided by four" in Q["bg_goschen_divided"]
    chk("London over Paris: more than (points)", F["bg_paris"], [2])
    assert "Goschen recommended" in Q["bg_goschen_rec"]
    chk("steps of 1 point; from 1860; before, 1/2", F["bg_steps"] + F["bg_steps1860"], [1, 1860, 0.5])
    assert "most unpopular" in Q["bg_unpopular"]
    r1, r2 = rises(D, 1844, 1859), rises(D, 1860, 1873)
    chk("1844-1859: rises; of 1/2 point", [r1.sum(), r1[0.5]], [31, 21])
    chk("1860-1873: rises; of 1 point; of 1/2 point", [r2.sum(), r2[1.0], r2[0.5]], [74, 45, 29])
    assert r2.sum() == r2[1.0] + r2[0.5]
    assert Y["bg_limited"] == 1873                                                # Lombard Street, 1873
    # ex:gold-goschen
    chk("(1) three months (%)", goschen(c, tau), 2)
    chk("    one month (%)", goschen(c, GOSCHEN["tau_short"]), 6)
    chk("(2) Bank Rate from 12 May 1866", rate_on(D, "1866-05-12"), 10)
    chk("    Paris less than (%)", F["an_france"], [4])
    gap = rate_on(D, "1866-05-12") - F["an_france"][0]
    chk("    the difference is more than (points)", gap, 6)
    chk("    on three months, more than (%)", gap * tau / 12, 1.5)
    chk("    three times the cost", gap * tau / 12 / c, 3)
    chk("(3) rho more than (points)", gap - goschen(c, tau), 4)
    # Tiberius
    chk("AD 33", [Y["ta_loan"]], [33])
    chk("a hundred thousand great sesterces (十万)", F["ta_loan"], [100000])
    # 一个大塞斯特斯（sestertium）合一千塞斯特斯: Gordon's footnotes price a thousand small sesterces at £8 6s 8d
    # and a thousand great sesterces at £8333, so one great sesterce is a thousand small ones
    small = F["ta_small"][1] + F["ta_small"][2] / 20 + F["ta_small"][3] / 240
    chk("    Gordon: great / small sesterce", (F["ta_great"][1] / F["ta_great"][0]) / (small / F["ta_small"][0]),
        1000, tol=0.5)
    assert "small sesterces" in Q["ta_small"] and "great sesterces" in Q["ta_great"]
    chk("    = 一亿 sesterces", F["ta_loan"][0] * 1000 / YI, 1)
    chk("three years; double", F["ta_terms"], [3, 2])
    assert "without interest" in Q["ta_terms"]
    chk("Overends 1857", [Y["bg_1857brokers"]], [1857])
    # pitfall
    chk("help asked for (万英镑)", F["an_refused"][0] / WAN, 40)
    chk("risky speculations after", F["an_insolvent"], [1860])


def rules(F, Y, Q, W, D):
    chk("Kindersley, February 1930", F["mo_kindersley"], [1930])
    assert "before World War I" in Q["du_phrase"] and "after the war" in Q["du_phrase"]   # 第一次世界大战以后才有
    assert "February 1930" in Q["mo_kindersley"] and "Committee on Finance and Industry" in Q["mo_committee"]
    assert "two weeks later" in Q["mo_twoweeks"] and "So far as I can ascertain" in Q["mo_ascertain"]
    assert "Bank of England" in Q["mo_kindersley"]
    # Keynes used the phrase in 1925, five years before the first use Moggridge could find; both after the war
    chk("Keynes, The Economic Consequences of Mr. Churchill", F["ke_1925"], [1925])
    chk("    five years before Kindersley", F["mo_kindersley"][0] - F["ke_1925"][0], 5)
    assert "pre-war value in gold" in Q["ke_prewar"] and "So far as I can ascertain" in Q["mo_ascertain"]
    chk("Bloomfield's annual data", F["du_annual"], [1880, 1914])
    chk("    all central banks: comply, violate (%)", F["du_34_60"], [34, 60])
    chk("    the Bank of England (%)", F["du_boe"], [47, 50])
    assert "opposite direction" in Q["bo_opposite"]
    # the count from the weekly returns
    e, m = changes(W, "end"), changes(W, "mean")
    se, sm = shares(e), shares(m)
    chk("year-end changes 1880-1913: n, same, opposite", [se["n"], se["comply"], se["violate"]], [34, 16, 18])
    chk("annual means: same, opposite", [sm["comply"], sm["violate"]], [17, 17])
    chk("    no change", [se["none"], sm["none"]], [0, 0])
    # ex:gold-rules
    for y, a, b in [(1894, 8.06, -4.53), (1895, 11.08, 10.28), (1896, -9.47, 6.76)]:
        pct(f"ex:gold-rules {y} international", e.loc[y, "intl"], a, 2)
        pct(f"    {y} domestic", e.loc[y, "dom"], b, 2)
    assert list(classify(e.loc[1894:1896])) == ["violate", "comply", "violate"]
    d99 = e.loc[1899, "intl"]
    assert 0 < d99 < 0.01, d99                                                      # 不到 1 万英镑
    assert classify(e.loc[[1899]]).iloc[0] == "comply"
    assert "countercyclically" in Q["du_counter"]
    # critiques
    assert "Taussig" not in Q["bo_taussig"] and "simultaneity" in Q["bo_taussig"]
    assert "too rapid" in Q["bo_toorapid"]
    assert "wheat" in Q["bo_wheat"] and "bricks" in Q["bo_wheat"]
    chk("1913: selling the securities would cut world reserves by (%)", F["bo_06"], [1913, 0.6])
    chk("    selling the gold would add (%)", F["bo_05"], [0.5])
    # pitfall: Bank Rate changed more than six times a year on average
    ch = D.diff().dropna().loc["1844":"1913"]
    per_year = len(ch) / (1913 - 1844 + 1)
    chk("Bank Rate changes a year, 1844-1913 (more than 6)", per_year, None)
    assert 6 < per_year < 7, per_year


def state(F, Y, Q, W, D, P):
    chk("Menger 1892", [Y["me_noaccident"]], [1892])
    assert "cowrie-shells" in Q["me_cowrie"] and "slabs of salt" in Q["me_cowrie"]
    assert "less saleable for more saleable" in Q["me_saleable"]
    chk("Knapp, first in 1905; the translation 1924", F["kn_1905"] + [Y["kn_creature"]], [1905, 1924])
    assert "accepted in payment by the State" in Q["kn_statemoney"]
    assert "No material has per se a fixed price" in Q["kn_noprice"]
    assert "France and Germany" in Q["kn_england"] and "regulate the exchange on England" in Q["kn_england"]
    assert "Bourse" in Q["kn_bourse"] and "foreign exchange" in Q["kn_specie"]
    assert "outside its own country, no Government can do so" in Q["bg_inside"]
    # the case box
    chk("Germany chose freely: 1871", F["kn_free"], [1871])
    chk("1,392 marks a pound of fine gold", F["rb_pound"], [1392])
    chk("the Bank Act of 14 March 1875; operations from 1876", F["rb_act"] + [F["mg_founded"][1]], [14, 1875, 1876])
    chk("contingents: total; the Reichsbank (亿马克)", [x / YI for x in F["rb_contingent"]], [3.85, 2.5])
    chk("the tax on the excess (% a year)", F["rb_tax"], [5])
    chk("discount rate at least (%)", F["rb_raise"], [5])
    chk("cover at least", F["rb_third"], [1 / 3])
    assert "one-third of its note liabilities" in Q["mg_third"]
    assert "Three times" in Q["rb_three"] and "impassable limit" in Q["rb_contrast"]
    assert "cost penalty" in Q["mg_penalty"]
    chk("the first five years: 1876-1880", [F["mg_founded"][1], Y["rb_first5"]], [1876, 1880])
    assert Q["rb_first5"].endswith("there was no")                                 # 'excess issue' (note)
    chk("1881-1885: five", F["rb_1881"], [1881, 1885, 5])
    chk("1886-1890: ten, six in 1890", F["rb_1886"], [10, 6, 1890])
    chk("1891-1895: four", F["rb_1891"], [4])
    chk("1896-1900: 71", F["rb_1896"], [71])
    chk("30 September 1899 (亿马克)", [F["rb_1899"][0], F["rb_1899"][1], F["rb_1899"][2] / YI], [30, 1899, 3.712])
    assert "consistently expanded its portfolio when losing gold" in Q["mg_opposite"]
    assert "exchange rate with London" in Q["mg_target"]
    # 1896
    w_, c_, u_ = P.uk_wholesale_2010_100, P.uk_cpi_2015_100, P.us_cpi_1982_84_100
    pct("UK wholesale prices 1873-1896 (%)", 100 * (w_[1896] / w_[1873] - 1), -45, 0)
    pct("UK consumer prices (%)", 100 * (c_[1896] / c_[1873] - 1), -23, 0)
    pct("US consumer prices (%)", 100 * (u_[1896] / u_[1873] - 1), -30, 0)
    pct("UK wholesale 1913 over 1896 (%)", 100 * (w_[1913] / w_[1896] - 1), 40, 0)
    assert u_.loc[1873:1896].idxmin() >= 1894 and w_.loc[1873:1913].idxmin() == 1896
    chk("Fisher 1896", [Y["fi_opening"]], [1896])
    chk("the Chicago platform: 9 July 1896", F["br_platformdate"], [9, 1896])
    chk("16 to 1", F["br_populist"], [16, 1])
    chk("    the platform's 16", F["br_plank"], [16])
    chk("    the Populists in", [Y["br_populist"]], [1892])
    chk("Bryan 1860-1925", F["ws_bryan"], [1860, 1925])
    chk("Bryan's vote (万)", F["br_votes"][0] / WAN, 651.1, tol=0.05)
    chk("McKinley's plurality (万)", F["br_plurality"][0] / WAN, 59.7, tol=0.05)
    chk("19,436 votes; 48 more; 224", F["br_19436"], [19436, 48, 224])
    chk("McKinley 1843-1901; the 25th, 1897-1901", F["ws_mckinley"] + F["ws_mckinley_pres"],
        [1843, 1901, 25, 1897, 1901])
    chk("Gold Standard Act, 14 March 1900", F["gs_title"], [14, 1900])
    chk("25.8 grains, nine-tenths fine", F["gs_grains"], [25.8, 0.9])
    chk("the gold reserve (亿美元)", F["gs_reserve"][0] / YI, 1.5)
    # ex:gold-debt
    p73, p96 = u_[1873], u_[1896]
    pct("ex:gold-debt US CPI 1873", p73, 11.6, 1)
    pct("    1896", p96, 8.14, 2)
    pct("(1) real burden up (%)", 100 * (p73 / p96 - 1), 42.5, 1)
    g = (p96 / p73) ** (1 / (1896 - 1873)) - 1
    pct("(2) prices a year (%)", 100 * g, -1.53, 2)
    pct("(3) ex post real rate at 6% (eq:prices-fisher, %)", 100 * ((1 + DEBT_I / 100) / (1 + round(g, 4)) - 1), 7.6, 1)


def test(F, Y, Q, W, D):
    chk("Bank Rate 10% from 12 May 1866", rate_on(D, "1866-05-12"), 10)
    chk("    9% on 11 May", rate_on(D, "1866-05-11"), 9)
    chk("    still 10% on 15 August", rate_on(D, "1866-08-15"), 10)
    chk("    8% on 16 August", rate_on(D, "1866-08-16"), 8)
    chk("Gladstone, 17 May 1866", F["hm_ref"][:2], [17, 1866])
    gs = F["hm_govsec"]
    chk("government securities in five days (万英镑)", gs[2] / WAN, 287.4)
    chk("bills; the total (万英镑)", [x / WAN for x in F["hm_bills"]], [935, 1222.5])
    chk("    the total is rounded: 2,874,000 + 9,350,000 (万英镑)", (gs[2] + F["hm_bills"][0]) / WAN, 1222.4)
    chk("Bagehot: new money; the reserve before (万英镑)", [F["bg_13m"][1] / WAN, F["bg_13m"][0] / WAN],
        [1300, 581.2])
    pct("the return of 9 May: the reserve (万英镑)", W.loc["1866-05-09"].bd_reserve * 100, 581.2, 1)
    pct("30 May: the reserve (万英镑)", W.loc["1866-05-30"].bd_reserve * 100, 86, 0)
    assert "went down to nothing" in Q["bg_13m"] and W.bd_reserve.loc["1866-05":"1866-06"].min() > 0.5  # 并没有真的到零
    pct("    the loans (万英镑)", W.loc["1866-05-30"].bd_other_securities * 100, 3344.7, 1)
    # tab:gold-three
    peaks, lows = {}, {}
    for y, day in LETTERS.items():
        t0 = pd.Timestamp(day)
        peaks[y] = D.loc[t0 - pd.Timedelta(weeks=WINDOW): t0 + pd.Timedelta(weeks=WINDOW)].max()
        lows[y] = window_min(W, "bd_reserve", day)
    chk("tab:gold-three: the peak of Bank Rate", [peaks[y] for y in LETTERS], [8, 10, 10])
    for y, (d, x), (md, v) in [(1847, lows[1847], ("10-30", 1.61)), (1857, lows[1857], ("11-11", 1.46)),
                               (1866, lows[1866], ("05-30", 0.86))]:
        pct(f"    the lowest reserve, {y}", x, v, 2)
        assert d.strftime("%m-%d") == md, (y, d)
    for rid, d1, d2 in [("bg_loans1847", "1847-10-16", "1847-10-30"), ("bg_loans1857", "1857-10-24", "1857-11-25"),
                        ("bg_loans1866", "1866-04-25", "1866-05-30")]:
        got = [truncated(W.loc[d].bd_other_securities) for d in (d1, d2)]
        chk(f"    Bagehot's loans = W2, truncated ({rid})", got, [x / MILL for x in F[rid]], tol=1e-9)
        for x, v in zip(F[rid], got):
            pct(f"    printed ({rid})", x / MILL, round(v, 2), 2)
    f = W.fiduciary_issue
    chk("    1857: over the limit by (£ m)", f.loc["1857"].max() - f.loc["1857-11-11"], 2.00)
    # Gladstone on 17 May
    assert "open market" in Q["hm_openmarket"] and "unlimited amount of discount" in Q["hm_unlimited"]
    # the gold came back
    gmin = W.issue_gold.loc["1866-05":"1866-06"]
    assert gmin.idxmin() == pd.Timestamp("1866-05-23")
    pct("gold, 23 May 1866 (万英镑)", gmin.min() * 100, 1130, 0)
    pct("    20 June (万英镑)", W.loc["1866-06-20"].issue_gold * 100, 1417, 0)
    assert W.loc["1866-06-20"].issue_gold > W.loc["1866-05-09"].issue_gold                # 比 5 月 9 日还多
    chk("Paris less than (%); London (%)", F["an_france"] + [rate_on(D, "1866-05-12")], [4, 10])
    assert "distrust of English investments" in Q["an_aug6"]
    chk("no banking crisis after", F["rk_schwartz"], [1866])
    chk("the Baring crisis (the OCR reads '189O')", [Y["du_baring"]], [1890])
    assert "189O-the Baring crisis" in Q["du_baring"] and "gold convertibility" in Q["du_convertible"]
    assert "complex" in Q["rk_complex"]
    # 1907
    chk("Knickerbocker's deposits (万美元)", F["sp_knick"][0] / WAN, 6200)
    assert "third largest trust company" in Q["sp_knick"]
    chk("Monday 21 October 1907", [F["sp_oct21"][0], date(1907, 10, 21).weekday()], [21, 0])
    chk("a run of three hours; paid out (万美元)", [F["sp_run3h"][0], F["sp_run3h"][1] / WAN], [3, 800])
    chk("    on Tuesday 22 October (Sprague: 'On Tuesday'; the clearing was stopped 'on the following day')",
        date(1907, 10, 22).weekday(), 1)
    assert Q["sp_run3h"].startswith("On Tuesday") and "on the following day" in Q["sp_oct21"]
    chk("Wednesday 23 October; deposits (万美元)", [F["sp_tca"][0], date(1907, 10, 23).weekday(),
                                                     F["sp_tca"][1] / WAN], [23, 2, 6400])
    assert "second of the trust companies in size" in Q["sp_tca"]
    chk("    paid out in two weeks (万美元)", F["sp_34m"][0] / WAN, 3400)
    assert "two weeks" in Q["sp_34m"]
    chk("loan certificates from 26 October", F["sp_lc1907"], [26])
    # the $110m is the increase of the New York banks' loans in the weeks ending 26 October, 2 and 9 November
    # (10.8 + 60.7 + 38.9, Sprague p. 271), not the amount of loan certificates issued
    chk("    loans up by over (亿美元) in three weeks", F["sp_110m"][3] / YI, 1.1)
    chk("    the three weekly loan increases add up to over the $110m (亿美元)", sum(F["sp_110m"][:3]) / YI, 1.104)
    assert "loan increase" in Q["sp_110m"] and "three weeks" in Q["sp_110m"]
    assert "solely in settling balances between the banks" in Q["sp_lcdef"]
    chk("the currency premium: 31 October to 31 December", F["sp_premium"], [31, 31])
    chk("the reserve ratio never below; 1873 (%)", F["sp_ratio"], [20, 12.8, 18, 1873])
    assert "varying with the location of the bank" in Q["sp_minimum"]
    assert "partial suspension" in Q["sp_deficit"] and "arithmetical ratio of reserve" in Q["sp_arith"]
    # 1913
    chk("Federal Reserve Act approved 23 December 1913", F["fr_approved"], [23, 1913])
    assert "rediscounting commercial paper" in Q["fr_preamble"] and "supervision of banking" in Q["fr_preamble"]
    chk("reserves: deposits 35%, notes 40% gold", F["fr_reserve"], [35, 40])
    assert "gold or lawful money" in Q["fr_reserve"] and "reserves in gold of not less than forty" in Q["fr_reserve"]
    assert "actual commercial transactions" in Q["fr_commercial"]
    chk("suspension up to (days)", F["fr_suspend"], [30])
    chk("the tax: at most 1% a year until 32.5%", F["fr_tax"], [1, 32.5])
    chk("    on the deficiency below the 40% gold reserve against the notes", F["fr_reserve"][1], 40)
    assert "such deficiency" in Q["fr_tax"]
    # tab:gold-limits
    chk("tab:gold-limits: 1,400 万英镑; 3.85 亿, 2.5 亿马克", [F["ac_14m"][0] / WAN] +
        [x / YI for x in F["rb_contingent"]], [1400, 3.85, 2.5])
    chk("    one-third; 35%, 40%; 5%; 30 days", [F["rb_third"][0], *F["fr_reserve"], F["rb_tax"][0], F["fr_suspend"][0]],
        [1 / 3, 35, 40, 5, 30])
    chk("    71 excess issues in 1896-1900", F["rb_1896"], [71])
    # the deeper box
    chk("Friday: Hansard (万英镑); Andreades", [gs[0] / WAN, F["an_929"][0] / WAN], [91.9, 92.9])
    chk("    the total exceeds the sum by (英镑)", F["hm_bills"][1] - gs[2] - F["hm_bills"][0], 1000)
    chk("Andreades: 10% from 11 May", F["an_rate10"], [7, 8, 9, 10])
    assert "August 6th" in Q["an_aug6"] and "11th" in column("note")["an_rate10"]
    chk("the Governor's letter: morning; about (万英镑)", [F["an_5727"][0] / WAN, F["an_5727"][1] * 100], [572.7, 300])
    assert "letter of the Governor" in Q["an_holland"]
    chk("Bagehot's reserve before = W2 on 9 May, to the thousand pounds (万英镑)", F["bg_13m"][0] / WAN,
        round(W.loc["1866-05-09"].bd_reserve * 1000) / 10)
    chk("Bagehot 1847: the reserve fell to (万英镑)", F["bg_reserve1847"][0] / WAN, 117.6)
    chk("    = the notes of the Banking Department on 30 October 1847", F["bg_reserve1847"][0] / MILL,
        truncated(W.loc["1847-10-30"].notes_in_banking_dept))


def selfcheck(F, W):
    a, b = departments(W, "1857-11-11"), departments(W, "1857-11-18")
    pct("SC1 F, 11 Nov", a["F"], 14.475, 3)
    pct("    G", a["G"], 6.666, 3)
    pct("    C", a["C"], 20.183, 3)
    pct("    F, 18 Nov", b["F"], 16.475, 3)
    pct("    G", b["G"], 6.080, 3)
    pct("    C", b["C"], 21.406, 3)
    pct("    R_n, 11 Nov (printed inputs)", 14.475 + 6.666 - 20.183, 0.958, 3)
    pct("    R_n, 18 Nov", 16.475 + 6.080 - 21.406, 1.149, 3)
    pct("    without the letter", 14.475 + 6.080 - 21.406, -0.851, 3)
    pct("    short by about (万英镑)", -(14.475 + 6.080 - 21.406) * 100, 85, 0)
    pct("    the return: R_n, 18 Nov", b["Rn"], 1.15, 2)
    chk("SC2 (%)", goschen(SC2["c"], SC2["tau"]), 1.5)
    chk("    London at least (%)", SC2["paris"] + goschen(SC2["c"], SC2["tau"]), 4.5)
    e = changes(W, "end")
    for y, a_, b_, cls in [(1902, -2.29, 18.71, "violate"), (1913, 4.65, 15.52, "comply")]:
        pct(f"SC3 {y} international", e.loc[y, "intl"], a_, 2)
        pct(f"    {y} domestic", e.loc[y, "dom"], b_, 2)
        assert classify(e.loc[[y]]).iloc[0] == cls
    year_tax = F["rb_1899"][2] * F["rb_tax"][0] / 100
    chk("SC5: a year's tax (万马克)", year_tax / WAN, 1856)
    pct("    a week (万马克)", year_tax / WEEKS / WAN, 35.7, 1)


def ending(F, D):
    chk("12 May 1866 was a Saturday (weekday 5)", date(1866, 5, 12).weekday(), 5)
    chk("10% until 15 August", [rate_on(D, "1866-05-12"), rate_on(D, "1866-08-15")], [10, 10])
    assert "commercially weaker State" in quotes()["kn_weaker"]


# the life dates the chapter gives without a row of its own: the same words in an earlier chapter
LIVES = {"Walter Bagehot，1826—1877": "ch18_smith", "Thomas Tooke，1774—1858": "ch19_bullion",
         "Robert Peel，1788—1850": "ch19_bullion", "Henry Thornton，1760—1815": "ch19_bullion",
         "David Hume，1711—1776": "ch19_bullion", "John Maynard Keynes，1883—1946": "ch20_say",
         "Carl Menger，1840—1921": "ch14_africa", "Georg Friedrich Knapp，1842—1926": "ch04_money",
         "Irving Fisher，1867—1947": "ch03_prices"}
# the years of the cross-references: (words of this chapter, chapter where the event is told, words there)
EVENTS = [("1772 年艾尔银行", "ch18_smith", "1772 年 6 月"), ("1819 年恢复兑付的法案", "ch19_bullion", "1819 年"),
          ("里的 1720 年", "ch16_mercantilism", "1720"), ("1672 年的阿姆斯特丹银行", "ch15_finrevolution", "1672 年"),
          ("美联储在不到四个月里把资产负债表扩大了一倍半", "ch04_money", "美联储在不到四个月里把资产负债表扩大了一倍半"),
          ("扩大的主要是各种流动性便利", "ch04_money", "2008 年秋天主要是各种流动性便利"),
          ("被高利贷法卡在 5\\% 的上限上", "ch20_say", "贴现率提到 5\\%，即高利贷法允许的上限")]


def book(Q):
    """Life dates, the years of events told in other chapters, and the years of works cited through others."""
    t = tex_text()
    for words, ch in LIVES.items():
        assert words in t, words
        other = next((ROOT / "zh").glob(ch + ".tex")).read_text(encoding="utf-8")
        assert words in other, (words, ch)
    for here, ch, there in EVENTS:
        assert here in t, here
        assert there in next((ROOT / "zh").glob(ch + ".tex")).read_text(encoding="utf-8"), (ch, there)
    L = column("juan")
    assert "Taussig 1927" in L["bo_taussig"] and "Taussig（1927）" in t
    assert all("McCloskey and Zecher 1976" in L[i] for i in ("bo_violinist", "bo_regions", "bo_unified", "bo_06"))
    assert "Bloomfield 1959" in L["bo_managed"] and "Bloomfield（1959）" in t
    chk("Schwartz (1987), quoted by Rockoff", facts()["rk_schwartz_who"], [1987])
    assert "Schwartz（1987）据 Rockoff" in t
    _, m = load_snapshot("boe_millennium_prices_1821_1913")
    assert "Williamson (2017a)" in m["series"] and "Williamson 2017" in t
    # the sources of the table tab:gold-limits
    assert L["ac_14m"].endswith("s. II") and "1844 年法令第 2 条" in t
    pages = {L[i] for i in ("rb_contingent", "rb_tax", "rb_third", "rb_1896")}
    assert pages <= {"p. 22", "p. 23", "pp. 23-24", "p. 68 (sec. 17 of the Bank Act)", "p. 81", "p. 82"}, pages
    assert "第 22—23、68、82 页" in t
    assert {L["fr_reserve"], L["fr_tax"], L["fr_suspend"]} <= {"sec. 11(c)", "sec. 16"}
    assert "联邦储备法第 11、16 条" in t
    # ex:gold-rules (3): Bloomfield's half and half in the year-end count
    e = shares(changes(weekly(), "end"))
    pct("    year-end: comply (%)", 100 * e["comply"] / e["n"], 47, 0)
    pct("    violate (%)", 100 * e["violate"] / e["n"], 53, 0)
    # fig:gold_prices: 1870-1913; fig:gold_panics: Bank Rate reaches its top on the day of the letter (1866: the next)
    P = prices()
    assert P.loc[1870:1913].notna().all().all() and "1870—1913 年" in t
    D = bank_rate()
    for y, day in LETTERS.items():
        t0 = pd.Timestamp(day)
        s = D.loc[t0 - pd.Timedelta(weeks=WINDOW): t0 + pd.Timedelta(weeks=WINDOW)]
        first = s[s == s.max()].index[0]
        assert 0 <= (first - t0).days <= 1, (y, first)


def witnesses(F, Q):
    """Second witnesses of statements of the text that the text does not quote, and the notices of the bibliography."""
    chk("advances on 11 May 1866: Andreades 'nearly', Hansard 'more than' (the text follows Hansard; £ m)",
        [F["an_4m"][0], F["hs_4m"][0] / MILL], [4, 4])
    assert "nearly" in Q["an_4m"] and "more than" in Q["hs_4m"]
    assert "most respected" in Q["an_respected"] and "next to the Bank of England" in Q["bg_nexttobank"]
    assert "freely" in Q["bg_ultimate"] and "good securities" in Q["bg_ultimate"]
    assert "yesterday" in Q["hq_calamitous"] and "rapidity" in Q["hs_rapidity"]          # 前一天傍晚开始的
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    block = bib[bib.index("% ---- 第 23 章"):bib.index("\\end{thebibliography}")]
    items = {m.group(1): m.group(2) for m in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", block)}
    for key in ("bordo1984", "dutton1984", "mcgouldrick1984", "dornbusch1984"):
        assert Q["nb_notice"] in items[key] and "All rights reserved" in items[key], key
    assert Q["nb_rights"].startswith("All rights reserved")
    keys = set(re.findall(r"\\bibitem\{([^}]+)\}", bib))
    cited = {k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", tex_text()) for k in c.split(",")}
    assert cited <= keys, sorted(cited - keys)
    assert set(items) <= cited, sorted(set(items) - cited)
    print(f"ok {len(cited)} works cited, {len(items)} of them in the bibliography block of Chapter 23")


def main() -> None:
    df = _rows()
    F, Y, Q = facts(), years(), quotes()
    W, D, P = weekly(), bank_rate(), prices()
    check_readings(df)
    check_text(df)
    opening(F, Y, Q, W)
    world(F, Y, Q, W, D)
    sec1844(F, Y, Q, W)
    bagehot(F, Y, Q, W, D)
    rules(F, Y, Q, W, D)
    state(F, Y, Q, W, D, P)
    test(F, Y, Q, W, D)
    selfcheck(F, W)
    ending(F, D)
    witnesses(F, Q)
    book(Q)
    anchors("zh/ch23_goldstandard.tex", df["id"], script=Path(__file__))


if __name__ == "__main__":
    main()
