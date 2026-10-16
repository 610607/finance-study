"""The London market price of silver, 1850-1914, from the Global Price and Income History Group (GPIH, UC Davis)
(Chapter 24).

    python3 data/fetch/gpih_silver24.py          # download the file (if needed) and write the snapshot
    python3 data/fetch/gpih_silver24.py DIR      # use a copy of the file already in DIR

"Silver_value_of_1273-1977.xls" (P. Lindert, 2006, from R. W. Jastram, Silver: The Restless Metal, 1981,
pp. 164-188): the London market price of silver in pounds per troy ounce, of standard silver (0.925 fine,
column 2) and of pure silver (column 5). The script checks the headings it relies on and writes the years
1850-1914 to data/snapshots/gpih_silver_market_1850_1914.csv, with the standard price also in pence
(240 pence to the pound), as the sources of the time quoted it.

The SHA-256 of the file is printed so that it can be compared with the one recorded in the .json.
The .xls file needs the xlrd package (pip install xlrd). Chapter 13's script (gpih_silver.py) reads the mint
price from the same file.
"""
from __future__ import annotations

import csv
import hashlib
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SNAP = HERE.parent / "snapshots"
OUT = SNAP / "gpih_silver_market_1850_1914.csv"
URL = "https://gpih.ucdavis.edu/files/Silver_value_of_1273-1977.xls"
NAME = "Silver_value_of_1273-1977.xls"
UA = "Mozilla/5.0 (X11; Linux x86_64) finance-study data fetch"
FIRST, LAST = 1850, 1914
# (row, column, expected text): the headings of the two columns used
HEADS = [(9, 1, "Standard silver = 0.925 fine"), (10, 2, "£  market price"), (11, 2, "per troy ounce"),
         (9, 5, "Pure silver"), (10, 5, "£  market price"), (11, 5, "per troy ounce"), (11, 0, "Year")]


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
    path = fetch(dest)
    sh = xlrd.open_workbook(str(path)).sheet_by_index(0)
    for row, col, text in HEADS:
        got = str(sh.cell_value(row, col)).strip()
        if got != text:
            raise ValueError(f"{path.name}: row {row} column {col} is {got!r}, expected {text!r}")
    n = 0
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "gbp_per_oz_standard_market", "gbp_per_oz_pure_market", "pence_per_oz_standard"])
        for i in range(12, sh.nrows):
            y = sh.cell_value(i, 0)
            if isinstance(y, float) and FIRST <= y <= LAST:
                std, pure = sh.cell_value(i, 2), sh.cell_value(i, 5)
                if not isinstance(std, float) or not isinstance(pure, float):
                    raise ValueError(f"{path.name}: no market price for {int(y)}")
                w.writerow([int(y), round(std, 6), round(pure, 6), round(std * 240, 4)])
                n += 1
    if n != LAST - FIRST + 1:
        raise ValueError(f"{path.name}: {n} years found, expected {LAST - FIRST + 1}")
    print(f"{n} years -> {OUT}")


if __name__ == "__main__":
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / ".cache" / "finance-study" / "gpih"
    folder.mkdir(parents=True, exist_ok=True)
    main(folder)
