# Chapter 43 (`ch:planned`): the editor's research before the writer starts (2026-11-12)

Collected by the editor while Chapter 42 was being written (the author: “可以在前一章写作时收集下一章资料”).
Everything below was downloaded by shell with the User-Agent "Mozilla/5.0 (X11; Linux x86_64) finance-study
quotation check" into the scratchpad of this session (`research43/<name>/`), checked with `file`, and read with
`python3 -I` or poppler tools; nothing is committed. Fetch each document again from its URL into your own
scratchpad directory and compare its SHA-256 (an HTML page may change between fetches: then record your own).
This is a colleague's note, not a source: confirm every fact on the document before you use it.

## 1. Sources obtained

| suggested key | what | URL | SHA-256 | terms read |
|---|---|---|---|---|
| mqy2010 | Xin Meng, Nancy Qian and Pierre Yared, "The Institutional Causes of China's Great Famine, 1959–61", NBER Working Paper 16361, September 2010, 76 pp. (good text layer; `pdftotext` warns about the xref table but reads it) | https://www.nber.org/system/files/working_papers/w16361/w16361.pdf | d6bffc17a1a9cf9c1670a2b9da6cd1e5ec77cbd67be54c327de44ead7607968a | p. [i]: "© 2010 by Xin Meng, Nancy Qian, and Pierre Yared. All rights reserved. Short sections of text, not to exceed two paragraphs, may be quoted without explicit permission provided that full credit, including © notice, is given to the source." (cite the working paper: STYLE.md §3) |
| nbs50 | 国家统计局国民经济综合统计司编《新中国五十年统计资料汇编》，中国统计出版社，1999 年 11 月第 1 版: an excerpt of 5 PDF pages (title page, imprint, part of the contents, table A-1 全国人口状况 1949–1998) scanned with OCR, in a USC library guide. Third-party copy of a copyrighted compilation (the imprint: “中国统计版图书，版权所有，侵权必究”): read to verify the official numbers only, never commit, cite the book | https://scalar.usc.edu/works/chinese-studies-reference-collection/media/HA4631%20.H75%20%E6%96%B0%E4%B8%AD%E5%9B%BD%E4%BA%94%E5%8D%81%E5%B9%B4%E7%BB%9F%E8%AE%A1%E8%B5%84%E6%96%99%E6%B1%87%E7%BC%96_OCR.pdf | bf93d80536dcc4f9ec795af407bc2f579f5b4811d1b46ab39ca20334943c1e71 | see nbsterms for the NBS's own data terms |
| nbs2000 | 国家统计局《中国统计年鉴 2000》表 4-2 人口出生率、死亡率、自然增长率 (selected years only: 1952, 1957, 1962, 1965, 1970, 1975, 1978, 1980, 1985–1999; the famine years are not in it) | https://www.stats.gov.cn/sj/ndsj/zgnj/2000/D02c.htm (GB18030) | d951679cb77899d313d659e1017783ae5679932f1a0d435cf1d2aed8950b37ea | nbsterms |
| nbsterms | 国家统计局网站 服务条款 (2023-02-17 page) | https://www.stats.gov.cn/wzgl/202302/t20230217_1912857.html | (HTML; record your own) | verbatim excerpts: “转载或引用本网内容，务必在显著位置注明转自（或引自）国家统计局网站（或中国统计信息网）字样，并标明本网网址：www.stats.gov.cn。” “三、数据使用 1.用户可以在本网站下载和使用国家统计局发布的统计数据； 2.个人和组织机构应依法使用国家统计局网站发布的统计数据；” and 二.3 “转载或引用本网内容必须是以新闻性或资料性公共免费信息为使用目的的合理、善意引用，不得对本网内容原意进行曲解、修改。” Copy the whole relevant text verbatim into the snapshot json |
| res1981 | 《关于建国以来党的若干历史问题的决议》（一九八一年六月二十七日中国共产党第十一届中央委员会第六次全体会议一致通过）, as printed on 共产党员网 (12371.cn), 2021-11-09, “来源：中国政府网” | https://www.12371.cn/2021/11/09/ARTI1636454249781129.shtml | af0ca3335827187455dc50df4959bfb95db2c8b49811461a9bcb38e010f3f8d2 (HTML; record your own) | site footer “共产党员网 版权所有”; a Party resolution: short quotations, record the edition (find the gov.cn page the site names as its source if you can) |
| kornai1986 | János Kornai, "The Soft Budget Constraint", *Kyklos* 39 (1986), fasc. 1, pp. 3–30: scan without a text layer, on the Kornai estate's site; OCR with `tesseract -l eng` reads well | https://www.kornai-janos.hu/media/konyvek_cikkek/w20825/Kornai1986_The_Soft_budget_Constraint_-_Kyklos.pdf | 84285a1404e2da563819537bfb9879251a1502854197c002bccb756906e51fb1 | in copyright: short phrases; read the site's terms (none found on the home or publications page) |
| kmr2003 | János Kornai, Eric Maskin and Gérard Roland, "Understanding the Soft Budget Constraint", *Journal of Economic Literature* 41(4), December 2003, pp. 1095–1136 (good text layer) | https://www.kornai-janos.hu/media/konyvek_cikkek/w20825/Kornai-Maskin-Roland2003_Understanding_the_SBC_-_JEconLit.pdf | f35e3c314a8533292f259d37cdf93d1b425913d18d7ae08fb3f4865ead4723c6 | AEA journal: short phrases |
| kornai1980 | János Kornai, *Economics of Shortage*, vol. A, Amsterdam: North-Holland, 1980, 317 PDF pages, scan without text (vol. B: …Vol.B.pdf, 101 MB, not downloaded; the Chinese translation 《短缺经济学》 is …Konyvek_0059_Kinai.pdf, 161 MB, and the 1998 edition …0102_Kinai.pdf, not downloaded) | https://www.kornai-janos.hu/media/konyvek_cikkek/w20825/Kornai1980-Economics-of-shortage-Vol.A.pdf | b6729abcb88104a34633b15159eae386a81aec83508a690606c4bac8a1153f7e | in copyright: short phrases. The editor's OCR of vol. A (`tesseract -l eng`, 200 dpi, 114,559 words; its contents list chapters on forced substitution (2.7), queuing, the suction model (ch. 21, with 21.10 “Suction and inflation”) and a mathematical appendix on queuing): OCR to be rerun by the writer, page numbers read on the page images |
| frus1947 | FRUS 1947, vol. IV, doc. 436: telegram 3367, the Chargé in the Soviet Union (Durbrow) to the Secretary of State, Moscow, 14 December 1947, 9 p.m., file 861.5151/12–1447, with the editors' note on decree No. 4004 and decree No. 4005 | https://history.state.gov/historicaldocuments/frus1947v04/d436 | 41a3e7f86f9e90b58881223b284a82e012f9f7a5744a3a1a4fb7ab3bd83b5ef7 (HTML) | US government work, public domain |
| zv1947 | *Заря Востока* (Tbilisi), № 248 (7142), 16 December 1947, 4 pp.: the editorial “Денежная реформа 1947 года” and meetings welcoming the decree (OCR text layer, messy). The decree itself is probably in the issue of 15 December (№ 247): not checked | https://dspace.nplg.gov.ge/bitstream/1234/473867/1/Zaria_Vostoka_1947_N248.pdf | 057d67b13a1dccfc83045959e4f58f80cd8d3788cba5247ba5bcac0e17f69c06 | National Parliamentary Library of Georgia: read the repository's terms; the decree is an official document |
| zv1962 | *Заря Востока* (Tbilisi), № 126, 1 June 1962, 4 pp.: the appeal of the CPSU Central Committee and the Council of Ministers of the USSR to the Soviet people on the price rise (page 1), with “В Совете Министров СССР” (OCR text layer, three columns run together: read the page image) | https://dspace.nplg.gov.ge/bitstream/1234/502639/1/Zaria_Vostoka_1962_N126.pdf | 974f7f76f0558d485701eadbeef3789f1137afb32c991c59f9819398a14583c0 | official document; read the repository's terms |
| smil1999 | Vaclav Smil, "China's great famine: 40 years later", *BMJ* 319 (7225), 18 December 1999, pp. 1619–1621, full text on PubMed Central (PMC1127087) | https://pmc.ncbi.nlm.nih.gov/articles/PMC1127087/ | 13f4895d868e67b1c3cf60f320dff0be70ca800e8ac3490b163a65e7f802953c (HTML) | “Copyright © 1999, British Medical Journal”: short phrases; read the PMC copyright notice |

## 2. Facts read (confirm each on the document)

### China: official series (nbs50, table A-1 全国人口状况, p. 1 of the tables; the OCR puts spaces inside numbers)
- Year-end population (万人): 1957 64,653; 1958 65,994; 1959 67,207; 1960 66,207; 1961 65,859; 1962 67,295; 1963 69,172.
  The population fell by 1,000 万 in 1960 and by 348 万 in 1961 (the book's arithmetic).
- Birth / death / natural growth (‰): 1957 34.03 / 10.80 / 23.23; 1958 29.22 / 11.98 / 17.24; 1959 24.78 / 14.59 / 10.19;
  1960 20.86 / 25.43 / −4.57; 1961 18.02 / 14.24 / 3.78; 1962 37.01 / 10.02 / 26.99; 1963 43.37 / 10.04 / 33.33;
  1965 37.88 / 9.50 / 28.38. Also 1949 36.00 / 20.00 / 16.00 and every year to 1998.
- Cross-check: the 2000 yearbook's table 4-2 (nbs2000) has the same 1952, 1957, 1962, 1965 and 1970 values.
- The A-1 columns 农业/非农业 look swapped in the OCR (1949: 9,441 and 44,726): do not use them without the page image.
- data.stats.gov.cn (the NBS database) answered every query with “403 Forbidden … reason:UrlACL” (a WAF): not used.

### China: Meng, Qian and Yared (mqy2010; printed page numbers, PDF page = printed + 2)
- p. 1: the famine “began in the winter of 1959-60 and lasted until 1961”; it “claimed the lives of between seventeen and
  thirty million people” (their footnote 2 cites Ashton et al. 1984, Banister 1987, Coale 1981, Peng 1987, Yao 1999).
- p. 1: 1959 per capita grain production fell by 15% from 1958; production in 1959 “at least 205% above the amount
  required to avoid mortality”; regions with higher per capita production in 1959 had higher famine mortality, “a
  surprising reversal of a typically negative correlation”.
- p. 7 fn. 13: in 1959 about 4.3 million tons exported to the USSR, about 2.3% of production.
- p. 7: about 80% of the population worked in agriculture; grain for industrialization (43% of government spending in
  the 1950s, citing Eckstein 1977); private plots about 5% of land, 83% of pigs and poultry in 1957 (citing Spence).
- p. 8: by 1959 93% of agricultural land under high-level collectivization; private plots abolished; communal kitchens;
  livestock halved 1957–58 (citing Becker).
- p. 9: 1959 grain fell 15%; about 38% of production procured in October–November 1959 (citing Li and Yang 2005); with
  4% growth it would have been 32%, against 26% in 1958; most deaths in January–February 1960 (citing Becker).
- p. 9: “The Chinese government has claimed that the famine was a result of bad weather and low production in 1959”;
  weather explains “at most 14-50%” (citing Li and Yang 2005, Kueh 1995); other causes in the literature: labour and
  acreage diverted, communal dining, commune incentives, the denial of the right to exit (Lin 1990).
- p. 9 fn. 18: mortality almost 22 per 1,000 in 1960, about 10 at the 1950s low, 11–13 in 1958–59.
- p. 10 fn. 19: Li and Yang's retention after procurement 223 kg per person in 1959 and 212 in 1960.
- p. 17 (PDF p. 19): 1,870 calories a day = 190 kg of grain a year (365 × 1870 / 3587); 804 calories = 82 kg; in 1959 production
  exceeded the 48 million tons needed to stay alive by 99 million tons.
- Appendix Table A8 (PDF p. 71; from Li and Yang 2005; “Original Sources: Ministry of Agriculture (1989). Sample of 24 provinces.”):
  production (Mt) / procurement (Mt) / % / retained kg per agricultural labourer: 1957 195 / 46 / 23.59% / 273;
  1958 200 / 52 / 26.00% / 268; 1959 170 / 64 / 37.65% / 193; 1960 143 / 47 / 32.87% / 182; 1961 148 / 37 / 25.00% / 209;
  1962 160 / 32 / 20.00% / 229. Frame these as Li and Yang's figures as MQY reprint them.
- Appendix Table A3 (PDF p. 66; 27 provinces, their sum): production 1958 169.04, 1959 147.58, 1960 126.87, 1961 122.14 Mt.
  (Two different samples: say which one a number comes from.)
- Table 1 (PDF p. 54; stylized example, three regions): subsistence 100; region A produces 225 (prob. 0.8) or 180 (0.2), B 150 or
  120; expected 216 and 144; procurement fixed at expected production minus 120; consumption in the low state 84 and 96.
  A worked example can follow its mechanism with the book's own teaching inputs (credit the model to MQY).

### China: the official verdict (res1981)
- Adopted 27 June 1981 by the Sixth Plenum of the 11th Central Committee.
- “……就在总路线提出后轻率地发动了“大跃进”运动和农村人民公社化运动，使得以高指标、瞎指挥、浮夸风和“共产风”为主要标志的左倾错误严重地泛滥开来。”
- “庐山会议后期，毛泽东同志错误地发动了对彭德怀同志的批判，进而在全党错误地开展了“反右倾”斗争。”
- “主要由于“大跃进”和“反右倾”的错误，加上当时的自然灾害和苏联政府背信弃义地撕毁合同，我国国民经济在一九五九年到一九六一年发生严重困难，国家和人民遭到重大损失。”
- “一九六〇年冬，党中央和毛泽东同志开始纠正农村工作中的左倾错误，并且决定对国民经济实行“调整、巩固、充实、提高”的方针”.
- The resolution gives no death toll (the book can say so, as an observation on the text).

### China: Smil (smil1999)
- “between the spring of 1959 and the end of 1961 some 30 million Chinese starved to death and about the same number of
  births were lost or postponed”; first calculations by American demographers 16.5–23 million, later studies 23–30
  million, “unpublished Chinese materials hint at totals closer to 40 million”; the official figures for the famine
  years “greatly underestimate both the fall in fertility and the rise in mortality”; drought a contributory factor,
  “largely a manmade catastrophe for which Mao Zedong bears the greatest responsibility”. (Smil's own judgments: frame as his.)

### Soft budget constraint (kornai1986, kmr2003)
- Kornai 1986, p. 3: the budget constraint becomes “soft” in many economies, “conspicuously apparent in socialist
  systems”, associated with “the paternalistic role of the State”; he introduced the concept in *Economics of Shortage*
  (1980) and an expository paper (1979). Sections III–IV: observations in Hungary, Yugoslavia and China.
- KMR 2003, pp. 1108–1111: the Dewatripont–Maskin (1995) model. Set-up cost 1; a good project (prob. a) returns R_g, B_g;
  a poor one returns nothing in period 1 and can be liquidated (R_L, B_L) or refinanced at a further cost of 1 (R_p, B_p).
  The centre refinances if R_p + B_p + E_p − 1 > R_L + B_L (their (1), an ex post criterion: the first 1 is sunk); the
  project is inefficient if 1 > R_p + B_p + E_p − 1 (their (2), ex ante). If both hold, poor projects are refinanced
  though they would not have been financed had their type been known: “a soft budget constraint equilibrium”. A
  manager submits a poor project if s B_p + (1 − s) B_L ≥ 0. Examples they give: Nowa Huta in Poland in the 1970s, the
  Eurotunnel. A good `eq:planned-…` with a worked example on teaching inputs.

### The USSR, December 1947 (frus1947)
- Telegram of 14 December 1947, 9 p.m.: decree announced by radio at 6 p.m.; cash exchanged 10 old for 1 new; bank savings
  1 for 1 up to 3,000 rubles, 3 for 2 on the next 7,000, 2 for 1 above; state loans converted 3 to 1 (1938 loan 5 to 1, 1947
  loan not converted); ration cards abolished; bread and flour 12% and macaroni and grits 10% below the ration price; the
  embassy's comment that the decree “Expropriates 90 percent of all cash holdings” and will “hit peasants hardest”
  (the embassy's reading, framed as such). The editors' note names decree No. 4004 (Council of Ministers and the
  Central Committee, 14 December) and No. 4005 (procedures).
- This keeps Ch 35's promise (FORWARD_REFS l.270) together with `eq:reconstruction-overhang`: the cash exchange is the
  “货币改革” cure of Ch 35's equation, the derationing the price side.

### The USSR, 1 June 1962 (zv1962; OCR, confirm on the page image)
- The appeal: procurement prices of cattle, pigs, sheep, goats and poultry raised “в среднем на 35 процентов”; retail prices of
  meat and meat products raised “в среднем на 30 процентов” and of butter “в среднем на 25 процентов”; at the same time some
  retail prices cut (sugar on average 5%; rayon staple goods: read the figures on the page).
- The appeal's own words: price rises are “мера нежелательная”; “это мера временная”; it gives the cost of producing meat
  against the procurement price (e.g. a centner of beef: cost 91.6 rubles in 1960 and 88 in 1961 against a procurement price
  of 59.1, as the OCR reads it) and says retail prices of meat and butter had been set too low “без достаточных экономических
  обоснований”. A good document for the guide question: the state raising prices openly, and saying why.

## 3. Leads not yet followed (verify before use)
- Novocherkassk (1–2 June 1962; 26
  dead is the usual figure, unverified): the Supreme Soviet of the RSFSR/RF documents of May 1992 (Ведомости СНД и ВС
  РФ 1992 № 21, as pravo.ru reports), the KGB and prosecutors' reports published in *Исторический архив* (1993);
  the OSA Archivum blog (legacy.osaarchivum.org) for a list of sources; the toll and the decisions need an official or archival source.
- Kosygin reform: the resolution of the CPSU Central Committee and the Council of Ministers of 4 October 1965 «О
  совершенствовании планирования и усилении экономического стимулирования промышленного производства»; the plenum of
  27–29 September 1965 (Kosygin's report of 27 September; an English translation “On Improving Industrial Management”
  on soviethistory.msu.edu: read its terms); the USSR law of 2 October 1965 on the industrial ministries (pravo.by,
  Belarus legal-history pages); Zaria Vostoka 1965 № 229 and № 232 (dspace.nplg.gov.ge).
- CIA reports (public domain, mirrored on archive.org): “The Food Situation in Communist China” (RR EM 62-3, 1962),
  “Food in Communist China” (1961), “Statistics on Communist China's population, birth and death rates …” (1959): what
  outsiders knew at the time, if the chapter wants it.
- Kornai, *Economics of Shortage*: chapters on forced substitution, queues and “suction”; the Chinese translation
  《短缺经济学》 on the same site.
- Not obtained: Coale (1984), *Rapid Population Change in China, 1952–1982* (National Academy Press): the PDF needs an
  e-mail address and the reader's page images are not served to a script (the editor's attempt to fetch them was
  stopped as circumvention: do not try); Lin (1990, JPE), Kung and Lin (2003, EDCC), Li and Yang (2005, JPE), Ward (1958,
  AER), Portes and Winter (1980, REStud): publishers answer 403 and JSTOR has a bot check. Use them only through those
  who report them (MQY, KMR, Smil), framed so.
- Probed 2026-11-12 (see the notes section for the list): data.stats.gov.cn's database blocks queries (WAF); www.nap.edu
  needs an e-mail for the PDF.

## 4. Added while Chapter 42 was reviewed (2026-11-12)

| suggested key | what | URL | SHA-256 | terms read |
|---|---|---|---|---|
| lenkom1962 | Информационная сводка сектора информации отдела партийных органов Ленинградского горкома КПСС № 75, 1 June 1962, «Отклики трудящихся на повышение закупочных и розничных цен на мясо и животное масло», to the gorkom secretary G. I. Popov; archive reference on the page: ЦГАИПД СПб. Ф. Р-25. Оп. 89. Д. 65. Л. 155–160 (source line: vk.com/cgaipdspb), published by the project «Исторические Материалы» | https://istmat.org/node/69040 | ed83c491f4ce50e53d63beb0e892c7891e7cdac9b9299f5c7bfe796a60b1fe8a (HTML; record your own) | site footer: “Вся информация на сайте, если не указано другое, предоставляется на условиях лицензии Creative Commons BY-SA 4.0”; the document is an archival record of the Party: short quotations, cite the archive reference and the publication |
| zv1965 | *Заря Востока* (Tbilisi), № 232 (12468), Friday 1 October 1965, 4 pp.: page 1 prints the resolution of the CC plenum of 29 September 1965 «Об улучшении управления промышленностью, совершенствовании планирования и усилении экономического стимулирования промышленного производства» (and the plenum's resolution calling the XXIII Congress for 29 March 1966); OCR text layer with spaces inside words: read the page images (`tesseract -l rus`) | https://dspace.nplg.gov.ge/bitstream/1234/506362/1/Zaria_Vostoka_1965_N232.pdf (item: https://dspace.nplg.gov.ge/handle/1234/506362; dc.date.issued 1965-10-01; dc.rights.holder the National Parliamentary Library of Georgia) | 7bf9a70b2e7143e8f35684a860104348dd2d056b756e5c3bbfe5b17d64668338 | as zv1962 |
| yusuf1977 | Shahid Yusuf, *Understanding Self-Management in Yugoslavia*, World Bank Domestic Finance Studies No. 44, November 1977, 80 pp. (foreword by V. V. Bhatt); text layer usable | https://documents.worldbank.org/curated/en/532061468915640475/pdf/Understanding-self-management-in-Yugoslavia.pdf | 8cd3d8fa600e7b0062292a9e9b4868b3954c4738fa7461a51af7898c85408877 | copy the rights statement from the document's landing page on documents.worldbank.org |
| wb1978yu | World Bank, *Yugoslavia: Self-Management Socialism and the Challenges of Development*, Report No. 1615a-YU, Volume I, Part 1 “An Economic System in Evolution”, 21 March 1978 (Europe, Middle East and North Africa Region; the cover still carries the restricted-distribution notice, the copy is marked “Public Disclosure Authorized”); text layer messy in places | https://documents.worldbank.org/curated/en/134111468101968175/pdf/multi0page.pdf | 7785580cfce85dafea9edf7e490d796e99d9ceae86638a9c589907fae33a6dd3 | as yusuf1977 |
| ardalan1980 | Cyrus Ardalan, “Workers' Self-Management and Planning: The Yugoslav Case”, *World Development* 8 (1980), pp. 623–638, World Bank Reprint Series No. 161 (“Reprinted with permission”; © Pergamon Press 1980): the 1974 constitution and the 1976 planning law | https://documents.worldbank.org/curated/en/398751468308357118/pdf/REP161000Worke00the0Yugoslavia0case.pdf | a0f207d7c2dc03139dc1627c2d7330098cc44628077f7b0bc81e88fa056bd468 | journal article: short phrases |

Facts read (confirm on the document):

- lenkom1962: the report says the resolution was adopted on 17 May and announced only on 31 May (“почему постановление было принято I7 мая с.г., а объявили его лишь 3I мая”); it lists approving remarks (“эта мера временная”; “лишь бы не было войны”) and, under “Имеются и такие высказывания”, critical ones (aid to other countries; “Почему Н.С. Хрущев … за 8 лет не выправил положение с сельским хозяйством?”); two staff of SKB-170 (Kronstadt) asked for a trade-union meeting to propose other ways (cutting the apparatus and the government dachas), which the Party bureau refused (“в профсоюзном собрании товарищам было отказано”); a turner at Lenpishchemash would not start work until “talked to”. What the Party recorded, not an opinion poll: say so.
- zv1965 (plenum resolution of 29 September 1965, page 1): the plenum found that “превалировали административные методы в ущерб экономическим”, that khozraschet was “во многом формальный”, that enterprises were regulated by “большим числом плановых показателей”; the remedy: cut the number of plan indicators set from above and use “прибыль, цена, премия, кредит”; ministries by branch replace the sovnarkhozy (the remarks of Tbilisi workers printed in the same issue); the plan keeps central control of investment, prices, wages and finance (“единую политику в области планирования главных направлений развития производства, технического прогресса, капитальных вложений, цен, оплаты труда и финансов”: OCR, confirm the wording). The joint CC–Council of Ministers resolution of 4 October 1965 was not found in issues № 239–240 (9–10 October): not read.
- wb1978yu (Vol. I, Part 1, paras. 1.7–1.8, 1.19–1.21, 1.30–1.31): GMP growth 7.2% a year in 1954–1974; population growth 1.1% a year; per-capita income US$1,480 by 1975; domestic savings about 30% of GDP “in earlier years”; real personal incomes in the social sector +5.8% a year; social-sector employment +3.7% a year; the private-agriculture share of the labour force 66% → 33% (1953–1975); after the 1965 reforms “high and rising rates of inflation”, wages rising more easily than falling, cost mark-up pricing; emigration liberalized in 1965 and “virtually as important as the social sector in absorbing labor”; open unemployment rising by the early 1970s. Currency: 12.5 dinars per US dollar before 23 January 1971; floating since 12 July 1973.
- yusuf1977 (pp. 16–17 of the typescript): reports Ward (1958, 1967) as a model in which income maximization by the members discourages investment, and its critics (Vanek 1971, Furubotn and Pejovich 1970; Horvat: “under-investment was never a problem”). This is Yusuf's summary of Ward, not Ward's text; it does not state the short-run supply result usually attributed to Ward (output falls when the price rises). Ward (1958), *AER* 48(4), September 1958, “The Firm in Illyria: Market Syndicalism” (Yusuf's bibliography gives the volume and month): not read (JSTOR). If the chapter teaches the Illyrian firm, derive it as the book's own model and say whose model it is in a clause; do not attribute a result to Ward's text that no source read states.
- Novocherkassk (1–2 June 1962): no official or archival source obtained (the CIA reading room answered “Access Denied”: not retried; alexanderyakovlev.org blocked; rusarchives.ru, doc.histrf.ru and pravo.gov.ru did not answer). Without one, a clause at most, without a death toll.
