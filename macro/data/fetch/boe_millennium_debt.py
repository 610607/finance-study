"""English (British) public debt, revenue, interest payments and interest rates, 1688-1760, from the
Bank of England's "A millennium of macroeconomic data".

    python3 data/fetch/boe_millennium_debt.py           # download the workbook (27 MB) and write the snapshot
    python3 data/fetch/boe_millennium_debt.py FILE      # use a copy of the workbook already downloaded

Sheet "A27. Central govt borrowing" (Mitchell 1988, pp. 575-593; financial years ending at Michaelmas):
total expenditure, of which interest payments, and total receipts (£ m). Sheet "A29. The National Debt"
(par values, £ m, end of financial year): funded debt of Great Britain, unfunded debt (Mitchell 1988), their
sum, the estimated capital value of terminable annuities, the spliced total including that value, and the
spliced total as a per cent of GB nominal GDP (from 1700). Sheet "A31. Interest rates & asset ps": "Yield on
perpetual annuities/consols" (1703-1726 yields on new long-term issues, 1727-1753 yield on 3% perpetual
annuities, then Consols; annual average) and the "Mortgage Interest Rate" (Allen 1988). The script checks
the headings, keeps 1688-1760 and writes data/snapshots/boe_millennium_england_debt.csv. A financial year
"1693/94" is stored as 1693.
"""
from __future__ import annotations

import csv
import hashlib
import sys
import urllib.request
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "snapshots" / "boe_millennium_england_debt.csv"
URL = ("https://www.bankofengland.co.uk/-/media/boe/files/statistics/research-datasets/"
       "a-millennium-of-macroeconomic-data-for-the-uk.xlsx")
UA = "Mozilla/5.0 (X11; Linux x86_64) finance-study data fetch"
FIRST, LAST = 1688, 1760
# (sheet, column, (row, expected heading), name in the snapshot)
COLS = [
    ("A27. Central govt borrowing ", 2, (8, "Total expenditure"), "expenditure_gbp_m"),
    ("A27. Central govt borrowing ", 7, (9, "o/w interest payments"), "interest_gbp_m"),
    ("A27. Central govt borrowing ", 13, (8, "Total receipts"), "receipts_gbp_m"),
    ("A29. The National Debt", 2, (5, "Funded Debt of Great Britain"), "funded_debt_gbp_m"),
    ("A29. The National Debt", 20, (5, "Mitchell (1988)"), "unfunded_debt_gbp_m"),
    ("A29. The National Debt", 23, (4, "Total funded and unfunded debt of the UK"), "total_debt_gbp_m"),
    ("A29. The National Debt", 26, (4, "Estimated capital value of terminable annuities"), "annuities_value_gbp_m"),
    ("A29. The National Debt", 42, (4, "Spliced measure using just debt funded in Great Britain up to 1816"),
     "debt_incl_annuities_gbp_m"),
    ("A29. The National Debt", 43, (4, "as a % of UK nominal GDP according to relevant political boundary"),
     "debt_pct_gdp"),
    ("A31. Interest rates & asset ps ", 19, (4, "Yield on perpetual annuities/consols"), "yield_long_pct"),
    ("A31. Interest rates & asset ps ", 9, (4, "Mortgage Interest Rate"), "mortgage_rate_pct"),
]


def year_of(cell) -> int | None:
    if isinstance(cell, (int, float)):
        return int(cell)
    if isinstance(cell, str) and cell[:4].isdigit():
        return int(cell[:4])
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
    for sheet, col, (row, head), name in COLS:
        rows = sheets.setdefault(sheet, list(wb[sheet].iter_rows(values_only=True)))
        if str(rows[row][col]).strip() != head:
            raise ValueError(f"{sheet}: column {col} row {row} is {rows[row][col]!r}, expected {head!r}")
        s = {}
        for r in rows[row + 1:]:
            y = year_of(r[0])
            if y is not None and FIRST <= y <= LAST and isinstance(r[col], (int, float)):
                s.setdefault(y, float(r[col]))
        data[name] = s
    years = range(FIRST, LAST + 1)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year"] + list(data))
        for y in years:
            w.writerow([y] + ["" if y not in data[k] else round(data[k][y], 6) for k in data])
    print(f"{len(years)} years -> {OUT}")
    for k, s in data.items():
        print(f"  {k}: {min(s)}-{max(s)}, {len(s)} values")


if __name__ == "__main__":
    default = Path.home() / ".cache" / "finance-study" / "boe" / "a-millennium-of-macroeconomic-data-for-the-uk.xlsx"
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else default
    p.parent.mkdir(parents=True, exist_ok=True)
    main(p)
