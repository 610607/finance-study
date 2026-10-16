"""Chapter 22 (马克思：积累、危机与再生产图式): every number and every quotation in zh/ch22_marx.tex.

    python3 checks/check_ch22.py

Inputs:
  marx_facts                           quotations of Marx (Zur Kritik 1859; Das Kapital I 1867 and its English
                                       translation of 1887; II 1885 and the Untermann translation, Kerr 1909; III
                                       1894 and its Kerr translation), Evans (1859, with the Select Committee's report
                                       of 1858), Wirth (1858), Tugan-Baranovsky (1901), Luxemburg (1913), Boehm-Bawerk
                                       (1896), Kalecki (1954), Allen (2009), Nakatani and Hagiwara (1997) and the Nobel
                                       Prize pages on Leontief (1973), and the Dictionary of National Biography
                                       (1889) on Evans (checked by data/fetch/verify_web_quotes.py)
  boe_millennium_gb_1855_1859_monthly  Bank of England, A Millennium of Macroeconomic Data: Bank Rate and the market
                                       rate of discount (sheet M9), the ironfounders' unemployment rate and raw cotton
                                       consumption (sheet M2, Klovland 1998), monthly 1855-1859
  boe_millennium_bank_rate_1856_1858   the days on which Bank Rate changed (sheet D1)
  boe_millennium_uk_1855_1913          union unemployment (A50, Feinstein 1972), real earnings (A48), factor incomes
                                       and GDP(I) (A17, Mitchell 1988), the capital stock (A55, Feinstein and Pollard
                                       1988), annual 1855-1913
  clark2015_england_decadal_1250_1860  Clark: England by decade (wage income, rents and NNI; real wages)
The figure module figsrc/fig_ch22.py imports the functions defined here.

What is checked here:
  1. readings   every number of the value column of marx_facts is read from its quotation: digits, English number
                words, vulgar fractions and the lines of the printed schemes and tables
  2. the text   every “…” in the chapter is the chapter's Chinese rendering of a quotation (TRANSLATIONS:
                rendering -> row or rows) or a term of the text (ALLOW)
  3. numbers    every number of the text, section by section, with quoted()
  4. anchors    the paraphrase anchors `% 据: ...` name rows of marx_facts

Models (the chapter's key equations):
    rates            m' = m/v,  q = c/v,  p' = m/(c+v) = m'/(1+q)                               (eq:marx-rates)
    the schemes      simple: I(v+m) = II c;  expanded: I(v + dv + m_k) = II(c + dc)             (eq:marx-schemes)
                     Marx's rule (ch. XXI): I accumulates half of its surplus value and splits it as its c:v;
                     II's dc closes the balance and its dv keeps II's c:v; m' = 100% in both     (tab:marx-path)
    input-output     x = Ax + f, solved with numpy.linalg.solve; (I - A)^-1                      (ex:marx-io)
    Okishio          one good: unit cost a + w l, profit rate 1/(a + w l) - 1, value l/(1 - a)  (ex:marx-okishio)
    Kalecki          gross profits = gross investment + capitalists' consumption               (eq:marx-kalecki)
    cycles           peaks and troughs of union unemployment, scipy.signal.find_peaks, prominence >= 2 points
"""
from __future__ import annotations

import math
import re
from datetime import date
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import find_peaks

from common import ROOT, anchors, load_snapshot, quoted

TEX = ROOT / "zh" / "ch22_marx.tex"
WAN = 1e4                                  # 万
MILL = 1e6

# Teaching inputs stated in the text
RATES_M2 = 1500                                        # ex:marx-rates (2): m of department I
RESERVE = dict(c=4000, v=1000, wage=1, labour=1100, g_labour=0.01, g_capital=0.10, q2=4.5)   # ex:marx-reserve
IO_CONSUMPTION2 = 3300                                 # ex:marx-io (2)
OKISHIO = dict(a=0.5, l=1.0, a2=0.6, l2=0.5, w=0.25, w2=0.4)                                 # ex:marx-okishio
PROMINENCE = 2.0                                       # fig:marx_uk: peaks at least 2 points above their surroundings
# self-check questions
SC1 = dict(c=3000, v=750, m=750, rate=1.0, q=2)
SC2 = dict(c=600, v=200, m=300)
SC3 = dict(c=300, v=100, rate1=1.0, rate2=2.0)
SC4 = dict(share=0.6)
SC5 = dict(investment=100, consumption=40, cut=10)


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
    """A number printed with `digits` decimals."""
    return quoted(what, float(value), expected, tol=0.5 * 10 ** -digits + 1e-12)


# ---------------------------------------------------------------------------------------------------
# Loaders
def _rows() -> pd.DataFrame:
    df, meta = load_snapshot("marx_facts", dtype=str, keep_default_na=False)
    assert 22 in meta["used_in"]
    assert df["id"].is_unique
    return df


def num(x: str) -> float:
    """'5', '1/3', '66+1/3'."""
    total = 0.0
    for part in x.split("+"):
        if "/" in part:
            a, b = part.split("/")
            total += float(a) / float(b)
        else:
            total += float(part)
    return total


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


def monthly() -> pd.DataFrame:
    """Monthly 1855-1859, indexed by (year, month)."""
    df, m = load_snapshot("boe_millennium_gb_1855_1859_monthly")
    assert 22 in m["used_in"]
    assert "three-month prime" in m["series"]
    return df.set_index(["year", "month"])


def bank_rate() -> pd.Series:
    """Bank Rate on 1 January 1856 and on each day it changed, 1856-1858."""
    df, m = load_snapshot("boe_millennium_bank_rate_1856_1858")
    assert 22 in m["used_in"]
    s = df.set_index(pd.to_datetime(df.date)).bank_rate
    assert s.index.is_monotonic_increasing and (s.diff().dropna() != 0).all()
    return s


def rate_on(s: pd.Series, day: str) -> float:
    """Bank Rate in force on a day."""
    return float(s.loc[:pd.Timestamp(day)].iloc[-1])


def annual() -> pd.DataFrame:
    """The UK 1855-1913, with the ratios of the chapter: the wage share (compensation of employees / GDP(I)), the
    profit proxy (profits and self-employment income / the nominal non-dwellings capital stock) and capital / GDP."""
    df, m = load_snapshot("boe_millennium_uk_1855_1913")
    assert 22 in m["used_in"]
    a = df.set_index("year")
    parts = a[["employees_gbp_m", "profits_selfemp_gbp_m", "rent_gbp_m", "public_enterprises_gbp_m"]].fillna(0)
    assert np.allclose(parts.sum(axis=1), a.gdp_factor_cost_gbp_m)               # the components add up
    a["wage_share"] = a.employees_gbp_m / a.gdp_factor_cost_gbp_m
    a["profit_rate"] = a.profits_selfemp_gbp_m / a.capital_nondwellings_gbp_m
    a["k_y"] = a.capital_nondwellings_gbp_m / a.gdp_factor_cost_gbp_m
    return a


def clark() -> pd.DataFrame:
    """Clark's decades with the shares of NNI: wage income, land rents and the rest (mostly capital)."""
    df, m = load_snapshot("clark2015_england_decadal_1250_1860")
    assert 22 in m["used_in"]
    c = df.set_index("decade")
    c["wage_share"] = c.wage_income_gbp_m / c.nni_gbp_m
    c["rent_share"] = c.land_rents_gbp_m / c.nni_gbp_m
    c["rest_share"] = 1 - c.wage_share - c.rent_share
    return c


# ---------------------------------------------------------------------------------------------------
# The arithmetic of the chapter
def rates(c: float, v: float, m: float) -> tuple[float, float, float]:
    """eq:marx-rates: m', q, p'."""
    return m / v, c / v, m / (c + v)


DEPTS = ["cI", "vI", "mI", "cII", "vII", "mII"]


def expanded(F, n: int = 5, share: float = 0.5) -> pd.DataFrame:
    """Marx's expanded reproduction (vol. II, ch. XXI) by his rule, years 0..n. Year 0 is the scheme of row k2_B0.
    Columns: c, v, m of the two departments; the accumulation of each (dc, dv) and the capitalists' consumption mk;
    the two sides of eq:marx-schemes; the products and the total."""
    x = np.array(F["k2_B0"][:3] + F["k2_B0"][4:7], dtype=float)        # cI vI mI cII vII mII
    rows = []
    for t in range(n + 1):
        cI, vI, mI, cII, vII, mII = x
        acc = share * mI
        dcI, dvI = acc * cI / (cI + vI), acc * vI / (cI + vI)
        lhs = vI + dvI + (mI - acc)                                    # I(v + dv + m_k)
        dcII = lhs - cII
        dvII = dcII * vII / cII
        rows.append(dict(zip(DEPTS, x), dcI=dcI, dvI=dvI, mkI=mI - acc, dcII=dcII, dvII=dvII,
                         mkII=mII - dcII - dvII, lhs=lhs, rhs=cII + dcII,
                         I=cI + vI + mI, II=cII + vII + mII))
        cI, vI, cII, vII = cI + dcI, vI + dvI, cII + dcII, vII + dvII
        x = np.array([cI, vI, vI, cII, vII, vII])                     # m' = 100%
    df = pd.DataFrame(rows)
    df["total"] = df.I + df.II
    return df


PRINTED = ["k2_B0", "k2_B1", "k2_B2", "k2_B3", "k2_B4", "k2_B5"]


def printed(F) -> pd.DataFrame:
    """The schemes as Marx printed them: c, v, s and the product of each department, years 0..5."""
    rows = []
    for k in PRINTED:
        v = F[k]
        rows.append(dict(cI=v[0], vI=v[1], mI=v[2], I=v[3], cII=v[4], vII=v[5], mII=v[6], II=v[7]))
    df = pd.DataFrame(rows)
    df["total"] = df.I + df.II
    return df


def io_matrix(F) -> np.ndarray:
    """ex:marx-io: the input coefficients of the simple scheme; only the products of department I are inputs."""
    cI, vI, mI, xI = F["k2_simple_I"]
    cII, vII, mII, xII = F["k2_simple_II"]
    return np.array([[cI / xI, cII / xII], [0.0, 0.0]])


def leontief(A: np.ndarray, f) -> np.ndarray:
    return np.linalg.solve(np.eye(len(A)) - A, np.asarray(f, dtype=float))


def okishio(a: float, l: float, w: float) -> dict:
    """One good made from itself (a) and labour (l), real wage w: unit cost, profit rate, and in value terms the
    value of a unit, c, v, m, q and m'."""
    cost = a + w * l
    lam = l / (1 - a)
    c, v = a * lam, w * l * lam
    m = l - v
    return dict(cost=cost, r=1 / cost - 1, lam=lam, c=c, v=v, m=m, q=c / v, mrate=m / v, p=m / (c + v))


def tugan(F) -> dict:
    """Tugan-Baranovsky's Schema II: the first year (the product of Schema I redistributed: means of production
    +240, workers' goods +120, capitalists' goods 360), each department split 2:1:1 into means of production, wages
    and profit; half of profit is capitalized at the same 2:1."""
    sI = F["tu_1440"]                                              # consumption 1440 = 720 + 720; total 2880
    cons, workers, capitalists, total = sI
    schema1 = np.array([total - cons, workers, capitalists])       # 1440, 720, 720
    more_mp, more_w = F["tu_240"]
    year1 = np.array([schema1[0] + more_mp, schema1[1] + more_w, F["tu_360"][0]])
    split = np.array([2, 1, 1]) / 4
    y1 = np.outer(year1, split)                                    # rows: departments; columns: mp, wages, profit
    acc = y1[:, 2] / 2
    y2 = np.column_stack([y1[:, 0] + acc * 2 / 3, y1[:, 1] + acc / 3])
    y2 = np.column_stack([y2, y2[:, 1]])                           # profit = wages (2:1:1)
    return dict(schema1=schema1, year1=year1, y1=y1, demand_mp=y2[:, 0], demand_wages=y2[:, 1],
                consumption_cap=y1[:, 2] - acc, y2=y2, out2=y2.sum(axis=1))


def cycles(A: pd.DataFrame) -> dict:
    """Peaks and troughs of union unemployment (prominence >= PROMINENCE points); expansions run from a peak to
    the next trough, recessions from a trough to the next peak."""
    u = A.unemp_unions
    pk, _ = find_peaks(u.values, prominence=PROMINENCE)
    tr, _ = find_peaks(-u.values, prominence=PROMINENCE)
    peaks, troughs = list(u.index[pk]), list(u.index[tr])
    turns = sorted([(y, "P") for y in peaks] + [(y, "T") for y in troughs])
    assert all(a[1] != b[1] for a, b in zip(turns, turns[1:])), turns          # they alternate
    exp = [(a[0], b[0]) for a, b in zip(turns, turns[1:]) if a[1] == "P"]
    rec = [(a[0], b[0]) for a, b in zip(turns, turns[1:]) if a[1] == "T"]
    return dict(peaks=peaks, troughs=troughs, expansions=exp, recessions=rec)


def rises(s: pd.Series, spans) -> int:
    return sum(int(s[b] > s[a]) for a, b in spans)


def decade_mean(s: pd.Series, a: int, b: int) -> float:
    return float(s.loc[a:b].mean())


DECADES = [(1855, 1864), (1865, 1874), (1875, 1884), (1885, 1894), (1895, 1904), (1905, 1913)]


ALLEN_ROWS = [("al_t1_1760a", "al_t1_1760b"), ("al_t1_1800a", "al_t1_1800b"), ("al_t1_1830a", "al_t1_1830b"),
              ("al_t1_1860a", "al_t1_1860b")]          # each line of the table is split around the T/L column


def allen_table(F) -> pd.DataFrame:
    """Allen (2009), Table 1: growth of output per worker, the contributions of K/L and T/L, TFP (A) and the real
    wage, % a year. The T/L column is printed with minus signs that the text layer lost; it is recovered as the
    residual Y/L - K/L - A."""
    rows = []
    for ra, rb in ALLEN_ROWS:
        a0, a1, yl, kl = F[ra]
        tfp, wage = F[rb]
        rows.append(dict(start=int(a0), end=int(a1), yl=yl, kl=kl, tl=round(yl - kl - tfp, 2), tfp=tfp, wage=wage))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------------------------------
# 1. Readings of the numbers
WORDS = {"a": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80,
         "ninety": 90}
VULGAR = {"⅓": Fraction(1, 3), "⅔": Fraction(2, 3)}
GERMAN = {"zwei": 2}


def cardinal(s: str) -> float:
    """An English cardinal ('ninety-eight')."""
    total = 0.0
    for w in s.lower().replace("-", " ").split():
        total += WORDS[w]
    return total


def figure(s: str) -> float:
    return float(s.replace(",", ""))


FIGURES = re.compile(r"\d[\d,]*(?:\.\d+)?")


def read(phrase: str, how: str) -> list[float]:
    if how == "num":
        return [figure(phrase)]
    if how == "en":
        return [cardinal(phrase)]
    if how == "vulgar":                       # '66⅓'
        return [figure(phrase[:-1]) + float(VULGAR[phrase[-1]])]
    if how == "de":
        return [float(GERMAN[phrase])]
    raise ValueError(how)


EN = "en"
SCHEME = "num"
# id -> [(phrase in the quotation, how it is read)], in order. Rows not listed are read with all the figures of the
# quotation (the lines of the printed schemes among them).
READINGS = {
    "ev_western": [("ninety-eight", EN), ("1,500,000", "num"), ("5,000,000", "num")],
    "ev_fortnight": [("two", EN), ("three", EN)],
    "wi_twoweeks": [("zwei", "de")],
    # the schemes: the figures of the two lines; the OCR noise between them is not read
    "k2_B2": [(x, SCHEME) for x in ("4840", "1210", "1210", "7260", "1760", "880", "880", "3520")],
    "k2_B4": [(x, SCHEME) for x in ("5856", "1464", "1464", "8784", "2129", "1065", "1065", "4249", "13,033")],
    "k2_B5": [(x, SCHEME) for x in ("6442", "1610", "1610", "9662", "2342", "1172", "1172", "4686")],
    "k3_tab_50": [("50", "num"), ("100", "num"), ("66⅓", "vulgar")],
    "k3en_tab_50": [("50", "num"), ("100", "num"), ("66⅓", "vulgar")],
    "k3_tab_200": [("200", "num"), ("100", "num"), ("33⅓", "vulgar")],
    "tu_360": [("360", "num")],                                    # 'N0. I' is the number of the schema
    "tu_1400": [("1400", "num"), ("980", "num"), ("420", "num"), ("3360", "num")],      # 'N0. II' likewise
}


def check_readings(df: pd.DataFrame) -> None:
    n = 0
    for r in df.itertuples():
        if not r.value:
            assert r.id not in READINGS, r.id
            continue
        vals = [num(x) for x in r.value.split(";")]
        quote = " ".join(r.quote.split())
        if r.id in READINGS:
            got, pos = [], 0
            for phrase, how in READINGS[r.id]:
                k = quote.find(phrase, pos)
                assert k >= 0, f"{r.id}: {phrase!r} not found (in order) in the quotation"
                pos = k + len(phrase)
                got += read(phrase, how)
        else:
            got = [figure(x) for x in FIGURES.findall(quote)]
        assert [round(g, 9) for g in got] == [round(v, 9) for v in vals], f"{r.id}: read {got}, value column {vals}"
        n += 1
    quoted("rows with values, each read from its quotation", n, 88)


# ---------------------------------------------------------------------------------------------------
# 2. Every “…” of the text against the snapshot
# terms of the text, which are not quotations
ALLOW = {"按规则", "不成比例", "即将发表"}
# the chapter's Chinese renderings of the quotations: rendering -> row (or rows)
TRANSLATIONS = {
    # opening
    "汉堡银行并不缺白银。银行地窖里的白银，其实比以往任何时候都多，可是信任完全丧失，持有白银的人不肯把它拿出来。": "ev_consul",
    "人们会记得，1857 年来了一场大危机，工业周期就是周期性地以这样的危机告终的。": "k1_1857",
    "真正根源是商业信用的过度扩张": "ev_origin",
    "没有哪一种通货制度，能使一个商业社会免于它自己的轻率所带来的后果": "ev_nosystem",
    # sec:marx-world
    "没有行政当局出面干预，英格兰银行的董事们根本无权超过法律规定的限额发行。": "ev_limit",
    # sec:marx-accumulation
    "是劳动力受资本剥削、或者说工人受资本家剥削的程度的准确表现": "k1_rate",
    "积累吧，积累吧！这就是摩西和先知们！": "k1_moses",
    "在停滞与中等繁荣的时期，产业后备军压着现役劳动军；在生产过剩与狂热的时期，它又压住现役劳动军的要求。": "k1_reserve",
    "资本主义积累的绝对的、一般的规律": "k1_law",
    "像其他一切规律一样，在实现中会因各种各样的情况而有所改变": "k1_law",
    # sec:marx-schemes
    "这就意味着第 II 部类生产过剩，只有通过一场大崩溃才能抵消，崩溃的结果是第 II 部类的一部分资本转到第 I 部类。": "k2_crash",
    # sec:marx-profit
    "表现了资本主义生产的实际趋势": "k3_tendency",
    "资本主义生产的真正限制是资本自身。": "k3_schranke",
    "第三卷否定了第一卷": "bb_denies",
    # sec:marx-crisis
    "并不站在马克思剩余价值论的立场上": "tu_not_mehrwert",
    "资本主义生产的目的不在消费，而在资本本身的增长": "tu_purpose",
    "在这一点上，西斯蒙第完全正确。但他对这个现象的解释是错的。": "tu_sismondi",
    "无论社会的消费多么低，商品的供给都不会超过需求": "tu_planned",
    "在社会生产完全没有计划、商品市场一片无政府状态的情况下，资本积累必然导致危机": "tu_anarchy",
    "谁来实现积累起来的剩余价值？": "lu_who",
    "说到底不过是萨伊那套陈腐荒谬的说法的翻版": "lu_say",
    "资本主义的存在与发展，需要非资本主义的生产形式作为它的环境。": "lu_need",
    "一切真正的危机的最后原因，总是群众的贫困与消费受限，而资本主义生产却竭力发展生产力，好像只有社会的绝对的消费能力才是它的界限。":
        "k3_letzter",
    "这纯粹是同义反复": "k2_tautology",
    # sec:marx-test
    "令人兴奋的修正": "al_revisionism",
    "光有马尔萨斯与马克思是不够的。": "al_enough",
    "如果利润率在长期中下降，那一定是因为实际工资率上升了。": "nh_wage",
    "不管他的报酬高低": "k1_lot",
    "我们的领事": "ev_consul",
    # sec:marx-legacy
    "发展了投入产出方法，并把它应用于重要的经济问题": "nb_citation",
    "却不能决定多赚": "ka_decide",
    "是他们的投资与消费决定利润，而不是反过来": "ka_determine",
}
# the renderings that are kept literally close to the source: a word of the source that must be there
KEYWORDS = {
    "ev_consul": ["no deficiency of silver", "cellars", "total want of confidence"],
    "ev_origin": ["real origin", "undue expansion of commercial credit"],
    "ev_nosystem": ["no system of currency", "improvidence"],
    "ev_limit": ["interposition of the Executive Government", "limit imposed by law"],
    "k1_1857": ["1857", "industrial cycle periodically ends"],
    "k1_moses": ["Accumulirt", "Moses und die Propheten"],
    "k1_lot": ["be his payment high or low"],
    "k3_schranke": ["wahre Schranke", "Kapital selbst"],
    "bb_denies": ["dritte Band", "verleugnet den ersten"],
    "tu_not_mehrwert": ["nicht auf dem Boden der Mehrwerttheorie"],
    "lu_who": ["wer realisiert den akkumulierten Mehrwert"],
    "lu_need": ["nichtkapitalistischer Produktionsformen", "Umgebung"],
    "k2_tautology": ["reine Tautologie"],
    "al_enough": ["Malthus and Marx are not enough"],
    "al_revisionism": ["exciting revisionism"],
    "nh_wage": ["real wage rate"],
    "ka_decide": ["cannot decide to earn more"],
    "nb_citation": ["input-output method"],
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
    print(f"ok {n} quotations of the text found in the snapshot (or listed as exceptions)")


# ---------------------------------------------------------------------------------------------------
# 3. Numbers, section by section
def opening(F, Y, Q, D):
    chk("the Treasury letter: 12 November 1857", [Y["ev_treasury"]] + F["ev_treasury"], [1857, 12])
    assert "Treasury Letter" in Q["ev_treasury"] and "Downing Street" in Q["ev_treasury"]
    before, peak, on4, res, bullion = F["ev_reserve"]
    pct("the reserve that day (万英镑)", res / WAN, 58.1)
    pct("    on the 4th (万英镑)", peak / WAN, 370.6)
    chk("    eight days before", F["ev_treasury"][0] - on4, 8)
    consul = date(1857, 12, int(F["ev_consul"][0]))
    chk("the consul wrote three weeks later (days)", (consul - date(1857, 11, 12)).days, 21)
    assert "exclusively metallic" in Q["ev_metallic"] and "most severely" in Q["ev_hamburg_blow"]
    chk("Marx in London from", F["zk_1850"], [1850])
    chk("Zur Kritik, January", Y["zk_date"], 1859)
    assert "achtjährige" in Q["zk_tribune"]                                           # 八年
    chk("Capital I, the crisis of", F["k1_1857"], [1857])
    chk("the Select Committee reported", [Y["ev_origin"], Y["ev_nosystem"]], [1858, 1858])
    assert "symptom" in Q["k1_symptom"] and "cause" in Q["k1_symptom"]


def world(F, Y, Q, M, D):
    chk("Evans, 1819-1874 (DNB, 1889)", F["dnb_evans"] + [Y["dnb_evans"]], [1819, 1874, 1889])
    assert "financial journalist" in Q["dnb_evans"]                                   # 金融记者
    assert "Ohio Life" in Q["ev_ohio"] and "first signal" in Q["ev_ohio"]
    chk("25 to 29 September; 150 banks", F["ev_150banks"], [25, 29, 150])
    assert "Pennsylvania, Maryland, Virginia, and Rhode Island" in Q["ev_150banks"]
    chk("failures in the United States and Canada", F["ev_failures"][0], 5123)
    chk("Liverpool Borough Bank: 27 October", F["ev_liverpool"], [27])
    chk("Western Bank: 98 branches, capital (万), deposits (万)",
        [F["ev_western"][0], F["ev_western"][1] / WAN, F["ev_western"][2] / WAN], [98, 150, 500])
    chk("    9 November", F["ev_western_date"], [9])
    chk("Wolverhampton: 17 November", F["ev_wolverhampton"], [17])
    chk("    works stopped (万 hands)", F["ev_30000"][0] / WAN, 3)
    # Bank Rate (sheet D1)
    chk("Bank Rate before 8 October 1857", rate_on(D, "1857-10-07"), 5.5)
    chk("    8 October", rate_on(D, "1857-10-08"), 6)
    ups = D.loc["1857-10-09":"1857-11-30"]
    chk("    raised four more times", len(ups), 4)
    assert (ups.diff().dropna() > 0).all() and ups.iloc[0] > 6
    chk("    12 November", D[pd.Timestamp("1857-11-12")], 10)
    chk("    the peak", D.loc["1857":"1858"].max(), 10)
    nov = M.loc[(1857, 11)]
    chk("prime bills, November 1857 (将近 10%)", nov.prime_bills_rate, 9.75)
    assert 9.5 <= nov.prime_bills_rate < 10
    u = M.unemp_ironfounders
    pct("ironfounders' unemployment, September 1857 (%)", u[(1857, 9)], 8.1)
    pct("    November", u[(1857, 11)], 13.6)
    pct("    May 1858", u[(1858, 5)], 20.6)
    cot = M.cotton_bales_week
    pct("raw cotton, November / September - 1 (%)", 100 * (cot[(1857, 11)] / cot[(1857, 9)] - 1), -55, 0)
    # the way down
    cuts = D.loc["1857-12-24":"1858-02-11"]
    assert cuts.index[0] == pd.Timestamp("1857-12-24")                                 # 12 月 24 日起
    chk("cuts from 24 December 1857 to 11 February 1858", len(cuts), 6)
    assert (cuts.diff().dropna() < 0).all() and cuts.iloc[0] < 10
    chk("    11 February", D[pd.Timestamp("1858-02-11")], 3)
    chk("prime bills, February 1858", M.loc[(1858, 2)].prime_bills_rate, 2.5)
    peak = u.loc[(1857, 1):(1859, 12)].idxmax()
    chk("unemployment peaks in May 1858", [peak[0], peak[1]], [1858, 5])
    chk("    three months after February", peak[1] - 2, 3)
    days = (date(1858, 2, 11) - date(1857, 9, int(F["ev_150banks"][1]))).days
    assert days < 183, days                                                            # 不到半年
    assert rate_on(D, "1858-02-11") < rate_on(D, "1857-10-07")                          # 3% < 5.5%
    chk("Capital I; II; III", [Y["k1_value"], Y["k2_date"], Y["k3_date"]], [1867, 1885, 1894])
    assert "druckfertig" in Q["k2_finish"]


def accumulation(F, Q):
    assert "konstantes Kapital" in Q["k1_const"] and "variables Kapital" in Q["k1_var"]
    cI, vI, mI = F["k2_B0"][:3]
    cII, vII, mII = F["k2_B0"][4:7]
    # ex:marx-rates
    chk("(1) I: c, v, m", [cI, vI, mI], [4000, 1000, 1000])
    chk("    II: c, v, m", [cII, vII, mII], [1500, 750, 750])
    r1, q1, p1 = rates(cI, vI, mI)
    chk("    I: m' (%), q, p' (%)", [100 * r1, q1, 100 * p1], [100, 4, 20])
    chk("    I: c + v", cI + vI, 5000)
    r2, q2, p2 = rates(cII, vII, mII)
    chk("    II: m' (%), q", [100 * r2, q2], [100, 2])
    chk("    II: c + v", cII + vII, 2250)
    pct("    II: p' (%)", 100 * p2, 33.3)
    chk("    = 1/(1+2)", p2, 1 / (1 + q2))
    r3, q3, p3 = rates(cI, vI, RATES_M2)
    chk("(2) m = 1500: m' (%), q, p' (%)", [100 * r3, q3, 100 * p3], [150, 4, 30])
    chk("    = 1.5/(1+4)", p3, r3 / (1 + q3))
    # ex:marx-reserve
    R = RESERVE
    K = R["c"] + R["v"]
    chk("capital 5,000 = 4,000 + 1,000", K, 5000)
    chk("labour 1,100; growth 1%; accumulation 10%", [R["labour"], 100 * R["g_labour"], 100 * R["g_capital"]],
        [1100, 1, 10])
    K1, L1 = K * (1 + R["g_capital"]), R["labour"] * (1 + R["g_labour"])
    chk("a year later: capital, labour", [K1, L1], [5500, 1111])
    v1 = K1 / (1 + R["c"] / R["v"])
    chk("(1) q = 4: employed", v1 / R["wage"], 1100)
    pct("    employment +%", 100 * (v1 / R["v"] - 1), 10, 0)
    chk("    reserve: 100 -> 11", [R["labour"] - R["v"], L1 - v1], [100, 11])
    v2 = K1 / (1 + R["q2"])
    chk("(2) q = 4.5: employed", v2, 1000)
    chk("    capital +10%, employment +0", [100 * (K1 / K - 1), v2 - R["v"]], [10, 0])
    chk("    reserve: 100 -> 111", L1 - v2, 111)
    assert "decennial cycle" in Q["k1_cycle"]                                          # 大约十年
    for w in ("average activity", "production at high pressure", "crisis and stagnation"):
        assert w in Q["k1_cycle"]


def schemes(F, Q, J):
    sI, sII = F["k2_simple_I"], F["k2_simple_II"]
    chk("simple: I", sI, [4000, 1000, 1000, 6000])
    chk("    II", sII, [2000, 500, 500, 3000])
    assert sum(sI[:3]) == sI[3] and sum(sII[:3]) == sII[3]
    chk("    the exchange: I(v+m) = II c", [sI[1] + sI[2], sII[0]], [2000, 2000])
    chk("    total product", sI[3] + sII[3], 9000)
    chk("    v + m (NDP) = II's product", [sI[1] + sI[2] + sII[1] + sII[2], sII[3]], [3000, 3000])
    chk("Engels's preface: 5 May 1885, Marx's birthday", F["k2_date"], [5, 1885])
    assert "Mai" in Q["k2_date"] and "Geburtstag" in Q["k2_date"] and "wörtlich" in Q["k2_literal"]
    assert J["k2_depts"].startswith("ch. XX,") and J["k2_simple_I"].startswith("ch. XX,")    # 第二十章
    # expanded reproduction
    P, E = printed(F), expanded(F)
    chk("start: total", P.total[0], 9000)
    chk("I accumulates 500: 400 c, 100 v", F["k2_400"], [400, 500, 100])
    chk("    = half of I's m", F["k2_400"][1] / P.mI[0], 0.5)
    chk("    split as I's c:v (4:1)", [E.dcI[0], E.dvI[0], P.cI[0] / P.vI[0]], [400, 100, 4])
    chk("    II's c:v (Δv = Δc/2)", P.cII[0] / P.vII[0], 2)
    chk("    m' = 100% in both", [P.mI[0] / P.vI[0], P.mII[0] / P.vII[0]], [1, 1])
    for k in PRINTED:
        assert J[k].startswith("ch. XXI,"), k                                         # 第二十一章
    chk("Kerr pages 596-600", [int(J["k2_B0"][-3:]), int(J["k2_B5"][-3:])], [596, 600])
    marx_I = [6000, 6600, 7260, 7986, 8784, 9662]
    marx_II = [3000, 3200, 3520, 3872, 4249, 4686]
    marx_T = [9000, 9800, 10780, 11858, 13033, 14348]
    chk("tab:marx-path: I (Marx)", P.I, marx_I)
    chk("    II (Marx)", P.II, marx_II)
    chk("    total (Marx)", P.total, marx_T)
    chk("    the totals Marx printed", [F["k2_B3"][-1], F["k2_B4"][-1]], [11858, 13033])
    pct("    I (by the rule), years 4-5", E.I[4], 8784.6)
    pct("    ", E.I[5], 9663.1)
    pct("    II (by the rule), years 4-5", E.II[4], 4259.2)
    pct("    ", E.II[5], 4685.1)
    pct("    total (by the rule), years 4-5", E.total[4], 13043.8)
    pct("    ", E.total[5], 14348.2)
    chk("    years 0-3 (by the rule, rounded)", [round(x) for x in E.total[:4]], marx_T[:4])
    for t in range(4):
        assert abs(E.I[t] - marx_I[t]) < 1e-6 and abs(E.II[t] - marx_II[t]) < 1e-6, t
    g = 100 * (E.total / E.total.shift(1) - 1)
    pct("    growth of the total, year 1 (%)", g[1], 8.9)
    for t in range(2, 6):
        pct(f"    year {t}", g[t], 10.0)
    # Marx's figures differ from the rule only by rounding, except II in year 4, a slip in the addition
    for t in range(6):
        for col in DEPTS:
            assert abs(P[col][t] - E[col][t]) < 1, (t, col, P[col][t], E[col][t])
        for col in ("I", "II"):
            if (t, col) != (4, "II"):
                assert abs(P[col][t] - round(E[col][t])) <= 1.5, (t, col)
    chk("    year 4, II: Marx's three terms add up to", P.cII[4] + P.vII[4] + P.mII[4], 4259)
    assert P.II[4] == 4249 and abs(P.II[4] - E.II[4]) > 10
    chk("    year 5 is unaffected (II)", abs(P.II[5] - E.II[5]) < 1, True)
    # ex:marx-expanded
    e0 = E.iloc[0]
    chk("(1) I's demand for consumer goods: 1000v + 100Δv + 500m_k", [e0.vI, e0.dvI, e0.mkI, e0.lhs],
        [1000, 100, 500, 1600])
    chk("    II: c 1,500 -> 1,600; Δc, Δv", [e0.cII, e0.cII + e0.dcII, e0.dcII, e0.dvII], [1500, 1600, 100, 50])
    chk("    II's capitalists consume", [e0.mII - e0.dcII - e0.dvII, e0.mkII], [600, 600])
    chk("    750 - 150", e0.dcII + e0.dvII, 150)
    chk("(2) 1000 + 100 + 500 = 1500 + 100", [e0.lhs, e0.rhs], [1600, 1600])
    chk("    I's product: 4,400 to itself, 1,600 to II", [e0.cI + e0.dcI, e0.rhs, P.I[0]], [4400, 1600, 6000])
    chk("(3) next year I", [E.cI[1], E.vI[1], E.mI[1], E.I[1]], F["k2_B1"][:4])
    chk("    II", [E.cII[1], E.vII[1], E.mII[1], E.II[1]], F["k2_B1"][4:])
    chk("    total", E.total[1], 9800)
    e1 = E.iloc[1]
    chk("    the second year's exchange: 1100 + 110 + 550 = 1600 + 160",
        [e1.vI, e1.dvI, e1.mkI, e1.lhs, e1.cII, e1.dcII], [1100, 110, 550, 1760, 1600, 160])
    assert "cannot be equal to II c" in Q["k2_cannot"]
    assert "overproduction in II" in Q["k2_crash"] and "great crash" in Q["k2_crash"]
    # fig:marx_schemes (a)
    chk("fig (a): I(v+m), II c", [sI[1] + sI[2], sII[0]], [2000, 2000])
    # ex:marx-io
    A = io_matrix(F)
    chk("A", A.ravel(), [2 / 3, 2 / 3, 0, 0])
    chk("    a11 = 4000/6000, a12 = 2000/3000", [A[0, 0], A[0, 1]], [4000 / 6000, 2000 / 3000])
    f = np.array([0.0, sII[3]])
    chk("(1) f = (0, 3000)", f, [0, 3000])
    x = leontief(A, f)
    chk("    x", x, [6000, 3000])
    chk("    x1 = (2/3) 3000 / (1 - 2/3)", (2 / 3) * 3000 / (1 - 2 / 3), 6000)
    chk("    = Marx's two departments", x, [sI[3], sII[3]])
    x2 = leontief(A, [0, IO_CONSUMPTION2])
    chk("(2) f = (0, 3300): x", x2, [6600, 3300])
    chk("    +10% each", 100 * (x2 / x - 1), [10, 10])
    inv = np.linalg.inv(np.eye(2) - A)
    chk("(3) (I - A)^-1", inv.ravel(), [3, 2, 0, 1])
    chk("    direct: 2/3", A[0, 1], 2 / 3)
    va = np.array([sI[1] + sI[2], sII[1] + sII[2]])
    chk("    value-added ratios", va / x, [1 / 3, 1 / 3])
    chk("    value added 2000 + 1000 = final demand", [va[0], va[1], va.sum(), f.sum()], [2000, 1000, 3000, 3000])
    # Kerr 1909 / the 史料说明: the initial capital and the growth of capital
    c7, v7, k7, c11, v11, k11, a, b = F["k2_7150"]
    chk("Marx: 5400c + 1750v = 7150", [c7, v7, k7], [5400, 1750, 7150])
    assert c7 + v7 == k7
    chk("    by his scheme: c, c + v", [P.cI[0] + P.cII[0], P.cI[0] + P.cII[0] + P.vI[0] + P.vII[0]], [5500, 7250])
    chk("    to 8784c + 2782v = 11,566", [c11, v11, k11], [8784, 2782, 11566])
    chk("    the capital of year 5 by the rule (rounded)", [round(E.cI[5] + E.cII[5]), round(E.vI[5] + E.vII[5])],
        [8785, 2782])
    chk("    100 : 160", [a, b], [100, 160])
    chk("    11,566 / 7,250 (rounded, per 100)", round(100 * k11 / 7250), 160)
    chk("    11,566 / 7,150 (rounded, per 100)", round(100 * k11 / k7), 162)
    return E


def profit(F, Y, Q, J):
    w, workers, week = F["k3_100"]
    chk("100 workers, 100 pounds, a week", [workers, w, week], [100, 100, 1])
    assert J["k3_100"].startswith("Kap. 13")                                           # 第十三章
    cs = [50, 100, 200, 300, 400]
    rows = ["k3_tab_50", "k3_tab_100", "k3_tab_200", "k3_tab_300", "k3_tab_400"]
    for c, k in zip(cs, rows):
        chk(f"the table: c = {c}, v", F[k][:2], [c, 100])
    ps = [100 * Fraction(100, c + 100) for c in cs]
    chk("p' (%)", [float(p) for p in ps], [200 / 3, 50, 100 / 3, 25, 20])
    assert ps[0] == Fraction(200, 3) and ps[2] == Fraction(100, 3)                      # 66⅔, 33⅓
    for k, p in zip(rows[1:], ps[1:]):
        chk(f"    printed ({k})", F[k][2], float(p))
    chk("    printed for c = 50 (a slip: 66⅓)", [F["k3_tab_50"][2], F["k3en_tab_50"][2]], [66 + 1 / 3, 66 + 1 / 3])
    assert F["k3_tab_50"][2] != float(ps[0])
    for c, k in zip(cs, rows):
        if k != "k3_tab_50":
            chk(f"    the surplus value implied by the printed p' (c = {c})", F[k][2] / 100 * (c + 100), 100)
    t = F["k3_tab_100"]
    chk("    m' = m / v (%)", 100 * (t[2] / 100 * (t[0] + t[1])) / t[1], 100)
    chk("from 66⅔% to 20%", [float(ps[0]), float(ps[-1])], [200 / 3, 20])
    assert "wirkliche Tendenz" in Q["k3_tendency"] and "Produktivkraft" in Q["k3_productivity"]
    # ex:marx-profit (2)
    vm = 200
    chk("(2) v + m = 200; m = 200 when the wage is 0", vm, 200)
    chk("    the bound at c = 400 (%)", 100 * vm / 400, 50)
    for c in cs:
        assert 100 / (c + 100) < vm / c
    # six counteracting causes
    six = ["k3_c1", "k3_c2", "k3_c3", "k3_c4", "k3_c5", "k3_c6"]
    chk("six counteracting causes", len(six), 6)
    for k, w in zip(six, ("Exploitationsgrads", "Arbeitslohns", "konstanten Kapitals", "Ueberbevölkerung",
                          "auswärtige Handel", "Aktienkapitals")):
        assert w in Q[k] and J[k].startswith("Kap. 14"), k
    assert J["k3_schranke"].startswith("Kap. 15")                                      # 第十五章
    assert "Tendenz" in Q["k3_tendenz"]
    chk("Böhm-Bawerk", Y["bb_denies"], 1896)
    # the deeper box: 20% and 33.3%
    p1 = rates(*F["k2_B0"][:3])[2]
    p2 = rates(*F["k2_B0"][4:7])[2]
    pct("ex:marx-rates: 20% and 33.3%", 100 * p1, 20, 0)
    pct("    ", 100 * p2, 33.3)


def crisis(F, Y, Q, J):
    chk("Tugan 1901; Luxemburg 1913", [Y["tu_not_mehrwert"], Y["lu_who"]], [1901, 1913])
    assert "willkürlich" in Q["tu_arbitrary"] and "Hälfte des Profites" in Q["tu_half"]
    T_ = tugan(F)
    chk("Schema I: total, consumption", [F["tu_1440"][3], F["tu_1440"][0]], [2880, 1440])
    chk("    the three departments", T_["schema1"], [1440, 720, 720])
    chk("Schema II, year 1", T_["year1"], [1680, 840, 360])
    chk("    2:1:1, means of production", T_["y1"][0], [840, 420, 420])
    chk("    workers' goods", T_["y1"][1], [420, 210, 210])
    chk("    capitalists' goods", T_["y1"][2], [180, 90, 90])
    chk("    total", T_["y1"].sum(), 2880)
    chk("    = Schema I + 240, + 120; 360", [T_["year1"][0] - T_["schema1"][0], T_["year1"][1] - T_["schema1"][1],
                                         T_["year1"][2]], [240, 120, 360])
    chk("    360 is half of 720", T_["schema1"][2] / T_["year1"][2], 2)
    chk("ex:marx-tugan (1) means of production 980 + 490 + 210", list(T_["demand_mp"]) + [T_["demand_mp"].sum()],
        [980, 490, 210, 1680])
    chk("    wages 490 + 245 + 105", list(T_["demand_wages"]) + [T_["demand_wages"].sum()], [490, 245, 105, 840])
    chk("    capitalists consume 210 + 105 + 45", list(T_["consumption_cap"]) + [T_["consumption_cap"].sum()],
        [210, 105, 45, 360])
    chk("(2) = the year-1 products", [T_["demand_mp"].sum(), T_["demand_wages"].sum(), T_["consumption_cap"].sum()],
        list(T_["year1"]))
    chk("(3) year 2: 980+490+490, 490+245+245, 210+105+105", T_["y2"].ravel(),
        [980, 490, 490, 490, 245, 245, 210, 105, 105])
    chk("    products", T_["out2"], [1960, 980, 420])
    chk("    total; consumption 980 + 420", [T_["out2"].sum(), T_["out2"][1] + T_["out2"][2]], [3360, 1400])
    chk("    Tugan's figures", F["tu_1400"], [1400, 980, 420, 3360])
    assert T_["out2"][1] + T_["out2"][2] < F["tu_1440"][0]                              # 消费减少了
    assert "Absatz" in Q["tu_absatz"] and "Markt schafft" in Q["tu_market"]
    assert "Say" in Q["tu_synthesis"] and "Ricardo" in Q["tu_synthesis"] and "anbestreitbar" in Q["tu_kernel"]
    assert "unüberwindliche" in Q["tu_hard"] and "Anarchie" in Q["tu_anarchy"]
    assert "So fragte Sis" in Q["lu_sismondi"] and "Imperialismus" in Q["lu_imperialism"]
    assert "sicherste Mittel" in Q["lu_end"] and "Boden unter den Füßen" in Q["lu_ground"]   # 最可靠的办法；脚下的地面
    assert "Ueberschuss an Produktivkräften" in Q["tu_surplus"]                       # 用不尽已有的生产力
    assert J["k3_imagine"] == J["k3_letzter"] == "Kap. 30"                             # 第三十章
    assert "wages rise generally" in Q["k2_wages"] and "larger share" in Q["k2_wages"]


def hamburg(F, Y, Q):
    assert "three or four" in Q["ev_nov23"]                                            # 三四家
    chk("23 November", F["ev_nov23"], [23])
    d, v = F["wi_verein"]
    chk("the Verein, 23 November; nearly 1,400 万 (14 Mill.)", [d, v * MILL / WAN], [23, 1400])
    assert "faft 14 Mill" in Q["wi_verein"]                                             # fast = nearly
    v, d = F["wi_verein_end"]
    chk("    about 1,200 万; stopped 28 November", [v * MILL / WAN, d], [1200, 28])
    d, v = F["wi_heine_offer"]
    chk("Heine, 28 November; 2 万 a broker", [d, v / WAN], [28, 2])
    chk("    within an hour: 100 万", F["wi_heine_hour"][0] * MILL / WAN, 100)
    assert "kaum einer Stunde" in Q["wi_heine_hour"] and "dreimaliges Hoch" in Q["wi_hoch"]   # 一个小时；三次
    chk("demanded: 4,000 万 of forced paper", F["wi_zwang"][0] * MILL / WAN, 4000)
    chk("by 10 December: 135 houses; 65", F["wi_135"] + F["wi_65"], [135, 10, 65])
    d, v = F["wi_dec6"]
    chk("6 December: a discount office of 1,500 万", [d, v * MILL / WAN], [6, 1500])
    chk("    of which 1,000 万 borrowed", F["wi_borrow"][0] * MILL / WAN, 1000)
    assert "baar angeliehen" in Q["wi_borrow"]
    chk("Vienna: 1,000 万 at 6%, by the end of 1858", [F["wi_nationalbank"][0] * MILL / WAN] + F["wi_6pct"],
        [1000, 6, 1858])
    chk("    = Evans: the first 10,000,000 marks banco", F["ev_vienna"][0] / MILL, F["wi_nationalbank"][0])
    chk("the second measure, 27 November", F["wi_nov27"], [27])
    assert "zweite" in Q["wi_second"] and "Solawech" in Q["wi_sola"] and "Waaren und" in Q["wi_pledge"]
    assert "verfilbern" in Q["wi_cash"]                                                 # versilbern: 换成现钱
    chk("hard to place for two weeks; from 15 December 4%-5%; bills hardly at 10%", F["wi_twoweeks"] + F["wi_dec15"],
        [2, 15, 5, 4, 10])
    chk("12 December", F["ev_dec12"], [12])
    chk("repaid about Johanni 1858", F["wi_repaid"], [1858])
    assert "Johanni" in Q["wi_repaid"] and "24 June" in column("note")["wi_repaid"]
    chk("silver: 1 亿 (100 Mill.)", F["wi_silver100"][0] * MILL / 1e8, 1)
    chk("the National Bank resumes silver payments: 1 January 1859", F["wi_1859"], [1, 1859])
    assert "secret committee" in Q["ev_secret"] and "reluctantly" in Q["ev_loan"]


def test(F, Y, Q, A, C):
    # Clark's shares (Chapter 21's figures)
    pct("Clark: wage share 1700s (%)", 100 * C.wage_share[1700], 57, 0)
    pct("    1800s", 100 * C.wage_share[1800], 54, 0)
    pct("    the rest 1700s (%)", 100 * C.rest_share[1700], 24, 0)
    pct("    1800s", 100 * C.rest_share[1800], 32, 0)
    pct("    wage share 1860s", 100 * C.wage_share[1860], 63, 0)
    assert C.wage_share[1860] > C.wage_share[1800]                                     # 1800 年以后回升
    assert C.real_nni_pc_1860s_100[1800] > C.real_nni_pc_1860s_100[1700]
    for col in ("real_farm_1860s_100", "real_blab_1860s_100", "real_bcraft_1860s_100"):
        assert C[col][1800] <= C[col][1700], col                                       # 工资却没有
    # Allen
    chk("Allen 2009", Y["al_46_12"], 2009)
    chk("1780-1840: output per worker +46%, Feinstein's real wage +12%", F["al_46_12"], [46, 1780, 1840, 12])
    chk("labour's share: late 18th century 60%", F["al_labour60"], [18, 60, 19])
    assert "about 60%" in Q["al_labour60"] and "around one half" in Q["al_labour60"]
    chk("capital's share 20% -> over 40%", F["al_capital40"], [18, 20, 40, 19])
    assert "over 40%" in Q["al_capital40"]
    chk("return: near 10% -> surpassed 20%", [F["al_return"][0], F["al_return"][-1]], [10, 20])
    assert "near 10%" in Q["al_return"] and "surpassed 20%" in Q["al_return"]
    chk("1840-1900: +90%, +123%", F["al_90_123"], [1840, 1900, 90, 123])
    chk("Feinstein's wage raised by 14%", F["al_14"], [14])
    T1 = allen_table(F).set_index("start")
    chk("1800-1830: TFP, Y/L, real wage (% a year)", [T1.tfp[1800], T1.yl[1800], T1.wage[1800]], [0.69, 0.63, 0])
    chk("    the shares in the note", F["al_t1_shares"], [0.35, 0.15])
    assert (T1.tl < 0).all()                                                          # the lost minus signs
    assert "doubled" in Q["al_doubled"] and "first four decades" in Q["al_inequality"]
    assert "as he expected" in Q["al_expected"] and "capital stock" in Q["al_mediate"]       # 像马克思预料的那样；资本存量
    chk("    the 19th century", F["al_inequality"], [19])
    # cycles
    cy = cycles(A)
    chk("eight peaks", cy["peaks"], [1858, 1862, 1868, 1879, 1886, 1893, 1904, 1908])
    gaps = np.diff(cy["peaks"])
    chk("    gaps 4 to 11 years", [gaps.min(), gaps.max()], [4, 11])
    pct("    mean gap (约 7)", gaps.mean(), 7, 0)
    chk("Marx's crises: 1857, 1866", [F["k1_1857"][0], F["k1_1866"][0]], [1857, 1866])
    # real earnings and the wage share
    e = A.real_earnings_1900_100
    pct("real earnings 1855", e[1855], 56.1)
    pct("    1913", e[1913], 104.2)
    chk("    years", 1913 - 1855, 58)
    pct("    rise (%)", 100 * (e[1913] / e[1855] - 1), 86, 0)
    pct("    a year (%)", 100 * ((e[1913] / e[1855]) ** (1 / 58) - 1), 1.1)
    ws = A.wage_share
    pct("wage share 1855 (%)", 100 * ws[1855], 52.9)
    pct("    1913", 100 * ws[1913], 54.4)
    chk("    lowest; highest", [ws.idxmin(), ws.idxmax()], [1871, 1892])
    pct("    1871", 100 * ws.min(), 46.5)
    pct("    1892", 100 * ws.max(), 56.7)
    # the profit proxy
    pr = A.profit_rate
    pct("profit proxy 1855 (约 20%)", 100 * pr[1855], 20, 0)
    chk("    highest", pr.idxmax(), 1871)
    pct("    1871 (约 28%)", 100 * pr.max(), 28, 0)
    pct("    1913 (约 20%)", 100 * pr[1913], 20, 0)
    dm = {a: decade_mean(pr, a, b) for a, b in DECADES}
    pct("    1865-1874 (%)", 100 * dm[1865], 24, 0)
    pct("    1875-1884", 100 * dm[1875], 20, 0)
    for a in (1885, 1895, 1905):
        assert abs(dm[a] - 0.20) < 0.015, (a, dm[a])                                  # 20% 上下
    ky = {a: decade_mean(A.k_y, a, b) for a, b in DECADES}
    pct("capital / GDP 1855-1864", ky[1855], 1.51, 2)
    pct("    1905-1913", ky[1905], 1.61, 2)
    k = [ky[a] for a, _ in DECADES]
    assert not all(x < y for x, y in zip(k, k[1:]))                                   # 没有持续上升
    # Okishio
    chk("Okishio 1961; Shaikh 1978; Alberro & Persky 1979", [F["nh_okishio"][0]] + F["nh_shaikh"],
        [1961, 1978, 1979])
    assert "Shaikh" in Q["nh_shaikh"] and "Okishio" in Q["nh_okishio"]
    O = OKISHIO
    old, new = okishio(O["a"], O["l"], O["w"]), okishio(O["a2"], O["l2"], O["w"])
    chk("ex:marx-okishio inputs", [O["a"], O["l"], O["a2"], O["l2"], O["w"], O["w2"]], [0.5, 1, 0.6, 0.5, 0.25, 0.4])
    chk("(1) costs", [old["cost"], new["cost"]], [0.75, 0.725])
    pct("    profit rates (%)", 100 * old["r"], 33.3)
    pct("    ", 100 * new["r"], 37.9)
    assert new["cost"] < old["cost"] and new["r"] > old["r"]
    chk("(2) values", [old["lam"], new["lam"]], [2, 1.25])
    chk("    old: c, v, m, q, m' (%)", [old["c"], old["v"], old["m"], old["q"], 100 * old["mrate"]],
        [1, 0.5, 0.5, 2, 100])
    chk("    new: c", new["c"], 0.75)
    pct("    v", new["v"], 0.156, 3)
    pct("    m", new["m"], 0.344, 3)
    chk("    q, m' (%)", [new["q"], 100 * new["mrate"]], [4.8, 220])
    assert new["q"] / old["q"] > 2 and new["mrate"] / old["mrate"] > 2                 # 都提高了一倍多
    pct("    m'/(1+q) (%)", 100 * new["mrate"] / (1 + new["q"]), 37.9)
    chk("    = the price profit rate (one good)", new["p"], new["r"], tol=1e-12)
    high = okishio(O["a2"], O["l2"], O["w2"])
    chk("(3) cost; profit rate (%)", [high["cost"], 100 * high["r"]], [0.8, 25])
    assert high["r"] < old["r"]
    # the wage squeeze
    ex, re_ = cy["expansions"], cy["recessions"]
    chk("seven expansions, seven recessions", [len(ex), len(re_)], [7, 7])
    chk("profit proxy rises in expansions; falls in recessions",
        [rises(pr, ex), len(re_) - rises(pr, re_)], [5, 6])
    chk("wage share rises in expansions; in recessions", [rises(ws, ex), rises(ws, re_)], [3, 4])
    assert "his payment high or low" in Q["k1_lot"]
    return cy


def deeper(F, Y, Q):
    chk("versions: 1867, 1887; 1885, 1894; Kerr 1909", [Y["k1_value"], Y["k1_organic"], Y["k2_date"], Y["k3_date"],
                                                      Y["k2_depts"]], [1867, 1887, 1885, 1894, 1909])
    # the copy of Untermann's vol. II: printed 1933, copyright page 1909 (its title page and verso, as scanned)
    _, meta = load_snapshot("marx_facts", dtype=str, keep_default_na=False)
    src = meta["sources"]
    assert "copyright 1909" in src["marx1909k2"]["version"] and "printed 1933" in src["marx1909k2"]["version"]
    assert "1859)" in src["evans1859"]["version"]                                    # Evans 1859 年出版
    assert "Wirth" in src["wirth1858"]["version"] and "1858;" in src["wirth1858"]["version"]   # 维尔特 1858 年出版
    # dates: Evans 11 November; the Commons speech 9 November; D1 12 November
    chk("Evans: 10% on 11 November", F["ev_rate10"], [11, 10])
    s = F["ev_rates_commons"]
    chk("the Commons speech: 7% on 12 October; 10% on 9 November", [s[2], s[3], s[8], s[9]], [12, 7, 9, 10])
    D = bank_rate()
    chk("D1: 7% on 15 October; 10% on 12 November", [D[pd.Timestamp("1857-10-15")], D[pd.Timestamp("1857-11-12")]],
        [7, 10])
    chk("Leontief: born 5 August 1906 (autobiography); 1905 (the site's note); died 1999",
        F["nb_born"] + F["nb_1905"] + [F["nb_died"][1]], [5, 1906, 1905, 1999])
    assert "August 5, 1906" in Q["nb_born"] and "Munich" in Q["nb_1905"]
    assert "里昂惕夫（Wassily Leontief，1906—1999，生年一说 1905）" in tex_text()                # the text gives both
    # the transformation: Marx's own answer (vol. III, ch. 9) and Hilferding's reply to Böhm-Bawerk
    assert "Summe der Produktionspreise" in Q["k3_sum"] and "Summe ihrer Werthe" in Q["k3_sum"]
    assert "auf dem Markt gekauft" in Q["k3_market"] and "Kostpreis" in Q["k3_costprice"]
    assert "nicht nöthig" in Q["k3_notnow"]
    chk("Hilferding 1904 (1877—1941)", [Y["hi_total"]] + F["hi_dates"], [1904, 1877, 1941])
    assert "Gesamtwert" in Q["hi_total"] and "Einzelware" in Q["hi_single"] and "Zirkulation" in Q["hi_production"]
    assert "Gesamtmehrwert" in Q["hi_profit"] and "quantitativ bestimmt" in Q["hi_quantity"]
    assert "希法亭（Rudolf Hilferding，1877—1941）1904 年" in tex_text()


def legacy(F, Y, Q):
    chk("Nobel 1973", Y["nb_citation"], 1973)
    chk("The Structure of American Economy, 1919-1929", F["nb_1941"], [1919, 1929])
    assert "centrally planned" in Q["nb_planning"] or "planned" in Q["nb_planning"]
    assert "three departments" in Q["ka_three"] and "schemes of reproduction" in Q["ka_schemes"]
    assert "workers do not save" in Q["ka_save"]
    assert Q["ka_profits"].startswith("Gross profits = Gross investment")
    chk("Kalecki: developed in 1935", F["ka_1935"], [1935])


def takeaways_and_selfcheck(F, E, A, cy):
    chk("takeaways: 10% a year after the first", [round(100 * (E.total[t] / E.total[t - 1] - 1), 6)
                                                  for t in range(2, 6)], [10, 10, 10, 10])
    e = A.real_earnings_1900_100
    pct("    real earnings +86%", 100 * (e[1913] / e[1855] - 1), 86, 0)
    g = np.diff(cy["peaks"])
    chk("    peaks 4 to 11 years apart", [g.min(), g.max()], [4, 11])
    # 1
    s = SC1
    IIc = s["v"] + s["m"]
    vII = IIc / s["q"]
    chk("SC1: II c; v, m; product", [IIc, vII, s["rate"] * vII, IIc + vII + s["rate"] * vII], [1500, 750, 750, 3000])
    # 2
    m1, q, p = rates(SC2["c"], SC2["v"], SC2["m"])
    chk("SC2: m' (%), q, p' (%)", [100 * m1, q, 100 * p], [150, 3, 37.5])
    chk("    = 1.5/(1+3)", p, m1 / (1 + q))
    chk("    c + v", SC2["c"] + SC2["v"], 800)
    # 3
    v = SC3["v"]
    chk("SC3: p' (%) at m' 100%, 200%", [100 * SC3["rate1"] * v / (SC3["c"] + v), 100 * SC3["rate2"] * v / (SC3["c"] + v)],
        [25, 50])
    chk("    c + v", SC3["c"] + v, 400)
    # 4
    E60 = expanded(F, n=0, share=SC4["share"]).iloc[0]
    chk("SC4: I accumulates 600: Δc, Δv; consumes", [E60.dcI + E60.dvI, E60.dcI, E60.dvI, E60.mkI], [600, 480, 120, 400])
    chk("    1000 + 120 + 400", E60.lhs, 1520)
    chk("    II: Δc, Δv; consumes", [E60.dcII, E60.dvII, E60.mkII], [20, 10, 720])
    chk("    750 - 30", E60.dcII + E60.dvII, 30)
    assert E60.dcII + E60.dvII < expanded(F, n=0).iloc[0].dcII                        # I more, II less
    # 5
    s = SC5
    pi = s["investment"] + s["consumption"]
    chk("SC5: profits; after the cut", [pi, s["investment"] + s["consumption"] - s["cut"]], [140, 130])


def main():
    df = _rows()
    F, Y, Q, J = facts(), years(), quotes(), column("juan")
    M, D, A, C = monthly(), bank_rate(), annual(), clark()
    check_readings(df)
    check_text(df)
    opening(F, Y, Q, D)
    world(F, Y, Q, M, D)
    accumulation(F, Q)
    E = schemes(F, Q, J)
    profit(F, Y, Q, J)
    crisis(F, Y, Q, J)
    hamburg(F, Y, Q)
    cy = test(F, Y, Q, A, C)
    deeper(F, Y, Q)
    legacy(F, Y, Q)
    takeaways_and_selfcheck(F, E, A, cy)
    anchors("zh/ch22_marx.tex", df["id"], script=Path(__file__))
    print("all Chapter 22 checks passed")


if __name__ == "__main__":
    main()
