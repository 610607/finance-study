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
