# Part 1 (第一部分 宏观的语言): notes for the chapter writers

Part 3 is written and reviewed, so Part 1 can be written against it. Chapters 2–5 are written one at a
time in that order (docs/WORKFLOW.md, sequential mode); Chapter 1, which introduces the whole course,
is written last, after Part 2. Give the writer `batch_brief.txt` plus its section below.

Part 1 differs from Part 3 in one way: these chapters teach tools, not an era. Each still opens with
"当时的世界", the moment the tool was invented to answer a question (the Depression without national
income figures, the 1990s argument over the US CPI, the 2008 balance sheets, Sri Lanka in 2022), and
ends with "今天还剩什么"; but the body is mostly the tool itself, taught with worked examples. Numbers
are modern statistics: take them from official providers the shell can reach (BEA, FRED and FRASER,
the Federal Reserve, the Bank of England, the PBoC and SAFE, the Central Bank of Sri Lanka, Japan's
Ministry of Finance), each as a snapshot with a fetch script that checks the hash; US federal data are
public domain. Mark every fact after 2024 with its date. The written chapters (10–17) have promised
things to these chapters (docs/FORWARD_REFS.md); each section below lists them, and each must be kept.

## 第 2 章 `ch:accounts` 国民核算与恒等式 (`zh/ch02_accounts.tex`)
- Neighbours: Ch 3 owns price indices and the deflator as an index (this chapter defines real GDP and the implicit deflator only as nominal / real); Ch 5 owns the balance of payments and the foreign position (here the rest of the world is one balance, $X-M$); Ch 16 has Quesnay's Tableau (`\chref{ch:mercantilism}`, `eq:merc-tableau`) — refer back to it as the forerunner, do not retell; Ch 81 owns data reliability in planned and authoritarian economies.
- Owns: GDP by production (value added), expenditure and income, and why the three are equal; final vs intermediate goods; stocks vs flows; GDP vs GNI; a simplified flow-of-funds table; the sector-balance identity $(S-I)+(T-G)+(M-X)=0$ (running model M0) and why it has no causal direction; what GDP leaves out (household work, the non-market sector, assets, distribution).
- Promise (FORWARD_REFS, from Ch 16): sector accounts in which every payment is another sector's receipt, sector balances sum to zero, and output covers intermediate inputs, the upkeep of capital and incomes.
- When it began: Senate Resolution 220 (1932) and Kuznets's report *National Income, 1929–32* (Senate Document 124, 1934; FRASER) — the numbers it gave and its own warning that national income does not measure welfare (quote verbatim). Stone and Meade's British estimates (1941) and the SNA as the international standard (SNA 2008; verify the 2025 revision's status).
- Case (outside the US/UK): China's move from the Material Product System (MPS) to the SNA — GDP first published, the MPS dropped, the 2004 economic census revision; or the rebasing of Nigeria's or Ghana's GDP. Official documents only (NBS; verify host).
- Data: US GDP, GDI and the statistical discrepancy (BEA NIPA tables 1.1.5, 1.10 or the FRED copies); US sector net lending (BEA/Fed); one country's three-way accounts in a worked table.
- Figures: a canvas diagram of value added along a production chain and of the circular flow; US sector balances over time from the snapshot.
- Compare boxes: identity vs behavioural equation; stock vs flow; GDP vs GNI.

## 第 3 章 `ch:prices` 价格、通胀与利率 (`zh/ch03_prices.tex`)
- Neighbours: Ch 2 defines real GDP and the implicit deflator; Ch 4 owns how the central bank sets the short rate (here the short rate is given); Ch 25 owns Wicksell's natural rate; Ch 23 the 1896 US gold-standard politics (mention at most); Ch 52 hyperinflation.
- Owns: Laspeyres, Paasche and Fisher indices; substitution and quality bias of the CPI and the Boskin Commission (1996); CPI vs GDP deflator; the Fisher relation, ex ante vs ex post real rates; bond price, yield to maturity, duration; the shapes of the yield curve; breakeven inflation from nominal and index-linked bonds and the premia mixed into it.
- Promise (FORWARD_REFS, from Ch 11): nominal vs real values; real wages and the choice of deflator; how inflation redistributes wealth under contracts written in nominal terms.
- When it began: Fisher (1896) *Appreciation and Interest* (archive.org) — written in a decade of falling prices in which debtors and creditors argued over the gold standard; the Boskin report (Senate print, 1996; find a reachable copy, FRASER or GovInfo).
- Case (outside the US/UK): Japan's yield curve under negative rates (MoF JGB yields, 2016–2024); index-linked gilts (1981) and TIPS (1997) as the instruments behind breakeven inflation.
- Data: CPI and deflator series (FRED, BEA); JGB yields by maturity (MoF Japan CSV); TIPS and nominal Treasury yields, breakeven (FRED).
- Figures: a worked price–yield curve with duration as its slope; Japan's yield curves on chosen dates; US breakeven inflation.
- Compare boxes: nominal vs real interest rate; CPI vs GDP deflator; yield to maturity vs holding-period return.

## 第 4 章 `ch:money` 货币、银行与央行的资产负债表 (`zh/ch04_money.tex`)
- Neighbours: Ch 10 (bills, banking by transfer — refer back); Ch 12 (paper money's value — refer back); Ch 15 (the Bank of England 1694, bank money in Amsterdam); Ch 17 (rice as unit of account); Ch 23 the gold standard; Ch 45 monetarism; Ch 52 money demand (Cagan); Ch 77 digital money; Ch 74/75 MMT and fiscal dominance — state the open questions, do not decide them.
- Owns: balance sheets of the central bank, a commercial bank, the Treasury and a household; following a loan, a tax payment and a bond issue through them; base money vs broad money; "loans create deposits" vs the textbook money multiplier (McLeay, Radia & Thomas 2014); corridor vs floor systems and the Fed's ample-reserves regime after 2008; the PBoC's reserve requirement and relending; the functions of money and their separation.
- Promises (FORWARD_REFS):
  - from Ch 12: fiat money is valuable because it is a central-bank liability backed by the state's taxes and laws; the policy rate as the "peg" of a floating currency;
  - from Ch 10: bank deposits are bank liabilities; a transfer moves a liability from one customer to another; banks settle only net balances (clearing, correspondent banks);
  - from Ch 13: what the state accepts in taxes largely decides what money people hold — present it as an argument with its evidence and limits (Smith 1776, Book II ch. 2, the passage on taxes payable in paper; Knapp's state theory if verified; dollarization as the counter-case), and if the evidence supports only a weaker claim, change Ch 13's sentence to match and say so;
  - from Ch 17: the functions of money can be separated (rice as unit of account in Tokugawa Japan).
- When it began: 2008 — the Fed's balance sheet and reserves (H.4.1, FRED), interest on reserves (October 2008); the Bank of England's 2014 explanation of money creation.
- Case (outside the US/UK): the PBoC's reserve-requirement ratio and relending (PBoC documents); optionally a unit of account separated from the means of payment (Chile's Unidad de Fomento — verify).
- Figures: canvas T-accounts for a loan, a tax payment and a bond purchase; the Fed's balance sheet and reserves 2007–2026; a corridor vs floor diagram.
- Compare boxes: base vs broad money; multiplier vs endogenous-money story; corridor vs floor.

## 第 5 章 `ch:external` 国际收支与汇率 (`zh/ch05_external.tex`)
- Neighbours: Ch 2 (sector balances, here opened up); Ch 4 (reserves on the central bank's balance sheet); Ch 13 (`eq:silver-arbitrage`); Ch 16 (Mun's balance of trade); Ch 19 the price–specie flow; Ch 36 Bretton Woods; Ch 37 Mundell–Fleming and the trilemma; Ch 61 currency crises; Ch 76 the currency hierarchy.
- Owns: the balance of payments by BPM6 — current, capital and financial accounts, errors and omissions, and why they sum to zero; the open-economy sector balance; the international investment position and valuation effects; nominal vs real exchange rates ($e$ = domestic currency per unit of foreign, STYLE §3); PPP (absolute, relative) and covered and uncovered interest parity, with their ranges of validity; reserves, foreign-currency debt and the regime as the external constraint.
- Promises (FORWARD_REFS):
  - from Ch 10: covered interest parity — the forward–spot difference is set by the interest differential;
  - from Ch 13: the balance of payments and exchange rates; PPP and interest parity as the modern form of the arbitrage condition `eq:silver-arbitrage`;
  - from Ch 16: the goods balance as one part of the current account, services (freight, insurance) and capital flows beside it, and how an external balance adjusts through prices and the exchange rate.
- When it began / case (outside the US/UK): Sri Lanka 2022 — reserves, imports, the suspension of external debt service (CBSL documents); China's reserves and capital-account management (SAFE); the US current-account deficit as the contrast.
- Data: CBSL official reserves; SAFE reserves and BoP; BEA international transactions and IIP.
- Figures: a canvas BoP double-entry diagram; Sri Lanka's reserves 2018–2023; China's reserves.
- Compare boxes: current vs financial account; nominal vs real exchange rate; fixed vs floating.
