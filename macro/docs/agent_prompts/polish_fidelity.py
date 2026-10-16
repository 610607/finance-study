"""Compare a chapter before and after polishing.

    cd /tmp && python3 -I <repo>/macro/docs/agent_prompts/polish_fidelity.py OLD.tex NEW.tex
Reports what was removed or added: Arabic numbers, quotations, cite keys, labels, references,
figures and inline math, plus readability metrics before and after.
Give the same file twice to measure a new chapter. Metrics count the main text only (no boxes, examples,
tables or display math); colon and semicolon counts are per 1000 Chinese characters, colons before a
quotation excluded; they come from tools/readability.py, which also lists the failing paragraphs and
sentences of one chapter. Used for the language polish of Chapters 1–21 (docs/POLISH.md)."""
import re, sys
from collections import Counter
from pathlib import Path

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

# The readability metrics live in tools/readability.py (the same code measured docs/POLISH.md §2).
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from readability import metrics  # noqa: E402

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
