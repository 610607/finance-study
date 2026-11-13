"""The sources of Chapter 45: download them into the web cache, compare their hashes, rebuild the series, check.

    python3 data/fetch/monetarism45.py              # download what is missing from WEB_CACHE, compare, then check
    python3 data/fetch/monetarism45.py --offline    # use the cache only
    python3 data/fetch/monetarism45.py --write      # also rewrite the series snapshot from the two tables

Two snapshots:
  monetarism_facts            the quotations of the chapter's sources with their page: Friedman and Schwartz, 'Money
                              and Business Cycles', with Minsky's comment (NBER's PDF of the chapter); Friedman (AER,
                              March 1968); Poole and Lieberman (BPEA 1972:2), Modigliani and Papademos (BPEA 1975:1),
                              Goldfeld (BPEA 1976:3); the records of policy actions of the FOMC of 6 October 1979,
                              1-2 February 1982 and 5 October 1982; the Budget statements of 1980, 1986 and 1987
                              (historic Hansard); the Bank of England's Quarterly Bulletin of March 1981 and the
                              Governor's lecture of October 1986; Bouey's speeches of November and December 1982 (the
                              Bank of Canada's open archive); Moses (RBA RDP 8301, 1983); Rich (ECB WP 236, 2003);
                              Gerberding, Worms and Seitz (Bundesbank DP 25/2004); tables B-1 and B-67 of the Economic
                              Report of the President of 2000; the terms of the AEA, Brookings, the Bank of England,
                              the Bank of Canada and the RBA; the authority records of the Library of Congress and the
                              GND (lobid.org)
  monetarism_us_1959_1999     GDP (B-1, first column) and the December averages of M1 and M2 (B-67, first two
                              columns), billions of dollars, read from the -layout text of the two PDFs

The .json of monetarism_facts lists every document with a URL and the SHA-256 of the copy read; the series lists its
two under "documents". This script fetches each into the cache with verify_web_quotes.fetch (documents only; no program
that comes with a download is run). A source of format "image" names a PDF whose pages were read by eye on images
rendered with pdftoppm; it is the same file as the PDF source and is not fetched again. A PDF whose hash differs stops
the run. A web page or authority record (DATED: they carry the day's scripts, dates and record updates) is reported and
the run goes on: its quotations are checked by data/fetch/verify_web_quotes.py. Without --write the series is rebuilt
in memory and compared with the snapshot. checks/check_ch45.py runs last.
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
SNAP = ROOT / "data" / "snapshots"
FETCH = "data/fetch/monetarism45.py"
DATED = ("html", "json")                              # formats whose copies change from day to day
US = "monetarism_us_1959_1999"
YEARS = range(1959, 2000)
HEADER = ["year", "gdp_bn", "m1_dec_bn", "m2_dec_bn"]


def documents() -> dict[str, dict]:
    """Every document of the two snapshots: key -> url, format, sha256."""
    out: dict[str, dict] = {}
    for name, field in (("monetarism_facts", "sources"), (US, "documents")):
        meta = json.loads((SNAP / f"{name}.json").read_text(encoding="utf-8"))
        assert meta["fetch"] == FETCH, name
        for key, src in meta[field].items():
            if key in out:
                assert (out[key]["url"], out[key]["sha256"]) == (src["url"], src["sha256"]), key
            out[key] = src
    return out


def number(s: str) -> float:
    """A figure of the ERP tables: '9,248.4' -> 9248.4, '−1.7' -> -1.7, '.5' -> 0.5."""
    return float(s.replace(",", "").replace("−", "-"))


def erp_rows(path: Path, page: int = 1) -> dict[int, list[float]]:
    """The yearly rows of one page of an ERP table, from pdftotext -layout: year -> the figures of the row. The
    preliminary year is printed '1999 p'; a run of points ('..........') marks a figure not given."""
    text = subprocess.run(["pdftotext", "-enc", "UTF-8", "-layout", "-f", str(page), "-l", str(page), str(path), "-"],
                          capture_output=True, text=True, check=True).stdout
    out: dict[int, list[float]] = {}
    for line in text.splitlines():
        m = re.match(r"\s*(\d{4})( p)? \.{5,}\s+(.*)$", line)
        if m:
            year = int(m.group(1))
            assert year not in out, (path.name, year)
            out[year] = [number(t) for t in m.group(3).split() if not t.startswith(".....")]
    return out


def us_series(paths: dict[str, Path]) -> list[list]:
    b1, b67 = erp_rows(paths["erpb1_45"], 1), erp_rows(paths["erpb67_45"], 1)
    assert set(YEARS) <= set(b1) and set(YEARS) <= set(b67)
    return [[y, b1[y][0], b67[y][0], b67[y][1]] for y in YEARS]


def render(rows: list[list]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(HEADER)
    w.writerows(rows)
    return buf.getvalue()


def main(offline: bool, write: bool) -> None:
    paths: dict[str, Path] = {}
    for key, src in sorted(documents().items()):
        if src["format"] == "image":
            print(f"-- {key}: read on page images ({src['url']}), not fetched")
            continue
        path, note = fetch(key, src, offline)
        if path is None:
            raise SystemExit(f"{key}: {note}")
        if note and src["format"] not in DATED:
            raise SystemExit(f"{key}: {note}")
        print(f"{'NOTE' if note else 'ok'} {key} {src['sha256'][:16]}{' ' + note if note else ''}")
        paths[key] = path
    rows = us_series(paths)
    text = render(rows)
    out = SNAP / f"{US}.csv"
    if write:
        out.write_text(text, encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)} ({len(rows)} years)")
    else:
        assert out.read_text(encoding="utf-8") == text, f"{US}.csv differs from the documents"
        print(f"ok {US}.csv matches the documents ({len(rows)} years)")
    subprocess.run([sys.executable, str(ROOT / "checks" / "check_ch45.py")], check=True)


if __name__ == "__main__":
    main("--offline" in sys.argv[1:], "--write" in sys.argv[1:])
