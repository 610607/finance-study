"""Chapter 42 (东亚奇迹：日本高速增长与发展型国家): every number and every quotation in zh/ch42_eastasia.tex.

    python3 checks/check_ch42.py

Inputs:
  eastasia_facts                quotations of the chapter's sources with their page: the World Bank's news release
                                93/S17 (26 September 1993) and its report The East Asian Miracle (1993; the copyright
                                page, the footnote on China, a sentence of p. 308 and two rows of the timelines read on
                                the page images); Young (1994), NBER Working Paper 4680; Young (1992), NBER
                                Macroeconomics Annual 1992, with the comments of Krugman and Barro; Rodrik (1994), NBER
                                Working Paper 4964 (read on the page images: its text layer is unusable); Collins and
                                Bosworth (1996), Brookings Papers on Economic Activity 1996:2, with Rodrik's comment,
                                and the terms of use of brookings.edu; Krugman (1994), Foreign Affairs 73 (6), a
                                JSTOR-derived copy (read to verify, not committed); the abstract of Hsieh (2002) on
                                IDEAS; the Economic White Papers of 1956 and 1961 and the Cabinet Office's terms of use;
                                the Taiwanese statute on the period of martial law and article 9 of Taiwan's Copyright
                                Act; the World Bank's page on Lewis T. Preston; the Singapore Open Data Licence; the
                                authority records of the Library of Congress and the GND. data/fetch/verify_web_quotes.py
                                checks the quotations against the documents; the rows with an empty quotation are read
                                on page images, with a transcription between « and » in the note;
                                data/fetch/eastasia42.py fetches the documents
  pwt1001_eastasia              Penn World Table 10.01: Japan, Korea, Taiwan, Hong Kong, Singapore and the United
                                States, 1950-2019 (eq:eastasia-accounting, tab:eastasia-accounting,
                                fig:eastasia_levels, fig:eastasia_accounting)
  cpf_rates_1955_2026           the Central Provident Fund Board's contribution rates for employers and employees aged
                                35 and below (the case box, fig:eastasia_cpf)
  zh/ch21, ch35, ch39, ch40, ch41    the statements and numbers of earlier chapters that this chapter repeats, checked
                                against those chapters' words (there(), EVENTS); the stubs of Chapters 43, 46, 47,
                                56, 58, 61, 72, 78 and 79 for what is handed on (LATER)

This script

1. reads the numbers of every row from its quotation (or from the transcription of a page image) by the rules of
   READINGS and compares them with the value column; the misreadings of the text layers are listed in MISPRINTS;
2. finds every “…” of the text among the renderings of TRANSLATIONS, and the words of the source each one renders
   (KEYWORDS) in the row; the quotations stay short (all the sources are in copyright or allow short phrases only);
3. checks each number of the text with said(): the phrase is in the text and each number is the value of a row, a
   teaching input, or arithmetic on them (the growth accounting eq:eastasia-accounting on Young's rows and on PWT
   10.01, the dual eq:eastasia-dual, Krugman's arithmetic of diminishing returns, the transfer of financial repression,
   the levels of fig:eastasia_levels, the CPF rates); every Arabic number of the text must lie in a phrase said() read
   (coverage());
4. checks the key equations as printed, the claims made of them on random numbers, the data of the figures
   (figsrc/fig_ch42.py imports levels(), accounting() and cpf() from here), the life dates against the authority
   records, what other chapters tell, the licences and the bibliography block of Chapter 42, and the editor's limits;
5. lists the rows no "% 据:" anchor of the text names (common.anchors).

Set CH42_TEX to a scratch copy of the chapter to run the checks on it (mutation tests).
"""
from __future__ import annotations

import math
import os
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from common import ROOT, anchors, load_snapshot, quoted

TEX = Path(os.environ.get("CH42_TEX", ROOT / "zh" / "ch42_eastasia.tex"))   # a scratch copy for mutation tests
GUIDE = "日本和东亚“四小龙”的高速增长，是生产率的奇迹，还是要素积累的结果？"
PREV = GUIDE                                        # Chapter 41's NEXT
NEXT = "计划经济里的“通胀”藏在哪里？"                   # Chapter 43's question (its stub)
MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"], 1)}
FETCH = "data/fetch/eastasia42.py"
IMAGE_NOTE = "read on the page image"


def chk(what: str, value, expected=None, tol: float = 1e-6, rel: float = 0.0) -> float:
    """quoted() with a tolerance for floating-point error; a list is compared element by element."""
    if isinstance(value, (list, tuple)):
        assert expected is not None and len(value) == len(expected), (what, value, expected)
        for i, (v, e) in enumerate(zip(value, expected)):
            quoted(f"{what} [{i + 1}]", float(v), e, tol=tol, rel=rel)
        return float(value[0])
    return quoted(what, float(value), expected, tol=tol, rel=rel)


# ---------------------------------------------------------------------------------------------------
# Loaders
@lru_cache(maxsize=None)
def _rows() -> pd.DataFrame:
    df, m = load_snapshot("eastasia_facts", dtype=str, keep_default_na=False)
    assert 42 in m["used_in"] and m["fetch"] == FETCH
    assert df["id"].is_unique
    return df


@lru_cache(maxsize=None)
def meta() -> dict:
    return load_snapshot("eastasia_facts")[1]


def facts() -> dict[str, list[float]]:
    """id -> the numbers of the value column (several are separated by ';')."""
    return {r.id: [float(x) for x in r.value.split(";")] for r in _rows().itertuples() if r.value}


def years() -> dict[str, int]:
    return {r.id: int(r.year) for r in _rows().itertuples() if r.year.isdigit()}


@lru_cache(maxsize=None)
def quotes() -> dict[str, str]:
    """id -> the quotation, with the line breaks of the source joined (empty for a row read on a page image)."""
    return {r.id: " ".join(r.quote.split()) for r in _rows().itertuples()}


@lru_cache(maxsize=None)
def column(name: str) -> dict[str, str]:
    return {r.id: getattr(r, name) for r in _rows().itertuples()}


def transcription(rid: str) -> str:
    """The words of a row read on a page image, as its note transcribes them between « and »."""
    m = re.search(r"«(.*)»", column("note")[rid])
    assert m, f"{rid}: no transcription in the note"
    return m.group(1)


def words_of(rid: str) -> str:
    """What a row says: its quotation, or the transcription of a page image."""
    return quotes()[rid] or transcription(rid)


def has(rid: str, *words: str) -> None:
    """Each of the words is in what row rid says."""
    for w in words:
        assert w in words_of(rid), (rid, w)


def mon(rid: str, name: str) -> int:
    """The month `name` (English, or its abbreviation), asserted to be in what row rid says."""
    has(rid, name)
    key = name.lower().rstrip(".")
    return MONTHS[key] if key in MONTHS else [i for m, i in MONTHS.items() if m.startswith(key)][0]


def page(rid: str) -> int:
    """The first printed page number of a row's juan column: 'p. 155 (PDF p. 159)' -> 155."""
    return int(re.search(r"pp?\. (\d+)", column("juan")[rid]).group(1))


def pdfpage(rid: str) -> int:
    return int(re.search(r"PDF p\. (\d+)", column("juan")[rid]).group(1))


def chapter(name: str) -> str:
    """Another chapter's text without its comment lines."""
    t = (ROOT / "zh" / f"{name}.tex").read_text(encoding="utf-8")
    return "\n".join(l for l in t.splitlines() if not l.lstrip().startswith("%"))


# ---------------------------------------------------------------------------------------------------
# 1. Readings of the numbers (the same rules wrote the value column when the snapshot was built)
SMALL = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
         "ten": 10, "eleven": 11, "twelve": 12, "fifteen": 15}
TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50}
WORDS = {"twice": 2, "twothirds": 2 / 3, "two-thirds": 2 / 3, "third": 1 / 3, "one-fourth": 1 / 4}


def cardinal(s: str) -> float:
    """An English cardinal: 'three', 'fifteen', 'twenty-four'."""
    return float(sum(SMALL.get(w, 0) + TENS.get(w, 0) for w in s.lower().replace("-", " ").split()))


def figure(s: str) -> float:
    """'1,000', '30.5', '.28', '-0.003', '－1.6' and full-width digits."""
    return float(unicodedata.normalize("NFKC", s).replace(",", "").replace("−", "-"))


def neg(s: str) -> float:
    """A minus sign printed apart from its number: '- 8' -> -8."""
    return -float(s.replace("-", "").strip())


ZH_DIGITS = {"〇": 0, "零": 0, "一": 1, "两": 2, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
ZH_UNITS = {"十": 10, "百": 100, "千": 1000, "万": 10 ** 4, "亿": 10 ** 8}


def zh(s: str) -> float:
    """A Chinese numeral: '六', '十四', '七十六', '三分之二', '一半', '二十五', '七成', '四倍多'."""
    if "分之" in s:
        b, a = s.split("分之")
        return zh(a) / zh(b)
    if s.endswith("成"):
        return zh(s[:-1]) / 10
    if s.endswith("半"):
        return 0.5 * (zh(s[:-1]) if s[:-1] else 1)
    s = s.rstrip("多倍")
    big, total, part = 0, 0, 0
    for ch in s:
        if ch in ZH_DIGITS:
            part = ZH_DIGITS[ch]
        elif ch in "万亿":
            big += max(total + part, 1) * ZH_UNITS[ch]
            total, part = 0, 0
        else:
            total += max(part, 1) * ZH_UNITS[ch]
            part = 0
    return float(big + total + part)


# a figure with its sign: a minus that follows no letter, digit or bracket
FIGURES = re.compile(r"((?<![\w)])[-−])?(\d[\d,]*(?:\.\d+)?|\.\d+)")
HOW = {"num": figure, "en": cardinal, "word": lambda w: WORDS[w], "neg": neg, "zh": zh}
# id -> [(phrase, how)], in order. A phrase 'context|word' is searched as a whole and read from `word`. Rows not
# listed are read with all the figures of the quotation (a page image: of the transcription), with their signs. An
# empty list: the row prints no number of the story (titles, licences, report numbers, a sentence without numbers).
EMPTY = ("wn_number wn_headline wn_eight2 wn_page wn_interventions wn_exportpush wn_vested wb_rights "
         "wb_series wb_accumulation wb_miraculous wb_japan_support wb_board wb_team wb_financial wb_tigers "
         "wb_china wb_exceeds wb_selective wb_failure wb_mof wb_ledmarket wb_mildrep wb_transfer wb_misallocated "
         "wb_notinhibit wb_provident wb_ch1_groups wb_ch1_dominant wb_repressed wb_hci wb_targets wb_housing wb_unions "
         "wb_authoritarian wb_seized_land wb_sg_unions wb_sg_peace wb_johnson wb_epb wb_banking wb_uneven "
         "wb_filp_sources  wb_hci_costs wb_promotion wb_promoted wb_controlled wb_savers y4_number "
         "y4_singapore y4_boring y4_log y4_armies y4_unprecedented y4_anglo y4_t81_note y4_nothigh "
         "y2_selection y2_victim y2_withdraw y2_1968 y2_prerog y2_arbitration y2_numbered "
         "y2_kr_barking y2_kr_startling y2_kr_fickle y2_kr_faster y2_kr_face y2_kr_dontknow y2_barro_dr rd_causal "
         "rd_small rd_boom rd_engineer rd_outward rd_orthodox cb_views cb_sacrifice cb_similar cb_krugman cb_room "
         "cb_rd_miracle cb_rd_indirect cb_rd_tools cb_rd_hk cb_bosworth br_copyright br_personal kg_jstor "
         "kg_fable kg_mystery kg_perspiration kg_stalin kg_fn6 kg_japan kg_noefficiency kg_deferred "
         "kg_pace kh_stalin hs_dual hs_reason hs_notexplained hs_restricted wp56_sengo wp56_modern wp56_burden "
         "wp61_window tw_title tw_ca9 loc_preston loc_lee_note sl_use sl_attribution sl_official gnd_licence wb_johnson_q wb_neoclassical "
         "wb_marketfail wb_lowgrowth wb_repdef wb_neo_detail wb_invdriven wb_proddriven y2_housing y2_list kg_allgrowth "
         "kg_double cb_rd_conjecture cb_rd_hkonly cb_rd_guess kg_outpace wb_spread wb_hci_motive wb_tw_public "
         "wn_pushdef wb_jdb_why wp56_race wp56_pain wp61_control wp61_nopolitics y2_educated cb_lesson y2_foreign wb_npa wn_gap "
         "wb_responsive wb_park_educ wb_npa2 wb_drafts wb_tw_landlords wb_consumer wb_restrict wb_payoffs wb_soviet "
         "wb_failures wb_command wb_shared wb_leaders wb_contests wb_councils wb_contest_key wb_evident kg_baseline "
         "wb_statebanks wb_bank_export wb_hci_partly wb_hci_starved wb_hci_switch wb_diet "
         "wb_guidance wb_guidance_law wb_miti_skill y2_entrepot y2_conduit y2_maximalist "
         "wb_miti_fx kg_predicted kg_naive wn_boosted y2_ahead y2_masked y2_kr_couldbe y2_kr_noevidence "
         "y4_hours y4_hkhours wb_neutral").split()
READINGS: dict[str, list[tuple[str, str]]] = {rid: [] for rid in EMPTY}
READINGS.update({
    "wn_date": [("SEPTEMBER |26", "num"), (", |1993", "num")],
    "wn_poverty": [("past |three", "en")],
    "wn_eight": [("in |eight", "en")],
    "wn_twice": [("Since |1960", "num"), ("grown |twice", "word"), ("Asia, |three", "en"), ("and |five", "en")],
    "wb_copyright": [("© |1993", "num")],
    "wb_printing": [("September |1993", "num")],
    "wb_signed": [("Augur |1993", "num")],
    "wb_august": [("August |1993", "num")],
    "wb_fourtimes": [("Between |1960", "num"), ("and |1985", "num"), ("than |four", "en")],
    "wb_twothirds": [("roughly |twothirds", "word")],
    "kg_edu": [("in |1966", "num"), ("by |1990", "num"), (" |two-thirds", "word")],
    "y4_kr_invest": [("around |5", "num"), ("early |1950", "num"), ("upto |20", "num"), ("reached |30", "num"), ("early |1980", "num"),
                     ("approaching |40", "num"), ("by |1991", "num")],
    "wb_jdb": [("mere |0.09", "num"), ("in |1951", "num"), ("just |0.01", "num"), ("in |1956", "num")],
    "wb_korea_exp": [("In the |1950", "num"), ("grow |four", "en"), ("next |thirty", "en")],
    "wb_integrated": [("early |1970", "num")],
    "wp61_lowwage": [],
    "wp61_fullemp": [],
    "y2_kr_35": [("the |35", "num")],
    "y4_agri": [("by |.6", "num"), ("and |.7", "num")],
    "y2_pioneer": [("in |1959", "num"), ("the |40", "num"), ("of |5", "num"), (", |10", "num")],
    "wb_japan_credit": [("early |1970", "num")],
    "y4_overestimates": [("during the |1950", "num")],
    "wb_tw_rates": [("negative|300", "num"), ("in |1949", "num"), ("about |8.5", "num"), ("in |1953", "num"), ("from |2", "num"),
                    ("to |34", "num"), ("in |three", "en")],
    "wb_hci_shift": [("Drive1|1973", "num"), ("-|79", "num")],
    "wb_hci_six": [("out |six", "en")],
    "y2_textiles": [("early |1950", "num")],
    "y2_stagnation": [("The |1950", "num"), ("early |1960", "num")],
    "wb_guidance_tool": [("mid-|1960", "num")],
    "wb_liberalize": [("mid|1960", "num"), ("till |1979", "num")],
    "y2_lowest": [("mid-|1980", "num")],
    "wb_takeoff": [("Takeoff |1961", "num"), ("-|73", "num")],
    "wb_6090": [("between|60", "num"), ("and |90", "num")],
    "wb_pricewrong": [("Amsden|1989", "num")],
    "wb_weak": [("first |fifteen", "en")],
    "wb_filp_third": [("about a |third", "word"), ("the |1950", "num")],
    "wb_miti": [("late as |1978", "num"), ("was |22", "num")],
    "wb_tl_sg": [("|1959", "num"), ("|1965", "num"), ("|1968", "num"), ("all |58", "num")],
    "y4_t11_hksg": [("1.6 |5.7", "num"), ("1.9 |6.6", "num")],
    "y4_t11_krtw": [("1.8 |6.9", "num"), ("1.8 |6.8", "num")],
    "y4_t31": [("66-91 |0.073", "num"), (" |0.080", "num"), (" |0.032", "num"), (" |0.023", "num"), (" |0.628", "num")],
    "y4_t41": [("66-90 |0.085", "num"), (" |0.115", "num"), (" |0.057", "num"), (" |-0.003", "num"), (" |0.470", "num")],
    "y4_t51": [("66-90 |0.104", "num"), (" |0.137", "num"), (" |0.064", "num"), (" |0.016", "num"), (" |0.680", "num")],
    "y4_t61": [("66-90 |0.096", "num"), (" |0.123", "num"), (" |0.051", "num"), (" |0.024", "num"), (" |0.710", "num")],
    "y4_sg_text": [("extraordinaiy |-0.3", "num"), ("a |twenty-four", "en")],
    "y4_t81": [("Economy: |2.3", "num"), (" |-0.3", "num"), (" |1.6", "num"), (" |1.9", "num")],
    "y2_laissez": [("early |1960", "num")],
    "y2_t5_hk": [("71-90 |1.472", "num"), (" |0.549", "num"), (" |1.599", "num"), (" |0.384", "num"), (" |0.23", "num"), (" |0.42", "num"), (" |0.35", "num")],
    "y2_t5_sg": [("70-90 |1.545", "num"), (" |0.825", "num"), (" |2.402", "num"), (" |0.533", "num"), (" |0.25", "num"), (" |0.83", "num"), (" |-0.08", "num")],
    "y2_m8": [("to |- 8", "neg")],
    "y2_t8_6970": [("1969-70 |0.401", "num")],
    "y2_t8_8889": [("1988-89 |0.128", "num")],
    "y2_return": [("late |1980", "num"), ("over |10", "num")],
    "rd_copyright": [("© |1994", "num")],
    "rd_number": [("No. |4964", "num"), ("December |1994", "num")],
    "rd_panel": [("the |20", "num"), ("on |21", "num"), ("-|22", "num"), ("October |1994", "num")],
    "rd_poorer": [("In |1960", "num")],
    "cb_journal": [("Activity, |2", "num"), (":|1996", "num")],
    "cb_fourth": [("only |one-fourth", "word")],
    "cb_rd_elastic": [("substitutionof |0.5", "num"), ("to |1.93", "num"), ("in |ten", "en"), ("years, |2.53", "num"),
                      ("in |twenty", "en"), ("and |2.89", "num"), ("percentin |thirty", "en")],
    "kg_source": [("Dec., |1994", "num"), ("Vol. |73", "num"), ("No. |6", "num"), ("pp. |62", "num"), ("-|78", "num")],
    "kg_singapore": [("Between |1966", "num"), ("and |1990", "num"), ("remarkable |8.5", "num"), ("annum, |three", "en"),
                     ("at a |6.6", "num")],
    "tw_martial": [("民國|三十八", "zh"), ("年|五", "zh"), ("月|二十", "zh"), ("至|七十六", "zh"), ("年|七", "zh"),
                   ("月|十四", "zh")],
    "y2_fn79": [("averageof |.000", "num"), ("between |1974", "num"), ("and |1989", "num")],
    "loc_park_note": [("assassinated, |10", "num"), ("/|26", "num"), ("/|79", "num")],
})


def read(word: str, how: str) -> list[float]:
    return [HOW[how](word)]


def read_rule(rid: str, text: str) -> list[float]:
    got, pos = [], 0
    for phrase, how in READINGS[rid]:
        context, _, word = phrase.rpartition("|")
        k = text.find(context + word, pos)
        assert k >= 0, f"{rid}: {phrase!r} not found (in order)"
        pos = k + len(context + word)
        got += read(word, how)
    return got


def read_text(rid: str, text: str) -> list[float]:
    """The numbers of a quotation or of the transcription of a page image, by READINGS or by its figures."""
    if rid in READINGS:
        return read_rule(rid, text)
    text = unicodedata.normalize("NFKC", text)
    return [(-1 if sign else 1) * figure(n.rstrip(",")) for sign, n in FIGURES.findall(text)]


# the misreadings of the text layers and the misprints, each printed in the quotation and named in the snapshot's
# notes with its row: (row, as printed in the quotation, the words of the notes that name it)
MISPRINTS = [("wn_eight", "economieq", "'economieq' for 'economies'"),
             ("wb_bangkok", "Govemors", "'Govemors' for 'Governors'"),
             ("wb_accumulation", "cosuperior", "'cosuperior' and 'capita.' for 'to superior' and 'capital.'"),
             ("wb_japan_support", "gratfilly", "'gratfilly' for 'gratefully'"),
             ("wb_board", "rcprescnt", "'rcprescnt' for 'represent'"),
             ("wb_signed", "Augur", "'Augur' for 'August'"),
             ("wb_team", "Pagc", "'Pagc' for 'Page'"),
             ("wb_financial", "Govemrnment", "'Govemrnment' for 'Government'"),
             ("wb_tigers", "thc", "'thc' for 'the'"),
             ("wb_twothirds", "dte", "'dte' for 'the'"),
             ("wb_exceeds", "FHAEs", "'FHAEs' for 'HPAEs'"),
             ("wb_selective", "govenment", "'govenment' for 'government'"),
             ("wb_mof", "Minisrryof IntcrnationalTrade and Indusry",
              "'Minisrryof IntcrnationalTrade and Indusry' for 'Ministry of International Trade and Industry'"),
             ("wb_pricewrong", "struccure", "'struccure' for 'structure'"),
             ("wb_ledmarket", "m.narke\"e", "'\"led the m.narke\"e' for '\"led the market\"'"),
             ("wb_transfer", "firns", "'firns' for 'firms'"),
             ("wb_notinhibit", "appaently", "'appaently' for 'apparently'"),
             ("wb_provident", "compeled", "'compeled' and 'dtrough' for 'compelled' and 'through'"),
             ("wb_ch1_singapore", " ac rates", "'ac' for 'at'"),
             ("wb_ch1_dominant", "nor the", "'nor' for 'not'"),
             ("wb_repressed", "interesr", "'interesr' for 'interest'"),
             ("wb_hci", "(Hcr)", "'(Hcr)' for '(HCI)'"),
             ("wb_authoritarian", "&cing", "'&cing' for 'facing'"),
             ("wb_seized_land", "rhe government", "'rhe' for 'the'"),
             ("wb_korea_land", "renants", "'renants' for 'tenants'"),
             ("wb_sg_unions", "lirmitedunion", "'lirmitedunion' for 'limited union'"),
             ("wb_park", "govemment", "'govemment' for 'government'"),
             ("wb_epb", "authoriry", "'authoriry' for 'authority'"),
             ("wb_japan_negative", "raceson", "'raceson' for 'rates on'"),
             ("wb_hci_costs", "Ha:", "'Ha:' and 'filly' for 'HCI' and 'fully'"),
             ("wb_promoted", "significantdy", "'significantdy' for 'significantly'"),
             ("wb_controlled", "interesr races", "'interesr races' for 'interest rates'"),
             ("wb_savers", "mosdy", "'mosdy' for 'mostly'"),
             ("y4_sg_invest", "GD?", "'GD?' for 'GDP'"),
             ("y4_sg_text", "extraordinaiy", "'extraordinaiy' for 'extraordinary'"),
             ("y2_mandays", "mid1960s", "'mid1960s' for 'mid-1960s'"),
             ("cb_rd_hk", "srategy", "'srategy' for 'strategy'"),
             ("wb_marketfail", "markersconsistendy", "'markersconsistendy' for 'markets consistently'"),
             ("wb_proddriven", "Tliailand", "'Tliailand' for 'Thailand'"),
             ("wp61_window", "引線め", "'引線め' for '引締め'"),
             ("wb_jdb_why", "effltive", "'effltive' for 'effective'"),
             ("wb_korea_exp", "four times as fist", "'fist' for 'fast'"),
             ("wb_integrated", "markeL", "'markeL' for 'market', 'abiity' for 'ability'"),
             ("wb_npa", "vice-nunisters", "'caes', 'vice-nunisters', 'resrt' for 'cases', 'vice-ministers', 'rest'"),
             ("wb_responsive", "are nor very", "'nor' for 'not'"),
             ("wb_npa2", "protecred fiom", "'protecred fiom', 'Natonal', 'bureaucray's' and 'promotdon' for 'protected from', 'National', 'bureaucracy's' and 'promotion'"),
             ("wb_korea_land1", "Wurid", "'Wurid' for 'World'"),
             ("wb_korea_land2", "legislatum", "'legislatum' for 'legislature'"),
             ("wb_tw_landlords", "authoriies", "'authoriies' for 'authorities''"),
             ("wb_consumer", "contrls", "'contrls' for 'controls'"),
             ("wb_restrict", "Restrictons", "'Restrictons' and 'induding' for 'Restrictions' and 'including'"),
             ("wb_payoffs", "generaed", "'generaed' and 'consistendy' for 'generated' and 'consistently'"),
             ("wb_soviet", "dearly offset", "'conwnt', 'fonrer' and 'dearly' for 'contrast', 'former' and 'clearly'"),
             ("wb_command", "Examplesindude", "'indude' and 'Widespread' for 'include' and 'widespread'"),
             ("wb_shared", "sociey", "'sociey' for 'society'"),
             ("wb_leaders", "paternalisdtithey", "'paternalisdtithey' for 'paternalistic, they'"),
             ("wb_contests", "berween", "'HPABs' and 'berween' for 'HPAEs' and 'between'"),
             ("wb_contest_key", "caedit", "'caedit' for 'credit'"),
             ("wb_evident", "especialy", "'especialy' for 'especially'"),
             ("kg_china78", "ques tion", "'ques tion' for 'question' (a hyphen lost at a line end)"),
             ("wb_statebanks", "rhe stare-controlled", "'rhe stare-controlled' for 'the state-controlled'"),
             ("wb_hci_shift", "Indostries Drive11973-791", "'Indostries Drive11973-791', 'takeoffperiod' and 'govremment' for 'Industries Drive (1973-79)', 'takeoff period' and 'government'"),
             ("wb_hci_six", "industriessteel", "'industriessteel', 'machinery-to' and 'induding' for 'industries—steel', 'machinery—to' and 'including'"),
             ("wb_hci_partly", "dear fiom", "'dear fiom' for 'clear from'"),
             ("wb_hci_starved", "botdenecks", "'botdenecks' and 'largscale' for 'bottlenecks' and 'large-scale'"),
             ("wb_hci_switch", "apprecated", "'apprecated', 'utiliation', ':HC: seccor' and 'switchled' for 'appreciated', 'utilization', 'HCI sector' and 'switched'"),
             ("wb_guidance", "bureauicracyin", "'bureauicracyin' and 'privatcpartiesto' for 'bureaucracy in' and 'private parties to'"),
             ("wb_miti_skill", "MITEis wellkcnownfor", "'MITEis wellkcnownfor' for 'MITI is well known for'"),
             ("wb_diet", "rulingliberal", "'rulingliberal' for 'ruling Liberal'"),
             ("wb_guidance_tool", "powerfil4tool for Mm", "'powerfil4tool for Mm' for 'powerful tool for MITI'"),
             ("wb_miti_fx", "Mm had", "'Mm' for 'MITI'"),
             ("wb_liberalize", "intermationalpressure", "'intermationalpressure', 'maintin', 'rade' and 'mid1960sand' for 'international pressure', 'maintain', 'trade' and 'mid-1960s and'"),
             ("kg_predicted", "slow ing", "'slow ing' for 'slowing' (a hyphen lost at a line end)"),
             ("y4_overestimates", "corrobate", "'corrobate' for 'corroborate'"),
             ("wb_neutral", "fiavorof", "'fiavorof' and 'dte' for 'favor of' and 'the'"),
             ("wb_6090", "rtheiroutput growthctcrivres", "'rtheiroutput growthctcrivres' for 'their output growth derives'")]


def check_readings(df: pd.DataFrame) -> None:
    src = meta()["sources"]
    n = img = 0
    for r in df.itertuples():
        assert r.file in src, (r.id, r.file)
        vals = [float(x) for x in r.value.split(";")] if r.value else []
        if src[r.file]["format"] == "image":                 # read on a page image: no quotation
            assert not r.quote and IMAGE_NOTE in r.note, r.id
            img += 1
            got = read_text(r.id, transcription(r.id))
        else:
            assert r.quote and IMAGE_NOTE not in r.note, f"{r.id}: no quotation"
            got = read_text(r.id, " ".join(r.quote.split()))
            n += bool(vals)
        assert [round(g, 6) for g in got] == [round(v, 6) for v in vals], f"{r.id}: read {got}, value column {vals}"
    quoted("rows with values, each read from its quotation", n, N_QUOTED)
    quoted("rows read on a page image (no quotation)", img, N_IMAGE)
    Q, notes = quotes(), meta()["notes"]
    for rid, word, named in MISPRINTS:
        assert word in Q[rid], (rid, word)                                      # printed in the quotation
        found = False
        for m in re.finditer(re.escape(named), notes):
            g = re.match(r"[^(]{0,80}\(([^)]*)\)", notes[m.end():])
            found |= bool(g) and rid in re.split(r",\s*", g.group(1))
        assert found, (rid, named)                                                # and named, with its row
    assert set(src) == set(df["file"]), sorted(set(src) ^ set(df["file"]))
    # the page images of the World Bank's report belong to its scan: the same address and file
    assert src["wb1993_42img"]["url"] == src["wb1993_42"]["url"]
    assert src["wb1993_42img"]["sha256"] == src["wb1993_42"]["sha256"]
    assert src["rodrik1994_42img"]["format"] == "image" and src["rodrik1994_42img"]["url"].endswith("w4964.pdf")


N_QUOTED, N_IMAGE = 134, 23


# ---------------------------------------------------------------------------------------------------
# The data: Penn World Table 10.01 and the CPF rates
CODES = ("JPN", "KOR", "TWN", "HKG", "SGP", "USA")
NAMES_ZH = {"JPN": "日本", "KOR": "韩国", "TWN": "台湾", "HKG": "香港", "SGP": "新加坡", "USA": "美国"}
# the periods of Young (1994): Tables 8-1 and 8-2 (Japan from Christensen, Cummings and Jorgenson), and a benchmark
PERIODS = (("HKG", 1966, 1991), ("SGP", 1966, 1990), ("KOR", 1966, 1990), ("TWN", 1966, 1990), ("JPN", 1952, 1973),
           ("USA", 1966, 1990))
CB_SHARE_ROW = "cb_share"                                  # Collins and Bosworth's uniform capital share


@lru_cache(maxsize=None)
def pwt() -> dict[str, pd.DataFrame]:
    df, m = load_snapshot("pwt1001_eastasia")
    assert 42 in m["used_in"] and m["fetch"] == FETCH
    assert set(df["countrycode"]) == set(CODES) and df["year"].min() == 1950 and df["year"].max() == 2019
    return {c: g.set_index("year") for c, g in df.groupby("countrycode")}


def accounting(code: str, a: int, b: int, alpha: float | None = None, hours: bool = False) -> dict[str, float]:
    """eq:eastasia-accounting on PWT 10.01 (per cent a year, logarithmic growth between the end years): output rgdpna,
    capital rnna, labour emp (with hours: emp x avh, the hours worked), human capital hc; alpha = 1 - the mean labsh of
    the years a..b unless given. Also the per-worker form: y = Y/L, k = K/L."""
    x = pwt()[code]
    g = lambda v: 100 * (math.log(x.loc[b, v]) - math.log(x.loc[a, v])) / (b - a)     # noqa: E731
    al = 1 - x.loc[a:b, "labsh"].mean() if alpha is None else alpha
    gY, gK, gL, gh = g("rgdpna"), g("rnna"), g("emp") + (g("avh") if hours else 0.0), g("hc")
    gA = gY - al * gK - (1 - al) * (gL + gh)
    return dict(gY=gY, alpha=al, cap=al * gK, lab=(1 - al) * (gL + gh), gA=gA, gK=gK, gL=gL, gh=gh,
                gy=gY - gL, capw=al * (gK - gL), edu=(1 - al) * gh)


@lru_cache(maxsize=None)
def levels() -> pd.DataFrame:
    """rgdpe/pop relative to the United States (= 100), year x economy."""
    P = pwt()
    us = P["USA"]["rgdpe"] / P["USA"]["pop"]
    return pd.DataFrame({c: 100 * (P[c]["rgdpe"] / P[c]["pop"]) / us for c in CODES if c != "USA"})


@lru_cache(maxsize=None)
def cpf() -> pd.DataFrame:
    """The CPF contribution rates of the age group 35 and below: effective month x party (per cent of wage)."""
    df, m = load_snapshot("cpf_rates_1955_2026", dtype=str, keep_default_na=False)
    assert 42 in m["used_in"] and m["fetch"] == FETCH and set(df["age_grp"]) == {"35 years & below"}
    out = df.pivot(index="effective_from", columns="contributing_party", values="contribution_rate").astype(float)
    return out.sort_index()


def cpf_at(month: str, party: str) -> float:
    """The rate in force in a month 'YYYY-MM'."""
    D = cpf()
    return float(D[D.index <= month][party].iloc[-1])


def young_tfp() -> dict[str, float]:
    """Young's Table 8-1 (economy) and Table 8-2 (Japan, United States), per cent a year."""
    F = facts()
    hk, sg, kr, tw = F["y4_t81"]
    return {"HKG": hk, "SGP": sg, "KOR": kr, "TWN": tw, "JPN": F["y4_t82_japan"][2], "USA": None}


def cb_tfp() -> dict[str, float]:
    """Collins and Bosworth's Table 6, 1960-94: the TFP column."""
    F = facts()
    return {"KOR": F["cb_t6_kr"][5], "SGP": F["cb_t6_sg"][5], "TWN": F["cb_t6_tw"][5]}


# ---------------------------------------------------------------------------------------------------
# 2. The quotations of the text: each “…” is a rendering of words of a row
TRANSLATIONS = {
    "奇迹": "wn_headline",
    "更多积累": "wb_accumulation",
    "神奇": "wb_miraculous",
    "汗水": "kg_perspiration",
    "已经不再是‘战后’了": "wp56_sengo",
    "四虎": "wb_fourtimes",
    "共享增长": "wb_shared",
    "大部分的分析和全部的结论": "y4_singapore",
    "我们不知道": "y2_kr_dontknow",
    "新增长理论": "y2_kr_barking",
    "一则警世寓言": "kg_fable",
    "斯大林也会引以为傲": "kg_stalin",
    "延迟满足": "kg_deferred",
    "竞赛": "wb_contests",
    "把价格做错": "wb_pricewrong",
    "引领市场": "wb_ledmarket",
    "出口推动": "wn_pushdef",
    "很不相同": "wb_china",
    # the misreadings of the text layers quoted in the 史料说明
    "Augur 1993": "wb_signed",
    "cosuperior": "wb_accumulation",
    "Mm": "wb_miti_fx",
    "MITE": "wb_miti_skill",
    "dearly offset": "wb_soviet",
    "11973-791": "wb_hci_shift",
}
# the words of the source each rendering renders, in the quotation (or the transcription of the page image)
KEYWORDS = {
    "wn_headline": ['"MIRACLE"'],
    "wb_accumulation": ["superior accumulation", "cosuperior"],
    "wb_miraculous": ["nothing'miraculous\""],
    "kg_perspiration": ["perspiration"],
    "wp56_sengo": ["もはや「戦後」ではない"],
    "wb_fourtimes": ["the Four Tigers"],
    "wb_shared": ["the principle of shared growth"],
    "y4_singapore": ["most of my analysis and all of my conclusions"],
    "y2_kr_dontknow": ["We don't know"],
    "y2_kr_barking": ["\"new growth theory\""],
    "kg_fable": ["A CAUTIONARY FABLE"],
    "kg_stalin": ["would have done Stalin proud"],
    "kg_deferred": ["deferred gratification"],
    "wb_contests": ["contests"],
    "wb_pricewrong": ["\"getting the prices wrong\""],
    "wb_ledmarket": ["\"led the m.narke\"e"],
    "wn_pushdef": ["\"export push\""],
    "wb_china": ["so different"],
    "wb_signed": ["Augur 1993"],
    "wb_miti_fx": ["Mm had"],
    "wb_miti_skill": ["MITEis"],
    "wb_soviet": ["dearly offset"],
    "wb_hci_shift": ["11973-791"],
}
MISREAD = ("Augur 1993", "cosuperior", "Mm", "MITE", "dearly offset", "11973-791")


def tex_text() -> str:
    return "\n".join(l for l in TEX.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("%"))


def text_quotations() -> list[str]:
    """The “…” of the text; the closing question is Chapter 43's and the chapter's own question is in the guide and at
    the end of the opening (both checked by guide() and opening())."""
    t = tex_text().rstrip()
    assert t.endswith(NEXT), "the last words are not Chapter 43's question"
    t = t[:-len(NEXT)]
    assert t.count(GUIDE) == 2, "the question is not in the guide and at the end of the opening"
    return re.findall(r"“([^”]*)”", t.replace(GUIDE, ""))


def check_text(df: pd.DataFrame) -> None:
    ids = set(df["id"])
    used, n = set(), 0
    for q in text_quotations():
        n += 1
        used.add(q)
        assert q in TRANSLATIONS, f"not listed: “{q}”"
        rid = TRANSLATIONS[q]
        assert rid in ids and rid in KEYWORDS, rid
    stale = set(TRANSLATIONS) - used
    assert not stale, f"listed but not in the text: {sorted(stale)}"
    for rid, words in KEYWORDS.items():
        for w in words:
            assert w in words_of(rid), f"{rid}: {w!r} not in the quotation"
    assert set(KEYWORDS) == set(TRANSLATIONS.values())
    # the misreadings quoted in the 史料说明 are those of MISPRINTS
    deeper = re.search(r"\\begin\{deeper\}\[史料说明\].*?\\end\{deeper\}", tex_text(), re.DOTALL).group(0)
    for q in MISREAD:
        assert f"“{q}”" in deeper, q
        rid = TRANSLATIONS[q]
        assert any(m[0] == rid and (q in m[1] or m[1] in q) for m in MISPRINTS), q
    # every source of the chapter is in copyright or allows short phrases only: at most 12 characters
    for q in used - set(MISREAD):
        assert len(q) <= 12, f"a long quotation: “{q}”"
    print(f"ok {n} quotations of the text found in the snapshot ({len(used)} distinct)")


# ---------------------------------------------------------------------------------------------------
# 3. Numbers: said() and the parts of the text it does not read
UNITS = {"万亿": 10 ** 12, "亿": 10 ** 8, "万": 10 ** 4}
AMOUNT = re.compile(r"(\d[\d,]*(?:\.\d+)?)(?:\s*(万亿|亿|万))?")
# what is not a number of the story: labels, citations, cross-references, the key equations (models() reads them), the
# sub- and superscripts of the math and the numbers of the parts of an example
MASKS = [re.compile(r"\\begin\{keyeq\}.*?\\end\{keyeq\}", re.DOTALL),
         re.compile(r"\\(?:label|cite|chref|secref|figref|tabref|exref|eqref|ref|nameref|url|fig)\{[^}]*\}"),
         re.compile(r"_\{[^}]*\}|_\d"),
         re.compile(r"\^\{\d+\}"),
         re.compile(r"（\d）"),
         re.compile(r"\{(?:fig|tab):[^}]*\}|\\multicolumn\{\d+\}"),             # the label of a figure, column spans
         re.compile(r"\\begin\{tabularx\}\{\\linewidth\}\{[^\n]*")]                # the column widths of the tables
COVERED: list[str] = []                    # the phrases said() has read


def mask(s: str) -> str:
    """The string with the parts that print no number of the story blanked out (same length)."""
    for p in MASKS:
        s = p.sub(lambda m: " " * len(m.group(0)), s)
    return s


def say(*phrases: str) -> None:
    """The phrases are in the text."""
    t = tex_text()
    for s in phrases:
        assert s in t, f"not in the text: {s!r}"


def said(phrase: str, *values: float | None, slack: float = 0.0) -> None:
    """The phrase is in the text, and each number it prints (with its unit 万; a minus sign not read) is the value
    given, within half a unit of its last digit (plus `slack`, in the same units). None skips a number (one checked by
    an assertion)."""
    say(phrase)
    found = AMOUNT.findall(mask(phrase).replace("{,}", ","))                     # 10{,}000 in the math
    assert len(found) == len(values), f"{phrase!r}: {len(found)} numbers {found}, {len(values)} values"
    for (digits, unit), v in zip(found, values):
        if v is None:
            continue
        scale = UNITS.get(unit, 1)
        decimals = len(digits.split(".")[1]) if "." in digits else 0
        tol = (0.5 * 10 ** -decimals + slack) * scale
        quoted(f"{phrase[:60]!r}: {digits}{unit}", float(v), figure(digits) * scale, tol=tol + 1e-9 * scale)
    COVERED.append(phrase)


def told(phrase: str, pre: str, post: str = "") -> float:
    """The phrase is in the text; the Chinese numeral it prints between `pre` and `post` (to the end of the phrase when
    post is empty), read by zh()."""
    say(phrase)
    m = re.search(re.escape(pre) + ("(.+?)" + re.escape(post) if post else "(.+)$"), phrase)
    assert m, (phrase, pre, post)
    return zh(m.group(1))


def there(ch: str, words: str) -> list[float]:
    """The words are in another chapter's text; the numbers they print."""
    assert words in chapter(ch), (ch, words)
    return [figure(d) * UNITS.get(u, 1) for d, u in AMOUNT.findall(mask(words))]


def coverage() -> None:
    """Every Arabic number of the text lies inside a phrase read by said()."""
    t = tex_text()
    m = mask(t)
    covered = bytearray(len(t))
    for s in set(COVERED):
        k = t.find(s)
        while k >= 0:
            covered[k:k + len(s)] = b"\x01" * len(s)
            k = t.find(s, k + 1)
    runs_ = list(re.finditer(r"\d+", m))
    bad = [(r.group(), t[max(0, r.start() - 25):r.end() + 10].replace("\n", " ")) for r in runs_
           if not all(covered[r.start():r.end()])]
    for b in bad[:60]:
        print("    not read:", b)
    assert not bad, f"{len(bad)} numbers of the text not read by said()"
    print(f"ok all {len(runs_)} numbers of the text are read by said() ({len(set(COVERED))} phrases)")


def paragraph(start: str) -> str:
    """The paragraph of the text that contains `start`, from `start` to its end."""
    t = tex_text()
    return t[t.index(start):].split("\n")[0]


def version(key: str) -> str:
    return meta()["sources"][key]["version"]


def their(name: str, rid: str, *words: str) -> list[str]:
    """Row rid of another chapter's snapshot: the words are in its quotation; its values as printed (';'-separated)."""
    df = load_snapshot(name, dtype=str, keep_default_na=False)[0].set_index("id")
    q = " ".join(df.loc[rid, "quote"].split())
    for w in words:
        assert w in q, (name, rid, w)
    return df.loc[rid, "value"].split(";") if df.loc[rid, "value"] else []


def showa(n: float) -> int:
    """昭和 n -> the Gregorian year."""
    return int(n) + 1925


def minguo(n: float) -> int:
    """民國 n -> the Gregorian year."""
    return int(n) + 1911


# ---------------------------------------------------------------------------------------------------
# The models, with the teaching inputs of the examples and the self-check
JP = (1955, 1973)                                         # Japan's high growth (the text's PWT computations)
REP = dict(dep_cap=0.04, loan_cap=0.06, infl=0.06, dep_free=0.02, loan_free=0.04, n=100, years=10)
SC_REP = dict(dep_cap=0.03, infl=0.05, dep_free=0.01, n=100)   # self-check 4
DUAL_EX = (0.5, -0.01, 0.04)                              # ex:eastasia-dual (1): capital share, g_r, g_w
SC_DUAL = (0.4, 0.0, 0.03)                                # self-check 3
SC_HK_SHARE = 0.70                                        # self-check 1: Hong Kong's labour share
SC_R = 0.20                                               # self-check 2: Krugman's return falls to 20 per cent
EQ_ACC = r"g_Y=\alpha\,g_K+(1-\alpha)\,(g_L+g_h)+g_A ,\label{eq:eastasia-accounting}"
EQ_DUAL = r"g_A\equiv g_Y-s_K\,g_K-s_L\,g_L=s_K\,g_r+s_L\,g_w ,\label{eq:eastasia-dual}"


def residual(gY: float, share_k: float, gK: float, gL: float) -> float:
    """eq:eastasia-accounting with the labour input already weighted (Young's tables): g_A = g_Y - a g_K - (1-a) g_L."""
    return gY - share_k * gK - (1 - share_k) * gL


def dual(sK: float, gr: float, gw: float) -> float:
    """eq:eastasia-dual: g_A = s_K g_r + s_L g_w."""
    return sK * gr + (1 - sK) * gw


def krugman(r: float, s: float, y: float) -> tuple[float, float, float]:
    """Krugman's footnote 3: investment s*y, the output it adds r*s*y, the growth rate r*s."""
    inv = s * y
    return inv, r * inv, r * inv / y


def repression(dep_cap, loan_cap, infl, dep_free, loan_free, n, years) -> dict:
    dep, loan = dep_cap - infl, loan_cap - infl
    return dict(dep=dep, loan=loan, savers=(dep_free - dep) * n, firms=(loan_free - loan) * n,
                capped=n * (1 + dep) ** years, free=n * (1 + dep_free) ** years)


def models() -> None:
    t = TEX.read_text(encoding="utf-8")
    assert EQ_ACC in t and EQ_DUAL in t
    rng = np.random.default_rng(42)
    # eq:eastasia-accounting: Y = A K^a (hL)^(1-a) on exponential paths, log growth over a year
    for _ in range(200):
        a, gK, gL, gh, gA = rng.uniform(0.2, 0.7), *rng.uniform(-0.03, 0.12, 4)
        K0, L0, h0, A0 = rng.uniform(0.5, 5, 4)
        Y = lambda s: A0 * math.exp(gA * s) * (K0 * math.exp(gK * s)) ** a * (h0 * math.exp(gh * s) * L0 * math.exp(gL * s)) ** (1 - a)  # noqa: E731
        assert abs(math.log(Y(1) / Y(0)) - (a * gK + (1 - a) * (gL + gh) + gA)) < 1e-12
    # eq:eastasia-dual: Y = rK + wL; at each instant the primal residual with the current shares equals the dual
    for _ in range(200):
        gr, gw, gK, gL = rng.uniform(-0.05, 0.1, 4)
        r0, w0, K0, L0 = rng.uniform(0.05, 0.5), rng.uniform(0.5, 2), rng.uniform(1, 10), rng.uniform(1, 10)
        f = lambda s, g, x: x * math.exp(g * s)                                    # noqa: E731
        Y = lambda s: f(s, gr, r0) * f(s, gK, K0) + f(s, gw, w0) * f(s, gL, L0)    # noqa: E731
        h = 1e-6
        gY = (math.log(Y(h)) - math.log(Y(-h))) / (2 * h)
        sK = r0 * K0 / Y(0)
        assert abs((gY - sK * gK - (1 - sK) * gL) - dual(sK, gr, gw)) < 1e-8
    # the examples
    y4 = facts()["y4_t31"], facts()["y4_t41"]
    hk = residual(y4[0][0], 1 - y4[0][4], y4[0][1], y4[0][2])
    sg = residual(y4[1][0], 1 - y4[1][4], y4[1][1], y4[1][2])
    chk("ex:eastasia-young HK", hk, y4[0][3], tol=0.0005)
    chk("ex:eastasia-young SG", sg, y4[1][3], tol=0.0005)
    inv, add, g = krugman(0.4, 0.2, 10_000)
    assert (inv, add, round(g, 10)) == (2000, 800, 0.08)
    R = repression(**REP)
    assert np.isclose(R["dep"], -0.02) and np.isclose(R["loan"], 0) and np.isclose(R["savers"], R["firms"])
    print("ok the key equations and the claims made of them on 400 random draws; the examples' arithmetic")


# ---------------------------------------------------------------------------------------------------
# 4. The text, section by section
def guide(F, Y, Q):
    t = TEX.read_text(encoding="utf-8")
    assert f"\\guidequestion{{{GUIDE}}}" in t and GUIDE == PREV
    assert chapter("ch41_development").rstrip().endswith(PREV)                     # 第 41 章交来的问题
    assert ("\\guideprereq{\\chref{ch:solow}\\enspace\\nameref{ch:solow}；"
            "\\chref{ch:development}\\enspace\\nameref{ch:development}}") in t
    johnson = int(re.search(r"\(Johnson (\d{4}), p\. \d+\)", Q["wb_johnson"]).group(1))
    said("描述日本 1955—1973 年高速增长的特征与产业政策（世界银行 1993 年报告的概括，及其转引的 Johnson 1982）",
         *JP, F["wb_copyright"][0], johnson)
    said("概括世界银行（1993）报告与 Krugman（1994）、Young（1994）的争论", F["wb_copyright"][0], F["kg_source"][0],
         F["y4_date"][0])
    assert "\\chapterstub" not in t


def opening(F, Y, Q):
    d, y = F["wn_date"]
    has("wn_date", "SUNDAY, SEPTEMBER 26, 1993")
    assert pd.Timestamp(int(y), mon("wn_date", "SEPTEMBER"), int(d)).day_name() == "Sunday"
    said("1993 年 9 月 26 日是星期日", y, 9, d)
    num = re.search(r"NO\. (\d+)/S(\d+)", Q["wn_number"])
    said("世界银行在华盛顿发出第 93/S17 号新闻稿", int(num.group(1)), int(num.group(2)))
    has("wn_headline", '"MIRACLE" COULD BE REPEATED IN OTHER COUNTRIES')
    say("用标题宣布东亚的经济“奇迹”可以在别的国家重演")
    has("wn_poverty", "during the past three decades has lifted millions of people out of poverty")
    assert told("它说，过去三十年东亚的快速增长让数以百万计的人摆脱了贫困", "过去", "年") == 10 * F["wn_poverty"][0]
    has("wn_eight", "eight economieq: Hong Kong, Indonesia, Japan, Malaysia,")
    has("wn_eight2", "Republic of Korea, Singapore, Taiwan and Thailand")
    assert told("增长大多发生在八个经济体", "发生在", "个") == F["wn_eight"][0]
    say("它们是香港、印度尼西亚、日本、马来西亚、韩国、新加坡、台湾与泰国")
    s60, a, b, c = F["wn_twice"]
    said("按新闻稿的说法，1960 年以来", s60)
    assert (a, b, c) == (2, 3, 5)
    say("它们增长的速度是东亚其余地方的两倍，拉丁美洲与南亚的三倍，撒哈拉以南非洲的五倍")
    has("wn_page", "John Page, the leader of a research team")
    has("wb_team", "LED by John Pagc")
    say("新闻稿介绍的是世界银行的政策研究报告《东亚奇迹：经济增长与公共政策》，研究组的组长是佩奇（John Page，生卒年未详）")
    has("wb_bangkok", "1991AnnualMeetings", "World Bank in Bangkok")
    said("这项研究是他 1991 年在曼谷的世界银行年会上宣布的", F["wb_bangkok"][0])
    said("前言署的日期是 1993 年 8 月", F["wb_august"][0], mon("wb_august", "August"))
    has("wb_accumulation", "extraordinarygrowthisdue cosuperior accumulation of physical and human capita")
    has("wb_miraculous", "nothing'miraculous\"aboutthe EastAsianeconomics'success")
    say("在这个意义上，东亚的成功没有什么“神奇”之处")
    has("wb_japan_support", "The support of the Government ofjapan for the researchprogram")
    has("wb_financial", "The financialassistanceof the Govemrnment ofJapan is gratefullyacknowledged")
    say("前言的末尾感谢日本政府对这项研究的支持", "研究组在致谢里写明，日本政府给了资金援助")
    has("wb_twothirds", "account for roughly twothirds of the growth", "The remainder is attributable to improved productivity")
    assert abs(told("高投资与人力资本大约解释了增长的三分之二", "增长的") - F["wb_twothirds"][0]) < 1e-6
    has("wb_exceeds", "exceeds that of most other developing and industrial economies")
    has("kg_parallel", "Warsaw Pact nations in the 1950s")
    said("一年以后，Krugman 在《外交事务》上把东亚的增长比作 1950 年代华约国家的增长", F["kg_parallel"][0])
    assert F["kg_source"][0] == F["wn_date"][1] + 1
    has("kg_perspiration", "based on perspiration rather than")
    say("说新加坡的增长靠的是“汗水”", "上一章末尾说的最早转向出口的几个经济体，都在这八个里面（\\chref{ch:development}）")
    assert paragraph("标题里是奇迹，前言里并不神奇").endswith(GUIDE)                  # the opening ends with the question


def world(F, Y, Q):
    m, d = F["wp56_issued"][1:]
    has("wp56_issued", "昭和３１年７月１７日発行")
    has("wp56_title", "昭和31年度 年次経済報告")
    said("1956 年 7 月 17 日，经济企画厅的昭和 31 年度《年次经济报告》发行", showa(F["wp56_issued"][0]), m, d,
         F["wp56_title"][0])
    has("wp56_hakusho", "経済白書")
    assert F["wp56_hakusho"][0] == F["wp56_title"][0] == F["wp56_issued"][0]
    has("wp56_sengo", "もはや「戦後」ではない")
    has("wp56_modern", "回復を通じての成長は終わった", "近代化によって支えられる")
    has("wp56_burden", "その遂行に伴う負担は国民相互にその力に応じて分け合わねばならない")
    # Chapter 35: the Dodge Line, 360 yen and the Korean War
    assert there("ch35_reconstruction", "1949 年 4 月的道奇预算与 360 日元的单一汇率以后") == [1949, 4, 360]
    assert there("ch35_reconstruction", "1950 年 6 月 25 日，朝鲜战争爆发") == [1950, 6, 25]
    said("道奇计划与每美元 360 日元的单一汇率以后，1950 年的朝鲜战争带来了美军的特需", 360, 1950)
    has("wp56_race", "原子兵器の競争から平和的競存に移った", "経済成長率の闘い", "生産性向上のせり合い")
    has("wp56_pain", "苦痛")
    # Chapter 39's numbers
    assert there("ch39_consumption", "1956—1973 年，实际国内总支出平均每年增长约 9.2\\%（本书的计算）") == [1956, 1973, 9.2]
    assert there("ch39_consumption", "家庭储蓄率在 1974 年与 1976 年都到了 23.2\\%") == [1974, 1976, 23.2]
    said("1956—1973 年，日本的实际国内总支出平均每年增长约 9.2\\%（\\chref{ch:consumption}）", 1956, 1973, 9.2)
    said("同一时期家庭储蓄率也在上升，1974 年与 1976 年都到了 23.2\\%", 1974, 1976, 23.2)
    L = levels()
    said("按 Penn World Table，日本的人均 GDP 1950 年约为美国的 18\\%，1973 年约为 59\\%（本书的计算）",
         1950, L["JPN"][1950], 1973, L["JPN"][1973])
    has("kg_torrid", "8.9")
    said("1973 年以前的十年里日本实际 GDP 每年增长 8.9\\%", 1973, F["kg_torrid"][0])
    said("他说，1973 年日本的人均 GDP 只有美国的 55\\%", 1973, F["kg_55"][0])
    has("kg_55", "55 percent")
    P = pwt()["JPN"]
    g = lambda v, a=JP[0], b=JP[1]: 100 * math.log(P.loc[b, v] / P.loc[a, v]) / (b - a)   # noqa: E731
    said("按 Penn World Table，1955—1973 年日本的资本存量每年增长约 10\\%（本书的计算）", *JP, g("rnna"), slack=0.3)
    said("同期就业每年只增长约 1.4\\%，人均 GDP 每年增长约 7.8\\%，都是对数增长率（本书的计算）", g("emp"),
         g("rgdpna") - g("pop"))
    said("投资占 GDP 的比例从 1955 年的约 18\\% 升到 1973 年的约 42\\%（本书的计算）",
         JP[0], 100 * P.loc[JP[0], "csh_i"], JP[1], 100 * P.loc[JP[1], "csh_i"])
    has("kg_slow", "gdp per capita grew only 3 percent per year")
    a, b = (int(x) for x in re.search(r"(\d{4})-(\d{4})", column("note")["kg_slow"]).groups())
    said("1973 年以后增长慢了下来，Krugman 说 1973—1992 年日本的人均 GDP 每年只增长 3\\%", a, a, b, F["kg_slow"][0])
    plan_y, plan_m = F["wp61_plan"]
    has("wp61_plan", "政府決定をみた「国民所得倍増計画」")
    said("1960 年 12 月，日本政府决定了《国民所得倍增计划》", showa(plan_y), plan_m)
    y61, y70 = F["wp61_invest"]
    said("1961 年度民间设备投资的规模，已经快要赶上计划最后一年 1970 年度的水平", showa(y61), showa(y70))
    said("按 Penn World Table，日本 1970 年的实际 GDP 约为 1960 年的 2.6 倍（本书的计算）", 1970,
         1960, P.loc[1970, "rgdpna"] / P.loc[1960, "rgdpna"])
    a, b = F["loc_sakomizu"]
    has("loc_sakomizu", "Sakomizu, Hisatsune, 1902-1977")
    said("这份白皮书的序言署名是经济企画厅长官迫水久常（1902—1977）", a, b)
    ys, ms, ds = F["wp61_signed"]
    said("序言的日期是 1961 年 7 月 14 日", showa(ys), ms, ds)
    has("wp61_signed", "迫水 久常 ( 経済企画庁長官 )")
    for rid in ("wp61_fullemp", "wp61_lowwage", "wp61_nopolitics", "wp61_control"):
        assert words_of(rid), rid
    has("wp61_lowwage", "労働力の過剰従って労銀の低位を前提として", "きらいがあり")     # the hedge: 有…的倾向
    say("他说，日本经济过去的生产，多少有以劳动力过剩、因而工资低为前提的倾向")
    has("wp61_control", "神")
    # the Four Tigers
    has("wb_fourtimes", "more than four times in Japan and the Four Tigers")
    a, b, k = F["wb_fourtimes"]
    said("按研究组的数，1960—1985 年日本与四虎的实际人均收入增加到四倍多", a, b)
    assert told("1960—1985 年日本与四虎的实际人均收入增加到四倍多", "增加到", "倍") == k
    has("wb_tigers", "have been growing rapidly for decadesand havejoined or approached the ranksof high-income economies")
    lo, hi = F["y4_t11_hksg"][0], F["y4_t11_krtw"][0]
    assert lo == min(F["y4_t11_hksg"] + F["y4_t11_krtw"]) and hi == max(F["y4_t11_hksg"] + F["y4_t11_krtw"])
    said("按 Young 的统计，1966—1990 年前后，四个经济体的人均 GDP 每年增长 5.7\\%—6.9\\%，香港最低，韩国最高",
         1966, 1990, lo, hi)
    has("y4_log", "log")
    # Chapter 40's nine economies
    assert there("ch40_solow", "1960—2019 年人均增长率每年超过 4\\% 的有 9 个经济体，即台湾、韩国、博茨瓦纳、新加坡") \
        == [1960, 2019, 4, 9]
    said("上一章用 Penn World Table 算过，1960—2019 年人均增长率每年超过 4\\% 的九个经济体里", 1960, 2019, 4)
    has("rd_poorer", "In 1960")
    said("Rodrik 说，1960 年的韩国比许多撒哈拉以南非洲国家还穷", F["rd_poorer"][0])
    said("按 Penn World Table，韩国 1960 年的人均 GDP 约为美国的 6.5\\%，2019 年约为 64\\%（本书的计算）",
         1960, L["KOR"][1960], 2019, L["KOR"][2019])
    said("新加坡 1960 年约为美国的 15\\%，2019 年约为 140\\%（本书的计算）", 1960, L["SGP"][1960], 2019, L["SGP"][2019])
    said("五个经济体的人均 GDP 相对美国的水平，1950—2019 年（对数刻度，美国＝100）", 1950, 2019, 100)
    first = {c: int(L[c].dropna().index.min()) for c in L}
    assert first == {"JPN": 1950, "KOR": 1953, "TWN": 1951, "HKG": 1960, "SGP": 1960}, first
    said("韩国从 1953 年起，香港与新加坡从 1960 年起", first["KOR"], first["HKG"])
    said("日本与台湾从 1950 年代初起", first["JPN"])
    assert first["TWN"] < 1955
    said("数据：Penn World Table 10.01（Feenstra、Inklaar 与 Timmer 2015，CC BY 4.0）的支出法实际 GDP（按 2017 年美元的链式购买力平价）除以人口",
         10.01, 2015, 4.0, 2017)


def state(F, Y, Q):
    has("wb_park", "in 1961, when army General Park Chung Hee seized power and reorganized the govemment to promote rapid development")
    b, d = F["loc_park"]
    said("1961 年，陆军将领朴正熙（Park Chung Hee，1917—1979）在韩国夺取了政权", F["wb_park"][0], b, d)
    has("wb_epb", "Economic Planning Board")
    for rid in ("wb_banking", "wb_uneven"):
        assert words_of(rid), rid
    m_, d_, y_ = F["loc_park_note"]
    has("loc_park_note", "assassinated, 10/26/79")
    said("1979 年 10 月 26 日，朴正熙遇刺身亡", 1900 + y_, m_, d_)
    y61, y73 = F["wb_takeoff"]
    has("wb_takeoff", "aggressive promotion of exports was combined with-classicimport protection at home")
    said("1961—1973 年是韩国的出口起飞期", y61, 1900 + y73)
    has("wb_neutral", "biased in fiavorof exports as a whole but essentiallyneutral")
    a, b_, share = F["wb_korea_policy"]
    said("按研究组的数，1973—1981 年，韩国的政策性贷款约占存款货币银行全部贷款的 60\\%", a, b_, share)
    has("wb_targets", "In Japan, Korea, and Thailand, implicit or explicit export targets")
    has("cb_rd_single", "from the early 1960s in Korea")
    said("Rodrik 在评论 Collins 与 Bosworth 时说，韩国政府从 1960 年代初起一心追求投资与增长", F["cb_rd_single"][1])
    has("cb_rd_tools", "includingadministrativeguidance, creditsubsidies, tax incentives, public enterprises")
    has("wb_statebanks", "stare-controlled banking system")
    has("wb_bank_export", "banks increasingly used export performance as the criterion of creditworthiness")
    y73, y79 = F["wb_hci_shift"]
    said("1973—1979 年的重化工业推动是一次大转向", y73, 1900 + y79)
    has("wb_hci_shift", "a commitment by govremment to use all its levers to steer resources into specific sectors")
    has("wb_hci_six", "steel, petrochemicals, nonferrous metals, shipbuilding, electronics, and machinery")
    assert told("专门的立法挑出六个战略产业", "挑出", "个") == F["wb_hci_six"][0]
    say("钢铁、石化、有色金属、造船、电子与机械，给它们税收优惠与优惠融资等支持")
    has("wb_hci_motive", "both strategic-to increasedefensecapability-and economic")
    has("wb_hci_partly", "Korea was at least partly successful")
    has("wb_hci_starved", "labor-intensive industries were starved of credit")
    has("wb_hci_switch", "When the second oil shock hit", "The government switchled course")
    has("wb_hci", "did not live up to expectations")
    has("wb_hci_costs", "still not filly known, but theywere high")
    said("它的代价在 1993 年还不完全清楚，但很高", F["wb_copyright"][0])
    y47 = F["wb_korea_land1"][0]
    has("wb_korea_land1", "initiated by U.S. forcesin 1947", "to the tillersand put a ceiling on rents of other land")
    said("韩国的土地改革第一步由美军在 1947 年发起", y47)
    has("wb_korea_land2", "begun in 1950 and completed after the Korean War")
    said("第二步由韩国政府在 1950 年开始，朝鲜战争以后完成", F["wb_korea_land2"][0])
    has("wb_korea_land", "900,000")
    said("把地分给了 90 万名佃农", F["wb_korea_land"][0])
    # Japan
    has("wb_weak", "in the first fifteen yearsafter World War II")
    assert told("二战后头十五年", "头", "年") == F["wb_weak"][0]
    say("二战后头十五年，日本用保护性关税与金融优惠扶持了几个弱小的产业")
    has("wb_japan_credit", "until the early 1970s")
    said("直到 1970 年代初，政府都把信贷导向大企业", F["wb_japan_credit"][0])
    y78, erp = F["wb_miti"]
    has("wb_miti", "MITI allocated foreign exchange to favored large firms")
    said("到 1978 年，制造业的平均有效保护率还有 22\\%", y78, erp)
    has("wb_diet", "the diet (parliament)merely ratifieswhatthe bureaucracyhasprepared")
    has("wb_npa2", "an independent body that sets the bureaucray's pay scales and promotdon policies")
    has("wb_npa", "names only his ministers and, except in a few caes, one of the two vice-nunisters in each ministry")
    has("wb_guidance", "the useof threatsand rewards")
    has("wb_guidance_law", "doesnot depend on any law or regulation")
    said("1960 年代中期以前，行政指导都是通商产业省官僚的有力工具", F["wb_guidance_tool"][0])
    has("wb_guidance_tool", "Until the mid-1960s")
    has("wb_miti_fx", "ForeignExchangeand Trade Control Law")
    a, b = F["wb_liberalize"]
    said("这个过程从 1960 年代中期开始，到 1979 年才结束", a, b)
    lo, hi = F["wb_filp_absorbed"]
    said("按研究组的数，高速增长期它吸收了家庭储蓄的 20\\%—40\\%，1950 年代约占新增设备贷款的三分之一", lo, hi,
         F["wb_filp_third"][1])
    assert abs(told("1950 年代约占新增设备贷款的三分之一", "贷款的") - F["wb_filp_third"][0]) < 1e-6
    has("wp61_window", "日銀窓口規制")
    said("经济企画厅 1961 年说，紧缩通过日本银行的窗口规制来实行", showa(F["wp61_title"][0]))
    johnson = int(re.search(r"\(Johnson (\d{4}), p\. \d+\)", Q["wb_johnson"]).group(1))
    has("wb_johnson_q", "wage policies tied to increasesin productivity")
    said("研究组引 Johnson（1982）的话说", johnson)
    p1, a1, p2, a2 = F["wb_jdb"]
    has("wb_jdb", "in 1951-55 and just 0.01 percent in 1956-65")
    assert p1 < 0.1 and abs(p2 - 0.01) < 1e-9                                       # 不到千分之一，万分之一
    said("1951—1955 年核销的坏账不到平均贷款余额的千分之一，1956—1965 年只有万分之一", a1, 1955, a2, 1965)
    has("wb_jdb_why", "Coupled with Japan's overall economic success, effltive pre-appraisal and monitoring")
    said("日本存款的实际利率直到 1983 年都是负的，但很稳定", F["wb_japan_negative"][0])
    for rid in ("wb_controlled", "wb_savers", "wb_repdef", "wb_transfer", "wb_spread"):
        assert words_of(rid), rid
    has("wb_controlled", "during much oF their rapid growth")                       # not the whole of it
    say("所有高绩效经济体在高速增长的很长一段时间里都管制存贷款利率")
    # ex:eastasia-repression
    R = repression(**REP)
    said("教学输入：存款利率上限 4\\%，贷款利率上限 6\\%，通胀率 6\\%；没有上限时，存款的实际利率是 2\\%，贷款的实际利率是 4\\%",
         100 * REP["dep_cap"], 100 * REP["loan_cap"], 100 * REP["infl"], 100 * REP["dep_free"], 100 * REP["loan_free"])
    said("每存 100 单位、由银行贷给企业", REP["n"])
    said("100 单位的存款 10 年后的购买力各是多少", REP["n"], REP["years"])
    said("存款$4\\%-6\\%=-2\\%$，贷款$6\\%-6\\%=0$", 4, 6, -100 * R["dep"], 6, 6, 100 * R["loan"])
    said("储户少得$2-(-2)=4$单位，企业少付$4-0=4$单位", 2, 2, R["savers"], 4, 0, R["firms"])
    said("$100\\times0.98^{10}\\approx81.7$，$100\\times1.02^{10}\\approx121.9$", 100, 0.98, R["capped"], 100, 1.02, R["free"])
    # Taiwan
    y1, m1, d1, y2, m2, d2 = F["tw_martial"]
    has("tw_martial", "自民國三十八年五月二十日起至七十六年七月十四日止")
    has("tw_title", "戒嚴時期人民受損權利回復條例")
    said("1995 年公布的《戒严时期人民受损权利回复条例》界定了戒严的时期", minguo(F["tw_dates"][0]))
    said("按这部条例，台湾地区的戒严从 1949 年 5 月 20 日起", minguo(y1), m1, d1)
    said("戒严到 1987 年 7 月 14 日为止", minguo(y2), m2, d2)
    has("wb_authoritarian", "authoritarian governments&cing a communist threat were dependent on the assistanceof the United States")
    has("wb_tw_landlords", "Former landlords, as new shareholdersin state enterprises")
    a, b, c = F["wb_tl_tw"]
    has("wb_tl_tw", "Nineteen-Point Program", "Statutes for Encouragement of Investment", "Single Uniform Exchange Rate")
    said("按研究组的年表，1959 年有十九点财经改革方案，1960 年有奖励投资条例，1961 年改为单一汇率", a, b, c)
    said("出口在 1960 年代中期起飞", F["rd_tookoff"][0])
    said("出口转向发生在 1960 年前后", F["wb_tl_tw"][1])
    said("他在 1996 年的评论里说，台湾政府从 1960 年起一心追求投资与增长", F["cb_journal"][1], F["cb_rd_single"][0])
    has("cb_rd_single", "from 1960 in Taiwan")
    said("约占出口总值的 60\\%", F["wb_tw_sme"][0])
    # Singapore and Hong Kong
    has("y2_entrepot", "British colonies that served as entrepot trading ports")
    has("y2_conduit", "Hong Kong processed trade between Mainland China and the rest of the world")
    said("1950 年代初，从上海逃来的企业家在香港开办工厂", F["y2_textiles"][0])
    has("y2_textiles", "refugee Shanghainese entrepreneurs opened factories")
    a, b = F["y2_stagnation"]
    said("1950 年代与 1960 年代初经济停滞", a, b)
    said("Young 说，1960 年香港与新加坡的人均 GDP 很接近", F["y2_close"][0])
    said("新加坡政府从 1960 年代初起用强制的国民储蓄和大举招引外资来积累资本", F["y2_laissez"][0])
    has("y2_maximalist", "financed, in the main, by extensive taxation of labor income")
    i60, y60, i84, y84 = F["y2_invest"]
    said("新加坡的投资占 GDP 的比例从 1960 年的 9\\% 升到 1984 年的 43\\%", y60, i60, y84, i84)
    # Summers-Heston at constant international prices, not Young (1994)'s 11% -> 47% at constant (national) prices
    assert "constant international prices" in column("note")["y2_invest"]
    say("按不变的国际价格，新加坡的投资占 GDP 的比例从")
    said("香港一直在 20\\% 上下", F["y2_hk20"][0])
    y1, a1, b1, y2_, a2, b2 = F["y2_school"]
    said("Barro 在评论里估计，1960 年成人平均上学的年数香港是 6.2 年，新加坡是 3.5 年", y1, a1, b1)
    said("到 1985 年，两地分别是 8.0 年与 5.6 年", y2_, a2, b2)
    y59, tax, n1, n2 = F["y2_pioneer"]
    said("1959 年起的先锋企业地位让选中的企业 5 年、10 年或更久免缴 40\\% 的利润税", y59, n1, n2, tax)
    has("y2_foreign", "the overwhelming majority of participants are foreign")
    # the case box
    y55, e55, r55 = F["y2_cpf55"]
    said("\\begin{case}{新加坡 · 1955—1990 · 中央公积金}", F["y2_cpf55"][0], F["y2_mandays"][4])
    said("中央公积金 1955 年设立，是按个人账户积累的社会保障计划", y55)
    assert cpf_at("1955-07", "Employer") == cpf_at("1955-07", "Employee") == e55 == r55
    assert cpf().index.min() == "1955-07"
    said("35 岁及以下的雇员与雇主 1955 年 7 月起各缴工资的 5\\%", 35, 1955, 7, cpf_at("1955-07", "Employee"))
    assert cpf_at("1984-07", "Employee") == cpf_at("1984-07", "Employer") == F["y2_cpf84"][4]
    assert cpf_at("1984-06", "Employee") < 25 and F["y2_cpf84"][3] == 1984
    said("1984 年 7 月起，双方各缴 25\\%", 1984, 7, cpf_at("1984-07", "Employee"))
    has("y2_housing", "housing")
    y80, g80 = F["y2_govsec"]
    said("1980 年，基金的 95.1\\% 投在政府证券上", y80, g80)
    y85, gnp, sav = F["y2_gnp"]
    said("1985 年缴费达到顶峰，相当于国民生产总值的 14.9\\%，国民总储蓄的 36\\%", y85, gnp, sav)
    has("wb_provident", "mandatory provident fund contributions")
    a, b, c, seats = F["wb_tl_sg"]
    has("wb_tl_sg", "People's Action Party")
    said("人民行动党 1959 年起领导自治的新加坡，1965 年新加坡脱离马来西亚联邦独立", a, b)
    said("1968 年的大选里，人民行动党赢得全部 58 个议席", c, seats)
    has("loc_lee_note", "first prime minister of Singapore")
    yb, yd = F["loc_lee"]
    said("李光耀（Lee Kuan Yew，1923—2015）是新加坡的第一任总理", yb, yd)
    assert F["gnd_lee"][0] == yb and F["gnd_lee_d"][0] == yd
    y86, r86 = F["y2_fn30"]
    assert cpf_at("1986-04", "Employer") == r86 and cpf_at("1986-03", "Employer") > r86
    said("1986 年 4 月，雇主的缴费率降到 10\\%", y86, 4, r86)
    has("y2_fn30", "to stimulateinvestment")
    said("Young 说，1968 年通过的劳工立法", F["y2_1968b"][0])
    has("y2_list", "promotion")
    mandays, mid, two, a, b = F["y2_mandays"]
    said("罢工损失的工作日，1960 年代中期每年约 4 万个", mid, mandays)
    said("1978—1990 年，除两年外都是零", a, b)
    assert two == 2
    has("wb_sg_unions", "lirmitedunion")
    # the figure of the case box
    D = cpf()
    said("新加坡中央公积金的缴费率（工资的百分比，35 岁及以下），1955—1990 年", 35, 1955, 1990)
    said("1984 年 7 月起各为 25\\%，1986 年 4 月雇主的缴费率降到 10\\%", 1984, 7, cpf_at("1984-07", "Employer"), 1986, 4,
         cpf_at("1986-04", "Employer"))
    retrieved = meta_cpf()["retrieved"]
    said("2026 年 11 月 12 日从 data.gov.sg 下载，依新加坡开放数据许可 1.0 版使用", *[int(x) for x in retrieved.split("-")], 1.0)
    assert len(D) > 10
    # consumers, the summary and shared growth
    has("wb_consumer", "Japan, Korea and Taiwan, China, all imposed stringent contrls")
    has("wb_restrict", "have welfare costs")
    has("wb_payoffs", "Savings, forced or not")
    has("wb_soviet", "such as the fonrer Soviet Union")
    has("wb_housing", "Hong Kong")
    has("wb_shared", "promising that as the economy expanded all groupswould benefit")
    has("wb_leaders", "either authoritarian or paternalisdtithey")
    has("wn_gap", "reducing the gap between the rich and poor")


def meta_cpf() -> dict:
    return load_snapshot("cpf_rates_1955_2026")[1]


def accounting_section(F, Y, Q):
    has("y4_boring", "This is a fairly boring and tedious paper, and is intentionally so.")
    said("Young 1994 年的工作论文，开头一句就说", F["y4_date"][0])
    has("y4_singapore", "while disagreeing with most of my analysis and all of my conclusions")
    has("y4_unprecedented", "virtually unprecedented, the growth of total factor productivity in these economies is not")
    a, b, c = F["y4_particip"]
    said("Young 算过，就业人口比例的上升使香港的人均增长每年多出 1 个百分点，韩国与台湾分别多出 1.2 与 1.3 个百分点", a, b, c)
    g, n = F["y4_stunning"]
    said("新加坡更多，24 年里每年多出 2.6 个百分点", n, g)
    y66, y90, two3 = F["kg_edu"]
    said("按 Krugman 转引 Young 的数，新加坡 1966 年过半的工人没有受过正规教育，1990 年三分之二读完了中学", y66, y90)
    assert abs(told("1990 年三分之二读完了中学", "1990 年", "读完") - two3) < 1e-6
    has("y4_weighting", "contributes to about 1% per annum additional growth in labour input")
    said("使每个经济体的劳动投入每年多增长约 1\\%", F["y4_weighting"][0])
    i60, y60, _, _, i84, y84 = F["y4_sg_invest"]
    said("按不变价格，新加坡的投资占 GDP 的比例 1960 年是 11\\%，1984 年达到 47\\%", y60, i60, y84, i84)
    k5, k50, _, _, _, k40, k91 = F["y4_kr_invest"]
    said("韩国从 1950 年代初的约 5\\% 升到 1991 年的接近 40\\%", k50, k5, k91, k40)
    _, _, t27, t75, t20 = F["y4_tw_invest"]
    said("台湾在 1975 年最高，约 27\\%，此后在 20\\% 上下", t75, t27, t20)
    has("y4_hours", "proportional to total hours of work")
    has("y4_weighting", "weighting labour input by sex, age and educational characteristics")
    has("y4_translog", "aggregate capital and labour input", "weighting the growth of each sub-input by its average marginal product")
    assert "raw capital, weighted capital, raw labour, weighted labour" in column("note")["y4_t31"]
    say("资本与劳动都分成几类，每类的增长按它的平均边际产出加权，他的表里叫加权资本与加权劳动")
    has("y4_log", "logarithmic, rather than geometric")
    said("设产出是$Y=A\\,K^{\\alpha}(hL)^{1-\\alpha}$", 1)                      # the exponent of the model
    said("$1-\\alpha$是劳动的份额", 1)
    # ex:eastasia-young
    hk, sg = F["y4_t31"], F["y4_t41"]
    assert column("note")["y4_t31"].startswith("Table 3-1") and column("note")["y4_t41"].startswith("Table 4-1")
    said("用 Young 表 3-1 与表 4-1 的数", 3, 1, 4, 1)
    _, a, b = F["y4_hk"]
    has("y4_t31", "66-91 0.073")
    said("香港 1966—1991 年产出每年增长 0.073，加权资本 0.080，加权劳动 0.032，劳动份额 0.628", a, b, hk[0], hk[1], hk[2], hk[4])
    has("y4_t41", "66-90 0.085")
    said("新加坡 1966—1990 年依次是 0.085、0.115、0.057 与 0.470", 1966, 1990, sg[0], sg[1], sg[2], sg[4])
    r_hk = residual(hk[0], 1 - hk[4], hk[1], hk[2])
    r_sg = residual(sg[0], 1 - sg[4], sg[1], sg[2])
    said("（1）香港$0.073-0.372\\times0.080-0.628\\times0.032\\approx0.023$", hk[0], 1 - hk[4], hk[1], hk[4], hk[2], r_hk)
    said("新加坡$0.085-0.530\\times0.115-0.470\\times0.057\\approx-0.003$", sg[0], 1 - sg[4], sg[1], sg[4], sg[2], -r_sg)
    said("与 Young 的 2.3\\% 和$-0.3\\%$相同", 100 * hk[3], -100 * sg[3])
    r2 = residual(sg[0], 1 - hk[4], sg[1], sg[2])
    said("（2）$0.085-0.372\\times0.115-0.628\\times0.057\\approx0.006$，余量升到约 0.6\\%（本书的计算）", sg[0], 1 - hk[4],
         sg[1], hk[4], sg[2], r2, 100 * r2)
    v, a, b = F["y2_fn79"]
    said("Young 自己也试过用香港的劳动份额重算新加坡 1974—1989 年的逐年数，平均余量升到 0", a, b, v)
    tfp, n = F["y4_sg_text"]
    said("Young 说，新加坡 24 年里平均每年$-0.3\\%$的余量，是几乎前所未有的生产率倒退", n, -tfp)
    said("他在 1992 年就比较过两座城市", F["y2_volume"][0])
    has("y2_t5_hk", "71-90 ")
    has("y2_t5_sg", "70-90 ")
    said("按他的表 5，1971—1990 年香港产出增长的 35\\% 来自全要素生产率", 5, 1971, 1990, 100 * F["y2_t5_hk"][6])
    assert column("note")["y2_t5_hk"].startswith("Table 5")
    said("1970—1990 年，新加坡的这个比例是$-8\\%$", 1970, 1990, -100 * F["y2_t5_sg"][6])
    assert F["y2_m8"][0] == 100 * F["y2_t5_sg"][6]
    said("在新加坡，资本积累解释了每个工人产出增长的 117\\%", F["y2_117"][0])
    # the compare box of the two cities
    said("\\cmprow{1960 年的起点}", F["y2_barro_start"][2])
    said("约为香港的 108\\%（Barro 的评论）", F["y2_barro_start"][0])
    said("\\cmprow{投资占 GDP}{在 20\\% 上下", F["y2_hk20"][0])
    i60, y60, i84, y84 = F["y2_invest"]
    said("{从 1960 年的 9\\% 升到 1984 年的 43\\%", y60, i60, y84, i84)
    said("{1971—1990 年产出增长的 35\\%", 1971, 1990, 100 * F["y2_t5_hk"][6])
    said("{1970—1990 年为$-8\\%$", 1970, 1990, -F["y2_m8"][0])
    said("{一直在 20\\% 以上", F["y2_hk_return"][0])
    has("y2_t8_6970", "1969-70 0.401")
    said("{1969—1970 年约 40\\%，1980 年代后期的景气年份略高于 10\\%", 1969, 1970, 100 * F["y2_t8_6970"][0],
         F["y2_return"][0], F["y2_return"][1])
    # Krugman
    said("Krugman 1992 年是 Young 那篇比较两座城市的论文的评论人", F["y2_volume"][0])
    has("y2_kr_barking", "barking up the wrong tree")
    has("y2_kr_startling", "Singapore showed no technical progress at all")
    said("用的还是 35 年前的增长核算", F["y2_kr_35"][0])
    said("Krugman 1994 年的文章以“一则警世寓言”开头", F["kg_source"][0])
    has("kg_predicted", "it was predicted on the basis of growth accounting")
    has("kg_naive", "naive extrapolation of past trends")
    a, b, g, x3, gpc = F["kg_singapore"]
    said("按他的数，1966—1990 年新加坡经济每年增长 8.5\\%，人均收入每年增长 6.6\\%", a, b, g, gpc)
    said("就业人口的比例从 27\\% 升到 51\\%", *F["kg_employed"])
    has("kg_japan", "high rates of input growth and through high rates of efficiency growth")
    # ex:eastasia-krugman
    k0, y0, r0 = F["kg_fn3_start"]
    s0 = F["kg_fn3_invest"][0]
    said("劳动力不变，每个工人起初有 10,000 美元的设备，每人生产 10,000 美元的产品，资本的回报率是 40\\%，产出的 20\\% 用于投资",
         k0, y0, r0, s0)
    y14 = F["kg_fn3_14"][0]
    r30, add30, g30, r25, g25 = F["kg_fn3_later"]
    said("（2）每人的资本翻一番以后，产出升到 14,000 美元，回报率降到 30\\% 或 25\\%", y14, r30, r25)
    inv, add, g1 = krugman(r0 / 100, s0 / 100, y0)
    assert add == F["kg_fn3_8"][0] and 100 * g1 == F["kg_fn3_8"][1]
    said("（1）投资$0.2\\times10{,}000=2{,}000$，产出增加$0.4\\times2{,}000=800$，增长 8\\%", s0 / 100, y0, inv, r0 / 100,
         inv, add, 100 * g1)
    inv2, add2, g2 = krugman(r30 / 100, s0 / 100, y14)
    _, add3, g3 = krugman(r25 / 100, s0 / 100, y14)
    assert (add2, round(100 * g2), round(100 * g3)) == (add30, g30, g25)
    said("（2）投资$0.2\\times14{,}000=2{,}800$，回报率 30\\% 时产出增加 840，增长 6\\%；25\\% 时增加 700，增长 5\\%",
         s0 / 100, y14, inv2, r30, add2, 100 * g2, r25, add3, 100 * g3)
    need = g1 * y14
    said("（3）要增加$0.08\\times14{,}000=1{,}120$，回报率须是$1{,}120/2{,}800=40\\%$", g1, y14, need, need, inv2, 100 * need / inv2)
    has("kg_deferred", "deferred gratification")
    has("kg_outpace", "outpace growth in the West for the next decade and beyond")
    # the dual
    has("hs_exceed", "by 1 percent a year for Taiwan and by more than 2 percent for Singapore")
    said("台湾的对偶估计每年高出 1 个百分点，新加坡高出 2 个多百分点", *F["hs_exceed"])
    has("hs_journal", "American Economic Review", "vol. 92(3)")
    said("Hsieh（2002）用的正是这个办法", 2002)
    say("他在摘要里说，韩国与香港的对偶估计与原始估计相近")
    assert Y["hs_dual"] == 2002
    said("Young 1992 年按自己的资本存量推算的回报却在下降", F["y2_volume"][0])
    has("y2_t8_8889", "1988-89 0.128")
    said("新加坡的回报 1969—1970 年约为 40\\%，1988—1989 年约为 13\\%", 1969, 1970, 100 * F["y2_t8_6970"][0], 1988, 1989,
         100 * F["y2_t8_8889"][0])
    sK, gr, gw = DUAL_EX
    said("（1）教学输入：资本份额 0.5，资本的实际回报每年下降 1\\%，实际工资每年上升 4\\%", sK, -100 * gr, 100 * gw)
    hi, lo = F["y2_t8_6970"][0], F["y2_t8_8889"][0]
    years_ = (1988 + 1989) / 2 - (1969 + 1970) / 2
    share = F["cb_young"][2]
    assert column("note")["y2_t8_6970"].startswith("Table 8") and column("note")["y2_t8_8889"].startswith("Table 8")
    assert abs(share - (1 - F["y4_t41"][4])) < 1e-9                       # Young (1994)'s Table 4-1 gives the same
    said("（2）按 Young 1992 年的表 8，新加坡的回报 19 年里从 0.401 降到 0.128，资本份额取 0.53", F["y2_volume"][0], 8,
         years_, hi, lo, share)
    d1 = dual(sK, gr, gw)
    said("（1）$0.5\\times(-1\\%)+0.5\\times4\\%=1.5\\%$", sK, 1, 1 - sK, 100 * gw, 100 * d1)
    gret = math.log(lo / hi) / years_
    said("（2）回报每年下降$\\ln(0.128/0.401)/19\\approx-6.0\\%$，乘以 0.53，余量被拉低约 3.2 个百分点（本书的计算）", lo, hi,
         years_, -100 * gret, share, -100 * share * gret)
    said("（3）高出的正是这 3.2 个百分点。Hsieh 摘要里说的是高出 2 个多百分点", -100 * share * gret, F["hs_exceed"][1])
    # the pitfall box
    said("四个经济体的人均产出每年增长 6\\%—7\\%", *F["y4_67"])
    said("他用水泥进口推算出 1950 年代极高的建筑投资", F["y4_overestimates"][0])
    has("y2_kr_fickle", "notoriously fickle")
    e, a10, n10, _, _, a30, n30 = F["cb_rd_elastic"]
    # Rodrik's own words (p. 193): the Cobb-Douglas share imposes an elasticity of one; below one, capital deepening
    # lowers capital's share and raises the residual
    has("cb_rd_unity", "imposes an elasticity of substitution", "of unity")
    has("cb_rd_fall", "factor share of capital to fall over time")
    has("cb_rd_residual", "would increase correspondingly")
    said("Rodrik 说，Collins 与 Bosworth 用资本份额固定为 0.35 的生产函数，等于假定资本与劳动的替代弹性是 1",
         F[CB_SHARE_ROW][0], 1)
    said("他说，弹性若小于 1，资本越积越多，它的份额会随时间下降，归给生产率的余量就相应升高", 1)
    # with sigma = 1 his Table B1 is Collins and Bosworth's own estimate, 'slightly over 1 percent' (their Table 7: 1.1)
    one, y0, y1 = F["cb_rd_onepct"]
    assert (one, y0, y1) == (1, 1960, 94) and one < F["cb_t7_ea"][5] < one + 0.5
    has("cb_rd_onepct", "slightly over 1 percent")
    said("按他的算例，弹性是 1 时东亚的余量每年略高于 1\\%，是 0.5 时 10 年后是 1.93\\%，30 年后是 2.89\\%", 1, one, e, n10,
         a10, n30, a30)
    assert a10 > F["cb_t7_ea"][5] and a30 > a10
    has("cb_rd_elastic", "would rise to 1.93 percent in ten years")
    has("cb_bosworth", "depends on the stability of capital's share, not on the elasticity of substitution")


def data_check(F, Y, Q):
    said("\\tabref{tab:eastasia-accounting}用 Penn World Table 10.01 重算", 10.01)
    has("y4_t81_note", "excluding agriculture")
    said("增长核算：Penn World Table 10.01 的重算与 Young（1994）（每年 \\%，对数增长率）", 10.01, F["y4_date"][0])
    young = dict(zip(("HKG", "SGP", "KOR", "TWN"), F["y4_t81"]))
    young["JPN"] = F["y4_t82_japan"][2]
    assert tuple(F["y4_t82_japan"][:2]) == (1952, 1973)
    for code, a, b in PERIODS:
        A = accounting(code, a, b)
        cells = [A["gY"], A["alpha"], A["cap"], A["lab"], A["gA"]]
        row = f"{NAMES_ZH[code]} {a}—{b} & " + " & ".join(
            f"{v:.2f}" if i == 1 else f"{v:.1f}" for i, v in enumerate(cells))
        if code in young:
            y = young[code]
            row += f" & {y:.1f}" if y >= 0 else f" & $-{-y:.1f}$"
            said(row, a, b, *cells, abs(y))
        else:
            said(row + " & — \\\\", a, b, *cells)
        assert abs(A["cap"] + A["lab"] + A["gA"] - A["gY"]) < 1e-9
    assert [c for c, _, _ in PERIODS] == ["HKG", "SGP", "KOR", "TWN", "JPN", "USA"]
    assert Q["y4_t81"].startswith("Economy:") and "Hong Kong (1966-1991)" in column("note")["y4_t81"]
    has("y4_t82_japan", "Japan 1952-1973 4.1")
    assert "Christensen, Cummings and Jorgenson (1980)" in column("note")["y4_t82_japan"]
    said("Penn World Table 10.01（Feenstra、Inklaar 与 Timmer 2015，CC BY 4.0）的 rgdpna、rnna、emp、hc 与 labsh", 10.01, 2015, 4.0)
    said("资本份额取 1 减各年劳动份额的平均", 1)
    said("劳动与人力资本一栏是$(1-\\alpha)(g_L+g_h)$", 1)
    said("Young 的余量见他的表 8-1，韩国与台湾不含农业；日本一行是他表 8-2 转引 Christensen、Cummings 与 Jorgenson（1980）的 1952—1973 年",
         8, 1, 8, 2, 1980, 1952, 1973)
    A = {c: accounting(c, a, b) for c, a, b in PERIODS}
    tfp = {c: A[c]["gA"] for c in young}
    assert min(tfp, key=tfp.get) == min(young, key=young.get) == "SGP"
    assert max(tfp, key=tfp.get) == max(young, key=young.get) == "JPN"                # 新加坡都最低，日本都最高
    say("两头还在，中间变了。")
    mid = ("HKG", "TWN", "KOR")
    assert sorted(mid, key=lambda c: -young[c]) == ["HKG", "TWN", "KOR"]
    assert sorted(mid, key=lambda c: -tfp[c]) == ["TWN", "KOR", "HKG"]
    say("中间的三个，Young 依次是香港、台湾、韩国，Penn World Table 是台湾、韩国、香港（本书的计算）")
    said("Penn World Table 的新加坡是每年 0.7\\%，Young 是$-0.3\\%$（本书的计算）", tfp["SGP"], -young["SGP"])
    kr, tw, sg, hk = F["cb_young"]
    assert "Young (1995)" in column("note")["cb_young"]
    said("Young 1995 年的论文给新加坡的资本份额是 0.53，香港是 0.37", 1995, sg, hk)
    lab = pwt()["TWN"]["labsh"]
    run = lab.loc[1951:2000]
    assert run.nunique() == 1 and lab.loc[2001] != run.iloc[0] and pd.isna(lab.loc[1950])
    said("Penn World Table 的香港是 0.53，台湾的劳动份额 1951—2000 年每年都是同一个数（本书的计算）", A["HKG"]["alpha"], 1951, 2000)
    # Hong Kong: capital grows faster than labour and human capital, so a larger capital share lowers the residual,
    # and Young's share closes most of the gap
    H = A["HKG"]
    assert H["gK"] > H["gL"] + H["gh"]
    say("香港的资本比劳动与人力资本增长得快，资本的份额越大，余量就越小")
    H37 = accounting("HKG", 1966, 1991, alpha=hk)
    assert H["gA"] < H37["gA"] < young["HKG"] and young["HKG"] - H37["gA"] < 0.5 * (young["HKG"] - H["gA"])
    say("香港的差距多半出在资本份额上")
    said("改用 0.37，Penn World Table 的香港余量升到约 2.1\\%（本书的计算）", hk, H37["gA"])
    # Singapore: PWT's capital share is above Young's, which by itself would lower PWT's residual, not raise it
    S = A["SGP"]
    y_sg = F["y4_t41"]
    assert abs(1 - y_sg[4] - sg) < 1e-9 and S["alpha"] > sg
    assert residual(y_sg[0], S["alpha"], y_sg[1], y_sg[2]) < y_sg[3]                 # Young's inputs, PWT's share
    assert accounting("SGP", 1966, 1990, alpha=sg)["gA"] > S["gA"]                    # PWT's inputs, Young's share
    said("Penn World Table 给它的资本份额是 0.58，比 Young 的还高，只看份额，余量应当更低（本书的计算）", S["alpha"])
    assert S["gK"] < 100 * y_sg[1]
    said("例如 Penn World Table 的资本每年增长约 10.1\\%，Young 的加权资本是 11.5\\%（本书的计算）", S["gK"], 100 * y_sg[1])
    has("y4_hkhours", "with the exception of Hong Kong (where they fell)")
    P = pwt()
    h0, h1 = P["HKG"].loc[1966, "avh"], P["HKG"].loc[1991, "avh"]
    assert P["SGP"].loc[1990, "avh"] > P["SGP"].loc[1966, "avh"]                     # 新加坡略有增加
    said("同一时期香港每个就业者一年的工作小时从约 2,600 减到约 2,300", h0, h1, slack=50)
    Ah = {c: accounting(c, a, b, hours=True) for c, a, b in PERIODS}
    said("把就业人数换成总工时，香港的余量升到约 1.9\\%，新加坡仍约 0.7\\%，排序不变（本书的计算）", Ah["HKG"]["gA"], Ah["SGP"]["gA"])
    assert min(Ah, key=lambda c: Ah[c]["gA"] if c != "USA" else 9) == "SGP"
    assert max(Ah, key=lambda c: Ah[c]["gA"]) == "JPN" and Ah["HKG"]["gA"] > A["HKG"]["gA"]
    said("日本 1952—1973 年的余量每年 3.4\\%，是表里最高的，Young 转引的 Christensen 等人的估计是 4.1\\%", 1952, 1973,
         A["JPN"]["gA"], young["JPN"])
    said("美国 1966—1990 年的余量每年只有 0.4\\%（本书的计算）", 1966, 1990, A["USA"]["gA"])
    J = accounting("JPN", *JP)
    said("换成 1955—1973 年，日本的产出每年增长约 8.8\\%（本书的计算）", *JP, J["gY"])
    said("资本贡献约 3.8 个百分点，余量约 3.6 个百分点", J["cap"], J["gA"])
    assert abs(told("余量约 3.6 个百分点，约占四成", "约占", "") - J["gA"] / J["gY"]) < 0.05
    a, b = (int(x) for x in re.search(r"(\d{4})-(\d{4})", column("note")["y4_anglo"]).groups())
    said("Young 说 1981—1986 年中英谈判香港前途", a, b)
    said("台湾与韩国每个工人的产出增长每年分别低 0.6 与 0.7 个百分点", *F["y4_agri"])
    has("y4_armies", "exclude their large (predominantly conscript) armies")
    share = F[CB_SHARE_ROW][0]
    said("他们给所有国家用统一的资本份额 0.35，算 1960—1994 年每个工人的产出", share, 1960, 1900 + F["cb_t6_kr"][1])
    CB = cb_tfp()
    assert CB["KOR"] == CB["SGP"]
    said("韩国与新加坡的余量都是每年 1.5\\%，台湾是 2.0\\%", CB["KOR"], CB["TWN"])
    said("东亚（不含中国与日本）的余量每年 1.1\\%", F["cb_t7_ea"][5])
    assert "excludes China and Japan" in column("note")["cb_t7_ea"]
    assert told("只占每个工人产出增长的四分之一", "增长的") == F["cb_fourth"][0]
    S35 = accounting("SGP", 1960, 1994, share)
    said("用同样的 0.35，Penn World Table 给新加坡 1960—1994 年的余量是 1.8\\%（本书的计算）", share, 1960, 1994, S35["gA"])
    said("用数据库自己的份额，余量只有 0.9\\%（本书的计算）", accounting("SGP", 1960, 1994)["gA"])
    assert abs(S35["gA"] - CB["SGP"]) < abs(accounting("SGP", 1960, 1994)["gA"] - CB["SGP"])
    say("在新加坡上，Penn World Table 与 Collins 和 Bosworth 的分歧，多半出在资本份额上（本书的解读）")
    said("(a) Penn World Table 10.01 的分解（本书的计算）", 10.01)
    said("(b) 余量的几种估计：Young（1994）的表 8-1 与表 8-2", F["y4_date"][0], 8, 1, 8, 2)
    said("Collins 与 Bosworth（1996）表 6 的 1960—1994 年（统一资本份额 0.35），以及 Penn World Table 1960—1994 年按 0.35 的重算",
         F["cb_journal"][1], 6, 1960, 1994, share, 1960, 1994, share)
    said("数据：Penn World Table 10.01（Feenstra、Inklaar 与 Timmer 2015，CC BY 4.0），Young（1994），Collins 与 Bosworth（1996）",
         10.01, 2015, 4.0, F["y4_date"][0], F["cb_journal"][1])
    said("新加坡每年落后国际最佳实践 3.5\\%", F["wb_ch1_singapore"][1])
    has("wb_ch1_singapore", "3.5 percent (Singapore)")
    has("wb_invdriven", "The investment-driven economiesIndonesia, Malaysia, and Singapore")
    has("wb_proddriven", "Japan, Korea, Hong Kong, Tliailand, and Taiwan, China")
    has("wb_ch1_dominant", "But it is nor the dom-inantfactor.")
    # Singapore is behind in every set (in Collins and Bosworth it ties with Korea); the rest of the order differs
    assert CB["SGP"] == min(CB.values())
    say("几套估计都把新加坡放在后面，其余的次序与水平取决于份额与投入的量法")


def debate(F, Y, Q):
    has("y4_nothigh", "not particularly high")
    has("kg_allgrowth", "all of Singapore's growth can be explained by increases in measured inputs")
    has("hs_reason", "the return to capital has remained constant")
    said("Krugman 1992 年说新加坡的增长也许比数字显示的快", F["y2_volume"][0])
    has("y2_kr_faster", "Singapore grew more rapidly than the numbers suggest")
    has("y2_kr_face", "I have no reason to believe that they are far off base")
    said("他 1994 年也承认日本靠了效率", F["kg_source"][0])
    hk, sg = F["y2_barro_tfp"]
    assert "1966-1971 for Hong Kong and 1966-1970 for Singapore" in column("note")["y2_barro_tfp"]
    said("投资率相近的 1966—1970 年前后，新加坡的余量每年 2.9\\%，高过香港的 2.1\\%", 1966, 1970, sg, hk)
    has("y2_barro_dr", "say more about diminishing returns to capital than they do about technical change")
    said("\\cmprow{代表}{Young（1992、1994），Krugman（1994）}{世界银行研究组（1993），Hsieh（2002）}", F["y2_volume"][0],
         F["y4_date"][0], F["kg_source"][0], F["wb_copyright"][0], Y["hs_dual"])
    tfp, n = F["y4_sg_text"]
    said("\\cmprow{新加坡}{24 年里每年$-0.3\\%$", n, -tfp)
    said("对偶估计高出原始估计 2 个多百分点", F["hs_exceed"][1])
    has("cb_similar", "very similarto those of Young")
    has("cb_lesson", "paid for in large part through forgone current consumption")
    has("cb_krugman", "Krugmanis certainlyrightto say")
    has("cb_room", "room for high growth to continue in East Asia")
    has("cb_rd_miracle", "a miracle of accumulation(of physical capital, in particular)ratherthan of productivity")
    has("cb_rd_indirect", "the evidence on TFP is indirectand has to be intrepretedwith care")
    # industrial policy
    has("wn_interventions", "suppressing interest rates or promoting favored industries -- as always harmful to growth")
    has("wn_boosted", "boosted growth by intervening in the economy where markets were weak")
    has("wn_vested", "vested interests will shape policies to their own advantage")
    for rid in ("wb_neoclassical", "wb_marketfail", "wb_selective", "wb_failure", "wb_promotion", "wb_promoted"):
        assert words_of(rid), rid
    has("wb_contests", "creatingconteststhat combinecompetitionwiththe benefitsof cooperation")
    has("wb_contest_key", "the governmentdistributes rewards-oftenaccessto caedit or foreignexchange-on the basisof performance")
    has("wb_councils", "accessto rationed credit for exporters", "deliberationcouncilsofJapanand Korea")
    has("y2_victim", "Singapore is a victim of its own targeting policies")
    has("y2_kr_couldbe", "This could be right, but there is no")
    has("y2_kr_noevidence", "positive evidence for it in this paper")
    a, b, c = F["wb_revisionists"]
    said("修正派以 Amsden（1989）与 Wade（1989、1990）等人为代表", a, b, c)
    has("kg_noefficiency", "there is no sign of such exceptional efficiency growth")
    has("cb_rd_hkonly", "Hong Kong")
    # exports
    y50, k, n30 = F["wb_korea_exp"]
    has("wb_korea_exp", "four times as fist as world trade")                       # the rate, not the amount
    said("1950 年代连对贸易乐观的人都没有料到，此后三十年韩国出口的增长速度会是世界贸易的四倍", y50)
    assert told("此后三十年韩国出口的增长速度会是世界贸易的四倍", "此后", "年") == n30
    assert told("会是世界贸易的四倍", "贸易的", "倍") == k
    assert there("ch41_development", "是外向带来了更好的表现，还是更好的表现为外向铺了路\\cite{wdr1987}") == []
    said("世界银行 1987 年自己也说不清是外向带来了更好的表现", 1987)
    said("Rodrik 在 1994 年的工作论文里说", F["rd_number"][1])
    said("1960 年代出口相对盈利能力的提高太小", F["rd_profit"][0])
    has("rd_engineer", "engineer a significant increase in the private return to capital")
    has("wb_park_educ", "Park Chung Hee's export-promotion drive boosted demand for educated labor")
    assert there("ch21_divergence", "1798 年，马尔萨斯（Thomas Robert Malthus，1766—1834）") == [1798, 1766, 1834]
    said("马尔萨斯 1798 年设想，中国可以靠劳动者之多、劳动之便宜", 1798)
    assert "中国靠劳动者之多、劳动之便宜，可以制造数量极大的制成品向外国出售" in chapter("ch21_divergence")
    # financial repression
    has("wb_mildrep", "Japan, Korea")
    has("wb_evident", "highly negativeto positive real rates of interest")
    neg, y49, r53, y53, a, b, three = F["wb_tw_rates"]
    said("1949 年，台湾存款的实际利率是$-300\\%$", y49, neg)
    said("到 1953 年，它提高到约 8.5\\%，三年里定期与储蓄存款占货币存量的比例从 2\\% 升到 34\\%", y53, r53, a, b)
    assert told("三年里定期与储蓄存款", "", "年里") == three
    has("wb_responsive", "minimalimpact on savings")
    has("wb_notinhibit", "appaently")
    assert "mild repression of interest rates at positive real levels" in column("note")["wb_notinhibit"]
    say("他们无法断定把利率温和地压在正的实际水平上促进了东北亚的增长，只能说这看来没有妨碍增长")
    assert there("ch61_emcrises", "亚洲（1997）") == [1997]
    said("1997 年的亚洲危机在\\chref{ch:emcrises}", 1997)
    # each debate ends open (counts() checks the four sub-sections)


def deeper(F, Y, Q):
    imgs = {r.id: r.juan for r in _rows().itertuples() if r.file == "wb1993_42img"}
    pages = sorted({page(rid) for rid, j in imgs.items() if re.match(r"p\. \d+", j)})
    assert pages == [1, 152, 154, 308], pages
    assert {rid for rid, j in imgs.items() if j.startswith("copyright page")} == {"wb_copyright", "wb_rights", "wb_printing",
                                                                                   "wb_series"}
    assert imgs["wb_august"].startswith("p. vii")
    said("书名页背面、第 vii 页前言的署名、第 1 页关于中国的脚注、第 308 页关于通商产业省与有效保护率的一段，以及第 152、154 页的年表，按页面图像读",
         1, 308, 152, 154)
    has("wb_board", "do not necessarilyreflectthe view of its Board of Directors or the governmentsthey rcprescnt")
    has("y4_number", "Working Paper No. 4680")
    said("Young（1994）用的是 NBER 第 4680 号工作论文（1994 年 3 月），Collins 与 Bosworth 引的 Young（1995）没有读到",
         F["y4_date"][0], int(Q["y4_number"].split()[-1]), F["y4_date"][0], mon("y4_date", "March"), 1995)
    y2v = F["y2_volume"][0]
    has("y2_volume", "NBER Macroeconomics Annual 1992, Volume 7")
    said("Young（1992）据 NBER 网站上《NBER 宏观经济学年刊 1992》的章节本", y2v, y2v)
    rn, ry = F["rd_number"]
    has("rd_number", "December 1994")
    rd_pages = sorted({pdfpage(r.id) for r in _rows().itertuples() if r.file == "rodrik1994_42img"})
    assert rd_pages == [1, 2, 3], rd_pages
    said("Rodrik（1994）用的是 NBER 第 4964 号工作论文（1994 年 12 月），它的文字层无法使用，第 1—3 页按页面图像读", ry, rn, ry,
         mon("rd_number", "December"), rd_pages[0], rd_pages[-1])
    said("Collins 与 Bosworth（1996）据 Brookings 网站上的 PDF", F["cb_journal"][1])
    said("Krugman（1994）据网上两份由 JSTOR 下载的副本核对，只用来核对", F["kg_source"][0])
    assert sorted(k for k in meta()["sources"] if k.startswith("krugman")) == ["krugman1994_42", "krugmanh42"]
    said("Hsieh（2002）只读到 IDEAS 上的摘要", Y["hs_dual"])
    johnson = int(re.search(r"\(Johnson (\d{4}), p\. \d+\)", Q["wb_johnson"]).group(1))
    a, b, c = F["wb_revisionists"]
    said("Johnson（1982）、Amsden（1989）与 Wade（1990）的书没有读到", johnson, a, c)
    said("Kim 与 Lau（1994）、Westphal（1990）与 Nelson 与 Pack 的论文没有取得", 1994, 1990)
    said("正文只用 1961 年白皮书的说法", showa(F["wp61_title"][0]))
    said("朴正熙 1961 年夺取政权的月份", F["wb_park"][0])
    t61 = F["y4_t61"]
    has("y4_t61", "66-90 0.096")
    said("Young 的表 6-1 给台湾 1966—1990 年的余量是 0.024，正文也说 2.4\\%，汇总的表 8-1 却是 1.9", 6, 1, 1966, 1990, t61[3],
         F["y4_tw_text"][0], 8, 1, F["y4_t81"][3])
    a, b = F["wb_6090"]
    said("第 1 章又说高绩效经济体产出增长的 60\\% 到 90\\% 来自积累", 1, a, b)
    assert "chapter 1" in column("note")["wb_ch1_dominant"] or page("wb_6090") > 30
    said("新加坡的年表把人民行动党的自治、独立与 1968 年的大选写在各年份的下面", F["wb_tl_sg"][2])
    P = pwt()
    for code, a, b in (("JPN", 1950, 1980), ("KOR", 1953, 1970), ("HKG", 1960, 1980), ("SGP", 1960, 1980)):
        lab = P[code]["labsh"]
        assert lab.loc[a:b].nunique() == 1 and lab.loc[b + 1] != lab.loc[b], code
        assert lab.loc[:a - 1].isna().all(), code
    said("日本 1950—1980 年、韩国 1953—1970 年、香港与新加坡 1960—1980 年都是这样（本书的计算）",
         1950, 1980, 1953, 1970, 1960, 1980)
    assert "number out of 1" in meta_cpf()["notes"]
    said("中央公积金局的数据集说百分比按 1 为满分写", 1)
    chiu = int(re.search(r"\(Chiu (\d{4})\)", Q["wb_tw_rates"]).group(1))
    said("韩国政策性贷款的 60\\%、台湾 1949 年与 1953 年的实际利率", F["wb_korea_policy"][2], F["wb_tw_rates"][1],
         F["wb_tw_rates"][3])
    said("后者是报告转引的 Chiu（1992）", chiu)
    said("只见于 Young（1992）", y2v)
    has("wb_signed", "Augur 1993")
    said("世界银行报告的文字层把 August 1993 读作“Augur 1993”", F["wb_august"][0], F["wb_signed"][0])
    assert page("wb_soviet") == 16 and page("wb_hci_shift") == 129
    m_ = re.search(r"Drive(\d+)-(\d+)\.", Q["wb_hci_shift"])
    said("第 16 页的 clearly offset 读作“dearly offset”，第 129 页标题里的年份读作“11973-791”", 16, 129, int(m_.group(1)),
         int(m_.group(2)))
    said("Young（1992）的文字层丢了 mid-1960s 的连字符", y2v, F["y2_mandays"][1])
    has("y2_mandays", "mid1960s")


def legacy(F, Y, Q):
    has("kg_baseline", "it is unclear what year to use as a baseline")
    has("kg_china78", "decisive turn toward the market, say 1978", "dramatic improvement in efficiency")
    has("kg_china64", "before the Cultural Revolution, say 1964", "only modest growth in efficiency")
    said("从 1978 年决定性地转向市场算起，效率无疑大大提高了", F["kg_china78"][0])
    said("从文化大革命以前的 1964 年算起", F["kg_china64"][0])
    has("kg_double", "one-time changes in behavior that cannot be repeated", "has almost doubled; it cannot double again")
    said("Young 1992 年说，粗略的跨国资本存量估计显示，到 1980 年代中期", F["y2_volume"][0], F["y2_lowest"][0])
    has("y2_lowest", "Crude cross-national estimates of capital stocks", "one of the lowest returns to physical capital in the world")
    has("y2_numbered", "clearly numbered")
    has("wb_integrated", "Since the early 1970s, developing economies have become ever more integrated with the global capital markeL")
    said("研究组 1993 年已经说，1970 年代初以来发展中经济体与全球资本市场越连越紧", F["wb_copyright"][0], F["wb_integrated"][0])
    assert there("ch58_japanbubble", "1980 年代后期的资产泡沫") == [1980]
    said("日本 1980 年代后期的泡沫与 1997 年的亚洲危机", 1980, 1997)
    said("世界银行 1993 年的判断是这场争论的一个起点（本书的解读）", F["wb_copyright"][0])
    has("wb_promotion", "promotion of specific industries had little apparent impact")
    has("wn_exportpush", "those associated with export push hold the most promise")
    say("研究组看不出扶持特定产业的影响，却看好与出口推动相关的干预")


def takeaways(F, Y, Q):
    said("\\item 1956—1973 年日本的实际国内总支出平均每年增长约 9.2\\%", 1956, 1973, 9.2)
    said("按 Young 的统计，1966—1990 年前后，韩国、台湾、香港与新加坡的人均 GDP 每年增长约 6\\%—7\\%", 1966, 1990,
         *F["y4_67"])
    say("付账的是存款利率被压低的储户、拿名义补偿的地主、消费受到限制的家庭、被强制储蓄的雇员和失去谈判权的工人")


def selfcheck(F, Y, Q):
    hk = F["y4_t31"]
    said("按\\exref{ex:eastasia-young}香港的数，劳动份额若是 0.70，余量是多少？", SC_HK_SHARE)
    r1 = residual(hk[0], 1 - SC_HK_SHARE, hk[1], hk[2])
    said("\\item $0.073-0.30\\times0.080-0.70\\times0.032\\approx0.027$，约 2.7\\%", hk[0], 1 - SC_HK_SHARE, hk[1], SC_HK_SHARE,
         hk[2], r1, 100 * r1)
    y14, s0 = F["kg_fn3_14"][0], F["kg_fn3_invest"][0] / 100
    said("产出 14,000 美元时，回报率若降到 20\\%，增长率是多少？", y14, 100 * SC_R)
    inv, add, g = krugman(SC_R, s0, y14)
    said("\\item 投资 2,800，产出增加 560，增长 4\\%", inv, add, 100 * g)
    sK, gr, gw = SC_DUAL
    said("\\item 资本份额 0.4，回报不变，工资每年上升 3\\%，对偶法的余量是多少？", sK, 100 * gw)
    said("\\item $0.4\\times0+0.6\\times3\\%=1.8\\%$", sK, 0, 1 - sK, 100 * gw, 100 * dual(sK, gr, gw))
    R = SC_REP
    said("\\item 存款利率上限 3\\%，通胀率 5\\%，没有上限时存款的实际利率是 1\\%，每 100 单位存款一年里储户少得多少？",
         100 * R["dep_cap"], 100 * R["infl"], 100 * R["dep_free"], R["n"])
    dep = R["dep_cap"] - R["infl"]
    loss = (R["dep_free"] - dep) * R["n"]
    said("\\item 实际利率$3\\%-5\\%=-2\\%$，比 1\\% 少 3 个百分点，即少得 3 单位", 100 * R["dep_cap"], 100 * R["infl"], -100 * dep,
         100 * R["dep_free"], loss, loss)


def ending(F, Y, Q):
    d, y = F["wn_date"]
    said("回到 1993 年 9 月 26 日的那份新闻稿", y, mon("wn_date", "SEPTEMBER"), d)
    has("wb_china", "so different from the those of the HPAEs", "beyond the scope of our study")
    said("他们在第 1 页的脚注里说", page("wb_china"))
    has("wb_failures", "spectacularfailures")
    has("wb_command", "deprivationand massivewaste associatedwith forced savingsin the now-defunctcommand economies")
    assert "强制储蓄与货币过剩等被压抑的通胀" in chapter("ch43_planned")                  # Chapter 43's guide
    assert tex_text().rstrip().endswith("（本书的解读）。" + NEXT)
    assert f"\\guidequestion{{{NEXT}}}" in chapter("ch43_planned")


def figures_data() -> None:
    """What the figures assert of their data, and the quality flags of the observations they draw."""
    L = levels()
    assert L.min().min() > 4 and L.max().max() < 200
    P = pwt()
    for code in CODES:
        x = P[code].dropna(subset=["rgdpe"])
        assert set(x["i_outlier"]) == {"Regular"} and set(x["i_xr"]) == {"Market-based"}, code
    A = {c: accounting(c, a, b) for c, a, b in PERIODS}
    assert all(A[c]["gA"] < 0.5 * A[c]["gY"] for c in A)                                    # panel (a)'s title
    Y4 = {c: v for c, v in young_tfp().items() if v is not None}
    assert min(Y4, key=Y4.get) == "SGP" and min((A[c]["gA"], c) for c in Y4)[1] == "SGP"   # panel (b)'s title
    D = cpf()
    assert D.loc[D.index <= "1990-12", "Employer"].max() == 25
    said("这些观测的价格水平，数据库都标为正常（Regular），汇率都是市场汇率（Market-based）")


# ---------------------------------------------------------------------------------------------------
# 5. The book
# the life dates: words -> (row of the birth year, index), (row of the death year, index), row of the heading, heading
LIVES = {"Lewis T. Preston，1926—1995": (("wp_preston_life", 0), ("wp_preston_life", 1), "loc_preston", "Preston, Lewis T."),
         "Park Chung Hee，1917—1979": (("loc_park", 0), ("loc_park", 1), "loc_park", "Park, Chung Hee"),
         "Lee Kuan Yew，1923—2015": (("loc_lee", 0), ("loc_lee", 1), "loc_lee", "Lee, Kuan Yew"),
         "迫水久常（1902—1977）": (("loc_sakomizu", 0), ("loc_sakomizu", 1), "loc_sakomizu", "Sakomizu, Hisatsune")}
# where two records have a date, they agree: (row, index) pairs
AGREE = [(("wp_preston_life", 1), ("loc_preston_note", 1)), (("wp_preston_life", 1), ("gnd_preston", 0)),
         (("wp_preston_born", 1), ("wp_preston_life", 0)), (("wp_preston_term", 2), ("wb_bangkok", 0)),
         (("gnd_lee", 0), ("loc_lee", 0)), (("gnd_lee_d", 0), ("loc_lee", 1))]
# what other chapters tell: (words of this chapter, chapter where it is told, words there)
EVENTS = [("道奇计划与每美元 360 日元的单一汇率以后，1950 年的朝鲜战争带来了美军的特需", "ch35_reconstruction",
           "1950 年 6 月 25 日，朝鲜战争爆发"),
          ("1956—1973 年，日本的实际国内总支出平均每年增长约 9.2\\%", "ch39_consumption",
           "1956—1973 年，实际国内总支出平均每年增长约 9.2\\%"),
          ("1974 年与 1976 年都到了 23.2\\%", "ch39_consumption", "家庭储蓄率在 1974 年与 1976 年都到了 23.2\\%"),
          ("1960—2019 年人均增长率每年超过 4\\% 的九个经济体里，有台湾、韩国、新加坡与香港（\\chref{ch:solow}）", "ch40_solow",
           "1960—2019 年人均增长率每年超过 4\\% 的有 9 个经济体，即台湾、韩国、博茨瓦纳、新加坡"),
          ("上一章末尾说的最早转向出口的几个经济体，都在这八个里面（\\chref{ch:development}）", "ch41_development",
           "下一章讲的是最早转向出口的那几个经济体"),
          ("有效保护率衡量关税对增加值的保护（\\chref{ch:development}）", "ch41_development", "\\subsubsection{有效保护率}"),
          ("世界银行 1987 年自己也说不清是外向带来了更好的表现，还是更好的表现为外向铺了路", "ch41_development",
           "是外向带来了更好的表现，还是更好的表现为外向铺了路"),
          ("马尔萨斯 1798 年设想，中国可以靠劳动者之多、劳动之便宜，制造数量极大的制成品向外国出售（\\chref{ch:divergence}）",
           "ch21_divergence", "中国靠劳动者之多、劳动之便宜，可以制造数量极大的制成品向外国出售"),
          ("这正是\\chref{ch:solow}的过渡，按式~\\eqref{eq:solow-speed}", "ch40_solow", "\\label{eq:solow-speed}"),
          ("\\chref{ch:solow}的式~\\eqref{eq:solow-accounting}只有资本与劳动", "ch40_solow", "\\label{eq:solow-accounting}"),
          ("日本 1980 年代后期的泡沫与 1997 年的亚洲危机", "ch58_japanbubble", "1980 年代后期的资产泡沫"),
          ("1997 年的亚洲危机", "ch61_emcrises", "亚洲（1997）"),
          ("那一年的石油危机在\\chref{ch:oil}", "ch47_oil", "1973 年与 1979 年的油价冲击"),
          ("日元转向浮动在\\chref{ch:floating}", "ch46_floating", "1973 年主要货币转向浮动"),
          ("中国的信贷与有管理的汇率在\\chref{ch:chinacredit}", "ch72_chinacredit", "中国：信贷、资本管制与有管理的汇率"),
          ("技术进步本身从哪里来，是\\chref{ch:endogenous}的问题", "ch56_endogenous", "技术进步从哪里来？"),
          ("人口老化以后劳动供给怎样变化，在\\chref{ch:demography}", "ch79_demography", "人口老龄化对储蓄、利率与劳动供给的影响"),
          ("关税在今天的效果在\\chref{ch:fragmentation}", "ch78_fragmentation", "关税的价格与汇率效应"),
          ("例如已经消失的指令经济里普遍的匮乏与巨大的浪费", "ch43_planned", "强制储蓄与货币过剩等被压抑的通胀")]
# the chapters this one hands on to, and those it draws on
LATER = {"ch:solow": "ch40_solow", "ch:development": "ch41_development", "ch:reconstruction": "ch35_reconstruction",
         "ch:consumption": "ch39_consumption", "ch:oil": "ch47_oil", "ch:floating": "ch46_floating",
         "ch:divergence": "ch21_divergence", "ch:japanbubble": "ch58_japanbubble", "ch:emcrises": "ch61_emcrises",
         "ch:endogenous": "ch56_endogenous", "ch:demography": "ch79_demography", "ch:chinacredit": "ch72_chinacredit",
         "ch:fragmentation": "ch78_fragmentation"}
# the chapters that point here
POINTERS = ("ch21_divergence", "ch35_reconstruction", "ch39_consumption", "ch40_solow", "ch41_development",
            "ch58_japanbubble")


def book(F, Q):
    """Life dates and what other chapters tell."""
    t = tex_text()
    for words, ((rb, ib), (rd, id_), head_row, head) in LIVES.items():
        assert words in t, words
        assert f"{F[rb][ib]:.0f}—{F[rd][id_]:.0f}" in words, (words, rb, rd)
        assert Q[head_row].startswith(head), (head_row, Q[head_row])             # the person of the record
        COVERED.append(words)
    has("loc_preston_note", "pres. World Bank Sept. 1991-", "d. May 1995")
    has("wp_preston_born", "born on August 5, 1926")
    assert "生卒年未详" in t and "John Page，生卒年未详" in t
    for (r1, i1), (r2, i2) in AGREE:
        assert F[r1][i1] == F[r2][i2], (r1, r2)
    assert 1900 + F["loc_park_note"][2] == F["loc_park"][1]                          # assassinated 10/26/79
    assert "朴正熙（Park Chung Hee，1917—1979）" in t and "李光耀（Lee Kuan Yew，1923—2015）" in t
    assert "普雷斯顿（Lewis T. Preston，1926—1995）" in t
    for here, ch, there_ in EVENTS:
        assert here in t, here
        assert there_ in chapter(ch), (ch, there_)
    named = set(re.findall(r"\\chref\{(ch:[^}]+)\}", t)) | set(re.findall(r"\\nameref\{(ch:[^}]+)\}", t))
    assert named == set(LATER), sorted(named ^ set(LATER))
    for label, ch in LATER.items():
        assert f"\\label{{{label}}}" in (ROOT / "zh" / f"{ch}.tex").read_text(encoding="utf-8"), (label, ch)
    for ch in POINTERS:
        assert re.search(r"\\(?:chref|ref)\{ch:eastasia\}", chapter(ch)), ch
    print(f"ok {len(LIVES)} life dates, {len(EVENTS)} statements of other chapters, {len(LATER)} other chapters named")


# the bibliography item of each source of the snapshot (the authority records: loc42 and gnd42)
ITEM_OF = {"wbnews42": "worldbank1993news", "wb1993_42": "worldbank1993", "wb1993_42img": "worldbank1993",
           "young1994_42": "young1994", "young1992_42": "young1992", "rodrik1994_42img": "rodrik1994",
           "cb1996_42": "collinsbosworth1996", "brookings42": "collinsbosworth1996", "krugman1994_42": "krugman1994",
           "krugmanh42": "krugman1994", "hsieh2002_42": "hsieh2002", "wp1956_42": "epa1956", "wp1956m42": "epa1956",
           "wp1961_42": "epa1961", "wp1961a42": "epa1961", "wp1961b42": "epa1961", "wp1961m42": "epa1961",
           "cao_rules42": "epa1956", "twlaw42": "taiwan1995", "twcopyright42": "taiwan1995",
           "wbpreston42": "worldbankpreston", "sglicence42": "cpf2026"}
REUSED_KEYS = {"pwt1001", "wdr1987"}


def runs(ps) -> str:
    """'第 2、7、8、25、26 页' from page numbers: ranges joined by '—', two neighbours by '、'."""
    out, rs = [], []
    for p in sorted(set(ps)):
        if rs and p == rs[-1][1] + 1:
            rs[-1][1] = p
        else:
            rs.append([p, p])
    for a, b in rs:
        out.append(f"{a}" if a == b else f"{a}{'、' if b == a + 1 else '—'}{b}")
    return "、".join(out)


def printed(srcs) -> str:
    """The printed (Arabic) pages of the rows of these sources (their juan columns begin 'p. N')."""
    return runs(int(m.group(1)) for r in _rows().itertuples() if r.file in srcs
                for m in [re.match(r"pp?\. (\d+)\b", r.juan)] if m)


def pdf(srcs) -> str:
    """The PDF pages of the rows of these sources."""
    return runs(int(p) for r in _rows().itertuples() if r.file in srcs for p in re.findall(r"PDF pp?\. (\d+)", r.juan))


def witnesses(F, Q):
    """Second witnesses of statements of the text, the licences and the bibliography block of the chapter."""
    # Krugman's numbers for Singapore are Young's (footnote 6): one witness, said so in the 史料说明
    has("kg_fn6", "These figures are taken from Young, ibid.")
    has("kh_stalin", "would have done Stalin proud")
    assert words_of("kh_stalin") == words_of("kg_stalin")                     # the second copy of the article
    assert F["wb_signed"] == F["wb_august"] == F["wb_copyright"] == F["wb_printing"]
    assert F["wp_preston_term"][2] == F["wb_bangkok"][0] == F["loc_preston_note"][0]
    # the licences
    m = meta()
    lic = m["license"]
    for rid in ("wb_copyright", "wb_rights", "wb_board", "rd_copyright", "y4_number", "y4_date", "y2_selection",
                "cb_journal", "br_copyright", "br_personal", "kg_jstor", "hs_restricted", "cao_rules", "cao_date",
                "wp56_rights", "tw_ca9", "sl_use", "sl_attribution", "sl_official", "gnd_licence"):
        assert re.search(r"\brows? [^)]*\b" + rid + r"\b", lic), rid
    for rid in ("rd_copyright", "br_copyright", "br_personal", "kg_jstor", "hs_restricted", "cao_rules", "wp56_rights"):
        assert words_of(rid) in lic, rid
    data, dm = load_snapshot("pwt1001_eastasia")
    assert "CC BY 4.0" in dm["license"] and "Feenstra" in dm["citation"]
    cm = meta_cpf()
    assert "Singapore Open Data Licence" in cm["license"] and words_of("sl_attribution") in cm["license"]
    # the bibliography block of the chapter
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    start = bib.index("% ---- 第 42 章")
    following = re.search(r"^% ---- 第 \d+ 章", bib[start + 1:], re.MULTILINE)
    end = start + 1 + following.start() if following else bib.index("\\end{thebibliography}")
    block = bib[start:end]
    assert FETCH in block and bib.index("% ---- 第 41 章") < start
    items = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", block)}
    allitems = {m_.group(1): m_.group(2) for m_ in re.finditer(r"\\bibitem\{([^}]+)\}(.*)", bib)}
    assert f"共 {len(items)} 条" in block
    unescape = lambda s: re.sub(r"\\([$%&_#~])", r"\1", s).replace("--", "-")     # noqa: E731 - as LaTeX prints it
    assert words_of("wb_copyright").split(" 1818")[0] in unescape(items["worldbank1993"])
    assert words_of("wb_rights") in unescape(items["worldbank1993"])
    assert words_of("rd_copyright") in unescape(items["rodrik1994"])
    for rid in ("br_copyright", "br_personal"):
        assert words_of(rid) in unescape(items["collinsbosworth1996"]), rid
    assert words_of("kg_jstor") in unescape(items["krugman1994"])
    assert words_of("hs_restricted") in unescape(items["hsieh2002"])
    assert words_of("wp56_rights") in unescape(items["epa1956"]) and words_of("cao_rules") in unescape(items["epa1956"])
    assert "PDL1.0" in items["epa1961"] and words_of("wp61_signed") in unescape(items["epa1961"])
    assert words_of("tw_ca9") in unescape(items["taiwan1995"])
    assert words_of("y2_selection") in unescape(items["young1992"])
    assert "Singapore Open Data Licence version 1.0" in items["cpf2026"]
    assert "公共数据" in items["loc42"] and words_of("gnd_licence") in unescape(items["gnd42"])
    for key in ("krugman1994",):
        assert "只用来核对，不随本书分发" in items[key], key
        for src in ("krugman1994_42", "krugmanh42"):
            assert m["sources"][src]["sha256"] in items[key], src
    for src, key in (("wbnews42", "worldbank1993news"), ("wb1993_42", "worldbank1993"), ("young1994_42", "young1994"),
                     ("young1992_42", "young1992"), ("rodrik1994_42img", "rodrik1994"), ("cb1996_42", "collinsbosworth1996")):
        assert m["sources"][src]["sha256"] in items[key], src
    # the pages of each work, as the snapshot's rows have them
    for key, srcs in (("worldbank1993", ("wb1993_42", "wb1993_42img")), ("young1994", ("young1994_42",)),
                      ("young1992", ("young1992_42",)), ("collinsbosworth1996", ("cb1996_42",))):
        assert f"第 {printed(srcs)} 页" in items[key] or f"第 {printed(srcs)} 页" in items[key].replace("封面、摘要与第 ", "第 ") \
            or printed(srcs) in items[key], (key, printed(srcs))
        assert f"PDF 第 {pdf(srcs)} 页" in items[key], (key, pdf(srcs))
    assert f"第 {printed(('krugman1994_42', 'krugmanh42'))} 页" in items["krugman1994"]
    assert f"PDF 第 {pdf(('rodrik1994_42img',))} 页" in items["rodrik1994"]
    for words, (_, _, head_row, _) in LIVES.items():
        if head_row.startswith("loc_"):
            assert Q[head_row].replace("-", "--") in items["loc42"] or Q[head_row] in items["loc42"], head_row
    for rid in ("gnd_preston", "gnd_lee", "gnd_lee_d"):
        assert Q[rid] in items["gnd42"], rid
    # every source of the snapshot is named by its URL in its item
    for key, s in m["sources"].items():
        item = "loc42" if key.startswith("loc_") else "gnd42" if key.startswith("gnd_") else ITEM_OF[key]
        assert unescape(s["url"]).replace("%7E", "~") in unescape(items[item]).replace("%7E", "~"), key
    keys = set(allitems)
    cited = {k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", tex_text()) for k in c.split(",")}
    assert cited <= keys, sorted(cited - keys)
    assert REUSED_KEYS <= cited and not REUSED_KEYS & set(items)
    assert set(items) == cited - REUSED_KEYS, sorted(set(items) ^ (cited - REUSED_KEYS))
    print(f"ok {len(cited)} works cited, {len(items)} in the bibliography block of Chapter 42, "
          f"{len(REUSED_KEYS)} in earlier blocks")


def counts() -> None:
    """The editor's limits: “不能” at most about a dozen; the forbidden words; who decided and who paid stated; the four
    debates left open; the boxes."""
    t = tex_text()
    main_ = re.sub(r"\\begin\{deeper\}\[史料说明\].*?\\end\{deeper\}", "", t, flags=re.DOTALL)
    n = t.count("不能")
    print(f"ok “不能” {n} times")
    assert n <= 12, n
    for words in ("本书没有找到", "没能取得", "没有取得", "没有读到"):
        assert words not in main_, words                                          # only in the 史料说明
    narrative = re.sub(r"“[^”]*”", "", t)
    for bad in ("这一节回答", "不是因为", "而是", "详见", "\\textsc", "\\underline", "\\clearpage", "值得注意", "如前所述"):
        assert bad not in narrative, bad
    assert not re.search(r"(?<![意看])见\\(?:chref|secref|figref|tabref|exref|eqref)", t)
    for bad in ("中国台湾", "中国香港"):
        assert bad not in t, bad
    # who decided and who paid
    for words in ("\\section{谁决定，谁承担}", "钱怎样分，由政府说了算", "做决定的多是官僚（本书的概括）", "储户拿到的利率被压低了",
                  "台湾的改革是在戒严中进行的", "决定缴费率的是政府", "工人也付了账", "消费者也付了账",
                  "决定投资率与信贷流向的是政府与官僚机构，付账的是存款利率被压低的储户、拿名义补偿的地主、消费受到限制的家庭、被强制储蓄的雇员和失去谈判权的工人（本书的概括）",
                  "这次推动的账，研究组算了两面", "土地改革的账先算在地主身上"):
        assert words in main_, words
    # documents are not the subjects of sentences: the author is named
    for bad in ("报告说", "新闻稿说", "白皮书说", "论文说", "摘要说", "标题说", "前言说", "年表列出", "报告认为"):
        assert bad not in main_, bad
    # at most one source frame (按……的说法、转述……) in a sentence
    frame = re.compile(r"按[^，。；“”]{0,40}?的(?:说法|转述|解释|估计|叙述|描述|判断|概括|统计|数|年表|表 \d)")
    for s in re.split(r"(?<=[。？！])|\n", re.sub(r"“[^”]*”", "“”", main_)):
        assert len(frame.findall(s)) <= 1, s
    # the four debates are left open
    for words in ("第一个争论", "第二个争论", "第三个争论", "第四个争论"):
        assert main_.count(words) == 1, words
    part = main_[main_.index("\\section{四个争论}"):main_.index("\\section{今天还剩什么}")]
    debates = part.split("\\subsubsection{")[1:]
    assert len(debates) == 4
    for d in debates:
        d = re.sub(r"\\begin\{compare\}.*?\\end\{compare\}", "", d, flags=re.DOTALL)
        assert d.rstrip().endswith("至今没有定论。"), d[-80:]
    # the inferences are marked
    assert main_.count("本书的解读") >= 8 and main_.count("本书的计算") >= 10 and "本书的概括" in main_ \
        and "本书的推导" in main_, main_.count("本书的解读")
    # sentences: one semicolon at most
    for s in re.split(r"(?<=[。？！])|\n", re.sub(r"“[^”]*”", "“”", main_)):
        assert s.count("；") <= 1, s
    # the boxes the editor asks for
    assert 2 <= t.count("\\begin{compare}") <= 4 and t.count("\\begin{case}") == 1 and t.count("\\begin{pitfall}") == 1
    assert t.count("\\begin{deeper}[史料说明]") == 1 and 1 <= t.count("\\begin{keyeq}") <= 4
    assert t.count(GUIDE) == 2
    # the neighbours' topics: one clause each
    assert t.count("大跃进") == 0 and t.count("\\chref{ch:japanbubble}") <= 2 and t.count("\\chref{ch:emcrises}") <= 2


def main() -> None:
    df = _rows()
    F, Y, Q = facts(), years(), quotes()
    check_readings(df)
    check_text(df)
    for part in (guide, opening, world, state, accounting_section, data_check, debate, deeper, legacy, takeaways,
                 selfcheck, ending):
        part(F, Y, Q)
    models()
    figures_data()
    book(F, Q)
    witnesses(F, Q)
    counts()
    coverage()
    anchors(str(TEX), set(df["id"]), script=Path(__file__))


if __name__ == "__main__":
    main()
