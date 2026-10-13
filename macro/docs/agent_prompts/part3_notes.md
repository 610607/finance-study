# Part 3 (第三部分 中世纪与近世): notes for the chapter writers

Chapter 12 is written and approved. The other seven chapters of Part 3 are written as one batch
(docs/WORKFLOW.md). Give each writer `batch_brief.txt` plus its section below. The notes divide
the ground between chapters written in parallel, so that none retells another.

## 第 10 章 `ch:islamic` 伊斯兰世界与地中海的商业革命 (`zh/ch10_islamic.tex`)
- Neighbours: Ch 11 (manors, Black Death, debasement); Ch 15 (Bank of Amsterdam and later banking — refer forward with `\chref{ch:finrevolution}`); Ch 14 (trans-Saharan gold). Ch 4 defines bank balance sheets (`\chref{ch:money}`); Ch 9 the Indian Ocean (`\chref{ch:india}`).
- Owns: paying and financing across distance without shipping metal — suftaja and hawala, partnership contracts (qirad/commenda), credit under the prohibition of interest and how it was redesigned, Genoese, Venetian and Florentine bills of exchange and banking (the Medici network), commercial arithmetic and Fibonacci's *Liber Abaci* (1202).
- Candidate scholarship (verify): Udovitch (1970) *Partnership and Profit in Medieval Islam*; Goitein, *A Mediterranean Society*; Goldberg (2012) *Trade and Institutions in the Medieval Mediterranean*; Greif (1989, 1993) on the Maghribi traders and the critique by Edwards & Ogilvie (2012) — a contested question, present both sides; de Roover (1963) *The Rise and Decline of the Medici Bank*; Sigler (2002), English *Liber Abaci*.
- Teaching ideas: a worked bill of exchange (four parties, two places, an exchange rate that hides interest); commenda profit-sharing versus an interest-bearing loan; a canvas diagram of the bill's flows.
- Compare boxes: bill of exchange vs shipping coin; profit-sharing partnership vs interest-bearing loan. Case: a Geniza merchant's letters, or the Medici network.

## 第 11 章 `ch:medieval` 中世纪欧洲：庄园、黑死病与货币贬值 (`zh/ch11_medieval.tex`)
- Neighbours: Ch 13 uses this chapter's population–land–wage relation for the demographic explanation of the price revolution — label the key equation and figure and list them for the registry. Ch 10 covers bills of exchange and Italian banking. Ch 7 covers Roman debasement (`\chref{ch:greekroman}`); Ch 3 defines real wages and price indices (`\chref{ch:prices}`).
- Owns: the manorial economy; the Malthusian population–land–wage relation applied to the Black Death (1347–1351) and real wages afterwards; why the Statute of Labourers (1351) could not hold wages down; debasement as a fiscal tool (seigniorage, its revenue and costs, e.g. Philip IV of France); Oresme's *De moneta* (c. 1360).
- Model: a Malthusian teaching model (e.g. Cobb–Douglas land and labour, marginal product of labour against population) in NumPy, citing the source of the equations (e.g. Clark 2007 *A Farewell to Alms*, or Ashraf & Galor 2011 — verify), with teaching inputs stated in the text.
- Data: English real wages around the Black Death (Clark 2005 *JPE*; Allen 2001 *EEH*; Munro — verify); French mint revenue or coin silver content (e.g. Sussman 1993 *JEH* — verify).
- Compare boxes: real shock vs monetary shock; seigniorage vs inflation tax. Case: Philip IV's debasements, or Florence after the plague.

## 第 13 章 `ch:silver` 白银的世纪：波托西、马尼拉与价格革命 (`zh/ch13_silver.tex`)
- Neighbours: Ch 12 ends with the Ming turn to silver — pick up there without retelling (`\chref{ch:songming}`; its snapshot already has 《明史》 rows to reuse). Ch 17 owns Qing bimetallism and 19th-century 银贵钱贱. Ch 15 owns Dutch and English public finance — keep Spain as the case and refer forward. Ch 11 builds the Malthusian relation — refer back for the demographic explanation.
- Owns: the Potosí (1545)–Seville–Manila (1571) silver flows and China's demand; the quantity-theory (Bodin 1568) versus demographic explanations of the price revolution; the monetization of taxes by 一条鞭法 and its consequences; Philip II's repeated defaults as "sustainable default".
- Primary texts in the corpus: 明史 食货志, 大明会典, 皇明经世文编. Bodin: a verified edition or translation, quoted briefly.
- Candidate scholarship (verify): Flynn & Giráldez (1995); Drelichman & Voth (2014) *Lending to the Borrower from Hell*; von Glahn (1996, in the bibliography); TePaske (2010) on New World gold and silver output; Hamilton (1934) on prices in Spain.
- Compare boxes: monetary vs demographic explanation of the price revolution; default vs debt restructuring.

## 第 14 章 `ch:africa` 非洲与美洲：黄金、贝币与没有货币的帝国 (`zh/ch14_africa.tex`)
- Neighbours: Ch 13 (Potosí, colonial silver — `\chref{ch:silver}`); Ch 10 (Islamic commercial institutions — `\chref{ch:islamic}`); Ch 6 (temple and palace redistribution — `\chref{ch:mesopotamia}`) for the comparison with Inca storehouses.
- Owns: trans-Saharan gold and Mali (al-ʿUmarī on Mansa Musa's pilgrimage of 1324 and the gold price in Cairo); cowries as a trans-regional currency, their link to the Atlantic slave trade and their later depreciation; the Inca economy run on labour tax (mit'a) and storehouses; Aztec cacao money; when money appears and when it does not.
- Candidate scholarship (verify): Levtzion & Hopkins (eds.), *Corpus of Early Arabic Sources for West African History*; Hogendorn & Johnson (1986) *The Shell Money of the Slave Trade*; Murra on the Inca economy; work on Aztec cacao currency.
- The slave trade: state the human cost and its coercive character plainly.
- Compare boxes: commodity money vs state money; labour tax vs money tax.

## 第 15 章 `ch:finrevolution` 早期金融革命：荷兰、英国与可信的国债 (`zh/ch15_finrevolution.tex`)
- Neighbours: Ch 13 owns Philip II's defaults (compare, refer back); Ch 16 owns Law's System and the South Sea bubble — stop before 1720; Ch 10 owns bills of exchange and Italian banking.
- Owns: the Bank of Amsterdam (1609) and bank money (agio); the VOC (1602) and transferable shares; the Stop of the Exchequer (1672); the Glorious Revolution and North & Weingast (1989) with its critics (e.g. Sussman & Yafeh 2006; Stasavage; Quinn 2001 — verify); the Bank of England (1694) and long-term funded debt; Dutch, English, Spanish and French public finance compared.
- Data: yields on government debt before and after 1688 and the growth of English public debt, only from verified published tables.
- Compare boxes: credible commitment vs forced loans; bank money vs coin. Case: the Bank of Amsterdam.

## 第 16 章 `ch:mercantilism` 重商主义、约翰·劳与重农学派 (`zh/ch16_mercantilism.tex`)
- Neighbours: Ch 15 owns the Bank of England and English debt to 1720; Ch 2 teaches the circular flow (`\chref{ch:accounts}`) — Quesnay's Tableau as the first circular-flow model.
- Owns: Mun (1664) and the balance-of-trade view; Law's System 1716–1720 (Banque Générale/Royale, the Mississippi Company, the debt-for-equity conversion, note expansion, collapse) as a mechanism; the South Sea bubble as comparison; the Cantillon effect (1755); Quesnay's *Tableau économique* (1758).
- Candidate scholarship (verify): Murphy (1997) *John Law*; Velde on Law's System; Neal (1990) *The Rise of Financial Capitalism*; Frehen, Goetzmann & Rouwenhorst (2013, *JFE*); Law (1705) *Money and Trade Considered*.
- Figures: share prices of 1719–1720 if a verified series is available; otherwise verified price points; canvas diagrams of the System's balance sheet and of the Tableau.
- Compare boxes: Law's System vs the South Sea bubble; mercantilists vs physiocrats. Case: Law's System in France.

## 第 17 章 `ch:tokugawa` 德川日本与清代中国：东亚的前现代市场 (`zh/ch17_tokugawa.tex`)
- Neighbours: Ch 12 (Song–Ming paper money) and Ch 13 (Ming silver inflow, 一条鞭法) — refer, do not retell; Ch 15 for the European comparison.
- Owns: the koku system and the three-metal currency (金銀銭三貨制); the Genroku recoinage (1695) and Arai Hakuseki's restoration (1714); the Dōjima rice market (recognized 1730) and its forward trading; the Qing silver–copper dual system and 银贵钱贱 (causes, including the debate over silver outflow); East Asian and European financial institutions compared.
- Primary texts in the corpus: 清史稿 食货志 (钱法); 皇朝经世文编 and sequels (memorials on the silver–copper ratio) — read every memorial in context.
- Japanese material: verified English-language scholarship (e.g. Schaede 1989, *Journal of Banking & Finance*, on Dōjima forwards; Bank of Japan IMES papers on Tokugawa monetary policy). Give kanji and a Chinese explanation for Japanese terms.
- Compare boxes: taxation in rice vs in metal; Dōjima rice bills vs modern futures. Case: the Genroku recoinage or Dōjima.
