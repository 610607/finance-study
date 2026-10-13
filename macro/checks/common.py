"""Shared helpers for the chapter check scripts checks/check_chNN.py.

Every number quoted in a chapter is either read from a data snapshot or computed from stated
teaching inputs, and then asserted here so that the text, the figures and the checks agree.

    from common import load_snapshot, quoted
    df, meta = load_snapshot("fred_cpiaucsl")          # data/snapshots/fred_cpiaucsl.csv + .json
    quoted("CPI inflation 2022 (Dec/Dec, %)", value, expected=6.5, tol=0.05)

Only the standard library, NumPy and pandas are used here.  Model solutions belong to open-source
libraries named in docs/STYLE.md, not to code written in this folder.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOTS = ROOT / "data" / "snapshots"
REQUIRED = ["title", "source", "url", "series", "retrieved", "license", "used_in"]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_snapshot(name: str, **read_csv_kwargs):
    """Return (DataFrame, metadata) for data/snapshots/<name>.csv and its <name>.json."""
    import pandas as pd

    csv, meta_file = SNAPSHOTS / f"{name}.csv", SNAPSHOTS / f"{name}.json"
    if not meta_file.exists():
        raise FileNotFoundError(f"{meta_file} is missing: every snapshot needs its metadata")
    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    missing = [k for k in REQUIRED if not meta.get(k)]
    if missing:
        raise ValueError(f"{meta_file.name}: missing metadata fields {missing}")
    if not csv.exists():
        raise FileNotFoundError(f"{csv} is missing; if its licence forbids redistribution, run the "
                                f"fetch script named in {meta_file.name} first")
    return pd.read_csv(csv, **read_csv_kwargs), meta


def quoted(what: str, value: float, expected: float | None = None, tol: float = 0.0, rel: float = 0.0) -> float:
    """Print a value quoted in the text and, if `expected` is given, assert that it matches.

    tol is an absolute tolerance, rel a relative one (use the rounding of the printed number).
    """
    ok = True
    if expected is not None:
        ok = math.isclose(value, expected, abs_tol=tol, rel_tol=rel)
    print(f"{'ok ' if ok else 'BAD'} {what}: {value:.6g}" + ("" if expected is None else f" (text: {expected:g})"))
    if not ok:
        raise AssertionError(f"{what}: computed {value!r}, text says {expected!r}")
    return value
