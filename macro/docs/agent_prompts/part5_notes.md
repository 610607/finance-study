# Part 5 (第五部分 战争、萧条与凯恩斯革命，1914—1945 年): notes for the chapter writers

Parts 1–4 are written and reviewed, so Part 5 is written against them. Chapters 26–34 are written one
at a time in that order (docs/WORKFLOW.md, sequential mode), each reviewed by one independent reviewer
before the next. Give the writer `batch_brief.txt` plus its section below. Sections for Chapters 28–34
are added when each is started; until then the neighbours named below divide the ground.

Part 5 moves from theory as it was written to policy under pressure: war finance, hyperinflation, the
return to gold, the Depression and the answers to it. Its evidence is of three kinds:

- **Contemporary texts.** Keynes (d. 1946) is public domain in the UK and, for works published before
  1930, in the US: quote briefly and record the copy used (Gutenberg, archive.org). Ohlin (d. 1979),
  Schacht (d. 1970), Bresciani-Turroni (d. 1963) and Eichengreen are in copyright: short phrases only,
  otherwise paraphrase with `% 据:` anchors. A participant's statement quoted by a later author is
  indirect testimony and is named as such once, in the 史料说明.
- **Official documents and statistics.** Laws and decrees (Reichsgesetzblatt texts on de.wikisource),
  League of Nations and Reparation Commission papers, the *Federal Reserve Bulletin* (FRASER), US
  Senate and Commission reports, and the German Statistisches Reichsamt are public domain. Prefer the
  original table to a later transcription; when only the transcription can be had, say so once.
- **Modern data.** As in Part 4 (BoE millennium, Maddison, JST, Riksbank, NBER, FRASER); run
  `tools/probe_network.sh` first.

Earlier chapters own (refer back, do not retell):
- Ch 1 `ch:intro`: Weimar's scale (`\subsubsection` 魏玛德国：一万亿倍; Koech's highest monthly rate
  29,525.71%, Reinhart–Rogoff's domestic debt 52.6% of GDP in 1920, the Rentenbank's capital and its
  1.2 billion credit from the *Federal Reserve Bulletin*), and the consolidated budget constraint
  `eq:intro-budget`;
- Ch 3: the Fisher relation `eq:prices-fisher`; Ch 4: the central bank's balance sheet; Ch 5: the
  balance of payments `eq:external-bop` and the real exchange rate;
- Ch 11: gross seigniorage `eq:medieval-seigniorage`; Ch 12: the collapse of Song–Ming paper money;
- Ch 19: the quantity equation and the bullion controversy; Ch 23: the gold standard and the lender
  of last resort; Ch 24: the indemnities of 1895 and 1901 and the transfer problem as first posed;
  Ch 25: Fisher (1930) on the German real rate near −100%, and the end of Gibson's paradox with gold.

Later chapters own: Ch 50 the government budget constraint and unpleasant arithmetic; Ch 52 Cagan's
money demand, Sargent's four inflations as a theory of regime change, and the cross-country
comparison of stabilizations; Ch 61 emerging-market crises; Ch 75 fiscal dominance.

## 第 26 章 `ch:weimar` 一战、赔款与魏玛恶性通胀 (`zh/ch26_weimar.tex`)

A first version exists (written outside the usual workflow, branch `codex/ch26-weimar`, merged into
the working branch 2026-10-21). The editor's review found its facts sound and its structure right,
and its check script and prose below the book's standard. **Rewrite the chapter**: keep what is
right, reuse its verified snapshots and figures, and fix the problems listed below.

- Neighbours:
  - Ch 27 owns the interwar gold-exchange standard, Britain's return in 1925 and Poincaré's
    stabilization; this chapter ends with the Reichsmark of 1924 and hands over the question of the
    parity.
  - Ch 29 owns 1931 (the German banking crisis, the end of reparations); Ch 30 owns Schacht's later
    career and Nazi finance; Ch 34 owns the Second World War's finance.
  - Ch 52 owns Cagan and Sargent's general argument; this chapter gives Cagan's definition of
    hyperinflation in one sentence and the German facts.
- Owns:
  - war finance 1914–1918 (suspension of convertibility on 31 July 1914, treasury bills discounted at
    the Reichsbank, war loans, the small share of ordinary revenue);
  - reparations: the London Schedule of 1921 (A, B, C bonds), Keynes (1919), the Keynes–Ohlin
    transfer debate (1929), with each side's concessions;
  - the fiscal mechanism: the Ruhr occupation and passive resistance (1923), seigniorage and the
    inflation tax, the tax-collection lag;
  - the collapse of money demand in 1922–1923 and its feedback with the exchange rate, and the
    balance-of-payments explanation of the time (Helfferich) against the fiscal-monetary one;
  - the stabilization of 1923–1924 in its steps: the Rentenbank decree (15 October), the first notes
    (15 November), the dollar rate fixed at 4.2 trillion paper marks (20 November), the refusal of
    further credit (December), the budget, the Dawes Plan and the Reichsmark (1924);
  - who paid: creditors and savers, wage and salary earners, the revaluation question, dismissals.
- Promises (FORWARD_REFS): from Ch 1 (Weimar 1919–1923: reparations, treasury bills discounted at the
  Reichsbank, the Rentenbank), Ch 7 (paper money has no floor like a coin's metal), Ch 24 (the
  transfer problem after the indemnities of 1895 and 1901) and Ch 25 (the closing question; money
  without an anchor; Fisher's real rate near −100%). Keep all four.
- When it began: Chapter 25 hands over "一个国家为什么会印钞印到物价每天翻倍？恶性通胀又是怎样一夜止住的？".
  Keep the PLAN's 核心问题 exactly as written (the first version changed it; the editor restored it):
  the reader's question in the reader's words. The chapter answers it precisely: at the peak the
  monthly index implies prices doubling every three to four days, single days in which the dollar
  rate doubled, and a stop that came in steps over weeks and months, with the exchange rate first.
- Opening (suggested, verify every detail): 20 November 1923, the day the Berlin dollar rate was
  fixed at 4.2 trillion paper marks, which with one rentenmark for a trillion paper marks is the
  pre-war rate of about 4.2 marks to the dollar; Rudolf Havenstein, president of the Reichsbank
  through the whole inflation, died that day (Deutsche Biographie). The free market in Cologne still
  paid far more for a dollar. A better-sourced scene is welcome; the opening must have a person, a
  date and the question within one page.
- People (one sentence each at first appearance, NARRATIVE §8.1): Havenstein; Karl Helfferich (war
  finance, then the balance-of-payments explanation, and a proposal behind the Rentenmark, if
  sourced); Walther Rathenau (his murder on 24 June 1922 and the flight from the mark that followed,
  if sourced); Hans Luther and Hjalmar Schacht (Currency Commissioner from November 1923, Reichsbank
  president from December); Keynes and Ohlin. Do not add people the sources do not support.
- Case (outside Britain and the US, and outside Germany): Austria 1922 and Hungary 1924, the League of
  Nations stabilizations with foreign loans and limits on central-bank lending to the state.
- Data and sources (keep the first version's verified snapshots `weimar_facts`,
  `weimar_prices_1920_1924`, `weimar_budget_1923_1924`, `weimar_notes_1923_1924` and extend them):
  - Bresciani-Turroni (1937, archive.org text, in copyright: short quotes), Sargent (1982, NBER
    chapter; add its © notice to the bibitem and the snapshot licence), Keynes (1919, 1923 *A Tract
    on Monetary Reform* if reachable, 1929), Ohlin (1929), the Rentenbank decree, the London Schedule;
  - try for the originals the first version could not get: Young (1925), *European Currency and
    Finance* (US Senate Commission of Gold and Silver Inquiry, public domain; FRASER or archive.org),
    and Statistisches Reichsamt (1925), *Zahlen zur Geldentwertung in Deutschland 1914 bis 1923*
    (daily dollar rates, prices and note issue). If neither can be had, keep Sargent's transcription
    and say so once in the 史料说明.
  - Stay consistent with Chapter 1's numbers (frb1923, frb1924, koech2011, reinhart2008): refer back to
    them, do not restate them with other figures.
- Teaching: the transfer identity (`eq:weimar-transfer`), the consolidated financing and the split of
  seigniorage into Δh and the inflation tax (`eq:weimar-budget`, referring back to `eq:intro-budget`
  and `eq:medieval-seigniorage`), money demand with a falling k (`eq:weimar-demand`); worked examples
  with stated teaching inputs and one from the monthly index (doubling time).
- Compare boxes (2–4): 高通胀 vs 恶性通胀 (Cagan's 50% a month, from cagan1956; Ch 52 for the rest);
  凯恩斯 vs 俄林; 货币改革 vs 财政改革 (only a new unit vs the 1923 package); optionally 征税、借债与发钞.
- Keep the labels of the first version (they are in the registry and FORWARD_REFS): sections
  `sec:weimar-world`, `-transfer`, `-fiscal`, `-demand`, `-test`, `-stabilization`, `-cost`, `-legacy`;
  equations `eq:weimar-transfer`, `-budget`, `-demand`; figures `fig:weimar_prices`,
  `fig:weimar_balances`, `fig:weimar_budget`; `tab:weimar-stages`; examples `ex:weimar-transfer`,
  `-seigniorage`, `-taxlag`, `-double`. New labels may be added (report them).

### What the first version got wrong (fix all of it)

1. **The check script does not tie the text to the snapshots.** Seven numbers of the text were
   changed (480 亿 → 580 亿, 两千倍 → 三千倍, 32 亿 → 42 亿, 3.7 天 → 2.7 天, 12 万人 → 15 万人,
   980 亿 → 680 亿, 1320 亿 → 1520 亿) and the script still passed. Many of its "ok" lines compare a
   number with itself; some values are typed in rather than read from a snapshot. Rewrite
   `checks/check_ch26.py` in the style of `checks/check_ch25.py` (sections by the chapter's sections;
   `say()` for every phrase of the text that carries a number, `chk()` against the snapshot values;
   TRANSLATIONS for every quotation; ORDINAL and Chinese numerals asserted; `anchors()` at the end).
   Before reporting, run a mutation test: change at least ten numbers in a scratch copy of the
   chapter (pointing the script at it, or restoring the file afterwards) and show that each change
   makes the script fail.
2. **Over-hedging.** "不能" occurs 54 times (Chapters 22–25: 7–13 each); a table column is titled
   "不能据此断言什么"; many paragraphs end with what cannot be concluded. State each point fully, then
   put the limits in one clause, the pitfall box or the 史料说明 (NARRATIVE §7.5). Aim for at most
   about a dozen "不能" in the chapter.
3. **Sources as subjects.** Bresciani-Turroni is the subject of the sentence ten times and Sargent
   five times outside the 史料说明. Name a line of evidence once (NARRATIVE §7.2); let the people and
   the institutions be the subjects.
4. **The title's term is never defined.** Define 恶性通胀 at its first use (Cagan's threshold of 50% a
   month, with the cite), and add the compare box 高通胀 vs 恶性通胀.
5. **Too few people and scenes.** The mechanism of 1922–1923 (goal 3) lacks its turning points and its
   actors (see People above). Scenes need sources: wages paid daily, prices repriced during the day,
   the queues at the end of the day, only where Bresciani-Turroni or another verified source records
   them.
6. **Translationese**: "100 百万马克", "20 百万"; write 1 亿, 2,000 万, or state the unit once.
7. **Code style**: `check_ch26.py` and `fig_ch26.py` were written as semicolon-joined one-liners. Write
   them like the other modules (one statement per line, docstrings, comments where a reading needs
   one). Keep the figures' content and labels; fix the colour mapping of `weimar_balances` (Reichsbank
   notes are amber in panel (a) and blue in panel (b): give the same series the same colour).
8. **The core question.** Restore the PLAN's 核心问题 (see "When it began").

What the first version got right, and should be kept: the war-finance account (31 July 1914, the
treasury-bill channel), the London Schedule's A/B/C bonds, the Keynes–Ohlin debate organized by
question with Ohlin's concession that some fall of wages and prices is almost certainly needed, the
seigniorage identity and its examples, the 3.7-day doubling from the monthly index, the steps of the
stabilization (decree limits 3.2 billion, government credit 1.2 billion, private credit 1.2 billion;
the December refusal; the ordinary budget still in deficit in December), the 15/16 November discrepancy
in the 史料说明, the British-number note (milliard, billion, trillion), the Austrian and Hungarian
case, and the hand-off to Chapter 27 (which parity, and who pays). The Reichsmark of 1924 kept the
pre-war gold content, so Germany did return to the old parity — in a unit twelve zeros away from the
old one; if verified (the Münzgesetz of 30 August 1924), this makes the hand-off sharper: Britain went
back to the old parity without striking off any zeros.

## Rules carried over from the rewrite of Chapter 26 (every Part 5 chapter)

- **The check script ties the text to the snapshots.** Model it on `checks/check_ch26.py`: `said()`
  reads every number of a phrase with its unit (万, 亿, 万亿) and compares it with the snapshot value;
  READINGS give, for every row, how its quote states the number (num, en, frac, gap, ocr …), and a
  misprint in the source is named in the row's note; TRANSLATIONS for every “…” quotation; `anchors()`
  at the end. Before reporting, run a mutation test: change at least ten numbers of the text in a
  scratch copy and show that the script fails on each.
- At most about a dozen "不能"; limits in one clause, the pitfall box or the 史料说明.
- Name a line of evidence once; people and institutions are the subjects of sentences. Authors of cited
  works appear under their original names (STYLE §11: Eichengreen, Moggridge, Nurkse); historical
  actors under the usual Chinese renderings (凯恩斯, 丘吉尔).
- Foreign variables take a superscript $f$ (Appendix B, `eq:external-real`); the star is the neutral
  rate's.
- Snapshot CSVs keep their line endings (several use CRLF); edit them as bytes or check `git diff`.
- Licence lines: Hansard "Contains Parliamentary information licensed under the Open Parliament
  Licence v3.0"; legislation.gov.uk and other Crown material "Contains public sector information
  licensed under the Open Government Licence v3.0" (both already used in `references_zh.tex`; copy the
  existing wording). Crown reports older than 50 years (Cunliffe 1918, the Chamberlain–Bradbury
  Committee 1925, the Macmillan Committee 1931) are out of Crown copyright. US federal documents
  (*Federal Reserve Bulletin*, *Banking and Monetary Statistics*, Senate hearings) are public domain.
  NBER working papers and books: short quotations with the © notice, as for `reinhart2008`.

## 第 27 章 `ch:interwar` 两次大战之间的金本位 (`zh/ch27_interwar.tex`)

- Neighbours:
  - Ch 23 owns the pre-war gold standard (the 1844 Act, Bank Rate, Goschen's condition
    `eq:gold-goschen`, the rules of the game before 1914 and Bloomfield's counts). Refer back; do not
    retell.
  - Ch 26 owns Germany to 1924 (the Rentenmark, the Dawes Plan, the Reichsmark at the old gold
    content). Use the Reichsmark only as one member of the gold-exchange standard, with `\chref`.
  - Ch 28 owns the American Depression from 1929 (output, prices, bank failures; Fisher's debt
    deflation, Friedman–Schwartz, Bernanke; the recovery). This chapter ends with the crash of
    October 1929 and hands over Ch 28's question.
  - Ch 29 owns 1931 (the Creditanstalt, the German crisis, Britain leaving gold on 21 September 1931),
    the gold bloc, Eichengreen–Sachs and the "golden fetters" argument as a theory of the Depression.
    This chapter shows the fragility of the system and stops before it breaks.
  - Ch 30 owns Japan's exit and Takahashi (Japan's return to gold in January 1930 may appear in one
    line of a table of returns); Ch 32 owns the *General Theory* and the "Treasury view"; Ch 34 owns
    Bretton Woods (one clause with `\chref` in the legacy section).
  - Ch 5 owns the real exchange rate and PPP (`eq:external-real`, `eq:external-ppp`); Ch 4 the central
    bank's balance sheet; use them, do not re-derive.
- Owns:
  - Britain from the war to 1925: convertibility in practice suspended and the exchange pegged during
    the war, the Cunliffe Committee (1918) and its programme, the slump and deflation of 1920–1921,
    the pound's climb back to \$4.86, the Chamberlain–Bradbury Committee, Churchill's decision, the
    Gold Standard Act of 1925 (a gold bullion standard: bars, not coins);
  - Keynes's critique: *A Tract on Monetary Reform* (1923, price stability against exchange stability)
    and *The Economic Consequences of Mr. Churchill* (1925): the overvaluation, the cut in money wages
    it requires, deflation working through unemployment, the coal industry; the other side's case in
    its strongest form (credibility, London's position, creditors, the Cunliffe programme);
  - the gold-exchange standard: the Genoa resolutions (1922), reserves held as sterling and dollar
    balances, the economy of gold and the fragility it brings (a run from exchange into gold shrinks
    the world's reserves); the rules of the game between the wars (the phrase is postwar: Keynes
    1925, Kindersley to the Macmillan Committee 1930) and sterilization, with Nurkse's counts against
    Bloomfield's pre-war ones (if the counts can be verified);
  - France 1926–1928 (the case box): the franc's fall in July 1926, Poincaré's government, the budget
    and the sinking fund, de facto stabilization in December 1926 and the law of 25 June 1928 at about
    one fifth of the pre-war gold value; the undervalued franc and the Banque de France's gold; Moreau
    and Norman;
  - the maldistribution of gold: the shares of the United States and France in the world's monetary
    gold, and their sterilization;
  - the United States in the 1920s: the Fed's easing of 1927 (the Long Island meeting of Strong,
    Norman, Schacht and Rist, if sourced), credit expansion (instalment credit, real estate, brokers'
    loans and call money), the Fed's tightening of 1928–1929, and the crash of October 1929.
- Promises (FORWARD_REFS rows from Ch 19, Ch 23 and Ch 26; read them in full): Britain and Sweden (1924)
  returned at the pre-war parity, who bears the cost of the parity chosen, Hume's conditions mostly no
  longer held; why the interwar standard lacked the pre-war room for manoeuvre, the phrase "rules of
  the game" is postwar (Keynes 1925; Kindersley 1930) while Bloomfield's prewar counts show the Bank of
  England broke the rule in about half the years; the gold-exchange standard (Ch 26 calls the Reichsmark
  of 1924 "实际上是美元汇兑本位"); Britain's return in 1925 and who bears the adjustment. Keep them all and
  mark the rows done.
- When it begins: Chapter 26 ends "英国走了另一条路，1925 年把英镑提回到战前的黄金价值，一个零也没有去掉"
  and hands over the PLAN's 核心问题 "英国 1925 年按战前平价回到黄金，代价是什么？1920 年代的繁荣建立在什么之上？".
  Keep it exactly. The chapter answers both halves: the cost (the overvaluation, deflation and
  unemployment, the burden on export industries and on wage earners) and the base of the prosperity
  (credit, American lending abroad, a system that economized gold and so depended on confidence).
- Opening (suggested, verify every detail): 28 April 1925, Winston Churchill, Chancellor of the
  Exchequer, opens his Budget in the House of Commons and announces the return to gold at the pre-war
  parity (Hansard, `api.parliament.uk/historic-hansard/sittings/1925/apr/28`, reachable from the
  shell). The Gold Standard Act followed (legislation.gov.uk has the enacted text,
  `ukpga/Geo5/15-16/29`). A better-sourced scene is welcome; a person, a date and the question within
  the first page.
- People (one sentence each at first appearance; only where sourced): Churchill; Montagu Norman
  (Governor of the Bank of England 1920–1944); Keynes; Lord Cunliffe; Benjamin Strong (Federal Reserve
  Bank of New York); Raymond Poincaré; Émile Moreau (Banque de France); Irving Fisher in October 1929
  (Ch 25's Fisher; his "permanently high plateau" only from a verified contemporary report); Reginald
  McKenna and the Treasury's Otto Niemeyer and John Bradbury only if a primary or verified source
  records their part.
- Case (outside Britain and the US): France 1926–1928. Sweden (an early return at the old parity in
  1924; verify the date, e.g. on the Riksbank's krona page used in Ch 25) and Italy's "quota novanta" (1927) may appear
  in a table of returns.
- Data and sources (probe first; on 2026-10-22 archive.org, NBER, the Bank of England, Hansard,
  legislation.gov.uk, the Riksbank and FRASER's `/files/` PDFs answered; Gallica, Légifrance and the
  Banque de France answered 403):
  - Keynes 1923 and 1925 (`keynes1923`, `keynes1925` already in `references_zh.tex`, with copies in the
    web cache; Keynes is public domain in the UK, quote briefly);
  - Hansard 28 April 1925; the Gold Standard Act 1925; the Cunliffe Committee's First Interim Report
    (1918, Cd. 9182), the Chamberlain–Bradbury Committee's report (1925, Cmd. 2393) and the Macmillan
    Committee's evidence (archive.org has minutes of evidence; Kindersley's "rules of the game" if found
    there; otherwise keep `dutton1984`'s Moggridge as the witness, as Ch 23 does);
  - the Bank of England's *Millennium of Macroeconomic Data* (`boe2017`; workbook in
    `~/.cache/finance-study/boe/`): M15 monthly \$–£ 1791–2015, M5 unemployment, M6 monthly prices and
    wages, D1 Bank Rate, Q5 quarterly effective exchange rates 1920–38;
  - the Federal Reserve's *Banking and Monetary Statistics 1914–1941* (1943, FRASER) and the *Federal
    Reserve Bulletin*: gold reserves of central banks by country, discount rates, brokers' loans, call
    money, stock prices;
  - W. A. Brown Jr. (1940), *The International Gold Standard Reinterpreted, 1914–1934* (NBER, free on
    nber.org; check its copyright page): the dates and parities of the returns, the gold-exchange
    standard;
  - France: E. L. Dulles (1929), *The French Franc, 1914–1928* (archive.org), R. M. Haig (1929), *The
    Public Finances of Post-War France*; the 1928 monetary law's text from a reachable copy;
  - the 1929 boom: De Long and Shleifer (1991, NBER WP 3523, closed-end fund premia), White (1990,
    *JEP*), McGrattan and Prescott (2004, Minneapolis Fed); Eichengreen (1992) and Moggridge (1969)
    only in short phrases or through verified reviews, if no copy can be read.
  - Avoid FRED (its terms forbid extraction); take US series from FRASER's PDFs or another source whose
    terms allow it.
- Teaching:
  - the overvaluation from the real exchange rate (`eq:external-real`): at a fixed $e$, the domestic
    price level that restores the pre-war $q$, and the cut it requires; a worked example from the
    indices Keynes used (if his essay gives them) or from the Bank of England and US series, with the
    choice of index stated, since it changes the answer;
  - the gold-exchange standard as a pyramid: reserves $R=G+F$, money bounded by the cover ratio; a
    conversion of $F$ into gold leaves the gold where it was and destroys the exchange reserves; one
    example with teaching inputs;
  - sterilization on the central bank's balance sheet (Ch 4): base money = domestic assets + reserves;
    the rule of the game against offsetting, and how Nurkse (or Bloomfield in Ch 23) counted it;
  - optionally margin buying: with a margin of $m$, a fall of $m$ in the price wipes out the buyer's
    equity (teaching inputs; the margins of 1929 only if sourced).
- Compare boxes (2–4): 金本位 vs 金汇兑本位; 按战前平价回归 vs 贬值后回归 (Britain 1925 vs France 1928);
  optionally 战前的英格兰银行 vs 战后的英格兰银行 (the room for manoeuvre), or 凯恩斯 vs 财政部 on the
  return, by question with each side's concessions.
- Contested questions (§8, each side's strongest case and its evidence): was \$4.86 a mistake, and by
  how much was sterling overvalued (the estimate depends on the index); what drove the boom of
  1927–1929 (the easing of 1927, credit, fundamentals, or a bubble). Do not decide for the reader.
- Figures (2–4, at least two from snapshot data): the \$–£ rate 1919–1931 against the parity of 4.86,
  with a price ratio; the shares of the world's monetary gold; American credit and stock prices
  1925–1930; or the UK's unemployment and wages through the return.
- Ending: after `\end{answers}`, return to the opening (Churchill, the parity of 1925, or a person of
  the opening) and hand over Ch 28's question "一次股市崩盘为什么会变成持续数年、产出与物价同时坍塌的萧条？".
- Labels: sections `sec:interwar-…` (report them); `eq:interwar-…`, `fig:interwar_…`, `tab:interwar-…`,
  `ex:interwar-…`. Ch 28's stub cites `\nameref{ch:interwar}` only.

### Carried over from the editor's round on Chapter 27

- When two sources disagree on a number (Chapter 27's margins: Federal Reserve History's "typically 10
  percent" against Rappoport and White's 20–25% rising to 40–50%), give both in the text and say in the
  史料说明 which one an example uses and why; a teaching input says it is one.
- Life dates: look in the BnF authority records (data.bnf.fr; the SPARQL endpoint answers from the
  shell, Licence Ouverte, key `bnf27` shows the form) or the Library of Congress name authorities before
  writing 生卒年未详; record the record's URL in the snapshot.
- A participant's statement quoted by a later author is indirect testimony; say so once in the 史料说明
  and name the document that was not obtained.
- Quote a law or speech from its official or archival text (Statutes at Large, the American Presidency
  Project, the Federal Register), not a later summary.

## 第 28 章 `ch:depressionus` 大萧条：美国 (`zh/ch28_depressionus.tex`)

- Neighbours:
  - Ch 27 owns the 1920s boom, the Fed's easing of 1927 and tightening of 1928–29, brokers' loans and
    margins, Strong's death in October 1928 (Strong 1872—1928) and the crash of 28–29 October 1929
    (Federal Reserve History's figures, `frh2013`). Begin after the crash; refer back with
    `\chref{ch:interwar}` or `\secref{sec:interwar-boom}`, do not retell.
  - Ch 23 owns the National Banking System, the panic of 1907 with its restriction of payments
    (`sprague1910`), the lender of last resort (Bagehot) and the Federal Reserve Act of 1913
    (`fra1913`). Ch 4 owns the central bank's balance sheet and the money multiplier
    `eq:money-mult` with Cagan's ratios $C/M$ and $R/D$ (`cagan1965`); Ch 3 the Fisher relation
    `eq:prices-fisher`; Ch 25 Fisher's real rate, money illusion and his table 14. Use them with
    `\eqref`/`\chref`; do not re-derive.
  - Ch 29 owns the international side: the Creditanstalt and the German crisis of 1931, Britain leaving
    gold on 21 September 1931, the gold bloc, Eichengreen's golden fetters as a theory of the
    Depression, the Silver Purchase Act of 1934 and China. This chapter may say in one clause, with
    `\chref{ch:depressionworld}`, that Britain left gold in September 1931, because the Fed's rise of
    its discount rate in October 1931 is an American decision this chapter owns.
  - Ch 30 uses the New Deal only as a comparison; this chapter owns the American recovery of
    1933–1936. Ch 32 owns the *General Theory*, the multiplier and the Treasury view; Ch 33 owns the
    recession of 1937–38 (one clause with `\chref{ch:islm}` at most); Ch 45 owns monetarism as a
    programme (Friedman–Schwartz here only as a history of the Depression); Ch 64–65 own 2008 and the
    financial accelerator (Bernanke–Gertler–Gilchrist), Ch 66 the zero lower bound; one clause each in
    the legacy section.
- Owns:
  - the data of 1929–1933 and after: output (BEA's real GDP from 1929, industrial production), prices
    (consumer and wholesale), unemployment, bank suspensions and their deposits, the money stock and
    its two ratios, nominal and real interest rates; the trough of March 1933;
  - the course of the contraction: the Fed after the crash, the banking panics of late 1930 (the Bank
    of United States, 11 December 1930), spring and autumn 1931, the Fed's rise of its discount rate in
    October 1931, the open-market purchases of 1932 and their end, the panic of February–March 1933 and
    the national bank holiday;
  - three explanations, each from its own text: Fisher's debt deflation (1933: over-indebtedness and
    deflation feeding each other; the more the debtors pay, the more they owe, if the article says so),
    Friedman and Schwartz's great contraction (1963: the money stock fell by about a third because the
    currency ratio and the reserve ratio rose while the Fed let it happen; the leadership vacuum after
    Strong), Bernanke's credit channel (1983: bank failures destroyed the information capital of
    intermediation and raised the cost of credit, beyond their effect on money); and, as a fourth view
    the reader should meet, the spending side (Romer 1990 on the uncertainty after the crash; Temin 1976
    only through a verified summary);
  - why the Fed did not act, as a contested question: Friedman and Schwartz's account against
    Wheelock's (1992, St. Louis Fed *Review*: the Fed's own doctrine, low nominal rates and member-bank
    borrowing read as easy money; real bills, Ch 18) and Meltzer's (short phrases or through verified
    reviews only);
  - the recovery: the bank holiday and the Emergency Banking Act (March 1933), the gold embargo and
    Executive Order 6102 (5 April 1933), the dollar's devaluation and the Gold Reserve Act (30 January
    1934, \$35 an ounce against \$20.67), deposit insurance under the Banking Act of 1933, the gold
    inflows of 1934–36 and Romer's (1992) case that money, not fiscal policy, drove the recovery; NIRA
    and the debate on it only if verified sources for both sides can be read.
- Promises (FORWARD_REFS rows from Ch 4, Ch 17 and Ch 23; read them in full):
  - Ch 4: how $C/M$ and $R/D$ of `eq:money-mult` moved in the 1930s (Cagan's decomposition; Friedman and
    Schwartz). Compute them from a public-domain table (*Banking and Monetary Statistics 1914–1941*), say
    which definition of money and of reserves you use, and show $H$ rising while $M$ fell;
  - Ch 17: Fisher's debt deflation as the redistribution of nominal debts in inflation and deflation
    (the Genbun recoinage and dear silver are Ch 17's; one clause back to them);
  - Ch 23 (限额从墙变成了门): the 1913 Act made the reserve limit elastic; what then disciplined the Fed in
    the Depression (the gold cover and the free-gold question of 1931–32, if sourced; the Glass–Steagall
    Act of February 1932 that let government securities back Federal Reserve notes). Keep them and mark
    the rows done.
- When it begins: Chapter 27 ends on 28–29 October 1929 and hands over the PLAN's 核心问题
  "一次股市崩盘为什么会变成持续数年、产出与物价同时坍塌的萧条？". Keep it exactly.
- Opening (suggested, verify every detail): Sunday 12 March 1933, Franklin D. Roosevelt's first fireside
  chat, explaining on the radio why the banks were shut and how a bank works (the text of the American
  Presidency Project, `www.presidency.ucsb.edu/documents/fireside-chat-banking`, reachable; a US
  government work, public domain), after his proclamation of the national bank holiday of 6 March. Or
  11 December 1930, the closing of the Bank of United States in New York. A person, a date and the
  question within the first page; go back to the crash of 1929 in the next paragraph.
- People (one sentence each at first appearance, only where sourced): Herbert Hoover; Franklin D.
  Roosevelt; Andrew Mellon (his "liquidate" advice only as Hoover's later recollection, flagged as such);
  George L. Harrison of the New York Fed (Ch 27 wrote 生卒年未详: look again in the LC or BnF authorities
  and, if found, fix Ch 27 in your report rather than in its file); Eugene Meyer; Adolph Miller; Irving
  Fisher (Ch 25's Fisher; his losses in 1929 only if sourced); Milton Friedman and Anna Schwartz; Ben
  Bernanke; Christina Romer; Marriner Eccles only if he enters through a source.
- Case (outside the US and Britain): Canada 1929–1933, a depression of similar depth with almost no bank
  failures (verify both halves and the number of chartered banks). It tests the bank-failure
  explanations: Bordo, Redish and Rockoff (NBER WP 17312, reachable), Friedman and Schwartz's own
  comparison if a verified text has it, Historical Statistics of Canada (Statistics Canada 11-516-X,
  Statistics Canada Open Licence; cite as it asks). Say what the case does and does not show.
- Data and sources (probe first; on 2026-10-22 the shell reached FRASER's `/files/` PDFs, the Census
  Bureau, BEA, federalreserve.gov, the American Presidency Project, Statistics Canada, NBER, FDIC,
  govinfo and loc.gov; BLS answered 403; FRED's terms forbid extraction, do not use it):
  - *Banking and Monetary Statistics 1914–1941* (Board of Governors 1943, public domain;
    `fraser.stlouisfed.org/files/docs/publications/bms/1914-1941/BMS14-41_complete.pdf`): currency,
    deposits, member-bank reserves, the gold stock, discount rates, bank suspensions; the *Federal
    Reserve Bulletin* (e.g. September 1937, bank suspensions 1921–36);
  - *Historical Statistics of the United States, Colonial Times to 1970* (Census Bureau 1975, public
    domain; `www2.census.gov/library/publications/1975/compendia/hist_stats_colonial-1970/`):
    unemployment (Lebergott), prices, debt;
  - BEA's NIPA tables from 1929 (public domain; the flat files under `apps.bea.gov/national/Release/TXT/`
    with their series register) and the Board's industrial production (G.17, from 1919);
  - Fisher (1933), "The Debt-Deflation Theory of Great Depressions", *Econometrica* 1(4) (FRASER copy
    `fraser.stlouisfed.org/files/docs/meltzer/fisdeb33.pdf`; in copyright in the US: short phrases);
  - Bernanke (1983) as NBER WP 1054 (published *AER* 73(3); say which version you quote); Romer (1990)
    as NBER WP 2639; Romer (1992) as NBER WP 3829; Bernanke's speech of 8 November 2002 on Friedman's
    ninetieth birthday (federalreserve.gov, public domain), which summarizes Friedman and Schwartz's
    case; Wheelock (1992); Federal Reserve History's essays on the Great Depression, the bank holiday,
    the Banking Act of 1933 and the Gold Reserve Act (short phrases, as `frh2013`);
  - Friedman and Schwartz (1963) are in copyright (Princeton/NBER): short phrases only, from a copy you
    can read; otherwise state their argument through Bernanke 2002 and Wheelock and say so;
  - laws and orders from the Statutes at Large (govinfo, loc.gov), the Federal Register or the American
    Presidency Project.
- Teaching:
  - debt deflation on a borrower's account: a nominal debt $D$, prices falling by a stated share, the
    real burden $D/P$ and the real rate from `eq:prices-fisher` with a nominal rate of a few per cent;
    teaching inputs, then the actual price fall of 1929–33;
  - the money stock decomposed with `eq:money-mult`: $H$, $C/M$, $R/D$ in 1929 and 1933 from the table
    you use; how much of the fall in $M$ each ratio accounts for (a stated, simple decomposition);
  - a bank run on a balance sheet (Ch 4 notation): deposits withdrawn, reserves gone, assets sold at a
    discount, a solvent bank made insolvent; why one failure raises $C/M$ and $R/D$ elsewhere;
  - Bernanke's regression in the deeper box: what he regressed on what, and what the coefficients on the
    deposits of failing banks and the liabilities of failing businesses add to the money surprises (his
    table, read as he reports it);
  - the devaluation of 1933–34: \$20.67 to \$35 an ounce, the Treasury's gold profit, gold inflows
    adding to $H$ (Romer 1992's figures, if verified).
- Compare boxes (2–4): 债务—通缩 vs 货币紧缩 (Fisher vs Friedman–Schwartz); 货币渠道 vs 信贷渠道
  (Friedman–Schwartz vs Bernanke); optionally 1907 年的限制付现 vs 1930—1933 年的银行倒闭 (Ch 23's
  restriction of payments against the Fed era, from Friedman and Schwartz's argument if verified), or
  美国 vs 加拿大 inside the case box.
- Contested questions (§8, each side's strongest case, concessions and the strength of the evidence):
  what turned the recession of 1929–30 into the Great Depression (money, credit, debt, spending); why
  the Fed did not stop the fall; what ended it (gold and money against fiscal policy and the New Deal).
  Do not decide for the reader.
- Figures (2–4, at least two from snapshot data): output, prices and unemployment 1929–1941; the money
  stock, $H$ and the two ratios 1929–1936; bank suspensions and their deposits by year or month,
  1921–1936; Canada against the US.
- Legacy (今天还剩什么): Bernanke's 2002 sentence to Friedman and Schwartz (a dated document, quote it
  exactly), deposit insurance, the lender of last resort to the banking system as a whole, the zero
  lower bound and 2008 (one clause each with `\chref{ch:gfc}`, `\chref{ch:frictions}`,
  `\chref{ch:zlb}`).
- Ending: after `\end{answers}`, return to the opening scene and hand over Ch 29's question
  "金本位怎样把萧条传到全世界？" (its guide box asks it with China; hand over the first half).
- Labels: sections `sec:depressionus-…` (report them); `eq:depressionus-…`, `fig:depressionus_…`,
  `tab:depressionus-…`, `ex:depressionus-…`. Ch 29, 30 and 32 cite `\nameref{ch:depressionus}` only.

### Carried over from the editor's round on Chapter 28

- When an institution's own history and a later essay disagree on a date or a limit (Chapter 28:
  Federal Reserve History's "became permanent in July 1934" against the FDIC's own history of 1998),
  follow the institution's document, say so in the 史料说明, and check every statutory date against the
  statute or the agency's own account.
- An interpretation belongs to its author: write "另一种解释从支出入手\cite{…}" or name the author once
  in a clause, never state a contested reading as the chapter's own; concessions and caveats in the
  source's own terms, not stronger or weaker.
- No pointer phrases ("见 X（年份）", "详见"): say what the source shows, then cite it.
- Name the actors in the main text (Chapter 28 left Hoover to the 史料说明); explain old units (格令)
  where they first appear.
- Quotations below 8% are acceptable only when most sources are in copyright; public-domain texts
  (Hansard, statutes, government decrees, Keynes in the UK) can carry a few more exact sentences.

## 第 29 章 `ch:depressionworld` 大萧条：世界与“金色枷锁” (`zh/ch29_depressionworld.tex`)

- Neighbours:
  - Ch 27 owns the gold-exchange standard (`eq:interwar-pyramid`), the rules of the game, Nurkse's
    counts, France's undervalued franc and the maldistribution of gold to 1929. Refer back; the
    asymmetry is the starting point here (FORWARD_REFS row from Ch 27: keep it).
  - Ch 28 owns the American Depression: output, prices, bank failures, Fisher, Friedman–Schwartz,
    Bernanke, the Fed's rise of October 1931, the bank holiday, the dollar's devaluation of 1933–34
    (\$20.67 to \$35) and the American recovery, and its case box on Canada (no bank failures, a
    depression as deep; Friedman–Schwartz's reading and Bernanke's reply with his 26-country sample, both
    through Bernanke 2002). Use them with `\chref{ch:depressionus}`; America here only as the country
    whose deflation and gold policy the others faced; do not retell Canada, use Bernanke–James's own
    tables for the cross-country evidence.
  - Ch 30 owns Germany from 1933 (MEFO bills, exchange control as Schacht's system), Japan's exit in
    December 1931 and Takahashi, and Sweden's price-level programme of 1931–37 (the FORWARD_REFS row
    from Ch 25 now points there). Here Sweden and Japan appear only as dates in the table of exits and
    points in the figure.
  - Ch 24 owns the periphery before 1914 (the silver standard in China and India, the fall of silver
    after 1873); Ch 13 and Ch 17 the silver of earlier centuries; Ch 34 owns Bretton Woods (one clause
    in the legacy section). Ch 5 owns PPP and the real exchange rate (`eq:external-ppp`,
    `eq:external-real`).
- Owns:
  - the transmission under fixed parities: a deflating centre, fixed $e$, prices of traded goods tied
    by `eq:external-ppp`, gold and exchange reserves draining, central banks raising rates to defend
    the parity in a slump; the run from exchange reserves into gold (`eq:interwar-pyramid`);
  - 1931: the Creditanstalt (May 1931), the Hoover moratorium (20 June 1931), the German banking crisis
    and exchange control (July 1931), Britain's suspension of gold payments on 21 September 1931 (the
    Gold Standard (Amendment) Act 1931, Hansard of that day; the Macmillan Report of July 1931 and the
    May Report only through what can be read);
  - the exits and their timing: the sterling area, the countries that followed Britain, the gold bloc
    (France, Belgium, the Netherlands, Switzerland, Italy, Poland) to 1935–36, the Tripartite Agreement
    of 1936; Eichengreen and Sachs (1985): the earlier a country left gold, the sooner it recovered;
  - golden fetters as a theory of the Depression (Eichengreen 1992 in short phrases or through verified
    reviews; Bernanke and James 1991; Bernanke 1995), and the case against it or for its limits;
  - China and silver (the case box): a silver-standard country in a gold world; the fall of silver
    1929–31 that cushioned China, the rise after Britain and Japan left gold and after the US Silver
    Purchase Act (19 June 1934), the outflow of silver, deflation and the banking trouble of 1934–35,
    the 法币 reform of 3–4 November 1935 (the decree's text from a reachable copy; it is a Chinese
    government document of 1935); Friedman (1992) against Brandt and Sargent (1989) as the contested
    question (did American silver policy cause China's depression?), each through what can be read;
  - Latin America and the primary-product exporters: the fall of export prices and the terms of trade,
    default, exchange control and early exits (Argentina from December 1929 and its central bank of
    1935; Brazil's coffee purchases), with Maddison's output data; only what is verified.
- Promises (FORWARD_REFS rows pointing to 29; read them in full and mark them done): Ch 27's asymmetry
  of 1931 and the run from exchange into gold. Ch 28's rows to 29 (added by its writer).
- When it begins: Chapter 28 ends by handing over "金本位怎样把萧条传到全世界？"; keep it and take up the
  second half of the guide question (China) in the case box.
- Opening (suggested, verify every detail): Monday 21 September 1931, the House of Commons passes the
  Gold Standard (Amendment) Bill in one day (Hansard, reachable; the Act on legislation.gov.uk,
  `ukpga/Geo5/21-22/46`); or Keynes's "The End of the Gold Standard" (*Sunday Express*, 27 September
  1931, reprinted in *Essays in Persuasion*: archive.org `in.ernet.dli.2015.89977`, the 1933 printing),
  the source of the phrase "gold fetters" (quote it exactly, if the text has it). Six years after
  Chapter 27's opening, the same Commons.
- People (only where sourced): Philip Snowden (Chancellor, 1931); Ramsay MacDonald; Montagu Norman
  (ill and at sea in September 1931, if sourced); Keynes; Heinrich Brüning and Hans Luther (Germany,
  1931); Herbert Hoover (the moratorium); in China 孔祥熙 (H. H. Kung) and 宋子文 (T. V. Soong), Frederick
  Leith-Ross; Henry Morgenthau and Key Pittman (the silver policy); Raúl Prebisch (Argentina).
- Data and sources (probe first; on 2026-10-22 the shell reached Hansard, legislation.gov.uk, NBER,
  FRASER `/files/`, archive.org, the Bank of England, the GGDC, the Riksbank, the Bank of Japan,
  BCRA; Northwestern's League of Nations collection redirects to dc.library.northwestern.edu, check
  its terms; zh.wikisource answered 429; FRED is not to be used):
  - Eichengreen and Sachs, NBER WP 1498 (1984; published *JEH* 45(4), 1985; say which version);
    Bernanke and James, NBER chapter c11482 (1991; WP 3488's text layer is unreadable OCR, use the
    chapter); Bernanke, NBER WP 4814 (1994; *JMCB* 1995); © notices as printed;
  - Hansard 21 September 1931; the Gold Standard (Amendment) Act 1931 (OGL notice);
  - *Banking and Monetary Statistics 1914–1941* (FRASER, public domain): foreign exchange rates,
    central banks' gold reserves by country, the price of silver in New York; the *Federal Reserve
    Bulletin* (FRASER): the chronology of 1931, China's monetary reform of 1935 if the Bulletin
    reported it;
  - the Bank of England's millennium workbook (`boe2017`; `~/.cache/finance-study/boe/`): Bank Rate and
    \$–£ in 1931;
  - Maddison 2023 (`data/fetch/maddison2023.py`; CC BY 4.0 with its citation policy): GDP per head
    1925–1938 for the countries of the table of exits;
  - the Silver Purchase Act of 1934 (48 Stat. 1178) from the Statutes at Large; the 法币 decree of
    1935 from a reachable copy (Chinese government documents of 1935); Friedman (1992, *JPE*) and
    Brandt and Sargent (1989, *JME*) only through what can be read (working-paper versions, verified
    summaries); state indirect testimony once.
- Teaching:
  - the fetters in one equation: with $e$ fixed, $P\approx eP^{f}$ for traded goods (`eq:external-ppp`)
    and the money stock bounded by reserves and the cover ratio; deflation abroad pulls $P$ down
    unless $e$ moves; leaving gold lets $e$ rise and $P$ stop falling; a worked example with teaching
    inputs, then the British numbers of 1931–32;
  - Eichengreen and Sachs's cross-section: changes in the exchange rate against changes in industrial
    production 1929–1935 for their countries, from their table; a least-squares line with
    statsmodels or numpy, its slope read for the reader, and what a cross-section cannot show;
  - silver in China: the yuan's gold value moves with the price of silver; a fall of silver
    depreciates the currency and cushions deflation, a rise appreciates it and drains silver; the
    numbers of 1929–1935 from the Bulletin or BMS.
- Compare boxes (2–4): 早脱离 vs 留在金本位 (Britain 1931 vs France and the gold bloc to 1936); 银本位的中国
  vs 金本位国家; optionally 1925 年回到黄金 vs 1931 年离开黄金 (the same Commons, Ch 27's opening), or
  货币贬值 vs 外汇管制 (Britain vs Germany in 1931).
- Contested questions (§8): did the gold standard cause or only transmit the Depression (Eichengreen,
  Bernanke–James, Bernanke 1995 against the reverse-causation and policy-choice readings: countries
  that suffered less could afford to stay, or stayed for reasons of their own; Wolf 2008 if a copy can
  be read); did American silver policy cause China's depression (Friedman 1992 vs Brandt and Sargent
  1989). Do not decide for the reader.
- Figures (2–4, at least two from snapshot data): the year each country left gold against its output
  recovery (Maddison, 1929 = 100); the exchange-rate change against the industrial-production change
  (Eichengreen–Sachs's table); the price of silver and China's exchange rate 1929–1936; \$–£ and Bank
  Rate in 1931.
- Legacy: the trilemma (`ch:external`, `\chref{ch:mundell}` for the theory), Bretton Woods's
  adjustable peg (`\chref{ch:brettonwoods}`), the euro's fixed parities (`\chref{ch:euro}`).
- Ending: after `\end{answers}`, return to the opening and hand over Ch 30's question
  "纳粹德国、高桥财政下的日本和瑞典都较早走出了萧条，各自靠的是什么？代价记在了哪里？" (or its first half).
- Labels: sections `sec:depressionworld-…`; `eq:depressionworld-…`, `fig:depressionworld_…`,
  `tab:depressionworld-…`, `ex:depressionworld-…`.

### Carried over from the editor's round on Chapter 29

- Worked examples must use the same definition throughout: when an example sets "the sterling price of
  imports rises with the depreciation", every later part measures depreciation the same way (the price
  of foreign currency, not the home currency's foreign value). Check each example's arithmetic against
  its own stated assumptions and its own data before claiming a result ("通缩停了下来").
- An arithmetic correspondence is not an author's method: do not write "凯恩斯用的也是这种算法" unless the
  source says so.
- A classification built from a source's table (the earliest of three dates) is the book's own
  construction: say so in the text, the caption and the 史料说明.
- Compare-box cells carry their own citation when the numbers come from a table.

## 第 30 章 `ch:alternatives` 1930 年代的另类出路：纳粹德国、高桥财政与瑞典 (`zh/ch30_alternatives.tex`)

- Neighbours:
  - Ch 26 owns Germany to 1924 and Schacht's first term (Rentenmark, Reichsbank president from
    December 1923; Schacht 1877—1970 is introduced there). Ch 27 has Schacht at the 1927 meeting. Ch 29
    owns 1931: the German banking crisis and exchange control of July 1931, the exits from gold and the
    gold bloc, Japan and Sweden as dates in its table of exits. Begin here in 1932–33.
  - Ch 28 owns the American banking holiday, deposit insurance, the devaluation of 1933–34, gold
    inflows as base money and Romer's (1992) reading of the recovery; its recovery section says
    "新政的其他措施与别国的出路，在\chref{ch:alternatives}里比较" (FORWARD_REFS row from Ch 28 to 30:
    keep it). So this chapter owns the New Deal's other measures as a comparison: the National
    Industrial Recovery Act (16 June 1933: codes of fair competition, the Public Works Administration),
    the Agricultural Adjustment Act (12 May 1933), the relief and works programmes (the CWA, the WPA
    of 1935), and the size of the federal deficit (Brown's "not tried", already quoted in Ch 28 through
    Romer: do not repeat it); from the Statutes at Large and the American Presidency Project (public
    domain), Historical Statistics 1975 for the deficit. One compare box or one section, not a retelling
    of Ch 28; the 1937–38 recession stays in Ch 33. Ch 31 owns the Soviet five-year plans (one
    clause for the comparison of "practice before theory"). Ch 32 owns the *General Theory* and the
    Stockholm school as a parallel discovery (its case box): here Sweden's monetary programme and its
    practice, not the theory of the Stockholm school. Ch 34 owns war finance (Germany's war economy
    from 1939, Britain's and America's); this chapter stops in 1938–39.
  - Ch 25 owns Wicksell's price-level rule and Berg and Jonung's statement that Sweden was the first
    country to make the price level the official goal (`berg1998`); keep the FORWARD_REFS row (re-pointed
    to 30) and tell how the programme of 1931–1937 worked. Ch 1 has one line on Takahashi
    (1854—1936) with `\chref{ch:alternatives}`; keep the dates consistent.
- Owns:
  - Nazi Germany 1933–1938: the work-creation programmes (the Reinhardt programme of June 1933), MEFO
    bills (Metallurgische Forschungsgesellschaft) as off-budget finance for rearmament discounted at
    the Reichsbank, Schacht's New Plan of 1934 and exchange control, bilateral clearing, the price
    freeze of 26 November 1936 (Preisstopverordnung) and repressed inflation, the Four-Year Plan of
    1936, Schacht's dismissal from the Reichsbank in January 1939; how much of the recovery came from
    rearmament (Ritschl against the older view of a civilian work-creation boom, if the texts can be
    read). The character of the regime and the human cost stated plainly: the destruction of trade
    unions in May 1933, the persecution and expropriation of Jews ("Aryanization"), forced labour, and
    that rearmament served a war of aggression and plunder (write_template rule 5);
  - Japan 1931–1936: Takahashi Korekiyo's return as finance minister in December 1931, the embargo on
    gold exports of 13 December 1931, the yen's depreciation, the Bank of Japan's underwriting of
    government bonds from November 1932, the deficits, the recovery, Takahashi's attempt to cut
    military spending in 1935–36 and his assassination in the incident of 26 February 1936; what came
    after (the Bank of Japan's underwriting as a route to wartime inflation, in one clause with
    `\chref{ch:warfinance}`);
  - Sweden 1931–1937: the suspension of gold convertibility on 27 September 1931, the Riksbank's and
    the government's declaration of the price-level goal, the index the Riksbank built for it, the
    advice of the economists (Cassel, the Stockholm school's members only as advisers), how the krona
    was managed and later pegged to sterling (1933), and how well the price level held;
  - the comparison: expansion under controls vs expansion in a market economy; open vs repressed
    inflation; "practice before theory" (the three acted before the *General Theory* of 1936).
- Promises (FORWARD_REFS rows pointing to 30; read them in full and mark them done): from Ch 25
  (Sweden's price-level programme of 1931–37 as Wicksell's rule), from Ch 28 (the New Deal's other
  measures and the other countries' ways out, compared), from Ch 29 (Germany kept its parity behind
  exchange control and standstill agreements in July 1931; Japan suspended convertibility in December
  1931 and introduced exchange control in July 1932; Sweden left gold in September 1931; Ch 29's
  ending question). Ch 29's table of exits (`tab:depressionworld-exits`, Bernanke–James Table 2.1)
  gives the dates: use them and refer back, do not re-tabulate.
- Opening (suggested, verify every detail): 13 December 1931 in Tokyo, the day Takahashi became finance
  minister and Japan banned gold exports; or 27 September 1931 in Stockholm (the Riksbank's decision,
  the Riksbank's own history pages); or 1 June 1933 in Berlin (the Reinhardt programme's law in the
  Reichsgesetzblatt). Ch 29 ends by handing over "纳粹德国、高桥财政下的日本和瑞典都较早走出了萧条，各自靠的
  是什么？代价记在了哪里？"; keep it.
- People (only where sourced): Takahashi Korekiyo (1854—1936); Inoue Junnosuke (his predecessor, the
  return to gold of January 1930, assassinated February 1932, if sourced); Hjalmar Schacht (Reichsbank
  president again from March 1933, economics minister 1934–37); Hermann Göring (the Four-Year Plan);
  Fritz Reinhardt; in Sweden Ernst Wigforss (finance minister from 1932), Gustav Cassel, the Riksbank's
  governor; Berg and Jonung as authors of the account.
- Case box: all three are outside the US and Britain; the case box takes one of them as a dated case
  (e.g. 日本 · 1932—1936 · 日本银行承购国债), the other two as sections.
- Data and sources (probe first; on 2026-10-22 the shell reached the Riksbank's history pages, the Bank
  of Japan's site (history, the Bank of Japan Review), NDL Digital and NDL authorities (id.ndl.go.jp),
  JACAR, J-STAGE, e-Stat, the Deutsche Digitale Bibliothek, DigiZeitschriften (check its terms),
  the Bundesarchiv's site, econstor, NBER, FRASER (Banking and Monetary Statistics 1914–1941 answered)
  and Maddison; de.wikisource answered 429 at times (wait and retry once); ALEX (ÖNB, the
  Reichsgesetzblatt scans), documentArchiv.de and GHDI did not answer; the IMES English papers page
  answered 404/403):
  - Germany: Reichsgesetzblatt texts on de.wikisource (public domain as official works); the
    *Statistisches Jahrbuch für das Deutsche Reich* (if an open scan can be read); the Reichsbank's
    annual reports; Tooze (2006) in copyright: short phrases or verified reviews only; Ritschl (2002,
    *Journal of the Japanese and International Economies*, working-paper version if open); Overy and
    Buchheim only through what can be read; Maddison 2023 for output;
  - Japan: the Bank of Japan's publications (credit "Bank of Japan"): Shizume's papers in the *Bank of
    Japan Review* or IMES discussion papers if reachable; Takahashi's dates from a verified source (NDL
    authority records); the *Hundred-Year Statistics of the Japanese Economy* if open; Cha (2003, *JEH*)
    and Shibamoto–Shizume (2014) only through open versions;
  - Sweden: Berg and Jonung (`berg1998`, with the version already cited); the Riksbank's open data (its
    licence sentence verbatim); Jonung's other papers if open;
  - FRASER: the *Federal Reserve Bulletin*'s reports on Germany's exchange control and Japan's
    measures, as public-domain contemporary records.
- Teaching:
  - financing a deficit off the budget: MEFO bills on the Reichsbank's balance sheet (Ch 4 notation),
    the consolidated budget constraint of Ch 1 (`eq:intro-budget`) showing that the bills are
    government debt and base money in waiting; a worked example with teaching inputs, then the stock
    of MEFO bills from a verified source;
  - repressed inflation: a price ceiling with excess demand; what rations instead (queues, quality,
    allocation); why the measured price index understates;
  - bond underwriting by the central bank (Japan): primary purchases, then sales to banks to absorb
    the money ("sterilization" in the Bank of Japan's sense, if the source says so); compare with Ch 26's
    discounting of Treasury bills;
  - price-level targeting (Sweden) against inflation targeting: a shock to the price level is reversed
    under the first and not under the second; a two-period example, using Wicksell's rule of Ch 25.
- Compare boxes (2–4): 统制下的扩张 vs 市场经济中的扩张 (Germany vs Sweden or the New Deal: this box can
  carry the FORWARD_REFS row from Ch 28); 公开通胀 vs 被压抑的通胀;
  optionally 物价水平目标 vs 通胀目标 (Sweden 1931 vs today, with `\chref{ch:consensus}`).
- Contested questions (§8): what drove the German recovery (rearmament vs civilian work creation and the
  cycle); did Takahashi's policy rescue Japan (the exchange rate vs the deficits; the role of the
  military budget); how far Sweden's programme was followed in practice (Berg and Jonung's reading).
  Do not decide for the reader; state the political character and the human cost plainly.
- Figures (2–4, at least two from snapshot data): GDP per head 1929–1938, 1929 = 100, for Germany,
  Japan, Sweden, the US, Britain and France (Maddison); Germany's public spending or MEFO bills; Japan's
  government bonds held by the Bank of Japan; Sweden's price index against the goal.
- Legacy: central-bank finance of deficits and fiscal dominance (`\chref{ch:fiscaldominance}`), price
  freezes and repressed inflation in planned economies (`\chref{ch:planned}`), price-level targeting
  in the debate on the zero lower bound (`\chref{ch:zlb}`), the Bank of Japan's yield-curve control
  (`\chref{ch:abenomics}`).
- Ending: after `\end{answers}`, return to the opening and hand over Ch 31's question
  "没有市场价格，经济能不能算清楚该生产什么？".
- Labels: sections `sec:alternatives-…`; `eq:alternatives-…`, `fig:alternatives_…`,
  `tab:alternatives-…`, `ex:alternatives-…`.

## 第 31 章 `ch:soviet` 苏联工业化与社会主义核算论战 (`zh/ch31_soviet.tex`)

- Neighbours:
  - Ch 22 owns Marx: accumulation, crises, the reproduction schemes (`eq:marx-…`), and the line from
    the schemes to the input–output table and the planners' material balances (its legacy names this
    chapter and Ch 43). Refer back; do not retell Marx.
  - Ch 26 owns war finance and hyperinflation in Germany; the Soviet hyperinflation of 1918–1924 and the
    chervonets appear here only as the background of War Communism and NEP (one paragraph; Ch 52 owns
    the cross-country comparison of stabilizations).
  - Ch 29 owns the Depression abroad; Ch 30 compares the five-year plans with Germany, Japan and Sweden
    in one clause; Ch 34 owns the Soviet war economy (1941–45); Ch 43 owns China's planned economy and
    the Great Leap Forward famine; Ch 81 owns the reliability of Soviet statistics as a general
    question (one clause with `\chref{ch:datareliability}`, but state here what uncertainty the
    growth figures carry).
- Owns:
  - War Communism (1918–1921), NEP (1921–1928: the tax in kind, the scissors crisis of 1923, the
    chervonets), the industrialization debate (Preobrazhensky's primitive socialist accumulation vs
    Bukharin, in short phrases or verified summaries), the grain procurement crisis of 1927–28;
  - the first five-year plan (from October 1928; approved in 1929; declared fulfilled in four years and
    a quarter at the end of 1932), forced collectivization from 1929–30, the deportation of the
    "kulaks", the famine of 1932–1933 (Ukraine, Kazakhstan, the Volga and elsewhere), the second plan;
  - planning in practice: material balances (supply = output + stocks + imports against uses), why
    they need iteration, the planners' priorities; the price system that remained (wages, retail
    prices, the turnover tax);
  - the calculation debate: Mises (1920), Lange (1936–37) and the trial-and-error "market socialism",
    Hayek (1945, "The Use of Knowledge in Society"); later readings in one clause (the incentive
    problem, the soft budget constraint of Ch 43, if promised);
  - Soviet growth and its uncertainty: official indices against Western recalculations (Bergson;
    Khanin as reported by Harrison), the index-number problem (the Gerschenkron effect), Allen's (2003)
    counterfactual reading against those who see the growth as bought by famine and coercion.
- The human cost and the political character stated plainly (write_template rule 5): collectivization
  by force, deportations, the famine's deaths (give the range of estimates from verified demographic
  sources and say where they differ), the Gulag's labour as part of the plan's economy if sourced.
- Promises: FORWARD_REFS rows from Ch 22 (material balances; read them in full, mark them done).
- When it begins: Ch 30 ends by handing over "没有市场价格，经济能不能算清楚该生产什么？"; keep it.
- Neighbour in Part 5: Ch 30 compares the five-year plans with Germany's Four-Year Plan in one clause
  at most; read Ch 30's text when it is committed and do not retell what it says.
- Opening (suggested, verify every detail): a dated moment of the plan, e.g. the Sixteenth Party
  Conference's approval of the first five-year plan (April 1929) or the declaration of January 1933
  that it was fulfilled in four years and three months; or Mises's article of 1920 and the year's
  War Communism; a person, a date and the question within the first page.
- People (only where sourced): Lenin (NEP), Stalin, Preobrazhensky, Bukharin, Gosplan's chairmen
  (Krzhizhanovsky, Kuibyshev), Ludwig von Mises (1881—1973), Oskar Lange (1904—1965), Friedrich Hayek
  (1899—1992), Abram Bergson, Robert Allen as author.
- Case box: the chapter itself is outside the US and Britain; a dated case box such as 哈萨克斯坦 ·
  1930—1933 · 游牧的终结 (if verified sources allow) or 马格尼托哥尔斯克 · 1929—1932 · 一座计划中的钢城.
- Data and sources (probe first; on 2026-10-22 the shell reached Econlib (Hayek 1945,
  `library/Essays/hykKnw.html`; check its reprint terms), Mark Harrison's Warwick pages, marxists.org
  (translations; check each text's licence), prlib.ru, archive.org, NBER, the GGDC (Maddison 2023) and
  econstor; the Mises Institute's CDN answered 403 on the second probe (the first answered), mises.org's
  pages and Princeton UP answered 403, cpsjournal.ca did not answer, Russian statistical sites did not
  answer). Chapter 29's `maddison2023_interwar` already holds GDP per head 1925–1938 for many
  economies; extend it or add a series for the USSR 1913–1940 with Maddison's own caveat:
  - Mises (1920; d. 1973, in copyright): short phrases from the English translation of 1935 (in Hayek
    ed., *Collectivist Economic Planning*); Lange (1936–37, *Review of Economic Studies*; d. 1965, in
    copyright): short phrases, through a readable copy; Hayek (1945, *AER*; d. 1992): short phrases;
  - the five-year plan's figures from the plan document (Gosplan 1929; English editions of 1929–30 on
    archive.org, check the copyright page) and the official results of 1933, both as the planners'
    claims;
  - Western recalculations and Allen (2003): through Harrison's open papers and verified summaries;
  - the famine: demographic estimates from open-access publications (e.g. *Canadian Studies in
    Population*) and the range in Davies and Wheatcroft through verified summaries;
  - Maddison 2023 (CC BY 4.0) for the USSR's GDP per head, with its own caveat on Soviet data.
- Teaching:
  - a material balance for one good (steel) and a two-sector consistency check with a small
    input–output matrix (numpy), teaching inputs; what changes when one target is raised;
  - Lange's trial and error: a planner adjusts a price by excess demand, $p_{t+1}=p_t+\lambda(D-S)$,
    with teaching inputs; when it converges and what information it needs, against Hayek's point;
  - the index-number problem: growth measured at early-year prices vs late-year prices for two goods
    whose relative price falls as output soars (teaching inputs, then the direction of the Soviet
    case).
- Compare boxes (2–4): 物资平衡 vs 价格机制; 兰格的市场社会主义 vs 哈耶克的知识论证; optionally 苏联的五年计划
  vs 纳粹德国的四年计划 (both 1936-era plans, with `\chref{ch:alternatives}`), or 官方增长 vs 西方重估.
- Contested questions (§8): could a socialist economy calculate (Mises/Hayek vs Lange), and what the
  Soviet record shows about it; how fast the Soviet economy grew and whether the coercion bought the
  growth (Allen vs the critics). Do not decide for the reader.
- Figures (2–4, at least two from snapshot data): GDP per head 1913–1940 for the USSR against others
  (Maddison); plan targets against reported output for a few goods; grain procurement and harvest
  around 1928–1934 from a verified table.
- Legacy: shadow prices and linear programming (Kantorovich, one clause; `\chref{ch:planned}`), the
  soft budget constraint (`\chref{ch:planned}` or `\chref{ch:transition}` if it exists), the reliability
  of planned-economy statistics (`\chref{ch:datareliability}`).
- Ending: after `\end{answers}`, return to the opening and hand over Ch 32's question
  "如果人人都想多储蓄，总储蓄为什么可能反而减少？".
- Labels: sections `sec:soviet-…`; `eq:soviet-…`, `fig:soviet_…`, `tab:soviet-…`, `ex:soviet-…`.
