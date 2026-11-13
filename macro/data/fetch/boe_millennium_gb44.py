"""British unemployment and consumer-price inflation, 1954-1986, from the Bank of England's "A millennium of
macroeconomic data" (Chapter 44: the natural rate and the drifting Phillips curve).

    python3 data/fetch/boe_millennium_gb44.py           # download the workbook (27 MB) and write the snapshot
    python3 data/fetch/boe_millennium_gb44.py FILE      # use a copy of the workbook already downloaded

Annual, 1954-1986 (data/snapshots/boe_millennium_uk_1954_1986.csv), one row per calendar year:
  sheet "A47. Wages and prices", column 4: CPI inflation, GB/UK (GB+NI), annual inflation rate, per cent (cpi_infl_pct);
  the index of column 3 is "1949-2014 CPI (ONS)" for these years (its heading names the sources);
  sheet "A50. Employment & unemployment", column 9: the unemployment rate as a % of total UK workforce (unemp_pct),
  with column 6, unemployed (preferred measure adjusting 1946-1971 data for LFS/CC differences in female
  unemployment), and column 2, total employment in heads, thousands (unemployed_000s, employment_000s).
The script checks every heading it relies on, that column 9 is 100 x unemployed / (employment + unemployed), that from
1971 the two columns are the ONS Labour Force Survey series MGRZ (employment) and MGSC (unemployed) of columns 62 and
68, and that before 1971 the unemployed are the mid-year estimates of the Economic Trends Annual Supplement 1997
(column 53) plus the female adjustment (column 104) and employment moves with that supplement's workforce in
employment (column 49). The CSV is written with LF line ends.
"""
from __future__ import annotations

import hashlib
import sys
import urllib.request
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from boe_millennium_gb27 import URL, UA, check, number  # noqa: E402
from boe_millennium_gb38 import write  # noqa: E402

SNAP = HERE.parent / "snapshots"
OUT = SNAP / "boe_millennium_uk_1954_1986.csv"
FIRST, LAST, LFS = 1954, 1986, 1971
A50, A47 = "A50. Employment & unemployment", "A47. Wages and prices"
HEADER = ["year", "cpi_infl_pct", "unemp_pct", "unemployed_000s", "employment_000s"]
CPI_SOURCES = ("1661-1750, Schumpeter-Gilboy index from Mitchell(1988), 1750-1770 from Crafts and Mills (1991), "
               "1770-1882, Feinstein (1998), 1882-1914 Feinstein (1991),1914-1949 from ONS (O'Donoghue et al (2004)), "
               "1949-2014 CPI (ONS)")


def main(path: Path) -> None:
    if not path.exists():
        req = urllib.request.Request(URL, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=300) as r:
            path.write_bytes(r.read())
    print(f"{path.name}: sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}")
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    years = list(range(FIRST, LAST + 1))
    table: dict[int, dict[str, float]] = {y: {} for y in years}

    rows = list(wb[A47].iter_rows(values_only=True))
    check(rows, A47, 3, [(2, "Consumer Price Index (CPI) -  preferred measure"), (3, "GB/UK(GB+NI)"),
                         (4, CPI_SOURCES), (5, "Spliced index 2015=100")])
    check(rows, A47, 4, [(2, "CPI inflation"), (3, "GB/UK(GB+NI)"), (5, "annual inflation rate")])
    index = {}
    for r in rows[6:]:
        y = number(r[0])
        if y is not None and FIRST - 1 <= y <= LAST:
            index[int(y)] = number(r[3])
            if y >= FIRST:
                table[int(y)]["cpi_infl_pct"] = number(r[4])
    for y in years:                                   # column 4 is the change of the index of column 3
        assert abs(100 * (index[y] / index[y - 1] - 1) - table[y]["cpi_infl_pct"]) < 1e-6, y

    rows = list(wb[A50].iter_rows(values_only=True))
    check(rows, A50, 1, [(2, "Total Employment in Heads")])          # the heading spans columns 1 and 2
    check(rows, A50, 2, [(3, "with S.Ireland break retained in 1920")])
    check(rows, A50, 6, [(2, "Unemployed"),
                         (3, "Preferred measure adjusting 1946-1971 data for LFS/CC differences in female unemployment")])
    check(rows, A50, 8, [(2, "Total workforce/participation")])
    check(rows, A50, 9, [(2, "Unemployment rate"), (3, "as a % of total UK workforce")])
    check(rows, A50, 49, [(2, "Workforce in employment"), (3, "Mid year estimates"),
                          (4, "Economic Trends Annual Supplement 1997 edition")])
    check(rows, A50, 53, [(2, "Unemployed"), (3, "Mid year estimates"),
                          (4, "Economic Trends Annual Supplement 1997 edition")])
    check(rows, A50, 62, [(1, "LFS data 1971-2016"), (2, "Employment"), (4, "ONS: Series code MGRZ")])
    check(rows, A50, 68, [(2, "Unemployed"), (4, "ONS: Series code MGSC")])
    check(rows, A50, 104, [(3, "Scaled to match LFS CC discrepancy in female unemployment")])
    raw = {}
    for r in rows[5:]:
        y = number(r[0])
        if y is not None and FIRST <= y <= LAST + 1:
            raw[int(y)] = {c: number(r[c]) if c < len(r) else None for c in (2, 6, 8, 9, 49, 53, 62, 68, 104)}
    for y in years:
        c = raw[y]
        assert abs(c[8] - (c[2] + c[6])) < 1e-6 and abs(c[9] - 100 * c[6] / c[8]) < 1e-9, y
        if y >= LFS:                                  # the Labour Force Survey from 1971
            assert c[2] == c[62] and c[6] == c[68], y
        else:                                         # the 1997 supplement, the female adjustment, chained to 1971
            assert abs(c[6] - (c[53] + c[104])) < 1e-6, y
            assert abs(c[2] / raw[y + 1][2] - c[49] / raw[y + 1][49]) < 1e-12, y
        table[y].update(unemp_pct=c[9], unemployed_000s=c[6], employment_000s=c[2])

    out = []
    for y in years:
        t = table[y]
        missing = [h for h in HEADER[1:] if t.get(h) is None]
        assert not missing, (y, missing)
        out.append([y] + [round(float(t[h]), 6) for h in HEADER[1:]])
    write(OUT, HEADER, out)
    print(f"{len(years)} years {FIRST} - {LAST} -> {OUT}")


if __name__ == "__main__":
    default = Path.home() / ".cache" / "finance-study" / "boe" / "a-millennium-of-macroeconomic-data-for-the-uk.xlsx"
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else default
    p.parent.mkdir(parents=True, exist_ok=True)
    main(p)
