# 脚本依赖速查

所有脚本支持 `--json` 输出机器可读格式（另有说明的除外）。

## 统一入口（Agent 首选）

| 脚本 | 用途 | 调用方式 |
|------|------|----------|
| `calculate_yunqi_api.py` | 日期→完整运气 JSON（大寒定年）+ 思想层/导出 | `python scripts/calculate_yunqi_api.py today --summary --json` |
| `calculate_yunqi_api.js` | JS 版（需 lunar-javascript） | `node scripts/calculate_yunqi_api.js <YYYY-MM-DD> --json` |
| `yunqi_report.py` | 综合年度报告 | `python scripts/yunqi_report.py <年份> --audience student\|practitioner\|researcher` |

**大寒定年**：运气年以大寒为界，非公历 1 月 1 日。

- `2026-01-15` → 运气年 2025（乙巳）
- `2026-01-20`（大寒后）→ 运气年 2026（丙午）

输出含 `rag_keys`，可直接检索 `rag-knowledge-base/`。

## 分项推算

| 脚本 | 用途 | 调用方式 |
|------|------|----------|
| `ganzhi_calc.py` | 年份→天干地支 | `python scripts/ganzhi_calc.py <年份>` |
| `dayun_calc.py` | 大运+太过不及+天符岁会 | `python scripts/dayun_calc.py <年份>` |
| `keyun_calc.py` | 主运+客运五步 | `python scripts/keyun_calc.py <年份>` |
| `liuqi_calc.py` | 司天在泉+客气主气六步 | `python scripts/liuqi_calc.py <年份>` |
| `kezhujialin.py` | 客主加临顺逆 | `python scripts/kezhujialin.py <年份>` |

## 高级对齐与导出

| 脚本 | 用途 | 调用方式 |
|------|------|----------|
| `weather_alignment.py` | 天气×运气对齐（Open-Meteo，`--mock` 可测） | `python scripts/weather_alignment.py <日期> --city <城市> --json` |
| `personal_yunqi_profile.py` | 个人运气体质 | `python scripts/personal_yunqi_profile.py <出生日期> [地区]` |
| `advanced_alignment.py` | 天气+体质+地域统一入口 | `python scripts/advanced_alignment.py --date <日期> --json` |
| `export_thought.py` | 思想摘要/Anki 卡片/PDF | `python scripts/export_thought.py today --format all` |
| `ingest_literature.py` | 文献注入 RAG | `python scripts/ingest_literature.py --source <文件> --category <分类>` |

## 运维与自进化

| 脚本 | 用途 | 调用方式 |
|------|------|----------|
| `self_evolve.py` | 日志/反馈/盲区/月报 | `python scripts/self_evolve.py stats\|feedback\|report ...` |
| `health_check.py` | 环境检查 | `python scripts/health_check.py` |
| `validate_knowledge_base.py` | RAG 校验 | `python scripts/validate_knowledge_base.py` |

## 主链路优先级

1. `calculate_yunqi_api.py`（首选）
2. `yunqi_report.py`（年度报告）
3. `personal_yunqi_profile.py`（个人体质）
4. JS 版仅在前端/Node 集成时使用；与 Python 不一致时以 Python 为准。