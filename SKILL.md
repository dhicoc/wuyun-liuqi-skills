---
name: wuyun-liuqi
description: >
  五运六气（运气学）AI Agent 技能包。帮助人类准确理解《黄帝内经》运气学思想体系（天人合一、气化、中和、时间节律）。
  提供干支推算、思想解读、概念解释、导出复习材料、自进化优化。
  触发词：五运六气、运气、大运、主运客运、主气客气、司天在泉、客主加临、
  太过不及、天符岁会、运气病机、运气治法、七篇大论。
  面向：学生、医师（理论参考）、研究者。
---

# 五运六气

> 运气学说为中医传统理论，非现代医学诊断标准。临床输出须附加免责声明。
> 详见 `case-journal/precedent-disclaimer.md`。

## Always Read

<!-- SYNC:ALWAYS_READ_START -->
1. `case-journal/precedent-disclaimer.md`
2. `rules/calculation.md`
3. `routing.yaml`
4. `workflows/routing-contract.md`
<!-- SYNC:ALWAYS_READ_END -->

首次使用另读：`workflows/bootstrap.md`

## 路由协议（摘要）

1. 读 `routing.yaml` 匹配任务（三轴：时间 + 意图 + 知识层级）
2. 意图模糊 → `prompts/onboarding_prompt.md`
3. 进入目标子技能 `SKILL.md` 后执行
4. 推算 MUST 调脚本，MUST NOT 凭记忆推算

完整契约见 `workflows/routing-contract.md`。人类可读路由摘要见 `routing.md`。

## Common Tasks

<!-- SYNC:COMMON_TASKS_START -->
| 用户说 | 路由 |
|--------|------|
| 今天/某日运气 | `tasks/quick-lookup` → `calculate_yunqi_api.py today --summary` |
| 最近/当前步位 | `tasks/current-step` → `--focus current-step` |
| 完整年度分析 | `tasks/full-year-analysis` → `yunqi_report.py` |
| 推算某年运气 | `tasks/year-calc` → `yunqi-calc/SKILL.md` |
| 运气病机 | `tasks/pathogenesis` → `yunqi-pathogenesis/SKILL.md` |
| 治法/方药/养生 | `tasks/clinical` → `yunqi-clinical/SKILL.md` |
| 七篇大论/文献 | `tasks/classics` → `yunqi-classics/SKILL.md` |
| 学概念/思想 | `tasks/learn-concept` → `--explain-concept` |
| 个人运气/体质 | `tasks/personal-profile` → `personal_yunqi_profile.py` |
| 结合天气 | `tasks/weather-alignment` → `weather_alignment.py` |
| 导出摘要/卡片 | `tasks/export-thought` → `export_thought.py` |
| 写医案 | `tasks/case-journal` → `case-journal/_template.md` |
| Claude Code 插件 | `tasks/claude-plugin-install` → `workflows/claude-plugin-install.md` |
<!-- SYNC:COMMON_TASKS_END -->

未命中 → 查 `routing.yaml` 的 `axes` 与 `on_miss`，不得强行匹配。

## 延伸索引

| 需求 | 文件 |
|------|------|
| 规则索引 | `RULES.md` → `rules/` |
| 常见踩坑 | `references/gotchas.md` |
| 任务闭环 | `workflows/task-closure.md` |
| 模块地图 | `references/module-index.md` |
| 脚本速查 | `references/script-index.md` |
| Agent 全链路 | `README_AI.md` |
| 跨工具薄壳 | `AGENTS.md`、`CLAUDE.md`、`.cursor/skills/wuyun-liuqi/SKILL.md` |
| Claude 插件 | `.claude-plugin/`、`workflows/claude-plugin-install.md` |
| 路由场景测试 | `tests/routing_scenarios.json`、`scripts/check_routing_scenarios.py` |
| 路由同步 | `scripts/sync_routing.py`（改 `routing.yaml` 后 `--write`） |
| 一致性/孤儿 | `conformance.yaml`、`scripts/check_conformance.py`、`scripts/audit_orphans.py` |
| ReAct 推理 | `agent-workflow/react_workflow.md` |
| 报告规范 | `docs-generator/SKILL.md` |
| 当前优化冲刺 | `docs/optimization-sprint.md` |
| 思想地图 | `scripts/export_thought_map.py` |
| 苏格拉底学习 | `scripts/socratic_learn.py` / `yunqi_cli.py learn` |
| 统一 CLI | `scripts/yunqi_cli.py` |
| 学习仪表盘 | `scripts/learning_dashboard.py` / `yunqi_cli.py dashboard` |
| RAG 检索 | `yunqi_cli.py search --date today` · `--key` · `--semantic 口语` |
| 可导入包 | `wuyun_liuqi`（`from wuyun_liuqi import calculate, semantic_search`） |
| HTML 报告 | `generate_html_report.py`（含知识库精确命中章节） |
| pip 安装 | `pip install -e ".[lunar]"` → `python tests/smoke_pip_install.py` |
| Py/JS 一致性 | `scripts/compare_py_js_yunqi.py` |