"""Japanese government bond yields by maturity (constant maturity, 1974 onward), from Japan's Ministry of Finance.

    python3 data/fetch/mof_jgb.py           # download jgbcme_all.csv and write the snapshot
    python3 data/fetch/mof_jgb.py FILE      # use a copy of jgbcme_all.csv

The Ministry publishes the daily yield curve of JGBs (1 to 40 years) as one CSV file. The script checks the
header, keeps every business day from 2013 onward (the period of the Bank of Japan's quantitative easing,
negative rate and yield curve control) and the last business day of each month before 2013, and writes
data/snapshots/mof_jgb_curves.csv in percent, with "-" (not published) as an empty cell. The SHA-256 of the
download is printed; the file is replaced every month, so a later run has more rows.
"""
from __future__ import annotations

import csv
import hashlib
import io
import sys
import tempfile
import urllib.request
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "snapshots" / "mof_jgb_curves.csv"
URL = "https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/historical/jgbcme_all.csv"
COLS = ["1Y", "2Y", "3Y", "4Y", "5Y", "6Y", "7Y", "8Y", "9Y", "10Y", "15Y", "20Y", "25Y", "30Y", "40Y"]
DAILY_FROM = date(2013, 1, 1)


def main(path: Path | None) -> None:
    if path is None:
        path = Path(tempfile.mkdtemp(prefix="mof_")) / "jgbcme_all.csv"   # downloads stay out of the repository
        req = urllib.request.Request(URL, headers={"User-Agent": "curl/8"})
        with urllib.request.urlopen(req, timeout=120) as r:
            path.write_bytes(r.read())
    raw = path.read_bytes()
    print(f"{path.name}: sha256 {hashlib.sha256(raw).hexdigest()}")
    rows = list(csv.reader(io.StringIO(raw.decode("ascii"))))
    if rows[1] != ["Date"] + COLS:
        raise ValueError(f"unexpected header {rows[1]}")
    data = []
    for r in rows[2:]:
        if not r or not r[0]:
            continue
        y, m, d = (int(x) for x in r[0].split("/"))
        data.append((date(y, m, d), [v if v != "-" else "" for v in r[1:]]))
    keep = []
    for i, (d, v) in enumerate(data):
        last_of_month = i + 1 == len(data) or data[i + 1][0].month != d.month
        if d >= DAILY_FROM or last_of_month:
            keep.append((d, v))
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["date"] + COLS)
        for d, v in keep:
            w.writerow([d.isoformat()] + v)
    print(f"wrote {OUT} ({len(keep)} rows, {keep[0][0]} to {keep[-1][0]})")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
