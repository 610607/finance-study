"""British unemployment and average weekly earnings, 1860-1958, from the Bank of England's "A millennium of
macroeconomic data" (Chapter 38: the revised series against Phillips's curve).

    python3 data/fetch/boe_millennium_gb38.py           # download the workbook (27 MB) and write the snapshot
    python3 data/fetch/boe_millennium_gb38.py FILE      # use a copy of the workbook already downloaded

Annual, 1860-1958 (data/snapshots/boe_millennium_uk_1860_1958.csv), one row per calendar year:
  sheet "A50. Employment & unemployment", column 16: the unemployment rate based on unions that offered unemployment
  benefit schemes to their members, Feinstein (1972) and the Board of Trade (adjusted), per cent, 1860-1920
  (union_unemp_pct; empty from 1921);
  the same sheet, column 46: the unemployment rate defined as a per cent of the civilian working population,
  Feinstein (1972), 1920-1958 (civilian_unemp_pct; empty before 1920);
  sheet "A47. Wages and prices", column 55: average weekly wage earnings of the UK, 1913 = 100 (C. H. Feinstein,
  National Income, Expenditure and Output of the United Kingdom 1855-1965, Table 65, pp. T140-T141), weekly_earnings.
The script checks every heading it relies on and fails if one has moved. The CSV is written with LF line ends.
"""
from __future__ import annotations

import csv
import hashlib
import sys
import urllib.request
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from boe_millennium_gb27 import URL, UA, check, number  # noqa: E402

SNAP = HERE.parent / "snapshots"
OUT = SNAP / "boe_millennium_uk_1860_1958.csv"
FIRST, LAST = 1860, 1958
UNION_LAST, CIVILIAN_FIRST = 1920, 1920
A50, A47 = "A50. Employment & unemployment", "A47. Wages and prices"
HEADER = ["year", "union_unemp_pct", "civilian_unemp_pct", "weekly_earnings_1913_100"]


def write(path: Path, header: list[str], rows: list[list]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def main(path: Path) -> None:
    if not path.exists():
        req = urllib.request.Request(URL, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=300) as r:
            path.write_bytes(r.read())
    print(f"{path.name}: sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}")
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    years = list(range(FIRST, LAST + 1))
    table: dict[int, dict[str, object]] = {y: {} for y in years}

    rows = list(wb[A50].iter_rows(values_only=True))
    check(rows, A50, 16, [(2, "Unemployment rate"),
                          (3, "Unemployment rate based on unions that offered unemployment benefit schemes to their "
                              "members"),
                          (4, "Feinstein (1972)/Board of Trade (adjusted)")])
    check(rows, A50, 46, [(2, "Unemployment rate"), (3, "defined as % of civilian working population"),
                          (4, "Feinstein(1972)")])
    for r in rows[5:]:
        y = number(r[0])
        if y is not None and FIRST <= y <= LAST:
            y = int(y)
            if y <= UNION_LAST:
                table[y]["union_unemp_pct"] = number(r[16])
            if y >= CIVILIAN_FIRST:
                table[y]["civilian_unemp_pct"] = number(r[46])

    rows = list(wb[A47].iter_rows(values_only=True))
    check(rows, A47, 55, [(3, "UK"),
                          (4, "Average Weekly Wage earnings: 1855-1965. Source: C.H. Feinstein, National Income "
                              "Expenditure and Output of the United Kingdom 1855-1965 Table 65 pages T140 to T141"),
                          (5, "1913=100")])
    for r in rows[6:]:
        y = number(r[0])
        if y is not None and FIRST <= y <= LAST:
            table[int(y)]["weekly_earnings_1913_100"] = number(r[55])

    out = []
    for y in years:
        t = table[y]
        need = ["weekly_earnings_1913_100"] + (["union_unemp_pct"] if y <= UNION_LAST else []) + \
            (["civilian_unemp_pct"] if y >= CIVILIAN_FIRST else [])
        missing = [h for h in need if t.get(h) is None]
        assert not missing, (y, missing)
        out.append([y] + ["" if t.get(h) is None else round(float(t[h]), 6) for h in HEADER[1:]])
    write(OUT, HEADER, out)
    print(f"{len(years)} years {FIRST} - {LAST} -> {OUT}")


if __name__ == "__main__":
    default = Path.home() / ".cache" / "finance-study" / "boe" / "a-millennium-of-macroeconomic-data-for-the-uk.xlsx"
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else default
    p.parent.mkdir(parents=True, exist_ok=True)
    main(p)
