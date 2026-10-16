# Check scripts

One script per chapter, `check_chNN.py`, recomputes every number quoted in `zh/chNN_<slug>.tex` and asserts it. Start from `_template.py`; shared helpers are in `common.py` (`load_snapshot`, `quoted`, `anchors`).

- Data are read from `data/snapshots/` through `load_snapshot(name)`, which refuses snapshots without complete metadata.
- Teaching inputs (the parameters of a stylized economy) are labelled as such in the text once. The running teaching model of the volume gets its parameters from `teaching_params.py`, created when Chapter 32 is written.
- Models are solved with the open-source libraries listed in `docs/STYLE.md`; nothing here implements its own solver.
- A paragraph that paraphrases snapshot rows ends with a comment line `% 据: row_id, row_id` (`docs/STYLE.md` §5). `anchors(tex, rows, script=Path(__file__))` checks that every anchored id is a row of the chapter's snapshots, and lists the rows that neither the script names nor an anchor covers (a reminder, not an error). Used from Chapter 22 on; Chapters 1–21 have no anchors.

Run one chapter with `python3 checks/check_chNN.py`, all of them with `python3 build.py --checks`. `validate_source.py` checks that every `check_chNN.py` belongs to an existing chapter.
