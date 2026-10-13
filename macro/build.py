"""Build Volume 1 (Chinese) as one PDF or as separate books (分册).

    python build.py                       # whole volume  -> compiled/Macroeconomics_Vol1_ZH.pdf
    python build.py --book 2              # book 2 only   -> compiled/Macroeconomics_Vol1_Book2_ZH.pdf
    python build.py --book all            # whole volume, then each of the five books
    python build.py --checks              # run checks/check_*.py and validate_source.py first
    python build.py --regenerate-figures  # redraw the figures (figsrc/build.py) first
    python build.py --epub                # also write the EPUB edition(s) (tools/epub/build_epub.py)

Everything is compiled with XeLaTeX (three passes) into build/.  Chapter numbers are
continuous across books.  A book build resolves references to chapters in other books from
the last whole-volume build (build/main_zh.aux); without it, chapter, part and appendix
numbers are taken from structure.py.  Such references print the number and title but are
not hyperlinks, because the target lives in another PDF.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import structure as S  # noqa: E402

BUILD = ROOT / "build"
OUT = ROOT / "compiled"
CN = "一二三四五六七八九十"


def cnum(k: int) -> str:
    return CN[k - 1] if k <= 10 else "十" + CN[k - 11]


def run(cmd: list[str], log: Path | None = None, env: dict[str, str] | None = None) -> None:
    if log is None:
        subprocess.run(cmd, cwd=ROOT, check=True, env=env)
        return
    with log.open("w", encoding="utf-8") as f:
        p = subprocess.run(cmd, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT, text=True, env=env)
    if p.returncode:
        tail = "\n".join(log.read_text(errors="replace").splitlines()[-40:])
        raise RuntimeError(f"Build failed; inspect {log}\n{tail}")


# ---------------------------------------------------------------------------
# Labels of material outside a book
# ---------------------------------------------------------------------------
def brace_groups(s: str, i: int, n: int) -> tuple[list[str], int]:
    """Read n consecutive {...} groups starting at s[i] == '{'."""
    out = []
    for _ in range(n):
        while i < len(s) and s[i] != "{":
            i += 1
        depth, j = 0, i
        while j < len(s):
            c = s[j]
            if c == "\\":
                j += 2
                continue
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        out.append(s[i + 1:j])
        i = j + 1
    return out, i


def labels_in(files: list[Path]) -> set[str]:
    """Labels defined in these files: \\label{...} and the label argument of \\fig / \\figH."""
    found: set[str] = set()
    for f in files:
        if f.exists():
            t = re.sub(r"(?<!\\)%.*", "", f.read_text(encoding="utf-8"))
            found |= set(re.findall(r"\\label\{([^}]+)\}", t))
            for m in re.finditer(r"\\figH?(?![A-Za-z])(\[[^\]]*\])?", t):
                groups, _ = brace_groups(t, m.end(), 3)
                found.add(groups[2].strip())
    return found


def external_labels(book: tuple, own: set[str]) -> list[str]:
    """\\newlabel lines for every label that is not defined inside this book."""
    lines: list[str] = []
    aux = BUILD / "main_zh.aux"
    if aux.exists():
        text = aux.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"\\newlabel\{([^}]+)\}", text):
            name = m.group(1)
            if name in own:
                continue
            groups, _ = brace_groups(text, m.end(), 1)
            fields = groups[0]
            n_inner = 5 if fields.startswith("{") else 0
            inner, _ = brace_groups(fields, 0, n_inner) if n_inner else ([], 0)
            if len(inner) < 3:
                continue
            num, page, title = inner[0], inner[1], inner[2]
            # anchor left empty: the target is in another PDF, so print the reference without a link
            lines.append(f"\\newlabel{{{name}}}{{{{{num}}}{{{page}}}{{{title}}}{{}}{{}}}}")
        return lines
    # fall back on structure.py
    for n, slug, zh, _en in S.CHAPTERS:
        if f"ch:{slug}" not in own:
            lines.append(f"\\newlabel{{ch:{slug}}}{{{{{n}}}{{}}{{{zh}}}{{}}{{}}}}")
    for k, key, zh, *_ in S.PARTS:
        if f"part:{key}" not in own:
            lines.append(f"\\newlabel{{part:{key}}}{{{{第{cnum(k)}部分}}{{}}{{{zh}}}{{}}{{}}}}")
    for letter, lab, zh, _en in S.APPENDICES:
        if lab not in own:
            lines.append(f"\\newlabel{{{lab}}}{{{{{letter}}}{{}}{{{zh}}}{{}}{{}}}}")
    return lines


def book_entry(b: tuple) -> str:
    n, zh, _en, parts = b
    chapters = [c for c in S.CHAPTERS if S.part_of(c[0]) in parts]
    first, last = chapters[0][0], chapters[-1][0]
    final = n == S.BOOKS[-1][0]
    files = [ROOT / "zh" / f"{S.chapter_file(c[0], c[1])}.tex" for c in chapters]
    files += [ROOT / "zh" / "front_preface.tex"]
    if final:
        files += [ROOT / "zh" / f for f in ("appendices.tex", "app_index.tex", "app_timeline.tex")]
    own = labels_in(files) | {f"part:{p[1]}" for p in S.PARTS if p[0] in parts} | {"nav:contents", "nav:compare"}
    (BUILD / f"book{n}_labels.tex").write_text("\n".join(external_labels(b, own)) + "\n", encoding="utf-8")
    body = [r"\documentclass[11pt,a4paper,oneside,openany]{book}",
            r"\newif\ifChinese", r"\Chinesetrue", r"\input{preamble}",
            f"\\input{{build/book{n}_labels}}",
            f"\\newcommand{{\\bookline}}{{第{cnum(n)}分册\\enspace·\\enspace {zh}（第 {first}—{last} 章）}}",
            f"\\hypersetup{{pdftitle={{宏观经济学 第{cnum(n)}分册：{zh}}},pdfauthor={{Prepared for Biobot}}}}",
            r"\begin{document}", r"\input{zh/front_titlepage}", r"\frontmatter", r"\pagestyle{fancy}",
            r"\inputchapter{zh/front_preface}", r"\cleardoublepage", r"\phantomsection\label{nav:contents}",
            r"\tableofcontents", r"\mainmatter", r"\input{zh/parts}",
            f"\\setcounter{{chapter}}{{{first - 1}}}"]
    for k in parts:
        body.append(f"\\partpage{{{k}}}")
        for c in chapters:
            if S.part_of(c[0]) == k:
                body.append(f"\\inputchapter{{zh/{S.chapter_file(c[0], c[1])}}}")
    if final:
        body += [r"\appendix", r"\inputchapter{zh/appendices}", r"\input{zh/app_index}", r"\inputchapter{zh/app_timeline}"]
    else:
        body += [r"\chapter*{本分册的对照与案例}\phantomsection\label{nav:compare}",
                 r"\addcontentsline{toc}{chapter}{本分册的对照与案例}",
                 r"\section*{对照}{\small\listofcomparisons}", r"\section*{案例}{\small\listofcases}"]
    body += [r"\backmatter", r"\input{references_zh}", r"\end{document}", ""]
    return "\n".join(body)


# ---------------------------------------------------------------------------
def compile_tex(stem: str, pdf_name: str) -> None:
    for ext in ["aux", "out", "toc", "cmp", "cas"]:
        (BUILD / f"{stem}.{ext}").unlink(missing_ok=True)
    for k in range(1, 4):
        run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "-output-directory=build", f"{stem}.tex"],
            BUILD / f"{stem}_pass_{k}.txt")
    log = (BUILD / f"{stem}.log").read_text(errors="replace")
    problems = [bad for bad in ["There were undefined references", "multiply defined", "Missing character:"] if bad in log]
    if problems:
        print(f"warning ({stem}): {problems}; see build/{stem}.log", file=sys.stderr)
    OUT.mkdir(exist_ok=True)
    shutil.copy2(BUILD / f"{stem}.pdf", OUT / pdf_name)
    print("Written:", OUT / pdf_name)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--book", default=None, help="1-5 for one book, 'all' for the volume and every book")
    ap.add_argument("--regenerate-figures", action="store_true")
    ap.add_argument("--checks", action="store_true")
    ap.add_argument("--epub", action="store_true", help="after the PDF(s), write the same edition(s) as EPUB 3")
    a = ap.parse_args()
    BUILD.mkdir(exist_ok=True)
    if a.checks:
        for script in sorted((ROOT / "checks").glob("check_*.py")):
            run([sys.executable, str(script)])
        run([sys.executable, "validate_source.py"])
    if a.regenerate_figures:
        env = os.environ.copy()
        env["MACRO_LANG"] = "zh"
        run([sys.executable, "figsrc/build.py"], env=env)
    if not shutil.which("xelatex"):
        raise RuntimeError("xelatex was not found; install TeX Live with XeLaTeX and xeCJK.")
    books = [b for b in S.BOOKS]
    if a.book is None or a.book == "all":
        compile_tex("main_zh", "Macroeconomics_Vol1_ZH.pdf")
    if a.book is not None:
        wanted = books if a.book == "all" else [b for b in books if str(b[0]) == a.book]
        if not wanted:
            raise RuntimeError(f"Unknown book {a.book!r}; use 1-{len(books)} or 'all'.")
        for b in wanted:
            stem = f"main_zh_book{b[0]}"
            (ROOT / f"{stem}.tex").write_text(book_entry(b), encoding="utf-8")
            try:
                compile_tex(stem, f"Macroeconomics_Vol1_Book{b[0]}_ZH.pdf")
            finally:
                (ROOT / f"{stem}.tex").unlink(missing_ok=True)
    if a.epub:
        # numbers come from build/main_zh.aux, so the whole volume must have been compiled
        aux = BUILD / "main_zh.aux"
        sources = [*ROOT.glob("zh/*.tex"), ROOT / "references_zh.tex", ROOT / "main_zh.tex"]
        if not aux.exists() or max(p.stat().st_mtime for p in sources) > aux.stat().st_mtime + 1:
            compile_tex("main_zh", "Macroeconomics_Vol1_ZH.pdf")
        run([sys.executable, "tools/epub/build_epub.py"] + (["--book", a.book] if a.book else []))


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as e:
        print(e, file=sys.stderr)
        raise SystemExit(1)
