"""Chapter 25 (维克塞尔与费雪：自然利率与实际利率): every number and every quotation in zh/ch25_wicksell.tex.

    python3 checks/check_ch25.py

Inputs:
  wicksell_facts                       quotations of Wicksell's paper at York (Economic Journal, June 1907) and the
                                       British Association's report (1907), Interest and Prices (Kahn 1936, with
                                       Ohlin's introduction), Fisher (1911, and the printing of 1926; 1930), Keynes's
                                       Treatise on Money (1930, vol. II, two copies), Barsky and Summers (1985),
                                       Humphrey (1986), Berg and Jonung (1998), Lange (1942), the Riksbank's timeline,
                                       Waldenstroem (2014), Edvinsson and Soederberg (2010), Wikisource's author pages
                                       and the DNB (checked by data/fetch/verify_web_quotes.py)
  boe_millennium_gibson_1821_1913      Bank of England, A Millennium of Macroeconomic Data: the consol yield and
                                       Bank Rate (sheet A31), the wholesale and consumer price indices (sheet A47)
  riksbank_sweden_1870_1913            Sweden: the CPI of Edvinsson and Soederberg (Table I.A8.1) and the December
                                       values of the two rates (Table II.A6.3)
  riksbank_sweden_monthly_1870_1913    the Riksbank's discount rate and the long-term bond yield, monthly
                                       (Waldenstroem, Tables II.A6.9 and II.A6.10)
The figure module figsrc/fig_ch25.py imports the functions defined here.

What is checked here:
  1. readings   every number of the value column of wicksell_facts is read from its quotation (digits, English
                number words and fractions) or, for Barsky and Summers's Table 2, from the note (the page image)
  2. the text   every “…” in the chapter is the chapter's Chinese rendering of a quotation (TRANSLATIONS:
                rendering -> row or rows), an English quotation found word for word, or a term (ALLOW)
  3. numbers    every number of the text, section by section, with quoted()
  4. anchors    the paraphrase anchors `% 据: ...` name rows of wicksell_facts

Models (the chapter's key equations):
    the cumulative process (eq:wicksell-process), after Humphrey's (1986) equations (5) and (7) in discrete time:
        pi_t = kappa (r^n_t - i_t),   i_{t+1} = i_t + beta pi_t,   p_t = 100 ln P_t,  pi_t = p_{t+1} - p_t
        so g_t = r^n - i_t shrinks by the factor 1 - beta kappa a year, the prices rise by g_0 / beta in all, and
        i_t - i_0 = beta (p_t - p_0)
    the equation of exchange with deposits (eq:wicksell-exchange): M V + M' V' = P T (Fisher 1911)
    Fisher's relation (Chapter 3, eq:prices-fisher): 1 + i = (1 + r)(1 + pi)
    Gibson's regression: ln P_t = a + b * consol yield_t (+ e_t), in levels and in first differences, OLS
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

TEX = ROOT / "zh" / "ch25_wicksell.tex"
# Teaching inputs stated in the text
MODEL = dict(rn=5.0, i0=4.0, kappa=2.0, beta=0.1)     # ex:wicksell-model: 5% and 4% are Wicksell's, kappa and beta not
CYCLE = dict(T=120, period=40, low=5.0, high=6.0)     # fig:wicksell_model (b): the natural rate between 5% and 6%
SC1 = dict(rn=5.0, i0=4.5, kappa=2.0, beta=0.1)       # self-check 1
CONSOL = 3.0                                          # ex:wicksell-keynes (3): a yield of 3%, a teaching assumption
INFLATE = 5                                           # Barsky and Summers: standard errors inflated fivefold
# the samples of Gibson's regression (Barsky and Summers's Table 2) and of the Swedish correlations
SAMPLES = [(1821, 1913), (1821, 1871), (1872, 1913)]          # the rows of tab:wicksell-gibson
SWEDEN = (1874, 1913)


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
    df, meta = load_snapshot("wicksell_facts", dtype=str, keep_default_na=False)
    assert 25 in meta["used_in"]
    assert df["id"].is_unique
    return df


def num(x: str) -> float:
    """'5', '1/4', '.62', '0.403225'."""
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


def gibson() -> pd.DataFrame:
    """UK, 1821-1913: the consol yield and Bank Rate (%), the wholesale (2010 = 100) and consumer (2015 = 100)
    price indices; with lnP = ln(wholesale) and infl = 100 * the change of lnP."""
    df, m = load_snapshot("boe_millennium_gibson_1821_1913")
    assert 25 in m["used_in"] and "Bank of England" in m["license"]
    g = df.set_index("year")
    assert list(g.index) == list(range(1821, 1914)) and g.notna().all().all()
    g["lnP"] = np.log(g.uk_wholesale_2010_100)
    g["infl"] = 100 * g.lnP.diff()
    return g


def sweden() -> pd.DataFrame:
    """Sweden, 1870-1913: the CPI (1914 = 100) and the December values of the two rates (%)."""
    df, m = load_snapshot("riksbank_sweden_1870_1913")
    assert 25 in m["used_in"] and "Sveriges riksbank" in m["license"]
    assert "may not state Sveriges Riksbank as the source" in m["license"]
    return df.set_index("year")


def sweden_monthly() -> pd.DataFrame:
    """Sweden, monthly, 1870-1913: the discount rate and the long-term bond yield (%), indexed by 'YYYY-MM'."""
    df, m = load_snapshot("riksbank_sweden_monthly_1870_1913")
    assert 25 in m["used_in"] and "Sveriges riksbank" in m["license"]
    s = df.set_index("month")
    assert s.index.is_unique and s.index.is_monotonic_increasing
    return s


def annual(M: pd.DataFrame) -> pd.DataFrame:
    """The annual means of the monthly rates (the book's calculation)."""
    return M.groupby(M.index.str[:4].astype(int)).mean()


# ---------------------------------------------------------------------------------------------------
# The arithmetic of the chapter
def cumulative(r, i0: float, kappa: float, beta: float):
    """eq:wicksell-process. r: the natural rate for t = 0..T-1 (a number or an array). Returns (i, p, pi):
    i and p for t = 0..T (p_0 = 0), pi for t = 0..T-1."""
    r = np.asarray(r, dtype=float)
    T = r.size
    i, p, pi = np.empty(T + 1), np.empty(T + 1), np.empty(T)
    i[0], p[0] = i0, 0.0
    for t in range(T):
        pi[t] = kappa * (r[t] - i[t])
        p[t + 1] = p[t] + pi[t]
        i[t + 1] = i[t] + beta * pi[t]
    return i, p, pi


def natural_cycle(T: int = CYCLE["T"], period: int = CYCLE["period"], low: float = CYCLE["low"],
                  high: float = CYCLE["high"]) -> np.ndarray:
    """fig:wicksell_model (b): r^n_t = low + (high - low)/2 * (1 - cos(2 pi t / period))."""
    t = np.arange(T)
    return low + (high - low) / 2 * (1 - np.cos(2 * np.pi * t / period))


def regress(y: pd.Series, x: pd.Series, diff: bool = False) -> dict:
    """OLS of y on a constant and x (statsmodels), in levels or first differences: the slope, its standard error,
    R2, adjusted R2, the Durbin-Watson statistic and the number of observations."""
    import statsmodels.formula.api as smf
    from statsmodels.stats.stattools import durbin_watson

    d = pd.DataFrame({"y": y, "x": x})
    if diff:
        d = d.diff()
    d = d.dropna()
    m = smf.ols("y ~ x", data=d).fit()
    return dict(b=float(m.params["x"]), se=float(m.bse["x"]), r2=float(m.rsquared), r2adj=float(m.rsquared_adj),
                dw=float(durbin_watson(m.resid)), n=int(m.nobs))


def corr(a: pd.Series, b: pd.Series) -> float:
    d = pd.concat([a, b], axis=1).dropna()
    return float(np.corrcoef(d.iloc[:, 0], d.iloc[:, 1])[0, 1])


def discount(face: float, rate: float, months: int) -> float:
    """The cash a merchant gets for a bill: the face value less the interest at the yearly rate (%)."""
    return face * (1 - rate / 100 * months / 12)


# ---------------------------------------------------------------------------------------------------
# 1. Readings of the numbers
SMALL = {"a": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "twenty": 20, "fifty": 50, "seventy": 70}
ORDINAL = {"half": 2, "quarter": 4}
ROMAN = {"I": 1, "II": 2}


def cardinal(s: str) -> float:
    """An English cardinal: 'seven', 'fifty', 'a'."""
    total = 0.0
    for w in s.lower().replace("-", " ").split():
        total += SMALL[w]
    return total


def fraction(s: str) -> float:
    """'one-half', 'a quarter'."""
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
    if how == "fold":                         # 'fivefold'
        return [cardinal(phrase.removesuffix("fold"))]
    if how == "dashdec":                      # '0-893': the OCR prints the decimal point as '-'
        a, b = phrase.split("-")
        return [float(f"{a}.{b}")]
    if how == "roman":                        # 'World War I'
        return [float(ROMAN[phrase.split()[-1]])]
    raise ValueError(how)


FIGURES = re.compile(r"\d[\d,]*(?:\.\d+)?|\.\d+")      # '1,000', '8.15', and '.62' as Fisher's table prints it
EN, NUM, NOTE = "en", "num", "note"
# id -> [(phrase, how[, NOTE])], in order. A third element NOTE means the phrase is read from the note column (here:
# the page image of Barsky and Summers's Table 2, whose text layer drops points and brackets). Rows not listed are
# read with all the figures of the quotation.
READINGS = {
    "ej_bill3": [("3", NUM), ("a quarter", "frac"), ("1", NUM)],
    "ka_jumps": [("one-half", "frac"), ("one", EN)],
    "f30_variable": [("seven", EN), ("thirteen", EN)],
    "ke_893": [("0-893", "dashdec"), ("0-014", "dashdec"), ("1825", NUM), ("1924", NUM)],
    "ke2_893": [("0-893", "dashdec")],
    "bs_factor5": [("five", EN)],
    "bs_granger": [("fifty", EN), ("10", NUM), (".7", NUM), ("90", NUM), ("95", NUM)],   # not the 2 of 'R2'
    "bs_fivefold": [("fivefold", "fold")],
    "bs_ww1": [("World War I", "roman")],
    "bs_t2_lev": [(".38", NUM, NOTE), (".03", NUM, NOTE), ("0.44", NUM, NOTE), (".65", NUM, NOTE)],
    "bs_t2_dif": [(".16", NUM, NOTE), (".05", NUM, NOTE), ("1.71", NUM, NOTE), (".10", NUM, NOTE)],
    "bs_t2_lev1": [(".16", NUM, NOTE), (".06", NUM, NOTE), ("0.52", NUM, NOTE), (".11", NUM, NOTE)],
    "bs_t2_dif1": [(".14", NUM, NOTE), (".06", NUM, NOTE), ("1.77", NUM, NOTE), (".08", NUM, NOTE)],
    "bs_t2_lev2": [(".41", NUM, NOTE), (".05", NUM, NOTE), ("0.28", NUM, NOTE), (".67", NUM, NOTE)],
    "bs_t2_dif2": [(".24", NUM, NOTE), (".09", NUM, NOTE), ("1.50", NUM, NOTE), (".14", NUM, NOTE)],
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
    quoted("rows with values, each read from its quotation (or its note)", n, 89)
    # Table 2 of Barsky and Summers: the text layer has the coefficient and D-W of each line as the note reads them
    Q, N = quotes(), column("note")
    for rid in ("bs_t2_lev", "bs_t2_dif", "bs_t2_lev1", "bs_t2_dif1", "bs_t2_lev2", "bs_t2_dif2"):
        b, se, dw, r2 = facts()[rid]
        assert f"{b:.2f}".lstrip("0") in Q[rid] and f"{dw:.2f}" in Q[rid], rid
        assert "page image" in N[rid], rid


# ---------------------------------------------------------------------------------------------------
# 2. Every “…” of the text against the snapshot
# terms of the text, which are not quotations of the snapshot
ALLOW = {
    "吉布森悖论",       # the name (Keynes's “Gibson Paradox”, note of row ke_call)
    "自然",             # Ohlin's “natural” rate (note of row oh_natural)
    "概率误差",         # 'probable error' (note of row ke_893)
}
# the chapter's Chinese renderings of the quotations: rendering -> row (or rows)
TRANSLATIONS = {
    # opening
    "那么一切商品的价格都会涨、涨、再涨，没有任何限度": "ej_lower",
    "跌、跌、再跌，除了零以外没有限度": "ej_raise",
    "一般会发现，物价高并不对应着利率低，反过来也一样，倒是正好相反，利率与物价常常一起涨、一起跌": "ej_sauerbeck",
    "成了对我们理论的有力支持": "ej_support",
    "利率本身从来无所谓高低，只有同人们拿手里的钱能赚到的利润相比，才说得上高或低，而利润当然是会变的": "ej_relative",
    "但是升得不够": "f12_step2",
    # sec:wicksell-world, sec:wicksell-cumulative
    "物价为什么涨、为什么跌": "oh_mainproblem",
    "在一个纯粹的信用制度里，一切支付都靠银行账簿上的转账完成，银行可以随时按任何利率，哪怕是再低的利率，放出任何数量的贷款":
        "ej_pure",
    "永远不会停止": "ej_never",
    "一个新的物价水平已经形成，它又会成为将来一切计算与一切合同的基础": "ej_newlevel",
    "只会停在原地": "ej_remain",
    "银行的准备金会融化掉，它们的负债却很可能还增加了，这会逼着它们提高利率": "ej_melt",
    "可以说是被物价的变动以及随之而来的银行准备金状况的变化，拖在利润率的后面走": "ej_dragged",
    "最先提出这个理论的不是维克塞尔，而是远在他以前、在 19 世纪的头三分之一里写作的两位英国经济学家": "hu_notwicksell",
    "维克塞尔联系": "hu_leij",
    "当然不对": "hu_leij",
    "最终": "lg_ultimately",
    "起初": "lg_ultimately",
    # sec:wicksell-rule
    "显然应当看作货币科学的根本问题": "ej_fundamental",
    "只在于适当地操纵一般的银行利率，物价走低时就降低它，物价走高时就提高它": "ej_rule",
    "前一种情况下它会失去一切有利的生意，后一种情况下，很快资不抵债就是必然的结果": "ej_single",
    "仿佛有两个自由度": "ej_twodeg",
    "它可以设法让本国货币对商品的价值保持稳定，但那样就必然牺牲汇率的平价": "ej_steady",
    "它也可以设法让汇率严格保持平价，但那样它自己就管不了物价水平": "ej_par",
    # sec:wicksell-fisher
    "就像一座山坡，标志着从平坦的低地到平坦的高地的过渡": "f12_hill",
    "而且，法律与习俗武断地倾向于压低利率，助长了这种调整的不充分与迟缓": "f12_law",
    "被较高的名义利率迷惑，以为已经得到了相当高的利息，他们就扩大放款": "f12_beguiled",
    "七到十三倍": "f30_variable",
    "物价的上涨引起物价的上涨，只要利率落在它的正常水平后面，就一直如此": "f26_generates",
    "货币幻觉": "f30_illusion",
    "一元钱就是一元钱": "f30_dollar",
    "至少在长时期里，利率跟着物价的变动走": "f30_follow",
    "偶然结果": "f30_accidental",
    # sec:wicksell-test
    "整个数量经济学领域里确立得最完全的经验事实之一，虽然理论经济学家大多不理会它": "ke_fact",
    "黏": "ke_sticky",
    "如果市场利率与自然利率同向变动，却总是落在它后面，那么物价水平的变动即使在相当长的时期里，也会倾向于与利率的变动同向":
        "ke_lag",
    "恐怕必须毫无保留地否定": "ke_rejected",
    "恰恰相反": "ke_contrary",
    "在金本位下，物价水平是黄金实际价格的倒数": "bs_recip",
    "吉布森悖论仍然是一个没有理论解释的经验现象": "bs_fsquote",
    # sec:wicksell-legacy
    "近几十年通行法定货币本位，吉布森相关就蒸发了": "bs_fiat",
    # the deeper box
    "确立得最完全的经验事实之一": ("ke_fact", "bs_misquote"),
    "within the whole field": "ke_fact",
    "in the whole field": "bs_misquote",
}
# the renderings that are kept literally close to the source: words of the source that must be there
KEYWORDS = {
    "ej_lower": ["prices of all commodities would rise and rise and rise without any limit whatever"],
    "ej_raise": ["fall and fall and fall without any limit except Zero"],
    "ej_sauerbeck": ["generally find that high prices do not correspond with a low rate of interest, and vice versa",
                     "it rather comes the opposite way", "very often rising and falling together"],
    "ej_support": ["positive support of our"],
    "ej_relative": ["never high or low in itself", "only in relation to the profit which people can make with the money",
                    "this, of course, varies"],
    "ej_pure": ["In a pure system of credit", "transference in the bank-books",
                "any amount of loans at any, however diminutive, rate of interest"],
    "ej_newlevel": ["a new level of prices has formed itself", "basis for all calculations for the future, and all contracts"],
    "ej_melt": ["bank reserves will melt away", "liabilities very likely has increased",
                "force them to raise their rate of interest"],
    "ej_dragged": ["as it were, dragged after the rate of profit", "consequent changes in the state of bank reserve"],
    "ej_rule": ["proper manipulation of general bank-rates", "lowering them when prices are getting low",
                "raising them when prices are getting high"],
    "ej_single": ["lose all profitable business", "speedy insolvency would be the inevitable consequence"],
    "ej_steady": ["keep the value of its money steady towards the commodities", "necessarily sacrifices the parity"],
    "ej_par": ["keep its exchanges strictly at par", "has of itself no power over the level of prices"],
    "f12_law": ["inadequacy and tardiness of adjustment are fostered, moreover, by law and custom",
                "arbitrarily tend to keep down the rate of interest"],
    "f12_beguiled": ["Beguiled by the higher nominal rates", "fairly high interest is being realized", "extend their loans"],
    "f30_follow": ["over long periods at least, interest rates follow price movements"],
    "ke_lag": ["moves in the same direction as the natural-rate of interest but always lags behind it",
               "even over longish periods, to be in the same direction"],
    "bs_recip": ["Under a gold standard, the price level is the reciprocal of the real price of gold"],
    "bs_fsquote": ["remains an empirical phenomenon without a theoretical explanation"],
    "bs_fiat": ["The Gibson correlation evaporates in recent decades when a fiat money standard prevailed"],
    "f12_step2": ["rises, but not sufficiently"],
    "oh_mainproblem": ["Why do prices rise or fall"],
    "ej_never": ["can never cease"],
    "ej_remain": ["it will simply remain where it is"],
    "hu_leij": ["Certainly it is not true", "“Wicksell Connection,”"],
    "hu_notwicksell": ["it was not Knut Wicksell but rather two British economists",
                       "in the first third of the nineteenth century who first presented the theory"],
    "lg_ultimately": ["“ultimately”", "“in the first place.”"],
    "ej_fundamental": ["evidently is to be regarded as the fundamental problem of monetary science"],
    "ej_twodeg": ["as it were, two degrees of freedom"],
    "f12_hill": ["just as a hill marks the transition between flat lowlands and flat highlands"],
    "f30_variable": ["from seven to thirteen times as variable"],
    "f26_generates": ["Rise of prices generates rise of prices", "as long as the interest rate lags behind its normal"],
    "f30_illusion": ["“the money illusion,”"],
    "f30_dollar": ["“a dollar is a dollar!”"],
    "f30_accidental": ["accidental consequence"],
    "ke_fact": ["most completely established empirical facts within the whole field of quantitative economics",
                "theoretical economists have mostly ignored it"],
    "ke_sticky": ["very “sticky”"],
    "ke_rejected": ["must, I am afraid, be rejected unreservedly"],
    "ke_contrary": ["quite the contrary"],
    "bs_misquote": ["most completely established empirical facts in the whole field"],
}


def tex_text() -> str:
    return "\n".join(l for l in TEX.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("%"))


def say(*phrases: str) -> None:
    """The phrases are in the text (the numbers of a check are the numbers the text prints)."""
    t = tex_text()
    for s in phrases:
        assert s in t, f"not in the text: {s!r}"


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
            if q.isascii():                   # an English quotation is found word for word
                assert q in Q[rid], (q, rid)
    stale = (set(ALLOW) | set(TRANSLATIONS)) - used
    assert not stale, f"listed but not in the text: {sorted(stale)}"
    for rid, words in KEYWORDS.items():
        for w in words:
            assert w in Q[rid], f"{rid}: {w!r} not in the quotation"
    N = column("note")
    assert "“Gibson Paradox”" in N["ke_call"]                              # “吉布森悖论”
    assert "“natural”" in N["oh_natural"]                                   # “自然”
    assert "probable error" in N["ke_893"]                                  # “概率误差”
    print(f"ok {n} quotations of the text found in the snapshot (or listed as exceptions)")


# ---------------------------------------------------------------------------------------------------
# 3. Numbers, section by section
def guide(F, Y):
    say("维克塞尔（1898）", "费雪（1896）", "费雪（1911）")
    chk("Geldzins und Gueterpreise, Jena 1898", F["ej_jena"], [1898])
    chk("The Purchasing Power of Money, 1911", Y["f12_step2"], 1911)


def opening(F, Y, Q, G):
    chk("3 August 1906 was a Friday (weekday 4)", date(1906, 8, 3).weekday(), 4)
    chk("    the report: Friday, August 3", F["ba_friday"], [3])
    assert Q["ba_friday"] == "FRIDAY, AUGUST 3." and "August 1906" in Q["ba_meeting"]
    assert "SEVENTY-SIXTH" in Q["ba_seventysixth"]
    chk("    the 76th meeting", SMALL["seventy"] + 6, 76)
    say("1906 年 8 月 3 日是个星期五", "第 76 届年会")
    assert "ECONOMIC SCIENCE AND STATISTICS" in Q["ba_section"]                       # 经济科学与统计组
    assert "the first paper" in column("note")["ba_title"]                           # 第一篇论文
    assert Q["ba_title"] == "The Influence of the Rate of Interest on Prices."      # 《利率对物价的影响》
    chk("Wicksell 1851-1926", F["ws_wicksell"], [1851, 1926])
    assert Q["ws_wicksell_who"] == "Swedish economist"
    chk("one point below and above (%)", F["ej_lower"] + F["ej_raise"], [1, 1])
    say("比如说 1 个百分点", "把利率提高 1 个百分点")
    assert "Sauerbeck" in Q["ej_sauerbeck"] and "Journal of the Statistical Society" in Q["ej_sauerbeck"]
    # 1873-1896: the gold price of the pound unchanged (Chapters 23 and 24), wholesale prices and the consol yield fell
    for col in ("uk_wholesale_2010_100", "consol_yield"):
        assert G.loc[1896, col] < G.loc[1873, col], col
    chk("    more than twenty years", 1896 - 1873, 23)
    say("一起跌了二十多年")
    chk("Palgrave 1827-1919", F["ws_palgrave"], [1827, 1919])
    assert "Editor of The Economist" in Q["ws_palgrave_who"]                          # 他编过《经济学人》
    assert Q["ba_specie"].startswith("2. ")                                           # 排在第二
    chk("Edgeworth 1845-1926", F["ws_edgeworth"], [1845, 1926])
    assert "EDITED BY F. Y. EDGEWORTH" == Q["ej_editor"]                              # 《经济学杂志》的主编
    chk("five years later: Fisher (1911)", Y["f12_step2"] - 1906, 5)


def world(F, Y, Q):
    assert "Tooke" in column("note")["oh_tooke"] and "falling prices" in Q["oh_tooke"]
    chk("the article of 1897 (Band 68, pp. 228-243)", F["f12_wicksell"], [1897, 68, 228, 243])
    assert "Der Bankzins als Regulator der Warenpreise" in Q["f26_bankzins"]          # 《作为商品价格调节器的银行利率》
    assert "Conrad" in Q["ej_jena"]                                                   # Conrad 的《国民经济学年鉴》
    chk("    the next year: Jena 1898", F["ej_jena"][0] - 1897, 1)
    assert Q["ka_preface"] == "January 1898." and "Upsala" in column("note")["ka_preface"]
    chk("the translation, 1936", Y["ka_title"], 1936)
    assert "KAHN" in Q["ka_title"] and "OHLIN" in Q["ka_ohlin"]
    say("序言写于 1898 年 1 月的乌普萨拉", "英译本要到 1936 年才出版")


def cumulative_sec(F, Y, Q):
    # the bill
    chk("the bill: £100 at three months", F["ej_bill100"], [100])
    assert "three months" in Q["ej_bill100"]
    chk("    at 4%: interest (£)", 100 - discount(100, F["ej_bill4"][0], 3), 1)
    chk("    the cash price (£)", discount(100, 4, 3), F["ej_bill99"][0])
    rise = discount(100, F["ej_bill3"][0], 3) / discount(100, 4, 3) - 1
    pct("    at 3%: the cash price rises (%), 'a quarter of 1 per cent'", 100 * rise,
        F["ej_bill3"][1] * F["ej_bill3"][2], 2)
    chk("    a quarter", F["ej_bill3"][1], 0.25)
    # the railway
    chk("4% instead of 5%", F["ej_rail"], [4, 5])
    chk("£5 a year at 5% (£)", 5 / 0.05, F["ej_125"][4], tol=1e-9)
    chk("    at 4% (£)", 5 / 0.04, F["ej_125"][2], tol=1e-9)
    chk("    up to ... more (%)", 100 * (125 / 100 - 1), F["ej_125"][0])
    say("按 5\\% 算值 100 英镑。按 4\\% 算，它值 125 英镑", "最多可以比从前多付 25\\%")
    chk("the money rate jumps by one-half or one point", F["ka_jumps"], [0.5, 1])
    say("一次跳半个或一个百分点")
    assert "neutral equilibrium" in Q["ka_cylinder"] and "pendulum" in Q["ka_pendulum"]
    assert column("juan")["ka_neutral"].startswith("ch. 8")
    say("书的第 8 章又说")


def model(F):
    rn, i0, k, b = MODEL["rn"], MODEL["i0"], MODEL["kappa"], MODEL["beta"]
    chk("Wicksell's 4% and 5% (Humphrey)", F["hu_4pct"], [i0, rn])
    chk("Humphrey's equations (5) and (7)", F["hu_eq5"] + F["hu_eq7"], [5, 7])
    # (1) a pure credit system: beta = 0
    i, p, pi = cumulative(np.full(20, rn), i0, k, 0.0)
    chk("(1) beta = 0: inflation every year (%)", pi, [2.0] * 20)
    chk("    after 20 years p is higher by", p[20], 40)
    pct("    P is ... times", math.exp(p[20] / 100), 1.49, 2)
    # (2) beta = 0.1
    i, p, pi = cumulative(np.full(200, rn), i0, k, b)
    chk("(2) inflation in years 0, 1, 2 (%)", pi[:3], [2, 1.6, 1.28])
    chk("    the rate in years 1, 2, 3 (%)", i[1:4], [4.2, 4.36, 4.488])
    chk("    the gap shrinks by the factor 1 - beta kappa", 1 - b * k, 0.8)
    g = rn - i
    chk("    g_{t+1} / g_t, the first ten years", list(g[1:11] / g[:10]), [0.8] * 10, tol=1e-9)
    chk("    in three years by half: 0.8^3", 0.8 ** 3, 0.512)
    assert 0.8 ** 3 > 0.5 > 0.8 ** 4                                     # 约 3 年缩小一半
    # (3) the total rise
    chk("(3) the total rise g_0 / beta", (rn - i0) / b, 10)
    chk("    the sum of the inflation of 200 years", pi.sum(), 10, tol=1e-9)
    pct("    the price level rises (%)", 100 * (math.exp(0.1) - 1), 10.5, 1)
    pct("    the rate back at (%)", i[-1], 5.0, 6)
    # (4) i_t - i_0 = beta (p_t - p_0), every year
    chk("(4) largest |i_t - i_0 - beta p_t|", np.abs(i - i0 - b * p).max(), 0, tol=1e-9)
    chk("    the rate rises by 1 point, p by 10", [i[-1] - i0, p[-1]], [1, 10], tol=1e-9)
    say("$\\pi_0=2$，$i_1=4+0.1\\times2=4.2$", "$i_2=4.36$", "$\\pi_2=1.28$，$i_3=4.488$", "$0.8^{3}=0.512$",
        "$e^{0.4}\\approx1.49$", "$e^{0.1}-1\\approx10.5\\%$")
    # fig:wicksell_model (b): a natural rate between 5% and 6% with a period of 40 years
    r = natural_cycle()
    chk("(b) the natural rate between (%)", [r.min(), r.max()], [CYCLE["low"], CYCLE["high"]], tol=1e-9)
    i, p, pi = cumulative(r, CYCLE["low"], k, b)
    T = CYCLE["T"]
    pct("    120 years: corr(market rate, price level)", corr(pd.Series(i[:T]), pd.Series(p[:T])), 1.0, 2)
    chk("    corr(market rate, inflation), about -0.1", corr(pd.Series(i[:T]), pd.Series(pi)), -0.1, tol=0.05)
    say("自然利率在 5\\% 与 6\\% 之间以 40 年为周期起伏", "在 120 年里", "$-0.1$ 左右")


def history(F, Y, Q):
    chk("1851-73", F["ka_1851"], [1851, 73])
    assert "Crimean War" in Q["ka_wars"] and "American Civil War" in Q["ka_wars"]
    assert "Germany" in column("note")["ka_wars"]                                    # 德国的几场战争
    assert "Both of these reasons".lower() in Q["ka_reasons"].lower()
    chk("Humphrey: the model more than ... years old", F["hu_70"], [70])
    say("已经有 70 多年的历史")
    chk("Thornton 1802, 1811; Joplin 1823, 1828, 1832", F["hu_tj"], [1802, 1811, 1823, 1828, 1832])
    say("在 1802 年与 1811 年", "在 1823、1828 与 1832 年")
    chk("Joplin: born about 1790, died 1847", F["dnb_joplin"], [1790, 1847, 1790])
    assert "1790?" in Q["dnb_joplin"] and "born about 1790" in Q["dnb_joplin"]
    say("Thomas Joplin，约 1790—1847")
    chk("Thornton's chapter 10 (Humphrey)", F["hu_ch10"], [10])


def rule(F, Y, Q):
    assert column("juan")["ka_rule"].startswith("ch. 12")
    say("《利息与价格》第 12 章说")
    chk("Berg and Jonung: 1898", F["bj_1898"], [1898])
    chk("    their paper, December 1998", F["bj_date"], [1998])
    assert "P.S." in column("juan")["ej_twodeg"] and "P.S." in column("juan")["ej_choice"]     # 附记


def fisher(F, Y, Q):
    chk("The Theory of Interest, 1930", Y["f30_debated"], 1930)
    assert "MV+M'V'=PT" in Q["f12_equation"] and "M'" in Q["f12_mprime"]
    # 3% a year; 5% real
    a = F["f12_3pct"]
    chk("prices rise 3%; $100; 5%; $103; $108.15", [a[0], a[1], a[2], a[3], a[6]], [3, 100, 5, 103, 108.15])
    chk("    103 x 1.05", 103 * 1.05, 108.15, tol=1e-9)
    chk("    8.15%", F["f12_815"], [5, 8.15])
    chk("    eq:prices-fisher: 1.05 x 1.03", 1.05 * 1.03, 1.0815, tol=1e-12)
    chk("    the rate may reach 6%, later 7%", F["f12_67"], [6, 7])
    pct("    real: 1.06/1.03 - 1 (%)", 100 * (1.06 / 1.03 - 1), 2.9, 1)
    pct("    real: 1.07/1.03 - 1 (%)", 100 * (1.07 / 1.03 - 1), 3.9, 1)
    # falling prices
    chk("$97 buys as much as $100", F["f12_97"], [97, 100])
    chk("    97 x 1.05", 97 * 1.05, F["f12_10185"][0], tol=1e-9)
    chk("    1.85%, less than 2%, instead of 5%", F["f12_185"], [1.85, 2, 5])
    chk("    1.05 x 0.97", 1.05 * 0.97, 1.0185, tol=1e-12)
    chk("    far above 2%", F["f12_far"], [2])
    say("名义利率应当是 8\\% 出头", "$103\\times1.05=108.15$", "$97\\times1.05=101.85$", "$1.06/1.03-1=2.9\\%$",
        "$1.07/1.03-1=3.9\\%$", "利率本该降到不到 2\\%")
    # Table 14
    t = F["f30_table14"]
    rows = {c: t[3 * j:3 * j + 3] for j, c in enumerate(["London", "New York", "Berlin", "Calcutta", "Tokyo"])}
    for c in rows:
        assert c in Q["f30_table14"]
    tab = {"伦敦": (11, 0.62, 6.1), "纽约": (8, 1.07, 8.5), "柏林": (7, 0.73, 5.0), "加尔各答": (11, 0.57, 7.5),
           "东京": (5, 0.69, 7.0)}
    for (zh, v), (en, w) in zip(tab.items(), rows.items()):
        chk(f"tab:wicksell-fisher14 {en}", list(v), w)
        say(f"{zh} & {v[0]} & {v[1]:.2f} & {v[2]:.1f} \\\\")
    ratios = [w[2] / w[1] for w in rows.values()]
    for r_, e in zip(ratios, [9.8, 7.9, 6.8, 13.2, 10.1]):
        pct("    real / market", r_, e, 1)
    chk("    'seven to thirteen times': the ratios rounded", [round(min(ratios)), round(max(ratios))],
        F["f30_variable"])
    say("伦敦 $6.1/0.62=9.8$，纽约 7.9，柏林 6.8，加尔各答 13.2，东京 10.1")
    # the five steps; the footnote
    assert Q["f12_step5"].endswith("phenomenon No. 1 is repeated.")
    assert "Fetter" in Q["f12_step3"]
    chk("twenty years later: 1911 -> 1930", Y["f30_debated"] - Y["f12_step2"], 19)
    chk("Germany: nearly minus 100%", F["f30_germany"], [100])
    chk("1898-1924: r = 0.980, 28 years, 9.3 years", F["f30_r980"], [1898, 1924, 0.980, 28, 9.3])
    say("英国 1898—1924 年，相关系数最高可达 0.98", "摊到 28 年里，加权的平均落后 9.3 年")
    chk("1820-1864: the lowest correlations", F["f30_1820"], [1820, 1864])
    # the pitfall
    chk("London 1852-1857", F["f30_1852"], [1852, 1857])
    chk("    the market rate averaged (%)", F["f30_47"], [4.7])
    assert "less than" in Q["f30_47"] and "higher than in any subsequent or in any previous period" in Q["f30_47"]


def test(F, Y, Q, G):
    chk("Gibson: Bankers' Magazine, January 1923 and November 1926", F["ke_bm"], [1923, 1926])
    chk("    Fisher: January 1923, p. 15", F["f30_gibson"], [1923, 15])
    assert "more than a hundred years" in Q["ke_corr"]                                    # 一百多年
    chk("Coates: 1825-1924", F["ke_coates"], [1825, 1924])
    v = F["ke_893"]
    pct("    the correlation 0.893 (printed 0.89)", v[0], 0.89, 2)
    chk("    the probable error; the years", v[1:], [0.014, 1825, 1924])
    chk("    the second copy", F["ke2_893"], [0.893])
    chk("Keynes: fell 1873-1896, rose 1896-1900", F["ke_1873"], [1873, 1896, 1896, 1900])
    # the recomputation (fig:wicksell_gibson)
    pct("corr(ln WPI, consol yield), 1821-1913", corr(G.lnP, G.consol_yield), 0.77, 2)
    pct("    from 1825", corr(G.lnP.loc[1825:], G.consol_yield.loc[1825:]), 0.80, 2)
    pct("corr(inflation, consol yield), 1822-1913", corr(G.infl, G.consol_yield), -0.07, 2)
    pct("corr(ln WPI, Bank Rate, annual average)", corr(G.lnP, G.bank_rate_avg), 0.51, 2)
    say("相关系数是 0.77，算到 1825 年起是 0.80", "只有 $-0.07$", "相关只有 0.51")
    chk("Barsky and Summers: 1730-1930", F["bs_1730"], [1730, 1930])
    assert "long-term rate" in Q["ke_peake"] and "Peake" in column("note")["ke_peake"]
    # spurious?
    chk("Benjamin and Kochin (1984)", F["bs_bk"], [1984])
    chk("    standard errors underestimated by a factor of", F["bs_factor5"], [INFLATE])
    chk("Granger and Newbold (1977)", F["bs_diff"], [1977])
    chk("1821 to 1913, levels and first differences", F["bs_both"], [1821, 1913])
    chk("50 observations, t > 10, R2 .7, 90 to 95%", F["bs_granger"], [50, 10, 0.7, 90, 95])
    chk("    inflated fivefold", F["bs_fivefold"], [INFLATE])
    chk("    World War I", F["bs_ww1"], [1])
    say("有 50 个观测值时", "要大于 10 左右", "置信水平是 90\\%—95\\%", "五倍或者再多一点")
    assert "My tentative explanation" in Q["ke_tentative"]                             # 他的试探性解释
    # tab:wicksell-gibson
    printed = {(1821, 1913, False): (0.34, 0.03, 0.59, 0.43), (1821, 1913, True): (0.11, 0.05, 0.05, 1.77),
               (1821, 1871, False): (0.08, 0.07, 0.01, 0.48), (1821, 1871, True): (0.08, 0.06, 0.02, 1.86),
               (1872, 1913, False): (0.42, 0.04, 0.72, 0.32), (1872, 1913, True): (0.24, 0.08, 0.18, 1.68)}
    bs = {(1821, 1913, False): "bs_t2_lev", (1821, 1913, True): "bs_t2_dif", (1821, 1871, False): "bs_t2_lev1",
          (1821, 1871, True): "bs_t2_dif1", (1872, 1913, False): "bs_t2_lev2", (1872, 1913, True): "bs_t2_dif2"}
    R = {}
    for (a, b, d), (cf, se, r2, dw) in printed.items():
        x = regress(G.lnP.loc[a:b], G.consol_yield.loc[a:b], diff=d)
        R[(a, b, d)] = x
        lab = f"tab:wicksell-gibson {a}-{b} {'diff' if d else 'levels'}"
        pct(f"{lab}: coefficient", x["b"], cf, 2)
        pct("    standard error", x["se"], se, 2)
        pct("    adjusted R2", x["r2adj"], r2, 2)
        pct("    Durbin-Watson", x["dw"], dw, 2)
        chk("    observations", x["n"], b - a + 1 - d)
        bb, bse, bdw, br2 = F[bs[(a, b, d)]]
        line = f"{cf:.2f}（{se:.2f}） & {r2:.2f} & {dw:.2f} & {bb:.2f}（{bse:.2f}） & {br2:.2f} & {bdw:.2f}"
        say(line)
    full = R[(1821, 1913, False)]
    pct("the full sample: t with the standard error x5", full["b"] / (INFLATE * full["se"]), 2.3, 1)
    say("系数是 0.34，标准误放大五倍以后，$t$ 仍有 2.3")
    pct("    1 point of yield: the price level higher by (%), 'about four tenths'", 100 * (math.exp(0.34) - 1), 40, -1)
    dif = R[(1821, 1913, True)]
    assert dif["b"] < full["b"] and dif["b"] / dif["se"] > 1.96                       # 差分小一些，仍然显著
    late_l, late_d = R[(1872, 1913, False)], R[(1872, 1913, True)]
    assert late_l["b"] / late_l["se"] > 10 and late_d["b"] / late_d["se"] > 2.5       # 1872—1913 年两种回归都很强
    early = R[(1821, 1871, False)]
    assert early["r2adj"] < 0.02 and corr(G.lnP.loc[:1871], G.consol_yield.loc[:1871]) < 0.2   # 几乎没有相关
    assert F["bs_t2_lev1"][0] < F["bs_t2_lev2"][0] and F["bs_t2_lev1"][3] < F["bs_t2_lev2"][3]  # 前半段弱得多
    # why: Keynes, then ex:wicksell-keynes
    chk("Keynes: 1820-1900; the boom 1855-1875", F["ke_1820"], [1820, 1900, 1855, 1875])
    say("1820—1900 年，利率降得不够快", "只有 1855—1875 年的投资热潮是例外")
    chk("ex:wicksell-keynes: 5%, 2%, 107 for 100", F["ke_107"], [5, 2, 107, 100])
    chk("(1) 1.05 x 1.02", 1.05 * 1.02, 1.071, tol=1e-12)
    chk("    the product term 0.05 x 0.02", 0.05 * 0.02, 0.001, tol=1e-12)
    chk("(2) prices +2% a year, securities -2% a year", F["ke_2pa"], [2, 2])
    chk("    0.98 x 0.98", 0.98 * 0.98, 0.9604, tol=1e-12)
    chk("    4 per cent worse off", F["ke_4worse"], [4])
    pct("    1 - 0.9604 (%)", 100 * (1 - 0.98 * 0.98), 4, 0)
    pct("(3) the yield for a price 2% lower (%)", CONSOL / 0.98, 3.06, 2)
    pct("    a rise of (points)", CONSOL / 0.98 - CONSOL, 0.06, 2)
    say("$1.05\\times1.02=1.071$", "$(1-0.02)\\times(1-0.02)=0.9604$", "$3\\%/0.98=3.06\\%$", "升 0.06 个百分点")
    # Barsky and Summers on the two explanations
    chk("the pre-1914 American money stock", F["bs_kw"], [1914])
    pct("the autocorrelation of UK wholesale inflation, 1822-1913", G.infl.autocorr(1), 0.10, 2)
    say("与上一年涨幅的相关系数只有 0.10")
    chk("Sargent (1973)", F["bs_sargent"], [1973])
    chk("Friedman and Schwartz (1976, p. 288)", F["bs_fs"], [1976, 288])
    chk("Homer (1977); Sauerbeck-Statist from 1846", F["bs_homer"] + F["bs_prices"], [1977, 1846])


def case(F, Y, Q, S, M):
    chk("1873: the krona; 1 krona = 0.403225 g of gold", F["rk_title"] + F["rk_gram"], [1873, 1, 0.403225])
    chk("the Riksbank set the discount rate from November 1856", F["wa_1856"], [1856, 1980])
    assert "from November 1856" in Q["wa_1856"]
    a, b = SWEDEN
    d = M.discount_rate.loc[f"{a}-01":f"{b}-12"]
    chk("1874-1913: the discount rate between 3.5% and 7%", [d.min(), d.max()], [3.5, 7.0])
    chk("    the months in which it changed", int((d.diff().dropna() != 0).sum()), 70)
    chk("the bonds of 1872, 1880, 1887 and 1914", F["wa_bonds"][0::2], [1872, 1880, 1887, 1914])
    assert "John Håkansson and J. H. Zethreaus" in Q["wa_brokers"]                    # 两家证券经纪商
    chk("Edvinsson and Soederberg: 1732-1914 on Joerberg (1972) and Myrdal (1933)", F["es_basis"],
        [1732, 1914, 1972, 1933])
    cpi = S.cpi_1914_100
    chk("    1914 = 100", F["es_base"], [1914, 100])
    chk("    the printed table: 1887, 1913", [F["es_1887"][1], F["es_1913"][1]], [cpi[1887], cpi[1913]], tol=0.005)
    pct("the CPI 1874 -> 1887 (%)", 100 * (cpi[1887] / cpi[1874] - 1), -26, 0)
    chk("    the low year 1874-1913", int(cpi.loc[a:b].idxmin()), 1887)
    pct("    1887 -> 1913 (%)", 100 * (cpi[1913] / cpi[1887] - 1), 48, 0)
    by = M.bond_yield.dropna()
    assert by.index[0] == "1874-02"                                                   # the series starts in 1874
    assert by.idxmin() == "1896-08", by.idxmin()                                     # the monthly low
    pct("    at (%)", by.min(), 3.52, 2)
    A = annual(M)
    assert int(A.bond_yield.loc[a:b].idxmin()) in (1896, 1897)                    # the annual means: 1897
    chk("    nine years after the prices (1887)", int(by.idxmin()[:4]) - 1887, 9)
    say("长期利率却要晚九年才见底", "看长期利率怎样晚九年才见底")
    q = np.log(cpi)
    pct("corr(ln CPI, bond yield), 1874-1913", corr(q.loc[a:b], A.bond_yield.loc[a:b]), 0.51, 2)
    pct("    1874-1896", corr(q.loc[a:1896], A.bond_yield.loc[a:1896]), 0.81, 2)
    pct("    1897-1913", corr(q.loc[1897:b], A.bond_yield.loc[1897:b]), 0.93, 2)
    pct("corr(ln CPI, discount rate), 1874-1913", corr(q.loc[a:b], A.discount_rate.loc[a:b]), 0.62, 2)
    say("跌了约 26\\%", "涨了约 48\\%", "1896 年 8 月的 3.52\\%", "只有 0.51", "1874—1896 年是 0.81，1897—1913 年是 0.93",
        "贴现率与物价对数的相关系数是 0.62", "1 克朗合 0.403225 克黄金", "在 3.5\\% 与 7\\% 之间变动了 70 次")
    chk("Sweden left gold: autumn 1931", F["bj_left"] + F["bj_1931"], [1931, 1931])
    assert "fall of 1931" in Q["bj_left"] and "first country" in Q["bj_1931"] and "only country" in Q["bj_only"]


def deeper(F, Y, Q):
    abstracts = [r for r in quotes() if r in ("ba_relative", "ba_followed", "ba_goldlead", "ba_constant")]
    chk("the report prints a four-point abstract", len(abstracts), 4)
    _, m = load_snapshot("wicksell_facts")
    assert "June 1907" in m["source"]                                                  # 1907 年 6 月号
    chk("Thursday 2 August: Edgeworth's paper", F["ba_thursday"], [2])
    assert "By Professor F. Y." in Q["ba_edgeworth"] and "Edgeworth" in column("note")["ba_edgeworth"]
    chk("the reprint: February 1912", Y["f12_printing"], 1912)
    assert Q["f12_printing"] == "Reprinted February"
    assert "1926" in m["source"] and "doi:10.1086/261550" in m["source"] and "1988" in m["source"]
    _, g = load_snapshot("boe_millennium_gibson_1821_1913")
    assert "1888-1903" in g["series"] and "Klovland" in g["series"]
    say("1888—1903 年用的是 Klovland 的调整", "第 8a 页的图像")
    assert column("juan")["bs_t2_lev"] == "Table 2, p. 8a"


def legacy(F, Y, Q):
    assert "next twenty years" in Q["ke_prospect"]                                     # 未来二十年
    say("1930 年，凯恩斯说，未来二十年")
    assert "neutral in respect to commodity prices" in Q["ka_neutral"]


def takeaways(F, G):
    pct("1821-1913: 0.77", corr(G.lnP, G.consol_yield), 0.77, 2)
    assert corr(G.lnP.loc[1872:], G.consol_yield.loc[1872:]) > 0.85 > corr(G.lnP.loc[:1871], G.consol_yield.loc[:1871])
    say("相关系数是 0.77，主要来自 1872 年以后", "实际利率比市场利率多变七到十三倍")


def selfcheck(F):
    rn, i0, k, b = SC1["rn"], SC1["i0"], SC1["kappa"], SC1["beta"]
    i, p, pi = cumulative(np.full(300, rn), i0, k, b)
    chk("SC1 inflation in year 0 (%)", pi[0], 1.0, tol=1e-9)
    chk("    the rate in year 1 (%)", i[1], 4.6, tol=1e-9)
    chk("    the total rise g_0 / beta", (rn - i0) / b, 5, tol=1e-9)
    chk("    the sum of the inflation", pi.sum(), 5, tol=1e-9)
    pct("    (%)", 100 * (math.exp(0.05) - 1), 5.1, 1)
    chk("SC2 at 5%: interest (£)", 100 * 0.05 * 3 / 12, 1.25, tol=1e-12)
    chk("    the merchant gets (£)", discount(100, 5, 3), 98.75, tol=1e-9)
    chk("    at 4% (£)", discount(100, 4, 3), 99, tol=1e-9)
    pct("    the cash price rises (%)", 100 * (99 / 98.75 - 1), 0.25, 2)
    pct("SC3 5 / 0.045 (£)", 5 / 0.045, 111.1, 1)
    pct("    more (%)", 100 * (5 / 0.045 / 100 - 1), 11, 0)
    pct("SC4 1.05 x 1.02 - 1 (%)", 100 * (1.05 * 1.02 - 1), 7.1, 1)
    pct("    1.05 / 1.02 - 1 (%)", 100 * (1.05 / 1.02 - 1), 2.9, 1)
    for (cf, se), e in zip([(0.34, 0.03), (0.08, 0.07), (0.42, 0.04)], [2.3, 0.2, 2.1]):
        pct(f"SC5 {cf}/(5 x {se})", cf / (INFLATE * se), e, 1)
    say("$0.34/(5\\times0.03)\\approx2.3$", "$0.08/(5\\times0.07)\\approx0.2$", "$0.42/(5\\times0.04)\\approx2.1$",
        "$5/0.045\\approx111.1$", "$99/98.75-1\\approx0.25\\%$", "$i_1=4.5+0.1\\times1=4.6\\%$")


def ending(F, Y):
    chk("3 August 1906", date(1906, 8, 3).weekday(), 4)
    chk("eight years later: 1914", 1913 + F["bs_ww1"][0] - 1906, 8)
    say("1906 年 8 月 3 日，埃奇沃思在约克说", "八年以后，大战来了", "接近负 100\\%")
    say("一个国家为什么会印钞印到物价每天翻倍？恶性通胀又是怎样一夜止住的？")


# the life dates the chapter gives without a row of its own: the same words in an earlier chapter
LIVES = {"Irving Fisher，1867—1947": "ch03_prices", "John Maynard Keynes，1883—1946": "ch20_say",
         "Henry Thornton，1760—1815": "ch19_bullion", "Thomas Tooke，1774—1858": "ch19_bullion",
         "David Ricardo，1772—1823": "ch19_bullion", "Eugen von Böhm-Bawerk，1851—1914": "ch22_marx"}
# the life dates from rows of the snapshot
ROW_LIVES = {"Knut Wicksell，1851—1926": "ws_wicksell", "Robert Harry Inglis Palgrave，1827—1919": "ws_palgrave",
             "Francis Ysidro Edgeworth，1845—1926": "ws_edgeworth"}
UNKNOWN = ["Sauerbeck，生卒年未详", "A. H. Gibson，生卒年未详", "W. H. Coates，生卒年未详", "Peake（生卒年未详）"]
# what earlier chapters tell: (words of this chapter, chapter where it is told, words there)
EVENTS = [("高利贷法把前者卡在 5\\%", "ch19_bullion", "高利贷法卡在 5\\% 的上限"),
          ("1896 年的《升值与利息》", "ch03_prices", "出版了《升值与利息》"),
          ("用美国的纸币债券与印度的卢比债券做了检验", "ch03_prices", "检验了美国的纸币与印度的卢比"),
          ("卢比是印度以白银计价的货币", "ch03_prices", "以白银计价的卢比"),
          ("但调整得不完全、不及时", "ch03_prices", "但调整得不完全、不及时"),
          ("1873—1896 年，英镑的金价一直没有变", "ch23_goldstandard", "1873—1896 年跌了 45\\%")]


def book(F):
    """Life dates, what other chapters tell, and the works cited through others."""
    t = tex_text()
    for words, ch in LIVES.items():
        assert words in t, words
        assert words in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (words, ch)
    for words, rid in ROW_LIVES.items():
        assert words in t, words
        a, b = F[rid]
        assert f"{a:.0f}—{b:.0f}" in words, (words, rid)
    for words in UNKNOWN:
        assert words in t, words
    for here, ch, there in EVENTS:
        assert here in t, here
        assert there in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (ch, there)
    N, Q = column("note"), quotes()
    assert "Benjamin and Kochin (1984)" in Q["bs_bk"] and "Benjamin 与 Kochin（1984）" in t
    assert "Leijonhufvud" in Q["hu_leij"]
    assert "Sargent (1973)" in Q["bs_sargent"] and "Sargent（1973）" in t
    assert "Friedman and Schwartz (1976" in Q["bs_fs"] and "Friedman 与 Schwartz（1976）" in t
    assert "Granger and Newbold (1977)" in Q["bs_diff"] and "Granger and Newbold" in N["bs_granger"]
    assert "Gibson" in Q["f30_gibson"] and "Bankers" in Q["ke_bm"]
    assert "Peake" in N["ke_peake"] and "Coates" in Q["ke_coates_who"]
    assert "Jörberg (1972) and Myrdal (1933)" in Q["es_basis"] and "Jörberg（1972）与 Myrdal（1933）" in t
    assert "Homer, 1977" in Q["bs_homer"] and "Homer（1977）" in t


def witnesses(F, Q):
    """Second witnesses of statements of the text, and the bibliography block of the chapter."""
    # the full text (EJ) and the abstract (the report) agree on the paper's main points
    assert "relative" in Q["ba_relative"] and "only in relation to the profit" in Q["ej_relative"]
    assert "takes the lead in the long run" in Q["ba_goldlead"] and "take the lead in the long run" in Q["ej_goldlead"]
    # Wicksell's rule: Kahn's chapter 12 and Berg and Jonung
    assert "raise its discount rate as long as prices were rising" in Q["bj_rule"]
    # Coates's coefficient in both copies of the Treatise
    chk("0.893 in both copies", F["ke_893"][0], F["ke2_893"][0])
    # what the bibliography says of the documents
    assert Q["f30_pd"] == "The text of this edition is in the public domain"
    assert "CHAPTER XIX" in Q["f30_chapter"] and "MAY/JUNE 1986" in Q["hu_journal"]
    chk("Berg and Jonung: working paper No 290", F["bj_wp"], [290])
    chk("Barsky and Summers: NBER WP 1680, August 1985", F["bs_wp"] + F["bs_date"], [1680, 1985])
    chk("Edvinsson and Soederberg: 1290-2008", F["es_title"], [1290, 2008])
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    block = bib[bib.index("% ---- 第 25 章"):bib.index("\\end{thebibliography}")]
    items = {m.group(1): m.group(2) for m in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", block)}
    assert "版权" in items["wicksell1936"] and "只引短语" in items["wicksell1936"]
    assert "没有版权声明" in items["barsky1985"]
    assert "Sveriges riksbank" in items["riksbank2026b"] and "本书的计算" in items["riksbank2026b"]
    assert "public domain" in items["fisher1930"] and "第 XIX 章" in items["fisher1930"]
    assert "No. 290" in items["berg1998"] and "No. 1680" in items["barsky1985"] and "72(3)" in items["humphrey1986"]
    assert "1290--2008" in items["edvinsson2010b"] and "F. W-t." in items["watt1892"]
    assert "CC BY-SA" in items["wikisource2026"]
    keys = set(re.findall(r"\\bibitem\{([^}]+)\}", bib))
    cited = {k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", tex_text()) for k in c.split(",")}
    assert cited <= keys, sorted(cited - keys)
    assert set(items) <= cited, sorted(set(items) - cited)
    assert "A31" in bib[bib.index("\\bibitem{boe2017}"):].split("\n")[0] and "boe2017" in cited
    print(f"ok {len(cited)} works cited, {len(items)} of them in the bibliography block of Chapter 25")


def main() -> None:
    df = _rows()
    F, Y, Q = facts(), years(), quotes()
    G, S, M = gibson(), sweden(), sweden_monthly()
    check_readings(df)
    check_text(df)
    guide(F, Y)
    opening(F, Y, Q, G)
    world(F, Y, Q)
    cumulative_sec(F, Y, Q)
    model(F)
    history(F, Y, Q)
    rule(F, Y, Q)
    fisher(F, Y, Q)
    test(F, Y, Q, G)
    case(F, Y, Q, S, M)
    deeper(F, Y, Q)
    legacy(F, Y, Q)
    takeaways(F, G)
    selfcheck(F)
    ending(F, Y)
    book(F)
    witnesses(F, Q)
    anchors("zh/ch25_wicksell.tex", df["id"], script=Path(__file__))


if __name__ == "__main__":
    main()
