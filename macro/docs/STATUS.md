# Project status

Updated 2026-10-14.

## Skeleton — committed
- `structure.py`: 11 parts, 5 books (分册), 84 chapters, 4 appendices.
- `zh/`: 84 chapter stubs, each with its title, label and guide box (core question, learning goals, prerequisites); part pages with introductions; preface; title page; Appendix A (planned contents), B (symbol conventions), C (index of comparisons and cases, filled automatically), D (timeline, planned).
- `docs/PLAN.md`: principles, running teaching model and tools, case map, books, and for every chapter its question, goals, candidate sources, cases, comparison candidates and prerequisites; label registry.
- `docs/STYLE.md`: writing, notation, sources, data, methods and figure rules.
- Tools: `build.py` (whole volume or one book), `validate_source.py`, `tools/check_chapter.py`, `figsrc/style.py` and `figsrc/build.py`, `checks/common.py` and `checks/_template.py`, `data/README.md` and `data/SOURCES.md`.
- `python3 build.py --book all` builds the whole volume and the five books with no LaTeX errors, overfull boxes or undefined references; `python3 validate_source.py` passes.
- `references_zh.tex` holds the two verified general histories (De Vroey 2016; Snowdon & Vane 2005) and the sources of Chapter 12. Other candidate works in `PLAN.md` are not yet verified.

## Sample chapter — Chapter 12 (宋元明：世界最早的纸币及其崩溃), written 2026-10-13
- `zh/ch12_songming.tex`: full text (8 sections, 4 worked examples, 4 comparison boxes, 1 case box, 2 tables, 3 figures, takeaways, self-check with answers). An independent reviewer checked every quotation against the corpus and Wikisource and every cited work; the fixes are in (deposit fee rather than redemption fee, the speaker of the 1023 memorial, 省陌 in the 1268 valuation, the 1276 recall of Southern Song notes, the cost of the 张商英 restoration, the 称提 comparison recast as intervention against a peg).
- Open points from the review: the 《宋朝事实》 first-year issue (3,884,600 guan) is three times the 《宋史》 quota and is flagged in the text, not resolved; Guan et al.'s price index (direct evidence that official rates lag the market) is not yet in a snapshot.
- Data: `data/snapshots/yuanshi_suyinchao` (the 《元史》 table of notes printed each year, 1260–1329) and `data/snapshots/paper_money_facts` (quotations with their numbers from the Song, Yuan and Ming histories, each checked verbatim against a pinned digital text by `data/fetch/verify_quotes.py`).
- `checks/check_ch12.py` asserts every number in the text; `figsrc/fig_ch12.py` draws the figures in the style of the electromagnetics notes (STYLE.md §7.1).
- What the sample settled is recorded in `STYLE.md` §11. Approved by the author on 2026-10-13; §11 now binds every chapter.
- Brought in line with the Part 3 chapters on 2026-10-14, at the author's request ("保持12章与其他章节一致"):
  - Cross-references: `\appref` replaces the hand-written "附录 B". The opening now points to every section with `\secref`, as Chapters 11 and 13–17 do (Chapter 10 got the same).
  - Evidence: `paper_money_facts.json` has a `sources` block, so quotations from modern works and from Wikisource are checked verbatim by `verify_web_quotes.py`, as in Part 3.
    - Guan, Palma & Wu (2024): the published PDF (CC BY 4.0, from figshare).
    - Cagan's definition, as quoted by Fischer, Sahay & Végh (2002, NBER).
    - The 1232 variant on Wikisource.
    - von Glahn (1996): two passages read through archive.org's full-text search, which no script checks.
  - Corrections, made because the sources do not support the old wording:
    - The Encyclopaedia Iranica entry by Jackson (1990) answers 403 and could not be checked. The Tabriz case box now rests on d'Ohsson (1835) and Howorth (1888), and the Jackson citation is gone.
    - Its "prices rose more than tenfold" and the derived 216% a month are in neither book and were removed. They are replaced by Wassaf's horse price (7½ gold pieces; 750 asked in paper), presented as one asking price, not a price level.
    - Guan et al. say the 1276 jump came partly from converting huizi (at 50 to 1) and partly from Kublai's spending, not "很大一部分" from converting huizi.
    - Their war finding is restated as they put it: civil war raised over-issue; disasters and grants did not.
  - Still open: Guan et al.'s Table A1 is in the online Supporting Information (Wiley, 403), so the earlier six-year agreement with the 《元史》 table could not be checked again.
  - The English `yuan_issuance` had one label touching another; it is moved down.

## EPUB edition — added 2026-10-13
- `tools/epub/` converts the LaTeX sources to EPUB 3 with pandoc, taking every number from the PDF build (`docs/EPUB.md`). `python3 build.py --book all --epub` writes the volume and the five books; the EPUBs pass epubcheck 5.1 with no errors or warnings. `\tfrac` and `\dfrac` are set as `\frac` in the EPUB, because pandoc writes them as `<mfrac displaystyle=…>`, which epubcheck rejects (found with Chapter 10's partnership example, fixed 2026-10-13).

## Hand-off repaired — 2026-10-13
- `tools/setup_env.sh` now installs what a bare cloud container lacks (TeX Live, Noto CJK, fallback fonts, pandoc, Java) and the STIX Two fonts (stipub/stixfonts v2.13b171), and ends with a font check. The PDFs and EPUBs in `compiled/` were rebuilt with STIX Two Text and Math, the fonts `preamble.tex` intends (the earlier builds had fallen back to TeX Gyre Termes and Latin Modern Math); Chapter 12 checked clean with them (17 pages with its bibliography), all six EPUBs pass epubcheck.
- `tools/probe_network.sh` reports which source hosts the shell can reach; on 2026-10-13 many could be downloaded from directly. Evidence rule 3 of the brief now asks for the original document to be downloaded and every number found in its text, with the file's SHA-256 recorded; WebFetch is the fallback for blocked hosts.
- `docs/FORWARD_REFS.md` records what written chapters expect of unwritten ones (seeded with Chapter 12's references).
- Part 3 is written sequentially (author's choice): one chapter at a time, each reviewed by one independent reviewer before the next (`docs/WORKFLOW.md`).

## Part 3 — written and reviewed; awaiting the author's review (sequential, one reviewer per chapter)
- Chapter 10 (伊斯兰世界与地中海的商业革命): written and reviewed; the review's fixes are in commit "Chapter 10: apply the independent review".
- Chapter 11 (中世纪欧洲：庄园、黑死病与货币贬值): written and reviewed; fixes applied (including example 11.3 now set in the 1350s, labour 0.71, when the statutes were made; the intuition box now matches the one-quality-land model). Open points from the review, not done: the literature that followed Rolnick, Velde & Weber (Velde, Weber & Wright 1999; Sussman 1993; Sargent & Velde 2002) is not cited; Oresme's treatise is dated only by its 1864 editor (before 1373), not by the modern estimate (c. 1355–60), for want of a downloaded modern source; the tension between Oresme's fourth point (metal leaves the kingdom) and the mint inflows of the debasement puzzle is not discussed; the Peasants' Revolt of 1381 is not mentioned; in figure `plague_wages` (a) two labels could sit better and the shaded plague band is faint; the Great Famine of 1315–17 has no citation of its own (only Clark's cost-of-living series).
- Chapter 13 (白银的世纪：波托西、马尼拉与价格革命): written and reviewed; fixes applied in commit "Chapter 13: apply the independent review" (De Comyn's own range of a quarter to a half, example 13.1's two calculations reconciled, example 13.2 read as one range of fine-gold prices, Bodin's "en partie" already in the 1568 edition, Drelichman & Voth's no-haircut counterfactual, example 13.6's fall in the debt ratio attributed to the 1575 revenue jump and the 1577 settlement, the 明史 account of 1603 given in full). Added after the review: Potosí's silver mined by forced labour under the mita (Dell 2010, abstract; details owed by Chapter 14), the Álvarez-Nogal & Chamley (2014) reading of Philip II's debts (abstract only; the full text was not reachable), Malestroit's name (Jehan Cherruyt, known only from a handwritten note; life unknown), the common-gold sentence of the memorial. Open points, not done: Drelichman & Voth's 2015 reply to Álvarez-Nogal & Chamley is not cited (paywalled); the dates 1565 (全汉昇) and 1571 (Drelichman & Voth) for the Philippines stand side by side; 徐石楼 is not identified; the factor of two between Hamilton's 1929 Table A and his 1934 totals is unexplained; the chapter derives the debt dynamics formally, an exception to PLAN §1 that the author confirmed on 2026-10-14 (recorded in PLAN §1 and the Chapter 50 entry, and in FORWARD_REFS).
- Chapter 14 (非洲与美洲：黄金、贝币与没有货币的帝国): written and reviewed; fixes applied in commit "Chapter 14: apply the independent review" (the Takedda copper bars, 400 coarse or 600–700 fine to the ducat, read as two denominations; al-Maqrizi's "six dirhams" is a fall of six, not a fall to six, as Van Steenbergen's 2016 edition of the Arabic shows, so his fall of at most 24% and al-Umari's of at least 12% are compatible; the unpaid 50,000 dinars attributed to Ibn Khaldun, the repayment to al-Umari's informant; the women of the palace short-stringing the cowries at Whydah; Robinson's "Soudan" glossed; the carrying-cost inequality stated as a bound; the Kaffi starting point of the porters' fare; the Adamawa raid's second account of 2,000; the colonial replacement of cowries taking decades). Added after the review: a legacy item on money as commodity or creature of the state (Menger and Knapp in Chapter 23, MMT in Chapter 63, stablecoins in Chapter 77, recorded in FORWARD_REFS). Open points, not done: Schultz (2006) on the Mansa Musa gold story could not be obtained; Hogendorn & Johnson (1986) and Murra are replaced by Gardner (2015) and the primary accounts.
- Chapter 15 (早期金融革命：荷兰、英国与可信的国债): written and reviewed; fixes applied in commit "Chapter 15: apply the independent review" (the opening no longer calls England and Holland the biggest borrowers of 1672; why a rate cut on redeemable debt is not a default; the Tonnage Act's treble penalty falls on the directors who consent; France's 1715 debt, 17 times revenue, from Velde 2003 in the four-country table; Smith's Amsterdam digression confirmed in the first edition). Open points: the fiscal-capacity view (Brewer 1989, O'Brien 1988) and Clark (1996) on private returns are not discussed, because the works were not obtained; Dickson (1967) was not obtained either.
- Chapter 16 (重商主义、约翰·劳与重农学派): written and reviewed; fixes applied in commit "Chapter 16: apply the independent review" (the swap condition written P/(E/N), since e is the exchange rate in Appendix B; example 16.2(3) explains why the market value of the shares, not the debt, sets the cost at 9,413 livres; example 16.4 derives V/Y = P/M; sector accounts described as payments that are other sectors' receipts, with balances summing to zero; Mun's own remark on dear money (p. 24) and Cantillon on specie outflow before Hume; note issues from Velde's Table 4; the South Sea Company's slave-trade Assiento and the triangle trade in the authors' words; the Bank of England's 1720 rescue no longer called a lender of last resort; Mun's identity in EX and IM and government spending G in merc_system, to keep M, X and g for money, output and growth). Added after the review: Dale, Johnson & Tang (2005) against Shea (2007) on whether 1720 investors were irrational, from the two abstracts on the Economic History Society's pages; Smith's "capital error" of the physiocrats in the legacy section. One of my objections to the review was wrong: Cantillon's 1720 interest passages are in Part II, ch. 10 (headed "CHAPITRE DIXIEME", which my search for roman numerals missed), and the rows now say so. Open points: Kindleberger and Murphy (1997) were not obtained; the full texts of the two EHR articles need a login and were not read; the share-price data (fgr2009_1720_shares) may not be circulated, so a fresh checkout must run its fetch script before check_ch16.py.
- Chapter 17 (德川日本与清代中国：东亚的前近代市场): written and reviewed; fixes applied in commit "Chapter 17: apply the independent review". The fixes:
  - The compare box now says dear silver hurts Edo buyers of western goods. The Edo markup is ē/e_W, so the old "比价上升" row had the sign backwards.
  - "盯市" translates Schaede's "ten-day mark-to-market mechanism" (it had been rendered 逐日结算), and the margin is a fraction m, not "m 倍".
  - Example 17.3 is spelled out per 100 ryō: 150 minted, 101 paid out, 49 kept. It also states that the quantity theory fails only if V and Y are fixed.
  - Example 17.4: the Genbun valuation is at the mint's rate (1.65), not the metal ratio (1.744).
  - Schaede is named rather than given a pronoun, since no source states one (林满红 is "她", as in Irigoin and Atwell).
  - For balance:
    - Suzuki's reading of Arai's estimate is flagged as a challenge to the mainstream; the Keichō mintage is unknown because the mint documents burned (fn. 3).
    - Weak-form efficiency is defined, and Schaede's caveat on Miyamoto's annual averages is added (fn. 15).
    - Atwell's critique of Lin is added (pp. 577–578).
    - The copper side of the rate: 《清史稿》 says cash was cast thin from 嘉庆十年 (1805).
    - 包世臣's prices are for 谷 (paddy); 曾国藩 says three dou were 有余 and six 不足.
    - The Edo price is an official price, so the Genroku match should not be weighed too heavily.
  Added after the review:
  - The Tokugawa population was "stable" only after about 1720. The figures are 国土庁 (1974) as charted by MLIT (2011): 1,227万 in 1603, 3,128万 in 1716–45, 3,330万 in 1868. They have their own snapshot rows and bibitem.
  - Snapshot rows back each new paraphrase.
  - Table 17.3 moved to the start of §17.8, so it no longer takes a float page.
  Declined: 吴嘉宾's "一千一百文内外" is his norm for the century since 雍正, not a contradiction of the 1,500 he gives for 1845.
  Open points:
  - The two memorials of 曾国藩 are dated in the text only as after 1846. The reviewer recalls 咸丰元年十二月; Wikisource refused requests (429), so this is not confirmed.
  - The chapter relies on Suzuki (2021), a working paper, for the content theory. A mainstream quantity account (Shinbo, Saitō) was not obtained.
  - Notation clashes within the chapter (resolved 2026-10-14, author's decision): the hedged position is now $H_T$ ($V$ stays velocity, as in Appendix B) and the spot price $p_T$ (the chapter's rice price $p$), so $S$ is only the recoinage gain.
  - The Kobe 近世経済データベース was not used (its terms forbid redistribution); the rice prices are Iwahashi's, through GPIH.
- Pronouns: modern scholars whose pronoun no source states are referred to by name or in neutral wording (自己, 其, 原文, 原注). These are Greif (Ch10), Clark (Ch11), 全汉昇 and Hamilton (Ch13), Kocherlakota and Dalzel's annotator J. F. (Ch14), Velde, Garber and Shea (Ch16), and Suzuki, Irigoin, Takatsuki and Schaede (Ch17). Historical figures keep 他 where their own texts or the sources give it.
- EPUB: pandoc printed Table 17.3 as plain text because its `\multicolumn` spec had `@{}`, so three links had no target. `tools/epub/build_epub.py` now strips `@{}` from `\multicolumn` specs as it does for tabularx. The six EPUBs pass epubcheck with no messages, and none has a table rendered as text.
- Figures:
  - Every in-figure note in Part 3 is at least 7.6 pt in the source (STYLE.md §7.1).
  - The collisions the larger text caused are fixed in both languages, and text no longer sticks out of the canvas.
  - `tools/figlint.py` reports text off the canvas or on other text (WORKFLOW §3).
  - Print size (resolved 2026-10-14, author's decision): `\fig` sets figures at the full text width and FIG_W is 5.90 in, so a figure cropped with its 0.04 in pad is 152 mm wide and prints at 1:1; the height cap is .5\textheight (4.65 in). `figlint.py` now reports the printed scale and any text printing below 7.5 pt; all 31 figures pass in both languages (printed scale 1.00–1.05). Fixed on the way: the Chapter 2 plots had no margins set (they printed 17% enlarged), the Chapter 12 timeline's row labels touched, and some labels in Chapters 11, 14, 16 and 17 stuck out of the narrower canvas or (English) overlapped.

## Part 1 — in progress (sequential, one reviewer per chapter; notes in `docs/agent_prompts/part1_notes.md`)
- Started 2026-10-14 at the author's request ("按顺序继续"): Chapters 2, 3, 4, 5 in that order; Chapter 1 last, after Part 2.
- Chapter 2 (国民核算与恒等式): written and reviewed. Fixes are in the commit "Chapter 2: apply the independent review".
  - Kuznets's own reading of the negative business saving of 1931–32: he calls a draw on capital "misleading" and says the losses mostly covered rigid costs.
  - The real reasons his national income differs from BEA's: taxes on production and imports, imputed rent, and book valuation (both figures are net of depreciation).
  - Example 2.1 deflates income produced by both of Kuznets's price indexes, giving a real decline of 30–41%.
  - The trend-deviation caveat on China's 2004 revision.
  - The strongest case for each causal reading of the sector balances.
  Added after the review:
  - The wartime British origin of the accounts (Keynes, Meade, Stone), from the Royal Swedish Academy's 1984 press release.
  - The 2025 SNA's changes: depletion as a cost, and NDP as the preferred growth measure (pre-edit text).
  - Product taxes in the production line of eq. 2.1.
  - 30 new snapshot rows; 142 quotations verify verbatim.
  Open points:
  - The 1941 white paper of Meade and Stone was not obtained.
  - The two causal readings of the sector balances are not yet tied to their authors (Godley & Lavoie; Barro). Chapters 50 and 63 owe this (FORWARD_REFS).
  - The 2025 SNA is quoted from its pre-edit version.
  - `verify_web_quotes.py` takes a per-source `user_agent` (FRASER refuses the default one).
  - Rebuilt with `python3 build.py --book all --epub` (figures now at 1:1). The six EPUBs pass epubcheck 5.1 with no messages. In the EPUB, Table 2.1 keeps its two-column 企业 header and eq. 2.1 is MathML.
- Chapter 3 (价格、通胀与利率): written and reviewed. Fixes are in the commit "Chapter 3: fixes after the independent review".
  - Example 3.3 (4) follows BEA (McCully et al. 2007) on why CPI and PCE inflation differ: in 2002–07 the formula explains about half and the weights most of the rest (rent of shelter 32% vs 15%), with scope partly offsetting; in 1972–80 two-thirds come from owners' housing (Triplett 1981), and the CPI-U before 1983 was never revised.
  - Real hourly earnings deflated by the CPI-U first exceed their 1972 level again in 2020 (not "never since 1972").
  - The BoJ's 80 trillion yen is the annual increase in its JGB holdings; the TIPS principal has a floor at par (31 CFR 356, App. C).
  - The pitfall box's cumulative bias is over twenty years; the breakeven test has 163 months and few independent decades (overlapping windows).
  Added after the review:
  - The other side of the Boskin estimate: Lebow & Rudd (2001) put the bias at 0.6 pp (0.1–1.2) and report the Commission's members at 0.8 by 1999; BLS's switch to geometric means at the lower level in January 1999 (three-fifths of the weight, about 0.2 pp a year).
  - The two readings of breakeven inflation name their sources: Gürkaynak, Sack & Wright (2008) on time-varying premiums, Campbell, Shiller & Viceira (2009) on the fall of 2008.
  - A note on the chapter's local symbols; the monthly breakeven series keeps complete months only (to 2026-09).
  - `prices_facts` has 119 rows; 105 quotations verify verbatim, 14 are read from page images or carry no quotation.
  Open points:
  - Why the October 2025 CPI is missing (the BLS website returns 403); annual comparisons stop at 2024.
  - A composition effect in the 2020 jump in real hourly earnings is not measured.
  - Recession outcomes after yield-curve inversions, and the 2006–07 inversion left out of the breakeven discussion.
  - Rebuilt with `python3 build.py --book all --epub`; the six EPUBs pass epubcheck 5.1 with no messages; the four new figures pass figlint in both languages.
- Chapter 4 (货币、银行与中央银行的资产负债表): written and reviewed. Fixes are in the commit "Chapter 4: fixes after the independent review".
  - The leaky floor of 2008 now gives both changes in how interest on excess reserves was set (target less 35 bp from 23 October, equal to the target from 6 November), from FRED's daily IOER and target series.
  - The reverse repos of 7 October 2026 are split by holder: 331.4 of the 333.7 billion dollars are foreign official and international accounts, 2.3 billion the ON RRP facility (H.4.1). The federal funds market is "dominated by the Federal Home Loan Banks" (FOMC minutes, November 2018).
  - Smith's colonial exchange rates start from the units: Pennsylvania passed 5s sterling for 6s 8d, so £100 sterling was £133 currency even in coin.
  - Peru: most of the rise in the foreign-currency share of broad money in 2013–15 is the exchange rate (2.80 to 3.41 soles per dollar); at the December 2013 rate the December 2015 share is still 32.9%. BCRP series PN00023MM and PN00024MM were added to the snapshot for this.
  - Floor vs corridor is argued from both sides of the November 2018 minutes; September 2019 and the standing repo facility of July 2021 show the floor needs a ceiling. The PBoC's foreign-exchange share "about 80%" is limited to 2011–14.
  - `money_facts` has 168 rows; 167 quotations verify verbatim. The PBoC balance sheet has no terms of use; the author confirmed on 2026-10-14 that the snapshot may be committed.
  - FORWARD_REFS has ten new rows from Chapter 4 (Chapters 5, 28, 45, 52, 61, 63, 64, 66, 75, 76, 77).
  Open points:
  - The label `ex:money-tax` does not match its example's title (换一个买家); left so as not to move references.
  - The stigma of the discount window is not discussed (no citable source found).
  - The shrinking of interbank lending is covered only through the FHLBs.
  - Rebuilt with `python3 build.py --book all --epub`; the six EPUBs pass epubcheck 5.1 with no messages; the five figures pass figlint in both languages.
- Chapter 5 (国际收支与汇率): written and reviewed. Fixes are in the commit "Chapter 5: fixes after the independent review".
  - The opening sets Sri Lanka's reserves running out in 2022 against the long US deficit. The balance of payments is built from a worked example in BPM6 net-lending form, with SAFE's opposite sign convention beside it. The sector balances are extended to the open economy through gross national disposable income.
  - Exchange rates: real rates, PPP (tested on 181 price levels in 2021 and on 137 economies over 2001–21 and 2020–21), covered parity after 2008 (Du, Tepper & Verdelhan) and the failure of uncovered parity (Engel). Reserves, original sin and regimes are covered, with a case on China's reserves 2004–16 that gives both the precautionary and the mercantilist reading.
  - Review fixes:
    - The standstill's four categories of debt are listed in full.
    - The capital account's examples follow BEA (patents are in R&D services).
    - Most of the one-year PPP result comes from Libya alone; without it the slope is 0.65 and R² 0.20.
    - SAFE's 6.4% is checked against the end-2015 central parity.
    - The US income asymmetry now gives both readings: Gourinchas & Rey's "exorbitant privilege", and Curcuru, Dvorak & Warnock's critique.
    - BPM7 (2025) is mentioned, dated from the 2025 SNA.
    - The cost of import compression (real incomes, rice imports) is stated.
  - Mun was wrongly described as counting goods only, here and in Chapter 16. In fact, when drawing up the national balance he adds freight, insurance and merchants' gains to exports (ch. XX). Chapter 16's sentence, self-check 1 and its answer are corrected, and `merc_facts` has two new rows (316 quotations verify).
  - `external_facts` has 169 rows, all of which verify verbatim. The data snapshots are `cbsl_reserves`, `bis_fx`, `fred_us_external`, `wb_external_annual`, `wb_price_levels`, `wb_relppp` and `pbc_balance_sheet`.
  - FORWARD_REFS: five promises to Chapter 5 are marked done; there are eleven new rows from Chapter 5 (Chapters 6, 19/23, 36/46, 37, 61, 62, 64, 69, 72, 76, 82). Appendix B now has $q$ and the superscript-$f$ convention for foreign variables.
  For the author:
  - **CBSL reserve data:** only the derived extract `cbsl_reserves` is committed. The basis is the CBSL Bulletin's notice that its material "may be reproduced or translated in whole or in part without prior permission … provided due credit is given". Please confirm that this covers the reserve data template.
  - **SAFE:** SAFE's legal statement allows only non-commercial reproduction with permission, so no SAFE data file is committed. The chapter quotes a few sentences and numbers from the 2016 report and the 2015 annual report, with "信息来源：国家外汇管理局网站". China's numbers for calculation come from the World Bank (CC BY 4.0).
  - **Libya:** its 2020 official rate may not have been the rate most transactions used. The WDI notes do not flag it, so it stays in the sample and is marked in the figure. Dropping it would change the one-year headline to 0.65 / R² 0.20 and the figure.
  Open points:
  - IMF sites return 403. BPM6 is quoted through BEA's manual, and the IMF programme is described as CBSL tells it.
  - The month in which the PBoC swap entered Sri Lanka's reserves is not documented (the jump of December 2021 is left unexplained).
  - Chapter-local symbols ($F$, $\mathit{CA}$, $\mathit{KA}$, $\mathit{FA}$, $\mathit{EO}$) are not in Appendix B.
  - Rebuilt with `python3 build.py --book all --epub`; the six EPUBs pass epubcheck 5.1 with no messages; the five figures pass figlint in both languages.

## Part 2 — written and reviewed (sequential, one reviewer per chapter; notes in `docs/agent_prompts/part2_notes.md`)
- Started 2026-10-14: Chapters 6, 7, 8, 9 in that order, all four written and reviewed 2026-10-14; Chapter 1 after them.
- Chapter 6 (美索不达米亚与埃及：神庙、宫廷与记账): written and reviewed. Fixes are in the commit "Chapter 6: independent review fixes".
  - The edicts: Ammi-ṣaduqa's cancels debts owed to the crown; the innkeeper clause concerns the palace collector's claim (CAD M/2, Ṣ, Kraus's numbering 11′, 14′).
  - § 48 follows King's "rent", which CAD reads as interest; the debt is not cancelled, only that year's payment.
  - The CAD mathematical problem asks "how many years"; Erman's two statements (wages in kind; not to think the workmen wretched, pp. 125–126) stand side by side.
  - The risk reading rests only on the loans the chapter cites (barley loans tied to the harvest at Mari; silver lent at interest at Kanesh); the repayment probability is written $\theta$, because $p$ is the price and $q$ the real exchange rate.
  - The granary's tax is $I_t$ (harvests differ); Temin (2003) and Slotsky (1997) are cited separately.
  - The deeper box explains clustered standard errors: dates show no seasonal pattern with errors clustered by year ($p=0.30$) but $p=0.001$ with ordinary errors; barley's joint test is $p=0.023$ (0.031 in $F$ form). The direction of the barley effect cannot be fixed, since the dataset's month numbers are not documented against the Babylonian calendar.
  - `meso_prices` panel titles now state the finding. `meso_facts` has 123 rows, all verified verbatim; it gains Erman pp. 125–126 and 497, King's gloss on § 273 and Mitchell Innes, and drops the unused § 100 row. The check asserts the dataset's "per mina (=0.5 kg)" metadata.
  - FORWARD_REFS: rows 53 and 113 done; new rows from Chapter 6 to Chapters 7, 8, 9, 51 and 77.
  Open points:
  - Humphrey (1985) and Graeber (2011) could not be obtained; their arguments are paraphrased, not quoted. Slotsky is cited from Temin's bibliography.
  - The reign years of Sumulael, Samsuiluna, Abi-ešuḫ, Ammi-ṣaduqa and Ramesses IX are not given (no source in hand).
  - The chapter borrows equations from Chapters 13 and 14 and restates them in place.
  - Layout, all chapters: a long chapter title wraps and leaves its last character or two alone on the second line (账 in Chapter 6, 命 in Chapter 13, 帝国 in Chapter 14). The title format is in `preamble.tex`, which I have not changed; a ragged or balanced title setting would fix all three. Please say if you want it.
  - Rebuilt with `python3 build.py --book all --epub`; the six EPUBs pass epubcheck 5.1 with no messages; the three figures pass figlint in both languages.
- Chapter 7 (希腊与罗马：铸币、城邦财政与帝国的贬值): written and reviewed. The draft is in "Chapter 7: Greece and Rome, first draft"; the review fixes are in "Chapter 7: fixes after the independent review; rebuild compiled/".
  - The model: a coin's exchange value lies between its metal value and its official value, $v=c+\tau(\bar v-c)$ (`eq:greek-value`), so a debasement raises prices by $(1-\tau)$ of its size; $\tau=0$ is Chapter 17's `eq:toku-content`. The text says plainly that $q$ (the silver price of wheat) and $v$ cannot be separated in the data.
  - The tests, on Kelly's (2021) Egyptian prices (CC BY 4.0, one row per document): private wheat 190–270 shows no trend (−0.09% a year, $p=0.75$, 27 documents) while barley rises 1.46% a year ($p=0.021$, 10 documents); 31 state wheat prices, 20 of them exactly 8 drachmas; the 274 reform (more silver, a tenfold price rise) read as a loss of trust (Haklai-Rotenberg 2011); wheat prices after the Edict of 301 rising 20.2% a year to 314.
  - Contested questions with each side's strongest case: metallism against nominalism (Aristotle's two passages); plague against money for 160–190; four views of debasement and inflation; Finley against Temin, reconciled through Kelly's two sectors. The Edict is read as law against enforcement (Kent's three readings of Lactantius' "much blood", Egyptian prices after 301).
  - Fixes after the review:
    - Haklai-Rotenberg's n. 108 rules out the same-year explanation of the 301 price rise; her conclusion (Diocletian's own 294/96 reform) is now quoted.
    - The denarius is compared over the same period as the tetradrachm (2.4 → 1.9 g).
    - Caracalla's antoninianus has the same alloy as the denarius (Cope p. 103); the minority 1.5-denarii tariff gives zero seigniorage.
    - Kelly's obol evidence replaces the reading of steps of four as convention.
    - Also: Aristotle's *Politics* 1257b, P.Oxy. 1411's limits, the 274/75 Egyptian reform, the two documents dated 160, Kent on meals, Kent's 1920 account set against Diocletian's reforms, and the slaves' human cost. Pronouns were replaced by names.
    - `greek_facts` has 204 rows, all verified verbatim. The `greek_silver` panel title was wrong (一两成 for 1%–2%).
  - FORWARD_REFS: rows 32 and 124 done; new rows from Chapter 7 to Chapters 8, 23, 26, 43, 47, 49, 52, 75 and 76. The label registry gains Chapter 7's labels and `sec:medieval-oresme`.
  Open points:
  - Finley (1973) and Rathbone (1997) could not be obtained; Finley is quoted through Temin, and the text says the "Finley side" evidence is the book's own arrangement of Kelly's data.
  - No BC year is given for the Laurion and Maroneia strike; only Xenophon's dates are given (from the note at the head of the Gutenberg e-book).
  - The 190–270 test sets Roman debasement against Egyptian prices; the chapter has no year-by-year fineness of the Egyptian tetradrachm for 190–270 and says so.
  - Kelly's printed text and his appendix differ for P.Mich. II 123/127 (AD 45/46); the deeper box records it, and the pre-160 median is 8.73 either way.
  - Tacitus' "hundred thousand great sesterces" is left as Gordon translates it; no source in hand converts it.
  - The Haklai-Rotenberg PDF (iDAI, personal use) is quoted in short passages only and not redistributed.
  - Rebuilt with `python3 build.py --book all --epub`; the six EPUBs pass epubcheck 5.1 with no messages; the four figures pass figlint in both languages.
- Chapter 8 (先秦与秦汉：轻重之术、盐铁与常平仓): written and reviewed. The draft is in "Chapter 8: early China (qingzhong, salt and iron, the ever-normal granary), first draft"; the review fixes are in "Chapter 8: fixes after the independent review; rebuild compiled/".
  - The model: the ever-normal granary as a price band with a stock (`eq:qinhan-band`). A Monte Carlo summary shows the floor always holds and the ceiling often does not: storage loses 10% a year and grain must be bought before it is sold. Teaching inputs are stated in `checks/check_ch08.py`.
  - The 《管子》's 币重而万物轻 is set in Chapter 13's quantity equation, with the condition that velocity and the goods for sale stay fixed. The profit on a coin, $v-c-k$, uses Chapter 7's notation and explains 贾谊's two arguments and the 上林三官.
  - Sources: the 史记, 汉书 and 后汉书 (`verify_quotes.py`), and the 管子 and 盐铁论 (unpunctuated 四库 texts, checked verbatim by the check script). Every quotation was compared with Wikisource. Kanaya (1984) is used for the date of the 轻重 chapters: compiled in the Han, adopted but not as settled, with the earlier datings given.
  - Contested questions with each side's case: the date of the 轻重 chapters; the 大夫 against the 贤良 and 文学 at the salt and iron debate; free against state minting (贾谊, and the 文学's case against the 三官 coins); design against war and famine for Wang Mang. Law is kept apart from what happened (其货不行; 百姓不从，但行小大钱二品).
  - Fixes after the review:
    - The memorial that ended the debate (《盐铁论·取下》) also abolished the iron offices within the passes, not only the liquor monopoly. The reviewer's "最后一篇" is corrected to 取下.
    - The 600万石 passage now says part of the full granaries was bought with offices and remissions (入粟补吏，及罪以赎).
    - The 文学's reply on the 三官 coins is added after the 三官 section (或不中式，故有薄厚轻重; 择钱则物稽滞; 内不禁刀币以通民施).
    - Kanaya's account of the earlier datings is paraphrased.
    - Wang Mang's 宝货 were refused in the year they were issued (王莽传中).
    - The Monte Carlo result is split: the first ten years about a quarter, the later twenty about 40%.
    - 萧望之's objection is dated 五凤中 (57 BC).
    - Also: the 关东 price ratio (1.7 to 2.5), the 所转贩者/所轉貶者 reading, the takeaway on the quantity equation (now conditional), and two figure titles (`qinhan_prices` loses its single-panel title; `qinhan_wangmang` (a) states the finding).
    - `qinhan_facts` has 172 rows.
    - The 本章要点 box no longer leaves its heading alone at the foot of a page.
  - Outside the chapter: the English `greek_silver` (Chapter 7) had two overlapping labels, which figlint reported; the labels are moved.
  Open points:
  - 彭信威《中国货币史》 could not be obtained and is not cited; the chapter rests on the primary texts and Kanaya.
  - The legacy section names no modern buffer-stock schemes (commodity stabilisation funds, state grain reserves), because no source is in hand.
  - No dates of birth or death are given for persons (STYLE §3).
  - The PLAN suggested comparing the 常平仓 with open market operations. The compare box sets it against the interest-rate corridor of Chapter 4 instead, and the text links 贾谊's 以术敛之、以术散之 to open market operations.
  - Rebuilt with `python3 build.py --book all --epub`; the six EPUBs pass epubcheck 5.1 with no messages; the three figures pass figlint in both languages.

- Chapter 9 (古代印度与印度洋贸易): written and reviewed. The draft is in "Write Chapter 9: ancient India and the Indian Ocean trade"; the review fixes are in "Chapter 9: fixes after the independent review; rebuild compiled/".
  - The model: Rome's coins sent east in the balance of payments (`eq:india-coin`, a keyeq): as goods the current account balances ($X+C-M=0$); as Rome's financial asset it shows a deficit $C$ met by a fall in foreign assets. The BEA manual (monetary against nonmonetary gold, noncommemorative gold coins) supports the first; a third reading, coins as the issuer's currency (a liability, $\Delta L=C$), is set out and rejected because no one in India guaranteed the face value.
  - Pliny's 6.101 is read from the Latin: the framed D is 500 hundred-thousands, 50 million sesterces (Mayhoff's apparatus DL, 55 million); the English 550 million is ten times DL and clashes with 12.84's 100 million for three regions. The bar and the frame of the numerals on the LacusCurtius page are checked against the English distances (MM p. = 2 miles; CCCVIIII p. = 309 against 308; |XIII|·XXXII p. = 1332 against 1335).
  - Scale: Pliny's figures are 0.3%–0.6% of Scheidel and Friesen's 18 billion sesterces; the "hundred times" would be 27.8% of GDP and is read as rhetoric. The Muziris papyrus (Casson 1990) gives the Hermapollon's cargo, 6.927 million drachmas, and its quarter duty; the talent and the mina are solved exactly from the papyrus's own arithmetic.
  - The Arthashastra's interest rates by risk (1¼, 5, 10 and 20 per month per cent) are read with Chapter 14's $p=(1+r_f)/(1+i)$; its mint, salt, mines, commerce and tolls (1/5 on imports, lower rates for many goods) are compared with Chapter 8. Its date is given both ways (Fleet 1914; Olivelle via Francis's review).
  - Coins: Darley's (2014) totals by century and Appendix 6 by issuer (the counts CSV is gitignored; see below): 99.3% of the identified first-century silver is of Augustus and Tiberius. Read with `eq:greek-value` ($\tau=0$ in India, the fineness must be known), with two limits: Caligula and Claudius are also before the reform (14 coins), and Darley warns that "trusted" types imply unskilled assayers.
  - Contested questions with each side's strongest case: the drain as a loss (Pliny, Tacitus); Raschke and Darley against using Pliny's numbers; Casson and Young for the papyrus and the duties; Thür (Alexandria, two documents) against Casson (Muziris) on where the loan was drawn up.
  - Fixes after the review:
    - The Periplus only says the wind "it seems" is called Hippalos; the bracket is the translator's. 直到《周航记》的时代 stands outside the quotation.
    - Cunningham's 19-grain loss is "very exceptional" (3 grains a century against 1½); Fleet's claim is what "competent judges" seem to agree; Francis finds Olivelle's layers "globalement convaincante".
    - Arthashastra wording (隐士, 航海者…减免…以示优待, 供养臣仆) and the lower tolls of II.22 (1/6; 1/10 or 1/15; 1/20 or 1/25).
    - Casson: Thür's view; 几乎可以肯定; 计税重量; the Arabarchs. Young's rationale is paraphrased from Darley p. 87.
    - Scheidel's 18 billion is Scheidel and Friesen's figure. Darley's appearance premium is about late Roman coins; his Fig. 5.7 totals (6446 Roman, 4792 silver) differ from Fig. 5.8's and are mentioned; the 4120 undatable Karur coins are named in the caption.
    - Also: the route example starts at Alexandria (94 days; the Han route 3.8 times as long), Strabo's 120 ships "if a year's number", the full 王莽 quotation (元始元年 = AD 1), an intuition box on knowing a coin's fineness, `sec:india-test` admits the counts cannot separate the explanations, the pitfall matches Chapter 16 on Mun, and pronouns replaced by names.
    - `india_facts` has 184 rows from 23 sources, all verified verbatim (168 web rows, 16 corpus rows); 94 rows with values are read from their quotations.
  - FORWARD_REFS: rows 27, 126 and 137 done; new rows from Chapter 9 to Chapters 19 and 76. The label registry gains Chapter 9's labels and `sec:islamic-world`.
  Open points:
  - Darley's thesis forbids further distribution: it is quoted in short passages, the PDF is not in the repository, and the counts of its Appendix 6 (`data/fetch/darley2014_coin_finds.py` writes them) are gitignored. Please decide whether a derived table of counts may be committed.
  - Thür's articles (Tyche 2 and 3) could not be obtained; his view is given through Casson.
  - No reign years are given for the emperors (no source row in hand); no modern dating of the punch-marked coins (only Cunningham 1891).
  - Mayhoff's sigla ("v. DL rS.") are not explained in the file and are not interpreted.
  - The chapter has one keyeq (`eq:india-coin`).
  - Rebuilt with `python3 build.py --book all --epub`; the six EPUBs pass epubcheck 5.1 with no messages; the four figures pass figlint in both languages.

## Next
1. Part 2 is written (Chapters 6–9); next Chapter 1, reviewed like the others. Prepare a new session with `bash tools/setup_env.sh` and `bash tools/probe_network.sh`.
2. The author's review of Part 3 (Chapters 10, 11, 13–17) can come at any time; the open points are listed under each chapter above.
3. Then the other parts in the order of the books.

## English edition — reserved
`\ZE{}{}` in the preamble, `T("中文", "English")` in figures, English titles in `structure.py` and `en/README.md` are in place. No translation has started.

## Chapter 84 (outlook) revision log
- (none yet; record the date and the data snapshots used each time the chapter is revised)
