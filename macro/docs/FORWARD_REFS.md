# Forward references: what written chapters expect of chapters not yet written

Chapters are not written in order (Chapter 12 first, then Part 3, Parts 1 and 2 later). When a
written chapter refers to an unwritten one for a definition, a result or a later episode, the
promise is recorded here, so that the later chapter keeps it, or the earlier one is changed.

- **Writer of a chapter:** add one row for every `\chref`/`\ref` to an unwritten chapter that the
  reader needs (a concept the text uses without defining it, a result it takes as given, a story
  it hands on). A bare "see also" needs no row.
- **Writer of a chapter that has rows here:** read them before writing; deliver each promise, or
  change the earlier chapter's sentence and say so in the report. Mark the row done with the
  section label that delivers it.

| From | To | What the reader is promised | Status |
|---|---|---|---|
| 12 (opening, §12.2) | 4 `ch:money` | Fiat money is valuable because it is a central-bank liability backed by the state's taxes and laws; the policy rate as the "peg" of a floating currency (compare box 称提 vs today's central bank) | open |
| 12 (§12.7, legacy) | 8 `ch:qinhan` | The 《管子》 轻重 line of thought on the quantity of money and prices | open |
| 12 (§12.7) | 13 `ch:silver` | Bodin (1568) and the quantity theory; the Ming turn to silver and the market price of silver | done (`sec:silver-world`, `sec:silver-china`, `sec:silver-revolution`) |
| 12 (§12.7) | 19 `ch:bullion` | Hume and the quantity theory | open |
| 12 (compare boxes, legacy) | 23 `ch:goldstandard`, 61 `ch:emcrises` | Reserves behind convertible money: the gold standard and currency boards | open |
| 12 (legacy) | 50 `ch:budget` | The government budget constraint; "unpleasant arithmetic" | open |
| 12 (§12.7, legacy) | 52 `ch:hyperinflation` | Cagan's money-demand model explains the collapse of paper money | open |
| 12 (legacy) | 75 `ch:fiscaldominance` | Fiscal dominance: the central bank forced to finance deficits | open |
| 12 (legacy) | 77 `ch:digitalmoney` | Stablecoins as private notes backed by reserve assets | open |
| 12 (legacy) | 49 `ch:credibility`, 55 `ch:consensus` | Central-bank independence and inflation targeting as an answer to the lack of commitment | open |
| 10 (opening, §10.2 intuition and compare box, legacy) | 4 `ch:money` | Bank deposits are bank liabilities; a transfer moves a liability from one customer to another, and banks settle only net balances between them (clearing, correspondent banks) | open |
| 10 (§10.1) | 9 `ch:india` | The Indian Ocean trade that the Islamic world joined to the Mediterranean | open |
| 10 (legacy) | 5 `ch:external` | Covered interest parity: the forward–spot difference is set by the interest differential between two currencies | open |
| 10 (compare box, legacy) | 15 `ch:finrevolution` | Bank money of the Bank of Amsterdam (accounts of merchants centralised in a public bank); joint-stock companies with limited liability and transferable shares | done (`sec:finrev-amsterdam`, `sec:finrev-voc`) |
| 10 (compare box, legacy) | 21 `ch:divergence` | Institutional explanations of why Europe took off first, compared with the others (Chapter 10 ends the Maghribi traders debate — Greif's cultural beliefs vs Edwards & Ogilvie — by pointing here) | open |
| 10 (closing sentence) | 11 `ch:medieval` | The Black Death and the relative price of labour and land; repeated debasement of the coinage | done (`sec:medieval-malthus`, `sec:medieval-plague`, `sec:medieval-debasement`) |
| 11 (guide, §11.4 after the compare box, legacy) | 7 `ch:greekroman` | Diocletian's price edict (301) and why it failed; Chapter 11 says the price rises it faced were "inseparable from the debasement of the money" | open |
| 11 (guide, Example 11.5, compare box 实物冲击 vs 货币冲击, legacy) | 3 `ch:prices` | Nominal vs real values; real wages and the choice of deflator; how inflation redistributes wealth under contracts written in nominal terms | open |
| 11 (§11.2, legacy) | 21 `ch:divergence` | How Europe escaped the Malthusian steady state of `eq:medieval-dynamics` (income per head independent of technology and land) | open |
| 11 (§11.6 Oresme's second point, legacy) | 49 `ch:credibility` | The commitment problem of an authority that can change the money at will (time inconsistency) and central-bank independence as the answer | open |
| 11 (§11.6 Oresme's first point, legacy) | 50 `ch:budget` | Seigniorage / the inflation tax as a transfer of purchasing power from money holders to the issuer | open |
| 11 (compare box 铸币税 vs 通胀税, legacy) | 52 `ch:hyperinflation` | The revenue from the inflation tax is limited by money demand: at very high inflation people hold less money and the base shrinks | open |
| 11 (legacy) | 13 `ch:silver` | The sixteenth-century price revolution, with population (`eq:medieval-factor`) and American silver compared as causes | done (`sec:silver-revolution`, `ex:silver-malthus`, `sec:silver-test`) |
| 13 (guide, §13.2, legacy) | 5 `ch:external` | The balance of payments and exchange rates; purchasing-power and interest parity as the modern form of the arbitrage condition `eq:silver-arbitrage` | open |
| 13 (§13.2 after the intuition box, legacy) | 19 `ch:bullion`, 23 `ch:goldstandard` | Hume's price–specie flow mechanism and automatic adjustment of the balance of payments under the gold standard | open |
| 13 (legacy) | 76 `ch:hierarchy`, 61 `ch:emcrises` | An economy whose money is set abroad: the currency hierarchy and "original sin"; pegs that break when capital flows reverse | open |
| 13 (legacy) | 17 `ch:tokugawa` | Silver in Qing China and 银贵钱贱 (silver dear, copper cash cheap) | done (`sec:toku-qing`, `sec:toku-debate`, `sec:toku-test`) |
| 13 (legacy) | 4 `ch:money` | The text says Chapter 4 has already shown that what the state accepts in taxes largely decides what money people hold | open |
| 13 (legacy) | 75 `ch:fiscaldominance` | Taxes, money demand and the relation between fiscal and monetary policy, returned to | open |
| 13 (legacy) | 45 `ch:monetarism` | The quantity theory in twentieth-century monetarism; whether velocity is stable and whether money leads prices | open |
| 13 (deeper box, legacy) | 50 `ch:budget` | $D^{*}=PS/(r-g)$ as the basic tool for judging public debt; the case $r\le g$ under today's low interest rates | open |
| 13 (§13 debt, `eq:silver-debt`) | 50 `ch:budget` | Chapter 13 derives $d'=\frac{1+r}{1+g}d-ps$ and $D^{*}=PS/(r-g)$ with royal revenue as the denominator (kept by the author, 2026-10, as the exception in PLAN §1); Chapter 50 refers back to it and explains the change of denominator to GDP | open |
| 13 (compare box, legacy) | 51 `ch:latamdebt`, 69 `ch:eurocrisis` | Modern sovereign restructurings: exchange offers, haircuts that differ widely from case to case, creditor committees and holdouts | open |
| 13 (legacy) | 15 `ch:finrevolution` | How the Dutch Republic and England borrowed far more cheaply than Philip II | done (`sec:finrev-holland`, `sec:finrev-bank`, `ex:finrev-debt`, `tab:finrev-four`) |
| 13 (legacy) | 47 `ch:oil` | Governments that depend on volatile resource revenue (oil) | open |
| 13 (closing sentence) | 14 `ch:africa` | Whether a large empire (the Inca) could do without money: labour tribute and storehouses | done (`sec:africa-inca`, `sec:africa-test`) |
| 13 (§13.1, Potosí) | 14 `ch:africa` | The colonial mita (1573–1812) that mined Potosí's silver: its Inca origin, its human cost and its long-run effects (Dell 2010) | done (`sec:africa-inca`, subsection 殖民时期的米塔制 and the compare box) |
| 14 (Inca, intuition box) | 6 `ch:mesopotamia` | Temples and palaces that organised production by keeping accounts rather than by using money | open |
| 14 (closing sentence) | 15 `ch:finrevolution` | How a sovereign makes lenders believe it will repay, and so borrows a lot at low rates (Mansa Musa's lenders could not enforce) | done (`sec:finrev-england`, `eq:finrev-commit`, `sec:finrev-test`) |
| 14 (case box, legacy) | 16 `ch:mercantilism` | Restricting trade "that the treasure might be kept" at home: the European mercantilists' version of Adahoonzou II's pretext | done (`sec:merc-world`, `sec:merc-mun`) |
| 14 (legacy) | 23 `ch:goldstandard` | Menger against Knapp: money as a commodity that emerges from trade or as a creature of the state (cowries, salt, cloth and cacao were not state-issued but were shaped by what rulers accepted in tax) | open |
| 14 (legacy) | 24 `ch:periphery`, 76 `ch:hierarchy` | Economies whose money is supplied or set from elsewhere; colonial currencies (the West African pound) that replaced commodity monies | open |
| 14 (legacy) | 41 `ch:development` | Institutions with long-run effects on development (Dell's mining mita) | open |
| 14 (legacy) | 63 `ch:minsky` | Modern monetary theory as the far end of the chartalist (Knapp) side of the question "must money be issued by the state?" | open |
| 14 (legacy) | 66 `ch:zlb` | The cost of holding and storing cash sets how far below zero interest rates can go (cacao's negative own return) | open |
| 14 (legacy) | 77 `ch:digitalmoney` | Money as record-keeping ("money is memory", Kocherlakota 1998): who keeps the ledger, what it records, who can see it; privately issued stablecoins as the other side of "must money be issued by the state?" | open |
| 15 (debt example, legacy) | 50 `ch:budget` | The formal derivation of government debt dynamics (Chapter 15 reuses Chapter 13's `eq:silver-debt` to compare England 1714–1738 with Philip II, dividing debt by revenue) | open |
| 15 (legacy) | 23 `ch:goldstandard` | Runs and the lender of last resort under the gold standard (the Bank of Amsterdam's 1672 run and its withdrawal fee are the early version) | open |
| 15 (legacy) | 77 `ch:digitalmoney` | Privately issued stablecoins and the problems of the Bank of Amsterdam: metal reserves, hidden lending, collapse without fiscal backing (Frost, Shin and Wierts 2020) | open |
| 15 (legacy) | 49 `ch:credibility`, 50 `ch:budget` | Central bank independence and fiscal rules as ways of making the costs of default or inflation fall on those who decide (Chapter 15's $K$ in `eq:finrev-commit`) | open |
| 15 (legacy) | 50 `ch:budget`, 70 `ch:stagnation` | How high debt can be sustained when the interest rate is below or close to the growth rate | open |
| 15 (legacy) | 16 `ch:mercantilism` | John Law's experiment in France and the South Sea bubble of 1720 (England's conversion of short-term debt into company shares) | done (`sec:merc-system`, `sec:merc-southsea`) |
| 15 (legacy) | 18 `ch:smith` | Smith's views on banks and paper money (Chapter 15 quotes only his digression on the Bank of Amsterdam) | open |
| 16 (§16.2, legacy) | 5 `ch:external` | The balance of payments: the goods balance as one part of the current account, services (freight, insurance) and capital flows beside it, and how an external balance adjusts through prices and the exchange rate (Chapter 16 assumes trade in goods settled in metal only) | open |
| 16 (§16.2, takeaways, legacy) | 19 `ch:bullion` | Hume's price–specie-flow mechanism: a surplus brings in metal, raises prices at home and corrects itself (Chapter 16 states the result and leaves the mechanism to Hume) | open |
| 16 (§16.2, §16.3 intuition) | 18 `ch:smith` | Smith's critique of the mercantile system (gold and silver are wanted for what they buy) and the real-bills doctrine, which meets the question Law's land bank left open: what limits the demand for notes lent on fixed terms | open |
| 16 (§16.4 intuition, legacy) | 37 `ch:mundell` | A central bank that pegs the exchange rate gives up control of the money supply; the trilemma (Law's peg of the share price, `eq:merc-peg`, is the analogy) | open |
| 16 (case box, Bank of England 1720) | 23 `ch:goldstandard` | The lender of last resort: a run stopped by the belief that enough people stand behind the bank, not by the metal in its vault (Cantillon's account of 1720) | open |
| 16 (§16.6, legacy) | 71 `ch:heterogeneity` | The distributional effects of monetary policy depend on who gets new money first (the Cantillon effect, `eq:merc-cantillon`); monetary policy works through the incomes, assets and debts of different households | open |
| 16 (legacy) | 78 `ch:fragmentation` | Global imbalances and trade conflict: bilateral deficits still described as losses | open |
| 16 (legacy) | 66 `ch:zlb`, 75 `ch:fiscaldominance` | Central-bank purchases of government bonds to lower long rates, and whether monetary policy is financing the treasury (Law's System as the extreme case: the bank of issue merged into the company that farmed the taxes, whose head was finance minister) | open |
| 16 (legacy) | 50 `ch:budget` | Debt sustainability; Velde's "government equity" (claims whose return varies with the state of the economy) as an alternative to fixed-interest debt | open |
| 16 (legacy) | 32 `ch:generaltheory` | Whether more money raises output when there is unemployment (Law's claim of 1705; Velde notes that Law's reputation rose in the 1930s) | open |
| 16 (§16.7, legacy) | 2 `ch:accounts`, 22 `ch:marx` | Sector accounts in which every payment is another sector's receipt, sector balances sum to zero, and output covers intermediate inputs, the upkeep of capital and incomes (Quesnay's Tableau, `eq:merc-tableau`, is the forerunner); Marx's schemes of reproduction and input–output tables built on it | done for Ch 2 (`sec:accounts-gdp`, `sec:accounts-sectors`, `tab:accounts-flows`); open for Ch 22 |
| 17 (§17.2 越后屋的换算表, legacy) | 54 `ch:newkeynesian` | Menu costs as one reason for sticky prices (Echigoya's 60-momme table removed the part of the price that changed from the price tag) | open |
| 17 (legacy, 期货与中央清算) | 64 `ch:gfc` | Moving over-the-counter derivatives to central counterparty clearing after the global financial crisis; the risk a clearinghouse bears when margins are low (`ex:toku-hedge`) | open |
| 17 (legacy, 铸币税与贬值) | 75 `ch:fiscaldominance`, 52 `ch:hyperinflation` | The inflation tax as today's form of the revenue a debasement raised (`eq:toku-seign`, a rate of about 32% in 1695) | open |
| 17 (legacy, 货币错配) | 61 `ch:emcrises`, 76 `ch:hierarchy` | Currency mismatch: income in one money, obligations in another (Qing taxpayers earned copper and owed silver), and the burden when the debt currency appreciates | open |
| 17 (legacy, 名义合约与通缩) | 28 `ch:depressionus` | Fisher's debt deflation: how nominal debts redistribute wealth in inflation and deflation (the Genbun recoinage eased the samurai's debts; dear silver made silver debts and taxes heavier) | open |
| 17 (legacy, 记账单位) | 4 `ch:money` | The functions of money can be separated: rice was the unit of account in Tokugawa Japan but not the medium of exchange (Schaede) | open |
| 17 (pitfall box 银贵钱贱) | 24 `ch:periphery` | Opium, silver and China's money in the second half of the nineteenth century | open |
| 17 (closing sentence) | 18 `ch:smith` | Smith asking systematically where the wealth of nations comes from and on what principle banks should lend (not "the first": Chapter 16 covers Cantillon and Quesnay) | open |
| 2 (§2.3, deflator) | 3 `ch:prices` | How chained real GDP is built; why the GDP deflator differs from the consumer price index (Ch 2 defines the deflator only as nominal / real GDP) | open |
| 2 (§2.4, derivation of `eq:accounts-balances`) | 5 `ch:external` | With cross-border wages, interest, profits and transfers, the third term of the sector-balance identity is minus the current-account balance; the rest-of-the-world account opened into current and financial accounts | open |
| 2 (ex:accounts-thrift, pitfall box) | 20 `ch:say`, 32 `ch:generaltheory` | What happens after unplanned inventories pile up: Say's law against the paradox of thrift; behavioural equations (consumption function, multiplier) that give the identity $S=I$ a causal direction | open |
| 2 (§2.4, US sector balances; pitfall box) | 50 `ch:budget`, 63 `ch:minsky`, 64 `ch:gfc` | Which sector drove the US balances around 2000, 2009 and 2020 (private borrowing, deficits): the identity is shown, the causal story is promised. The pitfall box names the two readings: Chapter 63 gives the sectoral-balance view (the private sector's desired net saving is fairly stable, so a slump's deficit is largely passive), Chapter 50 crowding out near full employment and Ricardian equivalence; both should cite the authors (candidates: Godley & Lavoie 2007; Barro 1974) | open |
| 2 (legacy, 三种算法与恒等式) | 50 `ch:budget` | The government budget constraint and debt dynamics derived from the government's own account in the sector accounts | open |
| 2 (§2.6, legacy) | 81 `ch:datareliability` | Reliability of official statistics, especially in planned and authoritarian economies (Ch 2 shows China's 2004 census revision only as a revision of coverage) | open |
| 2 (§2.7, legacy) | 71 `ch:heterogeneity` | How the distribution of income and wealth matters for macroeconomics (Kuznets's 1934 warning that welfare cannot be measured without the distribution) | open |
