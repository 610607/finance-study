"""Readability report for chapter files: the metrics of docs/NARRATIVE.md §10.3 and where they fail.

    python3 tools/readability.py zh/chNN_<slug>.tex [...]

The metrics count the main text only (no boxes, examples, tables, figures or display math), as in
docs/POLISH.md §2; punctuation and asides are per 1000 Chinese characters, colons before a
quotation are not counted.  Below the metrics the report lists, with line numbers: sentences over
80 characters, sentences with more than three numbers (years and dates aside) or two semicolons,
paragraphs over 400 characters or with more than two quotations, section-opening formulas, meta
phrases and sentences about the book, a roadmap of \\secref in the opening, and the currencies and
units of docs/NARRATIVE.md §7.6 whose first use in the chapter is not explained in the same
paragraph.  The unit check is a heuristic: it looks for "是……单位／货币／金币……", "合 N", "等于"
and the like next to the word.  Everything here is advisory; tools/check_chapter.py prints it after
the LaTeX checks.  Standard library only.
"""
from __future__ import annotations

import re
import statistics as st
import sys
from pathlib import Path

CJK = re.compile(r"[\u4e00-\u9fff]")
BOXES = ["equation\\*?", "align\\*?", "keyeq", "figure", "table", "tabularx", "gather\\*?", "example",
         "solution", "deeper", "pitfall", "intuition", "compare", "case", "exercises", "selfcheck"]
TARGETS = [  # (metric, limit, unit) from NARRATIVE.md §10.3
    ("sent_med", 40, "字"), ("gt80", 10, "%"), ("para_med", 200, "字"), ("para_max", 400, "字"),
    ("quote_pct", 15, "%"), ("q_para_max", 2, "处"), ("colon", 4, "/千字"), ("semi", 3, "/千字"),
    ("aside", 1, "/千字"), ("dec2", 1, "/千字"), ("formula", 0, ""), ("book_self", 0, "")]
FORMULA = r"这一节(?:回答|交代|讨论|看|说)|这一章回答"
META = r"如前所述|值得注意的是|需要指出的是|下面我们来看|下面来看|不难看出|众所周知"
BOOK_SELF = r"本书没有找到|没能取得|中文都是本书的翻译"

# Currencies and units met in Chapters 1–21 (NARRATIVE.md §7.6).  Words of two or more characters
# are matched anywhere; one-character units only after a numeral.
UNITS = ["德拉克马", "四德拉克马", "奥波尔", "塔兰特", "弥那", "舍客勒", "德本", "阿塔巴", "第纳尔",
         "塞斯特斯", "安东尼尼安努斯", "索利都斯", "迪拉姆", "米斯卡勒", "杜卡特", "弗罗林", "里弗尔",
         "德尼耶", "埃居", "厄尔", "马克", "先令", "便士", "基尼", "比索", "马拉维迪", "雷亚尔", "斯泰弗",
         "塔勒", "里克斯达勒", "卢比", "安那", "派斯", "克罗尔", "戈比", "卢布", "贝币", "国际元",
         "盎司", "斯克鲁普尔", "阿斯"]
ONE = "石斗升两钱分厘贯缗匁朱文铢锭斤镑盾苏両"
NUMERAL = r"(?:\d[\d,.]*\s*|(?<![百千万])[一二三四五六七八九十]+)"
NOT_AFTER = {"分": "之点比钟号界析配别子", "升": "到至为高了起", "文": "不", "贯": "的地如以", "两": "个天年次句种家位人条处"}
ONE_RE = re.compile(NUMERAL + r"([%s])" % ONE)
IDIOM = re.compile(r"一文钱|一文也|一文不|一分钱|一分也|一升，|[降五]升[；，]|(?<!\d)十分(?!钱)|一贯(?=[支主反坚的地如以])|厘米|分位")
EXPL = re.compile(r"(?:是|为|即|指|叫|称|作|一种)[^。；！？]{0,25}?(?:单位|货币|钱币|金币|银币|铜币|铸币|硬币|纸币"
                  r"|银元|钞|重量|容量|长度|面积|记账)|(?:合|就是|等于)\s*约?\s*[\d一二三四五六七八九十半百千]|折合|进位")


# ---------- the metrics, measured as in docs/POLISH.md §2 ----------

def nocomment(t: str) -> str:
    return "\n".join(l for l in t.splitlines() if not l.lstrip().startswith("%"))


def body(t: str) -> str:
    t = nocomment(t)
    t = t.split(r"\end{chapterguide}", 1)[-1]
    t = re.split(r"\\begin\{takeaways\}", t)[0]
    for env in BOXES:
        t = re.sub(r"\\begin\{(%s)\}.*?\\end\{\1\}" % env, "\n\n", t, flags=re.S)
    t = re.sub(r"\$[^$]*\$", "X", t)
    t = re.sub(r"\\cite[pt]?\{[^}]*\}", "", t)
    t = re.sub(r"\\(chref|secref|figref|tabref|exref|eqref|appref|ref|label)\{[^}]*\}", "R", t)
    t = re.sub(r"\\fig\{[^}]*\}\{[^}]*\}", "\n\n", t)
    t = re.sub(r"\\(sub)*section\*?\{[^}]*\}", "\n\n", t)
    t = re.sub(r"\\[a-zA-Z]+\*?", "", t)
    return t.replace("{", "").replace("}", "").replace("~", " ")


def metrics(t: str) -> dict:
    b = body(t)
    paras = [p.strip() for p in re.split(r"\n\s*\n", b) if len(CJK.findall(p)) > 20]
    han = sum(len(CJK.findall(p)) for p in paras) or 1
    sents = [s for p in paras for s in re.split(r"(?<=[。！？])", p) if len(CJK.findall(s)) > 3] or [""]
    sl = [len(re.sub(r"\s", "", s)) for s in sents]
    pl = [len(re.sub(r"\s", "", p)) for p in paras] or [0]
    q = re.findall(r"“([^”]*)”", b)
    nq = re.sub(r"“[^”]*”", "", b)
    par = re.findall(r"（([^（）]*)）", nq)
    aside = [p for p in par if re.match(r"[\u4e00-\u9fff“]", p) and not re.match(r"[\u4e00-\u9fff]{1,6}$", p)]
    k = 1000 / han
    qpp = [len(re.findall(r"“", p)) for p in paras] or [0]
    return dict(han=han, sent_med=st.median(sl), gt80=round(100 * sum(x > 80 for x in sl) / len(sl)),
                para_med=st.median(pl), para_max=max(pl),
                quote_pct=round(100 * sum(len(x) for x in q) / max(1, len(re.sub(r"\s", "", b))), 1),
                q_para_max=max(qpp), q_para_ge3=sum(x >= 3 for x in qpp),
                colon=round(len(re.findall(r"：(?!“)", nq)) * k, 1), semi=round(nq.count("；") * k, 1),
                aside=round(len(aside) * k, 1), dec2=round(len(re.findall(r"\d\.\d\d", b)) * k, 1),
                formula=len(re.findall(FORMULA, b)), book_self=len(re.findall(BOOK_SELF, b)))


# ---------- paragraphs with line numbers, for the itemized findings ----------

def clean_line(l: str) -> str:
    l = re.sub(r"(?<!\\)%.*", "", l).replace("\\%", "%")
    l = re.sub(r"\$[^$]*\$", "X", l)
    l = re.sub(r"\\cite[pt]?\{[^}]*\}", "", l)
    l = re.sub(r"\\(chref|secref|figref|tabref|exref|eqref|appref|ref|label)\{[^}]*\}", "R", l)
    l = re.sub(r"\\footnote\{[^}]*\}", "", l)
    l = re.sub(r"\\(begin|end)\{[^}]*\}(\[[^\]]*\])?", "", l)
    l = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", "", l)
    return l.replace("{", "").replace("}", "").replace("~", " ").strip()


def paragraphs(t: str) -> list[tuple[int, list[tuple[int, str]]]]:
    """Main-text paragraphs as (kind, [(line, cleaned text)]); kind 0 = opening, 1 = after a \\section."""
    lines = t.splitlines()
    out, cur, depth, started, kind = [], [], 0, False, 0
    box = re.compile(r"\\(begin|end)\{(%s)\}" % "|".join(BOXES))

    def flush():
        nonlocal cur
        if cur and sum(len(CJK.findall(x)) for _, x in cur) > 20:
            out.append((kind, cur))
        cur = []

    for n, raw in enumerate(lines, 1):
        if r"\end{chapterguide}" in raw:
            started = True
            continue
        if not started:
            continue
        if r"\begin{takeaways}" in raw:
            break
        for m in box.finditer(raw):
            depth += 1 if m.group(1) == "begin" else -1
            flush()
        if depth > 0 or box.search(raw):
            continue
        if raw.lstrip().startswith("%"):
            continue
        if re.match(r"\s*\\(sub)*section", raw) or raw.lstrip().startswith(r"\fig{"):
            flush()
            if raw.lstrip().startswith(r"\section"):
                kind = 1
            continue
        if not raw.strip() or re.match(r"\s*\\(item|begin\{(itemize|enumerate)\}|end\{(itemize|enumerate)\})", raw):
            flush()
            if not raw.strip() or not re.match(r"\s*\\item", raw):
                continue
        cur.append((n, clean_line(raw)))
    flush()
    return out


def sentences(par: list[tuple[int, str]]):
    """Yield (line, sentence) for one paragraph."""
    text, starts = "", []
    for n, x in par:
        starts.append((len(text), n))
        text += x
    pos = 0
    for s in re.split(r"(?<=[。！？])", text):
        line = max(n for off, n in starts if off <= pos)
        pos += len(s)
        if len(CJK.findall(s)) > 3:
            yield line, s


def numbers(s: str) -> int:
    s = re.sub(r"“[^”]*”", "", s)
    toks = re.finditer(r"\d[\d,]*(?:\.\d+)?", s)
    return sum(1 for m in toks
               if not re.fullmatch(r"1\d{3}|20\d{2}", m.group())
               and not re.match(r"\s*(月|日|世纪|年代)", s[m.end():]))


def findings(t: str) -> list[str]:
    out = []
    paras = paragraphs(t)
    raw = t.splitlines()
    for kind, par in paras:
        first = par[0][0]
        plen = len(re.sub(r"\s", "", "".join(x for _, x in par)))
        nq = sum(x.count("“") for _, x in par)
        if plen > 400:
            out.append(f"line {first}: paragraph of {plen} characters (≤400)")
        if nq > 2:
            out.append(f"line {first}: {nq} quotations in one paragraph (≤2)")
        if kind == 0:
            src = "\n".join(raw[n - 1] for n, _ in par)
            if src.count(r"\secref") >= 3:
                out.append(f"line {first}: a roadmap of {src.count(chr(92) + 'secref')} \\secref in the opening")
        for line, s in sentences(par):
            short = re.sub(r"\s+", " ", s).strip()
            if len(re.sub(r"\s", "", s)) > 80:
                out.append(f"line {line}: sentence of {len(re.sub(chr(92) + 's', '', s))} characters (≤80): {short[:24]}……")
            if numbers(s) > 3:
                out.append(f"line {line}: {numbers(s)} numbers in one sentence (≤3): {short[:24]}……")
            if s.count("；") >= 2:
                out.append(f"line {line}: {s.count('；')} semicolons in one sentence (≤1): {short[:24]}……")
            for pat, what in ((FORMULA, "section-opening formula"), (META, "meta phrase"),
                              (BOOK_SELF, "sentence about the book")):
                for m in re.finditer(pat, s):
                    out.append(f"line {line}: {what} “{m.group()}”")
            if re.search(r"\d\.\d{3}", re.sub(r"X", "", s)):
                out.append(f"line {line}: three or more decimals in the narrative: {short[:24]}……")
    return out


# ---------- currencies and units: first use, and whether it is explained there ----------

def unit_uses(t: str) -> dict[str, list[int]]:
    """{unit: [line numbers]} over the whole chapter, boxes and tables included, from the opening on."""
    uses: dict[str, list[int]] = {}
    started = False
    for n, raw in enumerate(t.splitlines(), 1):
        if r"\end{chapterguide}" in raw:
            started = True
            continue
        if not started or raw.lstrip().startswith("%"):
            continue
        x = clean_line(raw)
        y = re.sub(r"四德拉克马|马克思|马克斯|马克·", "", x)
        for u in UNITS:
            if u in (x if u == "四德拉克马" else y):
                uses.setdefault(u, []).append(n)
        z = IDIOM.sub(lambda m: "□" * len(m.group()), x)
        for m in ONE_RE.finditer(z):
            u = m.group(1)
            if x[m.end():m.end() + 1] and x[m.end()] in NOT_AFTER.get(u, ""):
                continue
            uses.setdefault(u, []).append(n)
    return uses


def explained(unit: str, text: str) -> bool:
    for s in re.split(r"(?<=[。！？；])", text):
        if unit in s and EXPL.search(s):
            return True
    return False


def unit_findings(t: str) -> tuple[int, list[str]]:
    lines = t.splitlines()
    blocks: dict[int, str] = {}  # line -> text of the blank-line block around it
    start = 0
    for i in range(len(lines) + 1):
        if i == len(lines) or not lines[i].strip():
            text = " ".join(clean_line(l) for l in lines[start:i])
            for j in range(start, i):
                blocks[j + 1] = text
            start = i + 1
    out = []
    uses = unit_uses(t)
    for u, ls in sorted(uses.items(), key=lambda kv: kv[1][0]):
        if explained(u, blocks.get(ls[0], "")):
            continue
        later = next((n for n in range(ls[0] + 1, len(lines) + 1)
                      if lines[n - 1].strip() and explained(u, clean_line(lines[n - 1]))), None)
        where = f"explained at line {later}" if later else \
            "not explained in this chapter (an earlier chapter may: then give a one-clause reminder)"
        out.append(f"line {ls[0]}: {u} first used, {where}")
    return len(uses), out


def report(path, limit: int = 12) -> None:
    path = Path(path)
    t = path.read_text(encoding="utf-8")
    m = metrics(t)
    print(f"readability (advisory), {path.name}: main text {m['han']} Chinese characters, boxes excluded")
    cells, over = [], []
    for k, lim, unit in TARGETS:
        cells.append(f"{k} {m[k]}{unit}")
        if m[k] > lim:
            over.append(f"{k} {m[k]} > {lim}")
    print("  " + " | ".join(cells))
    print("  over target (NARRATIVE.md §10.3):", ", ".join(over) or "none")
    f = findings(t)
    for x in f[:limit]:
        print("  " + x)
    if len(f) > limit:
        print(f"  ... and {len(f) - limit} more (python3 tools/readability.py {path.as_posix()} --all)")
    n, u = unit_findings(t)
    print(f"  currencies and units (§7.6): {n} found; first use not explained in its paragraph: {len(u)}")
    for x in u[:limit]:
        print("    " + x)
    if len(u) > limit:
        print(f"    ... and {len(u) - limit} more")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit(__doc__)
    for a in args:
        report(a, limit=10 ** 6 if "--all" in sys.argv else 12)
