"""Chapter 14 (非洲与美洲：黄金、贝币与没有货币的帝国): every number quoted in zh/ch14_africa.tex.

    python3 checks/check_ch14.py

Input is the snapshot africa_money_facts (and, for one teaching input, Chapter 10's medieval_credit_facts): quotations from al-Umari (with al-Maqrizi and Ibn Khaldun), Ibn Battuta,
Barth, Burton, Ellis, Dalzel (with Norris and J. F.), Robinson, Gardner, Garcilaso de la Vega (with Blas Valera),
Acosta, Oviedo, Peter Martyr, Dell and Kocherlakota, checked by data/fetch/verify_web_quotes.py (rows read on page
images are marked as such in the snapshot's metadata).
The figure module figsrc/fig_ch14.py imports the functions defined here.

Models (the chapter's key equations):
    carrying cost       P_B / P_A - 1 <= c                                     (eq:africa-carry; Ch. 13 eq:silver-arbitrage)
    default risk        p (1 + i) = 1 + r_f                                    (eq:africa-risk)
    storehouse          S_{t+1} = (1 - delta) S_t + I - G_t; S* = (I - G)/delta  (eq:africa-store)
    holding a commodity money   1 + r^m = (1 - delta) P_t / P_{t+1}           (eq:africa-hold)
    short strings (Ch. 11)      seigniorage rate = 1 - MP/ME                    (eq:medieval-seigniorage)
Units: 1 pound sterling = 20 shillings = 240 pence; 1 lb avoirdupois = 453.59237 g; a long ton = 2,240 lb;
a cowrie string is 40 shells loose, 39 strung (J. F.); Ellis's head is 50 strings, J. F.'s cabess 4,000 shells.
"""
from __future__ import annotations

import math

from common import load_snapshot, quoted

GRAM_PER_LB = 453.59237
LB_PER_LONG_TON = 2240
SHILLING_PER_POUND = 20
PENCE_PER_SHILLING = 12

# Teaching inputs stated in the text
R_F = 0.15                 # ex:africa-gold: the lenders' alternative return on the money for the life of the loan
                           # (Ch. 10, tab:islamic-rates: Italian commercial loans 10%-18% a year)
STORE_SURPLUS = 5.0        # ex:africa-store: yearly inflow minus normal use, % of a year's consumption
DELTA_DRY = 0.05           # ex:africa-store: share of the stock lost in a year, chuño and dried food
DELTA_FRESH = 0.25         # ex:africa-store: the same for food that keeps badly
FAMINE = 40.0              # ex:africa-store: extra draw in a famine year, % of a year's consumption
FAMINE_YEAR = 30           # ex:africa-store: the famine comes in year 30 after the storehouses are built
CACAO_DELTA = 0.10         # ex:africa-cacao: share of a stock of cacao beans lost in a year
CACAO_INFL = 0.05          # ex:africa-cacao: prices in beans rise 5% in a good harvest year


def _snapshot_facts():
    df, _ = load_snapshot("africa_money_facts", dtype={"value": str})
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


def ch10_quotes() -> dict[str, str]:
    """Chapter 10's quotations (Bell, Brooks and Moore on Italian interest rates), for the teaching input R_F."""
    df, _ = load_snapshot("medieval_credit_facts", dtype={"value": str})
    return dict(zip(df["id"], df["quote"].fillna("")))


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


def gross_gap(p_b: float, p_a: float) -> float:
    """eq:africa-carry: what carrying one unit from A to B earns, as a share of its price in A."""
    return p_b / p_a - 1.0


def repay_prob(i: float, r_f: float = R_F) -> float:
    """eq:africa-risk: the repayment probability at which a risk-neutral lender breaks even."""
    return (1.0 + r_f) / (1.0 + i)


def store_path(delta: float, T: int, surplus: float = STORE_SURPLUS, famine: float = 0.0,
               famine_year: int = FAMINE_YEAR) -> tuple[list[float], float]:
    """eq:africa-store from S_0 = 0: S_{t+1} = max(0, (1-delta) S_t + surplus - famine draw).
    Returns the path and the part of the famine draw the stock could not cover."""
    s, short = [0.0], 0.0
    for t in range(1, T + 1):
        nxt = (1.0 - delta) * s[-1] + surplus
        if t == famine_year and famine:
            short = max(0.0, famine - nxt)
            nxt = max(0.0, nxt - famine)
        s.append(nxt)
    return s, short


def store_star(delta: float, surplus: float = STORE_SURPLUS) -> float:
    """eq:africa-store: the stock at which losses just offset the surplus."""
    return surplus / delta


def half_life(delta: float) -> float:
    """Years for the gap between S_t and S* to halve."""
    return math.log(2.0) / -math.log(1.0 - delta)


def hold_return(delta: float, infl: float) -> float:
    """eq:africa-hold: r^m = (1 - delta) / (1 + infl) - 1."""
    return (1.0 - delta) / (1.0 + infl) - 1.0


# --- the series the figures draw ---------------------------------------------
def per_gold(F) -> list[tuple[str, str, float, float]]:
    """Cowries for a dinar or mithqal of gold: (place, year label, low, high)."""
    return [
        ("maldives", "1344", F["battuta_four_bostu"][0], F["battuta_twelve_bostu"][0]),
        ("mali", "1352", F["battuta_mali_1150"][0], F["battuta_mali_1150"][0]),
        ("kano", "1851", F["barth_kano_mithkal"][0], F["barth_kano_mithkal"][0]),
        ("timbuktu", "1851", F["barth_timbuktu"][0], F["barth_timbuktu"][1]),
    ]


def per_shilling(F) -> list[tuple[str, int, float]]:
    """Cowries for a shilling sterling: (place, year, shells)."""
    head = F["ellis_head"][0] * F["ellis_string"][0]                       # Ellis: 50 strings x 40 = 2,000
    dollar_d = F["burton_rates"][0]                                         # Burton: the dollar is 4s. 6d. = 54d.
    shilling_d = PENCE_PER_SHILLING
    lagos = F["burton_rates"][2] * head + F["burton_rates"][3] * F["ellis_string"][0]
    pairs = F["robinson_value"]                                             # 2,000 = 12d, 16d, 18d
    return [
        ("coast", 1720, F["gardner_1720"][2] / (F["gardner_1720"][3] * SHILLING_PER_POUND)),
        ("jf", 1793, F["dalzel_table"][4] / F["dalzel_table"][6]),
        ("whydah", 1863, F["burton_rates"][1] * head / (dollar_d / shilling_d)),
        ("lagos", 1863, lagos / (dollar_d / shilling_d)),
        ("kaffi", 1894, F["robinson_220000"][0] / (F["robinson_220000"][1] * SHILLING_PER_POUND)),
        ("lokoja", 1894, pairs[0] / (pairs[1] / shilling_d)),
        ("zaria", 1894, pairs[0] / (pairs[2] / shilling_d)),
        ("kano", 1894, pairs[0] / (pairs[3] / shilling_d)),
    ]


def shells_per_lb(F) -> tuple[float, float]:
    """J. F. (1793): 16,000 shells weigh 42 lb; Robinson (1894): 220,000 weigh 1,000 lb."""
    return F["dalzel_table"][4] / F["dalzel_ounce_weight"][0], F["robinson_220000"][0] / F["robinson_220000"][2]


def carry(F) -> dict[str, float]:
    """Robinson's porters: the fee as a share of the value of the cowries in a 95 lb load, at Lokoja's 2,000 a shilling."""
    _, per_lb = shells_per_lb(F)
    fee4, fee4_s, load_lb, days = F["robinson_carry4"]
    lokoja = dict((p, v) for p, _, v in per_shilling(F))["lokoja"]
    load_shells = load_lb * per_lb
    load_s = load_shells / lokoja
    zaria_fee, zaria_fee_s, miles = F["robinson_zaria_carry"]
    return dict(load_shells=load_shells, load_s=load_s, fee4=fee4 / load_shells, per_day=fee4 / load_shells / days,
                zaria=zaria_fee / load_shells, days=days, miles=miles,
                gap_zaria=F["robinson_value"][2] / F["robinson_value"][1] - 1.0,
                gap_kano=F["robinson_value"][3] / F["robinson_value"][1] - 1.0)


# ---------------------------------------------------------------------------
def intro(F):
    print("\n== opening: Mansa Musa in Cairo ==")
    quoted("Mansa Musa reaches Cairo: AH 724", F["maqrizi_1324"][0], 724, tol=0)
    quoted("  = AD 1324", F["maqrizi_1324"][1], 1324, tol=0)
    quoted("gold in Cairo that year: at least 25 dirhams a mithqal", F["umari_gold_25"][0], 25, tol=0)
    quoted("gold when al-Umari wrote: at most 22", F["umari_gold_22"][0], 22, tol=0)
    quoted("  for twelve years", F["umari_gold_22"][1], 12, tol=0)
    quoted("fall in the price of gold, at least (%)", 100 * (1 - F["umari_gold_22"][0] / F["umari_gold_25"][0]), 12, tol=1e-9)
    quoted("one hundred loads of gold", F["umari_loads"][0], 100, tol=0)
    quoted("al-Maqrizi: 14,000 young slave women", F["maqrizi_slaves"][0], 14_000, tol=0)


def world(F):
    print("\n== the world: gold, salt, copper, cloth, cowries ==")
    quoted("Takedda copper: 100 mithqal of copper", F["umari_copper"][0], 100, tol=0)
    quoted("  for 66 2/3 mithqal of gold", F["umari_copper"][1], 66.6667, tol=1e-4)
    quoted("  copper per unit of gold, by weight", F["umari_copper"][0] / F["umari_copper"][1], 1.5, tol=1e-4)
    quoted("Takedda bars: thin, per gold ducat", F["battuta_takedda_bars"][0], 400, tol=0)
    quoted("  thick, per gold ducat (low)", F["battuta_takedda_bars"][1], 600, tol=0)
    quoted("  thick, per gold ducat (high)", F["battuta_takedda_bars"][2], 700, tol=0)
    quoted("Kanem: a piece of cloth is ten cubits", F["umari_kanem_cloth"][0], 10, tol=0)
    quoted("Sijilmasa to Taghaza (days)", F["battuta_taghaza_days"][0], 25, tol=0)
    quoted("a camel carries two slabs of salt", F["battuta_camel_two"][0], 2, tol=0)
    lo_w, hi_w, lo_m, hi_m, top = F["battuta_salt_price"]
    quoted("salt at Iwalatan, a camel load (low)", lo_w, 8, tol=0)
    quoted("  (high)", hi_w, 10, tol=0)
    quoted("salt at Mali (low)", lo_m, 20, tol=0)
    quoted("  (high)", hi_m, 30, tol=0)
    quoted("  sometimes", top, 40, tol=0)
    quoted("a slab at Iwalatan (low)", lo_w / F["battuta_camel_two"][0], 4, tol=0)
    quoted("  (high)", hi_w / F["battuta_camel_two"][0], 5, tol=0)
    quoted("a slab at Mali (low)", lo_m / F["battuta_camel_two"][0], 10, tol=0)
    quoted("  (high)", hi_m / F["battuta_camel_two"][0], 15, tol=0)
    quoted("Maldives: a cotta is 12,000 shells", F["battuta_units"][0], 12_000, tol=0)
    quoted("  a bostu 100,000", F["battuta_units"][1], 100_000, tol=0)
    quoted("  four bostu for a gold dinar", F["battuta_four_bostu"][0], 4 * F["battuta_units"][1], tol=0)
    quoted("  when cheap, twelve bostu", F["battuta_twelve_bostu"][0], 12 * F["battuta_units"][1], tol=0)
    quoted("Mali and Gao: 1,150 for a gold dinar", F["battuta_mali_1150"][0], 1150, tol=0)
    quoted("Ibn Battuta leaves the Maldives", F["battuta_leave_maldives"][0], 1344, tol=0)
    quoted("  sets out from Sijilmasa", F["battuta_sijilmasa"][0], 1352, tol=0)
    quoted("  leaves Takedda", F["battuta_1353"][0], 1353, tol=0)
    quoted("  caravan with about 600 slave girls", F["battuta_600"][0], 600, tol=0)


def gold(F):
    print("\n== sec:africa-gold ==")
    # al-Maqrizi's six dirhams
    quoted("al-Maqrizi: the dinar fell to six dirhams", F["maqrizi_six"][0], 6, tol=0)
    quoted("  six against al-Umari's 25: share", F["maqrizi_six"][0] / F["umari_gold_25"][0], 0.24, tol=1e-9)
    # salt: carrying cost
    lo_w, hi_w, lo_m, hi_m, top = F["battuta_salt_price"]
    quoted("salt gap, smallest: 20/10 - 1 (%)", 100 * gross_gap(lo_m, hi_w), 100, tol=1e-9)
    quoted("salt gap, largest of the usual: 30/8 - 1 (%)", 100 * gross_gap(hi_m, lo_w), 275, tol=1e-9)
    quoted("salt gap at 40: 40/8 - 1 (%)", 100 * gross_gap(top, lo_w), 400, tol=1e-9)
    quoted("salt: Mali/Iwalatan price ratio (low)", lo_m / hi_w, 2, tol=0)
    quoted("  (high)", hi_m / lo_w, 3.75, tol=0)
    # the loans
    lent, gain = F["umari_loan_gain"]
    quoted("lent 300 dinars", lent, 300, tol=0)
    quoted("  700 of gain", gain, 700, tol=0)
    i_total = gain / lent - 1
    i_profit = (lent + gain) / lent - 1
    quoted("reading 1: 700 in all, i (%)", 100 * i_total, 133.3, tol=0.05)
    quoted("reading 2: 700 profit, 1,000 back, i (%)", 100 * i_profit, 233.3, tol=0.05)
    quoted("teaching input r_f (%)", 100 * R_F, 15, tol=0)
    ch10 = ch10_quotes()
    said(ch10, "bbm_medici_loans", "10-12%")               # Ch. 10, tab:islamic-rates: the low end, 10%
    said(ch10, "bbm_genoese_london", "18%")                # the high end, 18%
    p1, p2 = repay_prob(i_total), repay_prob(i_profit)
    quoted("p, reading 1", p1, 0.49, tol=0.005)
    quoted("p, reading 2", p2, 0.345, tol=0.0005)
    quoted("p, reading 1, r_f = 0", repay_prob(i_total, 0.0), 0.43, tol=0.005)
    quoted("p, reading 2, r_f = 0", repay_prob(i_profit, 0.0), 0.30, tol=1e-9)
    quoted("Ibn Khaldun: the Kuwayk lent 50,000 dinars", F["khaldun_loan"][0], 50_000, tol=0)


def cowries(F):
    print("\n== sec:africa-cowrie: units ==")
    quoted("a string: 40 shells loose", F["dalzel_string"][0], 40, tol=0)
    quoted("  39 strung", F["dalzel_string"][1], 39, tol=0)
    quoted("Ellis: a string is 40", F["ellis_string"][0], 40, tol=0)
    quoted("Ellis: a head is 50 strings", F["ellis_head"][0], 50, tol=0)
    head = F["ellis_head"][0] * F["ellis_string"][0]
    quoted("  = 2,000 shells", head, 2000, tol=0)
    t = F["dalzel_table"]
    quoted("J. F.: string", t[0], 40, tol=0)
    quoted("J. F.: galhina", t[1], 200, tol=0)
    quoted("J. F.: ackey", t[2], 1000, tol=0)
    quoted("J. F.: cabess", t[3], 4000, tol=0)
    quoted("J. F.: ounce trade", t[4], 16_000, tol=0)
    quoted("J. F.: cabess in shillings", t[5], 10, tol=0)
    quoted("J. F.: ounce trade in shillings", t[6], 40, tol=0)
    quoted("  ounce trade = 4 cabess", t[4] / t[3], 4, tol=0)
    quoted("J. F.: an ounce weighs 42 lb", t[7], F["dalzel_ounce_weight"][0], tol=0)
    quoted("J. F. note: the ounce of gold is worth 4 pounds", F["dalzel_ounce_value"][0], 4, tol=0)
    quoted("  the ounce trade half of it (shillings)", F["dalzel_ounce_value"][0] * SHILLING_PER_POUND / 2, t[6], tol=0)
    quoted("Dalzel's note: a cabess is ten shillings", F["dalzel_cabess"][0], t[5], tol=0)
    quoted("Norris: five cabess = fifty shillings", F["dalzel_five_cabess"][1] / F["dalzel_five_cabess"][0], t[5], tol=0)
    quoted("Gardner 1720: a grand cabess of 100 strings", F["gardner_1720"][1], 100, tol=0)
    quoted("  = 4,000 shells", F["gardner_1720"][2], F["gardner_1720"][1] * F["ellis_string"][0], tol=0)
    quoted("  worth about 1 pound", F["gardner_1720"][3], 1, tol=0)
    # Norris 1772
    oz, wives, each = F["dalzel_norris_80"]
    quoted("Norris: 80 ounces", oz, 80, tol=0)
    quoted("  320 wives, each a cabess of 4,000", wives * each, oz * t[4], tol=0)
    quoted("  shells in all", wives * each, 1_280_000, tol=0)
    quoted("  value (pounds)", oz * t[6] / SHILLING_PER_POUND, 160, tol=0)
    quoted("  weight (lb)", oz * t[7], 3360, tol=0)
    quoted("  weight (long tons)", oz * t[7] / LB_PER_LONG_TON, 1.5, tol=0)
    quoted("  one woman's load (lb)", t[7] / (t[4] / each), 10.5, tol=0)

    print("\n== the gap between the Maldives and Mali ==")
    lo = F["battuta_four_bostu"][0] / F["battuta_mali_1150"][0]
    hi = F["battuta_twelve_bostu"][0] / F["battuta_mali_1150"][0]
    quoted("a shell in Mali is worth x times its Maldives value (low)", lo, 348, tol=0.5)
    quoted("  (when cheap in the Maldives)", hi, 1043, tol=0.5)
    quoted("  implied carrying cost at least (%)", 100 * (lo - 1), 34_700, tol=50)

    print("\n== shells per shilling, shells per lb ==")
    ps = dict((p, v) for p, _, v in per_shilling(F))
    quoted("1720 (Gardner)", ps["coast"], 200, tol=0)
    quoted("1793 (J. F.)", ps["jf"], 400, tol=0)
    quoted("Burton: the dollar is 54d", F["burton_rates"][0], 54, tol=0)
    quoted("  buys 2.5 heads at Whydah", F["burton_rates"][1], 2.5, tol=0)
    quoted("  2.5 heads = shells", F["burton_rates"][1] * head, 5000, tol=0)
    quoted("1863 Whydah", ps["whydah"], 1111, tol=0.5)
    quoted("  Lagos: 3 heads and 20 strings = shells", F["burton_rates"][2] * head + F["burton_rates"][3] * 40, 6800, tol=0)
    quoted("1863 Lagos", ps["lagos"], 1511, tol=0.5)
    quoted("Burton: a head now 21.5d", F["burton_rates"][4], 21.5, tol=0)
    quoted("  54/2.5 (d)", F["burton_rates"][0] / F["burton_rates"][1], 21.6, tol=1e-9)
    quoted("1894 Lokoja", ps["lokoja"], 2000, tol=0)
    quoted("1894 Kaffi (220,000 = 6 pounds)", ps["kaffi"], 1833, tol=0.5)
    quoted("1894 Zaria", ps["zaria"], 1500, tol=0)
    quoted("1894 Kano", ps["kano"], 1333, tol=0.5)
    quoted("Robinson's porter: 10,000 cowries = 5s", F["robinson_carry4"][0] / F["robinson_carry4"][1], ps["lokoja"], tol=0)
    quoted("1720 -> 1894 Lokoja: ratio", ps["lokoja"] / ps["coast"], 10, tol=0)
    quoted("  years", 1894 - 1720, 174, tol=0)
    quoted("  a year (%)", 100 * compound(ps["lokoja"] / ps["coast"], 1894 - 1720), 1.33, tol=0.005)
    quoted("1793 -> 1863 Whydah: ratio", ps["whydah"] / ps["jf"], 2.78, tol=0.005)
    quoted("  a year (%)", 100 * compound(ps["whydah"] / ps["jf"], 1863 - 1793), 1.47, tol=0.005)
    jf_lb, rob_lb = shells_per_lb(F)
    quoted("J. F.: shells per lb", jf_lb, 381, tol=0.5)
    quoted("  grams a shell", GRAM_PER_LB / jf_lb, 1.19, tol=0.005)
    quoted("Robinson: shells per lb", rob_lb, 220, tol=0)
    quoted("  grams a shell", GRAM_PER_LB / rob_lb, 2.06, tol=0.005)
    v_jf = t[6] / t[7]
    v_rob = F["robinson_220000"][1] * SHILLING_PER_POUND / F["robinson_220000"][2]
    quoted("value of a lb of shells, 1793 (s)", v_jf, 0.95, tol=0.005)
    quoted("value of a lb of shells, 1894 (s)", v_rob, 0.12, tol=0)
    quoted("  ratio", v_jf / v_rob, 7.9, tol=0.05)
    # gold: Mali 1352 vs Kano 1851
    quoted("Mali 1352 -> Kano 1851: ratio", F["barth_kano_mithkal"][0] / F["battuta_mali_1150"][0], 3.48, tol=0.005)
    quoted("  years", 1851 - 1352, 499, tol=0)
    quoted("  a year (%)", 100 * compound(F["barth_kano_mithkal"][0] / F["battuta_mali_1150"][0], 499), 0.25, tol=0.005)
    quoted("Kano 1851: a mithqal in dollars", F["barth_kano_mithkal"][0] / F["barth_kano_dollar"][0], 1.6, tol=1e-9)
    quoted("Timbuktu low", F["barth_timbuktu"][0], 3500, tol=0)
    quoted("Timbuktu high", F["barth_timbuktu"][1], 4500, tol=0)

    print("\n== carrying cowries (Robinson) ==")
    c = carry(F)
    quoted("a 95 lb load: shells", c["load_shells"], 20_900, tol=0)
    quoted("  worth at Lokoja (s)", c["load_s"], 10.45, tol=1e-9)
    quoted("4-day fee: share of the load (%)", 100 * c["fee4"], 47.8, tol=0.05)
    quoted("  a day (%)", 100 * c["per_day"], 12, tol=0.05)
    quoted("to Zaria, 180 miles: 20,000 cowries", F["robinson_zaria_carry"][0], 20_000, tol=0)
    quoted("  = 10s", F["robinson_zaria_carry"][1], 10, tol=0)
    quoted("  share of the load (%)", 100 * c["zaria"], 95.7, tol=0.05)
    quoted("price gap Lokoja -> Zaria (%)", 100 * c["gap_zaria"], 33.3, tol=0.05)
    quoted("price gap Lokoja -> Kano (%)", 100 * c["gap_kano"], 50, tol=1e-9)
    quoted("the horse: fifteen porters", F["robinson_horse"][0], 15, tol=0)
    quoted("  shells (fifteen 95 lb loads)", F["robinson_horse"][0] * c["load_shells"], 313_500, tol=0)
    quoted("  pounds at Lokoja's rate", F["robinson_horse"][0] * c["load_s"] / SHILLING_PER_POUND, 7.8, tol=0.05)
    quoted("Kaffi: ten days to raise the cowries", F["robinson_kaffi"][0], 10, tol=0)
    quoted("Kaffi: 220,000 cowries", F["robinson_220000"][0], 220_000, tol=0)
    quoted("  weigh 1,000 lb = 95 lb loads", F["robinson_220000"][2] / F["robinson_carry4"][2], 10.5, tol=0.05)
    lo, hi_lo, hi_hi = F["robinson_mt_silver"]
    quoted("Maria Theresa dollar: silver (s)", lo, 2, tol=0)
    quoted("  premium, low (%)", 100 * (hi_lo / lo - 1), 50, tol=0)
    quoted("  premium, high (%)", 100 * (hi_hi / lo - 1), 125, tol=0)
    quoted("  at Kaffi: 3s 6d, premium (%)", 100 * (F["robinson_mt_kaffi"][0] / lo - 1), 75, tol=0)
    quoted("the dollar bears the date 1780", F["robinson_mt_vienna"][0], 1780, tol=0)
    n, each = F["robinson_mt_140"]
    quoted("Zaria: 140 dollars at 5,000", n * each, 700_000, tol=0)
    quoted("  needed: nearly 750,000", F["robinson_750k"][0], 750_000, tol=0)
    quoted("  the dollar fell (%)", 100 * (1 - F["robinson_mt_20pct"][2] / F["robinson_mt_20pct"][1]), F["robinson_mt_20pct"][0], tol=1e-9)
    # Kano: dollar in cowries, 1851 and 1894
    quoted("Kano 1894: a dollar, low (cowries)", hi_lo * ps["kano"], 4000, tol=1e-6)
    quoted("Kano 1894: a dollar, high (cowries)", hi_hi * ps["kano"], 6000, tol=1e-6)
    quoted("Kano 1851: a dollar", F["barth_kano_dollar"][0], 2500, tol=0)

    print("\n== slaves as money ==")
    lo_c, hi_c, lo_p, hi_p = F["robinson_slave_price"]
    quoted("Zaria: a slave 100,000-300,000 cowries", lo_c, 100_000, tol=0)
    quoted("  = 3-9 pounds", lo_p, 3, tol=0)
    quoted("  cowries per shilling implied", lo_c / (lo_p * SHILLING_PER_POUND), 1667, tol=0.5)
    quoted("  weight of the low price (lb)", lo_c / rob_lb, 455, tol=0.5)
    quoted("  weight of the high price (lb)", hi_c / rob_lb, 1364, tol=0.5)
    quoted("  porter loads, low", lo_c / c["load_shells"], 4.8, tol=0.05)
    quoted("  porter loads, high", hi_c / c["load_shells"], 14.4, tol=0.05)
    quoted("as many as 300 on sale at one time", F["robinson_300"][0], 300, tol=0)
    quoted("tribute to Sokoto in slaves: at least (%)", 100 * F["robinson_tribute"][0], 75, tol=0)
    quoted("Adamawa: 10,000 slaves a year", F["robinson_adamawa"][0], 10_000, tol=0)
    quoted("Kano: about 100", F["robinson_kano_cloth"][0], 100, tol=0)

    print("\n== Bornu (Barth 1851) ==")
    r = F["barth_32"][0]
    quoted("32 shells a rotl", r, 32, tol=0)
    quoted("dollar at 45 rotls = shells", F["barth_fall"][0] * r, 1440, tol=0)
    quoted("dollar at 50 rotls = shells", F["barth_fall"][1] * r, 1600, tol=0)
    quoted("dollar at 100 rotls = shells", F["barth_100"][0] * r, F["barth_100"][1], tol=0)
    quoted("  700 more than Kano", F["barth_100"][1] - F["barth_kano_dollar"][0], F["barth_100"][2], tol=0)
    quoted("  high/low", F["barth_100"][1] / (F["barth_fall"][0] * r), 2.22, tol=0.005)
    quoted("Barth: cowries in sacks of 20,000", F["barth_sack"][0], 20_000, tol=0)
    quoted("  counting 500,000 = sacks", F["barth_heroic"][0] / F["barth_sack"][0], 25, tol=0)
    quoted("cowries into Bornu, demand on the coast after", F["barth_drain"][0], 1849, tol=0)
    quoted("Barth's year 1848", F["barth_1848"][0], 1848, tol=0)


def dahomey(F):
    print("\n== case: Dahomey ==")
    quoted("Bossa Ahadee dies", F["dalzel_1774"][0], 1774, tol=0)
    quoted("Adahoonzou II dies", F["dalzel_1789"][0], 1789, tol=0)
    cab = F["dalzel_cabess"][0]
    man, woman = F["dalzel_cap"]
    quoted("cap for a man (cabess)", man, 32, tol=0)
    quoted("  in pounds", man * cab / SHILLING_PER_POUND, 16, tol=0)
    quoted("cap for a woman (cabess)", woman, 26, tol=0)
    quoted("  in pounds", woman * cab / SHILLING_PER_POUND, 13, tol=0)
    mkt = F["dalzel_1786"][0]
    quoted("1786: a prime slave, about (pounds)", mkt, 30, tol=0)
    quoted("cap / market, man (%)", 100 * man * cab / SHILLING_PER_POUND / mkt, 53.3, tol=0.05)
    quoted("cap / market, woman (%)", 100 * woman * cab / SHILLING_PER_POUND / mkt, 43.3, tol=0.05)
    strung = F["dalzel_string"][1]
    lo, hi = F["dalzel_short"]
    s_lo, s_hi = lo / strung, hi / strung
    quoted("short strings: 3 of 39 (%)", 100 * s_lo, 7.7, tol=0.05)
    quoted("  6 of 39 (%)", 100 * s_hi, 15.4, tol=0.05)
    quoted("  MP/ME, 36 of 39 (%)", 100 * (strung - lo) / strung, 92.3, tol=0.05)
    quoted("  MP/ME, 33 of 39 (%)", 100 * (strung - hi) / strung, 84.6, tol=0.05)
    paid_lo = man * cab / SHILLING_PER_POUND * (1 - s_hi)
    paid_hi = man * cab / SHILLING_PER_POUND * (1 - s_lo)
    quoted("a man, paid in short strings: high (pounds)", paid_hi, 14.8, tol=0.05)
    quoted("  low (pounds)", paid_lo, 13.5, tol=0.05)
    quoted("  high / market (%)", 100 * paid_hi / mkt, 49, tol=0.5)
    quoted("  low / market (%)", 100 * paid_lo / mkt, 45, tol=0.5)
    quoted("two slaves: the king takes one", F["dalzel_two_slaves"][1], 1, tol=0)
    quoted("three: the king takes two", F["dalzel_two_slaves"][3], 2, tol=0)
    quoted("bankrupt traders had 60-70 slaves' worth (low)", F["dalzel_bankrupt"][0], 60, tol=0)
    quoted("  (high)", F["dalzel_bankrupt"][1], 70, tol=0)


def inca(F):
    print("\n== sec:africa-inca ==")
    quoted("Garcilaso: no coined money for twenty years after his time", F["garcilaso_coined"][0], 20, tol=0)
    quoted("three kinds of storehouses", F["garcilaso_stores"][0], 3, tol=0)
    quoted("storehouses every three leagues", F["garcilaso_roads"][0], 3, tol=0)
    quoted("Valera: scarcely four reals", F["valera_four_reals"][0], 4, tol=0)
    quoted("  exempt until 25", F["valera_boys"][0], 25, tol=0)
    quoted("  exempt over 50", F["valera_fifty"][0], 50, tol=0)
    quoted("  years owing labour (25 to 50)", F["valera_fifty"][0] - F["valera_boys"][0], 25, tol=0)
    quoted("accountants: four a village", F["garcilaso_accountants"][0], 4, tol=0)
    quoted("  up to 20", F["garcilaso_accountants"][1], 20, tol=0)
    quoted("  or 30", F["garcilaso_accountants"][2], 30, tol=0)
    # storage model
    print("-- ex:africa-store (teaching inputs) --")
    quoted("surplus (% of a year's consumption)", STORE_SURPLUS, 5, tol=0)
    quoted("delta, dried (%)", 100 * DELTA_DRY, 5, tol=0)
    quoted("delta, fresh (%)", 100 * DELTA_FRESH, 25, tol=0)
    quoted("S*, dried (% of a year)", store_star(DELTA_DRY), 100, tol=1e-9)
    quoted("S*, fresh (% of a year)", store_star(DELTA_FRESH), 20, tol=1e-9)
    quoted("  in months, dried", 12 * store_star(DELTA_DRY) / 100, 12, tol=1e-9)
    quoted("  in months, fresh", 12 * store_star(DELTA_FRESH) / 100, 2.4, tol=1e-9)
    quoted("half-life, dried (years)", half_life(DELTA_DRY), 13.5, tol=0.05)
    quoted("half-life, fresh (years)", half_life(DELTA_FRESH), 2.4, tol=0.05)
    sd, _ = store_path(DELTA_DRY, FAMINE_YEAR)
    sf, _ = store_path(DELTA_FRESH, FAMINE_YEAR)
    quoted("year 30: stock, dried (before the famine draw)", sd[-1], 78.5, tol=0.05)
    quoted("year 30: stock, fresh", sf[-1], 20, tol=0.05)
    quoted("famine draw", FAMINE, 40, tol=0)
    _, short_d = store_path(DELTA_DRY, FAMINE_YEAR, famine=FAMINE)
    _, short_f = store_path(DELTA_FRESH, FAMINE_YEAR, famine=FAMINE)
    quoted("shortfall, dried", short_d, 0, tol=0)
    quoted("shortfall, fresh", short_f, 20, tol=0.05)
    quoted("  left after the famine, dried", sd[-1] - FAMINE, 38.5, tol=0.05)
    # the colonial mita
    quoted("mita: from 1573", F["dell_mita"][0], 1573, tol=0)
    quoted("  to 1812", F["dell_mita"][1], 1812, tol=0)
    quoted("  years", F["dell_mita"][1] - F["dell_mita"][0], 239, tol=0)
    quoted("Acosta: two arrobas", F["acosta_arrobas"][0], 2, tol=0)
    quoted("  four arrobas = a hundredweight, so two = half", F["acosta_arrobas"][0] / F["acosta_hundredweight"][0], 0.5, tol=0)
    quoted("  ladders above 150 estados", F["acosta_150"][0], 150, tol=0)
    quoted("coca at Potosí: above half a million a year", F["acosta_coca"][0], 500_000, tol=0)
    quoted("Dell: consumption lower by about (%)", F["dell_25"][0], 25, tol=0)
    quoted("Dell: stunting higher by about (pp)", F["dell_6"][0], 6, tol=0)


def cacao(F):
    print("\n== sec:africa-cacao ==")
    rabbit, beans4, fruits = F["oviedo_rabbit"]
    quoted("a rabbit: ten beans", rabbit, 10, tol=0)
    quoted("four beans: eight fruits", fruits / beans4, 2, tol=0)
    quoted("a slave: about 100 beans", F["oviedo_slave"][0], 100, tol=0)
    quoted("  = rabbits", F["oviedo_slave"][0] / rabbit, 10, tol=0)
    quoted("Acosta: five cacaos", F["acosta_five"][0], 5, tol=0)
    quoted("  thirty", F["acosta_thirty"][0], 30, tol=0)
    quoted("  pirate burned above 100,000 cargoes", F["acosta_pirate"][0], 100_000, tol=0)
    print("-- ex:africa-cacao (teaching inputs) --")
    quoted("delta (%)", 100 * CACAO_DELTA, 10, tol=0)
    quoted("inflation (%)", 100 * CACAO_INFL, 5, tol=0)
    quoted("r^m, stable prices (%)", 100 * hold_return(CACAO_DELTA, 0.0), -10, tol=1e-9)
    quoted("r^m, prices up 5% (%)", 100 * hold_return(CACAO_DELTA, CACAO_INFL), -14.3, tol=0.05)
    ps = dict((p, v) for p, _, v in per_shilling(F))
    quoted("cowries 1720-1894: r^m against gold (%)", 100 * hold_return(0.0, compound(ps["lokoja"] / ps["coast"], 174)),
           -1.31, tol=0.005)


def selfcheck():
    print("\n== selfcheck ==")
    # 1: a gap and a cost
    quoted("Q1: 12/9 - 1 (%)", 100 * gross_gap(12, 9), 33.3, tol=0.05)
    # 2: lender
    quoted("Q2: p = 1.1/1.5", repay_prob(0.5, 0.10), 0.733, tol=0.0005)
    quoted("Q2: p = 1.1/1.2", repay_prob(0.2, 0.10), 0.917, tol=0.0005)
    # 3: storage
    quoted("Q3: S* = 3/0.1", store_star(0.10, 3.0), 30, tol=1e-9)
    quoted("Q3: S* = 3/0.02", store_star(0.02, 3.0), 150, tol=1e-9)
    # 4: holding cacao
    quoted("Q4: (1 - 0.2)/0.95 - 1 (%)", 100 * hold_return(0.20, -0.05), -15.8, tol=0.05)
    # 5: short strings
    quoted("Q5: 1 - 35/39 (%)", 100 * (1 - 35 / 39), 10.3, tol=0.05)
    quoted("Q5: 1 - 35/40 (%)", 100 * (1 - 35 / 40), 12.5, tol=0)
    # 6: shells for a horse
    quoted("Q6: 6 pounds at 1,500 a shilling", 6 * SHILLING_PER_POUND * 1500, 180_000, tol=0)
    quoted("Q6: lb at 220 a lb", 6 * SHILLING_PER_POUND * 1500 / 220, 818, tol=0.5)
    quoted("Q6: porter loads of 95 lb", 6 * SHILLING_PER_POUND * 1500 / 220 / 95, 8.6, tol=0.05)


def from_quotes(Q):
    print("\n== numbers read straight from the quotations ==")
    said(Q, "maqrizi_1324", "724", "1324")
    said(Q, "umari_gold_25", "vingt-cinq")
    said(Q, "umari_gold_22", "vingt-deux", "douze ans")
    said(Q, "umari_loads", "cent charges")
    said(Q, "umari_loan_gain", "trois cents", "sept cents")
    said(Q, "umari_copper", "cent mitqal", "soixante-six mitqal et deux tiers")
    said(Q, "umari_kanem_cloth", "dix coudées")
    said(Q, "maqrizi_slaves", "quatorze mille")
    said(Q, "maqrizi_six", "six dirhems")
    said(Q, "khaldun_loan", "50.000")
    said(Q, "battuta_units", "douze mille", "cent mille")
    said(Q, "battuta_four_bostu", "quatre bostoû")
    said(Q, "battuta_twelve_bostu", "douze bostoû")
    said(Q, "battuta_mali_1150", "onze cent cinquante")
    said(Q, "battuta_leave_maldives", "745", "1344")
    said(Q, "battuta_sijilmasa", "753", "1352")
    said(Q, "battuta_taghaza_days", "vingt-cinq jours")
    said(Q, "battuta_camel_two", "deux")
    said(Q, "battuta_salt_price", "huit à dix", "vingt à trente", "quarante")
    said(Q, "battuta_takedda_bars", "Quatre cents", "six cents ou sept cents")
    said(Q, "battuta_1353", "754", "1353")
    said(Q, "battuta_600", "six cents")
    said(Q, "barth_kano_1851", "1851")
    said(Q, "barth_kano_dollar", "2,500")
    said(Q, "barth_kano_mithkal", "four thousand")
    said(Q, "barth_timbuktu", "three thousand five hundred", "four thousand five hundred")
    said(Q, "barth_1848", "1848")
    said(Q, "barth_drain", "1849")
    said(Q, "barth_sack", "20,000")
    said(Q, "barth_heroic", "500,000")
    said(Q, "barth_32", "two-and-thirty")
    said(Q, "barth_fall", "forty or fifty")
    said(Q, "barth_100", "one hundred rotls", "three thousand two hundred", "seven hundred")
    said(Q, "burton_march", "December 13th")
    said(Q, "burton_rates", "4s. 6d.", "2½ heads", "3 heads and 20 strings", "1s. 9½d.")
    said(Q, "ellis_string", "forty")
    said(Q, "ellis_head", "fifty strings")
    said(Q, "dalzel_1774", "70", "1774")
    said(Q, "dalzel_1789", "1789")
    said(Q, "dalzel_norris_80", "eighty ounces", "three hundred and twenty", "four thousand")
    said(Q, "dalzel_ounce_value", "four pounds", "half that value")
    said(Q, "dalzel_ounce_weight", "forty-two pounds", "a ton and a half")
    said(Q, "dalzel_table", "40 cowries", "200", "1000", "4000", "16000", "10 0", "40 0", "42 0 0")
    said(Q, "dalzel_five_cabess", "five cabess", "fifty shillings")
    said(Q, "dalzel_1786", "thirty pounds")
    said(Q, "dalzel_cap", "thirty-two cabesses", "twenty-six cabesses")
    said(Q, "dalzel_cabess", "ten shillings")
    said(Q, "dalzel_two_slaves", "two slaves", "relinquish one", "if three, two")
    said(Q, "dalzel_short", "three to six")
    said(Q, "dalzel_string", "Forty", "39")
    said(Q, "dalzel_bankrupt", "sixty or seventy")
    said(Q, "robinson_1894", "1894")
    said(Q, "robinson_1895", "1895")
    said(Q, "robinson_carry4", "ten thousand", "five shillings", "ninety-five pounds", "four days")
    said(Q, "robinson_horse", "fifteen")
    said(Q, "robinson_220000", "two hundred and twenty thousand", "£6", "a thousand pounds")
    said(Q, "robinson_mt_kaffi", "three shillings and sixpence")
    said(Q, "robinson_mt_vienna", "1780")
    said(Q, "robinson_kaffi", "ten days")
    said(Q, "robinson_mt_silver", "two shillings", "three to four shillings and sixpence")
    said(Q, "robinson_zaria_carry", "twenty thousand", "ten shillings", "one hundred and eighty miles")
    said(Q, "robinson_750k", "three-quarters of a million")
    said(Q, "robinson_mt_140", "one hundred and forty", "five thousand")
    said(Q, "robinson_mt_20pct", "20 per cent", "five thousand to four thousand")
    said(Q, "robinson_value", "two thousand", "a shilling", "one shilling and fourpence", "one shilling and sixpence")
    said(Q, "robinson_slave_price", "one hundred thousand to three hundred thousand", "three to nine pounds")
    said(Q, "robinson_300", "three hundred")
    said(Q, "robinson_tribute", "three quarters")
    said(Q, "robinson_adamawa", "ten thousand")
    said(Q, "robinson_kano_cloth", "one hundred")
    said(Q, "robinson_three", "three characteristics")
    said(Q, "gardner_100t", "100 tons")
    said(Q, "gardner_1720", "1720", "100 strings", "4,000 shells", "£1")
    said(Q, "garcilaso_coined", "twenty years")
    said(Q, "garcilaso_stores", "three kinds")
    said(Q, "garcilaso_roads", "three leagues")
    said(Q, "valera_four_reals", "four reals")
    said(Q, "valera_boys", "twenty-five")
    said(Q, "valera_fifty", "fifty")
    said(Q, "garcilaso_accountants", "four accountants", "twenty or thirty")
    said(Q, "acosta_arrobas", "two arrobas")
    said(Q, "acosta_hundredweight", "four arrobas", "a hundred weight")
    said(Q, "acosta_150", "a hundred and fiftie")
    said(Q, "acosta_pirate", "a hundred thousand")
    said(Q, "acosta_five", "five Cacaos")
    said(Q, "acosta_thirty", "thirtie")
    said(Q, "acosta_coca", "half a million")
    said(Q, "oviedo_rabbit", "diez almendras", "quatro almendras", "ocho pomas")
    said(Q, "oviedo_slave", "çiento")
    said(Q, "dell_mita", "1573", "1812")
    said(Q, "dell_25", "25%")
    said(Q, "dell_6", "6 percentage points")


def main():
    F, Q = facts(), quotes()
    intro(F)
    world(F)
    gold(F)
    cowries(F)
    dahomey(F)
    inca(F)
    cacao(F)
    selfcheck()
    from_quotes(Q)
    print("all numbers in Chapter 14 check out")


if __name__ == "__main__":
    main()
