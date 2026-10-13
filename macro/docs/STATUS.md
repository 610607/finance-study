# Project status

Updated 2026-10-13.

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

## EPUB edition — added 2026-10-13
- `tools/epub/` converts the LaTeX sources to EPUB 3 with pandoc, taking every number from the PDF build (`docs/EPUB.md`). `python3 build.py --book all --epub` writes the volume and the five books; the EPUBs pass epubcheck 5.1 with no errors or warnings.

## Hand-off repaired — 2026-10-13
- `tools/setup_env.sh` now installs what a bare cloud container lacks (TeX Live, Noto CJK, fallback fonts, pandoc, Java) and the STIX Two fonts (stipub/stixfonts v2.13b171), and ends with a font check. The PDFs and EPUBs in `compiled/` were rebuilt with STIX Two Text and Math, the fonts `preamble.tex` intends (the earlier builds had fallen back to TeX Gyre Termes and Latin Modern Math); Chapter 12 checked clean with them (17 pages with its bibliography), all six EPUBs pass epubcheck.
- `tools/probe_network.sh` reports which source hosts the shell can reach; on 2026-10-13 many could be downloaded from directly. Evidence rule 3 of the brief now asks for the original document to be downloaded and every number found in its text, with the file's SHA-256 recorded; WebFetch is the fallback for blocked hosts.
- `docs/FORWARD_REFS.md` records what written chapters expect of unwritten ones (seeded with Chapter 12's references).
- Part 3 is written sequentially (author's choice): one chapter at a time, each reviewed by one independent reviewer before the next (`docs/WORKFLOW.md`).

## Part 3 — in progress (sequential, one reviewer per chapter)
- Chapter 10 (伊斯兰世界与地中海的商业革命): written and reviewed; the review's fixes are in commit "Chapter 10: apply the independent review".
- Chapter 11 (中世纪欧洲：庄园、黑死病与货币贬值): written and reviewed; fixes applied (including example 11.3 now set in the 1350s, labour 0.71, when the statutes were made; the intuition box now matches the one-quality-land model). Open points from the review, not done: the literature that followed Rolnick, Velde & Weber (Velde, Weber & Wright 1999; Sussman 1993; Sargent & Velde 2002) is not cited; Oresme's treatise is dated only by its 1864 editor (before 1373), not by the modern estimate (c. 1355–60), for want of a downloaded modern source; the tension between Oresme's fourth point (metal leaves the kingdom) and the mint inflows of the debasement puzzle is not discussed; the Peasants' Revolt of 1381 is not mentioned; in figure `plague_wages` (a) two labels could sit better and the shaded plague band is faint; the Great Famine of 1315–17 has no citation of its own (only Clark's cost-of-living series).
- Chapter 13 (白银的世纪：波托西、马尼拉与价格革命): written and reviewed; fixes applied in commit "Chapter 13: apply the independent review" (De Comyn's own range of a quarter to a half, example 13.1's two calculations reconciled, example 13.2 read as one range of fine-gold prices, Bodin's "en partie" already in the 1568 edition, Drelichman & Voth's no-haircut counterfactual, example 13.6's fall in the debt ratio attributed to the 1575 revenue jump and the 1577 settlement, the 明史 account of 1603 given in full). Added after the review: Potosí's silver mined by forced labour under the mita (Dell 2010, abstract; details owed by Chapter 14), the Álvarez-Nogal & Chamley (2014) reading of Philip II's debts (abstract only; the full text was not reachable), Malestroit's name (Jehan Cherruyt, known only from a handwritten note; life unknown), the common-gold sentence of the memorial. Open points, not done: Drelichman & Voth's 2015 reply to Álvarez-Nogal & Chamley is not cited (paywalled); the dates 1565 (全汉昇) and 1571 (Drelichman & Voth) for the Philippines stand side by side; 徐石楼 is not identified; the factor of two between Hamilton's 1929 Table A and his 1934 totals is unexplained; the chapter derives the debt dynamics formally, an exception to PLAN §1 that the author should confirm (recorded in PLAN).

## Next
1. Part 3 (Chapters 10, 11, 13–17), sequentially in that order, following `docs/WORKFLOW.md`: brief `docs/agent_prompts/batch_brief.txt`, chapter notes `docs/agent_prompts/part3_notes.md`, an independent review of each chapter. Prepare a new session with `bash tools/setup_env.sh` and `bash tools/probe_network.sh`.
2. Then the other parts in the order of the books, each as a batch.
3. Chapter 1 is finalized last, because it previews the whole volume.

## English edition — reserved
`\ZE{}{}` in the preamble, `T("中文", "English")` in figures, English titles in `structure.py` and `en/README.md` are in place. No translation has started.

## Chapter 84 (outlook) revision log
- (none yet; record the date and the data snapshots used each time the chapter is revised)
