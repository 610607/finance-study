# Chapter 46 (`ch:floating`): the editor's research before the writer starts (2026-11-27)

Collected by the editor before the writer starts (the author, 2026-11-27: “往后继续写两章”; Chapter 45 was finished
before the pause, so nothing was collected while it was written). Downloaded by shell with the User-Agent
"Mozilla/5.0 (X11; Linux x86_64) finance-study quotation check" into the session's scratchpad (`research46/<name>/`),
checked with `file`, read with poppler tools or tesseract (`jpn` is now installed, as well as eng, chi_sim and rus);
nothing is committed. Fetch each document again into your own scratchpad and compare the SHA-256 (HTML pages can
change between fetches: record your own). A colleague's note, not a source: confirm every fact on the document.

## 1. Sources obtained

| suggested key | what | URL | SHA-256 | terms |
|---|---|---|---|---|
| nixon1971 | Nixon, Address to the Nation Outlining a New Economic Policy: “The Challenge of Peace”, 15 August 1971 (The American Presidency Project, from *Public Papers* 1971, pp. 886–891) | https://www.presidency.ucsb.edu/documents/address-the-nation-outlining-new-economic-policy-the-challenge-peace | 0c852759… (HTML) | US government work, public domain; cite the Project as the copy read |
| nixon1971b | Nixon, Remarks Announcing a Monetary Agreement Following a Meeting of the Group of Ten, 18 December 1971 (same project) | https://www.presidency.ucsb.edu/documents/remarks-announcing-monetary-agreement-following-meeting-the-group-ten | 67badd75… (HTML) | public domain |
| frus3 | FRUS 1969–1976, vol. III, Foreign Economic Policy; International Monetary Policy, 1969–1972: documents 164, 165, 168 (editorial notes on 2, 11–12 and 13–15 August 1971), 211 (Connally's telegram from Rome, 30 November 1971), 219 (Azores), 221 (Smithsonian) | https://history.state.gov/historicaldocuments/frus1969-76v03/d168 (and d164, d165, d211, d219, d221) | d168 4f45db83…; d164 62ef5f1b…; d165 c1fbc71b…; d211 df727f5e…; d219 683a9e15…; d221 31e00b82… | public domain (the volume's static PDF answered 403: use the HTML documents) |
| frus31 | FRUS 1969–1976, vol. XXXI, Foreign Economic Policy, 1973–1976: documents 3 (Nixon, Shultz, Burns, 6 February 1973), 12 (editorial note, 12–13 February 1973), 14 (editorial note, March 1973), 16, 33 and 35 (editorial notes on Kissinger and Simon, 14–16 March 1973), 128–129 (Jamaica, January 1976) | https://history.state.gov/historicaldocuments/frus1969-76v31/d12 (and d3, d14, d16, d33, d35, d128, d129) | d12 f090404b…; d14 334310f8…; d33 cd440725…; d35 bc9faa58… | public domain |
| bis1972–bis1976 | BIS, 42nd Annual Report (1 April 1971–31 March 1972), 43rd (1972–73), 44th (1973–74), 46th (1975–76): scans with an OCR text layer (some pages of the 43rd are letter-spaced in the text layer: read those on the page image) | https://www.bis.org/publications/annual-report-1972.pdf, …-1973.pdf, …-1974.pdf, …-1976.pdf | e11de749…; 7e1a4945…; 30201ed3…; ed0cc65f… | the BIS terms (https://www.bis.org/about/terms-conditions, as for Ch 36's `bis36`): limited extracts “provided the BIS is cited as the source”; translations marked as not official, with “the original content can be found at [link]” |
| bisxru, biscpi | BIS Data Portal bulk files: bilateral exchange rates against the US dollar (WS_XRU, monthly averages and end of period; Germany is given in euro: the mark is the value × 1.95583) and long consumer price series (WS_LONG_CPI, monthly indices 2010 = 100) | https://data.bis.org/static/bulk/WS_XRU_csv_flat.zip; https://data.bis.org/static/bulk/WS_LONG_CPI_csv_flat.zip | 8433cfc7…; 45fb4770… (zips change when the BIS updates them: record your own and the download date) | “Terms of permitted use of BIS statistics” (https://data.bis.org/help/legal): “The use of the statistics is unrestricted, provided that: if the statistics are reproduced, the BIS must be cited in your publication or product as the source of the statistics; if the statistics will be translated into another language, a statement must be included … that the translation is not an official BIS translation; …” (copy the whole list verbatim into the snapshot json) |
| dornbusch1976 | R. Dornbusch, “Expectations and Exchange Rate Dynamics”, *JPE* 84(6), 1976, pp. 1161–1176: a JSTOR copy (cover page dated 11/11/2010) on a course page at the University of Wisconsin; text layer good, Greek letters garbled (read the equations on the page images) | https://users.ssc.wisc.edu/~cengel/IMF/DornbuschJPE1976.pdf | f6a4c668b46d0ad1e287c1a23223d46e3432d06b676f5da8672a5adea27f89de | “© 1976 by The University of Chicago. All rights reserved.” Third-party copy: read to verify only, never committed or redistributed (as Ch 42's `krugman1994`); short phrases only |
| meese1981 | R. Meese and K. Rogoff, “Empirical Exchange Rate Models of the Seventies: Are Any Fit to Survive?”, International Finance Discussion Papers No. 184, Board of Governors of the Federal Reserve System, June 1981 (51-page scan, no text layer: OCR with tesseract eng and check on the page images) | https://www.federalreserve.gov/pubs/ifdp/1981/184/ifdp184.pdf (landing page https://www.federalreserve.gov/econres/ifdp/empirical-exchange-rate-models-of-the-seventies-are-any-fit-to-survive.htm) | 4ebe2dbc114887096d073a397f634679a1f11c3c2fe8ec84a1288494bfa8f09f | written by Board staff; the cover note: “References in publications to International Finance Discussion Papers (other than an acknowledgment by a writer that he has had access to unpublished material) should be cleared with the author or authors.” Use the published version (next row) for the results and cite the IFDP only as its earlier version |
| meeserogoff1983 | Meese and Rogoff, “Empirical Exchange Rate Models of the Seventies: Do They Fit Out of Sample?”, *Journal of International Economics* 14 (1983) 3–24: a copy on a course page at the University of Wisconsin (22 pages, text layer letter-spaced in places) | https://users.ssc.wisc.edu/~behansen/390/MeeseRogoff.pdf | a77da74666890db4476b10f11a7e96334ad8009b38ae0fe41304a280102a74f2 | “© 1983 North-Holland”: third-party copy, read to verify only, never committed; short phrases only |
| boj1986 | 日本銀行百年史編纂委員会編『日本銀行百年史』第 6 巻（1986）第 6 章「変動相場制下の金融政策（昭和46年～57年）」1(2)「ニクソン・ショックと円切上げ」（pp. 318–345）and 1(3)「世界的なフロート制移行」（pp. 345–356）: scans without a text layer (OCR with tesseract jpn; quote only from the page image) | https://www.boj.or.jp/about/outline/history/hyakunen/data/hyaku6_6_1_2.pdf; …/hyaku6_6_1_3.pdf (index https://www.boj.or.jp/about/outline/history/hyakunen/hyaku6.htm) | 30673ecb…; a965b68a… | as Ch 35's `boj1985`: the BoJ site terms (https://www.boj.or.jp/en/copyright.htm), source “Bank of Japan”; the history is the Bank's own work: short phrases, otherwise paraphrase |
| epa1972 | 経済企画庁『昭和47年 年次経済報告 新しい福祉社会の建設』（1972 年 8 月 1 日）第 2 章「円切上げの影響」 1 節と 3 節（3）「中小企業輸出産地への影響」 | https://www5.cao.go.jp/keizai3/keizaiwp/wp-je72/wp-je72-00201.html; …/wp-je72-00203.html (目次 wp-je72-000i1.html) | 7dd47e57…; c7471dc1… | the Cabinet Office site terms as recorded for Ch 44's `epa1974` (https://www.cao.go.jp/notice/rule.html; PDL 1.0 style: name the source, mark processed figures) |
| ojc38 | Résolution du Conseil et des représentants des gouvernements des États membres, du 21 mars 1972, relative à l'application de la résolution du 22 mars 1971 … de l'union économique et monétaire, *Journal officiel des Communautés européennes* C 38, 18 avril 1972, pp. 3–4 (French: the OJ had no English edition before 1973) | https://eur-lex.europa.eu/legal-content/FR/TXT/PDF/?uri=OJ:C:1972:038:FULL (TOC https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=OJ:C:1972:038:TOC) | 03bf8797197098e63f2dc9abe8bfcc2b325b9d812972cff0e63456c6e63ceaa2 | EUR-Lex legal notice (https://eur-lex.europa.eu/content/legal-notice/legal-notice.html): reuse of the legal documents under Decision 2011/833/EU, “provided you acknowledge the source”; copy the sentence verbatim. An English translation is on cvce.eu, but its page says “All rights of reproduction … are strictly reserved”: read it only to check your translation, do not cite it as the text |

## 2. Facts read (confirm each on the document)

- **nixon1971**: “this Sunday evening”; Note: “The President spoke at 9 p.m. in the Oval Office”, broadcast live. Three
  targets: “unemployment, inflation, and international speculation”. A 90-day freeze on prices and wages; a 10% job
  development credit; a 10% cut in foreign economic aid. “I have directed Secretary Connally to suspend temporarily
  the convertibility of the dollar into gold or other reserve assets, except in amounts and conditions determined
  to be in the interest of monetary stability and in the best interests of the United States.” “Let me lay to rest
  the bugaboo of what is called devaluation.” “your dollar will be worth just as much tomorrow as it is today.” “In the
  past 7 years, there has been an average of one international monetary crisis every year.” A temporary additional
  tax of 10 percent on imports, “to make certain that American products will not be at a disadvantage because of
  unfair exchange rates”.
- **nixon1971b**: “the most significant monetary agreement in the history of the world”; “Who won, who lost?”; Note:
  5:48 p.m., Commons Room of the Smithsonian; the G-10 met 17–18 December under Connally's chairmanship;
  Switzerland, not an IMF member, represented.
- **frus3 d164**: on 2 August 1971 Connally “outlined forcefully … virtually all the essential elements of the New
  Economic Policy”; tapes “portray Connally as the primary architect”; Connally thought convertibility could not be
  maintained through the 1972 election; Nixon: the State Department not to be consulted. **d165**: “Arthur [Burns] is
  very nervous about this”; Shultz: closing the gold window alone might not bring the change in the exchange rate if
  others intervened; the options of 12 August. **d168**: Camp David, 3:15–7 p.m. on 13 August, continuing to 11:30
  a.m. on 15 August; attendance by the President's Daily Diary (Connally, McCracken, Burns, Volcker, Stein, Peterson,
  Haldeman, Ehrlichman, Shultz, Safire); State and the NSC not represented; Kissinger's memoir quoted (“a decision of
  major foreign policy importance had been taken about which neither the Secretary of State nor the national
  security adviser had been consulted”); Haldeman's notes show “Burns' lonely and unsuccessful attempt to keep the
  gold window open” (the editor's summary of the notes: say so); Stein in 1998: unclear to those present whether
  closing the gold window implied a floating dollar. **d211**: the US package of 29–30 November: an 11% weighted
  appreciation of other OECD currencies, margins of 3%; no change in the gold price presumed. **d221**: Connally's
  press conference: the dollar to depreciate by an average 12%; the gold price to $38; the surcharge lifted; Brandt
  on “some nations” having “ganged up” on the Federal Republic (a report from Bonn: say so).
- **bis1972** (PDF pp. 29–36; printed pp. 24–30): the US official settlements deficit of $9.8 milliard in 1970; the
  Fed's ease against Europe's restraint in 1969–70; the mark's float from 10 May 1971; the crisis “began on the 6th”
  of August with a congressional sub-committee report; $3.7 milliard into other reserves in the week after, $1.7
  milliard of it into Swiss francs; “on Sunday, 15th August, the suspension of convertibility”; markets reopened 23
  August, all European currencies but the French franc floated; Tokyo stayed open, the Bank of Japan absorbed “about
  $4 milliard” and on 28 August let the yen float; the US projection of a $13 milliard required swing against $9
  milliard by the IMF and the OECD; Rome at the end of November; Smithsonian 18 December: dollar devaluation 7.9%,
  gold from $35 to $38; central rates and 2¼% margins; the realignment table (yen +16.9% against the dollar, 308.00;
  mark +13.6%, 3.2225; Swiss franc +13.9%; sterling and French franc +8.6%; lira and krona +7.5%); the par value
  change notified to the IMF on 5 May 1972. The report also gives the political reasons other countries would not
  let their currencies float freely (exporters' opposition, uneven appreciation).
- **bis1973** (PDF pp. 30–31, 142–143): the Swiss franc floats from 23 January 1973; $8 milliard bought by G-10
  authorities in the first seven working days of February, nearly $6 milliard by Germany; a second dollar
  devaluation of 10% announced 13 February (FRUS d12: Shultz announced it on the evening of 12 February); the yen
  and the commercial lira float; markets closed again after 1 March ($2.7 milliard bought by the Bundesbank that
  day); six EEC countries decide on a joint float (ch. I says “on 12th March”, the exchange-market chapter says
  “concluded on 11th March”, FRUS d35 says “the March 11 establishment”: give the discrepancy or use the date the
  sources agree on), the mark revalued by 3%, markets reopen 19 March; the snake in the tunnel from 24 April 1972
  (2¼% between Community currencies inside the 4½% band against the dollar); the UK and Denmark join on 1 May,
  Norway on 23 May; sterling floats on 23 June 1972 (the BoJ history's 1(3) has the same date), Denmark withdraws and rejoins
  on 11 October; Italy withdraws in February 1973; the European Monetary Co-operation Fund (April 1973, operating
  1 June). **bis1974**: France withdrew from the joint float on 21 January 1974. **bis1976**: the franc returned
  in July 1975 (“on 10th July”: check the page image) and left again in March 1976; Jamaica, January 1976: the
  Interim Committee's agreement on quotas and the rules of the system; gold.
- **frus31 d12**: Shultz's statement of 12 February 1973 (10% devaluation; “firm expectation” that the yen will
  float). **d14**: Nixon, 2 March 1973: “there will not be another devaluation”. **d33, d35**: Kissinger to Simon,
  14–15 March 1973: he wants to “prevent a united European position”, “my reason's entirely political”, “create
  conditions in which the Common float is as hard to work as possible” (telephone transcripts summarized and quoted
  in the editorial notes: quote them as FRUS gives them, and say who said what to whom).
- **boj1986 1(2)** (pp. 318–321, 324–326; OCR, check each on the image): Nixon's statement reached Tokyo at 10 a.m.
  on Monday 16 August, after the market had opened; Governor Sasaki and Finance Minister Mizuta announced the parity
  would be kept; the stock market's largest fall on record; the decision to keep the market open was the Finance
  Minister's (the Bank had argued against closing it); Mizuta's two reasons to the Diet on 1–2 September (trade
  invoiced in dollars; confidence in exchange controls); from 16 to 27 August (11 days, Sundays excluded) the
  authorities bought nearly $4 billion, about four months of imports, and reserves rose from under $8 billion to $12
  billion; export prepayments of about $1.8 billion; on the evening of 27 August the Finance Minister announced that
  the margins were suspended provisionally from 28 August; the rate, stuck at 357.37 yen, went to 341.30 on Saturday
  28 August, 341.20 on the 30th, 339 on the 31st (table 1-6); “円は 1 ドル=360円の時代に決別し”; the Ministry's plan
  to announce a redenomination at the same time, which the Bank opposed (later dropped). Note 44 cites Sasaki's own
  later account (エコノミスト編集部編『戦後産業史への証言』4, 1978): he had overrated the effect of revaluation and been
  a little naive about how the international problems would be solved: give it as the history reports it.
- **boj1986 1(3)** (pp. 345–356): the Smithsonian system's two weak points as the history sees them; dollar
  purchases totalling $7.5 billion by February 1973; the yen at 301.90 in late February 1972; the float of
  February 1973 decided because the budget was before the Diet (平価変更が困難); Aichi's statement of 13 February.
- **epa1972** ch. 2 §3(3): small firms' export dependence lower than large firms', but 120 production districts with
  an export ratio over 10% (¥800 billion of exports in 1970, 30% of small firms' exports; export ratio 41.6%, 50.6% of
  it to the United States); the districts kept volumes by cutting yen export prices and passed the cuts down the
  chain: 単価工賃の切下げ, longer hours, homeworkers at the end of the chain. This is the chapter's “who paid” evidence
  for Japan, with the Bank of Japan's intervention.
- **ojc38**: III.1: as a first step towards a Community monetary zone, the central banks to reduce progressively,
  using the margins of the IMF rules, the gap between member currencies, to no more than 2,25 % by 1 July 1972
  (read the French and translate it yourself; mark the translation as the book's).
- **dornbusch1976**: perfect capital mobility (1) $r=r^{*}+x$; expectations (2) $x=\theta(\bar e-e)$; money demand
  (3) $-\lambda r+\phi y=m-p$; (6) $e=\bar e-(1/\lambda\theta)(p-\bar p)$; goods demand (7) and price adjustment (8)
  with speed $\pi$; (10)–(13) the convergence rate $\nu$; consistent expectations require $\theta=\nu$ (Part III);
  the overshooting result $de/dm=1+1/\lambda\theta$ and the variable-output case (Part V). The abstract: “An initial
  overshooting of exchange rates is shown to derive from the differential adjustment speed of markets.” Read every
  equation on the page image (the text layer garbles the Greek letters).
- **meeserogoff1983**: a random walk “performs as well as any estimated model at one to twelve month horizons” for
  the dollar/pound, dollar/mark, dollar/yen and trade-weighted dollar; the structural models (Frenkel–Bilson,
  Dornbusch–Frankel, Hooper–Morton) fail even with realized future explanatory variables; Table 1 RMSE by horizon.
  The IFDP (1981) adds the reasons the authors suggest for instability (“the Lucas critique”, oil supply shocks …).

## 3. Leads and gaps

- Data for the figures and the test: monthly DM/$, yen/$, Swiss franc/$ and £/$ from the BIS (from the 1950s; the
  Fed's H.10 package also has yen, Swiss franc and sterling from January 1971, but not the mark); CPIs from the BIS
  long series. The test the chapter needs: the standard deviation of monthly changes in the log nominal and real
  rates (q = eP^f/P, Ch 5's `eq:external-real`) and in the log relative CPI, 1960–1970 against 1974–1985, computed in
  the check script (the writer's own computation; say so).
- Swiss franc: Rich (2003, Ch 45's `rich2003`) has the 1973 float and the exchange-rate target of October 1978 (the
  mark's franc price “clearly” above 80): Ch 45 left that story here (FORWARD_REFS row from 45).
- Canada floated again on 1 June 1970 (Powell 2005, Ch 37's `powell2005`, check the page).
- Not used: Connally's “our currency, but your problem” is not in any document read here: do not use it unless a
  primary record is found. Volcker and Gyohten (1992), Solomon (1982), James (1996, IMF) not obtained (imf.org answers
  403). JSTOR not tried (bot check). Mussa (1986) and Frankel (1979) are not free.
- Life dates: id.loc.gov (as `loc45`), the DNB/GND through lobid.org, or the NDL authorities (id.ndl.go.jp; probe it
  first) for Mizuta, Sasaki and Aichi.
