# English chapter text (reserved)

This folder will hold the English edition of Volume 1: one file per Chinese file in `../zh/`, with the same file name and identical labels, citations, figure calls, teaching-box order and displayed mathematics. The Chinese edition is the master text; the translation will start once Chinese chapters are finished.

Already prepared for it: the `\ZE{中文}{English}` switch in `../preamble.tex` (box headings, cross-reference words), `T("中文", "English")` labels in every figure (`../figsrc/`), and English part, book and chapter titles in `../structure.py`. When translation starts, add `main_en.tex`, `en/parts.tex`, `en/front_*.tex` and `references_en.tex`; `../validate_source.py` then checks every translated pair.
