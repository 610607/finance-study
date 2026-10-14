"""External accounts of China, Sri Lanka and the United States, and price levels across countries, for Chapter 5,
from the World Bank's World Development Indicators (API v2).

    python3 data/fetch/wb_external.py          # query the API and write the two snapshots
    python3 data/fetch/wb_external.py DIR      # use saved API responses (DIR/<indicator>_<scope>.json)

Series (all "License_Type: CC BY-4.0" in the WDI metadata, 2026-10-14):
  FI.RES.TOTL.CD   Total reserves, including gold (current US$); source IMF International Financial Statistics
  BN.CAB.XOKA.CD   Current account balance (current US$, BoP); source IMF Balance of Payments Statistics
  BN.FIN.TOTL.CD   Net financial account (BoP, current US$); same source
  BN.RES.INCL.CD   Reserves and related items (current US$, BoP); same source
  NY.GDP.MKTP.CD   GDP (current US$)
  BN.TRF.KOGT.CD   Net capital account (BoP, current US$); IMF Balance of Payments Statistics
  FP.CPI.TOTL      Consumer price index (2010 = 100); IMF International Financial Statistics
  PA.NUS.PPP       PPP conversion factor, GDP (LCU per international $); International Comparison Program
  PA.NUS.FCRF      Official exchange rate (LCU per US$, period average); IMF International Financial Statistics
  NY.GDP.PCAP.CD   GDP per capita (current US$)
Writes
  data/snapshots/wb_external_annual.csv  country (ISO3), year, reserves, ca, fa, res_bop, gdp, ka (US$), cpi
                                         (2010 = 100) and fx (LCU per US$) for CHN, LKA and USA, 1982-2025; a cell is
                                         empty when WDI has no value
  data/snapshots/wb_price_levels.csv     iso3, country, ppp, fx, gdppc and price_level = ppp / fx for every economy
                                         (aggregates excluded) with all three values in 2021, the ICP benchmark year
The SHA-256 of every response is printed; the values of the 2026-10-14 download are in the snapshots' .json.
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
SNAP = HERE.parent / "snapshots"
API = "https://api.worldbank.org/v2/country/{countries}/indicator/{ind}?format=json&per_page=20000&date={dates}"
PANEL = {"reserves": "FI.RES.TOTL.CD", "ca": "BN.CAB.XOKA.CD", "fa": "BN.FIN.TOTL.CD", "res_bop": "BN.RES.INCL.CD",
         "gdp": "NY.GDP.MKTP.CD", "ka": "BN.TRF.KOGT.CD", "cpi": "FP.CPI.TOTL", "fx": "PA.NUS.FCRF"}
PANEL_COUNTRIES, PANEL_DATES = "CHN;LKA;USA", "1982:2025"
CROSS = {"ppp": "PA.NUS.PPP", "fx": "PA.NUS.FCRF", "gdppc": "NY.GDP.PCAP.CD"}
CROSS_YEAR = "2021"
COUNTRY_LIST = "https://api.worldbank.org/v2/country?format=json&per_page=400"


def fetch(url: str, name: str, folder: Path | None) -> list:
    if folder is None:
        folder = Path(tempfile.mkdtemp(prefix="wb_"))       # downloads stay out of the repository
        req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})
        for attempt in range(4):                              # the API answers 400 now and then; retry
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    (folder / f"{name}.json").write_bytes(r.read())
                break
            except urllib.error.HTTPError:
                if attempt == 3:
                    raise
                time.sleep(2 ** (attempt + 1))
        time.sleep(1)
    raw = (folder / f"{name}.json").read_bytes()
    print(f"{name}: sha256 {hashlib.sha256(raw).hexdigest()}")
    d = json.loads(raw)
    if not isinstance(d, list) or len(d) < 2 or d[0].get("pages") != 1:
        raise ValueError(f"{name}: unexpected response {str(d)[:200]}")
    return d[1]


def series(ind: str, countries: str, dates: str, scope: str, folder: Path | None) -> dict[tuple[str, str], float]:
    rows = fetch(API.format(countries=countries, ind=ind, dates=dates), f"{ind}_{scope}", folder)
    if any(r["indicator"]["id"] != ind for r in rows):
        raise ValueError(f"{ind}: rows of another indicator")
    return {(r["countryiso3code"], r["date"]): float(r["value"]) for r in rows if r["value"] is not None}


def main(folder: Path | None) -> None:
    panel = {col: series(ind, PANEL_COUNTRIES, PANEL_DATES, "panel", folder) for col, ind in PANEL.items()}
    keys = sorted(set().union(*panel.values()))
    with (SNAP / "wb_external_annual.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["country", "year"] + list(PANEL))
        for k in keys:
            w.writerow(list(k) + [repr(panel[c][k]) if k in panel[c] else "" for c in PANEL])
    print(f"wrote wb_external_annual.csv ({len(keys)} rows)")

    economies = {c["id"]: c["name"] for c in fetch(COUNTRY_LIST, "countries", folder)
                 if c["region"]["value"] != "Aggregates"}
    cross = {col: series(ind, "all", CROSS_YEAR, "all", folder) for col, ind in CROSS.items()}
    n = 0
    with (SNAP / "wb_price_levels.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["iso3", "country", "year", "ppp", "fx", "gdppc", "price_level"])
        for iso in sorted(economies):
            k = (iso, CROSS_YEAR)
            if all(k in cross[c] for c in CROSS):
                ppp, fx, pc = (cross[c][k] for c in CROSS)
                w.writerow([iso, economies[iso], CROSS_YEAR, repr(ppp), repr(fx), repr(pc), "%.6f" % (ppp / fx)])
                n += 1
    print(f"wrote wb_price_levels.csv ({n} economies, {CROSS_YEAR})")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
