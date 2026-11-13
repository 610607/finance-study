"""The sources of Chapter 44: download them into the web cache, compare their hashes, rebuild the series, check.

    python3 data/fetch/naturalrate44.py              # download what is missing from WEB_CACHE, compare, then check
    python3 data/fetch/naturalrate44.py --offline    # use the cache only
    python3 data/fetch/naturalrate44.py --write      # also rewrite the two series snapshots from the documents

Three snapshots:
  naturalrate_facts            the quotations of the chapter's sources with their page: Friedman's presidential
                               address of 1967 (AER, March 1968) and his Nobel lecture of 1976; Phelps's Nobel lecture
                               of 2006; Modigliani and Papademos (BPEA 1975:1) with its erratum slip; Gordon and King
                               (BPEA 1982:1); tables B-40 and B-62 of the Economic Report of the President of 2000; the
                               Economic Planning Agency's annual economic report of 1974 (the Cabinet Office's online
                               edition); the e-Stat listings and terms, the Cabinet Office's terms and the Public Data
                               License 1.0; the terms of the AEA and of Brookings; the Nobel pages; the authority records
                               of the Library of Congress and the GND (lobid.org)
  naturalrate_us_1959_1985     the civilian unemployment rate (B-40, all civilian workers) and the change of the CPI-U
                               (B-62, December to December and year to year), read from the -layout text of the two
                               one-page PDFs
  naturalrate_japan_1953_1986  the unemployment rate of the Labour Force Survey (e-Stat, long-term table 2, sheet 長期02,
                               with and without Okinawa in 1973) and the change over the year of the 2015-base CPI, all
                               items less imputed rent (1948-) and all items (1971-) (e-Stat CSV files, Shift_JIS)

The .json of naturalrate_facts lists every document with a URL and the SHA-256 of the copy read; the series list theirs
under "documents". This script fetches each into the cache with verify_web_quotes.fetch (documents only; no program that
comes with a download is run). A PDF, workbook or CSV whose hash differs stops it. A web page or authority record
(DATED: they carry the day's scripts, dates and record updates) is reported and the run goes on: its quotations are
checked by data/fetch/verify_web_quotes.py. Without --write the two series are rebuilt in memory and compared with the
snapshots. checks/check_ch44.py runs last.
"""
from __future__ import annotations

import csv
import io
import json
import re
import subprocess
import sys
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verify_web_quotes import fetch  # noqa: E402

ROOT = HERE.parents[1]
SNAP = ROOT / "data" / "snapshots"
FETCH = "data/fetch/naturalrate44.py"
DATED = ("html", "json")                              # formats whose copies change from day to day
US, JP = "naturalrate_us_1959_1985", "naturalrate_japan_1953_1986"
US_YEARS, JP_YEARS = range(1959, 1986), range(1953, 1987)
LT02_SHEET, LT02_NOTES = "長期02", "※注_Notes"
OKINAWA = ("「年次」欄に「*」を付してある結果数値には、沖縄県分は含まれていない。"
           "沖縄の本土復帰により、1972年７月以降、沖縄県も調査の範囲に含まれた。")


def documents() -> dict[str, dict]:
    """Every document of the three snapshots: key -> url, format, sha256."""
    out: dict[str, dict] = {}
    for name, field in (("naturalrate_facts", "sources"), (US, "documents"), (JP, "documents")):
        meta = json.loads((SNAP / f"{name}.json").read_text(encoding="utf-8"))
        assert meta["fetch"] == FETCH, name
        for key, src in meta[field].items():
            if key in out:
                assert (out[key]["url"], out[key]["sha256"]) == (src["url"], src["sha256"]), key
            out[key] = src
    return out


def number(s: str) -> float:
    """A figure of the ERP tables: '.7' -> 0.7, '−.5' -> -0.5."""
    return float(s.replace("−", "-"))


def erp_rows(path: Path) -> dict[int, list[float]]:
    """The yearly rows of a one-page ERP table, from pdftotext -layout: year -> the figures of the row."""
    text = subprocess.run(["pdftotext", "-enc", "UTF-8", "-layout", str(path), "-"], capture_output=True, text=True,
                          check=True).stdout
    out: dict[int, list[float]] = {}
    for line in text.splitlines():
        m = re.match(r"\s*(\d{4}) \.{5,}\s+(.*)$", line)
        if m:
            year = int(m.group(1))
            assert year not in out, (path.name, year)
            out[year] = [number(t) for t in m.group(2).split() if not t.startswith(".....")]
    return out


def us_series(paths: dict[str, Path]) -> list[list]:
    b40, b62 = erp_rows(paths["erpb40_44"]), erp_rows(paths["erpb62_44"])
    return [[y, b40[y][0], b62[y][0], b62[y][1]] for y in US_YEARS]


def lt02(path: Path) -> tuple[dict[int, float], dict[int, float], str]:
    """Sheet 長期02, column 12 (完全失業率): the rows with Okinawa (from 1973) and without (to 1973), and note 1."""
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[LT02_SHEET]
    rows = list(ws.iter_rows(min_row=1, max_row=60))
    head = [str(c.value) for c in rows[5]] + [str(c.value) for c in rows[8]]
    assert rows[5][12].value.startswith("完全失業率") and "Unemployment rate" in rows[8][12].value, head
    with_ok, without = {}, {}
    for r in rows[10:]:
        y = r[1].value
        if not isinstance(y, (int, float)) or not JP_YEARS.start <= y < JP_YEARS.stop:
            continue
        star = r[1].number_format.endswith('"*"')         # 「年次」欄に「*」: without Okinawa
        target = without if star else with_ok
        assert int(y) not in target, y
        target[int(y)] = float(r[12].value)
    note = str(list(wb[LT02_NOTES].iter_rows(min_row=3, max_row=3, values_only=True))[0][1])
    assert note.startswith(OKINAWA), note[:80]
    assert set(without) == set(range(1953, 1974)) and set(with_ok) == set(range(1973, 1987))
    return with_ok, without, OKINAWA


def cpi_csv(path: Path, column: str) -> dict[int, float]:
    """An e-Stat CPI file (Shift_JIS): the column headed `column` on its first line, year -> value."""
    rows = list(csv.reader(io.StringIO(path.read_bytes().decode("cp932"))))
    k = [c.strip() for c in rows[0]].index(column)
    out = {}
    for r in rows:
        y = r[0].strip()
        if y.isdigit() and len(r) > k and r[k].strip():
            out[int(y)] = float(r[k])
    return out


def jp_series(paths: dict[str, Path]) -> list[list]:
    with_ok, without, _ = lt02(paths["estatlt02_44"])
    xr = cpi_csv(paths["estatcpixr44"], "持家の帰属家賃を除く総合")
    allitems = cpi_csv(paths["estatcpizny44"], "総合")
    xr2 = cpi_csv(paths["estatcpizny44"], "持家の帰属家賃を除く総合")
    for y in range(1971, JP_YEARS.stop):                  # the two files agree where both print the series
        assert xr[y] == xr2[y], y
    out = []
    for y in JP_YEARS:
        u = with_ok.get(y, without.get(y))
        out.append([y, u, without.get(y, ""), xr[y], allitems.get(y, "")])
    return out


HEADERS = {US: ["year", "unemp_pct", "cpi_dec_dec_pct", "cpi_year_pct"],
           JP: ["year", "unemp_pct", "unemp_excl_okinawa_pct", "cpi_less_rent_pct", "cpi_all_pct"]}


def render(name: str, rows: list[list]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(HEADERS[name])
    w.writerows(rows)
    return buf.getvalue()


def main(offline: bool, write: bool) -> None:
    paths: dict[str, Path] = {}
    for key, src in sorted(documents().items()):
        path, note = fetch(key, src, offline)
        if path is None:
            raise SystemExit(f"{key}: {note}")
        if note and src["format"] not in DATED:
            raise SystemExit(f"{key}: {note}")
        print(f"{'NOTE' if note else 'ok'} {key} {src['sha256'][:16]}{' ' + note if note else ''}")
        paths[key] = path
    for name, rows in ((US, us_series(paths)), (JP, jp_series(paths))):
        text = render(name, rows)
        out = SNAP / f"{name}.csv"
        if write:
            out.write_text(text, encoding="utf-8")
            print(f"wrote {out.relative_to(ROOT)} ({len(rows)} years)")
        else:
            assert out.read_text(encoding="utf-8") == text, f"{name}.csv differs from the documents"
            print(f"ok {name}.csv matches the documents ({len(rows)} years)")
    subprocess.run([sys.executable, str(ROOT / "checks" / "check_ch44.py")], check=True)


if __name__ == "__main__":
    main("--offline" in sys.argv[1:], "--write" in sys.argv[1:])
