"""Extract the Yuan shi table of notes printed each year (《元史·食货志一·钞法》“岁印钞数”, 卷 93).

    python3 data/fetch/yuanshi_suyinchao.py /path/to/daizhigev20

The digital text is the daizhigev20 corpus (github.com/garychowcmu/daizhigev20, commit
4a6d6f2088825f132521d848c2ea86cf9c9a7620, file 史藏/正史/元史.txt).  The script finds the
passage that begins with 岁印钞数 and ends before 卷九十四, reads every entry
"<reign><n>年，<note>钞<numeral>锭" and writes data/snapshots/yuanshi_suyinchao.csv.

Reign periods are converted to CE years by the standard reign table below (first year of each
period).  The table gives one entry for every year from 1260 to 1329; the script stops if a year
is missing or repeated.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from classical_numerals import checked  # noqa: E402

FIRST_YEAR = {"中统": 1260, "至元": 1264, "元贞": 1295, "大德": 1297, "至大": 1308, "皇庆": 1312,
              "延祐": 1314, "至治": 1321, "泰定": 1324, "天历": 1328}
NOTES = {"中统钞": "zhongtong_ding", "至元钞": "zhiyuan_ding", "至大银钞": "zhida_ding"}
OUT = HERE.parent / "snapshots" / "yuanshi_suyinchao.csv"


def main(corpus: Path) -> None:
    text = (corpus / "史藏" / "正史" / "元史.txt").read_text(encoding="utf-8")
    start = text.index("岁印钞数：")
    end = text.index("卷九十四", start)
    passage = re.sub(r"\s+", "", text[start + len("岁印钞数："):end])
    rows, reign = [], None
    for seg in filter(None, passage.split("。")):
        m = re.match(r"(" + "|".join(FIRST_YEAR) + r")?([一二三四五六七八九十]+|元)年，(.+)$", seg)
        if not m:
            raise ValueError(f"cannot read entry {seg!r}")
        reign = m.group(1) or reign
        n = 1 if m.group(2) == "元" else checked(m.group(2))
        row = {"year": FIRST_YEAR[reign] + n - 1, "reign": reign, "reign_year": n,
               "zhongtong_ding": 0, "zhiyuan_ding": 0, "zhida_ding": 0, "source_text": seg + "。"}
        for item in m.group(3).split("，"):
            k = re.match(r"(中统钞|至元钞|至大银钞)([一二三四五六七八九十百千万]+)锭$", item)
            if not k:
                raise ValueError(f"cannot read item {item!r} in {seg!r}")
            row[NOTES[k.group(1)]] = checked(k.group(2))
        rows.append(row)
    years = [r["year"] for r in rows]
    if years != list(range(years[0], years[-1] + 1)):
        raise ValueError("years are not consecutive")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} years {years[0]}-{years[-1]} -> {OUT}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(Path(sys.argv[1]))
