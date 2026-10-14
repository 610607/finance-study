"""Consumer-price inflation of Japan, Russia, Sri Lanka and Zimbabwe for Chapter 1, from the World Bank's
World Development Indicators (API v2).

    python3 data/fetch/wb_inflation.py          # query the API and write the snapshot
    python3 data/fetch/wb_inflation.py DIR      # keep the API response in DIR (DIR/FP.CPI.TOTL.ZG.json); a response
                                                # already there is read, not downloaded again

Series: FP.CPI.TOTL.ZG  Inflation, consumer prices (annual % growth); source IMF International Financial Statistics;
"License_Type: CC BY-4.0" in the WDI metadata (2026-10-14).
Writes data/snapshots/wb_inflation_annual.csv: country (ISO3), year, inflation (percent), 1960-2025, one row for
each year in which WDI has a value (Zimbabwe has none before 2010, Russia none before 1993). The SHA-256 of the
response is printed.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "snapshots" / "wb_inflation_annual.csv"
IND, COUNTRIES, DATES = "FP.CPI.TOTL.ZG", "JPN;RUS;LKA;ZWE", "1960:2025"
API = f"https://api.worldbank.org/v2/country/{COUNTRIES}/indicator/{IND}?format=json&per_page=20000&date={DATES}"


def main(folder: Path | None) -> None:
    folder = folder or Path(tempfile.mkdtemp(prefix="wb_"))   # downloads stay out of the repository
    path = folder / f"{IND}.json"
    if not path.exists():
        req = urllib.request.Request(API, headers={"User-Agent": "curl/8"})
        for attempt in range(4):                              # the API answers 400 now and then; retry
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    path.write_bytes(r.read())
                break
            except urllib.error.HTTPError:
                if attempt == 3:
                    raise
                time.sleep(2 ** (attempt + 1))
    raw = path.read_bytes()
    print(f"{IND}: sha256 {hashlib.sha256(raw).hexdigest()}")
    d = json.loads(raw)
    if not isinstance(d, list) or len(d) < 2 or d[0].get("pages") != 1:
        raise ValueError(f"unexpected response {str(d)[:200]}")
    if any(r["indicator"]["id"] != IND for r in d[1]):
        raise ValueError("rows of another indicator")
    rows = sorted((r["countryiso3code"], r["date"], r["value"]) for r in d[1] if r["value"] is not None)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["country", "year", "inflation"])
        w.writerows([c, y, repr(float(v))] for c, y, v in rows)
    print(f"wrote {OUT} ({len(rows)} rows)")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
