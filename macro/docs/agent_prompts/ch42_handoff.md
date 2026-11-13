# Chapter 42 (`ch:eastasia`): hand-off note (work paused 2026-11-06)

> Saved into the repository by the editor on 2026-11-06, when the author asked to save the work and pause (“先保存已有工作并暂停”). The scratchpad paths below (`S/…`) belonged to that session and are gone: fetch each document again from its URL (into a new scratchpad directory, checked with `file`) and compare its SHA-256 with the table before using it. The writer's brief is saved beside this note as `ch42_writer_brief.txt`; the notes for the chapter are the section “第 42 章” of `part6_notes.md`.

State of the repository: nothing edited, nothing committed. `git status` on branch
`claude/adoring-dirac-hgq2or` was clean when the work stopped. All the work so far is reading and downloads in
this scratchpad (`/tmp/claude-0/-home-user-finance-study/09f5dc87-4665-5290-8ae8-96469f4e0747/scratchpad/writer42/`,
written `S/` below). Downloads are untrusted data: none is committed, and no script that came with one was run.
All downloads used the User-Agent "Mozilla/5.0 (X11; Linux x86_64) finance-study quotation check".

## 0. What was read before stopping

The read-first list is done: the brief `editor42/writer42_brief.txt`, `docs/agent_prompts/batch_brief.txt`,
`part6_notes.md` in full (including the section "第 42 章" and every "Carried over" section for Ch 35–41), the
Part 5 carried-over rules (Ch 26–34), STYLE.md, NARRATIVE.md, POLISH.md §3–§4, write_template.txt,
`zh/ch41_development.tex` in full, the structure of `checks/check_ch41.py` (said/say/told, READINGS,
MISPRINTS, TRANSLATIONS/KEYWORDS, LIVES/AGREE/EVENTS/LATER, witnesses, counts, coverage, anchors),
`checks/common.py`, `data/README.md`, `data/fetch/verify_web_quotes.py` (formats: pdf/html/json/txt/image only, no
xlsx), and `data/fetch/solow40.py` (how the PWT workbook is read). Also read: the stub of Ch 42 and the stubs of
Ch 43, 46, 47, 56, 58, 61, 72, 78 and 79; the PLAN entry for Ch 42; and the five FORWARD_REFS rows pointing to
42, with the passages they come from.
- FORWARD_REFS rows to 42 (all still open): line 183 (Ch 21, Malthus on China's cheap labour and manufactures
  for foreign sale, `zh/ch21_divergence.tex` l.39 and l.368); l.269 (Ch 35, high growth after the Korean War
  procurement, `ch35` l.255 ends “日本此后的高速增长，在\chref{ch:eastasia}。”); l.297 (Ch 39, case box, the
  1956–1973 average of about 9.2% real GDE growth, saving peak 23.2% in 1974 and 1976, `ch39` l.281–287); l.303
  (Ch 40 `sec:solow-legacy` l.320 and l.324: Krugman 1994 as Easterly and Fischer report it; the nine
  economies over 4% a year per head in 1960–2019 on PWT 10.01, including Taiwan, Korea, Singapore and Hong Kong);
  l.310 (Ch 41 compare box and third debate: the World Bank's strongly outward oriented Hong Kong, Korea and
  Singapore in 1963–1985, and causality).
- The question to hand over at the end (Ch 43's stub, copy exactly): “计划经济里的“通胀”藏在哪里？”
- Ch 41 ends with Ch 42's question, which is also the stub's guide question:
  “日本和东亚“四小龙”的高速增长，是生产率的奇迹，还是要素积累的结果？”. Its last paragraph ends with “下一章讲的是最早转向出口的那几个经济体。”.
- Labels to use (they exist): `eq:solow-accounting` (g_Y = α g_K + (1−α) g_L + g_A), `eq:solow-speed`,
  `eq:solow-steady`, `tab:solow-convergence`, `fig:solow_convergence`, `sec:solow-legacy`, `sec:consumption-check`,
  `fig:consumption_japan`, `sec:reconstruction-japan`, `ex:reconstruction-yen`, `tab:development-paths`,
  `sec:development-isi`, `sec:development-debate`.
- Bib keys that already exist and can be reused: `pwt1001` (in Ch 40's block; adding a note "第 42 章用…" to it is a
  shared-file edit, so ask the editor), `ef1995` (Easterly and Fischer 1995, already in the web cache),
  `esri68`, `esri2024` (the ESRI series used in Ch 39), `wdr1987`, `mpd2023`, `boltvanzanden2024`.

## 1. Sources obtained (downloaded by shell on 2026-11-06)

| key (suggested) | what | URL | file in scratchpad | SHA-256 |
|---|---|---|---|---|
| wb1993 | World Bank, *The East Asian Miracle: Economic Growth and Public Policy*, Policy Research Report, Oxford University Press for the World Bank, 1993; Report No. 12351, main report, 402 PDF pages (scan with an OCR text layer, often with the spaces between words missing) | https://documents.worldbank.org/curated/en/975081468244550798/pdf/multi-page.pdf (found with the API search.worldbank.org/api/v2/wds) | `S/wb1993/multi-page.pdf` (text `S/wb1993/wb.txt`, pdftotext -layout) | d29b62c4721f11da5b5b5093a89bc640fdb6f159376136c60b13fc9532557257 |
| wbnews1993 | World Bank, Bank News Release No. 93/S17, "East Asia's economic 'miracle' could be repeated in other countries, new study shows", Washington, Sunday, September 26, 1993 (embargo 4 p.m. EDT), 6 PDF pages, with a background note | https://documents.worldbank.org/curated/en/495771624970707489/pdf/Announcement-that-East-Asias-Dramatic-Economic-Growth-Could-be-Repeated-in-Other-Countries-on-September-26-1993.pdf | `S/wb1993ann/ann.pdf` (text `ann.txt`) | 6c66c1a70fc118da60037268e9d8d25bf8c90e6fc518f35b2c73f5a28fe7063d |
| young1994 | Alwyn Young, "The Tyranny of Numbers: Confronting the Statistical Realities of the East Asian Growth Experience", NBER Working Paper 4680, March 1994 (42 PDF pages; good text layer) | https://www.nber.org/system/files/working_papers/w4680/w4680.pdf | `S/w4680/w4680.pdf` (text `w.txt`) | 1806bcdae7f1011aecf01c702cf674779efcad3da5395e51d4ded25440861984 |
| young1992 | Alwyn Young, "A Tale of Two Cities: Factor Accumulation and Technical Change in Hong Kong and Singapore", in O. J. Blanchard and S. Fischer (eds), *NBER Macroeconomics Annual 1992*, vol. 7, MIT Press, pp. 13–64 (the NBER selection PDF, 52 pages; text layer good, some words run together) | https://www.nber.org/system/files/chapters/c10990/c10990.pdf | `S/c10990/c10990.pdf` (text `c.txt`) | d7cb151d12169f228b5fd847b6b9c0876773fc9a97d370863fa76de246ecc474 |
| rodrik1994 | Dani Rodrik, "Getting Interventions Right: How South Korea and Taiwan Grew Rich", NBER Working Paper 4964, December 1994 (78 PDF pages). **The text layer is unusable (mirrored or garbled OCR)**; the page images are clear. Rows from it must be page-image rows (`format` image, with a transcription in the note) | https://www.nber.org/system/files/working_papers/w4964/w4964.pdf | `S/w4964/w4964.pdf`; renders `pg-01..04.png`, `hi-01.png`, `hi1b.png` | a39fae4fd41301c51aecc4da17d081e5fb02a7d761ae48aba0a4391bf9749d48 |
| collinsbosworth1996 | Susan M. Collins and Barry P. Bosworth, "Economic Growth in East Asia: Accumulation versus Assimilation", *Brookings Papers on Economic Activity* 1996(2): 135ff. (with the discussion; 69 PDF pages; the first page's text layer is readable). **Not read yet**: neither the tables nor the Brookings copyright page | https://www.brookings.edu/wp-content/uploads/1997/06/1996b_bpea_collins_bosworth_rodrik.pdf | `S/cb1996/cb1996.pdf` | e4442a10fb224d481a81de0ad3bfa277b4d44de2596647a3fab8943349aece52 |
| krugman1994 (copy A) | Paul Krugman, "The Myth of Asia's Miracle", *Foreign Affairs* 73(6), Nov.–Dec. 1994, pp. 62–78: a JSTOR-derived copy (17 pages) on a Hanover College course page. Third-party copy: read to verify only, never commit, cite the journal, short phrases. **Not read yet** | https://vault.hanover.edu/%7Eeiriksson/classes/214/files/MythOfAsiasMiraclePaulKrugman.pdf | `S/krugman_hanover/krugman_hanover.pdf` | c6fcb3fb85ad5fa52747e912cd45e078161b053cadf677ea234db19d15414ca8 |
| krugman1994 (copy B) | The same article: a JSTOR download with its cover page ("Published by: Council on Foreign Relations", "Stable URL: https://www.jstor.org/stable/20046929"), 18 pages, on cooperative-individualism.org. Third-party copy, same rules. **Not read yet** | https://cooperative-individualism.org/krugman-paul_the-myth-of-asia's-miracle-1994-dec.pdf | `S/krugman_ci/krugman_ci.pdf` | dd1314f2c11b47dee826bd7645122480e452d333ace3602761960249ac6b8e51 |
| (not Hsieh) | The search result named as a copy of Hsieh (2002) is **only a one-page biography** of Chang-Tai Hsieh, not the paper. Useless | https://www.sem.tsinghua.edu.cn/__local/1/D4/EF/951F46C306230C12DE143E53494_CEFC2D1C_16150.pdf?e=.pdf | `S/hsieh_tsinghua/hsieh_tsinghua.pdf` | d2631f5f2d7c3e3c06846f371f7da3a559a07447b0d9cfcca4cf624ff756d693 |

Already in caches (not downloaded again): the PWT 10.01 workbook (`~/.cache/finance-study/web/pwt1001_xlsx…`,
SHA-256 bf2b66c5…, CC BY 4.0, cite Feenstra, Inklaar and Timmer 2015: see `data/snapshots/pwt1001_usa.json` for the
exact licence wording); Maddison 2023 (`~/.cache/finance-study/maddison2023/mpd2023_web.xlsx`); Easterly and
Fischer (1995) (key `ef1995` in the web cache); the ESRI tables of Ch 39 (snapshot
`esri_household_saving_1955_2024`, with its terms already copied verbatim in bib items `esri68`/`esri2024`).

### Licence and terms read so far (verbatim where copied)
- Rodrik WP 4964, PDF p. 1 (read on the page image): "© 1994 by Dani Rodrik. All rights reserved. Short sections
  of text, not to exceed two paragraphs, may be quoted without explicit permission provided that full credit,
  including © notice, is given to the source." The same page has: "Paper presented at the 20th Panel Meeting of
  *Economic Policy* on 21-22 October 1994."
- Young WP 4680, PDF p. 1 (page image looked at): **no © notice** on the cover page. The abstract page was not
  checked for one. Record it as "prints no © notice" only after checking p. 2 as well; the work is in copyright,
  so use short phrases only.
- Young 1992, NBER selection: the cover page says "This PDF is a selection from an out-of-print volume from the
  National Bureau of Economic Research". No © line in the text layer of the selection; the volume's own copyright
  page is not in the selection. In copyright: short phrases only.
- World Bank 1993 main report: the copyright page (PDF p. 5) is OCR-garbled in the text layer and **must be read on
  the page image** before copying the rights statement (it is a © 1993 IBRD/World Bank page, published by Oxford
  University Press, with an all-rights-reserved clause, judging from the garbled text). The foreword (PDF p. 8)
  says "the judgments made herein do not necessarily reflect the view of its Board of Directors or the
  governments they represent" (as it reads after the OCR is corrected).
- Press release 93/S17: no rights statement seen; the pages carry "Public Disclosure Authorized" stamps.
- Collins–Bosworth (Brookings) and the two Krugman copies: terms not read yet. Copy B has the JSTOR cover page;
  read JSTOR's notice on it. Brookings: read the BPEA copyright page and record it, as the brief requires.

## 2. Not obtained or not tried yet

- **Hsieh (2002, AER 92(3): 502–526) or a working-paper version**: not found. The AEA full text is restricted and
  pubs.aeaweb.org answered 403 in the probe. A Scribd copy exists (provenance unclear; not tried). Next steps:
  an NBER or Princeton/Berkeley working-paper version, or his 1999 AER P&P paper "Productivity Growth and Factor
  Prices in East Asia". If nothing opens, give the dual approach only as a derivation of the book's own, and
  report Hsieh as not obtained.
- **Westphal (1990, JEP 4(3))**: not tried. aeaweb.org answers, but the PDFs on pubs.aeaweb.org answered 403.
- **Not tried yet**: the Economic White Paper of July 1956 (年次経済報告 昭和31年, "もはや「戦後」ではない", on
  www5.cao.go.jp: read the site's terms first); the income-doubling plan (国民所得倍増計画, cabinet decision
  1960-12-27, on worldjpn.net: read the database's terms); Nelson and Pack, World Bank PRWP 1881 (1998-02-28,
  "The Asian miracle and modern growth theory", listed by the WB API without a pdfurl: fetch its documents page);
  Kim and Lau (1994); the CPF's own pages (www.cpf.gov.sg); Bank of Japan, IMES or Ministry of Finance sources on
  the Temporary Interest Rate Adjustment Law of 1947 and window guidance; a source for martial law in Taiwan
  (1949–1987); a primary source for the coup of May 1961 in Korea (try the World Bank report's Appendix 3.1
  "Economic and Political Timelines", printed p. 148); the authority records (id.loc.gov MADS/RDF JSON and
  lobid.org GND JSON, as `loc41`/`gnd41` do) for Ikeda Hayato, Park Chung-hee, Lewis T. Preston and anyone else
  named with dates.
- Johnson (1982), Amsden (1989) and Wade (1990) are books in copyright and were not looked for. Report them through
  those who cite them (e.g. the World Bank report), framed as such.
- Not to be tried: www.jstor.org (bot check), FRED/ALFRED, the Kobe 近世経済データベース, and the gitignored
  fgr2009 CSV.

## 3. Facts verified so far (read in the text layer or on page images; none is in a snapshot yet)

Every quotation must still be put in a facts CSV and checked with `verify_web_quotes.py`. The WB report's text
layer has words run together (e.g. "ofjapan", "researchprogram"), so a quotation must copy that text exactly or
become a page-image row named in MISPRINTS.

**World Bank news release 93/S17 (wbnews1993)**, p. 1: "SUNDAY, SEPTEMBER 26, 1993"; "EMBARGO: NOT FOR BROADCAST
OR PUBLICATION UNTIL 4 P.M. EDT (20.00 GMT)"; headline "EAST ASIA'S ECONOMIC "MIRACLE" COULD BE REPEATED IN OTHER
COUNTRIES, NEW STUDY SHOWS"; "The dramatic growth of East Asian economies during the past three decades has
lifted millions of people out of poverty"; the eight economies "Hong Kong, Indonesia, Japan, Malaysia, Republic
of Korea, Singapore, Taiwan and Thailand" (the OCR prints "economieq" and "Thailand.."); "Since 1960, these
economies have grown twice as fast as the rest of East Asia, three times as fast as Latin America and South Asia,
and five times as fast as sub-Saharan Africa"; "the only economies in the world that have achieved rapid
sustained growth while reducing the gap between the rich and poor"; "John Page, the leader of a research team";
"policy fundamentals". P. 2: "Previous bank studies have described these "policy interventions" -- for example,
suppressing interest rates or promoting favored industries -- as always harmful to growth."; "export push";
"Of the many interventions tried in East Asia, those associated with export push hold the most promise for other
developing economies"; Page: "Government intervention in the economy always carries a risk that vested interests
will shape policies to their own advantage".

**World Bank 1993 main report (wb1993)**, PDF page = printed page + 15 in the Overview (PDF p. 16 = p. 1):
- Foreword (PDF pp. 6–8, printed v–vii; signed "Lewis T. Preston, President, The World Bank", dated August 1993,
  printed "Augur 1993" in the OCR). Preston announced the study at the 1991 Annual Meetings of the Board of
  Governors in Bangkok. "most of East Asia's extraordinary growth is due to superior accumulation of physical and
  human capital" (OCR: "superior accumulation of physical and human capita."). These economies were also better
  able than most to allocate resources to highly productive investments and to acquire and master technology:
  "In this sense there is nothing 'miraculous'". "no single 'East Asian model'". "market-friendly economic
  policies". "in some economies, mainly those in Northeast Asia, some selective interventions contributed to
  growth", with three prerequisites ("economic contests"). The support of the Government of Japan for the
  research programme "is gratefully acknowledged" (PDF p. 8, OCR "ofjapan").
- The Research Team (PDF p. 11, printed xi): led by John Page (team: Birdsall, Campos, Corden, Chang-Shik Kim,
  Howard Pack, Sabot, Joseph E. Stiglitz, Uy; major contributions by Cassen, William Easterly, Lawrence, Petri,
  Lant Pritchett). "The work was initiated by Lawrence H. Summers and was carried out under the general direction
  of Nancy Birdsall."
- Acknowledgments (PDF p. 12, xiii): "The financial assistance of the Government of Japan is gratefully
  acknowledged." Also a project on the Japanese main bank system and civil service, and one on the effectiveness
  of credit policies in East Asia (Yoon-Je Cho and Dimitri Vittas).
- Definitions (PDF p. 14): the HPAEs are "led by Japan"; the Four Tigers are Hong Kong, the Republic of Korea,
  Singapore, and "Taiwan, China"; the NIEs are Indonesia, Malaysia and Thailand. Write 台湾 in the text (STYLE §3)
  and keep the source's wording in the snapshot.
- Overview (PDF p. 16, printed p. 1): "From 1965 to 1990 the twenty-three economies of East Asia grew faster than
  all other regions of the world". The footnote on China: "Recently China, particularly southern China, has
  recorded remarkably high growth rates using policies that in some ways resemble those of the HPAEs. This very
  significant development is beyond the scope of our study, mainly because China's ownership structure, methods
  of corporate and civil governance, and reliance on markets are so different from the those of the HPAEs" (the
  OCR has "vtay", "seruc-. ure"; read the page image). **This is the planned bridge to Ch 43.**
- Contents (PDF pp. 9–10): Ch. 1 "Rapid Productivity Growth" p. 46, Appendix 1.1 "Accounting for Growth" p. 60;
  Ch. 3 Appendix 3.1 "Economic and Political Timelines" p. 148; Ch. 5 "Explaining East Asia's High Savings Rates"
  p. 203 and Appendix 5.2 on interest rates and growth p. 245; Ch. 6 "Assisting the Market: Financial Markets
  and Allocation" p. 273, "Using the International Trade and Industrial Policy" p. 292, Appendix 6.1 "Testing the
  Impact of Industrial Policy on Productivity Change" p. 326. **None of these chapters has been read yet**; they
  should give the Bank's TFP table, its "mild financial repression" and real deposit rates, its industrial-policy
  verdict, the CPF and the political timelines.

**Young (1994), NBER WP 4680 (young1994)**, cover dated March 1994:
- Cover p. 1: "Special appreciation is due the government of Singapore which, while disagreeing with most of my
  analysis and all of my conclusions, has generously supplied me with both published and unpublished data on the
  Singaporean economy." (a voice quotation: keep it short, the clause "while disagreeing with most of my analysis
  and all of my conclusions").
- Abstract (p. 2): output per capita growth "averaged 6% to 7% per annum over the past two and a half decades";
  output per effective worker in the non-agricultural sector "only 3% to 4% per annum"; "the doubling, tripling
  and even quadrupling of the investment to GDP ratio"; "While the growth of output and manufacturing exports in
  the newly industrializing economies of East Asia is virtually unprecedented, the growth of total factor
  productivity in these economies is not."
- p. 1: "This is a fairly boring and tedious paper, and is intentionally so." Footnote 1: growth rates are
  logarithmic; the labour force of Korea and Taiwan excludes their armies.
- p. 2: rising participation removes 1% a year from Hong Kong's per capita growth, 1.2% and 1.3% from Korea and
  Taiwan, "a stunning 2.6% per annum (for 24 years!)" from Singapore's. Singapore's constant-price I/GDP: 11% in
  1960, 38% by 1980, 47% by 1984. Korea: about 5% in the early 1950s, 20% in the mid-60s, 30% in the early 1980s,
  approaching 40% by 1991. Taiwan: about 10% in the early 1950s, a high of 27% in 1975, then about 20%.
- Hong Kong text, p. 15: TFP "averaging 2.3% over the 1966-1991 period"; the exception 1981–86, during the
  Anglo-Chinese negotiations. Table 3-1 (p. 16), 66-91: output 0.073, weighted capital 0.080, weighted labour
  0.032, TFP 0.023, labour share 0.628.
- Singapore text, p. 17: "the total factor productivity residual for the aggregate economy averages an
  extraordinary -0.3% per annum over a twenty-four year period, a virtually unprecedented record of productivity
  regress" (the OCR prints "extraordinaiy"); output per effective worker growth 9.2% (late 1960s), 2.7% (1970s),
  .2% (1980s). Footnote 21: the TFP estimates "are likely to be overestimates". Table 4-1 (p. 18), 66-90:
  output 0.085, weighted capital 0.115, weighted labour 0.057, TFP −0.003, labour share 0.470.
- p. 32: NIC productivity growth "ranges from a low of -0.3% in Singapore to a high of 2.3% in Hong Kong";
  "Although, with the possible exception of Singapore, productivity growth in the NICs is not particularly low,
  it is also, by post-war standards, not particularly high." Footnote: Lau and Kim (1992) find productivity growth
  in the NICs in the 1970s and 1980s "not significantly different from zero".
- Table 8-1 (p. 33), economy-wide TFP growth: Hong Kong (1966–1991) 2.3, Singapore (1966–1990) −0.3, South Korea
  (1966–1990) 1.6, Taiwan (1966–1990) 1.9 (Korea and Taiwan excluding agriculture). Manufacturing: −1.0, 2.9,
  1.5. Table 8-2 (p. 33): Japan 1952–1973 4.1; US 1947–1973 1.4; Germany 1950–1973 3.7; France 3.0; Italy 3.4;
  UK 1.9; Canada 1.8; Netherlands 2.5; Brazil 1950–1980 2.0; Mexico 1940–1980 1.7 (developed economies from
  Christensen, Cummings and Jorgenson 1980, the others from Elias 1990, printed "Elms" in the OCR).
- Caution: these are the working-paper figures. The QJE 1995 version may differ: cite the version read
  (STYLE §3) and say so in the 史料说明.

**Young (1992), NBER Macroeconomics Annual (young1992)**, pp. 13–64:
- p. 14: GDP per capita of Hong Kong and Singapore "was quite close in 1960". The Hong Kong government "has
  emphasized a policy of laissez faire", while the Singaporean government has pursued capital accumulation "via
  forced national saving and the solicitation of a veritable deluge of foreign investment". Singapore's I/GDP rose
  "from 9% in 1960 to a high of 43% in 1984"; Hong Kong's fluctuated around some 20% (p. 15; constant
  international prices, Summers–Heston Mark V, n. 4). Footnote 2: Mark V gives 1960–85 per capita growth of 6.09%
  (Hong Kong) and 6.03% (Singapore) a year.
- p. 16: TFP growth's "contribution to growth in Singapore is next to nil"; Singapore as "a victim of its own
  targeting policies".
- p. 22, the CPF: established in 1955; the contribution rate at first 5% of the employee's salary with a matching
  5% from the employer; 15%/15% by 1975; "by 1984 to a rather impressive 25% apiece"; members have "a limited
  ability to withdraw their balances, even upon retirement"; as of 1980, 95.1% of the Fund was invested in
  government securities; at its peak in 1985, CPF contributions were "14.9% of GNP, or 36% of gross national
  savings". Footnote 30: in 1986 the employer's rate was cut to 10%; as of 1989, 15% (employer) and 23% (employee).
- pp. 22–23, labour (who paid): the labour legislation of 1968 made promotion, transfer, recruitment, retirement,
  dismissal and the allocation of duties "nonnegotiable managerial prerogatives"; disputes went to compulsory
  arbitration at the Industrial Arbitration Court; man-days lost in stoppages fell from some 40,000 a year in the
  mid-1960s to nil (in all but 2 years) in 1978–1990.
- Table 5 (p. 35): over 1971–90, TFP contributed 35% of Hong Kong's output growth (the text adds that 56% of the
  rise in output per worker came from TFP); over 1970–90 it contributed −8% of Singapore's output growth, and
  capital accumulation explains 117% of the rise in output per worker (pp. 35–36). Table 6 is on p. 36 and the
  annual Singapore Table 7 on p. 37 (average TFP −0.004). Footnote 76: the Singapore estimates were revised after
  computational errors were removed and the Singaporean government supplied more data, which lowered TFP growth.
- The published discussion (around text lines 2215–2231 of `c.txt`) contains a discussant's recomputation
  (Singapore's TFP higher than Hong Kong's in some periods). **Not read**: identify the discussant before using it.

**Rodrik (1994), NBER WP 4964 (rodrik1994)**, read on page images:
- PDF p. 2, abstract: "it is difficult to see how export orientation could have played a significant causal role
  in these countries' growth"; the measured rise in the relative profitability of exports in the 1960s "is too
  insignificant"; "exports were initially too small"; "A more plausible story focuses on the investment boom";
  "The outward orientation of the economy was the result of the increase in demand for imported capital goods."
- PDF p. 3, introduction: in 1960 South Korea "was poorer than many sub-Saharan African countries, and Taiwan
  not all that much richer"; average increases in per-capita income "of 6.8 and 6.2 percent"; the orthodox story
  (import substitution in the 1950s, the "easy stage" exhausted, the cut in US aid, unified exchange rates and
  devaluations, duty-free imported inputs for exporters, higher interest rates; exports "took off in the
  mid-1960s").

## 4. The plan (nothing written yet)

- **Opening** (a dated document with a gap between what it says and what it shows): Sunday 26 September 1993. The
  World Bank releases *The East Asian Miracle*: "could be repeated in other countries", with John Page as team
  leader. In the foreword (August 1993), President Lewis T. Preston writes that most of the growth is due to
  superior accumulation of physical and human capital, and that in this sense there is "nothing 'miraculous'"; the
  Government of Japan paid for the research. Pick up Ch 41's last line (the economies that turned to exports
  first). End the opening with the guide question.
- **Sections** (planned; aim for 8,000–9,000 characters of main text):
  1. 当时的世界: Japan 1955–1973, told on from Ch 35 in a clause (Dodge Line, 360 yen, the procurement boom).
     Sources to get: the 1956 White Paper and the doubling plan of 27 December 1960 (its target and the outcome
     against ESRI growth from Ch 39's snapshot, about 9.2%). MITI and the Ministry of Finance as those who chose
     the industries and steered credit, through sources that can be had.
  2. The four (Korea, Taiwan, Hong Kong, Singapore), who decided and who paid: Park's military government from May
     1961 (find a source); Taiwan under martial law (find a source); Hong Kong's laissez faire against Singapore's
     forced saving through the CPF (Young 1992: 5%/5% → 25%/25%, 14.9% of GNP), the 1968 labour law and
     compulsory arbitration.
  3. Theory: growth accounting with human capital, g_Y = α g_K + (1−α)(g_L + g_h) + g_A (from
     `eq:solow-accounting`); the dual approach from Y = rK + wL (TFP = share-weighted growth of r and w); the Solow
     transition (`eq:solow-speed`, Krugman's argument as reported). Planned labels: `eq:eastasia-accounting`,
     `eq:eastasia-dual`.
  4. Data check: the book's own PWT 10.01 calculation (rgdpna, rnna, emp, hc, labsh; JPN, KOR, TWN, HKG, SGP,
     with USA as a benchmark) for Young's periods (1966–1990/91), set beside Young's Table 8-1 and Collins–Bosworth.
     Singapore against Hong Kong.
  5. Financial repression: a deposit-rate ceiling below inflation as a transfer from savers to borrowers (a worked
     example with the World Bank's real deposit rates, if Ch. 5 or 6 gives them).
  6. Four debates, each ending open ("至今没有定论。"): accumulation or productivity (Young/Krugman against the
     Bank's foreword and Hsieh, if obtained); industrial policy (the Bank's mixed verdict and its critics); exports
     or investment first (Rodrik against the outward-orientation reading of Ch 41's groups); financial repression
     (a clause each pointing to Ch 58 and Ch 61).
  7. 史料说明 (deeper box), 今天还剩什么, takeaways, self-check and answers.
- **Boxes**: compare 要素积累 vs 生产率增长 (Young/Krugman against the Bank/Hsieh, in their own words); compare
  产业政策 vs 市场 (if the material earns it); a case box (Singapore · 1955—1990 · 中央公积金 and Young's TFP, or
  Japan); a pitfall box (a low TFP does not mean a failure, or primal and dual measure different things); the
  deeper box 史料说明.
- **Examples**: (1) growth accounting with Young's Singapore and Hong Kong numbers (Table 3-1, Table 4-1);
  (2) the dual approach with teaching inputs; (3) financial repression with teaching inputs or the Bank's rates;
  (4) a Solow transition with a rising investment share.
- **Figures** (`figsrc/fig_ch42.py`): `eastasia_levels` (GDP per head relative to the US from PWT rgdpe/pop, log
  scale; Hong Kong and Singapore start in 1960 in PWT, so Maddison 2023 is the alternative, which needs an
  `mpd42src` bib item listing each economy's original sources); `eastasia_accounting` (the book's PWT
  decomposition beside Young's numbers); `eastasia_investment` (PWT csh_i over time, at current PPPs: say so).
- **Data snapshots planned**: `eastasia_facts` (quotations: CSV + JSON with "sources", columns as
  development_facts); `pwt1001_eastasia` (read from the cached workbook by a new `data/fetch/eastasia42.py`,
  modelled on `solow40.py`, with PWT's own flags i_outlier/i_xr kept).
- **Ending**: back to September 1993. The Bank left China out because its ownership structure and reliance on
  markets were "so different" (Overview, footnote). East Asia controlled the price of money, while the planned
  economies controlled all prices. Then hand over “计划经济里的“通胀”藏在哪里？” exactly.

## 5. Notes for the next writer

- The WB report's OCR layer is poor. Several facts (copyright page, China footnote, Appendix 3.1, any table) need
  the page images. Name each OCR misreading in MISPRINTS, as Ch 41 did.
- Rodrik's PDF has no usable text layer: every row from it is a page-image row (`format` image, transcription
  between « and » in the note), checked by eye by the reviewer. `pdftoppm -r 110 -f N -l N -png` works.
- No OCR tool is installed (no tesseract, no PyMuPDF); `pdftoppm`, `pdftotext` and `pdfimages` are available.
- Young's figures are logarithmic growth rates (WP n. 1), and his labour shares differ by economy (Hong Kong about
  0.63, Singapore about 0.47): an example built on them must use his own shares.
- The coordinator's rules: 台湾、香港 with no prefix; 中国大陆 only where it must be told apart in the same list;
  Ch 43 owns the planned economies, Ch 58 Japan's bubble, Ch 61 the 1997–98 crisis (one clause each).
- Do not edit the `pwt1001` bib item (Ch 40's block) or other shared files: ask the editor.
- No personal data was sent anywhere. All downloads are in the scratchpad only.
