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
- [x] 对临床版报告增加更严格的免责声明检查。
- [x] 为严重症状或急症相关输入增加就医提醒。
- [x] 增加报告快照测试，避免格式回退。

## P4：测试与发布

- [x] 将 `verify_expansion.py`、`full_regression_test.py` 逐步迁移到 `tests/`。
- [x] 在 `scripts/` 保留兼容 wrapper，避免破坏既有用户命令。
- [x] 增加示例案例库与标准输出样例。
- [x] 完整回归稳定在 63/0 + 75/0 verify。

## P5：思想理解与导出（已完成核心）

- [x] 报告思想层解读（build_thought_layer_section + CONCEPT_PHILOSOPHY）。
- [x] 支持 --level 渐进式 + --explain-concept。
- [x] 新增 export_thought.py：纯文本思想摘要、Anki卡片集（TSV+MD）、HTML/PDF导出。
- [x] 主入口集成 --export。
- [x] 自进化增强：概念追踪、理解反馈、隐私（SHA256 + sanitize）、会话统计。

## 当前工程冲刺（2026-07）

  
（文档去漂移 · CLI 统一 · 去 subprocess · 测试加固 · 包结构准备）

## 未来迭代方向（P6+）

- [x] 思想地图（Mermaid 概念关系图）- `scripts/export_thought_map.py`
- [x] 交互式苏格拉底学习模式 - `scripts/socratic_learn.py`
- [x] 统一 CLI / 菜单交互 - `scripts/yunqi_cli.py`
- [x] 个性化学习路径仪表盘 - `scripts/learning_dashboard.py`
- [x] 文献关键词检索（轻量）- `scripts/rag_search.py`
- [x] 文献片段深度语境化 - 10 本蒸馏指南 + 35 篇文献 Grep+Read（零依赖，开箱即用）

---

## P7：算法完整性与知识库扩展（2026-08 规划）

> 依据：`references/research-2026-08-11.md` 外部生态调研

### P7-1 推算算法覆盖度校验

- [x] 对照 `seLc7/YunQiXueShuo` 检查「五运齐化兼化」推算覆盖，缺失则补充到 `calculate_yunqi_api.py` -- 新增 `get_qihua` / `get_jianhua` 函数，输出到 `qi_hua` 字段
- [x] 对照检查「六气正化对化」推算覆盖 -- 新增 `get_zhengdui_huaqi` 函数 + `DIZHI_ZHENGDUI` 表，输出到 `zheng_dui` 字段
- [x] 补充「同天符 / 同岁会」推算 -- 新增 `check_tong_tianfu` / `check_tong_suihui` 函数，输出到 `tong_hua` 字段
- [x] 新增推算结果交叉验证：基于《医宗金鉴·运气要诀》《素问·天元纪大论》经典文献蒸馏的 52 项验证基线（天符12/岁会8/太乙天符4/同天符6/同岁会6/正化对化12/齐化兼化4）-- `scripts/verify_cross_check.py`，完全本地化无外部依赖
- [x] CI 增加「经典文献交叉验证」测试项 -- 52 项验证基线已纳入 CI 流程

### P7-2 疾病易感性 RAG

- [x] 新增 `rag-knowledge-base/asset33_disease_susceptibility.json` -- 12 条，覆盖岁运/司天/在泉/主气/运气相合五维度
- [x] 收录「出生运气格局 × 疾病易感性」临床数据 -- 33669 例 + 691 例高血压运气研究
- [x] 数据来源：高血压运气研究（太阴湿土司天/金运不及/阳明燥金/太阳寒水司天/顺化/天刑等）
- [x] `rag_search.py` 支持按疾病名/rag_key 检索易感性数据 -- `--asset asset33 高血压` / `--key taiyin_shitu_sitian --asset asset33`
- [x] `infer_pathogenesis.py` 推理链增加疾病易感性提示 -- 自动匹配岁运/司天/在泉组合 key
- [x] `system_prompt.md` 增加 asset33 路由说明
- [x] `SKILL.md` 延伸索引增加 asset33
- [x] schema 文件 + index.json 更新
- [x] 补全缺失的 21 个条目（6 岁运 + 4 司天 + 6 在泉 + 5 组合），总计 33 条，28 个 rag_key 全覆盖
- [x] 任意年份 --date 检索均命中 4 条疾病易感性（岁运+司天+在泉+组合）

### P7-3 skill 级 evals -- 不采纳

> 经评估，本项目已有 11 个测试文件、累计 200+ 项断言（full_regression 55 项 + skill_e2e 40 项 + full_scenario 51 项 + verify_expansion 105 项 + verify_cross_check 52 项），已远超官方标准对 evals 的要求。`evals/` 目录是第三方 skill 生成工具（agent-skill-creator）的建议模式，非 Agent Skills 开放规范的硬性要求。新增 evals 只会与现有 tests/ 重复，增加维护负担，对终端用户和 Agent 均无实际价值。

### P7-4 Skill 可移植性增强 -- 不采纳

> 经评估，本项目三项均不适用：
> 1. **`${CLAUDE_SKILL_DIR}`**：本项目是「仓库即 skill」模式（install.py 把整个仓库链接到 `~/.claude/skills/`），不是「目录即 skill」模式。相对路径已天然可用，加路径变量反而破坏现有路径解析。
> 2. **`context: fork`**：适用于长时间扫描/大量文件处理的隔离场景。运气推算是一次性计算，不需要隔离。
> 3. **`disable-model-invocation`**：适用于手动触发的 skill。本项目要 Agent 听到「五运六气」自动激活，不应禁用。

## P8：生态协作与数据导出（远期）

### P8-1 内经方法论交叉引用

- [x] 在 `teaching-modules/` 中引用 `kangarooking/huangdi-neijing-skill` 的 22 个思维工具 skill -- 新增 `teaching-modules/相关思维工具.md`，含 10 个教学模块 ↔ 22 个思维工具的完整映射表
- [x] 形成「内经方法论 + 运气推算」完整中医 Agent 能力栈 -- 映射表按根观念/格局/同化/推移/通用方法论五层组织
- [x] README 增加「相关项目」章节 -- 根 README + teaching-modules/README 均已添加

### P8-2 Parquet 数据导出

- [ ] 为 RAG asset 增加 Parquet 导出能力，服务 ML 研究者
- [ ] 参考 Pokkoa 数据集格式（HuggingFace `pokkoa/chinese-five-circuits-six-qi`）
- [ ] `generate_rag_index.py` 增加 `--format parquet` 选项

### P8-3 推算引擎第三方验证 -- 不采纳

> 经调研，`ZhuChaozheng/next-live-card` 的在线 API 返回 502 不可用，且无使用授权。`ccjaread/five_circuits_six_qi` 算法与本项目已覆盖的规则一致，无额外可验证项。P7-1 已通过《医宗金鉴·运气要诀》蒸馏的 52 项经典文献验证基线实现了本地自验证，无需依赖第三方服务。

## 不建议跟进

| 方向 | 原因 |
|------|------|
| 改用 `-skill` 后缀命名 | modules/ 已稳定，改名破坏性大、收益低 |
| 接入命理学说（三命通会等） | 与本项目「纯运气学」定位冲突 |
| 强行 L0-L4 显式分层 | 扁平路由已够用，强行分层增加复杂度 |
| P7-3 skill 级 evals | 现有 200+ 项 CI 断言已远超官方要求，evals 只会重复 |
| P7-4 `${CLAUDE_SKILL_DIR}` / `context: fork` / `disable-model-invocation` | 「仓库即 skill」模式不适用，自动激活场景不适用 |
| P8-3 第三方 API 验证 | 第三方 API 不可靠且无授权，P7-1 已有 52 项本地经典文献验证 |
