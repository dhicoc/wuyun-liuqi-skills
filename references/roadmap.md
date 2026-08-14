# 路线图

本文档记录五运六气 AI Agent 技能包的后续优化方向。

- **已完成里程碑**见文末「已完成里程碑（归档）」，仅作备查，不在活跃路线图内。
- **当前下一阶段方向（0.2.0+）**&#x89C1;「下一阶段路线图」，为本文件主体。

---

## 下一阶段路线图（0.2.0+）

> 2026-08-13 评审采纳的下一阶段方向（源自 `references/research-2026-08-11.md` 生态调研 + `self-evolve/reports/report_2026-08-12.md` 盲区信号）。>   
> 未采纳的提案（MCP 化 / 多宿主幂等等）仍在文末「候选项 / 暂缓」；**真·语义检索**经评审已明确不跟进，移入「不建议跟进」（见下表，n-gram + 字段精确匹配实为合理选型）。

### P9：发版 0.2.0 与文档去漂移

> 目标：把已落地但尚未固化的 2026-08-12 工程批次正式发布，并消除各文档间的计数 / 口径漂移。

- [x] 将 CHANGELOG `[Unreleased]` 的 2026-08-12 工程优化批次固化，发布 `0.2.0`（`pyproject.toml` 版本 `0.1.0` → `0.2.0` + 打 git tag `0.2.0`）
- [x] 消除文档漂移：统一到 CI 强制校验的权威值（原本 README 写 35 项、roadmap 写 63/0 + 75/0 verify；实际 36 项 CI 步骤 / 55/0 回归 / 105/0 扩展验证 / 1994 医案）
- [x] 同步 SKILL.md / README 的能力版图到实际计数（推算 9 / 检索 5 / 检索增强 5 / 报告导出 6 / 学习教学 3 / 自进化运维 7 / 安装校验 6）
- [x] 发布说明补「面向 AI Agent 的唯一形态」差异化定位 + 1994 条逐字医案 `source_quote` 存证

### P10：Parquet 数据导出

> 现状：roadmap 中唯一仍 `[ ]` 的项；低成本、价值明确，服务 ML 研究者。>   
> 情报（2026-08-13 调研，见 `research-2026-08-13.md` §3）：HuggingFace `pokkoa/chinese-five-circuits-six-qi` 实为**单列 `text` 散文（311 行、年+月粒度）**，非结构化运气表；其许可证**存在歧义**（HF 页「商业需授权」vs 镜像标 CC BY 4.0）。

- [x] 为 RAG asset 增加 Parquet 导出能力，对齐 Parquet **容器格式**（HF `datasets` 标准），但**导出自有结构化字段**，不照搬 pokkoa schema
- [x] `generate_rag_index.py` 增加 `--format parquet` + `--export-mode {index,rag,calendar}`（默认 JSON 不变，向后兼容；pyarrow 懒加载，零新增硬依赖）
- [x] 导出字段覆盖岁运 / 司天 / 在泉 / 主气 / 运气相合五维度 + `rag_key` + `source_quote` + `disease`
- [x] 已实现增值：额外生成「year×六步、宽年份跨度（1900–2100）」结构化运气 Parquet（pokkoa 仅 311 条散文），并附 CHANGELOG 字段说明；**不重分发 pokkoa 内容**，仅互引对照（见 `research-2026-08-13.md` §3.2）
- [x] 冒烟测试新增 P10 Parquet 场景并接入 CI（多轮 `--rounds 3`：CI 步骤先 `pip install pyarrow` 再 `python tests/skill_full_feature_smoke.py`）；实施提交见 `git log --oneline -1 -- scripts/generate_rag_index.py`。

### 近期修正（已完成）· 算法正确性

- [x] **岁会算法修正（P0 级）**：`check_suihui` 朴素判等「大运五行==地支五行」误报 4 年（壬寅/癸巳/庚申/辛亥），改为经典「运临本辰」（木临卯/火临午/金临酉/水临子/土临辰戌丑未），岁会恰为 8 年；Py/JS 双引擎同步，`compare_py_js` 一致。
- [x] **CI 盲区补齐**：`verify_cross_check` 的岁会/太乙天符断言改为全甲子逆向（恰好 8/4 年，无多无少），验证项 61→63。
- [x] **太乙天符确认**：`天符∩岁会`布尔组合即经典定义（命中经典四年），无需底层独立算法；docs/术语朴素定义已统一对齐。
- [x] 发布 `0.3.1`（`pyproject` 0.3.0→0.3.1 + tag 0.3.1）。

### P11：体质 / 易感性「激活」而非继续扩数据

> 反直觉信号（来自自进化报告）：asset33 的 earth/fire 体质·易感性条目**存在但从未被查**（低覆盖）——根因是路由未激活，不是缺数据。下一步应在推理链主动联动这些维度，而非再扩库。>   
> 情报（2026-08-13 调研，见 `research-2026-08-13.md` §5）：**学术依据充分**——出生/胎孕运气→体质→疾病易感性有多项统计研究（胎孕运气发病倾向符合率 79.1%；王琦九体 40 万+ 流调对应 313 病种；RA 2306 例运气禀赋 P<0.05）。具体映射可编码（火运不及+阳明燥金司天→阴虚质倾向；厥阴风木司天+少阳相火在泉→阳虚质倾向）。

- [x] 在 `personal_yunqi_profile.py` 计算**先天运气**（出生年干支 → 岁运/司天/在泉 + 胎孕期运气 `birth-280d`，权重参考「胎孕期前 3 个月」），作为一等输入喂给 `infer_pathogenesis` 与体质评估
- [x] 把 §5 的具体映射规则编码进 asset33 推理，使 earth/fire 维度在个人档案场景被**主动召回**（新增 `scripts/yunqi_susceptibility.py`：`compute_congenital_yunqi` / `recall_disease_susceptibility` / `eval_constitution_tendency`，含阴虚/阳虚/土运防五脏规则 + source）
- [x] `cases_routing.py` / `infer_pathogenesis.py` 增加「体质 → 易感性 → 病证」激活分支（`--congenital` 路由；`infer_pathogenesis(..., congenital_keys=None)` 可选注入，默认行为不变快照安全）
- [x] 增加联动的回归 / 快照测试，验证 earth/fire 覆盖度回升；复盘自进化 `misses/` 确认其它「存在但零查询」维度 → 新增 `tests/verify_p11_congenital_activation.py`（6/6：earth/fire 覆盖回升、earth_excess 命中、阳虚质规则对「厥阴风木司天+少阳相火在泉」触发）
- [x] 保留现有免责声明与「不替代临床诊断」红线（关联为统计性，非因果；`yunqi_susceptibility.py` 结论附免责声明）

> **完成说明（2026-08-14）**：P11 已「激活」而非扩数据——接线已存在的「先天运气 → 体质 → 易感性」链路（asset7 `birth_yunqi_mapping` 岁运 code 即 asset33 `sui_yun` rag_key，此前链路断开）。实施提交 `27efa98`（feat(P11)）+ `98e2fba`（fix(ci)：README 脚本数 44→45 对齐新增脚本）。CI run `31791246883` 全绿。未打版本 tag（用户确认保持提交即可）。

### P12：与 huangdi-neijing-skill 功能级集成（已完成）

> 现状仅交叉引用（`teaching-modules/相关思维工具.md` 的 10 教学模块 ↔ 22 思维工具映射）。目标是在 runtime 层打通，形成「内经方法论 + 运气推算」完整中医 Agent 能力栈。>   
> 情报（2026-08-13 调研，见 `research-2026-08-13.md` §4）：`kangarooking/huangdi-neijing-skill` 为 **MIT、22 skills（素问12+灵枢10）**，默认分支 `main`、仅 1 commit（2026-04-18，cangjie-skill AI 蒸馏，无后续维护）；每个 `SKILL.md` 带**机器可读 `related_skills` YAML frontmatter**（`depends-on`/`composes-with`/`contrasts-with`），正文为 **R/I/A1/A2/E/B 六维**（原文/方法论/书内案例/触发场景/可执行步骤/边界）；**无 `npx skills add` 机制**，采用路径检测 + glob（详见 PRD）。与运气链可组合者：`personalize-by-constitution`(因人施术)、`seasonal-regimen`(四时调养)、`emotion-organ-proxy`(情志脏腑)、`cascade-prediction`(传变预测)、`context-adaptation`(因地制宜)、`timing-opportunity`(时机)、`observation-inference`(以外测内)、`yin-yang-balance`/`five-elements-network`(运气太少/生克)。

- [x] 新增 `scripts/neijing_bridge.py`：只读解析器（glob `**/SKILL.md` + 解析 YAML frontmatter + **R/I/A1/A2/E/B 六维**）+ `neijing_available()` 路径检测；`yunqi→neijing` 映射表 `YUNQI_NEIJING_MAP` + `select_skills()`（按运气维度加权 + `related_skills` 多级展开，默认 top-N=3）
- [x] `build_methodology_section()`：输入运气格局 + 体质/病证 → 选 top-N 内经 skill → 拼装其 **I(框架)/E(步骤)/B(边界)** 为报告「内经方法论」章节，保留《内经》原文章节出处引用
- [x] **临床安全红线（MUST）**：复用 `_safety_text` 三件套（DISCLAIMER / CLINICAL_SAFETY_NOTICE / EMERGENCY_NOTICE）；灵枢临床/针刺类 skill（`qi-regulation`/`excess-deficiency-decision`/`root-cause-priority`/`observe-infer` 等）默认不进映射，若显式触发仅保留框架层、剥离 E 段可执行步骤、强制拒诊拒方，绝不输出具体穴位/方剂
- [x] **供应方式**：仓库**无 `npx skills add` 机制**，采用**路径检测 + glob**——`neijing_available()` 读 `HUANGDI_NEIJING_SKILL_DIR` 或默认目录；所需 `SKILL.md` **vendored 快照**于 `scripts/lib/neijing_snapshot/`（锁定 commit `17106a2`），CI 零网络依赖；缺失时优雅降级（主流程零报错、仅少一章）
- [x] 利用 `related_skills` 的 `composes-with` / `depends-on` 做多级联动（如 `personalize-by-constitution` ← `observe-infer` ← `context-adaptation`）
- [x] 集成 `yunqi_report.py` / `personal_yunqi_profile.py`：在「知识库/RAG 章节」之后、「临床安全提示」之前追加「内经方法论」章节；CLI `--neijing` / `--no-neijing` 开关
- [x] 补充联动回归测试（`tests/test_neijing_bridge.py` 用 vendored 快照、不依赖网络；`full_regression_test` 条件用例），验证运气结论可回链到内经方法论条目且临床类含三件套、无操作指令

> 完整实施设计见 `references/p12-implementation-prd.md`（2026-08-14 起草，已批准）。

---

## 候选项 / 暂缓（未采纳，保留参考）

- [ ] **MCP / Connector 化**：将推算 / 检索 / 报告 / 医案浏览器 / 时间轴封装为 MCP tool，暴露给更多 Agent 宿主（需先核实 `mcps/` 下 JSON 为真实 server 还是 stub）。
- [ ] **多宿主安装幂等 + 国际化英文蒸馏**（低优先）。

## 不建议跟进

| 方向                                                                   | 原因                                                                                                                                                                                                                                        |
| -------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 改用 `-skill` 后缀命名                                                     | modules/ 已稳定，改名破坏性大、收益低                                                                                                                                                                                                                   |
| 接入命理学说（三命通会等）                                                        | 与本项目「纯运气学」定位冲突                                                                                                                                                                                                                            |
| 强行 L0-L4 显式分层                                                        | 扁平路由已够用，强行分层增加复杂度                                                                                                                                                                                                                         |
| skill 级 evals                                                        | 现有 200+ 项 CI 断言已远超官方要求，evals 只会重复                                                                                                                                                                                                         |
| `${CLAUDE_SKILL_DIR}` / `context: fork` / `disable-model-invocation` | 「仓库即 skill」模式不适用，自动激活场景不适用                                                                                                                                                                                                                |
| 第三方 API 验证                                                           | 第三方 API 不可靠且无授权，P7-1 已有 61 项本地经典文献验证                                                                                                                                                                                                      |
| 继续扩 RAG 数据（体质/易感性维度）                                                 | 自进化报告显示相关条目已存在但零查询，应先「激活」而非扩库（见 P11）                                                                                                                                                                                                      |
| 真·语义检索（sentence-transformers 真实 embedding）                           | 本域词汇（药名/方剂名/术语）要求精确匹配，dense embedding 在近义词上易漂移（如「石膏」↔「寒水石」语义相近但为两味不同药）；`--field/--key` 结构化精确检索风险更低、更可控。`rag_semantic.py` 现以字符 n-gram + 字段匹配实现「无需向量数据库」，`--semantic` 实为 n-gram 退化，这恰是匹配领域特性的合理选型，印证「技术选型要匹配领域特性，不是复杂的就是对的」，故不做真实 embedding |

---

## 已完成里程碑（归档）

> 以下均已交付，归档备查，不在活跃路线图内。

### v0.1.0（2026-08-10）及此前

- **P0 工程稳定性**：Python 主链路 / JS 可选接口；CI 工作流；报告输出分区（examples / generated / test-results）；本地生成与自进化数据彻底隔离。
- **P1 知识库与文档**：README 功能覆盖矩阵 / AI Agent 引导；架构与功能文档；RAG `index.json` 自动校验；asset 字段级 schema 说明；结论关联经典 / 注家出处。
- **P2 个人化与高级对齐**：九种体质量表（`constitution_assessment.py`）；体质深度接入个人档案；地域修正可解释化；天气对齐模块（`weather_alignment.py`，含缓存 / 历史均值 / 多源）；天气 × 体质三维叠加；统一高级对齐入口（`advanced_alignment.py`）。
- **P3 临床安全与输出质量**：报告融合高级对齐章节；方药 / 针灸安全策略；临床版严格免责声明检查；急症就医提醒；报告快照测试。
- **P4 测试与发布**：测试迁移 `tests/`；保留兼容 wrapper；示例案例库；回归稳定 55/0 + 105/0 verify。
- **P5 思想理解与导出**：思想层解读（`build_thought_layer_section` + `CONCEPT_PHILOSOPHY`）；`--level` 渐进 + `--explain-concept`；`export_thought.py`（文本 / Anki TSV+MD / HTML / PDF）；`--export` 入口；自进化增强（概念追踪 / 反馈 / 隐私 / 统计）。
- **P6 未来迭代**：思想地图（`export_thought_map.py`）；苏格拉底学习（`socratic_learn.py`）；统一 CLI（`yunqi_cli.py`）；学习仪表盘（`learning_dashboard.py`）；文献关键词检索（`rag_search.py`）；片段深度语境化（10 指南 + 35 文献 Grep+Read，零依赖）。
- **2026-07 工程冲刺**：文档去漂移 · CLI 统一 · 去 subprocess · 测试加固 · 包结构准备。

### P7：算法完整性与知识库扩展（2026-08）

- **P7-1 推算算法覆盖度**：五运齐化 / 兼化、六气正化 / 对化、同天符 / 同岁会推算（`get_qihua` / `get_jianhua` / `get_zhengdui_huaqi` / `check_tong_tianfu` / `check_tong_suihui`）；基于《医宗金鉴·运气要诀》蒸馏的 52→61 项经典交叉验证基线（`verify_cross_check.py`，纳入 CI）。
- **P7-2 疾病易感性 RAG**：`asset33_disease_susceptibility.json` 12 → 33 条（28 个 `rag_key` 全覆盖），含 33669 + 691 例临床数据；`rag_search` 按疾病名 / `rag_key` 检索；`infer_pathogenesis` 推理链自动匹配。
- **P7-3 skill 级 evals**：经评估不采纳（现有 200+ 项断言已远超官方要求）。
- **P7-4 Skill 可移植性增强**：经评估不采纳（「仓库即 skill」模式不适用）。

### P8：生态协作与数据导出（远期）

- **P8-1 内经方法论交叉引用（已完成）**：`teaching-modules/相关思维工具.md` 10 教学模块 ↔ 22 思维工具映射（五层组织）；README「相关项目」章节。
- **P8-2 Parquet 数据导出**：见上方 P10（唯一仍 `[ ]` 项，已采纳为下一步）。
- **P8-3 推算引擎第三方验证**：经评估不采纳（第三方 API 不可靠且无授权）。
