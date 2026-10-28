"""The sources of Chapter 36's quotation snapshot: download them into the web cache, compare their hashes, run the check.

    python3 data/fetch/brettonwoods36.py              # download what is missing from WEB_CACHE, then check
    python3 data/fetch/brettonwoods36.py --offline    # use the cache only

The snapshot is brettonwoods_facts (quotations with their page): Bordo, 'The Bretton Woods International Monetary
System: A Historical Overview', Garber, 'The Collapse of the Bretton Woods Fixed Exchange Rate System', and
Eichengreen, 'Epilogue: Three Perspectives on the Bretton Woods System', the chapter PDFs of Bordo and Eichengreen
(eds.), A Retrospective on the Bretton Woods System (NBER, 1993), with the volume's front matter; the Annual Reports
of the Bank for International Settlements of 1948, 1950, 1959, 1961, 1962, 1966, 1968 and 1970 and the BIS's terms
and conditions; Foreign Relations of the United States 1964-1968, vol. VIII, documents 36, 135, 191 and 193 (the
Office of the Historian); House of Commons Hansard of 20 November 1967 (UK Parliament's historic Hansard site);
Gourinchas, Rey and Govillot, IMES Discussion Paper 2010-E-20 (Bank of Japan); Lelart (2018) in the Revue
Internationale des Economistes de Langue Francaise; the authority records of the Library of Congress and of the
Deutsche Nationalbibliothek (lobid.org). Its .json lists every document with a URL and the SHA-256 of the copy read;
this script fetches each one into the cache with verify_web_quotes.fetch (documents only; no program that comes with
a download is run), stops if a hash differs, and then runs checks/check_ch36.py. The sources of format "image" name
pages that were read by eye on images rendered with pdftoppm (Bordo's Table 1.2, Garber's Table 9.1, the copyright
page of the volume, and the tables of the Statistical Abstract of the United States 1964, 1968 and 1972, which are
scans without a text layer); they are not fetched here. The quotations themselves are checked by
data/fetch/verify_web_quotes.py.
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
SNAPSHOTS = ["brettonwoods_facts"]


def sources() -> dict[str, dict]:
    """Every source named by the snapshots (a key names the same document in each of them)."""
    out: dict[str, dict] = {}
    for name in SNAPSHOTS:
        meta = json.loads((ROOT / "data" / "snapshots" / f"{name}.json").read_text(encoding="utf-8"))
        assert meta["fetch"] == "data/fetch/brettonwoods36.py", name
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
    subprocess.run([sys.executable, str(ROOT / "checks" / "check_ch36.py")], check=True)


if __name__ == "__main__":
    main("--offline" in sys.argv[1:])
