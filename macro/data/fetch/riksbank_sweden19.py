"""Sweden 1740-1777: the riksdaler in marks and the Riksbank's notes and metal reserves (Chapter 19).

    python3 data/fetch/riksbank_sweden19.py              # download the two workbooks and write the snapshot
    python3 data/fetch/riksbank_sweden19.py DIR          # use copies already downloaded into DIR

From the Riksbank's "Historical Monetary and Financial Statistics for Sweden":
  Volume I, ch. 4 (Edvinsson 2010), Table I.A4.7 "Riksdaler in marks 1534-1776": the annual average price of the
    riksdaler (specie) in marks kopparmynt, with the lowest and highest quotation of the year;
  Volume II, ch. 8 (Fregert 2014), Table II.A8.1 "Riksbank assets" (column "Reserves: metal") and Table II.A8.2
    "Riksbank liabilities and equity" (column "Notes"), in SEK.
The script checks the headings, keeps 1740-1777 and writes data/snapshots/riksbank_sweden_1740_1777.csv. It
stores the values as published; the chapter's ratios are the book's own calculations.
"""
from __future__ import annotations

import csv
import hashlib
import sys
import urllib.request
from pathlib import Path

import xlrd

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "snapshots" / "riksbank_sweden_1740_1777.csv"
BASE = "https://www.riksbank.se/globalassets/media/forskning/monetar-statistik/"
FILES = {"I": "volym1/volumeich4exchangerates1534_1803.xls", "II": "volym2/volumeiich8riksbankbalancesheet.xls"}
UA = "Mozilla/5.0 (X11; Linux x86_64) finance-study data fetch"
FIRST, LAST = 1740, 1777
# (volume, sheet, title cell (row, col, text), heading row, {column: (expected heading, name in the snapshot)})
TABLES = [
    ("I", "Tables I.A4.7", (2, 1, "Table I.A4.7 Riksdaler in mark 1534–1776"), 3,
     {1: ("Riksdaler in mark", "riksdaler_marks"), 2: ("Lowest", "riksdaler_low"), 3: ("Highest", "riksdaler_high")}),
    ("II", "Table II.A8.2", (2, 1, "Riksbank liabilities and equity 1668– in SEK."), 3,
     {2: ("Notes", "notes_sek")}),
    ("II", "Table II.A8.1", (2, 1, "Riksbank assets 1668– in SEK"), 3,
     {2: ("Reserves: metal", "metal_reserves_sek")}),
]


def year_of(cell) -> int | None:
    if isinstance(cell, float):
        return int(cell)
    if isinstance(cell, str) and cell.strip()[:4].isdigit():
        return int(cell.strip()[:4])
    return None


def main(d: Path) -> None:
    books = {}
    for vol, name in FILES.items():
        p = d / Path(name).name
        if not p.exists():
            req = urllib.request.Request(BASE + name, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                p.write_bytes(r.read())
        print(f"{p.name}: sha256 {hashlib.sha256(p.read_bytes()).hexdigest()}")
        books[vol] = xlrd.open_workbook(str(p))
    data: dict[str, dict[int, float]] = {}
    for vol, sheet, (r0, c0, title), head_row, cols in TABLES:
        sh = books[vol].sheet_by_name(sheet)
        if str(sh.cell_value(r0, c0)).strip() != title:
            raise ValueError(f"{sheet}: title is {sh.cell_value(r0, c0)!r}, expected {title!r}")
        for col, (head, name) in cols.items():
            if str(sh.cell_value(head_row, col)).strip() != head.strip():
                raise ValueError(f"{sheet}: column {col} is {sh.cell_value(head_row, col)!r}, expected {head!r}")
            s = {}
            for i in range(head_row + 1, sh.nrows):
                y = year_of(sh.cell_value(i, 0))
                v = sh.cell_value(i, col)
                if y is not None and FIRST <= y <= LAST and isinstance(v, float):
                    s[y] = v
            data[name] = s
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year"] + list(data))
        for y in range(FIRST, LAST + 1):
            w.writerow([y] + ["" if y not in data[k] else round(data[k][y], 6) for k in data])
    print(f"{LAST - FIRST + 1} years -> {OUT}")
    for k, s in data.items():
        print(f"  {k}: {min(s)}-{max(s)}, {len(s)} values")


if __name__ == "__main__":
    default = Path.home() / ".cache" / "finance-study" / "riksbank"
    d = Path(sys.argv[1]) if len(sys.argv) > 1 else default
    d.mkdir(parents=True, exist_ok=True)
    main(d)
