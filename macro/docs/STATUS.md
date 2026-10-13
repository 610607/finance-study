# Project status

Updated 2026-10-13.

## Skeleton — committed
- `structure.py`: 11 parts, 5 books (分册), 84 chapters, 4 appendices.
- `zh/`: 84 chapter stubs, each with its title, label and guide box (core question, learning goals, prerequisites); part pages with introductions; preface; title page; Appendix A (planned contents), B (symbol conventions), C (index of comparisons and cases, filled automatically), D (timeline, planned).
- `docs/PLAN.md`: principles, running teaching model and tools, case map, books, and for every chapter its question, goals, candidate sources, cases, comparison candidates and prerequisites; label registry.
- `docs/STYLE.md`: writing, notation, sources, data, methods and figure rules.
- Tools: `build.py` (whole volume or one book), `validate_source.py`, `tools/check_chapter.py`, `figsrc/style.py` and `figsrc/build.py`, `checks/common.py` and `checks/_template.py`, `data/README.md` and `data/SOURCES.md`.
- `python3 build.py --book all` builds the whole volume and the five books with no LaTeX errors, overfull boxes or undefined references; `python3 validate_source.py` passes.
- `references_zh.tex` holds only the two verified general histories (De Vroey 2016; Snowdon & Vane 2005). Candidate works in `PLAN.md` are not yet verified.
- No chapter text, figures or data snapshots yet.

## Next
1. Sample chapter: Chapter 12 (宋元明纸币). Once the author approves it, add what it settles to `STYLE.md`.
2. Then the books in order, each chapter followed by an independent review (`docs/agent_prompts/review_template.txt`).
3. Chapter 1 is finalized last, because it previews the whole volume.

## English edition — reserved
`\ZE{}{}` in the preamble, `T("中文", "English")` in figures, English titles in `structure.py` and `en/README.md` are in place. No translation has started.

## Chapter 84 (outlook) revision log
- (none yet; record the date and the data snapshots used each time the chapter is revised)
