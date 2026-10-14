"""Chapter 7 (希腊与罗马：铸币、城邦财政与帝国的贬值): every number quoted in zh/ch07_greekroman.tex.

    python3 checks/check_ch07.py

Inputs are two snapshots:
  greek_facts         quotations from Herodotus (Macaulay), the Athenian Constitution (Kenyon), Xenophon's
                      Revenues (Dakyns), Aristotle's Politics (Ellis) and Ethics (Everyman), Cassius Dio 78 (Cary),
                      Tacitus, Annals VI (Gordon), Lactantius (Fletcher, ANF 7), Kent (1920), Haklai-Rotenberg
                      (2011), Howgego, Butcher, Ponting and Heuchert (2010), Cope (1974), Temin (2001) and Kelly
                      (2021); checked by data/fetch/verify_web_quotes.py
  kelly_egypt_prices  wheat and barley prices in Roman Egypt, AD 3-350, drachmas per artaba, one row per document
                      (Kelly 2021, Appendix 2, CC BY 4.0; medians per document by data/fetch/kelly_prices.py)
The figure module figsrc/fig_ch07.py imports the functions defined here.

Notation of the chapter:
    value of a coin   P = q / v,   v = c + tau (vbar - c),   0 <= tau <= 1                  (eq:greek-value)
                      eta = -dln P / dln c = (1 - tau) c / v
                      c: grams of silver in the coin (metallic value), vbar: its official value and v its
                      exchange value, both in grams of silver; q: grams of silver an artaba of wheat is worth;
                      P: price in coins. tau = 0 is eq:toku-content (Chapter 17); tau = 1 prices at the
                      official value. Haklai-Rotenberg's VM <= VE <= VO, written as a teaching model.
    price ceiling     X_t = (b + d) (p* - pbar / P_t),   P_t = (1 + pi)^t                        (eq:greek-ceiling)
                      linear demand a - b p and supply c0 + d p in prices of the base year; a nominal ceiling pbar
    seigniorage       1 - MP/ME (eq:medieval-seigniorage, Chapter 11)
Units: 1 talent = 60 minas = 6,000 drachmas, 1 mina = 100 drachmas, 1 drachma = 6 obols (Athens; Egypt before
AD 190, 7 after); the Roman pound (libra) = 12 unciae = 288 scrupula; Kent's US units: 1 bushel = 4 pecks
= 32 dry quarts, 1 US dry quart = 1.101221 litres. The examples and the self-check use the teaching inputs
defined below and stated in the text.

The regressions are OLS of the log price on the year (statsmodels), one observation per document.
"""
from __future__ import annotations

import math
import re

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from common import load_snapshot, quoted

# ---------------------------------------------------------------------------------------------------
# Units and teaching inputs stated in the text
OBOLS = 6                     # obols per drachma (Athens): Hipponicus' 600 obols a day are 'a mina'
MINA_DR = 100                 # Ath. Pol. 10: the mina 'raised to the full hundred'
TALENT_MINAS = 60             # the money talent; Solon's weight talent had 63 minas (Ath. Pol. 10)
TALENT_DR = TALENT_MINAS * MINA_DR
YEAR_DAYS = 360               # the year implied by Xenophon's arithmetic
UNCIAE, SCRUPULA = 12, 288    # per Roman pound (Kent: the uncia is one-twelfth; Cope: 24 scrupula = 1 uncia)
QUARTS_PER_BUSHEL = 32
LITRES_PER_DRY_QUART = 1.101221
TROY_OZ_PER_LB = 12
# ex:greek-trust (AD 274): the official value corresponds to the silver of a 70% coin of the same weight per
# unit of face value (Howgego Table 1, 155-180); the reformed coin 'almost 5%' (Haklai-Rotenberg)
REF_FINENESS, REFORMED = 70.0, 5.0
PRE_REFORM = 2.5              # 'around 2 or 3 per cent'
# ex:greek-ceiling: linear demand and supply in prices of 301, a ceiling at the market price of 301
CEIL = dict(a=200.0, b=1.0, c0=0.0, d=1.0, years=(1, 4))
# the self-check
SC = dict(slaves=1200, tau=0.5, c_ratio=0.5, pi=0.2, t=2)


# ---------------------------------------------------------------------------------------------------
# Loaders
def facts() -> dict[str, list[float]]:
    """id -> the numbers of the value column (several are separated by ';'; '2/3' is read as a fraction)."""
    df, _ = load_snapshot("greek_facts", dtype={"value": str})
    out = {}
    for _, r in df.iterrows():
        v = r["value"]
        if isinstance(v, str) and v.strip():
            out[r["id"]] = [float(x.split("/")[0]) / float(x.split("/")[1]) if "/" in x else float(x)
                            for x in v.split(";")]
    return out


def quotes() -> set[str]:
    df, _ = load_snapshot("greek_facts")
    return set(df["id"])


def prices() -> pd.DataFrame:
    df, _ = load_snapshot("kelly_egypt_prices")
    return df


def table(name: str, P: pd.DataFrame | None = None) -> pd.DataFrame:
    """One of Kelly's tables, documents with a year and a price only."""
    P = prices() if P is None else P
    return P[P["table"] == name].dropna(subset=["year", "dr_per_artaba"]).copy()


# ---------------------------------------------------------------------------------------------------
# Teaching models
def fineness_unciae(x: float) -> float:
    """Cope's 'x unciae of alloy per libra of silver': per cent silver in the alloy."""
    return 100 * UNCIAE / (UNCIAE + x)


def fineness_scrupula(s: float) -> float:
    """Cope's 's scrupula of silver per libra of alloy': per cent silver."""
    return 100 * s / SCRUPULA


def exchange_value(c: float, vbar: float, tau: float) -> float:
    """eq:greek-value: v = c + tau (vbar - c)."""
    return c + tau * (vbar - c)


def trust(v: float, c: float, vbar: float) -> float:
    """eq:greek-value solved for tau."""
    return (v - c) / (vbar - c)


def pass_through(c: float, v: float, tau: float) -> float:
    """eq:greek-value: eta = -dln P / dln c = (1 - tau) c / v."""
    return (1 - tau) * c / v


def shortage(t: float, pi: float, a=CEIL["a"], b=CEIL["b"], c0=CEIL["c0"], d=CEIL["d"], pbar=None) -> dict:
    """eq:greek-ceiling: excess demand at a nominal ceiling pbar, t years after it was set, inflation pi."""
    pstar = (a - c0) / (b + d)
    pbar = pstar if pbar is None else pbar
    real = pbar / (1 + pi) ** t
    return dict(pstar=pstar, real=real, demand=a - b * real, supply=c0 + d * real, x=(b + d) * (pstar - real))


def trend(df: pd.DataFrame) -> dict:
    """OLS of the log price on the year: slope (log points a year), its 95% interval, p, R2; and R2 in levels."""
    df = df.assign(lp=np.log(df["dr_per_artaba"]))
    m = smf.ols("lp ~ year", df).fit()
    lo, hi = m.conf_int().loc["year"]
    lin = smf.ols("dr_per_artaba ~ year", df).fit()
    return dict(n=int(m.nobs), b=m.params["year"], lo=lo, hi=hi, p=m.pvalues["year"], r2=m.rsquared,
                r2_lin=lin.rsquared, fit=m)


def cagr(x0: float, x1: float, years: float) -> float:
    return (x1 / x0) ** (1 / years) - 1


# ---------------------------------------------------------------------------------------------------
# The text, section by section
def opening(F, Q):
    P = prices()
    w = table("wheat_private", P)
    post = table("wheat_post274", P)
    quoted("wheat, 270, private (dr per artaba)", w.loc[w["year"] == 270, "dr_per_artaba"].item(), 24)
    quoted("    276, adaeratio", post.loc[post["year"] == 276, "dr_per_artaba"].item(), 200)
    x = post[post["reference"].str.startswith("P.Oxy. LIV 3773")]
    quoted("    c. 340, traders' declarations (P.Oxy. LIV 3773), median in drachmas", x["dr_per_artaba"].item(), 270000)
    quoted("        in talents", x["dr_per_artaba"].item() / TALENT_DR, 45)
    quoted("        prices in the document", x["n_prices"].item(), 7)
    quoted("    276 / 270", 200 / 24, 8.3, tol=0.05)
    quoted("silver: Nero's new standard (%)", F["hr_nero"][1], 80)
    quoted("    late 260s, less than (%)", F["hr_gallienus"][1], 5)
    quoted("Aurelian's reform (CE)", F["hr_aurelian"][0], 274)
    quoted("    silver from about (%)", F["hr_improved"][0], 2)
    quoted("    or (%)", F["hr_improved"][1], 3)
    quoted("    to almost (%)", F["hr_improved"][2], 5)
    quoted("Haklai-Rotenberg: a tenfold rise", F["hr_tenfold"][0], 10)
    quoted("edict (year)", F["kent_301"][0], 301)
    assert {"hdt_lydia", "lac_edict", "lac_blood", "hr_noprice"} <= Q


def world(F, Q):
    quoted("Xenophon born (BC)", -F["xen_born"][0], 431)
    quoted("    died (BC)", -F["xen_died"][0], 354)
    quoted("Solon: mina from (dr)", F["ath_mina"][0], 70)
    quoted("    to (dr)", F["ath_mina"][1], MINA_DR)
    quoted("    weight talent (minas)", F["ath_talent"][0], 63)
    quoted("    odd minas", F["ath_talent"][1], 3)
    quoted("    money talent (minas)", F["ath_talent"][0] - F["ath_talent"][1], TALENT_MINAS)
    quoted("    drachmas per talent", TALENT_DR, F["kl_talent"][0])
    quoted("Diocletian proclaimed (AD)", F["kent_284"][0], 284)
    quoted("    co-Augustus", F["kent_286"][0], 286)
    quoted("    two Caesars", F["kent_286"][1], 293)
    quoted("    abdicated", F["kent_305"][0], 305)
    quoted("    years after the edict", F["kent_305"][1], 4)
    quoted("Caracalla from", F["hr_caracalla"][0], 211)
    quoted("    to", F["hr_caracalla"][1], 217)
    quoted("Lactantius: four princes", F["lac_armies"][0], 4)
    quoted("ANF volume", F["lac_translator"][0], 7)
    quoted("    year", F["lac_translator"][1], 1886)
    quoted("Egypt: a tetradrachm is (drachmas)", F["kl_tetra"][0], 4)
    quoted("    and is worth (denarius)", F["hb_tetra"][0], 1)
    quoted("obols per drachma after AD 190", F["kl_obols"][0], 7)
    quoted("    before", F["kl_obols"][2], 6)
    quoted("Kelly: private wheat price points", F["kl_counts"][0], 40)
    quoted("    state", F["kl_counts"][1], 31)
    P = prices()
    quoted("    private wheat rows in the appendix", (P["table"] == "wheat_private").sum(), 40)
    quoted("    state wheat rows", (P["table"] == "wheat_state").sum(), 31)
    quoted("    barley rows before 274", (P["table"] == "barley").sum(), 25)
    quoted("    wheat rows after 274", (P["table"] == "wheat_post274").sum(), 23)
    quoted("    barley rows after 274", (P["table"] == "barley_post274").sum(), 11)
    quoted("    documents in all", len(P), 130)
    quoted("Kelly's text: P.Mich. II 123, AD", F["kl_p123"][0], 45)
    quoted("    median (dr)", F["kl_p123"][1], 3.0)
    w = P[P["table"] == "wheat_private"]
    r45 = w[w["year"] == 45]
    assert r45["reference"].item().startswith("P.Mich. II 127"), r45      # the appendix: AD 45 is P.Mich. II 127
    quoted("    appendix: AD 45 row (P.Mich. II 127), median", r45["dr_per_artaba"].item(), 7.445, tol=1e-9)
    quoted("        prices", r45["n_prices"].item(), 6)
    r123 = w[w["reference"].str.startswith("P.Mich. II 123")]
    quoted("    appendix: P.Mich. II 123, year", r123["year"].item(), 46)
    quoted("        price", r123["dr_per_artaba"].item(), 8.73, tol=1e-9)
    assert {"hb_closed", "kl_midpoint"} <= Q


def coin(F, Q):
    assert {"pol_stamp", "pol_carriage", "ne_custom", "ne_security", "ne_depreciation", "xen_frontier",
            "xen_export"} <= Q
    quoted("five beds for a house", F["ne_beds"][0], 5)


def laurion(F, Q):
    quoted("Herodotus: drachmas a head", F["hdt_laureion"][0], 10)
    quoted("    ships", F["hdt_ships"][0], 200)
    quoted("Ath. Pol.: talents of profit", F["ath_maroneia"][0], 100)
    quoted("    richest men", F["ath_lend"][0], 100)
    quoted("    talent each", F["ath_lend"][1], 1)
    quoted("    triremes", F["ath_triremes"][0], 100)
    quoted("    Xerxes' advance, years later", F["ath_xerxes"][0], 3)
    dr = F["ath_maroneia"][0] * TALENT_DR
    quoted("ex:greek-laurion: 100 talents in drachmas", dr, 600000)
    heads = dr / F["hdt_laureion"][0]
    quoted("    heads at 10 dr", heads, 60000)
    quoted("    Herodotus' Athenians (5.97)", F["hdt_30000"][0], 30000)
    quoted("    ratio", heads / F["hdt_30000"][0], 2)
    quoted("    30,000 at 10 dr, in talents", F["hdt_30000"][0] * F["hdt_laureion"][0] / TALENT_DR, 50)
    quoted("    talents per trireme (Ath. Pol.)", F["ath_maroneia"][0] / F["ath_triremes"][0], 1)
    quoted("    Herodotus' 200 ships at 1 talent", F["hdt_ships"][0] * 1, 200)
    quoted("        / the Maroneia profit", F["hdt_ships"][0] / F["ath_maroneia"][0], 2)
    quoted("    50 talents / the Maroneia profit", 50 / F["ath_maroneia"][0], 0.5)
    assert {"ath_distribute", "ath_terms", "hdt_naval"} <= Q


def xenophon(F, Q):
    quoted("Nicias: slaves", F["xen_nicias"][0], 1000)
    quoted("    obol a day each", F["xen_obol"][0], 1)
    quoted("    drachmas a day", 1000 / OBOLS, 166.7, tol=0.05)
    quoted("    talents a year (360 days)", 1000 / OBOLS * YEAR_DAYS / TALENT_DR, 10)
    quoted("Hipponicus: slaves", F["xen_hipponicus"][0], 600)
    quoted("    a mina a day: 600 obols in drachmas", F["xen_hipponicus"][0] / OBOLS, MINA_DR)
    quoted("Philemonides: slaves", F["xen_philemonides"][0], 300)
    quoted("    half a mina: 300 obols / 100 dr", F["xen_philemonides"][0] / OBOLS / MINA_DR, F["xen_philemonides"][1])
    quoted("plan: first slaves", F["xen_1200"][0], 1200)
    quoted("    within five or six years", F["xen_1200"][1], 6000)
    n, rev = F["xen_60"][0], F["xen_60"][2]
    quoted("    6,000 slaves at an obol: talents a year", rev, 60)
    days = rev * TALENT_DR * OBOLS / n
    quoted("    implied days in the year", days, YEAR_DAYS)
    quoted("    60 talents in drachmas", rev * TALENT_DR, 360000)
    quoted("        in obols", rev * TALENT_DR * OBOLS, 2160000)
    quoted("    6,000 x 365 days, in talents", n * 365 / OBOLS / TALENT_DR, 60.8, tol=0.05)
    quoted("    10,000 slaves: talents", F["xen_100"][1], 100)
    quoted("        10,000 x 360 / 6 / 6,000", F["xen_100"][0] * YEAR_DAYS / OBOLS / TALENT_DR, 100)
    quoted("    1,200 slaves: talents (self-check)", SC["slaves"] * YEAR_DAYS / OBOLS / TALENT_DR, 12)
    quoted("public slaves per citizen", F["xen_public"][0], 3)
    quoted("    for 30,000 citizens", 3 * F["hdt_30000"][0], 90000)
    quoted("        talents a year at an obol", 3 * F["hdt_30000"][0] * YEAR_DAYS / OBOLS / TALENT_DR, 900)
    quoted("        / the Maroneia profit", 900 / F["ath_maroneia"][0], 9)
    quoted("Decelea (BC)", -F["xen_decelea"][0], 413)
    quoted("    deserted slaves, more than", F["xen_deserted"][0], 20000)
    assert {"xen_more", "xen_enough", "xen_hoard", "xen_gold", "xen_nodanger"} <= Q


def coins(F, Q):
    """tab:greek-silver and the arithmetic of fineness."""
    quoted("Nero (CE)", F["hr_nero"][0], 64)
    quoted("    4 parts silver to 1 copper (%)", 100 * F["hr_nero"][2] / (F["hr_nero"][2] + F["hr_nero"][3]), 80)
    quoted("    successors: old standard about (%)", F["hr_pre64"][2], 90)
    quoted("Trajan re-establishes the Neronian standard (CE)", F["hr_trajan"][0], 100)
    quoted("Cope: Nero's first debased standard, 1 uncia (%)", fineness_unciae(1), 92.3, tol=0.05)
    quoted("    5 unciae (%)", fineness_unciae(F["cope_severus"][1]), 70.6, tol=0.05)
    quoted("    Severus, AD", F["cope_severus"][2], 193)
    quoted("    15 unciae (%)", fineness_unciae(F["cope_severus"][3]), 44.4, tol=0.05)
    quoted("    base metal until c. AD", F["cope_base"][0], 294)
    quoted("Haklai-Rotenberg: Severus about (%)", F["hr_severus"][0], 50)
    t1 = F["hb_t1"]
    quoted("Howgego Table 1: to 155 (%)", t1[1], 80)
    quoted("    from 155 (%)", t1[2], 70)
    quoted("    from 180 (%)", t1[4], 67)
    quoted("Caracalla: weight of the antoninianus (denarii)", F["hr_caracalla"][2], 1.5)
    # Cope (1974) p. 103 (row cope_alloy; also Table III item 10a, p. 107): the same alloy for denarii and
    # antoniniani after AD 214, i.e. Severus' 15-unciae standard
    quoted("    Cope: same alloy for denarius and antoninianus from AD", F["cope_alloy"][0], 214)
    quoted("    Severus' standard, so Caracalla's antoninianus (%)", fineness_unciae(F["cope_severus"][3]), 44.4,
           tol=0.05)
    quoted("Gallienus, Cope: 3 scrupula (%)", fineness_scrupula(F["cope_gallienus"][0]), 1.04, tol=0.005)
    quoted("    6 scrupula (%)", fineness_scrupula(F["cope_animal"][0]), 2.08, tol=0.005)
    quoted("    Cope Table X: 24 scrupula = 1 uncia", F["cope_tx24"][0] / F["cope_tx24"][1], SCRUPULA / UNCIAE)
    quoted("        per mille", F["cope_tx24"][2], 1000 * 24 / SCRUPULA, tol=0.5)
    quoted("        6 scrupula, per mille", F["cope_tx6"][1], 1000 * 6 / SCRUPULA, tol=0.5)
    quoted("        3 scrupula, per mille", F["cope_tx3"][1], 1000 * 3 / SCRUPULA, tol=0.5)
    quoted("Kent: unciae per pound", F["kent_uncia"][0], UNCIAE)
    quoted("Haklai n. 42 on Cope (1972): Gallienus, from (%)", F["hr_cope"][0], 2)
    quoted("    to (%)", F["hr_cope"][1], 3)
    quoted("tetradrachm: debasement began (AD 164/5)", F["hb_parthian"][0], 164)
    quoted("    took hold (AD 167/8)", F["hb_parthian"][2], 167)
    quoted("Diocletian's reforms: gold standard (CE)", F["hr_diocletian"][0], 286)
    quoted("    monetary reform (294/96)", F["hr_diocletian"][1], 294)
    quoted("    Currency Edict", F["hr_diocletian"][3], 301)
    assert {"hr_xray", "hr_expect", "hr_mistrust", "hr_constantine", "hr_onlybankers", "hr_notlost", "pol_compact",
            "kl_wine", "kent_meals", "hr_n108c"} <= Q
    quoted("Haklai n. 108: the 301 rise from Diocletian's own reform of", F["hr_n108d"][1], 294)
    quoted("    /", F["hr_n108d"][2], 96)
    quoted("    the two edicts of", F["hr_n108c"][0], 301)
    # the Egyptian tetradrachm (Howgego Tables 2 and 3)
    t2 = F["hb_t2"]
    quoted("tetradrachm: to 167 (%)", t2[1], 18)
    quoted("    167/8-168/9 (%)", t2[2], 5)
    quoted("    from 169/70 (%)", t2[3], 10)
    rows = {k: F[k] for k in ("hb_t3a", "hb_t3b", "hb_t3c", "hb_t3d", "hb_t3e", "hb_t3f")}
    for k, r in rows.items():   # fineness x weight = silver, to the table's rounding
        assert abs(r[0] / 100 * r[1] - r[2]) <= 0.051, (k, r)
        assert abs(r[4] / 100 * r[3] - r[5]) <= 0.051, (k, r)
    quoted("    silver to 167 (g)", F["hb_t3b"][2], 2.3)
    quoted("    from 185/6 (g)", F["hb_t3f"][2], 0.6)
    quoted("    ratio", F["hb_t3b"][2] / F["hb_t3f"][2], 3.83, tol=0.005)
    quoted("    fall (%)", 100 * (1 - F["hb_t3f"][2] / F["hb_t3b"][2]), 74, tol=0.5)
    quoted("denarius silver to 167 (g), the same period as the tetradrachm", F["hb_t3b"][5], 2.4)
    quoted("    from 185/6 (g)", F["hb_t3f"][5], 1.9)
    quoted("    fall (%)", 100 * (1 - F["hb_t3f"][5] / F["hb_t3b"][5]), 21, tol=0.5)
    quoted("silver per coin, from 80% to 2% (fall, %)", 100 * (1 - 2 / 80), 97.5, tol=1e-9)
    assert {"dio_debased", "hr_disguise", "hb_classic", "lac_taxpayers"} <= Q


def seigniorage(F):
    """ex:greek-seign with eq:medieval-seigniorage."""
    old, new = fineness_unciae(F["cope_severus"][1]), fineness_unciae(F["cope_severus"][3])
    quoted("ex:greek-seign (1): silver of a new denarius / old", new / old, 0.63, tol=0.005)
    quoted("    ME rises by", old / new, 1.59, tol=0.005)
    quoted("    gross seigniorage rate at par exchange (%)", 100 * (1 - new / old), 37, tol=0.5)
    w = F["hr_caracalla"][2]
    quoted("(2) antoninianus: silver per denarius of face value / old", w / 2, 0.75)
    quoted("    gross seigniorage rate (%)", 100 * (1 - w / 2), 25)
    quoted("    the minority view (Haklai n. 41): tariff (denarii)", F["hr_n41"][0], 1.5)
    quoted("    if tariffed at 1.5 denarii (Haklai n. 41): seigniorage (%)", 100 * (1 - w / F["hr_n41"][0]), 0)
    quoted("(3) both: silver per denarius of face value / pre-193", new / old * w / 2, 0.47, tol=0.005)


def egypt_prices(F):
    quoted("Antonine plague: into Egypt (AD 166/7)", F["hb_loss"][0], 166)
    quoted("    population loss, from (%)", F["hb_loss"][2], 20)
    quoted("    to (%)", F["hb_loss"][3], 30)
    quoted("Kelly: barley, private price points", F["kl_barley"][0], 21)
    quoted("    state", F["kl_barley"][1], 4)
    quoted("    share of state prices (%)", F["kl_barley"][2], 16)
    quoted("    = the barley rows before 274", F["kl_barley"][0] + F["kl_barley"][1], 25)
    quoted("    wheat: share of state prices (%)", 100 * F["kl_counts"][1] / sum(F["kl_counts"]), 44, tol=0.5)
    P = prices()
    w = table("wheat_private", P)
    pre = w[w["year"] < 160]
    quoted("private wheat before 160: documents", len(pre), 11)
    quoted("    from AD", pre["year"].min(), 45)
    quoted("    median (dr)", pre["dr_per_artaba"].median(), 8.73, tol=1e-9)
    alt = pre["dr_per_artaba"].where(pre["year"] != 45, F["kl_p123"][1])   # Kelly's text: AD 45 at 3.0
    quoted("    median with AD 45 at Kelly's 3.0 (deeper box)", alt.median(), 8.73, tol=1e-9)
    quoted("    lowest", pre["dr_per_artaba"].min(), 5)
    quoted("    highest", pre["dr_per_artaba"].max(), 12)
    mid = w[(w["year"] >= 190) & (w["year"] <= 270)]
    quoted("190-270: documents", len(mid), 27)
    quoted("    median (dr)", mid["dr_per_artaba"].median(), 16)
    quoted("    documents at exactly 16", (mid["dr_per_artaba"] == 16).sum(), 9)
    quoted("    in estate accounts or letters", mid["nature"].str.contains("estate", case=False).sum(), 26)
    quoted("    in a temple account", mid["nature"].str.contains("temple", case=False).sum(), 1)
    quoted("    from the Arsinoite nome", (mid["nome"] == "Arsinoite").sum(), 20)
    quoted("    a date range 202-231", mid["date"].str.startswith("202-31").sum(), 1)
    quoted("    lowest", mid["dr_per_artaba"].min(), 9)
    quoted("    highest", mid["dr_per_artaba"].max(), 28)
    late = w[(w["year"] >= 249) & (w["year"] <= 270)]
    quoted("249-270: documents", len(late), 18)
    quoted("    median", late["dr_per_artaba"].median(), 16)
    quoted("    multiples of four", (late["dr_per_artaba"] % 4 == 0).mean(), 1.0)
    at160 = w[w["year"] == 160]
    quoted("private wheat dated exactly 160: documents", len(at160), 2)
    quoted("    lower price", at160["dr_per_artaba"].min(), 5.52, tol=1e-9)
    quoted("    higher price", at160["dr_per_artaba"].max(), 11)
    quoted("    median to 160 inclusive", w.loc[w["year"] <= 160, "dr_per_artaba"].median(), 8.73, tol=1e-9)
    quoted("no private wheat document between 160 and 190", ((w["year"] > 160) & (w["year"] < 190)).sum(), 0)
    # Kelly: obol fractions in wine and barley, none in private wheat after 160
    after160 = w[w["year"] > 160]
    nums = [float(x) for a in after160["amounts"].astype(str) for x in re.findall(r"\d+(?:\.\d+)?", a)]
    assert not after160["amounts"].astype(str).str.contains("ob").any() and all(x == int(x) for x in nums)
    quoted("private wheat after 160: documents with obols or fractions",
           int(after160["amounts"].astype(str).str.contains("ob").sum()) + sum(x != int(x) for x in nums), 0)
    bm = table("barley", P)
    bm = bm[(bm["year"] >= 190) & (bm["year"] <= 270)]
    quoted("barley 190-270: documents", len(bm), 10)
    quoted("    with obols", bm["amounts"].astype(str).str.contains("ob").sum(), 4)
    quoted("Kelly: no private wheat price with obols after AD", F["kl_fraction"][0], 160)
    quoted("Kelly: amounts in multiples of", F["kl_fours"][0], 4)
    quoted("274/75: Egyptian tetradrachm reformed with the imperial coinage (Haklai n. 107)", F["hr_n107b"][0], 274)
    quoted("    and 75", F["hr_n107b"][1], 75)
    quoted("    slight increase in silver in", F["hr_n107"][2], 274)
    quoted("192 (P.Cair.Goodsp. 30)", w.loc[w["year"] == 192, "dr_per_artaba"].item(), 18)
    quoted("    prices behind the median", w.loc[w["year"] == 192, "n_prices"].item(), 3)
    quoted("190-270 median / pre-160 median", 16 / 8.73, 1.83, tol=0.005)
    s = table("wheat_state", P)
    quoted("state wheat: documents", len(s), 31)
    eight = s[s["dr_per_artaba"] == 8]
    quoted("    at exactly 8 dr", len(eight), 20)
    quoted("    below 8 (fig:greek_sectors)", (s["dr_per_artaba"] < 8).sum(), 6)
    quoted("    above 8", (s["dr_per_artaba"] > 8).sum(), 5)
    quoted("    share (%)", 100 * len(eight) / len(s), 65, tol=0.5)
    quoted("    last price of 8 (AD)", eight["year"].max(), 216)
    quoted("    246, compulsory purchase (P.Oxy. XLII 3048)", s.loc[s["year"] == 246, "dr_per_artaba"].item(), 24)
    quoted("    documents before 246", (s["year"] < 246).sum(), 30)
    post = table("wheat_post274", P)
    for y, v in ((301, 640), (304.5, 1200), (311, 1200), (312.5, 2000), (314, 7000), (315, 3000), (327, 17333),
                 (335, 84000), (338, 144000)):
        quoted(f"wheat after 274: {y:g}", post.loc[post["year"] == y, "dr_per_artaba"].item(), v)
    quoted("    335: talents", 84000 / TALENT_DR, 14)
    quoted("    338: talents", 144000 / TALENT_DR, 24)
    quoted("    314: the two prices", 7000, (6000 + 8000) / 2)
    quoted("    c. 340-50 (P.Abinn. 68)", post.loc[post["year"] == 345, "dr_per_artaba"].item(), 300000)
    quoted("276 -> c. 340: per cent a year", 100 * cagr(200, 270000, 64), 11.9, tol=0.05)
    quoted("301 -> 314: per cent a year", 100 * cagr(640, 7000, 13), 20.2, tol=0.05)
    quoted("    times", 7000 / 640, 10.9, tol=0.05)
    quoted("pre-160 median -> c. 340: times", 270000 / 8.73, 30900, rel=0.002)
    quoted("190-270 median -> 276: times", 200 / 16, 12.5)


def model(F):
    """eq:greek-value: ex:greek-commodus and ex:greek-trust."""
    c0, c1 = F["hb_t3b"][2] / 4, F["hb_t3f"][2] / 4          # grams of silver per drachma
    quoted("ex:greek-commodus: silver per drachma to 167 (g)", c0, 0.575, tol=1e-9)
    quoted("    from 185/6 (g)", c1, 0.15, tol=1e-9)
    p0, p1 = 8.73, 18.0
    q = p0 * c0
    quoted("    wheat in silver before 160 (g per artaba)", q, 5.02, tol=0.005)
    quoted("    (1) content theory: price in 192 (dr)", q / c1, 33.5, tol=0.05)
    quoted("        times", c0 / c1, 3.83, tol=0.005)
    quoted("    observed: 192 / pre-160", p1 / p0, 2.06, tol=0.005)
    eta = math.log(p1 / p0) / math.log(c0 / c1)
    quoted("    (2) pass-through", eta, 0.54, tol=0.005)
    quoted("    (3) wheat in silver in 192 (g per artaba)", p1 * c1, 2.70, tol=0.005)
    v1 = q / p1
    quoted("        exchange value per drachma (g)", v1, 0.279, tol=0.0005)
    quoted("        v / c", v1 / c1, 1.86, tol=0.005)
    tau = trust(v1, c1, c0)
    quoted("        tau (vbar = 0.575 g)", tau, 0.30, tol=0.005)
    quoted("        pass-through at this tau (formula)", pass_through(c1, v1, tau), 0.37, tol=0.005)
    quoted("    with the 190-270 median of 16: times", 16 / p0, 1.83, tol=0.005)
    quoted("        pass-through", math.log(16 / p0) / math.log(c0 / c1), 0.45, tol=0.005)
    quoted("        tau", trust(q / 16, c1, c0), 0.39, tol=0.005)
    quoted("    (4) if q rose as much as the price: tau", trust(q * (p1 / p0) / p1, c1, c0), 1)
    # ex:greek-trust: the reform of 274
    ratio = 200 / 16
    quoted("ex:greek-trust: price jump", ratio, 12.5)
    quoted("    (1) content theory, silver 2.5% -> 5%: prices x", PRE_REFORM / REFORMED, 0.5)
    vbar, c_new = 1.0, REFORMED / REF_FINENESS
    quoted("    (2) c / vbar after the reform", c_new, 0.071, tol=0.0005)
    v_new = vbar / ratio
    quoted("        v / vbar", v_new, 0.08)
    quoted("        tau after", trust(v_new, c_new, vbar), 0.009, tol=0.0005)
    quoted("        tau = 0 would give x", vbar / c_new, 14)
    quoted("    (3) lowest v / vbar before the reform", ratio * c_new, 0.89, tol=0.005)
    quoted("    with 24 (270): x", 200 / 24, 8.3, tol=0.05)
    quoted("        tau after", trust(vbar / (200 / 24), c_new, vbar), 0.05, tol=0.005)


def edict(F, Q):
    quoted("schedules, at least", F["kent_32"][0], 32)
    quoted("items, over", F["kent_32"][1], 1000)
    quoted("copies", F["kent_35"][0], 35)
    quoted("preamble: not fourfold", F["kent_fourfold"][0], 4)
    quoted("    or eightfold", F["kent_fourfold"][1], 8)
    gold, cents = F["kent_gold"]
    quoted("gold: denarii per pound", gold, 50000)
    quoted("    cents per denarius", cents, 0.434)
    den = cents / 100                                        # dollars per denarius
    modius = 2 * F["kent_modius"][0]                         # military modius in dry quarts
    quoted("military modius (dry quarts)", modius, 15.9, tol=1e-9)
    quoted("    in litres", modius * LITRES_PER_DRY_QUART, 17.5, tol=0.05)
    barley = F["kent_barley"][0] * modius / QUARTS_PER_BUSHEL / den
    quoted("ex:greek-wage: barley, denarii per military modius", barley, 99.95, tol=0.005)
    quoted("    rounded", barley, 100, tol=0.5)
    wage = F["kent_labor"][0] / den
    quoted("    farm labourer, denarii a day", wage, 24.88, tol=0.005)
    quoted("    rounded", wage, 25, tol=0.5)
    mason = F["kent_mason"][0] / den
    quoted("    mason or carpenter, denarii a day", mason, 50, tol=0.05)
    share = 25 / 100
    quoted("    a day's wage buys (military modius)", share, 0.25)
    quoted("        dry quarts", share * modius, 3.98, tol=0.005)
    quoted("        litres", share * modius * LITRES_PER_DRY_QUART, 4.4, tol=0.05)
    oz = F["kent_pound"][1] * TROY_OZ_PER_LB
    quoted("Roman pound in troy ounces", oz, 10.5, tol=1e-9)
    quoted("    Kent's implied gold price (dollars per troy oz)", den * gold / oz, 20.67, tol=0.005)
    quoted("Aezani: denarii per pound of gold", F["hr_aezani"][0], 72000)
    quoted("    / Kent's 50,000", F["hr_aezani"][0] / gold, 1.44)
    quoted("    cents per denarius at 72,000", cents * gold / F["hr_aezani"][0], 0.301, tol=0.0005)
    quoted("    Kent's dollar prices times", gold / F["hr_aezani"][0], 0.69, tol=0.005)
    quoted("litres per US dry quart (stated)", LITRES_PER_DRY_QUART, 1.101, tol=0.0005)
    quoted("Haklai n. 108: years after Aurelian's reform", F["hr_n108"][1], 25)
    quoted("    301 - 274", 301 - 274, 27)
    assert {"kent_notfixed", "kent_maximum", "kent_capital", "kent_buyer", "kent_withhold", "kent_soldier",
            "kent_greed", "kent_debasing", "kent_tin", "kent_copper", "kent_upward", "kent_unknown",
            "kent_impartial", "kent_wheat", "hr_n108b", "kent_christian", "kent_onesided", "kent_highest",
            "kent_courts", "kent_vicious", "kent_standard", "kent_disappeared", "kent_observed", "kent_dealers", "kent_resisted",
            "kent_hoarded", "kent_clandestine", "kent_region", "kent_withdrawn"} <= Q
    quoted("Kent: 'not much if at all over four years'", F["kent_fouryears"][0], 4)


def ceiling():
    """ex:greek-ceiling with eq:greek-ceiling."""
    pi = cagr(640, 7000, 13)
    s0 = shortage(0, pi)
    quoted("ex:greek-ceiling: market price of 301", s0["pstar"], 100)
    quoted("    quantity", s0["supply"], 100)
    quoted("    elasticity of demand at p*", CEIL["b"] * s0["pstar"] / s0["demand"], 1)
    quoted("    inflation (% a year)", 100 * pi, 20.2, tol=0.05)
    s1 = shortage(1, pi)
    quoted("    after 1 year: real ceiling", s1["real"], 83.2, tol=0.05)
    quoted("        supplied", s1["supply"], 83.2, tol=0.05)
    quoted("        demanded", s1["demand"], 116.8, tol=0.05)
    quoted("        shortage", s1["x"], 33.6, tol=0.05)
    s4 = shortage(4, pi)
    quoted("    after 4 years: price level x", (1 + pi) ** 4, 2.09, tol=0.005)
    quoted("        real ceiling", s4["real"], 47.9, tol=0.05)
    quoted("        demanded", s4["demand"], 152.1, tol=0.05)
    quoted("        shortage", s4["x"], 104.2, tol=0.05)
    return pi


def test():
    P = prices()
    w = table("wheat_private", P)
    tw = trend(w[(w["year"] >= 190) & (w["year"] <= 270)])
    quoted("wheat 190-270: documents", tw["n"], 27)
    quoted("    slope (log points a year, %)", 100 * tw["b"], -0.09, tol=0.005)
    quoted("    95% interval, low", 100 * tw["lo"], -0.67, tol=0.005)
    quoted("    high", 100 * tw["hi"], 0.49, tol=0.005)
    quoted("    p", tw["p"], 0.75, tol=0.005)
    quoted("    R2 (log)", tw["r2"], 0.004, tol=0.0005)
    quoted("    R2 (levels)", tw["r2_lin"], 0.016, tol=0.0005)
    b = table("barley", P)
    tb = trend(b[(b["year"] >= 190) & (b["year"] <= 270)])
    quoted("barley 190-270: documents", tb["n"], 10)
    quoted("    slope (%)", 100 * tb["b"], 1.46, tol=0.005)
    quoted("    95% interval, low", 100 * tb["lo"], 0.28, tol=0.005)
    quoted("    high", 100 * tb["hi"], 2.64, tol=0.005)
    quoted("    p", tb["p"], 0.021, tol=0.0005)
    quoted("    R2 (log)", tb["r2"], 0.50, tol=0.005)
    quoted("    over 80 years: times", math.exp(80 * tb["b"]), 3.2, tol=0.05)
    bb = b[(b["year"] >= 190) & (b["year"] <= 270)]
    quoted("    state compulsory purchase among them (209)", bb.loc[bb["year"] == 209, "dr_per_artaba"].item(), 5)
    t9 = trend(bb[bb["year"] != 209])
    quoted("    without 209: documents", t9["n"], 9)
    quoted("        slope (%)", 100 * t9["b"], 1.35, tol=0.005)
    quoted("        95% interval, low", 100 * t9["lo"], 0.19, tol=0.005)
    quoted("        high", 100 * t9["hi"], 2.52, tol=0.005)
    quoted("        p", t9["p"], 0.029, tol=0.0005)
    assert {"kl_sectors", "kl_dampen", "kl_taxes", "kl_noedict", "kl_plague", "kl_endogenous", "kl_poly"} <= facts().keys() | quotes()
    k = facts()["kl_r2"]
    quoted("Kelly: wheat R2 (log, from 190)", k[0], 0.01)
    quoted("    n", k[1], 27)
    quoted("    barley R2", k[2], 0.61)
    quoted("    n", k[3], 10)
    r = {k: v for k, v in zip(("wheat", "barley", "wine", "donkeys", "blended"), facts()["kl_t1c"])}
    quoted("Kelly Table 1, 190-270: wheat (% a year)", r["wheat"], 0.1)
    quoted("    barley", r["barley"], 1.4)
    quoted("    wine", r["wine"], 0.7)
    quoted("    donkeys", r["donkeys"], 1.5)
    quoted("    blended", r["blended"], 1.1)
    quoted("    blended over 80 years: times", 1.011 ** 80, 2.40, tol=0.005)
    a = facts()["kl_t1a"]
    quoted("    50-160 blended", a[4], 0.3)
    m = facts()["kl_t1b"]
    quoted("    160-190 wheat", m[0], 0.7)
    quoted("    160-190 blended", m[4], 0.8)
    quoted("Kelly rule of thumb (% a year after 150)", facts()["kl_rule"][2], 1)
    return tw, tb


def case33(F, Q):
    quoted("Tacitus: twelve in the hundred", F["tac_twelve"][0], 12)
    quoted("    respite (years)", F["tac_respite"][0], 1.5)
    quoted("    two-thirds of debts in Italian land", F["tac_twothirds"][0], 2 / 3, tol=1e-9)
    quoted("    great sesterces lent", F["tac_loan"][0], 100000)
    quoted("    the Twelve Tables: twelve in the hundred", F["tac_tables"][0], 12)
    quoted("    years", F["tac_terms"][0], 3)
    quoted("    security, times the loan", F["tac_terms"][1], 2)
    quoted("Temin: crisis (CE)", F["tm_33"][0], 33)
    quoted("    three years", F["tm_tiberius"][0], 3)
    quoted("    interest rates from (%)", F["tm_interest"][0], 4)
    quoted("    to (%)", F["tm_interest"][1], 12)
    assert {"tac_scarcity", "tac_hoard", "tac_restored", "tm_land", "tm_finley", "tm_wrong", "tm_rathbone",
            "tac_caesar", "tac_impunity", "tm_debate", "tm_polanyi", "tm_primarily", "tm_loose"} <= Q


def selfcheck(F):
    quoted("SC1: 15 unciae (%)", fineness_unciae(15), 44.4, tol=0.05)
    quoted("    3 scrupula (%)", fineness_scrupula(3), 1.04, tol=0.005)
    quoted("SC2: 1,200 slaves, talents a year", SC["slaves"] * YEAR_DAYS / OBOLS / TALENT_DR, 12)
    v = exchange_value(SC["c_ratio"], 1.0, SC["tau"])
    quoted("SC3: v / vbar", v, 0.75)
    quoted("    prices x", 1 / v, 1.33, tol=0.005)
    quoted("    pass-through (log)", math.log(1 / v) / math.log(1 / SC["c_ratio"]), 0.42, tol=0.005)
    s = shortage(SC["t"], SC["pi"])
    quoted("SC5: real ceiling after 2 years at 20%", s["real"], 69.4, tol=0.05)
    quoted("    demand", s["demand"], 130.6, tol=0.05)
    quoted("    shortage", s["x"], 61.1, tol=0.05)
    quoted("SC6: 1 - 44.4/70.6 (%)", 100 * (1 - fineness_unciae(15) / fineness_unciae(5)), 37, tol=0.5)


def main():
    F, Q = facts(), quotes()
    opening(F, Q)
    world(F, Q)
    coin(F, Q)
    laurion(F, Q)
    xenophon(F, Q)
    coins(F, Q)
    seigniorage(F)
    egypt_prices(F)
    model(F)
    edict(F, Q)
    ceiling()
    test()
    case33(F, Q)
    selfcheck(F)
    print("all Chapter 7 checks passed")


if __name__ == "__main__":
    main()
