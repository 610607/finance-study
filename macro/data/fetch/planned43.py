"""The sources of Chapter 43: download them into the web cache, compare their hashes, check.

    python3 data/fetch/planned43.py              # download what is missing from WEB_CACHE, then check
    python3 data/fetch/planned43.py --offline    # use the cache only

One snapshot, planned_facts, holds the quotations of the chapter's sources with their page: the appeal of the CC of the
CPSU and the USSR Council of Ministers of 31 May 1962 and the resolution of the plenum of 29 September 1965 as Заря
Востока printed them (the scans of the National Parliamentary Library of Georgia; the masthead of 1962 and the whole
issue of 1965, whose text layer splits its words, read on page images); the report of the Leningrad city committee of
1 June 1962 as istmat.org publishes it (the transcription and the scan); two FRUS telegrams (1947, 1970) and a
memorandum of 1970; the CPC resolution of 27 June 1981 (12371.cn); table A-1 of 新中国五十年统计资料汇编 (1999) in a
third-party scan on scalar.usc.edu (read to verify the official numbers only; the file is never committed), table 4-2
of 中国统计年鉴 2000 and the terms of stats.gov.cn; Meng, Qian and Yared, NBER Working Paper 16361 (2010); Smil (1999)
on PubMed Central; Kornai (1980, volume A) and Kornai (1986), scans without a text layer on kornai-janos.hu (read on
page images); Kornai, Maskin and Roland (2003); the World Bank's report 1615a-YU (1978) and Yusuf (1977) with their
landing pages; the authority records of the Library of Congress and the Deutsche Nationalbibliothek (lobid.org).

The .json lists every document with a URL and the SHA-256 of the copy read. A key whose format is 'image' names a scan
read on page images rendered with pdftoppm: its file is the PDF of the same URL, cached under the key without its
suffix 'img' (zv1962_43img -> zv1962_43.pdf), and its hash is that PDF's. This script fetches each document into the
cache with verify_web_quotes.fetch (documents only; no program that comes with a download is run) and stops if a hash
differs. The quotations themselves are checked by data/fetch/verify_web_quotes.py, the numbers read from them and
from the transcriptions of the page images by checks/check_ch43.py, which this script runs last.
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
SNAP = ROOT / "data" / "snapshots"
FETCH = "data/fetch/planned43.py"


def sources() -> dict[str, dict]:
    """The documents of planned_facts.json; an image key becomes the PDF it was rendered from."""
    meta = json.loads((SNAP / "planned_facts.json").read_text(encoding="utf-8"))
    assert meta["fetch"] == FETCH
    out: dict[str, dict] = {}
    for key, src in meta["sources"].items():
        if src["format"] == "image":
            assert key.endswith("img") and src["url"].endswith(".pdf"), key
            key, src = key[:-3], {**src, "format": "pdf"}
            if key in out:
                assert (out[key]["url"], out[key]["sha256"]) == (src["url"], src["sha256"]), key
                continue
        out[key] = src
    return out


def main(offline: bool) -> None:
    for key, src in sorted(sources().items()):
        path, note = fetch(key, src, offline)
        if path is None or note:
            raise SystemExit(f"{key}: {note}")
        print(f"ok {key} {src['sha256'][:16]}")
    subprocess.run([sys.executable, str(ROOT / "checks" / "check_ch43.py")], check=True)


if __name__ == "__main__":
    main("--offline" in sys.argv[1:])
