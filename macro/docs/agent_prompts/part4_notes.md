# Part 4 (第四部分 古典世界，1750—1914 年): notes for the chapter writers

Parts 1, 2 and 3 and Chapter 1 are written and reviewed, so Part 4 is written against them. Chapters
18–25 are written one at a time in that order (docs/WORKFLOW.md, sequential mode), each reviewed by one
independent reviewer before the next. Give the writer `batch_brief.txt` plus its section below.

Part 4 is the first part about economic theory as it was written. Its evidence is of two kinds:

- **The classics themselves.** Smith, Hume, Thornton, Ricardo, Say, Malthus, Sismondi, Walras, Marx,
  Bagehot, Menger, Knapp, Wicksell and Fisher are public domain in their original language and, for
  most of them, in an old English translation. Quote the text verbatim in a facts snapshot with a
  "sources" block (the Gutenberg or archive.org plain text, as `smith1776` in `merc_facts.json`), so
  that `verify_web_quotes.py` finds every quotation; render it in Chinese in the text, and name the
  edition or translator in the bibitem. Say which edition: later editions of Smith, Malthus and
  Ricardo changed the text. A modern translation still in copyright is quoted only in short phrases.
- **Data.** Historical series already cached or reachable from the shell (probe of 2026-10-14):
  - the Bank of England's *Millennium of Macroeconomic Data* (cached; `boe_millennium_*`), with UK
    prices, Bank Rate, consol yields, money and the exchange rates of the restriction period;
  - Clark's England series (cached; `clark2015_*`);
  - GPIH (Allen's European wages and prices, Chinese wages; cached);
  - the Maddison Project Database (www.rug.nl; CC BY 4.0);
  - the Jordà–Schularick–Taylor Macrohistory Database (www.macrohistory.net; check its licence);
  - the Riksbank's historical monetary statistics of Sweden (www.riksbank.se);
  - MeasuringWorth (check its terms before storing anything);
  - FRASER for US documents (intermittent on 2026-10-14);
  - NBER working papers; JSTOR front pages only.
  
  Blocked: Wiley, Elsevier, Cambridge, Oxford, Chicago journals, the IMF, CEPR, HathiTrust, Gallica,
  the Online Library of Liberty, parliament.uk. A published article behind them may have an NBER,
  central-bank or author's version; say which version is quoted.

Every chapter of this part tells one theory against the crisis or the facts that tested it, gives the
strongest case of each side of its debate (STYLE.md: contested questions), and has at least one case
from outside Britain and the United States. Each chapter section below names the case.

Equations that earlier chapters own are referred back to, not derived again:
- the Fisher relation, `eq:prices-fisher`, and the test of 1896, `sec:prices-test` (Ch 3);
- the quantity equation, `eq:silver-qty` (Ch 13);
- the Malthusian dynamics, `eq:medieval-dynamics` (Ch 11);
- gross seigniorage, `eq:medieval-seigniorage` (Ch 11);
- the balance-of-payments identity, `eq:external-bop` (Ch 5), and the real exchange rate,
  `eq:external-real` (Ch 5);
- the central bank's balance sheet and the money multiplier (Ch 4, `sec:money-*`);
- the sector-balance identity (Ch 2);
- Quesnay's Tableau, `eq:merc-tableau` (Ch 16).

Check the registry for the exact labels before use.

## 第 18 章 `ch:smith` 亚当·斯密：分工、积累与真实票据 (`zh/ch18_smith.tex`)
- Neighbours:
  - Ch 16 owns Mun, Law, Cantillon and Quesnay; this chapter starts from Smith's critique of the mercantile system without retelling it.
  - Ch 15 quotes Smith's digression on the Bank of Amsterdam; refer back.
  - Ch 4 quotes Book II ch. 2 on the colonial paper money; refer back.
  - Ch 6 quotes Book I ch. 4 (barter and the origin of money); refer back.
  - Ch 19 owns the quantity theory and Thornton's critique of the real-bills doctrine; state the critique here, and leave Thornton's full argument to Ch 19.
  - Ch 21 owns the industrial revolution; Ch 40 owns growth theory.
- Owns:
  - the division of labour (the pin factory) and the extent of the market;
  - productive and unproductive labour, capital accumulation and parsimony (Book II ch. 3);
  - the three states of an economy (advancing, stationary, declining: North America, China, Bengal; Book I ch. 8) and wages;
  - Smith's banking: paper money replacing gold and silver (the "waggon-way through the air"), the real-bills rule (Book II ch. 2), and the Ayr Bank (Douglas, Heron & Co.) of 1769–1772;
  - the critique of the mercantile system (Book IV ch. 1, without retelling Ch 16).
- Promises (FORWARD_REFS):
  - row 68, from Ch 15: Smith's views on banks and paper money;
  - row 71, from Ch 16: the critique of the mercantile system, and the real-bills doctrine as an answer to what limits the demand for notes lent on fixed terms;
  - row 87, from Ch 17: Smith asking systematically where the wealth of nations comes from and on what principle banks should lend. Not "the first": Ch 16 covers Cantillon and Quesnay.
- When it began: 1772. The collapse of the Ayr Bank and the credit crisis of June 1772, four years before the *Wealth of Nations*; Smith's own account in Book II ch. 2.
- Sources:
  - Smith (1776): Gutenberg 3300 (cached, a later edition) and the first edition (archive.org, `smith1776ed1`) for passages that later editions changed. Reuse the key `smith1776`.
  - Rockoff (2009), "Upon Daedalian Wings of Paper Money: Adam Smith and the Crisis of 1772", NBER WP 15594 (reachable).
  - Thornton (1802) for the critique of real bills, briefly (archive.org).
  - For the crisis: Hamilton (1956) is in *EHR* (Wiley, blocked); Kosmetatos (2018) is a Palgrave book. Use them only through what can be read.
- Case (outside Britain and the US): Smith's three economies — North America advancing, China stationary, Bengal declining (the famine of 1770 and the East India Company). Give the human cost of the Bengal famine plainly, and what Smith does and does not claim about it.
- Data: England's GDP per head and real wages around 1700–1800 (`boe_millennium_*`, Clark); Smith's own numbers (the pin factory) as teaching inputs read from the text.
- Figures:
  - a canvas diagram of the division of labour and the extent of the market;
  - a canvas balance sheet of a note-issuing bank lending on real bills against one lending on "circulating" bills (the Ayr Bank's drawing and redrawing);
  - a data figure from the snapshots.
- Compare boxes: real bills vs the quantity theory (PLAN); productive vs unproductive labour, or Smith vs Mun on what wealth is.

## 第 19 章 `ch:bullion` 数量论、价格–铸币流动与金块论战 (`zh/ch19_bullion.tex`)
- Neighbours:
  - Ch 13 owns the quantity equation (`eq:silver-qty`) and Bodin; refer back.
  - Ch 23 owns the classical gold standard (1821–1914), the "rules of the game", the Bank Charter Act of 1844 and the lender of last resort. Stop in 1821, and leave 1844 to Ch 23.
  - Ch 5 owns the balance of payments and real exchange rates.
- Owns:
  - Hume's price–specie-flow mechanism (1752) and its assumptions;
  - the equation of exchange as an identity vs the quantity theory as a theory;
  - Thornton's *Paper Credit* (1802): velocity, the real-bills fallacy, the lender of last resort in embryo;
  - the Restriction of 1797–1821, the Bullion Report (1810), Ricardo's *High Price of Bullion* (1810) and the anti-bullionists;
  - resumption in 1821.
- Promises (FORWARD_REFS):
  - row 19, from Ch 12: Hume and the quantity theory;
  - row 40, from Ch 13: Hume's mechanism and the automatic adjustment of the balance of payments. Ch 23 does the gold-standard part.
  - row 70, from Ch 16: the price–specie-flow mechanism;
  - row 114, from Ch 5: under the gold standard a deficit country loses gold, its prices fall and its exports become cheaper, the second route to a real depreciation;
  - row 142, from Ch 9: coin sent abroad leaves less money at home and may lower prices.
- When it began: February 1797. The Order in Council suspending cash payments, after the landing at Fishguard and a run on country banks.
- Sources:
  - Hume, "Of the Balance of Trade" in *Political Discourses* (1752) or a later *Essays* edition (Gutenberg or archive.org).
  - The Bullion Report (1810), e.g. as reprinted in Cannan, *The Paper Pound of 1797–1821* (1919, archive.org).
  - Ricardo (1810).
  - Thornton (1802).
- Data: the Restriction from the BoE millennium dataset: the price of gold, the Hamburg exchange, prices, Bank of England notes. Check which columns exist and their sources.
- Case (outside Britain and the US): a contemporary inconvertible paper money abroad, judged by the same bullionist test. Options:
  - Sweden's paper money of 1745–1776 and its own bullionist debate (Christiernin against the Hats' critics), if the Riksbank's historical statistics and a verifiable text are reachable;
  - Austria's Bancozettel and the Finanzpatent of 1811;
  - Russia's assignats.

  Pick the one whose numbers can be verified.
- Figures:
  - the market price of gold and the exchange against the mint parity, 1797–1821, with prices;
  - a canvas diagram of Hume's mechanism.
- Compare boxes: equation of exchange (identity) vs quantity theory (theory); bullionists vs anti-bullionists.

## 第 20 章 `ch:say` 萨伊定律与普遍过剩之争 (`zh/ch20_say.tex`)
- Neighbours:
  - Ch 2 owns the sector-balance identity and the unplanned-inventory example (`ex:accounts-thrift`).
  - Ch 32 owns Keynes's critique and the multiplier; this chapter only prepares it.
  - Ch 22 owns Marx's crises.
  - Ch 23 owns the panics of 1866 and 1907 and Bagehot; the 1825 crisis belongs here.
- Owns:
  - Say's *Traité* (1803) and the versions of the law (identity vs equilibrium);
  - Ricardo, Malthus, Sismondi and James Mill in the glut debate, 1819–1821;
  - Walras's general equilibrium (1874) and Walras's law, and why Walras's law is not Say's law once money is a good;
  - the place of money (hoarding).
- Promises (FORWARD_REFS):
  - row 90, from Ch 2: what happens after unplanned inventories pile up — Say's law against the paradox of thrift (with Ch 32);
  - row 153, from Ch 1: the main line. Show the claim that general gluts are impossible, the crises that tested it, and why it survived until the Depression (Ch 32 finishes the story).
- When it began: the crisis of 1825–1826 (the Bank of England's near-suspension in December 1825, the country-bank failures).
- Case (outside Britain and the US): the Latin American loans of 1822–1825 and their defaults (Gran Colombia, Peru, Chile, Mexico and others), which were part of the 1825 boom and bust. Use verified sources only (e.g. Marichal 1989 if reachable; the Reinhart–Rogoff default dates; NBER working papers on the 1820s).
- Sources: Say (1803; Prinsep's English translation of the 4th edition, 1821, archive.org), Ricardo (1817; Gutenberg), Malthus (1820; archive.org), Sismondi (1819; archive.org or e-rara), James Mill (1808), Walras (1874; archive.org).
- Data: UK prices and Bank Rate around 1825 (BoE millennium dataset); bank failures if a verified count exists.
- Compare boxes: Say's identity vs Say's equilibrium; Walras's law vs Say's law.

## 第 21 章 `ch:divergence` 工业革命与大分流 (`zh/ch21_divergence.tex`)
- Neighbours:
  - Ch 11 owns the Malthusian model (`eq:medieval-dynamics`); refer back and build the escape on it.
  - Ch 40 owns Solow growth; Ch 41 owns development theory.
  - Ch 17 owns Qing and Tokugawa markets; Ch 13 owns the silver century.
  - Ch 24 owns India's "drain" and the colonial monetary system. This chapter owns Indian cotton textiles (the rise and fall of the Indian industry) as a case of deindustrialization.
- Owns:
  - Malthus (1798) and the stagnation of income per head before 1800;
  - the take-off in Maddison data, with its uncertainty;
  - the explanations: Pomeranz (2000, coal and colonies), Allen (2009, high wages and cheap energy), Mokyr (knowledge, the Industrial Enlightenment), Clark (2007), and institutions (North, Acemoglu–Johnson–Robinson) — each with its evidence and its critics;
  - Britain vs the Yangzi delta (江南).
- Promises (FORWARD_REFS):
  - row 30, from Ch 10: institutional explanations of why Europe took off first;
  - row 34, from Ch 11: how Europe escaped the Malthusian steady state of `eq:medieval-dynamics`.
- When it began: the end of the Malthusian era in England's real wages and GDP per head, around 1800–1830 (Clark; BoE millennium dataset).
- Case (outside Britain and the US): the Yangzi delta, and India's cotton textiles.
- Sources: Malthus (1798, Gutenberg); the Maddison Project Database 2023 (Bolt & van Zanden); Allen's welfare ratios (GPIH; Allen et al. 2011 is in the bibliography); Broadberry et al. (2015) are in the bibliography; Pomeranz (2000) and Mokyr (2009) are books, quoted only through what can be read. Li Bozhong's work on the Yangzi delta, if reachable.
- Data: Maddison GDP per head for Britain, the Netherlands, China, India and Japan; Allen's real wages (London, Beijing/Canton, Delhi); Clark or BoE for England.
- Figures:
  - GDP per head of several economies over 1600–1913 (log scale) with uncertainty marked;
  - real wages in London, Amsterdam, Beijing and Delhi;
  - a canvas diagram of the Malthusian trap and the escape.
- Compare boxes: Malthusian economy vs modern economic growth; high-wage explanation vs resource explanation.

## 第 22 章 `ch:marx` 马克思：积累、危机与再生产图式 (`zh/ch22_marx.tex`)
- Neighbours:
  - Ch 16 owns Quesnay's Tableau (`eq:merc-tableau`); Marx's schemes are built on it — refer back.
  - Ch 2 owns sector accounts.
  - Ch 31 owns Soviet planning and material balances; Ch 63 owns post-Keynesian and MMT views.
  - Ch 20 owns the glut debate.
- Owns:
  - *Capital* vol. 1 (1867): accumulation, the reserve army;
  - vol. 2 (1885): simple and expanded reproduction schemes, and the balance condition between departments;
  - vol. 3 (1894): the tendency of the rate of profit to fall;
  - the readings of Marx's crisis theory: disproportionality (Tugan-Baranovsky), underconsumption (Luxemburg), falling profit rate — each with its strongest case;
  - the influence on Kalecki and on planning balances.
- Promises (FORWARD_REFS): row 79, from Ch 16 — Marx's schemes of reproduction and input–output tables built on the sector accounts.
- When it began: the world crisis of 1857, which Marx followed in his articles for the *New-York Daily Tribune*.
- Case (outside Britain and the US): Hamburg in 1857, the commercial crisis and the Hamburg *Silberdarlehen*. Use verified sources (e.g. Ahrens' or Schubert's work if reachable; contemporary reports).
- Sources:
  - *Capital* vol. 1 (Moore & Aveling translation 1887) and vols. 2–3 (Untermann translations 1907, 1909), public domain (archive.org; marxists.org is reachable but quote from scans or Gutenberg where possible);
  - Marx's *Tribune* articles of 1857 (archive.org or marxists.org);
  - Leontief (1936) only if reachable.
- Teaching: the schemes' numbers (Marx's own: 4000c + 1000v + 1000s in Department I) as a worked example, verified from the text, in NumPy if iterated; the balance condition I(v+s) = II(c) for simple reproduction.
- Compare boxes: reproduction schemes vs input–output table; underconsumption vs falling rate of profit.
- Tone: an economics textbook's account of Marx's theory, its tests and its critics (Böhm-Bawerk 1896 on the transformation problem, briefly); neither advocacy nor dismissal.

## 第 23 章 `ch:goldstandard` 金本位、挤兑与最后贷款人 (`zh/ch23_goldstandard.tex`)
- Neighbours:
  - Ch 19 owns Hume's mechanism and the Restriction; refer back for the mechanism.
  - Ch 24 owns the periphery: India, the silver countries, Meiji Japan, Argentina and Baring 1890.
  - Ch 27 owns the interwar gold standard.
  - Ch 4 owns central-bank balance sheets; Ch 64 owns 2008 lender-of-last-resort operations.
- Owns:
  - the classical gold standard 1821/1870–1914 and its adjustment, the "rules of the game" (Keynes 1925, Bloomfield 1959) and whether central banks followed them;
  - the Currency vs Banking School debate and the Bank Charter Act of 1844 (and its suspensions in 1847, 1857 and 1866);
  - Bagehot (1873) and the lender of last resort, tested in 1866 (Overend, Gurney) and 1907 (the US panic and the Federal Reserve Act of 1913);
  - Menger (1892) vs Knapp (1905) on the origin and nature of money;
  - bimetallism and the gold–silver politics of the 1890s.
- Promises (FORWARD_REFS):
  - row 20, from Ch 12: reserves behind convertible money;
  - row 40, from Ch 13, and row 114, from Ch 5: automatic adjustment under the gold standard;
  - row 56, from Ch 14: Menger against Knapp;
  - row 63, from Ch 15: runs and the lender of last resort (the Bank of Amsterdam's 1672 run is the early version);
  - row 73, from Ch 16: a run stopped by belief (Cantillon on 1720);
  - row 95, from Ch 3: the politics of the gold standard in the 1890s, the bimetallic controversy that Fisher (1896) was written for. Ch 3 refers to `ch:goldstandard` for it, so it is told here, including the 1896 election; Ch 24 refers back.
  - row 135, from Ch 7: how Bagehot's rule differs from Tiberius' loans of AD 33.
- When it began: Black Friday, 11 May 1866, and the suspension of the 1844 Act that night.
- Case (outside Britain and the US): Germany's move to gold in 1871–1873 and the founding of the Reichsbank (1876); or the Banque de France and the crash of the Union Générale in 1882. Pick by verified sources.
- Sources:
  - Bagehot (1873, Gutenberg);
  - the Bank Charter Act 1844 (legislation.gov.uk if reachable);
  - Menger (1892, cached) and Knapp (1924 translation, cached);
  - the Federal Reserve Act (FRASER);
  - Bloomfield (1959, *Monetary Policy under the International Gold Standard*, FRBNY; FRASER or newyorkfed.org).
- Data: Bank Rate and the Bank of England's reserve (BoE millennium dataset); the price level under gold (US, UK); gold production if a verified series exists.
- Compare boxes: Currency School vs Banking School; commodity money vs state money (Menger vs Knapp).

## 第 24 章 `ch:periphery` 第一次全球化中的边缘 (`zh/ch24_periphery.tex`)
- Neighbours:
  - Ch 23 owns the gold standard at the centre and the US silver politics of the 1890s (refer back; do not retell 1896).
  - Ch 17 owns the Qing silver–copper system and 银贵钱贱 up to the mid-nineteenth century.
  - Ch 21 owns Indian cotton textiles and deindustrialization.
  - Ch 61 owns modern emerging-market crises; Ch 76 the currency hierarchy.
- Owns:
  - capital flows, trade and migration in 1870–1914 (Obstfeld & Taylor);
  - Naoroji's "drain" (1901) and its critics;
  - the fall of silver after 1873 and the silver-standard countries (China, India until 1893, Mexico);
  - India's closing of the mints (1893) and the gold-exchange standard (Keynes 1913, *Indian Currency and Finance*);
  - opium, silver and China's money after 1850;
  - Meiji Japan (the Bank of Japan 1882, gold in 1897 with the Chinese indemnity);
  - Argentina and the Baring crisis of 1890.
- Promises (FORWARD_REFS):
  - row 57, from Ch 14: economies whose money is supplied or set from elsewhere, and colonial currencies (the West African pound);
  - row 86, from Ch 17: opium, silver and China's money in the second half of the nineteenth century.
- When it began: 1873, when Germany sold silver for gold, the US stopped coining the silver dollar and the gold price of silver began to fall.
- Sources:
  - Naoroji (1901, archive.org);
  - Keynes (1913) is public domain in many countries but not everywhere; check, and quote briefly;
  - Bank of Japan IMES papers on the Meiji currency (reachable);
  - NBER papers on the first globalization and on Baring (e.g. Mitchener & Weidenmier);
  - Lin (2006) is in the bibliography through a review.
- Data:
  - the gold price of silver 1850–1914;
  - the rupee and the Mexican dollar in sterling;
  - Japanese and Argentine series (JST covers some);
  - capital exports (verify).
- Compare boxes: gold standard at the centre vs at the periphery; gold standard vs silver standard.
- Human costs: the Indian famines of 1876–1878 and 1896–1902, the opium trade. State them plainly with verified numbers or not at all.

## 第 25 章 `ch:wicksell` 维克塞尔与费雪：自然利率与实际利率 (`zh/ch25_wicksell.tex`)
- Neighbours:
  - Ch 3 owns the Fisher relation and Fisher's 1896 test (`sec:prices-fisher`, `sec:prices-test`); refer back, do not retell.
  - Ch 44 owns the natural rate of unemployment.
  - Ch 57 or the new-consensus chapter owns Taylor rules; Ch 70 owns secular stagnation and $r^{*}$ estimates (Laubach–Williams, Holston–Laubach–Williams).
  - Ch 19 owns the quantity theory.
- Owns:
  - Wicksell's *Geldzins und Güterpreise* (1898; Kahn's translation *Interest and Prices*, 1936, in copyright — quote briefly) and "The Influence of the Rate of Interest on Prices" (*Economic Journal*, 1907, public domain);
  - the cumulative process in a pure credit economy, and the natural vs the market rate;
  - Fisher's *Purchasing Power of Money* (1911): the equation of exchange MV + M'V' = PT and the transition period;
  - Gibson's paradox (Gibson 1923; named by Keynes 1930) and its explanations (Fisher's slow adjustment of expectations; Barsky & Summers 1988, NBER);
  - from the natural rate to today's $r^{*}$, as a pointer forward.
- Promises (FORWARD_REFS): row 101, from Ch 3 — what determines the real rate of interest, starting from Fisher and Wicksell, referring back to `sec:prices-fisher` and `sec:prices-test`.
- When it began: Sweden in the 1890s, or the long fall of prices in 1873–1896 and the rise after 1896 under unchanged gold.
- Case (outside Britain and the US): Sweden. The Riksbank's discount rate and Swedish prices under gold (Riksbank historical monetary statistics), and Wicksell's proposal for price-level targeting, which the Riksbank adopted in 1931 (Ch 29 may own 1931 — refer forward).
- Data:
  - UK consol yields and prices 1820–1913 (BoE millennium dataset) for Gibson's paradox;
  - Swedish rates and prices (Riksbank);
  - JST for other countries if the licence allows.
- Teaching: a Wicksellian cumulative process in NumPy (a teaching model with stated inputs, citing the equations' source), and Gibson's correlation recomputed from the snapshot.
- Compare boxes: natural vs market rate; Wicksell's natural rate vs today's $r^{*}$.
