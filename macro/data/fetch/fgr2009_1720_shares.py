"""Daily share prices in London and Paris, 1718-1720, from the 1720 price database of Frehen, Goetzmann & Rouwenhorst.

    python3 data/fetch/fgr2009_1720_shares.py          # download the workbook and write the snapshot
    python3 data/fetch/fgr2009_1720_shares.py FILE     # use a copy already downloaded

R. G. P. Frehen, W. N. Goetzmann and K. G. Rouwenhorst, "New Evidence on the First Financial Bubble", Yale ICF
Working Paper 09-04 (2009), published in Journal of Financial Economics 108(3), 2013. Their workbook
"1720PriceDatabaseOctober5_10version.xlsx" (Yale School of Management) has a sheet "British and French shares"
with the Julian and the Gregorian date of each trading day and the price of each company. The script checks
the headings, keeps the eight series below, and writes data/snapshots/fgr2009_1720_shares.csv:

    date (Gregorian, ISO), date_julian (ISO; the London date), and in this order bank_of_england,
    royal_african, old_east_india, south_sea (pounds per 100 pounds of nominal stock), mississippi (livres per
    share of the Compagnie des Indes), million_bank, royal_exchange_assurance, london_assurance

Empty cells are days without a quotation. One date is mistyped in the workbook ("20-51719", in the Gregorian column of
9 May 1719 Julian and the Julian column of 31 May 1719 Gregorian); the script rebuilds an unreadable date from the
other calendar (the Gregorian date is 11 days later in 1700-1800) and reports it. Each sheet of the workbook says "Please do not circulate this data
without the expressed permission of the authors", so the .csv is not kept in the repository (.gitignore):
run this script before the check script and the figures of Chapter 16. The SHA-256 of the workbook is
printed so that it can be compared with the one recorded in the .json.
"""
from __future__ import annotations

import csv
import datetime
import hashlib
import sys
import urllib.request
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "snapshots" / "fgr2009_1720_shares.csv"
URL = "https://som.yale.edu/sites/default/files/2022-03/1720PriceDatabaseOctober5_10version.xlsx"
SHA256 = "8c829098d23fd3c8cf11ed0bf61f1d74df86abf68715157c813da0258aee578c"
UA = "Mozilla/5.0 (X11; Linux x86_64) finance-study data fetch"
SHEET = "British and French shares"
COLS = [("Bank of England", "bank_of_england"), ("Royal African Company", "royal_african"),
        ("Old East India Company", "old_east_india"), ("South Sea Company", "south_sea"),
        ("Mississippi Company", "mississippi"), ("Million Bank", "million_bank"),
        ("Royal Exchange Assurance", "royal_exchange_assurance"), ("London Assurance", "london_assurance")]


def day(cell) -> datetime.date | None:
    if cell is None:
        return None
    if isinstance(cell, datetime.datetime):
        return cell.date()
    d, m, y = (int(x) for x in str(cell).strip().split("-"))
    return datetime.date(y, m, d)


def main(path: Path) -> None:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    print(f"{path.name}: sha256 {digest}" + ("" if digest == SHA256 else f" (recorded: {SHA256})"))
    rows = list(openpyxl.load_workbook(path, read_only=True, data_only=True)[SHEET].iter_rows(values_only=True))
    head = [str(c).strip() if c is not None else "" for c in rows[4]]
    if head[:2] != ["Julian Date", "Gregorian Date"]:
        raise ValueError(f"unexpected headings {head[:2]}")
    idx = [head.index(name) for name, _ in COLS]
    out, last = [], None
    eleven = datetime.timedelta(days=11)
    for r in rows[5:]:
        dates = []
        for cell in r[:2]:
            try:
                dates.append(day(cell))
            except ValueError:
                dates.append("bad")
        j, g = dates
        if g == "bad" and isinstance(j, datetime.date):
            g = j + eleven
            print(f"Gregorian date {r[1]!r} unreadable; taken as {g} (Julian {j} + 11 days)")
        if j == "bad" and isinstance(g, datetime.date):
            j = g - eleven
            print(f"Julian date {r[0]!r} unreadable; taken as {j} (Gregorian {g} - 11 days)")
        if "bad" in (j, g):
            raise ValueError(f"unreadable dates {r[:2]}")
        if g is None:
            continue
        if j is not None and g - j != eleven:
            raise ValueError(f"{g}: Julian date {j} is not 11 days earlier")
        if last is not None and g <= last:
            raise ValueError(f"dates out of order at {g}")
        last = g
        vals = [r[k] for k in idx]
        if any(v is not None and not isinstance(v, (int, float)) for v in vals):
            raise ValueError(f"{g}: non-numeric price {vals}")
        out.append([g.isoformat(), j.isoformat() if j else ""] + ["" if v is None else f"{v:g}" for v in vals])
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "date_julian"] + [c for _, c in COLS])
        w.writerows(out)
    print(f"wrote {OUT.relative_to(HERE.parent.parent)}: {len(out)} days, {out[0][0]} to {out[-1][0]}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(Path(sys.argv[1]))
    else:
        tmp = HERE / "_fgr2009_1720.xlsx"
        if not tmp.exists():
            req = urllib.request.Request(URL, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as resp:
                tmp.write_bytes(resp.read())
        try:
            main(tmp)
        finally:
            tmp.unlink()
