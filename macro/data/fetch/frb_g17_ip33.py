"""Industrial production of the United States, monthly 1929-1941 (Chapter 33): the Federal Reserve Board's G.17 index.

    python3 data/fetch/frb_g17_ip33.py              # download ip_sa.txt into WEB_CACHE if missing, compare with the snapshot
    python3 data/fetch/frb_g17_ip33.py --offline    # use the cache only
    python3 data/fetch/frb_g17_ip33.py --write      # (re)write data/snapshots/frb_g17_ip_1929_1941.csv from the cached file

The Board publishes its industrial production data as fixed-width text files on the G.17 data download page
(https://www.federalreserve.gov/releases/g17/download.htm); ip_sa.txt holds the seasonally adjusted indexes, one row
per series and year: the series code in quotation marks, the year and twelve monthly values. The total index is series
B50001 (2017 = 100). The file is replaced with every monthly release and the history is revised from time to time, so
the snapshot records the SHA-256 of the copy read; a later copy is compared value by value and the differences are
reported. This is not FRED: the file comes from the Board's own site, whose terms say 'Unless otherwise indicated,
information on Board's website is in the public domain and may be copied and distributed without permission. Please
cite to the Board as the source of the information.' (row fed_terms of islm_facts).
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verify_web_quotes import CACHE, fetch

ROOT = HERE.parents[1]
NAME = "frb_g17_ip_1929_1941"
KEY = "frb_g17_ip_sa"
SERIES = "B50001"
YEARS = range(1929, 1942)


def parse(path: Path) -> dict[tuple[int, int], float]:
    """(year, month) -> the total index, for every year of the file; and the mean of 2017, the base year."""
    out: dict[tuple[int, int], float] = {}
    for line in path.read_text(encoding="ascii").splitlines():
        parts = line.split()
        if len(parts) == 14 and parts[0] == f'"{SERIES}"':
            year = int(parts[1])
            for m, v in enumerate(parts[2:], 1):
                out[(year, m)] = float(v)
    base = sum(out[(2017, m)] for m in range(1, 13)) / 12
    assert abs(base - 100) < 0.01, base                         # 2017 = 100
    return out


def main(offline: bool, write: bool) -> None:
    meta = json.loads((ROOT / "data" / "snapshots" / f"{NAME}.json").read_text(encoding="utf-8"))
    src = {"url": meta["url"], "format": "txt", "sha256": meta["sha256"]}
    path, note = fetch(KEY, src, offline)
    if path is None:
        raise SystemExit(f"{KEY}: {note}")
    if note:
        print(f"NOTE {KEY}: {note}; comparing the values")
    ip = parse(path)
    rows = [(y, m, ip[(y, m)]) for y in YEARS for m in range(1, 13)]
    out = ROOT / "data" / "snapshots" / f"{NAME}.csv"
    if write:
        with out.open("w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["year", "month", "ip_2017_100"])
            w.writerows((y, m, f"{v:.4f}") for y, m, v in rows)
        print(f"written {out} ({len(rows)} months), SHA-256 of the source {hashlib.sha256(path.read_bytes()).hexdigest()}")
        return
    with out.open(encoding="utf-8") as fh:
        old = {(int(r["year"]), int(r["month"])): float(r["ip_2017_100"]) for r in csv.DictReader(fh)}
    diff = [(k, old[k], v) for k, _, v in [((y, m), y, v) for y, m, v in rows] if abs(old[k] - v) > 5e-5]
    for k, a, b in diff:
        print(f"    {k}: snapshot {a}, this copy {b}")
    print(f"ok {len(rows)} months of {SERIES} compared, {len(diff)} differ")


if __name__ == "__main__":
    main("--offline" in sys.argv[1:], "--write" in sys.argv[1:])
