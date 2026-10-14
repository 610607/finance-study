"""Prices of wheat and barley in Roman Egypt, AD 3-350, in drachmas per artaba, for Chapter 7.

    python3 -I data/fetch/kelly_prices.py            # download the appendix and write the snapshot
    python3 -I data/fetch/kelly_prices.py FILE       # use a saved copy of the appendix

Source: P. V. Kelly, "Third-Century Price Inflation Reassessed", Theoretical Roman Archaeology Journal 4(1): 5
(2021), doi:10.16995/traj.4338, licence CC BY 4.0; Supplementary file 2, "Appendix 2, database of prices"
(doi:10.16995/traj.4338.s2), a Word document (traj-4338-kelly.docx). Kelly compiled the prices from the
documentary papyri (Duke Databank, checked against earlier collections; his Appendix 1 gives the details).

The appendix has one table per good and period. This script keeps five of them: private wheat prices
before AD 274, state wheat prices before 274, barley prices before 274, and wheat and barley prices after
274. Each row of a table is one document. As Kelly does (2021, pp. 6 and 8), a document with several prices is
reduced to their median, and a date given as a range is placed at its midpoint; obols are converted at 6
to the drachma before AD 190 and 7 after (Kelly p. 8), talents at 6,000 drachmas. A price marked "<"
(an upper bound) is left out of the median; "10+" is read as 10; where Kelly gives two readings and
"Assumed to be" one of them, that one is used; "4 dr. 2 ob./3 ob." is read as its first reading; "13 and
1/3rd talents" is one price; "54[0]" (a digit restored by the editor of the papyrus) is 540; in a list that
mentions talents, a bare number below 1,000 is in talents and a larger one in drachmas. The
script uses only the standard library (zipfile and xml), checks the SHA-256 of the document and the
header of each table, and writes data/snapshots/kelly_egypt_prices.csv.
"""
from __future__ import annotations

import csv
import hashlib
import re
import statistics
import sys
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "snapshots" / "kelly_egypt_prices.csv"
URL = "https://traj.openlibhums.org/download/article/4338/supp_file/29/"
SHA256 = "42c9a29138d22a28cf7fb05e9090137d2a2fa8df2db2412c870d5e915f7dc583"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
# table title in the appendix -> (short name, expected header)
KEEP = {
    "Private Wheat Prices pre-AD 274": ("wheat_private",
        ["Date", "Amounts in dr./art.", "Nature of price", "Nome", "Reference"]),
    "State Wheat Prices pre-AD 274": ("wheat_state",
        ["Date", "Amounts in dr./art.", "Description", "Nome", "Reference"]),
    "Barley Prices pre-AD 274": ("barley",
        ["Date", "Amounts in dr./art.", "Nature of price", "Nome", "Reference"]),
    "Wheat prices post-AD 274": ("wheat_post274",
        ["Date", "Amounts per art. in drachmas unless stated", "Nature of price", "Nome", "Reference"]),
    "Barley Prices post-AD 274": ("barley_post274",
        ["Date", "Amounts per art. in drachmas unless stated", "Nature of price", "Nome", "Reference"]),
}


def tables(path: Path):
    body = ET.fromstring(zipfile.ZipFile(path).read("word/document.xml")).find(W + "body")
    text = lambda el: "".join(t.text or "" for t in el.iter(W + "t")).strip()
    title = None
    for el in body:
        if el.tag == W + "p" and text(el):
            title = text(el)
        elif el.tag == W + "tbl":
            yield title, [[text(tc) for tc in tr.findall(W + "tc")] for tr in el.iter(W + "tr")]


def dating(s: str):
    """(first year, last year, midpoint, uncertain) of a date such as '45', '46-7', 'c.75-125', '217(?)'."""
    uncertain = "?" in s or s.startswith("c.")
    t = s.replace("(?)", "").replace("?", "").replace("c.", "").replace(" ", "")
    if " or " in s or not t:
        return None, None, None, True
    m = re.fullmatch(r"(\d+)(?:-(\d+))?", t)
    if not m:
        return None, None, None, True
    a, b = int(m.group(1)), m.group(2)
    if b is None:
        return a, a, float(a), uncertain
    if len(b) < len(m.group(1)):                       # 46-7 -> 47, 202-31 -> 231
        b = m.group(1)[: len(m.group(1)) - len(b)] + b
    b = int(b)
    return a, b, (a + b) / 2, uncertain


def amounts(s: str, year: float | None) -> list[float]:
    """The prices of one document in drachmas. In a list that mentions talents ('45, 50, 40 talents', '20 talents,
    120,000'), a bare number below 1,000 is in talents and a larger one in drachmas, as in every such list of the
    appendix; '13 and 1/3rd talents' is one price; '54[0]' (a digit restored by the editor) is 540."""
    obols = 7 if (year or 0) >= 190 else 6
    m = re.search(r"Assumed to be (\d+(?:\.\d+)?)", s)
    if m:
        return [float(m.group(1))]
    s = re.sub(r"(\d),(\d{3})", r"\1\2", s).replace("[", "").replace("]", "")
    s = re.sub(r"(\d+) and (\d)/(\d)(?:st|nd|rd|th)?s?",
               lambda m: "%.12g" % (int(m.group(1)) + int(m.group(2)) / int(m.group(3))), s)
    s = s.replace(" and ", ", ")
    talents = "talent" in s
    out = []
    for part in re.split(r",\s*", s):
        part = part.strip()
        if not part or part.startswith("<"):
            continue
        m = re.match(r"(\d+(?:\.\d+)?)\s*dr\.\s*(\d+(?:\.\d+)?)\s*ob\.", part)
        if m:
            out.append(float(m.group(1)) + float(m.group(2)) / obols)
            continue
        m = re.match(r"(\d+(?:\.\d+)?)", part)
        if m:
            x = float(m.group(1))
            out.append(x * 6000 if talents and ("talent" in part or x < 1000) else x)
    return out


def main(path: Path | None) -> None:
    if path is None:
        path = Path(tempfile.mkdtemp(prefix="kelly_")) / "traj-4338-kelly.docx"   # downloads stay out of the repository
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"})
        with urllib.request.urlopen(req, timeout=120) as r:
            path.write_bytes(r.read())
    if not zipfile.is_zipfile(path):
        # On 2026-10-14 the first download worked; later ones got an HTML "not a bot" check page.
        sys.exit("the site did not return the Word document (perhaps a bot-check page); download it in a browser "
                 f"from {URL} and pass the file to this script")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    print(f"traj-4338-kelly.docx: sha256 {digest}")
    if digest != SHA256:
        sys.exit(f"the appendix has changed (expected {SHA256}); check it before updating the snapshot")
    seen, rows = set(), []
    for title, tab in tables(path):
        if title not in KEEP:
            continue
        name, head = KEEP[title]
        assert tab[0] == head, (title, tab[0])
        seen.add(title)
        for r in tab[1:]:
            lo, hi, mid, unc = dating(r[0])
            vals = amounts(r[1], mid)
            dr = statistics.median(vals) if vals and mid is not None else None
            rows.append([name, r[0], lo or "", hi or "", "" if mid is None else "%g" % mid, int(unc), r[1],
                         "" if dr is None else "%g" % round(dr, 4), len(vals), r[2], r[3], r[4]])
    assert seen == set(KEEP), set(KEEP) - seen
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["table", "date", "year_from", "year_to", "year", "uncertain", "amounts", "dr_per_artaba",
                    "n_prices", "nature", "nome", "reference"])
        w.writerows(rows)
    counts = {n: sum(r[0] == n for r in rows) for n, _ in KEEP.values()}
    print(f"wrote {OUT} ({len(rows)} rows: {counts})")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
