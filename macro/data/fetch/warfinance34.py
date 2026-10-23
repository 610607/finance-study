"""The sources of Chapter 34's quotation snapshot: download them into the web cache, compare their hashes, run the check.

    python3 data/fetch/warfinance34.py              # download what is missing from WEB_CACHE, then check
    python3 data/fetch/warfinance34.py --offline    # use the cache only

The snapshot is warfinance_facts (quotations with their page): Keynes, How to Pay for the War (1940), the OCR text of
the Digital Library of India's copy on archive.org and the item's metadata; House of Commons Hansard of 7 April 1941
(Sir Kingsley Wood's Budget speech) and House of Lords Hansard of 23 May 1944 (International Monetary Fund), from UK
Parliament's historic Hansard site; Lerner (Social Research, February 1943), Kalecki (The Political Quarterly,
October-December 1943) and Domar (American Economic Review, December 1944) in the OCR texts on archive.org; the
Federal Reserve Bulletin of June 1943 (the texts of the White and Keynes plans) and September 1944 (Goldenweiser and
Bourneuf, 'Bretton Woods Agreements'); the hearings of the Senate Committee on Banking and Currency on the Bretton
Woods Agreements Act (June 1945); the Annual Report of the Board of Governors for 1942 (FRASER); Harrison's preprints
on the economics of World War II (1998) and war finance (1992) from his Warwick pages; the Famine Inquiry
Commission's Report on Bengal (1945) and its archive.org metadata; Chapter 30's cached copies of the judgment of the
International Military Tribunal, Nazi Conspiracy and Aggression vol. II, Shizume (2009), Ide (2003) and the Bank of
Japan's chronology; the authority records of the Library of Congress, the Bibliotheque nationale de France and the
Deutsche Nationalbibliothek (lobid.org). Its .json lists every document with a URL and the SHA-256 of the copy read;
this script fetches each one into the cache with verify_web_quotes.fetch (documents only; no program that comes with
a download is run), stops if a hash differs, and then runs checks/check_ch34.py. The sources of format "image" name a
scan whose pages were read by eye on images rendered with pdftoppm (Keynes's pp. vi, 15, 16, 23, 28 and 32; Domar's
pp. 799, 803, 810 and 811; the Final Act, Cmd. 6546; p. 14 of the Annual Report for 1942; p. 110 of the Famine
Inquiry Commission's report; the table of federal finances in Historical Statistics); they are not fetched here. The
quotations themselves are checked by data/fetch/verify_web_quotes.py.

British central government finance, the national debt and consumer prices (1913-1950) come from
data/fetch/boe_millennium_gb34.py (the Bank of England's millennium workbook).
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
SNAPSHOTS = ["warfinance_facts"]


def sources() -> dict[str, dict]:
    """Every source named by the snapshots (a key names the same document in each of them)."""
    out: dict[str, dict] = {}
    for name in SNAPSHOTS:
        meta = json.loads((ROOT / "data" / "snapshots" / f"{name}.json").read_text(encoding="utf-8"))
        assert meta["fetch"] == "data/fetch/warfinance34.py", name
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
    subprocess.run([sys.executable, str(ROOT / "checks" / "check_ch34.py")], check=True)


if __name__ == "__main__":
    main("--offline" in sys.argv[1:])
