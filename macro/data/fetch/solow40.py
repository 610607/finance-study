"""The sources of Chapter 40: download them into the web cache, compare their hashes, rebuild the data snapshots, check.

    python3 data/fetch/solow40.py              # download what is missing from WEB_CACHE, then check
    python3 data/fetch/solow40.py --offline    # use the cache only
    python3 data/fetch/solow40.py --write      # also (re)write data/snapshots/pwt1001_convergence.csv and pwt1001_usa.csv

Three snapshots. solow_facts holds the quotations of the chapter's sources with their page: Solow's Nobel lecture of 8
December 1987 and the Nobel page of the prize (nobelprize.org); Harrod (1939), Solow (1956, 1957), Phelps (1961) and
Baumol (1986), the JSTOR copies on Thomas Piketty's page at the Paris School of Economics (read to verify, not
committed), several of whose pages are read on the page images; Swan (1956) and the index of Econometrica 14 (1946),
the microfilm scans on archive.org with their metadata records; Abramovitz (1956), the NBER's PDF; the NBER working
papers of De Long (1987), Barro (1989), Barro and Sala-i-Martin (1990) and Mankiw, Romer and Weil (1990); Pritchett
(1995) and Easterly and Fischer (1995), the PDFs of documents.worldbank.org; the study of Soviet GNP printed for the
Joint Economic Committee (1990), the microfiche scan on archive.org; Part II of the Survey of Current Business of May
1972 (Jorgenson and Griliches, Denison), the BEA's PDF; the record of Penn World Table 10.01 on DataverseNL; the
authority records of the Library of Congress and the Deutsche Nationalbibliothek (lobid.org). Its .json lists every
document with a URL and the SHA-256 of the copy read; this script fetches each one into the cache with
verify_web_quotes.fetch (documents only; no program that comes with a download is run) and stops if a hash differs.
The quotations themselves are checked by data/fetch/verify_web_quotes.py, the numbers read from them by
checks/check_ch40.py.

pwt1001_convergence and pwt1001_usa are read from the workbook pwt1001.xlsx of Penn World Table 10.01 (sheet Data;
DOCS below; CC BY 4.0, cite Feenstra, Inklaar and Timmer 2015). pwt1001_convergence has one row for each country with
rgdpe, rgdpna and pop in 1960 and rgdpna and pop in 2019 and with csh_i in every year from 1960 to 2019: those figures,
the mean of csh_i over the 60 years and hc in 1960 (empty where the workbook has none). pwt1001_usa has the United
States' rgdpna, emp, rnna, labsh and pop for 1950-2019. The figures are written as the workbook stores them (repr of
the float). This script compares what it reads with the snapshots (or writes them with --write), then runs
checks/check_ch40.py.
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verify_web_quotes import fetch  # noqa: E402

ROOT = HERE.parents[1]
SNAP = ROOT / "data" / "snapshots"
CONV = SNAP / "pwt1001_convergence.csv"
USA = SNAP / "pwt1001_usa.csv"
FETCH = "data/fetch/solow40.py"
# the workbook of the data snapshots (its address and hash are also in the snapshots' notes)
DOCS = {
    "pwt1001_xlsx": {"url": "https://dataverse.nl/api/access/datafile/354095", "format": "xlsx",
                     "sha256": "bf2b66c5fd8b465870eeab8bbfa3a57e73253a3236a933286259efbbb5fb67a2"},
}
CONV_COLUMNS = ["countrycode", "country", "rgdpe_1960", "rgdpna_1960", "pop_1960", "rgdpna_2019", "pop_2019",
                "csh_i_mean_1960_2019", "hc_1960"]
USA_COLUMNS = ["year", "rgdpna", "emp", "rnna", "labsh", "pop"]
FIRST, LAST = 1960, 2019


def sources() -> dict[str, dict]:
    meta = json.loads((SNAP / "solow_facts.json").read_text(encoding="utf-8"))
    assert meta["fetch"] == FETCH
    for snap in (CONV, USA):
        data = json.loads(snap.with_suffix(".json").read_text(encoding="utf-8"))
        assert data["fetch"] == FETCH
        for key, doc in DOCS.items():
            assert f"{doc['url']} (SHA-256 {doc['sha256']})" in data["notes"], (snap.name, key)
    return meta["sources"]


def workbook(path: Path) -> dict[str, dict[int, dict]]:
    """countrycode -> year -> the row of sheet Data (with the country's name under 'country')."""
    import openpyxl
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True)["Data"]
    rows = ws.iter_rows(values_only=True)
    head = list(next(rows))
    out: dict[str, dict[int, dict]] = {}
    for r in rows:
        d = dict(zip(head, r))
        out.setdefault(d["countrycode"], {})[int(d["year"])] = d
    return out


def num(v) -> str:
    return "" if v is None else repr(float(v))


def convergence(data) -> list[dict[str, str]]:
    out = []
    for code in sorted(data):
        d = data[code]
        a, b = d.get(FIRST), d.get(LAST)
        if not a or not b or None in (a["rgdpe"], a["rgdpna"], a["pop"], b["rgdpna"], b["pop"]):
            continue
        csh = [d[y]["csh_i"] for y in range(FIRST, LAST + 1)]
        if any(v is None for v in csh):
            continue
        out.append(dict(zip(CONV_COLUMNS, [code, a["country"], num(a["rgdpe"]), num(a["rgdpna"]), num(a["pop"]),
                                           num(b["rgdpna"]), num(b["pop"]), num(sum(csh) / len(csh)),
                                           num(a["hc"])])))
    return out


def usa(data) -> list[dict[str, str]]:
    d = data["USA"]
    return [dict(zip(USA_COLUMNS, [str(y)] + [num(d[y][c]) for c in USA_COLUMNS[1:]])) for y in range(1950, LAST + 1)]


def main(offline: bool, write: bool) -> None:
    cache = {}
    for key, src in sorted({**sources(), **DOCS}.items()):
        path, note = fetch(key, src, offline)
        if path is None or note:
            raise SystemExit(f"{key}: {note}")
        cache[key] = path
        print(f"ok {key} {src['sha256'][:16]}")
    data = workbook(cache["pwt1001_xlsx"])
    for snap, columns, rows in ((CONV, CONV_COLUMNS, convergence(data)), (USA, USA_COLUMNS, usa(data))):
        if write:
            with snap.open("w", encoding="utf-8", newline="") as fh:
                w = csv.DictWriter(fh, columns, lineterminator="\n")
                w.writeheader()
                w.writerows(rows)
            print(f"wrote {snap.relative_to(ROOT)} ({len(rows)} rows)")
        with snap.open(encoding="utf-8") as fh:
            assert list(csv.DictReader(fh)) == rows, f"{snap.name} differs from the workbook"
        print(f"ok {snap.name}: {len(rows)} rows read again from the workbook")
    subprocess.run([sys.executable, str(ROOT / "checks" / "check_ch40.py")], check=True)


if __name__ == "__main__":
    main("--offline" in sys.argv[1:], "--write" in sys.argv[1:])
