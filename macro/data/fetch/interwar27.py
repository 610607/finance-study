"""The sources of Chapter 27's quotation snapshot: download them into the web cache, compare their hashes, run the check.

    python3 data/fetch/interwar27.py              # download what is missing from WEB_CACHE, then check
    python3 data/fetch/interwar27.py --offline    # use the cache only

The snapshot is interwar_facts (quotations with their page or column: Hansard for 28 April and 11 May 1925, the Gold
Standard Act 1925, Keynes 1923 and 1925, the Macmillan Committee's Minutes of Evidence, Brown 1940, Nurkse 1944,
Dulles 1929, De Long and Shleifer 1990, McGrattan and Prescott 2003, Federal Reserve History, the Riksbank and
Wikisource). Its .json lists every document with a URL and the SHA-256 of the copy read; this script fetches each one
into the cache with verify_web_quotes.fetch (documents only; no program that comes with a download is run), stops if a
hash differs, and then runs checks/check_ch27.py. The quotations themselves are checked by
data/fetch/verify_web_quotes.py. The chapter's monthly British series and Bank Rate come from the Bank of England's
workbook through data/fetch/boe_millennium_gb27.py.
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
SNAPSHOTS = ["interwar_facts"]


def sources() -> dict[str, dict]:
    """Every source named by the snapshots (a key names the same document in each of them)."""
    out: dict[str, dict] = {}
    for name in SNAPSHOTS:
        meta = json.loads((ROOT / "data" / "snapshots" / f"{name}.json").read_text(encoding="utf-8"))
        assert meta["fetch"] == "data/fetch/interwar27.py", name
        for key, src in meta["sources"].items():
            if key in out and out[key]["sha256"] != src["sha256"]:
                raise SystemExit(f"{key}: two hashes in the snapshots ({name})")
            out[key] = src
    return out


def main(offline: bool) -> None:
    for key, src in sorted(sources().items()):
        path, note = fetch(key, src, offline)
        if path is None or note:
            raise SystemExit(f"{key}: {note}")
        print(f"ok {key} {src['sha256'][:16]}")
    subprocess.run([sys.executable, str(ROOT / "checks" / "check_ch27.py")], check=True)


if __name__ == "__main__":
    main("--offline" in sys.argv[1:])
