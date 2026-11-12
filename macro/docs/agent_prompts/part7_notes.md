# Part 7 (第七部分 滞胀与预期革命，1968—1985 年): notes for the chapter writers

Parts 1–6 are written and reviewed, so Part 7 is written against them. Chapters 44–52 are written one
at a time in that order (docs/WORKFLOW.md, sequential mode), each reviewed by one independent reviewer
before the next; the editor collects the next chapter's sources while the previous one is written (the
author, 2026-11-12: “可以在前一章写作时收集下一章资料”) and saves them as `docs/agent_prompts/chNN_research.md`.
Give the writer `batch_brief.txt` plus its section below. Sections are added when each chapter is started;
until then the neighbours named below divide the ground.

Part 7 is where inflation and unemployment rose together and the theory changed under the pressure of the
data: the natural rate, monetarism, rational expectations and credibility, alongside floating exchange
rates, the oil shocks, Latin America's debt crisis and hyperinflation. Its evidence is of three kinds:

- **Official documents.** US government papers (the *Economic Report of the President* and its statistical
  tables on GovInfo, FOMC records and the *Federal Reserve Bulletin*, FRUS: public domain), UK papers
  (Hansard, Open Parliament Licence v3.0; budget documents and white papers, Open Government Licence v3.0
  where the page says so), Japanese statistics (e-Stat and the Statistics Bureau: 政府標準利用規約 第2.0版,
  numbers free, the source named, processed figures marked “を加工して作成”), central-bank publications
  (Bank of Japan: credit "Bank of Japan"; Bank of England; Deutsche Bundesbank: copy the reproduction notice
  verbatim). Prefer the original table to a later transcription.
- **Contemporary and later scholarship.** Friedman, Phelps, Modigliani, Okun, Lucas, Sargent, Kydland and
  Prescott, Barro … and the historians after them are in copyright: short phrases only, otherwise paraphrase
  with `% 据:` anchors. NBER papers: the © notice exactly as printed. Nobel lectures: © The Nobel Foundation,
  short phrases. Brookings Papers: short phrases (terms as recorded for Ch 39). Cite the version read
  (STYLE.md §3).
- **Modern data.** The ERP tables, the BoE millennium workbook, e-Stat, Maddison 2023 and PWT 10.01 (CC BY
  4.0), WDI (CC BY 4.0). Do not use FRED or ALFRED. Run `tools/probe_network.sh` first.

Earlier chapters own (refer back, do not retell):
- Ch 3: the Fisher relation; Ch 19: the quantity equation and Hume's short-run non-neutrality; Ch 25:
  Wicksell's natural rate of interest (`sec:wicksell-legacy`: the natural rate of unemployment shares only the
  adjective); Ch 32: whether flexible wages would restore full employment; Ch 33: IS–LM with the money wage
  given; Ch 38: the Phillips curve, Samuelson and Solow's menu, the macroeconometric models, the American
  record to 1969 and the promise that the menu drifts (`sec:phillips-legacy`); Ch 39: Modigliani; Ch 42–43:
  East Asia and the planned economies.

Later chapters own: Ch 53 onwards the Great Moderation, inflation targeting and the new consensus; Ch 62 the
moderation; Ch 74 inflation in the 2020s.

## Rules carried over from Parts 5 and 6 (every Part 7 chapter)

Everything under "Rules carried over from the rewrite of Chapter 26" and every "Carried over from the
editor's round on Chapter NN" section of `docs/agent_prompts/part5_notes.md` (Chapters 27–34) and of
`docs/agent_prompts/part6_notes.md` (Chapters 35–43), with part6_notes' "Rules carried over from Part 5",
applies to Part 7. Read them all before writing. Place names follow STYLE.md §3 (台湾、香港 without prefix).

## 第 44 章 `ch:naturalrate` 自然率与附加预期的菲利普斯曲线 (`zh/ch44_naturalrate.tex`)

A theory-and-test chapter. The guide question asks why the Phillips “menu” drifts. The theory is the
expectations-augmented Phillips curve and the accelerationist hypothesis: with adaptive expectations a rate of
unemployment held below the natural rate needs ever-rising inflation, and bringing inflation down costs
output. The test is the 1970s. Model chapters: zh/ch38_phillips.tex (the chapter it continues: the menu, the
models, the record to 1969; its ending and `sec:phillips-legacy` promise this chapter), zh/ch39_consumption.tex
(theory tested against data, debates ending “至今没有定论。”), zh/ch40_solow.tex (a model with a worked simulation
and a data test), zh/ch43_planned.tex (the chapter before; its ending hands over this chapter's question).

- Neighbours:
  - Earlier chapters own the items listed above; FORWARD_REFS rows point here from Ch 1 (crisis, theory,
    test), Ch 25 (the adjective “natural”), Ch 32 (flexible wages), Ch 33 (IS–LM joined to price and wage
    adjustment), Ch 38 (why the menu drifts) and any added by Ch 43: read each with its passage and keep it.
  - Later chapters own: Ch 45 monetarism (the money rule, Friedman and Schwartz, the monetary targets of
    1979–1982: a clause forward), Ch 46 the end of Bretton Woods and the controls of August 1971, Ch 47 the oil
    shocks and stagflation (the shocks as causes: this chapter uses the 1970s data as a test and names the
    shocks in a clause), Ch 48 rational expectations and the Lucas critique (this chapter stays with adaptive
    expectations; rational expectations a clause forward), Ch 49 credibility and the Volcker disinflation
    (the realized cost of 1979–1984 belongs there; this chapter simulates the cost and reports the estimates
    made before it, Okun 1978 through Gordon and King 1982), Ch 50 the budget constraint. Each at most a
    sentence.
- Owns:
  - the model: π = π^e − β(u − u*) (state the book's symbols and the sources'; one letter, one meaning),
    adaptive expectations π^e_t = π_{t−1}, the accelerationist result, the vertical long-run curve, and a
    worked disinflation with teaching inputs (unemployment held above u* until inflation falls by a set amount:
    the cumulative excess unemployment, the sacrifice ratio, and Okun's law if used, from a source);
  - the people and the claims: Friedman's AEA presidential address of 29 December 1967 (*AER* March 1968:
    the natural rate's definition, “natural” as Wicksell's, not “immutable”, the authority “cannot know” the
    rate) and his Nobel lecture of 13 December 1976 (three stages, Table 1, “stagflation”); Phelps (1967, 1968)
    only through Phelps (2006) and Friedman (1976) unless a copy is obtained, and Phelps's own claim that the two
    models are “two distinct phenomena”; Modigliani and Papademos (1975), NIRU, the source of the later NAIRU
    (compare box 自然失业率与 NAIRU: what each assumes, who used it, with the sources' words);
  - compare box 短期菲利普斯曲线与长期菲利普斯曲线 (PLAN);
  - the data test: the US unemployment and CPI inflation, 1960–1985, from the ERP 2000 tables; Friedman's seven
    countries 1956–1975; the UK from the BoE millennium workbook; Japan from the Labour Force Survey and the
    CPI (non-Anglo-American case box: Japan's inflation of 1973–1974 with unemployment that stayed low; what the
    natural-rate reading says and what it leaves out; who decided and who paid, from sources: the 1974
    white paper of the 経済企画庁 gives the causes in its own words (slower supply growth after the late 1960s,
    M2 growth of 21.9%, the oil shock), the Bank of Japan's five discount-rate rises to 9% and window guidance,
    and the burden on low-income households);
  - debates (each ending “至今没有定论。”): who found the vertical curve and whether it was the same idea
    (Friedman, Phelps); whether the natural rate is a constant, a slow-moving number, or not identifiable
    (Friedman's own reasons it rose, Modigliani–Papademos' composition adjustment); how large the cost of
    disinflation is (Okun's 6–18% with a mean of 10% against Gordon and King's “roughly half”).
- Who decided and who paid: name the policy-makers and what they chose where a source supports it (the
  Federal Reserve's and the government's choices in the late 1960s and 1970s; incomes policies; Japan's
  総需要抑制 of 1973–74); the cost of
  disinflation falls on the unemployed: say so with the sources' numbers.
- Data and sources: start from `docs/agent_prompts/ch44_research.md` (the editor's research, collected while
  Ch 43 was written; confirm every fact on the document). Terms: AEA (short phrases), the Nobel Foundation
  (short phrases), Brookings (short phrases), US government works (public domain), e-Stat (政府標準利用規約
  第2.0版, verbatim excerpts in the research note), the Bank of England (as recorded for Ch 38).
- Figures: the US inflation–unemployment scatter, 1960–1985, with the years labelled (the menu drifting); the
  simulated disinflation (unemployment, inflation, expected inflation over time); Friedman's Table 1 as a
  figure or table; Japan and the UK beside the US if the data allow.
- Ending: return to the opening and hand over Ch 45's question “控制货币数量就能控制通胀吗？” (read its stub's
  guide box and copy the question exactly).
- Labels: `sec:naturalrate-…`, `eq:naturalrate-…`, `fig:naturalrate_…`, `tab:naturalrate-…`, `ex:naturalrate-…`.
- Length: 8,000–9,000 characters of main text.
