"""The sources of Chapter 28's quotation snapshot: download them into the web cache, compare their hashes, run the check.

    python3 data/fetch/depressionus28.py              # download what is missing from WEB_CACHE, then check
    python3 data/fetch/depressionus28.py --offline    # use the cache only

The snapshot is depressionus_facts (quotations with their page or document: Roosevelt's fireside chat of 12 March 1933,
the proclamations, the executive order and the White House statement from the American Presidency Project, four acts in
the Statutes at Large, the Federal Reserve Bulletin of February 1933, February 1937 and September 1937, Fisher 1933,
Bernanke 1983, Romer 1990 and 1992, Bordo, Redish and Rockoff 2011, Bernanke's remarks of 8 November 2002, Federal
Reserve History, the Canada Year Book 1934-35, and the authority records of the BnF and the Library of Congress). Its
.json lists every document with a URL and the SHA-256 of the copy read; this script fetches each one into the cache with
verify_web_quotes.fetch (documents only; no program that comes with a download is run), stops if a hash differs, and
then runs checks/check_ch28.py. The two sources of format "image" name a PDF whose pages were read by eye on images
rendered with pdftoppm; they are not fetched here (their notes give the pages). The quotations themselves are checked
by data/fetch/verify_web_quotes.py.

The annual snapshot depressionus_annual (Historical Statistics of the United States, 1975, and the Bulletin's tables)
was also read on page images: its notes name each file with its URL and SHA-256. Real GDP and the GDP deflator are
Chapter 2's bea_nipa_annual (data/fetch/bea_nipa_annual.py).
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
SNAPSHOTS = ["depressionus_facts"]


def sources() -> dict[str, dict]:
    """Every source named by the snapshots (a key names the same document in each of them)."""
    out: dict[str, dict] = {}
    for name in SNAPSHOTS:
        meta = json.loads((ROOT / "data" / "snapshots" / f"{name}.json").read_text(encoding="utf-8"))
        assert meta["fetch"] == "data/fetch/depressionus28.py", name
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
    subprocess.run([sys.executable, str(ROOT / "checks" / "check_ch28.py")], check=True)


if __name__ == "__main__":
    main("--offline" in sys.argv[1:])
