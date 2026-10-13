"""Check data/snapshots/paper_money_facts.csv against the digital texts it quotes.

    python3 data/fetch/verify_quotes.py /path/to/daizhigev20

For every row whose `file` is one of the corpus texts below, the quotation must occur in that
text (whitespace ignored), and when `numeral` is given it must contain that numeral and be read
as `value` (data/fetch/classical_numerals.py).  Rows citing another source (a modern publication
such as `jackson1990`, or another edition such as `wikisource_songshi181`) are counted but not
checked here; they are described in paper_money_facts.json.
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
    "songshi": "史藏/正史/宋史.txt",
    "songchaoshishi": "史藏/政书/宋朝事实.txt",
    "yuanshi": "史藏/正史/元史.txt",
    "mingshi": "史藏/正史/明史.txt",
    "xuwenxiantongkao": "史藏/政书/钦定续文献通考.txt",
}
FACTS = HERE.parent / "snapshots" / "paper_money_facts.csv"


def main(corpus: Path) -> None:
    texts = {k: re.sub(r"\s+", "", (corpus / v).read_text(encoding="utf-8")) for k, v in FILES.items()}
    bad, checked_rows, other = [], 0, 0
    with FACTS.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["file"] not in FILES:
                other += 1
                continue
            q = re.sub(r"\s+", "", row["quote"])
            if q not in texts[row["file"]]:
                bad.append(f"{row['id']}: quotation not found in {FILES[row['file']]}")
                continue
            if row["numeral"]:
                if row["numeral"] not in q:
                    bad.append(f"{row['id']}: numeral {row['numeral']!r} is not in the quotation")
                elif float(checked(row["numeral"])) != float(row["value"]):
                    bad.append(f"{row['id']}: {row['numeral']!r} reads {checked(row['numeral'])}, value is {row['value']}")
            checked_rows += 1
    for b in bad:
        print("ERROR:", b)
    print(f"{checked_rows} quotations found in the corpus; {other} rows cite other sources.")
    if bad:
        raise SystemExit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(Path(sys.argv[1]))
