"""The sources of Chapter 46: download them into the web cache, compare their hashes, rebuild the series, check.

    python3 data/fetch/floating46.py              # download what is missing from WEB_CACHE, compare, then check
    python3 data/fetch/floating46.py --offline    # use the cache only
    python3 data/fetch/floating46.py --write      # also rewrite the series snapshot from the five BIS series

Two snapshots:
  floating_facts              the quotations of the chapter's sources with their page: Nixon's address of 15 August
                              1971 and remarks of 18 December 1971 (American Presidency Project); FRUS 1969-1976 vol.
                              III documents 164, 165, 168, 211, 221 and vol. XXXI documents 12, 14, 33, 35; the BIS
                              Annual Reports of 1972, 1973, 1974 and 1976; Dornbusch (1976) and Meese and Rogoff (1983)
                              (third-party copies, read to verify only); IFDP 184; the Bank of Japan's history, vol. 6;
                              the Economic Planning Agency's white paper of 1972; OJ C 38 of 18 April 1972; Rich (2003);
                              Powell (2005); the BIS Data Portal; the terms of the sites; the Library of Congress
  floating_bis_1959_1985      monthly averages, December 1959 to December 1985: the yen, the German series in euro
                              (the mark = euro x 1.95583), the Swiss franc and sterling per US dollar (WS_XRU), and the
                              consumer price indices of the United States, Japan, Germany, Switzerland and the United
                              Kingdom (WS_LONG_CPI, 2010 = 100), from the CSV of the BIS SDMX API

The .json of floating_facts lists every document with a URL and the SHA-256 of the copy read; the series lists its five
API queries under "documents" (they are also sources of floating_facts). This script fetches each into the cache with
verify_web_quotes.fetch (documents only; no program that comes with a download is run). A source of format "image"
names a PDF whose pages were read by eye on images rendered with pdftoppm; it is the same file as the PDF source, or a
scan without a text layer, and is not fetched here. A PDF whose hash differs stops the run. A web page, authority record
or API answer (DATED: they carry the day's scripts, record updates and data revisions) is reported and the run goes on:
its quotations are checked by data/fetch/verify_web_quotes.py, and the series is compared with the snapshot. Without
--write the series is rebuilt in memory and compared with the snapshot. checks/check_ch46.py runs last.
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
FETCH = "data/fetch/floating46.py"
DATED = ("html", "json", "txt")                       # formats whose copies change from day to day
SERIES = "floating_bis_1959_1985"
FIRST, LAST = "1959-12", "1985-12"
COLUMNS = {"jpy": "bisxrujp_46", "deu_eur": "bisxrude_46", "chf": "bisxruch_46", "gbp": "bisxrugb_46",
           "cpi_us": "biscpius_46", "cpi_jp": "biscpijp_46", "cpi_de": "biscpide_46", "cpi_ch": "biscpich_46",
           "cpi_gb": "biscpigb_46"}


def documents() -> dict[str, dict]:
    """Every document of the two snapshots: key -> url, format, sha256."""
    out: dict[str, dict] = {}
    for name, field in (("floating_facts", "sources"), (SERIES, "documents")):
        meta = json.loads((SNAP / f"{name}.json").read_text(encoding="utf-8"))
        assert meta["fetch"] == FETCH, name
        for key, src in meta[field].items():
            if key in out:
                assert (out[key]["url"], out[key]["sha256"]) == (src["url"], src["sha256"]), key
            out[key] = src
    return out


def months() -> list[str]:
    y, m = map(int, FIRST.split("-"))
    out = []
    while f"{y}-{m:02d}" <= LAST:
        out.append(f"{y}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def observations(path: Path) -> dict[str, str]:
    """TIME_PERIOD -> OBS_VALUE of one CSV answer of the BIS API (labels=both), as printed."""
    with path.open(encoding="utf-8") as fh:
        return {r["TIME_PERIOD"]: r["OBS_VALUE"] for r in csv.DictReader(fh) if r["OBS_VALUE"]}


def render(paths: dict[str, Path]) -> str:
    cols = {c: observations(paths[k]) for c, k in COLUMNS.items()}
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["month", *COLUMNS])
    for m in months():
        w.writerow([m, *(cols[c][m] for c in COLUMNS)])
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
    text = render(paths)
    out = SNAP / f"{SERIES}.csv"
    if write:
        out.write_text(text, encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)} ({len(months())} months)")
    else:
        assert out.read_text(encoding="utf-8") == text, f"{SERIES}.csv differs from the API answers"
        print(f"ok {SERIES}.csv matches the API answers ({len(months())} months)")
    subprocess.run([sys.executable, str(ROOT / "checks" / "check_ch46.py")], check=True)


if __name__ == "__main__":
    main("--offline" in sys.argv[1:], "--write" in sys.argv[1:])
