"""The sources of Chapter 37: download them into the web cache, compare their hashes, rebuild the data snapshot, check.

    python3 data/fetch/mundell37.py              # download what is missing from WEB_CACHE, then check
    python3 data/fetch/mundell37.py --offline    # use the cache only
    python3 data/fetch/mundell37.py --write      # also (re)write data/snapshots/canada_float_1946_1965.csv

Two snapshots. mundell_facts holds the quotations of the chapter's sources with their page: Powell, A History of the
Canadian Dollar (Bank of Canada, 2005) and the Bank's terms of use; the Annual Reports of the Bank of Canada for 1961
and 1962 (the Bank's open archive); Historical Statistics of Canada (Statistics Canada, 1983: the CSV files of series
J560-567 and J471-480, the page of Section J and the catalogue page) and the Statistics Canada Open Licence; the
Economic Report of the President 1964 (Table C-48); Fleming (1962) and Boughton (2003) in the IMF eLibrary; Mundell
(1963) on Cambridge Core; the Nobel press release of 1999; Obstfeld, Shambaugh and Taylor (NBER Working Paper 10396);
Rey (NBER Working Paper 21162); Mongelli (ECB Working Paper 138); the Central Bank of Sri Lanka's Annual Report 2022,
chapter 5; the authority records of the Library of Congress and of the Deutsche Nationalbibliothek (lobid.org). Its
.json lists every document with a URL and the SHA-256 of the copy read; this script fetches each one into the cache
with verify_web_quotes.fetch (documents only; no program that comes with a download is run) and stops if a hash
differs. The quotations themselves are checked by data/fetch/verify_web_quotes.py.

canada_float_1946_1965 holds the yearly series of the chapter's figure and example: the high, low and average of the
Canadian-dollar price of the US dollar (Historical Statistics of Canada, J560-562), the yield of Canada's 3-month
treasury bills (J471) and that of the United States (Economic Report of the President 1964, Table C-48, the first
column, read from the text layer of PDF page 273 with pdftotext -layout). This script reads the three documents from
the cache, compares what it reads with the snapshot (or writes it with --write) and then runs checks/check_ch37.py.
"""
from __future__ import annotations

import csv
import io
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verify_web_quotes import fetch  # noqa: E402

ROOT = HERE.parents[1]
SNAPSHOTS = ["mundell_facts"]
DATA = ROOT / "data" / "snapshots" / "canada_float_1946_1965.csv"
YEARS = range(1946, 1966)
COLUMNS = ["year", "cad_per_usd_high", "cad_per_usd_low", "cad_per_usd_avg", "ca_tbill_3m", "us_tbill_3m"]


def sources() -> dict[str, dict]:
    """Every source named by the snapshots (a key names the same document in each of them)."""
    out: dict[str, dict] = {}
    for name in SNAPSHOTS:
        meta = json.loads((ROOT / "data" / "snapshots" / f"{name}.json").read_text(encoding="utf-8"))
        assert meta["fetch"] == "data/fetch/mundell37.py", name
        for key, src in meta["sources"].items():
            if key in out and out[key]["sha256"] != src["sha256"]:
                raise SystemExit(f"{key}: two hashes in the snapshots ({name})")
            out[key] = src
    return out


def hsc_rows(path: Path, encoding: str) -> dict[int, list[str]]:
    """The year rows of a CSV file of Historical Statistics of Canada: year -> the fields after the year."""
    out = {}
    for row in csv.reader(io.StringIO(path.read_text(encoding=encoding))):
        if len(row) > 2 and re.fullmatch(r"19\d\d", row[1]):
            out[int(row[1])] = row[2:]
    return out


def erp_bills(path: Path) -> dict[int, str]:
    """Table C-48 of the Economic Report of the President 1964: year -> the 3-month Treasury bill rate as printed
    (the first figure of the year's line; the monthly lines of 1961-63 start with a month or 'YYYY*')."""
    text = subprocess.run(["pdftotext", "-layout", "-f", "273", "-l", "273", str(path), "-"], capture_output=True,
                          text=True, check=True).stdout
    assert "TABLE C-48" in text, "not Table C-48"
    out = {}
    for line in text.splitlines():
        m = re.match(r"(19[2-6]\d)\b[\s_\-]*\s+(\d?\.\d{3})\s", line)
        if m:
            out[int(m.group(1))] = m.group(2)
    return out


def series(cache: dict[str, Path]) -> list[dict[str, str]]:
    fx = hsc_rows(cache["hsc_j560"], "utf-8")
    yields = hsc_rows(cache["hsc_j471"], "latin-1")
    us = erp_bills(cache["erp1964"])
    rows = []
    for y in YEARS:
        h, l, a = fx[y][:3]
        us_y = us.get(y, "")
        if us_y.startswith("."):
            us_y = "0" + us_y
        rows.append(dict(zip(COLUMNS, [str(y), h, l, a, yields[y][0], us_y])))
    assert all(r["us_tbill_3m"] for r in rows if int(r["year"]) <= 1963) and not rows[-1]["us_tbill_3m"]
    return rows


def main(offline: bool, write: bool) -> None:
    cache = {}
    for key, src in sorted(sources().items()):
        path, note = fetch(key, src, offline)
        if path is None or note:
            raise SystemExit(f"{key}: {note}")
        cache[key] = path
        print(f"ok {key} {src['sha256'][:16]}")
    rows = series(cache)
    if write:
        with DATA.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, COLUMNS, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        print(f"wrote {DATA.relative_to(ROOT)} ({len(rows)} years)")
    with DATA.open(encoding="utf-8") as fh:
        assert list(csv.DictReader(fh)) == rows, f"{DATA.name} differs from the documents"
    print(f"ok {DATA.name}: {len(rows)} years read again from the documents")
    subprocess.run([sys.executable, str(ROOT / "checks" / "check_ch37.py")], check=True)


if __name__ == "__main__":
    main("--offline" in sys.argv[1:], "--write" in sys.argv[1:])
