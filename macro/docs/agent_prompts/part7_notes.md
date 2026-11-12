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

### Carried over from the editor's round on Chapter 44

- Check every point a sentence sums up. “这些点都不在那张菜单上” was wrong for 1967, which lies on Samuelson and
  Solow's line. The check script now measures each point's distance from the line.
- A compare box's one-line summary states the condition under which two ideas coincide. The natural rate and
  the NIRU name the same point only if the long-run curve is vertical; the NIRU's definition does not need it.
- When a source says “One problem is…” and then “But the basic problem is…”, give the basic problem. Friedman's
  main objection to a natural-rate target is that even a known natural rate gives no determinate policy.
- Date a model as its author does. Phelps's note 13 says the passage fuses his 1968 paper with Phelps and Winter
  (1970): write “从 1968 年起建的几个模型”, not “1968 年的模型”.
- Who paid: when the source says the burden was greater for a group (“より大きな影響”), write “代价更重地落在……”,
  not “付代价的是……”.
- A learning goal is a promise. If the guide asks why Phelps predicted a vertical curve, the chapter gives
  Phelps's own reason (the velocity shock, neutral once expectations are correct), not only Friedman's.
- A debate on cost gives the other side's argument. Gordon and King's discussion has Fellner's credibility
  objection, Gordon's reply and several participants' view that steadfast disinflation could change
  expectations: report it, without taking Ch 49's subject.
- Explain a technical step in the source's own terms (“把国际变量当作外生” = cutting the channels of import
  prices, food and energy prices and the exchange rate).
- Say which version of a series a caption plots: B-62 has year-to-year and December-to-December columns, and
  they differ (1975: 9.1 against 6.9). State whether annual-average or December levels are used.
- Key terms in bold with the English at first definition (STYLE.md §3). Ch 44 now does this for 自然失业率,
  附加预期的菲利普斯曲线, 适应性预期, 加速论 and 牺牲率.
- Report a test where the source reports it: “据 Gordon 与 King 的注”, when the test is only in their footnote.
- Shared bibliography items (`friedman1976`, `boe2017`, …): the writer asks in a comment and the editor merges
  the chapter's pages and hashes into the shared item; the check script then reads the shared item, not a
  comment in the chapter's block.

## 第 45 章 `ch:monetarism` 货币主义 (`zh/ch45_monetarism.tex`)

A theory-and-practice chapter. The guide question asks whether controlling the quantity of money controls
inflation. The theory is the monetarist case: a stable demand for money (velocity predictable), a rule of steady
money growth, money neutral in the long run. The practice is the money targets of 1975–1999 and their retreat:
the Federal Reserve's new operating procedure of 6 October 1979 and its loosening in 1982, the Medium-Term
Financial Strategy of March 1980 and the end of the £M3 target in March 1987, Canada's M1 target (1975–1982),
and, as the non-Anglo-American cases the PLAN names, the Bundesbank (1975–1998) and the Swiss National Bank
(1975–1999). Model chapters: zh/ch44_naturalrate.tex (the chapter before; its ending hands over this
chapter's question; it already uses Friedman's 1968 address for the natural rate), zh/ch28_depressionus.tex
(Friedman and Schwartz on 1929–33, the compare box 萧条从哪里来: do not repeat it), zh/ch38_phillips.tex and
zh/ch39_consumption.tex (theory tested against data, debates ending “至今没有定论。”).

- Neighbours:
  - Earlier chapters own: Ch 4 the money multiplier and the central bank's balance sheet (`eq:money-mult`, and
    its legacy item 乘数与货币主义), Ch 8 “more money, higher prices”, Ch 13 the quantity theory from Bodin to
    the twentieth century, Ch 19 the equation of exchange and its conditions (whether velocity is stable), Ch 25
    Wicksell's cumulative process (pegged interest rates), Ch 28 Friedman and Schwartz on the Great
    Contraction, Ch 33 1937–38 and IS–LM, Ch 38 the Phillips menu, Ch 44 the natural rate and the
    accelerationist hypothesis. Point back; do not re-derive. FORWARD_REFS rows point here from Ch 4, 8, 13, 19
    and 44 (Ch 44's ending: Friedman's prescription of 1967, money demand standing between money growth and
    inflation, and Modigliani and Papademos (1975) blaming the Fed's money-aggregate targets and "orderly
    markets" for the squeeze of 1974): read each with its passage and keep it.
  - Later chapters own: Ch 46 the end of Bretton Woods, floating and the snake (the Swiss exchange-rate target of
    October 1978 is a clause here), Ch 47 the oil shocks, Ch 48 rational expectations and the Lucas critique
    (Goodhart's law is a cousin: a clause forward), Ch 49 credibility and the Volcker disinflation (the interest
    rates of 1979–1984, the recession and its cost belong there: this chapter tells the operating procedure, the
    targets and the outturns), Ch 50 the budget constraint (the PSBR side of the MTFS: a clause), Ch 55 the new
    consensus, the Taylor rule and inflation targeting (what replaced money targets: a clause). Each at most a
    sentence.
- Owns:
  - the propositions in their authors' words: Friedman and Schwartz, “Money and Business Cycles” (1963, read in
    the NBER volume of 1965): the six major declines in the money stock since 1867 and the six major contractions
    (p. 34), the “necessary and sufficient condition” claim, long-period changes showing up mainly in prices (pp.
    53–54), the two tests a rival explanation must meet, and Minsky's comment in the same volume; Friedman's
    rule (*AER* 1968, pp. 15–16: a monetary total as the guide, “a steady rate of growth in a specified monetary
    total”, 3 to 5 per cent for his broad total); the growth-rate form of the quantity equation (m + v = π + y,
    from Ch 19's identity) with a worked example that sets a money target the way the Bundesbank did (trend
    output growth, a normative inflation rate, the velocity trend: Gerberding, Worms and Seitz 2004, pp. 19–20);
  - compare box 货币目标与利率目标 (PLAN): Poole's rule in Poole's own summary (Poole and Lieberman 1972, pp.
    296–297: real disturbances favour a money target, monetary disturbances an interest-rate target); a worked
    example solving the small IS–LM of their equations (1)–(5) under each instrument with teaching variances;
    Goldfeld (1976) applying it to the “missing money”;
  - the practice, each with who decided and the record: the FOMC of 6 October 1979 (the vote by name, the
    reasons in the Record of Policy Actions, the 11½–15½% funds-rate band, the discount rate and marginal
    reserve requirement), the 1981 outturn (M1-B below, M2 and M3 above their ranges) and October 1982 (“much less
    than the usual weight”); the UK from Howe's budget statement (26 March 1980: “at the heart of what
    "monetarism" means in practice”, £M3 7–11%) through the Bank's March 1981 commentary (the overshoot), the
    Governor's Loughborough lecture (22 October 1986: velocity of broad money falling 4% a year; the marksman)
    and Lawson's budgets (18 March 1986: the range raised to 11–15%; 17 March 1987: “eschew an explicit target
    altogether”); Canada (Bouey, 29 November and 8 December 1982; the line “We didn't abandon M1, M1 abandoned
    us” is NOT in either document: do not use it unless a primary record is found);
  - Goodhart's law, quoted through Moses (1983, RBA RDP 8301, p. 1 n. 1) with Goodhart (1975, p. 5) as the
    original (not read); not the later “when a measure becomes a target” wording (Strathern 1997);
  - the data: US M1 and nominal GDP from ERP 2000 Tables B-67 and B-1 (public domain): M1 velocity rising about
    3% a year to 1981, then breaking in 1982 and 1985–86 (the writer recomputes in the check script and states
    whether velocity uses December or average M1); targets against outturns for the Bundesbank (Gerberding et
    al., Table 10, p. 44, read on the page image) and the SNB (Rich 2003, Table 1, p. 18, read on the page image);
    the UK targets and outturns from the budget statements and the Quarterly Bulletin;
  - case box(es), non-Anglo-American: Germany and Switzerland: targets announced every year, missed often (the
    Bundesbank 7 times of 20, six of them above; the SNB 1978 by over 10 points under an exchange-rate target)
    and kept for two decades; why each kept them and how each ended (the euro in 1999; the SNB's switch to
    inflation forecasts at the end of 1999);
  - debates (each ending “至今没有定论。”): whether Friedman and Schwartz's timing shows that money causes income
    (their two tests; Minsky's reply); whether the money targets failed because money demand shifted (financial
    innovation, deregulation: the sources' own reasons) or because they were never really kept (the Bundesbank's
    misses; the Fed's retreat; give each side only as a source states it); whether Goodhart's law dooms any
    intermediate target.
- Who decided and who paid: name the decision-makers from the records (the FOMC members who voted on 6 October
  1979; Howe and Lawson as Chancellors; the Governors Leigh-Pemberton and Bouey; the Bundesbank's Council and the
  SNB's Directorate as the sources name them). Who paid: borrowers and the unemployed in the tightening, exporters
  under a rising currency (Switzerland 1978): say so only with the sources' words and numbers; the realized cost
  of 1979–1984 is Ch 49's.
- Data and sources: start from `docs/agent_prompts/ch45_research.md` (the editor's research, collected while
  Ch 44 was written; confirm every fact on the document). Terms: US government works (public domain: FOMC
  records, ERP); Hansard (Open Parliament Licence v3.0, verbatim attribution line); the Bank of England (legal
  page: numbers and short phrases with the source named, no reproduced charts); the Bank of Canada (attribute
  and indicate changes); the Bundesbank (“Reproduction permitted only if source is stated.”); the ECB working
  paper (reproduction for educational and non-commercial purposes with the source acknowledged); the RBA (CC BY
  4.0 with its attribution form; Goodhart's sentence is third-party: one short quotation); the AEA, Brookings
  and the NBER volume (short phrases only).
- Figures: US M1 velocity 1959–1999 with 1979, 1982 and 1986 marked; targets against outturns (the Bundesbank
  and the SNB side by side, and the UK's £M3 ranges if the numbers allow); the instrument example (output
  variance under each instrument as the share of monetary disturbances rises).
- Ending: return to the opening and hand over Ch 46's question “美元与黄金为什么脱钩？浮动汇率为什么会“超调”？”
  (read its stub's guide box and copy the question exactly).
- Labels: `sec:monetarism-…`, `eq:monetarism-…`, `fig:monetarism_…`, `tab:monetarism-…`, `ex:monetarism-…`.
- Length: 8,000–9,000 characters of main text.

### Carried over from the editor's round on Chapter 45

- Use the book's notation. Appendix B keeps the star for the neutral rate, and lower-case $y$ means the output gap
  from Ch 44 on. Ch 45's growth-rate quantity equation therefore takes Ch 13's $g_M$, $g_V$, $g_Y$, with a
  superscript T for targets and a bar for trends. $v$ stays with Poole's money-demand disturbance.
- A summary of a source's numbers covers only the years the source explains. Rich ties only the 1988 undershoot to
  the new payment system. The 1989 miss was half a deliberately tighter course, and 1990 was mainly a tighter
  course. Give each year its own cause, and keep figure labels to the same years.
- A parliamentary aside is not a scene. “—Opposition Members may laugh—” is Howe's own words in mid-sentence; the
  record has no laughter.
- When an institution stops doing something, say why, with a source: the Bundesbank's targets end because Stage
  Three of EMU began on 1 January 1999 (the ECB's EMU history page). Do not leave “the sources do not say” when a
  primary page says it.
- In a debate, each side is argued from the record of every country it concerns. “The targets were never really
  kept” needs the US (two of the three dissenters of October 1982 wanted firmer restraint) and the UK (most
  targets missed, the range raised in 1986), not only the Bundesbank.
- A learning goal that names a government (撒切尔政府) must be met in the text: name the head of government, with
  dates from an authority record.
- Use a speech's own name for a policy (“the medium-term financial strategy”), not a paraphrase that sounds like a
  different policy.
- When two chapters give different numbers for the same event (28: 30.9%; 45: 35.2%), say in the text what each
  measures.
- State the vintage and the measure when two series differ: the FOMC's real-time, shift-adjusted M1-B against the
  ERP 2000 revised M1; a month's year-on-year inflation against an annual average.
- Who paid includes who the speaker blames: Bouey puts the costs down to inflation having been allowed to get out
  of hand.
- STYLE.md §7.1 applies to teaching figures too: a panel's second series is AMBER, dashed, with squares.
