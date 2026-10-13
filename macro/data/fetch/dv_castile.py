"""Castile's fiscal accounts under Philip II, 1566-1596, from the dataset of Drelichman & Voth (2010).

    python3 data/fetch/dv_castile.py          # download the workbook and write the snapshot
    python3 data/fetch/dv_castile.py FILE     # use a copy already downloaded

The workbook "excel_article_mauricio-drelichman-dataset-sustainable-debt.xls" (author's page, University
of British Columbia) holds the data behind M. Drelichman and H.-J. Voth, "The Sustainable Debts of
Philip II: A Reconstruction of Castile's Fiscal Position, 1566-1596", Journal of Economic History 70(4),
2010. Two sheets are read:
  "Revenues"         revenue by source, 1555-1596; the column "Indies" (the Crown's American silver) and
                     the "Total" are kept;
  "Fiscal accuonts"  [sic] revenue, military and non-military expenditure, primary surplus, long- and
                     short-term debt service, fiscal balance and outstanding debt; the rows carry no year,
                     so the script matches each row's revenue to the "Total" of the Revenues sheet for
                     1566, 1567, ... 1596 and stops if any year disagrees.
All figures are millions of current ducats. Writes data/snapshots/dv2010_castile_annual.csv; the .xls
needs the xlrd package.
"""
from __future__ import annotations

import csv
import hashlib
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "snapshots" / "dv2010_castile_annual.csv"
URL = ("https://econ.sites.olt.ubc.ca/files/2013/05/"
       "excel_article_mauricio-drelichman-dataset-sustainable-debt.xls")
UA = "Mozilla/5.0 (X11; Linux x86_64) finance-study data fetch"
FIRST, LAST = 1566, 1596
ACCOUNTS = ["Revenue", "Military expenditure", "Non-military expenditure", "Primary surplus",
            "Long-term debt service", "Short-term debt service", "Fiscal balannce", "Outstanding debt"]
NAMES = ["revenue", "military", "nonmilitary", "primary_surplus", "lt_debt_service", "st_debt_service",
         "fiscal_balance", "debt"]


def main(path: Path) -> None:
    import xlrd
    if not path.exists():
        req = urllib.request.Request(URL, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=120) as r:
            path.write_bytes(r.read())
    print(f"{path.name}: sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}")
    book = xlrd.open_workbook(str(path))
    rev = book.sheet_by_name("Revenues")
    head = [str(v).strip() for v in rev.row_values(2)]
    if head[0] != "Year" or head[8] != "Indies" or head[9] != "Total":
        raise ValueError(f"Revenues: unexpected headings {head}")
    by_year = {int(r[0]): (r[8], r[9]) for r in (rev.row_values(i) for i in range(3, rev.nrows))
               if isinstance(r[0], float)}
    acc = book.sheet_by_name("Fiscal accuonts")
    if [str(v).strip() for v in acc.row_values(3)] != ACCOUNTS:
        raise ValueError(f"Fiscal accounts: unexpected headings {acc.row_values(3)}")
    rows = [acc.row_values(i) for i in range(4, 4 + LAST - FIRST + 1)]
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "indies"] + NAMES)
        for year, r in zip(range(FIRST, LAST + 1), rows):
            indies, total = by_year[year]
            if abs(r[0] - total) > 1e-9:
                raise ValueError(f"{year}: revenue {r[0]} in the accounts, {total} in the Revenues sheet")
            w.writerow([year, round(indies, 4)] + [round(v, 4) for v in r])
    print(f"{LAST - FIRST + 1} years -> {OUT}")


if __name__ == "__main__":
    default = Path.home() / ".cache" / "finance-study" / "dv" / "dataset-sustainable-debt.xls"
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else default
    p.parent.mkdir(parents=True, exist_ok=True)
    main(p)
