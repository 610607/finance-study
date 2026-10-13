"""Check that the sources of Volume 1 are consistent.

Structure (always):
  * structure.py: chapters numbered 1..N without gaps, unique slugs, parts covering the
    chapters in order, books covering the parts in order;
  * every chapter file zh/chNN_slug.tex exists, has exactly one \\chapter, whose title equals
    the Chinese title in structure.py and which carries \\label{ch:slug};
  * main_zh.tex inputs the part pages and chapters in the order of structure.py;
  * zh/parts.tex defines every part page with the right key;
  * labels are unique; every reference target is defined (or is fig:<existing figure>);
    every \\cite key has a \\bibitem; every figure file exists;
  * every data snapshot in data/snapshots/ has a metadata file with the required fields;
  * every checks/check_chNN.py belongs to an existing chapter.
Bilingual (when en/ has chapter files): for every en/X.tex the pair zh/X.tex, en/X.tex must have
the same labels, citations, reference targets, figure calls, teaching-box sequence and
displayed mathematics (the same rules as in 610607/electromagnetics-study).

    python validate_source.py          # exit status 1 on any error
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import structure as S  # noqa: E402

DISPLAY = ["equation", "equation*", "align", "align*", "gather", "gather*", "multline", "multline*",
           "keyeq", "keyeq*"]
BOXES = ["chapterguide", "guidegoals", "intuition", "example", "compare", "compare*", "case", "pitfall", "deeper",
         "takeaways", "selfcheck", "answers", "table", "figure"]
REFCMDS = ["ref", "eqref", "chref", "secref", "figref", "tabref", "exref", "appref", "pgref", "nameref",
           "pageref", "autoref"]
TEXTCMDS = ["text", "textup", "textrm", "textsf", "textit", "mbox", "mathrm", "operatorname", "ZE", "intertext",
            "shortintertext", "tag"]
SNAPSHOT_FIELDS = ["title", "source", "url", "series", "retrieved", "license", "used_in"]


def strip_comments(s: str) -> str:
    return re.sub(r"(?<!\\)%.*", "", s)


def brace_arg(s: str, i: int) -> tuple[str, int]:
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
                return s[i + 1:j], j + 1
        j += 1
    return s[i + 1:], len(s)


def args_of(text: str, cmds: list[str]) -> list[str]:
    pat = re.compile(r"\\(" + "|".join(cmds) + r")\*?(?:\[[^\]]*\])?\{([^}]*)\}")
    return [m.group(2) for m in pat.finditer(text)]


def cites(text: str) -> list[str]:
    out = []
    for a in re.findall(r"\\cite[a-z]*\*?(?:\[[^\]]*\])*\{([^}]*)\}", text):
        out += [k.strip() for k in a.split(",") if k.strip()]
    return out


def figures(text: str) -> list[str]:
    calls = re.findall(r"\\fig(?:H)?\*?(?:\[[^\]]*\])?\{([^}]+)\}", text)
    calls += [Path(p).stem for p in re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", text)
              if "\\figdir" not in p]
    return calls


def env_sequence(text: str, names: list[str]) -> list[str]:
    pat = re.compile(r"\\begin\{(" + "|".join(re.escape(n) for n in names) + r")\}")
    return [m.group(1) for m in pat.finditer(text)]


def drop_text(s: str) -> str:
    out, i = [], 0
    pat = re.compile(r"\\(" + "|".join(TEXTCMDS) + r")\b\s*")
    while True:
        m = pat.search(s, i)
        if not m:
            out.append(s[i:])
            break
        out.append(s[i:m.start()])
        j, n = m.end(), 0
        while j < len(s) and s[j] == "{" and n < 2:
            _, j = brace_arg(s, j)
            n += 1
            while j < len(s) and s[j] in " \t":
                j += 1
        out.append("T")
        i = j
    return "".join(out)


def normalize_math(s: str) -> str:
    s = drop_text(s)
    s = re.sub(r"\\label\{[^}]*\}", "", s)
    s = re.sub(r"\\(nonumber|notag)\b", "", s)
    s = re.sub(r"[\u3000-\u303f\uff00-\uffef\u4e00-\u9fff]+", "T", s)
    s = re.sub(r"\\[,;:! ]|~", "", s)
    s = re.sub(r"\\(quad|qquad)\b", "", s)
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"[.,;]+(?=(\\\\|&|$))", "", s)
    return re.sub(r"[.,;]+$", "", s)


def display_blocks(text: str) -> list[tuple[str, str]]:
    pat = re.compile(r"\\begin\{(" + "|".join(re.escape(n) for n in DISPLAY) + r")\}(?:\[[^\]]*\])?([\s\S]*?)\\end\{\1\}")
    return [(m.group(1), m.group(2)) for m in pat.finditer(text)]


def compare_pair(zh: Path, en: Path) -> list[str]:
    errors = []
    a, b = strip_comments(zh.read_text(encoding="utf-8")), strip_comments(en.read_text(encoding="utf-8"))
    name = zh.name
    la, lb = Counter(args_of(a, ["label"])), Counter(args_of(b, ["label"]))
    if la != lb:
        errors.append(f"{name}: labels differ; zh only {sorted((la - lb).elements())}, en only {sorted((lb - la).elements())}")
    if set(cites(a)) != set(cites(b)):
        errors.append(f"{name}: citations differ")
    if set(args_of(a, REFCMDS)) != set(args_of(b, REFCMDS)):
        errors.append(f"{name}: reference targets differ")
    if figures(a) != figures(b):
        errors.append(f"{name}: figure calls differ")
    if env_sequence(a, BOXES) != env_sequence(b, BOXES):
        errors.append(f"{name}: teaching-box sequence differs")
    da, db = display_blocks(a), display_blocks(b)
    if len(da) != len(db):
        errors.append(f"{name}: {len(da)} displayed equations in zh but {len(db)} in en")
    for k, ((ea, xa), (eb, xb)) in enumerate(zip(da, db), 1):
        if ea != eb or normalize_math(xa) != normalize_math(xb):
            errors.append(f"{name}: displayed block {k} differs ({ea} vs {eb})")
    return errors


# ---------------------------------------------------------------------------
def check_structure(errors: list[str]) -> None:
    nums = [c[0] for c in S.CHAPTERS]
    if nums != list(range(1, len(nums) + 1)):
        errors.append("structure.py: chapter numbers are not 1..N in order")
    slugs = [c[1] for c in S.CHAPTERS]
    for s, k in Counter(slugs).items():
        if k > 1:
            errors.append(f"structure.py: slug {s!r} used {k} times")
    for s in slugs:
        if not re.fullmatch(r"[a-z][a-z0-9]*", s):
            errors.append(f"structure.py: slug {s!r} must be lowercase letters and digits")
    expect = 1
    for k, key, _zh, _en, _period, first, last in S.PARTS:
        if first != expect or last < first:
            errors.append(f"structure.py: part {k} ({key}) covers {first}-{last}, expected to start at {expect}")
        expect = last + 1
    if expect != len(nums) + 1:
        errors.append("structure.py: parts do not cover every chapter")
    covered = [p for b in S.BOOKS for p in b[3]]
    if covered != [p[0] for p in S.PARTS]:
        errors.append(f"structure.py: books cover parts {covered}, expected every part once in order")


def check_chapters(errors: list[str], warnings: list[str]) -> int:
    stubs = 0
    expected = {f"{S.chapter_file(n, slug)}.tex" for n, slug, *_ in S.CHAPTERS}
    for f in sorted((ROOT / "zh").glob("ch*.tex")):
        if f.name not in expected:
            errors.append(f"zh/{f.name} is not listed in structure.py")
    for n, slug, zh, _en in S.CHAPTERS:
        f = ROOT / "zh" / f"{S.chapter_file(n, slug)}.tex"
        if not f.exists():
            errors.append(f"missing chapter file zh/{f.name}")
            continue
        t = strip_comments(f.read_text(encoding="utf-8"))
        heads = re.findall(r"\\chapter\{", t)
        if len(heads) != 1:
            errors.append(f"zh/{f.name}: expected one \\chapter, found {len(heads)}")
            continue
        title, j = brace_arg(t, t.index("\\chapter{") + len("\\chapter"))
        if title.strip() != zh:
            errors.append(f"zh/{f.name}: title {title.strip()!r} differs from structure.py {zh!r}")
        if not re.match(r"\s*\\label\{ch:" + re.escape(slug) + r"\}", t[j:]):
            errors.append(f"zh/{f.name}: \\chapter must be followed by \\label{{ch:{slug}}}")
        if "\\chapterstub" in t:
            stubs += 1
    return stubs


def check_main(errors: list[str]) -> None:
    t = strip_comments((ROOT / "main_zh.tex").read_text(encoding="utf-8"))
    seq = re.findall(r"\\(partpage|inputchapter)\{([^}]+)\}", t)
    got = [(a, b) for a, b in seq if a == "partpage" or b.startswith("zh/ch")]
    want = []
    for k, *_rest in S.PARTS:
        first, last = _rest[4], _rest[5]
        want.append(("partpage", str(k)))
        want += [("inputchapter", f"zh/{S.chapter_file(n, slug)}") for n, slug, *_ in S.CHAPTERS if first <= n <= last]
    if got != want:
        errors.append("main_zh.tex: part pages and chapters are not in the order of structure.py")
    for need in ["zh/appendices", "zh/app_index", "zh/app_timeline", "references_zh"]:
        if need not in t:
            errors.append(f"main_zh.tex does not input {need}")
    p = strip_comments((ROOT / "zh" / "parts.tex").read_text(encoding="utf-8"))
    defs = re.findall(r"\\@namedef\{partpage@(\d+)\}\{\\bookpart(?:\[[^\]]*\])?\{([^}]+)\}", p)
    if [(int(a), b) for a, b in defs] != [(k, key) for k, key, *_ in S.PARTS]:
        errors.append(f"zh/parts.tex: part pages {defs} do not match structure.py")


def check_labels_refs(errors: list[str], warnings: list[str]) -> None:
    files = sorted((ROOT / "zh").glob("*.tex"))
    defined: Counter = Counter()
    texts = {}
    for f in files:
        t = strip_comments(f.read_text(encoding="utf-8"))
        texts[f] = t
        defined.update(args_of(t, ["label"]))
    defined.update(f"part:{key}" for _k, key, *_ in S.PARTS)
    for lab, k in defined.items():
        if k > 1:
            errors.append(f"label {lab!r} is defined {k} times")
    figs = {p.stem for p in (ROOT / "figures_zh").glob("*.pdf")} if (ROOT / "figures_zh").exists() else set()
    bib = (ROOT / "references_zh.tex").read_text(encoding="utf-8")
    keys = set(re.findall(r"\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}", bib))
    plan = (ROOT / "docs" / "PLAN.md").read_text(encoding="utf-8")
    registry = set(plan.split("## Label registry", 1)[1].split("```")[1].split()) if "## Label registry" in plan else set()
    for f, t in texts.items():
        own = set(args_of(t, ["label"]))
        for r in args_of(t, REFCMDS):
            if r in defined or (r.startswith("fig:") and r[4:] in figs):
                if r not in own and r not in registry and not r.startswith("fig:") and f.name.startswith("ch"):
                    warnings.append(f"zh/{f.name}: refers to {r!r}, which is not in the PLAN.md label registry")
                continue
            errors.append(f"zh/{f.name}: reference to undefined label {r!r}")
        for c in cites(t):
            if c not in keys:
                errors.append(f"zh/{f.name}: \\cite{{{c}}} has no \\bibitem in references_zh.tex")
        for g in figures(t):
            if g not in figs:
                errors.append(f"zh/{f.name}: figure figures_zh/{g}.pdf is missing")


def check_data_and_checks(errors: list[str]) -> None:
    snap = ROOT / "data" / "snapshots"
    if snap.exists():
        for f in sorted(snap.iterdir()):
            if f.suffix in {".json", ".md"} or f.name.startswith("."):
                continue
            meta = f.with_suffix(".json")
            if not meta.exists():
                errors.append(f"data/snapshots/{f.name} has no metadata file {meta.name}")
                continue
            try:
                m = json.loads(meta.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                errors.append(f"data/snapshots/{meta.name}: invalid JSON ({e})")
                continue
            missing = [k for k in SNAPSHOT_FIELDS if not m.get(k)]
            if missing:
                errors.append(f"data/snapshots/{meta.name}: missing fields {missing}")
    for f in sorted((ROOT / "checks").glob("check_ch*.py")):
        m = re.fullmatch(r"check_ch(\d+)\.py", f.name)
        if not m or not 1 <= int(m.group(1)) <= len(S.CHAPTERS):
            errors.append(f"checks/{f.name} does not belong to a chapter")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    check_structure(errors)
    stubs = check_chapters(errors, warnings)
    check_main(errors)
    check_labels_refs(errors, warnings)
    check_data_and_checks(errors)
    pending = []
    for zh in sorted((ROOT / "zh").glob("*.tex")):
        en = ROOT / "en" / zh.name
        if en.exists():
            errors += compare_pair(zh, en)
        else:
            pending.append(zh.name)
    for en in sorted((ROOT / "en").glob("*.tex")):
        if not (ROOT / "zh" / en.name).exists():
            errors.append(f"en/{en.name} has no Chinese counterpart")
    for w in warnings:
        print("warning:", w)
    n = len(S.CHAPTERS)
    print(f"{n - stubs} of {n} chapters written; {stubs} still skeletons.")
    if len(pending) == len(list((ROOT / 'zh').glob('*.tex'))):
        print("English edition: not started (reserved).")
    if errors:
        for e in errors:
            print("ERROR:", e)
        return 1
    print("Structure, labels, references, citations, figures, data snapshots and check scripts are consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
