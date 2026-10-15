"""Chapter 21 (工业革命与大分流): every number and every quotation in zh/ch21_divergence.tex.

    python3 checks/check_ch21.py

Inputs:
  divergence_facts                     quotations of Malthus (1798), of four EH.Net reviews (Lal on Pomeranz 2000,
                                       Leunig on Allen 2009, Harley on Mokyr 2009, Margo on Clark 2007), of Allen,
                                       Bassino, Ma, Moll-Murata and van Zanden (2009), Broadberry, Guan and Li (2017),
                                       Broadberry and Gupta (2005), Humphries and Schneider (2018, 2019), Allen (2018)
                                       and Acemoglu, Johnson and Robinson (2002) (checked by
                                       data/fetch/verify_web_quotes.py)
  maddison2023_divergence              Maddison Project Database 2023: GDP per head (2011 dollars) and population of
                                       the United Kingdom, the Netherlands, China, India, Japan and the United States,
                                       1500-1913
  gpih_allen2011_welfare               the welfare ratios of Allen et al. (2011): ten cities, 1730-1913
  clark2015_england_decadal_1250_1860  Clark: England by decade, population, land rents, wage income, real NNI per
                                       head and real wages, 1250-1860
  boe_millennium_england_1270_1913     Bank of England, A Millennium of Macroeconomic Data: the population of England
                                       (to 1870) and its real GDP per head (Broadberry et al. 2015), 1270-1913
The figure module figsrc/fig_ch21.py imports the functions defined here.

What is checked here:
  1. readings   every number of the value column of divergence_facts is read from its quotation: digits, English
                number words, fractions and the cells of the printed tables
  2. the text   every “…” in the chapter is the chapter's Chinese rendering of a quotation (TRANSLATIONS:
                rendering -> row or rows) or a term of the text (ALLOW)
  3. numbers    every number of the text, section by section, with quoted()

Models (the chapter's key equations):
    the Malthusian escape   ln y' - ln y = g - alpha ln(L'/L),  L'/L = (y/ybar)^beta,
                            so z' = (1 - alpha beta) z + g,  z* = g / (alpha beta),  z = ln(y/ybar)   (eq:divergence-escape)
                            (beta = 1, g = 0: Chapter 11's eq:medieval-dynamics)
    unit labour costs       ULC/ULC* = (W/W*) / (y/y*);  A/A* = (W/W*)^a (C/C*)^(1-a) / (P/P*)       (eq:divergence-ulc)
    growth accounting       g_TFP = dln(Y/L) + alpha dlnL  (land fixed, Cobb-Douglas)               (sec:divergence-test)
"""
from __future__ import annotations

import math
import re

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

import check_ch18
from common import ROOT, load_snapshot, quoted

TEX = ROOT / "zh" / "ch21_divergence.tex"
WAN = 1e4                                  # 万

# Teaching inputs stated in the text
GEN = 30                                   # years in a generation
PLATEAU = dict(alpha=0.25, beta=1.0, tfp=0.0025)      # ex:divergence-plateau (1)-(2): TFP growth a year
FAST = dict(alpha=0.15, beta=1.0, tfp=0.008)          # ex:divergence-plateau (3)
SLOW_POP = 0.5                                        # fig:div_model: beta halved
GENS = 10                                             # fig:div_model: generations drawn
# self-check questions
SC1 = dict(pop=10, years=100, double=25, food=10)     # millions; arithmetic growth of food: +10 m a 25 years
SC2 = dict(alpha=0.2, beta=0.5, tfp=0.004)
SC3 = dict(wage=30, basket=8, rent=0.05, adults=3)    # taels a year; one adult's basket
SC4 = dict(w=400, y=200, w2=400, y2=500)              # comparative wages and productivity, India = 100
SC5 = dict(dly=0.3, dlL=0.6, alpha=0.2)               # % a year
SC6 = dict(pop=1.5, alpha=0.3)                        # population x1.5


def chk(what: str, value, expected=None, tol: float = 1e-9, rel: float = 0.0) -> float:
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
    df, meta = load_snapshot("divergence_facts", dtype=str, keep_default_na=False)
    assert 21 in meta["used_in"]
    assert df["id"].is_unique
    return df


def meta() -> dict:
    return load_snapshot("divergence_facts")[1]


def num(x: str) -> float:
    """'5', '1/2', '2+1/2'."""
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
    return {r.id: r.quote for r in _rows().itertuples()}


def column(name: str) -> dict[str, str]:
    return {r.id: getattr(r, name) for r in _rows().itertuples()}


COUNTRIES = [("GBR", "英国", "Britain"), ("NLD", "荷兰", "Netherlands"), ("CHN", "中国", "China"),
             ("IND", "印度", "India"), ("JPN", "日本", "Japan"), ("USA", "美国", "United States")]


def maddison() -> tuple[pd.DataFrame, pd.DataFrame]:
    """GDP per head (2011 dollars) and population (thousands): year x country, NaN where there is no estimate."""
    df, m = load_snapshot("maddison2023_divergence")
    assert 21 in m["used_in"]
    g = df.pivot(index="year", columns="country", values="gdppc_2011usd")
    p = df.pivot(index="year", columns="country", values="pop_thousands")
    return g, p


CITIES = [("london", "伦敦", "London"), ("amsterdam", "阿姆斯特丹", "Amsterdam"), ("milan", "米兰", "Milan"),
          ("beijing", "北京", "Beijing"), ("suzhou_shanghai", "苏州/上海", "Suzhou/Shanghai"),
          ("canton", "广州", "Canton"), ("kyoto_tokyo", "京都/东京", "Kyoto/Tokyo"), ("bengal", "孟加拉", "Bengal")]


def welfare() -> pd.DataFrame:
    df, m = load_snapshot("gpih_allen2011_welfare")
    assert 21 in m["used_in"]
    return df.set_index("year")


def decade_mean(s: pd.Series, a: int, b: int) -> float:
    """The mean of the years with a value in a..b (the series has gaps)."""
    v = s.loc[a:b].dropna()
    assert len(v), (s.name, a, b)
    return float(v.mean())


def clark() -> pd.DataFrame:
    """Clark's decades, with the land share alpha = rents / (rents + wage income)."""
    df, m = load_snapshot("clark2015_england_decadal_1250_1860")
    assert 21 in m["used_in"]
    c = df.set_index("decade")
    c["alpha"] = c.land_rents_gbp_m / (c.land_rents_gbp_m + c.wage_income_gbp_m)
    return c


def boe() -> pd.DataFrame:
    df, m = load_snapshot("boe_millennium_england_1270_1913")
    assert 21 in m["used_in"]
    return df.set_index("year")


# ---------------------------------------------------------------------------------------------------
# The arithmetic of the chapter
def growth(s: pd.Series, a: int, b: int) -> float:
    """Average growth, % a year (logarithmic)."""
    return 100 * math.log(s[b] / s[a]) / (b - a)


def doubling(s: pd.Series, a: int, b: int) -> float:
    """Years to double at the average growth of a..b."""
    return math.log(2) / (math.log(s[b] / s[a]) / (b - a))


def boe_decades(B: pd.DataFrame) -> pd.Series:
    """The BoE real GDP per head of England by decade (mean of the ten years), 1860s = 100."""
    y = B.england_real_gdp_pc_2013gbp.loc[1270:1869]
    d = y.groupby((y.index // 10) * 10).mean()
    return 100 * d / d[1860]


def tfp(C: pd.DataFrame, a: int, b: int) -> dict:
    """Growth accounting a..b, decade by decade: g_TFP = dln(Y/L) + alpha dlnL, alpha the mean of the two decades;
    % a year. Also the growth of income per head and of population, and the mean land share."""
    ly, lL = np.log(C.real_nni_pc_1860s_100), np.log(C.pop_england_m)
    am = (C.alpha + C.alpha.shift(1)) / 2
    g = (ly.diff() + am * lL.diff()).loc[a + 10:b]
    n = b - a
    return dict(tfp=100 * g.sum() / n, y=100 * (ly[b] - ly[a]) / n, L=100 * (lL[b] - lL[a]) / n,
                alpha=float(C.alpha.loc[a:b].mean()))


def _ols(s: pd.DataFrame):
    return smf.ols("ly ~ lL", data=s).fit(cov_type="HAC", cov_kwds={"maxlags": 3})


def frontier(C: pd.DataFrame, a: int, b: int, col: str = "real_nni_pc_1860s_100"):
    """ln(real income per head) on ln(population), Clark's decades a..b, with HAC standard errors (three lags)."""
    return _ols(C.loc[a:b].assign(ly=np.log(C[col]), lL=np.log(C.pop_england_m)))


def boe_frontier(B: pd.DataFrame, a: int, b: int):
    """The same with the decade means of Broadberry et al. (real GDP per head and population), decades a..b."""
    y = B.england_real_gdp_pc_2013gbp.loc[a:b + 9]
    L = B.pop_england_m.loc[a:b + 9]
    d = pd.DataFrame(dict(ly=np.log(y.groupby((y.index // 10) * 10).mean()),
                          lL=np.log(L.groupby((L.index // 10) * 10).mean())))
    return _ols(d)


def escape(z0: float, g: float, alpha: float, beta: float, n: int) -> list[float]:
    """eq:divergence-escape: z' = (1 - alpha beta) z + g, n generations from z0."""
    z = [z0]
    for _ in range(n):
        z.append((1 - alpha * beta) * z[-1] + g)
    return z


def plateau(g: float, alpha: float, beta: float) -> float:
    return g / (alpha * beta)


def half_life(alpha: float, beta: float) -> float:
    """Generations for the gap to the plateau (in logs) to halve."""
    return math.log(0.5) / math.log(1 - alpha * beta)


# ---------------------------------------------------------------------------------------------------
# 1. Readings of the numbers
WORDS = {"a": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
         "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
         "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
ORDINALS = {"eighteenth": 18}
VULGAR = {"½": 0.5}


def _words(s: str) -> list[str]:
    return s.lower().replace("-", " ").split()


def cardinal(s: str) -> float:
    """An English cardinal ('twenty-five', 'one hundred and twelve'); a unit word after it ('millions') ends it."""
    total, cur, seen = 0.0, 0.0, False
    for w in _words(s):
        if w in WORDS:
            cur += WORDS[w]
        elif w == "hundred":
            cur = (cur or 1) * 100
        elif w == "thousand":
            total += (cur or 1) * 1e3
            cur = 0
        elif w == "and" and seen:
            continue
        else:
            break
        seen = True
    assert seen, s
    return total + cur


def figure(s: str) -> float:
    return float(s.replace(",", ""))


FIGURES = re.compile(r"\d[\d,]*(?:\.\d+)?")


def read(phrase: str, how: str) -> list[float]:
    if how == "num":
        return [figure(phrase)]
    if how == "en":
        return [cardinal(phrase)]
    if how == "half":                         # 'seven millions and a half'
        assert phrase.endswith("and a half"), phrase
        return [cardinal(phrase) + 0.5]
    if how == "or hundred":                   # 'three or four hundred': 300 or 400
        a, o, b, h = _words(phrase)
        assert (o, h) == ("or", "hundred"), phrase
        return [WORDS[a] * 100, WORDS[b] * 100]
    if how == "ordinal":
        return [ORDINALS[phrase]]
    if how == "vulgar":                       # '2½'
        return [figure(phrase[:-1]) + VULGAR[phrase[-1]]]
    if how == "note":                         # a page number given in the year_note, not in the quotation
        return [figure(x) for x in FIGURES.findall(phrase)]
    raise ValueError(how)


EN = "en"
# id -> [(phrase in the quotation, how it is read)], in order. Rows not listed are read with all the figures of the
# quotation (the cells of a printed table among them).
READINGS = {
    "mt_usa": [("twenty-five", EN)],
    "mt_rule": [("twenty-five", EN)],
    "mt_island": [("seven", EN)],
    "mt_century": [("one hundred and twelve", EN), ("thirty-five", EN), ("seventy-seven", EN)],
    "mt_seven": [("seven", EN), ("seven millions and a half", "half"), ("eight", EN)],
    "mt_europe": [("twenty-five", EN), ("three or four hundred", "or hundred")],
    "pz_seasia": [("p. 200", "note")],
    "lg_wages": [("p. 2", "note")],
    "hr_beliefs": [("p. 478", "note")],
    "mg_genetic": [("p. 8", "note")],
    "lg_ch2": [("2", "num"), ("eighteenth", "ordinal")],
    "al11_three": [("three", EN)],
    "al11_one": [("one", EN)],
    "al11_four": [("four", EN)],
    "bg_ellison": [("2½", "vulgar")],
    "al18_40": [("40", "num")],
    "al18_109": [("1.09", "num"), ("one", EN), ("2.18", "num")],
}


def check_readings(df: pd.DataFrame) -> None:
    n = 0
    for r in df.itertuples():
        if not r.value:
            assert r.id not in READINGS, r.id
            continue
        vals = [num(x) for x in r.value.split(";")]
        quote = " ".join(r.quote.split())                  # the line breaks of the source
        if r.id in READINGS:
            got, pos = [], 0
            for phrase, how in READINGS[r.id]:
                if how == "note":
                    assert phrase in r.year_note, f"{r.id}: {phrase!r} not in the year_note"
                else:
                    k = quote.find(phrase, pos)
                    assert k >= 0, f"{r.id}: {phrase!r} not found (in order) in the quotation"
                    pos = k + len(phrase)
                got += read(phrase, how)
        else:
            got = [figure(x) for x in FIGURES.findall(quote)]
        assert [round(g, 9) for g in got] == [round(v, 9) for v in vals], f"{r.id}: read {got}, value column {vals}"
        n += 1
    quoted("rows with values, each read from its quotation", n, 125)


# ---------------------------------------------------------------------------------------------------
# 2. Every “…” of the text against the snapshot
# terms of the text, which are not quotations
ALLOW = {"千年宏观数据", "工作日", "一天", "对了方向", "完全对", "欧洲与亚洲"}
# the chapter's Chinese renderings of the quotations: rendering -> row (or rows)
TRANSLATIONS = {
    # opening
    "第一，食物是人类生存所必需的": "mt_food",
    "第二，两性间的情欲是必然的，并将几乎保持现状": "mt_passion",
    "人口增长的能力无限大于土地为人类生产生活资料的能力": "mt_power",
    "人口在不受抑制时按几何级数增长，生活资料只按算术级数增长。": "mt_ratio",
    "二十五年就翻了一番": "mt_usa",
    "每二十五年翻一番": "mt_rule",
    "这个岛的人口据计算约为七百万": "mt_island",
    "第一个世纪结束时，人口将是一亿一千二百万，而生活资料只够养活三千五百万，剩下七千七百万人完全没有着落": "mt_century",
    "国家财富的增长对改善劳动贫民的处境几乎没有或完全没有作用。": "mt_wealth",
    # sec:divergence-world
    "不是每二十五年翻一番，而是要三四百年或更久": "mt_europe",
    "确实一直在迅速前进": "mt_commerce",
    "主要是劳动的产品，而不是土地的产品": "mt_produce",
    "维持劳动的实际基金增加得很慢": "mt_funds",
    "我相信，他们并没有更多地支配生活必需品与便利品": "mt_command",
    "比起革命时期，他们中有大得多的一部分在制造业里做工，挤在狭窄而不卫生的屋子里": "mt_rooms",
    "亚当·斯密博士说，中国大概早已富到它的法律与制度所容许的程度": "mt_smithchina",
    "换一套法律与制度，再重视对外贸易，它还可以富得多": "mt_richer",
    "中国是世界上土地最肥沃的国家，几乎所有的土地都在耕种": "mt_fertile",
    "相对于它的资本所能雇用的人数，人口相当过多": "mt_overpeople",
    "劳动如此充裕，没有人费心去节省它": "mt_abridge",
    "靠劳动者之多、劳动之便宜，可以制造数量极大的制成品向外国出售": "mt_manufactures",
    "主要是从世界各地收集来的奢侈品": "mt_luxuries",
    # sec:divergence-malthus
    "原来养活七百万人的食物，现在要分给七百五十万或八百万人": "mt_seven",
    "劳动的价格必定趋于下降，同时食物的价格趋于上涨": "mt_price",
    "劳动者于是必须更辛苦地劳动，才能挣到和以前一样多的东西": "mt_harder",
    "结婚的阻碍与养家的困难如此之大，人口停滞不前": "mt_stand",
    "鼓励耕种者在土地上使用更多的劳动，开垦新的土地，给已经耕种的土地更充分地施肥与改良": "mt_cultivators",
    "劳动者的处境于是又相当舒适了，对人口的限制在某种程度上放松": "mt_loosened",
    "幸福方面同样的倒退与前进的运动周而复始": "mt_repeated",
    "对养家之难的预见起着预防性抑制的作用；下层阶级中一些人的实际困苦，使他们不能给孩子适当的食物与照料，则起着积极性抑制的作用。":
        "mt_checks",
    # sec:divergence-takeoff
    "1780 年到 1800 年，产出每年增长 10.8\\%，出口则以惊人的每年 14.0\\% 扩张。": "bg_rates",
    "对于可靠的数字（A 级），所报告的序列的误差范围被判断为不到正负 5\\%": "bgl_gradeA",
    "对于较好的估计（B 级），误差范围为正负 5\\%—15\\%": "bgl_gradeB",
    "粗略的估计（C 级）为正负 15\\%—25\\%，猜测（D 级）则超过正负 25\\%": "bgl_gradeC",
    "从 1393 年的约正负 10\\% 降到 19 世纪中叶的正负 6\\%": "bgl_perkins",
    "也许更恰当的是采纳 Perkins 的建议，即 80\\% 的置信区间": "bgl_perkins80",
    # sec:divergence-when
    "相当令人信服地表明，直到十八世纪的世纪之交，中国与欧洲的核心地区之间生活水平并没有明显的分流": "lal_parity",
    "晚至 1750 年，长江三角洲与英格兰之间的相似之处仍多于不同之处": "lal_1750",
    "核心地区": "lal_parity",
    "那么，英格兰与随后的欧洲为什么没有走它们远东表亲那种劳动密集的‘勤劳革命’之路，而走上了资本密集的工业革命之路？": "lal_path",
    "仅够糊口": "al11_2259",
    "乘以三，代表一个家庭的年度预算": "al11_three",
    "我们现在再把它们提高 5\\%，这是对房租最低限度的估计": "al11_rent",
    "我们假定一年的工作是 250 天": "al11_250",
    "这类实际工资指数叫作‘福利比率’。": "al11_called",
    "等于一，一个全时工作的非熟练劳动者挣的正好够按糊口的收入养活一家": "al11_one",
    "中国的城市与意大利的城市并列最后一名，后者是欧洲生活水平最低的": "al11_tie",
    "那里的实际工资并不明显高于北京或广州": "al11_yangzi",
    "中国与日本主要城市的非熟练劳动者——尽管很穷——同中欧与南欧的同类劳动者生活水平大体相同": "al11_surprise",
    "只有英格兰与低地国家领先于其他地区": "al11_lowc",
    "反驳修正派的说法，即长江三角洲这样的中国先进地区在工业革命前夕与英格兰不相上下": "al11_dispute",
    "继续下滑，直到世纪中叶的太平天国起义，那时达到了危及生命的低水平": "al11_taiping",
    "秩序恢复以后，生活水平缓慢改善，一直到 20 世纪初": "al11_restored",
    "1913 年欧洲与中国之间的差距，大部分来自欧洲的进步，而不是中国的衰退。": "al11_1913",
    "荷兰经济在 19 世纪初步履蹒跚": "al11_dutch",
    "不过，到世纪中叶，增长恢复了，实际工资攀上新的高度": "al11_resumed",
    "Pomeranz 估计，一个全年受雇的男性农业劳动者大约能挣 12 两银子": "al11_p12",
    "维持一家人‘仅够糊口’的费用是 22.59 两": "al11_2259",
    "Li 与 Pomeranz 都认为这大约是可能的最多天数": "al11_woman",
    "勉强养得活自己，更不用说妻子与孩子了": "al11_barely",
    "只要不出什么意外，一家人靠这些可以活下去": "al11_survive",
    "也远远落后于伦敦或阿姆斯特丹": "al11_behind",
    "中国在北宋时期的生活水平领先世界，但到 1300 年已经落后于意大利": "bgl_song",
    "到 1750 年，差距已经大到不能用中国内部的地区差别来弥合，大分流在工业革命以前就已经开始了": "bgl_1750",
    "到 1840 年降到 980 年水平的约 70\\%": "bgl_70",
    "比全中国约高 75\\%": "bgl_1050",
    "长江三角洲的人均 GDP 晚至 1700 年仍是欧洲领先国家水平的 93\\%": "bgl_93",
    "到 1750 年，荷兰的人均 GDP 比长江三角洲高 42\\%，到 1770 年领先 90\\%": "bgl_dutch",
    "新共识": "bgl_consensus",
    "得到 472 元，这已经很接近 400 元的仅够糊口的水平，因而是一个有效的下限": "bgl_472",
    "在中国，人口数据在这里所涉及的整个时期都有系统的记录，与征税有关。": "bgl_recorded",
    "一般认为，官员是能够准确记录人口数目的": "bgl_accurate",
    "官员有很强的动机正确地估计人口": "bgl_incentive",
    "提高到每年 0.70\\%": "bgl_qing",
    "相当令人信服": "lal_parity",
    # sec:divergence-why
    "工资高得出奇，能源便宜得出奇": "lg_wages",
    "工业革命在英国被触发，是因为这个国家异常高的工资与便宜的能源价格": "al18_trigger",
    "英国的要素价格使使用——因而发明——提高劳动生产率的机器技术有利可图，这种技术靠的是增加每个工人使用的资本与能源": "al18_prices",
    "这种不寻常的价格结构，可以归因于英国的帝国政策造成的贸易繁荣": "al18_trade",
    "独一无二地有利可图": "lg_profitable",
    "提出了 18 世纪英国工人按国际标准是富裕的证据": "lg_ch2",
    "除了 Greg Clark，所有人都会大体接受这一章": "lg_clark",
    "相反，城市的高工资使人们离开，这又导致生产率上升": "lg_city",
    "承认启蒙的经济是必要的，但用欧洲的证据论证它是不充分的": "lg_mokyr",
    "国内生产者没有试图模仿印度劳动密集的生产方法，那在英国的工资水平下在经济上不可能行得通": "bg_imitate",
    "由英国比印度高得多的工资所推动的、对节省劳动的发明的探索，这时已经开始了": "bg_search",
    "印度的非熟练劳动者挣的只比英格兰非熟练工资的 20\\% 多一点": "bg_silver20",
    "在英格兰要花一先令的劳动，在印度两便士就能得到": "bg_shilling",
    "印度的谷物价格也相对便宜": "bg_grain",
    "同印度生产者竞争的英国厂商必须按白银工资考虑问题，因为它们必须按世界的白银价格在世界市场上出售": "bg_world",
    "到 1750 年雇用了一百多万妇女与儿童": "hs_million",
    "纺纱这个工业化的主导部门，并不存在这样的‘高工资经济’": "hs_nohwe",
    "机械化的动机必须到别处去找": "hs_elsewhere",
    "确实在缓慢上升，但速度只有每年 0.3\\%": "hs_03",
    "在 1760 年代与 1770 年代的纺纱发明之前，纺纱工的名义工资、实际工资与相对工资都没有大的跳跃": "hs_nojump",
    "即使按当时女性劳动市场的标准，纺纱的报酬也相对较低": "hs_poorly",
    "没有出现高峰": "hs_gun",
    "冒烟的枪": "hs_gun",
    "体面": "hs_welfare",
    "用名义工资除以 Allen 的‘体面’篮子里一个成年人的生活费用": "hs_welfare",
    "制造商作为一个买方垄断的卡特尔行事": "hs_cartel",
    "克服低生产率与纱线质量的不稳定，利用就业不足的妇女与儿童的低工资，这些也许才是修补匠与发明家的动机": "hs_motives",
    "不知道纺纱工工作了多少小时，所以这些数据不能确定她们每小时的工资（这才是相关的变量）是高还是低": "al18_hours",
    "这些信息主要来自学校与慈善项目，项目的参加者正是因为没有生产力才被选中的": "al18_selected",
    "典型的纺纱工只工作全时的 40\\%，只挣到全时收入的 40\\%": "al18_40",
    "每磅花 9 便士，清棉与梳棉合起来又是 9 便士": "al18_9d",
    "纺一磅棉花需要 1.09 天的劳动，纺纱的全部工序，包括准备与梳棉，共需 2.18 天": "al18_109",
    "1750 年代与 1760 年代受雇为仆人的妇女隐含的平均日收入是每天 8.275 便士": "al18_8275",
    "如果工业革命发生在印度，Humphries 与 Schneider 关于低工资导致机械化的看法就值得认真考虑。但它没有发生在印度。": "al18_india",
    "高工资假说并没有因为 Humphries 与 Schneider 的批评而受损。": "al18_unimpaired",
    "为我们的数据集增加了 1500 多个新的观测值": "hs19_1500",
    "即使同其他女工相比也很低，其变化轨迹也不能解释珍妮纺纱机的发明与推广": "hs19_low",
    "质疑这样一个奇怪的假定：纺纱工虽然贫困，却选择放弃挣钱的机会而宁要闲暇": "hs19_leisure",
    "在原地空转纺车的是 Allen 教授，不是我们。": "hs19_wheels",
    "为英国工业革命提供燃料的煤，在地理上对 18 世纪中国南方的核心地区并不那么容易得到，因为它集中在西北": "lal_coal",
    "把长江三角洲与西北的煤矿连起来，回报是巨大的，但这些回报事前是看不见的": "lal_invisible",
    "Pomeranz 对大分流原因的回答的第二部分，是欧洲对新大陆的发现与开发——部分是通过贸易": "lal_newworld",
    "无疑扩展了欧洲的土地边疆": "lal_frontier",
    "幽灵土地": ("bgl_ghost", "bgl_roots"),
    "像接触以后的新大陆一样，人口稀少，能够供给大量‘国内’需要的土地密集型资源；中国人大量去了那里，但东南亚从来没有成为沿海中国的新大陆":
        "pz_seasia",
    "在没有国家支持的情况下在东南亚立足": "pz_backing",
    "由 Hartwell 记录的煤铁联合体的惊人发展": "lal_hartwell",
    "几乎具备了这场革命的所有要素，可它仍然没有发生": "lal_song",
    "在恒河平原的东部，即今天的比哈尔": "lal_core",
    "我们现在知道，这个地区也有印度的煤炭储藏": "lal_bihar",
    "尽管如此，没有人认为印度人本可以发展出煤与蒸汽的工业革命": "lal_noone",
    "承认从新大陆流入欧洲的土地密集型产品，增量不可能很大": "lal_admits",
    "所以，正如韦伯以及近来的 Landes 都坚持的，我们又回到了文化。": "lal_culture",
    "我们与启蒙运动联系在一起的那套不断变化的信念": "hr_beliefs",
    "一个社会，其中占主导的是这样一种心态：相信通过观察与实验获得的有用知识可以带来进步": "hr_define",
    "持续的变化取决于持续的技术进步，而技术进步又取决于知识及其发展的过程": "hr_knowledge",
    "所谓工业启蒙，似乎至少是在描述成功的变化是什么样子，而不是它的原因": "hr_cause",
    "没有完全说服人：为什么一场英国特有的工业启蒙，应当在理解 18 世纪现代经济增长的出现时占首要的位置": "hr_notfully",
    "问题在于，这样的改进太零星、太有限了": "mg_sporadic",
    "要得到持续的经济增长，我们需要持续的全要素生产率增长": "mg_tfp",
    "在文化上，或许也在遗传上": "mg_genetic",
    "尤其是耐心": "mg_patience",
    "第六章根据遗嘱提出证据，表明生育上的成功（男人有多少个孩子）与去世时的财富正相关": "mg_wills",
    "中产阶级的": "mg_values",
    "只等着技术的持续进步一旦到来就加以利用": "mg_passed",
    "Clark 的回答是，中国等地的人口增长更快（更马尔萨斯），富人生育上的成功更少": "mg_china",
    "认为所有相关的制度在工业革命之前很久就已经在英格兰具备了": "mg_institutions",
    "即使只看表面，我该相信这些数据吗？": "mg_trust",
    "让良好的行为代代相传的，究竟是什么机制？": "mg_mechanism",
    "我认为，任何单一的故事都不太可能解释国家的财富。": "mg_single",
    "1500—1850 年（西）欧的兴起，主要可以由有通向大西洋通道的欧洲国家的增长来解释，尤其是那些从事殖民与远洋长途贸易的国家":
        "ajr_atlantic",
    "1500 年以后同新大陆、非洲与亚洲贸易的增长，壮大了商业资产阶级中的新的部分，使这些群体能够要求、得到并维持保护其产权的制度变革":
        "ajr_bourgeois",
    "最重要的制度变化，以及因此最大的经济收益，出现在原有制度对君主有某些制约、尤其是限制了君主对海外贸易控制的国家。": "ajr_checks",
    "欧洲的兴起，主要是晚期中世纪的制度与‘大西洋贸易’提供的经济机会相互作用所推动的资本主义发展的结果": "ajr_result",
    "这表明大分流有深厚的制度根源，而不是因为煤或‘幽灵土地’之类的因素突然出现的": "bgl_roots",
    # the case of India
    "为英国制造商开辟了新的机会，即进口替代与转口替代的策略": "bg_eic",
    "已经成为世界上最重要的棉纺织品生产国，支配着世界的出口市场，甚至向印度出口": "bg_dominate",
    "从 1701 年起，从印度进口的印花布与其他某些种类的棉布被禁止": "bg_1701",
    "1701 年的《印花布法》仍然允许从印度进口白棉布在英国印花，直到 1721 年的进一步立法禁止了这种进口，除非是为了转口": "bg_1721",
    "一直有效到 1774 年": "bg_1774",
    "保护对英国棉纺织业的作用似乎是中性的，《印花布法》被规避了": "bg_neutral",
    "如果《印花布法》成功了，英国棉纺织业也许会像美国的同行一样，永远不能在世界市场上竞争": "bg_us",
    "1770 年，英国的工资约为印度的 6 倍，但英国的劳动生产率只比印度高两到三倍": "bg_1770",
    "到 1820 年，由于英国的生产率提高到 6.53 倍，并假定印度停滞，英国的生产率上升到印度水平的 1625\\%": "bg_1625",
    "由于这时英国的工资已经回落到印度水平的 517\\% 左右，英国的单位劳动成本已经低于印度": "bg_517",
    "1818 年，达卡的商馆关闭了。促使董事会在 1818 年放弃它的，不是运费，也不是保护性关税，而是英国同类棉制品价格的大幅下降": "bg_dacca",
    "一直到 1860 年代都给了印度生产者在本国市场上的优势": "bg_transport",
    "只是在 1850 年以后才下降": "bg_twomey2",
    "1680—1770": "bg_fn8",
    # the deeper box
    "Princeton: Princeton University Press, 2010": "hr_header",
    "星号表示作为计价标准的国家，这里是英国": "bg_numeraire",
    "星号表示外国，这里取为印度": "bg_foreign",
    "我们假定最初的离岸价格之比是 200": "bg_fob200",
}


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
def n_max(F) -> float:
    """Malthus's unchecked growth, doubling in 25 years: % a year as a fraction."""
    return math.log(2) / F["mt_rule"][0]


def opening(F, Y, B, G):
    chk("Malthus, first edition", Y["mt_food"], 1798)
    chk("North America: twenty-five years; the rule", F["mt_usa"] + F["mt_rule"], [25, 25])
    m, d = F["mt_island"][0], F["mt_rule"][0]
    n = 100 / d                                            # doublings in a century
    chk("the Island: seven millions", m, 7)
    chk("a century: 112, 35, 77 millions", [m * 2 ** n, m * (1 + n), m * 2 ** n - m * (1 + n)], F["mt_century"])
    L, y = B.pop_england_m, B.england_real_gdp_pc_2013gbp
    pct("England 1800 (万)", 100 * L[1800], 862, 0)
    pct("    1850 (万)", 100 * L[1850], 1651, 0)
    pct("    ratio", L[1850] / L[1800], 1.915, 3)
    pct("    doubling every 25 years, 1850 (万)", 100 * L[1800] * 2 ** (50 / d), 3448, 0)
    pct("GDP per head 1800-1850 (%)", 100 * (y[1850] / y[1800] - 1), 25.0)
    pct("    1270-1700", y[1700] / y[1270], 2.07, 2)
    chk("    four hundred and more years", 1700 - 1270, 430)
    pct("    1700-1913", y[1913] / y[1700], 3.26, 2)
    pct("MPD: Britain / China 1700", G.GBR[1700] / G.CHN[1700], 1.56, 2)
    pct("    1913", G.GBR[1913] / G.CHN[1913], 8.34, 2)
    chk("Pomeranz (2000)", Y["lal_parity"], 2000)


def world(F, Y, B, G):
    chk("Europe: 25 years; 300 or 400", F["mt_europe"], [25, 300, 400])
    L = B.pop_england_m
    pct("England doubling 1700-1770 (years)", doubling(L, 1700, 1770), 205, 0)
    pct("    1750-1780", doubling(L, 1750, 1780), 107, 0)
    pct("    1780-1820", doubling(L, 1780, 1820), 61.0)
    pct("    1800-1850", doubling(L, 1800, 1850), 53.3)
    J = column("juan")
    assert J["mt_commerce"] == J["mt_rooms"] == J["mt_smithchina"] == "ch. XVI"      # 第十六章
    tab = {1700: dict(NLD=3377, GBR=2412, CHN=1543, IND=1162, JPN=1073),
           1820: dict(GBR=3306, NLD=3006, USA=2674, JPN=1317, CHN=882),
           1913: dict(USA=10108, GBR=8212, NLD=6454, JPN=2431, IND=1073, CHN=985)}
    for yr, row in tab.items():
        for c, v in row.items():
            pct(f"MPD {yr} {c} (2011 dollars)", G.loc[yr, c], v, 0)
    assert G.loc[1700].idxmax() == "NLD" and pd.isna(G.USA[1700]) and pd.isna(G.IND[1820])
    chk("MPD: 1500-1913", [G.index.min(), G.index.max()], [1500, 1913])
    both = G[["GBR", "NLD"]].dropna()
    ahead = both.GBR > both.NLD
    chk("Britain passes the Netherlands", ahead.idxmax(), 1808)
    assert ahead.loc[1808:].all()
    nld = G.NLD.reindex(range(1808, 1816))
    assert nld.loc[1809:1814].isna().all() and nld[[1808, 1815]].notna().all()        # no figures 1809-1814
    both = G[["GBR", "USA"]].dropna()
    ahead = both.USA > both.GBR
    chk("the United States first above Britain", ahead.idxmax(), 1880)
    chk("    above from", max(ahead.index[~ahead]) + 1, 1899)
    assert ahead.loc[1899:].all()


def malthus_model(F):
    chk("food for seven millions; 7.5 or 8", F["mt_seven"], [7, 7.5, 8])
    nm = n_max(F)
    pct("n_max (% a year)", 100 * nm, 2.77, 2)
    pct("    threshold, alpha 0.25 (%)", 100 * PLATEAU["alpha"] * nm, 0.69, 2)
    pct("    alpha 0.15 (%)", 100 * FAST["alpha"] * nm, 0.42, 2)
    chk("a generation (years)", GEN, 30)
    # ex:divergence-plateau
    a, b, t = PLATEAU["alpha"], PLATEAU["beta"], PLATEAU["tfp"]
    chk("(1) alpha, beta, TFP (% a year)", [a, b, 100 * t], [0.25, 1, 0.25])
    g = GEN * t
    pct("    g", g, 0.075, 3)
    z = plateau(g, a, b)
    pct("    z*", z, 0.3, 1)
    pct("    e^z*", math.exp(z), 1.35, 2)
    pct("    population a generation, g/alpha", g / a, 0.3, 1)
    pct("    a year (%)", 100 * g / a / GEN, 1, 0)
    z1 = escape(0, g, a, b, 1)[1]
    pct("(2) z1", z1, 0.075, 3)
    pct("    (%)", 100 * (math.exp(z1) - 1), 7.8)
    pct("    1 - alpha beta", 1 - a * b, 0.75, 2)
    h = half_life(a, b)
    pct("    half-life (generations)", h, 2.41, 2)
    pct("    (years)", h * GEN, 72, 0)
    a3, b3, t3 = FAST["alpha"], FAST["beta"], FAST["tfp"]
    chk("(3) alpha, beta, TFP (% a year)", [a3, b3, 100 * t3], [0.15, 1, 0.8])
    g3 = GEN * t3
    pct("    g", g3, 0.24, 2)
    z3 = plateau(g3, a3, b3)
    pct("    z*", z3, 1.6, 1)
    pct("    e^z*", math.exp(z3), 4.95, 2)
    pct("    1 - alpha beta", 1 - a3 * b3, 0.85, 2)
    h3 = half_life(a3, b3)
    pct("    half-life (generations)", h3, 4.27, 2)
    pct("    (years)", h3 * GEN, 128, 0)
    pct("    one generation: e^0.24 - 1 (%)", 100 * (math.exp(g3) - 1), 27, 0)
    z4 = escape(0, g3, a3, b3, 4)[4]
    chk("    four generations, 120 years", 4 * GEN, 120)
    chk("    z4 = z*(1 - 0.85^4)", z4, z3 * (1 - (1 - a3 * b3) ** 4))
    pct("    z4", z4, 0.765, 3)
    pct("    e^z4", math.exp(z4), 2.15, 2)
    pct("    population a generation", g3 / a3, 1.6, 1)
    pct("    a year (%)", 100 * g3 / a3 / GEN, 5.3, 1)
    pct("    floor: 0.8 - 0.15 x 2.77 (%)", 100 * (t3 - a3 * nm), 0.38, 2)
    chk("fig:div_model: ten generations; beta halved", [GENS, SLOW_POP], [10, 0.5])


def takeoff(F, Y, B, C, G):
    for c, a, b, v in [("GBR", 1700, 1820, 0.26), ("GBR", 1820, 1870, 1.13), ("GBR", 1870, 1913, 0.80),
                       ("NLD", 1700, 1820, -0.10), ("CHN", 1700, 1820, -0.47), ("JPN", 1700, 1820, 0.17),
                       ("USA", 1820, 1870, 1.17), ("USA", 1870, 1913, 1.73), ("JPN", 1870, 1913, 1.00)]:
        pct(f"MPD {c} {a}-{b} (% a year)", growth(G[c], a, b), v, 2)
    pct("    doubling at Britain's 1700-1820 rate (years)", doubling(G.GBR, 1700, 1820), 264, 0)
    t1 = {}
    for k in F:
        if k.startswith("bg_t1_"):
            v = F[k]
            t1[v[0]], t1[v[3]] = v[2], v[5]
    chk("Table 1: 1697-99 and 1770-79", F["bg_t1_1697"][:2] + F["bg_t1_1697"][3:5], [1697, 99, 1770, 79])
    chk("    1700-09", F["bg_t1_1700"][:2], [1700, 9])
    chk("    raw cotton (万磅)", [100 * t1[k] for k in (1697, 1700, 1770, 1780, 1790, 1800)],
        [110, 110, 480, 1550, 2860, 5960], tol=1e-6)
    chk("    (亿磅)", [t1[k] / 100 for k in (1820, 1840)], [1.665, 5.263])
    chk("1780-1800: output 10.8, exports 14.0", F["bg_rates"], [1780, 1800, 10.8, 14.0])
    note = column("year_note")["bg_t8_1780"]
    assert "100 lb" in note and "80s yarn" in note
    chk("Catling: India, 50,000 hours, around 1780", F["bg_t8_india"], [50000, 1780])
    chk("    Crompton's mule 1780: 2,000; Roberts 1825: 135", F["bg_t8_1780"] + F["bg_t8_1825"], [1780, 2000, 1825, 135])
    Q = quotes()
    assert "Crompton" in Q["bg_t8_1780"] and "Roberts" in Q["bg_t8_1825"]
    chk("grades: A < 5; B 5-15; C 15-25, D > 25", F["bgl_gradeA"] + F["bgl_gradeB"] + F["bgl_gradeC"],
        [5, 5, 15, 15, 25, 25])
    assert column("year_note")["bgl_t3"] == column("year_note")["bgl_t3n"] == "Table 3, Northern Song, Ming, Qing"
    assert Q["bgl_t3"].split()[-3:] == ["B", "B", "A"] and Q["bgl_t3n"].split()[-3:] == ["C", "C", "B"]
    p = F["bgl_perkins"]
    chk("Perkins (1969): 10% in 1393 to 6%", [p[0], p[2], p[3], p[4]], [1969, 10, 1393, 6])
    assert Q["bgl_perkins"].endswith("in the mid-nineteenth")          # 'century' follows on p. 11
    chk("    80% confidence interval", F["bgl_perkins80"], [1969, 216, 80])
    bd, cd = boe_decades(B), C.real_nni_pc_1860s_100
    chk("Broadberry et al.: 1860s = 100", bd[1860], 100)
    pct("Clark's index in the 1860s", cd[1860], 100.3, 1)
    for d, vb, vc in [(1270, 23.0, 44.8), (1450, 31.9, 91.1), (1640, 30.8, 52.5), (1700, 50.0, 59.0),
                      (1800, 66.3, 69.6), (1850, 90.4, 94.9)]:
        pct(f"{d}s: Broadberry et al.", bd[d], vb)
        pct("    Clark", cd[d], vc)


def welfare_check(F, Y, W):
    chk("Lal: as late as 1750", F["lal_1750"], [1750])
    chk("Allen et al.: x3, +5% rent, 250 days, 1 = subsistence",
        F["al11_three"] + F["al11_rent"] + F["al11_250"] + F["al11_one"], [3, 5, 250, 1])
    t = dict(london=3.96, amsterdam=4.18, milan=1.34, beijing=1.35, canton=1.23, suzhou_shanghai=1.16,
             kyoto_tokyo=0.81, bengal=0.88)
    assert set(t) == {c for c, _, _ in CITIES}
    for c, v in t.items():
        pct(f"1750s: {c}", decade_mean(W[c], 1750, 1759), v, 2)
    for c, a, b, v in [("beijing", 1840, 1849, 0.76), ("beijing", 1850, 1859, 0.56), ("beijing", 1900, 1913, 1.49),
                       ("london", 1850, 1859, 4.53), ("london", 1900, 1913, 7.77), ("amsterdam", 1850, 1859, 2.31)]:
        pct(f"{c} {a}-{b}", decade_mean(W[c], a, b), v, 2)
    chk("1913", F["al11_1913"], [1913])
    # ex:divergence-welfare
    w, fam = F["al11_p12"][0], F["al11_2259"][2]
    chk("(1) 12 taels; prices of 1745-54; 22.59", [w] + F["al11_2259"][:3], [12, 1745, 54, 22.59])
    pct("    12/22.59", w / fam, 0.53, 2)
    chk("    printed: 53%, 0.53", F["al11_2259"][3:], [53, 0.53])
    pct("    (%)", 100 * w / fam, 53, 0)
    chk("(2) 200 days, 14.61 taels", F["al11_woman"], [200, 14.61])
    pct("    together", w + F["al11_woman"][1], 26.61, 2)
    pct("    ratio", (w + F["al11_woman"][1]) / fam, 1.18, 2)
    chk("    printed", F["al11_both"], [26.61, 1.18])
    pct("(3) one adult's basket", fam / (F["al11_three"][0] * (1 + F["al11_rent"][0] / 100)), 7.17, 2)
    pct("(4) 4 / 1.18", F["al11_four"][0] / F["al11_both"][1], 3.4, 1)


def output_check(F, Y):
    chk("BGL: behind Italy by 1300; by 1750", F["bgl_song"] + F["bgl_1750"], [1300, 1750])
    chk("    980-1850", [F["bgl_70"][1], F["bgl_t6_1850"][0]], [980, 1850])
    for yr, v in {1090: 116.4, 1400: 94.7, 1500: 77.0, 1600: 77.0, 1700: 70.6, 1750: 42.5, 1800: 29.5, 1840: 23.8,
                  1850: 20.0}.items():
        r = F[f"bgl_t6_{yr}"]
        chk(f"Table 6 {yr}: China/GB (%)", r[3], v)
        pct("    recomputed", 100 * r[1] / r[2], v, 1)
    chk("70% of the 980 level by 1840", F["bgl_70"], [70, 980, 1840])
    pct("    Table 6: 1840 / 1090 (%)", 100 * F["bgl_t6_1840"][1] / F["bgl_t6_1090"][1], 68.2)
    assert column("year_note")["bgl_t8_1600"] == "Table 8: GB, NL, Italy, Japan, China, India"
    chk("Table 8: 1600-1850", [F["bgl_t8_1600"][0], F["bgl_t8_1850"][0]], [1600, 1850])
    for yr in (1600, 1700, 1750, 1800, 1850):
        r = F[f"bgl_t8_{yr}"]
        assert len(r) == 7
        chk(f"    {yr}: GB and China as in Table 6", [r[1], r[5]], [F[f"bgl_t6_{yr}"][2], F[f"bgl_t6_{yr}"][1]])
    assert "Li and van Zanden (2012)" in column("year_note")["bgl_lz"]
    chk("Li and van Zanden: 53.8% in the 1820s", F["bgl_lz"], [53.8, 1820])
    chk("Lower Yangzi: $1,050 (1990 dollars) in 1820, 75% above China", F["bgl_1050"] + [Y["bgl_1050"]],
        [1050, 1990, 75, 1820])
    chk("93% in 1700", F["bgl_93"], [93, 1700])
    chk("Dutch lead 42% in 1750, 90% by 1770", F["bgl_dutch"], [1750, 42, 90, 1770])
    chk("Pomeranz (2011)", F["bgl_consensus"], [2011])
    chk("$600 in 1850; 472; 400", F["bgl_472"], [600, 1850, 472, 400])
    chk("    600 = Table 6", F["bgl_t6_1850"][1], 600)
    pa, pb = check_ch18.qing()
    pct("Chapter 18: 1764-1795 (% a year)", 100 * check_ch18.growth_rate(pa, pb, 1795 - 1764), 1.19, 2)
    chk("Perkins (1969: 193)", F["bgl_accurate"], [1969, 193])
    chk("Qing: 0.70% a year", F["bgl_qing"], [0.70])
    chk("case: 1.18 against four; 93, 42 (1750), 90 (1770)",
        [F["al11_both"][1], F["al11_four"][0], F["bgl_93"][0]] + F["bgl_dutch"], [1.18, 4, 93, 1750, 42, 90, 1770])


def why(F, Y, W):
    chk("Leunig quotes Allen (2009), p. 2; Allen's reply 2018", [F["lg_wages"][0], Y["al18_trigger"]], [2, 2018])
    chk("chapter 2: eighteenth century", F["lg_ch2"], [2, 18])
    N = column("year_note")
    assert N["lg_city"].endswith("chapter 3") and N["lg_mokyr"].endswith("chapter 10")
    assert N["bg_search"] == "by the mid-eighteenth century" and Y["bg_search"] == 1750
    chk("20% as early as 1600; 1701", F["bg_silver20"] + F["bg_shilling"], [20, 1600, 1701])
    Q = {k: " ".join(v.split()) for k, v in quotes().items()}
    assert "a shilling in England may be had for two pence in India" in Q["bg_shilling"]
    chk("    silver wages 20%", F["bg_grain"], [20])
    chk("Muldrew: by 1750, over a million", F["hs_million"], [1750])
    assert "over a million women and children" in Q["hs_million"]
    chk("0.3% a year", F["hs_03"], [0.3])
    assert "spinning innovations of the 1760s and 1770s" in Q["hs_nojump"]
    assert "three spinning inventions of the late eighteenth century" in Q["hs_gun"]
    ap = {k: F[f"hs_ap_{k}"] for k in (1750, 1760, 1770)}
    chk("Appendix I: decades", [x for v in ap.values() for x in v[:2]], [1750, 59, 1760, 69, 1770, 79])
    for k, n, wage, basket, wr, casual, r in [(1750, 703, 3.68, 3.07, 1.20, 6.31, 0.58),
                                               (1760, 26, 3.19, 3.31, 0.97, 6.54, 0.49),
                                               (1770, 60, 4.47, 3.74, 1.20, 6.19, 0.72)]:
        chk(f"{k}s: n, wage, basket, welfare ratio, casual wage, ratio", ap[k][2:], [n, wage, basket, wr, casual, r])
        pct("    ratio to the casual wage", wage / casual, r, 2)
        if k != 1760:
            pct("    welfare ratio", wage / basket, wr, 2)
    pct("1760s: 3.19/3.31 (printed 0.97)", ap[1760][3] / ap[1760][4], 0.96, 2)
    chk("Allen: 40% of full time", F["al18_40"], [40])
    assert Q["al18_40"].count("40%") == 2
    assert "Guest (1823)" in N["al18_guest"]
    chk("Guest: 1760", F["al18_guest"], [1760])
    chk("9d and 9d", F["al18_9d"], [9, 9])
    chk("1.09 days for one pound; 2.18", F["al18_109"], [1.09, 1, 2.18])
    assert "1750s and 1760s" in Q["al18_8275"]
    chk("servants: 8.275d", F["al18_8275"][-1], 8.275)
    chk("Humphries and Schneider 2019: more than 1500", F["hs19_1500"], [1500])
    # ex:divergence-spinners
    s9, c9 = F["al18_9d"]
    day1, _, day2 = F["al18_109"]
    pct("(1) 9 / 1.09 (d)", s9 / day1, 8.26, 2)
    chk("    18", s9 + c9, 18)
    pct("    18 / 2.18 (d)", (s9 + c9) / day2, 8.26, 2)
    pct("(2) 3.68 / 8.26", ap[1750][3] / (s9 / day1), 0.45, 2)
    pct("    0.4 x 8.26 (d)", F["al18_40"][0] / 100 * s9 / day1, 3.30, 2)
    # Pomeranz and Lal
    assert "eighteenth-century core in southern China" in Q["lal_coal"]
    assert "in the eleventh century" in Q["lal_hartwell"] and "invaders of the twelfth century" in Q["lal_hartwell"]
    assert "by the eleventh century" in Q["lal_song"]
    assert "Liu (1993)" in N["bgl_liu"]
    chk("Hartwell: 150,000 tons in 1078; Liu: 13,500", F["bgl_liu"], [1078, 13500, 150000])
    chk("    Hartwell's claim", [F["bgl_hartwell"][-2], F["bgl_hartwell"][-1]], [150000, 1078])
    chk("    (万吨)", [F["bgl_liu"][2] / WAN, F["bgl_liu"][1] / WAN], [15, 1.35])
    chk("AJR: 1500-1850; after 1500", F["ajr_atlantic"] + F["ajr_bourgeois"], [1500, 1850, 1500])
    # table and compare box
    chk("tab: 1770, wages 6 times", F["bg_1770"], [1770, 6])
    pct("    London / Beijing, 1750s", decade_mean(W.london, 1750, 1759) / decade_mean(W.beijing, 1750, 1759), 3, 0)


def india(F, Y):
    chk("Calico laws 1701, 1721, 1774", F["bg_1701"] + F["bg_1721"] + F["bg_1774"], [1701, 1701, 1721, 1774])
    Q = quotes()

    def pence(s: str) -> int:
        m = re.fullmatch(r"(\d+)s/(\d+)d", s)
        return 12 * int(m[1]) + int(m[2])

    for k, lan, ind, p in [(1680, (6, 0), (1, 6), 400), (1770, (9, 0), (1, 6), 600), (1790, (13, 3), (2, 0), 663),
                           (1820, (10, 4), (2, 0), 517)]:
        c, a, b, q = Q[f"bg_t7_{k}"].split()
        assert c == f"c.{k}"
        chk(f"Table 7 c.{k}: Lancashire, India (d), printed %", [pence(a), pence(b), int(q)],
            [12 * lan[0] + lan[1], 12 * ind[0] + ind[1], p])
        pct("    recomputed", 100 * pence(a) / pence(b), p, 0)
    t70, t20 = F["bg_t10_1770"], F["bg_t10_1820"]
    chk("Table 10, 1770: 600, 250, 240", t70, [1770, 600, 250, 240])
    chk("    1820: 517, 1625, 32", t20, [1820, 517, 1625, 32])
    assert "between two and three times higher" in " ".join(Q["bg_1770"].split())
    chk("Cuenca Esteban: 1770/4-1820/4, 6.53", F["bg_653"][4:], [1770, 4, 1820, 4, 6.53])
    chk("by 1820: 6.53, 1625%; 517%", F["bg_1625"] + F["bg_517"], [1820, 6.53, 1625, 517])
    pct("    517/1625 (%)", 100 * 517 / 1625, 32, 0)
    e90, e30 = F["bg_t6_1790"], F["bg_t6_1830"]
    chk("Table 6: 1790-99, 1830-39", e90[:2] + e30[:2], [1790, 99, 1830, 39])
    chk("    Bengal to Britain (万匹; 匹)", [e90[2] * 1e3 / WAN, e30[2] * 1e3], [78.7, 6000], tol=1e-9)
    chk("    all India to Britain (万匹)", [e90[3] * 1e3 / WAN, e30[3] * 1e3 / WAN], [220, 27.1], tol=1e-9)
    chk("Dacca 1818", F["bg_dacca"], [1818, 1818])
    assert column("year_note")["bg_dacca"].startswith("Mitra")
    chk("transport costs: to the 1860s", F["bg_transport"], [1860])
    for k, a, b, v, s in [("bg_t4_1831", 1831, 35, 3.75, 3.9), ("bg_t4_1856", 1856, 60, 4.55, 35.3),
                          ("bg_t4_1880", 1880, 81, 6.00, 58.4)]:
        r = F[k]
        chk(f"Table 4 {a}-{b}: consumption (亿磅), British share (%)", [r[0], r[1], r[2] / 100, r[3]], [a, b, v, s])
    chk("Twomey: about 1830; after 1850", F["bg_twomey2"], [1830, 1850])
    # ex:divergence-ulc
    pct("(1) 1770: 600/250 (%)", 100 * t70[1] / t70[2], 240, 0)
    pct("    1820: 517/1625 (%)", 100 * t20[1] / t20[2], 31.8, 1)
    pct("(2) 250 x 6.53 (%)", t70[2] * F["bg_653"][-1], 1632.5, 1)
    chk("    1625 = 250 x 6.5", t70[2] * 6.5, t20[2])
    th = F["bg_t13_head"]
    chk("Table 13: exponents 0.5 and 0.5", th, [0.5, 0.5])
    th = th[0]
    t13 = {k: F[f"bg_t13_{k}"] for k in (1680, 1770, 1790, 1820)}
    for k, v in t13.items():
        _, w, c, comb, fob, a = v
        pct(f"Table 13 c.{k}: combined cost", w ** th * c ** (1 - th), comb, 0)
        pct("    TFP (from the unrounded cost)", 100 * w ** th * c ** (1 - th) / fob, a, 0)
    chk("(3) raw cotton 320, 127; FOB 200, 43", [t13[1770][2], t13[1820][2], t13[1770][4], t13[1820][4]],
        [320, 127, 200, 43])
    pct("    1770: sqrt(600 x 320)", math.sqrt(600 * 320), 438, 0)
    pct("    438/200", t13[1770][3] / t13[1770][4], 2.19, 2)
    pct("    1820: sqrt(517 x 127)", math.sqrt(517 * 127), 256.2, 1)
    pct("    256.2/43", math.sqrt(517 * 127) / 43, 5.96, 2)
    chk("(4) c.1680: 400, 182, 200", [t13[1680][1], t13[1680][2], t13[1680][4]], [400, 182, 200])
    pct("    sqrt(400 x 182)", math.sqrt(400 * 182), 270, 0)
    pct("    270/200", t13[1680][3] / t13[1680][4], 1.35, 2)
    pct("    ln(596/135)/140 (%)", 100 * math.log(t13[1820][5] / t13[1680][5]) / (1820 - 1680), 1.06, 2)
    pct("    ln(219/135)/90 (%)", 100 * math.log(t13[1770][5] / t13[1680][5]) / (1770 - 1680), 0.54, 2)
    chk("footnote 8: 1.28, 1680-1770, 1.06, Table 13", F["bg_fn8"], [1.28, 1680, 1770, 1.06, 13])
    assert column("juan")["bg_fn8"].endswith("note 8")


def test(F, B, C, W):
    a = C.alpha.loc[1250:1630]
    chk("decades 1250-1630", len(a), 39)
    pct("land share: mean", a.mean(), 0.235, 3)
    pct("    min", a.min(), 0.163, 3)
    pct("    max", a.max(), 0.314, 3)
    f = frontier(C, 1250, 1630)
    lo, hi = f.conf_int().loc["lL"]
    chk("frontier 1250-1630: n", f.nobs, 39)
    pct("    slope", f.params.lL, -0.72, 2)
    pct("    95% CI (HAC, 3 lags)", lo, -0.83, 2)
    pct("    ", hi, -0.60, 2)
    pct("    R2", f.rsquared, 0.88, 2)
    pct("    farm wage", frontier(C, 1250, 1630, "real_farm_1860s_100").params.lL, -1.17, 2)
    pct("    slope / land share", -f.params.lL / a.mean(), 3, 0)
    pct("    corr(alpha, ln L)", np.corrcoef(a, np.log(C.pop_england_m.loc[1250:1630]))[0, 1], 0.53, 2)
    fb = boe_frontier(B, 1270, 1630)
    lo, hi = fb.conf_int().loc["lL"]
    pct("Broadberry et al. 1270-1630: slope", fb.params.lL, -0.28, 2)
    pct("    95% CI", lo, -0.50, 2)
    pct("    ", hi, -0.05, 2)
    pct("    R2", fb.rsquared, 0.36, 2)
    pct("1640-1790: slope", frontier(C, 1640, 1790).params.lL, 0.45, 2)
    f2 = frontier(C, 1800, 1860)
    pct("1800-1860: slope", f2.params.lL, 0.46, 2)
    pct("    R2", f2.rsquared, 0.995, 3)
    r = {k: tfp(C, *k) for k in [(1250, 1640), (1640, 1800), (1800, 1860)]}
    for k, (t, y, L) in {(1250, 1640): (-0.04, -0.06, 0.09), (1640, 1800): (0.25, 0.18, 0.32),
                         (1800, 1860): (0.80, 0.61, 1.29)}.items():
        pct(f"{k[0]}-{k[1]}: TFP (% a year)", r[k]["tfp"], t, 2)
        pct("    income per head", r[k]["y"], y, 2)
        pct("    population", r[k]["L"], L, 2)
    for d, v in {1250: 0.284, 1600: 0.314, 1700: 0.252, 1800: 0.211, 1850: 0.109, 1860: 0.095}.items():
        pct(f"land share {d}s", C.alpha[d], v, 3)
    nm = n_max(F)
    pct("1640-1800: alpha about 0.25", r[(1640, 1800)]["alpha"], 0.25, 2)
    pct("    threshold (%)", 100 * 0.25 * nm, 0.69, 2)
    pct("1800-1860: mean alpha", r[(1800, 1860)]["alpha"], 0.149, 3)
    pct("    threshold (%)", 100 * r[(1800, 1860)]["alpha"] * nm, 0.41, 2)
    # the compare box
    chk("compare box", [round(a.mean(), 3), round(C.alpha[1860], 3), round(r[(1250, 1640)]["tfp"], 2),
                        round(r[(1800, 1860)]["tfp"], 2), round(f.params.lL, 2), round(f2.params.lL, 2)],
        [0.235, 0.095, -0.04, 0.80, -0.72, 0.46])
    # ex:divergence-tfp
    y1, L1 = round(r[(1640, 1800)]["y"], 3), round(r[(1640, 1800)]["L"], 3)
    chk("(1) inputs", [y1, L1], [0.177, 0.323])
    t1 = y1 + 0.25 * L1
    pct("    0.177 + 0.25 x 0.323", t1, 0.258, 3)
    pct("    share (%)", 100 * y1 / t1, 69, 0)
    pct("    decade by decade", r[(1640, 1800)]["tfp"], 0.253, 3)
    y2, L2 = round(r[(1800, 1860)]["y"], 3), round(r[(1800, 1860)]["L"], 3)
    chk("(2) inputs", [y2, L2], [0.609, 1.290])
    pct("    alpha about 0.15", r[(1800, 1860)]["alpha"], 0.15, 2)
    t2 = y2 + 0.15 * L2
    pct("    0.609 + 0.15 x 1.290", t2, 0.803, 3)
    pct("    share (%)", 100 * y2 / t2, 76, 0)
    gL = C.pop_england_m[1800] / C.pop_england_m[1700]
    pct("(3) population 1700-1800", gL, 1.651, 3)
    pct("    1.651^-0.25", gL ** -0.25, 0.882, 3)
    pct("    (%)", 100 * (1 - gL ** -0.25), 11.8)
    for col, a0, a1, ch in [("real_nni_pc_1860s_100", 58.97, 69.63, 18.1), ("real_farm_1860s_100", 70.09, 67.34, -3.9),
                            ("real_blab_1860s_100", 58.17, 56.87, None), ("real_bcraft_1860s_100", 60.83, 55.90, None)]:
        pct(f"    {col} 1700", C[col][1700], a0, 2)
        pct("    1800", C[col][1800], a1, 2)
        if ch is not None:
            pct("    change (%)", 100 * (C[col][1800] / C[col][1700] - 1), ch)
        assert (C[col][1800] > C[col][1700]) == (col == "real_nni_pc_1860s_100")
    for col, v in [("real_farm_1860s_100", 45.9), ("real_blab_1860s_100", 62.2), ("real_bcraft_1860s_100", 63.2)]:
        pct(f"    1800-1850 {col} (%)", 100 * (C[col][1850] / C[col][1800] - 1), v)
    # the pitfalls
    m = {c: decade_mean(W[c], 1750, 1759) for c in ("london", "amsterdam", "beijing", "suzhou_shanghai", "canton",
                                                     "milan", "leipzig")}
    ratios = [m[a] / m[b] for a in ("london", "amsterdam") for b in ("beijing", "suzhou_shanghai", "canton")]
    pct("1750s: London and Amsterdam against the Chinese cities, from", min(ratios), 2.9, 1)
    pct("    to", max(ratios), 3.6, 1)
    pct("    Milan", m["milan"], 1.34, 2)
    pct("    Beijing", m["beijing"], 1.35, 2)
    pct("    Leipzig", m["leipzig"], 1.65, 2)
    assert m["leipzig"] < m["london"] / 2
    chk("    Dutch lead 1750: 42%", F["bgl_dutch"][:2], [1750, 42])


def deeper(F, Y):
    chk("pages: Allen 2, Mokyr 478, Clark 8, Pomeranz 200",
        F["lg_wages"] + F["hr_beliefs"] + F["mg_genetic"] + F["pz_seasia"], [2, 478, 8, 200])
    chk("Harley's header: 2010, 564 pp.", F["hr_header"], [2010, 564])
    assert "978-0-300-12455-2" in quotes()["hr_isbn"]
    V = {k: " ".join(v["version"].split()) for k, v in meta()["sources"].items()}
    assert "Economic History Review" in V["allen2009wp"] and "2011" in V["allen2009wp"]
    assert "Journal of Economic History" in V["bgl2017"] and "2018" in V["bgl2017"]
    assert "Economic History Review" in V["bg2005"] and "2009" in V["bg2005"]
    assert "American Economic Review 95(3), 2005" in V["ajr2002"] and "(December 2002)" in V["ajr2002"]
    assert "accepted manuscript" in V["hs2018"] and "(July 2018)" in V["allen2018"] and "(October 2019)" in V["hs2019"]
    chk("Table 10: 1625 = 250 x 6.5", F["bg_t10_1770"][2] * 6.5, F["bg_t10_1820"][2])
    chk("footnote 8 prints 1680-1770", F["bg_fn8"][1:3], [1680, 1770])
    chk("initial FOB ratio 200", F["bg_fob200"], [13, 200])
    ap = F["hs_ap_1760"]
    chk("1760s: printed 0.97; 26 observations", [ap[5], ap[2]], [0.97, 26])
    pct("    3.19/3.31", ap[3] / ap[4], 0.96, 2)
    chk("1990 and 2011 dollars", F["bgl_1050"][1], 1990)
    assert "2011 international dollars" in load_snapshot("maddison2023_divergence")[1]["series"]
    chk("Li and van Zanden (2012); Perkins (1969)", [F["bgl_accurate"][0]], [1969])


def takeaways_and_selfcheck(F, Y, B, C, G, W):
    chk("Malthus 1798", Y["mt_ratio"], 1798)
    pct("Britain 1700-1820, 1820-1870 (% a year)", growth(G.GBR, 1700, 1820), 0.26, 2)
    pct("    ", growth(G.GBR, 1820, 1870), 1.13, 2)
    t1 = {F[k][3]: F[k][5] for k in F if k.startswith("bg_t1_")} | {F[k][0]: F[k][2] for k in F if k.startswith("bg_t1_")}
    chk("raw cotton: 1700s 110 万磅, 1840s 5.263 亿磅", [100 * t1[1700], t1[1840] / 100], [110, 5.263], tol=1e-9)
    pct("London / Beijing, 1750s: three times",
        decade_mean(W.london, 1750, 1759) / decade_mean(W.beijing, 1750, 1759), 3, 0)
    chk("93% (1700), 42% (1750), 90% (1770)", [F["bgl_93"][0]] + F["bgl_dutch"][1:3], [93, 42, 90])
    chk("India: 6 times, 240%; 1625%, 32%", [F["bg_1770"][1], F["bg_t10_1770"][3], F["bg_t10_1820"][2],
                                             F["bg_t10_1820"][3]], [6, 240, 1625, 32])
    chk("    Bengal: 78.7 万匹 to 6,000", [F["bg_t6_1790"][2] / 10, F["bg_t6_1830"][2] * 1e3], [78.7, 6000], tol=1e-9)
    pct("land share 1250s", C.alpha[1250], 0.28, 2)
    # self-check answers
    p, d, food = SC1["pop"], SC1["double"], SC1["food"]
    k = SC1["years"] / d
    chk("1. population (万)", 100 * p * 2 ** k, 16000)
    chk("    food (万)", 100 * (p + k * food), 5000)
    chk("    gap (万)", 100 * (p * 2 ** k - p - k * food), 11000)
    a, b, t = SC2["alpha"], SC2["beta"], SC2["tfp"]
    g = GEN * t
    pct("2. g", g, 0.12, 2)
    z = plateau(g, a, b)
    pct("    z*", z, 1.2, 1)
    pct("    e^1.2", math.exp(z), 3.32, 2)
    pct("    population a generation, beta z*", b * z, 0.6, 1)
    pct("    a year (%)", 100 * b * z / GEN, 2, 0)
    pct("    1 - alpha beta", 1 - a * b, 0.9, 1)
    pct("    half-life", half_life(a, b), 6.58, 2)
    fam = SC3["basket"] * SC3["adults"] * (1 + SC3["rent"])
    pct("3. family budget", fam, 25.2, 1)
    pct("    welfare ratio", SC3["wage"] / fam, 1.19, 2)
    pct("4. ULC (%)", 100 * SC4["w"] / SC4["y"], 200, 0)
    chk("    break-even productivity (%)", SC4["w2"], 400)
    pct("    at 500%", 100 * SC4["w2"] / SC4["y2"], 80, 0)
    t5 = SC5["dly"] + SC5["alpha"] * SC5["dlL"]
    pct("5. TFP (% a year)", t5, 0.42, 2)
    pct("    share (%)", 100 * SC5["dly"] / t5, 71.4, 1)
    pct("6. 1.5^-0.3", SC6["pop"] ** -SC6["alpha"], 0.885, 3)
    pct("    fall (%)", 100 * (1 - SC6["pop"] ** -SC6["alpha"]), 11.5, 1)
    pct("    TFP (%)", 100 * (SC6["pop"] ** SC6["alpha"] - 1), 12.9, 1)


def main():
    df = _rows()
    F, Y = facts(), years()
    B, C, W = boe(), clark(), welfare()
    G, _ = maddison()
    check_readings(df)
    check_text(df)
    opening(F, Y, B, G)
    world(F, Y, B, G)
    malthus_model(F)
    takeoff(F, Y, B, C, G)
    welfare_check(F, Y, W)
    output_check(F, Y)
    why(F, Y, W)
    india(F, Y)
    test(F, B, C, W)
    deeper(F, Y)
    takeaways_and_selfcheck(F, Y, B, C, G, W)
    print("all Chapter 21 checks passed")


if __name__ == "__main__":
    main()
