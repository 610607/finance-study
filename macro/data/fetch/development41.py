"""The sources of Chapter 41: download them into the web cache, compare their hashes, check the quotations and the chapter.

    python3 data/fetch/development41.py              # download what is missing from WEB_CACHE, then check
    python3 data/fetch/development41.py --offline    # use the cache only

The snapshot development_facts holds the quotations of the chapter's sources with their page: Lewis (1954), the scan of
The Manchester School 22 on archive.org (read to verify, not committed); Lewis's autobiography and Nobel lecture,
Schultz's Nobel lecture and the facts of the prize of 1979 (nobelprize.org); Prebisch (1950), the United Nations
document E/CN.12/89/Rev.1 in a scan on archive.org; the World Development Report 1987, Easterly (1997, Policy Research
Working Paper 1807) and the reports PA-43a (1970) and AF-57a (1967) on Ghana, the PDFs of documents.worldbank.org;
Murphy, Shleifer and Vishny (1988), the NBER's PDF of Working Paper 2708; the Indian Planning Commission's draft outline
of the Second Plan (1956), its reappraisal (1958) and the Third Plan (1961) and the Ghanaian outline of the Seven-Year
Plan (1963), the text layers of the microfilm scans on archive.org and one page image; the terms of use and the
copyright page of the United Nations; section 52(1)(q) of the Indian Copyright Act, 1957 (Indian Kanoon) and the
Ghanaian Copyright Act, 2005 (ARIPO's PDF); the authority records of the Library of Congress and the Deutsche
Nationalbibliothek (lobid.org). Its .json lists every document with a URL and the SHA-256 of the copy read; this script
fetches each one into the cache with verify_web_quotes.fetch (documents only; no program that comes with a download is
run) and stops if a hash differs. The pages of nobelprize.org print the day they are served, so a fresh download of
them differs from the recorded copy: the script then names the source and stops, and the quotations can still be
checked in the fresh copy with data/fetch/verify_web_quotes.py. The quotations are checked by
data/fetch/verify_web_quotes.py, the numbers read from them by checks/check_ch41.py, which this script runs last.

The GDP per head of the chapter's table and figure is the snapshot maddison2023_development, written by
data/fetch/maddison2023_development41.py from the workbook of the Maddison Project Database 2023.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verify_web_quotes import fetch  # noqa: E402

ROOT = HERE.parents[1]
SNAP = ROOT / "data" / "snapshots" / "development_facts"
FETCH = "data/fetch/development41.py"


def sources() -> dict[str, dict]:
    meta = json.loads(SNAP.with_suffix(".json").read_text(encoding="utf-8"))
    assert meta["fetch"] == FETCH
    return meta["sources"]


def main(offline: bool) -> None:
    for key, src in sorted(sources().items()):
        path, note = fetch(key, src, offline)
        if path is None or note:
            raise SystemExit(f"{key}: {note}")
        print(f"ok {key} {src['sha256'][:16]}")
    subprocess.run([sys.executable, str(HERE / "verify_web_quotes.py"), str(SNAP.with_suffix(".csv"))]
                   + (["--offline"] if offline else []), check=True)
    subprocess.run([sys.executable, str(ROOT / "checks" / "check_ch41.py")], check=True)


if __name__ == "__main__":
    main("--offline" in sys.argv[1:])
