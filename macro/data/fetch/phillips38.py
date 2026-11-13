"""The sources of Chapter 38: download them into the web cache, compare their hashes, rebuild the data snapshot, check.

    python3 data/fetch/phillips38.py              # download what is missing from WEB_CACHE, then check
    python3 data/fetch/phillips38.py --offline    # use the cache only
    python3 data/fetch/phillips38.py --write      # also (re)write data/snapshots/menu_us_canada_1946_1969.csv

Two snapshots. phillips_facts holds the quotations of the chapter's sources with their page: Phillips (Economica,
1958) and Samuelson and Solow (The American Economic Review, 1960), the JSTOR scans that two university course pages
post (read to verify; the address, date and SHA-256 of each copy are in the .json, the files are not committed); the
Economic Reports of the President of January 1962 and February 1971 (The American Presidency Project); Okun (1962,
Cowles Foundation Paper 190) and Klein (1950, Cowles Commission Monograph 11), scans without a text layer, read on the
page images, and the Cowles Foundation's pages; Friedman's Nobel lecture (1976) and the Nobel pages of 1980 on Klein;
Fisher (1926) in the International Labour Review and the ILO's terms; the Science Museum Group's pages on Phillips and
his machine; Historical Statistics of Canada (series D491-497 and K8-18, the pages of sections D and K) and the
Statistics Canada Open Licence; the authority records of the Library of Congress, the Deutsche Nationalbibliothek
(lobid.org) and the Bibliothèque nationale de France, and the Internet Archive's record of Klein and Goldberger. Its
.json lists every document with a URL and the SHA-256 of the copy read; this script fetches each one into the cache
with verify_web_quotes.fetch (documents only; no program that comes with a download is run) and stops if a hash
differs, except for the page of the Science Museum Group's object, which prints the date on which it is read. The
quotations themselves are checked by data/fetch/verify_web_quotes.py, the numbers read from them by
checks/check_ch38.py.

menu_us_canada_1946_1969 holds the yearly series of the chapter's menu figure: the unemployment rate of all workers in
the United States (Economic Report of the President 1971, Table C-24, the first column, 1948-1969, read from the text
layer of PDF page 231 with pdftotext -layout), the consumer price index for city wage earners and clerical workers
(Table C-45, all items, 1967 = 100, PDF page 255; the text layer reads the years 1968 and 1969 as '1958' and '1989',
and the lines are read by their position after 1967), Canada's unemployment rate (Historical Statistics of Canada,
D491, Canada total) and consumer price index (K8, total, 1971 = 100). This script reads the four documents from the
cache, compares what it reads with the snapshot (or writes it with --write) and then runs checks/check_ch38.py.
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
SNAPSHOTS = ["phillips_facts", "menu_us_canada_1946_1969"]
DATA = ROOT / "data" / "snapshots" / "menu_us_canada_1946_1969.csv"
YEARS = range(1946, 1970)
COLUMNS = ["year", "us_unemp_pct", "us_cpi_1967_100", "ca_unemp_pct", "ca_cpi_1971_100"]
DATED = {"smg_moniac38"}          # the page prints the day it is read ("Accessed 29 October 2026")


def sources() -> dict[str, dict]:
    """Every source named by the snapshots (a key names the same document in each of them)."""
    out: dict[str, dict] = {}
    for name in SNAPSHOTS:
        meta = json.loads((ROOT / "data" / "snapshots" / f"{name}.json").read_text(encoding="utf-8"))
        assert meta["fetch"] == "data/fetch/phillips38.py", name
        for key, src in meta.get("sources", {}).items():
            if key in out and out[key]["sha256"] != src["sha256"]:
                raise SystemExit(f"{key}: two hashes in the snapshots ({name})")
            out[key] = src
    return out


def layout(path: Path, page: int) -> str:
    return subprocess.run(["pdftotext", "-layout", "-f", str(page), "-l", str(page), str(path), "-"],
                          capture_output=True, text=True, check=True).stdout


def us_unemployment(path: Path) -> dict[int, str]:
    """Table C-24 of the Economic Report of the President 1971: year -> the rate of all workers as printed."""
    text = layout(path, 231)
    assert "TABLE C-24" in text and "Selected unemployment rates, 1948-70" in text, "not Table C-24"
    out = {}
    for line in text.split("Seasonally adjusted")[0].splitlines():
        m = re.match(r"(19[4-7]\d)\.\s+(\d+\.\d)\s", line)
        if m:
            out[int(m.group(1))] = m.group(2)
    assert sorted(out) == list(range(1948, 1971)), sorted(out)
    return out


def us_cpi(path: Path) -> dict[int, str]:
    """Table C-45 of the Economic Report of the President 1971: year -> all items (1967 = 100) as printed. The yearly
    lines run from 1929 to 1970; the text layer reads 1968 and 1969 as '1958' and '1989' and 1970 as '1970i' (the
    footnote of an eleven-month average), so the lines after 1967 are read by their position."""
    text = layout(path, 255)
    assert "TABLE C-45" in text and "[1967=100]" in text, "not Table C-45"
    lines = [re.match(r"(\d{4})\S*\s+(\d+\.\d)\s", l) for l in text.split("1969: Jan")[0].splitlines()]
    printed = [(m.group(1), m.group(2)) for m in lines if m]
    assert [p[0] for p in printed[-4:]] == ["1967", "1958", "1989", "1970"], printed[-4:]
    assert [int(p[0]) for p in printed[:-3]] == list(range(1929, 1968))
    return {1929 + i: v for i, (_, v) in enumerate(printed)}


def hsc_rows(path: Path) -> dict[int, list[str]]:
    """The year rows of a CSV file of Historical Statistics of Canada (Latin-1): year -> the fields after the year."""
    out = {}
    for row in csv.reader(io.StringIO(path.read_text(encoding="latin-1"))):
        if len(row) > 2 and re.fullmatch(r"19\d\d", row[1]):
            out[int(row[1])] = row[2:]
    return out


def series(cache: dict[str, Path]) -> list[dict[str, str]]:
    un, cpi = us_unemployment(cache["erp1971"]), us_cpi(cache["erp1971"])
    d491, k8 = hsc_rows(cache["hsc_d491"]), hsc_rows(cache["hsc_k8"])
    rows = []
    for y in YEARS:
        ca_u = d491[y][1]                       # after the empty field: Canada total
        rows.append(dict(zip(COLUMNS, [str(y), un.get(y, ""), cpi[y], ca_u, k8[y][0]])))
    assert all(r["us_unemp_pct"] for r in rows if int(r["year"]) >= 1948)
    assert all(re.fullmatch(r"\d+\.\d", r[c]) for r in rows for c in COLUMNS[2:])
    return rows


def main(offline: bool, write: bool) -> None:
    cache = {}
    for key, src in sorted(sources().items()):
        path, note = fetch(key, src, offline)
        if path is None or (note and key not in DATED):
            raise SystemExit(f"{key}: {note}")
        cache[key] = path
        print(f"ok {key} {src['sha256'][:16]}" + (f" ({note})" if note else ""))
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
    subprocess.run([sys.executable, str(ROOT / "checks" / "check_ch38.py")], check=True)


if __name__ == "__main__":
    main("--offline" in sys.argv[1:], "--write" in sys.argv[1:])
