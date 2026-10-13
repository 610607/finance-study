# Check scripts

One script per chapter, `check_chNN.py`, recomputes every number quoted in `zh/chNN_<slug>.tex` and asserts it. Start from `_template.py`; shared helpers are in `common.py` (`load_snapshot`, `quoted`).

- Data are read from `data/snapshots/` through `load_snapshot(name)`, which refuses snapshots without complete metadata.
- Teaching inputs (the parameters of a stylized economy) are labelled as such in the text once. The running teaching model of the volume gets its parameters from `teaching_params.py`, created when Chapter 32 is written.
- Models are solved with the open-source libraries listed in `docs/STYLE.md`; nothing here implements its own solver.

Run one chapter with `python3 checks/check_chNN.py`, all of them with `python3 build.py --checks`. `validate_source.py` checks that every `check_chNN.py` belongs to an existing chapter.
