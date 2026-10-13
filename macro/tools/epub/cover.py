"""Cover image for the EPUB editions, laid out like the PDF title page (zh/front_titlepage.tex).

    MACRO_LANG=zh python3 tools/epub/cover.py OUT.png "全卷（第一至第五分册）"

The texts are read from zh/front_titlepage.tex so that the cover and the title page agree; the
second argument is the book line (\\bookline).  Fonts and colours come from figsrc/style.py.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "figsrc"))
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
from style import ACCENT, EXTERNAL, FISCAL, INK, INSTIT, MONEY, MUTED, OUTPUT, PRICE  # noqa: E402


def titlepage_texts() -> dict[str, str]:
    t = (ROOT / "zh" / "front_titlepage.tex").read_text(encoding="utf-8")

    def grab(pattern):
        m = re.search(pattern, t, re.S)
        if not m:
            raise RuntimeError(f"cover: {pattern!r} not found in zh/front_titlepage.tex")
        return re.sub(r"\\enspace", " ", m.group(1)).strip()
    return {
        "series": grab(r"\\large ([^\\]*?(?:\\enspace[^\\]*?)*)\\par\}\s*\\vspace\{9mm\}"),
        "title": grab(r"\\fontsize\{40\}\{48\}\\selectfont ([^\\]+)\\par"),
        "subtitle": grab(r"\\fontsize\{22\}\{28\}\\selectfont ([^\\]+)\\par"),
        "tagline": grab(r"\\large ([^\\]+)\\par\}\};\s*% One strip"),
        "topics": grab(r"\\sffamily\\color\{accent\} (.*?)\\par"),
        "foot_left": grab(r"\\small ([^\\]+)\\hfill"),
        "foot_right": grab(r"\\hfill ([^\\]+)\\par"),
    }


def main(out: Path, line: str) -> None:
    tx = titlepage_texts()
    W, H = 6.0, 9.0                                   # 2:3, written at 1600 x 2400 px
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 210)
    ax.set_ylim(0, 315)                               # millimetres of an A4-like page, 2:3
    ax.axis("off")
    band = 315 - 125
    ax.add_patch(Rectangle((0, band), 210, 125, fc=ACCENT, ec="none"))
    x = 22
    ax.text(x, 315 - 26, tx["series"], color="white", fontsize=13, va="top")
    ax.text(x, 315 - 46, tx["title"], color="white", fontsize=40, weight="bold", va="top")
    ax.text(x, 315 - 72, tx["subtitle"], color="white", fontsize=22, va="top")
    ax.text(x, 315 - 92, tx["tagline"], color="white", fontsize=13, va="top")
    for k, c in enumerate([OUTPUT, PRICE, MONEY, FISCAL, EXTERNAL, INSTIT]):
        ax.add_patch(Rectangle((x + k * 28, band - 8), 25, 2.2, fc=c, ec="none"))
    ax.text(x, band - 22, line, color=ACCENT, fontsize=17, va="top")
    topics = tx["topics"].replace("·", " · ").replace("  ", " ")
    ax.text(x, 52, topics, color=ACCENT, fontsize=9.5, va="bottom", wrap=True)
    ax.plot([x, 210 - x], [40, 40], color=MUTED, lw=0.6)
    ax.text(x, 33, tx["foot_left"], color=INK, fontsize=9.5, va="top")
    ax.text(210 - x, 33, tx["foot_right"], color=INK, fontsize=9.5, va="top", ha="right")
    fig.savefig(out, dpi=1600 / W, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(Path(sys.argv[1]), sys.argv[2])
