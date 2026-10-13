# 宏观经济学：从古代货币到当下争论 · Macroeconomics: From Ancient Money to Present Debates

**Finance Study Series, Volume 1 · 金融学习丛书 · 第一卷**

**Status (October 2026): skeleton and one sample chapter.** All 84 chapters exist with their guide box (core question, learning goals, prerequisites); the plan for every chapter is in `docs/PLAN.md`. Chapter 12 (Song, Yuan and Ming paper money) is written in full as the sample that sets the style; the others will follow chapter by chapter. The volume compiles to PDF and EPUB (`compiled/`). Chinese is the master text; an English edition is reserved.

状态（2026 年 10 月）：骨架版加一章样章。84 章均已建立，每章有导引框（核心问题、学习目标、前置章节）；各章写作计划见 `docs/PLAN.md`。第 12 章（宋元明纸币）已作为样章完整写出，其余各章将逐章写出。全卷可编译为 PDF 与 EPUB（`compiled/`）。中文为母本，英文版预留。

A question-driven course in macroeconomics that follows history: from temple accounts in Mesopotamia, Han granaries and Song paper money, through the gold standard, the Great Depression and Keynes, planned economies and the postwar golden age, stagflation and the expectations revolution, the Great Moderation and transition, the 2008 crisis, to the 2021–23 inflation, fiscal dominance and the currency hierarchy — ending with an outlook. Each era brings a crisis the old theory could not explain; each new theory is then tested by the next crisis.

本书以问题为线索、沿历史讲宏观经济学：从美索不达米亚的神庙记账、汉代的常平仓与宋代的纸币，经过金本位、大萧条与凯恩斯，计划经济与战后黄金时代，滞胀与预期革命，大缓和与转轨，2008 年危机，一直讲到 2021—2023 年的通胀、财政主导与货币等级，最后展望未来。每个时代都有一场旧理论解释不了的危机，每个新理论又被下一场危机检验。

## How the volume is built / 全卷结构

| Part / 部分 | Chapters / 章 | Book / 分册 |
|---|---|---|
| I 宏观的语言 · The language of macroeconomics | 1–5 | 1 |
| II 古代世界 · The ancient world (3000 BCE–600 CE) | 6–9 | 1 |
| III 中世纪与近世 · The medieval and early modern world (600–1750) | 10–17 | 1 |
| IV 古典世界 · The classical world (1750–1914) | 18–25 | 2 |
| V 战争、萧条与凯恩斯革命 · War, depression and the Keynesian revolution (1914–1945) | 26–34 | 2 |
| VI 战后黄金时代：东方与西方 · The postwar golden age: East and West (1945–1970) | 35–43 | 3 |
| VII 滞胀与预期革命 · Stagflation and the expectations revolution (1968–1985) | 44–52 | 3 |
| VIII 大缓和、新共识与转轨 · The Great Moderation, the new consensus and transition (1982–2007) | 53–63 | 4 |
| IX 金融危机之后 · After the financial crisis (2008–2019) | 64–72 | 4 |
| X 疫情通胀与当下 · Pandemic inflation and the present (2020–2026) | 73–79 | 5 |
| XI 综合与展望 · Synthesis and outlook | 80–84 | 5 |
| Appendices · 附录 A 数学工具 · B 符号与数据来源 · C 对照与案例索引 · D 分地区大事年表 | | 5 |

Every chapter follows the same path: guiding question → the world at the time → the theory's answer (intuition → derivation) → worked examples → data check and counterexamples → what remains today → takeaways → self-check with answers. Comparison boxes ("same / different / one sentence") and case boxes (at least one outside the US and UK per chapter) are indexed in Appendix C. Colours carry meaning in text and figures: green output, vermilion prices and inflation, blue money and interest rates, purple fiscal, orange external sector and exchange rates, warm grey institutions and data.

每章遵循同一学习路径：核心问题 → 当时的世界 → 理论的回答（直觉 → 推导）→ 例题 → 数据检验与反例 → 今天还剩什么 → 本章要点 → 自测与答案。对照框（相同／不同／一句话）与案例框（每章至少一个来自英美以外）在附录 C 汇总。颜色在正文与插图中含义一致：绿为产出，朱红为价格与通胀，蓝为货币与利率，紫为财政，橙为对外部门与汇率，暖灰为制度与数据。

## Repository layout / 文件结构

```
structure.py                 parts, books (分册) and chapters: the list every tool reads
main_zh.tex                  whole-volume entry point (title page, preface, parts, chapters, appendices)
preamble.tex                 layout: fonts, colours, teaching boxes, cross-reference helpers
zh/                          chapters chNN_slug.tex, parts.tex, front matter, appendices
en/                          reserved for the English edition
references_zh.tex            bibliography (verified entries only)
data/                        snapshots with metadata (README.md), planned sources (SOURCES.md)
checks/                      check_chNN.py: every number of a chapter recomputed and asserted
figsrc/                      figure sources: style.py (palette, helpers), fig_chNN.py
figures_zh/, figures/        figure PDFs (Chinese / English), created as chapters are written
validate_source.py           consistency of structure, labels, references, sources, data and checks
tools/check_chapter.py       compile one chapter in isolation and report layout problems
tools/epub/                  EPUB edition: build_epub.py (LaTeX -> pandoc), boxes.lua, epub.css, cover.py
tools/setup_env.sh           prepares a fresh machine: system packages (TeX Live, fonts), Python packages, the classical-Chinese corpus, epubcheck, STIX Two
tools/probe_network.sh       which source hosts the shell can reach in this session
build.py                     builds the whole volume or one book (PDF; --epub also EPUB)
docs/                        PLAN.md (chapter plan, label registry), STYLE.md, WORKFLOW.md (batch writing), FORWARD_REFS.md, EPUB.md, STATUS.md, agent_prompts/
compiled/                    the built PDFs and EPUBs
```

## Build / 编译

Requirements:
- TeX Live 2023 or newer with **XeLaTeX** and **xeCJK** (Debian/Ubuntu: `texlive-xetex`, `texlive-latex-extra`, `texlive-lang-chinese`), including `fontspec`, `unicode-math`, `tcolorbox`, `titlesec`, `titletoc`, `fancyhdr`, `booktabs`, `tabularx`, `hyperref`, `tikz`.
- Fonts: STIX Two Text and STIX Two Math, Inter, Noto Serif CJK SC and Noto Sans CJK SC (`tools/setup_env.sh` installs STIX Two from stipub/stixfonts and checks the others). Fallbacks are built in (TeX Gyre Termes/Heros, Latin Modern Math, Fandol) so that the sources always compile, but the books in `compiled/` are built with the intended fonts; no fonts are distributed here.
- Python 3.10+ with the packages in `requirements.txt` for figures, checks and contact sheets; `pdftoppm` (poppler) for `tools/check_chapter.py`.
- For the EPUB edition: pandoc 3.1 or newer; optionally epubcheck (Java) to validate it (`docs/EPUB.md`).

```bash
python build.py                    # whole volume -> compiled/Macroeconomics_Vol1_ZH.pdf
python build.py --book 2           # one book     -> compiled/Macroeconomics_Vol1_Book2_ZH.pdf
python build.py --book all         # whole volume and all five books
python build.py --checks           # run checks/check_*.py and validate_source.py first
python build.py --book all --epub  # also the EPUB editions -> compiled/*.epub (numbers taken from the PDF build)
python tools/epub/build_epub.py --check   # EPUB only, validated with epubcheck (docs/EPUB.md)
python validate_source.py          # consistency checks only
python tools/check_chapter.py zh/ch12_songming.tex   # compile one chapter and report layout problems
```

## What the numbers will and will not establish / 数字的范围

Every statistic in the text will come from a dated data snapshot with its source and licence recorded, and every computed number will be reproduced by a check script. Premodern and planned-economy figures are reconstructions or contested official statistics and are presented with their uncertainty. The teaching models illustrate mechanisms; they are not forecasts or investment advice.

正文中的统计数字都将来自注明来源、序列与下载日期的数据快照，计算得到的数字都由检查脚本复算。前现代与计划经济的数字多为重建估计或有争议的官方统计，正文会写明不确定性。教学模型用来说明机制，不是预测，也不构成投资建议。
