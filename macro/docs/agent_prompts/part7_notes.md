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

## 第 46 章 `ch:floating` 布雷顿森林解体与浮动汇率 (`zh/ch46_floating.tex`)

A history-and-theory chapter. The guide question asks why the dollar was cut loose from gold and why floating
exchange rates “overshoot”. The history runs from the closing of the gold window on 15 August 1971 through the
Smithsonian agreement (18 December 1971), the snake (April 1972) and the second devaluation (February 1973) to
general floating (March 1973) and its legal acceptance at Jamaica (January 1976). The theory is Dornbusch's
overshooting model (1976). The test is how floating rates behaved: far more volatile than prices, and (Meese and
Rogoff 1983) no better forecast by the models than by a random walk. Model chapters: zh/ch36_brettonwoods.tex (the
system to 15 August 1971; its legacy hands the break-up on: do not retell Triffin, the gold pool or its debates),
zh/ch37_mundell.tex (the open-economy IS–LM, Canada's float, the trilemma: point back), zh/ch05_external.tex (the
real exchange rate `eq:external-real`, PPP `eq:external-ppp`, UIP `eq:external-uip` and its failure: reuse, do not
re-derive), zh/ch45_monetarism.tex (the chapter before; its ending hands over this chapter's question), and
zh/ch38_phillips.tex / zh/ch44_naturalrate.tex for a model tested against data.

- Neighbours:
  - Earlier chapters own: Ch 5 the exchange-rate definitions, PPP, UIP and the forward-premium puzzle
    (`sec:external-rates`, `sec:external-test`); Ch 23 the gold standard; Ch 36 Bretton Woods to 15 August 1971
    (the par values, the gold pool, the two-tier market, the mark's floats of 1969 and May 1971, the debate 缺陷在设计还是
    在美国的政策 and whether surplus countries should adjust); Ch 37 Mundell–Fleming, Canada 1950–1962 and the debate
    whether Canada's float was a success; Ch 42 Japan's 360 yen and its high growth; Ch 45 the money targets of
    1975–1999, the SNB and the Bundesbank. FORWARD_REFS rows point here from Ch 5, 36, 37, 42 and 45: read each with
    its passage and keep it (Ch 37: Canada's float of the 1950s as the precedent, and overshooting with slow prices
    and rational expectations; Ch 42: the yen's move to floating closing the single-rate years; Ch 45: the Swiss
    exchange-rate target of October 1978 told here).
  - Later chapters own: Ch 47 the oil shocks (OPEC's prices and the petrodollars: a clause at the end), Ch 48 rational
    expectations (Dornbusch's “consistent expectations” are perfect foresight: say so and point forward, do not
    teach rational expectations here), Ch 49 the Volcker disinflation (the dollar's rise of 1980–1985 at most a
    clause), Ch 58 the Plaza agreement and Japan's bubble, Ch 60 the European Monetary System of 1979 and the euro,
    Ch 61 emerging-market crises, the hierarchy chapter (the dollar's role). Each at most a sentence.
- Owns:
  - the decision of August 1971, from the records: the Camp David meeting of 13–15 August (who was there by the
    President's Daily Diary; State and the NSC not represented; Connally as the architect of the package in the
    tapes of 2 August; Burns's lonely attempt to keep the gold window open as the FRUS editor summarizes Haldeman's
    notes; Stein's recollection that it was unclear whether closing the window meant floating); the address of
    Sunday 15 August, 9 p.m. (its words on convertibility, “devaluation” and the surcharge); the BIS's account of
    the run that preceded it (the 1970 deficit, the opposite monetary policies of 1969–1970, the congressional
    sub-committee report of 6 August);
  - the Smithsonian agreement and its collapse: Connally's G-10 package of 30 November (the 11% demand), the US
    projection of a $13 billion swing against the IMF–OECD $9 billion, the realignment table (a table in the
    chapter: BIS 1972's “Realignment of leading currencies”, with the source and its notes), Nixon's “most significant
    monetary agreement in the history of the world”, the wider margins, sterling's float of June 1972, the February
    1973 devaluation, the joint float of March 1973 (the date discrepancy among the sources: say so), Kissinger's
    political reasons as FRUS quotes him, Jamaica (BIS 1976);
  - the model: Dornbusch (1976) in the book's notation (Appendix B: $e$ the home-currency price of foreign
    currency, $q$ the real rate, $i^{f}$ the foreign interest rate, $P^{f}$, $\E_t$; logs in lower case only if
    the text says so once and keeps it; give Dornbusch's own symbols in a sentence): UIP, regressive expectations
    that are consistent with the model's own path (perfect foresight), money-market equilibrium with the price level
    fixed in the short run, slow price adjustment; the long run (PPP and money neutrality, back to Ch 5 and Ch 45),
    the impact of a money increase and the overshooting result (the exchange rate jumps by more than the money
    increase, by the factor $1+1/(\lambda\theta)$ in Dornbusch's symbols), then appreciation while prices rise; the
    variable-output case that dampens it (Part V) in a sentence. A worked example with teaching inputs (state them)
    and a figure of the time paths of $e$, $p$ and $i$ after a money increase;
  - compare box 固定汇率下的调整与浮动汇率下的调整 (PLAN): who moves (reserves and money stock under a peg, the exchange
    rate under a float), how fast, who bears it, with the chapter's own cases;
  - case boxes, non-Anglo-American (PLAN): 日本 · 1971—1973 · 360 日元的终结 (the Bank of Japan's history and the
    1972 white paper: the market kept open by the Finance Minister's decision, nearly $4 billion bought in 11 days,
    the float of 28 August, 308 yen at the Smithsonian, the float of February 1973; who paid: the reserves bought at
    the old rate, exporters and the small export districts that cut piece rates and lengthened hours; Sasaki's
    later view as the history reports it); 欧洲 · 1972—1976 · 蛇形浮动 (the Council resolution of 21 March 1972 in
    the Official Journal, the snake in the tunnel from 24 April 1972, who joined and who left when, the joint float,
    the EMCF; the Swiss franc's float of January 1973 and the SNB's exchange-rate target of October 1978 through Rich
    2003, the story Ch 45 left here). The EMS of 1979 is Ch 60's: a clause;
  - the data test: monthly exchange rates and consumer prices from the BIS Data Portal (bilateral rates against
    the dollar, long CPI series): the volatility of monthly changes in the nominal and the real rate (Ch 5's $q$)
    against that of relative prices, before (1960–1970) and after (1974–1985) the break, computed in the check
    script and stated as the book's computation; Meese and Rogoff's finding in their words (short phrases) and
    their Table 1; what the overshooting model can and cannot explain of the pattern;
  - debates (each ending “至今没有定论。”; not the Ch 36 or Ch 37 debates): candidates, chosen by what the sources
    support: why the Smithsonian rates lasted only fourteen months (rates not moved enough, the US not adjusting,
    the speculation the wider margins invited: the BIS 1973, the Bank of Japan's history, the FRUS records); whether
    the overshooting model explains floating-rate volatility (Dornbusch's claim against Meese and Rogoff, and the
    reasons the IFDP gives for unstable structure); whether floating rates should be managed (the US policy of
    non-intervention and Kissinger's aims in March 1973; the G-10's agreement of 16 March that floating could be
    managed by intervention; why other countries would not let their currencies float freely in 1971, BIS 1972;
    Switzerland's return to an exchange-rate target in 1978). Give each side only as a source states it.
- Who decided and who paid: name the decision-makers from the records (Nixon, Connally, Shultz, Burns and Volcker
  at Camp David; the G-10 ministers and governors; Japan's Finance Minister Mizuta and Governor Sasaki; the
  Council and governments of the Six; Aichi in 1973); who paid: the trading partners hit by the 10% surcharge, the
  central banks that bought dollars at the old rates (Germany, Japan, Switzerland: the BIS figures), Japan's small
  exporters and their workers (the 1972 white paper), exporters under a rising currency (the BIS 1972 on political
  opposition from exporters). Say so with the sources' words and numbers, no stronger than the sources.
- Data and sources: start from `docs/agent_prompts/ch46_research.md` (the editor's research, collected before the
  writer started; confirm every fact on the document). Terms: US government works (FRUS, the Public Papers via the
  American Presidency Project: public domain); the BIS (publications: limited extracts with the BIS cited and the
  translation statement; statistics: the Data Portal's terms, verbatim); the Bank of Japan (source “Bank of
  Japan”; its history: short phrases); the Cabinet Office (as for Ch 44); EUR-Lex (Decision 2011/833/EU,
  acknowledge the source); Dornbusch (JPE, © University of Chicago) and Meese–Rogoff (JIE, © North-Holland) read in
  third-party copies, to verify only, never committed, short phrases; the IFDP's cover note on references.
- Figures: exchange rates of the yen, the mark, the Swiss franc and sterling against the dollar, monthly, 1965–1985
  (index or log scale, with 15 August 1971, 18 December 1971 and 19 March 1973 marked); the overshooting paths
  (teaching model); the volatility comparison (nominal, real and relative prices, before and after).
- Ending: return to the opening and hand over Ch 47's question “油价冲击为什么同时推高通胀和失业？产油国为什么会被“资源诅咒”？”
  (read its stub's guide box and copy the question exactly). A link to oil (OPEC's prices were set in dollars) only
  with a source, or marked 本书的解读.
- Labels: `sec:floating-…`, `eq:floating-…`, `fig:floating_…`, `tab:floating-…`, `ex:floating-…`.
- Length: 8,000–9,000 characters of main text.

### Carried over from the editor's round on Chapter 46

- A takeaway or an ending says no more than the body. “The decision was made at Camp David” was wrong by the chapter's
  own story (the programme was agreed on 2 and 12 August; FRUS says Camp David was to detail it); “the dollar did not
  buy less” was the book asserting Nixon's claim against the BIS's own words on import prices. Re-read the takeaways
  and the ending against the sections before finishing.
- When a secondary source and a primary document disagree on a date, find the primary (the statute, the decree, the
  minutes) and follow it; name the other date in the 史料说明. The BIS printed 3 April 1972 for a law approved on
  31 March.
- Two sources that seem to disagree may describe the same rule in two ways (±1.125% from a common midline is at most
  2.25% between any two currencies). Work it out before calling it a discrepancy.
- A data artefact that drives a computed result belongs in the main text, in a clause, where the result is stated
  (the yen recorded at its parity for ten years; the UK CPI's coarse rounding), not only in the 史料说明.
- Watch sentences that state the opposite of what is meant (“央行不必等汇率离开中心 1% 就入市”); read each 本书的解读
  sentence once for its direction.
- A figure that marks a point the text does not mention: say it in the text or leave the mark out.
- A chapter's pages in a shared bibliography item go into that item as “第 NN 章另用第 … 页（PDF 第 … 页）”, after the
  earlier chapters' pages, so that every chapter's check still finds its own pages.

## 第 47 章 `ch:oil` 石油危机与滞胀 (`zh/ch47_oil.tex`)

A history-theory-and-test chapter in two halves. The guide question asks why an oil shock raises inflation and
unemployment together, and why oil producers fall under a “resource curse”. The first half is the importers' side:
the shocks of 1973–1974 and 1979–1980, the supply shock in Ch 44's Phillips curve, and the choice to accommodate or
resist. The second half is the producers' side: where the money went (petrodollar recycling, a hand-over to
Ch 51), Corden and Neary's model of the Dutch disease, and whether the resource curse is real. Model chapters:
zh/ch44_naturalrate.tex (the expectations-augmented curve `eq:naturalrate-curve`, the accelerationist form
`eq:naturalrate-accel`, the sacrifice ratio `eq:naturalrate-sacrifice` and Okun's law `eq:phillips-okun`: extend
them, do not re-derive), zh/ch05_external.tex (the real exchange rate `eq:external-real`), zh/ch46_floating.tex
(the chapter before; its ending hands over this chapter's question), zh/ch41_development.tex and
zh/ch40_solow.tex (growth regressions with PWT and WDI: the data-test machinery), and zh/ch45_monetarism.tex for a
case box built on a central bank's own history.

- Neighbours:
  - Earlier chapters own: Ch 5 the real exchange rate and the current account; Ch 13 Spain's dependence on silver
    revenue (its row points here: governments that live on a volatile revenue from under the ground); Ch 7 Athens'
    Laurion windfall (share it out or invest it: its row points here); Ch 38 the word “stagflation” and the drift of
    the menu; Ch 42 Japan's high growth to 1973 (its row: the oil shock as the end of high growth, 3% a year against
    8.9%: keep Ch 42's numbers as Ch 42 states them); Ch 44 the 1970s test, Friedman's (1976) view that the oil
    crisis alone cannot explain the rise of inflation and unemployment, and Gordon and King's (1982) sacrifice ratio
    (`gordon1982`: a different paper from Gordon 1975); Ch 45 the money targets, the Bundesbank's from December 1974
    and the SNB's, and Switzerland's output fall of 7.5% in 1975 (Rich 2003); Ch 46 the end of Bretton Woods and
    general floating from March 1973 (OPEC's prices were set in dollars: say so only with a source). FORWARD_REFS
    rows point here from Ch 7, 13, 38, 42, 44, 45 and 46 (Ch 46's ending: the Bank of Japan's remark that oil
    producers holding dollars were likely to sell them): read each with its passage and keep it.
  - Later chapters own: Ch 48 rational expectations (the ending hands over); Ch 49 the Volcker disinflation of
    1979–1982 and the Bundesbank's credibility (1979 here only as the second shock; Volcker in a clause); Ch 50 the
    budget constraint; Ch 51 Latin America's debt crisis (the syndicated loans, floating rates and Mexico 1982: here
    one paragraph on recycling and the BIS's warning of 1980, no more); Ch 53 real business cycles (oil as a
    technology shock: at most a clause); Ch 55 supply shocks in the three-equation model; Ch 62 the oil exporters'
    surpluses of the 2000s; Ch 74 the energy shock of 2021–2023; Ch 78 supply shocks and “looking through” them.
    Each at most a sentence.
- Owns:
  - the first shock, from the records: the war of 6 October 1973 and the WSAG's view of an embargo (FRUS); the Gulf
    producers' posted-price decision of 16 October and OAPEC's production cuts of 17 October (“not less than 5% a
    month”), the embargo on the United States and the Netherlands, the November cut of 25%; the Tehran price of 23
    December; the scale (Hamilton's 7.5% of world output; the BIS's “take” of $1.75 → $7; the CIA's and the BIS's
    estimates of the importers' extra bill and its size relative to GNP). The price numbers differ among the sources
    ($5.11 or $5.12; $11.65 or $11.60): say which source gives which, or round with a footnote;
  - the model: add a supply-shock term to Ch 44's curve ($\pi_t=\pi^{e}_t-\alpha(u_t-u^{n})+\varepsilon_t$ as written, not $s_t$: Appendix B's $s$ is the primary surplus; or the form the
    writer derives; say it is the book's extension and why: a rise in the real price of an imported input raises
    firms' costs at a given unemployment), and a demand side that policy controls (Gordon's nominal-income growth, or
    Ch 44's own devices). Show the two extreme policies: hold nominal demand (inflation rises on impact, unemployment
    rises, then both return as the shock passes) and accommodate fully (unemployment unchanged, inflation higher
    and, with adaptive expectations, it stays higher: Gordon's “permanent” case). The terms-of-trade loss (a tax paid
    to the producers, BIS 1980; about 3% of GNP for Europe and Japan, the CIA in January 1974, and Japan's 3% of GNE,
    the Bank of Japan): why no policy can restore the real income lost. A worked example with teaching inputs
    (state them) and a figure of the paths under the two policies;
  - compare boxes (PLAN): 需求冲击 vs 供给冲击 (the sign of the comovement of inflation and unemployment; what a
    monetary contraction does to each); 迁就 vs 不迁就 (BIS 1980's own sentence on accommodation and resistance and
    Gordon's conclusions, with the countries that did each, from the BIS 1980 statement that most countries chose to
    support demand in 1973–74);
  - the countries' responses and results (goal 2): inflation and growth in the G7 and Switzerland, 1970–1985, with
    both shocks marked (WDI consumer prices, PWT 10.01 growth: WDI's 1970s growth rates for Switzerland and Japan are
    unreliable, see ch47_research.md); what the BIS says each did in 1973–74 and in 1979–80; no ranking beyond what
    the numbers and the BIS support;
  - case box, non-Anglo-American (PLAN): 日本 · 1973—1980 · 两次石油危机 (the Bank of Japan's history: the 2-point
    discount-rate rise of 22 December 1973, 狂乱物价 and its origin in Fukuda's words of 12 January 1974, the run on
    the Toyokawa credit union, wholesale prices +37% and the first negative growth since 1947, the wage round of
    1974; then the second shock: the 予防的 stance of 1979 against the money growth of 1971–72, and the outcome;
    who paid: households and wage earners in 1974, the unemployed);
  - petrodollar recycling (goal 3): OPEC's current surplus of about $70 billion in 1974, its placement (the BIS:
    dollar and sterling reserves, the bulk in the Euro-currency market, US banks' loans), the non-oil developing
    countries' deficit; BIS 1980's warning that recycling would be harder the second time and that the banks were
    already burdened with third-world risks. Hand over to Ch 51 in a sentence, with the PLAN's words (浮动利率银团贷款,
    1982 年墨西哥): do not tell the debt crisis;
  - the model of the Dutch disease (goal 4): Corden and Neary's three sectors (a booming energy sector and
    manufactures, both traded at world prices, and non-traded services), the real exchange rate as the relative price
    of non-traded to traded goods (relate it to Ch 5's $q$ in a sentence; do not reuse $q$ for it), the
    resource-movement effect and the spending effect, direct and indirect de-industrialization. Paraphrase only (the
    IIASA paper's cover forbids quotation without permission), set it up in the book's own notation with a worked
    example and a figure or a table of the two effects;
  - case boxes, non-Anglo-American (PLAN): 荷兰 · 1959—1982 · 格罗宁根的天然气 (the Slochteren field of 1959,
    Hutchison's BIS paper, WDI's manufacturing share and fuel exports; Hutchison's conclusion as he states it: for
    the Netherlands little systematic, long-term harm to manufacturing, the effects early, episodic and transitory) and 尼日利亚 · 1970—1985 · 石油繁荣 (WDI's export composition:
    fuel 58% → 93% of merchandise exports, food and raw materials down to a few percent; Budina, Pang and van
    Wijnbergen on spending volatility and debt overhang: the windfall spent by 1976, capital spending six times its
    1970 level, debt and reserves 1980–83). Who paid: as the sources say; a claim about farmers or workers needs a
    source that says it;
  - the data test (goal 4): does resource dependence predict slower growth, and does the answer depend on the
    period? Resource rents (WDI, % of GDP, measured at the start of each window) against PWT growth per head with
    log initial income, for 1970–1990 and 1990–2019, computed in the check script and stated as the book's
    computation; set against Sachs and Warner's coefficient (their Table 1; one standard deviation is about 0.9
    points a year) and against the counterexamples (Botswana, Norway, Malaysia). State the sample, mark the Gulf
    states, and say what a cross-country regression cannot show (causality, the quality of institutions);
  - debates (each ending “至今没有定论。”): whether oil caused the Great Stagflation (Barsky and Kilian's monetary
    alternative against Hamilton's record of shocks and recessions; Bernanke, Gertler and Watson on the monetary
    response; Blanchard and Galí's four reasons why the 2000s differed); whether the resource curse is real and what
    carries it (Sachs and Warner; Mehlum, Moene and Torvik's institutions; Budina et al.'s volatility and
    Hutchison's weak evidence against the Dutch disease as the channel). Give each side only as a source states it.
- Who decided and who paid: name the decision-makers from the records (the OAPEC ministers in Kuwait on 17 October
  1973 and King Faisal and Yamani as FRUS names them; the Shah at Tehran on 23 December; Nixon and Kissinger;
  Japan's Finance Minister Fukuda and the Bank of Japan's Policy Board and governors, Sasaki and Morinaga, with dates
  from an authority record; the BIS's “main industrial countries”); who paid: the importers' consumers (the
  terms-of-trade “tax”), the non-oil developing countries (the BIS's deficits; India's plan in the Shah's words as
  Helms reports them), Japan's households and wage earners in 1974, the unemployed of 1974–1975 and 1980–1982 in the
  importing countries, and in Nigeria those the sources name. No stronger than the sources.
- Data and sources: start from `docs/agent_prompts/ch47_research.md` (the editor's research, collected while Ch 46
  was written; confirm every fact on the document). Terms: US government works (FRUS: public domain); the BIS
  (publications: limited extracts with the BIS cited and the translation statement); the Bank of Japan (source
  “Bank of Japan”; its history: short phrases); NBER working papers (the © notice exactly as printed, short
  sections); Brookings Papers (short phrases); the IIASA paper (no quotation); the Oslo memorandum (no licence:
  short phrases); the World Bank PRWP (CC BY 3.0 IGO) and the Pink Sheet and WDI (CC BY 4.0); PWT 10.01 (CC BY 4.0,
  its citation).
- Figures: the real and nominal price of crude oil, 1960–2024 (Pink Sheet; 1973–74 and 1979–80 shaded); inflation
  and growth of the major countries, 1970–1985; the teaching model's paths under accommodation and non-accommodation;
  the Dutch-disease effects; the data-test scatter for the two windows; Nigeria's export composition if it adds to the
  text.
- Ending: return to the opening and hand over Ch 48's question “人们会预期政策时，政策还有效吗？用历史数据估计的模型，为什么会在
  政策改变后失效？” (read its stub's guide box and copy the question exactly). A link from the shocks to rational
  expectations (the models of the 1960s failed in the 1970s) only with a source, or marked 本书的解读.
- Labels: `sec:oil-…`, `eq:oil-…`, `fig:oil_…`, `tab:oil-…`, `ex:oil-…`.
- Length: 8,000–9,000 characters of main text (two halves: keep each to its goals; the history of the embargo is
  context, not the chapter).

### Carried over from the editor's round on Chapter 47

- Before using a symbol, check Appendix B's table (`tab:app-symbols`): $s$ is the primary surplus, so Chapter 47's
  supply shock is $\varepsilon_t$ (NARRATIVE: when symbols collide, change the symbol). Chapter 55 should keep
  $\varepsilon_t$ for a supply shock.
- When the book contrasts its own model with a source's result, read the source's conditions first. Gordon's
  “the price level, not the rate” is for a temporary shock (the crop failure ends and prices fall back); the
  chapter's example, where the oil price never falls back, is his permanent case, not “more extreme”. Show the other
  case with the model when it is one line of arithmetic.
- One source that gives two numbers for what looks like the same thing (the Bank of Japan's 3% and 2.0%): find its
  definitions (a footnote, a table note, the next page) and say in the text how they differ.
- A person named in an earlier chapter is named the same way, with the same source for the name (佐佐木直, note 44 of
  the Bank of Japan's history, p. 318).
- One bibliography item per work: the later chapter's sections and pages of the same volume go into the earlier item
  (`boj1986`), even when they come from other PDF files.
- A compare box sets the two sides against each other: a row whose two cells are both about one side (the CIA's
  two views of the oil shock) does not belong in it.
- “Who paid” names those who bore a cost; a group that gained in the source (wage earners' 32.9% in 1974) is not
  listed there.
- A coefficient is “significant” only under the standard errors the chapter uses elsewhere (robust in both windows).
