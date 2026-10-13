"""Chapter 13 (白银的世纪：波托西、马尼拉与价格革命): every number quoted in zh/ch13_silver.tex.

    python3 checks/check_ch13.py

Inputs are eight snapshots:
  silver_century_facts          quotations (Ming history, 皇明经世文编, Quan Hansheng, Blair & Robertson,
                                Malestroit, Bodin, Le Branchu, Hamilton, Drelichman & Voth, Edo & Melitz),
                                checked by data/fetch/verify_quotes.py and data/fetch/verify_web_quotes.py
  quan1969_manila_silver        Quan's table 1: contemporary estimates of the silver sent from Mexico to Manila
  hamilton1929_treasure         Hamilton (1929) Table A: average annual registered imports by period (pesos)
  boe_millennium_england_money  England: nominal and real GDP, deflator, population (Broadberry et al. 2015),
                                coin in circulation (Palma 2018)
  gpih_silver_pound             grams of pure silver per pound sterling at the mint price (Lindert, from Jastram)
  clark2015_england_decadal_1490_1690  Clark's decadal wages, cost of living, population and land rents
  gpih_allen_silver_cpi         Allen's consumer price index in grams of silver, European cities
  dv2010_castile_annual         Castile's accounts 1566-1596 (Drelichman & Voth 2010 dataset)
  dv2010_philip2                Drelichman & Voth (2010) Tables 2 and 3
The figure module figsrc/fig_ch13.py imports the functions defined here.

Models (the chapter's key equations):
    arbitrage           R_E / R_C - 1 <= c                                          (eq:silver-arbitrage)
    quantity equation   M V = P Y, g_P ~ g_M + g_V - g_Y                             (eq:silver-qty)
    debt dynamics       d' = (1+r)/(1+g) d - ps; ps* = (r-g)/(1+g) d; D* = PS/(r-g)  (eq:silver-debt)
    Malthus (Ch. 11)    w1/w0 = (L1/L0)^(-alpha), s1/s0 = (L1/L0)^(1-alpha)           (eq:medieval-factor)
Decade means: every series is averaged over the calendar decade (1500-1509 = "1500 年代"); velocity is the
residual P Y / M of the decade means, with the deflator on 2013 = 100 and output in 2013 pounds.
"""
from __future__ import annotations

import math

import pandas as pd

from common import load_snapshot, quoted

# Chapter 11's effective land share (Clark's shares: labour 0.50, land 0.34, capital 0.16 adjusting)
ALPHA = 0.34 / (1.0 - 0.16)

GRAIN_PER_GRAM = 0.06479891            # one grain in grams
TAEL_PER_PESO = 0.72                   # Quan: one Spanish peso ~ 0.72 tael of Chinese silver

# Teaching inputs stated in the text
MANILA_PESOS = 2_000_000               # ex:silver-scale: pesos sent to Manila in a year, all to China
ARBITRAGE_COST = 0.20                  # ex:silver-arbitrage: freight, risk and interest, share of the outlay
GRAIN_PRICE_FALL = 0.5                 # ex:silver-burden: the silver price of grain halves
SILVER_VANISHES = True                 # ex:silver-debt (3): Indies revenue disappears, spending unchanged

QUANTITY_DECADES = (1500, 1600)
TABLE_DECADES = [1500, 1530, 1560, 1590, 1600, 1630, 1660, 1690]
CITIES = ["valencia", "paris", "london", "florence", "krakow", "antwerp"]


def _snapshot_facts():
    df, _ = load_snapshot("silver_century_facts", dtype={"value": str})
    return df


def facts() -> dict[str, list[float]]:
    """id -> list of the numbers in the value column (several values are separated by ';')."""
    out = {}
    for _, r in _snapshot_facts().iterrows():
        v = r["value"]
        if isinstance(v, str) and v.strip():
            out[r["id"]] = [float(x) for x in v.split(";")]
    return out


def quotes() -> dict[str, str]:
    """id -> verbatim quotation (for numbers the text takes straight from a quotation)."""
    df = _snapshot_facts()
    return dict(zip(df["id"], df["quote"].fillna("")))


def said(Q: dict[str, str], qid: str, *tokens: str) -> None:
    """Assert that each token (a number as printed in the source) occurs in the quotation qid."""
    missing = [t for t in tokens if t not in Q[qid]]
    print(f"{'ok ' if not missing else 'BAD'} {qid}: quotation contains {', '.join(tokens)}")
    if missing:
        raise AssertionError(f"{qid}: {missing} not in the quotation")


# --- data ------------------------------------------------------------------
def hamilton() -> pd.DataFrame:
    """Hamilton (1929) Table A with each period's total (average x years) and share of the 1503-1660 sum."""
    df, _ = load_snapshot("hamilton1929_treasure")
    df["sum_pesos"] = df["total_pesos"] * df["years"]
    df["share"] = df["sum_pesos"] / df["sum_pesos"].sum()
    return df


def manila() -> pd.DataFrame:
    df, _ = load_snapshot("quan1969_manila_silver")
    return df


def england() -> pd.DataFrame:
    """Decade means of M (coin, £m), Y (real GDP), P (deflator), grams of silver per pound and population;
    velocity V = P Y / 100 / M of the means; P_ag = P x grams per pound (silver price level)."""
    b, _ = load_snapshot("boe_millennium_england_money")
    g, _ = load_snapshot("gpih_silver_pound")
    df = b.set_index("year").join(g.set_index("year"))
    df["decade"] = df.index // 10 * 10
    d = df.groupby("decade").mean()
    d = d.rename(columns={"coin_palma_gbp_m": "M", "real_gdp_2013_gbp_m": "Y", "gdp_deflator_2013_100": "P",
                          "grams_ag_per_gbp_mint": "ag", "pop_england_m": "pop"})
    d["V"] = d["P"] * d["Y"] / 100.0 / d["M"]
    d["P_ag"] = d["P"] * d["ag"]
    return d


def england_index(col: str) -> pd.Series:
    """Column of england() with the 1500s = 100."""
    d = england()
    return 100.0 * d[col] / d.loc[1500, col]


def clark() -> pd.DataFrame:
    df, _ = load_snapshot("clark2015_england_decadal_1490_1690")
    df = df.set_index("decade")
    df["real_rent"] = df["land_rents_gbp_m"] / df["col_1860s_100"]
    return df


def allen() -> pd.DataFrame:
    """Allen's silver CPI, decade means (grams of silver per basket, common base)."""
    df, _ = load_snapshot("gpih_allen_silver_cpi")
    df["decade"] = df["year"] // 10 * 10
    return df.drop(columns="year").groupby("decade").mean()


def castile() -> pd.DataFrame:
    df, _ = load_snapshot("dv2010_castile_annual")
    df = df.set_index("year")
    df["debt_ratio"] = df["debt"] / df["revenue"]
    df["indies_share"] = df["indies"] / df["revenue"]
    return df


def table3() -> pd.DataFrame:
    """Drelichman & Voth (2010) Table 3, one row per period; g and r in per cent as printed."""
    df, _ = load_snapshot("dv2010_philip2", dtype={"table": str})
    t = df[df["table"] == "3"].pivot(index="period", columns="item", values="value")
    return t.loc[["1565-74", "1574-84", "1584-96", "1565-96"]]


def indies_share(C: pd.DataFrame, first: int, last: int) -> float:
    """Share of the Indies in total revenue over the years first..last (sum over sum)."""
    s = C.loc[first:last]
    return s["indies"].sum() / s["revenue"].sum()


# --- models ----------------------------------------------------------------
def arbitrage_gross(r_e: float, r_c: float) -> float:
    """eq:silver-arbitrage: gross return of carrying silver from E to C, buying gold, selling it in E."""
    return r_e / r_c - 1.0


def compound(ratio: float, years: float) -> float:
    """(X_T / X_0)^(1/T) - 1."""
    return ratio ** (1.0 / years) - 1.0


def factor_prices(l_ratio: float, alpha: float = ALPHA) -> tuple[float, float]:
    """eq:medieval-factor: (w1/w0, s1/s0) when labour rises to l_ratio of its old level, land fixed."""
    return l_ratio ** (-alpha), l_ratio ** (1.0 - alpha)


def ps_star(d: float, r: float, g: float) -> float:
    """eq:silver-debt: primary surplus (share of revenue) that keeps debt/revenue at d."""
    return (r - g) / (1.0 + g) * d


def d_star(ps: float, r: float, g: float) -> float:
    """eq:silver-debt: sustainable debt/revenue for a permanent primary surplus ps (IMF approximation)."""
    return ps / (r - g)


def debt_path(d0: float, ps: float, r: float, g: float, T: int) -> list[float]:
    """eq:silver-debt iterated: d_{t+1} = (1+r)/(1+g) d_t - ps."""
    d = [d0]
    for _ in range(T):
        d.append((1.0 + r) / (1.0 + g) * d[-1] - ps)
    return d


# ---------------------------------------------------------------------------
def intro(F):
    """Opening paragraph."""
    quoted("Santibáñez 1598: a million a year from New Spain", F["br10_1598"][0], 1_000_000, tol=0)
    quoted("the king's fourth default (1596) two years before the letter", 1598 - F["dv_four"][3], 2, tol=0)
    quoted("Bodin 1568, thirty years before the letter", 1598 - 1568, 30, tol=0)


def ming_money(F):
    """sec:silver-world, 明朝：一个缺银的大国; selfcheck 1."""
    quoted("1376: one tael of silver for one shi of rice", F["ming_1376_commute"][0], 1, tol=0)
    quoted("1397: gold one tael ten shi", F["ming_1397_gold"][0], 10, tol=0)
    quoted("1397: silver one tael two shi", F["ming_1397_silver"][0], 2, tol=0)
    quoted("1397 doubled: silver one tael four shi", 2 * F["ming_1397_silver"][0], 4, tol=0)
    quoted("1376 -> 1397: rate of 4 against 1, 'rose by three times'", 4 / F["ming_1376_commute"][0] - 1, 3, tol=0)
    quoted("1376 -> 1397: twenty-one years", 1397 - 1376, 21, tol=0)
    quoted("1397 official gold/silver ratio", F["ming_1397_gold"][0] / F["ming_1397_silver"][0], 5, tol=0)
    quoted("  after doubling, still", 2 * F["ming_1397_gold"][0] / (2 * F["ming_1397_silver"][0]), 5, tol=0)
    quoted("1436: 0.25 tael a shi", F["ming_1436_jinhua_rate"][0], 0.25, tol=0)
    quoted("1436: four shi a tael", 1 / F["ming_1436_jinhua_rate"][0], F["ming_1436_permanent"][0], tol=0)
    quoted("1436: over four million shi", F["ming_1436_jinhua_total"][0], 4_000_000, tol=0)
    quoted("1436: over a million taels", F["ming_1436_jinhua_total"][1], 1_000_000, tol=0)
    quoted("  4 million shi x 0.25 = 1 million taels", F["ming_1436_jinhua_total"][0] * F["ming_1436_jinhua_rate"][0],
           F["ming_1436_jinhua_total"][1], tol=0)
    quoted("selfcheck 1: 1376 -> 1436, sixty years", 1436 - 1376, 60, tol=0)
    quoted("Yongle: over 300,000 taels a year", F["ming_yongle_ban"][0], 300_000, tol=0)
    quoted("silver tax, Chengzu (taels/yr)", F["quan1968_yinke_chengzu"][0], 224_313, tol=0)
    quoted("silver tax, Xuanzong (taels/yr)", F["quan1968_yinke_xuanzong"][0], 256_450, tol=0)
    quoted("silver tax, Wuzong (taels/yr)", F["quan1968_yinke_wuzong"][0], 32_920, tol=0)
    quoted("Wuzong / Xuanzong (%)", 100 * F["quan1968_yinke_wuzong"][0] / F["quan1968_yinke_xuanzong"][0], 12.8, tol=0.05)
    quoted("Quan: purchasing power about twice that of Song-Yuan", F["quan1969_purchasing"][0], 2, tol=0)


def america(F, H):
    """sec:silver-world, 美洲的银山; fig:silver_flows (a); takeaways."""
    quoted("Potosí discovered", F["hamilton_potosi"][0], 1545, tol=0)
    potosi, world = F["quan1969_potosi"][0], F["quan1968_world"][0]
    quoted("Kobata: Potosí 1581-1600 (kg/yr)", potosi, 254_000, tol=0)
    quoted("Kobata: world 1581-1600 (kg/yr)", world, 418_900, tol=0)
    quoted("Potosí share of world output (%)", 100 * potosi / world, 60.6, tol=0.05)
    quoted("  Quan: 'a little over sixty per cent'", F["quan1969_potosi"][1], 60, tol=0)
    quoted("Casa de Contratación: tax on remittances (%)", F["dv_quint"][0], 20, tol=0)
    ag, au = F["hamilton_kg"]
    quoted("Hamilton: silver (kg)", ag, 16_632_648.20, tol=0)
    quoted("Hamilton: gold (kg)", au, 181_234.95, tol=0)
    quoted("silver / gold by weight", ag / au, 91.8, tol=0.05)
    years = 1660 - 1503 + 1
    quoted("1503-1660: years", years, 158, tol=0)
    quoted("silver a year (tonnes)", ag / years / 1000, 105, tol=0.5)
    quoted("takeaways: registered silver 1503-1660 (10,000 tonnes)", ag / 1e7, 1.66, tol=0.005)
    quoted("smuggling: from 10% of registered", F["hamilton_smuggling"][0], 10, tol=0)
    quoted("smuggling: to 50% of registered", F["hamilton_smuggling"][1], 50, tol=0)
    quoted("public receipts 1536-1660 (%)", F["hamilton_public"][0], 26.2, tol=0)
    share = H.set_index("period")["share"]
    before = H[H["last"] <= 1550]["share"].sum()
    after = H[H["first"] >= 1601]["share"].sum()
    quoted("Table A: share before 1550 (%)", 100 * before, 4.6, tol=0.05)
    quoted("Table A: share 1591-1600 (%)", 100 * share["1591-1600"], 15.5, tol=0.05)
    assert share.idxmax() == "1591-1600", share.idxmax()
    print("ok  Table A: 1591-1600 is the largest decade")
    quoted("Table A: share from 1601 (%)", 100 * after, 51.8, tol=0.05)
    quoted("Table A: share 1651-1660 (%)", 100 * share["1651-1660"], 2.4, tol=0.05)
    later = share.loc[["1631-1640", "1641-1650", "1651-1660"]].to_numpy()
    assert later[0] < share["1621-1630"] and later[1] < later[0] and later[2] < later[1]
    print("ok  Table A: falls in every decade after 1630")
    total = H["sum_pesos"].sum()
    hamilton34 = F["quan1969_hamilton_total"][0]
    quoted("Table A summed (million pesos)", total / 1e6, 895.6, tol=0.05)
    quoted("Hamilton 1934 total (million pesos)", hamilton34 / 1e6, 447.8, tol=0.05)
    quoted("Table A / 1934 total", total / hamilton34, 2.0, tol=0.05)
    em = F["em_european_silver"]
    quoted("Europe's silver output, 1460s (t/yr): from 2.5", em[0], 2.5, tol=0)
    quoted("Europe's silver output, 1460s (t/yr): to 7", em[1], 7, tol=0)
    quoted("Europe's silver output, 1540s (t/yr): over 60", em[2], 60, tol=0)


def manila_flows(F, Mn):
    """sec:silver-world, 马尼拉; fig:silver_flows (b); ex:silver-scale."""
    m = Mn.set_index("year")
    for year, low, plus in [(1598, 1_000_000, 0), (1602, 2_000_000, 0), (1604, 2_500_000, 1),
                            (1620, 3_000_000, 0), (1633, 2_000_000, 0)]:
        quoted(f"Quan table 1: {year} (pesos)", m.loc[year, "low_pesos"], low, tol=0)
        quoted(f"  {year}: 'or more'", m.loc[year, "plus"], plus, tol=0)
    quoted("Quan: at most four million", F["quan1969_range"][1], 4_000_000, tol=0)
    quoted("Quan: at least one million", F["quan1969_range"][0], 1_000_000, tol=0)
    # fig:silver_flows (b) shows 1598-1700, while the cap of 1593/1595 (still 500,000 in 1636) held
    early = m.loc[1598:1700]
    common = early[(early["low_pesos"] >= 2_000_000) & (early["high_pesos"] <= 3_000_000)]
    print(f"ok  Quan table 1, 1598-1700: {len(common)} of {len(early)} estimates within 2-3 million")
    assert len(common) >= len(early) - 1
    quoted("cap of the decrees of 1593 and 1595 (pesos)", F["quan1969_cap"][0], 500_000, tol=0)
    quoted("1636: silk worth 250,000 pesos", F["quan1969_permiso"][0], 250_000, tol=0)
    quoted("1636: silver back up to 500,000 pesos", F["quan1969_permiso"][1], 500_000, tol=0)
    quoted("Cerezo 1633: two millions", F["br24_1633"][0], 2_000_000, tol=0)
    quoted("De Comyn: 1571-1821 (years)", 1821 - 1571, 250, tol=0)
    quoted("De Comyn: 400 million pesos", F["quan1969_decomyn"][0], 400_000_000, tol=0)
    quoted("Quan: one half, 200 million pesos", F["quan1969_half"][0], F["quan1969_decomyn"][0] / 2, tol=0)
    quoted("peso in taels", F["quan1969_peso_tael"][0], TAEL_PER_PESO, tol=0)
    # ex:silver-scale
    taels = MANILA_PESOS * TAEL_PER_PESO
    quoted("ex:silver-scale (1): 2 million pesos x 0.72 (10,000 taels)", taels / 1e4, 144, tol=1e-9)
    quoted("  (2) / Xuanzong silver tax", taels / F["quan1968_yinke_xuanzong"][0], 5.6, tol=0.05)
    quoted("  (2) / Wuzong silver tax", taels / F["quan1968_yinke_wuzong"][0], 44, tol=0.5)
    quoted("  (2) / jinhuayin one million", taels / F["ming_1436_jinhua_total"][1], 1.4, tol=0.05)
    per_year = F["quan1969_half"][0] / 250
    quoted("  (3) 400 million x 1/2 / 250 (10,000 pesos)", per_year / 1e4, 80, tol=1e-9)
    quoted("  (3) in taels (10,000)", per_year * TAEL_PER_PESO / 1e4, 57.6, tol=1e-9)
    # De Comyn's total gives 1.6 million pesos a year at Manila, below Quan's usual 2-3 million
    quoted("  (3) De Comyn: 400 million / 250 (10,000 pesos a year)", F["quan1969_decomyn"][0] / 250 / 1e4, 160,
           tol=1e-9)
    assert F["quan1969_decomyn"][0] / 250 < 2_000_000
    low_ratio = per_year * TAEL_PER_PESO / F["quan1968_yinke_wuzong"][0]
    print(f"    flows / Wuzong silver tax: {low_ratio:.1f} (De Comyn) to {taels / F['quan1968_yinke_wuzong'][0]:.1f}")
    assert low_ratio > 10
    print("ok  either way, more than ten times Wuzong's silver tax ('十几倍以上')")


def china(F):
    """sec:silver-china: gold-silver ratios, ex:silver-arbitrage, the intuition box, fig:gold_silver_ratio."""
    fine, common, japan = F["br19_gold"]
    quoted("Canton, fine gold (taels of silver)", fine, 6.6, tol=0)
    quoted("Canton, common gold", common, 7, tol=0)
    quoted("Japan", japan, 8.3, tol=0)
    silk = F["br19_silk"]
    quoted("silk at Canton (taels/picul)", silk[0], 80, tol=0)
    quoted("silk in Japan, low", silk[1], 140, tol=0)
    quoted("silk in Japan, high", silk[2], 150, tol=0)
    eu16, eu17 = F["em_barrett"]
    quoted("Barrett: 16th century", eu16, 11.3, tol=0)
    quoted("Barrett: 17th century", eu17, 13.9, tol=0)
    quoted("tael = ducat of ten reals; a mace = one real", F["br19_tae"][0] / F["br19_tae"][1], 10, tol=0)
    # ex:silver-arbitrage: the memorial's 6.6 and 7 are read as the two ends of one range for Canton
    quoted("(1) Japan/Canton at the high end 7 (%)", 100 * arbitrage_gross(japan, common), 18.6, tol=0.05)
    quoted("(1) Japan/Canton at the low end 6.6 (%)", 100 * arbitrage_gross(japan, fine), 25.8, tol=0.05)
    quoted("(2) Europe 16th c. / 6.6 (%)", 100 * arbitrage_gross(eu16, fine), 71.2, tol=0.05)
    quoted("(2) Europe 16th c. / 7 (%)", 100 * arbitrage_gross(eu16, common), 61.4, tol=0.05)
    quoted("(2) Europe 17th c. / 7 (%)", 100 * arbitrage_gross(eu17, common), 98.6, tol=0.05)
    quoted("(3) teaching cost c (%)", 100 * ARBITRAGE_COST, 20, tol=0)
    assert arbitrage_gross(japan, fine) > ARBITRAGE_COST > arbitrage_gross(japan, common)
    print("ok  (3) at 6.6 the trade clears c = 20%, at 7 it does not: the gap is about the size of c")
    quoted("(4) silk 140/80 - 1 (%)", 100 * (silk[1] / silk[0] - 1), 75, tol=1e-9)
    quoted("(4) silk 150/80 - 1 (%)", 100 * (silk[2] / silk[0] - 1), 87.5, tol=1e-9)
    assert arbitrage_gross(eu16, common) > arbitrage_gross(japan, fine)
    print("ok  the Europe-China gap exceeds the Japan-China gap")
    quoted("Grau y Monfalcón 1637: one hundred to two hundred", F["br27_1637"][1] / F["br27_1637"][0], 2, tol=0)
    # fig:gold_silver_ratio: order of the bars
    assert F["ming_1397_gold"][0] / F["ming_1397_silver"][0] < fine < common < japan < eu16 < eu17
    print("ok  ratios in order: Ming 5 < Canton 6.6-7 < Japan 8.3 < Europe 11.3 < 13.9")
    # case box
    quoted("1593: 250 Chinese pressed to row", F["ming_1593_campaign"][0], 250, tol=0)
    quoted("Jiyi: gold 100,000 taels a year", F["ming_jiyi_date"][0], 100_000, tol=0)
    quoted("Jiyi: silver 300,000 taels a year", F["ming_jiyi_date"][1], 300_000, tol=0)
    quoted("1603: 25,000 dead (narrative)", F["ming_1603_dead"][0], 25_000, tol=0)
    quoted("1604 edict: 20,000 merchants", F["ming_1603_edict"][0], 20_000, tol=0)


def tiaobian(F):
    """sec:silver-tiaobian and ex:silver-burden; selfcheck 3."""
    quoted("Wanli 9 = 1581", 1573 + F["ming_tiaobian_1581"][0] - 1, 1581, tol=0)
    quoted("Wanli 46 = 1618", 1573 + 46 - 1, 1618, tol=0)
    quoted("Liaoxiang 1618: three million", F["ming_liaoxiang_1618"][0], 3_000_000, tol=0)
    first = 0.0035
    quoted("first levy: 3 li 5 hao (taels/mu)", F["ming_liaoxiang_more"][0], first, tol=0)
    quoted("  raised over two million", F["ming_liaoxiang_first"][0], 2_000_000, tol=0)
    total = first + F["ming_liaoxiang_more"][0] + F["ming_liaoxiang_more"][1]
    quoted("3.5 + 3.5 + 2 li = 9 li (taels/mu)", total, 0.009, tol=1e-12)
    quoted("nine li raised 5.2 million a year", F["ming_liaoxiang_total"][0], 5_200_000, tol=0)
    rate = F["ming_1436_jinhua_rate"][0]
    quoted("(1) 0.009 / 0.25 (shi)", total / rate, 0.036, tol=1e-12)
    quoted("(1)  in sheng", 100 * total / rate, 3.6, tol=1e-9)
    mu1 = F["ming_liaoxiang_first"][0] / first
    mu2 = F["ming_liaoxiang_total"][0] / total
    quoted("(2) 2,000,000 / 0.0035 (100 million mu)", mu1 / 1e8, 5.71, tol=0.005)
    quoted("(2) 5,200,000 / 0.009 (100 million mu)", mu2 / 1e8, 5.78, tol=0.005)
    quoted("(2) the two differ by (%)", 100 * (mu2 / mu1 - 1), 1, tol=0.5)
    low = rate * GRAIN_PRICE_FALL
    quoted("(3) grain price halved (taels/shi)", low, 0.125, tol=1e-12)
    quoted("(3) 0.009 / 0.125 (shi)", total / low, 0.072, tol=1e-12)
    quoted("(3)  in sheng", 100 * total / low, 7.2, tol=1e-9)
    quoted("Wuzong: 'a few tens of thousands' of taels", F["quan1968_yinke_wuzong"][0] / 1e4, 3.3, tol=0.05)
    # selfcheck 3
    quoted("selfcheck 3: 1 / 0.5 (shi)", 1 / 0.5, 2, tol=0)
    quoted("selfcheck 3: 1 / 0.4 (shi)", 1 / 0.4, 2.5, tol=1e-12)
    quoted("selfcheck 3: burden up (%)", 100 * (2.5 / 2 - 1), 25, tol=1e-9)


def malestroit(F):
    """sec:silver-revolution, 马莱斯特鲁瓦的悖论 and 博丹的回答; selfcheck 5 is in england()."""
    quoted("Malestroit: nothing dearer in three hundred years", 300, F["malestroit_1566"][0], tol=0)
    quoted("Philip VI began to reign", F["malestroit_philippe"][0], 1328, tol=0)
    then_l, then_e = F["malestroit_velvet_then"]
    now_l, now_e, now_s = F["malestroit_velvet_now"]
    quoted("écu then (sous)", F["malestroit_ecu20"][0], 20, tol=0)
    quoted("velvet then (livres)", then_l, 4, tol=0)
    quoted("velvet now (livres)", now_l, 10, tol=0)
    quoted("écu now (sous)", now_s, 50, tol=0)
    quoted("then: 4 livres = 4 écus at 20 sous", then_l * 20 / F["malestroit_ecu20"][0], then_e, tol=0)
    quoted("now: 10 livres = 4 écus at 50 sous", now_l * 20 / now_s, now_e, tol=0)
    quoted("velvet up in livres 'by 1.5 times'", now_l / then_l - 1, 1.5, tol=0)
    quoted("10/4 = 50/20 = 2.5", now_l / then_l, now_s / F["malestroit_ecu20"][0], tol=0)
    quoted("Le Branchu: Bodin's rise of three to four times", F["lebranchu_bodin_3to4"][1], 4, tol=0)
    quoted("Bodin 1568: three causes", F["bodin1568_causes"][0], 3, tol=0)
    quoted("the fifth cause of 1578", F["lebranchu_fifth"][0], 5, tol=0)
    quoted("Bodin: from 1533", F["bodin_peru"][0], 1533, tol=0)
    quoted("Bodin: wages in Spain three times", F["bodin_triple"][0], 3, tol=0)


def england_qty(F, E):
    """tab:silver-england, ex:silver-qty, sec:silver-revolution and sec:silver-test; selfcheck 4-5."""
    idx = {c: 100.0 * E[c] / E.loc[1500, c] for c in ("Y", "P", "P_ag")}
    table = {1500: (0.75, 100, 100, 5.53, 172.6, 100), 1530: (1.29, 118, 123, 4.68, 153.4, 110),
             1560: (1.72, 151, 218, 7.97, 115.1, 145), 1590: (3.24, 160, 312, 6.42, 115.1, 208),
             1600: (3.68, 192, 328, 7.15, 111.8, 212), 1630: (6.33, 201, 429, 5.68, 111.4, 277),
             1660: (11.64, 252, 464, 4.18, 111.4, 299), 1690: (10.75, 318, 490, 6.05, 111.4, 316)}
    for dec, (m, y, p, v, ag, pag) in table.items():
        quoted(f"table {dec}s: coin (£m)", E.loc[dec, "M"], m, tol=0.005)
        quoted(f"table {dec}s: real output (index)", idx["Y"][dec], y, tol=0.5)
        quoted(f"table {dec}s: prices (index)", idx["P"][dec], p, tol=0.5)
        quoted(f"table {dec}s: velocity PY/M", E.loc[dec, "V"], v, tol=0.005)
        quoted(f"table {dec}s: grams of silver per pound", E.loc[dec, "ag"], ag, tol=0.05)
        quoted(f"table {dec}s: silver prices (index)", idx["P_ag"][dec], pag, tol=0.5)
    s, _ = load_snapshot("gpih_silver_pound")
    s = s.set_index("year")["grams_ag_per_gbp_mint"]
    assert s.loc[1490:1523].nunique() == 1 and s[1524] < s[1523] and s.loc[1601:1700].nunique() == 1
    quoted("grams per pound 1490-1523", s[1490], 172.6, tol=0.05)
    quoted("grams per pound from 1601", s[1601], 111.4, tol=0.05)
    # ex:silver-qty
    a, b = QUANTITY_DECADES
    r = {c: E.loc[b, c] / E.loc[a, c] for c in ("M", "Y", "P", "V", "ag", "P_ag")}
    quoted("(given) coin 1500s -> 1600s", r["M"], 4.88, tol=0.005)
    quoted("(given) real output", r["Y"], 1.92, tol=0.005)
    quoted("(given) prices", r["P"], 3.28, tol=0.005)
    quoted("(given) grams per pound", r["ag"], 0.648, tol=0.0005)
    quoted("(1) V1/V0 = 3.28 x 1.92 / 4.88", 3.28 * 1.92 / 4.88, 1.29, tol=0.005)
    quoted("(1) from the data", r["V"], 1.29, tol=0.005)
    rates = {c: 100 * compound(r[c], b - a) for c in ("M", "Y", "P", "V", "P_ag")}
    quoted("(2) money (%/yr)", rates["M"], 1.60, tol=0.005)
    quoted("(2) output (%/yr)", rates["Y"], 0.66, tol=0.005)
    quoted("(2) prices (%/yr)", rates["P"], 1.19, tol=0.005)
    quoted("(2) velocity (%/yr)", rates["V"], 0.26, tol=0.005)
    quoted("(2) 1.60 + 0.26 - 0.66", 1.60 + 0.26 - 0.66, 1.20, tol=1e-9)
    quoted("(3) 3.28 x 0.648 (rounded inputs)", 3.28 * 0.648, 2.13, tol=0.005)
    quoted("(3) silver prices from the data", r["P_ag"], 2.12, tol=0.005)
    quoted("(3) silver prices (%/yr)", rates["P_ag"], 0.76, tol=0.005)
    share = math.log(1 / r["ag"]) / math.log(r["P"])
    quoted("(3) debasement share of the log rise (%)", 100 * share, 37, tol=0.5)
    quoted("(3)  rest (%)", 100 * (1 - share), 63, tol=0.5)
    assert share > 1 / 3
    print("ok  debasement explains more than a third")
    quoted("1.2% a year for a hundred years", 1.012 ** 100, 3.3, tol=0.05)
    em = F["em_rates"]
    quoted("Edo & Melitz: about four-fold", em[0], 4, tol=0)
    quoted("Edo & Melitz: no higher than 1.25%", em[1], 1.25, tol=0)
    quoted("Edo & Melitz: England 1.1%", em[2], 1.1, tol=0)
    quoted("velocity 1500s -> 1600s (%)", 100 * (r["V"] - 1), 29, tol=0.5)
    # sec:silver-test
    quoted("England prices 1500s -> 1540s", E.loc[1540, "P"] / E.loc[1500, "P"], 1.37, tol=0.005)
    late = {c: E.loc[1690, c] / E.loc[1660, c] for c in ("M", "Y", "P", "V")}
    quoted("1660s -> 1690s coin (%)", 100 * (late["M"] - 1), -8, tol=0.5)
    quoted("1660s -> 1690s output (%)", 100 * (late["Y"] - 1), 27, tol=0.5)
    quoted("1660s -> 1690s prices (%)", 100 * (late["P"] - 1), 6, tol=0.5)
    quoted("1660s -> 1690s velocity (%)", 100 * (late["V"] - 1), 45, tol=0.5)
    quoted("coin 1630s -> 1640s (%, 'nearly seventy')", 100 * (E.loc[1640, "M"] / E.loc[1630, "M"] - 1), 69, tol=1.0)
    # selfcheck 4 and 5
    v = 1.2 * 1.2 / 1.5
    quoted("selfcheck 4: V1/V0", v, 0.96, tol=1e-12)
    quoted("selfcheck 4: per year (%)", 100 * compound(v, 10), -0.41, tol=0.005)
    quoted("selfcheck 5: 3 x 111.4 (g)", 3 * 111.4, 334.2, tol=1e-9)
    quoted("selfcheck 5: / 172.6", 3 * 111.4 / 172.6, 1.94, tol=0.005)


def malthus(F, C, E):
    """sec:silver-revolution, 人口的解释 and ex:silver-malthus; the deeper box on two population series."""
    a, b = QUANTITY_DECADES
    quoted("alpha (Ch. 11)", ALPHA, 0.405, tol=0.0005)
    pop = C["pop_england_m"]
    quoted("Clark: 1500s population (10,000)", pop[a] * 100, 256, tol=0.5)
    quoted("Clark: 1600s population (10,000)", pop[b] * 100, 440, tol=0.5)
    quoted("Broadberry: 1500s population (10,000)", E.loc[a, "pop"] * 100, 223, tol=0.5)
    quoted("Broadberry: 1600s population (10,000)", E.loc[b, "pop"] * 100, 427, tol=0.5)
    L = pop[b] / pop[a]
    quoted("Clark: 1600s / 1500s", L, 1.72, tol=0.005)
    w, s = factor_prices(L)
    quoted("(1) model real wage", w, 0.80, tol=0.005)
    quoted("(1) model real rent", s, 1.38, tol=0.005)
    quoted("(1) wage falls (%)", 100 * (1 - w), 20, tol=0.5)
    quoted("(1) rent rises (%)", 100 * (s - 1), 38, tol=0.5)
    farm = C.loc[b, "real_farm_1860s_100"] / C.loc[a, "real_farm_1860s_100"]
    blab = C.loc[b, "real_blab_1860s_100"] / C.loc[a, "real_blab_1860s_100"]
    rent = C.loc[b, "real_rent"] / C.loc[a, "real_rent"]
    quoted("(2) real farm wage", farm, 0.59, tol=0.005)
    quoted("(2) real building labourer wage", blab, 0.60, tol=0.005)
    quoted("(2) real land rent", rent, 1.82, tol=0.005)
    quoted("(2) wages fell 'about 40%'", 100 * (1 - (farm + blab) / 2), 40, tol=1.0)
    quoted("(2) rent rose (%)", 100 * (rent - 1), 82, tol=0.5)
    quoted("(2) wage fall, data / model ('about twice')", (1 - (farm + blab) / 2) / (1 - w), 2, tol=0.1)
    quoted("(2) rent rise, data / model ('about twice')", (rent - 1) / (s - 1), 2, tol=0.2)
    Lb = E.loc[b, "pop"] / E.loc[a, "pop"]
    quoted("(3) Broadberry 1600s / 1500s", Lb, 1.91, tol=0.005)
    wb, sb = factor_prices(Lb)
    quoted("(3) model real wage", wb, 0.77, tol=0.005)
    quoted("(3) model real rent", sb, 1.47, tol=0.005)
    assert wb > max(farm, blab) and sb < rent
    print("ok  (3) still smaller changes than the data")
    col = C.loc[b, "col_1860s_100"] / C.loc[a, "col_1860s_100"]
    quoted("Clark: cost of living 1600s / 1500s", col, 3.78, tol=0.005)
    nominal = [C.loc[b, k] / C.loc[a, k] for k in ("farm_wage_d", "blab_wage_d", "bcraft_wage_d")]
    print(f"    nominal day wages 1600s / 1500s: {', '.join(f'{x:.3f}' for x in nominal)}")
    assert 2.2 <= min(nominal) and max(nominal) < 2.3 + 0.005
    print("ok  nominal wages rose 2.2-2.3 times")
    quoted("Clark: nominal land rents", C.loc[b, "land_rents_gbp_m"] / C.loc[a, "land_rents_gbp_m"], 6.85, tol=0.005)
    # compare box: 'real wages about 0.6'
    quoted("compare box: real wages about 0.6", (farm + blab) / 2, 0.6, tol=0.01)
    # deeper box: the two population series
    quoted("Clark: 1590s (10,000)", pop[1590] * 100, 355, tol=0.5)
    quoted("Clark: 1590s -> 1600s (%)", 100 * (pop[1600] / pop[1590] - 1), 24, tol=0.5)
    quoted("Broadberry: 1590s (10,000)", E.loc[1590, "pop"] * 100, 400, tol=0.5)


def test_cities(Al, E):
    """sec:silver-test: Bodin's ranking and the spread of prices; fig:price_revolution (b)."""
    quoted("Valencia silver prices 1500s -> 1540s", Al.loc[1540, "valencia"] / Al.loc[1500, "valencia"], 1.30, tol=0.005)
    for dec, vals in [(1560, dict(valencia=1.23, madrid=1.38, paris=1.03, florence=0.83, naples=0.83)),
                      (1570, dict(valencia=1.51, madrid=1.56, paris=1.27, florence=0.92, naples=0.90))]:
        for city, v in vals.items():
            quoted(f"Allen {dec}s: {city}", Al.loc[dec, city], v, tol=0.005)
        assert min(Al.loc[dec, ["valencia", "madrid"]]) > Al.loc[dec, "paris"] > max(Al.loc[dec, ["florence", "naples"]])
        print(f"ok  Allen {dec}s: Spain > France > Italy")
    for city, v in [("valencia", 2.94), ("paris", 2.53), ("london", 2.22), ("florence", 1.95), ("krakow", 1.94),
                    ("antwerp", 3.00)]:
        quoted(f"Allen 1600s / 1500s: {city}", Al.loc[1600, city] / Al.loc[1500, city], v, tol=0.005)
    quoted("Valencia / Krakow, 1500s", Al.loc[1500, "valencia"] / Al.loc[1500, "krakow"], 1.72, tol=0.005)
    quoted("Valencia / Krakow, 1600s", Al.loc[1600, "valencia"] / Al.loc[1600, "krakow"], 2.60, tol=0.005)
    start = Al.loc[1500].dropna()
    assert start.idxmin() == "antwerp", start.idxmin()
    print("ok  Antwerp has the lowest level of the 1500s")


def castile_fiscal(F, C, T):
    """sec:silver-default: revenue, the case box, tab:silver-castile, ex:silver-debt, fig:philip_debt."""
    quoted("defaults: 1557, 1560, 1575, 1596", sum(F["dv_four"]), 1557 + 1560 + 1575 + 1596, tol=0)
    quoted("Spain: 13 defaults 1500-1900", F["dv_thirteen"][0], 13, tol=0)
    quoted("Cortes-approved taxes 1555-1596 (%)", F["dv_cortes43"][0], 43, tol=0)
    quoted("one ducat in four from silver (%)", F["dv_one_in_four"][0], 25, tol=0)
    quoted("Indies share 1566-1574 (%)", 100 * indies_share(C, 1566, 1574), 16.2, tol=0.05)
    quoted("Indies share 1575-1584 (%)", 100 * indies_share(C, 1575, 1584), 20.3, tol=0.05)
    quoted("Indies share 1585-1596 (%)", 100 * indies_share(C, 1585, 1596), 24.5, tol=0.05)
    quoted("Indies 1594", C.loc[1594, "indies"], 0, tol=0)
    quoted("Indies share 1595 (%)", 100 * C.loc[1595, "indies_share"], 40.8, tol=0.05)
    quoted("dips before 1560, 1575, 1596: three of four", F["dv_three_of_four"][0], len(F["dv_dips"]), tol=0)
    # fig:philip_debt (a): the troughs of 1572-1574 and 1594 before the defaults of 1575 and 1596
    low, before = C.loc[1572:1574, "indies"], C.loc[1566:1571, "indies"]
    print(f"    Indies 1572-1574: {low.min():.2f}-{low.max():.2f}; mean of 1566-1571: {before.mean():.2f}")
    assert low.max() < before.mean() and C.loc[1594, "indies"] == 0
    print("ok  Indies revenue dips in 1572-1574 and 1594")
    dr = C["debt_ratio"]
    quoted("debt/revenue 1574", dr[1574], 7.4, tol=0.05)
    assert dr.loc[1566:1596].idxmax() == 1594 and dr.loc[1566:1574].idxmax() == 1574
    quoted("debt/revenue 1594", dr[1594], 8.1, tol=0.05)
    after = dr.loc[1577:1581]
    print(f"    debt/revenue 1577-1581: {after.min():.2f}-{after.max():.2f}")
    assert 4.0 <= after.min() and after.max() < 5.0
    print("ok  after the 1575 default the ratio falls back to 4-5")
    quoted("asientos 1565-1596: debt rose 40.9", F["dv_asiento_total"][0], 40.9, tol=0)
    quoted("asientos contracted 92.1", F["dv_asiento_total"][1], 92.1, tol=0)
    rise_share = F["dv_asiento_total"][0] / F["dv_asiento_total"][1]
    print(f"    debt increase / asientos contracted: {rise_share:.3f}")
    assert rise_share < 0.5
    print("ok  the rise in debt is less than half of the asientos ('还不到借款总额的一半')")
    # case box
    quoted("1574 military (million ducats)", C.loc[1574, "military"], 7.06, tol=0.005)
    quoted("1574 revenue", C.loc[1574, "revenue"], 5.65, tol=0.005)
    quoted("1574 Indies", C.loc[1574, "indies"], 0.70, tol=0.005)
    quoted("1574 Indies share (%)", 100 * C.loc[1574, "indies_share"], 12.4, tol=0.05)
    quoted("1574 primary surplus", C.loc[1574, "primary_surplus"], -1.97, tol=0.005)
    quoted("1575: 14.6 million outstanding", F["dv_1575"][0], 14.6, tol=0)
    quoted("  two years of revenue (1575)", F["dv_1575"][0] / C.loc[1575, "revenue"], 2, tol=0.4)
    quoted("1577: 62% repaid", F["dv_1575_repaid"][0], 62, tol=0)
    quoted("fresh lending from 1578", F["dv_fresh_lending"][0], 1578, tol=0)
    quoted("surpluses from 50% of revenue", F["dv_1577_surplus"][0], 50, tol=0)
    quoted("surpluses to 70% of revenue", F["dv_1577_surplus"][1], 70, tol=0)
    big = C.loc[1578:1584, "primary_surplus"] / C.loc[1578:1584, "revenue"]
    print(f"    primary surplus / revenue 1578-1584: {big.min():.2f}-{big.max():.2f}")
    quoted("1597: 7.04 million", F["dv_1597"][0], 7.04, tol=0)
    quoted("1597: two thirds of a year's revenue", F["dv_1597"][0] / C.loc[1596, "revenue"], 2 / 3, tol=0.1)
    quoted("1597: 80% repaid", F["dv_1597_repaid"][0], 80, tol=0)
    quoted("GDP estimates differ by over 200%", F["dv_gdp_uncertain"][0], 200, tol=0)
    # tab:silver-castile: Table 3 as printed and recomputed
    table = {"1565-74": (3.38, 10.20, 0.394, 0.249, 3.645, 5.863), "1574-84": (3.28, 9.30, 0.433, 0.454, 7.534, 4.787),
             "1584-96": (3.44, 8.80, 0.227, 0.201, 3.744, 5.728), "1565-96": (3.37, 9.40, 0.348, 0.315, 5.229, 5.476)}
    for period, (g, r, pss, ps, ds, d) in table.items():
        row = T.loc[period]
        for k, v in zip(("g", "r", "PS_star", "PS", "D_star", "D"), (g, r, pss, ps, ds, d)):
            quoted(f"Table 3 {period}: {k}", row[k], v, tol=0)
        quoted(f"  {period}: D* = PS/(r-g) recomputed", d_star(ps, r / 100, g / 100), ds, tol=0.02)
    for period, year in [("1574-84", 1574), ("1584-96", 1584)]:
        row = T.loc[period]
        quoted(f"  {period}: ps* from the {year} ratio", ps_star(dr[year], row["r"] / 100, row["g"] / 100),
               row["PS_star"], tol=0.002)
    # ex:silver-debt
    row = T.loc["1574-84"]
    quoted("(1) 1574 debt (million ducats)", C.loc[1574, "debt"], 42.02, tol=0.005)
    d0 = 42.02 / 5.65
    quoted("(1) d = 42.02 / 5.65", d0, 7.44, tol=0.005)
    quoted("(1) ps*", ps_star(d0, row["r"] / 100, row["g"] / 100), 0.433, tol=0.0005)
    quoted("(1) actual", row["PS"], 0.454, tol=0)
    quoted("(1) debt/revenue 1584", dr[1584], 4.38, tol=0.005)
    jump = C.loc[1575, "revenue"] / C.loc[1574, "revenue"] - 1
    print(f"    revenue 1575 / 1574 - 1: {jump:.3f}")
    assert 0.30 <= jump < 0.40
    print("ok  (1) and case box: revenue in 1575 a third or more above 1574 ('三成多')")
    # a surplus 0.02 above ps* alone would have lowered the ratio only a little in ten years
    alone = debt_path(d0, row["PS"], row["r"] / 100, row["g"] / 100, 10)[-1]
    print(f"    debt/revenue after ten years at the period-average r, g and PS: {alone:.2f} (actual 1584: {dr[1584]:.2f})")
    assert alone > 6.5 > dr[1584]
    print("ok  (1) the fall to 4.38 is not explained by the average surplus alone")
    whole = T.loc["1565-96"]
    rg = (whole["r"] - whole["g"]) / 100
    quoted("(2) r - g", rg, 0.0603, tol=1e-9)
    quoted("(2) D* = 0.315 / 0.0603", d_star(whole["PS"], whole["r"] / 100, whole["g"] / 100), 5.22, tol=0.005)
    quoted("(2) actual D", whole["D"], 5.48, tol=0.005)
    quoted("(2) gap, about a quarter of a year", whole["D"] - 5.22, 0.25, tol=0.02)
    share = indies_share(C, 1566, 1596)
    quoted("(3) Indies share 1566-1596 (%)", 100 * share, 21.5, tol=0.05)
    if SILVER_VANISHES:
        ps_left = round(whole["PS"] - round(share, 3), 3)
        quoted("(3) 0.315 - 0.215", ps_left, 0.100, tol=1e-9)
        new_rev = 1 - round(share, 3)
        quoted("(3) new revenue", new_rev, 0.785, tol=1e-9)
        quoted("(3) 0.100 / 0.785", ps_left / new_rev, 0.127, tol=0.0005)
        quoted("(3) D* = 0.127 / 0.0603", 0.127 / rg, 2.11, tol=0.005)
        quoted("(3) old debt on new revenue 5.48 / 0.785", 5.48 / new_rev, 6.98, tol=0.005)
    # what Drelichman & Voth say
    quoted("required 35%", F["dv_required"][0], 35, tol=0)
    quoted("  Table 3: 0.348", whole["PS_star"], 0.35, tol=0.005)
    quoted("attained 31.5%", F["dv_required"][1], 31.5, tol=0)
    quoted("sustainable 5.2", F["dv_sustainable"][0], 5.2, tol=0)
    quoted("actual 5.5", F["dv_sustainable"][1], 5.5, tol=0)
    quoted("Armada: over 10 million", F["dv_armada"][1], 10, tol=0)
    quoted("counterfactual 39 million", F["dv_counterfactual"][0], 39, tol=0)
    quoted("actual 66 million", F["dv_counterfactual"][1], 66, tol=0)
    quoted("debts 60% of GDP", F["dveeh_gdp"][0], 60, tol=0)
    ret = F["dveeh_return"]
    quoted("asiento return 15.5%", ret[0], 15.5, tol=0)
    quoted("reinvestment rate 7.14%", ret[1], 7.14, tol=0)
    quoted("finance rate 5%", ret[2], 5, tol=0)
    quoted("1575 settlement cut 'over three tenths'", 100 - F["dv_1575_repaid"][0], 38, tol=0)
    # selfcheck 6
    quoted("selfcheck 6: 0.30 / 0.05", d_star(0.30, 0.08, 0.03), 6, tol=1e-9)
    quoted("selfcheck 6: 0.30 / 0.07", d_star(0.30, 0.10, 0.03), 4.3, tol=0.05)
    quoted("selfcheck 6: fall (%, 'nearly three tenths')", 100 * (1 - d_star(0.30, 0.10, 0.03) / 6), 28.6, tol=0.05)
    # the debt path: with ps = ps* the ratio is constant
    path = debt_path(d0, ps_star(d0, row["r"] / 100, row["g"] / 100), row["r"] / 100, row["g"] / 100, 10)
    assert abs(path[-1] - d0) < 1e-9
    print("ok  with ps = ps* the debt ratio stays at 7.44")


def selfcheck_2():
    """selfcheck 2: ratios 12 and 8, cost 30%; then 9.5."""
    quoted("12/8 - 1 (%)", 100 * arbitrage_gross(12, 8), 50, tol=1e-9)
    quoted("12/9.5 - 1 (%)", 100 * arbitrage_gross(12, 9.5), 26.3, tol=0.05)
    assert arbitrage_gross(12, 8) > 0.30 > arbitrage_gross(12, 9.5)
    print("ok  selfcheck 2: 50% clears 30%, 26.3% does not")


def units(F):
    """Deeper box 单位、数据与几处不一致."""
    pes = F["hamilton_peso"]
    quoted("peso = 450 maravedís", pes[0], 450, tol=0)
    quoted("652.635 grains", pes[1], 652.635, tol=0)
    quoted("522.09 grains", pes[2], 522.09, tol=0)
    grams = pes[1] * GRAIN_PER_GRAM
    quoted("652.635 grains in grams", grams, 42.29, tol=0.005)
    tonnes = F["quan1969_hamilton_total"][0] * grams / 1e6
    quoted("447.8 million pesos in silver (10,000 t)", tonnes / 1e4, 1.89, tol=0.005)
    ag, au = F["hamilton_kg"]
    eq = (ag + au * F["em_barrett"][0]) / 1000
    quoted("Hamilton 1929 weights, gold at 11.3 (10,000 t)", eq / 1e4, 1.87, tol=0.005)
    quoted("the two differ by (%)", 100 * (tonnes / eq - 1), 1.4, tol=0.05)
    quoted("ducat = ten reals", F["br19_tae"][0], 10, tol=0)


def from_quotes(Q):
    """Numbers the text takes straight from a quotation."""
    said(Q, "br10_1598", "a million")
    said(Q, "br19_gold", "six taes six maçes", "seven taes", "eight taes and three maçes")
    said(Q, "br19_silk", "eighty taes", "one hundred and forty", "one hundred and fifty")
    said(Q, "br19_tae", "ten reals")
    said(Q, "br24_1633", "two millions")
    said(Q, "br27_1637", "one hundred", "two hundred")
    said(Q, "malestroit_1566", "trois cens ans")
    said(Q, "malestroit_philippe", "mil trois cens vingt hu")
    said(Q, "malestroit_ecu20", "vingt solz")
    said(Q, "malestroit_velvet_then", "quatre livres")
    said(Q, "malestroit_velvet_now", "dix livres", "quatre escuz", "cinquante")
    said(Q, "lebranchu_bodin_3to4", "trois à quatre fois", "un siècle")
    said(Q, "bodin1568_causes", "trois causes")
    said(Q, "bodin1568_principal", "quatre cens ans")
    said(Q, "bodin_causes_1578", "quatre ou cinq causes", "quatre cens ans")
    said(Q, "lebranchu_fifth", "cinquiesme")
    said(Q, "bodin_peru", "1533", "cent milions d'or", "deux fois autant d'argent")
    said(Q, "bodin_triple", "triple")
    said(Q, "hamilton_peso", "450", "652.635", "December 23, 1642", "522.09")
    said(Q, "hamilton_kg", "16,632,648.20", "181,234.95")
    said(Q, "hamilton_potosi", "1545")
    said(Q, "hamilton_public", "1536", "1660", "26.2 per cent")
    said(Q, "hamilton_smuggling", "ten to fifty per cent")
    said(Q, "dv_quint", "20%")
    said(Q, "dv_one_in_four", "one in four")
    said(Q, "dv_four", "1557", "1560", "1575", "1596")
    said(Q, "dv_thirteen", "13 times", "1500", "1900")
    said(Q, "dv_cortes43", "1555", "1596", "43%")
    said(Q, "dv_dips", "1560", "1575", "1596")
    said(Q, "dv_three_of_four", "three of the four")
    said(Q, "dv_philippines", "1571")
    said(Q, "dv_1540s", "1540s")
    said(Q, "dv_1566_resumed", "1566")
    said(Q, "dv_asiento_total", "40.9 million", "1565", "1596", "92.1 million")
    said(Q, "dv_1575", "14.6 million", "two years")
    said(Q, "dv_1575_repaid", "62 percent", "five million")
    said(Q, "dv_fresh_lending", "1578")
    said(Q, "dv_1577_surplus", "1577", "50 and 70 percent")
    said(Q, "dv_1597", "7.04 million", "two thirds")
    said(Q, "dv_1597_repaid", "80 percent")
    said(Q, "dv_gdp_uncertain", "200 percent")
    said(Q, "dv_required", "35 percent", "31.5 percent")
    said(Q, "dv_sustainable", "5.2 times", "5.5 times")
    said(Q, "dv_armada", "1588", "10 million", "two years")
    said(Q, "dv_counterfactual", "39 million", "66 million")
    said(Q, "dveeh_gdp", "60%")
    said(Q, "dveeh_serial", "four times", "first serial defaulter")
    said(Q, "dveeh_return", "7.14%", "5%", "15.5%", "more than double")
    said(Q, "dvej_cheat", "Kletzer and Wright, 2000")
    said(Q, "em_rates", "4-fold", "1530-1660", "1.25 percent", "1.1 percent")
    said(Q, "em_european_silver", "2.5 to 7 tonnes", "1460s", "over 60 tonnes", "1540s", "about 1540")
    said(Q, "em_barrett", "11.3:1", "13.9:1")
    said(Q, "em_timing", "1530s or 1540s", "1550s")
    said(Q, "em_timing2", "1550 to 1700", "1660-1700")
    said(Q, "quan1969_hamilton_total", "447,820,932.3", "百分之十至百分之五十")
    said(Q, "quan1969_potosi", "一五八一至一六〇〇", "254, 000", "百分之六十多")
    said(Q, "quan1968_world", "418,900")
    said(Q, "quan1968_yinke_chengzu", "1402—23", "224,313")
    said(Q, "quan1968_yinke_xuanzong", "1426—34", "256, 450")
    said(Q, "quan1968_yinke_wuzong", "1505—20", "32,920")
    said(Q, "quan1969_purchasing", "兩倍")
    said(Q, "quan1969_range", "四百萬", "一百萬", "二三百萬")
    said(Q, "quan1969_cap", "五十萬")
    said(Q, "quan1969_permiso", "二十五萬", "五十萬")
    said(Q, "quan1969_peso_tael", "七錢二分", "一兩")
    said(Q, "quan1969_decomyn", "一五七一年至一八二一年", "二百五十年", "四萬萬")
    said(Q, "quan1969_half", "四分之一", "二分之一", "二萬萬")
    said(Q, "quan1969_luzon_1565", "1565")
    said(Q, "quan1969_li_date", "萬曆三十一年")
    said(Q, "ming_1376_commute", "洪武九年", "一两", "千文", "一贯", "一石")
    said(Q, "ming_1397_gold", "十石")
    said(Q, "ming_1397_silver", "二石")
    said(Q, "ming_1397_double", "加一倍")
    said(Q, "ming_1436_jinhua_rate", "二钱五分")
    said(Q, "ming_1436_jinhua_total", "四百馀万石", "百万馀两")
    said(Q, "ming_1436_permanent", "四石", "一两")
    said(Q, "ming_yongle_ban", "三十万两")
    said(Q, "ming_tiaobian_1581", "万历九年")
    said(Q, "ming_liaoxiang_1618", "四十六年", "三百万")
    said(Q, "ming_liaoxiang_first", "三厘五毫", "二百万")
    said(Q, "ming_liaoxiang_more", "三厘五毫", "二厘")
    said(Q, "ming_liaoxiang_total", "九厘", "五百二十万")
    said(Q, "ming_1593_campaign", "二十一年", "二百五十")
    said(Q, "ming_jiyi_date", "十万两", "三十万两", "三十年七月")
    said(Q, "ming_1603_dead", "二万五千")
    said(Q, "ming_1603_edict", "二万")


def main():
    F, Q = facts(), quotes()
    H, Mn, E, C, Al, Cs, T = hamilton(), manila(), england(), clark(), allen(), castile(), table3()
    intro(F)
    ming_money(F)
    america(F, H)
    manila_flows(F, Mn)
    china(F)
    tiaobian(F)
    malestroit(F)
    england_qty(F, E)
    malthus(F, C, E)
    test_cities(Al, E)
    castile_fiscal(F, Cs, T)
    selfcheck_2()
    units(F)
    from_quotes(Q)
    print("all numbers in Chapter 13 check out")


if __name__ == "__main__":
    main()
