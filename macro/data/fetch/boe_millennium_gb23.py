"""The Bank of England under the Bank Charter Act of 1844: the weekly returns of the Issue Department and the
Banking Department (September 1844 - July 1914), Bank Rate on each day it changed (1844-1914) and annual price
indices of the UK and the US (1821-1913), from the Bank of England's "A millennium of macroeconomic data"
(Chapter 23).

    python3 data/fetch/boe_millennium_gb23.py           # download the workbook (27 MB) and write the snapshots
    python3 data/fetch/boe_millennium_gb23.py FILE      # use a copy of the workbook already downloaded

Weekly, 7 September 1844 - 29 July 1914 (data/snapshots/boe_millennium_weekly_1844_1914.csv), £ m:
  sheet "W1. Issue Department": total coin and bullion, o/w gold coin and bullion, o/w silver bullion, the
  fiduciary issue (the notes backed by securities), notes in circulation and notes held by the Banking
  Department;
  sheet "W2. Banking Department": government securities, "discounts, advances and other securities" (with its
  two parts from the sheet, where given), the reserve of notes and coin (o/w gold and silver coin), public
  deposits, other deposits (o/w bankers' deposits).
  The two sheets have one row per weekly return and the same dates; the script checks that they agree.
Daily, 1844-1914 (data/snapshots/boe_millennium_bank_rate_1844_1914.csv):
  sheet "D1. Official Interest Rates": 2 January 1844 and every day on which Bank Rate changed, with the new rate.
Annual, 1821-1913 (data/snapshots/boe_millennium_prices_1821_1913.csv):
  sheet "A47. Wages and prices": the preferred consumer price index of the UK, the spliced wholesale/producer
  price index of GB/UK, and the US CPI (Williamson 2017a).
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
OUT_W = SNAP / "boe_millennium_weekly_1844_1914.csv"
OUT_D = SNAP / "boe_millennium_bank_rate_1844_1914.csv"
OUT_A = SNAP / "boe_millennium_prices_1821_1913.csv"
URL = ("https://www.bankofengland.co.uk/-/media/boe/files/statistics/research-datasets/"
       "a-millennium-of-macroeconomic-data-for-the-uk.xlsx")
UA = "Mozilla/5.0 (X11; Linux x86_64) finance-study data fetch"
W_LAST = dt.date(1914, 7, 31)            # the last return before the war
D_FIRST, D_LAST = 1844, 1914
A_FIRST, A_LAST = 1821, 1913
W1, W2, D1, A47 = ("W1. Issue Department", "W2. Banking Department", "D1. Official Interest Rates",
                   "A47. Wages and prices")
# weekly columns: (sheet, column, headings in rows 4, 5 and 6 (None: empty), name in the snapshot)
WEEKLY = [
    (W1, 1, ("Total Coin", "and Bullion", None), "issue_coin_bullion"),
    (W1, 2, ("o/w", "Gold Coin", "and Bullion"), "issue_gold"),
    (W1, 3, ("o/w", "Silver", "Bullion"), "issue_silver"),
    (W1, 9, ("Memo:", "Fiduciary issue", None), "fiduciary_issue"),
    (W1, 11, (None, "Notes in", "Circulation"), "notes_circulation"),
    (W1, 12, (None, "Notes held by", "the Bank in Banking Department"), "notes_in_banking_dept"),
    (W2, 1, ("Government", "Securities", None), "bd_govt_securities"),
    (W2, 2, ("Discounts, advances", "and other securities", None), "bd_other_securities"),
    (W2, 3, ("o/w", "Discounts", "and Advances"), "bd_discounts_advances"),
    (W2, 4, ("o/w", "Other", "Securities"), "bd_other_sec_other"),
    (W2, 5, ("Reserve of notes", "and coin", None), "bd_reserve"),
    (W2, 7, ("o/w", "Gold and", "Silver Coin"), "bd_coin"),
    (W2, 12, ("Public", "Deposits", None), "public_deposits"),
    (W2, 13, ("Other Deposits", "and Accounts", None), "other_deposits"),
    (W2, 14, ("o/w", "Bankers' Deposits", None), "bankers_deposits"),
]
# annual columns: (sheet, column, [(row, expected heading)], name in the snapshot)
ANNUAL = [
    (A47, 3, [(2, "Consumer Price Index (CPI) -  preferred measure"), (3, "GB/UK(GB+NI)"),
              (5, "Spliced index 2015=100")], "uk_cpi_2015_100"),
    (A47, 8, [(2, "Spliced Wholesale/producer price index"), (3, "GB/UK"), (5, "2010=100")],
     "uk_wholesale_2010_100"),
    (A47, 22, [(2, "US CPI"), (4, "Williamson (2017a)"), (5, "1982-1984=100")], "us_cpi_1982_84_100"),
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


def check(rows: list, sheet: str, col: int, heads: list[tuple[int, str | None]]) -> None:
    for row, head in heads:
        cell = rows[row][col]
        if head is None:                       # a cell that must be empty (the column has no heading there)
            if cell is not None and str(cell).strip():
                raise ValueError(f"{sheet}: column {col} row {row} is {cell!r}, expected an empty cell")
            continue
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

    for sheet in (W1, W2):
        check(rows_of(sheet), sheet, 0, [(6, "Date")])
    check(rows_of(W1), W1, 5, [(2, "Assets")])
    check(rows_of(W2), W2, 4, [(2, "Assets")])
    for sheet in (W1, W2):
        check(rows_of(sheet), sheet, 0, [(2, "£ millions")])
    # the two sheets have one row per return, in the same order; the rows are paired by position
    dates: dict[str, list[dt.date]] = {}
    for sheet in (W1, W2):
        dates[sheet] = [d for d in (date_of(r[0]) for r in rows_of(sheet)[7:]) if d is not None and d <= W_LAST]
    if len(dates[W1]) != len(dates[W2]):
        raise ValueError("W1 and W2 do not have the same number of weekly returns")
    for a, b in zip(dates[W1], dates[W2]):
        if a != b:
            if abs((a - b).days) > 3:
                raise ValueError(f"W1 dates a return {a}, W2 the same return {b}")
            print(f"  W1 dates a return {a}, W2 {b}: the snapshot uses W1's date")
    weekly: dict[str, list[float | None]] = {}
    for sheet, col, heads, name in WEEKLY:
        rows = rows_of(sheet)
        check(rows, sheet, col, [(4, heads[0]), (5, heads[1]), (6, heads[2])])
        weekly[name] = [number(r[col]) for r in rows[7:] if (d := date_of(r[0])) is not None and d <= W_LAST]
    keys = dates[W1]
    with OUT_W.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date"] + list(weekly))
        for i, k in enumerate(keys):
            w.writerow([k.isoformat()] + ["" if weekly[n][i] is None else round(weekly[n][i], 6) for n in weekly])
    print(f"{len(keys)} weekly returns {keys[0]} - {keys[-1]} -> {OUT_W}")
    for n, s in weekly.items():
        got = [k for k, v in zip(keys, s) if v is not None]
        print(f"  {n}: {got[0]} - {got[-1]}, {len(got)} values")

    rows = rows_of(D1)
    check(rows, D1, 0, [(7, "Date")])
    check(rows, D1, 2, [(3, "Bank Rate 1833-1972, Minimum Lending Rate 1972-1981, Minimum Band 1 Dealing Rate "
                            "1981-1997, Repo Rate 1997-2006, Bank Rate, 2006-2016")])
    changes, prev = [], None
    for r in rows[8:]:
        d = date_of(r[0])
        v = number(r[2])
        if d is None or v is None:
            continue
        if D_FIRST <= d.year <= D_LAST and (v != prev or not changes):
            changes.append((d.isoformat(), v))
        prev = v
    with OUT_D.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "bank_rate"])
        w.writerows(changes)
    print(f"{len(changes)} rows (the first day of 1844 and every change) -> {OUT_D}")

    annual: dict[str, dict[int, float]] = {}
    for sheet, col, heads, name in ANNUAL:
        rows = rows_of(sheet)
        check(rows, sheet, col, heads)
        s = {}
        for r in rows[6:]:
            y, v = r[0], number(r[col])
            if isinstance(y, (int, float)) and A_FIRST <= int(y) <= A_LAST and v is not None:
                s.setdefault(int(y), v)
        annual[name] = s
    years = range(A_FIRST, A_LAST + 1)
    with OUT_A.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year"] + list(annual))
        for y in years:
            w.writerow([y] + ["" if y not in annual[n] else round(annual[n][y], 6) for n in annual])
    print(f"{len(years)} years -> {OUT_A}")
    for n, s in annual.items():
        print(f"  {n}: {min(s)} - {max(s)}, {len(s)} values")


if __name__ == "__main__":
    default = Path.home() / ".cache" / "finance-study" / "boe" / "a-millennium-of-macroeconomic-data-for-the-uk.xlsx"
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else default
    p.parent.mkdir(parents=True, exist_ok=True)
    main(p)
