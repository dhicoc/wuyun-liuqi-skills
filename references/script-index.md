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

## 分项推算（已并入统一入口）

> 原 `ganzhi_calc.py` / `dayun_calc.py` / `keyun_calc.py` / `liuqi_calc.py` / `kezhujialin.py` 五项单项脚本已合并进统一入口 `calculate_yunqi_api.py`，单次调用即返回全部域（干支/大运/主运客运/司天在泉/客主加临）。

| 域 | 在统一 JSON 中的关键键 |
|------|------|
| 干支 | `year_gz` / `sexagenary_index` |
| 大运 | `sui_yun` |
| 主运/客运 | `zhu_yun` / `ke_yun` |
| 六气 | `si_tian` / `zai_quan` / `ke_qi_six_steps` |
| 客主加临 | `ke_zhu_jia_lin` |

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
| `rag_search.py` | RAG 关键词 / 精确 key / 按日 / 语义 / 按字段 / 多库 | `--key` · `--date today` · `--semantic 心火偏旺` · `--field herbs 石膏` · `--asset asset26,asset27` |
| `infer_pathogenesis.py` | 运气病机推理链（岁运->司天在泉->六步->方剂） | `python scripts/infer_pathogenesis.py 2026` |
| `case_relations.py` | 医案关联图谱（跨医家对比+相似检索） | `--compare 孙一奎,叶桂 --tag 中风` · `--related swy_174` |
| `visualize_timeline.py` | 运气时间轴 HTML（复用报告 UI） | `python scripts/visualize_timeline.py 2026 --output timeline.html` |
| `generate_case_browser.py` | 医案知识库浏览器（1994条 HTML） | `python scripts/generate_case_browser.py --output browser.html` |
| `extract_structured_fields.py` | 医案结构化字段提取（herbs+formulas） | `python scripts/extract_structured_fields.py` |
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