# 五运六气路由矩阵

按时间维度、用户意图、知识层级三轴匹配，将任务路由到最合适的子技能模块。

## CRITICAL: 路由执行协议

1. **MUST** 在执行前完成路由匹配。不得"先做后路由"。
2. **MUST** 匹配全部三维（时间维度 + 用户意图 + 知识层级）后进入子技能。
3. 路由未命中 → 提议新增子技能，不得强行匹配。
4. 跨模块任务 → 按"路径交叉"章节组合执行。
5. 路由后，进入目标子技能的 SKILL.md 后再行动。

## 按时间维度

| 时间输入 | 推荐入口 |
|----------|----------|
| 给定公历日期（YYYY-MM-DD） | `scripts/calculate_yunqi_api.py` → `rag-knowledge-base/` → `agent-workflow/react_workflow.md` |
| 给定公历年份 | `ganzhi-basics/` → `yunqi-calc/` |
| 给定农历年份 | `ganzhi-basics/references/liushijiazi.md` → `yunqi-calc/` |
| 给定节气 | `ganzhi-basics/references/jieqi.md` → `yunqi-calc/` → `yunqi-pathogenesis/` |
| 当前时间（"今年""当下"） | `ganzhi-basics/` → `yunqi-calc/` → `yunqi-pathogenesis/` → `yunqi-clinical/` |
| 历史年份回溯 | `yunqi-classics/` → `yunqi-calc/` |
| 未来年份预测 | `ganzhi-basics/` → `yunqi-calc/` → `yunqi-pathogenesis/` |

## 按用户意图

| 用户说 | 路由到 |
|--------|--------|
| "推算XX年运气" / "今年大运是什么" | `yunqi-calc/SKILL.md` |
| "今年容易发什么病" / "运气病机" | `yunqi-pathogenesis/SKILL.md` |
| "最近运气怎么样" / "我这个月要注意什么" | `scripts/calculate_yunqi_api.py --focus current-step` + `yunqi-clinical/`（自然语言路由） |
| "五运六气是什么思想" / "运气学核心是什么" | 先用 onboarding 介绍思想，再路由到概念解释或当前格局 |
| "帮我学运气" / "解释天人合一" | 概念讲解模式 + 经典 + 现代比喻 + 计算示例（支持 --level / --explain-concept） |
| "导出思想摘要 / 卡片 / PDF" | 路由到 export_thought.py（summary / cards / pdf） |
| "我的运气" / "出生年份运气" | `scripts/personal_yunqi_profile.py` |
| "运气治法" / "运气方药" | `yunqi-clinical/SKILL.md` — 治则治法 |
| "运气养生" / "运气调理" | `yunqi-clinical/SKILL.md` — 养生调理 |
| "运气针灸" / "运气选穴" | `yunqi-clinical/SKILL.md` — 针灸选穴 |
| "七篇大论" / "运气学说历史" | `yunqi-classics/SKILL.md` — 素问七篇 |
| "历代运气学说" / "运气流派" | `yunqi-classics/SKILL.md` — 历代学说 |
| "运气现代研究" / "运气文献" | `yunqi-classics/SKILL.md` — 现代研究 |
| "天干地支怎么算" / "六十甲子" | `ganzhi-basics/SKILL.md` |
| "节气和运气" / "六气交司" | `ganzhi-basics/references/jieqi.md` |
| "天干化五运" / "甲己化土" | `yunqi-calc/references/tiangan_huayun.md` |
| "地支化六气" / "子午少阴" | `yunqi-calc/references/dizhi_huaqi.md` |
| "主运客运" / "五运推移" | `yunqi-calc/references/zhuyun_keyun.md` |
| "主气客气" / "六气推移" | `yunqi-calc/references/zhuqi_keqi.md` |
| "司天在泉" / "上半年下半年" | `yunqi-calc/references/sitian_zaiquan.md` |
| "客主加临" / "顺逆" | `yunqi-calc/references/kezhujialin.md` |
| "天符岁会" / "运气同化" / "太乙天符" | `yunqi-calc/references/yunqi_tonghua.md` |
| "太过不及" / "平气" | `yunqi-calc/references/taiguo_buji.md` |
| "五运病机" / "木运太过什么病" | `yunqi-pathogenesis/references/wuyun_bingji.md` |
| "六气病机" / "厥阴风木病机" | `yunqi-pathogenesis/references/liuqi_bingji.md` |
| "运气合病" / "运气同化病机" | `yunqi-pathogenesis/references/yunqi_hebing.md` |
| "完整分析XX年" / "全年运气分析" | `ganzhi-basics/` → `yunqi-calc/` → `yunqi-pathogenesis/` → `yunqi-clinical/` |
| "写医案" / "记录运气应用" | `case-journal/_template.md` |
| "生成运气报告" / "输出分析报告" | `docs-generator/SKILL.md` → 按受众选择 `--report-type student|practitioner|researcher` |
| "学生版报告" / "学习报告" | `docs-generator/SKILL.md` → `--report-type student` |
| "临床版报告" / "医师版报告" | `docs-generator/SKILL.md` → `--report-type practitioner` |
| "研究版报告" / "文献版报告" | `docs-generator/SKILL.md` → `--report-type researcher` |
| "运气治则" / "平气治法" | `yunqi-clinical/references/zhize_zhifa.md` |
| "运气方药" / "岁运方" | `yunqi-clinical/references/fangyao_xuanze.md` |
| "推算某日运气" / "今天运气如何" | `scripts/calculate_yunqi_api.py today --summary`（或直接省略日期）→ `rag-knowledge-base/` |
| "我现在运气如何" / "最近运气" | `scripts/calculate_yunqi_api.py --focus current-step` |
| "Agent集成" / "RAG检索" / "知识库" | `rag-knowledge-base/README.md` |
| "ReAct工作流" / "推理链路" | `agent-workflow/react_workflow.md` |
| "System Prompt" / "角色约束" | `prompts/system_prompt.md` |
| "天气对齐" / "内外邪相合" / "结合天气" / "当地天气" | `scripts/weather_alignment.py <日期> --city <城市>` → `advanced-alignment/weather_integration.md` |
| "体质分析" / "体质运气交叉" | `advanced-alignment/constitution_alignment.md` |
| "运气方" / "三因司天方" / "什么方" | `rag-knowledge-base/asset4_formula.json` — 按 rag_key 匹配运气方 |
| "历代注家" / "王冰怎么说" / "刘完素" | `rag-knowledge-base/asset5_commentary.json` — 历代医家运气学说 |
| "地域" / "南方北方" / "我在XX地方" | `rag-knowledge-base/asset6_regional.json` — 地域运气修正系数 |
| "体质" / "我是什么体质" / "体质调理" | `advanced-alignment/constitution_alignment.md` → `scripts/personal_yunqi_profile.py` |
| "个人运气" / "我的运气" / "出生年份运气" | `scripts/personal_yunqi_profile.py` → `rag-knowledge-base/asset7_constitution.json` + `asset6_regional.json` |
| "自进化" / "自学习" / "优化报告" | `self-evolve/README.md` — 自进化引擎使用指南 |

## 按知识层级

| 层级 | 模块 | 脚本支持 | 说明 |
|------|------|----------|------|
| 推算层 | `ganzhi-basics/`, `yunqi-calc/` | `ganzhi_calc.py`, `dayun_calc.py`, `keyun_calc.py`, `liuqi_calc.py`, `kezhujialin.py` | 有明确数学规则，脚本保证准确性 |
| 病机层 | `yunqi-pathogenesis/` | 无 | 依赖中医辨证思维，文档化推理 |
| 临床层 | `yunqi-clinical/` | 无 | 依赖辨证论治，文档化推理 |
| 文献层 | `yunqi-classics/` | 无 | 文献检索与索引 |
| Agent层 | `rag-knowledge-base/`, `agent-workflow/`, `prompts/`, `advanced-alignment/`, `self-evolve/` | `calculate_yunqi_api.py(.js)`, `weather_alignment.py`, `personal_yunqi_profile.py`, `ingest_literature.py`, `self_evolve.py` | 大寒定年+RAG检索(7 asset)+ReAct推理+天气/体质高级对齐+自进化 |

## 路径交叉（跨模块场景）

部分任务跨多个模块。常见交叉路径：

```
完整年度分析路径:
  ganzhi-basics/SKILL.md → 干支推算
  ↓ 获取天干地支
  yunqi-calc/SKILL.md → 大运/六气/客主加临推算
  ↓ 获取运气格局
  yunqi-pathogenesis/SKILL.md → 病机分析
  ↓ 确定病机倾向
  yunqi-clinical/SKILL.md → 治法/方药/养生建议
  ↓ 整合输出
  docs-generator/SKILL.md → 生成综合报告

推算+文献路径:
  yunqi-classics/SKILL.md → 检索相关经文
  ↓ 获取理论依据
  yunqi-calc/SKILL.md → 推算验证
  ↓ 对比文献记载

医案沉淀路径:
  yunqi-calc/ → 推算就诊年份运气
  ↓
  yunqi-pathogenesis/ → 分析患者病机与运气关联
  ↓
  yunqi-clinical/ → 记录治法方药
  ↓
  case-journal/_template.md → 沉淀医案

Agent ReAct 推理路径（LLM Agent 集成）:
  prompts/system_prompt.md → 加载角色约束
  ↓
  scripts/calculate_yunqi_api.py → 输入日期，获取标准化JSON（含rag_keys）
  ↓
  rag-knowledge-base/ → 用rag_keys依次检索：
    ├ asset1-3: 岁运/司天/客主加临病机（经典七篇大论）
    ├ asset4: 三因司天方（运气方剂匹配）
    ├ asset5: 历代注家观点（王冰→陆懋修补充视角）
    ├ asset6: 地域修正（用户所在地区的气候偏差）
    └ asset7: 运气体质交叉（用户体质与运气互动）
  ↓
  agent-workflow/react_workflow.md → 多层辨证推理（经典层+注释层+地域层+体质层）
  ↓
  advanced-alignment/ → (可选) 天气对齐 + 体质交叉分析
    ├ scripts/weather_alignment.py：实时/历史/预报天气 × 运气格局
    └ scripts/personal_yunqi_profile.py：出生运气 × 体质/地域
  ↓
  输出结构化报告 + 免责声明
  ↓
  scripts/self_evolve.py → 自动记录本次推理（rag_key频次+盲区检测）

学习路径（学生）:
  ganzhi-basics/ → 理解干支基础
  ↓
  yunqi-calc/references/ → 逐项学习运气推算规则
  ↓
  yunqi-calc/SKILL.md → 用脚本验证推算结果
```

## 路由未命中 — 处理

如果当前任务未匹配以上任何表格，**不得强行匹配现有子技能**：

1. 检查是否为现有子技能的边缘情况（可扩展覆盖）
2. 如确为新类型，主动向用户提议新增子技能：
   - 建议子技能名称与覆盖范围
   - 所需知识层级
   - 与现有子技能的关系
3. 用户确认 → 按 `CONTRIBUTING.md` 创建
4. 创建后更新本路由矩阵

**AI 不需要等待用户发现缺口。路由失败就是提议新增子技能的信号。**

---

## 模糊意图与首次使用引导

当用户仅发送触发词（如"五运六气""运气"）或意图不明确时，**不得直接进入完整推算/临床报告流程**。应先进行轻量级引导，明确用户需求。

### 触发词宽泛时的处理流程

```
用户输入仅包含触发词 / 无明确日期 / 无明确需求类型
  ↓
读取 prompts/onboarding_prompt.md
  ↓
回复引导语，询问：
  1. 你想推算哪个日期/年份的运气？（默认：今天）
  2. 你的主要需求是？
     A. 快速了解当前运气概况（推荐 --summary）
     B. 完整年度分析报告（student/practitioner/researcher）
     C. 运气病机分析
     D. 运气治法/方药/养生
     E. 学习某个概念（如天干化五运、客主加临）
     F. 个人运气体质分析（需提供出生日期+地区）
  ↓
用户明确选择后，再按对应路由执行
```

### 轻量级引导判定条件

满足以下任一条件时，先引导再执行：

- 用户输入只包含触发词（如"五运六气""运气"）
- 用户未提供具体日期或年份
- 用户未说明需求类型（推算/病机/临床/学习/个人）
- 用户说"帮我看看""分析一下"等模糊表达
- 用户输入无法匹配路由矩阵中任何一行

### 引导回复示例

> 你好，我是五运六气分析助手。我可以帮你：
> 1. 推算任意日期的运气格局
> 2. 分析当前步位的病机与调理方向
> 3. 生成完整年度分析报告
> 4. 学习运气学基础概念
> 5. 分析个人先天运气体质
>
> 请告诉我：你想分析哪个日期？主要关注哪方面？

### 常见快速意图匹配

| 用户回复 | 直接执行 |
|----------|----------|
| "2026-06-29" 或 "今天" | `calculate_yunqi_api.py <日期> --summary` |
| "完整分析2026年" | `yunqi_report.py 2026 --audience practitioner` |
| "学习客主加临" | 读取 `yunqi-calc/references/kezhujialin.md` |
| "我1990年出生，体质如何" | `personal_yunqi_profile.py 1990-XX-XX` |

---
