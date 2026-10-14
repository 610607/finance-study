"""Chapter 12 (宋元明：世界最早的纸币及其崩溃): every number quoted in zh/ch12_songming.tex.

    python3 checks/check_ch12.py

Inputs are the two snapshots data/snapshots/yuanshi_suyinchao.csv (the Yuan shi table of notes
printed each year) and data/snapshots/paper_money_facts.csv (quantities and rates quoted from the
Song, Yuan and Ming histories); see their .json metadata.  The figure module figsrc/fig_ch12.py
imports the series built here.  The only formula used is the compound average rate of change
(eq:songming-avg in the chapter): ((X_T / X_0) ** (1 / T) - 1).
"""
from __future__ import annotations

from common import load_snapshot, quoted

ZT_PER_ZY = 5          # 1 guan 至元钞 = 5 guan 中统钞 (1287), fact yuan_1287_ratio
ZY_PER_ZD = 5          # 1 liang 至大银钞 = 5 guan 至元钞 (1309), fact yuan_1309_zhida
GUAN_PER_DING = 50     # fact yuan_ding
# Southern Song 省陌: one guan of account = 770 wen zu.  宋史卷181 gives it for the 1268 guanzi
# (fact guanzi_1268, “贯作七百七十文足”) and for the 18th-issue huizi (宝祐四年: “仿十八界会子……视淳祐
# 之令，作七百七十陌”).  The face value of a one-guan huizi in wen zu is therefore 770, not 1000.
SHENGMO_WEN_ZU = 770


def facts() -> dict[str, float]:
    df, _ = load_snapshot("paper_money_facts")
    out = {}
    for _, r in df.iterrows():
        if r["value"] == r["value"]:          # not NaN
            out[r["id"]] = float(r["value"])
    return out


def avg_rate(x0: float, xT: float, years: float) -> float:
    """Compound average rate of change per year (eq:songming-avg)."""
    return (xT / x0) ** (1.0 / years) - 1.0


def yuan_issuance():
    """Annual issuance in ding of 中统钞-equivalent at the official rates."""
    df, _ = load_snapshot("yuanshi_suyinchao")
    df = df.copy()
    df["zt_equiv_ding"] = df["zhongtong_ding"] + ZT_PER_ZY * df["zhiyuan_ding"] + ZT_PER_ZY * ZY_PER_ZD * df["zhida_ding"]
    return df


# ---------------------------------------------------------------------------
def song(F):
    quoted("iron cash: jin per guan of small coins", F["song_iron_small"] / 10, 6.5, tol=1e-12)
    quoted("iron cash: weight of 3 guan (jin)", 3 * F["song_iron_small"] / 10, 19.5, tol=1e-12)
    quoted("iron cash: weight of 5 guan (jin)", 5 * F["song_iron_small"] / 10, 32.5, tol=1e-12)
    quoted("宋朝事实 first-year issue / 宋史 quota (about three times)", F["song_first_year_issue"] / F["song_jiaozi_quota"], 3, tol=0.15)
    quoted("jiaozi reserve ratio (%)", 100 * F["song_jiaozi_reserve"] / F["song_jiaozi_quota"], 28.7, tol=0.05)
    quoted("jiaozi redemption fee (% of 1000 wen)", 100 * F["song_official_fee"] / 1000, 3.0, tol=1e-12)
    quoted("Daguan conversion: loss of an old note (%)", 100 * (1 - 1 / F["song_daguan_conversion"]), 75.0, tol=1e-12)
    quoted("Zhang Chi 1108: loss (%)", 100 * (1 - F["song_zhangchi"]), 90.0, tol=1e-9)
    quoted("Sichuan qianyin reserve ratio, end of Shaoxing (%)", 100 * F["sichuan_reserve"] / F["sichuan_outstanding"], 1.7, tol=0.05)
    quoted("Sichuan qianyin outstanding / Northern Song quota", F["sichuan_outstanding"] / F["song_jiaozi_quota"], 33.0, tol=0.5)


def huizi(F):
    quoted("huizi share of 1176 revenue (guan)", F["huizi_revenue_1176"] / 2, 6_000_000, tol=0)
    quoted("huizi quota 1195 / 1168", F["huizi_quota_1195"] / F["huizi_quota_1168"], 3.0, tol=1e-12)
    quoted("huizi outstanding 1209 / quota 1168", F["huizi_outstanding_1209"] / F["huizi_quota_1168"], 10.2, tol=1e-9)
    gold = F["huizi_gold_1209"] * 40
    quoted("1209 gold allotment in guan (40 guan per liang)", gold, 42_000_000, tol=0)
    quoted("1209 gold / outstanding 12th-13th issues (%)", 100 * gold / F["huizi_outstanding_1209"], 41, tol=0.5)
    for key, ratio, rate in [("huizi_outstanding_1232", 32.9, 5.6), ("huizi_outstanding_1232_variant", 22.9, 5.0)]:
        quoted(f"{key} / quota 1168", F[key] / F["huizi_quota_1168"], ratio, tol=1e-9)
        quoted(f"{key}: average growth 1168-1232 (%/yr)", 100 * avg_rate(F["huizi_quota_1168"], F[key], 1232 - 1168), rate, tol=0.05)
    quoted("1209 conversion: loss of an old huizi (%)", 100 * (1 - 1 / F["huizi_1209_conversion"]), 50, tol=1e-12)
    quoted("1232 readings: level difference (%)", 100 * (F["huizi_outstanding_1232"] / F["huizi_outstanding_1232_variant"] - 1), 44, tol=0.5)
    quoted("1232 readings: difference of average growth (percentage points)",
           100 * (avg_rate(F["huizi_quota_1168"], F["huizi_outstanding_1232"], 64) - avg_rate(F["huizi_quota_1168"], F["huizi_outstanding_1232_variant"], 64)),
           0.6, tol=0.05)
    assert SHENGMO_WEN_ZU == F["guanzi_1268"], "省陌 constant must equal the guanzi rate quoted in the text"
    quoted("self-check: copper price in huizi 1168-1268 if at par (770 wen zu) in 1168 (%/yr)",
           100 * avg_rate(F["huizi_value_1268"], SHENGMO_WEN_ZU, 100), 1.1, tol=0.05)
    quoted("18th huizi in 1268 vs guanzi (%)", 100 * F["huizi_value_1268"] / F["guanzi_1268"], 33.4, tol=0.05)
    quoted("18th huizi in 1268 vs its face value of 770 wen zu (about one third)",
           F["huizi_value_1268"] / SHENGMO_WEN_ZU, 1 / 3, tol=0.005)


def yuan(F, df):
    zt_silver_1287 = F["yuan_1287_silver"] * F["yuan_1287_ratio"]       # guan 中统 per liang of silver
    quoted("silver price in Zhongtong notes, 1287 (guan/liang)", zt_silver_1287, 10, tol=0)
    quoted("Guan et al.: huizi taken in per guan of Zhongtong notes (1276)", F["guan_huizi_rate"], 50, tol=0)
    quoted("Zhongtong value 1287 vs 1260 (%)", 100 * F["yuan_1260_parity"] / zt_silver_1287, 20, tol=1e-9)
    quoted("silver price in Zhongtong 1260-1287 (%/yr)", 100 * avg_rate(F["yuan_1260_parity"], zt_silver_1287, 1287 - 1260), 6.1, tol=0.05)
    zy_silver_1309 = F["yuan_1309_zhida"]                                 # guan 至元 per liang of silver
    quoted("Zhiyuan value 1309 vs 1287 (%)", 100 * F["yuan_1287_silver"] / zy_silver_1309, 40, tol=1e-9)
    quoted("silver price in Zhiyuan 1287-1309 (%/yr)", 100 * avg_rate(F["yuan_1287_silver"], zy_silver_1309, 1309 - 1287), 4.3, tol=0.05)
    quoted("silver price 1309 in Zhongtong notes (guan/liang)", zy_silver_1309 * ZT_PER_ZY, 25, tol=0)
    quoted("official gold/silver ratio 1287", F["yuan_1287_gold"] / F["yuan_1287_silver"], 10, tol=0)
    quoted("ten ding of notes in guan (1350s)", F["yuan_1351_grain"] * F["yuan_ding"], 500, tol=0)
    quoted("silver price in Zhongtong 1260 -> Zhiyuan 1309, in Zhongtong (x)", zy_silver_1309 * ZT_PER_ZY / F["yuan_1260_parity"], 12.5, tol=1e-9)
    quoted("salt per guan, Dade -> Taiding (x price)", F["yuan_salt_dade"] / F["yuan_salt_taiding"], 4.5, tol=1e-9)

    y = df.set_index("year")
    early = y.loc[1260:1275, "zt_equiv_ding"]
    late = y.loc[1276:1286, "zt_equiv_ding"]
    quoted("years 1260-1275 in the table", len(early), 16, tol=0)
    quoted("mean issue 1260-1275 (thousand ding)", early.mean() / 1e3, 106, tol=0.5)
    quoted("mean issue 1276-1286 (thousand ding)", late.mean() / 1e3, 1174, tol=0.5)
    quoted("years 1276-1286 in the table", len(late), 11, tol=0)
    quoted("ratio of the two means", late.mean() / early.mean(), 11.1, tol=0.05)
    quoted("issue 1276 (thousand ding)", y.loc[1276, "zt_equiv_ding"] / 1e3, 1420, tol=0.5)
    quoted("issue 1275 (thousand ding)", y.loc[1275, "zt_equiv_ding"] / 1e3, 398, tol=0.5)
    quoted("issue 1287 in Zhongtong equivalent (thousand ding)", y.loc[1287, "zt_equiv_ding"] / 1e3, 5088, tol=0.5)
    quoted("issue 1310 in Zhongtong equivalent (million ding)", y.loc[1310, "zt_equiv_ding"] / 1e6, 36.3, tol=0.05)
    quoted("issue 1310 / issue 1260", y.loc[1310, "zt_equiv_ding"] / y.loc[1260, "zt_equiv_ding"], 494, tol=0.5)
    quoted("1287-1290 mean issue (Zhongtong equiv, thousand ding)", y.loc[1287:1290, "zt_equiv_ding"].mean() / 1e3, 5275, tol=0.5)
    quoted("number of years in the table", len(y), 70, tol=0)
    return y


def ming(F):
    quoted("Ming copper value c.1393 vs par (%)", 100 * F["ming_1393_copper"] / F["ming_1375_par"], 16, tol=1e-9)
    quoted("copper price of a note 1375-1393 (%/yr)", 100 * avg_rate(F["ming_1393_copper"], F["ming_1375_par"], 1393 - 1375), 10.7, tol=0.05)
    quoted("rice price in notes 1426 / 1385", F["ming_1426_rice"] / F["ming_1385_rice"], 20, tol=1e-9)
    quoted("rice price in notes 1385-1426 (%/yr)", 100 * avg_rate(F["ming_1385_rice"], F["ming_1426_rice"], 1426 - 1385), 7.6, tol=0.05)
    quoted("commercial tax paid in notes from 1377 (%)", 10 * F["ming_tax_mix"], 70, tol=0)
    quoted("Yongle: share of the early-Hongwu value lost (%)", 100 * (1 - F["ming_yongle"]), 90, tol=1e-9)
    quoted("silver value 1525 vs 1375 (%)", 100 * F["ming_1525_silver"] / 1.0, 0.3, tol=1e-9)
    quoted("silver value lost by 1525 (%)", 100 * (1 - F["ming_1525_silver"]), 99.7, tol=1e-9)
    quoted("silver price of notes 1375-1525 (%/yr)", 100 * avg_rate(F["ming_1525_silver"], 1.0, 1525 - 1375), 3.9, tol=0.05)
    quoted("official gold/silver ratio 1375", 4.0 / 1.0, 4, tol=0)
    quoted("Chenghua: value below (%)", 100 * F["ming_chenghua"] / F["ming_1375_par"], 0.1, tol=1e-12)


def cagan(F):
    """Cagan (1956): hyperinflation begins at 50 per cent a month (row cagan_threshold)."""
    quoted("Cagan's threshold (%/month)", F["cagan_threshold"], 50, tol=0)
    quoted("50%/month as a yearly factor", (1 + F["cagan_threshold"] / 100) ** 12, 129.7, tol=0.05)


def ilkhanate(F):
    """The 1294 paper money of Tabriz: d'Ohsson (1835) and Howorth (1888)."""
    quoted("Tabriz 1294: notes obeyed for (days)", F["ohsson_1294_deserted"], 8, tol=0)
    quoted("Tabriz 1294: trade stopped (months), d'Ohsson", F["ohsson_1294_two_months"], 2, tol=0)
    quoted("Tabriz 1294: trade stopped (months), Howorth", F["howorth_1294_two_months"], 2, tol=0)
    quoted("Tabriz 1294: horse worth (gold pieces)", F["howorth_1294_horse_coin"], 7.5, tol=0)
    quoted("Tabriz 1294: horse asked (paper)", F["howorth_1294_horse_paper"], 750, tol=0)
    quoted("Tabriz 1294: paper taken at (% of face)", 100 * F["howorth_1294_horse_coin"] / F["howorth_1294_horse_paper"], 1, tol=1e-12)


def main():
    F = facts()
    song(F)
    huizi(F)
    yuan(F, yuan_issuance())
    ming(F)
    cagan(F)
    ilkhanate(F)
    print("Chapter 12: all quoted numbers reproduced.")


if __name__ == "__main__":
    main()
