"""The US current account and international investment position, quarterly, for Chapter 5, from FRED (Federal
Reserve Bank of St. Louis), which republishes them from the Bureau of Economic Analysis.

    python3 data/fetch/fred_external.py          # download the series and write the snapshot
    python3 data/fetch/fred_external.py DIR      # use copies of the fredgraph CSV files kept in DIR

Series (BEA, millions of dollars):
  IEABC      balance on current account, seasonally adjusted, 1999 onward
  IEABCPI    balance on primary income, seasonally adjusted, 1999 onward
  IIPUSNETIQ US net international investment position, end of quarter, 2006 onward
  IIPUSASSQ  US assets, end of quarter
  IIPUSLIAQ  US liabilities, end of quarter
Each series is downloaded as https://fred.stlouisfed.org/graph/fredgraph.csv?id=CODE; the script checks the
header, merges by date and writes data/snapshots/fred_us_external.csv. The SHA-256 of every file is printed;
the values of the 2026-10-14 download are in the snapshot's .json. BEA revises these series every June.
"""
from __future__ import annotations

import csv
import hashlib
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "snapshots" / "fred_us_external.csv"
URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="
CODES = ["IEABC", "IEABCPI", "IIPUSNETIQ", "IIPUSASSQ", "IIPUSLIAQ"]


def read(code: str, folder: Path) -> dict[str, str]:
    path = folder / f"{code}.csv"
    if not path.exists():
        req = urllib.request.Request(URL + code, headers={"User-Agent": "curl/8"})
        with urllib.request.urlopen(req, timeout=120) as r:
            path.write_bytes(r.read())
        time.sleep(1)
    print(f"{code}: sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}")
    with path.open(encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    if rows[0] != ["observation_date", code]:
        raise ValueError(f"{code}: unexpected header {rows[0]}")
    return {d: v for d, v in rows[1:] if v not in ("", ".")}


def main(folder: Path | None) -> None:
    folder = folder or Path(tempfile.mkdtemp(prefix="fred_"))   # downloads stay out of the repository
    series = {c: read(c, folder) for c in CODES}
    dates = sorted(set().union(*series.values()))
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["date"] + CODES)
        for d in dates:
            w.writerow([d] + [series[c].get(d, "") for c in CODES])
    print(f"wrote {OUT} ({len(dates)} rows, {dates[0]} to {dates[-1]})")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
