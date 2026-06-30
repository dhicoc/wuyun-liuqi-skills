# 路线图

本文档记录五运六气 AI Agent 技能包的后续优化方向。

## P0：工程稳定性

- [x] 明确 Python 主链路、JS 可选接口。
- [x] 修复 Node.js 新版本下重复 `_` 解构占位符问题。
- [x] 增加 GitHub Actions CI 工作流。
- [x] 将报告输出划分为 examples / generated / test-results。
- [x] 在 CI 中增加更多 Python / Node 版本矩阵。
- [x] 将本地生成报告与自进化运行时数据从仓库追踪中彻底隔离。

## P1：知识库与文档

- [x] 补充 README 功能覆盖矩阵。
- [x] 补充 README_AI Agent 执行引导。
- [x] 补充架构文档与功能覆盖文档。
- [x] 完善 `rag-knowledge-base/index.json` 的自动生成或校验机制。
- [x] 为每个 RAG asset 补充字段级 schema 说明。
- [x] 将报告中的重要结论关联到具体经典或注家出处。

## P2：个人化与高级对齐

- [x] 新增九种体质量表评估脚本（`scripts/constitution_assessment.py`）。
- [x] 将九种体质量表评估结果深度接入 `personal_yunqi_profile.py`。
- [x] 将地域修正从静态提示扩展为报告中的可解释修正项。
- [x] 将天气 API 对齐设计转为可执行模块（`scripts/weather_alignment.py`）。
- [x] 为天气对齐增加缓存、历史同期均值和更多天气源适配。
- [x] 封装天气 × 体质三维叠加脚本（`scripts/yunqi_weather_constitution.py`）。
- [x] 新增统一高级对齐入口（`scripts/advanced_alignment.py`）。
- [x] 扩展天气对齐 AQI、UV、逐小时六步趋势与区域气候常年值。
- [x] 支持用户常住地、出生地、当前地的差异分析。

## P3：临床安全与输出质量

- [x] 报告融合：`yunqi_report.py --advanced-json` 与 `generate_html_report.py --with-advanced-alignment` 支持高级对齐章节。
- [x] 强化方药与针灸输出安全策略。
- [ ] 对临床版报告增加更严格的免责声明检查。
- [ ] 为严重症状或急症相关输入增加就医提醒。
- [ ] 增加报告快照测试，避免格式回退。

## P4：测试与发布

- [ ] 将 `verify_expansion.py`、`full_regression_test.py` 逐步迁移到 `tests/`。
- [ ] 在 `scripts/` 保留兼容 wrapper，避免破坏既有用户命令。
- [ ] 发布版本号与 changelog。
- [ ] 增加示例案例库与标准输出样例。
