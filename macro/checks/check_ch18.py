"""Chapter 18 (亚当·斯密：分工、积累与真实票据): every number and every quotation in zh/ch18_smith.tex.

    python3 checks/check_ch18.py

Inputs:
  smith_facts                  quotations of Smith (1776; the Gutenberg text and the first edition), Rockoff (2009),
                               Thornton (1802), Hunter (1868, with the letter of 3 November 1772), the Census Bureau's
                               series Z 1 (read on the page image) and the 清史稿 (checked by
                               data/fetch/verify_web_quotes.py and data/fetch/verify_quotes.py)
  boe_millennium_gb_1660_1780  Bank of England, A Millennium of Macroeconomic Data: population of England and Great
                               Britain, real GDP per head, nominal GDP and the national debt, 1660-1780
The figure module figsrc/fig_ch18.py imports the functions defined here.

What is checked here:
  1. readings   every number of the value column of smith_facts is read from its quotation: digits, English
                number words, fractions, shillings and pence, and pounds-shillings-pence
  2. the text   every “…” in the chapter is part of a 清史稿 quotation (quoted untranslated) after punctuation is
                removed, or is the chapter's Chinese rendering of a quotation (TRANSLATIONS: rendering -> row or
                rows), or a term of the text (ALLOW)
  3. numbers    every number of the text, section by section, with quoted()

Models (the chapter's key equations):
    two factors          Y/N = (Y/L)(L/N)                                     (eq:smith-twofactors)
    paper money          dY/Y = (M/Y)(1 - rho) r                              (eq:smith-saving)
    over-issue           R = rho Nbar + (N - Nbar),  N > Nbar                 (eq:smith-reflux)
    drawing, redrawing   c = i + n k                                          (eq:smith-redraw)
Units: 1 pound = 20 shillings = 240 pence; a guinea = 21 shillings; doubling time = ln 2 / mean log growth.
"""
from __future__ import annotations

import math
import re

import pandas as pd

from common import ROOT, load_snapshot, quoted

TEX = ROOT / "zh" / "ch18_smith.tex"
SHILLINGS, PENCE = 20, 240                 # per pound

# Teaching inputs stated in the text
SHARE, SHARE2 = 0.40, 0.50                 # ex:smith-pins (2): the share of useful labour
NAILS_PER_HOUSE, VILLAGE = 50, 15          # ex:smith-market (2)
PROFIT = 0.10                              # ex:smith-saving: Rockoff's 10 per cent on the carrying trade
TARGET = 0.10                              # ex:smith-saving (2): a gain of 10 per cent of output
LONDON_COST = 0.08                         # ex:smith-ayr: the cost of the London bills (Smith: upwards of 8 per cent)
# self-check questions
SC1 = dict(N=10e6, L=4.5e6, Y=9e8, L2=5e6)
SC2 = dict(ship=8, ship2=6, tons=200)
SC3 = dict(M=6e6, Y=60e6, rho=0.25, r=0.08)
SC4 = dict(Nbar=60_000, R=12_000, N=70_000)
SC5 = dict(i=0.05, n=4, k=0.0075, profit=0.08)
SC6 = dict(loans=1e6, rate=0.05, notes=3e5, borrowed=7e5, cost=0.07)


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


def doubling(a: float, b: float, years: float) -> float:
    """Years to double at the mean log growth rate between two levels."""
    return math.log(2) / (math.log(b / a) / years)


# ---------------------------------------------------------------------------------------------------
# Loaders
def _rows() -> pd.DataFrame:
    df, meta = load_snapshot("smith_facts", dtype=str, keep_default_na=False)
    assert 18 in meta["used_in"]
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
    df, meta = load_snapshot("boe_millennium_gb_1660_1780")
    assert 18 in meta["used_in"]
    return df.set_index("year")


CENSUS_YEARS = list(range(1780, 1629, -10))     # the columns of series Z 1, as transcribed


def colonies() -> pd.DataFrame:
    """Series Z 1: total and Negro population of the American colonies, every ten years 1630-1780."""
    F = facts()
    assert len(F["cz_total"]) == len(F["cz_negro"]) == len(CENSUS_YEARS) == 16
    df = pd.DataFrame({"total": F["cz_total"], "negro": F["cz_negro"]}, index=CENSUS_YEARS).sort_index()
    df["white"] = df.total - df.negro
    return df


# ---------------------------------------------------------------------------------------------------
# Chinese numerals of the 清史稿 row
CN = {c: i for i, c in enumerate("零一二三四五六七八九")}
CN_UNIT = {"十": 10, "百": 100, "千": 1000}


def cn_small(s: str) -> int:
    """A number below 10,000 written with 千, 百, 十 (a 零 or an omitted 零 between them is allowed)."""
    total, digit = 0, 0
    for ch in s:
        if ch in CN:
            digit = CN[ch]
        else:
            total += (digit or 1) * CN_UNIT[ch]
            digit = 0
    return total + digit


def cn_number(s: str) -> int:
    """The 清史稿's 二万五百五十九万一千一十七: the last 万 multiplies everything before it, which may itself contain
    a 万 (the reading (2 x 10,000 + 559) x 10,000 + 1,017 of the snapshot's note)."""
    if "万" not in s:
        return cn_small(s)
    head, tail = s.rsplit("万", 1)
    return cn_number(head) * 10_000 + (cn_small(tail) if tail else 0)


def qing() -> tuple[int, int]:
    q = quotes()["qs_qianlong"]
    a, b = re.findall(r"([零一二三四五六七八九十百千万]+)口", q)
    pa, pb = cn_number(a), cn_number(b)
    assert [pa, pb] == facts()["qs_qianlong"], (pa, pb)
    return pa, pb


# ---------------------------------------------------------------------------------------------------
# The arithmetic of the chapter
def pins(F) -> dict:
    """ex:smith-pins."""
    ten, twelve, per_lb = F["wn_ten"][0], F["wn_twelve"][0], F["wn_4000"][0]
    day = twelve * per_lb
    each = day / ten
    return dict(day=day, each=each, x20=each / F["wn_240"][0], x1=each / F["wn_240"][1])


def carriage(F) -> dict:
    """ex:smith-market (1): 200 tons by land and by sea."""
    men, horses, tons = F["wn_waggon"][0], F["wn_waggon"][1], F["wn_waggon"][3]
    ship_lo, ship_hi, ship_tons = F["wn_ship"]
    waggons = ship_tons / tons
    return dict(waggons=waggons, men=waggons * men, horses=waggons * horses,
                x_lo=waggons * men / ship_hi, x_hi=waggons * men / ship_lo)


def saving(m_over_y: float, rho: float, r: float) -> float:
    """eq:smith-saving."""
    return m_over_y * (1 - rho) * r


def reflux(nbar: float, reserve: float, n: float) -> dict:
    """eq:smith-reflux."""
    rho = reserve / nbar
    return dict(rho=rho, naive=rho * n, needed=rho * nbar + (n - nbar))


def lsd(pounds: float, shillings: float, pence: float) -> float:
    return pounds + shillings / SHILLINGS + pence / PENCE


def redraw(i: float, n: float, k: float) -> float:
    """eq:smith-redraw."""
    return i + n * k


def ayr(F, cost=LONDON_COST) -> dict:
    """ex:smith-ayr: Smith's figures for the Ayr Bank when it stopped."""
    notes, london = F["wn_200k"][0], F["wn_600k"][0]
    loans, rate = F["wn_800k"][0], F["wn_800k"][1] / 100
    income = loans * rate
    london_cost = london * cost
    paid = F["wn_capital160"][0] * F["wn_capital160"][1] / 100
    loss = london * (cost - rate)
    gain = notes * rate
    return dict(income=income, london_cost=london_cost, share=london / loans, loss=loss, gain=gain,
                net=gain - loss, paid=paid, years=paid / (loss - gain))


def growth_rate(a: float, b: float, years: float, compound: bool = False) -> float:
    return (b / a) ** (1 / years) - 1 if compound else math.log(b / a) / years


# ---------------------------------------------------------------------------------------------------
# 1. Readings of the numbers
WORDS = {"a": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
         "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
         "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90, "fortieth": 40}
MULT = {"hundred": 100, "hundredth": 100}
SCALE = {"thousand": 1e3, "million": 1e6, "millions": 1e6}
DENOM = {"half": 2, "third": 3, "fourths": 4, "quarters": 4, "fifth": 5, "fifths": 5, "tenth": 10, "twentieth": 20,
         "thirtieth": 30}
TIMES = {"doubled": 2, "quadrupled": 4}
PENCE_WORDS = {"three-halfpence": 1.5, "three-farthings": 0.75}
LONG_S = {"thoufand": "thousand", "fix": "six", "fixty": "sixty", "fhillings": "shillings"}


def _words(s: str) -> list[str]:
    w = s.lower().replace("-", " ").split()
    return [LONG_S.get(x, x) for x in w]


def cardinal(s: str) -> float:
    """An English cardinal ('forty-eight thousand', 'eight hundred and fifty thousand', 'five-and-twenty',
    'eighteen hundred thousand', 'a hundred and forty five millions'), or the ordinal of a fraction's denominator
    ('two hundred and fortieth', 'four thousand eight hundredth'); a unit word after the number ends it."""
    total, cur, seen = 0.0, 0.0, False
    for w in _words(s):
        if w == "and" and seen:
            continue
        if w in WORDS:
            cur += WORDS[w]
        elif w in MULT:
            cur = (cur or 1) * MULT[w]
        elif w in SCALE:
            total += (cur or 1) * SCALE[w]
            cur = 0
        else:
            break
        seen = True
    assert seen, s
    return total + cur


def fraction(s: str) -> float:
    """'a fifth', 'one half', 'three fourths', 'four-fifths', 'three quarters', 'one-third'."""
    w = _words(s)
    assert w[-1] in DENOM and len(w) == 2, s
    return WORDS[w[0]] / DENOM[w[-1]]


def mixed(s: str) -> float:
    """'two and a half', 'one and a half', 'four and a-half'."""
    a, b = s.split(" and ", 1)
    return cardinal(a) + fraction(b)


def shillings(s: str) -> float:
    """Shillings and pence in words: 'three shillings and sixpence', 'two shillings and tenpence', 'sixpence'."""
    w = _words(s)
    v = 0.0
    if "shillings" in w:
        v += cardinal(" ".join(w[:w.index("shillings")]))
        w = w[w.index("shillings") + 1:]
    if w and w[0] == "and":
        w = w[1:]
    if w:
        assert len(w) == 1 and w[0].endswith("pence"), s
        v += WORDS[w[0][:-5]] / 12
    return v


def pounds(s: str) -> float:
    """Pounds, shillings and pence in figures: '£411,117: 10: 9', '£3:17:10 ½'."""
    s = s.replace("£", "").replace("½", ".5").replace(" .5", ".5")
    p, sh, d = [float(x.replace(",", "").strip()) for x in s.split(":")]
    return lsd(p, sh, d)


def digits(s: str) -> float:
    return float(s.replace(",", ""))


def read(phrase: str, how: str) -> list[float]:
    if how == "num":
        return [digits(phrase)]
    if how == "en":
        return [cardinal(phrase)]
    if how == "frac":
        return [fraction(phrase)]
    if how == "mixed":
        return [mixed(phrase)]
    if how == "sd":
        return [shillings(phrase)]
    if how == "lsd":
        return [pounds(phrase)]
    if how == "or":                               # 'three or four hundred thousand': the scale of the second
        a, b = phrase.split(" or ")
        hi = cardinal(b)
        return [cardinal(a) * hi / cardinal(b.split()[0]), hi]
    if how == "half":                             # 'half a million'
        return [cardinal(phrase.split(" ", 1)[1]) / 2]
    if how == "in":                               # 'one in a thousand'
        a, b = phrase.split(" in ")
        return [cardinal(a) / cardinal(b)]
    if how == "times":
        return [TIMES[phrase]]
    if how == "pence":
        return [PENCE_WORDS[phrase]]
    raise ValueError(how)


# id -> [(phrase in the quotation, how it is read)], in order. Rows not listed are read with all the digits of
# the quotation.
EN = "en"
READINGS = {
    "wn_two": [("two", EN)],
    "wn_pinone": [("one pin", EN), ("twenty", EN)],
    "wn_eighteen": [("eighteen", EN)],
    "wn_ten": [("ten men", EN)],
    "wn_twelve": [("twelve pounds", EN)],
    "wn_4000": [("four thousand", EN)],
    "wn_48000": [("ten persons", EN), ("forty-eight thousand", EN)],
    "wn_4800": [("four thousand eight hundred", EN)],
    "wn_240": [("twenty", EN), ("one pin", EN), ("two hundred and fortieth", EN), ("four thousand eight hundredth", EN)],
    "wn_three": [("three", EN)],
    "wn_nails": [("a thousand", EN), ("three hundred working", EN), ("three hundred thousand", EN)],
    "wn_nails2": [("one thousand", EN)],
    "wn_waggon": [("two men", EN), ("eight horses", EN), ("six weeks", EN), ("four ton", EN)],
    "wn_ship": [("six", EN), ("eight men", EN), ("two hundred ton", EN)],
    "wn_fifty": [("fifty", EN), ("a hundred", EN), ("four hundred", EN)],
    "wn_ny_lab": [("1773", "num"), ("three shillings and sixpence", "sd"), ("two shillings", "sd")],
    "wn_ny_ship": [("ten shillings and sixpence", "sd"), ("sixpence", "sd"), ("six shillings and sixpence", "sd")],
    "wn_ny_house": [("eight shillings", "sd"), ("four shillings and sixpence", "sd")],
    "wn_ny_tailor": [("five shillings", "sd"), ("two shillings and tenpence", "sd")],
    "wn_double": [("five hundred", EN), ("twenty", EN), ("five-and-twenty", EN)],
    "wn_china_stat": [("five hundred", EN)],
    "wn_bengal_die": [("three or four hundred thousand", "or")],
    "wn_china12": [("Twelve", EN)],
    "wn_bengal60": [("forty", EN), ("fifty", EN), ("sixty", EN)],
    "wn_100k": [("a hundred thousand", EN), ("twenty thousand", EN)],
    "wn_80k": [("Eighty thousand", EN)],
    "wn_fifth": [("a fifth", "frac")],
    "wn_million": [("one million", EN), ("one million", EN), ("two hundred thousand", EN),
                   ("eight hundred thousand", EN), ("a million", EN), ("eighteen hundred thousand", EN)],
    "wn_overflow": [("Eight hundred thousand", EN)],
    "wn_ratios": [("a fifth", "frac"), ("a tenth", "frac"), ("a twentieth", "frac"), ("a thirtieth", "frac")],
    "wn_fourfifths": [("a fifth", "frac"), ("four-fifths", "frac")],
    "wn_glasgow": [("fifteen", EN), ("quadrupled", "times")],
    "wn_1707": [("1707", "num"), ("£411,117: 10: 9", "lsd")],
    "wn_metal_m": [("a million", EN)],
    "wn_twomillion": [("two millions", EN), ("half a million", "half")],
    "wn_cash": [("two or three thousand", "or"), ("two persons", EN)],
    "wn_40k": [("forty thousand", EN), ("ten thousand", EN)],
    "wn_44k": [("forty-four thousand", EN), ("four thousand", EN)],
    "wn_14k": [("eleven thousand", EN), ("fourteen thousand", EN)],
    "wn_gainnothing": [("four thousand", EN), ("four thousand", EN)],
    "wn_boe_coin": [("eight hundred thousand", EN), ("a million", EN), ("eight hundred and fifty thousand", EN)],
    "wn_boe_loss": [("four pounds", EN), ("£3:17:10 ½", "lsd"), ("two and a half", "mixed"), ("three per", EN)],
    "wn_agents": [("one and a half", "mixed"), ("two per", EN), ("three quarters", "frac"), ("fifteen", EN)],
    "wn_months": [("four", EN), ("five", EN), ("six", EN), ("eight", EN)],
    "wn_books": [("five hundred", EN)],
    "wn_25years": [("five and twenty", EN)],
    "wn_AB": [("two months", EN)],
    "wn_8pct": [("five per", EN), ("one half", "frac"), ("six times", EN), ("eight per", EN)],
    "wn_profits": [("six", EN), ("ten", EN)],
    "wn_exch3": [("three per", EN)],
    "wn_14pct": [("four times", EN), ("one half", "frac"), ("fourteen", EN)],
    "wn_capital160": [("one hundred and sixty thousand", EN), ("eighty", EN)],
    "wn_twoyears": [("two years", EN)],
    "wn_200k": [("two hundred thousand", EN)],
    "wn_600k": [("six hundred thousand", EN)],
    "wn_800k": [("eight hundred thousand", EN), ("five per", EN)],
    "wn_loss3": [("eight per", EN), ("three per", EN), ("three fourths", "frac")],
    "wn_longer": [("two years", EN)],
    "wn_sooner": [("two years", EN)],
    "wn_optional": [("six months", EN), ("six months", EN)],
    "wn_bankrupt": [("one in a thousand", "in")],
    "wn_legal5": [("three per", EN), ("four and", EN), ("four and a-half", "mixed"), ("five per", EN)],
    "wn_prodigals": [("eight", EN), ("ten per", EN)],
    "e1_pins": [("forty-eight thoufand", EN)],
    "e1_bengal": [("three or four hundred thoufand", "or")],
    "e1_ny": [("three fhillings and Sixpence", "sd")],
    "e1_bengal60": [("fixty", EN)],
    "e1_fifth": [("a fifth", "frac")],
    "e1_commission": [("one half", "frac")],
    "e1_600k": [("fix hundred thoufand", EN)],
    "e1_145": [("a hundred and forty five millions", EN)],
    "rk_notice": [("2009", "num"), ("two paragraphs", EN)],
    "th_six": [("two months", EN)],
    "th_joint": [("six months", EN)],
    "th_eight": [("eight", EN)],
    "th_ten": [("ten payments", EN), ("one day", EN), ("one payment", EN), ("ten days", EN)],
    "hu_third": [("one-third", "frac")],
    "hu_net1771": [("1,53,33,660", "num")],
    "hu_may1770": [("1770", "num"), ("one-third", "frac")],
    "hu_24_30": [("Twenty", EN), ("twenty-four", EN), ("thirty", EN)],
    "hu_ten": [("nine", EN), ("ten millions", EN)],
    "hu_farthings": [("three-halfpence", "pence"), ("1865", "num"), ("66", "num"), ("three-farthings", "pence")],
}


def check_readings(df: pd.DataFrame) -> None:
    n = 0
    for r in df.itertuples():
        if r.file == "qingshigao":                        # read in qing()
            continue
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
        else:
            got = [float(x.replace(",", "")) for x in re.findall(r"\d[\d,]*(?:\.\d+)?", r.quote)]
        assert [round(g, 9) for g in got] == [round(v, 9) for v in vals], f"{r.id}: read {got}, value column {vals}"
        n += 1
    qing()
    quoted("rows with values, each read from its quotation (and the 清史稿 row)", n + 1, 151)


# ---------------------------------------------------------------------------------------------------
# 2. Every “…” of the text against the snapshot
PUNCT = re.compile(r"[\s，。、；：！？“”‘’（）《》·…—﹑,.;:!?'\"()\[\]|\-]")
# terms of the text and claims it examines, which are not quotations
ALLOW = {"千年宏观数据", "真实的", "循环的", "虚构的", "生产性的", "生产", "普遍过剩", "先令", "万", "1771", "177 1",
         "节俭必然有益"}
# the chapter's Chinese renderings of the English quotations: rendering -> row (or rows)
TRANSLATIONS = {
    # opening
    "我们这里的情形非常凄惨：接连不断的破产，信用全面丧失，猜疑没完没了": "rk_hume1",
    "这些事件对你的理论有什么影响吗？": "rk_hume3",
    "为了解救国家的困境": "wn_newbank",
    "他描述的是哪一家银行，是清楚的": "rk_whichbank",
    "每一个国家一年的劳动，是最初供给它一年所消费的全部生活必需品与便利品的基金": "wn_annual",
    # sec:smith-world
    "声称要证明国家的财富正在迅速减少": "wn_declining",
    "四次耗资巨大的对法战争": "wn_wars",
    "欠下了超过 1.45 亿英镑的债": "wn_145", "总数不会少于 2 亿英镑": "wn_145", "超过 1.45 亿英镑": "wn_145",
    "无疑延缓了英格兰走向财富与改良的自然进程，却没能让它停下来": "wn_retarded", "却没能让它停下来": "wn_retarded",
    "公共银行": "wn_glasgow",
    "不会少于一百万英镑": "wn_metal_m",
    "不会少于两百万英镑": "wn_twomillion", "很可能不到五十万英镑": "wn_twomillion",
    "现金账户": "wn_instal",
    "比如两三千英镑": "wn_cash",
    "我不敢说知道": "wn_notknow",
    "据认为不到五百年不会翻一番": "wn_double", "二十或二十五年就翻一番": "wn_double", "不到五百年不会翻一番": "wn_double",
    "似乎长期停滞": "wn_china_stat", "几乎一样": "wn_china_stat",
    "这大概就是孟加拉……目前的状况": "wn_bengal",
    "一年里饿死三四十万人": ("wn_bengal_die", "e1_bengal"), "三四十万人": ("wn_bengal_die", "e1_bengal"),
    # sec:smith-division
    "取决于两种不同的情况：第一，劳动通常运用得是否熟练、灵巧、有判断；第二，从事有用劳动的人数与不从事有用劳动的人数之比": "wn_two",
    "似乎更多地取决于前一个情况，而不是后一个": "wn_former",
    "尽最大的努力，大概一天也做不出一枚别针，肯定做不出二十枚": "wn_pinone",
    "大约十八道不同的工序": "wn_eighteen",
    "我见过一家这样的小工场，只雇了十个人": "wn_ten",
    "能做出大约十二磅别针": "wn_twelve",
    "一天能做出四万八千多枚别针": ("wn_48000", "e1_pins"), "四万八千多枚": ("wn_48000", "e1_pins"),
    "肯定每人一天做不出二十枚，也许连一枚也做不出；就是说，肯定不到他们现在能做的二百四十分之一，也许不到四千八百分之一": "wn_240",
    "二百四十分之一": "wn_240", "也许连一枚也做不出": "wn_240", "肯定做不出二十枚": "wn_pinone",
    "从一种工作转到另一种工作时通常损失的时间": "wn_three",
    "便利和简化了劳动，使一个人能做许多人的工作": "wn_three",
    "所以分工的程度，总要受这种能力的大小限制，换句话说，受市场范围的限制": "wn_market",
    "每天做一千枚钉子，一年做三百个工作日，一年就做三十万枚钉子": "wn_nails",
    "一年也不可能卖出一千枚，也就是一天的活儿": "wn_nails2",
    "由两个人照料，八匹马拉着，大约六个星期，在伦敦与爱丁堡之间运去又运回将近四吨货物": "wn_waggon",
    "由六个或八个人驾驶": "wn_ship",
    "五十辆宽轮大车，由一百个人照料，四百匹马拉着": "wn_fifty",
    "伦敦与加尔各答之间，什么货物负担得起陆运的费用？": "wn_calcutta",
    "在孟加拉，恒河与其他几条大河形成了许多可以通航的水道，就像尼罗河在埃及一样": "wn_ganges",
    "许许多多的运河": "wn_chinacanals",
    # sec:smith-capital
    "有一种劳动，加在对象上能增加它的价值；另一种没有这种作用。前者因为生产价值，可以叫作生产性劳动，后者叫作非生产性劳动。": "wn_productive",
    "一个人雇用许多工匠就变富，养活许多仆人就变穷。": "wn_menial", "养活许多仆人": "wn_menial",
    "后者的劳动也有它的价值，也和前者一样应得到报酬": "wn_value", "也有它的价值，也应得到报酬": "wn_value",
    "固定并实现在某种特定的对象或可以出售的商品上，这种商品在劳动过去以后至少还能保存一段时间": "wn_vendible",
    "君主，以及在他手下任职的全部司法与军事官员，整个陆军与海军，都是非生产性劳动者": "wn_sovereign",
    "无论多么光荣、多么有用、多么必要": "wn_useful",
    "牧师、律师、医生、各种文人；演员、小丑、音乐家、歌剧演员、歌剧舞蹈演员等等": "wn_churchmen",
    "资本因节俭而增加，因奢侈与行为失当而减少": "wn_parsimony",
    "勤劳不是资本增加的直接原因，节俭才是": "wn_notindustry", "节俭，而不是勤劳，是资本增加的直接原因": "wn_notindustry",
    "每年省下来的，与每年花掉的一样，有规律地被消费掉，而且几乎在同一时间；只是消费它的是另一群人": "wn_consumed",
    "同样被消费掉": "wn_consumed", "省下的同样被消费掉": "wn_consumed",
    "消费是一样的，消费者不同。": "wn_consumers",
    "每个浪费的人都像是公众的敌人，每个节俭的人都是公众的恩人": "wn_benefactor",
    "是改善自身境况的愿望；这种愿望虽然一般是平静的、不动感情的，却从娘胎里就跟着我们，直到进坟墓都不离开": "wn_better",
    "也许不比千分之一多多少": "wn_bankrupt",
    "除了增加生产性劳动者的人数，或者提高原有劳动者的生产力，没有别的办法增加它的价值": "wn_twomeans",
    "死的资财": "wn_deadstock", "是死的资财，只要还留在这种状态，对他、对他的国家都不生产任何东西": "wn_deadstock",
    "大国从来不会因私人的浪费与失当而变穷，虽然有时会因公家的浪费与失当而变穷。": "wn_public",
    "永远、毫无例外，是社会上最大的浪费者": "wn_spendthrifts",
    # sec:smith-mercantile
    "要认真去证明财富不在于货币或金银，而在于货币能买到的东西，金银的价值只在于能买东西，这未免太可笑了。": "wn_ridiculous",
    "通常只是一小部分，而且总是最不能生利的部分": "wn_unprofitable",
    "引起普遍抱怨钱少的，不是金银的缺乏，而是这些人借钱的困难，以及他们的债主收债的困难": "wn_scarcity",
    "在这种情况下，金银的出口不是衰落的原因，而是衰落的结果": "wn_effect",
    "一个商人仓库里货物很多，有时会因为不能及时卖掉而破产，一个国家却不会遭遇同样的意外": "wn_nation",
    "他想的只是自己的安全": "wn_domestic",
    "他想的只是自己的得益；在这里，像在许多别的场合一样，他被一只看不见的手引导着，去促进一个并非他本意的目的": ("wn_invisible", "e2_invisible"),
    "他追求自己的利益，往往比真心想促进社会利益时更有效地促进了社会利益。我从没听说那些假装为公益而做生意的人做过多少好事。": "wn_publicgood",
    # sec:smith-paper
    "流通就由一个新的轮子来推动，造它、养它都比旧轮子便宜": "wn_wheel",
    "就足以应付随时的兑现要求": "wn_100k",
    "八万英镑的金银可以这样从国家的流通中节省下来": "wn_80k",
    "五分之一": ("wn_fifth", "e1_fifth"),
    "在各自的金库里留出二十万英镑应付随时的兑现要求": "wn_million",
    "流通的渠道，如果允许我这样说，仍然和以前一样": "wn_channel", "渠道": "wn_channel",
    "八十万英镑必然溢出": "wn_overflow",
    "纸币不能出国，因为离开发行它的银行、离开能依法要求兑付的国家，它在日常支付中不会被接受": "wn_abroad",
    "其余五分之四里的大部分": ("wn_fourfifths", "e1_fourfifths"),
    "也必然大大增加这种劳动的数量，从而大大增加一年的土地与劳动产出的价值": "wn_considerable",
    "大大增加": "wn_considerable",
    "不同的作者估计为五分之一、十分之一、二十分之一与三十分之一": "wn_ratios",
    "即使是较大的数字 1.60\\%，也是比较小的": "rk_small",
    "在这里，我认为，斯密打了个盹": "rk_nodded",
    "暗中假定农业投资的回报率非常高": "rk_assume",
    "它把全国的草与谷物运到市场上，自己却连一根草、一粒谷都不生产": "wn_highway",
    "一种空中的车道": ("wn_waggonway", "e1_waggonway"), "空中的车道": ("rk_draft", "wn_waggonway"),
    "这样悬在纸币的代达罗斯翅膀上": ("wn_daedalian", "e1_daedalian"), "在金银的坚实地面上行走": "wn_daedalian",
    "代达罗斯的翅膀": ("wn_daedalian", "e1_daedalian"),
    "一场失败的战争": "wn_war",
    "用蜡把羽毛粘成翅膀": "rk_wax",
    "或者说 2008 年的危机": "rk_meltdown",
    "正好能吸收四万英镑": "wn_40k", "必须随时在金库里留一万英镑的金银": "wn_40k",
    "超过流通容易吸收与使用的那四千英镑，几乎一发出去就会回到它手里": "wn_44k",
    "要留的不只是一万一千英镑，而是一万四千英镑": "wn_14k", "一万一千英镑": "wn_14k",
    "得不到任何利息": "wn_gainnothing",
    "平均约八十五万英镑": "wn_boe_coin",
    "这样损失二点五到三个百分点": "wn_boe_loss",
    "很少低于一点五或两个百分点": "wn_agents", "四分之三个百分点，即每一百英镑十五先令": "wn_agents",
    "英国两个地区的一些大胆的投机者过度经营，是纸币过度流通的根本原因": "wn_projectors",
    "有人说，纸币的增加增加了整个通货的数量，因而降低了它的价值，必然抬高商品的货币价格。": "wn_hume",
    "从流通中取走的金银，总是等于加进来的纸币，所以纸币不一定增加整个通货的数量。": "wn_equal",
    "苏格兰的粮食却从没有那样便宜过": "wn_1759",
    "休谟先生出版他的《政治论丛》的时候": "wn_seasons", "大概是由于年成不好，而不是由于纸币的增加": "wn_seasons",
    "在任何方面取决于发行人的善意": "wn_otherwise", "情形就不一样了": "wn_otherwise",
    "数量相同": "th_error",
    "同一张钞票可以一天完成十笔支付，也可以十天完成一笔支付": "th_ten",
    # sec:smith-realbills
    "银行可以适当地贷给一个商人或任何企业主的，不是他做生意的全部资本，甚至不是资本中相当大的一部分，而只是他本来不得不闲置在身边、留作现款以应付随时之需的那一部分。": "wn_propriety",
    "一家银行给一个商人贴现一张真实的汇票，它由一个真实的债权人开出，以一个真实的债务人为付款人，到期时真的由这个债务人付清；银行只是预付给他一部分价值，这部分价值他本来不得不闲置在身边、留作现款以应付随时之需。": "wn_realbill",
    "真实的债权人……真实的债务人": ("wn_realbill", "e1_realdebtor"),
    "像一个水池，虽然不断有水流出，也不断有同样多的水流进": ("wn_pond", "e1_pond"), "水池": ("wn_pond", "e1_pond"),
    "比如四个、五个、六个或八个月": "wn_months",
    "一家把钱借给大概五百个不同的人、注意力又不断被各种事情占据的银行，除了自己的账簿提供的情况以外，对大部分债务人的行为与境况，不可能有经常的了解。": "wn_books",
    "开凿矿井、安装抽水机械、修筑道路与车道": "wn_mine",
    "不应当向银行借，而应当凭债券或抵押，向那些打算靠利息生活的私人借": "wn_bond",
    "完全等于、甚至略多于国家的流通容易吸收与使用的数量": "wn_25years", "略多于": "wn_25years",
    "濒临破产的不幸商人有时采用的办法": "wn_brink",
    "上次战争期间，贸易的高利润诱人过度经营": "wn_latewar",
    "这房子是危楼，一个疲倦的旅客对自己说，它不会撑得太久；可它今晚倒下来的可能不大，我就冒险在里面睡一晚。": "wn_crazy",
    "爱丁堡的商人 A 开一张汇票给伦敦的 B，两个月后付款。": "wn_AB",
    "利息是每年 5\\%，每开一次票，佣金从不低于 0.5\\%。佣金一年要付六次以上，A 用这个办法筹到的钱，一年的成本必然超过 8\\%": ("wn_8pct", "e1_commission"),
    "这种做法叫作靠流通筹钱": "wn_circulation",
    "据认为在 6\\% 到 10\\% 之间": "wn_profits",
    "这种付款完全是虚构的": "wn_fictitious",
    "从来没有被真正流进来的水补上": "wn_stream",
    "尽可能难以分辨真实的汇票与虚构的汇票": "wn_distinguish",
    "目光短浅、胆小怯懦": "wn_dastardly",
    "几令纸": "wn_reams",
    "他们把自己的困境叫作国家的困境": "wn_distress",
    "实质上显然等于 A 与 B 以两人的共同担保借了这笔钱六个月": "th_joint",
    "超过 8\\%": "wn_8pct",
    "至少 14\\%": "wn_14pct", "至少要花 14\\%": "wn_14pct",
    "比斯密想象的": "th_less",
    "像派人提着水桶到几英里外的井里打水": "wn_buckets",
    "真实票据学说第一个彻底的阐述者": "rk_mints",
    "所以即使每一家银行、包括中央银行都遵循真实票据原则，通胀也可以持续下去": "rk_mintscrit",
    "谬误的真实票据学说": "rk_fallacious",
    "犯了把真实票据当作货币政策规则的错误": "rk_mistake",
    "在斯密的模型里，物价水平由金银本位来锚定；真实票据是为了防止不审慎的银行经营。": "rk_laidler",
    "真实票据代表财产、虚构票据不代表，这种看法对一种票据多给了公道，对另一种少给了公道": "th_justice",
    # sec:smith-ayr
    "在这一片抱怨与困境之中，苏格兰设立了一家新银行，明说是为了解救国家的困境。": "wn_newbank",
    "用意是慷慨的，执行却是不审慎的": "wn_generous",
    "似乎几乎不区分真实票据与循环票据，一律贴现": "wn_nodistinction",
    "公开的原则": "wn_land",
    "三年之内，艾尔银行成了一个巨人": "rk_colossus",
    "股东中很大一部分人在缴第一期股款时，就在本行开了现金账户": "wn_instal",
    "允许他们中的许多人从这个现金账户借钱，来缴以后各期的股款": "wn_borrowpaid",
    "只是把刚从一个金库里拿出来的钱放进另一个金库": "wn_coffer",
    "从来没有充实过": "wn_never",
    "值几百万": "wn_estates",
    "大约二十万英镑": "wn_200k", "超过六十万英镑": ("wn_600k", "e1_600k"), "超过八十万英镑，利率 5\\%": "wn_800k",
    "在它全部业务的四分之三以上，损失超过 3\\%": "wn_loss3", "四分之三以上": "wn_loss3",
    "有大量的往来": "rk_june8",
    "摇摇欲坠，这是整场灾难里最大的灾难之一，因为它雇用了将近一万人": "rk_hume2",
    "那个时代的雷曼兄弟": "rk_300k",
    "伦敦与阿姆斯特丹之间的贸易与金融陷于停顿": "rk_halt",
    "比本来能做的多做了大约两年": "wn_longer",
    "如果他们中的大部分人早两年被迫停下来，对他们自己、对他们的债主、对他们的国家都会好得多": "wn_sooner",
    "受到张开双臂的欢迎": "wn_openarms",
    "很容易地走出了那个致命的圈子": "wn_fatal",
    "加重了它想解救的国家的真实困境": "wn_realdistress",
    "从极大的困境中解救了出来": "wn_rivals",
    "雇许多人不断提着水桶，到几英里外的井里打水来补充": "wn_buckets",
    "只会把这家银行变成整个国家的一种普通的贷款所": "wn_loanoffice",
    # sec:smith-regulation
    "在伦敦，没有面额低于十英镑的银行券流通，纸币大体限于商人之间的流通": "wn_10pound",
    "二十先令": "wn_20s",
    "这样的穷银行家经常破产，可能给许多收了他们银行券的穷人带来很大的不便，有时甚至是很大的灾难": "wn_beggarly",
    "也许最好是全国任何地方都不发行面额低于五英镑的银行券": "wn_5pound",
    "是对天赋自由的明显侵犯，而法律的本分是保障这种自由，不是侵犯它": "wn_liberty", "天赋自由": "wn_liberty",
    "为了防止火灾蔓延而规定修筑隔墙，同样是对天赋自由的侵犯，与这里提议的银行业管制完全属于同一类": ("wn_party", "e1_party"),
    "如果禁止银行家发行面额低于一定数额的流通银行券或见票即付的票据，如果他们有义务一经提示就立即无条件地兑付这些银行券，那么，在其他一切方面，他们的营业都可以完全自由，而不危及公众的安全。": ("wn_free", "e1_free"),
    "完全自由": ("wn_free", "e1_free"),
    "最近英国两个地区银行公司的增多，许多人为之惊慌，其实不但没有减少，反而增加了公众的安全": "wn_security",
    "把整个流通分成更多的部分，任何一家公司的倒闭，这种事在事物的进程中总会发生，对公众的影响就小了": "wn_failure",
    "这种自由竞争也迫使所有银行家对客户更宽厚，免得对手把客户抢走。": "wn_compet",
    "现行的法定利率 5\\% 也许和任何利率一样合适": "wn_legal5",
    "大部分要借出去的钱就会借给浪费者与投机者，只有他们愿意付这样高的利息": "wn_prodigals",
    "（1）一部合理的高利贷法，（2）禁止银行券上的选择条款，（3）把真实票据原则作为银行业文化的一部分，（4）禁止面额低于五英镑的银行券": "rk_four",
    "前两条在 1772 年危机爆发时已经实行了": "rk_inplace",
    "由董事选择，在提示后六个月": "wn_optional",
    "尽管斯密主张，五英镑的下限无论在法律上还是在实践上，苏格兰都从未采用": "rk_never5",
    "可能会有相当大的作用": "rk_substantial",
    "靠范围更窄、更懂行的一类持券人": "rk_sophisticated",
    "艾尔银行的倒闭不是因为不懂审慎经营的规则，而是因为决意不理会它们": "rk_ignore",
    "主要的问题不是复杂的失误，而是过度的内部人贷款": "rk_insider", "过度的内部人贷款": "rk_insider",
    "不仅是一家普通的银行，而且是国家的一部大机器": "wn_engine",
    "支撑了不仅英格兰、而且汉堡与荷兰的主要商号的信用": "wn_houses",
    "在一个星期里": "wn_1763", "不过，我不敢担保数额有这么大，时间有这么短": "wn_1763", "不敢担保": "wn_1763",
    "斯密没有明确赞成用这些权力来缓和或防止危机": "rk_notendorse",
    "苏格兰那样的自由银行制度": "rk_bagehot",
    "斯密是一个经验主义者，愿意根据当时与历史的经验修改自己的看法。": "rk_empiricist",
    # sec:smith-states
    "引起劳动工资上涨的，不是国民财富的实际大小，而是它的不断增长。": "wn_increase",
    "英格兰今天无疑比北美的任何地方都富得多": "wn_richer", "却比英格兰的任何地方都高得多": "wn_richer",
    "在最近的骚乱开始以前": "wn_ny_lab",
    "三先令六便士殖民地货币，合两先令英镑": ("wn_ny_lab", "e1_ny"),
    "十先令六便士殖民地货币，外加一品脱朗姆酒，值六便士英镑，合计六先令六便士英镑": "wn_ny_ship",
    "八先令殖民地货币，合四先令六便士英镑": "wn_ny_house",
    "五先令殖民地货币，合大约两先令十便士英镑": "wn_ny_tailor", "大约": "wn_ny_tailor",
    "这些价格都高于伦敦的价格": "wn_london",
    "这种增长主要不是由于不断输入新居民，而是由于人类自身的大量繁殖": "wn_species", "不是由于输入新居民": "wn_species",
    "使人口的增殖在第一个地方迅速前进，在第二个地方缓慢渐进，在最后一个地方完全停滞": "wn_states",
    "缓慢渐进": "wn_states", "停滞": "wn_states",
    "在停滞的状态下是艰难的，在衰退的状态下是悲惨的": "wn_hard",
    "都说中国的劳动工资低，劳动者难以养家": "wn_china_wages",
    "在广州附近，有好几百户人家，一般的说法是好几千户，在陆地上没有住处，常年住在江河运河的小渔船上": "wn_canton",
    "也许停滞不前，却似乎没有退步": "wn_china_back",
    "中国似乎长期停滞，大概早就积累到了与它的法律与制度的性质相适应的全部财富": "wn_china_laws",
    "一个忽视或者鄙视对外贸易、只许外国船只进入一两个港口的国家，不能做它在不同的法律与制度下所能做的那么多的生意": "wn_ports",
    "几乎没有任何安全": "wn_mandarins", "在司法的名义下被下级官吏掠夺": "wn_mandarins",
    "据说中国普通的利率是 12\\%": "wn_china12",
    "在东印度压迫人、专横跋扈的那家商业公司": "wn_company", "也许没有比这两个地方的不同状况更好的说明了": "wn_company",
    "钱常常以 40\\%、50\\% 与 60\\% 的利率借给农民，下一季的收成抵押来还债": ("wn_bengal60", "e1_bengal60"),
    "几年前孟加拉的干旱，也许本来会造成一场很严重的歉收。东印度公司的雇员对大米贸易施加的一些不当的规定、一些不明智的限制，也许促成了把歉收变成饥荒。": "wn_drought",
    "也许": "wn_drought",
    # the case of Bengal
    "1770 年 5 月底以前，官方估计人口的三分之一已经消失": "hu_may1770", "三分之一": "hu_may1770",
    "为所有官方的与最审慎的": "hu_accepted",
    "在九个月里夺去了一千万人的生命": "hu_ten", "一千万人": "hu_ten",
    "1772 年 11 月 3 日，于威廉堡": "hu_date",
    "尽管全省至少失去了三分之一的居民，耕地也随之减少": "hu_third", "至少三分之一的居民": "hu_third",
    "甚至超过了 1768 年": "hu_exceeded",
    "是因为它被强行维持在原来的标准上": "hu_kept", "强行维持在原来的标准上": "hu_kept",
    "纳贾伊": "hu_najay",
    "是向各类田地上实际还活着的居民加征的一种摊派，用来弥补邻居死去或逃走而损失的地租": "hu_najay",
    "只要政府允许自由贸易": "wn_freetrade",
    "有时在一季开始的时候就造成饥荒": "wn_reasonable",
    "发布公告，禁止囤积或垄断粮食": "hu_proclaim",
    "1770 年，政府禁止它所谓的粮食垄断，阻止了价格立即涨到它自然的水平": "hu_interdict",
    "省着用，把压力平均分摊到整整九个月": "hu_spread",
    "不仅垄断粮食，而且强迫穷苦的农民卖掉下一季必需的种子": "hu_court",
    "这些垄断的欧洲人": "hu_court2", "我们有理由怀疑，他们只能是我们公司里有些地位的人": "hu_court2",
    "纵容了粮食的垄断与私人贸易": "hu_reproach",
    # sec:smith-test
    "无疑偏低": "cz_slavery",
    "银行券增加到 2.5 倍以上，年率 8.5\\%；存款增加到将近 3.3 倍，年率 10.8\\%。": "rk_bos2",
    "小额银行券狂热": "rk_zenith",
    "我的猜测是，小面额铸币的短缺是最重要的因素": "rk_coins",
    "七年战争（1754—1763）造成了英国铸币的净流失": "rk_seven",
    # the deeper box
    "一亿四千五百多万": "e1_145",
    "消费是一切生产的唯一目的": "wn_soleend", "重商主义的结论": ("wn_conclusion", "e2_ch8"),
    "被迫停止兑付银行券": "rk_june22", "停止以金银兑付银行券": "rk_june25",
    "包括一些印第安人": "cz_indians",
}


def norm(s: str) -> str:
    return PUNCT.sub("", s)


def tex_text() -> str:
    return "\n".join(l for l in TEX.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("%"))


def text_quotations() -> list[str]:
    return re.findall(r"“([^”]*)”", tex_text())


def check_text(df: pd.DataFrame) -> None:
    ids = set(df["id"])
    corpus = [norm(q) for q in df[df["file"] == "qingshigao"]["quote"]]       # quoted untranslated
    used, n = set(), 0
    for q in text_quotations():
        n += 1
        used.add(q)
        if q in ALLOW:
            continue
        if q in TRANSLATIONS:
            t = TRANSLATIONS[q]
            for rid in (t,) if isinstance(t, str) else t:
                assert rid in ids, rid
            continue
        assert any(norm(q) in c for c in corpus), f"not in the snapshot: “{q}”"
    stale = (set(ALLOW) | set(TRANSLATIONS)) - used
    assert not stale, f"listed but not in the text: {sorted(stale)}"
    print(f"ok {n} quotations of the text found in the snapshot (or listed as exceptions)")


# ---------------------------------------------------------------------------------------------------
# 3. Numbers, section by section
def opening(F, Y):
    chk("June 9, 1772 (fled)", F["rk_june9"][0], 9)
    chk("    year", Y["rk_june9"], 1772)
    chk("June 12 (horseman)", F["rk_june12"][0], 12)
    chk("June 22 (stopped)", F["rk_june22"][0], 22)
    quoted("15 private bankers in Edinburgh", int(re.match(r"Fifteen", quotes()["rk_fifteen"]) is not None) * 15, 15)
    chk("June 27 (Hume's letter)", F["rk_humedate"][0], 27)
    chk("four years later: 1776 - 1772", 1776 - Y["rk_june9"], 4)


def world(F, Y, B):
    pct("GB population 1700 (万)", B.pop_gb_m[1700] * 100, 621, 0)
    pct("    1776 (万)", B.pop_gb_m[1776] * 100, 838, 0)
    pct("GB real GDP per head 1700 (2013 pounds)", B.gb_real_gdp_pc_2013gbp[1700], 1610, 0)
    pct("    1776", B.gb_real_gdp_pc_2013gbp[1776], 1977, 0)
    chk("    76 years", 1776 - 1700, 76)
    pct("    growth (%)", 100 * (B.gb_real_gdp_pc_2013gbp[1776] / B.gb_real_gdp_pc_2013gbp[1700] - 1), 22.8)
    pct("    a year (%, compound)", 100 * growth_rate(B.gb_real_gdp_pc_2013gbp[1700], B.gb_real_gdp_pc_2013gbp[1776], 76,
                                                   compound=True), 0.27, 2)
    chk("wars began 1688, 1701, 1742, 1756; rebellions 1715, 1745", F["wn_wars"], [1688, 1701, 1742, 1756, 1715, 1745])
    chk("more than 145 million (亿)", F["wn_145"][0] / 1e8, 1.45)
    chk("    not less than 200 million (亿)", F["wn_145"][1] / 1e8, 2)
    pct("debt 1700 (万)", B.total_debt_gbp_m[1700] * 100, 1410, 0)
    chk("Treaty of Paris (1763)", Y["rk_treaty"], 1763)
    pct("debt 1763 (亿)", B.total_debt_gbp_m[1763] / 100, 1.342, 3)
    pct("    with annuities (亿)", B.debt_incl_annuities_gbp_m[1763] / 100, 1.442, 3)
    pct("debt 1776 (亿)", B.total_debt_gbp_m[1776] / 100, 1.366, 3)
    pct("    with annuities, % of GDP", B.debt_pct_gdp[1776], 97.5)
    # Scotland
    chk("Bank of Scotland 1695, Royal Bank 1727", F["wn_banks"], [1695, 1727])
    chk("before the Union: 1707", Y["wn_1707"], 1707)
    chk("    a million", F["wn_metal_m"][0], 1e6)
    chk("    411,117 10s 9d", F["wn_1707"][1], lsd(411_117, 10, 9))
    chk("now: two millions", F["wn_twomillion"][0], 2e6)
    chk("    gold and silver: half a million (万)", F["wn_twomillion"][1] / 1e4, 50)
    chk("notes of 20 shillings", F["wn_20s"][0], 20)
    chk("cash account: two or three thousand", F["wn_cash"][:2], [2000, 3000])
    chk("    two sureties", F["wn_cash"][2], 2)
    chk("Glasgow: doubled in fifteen years", F["wn_glasgow"][0], 15)
    chk("Scotland: more than quadrupled", F["wn_glasgow"][1], 4)
    # North America and the East
    chk("Europe: 500 years", F["wn_double"][0], 500)
    chk("    colonies: 20 or 25 years", F["wn_double"][1:], [20, 25])
    C = colonies()
    pct("colonies 1700 (万)", C.total[1700] / 1e4, 25.1)
    pct("    1770 (万)", C.total[1770] / 1e4, 214.8)
    chk("Marco Polo: more than 500 years ago", F["wn_china_stat"][0], 500)
    chk("Bengal: three or four hundred thousand (万)", [x / 1e4 for x in F["wn_bengal_die"]], [30, 40])


def division(F):
    P = pins(F)
    chk("one pin; twenty", F["wn_pinone"], [1, 20])
    chk("eighteen operations", F["wn_eighteen"][0], 18)
    chk("ten men; twelve pounds; 4,000 a pound", [F["wn_ten"][0], F["wn_twelve"][0], F["wn_4000"][0]], [10, 12, 4000])
    chk("ex:smith-pins (1): 12 x 4,000", P["day"], 48_000)
    chk("    Smith: forty-eight thousand", F["wn_48000"][1], P["day"])
    chk("    each", P["each"], 4800)
    chk("    Smith: four thousand eight hundred", F["wn_4800"][0], P["each"])
    chk("    / 20 = 240", P["x20"], 240)
    chk("    Smith: two hundred and fortieth", F["wn_240"][2], 240)
    chk("    / 1 = 4,800", P["x1"], 4800)
    chk("    Smith: four thousand eight hundredth", F["wn_240"][3], 4800)
    chk("three circumstances", F["wn_three"][0], 3)
    chk("(2) at most 1 / 0.4", 1 / SHARE, 2.5)
    pct("    0.5 / 0.4 - 1 (%)", 100 * (SHARE2 / SHARE - 1), 25, 0)
    quoted("(3) ln 2 / ln 1.0027 (years)", math.log(2) / math.log(1.0027), 257, tol=0.5)
    # the extent of the market
    chk("nailer: a thousand a day, 300 days, 300,000 a year", F["wn_nails"], [1000, 300, 300_000])
    chk("    1,000 x 300", F["wn_nails"][0] * F["wn_nails"][1], F["wn_nails"][2])
    chk("    not one thousand in the Highlands", F["wn_nails2"][0], 1000)
    chk("waggon: 2 men, 8 horses, 6 weeks, 4 tons", F["wn_waggon"], [2, 8, 6, 4])
    chk("ship: 6 or 8 men, 200 tons", F["wn_ship"], [6, 8, 200])
    chk("    50 waggons, 100 men, 400 horses", F["wn_fifty"], [50, 100, 400])
    K = carriage(F)
    chk("ex:smith-market (1): 200 / 4", K["waggons"], F["wn_fifty"][0])
    chk("    men", K["men"], F["wn_fifty"][1])
    chk("    horses", K["horses"], F["wn_fifty"][2])
    chk("    100 / 8", K["x_lo"], 12.5)
    pct("    100 / 6", K["x_hi"], 16.7)
    chk("(2) 300,000 / 50 households", F["wn_nails"][2] / NAILS_PER_HOUSE, 6000)
    chk("    15 x 50", VILLAGE * NAILS_PER_HOUSE, 750)
    assert VILLAGE * NAILS_PER_HOUSE < F["wn_nails"][0]


def capital(F, B):
    chk("one in a thousand", F["wn_bankrupt"][0], 1 / 1000)
    pct("1700-1763: debt 1,410 万 -> 1.342 亿", B.total_debt_gbp_m[1763] / 100, 1.342, 3)
    pct("    GDP per head 1,610 -> 1,945", B.gb_real_gdp_pc_2013gbp[1763], 1945, 0)
    pct("    growth (%)", 100 * (B.gb_real_gdp_pc_2013gbp[1763] / B.gb_real_gdp_pc_2013gbp[1700] - 1), 20.8)


def paper(F, Y):
    chk("100,000 of notes, 20,000 of gold and silver", F["wn_100k"], [100_000, 20_000])
    chk("    80,000 spared", F["wn_80k"][0], F["wn_100k"][0] - F["wn_100k"][1])
    chk("    a fifth", F["wn_fifth"][0], F["wn_100k"][1] / F["wn_100k"][0])
    m = F["wn_million"]
    chk("one million; 200,000 kept", [m[0], m[2]], [1e6, 200_000])
    chk("    800,000 + a million = 1,800,000", m[3] + m[4], m[5])
    chk("    800,000 = 1,000,000 - 200,000", m[0] - m[2], m[3])
    chk("    overflows: 800,000 (万)", F["wn_overflow"][0] / 1e4, 80)
    chk("    the other four-fifths", F["wn_fourfifths"][1], 1 - F["wn_fourfifths"][0])
    chk("ratios: a fifth, tenth, twentieth, thirtieth", F["wn_ratios"], [1 / 5, 1 / 10, 1 / 20, 1 / 30])
    chk("Rockoff: profit 10%", F["rk_profit10"][0], 100 * PROFIT)
    chk("    800,000 at 10% = 80,000", F["rk_80k"][0] * PROFIT, F["rk_80k"][1])
    pct("    1/5: 1.60%", 100 * saving(1 / 5, 1 / 5, PROFIT), F["rk_160"][0], 2)
    pct("    1/30: 0.27%", 100 * saving(1 / 30, 1 / 5, PROFIT), F["rk_027"][0], 2)
    chk("Rockoff: 10,000 tons of seed, 100,000 crop", F["rk_seed"], [10_000, 100_000])
    chk("    consumption 90,000, seed 20,000, harvest 200,000 (doubles)", F["rk_twice"][2] / F["rk_seed"][1], 2)
    chk("    900%", 100 * (F["rk_seed"][1] - F["rk_seed"][0]) / F["rk_seed"][0], F["rk_900"][0])
    # ex:smith-saving
    for frac, txt in zip(F["wn_ratios"], [1.6, 0.8, 0.4, 0.27]):
        pct(f"ex:smith-saving (1) M/Y = {frac:.4f}", 100 * saving(frac, 1 / 5, PROFIT), txt, 2 if txt == 0.27 else 1)
    pct("    (2) 10% / (0.2 x 0.8)", 100 * TARGET / ((1 / 5) * (4 / 5)), 62.5)
    pct("        10% / (1/30 x 0.8)", 100 * TARGET / ((1 / 30) * (4 / 5)), 375, 0)
    # the metaphor
    chk("draft before April 1763", Y["rk_draft"], 1763)
    chk("crises of 1772 and 2008", F["rk_meltdown"], [1772, 2008])
    # over-issue
    X = reflux(F["wn_40k"][0], F["wn_40k"][1], F["wn_44k"][0])
    chk("40,000 absorbed, 10,000 kept, 44,000 issued", [F["wn_40k"][0], F["wn_40k"][1], F["wn_44k"][0]],
        [40_000, 10_000, 44_000])
    chk("    the 4,000 return", F["wn_44k"][1], F["wn_44k"][0] - F["wn_40k"][0])
    chk("    rho", X["rho"], 1 / 4)
    chk("    naive 11,000", X["naive"], F["wn_14k"][0])
    chk("    eq:smith-reflux 14,000", X["needed"], F["wn_14k"][1])
    chk("BoE coined 800,000 to a million, about 850,000", F["wn_boe_coin"], [800_000, 1e6, 850_000])
    chk("    bought at 4 pounds an ounce", F["wn_boe_loss"][0], 4)
    chk("    3:17:10 1/2", F["wn_boe_loss"][1], lsd(3, 17, 10.5))
    chk("    = 3.89375", lsd(3, 17, 10.5), 3.89375)
    loss = F["wn_boe_loss"][0] / F["wn_boe_loss"][1] - 1
    pct("    loss (%)", 100 * loss, 2.73, 2)
    assert F["wn_boe_loss"][2] <= 100 * loss <= F["wn_boe_loss"][3]
    quoted("    a year (万 pounds)", F["wn_boe_coin"][2] * loss / 1e4, 2.3, tol=0.05)
    chk("Scotch agents 1.5 or 2%, insurance 3/4% = 15s per 100 pounds", F["wn_agents"], [1.5, 2, 0.75, 15])
    chk("    15 shillings per 100 pounds", F["wn_agents"][3] / SHILLINGS / 100 * 100, F["wn_agents"][2])
    # Hume and Thornton
    chk("ten and five shilling notes, 1759", Y["wn_1759"], 1759)
    chk("1751 and 1752", F["wn_seasons"], [1751, 1752])
    chk("Thornton 1802: 1802 - 1776", Y["th_ten"] - 1776, 26)
    chk("    ten payments in one day, one in ten days", F["th_ten"], [10, 1, 1, 10])



def realbills(F):
    chk("four, five, six or eight months", F["wn_months"], [4, 5, 6, 8])
    chk("five hundred debtors", F["wn_books"][0], 500)
    chk("more than five and twenty years", F["wn_25years"][0], 25)
    chk("two months", F["wn_AB"][0], 2)
    chk("5%, 1/2% a draught, more than six times, more than 8%", F["wn_8pct"], [5, 0.5, 6, 8])
    chk("eq:smith-redraw: 5 + 6 x 0.5", redraw(F["wn_8pct"][0], F["wn_8pct"][2], F["wn_8pct"][1]), F["wn_8pct"][3])
    chk("profits 6 to 10%", F["wn_profits"], [6, 10])
    chk("(2) the note: 3% exchange", F["wn_exch3"][0], 3)
    chk("    4 x (3 + 0.5) = 14", F["wn_14pct"][0] * (F["wn_exch3"][0] + F["wn_14pct"][1]), F["wn_14pct"][2])
    chk("(3) Thornton: six months", F["th_joint"][0], 6)
    chk("    two-month bills", F["th_six"][0], 2)
    chk("    Thornton: eight per cent", F["th_eight"][0], 8)
    chk("    net of alternating commissions: the interest only", redraw(5, 6, 0.5) - 6 * 0.5, 5)


def ayr_bank(F, Y):
    chk("opened 6 November 1769", F["rk_opens"][0], 6)
    chk("    year", Y["rk_opens"], 1769)
    chk("by 1772: 25% notes, 25% deposits, 40% assets", F["rk_size"][2:], [25, 25, 40])
    chk("    public banks 21% of assets", F["rk_public21"][0], 21)
    chk("capital 160,000, 80% paid", F["wn_capital160"], [160_000, 80])
    A = ayr(F)
    chk("notes about 200,000; London bills upwards of 600,000; loans upwards of 800,000 at 5%",
        [F["wn_200k"][0], F["wn_600k"][0], F["wn_800k"][0], F["wn_800k"][1]], [200_000, 600_000, 800_000, 5])
    chk("    upwards of 8%, losing more than 3%, more than 3/4", F["wn_loss3"], [8, 3, 3 / 4])
    chk("ex:smith-ayr (1) income", A["income"], 40_000)
    chk("    London cost at 8%", A["london_cost"], 48_000)
    chk("(2) 600 / 800", A["share"], F["wn_loss3"][2])
    chk("    loss on the London part", A["loss"], 18_000)
    chk("    gain on the notes", A["gain"], 10_000)
    chk("    net", A["net"], -8_000)
    chk("(3) paid-up capital", A["paid"], 128_000)
    chk("    years", A["years"], 16)
    # the crisis
    chk("June 8 (the partner's bank failed)", F["rk_june8"][0], 8)
    chk("Carron: near 10,000 people (一万)", F["rk_hume2"][0] / 1e4, 1)
    chk("BoE offered 300,000 (万)", F["rk_300k"][0] / 1e4, 30)
    chk("first week of January 1773", Y["rk_halt"], 1773)
    chk("10 January 1773", F["rk_jan10"], [10, 1773])
    chk("    one Dutch banker 500,000 (万)", F["rk_500k"][0] / 1e4, 50)
    chk("Amsterdam loan office, January 1773", Y["rk_loanoffice"], 1773)
    chk("reopened 28 September 1772", F["rk_reopen"][0], 28)
    chk("    year", Y["rk_reopen"], 1772)
    chk("wind up 12 August 1773", F["rk_windup"][0], 12)
    chk("    year", Y["rk_windup"], 1773)
    chk("about two years longer; two years sooner", [F["wn_longer"][0], F["wn_sooner"][0]], [2, 2])


def regulation(F, Y):
    chk("under 10 pounds in London", F["wn_10pound"][0], 10)
    chk("20 shillings in Scotland", F["wn_20s"][0], 20)
    chk("no notes below 5 pounds", F["wn_5pound"][0], 5)
    chk("government 3%, private 4 and 4.5%, legal 5%", F["wn_legal5"], [3, 4, 4.5, 5])
    chk("    8 or 10%", F["wn_prodigals"], [8, 10])
    chk("Rockoff's four restrictions; 5 pounds", F["rk_four"], [1, 2, 3, 4, 5])
    chk("    in place in 1772", Y["rk_inplace"], 1772)
    chk("optional clause: six months", F["wn_optional"], [6, 6])
    chk("1766: May 15 option clause", F["rk_1766option"][0], 15)
    chk("    June 1, notes below 1 pound", F["rk_1766pound"], [1, 1])
    chk("    year", Y["rk_1766pound"], 1766)
    chk("Ayr: 1 pound and one guinea (1.05)", F["rk_guinea"], [1, 21 / SHILLINGS])
    chk("before 1769", F["rk_substantial"][0], 1769)
    chk("1763: about 1,600,000 in one week (万)", F["wn_1763"][1] / 1e4, 160)
    chk("    year", F["wn_1763"][0], 1763)
    chk("    the 1763 crisis centred in Amsterdam", Y["rk_1763"], 1763)
    chk("Schwartz: no crises after 1866", F["rk_schwartz"][3], 1866)


def states(F, Y, B):
    lab, ship, house, tailor = F["wn_ny_lab"], F["wn_ny_ship"], F["wn_ny_house"], F["wn_ny_tailor"]
    chk("New York 1773", lab[0], 1773)
    rate = lab[1] / lab[2]
    chk("ex:smith-wages (1) 3.5 / 2", rate, 1.75)
    pct("    1 / 1.75", 1 / rate, 0.571, 3)
    chk("(2) ship-carpenters 10.5 / 1.75", ship[0] / rate, 6)
    chk("    + 6d = 6s 6d", ship[0] / rate + ship[1], ship[2])
    pct("    tailors 5 / 1.75", tailor[0] / rate, 2.857, 3)
    pct("        Smith: about 2s 10d", tailor[1], 2 + 10 / 12, 3)
    pct("    house-carpenters 8 / 1.75", house[0] / rate, 4.571, 3)
    chk("        Smith: 4s 6d", house[1], 4.5)
    pct("        pence above 4s", (house[0] / rate - 4) * 12, 6.9)
    assert (house[0] / rate - house[1]) * 12 < 1
    assert (tailor[0] / rate - 2) * 12 > 10                                  # 'a little more than 2s 10d'
    chk("China 12%", F["wn_china12"][0], 12)
    pa, pb = qing()
    chk("乾隆二十九年 = 1764", 1736 + 29 - 1, 1764)
    chk("    六十年 = 1795", 1736 + 60 - 1, 1795)
    chk("    Y", Y["qs_qianlong"], 1764)
    chk("Bengal 40, 50 and 60%", F["wn_bengal60"], [40, 50, 60])
    # the case
    chk("Hunter: May 1770, one-third", F["hu_may1770"], [1770, 1 / 3])
    chk("    nine months, ten millions", F["hu_ten"], [9, 1e7])
    chk("Smith's 300,000-400,000 vs Hunter's 10 million: x25", F["hu_ten"][1] / F["wn_bengal_die"][1], 25)
    pct("    x33", F["hu_ten"][1] / F["wn_bengal_die"][0], 33, 0)
    chk("letter of 3 November 1772", F["hu_date"], [3, 1772])
    chk("    at least one-third", F["hu_third"][0], 1 / 3)
    chk("    1771 exceeded 1768", F["hu_exceeded"][0], 1768)
    chk("net 1768-69: 1,52,54,856", F["hu_net1768"][2], 15_254_856)
    chk("    years 1768-69", F["hu_net1768"][:2], [1768, 69])
    chk("net 1771-72: 1,53,33,660", F["hu_net1771"][0], 15_333_660)
    assert F["hu_net1771"][0] > F["hu_net1768"][2]
    chk("Hunter: 1770", F["hu_interdict"][0], 1770)
    chk("    three-farthings, not three-halfpence as in 1865-66", F["hu_farthings"], [1.5, 1865, 66, 0.75])
    # table
    C = colonies()
    pct("tab: colonies doubling 1700-1770", doubling(C.total[1700], C.total[1770], 70), 22.6)
    pct("    England 1700-1770", doubling(B.pop_england_m[1700], B.pop_england_m[1770], 70), 205, 0)
    pct("    England 1750-1780", doubling(B.pop_england_m[1750], B.pop_england_m[1780], 30), 107, 0)
    pct("    Qing 1764-1795 (%)", 100 * (pb / pa - 1), 44.4)
    pct("    Qing doubling", doubling(pa, pb, 1795 - 1764), 58, 0)


def test(F, Y, B):
    C = colonies()
    pct("colonies 1770 / 1700", C.total[1770] / C.total[1700], 8.56, 2)
    pct("    doubling", doubling(C.total[1700], C.total[1770], 70), 22.6)
    pct("    1700-1780", doubling(C.total[1700], C.total[1780], 80), 23.1)
    chk("Negro 1770", C.negro[1770], 459_822)
    pct("    share (%)", 100 * C.negro[1770] / C.total[1770], 21.4)
    chk("    17th century", F["cz_slavery"][0], 17)
    pct("white doubling 1700-1770", doubling(C.white[1700], C.white[1770], 70), 24.0)
    pct("Negro doubling 1700-1770", doubling(C.negro[1700], C.negro[1770], 70), 17.3)
    pct("England 1700 (万)", B.pop_england_m[1700] * 100, 520, 0)
    pct("    1770 (万)", B.pop_england_m[1770] * 100, 658, 0)
    pa, pb = qing()
    pct("Qing +44.4%", 100 * (pb / pa - 1), 44.4)
    pct("    a year (%, log)", 100 * growth_rate(pa, pb, 31), 1.19, 2)
    pct("    doubling", doubling(pa, pb, 31), 58, 0)
    assert doubling(pa, pb, 31) < doubling(B.pop_england_m[1750], B.pop_england_m[1780], 30)
    pct("debt 1776 / 1700", B.total_debt_gbp_m[1776] / B.total_debt_gbp_m[1700], 9.7)
    pct("GDP per head +22.8%", 100 * (B.gb_real_gdp_pc_2013gbp[1776] / B.gb_real_gdp_pc_2013gbp[1700] - 1), 22.8)
    # Bank of Scotland (Rockoff Table 1)
    t53, t64 = F["rk_t1753"], F["rk_t1764"]
    chk("1753: notes 64, deposits 31 (thousand)", t53[1:3], [64, 31])
    chk("1764: notes 163, deposits 102", t64[1:3], [163, 102])
    pct("    notes x", t64[1] / t53[1], 2.55, 2)
    assert t64[1] / t53[1] > F["rk_bos2"][0]
    pct("    deposits x", t64[2] / t53[2], 3.29, 2)
    assert abs(t64[2] / t53[2] - F["rk_bos2"][2]) < 0.05
    pct("    notes: log rate (%)", 100 * growth_rate(t53[1], t64[1], 11), F["rk_bos2"][1])
    pct("        compound (%)", 100 * growth_rate(t53[1], t64[1], 11, compound=True), 8.9)
    pct("    deposits: log rate (%)", 100 * growth_rate(t53[2], t64[2], 11), F["rk_bos2"][3])
    pct("        compound (%)", 100 * growth_rate(t53[2], t64[2], 11, compound=True), 11.4)
    chk("Small Note Mania 1763 and 1764", F["rk_zenith"], [1763, 1764])
    chk("Seven Years' War 1754-1763", F["rk_seven"], [1754, 1763])


def deeper(F):
    chk("first edition: a hundred and forty five millions", F["e1_145"][0], F["wn_145"][0])
    chk("    pp. 375-377: one half per cent", F["e1_commission"][0], 0.5)
    chk("the 14% note", F["wn_14pct"][2], 14)
    chk("June 22 and June 25", [F["rk_june22"][0], F["rk_june25"][0]], [22, 25])
    pa, _ = qing()
    chk("(2 x 10,000 + 559) x 10,000 + 1,017", (2 * 10_000 + 559) * 10_000 + 1_017, pa)
    chk("    = 205,591,017", pa, 205_591_017)
    chk("Rockoff: 8.5 and 10.8 are log rates",
        round(100 * growth_rate(F["rk_t1753"][1], F["rk_t1764"][1], 11), 1), F["rk_bos2"][1])


def takeaways_and_selfcheck(F, Y, B):
    chk("TA1: 4,800 = 240 x 20", F["wn_4800"][0], 240 * 20)
    chk("    200 tons: 50 waggons, 100 men, 400 horses", F["wn_fifty"], [50, 100, 400])
    pct("TA2: debt 1,410 万 -> 1.366 亿", B.total_debt_gbp_m[1776] / 100, 1.366, 3)
    pct("TA3: 0.27 to 1.60", 100 * saving(1 / 30, 1 / 5, PROFIT), 0.27, 2)
    chk("TA4: profits 6 to 10%", F["wn_profits"], [6, 10])
    chk("TA5: 1769, 40%, 800,000 at 5%, 600,000", [Y["rk_opens"], F["rk_size"][4], F["wn_800k"][0], F["wn_600k"][0]],
        [1769, 40, 800_000, 600_000])
    # self-check
    s = SC1
    chk("SC1 productivity", s["Y"] / s["L"], 200)
    chk("    per head", s["Y"] / s["N"], 90)
    chk("    = 200 x 0.45", 200 * s["L"] / s["N"], 90)
    chk("    500 万: per head", 200 * s["L2"] / s["N"], 100)
    pct("    +%", 100 * (100 / 90 - 1), 11.1)
    s = SC2
    chk("SC2 waggons", s["tons"] / F["wn_waggon"][3], 50)
    chk("    men", s["tons"] / F["wn_waggon"][3] * F["wn_waggon"][0], 100)
    pct("    6 vs 8 men (%)", 100 * (1 - s["ship2"] / s["ship"]), 25, 0)
    chk("    100 - 6", 100 - s["ship2"], 94)
    s = SC3
    pct("SC3 (%)", 100 * saving(s["M"] / s["Y"], s["rho"], s["r"]), 0.6)
    chk("    万 pounds", saving(s["M"] / s["Y"], s["rho"], s["r"]) * s["Y"] / 1e4, 36)
    s = SC4
    X = reflux(s["Nbar"], s["R"], s["N"])
    chk("SC4 rho", X["rho"], 0.2)
    chk("    R", X["needed"], 22_000)
    chk("    naive", X["naive"], 14_000)
    chk("    more", X["needed"] - X["naive"], 8_000)
    s = SC5
    pct("SC5 c (%)", 100 * redraw(s["i"], s["n"], s["k"]), 8, 0)
    s = SC6
    chk("SC6 income", s["loans"] * s["rate"], 50_000)
    chk("    cost", s["borrowed"] * s["cost"], 49_000)
    chk("    net", s["loans"] * s["rate"] - s["borrowed"] * s["cost"], 1_000)
    chk("    share", s["borrowed"] / s["loans"], 0.7)
    chk("    loss on the borrowed part", s["borrowed"] * (s["cost"] - s["rate"]), 14_000)
    chk("    gain on the notes", s["notes"] * s["rate"], 15_000)


def main():
    df = _rows()
    F, Y, B = facts(), years(), boe()
    check_readings(df)
    check_text(df)
    opening(F, Y)
    world(F, Y, B)
    division(F)
    capital(F, B)
    paper(F, Y)
    realbills(F)
    ayr_bank(F, Y)
    regulation(F, Y)
    states(F, Y, B)
    test(F, Y, B)
    deeper(F)
    takeaways_and_selfcheck(F, Y, B)
    print("all Chapter 18 checks passed")


if __name__ == "__main__":
    main()
