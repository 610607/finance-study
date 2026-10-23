"""The sources of Chapter 31's quotation snapshot: download them into the web cache, compare their hashes, run the check.

    python3 data/fetch/soviet31.py              # download what is missing from WEB_CACHE, then check
    python3 data/fetch/soviet31.py --offline    # use the cache only

The snapshot is soviet_facts (quotations with their page or section): Stalin's report of 7 January 1933 on the first
five-year plan (Works, vol. 13, on the Marxists Internet Archive); the State Planning Commission's plan in its English
edition of 1929 (The Soviet Union Looks Ahead) and its report on the plan's fulfilment (Moscow, 1933), both in the OCR
text of archive.org; the Soviet Union Information Bureau's handbook of 1929 (chapter on money and banking); Mises
(1920, in Hayek's collection of 1935), Lange (1938) and Hayek (1945); Markevich, Naumenko and Qian (NBER Working Paper
29089), Rudnytskyi et al. (2015), Cameron (2016) and Werth (2016) on the famine; Davies's review (2004) of Allen's
Farm to Factory; Cheremukhin, Golosov, Guriev and Tsyvinski (NBER Working Paper 19425); Gregory and Harrison (2005),
Harrison (1980, 2017), Markevich and Harrison (2011) and Harrison and Markevich (2018) from Mark Harrison's Warwick
pages; the Nobel press releases of 1973 and 1975; and the authority records of the Library of Congress. Its .json
lists every document with a URL and the SHA-256 of the copy read; this script fetches each one into the cache with
verify_web_quotes.fetch (documents only; no program that comes with a download is run), stops if a hash differs, and
then runs checks/check_ch31.py. The sources of format "image" name a file whose pages were read by eye on images
rendered with pdftoppm (the tables of the Gosplan report of 1933, the budget table of Socialist Construction in the
U.S.S.R., 1936, Table A.2 of Markevich, Naumenko and Qian, and Harrison's article of 1993 on Khanin, a scan without a
text layer); they are not fetched here (their notes give the pages). The quotations themselves are checked by
data/fetch/verify_web_quotes.py.

The table snapshot soviet_grain (Markevich, Naumenko and Qian, Appendix Table A.2, panel II: the grain harvest and
procurement of the USSR, 1927-1939) was read on the image of PDF page 51 of the same working paper: its .json names the
file with its URL and SHA-256. GDP per head of the USSR and six other economies, 1913-1940, comes from
data/fetch/maddison2023_ussr31.py (Maddison Project Database 2023).
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
SNAPSHOTS = ["soviet_facts"]


def sources() -> dict[str, dict]:
    """Every source named by the snapshots (a key names the same document in each of them)."""
    out: dict[str, dict] = {}
    for name in SNAPSHOTS:
        meta = json.loads((ROOT / "data" / "snapshots" / f"{name}.json").read_text(encoding="utf-8"))
        assert meta["fetch"] == "data/fetch/soviet31.py", name
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
    subprocess.run([sys.executable, str(ROOT / "checks" / "check_ch31.py")], check=True)


if __name__ == "__main__":
    main("--offline" in sys.argv[1:])
