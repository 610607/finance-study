"""Chapter 2 (国民核算与恒等式): every number quoted in zh/ch02_accounts.tex.

    python3 checks/check_ch02.py

Inputs are two snapshots: accounts_facts (quotations from Kuznets's 1934 report, BEA's account of its origins,
the SNA 2008 and the UN page on the 2025 SNA, the NBS notes on China's move to the SNA and on the 2004 census
revision, Kanal & Kornegay's household-production account and the CSO's notice on Ireland's GNI*; checked by
data/fetch/verify_web_quotes.py, six rows read on page images) and bea_nipa_annual (US national accounts,
1929-2025, written by data/fetch/bea_nipa_annual.py from the BEA's bulk NIPA files). The figure module
figsrc/fig_ch02.py imports the functions defined here.

Identities (the chapter's key equations; all are accounting, none is a model):
    three approaches     GDP = sum of value added = C + I + G + X - M = W + Pi (+ taxes on production)   (eq:accounts-three)
    nominal and real     1 + g_nominal = (1 + g_real)(1 + g_deflator), P = Y / y                         (eq:accounts-deflator)
    capital stock        K' = K + I - D                                                                 (eq:accounts-capital)
    sector balances      (S - I) + (T - G) + (M - X) = 0                                                (eq:accounts-balances)
    national income      GNI = GDP + primary income from abroad - primary income paid abroad            (eq:accounts-gni)
The cotton economy (ex:accounts-cloth, ex:accounts-thrift) and the flow-of-funds table (tab:accounts-flows) are
teaching inputs, defined below and stated in the text.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import load_snapshot, quoted

# ---------------------------------------------------------------------------------------------------
# Teaching inputs stated in the text
# ex:accounts-cloth: one year of a closed economy with three firms (yuan). Output of the spinner includes
# 10 of yarn put into stock; the weaver sells all its cloth to households.
CHAIN = {
    "棉农": dict(output=30, inputs=0, wages=20),
    "纺纱厂": dict(output=60, inputs=30, wages=20),
    "织布厂": dict(output=80, inputs=50, wages=25),
}
SALES = {"棉农": 30, "纺纱厂": 50, "织布厂": 80}       # what each firm sells (the spinner stocks the rest)
CONSUMPTION = 80                                        # households buy all the cloth
THRIFT_CONSUMPTION = 70                                 # ex:accounts-thrift: households now buy cloth for 70

# tab:accounts-flows: a year of an economy with four sectors (GDP = 100). Signs: + receipt, - payment.
FLOW_INPUTS = dict(C=60, I=20, G=22, X=13, M=15, W=58, D=10, Pi_d=30, T=18)


def _facts_df() -> pd.DataFrame:
    df, _ = load_snapshot("accounts_facts", dtype={"value": str})
    return df


def facts() -> dict[str, list[float]]:
    """id -> the numbers of the value column (several are separated by ';')."""
    out = {}
    for _, r in _facts_df().iterrows():
        v = r["value"]
        if isinstance(v, str) and v.strip():
            out[r["id"]] = [float(x) for x in v.split(";")]
    return out


def bea() -> pd.DataFrame:
    df, _ = load_snapshot("bea_nipa_annual")
    return df.set_index("year")


# ---------------------------------------------------------------------------------------------------
# Models: accounting only
def kuznets_table(F) -> pd.DataFrame:
    """Kuznets (1934), Table 1, lines 1-3 (millions of dollars)."""
    rows = {y: F[f"k_table1_{y}"] for y in (1929, 1930, 1931, 1932)}
    return pd.DataFrame(rows, index=["paid_out", "business_savings", "produced"]).T


def chain_accounts(consumption: float = CONSUMPTION) -> dict[str, float]:
    """Production, expenditure and income measures of the cotton economy (eq:accounts-three).

    If households buy less cloth than the weaver made, the unsold cloth goes into stock at its market price;
    so the weaver's output and income do not change, and the stock change is counted as investment.
    """
    va = {k: v["output"] - v["inputs"] for k, v in CHAIN.items()}
    profits = {k: va[k] - CHAIN[k]["wages"] for k in CHAIN}
    stocks = (CHAIN["纺纱厂"]["output"] - SALES["纺纱厂"]) + (CHAIN["织布厂"]["output"] - consumption)
    income = sum(v["wages"] for v in CHAIN.values()) + sum(profits.values())
    return dict(production=sum(va.values()), expenditure=consumption + stocks, income=income,
                consumption=consumption, investment=stocks, saving=income - consumption,
                wages=sum(v["wages"] for v in CHAIN.values()), profits=sum(profits.values()),
                sum_of_sales=sum(SALES.values()), output=sum(v["output"] for v in CHAIN.values()),
                va_farmer=va["棉农"], va_spinner=va["纺纱厂"], va_weaver=va["织布厂"],
                profit_farmer=profits["棉农"], profit_spinner=profits["纺纱厂"], profit_weaver=profits["织布厂"])


def flow_table(p: dict = FLOW_INPUTS) -> dict[str, dict[str, float]]:
    """tab:accounts-flows: rows are transactions, columns sectors.

    Columns: households H, firms' current account Fc, firms' capital account Fk, government G, rest of the world R.
    Firms receive C, G, X and the sales of investment goods I, and pay M, wages and distributed profits; what is
    left on their current account is their gross saving (consumption of fixed capital D plus retained net profit).
    Their capital account buys the investment goods. Households receive W and Pi_d and pay C and T.
    Every row sums to zero: each payment is another account's receipt.
    """
    z = dict(H=0, Fc=0, Fk=0, G=0, R=0)
    T = {
        "消费": dict(z, H=-p["C"], Fc=+p["C"]),
        "投资": dict(z, Fc=+p["I"], Fk=-p["I"]),
        "政府购买": dict(z, Fc=+p["G"], G=-p["G"]),
        "出口": dict(z, Fc=+p["X"], R=-p["X"]),
        "进口": dict(z, Fc=-p["M"], R=+p["M"]),
        "工资": dict(z, H=+p["W"], Fc=-p["W"]),
        "分配的利润": dict(z, H=+p["Pi_d"], Fc=-p["Pi_d"]),
        "税": dict(z, H=-p["T"], G=+p["T"]),
    }
    return T


def gdp_of(p: dict = FLOW_INPUTS) -> float:
    return p["C"] + p["I"] + p["G"] + p["X"] - p["M"]


def net_lending(T) -> dict[str, float]:
    """Column sums: each account's net lending (+) or borrowing (-); firms = Fc + Fk."""
    col = {s: sum(row[s] for row in T.values()) for s in ("H", "Fc", "Fk", "G", "R")}
    return dict(H=col["H"], F=col["Fc"] + col["Fk"], G=col["G"], R=col["R"], Fc=col["Fc"], Fk=col["Fk"])


def avg_rate(x0: float, xT: float, years: float) -> float:
    return (xT / x0) ** (1.0 / years) - 1.0


def china_revision(F) -> pd.DataFrame:
    """NBS (2006), Table 1: GDP after and before the census revision, 1993-2004 (100 million yuan)."""
    cols = ["gdp_new", "p1_new", "p2_new", "p3_new", "gdp_old", "p1_old", "p2_old", "p3_old",
            "d_gdp", "d_p1", "d_p2", "d_p3"]
    df = pd.DataFrame({y: F[f"census_rev_{y}"] for y in range(1993, 2005)}, index=cols).T
    df["rev_pct"] = 100 * df.d_gdp / df.gdp_old
    df["tertiary_share"] = 100 * df.d_p3 / df.d_gdp
    return df


def sector_balances(B: pd.DataFrame) -> pd.DataFrame:
    """Net lending (+) or borrowing (-) as a percentage of GDP; the rest of the world is minus the nation."""
    x = B.loc[1960:]
    return pd.DataFrame({"private": 100 * x.net_lending_private / x.gdp,
                         "government": 100 * x.net_lending_government / x.gdp,
                         "rest_of_world": -100 * x.net_lending_nation / x.gdp})


# ---------------------------------------------------------------------------------------------------
def world(F):
    print("-- 2.1 the world of 1932-1934")
    quoted("Senate Resolution", F["bea_resolution"][0], 220, tol=0)
    quoted("  asked for 1929-1931", F["bea_resolution"][2], 1931, tol=0)
    quoted("report transmitted to the Senate (1934-01-04): year", F["k_transmitted"][0], 1934, tol=0)
    quoted("  day of January", F["k_transmitted"][1], 4, tol=0)
    K = kuznets_table(F)
    for y in (1929, 1930, 1931, 1932):
        assert K.loc[y, "paid_out"] + K.loc[y, "business_savings"] == K.loc[y, "produced"], y
    quoted("Table 1 identity 1929: 81,136 + 1,896", K.loc[1929, "paid_out"] + K.loc[1929, "business_savings"], 83_032, tol=0)
    quoted("Table 1 identity 1931: 63,247 - 8,604", K.loc[1931, "paid_out"] + K.loc[1931, "business_savings"], 54_643, tol=0)
    quoted("income produced 1929 ($bn)", K.loc[1929, "produced"] / 1000, 83.0, tol=0.05)
    quoted("income produced 1932 ($bn)", K.loc[1932, "produced"] / 1000, 39.4, tol=0.05)
    quoted("income paid out 1929 ($bn)", K.loc[1929, "paid_out"] / 1000, 81.1, tol=0.05)
    quoted("income paid out 1932 ($bn, about)", K.loc[1932, "paid_out"] / 1000, 48.9, tol=0.05)
    quoted("paid out 1932, % of 1929 (Table 1 prints 60.3)", 100 * K.loc[1932, "paid_out"] / K.loc[1929, "paid_out"], 60.3, tol=0.05)
    quoted("  Table 1 line 1, 1932 (% of 1929)", F["k_table1_index_1932"][0], 60.3, tol=0)
    quoted("produced 1932, % of 1929 (Table 1 prints 47.4)", 100 * K.loc[1932, "produced"] / K.loc[1929, "produced"], 47.4, tol=0.05)
    quoted("  decline of income produced, text (%)", F["k_produced_53"][0], 53, tol=0)
    quoted("  decline of income paid out, text (%)", F["k_paid_40"][0], 40, tol=0)
    quoted("King's series starts in", F["k_king_series"][0], 1909, tol=0)
    quoted("King: 1920-21 decline (%)", F["k_king_14"][0], 14.4, tol=0)
    quoted("business savings 1929 ($bn)", F["k_business_savings"][0], 1.9, tol=0)
    quoted("  1932 losses ($bn)", F["k_business_savings"][1], 9.5, tol=0)
    quoted("  Table 1 line 2, 1932 ($bn)", -K.loc[1932, "business_savings"] / 1000, 9.5, tol=0.05)
    quoted("corporation example: net product ($)", F["k_corp_net"][0], 1_000_000, tol=0)
    quoted("  paid out + retained ($)", sum(F["k_corp_split"]), 1_000_000, tol=0)
    quoted("Kuznets's example of abuse: decline (%)", F["k_30pct"][0], 30, tol=0)


def ex_kuznets(F):
    print("-- ex:accounts-kuznets")
    idx = F["k_table1_index_1932"]           # 1932 as % of 1929: paid out, produced, cost of living, wholesale
    quoted("cost of living 1932 (1929 = 100)", idx[2], 80.4, tol=0)
    quoted("  fall of the cost of living (%)", 100 - idx[2], 19.6, tol=1e-9)
    quoted("wholesale prices 1932 (1929 = 100)", idx[3], 68.0, tol=0)
    quoted("real income paid out 1932 (% of 1929)", 100 * idx[0] / idx[2], 75.0, tol=0.05)
    quoted("  real decline (%)", 100 - 100 * idx[0] / idx[2], 25.0, tol=0.05)
    quoted("real income produced 1932, cost of living (% of 1929)", 100 * idx[1] / idx[2], 59.0, tol=0.05)
    # Kuznets (p. 13) deflates income produced by the wholesale index, which falls more than an all-inclusive index
    # would; the two indexes bound the real decline of income produced
    quoted("real income produced 1932, wholesale prices (% of 1929)", 100 * idx[1] / idx[3], 69.7, tol=0.05)
    quoted("  real decline of income produced: low end (%)", 100 - 100 * idx[1] / idx[3], 30, tol=0.5)
    quoted("  real decline of income produced: high end (%)", 100 - 100 * idx[1] / idx[2], 41, tol=0.5)


def cloth():
    print("-- ex:accounts-cloth")
    a = chain_accounts()
    for k in ("production", "expenditure", "income"):
        quoted(f"cotton economy: {k}", a[k], 90, tol=0)
    quoted("  value added: farmer", a["va_farmer"], 30, tol=0)
    quoted("  value added: spinner", a["va_spinner"], 30, tol=0)
    quoted("  value added: weaver", a["va_weaver"], 30, tol=0)
    quoted("  wages", a["wages"], 65, tol=0)
    quoted("  profits", a["profits"], 25, tol=0)
    quoted("  profit: farmer", a["profit_farmer"], 10, tol=0)
    quoted("  profit: spinner", a["profit_spinner"], 10, tol=0)
    quoted("  profit: weaver", a["profit_weaver"], 5, tol=0)
    quoted("  consumption", a["consumption"], 80, tol=0)
    quoted("  investment (yarn put into stock)", a["investment"], 10, tol=0)
    quoted("  sum of all sales (double counting)", a["sum_of_sales"], 160, tol=0)
    quoted("  sum of all output", a["output"], 170, tol=0)
    quoted("  saving = investment", a["saving"], a["investment"], tol=0)


def thrift():
    print("-- ex:accounts-thrift")
    a = chain_accounts(THRIFT_CONSUMPTION)
    quoted("thrift: consumption", a["consumption"], 70, tol=0)
    quoted("thrift: income unchanged", a["income"], 90, tol=0)
    quoted("thrift: saving", a["saving"], 20, tol=0)
    quoted("thrift: investment (yarn 10 + unsold cloth 10)", a["investment"], 20, tol=0)
    quoted("thrift: unplanned part", a["investment"] - chain_accounts()["investment"], 10, tol=0)


def flows():
    print("-- tab:accounts-flows")
    T = flow_table()
    quoted("GDP of the table", gdp_of(), 100, tol=0)
    for k, row in T.items():
        assert sum(row.values()) == 0, f"row {k} must sum to zero"
    NL = net_lending(T)
    quoted("net lending: households", NL["H"], 10, tol=0)
    quoted("net lending: firms", NL["F"], -8, tol=0)
    quoted("  firms' current account = gross saving", NL["Fc"], 12, tol=0)
    quoted("  firms' capital account", NL["Fk"], -20, tol=0)
    quoted("net lending: government", NL["G"], -4, tol=0)
    quoted("net lending: rest of world", NL["R"], 2, tol=0)
    quoted("sum of the columns", NL["H"] + NL["F"] + NL["G"] + NL["R"], 0, tol=0)
    p = FLOW_INPUTS
    quoted("  of which depreciation", p["D"], 10, tol=0)
    quoted("  retained net profit", NL["Fc"] - p["D"], 2, tol=0)
    quoted("gross operating surplus = GDP - W", gdp_of() - p["W"], 42, tol=0)
    quoted("  net operating surplus", gdp_of() - p["W"] - p["D"], 32, tol=0)
    quoted("  = distributed + retained", p["Pi_d"] + NL["Fc"] - p["D"], 32, tol=0)
    quoted("net investment", p["I"] - p["D"], 10, tol=0)
    quoted("(S - I) private", NL["H"] + NL["F"], 2, tol=0)
    quoted("(T - G)", p["T"] - p["G"], -4, tol=0)
    quoted("(M - X)", p["M"] - p["X"], 2, tol=0)
    quoted("household saving", NL["H"], 10, tol=0)
    quoted("private saving", NL["H"] + NL["Fc"], 22, tol=0)


def depression(B):
    print("-- ex:accounts-depression")
    g, r = B.gdp, B.gdp_real_2017
    p = g / r
    quoted("GDP 1929 ($bn)", g[1929] / 1000, 104.6, tol=0.05)
    quoted("GDP 1933 ($bn)", g[1933] / 1000, 57.2, tol=0.05)
    nom, real, defl = g[1933] / g[1929] - 1, r[1933] / r[1929] - 1, p[1933] / p[1929] - 1
    quoted("nominal GDP 1929-33 (%)", 100 * nom, -45.3, tol=0.05)
    quoted("real GDP 1929-33 (%)", 100 * real, -26.3, tol=0.05)
    quoted("deflator 1929-33 (%)", 100 * defl, -25.8, tol=0.05)
    quoted("  (1 - 0.263)(1 - 0.258)", (1 + real) * (1 + defl), 1 + nom, tol=1e-12)
    quoted("  rounded: 0.737 x 0.742", 0.737 * 0.742, 0.547, tol=0.0005)
    quoted("  additive approximation (%)", round(100 * real, 1) + round(100 * defl, 1), -52.1, tol=1e-9)
    quoted("  its error (points)", (round(100 * real, 1) + round(100 * defl, 1)) - 100 * nom, -6.8, tol=0.05)
    quoted("  quantity's share of the nominal fall, in logs (%)", 100 * np.log(1 + real) / np.log(1 + nom), 50.6, tol=0.05)
    quoted("real GDP 1929 (100 million dollars of 2017)", r[1929] / 100, 11911, tol=0.5)
    ri, pi_ = 100 * r / r[1929], 100 * p / p[1929]
    assert ri.loc[1930:1935].max() < 100 <= ri[1936], "real GDP first back at its 1929 level in 1936"
    quoted("real GDP 1936 (1929 = 100)", ri[1936], 100.3, tol=0.05)
    quoted("deflator 1939 (1929 = 100)", pi_[1939], 81.1, tol=0.05)
    quoted("deflator, highest 1934-1940 (1937)", pi_.loc[1934:1940].max(), 84.3, tol=0.05)
    quoted("BEA national income 1929 ($bn)", B.national_income[1929] / 1000, 94.2, tol=0.05)
    quoted("BEA national income 1932 ($bn)", B.national_income[1932] / 1000, 51.3, tol=0.05)
    quoted("BEA national income 1929-32 (%)", 100 * (B.national_income[1932] / B.national_income[1929] - 1), -45.6, tol=0.05)
    quoted("BEA NI 1929 vs Kuznets 83.0 (%)", 100 * (B.national_income[1929] / 83_032 - 1), 13.4, tol=0.05)


def capital(B):
    print("-- 2.3 stocks and flows")
    quoted("1932 gross private investment ($bn)", B.gross_private_investment[1932] / 1000, 1.8, tol=0.05)
    quoted("1932 depreciation ($bn)", B.private_cfc[1932] / 1000, 7.5, tol=0.05)
    quoted("1932 net private investment ($bn)", B.net_private_investment[1932] / 1000, -5.6, tol=0.05)
    assert all(B.gross_private_investment - B.private_cfc - B.net_private_investment <= 1)
    neg = [y for y in range(1929, 1942) if B.net_private_investment[y] < 0]
    assert neg == [1931, 1932, 1933, 1934, 1938], neg
    quoted("negative net investment: 1931-1934 and 1938 (count)", len(neg), 5, tol=0)
    quoted("1929 net private investment ($bn)", B.net_private_investment[1929] / 1000, 7.8, tol=0.05)
    quoted("sum of net private investment 1931-1934 ($bn)", B.net_private_investment.loc[1931:1934].sum() / 1000, -15.4, tol=0.05)


def discrepancy(B):
    print("-- GDP and GDI")
    assert all((B.gdp - B.gdi - B.stat_discrepancy).abs() <= 1)
    sd = 100 * B.stat_discrepancy / B.gdp
    x = sd.loc[1960:]
    quoted("statistical discrepancy, minimum since 1960 (% of GDP)", x.min(), -1.5, tol=0.05)
    assert x.idxmin() == 2006
    quoted("statistical discrepancy, maximum since 1960 (% of GDP)", x.max(), 2.3, tol=0.05)
    assert x.idxmax() == 1993
    quoted("  mean absolute size since 1960 (% of GDP)", x.abs().mean(), 0.7, tol=0.05)
    quoted("GDP 2025 ($tn)", B.gdp[2025] / 1e6, 30.86, tol=0.005)
    quoted("GDI 2025 ($tn)", B.gdi[2025] / 1e6, 30.91, tol=0.005)
    quoted("discrepancy 2025 ($bn)", B.stat_discrepancy[2025] / 1000, -46.4, tol=0.05)


def balances(B):
    print("-- ex:accounts-us, fig:accounts_balances")
    S = sector_balances(B)
    assert (S.sum(axis=1).abs() < 0.001).all()
    for y, vals in {2000: (-4.2, 0.3, 3.9), 2009: (10.5, -13.2, 2.7), 2020: (12.3, -15.0, 2.7), 2025: (3.5, -7.3, 3.8)}.items():
        for col, v in zip(S.columns, vals):
            quoted(f"{y} {col} (% of GDP)", S.loc[y, col], v, tol=0.05)
    quoted("private surplus, largest since 1960 (2020)", S.private.max(), 12.3, tol=0.05)
    assert [y for y in S.index if S.government[y] > 0] == [2000], "government a net lender only in 2000"
    assert [y for y in S.index if S.private[y] < -0.05] == [1998, 1999, 2000, 2001, 2005, 2006, 2007]
    quoted("private 2022, about zero (% of GDP)", S.private[2022], 0.0, tol=0.05)
    assert (S.rest_of_world.loc[1992:] > 0).all() and S.rest_of_world[1991] < 0, "RoW a net lender every year from 1992"
    quoted("rest of the world, largest (2006)", S.rest_of_world.max(), 6.0, tol=0.05)
    assert S.rest_of_world.idxmax() == 2006
    assert S.private.idxmax() == 2020 and S.government.idxmin() == 2020 and S.government.idxmax() == 2000
    quoted("gross saving + discrepancy = investment + capital transfers + net lending (2025, $m)",
           B.gross_saving[2025] + B.stat_discrepancy[2025] - B.gross_domestic_investment[2025]
           - B.capital_account_net[2025] - B.net_lending_nation[2025], 0, tol=2)


def gni(B, F):
    print("-- 2.5 GDP and GNI")
    # BEA's GNP starts from GDP, its GNI from GDI: the two differ by the statistical discrepancy (BEA rounds each
    # series separately; the largest residual, 18 million dollars in 2015, is under 0.0001% of GDP)
    assert all((B.gnp - B.gni - B.stat_discrepancy).abs() <= 20), "GNP - GNI = statistical discrepancy"
    quoted("US 2024: GNP - GDP (% of GDP)", 100 * (B.gnp[2024] - B.gdp[2024]) / B.gdp[2024], -0.12, tol=0.005)
    quoted("US 2024: GNI - GDP (% of GDP)", 100 * (B.gni[2024] - B.gdp[2024]) / B.gdp[2024], -0.41, tol=0.005)
    gdp, gni_, star = F["ie_gdp"], F["ie_gni"], F["ie_gnistar_values"]
    quoted("Ireland: GDP 2014 -> 2015, current prices (%)", 100 * (gdp[1] / gdp[0] - 1), 34.7, tol=0.05)
    quoted("Ireland: GNI* 2014 (100 million euro)", 10 * star[0], 1545, tol=0)
    quoted("Ireland: GNI* 2014 -> 2015 (%)", 100 * (star[1] / star[0] - 1), 11.9, tol=0.05)
    quoted("Ireland 2015: GNI / GDP (%)", 100 * gni_[1] / gdp[1], 79.1, tol=0.05)
    quoted("Ireland 2015: GNI* / GDP (%)", 100 * star[1] / gdp[1], 66.0, tol=0.05)
    quoted("Ireland 2015: net factor income paid abroad ($bn eur)", gdp[1] - gni_[1], 54.8, tol=0.05)
    nfi, red, ip, air = F["ie_nfi"], F["ie_redomiciled"], F["ie_ip_dep"], F["ie_aircraft"]
    for k, y in enumerate((2014, 2015, 2016)):     # CSO Table 1 adds up (to the rounding of its one decimal)
        quoted(f"Ireland {y}: GDP + NFI = GNI", gdp[k] + nfi[k], gni_[k], tol=0.15)
        quoted(f"Ireland {y}: GNI less the three items = GNI*", gni_[k] + red[k] + ip[k] + air[k], star[k], tol=0.15)
    quoted("Ireland 2015: GNI - GNI* (bn eur)", gni_[1] - star[1], 34.3, tol=0.05)
    quoted("  of which depreciation of IP (bn eur)", -ip[1], 25.0, tol=0)
    quoted("  IP depreciation 2014 (bn eur)", -ip[0], 0.8, tol=0)
    quoted("  re-domiciled companies 2015 (bn eur)", -red[1], 4.7, tol=0)
    quoted("  aircraft 2015 (bn eur)", -air[1], 4.6, tol=0)
    quoted("CSO's level shift 2015 (%)", F["ie_shift"][0], 26, tol=0)
    quoted("GNI* growth as a fraction of GDP growth 2015", (star[1] / star[0] - 1) / (gdp[1] / gdp[0] - 1), 0.34, tol=0.005)
    quoted("relocated capital (bn eur)", F["ie_300"][0], 300, tol=0)


def ex_ireland(F):
    print("-- ex:accounts-ireland")
    debt, gdp, star = F["ie_debt"], F["ie_gdp"], F["ie_gnistar_values"]
    quoted("debt 2014 (bn eur)", debt[0], 203.3, tol=0)
    quoted("debt 2015 (bn eur)", debt[1], 201.4, tol=0)
    quoted("debt change 2014-2015 (%)", 100 * (debt[1] / debt[0] - 1), -0.9, tol=0.05)
    quoted("debt / GDP 2014 (%)", 100 * debt[0] / gdp[0], 104.5, tol=0.05)
    quoted("debt / GDP 2015 (%)", 100 * debt[1] / gdp[1], 76.9, tol=0.05)
    quoted("debt / GNI* 2014 (%)", 100 * debt[0] / star[0], 131.6, tol=0.05)
    quoted("debt / GNI* 2015 (%)", 100 * debt[1] / star[1], 116.5, tol=0.05)
    quoted("  CSO table: debt / GDP 2015", F["ie_debt_gdp"][1], 76.9, tol=0)
    quoted("  CSO table: debt / GNI* 2015", F["ie_debt_gnistar"][1], 116.5, tol=0)
    quoted("fall of the ratio to GDP (points)", F["ie_debt_gdp"][0] - F["ie_debt_gdp"][1], 27.6, tol=0.05)
    quoted("fall of the ratio to GNI* (points)", F["ie_debt_gnistar"][0] - F["ie_debt_gnistar"][1], 15.1, tol=0.05)


def china(F):
    print("-- case: China, fig:accounts_china")
    D = china_revision(F)
    assert all(D.gdp_new - D.gdp_old == D.d_gdp)
    quoted("2004 GDP after the census (100m yuan)", D.gdp_new[2004], 159_878, tol=0)
    quoted("2004 GDP before (100m yuan)", D.gdp_old[2004], 136_876, tol=0)
    quoted("2004 revision (100m yuan)", D.d_gdp[2004], 23_002, tol=0)
    quoted("2004 revision (%)", D.rev_pct[2004], 16.8, tol=0.05)
    quoted("  NBS text", F["census_2004"][2], 16.8, tol=0)
    quoted("2004 GDP after, trillion yuan", D.gdp_new[2004] / 1e4, 16.0, tol=0.05)
    quoted("2004 tertiary revision (100m yuan)", D.d_p3[2004], 21_297, tol=0)
    quoted("2004 tertiary share of the revision (%)", D.tertiary_share[2004], 92.6, tol=0.05)
    quoted("  NBS text (93%)", F["census_93"][1], 93, tol=0)
    assert (D.tertiary_share > 90).all(), D.tertiary_share      # NBS: 各年……都占当年 GDP 修订量的 90% 以上
    quoted("tertiary share of the revision, minimum over 1993-2004 (%)", D.tertiary_share.min(), 91.7, tol=0.05)
    quoted("tertiary share of the revision, maximum over 1993-2004 (%)", D.tertiary_share.max(), 95.4, tol=0.05)
    quoted("tertiary value added 2004 before (trillion yuan)", D.p3_old[2004] / 1e4, 4.37, tol=0.005)
    quoted("tertiary value added 2004 after (trillion yuan)", D.p3_new[2004] / 1e4, 6.50, tol=0.005)
    quoted("1993 revision (%)", D.rev_pct[1993], 2.0, tol=0.05)
    assert D.rev_pct.is_monotonic_increasing
    quoted("tertiary value added 2004: increase (%)", F["census_tertiary"][1], 48.7, tol=0)
    quoted("  computed", 100 * D.d_p3[2004] / D.p3_old[2004], 48.7, tol=0.05)
    quoted("tertiary share of GDP, before (%)", F["census_share"][0], 31.9, tol=0)
    quoted("tertiary share of GDP, after (%)", F["census_share"][1], 40.7, tol=0)
    quoted("  computed before", 100 * D.p3_old[2004] / D.gdp_old[2004], 31.9, tol=0.05)
    quoted("  computed after", 100 * D.p3_new[2004] / D.gdp_new[2004], 40.7, tol=0.05)
    quoted("construction revised (100m yuan)", F["census_construction"][4], -878, tol=0)
    quoted("finance and insurance revised (100m yuan)", F["census_finance"][4], -1633, tol=0)
    quoted("growth revisions within (points)", F["census_growth"][0], 0.8, tol=0)
    quoted("average growth 1979-2004 after (%)", F["census_avg"][0], 9.6, tol=0)
    quoted("  before (%)", F["census_avg"][1], 9.4, tol=0)
    quoted("primary revision 2004 (100m yuan)", D.d_p1[2004], 188, tol=0)
    usd = F["census_rank"]                          # IMF figure for 2004 and after the revision (100m dollars), rank
    quoted("2004 GDP in dollars, revised / IMF (%)", 100 * (usd[1] / usd[0] - 1), 16.8, tol=0.05)
    quoted("  rank before / after", usd[2] - usd[3], 1, tol=0)
    quoted("MPS national income first tried", F["mps_1953"][0], 1953, tol=0)
    quoted("trial SNA scheme", F["mps_1992"][0], 1992, tol=0)
    quoted("MPS national income dropped", F["mps_1993"][0], 1993, tol=0)
    quoted("  2002 system", F["mps_2002"][0], 2002, tol=0)


def household(F):
    print("-- 2.6 what GDP leaves out")
    t = F["hh_table1"]          # NIPA 1965, 2017, growth; satellite 1965, 2017, growth ($bn, %)
    quoted("household production adds, 1965 (%)", 100 * (t[3] / t[0] - 1), 37.4, tol=0.05)
    quoted("household production adds, 2017 (%)", 100 * (t[4] / t[1] - 1), 23.2, tol=0.05)
    quoted("  Table 2 (rounded)", F["hh_table2"][0], 37, tol=0)
    quoted("  Table 2 (rounded)", F["hh_table2"][1], 23, tol=0)
    quoted("nonmarket services alone, 1965 (% of NIPA GDP)", F["hh_nonmarket"][0], 30, tol=0)
    quoted("nonmarket services alone, 2017 (% of NIPA GDP)", F["hh_nonmarket"][1], 17, tol=0)
    quoted("NIPA GDP growth 1965-2017 (%)", F["hh_growth"][0], 6.5, tol=0)
    quoted("  with household production (%)", F["hh_growth"][1], 6.3, tol=0)
    quoted("  check: NIPA from the levels (%)", 100 * avg_rate(t[0], t[1], 52), 6.5, tol=0.05)
    quoted("  check: satellite from the levels (%)", 100 * avg_rate(t[3], t[4], 52), 6.3, tol=0.05)
    quoted("NIPA GDP 2017 / 1965 (times)", t[1] / t[0], 26.3, tol=0.05)
    quoted("with household production 2017 / 1965 (times)", t[4] / t[3], 23.5, tol=0.05)
    quoted("NIPA GDP 2017 ($bn)", t[1], 19_485.4, tol=0)
    quoted("satellite GDP 2017 ($bn)", t[4], 24_001.5, tol=0)


def legacy(F):
    print("-- legacy")
    quoted("first SNA", F["sna_versions"][0], 1953, tol=0)
    quoted("2025 SNA adopted at the Statistical Commission's session", F["sna2025_adopted"][0], 56, tol=0)


def selfcheck(F, B):
    print("-- self-check answers")
    # 1: the weaver sells 40 to households and 40 to a retailer, who sells it on for 55
    a = chain_accounts()
    va_retail = 55 - 40
    quoted("Q1: retailer's value added", va_retail, 15, tol=0)
    quoted("Q1: GDP, production", a["va_farmer"] + a["va_spinner"] + a["va_weaver"] + va_retail, 105, tol=0)
    quoted("Q1: consumption", 40 + 55, 95, tol=0)
    quoted("Q1: GDP, expenditure", 40 + 55 + a["investment"], 105, tol=0)
    # 2: nominal +5%, deflator +3% -> real growth
    quoted("Q2: real growth (%)", 100 * (1.05 / 1.03 - 1), 1.94, tol=0.005)
    quoted("Q2: error of the approximation (points)", 2 - 100 * (1.05 / 1.03 - 1), 0.06, tol=0.005)
    # 4: in the flow table, government buys 4 more, taxes unchanged, X and M unchanged -> private balance
    p = dict(FLOW_INPUTS, G=FLOW_INPUTS["G"] + 4)
    NL = net_lending(flow_table(p))
    quoted("Q4: GDP after +4", gdp_of(p), 104, tol=0)
    quoted("Q4: government balance after +4", NL["G"], -8, tol=0)
    quoted("Q4: firms' gross saving after +4", NL["Fc"], 16, tol=0)
    quoted("Q4: firms' net lending after +4", NL["F"], -4, tol=0)
    quoted("Q4: private balance after +4 (if X, M unchanged)", NL["H"] + NL["F"], 6, tol=0)
    # 5: US 2025, the government deficit 2 points smaller, the rest of the world unchanged
    S = sector_balances(B).round(1)
    quoted("Q5: private balance (% of GDP)", -((S.government[2025] + 2) + S.rest_of_world[2025]), 1.5, tol=1e-9)
    # 6: Ireland 2015, GNI - GNI* and the share of IP depreciation
    gap = F["ie_gni"][1] - F["ie_gnistar_values"][1]
    quoted("Q6: GNI - GNI* (bn eur)", gap, 34.3, tol=0.05)
    quoted("Q6: IP depreciation's share of the gap (%)", 100 * -F["ie_ip_dep"][1] / gap, 73, tol=0.5)


def main():
    F, B = facts(), bea()
    world(F)
    ex_kuznets(F)
    cloth()
    thrift()
    flows()
    depression(B)
    capital(B)
    discrepancy(B)
    balances(B)
    gni(B, F)
    ex_ireland(F)
    china(F)
    household(F)
    legacy(F)
    selfcheck(F, B)
    print("check_ch02: all numbers agree")


if __name__ == "__main__":
    main()
