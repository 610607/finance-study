"""The first auctions of US Treasury inflation-protected securities (TIPS), 1997-1998, from Treasury's Fiscal Data API.

    python3 data/fetch/treasury_tips_auctions.py            # query the API and write the snapshot
    python3 data/fetch/treasury_tips_auctions.py FILE.json  # use a saved API response

The dataset "Treasury Securities Auctions Data" (endpoint v1/accounting/od/auctions_query) lists every auction
since 1979. The script asks for the inflation-indexed securities, oldest first, and writes the first six to
data/snapshots/treasury_tips_first.csv. The SHA-256 of the response is printed.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import tempfile
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "snapshots" / "treasury_tips_first.csv"
FIELDS = ["cusip", "security_type", "security_term", "auction_date", "issue_date", "maturity_date", "int_rate",
          "high_yield", "offering_amt", "total_tendered", "total_accepted", "ref_cpi_on_dated_date", "auction_format"]
URL = ("https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query"
       "?filter=inflation_index_security:eq:Yes&sort=auction_date&page%5Bsize%5D=6&fields=" + ",".join(FIELDS))


def main(path: Path | None) -> None:
    if path is None:
        path = Path(tempfile.mkdtemp(prefix="tips_")) / "tips_first.json"   # downloads stay out of the repository
        req = urllib.request.Request(URL, headers={"User-Agent": "curl/8"})
        with urllib.request.urlopen(req, timeout=120) as r:
            path.write_bytes(r.read())
    raw = path.read_bytes()
    print(f"{path.name}: sha256 {hashlib.sha256(raw).hexdigest()}")
    rows = json.loads(raw)["data"]
    if len(rows) != 6 or set(rows[0]) != set(FIELDS):
        raise ValueError("unexpected response")
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(FIELDS)
        for r in rows:
            w.writerow([r[f] for f in FIELDS])
    print(f"wrote {OUT} ({len(rows)} auctions, {rows[0]['auction_date']} to {rows[-1]['auction_date']})")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
