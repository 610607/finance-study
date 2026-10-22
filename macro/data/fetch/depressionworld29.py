"""The sources of Chapter 29's quotation snapshot: download them into the web cache, compare their hashes, run the check.

    python3 data/fetch/depressionworld29.py              # download what is missing from WEB_CACHE, then check
    python3 data/fetch/depressionworld29.py --offline    # use the cache only

The snapshot is depressionworld_facts (quotations with their page or document: Hansard of 21 September 1931 for both
Houses, the Gold Standard (Amendment) Act 1931, Keynes's essay of 27 September 1931, Hoover's statement of the
moratorium from the American Presidency Project, six issues of the Federal Reserve Bulletin (July to October 1931,
December 1935, October 1936), the Silver Purchase Act of 1934, Foreign Relations of the United States 1934 and 1935,
Bernanke and James 1991, Bernanke 1994 (NBER Working Paper 4814), Eichengreen and Sachs 1984 (NBER Working Paper 1498),
Brandt and Sargent 1989, the abstract of Friedman 1992, Diaz Alejandro 1983, the history pages of the Banco Central de
la Republica Argentina, Wolf 2007, and the authority records of the BnF and the Library of Congress). Its .json lists
every document with a URL and the SHA-256 of the copy read; this script fetches each one into the cache with
verify_web_quotes.fetch (documents only; no program that comes with a download is run), stops if a hash differs, and
then runs checks/check_ch29.py. The sources of format "image" name a PDF whose pages were read by eye on images rendered
with pdftoppm; they are not fetched here (their notes give the pages). The quotations themselves are checked by
data/fetch/verify_web_quotes.py.

The table snapshots depressionworld_goldexits, depressionworld_es, depressionworld_silver, depressionworld_yuan_monthly
and depressionworld_china were read on page images: their notes name each file with its URL and SHA-256. The British
monthly series and Bank Rate come from data/fetch/boe_millennium_gb29.py, GDP per head from
data/fetch/maddison2023_interwar29.py.
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
SNAPSHOTS = ["depressionworld_facts"]


def sources() -> dict[str, dict]:
    """Every source named by the snapshots (a key names the same document in each of them)."""
    out: dict[str, dict] = {}
    for name in SNAPSHOTS:
        meta = json.loads((ROOT / "data" / "snapshots" / f"{name}.json").read_text(encoding="utf-8"))
        assert meta["fetch"] == "data/fetch/depressionworld29.py", name
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
        if path is None or note:
            raise SystemExit(f"{key}: {note}")
        print(f"ok {key} {src['sha256'][:16]}")
    subprocess.run([sys.executable, str(ROOT / "checks" / "check_ch29.py")], check=True)


if __name__ == "__main__":
    main("--offline" in sys.argv[1:])
