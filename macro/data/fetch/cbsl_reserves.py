"""Sri Lanka's official reserve assets, monthly, from the Central Bank of Sri Lanka's reserve data template
("Reserve Data Template - Historical", table 2.15.2 of its external-sector statistics), for Chapter 5.

    python3 data/fetch/cbsl_reserves.py            # download the workbook and write the snapshot
    python3 data/fetch/cbsl_reserves.py FILE       # use a saved copy of the workbook

The workbook has one sheet per month (November 2013 onward) in the IMF/SDDS template "International
Reserves/Foreign Currency Liquidity". From each sheet the script reads, in US$ million:
  official_reserve_assets  line A, "Official reserve assets" (gross official reserves; from June 2015, the
                           earlier sheets have only line 1)
  fx_reserves              line A(1), "Foreign currency reserves (in convertible foreign currencies)"
  gold                     line A(4), "Gold (including gold deposits ...)"
and from the country notes under the sheet
  pboc_swap_note           1 if the notes say the reserves include the PBOC swap "which is subject to conditionalities
                           on usability" (March 2022 onward), else 0
  pboc_swap_bn             the amount in "This includes proceeds from the PBOC swap equivalent to around US dollars
                           X billion, which is subject to conditionalities on usability" (US$ billion; empty when the
                           note gives no amount: from March 2024 it says only "the PBOC swap arrangement")
  gor_months               "gross official reserves were equivalent to X months of imports" (empty when absent)
Writes data/snapshots/cbsl_reserves.csv and prints the SHA-256 of the workbook. The CBSL publishes the file on
https://www.cbsl.gov.lk/en/statistics/statistical-tables/external-sector; its file name carries the date of the
latest month, so URL below is the one downloaded on 2026-10-14.
"""
from __future__ import annotations

import csv
import hashlib
import re
import sys
import tempfile
import urllib.request
from datetime import datetime
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "snapshots" / "cbsl_reserves.csv"
URL = ("https://www.cbsl.gov.lk/sites/default/files/cbslweb_documents/statistics/sheets/"
       "table2.15.2_20260930_e.xlsx")
SWAP = re.compile(r"PBOC swap equivalent to around US dollars ([\d.]+) billion, which is subject to conditionalities")
MONTHS = re.compile(r"gross official reserves were equivalent to ([\d.]+) months of imports")


def number(v) -> float | None:
    """A cell such as 1917.0, '1,917(II)(III)' or '6,600 (II) (III)'; None if it holds no number."""
    if isinstance(v, (int, float)):
        return None if pd.isna(v) else float(v)
    m = re.match(r"\s*(-?[\d,]+(?:\.\d+)?)", str(v))
    return float(m.group(1).replace(",", "")) if m else None


def month_of(sheet: str) -> str:
    for fmt in ("%b-%Y", "%B-%Y", "%b-%y", "%B-%y"):
        try:
            return datetime.strptime(sheet.strip(), fmt).strftime("%Y-%m")
        except ValueError:
            pass
    raise ValueError(f"cannot read the month of sheet {sheet!r}")


def parse_sheet(df: pd.DataFrame) -> dict:
    rec: dict = {}
    notes = []
    for _, r in df.iterrows():
        cells = [v for v in r.tolist() if not (isinstance(v, float) and pd.isna(v))]
        if not cells:
            continue
        label, rest = str(cells[0]).strip(), cells[1:]
        first = next((x for x in (number(c) for c in rest) if x is not None), None)
        if label.startswith("A.") and "Official reserve assets" in label:
            rec["official_reserve_assets"] = first
        elif label.startswith("(1)") and "Foreign currency reserves" in label and "fx_reserves" not in rec:
            rec["fx_reserves"] = first
        elif label.startswith("(4)") and "Gold" in label and "gold" not in rec:
            rec["gold"] = first
        elif re.match(r"\((?:I|II|III|IV|V|VI|VII)\)\s", label):
            notes.append(" ".join(str(c) for c in cells))
    text = " ".join(" ".join(notes).split())
    m = SWAP.search(text)
    rec["pboc_swap_bn"] = float(m.group(1)) if m else None
    rec["pboc_swap_note"] = 1.0 if re.search(r"PBOC swap.{0,120}?subject to conditionalities on usability", text) else 0.0
    m = MONTHS.search(text)
    rec["gor_months"] = float(m.group(1)) if m else None
    return rec


def main(path: Path | None) -> None:
    if path is None:
        path = Path(tempfile.mkdtemp(prefix="cbsl_")) / "table2.15.2.xlsx"   # downloads stay out of the repository
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"})
        with urllib.request.urlopen(req, timeout=120) as r:
            path.write_bytes(r.read())
    print(f"table2.15.2: sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}")
    book = pd.ExcelFile(path)
    rows = {}
    for sheet in book.sheet_names:
        rows[month_of(sheet)] = parse_sheet(book.parse(sheet, header=None))
    cols = ["official_reserve_assets", "fx_reserves", "gold", "pboc_swap_note", "pboc_swap_bn", "gor_months"]
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["month"] + cols)
        for m in sorted(rows):
            w.writerow([m] + ["" if rows[m].get(c) is None else ("%d" % rows[m][c] if c == "pboc_swap_note"
                                                                   else "%.4f" % rows[m][c]) for c in cols])
    print(f"wrote {OUT} ({len(rows)} months, {min(rows)} to {max(rows)})")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
