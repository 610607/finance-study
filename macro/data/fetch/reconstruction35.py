"""The sources of Chapter 35's quotation snapshot: download them into the web cache, compare their hashes, run the check.

    python3 data/fetch/reconstruction35.py              # download what is missing from WEB_CACHE, then check
    python3 data/fetch/reconstruction35.py --offline    # use the cache only

The snapshot is reconstruction_facts (quotations with their page): Buchheim (1988), Ritschl (1985) and Abelshauser
(1981) from the Institut fuer Zeitgeschichte's archive of the Vierteljahrshefte fuer Zeitgeschichte; the Military
Government laws of 1948 (the Waehrungsgesetz, Umstellungsgesetz and Festkontogesetz and the law establishing the
Bank deutscher Laender) as printed by verfassungen.de; the Monatsberichte der Bank deutscher Laender of February
1950 and the terms of use of the Deutsche Bundesbank's site; De Long and Eichengreen, NBER Working Paper 3899;
Marshall's remarks at Harvard in the Department of State Bulletin (the OCR text on archive.org); the Economic
Cooperation Act of 1948 (62 Stat. 137, govinfo.gov); Foreign Relations of the United States (the Office of the
Historian); the Ministry of Finance's Fiscal and Monetary Policies of Japan 1945-1971, Part 1, Chapters 1 and 2, and
its terms of use; the Bank of Japan's chronology and copyright page; the excerpt of the Soviet decision of 14
December 1947 in Vestnik Universiteta imeni O. E. Kutafina; House of Commons Hansard of 15 April 1959, 18 January
1972 and 9 March 1972 (UK Parliament's historic Hansard site); Wang Yunwu's statement of 19 August 1948 on Chinese
Wikisource; the authority records of the Library of Congress and of the Deutsche Nationalbibliothek (lobid.org).
Its .json lists every document with a URL and the SHA-256 of the copy read; this script fetches each one into the
cache with verify_web_quotes.fetch (documents only; no program that comes with a download is run), stops if a hash
differs, and then runs checks/check_ch35.py. The sources of format "image" name a scan whose pages were read by eye
on images rendered with pdftoppm (Ritschl's Tab. I; p. 57 of the Monatsberichte; four sections of the Centennial
History of the Bank of Japan, vol. 5; p. 1 of Zaria Vostoka no. 247); they are not fetched here. The quotations
themselves are checked by data/fetch/verify_web_quotes.py.

Japan's prewar-base wholesale price index (1944-1952) comes from data/fetch/boj_wpi35.py.
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
SNAPSHOTS = ["reconstruction_facts"]


def sources() -> dict[str, dict]:
    """Every source named by the snapshots (a key names the same document in each of them)."""
    out: dict[str, dict] = {}
    for name in SNAPSHOTS:
        meta = json.loads((ROOT / "data" / "snapshots" / f"{name}.json").read_text(encoding="utf-8"))
        assert meta["fetch"] == "data/fetch/reconstruction35.py", name
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
    subprocess.run([sys.executable, str(ROOT / "checks" / "check_ch35.py")], check=True)


if __name__ == "__main__":
    main("--offline" in sys.argv[1:])
