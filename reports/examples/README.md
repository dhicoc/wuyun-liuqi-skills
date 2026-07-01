# 标准输出样例

本目录保存可提交到仓库的标准输出样例，用于帮助用户理解 CLI 输出结构，也可作为人工回归参考。

## 样例列表

| 文件 | 生成命令 | 用途 |
|------|----------|------|
| `wuyun-liuqi-report.html` | `python scripts/generate_html_report.py 2026-06-29` | HTML 可视化示例 |
| `sample-data.json` | 手工维护 | HTML 报告示例数据 |
| `yunqi-report-practitioner-sample.md` | `python scripts/yunqi_report.py 2026 --audience practitioner` | 临床版年度报告样例，含经典与注家依据、安全提示 |
| `personal-profile-sample.md` | `python scripts/personal_yunqi_profile.py 2003-04-19 杭州 --constitution-demo` | 个人运气体质 + 九种体质量表示例 |
| `personal-profile-sample.json` | 同上加 `--json` | 个人画像机器可读输出 |
| `weather-alignment-sample.md` | `python scripts/weather_alignment.py 2026-06-29 --city 杭州 --mock --with-hourly-trend --with-regional-climate` | 天气对齐 Markdown 样例 |
| `weather-alignment-sample.json` | 同上加 `--json` | 天气对齐机器可读输出 |
| `advanced-alignment-sample.md` | `python scripts/advanced_alignment.py --date 2026-06-29 --birth-date 2003-04-19 --city 杭州 --constitution-demo --mock` | 统一高级对齐 Markdown 样例 |
| `advanced-alignment-sample.json` | 同上加 `--json` | 统一高级对齐机器可读输出 |

## 维护原则

1. 样例应使用固定日期与 mock 数据，避免因外部 API 变化导致内容漂移。
2. 样例中若涉及方药、针灸、穴位，必须保留安全提示与免责声明。
3. 修改报告结构后，应同步更新样例和快照。
4. 本目录与 `reports/generated/` 不同：本目录内容可纳入版本控制；本地生成结果应输出到 `reports/generated/` 或 `reports/test-results/`。
