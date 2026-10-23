"""The sources of Chapter 32's quotation snapshot: download them into the web cache, compare their hashes, run the check.

    python3 data/fetch/generaltheory32.py              # download what is missing from WEB_CACHE, then check
    python3 data/fetch/generaltheory32.py --offline    # use the cache only

The snapshot is generaltheory_facts (quotations with their page or column): Keynes's General Theory (Macmillan, 1936)
and his Essays in Persuasion (1931: the broadcast 'Saving and Spending' of January 1931 and 'A Programme of
Expansion', May 1929, from the pamphlet written with H. D. Henderson), both in the OCR text of the Digital Library of
India's copies on archive.org; the Commons debates of 15 April 1929 (Churchill's Budget speech) and 4 November 1936
(Jarrow) in Historic Hansard; the Macmillan Committee's Minutes of Evidence (Sir Josiah Stamp, 4 April 1930); Kahn
(Economic Journal, June 1931), Pigou (Economica, May 1936), Ohlin (Economic Journal, March and June 1937), Keynes
(Economic Journal, June 1937) and Kalecki (Econometrica, 1935) in the OCR text of the journals on archive.org; Berg and
Jonung (1998), Shizume (2009), Baumol (1999) and Velde (2003), already used by earlier chapters; the people pages of
Historic Hansard and the authority records of the Library of Congress and the Bibliotheque nationale de France. Its
.json lists every document with a URL and the SHA-256 of the copy read; this script fetches each one into the cache
with verify_web_quotes.fetch (documents only; no program that comes with a download is run), stops if a hash
differs, and then runs checks/check_ch32.py. The sources of format "image" name a scan whose pages were read by eye on
images rendered with pdftoppm (pages of the General Theory and of Essays in Persuasion whose OCR is garbled or loses
the pound signs, Kahn's equations and table); they are not fetched here (their notes give the pages). The quotations
themselves are checked by data/fetch/verify_web_quotes.py.

Britain's unemployment, output, expenditure, trade and Bank Rate, 1919-1939, come from
data/fetch/boe_millennium_gb32.py (the Bank of England's "A millennium of macroeconomic data").
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
SNAPSHOTS = ["generaltheory_facts"]


def sources() -> dict[str, dict]:
    """Every source named by the snapshots (a key names the same document in each of them)."""
    out: dict[str, dict] = {}
    for name in SNAPSHOTS:
        meta = json.loads((ROOT / "data" / "snapshots" / f"{name}.json").read_text(encoding="utf-8"))
        assert meta["fetch"] == "data/fetch/generaltheory32.py", name
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
    subprocess.run([sys.executable, str(ROOT / "checks" / "check_ch32.py")], check=True)


if __name__ == "__main__":
    main("--offline" in sys.argv[1:])
