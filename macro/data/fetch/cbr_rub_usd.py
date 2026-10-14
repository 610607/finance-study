"""Official rouble exchange rate of the US dollar, 1998-1999, for Chapter 1, from the Bank of Russia.

    python3 data/fetch/cbr_rub_usd.py          # query the Bank of Russia and write the snapshot
    python3 data/fetch/cbr_rub_usd.py DIR      # use DIR/rub.xml (downloaded into DIR if it is not there)

Source: the Bank of Russia's XML service for the dynamics of the official exchange rate of one currency,
https://www.cbr.ru/scripts/XML_dynamic.asp?date_req1=01/01/1998&date_req2=31/12/1999&VAL_NM_RQ=R01235
(R01235 is the US dollar). The response is windows-1251 XML with one <Record Date="DD.MM.YYYY"> per date on which the
Bank set a rate; <Value> is in roubles for <Nominal> dollars, with a decimal comma. Roubles are the new roubles of
1 January 1998 (1 new rouble = 1000 old). Writes data/snapshots/cbr_rub_usd.csv: date (ISO) and rub_per_usd, and
prints the SHA-256 of the response.
Bank of Russia terms ("About the Site", https://www.cbr.ru/eng/about/, 2026-10-14): "Copying of information
available at http://www.cbr.ru/ ... is allowed provided that the link to the source of this information is
indicated"; the information "cannot be used for commercial purposes".
"""
from __future__ import annotations

import csv
import hashlib
import sys
import tempfile
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "snapshots" / "cbr_rub_usd.csv"
URL = "https://www.cbr.ru/scripts/XML_dynamic.asp?date_req1=01/01/1998&date_req2=31/12/1999&VAL_NM_RQ=R01235"


def main(folder: Path | None) -> None:
    folder = folder or Path(tempfile.mkdtemp(prefix="cbr_"))  # downloads stay out of the repository
    path = folder / "rub.xml"
    if not path.exists():
        req = urllib.request.Request(URL, headers={"User-Agent": "curl/8"})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    path.write_bytes(r.read())
                break
            except urllib.error.URLError:
                if attempt == 3:
                    raise
                time.sleep(2 ** (attempt + 1))
    raw = path.read_bytes()
    print(f"rub.xml: sha256 {hashlib.sha256(raw).hexdigest()}")
    root = ET.fromstring(raw)                                 # the XML declaration names the encoding
    if root.tag != "ValCurs" or root.get("ID") != "R01235":
        raise ValueError("unexpected response")
    rows = []
    for rec in root.iter("Record"):
        if rec.findtext("Nominal") != "1":
            raise ValueError(f"{rec.get('Date')}: nominal {rec.findtext('Nominal')}")
        d, m, y = rec.get("Date").split(".")
        rows.append([f"{y}-{m}-{d}", rec.findtext("Value").replace(",", ".")])
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "rub_per_usd"])
        w.writerows(sorted(rows))
    print(f"wrote {OUT} ({len(rows)} dates, {min(rows)[0]} to {max(rows)[0]})")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
