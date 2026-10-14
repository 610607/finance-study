"""Check quotations from modern publications and online editions against the documents themselves.

    python3 data/fetch/verify_web_quotes.py                      # every quotation snapshot with "sources"
    python3 data/fetch/verify_web_quotes.py data/snapshots/x.csv  # selected snapshots
    python3 data/fetch/verify_web_quotes.py --offline            # use the cache only

data/fetch/verify_quotes.py checks quotations from the classical-Chinese corpus. This script does the
same for the other rows of a quotation snapshot (columns id, value, numeral, file, quote): a row whose
`file` is a key of the "sources" object in the snapshot's .json is looked up in that document.

    "sources": {
      "bbm2017": {"url": "https://.../paper.pdf", "format": "pdf", "sha256": "...",
                  "version": "accepted manuscript", "retrieved": "2026-10-13"},
      ...
    }

`format` is pdf (text extracted with pdftotext), html (tags removed), json (all string values),
txt, or image (a scanned page read by eye: such rows are counted but not checked here, and the
source entry says which page was read). An entry may add "user_agent" for a host that refuses the default
one. Each document is downloaded once into
$WEB_CACHE (default ~/.cache/finance-study/web) and its SHA-256 is compared with the one recorded
when the chapter was written; a different hash is reported (the site may have changed the file)
but the quotations are still searched. Text and quotation are compared after normalizing
whitespace (a space next to a Chinese character is dropped), line-end hyphenation, typographic quotes
and dashes, and Unicode compatibility forms.
A site that cannot be reached is reported, not counted as a failure: network access differs
between sessions (docs/WORKFLOW.md §0).
"""
from __future__ import annotations

import csv
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import unicodedata
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SNAPSHOTS = HERE.parent / "snapshots"
CACHE = Path(os.environ.get("WEB_CACHE", Path.home() / ".cache" / "finance-study" / "web"))
UA = "Mozilla/5.0 (X11; Linux x86_64) finance-study quotation check"
# A space next to a Chinese character is dropped: pdftotext turns the line ends of a Chinese text into spaces,
# and Chinese writing has none of its own (applied to text and quotation alike, so no match is lost).
CJK_GAP = re.compile(r"(?<=[\u3000-\u303f\u3400-\u9fff]) | (?=[\u3000-\u303f\u3400-\u9fff])")


def normalize(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"([a-z])-[ \t]*\n\s*([a-z])", r"\1\2", s)   # a word hyphenated at a line end
    s = re.sub(r"(\d)-[ \t]*\n\s*(\d)", r"\1-\2", s)        # a range such as 5-12 broken after the dash
    for a, b in [("‘", "'"), ("’", "'"), ("“", '"'), ("”", '"'), ("–", "-"), ("—", "-"),
                 ("­", ""), ("‎", ""), ("‏", "")]:
        s = s.replace(a, b)
    s = re.sub(r"\s+", " ", s).strip()
    return CJK_GAP.sub("", s)                                # a line break inside Chinese text


def strings_in(obj) -> list[str]:
    if isinstance(obj, str):
        return [obj]
    if isinstance(obj, dict):
        return [s for v in obj.values() for s in strings_in(v)]
    if isinstance(obj, list):
        return [s for v in obj for s in strings_in(v)]
    return []


def text_of(path: Path, fmt: str) -> str:
    if fmt == "pdf":
        # pdftotext's reading order joins words hyphenated at line ends (and also ranges such as
        # "5-" + "12%"); -layout keeps the lines as printed. Search both.
        runs = [subprocess.run(["pdftotext", "-enc", "UTF-8", *opt, str(path), "-"], capture_output=True, text=True,
                               check=True).stdout for opt in ([], ["-layout"])]
        return "\n\f\n".join(runs)
    raw = path.read_text(encoding="utf-8", errors="replace")
    if fmt == "html":
        raw = re.sub(r"<(script|style)\b.*?</\1>", " ", raw, flags=re.S | re.I)
        return html.unescape(re.sub(r"<[^>]+>", " ", raw))
    if fmt == "json":
        return html.unescape(re.sub(r"<[^>]+>", " ", "\n".join(strings_in(json.loads(raw)))))
    return raw


def fetch(key: str, src: dict, offline: bool) -> tuple[Path | None, str]:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{key}.{src['format']}"
    if not path.exists():
        if offline:
            return None, "not in the cache (--offline)"
        try:
            # a few hosts refuse browser-like agents (FRASER accepts curl's): a source may name its own
            req = urllib.request.Request(src["url"], headers={"User-Agent": src.get("user_agent", UA)})
            with urllib.request.urlopen(req, timeout=90) as r:
                path.write_bytes(r.read())
        except Exception as e:  # noqa: BLE001 - any network failure is reported, not fatal
            return None, f"cannot download ({e.__class__.__name__}: {e})"
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if src.get("sha256") and digest != src["sha256"]:
        return path, f"SHA-256 differs from the recorded one ({digest[:12]}… vs {src['sha256'][:12]}…)"
    return path, ""


def snapshots_with_sources() -> list[Path]:
    out = []
    for f in sorted(SNAPSHOTS.glob("*.json")):
        meta = json.loads(f.read_text(encoding="utf-8"))
        if meta.get("sources") and f.with_suffix(".csv").exists():
            out.append(f.with_suffix(".csv"))
    return out


def main(paths: list[Path], offline: bool) -> None:
    bad, notes, found, skipped = [], [], 0, 0
    for snap in paths:
        meta = json.loads(snap.with_suffix(".json").read_text(encoding="utf-8"))
        sources = meta.get("sources", {})
        texts: dict[str, str | None] = {}
        with snap.open(encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                key = row["file"]
                if key not in sources:
                    continue
                src = sources[key]
                if src["format"] == "image" or not row["quote"].strip():
                    skipped += 1
                    continue
                if key not in texts:
                    path, msg = fetch(key, src, offline)
                    if msg:
                        notes.append(f"{snap.name}:{key}: {msg}")
                    texts[key] = normalize(text_of(path, src["format"])) if path else None
                if texts[key] is None:
                    skipped += 1
                    continue
                if normalize(row["quote"]) in texts[key]:
                    found += 1
                else:
                    bad.append(f"{snap.name}:{row['id']}: quotation not found in {key} ({src['url']})")
    for n in notes:
        print("NOTE:", n)
    for b in bad:
        print("ERROR:", b)
    print(f"{found} quotations found verbatim; {skipped} rows not checked here (scanned pages, rows without a "
          f"quotation, or documents that could not be downloaded).")
    if bad:
        raise SystemExit(1)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--offline"]
    main([Path(a) for a in args] or snapshots_with_sources(), "--offline" in sys.argv)
