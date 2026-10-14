"""Chapter 6 (美索不达米亚与埃及：神庙、宫廷与记账): every number quoted in zh/ch06_mesopotamia.tex.

    python3 checks/check_ch06.py

Inputs are two snapshots:
  meso_facts      quotations from the Code of Hammurabi (King's translation, 1910), the Louvre's notice of the stele,
                  the Chicago Assyrian Dictionary (vols. K, M/2, Ṣ, Š/3), Visible Language (Woods ed. 2010), Teeter
                  (2024), Temin (2003), Erman (1894), Smith (1776), Jevons (1875), Menger (1892), Mitchell Innes (1913)
                  and Polanyi and Oppenheim in Trade and Market in the Early Empires (1957); checked by
                  data/fetch/verify_web_quotes.py
  babylon_prices  monthly prices of barley and dates (and four other goods) in Babylon, 582-61 BC, in grams of
                  silver per 100 litres (van der Spek, van Leeuwen & van Zanden, DataverseNL, CC0)
The figure module figsrc/fig_ch06.py imports the functions defined here.

Notation of the chapter:
    exchange ratios    N_barter = n (n - 1) / 2,  N_unit = n - 1                              (eq:meso-ratios)
    own rates          1 + i_b = (1 + i_s) p_0 / p_1                                          (eq:meso-own)
                       p: price of barley in silver; i_s, i_b: interest on silver and on barley loans;
                       eq:prices-fisher (Chapter 3) with silver as the money and barley as the good
    debt               D_{t+1} = (1 + i) D_t - x_t,  D_bar = x_bar / i,  T_2 = ln 2 / ln(1 + i)   (eq:meso-debt)
Units (CAD): 1 mina = 60 shekels, 1 shekel = 180 grains (about 8 1/3 g), 1 kur = 300 qa (sila); Erman: 1 uten
(deben) = 91 g of copper. The examples ex:meso-ox, ex:meso-own and ex:meso-debt, and the self-check, use the
teaching inputs defined below and stated in the text.

The seasonal check regresses the log price on year and month dummies (statsmodels OLS, standard errors clustered
by year), on the months as numbered in the workbook; the workbook does not say which calendar they follow.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from common import load_snapshot, quoted

# ---------------------------------------------------------------------------------------------------
# Units and teaching inputs stated in the text
MINA_SHEKELS = 60
SHEKEL_GRAINS = 180
KUR_SILA = 300
SHEKEL_G = 25 / 3                     # "about eight and one-third grams"
UTEN_G = 91
# ex:meso-debt: a farmer who can repay at most X_BAR kur a year owes D0 kur of barley
DEBT = dict(d0=2.0, x_bar=1.0, i_b=1 / 3, i_s=0.2, bad=(1, 2), years=8)
# the self-check
SC = dict(goods=5, days=30, oa_mina=1.0, fall=0.15)
# months of the seasonal contrast, read off the estimated profile (stated in the text as such)
HIGH, LOW = (12, 1, 2, 3, 4), (5, 6, 7, 8)


# ---------------------------------------------------------------------------------------------------
# Loaders
def facts() -> dict[str, list[float]]:
    """id -> the numbers of the value column (several are separated by ';')."""
    df, _ = load_snapshot("meso_facts", dtype={"value": str})
    out = {}
    for _, r in df.iterrows():
        v = r["value"]
        if isinstance(v, str) and v.strip():
            out[r["id"]] = [float(x) for x in v.split(";")]
    return out


def quotes() -> set[str]:
    df, _ = load_snapshot("meso_facts")
    return set(df["id"])


def prices() -> pd.DataFrame:
    df, _ = load_snapshot("babylon_prices")
    return df


# ---------------------------------------------------------------------------------------------------
# Teaching models
def ratios(n: int) -> tuple[int, int]:
    """eq:meso-ratios: exchange ratios among n goods without and with a unit of account (one of the goods)."""
    return n * (n - 1) // 2, n - 1


def own_ratio(i_s: float, i_b: float) -> float:
    """eq:meso-own: p_0 / p_1, the fall in the silver price of barley that makes the two loans equivalent."""
    return (1 + i_b) / (1 + i_s)


def doubling(i: float) -> float:
    """eq:meso-debt: years for a debt to double at the annual rate i, compounded yearly."""
    return math.log(2) / math.log(1 + i)


def debt_path(d0: float, i: float, x_bar: float, bad=(), s48: bool = False, years: int = 8) -> np.ndarray:
    """eq:meso-debt year by year: D_{t+1} = (1 + i) D_t - x_t, x_t = min(x_bar, (1 + i) D_t).

    In a bad year (t + 1 in `bad`) nothing is repaid; with s48 (Code of Hammurabi § 48) no interest accrues that
    year either. Once repaid the debt stays at zero."""
    d = [d0]
    for t in range(1, years + 1):
        prev = d[-1]
        if t in bad:
            d.append(prev if s48 else (1 + i) * prev)
        else:
            d.append(max((1 + i) * prev - x_bar, 0.0))
    return np.array(d)


def payoff_year(path: np.ndarray) -> int | None:
    z = np.nonzero(path <= 1e-12)[0]
    return int(z[0]) if len(z) else None


# ---------------------------------------------------------------------------------------------------
# The seasonal and co-movement checks
def seasonal(good: str, P: pd.DataFrame | None = None) -> dict:
    """Month effects of log price with year fixed effects (OLS, SE clustered by year); years with >= 2 months."""
    P = prices() if P is None else P
    s = P.dropna(subset=["month", good]).copy()
    s["lp"] = np.log(s[good])
    s["month"] = s["month"].astype(int)
    s = s[s.groupby("year")["lp"].transform("size") >= 2].reset_index(drop=True)
    groups = pd.factorize(s["year"])[0]
    kw = dict(cov_type="cluster", cov_kwds={"groups": groups})
    m = smf.ols("lp ~ C(year) + C(month, Treatment(1))", data=s).fit(**kw)
    names = [f"C(month, Treatment(1))[T.{k}]" for k in range(2, 13)]
    idx = [list(m.params.index).index(n) for n in names]
    b = np.r_[0.0, m.params.iloc[idx].to_numpy()]
    V = np.zeros((12, 12))
    V[1:, 1:] = m.cov_params().iloc[idx, idx].to_numpy()
    dev = np.eye(12) - 1.0 / 12                    # deviations from the mean of the twelve months
    eff, se = dev @ b, np.sqrt(np.diag(dev @ V @ dev.T))
    R = np.zeros((11, len(m.params)))
    for r, j in enumerate(idx):
        R[r, j] = 1.0
    w = m.wald_test(R, scalar=True)
    s["hi"] = s["month"].isin(HIGH).astype(int)
    s["lo"] = s["month"].isin(LOW).astype(int)
    m2 = smf.ols("lp ~ C(year) + hi + lo", data=s).fit(**kw)
    V2 = m2.cov_params()
    diff = m2.params["hi"] - m2.params["lo"]
    dse = math.sqrt(V2.loc["hi", "hi"] + V2.loc["lo", "lo"] - 2 * V2.loc["hi", "lo"])
    return dict(n=len(s), years=s["year"].nunique(), eff=eff, se=se, wald=float(w.statistic),
                p=float(w.pvalue), diff=float(diff), dse=dse)


def annual(P: pd.DataFrame | None = None) -> pd.DataFrame:
    """Annual geometric means of barley and dates (years with at least one price)."""
    P = prices() if P is None else P
    return np.exp(np.log(P[["barley", "dates"]]).groupby(P["year"]).mean())


def comovement(P: pd.DataFrame | None = None) -> dict:
    P = prices() if P is None else P
    A = np.log(annual(P))
    both = A.dropna()
    yrs = both.index.to_numpy()
    step = np.r_[False, np.diff(yrs) == 1]
    ch = both.diff()[step]
    m = P.dropna(subset=["month"]).copy()
    m["t"] = m["year"] * 12 + m["month"]
    m = m.sort_values("t").set_index("t")
    lb, ld = np.log(m["barley"]), np.log(m["dates"])
    nxt = pd.Series(np.r_[np.nan, np.diff(m.index.to_numpy())], index=m.index) == 1
    db, dd = lb.diff()[nxt], ld.diff()[nxt]
    ok = db.notna() & dd.notna()
    # first-order autocorrelation of monthly barley changes (three consecutive months)
    b = lb.dropna()
    t = b.index.to_numpy()
    d1 = pd.Series(np.r_[np.nan, np.diff(b.to_numpy())], index=t)[np.r_[False, np.diff(t) == 1]]
    pairs = np.array([(d1[k], d1[k + 1]) for k in d1.index if (k + 1) in d1.index])
    ab = A["barley"].dropna()
    lv = np.array([(ab[y], ab[y + 1]) for y in ab.index if (y + 1) in ab.index])
    return dict(n_years=len(both), r_level=both.corr().iloc[0, 1], n_dyears=len(ch), r_dyear=ch.corr().iloc[0, 1],
                n_months=int(ok.sum()), r_month=float(np.corrcoef(db[ok], dd[ok])[0, 1]),
                n_ac=len(pairs), ac1=float(np.corrcoef(pairs.T)[0, 1]),
                n_lv=len(lv), ac_level=float(np.corrcoef(lv.T)[0, 1]))


# ---------------------------------------------------------------------------------------------------
# Sections
def opening(F, Q):
    quoted("the ox: uten to be paid", F["erman_ox119"][0], 119)
    quoted("    uten for the animal", F["erman_ox111"][0], 111)
    quoted("    other expenses (uten)", F["erman_ox119"][0] - F["erman_ox111"][0], 8)
    quoted("    one uten (g of copper)", F["erman_uten"][1], UTEN_G)
    quoted("    119 uten in kg of copper", F["erman_ox119"][0] * F["erman_uten"][1] / 1000, 10.8, tol=0.05)
    sub = F["erman_subst"]
    quoted("    stick with inlaid work (uten)", sub[0], 25)
    quoted("    plainer stick (uten)", sub[1], 12)
    quoted("    jars of honey", sub[2], 11)
    quoted("    for uten", sub[3], 11)
    quoted("    listed substitutes (uten)", sub[0] + sub[1] + sub[3], 48)
    quoted("    not itemised by Erman ('and so on')", F["erman_ox119"][0] - (sub[0] + sub[1] + sub[3]), 71)
    quoted("Old Assyrian trade from c. (BC)", -F["vl_kanes"][0], 2000)
    quoted("    into the 1730s", -F["vl_kanes"][1], 1730)
    assert {"cad_oa_compound", "erman_nochange"} <= Q


def world(F, Q):
    quoted("Late Uruk from (BC)", -F["vl_uruk"][0], 3350)
    quoted("    to (BC)", -F["vl_uruk"][1], 3100)
    quoted("Uruk population, low", F["vl_pop"][0], 20000)
    quoted("    high", F["vl_pop"][1], 50000)
    quoted("conventional date of writing (BC)", -F["vl_3200"][0], 3200)
    quoted("archaic texts administrative (%)", F["vl_90"][0], 90)
    quoted("Old Babylonian period from (BC)", -F["vl_ob"][0], 2000)
    quoted("    to (BC)", -F["vl_ob"][1], 1595)
    quoted("Hammurabi reigned from (BC)", -F["louvre_date"][0], 1792)
    quoted("    to (BC)", -F["louvre_date"][1], 1750)
    quoted("stele height (cm)", F["louvre_height"][0], 225)
    quoted("    found at Susa", F["louvre_found"][0], 1901)
    quoted("    to", F["louvre_found"][1], 1902)
    quoted("paragraphs missing after § 65", F["ham_gap"][0], 34)
    quoted("Old Assyrian records, over", F["vl_20000"][0], 20000)
    quoted("Ramesses III from (BC)", -F["teeter_r3"][0], 1184)
    quoted("    to (BC)", -F["teeter_r3"][1], 1153)
    quoted("    year 29 falls about (BC)", -(F["teeter_r3"][0] + 28), 1156)
    P = prices()
    quoted("Babylon prices from (BC)", -P["year"].min(), 582)
    quoted("    to (BC)", -P["year"].max(), 61)
    quoted("months with at least one price", len(P), 858)
    quoted("barley prices", P["barley"].notna().sum(), 548)
    quoted("dates prices", P["dates"].notna().sum(), 504)
    quoted("barley prices after 400 BC (share, %)", 100 * (P.dropna(subset=["barley"])["year"] > -400).mean(), 97.6,
           tol=0.05)
    quoted("Temin: six commodities", F["temin_six"][0], 6)
    quoted("    400 years", F["temin_six"][1], 400)


def units(F):
    quoted("shekels per mina", F["cad_shekel"][0], MINA_SHEKELS)
    quoted("grams per shekel (about)", F["cad_shekel"][1], 8.33)
    quoted("grams per mina", MINA_SHEKELS * SHEKEL_G, 500, tol=1e-9)
    quoted("grains per shekel", F["cad_grains180"][0], SHEKEL_GRAINS)
    quoted("qa (sila) per kur", F["cad_kurru"][0], KUR_SILA)
    quoted("LE § 1: kur of barley", F["cad_le1_barley"][0], 1)
    quoted("    per shekel of silver", F["cad_le1_barley"][1], 1)
    quoted("LE § 1: minas of wool per shekel", F["cad_le1_wool"][0], 6)
    quoted("    implied: minas of wool per kur of barley", F["cad_le1_wool"][0] / F["cad_le1_barley"][0], 6)
    quoted("§ 257: field labourer, kur of barley a year", F["ham_257"][0], 8)
    quoted("    per month", F["ham_257"][0] / 12, 0.67, tol=0.005)
    quoted("§ 273: grains a day, months 1-5", F["ham_273"][0], 6)
    quoted("    30 days in shekels", F["ham_273"][0] * 30 / SHEKEL_GRAINS, 1.0, tol=1e-9)
    quoted("    in grams of silver", F["ham_273"][0] * 30 / SHEKEL_GRAINS * SHEKEL_G, 8.33, tol=0.005)
    quoted("    later months: 5 grains a day, 30 days in shekels", 5 * 30 / SHEKEL_GRAINS, 0.83, tol=0.005)
    quoted("Jevons: articles", F["jevons_4950"][0], 100)
    quoted("    ratios", F["jevons_4950"][1], 4950)
    quoted("    n(n-1)/2 for n = 100", ratios(100)[0], 4950)
    quoted("    prices with a unit, n = 100", ratios(100)[1], 99)
    quoted("Babylon goods: ratios among 6", ratios(6)[0], 15)
    quoted("    prices in one of them", ratios(6)[1], 5)


def ex_ox(F):
    quoted("ox / donkey, by the price of the animal", F["erman_ox111"][0] / F["erman_donkey"][0], 2.78, tol=0.005)
    quoted("ox / donkey, by the whole bill", F["erman_ox119"][0] / F["erman_donkey"][0], 2.98, tol=0.005)
    quoted("    Erman: three to one", F["erman_ratio"][0] / F["erman_ratio"][1], 3)
    quoted("goods in the bill (ox, two sticks, honey, the rest)", 5, 5)
    quoted("    ratios without a unit", ratios(5)[0], 10)
    quoted("    prices in uten", 5, 5)
    quoted("listed substitutes, share of the bill (%)", 100 * 48 / 119, 40, tol=0.5)


def rates(F):
    le = F["cad_le18a"]
    i_s = le[0] / SHEKEL_GRAINS
    i_b = le[1] / KUR_SILA
    quoted("LE § 18A: grains per shekel", le[0], 36)
    quoted("    silver rate (%)", 100 * i_s, 20, tol=1e-9)
    quoted("    silas per kur", le[1], 100)
    quoted("    barley rate (%)", 100 * i_b, 33.33, tol=0.005)
    quoted("contract: grains per shekel", F["cad_60a"][0], 60)
    quoted("    = one-third shekel", F["cad_60a"][0] / SHEKEL_GRAINS, 1 / F["cad_60b"][0], tol=1e-12)
    quoted("    rate (%)", 100 * F["cad_60a"][0] / SHEKEL_GRAINS, 33.33, tol=0.005)
    quoted("contract: one-third mina per mina (%)", 100 * F["cad_third_mina"][0] / F["cad_third_mina"][1], 33.33,
           tol=0.005)
    quoted("Ishchali, Khafajah: silas per gur", F["cad_100silas1"][0], 100)
    oa = F["cad_oa_rate"][0] / MINA_SHEKELS
    quoted("Old Assyrian: shekels per mina per month", F["cad_oa_rate"][0], 1.5)
    quoted("    per month (%)", 100 * oa, 2.5, tol=1e-9)
    quoted("    a year, simple (%)", 100 * 12 * oa, 30, tol=1e-9)
    quoted("    a year, compounded monthly (%)", 100 * ((1 + oa) ** 12 - 1), 34.5, tol=0.05)
    return i_s, i_b


def own(i_s, i_b):
    r = own_ratio(i_s, i_b)
    quoted("p0/p1 implied by 20% and 33 1/3%", r, 1.111, tol=0.0005)
    quoted("    barley cheaper at repayment by (%)", 100 * (1 - 1 / r), 10, tol=1e-9)
    quoted("    in log points", 100 * math.log(r), 10.5, tol=0.05)
    quoted("risk reading: repayment probability (%)", 100 * (1 + i_s) / (1 + i_b), 90, tol=1e-9)
    # ex:meso-own
    quoted("silver loan, unchanged price: kur to repay per kur", 1 + i_s, 1.2, tol=1e-12)
    quoted("barley loan: kur to repay", 1 + i_b, 1.333, tol=0.0005)
    swing = math.exp(0.169)
    quoted("silver loan when barley is 18.4% dearer at lending: kur to repay", (1 + i_s) * swing, 1.42, tol=0.005)
    # Fisher's wheat example (Chapter 3) in the same form
    quoted("Fisher: wheat rate with gold at 8% and wheat 100 -> 96 (%)", 100 * (1.08 / 0.96 - 1), 12.5, tol=1e-9)


def debt(F, i_s, i_b):
    for i, t in ((i_s, 3.80), (i_b, 2.41), (0.30, 2.64)):
        quoted(f"doubling time at {100 * i:.4g}% (years)", doubling(i), t, tol=0.005)
    quoted("§ 117: years of labour", F["ham_117"][0], 3)
    quoted("    set free in year", F["ham_117"][1], 4)
    quoted("33 1/3% for three years: factor", (1 + i_b) ** 3, 2.37, tol=0.005)
    quoted("20% for three years: factor", (1 + i_s) ** 3, 1.73, tol=0.005)
    D = DEBT
    quoted("threshold x_bar / i at 33 1/3% (kur)", D["x_bar"] / D["i_b"], 3, tol=1e-9)
    quoted("threshold at 20% (kur)", D["x_bar"] / D["i_s"], 5, tol=1e-9)
    a = debt_path(D["d0"], D["i_b"], D["x_bar"], years=D["years"])
    for t, v in ((1, 1.67), (2, 1.22), (3, 0.63)):
        quoted(f"no bad year, debt after year {t}", a[t], v, tol=0.005)
    quoted("    repaid in year", payoff_year(a), 4)
    quoted("    last payment (kur)", (1 + D["i_b"]) * a[3], 0.84, tol=0.005)
    b = debt_path(D["d0"], D["i_b"], D["x_bar"], bad=D["bad"], years=D["years"])
    quoted("two bad years, no § 48: after year 1", b[1], 2.67, tol=0.005)
    quoted("    after year 2", b[2], 3.56, tol=0.005)
    quoted("    after year 3", b[3], 3.74, tol=0.005)
    quoted("    after year 5", b[5], 4.32, tol=0.005)
    quoted("    after year 8", b[8], 6.12, tol=0.005)
    assert payoff_year(b) is None and np.all(np.diff(b[2:]) > 0)
    c = debt_path(D["d0"], D["i_b"], D["x_bar"], bad=D["bad"], s48=True, years=D["years"])
    quoted("with § 48: debt after year 2", c[2], 2.0, tol=1e-12)
    quoted("    repaid in year", payoff_year(c), 6)
    e = debt_path(D["d0"], D["i_s"], D["x_bar"], bad=D["bad"], years=D["years"])
    quoted("at 20%, two bad years, no § 48: after year 2", e[2], 2.88, tol=0.005)
    quoted("    repaid in year", payoff_year(e), 7)


def misharum(F, Q):
    assert {"cad_misharum", "cad_sumulael", "cad_samsuiluna", "cad_abiesuh", "cad_collector1", "cad_arrears",
            "cad_innkeeper", "cad_broke"} <= Q
    quoted("Abi-esuh, regnal year", F["cad_abiesuh"][0], 2)
    quoted("Edict of Ammisaduqa §", F["cad_collector2"][0], 2)


def egypt(F, Q):
    quoted("raw skins: pieces", F["erman_skins"][0], 4)
    quoted("    worth uten", F["erman_skins"][1], 8)
    quoted("servant's average payment (uten a year)", F["erman_five"][0], 5)
    quoted("    in grams of copper", F["erman_five"][0] * UTEN_G, 455, tol=1e-9)
    quoted("corn due on day", F["erman_corn28"][0], 28)
    quoted("year of Ramesses III", F["erman_year29"][0], 29)
    quoted("days starving", F["erman_18"][0], 18)
    assert {"erman_strike1", "erman_strike2", "erman_hunger", "erman_empty", "erman_govcorn", "erman_rations"} <= Q


def data_check():
    P = prices()
    b = seasonal("barley", P)
    d = seasonal("dates", P)
    quoted("barley: observations in the regression", b["n"], 518)
    quoted("    years", b["years"], 144)
    quoted("    joint test of the month effects, p", b["p"], 0.023, tol=0.0005)
    quoted("    month 1 effect (%)", 100 * b["eff"][0], 15.3, tol=0.05)
    quoted("    month 2 (%)", 100 * b["eff"][1], 12.2, tol=0.05)
    quoted("    month 6 (%)", 100 * b["eff"][5], -14.8, tol=0.05)
    quoted("    highest month", int(np.argmax(b["eff"])) + 1, 1)
    quoted("    lowest month", int(np.argmin(b["eff"])) + 1, 6)
    quoted("    months 12-4 minus months 5-8 (log points)", 100 * b["diff"], 16.9, tol=0.05)
    quoted("        standard error", 100 * b["dse"], 4.5, tol=0.05)
    quoted("        as a ratio (%)", 100 * (math.exp(b["diff"]) - 1), 18.4, tol=0.05)
    quoted("dates: observations", d["n"], 468)
    quoted("    years", d["years"], 132)
    quoted("    joint test, p", d["p"], 0.30, tol=0.005)
    quoted("    month 12 (%)", 100 * d["eff"][11], -15.7, tol=0.05)
    quoted("    months 12-4 minus 5-8 (log points)", 100 * d["diff"], -0.4, tol=0.05)
    c = comovement(P)
    quoted("years with both prices", c["n_years"], 134)
    quoted("    correlation of annual log levels", c["r_level"], 0.67, tol=0.005)
    quoted("pairs of consecutive years", c["n_dyears"], 70)
    quoted("    correlation of annual changes", c["r_dyear"], 0.42, tol=0.005)
    quoted("pairs of consecutive months with both prices", c["n_months"], 216)
    quoted("    correlation of monthly changes", c["r_month"], 0.12, tol=0.005)
    quoted("barley: consecutive monthly changes", c["n_ac"], 180)
    quoted("    first-order autocorrelation", c["ac1"], -0.20, tol=0.005)
    quoted("barley: consecutive years", c["n_lv"], 104)
    quoted("    autocorrelation of annual log levels", c["ac_level"], 0.69, tol=0.005)
    med_b, med_d = P["barley"].median(), P["dates"].median()
    quoted("median barley price (g per 100 l)", med_b, 10.68, tol=0.005)
    quoted("median dates price", med_d, 7.71, tol=0.005)
    for y, xb, xd in ((-322, 6.5, 5.5), (-309, 8.7, 7.8), (-83, 14.0, 5.7)):
        r = P[P["year"] == y]
        quoted(f"{-y} BC: highest barley price / median", r["barley"].max() / med_b, xb, tol=0.05)
        quoted(f"    highest dates price / median", r["dates"].max() / med_d, xd, tol=0.05)
    quoted("barley, highest price (83 BC)", P["barley"].max(), 149.13, tol=0.005)
    quoted("barley, lowest price", P["barley"].min(), 2.14, tol=0.005)
    q1, q3 = P["barley"].quantile([0.25, 0.75])
    quoted("barley, lower quartile", q1, 6.94, tol=0.005)
    quoted("barley, upper quartile", q3, 19.24, tol=0.005)
    quoted("    ratio of quartiles", q3 / q1, 2.8, tol=0.05)
    quoted("dataset: grams per mina of wool", 500, MINA_SHEKELS * SHEKEL_G, tol=1e-9)
    return b


def selfcheck(F, i_s):
    quoted("SC1: minas of wool per kur", F["cad_le1_wool"][0], 6)
    quoted("SC1: ratios among 5 goods", ratios(SC["goods"])[0], 10)
    quoted("    prices in silver (silver a sixth good)", ratios(SC["goods"] + 1)[1], 5)
    quoted("    ratios among 6 goods", ratios(SC["goods"] + 1)[0], 15)
    quoted("SC2: shekels for 30 busy days", F["ham_273"][0] * SC["days"] / SHEKEL_GRAINS, 1, tol=1e-12)
    quoted("SC3: Old Assyrian, shekels a year on a mina", 12 * F["cad_oa_rate"][0], 18)
    quoted("SC4: barley rate when barley falls 15% (%)", 100 * ((1 + i_s) / (1 - SC["fall"]) - 1), 41.2, tol=0.05)


def main():
    F, Q = facts(), quotes()
    opening(F, Q)
    world(F, Q)
    units(F)
    ex_ox(F)
    i_s, i_b = rates(F)
    own(i_s, i_b)
    debt(F, i_s, i_b)
    misharum(F, Q)
    egypt(F, Q)
    data_check()
    selfcheck(F, i_s)
    print("all Chapter 6 checks passed")


if __name__ == "__main__":
    main()
