"""Chapter 10 (伊斯兰世界与地中海的商业革命): every number quoted in zh/ch10_islamic.tex.

    python3 checks/check_ch10.py

Inputs are two snapshots: data/snapshots/medieval_credit_facts.csv (quotations from the Muwatta,
Geniza documents, a Venetian contract of 1199, the calendar of the 1442 protest, Bell, Brooks &
Moore 2017, Liber abbaci and others; verified by data/fetch/verify_web_quotes.py) and
data/snapshots/bbm2017_implied_rates.csv (Tables 4 and 5 of Bell, Brooks & Moore).  The figure
module figsrc/fig_ch10.py imports the functions defined here.

Formulas (the chapter's key equations):
    spread            Sp = E_A / E_B - 1               (eq:islamic-spread)
    annualized rate   simple Sp / T, compound (1 + Sp) ** (1 / T) - 1, T in years (eq:islamic-annual)
The compound form is the book's compound average rate (STYLE.md §11) with X_T / X_0 = 1 + Sp.
"""
from __future__ import annotations

import math

from common import load_snapshot, quoted

# Units of account: 1 pound = 20 shillings (soldi) = 240 pence (denari), in England and in the
# Italian moneys of account; Bell, Brooks & Moore subdivide the Venetian ducat the same way
# (their "161 ducats 16 soldi and 4 denari").
PENCE_PER_POUND, PENCE_PER_SHILLING = 240, 12

# Teaching inputs of the partnership example (ex:islamic-commenda); stated in the text.
LOAN_RATE = 0.20                  # interest of a comparison loan for one voyage (the 1199 penalty rate, used only as a reference)
OUTCOMES = (600, 360, 150)        # value brought back to Venice from 300 pounds: +100%, +20%, -50%


def facts() -> dict[str, float]:
    df, _ = load_snapshot("medieval_credit_facts")
    return {r["id"]: float(r["value"]) for _, r in df.iterrows() if r["value"] == r["value"]}


def bbm():
    df, _ = load_snapshot("bbm2017_implied_rates")
    return df


def avg_rate(x0: float, xT: float, years: float) -> float:
    """Compound average rate of change per year (STYLE.md §11)."""
    return (xT / x0) ** (1.0 / years) - 1.0


def spread(e_home: float, e_abroad: float) -> float:
    """eq:islamic-spread: E_A / E_B - 1, both rates in units of the same currency per unit of the other."""
    return e_home / e_abroad - 1.0


def annualized(sp: float, years: float) -> tuple[float, float]:
    """eq:islamic-annual: (simple, compound) annual rates for a spread earned over `years`."""
    return sp / years, (1.0 + sp) ** (1.0 / years) - 1.0


def lsd(pence: float) -> tuple[int, int, float]:
    pounds = int(pence // PENCE_PER_POUND)
    rest = pence - pounds * PENCE_PER_POUND
    shillings = int(rest // PENCE_PER_SHILLING)
    return pounds, shillings, rest - shillings * PENCE_PER_SHILLING


# ---------------------------------------------------------------------------
def suftaja(F):
    quoted("Baghdad deposit = two suftajas (100 + 50 dirhams)", F["pgp39110_bills"] + 50, F["pgp39110_deposit"], tol=0)
    quoted("suftaja for Sahlawayh reduced from 50 to (dirhams)", F["pgp39110_reduce"], 30, tol=0)
    quoted("difference taken back or kept (dirhams)", 50 - F["pgp39110_reduce"], F["pgp39110_desc"], tol=0)


def bill_1442(F):
    """The protested bill of 1442 (CSP Venice vol. 2, p. 568) and its rechange (Bell, Brooks & Moore)."""
    ducats, e_ven, e_lon = F["csp_bill"], F["csp_rate_venice"], F["csp_rate_london"]
    pence = ducats * e_ven
    quoted("1442: sterling due in London (pence)", pence, 6675, tol=1e-9)
    p, s, d = lsd(pence)
    quoted("1442: ... in pounds, shillings, pence (27 16s 3d)", 10000 * p + 100 * s + d, 271603, tol=1e-9)
    back = pence / e_lon
    quoted("1442: ducats owed in Venice after the rechange", back, 161.82, tol=0.005)
    d_s = (back - int(back)) * 20
    quoted("1442: ... = 161 ducats 16 soldi 4 denari (soldi)", int(d_s), 16, tol=0)
    quoted("1442: ... (denari)", int((d_s - int(d_s)) * 12), 4, tol=0)
    sp = spread(e_ven, e_lon)
    quoted("1442: spread (%)", 100 * sp, F["bbm_1442"], tol=0.05)
    quoted("1442: spread of the quotes, 3 1/4 pence", e_ven - e_lon, 3.25, tol=1e-12)
    # deeper box: a lender in London quotes ducats per penny (reciprocals) and earns the same spread
    quoted("lender in London: spread from 1/41.25 and 1/44.5 ducats per penny (%)",
           100 * spread(1 / e_lon, 1 / e_ven), 7.9, tol=0.05)
    assert abs(spread(1 / e_lon, 1 / e_ven) - sp) < 1e-12, "the spread does not depend on the direction"
    quoted("1442: return on the ducats lent (%)", 100 * (back / ducats - 1), 7.9, tol=0.05)
    simple, comp = annualized(sp, 0.5)
    quoted("1442: simple annual rate over six months (%)", 100 * simple, F["bbm_1442_rates"], tol=0.05)
    quoted("1442: compound annual rate (%)", 100 * comp, 16.4, tol=0.05)
    quoted("1442: compound rate = compound average rate of 1 + Sp over half a year (%)",
           100 * avg_rate(1.0, 1.0 + sp, 0.5), 16.4, tol=0.05)
    return sp


def bbm_table(F):
    d = bbm()
    calc = d.spread_pct * 365 / d.term_days
    misprint = (d.city_from == "Bruges") & (d.city_to == "Paris")
    assert ((calc - d.simple_apr_pct)[~misprint].abs() <= 0.06).all(), "simple APR = spread x 365 / term"
    quoted("Bruges->Paris: 1.33% x 365/46 (printed 11.55)", float(calc[misprint].iloc[0]), 10.55, tol=0.01)
    quoted("number of directions", len(d), 28, tol=0)
    pairs = {frozenset((a, b)) for a, b in zip(d.city_from, d.city_to)}
    quoted("number of city pairs", len(pairs), 14, tol=0)
    quoted("matched observations in Table 4", d.observations.sum(), 11549, tol=0)
    quoted("smallest spread (%)", d.spread_pct.min(), 0.79, tol=0)
    quoted("largest spread (%)", d.spread_pct.max(), 6.85, tol=0)
    quoted("largest / smallest spread", d.spread_pct.max() / d.spread_pct.min(), 8.7, tol=0.05)
    quoted("lowest simple annual rate (%)", calc.min(), 9.1, tol=0.05)
    quoted("highest simple annual rate (%)", calc.max(), 15.9, tol=0.05)
    quoted("highest / lowest simple annual rate", calc.max() / calc.min(), 1.7, tol=0.05)
    T = d.term_days / 365
    slope = float((d.spread_pct * T).sum() / (T ** 2).sum())
    quoted("least-squares line through the origin: annual rate (%)", slope, 13.0, tol=0.05)
    row = lambda a, b: d[(d.city_from == a) & (d.city_to == b)].iloc[0]  # noqa: E731
    fv, gl = row("Florence", "Venice"), row("Genoa", "London")
    quoted("Florence->Venice spread (%)", fv.spread_pct, 0.82, tol=0)
    quoted("Florence->Venice round trip (days)", fv.term_days, F["bbm_round_trip"], tol=0)
    quoted("Florence->Venice simple annual rate (%)", fv.spread_pct * 365 / fv.term_days, 10.0, tol=0.05)
    quoted("Genoa->London spread (%)", gl.spread_pct, 6.85, tol=0)
    quoted("Genoa->London term (days)", gl.term_days, 180, tol=0)
    quoted("Genoa->London simple annual rate (%)", gl.spread_pct * 365 / gl.term_days, 13.9, tol=0.05)
    quoted("Genoa->London / Florence->Venice spread", gl.spread_pct / fv.spread_pct, 8.4, tol=0.05)
    quoted("Genoa->London / Florence->Venice simple annual rate (about four tenths higher)",
           (gl.spread_pct / gl.term_days) / (fv.spread_pct / fv.term_days), 1.4, tol=0.05)
    # risk: share of matched transactions with a negative return
    quoted("Florence->Venice negative (81 of 832, %)", 100 * F["bbm_neg_fv"] / 832, 9.7, tol=0.05)
    quoted("... equals Table 5 (%)", fv.negative_return_pct, 9.74, tol=0)
    vf = row("Venice", "Florence")
    quoted("Venice->Florence negative (142 of 769, %)", 100 * 142 / 769, vf.negative_return_pct, tol=0.01)
    quoted("London->Genoa negative (%)", row("London", "Genoa").negative_return_pct, F["bbm_neg_lg"], tol=0)
    quoted("Genoa->London negative (%)", gl.negative_return_pct, 4.5, tol=0.05)
    quoted("Venice->Florence negative (%)", vf.negative_return_pct, 18.5, tol=0.05)
    # §10.7: how much a transaction earns is uncertain on long routes too (Table 5, SD of the spread)
    quoted("Genoa->London SD of the spread (percentage points)", gl.spread_sd_pct, 3.87, tol=0)
    assert gl.spread_sd_pct / gl.spread_pct > 0.5, "Genoa->London: SD of the spread is more than half its mean"
    quoted("Florence->Venice SD of the spread (percentage points)", fv.spread_sd_pct, 0.74, tol=0)
    # §10.4: exchange and rechange gave loans from about one month to six months
    quoted("shortest round trip (days)", d.term_days.min(), 28, tol=0)
    quoted("longest round trip (days, six months)", d.term_days.max(), 180, tol=0)
    short, long_ = d[d.term_days <= 30], d[d.term_days >= 120]
    quoted("directions with terms of 30 days or less", len(short), 4, tol=0)
    quoted("... mean share negative (%)", short.negative_return_pct.mean(), 12.4, tol=0.05)
    quoted("directions with terms of 120 days or more", len(long_), 12, tol=0)
    quoted("... mean share negative (%)", long_.negative_return_pct.mean(), 4.7, tol=0.05)
    return d, slope


def other_rates(F):
    # monti: a coupon on par becomes a higher yield at a price below par
    quoted("Florentine coupon 5% at 50% of par: current yield (%)", 100 * 0.05 / 0.50, 10.0, tol=1e-9)
    quoted("Florentine coupon 3.75% at 60% of par: current yield (%)", 100 * 0.0375 / 0.60, 6.25, tol=1e-9)
    quoted("Datini's investment in six companies (florins)", F["bbm_datini_invest"], 26000, tol=0)


def commenda(F):
    """ex:islamic-commenda: the 1199 colleganza against a loan, with teaching inputs."""
    K, s_inv = F["pt_1199_capital"], F["pt_1199_share"]
    quoted("1199: investor's share of profit", s_inv, 0.75, tol=0)
    quoted("1199: penalty interest (% a year, six per five)", 100 * (F["pt_1199_penalty"] - 1), 20, tol=1e-9)
    repay = K * (1 + LOAN_RATE)
    quoted("loan: repayment (pounds)", repay, 360, tol=1e-9)
    rows = []
    for V in OUTCOMES:
        inv = min(V, K) + s_inv * max(V - K, 0)
        agent = (1 - s_inv) * max(V - K, 0)
        rows.append((V, inv, agent, repay, V - repay))
    expected = {600: (525, 75, 240), 360: (345, 15, 0), 150: (150, 0, -210)}
    for V, inv, agent, rep, a_loan in rows:
        e = expected[V]
        quoted(f"V={V}: commenda investor", inv, e[0], tol=1e-9)
        quoted(f"V={V}: commenda traveller", agent, e[1], tol=1e-9)
        quoted(f"V={V}: loan traveller (after repaying 360)", a_loan, e[2], tol=1e-9)
    quoted("V=600: investor's return under the commenda (%)", 100 * (rows[0][1] / K - 1), 75, tol=1e-9)
    quoted("V=360: investor's return under the commenda (%)", 100 * (rows[1][1] / K - 1), 15, tol=1e-9)
    v_star = K + (repay - K) / s_inv
    quoted("break-even value: commenda = loan for the investor (pounds)", v_star, 380, tol=1e-9)
    quoted("... i.e. a gross return on the voyage of (%)", 100 * (v_star / K - 1), 26.7, tol=0.05)
    return rows, v_star


def fibonacci(F):
    a, b, profit = 18, 25, 7
    first, second = a * profit / (a + b), b * profit / (a + b)
    quoted("Liber abbaci: first partner 126/43 pounds", first, F["fib_societas_steps"] / 43, tol=1e-12)
    quoted("... first partner (pounds)", first, 2.93, tol=0.005)
    p, s, d = lsd(first * PENCE_PER_POUND)
    quoted("... = 2 pounds 18 shillings", 100 * p + s, 218, tol=0)
    quoted("... and 7 11/43 pence", d, 7 + 11 / 43, tol=1e-9)
    p, s, d = lsd(second * PENCE_PER_POUND)
    quoted("... second partner 4 pounds 1 shilling", 100 * p + s, 401, tol=0)
    quoted("... and 4 32/43 pence", d, 4 + 32 / 43, tol=1e-9)
    quoted("... second partner's pence beyond 4 pounds", s * 12 + d, 16 + 32 / 43, tol=1e-9)
    quoted("... shares sum to the profit", first + second, profit, tol=1e-12)
    # two fairs: 100 -> 200 at the same proportional gain
    x1 = math.sqrt(F["fib_fairs"] * 100)
    quoted("two fairs: capital after the first fair (pounds)", x1, 141.42, tol=0.005)
    p, s, d = lsd(x1 * PENCE_PER_POUND)
    quoted("... = 141 pounds 8 shillings", 100 * p + s, 14108, tol=0)
    quoted("... and about 5 pence", d, 5.1, tol=0.05)
    quoted("two fairs: gain per fair (%)", 100 * avg_rate(100, F["fib_fairs"], 2), 41.4, tol=0.05)
    quoted("three fairs: gain per fair (%)", 100 * avg_rate(100, F["fib_three_fairs"], 3), 26.0, tol=0.05)
    quoted("three fairs: after the first fair (pounds)", 100 * 2 ** (1 / 3), 125.99, tol=0.005)
    quoted("three fairs: after the second fair (pounds)", 100 * 2 ** (2 / 3), 158.74, tol=0.005)
    # voyage with a partner's 100 pounds added after the first voyage: (100 g + 100) g = 299
    g = (-100 + math.sqrt(100 ** 2 + 4 * 100 * F["fib_voyage"])) / (2 * 100)
    quoted("voyage: growth factor per voyage", g, 1.3, tol=1e-12)
    quoted("voyage: gain per 100 pounds (Fibonacci: 30)", 100 * (g - 1), F["fib_voyage_answer"], tol=1e-9)
    quoted("voyage: 6 shillings per pound = (%)", 100 * 6 / 20, 30, tol=1e-12)
    quoted("voyage: after the first voyage (pounds)", 100 * g, 130, tol=1e-9)
    quoted("voyage: after the second voyage (pounds)", (100 * g + 100) * g, 299, tol=1e-9)


def legacy(F):
    quoted("Datini archive: account books", F["bbm_archive"], 600, tol=0)


def selfcheck(F):
    """Answers to the self-check questions."""
    pence = F["csp_bill"] * F["csp_rate_venice"]
    quoted("Q2: ducats owed at a London rate of 43", pence / 43, 155.23, tol=0.005)
    sp = spread(F["csp_rate_venice"], 43)
    quoted("Q2: spread (%)", 100 * sp, 3.49, tol=0.005)
    simple, comp = annualized(sp, 0.5)
    quoted("Q2: simple annual rate (%)", 100 * simple, 6.98, tol=0.005)
    quoted("Q2: compound annual rate (%)", 100 * comp, 7.10, tol=0.005)
    K, s_inv = F["pt_1199_capital"], F["pt_1199_share"]
    V = 450
    quoted("Q3: commenda investor (pounds)", min(V, K) + s_inv * max(V - K, 0), 412.5, tol=1e-9)
    quoted("Q3: commenda traveller (pounds)", (1 - s_inv) * max(V - K, 0), 37.5, tol=1e-9)
    quoted("Q3: loan traveller (pounds)", V - K * (1 + LOAN_RATE), 90, tol=1e-9)
    quoted("Q5: Venetian coupon 4% at 60% of par (%)", 100 * 0.04 / 0.60, 6.7, tol=0.05)
    quoted("Q5: ... at 20% of par (%)", 100 * 0.04 / 0.20, 20, tol=1e-9)


if __name__ == "__main__":
    F = facts()
    suftaja(F)
    bill_1442(F)
    bbm_table(F)
    other_rates(F)
    commenda(F)
    fibonacci(F)
    legacy(F)
    selfcheck(F)
