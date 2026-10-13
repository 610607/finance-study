"""Regenerate figures for one language.

    MACRO_LANG=zh python figsrc/build.py            # all Chinese figures
    MACRO_LANG=en python figsrc/build.py name ...   # selected English figures

Figure modules are figsrc/fig_chNN.py (one per chapter); each figure is a function decorated
with @style.figure("name").
"""
from __future__ import annotations

import importlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

import style  # noqa: E402

MODULES = sorted(p.stem for p in HERE.glob("fig_*.py"))


def main(argv: list[str]) -> None:
    for m in MODULES:
        importlib.import_module(m)
    names = argv or sorted(style.REGISTRY)
    unknown = [n for n in names if n not in style.REGISTRY]
    if unknown:
        raise SystemExit(f"Unknown figure(s): {unknown}")
    if not names:
        print("No figures defined yet (figsrc/fig_chNN.py).")
        return
    t0 = time.time()
    for n in names:
        style.save(style.REGISTRY[n](), n)
        print(f"[{style.LANG}] {n}")
    done = sorted(p.stem for p in style.OUT.glob("*.pdf"))
    (style.OUT / "manifest.json").write_text(json.dumps({"language": style.LANG, "font": style.FONT,
                                                         "figures": done}, indent=2, ensure_ascii=False))
    print(f"{len(names)} figure(s) in {time.time() - t0:.1f} s -> {style.OUT}")


if __name__ == "__main__":
    main(sys.argv[1:])
