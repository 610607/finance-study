"""Chapter 16 (重商主义、约翰·劳与重农学派): every number quoted in zh/ch16_mercantilism.tex.

    python3 data/fetch/fgr2009_1720_shares.py      # once: the share prices are not kept in the repository
    python3 checks/check_ch16.py

Inputs are the snapshots merc_facts (quotations from Mun, Smith, Law, Velde, Garber, Temin and Voth, Frehen,
Goetzmann and Rouwenhorst, Cantillon, Quesnay and Oncken, checked by data/fetch/verify_web_quotes.py; four rows
were read on page images, see the snapshot's metadata), fgr2009_1720_shares (daily share prices 1718-1720; its
licence forbids circulating it, so the fetch script above writes it) and, for France in 1715, finrev_facts
(Chapter 15). The figure module figsrc/fig_ch16.py imports the functions defined here.

Models (the chapter's key equations):
    balance of trade (Mun)      net inflow of treasure = EX - IM                    (unnumbered)
    debt-for-equity swap        E/(N P) < i  <=>  P/(E/N) > 1/i                      (eq:merc-swap; Velde 2003, p. 49)
    pegged share price          dM = p_bar dS                                        (eq:merc-peg)
    Cantillon, two groups       s_B' = m_B/(M + dM) = s_B/(1 + dM/M)                 (eq:merc-cantillon)
    Tableau                     sum_j T_ij = sum_j T_ji;  X = A + I + R              (eq:merc-tableau; Quesnay 1766)
    Gordon formula              P = d/(r - g)                                        (eq:merc-gordon; g = 0 is eq:finrev-perp)
Units: 1 shilling = 12 pence; mL = million livres; London dates are Julian, Paris dates Gregorian (11 days later).
"""
from __future__ import annotations

import math

import pandas as pd

from common import load_snapshot, quoted

PENCE_PER_SHILLING = 12
JULIAN_LAG_DAYS = 11

# Teaching inputs stated in the text
VOYAGE_CHARGES = 18        # ex:merc-mun: freight, insurance and customs per pound of pepper from the Indies (pence)
CANTILLON = dict(M=100.0, mA=20.0, dM=25.0)   # ex:merc-cantillon
LUXURY_SHIFT = 0.2         # ex:merc-tableau (3): billion livres moved from food to braid made of imported material
GROWTH_GDP = 0.005         # ex:merc-gordon (3): Velde's 0.5% GDP growth (velde_growth)
PEG_DATES = ("1720-03-05", "1720-05-21")


def _snapshot_facts():
    df, _ = load_snapshot("merc_facts", dtype={"value": str})
    return df


def facts() -> dict[str, list[float]]:
    """id -> list of the numbers in the value column (several values are separated by ';')."""
    out = {}
    for _, r in _snapshot_facts().iterrows():
        v = r["value"]
        if isinstance(v, str) and v.strip():
            out[r["id"]] = [float(x) if "-" not in x else x for x in v.split(";")]
    return out


def quotes() -> dict[str, str]:
    """id -> verbatim quotation."""
    df = _snapshot_facts()
    return dict(zip(df["id"], df["quote"].fillna("")))


def france1715() -> dict[str, float]:
    """Velde (2003) Table 2, September 1715, from Chapter 15's snapshot (mL)."""
    df, _ = load_snapshot("finrev_facts", dtype={"value": str})
    v = dict(zip(df["id"], df["value"]))
    keys = ["rentes", "rentes_int", "offices", "offices_int", "floating", "total", "interest", "revenue", "primary"]
    d = dict(zip(keys, [float(x) for x in v["velde_t2_1715"].split(";")]))
    d["billets_coupon"] = float(v["velde_billets"])
    d["billets_discount"] = float(v["velde_discount"])
    return d


def said(Q: dict[str, str], qid: str, *tokens: str) -> None:
    """Assert that each token (a number as printed in the source) occurs in the quotation qid."""
    missing = [t for t in tokens if t not in Q[qid]]
    print(f"{'ok ' if not missing else 'BAD'} {qid}: quotation contains {', '.join(tokens)}")
    if missing:
        raise AssertionError(f"{qid}: {missing} not in the quotation")


# --- data ------------------------------------------------------------------
def shares() -> pd.DataFrame:
    """Frehen, Goetzmann & Rouwenhorst (2009) price database: daily prices indexed by the Gregorian date."""
    df, _ = load_snapshot("fgr2009_1720_shares", parse_dates=["date"])
    return df.set_index("date")


def table4() -> pd.DataFrame:
    """Velde (2003) Table 4, read from the quoted rows: notes issued less burned (col1), adjusted for notes retired but
    not burned (col2; equal to col1 where the table leaves it blank), market value in current silver livres (col3)
    and in constant silver livres of 1719 at 60L per marc (col4); mL. `deflator` = col4/col2 is the value in 1719
    silver livres of one livre of notes."""
    df = _snapshot_facts()
    rows = []
    for _, r in df[df["id"].str.startswith("velde_t4_") & (df["id"] != "velde_t4_cols")].iterrows():
        tok = r["quote"].split()
        date = pd.Timestamp(" ".join(tok[:3]))
        tail = [float(x) for x in tok[3 + 5:]]
        if len(tail) == 2:
            c1, c2, c3, c4 = tail[0], tail[0], None, tail[1]
        else:
            c1, c2, c3, c4 = tail
        assert [c1, c4] == [float(x) for x in r["value"].split(";")], r["id"]
        rows.append(dict(date=date, col1=c1, col2=c2, col3=c3, col4=c4))
    t = pd.DataFrame(rows).set_index("date").sort_index()
    t["deflator"] = t["col4"] / t["col2"]
    return t


def silver_price(S: pd.DataFrame, T: pd.DataFrame) -> pd.Series:
    """The Mississippi share in 1719 silver livres at the dates of Table 4: the last quotation on or before each
    date (at most ten days earlier) times Table 4's deflator."""
    m = S["mississippi"].dropna()
    out = {}
    for d, row in T.iterrows():
        prev = m[m.index <= d]
        if len(prev) and (d - prev.index[-1]).days <= 10:
            out[d] = prev.iloc[-1] * row["deflator"]
    return pd.Series(out)


def last_on_or_before(s: pd.Series, date: str) -> float:
    s = s.dropna()
    return float(s[s.index <= pd.Timestamp(date)].iloc[-1])


def julian(S: pd.DataFrame, date: str, col: str) -> float:
    """Price on a London (Julian) date."""
    row = S[S["date_julian"] == date]
    return float(row[col].iloc[0])


# --- models ----------------------------------------------------------------
def swap_cheaper(E: float, N: float, P: float, i: float) -> bool:
    """eq:merc-swap: the swap costs the king E/(N P) a year per livre of debt retired."""
    return E / (N * P) < i


def pe_threshold(i: float) -> float:
    return 1.0 / i


def peg_money(p_bar: float, dS: float) -> float:
    """eq:merc-peg."""
    return p_bar * dS


def cantillon(M: float, mA: float, dM: float) -> dict[str, float]:
    """eq:merc-cantillon with V = 1 and Y fixed: shares of output before and after dM goes to group A."""
    mB = M - mA
    return dict(sA=mA / M, sB=mB / M, sA1=(mA + dM) / (M + dM), sB1=mB / (M + dM), price=(M + dM) / M)


def gordon(d: float, r: float, g: float = 0.0) -> float:
    """eq:merc-gordon."""
    assert r > g
    return d / (r - g)


def annuity(c: float, r: float, n: int) -> float:
    return c * (1 - (1 + r) ** -n) / r


def garber_value(r: float = 0.04) -> float:
    """1.9m a year until 1727 and 1.5m thereafter, discounted from 1720 at r (end-of-year payments; GBP m)."""
    n = 1727 - 1720
    return annuity(1.9, r, n) + (1.5 / r) / (1 + r) ** n


# Quesnay's Tableau (1766), billion livres: payments T[payer][payee]
CLASSES = ("productive", "proprietors", "sterile")


def tableau(shift: float = 0.0) -> dict[str, dict[str, float]]:
    """The money flows of the Analyse (1766). `shift` moves proprietors' spending from food to braid whose material
    the sterile class buys abroad (ex:merc-tableau (3)); the extra receipts of the sterile class leave the country."""
    return {
        "productive": {"proprietors": 2.0, "sterile": 1.0},                        # rent; works (upkeep of original advances)
        "proprietors": {"productive": 1.0 - shift, "sterile": 1.0 + shift},        # food; works
        "sterile": {"productive": 2.0, "abroad": shift},                            # raw material 1 + food 1
    }


def receipts(T, k: str) -> float:
    return sum(v.get(k, 0.0) for v in T.values())


def payments(T, k: str) -> float:
    return sum(T[k].values())


# --- sections --------------------------------------------------------------
def intro(F, T):
    print("\n== opening ==")
    quoted("Law minister of finance: January 5, 1720", 1720, 1720, tol=1e-9)
    quoted("share price 1718 (L)", F["velde_40fold"][0], 250, tol=1e-9)
    quoted("peak January 1720 (L)", F["velde_40fold_b"][0], 10_000, tol=1e-9)
    quoted("notes 30 Apr 1719 (10k L... mL)", T.loc["1719-04-30", "col1"], 38.0, tol=1e-9)
    quoted("notes 30 Jun 1720 (100 mL)", T.loc["1720-06-30", "col1"] / 100, 23.59, tol=1e-9)
    quoted("South Sea January 1720 (about)", F["garber_120"][0], 120, tol=1e-9)
    quoted("South Sea peak", F["garber_peak"][0], 950, tol=1e-9)
    quoted("South Sea 1 October (about)", F["garber_collapse"][1], 290, tol=1e-9)
    quoted("Smith writes 'fifty-odd years later' (1776 - 1720)", 1776 - 1720, 56, tol=1e-9)
    assert 50 < 1776 - 1720 < 60


def world(F, Fr):
    print("\n== sec:merc-world ==")
    quoted("rentes principal Sep 1715 (100 mL)", Fr["rentes"] / 100, 10.686, tol=1e-9)
    quoted("offices (100 mL)", Fr["offices"] / 100, 8.30, tol=1e-9)
    quoted("floating debt (100 mL)", Fr["floating"] / 100, 9.189, tol=1e-9)
    quoted("total (100 mL)", Fr["total"] / 100, 28.175, tol=1e-9)
    assert math.isclose(Fr["rentes"] + Fr["offices"] + Fr["floating"], Fr["total"], abs_tol=0.05)
    quoted("revenue (100 mL)", Fr["revenue"] / 100, 1.656, tol=1e-9)
    quoted("debt / revenue", Fr["total"] / Fr["revenue"], 17, tol=0.05)
    quoted("interest on rentes and offices (10 mL... mL)", Fr["interest"], 86.7, tol=1e-9)
    assert math.isclose(Fr["rentes_int"] + Fr["offices_int"], Fr["interest"], abs_tol=0.05)
    quoted("  share of revenue -- more than half (%)", 100 * Fr["interest"] / Fr["revenue"], 52.4, tol=0.05)
    assert Fr["interest"] / Fr["revenue"] > 0.5
    quoted("primary surplus (mL)", Fr["primary"], 47.7, tol=1e-9)
    quoted("billets d'Etat coupon (%)", Fr["billets_coupon"], 4, tol=1e-9)
    quoted("  discount soon after issue (%)", Fr["billets_discount"], 37, tol=1e-9)
    # England 1720 (Garber)
    total, three, boe, eic, ssc, red, irr = F["garber_debt50"]
    _, lo, hi, short = F["garber_irred"]
    quoted("British debt 1720 (GBP m, about)", total, 50, tol=1e-9)
    quoted("  held by the three companies", three, 18.3, tol=1e-9)
    quoted("  Bank / EIC / South Sea add up", boe + eic + ssc, 18.3, tol=1e-9)
    quoted("  redeemables held privately", red, 16.5, tol=1e-9)
    quoted("  irredeemable annuities (about)", irr, 15, tol=1e-9)
    quoted("  parts add up to about 50", three + red + irr, 49.8, tol=1e-9)
    quoted("  long annuities, years (low)", lo, 72, tol=1e-9)
    quoted("  (high)", hi, 87, tol=1e-9)
    quoted("  short annuities, years", short, 22, tol=1e-9)


def mun(F):
    print("\n== sec:merc-mun ==")
    quoted("Mun written about", F["mun_written"][0], 1630, tol=1e-9)
    quoted("  printed by his son", F["mun_written"][1], 1664, tol=1e-9)
    quoted("director of the East India Company from", F["mun_1615"][0], 1615, tol=1e-9)
    quoted("Discourse of Trade published", F["mun_discourse"][0], 1621, tol=1e-9)
    x, m, g = F["mun_ex_export"][0], F["mun_ex_import"][0], F["mun_ex_gain"][0]
    quoted("exports (GBP m)", x / 1e6, 2.2, tol=1e-9)
    quoted("imports (GBP m)", m / 1e6, 2.0, tol=1e-9)
    quoted("net inflow = EX - IM (GBP m)", (x - m) / 1e6, 0.2, tol=1e-9)
    assert x - m == g
    home, ams, indies = F["mun_pepper_home"][0], F["mun_pepper_ams"][0], F["mun_pepper_indies"][0]
    quoted("pepper at home: two shillings = pence", 2 * PENCE_PER_SHILLING, home, tol=1e-9)
    quoted("  Amsterdam (d)", ams, 20, tol=1e-9)
    quoted("  East Indies (d)", indies, 3, tol=1e-9)
    # ex:merc-mun
    via_ams, via_ind = home - ams, home - indies - VOYAGE_CHARGES
    quoted("ex: merchant's profit via Amsterdam (d)", via_ams, 4, tol=1e-9)
    quoted("ex: merchant's profit via the Indies (d)", via_ind, 3, tol=1e-9)
    assert via_ams > via_ind
    quoted("ex: kingdom saves per pound (d)", ams - indies, 17, tol=1e-9)
    quoted("ex: merchant earns less by (d)", via_ams - via_ind, 1, tol=1e-9)
    quoted("ex: re-export at the Amsterdam price, inflow (d)", ams - indies, 17, tol=1e-9)


def law(F):
    print("\n== sec:merc-law ==")
    rent, years, value = F["law_acre"]
    quoted("acre pays", rent, 100, tol=1e-9)
    quoted("  at 20 years purchase", years, 20, tol=1e-9)
    quoted("  worth", rent * years, value, tol=1e-9)
    quoted("  implied rate (%)", 100 * rent / value, 5, tol=1e-9)


def system(F, T, S):
    print("\n== sec:merc-system: the Bank ==")
    shares_, price, disc = F["velde_bank_1716"]
    quoted("Bank shares", shares_, 1200, tol=1e-9)
    quoted("  at (L)", price, 5000, tol=1e-9)
    quoted("  billets at a market discount of (%)", disc, 60, tol=1e-9)
    quarter = F["velde_quarter"][0]
    cash, billets_m = F["velde_bank_assets"]
    quoted("  cash (L)", cash, 375_000, tol=1e-9)
    quoted("  billets (mL)", billets_m, 1.125, tol=1e-9)
    first = shares_ * price * quarter
    quoted("1200 x 5000 / 4 (10k L)", first / 1e4, 150, tol=1e-9)
    assert math.isclose(first, cash + billets_m * 1e6)
    per = price * quarter
    quoted("  first payment per share (L)", per, 1250, tol=1e-9)
    quoted("  of which cash (L)", cash / shares_, 312.5, tol=1e-9)
    quoted("  billets at face (L)", billets_m * 1e6 / shares_, 937.5, tol=1e-9)
    quoted("  billets worth at 40% (L)", billets_m * 1e6 / shares_ * (1 - disc / 100), 375, tol=1e-9)
    cash690 = cash / shares_ + billets_m * 1e6 / shares_ * (1 - disc / 100)
    quoted("  cash needed (L; Velde 690)", cash690, F["velde_690"][0], tol=3)
    quoted("legal tender for taxes: 10 April 1717", 1717, 1717, tol=1e-9)
    lo, hi = (float(x) for x in F["velde_bank_notes"][0].split("-"))
    quoted("notes a year, low (mL)", lo, 40, tol=1e-9)
    quoted("  high", hi, 50, tol=1e-9)
    quoted("  specie reserve (%)", F["velde_bank_notes"][1], 50, tol=1e-9)
    quoted("  in circulation Dec 1718 (10k... mL)", F["velde_bank_notes"][2], 39.5, tol=1e-9)
    quoted("bought out at face (L)", F["velde_royal"][0], 5000, tol=1e-9)

    print("\n== the Company ==")
    quoted("Louisiana population 1717 (about)", F["velde_louisiana"][0], 500, tol=1e-9)
    n_ipo, p_ipo = F["velde_ipo"]
    quoted("IPO shares", n_ipo, 200_000, tol=1e-9)
    quoted("  at (L)", p_ipo, 500, tol=1e-9)
    sold, king = F["velde_ipo_closed"]
    quoted("  sold by 31 Dec 1718 (100 mL)", sold / 100, 1, tol=1e-9)
    assert n_ipo * p_ipo == sold * 1e6
    quoted("  owned by the King (%)", king, 40, tol=1e-9)
    quoted("  billets bore (%)", F["velde_convert"][0], 4, tol=1e-9)
    quoted("tobacco, a year (10k L)", F["velde_tobacco"][0] * 100, 402, tol=1e-9)
    quoted("mints, lump sum (mL)", F["velde_mints"][0], 50, tol=1e-9)
    quoted("  for nine years", 9, 9, tol=1e-9)
    quoted("General Farms, share of revenue (%)", F["velde_farms"][0], 30, tol=1e-9)
    quoted("  lease a year (mL)", F["velde_farms_lease"][0], 52, tol=1e-9)
    quoted("  previously (mL)", F["velde_farms_lease"][1], 48.5, tol=1e-9)
    quoted("recettes generales, share of revenue (%)", F["velde_recettes"][0], 55, tol=1e-9)
    issues = [F["velde_issue2"], F["velde_issue3"], F["velde_issue4"]]
    for (n, p), (n0, p0) in zip(issues, [(50_000, 550), (50_000, 1000), (300_000, 5000)]):
        quoted(f"issue: {n0:,} shares", n, n0, tol=1e-9)
        quoted(f"  at {p0} L", p, p0, tol=1e-9)
    quoted("rights: four mothers", F["velde_mothers"][0], 4, tol=1e-9)
    quoted("  and one daughter", F["velde_mothers"][1], 1, tol=1e-9)
    total_shares = n_ipo + sum(n for n, _ in issues)
    quoted("shares after the four issues", total_shares, 600_000, tol=1e-9)
    assert total_shares == F["velde_t6_dec19"][1]

    print("\n== tab:merc-system ==")
    quoted("notes when the Bank became Royal (mL)", F["velde_bank_notes"][2], 39.5, tol=1e-9)
    quoted("loan 1200 then 1600 (mL)", F["velde_conv_date"][0], 1200, tol=1e-9)
    quoted("  raised to", F["velde_conv_date"][1], 1600, tol=1e-9)
    quoted("  at (%)", F["velde_conv_date"][2], 3, tol=1e-9)
    quoted("dividend 1720 (L)", F["velde_t6_dec19"][0], 200, tol=1e-9)
    quoted("  price 29 Dec 1719 (L)", F["velde_t6_dec19"][2], 9413, tol=1e-9)
    quoted("coins held at most (L)", F["velde_500coin"][0], 500, tol=1e-9)
    quoted("  payments above (L) in notes", F["velde_500coin"][1], 100, tol=1e-9)
    quoted("peg (L)", F["velde_peg"][0], 9000, tol=1e-9)
    quoted("May 21: shares to (L)", F["velde_may21"][1], 5000, tol=1e-9)
    quoted("  from (L)", F["velde_may21"][0], 9000, tol=1e-9)

    print("\n== the swap ==")
    quoted("interest 36 then 48 (mL)", F["velde_conv_48"][0], 36, tol=1e-9)
    quoted("  raised to", F["velde_conv_48"][1], 48, tol=1e-9)
    quoted("  deducted from the lease of", F["velde_conv_48"][2], 52, tol=1e-9)
    assert math.isclose(1200 * 0.03, 36) and math.isclose(1600 * 0.03, 48)
    quoted("ordered repaid 31 Aug 1719 (100 mL)", F["velde_t3_total"][0] / 1e8, 14.998, tol=0.0005)
    quoted("  of which rentes on the Hotel de Ville (100 mL)", F["velde_t3_rentes"][0] / 1e8, 9.617, tol=0.0005)
    quoted("  both parts by July 1720 (100 mL)", F["velde_t3_grand"][0] / 1e8, 19.771, tol=0.0005)
    quoted("share 26 Aug 1719 (L)", F["velde_3600"][0], 3600, tol=1e-9)
    quoted("  9 Sep (L)", F["velde_3600"][1], 5350, tol=1e-9)
    a, p, b = F["velde_500ml"]
    quoted("raise (mL)", a, 500, tol=1e-9)
    quoted("  at (L)", p, 5000, tol=1e-9)
    quoted("  further issues (mL)", b, 1000, tol=1e-9)
    quoted("5 + 10 = 15 (100 mL) = 300,000 x 5000", (a + b) / 100, 300_000 * 5000 / 1e8, tol=1e-9)
    i_old, c_new = F["velde_swap"]
    quoted("average rate of the bonds (%)", i_old, 4.5, tol=1e-9)
    quoted("  Company owed (%)", c_new, 3, tol=1e-9)
    quoted("State paid creditors a year (mL, roughly)", F["velde_fig6_90"][0], 90, tol=1e-9)
    quoted("dividend no less than (mL)", F["velde_fig6_48"][0], 48, tol=1e-9)
    quoted("Company collected of taxes (%)", F["velde_90pct"][0], 90, tol=1e-9)
    quoted("19.77 bn x 4.5% (100 mL)", F["velde_t3_grand"][0] * i_old / 100 / 1e8, 0.89, tol=0.005)
    quoted("P/E threshold 1/0.045", pe_threshold(i_old / 100), 22, tol=0.25)
    quoted("  Velde: higher than", F["velde_pe22"][0], 22, tol=1e-9)

    print("\n== ex:merc-swap ==")
    d1, n1, p1, pd1 = F["velde_t6_jul19"]
    d2, n2, p2, pd2 = F["velde_t6_dec19"]
    quoted("Jul 1719: dividend (L)", d1, 60, tol=1e-9)
    quoted("  shares", n1, 250_000, tol=1e-9)
    quoted("  price (L)", p1, 1960, tol=1e-9)
    quoted("  P/D", p1 / d1, pd1, tol=0.5)
    quoted("Dec 1719: shares", n2, 600_000, tol=1e-9)
    quoted("  P/D", p2 / d2, pd2, tol=0.5)
    assert p1 / d1 > 22 and p2 / d2 > 22
    quoted("  implied cost (%)", 100 * d2 / p2, 2.1, tol=0.05)
    quoted("Law's target (%)", F["velde_pe45"][3], 2, tol=1e-9)
    quoted("200 x 600,000 (100 mL)", d2 * n2 / 1e8, 1.2, tol=1e-9)
    assert d2 * n2 / 1e6 > F["velde_fig6_90"][0]
    need, dv, n4 = F["velde_80ml"]
    quoted("Law: revenues needed (mL)", need, 80, tol=1e-9)
    quoted("  = 200 x 400,000", dv * n4 / 1e6, need, tol=1e-9)
    quoted("  omitted shares held as collateral", 100_000, 100_000, tol=1e-9)
    assert swap_cheaper(E=need * 1e6, N=n4, P=p2, i=i_old / 100)
    # (3) why (1) and (3) do not contradict each other: N P is far above the debt retired (N P = D fails)
    debt = F["velde_t3_grand"][0]
    quoted("  600,000 x 9413 (100 mL, 'about 56')", n2 * p2 / 1e8, 56, tol=0.5)
    quoted("  debt to be repaid (100 mL, 'about 20')", debt / 1e8, 20, tol=0.25)
    quoted("  market value / debt ('nearly three times')", n2 * p2 / debt, 2.86, tol=0.005)
    assert 2.5 < n2 * p2 / debt < 3
    issue_prices = [p_ipo] + [p for _, p in issues]
    assert max(issue_prices) == 5000                      # 'issued at 5,000L or less'
    quoted("  P/D at the 5000 L issue price", 5000 / d2, 25, tol=1e-9)
    assert 5000 / d2 > pe_threshold(i_old / 100)            # 'only a little above 22'

    print("\n== notes and the peg ==")
    a, b, c = F["velde_notes_1bn"]
    quoted("notes Dec 1718 (mL)", a, 40, tol=1e-9)
    quoted("Table 4: 31 Aug 1719 (100 mL)", T.loc["1719-08-31", "col1"] / 100, 3.806, tol=1e-9)
    quoted("Table 4: 29 Feb 1720 (100 mL)", T.loc["1720-02-29", "col1"] / 100, 10.697, tol=1e-9)
    # deeper box: Velde's text (400mL 'by July 1719', 1bnL 'in January 1720') runs ahead of his Table 4
    quoted("Velde's text: Jul 1719 (100 mL)", b / 100, 4, tol=1e-9)
    quoted("  Jan 1720 (100 mL)", c / 100, 10, tol=1e-9)
    quoted("Table 4: 31 Jul 1719 (100 mL)", T.loc["1719-07-31", "col1"] / 100, 1.599, tol=1e-9)
    quoted("Table 4: 30 Jan 1720 (100 mL)", T.loc["1720-01-30", "col1"] / 100, 8.101, tol=1e-9)
    assert abs(T.loc["1719-08-31", "col1"] - b) < abs(T.loc["1719-07-31", "col1"] - b)    # 'close only by end-August'
    assert abs(T.loc["1720-02-29", "col1"] - c) < abs(T.loc["1720-01-30", "col1"] - c)    # 'and end-February'
    quoted("specie stock (100 mL)", F["velde_specie"][0] / 100, 12, tol=1e-9)
    quoted("authorized issues Dec 1719 (100 mL)", F["velde_640"][0] / 100, 6.4, tol=1e-9)
    quoted("  'tripled' = increased to three times", 3, 3, tol=1e-9)
    quoted("bought 5000 L from 5 Oct 1719", F["velde_buy5000"][0], 5000, tol=1e-9)
    bought, pct = F["velde_office"]
    quoted("office bought (100 mL)", bought / 100, 8, tol=1e-9)
    quoted("  of capitalization (%)", pct, 16, tol=1e-9)
    s0, p0, s1, p1_, cap = F["velde_cap"]
    quoted("original shares", s0, 300_000, tol=1e-9)
    quoted("  bought at (L)", p0, 9925, tol=1e-9)
    quoted("subscriptions (at most)", s1, 300_000, tol=1e-9)
    quoted("  valued at (L)", p1_, 6600, tol=1e-9)
    quoted("capitalization (100 mL)", (s0 * p0 + s1 * p1_) / 1e8, 49.6, tol=0.05)
    assert math.isclose(cap, 4.96)
    quoted("8 / 0.16 (100 mL)", bought / (pct / 100) / 100, 50, tol=1e-9)
    quoted("King's shares bought back", F["velde_feb22"][0], 100_000, tol=1e-9)
    quoted("  at (L)", F["velde_feb22"][1], 9000, tol=1e-9)
    quoted("market price fell from (L)", F["velde_8500"][0], 9925, tol=1e-9)
    quoted("  to (L) by March 1", F["velde_8500"][1], 8500, tol=1e-9)
    quoted("silver coin from (L)", F["velde_devalue"][0], 1, tol=1e-9)
    quoted("  to (L): devalued by a third", F["velde_devalue"][1], 1.5, tol=1e-9)
    assert math.isclose(1 - 1 / 1.5, 1 / 3)
    spent, pct27 = F["velde_1213"]
    quoted("spent Mar-May 1720 (100 mL)", spent / 100, 12.135, tol=1e-9)
    quoted("  share of stock (%)", pct27, 27, tol=1e-9)
    quoted("  shares at 9000 (10k)", peg_money(1, spent * 1e6 / 9000) / 1e4, 13.5, tol=0.05)
    rise = T.loc["1720-05-31", "col1"] - T.loc["1720-03-05", "col1"]
    quoted("Table 4: 5 Mar (100 mL)", T.loc["1720-03-05", "col1"] / 100, 10.899, tol=1e-9)
    quoted("Table 4: 31 May (100 mL)", T.loc["1720-05-31", "col1"] / 100, 22.351, tol=1e-9)
    quoted("  increase (100 mL)", rise / 100, 11.452, tol=1e-9)
    quoted("Garber: denomination of the share-notes (L)", F["garber_9000note"][0], 9000, tol=1e-9)

    print("\n== fig:merc_notes ==")
    quoted("col (1) max (100 mL)", T["col1"].max() / 100, 23.59, tol=1e-9)
    assert T["col1"].idxmax() == pd.Timestamp("1720-06-30")
    quoted("col (4) max (100 mL)", T["col4"].max() / 100, 16.255, tol=1e-9)
    assert T["col4"].idxmax() == pd.Timestamp("1720-05-31")
    quoted("col (4) 8 Jan 1721 (mL)", T.loc["1721-01-08", "col4"], 46.6, tol=1e-9)
    quoted("silver standard (L per marc)", F["velde_t4_cols"][0], 60, tol=1e-9)
    assert (T.loc[:"1720-03-05", "deflator"].round(3) >= 1).all()             # the lines coincide before March 1720
    quoted("deflator 31 Mar 1720 (1 - 1/3)", T.loc["1720-03-31", "deflator"], 2 / 3, tol=0.0005)

    print("\n== case: 21 May ==")
    quoted("notes to half by 1 December (%)", 50, 50, tol=1e-9)
    plan, notes, stock = F["garber_23bn"]
    quoted("Garber: paper left by December (bn)", plan, 2.3, tol=1e-9)
    quoted("  notes", notes, 1.3, tol=1e-9)
    quoted("  stock", stock, 1, tol=1e-9)
    assert math.isclose(notes + stock, plan)
    m = S["mississippi"]
    quoted("price 16 May 1720 (L)", m.loc["1720-05-16"], 9005, tol=1e-9)
    quoted("  28 May", m.loc["1720-05-28"], 6075, tol=1e-9)
    quoted("  30 May", m.loc["1720-05-30"], 4000, tol=1e-9)
    quoted("notes in 1719 silver 31 May (100 mL)", T.loc["1720-05-31", "col4"] / 100, 16.255, tol=1e-9)
    quoted("  30 Jun", T.loc["1720-06-30", "col4"] / 100, 11.903, tol=1e-9)
    quoted("  31 Jul", T.loc["1720-07-31", "col4"] / 100, 5.152, tol=1e-9)
    quoted("  fall in two months (%) -- 'two thirds'", 100 * (1 - T.loc["1720-07-31", "col4"] / T.loc["1720-05-31", "col4"]),
           68.3, tol=0.05)
    quoted("Law's real estate at least (100k L)", F["velde_realestate"][0] * 10, 95, tol=1e-9)

    print("\n== the Visa ==")
    issued, visa, rest = F["velde_2800"]
    quoted("notes issued (100 mL)", issued / 100, 28, tol=1e-9)
    quoted("  into the Visa (100 mL)", visa / 100, 22, tol=1e-9)
    sub, red, avg = F["velde_visa"]
    quoted("submitted (100 mL)", sub / 100, 22.112, tol=1e-9)
    quoted("  reduced to (100 mL)", red / 100, 17, tol=1e-9)
    quoted("  average reduction, Velde (%)", avg, 23.5, tol=1e-9)
    quoted("  computed (%)", 100 * (1 - red / sub), 23.1, tol=0.05)
    small, share_sum, cut = F["velde_visa_small"]
    quoted("small claims up to (L)", small, 500, tol=1e-9)
    quoted("  share of sums (%)", share_sum, 40, tol=1e-9)
    quoted("  remaining 60% cut by (%)", cut, 39, tol=1e-9)
    quoted("  60% x 39% (%)", (100 - share_sum) * cut / 100, 23.4, tol=1e-9)
    tax, rest15, life, perp = F["velde_visa_1500"]
    quoted("tax on about 200 people (mL)", tax, 190, tol=1e-9)
    quoted("  rest about (100 mL)", rest15 / 100, 15, tol=1e-9)
    quoted("  1700 - 190 (mL)", red - tax, 1510, tol=1e-9)
    quoted("  life annuities at (%)", life, 4, tol=1e-9)
    quoted("  perpetual at (%)", perp, 2, tol=1e-9)
    quoted("certificates worth in 1722 (%)", F["velde_visa_25"][0], 25, tol=1e-9)
    quoted("average holder got (%)", F["velde_visa_20"][1], 20, tol=1e-9)


def southsea(F, S):
    print("\n== sec:merc-southsea ==")
    quoted("ten voyages", F["smith_ss_ship"][0], 10, tol=1e-9)
    quoted("  gained by one (Royal Caroline 1731)", F["smith_ss_ship"][1], 1, tol=1e-9)
    pay, debt = F["garber_31m"]
    quoted("debt in noncorporate hands (GBP m)", debt, 31, tol=1e-9)
    quoted("  pay up to (GBP m)", pay, 7.5, tol=1e-9)
    long_, short, per = F["garber_terms"]
    quoted("par per 100/yr long annuity", long_, 2000, tol=1e-9)
    quoted("  short", short, 1400, tol=1e-9)
    quoted("  per 100 redeemables", per, 100, tol=1e-9)
    quoted("interest until 1727 (%)", F["garber_5pct"][0], 5, tol=1e-9)
    quoted("  thereafter (%)", F["garber_5pct"][1], 4, tol=1e-9)
    quoted("bribes (10k GBP)", F["garber_bribes"][0] * 100, 130, tol=1e-9)
    quoted("par before (10k GBP)", F["garber_par"][0] * 100, 1170, tol=1e-9)
    quoted("par after (10k GBP)", F["garber_par"][1] * 100, 2280, tol=1e-9)

    print("\n== ex:merc-offer ==")
    _, par700, cash, price, value, market = F["garber_offer"]
    n = par700 / 100
    quoted("offer value at 400", n * price + cash, value, tol=1e-9)
    quoted("  more than twice the annuity", (n * price + cash) / market, 2.11, tol=0.005)
    be = (market - cash) / n
    quoted("break-even share price", be, F["garber_offer_1600"][1], tol=0.5)
    left = long_ - par700
    quoted("par left (GBP)", left, 1300, tol=1e-9)
    quoted("  shares left", left / 100, 13, tol=1e-9)
    quoted("  worth at 400", left / 100 * price, 5200, tol=1e-9)

    print("\n== the price path ==")
    lo, a, b = F["garber_120"]
    quoted("Jan 1720 about", lo, 120, tol=1e-9)
    quoted("  21 March from", a, 200, tol=1e-9)
    quoted("  to", b, 300, tol=1e-9)
    par5, n3, p3, jump0, jump1 = F["garber_third"]
    quoted("third subscription par (GBP m)", par5, 5, tol=1e-9)
    quoted("  shares", n3, 50_000, tol=1e-9)
    assert n3 * 100 == par5 * 1e6
    quoted("  at (GBP)", p3, 1000, tol=1e-9)
    quoted("  jump from", jump0, 745, tol=1e-9)
    quoted("  to", jump1, 950, tol=1e-9)
    pk, scott, div = F["garber_peak"]
    quoted("Neal's peak", pk, 950, tol=1e-9)
    quoted("Scott's peak", scott, 1050, tol=1e-9)
    quoted("  stock dividend (%)", div, 10, tol=1e-9)
    irr, red = F["garber_acquired"]
    quoted("acquired irredeemables (%)", irr, 80, tol=1e-9)
    quoted("acquired redeemables (%)", red, 85, tol=1e-9)
    hi, lo = F["garber_collapse"]
    quoted("31 Aug (about)", hi, 775, tol=1e-9)
    quoted("1 Oct (about)", lo, 290, tol=1e-9)
    n, mv, gone = F["garber_164"]
    quoted("shares", n, 212_012, tol=1e-9)
    quoted("  x 775 (100m GBP)", n * hi / 1e8, 1.64, tol=0.005)
    quoted("  x (775 - 290) (100m GBP)", n * (hi - lo) / 1e8, 1.03, tol=0.005)
    assert n * (hi - lo) / 1e6 > 2 * F["garber_debt50"][0]
    quoted("directors' wealth (GBP m)", F["garber_stripped"][0], 2, tol=1e-9)
    quoted("forgiven (10k GBP)", F["garber_forgave"][1] * 100, 710, tol=1e-9)

    print("\n== case: the Bank of England ==")
    quoted("small coins (sols)", F["cant_sols"][0], 6, tol=1e-9)
    quoted("  and", F["cant_sols"][1], 12, tol=1e-9)

    print("\n== fig:merc_shares (b) ==")
    ss = S["south_sea"].dropna()
    quoted("South Sea first quotation Aug 1719", ss.iloc[0], 113, tol=1e-9)
    assert ss.index[0] == pd.Timestamp("1719-08-21")
    quoted("  max", ss.max(), 950, tol=1e-9)
    peak_days = ss[ss == ss.max()].index
    assert list(S.loc[peak_days, "date_julian"]) == ["1720-06-29", "1720-06-30", "1720-07-01"]
    quoted("  early December", last_on_or_before(ss, "1720-12-06"), 185, tol=1e-9)
    quoted("East India max", S["old_east_india"].max(), 420, tol=1e-9)
    quoted("South Sea 1 Jan 1720 (Julian)", julian(S, "1720-01-01", "south_sea"), 128.375, tol=1e-9)
    quoted("South Sea 31 Aug 1720 (Julian) in the data", julian(S, "1720-08-31", "south_sea"), 810, tol=1e-9)
    quoted("South Sea 1 Oct 1720 (Julian)", julian(S, "1720-10-01", "south_sea"), 290, tol=1e-9)
    assert all((d - pd.Timestamp(j)).days == JULIAN_LAG_DAYS for d, j in S["date_julian"].dropna().items())


def fig_shares_a(S, T):
    print("\n== fig:merc_shares (a) ==")
    m = S["mississippi"].dropna()
    quoted("first quotation 6 Aug 1718 (L)", m.iloc[0], 273.75, tol=1e-9)
    assert m.index[0] == pd.Timestamp("1718-08-06")
    quoted("max (L)", m.max(), 10_100, tol=1e-9)
    assert m.idxmax() == pd.Timestamp("1720-01-08")
    peg = m.loc[PEG_DATES[0]:"1720-05-16"]
    quoted("pegged 5 Mar - 16 May: median quote ('near 9000')", peg.median(), 9000, tol=1e-9)
    quoted("  lowest", peg.min(), 8450, tol=1e-9)
    quoted("  highest", peg.max(), 9060, tol=1e-9)
    assert (abs(peg / 9000 - 1) < 0.07).all()
    sp = silver_price(S, T)
    quoted("in 1719 silver: 5 Mar 1720", sp.loc["1720-03-05"], 9000, tol=0.5)
    quoted("  31 Mar 1720", sp.loc["1720-03-31"], 6000, tol=0.5)
    quoted("  31 May 1720", sp.loc["1720-05-31"], 2982, tol=0.5)
    quoted("  27 Nov 1720 (price of 25 Nov)", sp.loc["1720-11-27"], 300, tol=1)
    assert sp.loc["1720-11-27"] < 1.25 * F_cache["velde_40fold"][0]     # 'back near the level of 1718'


def cantillon_sec(F):
    print("\n== sec:merc-cantillon ==")
    quoted("Essai published 1755, after Cantillon's death in 1734 (years)", 1755 - 1734, 21, tol=1e-9)
    c = cantillon(**CANTILLON)
    quoted("ex: price level x", c["price"], 1.25, tol=1e-9)
    quoted("ex: one month +25%: purchasing power lost (%)", 100 * (1 - 1 / (1 + F["velde_hamilton"][0] / 100)), 20, tol=1e-9)
    quoted("ex: B share before", c["sB"], 0.8, tol=1e-9)
    quoted("ex: B share after", c["sB1"], 0.64, tol=1e-9)
    quoted("ex: B real loss (%)", 100 * (1 - c["sB1"] / c["sB"]), 20, tol=1e-9)
    quoted("  = dM/(M + dM) (%)", 100 * CANTILLON["dM"] / (CANTILLON["M"] + CANTILLON["dM"]), 20, tol=1e-9)
    quoted("ex: A share after", c["sA1"], 0.36, tol=1e-9)
    quoted("ex: A real gain (%)", 100 * (c["sA1"] / c["sA"] - 1), 80, tol=1e-9)
    jan, rise, mult = F["velde_hamilton"]
    quoted("Jan-Aug 1720: money x", mult, 2.6, tol=1e-9)
    quoted("  prices (%)", rise, 19, tol=1e-9)
    quoted("  V / Y = P / M fell to (%)", 100 * (1 + rise / 100) / mult, 46, tol=0.5)
    i0, i1, i2 = F["cant_1720"]
    quoted("1720 interest before (%)", i0, 5, tol=1e-9)
    quoted("  raised to (%)", i1, 50, tol=1e-9)
    quoted("  and (%)", i2, 60, tol=1e-9)


def tableau_sec(F):
    print("\n== sec:merc-tableau ==")
    quoted("Dupont: December 1758", F["oncken_1758"][0], 1758, tol=1e-9)
    quoted("Mirabeau: 1759", F["oncken_1759"][0], 1759, tol=1e-9)
    quoted("Analyse: June 1766", 1766, 1766, tol=1e-9)
    quoted("reproduction (bn L)", F["ques_5"][0], 5, tol=1e-9)
    quoted("three classes", F["ques_classes"][0], 3, tol=1e-9)
    A, X, R = F["ques_avances"]
    quoted("annual advances", A, 2, tol=1e-9)
    quoted("  produce", X, 5, tol=1e-9)
    quoted("  net product", R, 2, tol=1e-9)
    rev, to_prod, to_ster = F["ques_revenu"]
    quoted("proprietors' revenue", rev, 2, tol=1e-9)
    quoted("  spent on the productive class", to_prod, 1, tol=1e-9)
    quoted("  on the sterile class", to_ster, 1, tol=1e-9)
    quoted("sterile advances", F["ques_sterile_adv"][0], 1, tol=1e-9)
    quoted("purchases from the productive class", F["ques_3"][0], 3, tol=1e-9)
    got, rent, works = F["ques_pays"]
    quoted("  rent owed", rent, 2, tol=1e-9)
    quoted("  works bought", works, 1, tol=1e-9)
    sales, food = F["ques_sterile_2"]
    quoted("sterile sales", sales, 2, tol=1e-9)
    quoted("  subsistence", food, 1, tol=1e-9)
    tot, bought, kept, w, fund = F["ques_reste2"]
    quoted("fund of the productive class", kept + w, fund, tol=1e-9)
    orig, I, rate = F["ques_interets"]
    quoted("original advances", orig, 10, tol=1e-9)
    quoted("  five times the annual", orig / A, 5, tol=1e-9)
    quoted("  interest", I, 1, tol=1e-9)
    quoted("  rate (%)", 100 * I / orig, rate, tol=1e-9)
    quoted("reproduction rate (%)", 100 * X / A, F["ques_250"][0], tol=1e-9)
    T = tableau()
    for k, v in [("productive", 3), ("proprietors", 2), ("sterile", 2)]:
        quoted(f"tab: {k} receives", receipts(T, k), v, tol=1e-9)
        quoted(f"tab: {k} pays", payments(T, k), v, tol=1e-9)
    quoted("tab: total payments", sum(payments(T, k) for k in CLASSES), 7, tol=1e-9)
    quoted("X = A + I + R", A + I + R, X, tol=1e-9)
    assert receipts(T, "productive") == F["ques_3"][0]
    # ex:merc-tableau
    s572, s1144, s286 = F["ques_shares"]
    quoted("sovereign 2/7 of 2000 (m)", 2000 * 2 / 7, 571.4, tol=0.05)
    quoted("  printed", s572, 572, tol=1e-9)
    quoted("proprietors 4/7 (m)", 2000 * 4 / 7, 1142.9, tol=0.05)
    quoted("  printed", s1144, 1144, tol=1e-9)
    quoted("tithe 1/7 (m)", 2000 / 7, 285.7, tol=0.05)
    quoted("  printed", s286, 286, tol=1e-9)
    quoted("  printed sum (m)", s572 + s1144 + s286, 2002, tol=1e-9)
    quoted("luxury example (L)", F["ques_luxe"][0], 100, tol=1e-9)
    T2 = tableau(LUXURY_SHIFT)
    quoted("ex: proprietors' food (100m L)", T2["proprietors"]["productive"] * 10, 8, tol=1e-9)
    quoted("ex: productive class receives (bn L, from 3)", receipts(T2, "productive"), 2.8, tol=1e-9)
    quoted("ex: left after the rent for works (100m L)", (receipts(T2, "productive") - 2) * 10, 8, tol=1e-9)
    quoted("wheat (L per septier)", F["ques_ble"][0], 18, tol=1e-9)


def test(F):
    print("\n== sec:merc-test ==")
    t10 = {k: F[f"velde_t10_{k}"] for k in ["debt", "farms", "rec", "mints", "tob", "trade", "total"]}
    for j, name in enumerate(["Law (1)", "Law (2)", "Dutot", "Velde"]):
        s = sum(t10[k][j] for k in ["debt", "farms", "rec", "mints", "tob", "trade"])
        quoted(f"Table 10 {name} total", s, t10["total"][j], tol=1e-9)
    E = t10["total"][3]
    quoted("Velde's earnings (mL)", E, 75.5, tol=1e-9)
    quoted("per share on 600,000 (L)", E * 1e6 / 600_000, 125.8, tol=0.05)
    quoted("  Velde: dividend down to", F["velde_125"][0], 125, tol=1e-9)
    # ex:merc-gordon
    lo, hi, avg = F["velde_pd15"]
    quoted("P/D 1723-69 low", lo, 4, tol=1e-9)
    quoted("  high", hi, 24, tol=1e-9)
    quoted("  average", avg, 15, tol=1e-9)
    rev, fac, val, price, peak, over = F["velde_back"]
    quoted("75.5 x 15 (mL)", E * avg, val, tol=0.5)
    quoted("  per share (L)", price, 1875, tol=1e-9)
    quoted("  implied shares (10k)", val * 1e6 / price / 1e4, 60, tol=0.5)
    quoted("  9000 / 1875", peak / price, 4.8, tol=1e-9)
    assert round(peak / price) == over
    cap = 300_000 * 9925 + 300_000 * 6600
    quoted("r - g for the market value (%)", 100 * E * 1e6 / cap, 1.5, tol=0.05)
    r, g, f2 = F["velde_dutch"]
    quoted("  Dutch rate (%)", r, 3, tol=1e-9)
    quoted("  growth (%)", g, 1.5, tol=1e-9)
    quoted("  Gordon 75.5/(3% - 1.5%) (mL)", gordon(E, r / 100, g / 100), 5033, tol=0.5)
    quoted("  Dutch rate alone (mL)", gordon(E, r / 100), 2517, tol=0.5)
    quoted("  overvalued x", cap / 1e6 / gordon(E, r / 100), 1.97, tol=0.005)
    quoted("  Velde: factor of", f2, 2, tol=1e-9)
    quoted("fiscal revenue growth 1726-1789 (%)", F["velde_growth"][0], 0.6, tol=1e-9)
    quoted("GDP growth (%)", F["velde_growth"][1], 0.5, tol=1e-9)
    d125 = F["velde_pe22"][1]
    quoted("125 / 3% (L)", gordon(d125, 0.03), 4167, tol=0.5)
    quoted("125 / (3% - 0.5%) (L)", gordon(d125, 0.03, GROWTH_GDP), 5000, tol=1e-6)
    quoted("  Velde: about (L)", F["velde_pe22"][3], 5000, tol=1e-9)
    quoted("Gordon: r - g from 3% to 1.5% doubles the price", gordon(1, 0.03, 0.015) / gordon(1, 0.03), 2, tol=1e-9)
    # Garber's South Sea fundamentals
    v = garber_value()
    quoted("market value Sep 1720 (GBP m)", F["garber_164sep"][0], 164, tol=1e-9)
    mv, f1, yr, f2_, rate, about = F["garber_fund"]
    quoted("claim a year until 1727 (GBP m)", f1, 1.9, tol=1e-9)
    quoted("  thereafter", f2_, 1.5, tol=1e-9)
    quoted("  discount rate (%)", rate, 4, tol=1e-9)
    quoted("annuity part (GBP m)", annuity(f1, rate / 100, 1727 - 1720), 11.4, tol=0.05)
    quoted("perpetuity part (GBP m)", (f2_ / 0.04) / 1.04 ** 7, 28.5, tol=0.05)
    quoted("value (GBP m; Garber about 40)", v, 39.9, tol=0.05)
    pay, bonds, net, loans, subs, excess = F["garber_net"]
    quoted("  less 7.1 and 6 (GBP m) -- Garber 26.1", v - pay - bonds, 26.8, tol=0.05)
    quoted("  Garber's net asset value", net, 26.1, tol=1e-9)
    quoted("  164 - 26.1 - 11 - 70", mv - net - loans - subs, 56.9, tol=0.05)
    quoted("  Garber: more than", excess, 60, tol=1e-9)
    quoted("  164 / 26.1 (five times or more)", mv / net, 6.3, tol=0.05)
    assert mv / net >= F["garber_five"][0]
    quoted("Scott: 400 not excessive", F["garber_scott400"][0], 400, tol=1e-9)
    # FGR
    quoted("Atlantic firms rose by factors of (low)", F["fgr_7to10"][0], 7, tol=1e-9)
    quoted("  (high)", F["fgr_7to10"][1], 10, tol=1e-9)
    for k, v_ in [("ins", 2013), ("atl", 895), ("pac", 349), ("bank", 335), ("total", 1172)]:
        quoted(f"Table 1 {k} (%)", F[f"fgr_t1_{k}"][0], v_, tol=1e-9)
    quoted("  number of firms", F["fgr_t1_total"][2], 45, tol=1e-9)
    quoted("Dutch average (%)", F["fgr_dutch127"][0], 127, tol=1e-9)
    # Temin & Voth
    profit, income = F["tv_hoare"]
    quoted("Hoare's profit (GBP)", profit, 28_000, tol=1e-9)
    quoted("  comfortable income (GBP)", income, 200, tol=1e-9)
    quoted("  years of income", profit / income, 140, tol=1e-9)


def deeper(F, S, T):
    print("\n== deeper ==")
    quoted("billets: 37% gives (L, about 900)", 312.5 + 937.5 * (1 - 0.37), 903, tol=0.5)
    e1, e2, e3, e4 = F["garber_expansions"]
    quoted("Garber's four issues (100 mL)", (e1 + e2 + e3 + e4) / 100, 14.9, tol=1e-9)
    quoted("January 1720: Velde (%)", F["velde_hamilton"][0], 25, tol=1e-9)
    quoted("  Garber (%)", F["garber_inflation"][1], 23, tol=1e-9)
    quoted("Visa computed (%)", 100 * (1 - F["velde_visa"][1] / F["velde_visa"][0]), 23.1, tol=0.05)
    quoted("Garber's 40m computed (10k GBP)", garber_value() * 100, 3990, tol=5)
    quoted("days between the calendars", F["fgr_calendar"][0], JULIAN_LAG_DAYS, tol=1e-9)
    # Garber's "745 to 950" against the price data (London dates, Julian)
    quoted("Garber: jumped from", F["garber_745"][0], 745, tol=1e-9)
    quoted("  to", F["garber_745"][1], 950, tol=1e-9)
    quoted("South Sea 10 Jun 1720 in the data", julian(S, "1720-06-10", "south_sea"), 745, tol=1e-9)
    quoted("  17 Jun", julian(S, "1720-06-17", "south_sea"), 755, tol=1e-9)
    j, ss = S["date_julian"], S["south_sea"]
    quoted("  highest 17-22 Jun", ss[(j >= "1720-06-17") & (j <= "1720-06-22")].max(), 765, tol=1e-9)
    assert ss[(j >= "1720-06-23") & (j <= "1720-06-28")].isna().all(), "no quotations 23-28 June"
    first950 = ss[ss == 950].index[0]
    assert S.loc[first950, "date_julian"] == "1720-06-29"
    assert S.loc[first950, "date_julian"] >= "1720-06-24", "after the transfer books closed"
    # what the company was to pay the government: up to 7.5m (if it took all 31m), 7.1m in the accounts
    quoted("pay up to (GBP m)", F["garber_31m"][0], 7.5, tol=1e-9)
    quoted("  in the net assets and the settlement (GBP m)", F["garber_net"][0], 7.1, tol=1e-9)
    assert F["garber_forgave"][1] == F["garber_net"][0]


def takeaways(F, T):
    print("\n== takeaways ==")
    quoted("notes lost in two months after 21 May (fraction)", 1 - T.loc["1720-07-31", "col4"] / T.loc["1720-05-31", "col4"],
           2 / 3, tol=0.02)


def selfcheck():
    print("\n== selfcheck ==")
    quoted("1. goods only (10k GBP)", 300 - 340, -40, tol=1e-9)
    quoted("   with freight", 300 - 340 + 30, -10, tol=1e-9)
    e = 4000e4 / 200_000
    quoted("2. earnings per share (L)", e, 200, tol=1e-9)
    quoted("   minimum price (L)", e * pe_threshold(0.05), 4000, tol=1e-9)
    quoted("   200,000 x 5000 (bn L)", 200_000 * 5000 / 1e9, 1, tol=1e-9)
    quoted("   cost (%)", 100 * 4000e4 / 1e9, 4, tol=1e-9)
    dm = peg_money(8000, 50_000)
    quoted("3. new notes (100 mL)", dm / 1e8, 4, tol=1e-9)
    quoted("   prices (%)", 100 * dm / 1e9, 40, tol=1e-9)
    quoted("4. break-even (GBP)", (1500 - 500) / 6, 166.7, tol=0.05)
    quoted("   at 300", 6 * 300 + 500, 2300, tol=1e-9)
    quoted("5. price (L)", gordon(150, 0.04, 0.01), 5000, tol=1e-6)
    quoted("   no growth", gordon(150, 0.04), 3750, tol=1e-6)
    quoted("   r - g at 9000 (%)", 100 * 150 / 9000, 1.7, tol=0.05)
    c = cantillon(200, 50, 50)
    quoted("6. loss (%)", 100 * (1 - c["sB1"] / c["sB"]), 20, tol=1e-9)
    quoted("   B share before", c["sB"], 0.75, tol=1e-9)
    quoted("   after", c["sB1"], 0.6, tol=1e-9)
    quoted("   A share before", c["sA"], 0.25, tol=1e-9)
    quoted("   after", c["sA1"], 0.4, tol=1e-9)


def from_quotes(Q):
    print("\n== numbers read straight from the quotations ==")
    said(Q, "velde_minister", "January 5, 1720")
    said(Q, "velde_four_stages", "May 1716", "December 1720")
    said(Q, "velde_left", "early December 1720")
    said(Q, "mun_written", "1630", "1664")
    said(Q, "mun_1615", "1615")
    said(Q, "mun_discourse", "1621")
    said(Q, "mun_ex_export", "twenty two hundred thousand pounds")
    said(Q, "mun_ex_import", "twenty hundred thousand pounds")
    said(Q, "mun_ex_gain", "two hundred thousand pounds")
    said(Q, "mun_pepper_home", "two Shillings")
    said(Q, "mun_pepper_ams", "twenty pence")
    said(Q, "mun_pepper_indies", "three pence")
    said(Q, "law_acre", "Number 100", "20 years", "Number 2000")
    said(Q, "velde_690", "690L")
    said(Q, "velde_quarter", "1/4")
    said(Q, "velde_bank_taxes", "April 10, 1717")
    said(Q, "velde_royal", "5,000L")
    said(Q, "velde_dec4", "Dec. 4, 1718")
    said(Q, "mun_dearer", "plenty of mony", "dearer")
    said(Q, "cant_outflow", "chez l’Etranger")
    said(Q, "smith_assiento", "Assiento", "Utrecht")
    said(Q, "smith_barren", "barren and unproductive")
    said(Q, "velde_daughters", "June", "July", "four mothers and one daughter")
    said(Q, "velde_fn19", "second issue or daughters", "third issue or granddaughters")
    said(Q, "velde_forfeit", "missing an installment", "options on shares")
    said(Q, "velde_west_aug", "August 1717")
    said(Q, "velde_louisiana", "1717", "500")
    said(Q, "velde_ipo_closed", "Dec 31, 1718", "100mL", "40%")
    said(Q, "velde_tobacco", "Aug. 1, 1718", "4.02mL")
    said(Q, "velde_mints", "Jul. 25, 1719", "50mL", "nine years")
    said(Q, "velde_farms", "Aug. 27, 1719", "30%")
    said(Q, "velde_farms_lease", "52mL", "48.5mL")
    said(Q, "velde_recettes", "late Aug 1719", "55%")
    said(Q, "velde_issue2", "June 1719", "50,000", "550L")
    said(Q, "velde_issue3", "July 1719", "50,000", "1,000L")
    said(Q, "velde_issue4", "Sep–Oct 1719", "300,000", "5,000L")
    said(Q, "velde_mothers", "four mothers and one daughter")
    said(Q, "velde_conv_date", "1200mL", "Sept. 17", "Oct. 10", "1600mL", "3%")
    said(Q, "velde_conv_48", "36mL", "48mL", "52mL")
    said(Q, "velde_3600", "August 26", "3600L", "September 9", "5350L")
    said(Q, "velde_500ml", "500mL", "5000L", "September 26", "October 2", "1000mL")
    said(Q, "velde_swap", "4.5%", "3%")
    said(Q, "velde_90pct", "90%")
    said(Q, "velde_fig6_90", "90mL")
    said(Q, "velde_fig6_48", "48mL")
    said(Q, "velde_pe22", "higher than 22", "125L", "3%", "5000L", "September 1719")
    said(Q, "velde_t6_jul19", "60", "26 Jul 1719", "250,000", "1960", "33")
    said(Q, "velde_t6_dec19", "200", "29 Dec 1719", "600,000", "9413", "47")
    said(Q, "velde_pe45", "200L", "9000L", "45", "2%")
    said(Q, "velde_80ml", "80mL", "200L", "400,000", "100,000")
    said(Q, "velde_notes_1bn", "December 1718", "40mL", "July 1719", "400mL", "1bnL", "January 1720")
    said(Q, "velde_specie", "1200mL")
    said(Q, "velde_640", "Dec. 1, 1719", "640mL", "three months", "tripled")
    said(Q, "velde_500coin", "Feb. 27, 1720", "500L", "100L")
    said(Q, "velde_mar11", "March 11")
    said(Q, "velde_apr1", "Apr. 1, 1720")
    said(Q, "velde_buy5000", "October 5, 1719", "5000L")
    said(Q, "velde_office", "800mL", "16%")
    said(Q, "velde_cap", "300,000", "9925L", "6600L", "4.96bnL")
    said(Q, "velde_feb22", "100,000", "9000L")
    said(Q, "velde_8500", "9925L", "8500L", "March 1")
    said(Q, "velde_peg", "March 5", "9,000L")
    said(Q, "velde_devalue", "March 5", "1/3", "1L", "1.5L")
    said(Q, "velde_1213", "March to late May 1720", "1213.5mL", "27%")
    said(Q, "velde_may21", "9000L", "5000L", "a half", "December 1")
    said(Q, "velde_may27", "May 27", "May 21")
    said(Q, "velde_suspend", "July 17, 1720")
    said(Q, "velde_realestate", "9.5mL")
    said(Q, "velde_2800", "2800mL", "2200mL")
    said(Q, "velde_visa", "2211.2mL", "1700mL", "23.5%")
    said(Q, "velde_visa_small", "500L", "half", "40%", "60%", "39%")
    said(Q, "velde_visa_1500", "two hundred", "190mL", "1500mL", "4%", "2%")
    said(Q, "velde_visa_20", "20%", "March 1722", "November 1720")
    said(Q, "velde_visa_25", "25%", "1722")
    said(Q, "velde_hamilton", "January 1720", "+25%", "19%", "August 1720", "2.6")
    said(Q, "velde_40fold", "1718", "250L")
    said(Q, "velde_40fold_b", "10,000L", "January 1720")
    said(Q, "velde_pd15", "4 and 24", "15")
    said(Q, "velde_back", "75.5mL", "15", "1132mL", "1875L", "9000L", "factor of 5")
    said(Q, "velde_dutch", "3%", "1.5%", "factor of 2")
    said(Q, "velde_growth", "0.6%", "1726", "1789", "0.5%")
    said(Q, "velde_125", "125L")
    said(Q, "velde_1722", "1722")
    said(Q, "velde_t10_total", "91 80 80.5 75.5")
    said(Q, "garber_debt50", "50 million", "18.3 million", "3.4 million", "3.2 million", "11.7 million", "16.5 million")
    said(Q, "garber_irred", "15 million", "72 and 87 years", "22 years")
    said(Q, "garber_31m", "7.5 million", "31 million")
    said(Q, "garber_terms", "100 pounds per year", "2000 pounds", "1400 pounds", "100 pound par value")
    said(Q, "garber_5pct", "5 percent", "1727", "4 percent")
    said(Q, "garber_bribes", "1.3 million")
    said(Q, "garber_par", "11.7 million", "22.8 million")
    said(Q, "garber_120", "120 pounds", "January 1720", "March 21", "200 to 300")
    said(Q, "garber_offer", "700 pounds", "7 shares", "575 pounds", "400 pounds", "3375 pounds")
    said(Q, "garber_offer_1600", "1600 pounds", "146 pounds")
    said(Q, "garber_third", "June 17, 1720", "5 million", "50,000 shares", "1000 pounds")
    said(Q, "garber_745", "745 to 950")
    said(Q, "garber_books", "June 24 to August 22")
    said(Q, "garber_peak", "950 on July 1", "1050", "10 percent")
    said(Q, "garber_acquired", "80 percent", "85 percent")
    said(Q, "garber_bubbleact", "June 1720")
    said(Q, "garber_aug18", "August 18, 1720")
    said(Q, "garber_collapse", "775 on August 31", "290 on October 1, 1720")
    said(Q, "garber_164", "212,012", "164 million", "103 million", "twice")
    said(Q, "garber_164sep", "September 1720", "164 million")
    said(Q, "garber_fund", "1.9 million", "1727", "1.5 million", "4 percent", "40 million")
    said(Q, "garber_net", "7.1 million", "6 million", "26.1 million", "11 million", "70 million", "60 million")
    said(Q, "garber_five", "five times")
    said(Q, "garber_stripped", "2 million")
    said(Q, "garber_forgave", "7.1 million")
    said(Q, "garber_june1716", "June 1716")
    said(Q, "garber_9000note", "9000 livres")
    said(Q, "garber_expansions", "300 million", "390 million", "438 million", "362 million", "one month")
    said(Q, "garber_inflation", "4 percent", "23 percent", "January 1720", "116.1", "203.7")
    said(Q, "garber_toohigh", "May 21, 1720")
    said(Q, "garber_23bn", "2.3 billion", "1.3 billion", "1 billion")
    said(Q, "garber_thrown", "end of May 1720")
    said(Q, "garber_scott400", "400")
    said(Q, "smith_ss_ship", "ten voyages", "1731")
    said(Q, "tv_hoare", "£28,000", "£200")
    said(Q, "tv_goldsmith", "goldsmith", "1690")
    said(Q, "fgr_triangle", "1720")
    said(Q, "fgr_mirror", "1721")
    said(Q, "djt_gaps", "subscription receipts", "wagering markets")
    said(Q, "shea_options", "default options", "eighteenth-century")
    said(Q, "shea_flawed", "Dale, Johnson, and Tang")
    said(Q, "garber_first_passage", "first passage", "March 21, 1720")
    said(Q, "fgr_7to10", "7 to 10")
    said(Q, "fgr_t1_ins", "2013%")
    said(Q, "fgr_t1_atl", "895%")
    said(Q, "fgr_t1_pac", "349%")
    said(Q, "fgr_t1_bank", "335%")
    said(Q, "fgr_t1_total", "1172%", "45")
    said(Q, "fgr_dutch127", "127%")
    said(Q, "fgr_insurers", "August 26th [G]", "27th [G]")
    said(Q, "fgr_ss_crash", "September 19[G]")
    said(Q, "fgr_calendar", "eleven")
    said(Q, "cant_1720", "cinq pour cent", "cinquante & soixante pour cent")
    said(Q, "cant_sols", "six & de douze sols")
    said(Q, "cant_run", "mil sept cent vingt")
    said(Q, "cant_bank1720", "mil sept cent vingt")
    said(Q, "ques_source", "juin 1766", "p. 11 - 41")
    said(Q, "ques_5", "cinq milliards")
    said(Q, "ques_classes", "trois classes")
    said(Q, "ques_avances", "deux milliards", "cinq milliards")
    said(Q, "ques_revenu", "deux milliards", "un milliard", "l’autre milliard")
    said(Q, "ques_sterile_adv", "un milliard")
    said(Q, "ques_3", "3 milliards")
    said(Q, "ques_pays", "trois milliards", "deux milliards", "un milliard")
    said(Q, "ques_sterile_2", "deux milliards", "un milliard")
    said(Q, "ques_reste2", "cinq milliards", "trois milliards", "deux milliards", "un milliard", "trois milliards")
    said(Q, "ques_interets", "deux milliards", "dix milliards", "un milliard", "dix pour cent")
    said(Q, "ques_250", "deux cent cinquante pour cent")
    said(Q, "ques_ble", "18 liv.")
    said(Q, "ques_shares", "572 millions", "quatre septiemes", "144 millions", "septieme", "286 millions")
    said(Q, "ques_luxe", "100 livres")
    said(Q, "oncken_1758", "décembre 1758")


def main():
    global F_cache
    F, Q = facts(), quotes()
    F_cache = F
    T, S, Fr = table4(), shares(), france1715()
    intro(F, T)
    world(F, Fr)
    mun(F)
    law(F)
    system(F, T, S)
    southsea(F, S)
    fig_shares_a(S, T)
    cantillon_sec(F)
    tableau_sec(F)
    test(F)
    deeper(F, S, T)
    takeaways(F, T)
    selfcheck()
    from_quotes(Q)
    print("all numbers in Chapter 16 check out")


F_cache: dict = {}

if __name__ == "__main__":
    main()
