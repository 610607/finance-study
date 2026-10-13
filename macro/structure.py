"""Registry of Volume 1: parts, books (分册) and chapters.

This file is the single list that build.py, validate_source.py and tools/check_chapter.py read.
Keep it in step with main_zh.tex and the chapter files: validate_source.py checks that the
chapter order, file names, labels and Chinese titles agree.
"""

TITLE_ZH = "宏观经济学：从古代货币到当下争论"
TITLE_EN = "Macroeconomics: From Ancient Money to Present Debates"
SERIES_ZH = "金融学习丛书 · 第一卷"
SERIES_EN = "Finance Study Series, Volume 1"

# (number, key, Chinese title, English title, period, first chapter, last chapter)
PARTS = [
    (1, 'language', '宏观的语言', 'The language of macroeconomics', '', 1, 5),
    (2, 'ancient', '古代世界', 'The ancient world', '公元前 3000 年—公元 600 年', 6, 9),
    (3, 'earlymodern', '中世纪与近世', 'The medieval and early modern world', '600—1750 年', 10, 17),
    (4, 'classical', '古典世界', 'The classical world', '1750—1914 年', 18, 25),
    (5, 'keynes', '战争、萧条与凯恩斯革命', 'War, depression and the Keynesian revolution', '1914—1945 年', 26, 34),
    (6, 'goldenage', '战后黄金时代：东方与西方', 'The postwar golden age: East and West', '1945—1970 年', 35, 43),
    (7, 'stagflation', '滞胀与预期革命', 'Stagflation and the expectations revolution', '1968—1985 年', 44, 52),
    (8, 'moderation', '大缓和、新共识与转轨', 'The Great Moderation, the new consensus and transition', '1982—2007 年', 53, 63),
    (9, 'aftercrisis', '金融危机之后', 'After the financial crisis', '2008—2019 年', 64, 72),
    (10, 'present', '疫情通胀与当下', 'Pandemic inflation and the present', '2020—2026 年', 73, 79),
    (11, 'synthesis', '综合与展望', 'Synthesis and outlook', '', 80, 84),
]

# (number, Chinese title, English title, parts)
BOOKS = [
    (1, '宏观的语言与前现代世界', 'The language of macroeconomics and the premodern world', (1, 2, 3)),
    (2, '古典与凯恩斯时代', 'The classical and Keynesian eras', (4, 5)),
    (3, '战后与滞胀', 'The postwar era and stagflation', (6, 7)),
    (4, '大缓和与金融危机', 'The Great Moderation and the financial crisis', (8, 9)),
    (5, '当下、综合与展望', 'The present, synthesis and outlook', (10, 11)),
]

# (number, slug, Chinese title, English title); file zh/chNN_slug.tex, label ch:slug
CHAPTERS = [
    (1, 'intro', '一个问题引出整门课', 'A question that leads to the whole course'),
    (2, 'accounts', '国民核算与恒等式', 'National accounts and identities'),
    (3, 'prices', '价格、通胀与利率', 'Prices, inflation and interest rates'),
    (4, 'money', '货币、银行与央行的资产负债表', "Money, banks and the central bank's balance sheet"),
    (5, 'external', '国际收支与汇率', 'The balance of payments and exchange rates'),
    (6, 'mesopotamia', '美索不达米亚与埃及：神庙、宫廷与记账', 'Mesopotamia and Egypt: temples, palaces and accounts'),
    (7, 'greekroman', '希腊与罗马：铸币、城邦财政与帝国的贬值', 'Greece and Rome: coinage, civic finance and imperial debasement'),
    (8, 'qinhan', '先秦与秦汉：轻重之术、盐铁与常平仓', 'Early China: the qingzhong arts, salt and iron, and the ever-normal granary'),
    (9, 'india', '古代印度与印度洋贸易', 'Ancient India and the Indian Ocean trade'),
    (10, 'islamic', '伊斯兰世界与地中海的商业革命', 'The Islamic world and the Mediterranean commercial revolution'),
    (11, 'medieval', '中世纪欧洲：庄园、黑死病与货币贬值', 'Medieval Europe: manors, the Black Death and debasement'),
    (12, 'songming', '宋元明：世界最早的纸币及其崩溃', 'Song, Yuan and Ming: the first paper money and its collapse'),
    (13, 'silver', '白银的世纪：波托西、马尼拉与价格革命', 'The silver century: Potosí, Manila and the price revolution'),
    (14, 'africa', '非洲与美洲：黄金、贝币与没有货币的帝国', 'Africa and the Americas: gold, cowries and an empire without money'),
    (15, 'finrevolution', '早期金融革命：荷兰、英国与可信的国债', 'The early financial revolution: Holland, England and credible public debt'),
    (16, 'mercantilism', '重商主义、约翰·劳与重农学派', 'Mercantilism, John Law and the physiocrats'),
    (17, 'tokugawa', '德川日本与清代中国：东亚的前现代市场', 'Tokugawa Japan and Qing China: premodern East Asian markets'),
    (18, 'smith', '亚当·斯密：分工、积累与真实票据', 'Adam Smith: division of labour, accumulation and real bills'),
    (19, 'bullion', '数量论、价格–铸币流动与金块论战', 'The quantity theory, price–specie flow and the bullion controversy'),
    (20, 'say', '萨伊定律与普遍过剩之争', "Say's law and the general glut controversy"),
    (21, 'divergence', '工业革命与大分流', 'The industrial revolution and the great divergence'),
    (22, 'marx', '马克思：积累、危机与再生产图式', 'Marx: accumulation, crises and reproduction schemes'),
    (23, 'goldstandard', '金本位、挤兑与最后贷款人', 'The gold standard, bank runs and the lender of last resort'),
    (24, 'periphery', '第一次全球化中的边缘', 'The periphery in the first globalization'),
    (25, 'wicksell', '维克塞尔与费雪：自然利率与实际利率', 'Wicksell and Fisher: the natural and the real rate of interest'),
    (26, 'weimar', '一战、赔款与魏玛恶性通胀', 'War, reparations and the Weimar hyperinflation'),
    (27, 'interwar', '两次大战之间的金本位', 'The interwar gold standard'),
    (28, 'depressionus', '大萧条：美国', 'The Great Depression in the United States'),
    (29, 'depressionworld', '大萧条：世界与“金色枷锁”', 'The Great Depression worldwide: golden fetters'),
    (30, 'alternatives', '1930 年代的另类出路：纳粹德国、高桥财政与瑞典', "Other ways out in the 1930s: Nazi Germany, Takahashi's Japan and Sweden"),
    (31, 'soviet', '苏联工业化与社会主义核算论战', 'Soviet industrialization and the socialist calculation debate'),
    (32, 'generaltheory', '凯恩斯《通论》', "Keynes's General Theory"),
    (33, 'islm', 'IS–LM：把凯恩斯写成方程', 'IS–LM: Keynes as a system of equations'),
    (34, 'warfinance', '战争财政、功能财政与布雷顿森林的设计', 'War finance, functional finance and the design of Bretton Woods'),
    (35, 'reconstruction', '战后重建：马歇尔计划、德国货币改革与道奇路线', 'Reconstruction: the Marshall Plan, German currency reform and the Dodge Line'),
    (36, 'brettonwoods', '布雷顿森林体系的运行', 'Bretton Woods in operation'),
    (37, 'mundell', '蒙代尔–弗莱明与最优货币区', 'Mundell–Fleming and optimum currency areas'),
    (38, 'phillips', '菲利普斯曲线与宏观计量模型', 'The Phillips curve and macroeconometric models'),
    (39, 'consumption', '消费与投资理论', 'Theories of consumption and investment'),
    (40, 'solow', '索洛增长模型', 'The Solow growth model'),
    (41, 'development', '发展经济学：二元经济、进口替代与大推进', 'Development economics: dual economies, import substitution and the big push'),
    (42, 'eastasia', '东亚奇迹：日本高速增长与发展型国家', "The East Asian miracle: Japan's high growth and the developmental state"),
    (43, 'planned', '成熟的计划经济：苏联、东欧、毛泽东时期的中国与南斯拉夫', "Mature planned economies: the USSR, Eastern Europe, Mao's China and Yugoslavia"),
    (44, 'naturalrate', '自然率与附加预期的菲利普斯曲线', 'The natural rate and the expectations-augmented Phillips curve'),
    (45, 'monetarism', '货币主义', 'Monetarism'),
    (46, 'floating', '布雷顿森林解体与浮动汇率', 'The end of Bretton Woods and floating exchange rates'),
    (47, 'oil', '石油危机与滞胀', 'Oil shocks and stagflation'),
    (48, 'ratex', '理性预期与卢卡斯批判', 'Rational expectations and the Lucas critique'),
    (49, 'credibility', '规则、可信度与沃尔克反通胀', 'Rules, credibility and the Volcker disinflation'),
    (50, 'budget', '政府预算约束：李嘉图等价与不愉快的算术', 'The government budget constraint: Ricardian equivalence and unpleasant arithmetic'),
    (51, 'latamdebt', '拉美债务危机与“失去的十年”', 'The Latin American debt crisis and the lost decade'),
    (52, 'hyperinflation', '恶性通胀怎样开始、怎样结束', 'How hyperinflations start and end'),
    (53, 'rbc', '实际经济周期', 'Real business cycles'),
    (54, 'newkeynesian', '新凯恩斯：名义刚性', 'New Keynesian economics: nominal rigidities'),
    (55, 'consensus', '新共识：三方程模型、泰勒规则与通胀目标制', 'The new consensus: the three-equation model, the Taylor rule and inflation targeting'),
    (56, 'endogenous', '内生增长', 'Endogenous growth'),
    (57, 'labor', '劳动市场与失业', 'Labour markets and unemployment'),
    (58, 'japanbubble', '日本：泡沫与失去的年代', 'Japan: the bubble and the lost decades'),
    (59, 'transition', '苏联解体与转轨：休克疗法与双轨渐进', 'The Soviet collapse and transition: shock therapy and dual-track reform'),
    (60, 'euro', '欧元的诞生', 'The birth of the euro'),
    (61, 'emcrises', '新兴市场的货币危机', 'Currency crises in emerging markets'),
    (62, 'moderation', '全球失衡与大缓和', 'Global imbalances and the Great Moderation'),
    (63, 'minsky', '另一条线：明斯基、存量–流量一致模型与 MMT', 'The other line: Minsky, stock–flow consistent models and MMT'),
    (64, 'gfc', '2008 年金融危机', 'The 2008 financial crisis'),
    (65, 'frictions', '金融摩擦与宏观审慎', 'Financial frictions and macroprudential policy'),
    (66, 'zlb', '零利率下限、量化宽松与前瞻指引', 'The zero lower bound, quantitative easing and forward guidance'),
    (67, 'abenomics', '安倍经济学与收益率曲线控制', 'Abenomics and yield curve control'),
    (68, 'multipliers', '财政乘数与紧缩之争', 'Fiscal multipliers and the austerity debate'),
    (69, 'eurocrisis', '欧债危机', 'The euro crisis'),
    (70, 'stagnation', '长期停滞、中性利率与低利率下的债务', 'Secular stagnation, the neutral rate and debt at low interest rates'),
    (71, 'heterogeneity', '异质性与不平等', 'Heterogeneity and inequality'),
    (72, 'chinacredit', '中国：信贷、资本管制与有管理的汇率', 'China: credit, capital controls and a managed exchange rate'),
    (73, 'pandemic', '疫情冲击与财政应对', 'The pandemic shock and the fiscal response'),
    (74, 'inflation21', '2021—2023 年通胀', 'The 2021–23 inflation'),
    (75, 'fiscaldominance', '财政主导与财政价格理论', 'Fiscal dominance and the fiscal theory of the price level'),
    (76, 'hierarchy', '货币等级、制裁与去美元化之争', 'The currency hierarchy, sanctions and de-dollarization'),
    (77, 'digitalmoney', '数字货币：加密资产、稳定币与央行数字货币', 'Digital money: crypto-assets, stablecoins and central bank digital currencies'),
    (78, 'fragmentation', '关税、碎片化与供给冲击', 'Tariffs, fragmentation and supply shocks'),
    (79, 'demography', '人口、AI 与长期增长', 'Demography, AI and long-run growth'),
    (80, 'evidence', '怎样判断一个宏观理论是对的', 'How to tell whether a macro theory is right'),
    (81, 'datareliability', '宏观数据的可靠性', 'How reliable are macroeconomic data?'),
    (82, 'assetprices', '从宏观到资产价格', 'From macroeconomics to asset prices'),
    (83, 'longarcs', '综合复盘：三条长弧', 'Synthesis: three long arcs'),
    (84, 'outlook', '展望：下一场“解释不了的危机”会从哪里来', 'Outlook: where the next unexplained crisis may come from'),
]

# Appendices: (letter, label, Chinese title, English title)
APPENDICES = [
    ('A', 'app:math', '数学工具', 'Mathematical tools'),
    ('B', 'app:symbols', '符号与数据来源', 'Symbols and data sources'),
    ('C', 'app:index', '对照与案例索引', 'Index of comparisons and cases'),
    ('D', 'app:timeline', '分地区大事年表', 'Timeline by region'),
]


def chapter_file(n: int, slug: str) -> str:
    return f"ch{n:02d}_{slug}"


def part_of(n: int) -> int:
    return next(p[0] for p in PARTS if p[5] <= n <= p[6])


def book_of_part(k: int) -> int:
    return next(b[0] for b in BOOKS if k in b[3])
