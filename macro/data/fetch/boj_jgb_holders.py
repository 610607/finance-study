"""Holders of Japanese government securities for Chapter 1, from the Bank of Japan's Flow of Funds, Chart 6-2
"Government bonds and treasury bills holdings by sector" of the release "Basic Figures".

    python3 data/fetch/boj_jgb_holders.py          # download the current release and write the snapshot
    python3 data/fetch/boj_jgb_holders.py DIR      # use DIR/sjexp.pdf (downloaded into DIR if it is not there)

The address always serves the latest release; the snapshot was written from "Basic Figures: Flow of Funds for the
Second Quarter of 2026 (Preliminary report)", September 17, 2026, SHA-256
e9d23d7bcf26ef6dbbc47bc031570dc022beacc43aaae2a9b6b628f9f0675177. A later release revises the recent quarters and
adds new ones; the script prints the release title and the hash, and reads whatever release it is given.
The chart's two panels are read from the text layer (pdftotext -layout):
  tb_jgb  (1) "treasury discount bills" and "central government securities and FILP bonds"
  jgb     (2) "central government securities and FILP bonds"
Each gives the share of each holding sector (percent, market value; "Figures are evaluated on a market value
basis") at the end of each quarter from March 2012, and the amounts outstanding in trillion yen at the end of the
latest quarter. Writes data/snapshots/boj_jgb_holders.csv: panel, month (YYYY-MM), unit (share_pct or tn_yen) and
the columns central_bank, depository, insurance_pension, public_pensions, households, overseas, others, total.
Bank of Japan terms (https://www.boj.or.jp/en/copyright.htm, 2026-10-14): "The information included in
the site may be copied or reproduced with the exceptions below. When copying or reproducing, the source, the Bank
of Japan, should be explicitly credited." (the exceptions are commercial use, material marked as needing
permission, and graphics and other image data).
"""
from __future__ import annotations

import csv
import hashlib
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "snapshots" / "boj_jgb_holders.csv"
URL = "https://www.boj.or.jp/en/statistics/sj/sjexp.pdf"
COLS = ["central_bank", "depository", "insurance_pension", "public_pensions", "households", "overseas", "others",
        "total"]
PANELS = [("tb_jgb", '(1) For "treasury discount bills"'), ("jgb", '(2) For "central government securities')]
SHARE = re.compile(r"^\s*(\d{4})?\s+(\d{1,2})\s+((?:\d+\.\d\d\s+){7})100\s*$")
AMOUNT = re.compile(r"^\s*(\d{4})\s+(\d{1,2})\s+((?:[\d,]+\s+){7}[\d,]+)\s*$")


def main(folder: Path | None) -> None:
    folder = folder or Path(tempfile.mkdtemp(prefix="boj_"))  # downloads stay out of the repository
    pdf = folder / "sjexp.pdf"
    if not pdf.exists():
        req = urllib.request.Request(URL, headers={"User-Agent": "curl/8"})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    pdf.write_bytes(r.read())
                break
            except urllib.error.URLError:
                if attempt == 3:
                    raise
                time.sleep(2 ** (attempt + 1))
    raw = pdf.read_bytes()
    if not raw.startswith(b"%PDF"):
        raise ValueError("the response is not a PDF")
    print(f"sjexp.pdf: sha256 {hashlib.sha256(raw).hexdigest()}")
    text = subprocess.run(["pdftotext", "-enc", "UTF-8", "-layout", str(pdf), "-"], capture_output=True, text=True,
                          check=True).stdout
    lines = text.splitlines()
    print("release:", " ".join(l.strip() for l in lines[:4] if l.strip()))
    starts = [next(i for i, l in enumerate(lines) if head in l) for _, head in PANELS] + [len(lines)]
    rows = []
    for (panel, _), a, b in zip(PANELS, starts, starts[1:]):
        year = None
        n = 0
        for l in lines[a:b]:
            m = SHARE.match(l)
            if m:
                year = m.group(1) or year
                v = m.group(3).split()
                rows.append([panel, f"{year}-{int(m.group(2)):02d}", "share_pct"] + v + ["100"])
                n += 1
                continue
            m = AMOUNT.match(l)
            if m and "," in m.group(3):
                v = [x.replace(",", "") for x in m.group(3).split()]
                rows.append([panel, f"{m.group(1)}-{int(m.group(2)):02d}", "tn_yen"] + v)
        if n < 50:
            raise ValueError(f"{panel}: only {n} quarters found")
        print(f"{panel}: {n} quarters")
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["panel", "month", "unit"] + COLS)
        w.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows)")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
