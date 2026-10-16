"""Sweden under the gold standard: the consumer price index, the Riksbank's discount rate and the yield on long-term
government bonds, 1870-1913 (Chapter 25).

    python3 data/fetch/riksbank_sweden25.py              # download the two workbooks and write the snapshots
    python3 data/fetch/riksbank_sweden25.py DIR          # use copies already downloaded into DIR

From the Riksbank's "Historical Monetary and Financial Statistics for Sweden":
  Volume I, ch. 8 (Edvinsson and Soderberg 2010), Table I.A8.1 "A Consumer Price Index for Sweden 1290-", column
    "Deflation index 1914 = 100" (version 2.1 of the file);
  Volume II, ch. 6 (Waldenstrom 2014), version 2.0 of the file:
    Table II.A6.9 "Short-term interest rate, 1856-", monthly, per cent: the Riksbank's discount rate (diskonto),
      which the chapter uses as the short-term rate until 1983;
    Table II.A6.10 "Long-run government bond yields, 1874-", monthly, per cent: yields on government bonds from the
      price lists of the Stockholm stockbrokers Hakansson and Zethraeus (bonds of 1872, 1880, 1887 and 1914);
    Table II.A6.3 "Yields on short- and long-term government securities, 1856-", annual (the December values of
      the two monthly tables, as the script checks).
The script checks the headings and writes
  data/snapshots/riksbank_sweden_1870_1913.csv           annual: cpi_1914_100, discount_rate_dec, bond_yield_dec
  data/snapshots/riksbank_sweden_monthly_1870_1913.csv   monthly: discount_rate, bond_yield
It stores the values as published; averages, changes and correlations are the book's own calculations.
"""
from __future__ import annotations

import csv
import hashlib
import sys
import urllib.request
from pathlib import Path

import xlrd

HERE = Path(__file__).resolve().parent
SNAP = HERE.parent / "snapshots"
OUT_A = SNAP / "riksbank_sweden_1870_1913.csv"
OUT_M = SNAP / "riksbank_sweden_monthly_1870_1913.csv"
BASE = "https://www.riksbank.se/globalassets/media/forskning/monetar-statistik/"
FILES = {"I": "volym1/volumeich8consumerpriceindex.xls", "II": "volym2/volumeiich6stocksandbonds.xls"}
UA = "finance-study-textbook-check/1.0"
FIRST, LAST = 1870, 1913


def title(sh, row: int, col: int, text: str) -> None:
    got = str(sh.cell_value(row, col)).strip()
    if got != text:
        raise ValueError(f"{sh.name}: cell ({row}, {col}) is {got!r}, expected {text!r}")


def main(d: Path) -> None:
    books = {}
    for vol, name in FILES.items():
        p = d / Path(name).name
        if not p.exists():
            req = urllib.request.Request(BASE + name, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                p.write_bytes(r.read())
        print(f"{p.name}: sha256 {hashlib.sha256(p.read_bytes()).hexdigest()}")
        books[vol] = xlrd.open_workbook(str(p))

    cpi_sh = books["I"].sheet_by_name("Table I.A8.1")
    title(cpi_sh, 2, 1, "Table I.A8.1 A Consumer Price Index for Sweden 1290–")
    title(cpi_sh, 3, 1, "Deflation index 1914 = 100")
    cpi = {int(r[0]): r[1] for r in (cpi_sh.row_values(i) for i in range(4, cpi_sh.nrows))
           if isinstance(r[0], float) and FIRST <= r[0] <= LAST}

    monthly = {}
    for sheet, head, name in [("Table II.A6.9", "Table II.A6.9 Short-term interest rate, 1856–", "discount_rate"),
                              ("Table II.A6.10", "Table II.A6.10 Long-run government bond yields, 1874–", "bond_yield")]:
        sh = books["II"].sheet_by_name(sheet)
        title(sh, 2, 1, head)
        title(sh, 3, 0, "YYYY:MM")
        title(sh, 3, 1, "per cent")
        s = {}
        for i in range(4, sh.nrows):
            k, v = sh.row_values(i)[:2]
            y, m = (int(x) for x in str(k).split(":"))
            if FIRST <= y <= LAST and isinstance(v, float):
                s[(y, m)] = v
        monthly[name] = s

    ann = books["II"].sheet_by_name("Table II.A6.3")
    title(ann, 2, 1, "Table II.A6.3 Yields on short- and long-term government securities, 1856–")
    title(ann, 3, 1, "Short-term government bill yield")
    title(ann, 3, 3, "Long-term government bond yield")
    dec = {"discount_rate_dec": {}, "bond_yield_dec": {}}
    for i in range(5, ann.nrows):
        r = ann.row_values(i)
        if isinstance(r[0], float) and FIRST <= r[0] <= LAST:
            y = int(r[0])
            if isinstance(r[1], float):
                dec["discount_rate_dec"][y] = r[1]
            if isinstance(r[3], float):
                dec["bond_yield_dec"][y] = r[3]
    # the annual table holds the December values of the monthly tables (rounded to two decimals)
    for col, name in [("discount_rate_dec", "discount_rate"), ("bond_yield_dec", "bond_yield")]:
        for y, v in dec[col].items():
            if abs(monthly[name][(y, 12)] - v) > 0.006:
                raise ValueError(f"{col} {y}: annual {v}, December {monthly[name][(y, 12)]}")

    with OUT_A.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "cpi_1914_100", "discount_rate_dec", "bond_yield_dec"])
        for y in range(FIRST, LAST + 1):
            w.writerow([y, round(cpi[y], 6)] + ["" if y not in dec[c] else dec[c][y] for c in dec])
    with OUT_M.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["month", "discount_rate", "bond_yield"])
        for y in range(FIRST, LAST + 1):
            for m in range(1, 13):
                w.writerow([f"{y}-{m:02d}"] + ["" if (y, m) not in monthly[c] else round(monthly[c][(y, m)], 6)
                                              for c in monthly])
    print(f"{LAST - FIRST + 1} years -> {OUT_A}; {12 * (LAST - FIRST + 1)} months -> {OUT_M}")
    for c, s in monthly.items():
        print(f"  {c}: {min(s)} - {max(s)}, {len(s)} months")


if __name__ == "__main__":
    default = Path.home() / ".cache" / "finance-study" / "riksbank"
    d = Path(sys.argv[1]) if len(sys.argv) > 1 else default
    d.mkdir(parents=True, exist_ok=True)
    main(d)
