"""Chapter 20 (萨伊定律与普遍过剩之争): every number and every quotation in zh/ch20_say.tex.

    python3 checks/check_ch20.py

Inputs:
  say_facts                            quotations of Say (1803, the first edition, and 1821, Prinsep's translation of
                                       the fourth), Say's Letters to Malthus (1821), Malthus (1820), Ricardo (1817, the
                                       first edition, and his letters to Malthus), Sismondi (1819), Walras (1874), Lange
                                       (1942), J. S. Mill (1844), Tooke (1838, vol. II), English (1827, with his table of
                                       the foreign loans read on the page image), Reinhart and Rogoff (2008) and Baumol
                                       (1999) (checked by data/fetch/verify_web_quotes.py)
  boe_millennium_gb_1815_1830          Bank of England, A Millennium of Macroeconomic Data: real GDP by sector, nominal
                                       GDP and the GDP deflator of Great Britain, and the output of the eight key
                                       industries of Broadberry et al. (2015), 1815-1830
  boe_millennium_gb_1822_1827_monthly  the same workbook: the share price indices of Gayer, Rostow and Schwartz, Bank
                                       Rate, the rate on three-month prime bills, the yield on 3% consols (Odlyzko 2014)
                                       and the wholesale price index, monthly, 1822-1827
  bullion_facts                        Cannan (1919) on the usury laws (row cn_usury5; Chapter 19's snapshot)
  smith_facts                          Smith (1776): a nation is not liable to a merchant's accident (row wn_nation;
                                       Chapter 18's snapshot)
The figure module figsrc/fig_ch20.py imports the functions defined here.

What is checked here:
  1. readings   every number of the value column of say_facts is read from its quotation: digits, English and
                French number words, fractions, Roman chapter numbers and the OCR's misreadings; the rows of English's
                table of loans and of Tooke's table of bankruptcies are read field by field
  2. the text   every “…” in the chapter is the chapter's Chinese rendering of a quotation (TRANSLATIONS:
                rendering -> row or rows) or a term of the text (ALLOW)
  3. numbers    every number of the text, section by section, with quoted()

Models (the chapter's key equations):
    Say's identity   sum_{i<n} p_i (D_i - S_i) == 0, from sum_i p_i d_ih = sum_i p_i s_ih for every h    (eq:say-identity)
    Walras' law      sum_{i<=n} p_i (D_i - S_i) == 0, so p_n (D_n - S_n) == 0 under Say's identity       (eq:say-walras)
    current yield    y = 100 c / P,  y ~ i + lambda (a loan lost on default, a default rate lambda)  (eq:say-yield)
    deflator         ln(nominal) = ln(real) + ln(deflator)                                       (eq:accounts-deflator)
"""
from __future__ import annotations

import math
import re

import pandas as pd

from common import ROOT, load_snapshot, quoted

TEX = ROOT / "zh" / "ch20_say.tex"
WAN = 1e4                                  # 万
YI = 1e8                                   # 亿

# Teaching inputs stated in the text
WALRAS = dict(price=0.5, demand=1000, supply=800)          # ex:say-walras (1): oats demanded and supplied, hl
GOODS = dict(sell=1000, buy=960)                           # ex:say-walras (2): cloth and corn, by value
MONEY = dict(stock=400, wanted=440, fall=0.03)             # ex:say-walras (3)
SPLIT = dict(cloth=-25, corn=-15)                          # fig:say_walras (b): the split of the -40 is assumed
CALL = 5                                                   # ex:say-leverage (2): a further call of £5 a share
YEARS = 3                                                  # ex:say-yield (3)
# self-check questions
SC1 = dict(last=10, made=10, sold=8, demand=8)             # 万顶
SC2 = dict(price=1 / 3, demand=300, d=900, s=600)
SC3 = dict(sell=2000, buy=1900, money=500)
SC4 = dict(c=6, P=80, r=3.5, years=5)
SC5 = dict(paid=10, premium=30, later=5)
SC6 = dict(nominal=-0.10, deflator=-0.07)


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
    df, meta = load_snapshot("say_facts", dtype=str, keep_default_na=False)
    assert 20 in meta["used_in"]
    assert df["id"].is_unique
    return df


def meta() -> dict:
    return load_snapshot("say_facts")[1]


def num(x: str) -> float:
    """'5', '1/2', '82+1/2'."""
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
    q = {r.id: r.quote for r in _rows().itertuples()}
    df, m = load_snapshot("smith_facts", dtype=str, keep_default_na=False)   # Chapter 18's snapshot
    assert 20 in m["used_in"]
    q["wn_nation"] = df.set_index("id").loc["wn_nation", "quote"]
    return q


def column(name: str) -> dict[str, str]:
    return {r.id: getattr(r, name) for r in _rows().itertuples()}


def annual() -> pd.DataFrame:
    df, m = load_snapshot("boe_millennium_gb_1815_1830")
    assert 20 in m["used_in"]
    return df.set_index("year")


def monthly() -> pd.DataFrame:
    df, m = load_snapshot("boe_millennium_gb_1822_1827_monthly")
    assert 20 in m["used_in"]
    df["t"] = df.year + (df.month - 1) / 12
    return df.set_index(["year", "month"])


def usury() -> float:
    """Cannan: the usury laws forbade interest above 5 per cent (Chapter 19's snapshot)."""
    df, m = load_snapshot("bullion_facts", dtype=str, keep_default_na=False)
    assert 20 in m["used_in"]
    return float(df.set_index("id").loc["cn_usury5", "value"])


# ---------------------------------------------------------------------------------------------------
# The arithmetic of the chapter
def change(s: pd.Series, a, b) -> float:
    """Per cent change from a to b."""
    return 100 * (s[b] / s[a] - 1)


SECTORS = [("real_agriculture", "农业", "agriculture"), ("real_industry", "工业", "industry"),
           ("real_services", "服务业", "services")]
INDUSTRIES = [("ind_textiles", "纺织品", "textiles"), ("ind_leather", "皮革", "leather"), ("ind_iron", "铁", "iron"),
              ("ind_tin", "锡", "tin"), ("ind_coal", "煤", "coal"), ("ind_foodstuffs", "食品", "foodstuffs"),
              ("ind_construction", "建筑", "construction"), ("ind_books", "印刷的书", "printed books")]


def decomp(nominal: float, real: float) -> dict:
    """eq:accounts-deflator in logs: the fall of nominal GDP and the share of it that is the fall of prices."""
    n, r = math.log(1 + nominal), math.log(1 + real)
    return dict(n=n, r=r, p=n - r, share=(n - r) / n)


def consol_mean(Mo: pd.DataFrame, year: int) -> float:
    """The yearly mean of the monthly consol yields (Odlyzko's weekly data averaged by month)."""
    v = Mo.loc[year, "consol_yield"]
    assert len(v) == 12 and v.notna().all(), year
    return float(v.mean())


# English's table of foreign loans (p. 42), in its order, with the borrower's row of Reinhart and Rogoff's Table 3
LOANS = [("en_l24_austria", "奥地利", "Austria", "rr_t3_austria"), ("en_l24_brazil", "巴西", "Brazil", "rr_t3_brazil"),
         ("en_l24_portugal", "葡萄牙", "Portugal", "rr_t3_portugal"), ("en_l24_greece", "希腊", "Greece", "rr_t3_greece"),
         ("en_l24_colombia", "哥伦比亚", "Colombia", "rr_t3_colombia"),
         ("en_l24_buenosaires", "布宜诺斯艾利斯", "Buenos Aires", "rr_t3_argentina"),
         ("en_l24_mexico", "墨西哥", "Mexico", "rr_t3_mexico"), ("en_l24_peru", "秘鲁", "Peru", "rr_t3_peru"),
         ("en_l24_naples", "那不勒斯", "Naples", None), ("en_l25_brazil", "巴西", "Brazil", "rr_t3_brazil"),
         ("en_l25_mexico", "墨西哥", "Mexico", "rr_t3_mexico"), ("en_l25_greece", "希腊", "Greece", "rr_t3_greece"),
         ("en_l25_denmark", "丹麦", "Denmark", None), ("en_l25_peru", "秘鲁", "Peru", "rr_t3_peru"),
         ("en_l25_guatemala", "危地马拉", "Guatemala", "rr_t3_guatemala")]
LATIN = {"rr_t3_brazil", "rr_t3_colombia", "rr_t3_argentina", "rr_t3_mexico", "rr_t3_peru", "rr_t3_guatemala"}


def coupon(row_id: str, Q: dict[str, str], prev: int | None) -> int:
    """The coupon in the first field of English's row: '5 per cent', or 'ditto' for the coupon of the row above."""
    head = Q[row_id].split("|")[0]
    m = re.search(r"(\d) per cent", head)
    if m:
        return int(m.group(1))
    assert "ditto" in head and prev is not None, row_id
    return prev


def rr_defaults(rid: str, F, U) -> list[int]:
    """The years of default in a row of Table 3 (without the year of independence where the row gives one)."""
    v = [int(x) for x in F[rid]]
    return v[1:] if U[rid].startswith("year of independence") else v


def first_default(rid: str | None, F, U) -> int | None:
    """The first default in the column 1825-1849 of Table 3; None if the row has none there or is not in the table."""
    if rid is None:
        return None
    d = [y for y in rr_defaults(rid, F, U) if 1825 <= y <= 1849]
    return min(d) if d else None


def loans() -> pd.DataFrame:
    """The fifteen loans of 1824 and 1825: coupon, nominal (£), price (per £100), paid (£), current yield and spread (%),
    and the first default of 1825-1849."""
    F, Q, Y, U = facts(), quotes(), years(), column("unit")
    Mo = monthly()
    rows, prev = [], {}
    for rid, zh, en, rr in LOANS:
        y = Y[rid]
        c = coupon(rid, Q, prev.get(y))
        prev[y] = c
        nominal, price, paid = F[rid]
        cy = 100 * c / price
        rows.append(dict(id=rid, year=y, zh=zh, en=en, rr=rr, coupon=c, nominal=nominal, price=price, paid=paid, cy=cy,
                         spread=cy - consol_mean(Mo, y), default=first_default(rr, F, U), latin=rr in LATIN))
    return pd.DataFrame(rows)


def defaulted_share(L: pd.DataFrame, year: int) -> float:
    """Per cent of the money paid that went to borrowers in default by the end of `year`."""
    d = L.default.fillna(9999) <= year
    return 100 * L.paid[d].sum() / L.paid.sum()


def interest(L: pd.DataFrame) -> pd.Series:
    """£ a year: coupon x nominal capital."""
    return L.coupon / 100 * L.nominal


def survival(lam: float, t: int) -> float:
    return (1 - lam) ** t


# ---------------------------------------------------------------------------------------------------
# 1. Readings of the numbers
WORDS = {"a": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
         "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
         "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
SCALE = {"thousand": 1e3, "million": 1e6, "millions": 1e6}
DENOM = {"half": 2}
FR = {"un": 1, "deux": 2, "dix": 10, "vingt": 20, "quatrevingt": 80}
FR_SCALE = {"mille": 1e3, "millions": 1e6}
FR_DENOM = {"quart": 4, "tiers": 3}
ROMAN = {"XV": 15}
OCR = {"SlXII": 22}                        # Say (1803): the chapter number XXII


def _words(s: str) -> list[str]:
    return s.lower().replace("-", " ").split()


def cardinal(s: str) -> float:
    """An English cardinal ('sixty-three', 'four thousand one hundred and eighteen'); a unit word after it ends it."""
    total, cur, seen = 0.0, 0.0, False
    for w in _words(s):
        if w in WORDS:
            cur += WORDS[w]
        elif w == "hundred":
            cur = (cur or 1) * 100
        elif w in SCALE:
            total += (cur or 1) * SCALE[w]
            cur = 0
        elif w == "and" and seen:
            continue
        else:
            break
        seen = True
    assert seen, s
    return total + cur


def cardinal_fr(s: str) -> float:
    """A French cardinal: 'cent mille', 'cent dix mille', 'quatrevingt-dix mille', 'deux millions'."""
    total, cur = 0.0, 0.0
    for w in _words(s):
        if w in FR:
            cur += FR[w]
        elif w == "cent":
            cur = (cur or 1) * 100
        elif w in FR_SCALE:
            total += (cur or 1) * FR_SCALE[w]
            cur = 0
        else:
            raise ValueError(s)
    return total + cur


def fraction(s: str) -> float:
    """'one half' (English) or 'un quart', 'un tiers' (French)."""
    a, b = _words(s)
    if b in DENOM:
        return WORDS[a] / DENOM[b]
    return FR[a] / FR_DENOM[b]


def figure(s: str) -> float:
    return float(s.replace(",", "").replace("£", ""))


def read(phrase: str, how: str) -> list[float]:
    if how == "num":
        return [figure(phrase)]
    if how == "en":
        return [cardinal(phrase)]
    if how == "fr":
        return [cardinal_fr(phrase)]
    if how == "frac":
        return [fraction(phrase)]
    if how == "roman":
        return [ROMAN[phrase]]
    if how == "ocr":
        return [OCR[phrase]]
    if how == "space":                        # '102,781 ,600': the OCR's space before a comma
        return [figure(phrase.replace(" ", ""))]
    if how == "point":                        # '12.869,571': the page's raised point for a comma
        return [figure(phrase.replace(".", ","))]
    raise ValueError(how)


def loan_fields(quote: str) -> list[float]:
    """A row of English's table: 'Austria, 5 per cent | 3,500,000 | 82 1/2 | 2,887,500'."""
    out = []
    for f in quote.split("|")[1:]:
        f = f.strip()
        if " " in f:
            a, b = f.split()
            out.append(figure(a) + num(b))
        else:
            out.append(figure(f))
    return out


FIGURES = re.compile(r"\d[\d,]*(?:\.\d+)?")
TABLE = re.compile(r"\d+")
EN, FRW = "en", "fr"
# id -> [(phrase in the quotation, how it is read)], in order. Rows not listed are read with all the figures of the
# quotation; English's loans (en_l24_*, en_l25_*) field by field; Tooke's tables (tk2_comm*) with every number that
# stands alone (the years end with a comma, the dashes are rules).
READINGS = {
    "sy03_title": [("SlXII", "ocr")],
    "sy03_cent": [("cent mille", FRW)],
    "sy21_title": [("XV", "roman")],
    "sy21_glut": [("two", EN)],
    "ml_mill": [("1808", "num"), ("one half", "frac")],
    "rp_chest": [("ten thousand", EN), ("100,000", "num")],
    "sm_hats": [("cent mille", FRW), ("1817", "num"), ("cent dix mille", FRW), ("1818", "num")],
    "sm_sold": [("cent mille", FRW), ("quatrevingt-dix mille", FRW)],
    "sm_quart": [("un quart", "frac"), ("un tiers", "frac")],
    "tk2_eight": [("100", "num"), ("5", "num"), ("40", "num"), ("eight", EN)],
    "tk2_height": [("four", EN), ("1825", "num")],
    "tk2_seventy": [("seventy", EN), ("1825", "num")],
    "tk2_ridley": [("1825", "num"), ("1826", "num"), ("770", "num"), ("sixty-three", EN)],
    "en_624": [("six hundred and twenty-four", EN), ("1824", "num"), ("1825", "num"), ("372,173,100", "num")],
    "en_existing": [("102,781 ,600", "space")],
    "en_l25_total": [("12.869,571", "point"), ("9,944,218", "num")],
    "tk2_resumed": [("sixty-three", EN), ("twenty-three", EN), ("20", "num")],
    "tk2_bkr1821": [("1821", "num"), ("four thousand one hundred and eighteen", EN), ("1816", "num"),
                    ("six thousand six hundred and twenty-seven", EN), ("1812", "num"),
                    ("seven thousand and forty- two", EN)],
    "tk2_cb1821": [("1819", "num"), ("1820", "num"), ("1821", "num"), ("twenty-seven", EN), ("thirteen", EN),
                   ("four", EN), ("ten", EN), ("1816", "num")],
    "sm_perdu": [("cent mille", FRW), ("1817", "num"), ("dix mille", FRW)],
    "sm_vingt": [("vingt", FRW), ("deux millions", FRW)],
    "sm_dixmille": [("dix mille", FRW)],
    "sm_gagne": [("1818", "num"), ("cent dix mille", FRW), ("cent mille", FRW)],
    "tk2_run": [("three", EN), ("four", EN)],
    "tk2_thirtyone": [("thirty-one", EN)],
    "tk2_ceased": [("one pound", EN)],
    "tk2_chasm": [("one pound", EN)],
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
                k = quote.find(phrase, pos)
                assert k >= 0, f"{r.id}: {phrase!r} not found (in order) in the quotation"
                pos = k + len(phrase)
                got += read(phrase, how)
        elif r.id.startswith(("en_l24_", "en_l25_")) and r.id not in ("en_l24_total", "en_l25_total"):
            got = loan_fields(quote)
        elif r.id.startswith("tk2_comm"):
            got = [float(t) for t in quote.split() if TABLE.fullmatch(t)]
        else:
            got = [figure(x) for x in FIGURES.findall(quote)]
        assert [round(g, 9) for g in got] == [round(v, 9) for v in vals], f"{r.id}: read {got}, value column {vals}"
        n += 1
    quoted("rows with values, each read from its quotation", n, 86)


# ---------------------------------------------------------------------------------------------------
# 2. Every “…” of the text against the snapshot
# terms of the text, which are not quotations
ALLOW = {"什么都卖不出去", "普遍过剩", "千年宏观数据", "无", "—", "过剩"}
# the chapter's Chinese renderings of the quotations: rendering -> row (or rows)
TRANSLATIONS = {
    # added after the independent review
    "相对令人满意": "tk2_workers",
    "劳动的价格远没有按必需品价格下跌的比例下跌": "tk2_workers",
    "绝大多数劳动人口的处境改善了": "tk2_bulk",
    "确实有工人因为许多行业的萧条而失业的抱怨": "tk2_outofemploy",
    "造成了暂时的过剩": "tk2_outofemploy",
    "一个商人仓库里货物很多，有时会因为不能及时卖掉而破产，一个国家却不会遭遇同样的意外": "wn_nation",
    "普遍的供给过剩固然必然只是暂时的，但这对每一种局部的供给过剩也同样可以这样说。": "jm_partial",
    "为了得到比本国公债高得多的利息": "tk2_hazard",
    "那个关键时期商人与银行家的困苦大大加重，从中可以清楚地看出高利贷法的作用": "tk2_usurylaw",
    "货物卖不出去了，消费者眼前迫切需要的除外": "tk2_unsaleable",
    "终于引来了足够的黄金，使英格兰银行脱离了眼前的危险": "tk2_influx",
    "其他谷物与豆类都受了旱灾，大大不足": "tk2_drought",
    "在制造业人口困苦的状况下，这是一个高价": "tk2_april60",
    "越来越响，在一些工业区演变成暴力行为": "tk2_violence",
    "智利与大哥伦比亚（包括今天的哥伦比亚、厄瓜多尔与委内瑞拉）在同一年晚些时候违约": "rr_t8_granc",
    # opening
    "全世界的市场普遍过剩，商品不断运去，只能亏本出售，原因是什么？": "sl_cause",
    "尤其是制造业大国英国的商品，充斥意大利的每一个市场": "sm_italie",
    "不得不亏掉四分之一或三分之一把它们卖掉，而不是赚钱": "sm_quart",
    "商业的洪流被意大利挡回来，就涌向德意志、俄国、巴西，很快又在那里遇到同样的障碍。": "sm_torrent",
    "所有的仓库都堆满了欧洲的商品，售价比欧洲还低，也卖不出去": "sm_cap",
    "布宜诺斯艾利斯、新格拉纳达、智利，也都已经堆满了商品": "sm_buenos",
    "如果某些商品卖不出去，那是因为别的商品没有生产出来；只有生产才为产品打开市场。": "sl_alone",
    "相反，您断言，各种商品可以同时过剩。": "sl_assert",
    # sec:say-world
    "从 1814 年到 1816 年，几乎一切产品的价格、一切固定财产的价值普遍下跌，农业、商业、制造业、采矿业、航运业与建筑业一起"
    "遭受损失、一起破产，使那个时期成为苦难与困窘最为普遍的时期之一。": "tk2_suffering",
    "主要是乡村银行家": "tk2_bankers",
    "从来没有在任何一个国家发生过比这个国家更大、更突然的收缩": "tk2_horner",
    "只有法国在密西西比计划以后与指券被毁以后的那两次是例外": "tk2_mississippi",
    "其规模之大，本来会被认为不可能不带来比实际更多的破产": "tk2_ruin",
    "一场范围与持续时间都非同寻常的战争结束以后的困苦，欧洲各国都或轻或重地感受到了。": "tk2_regent",
    "将近三倍": "tk2_cb1821",
    "1818 年年底的普遍停滞": "tk2_stag1818",
    "近几年欧洲经历的商业危机，制造业工人所受的残酷痛苦": "sm_crise",
    # sec:say-law
    "产品用产品购买": ("sy03_produits", "rp_productions"),
    "使销路通畅的，与其说是货币的充裕，不如说是其他产品的普遍充裕。这是政治经济学最重要的真理之一。": "sy03_truth",
    "在这双重的交换里，货币只起一时的作用": "sy03_passager",
    "人们发现，是用产品支付了产品": "sy03_produits",
    "一个国家某一类产品太多的时候，使它们卖得出去的办法，是创造另一类产品": "sy03_genre",
    "对十万个也成立": "sy03_cent",
    "一种产品一旦造出来，从那一刻起，就为其他产品提供了一个与它自身价值相等的市场。": "sy21_nosooner",
    "因为货币的价值也会消失": "sy21_perishable",
    "最终的目的也总是用它购买某种东西": "sy21_hoard",
    "说买卖清淡是因为货币稀缺，就是把手段当成了原因": "sy21_means",
    "是因为它超过了对它的全部需求，有两种情形：要么它生产得太多，要么别的商品生产得太少": "sy21_glut",
    "人们买得少了，是因为赚得少了": "sy21_less",
    "正当一种商品亏损的时候，另一种商品正赚着过高的利润": "sy21_excessive",
    "殖民地产品、小麦与别的一些东西的高价，与许多找不到有利销路的东西的低价同时并存": "sy21_colonial",
    "某种暴力手段，或某种非常的原因，政治的或自然的动乱，或当局的贪婪与无知": "sy21_convulsion",
    "如果完全听任生产自行其是，一种产品就很少会超过其他产品，它的价格也很少会不成比例地下跌。": "sy21_itself",
    "不但对农民有利，对一切商品的经销商也都有利": "sy21_harvest",
    "一个制造业或商业部门的停滞，会在其他所有部门感受到": "sy21_felt",
    "我并不想在这一章里主张，一种产品不可能相对于其他一切产品生产得太多": "sy21_notmaintain",
    "生产力过高": "sy21_sismondi",
    "只证明了那些被英国制成品充斥的国家生产的无力": "sy21_feeble",
    "如果巴西生产出足够的东西来购买运到那里的英国货，这些货物就不会充斥她的市场。": "sy21_brazil",
    "穆勒先生在 1808 年发表的对 Spence 先生的答复里，非常明确地提出了这样的学说：商品只能用商品购买，其中的一半必定为另一半"
    "提供市场": "ml_mill",
    "萨伊先生已经极为令人满意地证明，一个国家不论有多少资本，都不会用不出去，因为需求只受生产的限制。": "rp_say",
    "没有人生产不是为了消费或出售，没有人出售不是为了购买别的商品。": "rp_noman",
    "如果把一万英镑给一个年收入十万英镑的人，他不会把它锁在箱子里": "rp_chest",
    "产品总是用产品购买的，货币只是完成交换的媒介。": "rp_productions",
    "可能生产得太多，在市场上过剩到收不回投入的资本；但对所有商品来说，这种情形不可能发生": "rp_particular",
    "在一个国家里，不可能积累起用不出去的资本，除非必需品价格上涨，工资随之涨得那么高，留给资本利润的那么少，以致积累的动机"
    "消失。": "rp_wages",
    "如果每个人都放弃奢侈品的享用，一心只求积累，那就可能生产出一批无法立即消费的必需品。对于种类这样有限的商品，无疑可能出现"
    "普遍的过剩。": "rp_universal",
    "如果人们不再消费，他们也就不再生产。这个让步并不损害一般的原理。": ("rp_cease", "rp_admission"),
    "没有人出售不是为了购买": "rp_noman",
    # sec:say-glut
    "每一个节俭的人都是公众的恩人": "ml_smith",
    "在很大程度上无疑是对的": "ml_true",
    "储蓄的原则推到极端，会毁掉生产的动机": "ml_excess",
    "最简单的食物、最差的衣服与最简陋的房屋": "ml_simplest",
    "积累与生产的动机必定因为缺乏消费的意愿而消失": "ml_wantwill",
    "必定有某个中间点，虽然政治经济学的手段也许还确定不了它": "ml_point",
    "生产的能力与消费的意愿": "ml_powerwill",
    "有人断言，有效需求不过是用一种商品交换另一种商品。": "ml_effectual",
    "完全没有根据": "ml_unfounded",
    "大量的商品是直接与劳动交换的，无论是生产性的还是非生产性的劳动": "ml_labour",
    "商品相对于劳动必定贬值，使利润降到几乎为零，并暂时阻止进一步的生产": "ml_profits",
    "这正是过剩一词的含义，而在这种情形下，过剩显然是普遍的，而不是局部的。": "ml_general",
    "许多数学符号或算术记号": "ml_figures",
    "一个国家的年产品超过它的年消费，就说它增加了资本": "rp_capital",
    "怎么！里昂的帽子工场 1817 年做了十万顶帽子，1818 年做了十一万顶，或者 1818 年也做了十万顶、却只卖掉九万顶，两种情形都"
    "同样是繁荣的标志吗？": ("sm_quoi", "sm_hats", "sm_sold"),
    "又有一万顶卖不出去，那肯定是亏了": "sm_perdu",
    "每顶卖二十法郎，只卖给城里的消费者，这就是两百万": "sm_vingt",
    "这种生产不是按需求，而是按人们想要投入的资本来调整的": "sm_demand",
    "没有一座城市、没有一个小镇，摆出来卖的商品不是远远超过买主的财力": "sm_fearon",
    "没有一个事实，比消费的手段与生产的手段之间的不成比例，在更多的地方、以更多的面目出现在我们面前": "sm_disproportion",
    "他们的队伍只有靠破产才会变得稀疏": "sm_faillites",
    "哲学家们怎么就不愿意看见这到处都让普通人一眼就看到的东西呢？": "sm_philosophes",
    "年生产与收入是同一个东西": "sm_revenu",
    "李嘉图先生追随萨伊先生，重复并肯定了这一点": "sm_ricardo",
    "按照这一原则，就根本不可能理解或解释商业史上最确凿的事实，即市场的壅塞。": "sm_engorgement",
    "不成比例": "sm_disproportion",
    "一个部门过剩是因为别的部门不足": ("sy21_glut", "sl_several"),
    # sec:say-debate
    "我们也同意，有效需求由两个要素构成，购买的能力与购买的意愿；但我认为，有能力的地方很少缺少意愿。": "rl_will",
    "真正的补救办法肯定在于调整今后的生产；如果一种商品过剩，就少生产它，多生产另一种。": "rl_remedy",
    "人们怀着偏见、固执地坚持原来的行业；他们天天盼着情况好转，于是继续生产没有足够需求的商品": "rl_obstinacy",
    "人们在生产上犯了错；需求并不缺少。": "rl_err",
    "对我们两个都是很大的蠢事": "rl_velvets",
    "我们现在就在犯这样的蠢事，我简直无法解释这种错觉为什么持续这么久": "rl_delusion",
    "我无法想象，除非出现最严重的误算，资本与劳动会同时过剩。": "rl_redundancy",
    "我认为，在一段时间里没有进一步增加生产的动机，用停滞这个词来形容这样的状态并不恰当。": "rl_stagnation",
    "如果我像您那样认为我们现在苦于储蓄太多，我不会反对把增加消费当作贸易停滞的补救办法。": "rl_savings",
    "真正的消费者，只有那些自己也生产的人，因为只有他们才能购买别人的产品": "sl_consumers",
    "使一个国家不同于一片荒漠的，正是生产的能力": "sl_desert",
    "每当几种商品同时过剩的时候，那是因为别的商品生产得不够，不足以与前者交换。": "sl_several",
    "我很乐意在这里引用他最有力的说法，以免使您失去任何一点优势": "sl_strongest",
    # sec:say-walras
    "就等于说供给 100 百升小麦": "wl_avoine",
    "就等于说需求 75 百升小麦": "wl_150",
    "人们供给，只是因为不供给就不能需求；一句话，供给不过是需求的结果": "wl_offre",
    "如果燕麦的有效需求与有效供给相等，小麦的有效供给与有效需求也相等": "wl_sachons",
    "按同样的比例": "wl_proportion",
    "其中的一种，比如第 $n$ 种，充当交换的媒介": "lg_nth",
    "我提议把这个恒等式叫作瓦尔拉斯定律，因为瓦尔拉斯第一个认识到它在价格的数学理论中的根本重要性。": "lg_walras",
    "并不要求每一种商品、或其中任何一种商品的需求与供给处于均衡": "lg_each",
    "在没有统一的交换媒介、即没有货币的体系里，瓦尔拉斯定律也成立": "lg_moneyless",
    "不可能出现商品总供给的过剩（普遍的供给过剩）": "lg_def",
    "因为一切商品的总供给恒等于一切商品的总需求": "lg_because",
    "对现金余额的总需求恒等于现有的货币量": "lg_cash",
    "萨伊定律排除了任何货币理论。": "lg_precludes",
    "维克塞尔，以及与他一起的所有货币理论家，就这样放弃了萨伊定律：他们用一个只在均衡时成立的方程代替了恒等式。": "lg_equation",
    "写于 1829 年与 1830 年": "jm_written",
    "显然建立在物物交换的假设上；在这个假设下，它是完全无可争辩的": "jm_barter",
    "使这一次交换可以分成两个独立的行为或操作，一个可以现在做，另一个可以一年以后做": "jm_twoacts",
    "货币只起一时的作用": ("sy03_passager", "sy21_momentary"),
    "一时": ("sy03_passager", "sy21_momentary"),
    "普遍地想尽快卖出，同时普遍地想尽可能推迟一切购买": "jm_inclination",
    "不是非卖不可的人觉得停滞，非卖不可的人陷入困境": "jm_distress",
    "货币本身必须被当作一种商品。无疑必须承认，不可能一切其他商品过剩，同时货币也过剩": "jm_commodity",
    "认为不是货币过多，而是流通手段不足": "jm_deficiency",
    "是一切商品相对于货币的过剩": "jm_relatively",
    "人们普遍预期会突然被要求付款，在那个时候宁愿持有货币，而不愿持有任何别的商品": "jm_sudden",
    "极端的情形下，货币被大量地收集起来窖藏；温和的情形下，人们只是推迟付出货币": "jm_hoarded",
    "一切商品的过剩，在唯一可能的意义上，只是指它们相对于货币的价值暂时下跌": "jm_temporary",
    "相对于它们自己贬值": "jm_themselves",
    "只能是暂时的，而且必定被同样剧烈的反向变动接替": "jm_onlytemporary",
    "普遍急于购买与普遍不愿购买，交替出现": "jm_eagerness",
    "一个国家可能积累资本太快": "jm_toofast",
    "是完全有说服力的": "jm_conclusive",
    "一般商品不可能生产过多": "jm_general",
    "这只是一个命名问题，却是一个重要的命名问题": "jm_naming",
    "供给创造自己的需求": "bm_keynes",
    "并没有说得很准确": "bm_keynes",
    # sec:say-1825
    "1822 年夏天，英格兰银行把贴现率从 5\\% 降到 4\\%。": "tk2_rate",
    "关于墨西哥与南美洲一些主要矿山产量的最夸张的报道被带到公众面前": "tk2_flaming",
    "墨西哥的矿山，这个词让每一个人想象出无穷的财富": "tk2_mexico",
    "需要的资本总额是 372,173,100 英镑": "en_624",
    "只适合个人经营": "en_individual",
    "只能归因于发起人的某种险恶动机": "en_sinister",
    "只图钱财的无耻之徒": "en_unprincipled",
    "只缴一小笔分期款，很少超过 5\\%": "tk2_instalment",
    "比如，面值 100 英镑、已缴 5 英镑的股份，涨到溢价 40 英镑，每一股的利润就相当于已缴金额的八倍。": "tk2_eight",
    "狂热在 1825 年的头四个月达到顶点": "tk2_height",
    "在 1825 年 1 月与 2 月达到最高点以后，先是停顿，然后略有下跌，几周以后，即在随后的 5 月与 6 月，迅速下跌":
        "tk2_greatest",
    "紧迫而急切，收益的前景却变得更遥远、更不确定": "tk2_calls",
    "普遍没有足够的钱缴纳后面的分期款，因为他们大多指望价格继续上涨": "tk2_instalments",
    "这个国家利率的上升，对所有借款都有同样的压低作用": "tk2_ratehere",
    "业务很大，可用的资金却很不充足，所以一旦信用普遍动摇，就可能遭到挤兑": "tk2_london",
    "其中最大的银行之一（波尔公司），在困境中挣扎了一个多星期，于 1825 年 12 月初停止支付": "tk2_pole",
    "伦敦的几家银行遭到严重的挤兑，除了前面说的那一家，又有三四家停止支付": "tk2_run",
    "仅仅在去年（1825 年）12 月一个月里，伦敦与各地就有将近七十家银行停止支付。": "tk2_seventy",
    "英格兰银行券与黄金几乎是全国唯一被接受的支付手段": "tk2_onlymedium",
    "1825 年与 1826 年，乡村银行家有 770 家，其中 63 家停止了支付": "tk2_ridley",
    "有 23 家后来恢复了支付，按每镑 20 先令全额偿还": "tk2_resumed",
    "好几家银行早已资不抵债，只是靠顾客的信任才维持下来": "tk2_insolvent",
    "由于这些原因，为了国内的用途而从英格兰银行提取黄金的数量如此之大，加上此前为出口而提取的黄金，人们怀疑能否继续兑付。"
    "幸运的是，公众逃过了第二次停兑的灾难。": ("tk2_drain", "tk2_suspension"),
    "通过扩大商业票据的贴现，增发了英格兰银行券": "tk2_discounts",
    "一只箱子，里面有大约 60 万或 70 万英镑的 1 英镑银行券": "tk2_box",
    "对黄金的挤兑最严重的时候，似乎在发行的前一周就已经过去": "tk2_severest",
    "近乎奇迹": "tk2_miraculous",
    "极端怎样产生它们的反面": "tk2_extremes",
    "无限的信心与毫无根据的预期带来的一切错觉，被不信任与惊慌取代了。": "tk2_distrust",
    "宁愿持有货币，而不愿持有任何别的商品": ("jm_sudden", "jm_possess"),
    "为了增加准备金而留住的款项": "tk2_reserves",
    "也许比以往任何时候都大": "tk2_contraction",
    # the case of Latin America
    "秘鲁 1826 年违约以后，伦敦的债券持有人马上担心起其他拉丁美洲国家偿债的能力；债券价格崩溃": "rr_t8_peru",
    "到 1828 年，除巴西以外，整个拉丁美洲都违约了": "rr_t8_1828",
    "使认购的款项几乎全部损失": "tk2_loans",
    "除了一两个例外，结果都是所缴资本的全部损失": "tk2_mining",
    "拉丁美洲的许多国家（加上它们的宗主国西班牙）": "rr_1820s",
    "这些违约大多与拉丁美洲的独立战争有关": "rr_wars",
    "对所有借款都有同样的压低作用": "tk2_ratehere",
    # sec:say-test
    "人们在生产上犯了错": "rl_err",
    "只能是暂时的": "jm_onlytemporary",
    "暂时的": ("jm_temporary", "jm_onlytemporary"),
    "原因完全不同": "jm_different",
    "西斯蒙第在这一点上的看法，后来被我们的马尔萨斯采纳，而我们的作者的看法被李嘉图采纳": "sy21_prinsep",
    "将近七十家": "tk2_seventy",
    # sec:say-legacy and the takeaways
    "萨伊的同时代人，包括萨伊本人，没有一个人认为他是最早提出这些原理的人": "bm_first",
    "中间点": "ml_point",
    "宁愿持有货币": ("jm_sudden", "jm_possess"),
    "暂时": "jm_temporary",
    "排除了任何货币理论": "lg_precludes",
}


PUNCT = re.compile(r"[\s，。、；：！？“”‘’（）《》·…—,.;:!?'\"()\[\]|\-]")


def tex_text() -> str:
    return "\n".join(l for l in TEX.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("%"))


def text_quotations() -> list[str]:
    return re.findall(r"“([^”]*)”", tex_text())


def check_text(df: pd.DataFrame) -> None:
    ids = set(df["id"]) | set(quotes())                    # with the row of Chapter 18 (wn_nation)
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
def opening(F, Y, Q):
    chk("Say's letters, 1820", Y["sl_cause"], 1820)
    assert "English translation 1821" in column("year_note")["sl_cause"]
    chk("Sismondi's book, 1819", Y["sm_crise"], 1819)
    chk("    the markets of about 1818", [Y["sm_italie"], Y["sm_torrent"], Y["sm_cap"], Y["sm_buenos"]], [1818] * 4)
    assert column("year_note")["sm_cap"] == "August"                    # the only dated one: 1818 年前后
    assert all(column("year_note")[k].startswith("undated") for k in ("sm_italie", "sm_torrent", "sm_buenos"))
    chk("a quarter or a third", F["sm_quart"], [1 / 4, 1 / 3])
    assert "twentieth century appellation" in Q["bm_coined"]


def world(F, Y, A):
    chk("Tooke: 1814 to 1816", F["tk2_suffering"], [1814, 1816])
    pct("real GDP 1816 (%)", change(A.real_gdp, 1815, 1816), -5.3)
    pct("    industry (%)", change(A.real_industry, 1815, 1816), -6.3)
    pct("    nominal GDP (%)", change(A.nominal_gdp_gbp_m, 1815, 1816), -11.2)
    c10, c14 = F["tk2_comm1810"], F["tk2_comm1814"]
    chk("commissions 1814, 1815, 1816", c14[0:5:2], [1612, 2284, 2731])
    chk("    three years", c14[5], 6627)
    chk("    = sum", c14[0] + c14[2] + c14[4], c14[5])
    chk("    1810-1812", c10[5], 7042)
    chk("    = sum", c10[0] + c10[2] + c10[4], c10[5])
    assert c14[5] < c10[5]
    chk("against bankers 1814-1816", c14[7], 92)
    chk("    = sum", c14[1] + c14[3] + c14[6], c14[7])
    chk("    1810-1812", c10[7], 47)
    chk("    = sum", c10[1] + c10[3] + c10[6], c10[7])
    quoted("    nearly twice", c14[7] / c10[7], 2, tol=0.05)
    YN = column("year_note")
    chk("Horner, 1816", Y["tk2_horner"], 1816)
    assert YN["tk2_horner"] == "speech of 1 May 1816"
    chk("the Prince Regent, 1817", Y["tk2_regent"], 1817)
    assert YN["tk2_regent"] == "speech of 28 Jan. 1817"
    chk("bankruptcies: three years ending 1821, 1816, 1812", F["tk2_bkr1821"], [1821, 4118, 1816, 6627, 1812, 7042])
    chk("    the same totals as the table", [F["tk2_bkr1821"][3], F["tk2_bkr1821"][5]], [c14[5], c10[5]])
    cb = F["tk2_cb1821"]
    chk("country banks 1819, 1820, 1821", cb[4:7], [13, 4, 10])
    chk("    in all", cb[3], 27)
    chk("    = sum", sum(cb[4:7]), cb[3])
    chk("    against the three years ending 1816", cb[7], 1816)
    chk("the stagnation at the close of 1818", F["tk2_stag1818"][0], 1818)
    chk("Sismondi's preface, 1819", Y["sm_crise"], 1819)
    Q = quotes()
    assert "1814 and 1815" in Q["tk2_workers"] and "not fallen" in Q["tk2_workers"]
    assert "1811 and 1812" in Q["tk2_bulk"] and "improved" in Q["tk2_bulk"]
    assert "thrown out of employ" in Q["tk2_outofemploy"] and "army and navy" in Q["tk2_outofemploy"]


def law(F, Y, Q):
    U = column("juan")
    chk("Traité, 1803", Y["sy03_truth"], 1803)
    chk("    book I, ch. XXII", F["sy03_title"][0], 22)
    chk("    a hundred thousand", F["sy03_cent"][0], 100_000)
    assert "fourth edition" in column("year_note")["sy21_title"]
    chk("Prinsep's translation, 1821", Y["sy21_title"], 1821)
    chk("France, 1811-1813", F["sy21_france"], [1811, 1812, 1813])
    chk("two ways", F["sy21_glut"][0], 2)
    chk("James Mill, 1808; one half", F["ml_mill"], [1808, 0.5])
    chk("Ricardo, 1817", Y["rp_say"], 1817)
    assert column("year_note")["rp_say"] == "first edition"
    assert all(U[k] == "ch. XIX" for k in ("rp_say", "rp_noman", "rp_chest", "rp_productions", "rp_particular",
                                           "rp_wages", "rp_universal", "rp_cease", "rp_admission"))
    chk("ten thousand pounds to a man of 100,000 a year", F["rp_chest"], [10_000, 100_000])
    chk("    10,000 more spent, employed or lent", F["rp_either"][0], F["rp_chest"][0])


def glut(F, Y):
    U = column("juan")
    chk("Malthus, 1820", Y["ml_excess"], 1820)
    assert U["ml_excess"].startswith("Introduction")
    assert U["ml_effectual"].startswith("ch. VII, sect. III")
    chk("Sismondi a year before Malthus", Y["ml_excess"] - Y["sm_crise"], 1)
    assert U["rp_capital"].startswith("ch. VII 'On Taxes'")
    Q = quotes()
    assert "to the extent in which it has" in Q["ml_extent"]           # Malthus's qualifier
    assert Q["ml_errors"].startswith("M. Say, Mr. Mill, and Mr. Ricardo") and "fundamental errors" in Q["ml_errors"]
    assert "In the first place" in Q["ml_first"]                        # the first of several errors
    assert "a nation or country is not liable to the same accident" in Q["wn_nation"]
    h = F["sm_hats"]
    chk("hats: 100,000 in 1817, 110,000 in 1818", h, [100_000, 1817, 110_000, 1818])
    chk("    or 100,000 made, 90,000 sold", F["sm_sold"], [100_000, 90_000])
    chk("    10,000 more either way", [h[2] - h[0], F["sm_sold"][0] - F["sm_sold"][1]], [10_000, 10_000])
    chk("the hatter: 110,000 instead of 100,000", F["sm_gagne"], [1818, 110_000, 100_000])
    chk("    100,000 as in 1817, 10,000 unsold", F["sm_perdu"], [100_000, 1817, 10_000])
    # ex:say-hats
    price, value = F["sm_vingt"]
    chk("(0) twenty francs, two millions", [price, value], [20, 2e6])
    chk("    100,000 x 20", h[0] * price, value)
    extra = (h[2] - h[0]) * price
    chk("(1) 10,000 x 20 (万法郎)", extra / WAN, 20)
    made, sold = F["sm_sold"]
    chk("    output (万法郎)", made * price / WAN, 200)
    chk("    consumption (万法郎)", sold * price / WAN, 180)
    chk("    inventories (万法郎)", (made - sold) * price / WAN, 20)
    q, t = F["sm_quart"]
    chk("(2) price at a loss of a quarter", price * (1 - q), 15)
    pct("    of a third", price * (1 - t), 13.33, 2)
    chk("    loss (万法郎)", (made - sold) * price * q / WAN, 5)
    pct("    ", (made - sold) * price * t / WAN, 6.67, 2)
    produce = sold - (made - sold)
    chk("(3) produce (万顶)", produce / WAN, 8)
    chk("    fall from 1818 (%)", 100 * (1 - produce / made), 20)
    chk("    demand against 1817 (%)", 100 * (1 - sold / h[0]), 10)
    assert U["sm_demand"].startswith("tome I, livre IV, ch. IV")
    chk("Fearon's journey ended in the spring of 1818", F["sm_fearontrip"][0], 1818)


def debate(F, Y):
    YN = column("year_note")
    chk("Ricardo's letters: September 1814", Y["rl_will"], 1814)
    assert YN["rl_will"] == "16 Sept. 1814"
    assert YN["rl_remedy"] == "4 Sept. 1820"
    for k in ("rl_obstinacy", "rl_err", "rl_velvets", "rl_delusion", "rl_redundancy"):
        assert YN[k] == "10 Oct. 1820", k
    for k in ("rl_stagnation", "rl_savings"):
        assert YN[k] == "21 July 1821", k
    U = column("juan")
    for k in ("sl_consumers", "sl_desert", "sl_several", "sl_strongest"):
        assert U[k].startswith("Letter I,"), k


def walras(F, Y):
    U = column("juan")
    chk("Walras, 1874", Y["wl_avoine"], 1874)
    chk("200 hl of oats demanded = 100 hl of wheat offered", F["wl_avoine"], [200, 100])
    chk("    at the price ½", F["wl_avoine"][0] * WALRAS["price"], F["wl_avoine"][1])
    chk("150 hl offered = 75 hl demanded", F["wl_150"], [150, 75])
    chk("    at the price ½", F["wl_150"][0] * WALRAS["price"], F["wl_150"][1])
    assert U["wl_avoine"].startswith("§45") and U["wl_150"].startswith("§45")
    chk("Lange, 1942", Y["lg_walras"], 1942)
    # ex:say-walras
    p, d, s = WALRAS["price"], WALRAS["demand"], WALRAS["supply"]
    chk("(1) wheat offered", d * p, 500)
    chk("    wheat demanded", s * p, 400)
    chk("    1,000/800 = 500/400", d / s, (d * p) / (s * p))
    chk("    = 1.25", d / s, 1.25)
    ex_oats, ex_wheat = (d - s) * p, s * p - d * p
    chk("    excess demands in wheat", [ex_oats, ex_wheat], [100, -100])
    chk("    sum", ex_oats + ex_wheat, 0)
    goods = GOODS["buy"] - GOODS["sell"]
    chk("(2) goods", goods, -40)
    chk("    fig:say_walras (b): cloth + corn", SPLIT["cloth"] + SPLIT["corn"], goods)
    chk("    money", -goods, 40)
    k, w, f = MONEY["stock"], MONEY["wanted"], MONEY["fall"]
    pct("(3) prices to 400/440", k / w, 0.909, 3)
    pct("    a fall of (%)", 100 * (1 - k / w), 9.1)
    chk("    1 - 0.03", 1 - f, 0.97)
    pct("    wanted after a fall of 3%", w * (1 - f), 426.8)
    pct("    excess demand left", w * (1 - f) - k, 26.8)
    chk("Mill: written 1829 and 1830", F["jm_written"], [1829, 1830])
    assert "published 1844" in column("year_note")["jm_written"]
    assert all(U[k] == "Essay II" for k in TRANSLATED_MILL)


TRANSLATED_MILL = ["jm_barter", "jm_twoacts", "jm_inclination", "jm_distress", "jm_commodity", "jm_deficiency",
                   "jm_relatively", "jm_sudden", "jm_hoarded", "jm_temporary", "jm_themselves", "jm_onlytemporary",
                   "jm_eagerness", "jm_toofast", "jm_conclusive", "jm_general", "jm_naming", "jm_different"]


def boom(F, Y, Mo, L):
    chk("Tooke: summer of 1822, from 5 to 4 per cent", F["tk2_rate"], [1822, 5, 4])
    Q = quotes()
    assert "close of 1822" in Q["tk2_conversion"] and "early in 1824" in Q["tk2_conversion"]   # two conversions
    assert "income was thus reduced" in Q["tk2_hazard"] and "mode of living" in Q["tk2_hazard"]
    assert "Annual Register for 1824" in Q["tk2_annreg"]
    for k in ("tk2_mexico", "tk2_instalment", "tk2_eight"):        # the Annual Register, in Tooke's footnotes
        assert "Annual Register" in column("year_note")[k] and "footnote" in column("juan")[k]
    chk("Bank Rate: 5 in May 1822, 4 in June", [Mo.bank_rate[1822, 5], Mo.bank_rate[1822, 6]], [5, 4])
    chk("    4 from June 1822 to November 1825", Mo.bank_rate.loc[(1822, 6):(1825, 11)].unique().tolist(), [4])
    pb = Mo.prime_bills_rate
    chk("prime bills: 3.5 in every month of 1824", pb.loc[1824].unique().tolist(), [3.5])
    chk("    and to May 1825", pb.loc[(1825, 1):(1825, 5)].unique().tolist(), [3.5])
    assert pb.loc[(1825, 6)] > 3.5
    cy = Mo.consol_yield
    pct("consols, March 1823", cy[1823, 3], 4.10, 2)
    pct("    October 1824", cy[1824, 10], 3.15, 2)
    assert cy.loc[1823:1824].idxmax() == (1823, 3) and cy.loc[1823:1824].idxmin() == (1824, 10)
    pct("    mean 1824", consol_mean(Mo, 1824), 3.22, 2)
    pct("    mean 1825", consol_mean(Mo, 1825), 3.37, 2)
    # English
    chk("English, 1827", Y["en_loans"], 1827)
    chk("15 loans: 9 in 1824, 6 in 1825", [len(L), (L.year == 1824).sum(), (L.year == 1825).sum()], [15, 9, 6])
    chk("nominal (£)", L.nominal.sum(), F["en_loans"][0])
    chk("paid (£)", L.paid.sum(), F["en_loans"][1])
    pct("    nominal (万)", L.nominal.sum() / WAN, 3207.0)
    pct("    paid (万)", L.paid.sum() / WAN, 2530.8)
    pct("    paid (万), the table", L.paid.sum() / WAN, 2530.85, 2)
    for y, (n, p) in [(1824, F["en_l24_total"]), (1825, F["en_l25_total"])]:
        chk(f"    {y}: the rows add to the printed totals", [L.nominal[L.year == y].sum(), L.paid[L.year == y].sum()],
            [n, p])
    for r, (nom, price, paid, cy_, sp, d) in zip(L.itertuples(), LOAN_TABLE):
        pct(f"table {r.year} {r.en}: nominal (万)", r.nominal / WAN, nom)
        chk("    price", r.price, price)
        pct("    paid (万)", r.paid / WAN, paid, 2)
        pct("    current yield (%)", r.cy, cy_, 2)
        pct("    spread", r.spread, sp, 2)
        if d in ("无", "—"):
            assert pd.isna(r.default), r.id
            assert (d == "无") == pd.notna(r.rr), r.id
        else:
            chk("    first default 1825-1849", r.default, d)
    chk("Brazil: only 1898 in Table 3", rr_defaults("rr_t3_brazil", F, column("unit")), [1898])
    assert first_default("rr_t3_austria", F, column("unit")) is None
    chk("Denmark: 75% of the nominal capital", F["en_l25_denmark"][2] / F["en_l25_denmark"][0], 0.75)
    pct("Guatemala at 73 (万)", F["en_l25_guatemala"][0] * 0.73 / WAN, 104.29, 2)
    pct("    printed (万)", F["en_l25_guatemala"][2] / WAN, 104.30, 2)
    # eq:say-yield
    mx = L.set_index("id").loc["en_l24_mexico"]
    na = L.set_index("id").loc["en_l24_naples"]
    co = L.set_index("id").loc["en_l24_colombia"]
    chk("Mexico 1824: 5 per cent at 58", [mx.coupon, mx.price], [5, 58])
    pct("    yield", mx.cy, 8.62, 2)
    pct("    spread", mx.spread, 5.40, 2)
    chk("Naples at 92½", na.price, 92.5)
    pct("    spread", na.spread, 2.19, 2)
    # ex:say-yield
    chk("(1) Colombia: 6 per cent at 88½", [co.coupon, co.price], [6, 88.5])
    pct("    yield", co.cy, 6.78, 2)
    pct("    spread", co.spread, 3.56, 2)
    I = interest(L)
    pct("(2) interest 1824 (万)", I[L.year == 1824].sum() / WAN, 102.50, 2)
    pct("    1825 (万)", I[L.year == 1825].sum() / WAN, 62.34, 2)
    pct("    in all (万)", I.sum() / WAN, 164.84, 2)
    pct("    on the money paid (%)", 100 * I.sum() / L.paid.sum(), 6.51, 2)
    pct("    on the nominal capital (%)", 100 * I.sum() / L.nominal.sum(), 5.14, 2)
    lam = round(mx.cy, 2) - round(consol_mean(Mo, 1824), 2)
    pct("(3) lambda = 8.62 - 3.22", lam, 5.40, 2)
    pct("    (1 - 0.0540)^3 (%)", 100 * survival(lam / 100, YEARS), 84.7)
    pct("    with the unrounded lambda (%)", 100 * survival(mx.spread / 100, YEARS), 84.6)
    chk("    Mexico's default: 1827, the third year", [mx.default, mx.default - mx.year], [1827, YEARS])
    quoted("    a default within three years: about 15 per cent", 1 - survival(lam / 100, YEARS), 0.15, tol=0.005)
    # the companies
    chk("624 companies of 1824 and 1825; £372,173,100", F["en_624"], [624, 1824, 1825, 372_173_100])
    chk("74 mining companies (万)", [F["en_mining"][0], F["en_mining"][1] / WAN], [74, 3837])
    chk("1824 and 5", F["en_individual"], [1824, 5])
    chk("Tooke: seldom above 5 per cent", F["tk2_instalment"][0], 5)
    e = F["tk2_eight"]
    chk("£100 shares, £5 paid, £40 premium: eight times", e, [100, 5, 40, 8])
    chk("    40 / 5", e[2] / e[1], e[3])
    adv, inv, val = F["en_advanced"]
    pct("advanced (万)", adv / WAN, 1760.6)
    pct("    of the capital required (%)", 100 * adv / F["en_624"][3], 4.73, 2)
    # ex:say-leverage
    chk("(1) 40/5", e[2] / e[1], 8)
    pct("(2) 40/45 (%)", 100 * e[2] / (e[1] + e[2]), 88.9)
    chk("    paid in all", e[1] + e[2] + CALL, 50)
    chk("    the share is worth (paid up)", e[1] + CALL, 10)
    pct("(3) invested (万)", inv / WAN, 1518.6)
    pct("    worth (万)", val / WAN, 930.4)
    pct("    in £ millions: 9.304 / 15.186", val / 1e6, 9.304, 3)
    pct("    ", inv / 1e6, 15.186, 3)
    pct("    loss (%)", 100 * (val / inv - 1), -38.7)
    ab = F["en_abandoned"][2]
    pct("    abandoned (万)", ab / WAN, 242.0)
    chk("    invested + abandoned = advanced", inv + ab, adv)
    pct("    17.606", adv / 1e6, 17.606, 3)
    pct("    9.304/17.606 (%)", 100 * val / adv, 52.8)
    pct("    lost (%)", 100 * (1 - val / adv), 47.2)


# tab:say-loans: nominal (万), price, paid (万), current yield, spread, first default 1825-1849
LOAN_TABLE = [(350.0, 82.5, 288.75, 6.06, 2.84, "无"), (120.0, 75, 90.00, 6.67, 3.45, "无"),
         (150.0, 87, 130.50, 5.75, 2.53, 1828), (80.0, 59, 47.20, 8.47, 5.26, 1826),
         (475.0, 88.5, 420.38, 6.78, 3.56, 1826), (100.0, 85, 85.00, 7.06, 3.84, 1827),
         (320.0, 58, 185.60, 8.62, 5.40, 1827), (75.0, 77, 57.75, 7.79, 4.58, 1826),
         (250.0, 92.5, 231.25, 5.41, 2.19, "—"), (200.0, 85, 170.00, 5.88, 2.51, "无"),
         (320.0, 89.75, 287.20, 6.69, 3.32, 1827), (200.0, 56.5, 113.00, 8.85, 5.48, 1826),
         (362.5, 75.5, 271.88, 3.97, 0.61, "—"), (61.6, 78, 48.05, 7.69, 4.32, 1826),
         (142.9, 73, 104.30, 8.22, 4.85, 1828)]


def mania_and_panic(F, Y, Mo, L):
    m = load_snapshot("boe_millennium_gb_1822_1827_monthly")[1]
    assert "63 companies" in m["source"] and "June 1840 = 100" in m["series"]
    assert "Gayer, A. D., W. W. Rostow and A. J. Schwartz (1953)" in m["citation"]
    assert "Odlyzko, A. (2014)" in m["citation"] and "M10." in m["source"] and "M9." in m["source"]
    chk("the height in the first four months of 1825", F["tk2_height"], [4, 1825])
    chk("    the greatest elevation in January and February 1825", F["tk2_greatest"][0], 1825)
    s = Mo.shares_incl_mines
    pct("shares incl. mines, October 1824", s[1824, 10], 143.2)
    pct("    January 1825", s[1825, 1], 404.8)
    chk("    the highest", s.idxmax(), (1825, 1))
    pct("    times", s[1825, 1] / s[1824, 10], 2.83, 2)
    pct("    September 1826", s[1826, 9], 124.3)
    chk("    the lowest of 1826", s.loc[1826].idxmin(), 9)
    pct("    below the top (%)", 100 * (1 - s[1826, 9] / s[1825, 1]), 69.3)
    x = Mo.shares_excl_mines
    chk("shares excl. mines: highest in September 1824", x.idxmax(), (1824, 9))
    pct("    ", x[1824, 9], 108.7)
    pct("    August 1826", x[1826, 8], 82.2)
    chk("    the lowest of 1826", x.loc[1826].idxmin(), 8)
    pct("    fall (%)", 100 * (1 - x[1826, 8] / x[1824, 9]), 24.4)
    w = Mo.wholesale_1821_25
    chk("wholesale prices: highest in May 1825", w.idxmax(), (1825, 5))
    pct("    ", w[1825, 5], 116.6)
    pct("    July 1826", w[1826, 7], 96.0)
    chk("    the lowest of 1826", w.loc[1826].idxmin(), 7)
    pct("    fall (%)", 100 * (1 - w[1826, 7] / w[1825, 5]), 17.7)
    # the panic
    chk("Pole and Co., early December 1825", [Y["tk2_pole"], F["tk2_pole"][0]], [1825, 1825])
    assert column("year_note")["tk2_pole"] == "early December"
    chk("three or four London banks", F["tk2_run"], [3, 4])
    chk("Tooke's pamphlet, January 1826", F["tk2_pamphlet"][0], 1826)
    assert column("year_note")["tk2_pamphlet"] == "January"
    chk("nearly seventy banks in December 1825", F["tk2_seventy"], [70, 1825])
    chk("Ridley, 1828: 1825 and 1826, 770 country bankers, 63 stopped", [Y["tk2_ridley"]] + F["tk2_ridley"],
        [1828, 1825, 1826, 770, 63])
    pct("    63 of 770 (%)", 100 * F["tk2_ridley"][3] / F["tk2_ridley"][2], 8.2)
    chk("    23 resumed, paid 20s. in the pound", F["tk2_resumed"], [63, 23, 20])
    chk("    31 arranging", F["tk2_thirtyone"][0], 31)
    assert F["tk2_resumed"][1] + F["tk2_thirtyone"][0] < F["tk2_resumed"][0]
    chk("    1826: 17s. 6d. in the pound", F["tk2_seventeen"], [1826, 17, 6])
    pct("    (%)", 100 * (17 + 6 / 12) / 20, 87.5)
    chk("the Bank had ceased to issue £1 notes", [F["tk2_ceased"][0], F["tk2_chasm"][0]], [1, 1])
    br = Mo.bank_rate
    chk("Bank Rate: 4 in November 1825, 5 in December", [br[1825, 11], br[1825, 12]], [4, 5])
    chk("    the usury limit (Cannan)", usury(), 5)
    chk("Tooke: bills at 7 or 8 per cent, but for the usury law", F["tk2_usury78"], [7, 8])
    assert min(F["tk2_usury78"]) > usury() and "Had it not been for" in quotes()["tk2_usury78"]
    assert "at length" in quotes()["tk2_influx"]
    assert br.max() <= usury()
    chk("£600,000 or £700,000 of £1 notes (万)", [v / WAN for v in F["tk2_box"]], [60, 70])
    chk("    the week ending 24 December 1825", Y["tk2_box"], 1825)
    assert column("year_note")["tk2_box"] == "week ending 24 December"


def latin_america(F, Y, L):
    U = column("unit")
    indep = {k: int(F[k][0]) for k in ("rr_t3_argentina", "rr_t3_chile", "rr_t3_colombia", "rr_t3_mexico",
                                       "rr_t3_peru", "rr_t3_elsalvador", "rr_t3_guatemala", "rr_t3_honduras",
                                       "rr_t3_nicaragua", "rr_t3_brazil", "rr_t3_costarica")}
    for k in indep:
        assert U[k].startswith("year of independence"), k
    chk("independence: Argentina, Chile, Colombia", [indep[k] for k in ("rr_t3_argentina", "rr_t3_chile",
                                                                         "rr_t3_colombia")], [1816, 1818, 1819])
    chk("    Mexico, Peru, El Salvador, Guatemala, Honduras, Nicaragua",
        [indep[k] for k in ("rr_t3_mexico", "rr_t3_peru", "rr_t3_elsalvador", "rr_t3_guatemala", "rr_t3_honduras",
                            "rr_t3_nicaragua")], [1821] * 6)
    chk("    Brazil, Costa Rica", [indep["rr_t3_brazil"], indep["rr_t3_costarica"]], [1822, 1825])
    la = L[L.latin]
    chk("Latin American loans", len(la), 9)
    pct("    paid (万)", la.paid.sum() / WAN, 1448.3)
    pct("    share (%)", 100 * la.paid.sum() / L.paid.sum(), 57.2)
    chk("Peru 1826; by 1828", [F["rr_t8_peru"][0], F["rr_t8_1828"][0]], [1826, 1828])
    fd = {k: first_default(k, F, U) for k in ("rr_t3_peru", "rr_t3_colombia", "rr_t3_chile", "rr_t3_mexico",
                                              "rr_t3_argentina", "rr_t3_costarica", "rr_t3_elsalvador",
                                              "rr_t3_guatemala", "rr_t3_honduras", "rr_t3_nicaragua",
                                              "rr_t3_greece", "rr_t3_portugal")}
    chk("defaults: Peru, Colombia, Chile", [fd["rr_t3_peru"], fd["rr_t3_colombia"], fd["rr_t3_chile"]], [1826] * 3)
    chk("    Mexico, Argentina", [fd["rr_t3_mexico"], fd["rr_t3_argentina"]], [1827] * 2)
    chk("    Costa Rica, El Salvador, Guatemala, Honduras, Nicaragua",
        [fd[k] for k in ("rr_t3_costarica", "rr_t3_elsalvador", "rr_t3_guatemala", "rr_t3_honduras",
                         "rr_t3_nicaragua")], [1828] * 5)
    chk("    Greece, Portugal", [fd["rr_t3_greece"], fd["rr_t3_portugal"]], [1826, 1828])
    assert all(1825 <= v <= 1828 for v in fd.values())
    for y, v in [(1826, 27.1), (1827, 49.2), (1828, 58.4)]:
        pct(f"defaulted by the end of {y} (% of paid)", defaulted_share(L, y), v)
    assert defaulted_share(L, 1849) == defaulted_share(L, 1828)


def test(F, Y, A):
    g = A.pct_change() * 100
    pct("1825: real GDP (%)", g.real_gdp[1825], 2.3)
    pct("    industry (%)", g.real_industry[1825], 6.2)
    pct("    construction (%)", g.ind_construction[1825], 12.6)
    pct("    nominal GDP (%)", g.nominal_gdp_gbp_m[1825], 12.7)
    pct("    deflator (%)", g.gdp_deflator[1825], 10.2)
    pct("1826: real GDP (%)", g.real_gdp[1826], -5.4)
    pct("    agriculture (%)", g.real_agriculture[1826], -8.3)
    pct("    industry (%)", g.real_industry[1826], -8.0)
    pct("    services (%)", g.real_services[1826], -1.4)
    pct("    nominal GDP 1825 (亿)", A.nominal_gdp_gbp_m[1825] / 100, 4.287, 3)
    pct("    1826 (亿)", A.nominal_gdp_gbp_m[1826] / 100, 3.708, 3)
    pct("    nominal GDP (%)", g.nominal_gdp_gbp_m[1826], -13.5)
    pct("    deflator (%)", g.gdp_deflator[1826], -8.6)
    for (col, zh, _), v in zip(INDUSTRIES, [-18.6, -11.8, -9.4, 6.7, 7.2, 3.7, 1.4, 20.7]):
        pct(f"    {col} (%)", g[col][1826], v)
    chk("    three down, five up", [sum(g[c][1826] < 0 for c, _, _ in INDUSTRIES),
                                    sum(g[c][1826] > 0 for c, _, _ in INDUSTRIES)], [3, 5])
    pct("1827: real GDP (%)", g.real_gdp[1827], 7.7)
    chk("April 1826: wheat at 60s.", F["tk2_april60"][0], 60)
    chk("    the corn in bond, 1 May 1826", F["tk2_bond"], [1, 1826])
    Q = quotes()
    assert "acts of violence" in Q["tk2_violence"] and "distressed state" in Q["tk2_april60"]
    assert "wheat crop had been favoured" in Q["tk2_drought"] and "greatly deficient" in Q["tk2_drought"]
    chk("    the drought of 1826", Y["tk2_drought"], 1826)
    pct("    deflator (%)", g.gdp_deflator[1827], -2.7)
    d = decomp(g.nominal_gdp_gbp_m[1826] / 100, g.real_gdp[1826] / 100)
    pct("the fall of nominal GDP 1826: the price share (%)", 100 * d["share"], 62.1)
    quoted("    six tenths", d["share"], 0.6, tol=0.05)
    # ex:say-decomp, with the rounded numbers of the question
    pct("(1) ln(370.8/428.7)", math.log(370.8 / 428.7), -0.1451, 4)
    pct("    ln(1 - 0.054)", math.log(1 - 0.054), -0.0555, 4)
    pct("    ln(1 - 0.086)", math.log(1 - 0.086), -0.0899, 4)
    pct("    0.0899/0.1451 (%)", 100 * 0.0899 / 0.1451, 62.0)
    pct("    the unrounded logs (%)", 100 * math.log(1 - 0.086) / math.log(370.8 / 428.7), 62.0)
    pct("(2) 1816: nominal, real, deflator (%)", g.nominal_gdp_gbp_m[1816], -11.2)
    pct("    ", g.real_gdp[1816], -5.3)
    pct("    ", g.gdp_deflator[1816], -6.3)
    pct("    ln(1 - 0.112)", math.log(1 - 0.112), -0.1188, 4)
    pct("    ln(1 - 0.063)", math.log(1 - 0.063), -0.0651, 4)
    pct("    0.0651/0.1188 (%)", 100 * 0.0651 / 0.1188, 54.8)
    pct("    the unrounded logs (%)", 100 * math.log(1 - 0.063) / math.log(1 - 0.112), 54.8)
    pct("(3) 1.077 x 0.973 - 1 (%)", 100 * (1.077 * 0.973 - 1), 4.8)
    pct("    the data (%)", g.nominal_gdp_gbp_m[1827], 4.8)
    pct("    deflator 1827 against 1825 (%)", change(A.gdp_deflator, 1825, 1827), -11.1)
    # the long run
    pct("1815-1830: real GDP (%)", change(A.real_gdp, 1815, 1830), 27.0)
    pct("    industry (%)", change(A.real_industry, 1815, 1830), 63.6)
    pct("    deflator (%)", change(A.gdp_deflator, 1815, 1830), -24.9)
    pct("    nominal GDP (%)", change(A.nominal_gdp_gbp_m, 1815, 1830), -4.7)
    pct("1817: real GDP (%)", g.real_gdp[1817], 1.7)
    # the first slump was long: real GDP fell a little in 1818 and 1819 and passed 1815 only in 1820;
    # the second was short: 1827 was above 1825
    chk("    1818 and 1819 fell a little", [g.real_gdp[1818] < 0, g.real_gdp[1819] < 0], [True, True])
    chk("    below 1815 in 1816-1819, above in 1820",
        [A.real_gdp[y] < A.real_gdp[1815] for y in range(1816, 1821)], [True, True, True, True, False])
    chk("    1827 above 1825", A.real_gdp[1827] > A.real_gdp[1825], True)
    chk("the annual series: 1815-1830", [A.index[0], A.index[-1], len(A)], [1815, 1830, 16])


def deeper(F, Y):
    U = column("juan")
    pages = lambda pre: sorted({int(re.search(r"p\. (\d+)", U[k]).group(1)) for k in U if k.startswith(pre)})
    p3, p21 = pages("sy03_"), pages("sy21_")
    chk("Say (1803): pp. 152-154", [p3[0], p3[-1]], [152, 154])
    chk("Say (1821): pp. 162-170", [p21[0], p21[-1]], [162, 170])
    assert U["sy21_france"].endswith("footnote")
    s = meta()["sources"]["ricardo1817"]["version"]
    assert "two chapters V and two chapters VIII" in s and "first edition" in s
    chk("English: Denmark 75½, paid 75%", [F["en_l25_denmark"][1], F["en_l25_denmark"][2] / F["en_l25_denmark"][0]],
        [75.5, 0.75])
    chk("    Guatemala at 73 (£)", round(F["en_l25_guatemala"][0] * 0.73), 1_042_857)
    chk("    printed (£)", F["en_l25_guatemala"][2], 1_042_988)
    n24, p24 = F["en_l24_total"]
    n25, p25 = F["en_l25_total"]
    pct("1824: nominal, paid (万)", n24 / WAN, 1920.0)
    pct("    ", p24 / WAN, 1536.4)
    pct("1825: nominal, paid (万)", n25 / WAN, 1287.0)
    pct("    ", p25 / WAN, 994.4)
    chk("    together", [n24 + n25, p24 + p25], F["en_loans"])
    Un = column("unit")
    assert "Colombia, Ecuador, and Venezuela" in quotes()["rr_t8_granc"]
    chk("    Gran Colombia defaults in the year of Peru's default", Y["rr_t8_granc"], F["rr_t8_peru"][0])
    for k in ("rr_t3_ecuador", "rr_t3_venezuela"):
        chk(f"{k}: independence 1830, default 1826", F[k][:2], [1830, 1826])
        assert Un[k].startswith("year of independence")
    chk("Austria: defaults 1802, 1805, 1811, 1816 and 1868", sorted(F["rr_t3_austria"]),
        [1802, 1805, 1811, 1816, 1868])
    assert all(not 1825 <= v <= 1849 for v in F["rr_t3_austria"])
    eu = quotes()["rr_t3_europe"]
    assert "Denmark" not in eu and "Ital" not in eu and "Naples" not in eu and "Austria" in eu
    chk("Tooke: nearly seventy (January 1826); Ridley 1828: 63 of 770 in 1825-1826",
        [F["tk2_seventy"][0], Y["tk2_ridley"], F["tk2_ridley"][3], F["tk2_ridley"][2]], [70, 1828, 63, 770])


def takeaways_and_selfcheck(F, Y, A, Mo, L):
    chk("Say 1803, Ricardo 1817, Malthus 1820, Sismondi 1819", [Y["sy03_truth"], Y["rp_say"], Y["ml_excess"],
                                                                 Y["sm_crise"]], [1803, 1817, 1820, 1819])
    chk("Walras 1874, Lange 1942, Mill 1829-1830", [Y["wl_avoine"], Y["lg_walras"]] + F["jm_written"],
        [1874, 1942, 1829, 1830])
    chk("hats: 100,000 made, 90,000 sold, 10,000 left", F["sm_sold"] + [F["sm_sold"][0] - F["sm_sold"][1]],
        [100_000, 90_000, 10_000])
    chk("Bank Rate 4, prime bills 3.5 to May 1825", [Mo.bank_rate[1825, 5], Mo.prime_bills_rate[1825, 5]], [4, 3.5])
    pct("15 loans: nominal, paid (万)", L.nominal.sum() / WAN, 3207.0)
    pct("    ", L.paid.sum() / WAN, 2530.8)
    pct("    Mexico's spread", L.set_index("id").spread["en_l24_mexico"], 5.40, 2)
    chk("624 companies", F["en_624"][0], 624)
    pct("    4.73%", 100 * F["en_advanced"][0] / F["en_624"][3], 4.73, 2)
    s = Mo.shares_incl_mines
    pct("shares: 2.83 times, -69.3%", s[1825, 1] / s[1824, 10], 2.83, 2)
    pct("    ", 100 * (1 - s[1826, 9] / s[1825, 1]), 69.3)
    chk("nearly seventy; by 1828", [F["tk2_seventy"][0], F["rr_t8_1828"][0]], [70, 1828])
    g = A.pct_change() * 100
    pct("1826: real, nominal (%)", g.real_gdp[1826], -5.4)
    pct("    ", g.nominal_gdp_gbp_m[1826], -13.5)
    pct("1827 (%)", g.real_gdp[1827], 7.7)
    pct("1815-1830 (%)", change(A.real_gdp, 1815, 1830), 27.0)
    # self-check answers
    stock = SC1["made"] - SC1["sold"]
    chk("1. stock (万顶)", stock, 2)
    chk("    produce", SC1["demand"] - stock, 6)
    chk("    fall (%)", 100 * (1 - (SC1["demand"] - stock) / SC1["made"]), 40)
    chk("    demand against last year (%)", 100 * (1 - SC1["sold"] / SC1["last"]), 20)
    p = SC2["price"]
    pct("2. 300 x 1/3", SC2["demand"] * p, 100, 6)
    pct("    900 x 1/3, 600 x 1/3", SC2["d"] * p, 300, 6)
    pct("    ", SC2["s"] * p, 200, 6)
    pct("    900/600", SC2["d"] / SC2["s"], 1.5, 6)
    ex = SC3["sell"] - SC3["buy"]
    chk("3. excess demand for money", ex, 100)
    chk("    wanted", SC3["money"] + ex, 600)
    pct("    fall (%)", 100 * (1 - SC3["money"] / (SC3["money"] + ex)), 16.7)
    y = 100 * SC4["c"] / SC4["P"]
    chk("4. yield", y, 7.5)
    chk("    lambda", y - SC4["r"], 4.0)
    pct("    0.96^5 (%)", 100 * survival((y - SC4["r"]) / 100, SC4["years"]), 81.5)
    chk("5. profit / paid", SC5["later"] / SC5["paid"], 0.5)
    chk("    paid by the buyer", SC5["paid"] + SC5["premium"], 40)
    chk("    worth", SC5["paid"] + SC5["later"], 15)
    pct("    loss (%)", 100 * (1 - (SC5["paid"] + SC5["later"]) / (SC5["paid"] + SC5["premium"])), 62.5)
    n, dfl = 1 + SC6["nominal"], 1 + SC6["deflator"]
    pct("6. 0.90/0.93 - 1 (%)", 100 * (n / dfl - 1), -3.2)
    pct("    ln 0.93", -math.log(dfl), 0.0726, 4)
    pct("    ln 0.90", -math.log(n), 0.1054, 4)
    pct("    share (%)", 100 * math.log(dfl) / math.log(n), 68.9)


def main():
    df = _rows()
    F, Y, Q = facts(), years(), quotes()
    A, Mo, L = annual(), monthly(), loans()
    check_readings(df)
    check_text(df)
    opening(F, Y, Q)
    world(F, Y, A)
    law(F, Y, Q)
    glut(F, Y)
    debate(F, Y)
    walras(F, Y)
    boom(F, Y, Mo, L)
    mania_and_panic(F, Y, Mo, L)
    latin_america(F, Y, L)
    test(F, Y, A)
    deeper(F, Y)
    takeaways_and_selfcheck(F, Y, A, Mo, L)
    print("all Chapter 20 checks passed")


if __name__ == "__main__":
    main()
