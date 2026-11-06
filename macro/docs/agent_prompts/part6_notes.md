# Part 6 (第六部分 战后黄金时代：东方与西方，1945—1970 年): notes for the chapter writers

Parts 1–5 are written and reviewed, so Part 6 is written against them. Chapters 35–43 are written one
at a time in that order (docs/WORKFLOW.md, sequential mode), each reviewed by one independent reviewer
before the next. Give the writer `batch_brief.txt` plus its section below. Sections for Chapters 36–43
are added when each is started; until then the neighbours named below divide the ground.

Part 6 is where the book's theory and its history run side by side: reconstruction and the dollar
system, the models of the 1950s and 1960s (Mundell–Fleming, the Phillips curve, consumption and
investment, Solow), and the roads of the poor countries, East Asia and the planned economies. Its
evidence is of three kinds:

- **Official documents.** Laws and decrees (German laws of 1948 are official works, not protected,
  §5 UrhG; Soviet and Chinese decrees likewise), US government papers (*Foreign Relations of the
  United States* on history.state.gov, the *Department of State Bulletin*, ECA and SCAP reports, the
  Economic Report of the President, Census historical statistics: public domain), UK papers (Hansard
  through the historic-Hansard pages on api.parliament.uk, Open Parliament Licence; Command papers
  older than 50 years are out of Crown copyright), and central-bank publications (Bank of Japan:
  credit "Bank of Japan"; Deutsche Bundesbank and Bank deutscher Länder: copy the reproduction notice
  verbatim). Prefer the original table to a later transcription; when only the transcription can be
  had, say so once in the 史料说明.
- **Contemporary and later scholarship.** The economists of the period (Triffin, Mundell, Phillips,
  Modigliani, Friedman, Solow, Lewis, Prebisch, Kornai …) and the historians after them are in
  copyright: short phrases only, otherwise paraphrase with `% 据:` anchors. NBER papers: short
  quotations with the © notice exactly as printed. A participant's statement quoted by a later author
  is indirect testimony and is named as such once, in the 史料说明.
- **Modern data.** BoE millennium workbook, Maddison 2023 (CC BY 4.0 with its citation policy), JST,
  WDI (CC BY 4.0), Bank of Japan time series, NBER macrohistory, Penn World Table (CC BY 4.0) for the
  growth chapters. Do not use FRED or ALFRED. Run `tools/probe_network.sh` first.

Earlier chapters own (refer back, do not retell):
- Ch 1 `ch:intro`: the consolidated budget constraint `eq:intro-budget`; the Russian and Sri Lankan
  questions that Ch 37 answers with the trilemma;
- Ch 3: the Fisher relation; Ch 4: the central bank's balance sheet; Ch 5: the balance of payments
  `eq:external-bop`, the real exchange rate and the compare box 固定汇率 vs 浮动汇率;
- Ch 19: the quantity equation; Ch 21 and Ch 18: growth accounting with land and labour (Ch 40's
  promise); Ch 23: the classical gold standard; Ch 24: reserves held abroad;
- Ch 26: Weimar and the Rentenmark of 1923 (`sec:weimar-stabilization`); Ch 27: the gold-exchange
  standard and its dependence on confidence; Ch 29: the Tripartite statement of 1936 and the trilemma
  as a description of 1931; Ch 30: repressed inflation (`sec:alternatives-repressed`, compare box
  公开通胀与被压抑的通胀) and Japan to 1938; Ch 31: the Soviet plans, material balances, Kantorovich and
  the soft budget constraint's origins; Ch 32–33: the General Theory and IS–LM; Ch 34: war finance,
  deferred pay (`sec:warfinance-gap`), functional finance and the design of Bretton Woods
  (`sec:warfinance-plans`, `sec:warfinance-bw`).

Later chapters own: Ch 44 the natural rate and the expectations-augmented Phillips curve; Ch 45
monetarism; Ch 46 the end of Bretton Woods (1971–73); Ch 50 the government budget constraint;
Ch 52 hyperinflation (Cagan, Sargent, Hungary 1946); Ch 56 endogenous growth; Ch 59 transition and
shock therapy; Ch 72 China's credit and exchange rate.

## Rules carried over from Part 5 (every Part 6 chapter)

Everything under "Rules carried over from the rewrite of Chapter 26" and every "Carried over from the
editor's round on Chapter NN" section of `docs/agent_prompts/part5_notes.md` (Chapters 27–34) applies
to Part 6. Read them all before writing. In short:

- The check script ties the text to the snapshots (model: the latest chapter's script, with said(),
  say(), told(), READINGS, TRANSLATIONS, KEYWORDS, LIVES/ROW_LIVES/UNKNOWN, EVENTS, LATER, coverage(),
  counts(), anchors(), witnesses()). Mutation test of at least ten numbers before reporting.
- Read who said and did what in a source: speaker, date, subject and direction of every quotation;
  reported speech stays reported; state a source's own mechanism, not a plausible one; a second
  witness must be independent; a detail resting only on the editor's notes is not evidence.
- At most about a dozen "不能"; limits in one clause, the pitfall box or the 史料说明. Name a line of
  evidence once; people and institutions are the subjects of sentences.
- A person is named, never "一位教授"; years from an authority file, "生卒年未详" when they cannot be
  verified (STYLE §3).
- Count a source's items before naming their number; a number a box already gives is not repeated in
  the next paragraph; concessions in a debate come from the documents themselves.
- Snapshot CSVs keep their line endings (LF or CRLF); write rows with Python's csv module.
- Shared series (`boe2017` and others): the bibitem names the tables each chapter uses; `used_in`
  names the new chapter.

## 第 35 章 `ch:reconstruction` 战后重建：马歇尔计划、德国货币改革与道奇路线 (`zh/ch35_reconstruction.tex`)

- Neighbours:
  - Ch 26 owns Weimar and the Rentenmark of 1923; this chapter contrasts 1923 (an open
    hyperinflation stopped) with 1948 (a repressed inflation removed) in one paragraph or a box row.
  - Ch 30 owns the mechanism of repressed inflation and the Nazi price stop of 1936: refer back to
    `sec:alternatives-repressed`; do not retell it. Ch 34 owns war finance and deferred pay.
  - Ch 36 owns the working of Bretton Woods: the Anglo-American loan of 1946, the sterling
    convertibility crisis of 1947, the devaluations of September 1949, the European Payments Union
    (1950–58), the return to convertibility in 1958 and Triffin. Here the dollar shortage, the EPU
    and the 1949 devaluations get one clause each with `\chref{ch:brettonwoods}`.
  - Ch 42 owns Japan's high growth (1955–73) and industrial policy; this chapter stops with the
    Korean War procurement boom and the end of the occupation (1952).
  - Ch 43 owns the mature planned economies (the USSR after 1947, Mao's China from 1953); Ch 52 owns
    hyperinflation theory and Hungary 1946 (one clause at most); Ch 59 owns transition and shock
    therapy (the 1948 reform as a model for 1990: one clause forward).
- Owns:
  - the overhang at the end of the war: money held back by price controls and rationing in Germany
    and Japan (the size of the Reichsmark money stock against goods; the cigarette currency and the
    black market of 1945–48, only where sourced);
  - the West German currency reform of 20 June 1948 in its parts: the Allied laws (Währungsgesetz,
    Emissionsgesetz, Umstellungsgesetz, then the Festkontogesetz of October 1948), the Bank deutscher
    Länder (founded 1 March 1948), the per-head quota, the conversion of balances, debts, wages,
    prices and rents, the cancellation of the Reich's debt and the banks' equalization claims, and
    what the conversion finally was for savers (verify each number in the law texts);
  - the freeing of prices at the same time: Ludwig Erhard and the Leitsätzegesetz (the Economic
    Council's law of June 1948 on the principles of controls and price policy after the reform),
    what was freed and what stayed controlled (rents, basic foods, raw materials), the shop windows
    that filled, the price rise of the second half of 1948, the general strike of 12 November 1948,
    and the rise in unemployment in 1949–50, all only where sourced;
  - who planned it: the Colm–Dodge–Goldsmith plan of 1946 and the conclave at Rothwesten (April–June
    1948) with Edward A. Tenenbaum, only as far as the sources show; the Soviet reply (the eastern
    reform of 23 June and the Berlin blockade from 24 June) in one or two sentences;
  - the Marshall Plan: Marshall's Harvard speech (5 June 1947), the Economic Cooperation Act (3 April
    1948), the amounts by country and their size against national income, counterpart funds, the
    OEEC, the Soviet refusal; its role and the debate about it;
  - Japan: the Emergency Financial Measures of February 1946 (deposits frozen, the new yen), the
    Reconstruction Finance Bank (1947) financed by the Bank of Japan and the inflation that followed,
    priority production, the nine principles of December 1948, Joseph Dodge's arrival (February
    1949), the balanced budget of fiscal 1949, his "stilts" statement (March 1949), the single rate of
    360 yen per dollar (April 1949), the Shoup mission in one clause, the stabilization slump and the
    Korean War procurement boom (from June 1950);
  - Ch 34's promise on Britain and the USSR (below).
- Promises (FORWARD_REFS): the row from Ch 34 (`sec:warfinance-compare`, `sec:warfinance-legacy`,
  the ending): how the purchasing power held back in the war was released or written off after it —
  Britain's post-war credits (when and how they were repaid; historic Hansard), the Soviet money
  stock that trebled in the war (the currency reform of December 1947 and the end of rationing; the
  decree's own terms), the Bank of Japan's financing of the government (1946–49). One paragraph each
  for Britain and the USSR is enough; Japan is a main case. Mark the row done with the labels.
- When it began: Chapter 34 ends with “被压抑的通胀怎样一夜消失？”. Answer it precisely: in West
  Germany it did vanish in a night, because the reform cut the money stock and freed most prices at
  once; in Japan it did not (the 1946 freeze failed because the budget and the Bank of Japan's
  lending were not fixed; the stop came in 1949); Britain let the held-back money out slowly and the
  USSR confiscated most of it.
- Opening (suggested, verify every detail): Sunday 20 June 1948 in the western zones: every person
  receives the first 40 Deutsche Mark of the per-head quota against old marks, and on Monday goods
  that had not been seen for years are in the shop windows; Ludwig Erhard (1897–1977) announces the
  end of many controls. The opening must have a person, a date and the question within one page.
  A better-sourced scene is welcome.
- People (one sentence each at first appearance, NARRATIVE §8.1): Ludwig Erhard; Lucius D. Clay
  (US military governor); Edward A. Tenenbaum; Joseph M. Dodge (who worked on the German plan of 1946
  and came to Japan in 1949: a thread through the chapter, if the sources confirm both roles);
  George C. Marshall; Ikeda Hayato (finance minister from 1949) and Ichimada Hisato (Bank of Japan
  governor), Ishibashi Tanzan (finance minister 1946–47, who favoured expansion), only where the
  sources give their roles. Do not add people the sources do not support.
- Case (East, outside Germany and Japan): the gold yuan (金圆券) of 19 August 1948, a currency reform
  in the same summer as Germany's, with prices frozen instead of freed and no budget behind it (the
  decree's terms: the conversion rate against fabi, the issue limit, the price freeze, the forced sale
  of gold, silver and foreign exchange; Chiang Ching-kuo in Shanghai; the end of the limit in
  November), and in one closing sentence the stabilization of 1950. One box, only if the decree text
  and a numerical source for the outcome can be had; otherwise one paragraph with what is verified.
  Ch 29 owns the fabi reform of 1935: refer back.
- Data and sources (probed 2026-10-28 from the shell: answered 200):
  - history.state.gov (FRUS 1948 vol. II on Germany; FRUS 1949 vol. VII on Japan; public domain);
  - www.verfassungen.de (German laws 1945–49; documentarchiv.de did not answer); de.wikisource;
  - www.bundesbank.de (monthly reports and statistics; read the reproduction terms);
  - www.boj.or.jp (日本銀行百年史 online; BoJ copyright: short quotes) and www.stat-search.boj.or.jp
    (prewar-base wholesale price index; credit "Bank of Japan");
  - www.mof.go.jp (財務省 policy history; read its terms of use);
  - www.ifz-muenchen.de (Vierteljahrshefte für Zeitgeschichte archive PDFs, e.g. Buchheim 1988 on
    the currency reform; in copyright: short phrases);
  - www.nber.org (De Long and Eichengreen 1991, w3899: © notice);
  - archive.org (search for Wallich 1955, Milward 1984, Chang Kia-ngau 1958; check each copy's
    status), www.marshallfoundation.org (the speech text; prefer the *Department of State Bulletin*),
    www.trumanlibrary.gov, www.cvce.eu, dl.ndl.go.jp (Japanese government documents), zh.wikisource
    (the 1948 decrees), econstor, IDEAS;
  - api.parliament.uk/historic-hansard (answered; hansard.parliament.uk answered 403), FRASER did
    not answer.
  Stay consistent with Ch 30's and Ch 34's numbers (Ide 2003, Shizume 2009, Harrison): refer back.
- Teaching:
  - the overhang (`eq:reconstruction-overhang`): with money demand $M=kPY$ and prices held at
    $\bar P$, the overhang is $M-k\bar PY$; freeing prices without a reform moves $P$ to $M/(kY)$;
    the reform cuts $M$ instead. A worked example with stated teaching inputs, and one with the
    German numbers if the sources give the money stock and an output index;
  - the conversion as a balance-sheet operation (a table `tab:reconstruction-conversion` of the
    rules, from the law texts; a worked example of one household's cash, savings, debt and wage
    before and after, and who gained and who lost; the equalization of burdens of 1952 in one
    clause, if sourced);
  - the single exchange rate: implicit rates for different goods before April 1949 against the one
    rate of 360 yen, with a worked example (an exporter or importer whose subsidy ends).
- Compare boxes (2–3): 货币改革 vs 价格放开 (what each does alone; Germany did both); 德国的稳定 vs
  日本的稳定 (1948 vs 1949: money cut and prices freed vs budget balanced, the RFB's lending stopped
  and one exchange rate); optionally 1948 年的两次货币改革：西德与中国.
- Contested questions (give each side's strongest case and its own concessions; do not decide):
  - Did the reform and Erhard's freeing of prices start the German recovery, or was it under way
    before (the traditional account, e.g. Wallich 1955, against Abelshauser's view that production
    was rising before June 1948 and that part of the jump was hoarded stock and statistics; Buchheim
    1988 and Ritschl 1985 in the VfZ)?
  - How much did the Marshall Plan matter (De Long and Eichengreen 1991: a modest direct effect on
    investment, a larger one through policy and the payments system; Milward 1984: recovery was
    already under way and the 1947 "crisis" was a dollar shortage of a growing Europe)?
  - Was the Dodge Line's deflation necessary or excessive (the stabilization slump of 1949–50; the
    Korean War boom that ended it)?
- Figures (2–4): West German industrial production 1946–1950 with June 1948 marked; Japan's prices
  1945–1952 (Bank of Japan prewar-base index, log scale) with February 1946, the RFB and April 1949
  marked; Marshall aid by country (and against national income, if the source gives it).
- Ending: return to 20 June 1948 and hand over Ch 36's question “美元为什么既是体系的支柱，又是它的
  隐患？” (read its stub's guide box): by 1949 both new currencies were pegged to the dollar, and
  Europe's problem was a shortage of dollars.
- Labels: `sec:reconstruction-…`, `eq:reconstruction-…`, `fig:reconstruction_…`,
  `tab:reconstruction-…`, `ex:reconstruction-…`.
- Length: Chapters 30–33 have 7,400–7,900 characters of main text; Ch 34 has 10,700, which the reviewer
  found long. Aim for 8,000–9,000; cut retelling of neighbours first.

### Carried over from the editor's round on Chapter 35
- When two official histories disagree, read both in full before choosing: who decided something is
  often only in the more detailed one (the 360-yen rate: the Ministry of Finance's history says GHQ
  "floated" 300 or 400; the Bank of Japan's centenary history, pp. 254–256, shows Dodge and GHQ at
  330 and Washington's National Advisory Council insisting on 360). Name the disagreement in the
  史料说明.
- A worked example's reading must be the source's own mechanism. Chapter 35's draft read a price
  rise smaller than the money rise as $k$ rising; Buchheim says velocity was high and still rising.
  Check the starting point of a series before reading a ratio (the end-June money stock left out
  the free-account credits); when the start is uncertain, compute both extremes.
- A conversion or write-off has two sides: what creditors lose, debtors gain. State both, and the
  later law that took part of the gain back, if any.
- "照 Buchheim 的叙述", "按财务省的政策史" and the like belong to judgments, interpretations and
  disputed facts. A plain number or date carries its cite alone (the draft had 58 such frames; the
  editor removed 18).
- Two works that cite each other are one line of evidence (Ritschl 1985 and Buchheim 1988).
- Life dates: when the Library of Congress, the GND and data.bnf.fr have no record, historic
  Hansard's people pages (api.parliament.uk/historic-hansard/people/…) give MPs' dates of birth; a
  Wikidata description is not an authority record. Write "生卒年未详" when the death year cannot be
  verified.

## 第 36 章 `ch:brettonwoods` 布雷顿森林体系的运行 (`zh/ch36_brettonwoods.tex`)

- Neighbours:
  - Ch 34 owns the design: the Clearing Union against White's Fund, the conference of July 1944 and
    the Articles (quotas, par values, Article IV's fundamental disequilibrium, the scarce-currency
    clause, capital controls as a member's right): refer back to `sec:warfinance-plans` and
    `sec:warfinance-bw` in one clause each; do not retell.
  - Ch 35 owns reconstruction: the Marshall Plan and counterpart funds, the Deutsche Mark of 1948
    (its rate of 30 cents taken over from the Reichsmark) and the 360-yen rate of April 1949 (who
    decided it: `sec:reconstruction-japan`). This chapter takes the dollar shortage, the EPU and the
    1949 devaluations from there (Ch 35's FORWARD_REFS row). Do not retell the Marshall Plan.
  - Ch 37 owns the theory: Mundell–Fleming, the trilemma and optimum currency areas, and Canada's
    float of 1950–62 (its case). Here the trilemma is used as a description at most, with
    `\chref{ch:mundell}`.
  - Ch 46 owns the end: 15 August 1971, the Smithsonian agreement and the move to floating in 1973.
    This chapter ends with the pressures of 1968–71 (the two-tier gold market of March 1968, the
    franc and the mark in 1969) and hands over Ch 37's question.
  - Ch 76 owns the currency hierarchy today and the "exorbitant privilege" as a present-day debate;
    here the phrase and the French critique of the 1960s only.
- Owns:
  - how the system worked from 1946: the IMF's par values and drawings in practice, capital controls,
    the dollar shortage and the Anglo-American loan of 1946, the sterling convertibility crisis of
    July–August 1947, the devaluations of September 1949 (sterling from $4.03 to $2.80 and the
    others that followed);
  - the EPU (1950–58) as the road back to convertibility, and the return to current-account
    convertibility at the end of December 1958 (Article VIII status for the main European currencies
    in 1961), and what changed afterwards (capital flows through convertible current accounts, the
    first speculative attacks, the mark's revaluation of March 1961);
  - Triffin (1960) and the dilemma: the world's reserves grow only if the United States runs
    deficits; the deficits erode confidence in the dollar's gold value. The US gold stock against
    dollar liabilities to foreigners (official and total), with the year the lines cross;
  - the defence of the dollar: the London gold pool (1961–68), the gold price of October 1960, swap
    lines, Roosa bonds, the Interest Equalization Tax (1963) and the voluntary restraint programmes,
    the two-tier market of March 1968, the SDR (1969), each in a sentence or two;
  - the French critique (the case): Valéry Giscard d'Estaing's "privilège exorbitant" (verify who
    said it, when and in what words) and de Gaulle's press conference of 4 February 1965 calling for
    a return to gold, with Rueff's argument; France's conversion of dollars into gold;
  - sterling's long decline to the devaluation of 18 November 1967 (in one paragraph).
- Promises (FORWARD_REFS rows pointing to 36): from Ch 5 (fixed rates as the world's rule under
  Bretton Woods); Ch 24 (reserves held in the centre's money market: dollars as reserves); Ch 29
  (the adjustable peg in practice; done for Ch 34, open for Ch 36); Ch 34 (how the adjustable peg, the
  quotas, the scarce-currency clause and the capital controls worked in practice; which side of the
  creditor–debtor argument the record supported); Ch 35 (the EPU, the dollar shortage, the fixed
  rates of the mark and the yen). Mark each done with the labels.
- When it began: Ch 35 ends with “美元为什么既是体系的支柱，又是它的隐患？”. Answer it: the dollar was
  the pillar because it was the one currency convertible into gold at a fixed price and the reserve
  the others held; the more dollars the world held, the less gold stood behind each.
- Teaching:
  - the Triffin arithmetic (`eq:brettonwoods-triffin`): reserves $R=G+D$, with gold $G$ growing
    slowly and dollar reserves $D$ growing with the US deficit; the cover ratio $G/D$ and the year it
    falls below one (a worked example with teaching inputs, and one with the US data);
  - a parity change under Article IV with the BoP identity of Ch 5 (sterling in 1949 or 1967:
    what a devaluation of $x$% does to import prices and export receipts, teaching inputs);
  - optionally the gold-pool arithmetic (who sold how much gold to hold $35).
- Compare boxes: 布雷顿森林体系 vs 古典金本位 (PLAN's candidate; refer back to Ch 23); optionally 美元的
  “过度特权” vs 世界银行家（Despres, Kindleberger and Salant 1966).
- Contested questions (do not decide): did the system end because of a flaw in its design (Triffin)
  or because of American policy (the inflation of the late 1960s; Bordo and Eichengreen eds. 1993);
  was the dollar's role a privilege for the United States or a service to the world (the French
  critique against the "world banker" view); did the record support Keynes's case for charging
  creditors (Ch 34's question: the scarce-currency clause was never invoked; Germany's surpluses).
- Data and sources: the IMF's own histories (Horsefield 1969, de Vries 1976; imf.org answered 403
  on 2026-10-28: try archive.org copies and elibrary); the *Federal Reserve Bulletin* and *Banking
  and Monetary Statistics 1941–1970* (FRASER did not answer; try archive.org); the Economic Report of
  the President (govinfo, public domain, answered 200); the US Treasury Bulletin; Triffin's statement
  to the Joint Economic Committee of October 1959 (a congressional hearing; check its status; short
  quotations) and Triffin (1960) (in copyright: short phrases); de Gaulle's press conference of
  4 February 1965 (CVCE answered 200; Élysée and INA answered 200; check the terms); BIS annual
  reports (cite the BIS; translations marked not official); the BoE millennium workbook for sterling
  rates and reserves; the NBER volume of Bordo and Eichengreen (1993, chapters on nber.org: © notice).
- Figures: US gold stock against dollar liabilities to foreigners, 1950–1971; the London gold price
  around October 1960 and 1968, if a reliable series can be had; sterling's reserves or parity.
- Ending: return to the opening and hand over Ch 37's question “固定汇率、资本自由流动、独立的货币政
  策，为什么只能三选二？哪些地区适合共用一种货币？” (read its stub's guide box).
- Labels: `sec:brettonwoods-…`, `eq:brettonwoods-…`, `fig:brettonwoods_…`, `tab:brettonwoods-…`,
  `ex:brettonwoods-…`.
- Length: 8,000–9,000 characters of main text.

### Carried over from the editor's round on Chapter 36
- A secondary account's number is a claim to check against the primary record when one is in the
  cache. Chapter 36's draft took Bordo's "$35.20 (the U.S. Treasury's buying price)" and his "G10"
  agreement of October 1960; the BIS annual reports of 1961 and 1962 give the London quotations of
  $35.20–35.25, the Treasury's selling price of $35.0875 and "the central banks which meet monthly
  at the B.I.S." (the group of ten only came with the borrowing agreement of December 1961).
- Read a source's sentence to its end before using its first half: Garber's point that US
  residents' claims "could have been shifted abroad and quickly used to run the system" is the
  opposite of a harmless aside about gold ownership being illegal.
- A minister who reads out his earlier words is explaining them, not being caught by them
  (Callaghan, 20 November 1967, c. 936): do not frame reported speech as irony.
- A worked example's side remark must hold in every case the example covers, and agree with the
  chapter's self-checks: converting dollars into gold raises the cover ratio when it is above 1
  and lowers it when it is below 1.
- Two figures for "the same" share may measure different things (the gold pool: 50% the United
  States was to provide, 60% of the gold actually sold); check what each counts before calling it
  a disagreement.
- A compare box's cells must belong to the regimes they compare: Britain's 1925 return is the
  interwar standard (Chapter 27), not the classical one; use the resumption of 1821 (Chapter 19).
- An inference drawn from an institution's list of facts is the book's, not the institution's: put
  the citation after the facts and mark the inference (本书的解读).

## 第 37 章 `ch:mundell` 蒙代尔–弗莱明与最优货币区 (`zh/ch37_mundell.tex`)

A theory chapter, like Chapter 33: the model is the spine, and its history (who built it, when, from
what experience) and its tests are the story. Model chapter: zh/ch33_islm.tex.

- Neighbours:
  - Ch 5 owns the balance of payments (`eq:external-bop`), the real exchange rate (`eq:external-real`,
    $e$ = home currency per unit of foreign currency, so a rise is a depreciation; foreign variables
    carry a superscript f, $i^{f}$, $P^{f}$), the parity conditions (`eq:external-cip`,
    `eq:external-uip`) and the compare box 固定汇率与浮动汇率, whose trilemma sentence points here. Use
    its notation; do not re-derive the identities.
  - Ch 33 owns IS–LM (`eq:islm-is`, `eq:islm-lm`, `eq:islm-solution`, with $c$, $b$, $k$, $h$ and
    $A$): extend that model to the open economy with the same letters; do not re-derive the closed
    model.
  - Ch 16 (`eq:merc-peg`: who pegs a price gives up the quantity), Ch 1 (the peg and seigniorage in
    `ex:intro-peg` and `sec:intro-afford`; the Russian and Sri Lankan questions), Ch 29 (the trilemma as a
    description of 1931) and Ch 36 (West Germany 1960–61 and 1969, France's capital flight; Ch 36 ends
    with this chapter's question) are the cases this chapter's theory explains: refer back in a clause.
  - Ch 46 owns 1971–73, Dornbusch's overshooting and floating rates after 1973; Ch 60 owns the EMS,
    the ERM crisis of 1992–93 and the euro judged against the OCA criteria (with Frankel and Rose's
    endogeneity, if used); Ch 61 owns the currency-crisis models and the full account of Russia 1998
    (Chiodo and Owyang), Hong Kong and Argentina; Ch 76 owns the CFA franc, dollarization and the
    currency hierarchy. Here each is at most a sentence with `\chref`.
  - Two Flemings: J. Marcus Fleming, the IMF economist of the 1962 paper, is not Donald
    Fleming, Canada's Minister of Finance in the Coyne affair of 1961. Name both in full at first use
    if both appear, with dates from an authority file.
- Owns:
  - the open-economy IS–LM with a balance-of-payments condition: Mundell (1963, *Canadian Journal of
    Economics and Political Science*) and Fleming (1962, *IMF Staff Papers*), and how the pair got its
    name (Boughton 2003, *IMF Staff Papers*, on the origins, if obtained: Mundell at the IMF's
    research department 1961–63; who called it "Mundell–Fleming" first);
  - the results under perfect capital mobility: under a fixed rate monetary policy cannot move income
    (the money supply follows the reserves) and fiscal policy works with full force; under a float
    monetary policy works through the exchange rate and fiscal policy is crowded out by appreciation;
    then imperfect mobility (a BP curve with a finite slope) in a paragraph;
  - the trilemma ("impossible trinity") as the model's corollary, and its empirical test (Obstfeld,
    Shambaugh and Taylor, "The Trilemma in History", NBER working paper, if obtained: do pegged
    countries' interest rates follow the base country's, under the gold standard, Bretton Woods and
    after?);
  - the case: Canada's float, 30 September 1950 to 2 May 1962 (the inflows of 1950, the IMF's
    reaction to a member leaving its par value, the premium over the US dollar in the 1950s, the
    Coyne affair of 1961, the peg at 92½ US cents of 2 May 1962 and the crisis of June 1962). Mundell
    was Canadian, and the 1963 paper names Canada's experience: verify what it says;
  - optimum currency areas: Mundell (1961, *AER*: factor mobility, his two-region example), McKinnon
    (1963, *AER*: openness) and Kenen (1969: diversification), with what each criterion means for a
    region choosing to share a money; the answer to the second half of the guide question, in
    general terms (the euro's own test is Ch 60's).
- Promises (FORWARD_REFS rows pointing to 37): from Ch 5 (the trilemma; with a peg and free capital,
  monetary policy follows the anchor), Ch 16 (a peg gives up the money supply; Law's peg as the
  analogy), Ch 29 (the theory behind 1931's three choices), Ch 33 (the open-economy IS–LM), Ch 34 (the
  Articles left capital controls to members) and Ch 36 (West Germany 1960–61 and 1969, France under
  controls). Mark each done with the labels. The PLAN's guide also promises to apply the model to
  Ch 1's Russian and Sri Lankan questions: one paragraph each, with Ch 1's facts and at most a few new
  verified numbers (for Russia, the defence of the band by interest rates before 17 August 1998; for
  Sri Lanka, the rate held near 200–203 rupees to the dollar and the float of March 2022, from the
  CBSL, derived extract only), and say which corner of the triangle each tried to hold.
- When it begins: Ch 36 ends with West Germany in 1969 and this chapter's question. Answer it with the
  model: with free capital movement the interest rate is set abroad if the rate is fixed; a country
  keeps its own monetary policy only by floating or by controls.
- Teaching:
  - the model (`eq:mundell-…`): Ch 33's IS with net exports $\mathit{NX}=x\,e-mY$ (linear, teaching
    form, with $P$ and $P^{f}$ fixed so $e$ moves $q$), Ch 33's LM, and the capital-mobility condition
    $i=i^{f}$ (perfect mobility, from `eq:external-uip` with static expectations) or a BP condition with
    a finite slope; solve for $Y$ and $e$ (float) or $Y$ and $M$ (peg);
  - worked examples with teaching inputs: a fiscal expansion under each regime; a monetary expansion
    under a peg and the reserves it costs (tie to `eq:merc-peg` and Ch 1's example); one with Canada's
    own numbers if the data allow (the premium, the interest differential);
  - the OCA criteria as a short worked comparison (two regions hit by a demand shift: what adjusts
    with a common money and without one).
- Compare box: 固定汇率下的财政政策 vs 浮动汇率下的财政政策 (the PLAN's candidate); optionally a table of
  the three OCA criteria (author, year, criterion, what it implies).
- Contested questions (do not decide; each side's strongest case and its own concessions):
  - did Canada's float work? Friedman (1953, "The Case for Flexible Exchange Rates": short phrases) and
    the record of the 1950s, against the conflict of 1961 and the return to a peg in 1962 (was the float
    the problem, or the policy mix?);
  - does the trilemma still hold, or is it a "dilemma" (Rey 2013, Jackson Hole, and its NBER version: a
    global financial cycle reaches floaters too), against the evidence that floaters keep more
    monetary autonomy (Obstfeld, Shambaugh and Taylor; others, if obtained);
  - Mundell I against Mundell II (McKinnon 2004, *JCMS*: Mundell's 1961 case for flexible rates
    between regions against his 1973 arguments for common currencies), if the sources can be had.
- Data and sources (working-paper numbers, journal issues and dates in this list are leads, not
  evidence: verify each; probed 2026-10-29: www.bankofcanada.ca, www150.statcan.gc.ca, www.nber.org,
  archive.org, parl.canadiana.ca, www.elibrary.imf.org, www.jstor.org, www.ecb.europa.eu, www.cbsl.gov.lk,
  www.cbr.ru, eh.net, publications.gc.ca answered; www.imf.org and www.lipad.ca did not):
  - Bank of Canada: annual reports of the Governor 1950–62, its historical exchange-rate and
    interest-rate tables, and Powell, *A History of the Canadian Dollar* (Bank of Canada, 2005), if on
    the site. Terms (read 2026-10-29, bankofcanada.ca/terms/): content may be freely used, copied and
    distributed if "the Bank of Canada" is attributed as the source and changes are indicated; bank-note
    images, the logo and third-party content are excepted. Record the copy and the terms in the json.
  - Statistics Canada: *Historical Statistics of Canada* (11-516-X; exchange rates and interest rates)
    under the Statistics Canada Open Licence: copy its attribution statement verbatim.
  - Canada's House of Commons Debates (30 September 1950 statement by the Minister of Finance, Douglas
    Abbott; the debates of 1961 and 1962) through parl.canadiana.ca: check the terms first; short
    quotations.
  - IMF: Fleming (1962) and Boughton (2003) through the IMF eLibrary if they open (IMF copyright: short
    phrases); the IMF's annual reports of 1951 and 1962 on Canada's float and peg.
  - Mundell (1961, 1963), McKinnon (1963), Kenen (1969), Friedman (1953), Rey (2013): in copyright,
    short phrases only, otherwise paraphrase with `% 据:` anchors; NBER working papers with the ©
    notice exactly as printed.
  - Ch 1's own snapshots (`chiodo2002`, `cbr2026`, `cbsl2023ar` and their terms: CBR link to the source,
    not commercial; CBSL derived extract only) for Russia and Sri Lanka.
- Figures: the model (IS, LM and the capital-mobility line under a peg and a float, before and after
  a fiscal and a monetary expansion); Canada 1950–1962 (the US-dollar price of the Canadian dollar,
  monthly or annual, with the Canadian–US interest differential if a series can be had); optionally
  the trilemma test.
- Ending: return to the opening and hand over Ch 38's question “通胀与失业真是一张可以点菜的菜单吗？”
  (read its stub's guide box).
- Labels: `sec:mundell-…`, `eq:mundell-…`, `fig:mundell_…`, `tab:mundell-…`, `ex:mundell-…`.
- Length: 8,000–9,000 characters of main text.

### Carried over from the editor's round on Chapter 37
- Count a source's items before naming their number (Rey 2015 lists four options, (a)–(d), not three);
  the check script should test that there is no further item.
- Read the subject and the mood of a quoted sentence: in Mundell (1963) "It should also have a high
  degree of relevance … to a country like Canada" the subject is the assumption of perfect mobility,
  just admitted to "overstate the case", and "should" is a claim of relevance, not a finding.
- When a later author reports a reaction, name whose reaction and in which document: Powell gives the
  IMF staff's opposition from the Executive Board minutes and the "gravely compromised" worry from a
  Bank of Canada memorandum, not "the IMF".
- An author's own sentence placed straight after a quoted statement reads as the speaker's: keep the
  author's sentence unquoted and before or apart from the statement.
- The narrative must agree with the chapter's model: under a float with perfect mobility the model
  has $i=i^{f}$, so a floating Canada kept its monetary policy, not its interest rate.
- "X called it Y" is not "it was named Y in year Z": keep the source's attribution of a name.
- A statistical compilation that takes its numbers from the same institution's publication (the
  *Historical Statistics of Canada* from the *Bank of Canada Review*) agrees with that institution's
  history but is not an independent witness.

## 第 38 章 `ch:phillips` 菲利普斯曲线与宏观计量模型 (`zh/ch38_phillips.tex`)

A theory chapter, like Chapters 33 and 37: the relation and the models are the spine, and how they
were found (whose data, what method), how they were turned into policy and how they were tested are
the story. Model chapters: zh/ch33_islm.tex and zh/ch37_mundell.tex.

- Neighbours:
  - Ch 19 (`sec:bullion-hume`): Hume's remark that added money stimulates industry before prices
    catch up, and the sentence "货币在短期内不中性、在长期内中性，这个两分法后来贯穿了宏观经济学" that
    points here. Refer back in a clause; the long-run half is Ch 44's.
  - Ch 32 (`sec:generaltheory-legacy`, 教科书的凯恩斯) and Ch 33 (`sec:islm-legacy`: IS–LM takes the
    money wage as given; 谁把它们找了回来 names this chapter and Ch 44; Modigliani 1944 known only from
    his 1985 recollection; Tinbergen's twelve equations and Frisch at the Oxford meeting of 1937). Use
    Ch 33's letters ($c$, $b$, $k$, $h$, $A$) if the model is extended; do not re-derive IS–LM.
  - Ch 34 (`sec:warfinance-gap`, `eq:warfinance-gap`; 需求与产能的账 says "产出缺口与通胀的关系是本章的题目"):
    the gap between planned spending and capacity becomes the output gap; keep that promise with the
    output gap and its relation to unemployment and wages (Okun 1962, if obtained), not by retelling
    1940.
  - Ch 37 ends with this chapter's question: its model holds prices fixed, and Canada's quarrel of
    1961 (unemployment doubled from 1956 to 1961, Coyne fearing inflation) is the example. Answer it.
  - Ch 39 owns the consumption and investment theories (Modigliani–Brumberg 1954, Friedman 1957,
    Jorgenson 1963, Tobin 1969): the large models' consumption and investment equations are described
    here as equations, their theory is Ch 39's (the ending hands over its question).
  - Ch 44 owns Phelps (1967) and Friedman (1968), the natural rate, the expectations-augmented curve,
    the accelerationist hypothesis and the test of the 1970s; Ch 45 monetarism; Ch 47 supply shocks
    and stagflation; Ch 48 rational expectations and the Lucas critique of macroeconometric models
    (1976); Ch 54 the New Keynesian Phillips curve; Ch 74 the curve in the 2020s. Here each is at most a
    sentence with `\chref`. Do not derive the expectations-augmented curve; Samuelson and Solow's own
    warning about the longer run is this chapter's, the theory of the shift is Ch 44's.
- Owns:
  - Phillips (1958, *Economica*): his data (the money-wage-rate indexes and the unemployment figures
    he used for 1861–1913, 1913–48 and 1948–57, and where each came from), his method (how he measured
    the rate of change, how he averaged over intervals of unemployment, the curve he fitted and its
    parameters, the loops and how he read them, the years he set aside and why) and his conclusions in
    his own terms (the unemployment rate at which wages would be stable; the rate compatible with stable
    prices given productivity growth). Read the paper itself; every number from it is checked against
    the page.
  - Phillips himself: the New Zealand engineer at the LSE, the hydraulic machine (MONIAC, 1949) in a
    sentence or two if verified (the Science Museum Group's collection pages answered on 2026-10-29),
    life dates from an authority file.
  - Lipsey (1960, *Economica*): the theory behind the curve (wages respond to the excess demand for
    labour, unemployment as its proxy), the loops, and the re-estimation with the rate of change of
    unemployment and of prices: the step from a fitted regularity to a behavioural relation.
  - Samuelson and Solow (1960, *AER* Papers and Proceedings, read at the meetings of December 1959): the
    US data they plotted, the "menu" (verify the exact phrase and what it is a menu of), the two points
    they named on their curve, and their own caveats (the curve may shift in the longer run; policy
    that keeps demand low might change it). Copyright: short phrases only.
  - The output gap: Okun (1962, "Potential GNP: Its Measurement and Significance"; a Cowles Foundation
    reprint may be on cowles.yale.edu) and its rule of thumb relating unemployment to the gap (verify
    the ratio and the period), and the Council of Economic Advisers' *Economic Report of the President*
    of January 1962 (US government, public domain) with its unemployment target: the menu as an
    official choice.
  - Macroeconometric models: from Tinbergen (Ch 33's twelve equations; the League of Nations volumes of
    1939, if obtained) through Haavelmo (1944) and the Cowles Commission's structural equations and the
    identification problem (in a paragraph), to Klein and Goldberger (1955, *An Econometric Model of the
    United States 1929–1952*): its size (count the equations and identities), its data (annual, which
    years left out), its estimation method, its blocks (consumption, investment, the labour market —
    check whether it has a wage-adjustment equation and how it relates to Phillips's), and what it was
    used for (forecasts, multipliers; Adelman and Adelman 1959 in a sentence if obtained). Klein's
    Model I (Klein 1950, Cowles Commission Monograph 11, 1921–41, three behavioural equations) is the
    candidate for the teaching example if the monograph opens on cowles.yale.edu. Klein's Nobel prize
    (1980; nobelprize.org answered) with its citation.
- Promises (FORWARD_REFS rows pointing to 38): from Ch 19 (the short-run/long-run dichotomy), Ch 32
  (the textbook Keynes joined to price adjustment), Ch 33 (IS–LM joined to wage and price adjustment;
  Modigliani 1944), Ch 34 (the gap as the output gap and its relation to inflation) and Ch 37 (the menu
  question; Canada 1961). Mark each done with the labels; where a row names Ch 44 too, say which half
  this chapter kept.
- When it begins: Ch 37 ends with the question. A candidate opening is the paper's own moment (Phillips
  at the LSE, 1958, with a century of British figures on one page) or Samuelson and Solow at the
  meetings of December 1959; choose what the documents support.
- Teaching:
  - the relation (`eq:phillips-…`): Phillips's fitted curve with his parameters; the step from wage
    inflation to price inflation (price inflation ≈ wage inflation minus productivity growth, a
    teaching approximation: say so); Okun's rule;
  - worked examples with teaching inputs or the sources' own numbers: (1) read Phillips's curve: wage
    change at two unemployment rates, and the rate at which wages are stable; (2) from his curve to the
    unemployment rate compatible with stable prices, with his productivity figure; (3) the menu: a
    choice between two points and what each costs whom; (4) a small macroeconometric model (Klein's
    Model I or a three-equation teaching model built from Ch 33's IS): solve it, compute an impact and a
    long-run multiplier, and show what "simulation" means;
  - reproduce the curve: the UK scatter 1861–1913 with Phillips's fitted curve and the points of
    1948–57, from Phillips's own table if it gives the numbers, otherwise from the BoE millennium
    workbook (v3.1, already used by earlier chapters: name the sheets and the underlying sources the
    workbook asks users to cite). Revised series are not Phillips's series: say which you plot and
    show where they differ.
- Compare box: 统计关系 vs 结构关系 (the PLAN's candidate): a fitted regularity (Phillips's curve over
  1861–1913) against a behavioural equation with an identified cause (Lipsey's excess demand; the
  Cowles structural equations). The question of what changes when policy changes is Ch 48's; one cell
  or one sentence may point there. Every cell must belong to the two kinds compared.
- Contested questions (do not decide; each side's strongest case and its own concessions):
  - Did the economists of the 1960s believe in a stable menu they could exploit? The usual story (in
    Friedman's Nobel lecture of 1976, nobelprize.org, short phrases) against Samuelson and Solow's own
    caveats and Forder (2014, *Macroeconomics and the Phillips Curve Myth*, OUP, if obtained: short
    phrases). Read what each actually wrote.
  - Can statistics test economic theories? Keynes's review of Tinbergen (*Economic Journal* 1939,
    "Professor Tinbergen's Method"; Keynes is in the public domain in the UK, record the copy used) and
    Tinbergen's reply (1940), if obtained; Haavelmo's answer in the probability approach.
  - Who found the curve first? Fisher (1926, *International Labour Review*, "A Statistical Relation
    between Unemployment and Price Changes"; the ILO library hosts back issues: check, and copy the
    ILO's reproduction terms) and his 1973 reprint ("I Discovered the Phillips Curve", *JPE*), against
    what Phillips measured (wages, not prices; a century, not a decade). One paragraph, if verified.
- Political character (write_template rule 5): a point on the menu chooses who bears the cost, the
  unemployed (which workers, if a source says) or those whose incomes are fixed in money; say it plainly
  with the sources' own words where they exist (Samuelson and Solow's, the 1962 Report's). Britain's
  "stop–go" and incomes policies of the 1960s at most in a sentence, verified (Hansard through
  api.parliament.uk, Open Parliament Licence; hansard.parliament.uk answered 403 on 2026-10-29).
- Data and sources (journal issues, page ranges and dates in this list are leads, not evidence: verify
  each; probed 2026-10-29: www.bankofengland.co.uk, archive.org, fraser.stlouisfed.org (unstable),
  www.govinfo.gov, www.presidency.ucsb.edu, www.nobelprize.org, www.ons.gov.uk, cowles.yale.edu,
  elischolar.library.yale.edu, www.nber.org, www.aeaweb.org, eprints.lse.ac.uk, www.econlib.org,
  collection.sciencemuseumgroup.org.uk, www.census.gov answered; onlinelibrary.wiley.com, www.bls.gov,
  download.bls.gov, babel.hathitrust.org, hansard.parliament.uk and www.rbnz.govt.nz answered 403;
  www.jstor.org answers with a bot check: do not retry it):
  - Phillips (1958): Wiley is blocked and JSTOR has a bot check. A JSTOR-derived copy is on a
    university course page (found by web search 2026-10-29: elearning.unito.it, "Phillips_Econ58.pdf");
    read it to verify, cite the journal, record the copy used and its SHA-256, quote short phrases only
    (Phillips d. 1975; in copyright). Lipsey (1960) and Samuelson–Solow (1960): look for comparable
    copies; record each as not obtained if none opens.
  - UK data: the BoE millennium workbook (cached under ~/.cache/finance-study/boe; see data/SOURCES.md
    for the rows already using it and how they cite it).
  - US data: BLS is blocked; use the Census Bureau's *Historical Statistics of the United States,
    Colonial Times to 1970* (www.census.gov, public domain) or the Economic Report of the President's
    statistical tables (govinfo or FRASER; FRASER is not FRED, but check its terms page before use).
    Do not use FRED or ALFRED.
  - Klein and Goldberger (1955): archive.org lists copies (identifiers such as
    `econometricmodel0000klei`); they may be lending-only: if the text cannot be read, record it as
    not obtained and describe the model only from what can be verified (Klein's Nobel lecture and
    autobiography on nobelprize.org, a Cowles monograph or paper that describes it).
- Figures: the UK curve (scatter and fitted curve, 1861–1913, with 1948–57 marked); the US menu
  (Samuelson and Solow's two points against the US record of the 1950s and 1960s, ending in 1969: the
  1970s are Ch 44's); optionally the small model's simulated path.
- Ending: return to the opening and hand over Ch 39's question “政府一次性发钱，人们会花掉多少？企业凭什么决定投资？”
  (read its stub's guide box): the big models' largest blocks were the consumption and investment
  equations.
- Labels: `sec:phillips-…`, `eq:phillips-…`, `fig:phillips_…`, `tab:phillips-…`, `ex:phillips-…`.
- Length: 8,000–9,000 characters of main text.

### Carried over from the editor's round on Chapter 38
- A document with parts by different authors is attributed part by part: the 1962 *Economic Report of
  the President* is Kennedy's report (pp. iii–27, signed) and the Council of Economic Advisers' Annual
  Report (from p. 31); each sentence goes to the author of the part it is on, by page, and the check
  script tests the page. Documents are not the subjects of sentences ("报告说"): name the author.
- Keep a source's mood: a conjecture ("It would seem plausible"), a rhetorical question, a figure
  caption or a "this suggests … may have been" is not a finding; a hedge in the source stays in the
  translation.
- Check what a source actually correlated or measured, not only its title: Fisher's title says
  unemployment, his computation uses an employment index (the Harvard Committee's, built from both).
- A compare box states what each side claimed or assumed (the Cowles programme assumed autonomous
  relations that hold in changed conditions), not what a later critique says it cannot do; the
  critique is the later chapter's.
- Relative time words are read at the document's date: "after the war" in a report of 1936 means
  after the First World War ("一战以后").
- An authority record's source note can give dates its heading lacks (Okun: LoC n50025079, Who Was Who
  in America, vol. 7); record the note and its source as rows.
- Rows read on page images are not checked by `verify_web_quotes.py`: the reviewer renders those
  pages and checks each by eye.
- Quoted text: NARRATIVE §7.1 sets an upper limit (at most 15% of the main text), not a lower one.

## 第 39 章 `ch:consumption` 消费与投资理论 (`zh/ch39_consumption.tex`)

A theory chapter, like Chapters 33, 37 and 38: the theories of consumption and investment are the
spine; who built them, from what evidence, and how they were tested are the story. Model chapters:
zh/ch33_islm.tex and zh/ch38_phillips.tex.

- Neighbours:
  - Ch 32 owns Keynes's consumption function and multiplier (`eq:generaltheory-cross`,
    `ex:generaltheory-cross`, $C=a+cY$), the marginal efficiency of capital and "animal spirits"
    (`sec:generaltheory-expectations`, Kuznets's investment figures `ex:generaltheory-kuznets`), and the
    British counter-example (real consumption up 2.1% in 1929–32 while real GDP fell 5.3%,
    `sec:generaltheory-check`, self-check 5: "要用别的原因解释"). Use its letters; explain the
    counter-example with the new theories.
  - Ch 33 owns the investment demand $I=I_0-bi$ in IS–LM; Ch 38 owns Klein's Model I, whose
    consumption equation (0.80 of the wage bill, 0.02 and 0.23 of this year's and last year's profits)
    and investment equation (profits and the capital stock) drive its multipliers and cycle; Ch 38 ends
    with this chapter's question. Refer back in a clause.
  - Ch 3 owns the Fisher relation, present values and bond prices (`eq:prices-fisher`); Ch 2 the
    national accounts and the saving identity; Ch 25 Fisher's *Theory of Interest* (money illusion).
    Use their notation for the real interest rate and discounting.
  - Later chapters own: Ch 40 the saving rate in growth (Solow; its stub asks “长期增长为什么不能只靠多储蓄？”);
    Ch 42 Japan's high growth and industrial policy; Ch 48 rational expectations (Muth 1961) and the
    Lucas critique; Ch 50 Ricardian equivalence (Barro 1974); Ch 53 the Euler equation in real
    business cycle models; Ch 58 Japan's bubble; Ch 65 financial frictions; Ch 68 fiscal multipliers;
    Ch 71 heterogeneity, hand-to-mouth households and the MPC in HANK models; Ch 73 the transfers of
    2020; Ch 79 ageing and the life-cycle model. Here each is at most a sentence with `\chref`.
- Owns:
  - the puzzle: Kuznets's long-run evidence that the share of income saved did not rise with income
    over decades (NBER, if obtained: *Uses of National Income in Peace and War*, 1942, or *National
    Product since 1869*, 1946), against the cross-section and short-run evidence that fits Keynes's
    falling average propensity; how Friedman (1957) and Modigliani state the puzzle;
  - the life-cycle hypothesis: Modigliani and Brumberg (1954) and Ando and Modigliani (1963), through
    what can be obtained (Modigliani's Nobel lecture of 1985 on nobelprize.org, "Life Cycle, Individual
    Thrift, and the Wealth of Nations"; anything else verified). Its key aggregate result: the saving
    rate depends on the growth rate of income and the age structure, not on the level of income;
  - the permanent-income hypothesis: Friedman (1957, *A Theory of the Consumption Function*, NBER, full
    text on nber.org: NBER © notice, short quotations): permanent and transitory income, $c=kY_p$, how
    he read the cross-section and time-series evidence, and what a transitory windfall should do;
  - the Euler equation and Hall (1978, *JPE*; his NBER working paper 170 of 1977, if on nber.org):
    intertemporal smoothing, the random walk under his assumptions, his test (lagged income does not
    predict the change in consumption; what he found about stock prices). Rational expectations as
    an assumption here, explained in a sentence; their theory is Ch 48's;
  - investment: Jorgenson (1963, *AER* Papers and Proceedings, "Capital Theory and Investment
    Behavior") and the user cost of capital; Hall and Jorgenson (1967, *AER*, "Tax Policy and
    Investment Behavior") on the investment tax credit of 1962 (the credit itself from the Revenue Act
    of 1962 and the *Economic Report of the President*, public domain); Tobin's $q$ (Tobin 1969, *JMCB*;
    Brainard and Tobin 1968; Cowles Foundation papers on cowles.yale.edu, if the papers open there).
    Hayashi (1982) on marginal and average $q$ in a sentence, if verified;
  - the tests with one-off payments: the US tax rebate of 1975 (Modigliani and Steindel 1977, *BPEA*,
    on brookings.edu, if obtained; Blinder 1981), the rebates of 2001 (Johnson, Parker and Souleles
    2006, *AER*; NBER working paper) and the stimulus payments of 2008 (Parker, Souleles, Johnson and
    McClelland 2013, *AER*; NBER working paper), Japan's shopping coupons of 1999 (Hsieh, Shimizutani
    and Hori 2010, NBER working paper): what share of a payment was spent, on what, and how soon. The
    transfers of 2020 are Ch 73's; heterogeneity of the MPC is Ch 71's (a sentence each).
- Promises (FORWARD_REFS rows pointing to 39): from Ch 32 (the consumption function rewritten by the
  permanent-income and life-cycle theories; the British counter-example of 1929–32) and Ch 38 (the
  question; Model I's consumption and investment equations). Mark each done with the labels.
- The case: Japan's high saving rate (the PLAN's case): the household saving rate from the national
  accounts (Cabinet Office ESRI, www.esri.cao.go.jp answered on 2026-10-29: read its terms of use,
  copy them verbatim; note the SNA basis and breaks in the series), its rise in the high-growth years
  and its peak; the explanations and their disputes: the life-cycle model with fast growth and a young
  population (Modigliani; Horioka's surveys, NBER or ESRI working papers, if obtained), measurement
  (Hayashi 1986, *NBER Macroeconomics Annual*, "Why Is Japan's Saving Rate So Apparently High?", on
  nber.org), bonuses, the cost of housing and land, the social security system, culture. The fall of
  the rate with ageing gets one sentence pointing to Ch 79; the bubble to Ch 58.
- When it begins: Ch 38 ends with the question. A candidate opening is a one-off payment and what
  people did with it (the 1975 rebate, or Japan's coupons of 1999), or Friedman's or Modigliani's own
  moment; choose what the documents support.
- Teaching (`eq:consumption-…`, worked examples with teaching inputs or the sources' own numbers):
  - the two-period budget constraint and the Euler equation (with Ch 3's discounting); the random
    walk as a special case, with its assumptions stated;
  - a one-off payment of a given size under three theories: Keynes's MPC (Ch 32's $c$), the
    permanent-income rule (annuity value at interest rate $r$) and the life-cycle rule (spread over the
    remaining years): how much is spent in the first year;
  - the life-cycle saving pattern (work years, retirement years) and the aggregate saving rate with and
    without growth of income: why faster growth raises the saving rate in the model (the Japanese
    case);
  - the user cost $c=p_K(r+\delta)$ (with taxes and the investment tax credit as an extension, if
    Hall and Jorgenson are obtained), the desired capital stock with a Cobb–Douglas technology, and
    investment as gradual adjustment; Tobin's $q$ as the ratio of market value to replacement cost and
    what it implies for investment; the two related in a sentence (Hayashi 1982, if verified);
  - an estimate from a rebate study read as an MPC: what the share spent says about the three
    theories.
- Compare boxes (the PLAN's candidates): 生命周期假说 vs 持久收入假说; 乔根森投资模型 vs 托宾 $q$. Every cell
  must belong to the two theories compared, with the authors' own statements.
- Contested questions (do not decide; each side's strongest case and its own concessions):
  - Do households smooth consumption as the theories say, or spend windfalls? Hall's random walk and
    Friedman's transitory income against the rebate studies (and "excess sensitivity", Flavin 1981, in a
    sentence if verified); liquidity constraints as the reconciliation offered by the rebate authors
    themselves.
  - Why was Japan's saving rate so high? Life cycle and growth against measurement and institutions
    (Hayashi 1986; Horioka). Read what each actually concluded.
  - What drives investment: the user cost and $q$, or cash flow and sales (the accelerator; Fazzari,
    Hubbard and Petersen 1988, *BPEA*, on brookings.edu, against Kaplan and Zingales 1997, if obtained)?
    One paragraph; financial frictions are Ch 65's.
- Political character (write_template rule 5): who receives a one-off payment and who pays for it;
  who gains from an investment tax credit; said plainly with the sources' own words where they exist
  (the 1962 and 1975 reports and debates), without softening or inflating.
- Data and sources (journal issues, dates and working-paper numbers in this list are leads, not
  evidence: verify each; probed 2026-10-29: www.nber.org, cowles.yale.edu, web.stanford.edu,
  www.nobelprize.org, www.esri.cao.go.jp, www.stat.go.jp, www.e-stat.go.jp, www.boj.or.jp,
  www.imes.boj.or.jp, www.mof.go.jp, www.bea.gov, apps.bea.gov, www.federalreserve.gov,
  www.brookings.edu, www.aeaweb.org, www.econstor.eu, ideas.repec.org, www.irs.gov, www.census.gov,
  economics.mit.edu answered; www.ssa.gov and www.cbo.gov answered 403; www.econ.yale.edu did not
  answer; www.jstor.org answers with a bot check: do not try it):
  - NBER books and working papers on nber.org (Friedman 1957, Kuznets, Hayashi 1986, the rebate
    papers): short quotations with the © notice exactly as printed;
  - BEA NIPA tables (personal saving rate, consumption; public domain) and the Economic Report of the
    President (govinfo or the American Presidency Project) for US series; do not use FRED or ALFRED;
  - Japan: ESRI national accounts (household saving rate), Statistics Bureau family income and
    expenditure surveys (www.stat.go.jp), with their terms copied verbatim; Bank of Japan data: credit
    "Bank of Japan";
  - the UK figures of Ch 32's counter-example from the BoE millennium workbook (cached under
    ~/.cache/finance-study/boe; see data/SOURCES.md), if a figure is redrawn.
- Figures: the three theories' responses to a one-off payment (teaching); the life-cycle profile of
  income, consumption and wealth; Japan's household saving rate (and growth) from the national
  accounts; optionally the user cost or $q$ against investment.
- Ending: return to the opening and hand over Ch 40's question “长期增长为什么不能只靠多储蓄？” (read its
  stub's guide box): the saving that this chapter explains is what Solow's model takes as given.
- Labels: `sec:consumption-…`, `eq:consumption-…`, `fig:consumption_…`, `tab:consumption-…`,
  `ex:consumption-…`.
- Length: 8,000–9,000 characters of main text.

### Carried over from the editor's round on Chapter 39
- Who received money is read from the law itself, section by section, not from a speech about it: the
  Tax Reduction Act of 1975 has the rebate (§6428), the special payment of 50 dollars to three groups
  of benefit recipients (§702) and a new refundable earned income credit (§43, §204); a sentence on who
  got nothing must account for every payment the law makes.
- Read the unit of a rule: "each individual", with a joint return counted as one individual, is per
  return, not per person; state phase-outs exactly (which part phases out, between which incomes).
- Say which restriction a test statistic tests (one lag of income or four), with its own critical
  value.
- A worked example uses the estimate that matches its assumptions (Hall's log-utility 0.996, not the
  quadratic-utility 1.011).
- A list announced with a number is given in full (Modigliani's six propositions, Kennedy's six
  reforms), or described without the number (Chapter 37's lesson again).
- An equation taken from a source is copied in full, with its conditions and the source's notation,
  and checked against the page image.
- Name a measure as the source does: Hall and Jorgenson's "effective rate" of the credit is not an
  effective tax rate.
- A line that sits on an axis at the figure's scale gets its own labelled leader line.
- After the pause at Chapter 39 ("39章写完后暂停并提交", 2026-10-29) the author asked to continue
  ("继续", 2026-11-06); the section for Chapter 40 follows.

## 第 40 章 `ch:solow` 索洛增长模型 (`zh/ch40_solow.tex`)

A theory chapter, like Chapters 33, 37, 38 and 39: the model is the spine; who built it, from what
problem, and how it was taken to the data (growth accounting, convergence) are the story. Model
chapters: zh/ch33_islm.tex and zh/ch39_consumption.tex.

- Neighbours:
  - Ch 2 owns the national accounts and the capital-stock identity $K_{t+1}=K_t+I_t-D_t$
    (`eq:accounts-capital`) and the saving identity: use them, do not re-derive them.
  - Ch 18 splits output per head into productivity and the share of useful labour
    (`eq:smith-twofactors`); Ch 21 owns the Malthusian model (`eq:divergence-escape`), the two-factor
    TFP with land and labour (`ex:divergence-tfp`, `sec:divergence-test`) and the industrial
    revolution's numbers. The rows from Ch 18 and Ch 21 ask for growth accounting with capital: say
    once why two-factor TFP includes capital deepening and so overstates three-factor TFP.
  - Ch 22 (`sec:marx-legacy`, `fig:marx_uk`, `fig:marx_shares`): the UK wage share and profit proxy of
    1855–1913 and the Engels' pause; the stylised facts of factor shares (Kaldor 1961, if obtained)
    start here, the inequality debate is Ch 71's.
  - Ch 31 owns the Soviet growth estimates of 1928–1987 (`tab:soviet-growth`, Harrison 1993, the
    Gerschenkron effect `eq:soviet-index`): refer back, do not retell them. Ch 34 owns Domar (1944) on
    the debt burden with a growing income (`ex:warfinance-domar`); Domar's growth model of 1946 is
    this chapter's. Harrod's and Domar's life dates are in Ch 33 and Ch 34.
  - Ch 39 ends with this chapter's question: life-cycle saving rises with growth, Japan's household
    saving peaked as growth slowed. Saving that depends on growth is a reason why a regression of
    growth on saving is not the model's causal effect: say so in a sentence where the tests come.
  - Later chapters own: Ch 41 development (Lewis, import substitution, the big push; its stub asks
    “穷国怎样起飞？”), Ch 42 East Asia and the Krugman–Young growth-accounting debate, Ch 43 the mature
    planned economies (Kosygin, Kornai), Ch 56 endogenous growth (Romer, Lucas, AK), Ch 59 transition,
    Ch 71 inequality and factor shares (Piketty), Ch 79 demography and AI. Here each is at most a
    sentence with `\chref`.
- Owns:
  - the problem Solow answered: Harrod (1939, *Economic Journal*) and Domar (1946, *Econometrica*), the
    fixed capital–output ratio and the "knife-edge" (whose phrase, verify), through the papers if
    obtained, otherwise through Solow's own account (Solow 1956's introduction; his Nobel lecture of
    1987, "Growth Theory and After", nobelprize.org);
  - Solow (1956, *QJE*, "A Contribution to the Theory of Economic Growth") and Swan (1956, *Economic
    Record*, "Economic Growth and Capital Accumulation"): a production function with substitution, the
    accumulation equation, the steady state and its stability; the answer to the guide question
    (in the model a higher saving rate raises the level of output per worker, not its long-run growth
    rate, which technical progress sets); the golden rule (Phelps 1961, *AER*, "The Golden Rule of
    Accumulation", in a paragraph if obtained); the speed of convergence;
  - Solow (1957, *Review of Economics and Statistics*, "Technical Change and the Aggregate Production
    Function"): his data (US non-farm output per man-hour, 1909–1949), his method, the share of growth
    he attributed to technical change, and the residual; Abramovitz (1956, NBER, "Resource and Output
    Trends in the United States since 1870", on nber.org, NBER © notice) and his "measure of our
    ignorance" (verify the words and who said them first);
  - convergence: Baumol (1986, *AER*) and De Long's (1988, *AER*) objection (selection on ex-post
    success), Barro (1991, *QJE*) and Barro and Sala-i-Martin (1992, *JPE*; NBER working papers) on
    conditional convergence (the rate they estimate), Mankiw, Romer and Weil (1992, *QJE*; NBER working
    paper 3541 of 1990, on nber.org): the augmented model with human capital and what share of
    cross-country differences it explains, with the capital share it implies; Pritchett (1997,
    *Journal of Economic Perspectives*, "Divergence, Big Time": JEP is open on aeaweb.org) for the long
    run. Test absolute and conditional convergence on Penn World Table 10.01 (CC BY 4.0: cite Feenstra,
    Inklaar and Timmer 2015 as its terms ask) or the Maddison Project 2023 (cached; CC BY 4.0 with its
    citation policy);
  - the case: the Soviet Union's high investment and slowing growth after 1950 (the PLAN's case):
    Easterly and Fischer (1995, *World Bank Economic Review*; World Bank policy research working paper
    1284 of 1994 on documents.worldbank.org, if it opens: the investment share, the growth rates by
    period, their reading with a low elasticity of substitution after Weitzman 1970, *AER*, if
    obtained), with Ch 31's estimates referred back; the CIA's and the Joint Economic Committee's
    estimates (US government, public domain; www.cia.gov answered on 2026-11-06, www.jec.senate.gov did
    not) if a table can be had; Krugman (1994) only in a sentence pointing to Ch 42.
- Promises (FORWARD_REFS rows pointing to 40): from Ch 18 (growth accounting), Ch 21 (growth
  accounting with capital; two-factor TFP overstates three-factor TFP), Ch 22 (factor shares over
  growth: the stylised facts) and Ch 39 (the question; saving taken as given). Mark each done with the
  labels; where a row also names Ch 71, say which half was kept.
- When it begins: Ch 39 ends with the question. A candidate opening is Solow's own moment (the paper
  of February 1956, or his account in the Nobel lecture of why he distrusted the knife-edge), or the
  Soviet claim to overtake the West with ever more investment; choose what the documents support.
- Teaching (`eq:solow-…`, worked examples with teaching inputs or the sources' own numbers):
  - the model with Cobb–Douglas $y=k^{\alpha}$: $\Delta k=s\,y-(n+\delta)\,k$ (state where it differs
    from Solow's 1956 notation: he had no depreciation in the basic case), the steady state
    $k^{*}=(s/(n+\delta))^{1/(1-\alpha)}$, the elasticity of $y^{*}$ with respect to $s$, $\alpha/(1-\alpha)$;
    with labour-augmenting technical progress at rate $g$, the balanced growth path;
  - examples: doubling the saving rate (the level effect and the time it takes); the transition path
    and the half-life with $\lambda\approx(1-\alpha)(n+g+\delta)$ (a simulation, as Ch 38's Model I);
    the golden rule ($s=\alpha$ under Cobb–Douglas) and who gives up consumption to reach it; growth
    accounting $g_Y=\alpha g_K+(1-\alpha)g_L+g_A$ with Solow's own 1909–49 numbers; a reading of the
    Soviet numbers with the model (a rising investment share and falling growth);
  - the stylised facts as the model's targets (constant growth of output per worker, a stable
    capital–output ratio and stable factor shares), with Ch 22's UK numbers and PWT's labour share.
- Compare boxes (the PLAN's candidates): 水平效应 vs 增长效应; 绝对收敛 vs 条件收敛. Every cell must
  belong to the side it is under, with the authors' own statements.
- Contested questions (do not decide; each side's strongest case and its own concessions):
  - Is the residual technology or mismeasurement? Solow and Abramovitz against Jorgenson and Griliches
    (1967, *Review of Economic Studies*, "The Explanation of Productivity Change", if obtained), with
    Denison's reply if obtained;
  - Do poor countries catch up? Baumol against De Long; conditional convergence (Barro, Mankiw–Romer–
    Weil) against Pritchett's divergence;
  - Why did Soviet growth slow: diminishing returns to capital with low substitution (Easterly and
    Fischer; Weitzman), or incentives and innovation in the system (the planned economy's mechanics
    are Ch 43's: a sentence).
- Political character (write_template rule 5): a higher saving rate is paid for in consumption now;
  who chose the Soviet investment share and who bore the forgone consumption, said plainly with the
  sources' words where they exist (Ch 31 owns the famine of 1932–33: refer back in a clause, do not
  retell it).
- Data and sources (journal issues, dates and working-paper numbers in this list are leads, not
  evidence: verify each; probed 2026-11-06: www.rug.nl, dataverse.nl, documents.worldbank.org,
  openknowledge.worldbank.org, www.nber.org, www.nobelprize.org, www.cia.gov, archive.org,
  economics.mit.edu, www.anu.edu.au, www.econlib.org, fraser.stlouisfed.org, www.bea.gov,
  www.govinfo.gov, delong.typepad.com and eh.net answered; www.jec.senate.gov, scholar.harvard.edu,
  www.bls.gov and www.imf.org answered 403; www.ggdc.net and web.stanford.edu did not answer;
  www.jstor.org answers with a bot check: do not try it):
  - Solow (1956, 1957), Swan (1956), Harrod (1939), Domar (1946), Phelps (1961), Baumol (1986), De Long
    (1988), Barro (1991), Jorgenson–Griliches (1967): in copyright, short phrases only; look for
    copies on course pages or the authors' sites (read to verify, record URL, date and SHA-256, never
    commit the file), else record each as not obtained;
  - NBER working papers and books on nber.org (Abramovitz 1956, Mankiw–Romer–Weil, Barro and
    Sala-i-Martin): the © notice exactly as printed; JEP articles on aeaweb.org: read the AEA's terms;
  - World Bank working papers: copy the licence or rights statement printed in the document;
  - PWT 10.01 and the Maddison Project 2023: CC BY 4.0 with their citation requirements; BEA tables:
    public domain.
- Figures: the Solow diagram ($s\,y$ and $(n+\delta)k$ for two saving rates); the transition path after
  a rise in the saving rate (level and growth rate of output per worker); convergence scatters (all
  countries and a rich-country subset, or absolute against conditional); the Soviet investment share
  and growth by period.
- Ending: return to the opening and hand over Ch 41's question “穷国怎样起飞？” (read its stub's guide
  box): the model says where a poor country would go if it saved and invested like a rich one, not how
  it starts.
- Labels: `sec:solow-…`, `eq:solow-…`, `fig:solow_…`, `tab:solow-…`, `ex:solow-…`.
- Length: 8,000–9,000 characters of main text.

### Carried over from the editor's round on Chapter 40
- A sentence cited to a source must be in that source. The draft hung "计划经济里，投资率由中央定" on
  Solow's Nobel lecture, which does not say it; the source that does speak to who chooses the saving
  rate is Solow (1956, p. 93, "Policy Implications"). An inference from the model or a case is the
  book's and says so.
- A conclusion carried into another chapter keeps the conditions of its derivation: Ch 21's two-factor
  TFP overstates three-factor TFP only if capital per worker rose (Ch 21 itself says “一般”).
- When an author gives reasons for a reservation, give those reasons (Baumol's footnote 5: the 1870
  figures were back-extrapolated, and initial income is on both sides of the regression), not a
  neighbouring argument from another passage (the 72 countries serve a different point).
- Compare rival estimates over the same period: Denison's 1.37 is for 1950–1962, where Jorgenson and
  Griliches get 0.30; the choice of period explains 0.20 of the gap. The period is part of the dispute.
- A breakdown known only through another author's account is framed as such (Denison's 1929–1982
  split “据索洛的转述”).
- Keep the speaker's own caveat next to the claim reported (Solow's "Well, not simply": doubling the
  planned saving rate does not double the actual one unless investment keeps pace).
- Name a dataset's variable as it is defined (PWT `rgdpna` real GDP, `labsh` the share of labour
  compensation in GDP, both capital and output at constant prices for K/Y), and say in a table's note
  exactly what the regression ran.
- A simulated comparison says what it compares: consumption per effective worker catches up with the
  path without the higher saving rate, not with its old level.
- Report a dataset's own quality flags for the observations the text relies on: PWT 10.01 marks price
  levels as outliers (`i_outlier`), exchange rates as estimated (`i_xr`), and some investment shares are
  above GDP (Malta 1960–1961); keep the flags in the snapshot and say once what the book did with them.
- Place names in a list of economies: 台湾、香港 (the author's decision of 2026-11-06, “台湾、香港即可，
  不用考虑忌讳”, now in docs/STYLE.md §3); 中国大陆 only where it must be told apart from them in the same
  list, otherwise 中国. The reviewer's 中国台湾、中国香港 in Ch 40 was changed back.
- The author does not want the NBER working papers replaced by their journal versions (2026-11-06,
  “不用了”): cite the version actually read.
- When fixes push the main text over 9,000 characters, cut peripheral sentences and keep their snapshot
  rows and checks.

## 第 41 章 `ch:development` 发展经济学：二元经济、进口替代与大推进 (`zh/ch41_development.tex`)

A theory-and-policy chapter: the models (Lewis's dual economy, the Prebisch–Singer terms of trade,
the big push) are the spine; the case is how governments in Latin America, India and Ghana acted on
them after 1945, who decided and who paid. Model chapters: zh/ch40_solow.tex (theory with a case and a
data test) and zh/ch31_soviet.tex (a planned industrialisation told with its costs).

- Neighbours:
  - Ch 40 owns Harrod–Domar, the Solow model, Swan's elastic labour supply ("the typical classical
    answer"), the convergence tests on PWT 10.01 and Pritchett's divergence: use them in a clause
    (`eq:solow-steady`, `tab:solow-convergence`), do not re-derive them. Ch 40 ends with this
    chapter's question and says the next chapter starts from surplus labour and the dual economy.
  - Ch 24 owns the periphery in the first globalisation (India's silver rupee, Naoroji's drain,
    Maddison's quarter of India's savings sent abroad); Ch 29 owns the Depression's terms-of-trade
    shock and Prebisch at the Banco Central de la República Argentina, 1935–1943 (his life dates are
    there); Ch 31 owns Soviet industrialisation, the scissors and Cheremukhin et al.'s finding of no
    support for the big push (`ch:soviet`): refer back in a clause.
  - Later chapters own: Ch 42 East Asia (export orientation in practice, Japan's and Korea's industrial
    policy, the growth-accounting debate; the compare box 进口替代 vs 出口导向 here states the two
    strategies, the East Asian evidence is Ch 42's), Ch 43 planned economies (China's First Five-Year
    Plan and the Great Leap famine), Ch 51 the Latin American debt crisis of 1982 (how ISI was
    financed in the 1970s and ended), Ch 52 the hyperinflations, Ch 56 endogenous growth, Ch 61
    emerging-market crises, Ch 72 China's credit and its Lewis turning point if that chapter takes it,
    Ch 78 tariffs and industrial policy today, Ch 79 demography. Here each is at most a sentence.
- Owns:
  - Lewis (1954, *Manchester School*, "Economic Development with Unlimited Supplies of Labour"): the
    subsistence sector and the capitalist sector, the wage fixed at a margin above subsistence, the
    reinvested profits, the rising share of profits and saving (his question of how a community
    saving 4 or 5 per cent of national income comes to save 12 to 15 per cent: verify the words; it
    answers Ch 40's saving rate), the turning point; Lewis's Nobel lecture of 1979 and Schultz's
    (both on nobelprize.org, © The Nobel Foundation) for the later accounts and the objection that
    the marginal product of farm labour is not zero (Schultz 1964, if obtained, only through his own
    lecture otherwise);
  - Prebisch (1950, UN ECLA, *The Economic Development of Latin America and its Principal Problems*;
    a copy on archive.org: verify the edition and the UN's terms) and Singer (1950, *AER* Papers and
    Proceedings, "The Distribution of Gains between Investing and Borrowing Countries"); the UN's
    *Relative Prices of Exports and Imports of Under-developed Countries* (1949) if it can be had from
    digitallibrary.un.org; the thesis, the numbers they used (the UK's terms of trade from 1876), and
    the objections (Viner, Haberler, or later tests such as Grilli and Yang 1988 if obtained);
  - import-substituting industrialisation in practice: Latin America after 1945 (Argentina, Brazil,
    Mexico: tariffs, multiple exchange rates, state firms), with data that can be had (MOxLAD, INEGI,
    the Maddison Project 2023, WDI); the effective rate of protection (Balassa, Corden; a worked
    example); the critiques (Little, Scitovsky and Scott 1970; Krueger 1974 on rent-seeking) and the
    defence (Hirschman; the industry that ISI built);
  - the big push: Rosenstein-Rodan (1943, *Economic Journal*, "Problems of Industrialisation of
    Eastern and South-Eastern Europe"), Nurkse (1953) and Hirschman (1958) in a sentence each,
    Murphy, Shleifer and Vishny (1989, *JPE*; NBER working paper 2708, on nber.org, © notice as
    printed) for the coordination failure and the two equilibria; Easterly (1999, "The Ghost of
    Financing Gap", World Bank policy research working paper 1807, documents.worldbank.org: copy its
    rights statement) on the Harrod–Domar financing-gap model in aid practice (a bridge to Ch 40);
  - the cases (the PLAN's): India's five-year plans (the Second Plan of 1956 and the Mahalanobis
    model: heavy industry first; Planning Commission documents on niti.gov.in or archive.org; read
    the Indian government's terms of use), Ghana after independence (Nkrumah, the Seven-Year
    Development Plan of 1963–64 on archive.org, the Volta River project, the Cocoa Marketing Board's
    producer price against the world price), Latin American ISI.
- Promises (FORWARD_REFS rows pointing to 41): from Ch 14 (institutions with long-run effects: Dell's
  mining mita), Ch 21 (Allen's question reversed: why low-wage countries should use technology made
  for high wages; how poor countries take off), Ch 24 (where the savings of poor countries go:
  Maddison's quarter of India's savings) and Ch 40 (the question; the 27 poorest in 1960, 13 of which
  grew more slowly than the richest quarter; why saving, population and technology differ). Mark each
  done with the labels, or say why a row passes on.
- When it begins: Ch 40 ends with the question. Candidate openings: Lewis's article of May 1954 and
  its first question; Prebisch's ECLA report of 1949–50 (presented at Havana, verify); Ghana's
  independence day, 6 March 1957; India's Second Plan presented to Parliament in 1956. Choose what
  the documents support. "起飞" is Rostow's word (1956, *EJ*, "The Take-Off into Self-Sustained
  Growth"; 1960): say whose word it is if the chapter uses it, in a clause.
- Teaching (`eq:development-…`, worked examples with teaching inputs or the sources' own numbers):
  - Lewis's model: capitalist-sector labour demand from $\partial Y_c/\partial L_c=w$ with
    $Y_c=A\,K^{\alpha}L_c^{1-\alpha}$, the wage fixed while surplus labour lasts, profits $\alpha Y_c$
    reinvested, so the capitalist sector and the saving rate of the whole economy rise; the turning
    point when the subsistence sector's surplus is used up (a simulation with teaching inputs: when is
    the turning point reached, and how does the economy's saving rate move from about 5% towards 12%?);
  - the net barter terms of trade $P_x/P_m$ and the income terms of trade; the effective rate of
    protection $(t_f-a\,t_m)/(1-a)$ with an example; the big push as two equilibria (a firm's
    profit depends on how many others industrialise: a two-line payoff example); the financing gap
    $I/Y=\text{ICOR}\times g$ and why Ch 40's model says it misleads.
- Compare box (the PLAN's candidate): 进口替代 vs 出口导向, each cell with the authors' own
  statements; a second if the material earns it (平衡增长 vs 不平衡增长: Nurkse against Hirschman).
- Contested questions (do not decide; each side's strongest case and its own concessions):
  - Is there surplus labour with a marginal product near zero? Lewis against Schultz (and Sen if
    obtained);
  - Did primary producers' terms of trade decline in the long run? Prebisch and Singer against their
    critics and the later tests;
  - Did import substitution fail, or did it build the industry that later exported? Krueger and Little
    et al. against Hirschman and the structuralists (the East Asian comparison is Ch 42's: a sentence);
  - Big push and aid: Rosenstein-Rodan and Murphy–Shleifer–Vishny against Easterly.
- Political character (write_template rule 5): who decided and who paid. The planners chose heavy
  industry and the investment rate (India); the marketing board paid cocoa farmers less than the world
  price and the state spent the difference (Ghana); tariffs and overvalued exchange rates taxed
  exporters and consumers to favour industry (Latin America); in Lewis's model the wage is held down
  while profits rise. Say it plainly with the sources' own words and numbers; the one-party state in
  Ghana and the Preventive Detention Act in a clause if the sources support it.
- Data and sources (journal issues, dates and document numbers in this list are leads, not evidence:
  verify each; probed 2026-11-06: archive.org, digitallibrary.un.org, www.nber.org, niti.gov.in,
  documents.worldbank.org, openknowledge.worldbank.org, databank.worldbank.org, www.nobelprize.org,
  eprints.lse.ac.uk, www.gutenberg.org, en.wikisource.org, www.ilo.org, www.rug.nl, dataverse.nl,
  www.indianculture.gov.in, www.rbi.org.in, www.mospi.gov.in, www.indiabudget.gov.in,
  dspace.gipe.ac.in, moxlad.cienciassociales.edu.uy, www.inegi.org.mx, www.bcra.gob.ar,
  www.bog.gov.gh, statsghana.gov.gh, unstats.un.org, www.wto.org, eh.net, eml.berkeley.edu,
  www.econlib.org, fraser.stlouisfed.org, www.cia.gov and www.govinfo.gov answered;
  repositorio.cepal.org, www.cepal.org, www.wider.unu.edu, babel.hathitrust.org, www.ibge.gov.br,
  scholar.princeton.edu and www.princeton.edu answered 403; planningcommission.nic.in,
  egazette.gov.in, dbie.rbi.org.in, dpul.princeton.edu and www.econ.yale.edu did not answer;
  api.worldbank.org answered 404; www.jstor.org answers with a bot check: do not try it; archive.org
  has `1950-prebisch-un-the-economic-development-of-latin-america-and-its-principal-problems`,
  `micro_IA40244301_0028` (Ghana, Seven-year development plan, a brief outline) and
  `micro_IA40244302_0071` (India, Second five-year plan, a draft outline): verify each item's
  metadata and rights before use):
  - Lewis (1954), Singer (1950), Rosenstein-Rodan (1943), Rostow (1956), Nurkse, Hirschman, Krueger,
    Little–Scitovsky–Scott, Schultz: in copyright, short phrases only; look for copies on course pages
    or the authors' sites (read to verify, record URL, date and SHA-256, never commit the file), else
    record each as not obtained;
  - UN documents (Prebisch 1950, UN 1949): read the UN's terms of use; short phrases;
  - Government of India and Government of Ghana documents: read the terms that apply (India's
    Copyright Act s. 52(1)(q) for reports of committees and commissions; Ghana's copyright law) and
    record them; short phrases unless the terms allow more;
  - NBER working papers: the © notice exactly as printed; World Bank papers: copy the rights statement;
  - Maddison Project 2023 (cached; CC BY 4.0 with its citation policy), PWT 10.01 (CC BY 4.0, Feenstra,
    Inklaar and Timmer 2015), WDI (CC BY 4.0), MOxLAD and INEGI: read and record each one's terms.
- Figures: the Lewis diagram (the capitalist sector's labour demand shifting out along a flat wage
  until the turning point); a terms-of-trade series (Prebisch's own numbers or a later index);
  GDP per head of the cases against a benchmark (Maddison 2023: Argentina, Brazil, Mexico, India,
  Ghana, with Korea for the Ch 42 comparison); a protection or plan figure if the data support it.
- Ending: return to the opening and hand over Ch 42's question, the guide question of its stub
  (zh/ch42_eastasia.tex: whether the high growth of Japan and the four East Asian “小龙” was a miracle
  of productivity or the result of accumulation); copy it exactly from the stub.
- Labels: `sec:development-…`, `eq:development-…`, `fig:development_…`, `tab:development-…`,
  `ex:development-…`.
- Length: 8,000–9,000 characters of main text.

### Carried over from the editor's round on Chapter 41
- Who decided is read from the document's own words, paragraph by paragraph: in the 1958 résumé the
  Planning Commission submitted a memorandum and the National Development Council adopted the
  resolution that split the plan. A body that proposes is not the body that decides.
- A report that says it may not be quoted as representing an institution's views (the World Bank's
  project reports) is cited to "报告的作者", not to the institution.
- When a source gives the causes of an outcome, give its causes (PA-43a para. 3.01: four government
  decisions), not a mechanism the book prefers (farmers' response to price). A sentence that makes
  the source's facts fit the book's argument is the book's reading and is marked so.
- Keep every condition of a qualified judgment ("justifiable only … and if …"), and do not sharpen a
  source's vague phrase ("non-cocoa purposes" is not "investment").
- Two people set against each other in a debate must have answered each other, or the pairing is
  marked as the book's (Schultz's 1979 lecture does not mention Lewis).
- A document's date, its imprint and its signer are three facts: read each from the title page, the
  back of it and the letter, and do not merge them into an event ("printed at Lake Success on 27
  April").
- A trend word is checked against the whole series ("一路走低" when the table rises again three times).
- A worked example that combines two sources' numbers checks that they measure the same thing (net
  against gross investment) and says so where they do not.
- One letter, one meaning within a chapter: when two models use the same symbol for different things
  (the input share and productivity, value added and a wage premium), rename one and say where the
  source's symbol differs.
- A compare box's row compares like with like: a rationale from the time is not set against hindsight
  decades later.
- A figure's panel title states only what the data show at the scale drawn ("相差不到一倍", not "相近").
- Text-layer readings of numbers that matter are confirmed on the page image (the 1958 résumé's
  4500 read as "4600"); say in the 史料说明 which paragraphs were read on images.

## 第 42 章 `ch:eastasia` 东亚奇迹：日本高速增长与发展型国家 (`zh/ch42_eastasia.tex`)

A theory-and-history chapter: Chapter 40's growth accounting is the tool, applied to Japan's high
growth of 1955–1973 and to Korea, Taiwan, Hong Kong and Singapore; the developmental state (who chose
the industries, who allocated the credit, who paid) is the case. The guide question is the debate:
accumulation or productivity. Model chapters: zh/ch40_solow.tex (theory with a data test on PWT),
zh/ch41_development.tex (policy told as who decided and who paid) and zh/ch39_consumption.tex (the
Japanese case box and the ESRI series).

- Neighbours:
  - Ch 35 owns Japan's reconstruction (the Dodge Line, 360 yen, the Korean War procurement): start
    from it in a clause (FORWARD_REFS row from Ch 35). Ch 39 owns Japan's household saving rate (the
    ESRI series, about 9.2% real growth a year in 1956–1973, the peak of 1974 and 1976, Hayashi and
    Horioka): use its numbers through `\chref{ch:consumption}`, do not re-tell them. Ch 40 owns the
    Solow model, `eq:solow-accounting`, the convergence tests and Easterly and Fischer's report of
    Krugman's Soviet parable: use them, do not re-derive. Ch 41 owns import substitution against
    export orientation (the compare box, WDR 1987's four groups, the effective rate of protection,
    Korea against Ghana in `tab:development-paths`): build on it in a sentence.
  - Later chapters own: Ch 43 planned economies (China's First Five-Year Plan and the Great Leap),
    Ch 46 the end of Bretton Woods and the yen's float (1971–1973), Ch 47 the oil shock of 1973 (the
    end of Japan's high growth: a clause), Ch 56 endogenous growth (technology and catch-up as theory),
    Ch 58 Japan's bubble and lost decades, Ch 61 the Asian crisis of 1997–98 (the costs of the
    developmental state's finance: a clause at most), Ch 72 China, Ch 78 industrial policy today,
    Ch 79 demography. Each at most a sentence.
- Owns:
  - Japan 1955–1973: the growth record (ESRI's national accounts, cached for Ch 39; PWT 10.01, cached;
    Maddison 2023, cached); the Economic White Paper of July 1956 ("もはや「戦後」ではない", 内閣府
    www5.cao.go.jp: read the site's terms, 政府標準利用規約 if it applies); Ikeda's income-doubling plan
    (国民所得倍増計画, the cabinet decision of December 1960: its target rate and what happened; the
    text on worldjpn.net or the Cabinet Office: read the database's terms); MITI and industrial policy
    (Johnson 1982 is a book in copyright, likely not obtainable: through those who report it, framed as
    their report); financial repression (the Temporary Interest Rate Adjustment Law of 1947, the Bank
    of Japan's window guidance, the Fiscal Investment and Loan Program) with sources that can be had
    (Bank of Japan, IMES, Ministry of Finance, J-STAGE articles, NBER papers);
  - Korea: the government of Park Chung-hee from the coup of May 1961, the first five-year plan
    (1962–1966), the reforms of 1964–1965 (the devaluation and unified rate, the interest-rate reform),
    export targets, the heavy and chemical industry drive of 1973, state control of bank credit
    (Westphal 1990 *JEP* on www.aeaweb.org; Rodrik 1995, NBER WP 4964; KDI and K-Developedia documents:
    read the terms; the Bank of Korea's ECOS did not answer);
  - Taiwan: the land reform, the foreign-exchange reform of 1958–1960, the 1960 statute for the
    encouragement of investment, the export processing zone of 1966 (DGBAS national accounts on
    eng.stat.gov.tw or nstatdb.dgbas.gov.tw: read the open-data licence; Rodrik 1995);
  - Hong Kong and Singapore: Young (1992, "A Tale of Two Cities", NBER Macroeconomics Annual, on
    nber.org: © as printed): Singapore's investment rate and near-zero TFP growth against Hong Kong's;
    the Central Provident Fund (www.cpf.gov.sg, SingStat: read the terms);
  - the debate: World Bank (1993, *The East Asian Miracle*, documents.worldbank.org: copy the rights
    statement; who commissioned and paid for the study, if the foreword says so), Krugman (1994,
    *Foreign Affairs*, "The Myth of Asia's Miracle": in copyright and maybe behind a paywall; if not
    obtained, only through those who report it), Young (1995, *QJE*, "The Tyranny of Numbers"; NBER WP
    4680), Kim and Lau (1994) if obtained, Collins and Bosworth (1996, *Brookings Papers*, on
    brookings.edu), Hsieh (the dual approach with factor prices; a working-paper version if one can be
    had), Nelson and Pack (1999; World Bank PRWP 1881 if that is it: verify), Easterly and Fischer
    (1995, cached for Ch 40).
- Promises (FORWARD_REFS rows pointing to 42): from Ch 21 (Malthus on China's cheap labour and
  manufactures for foreign sale; East Asia's export-led path), Ch 35 (Japan's high growth after the
  Korean War procurement, told on from the Dodge Line), Ch 39 (Japan's high growth, with which the
  household saving rate rose), Ch 40 (accumulation or efficiency, Krugman's parable as Easterly and
  Fischer report it; Taiwan, Korea, Singapore and Hong Kong among the nine economies over 4% a year)
  and Ch 41 (the economies that turned to exports first; whether outward orientation caused growth or
  followed it; Korea's early move from import substitution to export expansion). Mark each done with
  the labels, or say why a row passes on.
- When it begins: Ch 41 ends with this chapter's question. Candidate openings: the Economic White
  Paper of July 1956; the cabinet decision on the income-doubling plan, 27 December 1960 (verify);
  Krugman's article of November/December 1994; the World Bank's report of September 1993. Choose what
  the documents support and give the date and the scene the sources allow, nothing more.
- Teaching (`eq:eastasia-…`, worked examples with teaching inputs or the sources' own numbers):
  - growth accounting with human capital, $g_Y=\alpha g_K+(1-\alpha)(g_L+g_h)+g_A$ (from Ch 40's
    `eq:solow-accounting`), applied with PWT 10.01 (rgdpna, rnna, emp, hc, labsh) to Japan and the
    four economies over the sources' periods: say which variables and years, and compare with Young's
    and Collins–Bosworth's numbers;
  - the dual approach: with constant shares, TFP growth equals the share-weighted growth of the
    rental rate and the wage (Hsieh's argument against Young for Singapore): derive it from the
    income identity $Y=rK+wL$;
  - financial repression: a ceiling on the deposit rate below inflation as a transfer from savers to
    the borrowers who got credit (a worked example with the sources' rates if they can be had);
  - a Solow transition: why a rising investment share gives fast growth for a time and then slower
    growth (Ch 40's `eq:solow-speed`; Krugman's argument as reported).
- Compare boxes (the PLAN's candidates): 要素积累 vs 生产率增长 (Young and Krugman against the World
  Bank and Hsieh, each cell with their own statements); 产业政策 vs 市场 (Johnson and those who
  report Amsden and Wade, against the World Bank's "market-friendly" reading), if the material earns it.
- Contested questions (do not decide; each side's strongest case and its own concessions):
  - accumulation or productivity (primal against dual; Singapore against Hong Kong);
  - did industrial policy pick winners, or did growth happen despite it (the World Bank 1993's mixed
    verdict and its critics; Korea's heavy and chemical industry drive);
  - did exports cause growth, or did the investment boom come first (Rodrik 1995 against the
    outward-orientation reading of Ch 41's World Bank groups);
  - financial repression: a cheap source of investment or a cost to savers that later fell due (a
    clause to Ch 58 and Ch 61).
- Political character (write_template rule 5): who decided and who paid. MITI and the Ministry of
  Finance in Japan, Park's government in Korea (a military government from 1961; credit through
  state-controlled banks; the export targets), the planners in Taiwan (martial law from 1949 to 1987:
  a clause if the sources support it), the Singapore government through the CPF; who paid: savers
  through controlled deposit rates, consumers through protected home markets, workers where the
  sources show suppressed wages or controlled unions. Say it plainly with the sources' own words and
  numbers; name places as STYLE.md §3 says (台湾、香港, no prefix).
- Data and sources (journal issues, dates and document numbers in this list are leads, not evidence:
  verify each; probed 2026-11-06: www5.cao.go.jp, www.esri.cao.go.jp, worldjpn.net,
  www.ioc.u-tokyo.ac.jp, documents.worldbank.org, openknowledge.worldbank.org, www.nber.org,
  www.brookings.edu, www.bok.or.kr, eng.stat.gov.tw, www.stat.gov.tw, nstatdb.dgbas.gov.tw,
  www.dgbas.gov.tw, www.singstat.gov.sg, tablebuilder.singstat.gov.sg, www.censtatd.gov.hk,
  www.boj.or.jp, www.imes.boj.or.jp, www.mof.go.jp, www.kdi.re.kr, www.kdevelopedia.org,
  www.archives.go.kr, www.foreignaffairs.com, web.mit.edu, dl.ndl.go.jp, warp.ndl.go.jp,
  www.stat.go.jp, www.e-stat.go.jp, kosis.kr, www.kantei.go.jp, www.ey.gov.tw, www.cbc.gov.tw,
  www.mof.gov.sg, www.cpf.gov.sg, www.mas.gov.sg, www.hkma.gov.hk, www.aeaweb.org, eml.berkeley.edu,
  www.econstor.eu, ideas.repec.org, www.jcer.or.jp, www.rieti.go.jp, www.jstage.jst.go.jp,
  www.piie.com, elibrary.imf.org, www.nobelprize.org, www.rug.nl, dataverse.nl and archive.org
  answered; www.meti.go.jp, www.ndc.gov.tw, www.mofa.go.jp, www.mod.go.jp, pubs.aeaweb.org,
  www.krugmanonline.com, scholar.harvard.edu, drodrik.scholar.harvard.edu, www.princeton.edu,
  www.oecd.org and www.imf.org answered 403; ecos.bok.or.kr, eng.kdi.re.kr, www.cepd.gov.tw,
  www.legco.gov.hk, www.pkarchive.org and www.econ.yale.edu did not answer; www.jstor.org answers with
  a bot check: do not try it):
  - Johnson (1982), Amsden (1989), Wade (1990), Krugman (1994), Young (1992, 1995), Kim–Lau, Collins–
    Bosworth, Hsieh, Rodrik, Westphal: in copyright, short phrases only; cite the version read
    (STYLE.md §3: the working paper if that is what was read);
  - Japanese government documents: read the site's terms (政府標準利用規約 or PDL 1.0) and record them;
    ESRI's terms as recorded for Ch 39; Bank of Japan: credit "Bank of Japan";
  - Korean, Taiwanese, Singaporean and Hong Kong government data and documents: read each one's
    terms and record them; short phrases unless they allow more;
  - World Bank documents: copy the rights statement; NBER: the © notice as printed;
  - PWT 10.01 (cached; CC BY 4.0, Feenstra, Inklaar and Timmer 2015) and Maddison 2023 (cached; CC BY
    4.0 with its citation policy, the original sources of each economy in a bib item).
- Figures: GDP per head of Japan, Korea, Taiwan, Hong Kong and Singapore against the United States,
  1950–2019 (PWT or Maddison, log scale); the growth-accounting decomposition (the book's PWT
  calculation beside Young's or Collins–Bosworth's numbers); the investment share over time
  (accumulation); a financial-repression or export figure if the data support it.
- Ending: return to the opening and hand over Ch 43's question “计划经济里的“通胀”藏在哪里？” (read its
  stub's guide box and copy the question exactly).
- Labels: `sec:eastasia-…`, `eq:eastasia-…`, `fig:eastasia_…`, `tab:eastasia-…`, `ex:eastasia-…`.
- Length: 8,000–9,000 characters of main text.
