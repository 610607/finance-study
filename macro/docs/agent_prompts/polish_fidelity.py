"""Compare a chapter before and after polishing.

    cd /tmp && python3 -I <repo>/macro/docs/agent_prompts/polish_fidelity.py OLD.tex NEW.tex
Reports what was removed or added: Arabic numbers, quotations, cite keys, labels, references,
figures and inline math, plus readability metrics before and after.
Give the same file twice to measure a new chapter. Metrics count the main text only (no boxes, examples,
tables or display math); colon and semicolon counts are per 1000 Chinese characters, colons before a
quotation excluded. Used for the language polish of Chapters 1–21 (docs/POLISH.md)."""
import re, sys, statistics as st
from collections import Counter

def nocomment(t):
    return "\n".join(l for l in t.splitlines() if not l.lstrip().startswith("%"))

def items(t):
    t = nocomment(t)
    d = {}
    d["label"] = Counter(re.findall(r"\\label\{([^}]*)\}", t))
    d["cite"] = Counter(k.strip() for g in re.findall(r"\\cite[pt]?\{([^}]*)\}", t) for k in g.split(","))
    d["ref"] = Counter(re.findall(r"\\(?:chref|secref|ref|eqref|figref|tabref|exref|appref)\{([^}]*)\}", t))
    d["fig"] = Counter(re.findall(r"\\fig\{([^}]*)\}", t))
    d["math"] = Counter(re.sub(r"\s+", "", m) for m in re.findall(r"\$([^$]+)\$", t))
    d["quote"] = Counter(re.findall(r"“([^”]*)”", t))
    plain = re.sub(r"\$[^$]*\$", " ", t)
    plain = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^}]*\})?", " ", plain)
    d["number"] = Counter(re.findall(r"\d[\d,]*(?:\.\d+)?", plain))
    d["envs"] = Counter(re.findall(r"\\begin\{([a-z]+)\}", t))
    return d

CJK = re.compile(r"[\u4e00-\u9fff]")
def body(t):
    t = nocomment(t)
    t = t.split(r"\end{chapterguide}", 1)[-1]
    t = re.split(r"\\begin\{takeaways\}", t)[0]
    for env in ["equation\\*?", "align\\*?", "keyeq", "figure", "table", "tabularx", "gather\\*?",
                "example", "solution", "deeper", "pitfall", "intuition", "compare", "case", "exercises", "selfcheck"]:
        t = re.sub(r"\\begin\{(%s)\}.*?\\end\{\1\}" % env, "\n\n", t, flags=re.S)
    t = re.sub(r"\$[^$]*\$", "X", t)
    t = re.sub(r"\\cite[pt]?\{[^}]*\}", "", t)
    t = re.sub(r"\\(chref|secref|figref|tabref|exref|eqref|appref|ref|label)\{[^}]*\}", "R", t)
    t = re.sub(r"\\fig\{[^}]*\}\{[^}]*\}", "\n\n", t)
    t = re.sub(r"\\(sub)*section\*?\{[^}]*\}", "\n\n", t)
    t = re.sub(r"\\[a-zA-Z]+\*?", "", t)
    return t.replace("{", "").replace("}", "").replace("~", " ")

def metrics(t):
    b = body(t)
    paras = [p.strip() for p in re.split(r"\n\s*\n", b) if len(CJK.findall(p)) > 20]
    han = sum(len(CJK.findall(p)) for p in paras) or 1
    sents = [s for p in paras for s in re.split(r"(?<=[。！？])", p) if len(CJK.findall(s)) > 3]
    sl = [len(re.sub(r"\s", "", s)) for s in sents]
    pl = [len(re.sub(r"\s", "", p)) for p in paras]
    q = re.findall(r"“([^”]*)”", b)
    nq = re.sub(r"“[^”]*”", "", b)
    par = re.findall(r"（([^（）]*)）", nq)
    aside = [p for p in par if re.match(r"[\u4e00-\u9fff“]", p) and not re.match(r"[\u4e00-\u9fff]{1,6}$", p)]
    k = 1000 / han
    qpp = [len(re.findall(r"“", p)) for p in paras]
    return dict(han=han, sent_med=st.median(sl), gt80=round(100 * sum(x > 80 for x in sl) / len(sl)),
                para_med=st.median(pl), para_max=max(pl),
                quote_pct=round(100 * sum(len(x) for x in q) / max(1, len(re.sub(r"\s", "", b))), 1),
                q_para_max=max(qpp), q_para_ge3=sum(x >= 3 for x in qpp),
                colon=round(len(re.findall(r"：(?!“)", nq)) * k, 1), semi=round(nq.count("；") * k, 1),
                aside=round(len(aside) * k, 1), dec2=round(len(re.findall(r"\d\.\d\d", b)) * k, 1),
                formula=len(re.findall(r"这一节(回答|交代|讨论|看|说)", b)) + len(re.findall(r"这一章回答", b)),
                book_self=len(re.findall(r"本书没有找到|没能取得|中文都是本书的翻译", b)))

if __name__ == "__main__":
    old, new = (open(p, encoding="utf-8").read() for p in sys.argv[1:3])
    a, b = items(old), items(new)
    for k in a:
        rem, add = a[k] - b[k], b[k] - a[k]
        if rem or add:
            print(f"== {k}: removed {sum(rem.values())}, added {sum(add.values())}")
            if k in ("quote",):
                for x in rem: print("   -", x[:90])
                for x in add: print("   +", x[:90])
            else:
                if rem: print("   -", " | ".join(list(rem.elements())[:60]))
                if add: print("   +", " | ".join(list(add.elements())[:60]))
    ma, mb = metrics(old), metrics(new)
    print("metric      " + " ".join(f"{k:>9}" for k in ma))
    print("before      " + " ".join(f"{str(v):>9}" for v in ma.values()))
    print("after       " + " ".join(f"{str(v):>9}" for v in mb.values()))
