# Part 2 (第二部分 古代世界): notes for the chapter writers

Parts 1 and 3 are written and reviewed, so Part 2 can be written against them. Chapters 6–9 are written
one at a time in that order (docs/WORKFLOW.md, sequential mode), each reviewed before the next. Give the
writer `batch_brief.txt` plus its section below.

Part 2 differs from the others in its evidence. There are no official statistics. The numbers are a
few figures that ancient texts state (rates of interest, prices, coin counts, sums of money) and
modern reconstructions (prices from the Babylonian astronomical diaries, coin weights and fineness).
So:

- **Translations.** Quote a public-domain translation verbatim in the snapshot and render it in
  Chinese in the text. Name the translator and edition in the caption or the bibitem, as STYLE §2
  asks ("引用译本时注明译本"). Examples: King 1910 for Hammurabi; Rawlinson for Herodotus; Schoff 1912
  for the Periplus; Shamasastry 1915 for the Arthashastra; the *Ante-Nicene Fathers* for Lactantius.
  Where a modern scholarly edition is needed (for example the interest provisions in the gap of the
  Hammurabi stele), cite the scholarly work and quote only a short phrase.
- **Classical Chinese.** Quote from the daizhigev20 corpus and verify with `verify_quotes.py $CORPUS`.
  《管子》 (`子藏/法家/管子.txt`) and 《盐铁论》 (`儒藏/语录/盐铁论.txt`) are outside the default
  sparse checkout; Chapter 8 adds them to `CORPUS_PATHS` in `tools/setup_env.sh`.
- **Uncertainty.** Every ancient number is a claim by the text or by the scholar who reconstructed
  it. Say which. State the margin when the source gives one, and say so when it gives none.
- **Dates.** Years before the common era are written "公元前 1754 年". Give a dating's basis when it
  is disputed (the Arthashastra; the "middle chronology" for Hammurabi).
- **Today.** "今天还剩什么" connects each ancient mechanism to its modern form through the chapters
  that own it (`\chref`), without retelling them.

The written chapters have promised things to these chapters (docs/FORWARD_REFS.md, rows listed
below); each must be kept or the earlier sentence changed. Equations that later chapters already own
are referred back to, not derived again:

- the Fisher relation between two standards, `eq:prices-fisher` (Ch 3, which tells Fisher's gold and wheat);
- the storehouse equation, `eq:africa-store` (Ch 14, Inca storehouses);
- risk-neutral default pricing, `eq:africa-risk` (Ch 14);
- the arbitrage band, `eq:africa-carry` (Ch 14);
- the quantity equation, `eq:silver-qty` (Ch 13);
- gross seigniorage, `eq:medieval-seigniorage` (Ch 11);
- the balance-of-payments identity, `eq:external-bop` (Ch 5).

## 第 6 章 `ch:mesopotamia` 美索不达米亚与埃及：神庙、宫廷与记账 (`zh/ch06_mesopotamia.tex`)
- Neighbours:
  - Ch 4 owns the functions of money and the state theory (Knapp); refer back (`sec:money-functions`).
  - Ch 14 tells the Inca records and Kocherlakota's "money is memory"; refer back (`sec:africa-inca`), do not retell.
  - Ch 3 owns the Fisher relation. Ch 7 owns coinage (Lydia), so this chapter stops before coins.
  - Ch 9 owns the Arthashastra's rates by risk.
- Owns:
  - silver (shekel, mina) and barley (sila, gur/kur) as units of account in temple and palace accounts;
  - credit before coinage (loan tablets, interest in silver and in barley);
  - the legal limits on interest and on debt bondage;
  - debt cancellations (the *mīšarum* and *andurārum* edicts) and their logic;
  - Egypt's in-kind wages and granaries;
  - the barter-origin vs credit-origin debate;
  - the redistribution vs market debate.
- Promises (FORWARD_REFS):
  - row 53, from Ch 14: temples and palaces that organised production by keeping accounts rather than by using money;
  - row 113, from Ch 5: debt and records older than coinage (who owed whom how much barley and silver) and how an economy without coinage priced, lent and taxed.
- When it began: an Old Babylonian loan of silver or barley at interest. Hammurabi's laws (c. 1754 BC, middle chronology):
  - §48, a failed harvest defers the debt and "he washes his debt-tablet in water";
  - §117, debt bondage limited to three years, free in the fourth;
  - both in King 1910, avalon.law.yale.edu.
- Sources checked (2026-10-14):
  - **Interest.** The interest provisions fall in the gap of the stele and are missing from King 1910. The *Chicago Assyrian Dictionary* (free PDFs from ISAC) gives them.
    - Volume Ṣ, s.v. *ṣibtu* A, pp. 158–159, quotes the Laws of Eshnunna §18A: "per shekel one pays as interest 36 grains, per kur one pays as interest 100 (silas) of barley". That is 20% on silver (180 grains to the shekel) and 33⅓% on barley (300 sila to the kur).
    - The same entry refers to CH § L after Driver & Miles, *The Babylonian Laws*, p. 38.
    - Verify the extraction: the PDF is a scan with a text layer.
  - **Prices.** van der Spek, van Leeuwen & van Zanden, "Monthly prices of various commodities in Babylon, −582 to −61" (dataverse.nl, doi:10.34894/VJZ5Z9, CC0).
    - File `appendix.xlsx`, sha256 152deda2…5fce3.
    - Six goods in grams of silver per 100 litres (wool per mina); 548 barley observations.
    - Spikes in 322–308 BC (the wars after Alexander) and 83 BC.
    - Cite it as the dataset asks: van der Spek, van Leeuwen & van Zanden (2014), "Markets from Ancient Babylonia to the Modern World – An Introduction", in their (eds.) *A History of Market Performance* (Abingdon: Routledge), 1–16; the dataset was deposited on 2025-12-22.
- Candidate scholarship (verify):
  - **Barter side:** Smith 1776 Book I ch. 4 (key `smith1776`); Menger 1892 "On the Origin of Money", *Economic Journal* (public domain).
  - **Credit side:** Mitchell-Innes 1913 "What is Money?", *Banking Law Journal* (public domain; cites Babylonian tablets); Humphrey 1985 "Barter and Economic Disintegration", *Man*; Graeber 2011 (contested — one view, with its critics).
  - **Debt cancellation and the edicts:** Hudson's work (Hudson & Van De Mieroop eds. 2002); the Ammi-saduqa edict (CAD *mīšaru*, *andurāru* entries).
  - **Markets:** Polanyi's view of Mesopotamia as redistributive, and the price-data answer of van der Spek and co-authors.
  - **Egypt:** Deir el-Medina rations and the strike of year 29 of Ramesses III; Černý / Janssen on prices in *deben*. Find a reachable translation; if none, describe and cite.
- Teaching ideas:
  - **Own rates of interest.** The silver and barley rates imply a seasonal price of barley, since 1+i_barley = (1+i_silver)·p_lent/p_repaid. With 20% and 33⅓% this gives p_lent/p_repaid ≈ 1.11. This is `eq:prices-fisher` with silver and barley as the two standards; refer back, keyeq only if it adds the seasonal step.
  - **Seasonality check.** Test the implied seasonal swing against the Babylonian price data, by month. Say plainly that the data are a thousand years later and from a different regime.
  - **Debt dynamics.** Debt at 33⅓% against an uncertain harvest: why a creditor's claim can outgrow the debtor, and what §48, §117 and periodic cancellation do to it.
- Data: `babylon_prices` (fetch script, hash checked, CC0, may be committed); `meso_facts`.
- Figures:
  - a canvas diagram of a temple's accounts (rations out, barley and silver in, debts on tablets);
  - Babylonian barley prices in silver (log scale) with the dated shocks;
  - mean price by month (the seasonal check).
- Compare boxes:
  - unit of account vs medium of exchange;
  - barter origin vs credit origin;
  - redistribution vs market (optional).
- Case: the Ammi-saduqa edict (c. 1646 BC), or Deir el-Medina.
- Pitfall: "没有铸币就没有货币" or "物物交换是货币之前的普遍阶段".

## 第 7 章 `ch:greekroman` 希腊与罗马：铸币、城邦财政与帝国的贬值 (`zh/ch07_greekroman.tex`)
- Neighbours:
  - Ch 6 (units of account before coins).
  - Ch 11 owns seigniorage as a fiscal tool and its formula (`eq:medieval-seigniorage`) and Oresme. Refer back, add only what is Roman.
  - Ch 17 (`eq:toku-content`, recoinage).
  - Ch 12 (paper money's over-issue, for the compare box).
  - Ch 3 (inflation, indices). Ch 52 hyperinflation.
- Owns:
  - coinage's invention in Lydia (Herodotus 1.94) and the coin as a state-guaranteed weight;
  - Athens' Laurion silver and the fleet (Herodotus 7.144); Xenophon's *Ways and Means* (*Poroi*) as an early tract on public revenue;
  - Roman coinage and the decline of the denarius's silver, 1st–3rd centuries;
  - the price rises of the third century (Egyptian papyri);
  - Diocletian's price edict (301) and its failure;
  - Finley's primitivism vs Temin's market economy.
- Promise (FORWARD_REFS row 32, from Ch 11): the edict and why it failed; Ch 11 says the price rises it faced were "inseparable from the debasement of the money" — show that link with evidence, or change Ch 11's sentence.
- When it began: Lactantius, *De mortibus persecutorum* 7 (ANF vol. 7, ccel.org), on the edict:
  - "much blood shed for trifles";
  - goods withheld from sale;
  - its abrogation "from mere necessity".
  - He was a Christian polemicist writing against Diocletian; say so.
  - The edict's preface: find a reachable translation (attalus.org, LacusCurtius, or Frank's *ESAR* vol. 5 if it can be quoted).
- Sources checked (2026-10-14):
  - LacusCurtius (penelope.uchicago.edu): Herodotus in Rawlinson's translation, Pliny's *Natural History* in Latin.
  - Gutenberg: Xenophon (Dakyns).
  - ccel.org: ANF vol. 7.
  - dspace.mit.edu: Temin's MIT working papers.
- Candidate scholarship (verify):
  - **Primitivists:** Finley 1973 *The Ancient Economy* (cite, quote briefly at most); Hopkins 1980 "Taxes and Trade" (*JRS*).
  - **Market reading:** Temin 2001 "A Market Economy in the Early Roman Empire" (*JRS*; MIT working paper); Temin 2013.
  - **Prices and plague:** Harper 2016 "People, Plagues, and Prices in the Roman World" (*JEH*; check for a replication dataset on Harvard Dataverse).
  - **Denarius fineness:** Walker 1976–78, or Butcher & Ponting. Find a reachable table; if none is reachable, use the few data points stated in reachable texts and say the series is not reproduced.
  - **Unreachable:** Scheidel's Princeton working papers (403).
- Teaching ideas:
  - debasement as a tax on coin holders, using Ch 11's formula with a Roman example;
  - why a price ceiling below the market price produces withholding and black markets (a supply–demand canvas);
  - the edict's prices as relative prices (wheat against a day's wage).
- Figures:
  - the denarius/antoninianus silver content (if a reachable source);
  - a canvas price-ceiling diagram;
  - the edict's wage–wheat ratios against other periods (optional).
- Compare boxes:
  - debasement vs paper over-issue;
  - primitivism vs modernism;
  - price ceiling vs market price (optional).
- Case: Athens and the Laurion strike of 483 BC, or Diocletian's edict.

## 第 8 章 `ch:qinhan` 先秦与秦汉：轻重之术、盐铁与常平仓 (`zh/ch08_qinhan.tex`)
- Neighbours:
  - Ch 12 (Song–Ming paper money, 称提, "多则贱"; refer forward).
  - Ch 13 (`eq:silver-qty`, Bodin).
  - Ch 14 (`eq:africa-store`, storehouses).
  - Ch 11 (`eq:medieval-seigniorage`).
  - Ch 4 (open-market operations, `sec:money-rate`).
  - Ch 7 (Roman coinage, for one comparison).
- Owns:
  - the 轻重 chapters of 《管子》 on money and prices (币重而万物轻 — quote verbatim with the chapter name);
  - 李悝's 平籴 and 耿寿昌's 常平仓 (both in 《汉书·食货志》);
  - 桑弘羊's 平准、均输 and the salt-and-iron monopolies (《史记·平准书》);
  - the debate of 81 BC (《盐铁论》, 大夫 vs 文学 — give each side's strongest case);
  - free and banned private minting under Wen and Wu (贾谊's memorial; 吴王濞, 邓通);
  - the 五铢 (118 BC) and how many were cast (《汉书·食货志》 gives a total to the reign of Ping — read it with `classical_numerals.py`);
  - Wang Mang's 宝货 system (9–23) and why it failed.
- Promise (FORWARD_REFS row 17, from Ch 12): the 《管子》 轻重 line of thought on the quantity of money and prices.
- When it began: the salt-and-iron debate of 81 BC, or Wang Mang's coinage.
- Sources: corpus 《史记》, 《汉书》 (`史藏/正史`); 《管子》, 《盐铁论》 (add to the checkout); 彭信威 《中国货币史》 (key `pengxinwei`).
  - Note the dating problem of 《管子·轻重》 (probably Western Han, not Guan Zhong's own); give the view and its basis.
- Teaching ideas:
  - **常平仓 as a price band:** buy below a floor, sell above a ceiling; its fiscal cost and the stock it needs, using `eq:africa-store`. Refer back; a keyeq only for the band.
  - **Wang Mang's denominations:** face value against copper weight, i.e. the seigniorage on each coin, using `eq:medieval-seigniorage`. Data from 《汉书·食货志》's list.
- Data: `qinhan_facts` (corpus quotes and numbers).
- Figures: a canvas price-band diagram; Wang Mang's coins, face value vs weight (from the text's list).
- Compare boxes:
  - 常平仓 vs open-market operations;
  - monopoly revenue vs tax;
  - free minting vs state monopoly (optional).
- Case: the salt-and-iron debate.

## 第 9 章 `ch:india` 古代印度与印度洋贸易 (`zh/ch09_india.tex`)
- Neighbours:
  - Ch 5 (`eq:external-bop`; refer back for the accounting).
  - Ch 7 (Roman coinage, the aureus and denarius).
  - Ch 14 (`eq:africa-risk`, `eq:africa-carry`).
  - Ch 13 (silver to China — the later analogue).
  - Ch 16 (bullionist worry).
  - Ch 10 (the Islamic Indian Ocean, later).
- Owns:
  - punch-marked coins;
  - the Arthashastra on the mint, the examiner of coins, prices and interest (date contested — give the range and its basis);
  - the monsoon route and the ports of the Periplus (Barygaza, Muziris);
  - what Rome bought and paid with;
  - Pliny's complaint about the drain of bullion;
  - the Muziris papyrus as one cargo's value;
  - Roman coin finds in South India;
  - how uncertain the totals are.
- Promise (FORWARD_REFS row 27, from Ch 10): the Indian Ocean trade that the Islamic world later joined to the Mediterranean.
- When it began: the first century AD, a ship leaving Egypt for Muziris with the monsoon.
- Sources checked (2026-10-14):
  - archive.org: Schoff 1912 Periplus; the Arthashastra in Shamasastry's translation (find the 1915 edition's identifier).
  - LacusCurtius: Pliny's *Natural History* 12.84 (the 100 million sesterces) and 6.101 (the 50 million to India), Latin; for a public-domain English translation use Bostock & Riley (1855) on archive.org.
  - ZPE: Casson 1990 "New Light on Maritime Loans: P. Vindob. G 40822", *ZPE* 84, 195–206 (uni-koeln.de PDF reachable).
- Candidate scholarship (verify):
  - Rathbone and Morelli on the Muziris papyrus;
  - Turner 1989 *Roman Coins from India*;
  - Scheidel & Friesen 2009 on the size of the Roman economy (to scale Pliny's sum).
- Teaching ideas:
  - **The Arthashastra's rates by risk.** Rates rise from ordinary loans to forest and sea trade (Book 3 ch. 11; verify the numbers and the per-month/per-cent wording). Use `eq:africa-risk` to read the implied chance of loss.
  - **Pliny's sum.** Pliny's 100 million sesterces a year as a share of an estimated Roman GDP: a current-account deficit paid in coin, using `eq:external-bop`. Say what the estimate leaves out (re-exports, customs revenue at 25%, goods sent east).
- Data: `india_facts`.
- Figures:
  - a canvas map-like diagram of the monsoon route (no external basemap);
  - Pliny's sum against estimated GDP, with a range;
  - the rates by risk.
- Compare boxes: bullion outflow vs a modern current-account deficit; punch-marked coin vs struck coin (optional).
- Case: the Muziris papyrus, or the Arikamedu/Muziris finds.
