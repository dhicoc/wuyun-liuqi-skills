# 脚本依赖速查

所有脚本支持 `--json` 输出机器可读格式（另有说明的除外）。

## 统一入口（Agent 首选）

| 脚本 | 用途 | 调用方式 |
|------|------|----------|
| **`yunqi_cli.py`** | **聚合 CLI**（calc/report/map/learn/compare/…） | `python scripts/yunqi_cli.py calc today --summary` |
| `calculate_yunqi_api.py` | 日期→完整运气 JSON（大寒定年）+ 思想层/导出 | `python scripts/calculate_yunqi_api.py today --summary --json` |
| `calculate_yunqi_api.js` | JS 版（需 lunar-javascript） | `node scripts/calculate_yunqi_api.js <YYYY-MM-DD> --json` |
| `yunqi_report.py` | 综合年度报告（默认含 rag_keys 知识库章节） | `python scripts/yunqi_report.py <年份> --audience student` · `--no-rag-bundle` 可关 |

**大寒定年**：运气年以大寒为界，非公历 1 月 1 日。

- `2026-01-15` → 运气年 2025（乙巳）
- `2026-01-20`（大寒后）→ 运气年 2026（丙午）

输出含 `rag_keys`，可直接检索 `rag-knowledge-base/`。

## 分项推算（legacy）

> 以下为**兼容分项入口**，均支持 `--help` / `--json`。  
> 日常与 Agent 请优先使用上方统一入口 `calculate_yunqi_api.py`。

| 脚本 | 用途 | 调用方式 |
|------|------|----------|
| `ganzhi_calc.py` | 年份→天干地支 | `python scripts/ganzhi_calc.py <年份> [--json]` |
| `dayun_calc.py` | 大运+太过不及+天符岁会 | `python scripts/dayun_calc.py <年份> [--json]` |
| `keyun_calc.py` | 主运+客运五步 | `python scripts/keyun_calc.py <年份> [--json]` |
| `liuqi_calc.py` | 司天在泉+客气主气六步 | `python scripts/liuqi_calc.py <年份> [--json]` |
| `kezhujialin.py` | 客主加临顺逆 | `python scripts/kezhujialin.py <年份> [--json]` |

## 高级对齐与导出

| 脚本 | 用途 | 调用方式 |
|------|------|----------|
| `weather_alignment.py` | 天气×运气对齐（Open-Meteo，`--mock` 可测） | `python scripts/weather_alignment.py <日期> --city <城市> --json` |
| `personal_yunqi_profile.py` | 个人运气体质 | `python scripts/personal_yunqi_profile.py <出生日期> [地区]` |
| `advanced_alignment.py` | 天气+体质+地域统一入口 | `python scripts/advanced_alignment.py --date <日期> --json` |
| `export_thought.py` | 思想摘要/Anki 卡片/PDF | `python scripts/export_thought.py today --format all` |
| `export_thought_map.py` | 思想地图（Mermaid） | `python scripts/export_thought_map.py today --format both` |
| `socratic_learn.py` | 苏格拉底学习会话 | `python scripts/socratic_learn.py today` |
| `yunqi_cli.py` | 统一入口（见上） | `python scripts/yunqi_cli.py learn today` |
| `learning_dashboard.py` | 学习路径仪表盘 | `python scripts/learning_dashboard.py` / `yunqi_cli.py dashboard` |
| `rag_search.py` | RAG 关键词 / 精确 key / 按日 / 语义 | `--key` · `--date today` · `--semantic 心火偏旺` |
| `rag_semantic.py` | 轻量语义检索（字符 n-gram） | `python scripts/rag_semantic.py 气候干燥 咳嗽` |
| `compare_py_js_yunqi.py` | Py/JS 关键字段一致性 | `python scripts/compare_py_js_yunqi.py` |
| `ingest_literature.py` | 文献注入 RAG | `python scripts/ingest_literature.py --source <文件> --category <分类>` |

## 运维与自进化

| 脚本 | 用途 | 调用方式 |
|------|------|----------|
| `self_evolve.py` | 日志/反馈/盲区/月报 | `python scripts/self_evolve.py stats\|feedback\|report ...` |
| `health_check.py` | 环境检查 | `python scripts/health_check.py` |
| `validate_knowledge_base.py` | RAG 校验 | `python scripts/validate_knowledge_base.py` |

## 主链路优先级

1. `yunqi_cli.py`（发现与聚合）或 `calculate_yunqi_api.py`（直接推算）
2. `yunqi_report.py` / `yunqi_cli.py report`（年度报告）
3. `socratic_learn.py` / `yunqi_cli.py learn`（思想理解）
4. `personal_yunqi_profile.py`（个人体质）
5. JS 版仅在前端/Node 集成时使用；与 Python 不一致时以 Python 为准。