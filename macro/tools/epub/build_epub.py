"""Build EPUB 3 editions of Volume 1 from the LaTeX sources with pandoc.

    python3 tools/epub/build_epub.py               # whole volume -> compiled/Macroeconomics_Vol1_ZH.epub
    python3 tools/epub/build_epub.py --book 2      # one book     -> compiled/Macroeconomics_Vol1_Book2_ZH.epub
    python3 tools/epub/build_epub.py --book all    # whole volume and the five books
    python3 tools/epub/build_epub.py --check       # also run epubcheck (EPUBCHECK_JAR or `epubcheck` on PATH)

or `python3 build.py --epub` after the PDF build.  The method (docs/EPUB.md):

1. Numbers come from the PDF build, never recomputed here.  Chapter, section, figure, table,
   example and equation numbers are read from build/main_zh.aux (\\newlabel) and build/main_zh.toc,
   citation numbers from \\bibcite.  Run `python3 build.py` first; the script stops if a source
   file is newer than the .aux.
2. The sources are rewritten into the subset of LaTeX that pandoc's LaTeX reader understands:
   the book's macros are expanded (\\chref -> "第 12 章" with a link, \\ZE{zh}{en} -> zh, \\fig ->
   figure with a PNG), every teaching box becomes an environment that pandoc turns into a Div,
   with its title marked by \\textsc{...}, and numbered equations become a Div with the number.
3. pandoc (https://pandoc.org, GPL) writes EPUB 3 with MathML; the Lua filter boxes.lua turns
   the box Divs into styled HTML, and epub.css (generated from the colours in preamble.tex)
   gives them the same colours as the PDF.

Figures use the PNG copies made by figsrc/build.py (redrawn here if missing).
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
import structure as S  # noqa: E402
from build import brace_groups, cnum, labels_in  # noqa: E402

BUILD = ROOT / "build"
OUT = ROOT / "compiled"
WORK = BUILD / "epub"
TITLE = "宏观经济学：从古代货币到当下争论"
SUBTITLE = "以问题为线索的历史与理论"
CREATOR = "Prepared for Biobot"          # as in the PDF metadata (main_zh.tex)
SERIES = "金融学习丛书 · 第一卷"
FIGDIR = "figures_zh"

BOX_TITLES = {"intuition": "直觉", "pitfall": "常见误区", "deeper": "深入一步（初读可跳过）"}


def sanitize(label: str) -> str:
    """XHTML ids may not contain ':'; use '-' (ch:songming -> ch-songming)."""
    return re.sub(r"[^A-Za-z0-9_-]", "-", label)


# ---------------------------------------------------------------------------
# Numbers from the PDF build
# ---------------------------------------------------------------------------
class Numbers:
    def __init__(self):
        aux, toc = BUILD / "main_zh.aux", BUILD / "main_zh.toc"
        if not aux.exists() or not toc.exists():
            raise RuntimeError("build/main_zh.aux is missing: run `python3 build.py` first (the EPUB takes its numbers from it).")
        newest = max(p.stat().st_mtime for p in [*ROOT.glob("zh/*.tex"), ROOT / "references_zh.tex", ROOT / "main_zh.tex"])
        if newest > aux.stat().st_mtime + 1:
            raise RuntimeError("A source file is newer than build/main_zh.aux: run `python3 build.py` first.")
        text = aux.read_text(encoding="utf-8", errors="replace")
        self.labels: dict[str, tuple[str, str]] = {}
        for m in re.finditer(r"\\newlabel\{([^}]+)\}", text):
            groups, _ = brace_groups(text, m.end(), 1)
            if not groups[0].startswith("{"):
                continue
            inner, _ = brace_groups(groups[0], 0, 5)
            if len(inner) >= 3:
                self.labels[m.group(1)] = (inner[0], inner[2])
        self.bib = dict(re.findall(r"\\bibcite\{([^}]+)\}\{([^}]+)\}", text))
        # section numbers and titles in order, per chapter number, from the table of contents
        self.sections: dict[str, list[tuple[str, str]]] = {}
        t = toc.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"\\contentsline \{section\}", t):
            (entry,), _ = brace_groups(t, m.end(), 1)
            mm = re.match(r"\\numberline \{([^}]*)\}(.*)", entry, re.S)
            if mm:
                num = mm.group(1)
                self.sections.setdefault(num.rsplit(".", 1)[0], []).append((num, mm.group(2).strip()))

    def num(self, label: str) -> str:
        if label not in self.labels:
            print(f"warning: label {label} is not in build/main_zh.aux", file=sys.stderr)
            return "??"
        return clean_inline(self.labels[label][0])

    def title(self, label: str) -> str:
        return clean_inline(self.labels.get(label, ("", "??"))[1])


def clean_inline(s: str) -> str:
    s = re.sub(r"\\(?:relax|nobreakspace|protect)\s*", "", s)
    s = re.sub(r"\\hskip\s*[0-9.]+\s*em\s*(?:\\relax)?", "\u3000", s)
    return s.replace("{}", "").replace("~", " ").strip()


# ---------------------------------------------------------------------------
# Small LaTeX helpers (balanced groups only; nothing is evaluated)
# ---------------------------------------------------------------------------
def group_at(s: str, i: int, open_="{", close="}") -> tuple[str, int]:
    """Content of the balanced group that opens at s[i]; returns (content, index after it)."""
    assert s[i] == open_, s[i:i + 30]
    depth, j = 0, i
    while j < len(s):
        c = s[j]
        if c == "\\":
            j += 2
            continue
        if c == open_:
            depth += 1
        elif c == close:
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    raise ValueError(f"unbalanced group: {s[i:i + 60]!r}")


def skip_ws(s: str, i: int) -> int:
    while i < len(s) and s[i] in " \t\n":
        i += 1
    return i


def sub_cmd(s: str, name: str, nargs: int, fn, opt: bool = False) -> str:
    """Replace \\name[opt]{a1}...{an} by fn(opt, a1, ..., an)."""
    pat = re.compile(r"\\" + re.escape(name) + r"(?![A-Za-z@*])")
    out, pos = [], 0
    while True:
        m = pat.search(s, pos)
        if not m:
            out.append(s[pos:])
            return "".join(out)
        i, o = m.end(), None
        if opt:
            k = skip_ws(s, i)
            if k < len(s) and s[k] == "[":
                o, i = group_at(s, k, "[", "]")
        args = []
        for _ in range(nargs):
            i = skip_ws(s, i)
            a, i = group_at(s, i)
            args.append(a)
        out.append(s[pos:m.start()])
        out.append(fn(o, *args))
        pos = i


def sub_env(s: str, name: str, fn, nargs: int = 0, opt: bool = False) -> str:
    """Replace \\begin{name}[opt]{a1}..{an} body \\end{name} by fn(opt, args, body) (no nesting of the same env)."""
    begin = re.compile(r"\\begin\{" + re.escape(name) + r"\}")
    end = "\\end{" + name + "}"
    out, pos = [], 0
    while True:
        m = begin.search(s, pos)
        if not m:
            out.append(s[pos:])
            return "".join(out)
        i, o = m.end(), None
        if opt:
            k = skip_ws(s, i)
            if k < len(s) and s[k] == "[":
                o, i = group_at(s, k, "[", "]")
        args = []
        for _ in range(nargs):
            i = skip_ws(s, i)
            a, i = group_at(s, i)
            args.append(a)
        e = s.index(end, i)
        out.append(s[pos:m.start()])
        out.append(fn(o, args, s[i:e]))
        pos = e + len(end)


MATH = re.compile(r"(\$\$.*?\$\$|(?<!\\)\$.*?(?<!\\)\$|\\\[.*?\\\]|\\\(.*?\\\)"
                  r"|\\begin\{(equation|align|gather|multline|keyeq)\*?\}.*?\\end\{\2\*?\})", re.S)


def outside_math(s: str, fn) -> str:
    """Apply fn to the text between math segments."""
    parts, pos = [], 0
    for m in MATH.finditer(s):
        parts.append(fn(s[pos:m.start()]))
        parts.append(m.group(0))
        pos = m.end()
    parts.append(fn(s[pos:]))
    return "".join(parts)


def strip_comments(s: str) -> str:
    return "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in s.splitlines())


# ---------------------------------------------------------------------------
# Rewriting one source file
# ---------------------------------------------------------------------------
class Converter:
    def __init__(self, nums: Numbers, included_labels: set[str]):
        self.n = nums
        self.included = included_labels
        self.chapter = None            # current chapter number as printed ("12", "A")
        self.appendix = False
        self.compares: list[tuple[str, str, str]] = []   # (id, chapter, title)
        self.cases: list[tuple[str, str, str]] = []

    # -- references ---------------------------------------------------------
    def link(self, label: str, text: str) -> str:
        if label in self.included:
            return f"\\hyperref[{sanitize(label)}]{{{text}}}"
        return text

    def refs(self, s: str) -> str:
        N = self.n
        fmt = {"chref": "第 {} 章", "secref": "第 {} 节", "figref": "图 {}", "tabref": "表 {}",
               "exref": "例 {}", "appref": "附录 {}"}
        for cmd, f in fmt.items():
            s = sub_cmd(s, cmd, 1, lambda o, x, f=f: self.link(x, f.format(N.num(x))))
        s = sub_cmd(s, "eqref", 1, lambda o, x: self.link(x, f"({N.num(x)})"))
        s = sub_cmd(s, "nameref", 1, lambda o, x: self.link(x, N.title(x)))
        s = sub_cmd(s, "pgref", 1, lambda o, x: self.link(x, "此处"))
        s = sub_cmd(s, "ref", 1, lambda o, x: self.link(x, N.num(x)))

        def cite(o, keys):
            items = []
            for k in [k.strip() for k in keys.split(",")]:
                if k not in N.bib:
                    print(f"warning: citation {k} is not in build/main_zh.aux", file=sys.stderr)
                items.append(f"\\hyperref[bib-{sanitize(k)}]{{{N.bib.get(k, '??')}}}")
            return "[" + ", ".join(items) + (f", {o}" if o else "") + "]"
        s = sub_cmd(s, "cite", 1, cite, opt=True)
        s = re.sub(r"\\label\{([^}]+)\}", lambda m: f"\\label{{{sanitize(m.group(1))}}}", s)
        return s

    # -- headings -----------------------------------------------------------
    def headings(self, s: str) -> str:
        out, pos = [], 0
        for m in re.finditer(r"\\chapter(\*?)\s*\{", s):
            title, j = group_at(s, m.end() - 1)
            out.append(s[pos:m.start()])
            if m.group(1):
                out.append(f"\\chapter*{{{title}}}")
                self.chapter = None
            else:
                lab = re.match(r"\s*\\label\{([^}]+)\}", s[j:])
                if not lab:
                    raise RuntimeError(f"\\chapter{{{title}}} has no \\label")
                self.chapter = self.n.num(lab.group(1))
                word = f"附录 {self.chapter}" if self.appendix else f"第 {self.chapter} 章"
                out.append(f"\\chapter{{{word}\u3000{title}}}")
            pos = j
        out.append(s[pos:])
        s = "".join(out)
        # numbered sections take their numbers from the table of contents, in order
        queue = list(self.n.sections.get(self.chapter or "", []))

        def section(o, title):
            if not queue:
                raise RuntimeError(f"section {title!r} of chapter {self.chapter} is not in build/main_zh.toc; rebuild the PDF")
            num, toc_title = queue.pop(0)
            if re.sub(r"\s", "", toc_title) != re.sub(r"\s", "", title):
                raise RuntimeError(f"section {title!r} does not match {toc_title!r} in build/main_zh.toc; rebuild the PDF")
            return f"\\section{{{num}\u3000{title}}}"
        return sub_cmd(s, "section", 1, section)

    # -- teaching boxes -----------------------------------------------------
    def boxes(self, s: str) -> str:
        def titled(env, word):
            def fn(o, args, body):
                t = word + (f"：{o}" if o else "")
                return f"\\begin{{{env}}}\\textsc{{{t}}}\n\n{body}\\end{{{env}}}"
            return fn
        for env, word in BOX_TITLES.items():
            s = sub_env(s, env, titled(env, word), opt=True)

        def case(o, args, body):
            k = len(self.cases) + 1
            cid = f"case-{self.chapter}-{k}"
            self.cases.append((cid, self.chapter, args[0]))
            return f"\\begin{{case}}\\hypertarget{{{cid}}}{{}}\n\\textsc{{案例 · {args[0]}}}\n\n{body}\\end{{case}}"
        s = sub_env(s, "case", case, nargs=1)

        def example(o, args, body):
            lab = re.search(r"\\label\{([^}]+)\}", body)
            if not lab:
                raise RuntimeError(f"example {args[0]!r} has no \\label")
            body = body.replace(lab.group(0), "", 1)
            body = re.sub(r"\\solution\b", "\n\n\\\\textsc{解}\\\\ ", body)
            return (f"\\begin{{example}}\\hypertarget{{{sanitize(lab.group(1))}}}{{}}\n"
                    f"\\textsc{{例 {self.n.num(lab.group(1))}\u3000{args[0]}}}\n\n{body}\\end{{example}}")
        s = sub_env(s, "example", example, nargs=1, opt=True)

        for env in ("compare", "compare*"):
            def compare(o, args, body, env=env):
                title, a, b = args
                summary = ""
                m = re.search(r"\\cmpsum\s*\{", body)
                if m:
                    summary, j = group_at(body, m.end() - 1)
                    body = body[:m.start()] + body[j:]
                rows = sub_cmd(body, "cmprow", 3, lambda o, x, y, z: f"\\textbf{{{x}}} & {y} & {z}\\\\\n")
                cid = ""
                if env == "compare":
                    k = len(self.compares) + 1
                    cid = f"cmp-{self.chapter}-{k}"
                    self.compares.append((cid, self.chapter, title))
                anchor = f"\\hypertarget{{{cid}}}{{}}\n" if cid else ""
                out = (f"\\begin{{compare}}{anchor}\\textsc{{对照 · {title}}}\n\n"
                       f"\\begin{{tabular}}{{lll}}\n\\toprule\n & \\textbf{{{a}}} & \\textbf{{{b}}}\\\\\n\\midrule\n"
                       f"{rows.strip()}\n\\bottomrule\n\\end{{tabular}}\n")
                if summary:
                    out += f"\n\\textsc{{一句话}}\\ {summary}\n"
                return out + "\\end{compare}"
            s = sub_env(s, env, compare, nargs=3)

        def guide(o, args, body):
            body = sub_cmd(body, "guidequestion", 1,
                           lambda o, q: f"\\begin{{guideq}}\\textsc{{核心问题}}\n\n{q}\n\\end{{guideq}}\n")
            body = sub_env(body, "guidegoals", lambda o, a, b: (
                f"\\begin{{guidegoals}}\\textsc{{学完本章，你应能}}\n\\begin{{itemize}}{b}\\end{{itemize}}\n\\end{{guidegoals}}"))
            body = sub_cmd(body, "guideprereq", 1,
                           lambda o, x: f"\\begin{{guideprereq}}\\textsc{{需要用到}}\\ {x}\n\\end{{guideprereq}}\n")
            return f"\\begin{{chapterguide}}{body}\\end{{chapterguide}}"
        s = sub_env(s, "chapterguide", guide, opt=True)
        for env, word in (("takeaways", "本章要点"), ("selfcheck", "自测")):
            s = sub_env(s, env, lambda o, a, b, env=env, word=word: f"\\begin{{{env}}}\\textsc{{{word}}}\n{b}\\end{{{env}}}")
        s = sub_env(s, "answers", lambda o, a, b: (
            f"\\begin{{answers}}\\textsc{{自测提示与答案}}\n\\begin{{enumerate}}{b}\\end{{enumerate}}\n\\end{{answers}}"))
        s = re.sub(r"\\chapterstub\b", lambda m: (
            "\\begin{stub}本章正文尚待写作。写作计划见仓库中的 \\texttt{docs/PLAN.md}。\\end{stub}"), s)
        s = sub_cmd(s, "datasource", 1, lambda o, x: f"\n\\begin{{datasource}}数据来源：{x}\\end{{datasource}}\n")
        return s

    # -- figures and tables -------------------------------------------------
    def floats(self, s: str) -> str:
        def fig(o, name, cap, lab):
            return (f"\\begin{{figure}}\n\\includegraphics{{{FIGDIR}/{name}.png}}\n"
                    f"\\caption{{{cap}}}\\label{{{lab}}}\n\\end{{figure}}")   # numbered below, with the other figures
        for cmd in ("fig", "figH"):
            s = sub_cmd(s, cmd, 3, fig, opt=True)

        def numbered(word):
            def fn(o, args, body):
                lab = re.search(r"\\label\{([^}]+)\}", body)
                if lab:
                    body = sub_cmd(body, "caption", 1, lambda o2, c: f"\\caption{{{word} {self.n.num(lab.group(1))}\u3000{c}}}")
                body = re.sub(r"\\includegraphics(\[[^\]]*\])?\{([^}]+?)(\.pdf|\.png)?\}",
                              lambda m: f"\\includegraphics{{{m.group(2)}.png}}", body)
                return f"\\begin{{{'figure' if word == '图' else 'table'}}}{body}\\end{{{'figure' if word == '图' else 'table'}}}"
            return fn
        s = sub_env(s, "figure", numbered("图"), opt=True)
        s = sub_env(s, "table", numbered("表"), opt=True)

        def tabularx(o, args, body):
            spec = re.sub(r"[@<>!]\{[^{}]*(\{[^{}]*\}[^{}]*)*\}", "", args[1])
            cols = len(re.findall(r"[lcrXYpmb]", re.sub(r"\{[^{}]*\}", "", spec)))
            return f"\\begin{{tabular}}{{{'l' * cols}}}{body}\\end{{tabular}}"
        return sub_env(s, "tabularx", tabularx, nargs=2)

    # -- displayed equations ------------------------------------------------
    def equations(self, s: str) -> str:
        def eq(env, key):
            def fn(o, args, body):
                labels = re.findall(r"\\label\{([^}]+)\}", body)
                math = re.sub(r"\\(label|tag)\{[^}]*\}|\\(nonumber|notag)\b", "", body).strip()
                if env.startswith("align"):
                    math = f"\\begin{{aligned}}{math}\\end{{aligned}}"
                numbered = not env.endswith("*")
                cls = "epubkeyeq" if key else "epubequation"
                out = f"\\begin{{{cls}}}"
                if labels:
                    out += f"\\hypertarget{{{sanitize(labels[0])}}}{{}}\n"
                if numbered and labels:
                    out += "\\textsc{(" + "，".join(self.n.num(x) for x in labels) + ")}\n"
                elif numbered:
                    print(f"warning: a numbered {env} in chapter {self.chapter} has no \\label; shown without number",
                          file=sys.stderr)
                return out + f"\n\\[{math}\\]\n\\end{{{cls}}}"
            return fn
        for env in ("keyeq", "keyeq*"):
            s = sub_env(s, env, eq("equation" + env[5:], True))
        for env in ("equation", "equation*", "align", "align*"):
            s = sub_env(s, env, eq(env, False))
        return s

    # -- the whole file -----------------------------------------------------
    def convert(self, text: str) -> str:
        s = strip_comments(text)
        while "\\ZE" in s:
            s = sub_cmd(s, "ZE", 2, lambda o, zh, en: zh)
        for cmd, n in (("markboth", 2), ("addcontentsline", 3), ("Needspace", 1), ("needspace", 1),
                       ("vspace", 1), ("setlength", 2), ("thispagestyle", 1)):
            s = sub_cmd(s, cmd, n, lambda o, *a: "")
        s = re.sub(r"\\(phantomsection|chapterstart|FloatBarrier|noindent|clearpage|cleardoublepage|null"
                   r"|makeatletter|makeatother)\b", "", s)
        s = sub_cmd(s, "rule", 2, lambda o, w, h: "■", opt=True)
        s = re.sub(r"\\textcolor\{(\w+)[^}]*\}", r"\\textcolor{\1}", s)
        s = self.headings(s)
        s = self.boxes(s)
        s = self.floats(s)
        s = self.equations(s)
        s = self.refs(s)
        s = outside_math(s, lambda t: t.replace("\\qquad", "\u3000\u3000").replace("\\quad", "\u3000")
                         .replace("\\enspace", " "))
        return s


# ---------------------------------------------------------------------------
# Book assembly
# ---------------------------------------------------------------------------
def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def part_page(k: int, conv: Converter) -> str:
    text = read("zh/parts.tex")
    m = re.search(r"\\@namedef\{partpage@" + str(k) + r"\}\{\\bookpart", text)
    i = m.end()
    period = None
    if text[i] == "[":
        period, i = group_at(text, i, "[", "]")
    key, word, title, intro, chapters = brace_groups(text, i, 5)[0]
    items = [x.strip() for x in chapters.split("\\par") if x.strip()]
    body = f"\\part{{{word}\u3000{title}}}\\label{{part:{key}}}\n\\begin{{partintro}}\n"
    if period:
        body += f"\\textsc{{{period}}}\n\n"
    body += f"{intro}\n\n\\textsc{{本部分各章}}\n\\begin{{itemize}}\n" + "".join(f"\\item {x}\n" for x in items)
    body += "\\end{itemize}\n\\end{partintro}\n"
    return conv.convert(body)


def bibliography(conv: Converter) -> str:
    s = strip_comments(read("references_zh.tex"))
    s = s[s.index("\\begin{thebibliography}"):s.index("\\end{thebibliography}")]
    entries = re.split(r"\\bibitem\{([^}]+)\}", s)[1:]
    out = ["\\part*{参考文献}\\label{bibliography}\n\\begin{bibliography}"]
    for key, body in zip(entries[::2], entries[1::2]):
        out.append(f"\\hypertarget{{bib-{sanitize(key)}}}{{[{conv.n.bib.get(key, '??')}]}}\\ {body.strip()}\n")
    out.append("\\end{bibliography}")
    return conv.refs("\n".join(out))


def index_list(items: list[tuple[str, str, str]], conv: Converter) -> str:
    if not items:
        return "\\begin{stub}条目随各章写作自动出现。\\end{stub}"
    lines = [f"\\item \\hyperref[{cid}]{{第 {ch} 章\u3000{conv.convert(t)}}}" for cid, ch, t in items]
    return "\\begin{itemize}\n" + "\n".join(lines) + "\n\\end{itemize}"


def assemble(book: tuple | None, nums: Numbers) -> tuple[str, str]:
    """Return (LaTeX for pandoc, subtitle line) for the whole volume (book=None) or one book."""
    parts = [p[0] for p in S.PARTS] if book is None else list(book[3])
    final = book is None or book[0] == S.BOOKS[-1][0]
    chapters = [c for c in S.CHAPTERS if S.part_of(c[0]) in parts]
    chapter_files = [f"zh/{S.chapter_file(c[0], c[1])}.tex" for c in chapters]
    app_files = ["zh/appendices.tex", "zh/app_index.tex", "zh/app_timeline.tex"] if final else []
    files = ["zh/front_preface.tex", *chapter_files, *app_files]
    labels = labels_in([ROOT / f for f in files])
    labels |= {f"part:{p[1]}" for p in S.PARTS if p[0] in parts}
    labels |= {x for x in nums.labels if x.startswith("nav:")}
    conv = Converter(nums, labels)
    macros = [r"\newcommand{\E}{\mathbb{E}}", r"\newcommand{\R}{\mathbb{R}}", r"\newcommand{\dd}{\mathrm{d}}",
              r"\newcommand{\abs}[1]{\left|#1\right|}"]
    body = macros + [conv.convert(read("zh/front_preface.tex"))]
    for k in parts:
        body.append(part_page(k, conv))
        for c in chapters:
            if S.part_of(c[0]) == k:
                p = ROOT / "zh" / f"{S.chapter_file(c[0], c[1])}.tex"
                if p.exists():
                    body.append(conv.convert(p.read_text(encoding="utf-8")))
    if final:
        body.append("\\part*{附录}")
        conv.appendix = True
        body.append(conv.convert(read("zh/appendices.tex")))
        idx = conv.convert(read("zh/app_index.tex"))
        idx = idx.replace("\\listofcomparisons", index_list(conv.compares, conv))
        body.append(idx.replace("\\listofcases", index_list(conv.cases, conv)))
        body.append(conv.convert(read("zh/app_timeline.tex")))
    else:
        body.append("\\part*{本分册的对照与案例}\n\\section*{对照}\n" + index_list(conv.compares, conv)
                    + "\n\\section*{案例}\n" + index_list(conv.cases, conv))
    body.append(bibliography(conv))
    if book is None:
        line = "全卷（第一至第五分册）"
    else:
        first, last = chapters[0][0], chapters[-1][0]
        line = f"第{cnum(book[0])}分册 · {book[1]}（第 {first}—{last} 章）"
    return "\n\n".join(body) + "\n", line


# ---------------------------------------------------------------------------
# Styles, cover, pandoc
# ---------------------------------------------------------------------------
def colours() -> dict[str, str]:
    pre = read("preamble.tex")
    return {k: v for k, v in re.findall(r"\\definecolor\{(\w+)\}\{HTML\}\{([0-9A-Fa-f]{6})\}", pre)}


def tint(hex6: str, amount: float) -> str:
    """LaTeX xcolor `c!amount` (mixed with white), as a CSS hex colour."""
    c = [int(hex6[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(255 - amount * (255 - x)):02X}" for x in c)


def write_css(path: Path) -> None:
    c = colours()
    tpl = (HERE / "epub.css").read_text(encoding="utf-8")

    def rep(m):
        name, pct = m.group(1), m.group(2)
        return "#" + c[name] if pct is None else tint(c[name], int(pct) / 100)
    path.write_text(re.sub(r"\{\{(\w+)(?:!(\d+))?\}\}", rep, tpl), encoding="utf-8")


def make_cover(path: Path, line: str) -> None:
    env = os.environ.copy()
    env["MACRO_LANG"] = "zh"
    subprocess.run([sys.executable, str(HERE / "cover.py"), str(path), line], cwd=ROOT, env=env, check=True)


def ensure_figures(tex: str) -> None:
    pngs = set(re.findall(r"\\includegraphics\{([^}]+\.png)\}", tex))
    if any(not (ROOT / p).exists() for p in pngs):
        env = os.environ.copy()
        env["MACRO_LANG"] = "zh"
        subprocess.run([sys.executable, "figsrc/build.py"], cwd=ROOT, env=env, check=True)
    missing = [p for p in pngs if not (ROOT / p).exists()]
    if missing:
        raise RuntimeError(f"figures missing after figsrc/build.py: {missing}")


def source_date() -> str:
    try:
        return subprocess.run(["git", "log", "-1", "--format=%ct"], cwd=ROOT, capture_output=True, text=True,
                              check=True).stdout.strip() or "0"
    except (OSError, subprocess.CalledProcessError):
        return "0"


def build(book: tuple | None, nums: Numbers, check: bool) -> Path:
    tex, line = assemble(book, nums)
    stem = "Macroeconomics_Vol1_ZH" if book is None else f"Macroeconomics_Vol1_Book{book[0]}_ZH"
    WORK.mkdir(parents=True, exist_ok=True)
    src = WORK / f"{stem}.tex"
    src.write_text(tex, encoding="utf-8")
    ensure_figures(tex)
    css, cover = WORK / "epub.css", WORK / f"{stem}_cover.png"
    write_css(css)
    make_cover(cover, line)
    meta = WORK / f"{stem}.yaml"
    title = TITLE if book is None else f"{TITLE}（第{cnum(book[0])}分册）"
    meta.write_text("\n".join([
        "---", f"title: \"{title}\"", f"subtitle: \"{SUBTITLE} · {line}\"", f"creator: \"{CREATOR}\"",
        f"belongs-to-collection: \"{SERIES}\"", "lang: zh-CN", "page-progression-direction: ltr",
        f"identifier: \"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, 'github.com/610607/finance-study/macro/' + stem)}\"",
        f"rights: \"见仓库 README；数据快照的许可见各自的元数据文件\"", "---", ""]), encoding="utf-8")
    OUT.mkdir(exist_ok=True)
    epub = OUT / f"{stem}.epub"
    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = source_date()       # reproducible timestamps inside the EPUB
    cmd = ["pandoc", str(src), "-f", "latex", "-t", "epub3", "-o", str(epub), "--metadata-file", str(meta),
           "--mathml", "--toc", "--toc-depth=3", "--split-level=2", "--top-level-division=part",
           "--css", str(css), "--epub-cover-image", str(cover), "--lua-filter", str(HERE / "boxes.lua"),
           "--resource-path", str(ROOT)]
    p = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)
    # pandoc 3.1 has no Chinese translation file; its warnings about that carry no information
    noise = ("Could not load translations", "translations/zh.yaml", "has no translation defined")
    for line in p.stderr.splitlines():
        if not any(n in line for n in noise):
            print(line, file=sys.stderr)
    if p.returncode:
        raise RuntimeError(f"pandoc failed with exit code {p.returncode}")
    print("Written:", epub)
    if check:
        epubcheck(epub)
    return epub


def epubcheck(epub: Path) -> None:
    jar = os.environ.get("EPUBCHECK_JAR")
    if jar:
        cmd = ["java", "-jar", jar, str(epub)]
    elif shutil.which("epubcheck"):
        cmd = ["epubcheck", str(epub)]
    else:
        print("epubcheck not found (set EPUBCHECK_JAR or put epubcheck on PATH); skipped", file=sys.stderr)
        return
    subprocess.run(cmd, check=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--book", default=None, help="1-5 for one book, 'all' for the volume and every book")
    ap.add_argument("--check", action="store_true", help="run epubcheck on the result")
    a = ap.parse_args()
    if not shutil.which("pandoc"):
        raise RuntimeError("pandoc was not found; install pandoc 3.1 or newer (https://pandoc.org/installing.html).")
    nums = Numbers()
    if a.book is None or a.book == "all":
        build(None, nums, a.check)
    if a.book is not None:
        wanted = S.BOOKS if a.book == "all" else [b for b in S.BOOKS if str(b[0]) == a.book]
        if not wanted:
            raise RuntimeError(f"Unknown book {a.book!r}; use 1-{len(S.BOOKS)} or 'all'.")
        for b in wanted:
            build(b, nums, a.check)


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError, subprocess.CalledProcessError) as e:
        print(e, file=sys.stderr)
        raise SystemExit(1)
