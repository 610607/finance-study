"""US national accounts, annual, 1929 onward, from the BEA's bulk NIPA files.

    python3 data/fetch/bea_nipa_annual.py                 # download the two files (13 MB) and write the snapshot
    python3 data/fetch/bea_nipa_annual.py DATA REGISTER   # use copies of NipaDataA.txt and SeriesRegister.txt

The Bureau of Economic Analysis publishes every NIPA series as a flat file (apps.bea.gov/national/Release/TXT/):
NipaDataA.txt holds the annual values (series code, year, value) and SeriesRegister.txt the label and the table
lines of each code. The script checks that every code below still carries the expected label, keeps the listed
series and writes data/snapshots/bea_nipa_annual.csv (millions of current dollars; real GDP in millions of chained
2017 dollars). The files are replaced at every BEA release, so a later download can differ from the snapshot
(revisions); the SHA-256 printed here is recorded in the snapshot's .json.
"""
from __future__ import annotations

import csv
import hashlib
import sys
import tempfile
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "snapshots" / "bea_nipa_annual.csv"
BASE = "https://apps.bea.gov/national/Release/TXT/"
# (BEA series code, label in SeriesRegister.txt, table:line where it is printed, column in the snapshot)
SERIES = [
    ("A191RC", "Gross domestic product", "T10105:1", "gdp"),
    ("A191RX", "Gross domestic product", "T10106:1", "gdp_real_2017"),
    ("A261RC", "Gross domestic income", "T11000:1", "gdi"),
    ("A030RC", "Statistical discrepancy", "T11000:24", "stat_discrepancy"),
    ("A001RC", "Gross national product", "T10705:4", "gnp"),
    ("A023RC", "Gross national income", "T10705:28", "gni"),
    ("A032RC", "National income", "T10705:16", "national_income"),
    ("A006RC", "Gross private domestic investment", "T50100:22", "gross_private_investment"),
    ("A024RC", "Less: Consumption of fixed capital", "T50100:14", "private_cfc"),
    ("A557RC", "Private", "T50100:50", "net_private_investment"),
    ("A929RC", "Gross saving", "T50100:1", "gross_saving"),
    ("W170RC", "Gross domestic investment", "T50100:21", "gross_domestic_investment"),
    ("W167RC", "Less: Capital account transactions (net)", "T50100:28", "capital_account_net"),
    ("W162RC", "Net lending or net borrowing (-), NIPAs", "T50100:35", "net_lending_nation"),
    ("W994RC", "Private", "T50100:36", "net_lending_private"),
    ("AD01RC", "Net lending (+)/Net borrowing (-) (1 - 2 - 31) (GNLB)", "T50100:39", "net_lending_government"),
]


def get(name: str, path: Path | None) -> Path:
    if path is None:
        path = Path(tempfile.mkdtemp(prefix="bea_")) / name   # downloads stay out of the repository
        req = urllib.request.Request(BASE + name, headers={"User-Agent": "curl/8"})
        with urllib.request.urlopen(req, timeout=300) as r:
            path.write_bytes(r.read())
    print(f"{path.name}: sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}")
    return path


def main(data_file: Path | None, register_file: Path | None) -> None:
    data_file, register_file = get("NipaDataA.txt", data_file), get("SeriesRegister.txt", register_file)
    with register_file.open(encoding="utf-8") as fh:
        register = {r["%SeriesCode"]: r for r in csv.DictReader(fh)}
    for code, label, line, _ in SERIES:
        r = register.get(code)
        if r is None or r["SeriesLabel"] != label or line not in r["TableId:LineNo"].split("|"):
            raise ValueError(f"{code}: expected {label!r} on {line}, register has {r and r['SeriesLabel']!r}")
    names = {code: name for code, _, _, name in SERIES}
    values: dict[int, dict[str, int]] = {}
    with data_file.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["%SeriesCode"] in names:
                values.setdefault(int(r["Period"]), {})[names[r["%SeriesCode"]]] = int(r["Value"].replace(",", ""))
    cols = ["year"] + [name for *_, name in SERIES]
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for year in sorted(values):
            w.writerow([year] + [values[year].get(c, "") for c in cols[1:]])
    print(f"wrote {OUT} ({len(values)} years, {min(values)}-{max(values)})")


if __name__ == "__main__":
    args = [Path(a) for a in sys.argv[1:3]]
    main(*(args + [None] * (2 - len(args))))
