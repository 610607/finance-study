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
- Chapter 3 (价格、通胀与利率): sources collected (Boskin report; Fisher 1896 with the US currency/coin bonds and India's rupee paper; BoJ statements of 2016 and 2024 with MoF JGB yields, under PDL 1.0; DMO on index-linked gilts; the first TIPS auction; FRED series). Writing next.

## Next
1. Part 1: Chapters 3, 4, 5, then Part 2 (Chapters 6–9), then Chapter 1; each reviewed before the next. Prepare a new session with `bash tools/setup_env.sh` and `bash tools/probe_network.sh`.
2. The author's review of Part 3 (Chapters 10, 11, 13–17) can come at any time; the open points are listed under each chapter above.
3. Then the other parts in the order of the books.

## English edition — reserved
`\ZE{}{}` in the preamble, `T("中文", "English")` in figures, English titles in `structure.py` and `en/README.md` are in place. No translation has started.

## Chapter 84 (outlook) revision log
- (none yet; record the date and the data snapshots used each time the chapter is revised)
