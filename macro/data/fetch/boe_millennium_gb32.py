"""Britain's slump and recovery, 1919-1938: unemployment month by month and year by year, output, consumption,
investment and trade, and Bank Rate on each day it changed (1929-1939), from the Bank of England's "A millennium of
macroeconomic data" (Chapter 32).

    python3 data/fetch/boe_millennium_gb32.py           # download the workbook (27 MB) and write the snapshots
    python3 data/fetch/boe_millennium_gb32.py FILE      # use a copy of the workbook already downloaded

Monthly, January 1919 - December 1938 (data/snapshots/boe_millennium_unemp_1919_1938_monthly.csv):
  sheet "M5. Administrative unemp 1881+": the administrative unemployment rate, per cent, as Denman and Macdonald
  (1996) give it (some months of 1919 and 1920 are empty), and the sheet's seasonally adjusted and interpolated
  series; the columns and headings of data/fetch/boe_millennium_gb27.py, whose table ends in December 1931.
Annual, 1919-1938 (data/snapshots/boe_millennium_gb_1919_1938.csv):
  sheet "A1. Headline series": real GDP at market prices, real consumption, real investment, export and import
  volumes (GBP million, chained volumes at 2013 prices);
  sheet "A50. Employment & unemployment": Feinstein's (1972) unemployed (thousands) and unemployment rates, as a per
  cent of the civilian working population and of the civilian working population minus the self-employed (UK excluding
  southern Ireland, from 1920).
Daily, 1929-1939 (data/snapshots/boe_millennium_bank_rate_1929_1939.csv):
  sheet "D1. Official Interest Rates": 1 January 1929 and every day on which Bank Rate changed, with the new rate.
The script checks every heading it relies on and fails if one has moved. CSV files are written with LF line ends.
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
from boe_millennium_gb27 import D1, M5, MONTHS, URL, UA, check, date_of, number

SNAP = HERE.parent / "snapshots"
OUT_M = SNAP / "boe_millennium_unemp_1919_1938_monthly.csv"
OUT_A = SNAP / "boe_millennium_gb_1919_1938.csv"
OUT_D = SNAP / "boe_millennium_bank_rate_1929_1939.csv"
FIRST, LAST = 1919, 1938
RATE_YEARS = (1929, 1939)
A1, A50 = "A1. Headline series", "A50. Employment & unemployment"
# monthly columns of M5 (heading rows 2-7, data from row 8), as in data/fetch/boe_millennium_gb27.py
MONTHLY = [
    (2, [(2, "Unemployment"), (4, "Source: Tables 1 and 2 of Denman, J and Macdonald, P (1996)"),
         (6, "Administrative unemployment rates"), (7, "%")], "unemp_admin"),
    (3, [(6, "seasonally-adjusted and interpolated"), (7, "%")], "unemp_sa"),
]
# annual columns: (sheet, column, [(row, expected start of the heading)], first data row, first year, name)
ANNUAL = [
    (A1, 1, [(3, "Real UK GDP at market prices, geographically-consistent estimate based on post-1922 borders"),
             (4, "A8. Real GDP (A) 1700-2015"), (5, "£mn, Chained Volume measure, 2013 prices")], 7, 1919,
     "real_gdp_gbp_mn_2013"),
    (A1, 15, [(3, "Real consumption"), (4, "A12. GDP(E) - volumes"), (5, "£mn, Chained Volume measure, 2013 prices"),
              (6, "Composite measure")], 7, 1919, "real_consumption_gbp_mn_2013"),
    (A1, 16, [(3, "Real investment"), (4, "A12. GDP(E) - volumes"), (5, "£mn, Chained Volume measure, 2013 prices"),
              (6, "Composite measure")], 7, 1919, "real_investment_gbp_mn_2013"),
    (A1, 19, [(3, "Export volumes"), (4, "A35. Trade volumes"), (5, "£mn, Chained Volume measure, 2013 prices")], 7,
     1919, "exports_gbp_mn_2013"),
    (A1, 20, [(3, "Import volumes"), (4, "A35. Trade volumes"), (5, "£mn, Chained Volume measure, 2013 prices")], 7,
     1919, "imports_gbp_mn_2013"),
    (A50, 45, [(2, "Unemployed"), (4, "Feinstein(1972)")], 5, 1920,
     "unemployed_000"),
    (A50, 46, [(2, "Unemployment rate"), (3, "defined as % of civilian working population"), (4, "Feinstein(1972)")],
     5, 1920, "unemp_rate_civilian"),
    (A50, 47, [(3, "defined as % of civilian working population minus self emplo"),
               (4, "Feinstein(1972) Table 58/Boyer and Hatton (2002)")], 5, 1920, "unemp_rate_employees"),
]


def write(path: Path, header: list[str], rows: list[list]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


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

    # monthly unemployment
    keys = [(y, m) for y in range(FIRST, LAST + 1) for m in range(1, 13)]
    rows = rows_of(M5)
    monthly: dict[str, dict[tuple[int, int], float]] = {}
    for col, heads, name in MONTHLY:
        check(rows, M5, col, heads)
        s, year = {}, None
        for r in rows[8:]:
            if isinstance(r[0], (int, float)):
                year = int(r[0])                       # M5 gives the year only in January
            if year is None or not FIRST <= year <= LAST or r[1] not in MONTHS:
                continue
            v = number(r[col])
            if v is not None:
                s[(year, MONTHS.index(r[1]) + 1)] = v
        monthly[name] = s
    missing = [k for k in keys if k not in monthly["unemp_admin"]]
    assert all(k[0] <= 1920 for k in missing), missing                     # only 1919-1920 have gaps
    assert all(k in monthly["unemp_sa"] for k in keys)
    write(OUT_M, ["year", "month"] + list(monthly),
          [list(k) + ["" if k not in monthly[n] else round(monthly[n][k], 6) for n in monthly] for k in keys])
    print(f"{len(keys)} months {keys[0]} - {keys[-1]} -> {OUT_M} (unemp_admin empty in {len(missing)} months)")

    # annual series
    check(rows_of(A50), A50, 36, [(1, "UK excl. S Ireland 1920-1965")])     # the block of columns 36-47
    years = list(range(FIRST, LAST + 1))
    table: dict[int, dict[str, float]] = {y: {} for y in years}
    for sheet, col, heads, first, start, name in ANNUAL:
        rows = rows_of(sheet)
        check(rows, sheet, col, heads)
        for r in rows[first:]:
            y = number(r[0])
            if y is None or not start <= y <= LAST:
                continue
            v = number(r[col])
            if v is None:
                raise ValueError(f"{name}: no value for {int(y)}")
            table[int(y)][name] = v
        assert all(name in table[y] for y in years if y >= start), name
    names = [a[-1] for a in ANNUAL]
    write(OUT_A, ["year"] + names,
          [[y] + ["" if n not in table[y] else round(table[y][n], 6) for n in names] for y in years])
    print(f"{len(years)} years {FIRST} - {LAST} -> {OUT_A}")

    # Bank Rate
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
        if RATE_YEARS[0] <= d.year <= RATE_YEARS[1] and (v != prev or not changes):
            changes.append([d.isoformat(), v])
        prev = v
    write(OUT_D, ["date", "bank_rate"], changes)
    print(f"{len(changes)} rows (the first day of {RATE_YEARS[0]} and every change) -> {OUT_D}")


if __name__ == "__main__":
    default = Path.home() / ".cache" / "finance-study" / "boe" / "a-millennium-of-macroeconomic-data-for-the-uk.xlsx"
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else default
    p.parent.mkdir(parents=True, exist_ok=True)
    main(p)
