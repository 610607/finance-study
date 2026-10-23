"""The sources of Chapter 33's quotation snapshot: download them into the web cache, compare their hashes, run the check.

    python3 data/fetch/islm33.py              # download what is missing from WEB_CACHE, then check
    python3 data/fetch/islm33.py --offline    # use the cache only

The snapshot is islm_facts (quotations with their page): Econometrica vol. 5 (1937) in the OCR text of the Internet
Archive's scan (the report of the Oxford meeting of the Econometric Society, September 1936, the list of those who
attended, and Hicks, 'Mr. Keynes and the "Classics"'); Keynes's General Theory (1936), already used by Chapter 32; the
Federal Reserve Bulletin of August 1936, January and February 1937, March and May 1938 (OCR texts on archive.org);
the text layer of Banking and Monetary Statistics 1914-1941 (FRASER) for the titles and headnotes of Tables 105, 107,
122 and 128; Velde (2009, Chicago Fed); Romer's NBER Working Paper 3829; Roosevelt's press conference of 2 April 1937
and message of 14 April 1938 (The American Presidency Project); Eggertsson and Pugsley (2006, the Bank of Japan's
Institute for Monetary and Economic Studies); the Bank of Japan's statements of 1999 and 2001; Hansen (American
Economic Review, March 1939) and Pigou (Economic Journal, December 1943) in the OCR texts on archive.org; Modigliani's
Nobel biography and the Econometric Society's page of his article of 1944; the U.S. Treasury's page on Morgenthau;
the authority records of the Library of Congress and the Bibliotheque nationale de France; the terms of the sites of
the Federal Reserve Board, the Federal Reserve Bank of Chicago and the Bank of Japan. Its .json lists every document
with a URL and the SHA-256 of the copy read; this script fetches each one into the cache with verify_web_quotes.fetch
(documents only; no program that comes with a download is run), stops if a hash differs (except the Nobel page, which
prints the day it is served), and then runs checks/check_ch33.py. The sources of format "image" name a scan whose
pages were read by eye on images rendered with pdftoppm (Hicks's equations, Hansen's pp. 2, 4 and 14, the table of
federal finances in Historical Statistics); they are not fetched here. The quotations themselves are checked by
data/fetch/verify_web_quotes.py.

The figures of Banking and Monetary Statistics (member bank reserves, reserve requirements, bill and bond yields) were
read on page images of the same FRASER scan and are kept in the snapshots bms_member_reserves_1935_1939,
bms_reserve_requirements_1917_1941 and bms_rates_1936_1940 (their .json say how). Industrial production comes from
data/fetch/frb_g17_ip33.py (the Board's G.17 file ip_sa.txt).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verify_web_quotes import fetch

ROOT = HERE.parents[1]
SNAPSHOTS = ["islm_facts"]
DAILY = {"nobel1985"}                     # the page prints the day it is served


def sources() -> dict[str, dict]:
    """Every source named by the snapshots (a key names the same document in each of them)."""
    out: dict[str, dict] = {}
    for name in SNAPSHOTS:
        meta = json.loads((ROOT / "data" / "snapshots" / f"{name}.json").read_text(encoding="utf-8"))
        assert meta["fetch"] == "data/fetch/islm33.py", name
        for key, src in meta["sources"].items():
            if key in out and out[key]["sha256"] != src["sha256"]:
                raise SystemExit(f"{key}: two hashes in the snapshots ({name})")
            out[key] = src
    return out


def main(offline: bool) -> None:
    for key, src in sorted(sources().items()):
        if src["format"] == "image":
            print(f"-- {key}: read on page images ({src['url']}), not fetched")
            continue
        path, note = fetch(key, src, offline)
        if path is None or (note and key not in DAILY):
            raise SystemExit(f"{key}: {note}")
        print(f"ok {key} {src['sha256'][:16]}" + (f" ({note})" if note else ""))
    subprocess.run([sys.executable, str(ROOT / "checks" / "check_ch33.py")], check=True)


if __name__ == "__main__":
    main("--offline" in sys.argv[1:])
