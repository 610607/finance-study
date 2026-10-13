# EPUB 版的工作流

PDF 是排版母本；EPUB 版从同一套 LaTeX 源文件生成，供手机和电子书阅读器使用。两者的章节、图、表、例题、公式和文献编号完全一致，因为 EPUB 不自己编号，而是读取 PDF 编译留下的编号。

## 命令

```bash
python3 build.py --epub                 # 编译全卷 PDF，再写 compiled/Macroeconomics_Vol1_ZH.epub
python3 build.py --book all --epub      # 全卷与五个分册，PDF 与 EPUB 各六份
python3 tools/epub/build_epub.py        # 只重写 EPUB（要求 build/main_zh.aux 比所有源文件新）
python3 tools/epub/build_epub.py --book 2 --check   # 一个分册，并用 epubcheck 检验
```

依赖：pandoc 3.1 或更新（https://pandoc.org/installing.html）；Python 包见 `requirements.txt`（封面用 matplotlib）。`--check` 需要 epubcheck（https://github.com/w3c/epubcheck/releases），把 `EPUBCHECK_JAR` 设为 `epubcheck.jar` 的路径，或把 `epubcheck` 放进 PATH。

## 做法

1. **编号取自 PDF 编译。** `build/main_zh.aux` 的 `\newlabel` 给出章、节、图、表、例题与公式的编号和章名，`\bibcite` 给出文献编号，`build/main_zh.toc` 给出未加标签的节的编号。源文件比 `.aux` 新时脚本停下，提示先编译 PDF；`build.py --epub` 会自动先编译。
2. **改写成 pandoc 能读的 LaTeX。** `tools/epub/build_epub.py` 不求值任何 TeX，只做有界的文本替换：
   - `\ZE{中}{英}` 取中文；`\chref`、`\secref`、`\figref`、`\tabref`、`\exref`、`\eqref`、`\appref`、`\nameref` 展开为“第 12 章”“图 12.1”等文字并加链接；指向本册以外的引用只留文字（与分册 PDF 相同）。
   - 各种框（导引、直觉、例题、对照、案例、常见误区、深入一步、本章要点、自测、答案）改写为同名环境，pandoc 读成带类名的 Div；框的标题用 `\textsc{…}` 标出。对照框改成三列表格。
   - `\fig` 改为插入 `figures_zh/*.png`（`figsrc/build.py` 生成；缺失时自动重画）；`\datasource` 改为图下的来源行。
   - 带编号的公式（`keyeq`、`equation`、`align`）改为显示公式加编号；公式用 MathML。
   - 标签中的冒号换成连字符（XHTML 的 id 不允许冒号）：`ch:songming` → `ch-songming`。
   - 部分页取自 `zh/parts.tex`；附录 C 的对照与案例索引由本次转换收集，链接到各框。
3. **pandoc 生成 EPUB 3**：一部分、一章各成一个文件，目录到节；Lua 过滤器 `tools/epub/boxes.lua` 把 Div 变成带标题的框、把公式编号放在右侧；样式表 `tools/epub/epub.css` 的颜色在生成时从 `preamble.tex` 的 `\definecolor` 读出，深浅按 xcolor 的 `颜色!百分比` 规则换算，所以框的颜色与 PDF 相同。封面由 `tools/epub/cover.py` 按扉页（`zh/front_titlepage.tex`）的文字与版式画出。
4. **可复现**：书的标识符由文件名确定（UUID v5），EPUB 内的时间戳取最近一次 git 提交的时间（`SOURCE_DATE_EPOCH`），同一提交两次生成的文件相同。

## 写作时要注意的事

- 带编号的公式、图、表、例题都要有 `\label`；没有标签的带编号公式在 EPUB 里没有编号（脚本会警告）。
- 正文不要用 `\textsc` 与 `\underline`：转换器用 `\textsc` 标记框标题。
- 新增宏或环境时，同时在 `build_epub.py` 的 `Converter` 里说明怎样改写，并用 `--check` 检验；`validate_source.py` 不检查 EPUB。
- 看效果：解开 EPUB，用浏览器打开 `EPUB/text/*.xhtml`，或用任何阅读器（Apple Books、Calibre、Thorium）。阅读器自选字体，EPUB 不内嵌字体。

## 已知限制

- 阅读器对 MathML 的支持不一：Apple Books、Thorium、Calibre 支持；部分 Kindle 与旧版阅读器不支持。
- 页码引用（`\pgref`）在 EPUB 里改为“此处”加链接。
- 图是 PNG（220 dpi），不随阅读器的字号缩放图中文字。
