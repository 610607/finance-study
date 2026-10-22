"""Britain off gold: the dollar-sterling rate and prices month by month (January 1929 - December 1936), and Bank Rate
on each day it changed (1929-1936), from the Bank of England's "A millennium of macroeconomic data" (Chapter 29).

    python3 data/fetch/boe_millennium_gb29.py           # download the workbook (27 MB) and write the snapshots
    python3 data/fetch/boe_millennium_gb29.py FILE      # use a copy of the workbook already downloaded

Monthly, January 1929 - December 1936 (data/snapshots/boe_millennium_gb_1929_1936_monthly.csv):
  sheet "M15. Mthly $-£ 1791-2015": the $/£ exchange rate, dollars per pound (Craighead 2010, Federal Reserve
  Board and ONS);
  sheet "M6. Mthly prices and wages": the Sauerbeck-Statist index of all commodities (1867-77 = 100) and the ONS
  monthly cost of living index (July 1914 = 100).
Daily, 1929-1936 (data/snapshots/boe_millennium_bank_rate_1929_1936.csv):
  sheet "D1. Official Interest Rates": 1 January 1929 and every day on which Bank Rate changed, with the new rate.
The columns and headings are those of data/fetch/boe_millennium_gb27.py (Chapter 27's table, which ends in December
1931); the script checks every heading it relies on and fails if one has moved.
"""
from __future__ import annotations

import csv
import hashlib
import sys
import urllib.request
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from boe_millennium_gb27 import D1, M6, M15, MONTHS, URL, UA, check, date_of, number

SNAP = HERE.parent / "snapshots"
OUT_M = SNAP / "boe_millennium_gb_1929_1936_monthly.csv"
OUT_D = SNAP / "boe_millennium_bank_rate_1929_1936.csv"
FIRST, LAST = 1929, 1936
# monthly columns: (sheet, column, [(row, expected start of the heading)], first data row, name in the snapshot)
MONTHLY = [
    (M15, 2, [(0, "M15. $/£ exchange rate 1791-2015"), (3, "$'s per £"),
              (4, "Craighead (2010), Federal Reserve Board and ONS")], 6, "usd_per_gbp"),
    (M6, 7, [(4, "Sauerbeck Statist index, all commodities 1885-1951"), (6, "1867-77=100"), (7, "nsa")], 8,
     "sauerbeck_1867_77_100"),
    (M6, 12, [(2, "Consumer Prices"), (4, "Monthly cost of living index 1914-1947"), (5, "ONS"),
              (6, "July 1914=100")], 8, "cost_of_living_jul1914_100"),
]


def main(path: Path) -> None:
    if not path.exists():
        req = urllib.request.Request(URL, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=300) as r:
            path.write_bytes(r.read())
    print(f"{path.name}: sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}")
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    cache: dict[str, list] = {}

    def rows_of(sheet: str) -> list:
        return cache.setdefault(sheet, list(wb[sheet].iter_rows(values_only=True)))

    keys = [(y, m) for y in range(FIRST, LAST + 1) for m in range(1, 13)]
    monthly: dict[str, dict[tuple[int, int], float]] = {}
    for sheet, col, heads, first, name in MONTHLY:
        rows = rows_of(sheet)
        check(rows, sheet, col, heads)
        s, year = {}, None
        for r in rows[first:]:
            if isinstance(r[0], (int, float)):
                year = int(r[0])
            if year is None or not FIRST <= year <= LAST or r[1] not in MONTHS:
                continue
            v = number(r[col])
            if v is not None:
                s[(year, MONTHS.index(r[1]) + 1)] = v
        missing = [k for k in keys if k not in s]
        if missing:
            raise ValueError(f"{name}: months missing {missing[:5]}")
        monthly[name] = s
    with OUT_M.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "month"] + list(monthly))
        for k in keys:
            w.writerow(list(k) + [round(monthly[n][k], 6) for n in monthly])
    print(f"{len(keys)} months {keys[0]} - {keys[-1]} -> {OUT_M}")
    for n, s in monthly.items():
        print(f"  {n}: {len(s)} values, {min(s.values()):.3f} - {max(s.values()):.3f}")

    rows = rows_of(D1)
    check(rows, D1, 0, [(7, "Date")])
    check(rows, D1, 2, [(3, ("Bank Rate 1833-1972, Minimum Lending Rate 1972-1981, Minimum Band 1 Dealing Rate "
                             "1981-1997, Repo Rate 1997-2006, Bank Rate, 2006-2016"))])
    changes, prev = [], None
    for r in rows[8:]:
        d = date_of(r[0])
        v = number(r[2])
        if d is None or v is None:
            continue
        if FIRST <= d.year <= LAST and (v != prev or not changes):
            changes.append((d.isoformat(), v))
        prev = v
    with OUT_D.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "bank_rate"])
        w.writerows(changes)
    print(f"{len(changes)} rows (the first day of 1929 and every change) -> {OUT_D}")


if __name__ == "__main__":
    default = Path.home() / ".cache" / "finance-study" / "boe" / "a-millennium-of-macroeconomic-data-for-the-uk.xlsx"
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else default
    p.parent.mkdir(parents=True, exist_ok=True)
    main(p)
