"""Britain as the lender of the first globalization: the current account, net external assets, nominal GDP and
the yield on consols, annual, 1850-1913, and Bank Rate on each day it changed, 1888-1892, from the Bank of
England's "A millennium of macroeconomic data" (Chapter 24).

    python3 data/fetch/boe_millennium_gb24.py           # download the workbook (27 MB) and write the snapshots
    python3 data/fetch/boe_millennium_gb24.py FILE      # use a copy of the workbook already downloaded

Annual, 1850-1913 (data/snapshots/boe_millennium_external_1850_1913.csv), £ m unless stated:
  sheet "A46. Net external assets": column 2, headed "Current account deficit including non-monetary bullion
  flows" (Mitchell 1988 for 1816-1920, from Imlah); the values are positive in the years in which Britain
  lent abroad, and column 3, "UK Net external assets" (Imlah's estimate for 1815, followed by cumulation of
  the current account), grows by exactly them, so the snapshot calls the column the surplus (ca_surplus);
  sheet "A9. Nominal GDP (A)": nominal UK GDP, headline measure at market prices (column 3);
  sheet "A31. Interest rates & asset ps ": the yield on perpetual annuities/consols, per cent (column 19).
Daily, 1888-1892 (data/snapshots/boe_millennium_bank_rate_1888_1892.csv):
  sheet "D1. Official Interest Rates": the last rate of 1887 and every day on which Bank Rate changed.
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
OUT_A = SNAP / "boe_millennium_external_1850_1913.csv"
OUT_D = SNAP / "boe_millennium_bank_rate_1888_1892.csv"
URL = ("https://www.bankofengland.co.uk/-/media/boe/files/statistics/research-datasets/"
       "a-millennium-of-macroeconomic-data-for-the-uk.xlsx")
UA = "Mozilla/5.0 (X11; Linux x86_64) finance-study data fetch"
A_FIRST, A_LAST = 1850, 1913
D_FIRST, D_LAST = 1888, 1892
A46, A9, A31, D1 = ("A46. Net external assets", "A9. Nominal GDP (A)", "A31. Interest rates & asset ps ",
                    "D1. Official Interest Rates")
# annual columns: (sheet, column, [(row, expected heading)], first data row, name in the snapshot)
ANNUAL = [
    (A46, 2, [(4, "Current account deficit including non-monetary bullion flows")], 7, "ca_surplus"),
    (A46, 3, [(4, "UK Net external assets")], 7, "net_external_assets"),
    (A9, 3, [(4, "Market prices")], 5, "gdp_market_prices"),
    (A31, 19, [(4, "Yield on perpetual annuities/consols")], 7, "consol_yield"),
]


def date_of(cell) -> dt.date | None:
    if isinstance(cell, dt.datetime):
        return cell.date()
    if isinstance(cell, str):
        parts = cell.strip().split("/")
        if len(parts) == 3 and all(p.isdigit() for p in parts):
            d, m, y = (int(p) for p in parts)
            return dt.date(y, m, d)
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


def year_of(cell) -> int | None:
    v = number(cell)
    return int(v) if v is not None and v == int(v) else None


def check(rows: list, sheet: str, col: int, heads: list[tuple[int, str]]) -> None:
    for row, head in heads:
        cell = rows[row][col]
        if str(cell).strip() != head.strip():
            raise ValueError(f"{sheet}: column {col} row {row} is {cell!r}, expected {head!r}")


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

    check(rows_of(A46), A46, 0, [(4, "All values £mn unless otherwise stated")])
    check(rows_of(A31), A31, 0, [(3, "% unless otherwise stated")])
    check(rows_of(A9), A9, 1, [(3, "Nominal UK GDP - headline  measure based on current definition of GB + "
                                   "Northern Ireland")])
    annual: dict[str, dict[int, float]] = {}
    for sheet, col, heads, first, name in ANNUAL:
        rows = rows_of(sheet)
        check(rows, sheet, col, heads)
        s: dict[int, float] = {}
        for r in rows[first:]:
            y, v = year_of(r[0]), number(r[col])
            if y is not None and A_FIRST <= y <= A_LAST and v is not None:
                s.setdefault(y, v)
        missing = [y for y in range(A_FIRST, A_LAST + 1) if y not in s]
        if missing:
            raise ValueError(f"{sheet}: column {col} has no value for {missing}")
        annual[name] = s
    # the surplus reading of A46 column 2: net external assets grow by it
    for y in range(A_FIRST + 1, A_LAST + 1):
        step = annual["net_external_assets"][y] - annual["net_external_assets"][y - 1]
        if abs(step - annual["ca_surplus"][y]) > 0.05:
            raise ValueError(f"A46 {y}: net external assets grow by {step:.1f}, column 2 is "
                             f"{annual['ca_surplus'][y]:.1f}")
    with OUT_A.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year"] + list(annual))
        for y in range(A_FIRST, A_LAST + 1):
            w.writerow([y] + [round(annual[n][y], 6) for n in annual])
    print(f"{A_LAST - A_FIRST + 1} years -> {OUT_A}")

    rows = rows_of(D1)
    check(rows, D1, 0, [(7, "Date")])
    check(rows, D1, 2, [(3, "Bank Rate 1833-1972, Minimum Lending Rate 1972-1981, Minimum Band 1 Dealing Rate "
                            "1981-1997, Repo Rate 1997-2006, Bank Rate, 2006-2016")])
    changes, prev, last_before = [], None, None
    for r in rows[8:]:
        d, v = date_of(r[0]), number(r[2])
        if d is None or v is None:
            continue
        if d.year < D_FIRST:
            last_before = (d, v)
        elif d.year <= D_LAST and v != prev:
            changes.append((d.isoformat(), v))
        prev = v
    if last_before is None:
        raise ValueError("D1: no rate before 1888")
    with OUT_D.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "bank_rate"])
        w.writerow([last_before[0].isoformat(), last_before[1]])
        w.writerows(changes)
    print(f"{len(changes) + 1} rows (the last rate of 1887 and every change) -> {OUT_D}")


if __name__ == "__main__":
    default = Path.home() / ".cache" / "finance-study" / "boe" / "a-millennium-of-macroeconomic-data-for-the-uk.xlsx"
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else default
    p.parent.mkdir(parents=True, exist_ok=True)
    main(p)
