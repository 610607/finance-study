"""Chapter 1 (一个问题引出整门课): every number and every quotation in zh/ch01_intro.tex.

    python3 checks/check_ch01.py

Inputs:
  intro_facts          quotations of the Federal Reserve Bulletin (December 1923, January 1924), Koech (2011),
                       Chiodo and Owyang (2002), Reinhart and Rogoff (2008) and the Bank of Japan's Flow of Funds
                       (checked by data/fetch/verify_web_quotes.py)
  paper_money_facts    the 明史·食货志 on the 大明宝钞 and von Glahn (1996) (Chapter 12)
  external_facts       Sri Lanka 2022: the Treasury's standstill and the CBSL's Annual Report 2022 (Chapter 5)
  prices_facts         the Bank of Japan's statements of 2016 and 2024 (Chapter 3)
  bis_japan_govcredit  BIS, credit to the general government of Japan, nominal and market value
  bis_japan_govsec     BIS, debt securities of Japan's general government by currency of denomination
  boj_jgb_holders      Bank of Japan, Flow of Funds, holders of central government securities and FILP bonds
  mof_jgb_curves       Ministry of Finance, 10-year JGB yields (Chapter 3)
  wb_inflation_annual  World Bank WDI, consumer-price inflation of Japan, Russia, Sri Lanka and Zimbabwe
  cbr_rub_usd          Bank of Russia, official rouble rate of the US dollar, 1998-1999
  cbsl_reserves        CBSL, official reserve assets and months of imports (Chapter 5)
The figure module figsrc/fig_ch01.py imports the functions defined here.

What is checked here:
  1. readings   every number of the value column of intro_facts is read from its quotation: digits, English
                number words and a number followed by million, billion or trillion
  2. the text   every “…” in the chapter is part of a quotation of the snapshots (the 明史 rows of
                paper_money_facts are quoted untranslated) after punctuation is removed, or is the chapter's Chinese
                rendering of a quotation (TRANSLATIONS: rendering -> row or rows), or a term or claim of the text
                (ALLOW)
  3. numbers    every number of the text, with quoted()
  4. the reading routes of sec:intro-map: the chapters cited in each bullet (and in the paragraph of the main
                line) are those of ROUTES, which fig:intro_road draws

Notation of the chapter (eq:intro-budget):
    G_t - T_t + i_{t-1} B_{t-1} + e_t i^f_{t-1} B^f_{t-1} = Delta B_t + e_t Delta B^f_t + Delta H_t
consolidated government (Treasury and central bank); B is held outside the central bank; the deeper box adds the
foreign-exchange reserves A^f (F is the forward rate in Chapter 5): B^f becomes B^f - A^f.
"""
from __future__ import annotations

import re
import sys

import numpy as np
import pandas as pd

from common import ROOT, load_snapshot, quoted

sys.path.insert(0, str(ROOT))
import structure  # noqa: E402

TEX = ROOT / "zh" / "ch01_intro.tex"

# Teaching inputs stated in the text
PEG = dict(need=100.0, peg=6.0, reserves=20.0, hold=40.0)   # ex:intro-peg: 亿本币, 本币/美元, 亿美元, 亿本币
CENTS = 100                    # cents per dollar
BILLION = 1e9                  # the Bulletin's 'cents per billion marks'
CBR_BEFORE = "1998-08-15"      # the last official rate before the devaluation of August 17 (a Saturday's rate,
                               # which holds until the next record, 1998-08-18)
CBR_END98, CBR_END99 = "1998-12-31", "1999-12-30"
# the reading routes of sec:intro-map and fig:intro_road, as chapter slugs in the order of the text
ROUTES = {
    "main": ["say", "generaltheory", "naturalrate", "ratex", "gfc", "frictions", "inflation21", "fiscaldominance"],
    "money": ["money", "greekroman", "medieval", "songming", "mercantilism", "tokugawa", "weimar", "monetarism",
              "hyperinflation", "digitalmoney"],
    "debt": ["accounts", "silver", "finrevolution", "warfinance", "budget", "eurocrisis", "fiscaldominance"],
    "fx": ["external", "goldstandard", "periphery", "brettonwoods", "mundell", "latamdebt", "emcrises", "hierarchy"],
    "japan": ["prices", "tokugawa", "alternatives", "japanbubble", "zlb", "abenomics", "fiscaldominance", "longarcs"],
}
# the bullet of each route in sec:intro-map, by its bold heading
ROUTE_HEADS = {"money": "钱为什么值钱。", "debt": "政府能借多少。", "fx": "汇率与外债。", "japan": "日本。"}


def chk(what: str, value: float, expected: float | None = None, tol: float = 1e-9, rel: float = 0.0) -> float:
    """quoted() with a tolerance for floating-point error on exact values."""
    return quoted(what, float(value), expected, tol=tol, rel=rel)


def pct(what: str, value: float, expected: float, digits: int = 1) -> float:
    """A number printed with `digits` decimals."""
    return quoted(what, float(value), expected, tol=0.5 * 10 ** -digits + 1e-12)


# ---------------------------------------------------------------------------------------------------
# Loaders
def _rows(name: str) -> pd.DataFrame:
    df, meta = load_snapshot(name, dtype=str, keep_default_na=False)
    assert 1 in meta["used_in"], name
    assert df["id"].is_unique, name
    return df


def rows() -> pd.DataFrame:
    return _rows("intro_facts")


def num(x: str) -> float:
    if "/" in x:
        a, b = x.split("/")
        return float(a) / float(b)
    return float(x)


def values(df: pd.DataFrame) -> dict[str, list[float]]:
    """id -> the numbers of the value column (several are separated by ';')."""
    return {r.id: [num(x) for x in r.value.split(";")] for r in df.itertuples() if r.value}


def facts() -> dict[str, list[float]]:
    """The values of intro_facts and of the rows of Chapters 3, 5 and 12 that the text uses."""
    F = values(rows())
    for name in ("paper_money_facts", "external_facts", "prices_facts"):
        F.update(values(_rows(name)))
    return F


def years() -> dict[str, int]:
    out = {}
    for name in ("intro_facts", "paper_money_facts", "external_facts", "prices_facts"):
        out.update({r.id: int(r.year) for r in _rows(name).itertuples() if r.year})
    return out


def year_notes() -> dict[str, str]:
    out = {}
    for name in ("intro_facts", "paper_money_facts"):
        out.update({r.id: r.year_note for r in _rows(name).itertuples() if r.year_note})
    return out


def bib_year(key: str) -> int:
    """The year of a reference, the last four-digit year before the full stop that ends its entry."""
    ref = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    entry = ref.split(f"\\bibitem{{{key}}}", 1)[1].split("\n\n", 1)[0]
    return int(re.findall(r"(\d{4})\.", entry)[0])


def other_quotes() -> pd.DataFrame:
    """The rows of Chapters 3, 5 and 12 whose quotations the text uses."""
    return pd.concat([_rows(n) for n in ("paper_money_facts", "external_facts", "prices_facts")], ignore_index=True)


def bis() -> pd.DataFrame:
    """Credit to Japan's general government (BIS WS_TC) with the securities by currency (WS_NA_SEC_DSS)."""
    a, m1 = load_snapshot("bis_japan_govcredit")
    b, m2 = load_snapshot("bis_japan_govsec")
    assert 1 in m1["used_in"] and 1 in m2["used_in"]
    df = a.set_index("quarter").join(b.set_index("quarter"), how="left")
    df["denominator"] = df.nominal_jpy_bn / df.nominal_pct * 100        # the GDP the BIS's ratio implies
    df["foreign_share"] = 100 * df.foreign_jpy_bn / df.all_jpy_bn
    return df


def holders(unit: str = "share_pct", panel: str = "jgb") -> pd.DataFrame:
    """Holders of central government securities and FILP bonds (panel jgb), market value."""
    df, m = load_snapshot("boj_jgb_holders")
    assert 1 in m["used_in"]
    return df[(df.panel == panel) & (df.unit == unit)].set_index("month").drop(columns=["panel", "unit"])


def jgb10() -> pd.Series:
    df, m = load_snapshot("mof_jgb_curves")
    assert 1 in m["used_in"]
    return df.set_index("date")["10Y"].dropna()


def jgb10_monthly() -> pd.Series:
    """Month-end 10-year yield: the snapshot keeps month-ends before 2013 and every business day from 2013."""
    s = jgb10()
    return s.groupby(s.index.str[:7]).last()


def wdi() -> pd.DataFrame:
    df, m = load_snapshot("wb_inflation_annual")
    assert 1 in m["used_in"]
    return df.pivot(index="year", columns="country", values="inflation")


def japan_level(start: int, end: int) -> float:
    """Japan's consumer price level in `end` relative to `start`, chained from WDI inflation."""
    j = wdi()["JPN"]
    return float(np.prod(1 + j.loc[start + 1:end] / 100))


def cbr() -> pd.Series:
    df, m = load_snapshot("cbr_rub_usd")
    assert 1 in m["used_in"]
    return df.set_index("date")["rub_per_usd"]


def lk_reserves() -> pd.DataFrame:
    df, m = load_snapshot("cbsl_reserves")
    assert 1 in m["used_in"]
    return df.set_index("month")


# ---------------------------------------------------------------------------------------------------
# The arithmetic of the chapter
def mark(F) -> dict:
    """The mark in the Bulletin of January 1924: par and the market rates, in marks per dollar."""
    par = F["fx_mark"][0]                                         # cents per mark
    dec_lo, dec_hi, dec_avg, nov_lo, nov_hi, nov_avg = F["fx_mark"][1:]  # cents per billion marks
    per_dollar = CENTS / dec_avg * BILLION
    return dict(par=CENTS / par, dec=per_dollar, ratio=per_dollar / (CENTS / par), nov_range=nov_hi / nov_lo,
                nov_lo=nov_lo, nov_hi=nov_hi, dec_avg=dec_avg, par_cents=par)


def zeros(F) -> dict:
    """Zimbabwe's three redenominations: zeros removed and the value of the Z$100 trillion note."""
    z = [F["ko_2006"][0], F["ko_2008"][0], F["ko_2009"][0]]
    assert [10 ** x for x in z] == [F["ko_2006"][1], F["ko_2008"][1], F["ko_2009"][1]]
    note = F["ko_100tn"][0]                       # a third-dollar note
    return dict(zeros=z, total=sum(z), note=note, note_fourth=note / 10 ** z[2],
                note_first=note * 10 ** (z[0] + z[1]))


def peg(P=PEG) -> dict:
    """ex:intro-peg: the part of the new money the public does not hold is changed into dollars at the peg."""
    excess = P["need"] - P["hold"]
    lost = excess / P["peg"]
    left = P["reserves"] - lost
    second = P["need"] / P["peg"]                 # next period: none of the 100 is held
    return dict(excess=excess, lost=lost, left=left, second=second, enough=second <= left, base=P["hold"])


def ratio_example(B: pd.DataFrame, a: str = "2020-Q4", b: str = "2026-Q1") -> dict:
    """ex:intro-ratio: debt up, ratio down; the denominator implied."""
    d = B.nominal_jpy_bn[b] / B.nominal_jpy_bn[a]
    r = B.nominal_pct[b] / B.nominal_pct[a]
    return dict(debt=d - 1, ratio=r - 1, denominator=d / r - 1, market=B.market_jpy_bn[b] / B.market_jpy_bn[a] - 1)


def rouble() -> dict:
    c = cbr()
    before, end98, end99 = c[CBR_BEFORE], c[CBR_END98], c[CBR_END99]
    return dict(before=before, end98=end98, end99=end99, x98=end98 / before, x99=end99 / before,
                lost=1 - before / end98)


def scale(F) -> pd.DataFrame:
    """fig:intro_scale: log10 of the factor by which each money lost value (Russia and Sri Lanka: the dollar's
    price in local money; Japan: the price level)."""
    M, Z, R = mark(F), zeros(F), rouble()
    ming = F["ming_1375_par"][0] / F["ming_chenghua"][0]          # 1000 文 to less than 1 文: at least 10^3
    lk = F["lk_t515_usd"][2] / F["lk_t515_usd"][1]
    items = [("ming", ming, True), ("weimar", M["ratio"], False), ("zimbabwe", 10.0 ** Z["total"], False),
             ("russia", R["x98"], False), ("russia99", R["x99"], False), ("srilanka", lk, False),
             ("japan", japan_level(1990, 2025), False)]
    return pd.DataFrame([(k, v, np.log10(v), lb) for k, v, lb in items],
                        columns=["case", "factor", "log10", "lower_bound"]).set_index("case")


def routes() -> dict[str, list[tuple[int, str, int]]]:
    """ROUTES as (chapter number, slug, part) in the order of the text."""
    num_of = {slug: n for n, slug, *_ in structure.CHAPTERS}
    part_of = {n: p for p, _k, _zh, _en, _per, a, b in structure.PARTS for n in range(a, b + 1)}
    return {k: [(num_of[s], s, part_of[num_of[s]]) for s in v] for k, v in ROUTES.items()}


# ---------------------------------------------------------------------------------------------------
# 1. Readings of the numbers
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
SCALES = {"million": 1e6, "billion": 1e9, "trillion": 1e12}
DENOMS = {"thirds": 3}


def english(s: str) -> float:
    """An English number word, with the unit after it: 'two years', 'three zeros'; or a fraction: 'two-thirds'."""
    w = s.lower().replace("-", " ").split()
    if w[-1] in DENOMS:
        return english(w[0]) / DENOMS[w[-1]]
    assert not any(x in WORDS for x in w[1:]), s
    return WORDS[w[0]]


def digits(s: str) -> float:
    """The number at the start of a phrase ('3 percent', '1,000', '.0153'), and a scale word after it
    ('231 million', '10 billion', '1 trillion')."""
    w = s.split()
    v = float(w[0].replace(",", ""))
    if len(w) > 1 and w[1] in SCALES:
        v *= SCALES[w[1]]
    return v


# id -> [(phrase in the quotation, how it is read)], in order; how: en (English words), num (digits, with a scale
# word after them). Rows not listed are read with all the digits of the quotation.
READINGS = {
    "frb_bills": [("two years", "en")],
    "fx_mark": [("23.82", "num"), (".0153", "num"), (".0249", "num"), (".0222", "num"), (".0140", "num"),
                (".2900", "num"), (".0430", "num")],
    "ko_official": [("231 million", "num"), ("489 billion", "num")],
    "ko_2006": [("three zeros", "en"), ("1,000 old", "num")],
    "ko_2008": [("10 zeros", "num"), ("10 billion", "num")],
    "ko_2009": [("12 zeros", "num"), ("1 trillion", "num")],
    "ko_100tn": [("100 trillion", "num")],
    "ko_t1_de": [("29,525.71", "num")],
    "ko_t1_zw": [("2,600.2", "num")],
    "ko_extdebt": [("119 percent", "num"), ("11 percent", "num")],
    "ko_output": [("50 percent", "num")],
    "ko_bonus": [("3 percent", "num")],
    "ko_cagan7": [("seven instances", "en"), ("six European", "en"), ("1920", "num"), ("1946", "num")],
    "ko_cagandef": [("50 percent", "num")],
    "co_gko30": [("30 percent", "num")],
    "co_aug17": [("17,", "num")],
    "co_sep2": [("2,", "num")],
    "co_depleted": [("17,", "num")],
    "co_generations": [("three generations", "en")],
    "rr_twothirds": [("64 countries", "num"), ("two-thirds", "en")],
    "rr_triple": [("66 percent", "num")],
    "rr_japan45": [("80 percent", "num"), ("500 percent", "num")],
    "rr_t3_de20": [("66.5", "num"), ("52.6", "num"), ("19.4", "num"), ("73.0", "num")],
    "rr_t3_de23": [("22220194522.37", "num"), ("0.0", "num"), ("0.0", "num"), ("1.0", "num")],
    "rr_t3_jp44": [("26.6", "num"), ("236.7", "num"), ("27.8", "num"), ("89.5", "num")],
    "rr_t3_jp45": [("568.1", "num"), ("266.5", "num"), ("74.4", "num"), ("78.2", "num")],
    "rr_ru": [("39 billion", "num")],
    "rr_zw": [("98.5 percent", "num")],
    "rr_jp46": [("100 yen", "num")],
}


def read(phrase: str, how: str) -> float:
    return english(phrase) if how == "en" else digits(phrase.rstrip(","))


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
                got.append(read(phrase, how))
        else:
            got = [float(x.replace(",", "")) for x in re.findall(r"\d[\d,]*(?:\.\d+)?", r.quote)]
        assert [round(g, 9) for g in got] == [round(v, 9) for v in vals], f"{r.id}: read {got}, value column {vals}"
        n += 1
    quoted("rows with values, each read from its quotation", n, 48)


# ---------------------------------------------------------------------------------------------------
# 2. Every “…” of the text against the snapshots
PUNCT = re.compile(r"[\s，。、；：！？“”‘’（）《》·…—﹑,.;:!?'\"()\[\]|\-]")
# terms of the text and claims it examines, which are not quotations
ALLOW = {"四层读法", "付得起", "深入一步", "发行货币", "外汇", "付不出", "拿不出外汇", "付不出美元", "闭合", "靠通胀来还",
         "不还", "买没买", "取决于", "政府能借多少", "日本", "储蓄必然等于投资", "债务约为 GDP 的两倍",
         "日本的债务这么高，迟早要靠通胀来还", "日本迟早要靠通胀来还债", "债务超过 GDP 的某个比例就会出事",
         "本币债不会违约", "印钱必然导致恶性通胀", "只有外债才会出问题", "能印钱就没有风险",
         "日本银行买了一半的国债，等于政府欠自己的钱，所以日本的债务其实只有一半。", "日本会不会走向财政主导"}
# the chapter's Chinese renderings of the English quotations: rendering -> row (or rows, for a sentence quoted in
# fragments)
TRANSLATIONS = {
    "每单位外币多少美分": "fx_cents",
    "每十亿马克多少美分": "fx_billion",
    "明代的宝钞从一开始就是不兑现的": "vg_nonconvertible",
    "几乎是基础货币的三倍": "rr_triple", "几乎是三倍": "rr_triple",
    "10 月 15 日依政府法令组建德国的一家新发行银行，名为地租银行（Rentenbank）": "frb_renten",
    "政府将从这家新银行得到 12 亿地租马克的贷款": "frb_loan",
    "政府打算用这笔信用赎回它在帝国银行贴现的全部国库券，并弥补今后两年的预算赤字": "frb_bills",
    "约 30\\%（5,000 万美元）出自德国帝国银行的储备，与向比利时支付的赔款有关": "frb_gold",
    "开始货币化（加印钞票）": "ko_monet", "货币化": "ko_monet",
    "政府印了更多的钱": "ko_printed",
    "官方记录的 2008 年 7 月的年通胀率是 2.31 亿\\%，国际货币基金组织估计 2008 年 9 月的年通胀率是 4,890 亿\\%": "ko_official",
    "去掉三个零": "ko_2006",
    "正式退出": "ko_demise",
    "超过 98.5\\% 的国内债务期限不到一年": "rr_zw",
    "将购买日本国债，使十年期国债收益率大体保持在目前的水平（零左右）": "boj_ycc",
    "0 至 0.1\\% 左右": "boj_exit",
    "把汇率维持在每美元 5 到 6 卢布之间": "co_band",
    "自 1990 年的巴西以来最大的本币债务违约（390 亿美元）": "rr_ru",
    "暂停偿付所有受影响的对外公共债务，为期至这些债务以有序、协商一致的方式重组为止": "lk_faq_policy",
    "外债": "lk_faq_extdebt",
    "（一）以斯里兰卡卢比以外的货币计价、（二）适用斯里兰卡以外的法律": "lk_faq_extdebt",
    "在钉住汇率下，俄罗斯无法靠铸币税融资": "co_seign",
    "印卢布只会加大这种压力，因为私人部门仍然可以按固定汇率把卢布换成外币": ("co_printing", "co_printing2"),
    "印卢布只会加大这种压力": "co_printing",
    "在固定汇率制度下，俄罗斯唯一的选择是耗尽外汇储备": "co_only",
    "除了 1998 年 8 月 17 日贬值以外，别无选择": "co_depleted",
    "俄罗斯政府的高债务与下降的收入，大大增加了它遭受投机攻击的可能": "co_revenue",
    "保卫卢布耗尽了俄罗斯的外汇储备": "co_depleted",
    "利息支付增加，债务迅速增长": "co_debtgrew",
    "收入的短缺预示着可能通过增加货币供给来减轻公共债务负担": "co_expect",
    "停止支付": "co_halt",
    "让汇率浮动": "co_floated",
    "国内债务占公共债务总额的将近三分之二": "rr_twothirds",
    "在通胀之后，把所有的钞票按一比一换成新发行的钞票，每人以 100 日元为限，其余的存进冻结账户": "rr_jp46",
    "政府可能用通胀把债务抹掉，但公开拒付国内公共债务极为罕见": "rr_assume",
    "货币与债务存量指每段时期开始时的水平": "rr_t3_note",
    "虽然比外债违约少，却绝不罕见": "rr_68",
}


def norm(s: str) -> str:
    return PUNCT.sub("", s)


def tex_text() -> str:
    return "\n".join(l for l in TEX.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("%"))


def text_quotations() -> list[str]:
    return re.findall(r"“([^”]*)”", tex_text())


def check_text(df: pd.DataFrame) -> None:
    other = other_quotes()
    ids = set(df["id"]) | set(other["id"])
    corpus = [norm(q) for q in other[other["file"] == "mingshi"]["quote"]]     # quoted untranslated
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
    print(f"ok {n} quotations of the text found in the snapshots (or listed as exceptions)")


# ---------------------------------------------------------------------------------------------------
# 3. Numbers, section by section
def opening(F, B, W, Y):
    M = mark(F)
    chk("Bulletin: par (cents per mark)", M["par_cents"], 23.82)
    chk("    Dec 1-21 average (cents per billion marks)", M["dec_avg"], 0.0222)
    pct("    par: marks per dollar", M["par"], 4.20, 2)
    quoted("    Dec: marks per dollar (万亿)", M["dec"] / 1e12, 4.5, tol=0.05)
    quoted("    ratio: about a trillion (万亿)", M["ratio"] / 1e12, 1.0, tol=0.1)
    pct("BIS: 2020-Q4, % of GDP (nominal)", B.nominal_pct["2020-Q4"], 220.3)
    pct("    2026-Q1", B.nominal_pct["2026-Q1"], 193.6)
    chk("    'about twice GDP': 2026-Q1 / 200", B.nominal_pct["2026-Q1"] / 200, 1, tol=0.05)
    j = W["JPN"].loc[1995:2021]
    chk("WDI: 1995-2021 years", len(j), 27)
    chk("    years with falling prices", (j < 0).sum(), 15)
    s = jgb10()
    chk("10Y: minimum (%)", s.min(), -0.297)
    assert s.idxmin().startswith("2016-07"), s.idxmin()
    chk("    2026-09-30 (%)", s["2026-09-30"], 3.057)
    assert s.index[-1] == "2026-09-30"
    chk("Russia: year of the default", Y["co_aug17"], 1998)
    chk("Sri Lanka: year of the standstill", Y["lk_faq_policy"], 2022)
    chk("chapters after this one: 八十多", len(structure.CHAPTERS) - 1, 83)


def world(F, B, W, Y):
    # Ming
    chk("Ming: 洪武八年", Y["ming_1375_par"], 1375)
    chk("    千文", F["ming_1375_par"][0], 1000)
    chk("    洪武二十六年", Y["ming_1393_copper"], 1393)
    chk("    百六十文", F["ming_1393_copper"][0], 160)
    chk("    永乐二年 (陈瑛)", Y["ming_chenying"], 1404)
    chk("    成化 (1465-1487): 不能直钱一文", F["ming_chenghua"][0], 1)
    chk("    below a thousandth of par", F["ming_chenghua"][0] / F["ming_1375_par"][0], 1e-3)
    # Weimar
    M = mark(F)
    chk("Weimar: November low (cents per billion)", M["nov_lo"], 0.0140)
    chk("    November high", M["nov_hi"], 0.2900)
    pct("    times", M["nov_range"], 20.7)
    de20, de23 = F["rr_t3_de20"], F["rr_t3_de23"]
    chk("RR 1920: inflation (%)", de20[0], 66.5)
    chk("    domestic debt / GDP (%)", de20[1], 52.6)
    chk("    base money / GDP (%)", de20[2], 19.4)
    quoted("    debt / base: 几乎三倍", de20[1] / de20[2], 3, tol=0.35)
    chk("RR 1923: debt and base / GDP (%)", de23[1] + de23[2], 0.0)
    chk("    inflation (%)", de23[0], 22220194522.37)
    chk("Koech Table 1: Germany 1920-23 (% a month)", F["ko_t1_de"][0], 29525.71)
    chk("Rentenbank: October 15", F["frb_renten"][0], 15)
    chk("    capital (亿 Rentenmarks)", F["frb_capital"][0] / 1e8, 32)
    chk("    loan (亿)", F["frb_loan"][0] / 1e8, 12)
    chk("    two years", F["frb_bills"][0], 2)
    chk("gold: per cent", F["frb_gold"][0], 30)
    chk("    万 dollars", F["frb_gold"][1] / 1e4, 5000)
    # Zimbabwe
    N = year_notes()
    for rid, date in [("ko_2006", "Aug. 1, 2006"), ("ko_2008", "Aug. 1, 2008"), ("ko_2009", "Feb. 3, 2009"),
                      ("ko_100tn", "Jan. 16, 2009"), ("co_lending", "May 27, 1998"), ("co_yield", "August 13, 1998")]:
        assert N[rid] == date, (rid, N[rid])
    chk("Zimbabwe: 1997, % of GDP", F["ko_bonus"][0], 3)
    chk("    veterans (万)", F["ko_veterans"][0] / 1e4, 6)
    chk("    drought from 1999, land 2000-2001", F["ko_drought"][0] + F["ko_land"][0], 1999 + 2000)
    chk("    output 2000-2009 (%)", F["ko_output"][0], 50)
    chk("    external debt 1980, 2008 (%)", F["ko_extdebt"][1], 11)
    chk("        2008", F["ko_extdebt"][0], 119)
    chk("    July 2008 (% a month)", F["ko_t1_zw"][0], 2600.2)
    chk("    July 2008 (亿 % a year)", F["ko_official"][0] / 1e8, 2.31)
    chk("    IMF September 2008 (亿 %)", F["ko_official"][1] / 1e8, 4890)
    Z = zeros(F)
    chk("    zeros removed", Z["zeros"][0], 3)
    chk("        2008", Z["zeros"][1], 10)
    chk("        2009", Z["zeros"][2], 12)
    chk("    total zeros (10^25)", Z["total"], 25)
    chk("    Z$100 trillion (万亿)", Z["note"] / 1e12, 100)
    chk("RR: Zimbabwe 2006, % under a year", F["rr_zw"][0], 98.5)
    chk("    year", Y["rr_zw"], 2006)
    # Japan
    pct("Japan BIS 1997-Q4 (%)", B.nominal_pct["1997-Q4"], 81.1)
    assert B.nominal_pct.idxmax() == "2020-Q4" and B.index[0] == "1997-Q4" and B.index[-1] == "2026-Q1"
    quoted("    securities 2026-Q1 (万亿 yen)", B.all_jpy_bn["2026-Q1"] / 1e3, 1267, tol=0.5)
    quoted("    foreign currency (万亿 yen)", B.foreign_jpy_bn["2026-Q1"] / 1e3, 1.0, tol=0.05)
    pct("    share (%)", B.foreign_share["2026-Q1"], 0.08, 2)
    fs = B.foreign_share.dropna()
    assert fs.index[0] == "2012-Q1"
    pct("    highest since 2012 (%)", fs.max(), 0.10, 2)
    H = holders()
    chk("BoJ share 2012-03 (%)", H.central_bank["2012-03"], 9.43)
    chk("    2023-09 (%)", H.central_bank["2023-09"], 53.86)
    assert H.central_bank.idxmax() == "2023-09"
    chk("    2026-06 (%)", H.central_bank["2026-06"], 46.70)
    assert H.index[-1] == "2026-06"
    chk("BoJ YCC: 2016", Y["boj_ycc"], 2016)
    chk("BoJ exit: 2024, 0 to 0.1", F["boj_exit"][0] + F["boj_exit"][1], 0.1)
    s = jgb10()
    chk("10Y 1990-09 month-end (%)", jgb10_monthly()["1990-09"], 8.105)
    chk("    the highest month-end", jgb10_monthly().max(), 8.105)
    j = W["JPN"]
    pct("CPI 1995-2021: mean (%)", j.loc[1995:2021].mean(), 0.1)
    pct("    2022", j[2022], 2.5)
    pct("    2023", j[2023], 3.3)
    pct("    2024", j[2024], 2.7)
    pct("    2025", j[2025], 3.2)
    # Russia
    chk("Russia: band 5 to 6", F["co_band"][0] * 10 + F["co_band"][1], 56)
    chk("    GKO non-residents, late 1997 (%)", F["co_gko30"][0], 30)
    chk("    lending rate May 27 (%)", F["co_lending"][0], 150)
    chk("    yields August 13 (%)", F["co_yield"][0], 200)
    chk("    devaluation August 17", F["co_aug17"][0], 17)
    chk("    float September 2", F["co_sep2"][0], 2)
    R = rouble()
    pct("CBR: 1998-08-15", R["before"], 6.29, 2)
    pct("    1998-12-31", R["end98"], 20.65, 2)
    pct("    1999-12-30", R["end99"], 27.00, 2)
    chk("    output 1998 (%)", F["co_output"][0], 4.9)
    r = W["RUS"]
    pct("WDI Russia 1998 (%)", r[1998], 27.7)
    pct("    1999 (%)", r[1999], 85.7)
    chk("RR: Russia (亿 dollars)", F["rr_ru"][0] / 1e8, 390)
    # Sri Lanka
    chk("Sri Lanka: GOR end-2022 (亿 dollars)", F["lk_gor_decl"][0] / 100, 18.98)
    chk("    months of merchandise imports", F["lk_gor_months"][0], 1.2)
    chk("    rupees per dollar end-2021", F["lk_t515_usd"][1], 200.43)
    chk("    end-2022", F["lk_t515_usd"][2], 363.11)
    pct("WDI Sri Lanka 2022 (%)", W["LKA"][2022], 49.7)


def afford(F, B, Y):
    chk("bullets: Zimbabwe external debt (%)", F["ko_extdebt"][0], 119)
    chk("    Russia GKO non-residents (%)", F["co_gko30"][0], 30)
    chk("paths: Russia yields (%)", F["co_yield"][0], 200)
    chk("    Zimbabwe under a year (%)", F["rr_zw"][0], 98.5)
    chk("    Sri Lanka months", F["lk_gor_months"][0], 1.2)
    de, zw = F["ko_t1_de"][0], F["ko_t1_zw"][0]                   # 一个月涨几十倍甚至几百倍
    chk("money: Germany's highest month (%)", de, 29525.71)
    chk("    Zimbabwe's last official month (%)", zw, 2600.2)
    assert 10 <= 1 + zw / 100 < 100 and 100 <= 1 + de / 100 < 1000, (zw, de)
    P = peg()
    chk("ex:intro-peg (1): not held (亿)", P["excess"], 60)
    chk("    reserves lost (亿 dollars)", P["lost"], 10)
    chk("    left", P["left"], 10)
    chk("    base money up by", P["base"], 40)
    pct("(2) dollars needed (亿)", P["second"], 16.7)
    assert not P["enough"]
    chk("case: lending rate from 30 to 150 in May 1998", F["co_twice"][0] + F["co_twice"][1], 180)
    chk("    year", F["co_twice"][2], 1998)
    chk("    attack held in November 1997", F["co_attack"][0], 1997)
    chk("    90 days", F["co_halt"][0], 90)
    R = rouble()
    pct("    1998-08-15 -> year end", R["before"], 6.29, 2)
    pct("    the ruble's dollar value lost (%)", 100 * R["lost"], 69.5)
    chk("compare: overt domestic defaults", F["rr_68"][0], 68)
    chk("    external defaults after 1800", F["rr_68"][1], 250)
    chk("        year", F["rr_68"][2], 1800)
    chk("RR: 64 countries", F["rr_twothirds"][0], 64)
    chk("    two-thirds", F["rr_twothirds"][1], 2 / 3)
    chk("pitfall: 1920 debt / GDP", F["rr_t3_de20"][1], 52.6)
    chk("    1923", F["rr_t3_de23"][1], 0.0)
    chk("    Japan 1946: 100 yen", F["rr_jp46"][0], 100)
    chk("        year", Y["rr_jp46"], 1946)
    A = holders("tn_yen").loc["2026-06"]
    chk("deeper: BoJ holdings (万亿 yen)", A.central_bank, 470)
    chk("    total (万亿 yen)", A.total, 1007)
    quoted("    share from the amounts (%)", 100 * A.central_bank / A.total, 46.70, tol=0.05)
    chk("    share (%)", holders().central_bank["2026-06"], 46.70)


def layers(F, B):
    pct("layer 1: foreign-currency share (%)", B.foreign_share["2026-Q1"], 0.08, 2)
    H = holders().loc["2026-06"]
    for col, v in [("central_bank", 46.70), ("insurance_pension", 18.31), ("depository", 14.23),
                   ("public_pensions", 7.61), ("overseas", 7.94), ("households", 2.18), ("others", 3.03)]:
        chk(f"layer 2: {col} (%)", H[col], v)
    domestic = H.depository + H.insurance_pension + H.public_pensions + H.households + H.others
    pct("    domestic holders other than the BoJ (%)", domestic, 45.36, 2)
    pct("    the shares add up", domestic + H.central_bank + H.overseas, 100, 2)
    assert H.overseas < 10                                                        # 海外不到一成
    pct("layer 4: nominal (%)", B.nominal_pct["2026-Q1"], 193.6)
    pct("    market (%)", B.market_pct["2026-Q1"], 175.6)
    E = ratio_example(B)
    quoted("ex:intro-ratio: debt 2020-Q4 (万亿 yen)", B.nominal_jpy_bn["2020-Q4"] / 1e3, 1219.96, tol=0.005)
    quoted("    2026-Q1", B.nominal_jpy_bn["2026-Q1"] / 1e3, 1302.19, tol=0.005)
    pct("    debt (%)", 100 * E["debt"], 6.7)
    pct("    ratio (%)", 100 * E["ratio"], -12.1)
    pct("    ratio (percentage points)", B.nominal_pct["2020-Q4"] - B.nominal_pct["2026-Q1"], 26.7)
    quoted("    printed factors", 1302.19 / 1219.96, 1.0674, tol=0.00005)
    quoted("        ", 193.6 / 220.3, 0.8788, tol=0.00005)
    pct("    denominator (%)", 100 * E["denominator"], 21.5)
    pct("    from the printed factors (%)", 100 * (1.0674 / 0.8788 - 1), 21.5)
    cpi = japan_level(2021, 2025)                                                 # 2022-2025, chained
    pct("    consumer prices 2022-2025 (%)", 100 * (cpi - 1), 12, 0)
    assert cpi - 1 < E["denominator"]                                             # only a part of it
    quoted("    market 2020-Q4 (万亿 yen)", B.market_jpy_bn["2020-Q4"] / 1e3, 1281.40, tol=0.005)
    quoted("    market 2026-Q1", B.market_jpy_bn["2026-Q1"] / 1e3, 1181.30, tol=0.005)
    pct("    market value (%)", 100 * E["market"], -7.8)


def cases(F, Y, N):
    S = scale(F)
    for k, v in S.log10.items():
        print(f"    scale {k}: x{S.factor[k]:.4g}, log10 {v:.3f}")
    chk("Ming: at least 10^3", S.factor["ming"], 1e3)
    quoted("Weimar: about 10^12", S.log10["weimar"], 12.0, tol=0.05)
    chk("Zimbabwe: 10^25", S.log10["zimbabwe"], 25)
    pct("Russia: dollar price x", S.factor["russia"], 3.28, 2)
    pct("Sri Lanka: x", S.factor["srilanka"], 1.81, 2)
    pct("Japan: price level 1990-2025 (%)", 100 * (S.factor["japan"] - 1), 25, 0)
    chk("    years", 2025 - 1990, 35)
    chk("compare: Russia", Y["co_halt"], 1998)
    chk("    Sri Lanka", Y["lk_faq_multilateral"], 2022)
    chk("    Japan", Y["rr_jp46"], 1946)
    chk("table: Ming from", Y["ming_1375_par"], 1375)
    assert "1465—1487" in N["ming_chenghua"]                                     # to the end of 成化
    chk("    Weimar 1920-1923", Y["rr_t3_de20"] + Y["rr_t3_de23"], 1920 + 1923)
    chk("    Zimbabwe 1997-2009", Y["ko_bonus"] + Y["ko_demise"], 1997 + 2009)
    chk("    Weimar Rentenbank, October 1923", F["frb_renten"][0], 15)
    chk("    Zimbabwe external debt (%)", F["ko_extdebt"][0], 119)


def test(F, B, W):
    chk("RR Japan 1944: debt / GDP", F["rr_t3_jp44"][1], 236.7)
    chk("    inflation", F["rr_t3_jp44"][0], 26.6)
    chk("    1945: debt / GDP", F["rr_t3_jp45"][1], 266.5)
    chk("        inflation", F["rr_t3_jp45"][0], 568.1)
    pct("BIS 2020-Q4 (%)", B.nominal_pct["2020-Q4"], 220.3)
    pct("WDI Japan 2020 (%)", W["JPN"][2020], -0.02, 2)
    H = holders()
    chk("BoJ 2012-03 -> 2023-09", H.central_bank["2023-09"] - H.central_bank["2012-03"], 53.86 - 9.43)
    j = W["JPN"].loc[2012:2023]
    pct("    Japan's CPI, highest year (%)", j.max(), 3.3)
    quoted("Zimbabwe: IMF / official, orders of magnitude", np.log10(F["ko_official"][1] / F["ko_official"][0]),
           3.3, tol=0.05)
    assert np.log10(F["ko_official"][1] / F["ko_official"][0]) > 3                        # 三个数量级以上
    assert W["ZWE"].dropna().index.min() == 2010
    chk("CO: floated on August 17 (text)", F["co_floated"][0], 17)
    chk("    September 2 (timeline)", F["co_sep2"][0], 2)
    c = cbr()
    pct("CBR 1998-08-18", c["1998-08-18"], 6.43, 2)
    pct("    1998-09-01", c["1998-09-01"], 9.33, 2)
    pct("    1998-09-04", c["1998-09-04"], 13.46, 2)
    # the official rate starts to rise after August 17; the large fall is in early September (the timeline's float)
    assert 0 < c["1998-08-18"] / c[CBR_BEFORE] - 1 < 0.05, c["1998-08-18"]
    assert c["1998-09-04"] / c["1998-08-18"] > 2, c["1998-09-04"]
    assert c.loc["1998-08-18":"1998-08-31"].max() < c["1998-09-01"]
    assert c[CBR_BEFORE] > F["co_band"][1]              # 6.29 is above the band of 1997 already (PLAN, review)


def check_routes():
    tex = tex_text()
    sec = tex.split("\\label{sec:intro-map}", 1)[1].split("\\section{", 1)[0]
    refs = lambda s: re.findall(r"\\(?:ch)?ref\{ch:([a-z0-9]+)\}", s)              # noqa: E731
    main = sec.split("本章的问题可以拆成四条线索", 1)[0]
    assert refs(main) == ROUTES["main"], refs(main)
    bullets = sec.split("\\begin{itemize}", 1)[1].split("\\end{itemize}", 1)[0].split("\\item")[1:]
    assert len(bullets) == len(ROUTE_HEADS)
    for (k, head), b in zip(ROUTE_HEADS.items(), bullets):
        assert f"\\textbf{{{head}}}" in b, head
        assert refs(b) == ROUTES[k], (k, refs(b))
    R = routes()
    for k, v in R.items():
        assert [n for n, *_ in v] == sorted(n for n, *_ in v), k                    # in the order of the book
        print(f"ok route {k}: chapters {[n for n, *_ in v]}, parts {sorted({p for *_, p in v})}")
    chk("parts", len(structure.PARTS), 11)
    chk("De Vroey (2016)", bib_year("devroey"), 2016)
    chk("Snowdon and Vane (2005)", bib_year("snowdonvane"), 2005)
    chk("Cagan (1956)", bib_year("cagan1956"), 1956)
    F = facts()                                         # the main line in the chapter's own cases (Koech; Chiodo-Owyang)
    chk("    episodes", F["ko_cagan7"][0], 7)
    chk("    countries", F["ko_cagan7"][1], 6)
    chk("    from", F["ko_cagan7"][2], 1920)
    chk("    to", F["ko_cagan7"][3], 1946)
    chk("Chiodo and Owyang: generations of models", F["co_generations"][0], 3)


def legacy(F, Y, B, W):
    s = jgb10()
    chk("10Y 2016-07 minimum", s.min(), -0.297)
    chk("    2026-09-30", s["2026-09-30"], 3.057)
    H = holders()
    chk("BoJ 2023-09 -> 2026-06", H.central_bank["2023-09"], 53.86)
    chk("overseas 2012-03 (%)", H.overseas["2012-03"], 4.03)
    chk("    2026-06 (%)", H.overseas["2026-06"], 7.94)
    quoted("a 3% rate: the 10-year yield, 2026-09-30", s["2026-09-30"], 3, tol=0.06)
    chk("Sri Lanka: IMF staff level 2022, Board 2023", Y["lk_imf"], 2023)
    L = lk_reserves()
    chk("    official reserve assets 2026-07 (亿 dollars)", L.official_reserve_assets["2026-07"] / 100, 66.00)
    chk("    months of imports", L.gor_months["2026-07"], 3.2)
    assert L.index[-1] == "2026-07"
    chk("RR: 64 countries", F["rr_twothirds"][0], 64)


def takeaways_and_selfcheck(F, B, W):
    chk("TA2: 1.2 months", F["lk_gor_months"][0], 1.2)
    chk("    52.6 -> 0.0", F["rr_t3_de20"][1] - F["rr_t3_de23"][1], 52.6)
    chk("TA3: 68", F["rr_68"][0], 68)
    pct("TA4: 193.6 and 175.6", B.nominal_pct["2026-Q1"] - B.market_pct["2026-Q1"], 193.6 - 175.6)
    chk("TA5: 1945 and 2020", F["rr_t3_jp45"][1], 266.5)
    pct("    2020", B.nominal_pct["2020-Q4"], 220.3)
    chk("    568.1", F["rr_t3_jp45"][0], 568.1)
    pct("    -0.02", W["JPN"][2020], -0.02, 2)
    E = ratio_example(B)
    pct("SC4: debt (%)", 100 * E["debt"], 6.7)
    pct("    ratio down (%)", -100 * E["ratio"], 12.1)
    pct("    denominator (%)", 100 * E["denominator"], 21.5)
    Z = zeros(F)
    chk("SC5: 3 + 10 + 12", Z["total"], 25)
    chk("    a fourth dollar in first dollars", 10.0 ** Z["total"], 1e25)
    chk("    Z$100 trillion in fourth dollars", Z["note_fourth"], 100)
    chk("        10^14 / 10^12", Z["note"] / 1e12, 100)
    chk("    in first dollars (10^27)", np.log10(Z["note_first"]), 27)
    pct("A2: Russia 1999 (%)", W["RUS"][1999], 85.7)
    pct("A3: 52.6 / 19.4", F["rr_t3_de20"][1] / F["rr_t3_de20"][2], 2.7)


def main():
    df = rows()
    F, Y = facts(), years()
    B, W = bis(), wdi()
    check_readings(df)
    check_text(df)
    opening(F, B, W, Y)
    world(F, B, W, Y)
    afford(F, B, Y)
    layers(F, B)
    cases(F, Y, year_notes())
    test(F, B, W)
    check_routes()
    legacy(F, Y, B, W)
    takeaways_and_selfcheck(F, B, W)
    print("all Chapter 1 checks passed")


if __name__ == "__main__":
    main()
