"""Chapter 4 (货币、银行与央行的资产负债表): every number quoted in zh/ch04_money.tex.

    python3 checks/check_ch04.py

Inputs are six snapshots:
  money_facts              quotations from McLeay, Radia & Thomas (2014, Bank of England), Cagan (1965), the
                           Federal Reserve (2008-2026: press releases, FOMC statements, minutes and implementation
                           notes, the FEDS Note on September 2019, the H.4.1 release of 8 October 2026, the Fedwire and
                           National Settlement Service pages), the ECB (2024), the People's Bank of China's monetary
                           policy reports (2011 Q4, 2025 Q2, 2025 Q4, 2026 Q2), Smith (1776), Knapp (1924), Peru's
                           Decreto Supremo 151-2002-EF and BIS Working Paper 675; checked by
                           data/fetch/verify_web_quotes.py, one row (Cagan's identity) read on the page image
  fred_fed_weekly          the Federal Reserve's balance sheet, Wednesday levels (H.4.1, via FRED)
  fred_money_monthly       monetary base, M2 and total reserves (H.3 and H.6, via FRED)
  fred_policy_rates_daily  effective federal funds rate, target and target range, interest on reserves, overnight
                           reverse repo award rate (via FRED); the EFFR carries the New York Fed's notice
  pbc_balance_sheet        the balance sheet of the People's Bank of China, monthly, 2002-2026
  bcrp_dollarization       Peru: dollarization of broad money and twelve-month inflation (BCRPData)
The figure module figsrc/fig_ch04.py imports the functions defined here.

Notation of the chapter (local; Appendix B uses M for the money stock): H base money, C currency held by the
public (not consumption), R reserves, D deposits, c = C/M, r = R/D.
    base and broad money   H = C + R,  M = C + D                                     (eq:money-base)
    multiplier             M = H / (c + r - c r)                                     (eq:money-mult)
    reserve identity       R = A - N - D^T - Q - X - K  (R: reserve balances)       (eq:money-reserves)
    rate corridor          i_D <= i <= i_L; floor: i ~ i_D when R is ample           (eq:money-corridor)
The five-step economy of tab:money-steps (a loan of 10, a tax of 8, a bond of 8 sold to a household, spending of
16, a purchase of the bond by the central bank), the variants in ex:money-tax and the self-check are teaching
inputs, defined below and stated in the text. US currency held by the public is approximated by the monetary
base less total reserves (total reserves include the vault cash used to satisfy reserve requirements).
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from common import load_snapshot, quoted

# ---------------------------------------------------------------------------------------------------
# Teaching inputs stated in the text
# tab:money-steps: changes in the balance sheets of four sectors, in the order of the text. Each entry is
# (sector, side, item, change); side is "A" (asset), "L" (liability) or "W" (net worth).
STEPS = {
    "loan": [("bank", "A", "loans", 10), ("bank", "L", "deposits", 10),
             ("household", "A", "deposits", 10), ("household", "L", "loans", 10)],
    "tax": [("household", "A", "deposits", -8), ("household", "W", "net worth", -8),
            ("bank", "A", "reserves", -8), ("bank", "L", "deposits", -8),
            ("cb", "L", "reserves", -8), ("cb", "L", "tga", 8),
            ("treasury", "A", "tga", 8), ("treasury", "W", "net worth", 8)],
    "bond": [("household", "A", "deposits", -8), ("household", "A", "bonds", 8),
             ("bank", "A", "reserves", -8), ("bank", "L", "deposits", -8),
             ("cb", "L", "reserves", -8), ("cb", "L", "tga", 8),
             ("treasury", "A", "tga", 8), ("treasury", "L", "bonds", 8)],
    "spend": [("treasury", "A", "tga", -16), ("treasury", "W", "net worth", -16),
              ("cb", "L", "tga", -16), ("cb", "L", "reserves", 16),
              ("bank", "A", "reserves", 16), ("bank", "L", "deposits", 16),
              ("household", "A", "deposits", 16), ("household", "W", "net worth", 16)],
    "qe": [("cb", "A", "bonds", 8), ("cb", "L", "reserves", 8),
           ("bank", "A", "reserves", 8), ("bank", "L", "deposits", 8),
           ("household", "A", "deposits", 8), ("household", "A", "bonds", -8)],
}
# ex:money-tax, variant: the bank (not the household) buys the bond in step 3 and sells it to the central bank in
# step 5
STEPS_BANK = dict(STEPS,
                  bond=[("bank", "A", "reserves", -8), ("bank", "A", "bonds", 8),
                        ("cb", "L", "reserves", -8), ("cb", "L", "tga", 8),
                        ("treasury", "A", "tga", 8), ("treasury", "L", "bonds", 8)],
                  qe=[("cb", "A", "bonds", 8), ("cb", "L", "reserves", 8),
                      ("bank", "A", "reserves", 8), ("bank", "A", "bonds", -8)])
# ex:money-smith: Smith's note, payable fifteen years hence at six per cent
SMITH = dict(face=100.0, years=15, i=0.06)
# ex:money-floor: a bank that borrows overnight and holds the funds as reserves, per $1 billion; money-market
# interest is on an actual/360 basis
ARB = dict(amount=1e9, days=360)
# the multiplier example and test: the months compared
MULT_MONTHS = ("2008-08-01", "2008-12-01")


# ---------------------------------------------------------------------------------------------------
# Data
def facts() -> dict[str, list[float]]:
    """id -> the numbers of the value column (several are separated by ';')."""
    df, _ = load_snapshot("money_facts", dtype={"value": str})
    out = {}
    for _, r in df.iterrows():
        v = r["value"]
        if isinstance(v, str) and v.strip():
            out[r["id"]] = [float(x) for x in v.split(";")]
    return out


def fed() -> pd.DataFrame:
    """H.4.1 Wednesday levels, millions of dollars, with the residual items of fig money_fed."""
    df, _ = load_snapshot("fred_fed_weekly", parse_dates=["date"])
    df = df.set_index("date")
    df["other_assets"] = df.WALCL - df.TREAST - df.WSHOMCB
    df["other_liab"] = df.WLTLECL - df.WLFN - df.WLODLL - df.WDTGAL - df.WLRRAL + df.WCTCL   # with capital
    return df


def money() -> pd.DataFrame:
    """Monthly averages, billions of dollars, with the ratios of eq:money-mult."""
    df, _ = load_snapshot("fred_money_monthly", parse_dates=["date"])
    df = df.set_index("date")
    df["C"] = df.BOGMBASE - df.TOTRESNS            # currency held by the public (approximation)
    df["D"] = df.M2NS - df.C
    df["c"] = df.C / df.M2NS
    df["r"] = df.TOTRESNS / df.D
    df["m"] = df.M2NS / df.BOGMBASE
    return df


def rates() -> pd.DataFrame:
    """Daily rates (percent); IOR is IOER to 2021-07-28 and IORB from 2021-07-29; spreads in basis points."""
    df, _ = load_snapshot("fred_policy_rates_daily", parse_dates=["date"])
    df = df.set_index("date")
    df["IOR"] = df.IOER.fillna(df.IORB)
    df["sp_ior"] = 100 * (df.EFFR - df.IOR)
    df["sp_rrp"] = 100 * (df.EFFR - df.RRPONTSYAWARD)
    return df


def pbc() -> pd.DataFrame:
    df, _ = load_snapshot("pbc_balance_sheet")
    df = df.set_index("month")
    for k in ("fx", "claims_banks", "claims_gov"):
        df[k + "_sh"] = 100 * df[k] / df.total_assets
    return df


def peru() -> pd.DataFrame:
    df, _ = load_snapshot("bcrp_dollarization")
    return df.set_index("month")


def weekly_spread(Wk: pd.DataFrame, R: pd.DataFrame) -> pd.DataFrame:
    """Reserve balances (Wednesday level, trillions) against the mean EFFR - IOR spread of the week to that
    Wednesday (basis points), from 2009 on (interest on reserves began on 2008-10-09)."""
    d = R.dropna(subset=["EFFR", "IOR"])
    sp = d.sp_ior.resample("W-WED").mean()
    J = pd.DataFrame({"res": Wk.WLODLL / 1e6, "sp": sp}).dropna()
    return J.loc["2009":]


def yearly(series: pd.Series) -> pd.Series:
    return series.groupby(series.index.year).mean()


# ---------------------------------------------------------------------------------------------------
# The five-step economy (tab:money-steps)
def apply(steps: dict, names=None) -> dict:
    """Total change of every (sector, side, item) over the named steps."""
    out: dict = {}
    for k in names or steps:
        for sec, side, item, v in steps[k]:
            out[(sec, side, item)] = out.get((sec, side, item), 0) + v
    return out


def balanced(step) -> bool:
    """Every sector: change in assets = change in liabilities + change in net worth."""
    secs = {s for s, *_ in step}
    return all(sum(v for s, side, _, v in step if s == sec and side == "A")
               == sum(v for s, side, _, v in step if s == sec and side in ("L", "W")) for sec in secs)


def broad_money(chg: dict) -> float:
    """Change in M = currency held by the public + deposits (deposits are the bank's liability)."""
    return chg.get(("bank", "L", "deposits"), 0)


def base_money(chg: dict) -> float:
    """Change in H = currency + reserves (the central bank's liabilities to the public and to banks)."""
    return chg.get(("cb", "L", "reserves"), 0)


# ---------------------------------------------------------------------------------------------------
# The multiplier (eq:money-mult)
def multiplier(c: float, r: float) -> float:
    return 1 / (c + r - c * r)


# ---------------------------------------------------------------------------------------------------
# Checks, in the order of the text
def opening(Mn):
    print("== opening")
    a, b = (Mn.loc[d] for d in MULT_MONTHS)
    quoted("base money, August 2008 ($bn)", a.BOGMBASE, 847.6, tol=0)
    quoted("base money, December 2008 ($bn)", b.BOGMBASE, 1666.4, tol=0)
    quoted("  multiple ('nearly doubled')", b.BOGMBASE / a.BOGMBASE, 1.97, tol=0.005)
    quoted("M2 (NSA), August 2008 ($bn)", a.M2NS, 7758.2, tol=0)
    quoted("M2 (NSA), December 2008 ($bn)", b.M2NS, 8244.1, tol=0)
    quoted("  growth (%)", 100 * (b.M2NS / a.M2NS - 1), 6.3, tol=0.05)


def world(F, Wk, R):
    print("== 4.1 the world of 2008 and 2014")
    quoted("Fed total assets 2008-09-03 ($bn)", Wk.loc["2008-09-03", "WALCL"] / 1e3, 905.3, tol=0.05)
    quoted("  2008-10-01 ($bn)", Wk.loc["2008-10-01", "WALCL"] / 1e3, 1504.0, tol=0.05)
    quoted("  2008-12-31 ($bn)", Wk.loc["2008-12-31", "WALCL"] / 1e3, 2239.5, tol=0.05)
    quoted("  multiple, Sept 3 to Dec 31", Wk.loc["2008-12-31", "WALCL"] / Wk.loc["2008-09-03", "WALCL"], 2.47, tol=0.005)
    quoted("Treasuries held 2008-09-03 ($bn)", Wk.loc["2008-09-03", "TREAST"] / 1e3, 479.7, tol=0.05)
    quoted("  2008-12-31 ($bn)", Wk.loc["2008-12-31", "TREAST"] / 1e3, 475.9, tol=0.05)
    quoted("  other assets (lending etc.), 2008-12-31 ($bn)", Wk.loc["2008-12-31", "other_assets"] / 1e3, 1763.5, tol=0.05)
    quoted("    2008-09-03 ($bn)", Wk.loc["2008-09-03", "other_assets"] / 1e3, 425.5, tol=0.05)
    quoted("reserve balances 2008-09-03 ($bn)", Wk.loc["2008-09-03", "WLODLL"] / 1e3, 10.9, tol=0.05)
    quoted("  2008-12-31 ($bn)", Wk.loc["2008-12-31", "WLODLL"] / 1e3, 860.0, tol=0.05)
    law = F["fr_ior_law"]
    quoted("IOR authorized by the act of", law[0], 2006, tol=0)
    quoted("  from October 1 of", law[1], 2011, tol=0)
    quoted("  brought forward to October 1 of", law[2], 2008, tol=0)
    quoted("required reserves: target less (bp)", F["fr_ior_rr"][0], 10, tol=0)
    quoted("excess reserves: lowest target less (bp)", F["fr_ior_er"][0], 75, tol=0)
    t = R.DFEDTAR
    quoted("target before 2008-10-08 (%)", t["2008-10-07"], 2.0, tol=0)
    quoted("target from 2008-10-08 (%)", t["2008-10-08"], 1.5, tol=0)
    quoted("target from 2008-10-29 (%)", t["2008-10-29"], 1.0, tol=0)
    quoted("range from 2008-12-16: lower (%)", R.loc["2008-12-16", "DFEDTARL"], 0.0, tol=0)
    quoted("  upper (%)", R.loc["2008-12-16", "DFEDTARU"], 0.25, tol=0)
    quoted("IOER on 2008-10-09 (%)", R.loc["2008-10-09", "IOER"], 0.75, tol=0)
    quoted("  = target 1.5 less 75 bp", 1.5 - F["fr_ior_er"][0] / 100, 0.75, tol=1e-12)
    late = R.loc["2008-10-09":"2008-12-15"].dropna(subset=["EFFR"])
    quoted("EFFR - IOER, 2008-10-09 to 2008-12-15: lowest (bp)", late.sp_ior.min(), -89, tol=0.5)
    quoted("  mean (bp)", late.sp_ior.mean(), -43, tol=0.5)
    quoted("  EFFR below the target on every day", float((late.EFFR < late.DFEDTAR).all()), 1, tol=0)
    quoted("BoE: three sets of constraints", F["mc_three"][0], 3, tol=0)


def sheets(F, Mn, P):
    print("== 4.2 four balance sheets: compare box")
    a = Mn.loc["2026-08-01"]
    quoted("US base money, August 2026 ($bn)", a.BOGMBASE, 5411.6, tol=0)
    quoted("US M2 (NSA), August 2026 ($bn)", a.M2NS, 23284.3, tol=0)
    quoted("  M2 / base", a.m, 4.30, tol=0.005)
    quoted("  total reserves ($bn)", a.TOTRESNS, 2936.0, tol=0)
    quoted("  currency held by the public ($bn)", a.C, 2475.6, tol=0.05)
    quoted("  currency / M2 (%)", 100 * a.c, 10.6, tol=0.05)
    m2, m0 = F["pbc26_m2"][0], F["pbc26_m0"][0]
    quoted("China M2, June 2026 (tn yuan)", m2, 356.7, tol=0)
    quoted("China M0, June 2026 (tn yuan)", m0, 14.7, tol=0)
    quoted("  M0 / M2 (%)", 100 * m0 / m2, 4.1, tol=0.05)
    rm = P.loc["2026-06", "reserve_money"] / 1e4
    quoted("PBoC reserve money, June 2026 (tn yuan)", rm, 40.6, tol=0.05)
    quoted("  M2 / reserve money", m2 / rm, 8.79, tol=0.005)


def fed_table(F):
    print("== tab:money-fed (H.4.1, Wednesday 7 October 2026, $bn)")
    tot = F["h4_total"][0]
    ust, bills = F["h4_ust"]
    mbs, loans = F["h4_mbs"][0], F["h4_loans"][0]
    other_a = tot - ust - mbs - loans
    notes, rrp = F["h4_notes"][0], F["h4_rrp"][0]
    dep, res = F["h4_deposits"]
    tga, foreign, other_dep = F["h4_tga"]
    dai, contrib, oth_l, tot_l = F["h4_other"]
    cap = F["h4_capital"][0]
    quoted("total assets", tot / 1e3, 6747.6, tol=0.05)
    quoted("Treasury securities", ust / 1e3, 4566.4, tol=0.05)
    quoted("  of which bills", bills / 1e3, 562.2, tol=0.05)
    quoted("mortgage-backed securities", mbs / 1e3, 1898.1, tol=0.05)
    quoted("loans", loans / 1e3, 10.0, tol=0.05)
    quoted("other assets (residual)", other_a / 1e3, 273.1, tol=0.05)
    quoted("securities share of assets (%)", 100 * (ust + mbs) / tot, 95.8, tol=0.05)
    quoted("Federal Reserve notes", notes / 1e3, 2434.3, tol=0.05)
    quoted("reverse repurchase agreements", rrp / 1e3, 333.7, tol=0.05)
    quoted("deposits, total", dep / 1e3, 4157.1, tol=0.05)
    quoted("  reserve balances (other deposits of depository institutions)", res / 1e3, 3022.1, tol=0.05)
    quoted("  Treasury General Account", tga / 1e3, 885.8, tol=0.05)
    quoted("  foreign official", foreign / 1e3, 9.5, tol=0.05)
    quoted("  other", other_dep / 1e3, 239.8, tol=0.05)
    quoted("  deposits add up (term deposits 0)", res + tga + foreign + other_dep, dep, tol=0)
    quoted("other liabilities and accrued dividends", oth_l / 1e3, -225.6, tol=0.05)
    quoted("deferred availability cash items", dai / 1e3, 0.3, tol=0.05)
    quoted("Treasury contributions to credit facilities", contrib, 0, tol=0)
    quoted("deferred availability + other liabilities", (dai + contrib + oth_l) / 1e3, -225.3, tol=0.05)
    quoted("total liabilities", tot_l / 1e3, 6699.8, tol=0.05)
    quoted("  liabilities add up", notes + rrp + dep + dai + contrib + oth_l, tot_l, tol=0)
    quoted("capital", cap / 1e3, 47.7, tol=0.05)
    quoted("  liabilities + capital = assets", tot_l + cap, tot, tol=0)
    quoted("reserve balances / total assets (%)", 100 * res / tot, 44.8, tol=0.05)
    quoted("notes + reserves = base money ($bn)", (notes + res) / 1e3, 5456.4, tol=0.05)
    return dict(tot=tot, notes=notes, rrp=rrp, tga=tga, foreign=foreign, other_dep=other_dep, dai=dai,
                contrib=contrib, oth_l=oth_l, cap=cap, res=res)


def steps():
    print("== tab:money-steps (teaching economy)")
    for k, s in STEPS.items():
        quoted(f"step '{k}' balances in every sector", float(balanced(s)), 1, tol=0)
    for k, s in STEPS_BANK.items():
        quoted(f"variant step '{k}' balances", float(balanced(s)), 1, tol=0)
    dm = {k: broad_money(apply(STEPS, [k])) for k in STEPS}
    dh = {k: base_money(apply(STEPS, [k])) for k in STEPS}
    for k, m, h in (("loan", 10, 0), ("tax", -8, -8), ("bond", -8, -8), ("spend", 16, 16), ("qe", 8, 8)):
        quoted(f"  {k}: change in M", dm[k], m, tol=0)
        quoted(f"  {k}: change in H", dh[k], h, tol=0)
    tot = apply(STEPS)
    quoted("total: household deposits", tot[("household", "A", "deposits")], 18, tol=0)
    quoted("total: household bonds", tot[("household", "A", "bonds")], 0, tol=0)
    quoted("total: household net worth", tot[("household", "W", "net worth")], 8, tol=0)
    quoted("total: bank reserves", tot[("bank", "A", "reserves")], 8, tol=0)
    quoted("total: bank loans", tot[("bank", "A", "loans")], 10, tol=0)
    quoted("total: bank deposits", tot[("bank", "L", "deposits")], 18, tol=0)
    quoted("total: central bank bonds", tot[("cb", "A", "bonds")], 8, tol=0)
    quoted("total: TGA", tot[("cb", "L", "tga")], 0, tol=0)
    quoted("total: Treasury bonds outstanding", tot[("treasury", "L", "bonds")], 8, tol=0)
    quoted("total: Treasury net worth (deficit)", tot[("treasury", "W", "net worth")], -8, tol=0)
    quoted("total change in M", broad_money(tot), 18, tol=0)
    quoted("  = loan 10 + deficit (16 - 8) - bonds held by the public (0)", 10 + (16 - 8) - 0, 18, tol=0)
    quoted("total change in H", base_money(tot), 8, tol=0)
    # the bank needs reserves along the way: the lowest cumulative change
    run, low = 0, 0
    for k in STEPS:
        run += apply(STEPS, [k]).get(("bank", "A", "reserves"), 0)
        low = min(low, run)
    quoted("lowest cumulative change in the bank's reserves (after the bond)", low, -16, tol=0)
    print("== ex:money-tax (variant: the bank buys the bond and sells it to the central bank)")
    vb = {k: broad_money(apply(STEPS_BANK, [k])) for k in STEPS_BANK}
    quoted("  bond bought by the bank: change in M", vb["bond"], 0, tol=0)
    quoted("  QE from the bank: change in M", vb["qe"], 0, tol=0)
    quoted("  QE from the bank: change in H", base_money(apply(STEPS_BANK, ["qe"])), 8, tol=0)
    tb = apply(STEPS_BANK)
    quoted("  total change in M", broad_money(tb), 18, tol=0)
    quoted("  total change in H", base_money(tb), 8, tol=0)
    quoted("  household deposits", tb[("household", "A", "deposits")], 18, tol=0)
    no_qe = apply(STEPS, ["loan", "tax", "bond", "spend"])
    quoted("  without step 5: change in M", broad_money(no_qe), 10, tol=0)
    quoted("  without step 5: change in H", base_money(no_qe), 0, tol=0)
    quoted("  without step 5: household bonds", no_qe[("household", "A", "bonds")], 8, tol=0)


def reserves_identity(T):
    print("== deeper box: the reserve identity (eq:money-reserves)")
    r = T["tot"] - T["notes"] - T["rrp"] - T["tga"] - T["foreign"] - T["other_dep"] - T["dai"] - T["contrib"] \
        - T["oth_l"] - T["cap"]
    for k, v in (("tot", 6747560), ("notes", 2434312), ("tga", 885783), ("rrp", 333739), ("cap", 47716)):
        quoted(f"  {k} in the identity ($m)", T[k], v, tol=0)
    quoted("reserves from the identity ($m)", r, 3022066, tol=0)
    quoted("  equals the H.4.1 line", r, T["res"], tol=0)
    quoted("X = foreign official + other deposits + other liabilities ($m)",
           T["foreign"] + T["other_dep"] + T["dai"] + T["contrib"] + T["oth_l"], 23944, tol=0)
    quoted("other liabilities in the table (100m dollars)", (T["dai"] + T["contrib"] + T["oth_l"]) / 100, -2253, tol=0.5)
    quoted("TGA as a share of reserves (%)", 100 * T["tga"] / T["res"], 29.3, tol=0.05)


def settlement(F):
    print("== settlement (Fedwire and NSS): no numbers")


def creation(F, Mn):
    print("== 4.3 ex:money-mult")
    a, b = (Mn.loc[d] for d in MULT_MONTHS)
    quoted("Aug 2008: total reserves ($bn)", a.TOTRESNS, 45.8, tol=0)
    quoted("  C", a.C, 801.8, tol=0.05)
    quoted("  D", a.D, 6956.4, tol=0.05)
    quoted("  c", a.c, 0.1033, tol=0.00005)
    quoted("  r", a.r, 0.00658, tol=0.000005)
    quoted("  m from the ratios", multiplier(a.c, a.r), 9.15, tol=0.005)
    quoted("  m = M/H", a.m, multiplier(a.c, a.r), tol=1e-9)
    quoted("Dec 2008: total reserves ($bn)", b.TOTRESNS, 820.9, tol=0)
    quoted("  C", b.C, 845.5, tol=0.05)
    quoted("  D", b.D, 7398.6, tol=0.05)
    quoted("  c", b.c, 0.1026, tol=0.00005)
    quoted("  r", b.r, 0.1110, tol=0.00005)
    quoted("  m", b.m, 4.95, tol=0.005)
    quoted("r rose by a factor of", b.r / a.r, 16.9, tol=0.05)
    quoted("M2 at the August multiplier ($bn)", a.m * b.BOGMBASE, 15253, tol=0.5)
    quoted("  over the actual M2", a.m * b.BOGMBASE / b.M2NS, 1.85, tol=0.005)
    quoted("check: H/M = c + r(1 - c), August", a.BOGMBASE / a.M2NS, a.c + a.r * (1 - a.c), tol=1e-12)
    pre = Mn.loc[:"2007-12-01", "m"]
    quoted("1959-2007: lowest multiplier", pre.min(), 5.74, tol=0.005)
    quoted("  in (yyyymm)", float(pre.idxmin().strftime("%Y%m")), 195901, tol=0)
    quoted("  highest", pre.max(), 11.71, tol=0.005)
    quoted("  highest in (yyyymm)", float(pre.idxmax().strftime("%Y%m")), 198502, tol=0)
    quoted("lowest multiplier", Mn.m.min(), 2.81, tol=0.005)
    quoted("  in (yyyymm)", float(Mn.m.idxmin().strftime("%Y%m")), 201408, tol=0)
    quoted("  Aug 2014: r", Mn.loc["2014-08-01", "r"], 0.278, tol=0.0005)
    quoted("Aug 2026: c", Mn.loc["2026-08-01", "c"], 0.106, tol=0.0005)
    quoted("  r", Mn.loc["2026-08-01", "r"], 0.141, tol=0.0005)
    print("== 4.3 the contested question")
    rr = F["pbc11_rrr6"]
    quoted("PBoC 2011 H1: RRR raised (times)", rr[0], 6, tol=0)
    quoted("  by (pp each)", rr[1], 0.5, tol=0)
    quoted("  in all (pp)", rr[0] * rr[1], rr[2], tol=1e-12)
    base = F["pbc11_base"]
    quoted("PBoC end-2011 base money (tn yuan)", base[0], 22.5, tol=0)
    quoted("  growth (%)", base[1], 23.2, tol=0)
    quoted("  multiplier", base[2], 3.79, tol=0)
    quoted("  change in the multiplier", -base[3], -0.13, tol=0)
    quoted("  excess reserve ratio (%)", base[4], 2.3, tol=0)
    quoted("PBoC 2025-05: RRR cut (pp)", F["pbc25_rrr"][0], 0.5, tol=0)
    quoted("  long-term liquidity (tn yuan)", F["pbc25_rrr"][1], 1, tol=0)
    quoted("loans / M2 increment 2019 (%)", F["pbc26_loans_m2"][0], 107, tol=0)
    quoted("  2025 (%)", F["pbc26_loans_m2"][1], 63, tol=0)
    quoted("Fed: reserve requirements cut to (%)", F["frr_zero"][0], 0, tol=0)


def china_multiplier(F, P):
    print("== China's multiplier, 2011 and 2026")
    rm11 = P.loc["2011-12", "reserve_money"] / 1e4
    quoted("reserve money end-2011 (tn yuan), the report's base money 22.5", rm11, F["pbc11_base"][0], tol=0.05)
    rm26 = P.loc["2026-06", "reserve_money"] / 1e4
    quoted("M2 / reserve money, June 2026", F["pbc26_m2"][0] / rm26, 8.79, tol=0.005)
    quoted("excess reserve ratio, June 2026 (%)", F["pbc26_excess"][0], 1.3, tol=0)


def rate_section(F, R):
    print("== 4.4 corridor and floor")
    lo, hi = F["fi_range"]
    quoted("target range, September 2026: lower (%)", lo, 3.75, tol=0)
    quoted("  upper (%)", hi, 4.0, tol=0)
    quoted("  statement", F["fo_sep_range"][1], hi, tol=0)
    quoted("IORB from 2026-09-17 (%)", F["fi_iorb"][0], 3.90, tol=0)
    quoted("  in the snapshot", R.loc["2026-09-17", "IORB"], 3.90, tol=0)
    quoted("ON RRP (%)", F["fi_rrp"][0], 3.75, tol=0)
    quoted("  in the snapshot", R.loc["2026-09-17", "RRPONTSYAWARD"], 3.75, tol=0)
    quoted("  per-counterparty limit ($bn)", F["fi_rrp"][1], 160, tol=0)
    quoted("standing repo (%)", F["fi_srf"][0], 4.0, tol=0)
    quoted("primary credit (%)", F["fi_primary"][0], 4.0, tol=0)
    quoted("IORB - ON RRP (bp)", 100 * (F["fi_iorb"][0] - F["fi_rrp"][0]), 15, tol=1e-9)
    quoted("SRF - IORB (bp)", 100 * (F["fi_srf"][0] - F["fi_iorb"][0]), 10, tol=1e-9)
    quoted("IORB - bottom of range (bp)", 100 * (F["fi_iorb"][0] - lo), 15, tol=1e-9)
    s = R.loc["2026-09-17":].dropna(subset=["EFFR"])
    quoted("EFFR, 2026-09-17 to last day: lowest (%)", s.EFFR.min(), 3.88, tol=0)
    quoted("  highest (%)", s.EFFR.max(), 3.88, tol=0)
    quoted("  business days", len(s), 17, tol=0)
    quoted("  last day (yyyymmdd)", float(s.index[-1].strftime("%Y%m%d")), 20261009, tol=0)
    quoted("bills of up to (years)", F["fi_bills"][0], 3, tol=0)
    quoted("December 2025 range: lower (%)", F["fo_dec_range"][0], 3.5, tol=0)
    quoted("  upper (%)", F["fo_dec_range"][1], 3.75, tol=0)
    quoted("  IORB from 2025-12-11 (%)", F["fi_dec_iorb"][0], 3.65, tol=0)
    quoted("  in the snapshot", R.loc["2025-12-11", "IORB"], 3.65, tol=0)
    d = R.dropna(subset=["EFFR", "IOR"])
    quoted("EFFR - IOER, 2009-2014 mean (bp)", d.loc["2009":"2014", "sp_ior"].mean(), -12.0, tol=0.05)
    y = yearly(d.sp_ior)
    quoted("  2014 mean (bp)", y[2014], -16.1, tol=0.05)
    quoted("  2019 mean (bp)", y[2019], 2.4, tol=0.05)
    quoted("  2022-2024 mean of yearly means (bp)", y.loc[2022:2024].mean(), -7.0, tol=0.05)
    quoted("  2026 mean (bp)", y[2026], -1.7, tol=0.05)
    rr = R.dropna(subset=["EFFR", "RRPONTSYAWARD"])
    yr = yearly(rr.sp_rrp)
    quoted("EFFR - ON RRP, 2022-2024 (bp)", yr.loc[2022:2024].mean(), 3.0, tol=0.05)
    quoted("  2026 (bp)", yr[2026], 13.3, tol=0.05)
    quoted("ON RRP began in the snapshot (year)", float(rr.index[0].year), 2013, tol=0)
    print("== ECB 2024")
    quoted("MRO - DFR: new (bp)", F["ecb_spread"][0], 15, tol=0)
    quoted("  old (bp)", F["ecb_spread"][1], 50, tol=0)
    quoted("MLF - MRO (bp)", F["ecb_mlf"][0], 25, tol=0)
    quoted("  MLF - DFR, new (bp)", F["ecb_spread"][0] + F["ecb_mlf"][0], 40, tol=0)
    print("== PBoC")
    pr = F["pbc25_rate"]
    quoted("7-day reverse repo: cut (pp)", pr[0], 0.1, tol=0)
    quoted("  from (%)", pr[1], 1.5, tol=0)
    quoted("  to (%)", pr[2], 1.4, tol=0)
    quoted("  2025: total cut (pp)", F["pbc25_year"][0], pr[0], tol=0)
    b25 = F["pbc25_band"]
    quoted("2025 band: policy rate less (bp)", b25[0], 20, tol=0)
    quoted("  plus (bp)", b25[1], 50, tol=0)
    quoted("  2024 temporary operations the same", F["pbc26_corridor"][0] + F["pbc26_corridor"][1], 70, tol=0)
    b = F["pbc26_band"]
    quoted("June 2026: band less / plus (bp)", b[0], 25, tol=0)
    quoted("  width before (bp)", b[2], b25[0] + b25[1], tol=0)
    quoted("  width after (bp)", b[3], b[0] + b[1], tol=0)
    quoted("  band at the 1.4% policy rate: lower (%)", pr[2] - b[0] / 100, 1.15, tol=1e-9)
    quoted("    upper (%)", pr[2] + b[1] / 100, 1.65, tol=1e-9)
    quoted("  2025 band: lower (%)", pr[2] - b25[0] / 100, 1.20, tol=1e-9)
    quoted("    upper (%)", pr[2] + b25[1] / 100, 1.90, tol=1e-9)
    slf = F["pbc26_slf"]
    quoted("SLF overnight (%)", slf[0], 2.25, tol=0)
    quoted("  7-day (%)", slf[1], 2.40, tol=0)
    quoted("  1-month (%)", slf[2], 2.75, tol=0)
    quoted("  overnight SLF - policy rate (bp)", 100 * (slf[0] - pr[2]), 85, tol=1e-9)
    ex = F["pbc26_excess"]
    quoted("excess reserve ratio, end-June 2026 (%)", ex[0], 1.3, tol=0)
    quoted("DR001 mean, H1 2026 (%)", ex[1], 1.31, tol=0)
    quoted("  below the policy rate by (bp)", 100 * (pr[2] - ex[1]), 9, tol=1e-9)


def ex_floor(F, R):
    print("== ex:money-floor")
    a, n = ARB["amount"], ARB["days"]
    iorb, effr, rrp = F["fi_iorb"][0], 3.88, F["fi_rrp"][0]
    quoted("EFFR 2026-10-07 (%)", R.loc["2026-10-07", "EFFR"], effr, tol=0)
    quoted("(1) bank: IORB - EFFR (bp)", 100 * (iorb - effr), 2, tol=1e-9)
    quoted("    a day, per $1bn ($)", a * (iorb - effr) / 100 / n, 556, tol=0.5)
    quoted("    a year of 360 days ($m)", a * (iorb - effr) / 100 / 1e6, 0.2, tol=1e-9)
    s14 = R.loc["2014"].dropna(subset=["EFFR"]).sp_ior.mean()
    quoted("(2) 2014: the gain a year per $1bn at the mean spread ($m)", -a * s14 / 1e4 / 1e6, 1.6, tol=0.05)
    quoted("(3) money fund: EFFR - ON RRP (bp)", 100 * (effr - rrp), 13, tol=1e-9)


def pbc_case(F, P):
    print("== case box: PBoC 2002-2026")
    quoted("FX share, Dec 2002 (%)", P.loc["2002-12", "fx_sh"], 43.3, tol=0.05)
    quoted("FX share, peak (%)", P.fx_sh.max(), 83.3, tol=0.05)
    quoted("  in (yyyymm)", float(P.fx_sh.idxmax().replace("-", "")), 201403, tol=0)
    s = P.fx_sh.loc["2011-01":"2014-12"]           # legacy section: 'in 2011-2014 about four-fifths'
    quoted("FX share 2011-2014: lowest (%), 'about 80%'", s.min(), 78.6, tol=0.05)
    quoted("  highest (%)", s.max(), 83.3, tol=0.05)
    above80 = P.fx_sh[P.fx_sh > 80]
    quoted("  months above 80%: first (yyyymm)", float(above80.index[0].replace("-", "")), 201102, tol=0)
    quoted("    last (yyyymm)", float(above80.index[-1].replace("-", "")), 201412, tol=0)
    quoted("FX, peak (tn yuan)", P.fx.max() / 1e4, 27.30, tol=0.005)
    quoted("  in (yyyymm)", float(P.fx.idxmax().replace("-", "")), 201405, tol=0)
    quoted("bonds issued (central bank bills), peak (tn yuan)", P.bonds.max() / 1e4, 4.75, tol=0.005)
    quoted("  in (yyyymm)", float(P.bonds.idxmax().replace("-", "")), 201007, tol=0)
    quoted("  end-2011 (tn yuan)", P.loc["2011-12", "bonds"] / 1e4, 2.33, tol=0.005)
    blank = P.bonds.isna()
    quoted("bonds blank: first month (yyyymm)", float(blank[blank].index[0].replace("-", "")), 201706, tol=0)
    quoted("  last month (yyyymm)", float(blank[blank].index[-1].replace("-", "")), 201810, tol=0)
    quoted("  blank months, all consecutive", float(blank.sum()), 17, tol=0)
    bills = F["pbc11_bills"]
    quoted("2011: bills issued (tn yuan)", bills[0], 1.4, tol=0)
    quoted("  bills outstanding end-2011 (tn yuan)", bills[1], 1.9, tol=0)
    quoted("claims on banks, share Dec 2011 (%)", P.loc["2011-12", "claims_banks_sh"], 3.6, tol=0.05)
    quoted("  Dec 2016 (%)", P.loc["2016-12", "claims_banks_sh"], 24.7, tol=0.05)
    quoted("  Aug 2026 (%)", P.loc["2026-08", "claims_banks_sh"], 42.8, tol=0.05)
    quoted("  Aug 2026 (tn yuan)", P.loc["2026-08", "claims_banks"] / 1e4, 21.34, tol=0.005)
    quoted("FX share, Aug 2026 (%)", P.loc["2026-08", "fx_sh"], 43.6, tol=0.05)
    quoted("  FX Aug 2026 (tn yuan)", P.loc["2026-08", "fx"] / 1e4, 21.72, tol=0.005)
    quoted("total assets Aug 2026 (tn yuan)", P.loc["2026-08", "total_assets"] / 1e4, 49.86, tol=0.005)
    quoted("reserve money Aug 2026 (tn yuan)", P.loc["2026-08", "reserve_money"] / 1e4, 40.18, tol=0.005)
    quoted("total assets Dec 2002 (tn yuan)", P.loc["2002-12", "total_assets"] / 1e4, 5.11, tol=0.005)
    quoted("  multiple to Aug 2026", P.loc["2026-08", "total_assets"] / P.loc["2002-12", "total_assets"], 9.8, tol=0.05)
    quoted("bank deposits at the PBoC, Dec 2011 (tn yuan)", P.loc["2011-12", "bank_deposits"] / 1e4, 16.88, tol=0.005)
    quoted("  share of reserve money (%)", 100 * P.loc["2011-12", "bank_deposits"] / P.loc["2011-12", "reserve_money"], 75.1, tol=0.05)
    quoted("assets = liabilities in every month (max gap, 100m yuan)", (P.total_assets - P.total_liab).abs().max(), 0, tol=0.01)
    quoted("months", len(P), 296, tol=0)


def functions(F):
    print("== 4.5 ex:money-smith")
    f = F["sm_forty"]
    quoted("Smith: £", f[0], 100, tol=0)
    quoted("  years", f[1], SMITH["years"], tol=0)
    quoted("  interest (%)", f[2], 100 * SMITH["i"], tol=0)
    quoted("  'little more than £40'", f[3], 40, tol=0)
    pv = SMITH["face"] / (1 + SMITH["i"]) ** SMITH["years"]
    quoted("(1) present value (£)", pv, 41.73, tol=0.005)
    ex = F["sm_exchange"]
    quoted("(3) £100 sterling = £130 currency: one currency pound in sterling (£)", ex[0] / ex[1], 0.77, tol=0.005)
    quoted("    £1100 currency (£)", ex[0] / ex[2], 0.091, tol=0.0005)
    quoted("    ratio of the two values", ex[2] / ex[1], 8.5, tol=0.05)
    quoted("    the £1100 colony's paper relative to the £130 colony's", ex[1] / ex[2], 0.12, tol=0.005)
    quoted("    discount on sterling, 15 years at 6% (pv/face), for comparison", pv / 100, 0.417, tol=0.0005)
    quoted("Knapp: first edition", F["kn_editions"][0], 1905, tol=0)
    quoted("  fourth edition", F["kn_editions"][3], 1923, tol=0)


def test(F, Mn, Wk, R, B):
    print("== 4.6 test 1: the multiplier after 2008 (see creation)")
    print("== 4.6 test 2: September 2019")
    J = weekly_spread(Wk, R)
    j19 = J.loc["2019"]
    quoted("lowest Wednesday reserves in 2019 ($tn)", j19.res.min(), 1.385, tol=0.0005)
    quoted("  on (yyyymmdd)", float(j19.res.idxmin().strftime("%Y%m%d")), 20190918, tol=0)
    quoted("  FEDS Note: 'less than $1.4 trillion'", F["rp_low"][0], 1.4, tol=0)
    quoted("  week's mean EFFR - IOER (bp)", j19.loc["2019-09-18", "sp"], 11.4, tol=0.05)
    quoted("2019 reserves range: low ($tn)", j19.res.min(), 1.39, tol=0.005)
    quoted("  high ($tn)", j19.res.max(), 1.74, tol=0.005)
    quoted("2014 reserves: low ($tn)", J.loc["2014", "res"].min(), 2.25, tol=0.005)
    quoted("  high ($tn)", J.loc["2014", "res"].max(), 2.82, tol=0.005)
    quoted("2026 reserves: low ($tn)", J.loc["2026", "res"].min(), 2.88, tol=0.005)
    quoted("  high ($tn)", J.loc["2026", "res"].max(), 3.18, tol=0.005)
    quoted("2026 weekly spread: lowest (bp)", J.loc["2026", "sp"].min(), -3, tol=1e-9)
    quoted("  highest (bp)", J.loc["2026", "sp"].max(), -1, tol=1e-9)
    k = J.loc["2018":"2019"]
    k = k[(k.res > 1.75) & (k.res <= 1.85)]
    quoted("2018-2019 weeks with reserves in (1.75, 1.85] $tn", len(k), 11, tol=0)
    quoted("  lowest spread (bp)", k.sp.min(), -3, tol=1e-9)
    quoted("  highest spread (bp)", k.sp.max(), 0, tol=1e-9)
    quoted("  mean spread (bp)", k.sp.mean(), -1.0, tol=0.05)
    quoted("2026 low reserves - 1.85 ($tn, 'more than 1tn')", float(J.loc["2026", "res"].min() - 1.85 > 1.0), 1, tol=0)
    quoted("weekly correlation, reserves and spread, 2016-2026", J.loc["2016":].corr().loc["res", "sp"], -0.29, tol=0.005)
    s16, s17 = F["rp_sofr16"], F["rp_sofr17"]
    quoted("SOFR 2019-09-16 (%)", s16[0], 2.43, tol=0)
    quoted("  up (bp)", s16[1], 13, tol=0)
    quoted("EFFR 2019-09-16 (%), FEDS Note", s16[2], 2.25, tol=0)
    quoted("  in the snapshot", R.loc["2019-09-16", "EFFR"], s16[2], tol=0)
    quoted("  top of the range", R.loc["2019-09-16", "DFEDTARU"], 2.25, tol=0)
    quoted("  up (bp)", s16[3], 11, tol=0)
    quoted("  the Friday before, snapshot (%)", R.loc["2019-09-13", "EFFR"], 2.14, tol=0)
    quoted("EFFR 2019-09-17 (%)", s17[0], 2.3, tol=0)
    quoted("  in the snapshot", R.loc["2019-09-17", "EFFR"], s17[0], tol=1e-9)
    quoted("SOFR 2019-09-17 above (%)", s17[1], 5, tol=0)
    quoted("IOER, September 2019 before the 18th (%)", R.loc["2019-09-17", "IOER"], 2.10, tol=0)
    quoted("  EFFR - IOER on the 17th (bp)", R.loc["2019-09-17", "sp_ior"], 20, tol=1e-9)
    quoted("  IOER from 2019-09-19 (%)", R.loc["2019-09-19", "IOER"], 1.80, tol=0)
    quoted("  range from 2019-09-19: upper (%)", R.loc["2019-09-19", "DFEDTARU"], 2.00, tol=0)
    quoted("Treasury settlement ($bn)", F["rp_settle"][0], 54, tol=0)
    quoted("reserves fell over two days by about ($bn)", F["rp_drain"][0], 120, tol=0)
    rp = F["rp_reserves_path"]
    quoted("reserves end-2007 below ($bn)", rp[0], 10, tol=0)
    quoted("  peak Oct 2014 about ($tn)", rp[1], 2.8, tol=0)
    quoted("  snapshot: highest Wednesday level, Oct 2014 ($tn)", Wk.loc["2014-10", "WLODLL"].max() / 1e6, 2.82, tol=0.005)
    quoted("reserves peak ($tn)", Wk.WLODLL.max() / 1e6, 4.27, tol=0.005)
    quoted("  on (yyyymmdd)", float(Wk.WLODLL.idxmax().strftime("%Y%m%d")), 20211215, tol=0)
    quoted("Fed total assets peak ($tn)", Wk.WALCL.max() / 1e6, 8.97, tol=0.005)
    quoted("  on (yyyymmdd)", float(Wk.WALCL.idxmax().strftime("%Y%m%d")), 20220413, tol=0)
    quoted("reverse repos peak ($tn)", Wk.WLRRAL.max() / 1e6, 2.68, tol=0.005)
    quoted("  on (yyyymmdd)", float(Wk.WLRRAL.idxmax().strftime("%Y%m%d")), 20230412, tol=0)
    print("== 4.6 test 3: Peru")
    p, d = B.cpi_12m_pct.dropna(), B.dollarization_pct.dropna()
    quoted("inflation peak (% over 12 months)", p.max(), 12377, tol=0.5)
    quoted("  in (yyyymm)", float(p.idxmax().replace("-", "")), 199008, tol=0)
    quoted("Dec 1990 (%)", p["1990-12"], 7650, tol=0.5)
    quoted("Dec 1991 (%)", p["1991-12"], 139.2, tol=0.05)
    quoted("first month below 10% after 1991 (yyyymm)", float(p.loc["1992":][p.loc["1992":] < 10].index[0].replace("-", "")), 199702, tol=0)
    quoted("dollarization Jan 1992 (%)", d["1992-01"], 59.4, tol=0)
    quoted("  Dec 1998 (%)", d["1998-12"], 70.1, tol=0.05)
    quoted("  peak (%)", d.max(), 73.2, tol=0.05)
    quoted("  in (yyyymm)", float(d.idxmax().replace("-", "")), 200005, tol=0)
    quoted("  inflation that month (%)", p["2000-05"], 3.3, tol=0.05)
    quoted("  inflation Dec 1999 (%)", p["1999-12"], 3.7, tol=0.05)
    quoted("  Sept 2002, the decree's month (%)", d["2002-09"], 67.6, tol=0.05)
    quoted("  Dec 2010 (%)", d["2010-12"], 37.6, tol=0.05)
    quoted("  Dec 2013 (%)", d["2013-12"], 32.9, tol=0)
    quoted("  Dec 2015 (%)", d["2015-12"], 37.4, tol=0.05)
    quoted("  lowest (%)", d.min(), 25.4, tol=0.05)
    quoted("  in (yyyymm)", float(d.idxmin().replace("-", "")), 202512, tol=0)
    quoted("  Aug 2026, the last month (%)", d["2026-08"], 26.0, tol=0.05)
    quoted("  last month (yyyymm)", float(d.index[-1].replace("-", "")), 202608, tol=0)
    s = d.loc["1992-01":"2001-12"]
    quoted("dollarization 1992-2001: lowest (%)", s.min(), 55.1, tol=0.05)
    quoted("  highest (%)", s.max(), 73.2, tol=0.05)
    quoted("  above one half in every month", float((s > 50).all()), 1, tol=0)
    quoted("inflation highest since 2001 (%)", p.loc["2001":].max(), 8.8, tol=0.05)
    quoted("  in (yyyymm)", float(p.loc["2001":].idxmax().replace("-", "")), 202206, tol=0)
    quoted("inflation 1997-2026 months above 10%", float((p.loc["1997-02":] > 10).sum()), 0, tol=0)
    lim = F["bis_limits"]
    quoted("BIS: growth limits (%)", lim[0], 10, tol=0)
    quoted("  ... (%)", lim[2], 20, tol=0)
    quoted("  additional requirements up to (%)", lim[5], 5, tol=0)
    quoted("  reduce to at least (% of Sept 2013)", F["bis_reduce"][0], 95, tol=0)
    print("== 4.6 test 4: the cost of a floor")
    res, iorb = F["h4_deposits"][1], F["fi_iorb"][0]
    quoted("interest on reserves at 3.90% a year ($bn)", res * iorb / 100 / 1e3, 117.9, tol=0.05)
    quoted("deferred asset ($bn)", -F["h4_remit"][0] / 1e3, 233.6, tol=0.05)
    quoted("  in 100m dollars", F["h4_remit"][0] / 100, -2335.87, tol=0)
    quoted("  over capital", -F["h4_remit"][0] / F["h4_capital"][0], 4.9, tol=0.05)


def selfcheck(F):
    print("== self-check answers")
    quoted("(1) repayment of 4: change in M", -4, -4, tol=0)
    quoted("(2) m at c = 0.1, r = 0.02", multiplier(0.1, 0.02), 8.47, tol=0.005)
    quoted("    m at c = 0.1, r = 0.2", multiplier(0.1, 0.2), 3.57, tol=0.005)
    quoted("    M with H = 100 (first case)", 100 * multiplier(0.1, 0.02), 847, tol=0.5)
    quoted("    H needed for the same M in the second case", 100 * multiplier(0.1, 0.02) / multiplier(0.1, 0.2), 237, tol=0.5)
    quoted("(3) tax payments of 1000 (100m dollars) into the TGA: reserves", -1000, -1000, tol=0)
    quoted("(4) corridor: market rate at the target (%)", (2.0 + 2.5) / 2, 2.25, tol=1e-9)
    quoted("    floor: at the deposit rate (%)", 2.0, 2.0, tol=0)
    quoted("    after +0.25: corridor (%)", (2.0 + 2.5) / 2 + 0.25, 2.50, tol=1e-9)
    quoted("    after +0.25: floor (%)", 2.0 + 0.25, 2.25, tol=1e-9)
    quoted("(5) £100 in 10 years at 5%", 100 / 1.05 ** 10, 61.39, tol=0.005)
    quoted("    accepted for a tax due now: worth", 100, 100, tol=0)


def main():
    F = facts()
    Wk, Mn, R, P, B = fed(), money(), rates(), pbc(), peru()
    opening(Mn)
    world(F, Wk, R)
    sheets(F, Mn, P)
    T = fed_table(F)
    steps()
    settlement(F)
    reserves_identity(T)
    creation(F, Mn)
    china_multiplier(F, P)
    rate_section(F, R)
    ex_floor(F, R)
    pbc_case(F, P)
    functions(F)
    test(F, Mn, Wk, R, B)
    selfcheck(F)
    print("all Chapter 4 checks passed")


if __name__ == "__main__":
    main()
