# Writing chapters in batches

Chapter 12 set the standard (`STYLE.md` §11, approved 2026-10-13). From Part 3 on, chapters are written
one part at a time: several writers in parallel, each chapter then reviewed independently, the editor
merges, rebuilds and checks everything, and the author reviews the part as a whole.

## 0. Prepare the session

```bash
cd macro
bash tools/setup_env.sh          # Python packages, xeCJK if missing, the classical-Chinese corpus, epubcheck
export CORPUS=...                # as printed by the script
export EPUBCHECK_JAR=...
python3 data/fetch/verify_quotes.py $CORPUS && python3 validate_source.py && python3 build.py
```

Network: in the cloud sessions used so far, the shell reached only github.com and PyPI; other hosts
returned 403. Web pages and papers are read with the web tools, under the evidence rules of the brief.

## 1. Write (one writer per chapter, in parallel)

- Each writer works in its own git worktree of this repository (its own branch).
- Brief: `docs/agent_prompts/batch_brief.txt` plus the chapter's section of the part's notes file
  (`docs/agent_prompts/part3_notes.md` for Part 3; write a similar file for later parts, dividing the
  ground between chapters written at the same time).
- The writer commits its chapter on its branch and reports: sources and how each was verified,
  single-witness numbers, things left out, labels for the registry, requests for shared-file changes.

## 2. Review (one independent reviewer per chapter)

- Brief: `docs/agent_prompts/review_template.txt`, pointed at the writer's worktree, with `$CORPUS`.
- The reviewer checks every quotation in context (`verify_quotes.py` and the surrounding passage), every
  cited work, every number against its check script, and the layout; fixes the chapter and its check
  script on the same branch; reports what it did not fix.
- The editor verifies the reviewer's substantive claims against the sources before accepting them
  (in Chapter 12 they all held; one diagnosis of a layout cause did not).

## 3. Merge and check (editor)

1. Merge each branch into `main`. `references_zh.tex` and `data/SOURCES.md` merge as unions
   (`.gitattributes`); remove duplicate `\bibitem` keys.
2. Add the labels the writers asked for to the PLAN.md registry; apply or decline shared-file requests.
3. Redraw all figures: `MACRO_LANG=zh python3 figsrc/build.py` and `MACRO_LANG=en python3 figsrc/build.py`.
4. Run, all clean: `checks/check_*.py`, `data/fetch/verify_quotes.py $CORPUS`, `validate_source.py`,
   `tools/check_chapter.py` for each new chapter, `build.py --book all --epub`, epubcheck on the six EPUBs.
5. Update `docs/STATUS.md`; commit and push; ask the author to review the part.

## Status of the batches

- Part 3 (第 10、11、13—17 章): notes ready in `docs/agent_prompts/part3_notes.md`; not started.
