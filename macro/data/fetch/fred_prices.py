"""US price indices, wages and Treasury yields for Chapter 3, from FRED (Federal Reserve Bank of St. Louis).

    python3 data/fetch/fred_prices.py            # download the series and write the two snapshots
    python3 data/fetch/fred_prices.py DIR        # use copies of the fredgraph CSV files kept in DIR

Each series is downloaded as https://fred.stlouisfed.org/graph/fredgraph.csv?id=CODE. The script checks that
every file has the expected header, merges the series by date and writes
  data/snapshots/fred_prices_monthly.csv   CPI-U (seasonally adjusted and not), chained CPI-U, PCE price index,
                                           average hourly earnings of production and nonsupervisory employees
  data/snapshots/fred_prices_quarterly.csv GDP implicit price deflator (2017 = 100, seasonally adjusted)
  data/snapshots/fred_yields_daily.csv     10-year and 2-year nominal Treasury yields and the 10-year TIPS yield
                                           (constant maturity, percent), 1997 onward
The SHA-256 of every downloaded file is printed; the values of the 2026-10-14 download are in the snapshots'
.json. FRED serves the latest vintage, so a later download can differ (CPI seasonal factors are revised every
February; the yields are not revised).
"""
from __future__ import annotations

import csv
import hashlib
import sys
import tempfile
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SNAP = HERE.parent / "snapshots"
URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="
MONTHLY = ["CPIAUCSL", "CPIAUCNS", "SUUR0000SA0", "PCEPI", "AHETPI"]
QUARTERLY = ["GDPDEF"]
DAILY = ["DGS10", "DGS2", "DFII10"]
DAILY_FROM = "1997-01-01"


def get(code: str, folder: Path | None) -> Path:
    if folder is None:
        folder = Path(tempfile.mkdtemp(prefix="fred_"))      # downloads stay out of the repository
        req = urllib.request.Request(URL + code, headers={"User-Agent": "curl/8"})
        with urllib.request.urlopen(req, timeout=120) as r:
            (folder / f"{code}.csv").write_bytes(r.read())
    path = folder / f"{code}.csv"
    print(f"{code}: sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}")
    return path


def read(code: str, folder: Path | None) -> dict[str, str]:
    with get(code, folder).open(encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    if rows[0] != ["observation_date", code]:
        raise ValueError(f"{code}: unexpected header {rows[0]}")
    return {d: v for d, v in rows[1:] if v not in ("", ".")}


def write(name: str, codes: list[str], series: dict[str, dict[str, str]], start: str = "") -> None:
    dates = sorted({d for c in codes for d in series[c] if d >= start})
    with (SNAP / f"{name}.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["date"] + codes)
        for d in dates:
            w.writerow([d] + [series[c].get(d, "") for c in codes])
    print(f"wrote {name}.csv ({len(dates)} rows, {dates[0]} to {dates[-1]})")


def main(folder: Path | None) -> None:
    series = {c: read(c, folder) for c in MONTHLY + QUARTERLY + DAILY}
    write("fred_prices_monthly", MONTHLY, series)
    write("fred_prices_quarterly", QUARTERLY, series)
    write("fred_yields_daily", DAILY, series, DAILY_FROM)


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
