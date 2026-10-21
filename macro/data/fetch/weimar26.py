"""The sources of Chapter 26's snapshots: download them into the web cache, compare their hashes, run the check.

    python3 data/fetch/weimar26.py              # download what is missing from WEB_CACHE, then check
    python3 data/fetch/weimar26.py --offline    # use the cache only

The snapshots are weimar_facts (quotations with their page or paragraph), weimar_prices_1914_1919 and
weimar_prices_1920_1924 (Sargent's Table G1), weimar_budget_1923_1924 (Sargent's Table G5) and
weimar_notes_1923_1924 (Bresciani-Turroni, p. 337). Each lists the documents it was read from, with a URL and the
SHA-256 of the copy (under "sources" in weimar_facts, whose quotations verify_web_quotes.py checks, and under
"documents" in the four tables, which hold no quotations). This script fetches every document into the cache with
verify_web_quotes.fetch (documents only; no program that comes with a download is run), stops if a hash differs, and
then runs checks/check_ch26.py, which parses Tables G1 and G5 from the cached PDF and compares them with the snapshots
month by month. The quotations themselves are checked by data/fetch/verify_web_quotes.py.
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
SNAPSHOTS = ["weimar_facts", "weimar_prices_1914_1919", "weimar_prices_1920_1924", "weimar_budget_1923_1924",
             "weimar_notes_1923_1924"]


def sources() -> dict[str, dict]:
    """Every source named by the five snapshots (a key names the same document in each of them)."""
    out: dict[str, dict] = {}
    for name in SNAPSHOTS:
        meta = json.loads((ROOT / "data" / "snapshots" / f"{name}.json").read_text(encoding="utf-8"))
        assert meta["fetch"] == "data/fetch/weimar26.py", name
        for key, src in meta.get("sources", meta.get("documents", {})).items():
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
    subprocess.run([sys.executable, str(ROOT / "checks" / "check_ch26.py")], check=True)


if __name__ == "__main__":
    main("--offline" in sys.argv[1:])
