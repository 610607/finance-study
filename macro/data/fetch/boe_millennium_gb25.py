"""Gibson's paradox in the British data: the yield on consols, Bank Rate and the price level, annual, 1821-1913,
from the Bank of England's "A millennium of macroeconomic data" (Chapter 25).

    python3 data/fetch/boe_millennium_gb25.py           # download the workbook (27 MB) and write the snapshot
    python3 data/fetch/boe_millennium_gb25.py FILE      # use a copy of the workbook already downloaded

Annual, 1821-1913 (data/snapshots/boe_millennium_gibson_1821_1913.csv):
  sheet "A31. Interest rates & asset ps " (the sheet name ends with a space):
    "Yield on perpetual annuities/consols" (annual average; 1756-2015 the yield on Consols, with Klovland's
    adjustment for 1888-1903, as the sheet's documentation row says);
    "Bank Rate", end-year observation and annual average;
  sheet "A47. Wages and prices":
    "Spliced Wholesale/producer price index", GB/UK, 2010 = 100 (the annual average of the spliced monthly index of
    sheet M6, whose ratio to its components shows the splices: Gayer, Rostow and Schwartz's index of domestic and
    imported commodities to 1844, the Sauerbeck-Statist index excluding duty (Klovland 1993) for 1845-1884, and the
    Sauerbeck-Statist index of all commodities from 1885);
    "Consumer Price Index (CPI) - preferred measure", GB/UK, 2015 = 100.
The script checks every heading it relies on and fails if one has moved.
"""
from __future__ import annotations

import csv
import hashlib
import sys
import urllib.request
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "snapshots" / "boe_millennium_gibson_1821_1913.csv"
URL = ("https://www.bankofengland.co.uk/-/media/boe/files/statistics/research-datasets/"
       "a-millennium-of-macroeconomic-data-for-the-uk.xlsx")
UA = "finance-study-textbook-check/1.0"
FIRST, LAST = 1821, 1913
A31, A47 = "A31. Interest rates & asset ps ", "A47. Wages and prices"
# (sheet, column, [(row index, expected heading or the start of it)], name in the snapshot); rows are 0-based
COLUMNS = [
    (A31, 19, [(4, "Yield on perpetual annuities/consols"), (6, "M10. Monthly rates sheet")], "consol_yield"),
    (A31, 1, [(4, "Bank Rate"), (5, "Bank Rate 1694-1972"), (6, "M9. Monthly rates sheet")], "bank_rate_end"),
    (A31, 2, [(5, "Bank Rate 1694-1972"), (6, "M9. Monthly rates sheet")], "bank_rate_avg"),
    (A47, 8, [(2, "Spliced Wholesale/producer price index"), (3, "GB/UK"), (5, "2010=100")],
     "uk_wholesale_2010_100"),
    (A47, 3, [(2, "Consumer Price Index (CPI) -  preferred measure"), (3, "GB/UK(GB+NI)"),
              (5, "Spliced index 2015=100")], "uk_cpi_2015_100"),
]
# words that must be in the documentation cells (row index 5) of A31: what the column measures
DOCS = {19: ["1756-2015 yield on Consols", "Annual average", "Klovland"], 1: ["End year observation"],
        2: ["Annual average observation"]}


def number(cell) -> float | None:
    if isinstance(cell, (int, float)):
        return float(cell)
    if isinstance(cell, str):
        try:
            return float(cell)
        except ValueError:
            return None
    return None


def main(path: Path) -> None:
    if not path.exists():
        req = urllib.request.Request(URL, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=300) as r:
            path.write_bytes(r.read())
    print(f"{path.name}: sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}")
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheets: dict[str, list] = {}
    data: dict[str, dict[int, float]] = {}
    for sheet, col, heads, name in COLUMNS:
        rows = sheets.setdefault(sheet, list(wb[sheet].iter_rows(values_only=True)))
        for row, head in heads:
            cell = str(rows[row][col]).strip()
            if not cell.startswith(head):
                raise ValueError(f"{sheet}: column {col} row {row} is {cell!r}, expected {head!r}")
        if sheet == A31:
            for words in DOCS[col]:
                if words not in str(rows[5][col]):
                    raise ValueError(f"{sheet}: the documentation of column {col} does not say {words!r}")
        s = {}
        for r in rows[6:]:
            y, v = r[0], number(r[col])
            if isinstance(y, (int, float)) and FIRST <= int(y) <= LAST and v is not None:
                s.setdefault(int(y), v)
        if sorted(s) != list(range(FIRST, LAST + 1)):
            raise ValueError(f"{name}: years missing")
        data[name] = s
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year"] + list(data))
        for y in range(FIRST, LAST + 1):
            w.writerow([y] + [round(data[n][y], 6) for n in data])
    print(f"{LAST - FIRST + 1} years -> {OUT}")
    for n, s in data.items():
        print(f"  {n}: {min(s.values()):.3f} - {max(s.values()):.3f}")


if __name__ == "__main__":
    default = Path.home() / ".cache" / "finance-study" / "boe" / "a-millennium-of-macroeconomic-data-for-the-uk.xlsx"
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else default
    p.parent.mkdir(parents=True, exist_ok=True)
    main(p)
