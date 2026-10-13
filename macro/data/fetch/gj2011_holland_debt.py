"""The size and composition of Holland's public debt, 1591-1720, from Gelderblom & Jonker (2011).

    python3 data/fetch/gj2011_holland_debt.py          # download the article and write the snapshot
    python3 data/fetch/gj2011_holland_debt.py FILE     # use a copy already downloaded

O. Gelderblom and J. Jonker, "Public Finance and Economic Growth: The Case of Holland in the Seventeenth
Century", Journal of Economic History 71(1), 2011, Appendix Tables 1A (1591-1646) and 1B (1647-1720):
total debt outstanding at the end of each year (guilders) and the shares (%) of life annuities (A),
redeemable annuities (B), bills (C), tax-exempt life annuities (D), tax-exempt bills (E) and lottery
loans (F). The PDF is the published article as posted on a course page at Boston University. The script
reads the text layer (pdftotext -layout), takes every line "year total share ..." of the two tables in
column order (a year gives three, five or six shares; no table row leaves a column blank in between),
checks that the years run from 1591 to 1720 without a gap and that the shares of each year add up to
between 96 and 100.5 per cent (as printed, those of 1655-1665 add up to only 96.5-99.4), and writes
data/snapshots/gj2011_holland_debt.csv.
"""
from __future__ import annotations

import csv
import hashlib
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "snapshots" / "gj2011_holland_debt.csv"
URL = "https://people.bu.edu/chamley/HSFref/GelderblomJonkerJEH11.pdf"
SHA256 = "ae400034e1148e92ac2bbb39750fe5272738dde47f1aec6af9fb95946f0dbd9e"
UA = "Mozilla/5.0 (X11; Linux x86_64) finance-study data fetch"
COLS = ["life_pct", "redeemable_pct", "bills_pct", "taxfree_life_pct", "taxfree_bills_pct", "lottery_pct"]
ROW = re.compile(r"^\s*(1[5-7]\d\d)\s+(\d{1,3}(?:,\d{3})+)((?:\s+\d+\.\d)+)\s*$")


def main(path: Path) -> None:
    if not path.exists():
        req = urllib.request.Request(URL, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=120) as r:
            path.write_bytes(r.read())
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    print(f"{path.name}: sha256 {sha}" + ("" if sha == SHA256 else f" (recorded {SHA256}: the file has changed)"))
    text = subprocess.run(["pdftotext", "-enc", "UTF-8", "-layout", str(path), "-"], capture_output=True,
                          text=True, check=True).stdout
    start = text.index("APPENDIX TABLE 1A")
    end = text.index("REFERENCES", start)
    rows = {}
    for line in text[start:end].splitlines():
        m = ROW.match(line)
        if not m:
            continue
        year, total = int(m.group(1)), int(m.group(2).replace(",", ""))
        shares = [float(x) for x in m.group(3).split()]
        if len(shares) not in (3, 5, 6) or year in rows:
            raise ValueError(f"unexpected row: {line!r}")
        if not 96.0 <= sum(shares) <= 100.5:
            raise ValueError(f"{year}: shares add up to {sum(shares):.1f}")
        rows[year] = (total, shares)
    if sorted(rows) != list(range(1591, 1721)):
        raise ValueError(f"years found: {min(rows)}-{max(rows)}, {len(rows)} rows")
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "total_guilders"] + COLS)
        for y in sorted(rows):
            total, shares = rows[y]
            w.writerow([y, total] + shares + [""] * (len(COLS) - len(shares)))
    print(f"{len(rows)} years -> {OUT}")


if __name__ == "__main__":
    default = Path.home() / ".cache" / "finance-study" / "web" / "gj2011.pdf"
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else default)
