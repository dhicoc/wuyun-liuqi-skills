# 优化路线图

> 基于全量审计（2124 条医案、32 资产、17 项全链路测试全绿）后制定的系统优化计划。
> 每项优化独立可验证，按优先级分批实施。

## 一、RAG 检索能力升级（P0-P1）

### OPT-01 多库联合检索 `[P0]`
- **现状**：`--asset` 只支持单库或全局，无法指定"在孙文垣+杏轩+临证指南三个库中搜索"
- **目标**：`--asset` 支持逗号分隔多库（如 `--asset asset26,asset27,asset16`）
- **改动文件**：`scripts/rag_search.py`
- **验证**：`python scripts/rag_search.py 头痛 --asset asset26,asset27 --json` 返回跨库结果

### OPT-02 embedding 语义检索 `[P0]` ~~已移除~~
- **决策**：知识库已蒸馏，不需要向量模型；sentence-transformers 对用户配置极不友好
- **现状**：已移除 embedding 后端，只保留 n-gram TF 余弦（零依赖）
- **改动**：从 rag_semantic.py 移除全部 embedding 代码，从 pyproject.toml/requirements.txt 移除依赖

### OPT-03 按字段检索 + 方药索引 `[P1]`
- **现状**：`_EXACT_ID_FIELDS` 只做精确匹配，`search()` 做全字段关键词，无法按 `formula`/`syndrome` 等单字段检索
- **目标**：新增 `--field` 参数（如 `--field formula 茵陈`），方药字段分词索引
- **改动文件**：`scripts/rag_search.py`
- **验证**：`python scripts/rag_search.py --field formula 石膏 --json` 返回所有用了石膏的医案

## 二、医案结构化增强（P1-P2）

### OPT-04 医案结构化字段 `[P1]`
- **现状**：`formula` 是一整段文字，`category` 是自由文本，无标准化标签
- **目标**：为医案新增 `herbs`（药味列表）、`formulas_referenced`（引用方剂）、`syndrome_tags`（证型标签）、`meridian_tags`（归经）字段
- **改动文件**：各 `asset*_*.json`（渐进式补充）、`scripts/generate_rag_index.py`
- **验证**：`python scripts/rag_search.py --field herbs 柴胡 --json` 精确检索药味

### OPT-05 医案关联图谱 `[P2]`
- **现状**：2124 条医案扁平无关联
- **目标**：按 `syndrome_tags` 关联同类医案，支持"对比检索"（如"孙一奎 vs 叶天士 治湿热对比"）
- **改动文件**：新增 `scripts/case_relations.py`、`rag-knowledge-base/case_relations.json`
- **验证**：`python scripts/case_relations.py --compare 孙一奎,叶天士 --tag 湿热`

## 三、运气推算引擎增强（P1-P2）

### OPT-06 运气病机自动推理链 `[P1]`
- **现状**：推算出运气结果后，病机分析靠 Agent 记忆推理
- **目标**：实现 `infer_pathogenesis(year)` -> 自动输出岁运病机、司天在泉民病、客主加临病机、推荐治法方剂
- **改动文件**：新增 `scripts/infer_pathogenesis.py`
- **验证**：`python scripts/infer_pathogenesis.py 2026 --json` 输出完整病机推理链

### OPT-07 运气时间轴可视化 `[P2]`
- **现状**：六步客主加临是文字描述
- **目标**：生成全年运气时间轴 HTML（12 个月 × 六步 × 客气/主气/运）
- **改动文件**：新增 `scripts/visualize_timeline.py`
- **验证**：生成 HTML 文件，含时间轴可视化

## 四、用户体验优化（P2-P3）

### OPT-08 CLI 交互增强 `[P2]`
- **现状**：CLI 是纯命令行式
- **目标**：`interactive` 模式做成菜单式 TUI，支持"输入症状 -> 推算运气 -> 检索医案 -> 给出分析"
- **改动文件**：`scripts/yunqi_cli.py`

### OPT-09 医案知识库浏览器 `[P2]`
- **现状**：2124 条医案只能命令行检索
- **目标**：生成静态 HTML 浏览器（按医家/朝代/病证分类浏览 + 全文搜索）
- **改动文件**：新增 `scripts/generate_case_browser.py`

### OPT-10 多语言医案摘要 `[P3]`
- **现状**：所有医案纯中文
- **目标**：为每条医案生成 `summary_en` 字段
- **改动文件**：各 `asset*_*.json`

## 五、工程质量（持续）

### OPT-11 测试覆盖率统计 `[P2]`
- 接入 `pytest-cov`，目标 ≥80%

### OPT-12 CI 自动化 `[P2]`
- 新增 `.github/workflows/ci.yml`，推送后自动跑全量测试

### OPT-13 医案去重检测 `[P2]`
- 跑 `source_quote` 相似度检测，标注可能跨库重复

### OPT-14 CHANGELOG 版本管理 `[P3]`
- 新增 `CHANGELOG.md`，语义化版本

## 六、reverse-skill 可借鉴亮点实施

> 借鉴 [reverse-skill](https://github.com/zhaoxuya520/reverse-skill) 的 Agent 行为工程实践，提升五运六气 Agent 的执行力和可靠性。

### OPT-16 防偷懒机制（Excuse Rebuttal Table）`[P1]`
- **现状**：agent 常见偷懒模式（凭记忆推算不调脚本、不查医案直接编、跳过免责声明）没有明确的反驳规则
- **目标**：在 `rules/agent-behavior.md` 新增"借口反驳表"，针对常见偷懒模式逐一反驳
- **改动文件**：`rules/agent-behavior.md`
- **验证**：`check_conformance.py` 通过 + `skill_e2e_test.py` 通过
- **示例**：
  | agent 借口 | 反驳 |
  |---|---|
  | "这步可以跳过" | 禁止跳过，输出理由等用户确认 |
  | "凭记忆推算就行" | MUST 调脚本，凭记忆推算违反 R2 |
  | "不查医案直接编" | MUST 调 rag_search，无医案佐证不得断言 |
  | "免责声明不用加" | 临床输出 MUST 附免责声明，违反 R1 |
  | "任务基本完成了" | 完成=全部自检清单打勾 |

### OPT-17 经验库前置查询 `[P1]`
- **现状**：经验库（`case-journal/field-journal/`）只在 fallback 时才查，不是每次任务开始前先查
- **目标**：将经验库查询提升为**每次任务开始前 MUST 先查**，命中则直接复用历史经验
- **改动文件**：`workflows/routing-contract.md`（NOW 步骤新增查经验库）、`prompts/system_prompt.md` §2.5
- **验证**：`skill_e2e_test.py` 通过
- **流程**：
  ```
  任务开始 -> 先查 field-journal/_index.md -> 命中则复用
           -> 未命中 -> 正常工具链 -> fallback 时沉淀新经验
  ```

### OPT-18 自我监督机制（每5步自检）`[P2]`
- **现状**：agent 可能反复调脚本但参数不对，没有自检机制
- **目标**：每 5 次工具调用暂停自检"在进步吗？重复了吗？"，同一方法失败 2-3 次换路
- **改动文件**：`rules/agent-behavior.md` 新增"自我监督"章节
- **验证**：`check_conformance.py` 通过

### OPT-19 联网搜索主动触发清单 `[P2]`
- **现状**：fallback 策略已有，但触发条件不够明确
- **目标**：在 `system_prompt.md` §2.6 新增"何时必须联网搜索"表格
- **改动文件**：`prompts/system_prompt.md` §2.6
- **验证**：`skill_e2e_test.py` 通过
- **示例**：
  | 场景 | 搜索什么 | 搜索后 |
  |---|---|---|
  | 知识库未命中的医家/方剂 | 医家理论/方剂解读 | 写入经验库 |
  | 用户要"现代研究" | 学术文献 | 写入经验库 |
  | 工具报错 | 错误信息+版本兼容 | 写入经验库 |

### OPT-20 完成清单结构化 `[P2]`
- **现状**：已有任务完成自检，但不够结构化
- **目标**：在 `workflows/routing-contract.md` 完善完成清单（报告/医案沉淀/经验回写/索引更新）
- **改动文件**：`workflows/routing-contract.md`
- **验证**：`check_conformance.py` 通过

### OPT-21 上下文注意力布局 `[P3]`
- **现状**：system_prompt 的 MUST/MUST NOT 散布在中间
- **目标**：将关键指令重排到首尾 10%（LLM 注意力最高区）
- **改动文件**：`prompts/system_prompt.md`
- **验证**：`skill_e2e_test.py` 通过

### 不再实施

| 优化项 | 原因 |
|---|---|
| OPT-10 多语言医案摘要 | 对 agent 对话能力提升有限，用户场景为中文 |
| OPT-11 测试覆盖率统计 | 工程侧，不直接影响用户体验 |
| OPT-02 embedding 语义检索 | 已移除，蒸馏库不需向量模型 |

## 实施记录

| 日期 | 优化项 | 状态 | 提交 |
|------|--------|------|------|
| 2026-08-11 | OPT-01 多库联合检索 | ✅ 已完成 | - |
| 2026-08-11 | OPT-02 embedding 语义检索 | ❌ 已移除（蒸馏库不需向量模型） | - |
| 2026-08-11 | OPT-03 按字段检索 | ✅ 已完成 | - |
| 2026-08-11 | OPT-06 运气病机自动推理链 | ✅ 已完成 | - |
| 2026-08-11 | OPT-12 CI 自动化 | ✅ 已有 | - |
| 2026-08-11 | OPT-07 运气时间轴可视化 | ✅ 已完成 | - |
| 2026-08-11 | OPT-13 医案去重检测 | ✅ 已完成（0.6%） | - |
| 2026-08-11 | OPT-09 医案知识库浏览器 | ✅ 已完成 | - |
| 2026-08-11 | OPT-Agent 医案白话解释能力 | ✅ 已完成 | - |
| 2026-08-11 | OPT-04 医案结构化字段 | ✅ 已完成（68.2%含药味） | - |
| 2026-08-11 | OPT-14 CHANGELOG 版本管理 | ✅ 已完成 | - |
| 2026-08-11 | OPT-05 医案关联图谱 | ✅ 已完成 | - |
| 2026-08-11 | OPT-08 CLI 交互增强 | ✅ 已完成 | - |
| 2026-08-11 | OPT-Fallback 联网搜索+经验库 | ✅ 已完成 | - |
| 2026-08-11 | OPT-16 防偷懒机制 | 待实施 | - |
| 2026-08-11 | OPT-17 经验库前置查询 | 待实施 | - |
| 2026-08-11 | OPT-18 自我监督机制 | 待实施 | - |
| 2026-08-11 | OPT-19 联网搜索触发清单 | 待实施 | - |
| 2026-08-11 | OPT-20 完成清单结构化 | 待实施 | - |
| 2026-08-11 | OPT-21 上下文注意力布局 | 待实施 | - |
| 2026-08-11 | OPT-10 多语言摘要 | ❌ 不做 | - |
| 2026-08-11 | OPT-11 测试覆盖率 | ❌ 不做 | - |
