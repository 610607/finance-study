"""Welfare ratios of unskilled labourers in ten cities of Europe and Asia, 1730-1913, from Allen, Bassino, Ma,
Moll-Murata and van Zanden (2011), as published by the Global Price and Income History Group (GPIH, UC Davis).

    python3 data/fetch/gpih_welfare.py          # download the file and write the snapshot
    python3 data/fetch/gpih_welfare.py DIR      # use a copy of China_1730-1933_Allen_et_al.xls already in DIR

The file "China_1730-1933_Allen_et_al.xls" holds the data of Figures 2-6 of "Wages, Prices, and Living Standards
in China, 1738-1925: in comparison with Europe, Japan, and India" (GPIH Working Paper No. 1; Economic History
Review 64(S1), 2011). Its sheet "Figures2-6" has three blocks side by side: silver wages (grams of silver a day),
"barebones" consumer price indices (grams of silver a man a year) and "Real Wage in Welfare Ratios ". The script
checks the block heading and the ten city headings of the last block (columns 22-31; the headings "Suzhou/" and
"Kyoto/" are completed on the next row by "Shanghai" and "Tokyo"), keeps the years 1730-1913 and writes
data/snapshots/gpih_allen2011_welfare.csv. A welfare ratio is a full-time year's earnings (250 days) divided by
the cost of a bare-bones basket for a family (three adult baskets plus 5% for rent), so 1 is bare subsistence.
The SHA-256 of the file is printed so that it can be compared with the one recorded in the .json. The file is
.xls and needs the xlrd package (pip install xlrd).
"""
from __future__ import annotations

import csv
import hashlib
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "snapshots" / "gpih_allen2011_welfare.csv"
URL = "https://gpih.ucdavis.edu/files/China_1730-1933_Allen_et_al.xls"
NAME = "China_1730-1933_Allen_et_al.xls"
UA = "Mozilla/5.0 (X11; Linux x86_64) finance-study data fetch"
FIRST, LAST = 1730, 1913
SHEET = "Figures2-6"
BLOCK = (5, 22, "Real Wage in Welfare Ratios")              # (row, column, heading)
# (column, heading on row 6, heading on row 7, name in the snapshot)
CITIES = [(22, "", "London", "london"), (23, "", "Amsterdam", "amsterdam"), (24, "", "Leipzig", "leipzig"),
          (25, "", "Milan", "milan"), (26, "", "Beijing", "beijing"), (27, "Suzhou/", "Shanghai", "suzhou_shanghai"),
          (28, "", "Canton", "canton"), (29, "Kyoto/", "Tokyo", "kyoto_tokyo"), (30, "", "Bengal", "bengal"),
          (31, "", "Oxford", "oxford")]


def fetch(dest: Path) -> Path:
    path = dest / NAME
    if not path.exists():
        req = urllib.request.Request(URL, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=120) as r:
            path.write_bytes(r.read())
    print(f"{path.name}: sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}")
    return path


def main(dest: Path) -> None:
    import xlrd
    sh = xlrd.open_workbook(str(fetch(dest))).sheet_by_name(SHEET)
    r, c, title = BLOCK
    if str(sh.cell_value(r, c)).strip() != title:
        raise ValueError(f"row {r}, column {c} is {sh.cell_value(r, c)!r}, expected {title!r}")
    for c, top, head, _ in CITIES:
        got = (str(sh.cell_value(6, c)).strip(), str(sh.cell_value(7, c)).strip())
        if got != (top, head):
            raise ValueError(f"column {c}: headings {got}, expected {(top, head)}")
    rows = {}
    for i in range(8, sh.nrows):
        y = sh.cell_value(i, 0)
        if not isinstance(y, float) or not FIRST <= y <= LAST:
            continue
        if int(y) in rows:
            raise ValueError(f"year {int(y)} appears twice")
        rows[int(y)] = {name: (sh.cell_value(i, c) if isinstance(sh.cell_value(i, c), float) else None)
                        for c, _, _, name in CITIES}
    years = list(range(FIRST, LAST + 1))
    missing = [y for y in years if y not in rows]
    if missing:
        raise ValueError(f"years missing: {missing}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["year"] + [c[3] for c in CITIES])
        w.writeheader()
        for y in years:
            w.writerow({"year": y, **{k: ("" if v is None else round(v, 4)) for k, v in rows[y].items()}})
    print(f"{len(years)} years {FIRST}-{LAST} -> {OUT}")


if __name__ == "__main__":
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / ".cache" / "finance-study" / "gpih"
    folder.mkdir(parents=True, exist_ok=True)
    main(folder)
