"""Debt of Japan's general government for Chapter 1, from the BIS Data Portal (SDMX API v2), quarterly: credit to
the general government (dataset WS_TC, total credit statistics) and debt securities issued by the general government
by currency of denomination (dataset WS_NA_SEC_DSS, debt securities statistics).

    python3 data/fetch/bis_credit_gov.py          # query the API and write the two snapshots
    python3 data/fetch/bis_credit_gov.py DIR      # keep the responses in DIR (DIR/<column>.csv); those already there
                                                  # are read, not downloaded again

Series (dataset, key; the title each response must carry, column TITLE_TS of WS_TC or TITLE of WS_NA_SEC_DSS):
  data/snapshots/bis_japan_govcredit.csv, quarter and
    nominal_pct     WS_TC Q.JP.G.A.N.770.A  credit to general government from all sectors, nominal value, % of GDP
    market_pct      WS_TC Q.JP.G.A.M.770.A  the same at market value, % of GDP
    nominal_jpy_bn  WS_TC Q.JP.G.A.N.XDC.A  nominal value, billions of yen
    market_jpy_bn   WS_TC Q.JP.G.A.M.XDC.A  market value, billions of yen
    (all four "Adjusted for breaks")
  data/snapshots/bis_japan_govsec.csv, quarter and
    all_jpy_bn      WS_NA_SEC_DSS Q.N.JP.XW.S13.S1.N.L.LE.F3.T._Z.JPY._T.N.V.N._T   debt securities issued by the general
                    government, all markets, all original maturities, all currencies, nominal value, stocks, billions
                    of yen
    domestic_jpy_bn the same, key with XDC in place of _T: denominated in domestic currency
    foreign_jpy_bn  the same, key with X1: denominated in foreign currency
Prints the SHA-256 of each response. BIS terms: "The use of the statistics is unrestricted, provided that ... the
BIS must be cited ... as the source" and translations carry a note that they are not official BIS translations
(https://data.bis.org/help/legal).
"""
from __future__ import annotations

import csv
import hashlib
import io
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SNAP = HERE.parent / "snapshots"
# WS_TC is asked for in version 2.0: version 1.0 answers "No structures match query parameters"
API = "https://stats.bis.org/api/v2/data/dataflow/BIS/{flow}/{ver}/{key}?format=csv"
T = "Japan - Credit to General government from All sectors at {v} value - {u} - Adjusted for breaks"
S = "Japan - Debt sec, issued by gen govt, all markets, all original maturities, {c}, nominal value, stocks"
DSS = "Q.N.JP.XW.S13.S1.N.L.LE.F3.T._Z.JPY.{c}.N.V.N._T"
SNAPSHOTS = {
    "bis_japan_govcredit": {
        "nominal_pct": ("WS_TC", "2.0", "Q.JP.G.A.N.770.A", T.format(v="Nominal", u="Percentage of GDP"), "0"),
        "market_pct": ("WS_TC", "2.0", "Q.JP.G.A.M.770.A", T.format(v="Market", u="Percentage of GDP"), "0"),
        "nominal_jpy_bn": ("WS_TC", "2.0", "Q.JP.G.A.N.XDC.A", T.format(v="Nominal", u="domestic currency"), "9"),
        "market_jpy_bn": ("WS_TC", "2.0", "Q.JP.G.A.M.XDC.A", T.format(v="Market", u="domestic currency"), "9"),
    },
    "bis_japan_govsec": {
        "all_jpy_bn": ("WS_NA_SEC_DSS", "1.0", DSS.format(c="_T"), S.format(c="all currencies"), "9"),
        "domestic_jpy_bn": ("WS_NA_SEC_DSS", "1.0", DSS.format(c="XDC"), S.format(c="domestic currency"), "9"),
        "foreign_jpy_bn": ("WS_NA_SEC_DSS", "1.0", DSS.format(c="X1"), S.format(c="foreign currency"), "9"),
    },
}


def read(col: str, flow: str, ver: str, key: str, title: str, mult: str, folder: Path) -> dict[str, float]:
    path = folder / f"{col}.csv"
    if not path.exists():
        req = urllib.request.Request(API.format(flow=flow, ver=ver, key=key), headers={"User-Agent": "curl/8"})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    path.write_bytes(r.read())
                break
            except urllib.error.URLError:
                if attempt == 3:
                    raise
                time.sleep(2 ** (attempt + 1))
        time.sleep(1)
    raw = path.read_bytes()
    print(f"{col}: sha256 {hashlib.sha256(raw).hexdigest()}")
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
    titles = {(r.get("TITLE_TS") or r.get("TITLE") or "").strip() for r in rows}
    if titles != {title}:
        raise ValueError(f"{col}: unexpected series {titles}")
    if {r["UNIT_MULT"] for r in rows} != {mult}:                # 9: the yen columns are in billions
        raise ValueError(f"{col}: unexpected unit multiplier")
    return {r["TIME_PERIOD"]: float(r["OBS_VALUE"]) for r in rows if r["OBS_VALUE"] not in ("", "NaN")}


def main(folder: Path | None) -> None:
    folder = folder or Path(tempfile.mkdtemp(prefix="bis_"))   # downloads stay out of the repository
    for name, series in SNAPSHOTS.items():
        data = {col: read(col, *spec, folder) for col, spec in series.items()}
        quarters = sorted(set().union(*data.values()))
        with (SNAP / f"{name}.csv").open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["quarter"] + list(series))
            for q in quarters:
                w.writerow([q] + [repr(data[c][q]) if q in data[c] else "" for c in series])
        print(f"wrote {name}.csv ({len(quarters)} quarters, {quarters[0]} to {quarters[-1]})")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
