# 功能覆盖说明

本文档将 README 中的功能覆盖矩阵展开说明，便于维护者判断当前能力边界与后续优化方向。

## 覆盖矩阵

| 功能层级 | 覆盖能力 | 主入口 / 文件 | 状态 |
|----------|----------|---------------|------|
| 干支基础 | 年干支、六十甲子序号、生肖 | `scripts/ganzhi_calc.py` | ✅ 已覆盖 |
| 五运推算 | 天干化五运、大运太过/不及、平气判断 | `scripts/dayun_calc.py`、`yunqi-calc/` | ✅ 已覆盖 |
| 主运客运 | 主运五步、客运五步、太少推移 | `scripts/keyun_calc.py` | ✅ 已覆盖 |
| 六气推算 | 司天、在泉、主气六步、客气六步 | `scripts/liuqi_calc.py` | ✅ 已覆盖 |
| 客主加临 | 六步客主关系、相得/不相得、顺逆分析 | `scripts/kezhujialin.py` | ✅ 已覆盖 |
| 日期统一接口 | 大寒定年、日干支、当前步位、RAG keys、JSON 输出 | `scripts/calculate_yunqi_api.py` | ✅ Python 主链路 |
| Node.js 接口 | 前端 / Node.js 集成 JSON 输出 | `scripts/calculate_yunqi_api.js` | 🟡 可选接口 |
| 病机分析 | 五运病机、六气病机、胜复、运气合病 | `yunqi-pathogenesis/` | ✅ 文档化推理 |
| 临床应用 | 治则治法、方药方向、针灸选穴、养生调理 | `yunqi-clinical/` | ✅ 参考建议，需免责声明 |
| 经典文献 | 素问七篇、历代学说、现代研究 | `yunqi-classics/` | ✅ 已覆盖 |
| RAG 知识库 | 岁运、司天在泉、客主加临、方剂、注家、地域、体质 | `rag-knowledge-base/asset*.json` | ✅ 已覆盖 |
| 个人体质 | 出生年运气倾向、当前岁运调理、地域修正 | `scripts/personal_yunqi_profile.py` | ✅ 已覆盖 |
| 天气对齐 | 实时气象 × 运气格局交叉分析；支持 Open-Meteo、QWeather、Seniverse、缓存、历史同期均值与 mock 测试 | `scripts/weather_alignment.py`、`advanced-alignment/weather_integration.md` | ✅ 已覆盖 |
| 天气 × 体质叠加 | 出生运气体质 × 当前岁运 × 天气实况三维叠加判断 | `scripts/yunqi_weather_constitution.py` | ✅ 已覆盖 |
| 报告生成 | 学生版、临床版、研究版报告 | `scripts/yunqi_report.py`、`docs-generator/` | ✅ 已覆盖 |
| 可视化 | 终端 ASCII、HTML 可视化报告 | `scripts/visualize_yunqi.py`、`scripts/generate_html_report.py` | ✅ 已覆盖 |
| 自进化 | 使用日志、盲区检测、反馈、月度报告 | `scripts/self_evolve.py` | ✅ 已覆盖 |
| 校验测试 | 环境检查、知识库校验、端到端测试、全量回归 | `scripts/health_check.py`、`scripts/validate_knowledge_base.py`、`scripts/verify_expansion.py`、`scripts/full_regression_test.py` | ✅ 已覆盖 |

## 当前成熟能力

1. **推算层**：干支、岁运、主运客运、司天在泉、客主加临均有脚本支持。
2. **Agent 集成层**：`calculate_yunqi_api.py` 可输出标准 JSON 与 RAG keys。
3. **知识层**：RAG assets 覆盖岁运、司天在泉、客主加临、运气方、注家、地域与体质。
4. **报告层**：支持学生版、临床版、研究版及 HTML 可视化。
5. **维护层**：具备健康检查、知识库校验、端到端测试、自进化报告。

## 仍可增强的方向

| 方向 | 说明 | 优先级 |
|------|------|--------|
| CI 稳定性 | 扩展 Python / Node 多版本矩阵 | 高 |
| 测试迁移 | 将测试脚本逐步迁移到 `tests/`，`scripts/` 保留兼容入口 | 中 |
| 天气对齐增强 | 已支持缓存、历史同期均值与多天气源；后续可扩展 AQI、UV、逐小时六步趋势和更多天气源 | 中 |
| 体质量表 | 引入九种体质量表评分输入，而非仅出生年映射 | 中 |
| 文献证据链 | 报告结论进一步标注出处与证据层级 | 中 |
| 医学安全 | 更严格区分理论参考、养生建议与临床处置 | 高 |

## 维护建议

- 新增功能时同时更新 README、README_AI 与本文件。
- 新增 RAG asset 时同步更新 `rag-knowledge-base/README.md` 与 `rag-knowledge-base/index.json`。
- 新增 CLI 参数时补充 `full_regression_test.py` 覆盖。
