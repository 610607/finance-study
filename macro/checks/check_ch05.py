"""Chapter 5 (国际收支与汇率): every number quoted in zh/ch05_external.tex.

    python3 checks/check_ch05.py

Inputs are eight snapshots:
  external_facts      quotations from the Central Bank of Sri Lanka (Annual Report 2022, chapter 5), Sri Lanka's
                      Ministry of Finance (FAQ on the debt standstill, April 2022), BEA (the concepts manual and the
                      release of 24 September 2026 with its history table), SAFE (the 2016 balance-of-payments
                      report), Du, Tepper & Verdelhan (2017/2018), Engel (2013/2014), Taylor & Taylor (2004),
                      Eichengreen & Hausmann (1999), Aizenman & Lee (2005/2007), Dooley, Folkerts-Landau & Garber
                      (2003), Obstfeld, Shambaugh & Taylor (2008/2010) and the terms of use of BIS, CBSL and SAFE;
                      checked by data/fetch/verify_web_quotes.py
  cbsl_reserves       Sri Lanka's official reserve assets, monthly (CBSL reserve data template)
  bis_fx              LKR and CNY per US dollar; China's nominal and real effective exchange rates (BIS)
  wb_external_annual  current account, capital account, financial account, reserve transactions, reserves and GDP
                      of China, Sri Lanka and the United States, 1982-2025 (World Bank WDI)
  fred_us_external    US current account, primary income and international investment position (BEA via FRED)
  wb_price_levels     PPP conversion factor, exchange rate and GDP per capita of 193 economies in 2021 (WDI)
  wb_relppp           consumer prices and exchange rates of 160 economies in 2001, 2020 and 2021 (WDI)
  pbc_balance_sheet   the balance sheet of the People's Bank of China (for the share of foreign exchange, Ch 4)
The figure module figsrc/fig_ch05.py imports the functions defined here.

Notation (Appendix B; foreign variables carry a superscript f because r* is the neutral rate):
    balance of payments  CA + KA + EO = FA = dA - dL       FA: net lending, BPM6 sign  (eq:external-bop)
    sector balances      (S - I) + (T - G) + (-CA) = 0                                   (eq:external-sectors)
    position             dNIIP = FA + price, exchange-rate and other changes             (eq:external-iip)
    real exchange rate   q = e P^f / P                                                   (eq:external-real)
    PPP                  e = P / P^f (absolute), dln e = pi - pi^f (relative)            (eq:external-ppp)
    covered parity       F / e = (1 + i) / (1 + i^f)                                     (eq:external-cip)
    uncovered parity     E_t e_{t+1} / e_t = (1 + i) / (1 + i^f)                         (eq:external-uip)
e is domestic currency per unit of foreign currency (a rise is a depreciation). In the WDI panel fa is net lending
including reserves and res_bop the reserve transaction (positive when reserves rise); the non-reserve financial
account is fa - res_bop and net errors and omissions are fa - ca - ka. SAFE prints the financial account with the
opposite sign (credit positive, debit negative; the four items add up to zero).
The four transactions of ex:external-entries, the forward example ex:external-cip and the self-check are teaching
inputs, defined below and stated in the text.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import stats

from common import load_snapshot, quoted

# ---------------------------------------------------------------------------------------------------
# Teaching inputs stated in the text
# ex:external-entries: (account, item, amount), BPM6 signs: CA credits positive; FA asset and liability changes
ENTRIES = {
    "a": [("ca", "exports", 100), ("asset", "exporter deposit abroad", 100)],
    "b": [("ca", "imports", -150), ("asset", "reserves", -150)],
    "c": [("ca", "secondary income", 30), ("asset", "bank deposit abroad", 30)],
    "d": [("liability", "government bond", 80), ("asset", "reserves", 80)],
}
ENTRIES_CB_RESERVES = 100            # question (3): the bond is not sold; the central bank holds 100
# ex:external-cip
CIP = dict(e=7.10, i=0.015, i_f=0.040, quote=7.00, usd=100.0)   # usd in 10,000 dollars (100 万美元)
# the self-check
SC = dict(export=50, ca=-20, nrfa=-50, nrfa2=-10, e0=6.40, e1=7.20, de=0.10, pi=0.08, pi_f=0.02,
          spot=150.0, i_jpy=0.005, i_usd=0.045, private=2.0, gov=-6.0, up=0.20)

# PPP tests: the WDI country notes decide which economies are left out (see data/fetch/wb_external.py)
PL_YEAR = 2021
REL_YEARS = (2001, 2020, 2021)


# ---------------------------------------------------------------------------------------------------
# Loaders
def facts() -> dict[str, list[float]]:
    """id -> the numbers of the value column (several are separated by ';')."""
    df, _ = load_snapshot("external_facts", dtype={"value": str})
    out = {}
    for _, r in df.iterrows():
        v = r["value"]
        if isinstance(v, str) and v.strip():
            out[r["id"]] = [float(x) for x in v.split(";")]
    return out


def lk_reserves() -> pd.DataFrame:
    df, _ = load_snapshot("cbsl_reserves")
    return df.set_index("month")


def bis() -> pd.DataFrame:
    df, _ = load_snapshot("bis_fx")
    return df.set_index("month")


def wdi() -> pd.DataFrame:
    """WDI panel in US$ billion, indexed by (country, year), with eo, nrfa and ca_gdp (%)."""
    df, _ = load_snapshot("wb_external_annual")
    df = df.set_index(["country", "year"])
    for k in ("reserves", "ca", "fa", "res_bop", "gdp", "ka"):
        df[k] = df[k] / 1e9
    df["eo"] = df.fa - df.ca - df.ka
    df["nrfa"] = df.fa - df.res_bop
    df["ca_gdp"] = 100 * df.ca / df.gdp
    return df


def us_external() -> pd.DataFrame:
    """BEA via FRED, US$ billion (positions in trillions are /1000)."""
    df, _ = load_snapshot("fred_us_external")
    df = df.set_index("date")
    return df / 1000.0


def primary_income_annual(U: pd.DataFrame) -> pd.Series:
    """Quarterly primary income balances summed to calendar years (complete years only), US$ billion."""
    s = U.IEABCPI.dropna()
    yr = s.index.str[:4].astype(int)
    g = s.groupby(yr)
    return g.sum()[g.count() == 4]


def pbc() -> pd.DataFrame:
    df, _ = load_snapshot("pbc_balance_sheet")
    df = df.set_index("month")
    df["fx_sh"] = 100 * df.fx / df.total_assets
    return df


def _bad(flag: str, years, euro_after: int | None = None, other_unit: bool = True) -> bool:
    """True when a WDI flag says the official exchange rate is not comparable in one of `years`."""
    for f in str(flag).split(";"):
        if f.startswith("dual_rate:"):
            spans = f.split(":", 1)[1]
            if spans == "unspecified":
                return True
            for s in spans.split(","):
                a, b = (int(x) for x in s.split("-"))
                if any(a <= y <= b for y in years):
                    return True
        if f.startswith("euro:"):
            y = int(f[5:])
            if euro_after is None and y > max(years):        # national series restated in euros, fx not yet
                return True
            if euro_after is not None and euro_after < y <= max(years):   # fx changes unit within the span
                return True
        if f == "other_unit" and other_unit:
            return True
    return False


def price_levels() -> tuple[pd.DataFrame, pd.DataFrame]:
    """(kept, excluded) economies of the 2021 price-level test. Kept rows carry x = ln(gdppc_ppp/US) and
    y = ln(price level)."""
    df, _ = load_snapshot("wb_price_levels", keep_default_na=False)
    bad = df.flag.apply(lambda f: _bad(f, [PL_YEAR]))
    kept, out = df[~bad].copy(), df[bad].copy()
    us = kept[kept.iso3 == "USA"].iloc[0]
    kept["x"] = np.log(kept.gdppc_ppp.astype(float) / float(us.gdppc_ppp))
    kept["y"] = np.log(kept.price_level.astype(float))
    return kept, out


def relppp() -> tuple[pd.DataFrame, pd.DataFrame]:
    """(kept, excluded) economies of the relative-PPP test, without the United States. Kept rows carry the log
    change of the CPI relative to the US (dx_a_b) and of the exchange rate (dy_a_b) for 2001-2021 and 2020-2021.
    A unit change of the national accounts (other_unit) does not affect a CPI index or the exchange rate, so only
    multiple rates and euro adoption within the span exclude an economy."""
    df, _ = load_snapshot("wb_relppp", keep_default_na=False)
    bad = df.flag.apply(lambda f: _bad(f, list(REL_YEARS), euro_after=REL_YEARS[0], other_unit=False))
    us = df[df.iso3 == "USA"].iloc[0]
    kept, out = df[~bad & (df.iso3 != "USA")].copy(), df[bad].copy()
    for a, b in ((2001, 2021), (2020, 2021)):
        us_ratio = float(us[f"cpi_{b}"]) / float(us[f"cpi_{a}"])
        kept[f"dx_{a}_{b}"] = np.log(kept[f"cpi_{b}"].astype(float) / kept[f"cpi_{a}"].astype(float) / us_ratio)
        kept[f"dy_{a}_{b}"] = np.log(kept[f"fx_{b}"].astype(float) / kept[f"fx_{a}"].astype(float))
    return kept, out


def regress(x, y):
    return stats.linregress(np.asarray(x, float), np.asarray(y, float))


def year_avg(series: pd.Series, year: int) -> float:
    return float(series[series.index.str.startswith(str(year))].mean())


# ---------------------------------------------------------------------------------------------------
# Balance-of-payments helpers
def entries_accounts(entries: dict) -> dict:
    ca = sum(v for t in entries.values() for a, _, v in t if a == "ca")
    dA = sum(v for t in entries.values() for a, _, v in t if a == "asset")
    dL = sum(v for t in entries.values() for a, _, v in t if a == "liability")
    res = sum(v for t in entries.values() for a, k, v in t if a == "asset" and k == "reserves")
    return dict(ca=ca, dA=dA, dL=dL, fa=dA - dL, reserves=res)


def cip_forward(e: float, i: float, i_f: float) -> float:
    return e * (1 + i) / (1 + i_f)


# ---------------------------------------------------------------------------------------------------
def opening(F, W, U):
    print("== opening")
    quoted("standstill: payments after 5.00 pm on 12 April 2022", F["lk_faq_capitalized"][0], 5.00)
    quoted("    day", F["lk_faq_capitalized"][1], 12)
    quoted("GOR end-2022 (亿美元)", F["lk_gor_decl"][0] / 100, 18.98, tol=0.005)
    quoted("PBoC swap end-2022 (亿美元)", F["lk_swap_val2"][1] / 100, 14.33, tol=0.005)
    us22 = W.loc[("USA", 2022)]
    quoted("US current account 2022 (亿美元)", us22.ca * 10, -9724, tol=0.5)
    quoted("Sri Lanka current account 2022 (亿美元)", F["lk_t51_ca"][1] / 100, -14.53, tol=0.005)
    quoted("    ratio US / Sri Lanka", us22.ca / (F["lk_t51_ca"][1] / 1000), 669, tol=0.5)
    quoted("US NIIP end-2022 (万亿美元)", U.loc["2022-10-01", "IIPUSNETIQ"] / 1000, -14.23, tol=0.005)
    us = W.loc["USA"].loc[1982:2025]
    surplus = list(us.index[us.ca > 0])
    assert surplus == [1991], surplus
    quoted("US deficits since 1982: years 1982-2025 with a surplus", len(surplus), 1)
    quoted("    'forty-odd years' of deficits (2025 - 1982)", 2025 - 1982, 43)


def world(F, LR, B, W, U):
    print("== sec:external-world")
    for y, v, t in zip(range(2018, 2023), F["lk_t512_gor"], [69.19, 76.42, 56.64, 31.39, 18.98]):
        quoted(f"GOR end-{y} (亿美元)", v / 100, t, tol=0.005)
    quoted("official reserve assets Nov 2021 (亿美元)", LR.loc["2021-11", "official_reserve_assets"] / 100, 15.88,
           tol=0.005)
    quoted("gold Jan 2020 (亿美元)", LR.loc["2020-01", "gold"] / 100, 9.36, tol=0.005)
    quoted("gold Apr 2022 (亿美元)", LR.loc["2022-04", "gold"] / 100, 0.29, tol=0.005)
    quoted("swap end-2021 (亿美元)", F["lk_swap_val2"][0] / 100, 15.74, tol=0.005)
    usable21 = (F["lk_t512_gor"][3] - F["lk_swap_val2"][0]) / 100
    usable22 = (F["lk_t512_gor"][4] - F["lk_swap_val2"][1]) / 100
    quoted("usable reserves end-2021 (亿美元)", usable21, 15.65, tol=0.005)
    quoted("usable reserves end-2022 (亿美元)", usable22, 4.65, tol=0.005)
    quoted("import cover end-2021 (months)", F["lk_t512_months"][3], 1.8)
    quoted("import cover end-2022 (months)", F["lk_t512_months"][4], 1.2)
    quoted("    annual report, end-2022", F["lk_gor_months"][0], 1.2)
    # fig ext_srilanka
    win = LR.loc["2018-01":"2026-07", "official_reserve_assets"]
    quoted("figure: minimum of the window, Nov 2021 (亿美元)", win.min() / 100, 15.88, tol=0.005)
    assert win.idxmin() == "2021-11"
    y22 = LR.loc["2022-01":"2022-12", "official_reserve_assets"]
    assert y22.idxmin() == "2022-10"
    quoted("figure: minimum of 2022, Oct 2022 (亿美元)", y22.min() / 100, 17.05, tol=0.005)
    amt = LR.pboc_swap_bn.dropna()
    assert (amt.index[0], amt.index[-1]) == ("2022-03", "2024-02"), (amt.index[0], amt.index[-1])
    assert LR.loc["2022-03":, "pboc_swap_note"].eq(1).all()
    # the exchange rate
    quoted("BIS LKR/USD end-Feb 2022", B.loc["2022-02", "lkr_usd_eop"], 201.00, tol=0.005)
    quoted("BIS LKR/USD end-Apr 2022", B.loc["2022-04", "lkr_usd_eop"], 345.27, tol=0.005)
    quoted("depreciation by end-April 2022 (%)", F["lk_dep_april"][0], 41.4)
    quoted("depreciation in 2022 (%)", F["lk_dep_year"][0], 44.8)
    quoted("    Table 5.15, change in 2022 (%)", -F["lk_t515_usd"][7], 44.80, tol=1e-9)
    quoted("LKR/USD end-2021", F["lk_t515_usd"][1], 200.43)
    quoted("LKR/USD end-2022", F["lk_t515_usd"][2], 363.11)
    quoted("official reserve assets end-2023 (亿美元)", LR.loc["2023-12", "official_reserve_assets"] / 100, 43.92,
           tol=0.005)
    quoted("official reserve assets end-July 2026 (亿美元)", LR.loc["2026-07", "official_reserve_assets"] / 100, 66.00,
           tol=0.005)
    quoted("    months of imports", LR.loc["2026-07", "gor_months"], 3.2)
    assert LR.index[-1] == "2026-07"
    assert LR.loc["2026-07", "pboc_swap_note"] == 1          # 'still includes the swap subject to conditions'
    # the United States
    quoted("US CA deficit widened by (US$ bn)", F["bea_ca"][0], 33.4)
    quoted("    (亿美元)", F["bea_ca"][0] * 10, 334, tol=1e-9)
    quoted("    by (%)", F["bea_ca"][1], 15.7)
    quoted("    to (亿美元)", F["bea_ca"][2] * 10, 2460, tol=1e-9)
    quoted("    history table (亿美元)", F["beah_ca"][0] * 10, 2460, tol=0.5)
    quoted("    share of GDP (%)", F["bea_ca_gdp"][0], 3.0)
    quoted("net financial-account transactions (亿美元)", F["bea_fa"][0] * 10, -3697, tol=1e-9)
    us = W.loc["USA"].loc[1982:2025]
    quoted("largest US deficit since 1982, 2006 (% of GDP)", us.ca_gdp.min(), -5.8, tol=0.05)
    assert us.ca_gdp.idxmin() == 2006
    quoted("US assets end-Q2 2026 (万亿美元)", F["bea_al"][0], 46.97)
    quoted("    FRED", U.loc["2026-04-01", "IIPUSASSQ"] / 1000, 46.97, tol=0.005)
    quoted("US liabilities end-Q2 2026 (万亿美元)", F["bea_al"][1], 69.39)
    quoted("    FRED", U.loc["2026-04-01", "IIPUSLIAQ"] / 1000, 69.39, tol=0.005)
    quoted("US NIIP end-Q2 2026 (万亿美元)", F["bea_niip"][0], -22.42)
    quoted("    FRED", U.loc["2026-04-01", "IIPUSNETIQ"] / 1000, -22.42, tol=0.005)


def lk_table(F):
    """tab:external-srilanka and the text around it (亿美元)."""
    print("== sec:external-bop: tab:external-srilanka")
    rows = {"lk_t51_ca": (-32.84, -14.53), "lk_t51_trade": (-81.39, -51.85), "lk_t51_exports": (124.99, 131.06),
            "lk_t51_imports": (206.37, 182.91), "lk_t51_services": (15.86, 21.10),
            "lk_t51_primary": (-19.59, -18.74), "lk_t51_secondary": (52.28, 34.96),
            "lk_t51_remit": (54.91, 37.89), "lk_t51_ka": (0.25, 0.19), "lk_t51_fa": (-42.11, -19.46),
            "lk_t51_di_a": (0.17, 0.15), "lk_t51_di_l": (5.92, 8.98), "lk_t51_pi_l": (-15.47, 3.55),
            "lk_t51_oi_a": (3.87, 13.02), "lk_t51_oi_l": (30.53, 7.76), "lk_t51_res": (-25.17, -12.34),
            "lk_t51_eo": (-9.52, -5.13)}
    for k, (a, b) in rows.items():
        quoted(f"{k} 2021", F[k][0] / 100, a, tol=0.005)
        quoted(f"{k} 2022", F[k][1] / 100, b, tol=0.005)
    assert "lk_t51_pi_a" not in F and "lk_t51_deriv" not in F         # printed as '-'
    v = {k: [x / 100 for x in F[k][:2]] for k in rows}
    for j, y in enumerate((2021, 2022)):
        ca = v["lk_t51_trade"][j] + v["lk_t51_services"][j] + v["lk_t51_primary"][j] + v["lk_t51_secondary"][j]
        quoted(f"    CA = goods + services + primary + secondary, {y}", ca, v["lk_t51_ca"][j], tol=0.011)
        fa = (v["lk_t51_di_a"][j] - v["lk_t51_di_l"][j] - v["lk_t51_pi_l"][j] + v["lk_t51_oi_a"][j]
              - v["lk_t51_oi_l"][j] + v["lk_t51_res"][j])
        quoted(f"    FA = assets - liabilities, {y}", fa, v["lk_t51_fa"][j], tol=0.011)
    lhs = v["lk_t51_ca"][1] + v["lk_t51_ka"][1] + v["lk_t51_eo"][1]
    quoted("CA + KA + EO 2022", lhs, -19.47, tol=0.005)
    quoted("    difference from FA (rounding)", lhs - v["lk_t51_fa"][1], -0.01, tol=0.0005)
    quoted("    2021: CA + KA + EO = FA", v["lk_t51_ca"][0] + v["lk_t51_ka"][0] + v["lk_t51_eo"][0],
           v["lk_t51_fa"][0], tol=0.0005)
    di = v["lk_t51_di_a"][1] - v["lk_t51_di_l"][1]
    oi = v["lk_t51_oi_a"][1] - v["lk_t51_oi_l"][1]
    quoted("direct investment 2022", di, -8.83, tol=0.005)
    quoted("portfolio investment 2022", 0 - v["lk_t51_pi_l"][1], -3.55, tol=0.005)
    quoted("other investment 2022", oi, 5.26, tol=0.005)
    quoted("non-reserve financial account 2022", di - v["lk_t51_pi_l"][1] + oi, -7.12, tol=0.005)
    quoted("fall in GOR 2022", (F["lk_t512_gor"][3] - F["lk_t512_gor"][4]) / 100, 12.41, tol=0.005)


def entries():
    print("== ex:external-entries")
    a = entries_accounts(ENTRIES)
    quoted("(1) CA", a["ca"], -20)
    quoted("    net acquisition of assets", a["dA"], 60)
    quoted("    net incurrence of liabilities", a["dL"], 80)
    quoted("    FA", a["fa"], -20)
    quoted("(2) reserves", a["reserves"], -70)
    quoted("    deposits added abroad by the exporter and the bank", 100 + 30, 130)
    quoted("    foreign exchange needed (deficit + deposits)", -a["ca"] + 130, 150)
    # (3): no bond; the central bank sells at most 100; imports compressed to 100
    quoted("(3) left uncovered", 150 - ENTRIES_CB_RESERVES, 50)
    e3 = {"a": ENTRIES["a"], "b": [("ca", "imports", -100), ("asset", "reserves", -100)], "c": ENTRIES["c"]}
    b = entries_accounts(e3)
    quoted("    CA with imports of 100", b["ca"], 30)
    quoted("    FA with imports of 100", b["fa"], 30)


def compare_ca(F, W):
    print("== compare: current vs financial account")
    quoted("Sri Lanka CA 2022 (% of GDP)", -F["lk_t51_ca"][1] / 1000 / W.loc[("LKA", 2022)].gdp * 100, 2.0,
           tol=0.05)


def safe_signs(F):
    print("== SAFE sign convention")
    quoted("BPM7 published (2025 SNA, para. 1.70)", F["sna_bpm7"][0], 2025)
    ca, ka = F["safe_t_ca"][0], F["safe_t_ka"][0]
    fa, fa_a, fa_l = F["safe_t_fa"]
    eo = F["safe_t_eo"][0]
    quoted("CA", ca, 1964)
    quoted("KA", ka, -3)
    quoted("FA, assets, liabilities", fa, 267)
    quoted("    assets", fa_a, -2174)
    quoted("    liabilities", fa_l, 2441)
    quoted("    FA = assets + liabilities", fa_a + fa_l, fa, tol=0)
    quoted("EO", eo, -2227)
    quoted("sum of the four items (rounding)", ca + ka + fa + eo, 1)
    quoted("FA in the BPM6 net-lending sign", -fa_a - fa_l, -267)
    quoted("    CA + KA + EO", ca + ka + eo, -266)
    quoted("non-reserve FA (SAFE sign)", F["safe_t_nrfa"][0], -4170)
    quoted("    BPM6 sign", -F["safe_t_nrfa"][0], 4170)
    quoted("    = net reserve-free FA in the text", F["safe_nrfa"][1], 4170)
    quoted("    net acquisition of non-reserve assets (BPM6 sign)", -F["safe_t_nrfa"][1], 6611)
    quoted("    net incurrence of liabilities", F["safe_t_nrfa"][2], 2441)
    quoted("    assets - liabilities", -F["safe_t_nrfa"][1] - F["safe_t_nrfa"][2], 4170)
    quoted("reserve assets (SAFE sign; a fall)", F["safe_t_res"][0], 4437)
    quoted("    text", F["safe_res_tx"][1], 4437)
    quoted("    FA = non-reserve + reserves (SAFE sign)", F["safe_t_nrfa"][0] + F["safe_t_res"][0], 267)


def pitfall(F):
    print("== pitfall")
    quoted("reserve assets 2022 (亿美元)", F["lk_t51_res"][1] / 100, -12.34, tol=0.005)
    quoted("imports 2021 (亿美元)", F["lk_t51_imports"][0] / 100, 206.37, tol=0.005)
    quoted("imports 2022 (亿美元)", F["lk_t51_imports"][1] / 100, 182.91, tol=0.005)
    quoted("    change (%)", 100 * (F["lk_t51_imports"][1] / F["lk_t51_imports"][0] - 1), -11.4, tol=0.05)
    quoted("rice imports 2022 over 2021 (%, 'about')", F["lk_rice"][0], 300)
    quoted("overall balance 2022 (亿美元)", F["lk_t512_ob"][4] / 100, -28.06, tol=0.005)
    quoted("    Table 5.1", F["lk_t51_ob"][1] / 100, -28.06, tol=0.005)
    quoted("    = change in NIR", (F["lk_t512_nir"][4] - F["lk_t512_nir"][3]) / 100, -28.06, tol=0.005)
    quoted("reserve-related liabilities end-2021 (亿美元)", F["lk_t512_rrl"][3] / 100, 35.62, tol=0.005)
    quoted("    end-2022", F["lk_t512_rrl"][4] / 100, 51.27, tol=0.005)
    d_gor = F["lk_t512_gor"][4] - F["lk_t512_gor"][3]
    d_nir = F["lk_t512_nir"][4] - F["lk_t512_nir"][3]
    share = d_gor / d_nir
    quoted("    fall in GOR / fall in NIR (less than half)", share, 0.44, tol=0.005)
    assert share < 0.5


def sectors(W):
    print("== eq:external-sectors")
    us, cn = W.loc[("USA", 2025)], W.loc[("CHN", 2025)]
    quoted("US CA 2025 (亿美元)", us.ca * 10, -11771, tol=0.5)
    quoted("    % of GDP", us.ca_gdp, -3.8, tol=0.05)
    quoted("China CA 2025 (亿美元)", cn.ca * 10, 7350, tol=0.5)
    quoted("    % of GDP", cn.ca_gdp, 3.8, tol=0.05)


def ex_us(F, U):
    print("== ex:external-us")
    quoted("assets up (万亿美元)", F["bea_assets_up"][0], 3.72)
    quoted("    price changes", F["bea_assets_why"][0], 3.03)
    quoted("    transactions (亿美元)", F["bea_assets_why"][1] * 10, 6633, tol=1e-9)
    quoted("liabilities up", F["bea_liab_up"][0], 4.87)
    quoted("    price changes", F["bea_liab_why"][0], 3.95)
    quoted("    transactions (亿美元)", F["bea_liab_why"][1] * 10, 9789, tol=1e-9)
    quoted("derivatives (亿美元)", F["beah_tx_d"][0] * 10, -541, tol=0.5)
    quoted("NIIP end-Q1 2026", F["bea_niip_q1"][0], -21.27)
    quoted("NIIP end-Q2 2026", F["bea_niip"][0], -22.42)
    d = F["bea_niip"][0] - F["bea_niip_q1"][0]
    quoted("(1) change", d, -1.15, tol=0.005)
    quoted("    assets transactions (万亿美元)", F["beah_tx_a"][0] / 1000, 0.6633, tol=0.00005)
    quoted("    liabilities transactions", F["beah_tx_l"][0] / 1000, 0.9789, tol=0.00005)
    quoted("    derivatives", F["beah_tx_d"][0] / 1000, -0.05, tol=0.005)
    tx = (F["beah_tx_a"][0] - F["beah_tx_l"][0]) / 1000
    quoted("    transactions excluding derivatives (万亿美元)", tx, -0.32, tol=0.005)
    quoted("    plus derivatives = FA (亿美元)", (tx + F["beah_tx_d"][0] / 1000) * 1e4, -3697, tol=0.5)
    quoted("    = the release", F["bea_fa"][0] * 10, -3697, tol=1e-9)
    price = F["bea_assets_why"][0] - F["bea_liab_why"][0]
    quoted("    price changes", price, -0.92, tol=1e-9)
    # the remainder as the student computes it, from the rounded numbers in the example
    rest = round(d, 2) - round(tx, 2) - round(price, 2)
    quoted("    remainder (exchange rates, other, derivatives), -1.15 + 0.32 + 0.92", rest, 0.09, tol=1e-9)
    d_exact = (U.loc["2026-04-01", "IIPUSNETIQ"] - U.loc["2026-01-01", "IIPUSNETIQ"]) / 1000   # US$ bn -> 万亿
    print(f"    (from the unrounded positions the remainder is {d_exact - tx - price:.3f}; BEA rounds the price changes)")
    quoted("(2) FA (万亿美元)", F["bea_fa"][0] / 1000, -0.37, tol=0.005)
    quoted("    price changes / change in NIIP", price / d, 0.80, tol=0.01)
    # cross-check against the FRED positions
    quoted("    FRED: change in NIIP", (U.loc["2026-04-01", "IIPUSNETIQ"] - U.loc["2026-01-01", "IIPUSNETIQ"]) / 1000,
           -1.15, tol=0.005)
    quoted("    FRED: change in assets", (U.loc["2026-04-01", "IIPUSASSQ"] - U.loc["2026-01-01", "IIPUSASSQ"]) / 1000,
           3.72, tol=0.005)
    quoted("    FRED: change in liabilities",
           (U.loc["2026-04-01", "IIPUSLIAQ"] - U.loc["2026-01-01", "IIPUSLIAQ"]) / 1000, 4.87, tol=0.005)


def position(F, U, W):
    print("== sec:external-position: valuation and income")
    quoted("Sri Lanka external debt end-2021 (亿美元)", F["lk_extdebt"][1] / 100, 517.75, tol=0.005)
    quoted("    end-2022", F["lk_extdebt"][0] / 100, 496.78, tol=0.005)
    quoted("US NIIP end-2006 (万亿美元)", U.loc["2006-10-01", "IIPUSNETIQ"] / 1000, -1.81, tol=0.005)
    quoted("US NIIP end-2025", U.loc["2025-10-01", "IIPUSNETIQ"] / 1000, -21.87, tol=0.005)
    quoted("    % of 2025 GDP", -100 * U.loc["2025-10-01", "IIPUSNETIQ"] / W.loc[("USA", 2025)].gdp, 71, tol=0.5)
    pi = primary_income_annual(U)
    assert pi.index[0] == 1999 and (pi.loc[1999:2023] > 0).all()
    quoted("primary income: first complete year", pi.index[0], 1999)
    quoted("primary income 2019 (亿美元)", pi[2019] * 10, 2474, tol=0.5)
    quoted("primary income 2023", pi[2023] * 10, 335, tol=0.5)
    quoted("primary income 2024", pi[2024] * 10, -687, tol=0.5)
    quoted("primary income 2025", pi[2025] * 10, -476, tol=0.5)
    # the two readings of the asymmetry (Gourinchas & Rey; Curcuru, Dvorak & Warnock)
    quoted("'exorbitant privilege': Giscard d'Estaing, February", F["gr_giscard"][0], 1965)
    quoted("Gourinchas-Rey positions at market value since", F["gr_since1952"][0], 1952)
    quoted("    Q2 2026 (history table, US$ bn)", F["beah_primary"][0], U.loc["2026-04-01", "IEABCPI"], tol=1e-6)


def rupee(F):
    print("== ex:external-rupee")
    e0, e1 = F["lk_t515_usd"][1], F["lk_t515_usd"][2]
    quoted("(1) rise in e (%)", 100 * (e1 / e0 - 1), 81.2, tol=0.05)
    quoted("(2) dollar value of the rupee (%)", 100 * (e0 / e1 - 1), -44.8, tol=0.05)
    quoted("(3) a $100 import, end-2021 (rupees)", 100 * e0, 20043, tol=0.5)
    quoted("    end-2022", 100 * e1, 36311, tol=0.5)


def china_rates(B):
    print("== real and nominal: China")
    quoted("CNY/USD 2004 average", year_avg(B.cny_usd_avg, 2004), 8.28, tol=0.005)
    quoted("CNY/USD 2014 average", year_avg(B.cny_usd_avg, 2014), 6.16, tol=0.005)
    n21, n25 = year_avg(B.cn_neer, 2021), year_avg(B.cn_neer, 2025)
    r04, r15 = year_avg(B.cn_reer, 2004), year_avg(B.cn_reer, 2015)
    r21, r25 = year_avg(B.cn_reer, 2021), year_avg(B.cn_reer, 2025)
    quoted("NEER 2021-2025 (%)", 100 * (n25 / n21 - 1), 1.2, tol=0.05)
    quoted("REER 2004-2015 (%)", 100 * (r15 / r04 - 1), 51.5, tol=0.05)
    quoted("REER 2021-2025 (%)", 100 * (r25 / r21 - 1), -14.0, tol=0.05)
    quoted("    relative prices 2021-2025 (REER / NEER, %)", 100 * ((r25 / r21) / (n25 / n21) - 1))


def ppp_levels(PL):
    print("== price levels 2021 (sec:external-rates)")
    lv = PL.set_index("iso3").price_level.astype(float)
    quoted("China", lv["CHN"], 0.62, tol=0.005)
    quoted("Sri Lanka", lv["LKA"], 0.28, tol=0.005)
    quoted("Switzerland", lv["CHE"], 1.16, tol=0.005)
    quoted("United States", lv["USA"], 1.0, tol=1e-9)


def ex_cip():
    print("== ex:external-cip")
    F_ = cip_forward(CIP["e"], CIP["i"], CIP["i_f"])
    quoted("(1) forward", F_, 6.929, tol=0.0005)
    quoted("    below spot (%)", 100 * (F_ / CIP["e"] - 1), -2.4, tol=0.05)
    borrow = CIP["e"] * CIP["usd"]                                     # 万元
    quoted("(2) borrowed (万元)", borrow, 710, tol=1e-9)
    quoted("    repaid", borrow * (1 + CIP["i"]), 720.65, tol=0.005)
    quoted("    dollars after a year (万美元)", CIP["usd"] * (1 + CIP["i_f"]), 104, tol=1e-9)
    quoted("    sold forward at 7.00 (万元)", CIP["usd"] * (1 + CIP["i_f"]) * CIP["quote"], 728, tol=1e-9)
    quoted("    profit (万元)", CIP["usd"] * (1 + CIP["i_f"]) * CIP["quote"] - borrow * (1 + CIP["i"]), 7.35,
           tol=0.005)


def deeper(F):
    print("== deeper: CIP after 2008")
    quoted("basis, three months (bp)", F["dtv_size"][0], 24)
    quoted("basis, five years (bp)", F["dtv_size"][1], 27)
    quoted("    sample", F["dtv_size"][2], 2010)
    quoted("    to", F["dtv_size"][3], 2016)
    quoted("yen five-year basis, end-2015 (bp)", F["dtv_yen"][0], -90)
    quoted("    Libor differential (bp)", F["dtv_yen2"][0], -70)
    quoted("    crisis year", F["dtv_violated"][0], 2008)


def constraint(F):
    print("== sec:external-constraint")
    quoted("NIR end-2021 (亿美元)", F["lk_t512_nir"][3] / 100, -4.23, tol=0.005)
    quoted("NIR end-2022", F["lk_t512_nir"][4] / 100, -32.29, tol=0.005)
    quoted("    = GOR - RRL", (F["lk_t512_gor"][4] - F["lk_t512_rrl"][4]) / 100, -32.29, tol=0.005)
    quoted("SAFE yardstick: months of imports", F["safe_3months"][0], 3)
    quoted("SAFE yardstick: short-term debt (%)", F["safe_100pct"][0], 100)
    quoted("swap share of GOR end-2022 (%; 'most of it')", 100 * F["lk_swap_val2"][1] / F["lk_t512_gor"][4], 75.5,
           tol=0.05)


def ex_sin(F):
    print("== ex:external-sin")
    d21, d22 = F["lk_extdebt"][1], F["lk_extdebt"][0]
    e21, e22 = F["lk_t515_usd"][1], F["lk_t515_usd"][2]
    r21, r22 = d21 * e21 / 1e6, d22 * e22 / 1e6                       # US$ million x Rs/US$ -> Rs trillion
    quoted("(1) end-2021 (万亿卢比)", r21, 10.38, tol=0.005)
    quoted("    end-2022", r22, 18.04, tol=0.005)
    quoted("    change in rupees (%)", 100 * (r22 / r21 - 1), 73.8, tol=0.05)
    quoted("    change in dollars (%)", 100 * (d22 / d21 - 1), -4.1, tol=0.05)


def regime(B):
    print("== compare: fixed vs floating")
    c = B.loc["1998-01":"2005-06", "cny_usd_avg"]
    quoted("CNY/USD monthly averages Jan 1998-Jun 2005: minimum", c.min(), 8.27, tol=0.005)
    quoted("    maximum", c.max(), 8.31, tol=0.005)
    assert B.loc["2005-07", "cny_usd_avg"] < c.min()


def china_case(F, W, B, P):
    print("== case: China 2004-2016")
    quoted("PBoC: foreign exchange share of assets, March 2014 (%)", P.loc["2014-03", "fx_sh"], 83.3, tol=0.05)
    assert P.fx_sh.idxmax() == "2014-03"
    cn = W.loc["CHN"]
    quoted("reserves end-2003 (亿美元)", cn.reserves[2003] * 10, 4162, tol=0.5)
    quoted("reserves end-2014", cn.reserves[2014] * 10, 39000, tol=0.5)
    assert cn.reserves.idxmax() == 2014
    quoted("reserves end-2016", cn.reserves[2016] * 10, 30977, tol=0.5)
    s = cn.loc[2004:2013]
    quoted("2004-2013 reserve transactions (亿美元)", s.res_bop.sum() * 10, 34536, tol=0.5)
    quoted("    current account", s.ca.sum() * 10, 21877, tol=0.5)
    quoted("    capital account", s.ka.sum() * 10, 355, tol=0.5)
    quoted("    errors and omissions", s.eo.sum() * 10, -1864, tol=0.5)
    quoted("    non-reserve financial account", s.nrfa.sum() * 10, -14168, tol=0.5)
    quoted("    identity: CA + KA + EO - NRFA", (s.ca + s.ka + s.eo - s.nrfa).sum() * 10, 34536, tol=0.5)
    quoted("CNY/USD June 2005", B.loc["2005-06", "cny_usd_avg"], 8.28, tol=0.005)
    quoted("CNY/USD January 2014", B.loc["2014-01", "cny_usd_avg"], 6.05, tol=0.005)
    s = cn.loc[2015:2016]
    quoted("2015-2016 current account (亿美元)", s.ca.sum() * 10, 4844, tol=0.5)
    quoted("    reserve transactions", s.res_bop.sum() * 10, -7866, tol=0.5)
    quoted("    non-reserve financial account", s.nrfa.sum() * 10, 8505, tol=0.5)
    quoted("    errors and omissions", s.eo.sum() * 10, -4204, tol=0.5)
    quoted("    errors and omissions / current account (%)", 100 * -s.eo.sum() / s.ca.sum(), 87, tol=0.5)
    quoted("SAFE: assets 2016 (亿美元)", F["safe_assets"][0], 6611)
    quoted("SAFE: inflow 2016", F["safe_inflow"][0], 2441)
    quoted("    outflow 2015", F["safe_inflow"][1], 1010)
    quoted("SAFE: private net liabilities end-2016 (万亿美元)", F["safe_private_nil"][1], 1.3)
    quoted("    end-2014", F["safe_private_nil"][3], 2.3)
    quoted("CNY/USD 2014 average", year_avg(B.cny_usd_avg, 2014), 6.16, tol=0.005)
    quoted("CNY/USD December 2016", B.loc["2016-12", "cny_usd_avg"], 6.92, tol=0.005)
    quoted("SAFE: central parity end-2016", F["safe_cny"][1], 6.9370)
    quoted("    depreciation (%)", F["safe_cny"][3], 6.4)
    p15, p16 = F["safe_cny2015"][1], F["safe_cny"][1]
    quoted("SAFE: central parity end-2015", p15, 6.4936)
    quoted("    dollar value of the renminbi (%), 6.4936/6.9370 - 1", 100 * (p15 / p16 - 1), -6.4, tol=0.05)
    quoted("    rise in e (%)", 100 * (p16 / p15 - 1), 6.8, tol=0.05)
    quoted("Aizenman & Lee sample", F["al_sample"][0], 1980)
    quoted("    to", F["al_sample"][1], 2000)


def penn(PL, PLX, F):
    print("== sec:external-test: price levels and income")
    quoted("economies left out", len(PLX), 12)
    quoted("economies kept", len(PL), 181)
    lv = PL.price_level.astype(float)
    quoted("lowest price level", lv.min(), 0.22, tol=0.005)
    quoted("highest price level", lv.max(), 1.22, tol=0.005)
    r = regress(PL.x, PL.y)
    quoted("elasticity", r.slope, 0.21, tol=0.005)
    quoted("    standard error", r.stderr, 0.02, tol=0.005)
    quoted("    R^2", r.rvalue ** 2, 0.30, tol=0.005)
    quoted("    10% more income -> price level (%)", 100 * (1.1 ** r.slope - 1), 2, tol=0.05)
    hrv = PLX.set_index("iso3").flag
    assert "euro:2023" in hrv["HRV"]
    quoted("Taylor & Taylor: since", F["tt_1950"][0], 1950)
    quoted("    elasticity 'over one half'", F["tt_elasticity"][0], 0.5)
    quoted("    latest cross-section", F["tt_1995"][0], 1995)
    quoted("    countries", F["tt_1995"][1], 142)
    return r


def relative_ppp(RP, RPX, F):
    print("== relative PPP")
    quoted("economies kept (without the US)", len(RP), 137)
    quoted("economies left out", len(RPX), 22)
    r20 = regress(RP.dx_2001_2021, RP.dy_2001_2021)
    quoted("2001-2021 slope", r20.slope, 0.95, tol=0.005)
    quoted("    standard error", r20.stderr, 0.04, tol=0.005)
    quoted("    R^2", r20.rvalue ** 2, 0.78, tol=0.005)
    r1 = regress(RP.dx_2020_2021, RP.dy_2020_2021)
    quoted("2020-2021 slope", r1.slope, 0.56, tol=0.005)
    quoted("    standard error", r1.stderr, 0.29, tol=0.005)
    quoted("    R^2", r1.rvalue ** 2, 0.03, tol=0.005)
    # how much of the one-year result is Libya's official devaluation (fig ext_ppp (c), the triangle)
    lby = RP.set_index("iso3").loc["LBY"]
    quoted("Libya: official rate 2020 (LYD per US$)", float(lby.fx_2020), 1.39, tol=0.005)
    quoted("    2021", float(lby.fx_2021), 4.51, tol=0.005)
    quoted("    inflation gap 2020-2021 (log; 'close to zero')", lby.dx_2020_2021, -0.018, tol=0.0005)
    nl = RP[RP.iso3 != "LBY"]
    r1n = regress(nl.dx_2020_2021, nl.dy_2020_2021)
    quoted("2020-2021 slope without Libya", r1n.slope, 0.65, tol=0.005)
    quoted("    standard error", r1n.stderr, 0.11, tol=0.005)
    quoted("    R^2 ('one fifth')", r1n.rvalue ** 2, 0.20, tol=0.005)
    quoted("dispersion of the inflation gap, 2001-2021 / 2020-2021 (sd ratio; 'small in one year')",
           RP.dx_2001_2021.std() / RP.dx_2020_2021.std(), 18.2, tol=0.05)
    quoted("half-lives (years)", F["tt_halflife"][0], 3)
    quoted("    to", F["tt_halflife"][1], 5)
    k = RP.set_index("iso3")
    quoted("China dx", k.loc["CHN", "dx_2001_2021"], 0.036, tol=0.0005)
    quoted("    as a percentage", 100 * (math.exp(k.loc["CHN", "dx_2001_2021"]) - 1), 4, tol=0.5)
    quoted("China dy", k.loc["CHN", "dy_2001_2021"], -0.25, tol=0.005)
    dq = k.loc["CHN", "dy_2001_2021"] - k.loc["CHN", "dx_2001_2021"]
    quoted("    log change in q, -0.25 - 0.036", dq, -0.29, tol=0.005)
    quoted("    fall in q (%; 'about a quarter'), a real appreciation", -100 * (math.exp(dq) - 1), 25, tol=1)
    quoted("Sri Lanka dx", k.loc["LKA", "dx_2001_2021"], 1.02, tol=0.005)
    quoted("Sri Lanka dy", k.loc["LKA", "dy_2001_2021"], 0.80, tol=0.005)
    quoted("figure (c): Libya, beyond the frame (log change 2020-2021)", k.loc["LBY", "dy_2020_2021"], 1.18, tol=0.005)
    assert (RP.dy_2020_2021 > 0.40).sum() == 1
    return r20, r1


def errors(F, W):
    print("== errors and omissions")
    quoted("US statistical discrepancy Q2 2026 (亿美元)", F["beah_sd"][0] * 10, -1249, tol=0.5)
    quoted("    |discrepancy| / current-account deficit (about half)", -F["beah_sd"][0] / F["beah_ca"][0], 0.51, tol=0.005)
    quoted("    = FA - (CA + KA)", F["beah_fa"][0] - (-F["beah_ca"][0] + F["beah_ka"][0]), F["beah_sd"][0], tol=0.001)
    eo = W.loc["CHN"].eo
    neg = eo.loc[2009:2024]
    assert (neg < 0).all() and eo[2008] > 0 and eo[2025] > 0
    quoted("China: years 2009-2024 with negative errors", len(neg), 16)
    quoted("    2015 (亿美元)", eo[2015] * 10, -2018, tol=0.5)
    quoted("    2016", eo[2016] * 10, -2186, tol=0.5)
    big = eo.loc[2009:2025].nsmallest(3)
    assert set(big.index) == {2015, 2016, 2017} and (big < -200).all(), big
    quoted("    2017 (亿美元; 2015-2017 each beyond -2,000)", eo[2017] * 10, -2066, tol=0.5)
    quoted("    2025", eo[2025] * 10, 385, tol=0.5)


def selfcheck():
    print("== selfcheck")
    quoted("(1) CA and FA rise by", SC["export"], 50)
    quoted("(2) reserves", SC["ca"] - SC["nrfa"], 30)
    quoted("    lend only 10", SC["ca"] - SC["nrfa2"], -10)
    quoted("(3) rise in e (%)", 100 * (SC["e1"] / SC["e0"] - 1), 12.5, tol=0.05)
    quoted("    dollar value of the yuan (%)", 100 * (SC["e0"] / SC["e1"] - 1), -11.1, tol=0.05)
    quoted("(4) approximately (%)", 100 * (SC["de"] + SC["pi_f"] - SC["pi"]), 4, tol=1e-9)
    quoted("    exactly (%)", 100 * ((1 + SC["de"]) * (1 + SC["pi_f"]) / (1 + SC["pi"]) - 1), 3.9, tol=0.05)
    F_ = cip_forward(SC["spot"], SC["i_jpy"], SC["i_usd"])
    quoted("(5) forward (yen)", F_, 144.26, tol=0.005)
    quoted("    expected dollar depreciation (%)", 100 * (1 - F_ / SC["spot"]), 3.8, tol=0.05)
    quoted("(6) CA (% of GDP)", SC["private"] + SC["gov"], -4)
    quoted("(7) foreign assets in home currency (%)", 100 * SC["up"], 20)


def main():
    F = facts()
    LR, B, W = lk_reserves(), bis(), wdi()
    U = us_external()
    P = pbc()
    PL, PLX = price_levels()
    RP, RPX = relppp()
    opening(F, W, U)
    world(F, LR, B, W, U)
    lk_table(F)
    entries()
    compare_ca(F, W)
    safe_signs(F)
    pitfall(F)
    sectors(W)
    ex_us(F, U)
    position(F, U, W)
    rupee(F)
    china_rates(B)
    ppp_levels(pd.concat([PL, PLX]))
    ex_cip()
    deeper(F)
    constraint(F)
    ex_sin(F)
    regime(B)
    china_case(F, W, B, P)
    penn(PL, PLX, F)
    relative_ppp(RP, RPX, F)
    errors(F, W)
    selfcheck()
    print("all Chapter 5 checks passed")



if __name__ == "__main__":
    main()
