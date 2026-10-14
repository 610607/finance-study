"""Chapter 9 (古代印度与印度洋贸易): every number and every quotation in zh/ch09_india.tex.

    python3 data/fetch/darley2014_coin_finds.py      # first: writes data/snapshots/darley2014_coin_finds.csv
    python3 checks/check_ch09.py

Inputs:
  india_facts            quotations of Pliny, Strabo, the Periplus, Tacitus, the Arthashastra (with Fleet's note and
                         Francis's review of Olivelle), Cunningham (1891), Casson (1990), Howgego et al. (2010),
                         Darley (2014), Scheidel (2019) and the BEA manual (checked by data/fetch/verify_web_quotes.py),
                         and of the 汉书 and 后汉书 (checked by data/fetch/verify_quotes.py)
  darley2014_coin_finds  Roman coins found in India by issuer, century and metal, summed from Appendix 6 of Darley
                         (2014); not kept in the repository (the thesis may not be redistributed): run the fetch first
  wb_external_annual     the US current account in 2025 (Chapter 5)
  greek_facts            Nero's reform of the denarius (Chapter 7, tab:greek-silver)
  qinhan_facts           the year of the salt and iron debate (Chapter 8)
The figure module figsrc/fig_ch09.py imports the functions defined here.

What is checked here:
  1. readings   every number of the value column is read from its quotation: digits, English number words,
                fractions, the Roman numerals of the Latin text and the classical numerals of the 汉书 and 后汉书
                (data/fetch/classical_numerals.py)
  2. the text   every “…” in the chapter is part of a quotation of the snapshot (the 汉书 and 后汉书, and the Latin
                and English quoted untranslated) after punctuation is removed and variant forms are mapped, or is the
                chapter's Chinese rendering of a quotation (TRANSLATIONS: rendering -> row), or a Wikisource reading
                listed in the snapshot's notes (WITNESS), or a term of the text (ALLOW)
  3. numbers    every number of the text, with quoted()

Notation of the chapter:
    balance of payments  CA + KA + EO = FA = Delta A - Delta L                        (eq:external-bop, Chapter 5)
    coins                X + C = M with Delta L = 0, KA = EO = 0:
                         coins as goods  CA = X + C - M = 0;  coins as a financial asset  CA = X - M = -C = Delta A
                                                                                       (eq:india-coin)
    risk                 p (1 + i) = 1 + r_f                                           (eq:africa-risk, Chapter 14)
    coin value           v = c + tau (vbar - c)                                         (eq:greek-value, Chapter 7)
Units: 1 denarius = 4 sesterces (Pliny 33.45); 1 aureus = 25 denarii (the translators' note); an Egyptian
tetradrachm = 1 denarius (Howgego et al.), so 1 Egyptian drachma = 1 sestertius; 1 talent = 60 minas (weight) or
6000 drachmas (money), 1 drachma = 6 obols, solved from the papyrus in ex:india-cargo; Pliny's numerals are read as
multiples of 100,000 sesterces (33.133 and 12.84).
"""
from __future__ import annotations

import re
import sys
from fractions import Fraction

import pandas as pd

from common import ROOT, load_snapshot, quoted

sys.path.insert(0, str(ROOT / "data" / "fetch"))
from classical_numerals import checked  # noqa: E402

TEX = ROOT / "zh" / "ch09_india.tex"

# Reign years (first year of each era) for the 汉书 and 后汉书; the snapshot's notes give the same conversions.
ERA = {"元始": 1, "永元": 89, "延熹": 158}

# Definitions and teaching inputs stated in the text
GRAIN_G = 0.06479891       # grams per grain (the definition of the grain)
R_F = 0.15                 # ex:india-risk: the 'just' rate taken as the riskless rate
MONTH_DAYS = 30            # ex:india-route: a month taken as 30 days, 余 taken at its lower bound
GDP_SCALE = 1e9            # Scheidel's billions of sesterces
POP_SCALE = 1e6            # and millions of people
SELF = dict(coins=1e6, gdp=20e9)   # selfcheck: 100 万 sesterces of coins; GDP 200 亿 (Scheidel's 'a little less than 20 billion')
CENTURY_YEARS = 100        # a century of Pliny's outflow
TRANSLATIONS_19C = {"Bostock and Riley 1855-57": 1855, "Hamilton and Falconer 1854-57": 1854, "McCrindle 1879": 1879,
                    "Church and Brodribb 1876": 1876, "Shamasastry 1915": 1915}
CENTURIES = ["pre-1st", "1st", "2nd", "3rd", "4th", "5th", "6th", "7th"]
METALS = ["AR", "AV", "AE"]          # Darley's note: silver, gold, copper
METAL_CSV = {"AR": "silver", "AV": "gold", "AE": "copper"}


def chk(what: str, value: float, expected: float | None = None, tol: float = 1e-9, rel: float = 0.0) -> float:
    """quoted() with a tolerance for floating-point error on exact values."""
    return quoted(what, float(value), expected, tol=tol, rel=rel)


def pct(what: str, value: float, expected: float, digits: int = 1) -> float:
    """A percentage printed with `digits` decimals."""
    return quoted(what, float(value), expected, tol=0.5 * 10 ** -digits + 1e-12)


# ---------------------------------------------------------------------------------------------------
# Loaders
def num(x: str) -> float:
    return float(Fraction(x)) if "/" in x else float(x)


def rows() -> pd.DataFrame:
    df, meta = load_snapshot("india_facts", dtype=str, keep_default_na=False)
    assert 9 in meta["used_in"]
    assert df["id"].is_unique
    return df


def meta() -> dict:
    return load_snapshot("india_facts", dtype=str, keep_default_na=False)[1]


def facts() -> dict[str, list[float]]:
    """id -> the numbers of the value column (several are separated by ';'; fractions as a/b)."""
    return {r.id: [num(x) for x in r.value.split(";")] for r in rows().itertuples() if r.value}


def years() -> dict[str, int]:
    return {r.id: int(r.year) for r in rows().itertuples() if r.year}


def darley() -> pd.DataFrame:
    """Coins by issuer, century and metal (Darley 2014, Appendix 6); run data/fetch/darley2014_coin_finds.py first."""
    df, m = load_snapshot("darley2014_coin_finds")
    assert 9 in m["used_in"]
    return df


def darley_totals() -> pd.DataFrame:
    """The note to Fig. 5.8: coins by century (rows) and metal (AR, AV, AE)."""
    v = facts()["da_totals"]
    assert len(v) == len(CENTURIES) * len(METALS)
    return pd.DataFrame([v[3 * i:3 * i + 3] for i in range(len(CENTURIES))], index=CENTURIES, columns=METALS)


def us_ca_2025() -> float:
    """US current account 2025, % of GDP (negative: a deficit), as in Chapter 5."""
    df, _ = load_snapshot("wb_external_annual")
    r = df.set_index(["country", "year"]).loc[("USA", 2025)]
    return 100 * r["ca"] / r["gdp"]


def greek() -> dict[str, list[float]]:
    df, _ = load_snapshot("greek_facts", dtype=str, keep_default_na=False)
    return {r.id: [num(x) for x in r.value.split(";")] for r in df.itertuples() if r.value}


def qinhan_years() -> dict[str, int]:
    df, _ = load_snapshot("qinhan_facts", dtype=str, keep_default_na=False)
    return {r.id: int(r.year) for r in df.itertuples() if r.year}


# ---------------------------------------------------------------------------------------------------
# The arithmetic of the chapter
def units(F) -> dict:
    """Units: sesterces per denarius, denarii per aureus, sesterces per Egyptian drachma, Pliny's multiple."""
    hs = F["pl_denarius"][0] / F["pl_denarius"][2]          # 16 asses / 4 asses
    return dict(hs_per_denarius=hs, denarii_per_aureus=F["pl_aureus"][0],
                hs_per_drachma=F["hw_tetra"][0] * hs / 4,    # a tetradrachm (4 drachmas) = 1 denarius
                multiple=F["pl_100k"][0])


def talents(F) -> tuple[float, float]:
    """(minas per talent of weight W, drachmas per talent of money T) solved from the ivory and the fabric:
    (76 W + 45) 100 = 76 T + 4500 and (12 W + 27) 70 = 8 T + 4290."""
    a_t, a_m, a_p, b_t, b_d = F["ca_ivory_net"]
    c_t, c_m = F["ca_fab_customs"]
    c_p, d_t, d_d = F["ca_fab_net"]
    # ivory: a_p a_t W - b_t T = b_d - a_p a_m;  fabric: c_p c_t W - d_t T = d_d - c_p c_m (Cramer's rule, exact)
    a11, a12, y1 = (Fraction(x) for x in (a_p * a_t, -b_t, b_d - a_p * a_m))
    a21, a22, y2 = (Fraction(x) for x in (c_p * c_t, -d_t, d_d - c_p * c_m))
    det = a11 * a22 - a12 * a21
    return float((y1 * a22 - a12 * y2) / det), float((a11 * y2 - y1 * a21) / det)


def obols(F) -> float:
    """Obols per drachma, from the remainder of the fabric: 22 3/4 m. at 70 d. = 1592 d. 3 ob."""
    d = F["ca_fab_rest_m"][0] * F["ca_fab_net"][0]
    whole, ob = F["ca_fab_rest"]
    return ob / (d - whole)


def cargo(F) -> dict:
    """The three parcels of the verso, in drachmas, and the grand total of the six."""
    W, T = talents(F)
    ob = obols(F)
    nard = F["ca_nard"][0] * T
    ivory = F["ca_ivory_tot"][0] * T + F["ca_ivory_tot"][1]
    fabric = F["ca_fab_tot"][0] * T + F["ca_fab_tot"][1] + F["ca_fab_tot"][2] / ob
    total = F["ca_total"][1] * T + F["ca_total"][2]
    return dict(W=W, T=T, ob=ob, nard=nard, ivory=ivory, fabric=fabric, three=nard + ivory + fabric, total=total,
                duty=total * F["ca_quarter"][0])


def pliny(F) -> dict:
    """Pliny's figures in sesterces: the 100 million of 12.84, the D and DL of 6.101 as multiples of 100,000, and
    the 550 million of the translation."""
    m = F["pl_100k"][0]
    return dict(three=F["pl_100m"][0], india=F["lc_drain"][0] * m, india_dl=F["my_app"][0] * m,
                translation=F["pl_drain"][0], hundred=F["pl_hundred"][0])


def scale(F) -> pd.DataFrame:
    """fig:india_scale: each item as a share of Roman GDP (Scheidel's 18 billion), %."""
    gdp = F["sc_gdp18"][0] * GDP_SCALE
    P, c = pliny(F), cargo(F)
    hs = units(F)["hs_per_drachma"]
    items = [("duty", c["duty"] * hs), ("ship", c["total"] * hs), ("india", P["india"]), ("india_dl", P["india_dl"]),
             ("three", P["three"]), ("translation", P["translation"]), ("centiplicato", P["india"] * P["hundred"])]
    return pd.DataFrame([(k, v, 100 * v / gdp) for k, v in items], columns=["item", "hs", "pct_gdp"]).set_index("item")


def rates(F) -> pd.DataFrame:
    """The Arthashastra's four rates: per month per cent, simple annual rate, and p of eq:africa-risk at r_f."""
    names = ["just", "commercial", "forest", "sea"]
    m = F["ar_just"]
    df = pd.DataFrame(dict(monthly=m), index=names)
    df["annual"] = 12 * df["monthly"] / 100
    df["p"] = (1 + R_F) / (1 + df["annual"])
    return df


def route(F) -> dict:
    """ex:india-route: days of the Roman route (Pliny) and of the Han route (汉书, months of 30 days)."""
    rome = dict(nile=F["pl_coptos"][1], desert=F["pl_desert"][0], red_sea=F["pl_ocelis"][0], ocean=F["pl_muziris"][0])
    m1, m2, d_ship, d_walk = F["hs_route"]
    m3 = F["hs_huangzhi"][0]
    back1, back2 = F["hs_return"]
    han_out = dict(dou=m1 * MONTH_DAYS, yilu=m2 * MONTH_DAYS, chenli=d_ship, walk=d_walk, huangzhi=m3 * MONTH_DAYS)
    han_back = dict(pizong=back1 * MONTH_DAYS, rinan=back2 * MONTH_DAYS)
    han_back_ws = dict(pizong=back1 * MONTH_DAYS, rinan=back1 * MONTH_DAYS)     # Wikisource: 船行可八月
    return dict(rome=rome, han_out=han_out, han_back=han_back, han_back_ws=han_back_ws)


def finds_1st(D: pd.DataFrame) -> pd.DataFrame:
    """fig:india_coins (b): coins of the 1st century by issuer and metal (Unidentified left out)."""
    sub = D[(D.century == "1st") & (D.issuer != "Unidentified")]
    return sub.pivot_table(index="issuer", columns="metal", values="coins", aggfunc="sum", fill_value=0)


# ---------------------------------------------------------------------------------------------------
# 1. Readings of the numbers
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
         "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
         "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
         "seventy": 70, "eighty": 80, "ninety": 90}
SCALES = {"thousand": 1e3, "million": 1e6, "millions": 1e6}
DENOMS = {"half": 2, "fourth": 4, "fourths": 4, "fifth": 5, "sixth": 6, "eighth": 8, "sixteenth": 16}
ORDINALS = {"sixth": 6, "third": 3}
ROMAN = {"D": 500, "L": 50}


def english(s: str) -> float:
    """An English number phrase: 'thirteen hundred and thirty-five', 'five hundred and fifty millions',
    'one-fourth', 'three-fourths', 'half'."""
    w = [x for x in s.lower().replace("-", " ").split() if x != "and"]
    if w[-1] in DENOMS:
        return (english(" ".join(w[:-1])) if w[:-1] else 1) / DENOMS[w[-1]]
    total, cur = 0.0, 0.0
    for x in w:
        if x in WORDS:
            cur += WORDS[x]
        elif x == "hundred":
            cur *= 100
        elif x in SCALES:
            total, cur = total + cur * SCALES[x], 0.0
        else:
            raise ValueError(f"not a number word: {x!r} in {s!r}")
    return total + cur


def digits(s: str) -> float:
    """Digits, with thousands separators, a mixed fraction ('54 3/4') or a fraction ('1/5th')."""
    s = s.replace(",", "").removesuffix("th")
    parts = s.split()
    return float(sum(Fraction(p) for p in parts))


def roman(s: str) -> float:
    out, prev = 0, 0
    for ch in reversed(s):
        v = ROMAN[ch]
        out, prev = (out - v if v < prev else out + v), max(prev, v)
    return out


# id -> [(phrase in the quotation, how it is read)], in order; how: en (English words), num (digits), bc (a year BC
# in digits), roman, ord (an ordinal), zh (a classical numeral, data/fetch/classical_numerals.py) or a number given
# with the reason in a comment
READINGS = {
    "pl_drain": [("five hundred and fifty millions", "en")],
    "pl_hundred": [("one hundred", "en")],
    "pl_coptos": [("three hundred and eight", "en"), ("twelve", "en")],
    "pl_berenice": [("two hundred and fifty-seven", "en")],
    "pl_desert": [("twelve", "en")],
    "pl_ocelis": [("thirty", "en")],
    "pl_muziris": [("forty", "en")],
    "pl_return": [("sixth day", "ord")],
    "pl_hippalus": [("thirteen hundred and thirty-five", "en")],
    "pl_100m": [("one hundred millions", "en")],
    "pl_denarius": [("sixteen", "en"), ("eight", "en"), ("four", "en")],
    "pl_100k": [("one hundred thousand", "en")],
    "lc_drain": [("D", "roman")],
    "my_app": [("DL", "roman")],
    "st_120": [("one hundred and twenty", "en")],
    "st_twenty": [("twenty", "en")],
    "ar_just": [("a pana and a quarter", 1.25), ("Five", "en"), ("Ten", "en"), ("Twenty", "en")],
    "ar_grain": [("half", "en")],
    "ar_mint": [("four", "en"), ("one-sixteenth", "en")],
    "ar_dharana": [("16", "num")],
    "ar_premia": [("8", "num"), ("5", "num"), ("one-eighth", "en")],
    "ar_saltshare": [("five", "en")],
    "ar_saltimport": [("one-sixth", "en")],
    "ar_store": [("half", "en")],
    "ar_toll": [("1/5th", "num")],
    "ar_profit": [("five", "en"), ("ten", "en")],
    "ar_wages": [("one-fourth", "en")],
    "fl_date": [("321", "bc"), ("296", "bc")],
    "cu_buddha": [("1,000", "bc")],
    "ca_quarter": [("one-fourth", "en")],
    "ca_default": [("three-fourths", "en")],
    "ca_missing": [("three", "en")],
    "ca_ivory_w": [("78", "num"), ("54 3/4", "num")],
    "ca_ivory_rest_m": [("11 3/4", "num")],
    "ca_fab_gross": [("13", "num"), ("9 3/4", "num")],
    "ca_fab_rest_m": [("22 3/4", "num")],
    "ca_aqueduct": [("1155", "num"), ("7,000,000", "num"), ("4,000,000", "num"), ("3,000,000", "num")],
    "hw_tetra": [("one", "en")],
    "da_young": [("100 million", 1e8)],                     # digits and a word
    "da_young2": [("twenty-five", "en")],
    "da_raschke_ref": [("1978", "num")],
    "da_young_ref": [("2001", "num")],
    "da_third_date": [("third", "ord")],
    "hs_route": [("船行可五月", "五"), ("又船行可四月", "四"), ("二十余日", "二十"), ("十余日", "十")],
    "hs_return": [("船行可八月", "八"), ("船行可二月", "二")],
    "hhs_ganying": [("永元九年", "九"), ("善风三月", "三")],
    "hhs_twoyears": [("二岁", "二"), ("三岁", "三")],
    "hhs_coins": [("银钱十当", "十")],
}


def read(phrase: str, how) -> float:
    if not isinstance(how, str):
        return float(how)
    if how == "en":
        return english(phrase)
    if how == "num":
        return digits(phrase)
    if how == "bc":
        return -digits(phrase)
    if how == "roman":
        return roman(phrase)
    if how == "ord":
        return ORDINALS[phrase.split()[0]]
    return float(checked(how))       # a classical numeral; the phrase is its context


def check_readings(df: pd.DataFrame) -> None:
    n = 0
    for r in df.itertuples():
        if not r.value:
            continue
        vals = [num(x) for x in r.value.split(";")]
        if r.id in READINGS:
            got, pos = [], 0
            for phrase, how in READINGS[r.id]:
                k = r.quote.find(phrase, pos)
                assert k >= 0, f"{r.id}: {phrase!r} not found (in order) in the quotation"
                if isinstance(how, str) and len(how) and how[0] > "　":   # classical numeral in its context
                    assert how in phrase
                pos = k + len(phrase)
                got.append(read(phrase, how))
        elif r.id == "da_totals":
            got = []
            for c in re.split(r";\s*(?=(?:Pre-1st|\d))", r.quote):
                got += [float(x) for x in re.findall(r"A[RVE]\s*=\s*(\d+)", c)]
        elif r.numeral:
            got = [float(checked(r.numeral))]
        else:
            got = [float(x.replace(",", "")) for x in re.findall(r"\d[\d,]*(?:\.\d+)?", r.quote)]
        assert [round(g, 9) for g in got] == [round(v, 9) for v in vals], f"{r.id}: read {got}, value column {vals}"
        n += 1
    quoted("rows with values, each read from its quotation", n, 84)


# ---------------------------------------------------------------------------------------------------
# 2. Every “…” of the text against the snapshot
VARIANTS = str.maketrans({"巿": "市", "檋": "瑇"})
PUNCT = re.compile(r"[\s，。、；：！？“”‘’（）《》·…—﹑,.;:!?'\"()\[\]|\-]")
CORPUS = ("hanshu", "houhanshu")
# terms and phrases of the text that are not quotations
ALLOW = {"国际收支", "经常账户逆差", "外流", "逆差", "本国", "外国", "1 世纪", "余"}
# Wikisource readings the text gives beside the corpus's: form in the text -> form in the snapshot's notes
WITNESS = {"船行可八月": "船行可八月，到日南", "八月": "船行可八月，到日南", "交市": "交市", "瑇瑁": "瑇瑁",
           "若遇遲風": "若遇遲風"}
# the chapter's Chinese renderings of the English, Latin and French quotations: rendering -> row
TRANSLATIONS = {
    "按最低的估计，印度、赛里斯（Seres）与阿拉伯半岛每年从我们的帝国拿走一亿塞斯特斯——我们为奢侈与女人付的代价就是这么高。": "pl_100m",
    "按最低的估计": "pl_100m", "一亿": "pl_100m", "至少一亿": "pl_100m", "我们为奢侈与女人付的代价就是这么高。": "pl_100m",
    "赫尔玛波隆号（Hermapollon）船上运出的六批货，以银计": "ca_total", "以银计": "ca_total",
    "每枚与一第纳尔等值": "hw_tetra",
    "伽卢斯（Gallus）任埃及长官时，我和他在一起": "st_gallus",
    "了解到，大约一百二十条船从米奥斯·霍尔莫斯（Myos Hormos）开往印度，而在托勒密王朝的时候，几乎没有人敢走这条航线、做印度的生意": "st_ptolemies",
    "从前，连二十条船都不敢驶入阿拉伯湾，或驶出湾口的海峡哪怕一点点；如今，大批船队被派往远至印度与埃塞俄比亚尽头的地方。": "st_twenty",
    "三百零八英里，在季节风吹的时候，十二天走完": "pl_coptos",
    "二百五十七英里": "pl_berenice",
    "从科普托斯到贝勒尼基，全程要走十二天": "pl_desert",
    "一般在仲夏、天狼星升起之前或刚过之后启航，大约三十天到达奥克利斯（Ocelis）": "pl_ocelis", "仲夏": "pl_ocelis",
    "四十天就能到达印度最近的商埠穆齐里斯（Muziris）": "pl_muziris",
    "埃及的提比月（Tybis）之初，即我们的十二月，至迟在埃及的梅基尔月（Mechir）第六天以前": "pl_return",
    "相当于我们的一月伊都斯日（ides）：这样做，就能在一年之内往返": "pl_sameyear",
    "现在每年都有船去印度，船上载着成队的弓箭手，因为那一带海上海盗猖獗。": "pl_archers",
    "借助一种西风最为便利，那里管这种风叫希帕洛斯（Hippalus）": "pl_hippalus",
    "第一个通过观察港口的方位与海的形状，发现了横渡大洋的直航航线的领航员": "pe_hippalos",
    "大约在七月，即厄庇菲月（Epiphi）": "pe_july",
    "文本、纳巴泰王表与纳哈帕纳（Nahapana）可能的在位年代，最好的重合当然落在公元 40—70 年这几十年": "da_periplus",
    "没有得到多少支持": "da_third",
    "完成于公元 79 年以前": "da_pliny79",
    "酒，主要是意大利的": "pe_wine",
    "金币与银币，换成当地的钱有利可图": "pe_specie_b", "换成当地的钱有利可图": "pe_specie_b", "第纳尔": "pe_specie_b",
    "刻着阿波罗多托斯（Apollodotos）与米南德（Menander）希腊铭文的旧德拉克马，至今在巴利加萨流通": "pe_drachmai",
    "来这些港口的船都很大，因为它们装的胡椒与蒌叶又多又占地方": "pe_ships",
    "大量的钱币": "pe_specie_m", "少量的素布": "pe_muz_cloth", "白玻璃、铜或黄铜": "pe_muz_glass", "锡、铅": "pe_muz_tin",
    "不多，大约与巴利加萨一样多": "pe_muz_wine", "只供船员吃，因为商人不卖它": "pe_corn",
    "大量的胡椒，只产在这些商埠中的一处，叫作科托纳拉（Kottonara）胡椒": "pe_pepper",
    "用整棵树挖成的小船": "pl_barace",
    "它们得到了‘打印币’（punch-marked）这个描述性的名字": "cu_name",
    "先把一块银子打成一张薄片，大约一先令那么厚": "cu_beaten",
    "每一条再切成重量相同的小块，约 56 格令，最后从较重的坯子上切下一两个角来调整重量": "cu_cut",
    "共重 111 格令，平均只有 37 格令": "cu_three",
    "这批供物是在公元 150 年前后、印度—斯基泰国王胡毗色伽（Huvishka）在位时放进去的，可见打印币那时仍在流通": "cu_gaya",
    "全印度八百多枚这种钱的平均重量在 47 格令以上": "cu_avg",
    "我愿意接受在大约六百年的流通中损失 19 格令": "cu_loss",
    "在佛陀的时代，即公元前 6 世纪，肯定已经通行；但我看不出它们为什么不能早到公元前 1000 年": "cu_buddha",
    "这部论著，是那个不能容忍（暴政）、迅速把经典、兵法与落入难陀王之手的大地拯救出来的人写成的。": "ar_nanda",
    "因此，这部著作自称写于公元前 321—前 296 年这一时期，它古朴的文体也与这一说法相合": "fl_date",
    "现存的文本也许不是考底利耶（Kauṭilya）一字不差写下的，但我们拿到的基本上就是他在上述时期所写的书": "fl_text",
    "不仅印证并扩充了我们从希腊作家麦加斯梯尼（Megasthenes）的一些话里知道的很多东西": "fl_megas",
    "只有一部抄本和上面提到的那部不完整的注释": "fl_ms",
    "大概写成于公元 50 年到 125 年之间": "fr_kautilya",
    "后来在 175 年到 300 年之间的一次改编，使这部书有了论（śāstra）的形式": "fr_sastra",
    "把考底利耶等同于旃陀罗笈多·孔雀（Candragupta Maurya）的大臣阇那迦（Cāṇakya）": "fr_ident",
    "是笈多时代的一种虚构": "fr_gupta", "讨论并没有因此结束": "fr_open",
    "铸币长官（lakshnádhyakshah）要铸造银币（rúpyarúpa），用四份铜，加十六分之一份（másha）的 tikshna、trapu、sisa 或 anjana 中的任一种金属。钱有一帕纳、半帕纳、四分之一帕纳与八分之一帕纳。": "ar_mint",
    "16 银马沙（másha）或 20 粒 saibya 种子合 1 达拉纳（dharana）": "ar_dharana",
    "验币官（rúpadarsaka）既管作为交换媒介的钱，也管作为可以缴入国库的法偿货币的钱": "ar_examiner",
    "8\\%，叫 rúpika；5\\%，叫 vyáji；每一百帕纳八分之一帕纳，叫 páríkshika（检验费）": "ar_premia",
    "国家要把采矿与（矿产品的）买卖都作为国家专营。": "ar_monopoly",
    "盐的长官要按时收取钱租（prakraya）和应归国家的那份盐；卖掉这些盐，不仅要收回它的价值（múlyam），还要加收 5\\% 的溢价（vyájím），都收现钱（rúpa）": "ar_saltshare",
    "进口的盐（ágantulavanam）要向国王交六分之一": "ar_saltimport",
    "在盐里掺假的，处以最重的罚金；除苦行者（vánaprastha）以外，未经许可制盐的也一样": "ar_saltlicence",
    "商业长官要弄清各种商品——无论是陆上还是水里的产品，从陆路还是水路运来——有没有需求，价格是涨是跌": "ar_demand",
    "分散在各处的商品要集中起来，抬高价格。抬高的价格被接受以后，再宣布另一个价格": "ar_centralise",
    "他要避免那种会伤害百姓的高额利润": "ar_harm",
    "商业长官要为本地商品在规定的价格之上定 5\\% 的利润，外国商品定 10\\%。": "ar_profit",
    "进口外国商品的船主（návika）与商人，要免除贸易税，让他们能得到一些利润。": "ar_importers",
    "进口商品要按价值的五分之一交通行税。": "ar_toll",
    "付完（外国国王的）通行税等各项费用以后，还有没有利润的余地": "ar_abroad", "还有没有利润的余地": "ar_abroad",
    "这样收来的储备，一半要留着，以防百姓遭灾，只用另一半；旧的储备要用新的替换。": "ar_store",
    "可以把自己储存的粮食或富人囤积的收入分给百姓，以示恩惠": "ar_famine",
    "国王应把养活仆从的开支定在全部收入的四分之一以下。": "ar_wages",
    "每月每百帕纳一又四分之一帕纳的利息是公正的。每月每百帕纳五帕纳是商业利息（vyávaháriki）。每月每百帕纳十帕纳，通行于林中。每月每百帕纳二十帕纳，通行于海上商人（sámudránám）。": "ar_just",
    "公正": "ar_just", "林中": "ar_just", "海上": "ar_just",
    "超过上述利率、或使别人超过上述利率的，处以初级罚金": "ar_exceed",
    "丰收时节，粮食的利息按钱折算，不得超过一半。": "ar_grain",
    "必定是一笔海事贷款，有了它才买得到这些货": "ca_maritime",
    "不是船，而是要交 25\\% 进口关税的货物": "ca_security",
    "正像几个世纪以前德摩斯梯尼时代的商人那样": "ca_demos",
    "如果船沉了，担保就毫无意义": "ca_shipdown",
    "大致同时，都在 2 世纪中期": "ca_date",
    "我会在看守与担保之下，把（货物）经沙漠运到科普托斯收取税款的公共仓库": "ca_desert",
    "把它们顺流运到亚历山大里亚收四分之一关税的仓库": "ca_quarter",
    "原来的合同是在穆齐里斯订的": "ca_muziris",
    "借贷双方或其中一方，很可能是住在那里的外国侨民": "ca_colony",
    "剩下的四分之三，你可以运到你想去的地方，卖掉、再抵押、转让给别人，随你的意": "ca_default",
    "另外三批一定写在缺失的那部分里": "ca_missing",
    "差不多等于修建亚历山大·特罗阿斯（Alexandria Troas）引水道的花费（700 万德拉克马，其中赫罗狄斯·阿提库斯出 400 万，哈德良出 300 万）": "ca_aqueduct",
    "一条普通大小的罗马商船，载重 340 吨": "ca_340",
    "能装 11000 多塔兰特这样的货": "ca_11000",
    "它们是名副其实的宝船": "ca_treasure", "是名副其实的宝船": "ca_treasure",
    "共重 92 塔兰特，价值 528,775 德拉克马": "ca_ivfab",
    "收双份的关税，一份来自进口，一份来自出口": "st_double", "收双份的关税": "st_double",
    "最贵重的货物课税最重，因为亚历山大里亚实际上垄断了这门贸易": "st_heaviest", "最贵重的货物课税最重": "st_heaviest",
    "没有哪一年印度从我们的帝国吸走的钱少于五亿五千万塞斯特斯，它运回来的货物，在我们这里卖到原价的整整一百倍。": "pl_hundred",
    "五亿五千万": "pl_drain", "卖到原价的整整一百倍": "pl_hundred", "一百倍": "pl_hundred",
    "所以到今天，我们还是按这个数的倍数来计": "pl_100k",
    "吸干": "lc_drain",
    "货币黄金是货币当局拥有所有权、作为储备资产持有的黄金": "bea_mgold",
    "与作为金融资产的货币黄金不同，非货币的实物黄金被归为货物": "bea_ngold",
    "没有看到要点：这些钱币在印度市场上是一种有价值的商品，凭它们的外观，作价高于所含的金属": "da_commodity",
    "凭它们的外观，作价高于所含的金属": "da_commodity",
    "2 世纪的罗马帝国": "sc_century", "略少于 200 亿": "sc_gdp", "这是一个更宽的可能区间的中点": "sc_gdp18",
    "GDP 不可能低很多，否则社会就会普遍贫困，而考古记录没有反映这一点": "sc_poverty",
    "为简单起见，取 7000 万": "sc_pop",
    "到 2 世纪中期，罗马帝国的全部钱币价值达到约 200 亿塞斯特斯": "sc_dj",
    "Duncan-Jones 的估计很可能偏高": "sc_inflated",
    "一个价值相当于全年 GDP 的铸币存量，会让罗马成为一个非常罕见的例子": "sc_fullyear",
    "这些数字只是提示性的": "da_suggestive",
    "约 1531 枚": "da_akenpalle", "1398 枚": "da_budinatham", "522 枚": "da_vellalur",
    "说印度洋贸易不要白银，是站不住的，因为至少到 2 世纪晚期，罗马与印度的贸易是用第纳尔进行的": "da_denarii",
    "印度不再要白银": "da_denarii",
    "与银币含银的不断降低同时发生，这强烈地提示：罗马对印度的贸易改用金币，是因为对罗马银币成色的不信任，而不是因为对白银本身失去了兴趣": "da_trust",
    "对成色的不信任": "da_trust",
    "大概经过埃及流到印度，在那里有相当数量的发现": "hw_gold",
    "那种妇女特有的奢侈，为了宝石，把我们的财富转移到外族乃至敌国手里。": "ta_jewels",
    "他的数字是整数，又在他抨击罗马精英挥霍的长篇议论里起着修辞的作用，这应当让人在用它们做定量分析时极其谨慎": "da_round",
    "这里的论点不是说普林尼肯定没有看到政府的档案，而是说，没有证据，就不能假定他看到了": "da_records",
    "所有这些虚假的数字都应当抛弃。它们暗示了一种证据所不能支持的准确与精确": "da_raschke",
    "避免一切绝对的价值计算": "da_absolute",
    "对任何一个参与的国家来说，意义都微乎其微": "da_minimal",
    "高估了普林尼的数字（一亿塞斯特斯）在数量上的可靠性": "da_young",
    "承认，用普林尼的数字去估计对进入红海的印度货物征收的百分之二十五的税对罗马经济的价值，是冒险的": "da_young2",
}


def norm(s: str) -> str:
    return PUNCT.sub("", s.translate(VARIANTS))


def text_quotations() -> list[str]:
    tex = "\n".join(l for l in TEX.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("%"))
    return re.findall(r"“([^”]*)”", tex)


def check_text(df: pd.DataFrame) -> None:
    ids = set(df["id"])
    notes = meta()["notes"]
    corpus = [norm(q) for q in df[df["file"].isin(CORPUS)]["quote"]]
    corpus += [a + b for a, b in zip(corpus, corpus[1:])]          # a quotation running over two adjacent rows
    direct = [norm(q) for q in df[~df["file"].isin(CORPUS)]["quote"]]
    used, n = set(), 0
    for q in text_quotations():
        for part in q.split("……"):
            if not norm(part):
                continue
            n += 1
            used.add(part)
            if part in ALLOW:
                continue
            if part in WITNESS:
                assert WITNESS[part] in notes, f"Wikisource reading {part!r} is not in the snapshot's notes"
                continue
            if part in TRANSLATIONS:
                assert TRANSLATIONS[part] in ids, TRANSLATIONS[part]
                continue
            p = norm(part)
            assert any(p in c for c in corpus) or any(p in c for c in direct), f"not in the snapshot: “{part}”"
    stale = (set(ALLOW) | set(WITNESS) | set(TRANSLATIONS)) - used
    assert not stale, f"listed but not in the text: {sorted(stale)}"
    print(f"ok {n} quotations of the text found in the snapshot (or listed as exceptions)")


# ---------------------------------------------------------------------------------------------------
# 3. The text, section by section
def opening(F, U):
    P, c = pliny(F), cargo(F)
    chk("Pliny 12.84: sesterces a year", P["three"], 1e8)
    chk("后汉书: 利有十倍 / 银钱十当金钱一", F["hhs_coins"][0], 10)
    chk("Hermapollon: parcels", F["ca_total"][0], 6)
    chk("    talents", F["ca_total"][1], 1154)
    chk("    drachmas", F["ca_total"][2], 2852)
    quoted("    total (万 drachmas)", c["total"] / 1e4, 692.7, tol=0.05)
    pct("    / Pliny's 100 million (%)", 100 * c["total"] * U["hs_per_drachma"] / P["three"], 6.9)
    chk("units: sesterces per denarius", U["hs_per_denarius"], 4)
    chk("    denarii per aureus", U["denarii_per_aureus"], 25)
    chk("    sesterces per Egyptian drachma", U["hs_per_drachma"], 1)
    chk("    W: minas per talent (weight)", c["W"], 60)
    chk("    T: drachmas per talent (money)", c["T"], 6000)
    chk("    obols per drachma", c["ob"], 6)


def world(F, Y):
    chk("Strabo: ships from Myos Hormos", F["st_120"][0], 120)
    chk("    formerly not even ... vessels", F["st_twenty"][0], 20)
    chk("Pliny: Nile miles", F["pl_coptos"][0], 308)
    chk("    days", F["pl_coptos"][1], 12)
    chk("    Coptos to Berenice, miles", F["pl_berenice"][0], 257)
    chk("    days", F["pl_desert"][0], 12)
    chk("    to Ocelis, days", F["pl_ocelis"][0], 30)
    chk("    to Muziris, days", F["pl_muziris"][0], 40)
    chk("    return before the n-th day of Mechir", F["pl_return"][0], 6)
    chk("    Syagrus to Patale, miles", F["pl_hippalus"][0], 1335)
    chk("Periplus: AD from", F["da_periplus"][0], 40)
    chk("    to", F["da_periplus"][1], 70)
    chk("    third-century dating (century)", F["da_third_date"][0], 3)
    chk("Natural History before AD", Y["da_pliny79"], 79)
    m1, m2, ds, dw = F["hs_route"]
    chk("汉书: months to 都元", m1, 5)
    chk("    to 邑卢没", m2, 4)
    chk("    days to 谌离, more than", ds, 20)
    chk("    days on foot, more than", dw, 10)
    chk("    months to 黄支, more than", F["hs_huangzhi"][0], 2)
    chk("    return: months to 皮宗", F["hs_return"][0], 8)
    chk("    months to 日南", F["hs_return"][1], 2)
    assert "船行可八月，到日南" in meta()["notes"]


def ex_route(F):
    R = route(F)
    rome = sum(R["rome"].values())
    chk("ex:india-route (1): days", rome, 94)
    chk("    from Berenice", R["rome"]["red_sea"] + R["rome"]["ocean"], 70)
    quoted("    Nile miles a day", F["pl_coptos"][0] / F["pl_coptos"][1], 25.7, tol=0.05)
    quoted("    desert miles a day", F["pl_berenice"][0] / F["pl_desert"][0], 21.4, tol=0.05)
    m1, m2, ds, dw = F["hs_route"]
    chk("(2) months out", m1 + m2 + F["hs_huangzhi"][0], 11)
    chk("    days of the months", (m1 + m2 + F["hs_huangzhi"][0]) * MONTH_DAYS, 330)
    chk("    days by ship and on foot", ds + dw, 30)
    out = sum(R["han_out"].values())
    chk("    days out, at least", out, 360)
    chk("    months back", sum(F["hs_return"]), 10)
    chk("    days back", sum(R["han_back"].values()), 300)
    chk("    Wikisource: months back", 2 * F["hs_return"][0], 16)
    chk("    days", sum(R["han_back_ws"].values()), 480)
    quoted("(3) ratio of the outward journeys", out / rome, 3.8, tol=0.05)
    chk("    Ocelis to Muziris, days", F["pl_muziris"][0], 40)


def artha(F, Y, G, QY):
    chk("Cunningham: grains", F["cu_cut"][0], 56)
    quoted("    grams", F["cu_cut"][0] * GRAIN_G, 3.63, tol=0.005)
    chk("Bodh Gaya: coins' weight, grains", F["cu_three"][0], 111)
    chk("    average", F["cu_three"][1], 37)
    chk("    3 coins", F["cu_three"][0] / 3, F["cu_three"][1])
    chk("    deposited about AD", Y["cu_gaya"], 150)
    chk("    all India: coins, more than", F["cu_avg"][0], 800)
    chk("    average grains, more than", F["cu_avg"][1], 47)
    chk("    loss accepted, grains", F["cu_loss"][0], 19)
    chk("    56 - 37 = the loss", F["cu_cut"][0] - F["cu_three"][1], F["cu_loss"][0])
    chk("    years", F["cu_loss"][1], 600)
    pct("    loss (%)", 100 * (F["cu_cut"][0] - F["cu_three"][1]) / F["cu_cut"][0], 34, digits=0)
    chk("    as early as (BC)", -F["cu_buddha"][0], 1000)
    src = meta()["sources"]
    assert "1891" in src["cunningham1891"]["version"] and "1914" in src["fleet1914"]["version"]
    assert "1915" in src["artha_b2"]["version"] and "2013" in src["francis2013"]["version"]
    chk("Cunningham: century", 1891 // 100 + 1, 19)
    chk("Fleet: BC from", -F["fl_date"][0], 321)
    chk("    to", -F["fl_date"][1], 296)
    chk("Olivelle: Kautilya from", F["fr_kautilya"][0], 50)
    chk("    to", F["fr_kautilya"][1], 125)
    chk("    redaction from", F["fr_sastra"][0], 175)
    chk("    to", F["fr_sastra"][1], 300)
    gap = (F["da_periplus"][0] - F["fl_date"][1] - 1, Y["da_pliny79"] - F["fl_date"][0] - 1)   # no year 0
    assert 300 <= gap[0] and gap[1] < 400, gap
    print(f"ok Fleet's date to the Periplus and Pliny: {gap[0]:.0f} to {gap[1]:.0f} years (三四百年)")
    copper, other = F["ar_mint"]
    mashas = F["ar_dharana"][0]
    chk("mint: parts of copper", copper, 4)
    chk("    other metal (1/16 part)", other * mashas, 1)
    chk("    mashas per dharana", mashas, 16)
    silver = mashas - copper - other * mashas
    chk("    parts of silver", silver, 11)
    pct("    silver (%)", 100 * silver / mashas, 68.75, digits=2)
    chk("Nero: year", G["hr_nero"][0], 64)
    chk("    silver after (%)", G["hr_nero"][1], 80)
    chk("    before, about (%)", G["hr_pre64"][2], 90)
    r, v, t = F["ar_premia"]
    chk("premia: rupika (%)", r, 8)
    chk("    vyaji (%)", v, 5)
    chk("    testing charge, pana per cent", t, 0.125)
    pct("    together (%)", r + v + t, 13.125, digits=3)
    chk("ex:india-mint (1) below the denarius by (points)", G["hr_nero"][1] - 100 * silver / mashas, 11.25)
    chk("(2) paid for 100 panas", 100 * (1 + (r + v + t) / 100), 113.125)
    chk("(3) testing charge (%)", t, 0.125)
    chk("salt: premium (%)", F["ar_saltshare"][0], 5)
    chk("    imported salt, share", F["ar_saltimport"][0], 1 / 6)
    chk("commerce: profit on local goods (%)", F["ar_profit"][0], 5)
    chk("    on foreign goods (%)", F["ar_profit"][1], 10)
    chk("toll on imports", F["ar_toll"][0], 1 / 5)
    chk("    Alexandria's duty", F["ca_quarter"][0], 1 / 4)
    assert F["ca_quarter"][0] > F["ar_toll"][0]
    chk("store: kept in reserve", F["ar_store"][0], 1 / 2)
    chk("servants: under, of revenue", F["ar_wages"][0], 1 / 4)
    chk("盐铁论 debate (BC)", -QY["debate_81"], 81)


def interest(F):
    R = rates(F)
    for k, m, a, p in (("just", 1.25, 15, 1.0), ("commercial", 5, 60, 0.72), ("forest", 10, 120, 0.52), ("sea", 20, 240, 0.34)):
        chk(f"{k}: per month per cent", R.loc[k, "monthly"], m)
        quoted("    a year (%)", 100 * R.loc[k, "annual"], a, tol=1e-9)
        quoted("    p", R.loc[k, "p"], p, tol=0.005)
    chk("commercial / just", R.loc["commercial", "monthly"] / R.loc["just", "monthly"], 4)
    chk("sea / just", R.loc["sea", "monthly"] / R.loc["just", "monthly"], 16)
    chk("r_f (%)", 100 * R_F, 15)
    chk("grain interest: at most", F["ar_grain"][0], 1 / 2)
    chk("Casson: customs duty (%)", F["ca_security"][0], 25)
    chk("    = one-fourth", F["ca_security"][0] / 100, F["ca_quarter"][0])
    chk("ex:india-risk (3): ship lost", 1 - R.loc["sea", "p"], 0.66, tol=0.005)
    quoted("    two of every three", 1 - R.loc["sea", "p"], 2 / 3, tol=0.01)


def cargo_section(F):
    c = cargo(F)
    chk("tab:india-cargo: nard containers", F["ca_nard_a"][0], 60)
    chk("    drachmas per container", F["ca_nard_b"][0], 4500)
    chk("    talents", F["ca_nard"][0], 45)
    chk("    60 x 4500 = 45 talents", F["ca_nard_a"][0] * F["ca_nard_b"][0], c["nard"])
    chk("    drachmas", c["nard"], 270_000)
    a_t, a_m, a_p, b_t, b_d = F["ca_ivory_net"]
    chk("ivory: talents", a_t, 76)
    chk("    minas", a_m, 45)
    chk("    drachmas per mina", a_p, 100)
    chk("    remainder, minas", F["ca_ivory_rest_m"][0], 11.75)
    chk("    x 100", F["ca_ivory_rest_m"][0] * a_p, F["ca_ivory_rest"][0])
    chk("    total talents", F["ca_ivory_tot"][0], 76)
    chk("    and drachmas", F["ca_ivory_tot"][1], 5675)
    chk("    4500 + 1175", b_d + F["ca_ivory_rest"][0], F["ca_ivory_tot"][1])
    chk("    drachmas", c["ivory"], 461_675)
    chk("fabric: lengths", F["ca_fab_w"][0], 54)
    chk("    talents", F["ca_fab_customs"][0], 12)
    chk("    minas", F["ca_fab_customs"][1], 27)
    chk("    drachmas per mina", F["ca_fab_net"][0], 70)
    chk("    at the customs weight: talents", F["ca_fab_net"][1], 8)
    chk("    and drachmas", F["ca_fab_net"][2], 4290)
    chk("    remainder, minas", F["ca_fab_rest_m"][0], 22.75)
    chk("    remainder: drachmas", F["ca_fab_rest"][0], 1592)
    chk("    and obols", F["ca_fab_rest"][1], 3)
    chk("    total talents", F["ca_fab_tot"][0], 8)
    chk("    drachmas", F["ca_fab_tot"][1], 5882)
    chk("    obols", F["ca_fab_tot"][2], 3)
    chk("    4290 + 1592 d. 3 ob.", F["ca_fab_net"][2] + F["ca_fab_rest"][0] + F["ca_fab_rest"][1] / c["ob"],
        F["ca_fab_tot"][1] + F["ca_fab_tot"][2] / c["ob"])
    chk("    drachmas", c["fabric"], 53_882.5)
    chk("three parcels", c["three"], 785_557.5)
    chk("six parcels", c["total"], 6_926_852)
    # the case box
    chk("default: three-fourths", F["ca_default"][0], 3 / 4)
    chk("parcels missing", F["ca_missing"][0], 3)
    chk("    3 + 3 = 6", 3 + F["ca_missing"][0], F["ca_total"][0])
    quoted("three parcels (万)", c["three"] / 1e4, 78.6, tol=0.05)
    pct("    share (%)", 100 * c["three"] / c["total"], 11.3)
    quoted("    missing (万)", (c["total"] - c["three"]) / 1e4, 614.1, tol=0.05)
    chk("aqueduct: drachmas", F["ca_aqueduct"][1], 7e6)
    chk("    Herodes Atticus", F["ca_aqueduct"][2], 4e6)
    chk("    Hadrian", F["ca_aqueduct"][3], 3e6)
    chk("    just short of talents", F["ca_aqueduct"][0], 1155)
    assert F["ca_total"][1] < F["ca_aqueduct"][0]
    chk("merchantman: tons", F["ca_340"][0], 340)
    chk("    talents, over", F["ca_11000"][0], 11000)
    quoted("duty (万 drachmas)", c["duty"] / 1e4, 173.2, tol=0.05)
    # ex:india-cargo
    W, T = c["W"], c["T"]
    chk("ex:india-cargo (1): T = 100 W", T / W, 100)
    chk("    840 W + 1890", F["ca_fab_net"][0] * F["ca_fab_customs"][0] * W + F["ca_fab_net"][0] * F["ca_fab_customs"][1],
        840 * W + 1890)
    chk("    = 800 W + 4290", F["ca_fab_tot"][0] * T + F["ca_fab_net"][2], 800 * W + 4290)
    chk("    W", W, 60)
    chk("    T", T, 6000)
    chk("    net weight of the ivory, minas", a_t * W + a_m, 4605)
    chk("    drachmas", (a_t * W + a_m) * a_p, 460_500)
    chk("    76 t. 4500 d.", b_t * T + b_d, 460_500)
    chk("    remainder of the fabric, drachmas", F["ca_fab_rest_m"][0] * F["ca_fab_net"][0], 1592.5)
    chk("    obols per drachma", c["ob"], 6)
    chk("(2) 270000 + 461675 + 53882.5", c["three"], 785_557.5)
    chk("    1154 x 6000 + 2852", c["total"], 6_926_852)
    chk("(3) duty", c["duty"], 1_731_713)
    quoted("    万 sesterces", c["duty"] * units(F)["hs_per_drachma"] / 1e4, 173.2, tol=0.05)
    P = pliny(F)
    pct("(4) / 100 million (%)", 100 * c["total"] / P["three"], 6.9)
    pct("    / 50 million (%)", 100 * c["total"] / P["india"], 13.9)
    return c


def bop(F, us):
    P, c, U = pliny(F), cargo(F), units(F)
    chk("Pliny 6.101 (translation): sesterces", P["translation"], 5.5e8)
    chk("    times the cost", P["hundred"], 100)
    chk("Teubner: numeral D", F["lc_drain"][0], 500)
    chk("    multiple", F["pl_100k"][0], 1e5)
    chk("    12.84: miliens centena milia = 1000 x 100,000", 1000 * F["pl_100k"][0], P["three"])
    chk("    D: sesterces", P["india"], 5e7)
    chk("    DL", F["my_app"][0], 550)
    chk("    DL: sesterces", P["india_dl"], 5.5e7)
    chk("    translation / DL", P["translation"] / P["india_dl"], 10)
    assert P["translation"] > P["three"]
    juan = rows().set_index("id")["juan"]
    assert "[12.84]" in juan["pl_100m"] and "6.101" in juan["pl_drain"] and "[33.133]" in juan["pl_100k"]
    gdp = F["sc_gdp18"][0] * GDP_SCALE
    chk("Scheidel: GDP, a little less than (亿)", F["sc_gdp"][0] * GDP_SCALE / 1e8, 200)
    chk("    for computation (亿)", gdp / 1e8, 180)
    chk("    population (万)", F["sc_pop"][0] * POP_SCALE / 1e4, 7000)
    quoted("    per head", gdp / (F["sc_pop"][0] * POP_SCALE), 257, tol=0.5)
    S = scale(F)
    quoted("India 50 million (% of GDP)", S.loc["india", "pct_gdp"], 0.28, tol=0.005)
    quoted("    55 million", S.loc["india_dl", "pct_gdp"], 0.31, tol=0.005)
    quoted("    100 million", S.loc["three", "pct_gdp"], 0.56, tol=0.005)
    quoted("    550 million", S.loc["translation", "pct_gdp"], 3.1, tol=0.05)
    quoted("US current account 2025 (% of GDP)", -us, 3.8, tol=0.05)
    assert S.loc["translation", "pct_gdp"] < -us
    quoted("one ship (% of GDP)", S.loc["ship", "pct_gdp"], 0.04, tol=0.005)
    stock = F["sc_dj"][0] * GDP_SCALE
    chk("money stock (亿)", stock / 1e8, 200)
    chk("    50 million a year (%)", 100 * P["india"] / stock, 0.25)
    chk("    a century (亿)", CENTURY_YEARS * P["india"] / 1e8, 50)
    chk("    share of the stock", CENTURY_YEARS * P["india"] / stock, 1 / 4)
    # ex:india-scale
    cent = P["india"] * P["hundred"]
    chk("ex:india-scale (1) (亿)", cent / 1e8, 50)
    pct("    % of GDP", 100 * cent / gdp, 27.8)
    quoted("(3) per head", cent / (F["sc_pop"][0] * POP_SCALE), 71, tol=0.5)
    pct("    % of GDP per head", S.loc["centiplicato", "pct_gdp"], 27.8)
    # the compare box: 0.3%-0.6%
    assert round(S.loc["india", "pct_gdp"], 1) == 0.3 and round(S.loc["three", "pct_gdp"], 1) == 0.6


def coins(F):
    T = darley_totals()
    D = darley()
    for c, m, v in (("pre-1st", "AR", 7), ("pre-1st", "AV", 6), ("1st", "AR", 4174), ("1st", "AV", 756), ("2nd", "AV", 378),
                    ("3rd", "AV", 12), ("4th", "AV", 1), ("4th", "AE", 616), ("5th", "AV", 84), ("5th", "AE", 101),
                    ("6th", "AV", 21), ("7th", "AV", 2)):
        chk(f"Darley: {c} {m}", T.loc[c, m], v)
    zero = [(c, m) for c in CENTURIES for m in METALS if T.loc[c, m] == 0]
    assert len(zero) == len(CENTURIES) * len(METALS) - 12
    total = T.values.sum()
    chk("    total", total, 6158)
    pct("    1st century (%)", 100 * T.loc["1st"].sum() / total, 80.1)
    chk("    silver", T["AR"].sum(), 4181)
    chk("    gold", T["AV"].sum(), 1260)
    chk("    copper", T["AE"].sum(), 717)
    chk("hoards: Akenpalle", F["da_akenpalle"][0], 1531)
    chk("    Budinatham", F["da_budinatham"][0], 1398)
    chk("    Vellalur", F["da_vellalur"][0], 522)
    assert "Turner (1989)" in rows().set_index("id").loc["da_hoards", "quote"]
    I = finds_1st(D)
    ident = I["silver"].sum()
    chk("1st-century silver, identified", ident, 2497)
    early = I.loc[["Augustus", "Augustus/Tiberius", "Tiberius"], "silver"].sum()
    chk("    Augustus and Tiberius", early, 2479)
    pct("    share (%)", 100 * early / ident, 99.3)
    chk("    Augustus/Tiberius", I.loc["Augustus/Tiberius", "silver"], 233)
    chk("    Nero", I.loc["Nero", "silver"], 4)
    chk("    unidentified", D[(D.century == "1st") & (D.issuer == "Unidentified") & (D.metal == "silver")].coins.sum(), 1675)
    chk("    all 1st-century silver in the table", ident + 1675, 4172)
    chk("gold: Claudius", I.loc["Claudius", "gold"], 215)
    chk("    Nero", I.loc["Nero", "gold"], 193)
    g2 = D[(D.century == "2nd") & (D.metal == "gold")].set_index("issuer").coins
    chk("    Hadrian", g2["Hadrian"], 100)
    chk("    Antoninus Pius", g2["Antoninus Pius"], 182)
    chk("2nd-century gold: table", g2.sum(), 357)
    chk("    note", T.loc["2nd", "AV"], 378)
    # ex:india-finds
    P, U = pliny(F), units(F)
    den = P["india"] / U["hs_per_denarius"]
    chk("ex:india-finds (2) denarii (万)", den / 1e4, 1250)
    chk("    aurei (万)", den / U["denarii_per_aureus"] / 1e4, 50)
    quoted("    4174 / a year's flow (%)", 100 * T.loc["1st", "AR"] / den, 0.033, tol=0.0005)


def debate(F, Y):
    c, P = cargo(F), pliny(F)
    chk("Tacitus: Tiberius's letter, AD", Y["ta_jewels"], 22)
    chk("Raschke", F["da_raschke_ref"][0], 1978)
    chk("Young", F["da_young_ref"][0], 2001)
    chk("    Pliny's figure", F["da_young"][0], P["three"])
    chk("    tax (%)", F["da_young2"][0], 25)
    duty = P["three"] * F["da_young2"][0] / 100
    chk("    duty on 100 million (万)", duty / 1e4, 2500)
    quoted("    Hermapollon duties", duty / c["duty"], 14, tol=0.5)


def china(F, Y):
    assert Y["hhs_ganying"] == ERA["永元"] + F["hhs_ganying"][0] - 1
    chk("永元九年 (AD)", Y["hhs_ganying"], 97)
    chk("    months with a good wind", F["hhs_ganying"][1], 3)
    chk("    years with a slow wind", F["hhs_twoyears"][0], 2)
    chk("    years of grain", F["hhs_twoyears"][1], 3)
    assert Y["hhs_envoy"] == ERA["延熹"] + 9 - 1
    chk("延熹九年 (AD)", Y["hhs_envoy"], 166)
    chk("银钱十当金钱一", F["hhs_coins"][0], 10)
    chk("    against denarii per aureus", F["pl_aureus"][0], 25)
    assert Y["hs_wangmang"] == ERA["元始"]


def test(F, Y):
    P, c = pliny(F), cargo(F)
    chk("India / three regions (D)", P["india"] / P["three"], 0.5)
    chk("    (DL)", P["india_dl"] / P["three"], 0.55)
    fleet = F["st_120"][0] * c["total"]
    quoted("120 Hermapollons (亿)", fleet / 1e8, 8.3, tol=0.05)
    quoted("    x 100 million", fleet / P["three"], 8.3, tol=0.05)
    quoted("    x 50 million", fleet / P["india"], 16.6, tol=0.05)
    quoted("100 million in ships", P["three"] / c["total"], 14.4, tol=0.05)
    quoted("50 million in ships", P["india"] / c["total"], 7.2, tol=0.05)
    W = c["W"]
    chk("Casson n. 29: talents", F["ca_ivfab"][0], 92)
    chk("    drachmas", F["ca_ivfab"][1], 528_775)
    gross = F["ca_ivory_w"][0] * W + F["ca_ivory_w"][1] + F["ca_fab_gross"][0] * W + F["ca_fab_gross"][1]
    quoted("    gross weight (talents)", gross / W, 92, tol=0.1)
    chk("    the papyrus's values", c["ivory"] + c["fabric"], 515_557.5)
    at_gross = (F["ca_ivory_w"][0] * W + F["ca_ivory_w"][1]) * F["ca_ivory_net"][2] + \
               (F["ca_fab_gross"][0] * W + F["ca_fab_gross"][1]) * F["ca_fab_net"][0]
    chk("    at the gross weights", at_gross, 528_757.5)
    chk("    difference", F["ca_ivfab"][1] - at_gross, 17.5)
    # the deeper box
    lic = meta()["license"]
    for k, y in TRANSLATIONS_19C.items():
        assert k in lic, k
    n19 = sum(1800 <= y < 1900 for y in TRANSLATIONS_19C.values())
    chk("translations of the 19th century", n19, 4)
    chk("    of", len(TRANSLATIONS_19C), 5)
    notes = meta()["notes"]
    for era, y in ERA.items():
        assert f"{era}元年 = AD {y}" in notes, era
    chk("元始元年", ERA["元始"], 1)
    chk("永元元年", ERA["永元"], 89)
    chk("延熹元年", ERA["延熹"], 158)
    chk("Arthashastra: from the n-th century BC", (-F["fl_date"][0] - 1) // 100 + 1, 4)
    chk("    to the n-th century AD", (F["fr_sastra"][1] - 1) // 100 + 1, 3)


def takeaways_and_selfcheck(F, us):
    R, c, P = rates(F), cargo(F), pliny(F)
    chk("takeaways: days", sum(route(F)["rome"].values()), 94)
    chk("    Han, days out at least", sum(route(F)["han_out"].values()), 360)
    # selfcheck
    chk("SC1: Berenice to Muziris", F["pl_ocelis"][0] + F["pl_muziris"][0], 70)
    quoted("SC2: forest a year (%)", 100 * R.loc["forest", "annual"], 120, tol=1e-9)
    quoted("    p", R.loc["forest", "p"], 0.52, tol=0.005)
    chk("SC3: ivory after the duty", c["ivory"] * (1 - F["ca_quarter"][0]), 346_256.25)
    chk("SC4: 100 million / 200 亿 (%)", 100 * P["three"] / SELF["gdp"], 0.5)
    chk("    50 million (%)", 100 * P["india"] / SELF["gdp"], 0.25)
    chk("SC5: coins as goods: CA", SELF["coins"] - SELF["coins"], 0)
    chk("    as an asset: CA (万)", -SELF["coins"] / 1e4, -100)


def main():
    df = rows()
    F, Y = facts(), years()
    check_readings(df)
    check_text(df)
    U = units(F)
    us = us_ca_2025()
    opening(F, U)
    world(F, Y)
    ex_route(F)
    artha(F, Y, greek(), qinhan_years())
    interest(F)
    cargo_section(F)
    bop(F, us)
    coins(F)
    debate(F, Y)
    china(F, Y)
    test(F, Y)
    takeaways_and_selfcheck(F, us)
    print("all Chapter 9 checks passed")


if __name__ == "__main__":
    main()
