"""GDP per head and population of six economies, 1500-1913, from the Maddison Project Database 2023.

    python3 data/fetch/maddison2023.py          # download the workbook (DataverseNL) and write the snapshot
    python3 data/fetch/maddison2023.py DIR      # use a copy of mpd2023_web.xlsx already in DIR

J. Bolt and J. L. van Zanden, "Maddison style estimates of the evolution of the world economy: A new 2023
update", Journal of Economic Surveys (2024), doi:10.1111/joes.12618; data: Maddison Project Database, version
2023, DataverseNL, doi:10.34894/INZBF2 (CC BY 4.0). The sheet "Full data" lists countrycode, country, region,
year, gdppc (real GDP per head in 2011 international dollars) and pop (mid-year population, thousands). The
script checks the headings, keeps the United Kingdom, the Netherlands, China, India, Japan and the United States
for 1500-1913 (the rows in which GDP per head or population has a value) and writes
data/snapshots/maddison2023_divergence.csv. The SHA-256 of the workbook is printed so that it can be compared with
the one recorded in the .json.
"""
from __future__ import annotations

import csv
import hashlib
import sys
import urllib.request
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "snapshots" / "maddison2023_divergence.csv"
URL = "https://dataverse.nl/api/access/datafile/421302"
NAME = "mpd2023_web.xlsx"
UA = "Mozilla/5.0 (X11; Linux x86_64) finance-study data fetch"
FIRST, LAST = 1500, 1913
HEAD = ("countrycode", "country", "region", "year", "gdppc", "pop")
COUNTRIES = ("GBR", "NLD", "CHN", "IND", "JPN", "USA")


def fetch(dest: Path) -> Path:
    path = dest / NAME
    if not path.exists():
        req = urllib.request.Request(URL, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=300) as r:
            path.write_bytes(r.read())
    print(f"{path.name}: sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}")
    return path


def main(dest: Path) -> None:
    ws = openpyxl.load_workbook(fetch(dest), read_only=True, data_only=True)["Full data"]
    rows = ws.iter_rows(values_only=True)
    head = tuple(next(rows))[:6]
    if head != HEAD:
        raise ValueError(f"headings {head}, expected {HEAD}")
    out, seen = [], set()
    for r in rows:
        code, _, _, year, gdppc, pop = r[:6]
        if code in COUNTRIES and FIRST <= year <= LAST and (gdppc is not None or pop is not None):
            if (code, year) in seen:
                raise ValueError(f"{code} {year} appears twice")
            seen.add((code, year))
            out.append((code, int(year), gdppc, pop))
    missing = [c for c in COUNTRIES if not any(o[0] == c for o in out)]
    if missing:
        raise ValueError(f"no rows for {missing}")
    out.sort(key=lambda o: (COUNTRIES.index(o[0]), o[1]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["country", "year", "gdppc_2011usd", "pop_thousands"])
        for code, year, g, p in out:
            w.writerow([code, year, "" if g is None else round(float(g), 3), "" if p is None else round(float(p), 3)])
    print(f"{len(out)} rows, {len(COUNTRIES)} economies, {FIRST}-{LAST} -> {OUT}")


if __name__ == "__main__":
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / ".cache" / "finance-study" / "maddison2023"
    folder.mkdir(parents=True, exist_ok=True)
    main(folder)
