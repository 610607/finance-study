"""Chapter 3 (价格、通胀与利率): every number quoted in zh/ch03_prices.tex.

    python3 checks/check_ch03.py

Inputs are six snapshots:
  prices_facts           quotations from Fisher (1896), the Boskin Commission (1996), McCully, Moyer & Stewart
                         (2007, BEA), the UK DMO, 31 CFR 356 App. B, Public Law 115-97, the FOMC and the Bank of
                         Japan; checked by data/fetch/verify_web_quotes.py, twelve rows read on page images
  fred_prices_monthly    CPI-U (SA and NSA), chained CPI-U, PCE price index, average hourly earnings (FRED)
  fred_prices_quarterly  GDP implicit price deflator (FRED)
  fred_yields_daily      10-year and 2-year Treasury yields and the 10-year TIPS yield (FRED)
  mof_jgb_curves         Japanese government bond yields by maturity (Ministry of Finance, Japan)
  treasury_tips_first    the first six TIPS auctions (Treasury, Fiscal Data)
The figure module figsrc/fig_ch03.py imports the functions defined here.

Formulas (the chapter's key equations):
    index numbers        P^L = sum p_t q_0 / sum p_0 q_0, P^P = sum p_t q_t / sum p_0 q_t, P^F = sqrt(P^L P^P)  (eq:prices-index)
    Fisher relation      1 + i = (1 + r)(1 + E pi); ex post 1 + r = (1 + i)/(1 + pi)                        (eq:prices-fisher)
    bond                 P = sum C/(1+i)^t + F/(1+i)^T; D = sum t CF_t/(1+i)^t / P; dP/P = -D/(1+i) di     (eq:prices-bond)
    yield curve          i^(n) = mean of expected short rates + term premium                              (eq:prices-curve)
    breakeven            i^(n) - r^(n) = expected inflation + inflation risk premium - liquidity premium   (eq:prices-breakeven)
The bread-and-computer economy (ex:prices-chain), the bond (ex:prices-bond), the loan (ex:prices-fisher) and the
zero-coupon approximation in the compare box are teaching inputs, defined below and stated in the text.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from common import load_snapshot, quoted

# ---------------------------------------------------------------------------------------------------
# Teaching inputs stated in the text
# ex:prices-chain: an economy that makes bread and computers (prices in yuan, quantities in units)
CHAIN_P = {1: dict(bread=2.0, computer=1000.0), 2: dict(bread=2.1, computer=800.0)}
CHAIN_Q = {1: dict(bread=500, computer=1.0), 2: dict(bread=510, computer=1.5)}
# ex:prices-fisher, part 3: a one-year loan written in yuan
LOAN = dict(principal=100_000, i=0.06, pi_expected=0.02, pi_actual=0.08)
# ex:prices-bond: a 10-year bond with an annual coupon of 3 per 100 of face value
BOND = dict(coupon=3.0, face=100.0, years=10, i0=0.03)
# fig:prices_bond (b): maturities shown
MATURITIES = np.arange(1, 31)
# compare box (YTM vs holding-period return), Japan 2016: a 10-year zero-coupon bond priced at the
# 10-year constant-maturity yields of 2016-01-28 and 2016-07-27 (an approximation stated in the text)
JGB_HPR_DATES = ("2016-01-28", "2016-07-27")
# case box and fig:prices_jgb: the dates shown
JGB_DATES = ["2016-01-28", "2016-07-27", "2019-08-28", "2024-03-18", "2026-09-30"]
# the breakeven test: monthly means of DGS10 - DFII10 against CPI-U (NSA) inflation over the next ten years
TEST_FROM, TEST_TO = "2003-01", "2016-08"


# ---------------------------------------------------------------------------------------------------
# Data
def facts() -> dict[str, list[float]]:
    """id -> the numbers of the value column (several are separated by ';')."""
    df, _ = load_snapshot("prices_facts", dtype={"value": str})
    out = {}
    for _, r in df.iterrows():
        v = r["value"]
        if isinstance(v, str) and v.strip():
            out[r["id"]] = [float(x) for x in v.split(";")]
    return out


def monthly() -> pd.DataFrame:
    df, _ = load_snapshot("fred_prices_monthly", parse_dates=["date"])
    return df.set_index("date")


def quarterly() -> pd.DataFrame:
    df, _ = load_snapshot("fred_prices_quarterly", parse_dates=["date"])
    return df.set_index("date")


def daily() -> pd.DataFrame:
    df, _ = load_snapshot("fred_yields_daily", parse_dates=["date"])
    df = df.set_index("date")
    df["BE"] = df["DGS10"] - df["DFII10"]          # 10-year breakeven inflation (FRED's T10YIE)
    return df


def jgb() -> pd.DataFrame:
    df, _ = load_snapshot("mof_jgb_curves", parse_dates=["date"])
    return df.set_index("date")


def tips() -> pd.DataFrame:
    df, _ = load_snapshot("treasury_tips_first", parse_dates=["auction_date", "issue_date", "maturity_date"])
    return df


def annual(df: pd.DataFrame) -> pd.DataFrame:
    """Calendar-year means; a year counts only if every observation of it is present."""
    g = df.groupby(df.index.year)
    return g.mean().where(g.count() == g.size().max())


# ---------------------------------------------------------------------------------------------------
# Index numbers (eq:prices-index)
def laspeyres(p0, p1, q0) -> float:
    return sum(p1[k] * q0[k] for k in p0) / sum(p0[k] * q0[k] for k in p0)


def paasche(p0, p1, q1) -> float:
    return sum(p1[k] * q1[k] for k in p0) / sum(p0[k] * q1[k] for k in p0)


def fisher_index(p0, p1, q0, q1) -> float:
    return math.sqrt(laspeyres(p0, p1, q0) * paasche(p0, p1, q1))


def shares(p, q) -> dict:
    total = sum(p[k] * q[k] for k in p)
    return {k: p[k] * q[k] / total for k in p}


def tornqvist(p0, p1, s0, s1) -> float:
    return math.exp(sum((s0[k] + s1[k]) / 2 * math.log(p1[k] / p0[k]) for k in p0))


def quantity_indices(p, q):
    """Laspeyres, Paasche and Fisher quantity indices of year 2 on year 1 (prices and quantities swap roles)."""
    return laspeyres(q[1], q[2], p[1]), paasche(q[1], q[2], p[2]), fisher_index(q[1], q[2], p[1], p[2])


# ---------------------------------------------------------------------------------------------------
# Fisher relation (eq:prices-fisher)
def real_rate(i: float, pi: float) -> float:
    return (1 + i) / (1 + pi) - 1


# ---------------------------------------------------------------------------------------------------
# Bonds (eq:prices-bond)
def bond_price(i: float, coupon: float = BOND["coupon"], years: int = BOND["years"], face: float = BOND["face"]) -> float:
    t = np.arange(1, years + 1)
    cf = np.full(years, coupon, dtype=float)
    cf[-1] += face
    return float((cf / (1 + i) ** t).sum())


def macaulay(i: float, coupon: float = BOND["coupon"], years: int = BOND["years"], face: float = BOND["face"]) -> float:
    t = np.arange(1, years + 1)
    cf = np.full(years, coupon, dtype=float)
    cf[-1] += face
    pv = cf / (1 + i) ** t
    return float((t * pv).sum() / pv.sum())


def modified(i: float, **kw) -> float:
    return macaulay(i, **kw) / (1 + i)


def price_changes_by_maturity(di: float = 0.01) -> pd.DataFrame:
    """Percent price change of a 3% annual-coupon bond priced at par when yields move by +/- di."""
    i0, c = BOND["i0"], BOND["coupon"]
    rows = []
    for n in MATURITIES:
        p0 = bond_price(i0, c, int(n))
        rows.append(dict(n=int(n), up=100 * (bond_price(i0 + di, c, int(n)) / p0 - 1),
                         down=100 * (bond_price(i0 - di, c, int(n)) / p0 - 1),
                         approx=100 * modified(i0, coupon=c, years=int(n)) * di))
    return pd.DataFrame(rows).set_index("n")


def forward(i_short: float, n_short: float, i_long: float, n_long: float) -> float:
    """Annual forward rate between n_short and n_long years implied by two yields (percent)."""
    g = (1 + i_long / 100) ** n_long / (1 + i_short / 100) ** n_short
    return 100 * (g ** (1 / (n_long - n_short)) - 1)


# ---------------------------------------------------------------------------------------------------
# TIPS: the reference CPI (31 CFR 356 App. B): the CPI-U (NSA) of the third preceding month on the first
# day of a month, linear interpolation in between
def ref_cpi(day: pd.Timestamp, cpi_nsa: pd.Series) -> float:
    first = day.to_period("M").to_timestamp()
    m0 = first - pd.DateOffset(months=3)
    m1 = first - pd.DateOffset(months=2)
    days = first.days_in_month
    v = cpi_nsa[m0] + (day.day - 1) / days * (cpi_nsa[m1] - cpi_nsa[m0])
    return round(math.trunc(v * 1e6) / 1e6, 5)                 # truncate to six decimals, round to five


# ---------------------------------------------------------------------------------------------------
# The breakeven test
def breakeven_monthly(D: pd.DataFrame) -> pd.DataFrame:
    """Monthly means of the daily yields; a month counts only if the data reach its last business day."""
    d = D[["DGS10", "DFII10", "BE"]].dropna()
    m = d.resample("MS").mean()
    if d.index[-1] < d.index[-1] + pd.offsets.BMonthEnd(0):
        m = m.iloc[:-1]
    return m


def forecast_test(D: pd.DataFrame, M: pd.DataFrame) -> pd.DataFrame:
    """Breakeven in month t against CPI-U (NSA) inflation from month t to month t + 120, % a year."""
    be = breakeven_monthly(D)["BE"]
    cpi = M["CPIAUCNS"].dropna()
    rows = []
    for t, v in be.items():
        t2 = t + pd.DateOffset(years=10)
        if t in cpi.index and t2 in cpi.index:
            rows.append((t, v, 100 * ((cpi[t2] / cpi[t]) ** 0.1 - 1)))
    return pd.DataFrame(rows, columns=["date", "be", "realized"]).set_index("date")


def inversions(D: pd.DataFrame, min_days: int = 300) -> list[tuple]:
    """Runs of business days with the 10-year yield below the 2-year yield, longer than min_days."""
    sp = (D["DGS10"] - D["DGS2"]).dropna()
    runs, start, prev = [], None, None
    for t, v in sp.items():
        if v < 0 and start is None:
            start = t
        if v >= 0 and start is not None:
            runs.append((start, prev))
            start = None
        prev = t
    if start is not None:
        runs.append((start, prev))
    return [(a, b, sp[a:b].min(), sp[a:b].idxmin()) for a, b in runs if (b - a).days >= min_days]


# ---------------------------------------------------------------------------------------------------
# Real wages and price indices
def wages_and_prices(M: pd.DataFrame, Q: pd.DataFrame) -> pd.DataFrame:
    a = annual(M[["CPIAUCSL", "PCEPI", "AHETPI"]])
    a["GDPDEF"] = annual(Q[["GDPDEF"]])["GDPDEF"]
    a["real_cpi"] = a["AHETPI"] / a["CPIAUCSL"]
    a["real_pce"] = a["AHETPI"] / a["PCEPI"]
    return a


# ---------------------------------------------------------------------------------------------------
# Checks, in the order of the text
def world(F):
    print("== 3.1 the world of 1896 and 1996")
    quoted("Fisher: yard delivered ten years hence", F["f_yard_terms"][0], 10, tol=0)
    quoted("ERTA indexed tax brackets in", F["b_erta"][0], 1981, tol=0)
    quoted("report submitted (year)", F["b_letter"][0], 1996, tol=0)
    quoted("commission chartered by Senate Resolution", F["b_charter_img"][0], 73, tol=0)
    quoted("Boskin: bias looking forward (pp a year)", F["b_bias"][0], 1.1, tol=0)
    quoted("  range low", F["b_bias"][1], 0.8, tol=0)
    quoted("  range high", F["b_bias"][2], 1.6, tol=0)
    quoted("  before 1996 (pp a year)", F["b_past_img"][0], 1.3, tol=0)
    quoted("  formula bias (pp)", F["b_past_img"][1], 0.2, tol=0)
    quoted("  formula bias introduced in", F["b_past_img"][2], 1978, tol=0)
    quoted("CBO: bias assumed (pp a year)", F["b_cbo_img"][0], 1.1, tol=0)
    quoted("  deficit in 2006 ($bn)", F["b_cbo_img"][1], 148, tol=0)
    quoted("  national debt by 2006 ($bn)", F["b_cbo_img"][2], 691, tol=0)


def ex_beef(F):
    print("== ex:prices-beef")
    t1 = F["b_table1_img"]
    p0, q0 = dict(beef=t1[0], chicken=t1[2]), dict(beef=t1[1], chicken=t1[3])
    p1, q1 = dict(beef=t1[4], chicken=t1[6]), dict(beef=t1[5], chicken=t1[7])
    quoted("beef price, period 2", p1["beef"], 1.6, tol=0)
    quoted("chicken price, period 2", p1["chicken"], 0.8, tol=0)
    quoted("beef quantity, period 2", q1["beef"], 0.8, tol=0)
    quoted("chicken quantity, period 2", q1["chicken"], 2.0, tol=0)
    quoted("spending, period 1 ($)", sum(p0[k] * q0[k] for k in p0), 2.00, tol=1e-12)
    quoted("old basket at period-2 prices ($)", sum(p1[k] * q0[k] for k in p0), 2.40, tol=1e-12)
    quoted("spending, period 2 ($)", sum(p1[k] * q1[k] for k in p0), 2.88, tol=1e-12)
    quoted("  beef ($)", p1["beef"] * q1["beef"], 1.28, tol=1e-12)
    quoted("  chicken ($)", p1["chicken"] * q1["chicken"], 1.60, tol=1e-12)
    quoted("new basket at period-1 prices ($)", sum(p0[k] * q1[k] for k in p0), 2.80, tol=1e-12)
    L, P, Fi = laspeyres(p0, p1, q0), paasche(p0, p1, q1), fisher_index(p0, p1, q0, q1)
    quoted("Laspeyres", L, 1.20, tol=1e-12)
    quoted("  Boskin's Laspeyres", F["b_laspeyres"][0], 1.20, tol=0)
    quoted("Paasche", P, 1.029, tol=0.0005)
    quoted("  Boskin's Paasche (rounded)", F["b_paasche"][0], 1.03, tol=0)
    quoted("Fisher", Fi, 1.111, tol=0.0005)
    quoted("  Boskin's Fisher", F["b_fisher"][0], 1.11, tol=0)
    quoted("Laspeyres - Fisher (pp)", 100 * (L - F["b_fisher"][0]), 9, tol=1e-9)
    quoted("Paasche - Fisher (pp, Boskin's rounding)", 100 * (F["b_paasche"][0] - F["b_fisher"][0]), -8, tol=1e-9)
    s0, s1 = shares(p0, q0), shares(p1, q1)
    quoted("period-2 share: beef", s1["beef"], 0.444, tol=0.0005)
    quoted("period-2 share: chicken", s1["chicken"], 0.556, tol=0.0005)
    quoted("Table 1 prints: beef", t1[8], 0.43, tol=0)
    quoted("Table 1 prints: chicken", t1[9], 0.57, tol=0)
    quoted("mean share: beef", (s0["beef"] + s1["beef"]) / 2, 0.472, tol=0.0005)
    quoted("mean share: chicken", (s0["chicken"] + s1["chicken"]) / 2, 0.528, tol=0.0005)
    T = tornqvist(p0, p1, s0, s1)
    quoted("ln Tornqvist (exact shares)", math.log(T), 0.104, tol=0.0005)
    quoted("Tornqvist (exact shares)", T, 1.110, tol=0.0005)
    T_tab = tornqvist(p0, p1, s0, dict(beef=t1[8], chicken=t1[9]))
    quoted("Tornqvist (Table 1 shares), Boskin prints 1.10", T_tab, F["b_tornqvist"][0], tol=0.005)
    quoted("beef twice as dear as chicken in period 2", p1["beef"] / p1["chicken"], 2, tol=1e-12)
    quoted("deeper box: upper bound 1.20 - lower bound 1.03 (pp)", 100 * (F["b_laspeyres"][0] - F["b_paasche"][0]), 17, tol=1e-9)


def boskin_bias(F, M):
    print("== 3.2 the size of the bias")
    t3 = F["b_table3_img"]
    quoted("upper level substitution", t3[0], 0.15, tol=0)
    quoted("lower level substitution", t3[1], 0.25, tol=0)
    quoted("new products / quality", t3[2], 0.60, tol=0)
    quoted("new outlets", t3[3], 0.10, tol=0)
    quoted("total (sum of the four)", sum(t3[:4]), t3[4], tol=1e-12)
    quoted("  total", t3[4], 1.10, tol=0)
    quoted("item groups", F["b_upper_level"][0], 207, tol=0)
    quoted("areas", F["b_upper_level"][1], 44, tol=0)
    quoted("1.1 pp for 12 years: cumulative (%)", 100 * (1.011 ** 12 - 1), 14.0, tol=0.05)
    quoted("  Boskin's 14%", F["b_14pct"][1], 14, tol=0)
    # chained CPI-U against CPI-U, both not seasonally adjusted, December 1999 to December 2024 (final values)
    a, b = pd.Timestamp("1999-12-01"), pd.Timestamp("2024-12-01")
    c0, c1 = M.loc[a, "CPIAUCNS"], M.loc[b, "CPIAUCNS"]
    s0, s1 = M.loc[a, "SUUR0000SA0"], M.loc[b, "SUUR0000SA0"]
    quoted("chained CPI-U, December 1999", s0, 100.0, tol=0)
    gc, gs = 100 * ((c1 / c0) ** (1 / 25) - 1), 100 * ((s1 / s0) ** (1 / 25) - 1)
    quoted("CPI-U Dec 1999 - Dec 2024 (%)", 100 * (c1 / c0 - 1), 87.5, tol=0.05)
    quoted("chained CPI-U Dec 1999 - Dec 2024 (%)", 100 * (s1 / s0 - 1), 75.2, tol=0.05)
    quoted("CPI-U (% a year)", gc, 2.55, tol=0.005)
    quoted("chained CPI-U (% a year)", gs, 2.27, tol=0.005)
    quoted("difference (pp a year)", gc - gs, 0.28, tol=0.005)
    quoted("  Boskin's upper-level substitution bias", t3[0], 0.15, tol=0)
    quoted("indexed benefit of 1,000 in Dec 1999, by CPI-U", 1000 * c1 / c0, 1875, tol=0.5)
    quoted("  by chained CPI-U", 1000 * s1 / s0, 1752, tol=0.5)
    quoted("  difference (%)", 100 * ((c1 / c0) / (s1 / s0) - 1), 7.0, tol=0.05)
    quoted("TCJA: taxable years beginning after December 31 of", F["tcja_effective"][0], 2017, tol=0)


def ex_chain():
    print("== ex:prices-chain")
    p, q = CHAIN_P, CHAIN_Q
    v = lambda pp, qq: sum(pp[k] * qq[k] for k in pp)
    quoted("nominal GDP, year 1", v(p[1], q[1]), 2000, tol=1e-9)
    quoted("nominal GDP, year 2", v(p[2], q[2]), 2271, tol=1e-9)
    quoted("  bread, year 2", p[2]["bread"] * q[2]["bread"], 1071, tol=1e-9)
    quoted("  computers, year 2", p[2]["computer"] * q[2]["computer"], 1200, tol=1e-9)
    quoted("nominal growth (%)", 100 * (v(p[2], q[2]) / v(p[1], q[1]) - 1), 13.55, tol=0.005)
    quoted("year-2 output at year-1 prices", v(p[1], q[2]), 2520, tol=1e-9)
    quoted("year-1 output at year-2 prices", v(p[2], q[1]), 1850, tol=1e-9)
    QL, QP, QF = quantity_indices(p, q)
    quoted("real growth at year-1 prices (%)", 100 * (QL - 1), 26.0, tol=0.05)
    quoted("real growth at year-2 prices (%)", 100 * (QP - 1), 22.8, tol=0.05)
    quoted("  gap (pp)", 100 * (QL - QP), 3, tol=0.5)
    quoted("Laspeyres quantity index", QL, 1.260, tol=0.0005)
    quoted("Paasche quantity index", QP, 1.228, tol=0.0005)
    quoted("Fisher quantity index", QF, 1.244, tol=0.0005)
    quoted("Fisher real growth (%)", 100 * (QF - 1), 24.4, tol=0.05)
    PL, PP = laspeyres(p[1], p[2], q[1]), paasche(p[1], p[2], q[2])
    PF = math.sqrt(PL * PP)
    quoted("Laspeyres price index", PL, 0.925, tol=0.0005)
    quoted("Paasche price index", PP, 0.901, tol=0.0005)
    quoted("Fisher price index", PF, 0.913, tol=0.0005)
    quoted("price change (%)", 100 * (PF - 1), -8.7, tol=0.05)
    quoted("Fisher price x quantity = nominal ratio", PF * QF, v(p[2], q[2]) / v(p[1], q[1]), tol=1e-12)
    quoted("  = 1.1355", PF * QF, 1.1355, tol=1e-12)
    quoted("real GDP, year 2, chained year-1 yuan", v(p[1], q[1]) * QF, 2487, tol=0.5)
    quoted("  bread at year-1 prices", p[1]["bread"] * q[2]["bread"], 1020, tol=1e-9)
    quoted("  computers at year-1 prices", p[1]["computer"] * q[2]["computer"], 1500, tol=1e-9)
    quoted("  sum of components - chained total", v(p[1], q[2]) - v(p[1], q[1]) * QF, 33, tol=0.5)


def real_side(F, M, Q):
    print("== 3.3 three price indices and real wages")
    W = wages_and_prices(M, Q)
    quoted("BEA: CPI faster than PCE, 2002Q1-2007Q2 (pp a year)", F["m_04"][0], 0.4, tol=0)
    for k, x, g in (("CPIAUCSL", 7.50, 3.95), ("PCEPI", 5.80, 3.44), ("GDPDEF", 5.68, 3.40)):
        quoted(f"{k} 2024 / 1972", W.loc[2024, k] / W.loc[1972, k], x, tol=0.005)
        quoted(f"{k} 1972-2024 (% a year)", 100 * ((W.loc[2024, k] / W.loc[1972, k]) ** (1 / 52) - 1), g, tol=0.005)
    quoted("CPI index / PCE index, 1972-2024", (W.loc[2024, "CPIAUCSL"] / W.loc[1972, "CPIAUCSL"])
           / (W.loc[2024, "PCEPI"] / W.loc[1972, "PCEPI"]), 1.293, tol=0.0005)
    quoted("  CPI - PCE (pp a year)", 100 * ((W.loc[2024, "CPIAUCSL"] / W.loc[1972, "CPIAUCSL"]) ** (1 / 52)
                                            - (W.loc[2024, "PCEPI"] / W.loc[1972, "PCEPI"]) ** (1 / 52)), 0.51, tol=0.005)
    quoted("2025 October CPI is missing", float(pd.isna(M.loc["2025-10-01", "CPIAUCSL"])), 1, tol=0)
    return W


def ex_wages(W):
    print("== ex:prices-wages")
    quoted("hourly earnings 1972 ($)", W.loc[1972, "AHETPI"], 3.90, tol=0.005)
    quoted("hourly earnings 2024 ($)", W.loc[2024, "AHETPI"], 30.12, tol=0.005)
    quoted("  nominal multiple", W.loc[2024, "AHETPI"] / W.loc[1972, "AHETPI"], 7.72, tol=0.005)
    quoted("CPI-U 1972 (1982-84 = 100)", W.loc[1972, "CPIAUCSL"], 41.81, tol=0.005)
    quoted("CPI-U 2024", W.loc[2024, "CPIAUCSL"], 313.70, tol=0.005)
    quoted("PCE 1972 (2017 = 100)", W.loc[1972, "PCEPI"], 21.31, tol=0.005)
    quoted("PCE 2024", W.loc[2024, "PCEPI"], 123.66, tol=0.005)
    rc = 100 * (W.loc[2024, "real_cpi"] / W.loc[1972, "real_cpi"] - 1)
    rp = 100 * (W.loc[2024, "real_pce"] / W.loc[1972, "real_pce"] - 1)
    quoted("real wage 1972-2024 by CPI-U (%)", rc, 2.9, tol=0.05)
    quoted("real wage 1972-2024 by PCE (%)", rp, 33.1, tol=0.05)
    pre = W.loc[1964:1994, "real_cpi"]
    quoted("CPI-deflated peak before 1995 (year)", pre.idxmax(), 1972, tol=0)
    quoted("CPI-deflated trough (year)", W["real_cpi"].dropna().idxmin(), 1995, tol=0)
    quoted("  1972-1995 by CPI-U (%)", 100 * (W.loc[1995, "real_cpi"] / W.loc[1972, "real_cpi"] - 1), -18.1, tol=0.05)
    quoted("  1972-1995 by PCE (%)", 100 * (W.loc[1995, "real_pce"] / W.loc[1972, "real_pce"] - 1), -6.1, tol=0.05)
    quoted("1972 real wage in 2024 dollars by CPI-U", W.loc[1972, "AHETPI"] * W.loc[2024, "CPIAUCSL"] / W.loc[1972, "CPIAUCSL"], 29.26, tol=0.005)
    quoted("  by PCE", W.loc[1972, "AHETPI"] * W.loc[2024, "PCEPI"] / W.loc[1972, "PCEPI"], 22.63, tol=0.005)


def fisher_section(F):
    print("== 3.4 Fisher relation")
    w = F["f_wheat_img"]
    quoted("wheat a year hence (cents)", w[0], 96, tol=0)
    quoted("gold repaid ($)", w[1], 108, tol=0)
    quoted("bushels repaid", 108 / (w[0] / 100), w[2], tol=1e-9)
    quoted("  Fisher: 112 1/2 bushels", w[2], 112.5, tol=0)
    quoted("appreciation of gold in wheat (%)", 100 * (1 / 0.96 - 1), 4.17, tol=0.005)
    quoted("wheat rate from 1 + j = (1 + a)(1 + i) (%)", 100 * ((1 / 0.96) * 1.08 - 1), w[4], tol=1e-9)
    n = F["f_negative_example_img"]
    quoted("Fisher's negative example: i (%)", 100 * ((1 + n[0] / 100) / (1 + n[1] / 100) - 1), n[2], tol=1e-9)


def ex_fisher(F):
    print("== ex:prices-fisher")
    quoted("(1) 8% gold, wheat falls to 96 cents: wheat rate (%)", 100 * real_rate(0.08, -0.04), 12.5, tol=1e-9)
    quoted("(2) wheat rises 4%: real rate (%)", 100 * real_rate(0.08, 0.04), 3.85, tol=0.005)
    L = LOAN
    quoted("(3) ex ante real rate (%)", 100 * real_rate(L["i"], L["pi_expected"]), 3.92, tol=0.005)
    quoted("    ex post real rate (%)", 100 * real_rate(L["i"], L["pi_actual"]), -1.85, tol=0.005)
    rep = L["principal"] * (1 + L["i"])
    quoted("    repayment (yuan)", rep, 106_000, tol=1e-6)
    quoted("    expected real value (yuan of today)", rep / (1 + L["pi_expected"]), 103_922, tol=0.5)
    quoted("    actual real value", rep / (1 + L["pi_actual"]), 98_148, tol=0.5)
    quoted("    transfer to the debtor", rep / (1 + L["pi_expected"]) - rep / (1 + L["pi_actual"]), 5_773, tol=0.5)


def ex_bond():
    print("== ex:prices-bond")
    i0 = BOND["i0"]
    quoted("price at 3%", bond_price(i0), 100.0, tol=1e-9)
    quoted("price at 4%", bond_price(0.04), 91.89, tol=0.005)
    quoted("price at 2%", bond_price(0.02), 108.98, tol=0.005)
    quoted("Macaulay duration (years)", macaulay(i0), 8.79, tol=0.005)
    quoted("modified duration", modified(i0), 8.53, tol=0.005)
    quoted("+1 pp: actual change (%)", bond_price(0.04) - 100, -8.11, tol=0.005)
    quoted("-1 pp: actual change (%)", bond_price(0.02) - 100, 8.98, tol=0.005)
    quoted("approximation 100 - 8.53", 100 - modified(i0), 91.47, tol=0.005)
    quoted("  error of the approximation, +1 pp", bond_price(0.04) - (100 - modified(i0)), 0.42, tol=0.005)
    quoted("  error of the approximation, -1 pp", bond_price(0.02) - (100 + modified(i0)), 0.45, tol=0.005)
    # holding-period return: buy at par, yields rise to 4% after one year
    p9 = bond_price(0.04, years=9)
    quoted("9-year bond at 4%", p9, 92.56, tol=0.005)
    quoted("one-year holding-period return (%)", 100 * ((BOND["coupon"] + p9) / 100 - 1), -4.44, tol=0.005)
    tab = price_changes_by_maturity()
    quoted("30-year: +1 pp (%)", tab.loc[30, "up"], -17.3, tol=0.05)
    quoted("30-year: -1 pp (%)", tab.loc[30, "down"], 22.4, tol=0.05)
    quoted("2-year: +1 pp (%)", tab.loc[2, "up"], -1.9, tol=0.05)


def compare_hpr(J):
    print("== compare box: YTM vs holding-period return (Japan 2016)")
    a, b = (J.loc[d, "10Y"] for d in JGB_HPR_DATES)
    quoted("10Y 2016-01-28 (%)", a, 0.229, tol=0)
    quoted("10Y 2016-07-27 (%)", b, -0.297, tol=0)
    p0 = 100 / (1 + a / 100) ** 10
    p1 = 100 / (1 + b / 100) ** 9.5
    quoted("zero price 2016-01-28", p0, 97.74, tol=0.005)
    quoted("zero price 2016-07-27 (9.5 years left)", p1, 102.87, tol=0.005)
    quoted("six-month holding-period return (%)", 100 * (p1 / p0 - 1), 5.2, tol=0.05)
    quoted("loss if held to maturity from 2016-07-27 (%)", 100 * (1 - 100 / p1), 2.8, tol=0.05)
    quoted("zero-coupon 10-year: modified duration at 0.229% (about 10)", 10 / (1 + a / 100), 10, tol=0.05)


def curve(F, D, J):
    print("== 3.6 yield curve")
    inv = inversions(D)
    assert len(inv) == 2, inv
    a, b, low, when = inv[-1]
    quoted("US inversion starts 2022-07-06", float(a.strftime("%Y%m%d")), 20220706, tol=0)
    quoted("  ends 2024-08-26 (last negative day)", float(b.strftime("%Y%m%d")), 20240826, tol=0)
    quoted("  deepest (pp)", low, -1.08, tol=0.005)
    quoted("  on 2023-07-03", float(when.strftime("%Y%m%d")), 20230703, tol=0)
    a0, b0, low0, _ = inv[0]
    quoted("the other long inversion starts in 2000", a0.year, 2000, tol=0)
    quoted("  low (pp)", low0, -0.52, tol=0.005)
    print("-- case box: Japan")
    quoted("BoJ: negative rate (%)", F["boj_nirp"][0], 0.1, tol=0)
    quoted("  vote for", F["boj_nirp_vote"][0], 5, tol=0)
    quoted("  vote against", F["boj_nirp_vote"][1], 4, tol=0)
    quoted("  effective from February 16", F["boj_nirp_start"][0], 16, tol=0)
    quoted("YCC vote for", F["boj_ycc_vote"][0], 7, tol=0)
    quoted("  against", F["boj_ycc_vote"][1], 2, tol=0)
    quoted("  JGB purchases (trn yen a year)", F["boj_ycc_pace"][0], 80, tol=0)
    quoted("exit: call rate upper bound (%)", F["boj_exit"][1], 0.1, tol=0)
    quoted("  effective March 21", F["boj_exit_start"][0], 21, tol=0)
    c = {d: J.loc[d] for d in JGB_DATES}
    quoted("2016-01-28 10Y", c["2016-01-28"]["10Y"], 0.229, tol=0)
    quoted("2016-01-28 1Y", c["2016-01-28"]["1Y"], -0.024, tol=0)
    quoted("2016-07-27 10Y", c["2016-07-27"]["10Y"], -0.297, tol=0)
    quoted("2016-07-27 15Y", c["2016-07-27"]["15Y"], -0.074, tol=0)
    quoted("2016-07-27 20Y", c["2016-07-27"]["20Y"], 0.161, tol=0)
    quoted("2016-07-27 7Y (lowest point of the curve)", c["2016-07-27"]["7Y"], -0.423, tol=0)
    quoted("2016-07-27: the minimum of the curve is at 7Y", float(c["2016-07-27"].idxmin() == "7Y"), 1, tol=0)
    quoted("2016-07-27 40Y", c["2016-07-27"]["40Y"], 0.333, tol=0)
    quoted("10Y minimum of the snapshot is on 2016-07-27", float(J["10Y"].idxmin() == pd.Timestamp("2016-07-27")), 1, tol=0)
    neg10 = J.loc["2013":, "10Y"] < 0
    quoted("first business day with 10Y < 0", float(J.loc["2013":].index[neg10.values][0].strftime("%Y%m%d")), 20160209, tol=0)
    quoted("business days with 10Y < 0, 2016-2026", neg10.sum(), 453, tol=0)
    quoted("2019-08-28 10Y", c["2019-08-28"]["10Y"], -0.271, tol=0)
    quoted("2024-03-18 10Y", c["2024-03-18"]["10Y"], 0.774, tol=0)
    quoted("2024-03-18 1Y", c["2024-03-18"]["1Y"], 0.081, tol=0)
    quoted("2026-09-30 10Y", c["2026-09-30"]["10Y"], 3.057, tol=0)
    quoted("2026-09-30 1Y", c["2026-09-30"]["1Y"], 1.684, tol=0)
    quoted("2026-09-30 30Y", c["2026-09-30"]["30Y"], 4.098, tol=0)
    quoted("1990-09-28 10Y (month-end high)", J.loc["1990-09-28", "10Y"], 8.105, tol=0)
    quoted("  highest month-end 10Y is 1990-09-28", float(J["10Y"].idxmax() == pd.Timestamp("1990-09-28")), 1, tol=0)


def ex_forward(J):
    print("== ex:prices-forward")
    c = J.loc["2026-09-30"]
    quoted("2Y", c["2Y"], 1.952, tol=0)
    quoted("5Y", c["5Y"], 2.399, tol=0)
    f11 = forward(c["1Y"], 1, c["2Y"], 2)
    quoted("1-year rate one year ahead (%)", f11, 2.22, tol=0.005)
    quoted("  arithmetic shortcut 2 x 1.952 - 1.684", 2 * c["2Y"] - c["1Y"], 2.22, tol=0.005)
    f55 = forward(c["5Y"], 5, c["10Y"], 10)
    quoted("5-year rate five years ahead (%)", f55, 3.72, tol=0.005)
    quoted("  shortcut 2 x 3.057 - 2.399", 2 * c["10Y"] - c["5Y"], 3.715, tol=0.0005)


def breakeven_section(F, D, T, M):
    print("== 3.7 index-linked gilts and TIPS")
    quoted("Wilson Report", F["dmo_wilson"][0], 1980, tol=0)
    quoted("first index-linked gilt", F["dmo_first"][0], 1981, tol=0)
    quoted("  £bn nominal", F["dmo_issue"][0], 1, tol=0)
    quoted("  coupon (%)", F["dmo_issue"][1], 2, tol=0)
    quoted("  maturity", F["dmo_issue"][2], 1996, tol=0)
    quoted("3-month lag from", F["dmo_lag"][0], 2005, tol=0)
    quoted("TIPS lag (months)", F["cfr_lag"][0], 3, tol=0)
    first = T.iloc[0]
    quoted("first TIPS auction 1997-01-29", float(first["auction_date"].strftime("%Y%m%d")), 19970129, tol=0)
    quoted("  coupon (%)", first["int_rate"], 3.375, tol=0)
    quoted("  real yield (%)", first["high_yield"], 3.449, tol=0)
    quoted("  offered ($bn)", first["offering_amt"] / 1e9, 7.0, tol=0)
    quoted("  tendered ($bn)", first["total_tendered"] / 1e9, 37.6, tol=0.05)
    quoted("  accepted ($bn)", first["total_accepted"] / 1e9, 7.35, tol=0.005)
    quoted("  tendered / accepted", first["total_tendered"] / first["total_accepted"], 5.1, tol=0.05)
    quoted("  maturity 2007-01-15", float(first["maturity_date"].strftime("%Y%m%d")), 20070115, tol=0)
    five = T[T["security_term"] == "5-Year"].iloc[0]
    quoted("first 5-year TIPS auctioned in July 1997", float(five["auction_date"].strftime("%Y%m")), 199707, tol=0)
    quoted("10-year Treasury yield on 1997-01-29 (%)", D.loc["1997-01-29", "DGS10"], 6.63, tol=0)
    quoted("breakeven at the first auction (%)", D.loc["1997-01-29", "DGS10"] - first["high_yield"], 3.18, tol=0.005)
    be = D["BE"].dropna()
    quoted("breakeven: lowest daily (%)", be.min(), 0.04, tol=0.005)
    quoted("  on 2008-11-20", float(be.idxmin().strftime("%Y%m%d")), 20081120, tol=0)
    quoted("breakeven: highest daily (%)", be.max(), 3.02, tol=0.005)
    quoted("  on 2022-04-21", float(be.idxmax().strftime("%Y%m%d")), 20220421, tol=0)
    quoted("breakeven 2026-10-09 (%)", be.loc["2026-10-09"], 2.33, tol=0.005)
    quoted("  10-year nominal 2026-10-09", D.loc["2026-10-09", "DGS10"], 5.24, tol=0)
    quoted("  10-year TIPS 2026-10-09", D.loc["2026-10-09", "DFII10"], 2.91, tol=0)
    quoted("mean daily breakeven 2003-2026 (%)", be.mean(), 2.11, tol=0.005)
    bm = breakeven_monthly(D)
    quoted("fig (a): monthly means from 2003-01", float(bm.index[0].strftime("%Y%m")), 200301, tol=0)
    quoted("  to 2026-09 (October 2026 incomplete)", float(bm.index[-1].strftime("%Y%m")), 202609, tol=0)
    quoted("  lowest monthly breakeven (%)", bm["BE"].min(), 0.25, tol=0.005)
    quoted("  in 2008-12", float(bm["BE"].idxmin().strftime("%Y%m")), 200812, tol=0)
    r = D["DFII10"].dropna()
    quoted("TIPS yield: lowest (%)", r.min(), -1.19, tol=0.005)
    quoted("  on 2021-08-03", float(r.idxmin().strftime("%Y%m%d")), 20210803, tol=0)
    quoted("TIPS series starts in 2003", r.index[0].year, 2003, tol=0)
    quoted("10-year nominal 2008-11-12 (%)", D.loc["2008-11-12", "DGS10"], 3.75, tol=0)
    quoted("  2008-11-20", D.loc["2008-11-20", "DGS10"], 3.10, tol=0)
    quoted("10-year TIPS 2008-11-12 (%)", D.loc["2008-11-12", "DFII10"], 2.79, tol=0)
    quoted("  2008-11-20", D.loc["2008-11-20", "DFII10"], 3.06, tol=0)
    quoted("TIPS yield: highest (%)", r.max(), 3.15, tol=0)
    quoted("  on 2008-11-21", float(r.idxmax().strftime("%Y%m%d")), 20081121, tol=0)


def ex_tips(F, T, M):
    print("== ex:prices-tips")
    cpi = M["CPIAUCNS"]
    quoted("CPI-U NSA October 1996", cpi["1996-10-01"], 158.3, tol=0)
    quoted("CPI-U NSA November 1996", cpi["1996-11-01"], 158.6, tol=0)
    r0 = ref_cpi(pd.Timestamp("1997-01-15"), cpi)
    quoted("reference CPI 1997-01-15", r0, 158.43548, tol=0)
    quoted("  Treasury's figure", T.iloc[0]["ref_cpi_on_dated_date"], 158.43548, tol=0)
    quoted("CFR example: reference CPI 1996-04-15", ref_cpi(pd.Timestamp("1996-04-15"), cpi), 154.63333, tol=0)
    quoted("  CPI-U NSA January 1996", cpi["1996-01-01"], F["cfr_nsa"][0], tol=0)
    quoted("CPI-U NSA October 2006", cpi["2006-10-01"], 201.8, tol=0)
    quoted("CPI-U NSA November 2006", cpi["2006-11-01"], 201.5, tol=0)
    r1 = ref_cpi(pd.Timestamp("2007-01-15"), cpi)
    quoted("reference CPI 2007-01-15", r1, 201.66452, tol=0)
    quoted("index ratio at maturity", r1 / r0, 1.2728, tol=0.00005)
    g = 100 * ((r1 / r0) ** 0.1 - 1)
    quoted("inflation over the life of the bond (% a year)", g, 2.44, tol=0.005)
    quoted("breakeven at auction - realized (pp)", 6.63 - 3.449 - g, 0.74, tol=0.005)
    quoted("TIPS: real yield plus realized inflation, approx (%)", 100 * ((1.03449) * (1 + g / 100) - 1), 5.98, tol=0.005)
    quoted("principal of 1,000 at maturity ($)", 1000 * r1 / r0, 1272.85, tol=0.005)


def test(F, D, M):
    print("== 3.8 tests")
    u = F["f_us_bonds_img"]
    quoted("coin 1870-79 (%)", u[0], 7.1, tol=0)
    quoted("currency (%)", u[1], 6.3, tol=0)
    quoted("expected appreciation from 1 + j = (1 + i)(1 + a) (%)", 100 * ((1 + u[0] / 100) / (1 + u[1] / 100) - 1), u[2], tol=0.05)
    quoted("actual (%)", u[3], 2.1, tol=0)
    quoted("  expected / actual", u[2] / u[3], 0.4, tol=0.02)
    gp = F["f_gold_price_img"]
    quoted("gold in currency, January 1870", gp[0], 119.9, tol=0)
    quoted("  January 1879", gp[1], 100, tol=0)
    quoted("resumption on January 1 of", F["f_resumption_date_img"][0], 1879, tol=0)
    quoted("gold price recomputed (% a year)", 100 * ((gp[0] / gp[1]) ** (1 / 9) - 1), 2.04, tol=0.005)
    rs = F["f_resumption_img"]
    quoted("after the Resumption Act: expected (%)", rs[1], 2, tol=0)
    quoted("  actual (%)", rs[2], 3.6, tol=0)
    ind = F["f_india_img"]
    quoted("India: difference before 1875 (%)", ind[0], 0.2, tol=0)
    quoted("  since 1875 (%)", ind[1], 0.7, tol=0)
    quoted("  in one year (%)", ind[2], 1.1, tol=0)
    o = F["boj_others"]
    quoted("BoJ note: Switzerland (%)", -o[0], -0.75, tol=0)
    quoted("  Sweden (%)", -o[1], -1.1, tol=0)
    quoted("  Denmark (%)", -o[2], -0.65, tol=0)
    ft = forecast_test(D, M)
    ft = ft.loc[TEST_FROM:TEST_TO]
    quoted("months in the test", len(ft), 163, tol=0)
    quoted("mean breakeven (%)", ft["be"].mean(), 2.11, tol=0.005)
    quoted("mean realized (%)", ft["realized"].mean(), 2.22, tol=0.005)
    err = ft["be"] - ft["realized"]
    quoted("mean error (pp)", err.mean(), -0.10, tol=0.005)
    quoted("mean absolute error (pp)", err.abs().mean(), 0.62, tol=0.005)
    quoted("correlation", ft["be"].corr(ft["realized"]), -0.28, tol=0.005)
    quoted("2008-07 breakeven", ft.loc["2008-07-01", "be"], 2.44, tol=0.005)
    quoted("  realized", ft.loc["2008-07-01", "realized"], 1.37, tol=0.005)
    quoted("2009-01 breakeven", ft.loc["2009-01-01", "be"], 0.61, tol=0.005)
    quoted("  realized", ft.loc["2009-01-01", "realized"], 1.77, tol=0.005)
    quoted("2016-02: largest shortfall (pp)", err.min(), -1.95, tol=0.005)
    quoted("  in 2016-02", float(err.idxmin().strftime("%Y%m")), 201602, tol=0)
    quoted("  2016-02 breakeven", ft.loc["2016-02-01", "be"], 1.31, tol=0.005)
    quoted("  2016-02 realized", ft.loc["2016-02-01", "realized"], 3.26, tol=0.005)
    quoted("2008-07: largest excess (pp)", err.max(), 1.07, tol=0.005)
    crisis = ft.loc["2008-11":"2009-01"]
    quoted("fig (b): 2008-11 to 2009-01, breakeven below 1% (max)", crisis["be"].max(), 0.64, tol=0.005)
    quoted("  realized inflation after them (min)", crisis["realized"].min(), 1.72, tol=0.005)
    late = ft.loc["2015-01":"2016-08"]
    quoted("fig (b): 2015-01 to 2016-08, breakeven at least 1.3%", late["be"].min(), 1.31, tol=0.005)
    quoted("  at most 1.9%", late["be"].max(), 1.87, tol=0.005)
    quoted("  realized inflation after them, at least 3%", late["realized"].min(), 3.06, tol=0.005)
    quoted("share of months with breakeven below realized", (err < 0).mean(), 0.51, tol=0.005)


def legacy(F):
    print("== 3.9 legacy")
    quoted("FOMC goal (%)", F["fomc_goal"][0], 2, tol=0)
    quoted("  adopted", F["fomc_dates"][0], 2012, tol=0)
    quoted("  reaffirmed", F["fomc_dates"][1], 2026, tol=0)


def selfcheck(F):
    print("== self-check answers")
    t1 = F["b_table1_img"]
    p0, p1 = dict(beef=t1[0], chicken=t1[2]), dict(beef=t1[4], chicken=t1[6])
    q0 = dict(beef=t1[1], chicken=t1[3])
    quoted("(1) no substitution: Laspeyres", laspeyres(p0, p1, q0), 1.20, tol=1e-12)
    quoted("    Paasche", paasche(p0, p1, q0), 1.20, tol=1e-12)
    quoted("    Fisher", fisher_index(p0, p1, q0, q0), 1.20, tol=1e-12)
    quoted("(2) 1.011^25", 1.011 ** 25, 1.315, tol=0.0005)
    quoted("(3) ex ante (%)", 100 * real_rate(0.05, 0.03), 1.94, tol=0.005)
    quoted("    ex post (%)", 100 * real_rate(0.05, 0.01), 3.96, tol=0.005)
    p4, p5 = 100 / 1.04 ** 5, 100 / 1.05 ** 5
    quoted("(4) 5-year zero at 4%", p4, 82.19, tol=0.005)
    quoted("    modified duration 5 / 1.04", 5 / 1.04, 4.81, tol=0.005)
    quoted("    at 5%", p5, 78.35, tol=0.005)
    quoted("    change (%)", 100 * (p5 / p4 - 1), -4.67, tol=0.005)
    quoted("(5) forward, no term premium (%)", forward(2, 1, 3, 2), 4.01, tol=0.005)
    quoted("    with 0.4 pp term premium (%)", forward(2, 1, 2.6, 2), 3.20, tol=0.005)
    quoted("(6) breakeven (%)", 4.5 - 2.0, 2.5, tol=1e-12)
    quoted("    expected inflation = 2.5 - 0.3 + 0.2 (%)", 2.5 - 0.3 + 0.2, 2.4, tol=1e-12)


def main():
    F = facts()
    M, Q, D, J, T = monthly(), quarterly(), daily(), jgb(), tips()
    world(F)
    ex_beef(F)
    boskin_bias(F, M)
    ex_chain()
    W = real_side(F, M, Q)
    ex_wages(W)
    fisher_section(F)
    ex_fisher(F)
    ex_bond()
    compare_hpr(J)
    curve(F, D, J)
    ex_forward(J)
    breakeven_section(F, D, T, M)
    ex_tips(F, T, M)
    test(F, D, M)
    legacy(F)
    selfcheck(F)
    print("all Chapter 3 checks passed")


if __name__ == "__main__":
    main()
