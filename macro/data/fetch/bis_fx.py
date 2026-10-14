"""Exchange rates for Chapter 5 from the BIS Data Portal (SDMX API v2): bilateral rates against the US dollar and
effective exchange rates, monthly.

    python3 data/fetch/bis_fx.py          # query the API and write the snapshot
    python3 data/fetch/bis_fx.py DIR      # use saved responses (DIR/<column>.csv)

Series (dataflow, key; the TITLE each response must carry):
  lkr_usd_eop  WS_XRU M.LK.LKR.E  Sri Lanka rupees per US dollar, end of month
  lkr_usd_avg  WS_XRU M.LK.LKR.A  Sri Lanka rupees per US dollar, monthly average
  cny_usd_avg  WS_XRU M.CN.CNY.A  yuan per US dollar, monthly average
  cn_neer      WS_EER M.N.B.CN    China, nominal effective exchange rate, broad basket (64 economies), 2020 = 100
  cn_reer      WS_EER M.R.B.CN    China, real effective exchange rate (CPI-based), broad basket, 2020 = 100
  us_reer      WS_EER M.R.B.US    United States, real effective exchange rate, broad basket, 2020 = 100
The effective rates rise when the currency appreciates (the opposite direction to e, the price of foreign currency
in domestic currency, used in the book). Writes data/snapshots/bis_fx.csv (month and the six columns, 1957 onward;
a cell is empty before its series starts) and prints the SHA-256 of each response. BIS terms: "The use of the
statistics is unrestricted, provided that ... the BIS must be cited ... as the source" and translations carry a note
that they are not official BIS translations (https://data.bis.org/help/legal).
"""
from __future__ import annotations

import csv
import hashlib
import io
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "snapshots" / "bis_fx.csv"
API = "https://stats.bis.org/api/v2/data/dataflow/BIS/{flow}/1.0/{key}?format=csv"
SERIES = {
    "lkr_usd_eop": ("WS_XRU", "M.LK.LKR.E", "Exchange rates against USD Sri Lanka - Sri Lanka rupee - Monthly - End of period"),
    "lkr_usd_avg": ("WS_XRU", "M.LK.LKR.A", "Exchange rates against USD Sri Lanka - Sri Lanka rupee - Monthly - Average of observations through period"),
    "cny_usd_avg": ("WS_XRU", "M.CN.CNY.A", "Exchange rates against USD China - Renminbi - Monthly - Average of observations through period"),
    "cn_neer": ("WS_EER", "M.N.B.CN", "China - Nominal - Broad (64 economies)"),
    "cn_reer": ("WS_EER", "M.R.B.CN", "China - Real - Broad (64 economies)"),
    "us_reer": ("WS_EER", "M.R.B.US", "United States - Real - Broad (64 economies)"),
}


def read(col: str, flow: str, key: str, title: str, folder: Path | None) -> dict[str, float]:
    if folder is None:
        folder = Path(tempfile.mkdtemp(prefix="bis_"))      # downloads stay out of the repository
        req = urllib.request.Request(API.format(flow=flow, key=key), headers={"User-Agent": "curl/8"})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    (folder / f"{col}.csv").write_bytes(r.read())
                break
            except urllib.error.URLError:
                if attempt == 3:
                    raise
                time.sleep(2 ** (attempt + 1))
        time.sleep(1)
    raw = (folder / f"{col}.csv").read_bytes()
    print(f"{col}: sha256 {hashlib.sha256(raw).hexdigest()}")
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
    titles = {(r.get("TITLE") or r.get("TITLE_TS") or "").strip() for r in rows}   # WS_EER calls it TITLE_TS
    if titles != {title}:
        raise ValueError(f"{col}: unexpected series {titles}")
    return {r["TIME_PERIOD"]: float(r["OBS_VALUE"]) for r in rows if r["OBS_VALUE"] not in ("", "NaN")}


def main(folder: Path | None) -> None:
    data = {col: read(col, *spec, folder) for col, spec in SERIES.items()}
    months = sorted(set().union(*data.values()))
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["month"] + list(SERIES))
        for m in months:
            w.writerow([m] + [repr(data[c][m]) if m in data[c] else "" for c in SERIES])
    print(f"wrote {OUT} ({len(months)} months, {months[0]} to {months[-1]})")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
