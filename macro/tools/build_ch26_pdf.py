"""Reproduce the reviewed Chapter 26 reader PDF (kept for the record in STATUS.md).

From macro/:
    python tools/build_ch26_pdf.py

Same as python tools/build_chapter_pdf.py zh/ch26_weimar.tex.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_chapter_pdf import main  # noqa: E402


if __name__ == '__main__':
    main('zh/ch26_weimar.tex')
