"""Compile one or more chapter files in a harness where every other label resolves.

    python3 tools/check_chapter.py zh/ch12_songming.tex [zh/ch13_silver.tex ...]

Labels of the rest of the volume come from the last whole-volume build (build/main_zh.aux) or,
without it, from structure.py (chapters, parts, appendices) and the PLAN.md label registry.
Writes build/check_<stem>/check.pdf and contact sheets sheet_*.png (6 pages each), and prints
LaTeX errors, overfull boxes, undefined references and citations, missing glyphs and pages
with ink in the side margins, then the advisory readability report of tools/readability.py.
Needs pdftoppm (poppler) and Pillow for the contact sheets.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import structure as S  # noqa: E402
from build import external_labels, labels_in  # noqa: E402


def main(argv: list[str]) -> None:
    latex(argv)
    import readability
    for a in argv:
        readability.report(ROOT / a)


def latex(argv: list[str]) -> None:
    files = [Path(a) for a in argv]
    if not files:
        raise SystemExit(__doc__)
    out = ROOT / "build" / f"check_{files[0].stem}"
    out.mkdir(parents=True, exist_ok=True)
    own = labels_in([ROOT / f for f in files])
    lines = external_labels((0, "", "", ()), own)
    plan = (ROOT / "docs/PLAN.md").read_text(encoding="utf-8")
    registry = plan.split("## Label registry", 1)[1].split("```", 2)[1].split()
    known = {re.match(r"\\newlabel\{([^}]+)\}", l).group(1) for l in lines}
    for lab in registry:
        if lab not in own and lab not in known:
            lines.append(f"\\newlabel{{{lab}}}{{{{0.0}}{{}}{{{lab}}}{{}}{{}}}}")
    (out / "labels.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    m = re.match(r"ch(\d+)", files[0].stem)
    start = int(m.group(1)) - 1 if m else 0
    body = "\n".join(f"\\input{{{(ROOT / f).with_suffix('').as_posix()}}}" for f in files)
    tex = f"""\\documentclass[11pt,a4paper,oneside,openany]{{book}}
\\newif\\ifChinese
\\Chinesetrue
\\input{{preamble}}
\\input{{{(out / 'labels').as_posix()}}}
\\begin{{document}}
\\setcounter{{chapter}}{{{start}}}
{body}
\\input{{references_zh}}
\\end{{document}}
"""
    (out / "check.tex").write_text(tex, encoding="utf-8")
    for _ in range(2):
        subprocess.run(["xelatex", "-interaction=nonstopmode", f"-output-directory={out}", str(out / "check.tex")],
                       cwd=ROOT, capture_output=True, text=True)
    log = (out / "check.log").read_text(errors="replace")
    errs = [l for l in log.splitlines() if l.startswith("!")]
    over = re.findall(r"Overfull \\hbox \(([\d.]+)pt too wide\)[^\n]*lines (\d+--\d+)", log)
    undef = sorted(set(re.findall(r"Reference `([^']+)' on page", log)))
    cites = sorted(set(re.findall(r"Citation `([^']+)' on page", log)))
    missing = sorted(set(re.findall(r"Missing character: There is no (.) ", log)))
    print("PDF:", out / "check.pdf")
    print("errors:", errs[:15] or "none")
    print("overfull hboxes (>1pt):", [o for o in over if float(o[0]) > 1.0][:20] or "none")
    print("undefined references:", undef or "none")
    print("undefined citations:", cites or "none")
    print("missing glyphs:", missing or "none")
    if not (out / "check.pdf").exists():
        return
    for f in out.glob("pg-*.png"):
        f.unlink()
    subprocess.run(["pdftoppm", "-r", "55", "-png", str(out / "check.pdf"), str(out / "pg")], check=True)
    from PIL import Image
    import numpy as np
    pages = sorted(out.glob("pg-*.png"))
    for f in out.glob("sheet_*.png"):
        f.unlink()
    if not pages:
        return
    w, h = Image.open(pages[0]).size
    for s in range(0, len(pages), 6):
        sheet = Image.new("RGB", (3 * w, 2 * h), "white")
        for i, f in enumerate(pages[s:s + 6]):
            sheet.paste(Image.open(f), ((i % 3) * w, (i // 3) * h))
        sheet.save(out / f"sheet_{s // 6 + 1}.png")
    print(f"{len(pages)} pages; contact sheets:", sorted(str(p) for p in out.glob("sheet_*.png")))
    bad = []
    for k, f in enumerate(pages, 1):
        a = np.asarray(Image.open(f).convert("L"))
        hh, ww = a.shape
        mm = ww / 210.0
        rows = slice(int(22 * mm), int(272 * mm))
        if (a[rows, : int(27.5 * mm)] < 200).sum() > 3 or (a[rows, int(182.5 * mm):] < 200).sum() > 3:
            bad.append(k)
    print("pages with ink in the side margins:", bad or "none")


if __name__ == "__main__":
    main(sys.argv[1:])
