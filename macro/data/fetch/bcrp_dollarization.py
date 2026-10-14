"""Dollarization of money and inflation in Peru, monthly, from the Banco Central de Reserva del Perú (BCRPData API).

    python3 data/fetch/bcrp_dollarization.py         # query the API and write the snapshot
    python3 data/fetch/bcrp_dollarization.py DIR     # use saved API responses (DIR/PN00025MM.json, DIR/PN01273PM.json)

Two series:
  PN00025MM  "Liquidez de las sociedades creadoras de depósito (fin de periodo) - Coeficiente de Dolarización de la
             Liquidez (%)": the share of the broad money of Peru's depository corporations held in foreign currency,
             end of month, January 1992 onward
  PN01273PM  "Índice de precios Lima Metropolitana (var% 12 meses) - IPC": consumer prices in Lima, change over twelve
             months, January 1985 onward
The script writes data/snapshots/bcrp_dollarization.csv (month, dollarization_pct, cpi_12m_pct; a cell is empty
before its series starts) and prints the SHA-256 of each response. BCRPData's terms of use allow reproduction
"siempre y cuando se cite la fuente" (https://estadisticas.bcrp.gob.pe/estadisticas/series/ayuda/condiciones-de-uso).
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import tempfile
import time
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "snapshots" / "bcrp_dollarization.csv"
API = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api/{code}/json/{start}/2026-12/ing"
SERIES = {   # column: (code, first month queried, the series name the API must return)
    "dollarization_pct": ("PN00025MM", "1992-1", "Liquidez de las sociedades creadoras de depósito (fin de periodo) - "
                          "Coeficiente de Dolarización de la Liquidez (%)"),
    "cpi_12m_pct": ("PN01273PM", "1985-1", "Índice de precios Lima Metropolitana (var% 12 meses) - IPC"),
}


def read(code: str, start: str, title: str, folder: Path | None) -> dict[str, float]:
    if folder is None:
        folder = Path(tempfile.mkdtemp(prefix="bcrp_"))     # downloads stay out of the repository
        req = urllib.request.Request(API.format(code=code, start=start),
                                     headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"})
        with urllib.request.urlopen(req, timeout=120) as r:
            (folder / f"{code}.json").write_bytes(r.read())
        time.sleep(1)
    raw = (folder / f"{code}.json").read_bytes()
    print(f"{code}: sha256 {hashlib.sha256(raw).hexdigest()}")
    d = json.loads(raw)
    if d["config"]["series"][0]["name"] != title:
        raise ValueError(f"{code}: unexpected series {d['config']['series'][0]['name']}")
    return {datetime.strptime(p["name"], "%b.%Y").strftime("%Y-%m"): float(p["values"][0])
            for p in d["periods"] if p["values"][0] not in ("n.d.", "")}


def main(folder: Path | None) -> None:
    data = {col: read(*spec, folder) for col, spec in SERIES.items()}
    months = sorted(set().union(*data.values()))
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["month"] + list(SERIES))
        for m in months:
            w.writerow([m] + [("%.2f" % data[c][m]) if m in data[c] else "" for c in SERIES])
    print(f"wrote {OUT} ({len(months)} months, {months[0]} to {months[-1]})")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
