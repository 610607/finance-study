"""Roman and early Byzantine coins found in India, by issuer, century and metal, from Appendix 6 of Darley (2014).

    python3 data/fetch/darley2014_coin_finds.py          # use the cached thesis PDF or download it, write the snapshot
    python3 data/fetch/darley2014_coin_finds.py FILE     # use a copy already downloaded

R. R. Darley, Indo-Byzantine Exchange, 4th to 7th Centuries: a Global History, PhD thesis, University of Birmingham
(2014), redacted version in the Birmingham eTheses repository. Appendix 6 (pages 67-71 of the appendices, pages
472-476 of the PDF) is "the data used to construct Fig. 5.8, along with published references": one line per
published group of coins, with the emperor, the century to which the thesis assigns the reign, the number of
gold, silver and copper coins, and the publication (Turner 1989, Sathyamurthy 1992, Subrahmanyam et al. 2008,
Krishnamurthy 2007). The script reads the table with `pdftotext -bbox` (poppler), assigns each number to the
column whose heading (Gold, Silver, Copper) ends nearest to it, adds up the lines and writes
data/snapshots/darley2014_coin_finds.csv:

    issuer, century (pre-1st, 1st, ..., 7th, as in the table), metal (gold, silver, copper), coins, entries
    (the number of lines of the table added up)

The table's "Severus" is written as "Septimius Severus"; "Republican" lines are dated "Pre-1st century A.D." (on one of them only "A.D." is on the line of the number). The
sums are compared with the totals of the note to Fig. 5.8 (p. 249), which the chapter quotes (india_facts, row
da_totals); the differences are printed and listed in the .json. The thesis reads "Further distribution or
reproduction in any format is prohibited without the permission of the copyright holder", so neither the PDF nor
the .csv is kept in the repository (.gitignore): run this script before the check script and the figures of
Chapter 9. The SHA-256 of the PDF is printed so that it can be compared with the one recorded in the .json.
"""
from __future__ import annotations

import collections
import csv
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "snapshots" / "darley2014_coin_finds.csv"
CACHE = Path.home() / ".cache" / "finance-study" / "web" / "darley2014.pdf"
URL = "https://etheses.bham.ac.uk/id/eprint/5357/1/Darley14PhD_redacted.pdf"
SHA256 = "c3400e2bb1366ae4178b72b98224fea5cbbc43c6751294d3611b457df7b74536"
UA = "finance-study-quote-check/1.0 (https://github.com/610607/finance-study)"
PAGES = (472, 476)
# the note to Fig. 5.8: (century, metal) -> coins
NOTE = {("pre-1st", "silver"): 7, ("pre-1st", "gold"): 6, ("1st", "silver"): 4174, ("1st", "gold"): 756,
        ("2nd", "gold"): 378, ("3rd", "gold"): 12, ("4th", "gold"): 1, ("4th", "copper"): 616,
        ("5th", "gold"): 84, ("5th", "copper"): 101, ("6th", "gold"): 21, ("7th", "gold"): 2}
WORD = re.compile(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>')
ROW = re.compile(r"^(.*?)\s+(\d+(?:st|nd|rd|th)|Pre-1st)\s+century(?:\s+A\.D\.)?$")


def pdf(path: Path | None) -> Path:
    if path is None:
        if not CACHE.exists():
            CACHE.parent.mkdir(parents=True, exist_ok=True)
            req = urllib.request.Request(URL, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r, CACHE.open("wb") as f:
                shutil.copyfileobj(r, f)
        path = CACHE
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    print(f"{path.name}: sha256 {digest}" + ("" if digest == SHA256 else f" (recorded: {SHA256})"))
    return path


def lines(path: Path) -> list[tuple[int, list[tuple[float, float, str]]]]:
    """(page, words of one printed line as (xMin, xMax, text)) for the pages of the appendix."""
    with tempfile.TemporaryDirectory() as tmp:
        html = Path(tmp) / "bbox.html"
        subprocess.run(["pdftotext", "-bbox", "-f", str(PAGES[0]), "-l", str(PAGES[1]), str(path), str(html)], check=True)
        text = html.read_text(encoding="utf-8")
    out = []
    for i, page in enumerate(text.split("<page ")[1:]):
        by_line = collections.defaultdict(list)
        for x0, y0, x1, _, w in WORD.findall(page):
            by_line[round(float(y0) / 3)].append((float(x0), float(x1), w))
        out += [(PAGES[0] + i, sorted(by_line[k])) for k in sorted(by_line)]
    return out


def main(path: Path | None) -> None:
    L = lines(pdf(path))
    head = next(ws for _, ws in L if [w for _, _, w in ws][:6] == ["Emperor", "Century", "Gold", "Silver", "Copper", "Publication"])
    cols = {w.lower(): x1 for _, x1, w in head if w in ("Gold", "Silver", "Copper")}
    left_of_numbers = min(x0 for x0, _, w in head if w == "Gold") - 15
    pub_from = next(x0 for x0, _, w in head if w == "Publication") - 2
    agg, n = collections.Counter(), collections.Counter()
    for page, ws in L:
        label = " ".join(w for x0, _, w in ws if x0 < left_of_numbers)
        m = ROW.match(label)
        if m:
            issuer, century = m.group(1), m.group(2).replace("Pre-1st", "pre-1st")
        elif label == "Republican A.D.":       # the century cell "Pre-1st century A.D." wraps onto this line
            issuer, century = "Republican", "pre-1st"
        else:
            continue
        issuer = {"Severus": "Septimius Severus"}.get(issuer, issuer)
        for x0, x1, w in ws:
            if left_of_numbers <= x0 and x1 < pub_from and re.fullmatch(r"\d+", w):
                metal = min(cols, key=lambda c: abs(cols[c] - x1))
                agg[(issuer, century, metal)] += int(w)
                n[(issuer, century, metal)] += 1
    order = ["pre-1st", "1st", "2nd", "3rd", "4th", "5th", "6th", "7th"]
    keys = sorted(agg, key=lambda k: (order.index(k[1]), k[0], k[2]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["issuer", "century", "metal", "coins", "entries"])
        w.writerows([*k, agg[k], n[k]] for k in keys)
    print(f"{sum(n.values())} lines of the table, {len(keys)} groups -> {OUT}")
    for c in order:
        for metal in ("gold", "silver", "copper"):
            s = sum(v for k, v in agg.items() if k[1] == c and k[2] == metal)
            t = NOTE.get((c, metal), 0)
            if s or t:
                print(f"  {c:8s} {metal:6s} table {s:5d}   note to Fig. 5.8 {t:5d}" + ("" if s == t else "   differs"))


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
