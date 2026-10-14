"""Monthly prices of six commodities in Babylon, 582-61 BC, in grams of silver, for Chapter 6.

    python3 data/fetch/babylon_prices.py            # download the workbook and write the snapshot
    python3 data/fetch/babylon_prices.py FILE       # use a saved copy of the workbook

Source: R. J. van der Spek, B. van Leeuwen and J. L. van Zanden, "Monthly prices of various commodities in
Babylon, -582BC to -61BC", DataverseNL, doi:10.34894/VJZ5Z9 (deposited 2025-12-22, licence CC0 1.0), file
appendix.xlsx. The dataset asks to be cited as van der Spek, van Leeuwen & van Zanden (2014), "Markets from
Ancient Babylonia to the Modern World - An Introduction", in their (eds.) A History of Market Performance
(Abingdon: Routledge), 1-16.

The workbook has one sheet: a header row (year, month, barley, dates, cuscuta, cress, sesame, wool), a row of
units ("gramme silver /100 litre" for the first five goods, "gramme silver per mina (=0.5 kg)" for wool) and
one row per month with a price. Years are negative for BC as in the workbook (-582 is 582 BC). The month is
the workbook's number 1-12; three rows have "?" for the month and are written with an empty month. The script
checks the SHA-256 of the workbook and the two header rows, and writes data/snapshots/babylon_prices.csv.
"""
from __future__ import annotations

import csv
import hashlib
import sys
import tempfile
import urllib.request
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "snapshots" / "babylon_prices.csv"
URL = "https://dataverse.nl/api/access/datafile/573029"
SHA256 = "152deda20f2bb39b4798ec05ba5afc76e684195c4e4aa7355fbbf43cb665fce3"
GOODS = ["barley", "dates", "cuscuta", "cress", "sesame", "wool"]
UNITS = ["gramme silver /100 litre"] * 5 + ["gramme silver per mina (=0.5 kg)"]


def main(path: Path | None) -> None:
    if path is None:
        path = Path(tempfile.mkdtemp(prefix="babylon_")) / "appendix.xlsx"   # downloads stay out of the repository
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"})
        with urllib.request.urlopen(req, timeout=120) as r:
            path.write_bytes(r.read())
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    print(f"appendix.xlsx: sha256 {digest}")
    if digest != SHA256:
        sys.exit(f"the workbook has changed (expected {SHA256}); check it before updating the snapshot")
    df = pd.read_excel(path, header=None)
    head, units = [str(v).strip() for v in df.iloc[0]], [str(v).strip() for v in df.iloc[1]]
    assert head == ["year", "month"] + GOODS, head
    assert units[2:] == UNITS, units
    n = 0
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["year", "month"] + GOODS)
        for _, r in df.iloc[2:].iterrows():
            month = str(r.iloc[1]).strip()
            month = "" if month == "?" else "%d" % int(float(month))
            vals = ["" if pd.isna(v) else ("%.2f" % float(v)) for v in r.iloc[2:8]]
            w.writerow(["%d" % int(r.iloc[0]), month] + vals)
            n += 1
    print(f"wrote {OUT} ({n} rows)")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
