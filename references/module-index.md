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
| System Prompt | `prompts/system_prompt.md` | TCM 运气专家角色约束 |
| 高级对齐 | `advanced-alignment/` | 天气、地域、体质交叉 |
| 自进化 | `self-evolve/` + `scripts/self_evolve.py` | 日志、盲区、反馈、月报 |

## RAG Asset 速查

| Asset | 文件 | 用途 |
|-------|------|------|
| 岁运病机 | `asset1_suiyun.json` | 五运太过/不及 |
| 司天在泉 | `asset2_sitian_zaiquan.json` | 上下半年六气 |
| 客主加临 | `asset3_kezhujialin.json` | 当前步位主客关系 |
| 运气方 | `asset4_formula.json` | 三因司天方 16 方 |
| 历代注家 | `asset5_commentary.json` | 王冰→陆懋修 11 家 |
| 地域修正 | `asset6_regional.json` | 八大区域修正系数 |
| 体质交叉 | `asset7_constitution.json` | 出生运气×体质调理 |

检索流程：`calculate_yunqi_api.py --json` → 取 `rag_keys` → 按 key 检索对应 asset。