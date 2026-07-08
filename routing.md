# 五运六气路由索引

> **单一真相源**：[`routing.yaml`](routing.yaml)  
> 本文件为人类可读摘要；路由匹配、新增条目、CI 校验均以 `routing.yaml` 为准。

## 如何使用

1. 打开 `routing.yaml`
2. 先匹配 `tasks`（高频任务）
3. 再查 `axes.time` / `axes.intent` / `axes.knowledge_level`
4. 跨模块任务查 `cross_paths`
5. 意图模糊查 `fuzzy_intent` → `prompts/onboarding_prompt.md`
6. 无匹配查 `on_miss`

执行契约见 [`workflows/routing-contract.md`](workflows/routing-contract.md)。

## 三轴概览

| 轴 | 决定什么 | YAML 节 |
|----|----------|---------|
| 时间 | 日期 API / 年份脚本 / 引导补信息 | `axes.time` |
| 意图 | 子技能组合与报告深度 | `axes.intent` + `tasks` |
| 知识层级 | 是否进入 RAG / 临床 / 文献 | `axes.knowledge_level` |

## 高频任务（tasks 摘要）

<!-- SYNC:TASKS_SUMMARY_START -->
| ID | 典型说法 | 入口 |
|----|----------|------|
| quick-lookup | 快速查某日/今天运气 | `calculate_yunqi_api.py today --summary` |
| current-step | 当前步位/最近注意 | `--focus current-step` |
| full-year-analysis | 完整年度分析 | `yunqi_report.py` |
| year-calc | 推算某年运气 | `yunqi-calc/SKILL.md` |
| pathogenesis | 运气病机 | `yunqi-pathogenesis/SKILL.md` |
| clinical | 运气治法/方药/养生 | `yunqi-clinical/SKILL.md` |
| classics | 经典文献/七篇大论 | `yunqi-classics/SKILL.md` |
| learn-concept | 学习概念/思想 | `--explain-concept` |
| personal-profile | 个人运气/体质 | `personal_yunqi_profile.py` |
| weather-alignment | 天气对齐 | `weather_alignment.py` |
| export-thought | 导出思想材料 | `export_thought.py` |
| case-journal | 写医案 | `case-journal/_template.md` |
| claude-plugin-install | Claude Code 插件安装 | `workflows/claude-plugin-install.md` |

完整列表与触发词见 `routing.yaml` → `tasks`。Agent 路由场景证明见 `tests/routing_scenarios.json`。
<!-- SYNC:TASKS_SUMMARY_END -->

## 跨模块路径（cross_paths 摘要）

- **完整年度**：干支 → 推算 → 病机 → 临床 → 报告
- **Agent ReAct**：system_prompt → calculate_yunqi_api → RAG → react_workflow → 自进化
- **医案沉淀**：推算 → 病机 → 临床 → case-journal 模板

## 跨工具入口

薄壳文件（`AGENTS.md`、`CLAUDE.md`、`CODEX.md`、`GEMINI.md`、`.cursor/rules/wuyun-liuqi.mdc`）均引导至本 `routing.yaml`，不重复规则正文。

## 维护说明

- 新增路由 → 先改 `routing.yaml`（含 `skill_sync.common_tasks`）
- 运行 `python scripts/sync_routing.py --write` 同步本文件与 `SKILL.md` 生成块
- 运行 `python scripts/sync_routing.py --check`（CI 默认）防止漂移
- 详细意图表、reference 级路由、层级定义均在 YAML 中，不在此重复