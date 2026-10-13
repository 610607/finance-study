"""Chapter 17 (德川日本与清代中国：东亚的前现代市场): every number quoted in zh/ch17_tokugawa.tex.

    python3 checks/check_ch17.py

Inputs are the snapshots toku_facts (quotations from Suzuki 2021, Schaede 1989, Takatsuki 2007, Irigoin 2013, Atwell
2008, 清史稿 and the two 皇朝经世文续编; checked by data/fetch/verify_web_quotes.py and data/fetch/verify_quotes.py;
Suzuki's Tables 1-5 were read on the page images, see the snapshot's metadata), gpih_iwahashi_rice (Iwahashi 1981,
annual rice prices in Osaka and Edo) and gpih_gamble_beijing (Gamble 1943, wages and the cash/tael rate near Beijing),
both written by data/fetch/gpih_east_asia.py, and, for the French devaluation of 1720, merc_facts (Chapter 16).
The figure module figsrc/fig_ch17.py imports the functions defined here.

Models (the chapter's key equations):
    tax paid in rice            x = T e / p                                          (eq:toku-burden)
    one good, two moneys        P_a = e P_b,  g_Pa ~ g_e + g_Pb                       (eq:toku-twoprice)
    content theory              P = q / c,  pi ~ g_q - g_c                            (eq:toku-content)
    profit from a recoinage     S = N (c_old / c_new - 1 - phi)                       (eq:toku-seign; eq:medieval-seigniorage)
    short hedge                 V_T = Q S_T + Q (F_0 - F_T) = Q F_0 + Q (S_T - F_T);
                                change in margin / margin = dF / (m F_0)              (eq:toku-hedge)
Units: 1 ryo = 4 bu = 16 shu; 1 kan = 1,000 momme; 1 两 (tael) = 10 钱 = 100 分; 1 石 (koku) = 10 斗;
Qing reign years are converted with reign() below (元年 = the first year).
"""
from __future__ import annotations

import math

import pandas as pd

from common import load_snapshot, quoted

BU_PER_RYO, SHU_PER_BU = 4, 4
MOMME_PER_KAN = 1000
QIAN_PER_TAEL, FEN_PER_QIAN = 10, 10
DOU_PER_SHI = 10
FIXED_RATE = 60            # momme per ryo: the Edo commodity market's rate after 1700 (suz_1700)

# Qing reigns: the Gregorian year in which each 元年 falls
REIGN = {"顺治": 1644, "康熙": 1662, "雍正": 1723, "乾隆": 1736, "道光": 1821, "咸丰": 1851}
STEMS, BRANCHES = "甲乙丙丁戊己庚辛壬癸", "子丑寅卯辰巳午未申酉戌亥"

# Teaching inputs stated in the text
DOMAIN_KOKU = 10_000       # sec:toku-koku: a domain sells 10,000 koku in Osaka
HEDGE = dict(F0=60.0, Q=100.0, m=1 / 3, drop=0.10, F_basis=55.0)   # ex:toku-hedge
GRAIN_HIGH = 750           # ex:toku-burden (2): 包世臣's 七百数十文 taken as 750
DOJIMA_OPEN, SMITH = 1730, 1776

# The coins in use in each period of tab:toku-test: (key, first year, last year); the base period comes first
EDO_REGIMES = [("keicho", 1685, 1694), ("genroku", 1696, 1710), ("kenji", 1711, 1718), ("kyoho", 1719, 1736),
               ("genbun", 1737, 1750)]
OSAKA_REGIMES = [("genroku", 1701, 1705), ("futatsu", 1706, 1710), ("yotsu", 1711, 1718), ("kyoho", 1719, 1736),
                 ("genbun", 1737, 1750)]
GAMBLE_BASE, GAMBLE_LATE = (1807, 1813), (1845, 1850)


def _snapshot_facts():
    df, _ = load_snapshot("toku_facts", dtype={"value": str})
    return df


def facts() -> dict[str, list[float]]:
    """id -> list of the numbers in the value column (several values are separated by ';')."""
    out = {}
    for _, r in _snapshot_facts().iterrows():
        v = r["value"]
        if isinstance(v, str) and v.strip():
            out[r["id"]] = [float(x) for x in v.split(";")]
    return out


def years() -> dict[str, int]:
    """id -> the year column."""
    df = _snapshot_facts()
    return dict(zip(df["id"], df["year"].astype(int)))


def quotes() -> dict[str, str]:
    """id -> verbatim quotation."""
    df = _snapshot_facts()
    return dict(zip(df["id"], df["quote"].fillna("")))


def said(Q: dict[str, str], qid: str, *tokens: str) -> None:
    """Assert that each token (a number as printed in the source) occurs in the quotation qid."""
    missing = [t for t in tokens if t not in Q[qid]]
    print(f"{'ok ' if not missing else 'BAD'} {qid}: quotation contains {', '.join(tokens)}")
    if missing:
        raise AssertionError(f"{qid}: {missing} not in the quotation")


def reign(era: str, n: int) -> int:
    return REIGN[era] + n - 1


def ganzhi(year: int) -> str:
    return STEMS[(year - 4) % 10] + BRANCHES[(year - 4) % 12]


# --- data ------------------------------------------------------------------
def rice() -> pd.DataFrame:
    """Iwahashi (1981) via GPIH: Osaka (monme of silver per koku, Dojima market price of Higo rice) and Edo (ryo of
    gold per koku, the shogunate's price), indexed by year."""
    df, _ = load_snapshot("gpih_iwahashi_rice")
    return df.set_index("year")


def gamble() -> pd.DataFrame:
    """Gamble (1943) via GPIH: unskilled daily wage in copper cash, cash per tael, indexed by year (to 1853: the chapter
    does not use the years of the large coins)."""
    df, _ = load_snapshot("gpih_gamble_beijing")
    return df.set_index("year").loc[:1853]


def koban(F) -> dict[str, dict[str, float]]:
    """Suzuki (2021) Table 2: gold per cent, weight (g), pure gold (g) per ryo and mintage (ryo)."""
    out = {}
    for k in ("keicho", "genroku", "kenji", "shotoku", "kyoho", "genbun"):
        v = F[f"suz_t2_{k}"]
        out[k] = dict(gold=v[0], weight=v[1], pure=v[0] * v[1] / 100, mintage=v[2])
    return out


def chogin(F) -> dict[str, dict[str, float]]:
    """Suzuki (2021) Table 3: silver per cent and mintage (kan)."""
    keys = ("keicho", "genroku", "futatsu", "eiji", "mitsu", "yotsu", "kyoho", "genbun")
    return {k: dict(silver=F[f"suz_t3_{k}"][0], mintage=F[f"suz_t3_{k}"][1]) for k in keys}


def mean(s: pd.Series, a: int, b: int) -> float:
    return float(s.loc[a:b].dropna().mean())


# --- models ----------------------------------------------------------------
def burden(T: float, e: float, p: float) -> float:
    """eq:toku-burden: rice (koku) sold to pay T taels at e cash per tael and p cash per koku."""
    return T * e / p


def content_price(q: float, c: float) -> float:
    """eq:toku-content."""
    return q / c


def seigniorage(N: float, c_old: float, c_new: float, phi: float) -> float:
    """eq:toku-seign."""
    return N * (c_old / c_new - 1 - phi)


def seign_rate(c_ratio: float, phi: float) -> float:
    """1 - MP/ME with ME = c_old/c_new and MP = 1 + phi (eq:medieval-seigniorage)."""
    return 1 - (1 + phi) / c_ratio


def hedge(Q: float, F0: float, ST: float, FT: float) -> dict[str, float]:
    """eq:toku-hedge for a holder of Q koku of rice bills who sells Q koku of futures at F0."""
    bills, fut = Q * ST, Q * (F0 - FT)
    return dict(bills=bills, futures=fut, total=bills + fut, locked=Q * F0 + Q * (ST - FT))


def margin_shock(dF_over_F: float, m: float) -> float:
    """eq:toku-hedge: change in the margin account as a share of the margin."""
    return dF_over_F / m


def edo_test(F, R=None) -> pd.DataFrame:
    """tab:toku-test, Edo: the content prediction from the pure gold per ryo of the koban in use."""
    R = rice() if R is None else R
    K = koban(F)
    rows = [dict(coin=k, start=a, end=b, c=K[k]["pure"], actual=mean(R["edo_ryo_per_koku"], a, b))
            for k, a, b in EDO_REGIMES]
    t = pd.DataFrame(rows).set_index("coin")
    base = t.iloc[0]
    t["pred"] = base["actual"] * base["c"] / t["c"]
    return t


def osaka_test(F, R=None) -> pd.DataFrame:
    """tab:toku-test, Osaka: the content prediction from the fineness of the chogin of each period."""
    R = rice() if R is None else R
    C = chogin(F)
    rows = [dict(coin=k, start=a, end=b, c=C[k]["silver"], actual=mean(R["osaka_monme_per_koku"], a, b))
            for k, a, b in OSAKA_REGIMES]
    t = pd.DataFrame(rows).set_index("coin")
    base = t.iloc[0]
    t["pred"] = base["actual"] * base["c"] / t["c"]
    return t


def step(t: pd.DataFrame, years) -> pd.Series:
    """The prediction of edo_test/osaka_test as an annual step function (years before the first period take the base
    prediction, years in a gap take the next period's)."""
    out = {}
    for y in years:
        later = t[t["end"] >= y]
        out[y] = float(later["pred"].iloc[0]) if len(later) else float(t["pred"].iloc[-1])
    return pd.Series(out)


def wages(G=None) -> dict[str, float]:
    """Averages of the copper wage and the cash/tael rate in the base (1807-1813) and late (1845-1850) years present
    in the workbook; the silver wage is the average wage over the average rate."""
    G = gamble() if G is None else G
    d = {}
    for name, (a, b) in (("base", GAMBLE_BASE), ("late", GAMBLE_LATE)):
        w, e = mean(G["wage_cash_per_day"], a, b), mean(G["cash_per_tael"], a, b)
        d[f"w_{name}"], d[f"e_{name}"], d[f"ws_{name}"] = w, e, w / e
    return d


def wage_index(G=None) -> pd.DataFrame:
    """fig:qing_cash (b): copper and silver wages, base years = 100."""
    G = gamble() if G is None else G
    W = wages(G)
    ws = G["wage_cash_per_day"] / G["cash_per_tael"]
    return pd.DataFrame({"copper": 100 * G["wage_cash_per_day"] / W["w_base"], "silver": 100 * ws / W["ws_base"]})


def contemporaries(F) -> list[tuple[int, float, str]]:
    """The rates said by contemporaries that fig:qing_cash (a) marks: (year, cash per tael, who)."""
    lo, hi = 2200, 2300                                   # 刘良驹: 外省 二千二三百文
    return [(reign("道光", 18), F["wei_1600"][0], "黄爵滋"),
            (reign("道光", 19), 1000 / 0.61, "包世臣"),
            (1845, F["liu_rate"][0], "刘良驹（京中）"),
            (1845, (lo + hi) / 2, "刘良驹（外省）")]


def cagr(a: float, b: float, years: int) -> float:
    return (b / a) ** (1 / years) - 1


# --- sections --------------------------------------------------------------
def intro(F, R):
    print("\n== opening ==")
    K = koban(F)
    quoted("Genroku debasement begins", F["suz_1695"][0], 1695, tol=0)
    quoted("koban weight, Keicho (g)", K["keicho"]["weight"], 17.85, tol=0)
    quoted("  Genroku (g)", K["genroku"]["weight"], 17.85, tol=0)
    quoted("gold, Keicho (%)", K["keicho"]["gold"], 84.291, tol=0)
    quoted("  Genroku (%)", K["genroku"]["gold"], 57.366, tol=0)
    fall = 1 - K["genroku"]["pure"] / K["keicho"]["pure"]
    quoted("pure gold per ryo fell (%) -- 'nearly a third'", 100 * fall, 31.94, tol=0.005)
    assert 0.30 < fall < 1 / 3
    e = R["edo_ryo_per_koku"]
    a, b = mean(e, 1685, 1694), mean(e, 1696, 1710)
    quoted("Edo rice 1685-1694 (ryo/koku)", a, 0.79, tol=0.005)
    quoted("  1696-1710", b, 1.15, tol=0.005)
    quoted("  rise (%)", 100 * (b / a - 1), 46, tol=0.5)
    print("Zeng Guofan: 3000 cash a koku; 1000 then 2000 cash a tael; 3 then 1.5 taels (see from_quotes)")
    quoted("  3000 / 1000 (taels)", F["zeng_rice"][0] / 1000, F["zeng_then"][0], tol=1e-9)
    quoted("  3000 / 2000 (taels)", F["zeng_rice"][0] / F["zeng_now"][0], 1.5, tol=1e-9)
    quoted("Dojima acknowledged", F["sch_1730"][0], 1730, tol=0)


def world(F):
    print("\n== sec:toku-world ==")
    pop, farm, war, merch = F["sch_pop"]
    quoted("population (m)", pop, 30, tol=0)
    quoted("  farmers (%)", farm, 87, tol=0)
    quoted("  warriors (%)", war, 5, tol=0)
    quoted("  merchants and artisans (%)", merch, 8, tol=0)
    assert farm + war + merch == 100 and F["sch_pop8"][0] == merch
    p1609, y, p1750 = F["sch_osaka"]
    quoted("Osaka 1609 (10k)", p1609 / 1e4, 20, tol=0)
    quoted("  1750s (10k), 'doubled'", p1750 / 1e4, 40, tol=0)
    assert y == 1609 and p1750 == 2 * p1609
    quoted("1 koku = 10 to", DOU_PER_SHI, 10, tol=0)
    quoted("  = litres", F["sch_koku"][0], 180, tol=0)
    n73, y73, n30, y30 = F["sch_warehouses"]
    quoted("warehouses 1673", n73, 91, tol=0)
    quoted("  1730", n30, 124, tol=0)
    assert (y73, y30) == (1673, 1730)
    bu, shu = F["suz_t1_ryo"]
    quoted("1 ryo = bu", bu, BU_PER_RYO, tol=0)
    quoted("  = shu", shu, BU_PER_RYO * SHU_PER_BU, tol=0)
    quoted("1 kan = momme", F["suz_t1_kan"][0], MOMME_PER_KAN, tol=0)
    quoted("one chogin weighs (g)", F["suz_chogin"][0], 161.25, tol=0)
    quoted("1 kan mon = mon", F["suz_t1_mon"][0], 1000, tol=0)
    print("\n-- Qing --")
    quoted("顺治二年", reign("顺治", 2), 1645, tol=0)
    quoted("  7 cash per fen -> per tael", F["qsg_seven"][0] * QIAN_PER_TAEL * FEN_PER_QIAN, 700, tol=0)
    quoted("  then 10 per fen -> per tael", F["qsg_ten"][0] * QIAN_PER_TAEL * FEN_PER_QIAN, 1000, tol=0)
    quoted("顺治十年", reign("顺治", 10), 1653, tol=0)
    quoted("  1000 cash a tael", F["qsg_1000"][0], 1000, tol=0)
    print("  徵银七钱三: seven parts silver, three parts cash (70/30)")
    quoted("Irigoin: about (cash per tael)", F["ir_1000"][0], 1000, tol=0)
    quoted("Kangxi: no less than", F["qsg_kangxi_floor"][0], 1000, tol=0)
    quoted("  last years: 880", F["qsg_kangxi_880"][0], 880, tol=0)
    quoted("  to 770", F["qsg_kangxi_770"][0], 770, tol=0)
    quoted("乾隆十三年", reign("乾隆", 13), 1748, tol=0)
    quoted("  Beijing before then (cash)", F["qsg_qianlong_800"][0], 800, tol=0)
    quoted("Wu Jiabin: since Yongzheng, about (cash)", F["wu_1100"][0], 1100, tol=0)
    quoted("  '几百年' since 雍正元年 to 1845 (years)", 1845 - REIGN["雍正"], 122, tol=0)


def koku(F, R):
    print("\n== sec:toku-koku ==")
    quoted("Bao Shichen: zhenggong (10k taels)", F["bao_zhenggong"][0] / 1e4, 4000, tol=0)
    o = R["osaka_monme_per_koku"]
    for y, kan in ((1721, 721), (1730, 310)):
        quoted(f"10,000 koku in Osaka {y} (kan)", DOMAIN_KOKU * o.loc[y] / MOMME_PER_KAN, kan, tol=1e-6)
    quoted("  fall (%)", 100 * (1 - o.loc[1730] / o.loc[1721]), 57, tol=0.5)
    a, b = F["sch_kyoho"]
    quoted("Kyoho era from", a, 1716, tol=0)
    quoted("  to", b, 1735, tol=0)
    quoted("Zeng: Jiangsu full grain tribute until 道光十五年", reign("道光", 15), 1835, tol=0)
    quoted("  shortfalls since 道光十六年", reign("道光", F["zeng_jiangsu"][0]), 1836, tol=0)
    print("\n-- the two prices --")
    lo, hi = F["suz_4080"]
    quoted("Suzuki's example: Osaka (momme/ryo)", lo, 40, tol=0)
    quoted("  Edo", hi, 80, tol=0)
    quoted("  'twice the price'", hi / lo, 2, tol=0)
    quoted("before 1695: momme per ryo", F["suz_stable60"][0], FIXED_RATE, tol=0)
    y, r, _ = F["suz_1700"]
    quoted("fixed rate law", y, 1700, tol=0)
    quoted("  momme per ryo", r, FIXED_RATE, tol=0)
    quoted("Tokumi Donya: guilds", F["suz_guilds"][0], 10, tol=0)
    # ex:toku-eastwest
    quoted("ex (1): ryo for 40 momme at 40", 40 / lo, 1, tol=0)
    quoted("  worth in Edo (momme)", 40 / lo * hi, 80, tol=0)
    w, east = F["suz_1718rate"]
    quoted("ex (2): West Nov 1718 (momme/ryo)", w, 45, tol=0)
    quoted("  East", east, FIXED_RATE, tol=0)
    quoted("  45 momme in ryo", 45 / w, 1, tol=0)
    quoted("  Edo tag at 60 (momme)", 45 / w * east, 60, tol=0)
    quoted("  mark-up (%)", 100 * (east / w - 1), 33, tol=0.5)
    quoted("ex (3): e_W = 60: ratio", FIXED_RATE / 60, 1, tol=0)
    quoted("Echigoya's table", F["suz_60mmt"][0], 1719, tol=0)


def genroku(F, R):
    print("\n== sec:toku-genroku: tab:toku-coins ==")
    K, C = koban(F), chogin(F)
    for k, g, wt, p, m in (("keicho", 84.291, 17.85, 15.05, 14_727_055), ("genroku", 57.366, 17.85, 10.24, 13_936_220),
                           ("kenji", 84.291, 9.38, 7.91, 11_515_500), ("shotoku", 84.291, 17.85, 15.05, 213_500),
                           ("kyoho", 86.785, 17.85, 15.49, 8_280_000), ("genbun", 65.714, 13.13, 8.63, 17_435_711)):
        quoted(f"{k}: gold (%)", K[k]["gold"], g, tol=0)
        quoted(f"  weight (g)", K[k]["weight"], wt, tol=0)
        quoted(f"  pure gold (g)", K[k]["pure"], p, tol=0.005)
        quoted(f"  mintage (ryo)", K[k]["mintage"], m, tol=0)
    for k, s, m in (("keicho", 80, 1_200_000), ("genroku", 64, 405_850), ("futatsu", 50, 278_130), ("eiji", 40, 5_836),
                    ("mitsu", 32, 370_487), ("yotsu", 20, 401_240), ("kyoho", 80, 331_420), ("genbun", 46, 525_465.9)):
        quoted(f"{k} silver: fineness (%)", C[k]["silver"], s, tol=0)
        quoted(f"  mintage (kan)", C[k]["mintage"], m, tol=0)
    quoted("Kyoho koban modelled on the Sandaime Keicho: gold (%)", F["suz_t2_sandaime"][0], K["kyoho"]["gold"], tol=0)

    print("\n== content theory ==")
    r = K["keicho"]["pure"] / K["genroku"]["pure"]
    quoted("15.05 / 10.24", r, 1.469, tol=0.0005)
    quoted("  price rise (%)", 100 * (r - 1), 46.9, tol=0.05)
    quoted("silver 80 / 64", C["keicho"]["silver"] / C["genroku"]["silver"], 1.25, tol=0)
    quoted("Edo rice rise (%)", 100 * (mean(R["edo_ryo_per_koku"], 1696, 1710) / mean(R["edo_ryo_per_koku"], 1685, 1694) - 1),
           46, tol=0.5)

    print("\n== seigniorage ==")
    prem, per, until = F["suz_premium"]
    quoted("premium (ryo per 100)", prem, 1, tol=0)
    assert per == 100 and until == 1707
    phi = prem / per
    old_g, old_s, new_g, new_s = F["suz_arai"]
    total_g, total_s = F["suz_officer"]
    ratio_g, ratio_s = new_g / old_g, new_s / old_s
    quoted("ex (1): new ryo per old ryo", ratio_g, 1.500, tol=0.0005)
    quoted("  by content", r, 1.469, tol=0.0005)
    quoted("  silver", ratio_s, 1.243, tol=0.0005)
    quoted("  silver by content", C["keicho"]["silver"] / C["genroku"]["silver"], 1.25, tol=0)
    S = seigniorage(old_g, 1, 1 / ratio_g, phi)
    quoted("ex (2): S (10k ryo)", S / 1e4, 432, tol=0.5)
    assert math.isclose(S, new_g - old_g * (1 + phi))
    quoted("  rate (%)", 100 * seign_rate(ratio_g, phi), 32.7, tol=0.05)
    quoted("  rate by content (%)", 100 * seign_rate(r, phi), 31.3, tol=0.05)
    quoted("  per 100 ryo collected: kept", 100 * (ratio_g - 1 - phi), 49, tol=0.05)
    quoted("  paid out", 100 * (1 + phi), 101, tol=1e-9)
    quoted("ex (3): gold reminted (%)", 100 * old_g / total_g, 44, tol=0.5)
    quoted("  silver (%)", 100 * old_s / total_s, 72, tol=0.5)
    left = total_g - old_g
    quoted("  gold not reminted (10k ryo)", left / 1e4, 1117.6, tol=0.05)
    quoted("  all hoarded: circulating (10k ryo)", new_g / 1e4, 1323.7, tol=0.05)
    quoted("    change (%)", 100 * (new_g / total_g - 1), -34, tol=0.5)
    quoted("  all circulating (10k ryo)", (new_g + left) / 1e4, 2441.2, tol=0.05)
    quoted("    change (%)", 100 * ((new_g + left) / total_g - 1), 22, tol=0.5)

    print("\n== debasement after debasement ==")
    Y = years()
    for k, y, s in (("futatsu", 1706, 50), ("eiji", 1710, 40), ("mitsu", 1710, 32), ("yotsu", 1711, 20)):
        quoted(f"{k}: first minted", Y[f"suz_t3_{k}"], y, tol=0)
        quoted(f"  fineness (%)", C[k]["silver"], s, tol=0)
    quoted("Kenji koban: gold (%) = Keicho's", K["kenji"]["gold"], K["keicho"]["gold"], tol=0)

    print("\n== Arai ==")
    quoted("Shotoku koban minted", Y["suz_t2_shotoku"], 1714, tol=0)
    quoted("Kyohogin from", Y["suz_t3_kyoho"], 1714, tol=0)
    quoted("  fineness (%)", C["kyoho"]["silver"], 80, tol=0)
    quoted("Kyoho koban from", Y["suz_t2_kyoho"], 1716, tol=0)
    print("Keicho koban back about 1716, nine-tenths of the kobans (suz_1716; see from_quotes)")
    quoted("1714 law: Keicho/Kyoho 1 = Kenji", F["suz_t4_1714"][1], 2, tol=0)
    quoted("  Genroku 1 = Kenji", F["suz_t4_1714"][0], 1, tol=0)
    old, new = F["suz_1500"]
    quoted("before: Keichogin bought (momme)", old, 1000, tol=0)
    quoted("  for Yotsuhogin", new, 1500, tol=0)
    quoted("after 1714 (momme)", F["suz_2000"][0], 2000, tol=0)
    quoted("by fineness: 1000 x 80/20", 1000 * C["keicho"]["silver"] / C["yotsu"]["silver"], F["suz_4000"][0], tol=0)
    quoted("  shogunate bore (momme)", F["suz_4000"][0] - F["suz_2000"][0], F["suz_defray"][0], tol=0)
    a, b, _ = F["suz_t5_1718"]
    quoted("1718: Keichogin 10,000", a, 10_000, tol=0)
    quoted("  = Yotsuhogin", b, 40_000, tol=0)
    assert b / a == C["keicho"]["silver"] / C["yotsu"]["silver"]
    quoted("Genroku koban banned", F["suz_t4_1718"][0], 1718, tol=0)
    quoted("Kenji koban banned", F["suz_t4_1720"][0], 1720, tol=0)
    o = R["osaka_monme_per_koku"]
    quoted("Osaka rice 1718", o.loc[1718], 127.9, tol=0)
    quoted("  1719", o.loc[1719], 40.6, tol=0)

    print("\n== Genbun ==")
    g = 1 - K["genbun"]["pure"] / K["kyoho"]["pure"]
    gk, gg = F["suz_genbun_gold"]
    quoted("Suzuki: Kyoho -> Genbun pure gold fell (%)", gk, 44.34, tol=0)
    quoted("  Genroku (%)", gg, 31.91, tol=0)
    sk, sg = F["suz_genbun_silver"]
    quoted("silver Kyoho -> Genbun (%)", sk, 100 * (1 - C["genbun"]["silver"] / C["kyoho"]["silver"]), tol=1e-9)
    quoted("  Keicho -> Genroku (%)", sg, 100 * (1 - C["genroku"]["silver"] / C["keicho"]["silver"]), tol=1e-9)
    old, new = F["suz_165"]
    quoted("mint: 100 old ryo", old, 100, tol=0)
    quoted("  for new", new, 165, tol=0)
    assert F["suz_t4_1736"] == [100, 100, 65]
    o_s, n_s = F["suz_15000"]
    quoted("silver: 10,000 old momme", o_s, 10_000, tol=0)
    quoted("  for new", n_s, 15_000, tol=0)
    quoted("Tokumi Donya complain (28 May)", F["suz_may28"][0], 1736, tol=0)
    quoted("Echigoya's sale from 15 June", F["suz_sale_date"][0], 1736, tol=0)
    # ex:toku-genbun
    dbl, orig, cut, ryo = F["suz_sale"]
    quoted("doubled price (momme)", dbl, 120, tol=0)
    quoted("  original (momme) = 1 ryo", orig, FIXED_RATE, tol=0)
    quoted("  reduced to (momme)", cut, 48, tol=0)
    quoted("  in ryo", cut / FIXED_RATE, ryo, tol=1e-9)
    quoted("  20% off", 100 * (1 - ryo), 20, tol=1e-9)
    quoted("  0.8 ryo = 3 bu + 3 momme (momme)", (ryo * BU_PER_RYO - 3) / BU_PER_RYO * FIXED_RATE, 3, tol=1e-9)
    m_new, r_new = F["suz_sale_new"]
    quoted("with new kobans (momme)", m_new, 79.2, tol=0)
    quoted("  in ryo", m_new / FIXED_RATE, r_new, tol=1e-9)
    p_new, p_old = F["suz_sale_gold"]
    quoted("pure gold, new koban (g)", p_new, 8.581726, tol=0)
    quoted("pure gold, 0.8 old ryo (g)", p_old, 11.9759232, tol=0)
    quoted("ex (1): 1.32 / 0.8", r_new / ryo, 1.65, tol=1e-9)
    assert math.isclose(r_new / ryo, new / old)
    rr = K["keicho"]["pure"] / K["genbun"]["pure"]
    quoted("ex (2): 15.05 / 8.63", rr, 1.744, tol=0.0005)
    quoted("  seigniorage (%)", 100 * seign_rate(rr, 0.65), 5.4, tol=0.05)
    rk = K["kyoho"]["pure"] / K["genbun"]["pure"]
    quoted("  by the Kyoho koban: ratio", rk, 1.795, tol=0.0005)
    quoted("  seigniorage (%)", 100 * seign_rate(rk, 0.65), 8.1, tol=0.05)
    quoted("ex (3): 1.32 x 8.58 (g)", r_new * p_new, 11.33, tol=0.005)
    quoted("  old pays more by (%)", 100 * (p_old / (r_new * p_new) - 1), 5.7, tol=0.05)
    quoted("  old payment (g)", p_old, 11.98, tol=0.005)
    quoted("  Suzuki's numbers: seigniorage (%)", 100 * (1 - r_new * p_new / p_old), 5.4, tol=0.05)
    return g


def dojima(F, R):
    print("\n== sec:toku-dojima ==")
    quoted("bills up to (months)", F["sch_18months"][0], 18, tol=0)
    quoted("standardized at (koku), about 1700", F["sch_10koku"][0], 10, tol=0)
    bills, stock = F["sch_1749"]
    quoted("1749 bills (bales)", bills / 1e4, 11, tol=0)
    quoted("  inventory (bales)", stock / 1e4, 3, tol=0)
    quoted("  ratio ('almost four times')", bills / stock, 3.67, tol=0.005)
    assert 3.5 < bills / stock < F["sch_four"][0]
    quoted("unbacked bills banned", F["sch_1652"][0], 1652, tol=0)
    y, d = F["sch_1660"]
    quoted("trading banned", y, 1660, tol=0)
    quoted("  term (days)", d, 30, tol=0)
    y, d = F["sch_1663"]
    quoted("shortened", y, 1663, tol=0)
    quoted("  to (days)", d, 10, tol=0)
    quoted("  merchants paid within (days)", F["sch_10days_eff"][0], 10, tol=0)
    print("\n-- case --")
    quoted("move to Dojima", F["sch_dojima_1688"][0], 1688, tol=0)
    quoted("Yodoya moves", F["sch_yodoya_1697"][0], 1697, tol=0)
    quoted("Yodoya closed", F["sch_1705"][0], 1705, tol=0)
    a, b = F["sch_1728"]
    quoted("prolonged transactions", a, 1728, tol=0)
    quoted("only acknowledged futures exchange", b, 1730, tol=0)
    quoted("decree item", F["sch_decree1"][0], 1, tol=0)
    quoted("  clearinghouses", F["sch_decree3"][0], 50, tol=0)
    quoted("'twenty-odd years later' (1705 -> 1728)", 1728 - 1705, 23, tol=0)
    print("\n-- structure --")
    n1, y1, n2, y2, n3, y3 = F["sch_licences"]
    quoted("licences 1731", n1, 500, tol=0)
    quoted("  April 1732", n2, 500, tol=0)
    quoted("  November 1732", n3, 300, tol=0)
    assert (y1, y2, y3) == (1731, 1732, 1732)
    quoted("  total", n1 + n2 + n3, F["sch_1300"][0], tol=0)
    a, y1, b, y2 = F["sch_clearing_1731"]
    quoted("clearinghouses 1731", a, 50, tol=0)
    quoted("  more in 1746", b, 10, tol=0)
    assert (y1, y2) == (1731, 1746)
    sixty, four = F["sch_clearing_four"]
    quoted("original houses", sixty, a + b, tol=0)
    quoted("  survived", four, 4, tol=0)
    pay, bal, days = F["sch_tonya30"]
    quoted("tonya pays (%)", pay, 30, tol=0)
    quoted("  balance (%)", bal, 70, tol=0)
    assert pay + bal == 100
    quoted("  within (days)", days, 30, tol=0)
    quoted("trading periods a year", F["sch_periods"][0], 3, tol=0)
    quoted("closed between periods (days)", F["sch_rollover"][0], 10, tol=0)
    quoted("contract (koku)", F["sch_100koku"][0], 100, tol=0)
    mai, p, koku_, p2 = F["sch_3mai"]
    quoted("'3 mai for 23' = koku", mai * F["sch_100koku"][0], koku_, tol=0)
    assert p == p2 == 23
    print("  margin at most one third (sch_third)")
    quoted("settlement every (days)", F["sch_tenday"][0], 10, tol=0)
    quoted("cash or rice settlement from", F["sch_1737"][0], 1737, tol=0)
    print("\n-- hedge --")
    quoted("margin around (%)", F["sch_margin30"][0], 30, tol=0)
    lo, hi, y = F["sch_margin1770"]
    quoted("1770 margin (momme/koku)", lo, 1, tol=0)
    quoted("  to", hi, 2, tol=0)
    a, b, c, pct = F["sch_margin5"]
    quoted("  per contract (momme)", a, 200, tol=0)
    quoted("  to", b, 300, tol=0)
    quoted("  minimal (%)", pct, 5, tol=0)
    quoted("Osaka rice 1770 (momme)", R["osaka_monme_per_koku"].loc[1770], 66.3, tol=0)
    H = HEDGE
    quoted("ex (1): margin (momme)", H["Q"] * H["F0"] * H["m"], 2000, tol=1e-9)
    ST = H["F0"] * (1 - H["drop"])
    quoted("  price after a 10% fall", ST, 54, tol=1e-9)
    h = hedge(H["Q"], H["F0"], ST, ST)
    quoted("  bills lose (momme)", h["bills"] - H["Q"] * H["F0"], -600, tol=1e-9)
    quoted("  futures gain", h["futures"], 600, tol=1e-9)
    quoted("  V_T", h["total"], 6000, tol=1e-9)
    assert math.isclose(h["total"], h["locked"])
    quoted("ex (2): loss / margin at 1/3 (%)", 100 * margin_shock(H["drop"], H["m"]), 30, tol=1e-9)
    quoted("  margin at 5% (momme per contract)", H["Q"] * H["F0"] * 0.05, 300, tol=1e-9)
    quoted("  loss / margin at 5% (%)", 100 * margin_shock(H["drop"], 0.05), 200, tol=1e-9)
    hb = hedge(H["Q"], H["F0"], ST, H["F_basis"])
    quoted("ex (3): V_T with basis (momme)", hb["total"], 5900, tol=1e-9)
    quoted("  basis cost (momme)", h["total"] - hb["total"], 100, tol=1e-9)
    print("\n-- efficiency --")
    a, b = F["tk_ito"]
    quoted("Ito: from", a, 1763, tol=0)
    quoted("  to", b, 1780, tol=0)
    a, b = F["tk_1798"]
    quoted("not rejected: from", a, 1798, tol=0)
    quoted("  to", b, 1835, tol=0)
    a, b = F["tk_1840"]
    quoted("rejected: from", a, 1840, tol=0)
    quoted("  to", b, 1864, tol=0)
    s, f = F["tk_8070"]
    quoted("weak form: spot (%)", s, 80, tol=0)
    quoted("  futures (%)", f, 70, tol=0)
    a, b = F["sch_miyamoto"]
    quoted("Miyamoto: from", a, 1751, tol=0)
    quoted("  to the 1830s", b, 1830, tol=0)
    a, b = F["sch_tenpo"]
    quoted("Tenpo from", a, 1830, tol=0)
    quoted("  to", b, 1843, tol=0)
    quoted("forward and book trading closed (April)", F["sch_1866"][0], 1866, tol=0)
    quoted("Dojima closed", F["sch_1869"][0], 1869, tol=0)
    assert F["tk_1730"] == [1730, 1869]
    quoted("commodities exchange opens", F["sch_1871"][0], 1871, tol=0)
    lo, hi = F["sch_margin_range"]
    quoted("compare: margin (%)", hi, 30, tol=0)
    quoted("  low", lo, 5, tol=0)


def qing(F, G):
    print("\n== sec:toku-qing ==")
    e = G["cash_per_tael"]
    for y, v in ((1807, 979), (1824, 1208), (1838, 1553), (1846, 2010), (1853, 2205)):
        quoted(f"Gamble {y} (cash/tael)", e.loc[y], v, tol=0)
    quoted("1807-1853 a year (%)", 100 * cagr(e.loc[1807], e.loc[1853], 1853 - 1807), 1.8, tol=0.05)
    quoted("道光十八年", reign("道光", F["wei_1838"][0]), 1838, tol=0)
    quoted("  Huang (via Wei Yuan): 1000 then", F["wei_1600"][0], 1600, tol=0)
    quoted("道光十九年", reign("道光", F["bao_date"][0]), 1839, tol=0)
    quoted("  Bao: 1000 / 0.61", 1000 / 0.61, 1639, tol=0.5)
    assert F["bao_1639"][0] <= 1000 / 0.61 < F["bao_1639"][0] + 10            # 一千六百三十余文
    quoted("道光二十五年 (刘良驹)", reign("道光", 25), 1845, tol=0)
    assert ganzhi(1845) == "乙巳"                                               # 吴嘉宾: 道光乙巳年
    quoted("  Beijing nearly", F["liu_rate"][0], 2000, tol=0)
    quoted("  provinces 2200-2300 (midpoint)", contemporaries(F)[3][1], 2250, tol=0)
    quoted("Wu: half a year from", F["wu_half_year"][0], 1500, tol=0)
    quoted("道光十七年 (清史稿)", reign("道光", F["qsg_daoguang17"][0]), 1837, tol=0)
    quoted("  often", F["qsg_2000"][0], 2000, tol=0)
    print("\n-- two moneys, one price --")
    quoted("Zeng: rice in silver then (taels)", F["zeng_rice"][0] / 1000, 3, tol=0)
    quoted("  now", F["zeng_rice"][0] / F["zeng_now"][0], 1.5, tol=0)
    quoted("Bao: grain at harvest (cash)", F["bao_500"][0], 500, tol=0)
    quoted("  before harvest", F["bao_700"][0], 700, tol=0)
    print("\n-- wages --")
    W = wages(G)
    quoted("wage 1807-1813 (cash/day)", W["w_base"], 81.25, tol=1e-9)
    quoted("  1845-1850", W["w_late"], 85.2, tol=0.05)
    quoted("  rise (%)", 100 * (W["w_late"] / W["w_base"] - 1), 4.8, tol=0.05)
    quoted("rate 1807-1813", W["e_base"], 1036, tol=0.5)
    quoted("  1845-1850 (about)", W["e_late"], 1990, tol=0.5)
    quoted("  rise (%)", 100 * (W["e_late"] / W["e_base"] - 1), 92, tol=0.5)
    quoted("silver wage 1807-1813 (tael)", W["ws_base"], 0.0784, tol=0.00005)
    quoted("  1845-1850", W["ws_late"], 0.0428, tol=0.00005)
    quoted("  fall (%)", 100 * (W["ws_late"] / W["ws_base"] - 1), -45, tol=0.5)
    idx = wage_index(G)
    quoted("fig (b): copper index 1845-1850", float(idx.loc[1845:1850, "copper"].mean()), 104.8, tol=0.05)
    quoted("  silver index, ratio of averages", 100 * W["ws_late"] / W["ws_base"], 55, tol=0.5)
    # ex:toku-burden
    x0, p, e0, e1 = F["zeng_dou3"][0] / DOU_PER_SHI, F["zeng_rice"][0], 1000, F["zeng_now"][0]
    T = x0 * p / e0
    quoted("ex (1): tax per mu (taels)", T, 0.9, tol=1e-9)
    quoted("  rice at 2000 (koku)", burden(T, e1, p), F["zeng_dou6"][0] / DOU_PER_SHI, tol=1e-9)
    tax = F["bao_1885"][0]
    quoted("ex (2): 1885 / 500 (koku)", tax / F["bao_500"][0], 3.8, tol=0.05)
    quoted("  1885 / 750", tax / GRAIN_HIGH, 2.5, tol=0.05)
    assert F["bao_700"][0] < GRAIN_HIGH < 800
    quoted("  by the rule: cash per tael", F["bao_rule"][0], 1000, tol=0)
    g, rate = F["wu_grain"][0], 2000
    quoted("ex (3): 10 koku x 600 / 2000 (taels)", 10 * g / rate, 3, tol=1e-9)
    quoted("  wage 10,000 / 2000", 10_000 / rate, F["wu_wage"][0], tol=1e-9)
    quoted("  at 1100: grain", 10 * g / F["wu_1100"][0], 5.5, tol=0.05)
    quoted("  wage", 10_000 / F["wu_1100"][0], 9.1, tol=0.05)


def debate(F, G):
    print("\n== sec:toku-debate ==")
    quoted("道光十八年 (Huang Juezi)", reign("道光", F["qsg_huang18"][0]), 1838, tol=0)
    quoted("  before 道光十四年: more than (10k taels)", F["qsg_huang_2000"][0], 2000, tol=0)
    quoted("  recently (10k taels)", F["qsg_huang_3000"][0], 3000, tol=0)
    # ex:toku-lin
    per_year = F["lin_36"][0]
    days = per_year * QIAN_PER_TAEL
    quoted("ex (1): days a year", days, 360, tol=0)
    pop = F["lin_pop"][0]
    spend = pop * 0.01 * per_year
    quoted("ex (2): 4e8 x 1% x 36 (100m taels)", spend / 1e8, 1.44, tol=1e-9)
    assert spend > F["lin_onepct"][0]
    quoted("  / zhenggong", spend / F["bao_zhenggong"][0], 3.6, tol=1e-9)
    quoted("ex (3): days a poor man lives on one qian: 10/5", FEN_PER_QIAN / 5, 2, tol=0)
    quoted("  10/4", FEN_PER_QIAN / 4, 2.5, tol=0)
    print("\n-- dissenters --")
    quoted("Liu: like the 捐输 rate (cash per tael)", F["liu_1500"][0], 1500, tol=0)
    a, b, c, d = F["zhou_67"]
    quoted("Zhou: when silver was ample (cash)", a, 600, tol=0)
    quoted("  to", b, 700, tol=0)
    quoted("  now", c, 1500, tol=0)
    quoted("  to", d, 1600, tol=0)
    print("\n-- modern research --")
    quoted("Lin: after (year)", F["ir_lin_supply"][0], 1808, tol=0)
    quoted("silver back after the mid-", F["at_back"][0], 1856, tol=0)
    a, b = F["ir_opium25"]
    quoted("opium imports multiplied by", a, 20, tol=0)
    quoted("  or", b, 25, tol=0)
    quoted("Carolus premium in Shanghai, 1856 (%)", F["ir_premium50"][0], 50, tol=0)
    e = G["cash_per_tael"]
    quoted("Gamble 1807 -> 1824", e.loc[1807], 979, tol=0)
    quoted("  1824", e.loc[1824], 1208, tol=0)
    quoted("  rise (%)", 100 * (e.loc[1824] / e.loc[1807] - 1), 23, tol=0.5)
    print("\n-- case: Beijing --")
    quoted("military and river costs (10k taels): 二千数百万", F["qsg_xianfeng_need"][0], 2000, tol=0)
    quoted("顺治八年", reign("顺治", F["qsg_shunzhi_chao"][0]), 1651, tol=0)
    quoted("  顺治十年", reign("顺治", 10), 1653, tol=0)
    quoted("  '十年' of circulation would end in", reign("顺治", 8) + 10, 1661, tol=0)
    quoted("note: 1 tael = cash", F["qsg_piao"][0], 2000, tol=0)
    quoted("dangshi coin used as (cash)", F["qsg_dangshi"][0], 2, tol=0)
    quoted("  share of face value (%)", 100 * F["qsg_dangshi"][0] / 10, 20, tol=1e-9)


def europe(F):
    print("\n== sec:toku-europe ==")
    m, _ = load_snapshot("merc_facts", dtype={"value": str})
    a, b = (float(x) for x in dict(zip(m["id"], m["value"]))["velde_devalue"].split(";"))
    quoted("France 1720: silver coin 1 L -> 1.5 L: devalued by (fraction)", 1 - a / b, 1 / 3, tol=1e-9)
    quoted("shogunate guarantees rice bills", F["sch_guarantee"][0], 1773, tol=0)
    quoted("suing-days", F["sch_1773"][0], 1773, tol=0)
    f, l, c = F["sch_frankfurt"]
    quoted("Chicago", c, 1848, tol=0)
    quoted("Frankfurt", f, 1867, tol=0)
    quoted("London", l, 1877, tol=0)
    quoted("Dojima earlier than Chicago by (years) -- 'more than a century'", c - DOJIMA_OPEN, 118, tol=0)


def test(F, R, G):
    print("\n== sec:toku-test: tab:toku-test ==")
    E, O = edo_test(F, R), osaka_test(F, R)
    for k, c, pred, act in (("keicho", 15.05, None, 0.786), ("genroku", 10.24, 1.155, 1.148), ("kenji", 7.91, 1.496, 1.781),
                            ("kyoho", 15.49, 0.763, 0.838), ("genbun", 8.63, 1.371, 1.154)):
        quoted(f"Edo {k}: pure gold (g)", E.loc[k, "c"], c, tol=0.005)
        if pred is not None:
            quoted("  prediction", E.loc[k, "pred"], pred, tol=0.0005)
        quoted("  actual", E.loc[k, "actual"], act, tol=0.0005)
    for k, c, pred, act in (("genroku", 64, None, 72.4), ("futatsu", 50, 92.7, 71.5), ("yotsu", 20, 231.8, 118.7),
                            ("kyoho", 80, 58.0, 47.1), ("genbun", 46, 100.8, 68.0)):
        quoted(f"Osaka {k}: fineness (%)", O.loc[k, "c"], c, tol=0)
        if pred is not None:
            quoted("  prediction", O.loc[k, "pred"], pred, tol=0.05)
        quoted("  actual", O.loc[k, "actual"], act, tol=0.05)
    assert (O["pred"].iloc[1:] > O["actual"].iloc[1:]).all()                    # 'every period too high'
    assert E.loc["kenji", "actual"] > E.loc["kenji", "pred"] and E.loc["kyoho", "actual"] > E.loc["kyoho", "pred"]
    quoted("Genbun: by content, rise over Kyoho (15.49/8.63)", E.loc["kyoho", "c"] / E.loc["genbun", "c"], 1.795,
           tol=0.0005)
    quoted("  (%)", 100 * (E.loc["kyoho", "c"] / E.loc["genbun", "c"] - 1), 80, tol=0.5)
    quoted("  actual (1.154/0.838)", E.loc["genbun", "actual"] / E.loc["kyoho", "actual"], 1.376, tol=0.0005)
    quoted("  (%)", 100 * (E.loc["genbun", "actual"] / E.loc["kyoho", "actual"] - 1), 38, tol=0.5)
    quoted("  quantity theory, all old coins at 165 (%)", F["suz_165"][1] - F["suz_165"][0], 65, tol=0)
    a, b = F["suz_six_eight"]
    quoted("1736: kobans in circulation", a, 6, tol=0)
    quoted("  chogins", b, 8, tol=0)
    print("\n-- fig:toku_rice --")
    quoted("(b) Yotsuhogin: prediction / actual -- 'nearly double'", O.loc["yotsu", "pred"] / O.loc["yotsu", "actual"],
           1.95, tol=0.005)
    C = chogin(F)
    before = sum(C[k]["mintage"] for k in ("genroku", "futatsu", "mitsu"))
    quoted("Yotsuhogin minted (10k kan, about 40)", C["yotsu"]["mintage"] / 1e4, 40.1, tol=0.05)
    quoted("  Genroku + Futatsuhogin + Mitsuhogin (10k kan) -- 'more than a million'", before / 1e4, 105.4, tol=0.05)
    assert 1e6 < before < 2e6
    o = R["osaka_monme_per_koku"]
    quoted("1718 law: good 1 = Yotsuhogin", F["suz_t5_1718"][1] / F["suz_t5_1718"][0], 4, tol=0)
    quoted("Osaka 1718 -> 1719: divided by", o.loc[1718] / o.loc[1719], 3.15, tol=0.005)
    print("\n-- Qing --")
    W = wages(G)
    quoted("rate rise (%)", 100 * (W["e_late"] / W["e_base"] - 1), 92, tol=0.5)
    quoted("copper wage (%)", 100 * (W["w_late"] / W["w_base"] - 1), 4.8, tol=0.05)
    quoted("silver wage (%)", 100 * (W["ws_late"] / W["ws_base"] - 1), -45, tol=0.5)
    quoted("1807-1824 (%)", 100 * (G["cash_per_tael"].loc[1824] / G["cash_per_tael"].loc[1807] - 1), 23, tol=0.5)
    return E, O


def deeper(F, R):
    print("\n== deeper box ==")
    p14, y14, p18, y18 = F["sch_200_30"]
    quoted("Schaede/Sugie 1714 (momme)", p14, 200, tol=0)
    quoted("  1718 (about)", p18, 30, tol=0)
    assert (y14, y18) == (1714, 1718)
    o = R["osaka_monme_per_koku"]
    quoted("Iwahashi 1714", o.loc[1714], 149.2, tol=0)
    quoted("  1718", o.loc[1718], 127.9, tol=0)
    quoted("  1719", o.loc[1719], 40.6, tol=0)
    K = koban(F)
    quoted("Table 2: Keicho -> Genroku pure gold fell (%)", 100 * (1 - K["genroku"]["pure"] / K["keicho"]["pure"]), 31.94,
           tol=0.005)
    quoted("  Suzuki's text", F["suz_genbun_gold"][1], 31.91, tol=0)
    quoted("Table 2: Kyoho -> Genbun (%)", 100 * (1 - K["genbun"]["pure"] / K["kyoho"]["pure"]), 44.30, tol=0.005)
    quoted("  Suzuki's text", F["suz_genbun_gold"][0], 44.34, tol=0)
    p_new, p_old = F["suz_sale_gold"]
    quoted("implied Genbun weight (g)", p_new / (K["genbun"]["gold"] / 100), 13.06, tol=0.005)
    quoted("implied Keicho weight (g)", p_old / F["suz_sale"][3] / (K["keicho"]["gold"] / 100), 17.76, tol=0.005)
    lo, hi, _ = F["sch_margin1770"]
    quoted("1-2 momme/koku x 100 koku: from", lo * F["sch_100koku"][0], 100, tol=0)
    quoted("  to", hi * F["sch_100koku"][0], 200, tol=0)
    quoted("300 momme / (100 x 66.3) (%)", 100 * F["sch_margin5"][1] / (100 * o.loc[1770]), 4.5, tol=0.05)
    quoted("道光二十四年", reign("道光", 24), 1844, tol=0)
    quoted("道光二十六年", reign("道光", F["zeng2_three"][0]), 1846, tol=0)
    quoted("Gamble 1854 (cash/tael)", load_snapshot("gpih_gamble_beijing")[0].set_index("year").loc[1854, "cash_per_tael"],
           2723, tol=0)
    quoted("  1856", load_snapshot("gpih_gamble_beijing")[0].set_index("year").loc[1856, "cash_per_tael"], 4970, tol=0)


def legacy_and_takeaways(F, R, G):
    print("\n== legacy and takeaways ==")
    K = koban(F)
    old_g, _, new_g, _ = F["suz_arai"]
    quoted("Genroku seigniorage rate (%) -- 'about 32'", 100 * seign_rate(new_g / old_g, 0.01), 32, tol=1)
    quoted("Edo mark-up at 45 (%)", 100 * (FIXED_RATE / 45 - 1), 33, tol=0.5)
    quoted("Genroku price rise by content (%)", 100 * (K["keicho"]["pure"] / K["genroku"]["pure"] - 1), 46.9, tol=0.05)
    rr, rk = K["keicho"]["pure"] / K["genbun"]["pure"], K["kyoho"]["pure"] / K["genbun"]["pure"]
    quoted("Genbun seigniorage, low (%)", 100 * seign_rate(rr, 0.65), 5, tol=0.5)
    quoted("  high (%)", 100 * seign_rate(rk, 0.65), 8, tol=0.5)
    quoted("1845-1850 rate (about)", wages(G)["e_late"], 1990, tol=0.5)
    quoted("Smith 1776: Dojima open for (years)", SMITH - DOJIMA_OPEN, 46, tol=0)


def selfcheck():
    print("\n== selfcheck ==")
    r = 15 / 12
    quoted("1: price x", r, 1.25, tol=1e-9)
    quoted("  S per 100", seigniorage(100, 15, 12, 0.05), 20, tol=1e-9)
    quoted("  rate (%)", 100 * seign_rate(r, 0.05), 16, tol=1e-9)
    quoted("  = 20/125 (%)", 100 * 20 / 125, 16, tol=1e-9)
    quoted("2: ryo", 100 / 50, 2, tol=0)
    quoted("  Edo tag (momme)", 100 / 50 * FIXED_RATE, 120, tol=0)
    quoted("  dearer (%)", 100 * (FIXED_RATE / 50 - 1), 20, tol=1e-9)
    quoted("3: rice at 1200 (koku)", burden(0.5, 1200, 2500), 0.24, tol=1e-9)
    quoted("  at 1800", burden(0.5, 1800, 2500), 0.36, tol=1e-9)
    quoted("  and rice 10% cheaper", burden(0.5, 1800, 2500 * 0.9), 0.4, tol=1e-9)
    h = hedge(200, 50, 45, 45.5)
    quoted("4: V_T (momme)", h["total"], 9900, tol=1e-9)
    quoted("  unhedged", 200 * 45, 9000, tol=0)
    quoted("  difference", h["total"] - 200 * 45, 900, tol=1e-9)
    quoted("  basis loss", 200 * 0.5, 100, tol=1e-9)
    quoted("5: wage at 1100 (taels)", 90 / 1100, 0.082, tol=0.0005)
    quoted("  at 2000", 90 / 2000, 0.045, tol=1e-9)
    quoted("  fall (%)", 100 * (1 - 1100 / 2000), 45, tol=1e-9)
    quoted("6: 3.5e8 x 0.5% x 36 (10k taels)", 3.5e8 * 0.005 * 36 / 1e4, 6300, tol=1e-6)


def from_quotes(Q):
    print("\n== the numbers as printed in the quotations ==")
    said(Q, "suz_1695", "1695 Genroku debasement")
    said(Q, "suz_plan", "remint twice the amount", "return half of it")
    said(Q, "suz_arai", "8,824,350 ryo", "287,617.155 kan", "13,236,534 ryo", "357,535.380 kan")
    said(Q, "suz_officer", "20,000,000 ryo", "400,000 kan")
    said(Q, "suz_half", "half the Keicho coins")
    said(Q, "suz_premium", "one ryo for every 100 ryo", "until 1707")
    said(Q, "suz_tani", "1714", "Tani Choemon", "Sakai")
    said(Q, "suz_1500", "1,000 momme", "1,500 momme")
    said(Q, "suz_2000", "after 1714", "2,000 momme")
    said(Q, "suz_4000", "4,000 momme")
    said(Q, "suz_defray", "2,000 momme")
    said(Q, "suz_1718law", "1718")
    said(Q, "suz_stable60", "60 momme of silver to 1 ryo of gold")
    said(Q, "suz_1700", "1700", "60 momme of silver to 1 ryo of gold")
    said(Q, "suz_4080", "40 momme", "80 momme", "twice the price")
    said(Q, "suz_1718rate", "45 momme of silver to 1 ryo", "60 momme to 1 ryo", "November 1718")
    said(Q, "suz_obeyed", "1700")
    said(Q, "suz_60mmt", "60 Momme", "1719")
    said(Q, "suz_genbun_gold", "44.34%", "31.91%")
    said(Q, "suz_genbun_silver", "42.5%", "20%")
    said(Q, "suz_165", "100 ryo", "165 ryo")
    said(Q, "suz_15000", "10,000 momme", "15,000 momme")
    said(Q, "suz_six_eight", "six types", "eight types", "1736")
    said(Q, "suz_1716", "two decades", "nine-tenths")
    said(Q, "suz_guilds", "Ten guilds")
    said(Q, "suz_fn5", "60 momme to 1 ryo")
    said(Q, "suz_sale_date", "June 15, 1736")
    said(Q, "suz_may28", "May 28, 1736")
    said(Q, "suz_sale", "120 momme", "60 momme = 1 ryo", "48 momme", "0.8 ryo", "3 gold bu and 3 silver momme", "20% off")
    said(Q, "suz_sale_new", "79.2 momme", "1.32 gold ryo")
    said(Q, "suz_sale_gold", "8.581726 grams", "0.8 ryo", "11.9759232 grams")
    said(Q, "suz_chogin", "161.25 g")
    said(Q, "suz_edo_emergent", "17th century")
    said(Q, "sch_pop", "30 million", "87%", "5%")
    said(Q, "sch_pop8", "8%")
    said(Q, "sch_osaka", "200 000", "1609", "doubled", "400 000", "1750s")
    said(Q, "sch_koku", "1 koku = 10 to = 180 litres")
    said(Q, "sch_warehouses", "91 warehouses in 1673", "124 in 1730")
    said(Q, "sch_dojima_1688", "1688")
    said(Q, "sch_yodoya_1697", "1697")
    said(Q, "sch_1730", "1730")
    said(Q, "sch_18months", "18 months")
    said(Q, "sch_10koku", "10 kok", "1700")
    said(Q, "sch_1749", "110,000 bales", "1749", "30,000 bales")
    said(Q, "sch_four", "four times")
    said(Q, "sch_1652", "1652")
    said(Q, "sch_1660", "1660", "30 days")
    said(Q, "sch_1663", "1663", "10 days")
    said(Q, "sch_10days_eff", "10 days")
    said(Q, "sch_1705", "1705")
    said(Q, "sch_kyoho", "1716-1735", "180 degree")
    said(Q, "sch_200_30", "200 monme", "1714", "30 monme", "1718")
    said(Q, "sch_1728", "1728", "1730")
    said(Q, "sch_decree1", "(1)")
    said(Q, "sch_decree3", "(3)", "50 clearinghouses")
    said(Q, "sch_decree5", "(5)")
    said(Q, "sch_1773", "1773")
    said(Q, "sch_guarantee", "1773")
    said(Q, "sch_licences", "500 in 1731", "500 in April 1732", "300 in November 1732")
    said(Q, "sch_1300", "1300")
    said(Q, "sch_clearing_1731", "1731, 50", "10 in 1746")
    said(Q, "sch_clearing_four", "sixty", "four", "19th century")
    said(Q, "sch_margin30", "30%")
    said(Q, "sch_margin1770", "one to two monme", "1770")
    said(Q, "sch_margin5", "200 to 300 monme", "100 koku", "5%")
    said(Q, "sch_periods", "three periods")
    said(Q, "sch_100koku", "100 koku")
    said(Q, "sch_third", "one third")
    said(Q, "sch_tenday", "ten-day")
    said(Q, "sch_1737", "1737")
    said(Q, "sch_1866", "April 1866")
    said(Q, "sch_1869", "April 1869")
    said(Q, "sch_miyamoto", "1751", "1830s")
    said(Q, "sch_margin_range", "5 and 30%")
    said(Q, "sch_tonya30", "70%", "30 days")
    said(Q, "sch_rollover", "10 days")
    said(Q, "sch_3mai", "3 mai", "23", "300 koku", "23 monme")
    said(Q, "sch_tenpo", "futures prices did not rise")
    said(Q, "sch_1871", "1871")
    said(Q, "sch_first", "18th century Japan")
    said(Q, "sch_frankfurt", "Frankfurt (1867)", "London (1877)", "1848")
    said(Q, "tk_1730", "1730", "1869")
    said(Q, "tk_ito", "1763 to 1780")
    said(Q, "tk_1798", "1798 to 1835", "1 %")
    said(Q, "tk_1840", "1840 to 1864", "1 %")
    said(Q, "tk_8070", "80%", "7")
    said(Q, "ir_1000", "1000 copper cash")
    said(Q, "ir_opium25", "20 or 25")
    said(Q, "ir_lin_supply", "1808")
    said(Q, "ir_timing", "1810s", "mid1820s")
    said(Q, "ir_new_coins", "1810s")
    said(Q, "ir_standard", "1820s")
    said(Q, "ir_premium50", "50%")
    said(Q, "at_back", "mid-1850s")
    said(Q, "qsg_seven", "二年", "钱七枚准银一分")
    said(Q, "qsg_ten", "十枚准一分")
    said(Q, "qsg_1000", "钱千准银一两")
    said(Q, "qsg_qiqi", "七钱三")
    said(Q, "qsg_kangxi_floor", "毋得不足一千")
    said(Q, "qsg_kangxi_880", "八百八十至七百七十")
    said(Q, "qsg_qianlong_800", "仅易八百文")
    said(Q, "qsg_leak", "以千万计")
    said(Q, "qsg_daoguang17", "十七年")
    said(Q, "qsg_2000", "常至二千")
    said(Q, "qsg_daqian", "当千至当十，凡五等")
    said(Q, "qsg_piao", "票银一两抵制钱二千", "钞二千抵银一两")
    said(Q, "qsg_dangshi", "当十", "当制钱二")
    said(Q, "qsg_huang18", "十八年")
    said(Q, "qsg_huang_early", "数百万")
    said(Q, "qsg_huang_2000", "十四年以前", "二千馀万")
    said(Q, "qsg_huang_3000", "三千馀万")
    said(Q, "qsg_huang_ports", "数千万")
    said(Q, "qsg_shunzhi_chao", "顺治八年", "十二万八千有奇", "十年而罢")
    said(Q, "qsg_xianfeng_need", "二千数百万")
    said(Q, "qsg_chao_fail", "七折钱")
    said(Q, "zeng_rice", "石米买钱三千")
    said(Q, "zeng_then", "两银换钱一千", "石米得银三两")
    said(Q, "zeng_now", "两银换钱二千", "石米仅得银一两五钱")
    said(Q, "zeng_dou3", "卖米三斗")
    said(Q, "zeng_dou6", "卖米六斗")
    said(Q, "zeng_double", "一倍")
    said(Q, "zeng_jiangsu", "道光十五年", "十六年")
    said(Q, "zeng2_three", "二十四年", "二十五年", "二十六年")
    said(Q, "liu_rate", "几及二千文", "二千二三百文")
    said(Q, "liu_1500", "一千五百文抵银一两")
    said(Q, "wu_year", "道光乙巳年")
    said(Q, "wu_1100", "一千一百文")
    said(Q, "wu_half_year", "半年", "一千五百文", "二千文有零")
    said(Q, "wu_grain", "十石谷", "三两银", "每石六百", "值钱二千")
    said(Q, "wu_wage", "五两银", "十千")
    said(Q, "bao_1639", "制钱一千", "六钱一分", "一千六百三十余文")
    said(Q, "bao_date", "道光十九年")
    said(Q, "bao_1885", "钱粮一两", "一千八百八十五文")
    said(Q, "bao_rule", "制钱一千", "库纹一两")
    said(Q, "bao_500", "谷一石", "五百上下")
    said(Q, "bao_700", "七百数十文", "二三石")
    said(Q, "bao_zhenggong", "四千万两")
    said(Q, "zhou_67", "六七百", "千五六百")
    said(Q, "wei_1838", "道光十八年")
    said(Q, "wei_1600", "每两兑钱千", "千有六百")
    said(Q, "lin_36", "银一钱", "三十六两")
    said(Q, "lin_pop", "四万万人")
    said(Q, "lin_onepct", "一百分之中仅有一分", "万万两")
    said(Q, "lin_ample", "银一钱")
    said(Q, "lin_huang", "数千万两")
    said(Q, "lin_poor", "四五分")


def main():
    F, Q, R, G = facts(), quotes(), rice(), gamble()
    intro(F, R)
    world(F)
    koku(F, R)
    genroku(F, R)
    dojima(F, R)
    qing(F, G)
    debate(F, G)
    europe(F)
    test(F, R, G)
    deeper(F, R)
    legacy_and_takeaways(F, R, G)
    selfcheck()
    from_quotes(Q)
    print("all numbers in Chapter 17 check out")


if __name__ == "__main__":
    main()
