# Data sources

## In use

| Source | Provider | Link | What it covers | Snapshots | Chapters |
|---|---|---|---|---|---|
| 殆知阁古代文献（daizhigev20） | digital texts of the classical corpus, mirrored on GitHub | https://github.com/garychowcmu/daizhigev20 (commit `4a6d6f2088825f132521d848c2ea86cf9c9a7620`) | 《宋史》《元史》《明史》《宋朝事实》《钦定续文献通考》 | `yuanshi_suyinchao`, `paper_money_facts` (quotations checked verbatim by `fetch/verify_quotes.py`; classical numerals read by `fetch/classical_numerals.py`) | 12 |
| 维基文库《宋史》卷 181 | Wikisource | https://zh.wikisource.org | second witness for the Song quotations; the one variant (1232) is kept as its own row | `paper_money_facts` | 12 |
| Guan, Palma & Wu (2024) | *Economic History Review* 77(4) | https://doi.org/10.1111/ehr.13305 | Yuan note issues and prices, 1260–1368; used to cross-check the 《元史》 table | (cross-check only) | 12 |
| Encyclopaedia Iranica, “ČĀV” (P. Jackson, 1990) | Encyclopaedia Iranica | https://www.iranicaonline.org/articles/cav | the 1294 paper money of the Ilkhanate | `paper_money_facts` (rows `jackson1990`) | 12 |
| Bell, Brooks & Moore (2017) | *Economic History Review* 70(2); accepted manuscript on CentAUR (Reading) | https://doi.org/10.1111/ehr.12374 ; https://centaur.reading.ac.uk/57199/ | exchange and rechange spreads and implied interest rates from the Datini letters, 1383–1411 (Tables 4–5); the 1442 bill; comparable Italian interest rates | `bbm2017_implied_rates`, `medieval_credit_facts` (rows `bell2017`) | 10 |
| Calendar of State Papers, Venice, vol. 2 (ed. R. Brown, 1867) | British History Online | https://www.british-history.ac.uk/cal-state-papers/venice/vol2/p568 | the protest of the 1442 bill of exchange | `medieval_credit_facts` (rows `brown1867`) | 10 |
| Puga & Trefler (NBER WP 18288, 2012; *QJE* 2014) | NBER | https://www.nber.org/papers/w18288 | the Venetian colleganza of 1199 (Figure 2) and its terms | `medieval_credit_facts` (rows `puga2014`) | 10 |
| Princeton Geniza Project, documents 39110, 6039, 2367 | Princeton University | https://geniza.princeton.edu | a traveller's suftajas; Nahray b. Nissim's memorandum; a qirad turned into a fixed-interest loan (Bilbays, 1239) | `medieval_credit_facts` (rows `pgp…`) | 10 |
| Mālik, *al-Muwaṭṭaʾ*, books 31–32 (English translation) | International Islamic University Malaysia | https://www.iium.edu.my/deed/hadith/malik/ | ḥawāla; the rules of qirad | `medieval_credit_facts` (rows `muwatta31`, `muwatta32`) | 10 |
| Qur'an 2:275, 2:279 (Ma Jian) and Luke 6:35 (CUV) | Quran.com API; Wikisource | https://api.quran.com ; https://zh.wikisource.org | the prohibitions of interest | `medieval_credit_facts` | 10 |
| Greif (2012); Edwards & Ogilvie (CWPE 0928, 2009; *EHR* 2012) | Stanford (author's page); Cambridge repository | https://web.stanford.edu/~avner/ ; https://www.repository.cam.ac.uk/handle/1810/229428 | the Maghribi traders debate | `medieval_credit_facts` (rows `greif2012`, `edwards2012`) | 10 |
| Maimbo (2003), World Bank Working Paper 13 | World Bank Open Knowledge Repository | https://openknowledge.worldbank.org/handle/10986/15087 | hawala in Kabul: speed, cost, settlement, enforcement | `medieval_credit_facts` (rows `maimbo2003`) | 10 |
| Leonardo Pisano, *Liber abbaci*, ed. Boncompagni (1857) | archive.org (Google scan, public domain) | https://archive.org/details/bub_gb_w86fLKi88pYC | the prologue, chapter list, a partnership problem, the fairs and voyage problems (read on the page images) | `medieval_credit_facts` (rows `fibonacci1857`) | 10 |

## Planned

These are the sources the chapters are expected to use. For each one, check the current terms of use and the exact series when the chapter is written, and record them in the snapshot's metadata (`README.md`).

| Source | Provider | Link | What it covers | Mainly for chapters |
|---|---|---|---|---|
| FRED | Federal Reserve Bank of St. Louis | https://fred.stlouisfed.org | US macro and financial series | 3, 28, 44–49, 62, 64–74 |
| ALFRED | Federal Reserve Bank of St. Louis | https://alfred.stlouisfed.org | real-time vintages of FRED series | 48, 80, 81 |
| Maddison Project Database | Groningen Growth and Development Centre | https://www.rug.nl/ggdc/historicaldevelopment/maddison/ | long-run GDP per capita and population | 9, 21, 40, 42, 81 |
| Jordà–Schularick–Taylor Macrohistory Database | Jordà, Schularick, Taylor | https://www.macrohistory.net/database/ | advanced economies since 1870: credit, interest rates, asset returns, crises | 23, 28, 62–65, 70 |
| A millennium of macroeconomic data | Bank of England | https://www.bankofengland.co.uk/statistics/research-datasets | UK prices, wages, rates, debt since the Middle Ages | 11, 19, 25, 27 |
| Clio Infra | Clio Infra project | https://clio-infra.eu | historical indicators by country | 21, 24, 41 |
| Global Price and Income History Group | UC Davis | https://gpih.ucdavis.edu | historical prices and wages, including Asia | 11, 13, 17, 21 |
| World Economic Outlook database | IMF | https://www.imf.org/en/Publications/WEO | growth, inflation, fiscal balances, debt, current accounts | 5, 52, 61, 68–79 |
| IMF data portal (IFS, BOP, COFER) | IMF | https://data.imf.org | reserves, balance of payments, currency composition of reserves | 5, 61, 76 |
| World Development Indicators | World Bank | https://databank.worldbank.org/source/world-development-indicators | development indicators | 41, 42, 59 |
| BIS Data Portal | Bank for International Settlements | https://data.bis.org | credit, property prices, exchange rates, policy rates | 62, 65, 72 |
| Measuring the natural rate of interest | Federal Reserve Bank of New York | https://www.newyorkfed.org/research/policy/rstar | Holston–Laubach–Williams estimates and code | 70 |
| ECB Data Portal | European Central Bank | https://data.ecb.europa.eu | euro-area money, rates, balance sheets | 60, 66, 69 |
| World Population Prospects | United Nations | https://population.un.org/wpp/ | population estimates and projections | 79, 84 |
| World hyperinflations table | S. H. Hanke and N. Krus (2013) | (book chapter; verify the published table) | peak monthly inflation of hyperinflations | 26, 52 |
| Reinhart–Rogoff data | C. M. Reinhart and K. S. Rogoff | https://carmenreinhart.com | public debt, defaults and crises over centuries | 13, 51, 61, 68, 83 |
| Chinese monetary history | 彭信威《中国货币史》and specialist studies | (verify edition) | premodern Chinese money, prices and silver | 8, 12, 13, 17 |
| National statistical offices and central banks | e.g. NBS China, Bank of Japan, Banco Central de la República Argentina | — | country chapters and cases | as needed |

Model code published by the original authors (for example the New York Fed's r\* code) is used in preference to re-implementations; see `docs/STYLE.md`.
