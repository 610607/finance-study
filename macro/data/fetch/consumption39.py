"""The sources of Chapter 39: download them into the web cache, compare their hashes, rebuild the data snapshot, check.

    python3 data/fetch/consumption39.py              # download what is missing from WEB_CACHE, then check
    python3 data/fetch/consumption39.py --offline    # use the cache only
    python3 data/fetch/consumption39.py --write      # also (re)write data/snapshots/esri_household_saving_1955_2024.csv

Two snapshots. consumption_facts holds the quotations of the chapter's sources with their page: Ford's address of 29
March 1975 (The American Presidency Project) and Public Law 94-12 (the Statutes at Large on govinfo.gov); the Economic
Report of the President of January 1962; Friedman's A Theory of the Consumption Function (1957) and Kuznets's Uses of
National Income in Peace and War (1942), the NBER's PDFs; the Nobel lectures of Modigliani (1985) and Tobin (1981);
Hall (1978) and Hall and Jorgenson (1967), the scans on Hall's page at Stanford University, and Modigliani and Steindel
(1977), the PDF on brookings.edu, read on the page images; Blinder (1981), the NBER's reprint; the NBER working papers
of Johnson, Parker and Souleles (2004), Parker, Souleles, Johnson and McClelland (2011), Fazzari, Hubbard and Petersen
(1987), Kaplan and Zingales (2000) and Horioka (2024, with Table S-1 read on the page images); Hayashi (1986); ESRI's
pages of the national accounts of 1998 and 2024 and the terms of use of ESRI, the Cabinet Office and the Digital
Agency; the authority records of the Library of Congress and the Deutsche Nationalbibliothek (lobid.org). Its .json
lists every document with a URL and the SHA-256 of the copy read; this script fetches each one into the cache with
verify_web_quotes.fetch (documents only; no program that comes with a download is run) and stops if a hash differs.
The quotations themselves are checked by data/fetch/verify_web_quotes.py, the numbers read from them by
checks/check_ch39.py.

esri_household_saving_1955_2024 holds the yearly series of the chapter's case and figure of Japan, read from four
workbooks of the Economic and Social Research Institute (内閣府経済社会総合研究所), whose addresses and hashes the
snapshot's notes record (DOCS below): the household saving rate (家計（個人企業を含む）, 貯蓄率) of the 1998 accounts
(68SNA, 1990 base; table 55i5.xls, sheet 暦年, 1955-1998) and of the 2024 accounts (2008SNA, 2020 base; table
2024i5_jp.xlsx, sheet 暦年（４）a, （参考）貯蓄率, 1994-2024), and the growth rate of real gross domestic expenditure
(table 55fcm1r.xls, sheet 増加率, 国内総支出, 1956-1998; 2024fcm1rn_jp.xlsx, sheet 増加率, 国内総生産（支出側）, chained
2020 prices, 1995-2024). The rows and the years are found by their labels; the figures are written as printed (one
decimal). This script compares what it reads with the snapshot (or writes it with --write), then runs
checks/check_ch39.py.
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
DATA = SNAP / "esri_household_saving_1955_2024.csv"
TABLES = "https://www.esri.cao.go.jp/jp/sna/data/data_list/kakuhou/files/"
# the workbooks of the data snapshot (their addresses and hashes are also in the snapshot's notes)
DOCS = {
    "esri68_i5": {"url": TABLES + "h10/tables/55i5.xls", "format": "xls",
                  "sha256": "6f6b99d2cf939d0220901d8785fca4e9af8db570f12a1caebf916abe31bf5647"},
    "esri68_fcm1r": {"url": TABLES + "h10/tables/55fcm1r.xls", "format": "xls",
                     "sha256": "70a1a880c7c15d64b1a2d1ff1d94c42818c60d2a34a06cfd5d45e9e6a1c0eee6"},
    "esri2024_i5": {"url": TABLES + "2024/tables/2024i5_jp.xlsx", "format": "xlsx",
                    "sha256": "5c72b85469dbe9b8320f76c99409cebc8bc5a45932aec9ee33c11cf54115164a"},
    "esri2024_fcm1rn": {"url": TABLES + "2024/tables/2024fcm1rn_jp.xlsx", "format": "xlsx",
                        "sha256": "dd90bf943a2067756652f2c22c4912fbd89424431c6ab47aa898820832b7d2c7"},
}
COLUMNS = ["year", "saving_68sna_pct", "saving_08sna_pct", "growth_68sna_pct", "growth_08sna_pct"]
YEARS = range(1955, 2025)


def sources() -> dict[str, dict]:
    meta = json.loads((SNAP / "consumption_facts.json").read_text(encoding="utf-8"))
    assert meta["fetch"] == "data/fetch/consumption39.py"
    data = json.loads(DATA.with_suffix(".json").read_text(encoding="utf-8"))
    assert data["fetch"] == "data/fetch/consumption39.py"
    for key, doc in DOCS.items():
        assert f"{key} {doc['url']} (SHA-256 {doc['sha256']})" in data["notes"], key
    return meta["sources"]


def grid_xls(path: Path, sheet: str) -> list[list]:
    import xlrd
    s = xlrd.open_workbook(str(path)).sheet_by_name(sheet)
    return [s.row_values(r) for r in range(s.nrows)]


def grid_xlsx(path: Path, sheet: str) -> list[list]:
    import openpyxl
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True)[sheet]
    return [["" if v is None else v for v in row] for row in ws.iter_rows(values_only=True)]


def row_of(grid: list[list], label: str, years_from: int) -> dict[int, float]:
    """year -> the figure of the row whose first cell is `label` (spaces of either width ignored); the years are
    the row of the grid that begins with `years_from` in its second cell."""
    def bare(s):
        return str(s).replace("　", "").replace(" ", "")
    head = [r for r in grid if len(r) > 1 and r[1] == years_from]
    assert len(head) == 1, (label, years_from)
    rows = [r for r in grid if bare(r[0]) == bare(label)]
    assert len(rows) == 1, label
    out = {}
    for y, v in zip(head[0][1:], rows[0][1:]):
        if y == "" or v in ("", "-"):
            continue
        assert abs(v * 10 - round(v * 10)) < 1e-6, (label, y, v)         # one decimal, as printed
        out[int(y)] = round(float(v), 1)
    return out


def series(cache: dict[str, Path]) -> list[dict[str, str]]:
    s68 = row_of(grid_xls(cache["esri68_i5"], "暦年"), "貯蓄率（％）", 1955)
    s08 = row_of(grid_xlsx(cache["esri2024_i5"], "暦年（４）a"), "（参考）貯蓄率", 1994)
    g68 = row_of(grid_xls(cache["esri68_fcm1r"], "増加率"), "5. 国内総支出", 1955)
    g08 = row_of(grid_xlsx(cache["esri2024_fcm1rn"], "増加率"), "５．国内総生産（支出側）", 1995)
    assert sorted(s68) == list(range(1955, 1999)) and sorted(s08) == list(range(1994, 2025))
    assert sorted(g68) == list(range(1956, 1999)) and sorted(g08) == list(range(1995, 2025))

    def cell(d, y):
        return f"{d[y]:.1f}" if y in d else ""
    return [dict(zip(COLUMNS, [str(y), cell(s68, y), cell(s08, y), cell(g68, y), cell(g08, y)])) for y in YEARS]


def main(offline: bool, write: bool) -> None:
    cache = {}
    for key, src in sorted({**sources(), **DOCS}.items()):
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
        assert list(csv.DictReader(fh)) == rows, f"{DATA.name} differs from the workbooks"
    print(f"ok {DATA.name}: {len(rows)} years read again from the workbooks")
    subprocess.run([sys.executable, str(ROOT / "checks" / "check_ch39.py")], check=True)


if __name__ == "__main__":
    main("--offline" in sys.argv[1:], "--write" in sys.argv[1:])
