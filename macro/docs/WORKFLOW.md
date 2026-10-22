# Writing chapters in batches

Chapter 12 set the standard (`STYLE.md` §11, approved 2026-10-13). From Part 3 on, chapters are written
one part at a time, each chapter then reviewed independently; the editor merges, rebuilds and checks
everything, and the author reviews the part as a whole. There are two ways to run a part:

- **Sequential (the author's choice for Part 3, 2026-10-13):** one chapter at a time, in the order of
  the part. The editor writes the chapter on the working branch, then one independent reviewer agent
  reviews it (never more than one agent at a time); the editor checks the review, commits and pushes,
  and goes on to the next chapter. Later chapters can then use labels and results of earlier ones.
- **Parallel:** several writers at once, each in its own git worktree, then one reviewer per chapter
  (§1–§3 below). Faster, but the writers cannot see each other's chapters, so the part's notes file
  must divide the ground between them.

**Language (from 2026-10-15).** Chapters 1–21 were polished to `docs/NARRATIVE.md` (language only;
record in `docs/POLISH.md`). New chapters are written to the same rules from the start: read
`NARRATIVE.md` §3–§8 and `POLISH.md` §3–§4 before writing, and measure the draft against
`NARRATIVE.md` §10.3 with `python3 tools/readability.py zh/chNN_<slug>.tex --all` (also printed at
the end of `tools/check_chapter.py`). Paragraphs that paraphrase snapshot rows end with
`% 据: row_id, ...`, checked by `checks/common.anchors()` (`STYLE.md` §5). The author decided on 2026-10-16 that Chapter 22 onwards is written to
these rules from the start; `docs/agent_prompts/write_template.txt` (rule 9) and `review_template.txt`
(item 7) now carry the checklist of `NARRATIVE.md` §10.2 and ask for the metrics row in the report.
Name a person whose years cannot be verified with “生卒年未详” (`STYLE.md` §3).

## 0. Prepare the session

```bash
cd macro
bash tools/setup_env.sh          # system packages if missing (TeX Live, fonts, pandoc, Java; ~5 min),
                                 # Python packages, the classical-Chinese corpus, epubcheck, STIX Two
export CORPUS=...                # as printed by the script
export EPUBCHECK_JAR=...
bash tools/probe_network.sh      # which source hosts the shell can reach in this session
python3 data/fetch/verify_quotes.py $CORPUS && python3 data/fetch/verify_web_quotes.py \
  && python3 validate_source.py && python3 build.py
```

- `setup_env.sh` ends with a font check. The books are set in STIX Two Text and Math with Noto CJK;
  without them `preamble.tex` falls back to TeX Gyre Termes and Latin Modern Math, and books built
  that way must not be committed to `compiled/`.
- Network access differs between sessions. In the first sessions (early October 2026) the shell
  reached only github.com and PyPI. On 2026-10-13 it reached Wikipedia and Wikisource, ctext,
  archive.org, JSTOR's front pages, NBER, the Bank of England, the GGDC (Maddison), MeasuringWorth,
  GPIH, the Bank of Japan's IMES, the BIS, the ECB, the New York Fed, the World Bank and FRED
  (intermittently), while Wiley, Elsevier, Cambridge, Oxford, Chicago journals, the IMF, CEPR,
  openICPSR and Encyclopaedia Iranica answered 403. Always run the probe rather than trusting this
  list. What can be downloaded is checked in the shell (evidence rule 3 of the brief); the web tools
  are for what cannot.

## 1. Write

- Brief: `docs/agent_prompts/batch_brief.txt` plus the chapter's section of the part's notes file
  (`docs/agent_prompts/part3_notes.md` for Part 3; write a similar file for later parts, dividing the
  ground between the chapters of the part).
- Read the rows of `docs/FORWARD_REFS.md` that point to your chapter and keep those promises; add a
  row for every reference your chapter makes to an unwritten chapter whose content the reader needs.
- Parallel mode: each writer works in its own git worktree of this repository (its own branch),
  commits its chapter there and reports: sources and how each was verified, single-witness numbers,
  things left out, labels for the registry, requests for shared-file changes.
- Sequential mode: the editor writes on the working branch and keeps the same record (it goes into
  the chapter's PLAN.md entry and the commit message).

## 2. Review (one independent reviewer per chapter)

- Brief: `docs/agent_prompts/review_template.txt`, pointed at the chapter (and in parallel mode at the
  writer's worktree), with `$CORPUS`.
- The reviewer checks every quotation in context (`verify_quotes.py` or `verify_web_quotes.py`, and the surrounding passage), every
  cited work, every number against its check script, and the layout; fixes the chapter and its check
  script; reports what it did not fix.
- The editor verifies the reviewer's substantive claims against the sources before accepting them
  (in Chapter 12 they all held; one diagnosis of a layout cause did not).

## 3. Merge and check (editor)

1. Parallel mode: merge each branch. `references_zh.tex` and `data/SOURCES.md` merge as unions
   (`.gitattributes`); remove duplicate `\bibitem` keys.
2. Add the labels the chapters need to the PLAN.md registry; apply or decline shared-file requests.
3. Redraw all figures: `MACRO_LANG=zh python3 figsrc/build.py` and `MACRO_LANG=en python3 figsrc/build.py`.
   Then run `MACRO_LANG=zh python3 tools/figlint.py` and the same with `en`. It reports text that
   prints below 7.5 pt, text off the FIG_W canvas (which widens the cropped file so that `\fig`
   shrinks the whole figure), and text overlapping other text. Then look at every PNG of the part in both languages for text on lines
   or markers, which the script cannot see. English labels are longer and collide more often.
4. Run, all clean: `checks/check_*.py`, `data/fetch/verify_quotes.py $CORPUS`,
   `data/fetch/verify_web_quotes.py` (quotations from modern publications and online editions), `validate_source.py`,
   `tools/check_chapter.py` for each new chapter, `build.py --book all --epub`, epubcheck on the six EPUBs.
5. Update `docs/STATUS.md`; commit and push; ask the author to review the part.

## Status of the batches

- Part 3 (第 10、11、13—17 章): notes in `docs/agent_prompts/part3_notes.md`; written sequentially in
  the order 10, 11, 13, 14, 15, 16, 17, started 2026-10-13; all seven written and reviewed and the figures redrawn
  by 2026-10-13; awaiting the author's review.
- Part 1 (第 2—5 章; 第 1 章 last, after Part 2): notes in `docs/agent_prompts/part1_notes.md`; written
  sequentially in the order 2, 3, 4, 5, started 2026-10-14; Chapters 2, 3, 4 and 5 written and reviewed 2026-10-14.
- Part 2 (第 6—9 章): notes in `docs/agent_prompts/part2_notes.md`; written sequentially in the order
  6, 7, 8, 9, started 2026-10-14; all four written and reviewed 2026-10-14.
- Chapter 1 (`ch:intro`): written and reviewed 2026-10-14, after Part 2; to be revisited when the book is complete
  (PLAN §7).
- Part 4 (第 18—25 章): notes in `docs/agent_prompts/part4_notes.md`; written sequentially in the order
  18, 19, …, 25, started 2026-10-15; Chapters 18, 19, 20 and 21 written and reviewed 2026-10-15; paused after Chapter 21 at the
  author's request. Resumed 2026-10-16 with the narrative plan (NARRATIVE.md, write_template rule 9, batch_brief's NARRATIVE AND
  LANGUAGE): Chapters 22 (`ch:marx`), 23 (`ch:goldstandard`) and 24 (`ch:periphery`) written and reviewed 2026-10-16; Chapter 25 (`ch:wicksell`) written in parallel in its own worktree at the author's request and reviewed (2026-10-16);
  figures redrawn and the book rebuilt; the author's decisions on Part 4 recorded and the branch merged into main
  (2026-10-16); paused before Part 5 at the author's request.

- Part 5 (第 26—34 章): notes in `docs/agent_prompts/part5_notes.md`; written sequentially in the order
  26, 27, …, 34. Chapter 26 (`ch:weimar`): a first version was written outside this workflow on 2026-10-20
  (branch `codex/ch26-weimar`); the editor reviewed it, merged the branch to keep its verified sources and
  data, and had the chapter rewritten to the notes and reviewed by one independent reviewer (2026-10-21). The
  author decided on 2026-10-21 that the remaining chapters are written in this workflow. Merged into main on
  2026-10-22 at the author's request; Chapter 27 (`ch:interwar`) started 2026-10-22.
