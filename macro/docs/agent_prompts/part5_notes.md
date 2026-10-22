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
