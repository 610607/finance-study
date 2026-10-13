"""Population of England around the Black Death, from the Bank of England's "A millennium of macroeconomic data".

    python3 data/fetch/boe_millennium_pop.py           # download the workbook (27 MB) and write the snapshot
    python3 data/fetch/boe_millennium_pop.py FILE      # use a copy of the workbook already downloaded

Sheet "A2. Pop of Eng & GB 1086-1870" gives the population of England in millions from Broadberry,
Campbell, Klein, Overton and van Leeuwen (2015), British Economic Growth, 1270-1870. Annual values between
the authors' benchmark years are interpolated in the sheet. The script keeps the years listed in YEARS and
writes data/snapshots/boe_millennium_pop_england.csv.
"""
from __future__ import annotations

import csv
import hashlib
import sys
import urllib.request
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "snapshots" / "boe_millennium_pop_england.csv"
URL = ("https://www.bankofengland.co.uk/-/media/boe/files/statistics/research-datasets/"
       "a-millennium-of-macroeconomic-data-for-the-uk.xlsx")
UA = "Mozilla/5.0 (X11; Linux x86_64) finance-study data fetch"
SHEET = "A2. Pop of Eng & GB 1086-1870"
YEARS = [1290, 1300, 1310, 1320, 1330, 1340, 1345, 1346, 1347, 1348, 1349, 1350, 1351, 1352,
         1360, 1370, 1377, 1380, 1390, 1400, 1410, 1420, 1430, 1440, 1450, 1460, 1470, 1480, 1490, 1500]


def main(path: Path) -> None:
    if not path.exists():
        req = urllib.request.Request(URL, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=300) as r:
            path.write_bytes(r.read())
    print(f"{path.name}: sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}")
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True)[SHEET]
    rows = list(ws.iter_rows(values_only=True))
    head = [i for i, r in enumerate(rows) if r and r[0] == "Year"]
    if not head or rows[head[0]][1] != "Population of England, millions":
        raise ValueError(f"{SHEET}: unexpected layout")
    pop = {}
    for r in rows[head[0] + 1:]:
        try:
            pop[int(r[0])] = float(r[1])
        except (TypeError, ValueError):
            continue
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "pop_england_m"])
        for y in YEARS:
            w.writerow([y, round(pop[y], 4)])
    print(f"{len(YEARS)} years -> {OUT}")


if __name__ == "__main__":
    default = Path.home() / ".cache" / "finance-study" / "boe" / "a-millennium-of-macroeconomic-data-for-the-uk.xlsx"
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else default
    p.parent.mkdir(parents=True, exist_ok=True)
    main(p)
