"""The Federal Reserve's balance sheet, US base and broad money and the Fed's administered rates, for Chapter 4,
from FRED (Federal Reserve Bank of St. Louis).

    python3 data/fetch/fred_money.py            # download the series and write the three snapshots
    python3 data/fetch/fred_money.py DIR        # use copies of the fredgraph CSV files kept in DIR

Each series is downloaded as https://fred.stlouisfed.org/graph/fredgraph.csv?id=CODE. The script checks that
every file has the expected header, merges the series by date and writes
  data/snapshots/fred_fed_weekly.csv     H.4.1, Wednesday levels, millions of dollars: total assets, Treasury
                                         securities and mortgage-backed securities held outright; Federal Reserve
                                         notes, deposits of depository institutions (reserve balances), the
                                         Treasury's General Account, reverse repurchase agreements, total
                                         liabilities and total capital
  data/snapshots/fred_money_monthly.csv  H.3 and H.6, billions of dollars: monetary base, M2 (not seasonally
                                         adjusted and seasonally adjusted), total reserves
  data/snapshots/fred_policy_rates_daily.csv  percent: effective federal funds rate, the target (to 2008-12-15)
                                         and the target range (from 2008-12-16), interest on excess and on
                                         required reserves (2008-10-09 to 2021-07-28), interest on reserve
                                         balances (from 2021-07-29) and the overnight reverse repo award rate;
                                         2007 onward. The effective federal funds rate is a New York Fed reference
                                         rate: its terms of use require a notice wherever the data are shown (see
                                         the snapshot's .json)
The SHA-256 of every downloaded file is printed; the values of the 2026-10-14 download are in the snapshots'
.json. FRED serves the latest vintage; H.4.1 levels are not revised, the money stock is (seasonal factors
and benchmarks).
"""
from __future__ import annotations

import csv
import hashlib
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SNAP = HERE.parent / "snapshots"
URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="
WEEKLY = ["WALCL", "TREAST", "WSHOMCB", "WLFN", "WLODLL", "WDTGAL", "WLRRAL", "WLTLECL", "WCTCL"]
MONTHLY = ["BOGMBASE", "M2NS", "M2SL", "TOTRESNS"]
DAILY = ["EFFR", "DFEDTAR", "DFEDTARU", "DFEDTARL", "IOER", "IORR", "IORB", "RRPONTSYAWARD"]
DAILY_FROM = "2007-01-01"


def get(code: str, folder: Path | None) -> Path:
    if folder is None:
        folder = Path(tempfile.mkdtemp(prefix="fred_"))      # downloads stay out of the repository
        req = urllib.request.Request(URL + code, headers={"User-Agent": "curl/8"})
        with urllib.request.urlopen(req, timeout=120) as r:
            (folder / f"{code}.csv").write_bytes(r.read())
        time.sleep(1)
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
    series = {c: read(c, folder) for c in WEEKLY + MONTHLY + DAILY}
    write("fred_fed_weekly", WEEKLY, series)
    write("fred_money_monthly", MONTHLY, series)
    write("fred_policy_rates_daily", DAILY, series, DAILY_FROM)


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
