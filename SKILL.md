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
| 推算某年运气 | `tasks/year-calc` → `modules/yunqi-calc/SKILL.md` |
| 运气病机 | `tasks/pathogenesis` → `modules/yunqi-pathogenesis/SKILL.md` |
| 治法/方药/养生 | `tasks/clinical` → `modules/yunqi-clinical/SKILL.md` |
| 七篇大论/文献 | `tasks/classics` → `modules/yunqi-classics/SKILL.md` |
| 学概念/思想 | `tasks/learn-concept` → `--explain-concept` |
| 个人运气/体质 | `tasks/personal-profile` → `personal_yunqi_profile.py` |
| 结合天气 | `tasks/weather-alignment` → `weather_alignment.py` |
| 导出摘要/卡片 | `tasks/export-thought` → `export_thought.py` |
| 写医案 | `tasks/case-journal` → `case-journal/_template.md` |
| Claude Code 插件 | `tasks/claude-plugin-install` → `workflows/claude-plugin-install.md` |
| 画个运气时间轴 | `tasks/timeline` → `scripts/visualize_timeline.py --output reports/generated/timeline_<年份>.html` |
| 安装/一致性自检 | `tasks/ops-selfcheck` → `scripts/health_check.py` |
<!-- SYNC:COMMON_TASKS_END -->

未命中 → 查 `routing.yaml` 的 `axes` 与 `on_miss`，不得强行匹配。
**讲解模式**：学概念/思想/注家对照 → `expression_style.md`（运气导师）+ `teaching-modules/` + `rag-knowledge-base/*_guide.md`；深度注家扮演 → `perspectives/`（刘完素/张介宾）。双语态见 `system_prompt.md` §1.1。

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
| 报告规范 | `modules/docs-generator/SKILL.md` |
| 思想地图 / 苏格拉底 / CLI / 仪表盘 | `export_thought_map.py` · `socratic_learn.py` · `yunqi_cli.py` · `learning_dashboard.py` |
| RAG 检索 | `rag_search.py --date today` · `--key` · `--asset asset9` 同格局岁图 · `--asset asset11-32` 历代名家医案（1994条/21部库，病证路由见 `system_prompt.md` §2.4）· `--asset asset33` 疾病易感性（33条，含33669例+691例高血压运气研究） · `--asset asset26,asset27` 逗号多库 · `--field herbs 石膏` 按字段 · `--semantic 口语` |
| 公版文献库/蒸馏指南 | `rag-knowledge-base/literature/`（51篇原文177.4万字）· `*_guide.md`（五层注释链+分组合并，Grep+Read 零依赖） |
| 医案库 | `asset9` 圣济总录岁图 + `asset11-32` 历代名家21部库共1994条（含杏轩184/孙文垣390/临证指南330等，按病证检索，含 herbs+formulas_referenced 结构化字段） |
| 医案渐进加载（P1-3） | 按病证/运气查医案库前**先调 `cases_routing.py`** 拿首选+补充+强制库清单，再只开命中库，避免整包 22 部撑爆上下文——`cases_routing.py --syndrome 湿温` · `--rag-key water_excess` · `--list-assets`。瘟疫/痈疽等高风险病证自动附加强制联动库 |
| 讲解人格/教学模块/注家 | `expression_style.md` + `teaching-modules/` + `perspectives/`（刘完素/张介宾） |
| 可导入包 | `wuyun_liuqi`（`from wuyun_liuqi import calculate, semantic_search`） |
| HTML 报告 | `generate_html_report.py`（含知识库精确命中章节） | 综合 Markdown 报告见 `yunqi_report.py`（含「内经方法论」章节，`--no-neijing` 可关） |
| 病机推理链 | `infer_pathogenesis.py <年份>`（岁运->司天在泉->六步->方剂五层推理） |
| Fallback 经验库 | `case-journal/field-journal/`（联网搜索沉淀，非原文存证；含 source_quote + confidence 字段；知识库未命中才查） |
| 医案关联图谱 | `case_relations.py --compare/--related`（跨医家对比+相似检索，1994条×402证型） |
| 运气时间轴 | `visualize_timeline.py <年份>`（六步客主加临时间轴 HTML） |
| 医案浏览器 | `generate_case_browser.py`（1994条静态HTML浏览+搜索+筛选） |
| pip 安装 | `pip install -e ".[lunar]"` → `python tests/smoke_pip_install.py` |
| Py/JS 一致性 | `scripts/compare_py_js_yunqi.py` |