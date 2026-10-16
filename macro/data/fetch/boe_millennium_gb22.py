"""Britain in the crisis of 1857 and the United Kingdom 1855-1913: Bank Rate, the market rate of discount and
monthly indicators of activity (1855-1859), the dates on which Bank Rate changed (1856-1858), and annual
unemployment, real earnings, factor incomes and the capital stock (1855-1913), from the Bank of England's
"A millennium of macroeconomic data" (Chapter 22).

    python3 data/fetch/boe_millennium_gb22.py           # download the workbook (27 MB) and write the snapshots
    python3 data/fetch/boe_millennium_gb22.py FILE      # use a copy of the workbook already downloaded

Monthly, 1855-1859 (data/snapshots/boe_millennium_gb_1855_1859_monthly.csv):
  sheet "M9. Mthly short-term rates": Bank Rate (end month) and the rate of discount for three-month prime bills
  (Overend Gurney; from June 1857 three-month bankers' bills from the Economist; monthly average of weekly data);
  sheet "M2. Monthly activity 1846+" (Klovland 1998): the unemployment rate of the ironfounders' union and raw
  cotton consumption (average number of bales consumed a week; the sheet gives no unit, the values are about 40,
  so the chapter uses the series only relative to its own earlier level).
Daily, 1856-1858 (data/snapshots/boe_millennium_bank_rate_1856_1858.csv):
  sheet "D1. Official Interest Rates": the days on which Bank Rate changed, and the new rate.
Annual, 1855-1913 (data/snapshots/boe_millennium_uk_1855_1913.csv):
  sheet "A50. Employment & unemployment": the unemployment rate of the unions with unemployment benefit schemes
  (Feinstein 1972 / Board of Trade, adjusted);
  sheet "A48. Real Earnings ": real consumption earnings of Great Britain (1900 = 100);
  sheet "A17. GDP(I) components": Mitchell's (1988) compensation of employees, gross trading profits and
  self-employment income, rent, the gross trading surplus of other public enterprises (from 1889) and GDP(I) at
  factor cost (£ m, current prices; the four components add up to GDP(I));
  sheet "A55. Capital Stock": Feinstein and Pollard's (1988) nominal capital stock of the UK, non-dwellings
  (whole economy) and dwellings (£ m).
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
SNAP = HERE.parent / "snapshots"
OUT_M = SNAP / "boe_millennium_gb_1855_1859_monthly.csv"
OUT_D = SNAP / "boe_millennium_bank_rate_1856_1858.csv"
OUT_A = SNAP / "boe_millennium_uk_1855_1913.csv"
URL = ("https://www.bankofengland.co.uk/-/media/boe/files/statistics/research-datasets/"
       "a-millennium-of-macroeconomic-data-for-the-uk.xlsx")
UA = "Mozilla/5.0 (X11; Linux x86_64) finance-study data fetch"
M_FIRST, M_LAST = 1855, 1859
D_FIRST, D_LAST = 1856, 1858
A_FIRST, A_LAST = 1855, 1913
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
M9, M2, D1 = "M9. Mthly short-term rates", "M2. Monthly activity 1846+", "D1. Official Interest Rates"
A50, A48, A17, A55 = ("A50. Employment & unemployment", "A48. Real Earnings ", "A17. GDP(I) components",
                      "A55. Capital Stock")
# monthly series: (sheet, column, [(row, expected heading)], name in the snapshot, first data row)
MONTHLY = [
    (M9, 2, [(5, "D1. Official rates"), (6, "End month")], "bank_rate", 7),
    (M9, 6, [(4, "Rate of  discount for three month prime or first class bills 1824-1939"),
             (5, "Overend Gurney quoted in 1857 Select Committee on Bank Acts, From June 1857, 3-month Banker's "
                 "Bills from Economist"),
             (6, "Monthly average of weekly data")], "prime_bills_rate", 7),
    (M2, 2, [(3, "UNEMP"), (4, "Unemployment rate (ironfounders July 1854-December 1886, all trades thereafter)")],
     "unemp_ironfounders", 5),
    (M2, 7, [(3, "COTRAR"), (4, "Raw Cotton Consumption, average number of cotton bales consumed per week")],
     "cotton_bales_week", 5),
]
# annual series: (sheet, column, [(row, expected heading)], name in the snapshot, first data row)
ANNUAL = [
    (A50, 16, [(2, "Unemployment rate"),
               (3, "Unemployment rate based on unions that offered unemployment benefit schemes to their members"),
               (4, "Feinstein (1972)/Board of Trade (adjusted)")], "unemp_unions", 5),
    (A48, 1, [(1, "Real Consumption Earnings"), (2, "GB"),
              (3, "Using preferred full employment earnings and CPI series. Traditional measure based on daily wage "
                  "rates in England before 1750, Index 1900=100")], "real_earnings_1900_100", 5),
    (A17, 1, [(2, "Compensation of employees"), (4, "Mitchell(1988), Chapter XVI, Table 4 pages 828 to 830")],
     "employees_gbp_m", 5),
    (A17, 14, [(3, "Gross trading profits and self-employment income"),
               (4, "Mitchell(1988), Chapter XVI, Table 5 pages 828 to 830.")], "profits_selfemp_gbp_m", 5),
    (A17, 38, [(2, "Rents/Gross operating surplus of households"), (3, "Rent"),
               (4, "Mitchell(1988), Chapter XVI, Table 5 pages 831 to 835")], "rent_gbp_m", 5),
    (A17, 31, [(2, None), (3, "Gross trading surplus of other public enterprises")], "public_enterprises_gbp_m", 5),
    (A17, 43, [(2, "GDP(I) at factor cost"),
               (4, "Mitchell(1988), Chapter XVI, Table 5 pages 828 to 830, assumption made about split between Self "
                   "employment and profits 1913-1920")], "gdp_factor_cost_gbp_m", 5),
    (A55, 3, [(3, "Non-dwellings whole economy"), (4, "UK"), (5, "Feinstein and Pollard (1988)")],
     "capital_nondwellings_gbp_m", 6),
    (A55, 5, [(3, "Dwellings"), (4, "UK"), (5, "Feinstein and Pollard (1988)")], "capital_dwellings_gbp_m", 6),
]

# headings that sit in another column (merged cells): (sheet, column, row, expected heading)
SPANNING = [(A55, 1, 2, "Nominal value of capital stock, £mn")]


def year_of(cell) -> int | None:
    if isinstance(cell, (int, float)):
        return int(cell)
    if isinstance(cell, str) and cell[:4].isdigit():
        return int(cell[:4])
    return None


def number(cell) -> float | None:
    if isinstance(cell, (int, float)):
        return float(cell)
    if isinstance(cell, str):
        try:
            return float(cell)
        except ValueError:
            return None
    return None


def check(rows: list, sheet: str, col: int, heads: list[tuple[int, str]]) -> None:
    for row, head in heads:
        if head is None:                       # a cell that must be empty (the column has no heading there)
            if rows[row][col] is not None:
                raise ValueError(f"{sheet}: column {col} row {row} is {rows[row][col]!r}, expected an empty cell")
            continue
        got = str(rows[row][col]).strip()
        if got != head.strip():
            raise ValueError(f"{sheet}: column {col} row {row} is {rows[row][col]!r}, expected {head!r}")


def main(path: Path) -> None:
    if not path.exists():
        req = urllib.request.Request(URL, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=300) as r:
            path.write_bytes(r.read())
    print(f"{path.name}: sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}")
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheets: dict[str, list] = {}

    def rows_of(sheet: str) -> list:
        return sheets.setdefault(sheet, list(wb[sheet].iter_rows(values_only=True)))

    monthly: dict[str, dict[tuple[int, int], float]] = {}
    for sheet, col, heads, name, first in MONTHLY:
        rows = rows_of(sheet)
        check(rows, sheet, col, heads)
        s = {}
        for r in rows[first:]:
            y, v = year_of(r[0]), number(r[col])
            if y is not None and M_FIRST <= y <= M_LAST and r[1] in MONTHS and v is not None:
                s[(y, MONTHS.index(r[1]) + 1)] = v
        monthly[name] = s
    keys = [(y, m) for y in range(M_FIRST, M_LAST + 1) for m in range(1, 13)]
    with OUT_M.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "month"] + list(monthly))
        for k in keys:
            w.writerow(list(k) + ["" if k not in monthly[n] else round(monthly[n][k], 6) for n in monthly])
    print(f"{len(keys)} months -> {OUT_M}")
    for n, s in monthly.items():
        print(f"  {n}: {min(s)}-{max(s)}, {len(s)} values")

    rows = rows_of(D1)
    check(rows, D1, 0, [(7, "Date")])
    check(rows, D1, 2, [(3, "Bank Rate 1833-1972, Minimum Lending Rate 1972-1981, Minimum Band 1 Dealing Rate "
                            "1981-1997, Repo Rate 1997-2006, Bank Rate, 2006-2016")])
    changes, prev = [], None
    for r in rows[8:]:
        if not (isinstance(r[0], str) and len(r[0]) == 10 and r[0][6:].isdigit()):
            continue
        d, mth, y = int(r[0][:2]), int(r[0][3:5]), int(r[0][6:])
        v = number(r[2])
        if v is None:
            continue
        if D_FIRST <= y <= D_LAST and (v != prev or not changes):
            changes.append((f"{y:04d}-{mth:02d}-{d:02d}", v))
        prev = v
    with OUT_D.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "bank_rate"])
        w.writerows(changes)
    print(f"{len(changes)} rows (1 January 1856 and every change) -> {OUT_D}")

    for sheet, col, row, head in SPANNING:
        check(rows_of(sheet), sheet, col, [(row, head)])
    annual: dict[str, dict[int, float]] = {}
    for sheet, col, heads, name, first in ANNUAL:
        rows = rows_of(sheet)
        check(rows, sheet, col, heads)
        s = {}
        for r in rows[first:]:
            y, v = year_of(r[0]), number(r[col])
            if y is not None and A_FIRST <= y <= A_LAST and v is not None:
                s.setdefault(y, v)
        annual[name] = s
    years = range(A_FIRST, A_LAST + 1)
    with OUT_A.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year"] + list(annual))
        for y in years:
            w.writerow([y] + ["" if y not in annual[n] else round(annual[n][y], 6) for n in annual])
    print(f"{len(years)} years -> {OUT_A}")
    for n, s in annual.items():
        print(f"  {n}: {min(s)}-{max(s)}, {len(s)} values")


if __name__ == "__main__":
    default = Path.home() / ".cache" / "finance-study" / "boe" / "a-millennium-of-macroeconomic-data-for-the-uk.xlsx"
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else default
    p.parent.mkdir(parents=True, exist_ok=True)
    main(p)
