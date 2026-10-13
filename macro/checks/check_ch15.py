"""Chapter 15 (早期金融革命：荷兰、英国与可信的国债): every number quoted in zh/ch15_finrevolution.tex.

    python3 checks/check_ch15.py

Inputs are the snapshots finrev_facts (quotations from Smith, Quinn and Roberds, Frost, Shin and Wierts, Gelderblom,
de Jong and Jonker, Temple, North and Weingast, Andréadès, Evelyn, the statutes, Stasavage, Sussman and Yafeh,
Quinn, Temin and Voth, Pincus and Robinson, checked by data/fetch/verify_web_quotes.py; rows read on page images
are marked as such in the snapshot's metadata), gj2011_holland_debt (Holland's debt 1591-1720),
boe_millennium_england_debt (England 1688-1760) and, for comparisons with Chapter 13, dv2010_philip2 and
silver_century_facts. The figure module figsrc/fig_ch15.py imports the functions defined here.

Models (the chapter's key equations):
    agio band          (1 + alpha)/(1 + w) - 1 <= a <= alpha, alpha = C/B - 1   (eq:finrev-agio; Quinn & Roberds eq. 1)
    perpetuity         P = c / r                                                (eq:finrev-perp)
    commitment         repay iff (1 + i) D <= K, so D_max = K / (1 + i)         (eq:finrev-commit)
    default risk (Ch. 14)       p (1 + i) = 1 + r_f                             (eq:africa-risk)
    debt dynamics (Ch. 13)      ps* = (r - g)/(1 + g) d; D* = PS / (r - g)      (eq:silver-debt)
Units: 1 guilder = 20 stivers. England's fiscal years end at Michaelmas and are labelled by the year they begin.
"""
from __future__ import annotations

import math

import pandas as pd

from common import load_snapshot, quoted

STIVER_PER_GUILDER = 20

# Teaching inputs stated in the text
R_F = 0.04                 # ex:finrev-commit: Holland's 4% as the nearly riskless rate
PERIOD = (1714, 1738)      # ex:finrev-debt: England's years compared with Philip II's 1565-1596


def _snapshot_facts():
    df, _ = load_snapshot("finrev_facts", dtype={"value": str})
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


def holland() -> pd.DataFrame:
    """Gelderblom & Jonker (2011) Appendix Tables 1A-1B: debt at the end of each year (million guilders) and
    the shares (%) of its parts; life = A + D, redeemable = B, bills = C + E, lottery = F."""
    df, _ = load_snapshot("gj2011_holland_debt")
    df = df.set_index("year").fillna(0.0)
    df["total"] = df["total_guilders"] / 1e6
    df["share_sum"] = df[["life_pct", "redeemable_pct", "bills_pct", "taxfree_life_pct", "taxfree_bills_pct",
                          "lottery_pct"]].sum(axis=1)
    df["life"] = df["total"] * (df["life_pct"] + df["taxfree_life_pct"]) / 100
    df["redeemable"] = df["total"] * df["redeemable_pct"] / 100
    df["bills"] = df["total"] * (df["bills_pct"] + df["taxfree_bills_pct"]) / 100
    df["lottery"] = df["total"] * df["lottery_pct"] / 100
    return df


def england() -> pd.DataFrame:
    """Bank of England millennium dataset, England 1688-1760 (GBP million; per cent)."""
    df, _ = load_snapshot("boe_millennium_england_debt")
    df = df.set_index("year")
    df["debt_ratio"] = df["debt_incl_annuities_gbp_m"] / df["receipts_gbp_m"]
    df["primary"] = (df["receipts_gbp_m"] - (df["expenditure_gbp_m"] - df["interest_gbp_m"])) / df["receipts_gbp_m"]
    df["interest_rate"] = df["interest_gbp_m"] / df["debt_incl_annuities_gbp_m"]
    return df


def table3() -> pd.DataFrame:
    """Drelichman & Voth (2010) Table 3, as in Chapter 13; g and r in per cent as printed."""
    df, _ = load_snapshot("dv2010_philip2", dtype={"table": str})
    return df[df["table"] == "3"].pivot(index="period", columns="item", values="value")


def ch13_facts() -> dict[str, float]:
    """Chapter 13: what Philip II's bankers recovered after the defaults of 1575 and 1596 (per cent)."""
    df, _ = load_snapshot("silver_century_facts", dtype={"value": str})
    v = dict(zip(df["id"], df["value"]))
    return {"1575": float(v["dv_1575_repaid"]), "1596": float(v["dv_1597_repaid"])}


def said(Q: dict[str, str], qid: str, *tokens: str) -> None:
    """Assert that each token (a number as printed in the source) occurs in the quotation qid."""
    missing = [t for t in tokens if t not in Q[qid]]
    print(f"{'ok ' if not missing else 'BAD'} {qid}: quotation contains {', '.join(tokens)}")
    if missing:
        raise AssertionError(f"{qid}: {missing} not in the quotation")


# --- models ----------------------------------------------------------------
def compound(ratio: float, years: float) -> float:
    """(X_T / X_0)^(1/T) - 1."""
    return ratio ** (1.0 / years) - 1.0


def statutory_agio(current: float, bank: float) -> float:
    """alpha = C/B - 1."""
    return current / bank - 1.0


def agio_band(alpha: float, w: float) -> tuple[float, float]:
    """eq:finrev-agio: the market agios at which a coin stays in the bank, (lower, upper)."""
    return (1.0 + alpha) / (1.0 + w) - 1.0, alpha


def receipt_value(alpha: float, a: float, fee: float) -> float:
    """Smith's receipt: a coin worth 1 + alpha bought back for (1 + a)(1 + fee) bank-money units, as a share."""
    return (1.0 + alpha) - (1.0 + a) * (1.0 + fee)


def perp_yield(c: float, price: float) -> float:
    """eq:finrev-perp: r = c / P."""
    return c / price


def sinking_years(saving: float, rate: float) -> float:
    """Years for a fund of `saving` x debt a year, plus the interest on what it has redeemed, to redeem the debt:
    saving * ((1 + rate)^n - 1) / rate = 1."""
    return math.log(1.0 + rate / saving) / math.log(1.0 + rate)


def repay_prob(i: float, r_f: float = R_F) -> float:
    """eq:africa-risk: the repayment probability at which a risk-neutral lender breaks even."""
    return (1.0 + r_f) / (1.0 + i)


def dmax_gain(i_old: float, i_new: float) -> float:
    """eq:finrev-commit with K fixed: D_max(i_new) / D_max(i_old) - 1."""
    return (1.0 + i_old) / (1.0 + i_new) - 1.0


def annuity_pv(c: float, r: float, n: float) -> float:
    """Present value of c a year for n years at r."""
    return c * (1.0 - (1.0 + r) ** -n) / r


def annuity_years(c: float, r: float, price: float = 100.0) -> float:
    """Years of c a year needed for the present value at r to reach the price."""
    return -math.log(1.0 - price * r / c) / math.log(1.0 + r)


def annuity_irr(c: float, n: float, price: float = 100.0) -> float:
    """Yield of an annuity of c a year for n years bought at price (bisection)."""
    lo, hi = 1e-6, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if annuity_pv(c, mid, n) > price else (lo, mid)
    return (lo + hi) / 2


def ps_star(d: float, r: float, g: float) -> float:
    """eq:silver-debt: primary surplus (share of revenue) that keeps debt/revenue at d."""
    return (r - g) / (1.0 + g) * d


def d_star(ps: float, r: float, g: float) -> float:
    """eq:silver-debt: sustainable debt/revenue for a permanent primary surplus ps."""
    return ps / (r - g)


# --- the series the figures draw ---------------------------------------------
def agio_curves(F, ws) -> dict[str, list[tuple[float, float]]]:
    """For each coin, the (lower, upper) agio band at each withdrawal fee in ws (all in per cent)."""
    out = {}
    for coin, i in (("dukaat", 0), ("rijder", 1)):
        alpha = statutory_agio(F["qr_t5_current"][i], F["qr_t5_bank"][i])
        out[coin] = [tuple(100 * x for x in agio_band(alpha, w / 100)) for w in ws]
    return out


def holland_rates(F) -> list[tuple[int, float, str]]:
    """Holland's issuing rates the text quotes: (year, per cent, source id)."""
    return [(1590, F["gj11_12_83"][0], "gj11_12_83"), (1597, F["gj11_12_83"][1], "gj11_12_83"),
            (1605, F["gj11_7_625"][1], "gj11_7_625"), (1608, F["gj11_7_625"][2], "gj11_7_625"),
            (1652, F["gj11_dewitt"][0], "gj11_dewitt"), (1655, F["gj11_cut4"][0], "gj11_cut4"),
            (1673, F["temple_65m"][1], "temple_65m")]


def crown_loans(F) -> list[tuple[float, float, bool]]:
    """England's Crown loans the text quotes: (year, per cent, perpetual?) -- the forced loans of 1604/5, 1611/2,
    1617 and 1625 (North & Weingast Table 2 and text) and the long-term loans of 1693-1739 (Table 4)."""
    out = [(1604.5, F["nw_t2_1604"][1], True), (1611.5, F["nw_t2_1611"][1], True), (1617, F["nw_1617"][1], True),
           (1625, F["nw_t2_1625"][1], True)]
    for k, y in (("1693", 1693), ("1694a", 1694.2), ("1694b", 1694.2), ("1697", 1697), ("1698", 1698),
                 ("1707", 1707), ("1721", 1721), ("1728", 1728), ("1731", 1731), ("1739", 1739)):
        out.append((y, F[f"nw_t4_{k}"][1], k not in ("1693", "1694a")))
    return out


# ---------------------------------------------------------------------------
def intro(F, H):
    print("\n== opening: 1672 ==")
    quoted("the Stop: for twelve months", F["and_order"][0], 12, tol=0)
    quoted("owed to the goldsmiths (GBP)", F["and_owed"][0], 1_300_000, tol=0)
    quoted("Bank of Amsterdam lost of its balances in two weeks (%)", F["qr_run34"][0], 34, tol=0)
    quoted("Temple ambassador at the Hague", F["temple_title"][0], 1668, tol=0)
    quoted("Smith writes about a century later (years)", 1776 - 1672, 104, tol=0)
    quoted("Holland's debt 1720 / 1672 (more than doubled)", H.loc[1720, "total"] / H.loc[1672, "total"], 2.39, tol=0.005)
    assert H.loc[1720, "total"] / H.loc[1672, "total"] > 2
    quoted("goldsmiths waited, 1672 to 1705 (years)", F["st1701_1705"][0] - 1672, 33, tol=0)
    quoted("England's debt by 1720: over fifty times 1688", F["nw_fifty"][0], 50, tol=0)
    quoted("rates by the 1730s (%)", F["nw_1730s"][0], 3, tol=0)


def world(F, H):
    print("\n== sec:finrev-world ==")
    quoted("Temple: Holland owes about 65 million", F["temple_65m"][0], 65, tol=0)
    quoted("bills: roll-over common by", F["gj11_rollover"][0], 1635, tol=0)
    quoted("Holland's debt 1609 (10k guilders)", H.loc[1609, "total"] * 100, 1442, tol=0.5)
    quoted("Holland's debt 1648 (100m guilders)", H.loc[1648, "total"] / 100, 1.29, tol=0.005)
    quoted("  1609-1648 a year (%)", 100 * compound(H.loc[1648, "total"] / H.loc[1609, "total"], 1648 - 1609), 5.8,
           tol=0.05)
    lo, hi = H.loc[1648:1672, "total"].min(), H.loc[1648:1672, "total"].max()
    quoted("  1648-1672 range, low (m)", lo, 128.4, tol=0.05)
    quoted("  1648-1672 range, high (m) -- roughly flat", hi, 132.0, tol=0.05)
    bills_all = H["bills_pct"] + H["taxfree_bills_pct"]
    assert bills_all.loc[1640] < 50 and (bills_all.loc[1641:1720] > 50).all()   # fig. caption: bills over half from 1641
    quoted("  bills incl. tax-free, lowest share 1641-1720 (%)", bills_all.loc[1641:1720].min(), 50.8, tol=0)
    quoted("Holland's debt 1672 (100m guilders)", H.loc[1672, "total"] / 100, 1.285, tol=0.0005)
    quoted("  bills share 1672 (%)", H.loc[1672, "bills_pct"], 56.4, tol=0)
    quoted("  redeemable share 1672 (%)", H.loc[1672, "redeemable_pct"], 34.8, tol=0)
    quoted("after 1648: interest 7m guilders", F["gj11_7m_60"][0], 7, tol=0)
    quoted("  60% of revenue", F["gj11_7m_60"][1], 60, tol=0)
    quoted("issuing rate 1590 (%)", F["gj11_12_83"][0], 12, tol=0)
    quoted("issuing rate 1597 (%)", F["gj11_12_83"][1], 8.3, tol=0)
    quoted("issuing rate 1605 (%)", F["gj11_7_625"][1], 7, tol=0)
    quoted("issuing rate 1608 (%)", F["gj11_7_625"][2], 6.25, tol=0)
    quoted("Temple: four in the hundred", F["temple_65m"][1], 4, tol=0)
    # England
    quoted("forced loan 1604/5 (GBP)", F["nw_t2_1604"][0], 111_891, tol=0)
    quoted("  at (%)", F["nw_t2_1604"][1], 10, tol=0)
    quoted("1617: 100,000", F["nw_1617"][0], 100_000, tol=0)
    quoted("  at 10%", F["nw_1617"][1], 10, tol=0)
    quoted("  for one year", F["nw_1617"][2], 1, tol=0)
    quoted("1624: lowered to 8%", F["nw_1624"][0], 8, tol=0)
    quoted("forced loan 1625 (GBP)", F["nw_t2_1625"][0], 60_000, tol=0)
    quoted("  at (%)", F["nw_t2_1625"][1], 8, tol=0)
    quoted("  unpaid until", F["nw_1628"][0], 1628, tol=0)
    quoted("debt before 1688: about 1 million", F["nw_1m"][0], 1, tol=0)
    quoted("  2-3% of GNP (low)", F["nw_gnp1688"][0], 2, tol=0)
    quoted("  (high)", F["nw_gnp1688"][1], 3, tol=0)
    quoted("Holland borrowing 5 million", F["nw_holland"][0], 5, tol=0)
    quoted("  at 4%", F["nw_holland"][1], 4, tol=0)
    quoted("Crown paying 6%", F["nw_holland"][2], 6, tol=0)
    quoted("  to 30%", F["nw_holland"][3], 30, tol=0)


def amsterdam(F):
    print("\n== sec:finrev-amsterdam ==")
    quoted("currency 9% below good money", F["smith_nine"][0], 9, tol=0)
    quoted("bank founded", F["smith_1609"][0], 1609, tol=0)
    quoted("bills of 600 guilders and upwards", F["smith_600"][0], 600, tol=0)
    quoted("agio at Amsterdam about (%)", F["smith_agio5"][0], 5, tol=0)
    quoted("Hamburg about (%)", F["smith_hamburg"][0], 14, tol=0)
    quoted("withdrawal fee up to, silver (%)", F["qr_fees"][0], 2, tol=0)
    quoted("  gold (%)", F["qr_fees"][1], 2.5, tol=0)
    quoted("  normally at most (%)", F["qr_fees"][2], 1.5, tol=0)
    quoted("1% for one month = simple annual rate (%)", F["qr_12pct"][0] * 12, F["qr_12pct"][1], tol=0)
    quoted("cashiers by", F["qr_cashiers"][0], 1650, tol=0)
    quoted("patagon re-rated in", F["qr_patagon"][0], 1645, tol=0)
    quoted("  from 2.5", F["qr_patagon"][1], 2.5, tol=0)
    quoted("  to 2.4", F["qr_patagon"][2], 2.4, tol=0)
    quoted("balances after one year", F["qr_first_year"][0], 925_562, tol=0)
    quoted("balances 1683 (m)", F["qr_83m"][0], 8.3, tol=0)
    quoted("  share of the coin stock (%)", F["qr_83m"][1], 5, tol=0)

    print("-- ex:finrev-agio --")
    quoted("mint ordinance", F["qr_1659"][0], 1659, tol=0)
    cur, bank = F["qr_t5_current"], F["qr_t5_bank"]
    quoted("dukaat current", cur[0], 2.5, tol=0)
    quoted("dukaat bank", bank[0], 2.4, tol=0)
    quoted("rijder current", cur[1], 3.15, tol=0)
    quoted("rijder bank", bank[1], 3.0, tol=0)
    a_d, a_r = statutory_agio(cur[0], bank[0]), statutory_agio(cur[1], bank[1])
    quoted("alpha dukaat (%)", 100 * a_d, F["qr_t5_alpha"][0], tol=0.005)
    quoted("alpha rijder (%)", 100 * a_r, F["qr_t5_alpha"][1], tol=1e-9)
    w15, w025 = F["qr_t5_w15"][0] / 100, F["qr_t5_w025"][0] / 100
    quoted("w = 1.5%", 100 * w15, 1.5, tol=0)
    quoted("  dukaat lower (%)", 100 * agio_band(a_d, w15)[0], F["qr_t5_w15"][1], tol=0.005)
    quoted("  rijder lower (%)", 100 * agio_band(a_r, w15)[0], F["qr_t5_w15"][2], tol=0.005)
    quoted("  overlap 3.45-4.17: upper bound is dukaat's alpha (%)", 100 * a_d, 4.17, tol=0.005)
    assert agio_band(a_r, w15)[0] < a_d                                    # the bands overlap
    quoted("w = 0.25%", 100 * w025, 0.25, tol=0)
    quoted("  dukaat lower (%)", 100 * agio_band(a_d, w025)[0], F["qr_t5_w025"][1], tol=0.005)
    quoted("  rijder lower (%)", 100 * agio_band(a_r, w025)[0], F["qr_t5_w025"][2], tol=0.005)
    assert agio_band(a_r, w025)[0] > a_d                                   # no overlap
    quoted("QR: above 4.17 dukaten come in", F["qr_bounds"][0], 4.17, tol=0)
    quoted("QR: below 3.45 rijders go out", F["qr_bounds"][1], 3.45, tol=0)
    # Smith's ducatoon
    dc, db, dpc = F["smith_ducatoon"]
    quoted("ducatoon: 3 guilders 3 stivers", 3 + 3 / STIVER_PER_GUILDER, dc, tol=1e-12)
    quoted("  bank credit (guilders)", db, 3, tol=0)
    quoted("  same values as the rijder", dc - cur[1] + db - bank[1], 0, tol=1e-12)
    quoted("  alpha (%)", 100 * statutory_agio(dc, db), dpc, tol=1e-9)
    fee = F["smith_fees"][0] / 100
    quoted("  keeping fee, silver (%)", 100 * fee, 0.25, tol=0)
    quoted("  receipt good for (months)", F["smith_receipt6m"][0], 6, tol=0)
    a3, sell = F["smith_receipt_175"]
    quoted("  at an agio of 3%", a3, 3, tol=0)
    quoted("  3 bank guilders at 3% agio (guilders)", db * (1 + a3 / 100), 3.09, tol=1e-9)
    quoted("  receipt, approximate (%)", dpc - a3 - 100 * fee, sell, tol=1e-9)
    quoted("  receipt, exact (%)", 100 * receipt_value(dpc / 100, a3 / 100, fee), 1.74, tol=0.005)
    assert receipt_value(dpc / 100, 0.05, fee) < 0
    quoted("  at 5%: approximate value (%)", dpc - 5 - 100 * fee, -0.25, tol=1e-9)
    quoted("Smith: agio now generally about (%)", F["smith_expire"][0], 5, tol=0)

    print("-- 1683 receipts --")
    quoted("receipt fee gold (%)", F["qr_receipt_fee"][0], 0.5, tol=0)
    quoted("receipt fee silver (%)", F["qr_receipt_fee"][1], 0.25, tol=0)
    quoted("receipt lasts (months)", F["qr_receipt_6m"][0], 6, tol=0)
    quoted("old balances without receipts (m)", F["qr_old8m"][0], 8, tol=0)
    quoted("agio around 4% until 1685", F["qr_until1685"][0], 4, tol=0)
    quoted("mean agio 1666:2-1683:7 (%)", F["qr_t3_agio_pre"][0], 3.89, tol=0)
    quoted("mean agio 1683:8-1703:2 (%)", F["qr_t3_agio_post"][0], 4.83, tol=0)
    assert agio_band(a_r, w15)[0] <= F["qr_t3_agio_pre"][0] / 100 <= a_d    # inside the common band
    assert agio_band(a_r, w025)[0] <= F["qr_t3_agio_post"][0] / 100 <= a_r  # inside the rijder band
    quoted("mean balances before (10k)", F["qr_t3_bal_pre"][0] * 100, 679, tol=0)
    quoted("mean balances after (10k)", F["qr_t3_bal_post"][0] * 100, 1251, tol=0)
    quoted("Smith: sell at 5%", F["smith_band"][0], 5, tol=0)
    quoted("  buy at 4%", F["smith_band"][1], 4, tol=0)
    quoted("  never above 5 nor below 4", F["smith_band2"][0] - F["smith_band2"][1], 1, tol=0)
    quoted("before: as high as 9%", F["smith_before"][0], 9, tol=0)
    quoted("  as low as par", F["smith_before"][1], 0, tol=0)

    print("-- lending: the 1669 balance sheet --")
    quoted("dated 31 January", F["qr_t1_date"][0], 31, tol=0)
    quoted("  1669", F["qr_t1_date"][1], 1669, tol=0)
    metal, dep = F["qr_t1_metal"]
    loans = F["qr_t1_ams"][0] + F["qr_t1_holland"][0] + F["qr_t1_voc"][0]
    quoted("metal (m)", metal, 4.5, tol=0)
    quoted("deposits (m)", dep, 6.1, tol=0)
    quoted("capital (m)", F["qr_t1_voc"][1], 1.8, tol=0)
    quoted("assets add up (m)", metal + loans, F["qr_t1_total"][0], tol=1e-9)
    quoted("liabilities add up (m)", dep + F["qr_t1_voc"][1], F["qr_t1_total"][0], tol=1e-9)
    quoted("metal / deposits (%)", 100 * metal / dep, F["qr_t1_ratio"][0], tol=0.5)
    quoted("loans / assets (%)", 100 * loans / F["qr_t1_total"][0], 43, tol=0.5)

    print("-- case: the 1672 run --")
    b14 = F["qr_run_june14"][0]
    b30, m30 = F["qr_run_june30"]
    quoted("balances June 14 (m)", b14, 7.6, tol=0)
    quoted("balances June 30 (m)", b30, 5.0, tol=0)
    quoted("  metal (m)", m30, 4.5, tol=0)
    quoted("  days", 30 - 14, 16, tol=0)
    quoted("  fall (%)", 100 * (1 - b30 / b14), 34, tol=0.5)
    quoted("  metal / deposits after (%)", 100 * m30 / b30, 90, tol=1e-9)
    quoted("compare box: burgomasters", F["smith_burgomasters"][0], 4, tol=0)
    quoted("FSW: the bank 1609-", F["fsw_dates"][0], 1609, tol=0)
    quoted("  -1820", F["fsw_dates"][1], 1820, tol=0)


def voc(F):
    print("\n== sec:finrev-voc ==")
    quoted("charter for (years)", F["gdj_21"][0], 21, tol=0)
    quoted("liquidation after (years)", F["gdj_ten"][0], 10, tol=0)
    quoted("capital (m guilders)", F["gdj_64"][0], 6.4, tol=0)
    quoted("permanent capital", F["gdj_liability"][0], 1612, tol=0)
    quoted("limited liability for directors", F["gdj_liability"][1], 1623, tol=0)
    quoted("trade began after flotation in", F["gj04_aug1602"][0], 1602, tol=0)
    quoted("first prices above par, low (%)", F["gj04_premium"][0], 14, tol=0)
    quoted("  high (%)", F["gj04_premium"][1], 15, tol=0)
    quoted("then around (% of par)", F["gj04_104"][0], 104, tol=0)


def holland_debt(F, H):
    print("\n== sec:finrev-holland ==")
    quoted("1640 plan: from 6.25%", F["gj11_1640"][0], 6.25, tol=0)
    quoted("  to 5%", F["gj11_1640"][1], 5, tol=0)
    quoted("  estimated debt (m)", F["gj11_94m"][0], 94, tol=0)
    quoted("  reconstruction 1640 (m), for comparison", H.loc[1640, "total"], 96.0, tol=0.05)
    quoted("net transfers 1650-53 (m)", F["gj11_transfers"][0], 7, tol=0)
    quoted("  then (m)", F["gj11_transfers"][1], 6, tol=0)
    quoted("private rates by 1655 (%)", F["gj11_private"][0], 4.5, tol=0)
    quoted("  five years later below (%)", F["gj11_private"][1], 4, tol=0)
    quoted("VOC bond rate from (%)", F["gj11_voc35"][0], 4, tol=0)
    quoted("  to (%)", F["gj11_voc35"][1], 3.5, tol=0)
    quoted("De Witt's plan", F["gj11_aug1652"][0], 1652, tol=0)
    quoted("  from 5%", F["gj11_dewitt"][0], 5, tol=0)
    quoted("  to 4%", F["gj11_dewitt"][1], 4, tol=0)
    quoted("  three years later", 1655 - F["gj11_aug1652"][0], 3, tol=0)

    print("-- ex:finrev-holland --")
    p_lo, p_hi = F["gj11_105"]
    c_old, c_new = F["gj11_dewitt"]
    quoted("price 105: yield (%)", 100 * perp_yield(c_old, p_lo), 4.76, tol=0.005)
    quoted("price 107: yield (%)", 100 * perp_yield(c_old, p_hi), 4.67, tol=0.005)
    quoted("cut to (%)", F["gj11_cut4"][0], c_new, tol=0)
    for p, e in zip(F["gj11_under_par"], (4.08, 4.17, 4.30)):
        quoted(f"  price {p:g}: yield (%)", 100 * perp_yield(c_new, p), e, tol=0.005)
        assert perp_yield(c_new, p) < c_old / 100
    d55 = H.loc[1655, "total"]
    quoted("debt 1655 (100m)", d55 / 100, 1.315, tol=0.0005)
    quoted("  bills share (%)", H.loc[1655, "bills_pct"], 58.5, tol=0)
    quoted("  redeemable share (%)", H.loc[1655, "redeemable_pct"], 33.0, tol=0)
    part = H.loc[1655, "bills_pct"] + H.loc[1655, "redeemable_pct"]
    quoted("  together (%)", part, 91.5, tol=1e-9)
    base = d55 * part / 100
    quoted("  together (m)", base, 120.4, tol=0.05)
    quoted("  1 point saved a year (m)", base * (c_old - c_new) / 100, 1.20, tol=0.005)
    n = sinking_years((c_old - c_new) / 100, c_new / 100)
    quoted("  (1.04)^n = 1 + 0.04/0.01", 1 + (c_new / 100) / ((c_old - c_new) / 100), 5, tol=1e-12)
    quoted("  years to redeem", n, 41, tol=0.05)
    quoted("GJ: in 40 years", F["gj11_40y"][0], 40, tol=0)
    quoted("GJ: needed over 3m a year", F["gj11_3m"][0], 3, tol=0)
    quoted("  straight-line on the 1655 debt (m a year)", d55 / F["gj11_40y"][0], 3.29, tol=0.005)
    quoted("  actual fall 1655-1670 (m)", d55 - H.loc[1670, "total"], 3.1, tol=0.05)
    quoted("  years", F["gj11_3m"][2] - F["gj11_3m"][1], 15, tol=0)
    quoted("funds diverted in", F["gj11_diverted"][0], 1664, tol=0)

    print("-- 1672 --")
    quoted("June 2: notice terms raised", F["gj11_june2"][0], 2, tol=0)
    pr = F["gj11_price30"]
    quoted("bill prices fell to (%)", pr[0], 30, tol=0)
    quoted("  recovered to (low)", pr[1], 70, tol=0)
    quoted("  (high)", pr[2], 85, tol=0)
    quoted("  late December (low)", pr[3], 50, tol=0)
    quoted("  (high)", pr[4], 55, tol=0)
    quoted("  early 1673", pr[5], 76, tol=0)
    vol, forced, wealth = F["gj11_1672_loans"]
    quoted("free loans 1672-75 (m)", vol, 10, tol=0)
    quoted("forced loans (m)", forced, 25, tol=0)
    quoted("  share of estimated wealth (%)", wealth, 7, tol=0)
    quoted("  debt rise 1672-1675 (m), for comparison", H.loc[1675, "total"] - H.loc[1672, "total"], 25.0, tol=0.05)
    lev = F["gj11_levies"][0]
    quoted("two levies of (%)", lev, 0.5, tol=0)
    quoted("  4% bills pay effectively (%)", c_new - 2 * lev, F["gj11_3pct"][0], tol=1e-12)
    quoted("debt 1713 (100m)", H.loc[1713, "total"] / 100, 3.10, tol=0.005)
    quoted("  1672-1713 a year (%)", 100 * compound(H.loc[1713, "total"] / H.loc[1672, "total"], 1713 - 1672), 2.2,
           tol=0.05)
    print("-- Temple against Gelderblom and Jonker --")
    t = H.loc[1668:1670, "total"]
    quoted("1668-1670 low (100m)", t.min() / 100, 1.28, tol=0.005)
    quoted("1668-1670 high (100m)", t.max() / 100, 1.31, tol=0.005)
    quoted("  about twice Temple's", t.mean() / F["temple_65m"][0], 2.0, tol=0.05)
    quoted("Temple's debt at 4% (m a year)", F["temple_65m"][0] * F["temple_65m"][1] / 100, 2.6, tol=1e-9)
    quoted("GJ net transfers (m)", F["gj11_transfers"][1], 6, tol=0)


def england_stop(F, E, T):
    print("\n== sec:finrev-england: the Stop ==")
    quoted("owed to Vyner", F["and_owed"][1], 416_724, tol=0)
    quoted("ruined: not less than", F["and_ten_thousand"][0], 10_000, tol=0)
    quoted("6% promised", F["and_6pct"][0], 6, tol=0)
    quoted("  for no more than (months)", F["and_sixmonths"][0], 6, tol=0)
    quoted("excise rent granted in", F["and_1677"][0], 1677, tol=0)
    quoted("1701 Act: 3%", F["st1701_forever"][0], 3, tol=0)
    quoted("  from", F["st1701_1705"][0], 1705, tol=0)
    half = F["and_664"][0]
    quoted("half the capital", half, 664_263, tol=0)
    quoted("six times", F["and_six_times"][0], 6, tol=0)
    print("-- ex:finrev-stop --")
    cap = 2 * half
    quoted("capital", cap, 1_328_526, tol=0)
    quoted("  against 1.3m (ratio)", cap / F["and_owed"][0], 1.02, tol=0.005)
    ann = cap * F["st1701_forever"][0] / 100
    quoted("3% a year (GBP)", ann, 39_856, tol=0.5)
    y1705 = E.loc[1705, "yield_long_pct"]
    quoted("BoE yield on new issues 1705 (%)", y1705, 6, tol=0)
    quoted("value of the annuity at 6% (GBP)", ann / (y1705 / 100), half, tol=0.5)
    years = F["st1701_1705"][0] - 1683
    quoted("unpaid years 1683-1705", years, 22, tol=0)
    claim = cap * (1 + F["and_6pct"][0] / 100 * years)
    quoted("claim with simple interest (GBP m)", claim / 1e6, 3.08, tol=0.005)
    quoted("six times (GBP m)", F["and_six_times"][0] * half / 1e6, 3.99, tol=0.005)
    quoted("recovery, simple interest (%)", 100 * half / claim, 21.6, tol=0.05)
    quoted("recovery, six times (%)", 100 / F["and_six_times"][0], 16.7, tol=0.05)
    rec = ch13_facts()
    quoted("Ch. 13: Philip II's bankers 1575 (%)", rec["1575"], 62, tol=0)
    quoted("  1596 (%)", rec["1596"], 80, tol=0)


def england_commit(F, E):
    print("\n== sec:finrev-england: commitment ==")
    quoted("first large long-term loan (GBP)", F["nw_1693"][0], 1_000_000, tol=0)
    quoted("  in", F["nw_1693"][1], 1693, tol=0)
    quoted("deficiency fund", F["nw_1698"][0], 1698, tol=0)
    print("-- ex:finrev-commit --")
    quoted("r_f (%)", 100 * R_F, F["temple_65m"][1], tol=1e-12)
    p17 = repay_prob(F["nw_1617"][1] / 100)
    quoted("p at 10%", p17, 0.945, tol=0.0005)
    quoted("  default probability (%)", 100 * (1 - p17), 5.5, tol=0.05)
    quoted("p at 6%", repay_prob(F["nw_holland"][2] / 100), 0.981, tol=0.0005)
    quoted("p at 30%", repay_prob(F["nw_holland"][3] / 100), 0.80, tol=1e-9)
    rf08 = F["gj11_7_625"][2] / 100                                          # Holland's 6.25% of 1608
    quoted("  r_f = Holland 1608 (%)", 100 * rf08, 6.25, tol=0)
    p17b = repay_prob(F["nw_1617"][1] / 100, r_f=rf08)
    quoted("  p at 10% with r_f = 6.25%", p17b, 0.966, tol=0.0005)
    quoted("  default probability (%)", 100 * (1 - p17b), 3.4, tol=0.05)
    d88, d20 = F["nw_1m"][0], F["nw_t3_1720"][1]
    quoted("debt 1688 (m)", d88, 1.0, tol=0)
    quoted("debt 1720 (m)", d20, 54.0, tol=0)
    gain = dmax_gain(F["nw_1617"][1] / 100, F["nw_t4_1721"][1] / 100)
    quoted("1721 loan at (%)", F["nw_t4_1721"][1], 5, tol=0)
    quoted("D_max gain, 10% -> 5% (%)", 100 * gain, 4.8, tol=0.05)
    quoted("debt ratio 1720/1688", d20 / d88, 54, tol=1e-9)
    quoted("K must rise to (times)", d20 / d88 / (1 + gain), 52, tol=0.5)
    r88, r20 = E.loc[1688, "receipts_gbp_m"], E.loc[1720, "receipts_gbp_m"]
    quoted("receipts 1688 (m)", r88, 2.87, tol=0.005)
    assert E.loc[1688, "receipts_gbp_m"] == E.loc[1689, "receipts_gbp_m"] == E.loc[1690, "receipts_gbp_m"]
    quoted("receipts 1720 (m)", r20, 5.95, tol=0.005)
    quoted("  ratio", r20 / r88, 2.1, tol=0.05)
    # robustness: interest-only perpetual debt against a yearly cost of default, i D <= k, so D_max = k / i
    perp_gain = (F["nw_1617"][1] / 100) / (F["nw_t4_1721"][1] / 100)
    quoted("  D_max = k/i: 10% -> 5% (times)", perp_gain, 2, tol=1e-12)
    quoted("  times the revenue ratio ('4 倍左右')", perp_gain * r20 / r88, 4, tol=0.2)
    assert perp_gain * r20 / r88 < d20 / d88 / 10
    quoted("compare box: Bank loan 1694 (%)", F["nw_t4_1694b"][1], 8, tol=0)


def bank(F, E, T, H):
    print("\n== sec:finrev-bank ==")
    rate, mgmt, total = F["and_1694"]
    quoted("Tonnage Act: capital (GBP)", F["st1694_xxv"][0], 1_200_000, tol=0)
    quoted("  8%", F["st1694_8pct"][0], rate, tol=0)
    quoted("  plus management (GBP)", mgmt, 4000, tol=0)
    quoted("  a year in all (GBP)", F["st1694_xxv"][0] * rate / 100 + mgmt, total, tol=0)
    quoted("  statute: 100,000", F["st1694_100k"][0], total, tol=0)
    quoted("  redeemable after", F["st1694_redeem"][1], 1705, tol=0)
    quoted("  penalty: treble", F["st1694_treble"][0], 3, tol=0)
    lut = F["and_luttrell"][0]
    quoted("Luttrell: first day (GBP)", lut, 300_000, tol=0)
    quoted("  share of 1.2m", lut / F["st1694_xxv"][0], 0.25, tol=0)
    nine, six = F["and_900"]
    quoted("first three days (GBP)", six, 600_000, tol=0)
    quoted("  share of 1.2m", six / F["st1694_xxv"][0], 0.5, tol=0)
    quoted("after June 25 (GBP)", nine, 900_000, tol=0)
    quoted("NW: one third on the first day (GBP)", F["st1694_xxv"][0] / 3, 400_000, tol=1e-6)
    print("-- Evelyn 1696 --")
    tal, disc = F["evelyn_tallies"]
    quoted("tallies (GBP)", tal, 2000, tol=0)
    quoted("  30% discount = 70% of face (%)", 100 - disc, 70, tol=0)
    quoted("Bank lent (GBP)", F["evelyn_200k"][0], 200_000, tol=0)
    lo, hi, tl = F["evelyn_14_15"]
    quoted("bills 14", lo, 14, tol=0)
    quoted("  or 15", hi, 15, tol=0)
    quoted("tallies 30", tl, 30, tol=0)
    print("-- Table 4 --")
    for k, amt, r in (("1693", 723_394, 14), ("1694a", 1_000_000, 14), ("1694b", 1_200_000, 8),
                      ("1697", 1_400_000, 6.3), ("1698", 2_000_000, 8), ("1707", 1_155_000, 6.25),
                      ("1721", 500_000, 5), ("1728", 1_750_000, 4), ("1731", 800_000, 3), ("1739", 300_000, 3)):
        quoted(f"  {k} amount", F[f"nw_t4_{k}"][0], amt, tol=0)
        quoted(f"  {k} rate (%)", F[f"nw_t4_{k}"][1], r, tol=0)
    print("-- pitfall: the 14% loans --")
    quoted("tontine at first (GBP)", F["and_tontine"][0], 108_000, tol=0)
    quoted("  14% for a life", F["and_tontine"][1], 14, tol=0)
    quoted("  in the end (GBP)", F["and_881"][0], 881_493, tol=0)
    quoted("  NW Table 4 (GBP)", F["nw_t4_1693"][0], 723_394, tol=0)
    c = F["and_tontine"][1]
    quoted("years at 8% to recover 100", annuity_years(c, F["nw_t4_1694b"][1] / 100), 11, tol=0.05)
    quoted("years to get the 100 back undiscounted", 100 / c, 7.14, tol=0.005)
    du, age, paid = F["and_duncombe"]
    quoted("Duncombe: 100", du, 100, tol=0)
    quoted("  aged three", age, 3, tol=0)
    quoted("  77 payments: yield (%)", 100 * annuity_irr(c, paid), 14, tol=0.05)
    li, yrs = F["and_lottery"]
    quoted("lottery: 10%", li, 10, tol=0)
    quoted("  for 16 years", yrs, 16, tol=0)
    prize, mill = F["and_prizes"][0], F["and_million"][0]
    quoted("  prizes a year (GBP)", prize, 40_000, tol=0)
    quoted("  raised (GBP)", mill, 1_000_000, tol=0)
    quoted("  interest plus prizes (%)", li + 100 * prize / mill, 14, tol=1e-9)
    quoted("  yield over 16 years (%)", 100 * annuity_irr(li + 100 * prize / mill, yrs), 11.6, tol=0.05)

    print("-- debt sustainability --")
    quoted("debt 1690 (m)", E.loc[1690, "total_debt_gbp_m"], 3.1, tol=0)
    quoted("debt 1720 (m)", E.loc[1720, "total_debt_gbp_m"], 54.9, tol=0)
    quoted("debt/receipts 1690", E.loc[1690, "debt_ratio"], 1.1, tol=0.05)
    quoted("debt/receipts 1714", E.loc[1714, "debt_ratio"], 9.7, tol=0.05)
    s = E.loc[PERIOD[0]:PERIOD[1]]
    D = s["debt_ratio"].mean()
    r = s["interest_rate"].mean()
    PS = s["primary"].mean()
    r0, r1 = s["receipts_gbp_m"].iloc[0], s["receipts_gbp_m"].iloc[-1]
    g = compound(r1 / r0, PERIOD[1] - PERIOD[0])
    quoted("D 1714-1738", D, 9.38, tol=0.005)
    quoted("r (%)", 100 * r, 4.61, tol=0.005)
    quoted("receipts 1714 (m)", r0, 5.55, tol=0.005)
    quoted("receipts 1738 (m)", r1, 5.82, tol=0.005)
    quoted("  years", PERIOD[1] - PERIOD[0], 24, tol=0)
    quoted("g (%)", 100 * g, 0.20, tol=0.005)
    quoted("PS", PS, 0.461, tol=0.0005)
    quoted("interest / receipts (%), for the record", 100 * (s["interest_gbp_m"] / s["receipts_gbp_m"]).mean(), 43,
           tol=0.5)
    quoted("ps*", ps_star(D, r, g), 0.413, tol=0.0005)
    quoted("D*", d_star(PS, r, g), 10.45, tol=0.005)
    tp = T.loc["1565-96"]
    quoted("Philip II: D 1565-96", tp["D"], 5.476, tol=0)
    quoted("  printed as", round(tp["D"], 2), 5.48, tol=1e-9)
    quoted("  r (%)", tp["r"], 9.40, tol=0)
    quoted("  g (%)", tp["g"], 3.37, tol=0)
    quoted("  PS", tp["PS"], 0.315, tol=0)
    quoted("England's D* at Philip's r", d_star(PS, tp["r"] / 100, g), 5.01, tol=0.005)
    print("-- tab:finrev-four --")
    rev48 = F["gj11_7m_60"][0] / (F["gj11_7m_60"][1] / 100)
    quoted("Holland 1648: revenue implied (m)", rev48, 11.67, tol=0.005)
    quoted("  debt / revenue", H.loc[1648, "total"] / rev48, 11.1, tol=0.05)
    quoted("  interest / debt (%)", 100 * F["gj11_7m_60"][0] / H.loc[1648, "total"], 5.4, tol=0.05)
    quoted("England / Castile, debt ratio", D / tp["D"], 1.7, tol=0.05)
    quoted("Holland / Castile, debt ratio", H.loc[1648, "total"] / rev48 / tp["D"], 2.0, tol=0.05)
    quoted("England / Castile, rate", 100 * r / tp["r"], 0.49, tol=0.005)
    quoted("Holland / Castile, rate", 7 / H.loc[1648, "total"] * 100 / tp["r"], 0.58, tol=0.005)
    # France, September 1715 (Velde 2003, Table 2): perpetual, offices, floating, total, revenue, surplus (m livres)
    perp, perp_i, off, off_i, flo, tot, tot_i, rev, surp = F["velde_t2_1715"]
    quoted("France 1715: capital adds up (m livres)", perp + off + flo, tot, tol=0.05)
    quoted("  interest adds up (m livres)", perp_i + off_i, tot_i, tol=0.05)
    quoted("  debt / revenue", tot / rev, 17.0, tol=0.05)
    quoted("  interest / funded debt (%)", 100 * tot_i / (perp + off), 4.57, tol=0.005)
    quoted("  France / England, debt ratio (text: higher)", tot / rev / D, 1.81, tol=0.005)
    quoted("billets d'Etat: coupon (%)", F["velde_billets"][0], 4, tol=0)
    quoted("  discount in mid-1716 (%)", F["velde_discount"][0], 37, tol=0)
    quoted("  yield at that price (%)", 100 * perp_yield(F["velde_billets"][0], 100 - F["velde_discount"][0]), 6.3, tol=0.05)


def test(F, E):
    print("\n== sec:finrev-test ==")
    quoted("Stasavage: more than thirty years", F["stas_thirty"][0], 30, tol=0)
    y = E["yield_long_pct"]
    assert (y.loc[1703:1709] == 6.0).all()
    quoted("yield 1710 (%)", y[1710], 8.3, tol=0)
    assert y[1711] == y[1712] == 8.7
    assert y[1715] == y[1716] == 5.0
    assert y[1719] == y[1720] == 4.0
    assert (y.loc[1722:1726] == 3.0).all()
    quoted("Bank stock fell, July-November 1710 (%)", F["stas_bank20"][0], 20, tol=0)
    quoted("Whig majority in both Houses", F["stas_whig1715"][0], 1715, tol=0)
    quoted("SY: debt per capita lower until about", F["sy_percapita"][0], 1780, tol=0)
    quoted("Quinn: war years from", F["quinn01_war"][0], 1690, tol=0)
    quoted("  to", F["quinn01_war"][1], 1697, tol=0)
    quoted("usury limit from (%)", F["tv_usury"][0], 6, tol=0)
    quoted("  to (%)", F["tv_usury"][1], 5, tol=0)
    m = E["mortgage_rate_pct"]
    assert (m.loc[1688:1703] == 6.0).all() and (m.loc[1704:1713] == 5.5).all()
    assert (m.loc[1714:1720] == 5.0).all() and (m.loc[1721:1730] == 4.5).all() and (m.loc[1731:1743] == 4.0).all()
    assert (m.loc[1744:1760] == 4.25).all()                                  # fig. caption: 4.25% from 1744
    quoted("France: defaults", F["stas_france"][0], 1715, tol=0)
    quoted("  ", F["stas_france"][1], 1759, tol=0)
    quoted("  ", F["stas_france"][2], 1770, tol=0)
    quoted("compare box: yields in the 1720s, low (%)", y.loc[1720:1729].min(), 3, tol=0.5)
    quoted("  high (%)", y.loc[1720:1729].max(), 5, tol=0)


def deeper(F, H, E):
    print("\n== deeper: discrepancies ==")
    s = H.loc[1655:1665, "share_sum"]
    quoted("shares 1655-1665 add up to, low (%)", s.min(), 96.5, tol=0.05)
    quoted("  high (%)", s.max(), 99.4, tol=0.05)
    quoted("NW Table 3 1697 (m)", F["nw_t3_1697"][1], 16.7, tol=0)
    quoted("  BoE 1696, i.e. 1696/97 (m)", E.loc[1696, "total_debt_gbp_m"], 16.7, tol=0)
    quoted("NW: about 40% of GNP", F["nw_gnp1697"][0], 40, tol=0)
    quoted("BoE 1699 debt incl. annuities / GDP (%)", E.loc[1699, "debt_pct_gdp"], 22.4, tol=0.05)
    quoted("Stasavage: selective default 1756", F["stas_france_sel"][0], 1756, tol=0)
    quoted("  and 1770", F["stas_france_sel"][1], 1770, tol=0)
    quoted("Smith: 2,000 account holders", F["smith_accounts"][0], 2000, tol=0)
    quoted("  1,500 each (GBP)", F["smith_accounts"][1], 1500, tol=0)
    tr, gpp, gl = F["smith_treasure"]
    quoted("  product (GBP)", F["smith_accounts"][0] * F["smith_accounts"][1], tr, tol=0)
    quoted("  in guilders at 11", tr * gpp, gl, tol=0)
    quoted("Smith writes in", F["smith_sept1775"][0], 1775, tol=0)


def selfcheck():
    print("\n== selfcheck ==")
    a = statutory_agio(10.5, 10)
    quoted("Q1: alpha (%)", 100 * a, 5, tol=1e-9)
    quoted("Q1: lower bound at 1% (%)", 100 * agio_band(a, 0.01)[0], 3.96, tol=0.005)
    quoted("Q1: lower bound at 0", 100 * agio_band(a, 0.0)[0], 5, tol=1e-9)
    quoted("Q2: price", 6 / 0.05, 120, tol=1e-9)
    quoted("Q2: 5% at 5%", 5 / 0.05, 100, tol=1e-9)
    quoted("Q2: 6% at 7%", 6 / 0.07, 85.7, tol=0.05)
    quoted("Q2: 5% at 7%", 5 / 0.07, 71.4, tol=0.05)
    quoted("Q3: p at 12%", repay_prob(0.12), 0.929, tol=0.0005)
    quoted("Q3: p at 5%", repay_prob(0.05), 0.990, tol=0.0005)
    quoted("Q4: D_max gain 8% -> 4% (%)", 100 * dmax_gain(0.08, 0.04), 3.8, tol=0.05)
    quoted("Q5: (1.06)^-n", 1 - 100 * 0.06 / 10, 0.4, tol=1e-12)
    quoted("Q5: years", annuity_years(10, 0.06), 15.7, tol=0.05)
    quoted("Q5: PV of 8 years", annuity_pv(10, 0.06, 8), 62.1, tol=0.05)
    quoted("Q5: loss (%)", 100 - annuity_pv(10, 0.06, 8), 38, tol=0.5)
    quoted("Q6: ps*", ps_star(8, 0.05, 0.01), 0.317, tol=0.0005)
    quoted("Q6: D*", d_star(0.30, 0.05, 0.01), 7.5, tol=1e-9)


def from_quotes(Q):
    print("\n== numbers read straight from the quotations ==")
    said(Q, "and_order", "January 2nd, 1672", "two months", "twelve months")
    said(Q, "and_owed", "1,300,000", "416,724")
    said(Q, "and_ten_thousand", "ten thousand")
    said(Q, "and_6pct", "6 per cent")
    said(Q, "and_sixmonths", "six months")
    said(Q, "and_1677", "1677")
    said(Q, "and_1683", "1683")
    said(Q, "and_1701", "3 per cent", "1705")
    said(Q, "and_664", "664,263")
    said(Q, "and_six_times", "six times")
    said(Q, "and_three_m", "three millions")
    said(Q, "and_tontine", "108,000", "14 per cent")
    said(Q, "and_881b", "881,493")
    said(Q, "and_duncombe", "100", "three years old", "77 annual payments", "1692")
    said(Q, "and_lottery", "10 per cent", "16 years")
    said(Q, "and_prizes", "each year")
    said(Q, "and_million", "A million")
    said(Q, "and_1694", "8 per cent")
    said(Q, "and_1694b", "4,000")
    said(Q, "and_100k", "100,000 per annum")
    said(Q, "and_luttrell", "300,000", "opening day")
    said(Q, "and_900", "900,000")
    said(Q, "qr_run34", "34 percent", "two weeks")
    said(Q, "qr_run_june14", "June 14, 1672", "7.6 million")
    said(Q, "qr_run_june30", "5.0 million", "June 30", "4.5 million")
    said(Q, "qr_fees", "2 percent", "2.5 percent", "1.5 percent")
    said(Q, "qr_12pct", "1 percent", "12 percent")
    said(Q, "qr_cashiers", "1650")
    said(Q, "qr_patagon", "1645", "2.5 to 2.4")
    said(Q, "qr_first_year", "925,562")
    said(Q, "qr_83m", "8.3 million", "1683", "5 percent")
    said(Q, "qr_1659", "1659", "dukaat", "rijder")
    said(Q, "qr_t5_current", "2.5", "3.15")
    said(Q, "qr_t5_bank", "2.4", "3.0")
    said(Q, "qr_t5_alpha", "4.17%", "5.00%")
    said(Q, "qr_t5_w15", "1.5%", "2.63%", "3.45%")
    said(Q, "qr_t5_w025", "0.25%", "3.91%", "4.74%")
    said(Q, "qr_bounds", "4.17", "3.45")
    said(Q, "qr_receipt_fee", "½ percent", "¼ percent")
    said(Q, "qr_receipt_6m", "six months")
    said(Q, "qr_old8m", "8 million")
    said(Q, "qr_until1685", "4 percent", "1685")
    said(Q, "qr_after1683", "1683", "5 percent")
    said(Q, "qr_t3_agio_pre", "1666:2-1683:7", "3.89")
    said(Q, "qr_t3_agio_post", "1683:8-1703:2", "4.83")
    said(Q, "qr_t3_bal_pre", "6.79")
    said(Q, "qr_t3_bal_post", "12.51")
    said(Q, "qr_t3_omit", "June-October 1672")
    said(Q, "qr_t1_date", "January 31, 1669")
    said(Q, "qr_t1_metal", "4.5", "6.1")
    said(Q, "qr_t1_ams", "2.1")
    said(Q, "qr_t1_holland", "0.2")
    said(Q, "qr_t1_voc", "1.1", "1.8")
    said(Q, "qr_t1_total", "7.9")
    said(Q, "qr_t1_ratio", "74 percent")
    said(Q, "fsw_dates", "1609-1820")
    said(Q, "fsw_failure", "1780s")
    said(Q, "smith_agio5", "five per cent")
    said(Q, "smith_hamburg", "fourteen per cent")
    said(Q, "smith_nine", "nine per cent")
    said(Q, "smith_1609", "1609")
    said(Q, "smith_600", "600 guilders")
    said(Q, "smith_ducatoon", "three guilders three stivers", "three guilders only", "five per cent")
    said(Q, "smith_fees", "one-fourth per cent", "one-half per cent")
    said(Q, "smith_receipt6m", "six months")
    said(Q, "smith_receipt_175", "three per cent", "one and three-fourths per cent")
    said(Q, "smith_expire", "five per cent")
    said(Q, "smith_band", "five per cent", "four per cent")
    said(Q, "smith_band2", "five", "four per cent")
    said(Q, "smith_before", "nine per cent", "par")
    said(Q, "smith_burgomasters", "four reigning burgomasters", "every year")
    said(Q, "smith_1672", "1672", "Utrecht")
    said(Q, "smith_accounts", "2000", "£1500")
    said(Q, "smith_treasure", "£3,000,000", "eleven guilders", "33,000,000")
    said(Q, "smith_sept1775", "September 1775")
    said(Q, "gdj_21", "21 years")
    said(Q, "gdj_ten", "ten years")
    said(Q, "gdj_64", "6.4 million")
    said(Q, "gdj_liability", "1612", "1623")
    said(Q, "gdj_1612", "July 1612")
    said(Q, "gj04_aug1602", "August 1602")
    said(Q, "gj04_premium", "14–15 percent", "September 1602")
    said(Q, "gj04_104", "104 percent")
    said(Q, "gj04_1609", "1609")
    said(Q, "gj04_bear", "1609/10")
    said(Q, "gj11_rollover", "1635")
    said(Q, "gj11_7m_60", "7 million", "60 percent")
    said(Q, "gj11_12_83", "12 percent in 1590", "8.3 percent in 1597")
    said(Q, "gj11_7_625", "8.3 percent in 1597", "7 in 1605", "6.25 in 1608")
    said(Q, "gj11_1640", "6.25 percent to 5")
    said(Q, "gj11_94m", "94 million")
    said(Q, "gj11_transfers", "1650 and 1653", "7 million", "6 million")
    said(Q, "gj11_private", "4.5 percent by 1655", "less than 4 percent")
    said(Q, "gj11_voc35", "4 to 3.5 percent", "1662 and 1665")
    said(Q, "gj11_aug1652", "August 1652")
    said(Q, "gj11_dewitt", "from 5 to 4 percent")
    said(Q, "gj11_105", "March 1655", "105–107 percent")
    said(Q, "gj11_cut4", "4 percent in August")
    said(Q, "gj11_40y", "40 years")
    said(Q, "gj11_under_par", "98 percent", "96 percent", "93")
    said(Q, "gj11_3m", "3 million", "1655 and 1670")
    said(Q, "gj11_diverted", "redemption funds")
    said(Q, "gj11_june2", "2 June")
    said(Q, "gj11_moratorium", "June 13")
    said(Q, "gj11_overdue", "1675", "1672")
    said(Q, "gj11_price30", "30 percent", "70-85", "50-55", "76 early in 1673")
    said(Q, "gj11_1672_loans", "1672 and 1675", "10 million", "25 million", "7 percent")
    said(Q, "gj11_levies", "0.5 percent each")
    said(Q, "gj11_3pct", "3 percent in 1673")
    said(Q, "temple_title", "1668")
    said(Q, "temple_65m", "Sixty five Millions", "Four in the Hundred")
    said(Q, "nw_t2_1604", "111,891", "10%")
    said(Q, "nw_1617", "100,000", "10 percent", "one year")
    said(Q, "nw_1624", "1624", "8 percent")
    said(Q, "nw_1628", "1628")
    said(Q, "nw_1m", "1 million", "2 and 3 percent")
    said(Q, "nw_holland", "4 percent", "6 and 30 percent")
    said(Q, "nw_1693", "£1,000,000", "1693")
    said(Q, "nw_1698", "1698")
    said(Q, "nw_t3_1697", "1697", "16.7")
    said(Q, "nw_t3_1720", "1720", "54.0")
    said(Q, "nw_gnp1697", "40 percent")
    said(Q, "nw_fifty", "1720", "fifty times", "1688")
    said(Q, "nw_1730s", "1730s", "3 percent")
    for k, amt, r in (("1693", "723,394", "14.0%"), ("1694a", "1,000,000", "14.0"), ("1694b", "1,200,000", "8.0"),
                      ("1697", "1,400,000", "6.3"), ("1698", "2,000,000", "8.0"), ("1707", "1,155,000", "6.25"),
                      ("1721", "500,000", "5.0"), ("1728", "1,750,000", "4.0"), ("1731", "800,000", "3.0"),
                      ("1739", "300,000", "3.0")):
        said(Q, f"nw_t4_{k}", amt, r)
    said(Q, "evelyn_tallies", "£2,000", "30 per cent")
    said(Q, "evelyn_200k", "200,000")
    said(Q, "evelyn_14_15", "14 or 15 per cent", "30 per cent")
    said(Q, "st1694_8pct", "Eight pounds")
    said(Q, "st1694_100k", "One hundred thousand pounds")
    said(Q, "st1694_redeem", "£100,000", "1705", "Year's Notice")
    said(Q, "st1694_xxv", "£1,200,000")
    said(Q, "st1694_treble", "treble")
    said(Q, "st1701_forever", "for ever", "Three Pounds per Centum")
    said(Q, "st1701_1705", "Twenty sixth Day of December One thousand seven hundred and five")
    said(Q, "st1701_redeem", "Moyety")
    said(Q, "stas_thirty", "thirty years")
    said(Q, "stas_bank20", "20%", "July 1710", "November 1710")
    said(Q, "stas_whig1715", "1715")
    said(Q, "stas_southsea", "1711")
    said(Q, "stas_france", "1715", "1759", "1770")
    said(Q, "stas_france_sel", "1756", "1770")
    said(Q, "velde_t2_1715", "Sep 1715", "2817.5", "165.6")
    said(Q, "velde_billets", "billets", "4%")
    said(Q, "velde_discount", "37%", "mid-1716")
    said(Q, "velde_partial", "October 1715", "June 1717")
    said(Q, "velde_floating", "40mL", "4%")
    said(Q, "nw_t2_1625", "1625", "60,000", "8", "1628")
    said(Q, "nw_t2_note_c", "Secured by Crownlands")
    said(Q, "gj11_small", "small ones", "pension")
    said(Q, "smith_ed1_1775", "1775")
    said(Q, "sy_four_decades", "four decades")
    said(Q, "sy_percapita", "1780")
    said(Q, "quinn01_war", "1690-1697")
    said(Q, "tv_usury", "6 to 5 per cent in 1714")


def main():
    F, Q = facts(), quotes()
    H, E, T = holland(), england(), table3()
    intro(F, H)
    world(F, H)
    amsterdam(F)
    voc(F)
    holland_debt(F, H)
    england_stop(F, E, T)
    england_commit(F, E)
    bank(F, E, T, H)
    test(F, E)
    deeper(F, H, E)
    selfcheck()
    from_quotes(Q)
    print("all numbers in Chapter 15 check out")


if __name__ == "__main__":
    main()
