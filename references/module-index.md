# 模块总表

| 模块 | 目录 | 适用场景 |
|------|------|----------|
| 干支基础 | `modules/ganzhi-basics/` | 天干地支、六十甲子、节气与运气 |
| 运气推算 | `modules/yunqi-calc/` | 大运/主运客运/司天在泉/客主加临/天符岁会 |
| 病机分析 | `modules/yunqi-pathogenesis/` | 五运六气病机、运气合病 |
| 临床应用 | `modules/yunqi-clinical/` | 治则治法、方药、针灸、养生 |
| 经典文献 | `modules/yunqi-classics/` | 素问七篇、历代学说、现代研究 |
| 报告生成 | `modules/docs-generator/` | 综合分析报告、医案报告 |
| 医案沉淀 | `case-journal/` | 运气应用医案记录 |
| 圣济岁图医案库 | `rag-knowledge-base/asset9_cases.json` + `case-journal/cases/distilled_cases.md` | 60 甲子岁图蒸馏医案，按 rag_key 可检索（asset9） |
| 统一计算 | `scripts/calculate_yunqi_api.py` | 大寒定年 + 日期输入 + JSON + rag_keys |
| RAG 知识库 | `rag-knowledge-base/` | 7 个 asset JSON（岁运/司天/客主/方药/注家/地域/体质） |
| ReAct 工作流 | `agent-workflow/` | 查工具→查知识库→辨证推理 |
| System Prompt | `prompts/system_prompt.md` | TCM 运气专家角色约束（临床模式 + 讲解模式双语态） |
| 讲解人格 | `prompts/expression_style.md` | 运气导师表达 DNA（讲解模式加载） |
| 注家人格 | `perspectives/` | 刘完素/张介宾可运行 perspective skill（深度扮演，nuwa 模式） |
| 教学模块 | `teaching-modules/` | 10 个概念五段式可加载模块（原文/注家/解读/金句/误区/深度分层） |
| 高级对齐 | `advanced-alignment/` | 天气、地域、体质交叉 |
| 自进化 | `self-evolve/` + `scripts/self_evolve.py` | 日志、盲区、反馈、月报 |
| 思想地图 | `scripts/export_thought_map.py` | Mermaid 概念图 + 年结构图 |
| 苏格拉底学习 | `scripts/socratic_learn.py` | 提问式学习会话 |
| 统一 CLI | `scripts/yunqi_cli.py` | calc/report/map/learn/search/dashboard |
| 学习仪表盘 | `scripts/learning_dashboard.py` | 概念覆盖 + 产物 + 推荐 |
| RAG 检索 | `scripts/rag_search.py` | 关键词 / `--key` 精确 / `--date` 按日打包 |
| 可导入包 | `wuyun_liuqi/` | `from wuyun_liuqi import calculate, fetch_by_date` |
| Py/JS 一致性 | `scripts/compare_py_js_yunqi.py` | 关键字段跨语言对比 |

## 五层注释链（公版蒸馏指南）

RAG asset 是精炼键值（回答"是什么"）；下列五本公版古籍蒸馏成的 Markdown 指南是**可 Grep+Read 的原文与注解**（回答"为什么、怎么治、古人怎么看"），零脚本零模型依赖，Agent 直接阅读。五层从方药到本体论，覆盖同一临床问题的不同深度。

| 层 | 指南文件 | 来源·注家 | 朝代 | 回答什么 |
|----|----------|----------|------|----------|
| 方药层 | `rag-knowledge-base/sanyin_sitianfang_guide.md` | 《三因极一病证方论》陈无择 | 宋 | 用什么方、六步怎么加减 |
| 教材层 | `rag-knowledge-base/yunqi_yaojue_pathogenesis_guide.md` | 《运气要诀》吴谦 | 清 | 病机歌诀、标准表述 |
| 病机层 | `rag-knowledge-base/suwen_xuanji_pathogenesis_guide.md` | 《素问玄机原病式》刘完素 | 金 | 逐症状辨病机、兼化是虚象 |
| 本体论层 | `rag-knowledge-base/leijing_tuyi_yunqi_philosophy_guide.md` | 《类经图翼》张介宾 | 明 | 太极阴阳五行本体、生克互藏 |
| 治法层 | `rag-knowledge-base/baoming_zhifa_guide.md` | 《素问病机气宜保命集》刘完素 | 金 | 病机十九条治则、六气岁宜治法 |

### 五运六气文献库（公版原文，35 篇）

| 目录 | 内容 | 检索 |
|------|------|------|
| `rag-knowledge-base/literature/` | 35 篇公版原文（61.6 万字，先秦至清代）含素问七篇大论全文、遗篇、圣济总录六十甲子岁图、玄珠密语等 | Grep+Read 零依赖，开箱即用 |

### 35 篇文献蒸馏指南（结构化速查，零依赖）

从 35 篇文献蒸馏出的 5 个结构化指南（合并分组），Agent 可 Grep 关键词定位要点，不必通读长文原文：

| 指南 | 覆盖文献 | 用途 |
|------|---------|------|
| `rag-knowledge-base/suwen_qipian_yipian_guide.md` | 素问七篇大论 + 遗篇（刺法论/本病论）9 篇 | 经文源头结构化：天干配五运/标本中气/亢则害承乃制/病机十九条/六气治法/运气疫病刺法 |
| `rag-knowledge-base/shengji_xuanzhu_suichatu_guide.md` | 圣济总录六十甲子岁图 + 玄珠密语 2 篇 | 逐年推演速查（按司天在泉六组示例）+ 王冰运气推演十七卷核心论点 |
| `rag-knowledge-base/mingqing_yunqi_zhuanzhu_guide.md` | 运气易览/松峰说疫/医学穷源集/运气证治歌诀/类经运气类/素问入式运气论奥/元和纪用经/本草纲目用药式 8 篇 | 明清运气推演与证治（含王旭高反刻板按语、李时珍五运六淫用药式） |
| `rag-knowledge-base/jinyuan_yijia_yunqi_guide.md` | 玄机原病式节录/医学启源/脾胃论/格致余论 4 篇 | 金元四家运气观（河间寒凉/易水/补土/养阴） |
| `rag-knowledge-base/xianqin_cunmu_yuanliu_guide.md` | 太始天元册/管子/月令/周礼/周易/王冰说明/天元玉册/昭明隐旨/已佚待考/时疫温病 10 篇 | 运学渊源（先秦思想源头）+ 已佚书目 + 晚清温病运气 |

详见 `rag-knowledge-base/literature/检索说明.md`。五本蒸馏指南是从这套文献中提炼的结构化产物；本目录是完整原文，供 Agent 引经据典、逐年详查。

**检索方式**：Grep 关键词定位 → Read 对应段落。各指南首部均有"关键词→定位段"索引表。

**与 RAG asset 的关系**：asset 给精炼结论（`rag_search --key`），指南给原文依据（Grep+Read）。两者互补。

**注家对照**：刘完素（寒凉派，"不可峻用辛温大热"）vs 张介宾（温补派，"阳气为本"）——运气学史上最尖锐的立场的对立，两方原文均可 Grep，供 `prompts/expression_style.md` 注家对照模式调用。

**同一问题五层 Grep 示例**（以"太阳寒水司天"为例）：
- 方药层：Grep `太阳司天` → 静顺汤、六步加减
- 教材层：Grep `太阳司天` → 歌诀"太阳司天寒下临"、病机症状
- 病机层：Grep `寒类` 或 `诸寒收引` → 寒属肾水、澄彻清冷
- 本体论层：Grep `五行统论` → 寒水之本在太极阴阳化生
- 治法层：Grep `太阳司天` → 岁宜苦以燥之温之、用热远热

**蒸馏原则**：仓库只放蒸馏产物，不放蒸馏工具（仿 nihaixia 模式）。五本均来自公版古籍，人读原文 + 结构化录入，逐字保留、不编造，每条可溯源至源文件行号。

## RAG Asset 速查

| Asset | 文件 | 条目 | 用途 |
|-------|------|------|------|
| 岁运病机 | `asset1_suiyun.json` | 10 | 五运太过/不及 |
| 司天在泉 | `asset2_sitian_zaiquan.json` | 6 | 上下半年六气 |
| 客主加临 | `asset3_kezhujialin.json` | 36 | 当前步位主客关系 |
| 运气方 | `asset4_formula.json` | 16 | 三因司天方（含蒸馏的六步加减） |
| 历代注家 | `asset5_commentary.json` | 30 | 王冰→高世栻 20 位医家 |
| 地域修正 | `asset6_regional.json` | 8 | 八大区域修正系数 |
| 体质交叉 | `asset7_constitution.json` | 108 | 9 体质×10 岁运完整覆盖 |
| 岁图医案 | `asset9_cases.json` | 60 | 圣济总录六十甲子岁图医案（按 rag_key 检索） |
| 岁宜治法 | `asset10_suiyi_zhifa.json` | 6 | 六气司天岁宜治法表 |
| 名医类案 | `asset11_mingyi_cases.json` | 102 | 明·江瓘，历代医案汇编 |
| 续名医类案 | `asset12_xumingyi_cases.json` | 84 | 清·魏之琇，续补医案 |
| 古今医案按 | `asset13_gujin_an_cases.json` | 159 | 清·俞震，含"震按"辨证 |
| 丁甘仁医案 | `asset14_dingganren_cases.json` | 177 | 近代丁甘仁，孟河医派 |
| 伤寒九十论 | `asset15_shanghan90_cases.json` | 49 | 宋·许叔微，伤寒经方 |
| 临证指南医案 | `asset16_ye_cases.json` | 330 | 清·叶桂，含华岫云按语 |
| 运气瘟疫防治 | `asset17_wenyi_yunqi.json` | 34 | 清·刘奎《松峰说疫》卷六：五运瘟疫侧重、六气司天民病、五郁治法、刚柔失守疫病专方 |
| 回春录医案 | `asset18_huichunlu_cases.json` | 40 | 清·王孟英《回春录》：湿热温病、内科杂病、妇科、儿科医案 |
| 张聿青医案 | `asset19_zhangyuqing_cases.json` | 138 | 清·张乃修《张聿青医案》：湿温伏暑、痰饮肝风、虚损血证医案 |
| 吴鞠通医案 | `asset20_wujutong_cases.json` | 120 | 清·吴瑭《吴鞠通医案》：温病三焦辨证、风温暑温伏暑、痹证痰饮医案 |
| 寓意草医案 | `asset21_yuyicao_cases.json` | 17 | 清·喻嘉言《寓意草》：议病式医案、伤寒危证、真阳上脱、误治救逆 |
| 洄溪医案 | `asset22_huixi_cases.json` | 23 | 清·徐灵胎《洄溪医案》（王孟英编）：经方辨证、中风伤寒、温疫、痰喘、血痢、产后、外科 |
| 花韵楼医案 | `asset23_huayunlou_cases.json` | 20 | 清·顾德华（女医）《花韵楼医案》：妇科专案，崩漏、月经、产后、胎产、乳癖 |
| 诊余举隅录 | `asset24_zhenyu_juji_cases.json` | 14 | 清·陈廷儒《诊余举隅录》：辨证精审，霍乱痢疾泄泻、感冒春温、中风、妇科经闭 |
| 许氏医案 | `asset25_xushi_cases.json` | 15 | 清·许恩普《许氏医案》：断证如折狱，伤寒痢疾中风、胎产妇科、误治救逆 |
| 杏轩医案 | `asset26_xingxuan_cases.json` | 184 | 清·程文囿（新安医派）《杏轩医案》：产后感邪、格阳证、大头时疫、半产血晕、蓄瘀脱血 |
| 孙文垣医案 | `asset27_sunwenyuan_cases.json` | 390 | 明·孙一奎《孙文垣医案》：温补命门、大头疫、目疾虚实、产后发热、痰火胁痛 |
| 丛桂草堂医案 | `asset28_conggui_cases.json` | 8 | 清·袁焯《丛桂草堂医案》：痰饮闭塞、喉痧阴亏、孕产寒痛 |
| 外科正宗·外用 | `asset29_waike_zhengzong.json` | 70 | 明·陈实功《外科正宗》：痈疽疔疮瘰疬脱疽，艾灸/火针/蟾酥饼/琥珀膏外治 |
| 立斋外科发挥 | `asset30_lizhai_waike.json` | 108 | 明·薛己《立斋外科发挥》：痈疽以气血为本最忌攻伐，内因→外候联动 |
| 醉花窗医案 | `asset31_zuihuachuang_cases.json` | 64 | 清·王堉《醉花窗医案》：脉证互参、虚实鉴别、误治救逆 |
| 医验随笔 | `asset32_yiyan_suibi.json` | 12 | 近代·沈奉江《医验随笔》：温病痰喘、温毒发痘、疙瘩瘟，内外兼治 |
| 术语 | `terminology.json` | 700 | 运气学术语白话解释 |

检索流程：`calculate_yunqi_api.py --json` → 取 `rag_keys` → 按 key 检索对应 asset。asset11-16 六部历代名家医案库（共 901 条）可按病证分类检索临证真实医案。