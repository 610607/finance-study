"""The sources of Chapter 47: download them into the web cache, compare their hashes, rebuild the data snapshots, check.

    python3 data/fetch/oil47.py              # download what is missing from WEB_CACHE, compare, then check
    python3 data/fetch/oil47.py --offline    # use the cache only
    python3 data/fetch/oil47.py --write      # also rewrite the three data snapshots from the documents

Four snapshots:
  oil_facts        the quotations of the chapter's sources with their page: FRUS 1969-1976 vol. XXXVI documents 209,
                   216, 220, 223, 271, 273, 277 and the volume's list of persons (history.state.gov); the BIS Annual
                   Reports of 1974, 1975 and 1980 (text layers) and Hutchison (BIS Working Paper 13, page images);
                   Gordon (BPEA 1975:1) and Bernanke, Gertler and Watson (BPEA 1997:1); the NBER working papers of
                   Hamilton (2011) and Blanchard and Gali (2007) (text layers) and of Barsky and Kilian (2001) and Sachs
                   and Warner (1995) (page images); Corden and Neary (IIASA CP-82-58); Mehlum, Moene and Torvik (Oslo
                   memorandum 29/2002); Budina, Pang and van Wijnbergen (World Bank PRWP 4256) with its record; the Bank
                   of Japan's history, vol. 6 (page images); the terms of the BIS, the Bank of Japan and the World Bank;
                   the records of the persons named (Library of Congress, Deutsche Nationalbibliothek, NDL)
  oil_pinksheet    the World Bank's annual crude-oil price (average of Brent, Dubai and WTI), nominal and real 2010 US
                   dollars a barrel, 1960-2025, from the annual workbook of the Pink Sheet
  oil_wdi          World Development Indicators: consumer-price inflation of the G7 and Switzerland 1965-1990; fuel,
                   food and agricultural raw materials as shares of merchandise exports and manufacturing value added
                   as a share of GDP for Nigeria, the Netherlands, Norway and the United Kingdom 1960-1990; total
                   natural-resource rents (% of GDP) of every economy that is not an aggregate, 1970 and 1990
  oil_pwt          Penn World Table 10.01: rgdpe, rgdpna and pop of every country in 1970, 1990 and 2019, and of the G7
                   and Switzerland in 1969-1985

The .json of oil_facts lists every document with a URL and the SHA-256 of the copy read; the data snapshots list theirs
under "documents". This script fetches each into the cache with verify_web_quotes.fetch (documents only; no program
that comes with a download is run). A source of format "image" names a PDF whose pages were read by eye on images
rendered with pdftoppm and is not fetched here. A PDF whose hash differs stops the run. A web page, an authority record,
an API answer or the Pink Sheet workbook (DATED: they carry the day's scripts, record updates, data revisions and the
monthly update of the workbook) is reported and the run goes on: the quotations are checked by
data/fetch/verify_web_quotes.py, and the data snapshots are rebuilt from the documents and compared. Without --write a
difference stops the run. checks/check_ch47.py runs last.
"""
from __future__ import annotations

import csv
import io
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verify_web_quotes import fetch  # noqa: E402

ROOT = HERE.parents[1]
SNAP = ROOT / "data" / "snapshots"
FETCH = "data/fetch/oil47.py"
DATED = ("html", "json", "txt", "xlsx")
DATA = ("oil_pinksheet", "oil_wdi", "oil_pwt")
G8 = ("USA", "JPN", "DEU", "FRA", "GBR", "ITA", "CAN", "CHE")    # the G7 and Switzerland
PRODUCERS = ("NGA", "NLD", "NOR", "GBR")
WDI = {"wdicpi_47": "FP.CPI.TOTL.ZG", "wdifuel_47": "TX.VAL.FUEL.ZS.UN", "wdifood_47": "TX.VAL.FOOD.ZS.UN",
       "wdiagri_47": "TX.VAL.AGRI.ZS.UN", "wdimanf_47": "NV.IND.MANF.ZS", "wdirents_47": "NY.GDP.TOTL.RT.ZS"}
RENT_YEARS = (1970, 1990)
PWT_YEARS = (1970, 1990, 2019)
G8_YEARS = range(1969, 1986)


def documents() -> dict[str, dict]:
    """Every document of the four snapshots: key -> url, format, sha256."""
    out: dict[str, dict] = {}
    for name, field in (("oil_facts", "sources"), *((d, "documents") for d in DATA)):
        meta = json.loads((SNAP / f"{name}.json").read_text(encoding="utf-8"))
        assert meta["fetch"] == FETCH, name
        for key, src in meta[field].items():
            if key in out:
                assert (out[key]["url"], out[key]["sha256"]) == (src["url"], src["sha256"]), key
            out[key] = src
    return out


def num(v) -> str:
    return "" if v is None else repr(float(v))


def definitions(name: str):
    return json.loads((SNAP / f"{name}.json").read_text(encoding="utf-8"))["definitions"]


def pinksheet(path: Path) -> str:
    """year, the crude-oil average in nominal and in real 2010 dollars a barrel, as the workbook stores them."""
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    for d in definitions("oil_pinksheet"):      # the words of the workbook that the snapshot's metadata quote
        col, row = ord(d["cell"][0]) - ord("A"), int(d["cell"][1:]) - 1
        got = list(wb[d["sheet"]].iter_rows(values_only=True, min_row=row + 1, max_row=row + 1))[0][col]
        assert got == d["text"], (d, got)
    cols = {}
    for sheet, name in (("Annual Prices (Nominal)", "crude_nominal"), ("Annual Prices (Real)", "crude_real")):
        rows = list(wb[sheet].iter_rows(values_only=True))
        assert rows[6][1] == "Crude oil, average" and rows[7][1] == "($/bbl)", sheet
        cols[name] = {int(r[0]): r[1] for r in rows[8:] if isinstance(r[0], int) and isinstance(r[1], (int, float))}
    years = sorted(cols["crude_nominal"])
    assert years == sorted(cols["crude_real"]) and years[0] == 1960
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["year", "crude_nominal", "crude_real"])
    for y in years:
        w.writerow([y, num(cols["crude_nominal"][y]), num(cols["crude_real"][y])])
    return buf.getvalue()


def wdi(paths: dict[str, Path]) -> str:
    """indicator, countrycode, country, year, value: the observations kept (see the module's docstring)."""
    countries = json.loads(paths["wdicountries_47"].read_text(encoding="utf-8"))[1]
    aggregates = {c["id"] for c in countries if c["region"]["id"] == "NA"}
    out = []
    for key, ind in WDI.items():
        head, rows = json.loads(paths[key].read_text(encoding="utf-8"))
        assert head["pages"] == 1, key
        for r in rows:
            assert r["indicator"]["id"] == ind, key
            assert r["indicator"]["value"] == definitions("oil_wdi")[ind], key
            c, y, v = r["countryiso3code"], int(r["date"]), r["value"]
            if v is None or not c or c in aggregates:
                continue
            if ind == "NY.GDP.TOTL.RT.ZS" and y not in RENT_YEARS:
                continue
            out.append((ind, c, r["country"]["value"], y, num(v)))
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["indicator", "countrycode", "country", "year", "value"])
    w.writerows(sorted(out, key=lambda t: (list(WDI.values()).index(t[0]), t[1], t[3])))
    return buf.getvalue()


def pwt(path: Path) -> str:
    """countrycode, country, year, rgdpe, rgdpna, pop of sheet Data, for the years kept."""
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    legend = {r[0]: r[1] for r in wb["Legend"].iter_rows(values_only=True) if r and r[0]}
    for var, words in definitions("oil_pwt").items():
        assert legend[var] == words, (var, legend.get(var))
    rows = wb["Data"].iter_rows(values_only=True)
    head = list(next(rows))
    out = []
    for r in rows:
        d = dict(zip(head, r))
        y = int(d["year"])
        if y in PWT_YEARS or (d["countrycode"] in G8 and y in G8_YEARS):
            out.append((d["countrycode"], d["country"], y, num(d["rgdpe"]), num(d["rgdpna"]), num(d["pop"])))
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["countrycode", "country", "year", "rgdpe", "rgdpna", "pop"])
    w.writerows(sorted(out, key=lambda t: (t[0], t[2])))
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
    built = {"oil_pinksheet": pinksheet(paths["pinksheet_47"]), "oil_wdi": wdi(paths),
             "oil_pwt": pwt(paths["pwt1001_xlsx"])}
    for name, text in built.items():
        out = SNAP / f"{name}.csv"
        if write:
            out.write_text(text, encoding="utf-8")
            print(f"wrote {out.relative_to(ROOT)} ({text.count(chr(10)) - 1} rows)")
        else:
            assert out.read_text(encoding="utf-8") == text, f"{name}.csv differs from the documents"
            print(f"ok {name}.csv matches the documents ({text.count(chr(10)) - 1} rows)")
    subprocess.run([sys.executable, str(HERE / "verify_web_quotes.py"), str(SNAP / "oil_facts.csv")]
                   + (["--offline"] if offline else []), check=True)
    subprocess.run([sys.executable, str(ROOT / "checks" / "check_ch47.py")], check=True)


if __name__ == "__main__":
    main("--offline" in sys.argv[1:], "--write" in sys.argv[1:])
