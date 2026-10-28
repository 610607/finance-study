"""Japan's wholesale prices for Chapter 35: the Bank of Japan's Corporate Goods Price Index on the prewar base
(formerly the Wholesale Price Index), all commodities, 1934-36 average = 1, monthly from January 1944 to December
1952, from the Bank's statistics API (series PRCG_28Z0000000 of database PR01).

    python3 data/fetch/boj_wpi35.py          # download the series and write the snapshot
    python3 data/fetch/boj_wpi35.py FILE     # read a CSV response saved earlier

Writes data/snapshots/boj_prewar_wpi_1944_1952.csv (month YYYY-MM, index) and its .json. The API's answer starts
with a header that includes the time of the request, so its hash changes with every download; the hash of the copy
that wrote the snapshot is in the .json. Bank of Japan terms (https://www.boj.or.jp/en/copyright.htm): "The
information included in the site may be copied or reproduced with the exceptions below. When copying or
reproducing, the source, the Bank of Japan, should be explicitly credited."
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "snapshots" / "boj_prewar_wpi_1944_1952"
CODE = "PRCG_28Z0000000"
URL = ("https://www.stat-search.boj.or.jp/api/v1/getDataCode?format=csv&lang=en&db=PR01&startDate=194401"
       f"&endDate=195212&code={CODE}")
UA = "Mozilla/5.0 (X11; Linux x86_64) finance-study quotation check"


def download() -> bytes:
    req = urllib.request.Request(URL, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except urllib.error.URLError:
            if attempt == 3:
                raise
            time.sleep(2 ** (attempt + 1))
    raise AssertionError


def main(path: Path | None) -> None:
    raw = path.read_bytes() if path else download()
    text = raw.decode("ascii")
    lines = list(csv.reader(io.StringIO(text)))
    assert lines[0] == ["STATUS", "200"], lines[0]
    asked = next(l[1] for l in lines if l and l[0] == "DATE")
    rows = [l for l in lines if l and l[0] == CODE]
    assert all(l[1] == "[Prewar Base Index] All commodities" and l[2] == "1934-36 average=1" and l[3] == "MONTHLY"
               for l in rows)
    months = [(f"{l[6][:4]}-{l[6][4:]}", l[7]) for l in rows]
    assert [m for m, _ in months] == [f"{y}-{m:02d}" for y in range(1944, 1953) for m in range(1, 13)], "months"
    with open(f"{OUT}.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["month", "index"])
        w.writerows(months)
    sha = hashlib.sha256(raw).hexdigest()
    meta = {
        "title": "Japan: Corporate Goods Price Index on the prewar base (formerly the Wholesale Price Index), all "
                 "commodities, 1934-36 average = 1, monthly, January 1944 to December 1952",
        "source": "Bank of Japan, Time-series data search, database PR01 (Corporate Goods Price Index), series "
                  f"{CODE} '[Prewar Base Index] All commodities', retrieved through the Bank's statistics API",
        "url": URL,
        "series": "month (YYYY-MM), index (1934-36 average = 1)",
        "retrieved": time.strftime("%Y-%m-%d"),
        "license": "Bank of Japan terms (https://www.boj.or.jp/en/copyright.htm): 'The information included in the "
                   "site may be copied or reproduced with the exceptions below. When copying or reproducing, the "
                   "source, the Bank of Japan, should be explicitly credited.' (row bojcr_terms of "
                   "reconstruction_facts)",
        "citation": "Source: Bank of Japan, Corporate Goods Price Index (prewar base index), all commodities.",
        "used_in": [35],
        "fetch": "data/fetch/boj_wpi35.py",
        "notes": f"The API answered at {asked} (Japan time), last update of the series {rows[0][5]}; SHA-256 of the "
                 f"answer {sha}. The answer's header carries the time of the request, so a new download has a new "
                 "hash with the same figures. The index is the Bank's continuation of its wholesale price index on "
                 "the base 1934-36 = 1; Chapter 35 uses it for its figure of Japan's postwar inflation and compares "
                 "the averages of 1944 and 1948 with the Ministry of Finance's '55.1 fold' (row mof_20fold of "
                 "reconstruction_facts).",
    }
    Path(f"{OUT}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT}.csv ({len(months)} months), sha256 {sha}")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
