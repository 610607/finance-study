"""The sources of Chapter 42: download them into the web cache, compare their hashes, rebuild the data snapshots, check.

    python3 data/fetch/eastasia42.py              # download what is missing from WEB_CACHE, then check
    python3 data/fetch/eastasia42.py --offline    # use the cache only
    python3 data/fetch/eastasia42.py --write      # also (re)write pwt1001_eastasia.csv and cpf_rates_1955_2026.csv

Three snapshots. eastasia_facts holds the quotations of the chapter's sources with their page: the World Bank's news
release 93/S17 of 26 September 1993 and its report The East Asian Miracle (1993), the scan on documents.worldbank.org
(the copyright page, a sentence of page 308, the footnote on China of page 1 and a row of the timeline of page 154 read
on the page images); Young (1994), NBER Working Paper 4680; Young (1992), the NBER's selection of the NBER
Macroeconomics Annual 1992 with the comments of Krugman and Barro; Rodrik (1994), NBER Working Paper 4964 (its text
layer is unusable: the rows are read on the page images); Collins and Bosworth (1996), the Brookings PDF with Rodrik's
comment, and the Brookings terms of use; Krugman (1994), a JSTOR-derived copy on cooperative-individualism.org (read
to verify, not committed); the abstract of Hsieh (2002) on IDEAS; the Economic White Papers of 1956 and 1961
(経済企画庁, on www5.cao.go.jp) and the Cabinet Office's terms of use; the Taiwanese statute on the period of martial law
and article 9 of Taiwan's Copyright Act; the World Bank's page on Lewis T. Preston; the Singapore Open Data Licence;
the authority records of the Library of Congress and the Deutsche Nationalbibliothek (lobid.org). Its .json lists every
document with a URL and the SHA-256 of the copy read; this script fetches each one into the cache with
verify_web_quotes.fetch (documents only; no program that comes with a download is run) and stops if a hash differs.
The quotations themselves are checked by data/fetch/verify_web_quotes.py, the numbers read from them by
checks/check_ch42.py.

pwt1001_eastasia is read from the workbook pwt1001.xlsx of Penn World Table 10.01 (sheet Data; DOCS below; CC BY 4.0,
cite Feenstra, Inklaar and Timmer 2015): Japan, the Republic of Korea, Taiwan, Hong Kong, Singapore and the United
States, every year 1950-2019, with rgdpna, rnna, emp, avh, hc, labsh, rgdpe, pop and csh_i and the workbook's own flags
i_outlier and i_xr. cpf_rates_1955_2026 is read from the dataset 'CPF contribution rates' of the Central Provident Fund
Board on data.gov.sg (DOCS below; Singapore Open Data Licence version 1.0): the rows of the age group '35 years & below'.
The figures are written as the sources store them (repr of the float for the workbook, the text of the dataset). This
script compares what it reads with the snapshots (or writes them with --write), then runs checks/check_ch42.py.
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
PWT = SNAP / "pwt1001_eastasia.csv"
CPF = SNAP / "cpf_rates_1955_2026.csv"
FETCH = "data/fetch/eastasia42.py"
# the data files of the two data snapshots (their addresses and hashes are also in the snapshots' notes)
DOCS = {
    "pwt1001_xlsx": {"url": "https://dataverse.nl/api/access/datafile/354095", "format": "xlsx",
                     "sha256": "bf2b66c5fd8b465870eeab8bbfa3a57e73253a3236a933286259efbbb5fb67a2"},
    "cpf_rates42": {"url": "https://data.gov.sg/api/action/datastore_search?resource_id="
                           "d_98ffa142ae0dec40391f78f81d26aca9&limit=1000", "format": "json",
                    "sha256": None},
    "cpf_meta42": {"url": "https://api-production.data.gov.sg/v2/public/api/datasets/"
                          "d_98ffa142ae0dec40391f78f81d26aca9/metadata", "format": "json", "sha256": None},
}
CODES = ("JPN", "KOR", "TWN", "HKG", "SGP", "USA")
PWT_COLUMNS = ["countrycode", "country", "year", "rgdpna", "rnna", "emp", "avh", "hc", "labsh", "rgdpe", "pop", "csh_i",
               "i_outlier", "i_xr"]
CPF_COLUMNS = ["effective_from", "age_grp", "contributing_party", "contribution_rate"]
AGE = "35 years & below"
FIRST, LAST = 1950, 2019


def docs() -> dict[str, dict]:
    """The data files, with the hashes recorded in the snapshots' notes (the CPF files are dated there)."""
    out = {k: dict(v) for k, v in DOCS.items()}
    for snap, keys in ((PWT, ("pwt1001_xlsx",)), (CPF, ("cpf_rates42", "cpf_meta42"))):
        data = json.loads(snap.with_suffix(".json").read_text(encoding="utf-8"))
        assert data["fetch"] == FETCH
        for key in keys:
            notes = data["notes"]
            k = notes.index(out[key]["url"])
            sha = notes[k:].split("SHA-256 ", 1)[1][:64]
            assert out[key]["sha256"] in (None, sha), key
            out[key]["sha256"] = sha
    return out


def sources() -> dict[str, dict]:
    meta = json.loads((SNAP / "eastasia_facts.json").read_text(encoding="utf-8"))
    assert meta["fetch"] == FETCH
    return {k: v for k, v in meta["sources"].items() if v["format"] != "image"}


def num(v) -> str:
    return "" if v is None else repr(float(v))


def workbook(path: Path) -> list[dict[str, str]]:
    import openpyxl
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True)["Data"]
    rows = ws.iter_rows(values_only=True)
    head = list(next(rows))
    out = []
    for r in rows:
        d = dict(zip(head, r))
        if d["countrycode"] in CODES and FIRST <= int(d["year"]) <= LAST:
            out.append(dict(zip(PWT_COLUMNS, [d["countrycode"], d["country"], str(int(d["year"]))]
                                + [num(d[c]) for c in PWT_COLUMNS[3:12]] + [d["i_outlier"] or "", d["i_xr"] or ""])))
    out.sort(key=lambda x: (CODES.index(x["countrycode"]), int(x["year"])))
    return out


def cpf(path: Path) -> list[dict[str, str]]:
    d = json.loads(path.read_text(encoding="utf-8"))
    recs = d["result"]["records"]
    assert d["result"]["total"] == len(recs), "the dataset has more rows than one page"
    out = [{c: str(r[c]) for c in CPF_COLUMNS} for r in recs if r["age_grp"] == AGE]
    return sorted(out, key=lambda x: (x["effective_from"], x["contributing_party"]))


def main(offline: bool, write: bool) -> None:
    cache = {}
    for key, src in sorted({**sources(), **docs()}.items()):
        path, note = fetch(key, src, offline)
        if path is None or note:
            raise SystemExit(f"{key}: {note}")
        cache[key] = path
        print(f"ok {key} {src['sha256'][:16]}")
    meta = json.loads(cache["cpf_meta42"].read_text(encoding="utf-8"))["data"]
    assert meta["name"] == "CPF contribution rates" and meta["managedBy"] == "Central Provident Fund Board"
    for snap, columns, rows in ((PWT, PWT_COLUMNS, workbook(cache["pwt1001_xlsx"])),
                                (CPF, CPF_COLUMNS, cpf(cache["cpf_rates42"]))):
        if write:
            with snap.open("w", encoding="utf-8", newline="") as fh:
                w = csv.DictWriter(fh, columns, lineterminator="\n")
                w.writeheader()
                w.writerows(rows)
            print(f"wrote {snap.relative_to(ROOT)} ({len(rows)} rows)")
        with snap.open(encoding="utf-8") as fh:
            assert list(csv.DictReader(fh)) == rows, f"{snap.name} differs from its source"
        print(f"ok {snap.name}: {len(rows)} rows read again from the source")
    subprocess.run([sys.executable, str(ROOT / "checks" / "check_ch42.py")], check=True)


if __name__ == "__main__":
    main("--offline" in sys.argv[1:], "--write" in sys.argv[1:])
