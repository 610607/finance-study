"""Decadal wages, prices, population and land rents for England, 1250-1500, from Gregory Clark's data.

    python3 data/fetch/clark_england.py              # download both workbooks and write the snapshot
    python3 data/fetch/clark_england.py DIR          # use Wages 2014.xlsx and the NNI workbook already in DIR
    python3 data/fetch/clark_england.py --early-modern [DIR]   # the decades 1490-1690 (Chapter 13)

Clark publishes the series on his data page (faculty.econ.ucdavis.edu/faculty/gclark/data.html):
"Nominal and Real Wages, England, 1209-1869" (English Data/Wages 2014.xlsx) and "National Income,
Prices, Wages, Land Rents, Population, England, 1209-1869" (English Data/England NNI - Clark - 2015.xlsx).
The script reads the sheet "Decadal" of each workbook, checks the column headings, keeps the decades
1250-1500 and writes data/snapshots/clark2015_england_decadal.csv; with --early-modern it keeps 1490-1690
and writes data/snapshots/clark2015_england_decadal_1490_1690.csv. The SHA-256 of each workbook is
printed so that it can be compared with the one recorded in the snapshot's .json.
"""
from __future__ import annotations

import csv
import hashlib
import sys
import urllib.request
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "snapshots" / "clark2015_england_decadal.csv"
OUT_EARLY_MODERN = HERE.parent / "snapshots" / "clark2015_england_decadal_1490_1690.csv"
BASE = "http://faculty.econ.ucdavis.edu/faculty/gclark/English%20Data/"
FILES = {"wages": "Wages%202014.xlsx", "nni": "England%20NNI%20-%20Clark%20-%202015.xlsx"}
UA = "Mozilla/5.0 (X11; Linux x86_64) finance-study data fetch"
FIRST, LAST = 1250, 1500

# (column index in the sheet "Decadal", heading as printed, name in the snapshot)
WAGES = [(1, "Farm Laborers, d/day", "farm_wage_d"),
         (3, "Building Laborers, d/day", "blab_wage_d"),
         (4, "Building Craftsmen, d/day", "bcraft_wage_d"),
         (6, "Cost of Living (1860s=100)", "col_1860s_100"),
         (8, "Real Farm Wage (1860s=100)", "real_farm_1860s_100"),
         (9, "Real Building Laborer Wage (1860s=100)", "real_blab_1860s_100"),
         (10, "Real Building Craftsman Wage (1860s=100)", "real_bcraft_1860s_100")]
NNI = [(2, "Pop England", "pop_england_m"),
       (9, "Land rents", "land_rents_gbp_m")]


def fetch(name: str, dest: Path) -> Path:
    path = dest / FILES[name].replace("%20", " ")
    if not path.exists():
        req = urllib.request.Request(BASE + FILES[name], headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=120) as r:
            path.write_bytes(r.read())
    print(f"{path.name}: sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}")
    return path


def read(path: Path, columns, header_row: int, first: int, last: int) -> dict[int, dict[str, float | None]]:
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True)["Decadal"]
    rows = list(ws.iter_rows(values_only=True))
    head = rows[header_row]
    for i, title, _ in columns:
        if str(head[i]).strip() != title:
            raise ValueError(f"{path.name}: column {i} is {head[i]!r}, expected {title!r}")
    out = {}
    for r in rows[header_row + 1:]:
        if isinstance(r[0], (int, float)) and first <= r[0] <= last:
            out[int(r[0])] = {name: (None if r[i] is None else float(r[i])) for i, _, name in columns}
    return out


def main(dest: Path, first: int = FIRST, last: int = LAST, out: Path = OUT) -> None:
    w = read(fetch("wages", dest), WAGES, header_row=0, first=first, last=last)
    n = read(fetch("nni", dest), NNI, header_row=0, first=first, last=last)
    decades = list(range(first, last + 1, 10))
    missing = [d for d in decades if d not in w or d not in n]
    if missing:
        raise ValueError(f"decades missing: {missing}")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        names = ["decade"] + [c[2] for c in NNI] + [c[2] for c in WAGES]
        wr = csv.DictWriter(f, fieldnames=names)
        wr.writeheader()
        for d in decades:
            row = {"decade": d, **n[d], **w[d]}
            wr.writerow({k: ("" if v is None else (round(v, 4) if isinstance(v, float) else v))
                         for k, v in row.items()})
    print(f"{len(decades)} decades {first}-{last} -> {out}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--early-modern"]
    folder = Path(args[0]) if args else Path.home() / ".cache" / "finance-study" / "clark"
    folder.mkdir(parents=True, exist_ok=True)
    if "--early-modern" in sys.argv[1:]:
        main(folder, 1490, 1690, OUT_EARLY_MODERN)
    else:
        main(folder)
