"""The sources of Chapter 30's quotation snapshot: download them into the web cache, compare their hashes, run the check.

    python3 data/fetch/alternatives30.py              # download what is missing from WEB_CACHE, then check
    python3 data/fetch/alternatives30.py --offline    # use the cache only

The snapshot is alternatives_facts (quotations with their page or document): Shizume (2009, Bank of Japan Review) and
Ide (2003, IMES Discussion Paper) on Takahashi's finance; the Bank of Japan's chronology and terms of use; the portraits
and chronology of the National Diet Library; the judgment of the International Military Tribunal (1947) and Nazi
Conspiracy and Aggression, vols. II and VII (1946: the prosecution's chapter on Schacht, Puhl's deposition EC-436 and
the Reichsbank directors' memorandum EC-369); the BIS annual report of 1937 and the BIS terms; the National Industrial
Recovery Act, the Agricultural Adjustment Act, the National Labor Relations Act and the Emergency Relief Appropriation
Act (Statutes at Large); Berg and Jonung (1998), Eichengreen and Sachs (1984), Bernanke and James (1991) and the Neue
Deutsche Biographie on Schacht (the last four shared with earlier chapters' snapshots); the Riksbank's history pages;
and the authority records of the Library of Congress. Its .json lists every document with a URL and the SHA-256 of the
copy read; this script fetches each one into the cache with verify_web_quotes.fetch (documents only; no program that
comes with a download is run), stops if a hash differs, and then runs checks/check_ch30.py. The sources of format
"image" name a file whose pages were read by eye on images rendered with pdftoppm (the Bank of Japan's history of
1984 and Historical Statistics of the United States, chapter Y); they are not fetched here (their notes give the
pages). The quotations themselves are checked by data/fetch/verify_web_quotes.py.

The table snapshots alternatives_reichsbank, alternatives_yen_monthly and alternatives_fx_annual (Banking and Monetary
Statistics 1914-1941, Tables 167 and 173) and alternatives_boj_sales (the Bank of Japan's Table 1-17) were read on
page images: their notes name each file with its URL and SHA-256. Sweden's price index and the Riksbank's discount
rate come from data/fetch/riksbank_sweden30.py, GDP per head from data/fetch/maddison2023_interwar29.py.
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
SNAPSHOTS = ["alternatives_facts"]


def sources() -> dict[str, dict]:
    """Every source named by the snapshots (a key names the same document in each of them)."""
    out: dict[str, dict] = {}
    for name in SNAPSHOTS:
        meta = json.loads((ROOT / "data" / "snapshots" / f"{name}.json").read_text(encoding="utf-8"))
        assert meta["fetch"] == "data/fetch/alternatives30.py", name
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
    subprocess.run([sys.executable, str(ROOT / "checks" / "check_ch30.py")], check=True)


if __name__ == "__main__":
    main("--offline" in sys.argv[1:])
