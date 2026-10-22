"""Britain between the wars: the dollar-sterling rate, prices, wages and unemployment month by month (July 1914 -
December 1931), and Bank Rate on each day it changed (1919-1931), from the Bank of England's "A millennium of
macroeconomic data" (Chapter 27).

    python3 data/fetch/boe_millennium_gb27.py           # download the workbook (27 MB) and write the snapshots
    python3 data/fetch/boe_millennium_gb27.py FILE      # use a copy of the workbook already downloaded

Monthly, July 1914 - December 1931 (data/snapshots/boe_millennium_interwar_monthly.csv):
  sheet "M15. Mthly $-£ 1791-2015": the $/£ exchange rate, dollars per pound (Craighead 2010, Federal Reserve
  Board and ONS);
  sheet "M6. Mthly prices and wages": the Sauerbeck-Statist index of all commodities (1867-77 = 100), the ONS
  monthly cost of living index (July 1914 = 100), and Capie and Collins's index of weekly wage rates (1919-1925)
  spliced with average weekly wages (1925-1939), January 1939 = 100, not seasonally adjusted (from January 1919);
  sheet "M5. Administrative unemp 1881+": the administrative unemployment rate, per cent, as Denman and Macdonald
  (1996) give it (some months are empty), and the sheet's seasonally adjusted and interpolated series.
Daily, 1919-1931 (data/snapshots/boe_millennium_bank_rate_1919_1931.csv):
  sheet "D1. Official Interest Rates": 1 January 1919 and every day on which Bank Rate changed, with the new rate.
Annual, 1913-1931 (data/snapshots/boe_millennium_prices_1913_1931.csv):
  sheet "A47. Wages and prices": the preferred consumer price index of the UK, the spliced wholesale/producer
  price index of GB/UK, and the US CPI (Williamson 2017a), the same columns as Chapter 23's 1821-1913 table.
The script checks every heading it relies on and fails if one has moved.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import sys
import urllib.request
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
SNAP = HERE.parent / "snapshots"
OUT_M = SNAP / "boe_millennium_interwar_monthly.csv"
OUT_D = SNAP / "boe_millennium_bank_rate_1919_1931.csv"
OUT_A = SNAP / "boe_millennium_prices_1913_1931.csv"
URL = ("https://www.bankofengland.co.uk/-/media/boe/files/statistics/research-datasets/"
       "a-millennium-of-macroeconomic-data-for-the-uk.xlsx")
UA = "Mozilla/5.0 (X11; Linux x86_64) finance-study data fetch"
FIRST, LAST = 1919, 1931                 # Bank Rate; the wage index begins in January 1919
START = (1914, 7)                        # the monthly table begins with the last month before the war
M15, M6, M5, D1, A47 = ("M15. Mthly $-£ 1791-2015", "M6. Mthly prices and wages", "M5. Administrative unemp 1881+",
                        "D1. Official Interest Rates", "A47. Wages and prices")
ANNUAL_YEARS = (1913, 1931)
# annual columns of A47 (heading rows 2-5, data from row 6), as in data/fetch/boe_millennium_gb23.py
ANNUAL = [
    (3, [(2, "Consumer Price Index (CPI) -  preferred measure"), (3, "GB/UK(GB+NI)"), (5, "Spliced index 2015=100")],
     "uk_cpi_2015_100"),
    (8, [(2, "Spliced Wholesale/producer price index"), (3, "GB/UK"), (5, "2010=100")], "uk_wholesale_2010_100"),
    (22, [(2, "US CPI"), (4, "Williamson (2017a)"), (5, "1982-1984=100")], "us_cpi_1982_84_100"),
]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
# monthly columns: (sheet, column, [(row, expected start of the heading)], first data row, name in the snapshot)
MONTHLY = [
    (M15, 2, [(0, "M15. $/£ exchange rate 1791-2015"), (3, "$'s per £"),
              (4, "Craighead (2010), Federal Reserve Board and ONS")], 6, "usd_per_gbp"),
    (M6, 7, [(4, "Sauerbeck Statist index, all commodities 1885-1951"), (6, "1867-77=100"), (7, "nsa")], 8,
     "sauerbeck_1867_77_100"),
    (M6, 12, [(2, "Consumer Prices"), (4, "Monthly cost of living index 1914-1947"), (5, "ONS"),
              (6, "July 1914=100")], 8, "cost_of_living_jul1914_100"),
    (M6, 20, [(2, "Average weekly earnings"), (4, "Index of 11 Weekly Wage Rates 1919-1925; Average Weekly Wage"),
              (5, "Capie and Collins (1983) Tables 4.1 and 4.2"), (6, "Jan 1939=100"), (7, "nsa")], 8,
     "wages_jan1939_100"),
    (M5, 2, [(2, "Unemployment"), (4, "Source: Tables 1 and 2 of Denman, J and Macdonald, P (1996)"),
             (6, "Administrative unemployment rates"), (7, "%")], 8, "unemp_admin"),
    (M5, 3, [(6, "seasonally-adjusted and interpolated"), (7, "%")], 8, "unemp_sa"),
]


def number(cell) -> float | None:
    if isinstance(cell, (int, float)):
        return float(cell)
    if isinstance(cell, str):
        try:
            return float(cell)
        except ValueError:
            return None
    return None


def date_of(cell) -> dt.date | None:
    if isinstance(cell, dt.datetime):
        return cell.date()
    if isinstance(cell, str):
        parts = cell.strip().split("/")
        if len(parts) == 3 and all(p.isdigit() for p in parts):
            d, m, y = map(int, parts)
            return dt.date(y, m, d)
    return None


def check(rows, sheet: str, col: int, heads) -> None:
    for row, head in heads:
        cell = str(rows[row][col]).strip()
        if not cell.startswith(head):
            raise ValueError(f"{sheet}: column {col} row {row} is {cell!r}, expected {head!r}")


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

    keys = [(y, m) for y in range(START[0], LAST + 1) for m in range(1, 13) if (y, m) >= START]
    monthly: dict[str, dict[tuple[int, int], float]] = {}
    for sheet, col, heads, first, name in MONTHLY:
        rows = rows_of(sheet)
        check(rows, sheet, col, heads)
        s, year = {}, None
        for r in rows[first:]:
            if isinstance(r[0], (int, float)):
                year = int(r[0])                       # M5 gives the year only in January
            if year is None or not START[0] <= year <= LAST or r[1] not in MONTHS:
                continue
            if (year, MONTHS.index(r[1]) + 1) < START:
                continue
            v = number(r[col])
            if v is not None:
                s[(year, MONTHS.index(r[1]) + 1)] = v
        monthly[name] = s
    for name in ("usd_per_gbp", "sauerbeck_1867_77_100", "cost_of_living_jul1914_100", "wages_jan1939_100",
                 "unemp_sa"):
        missing = [k for k in keys if k not in monthly[name] and (name != "wages_jan1939_100" or k[0] >= FIRST)]
        if missing:
            raise ValueError(f"{name}: months missing {missing[:5]}")
    with OUT_M.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "month"] + list(monthly))
        for k in keys:
            w.writerow(list(k) + ["" if k not in monthly[n] else round(monthly[n][k], 6) for n in monthly])
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
    print(f"{len(changes)} rows (the first day of 1919 and every change) -> {OUT_D}")

    rows = rows_of(A47)
    table = {}
    for col, heads, name in ANNUAL:
        check(rows, A47, col, heads)
        for r in rows[6:]:
            y = number(r[0])
            if y is not None and ANNUAL_YEARS[0] <= y <= ANNUAL_YEARS[1]:
                v = number(r[col])
                if v is None:
                    raise ValueError(f"{name}: no value for {int(y)}")
                table.setdefault(int(y), {})[name] = v
    years = list(range(ANNUAL_YEARS[0], ANNUAL_YEARS[1] + 1))
    assert sorted(table) == years
    with OUT_A.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year"] + [n for _, _, n in ANNUAL])
        for y in years:
            w.writerow([y] + [round(table[y][n], 6) for _, _, n in ANNUAL])
    print(f"{len(years)} years -> {OUT_A}")


if __name__ == "__main__":
    default = Path.home() / ".cache" / "finance-study" / "boe" / "a-millennium-of-macroeconomic-data-for-the-uk.xlsx"
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else default
    p.parent.mkdir(parents=True, exist_ok=True)
    main(p)
