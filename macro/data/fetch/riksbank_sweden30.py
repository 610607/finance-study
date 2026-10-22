"""Sweden after the gold standard: the consumer price index, 1925-1939, and the Riksbank's discount rate, monthly,
1929-1939 (Chapter 30).

    python3 data/fetch/riksbank_sweden30.py              # download the two workbooks (if missing) and write the snapshots
    python3 data/fetch/riksbank_sweden30.py DIR          # use copies already downloaded into DIR

From the Riksbank's "Historical Monetary and Financial Statistics for Sweden" (the same two files as
data/fetch/riksbank_sweden25.py, whose hashes it checks):
  Volume I, ch. 8 (Edvinsson and Soderberg 2010), Table I.A8.1 "A Consumer Price Index for Sweden 1290-", column
    "Deflation index 1914 = 100" (version 2.1 of the file); an annual index;
  Volume II, ch. 6 (Waldenstrom 2014), Table II.A6.9 "Short-term interest rate, 1856-", monthly, per cent: the
    Riksbank's discount rate (diskonto), version 2.0 of the file.
The script checks the hashes and the headings and writes
  data/snapshots/riksbank_sweden_1925_1939.csv          annual: cpi_1914_100
  data/snapshots/riksbank_sweden_monthly_1929_1939.csv  monthly: discount_rate
It stores the values as published; the index on another base year and the changes are the book's own calculations.
"""
from __future__ import annotations

import csv
import hashlib
import sys
import urllib.request
from pathlib import Path

import xlrd

HERE = Path(__file__).resolve().parent
SNAP = HERE.parent / "snapshots"
OUT_A = SNAP / "riksbank_sweden_1925_1939.csv"
OUT_M = SNAP / "riksbank_sweden_monthly_1929_1939.csv"
BASE = "https://www.riksbank.se/globalassets/media/forskning/monetar-statistik/"
FILES = {"I": ("volym1/volumeich8consumerpriceindex.xls",
               "e4ef149df8001ac824013efd21bc352c4d4e3fcfcdd56aac5d9bfa9257483b3d"),
         "II": ("volym2/volumeiich6stocksandbonds.xls",
                "6004da8cb630edec38cf3bd1d5a214af84ab0c60a84604329936b25aaf447830")}
UA = "Mozilla/5.0 (X11; Linux x86_64) finance-study quotation check"
FIRST_A, FIRST_M, LAST = 1925, 1929, 1939


def title(sh, row: int, col: int, text: str) -> None:
    got = str(sh.cell_value(row, col)).strip()
    if got != text:
        raise ValueError(f"{sh.name}: cell ({row}, {col}) is {got!r}, expected {text!r}")


def main(d: Path) -> None:
    books = {}
    for vol, (name, sha) in FILES.items():
        p = d / Path(name).name
        if not p.exists():
            req = urllib.request.Request(BASE + name, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                p.write_bytes(r.read())
        got = hashlib.sha256(p.read_bytes()).hexdigest()
        if got != sha:
            raise SystemExit(f"{p.name}: sha256 {got}, expected {sha} (the file has changed)")
        print(f"ok {p.name}: sha256 {got}")
        books[vol] = xlrd.open_workbook(str(p))

    cpi_sh = books["I"].sheet_by_name("Table I.A8.1")
    title(cpi_sh, 2, 1, "Table I.A8.1 A Consumer Price Index for Sweden 1290–")
    title(cpi_sh, 3, 1, "Deflation index 1914 = 100")
    cpi = {int(r[0]): r[1] for r in (cpi_sh.row_values(i) for i in range(4, cpi_sh.nrows))
           if isinstance(r[0], float) and FIRST_A <= r[0] <= LAST}

    sh = books["II"].sheet_by_name("Table II.A6.9")
    title(sh, 2, 1, "Table II.A6.9 Short-term interest rate, 1856–")
    title(sh, 3, 0, "YYYY:MM")
    title(sh, 3, 1, "per cent")
    rate = {}
    for i in range(4, sh.nrows):
        k, v = sh.row_values(i)[:2]
        y, m = (int(x) for x in str(k).split(":"))
        if FIRST_M <= y <= LAST and isinstance(v, float):
            rate[(y, m)] = v

    with OUT_A.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["year", "cpi_1914_100"])
        for y in range(FIRST_A, LAST + 1):
            w.writerow([y, round(cpi[y], 6)])
    with OUT_M.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["month", "discount_rate"])
        for y in range(FIRST_M, LAST + 1):
            for m in range(1, 13):
                w.writerow([f"{y}-{m:02d}", round(rate[(y, m)], 6)])
    print(f"{LAST - FIRST_A + 1} years -> {OUT_A}; {12 * (LAST - FIRST_M + 1)} months -> {OUT_M}")


if __name__ == "__main__":
    default = Path.home() / ".cache" / "finance-study" / "riksbank"
    d = Path(sys.argv[1]) if len(sys.argv) > 1 else default
    d.mkdir(parents=True, exist_ok=True)
    main(d)
