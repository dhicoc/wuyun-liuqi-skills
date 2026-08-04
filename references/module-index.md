# 模块总表

| 模块 | 目录 | 适用场景 |
|------|------|----------|
| 干支基础 | `ganzhi-basics/` | 天干地支、六十甲子、节气与运气 |
| 运气推算 | `yunqi-calc/` | 大运/主运客运/司天在泉/客主加临/天符岁会 |
| 病机分析 | `yunqi-pathogenesis/` | 五运六气病机、运气合病 |
| 临床应用 | `yunqi-clinical/` | 治则治法、方药、针灸、养生 |
| 经典文献 | `yunqi-classics/` | 素问七篇、历代学说、现代研究 |
| 报告生成 | `docs-generator/` | 综合分析报告、医案报告 |
| 医案沉淀 | `case-journal/` | 运气应用医案记录 |
| 统一计算 | `scripts/calculate_yunqi_api.py` | 大寒定年 + 日期输入 + JSON + rag_keys |
| RAG 知识库 | `rag-knowledge-base/` | 7 个 asset JSON（岁运/司天/客主/方药/注家/地域/体质） |
| ReAct 工作流 | `agent-workflow/` | 查工具→查知识库→辨证推理 |
| System Prompt | `prompts/system_prompt.md` | TCM 运气专家角色约束（临床模式 + 讲解模式双语态） |
| 讲解人格 | `prompts/expression_style.md` | 运气导师表达 DNA（讲解模式加载） |
| 教学模块 | `teaching-modules/` | 10 个概念五段式可加载模块（原文/注家/解读/金句/误区/深度分层） |
| 高级对齐 | `advanced-alignment/` | 天气、地域、体质交叉 |
| 自进化 | `self-evolve/` + `scripts/self_evolve.py` | 日志、盲区、反馈、月报 |
| 优化冲刺（执行真相源） | `docs/optimization-sprint.md` | 本轮文档/CLI/进程/测试任务与状态 |
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
| `rag-knowledge-base/literature/` | 35 篇公版原文（61.6 万字，先秦至清代）含素问七篇大论全文、遗篇、圣济总录六十甲子岁图、玄珠密语等 | Grep+Read 零依赖（基础层）；可选 bge-m3 向量语义检索（增强层，需本地 Ollama） |

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

| Asset | 文件 | 用途 |
|-------|------|------|
| 岁运病机 | `asset1_suiyun.json` | 五运太过/不及 |
| 司天在泉 | `asset2_sitian_zaiquan.json` | 上下半年六气 |
| 客主加临 | `asset3_kezhujialin.json` | 当前步位主客关系 |
| 运气方 | `asset4_formula.json` | 三因司天方 16 方（含蒸馏的六步加减） |
| 历代注家 | `asset5_commentary.json` | 王冰→陆懋修 11 家 |
| 地域修正 | `asset6_regional.json` | 八大区域修正系数 |
| 体质交叉 | `asset7_constitution.json` | 出生运气×体质调理 |

检索流程：`calculate_yunqi_api.py --json` → 取 `rag_keys` → 按 key 检索对应 asset。