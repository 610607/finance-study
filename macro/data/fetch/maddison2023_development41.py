"""GDP per head of Argentina, Brazil, Mexico, India, Ghana and Korea, 1950-2022, from the Maddison Project Database 2023
(Chapter 41).

    python3 data/fetch/maddison2023_development41.py          # use (or download) ~/.cache/finance-study/maddison2023
    python3 data/fetch/maddison2023_development41.py DIR      # use a copy of mpd2023_web.xlsx already in DIR

The workbook, its URL and its headings are those of data/fetch/maddison2023.py (Chapter 21). The script keeps the
three Latin American economies of the import-substitution years (Argentina, Brazil, Mexico), the two economies of the
chapter's case study (India, Ghana) and the Republic of Korea, for 1950-2022, and writes
data/snapshots/maddison2023_development.csv (country, year, gdppc_2011usd, pop_thousands). Every economy has a GDP per
head and a population for every year. The citation policy of the workbook ('Notes' sheet) asks that the original papers
be cited when the data are shown in a graph or when fewer than twelve countries are used: the script prints, for each
economy, the rows of the sheets 'Sources' and 'Maddison original sources' whose period covers any of 1950-2022, in the
form the snapshot's .json keeps them ('sources_by_country').
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from maddison2023 import HEAD, fetch

OUT = HERE.parent / "snapshots" / "maddison2023_development.csv"
FIRST, LAST = 1950, 2022
COUNTRIES = ("ARG", "BRA", "MEX", "IND", "GHA", "KOR")


def covers(period: str) -> bool:
    """'1946-50', '1911-1990', '1950 -': does the period touch FIRST..LAST?"""
    years = [int(y) for y in re.findall(r"\d{2,4}", period)]
    if not years:
        return False
    a = years[0]
    b = years[1] if len(years) > 1 else 9999
    if b < 100:                                        # '1946-50'
        b += a // 100 * 100
    return a <= LAST and b >= FIRST


def sources(wb) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {c: [] for c in COUNTRIES}
    for sheet in ("Sources", "Maddison original sources"):
        code = None
        for r in wb[sheet].iter_rows(values_only=True):
            if r and isinstance(r[0], str) and re.fullmatch(r"[A-Z]{3}", r[0]):
                code = r[0]
                continue
            if code in out and r and r[0] is None and r[1] and r[2] and covers(str(r[1])):
                out[code].append(f"{sheet}, {str(r[1]).strip()}: {str(r[2]).strip()}")
    return out


def main(dest: Path) -> None:
    wb = openpyxl.load_workbook(fetch(dest), read_only=True, data_only=True)
    rows = wb["Full data"].iter_rows(values_only=True)
    head = tuple(next(rows))[:6]
    if head != HEAD:
        raise ValueError(f"headings {head}, expected {HEAD}")
    got: dict[tuple[str, int], tuple[float, float]] = {}
    for r in rows:
        code, _, _, year, gdppc, pop = r[:6]
        if code in COUNTRIES and FIRST <= year <= LAST:
            if gdppc is None or pop is None:
                raise ValueError(f"{code} {year}: no GDP per head or population")
            if (code, int(year)) in got:
                raise ValueError(f"{code} {year} appears twice")
            got[(code, int(year))] = (float(gdppc), float(pop))
    missing = [(c, y) for c in COUNTRIES for y in range(FIRST, LAST + 1) if (c, y) not in got]
    if missing:
        raise ValueError(f"missing {missing[:5]}")
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["country", "year", "gdppc_2011usd", "pop_thousands"])
        for c in COUNTRIES:
            for y in range(FIRST, LAST + 1):
                g, p = got[(c, y)]
                w.writerow([c, y, round(g, 3), round(p, 3)])
    print(f"{len(got)} rows, {len(COUNTRIES)} economies, {FIRST}-{LAST} -> {OUT}")
    for c, s in sources(wb).items():
        print(c, s)


if __name__ == "__main__":
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / ".cache" / "finance-study" / "maddison2023"
    folder.mkdir(parents=True, exist_ok=True)
    main(folder)
