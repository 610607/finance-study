"""Chapter 11 (中世纪欧洲：庄园、黑死病与货币贬值): every number quoted in zh/ch11_medieval.tex.

    python3 checks/check_ch11.py

Inputs are five snapshots:
  medieval_europe_facts        quotations (manor extent, plague accounts, labour laws, de Wailly, Oresme,
                               Rolnick-Velde-Weber, Clark, Humphries-Weisdorf, Ashraf-Galor), checked by
                               data/fetch/verify_web_quotes.py
  clark2015_england_decadal    Clark's decadal wages, cost of living, population and land rents, 1250-1500
  boe_millennium_pop_england   population of England, Broadberry et al. (2015), via the Bank of England
  wailly1857_livre_tournois    value of the livre tournois in francs at each change, 1258-1360
  rvw1996_mint_revenue         total and mint revenue, France and England (Rolnick, Velde & Weber, Tables 2-3)
The figure module figsrc/fig_ch11.py imports the functions defined here.

Model (Ashraf & Galor 2011, section 2; the chapter's key equations):
    output            Y = (A X)^alpha L^(1-alpha); wage w = (1-alpha) Y/L, rent per acre s = alpha Y/X
                      (eq:medieval-output)
    a fall of L       w1/w0 = (L1/L0)^(-alpha), s1/s0 = (L1/L0)^(1-alpha)            (eq:medieval-factor)
    dynamics          n = gamma y / rho, L' = n L, so y' = (rho/gamma)^alpha y^(1-alpha) and
                      y/ybar evolves as x' = x^(1-alpha), ybar = rho/gamma          (eq:medieval-dynamics)
alpha is Clark's land share once capital is allowed to adjust at a fixed rate of return (deeper box):
with shares capital a, labour b, land c and r fixed, K = aY/r, so Y is proportional to
(L^b X^c)^(1/(1-a)) and alpha = c/(1-a).
Seigniorage (Rolnick, Velde & Weber): gross seigniorage rate 1 - MP/ME          (eq:medieval-seigniorage)
Efficiency (Clark, working paper, p. 6): E1/E0 = (r1/r0)^a (w1/w0)^b (s1/s0)^c.
"""
from __future__ import annotations

import math

import numpy as np

from common import load_snapshot, quoted

PENCE_PER_POUND, PENCE_PER_SHILLING = 240, 12

# Clark's benchmark shares for 1300-49 (working paper, p. 9: "wages were 50% of the value of output in
# agriculture, and land 34%"); capital takes the rest.
LABOUR_SHARE, LAND_SHARE = 0.50, 0.34
CAPITAL_SHARE = 1.0 - LABOUR_SHARE - LAND_SHARE
ALPHA = LAND_SHARE / (1.0 - CAPITAL_SHARE)     # effective land share, capital adjusting (deeper box)
BASE = (1300, 1340)                            # Clark's pre-plague benchmark, decades 1300-1349

# Teaching inputs stated in the text
LEASE_LIVRES = 10                    # ex:medieval-rent: a Paris rent fixed at 10 livres a year
MINT_VOLUME_FACTOR = 2               # ex:medieval-seigniorage: metal brought to the mint doubles


def facts() -> dict[str, list[float]]:
    """id -> list of the numbers in the value column (several values are separated by ';')."""
    df, _ = load_snapshot("medieval_europe_facts", dtype={"value": str})
    out = {}
    for _, r in df.iterrows():
        v = r["value"]
        if isinstance(v, str) and v.strip():
            out[r["id"]] = [float(x) for x in v.split(";")]
    return out


def quotes() -> dict[str, str]:
    """id -> verbatim quotation (for numbers the text takes straight from a quotation)."""
    df, _ = load_snapshot("medieval_europe_facts", dtype={"value": str})
    return dict(zip(df["id"], df["quote"].fillna("")))


def said(Q: dict[str, str], qid: str, *tokens: str) -> None:
    """Assert that each token (a number as printed in the source) occurs in the quotation qid."""
    missing = [t for t in tokens if t not in Q[qid]]
    print(f"{'ok ' if not missing else 'BAD'} {qid}: quotation contains {', '.join(tokens)}")
    if missing:
        raise AssertionError(f"{qid}: {missing} not in the quotation")


def clark():
    df, _ = load_snapshot("clark2015_england_decadal")
    df = df.set_index("decade")
    df["real_rent"] = df["land_rents_gbp_m"] / df["col_1860s_100"] * 100.0
    return df


def clark_index(col: str):
    """Column of clark() as a ratio to its mean over the decades 1300-1349."""
    d = clark()
    return d[col] / d.loc[BASE[0]:BASE[1], col].mean()


def broadberry():
    df, _ = load_snapshot("boe_millennium_pop_england")
    return df.set_index("year")["pop_england_m"]


def wailly():
    df, _ = load_snapshot("wailly1857_livre_tournois")
    month = df["month"].fillna(1)
    day = df["day"].fillna(1)
    df["t"] = df["year"] + (month - 1) / 12 + (day - 1) / 365
    return df


def rvw():
    df, _ = load_snapshot("rvw1996_mint_revenue")
    return df


# --- model -----------------------------------------------------------------
def factor_prices(l_ratio: float, alpha: float = ALPHA) -> tuple[float, float]:
    """eq:medieval-factor: (w1/w0, s1/s0) when labour falls to l_ratio of its old level, A and X fixed."""
    return l_ratio ** (-alpha), l_ratio ** (1.0 - alpha)


def alpha_with_capital(a: float, b: float, c: float) -> float:
    """Land share of the two-factor reduced form when capital earns a fixed return (deeper box)."""
    assert abs(a + b + c - 1.0) < 1e-12
    return c / (1.0 - a)


def income_path(x0: float, alpha: float = ALPHA, T: int = 8) -> np.ndarray:
    """eq:medieval-dynamics in ratios to the steady state: x_{t+1} = x_t^(1-alpha), x = y/ybar."""
    x = [x0]
    for _ in range(T):
        x.append(x[-1] ** (1.0 - alpha))
    return np.array(x)


def labour_map(ell: np.ndarray, alpha: float = ALPHA) -> np.ndarray:
    """Ashraf & Galor eq. (7) in ratios to the steady state Lbar: ell' = ell^(1-alpha)."""
    return ell ** (1.0 - alpha)


def half_life(alpha: float = ALPHA) -> float:
    """Generations until half of a log deviation of income per person is gone: (1-alpha)^k = 1/2."""
    return math.log(0.5) / math.log(1.0 - alpha)


def gross_seigniorage_rate(me: float, mp: float) -> float:
    """eq:medieval-seigniorage: 1 - MP/ME."""
    return 1.0 - mp / me


def efficiency(r_ratio: float, w_ratio: float, s_ratio: float) -> float:
    """Clark's dual measure E1/E0 = (r1/r0)^a (w1/w0)^b (s1/s0)^c with his benchmark shares."""
    return r_ratio ** CAPITAL_SHARE * w_ratio ** LABOUR_SHARE * s_ratio ** LAND_SHARE


def pence(l: float = 0, s: float = 0, d: float = 0) -> float:
    return l * PENCE_PER_POUND + s * PENCE_PER_SHILLING + d


# ---------------------------------------------------------------------------
def havering(F):
    """sec:medieval-world, ex:medieval-manor: the extent of Havering, 1306-7."""
    quoted("Havering: demesne 223.5 acres x 6d (pence)", 223.5 * F["havering_demesne"][0], F["havering_demesne_sum"][0], tol=0)
    quoted("  = 111s 9d (pence)", pence(s=111, d=9), F["havering_demesne_sum"][0], tol=0)
    works = pence(s=6, d=2) + 10
    quoted("works of a virgate 6s 2d + 10d increment (pence)", works, F["havering_works_sum"][0] + 10, tol=0)
    quoted("  = 7s a virgate (pence)", works, pence(s=F["havering_virgate"][0]), tol=0)
    quoted("40 virgates x 7s = 14 pounds (pence)", F["havering_assize"][0] * works, pence(l=F["havering_works"][0]), tol=0)
    quoted("rent of assize 47l 19s 5.5d (pence)", pence(47, 19, 5.5), F["havering_assize_sum"][0], tol=0)
    assize, labour = F["havering_assize_sum"][0], pence(l=14)
    quoted("rent of assize / value of works", assize / labour, 3.4, tol=0.05)
    quoted("works as % of all dues of the virgates", 100 * labour / (labour + assize), 22.6, tol=0.05)
    quoted("ploughing one acre (4d) as % of the yearly value of an acre of demesne (6d)",
           100 * F["havering_plough"][0] / F["havering_demesne"][0], 66.7, tol=0.05)


def population(B, C):
    """sec:medieval-world and sec:medieval-plague: Broadberry et al. and Clark."""
    quoted("Broadberry: 1300 (m)", B[1300], 4.73, tol=0.005)
    quoted("Broadberry: 1340 (m)", B[1340], 4.56, tol=0.005)
    quoted("Broadberry: 1348 (m)", B[1348], 4.81, tol=0.005)
    quoted("Broadberry: 1351 (m)", B[1351], 2.60, tol=0.005)
    quoted("Broadberry: 1348 -> 1351 change (%)", 100 * (B[1351] / B[1348] - 1), -46, tol=0.5)
    quoted("Broadberry: 1377 benchmark (m)", B[1377], 2.50, tol=0.005)
    quoted("Broadberry: 1400 (m)", B[1400], 2.08, tol=0.005)
    quoted("Broadberry: 1450 (m)", B[1450], 1.90, tol=0.005)
    quoted("Broadberry: 1450 / 1348 (%)", 100 * B[1450] / B[1348], 40, tol=0.5)
    pop = C["pop_england_m"]
    quoted("Clark: 1250s (m)", pop[1250], 3.84, tol=0.005)
    quoted("Clark: 1310s (m)", pop[1310], 5.61, tol=0.005)
    quoted("Clark: 1340s (m)", pop[1340], 4.48, tol=0.005)
    quoted("Clark: 1400s (m)", pop[1400], 2.64, tol=0.005)
    quoted("Clark: mean of 1300-49 (m)", pop.loc[1300:1340].mean(), 5.01, tol=0.005)
    quoted("Clark: 1400s / 1300-49", pop[1400] / pop.loc[1300:1340].mean(), 0.53, tol=0.005)
    # before the plague: more people, lower real wages (Malthusian pattern)
    quoted("Clark: population 1250s -> 1310s (%)", 100 * (pop[1310] / pop[1250] - 1), 46, tol=0.5)
    rb = C["real_blab_1860s_100"]
    quoted("Clark: real building labourer wage 1250s -> 1310s (%)", 100 * (rb[1310] / rb[1250] - 1), -32, tol=0.5)


def model():
    """sec:medieval-malthus, ex:medieval-plague, deeper box."""
    quoted("capital share 1 - 0.50 - 0.34", CAPITAL_SHARE, 0.16, tol=1e-12)
    quoted("alpha = 0.34 / (1 - 0.16)", alpha_with_capital(CAPITAL_SHARE, LABOUR_SHARE, LAND_SHARE), 0.405, tol=0.0005)
    quoted("1 - alpha", 1 - ALPHA, 0.595, tol=0.0005)
    w, s = factor_prices(0.44)
    quoted("Clark's labour 0.44: wage change (%)", 100 * (w - 1), 39, tol=0.5)
    quoted("Clark's labour 0.44: rent change (%)", 100 * (s - 1), -39, tol=0.5)
    C = clark()
    l = C.loc[1400, "pop_england_m"] / C.loc[1300:1340, "pop_england_m"].mean()
    w, s = factor_prices(l)
    quoted("Clark population 1400s/1300-49: predicted wage change (%)", 100 * (w - 1), 30, tol=0.5)
    quoted("Clark population 1400s/1300-49: predicted rent change (%)", 100 * (s - 1), -32, tol=0.5)
    quoted("half-life of the gain (generations)", half_life(), 1.3, tol=0.05)
    x = income_path(factor_prices(l)[0])
    quoted("income path after one generation (% above steady state)", 100 * (x[1] - 1), 17, tol=0.5)
    quoted("income path after four generations (% above steady state)", 100 * (x[4] - 1), 3, tol=0.5)
    quoted("ceiling at the old wage: market wage", factor_prices(l)[0], 1.30, tol=0.005)
    quoted("ceiling at the old wage: shortage 1 - L1", 1 - l, 0.47, tol=0.005)


def clark_benchmark(F):
    """Clark's own numbers, quoted from his working paper."""
    quoted("Clark: wage rise by 1400 with labour at 0.44 (%)", F["clark_40"][0], 40, tol=0)
    quoted("Clark: rents fall by 39% when wages rise by 40%", F["clark_equal"][1], 39, tol=0)
    quoted("Clark: our formula with 0.44 gives the same pair (%)", 100 * (factor_prices(F["clark_044"][0])[0] - 1),
           F["clark_equal"][0], tol=0.6)
    quoted("Clark: wage rise in the 1350s (%)", F["clark_1350s"][0], 25, tol=0)
    quoted("Clark: largest possible wage rise over his range of technologies (%)", F["clark_range"][1], 86, tol=0)
    quoted("Clark: real agricultural wages, 15th century, deflated by farm prices (% rise)", F["clark_64"][0], 64, tol=0)


def plague_records(F):
    """sec:medieval-plague: South Frith and the Selby proxy."""
    old, total = F["southfrith_old"][0], F["southfrith_new"][0]
    quoted("South Frith: defect of rent 1345-6 = 15s 4d (pence)", old, pence(s=15, d=4), tol=0)
    quoted("South Frith: 1349-50 = 119s 3.25d (pence)", total, pence(s=119, d=3.25), tol=0)
    quoted("  new defect 119s 3.25d - 15s 4d = 103s 11.25d (pence)", total - old, pence(s=103, d=11.25), tol=0)
    quoted("  ratio of the defects of rent", total / old, 7.8, tol=0.05)
    quoted("  the 40 waste acres, 13s 4d (pence)", F["southfrith_waste"][0], pence(s=13, d=4), tol=0)


def statute(F, C):
    """sec:medieval-statute and tab:medieval-statute."""
    caps = F["stat_1351_c3"]          # master carpenter, other carpenter, master mason, other masons, servants, tilers, knaves
    quoted("cap: master carpenter (d)", caps[0], 3, tol=0)
    quoted("cap: master free mason (d)", caps[2], 4, tol=0)
    quoted("cap: masons' servants, tilers' knaves (d)", caps[4], 1.5, tol=0)
    craft, lab, farm = C["bcraft_wage_d"], C["blab_wage_d"], C["farm_wage_d"]
    for dec, cr, la, fa in [(1340, 2.89, 1.61, 1.49), (1350, 4.06, 2.28, 2.80), (1360, 4.45, 2.75, 2.88)]:
        quoted(f"Clark {dec}s: building craftsman (d/day)", craft[dec], cr, tol=0.005)
        quoted(f"Clark {dec}s: building labourer (d/day)", lab[dec], la, tol=0.005)
        quoted(f"Clark {dec}s: farm labourer (d/day)", farm[dec], fa, tol=0.005)
    quoted("1350s craftsman above the 3d cap (%)", 100 * (craft[1350] / 3 - 1), 35, tol=0.5)
    quoted("1350s labourer above the 1.5d cap (%)", 100 * (lab[1350] / 1.5 - 1), 52, tol=0.5)
    quoted("1340s craftsman above the 3d cap (%)", 100 * (craft[1340] / 3 - 1), -4, tol=0.5)
    quoted("1340s labourer above the 1.5d cap (%)", 100 * (lab[1340] / 1.5 - 1), 7, tol=0.5)
    quoted("Denk: 20s against 8s", F["chelmsford_denk"][0] / 8, 2.5, tol=0)
    fines = [40, 6, 12, 12, 6, 24, 6, 12, 12, 12, 6, 12, 6, 6, 12, 6, 6, 6]   # Layer de la Hay, 18 fines (pence)
    quoted("Layer de la Hay: number of fines", len(fines), 18, tol=0)
    quoted("Layer de la Hay: smallest fine (d)", min(fines), 6, tol=0)
    quoted("Layer de la Hay: largest fine (d)", max(fines), 40, tol=0)
    quoted("Layer de la Hay: sum of the fines = 16s 10d (pence)", sum(fines), F["layer_sum"][0], tol=0)
    quoted("  = 16s 10d", sum(fines), pence(s=16, d=10), tol=0)
    workmen = pence(l=17, s=11, d=3)
    quoted("Winstree: fines of workmen 17l 11s 3d (pence)", workmen, 4215, tol=0)
    quoted("Winstree: whole sum 19l 10s 2d (pence)", pence(19, 10, 2), F["winstree_sum"][0], tol=0)
    quoted("Winstree: fifteenth 38s 11d + fines = whole (pence)", pence(s=38, d=11) + workmen, F["winstree_sum"][0], tol=0)
    quoted("Winstree: fines as % of the hundred's payment", 100 * workmen / F["winstree_sum"][0], 90, tol=0.5)


def livre(W, F):
    """sec:medieval-debasement, case box, ex:medieval-rent, fig:livre_tournois (de Wailly)."""
    v = dict(zip(W["date_fr"], W["livre_francs"]))
    for date, txt in [("1258", 20.26), ("1278, déc.", 20.10), ("1295, avril", 16.72), ("1303, août", 6.97),
                      ("1305, avril", 6.15), ("1306, oct.", 17.63), ("1310, août", 15.58), ("1311, janv.", 13.66),
                      ("1313, sept. 15", 18.37), ("1316, avril", 20.26), ("1342, juillet", 4.07),
                      ("1360, déc. 5", 10.92)]:
        quoted(f"livre tournois from {date} (francs)", v[date], txt, tol=0)
    quoted("de Wailly p. 32: 1303 value", F["wailly_1303"][0], v["1303, août"], tol=0)
    # Philip IV (1285-1314): value at accession (rate of 1278) and at death (rate of Sept. 1313)
    quoted("Philip IV: death / accession", v["1313, sept. 15"] / v["1278, déc."], 10 / 11, tol=0.01)
    quoted("Philip IV: lowest / accession (%)", 100 * v["1305, avril"] / v["1278, déc."], 30.6, tol=0.05)
    quoted("Philip IV: fall 1278 -> 1305 (%)", 100 * (v["1305, avril"] / v["1278, déc."] - 1), -69, tol=0.5)
    quoted("restoration Oct. 1306 / April 1305", v["1306, oct."] / v["1305, avril"], 2.87, tol=0.005)
    changes = W[(W["t"] >= 1295) & (W["t"] < 1314)]
    quoted("changes April 1295 - Sept. 1313 (de Wailly: 22)", len(changes), F["wailly_22"][0], tol=0)
    d = W[(W["year"] >= 1351) & (W["year"] <= 1360)]
    quoted("changes 1351-1360 (de Wailly: 71)", len(d), F["wailly_71"][0], tol=0)
    quoted("changes in 1359 (16)", int((d["year"] == 1359).sum()), 16, tol=0)
    quoted("changes in 1360 (17)", int((d["year"] == 1360).sum()), 17, tol=0)
    quoted("1351-1360 highest (13.59)", d["livre_francs"].max(), F["wailly_extremes"][0], tol=0)
    quoted("1351-1360 lowest (3.22)", d["livre_francs"].min(), F["wailly_extremes"][1], tol=0)
    x = W["livre_francs"].to_numpy()
    idx = W.index[(W["year"] >= 1351) & (W["year"] <= 1360)]
    rises = sum(1 for i in idx if x[i] > x[i - 1] and x[i - 1] < x[i - 2])
    quoted("1351-1360 rises that follow a fall (de Wailly: 11)", rises, F["wailly_11"][0], tol=0)
    quoted("1351-1360: highest / lowest", d["livre_francs"].max() / d["livre_francs"].min(), 4.2, tol=0.05)
    steps = W[(W["year"] >= 1296) & (W["year"] <= 1305)]
    quoted("changes May 1296 - April 1305", len(steps), 16, tol=0)
    quoted("  of which with a calculated pied (letter C.)", int(steps["calc"].sum()), 15, tol=0)
    # ex:medieval-rent
    rent = {k: LEASE_LIVRES * v[k] for k in ("1278, déc.", "1305, avril", "1306, oct.")}
    quoted("rent of 10 livres before 1295 (francs)", rent["1278, déc."], 201.0, tol=1e-9)
    quoted("  in April 1305 (francs)", rent["1305, avril"], 61.5, tol=1e-9)
    quoted("  after October 1306 (francs)", rent["1306, oct."], 176.3, tol=1e-9)


def mint(R, F):
    """tab:medieval-mint and ex:medieval-seigniorage (Rolnick, Velde & Weber)."""
    for _, r in R.dropna(subset=["mint_pct", "total_thousand"]).iterrows():
        pct = 100 * float(r["mint_thousand"]) / float(r["total_thousand"])
        quoted(f"{r['country']} {r['period']}: mint / total (%)", round(pct), float(r["mint_pct"]), tol=0)
    fr = R[(R["country"] == "France") & R["mint_pct"].notna()]
    deb = fr[fr["marks"].fillna("").str.contains(r"\*", regex=True)]
    nod = fr[~fr["marks"].fillna("").str.contains(r"\*", regex=True)]
    quoted("France: debasement periods with a mint share", len(deb), 5, tol=0)
    quoted("France: lowest mint share in a debasement period (%)", deb["mint_pct"].min(), 50, tol=0)
    quoted("France: highest mint share outside debasement (%)", nod["mint_pct"].max(), 4, tol=0)
    quoted("France 1419-20: mint share (%)", fr.set_index("period").loc["1419-20", "mint_pct"], 91, tol=0)
    eng = R[R["country"] == "England"].set_index("period")
    quoted("England 1544-47: mint share (%)", eng.loc["1544-47", "mint_pct"], 26, tol=0)
    quoted("England 1463-66: mint share (%)", eng.loc["1463-66", "mint_pct"], 17, tol=0)
    # ex:medieval-seigniorage: gross seigniorage rates (France 1354-1490), costs in 1401, volume doubled
    normal, debased = F["rvw_rates"][0], F["rvw_debasement_rates"][0]
    cost = F["rvw_costs"][0]
    quoted("MP/ME in a normal year (%)", 100 * (1 - normal / 100), 92.5, tol=1e-9)
    quoted("MP/ME in a debasement year (%)", 100 * (1 - debased / 100), 78.3, tol=1e-9)
    quoted("check: 1 - MP/ME with ME = 100, MP = 78.3", 100 * gross_seigniorage_rate(100, 78.3), 21.7, tol=1e-9)
    quoted("gross revenue, debasement / normal", MINT_VOLUME_FACTOR * debased / normal, 5.8, tol=0.05)
    quoted("net of costs, debasement / normal", MINT_VOLUME_FACTOR * (debased - cost) / (normal - cost), 8.3, tol=0.05)
    quoted("net seigniorage rate, normal year (%)", normal - cost, 4.5, tol=1e-9)
    quoted("net seigniorage rate, debasement year (%)", debased - cost, 18.7, tol=1e-9)


def test(C, F):
    """sec:medieval-test and fig:plague_wages: data against the model, 1300-49 = 1."""
    blab, farm, craft = (clark_index(c) for c in ("real_blab_1860s_100", "real_farm_1860s_100", "real_bcraft_1860s_100"))
    rent = clark_index("real_rent")
    quoted("real building labourer wage, 1400s (1300-49 = 1)", blab[1400], 1.83, tol=0.005)
    quoted("real farm wage, 1400s", farm[1400], 2.26, tol=0.005)
    quoted("real building craftsman wage, 1400s", craft[1400], 1.45, tol=0.005)
    quoted("real land rent, 1400s", rent[1400], 0.97, tol=0.005)
    quoted("real land rent, 1350s", rent[1350], 0.82, tol=0.005)
    quoted("real land rent, 1470s", rent[1470], 0.71, tol=0.005)
    quoted("real building labourer wage, 1350s", blab[1350], 1.24, tol=0.005)
    quoted("real building labourer wage, 1360s", blab[1360], 1.44, tol=0.005)
    quoted("real building labourer wage, 1370s", blab[1370], 1.55, tol=0.005)
    quoted("real building labourer wage, 1380s", blab[1380], 1.84, tol=0.005)
    quoted("real farm wage, 1350s", farm[1350], 1.71, tol=0.005)
    quoted("real building labourer wage, 1440s", blab[1440], 2.26, tol=0.005)
    quoted("farm wage: mean of the 1400s-1490s against 1300-49 (% rise)", 100 * (farm.loc[1400:1490].mean() - 1), 141, tol=0.5)
    quoted("real farm wage 1400s (% rise)", 100 * (farm[1400] - 1), 126, tol=0.5)
    quoted("real building labourer wage 1400s (% rise)", 100 * (blab[1400] - 1), 83, tol=0.5)
    quoted("real land rent 1400s (% change)", 100 * (rent[1400] - 1), -3, tol=0.5)
    l = clark_index("pop_england_m")
    w, s = factor_prices(l[1400])
    quoted("model wage, 1400s", w, 1.30, tol=0.005)
    quoted("model rent, 1400s", s, 0.68, tol=0.005)
    w50, s50 = factor_prices(l[1350])
    quoted("Clark population 1350s / 1300-49", l[1350], 0.71, tol=0.005)
    quoted("model wage, 1350s", w50, 1.15, tol=0.005)
    # Clark's dual measure: r from 8.1% (median of 1300-48 transfers) to 5% by 1400
    r0, r1 = F["clark_r_1300"][0], F["clark_r"][1]
    quoted("r1/r0", r1 / r0, 0.62, tol=0.005)
    quoted("efficiency 1400s, building labourers", efficiency(r1 / r0, blab[1400], rent[1400]), 1.24, tol=0.005)
    quoted("efficiency 1400s, farm labourers", efficiency(r1 / r0, farm[1400], rent[1400]), 1.38, tol=0.005)
    quoted("efficiency if wages and rents had followed the model (r fixed)", efficiency(1.0, w, s), 1.0, tol=1e-9)


def from_quotes(Q):
    """Numbers the text takes straight from a quotation (read on scanned pages or in the PDFs)."""
    said(Q, "rvw_123", "123", "1285", "1490", "112", "5 percent", "50 percent")
    said(Q, "rvw_england_stable", "20 percent")
    said(Q, "rvw_83", "1542", "1551", "ten times", "83 percent", "2 percent", "57 percent")
    said(Q, "rvw_rates", "7.5 percent", "2.0 percent")
    said(Q, "rvw_debasement_rates", "21.7 percent", "4.3 percent")
    said(Q, "rvw_costs", "1401", "3 percent", "0.5 percent")
    said(Q, "rvw_1412", "1412", "130")
    said(Q, "rvw_negligible", "5 percent", "50 percent", "1299", "1327", "1349")
    said(Q, "rvw_1350s", "1330s", "1370s", "8 to 12")
    said(Q, "clark_range", "0%", "86%")
    said(Q, "clark_r", "10%", "5%")
    said(Q, "clark_r_1300", "8.1%")
    said(Q, "clark_lag", "1350-9", "1360-9", "1300-49")
    said(Q, "clark_statute", "1351", "1346-7")
    said(Q, "clark_r_fixed", "1349")
    said(Q, "hw_days", "150 days", "300 days")
    said(Q, "ord_1349_sixty", "sixty")
    said(Q, "ord_1349_lords", "threefold")
    said(Q, "ord_1349_date", "eighteenth day of June")
    said(Q, "ord_1349_base", "twentieth year", "five or six")
    said(Q, "stat_1351_c1", "Twentieth Year", "Four Years")
    said(Q, "stat_1351_double", "double or treble")
    said(Q, "stat_1351_stocks", "Three Days")
    said(Q, "stat_1351_prison", "Forty Days", "Quarter of a Year", "double Pain")
    said(Q, "chelmsford_denk", "20s.", "8s.")
    said(Q, "wailly_22", "10/11", "vingt-deux", "dix-neuf")
    said(Q, "wailly_jews", "22 juillet 1306")
    said(Q, "oresme_date", "1373")
    said(Q, "oresme_louvre", "1373")
    said(Q, "oresme_ms1397", "1397")


def answers(F):
    """selfcheck answers."""
    w, s = factor_prices(0.6)
    quoted("answer 2: wage with labour at 0.6", w, 1.23, tol=0.005)
    quoted("answer 2: rent with labour at 0.6", s, 0.74, tol=0.005)
    quoted("answer 2: wage change (%)", 100 * (w - 1), 23, tol=0.5)
    quoted("answer 2: rent change (%)", 100 * (s - 1), -26, tol=0.5)
    quoted("answer 2: one generation later", income_path(w)[1], 1.13, tol=0.005)
    gross = 100 * gross_seigniorage_rate(100, 85)
    quoted("answer 4: gross seigniorage rate (%)", gross, 15, tol=1e-9)
    quoted("answer 4: net rate (%)", gross - F["rvw_costs"][0], 12, tol=1e-9)
    quoted("answer 4: net revenue with 3x the metal / normal", 3 * (gross - F["rvw_costs"][0]) / (F["rvw_rates"][0] - F["rvw_costs"][0]), 8.0, tol=0.05)
    v = dict(zip(wailly()["date_fr"], wailly()["livre_francs"]))
    quoted("answer 5: 10 livres in August 1303 (francs)", LEASE_LIVRES * v["1303, août"], 69.7, tol=1e-9)
    quoted("answer 5: share of the rent before 1295 (%)", 100 * v["1303, août"] / v["1278, déc."], 34.7, tol=0.05)
    blab = clark_index("real_blab_1860s_100")[1400]
    s_req = blab ** (-LABOUR_SHARE / LAND_SHARE)
    quoted("answer 6: rent with constant efficiency and r, wage 1.83", s_req, 0.41, tol=0.005)
    quoted("answer 6: implied rent change (%)", 100 * (s_req - 1), -59, tol=0.5)
    quoted("answer 6: check E = 1", efficiency(1.0, blab, s_req), 1.0, tol=1e-9)


def main() -> None:
    F = facts()
    B, C, W, R = broadberry(), clark(), wailly(), rvw()
    havering(F)
    population(B, C)
    model()
    clark_benchmark(F)
    plague_records(F)
    statute(F, C)
    livre(W, F)
    mint(R, F)
    test(C, F)
    from_quotes(quotes())
    answers(F)


if __name__ == "__main__":
    main()
