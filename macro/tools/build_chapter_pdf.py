"""Build one chapter's reader PDF, with only its cited bibliography.

From macro/ with the normal XeLaTeX/font environment active:
    python tools/build_chapter_pdf.py zh/ch27_interwar.tex

Reuses build.py's cross-reference harness and the shared preamble. It does not
rewrite any whole-volume or book PDF. Run build.py first when current volume-wide
reference numbering is required. Output: compiled/Macroeconomics_Vol1_ChapterNN_ZH.pdf.
"""
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from build import external_labels, labels_in  # noqa: E402


def main(chapter):
    chapter = (ROOT / chapter).resolve()
    number = int(re.match(r'ch(\d+)_', chapter.name).group(1))
    out = ROOT / 'build' / f'reader_{chapter.stem}'
    out.mkdir(parents=True, exist_ok=True)
    text = chapter.read_text(encoding='utf-8')
    own = labels_in([chapter])
    lines = external_labels((0, '', '', ()), own)
    registry = (ROOT / 'docs' / 'PLAN.md').read_text(encoding='utf-8').split('## Label registry', 1)[1].split('```', 2)[1].split()
    known = {re.match(r'\\newlabel\{([^}]+)\}', line).group(1) for line in lines}
    for label in registry:
        if label not in own and label not in known:
            lines.append(f'\\newlabel{{{label}}}{{{{0.0}}{{}}{{{label}}}{{}}{{}}}}')
    (out / f'labels_{chapter.stem}.tex').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    keys = {key.strip() for group in re.findall(r'\\cite\{([^}]+)\}', text) for key in group.split(',')}
    bibliography = (ROOT / 'references_zh.tex').read_text(encoding='utf-8')
    entries = re.findall(r'(\\bibitem\{([^}]+)\}.*?)(?=\\bibitem\{|\\end\{thebibliography\})', bibliography, re.S)
    selected = [entry.strip() for entry, key in entries if key in keys]
    found = {key for _, key in entries if key in keys}
    if keys != found:
        raise RuntimeError(f'Missing bibliography entries: {keys - found}')
    (out / f'references_{chapter.stem}.tex').write_text('\\begin{thebibliography}{99}\n' + '\n\n'.join(selected) + '\n\\end{thebibliography}\n', encoding='utf-8')
    tex = rf'''\documentclass[11pt,a4paper,oneside,openany]{{book}}
\newif\ifChinese
\Chinesetrue
\input{{preamble}}
\input{{{out / f'labels_{chapter.stem}'}}}
\begin{{document}}
\setcounter{{chapter}}{{{number - 1}}}
\input{{{chapter.with_suffix('')}}}
\input{{{out / f'references_{chapter.stem}'}}}
\end{{document}}
'''
    (out / 'reading.tex').write_text(tex, encoding='utf-8')
    for _ in range(2):
        run = subprocess.run(['xelatex', '-interaction=nonstopmode', f'-output-directory={out}', str(out / 'reading.tex')], cwd=ROOT, capture_output=True, text=True)
        if run.returncode:
            raise RuntimeError('XeLaTeX failed; see ' + str(out / 'reading.log'))
    log = (out / 'reading.log').read_text(encoding='utf-8', errors='replace')
    if re.search(r'^!|(?:Reference|Citation) `[^\n]+undefined|Missing character:', log, re.M):
        raise RuntimeError('LaTeX errors, undefined references or missing glyphs; see ' + str(out / 'reading.log'))
    over = re.findall(r'Overfull \\hbox \(([\d.]+)pt too wide\)', log)
    if any(float(v) > 1 for v in over):
        raise RuntimeError('Overfull line in reader PDF; see ' + str(out / 'reading.log'))
    destination = ROOT / 'compiled' / f'Macroeconomics_Vol1_Chapter{number}_ZH.pdf'
    destination.parent.mkdir(exist_ok=True)
    shutil.copyfile(out / 'reading.pdf', destination)
    print(f'{destination} ({len(selected)} cited bibliography entries)')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('usage: python tools/build_chapter_pdf.py zh/chNN_<slug>.tex')
    main(sys.argv[1])
