"""GDP per head of 28 economies, 1929-1938, from the Maddison Project Database 2023 (Chapter 29).

    python3 data/fetch/maddison2023_interwar29.py          # use (or download) ~/.cache/finance-study/maddison2023
    python3 data/fetch/maddison2023_interwar29.py DIR      # use a copy of mpd2023_web.xlsx already in DIR

The workbook, its URL and its headings are those of data/fetch/maddison2023.py (Chapter 21). The script keeps the
economies of Bernanke and James's table of exits from gold (Table 2.1) for which the database has figures, with
Argentina and Switzerland (whose dates Bernanke 1995 gives) and five Latin American economies, for 1929-1938 (Poland has no figure for 1928), and
writes data/snapshots/maddison2023_interwar.csv (country, year, gdppc_2011usd). Czechoslovakia, Estonia and Latvia
have no figures for these years in the database. The citation policy of the workbook ('Notes' sheet) asks that the
original papers be cited when the data are shown in a graph; the snapshot's .json lists them, from the sheets
'Sources' and 'Maddison original sources', for each economy.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from maddison2023 import HEAD, fetch

OUT = HERE.parent / "snapshots" / "maddison2023_interwar.csv"
FIRST, LAST = 1929, 1938
COUNTRIES = ("AUS", "AUT", "BEL", "CAN", "DNK", "FIN", "FRA", "DEU", "GRC", "HUN", "ITA", "JPN", "NLD", "NOR", "NZL",
             "POL", "ROU", "SWE", "ESP", "GBR", "USA", "ARG", "CHE", "BRA", "CHL", "COL", "MEX", "URY")


def main(dest: Path) -> None:
    ws = openpyxl.load_workbook(fetch(dest), read_only=True, data_only=True)["Full data"]
    rows = ws.iter_rows(values_only=True)
    head = tuple(next(rows))[:6]
    if head != HEAD:
        raise ValueError(f"headings {head}, expected {HEAD}")
    got: dict[tuple[str, int], float] = {}
    for r in rows:
        code, _, _, year, gdppc, _ = r[:6]
        if code in COUNTRIES and FIRST <= year <= LAST:
            if gdppc is None:
                raise ValueError(f"{code} {year}: no GDP per head")
            if (code, int(year)) in got:
                raise ValueError(f"{code} {year} appears twice")
            got[(code, int(year))] = float(gdppc)
    missing = [(c, y) for c in COUNTRIES for y in range(FIRST, LAST + 1) if (c, y) not in got]
    if missing:
        raise ValueError(f"missing {missing[:5]}")
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["country", "year", "gdppc_2011usd"])
        for c in COUNTRIES:
            for y in range(FIRST, LAST + 1):
                w.writerow([c, y, round(got[(c, y)], 3)])
    print(f"{len(got)} rows, {len(COUNTRIES)} economies, {FIRST}-{LAST} -> {OUT}")


if __name__ == "__main__":
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / ".cache" / "finance-study" / "maddison2023"
    folder.mkdir(parents=True, exist_ok=True)
    main(folder)
