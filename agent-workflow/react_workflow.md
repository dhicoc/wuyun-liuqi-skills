# 五运六气 Agent — ReAct 推理工作流

> 本文档定义五运六气 Agent 的 ReAct（Reasoning + Acting）闭环推理链。
> Agent 遵循"查工具 → 查知识库 → 辨证推理 → 输出"的闭环流程，
> 将确定性推算脚本与 RAG 知识检索、LLM 病机推理三者结合。
>
> 配套配置见 `agent-workflow/workflow_config.json`，Agent 行为约束见 `prompts/system_prompt.md`。

---

## 一、工作流总览

```
用户输入（日期/症状/体质）
        │
        ▼
┌───────────────────────────────────────────────────┐
│  Step 1  ACT    调用 calculate_yunqi_api(date_str) │  ← 确定性推算
│          获取精确干支/运气数据                       │
└──────────────────────┬────────────────────────────┘
                       ▼
┌───────────────────────────────────────────────────┐
│  Step 2  OBSERVE  解析 JSON，提取关键键值           │
│          year_gz / sui_yun / si_tian / zai_quan     │
│          / current_step / day_gz                    │
└──────────────────────┬────────────────────────────┘
                       ▼
┌───────────────────────────────────────────────────┐
│  Step 3  ACT    以提取键值为 query 检索 RAG 知识库   │  ← 知识检索
│          asset1(岁运) / asset2(司天在泉) /            │
│          asset3(客主加临)                            │
└──────────────────────┬────────────────────────────┘
                       ▼
┌───────────────────────────────────────────────────┐
│  Step 4  OBSERVE  接收 RAG 返回的                    │
│          病机文本 / 症状 / 治法 / 经文                │
└──────────────────────┬────────────────────────────┘
                       ▼
┌───────────────────────────────────────────────────┐
│  Step 5  THINK   三层辨证推理                        │  ← LLM 推理
│          岁运层 → 司天层 → 客主加临层                  │
│          策略："岁运为主，司天为统，客主加临看动态"      │
└──────────────────────┬────────────────────────────┘
                       ▼
┌───────────────────────────────────────────────────┐
│  Step 6  ACT    （可选）交叉比对用户体质数据           │  ← 个体化
│          体质 × 运气 → 个体倾向                       │
└──────────────────────┬────────────────────────────┘
                       ▼
┌───────────────────────────────────────────────────┐
│  Step 7  OUTPUT  生成结构化响应                      │  ← 输出
│          运气格局概述 → 病机分析 → 调理建议 → 免责声明  │
└───────────────────────────────────────────────────┘
```

**闭环特性**：每一步的 Observation 都会反馈到下一步的 Reasoning。若 Observation 异常（工具报错、RAG 未命中），Agent 进入错误处理分支（见第六章）而非中断。

---

## 二、逐步 ReAct 链

### Step 1 — ACT：调用推算工具

**动作**：调用 `calculate_yunqi_api(date_str)` 工具，传入用户提供的日期字符串。

```
TOOL_CALL: calculate_yunqi_api
INPUT: {"date_str": "1996-08-18"}
```

**说明**：
- `date_str` 支持格式：`YYYY`、`YYYY-MM-DD`、`YYYY-MM-DD HH:MM`
- 该工具封装了 `scripts/calculate_yunqi_api.py` 统一推算引擎，返回干支/大运/司天在泉/客主加临等完整运气 JSON
- 工具返回的数据是**绝对准确的**（R2 推算准确性规则），Agent 不得自行修正

**底层引擎映射（统一入口 calculate_yunqi_api.py）**：

| 工具输出字段 | 底层引擎 | 说明 |
|-------------|---------|------|
| year_gz / day_gz | `calculate_yunqi_api.py` | 年/日干支 |
| sui_yun | `calculate_yunqi_api.py` | 岁运（大运）含 code 与太过/不及 |
| si_tian / zai_quan | `calculate_yunqi_api.py` | 司天/在泉 |
| current_step | `calculate_yunqi_api.py` | 当前所处六步步位及客主加临关系 |

---

### Step 2 — OBSERVE：解析推算结果

**观察**：解析工具返回的 JSON，提取以下关键键值。

```json
{
  "year_gz": "丙子",
  "day_gz": "壬午",
  "sui_yun": {
    "element": "水",
    "code": "water_excess",
    "tai_shao": "太过",
    "is_taiguo": true
  },
  "si_tian": "少阴君火",
  "zai_quan": "阳明燥金",
  "current_step": {
    "step_num": 4,
    "step_name": "四之气",
    "jieqi_range": "大暑~秋分",
    "zhu_qi": "太阴湿土",
    "ke_qi": "太阴湿土",
    "jialin_relation": "客主同气",
    "jialin_shun_ni": "相得（顺）"
  },
  "tianfu": false,
  "suihui": true,
  "pingqi": false
}
```

**提取清单**（Agent 必须确认以下字段均已获取）：

| 字段 | 用途 |
|------|------|
| `year_gz` | 年干支 → 确定天干化运、地支化气 |
| `sui_yun.code` | 岁运编码（如 `water_excess`）→ RAG 检索 key |
| `si_tian` | 司天之气 → RAG 检索 key（如"少阴君火司天"） |
| `zai_quan` | 在泉之气 → 病机分析下半年的依据 |
| `current_step` | 当前步位 → 客主加临动态分析依据 |
| `current_step.jialin_relation` | 客主加临关系 → 动态病机 |

---

### Step 3 — ACT：检索 RAG 知识库

**动作**：以 Step 2 提取的键值为检索词，查询 RAG 知识库。核心病机查 asset1-3，补充方药/注家/地域/体质查 asset4-7，需医案佐证时查 asset9（同格局）、asset11-16（历代名家病证医案）、asset17（运气瘟疫防治）、asset18（回春录）、asset19（张聿青）、asset20（吴鞠通）、asset21（寓意草）、asset22（洄溪）、asset23（花韵楼）、asset24（诊余举隅录）、asset25（许氏）、asset26（杏轩）、asset27（孙文垣）、asset28（丛桂草堂）、asset29（外科正宗外用）、asset30（立斋内外联动）、asset31（醉花窗）或 asset32（医验随笔）。

```
TOOL_CALL: rag_search
INPUT: {
  "queries": [
    {"asset": "asset1", "query": "water_excess"},           // 岁运层
    {"asset": "asset2", "query": "少阴君火司天"},              // 司天层
    {"asset": "asset2", "query": "阳明燥金在泉"},              // 在泉层
    {"asset": "asset3", "query": "四之气_太阴湿土_客主同气"},    // 客主加临层
    {"asset": "asset16", "query": "诸痛"}                    // 医案佐证层（asset11-16 按病证检索）
  ]
}
```

**RAG 知识库结构**：

| Asset | 路径 | 内容 | 检索 key 示例 |
|-------|------|------|--------------|
| asset1 | `rag-knowledge-base/asset1_suiyun.json` | 岁运病机（《气交变大论》《五常政大论》） | `water_excess`、`wood_deficiency` |
| asset2 | `rag-knowledge-base/asset2_sitian_zaiquan.json` | 司天在泉病机（《至真要大论》） | `少阴君火司天`、`阳明燥金在泉` |
| asset3 | `rag-knowledge-base/asset3_kezhujialin.json` | 客主加临顺逆病机（《六元正纪大论》） | `zhu_shaoyang_ke_shaoyin`、`四之气_客主同气` |
| asset4-7 | `rag-knowledge-base/asset4-7_*.json` | 方药/注家/地域/体质补充层 | `water_excess`、related keys、region_id |
| asset9 | `rag-knowledge-base/asset9_cases.json` | 圣济总录六十甲子岁图医案（同格局） | 岁运 / rag_key |
| asset11-16 | `rag-knowledge-base/asset11-16_*_cases.json` | 六部历代名家医案库（名医类案/续名医类案/古今医案按/丁甘仁/伤寒九十论/临证指南，901 条） | `entry_id` / `category` |
| asset17 | `rag-knowledge-base/asset17_wenyi_yunqi.json` | 松峰说疫·运气瘟疫防治库（五运瘟疫侧重、六气司天民病、五郁治法、刚柔失守疫病专方，34 条） | `code` / `sitian_key` / `zaiquan_key` / `rag_key` / `ganzhi` |
| asset18 | `rag-knowledge-base/asset18_huichunlu_cases.json` | 回春录·王孟英湿热温病医案库（外感温病/内科杂病/妇科/儿科，40 条） | `category` / `rag_key` / `case_id` |
| asset19 | `rag-knowledge-base/asset19_zhangyuqing_cases.json` | 张聿青医案库（湿温伏暑/痰饮肝风/虚损血证/内科杂病，138 条） | `category` / `rag_key` / `case_id` |
| asset20 | `rag-knowledge-base/asset20_wujutong_cases.json` | 吴鞠通医案库（温病三焦辨证/风温暑温伏暑/痹证痰饮，120 条） | `category` / `rag_key` / `case_id` |
| asset21 | `rag-knowledge-base/asset21_yuyicao_cases.json` | 寓意草医案库（议病式医案/伤寒危证/真阳上脱/误治救逆，17 条） | `category` / `rag_key` / `case_id` |
| asset22 | `rag-knowledge-base/asset22_huixi_cases.json` | 洄溪医案库（经方辨证/中风伤寒/温疫/痰喘/血痢/产后/外科痈疽，23 条） | `category` / `rag_key` / `case_id` |
| asset23 | `rag-knowledge-base/asset23_huayunlou_cases.json` | 花韵楼医案库（妇科专案/崩漏/月经/产后/胎产/乳癖，20 条） | `category` / `rag_key` / `case_id` |
| asset24 | `rag-knowledge-base/asset24_zhenyu_juji_cases.json` | 诊余举隅录医案库（辨证精审/霍乱/痢疾/泄泻/感冒/中风/经闭，14 条） | `category` / `rag_key` / `case_id` |
| asset25 | `rag-knowledge-base/asset25_xushi_cases.json` | 许氏医案库（断证如折狱/伤寒/痢疾/中风/胎产/误治救逆，15 条） | `category` / `rag_key` / `case_id` |
| asset26 | `rag-knowledge-base/asset26_xingxuan_cases.json` | 杏轩医案库（新安医派/产后感邪/格阳证/大头时疫/蓄瘀脱血，14 条） | `category` / `rag_key` / `case_id` |
| asset27 | `rag-knowledge-base/asset27_sunwenyuan_cases.json` | 孙文垣医案库（12→26）（温补命门/大头疫/目疾虚实/产后发热/痰火胁痛，12 条） | `category` / `rag_key` / `case_id` |
| asset28 | `rag-knowledge-base/asset28_conggui_cases.json` | 丛桂草堂医案库（痰饮闭塞/喉痧阴亏/孕产寒痛/疮疡阴亏，8 条） | `category` / `rag_key` / `case_id` |
| asset29 | `rag-knowledge-base/asset29_waike_zhengzong.json` | 外科正宗·外用医案库（痈疽/疔疮/瘰疬/脱疽/咽喉/肺痈/腿痈/囊痈/臋痈/肛痈/痔漏/下疳/瘤/多骨疮/结毒/脚气/乳痈，70 条） | `category` / `rag_key` / `case_id` |
| asset30 | `rag-knowledge-base/asset30_lizhai_waike.json` | 立斋外科发挥·内外联动医案库（痈疽以气血为本，内因→外候联动，108 条） | `category` / `rag_key` / `internal_key` / `external_key` |
| asset31 | `rag-knowledge-base/asset31_zuihuachuang_cases.json` | 醉花窗医案库（脉证互参/虚实鉴别/误治救逆，64 条） | `category` / `rag_key` / `case_id` |
| asset32 | `rag-knowledge-base/asset32_yiyan_suibi.json` | 医验随笔医案库（温病/痰喘/便秘/温毒发痘/疙瘩瘟，内外兼治，12 条） | `category` / `rag_key` / `case_id` |

**检索策略**：
- 优先精确匹配 `sui_yun.code`（如 `water_excess`）
- 司天/在泉以六气名 + "司天"/"在泉" 组合检索
- 客主加临以步位 + 主气 + 客气 + 关系 组合检索
- 若精确匹配未命中，降级为语义检索（embedding 相似度）
- **需医案佐证时**：先 Read `rag-knowledge-base/yunqi_medical_cases_guide.md`（医案库×运气病证检索导航）确定查哪个库，再按病证关键词检索。rag_key 不直接查医案库（asset11-26 仅按病证检索），须先按指南第五节"运气病机→病证翻译对照"翻译成病证。

---

### Step 4 — OBSERVE：接收 RAG 返回

**观察**：RAG 返回病机文本、症状描述、治法建议、经文引用。

```json
{
  "asset1_results": [
    {
      "key": "water_excess",
      "source": "素问·气交变大论",
      "bingji": "岁水太过，寒气流行，邪害心火。民病身热烦心躁悸，阴厥上下中寒，谵妄心痛。",
      "zangfu": "肾（水过盛）、心（受邪）",
      "zhengtao": "心悸、烦躁、身热、心痛、寒厥"
    }
  ],
  "asset2_results": [
    {
      "key": "少阴君火司天",
      "source": "素问·至真要大论",
      "bingji": "少阴之胜，心下热善饥，脐中反动，气游三焦。",
      "zangfu": "心（火）、下半年肺（燥）"
    },
    {
      "key": "阳明燥金在泉",
      "source": "素问·至真要大论",
      "bingji": "阳明在泉，湿毒不生，其味甘，其治辛苦甘。"
    }
  ],
  "asset3_results": [
    {
      "key": "四之气_客主同气",
      "source": "素问·六元正纪大论",
      "bingji": "客主同气，气候偏盛，太阴湿土加临，湿气偏旺，脾土受困。",
      "zhengtao": "胸闷、脘痞、身重"
    }
  ]
}
```

---

### Step 5 — THINK：三层辨证推理

**推理**：基于 Step 2 推算数据 + Step 4 RAG 病机文本，按以下策略进行三层辨证推理。

> **核心策略**：岁运为主，司天为统，客主加临看动态。

#### 岁运层（宏观）

分析大运对五脏盛衰的宏观影响。

- 大运五行决定年度气候基调与对应脏腑的盛衰倾向
- 太过 → 本气偏盛，所胜（我所克）受邪
- 不及 → 本气偏衰，所不胜（克我者）来乘
- 引用依据：《气交变大论》五运太过不及病机条文

示例推理（1996 丙子年，水运太过）：
> 岁水太过，寒气流行。水盛则乘火，心火受邪。肾水偏盛，可见寒厥、身热；心火受邪，可见心悸、烦躁、心痛。这与用户"心慌"主诉方向一致。

#### 司天层（半年）

分析司天在泉对上半年/下半年的气候-病机影响。

- 司天主上半年（从大寒至大暑），在泉主下半年（从大暑至大寒）
- 司天之气胜 → 上半年相应脏腑易病
- 在泉之气胜 → 下半年相应脏腑易病
- 司天与在泉互为阴阳配对（一阴对一阳等）
- 引用依据：《至真要大论》六气病机十九条、司天在泉治法

示例推理（少阴君火司天、阳明燥金在泉）：
> 少阴君火司天，上半年火气偏旺。8月已入下半年，阳明燥金在泉当令，燥气偏盛。燥邪伤肺，肺金又生肾水，可加重水运太过的水盛倾向。火（司天）与水（大运）有制约关系，但下半年火气已退，制约力减弱。

#### 客主加临层（动态）

分析当前步位的动态病机。

- 客主加临决定当前时段的即时气候-病机倾向
- 相得（顺）→ 气候相对平和，但仍需看客气偏盛
- 不相得（逆）→ 气候异常，病机加重
- 引用依据：《六元正纪大论》六步客主加临

示例推理（四之气，客主同气太阴湿土，相得）：
> 当前处四之气，客主同气皆为太阴湿土，湿气偏盛。湿为阴邪，易阻遏气机，胸阳不振，可见胸闷。湿土又来乘肾水（土克水），与大运水运太过形成"湿来乘水"的叠加效应。用户"胸闷"症状与当前步位湿邪偏盛吻合。

**三层综合判断**：
> 岁运水太过为宏观背景（心火受邪 → 心悸），司天少阴君火/在泉阳明燥金为半年框架（下半年燥金当令），客主加临四之气湿土偏盛为即时因素（胸闷）。三层叠加指向心脾同病、水湿泛滥之候。

---

### Step 6 — ACT（可选）：交叉比对用户体质

**动作**：若用户提供了个人体质数据（如出生年月、体质类型、既往病史），将其与运气格局交叉比对。

```
CONDITIONAL:
IF user_provides_constitution:
    cross_reference(constitution, yunqi_pattern)
    → 个体化倾向分析
ELSE:
    skip (输出通用运气分析)
```

**交叉比对逻辑**：
- 用户出生年大运 × 当前年大运 → 体质运气叠加效应
- 用户体质五行偏盛 × 当前运气偏盛 → "同气相求"加重 / "异气相制"缓和
- 例：用户体质偏水湿（痰湿质），逢水运太过年 → 水湿更盛，需加强健脾利湿

> 此步为可选增强。无体质数据时，Agent 输出通用运气分析，并在调理建议中注明"如需个体化分析，请提供出生年月及体质信息"。

---

### Step 7 — OUTPUT：生成结构化响应

**输出**：按以下结构生成最终响应。

```
【运气格局概述】
  - 年份干支、大运（太过/不及）、司天/在泉、当前步位

【病机分析】
  - 岁运层：大运对五脏盛衰的宏观影响
  - 司天层：上半年/下半年气候病机
  - 客主加临层：当前步位动态病机
  - 三层综合判断

【调理建议】
  - 治则：遵循《至真要大论》五味制约原则
  - 食疗：按运气偏盛推荐食疗方向
  - 养生：起居、情志、运动建议

【相关医案佐证】（可选增强：当 Step 3 检索到医案时必填；未检索到或用户未问医案时省略）
  - 呈现 ≥1 个召回医案，每条按「一句话白话转述 + 原文关键句引用」格式：
    - 白话转述：用大白话讲清该案的病机、关键治法与转归（如"某案也是湿热困住气机，孟英用豁痰通腑让大便一通，痰排出来就好了"）
    - 原文引用：附 source_quote 关键句（文言原文，注明出库，如"《回春录·霍乱》：……"）
  - 若医案与本次运气病机吻合，点明"与本次推算的 X 病机相印证"；不吻合则如实说明差异，不强行套用
  - 医案仅作佐证参考，不得代替本次辨证结论

【免责声明】
  ⚠️ 免责声明：以上分析基于中医运气学说理论推算，仅供参考。
  运气学说非现代医学诊断标准，具体诊疗须由执业中医师辨证论治。
  请勿据此自行用药或针灸。

【反馈入口】
  本次分析是否对您有帮助？您可以通过以下方式提供反馈，帮助我们持续优化：
  `python scripts/self_evolve.py feedback --session-id <本次会话ID> --rating 1-5 --comment "您的建议"`
  
  评分说明：1=很不满意，2=不满意，3=一般，4=满意，5=非常满意。
  您的反馈将被记录到 `self-evolve/feedback/`，用于生成月度优化报告。
```

**输出约束**：
- 术语必须使用中医病机术语（见 `prompts/system_prompt.md` 措辞规范）
- 调理建议涉及药剂处方时必须声明"请遵医嘱"
- 免责声明为必须组成部分，不得省略（R1 医学安全规则）

---

## 三、示例工作流追踪

> **用户输入**："我生于1996年8月18日，最近总觉得心慌胸闷"

### Step 1 — ACT

```
THOUGHT: 用户提供了出生日期(1996-08-18)和症状(心慌胸闷)。
         需先获取该日期的精确运气数据。
ACTION: calculate_yunqi_api(date_str="1996-08-18")
```

### Step 2 — OBSERVE

```
OBSERVATION:
  year_gz = "丙子"
  day_gz = "壬午"
  sui_yun = {element:"水", code:"water_excess", tai_shao:"太过", is_taiguo:true}
  si_tian = "少阴君火"
  zai_quan = "阳明燥金"
  current_step = {
    step_num:4, step_name:"四之气",
    jieqi_range:"大暑~秋分",
    zhu_qi:"太阴湿土", ke_qi:"太阴湿土",
    jialin_relation:"客主同气", jialin_shun_ni:"相得（顺）"
  }
  tianfu=false, suihui=true, pingqi=false

THOUGHT: 1996丙子年，水运太过，少阴君火司天，阳明燥金在泉。
         8月18日处四之气，客主同气太阴湿土。
         用户生于此年此日，当前运气格局对其体质有直接影响。
         需检索RAG知识库获取病机文本。
```

### Step 3 — ACT

```
ACTION: rag_search(queries=[
  {asset:"asset1", query:"water_excess"},
  {asset:"asset2", query:"少阴君火司天"},
  {asset:"asset2", query:"阳明燥金在泉"},
  {asset:"asset3", query:"四之气_太阴湿土_客主同气"}
])
```

### Step 4 — OBSERVE

```
OBSERVATION:
  asset1 → "岁水太过，寒气流行，邪害心火。民病身热烦心躁悸..."
           来源：《素问·气交变大论》
           脏腑：肾(水过盛)、心(受邪)
           症候：心悸、烦躁、身热、心痛、寒厥

  asset2 → 少阴君火司天："少阴之胜，心下热善饥..."
           来源：《素问·至真要大论》
           阳明燥金在泉："湿毒不生，其治辛苦甘。"
           来源：《素问·至真要大论》

  asset3 → 四之气客主同气："太阴湿土加临，湿气偏旺，脾土受困。"
           来源：《素问·六元正纪大论》
           症候：胸闷、脘痞、身重

THOUGHT: RAG返回的病机文本与用户症状(心慌→心悸, 胸闷→胸痹)高度吻合。
         进入三层辨证推理。
```

### Step 5 — THINK

```
REASONING:

【岁运层】
1996丙子年，丙为阳干，水运太过。
《气交变大论》："岁水太过，寒气流行，邪害心火。"
水盛乘火 → 心火受邪 → 心悸、烦躁。
用户"心慌"对应中医"心悸"，与岁运层病机方向一致。

【司天层】
少阴君火司天(上半年火旺)，阳明燥金在泉(下半年燥旺)。
8月18日属下半年，燥金当令。
燥邪伤肺金，肺金生肾水 → 加重水运太过的水盛倾向。
下半年火气(司天)已退，对水运太过的制约力减弱。

【客主加临层】
当前四之气，客主同气太阴湿土，相得(顺)。
湿为阴邪，易阻遏气机 → 胸阳不振 → 胸闷。
湿土乘肾水(土克水) → 与大运水太过形成"湿来乘水"叠加。
用户"胸闷"对应湿邪困脾、胸阳不振。

【综合判断】
岁运层(心火受邪→心悸) + 客主加临层(湿邪偏盛→胸闷)
= 心脾同病、水湿泛滥之候。
宏观(岁运)与即时(客主加临)两层病机均指向用户症状。
```

### Step 6 — ACT（体质交叉）

```
THOUGHT: 用户生于1996年8月18日，即生于水运太过之年。
         出生年大运=当前讨论年大运(同为丙子年运气格局)。
         用户体质先天受水运太过影响 → 先天肾水偏盛倾向。
         当前逢同类运气 → 同气相求，水湿更易偏盛。
         个体化倾向：心悸(水乘火)+胸闷(湿困脾)风险更高。
ACTION: 体质交叉比对完成，结果纳入Step 7输出。
```

### Step 7 — OUTPUT

```
【运气格局概述】
1996年（丙子年），天干丙化水运，阳干主太过，故岁运为水运太过。
地支子化少阴君火司天，阳明燥金在泉。
8月18日处四之气（大暑~秋分），主气太阴湿土，客气亦为太阴湿土，
客主同气，相得（顺）。
本年为岁会之年（大运水与地支子五行同属水），运气同化，水气偏盛尤甚。

【病机分析】
· 岁运层：岁水太过，寒气流行，邪害心火（《气交变大论》）。
  水盛乘火，心火受邪，可见心悸、烦躁。此为全年宏观病机基调。
· 司天层：少阴君火司天主上半年火旺，阳明燥金在泉主下半年燥旺。
  8月已入下半年，燥金当令，肺金生水，助长水盛。
· 客主加临层：四之气客主同气太阴湿土，湿气偏盛。
  湿为阴邪，阻遏气机，胸阳不振，可见胸闷。
  湿土乘肾水（土克水），与岁运水太过形成叠加。
· 综合：岁运层心火受邪（心悸）+ 客主加临层湿邪偏盛（胸闷），
  指向心脾同病、水湿泛滥之候。用户生于此年，先天禀赋受水运太过影响，
  同气相求，症状更为典型。

【调理建议】
· 治则：水运太过，当"抑其太过，扶其不胜"（《至真要大论》）。
  宜温阳化气、利水泄浊，兼养心安神。湿土偏盛，佐以健脾化湿。
· 食疗：宜食辛苦温之品（辛开苦降、温阳化湿），如陈皮、茯苓、生姜等。
  忌生冷肥甘（助湿碍脾）。
· 养生：起居宜避寒就温，勿久居潮湿之地。情志宜静养心神，勿过度操劳。
  运动宜温和（八段锦、太极），微汗即止，勿大汗伤阳。
· 方药方向：温阳利水、养心安神之方向（如苓桂术甘汤类方向）。
  ⚠️ 具体方药须辨证加减，请遵医嘱，切勿自行用药。

【免责声明】
⚠️ 免责声明：以上分析基于中医运气学说理论推算，仅供参考。
运气学说非现代医学诊断标准，具体诊疗须由执业中医师辨证论治。
请勿据此自行用药或针灸。
```

---

## 四、错误处理

### 4.1 工具返回异常数据

| 异常场景 | 处理策略 |
|---------|---------|
| `calculate_yunqi_api` 返回非 JSON 或字段缺失 | 1. 重试一次（排除瞬时故障）<br>2. 仍失败则降级为手动调用 `scripts/yunqi_report.py <year> --json`<br>3. 手动调用也失败 → 告知用户"推算工具暂时不可用"，输出纯文献分析（无推算数据），附加免责声明 |
| `sui_yun.code` 为未知值（不在 RAG key 表中） | 1. 降级为语义检索（用 `sui_yun.element` + `tai_shao` 组合检索）<br>2. 仍无结果 → 使用 `modules/yunqi-pathogenesis/references/wuyun_bingji.md` 全文检索<br>3. 标注"此运为罕见格局，病机分析基于通论推导" |
| `current_step` 为 null（用户仅给年份无日期） | 1. 输出全年运气格局（不含动态步位分析）<br>2. 在病机分析中省略"客主加临层"<br>3. 提示用户"如需当前步位动态分析，请提供具体日期" |

### 4.2 RAG 检索未命中

| 未命中场景 | 处理策略 |
|-----------|---------|
| asset1（岁运）检索无结果 | 1. 降级检索 `modules/yunqi-pathogenesis/references/wuyun_bingji.md`<br>2. 以 `sui_yun.element` 为 key 全文匹配<br>3. 仍无 → 依据五行生克通论推导，标注"基于通论推导，未经文献验证" |
| asset2（司天在泉）检索无结果 | 1. 降级检索 `modules/yunqi-pathogenesis/references/liuqi_bingji.md`<br>2. 以六气名为 key 全文匹配<br>3. 仍无 → 依据《至真要大论》六气病机通论推导 |
| asset3（客主加临）检索无结果 | 1. 降级检索 `modules/yunqi-calc/references/kezhujialin.md`<br>2. 依据客主加临顺逆通论推导（相得→平和、不相得→异常）<br>3. 标注"客主加临病机基于顺逆通论推导" |
| 全部 asset 均未命中 | 1. 回退为纯推算+LLM通论推理模式<br>2. 在输出中显著标注"本次分析未经知识库验证，仅为理论推导"<br>3. 强化免责声明措辞 |

### 4.3 用户输入歧义

| 歧义场景 | 处理策略 |
|---------|---------|
| 日期格式不明确（如"96年8月"） | 1. 尝试解析为 1996-08-01（取月初默认）<br>2. 在输出中标注"按8月初推算，如需精确步位分析请提供完整日期"<br>3. 不擅自猜测，影响步位判断时必须确认 |
| 症状描述模糊（如"不舒服"） | 1. 输出该日期通用运气格局分析<br>2. 提示用户"如需针对性病机分析，请描述具体症状（如心悸、胸闷、头痛等）"<br>3. 不编造症状 |
| 年份范围歧义（如"甲子年"） | 1. 将"甲子年"转换为最近的甲子年（如 1984/2044）<br>2. 在输出中标注"按公历 XXXX 年推算"<br>3. 若存在多个可能年份，列出候选让用户确认 |
| 用户请求超出运气范畴（如"我血压高吃什么药"） | 1. 声明"此问题超出运气理论分析范畴"<br>2. 建议就医<br>3. 不替代现代医学诊断<br>4. 仅在用户重新表述为运气相关问题时继续 |

### 4.4 错误处理原则

```
错误处理三原则：
1. 不中断 — 遇到局部失败时，降级而非中断整体流程
2. 不编造 — RAG未命中时标注"未经文献验证"，不编造经文
3. 不省略 — 无论降级到何种程度，免责声明必须附加
```

---

## 五、与现有技能包的集成关系

| 本工作流步骤 | 对应技能包模块 | 关系 |
|-------------|--------------|------|
| Step 1 (ACT 工具调用) | `scripts/` | `calculate_yunqi_api` 封装了 scripts 下的推算引擎 |
| Step 3 (ACT RAG检索) | `modules/yunqi-pathogenesis/references/` | RAG 知识库 asset 内容来源于此 |
| Step 3 (ACT RAG检索) | `modules/yunqi-clinical/references/` | 治法方药 RAG 内容来源于此 |
| Step 5 (THINK 三层推理) | `modules/yunqi-pathogenesis/SKILL.md` | 推理策略与病机分析子技能一致 |
| Step 7 (OUTPUT 结构化输出) | `modules/docs-generator/SKILL.md` | 输出格式遵循报告生成子技能规范 |
| Step 7 (免责声明) | `case-journal/precedent-disclaimer.md` | 免责声明文本来源 |

> 本工作流是技能包的**Agent 编排层**，将现有的推算脚本、病机文档、临床文档、报告模板串联为可由 Agent 框架（LangChain / AutoGen / Dify）执行的闭环推理链。

---

## ACTION REQUIRED

- [ ] 确认 `calculate_yunqi_api` 工具已注册并可调用
- [ ] 确认 RAG 知识库三个 asset 已索引并可检索
- [ ] 确认 `prompts/system_prompt.md` 已加载为 Agent 系统提示词
- [ ] 确认 `case-journal/precedent-disclaimer.md` 免责声明文本已内置

## 任务完成自检

- [ ] Step 1 工具调用成功，JSON 解析无误
- [ ] Step 2 关键键值全部提取（year_gz / sui_yun.code / si_tian / zai_quan / current_step）
- [ ] Step 3 RAG 检索至少命中一个 asset
- [ ] Step 4 RAG 返回内容已解析（病机/症状/治法/经文）
- [ ] Step 5 三层推理完整（岁运层 + 司天层 + 客主加临层）
- [ ] Step 7 输出包含四部分（运气格局概述 + 病机分析 + 调理建议 + 免责声明）
- [ ] 免责声明已附加，措辞符合 `precedent-disclaimer.md` 规范
- [ ] 如有降级处理，已标注"未经文献验证"等提示
