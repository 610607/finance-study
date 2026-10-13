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
- `zh/ch12_songming.tex`: full text (8 sections, 4 worked examples, 4 comparison boxes, 1 case box, 2 tables, 3 figures, takeaways, self-check with answers); an independent review is under way.
- Data: `data/snapshots/yuanshi_suyinchao` (the 《元史》 table of notes printed each year, 1260–1329) and `data/snapshots/paper_money_facts` (quotations with their numbers from the Song, Yuan and Ming histories, each checked verbatim against a pinned digital text by `data/fetch/verify_quotes.py`).
- `checks/check_ch12.py` asserts every number in the text; `figsrc/fig_ch12.py` draws the figures in the style of the electromagnetics notes (STYLE.md §7.1).
- What the sample settled is recorded in `STYLE.md` §11. Awaiting the author's approval.

## EPUB edition — added 2026-10-13
- `tools/epub/` converts the LaTeX sources to EPUB 3 with pandoc, taking every number from the PDF build (`docs/EPUB.md`). `python3 build.py --book all --epub` writes the volume and the five books; the EPUBs pass epubcheck 5.1 with no errors or warnings.

## Next
1. Author's review of the sample chapter; adjust `STYLE.md` if needed.
2. Then the books in order, each chapter followed by an independent review (`docs/agent_prompts/review_template.txt`).
3. Chapter 1 is finalized last, because it previews the whole volume.

## English edition — reserved
`\ZE{}{}` in the preamble, `T("中文", "English")` in figures, English titles in `structure.py` and `en/README.md` are in place. No translation has started.

## Chapter 84 (outlook) revision log
- (none yet; record the date and the data snapshots used each time the chapter is revised)
