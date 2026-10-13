"""Check quotation snapshots against the digital texts they quote.

    python3 data/fetch/verify_quotes.py /path/to/daizhigev20                 # every quotation snapshot
    python3 data/fetch/verify_quotes.py /path/to/daizhigev20 data/snapshots/x.csv [...]

A quotation snapshot is a CSV in data/snapshots/ with the columns id, value, numeral, file, quote
(see paper_money_facts.csv, Chapter 12).  For every row whose `file` names a text of the classical
corpus — a key of FILES below, or a corpus path such as 史藏/正史/清史稿.txt — the quotation must occur
in that text (whitespace ignored), and when `numeral` is given it must contain that numeral and be
read as `value` (data/fetch/classical_numerals.py).  Rows citing another source (a modern
publication such as `jackson1990`, or another edition such as `wikisource_songshi181`) are counted
but not checked here; their snapshot's .json says how they were verified.

The corpus is daizhigev20 (https://github.com/garychowcmu/daizhigev20), pinned at commit
4a6d6f2088825f132521d848c2ea86cf9c9a7620; a sparse checkout of 史藏/正史, 史藏/政书 and
史藏/经世文编 is enough.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from classical_numerals import checked  # noqa: E402

FILES = {
    "shiji": "史藏/正史/史记.txt",
    "hanshu": "史藏/正史/汉书.txt",
    "houhanshu": "史藏/正史/后汉书.txt",
    "jiutangshu": "史藏/正史/旧唐书.txt",
    "xintangshu": "史藏/正史/新唐书.txt",
    "songshi": "史藏/正史/宋史.txt",
    "yuanshi": "史藏/正史/元史.txt",
    "mingshi": "史藏/正史/明史.txt",
    "qingshigao": "史藏/正史/清史稿.txt",
    "songchaoshishi": "史藏/政书/宋朝事实.txt",
    "songhuiyao": "史藏/政书/宋会要辑稿.txt",
    "wenxiantongkao": "史藏/政书/文献通考.txt",
    "xuwenxiantongkao": "史藏/政书/钦定续文献通考.txt",
    "daminghuidian": "史藏/政书/大明会典.txt",
    "huangchaojingshiwenbian": "史藏/经世文编/皇朝经世文编.txt",
    "huangchaojingshiwenxubian": "史藏/经世文编/皇朝经世文续编.txt",
    "huangchaojingshiwenxubian_ge": "史藏/经世文编/皇朝经世文续编-清-葛士浚.txt",
    "huangmingjingshiwenbian": "史藏/经世文编/皇明经世文编.txt",
}
SNAPSHOTS = HERE.parent / "snapshots"


def corpus_path(key: str) -> str | None:
    if key in FILES:
        return FILES[key]
    if key.startswith("史藏/"):
        return key
    return None


def quotation_snapshots() -> list[Path]:
    out = []
    for f in sorted(SNAPSHOTS.glob("*.csv")):
        with f.open(encoding="utf-8") as fh:
            header = next(csv.reader(fh), [])
        if {"id", "file", "quote", "numeral", "value"} <= set(header):
            out.append(f)
    return out


def main(corpus: Path, snapshots: list[Path]) -> None:
    texts: dict[str, str] = {}
    bad, checked_rows, other = [], 0, 0
    for snap in snapshots:
        with snap.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rel = corpus_path(row["file"])
                if rel is None:
                    other += 1
                    continue
                if rel not in texts:
                    p = corpus / rel
                    if not p.exists():
                        bad.append(f"{snap.name}:{row['id']}: corpus file {rel} is missing (extend the sparse checkout)")
                        continue
                    texts[rel] = re.sub(r"\s+", "", p.read_text(encoding="utf-8"))
                q = re.sub(r"\s+", "", row["quote"])
                if q not in texts[rel]:
                    bad.append(f"{snap.name}:{row['id']}: quotation not found in {rel}")
                    continue
                if row["numeral"]:
                    if row["numeral"] not in q:
                        bad.append(f"{snap.name}:{row['id']}: numeral {row['numeral']!r} is not in the quotation")
                    elif float(checked(row["numeral"])) != float(row["value"]):
                        bad.append(f"{snap.name}:{row['id']}: {row['numeral']!r} reads {checked(row['numeral'])}, "
                                   f"value is {row['value']}")
                checked_rows += 1
    for b in bad:
        print("ERROR:", b)
    names = ", ".join(s.name for s in snapshots)
    print(f"{checked_rows} quotations found in the corpus; {other} rows cite other sources ({names}).")
    if bad:
        raise SystemExit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    paths = [Path(p) for p in sys.argv[2:]] or quotation_snapshots()
    main(Path(sys.argv[1]), paths)
