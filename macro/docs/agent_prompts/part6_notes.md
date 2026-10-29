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
