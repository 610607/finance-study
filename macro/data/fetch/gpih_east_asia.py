"""Rice prices in Osaka and Edo, 1680-1867, and copper-cash wages and the cash price of silver near Beijing,
1807-1902, from the Global Price and Income History Group (GPIH, UC Davis).

    python3 data/fetch/gpih_east_asia.py          # download both files and write the two snapshots
    python3 data/fetch/gpih_east_asia.py DIR      # use copies already in DIR

1. "Japan_rice_P_1620-1867.xls" (from M. Iwahashi, Kinsei Nihon bukkashi no kenkyu, 1981, Appendix
   Table 1, pp. 460-465; notes by O. Saito, 2008), sheet "koku of rice": the price of one koku of rice
   in silver monme at Osaka (column 1, the Dojima market, rice of Higo) and in gold ryo in Edo (column 9,
   a price set by the bakufu). The script checks the headings and writes the years in which either
   series has a value to data/snapshots/gpih_iwahashi_rice.csv.
2. "China_wages_1807-1925.xls" (D. Ma, from S. D. Gamble, "Daily wages of unskilled Chinese laborers,
   1807-1902", Far Eastern Quarterly 3(1), 1943), sheet "Wages Beijing rural": the daily wage in copper
   cash (doubled by the compilers to allow for food; Allen et al. 2011, Appendix II), the price of one
   tael of silver in copper cash, and the wage in taels and in grams of silver. The script writes all
   rows to data/snapshots/gpih_gamble_beijing.csv.

The SHA-256 of each file is printed so that it can be compared with the one recorded in the .json.
Both files are .xls and need the xlrd package (pip install xlrd).
"""
from __future__ import annotations

import csv
import hashlib
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SNAP = HERE.parent / "snapshots"
BASE = "https://gpih.ucdavis.edu/files/"
RICE = "Japan_rice_P_1620-1867.xls"
WAGES = "China_wages_1807-1925.xls"
UA = "Mozilla/5.0 (X11; Linux x86_64) finance-study data fetch"


def fetch(name: str, dest: Path) -> Path:
    path = dest / name
    if not path.exists():
        req = urllib.request.Request(BASE + name, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=120) as r:
            path.write_bytes(r.read())
    print(f"{path.name}: sha256 {hashlib.sha256(path.read_bytes()).hexdigest()}")
    return path


def num(v):
    return v if isinstance(v, float) else None


def rice(path: Path) -> None:
    import xlrd
    sh = xlrd.open_workbook(str(path)).sheet_by_name("koku of rice")
    kind = [str(sh.cell_value(6, j)).strip() for j in range(sh.ncols)]
    head = [str(sh.cell_value(7, j)).strip() for j in range(sh.ncols)]
    unit = str(sh.cell_value(5, 1)), str(sh.cell_value(5, 9))
    if not (head[1] == "Osaka" and kind[1] == "Market" and head[9] == "Edo" and kind[9] == "Bakufu gov't"
            and unit[0].startswith("Price in Monme") and unit[1].startswith("Price in Ryo")):
        raise ValueError(f"{path.name}: unexpected headings {head} {kind} {unit}")
    out = SNAP / "gpih_iwahashi_rice.csv"
    n = 0
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "osaka_monme_per_koku", "edo_ryo_per_koku"])
        for i in range(8, sh.nrows):
            y = sh.cell_value(i, 0)
            if not isinstance(y, float):
                continue
            osaka, edo = num(sh.cell_value(i, 1)), num(sh.cell_value(i, 9))
            if osaka is None and edo is None:
                continue
            w.writerow([int(y), "" if osaka is None else round(osaka, 4), "" if edo is None else round(edo, 4)])
            n += 1
    print(f"{n} years -> {out}")


def wages(path: Path) -> None:
    import xlrd
    sh = xlrd.open_workbook(str(path)).sheet_by_name("Wages Beijing rural ")
    head = [str(sh.cell_value(3, j)).strip() for j in range(sh.ncols)]
    if not (head[1].startswith("Wages in copper cash") and head[2].startswith("Copper/ silver conversion")
            and head[3] == "Wages in silver tael per day" and head[4] == "Wages in grams of silver"
            and "Gamble" in str(sh.cell_value(72, 0))):
        raise ValueError(f"{path.name}: unexpected headings {head}")
    out = SNAP / "gpih_gamble_beijing.csv"
    n = 0
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "wage_cash_per_day", "cash_per_tael", "wage_tael_per_day", "wage_grams_silver"])
        for i in range(4, sh.nrows):
            y = sh.cell_value(i, 0)
            if not isinstance(y, float):
                continue
            vals = [num(sh.cell_value(i, j)) for j in range(1, 5)]
            w.writerow([int(y)] + ["" if v is None else round(v, 4) for v in vals])
            n += 1
    print(f"{n} years -> {out}")


def main(dest: Path) -> None:
    rice(fetch(RICE, dest))
    wages(fetch(WAGES, dest))


if __name__ == "__main__":
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / ".cache" / "finance-study" / "gpih"
    folder.mkdir(parents=True, exist_ok=True)
    main(folder)
