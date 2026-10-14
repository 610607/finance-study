"""The balance sheet of the People's Bank of China (货币当局资产负债表), monthly, from the PBoC's statistics pages.

    python3 data/fetch/pbc_balance_sheet.py            # download the yearly tables and write the snapshot
    python3 data/fetch/pbc_balance_sheet.py DIR        # use copies kept in DIR (named YYYY.htm)

The PBoC publishes one table per year under 调查统计司 → 统计数据 → YYYY年统计数据 → 货币统计概览 →
货币当局资产负债表 (an HTML table, 亿元, end of month). The script follows those links from
https://www.pbc.gov.cn/diaochatongjisi/116219/116319/index.html, reads each table, keeps the lines listed in ITEMS
and writes data/snapshots/pbc_balance_sheet.csv (one row per month, one column per line, 亿元). Before 2002 the
lines had other names, so the snapshot starts in 2002. The SHA-256 of every downloaded table is printed; the
values of the 2026-10-14 download are in the snapshot's .json. Later tables can revise the latest months.
"""
from __future__ import annotations

import csv
import hashlib
import re
import sys
import tempfile
import time
import urllib.error
import urllib.request
from io import StringIO
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "snapshots" / "pbc_balance_sheet.csv"
SITE = "https://www.pbc.gov.cn"
INDEX = SITE + "/diaochatongjisi/116219/116319/index.html"
FIRST = 2002
# snapshot column: the names of the line as printed (prefix match, spaces removed); the values of several names
# are added. The names changed in 2006 (对存款货币银行债权 and 对特定存款机构债权 became 对其他存款性公司债权; the
# deposits of 存款货币银行 and 特定存款机构 became those of 其他存款性公司) and the lines below them in 2011.
ITEMS = {
    "foreign_assets": ["国外资产"],
    "fx": ["外汇"],
    "gold": ["货币黄金"],
    "claims_gov": ["对政府债权"],
    "claims_banks": ["对其他存款性公司债权", "对存款货币银行债权", "对特定存款机构债权"],
    "claims_ofc": ["对其他金融"],
    "claims_nonfin": ["对非金融"],
    "other_assets": ["其他资产"],
    "total_assets": ["总资产"],
    "reserve_money": ["储备货币"],
    "currency": ["货币发行"],
    "bank_deposits": ["其他存款性公司", "存款货币银行", "特定存款机构"],
    "nonfin_deposits": ["非金融"],
    "fc_deposits_excl": ["不计入储备货币的金融性公司存款"],
    "bonds": ["发行债券"],
    "foreign_liab": ["国外负债"],
    "gov_deposits": ["政府存款"],
    "own_capital": ["自有资金"],
    "other_liab": ["其他负债"],
    "total_liab": ["总负债"],
}


def fetch(url: str, tries: int = 4) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"})
    for k in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            time.sleep(1)                                    # be gentle with the site
            return data
        except urllib.error.HTTPError:                       # the site now and then answers 404 to a valid link
            if k == tries - 1:
                raise
            time.sleep(2 ** (k + 1))
    raise AssertionError


def page(url: str) -> str:
    return fetch(url).decode("utf-8", "replace")


def absolute(href: str) -> str:
    url = href if href.startswith("http") else SITE + href
    return url.replace("http://", "https://", 1)             # the site redirects http to https


def find_table(t: str) -> str | None:
    """The .htm link of 货币当局资产负债表 on a page: an anchor named so, or the first .htm link in its table row."""
    for m in re.finditer(r'''<a\b([^>]*)>(.*?)</a>''', t, re.S):
        href = re.search(r'''href=["']([^"']+\.htm)["']''', m.group(1))
        if href and ("货币当局资产负债表" in re.sub(r"<[^>]+>", "", m.group(2))
                     or re.search(r'''title=["']货币当局资产负债表["']''', m.group(1))):
            return href.group(1)
    at = t.find("货币当局资产负债表")
    if at < 0:
        return None
    m = re.search(r'''href=["']([^"']+\.htm)["']''', t[t.rfind("<tr", 0, at):])
    return m.group(1) if m else None


def table_urls() -> dict[int, str]:
    """Year → URL of that year's 货币当局资产负债表 (HTML)."""
    t = page(INDEX)
    years = {}
    for m in re.finditer(r'''href=["'](/diaochatongjisi/116219/116319/[0-9a-z]+/index\.html)["']''', t):
        y = re.search(r"(\d{4})年统计数据", t[m.end():m.end() + 400])
        if y and int(y.group(1)) >= FIRST:
            years.setdefault(int(y.group(1)), absolute(m.group(1)))
    out = {}
    for y, url in sorted(years.items()):
        t = page(url)
        link = find_table(t)                                  # until about 2009 the year page lists the tables
        if not link:
            sub = re.search(r'''href=["']([^"']+)["'][^>]*>(?:\s|<[^>]+>)*货币统计概览''', t)
            if not sub:
                raise ValueError(f"{y}: no 货币统计概览 link on {url}")
            link = find_table(page(absolute(sub.group(1))))
        if not link:
            raise ValueError(f"{y}: no balance-sheet table found from {url}")
        out[y] = absolute(link)
    return out


def read_table(raw: bytes) -> dict[str, dict[str, float]]:
    """Month (YYYY-MM) → {column: value in 亿元} for one yearly table."""
    try:
        text = raw.decode("utf-8-sig")                       # some years are UTF-8, the others GB18030
    except UnicodeDecodeError:
        text = raw.decode("gb18030")
    d = pd.read_html(StringIO(text))[0]
    head = next(i for i in range(len(d)) if re.fullmatch(r"\d{4}\.\d{2}", str(d.iloc[i, 1]).strip()))  # the months
    months = {j: str(d.iloc[head, j]).strip() for j in range(1, d.shape[1])
              if re.fullmatch(r"\d{4}\.\d{2}", str(d.iloc[head, j]).strip())}
    labels = [re.sub(r"\s+", "", str(x)) for x in d.iloc[:, 0]]
    out: dict[str, dict[str, float]] = {m.replace(".", "-"): {} for m in months.values()}
    for col, names in ITEMS.items():
        rows = [next((i for i in range(head + 1, len(d)) if labels[i].startswith(n)), None) for n in names]
        rows = [i for i in rows if i is not None]
        for j, mo in months.items():
            vals = [str(d.iloc[i, j]).replace(",", "").strip() for i in rows]
            vals = [float(v) for v in vals if re.fullmatch(r"-?\d+(\.\d+)?", v)]
            if vals:
                out[mo.replace(".", "-")][col] = sum(vals)
    return {m: v for m, v in out.items() if v}


def main(folder: Path | None) -> None:
    if folder is None:
        folder = Path(tempfile.mkdtemp(prefix="pbc_"))       # downloads stay out of the repository
        for y, url in table_urls().items():
            (folder / f"{y}.htm").write_bytes(fetch(url))
            print(f"{y}: {url}")
    data: dict[str, dict[str, float]] = {}
    for f in sorted(folder.glob("*.htm")):
        raw = f.read_bytes()
        print(f"{f.name}: sha256 {hashlib.sha256(raw).hexdigest()}")
        data.update(read_table(raw))
    months = sorted(data)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["month"] + list(ITEMS))
        for m in months:
            w.writerow([m] + [("%.2f" % data[m][c]) if c in data[m] else "" for c in ITEMS])
    print(f"wrote {OUT} ({len(months)} months, {months[0]} to {months[-1]})")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
