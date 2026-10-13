"""Silver content of the pound sterling and silver prices of consumer goods in European cities, 1490-1700,
from the Global Price and Income History Group (GPIH, UC Davis).

    python3 data/fetch/gpih_silver.py          # download both files and write the two snapshots
    python3 data/fetch/gpih_silver.py DIR      # use copies already in DIR

1. "Silver_value_of_1273-1977.xls" (P. Lindert, 2006, from R. W. Jastram, Silver: The Restless Metal, 1981,
   pp. 164-188): the mint price of silver in pounds per troy ounce of sterling (0.925 fine) silver, and the
   grams of pure silver per pound at the mint price. The script checks the headings and writes the years
   1490-1700 to data/snapshots/gpih_silver_pound.csv.
2. "Allen_European_labourers_1264-1913.xlsx" (R. C. Allen, data of "The Great Divergence in European Wages
   and Prices from the Middle Ages to the First World War", Explorations in Economic History 38, 2001):
   block "(2) CONSUMER PRICE INDEX", the cost of one basket of consumer goods in grams of silver, on a
   common base for all cities. The script writes the seventeen cities for 1490-1700 to
   data/snapshots/gpih_allen_silver_cpi.csv; empty cells are years without an estimate.

The SHA-256 of each file is printed so that it can be compared with the one recorded in the .json.
The .xls file needs the xlrd package (pip install xlrd).
"""
from __future__ import annotations

import csv
import hashlib
import sys
import urllib.request
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
SNAP = HERE.parent / "snapshots"
BASE = "https://gpih.ucdavis.edu/files/"
SILVER = "Silver_value_of_1273-1977.xls"
ALLEN = "Allen_European_labourers_1264-1913.xlsx"
UA = "Mozilla/5.0 (X11; Linux x86_64) finance-study data fetch"
FIRST, LAST = 1490, 1700
CITIES = ["Antwerp", "Amsterdam", "London", "Oxford", "Paris", "Strasbourg", "Florence", "Milan", "Naples",
          "Valencia", "Madrid", "Augsburg", "Leipzig", "Vienna", "Gdansk", "Krakow", "Warsaw"]


def fetch(name: str, dest: Path) -> Path:
    path = dest / name
    if not path.exists():
        req = urllib.request.Request(BASE + name, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=120) as r:
            path.write_bytes(r.read())
    print(f"{path.name}: sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}")
    return path


def silver_pound(path: Path) -> None:
    import xlrd
    sh = xlrd.open_workbook(str(path)).sheet_by_index(0)
    head = [str(sh.cell_value(10, j)).strip() for j in range(sh.ncols)]
    unit = [str(sh.cell_value(11, j)).strip() for j in range(sh.ncols)]
    if not (head[1] == "£  mint price" and unit[1] == "per troy ounce" and head[10] == "Grams of silver per £"
            and unit[10] == "mint price"):
        raise ValueError(f"{path.name}: unexpected headings {head} {unit}")
    out = SNAP / "gpih_silver_pound.csv"
    n = 0
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "gbp_per_oz_sterling_mint", "grams_ag_per_gbp_mint"])
        for i in range(12, sh.nrows):
            y = sh.cell_value(i, 0)
            if isinstance(y, float) and FIRST <= y <= LAST:
                w.writerow([int(y), round(sh.cell_value(i, 1), 6), round(sh.cell_value(i, 10), 4)])
                n += 1
    print(f"{n} years -> {out}")


def allen_cpi(path: Path) -> None:
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True)["Labourers (Allen)"]
    rows = list(ws.iter_rows(values_only=True))
    if rows[6][21] != "(2) CONSUMER PRICE INDEX" or [rows[8][j] for j in range(21, 38)] != CITIES:
        raise ValueError(f"{path.name}: unexpected layout of the price block")
    out = SNAP / "gpih_allen_silver_cpi.csv"
    n = 0
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year"] + [c.lower() for c in CITIES])
        for r in rows[9:]:
            if isinstance(r[20], (int, float)) and FIRST <= r[20] <= LAST:
                vals = [r[j] for j in range(21, 38)]
                w.writerow([int(r[20])] + [round(v, 4) if isinstance(v, (int, float)) else "" for v in vals])
                n += 1
    print(f"{n} years -> {out}")


def main(dest: Path) -> None:
    silver_pound(fetch(SILVER, dest))
    allen_cpi(fetch(ALLEN, dest))


if __name__ == "__main__":
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / ".cache" / "finance-study" / "gpih"
    folder.mkdir(parents=True, exist_ok=True)
    main(folder)
