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
| 个人体质 | 出生年运气倾向、九种体质量表、当前岁运调理、地域修正 | `scripts/personal_yunqi_profile.py`、`scripts/constitution_assessment.py` | ✅ 已覆盖 |
| 天气对齐 | 实时气象 × 运气格局交叉分析；支持 Open-Meteo、QWeather、Seniverse、缓存、历史同期均值与 mock 测试 | `scripts/weather_alignment.py`、`advanced-alignment/weather_integration.md` | ✅ 已覆盖 |
| 天气 × 体质叠加 | 出生运气体质 × 当前岁运 × 天气实况三维叠加判断 | `scripts/yunqi_weather_constitution.py` | ✅ 已覆盖 |
| 统一高级对齐 | 基础运气、出生运气体质、九种体质量表、天气对齐统一入口 | `scripts/advanced_alignment.py` | ✅ 已覆盖 |
| 报告生成 | 学生版、临床版、研究版报告；支持注入高级对齐章节 | `scripts/yunqi_report.py`、`docs-generator/` | ✅ 已覆盖 |
| 可视化 | 终端 ASCII、HTML 可视化报告 | `scripts/visualize_yunqi.py`、`scripts/generate_html_report.py` | ✅ 已覆盖 |
| 自进化 | 使用日志 + 概念/哲学追踪 + 理解反馈 + 隐私（session_id SHA256哈希 + PII清洗） + 月度报告 + 清理 + 自动建议 | `scripts/self_evolve.py` | ✅ 已覆盖（支持思想理解维度） |
| 思想导出 | 纯文本思想摘要、Anki卡片集（TSV+MD）、高质量HTML/打印PDF | `scripts/export_thought.py`、`calculate_yunqi_api.py --export` | ✅ 已覆盖 |
| 思想层解读 | 报告内置思想层解读（宇宙观、生命观、现代连接）、核心概念哲学库 | `scripts/yunqi_report.py` (build_thought_layer_section + CONCEPT_PHILOSOPHY) | ✅ 已覆盖 |
| 渐进式学习 | --level simple/standard/deep、--explain-concept | `scripts/calculate_yunqi_api.py` | ✅ 已覆盖 |
| UX改进 | today默认、argparse --help、引导性下一步建议、ANSI颜色高亮、onboarding模糊引导 | `calculate_yunqi_api.py`、`health_check.py` 等 | ✅ 已覆盖 |
| 校验测试 | 环境检查、知识库校验、端到端测试、全量回归（75/0 verify, 63/0 full_regression） | `scripts/health_check.py`、`scripts/validate_knowledge_base.py`、`tests/verify_expansion.py`、`tests/full_regression_test.py` | ✅ 已覆盖 |

## 当前成熟能力

1. **推算层**：干支、岁运、主运客运、司天在泉、客主加临均有脚本支持。
2. **Agent 集成层**：`calculate_yunqi_api.py` 输出标准 JSON + RAG keys，支持 today、--level、--explain-concept、--export、自动自进化日志。
3. **思想理解层**：报告内置思想层解读（build_thought_layer_section）、CONCEPT_PHILOSOPHY 哲学库、引导性反思问题；支持渐进式学习。
4. **知识层**：7 个 RAG assets 覆盖岁运、司天在泉、客主加临、运气方、注家、地域、体质。
5. **报告与导出层**：学生/临床/研究版 + HTML 可视化；专用 export_thought.py 支持纯文本思想摘要、Anki 卡片、PDF/HTML。
6. **自进化层**：自动记录使用+概念，理解反馈，隐私保护（SHA256 session + sanitize），去重/过滤测试数据，会话统计，月报，清理。
7. **UX 层**：today 默认、优秀 --help、颜色高亮、输出末尾引导建议、onboarding 模糊意图处理、健康检查引导。
8. **维护层**：健康检查、知识库校验、端到端测试（75/0）、完整回归（63/0）。

## 仍可增强的方向

| 方向 | 说明 | 优先级 |
|------|------|--------|
| 渐进式学习深化 | 更强的概念连线、思想地图（Mermaid）、个性化学习路径 | 中 |
| 交互式学习模式 | 苏格拉底式对话、What-If 场景模拟、实时反思追踪 | 中 |
| 富交互报告 | HTML 报告增加可点击概念卡片、嵌入式思想地图 | 中 |
| 文献证据链 | 思想层解读中自动关联素问原文片段并语境化 | 中 |
| CI 稳定性 | 扩展 Python / Node 多版本矩阵 | 高 |
| 医学安全 | 更严格区分理论参考、养生建议与临床处置 | 高 |

## 维护建议

- 新增功能时同时更新 README、README_AI、SKILL.md、function-coverage.md、相关 optimization 文档。
- 新增 RAG asset 时同步更新 `rag-knowledge-base/README.md` 与 `rag-knowledge-base/index.json`。
- 新增 CLI 参数（--level、--export 等）或导出功能时补充 full_regression_test.py + 文档示例。
- 每次重大思想理解或自进化改动后，同步 self_evolve_optimization.md 和 understanding_the_thought_optimization.md。
