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
| "生成运气报告" / "输出分析报告" | `docs-generator/SKILL.md` |
| "运气治则" / "平气治法" | `yunqi-clinical/references/zhize_zhifa.md` |
| "运气方药" / "岁运方" | `yunqi-clinical/references/fangyao_xuanze.md` |
| "推算某日运气" / "今天运气如何" | `scripts/calculate_yunqi_api.py` → `rag-knowledge-base/` |
| "Agent集成" / "RAG检索" / "知识库" | `rag-knowledge-base/README.md` |
| "ReAct工作流" / "推理链路" | `agent-workflow/react_workflow.md` |
| "System Prompt" / "角色约束" | `prompts/system_prompt.md` |
| "天气对齐" / "内外邪相合" | `advanced-alignment/weather_integration.md` |
| "体质分析" / "体质运气交叉" | `advanced-alignment/constitution_alignment.md` |
| "运气方" / "三因司天方" / "什么方" | `rag-knowledge-base/asset4_formula.json` — 按 rag_key 匹配运气方 |
| "历代注家" / "王冰怎么说" / "刘完素" | `rag-knowledge-base/asset5_commentary.json` — 历代医家运气学说 |
| "地域" / "南方北方" / "我在XX地方" | `rag-knowledge-base/asset6_regional.json` — 地域运气修正系数 |
| "体质" / "我是什么体质" / "体质调理" | `rag-knowledge-base/asset7_constitution.json` — 体质运气交叉分析 |
| "自进化" / "自学习" / "优化报告" | `self-evolve/README.md` — 自进化引擎使用指南 |

## 按知识层级

| 层级 | 模块 | 脚本支持 | 说明 |
|------|------|----------|------|
| 推算层 | `ganzhi-basics/`, `yunqi-calc/` | `ganzhi_calc.py`, `dayun_calc.py`, `keyun_calc.py`, `liuqi_calc.py`, `kezhujialin.py` | 有明确数学规则，脚本保证准确性 |
| 病机层 | `yunqi-pathogenesis/` | 无 | 依赖中医辨证思维，文档化推理 |
| 临床层 | `yunqi-clinical/` | 无 | 依赖辨证论治，文档化推理 |
| 文献层 | `yunqi-classics/` | 无 | 文献检索与索引 |
| Agent层 | `rag-knowledge-base/`, `agent-workflow/`, `prompts/`, `advanced-alignment/`, `self-evolve/` | `calculate_yunqi_api.py(.js)`, `ingest_literature.py`, `self_evolve.py` | 大寒定年+RAG检索(7 asset)+ReAct推理+高级对齐+自进化 |

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
