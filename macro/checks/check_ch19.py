"""Chapter 19 (数量论、价格–铸币流动与金块论战): every number and every quotation in zh/ch19_bullion.tex.

    python3 checks/check_ch19.py

Inputs:
  bullion_facts                quotations of Cannan (1919: his introduction, his Tables I and II and the Bullion Report
                               of 1810 that he reprints), Hume (1752, a later edition and the first), Ricardo (1810),
                               Thornton (1802), Tooke (1838), Silberling (1919, with his Tables 6 and 7), Edvinsson
                               (2010) and Fregert (2014); the tables and the passages the OCR garbles are read on the
                               page images (checked by data/fetch/verify_web_quotes.py)
  boe_millennium_gb_1790_1830  Bank of England, A Millennium of Macroeconomic Data: the wholesale price index of Gayer,
                               Rostow and Schwartz (1821-25 = 100), the consumer price index (Feinstein for these years)
                               and the national debt, 1790-1830
  riksbank_sweden_1740_1777    Sveriges riksbank: the riksdaler in marks kopparmynt (Edvinsson 2010) and the Riksbank's
                               notes and metal reserves (Fregert 2014), 1740-1777
The figure module figsrc/fig_ch19.py imports the functions defined here.

What is checked here:
  1. readings   every number of the value column of bullion_facts is read from its quotation: digits (with the
                fractions ½, ¼ and ¾), English number words, fractions and the OCR's '£i' for £1 and 'hve' for five; the rows of the
                transcribed tables are read with their signs
  2. the text   every “…” in the chapter is the chapter's Chinese rendering of a quotation (TRANSLATIONS:
                rendering -> row or rows) or a term of the text (ALLOW)
  3. numbers    every number of the text, section by section, with quoted()

Models (the chapter's key equations):
    price-specie flow    x_{t+1} = (1 - kappa) x_t,  x_t = ln(M_t / Mbar)          (eq:bullion-hume)
    equation of exchange MV = PT                                                (eq:bullion-exchange)
    premium              P = (1 + pi) P^g                                       (eq:bullion-premium)
    gold point           1 - delta >= (1 - c) / (1 + pi)                        (eq:bullion-goldpoint)
Units: 1 pound = 20 shillings = 240 pence; the mint price of standard gold is £3 17s. 10½d. an ounce (934.5 pence),
and £1 is 123¼ grains of standard gold. Silberling's percentage deviation of the exchange is -100 delta.
"""
from __future__ import annotations

import math
import re

import pandas as pd

from common import ROOT, load_snapshot, quoted

TEX = ROOT / "zh" / "ch19_bullion.tex"
SHILLINGS, PENCE = 20, 240                 # per pound
GRAINS = 123.25                            # grains of standard gold in £1 at the mint price

# Teaching inputs stated in the text
KAPPA = 0.2                                # ex:bullion-hume
HUME_YEARS = [1, 2, 3, 5, 10]
TARGET = 0.9                               # ex:bullion-hume (3): back to 90 per cent in two years
PANIC_V = 0.9                              # ex:bullion-velocity: velocity falls 10 per cent
COSTS = (0.07, 0.035)                      # ex:bullion-goldpoint (1)
DELTAS = (0.16, 0.20)
# self-check questions
SC1 = dict(m=0.5, kappa=0.3, years=2)
SC2 = dict(c=0.05, delta=0.15, pi=0.08)
SC3 = dict(shillings=95)
SC4 = dict(P=1.3, pi=0.20)
SC5 = dict(M=2000, dv=0.20)
SC6 = dict(price=90, par=36, dv=0.25)


def chk(what: str, value: float, expected: float | None = None, tol: float = 1e-9, rel: float = 0.0) -> float:
    """quoted() with a tolerance for floating-point error on exact values; a list is compared element by element."""
    if isinstance(value, (list, tuple)):
        assert expected is not None and len(value) == len(expected), (what, value, expected)
        for i, (v, e) in enumerate(zip(value, expected)):
            quoted(f"{what} [{i + 1}]", float(v), e, tol=tol, rel=rel)
        return float(value[0])
    return quoted(what, float(value), expected, tol=tol, rel=rel)


def pct(what: str, value: float, expected: float, digits: int = 1) -> float:
    """A number printed with `digits` decimals."""
    return quoted(what, float(value), expected, tol=0.5 * 10 ** -digits + 1e-12)


# ---------------------------------------------------------------------------------------------------
# Loaders
def _rows() -> pd.DataFrame:
    df, meta = load_snapshot("bullion_facts", dtype=str, keep_default_na=False)
    assert 19 in meta["used_in"]
    assert df["id"].is_unique
    return df


def num(x: str) -> float:
    if "/" in x:
        a, b = x.split("/")
        return float(a) / float(b)
    return float(x)


def facts() -> dict[str, list[float]]:
    """id -> the numbers of the value column (several are separated by ';')."""
    return {r.id: [num(x) for x in r.value.split(";")] for r in _rows().itertuples() if r.value}


def years() -> dict[str, int]:
    return {r.id: int(r.year) for r in _rows().itertuples() if r.year}


def quotes() -> dict[str, str]:
    return {r.id: r.quote for r in _rows().itertuples()}


def boe() -> pd.DataFrame:
    df, meta = load_snapshot("boe_millennium_gb_1790_1830")
    assert 19 in meta["used_in"]
    return df.set_index("year")


def sweden() -> pd.DataFrame:
    df, meta = load_snapshot("riksbank_sweden_1740_1777")
    assert 19 in meta["used_in"]
    return df.set_index("year")


def cannan() -> pd.DataFrame:
    """Cannan's Tables I and II, 1792-1821 (£ millions); the bills begin in 1795."""
    F = facts()
    yrs = list(range(1792, 1822))
    cols = {"exp": "ci_t1_exp", "rev": "ci_t1_rev", "excess": "ci_t1_excess", "jevons": "ci_t1_jevons",
            "notes_f": "ci_t2_notes_f", "notes_a": "ci_t2_notes_a", "coin_f": "ci_t2_coin_f", "coin_a": "ci_t2_coin_a"}
    df = pd.DataFrame({k: F[v] for k, v in cols.items()}, index=yrs)
    assert len(F["ci_t1_bills"]) == 1821 - 1795 + 1
    df["bills"] = [float("nan")] * 3 + F["ci_t1_bills"]
    return df


def silberling() -> pd.DataFrame:
    """Silberling's Tables 6 and 7, 1790-1824: pi (premium, per cent) and dev (exchange, per cent from par)."""
    F = facts()
    yrs = list(range(1790, 1825))
    df = pd.DataFrame({"paper": F["si_t6_1"], "gold": F["si_t6_2"], "d_pence": F["si_t6_3"], "pi": F["si_t6_4"],
                       "quote": F["si_t7_1"], "ratio": F["si_t7_2"], "par": F["si_t7_3"], "d_sch": F["si_t7_4"],
                       "dev": F["si_t7_5"]}, index=yrs)
    return df


# ---------------------------------------------------------------------------------------------------
# The arithmetic of the chapter
def lsd(pounds: float, shillings: float, pence: float) -> float:
    """In pence."""
    return pounds * PENCE + shillings * 12 + pence


MINT = lsd(3, 17, 10.5)                    # pence an ounce of standard gold


def premium(price: float) -> float:
    """The premium of gold at a market price in pence an ounce."""
    return price / MINT - 1


def grains(price: float) -> float:
    """Grains of standard gold that £1 in notes buys at a market price in pence an ounce."""
    return GRAINS * MINT / price


def hume(x0: float, kappa: float, t: float) -> float:
    """eq:bullion-hume: M_t / Mbar."""
    return math.exp((1 - kappa) ** t * x0)


def half_life(kappa: float) -> float:
    return math.log(2) / -math.log(1 - kappa)


def min_premium(c: float, delta: float) -> float:
    """eq:bullion-goldpoint: the least premium at which the exchange can stand delta below par."""
    return (1 - c) / (1 - delta) - 1


def min_cost(pi: float, delta: float) -> float:
    """eq:bullion-goldpoint: the least cost of sending gold, given the premium and the fall of the exchange."""
    return 1 - (1 + pi) * (1 - delta)


def gold_prices(B: pd.DataFrame, S: pd.DataFrame) -> pd.Series:
    """eq:bullion-premium: the wholesale price index in gold, P / (1 + pi), 1790-1824."""
    yrs = S.index
    return B.wholesale_1821_25[yrs] / (1 + S.pi / 100)


def decompose(B: pd.DataFrame, S: pd.DataFrame, a: int, b: int) -> dict:
    """The change of ln P between two years, split into the premium and the price in gold."""
    P = B.wholesale_1821_25
    total = math.log(P[b] / P[a])
    prem = math.log((1 + S.pi[b] / 100) / (1 + S.pi[a] / 100))
    G = gold_prices(B, S)
    return dict(change=P[b] / P[a] - 1, total=total, prem=prem, gold=total - prem, share=prem / total,
                gold_change=G[b] / G[a] - 1)


def corr(x: list[float], y: list[float]) -> float:
    """Pearson's correlation coefficient (pandas.Series.corr; STYLE.md §6: no hand-written methods)."""
    return float(pd.Series(x, dtype=float).corr(pd.Series(y, dtype=float)))


PERIODS = [(1797, 1801), (1801, 1813), (1813, 1819), (1819, 1821)]     # fig:bullion_prices (b)


# ---------------------------------------------------------------------------------------------------
# 1. Readings of the numbers
WORDS = {"a": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
         "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
         "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90, "fourteenth": 14, "sixteenth": 16}
SCALE = {"thousand": 1e3, "million": 1e6, "millions": 1e6}
DENOM = {"half": 2, "fifth": 5, "fifths": 5, "sevenths": 7}
TIMES = {"double": 2, "fivefold": 5, "four-fold": 4}
OCR = {"£i": 1, "hve": 5}
LONG_S = {"fevenths": "sevenths"}
VULGAR = {"½": 0.5, "¼": 0.25, "¾": 0.75}


def _words(s: str) -> list[str]:
    w = s.lower().replace("-", " ").split()
    return [LONG_S.get(x, x) for x in w]


def cardinal(s: str) -> float:
    """An English cardinal ('forty-one', 'twelve millions', 'a million'); a unit word after the number ends it."""
    total, cur, seen = 0.0, 0.0, False
    for w in _words(s):
        if w in WORDS:
            cur += WORDS[w]
        elif w in SCALE:
            total += (cur or 1) * SCALE[w]
            cur = 0
        else:
            break
        seen = True
    assert seen, s
    return total + cur


def fraction(s: str) -> float:
    """'a fifth', 'four-fifths', 'three-sevenths'."""
    w = _words(s)
    assert w[-1] in DENOM and len(w) == 2, s
    return WORDS[w[0]] / DENOM[w[-1]]


def figure(s: str) -> float:
    """Digits with a vulgar fraction: '123¼', '10½', '2,380,216'."""
    s = s.replace(",", "").replace("£", "")
    if s and s[-1] in VULGAR:
        return (float(s[:-1]) if s[:-1] else 0.0) + VULGAR[s[-1]]
    return float(s)


def read(phrase: str, how: str) -> list[float]:
    if how == "num":
        return [figure(phrase)]
    if how == "en":
        return [cardinal(phrase)]
    if how == "m":                                # millions in words, in £ m
        return [cardinal(phrase) / 1e6]
    if how == "frac":
        return [fraction(phrase)]
    if how == "half":                             # 'half' alone
        return [0.5]
    if how == "slash":                            # '43/48'
        a, b = phrase.split("/")
        return [float(a) / float(b)]
    if how == "times":
        return [TIMES[phrase]]
    if how == "ocr":
        return [OCR[phrase]]
    raise ValueError(how)


FIGURES = re.compile(r"\d[\d,]*(?:\.\d+)?[½¼¾]?")
TABLE = re.compile(r"[-+]?\d+(?:\.\d+)?")
EN = "en"
# id -> [(phrase in the quotation, how it is read)], in order. Rows not listed are read with all the figures of the
# quotation; the rows of the transcribed tables (si_t*, ci_t*) with every signed number that stands alone.
READINGS = {
    "cn_terror": [("20", "num")],
    "cn_guinea": [("a pound", EN), ("a shilling", EN)],
    "cn_onepct": [("one per", EN)],
    "cn_doubled": [("double", "times"), ("half", "half"), ("a year", EN), ("two", EN)],
    "cn_fortyone": [("forty-one", EN), ("£i", "ocr"), ("forty", EN)],
    "cn_partial": [("2", "num"), ("1816", "num"), ("£i", "ocr"), ("2", "num"), ("1812", "num")],
    "cn_half": [("half", "half")],
    "cn_trifling": [("100", "num"), ("thirteen", EN), ("1810", "num")],
    "cn_counter": [("13", "num"), ("seventeen", EN)],
    "ci_t1_note": [("3", "num"), ("2", "num"), ("1", "num")],
    "ci_sixteen": [("sixteen resolutions", EN), ("fourteenth", EN), ("sixteenth", EN), ("two years", EN),
                   ("four days", EN)],
    "br_twoyears": [("two years", EN)],
    "br_nolimit": [("five per", EN)],
    "hm_louis": [("three-sevenths", "frac"), ("one", EN)],
    "hm_corn": [("1683", "num"), ("thirty", EN), ("fifty", EN)],
    "hm_fourfifths": [("four-fifths", "frac")],
    "hm_fivefold": [("fivefold", "times")],
    "hm_twelve": [("twelve millions", "m"), ("eighteen millions", "m"), ("thirty millions", "m")],
    "hm_scotland": [("a million", "m")],
    "hm_fifth": [("a fifth", "frac")],
    "h1_fourparts": [("four", EN)],
    "h1_fourfold": [("four-fold", "times")],
    "h1_louis": [("three fevenths", "frac"), ("one", EN)],
    "rc_fiveyears": [("one year", EN), ("five", EN)],
    "th_fivepct": [("five per", EN)],
    "tk_4and20": [("twelve years", EN), ("4", "num"), ("hve", "ocr"), ("20", "num")],
    "tk_probablyless": [("three years", EN)],
    "th_sixfour": [("six per", EN), ("five", EN), ("four per", EN)],
    "sb_430": [("43/48", "slash"), ("2", "num"), ("54", "num"), ("430", "num")],
    "sb_max": [("1813", "num"), ("two years", EN)],
    "sb_paperprices": [("26", "num")],
    "si_years": [("1790", "num"), ("1824", "num")],
    "ed_gradually": [("ten-year", EN), ("1760", "num")],
    "fr_tandem": [("1745", "num"), ("two decades", EN)],
}


def check_readings(df: pd.DataFrame) -> None:
    n = 0
    for r in df.itertuples():
        if not r.value:
            assert r.id not in READINGS, r.id
            continue
        vals = [num(x) for x in r.value.split(";")]
        if r.id in READINGS:
            got, pos = [], 0
            for phrase, how in READINGS[r.id]:
                k = r.quote.find(phrase, pos)
                assert k >= 0, f"{r.id}: {phrase!r} not found (in order) in the quotation"
                pos = k + len(phrase)
                got += read(phrase, how)
        elif r.id.startswith(("si_t", "ci_t")):
            got = [float(t) for t in r.quote.split() if TABLE.fullmatch(t)]
        else:
            got = [figure(x) for x in FIGURES.findall(r.quote)]
        assert [round(g, 9) for g in got] == [round(v, 9) for v in vals], f"{r.id}: read {got}, value column {vals}"
        n += 1
    quoted("rows with values, each read from its quotation", n, 132)


# ---------------------------------------------------------------------------------------------------
# 2. Every “…” of the text against the snapshot
# terms of the text, which are not quotations
ALLOW = {"千年宏观数据", "—", "只贴现好票据"}
# the chapter's Chinese renderings of the English quotations: rendering -> row (or rows)
TRANSLATIONS = {
    # opening
    "成群地来到我们的账房，显然是出于恐惧，要求兑付他们的银行券": "cn_terror",
    "极其富裕繁荣，足以消除对其银行券安全的一切怀疑": "cn_affluent",
    "走上指券的老路": "cn_assignats",
    "发烧在伦敦和在巴黎或阿姆斯特丹一样是发烧。": "cn_fever",
    # sec:bullion-world
    "在一个讲究妥协的国家里，可以预料两条路都会走。": "cn_both",
    "全国是多么平静地接受了用银行券办理一切交易，而发行人不再像从前那样兑付金银": "cn_quietly",
    "卷入一场大战的政府，没有一个愿意放弃不兑现的通货这样一部偷偷剥削臣民的强大机器": "cn_engine",
    # sec:bullion-hume
    "不是贸易的轮子，而是让轮子转得更平稳、更顺利的润滑油": "hm_oil",
    "依我看，只有在这段间隔、这个过渡的状态里，即在得到货币与物价上涨之间，金银数量的增加才有利于产业。": "hm_interval",
    "提高": "hm_louis",
    "官员的好政策只在于，如果可能，使货币不断增加": "hm_still",
    "设想英国全部货币的五分之四在一夜之间消失。": "hm_fourfifths",
    "这要多么短的时间，就会把我们失去的钱带回来": "hm_bringback",
    "一切相通的水，总是保持在同一水平上。": "hm_level",
    "把大帆船从西印度运回来的全部货币都留在西班牙": "hm_spain",
    "水平": ("hm_level", "h1_level"),
    "与各国的技艺与勤劳成比例": "hm_proportionable",
    "这要多么短的时间": "hm_bringback",
    "多么短的时间": "hm_bringback",
    "我几乎不知道还有什么办法能把货币压到它的水平以下，除了在这个王国里如此盛行的银行、公债与纸币信用制度。": "hm_paper",
    "我们通过纸币感受到货币过多带来的一切坏处，却得不到任何好处": "hm_foreigners",
    # sec:bullion-equation
    "一般说来，高度的信心会使银行券流通得更快。": "th_quicken",
    "错在近几次恐慌的时候过分收缩它的银行券，而不是过分扩大": "th_restricting",
    "我们多少会把结果当作原因": "th_mistake",
    "过分收缩": "th_restricting",
    # sec:bullion-restriction
    "他们忽略了一个事实：条件变了。": "cn_altered",
    # sec:bullion-report
    "指向我们自己国内通货的状况，是两者共同的原因": "br_domestic",
    "这是赫斯基森、桑顿和我拼凑起来的东西。": "cn_motley",
    "比铸币厂价格高约 15½\\%": "br_15half",
    "高 10\\% 多一点": "br_april",
    "大约 107 格令": "ci_1809",
    "87¼ 格令": "ci_gold1810",
    "世界其他地方对黄金的需求无论增加多少、无论出于什么原因，都不能在相当长的时期里使这里的金价大幅上涨": "br_sound",
    "据我所知，没有很大的变化。": "br_nochange",
    "对欧洲大陆贸易的限制，以及这个国家纸币流通的增加": "br_baring",
    "但实际发生的下跌，其余的部分仍要用别的方式来解释": "br_rest",
    "只要发行银行券的贷款是按照现在指导董事们行为的原则做出的，英格兰银行的纸币就不可能有任何过多的发行。": "br_doctrine",
    "我认为，如果我们只给殷实的人贴现……": "br_harman",
    "防止过多发行的保障，我想，完全一样。": "br_same",
    "如果降到 3\\% 呢？": "br_3pct",
    "一种在原则上完全错误、在实践中充满危险后果的学说": "br_erroneous",
    "借得太便宜了。借得太便宜的东西，他们就借得太多": "th_cheap",
    "完全一样": "br_same",
    "扩大贷款是治疗乡村地区偶然失去信心的真正办法": "br_1793remedy",
    "乡村银行家的全部纸币，是建立在英格兰银行纸币基础上的上层建筑": "br_superstructure",
    "这个国家的纸币流通目前有过多的发行，其最明确的征兆是金块的价格非常高，其次是对大陆的汇率很低；这个过多的发行，应当归因于对英格兰银行纸币发行缺乏足够的检查与控制，而最初的原因是停止现金兑付，它去掉了自然的、真正的控制。": "br_excess",
    "金块的价格与对外国的总体汇率，以任何相当长的时期来看": "br_criterion",
    "除了所有纸币都可以兑换成金银，找不到任何安全的、可靠的、始终适当的办法，防止纸币的过多发行，无论是偶然的还是长期的。": "br_convertibility",
    "明显得无需证明，又有违正义，不能不加纠正": "br_symptoms",
    # sec:bullion-debate
    "长期以来、现在也仍然处在相当大的折价之中，原因是它的数量过多，而不是对英格兰银行缺乏信心": "rc_superabundance",
    "在我看来，它是这种超出的结果": "rc_effect",
    "纸币数量的任何增加，都会提高金块的货币价格而不降低它的价值，与它提高其他商品的价格的方式相同、比例相同": "rc_wholly",
    "英格兰银行应当逐步减少它流通中的银行券，直到使剩下的银行券与它们所代表的铸币等值，换句话说，直到金块与银块的价格降到铸币厂价格。": "rc_remedy",
    "几乎跌到由运金费用决定的界限": "br_realfall",
    "1810 年到 1816 年的事态发展，不利于这一学说的传播与接受": "cn_admitted",
    "迄今为止、现在也仍然，在公众的估价中，与王国的法定铸币等值": "cn_vansittart3",
    "如果吃了，他也许会好得更快": "cn_patient",
    "任何相当长的时期": "br_criterion",
    "总的说来，我们可以判定，范西塔特的理论与他的财政管理一样不健全。": "cn_condemn",
    "以任何相当长的时期来看": "br_criterion",
    # sec:bullion-resumption
    "在停兑之下觉得很舒服，对回到一个不能保证它不会在不方便的时候被要求偿还债务的制度，毫无热情": "cn_bankcomfortable",
    "总之，发出 41 张一英镑的期票，换回来的东西很快只够兑付其中的 40 张，这不可能是好政策。": "cn_fortyone",
    "是愚蠢的，必须停止": "cn_follyword",
    "找不到这种看法的任何坚实的根据": "cn_nosolid",
    "银行券发行的那一点点减少，正如李嘉图一直坚持的，就是所需要的全部": "cn_ricardo_right",
    "最多不超过 4\\% 或 5\\%，那是当时纸币与黄金之间的差额；可实际上，法案的后果是物价普遍下跌了 30\\% 与 40\\%，有些人说甚至达到 50\\%": "tk_peel",
    "没有，按照任何正确的推理也不可能，使物价下跌超过纸币与黄金之间的差额": "tk_beyond",
    # the case of Sweden
    "事实上实行了不兑现的纸币本位，一直维持到 1776 年的铸币改革": "ed_fiat",
    "1760 年代后期出现了严重的通缩": "ed_gradually",
    "大量银行券被从流通中撤出，存起来，期待它们升值": "ed_saved",
    "36 马克的平价不得不放弃": "ed_1769",
    "都可以说是过度反应，或者说超调": "ed_overshoot",
    # sec:bullion-test
    "理论价格": "si_t6_2",
    "总的反向运动几乎是完全的，只有 1810—1812 年例外。": "sb_inverse",
    "对英国贸易的禁运与没收英国制造品，在欧洲达到了很高的效力": "sb_embargo",
    "约 4\\%": "tk_4and20",
    "约 20\\%": "tk_4and20",
    # the deeper box
    "全部货币的四份": "h1_fourparts",
    "增加到四倍": "h1_fourfold",
    "五分之四": "hm_fourfifths",
    "五倍": "hm_fivefold",
    "如此迷恋": "h1_infatuated",
    "如此盛行": "hm_paper",
    "七分之三": ("hm_louis", "h1_louis"),
    "有利于产业": ("hm_interval", "h1_industry"),
    "比 Jevons 的物价最高点晚两年": "sb_max",
    "那些人": "tk_50to100",
    "与我们通货制度的变化相比，都微不足道": "tk_50to100",
    "上涨了 50\\% 到 100\\%": "tk_50to100",
    # sec:bullion-legacy
    "借得太便宜了": "th_cheap",
    "与把它交给政府本身的现代办法相比，要好得多": "cn_favourably",
    "十三年里增加 100\\%": "cn_trifling",
    # takeaways
    "在原则上完全错误": "br_erroneous",
}


PUNCT = re.compile(r"[\s，。、；：！？“”‘’（）《》·…—,.;:!?'\"()\[\]|\-]")


def tex_text() -> str:
    return "\n".join(l for l in TEX.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("%"))


def text_quotations() -> list[str]:
    return re.findall(r"“([^”]*)”", tex_text())


def check_text(df: pd.DataFrame) -> None:
    ids = set(df["id"])
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
    print(f"ok {n} quotations of the text found in the snapshot (or listed as exceptions)")


# ---------------------------------------------------------------------------------------------------
# 3. Numbers, section by section
CANNAN_YEAR = 1919                         # the year of Cannan's book (bibitem cannan1919)


def opening(F, Y, T):
    chk("February 18 (the meeting reported)", F["cn_invasion"][0], 18)
    chk("    year", Y["cn_invasion"], 1797)
    chk("February 20, a Monday", F["cn_terror"][0], 20)
    pct("coin and bullion, end of February 1794 (万)", T.coin_f[1794] * 100, 700, 0)
    pct("    1796", T.coin_f[1796] * 100, 250, 0)
    pct("    1797", T.coin_f[1797] * 100, 110, 0)
    pct("notes, end of February 1797 (万)", T.notes_f[1797] * 100, 970, 0)
    chk("February 26, a Sunday", F["cn_sunday"][0], 26)
    chk("4,000 signatures", F["cn_4000"][0], 4000)
    chk("May 3 (37 Geo. III c. 45)", F["cn_may3"], [37, 45, 3])
    chk("June 24", F["cn_june24"][0], 24)
    chk("nearly a quarter of a century; the 24 years of the guide: 1821 - 1797", F["ci_ingots"][8] - 1797, 24)
    chk("early 1809: 90s.", F["ci_1809"][:2], [1809, 90])
    chk("    107 grains instead of 123¼", F["ci_1809"][3:], [107, 123.25])
    chk("the committee of 1810", Y["cn_feb19"], 1810)
    chk("Hume (1752): more than half a century before 1810", 1810 - Y["hm_oil"], 58)


def world(F, Y, T, B):
    chk("Cannan's account of 1792", Y["cn_12m"], 1792)
    chk("notes about 12 millions (万)", F["cn_12m"][0] * 100, 1200)
    chk("gold coin 20 to 30 millions (万)", [x * 100 for x in F["cn_goldcoin"]], [2000, 3000])
    chk("country banks: not below £5, since 1777", F["cn_country"], [5, 1777])
    chk("no interest above 5 per cent", F["cn_usury5"][0], 5)
    pct("expenditure 1792 (万)", T.exp[1792] * 100, 1740, 0)
    pct("revenue 1792 (万)", T.rev[1792] * 100, 1930, 0)
    quoted("    a small surplus: the excess of 1792 is negative", T.excess[1792], -1.9, tol=1e-9)
    chk("end of 1794", F["cn_pitt"][0], 1794)
    chk("1795 and 1796", F["ci_x"][:2], [1795, 1796])
    chk("    expenditure 51¾ and 57¾ millions (万)", [x * 100 for x in F["ci_x"][2:4]], [5175, 5775])
    chk("    revenue 20 and 21½ millions (万)", [x * 100 for x in F["ci_x"][4:]], [2000, 2150])
    chk("column 3 = column 1 - column 2", F["ci_t1_note"], [3, 2, 1])
    for y in T.index:
        assert abs(T.exp[y] - T.rev[y] - T.excess[y]) < 0.15, y
    pct("excess 1795 (万)", T.excess[1795] * 100, 3180, 0)
    pct("    1796 (万)", T.excess[1796] * 100, 3620, 0)
    pct("debt 1792 (亿)", B.total_debt_gbp_m[1792] / 100, 2.429, 3)
    pct("    1797 (亿)", B.total_debt_gbp_m[1797] / 100, 3.941, 3)
    pct("    1815 (亿)", B.total_debt_gbp_m[1815] / 100, 8.648, 3)
    pct("    1815, % of GDP", B.debt_pct_gdp[1815], 213.7)
    chk("a guinea: a pound and a shilling", F["cn_guinea"], [1, 1])
    chk("    21 shillings", F["cn_guinea"][0] * SHILLINGS + F["cn_guinea"][1], 21)
    chk("notes of £1 and £2", F["cn_partial"][2:4], [1, 2])


def hume_section(F, Y, T):
    chk("Political Discourses, 1752", Y["hm_oil"], 1752)
    chk("Louis XIV: raised three-sevenths, prices one (seventh)", F["hm_louis"], [3 / 7, 1])
    chk("1683; 30 and 50 livres the mark", F["hm_corn"], [1683, 30, 50])
    pct("silver in a livre: 30/50 (%)", 100 * F["hm_corn"][1] / F["hm_corn"][2], 60, 0)
    pct("corn in silver fell (%)", 100 * (1 - F["hm_corn"][1] / F["hm_corn"][2]), 40, 0)
    chk("four-fifths", F["hm_fourfifths"][0], 0.8)
    chk("fivefold", F["hm_fivefold"][0], 5)
    # ex:bullion-hume
    x0 = math.log(1 - F["hm_fourfifths"][0])
    pct("(1) x0 = ln(1/5)", x0, -1.609, 3)
    for t, v in zip(HUME_YEARS, [0.276, 0.357, 0.439, 0.590, 0.841]):
        pct(f"    M/Mbar after {t} years", hume(x0, KAPPA, t), v, 3)
    pct("    half-life (years)", half_life(KAPPA), 3.1)
    pct("(2) fivefold, after a year", hume(math.log(F["hm_fivefold"][0]), KAPPA, 1), 3.62, 2)
    lim = math.log(TARGET) / x0
    pct("(3) (1 - kappa)^2 <= ln 0.9 / ln 0.2", lim, 0.0655, 4)
    pct("    kappa >=", 1 - math.sqrt(lim), 0.74, 2)
    # paper
    chk("12 millions of paper, 18 of cash, 30 in all (万)", [x * 100 for x in F["hm_twelve"]], [1200, 1800, 3000])
    chk("    12 + 18", F["hm_twelve"][0] + F["hm_twelve"][1], F["hm_twelve"][2])
    chk("Scotland: near a million", F["hm_scotland"][0], 1)
    chk("    not a fifth of that", F["hm_fifth"][0], 0.2)
    pct("the Bank's coin, February 1797 (万)", T.coin_f[1797] * 100, 110, 0)


def equation(F, Y, T):
    chk("Thornton (1802)", Y["th_quicken"], 1802)
    chk("the alarm of 1793", Y["th_wanted"], 1793)
    chk("eight years before the Report: 1810 - 1802", 1810 - Y["th_quicken"], 8)
    # ex:bullion-velocity
    pct("(1) notes, end of February 1793 (万)", T.notes_f[1793] * 100, 1190, 0)
    need = T.notes_f[1793] * 100 / PANIC_V
    pct("    needed (万)", need, 1322, 0)
    pct("    more (万)", need - T.notes_f[1793] * 100, 132, 0)
    pct("(2) notes, end of August 1793 (万)", T.notes_a[1793] * 100, 1090, 0)
    pct("    share of the need (%)", 100 * T.notes_a[1793] * 100 / need, 82, 0)
    pct("    short (%)", 100 * (1 - T.notes_a[1793] * 100 / need), 18, 0)
    pct("(3) 1/0.9 - 1 (%)", 100 * (1 / PANIC_V - 1), 11, 0)


def restriction(F, Y, T, B, S):
    chk("one per cent", F["cn_onepct"][0], 1)
    chk("1773 to about the middle of 1799; £3 17s. 6d.", F["br_1773"], [1773, 1799, 3, 17, 6])
    chk("    two years after the stop: 1799 - 1797", F["br_1773"][1] - 1797, 2)
    chk("mint price £3 17s. 10½d.", F["br_mint"][:3], [3, 17, 10.5])
    assert lsd(*F["br_1773"][2:]) < MINT
    chk("Tooke: first twelve years about 4 per cent, next five about 20", F["tk_4and20"], [12, 4, 5, 20])
    chk("Cannan on Tooke: 5 per cent", F["cn_tooke5"][0], 5)
    P = B.wholesale_1821_25
    pct("wholesale 1797", P[1797], 106.2)
    pct("    1801", P[1801], 155.7)
    pct("    rise (%)", 100 * (P[1801] / P[1797] - 1), 46.6)
    pct("Silberling's premium 1800 (%)", S.pi[1800], 15.5)
    pct("    1801", S.pi[1801], 18.0)
    pct("prices in gold 1797-1801 (%)", 100 * decompose(B, S, 1797, 1801)["gold_change"], 29.1)
    chk("Tooke: 1799 and 1800", F["tk_harvests"], [1799, 1800])
    pct("wholesale 1802", P[1802], 122.2)
    chk("Tooke: money in 1799 and 1800 not increased", F["tk_notincreased"], [1799, 1800])
    chk("    compared with the three years ending in 1795", F["tk_probablyless"][0], 3)
    chk("    at least limit 1800 to 1799", F["tk_limit1799"], [1800, 1799])
    chk("Cannan: the Directors could reduce the rate to 4", F["cn_rate4"][0], 4)
    pct("notes, end of February 1799 (万)", T.notes_f[1799] * 100, 1300, 0)
    pct("    1800 (万)", T.notes_f[1800] * 100, 1680, 0)
    chk("1808", F["cn_1808"][0], 1808)
    for y, v in [(1808, 1300), (1809, 1550), (1810, 2010)]:
        pct(f"bills discounted {y} (万)", T.bills[y] * 100, v, 0)
    chk("1806, 1807 and 1808: as high as £4", F["br_mint"][3:], [1806, 1807, 1808, 4])


def report(F, Y, S):
    chk("1809: £4 9s. to £4 12s.; at £4 10s. about 15½ per cent", F["br_15half"], [4, 9, 4, 12, 4, 10, 15.5])
    chk("April 6, 1810: £4 6s., rather more than 10 per cent", F["br_april"], [6, 4, 6, 10])
    chk("    year", Y["br_april"], 1810)
    chk("1809: 16 to 20 per cent below par", F["br_16to20"], [1809, 16, 20])
    chk("August 29, 1809", [Y["cn_aug29"], F["cn_aug29"][0]], [1809, 29])
    chk("Horner, 1810", Y["cn_horner"], 1810)
    chk("February 19", F["cn_feb19"][0], 19)
    chk("June 8", F["cn_june8"][0], 8)
    # ex:bullion-mint
    chk("(1) mint price (pence)", MINT, 934.5)
    chk("    90s. (pence)", 90 * 12, 1080)
    pct("    premium (%)", 100 * premium(1080), 15.6)
    pct("    grains", grains(1080), 106.6)
    chk("    Cannan: about 107 grains", F["ci_1809"][3], 107)
    pct("(2) £4 10s. (%)", 100 * premium(lsd(4, 10, 0)), 15.57, 2)
    chk("    £4 6s. (pence)", lsd(4, 6, 0), 1032)
    pct("    premium (%)", 100 * premium(1032), 10.4)
    chk("(3) August 1813: 110s.", F["ci_gold1810"][3:5], [1813, 110])
    chk("    pence", 110 * 12, 1320)
    pct("    premium (%)", 100 * premium(1320), 41.3)
    pct("    grains", grains(1320), 87.3)
    chk("    Cannan: 87¼ grains", F["ci_gold1810"][6], 87.25)
    chk("    October 1816: 78s. 6d.", F["ci_1816"][:3], [1816, 78, 6])
    chk("    pence", lsd(0, 78, 6), 942)
    chk("    above the mint price (pence)", lsd(0, 78, 6) - MINT, 7.5)
    chk("    Cannan: 7½d.", F["ci_1816"][3], 7.5)
    pct("    premium (%)", 100 * premium(942), 0.80, 2)
    # the merchants
    chk("Hamburg: 3 to 4 per cent", F["br_goldsmid"], [3, 4])
    chk("1796 and 1797", F["br_never"], [1796, 1797])
    chk("1809: near 18 per cent below par", F["br_greffulhe"], [18, 1809])
    # the gold point
    chk("costs: 1½-2, 4, 5½-6; 1809: 4-7; 1797: 3½", F["br_costs"], [1.5, 2, 4, 5.5, 6, 1809, 4, 7, 1797, 3.5])
    chk("did not exceed 7 per cent", F["br_transport"][0], 7)
    chk("a fall of something more than 7 per cent", F["br_remains"][0], 7)
    chk("16 to 20 per cent below par", F["br_adequate"], [16, 20])
    ir = F["br_irving"]
    chk("Irving: 1805-1809", ir[0::2], [1805, 1806, 1807, 1808, 1809])
    chk("    balances (万)", [x / 1e4 for x in ir[1::2]], [661.6, 1043.7, 586.6, 1248.1, 1483.4])
    # ex:bullion-goldpoint
    for c, vals in zip(COSTS, [(10.7, 16.3), (14.9, 20.6)]):
        for d, v in zip(DELTAS, vals):
            pct(f"(1) c = {c:.3f}, delta = {d:.2f}: least premium (%)", 100 * min_premium(c, d), v)
    chk("    £4 9s. and £4 12s. (pence)", [lsd(4, 9, 0), lsd(4, 12, 0)], [1068, 1104])
    pct("    premium (%)", 100 * premium(1068), 14.3)
    pct("    ", 100 * premium(1104), 18.1)
    pct("(2) Silberling 1809: premium (%)", S.pi[1809], 14.5)
    pct("    exchange below par (%)", -S.dev[1809], 19.5)
    pct("    1 + pi", 1 + S.pi[1809] / 100, 1.145, 3)
    pct("    1 - delta", 1 + S.dev[1809] / 100, 0.805, 3)
    pct("    least cost (%)", 100 * min_cost(S.pi[1809] / 100, -S.dev[1809] / 100), 7.8)
    # real bills
    chk("from 5 to 4 per cent", F["br_5to4"], [5, 4])
    chk("to 3 per cent", F["br_3pct"][0], 3)
    chk("profit above five per cent", F["br_nolimit"][0], 5)
    chk("Thornton: more than five per cent", F["th_fivepct"][0], 5)
    chk("    six, five, four per cent", F["th_sixfour"], [6, 5, 4])
    # two drains
    chk("1793 (the Exchequer Bills)", [Y["br_exbills"], Y["br_1793remedy"]], [1793, 1793])
    chk("not before two years", F["br_twoyears"][0], 2)


def debate(F, Y, T):
    chk("Ricardo (1810)", Y["rc_mine"], 1810)
    chk("one year or five", F["rc_fiveyears"], [1, 5])
    chk("the embargoes of 1811", Y["sb_embargo"], 1811)
    chk("123¼ grains", F["ci_1809"][4], 123.25)
    chk("double or half; a year or two ago", F["cn_doubled"], [2, 0.5, 1, 2])
    # Cannan: in practice gold lost purchasing power too, only less than paper (sec:bullion-test numbers)
    B, S = boe(), silberling()
    G = gold_prices(B, S)
    pct("prices in gold 1797-1813 (%)", 100 * (G[1813] / G[1797] - 1), 17.3)
    quoted("    1809-1813: about a tenth lower", 1 - G[1813] / G[1809], 0.1, tol=0.02)
    chk("from 1810 to 1816", [Y["cn_admitted"], F["cn_admitted"][0]], [1810, 1816])
    chk("August 1810 to August 1813", F["cn_notincrease"], [1810, 1813])
    chk("    notes, end of August 1810 and 1813", [T.notes_a[1810], T.notes_a[1813]], [24.8, 24.8])
    chk("August 1813 to October 1814: 3½ millions (万)", F["ci_3half"], [1813, 1814, 3.5])
    chk("February 10, 1815", F["cn_vansittart1815"], [10, 1815])
    chk("May 6, 1811", [F["ci_may6"][0], Y["ci_may6"]], [6, 1811])
    chk("sixteen resolutions; the 14th and 16th; two years; four days", F["ci_sixteen"], [16, 14, 16, 2, 4])
    chk("151 to 75; 180 to 45", F["ci_divisions"], [151, 75, 180, 45])
    chk("May 13: seventeen counter-resolutions", F["cn_counter"], [13, 17])
    chk("May 15", F["cn_may15"][0], 15)
    chk("Lord King, 1811", Y["cn_king"], 1811)
    chk("more than a century after 1810", CANNAN_YEAR - 1810, 109)


def resumption(F, Y, T, B):
    chk("Cannan's account of the price of gold", F["ci_gold1810"],
        [1810, 84, 6, 1813, 110, 1, 87.25, 123.25, 1814, 85, 1815, 89, 107, 83, 1815, 78, 6, 83])
    chk("the treasure: nearly 8 to little over 2 millions (万)", [x * 100 for x in F["cn_treasure"]], [800, 200])
    chk("    February 1808 and 1815 in Table II", [T.coin_f[1808], T.coin_f[1815]], [7.9, 2.0])
    chk("80s.; £1 0s. 6d.", F["ci_80s"], [80, 1, 0, 6])
    chk("    80s. = a sovereign at £1 0s. 6d. ... (pence an ounce)", lsd(0, 80, 0), 960)
    pct("    above the mint price (%)", 100 * premium(960), 2.7)
    chk("41 promises, 40 redeemed", [F["cn_fortyone"][0], F["cn_fortyone"][2]], [41, 40])
    chk("December 2, 1816; £1 and £2 notes dated before 1812", F["cn_partial"], [2, 1816, 1, 2, 1812])
    pct("coin and bullion, end of August 1817 (万)", T.coin_a[1817] * 100, 1170, 0)
    pct("    end of February 1819 (万)", T.coin_f[1819] * 100, 420, 0)
    chk("early 1819", F["cn_folly"][0], 1819)
    chk("1810: 20 millions", F["cn_bills20"], [1810, 20])
    pct("bills 1817 (万)", T.bills[1817] * 100, 400, 0)
    pct("    1818 (万)", T.bills[1818] * 100, 430, 0)
    chk("10 millions of Exchequer Bills (万)", F["cn_exchequer"][0] * 100, 1000)
    chk("March 25, 1819", F["cn_directors1819"], [25, 1819])
    chk("rescinded in 1827", F["cn_rescinded"][0], 1827)
    chk("five years later", Y["cn_oneperson"] - F["cn_rescinded"][0], 5)
    chk("more than twenty years after 1810", Y["cn_oneperson"] - 1810, 22)
    chk("Peel's bill, 1819", Y["tk_peel"], 1819)
    chk("Ricardo's plan of 1811", F["cn_ingotplan"][0], 1811)
    chk("81s., 79s. 6d., 77s. 10½d.; May 1, 1823; May 1, 1821", F["ci_ingots"], [81, 79, 6, 77, 10.5, 1, 1823, 1, 1821])
    chk("    77s. 10½d. is the mint price", lsd(0, 77, 10.5), MINT)
    chk("February 1821: 19 per cent below August 1817", F["cn_19pct"], [1821, 19, 1817])
    pct("    Table II (%)", 100 * (1 - T.notes_f[1821] / T.notes_a[1817]), 19, 0)
    chk("    August 1817 was the highest", max(T.notes_f.max(), T.notes_a.max()), T.notes_a[1817])
    pct("coin and bullion, end of February 1821 (万)", T.coin_f[1821] * 100, 1190, 0)
    pct("notes, end of February 1821 (万)", T.notes_f[1821] * 100, 2390, 0)
    chk("half of its notes", F["cn_half"][0], 0.5)
    quoted("    coin / notes", T.coin_f[1821] / T.notes_f[1821], 0.5, tol=0.01)
    P = B.wholesale_1821_25
    for y, v in [(1813, 168.9), (1819, 128.1), (1821, 99.7), (1822, 87.9)]:
        pct(f"wholesale {y}", P[y], v)
    pct("    1813-1821 (%)", 100 * (P[1821] / P[1813] - 1), -41.0)
    chk("Tooke: 4 or 5 per cent; 30 and 40, even 50", F["tk_peel"], [4, 5, 30, 40, 50])
    pct("debt 1821 (亿)", B.total_debt_gbp_m[1821] / 100, 8.312, 3)
    pct("    % of GDP, 1819", B.debt_pct_gdp[1819], 176.8)
    pct("    1821", B.debt_pct_gdp[1821], 194.1)
    pct("the Bank's coin and bullion, end of August 1819 (万)", T.coin_a[1819] * 100, 360, 0)
    pct("    end of February 1821 (万)", T.coin_f[1821] * 100, 1190, 0)
    assert 3 < T.coin_f[1821] / T.coin_a[1819] < 3.5          # more than threefold
    gdp = B.total_debt_gbp_m / (B.debt_pct_gdp / 100)
    assert gdp[1821] < gdp[1819]          # nominal GDP shrank as prices fell


def sweden_case(F, Y, W):
    chk("periods of fiat money", F["fr_periods"], [1745, 76, 1809, 34, 1914, 24, 1931, 33])
    chk("the early 1740s", F["ed_war"][0], 1740)
    chk("1743: 9.5 million daler silvermynt, 10-12 per cent of GDP (万)", F["ed_1743"], [1743, 9.5, 10, 12])
    R = W.metal_reserves_sek / W.notes_sek
    pct("reserves / notes 1740 (%)", 100 * R[1740], 76.5)
    pct("    1745 (%)", 100 * R[1745], 9.6)
    chk("October 1745", F["ed_decree"][0], 1745)
    chk("until the reform of 1776", F["ed_fiat"][0], 1776)
    chk("the next two decades", F["fr_tandem"], [1745, 2])
    chk("the Seven Years' War 1757-1762", F["fr_wars"][3:], [1757, 1762])
    M = W.riksdaler_marks
    pct("riksdaler 1755 (marks)", M[1755], 40.8)
    pct("    1762", M[1762], 85.0)
    pct("    times", M[1762] / M[1755], 2.09, 2)
    pct("notes 1762 / 1755", W.notes_sek[1762] / W.notes_sek[1755], 3.27, 2)
    chk("1762-63: over 100 marks", F["ed_100"], [1762, 63, 100])
    chk("the Riksdag of 1765/6; 36 marks or 3 daler silvermynt", F["ed_caps"], [1765, 6, 36, 3])
    chk("ten years; the late 1760s", F["ed_gradually"], [10, 1760])
    pct("riksdaler 1764", M[1764], 91.7)
    pct("    1768", M[1768], 50.2)
    pct("    fall (%)", 100 * (1 - M[1768] / M[1764]), 45.3)
    pct("notes 1764-1768, fall (%)", 100 * (1 - W.notes_sek[1768] / W.notes_sek[1764]), 23.3)
    chk("1769; 36 marks", F["ed_1769"], [1769, 36])
    chk("1776: 50 per cent; 1 riksdaler = 6 daler silvermynt = 72 marks", F["ed_1776"], [50, 1, 6, 72])
    chk("    72 = 2 x 36", 2 * F["ed_caps"][2], F["ed_1776"][3])
    pct("1772-1776: lowest annual average", M.loc[1772:1776].min(), 71.6)
    pct("    highest", M.loc[1772:1776].max(), 82.1)
    chk("1777", F["fr_devalued"][0], 1777)
    pct("reserves / notes 1776 (%)", 100 * R[1776], 23.4)
    pct("    1777 (%)", 100 * R[1777], 42.4)
    chk("1924", F["fr_1924"][0], 1924)
    # ex:bullion-sweden, with the rounded numbers of the question
    m, p = 3.27, 2.09
    pct("(1) ln 3.27", math.log(m), 1.185, 3)
    pct("    ln 2.09", math.log(p), 0.737, 3)
    pct("    ln(V/T)", math.log(p) - math.log(m), -0.448, 3)
    chk("    0.737 - 1.185 (the rounded numbers of the text)", round(0.737 - 1.185, 3), -0.448)
    pct("    V/T", p / m, 0.64, 2)
    dn, dp = 0.233, 0.453
    pct("(2) ln(1 - 0.453)", math.log(1 - dp), -0.603, 3)
    pct("    ln(1 - 0.233)", math.log(1 - dn), -0.265, 3)
    pct("    ln(V/T)", math.log(1 - dp) - math.log(1 - dn), -0.34, 2)
    pct("    V/T", (1 - dp) / (1 - dn), 0.71, 2)
    pct("(3) riksdaler 1776", M[1776], 71.6)
    pct("    36 / 71.6 - 1 (%)", 100 * (36 / M[1776] - 1), -50, 0)
    pct("    72 / 71.6 - 1 (%)", 100 * (72 / M[1776] - 1), 0.6)


TABLE_YEARS = {1797: (3.9, 2.9, 1.069, None, 106.2, 102.2), 1801: (18.0, -11.7, 1.042, None, 155.7, 131.9),
               1808: (11.8, -8.6, 1.022, None, 144.5, 129.3), 1809: (14.5, -19.5, 0.922, 7.8, 155.0, 135.4),
               1810: (16.2, -18.0, 0.953, 4.7, 153.4, 132.0), 1811: (21.8, -30.9, 0.842, 15.8, 145.4, 119.4),
               1812: (32.4, -24.6, 0.998, 0.2, 163.7, 123.6), 1813: (40.9, -26.2, 1.040, None, 168.9, 119.9),
               1815: (15.7, -10.5, 1.036, None, 129.9, 112.3), 1819: (3.5, -0.8, 1.027, None, 128.1, 123.8),
               1821: (1.0, 3.5, 1.045, None, 99.7, 98.7)}


def test(F, Y, B, S, T):
    chk("Silberling (1919)", Y["sb_silver"], 1919)
    assert "British Financial Experience 1790--1830" in (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    chk("43/48 fine; 430 grains", [F["sb_430"][0], F["sb_430"][3]], [43 / 48, 430])
    chk("913.277 pence", F["sb_913"][0], 913.277)
    chk("par = ratio x 113.0016/48.7567 = 2.3177", F["si_par"][4], 2.3177)
    pct("    113.0016 / 48.7567", F["si_par"][1] / F["si_par"][0], 2.3177, 4)
    for y in S.index:
        assert abs(S.ratio[y] * F["si_par"][4] - S.par[y]) < 0.01, y
    chk("1790-1824: 35 years", [len(S), S.index[0], S.index[-1]], [35, 1790, 1824])
    pct("correlation of premium and exchange", corr(list(S.pi), list(S.dev)), -0.906, 3)
    ex = [y for y in S.index if y not in (1810, 1811, 1812)]
    pct("    without 1810-1812", corr([S.pi[y] for y in ex], [S.dev[y] for y in ex]), -0.926, 3)
    chk("Silberling: except 1810-12", F["sb_inverse"], [1810, 12])
    cost = {y: min_cost(S.pi[y] / 100, -S.dev[y] / 100) for y in S.index}
    chk("years with a positive bound", sorted(y for y in S.index if cost[y] > 0), [1795, 1809, 1810, 1811, 1812])
    chk("    negative in", sum(1 for y in S.index if cost[y] < 0), 30)
    for y, v in [(1795, 0.8), (1812, 0.2), (1809, 7.8), (1810, 4.7), (1811, 15.8)]:
        pct(f"    {y} (%)", 100 * cost[y], v)
    chk("witnesses: 4 to 7 per cent in 1809", F["br_costs"][5:8], [1809, 4, 7])
    chk("Silberling: about 3 per cent in 1797 to about 5½-7 per cent in 1810", F["si_specie"], [3, 1797, 5.5, 7, 1810])
    # tab:bullion-goldpoint
    G = gold_prices(B, S)
    P = B.wholesale_1821_25
    for y, (pi, dev, prod, c, p, g) in TABLE_YEARS.items():
        pct(f"table {y}: premium", S.pi[y], pi)
        pct("    exchange", S.dev[y], dev)
        pct("    (1 + pi)(1 - delta)", (1 + S.pi[y] / 100) * (1 + S.dev[y] / 100), prod, 3)
        if c is None:
            assert cost[y] <= 0, y
        else:
            pct("    least cost (%)", 100 * cost[y], c)
        pct("    wholesale", P[y], p)
        pct("    in gold", G[y], g)
    # the decomposition
    d = decompose(B, S, 1797, 1813)
    pct("1797-1813: wholesale, about (%)", 100 * d["change"], 59, 0)
    pct("    ln", d["total"], 0.464, 3)
    pct("    premium", d["prem"], 0.305, 3)
    pct("    share (%)", 100 * d["share"], 65.6)
    pct("    in gold (%)", 100 * d["gold_change"], 17.3)
    d = decompose(B, S, 1813, 1821)
    pct("1813-1821: wholesale (%)", 100 * d["change"], -41.0)
    pct("    ln", d["total"], -0.528, 3)
    pct("    premium", d["prem"], -0.333, 3)
    pct("    share (%)", 100 * d["share"], 63.1)
    pct("    in gold (%)", 100 * d["gold_change"], -17.7)
    d = decompose(B, S, 1801, 1813)
    pct("1801-1813: premium", d["prem"], 0.177, 3)
    pct("    in gold", d["gold"], -0.096, 3)
    d = decompose(B, S, 1813, 1819)
    pct("1813-1819: premium", d["prem"], -0.308, 3)
    pct("    in gold", d["gold"], 0.032, 3)
    # ex:bullion-decomp
    pct("(1) ln(168.9/106.2)", math.log(168.9 / 106.2), 0.464, 3)
    pct("    ln(1.409/1.039)", math.log(1.409 / 1.039), 0.305, 3)
    pct("    102.2 and 119.9", 106.2 / 1.039, 102.2)
    pct("    ", 168.9 / 1.409, 119.9)
    pct("(2) ln 1.409 / 0.464 (%)", 100 * math.log(1 + S.pi[1813] / 100) / decompose(B, S, 1797, 1813)["total"], 73.9)
    d = decompose(B, S, 1819, 1821)
    pct("(3) 1819-1821: wholesale (%)", 100 * d["change"], -22.2)
    pct("    ln", -d["total"], 0.251, 3)
    pct("    premium: ln(1.035/1.010)", -d["prem"], 0.0245, 4)
    # the share and the price in gold, from the rounded numbers of the question
    pct("    share (%)", 100 * math.log(1.035 / 1.010) / -math.log(99.7 / 128.1), 9.8)
    pct("    in gold (%)", 100 * ((99.7 / 1.010) / (128.1 / 1.035) - 1), -20.2)
    quoted("    nine tenths in gold", 1 - d["share"], 0.9, tol=0.01)
    d = decompose(B, S, 1797, 1801)
    pct("1797-1801: wholesale (%)", 100 * d["change"], 46.6)
    pct("    in gold (%)", 100 * d["gold_change"], 29.1)
    quoted("    mostly in gold", d["gold"] / d["total"], 0.67, tol=0.01)
    # the pitfall
    quoted("highest wholesale price of the Restriction against 1797: about six tenths",
           P.loc[1797:1821].max() / P[1797] - 1, 0.6, tol=0.01)
    assert P[1821] < P[1797]
    for a, b in [(1797, 1813), (1813, 1821)]:
        quoted(f"    about two thirds from the premium, {a}-{b}", decompose(B, S, a, b)["share"], 2 / 3, tol=0.04)
    # notes and the premium
    for y, n, pi in [(1810, 2480, 16.2), (1813, 2480, 40.9), (1814, 2840, 24.1)]:
        pct(f"notes, end of August {y} (万)", T.notes_a[y] * 100, n, 0)
        pct("    premium (%)", S.pi[y], pi)
    # the measures
    pct("premium 1792 (%)", S.pi[1792], 6.2)
    pct("    1796 (%)", S.pi[1796], 8.6)
    pct("mean premium 1797-1808 (%)", S.pi.loc[1797:1808].mean(), 9.9)
    pct("    1809-1813 (%)", S.pi.loc[1809:1813].mean(), 25.2)
    chk("Tooke: about 4 and about 20 per cent", [F["tk_4and20"][1], F["tk_4and20"][3]], [4, 20])
    chk("Jevons in Cannan's Table I: highest in 1810, 164", [T.jevons.idxmax(), T.jevons.max()], [1810, 164])
    chk("Gayer, Rostow and Schwartz: highest in 1813", P.loc[1790:1824].idxmax(), 1813)
    chk("the editor: 1813-14, not 1810", F["sb_taylor"], [1813, 14, 1810])
    C = B.cpi_2015
    pct("CPI 1797-1813 (%)", 100 * (C[1813] / C[1797] - 1), 73.3)
    pct("    1813-1821 (%)", 100 * (C[1821] / C[1813] - 1), -31.4)


def deeper(F, Y, S, T, W):
    df = _rows().set_index("id")
    chk("first edition, 1752", Y["h1_fourparts"], 1752)
    chk("four parts; four-fold", [F["h1_fourparts"][0], F["h1_fourfold"][0]], [4, 4])
    chk("later: four-fifths; fivefold", [F["hm_fourfifths"][0], F["hm_fivefold"][0]], [0.8, 5])
    chk("three sevenths in the first edition", F["h1_louis"][0], 3 / 7)
    chk("1811: 180 votes", [Y["ci_divisions"], F["ci_divisions"][2]], [1811, 180])
    assert "'1 80'" in df.loc["ci_divisions", "note"]
    chk("the Commons' committee of 1828 (Table I, columns 1 and 2)",
        int(re.search(r"Expenditure, (\d{4})", df.loc["ci_t1_exp", "note"]).group(1)), 1828)
    assert "Fourth Report" in df.loc["ci_t1_exp", "note"]
    chk("the Bank-Charter Committee of 1832 (the bills)",
        int(re.search(r"Committee of (\d{4})", df.loc["ci_t1_bills", "note"]).group(1)), 1832)
    chk("Silberling's row for 1813", [S.paper[1813], S.gold[1813], S.d_pence[1813], S.pi[1813]], [81.2, 56.2, 23.0, 40.9])
    pct("    23.0 / 56.2 (%)", 100 * S.d_pence[1813] / S.gold[1813], 40.9)
    pct("    81.2 - 56.2", S.paper[1813] - S.gold[1813], 25.0)
    pct("    25.0 / 56.2 (%)", 100 * (S.paper[1813] - S.gold[1813]) / S.gold[1813], 44.5)
    pct("    56.2 + 23.0", S.gold[1813] + S.d_pence[1813], 79.2)
    chk("silver highest in 1813, two years after Jevons", F["sb_max"], [1813, 2])
    chk("    Jevons highest in 1810: three years", F["sb_max"][0] - T.jevons.idxmax(), 3)
    chk("Tooke: 1797-1814; 50 to 100 per cent", F["tk_50to100"], [1797, 1814, 50, 100])
    meta = load_snapshot("riksbank_sweden_1740_1777")[1]
    assert "1 daler silvermynt = 1/6 SEK" in meta["series"]
    chk("notes 1743 (SEK)", round(W.notes_sek[1743]), 2_380_216)
    pct("    in daler silvermynt (万)", W.notes_sek[1743] * 6 / 1e4, 1428, 0)
    chk("Edvinsson: 9.5 million (万)", F["ed_1743"][1] * 100, 950)


def legacy(F, Y):
    chk("the usury limit, 5 per cent", F["th_fivepct"][0], 5)
    chk("Cannan, 1919", CANNAN_YEAR, 1919)
    chk("the war of 1914-18", F["cn_1914"], [1914, 18])
    chk("100 per cent in thirteen years; 1810", F["cn_trifling"], [100, 13, 1810])
    chk("    1810 - 13 = 1797", F["cn_trifling"][2] - F["cn_trifling"][1], 1797)
    chk("Bank of France: 6,000 to 30,500 million francs (亿)", [x / 100 for x in F["cn_france"][:2]], [60, 305])
    chk("Italy: 2,500 to over 8,000 millions (亿)", [x / 100 for x in F["cn_france"][2:]], [25, 80])


def takeaways_and_selfcheck(F, Y, B, S, T, W):
    pct("half-life at kappa = 0.2", half_life(KAPPA), 3.1)
    pct("February 1797: coin and notes (万)", T.coin_f[1797] * 100, 110, 0)
    pct("    ", T.notes_f[1797] * 100, 970, 0)
    chk("24 years", F["ci_ingots"][8] - 1797, 24)
    pct("90s.: premium (%)", 100 * premium(1080), 15.6)
    chk("16-20 per cent", F["br_16to20"][1:], [16, 20])
    chk("7 per cent; 5 per cent", [F["br_transport"][0], F["br_nolimit"][0]], [7, 5])
    chk("151 to 75, 180 to 45", F["ci_divisions"], [151, 75, 180, 45])
    pct("premium 1810 and 1813 (%)", S.pi[1810], 16.2)
    pct("    ", S.pi[1813], 40.9)
    pct("1811: least cost (%)", 100 * min_cost(S.pi[1811] / 100, -S.dev[1811] / 100), 15.8)
    chk("19 per cent", F["cn_19pct"][1], 19)
    M = W.riksdaler_marks
    pct("Sweden 1764-1768: riksdaler (%)", 100 * (1 - M[1768] / M[1764]), 45.3)
    pct("    notes (%)", 100 * (1 - W.notes_sek[1768] / W.notes_sek[1764]), 23.3)
    chk("1776: by half", F["ed_1776"][0], 50)
    # self-check answers
    x0 = math.log(SC1["m"])
    pct("1. x0", x0, -0.693, 3)
    pct("    x2", (1 - SC1["kappa"]) ** 2 * x0, -0.340, 3)
    pct("    M/Mbar (%)", 100 * hume(x0, SC1["kappa"], SC1["years"]), 71.2)
    pct("    half-life", half_life(SC1["kappa"]), 1.9)
    pct("2. least premium (%)", 100 * min_premium(SC2["c"], SC2["delta"]), 11.8)
    pct("    gold sent at 8 per cent (%)", 100 * (1 - SC2["c"]) / (1 + SC2["pi"]), 88.0)
    chk("    bill", 100 * (1 - SC2["delta"]), 85)
    chk("3. 95s. (pence)", SC3["shillings"] * 12, 1140)
    pct("    premium (%)", 100 * premium(1140), 22.0)
    pct("    grains", grains(1140), 101.0)
    pct("4. ln 1.2", math.log(1 + SC4["pi"]), 0.182, 3)
    pct("    ln 1.3", math.log(SC4["P"]), 0.262, 3)
    pct("    share (%)", 100 * math.log(1 + SC4["pi"]) / math.log(SC4["P"]), 69.5)
    pct("    in gold (%)", 100 * (SC4["P"] / (1 + SC4["pi"]) - 1), 8.3)
    chk("5. notes needed (万)", SC5["M"] / (1 - SC5["dv"]), 2500)
    chk("    PT falls (%)", 100 * SC5["dv"], 20)
    pct("6. 36/90 - 1 (%)", 100 * (SC6["par"] / SC6["price"] - 1), -60, 0)
    pct("    M1/M0", SC6["par"] / SC6["price"] / (1 - SC6["dv"]), 0.533, 3)
    pct("    fall (%)", 100 * (1 - SC6["par"] / SC6["price"] / (1 - SC6["dv"])), 46.7)


def main():
    df = _rows()
    F, Y = facts(), years()
    B, T, S, W = boe(), cannan(), silberling(), sweden()
    check_readings(df)
    check_text(df)
    opening(F, Y, T)
    world(F, Y, T, B)
    hume_section(F, Y, T)
    equation(F, Y, T)
    restriction(F, Y, T, B, S)
    report(F, Y, S)
    debate(F, Y, T)
    resumption(F, Y, T, B)
    sweden_case(F, Y, W)
    test(F, Y, B, S, T)
    deeper(F, Y, S, T, W)
    legacy(F, Y)
    takeaways_and_selfcheck(F, Y, B, S, T, W)
    print("all Chapter 19 checks passed")


if __name__ == "__main__":
    main()
