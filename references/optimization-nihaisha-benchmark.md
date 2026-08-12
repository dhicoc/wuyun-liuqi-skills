# 优化文档：对标 nihaisha-nishi-tcm 的工程质量升级

> 日期：2026-08-12
> 依据：本仓库五个子系统深度重读报告 + GitHub 仓库 `JuneYaooo/nihaisha-nishi-tcm`（约 1.9k star）一手实现调研。
> 定位：独立优化建议稿，供人工审订后并入 `references/roadmap.md`；本文档不改写既有决策（含 P7-3 / P7-4 / P8-3 不采纳项）。

---

## 〇、本文档要解决的问题

对标外部仓库后，本项目的**相对长板**是：推算确定性、routing 单一真相源、三层临床安全、自进化数据闭环、轻量零依赖检索。

nihaisha 无法替代的优势集中在**检索型 Agent 的工程质量**，本项目的相对短板与之一一对应：

| 维度 | 本项目现状 | nihaisha 做法 | 差距 |
|------|-----------|--------------|------|
| 答案评测 | 仅检索指标（precision/recall） | 六维答案评测 + 双模型盲评 | 缺答案层 |
| 基准集版本化 | golden 内联生成 | `.jsonl` 基准入库 + SHA-256 | 无法版本化 |
| 证据溯源 | 免责声明（prompt 层） | stable doc_id + 统一引用语法 | 缺机器可校验 |
| 按需加载 | routing 一层 required_reads | 三列表格 + 强制联动条件 | 缺多级渐进 |
| 检索健壮性 | 关键词/ngram，无归一化 | 检索词压缩 + 字形归一化 | 缺歧义消解 |

---

## P0：核心算法正确性（深读实证，必须先修）

> 非对标建议，是本地深读的**实证产出**。其余 P 级均源自 nihaisha 对标。

- [ ] **修复 `scripts/lib/yunqi_data.js` 的 `checkPingqi` 漏判「不及同气相助」**
  - 现象（已实测）：Python `yunqi_data.py:206-207` 含 `sitian_elem == dayun → 平气`；JS `yunqi_data.js:172-180` 只实现 `!taiguo && sheng(sitian, dayun)`，漏掉「不及之年五行同气相助」。
  - 波及干支（6 个）：`乙卯、乙酉`（金不及·阳明燥金司天）、`丁巳、丁亥`（木不及·厥阴风木司天）、`己丑、己未`（土不及·太阴湿土司天）。
  - 现状：`compare_py_js_yunqi.py` 默认 5 个日期（2025/2026 前后）恰好都不落在这 6 干支上，**CI 全绿但 bug 真实存在**。
- [ ] **给 `compare_py_js_yunqi.py` 加整甲子区间全字段 sweep**
  - 每个干支取代表年（或直接 1900–2200 全区间），对 `CRITICAL_PATHS` 全字段对比，property-style 一网打尽，而非抽样 5 个日期。
- [ ] **`verify_cross_check.py` 补平气基线**
  - 现基线只含天符/岁会/太乙天符/同天符/同岁会/正化对化/齐化兼化，`check_pingqi` 三条子规则全凭 docstring 自证，无经典案源核对。
- [ ] （建议）收敛两套日期归一化
  - `calculate_yunqi_api._resolve_date`（裸年份 → `-07-01`）与 `_common.resolve_year_or_date`（→ `-07-08`）行为不一致，易埋坑。

---

## P1：检索工程质量（nihaisha 可复用的最高价值）

### P1-1 黄金基准集持久化 + 修正范围错配

> 依据：nihaisha `evals/*.jsonl` + `reference_targets` 字段。

- [ ] 将 `scripts/eval_retrieval_quality.py` 内联的 golden 集落成 `tests/golden/` 下**独立版本化文件**（JSONL），加入 git 追踪。
- [ ] 修正**基准与检索范围错配**：现在 golden 用 `load_all_cases` 加载全部 `asset*_cases.json`（含 asset18–32），但 `search()` 用默认资产范围（**不含** asset18–32），导致来自 asset18–32 的 golden 必然不可命中，系统性拉低 recall / 抬高零命中。
  - 方案二选一：① 评测显式覆盖全 asset 范围；② 把 asset18–32 纳入 `_default_asset_keys()` 默认检索范围（后者更利终端）。
- [ ] 命中 ID 提取改为结构化字段，不再依赖 `title.split("_")`。
- [ ] 指标注明口径：如 nihaisha 明确「`pool_hit`/`pool_ndcg` 只描述证据池内排序，≠全库召回率」，避免指标被误读。

### P1-2 分层证据引用 + stable doc_id

> 依据：nihaisha `pdf-evidence:<doc_id>#p<page>` / `text-evidence:<doc_id>#s<section>` + `source-manifest.json`。

- [ ] 为 `rag-knowledge-base` 各 asset 引入 **stable doc_id**（`source-manifest.json` 维护 文档ID → 文件/条目 映射），供报告与检索稳定引用。
- [ ] 制定统一引用语法并写入回答格式（如 `yle:<doc_id>#<entry_id>`），强制「摘录 + 稳定引用」同时出现。
- [ ] 把「临床必带出处」从 prompt 约束升级为**可客观统计**的「引用可访问率」，纳入 CI 门禁（呼应你 `rules/medical-safety.md` 的 MUST 条）。

### P1-3 按需渐进加载 + 强制联动条件

> 依据：nihaisha `references/index.md` 的「文件 / 用途 / 何时打开」三列表格。

- [ ] 在 `rag-knowledge-base` 大模块（尤其 asset18–32 医案库）上方加「入口 → guide → 是否强制加载」薄索引，避免整包载入重量级条目。
- [ ] 为高风险类问题定义「强制联动」：如深针 / 急症 → 必读对应 safety 模块，不因主模块无命中而省略（对标 nihaisha 针灸 safety 模块强制加载）。

### P1-4 检索健壮性：字形归一化 + 检索词压缩

- [ ] 在 `rag_search.py` / `rag_semantic.py` 增加**字形归一化**（NFKC + 兪/腧→俞、鍼/針→针 等异体统一），模型无关、离线可跑。
- [ ] 借鉴 nihaisha `--show-terms`：暴露检索词如何被歧义消解（强 token 优先、去口语填充词、复合词分解），服务白话提问。
- [ ] （可选）两段式检索：主证据命中后自动补一轮「经典/注家」检索，与你的引经据典需求同构。

---

## P2：答案评测与安全可观测

### P2-1 答案评测增强（区别于 P7-3，需向读者说明）

> ⚠️ **与 P7-3「skill 级 evals — 不采纳」的关系**：P7-3 拒的是官方 skill 规范对 `evals/` 目录的形式要求（本项目 200+ 项 CI 断言已超）。本项不新增 evals 目录，而是**给既有 `report_quality_gate.py` / `verify_cross_check.py` 补"答案层"断言**，不重复不冲突。

- [ ] 给临床输出评测扩展 nihaisha 的题格字段：`expected_behavior(answer/clarify/abstain/safe_redirect)` + `forbidden_content` + `required_checks`，用于断言「MUST NOT 给剂量 / 必带免责」是否真成立。
- [ ] 增加 `pair_id` 鲁棒性配对：同类问题多次提问回答一致性（对标 nihaisha 62.5% 的坑，提醒规避）。
- [ ] 能力边界通过率：故意问出域题，断言 Agent **不越界**（对标 nihaisha 边界通过率仅 8.3%，说明"收紧边界"是刻意设计而非缺陷）。

### P2-2 免责声明单一权威来源

> 依据：现 DISCLAIMER / CLINICAL_SAFETY_NOTICE / EMERGENCY_NOTICE 在 4+ 文件硬拷贝重复，易措辞漂移。

- [ ] 将三类声明收敛为单一权威源（如 `rules/medical-safety.md` 或 `scripts/_safety.py`），各报告模块 import / 引用，杜绝漂移。
- [ ] 剂量脱敏：`redact_dosage` 正则对中文剂量表达（如「一两三」「二钱半」）有漏网风险，属 MUST NOT 红线，建议默认「含方药剂量即拒绝输出」而非仅正则替换（可在 `report_quality_gate` 强制）。

---

## P3：跨平台与工程可移植（低优先）

- [ ] 补一个 `agents/openai.yaml` 风格的结构化 agent 声明（`interface/policy/default_prompt`），供非 Claude 宿主复用；不引 MCP、不自动下载。
- [ ] 明确把「轻量零依赖」固化为架构原则：核心仅 `lunar-python`，重依赖（若未来引向量/embedding）一律进 optional extras（对标 nihaisha `pyproject.toml` 仅 `requests` + extras）。
- [ ] 审计 `mcps/` 7 个 MCP schema：当前**全部未接线**。若要打通「八字时间 → 干支 → 运气」可接入 `mcps/Bazi`，否则在文档标注为「休眠资产」避免误用。

---

## 不采纳 / 不建议跟进

延续项目「不采纳」惯例，逐条给出理由：

| 方向 | 理由 |
|------|------|
| 给 RAG 上向量库/embedding | nihaisha 自己的评测显示引用溯源项 RAG 反落后（85.3% vs 91.3%），印证轻量路线；本项目已蒸馏，ngram 余弦够用 |
| 新增独立 `evals/` 目录 | 与 P7-3 一致，避免与既有 tests/ 重复；改进走 P2-1「答案层断言」 |
| 照搬 nihaisha 的 `install_as_skill.sh` overwrite 无回滚逻辑 | 本项目 `install.py --link-global` 用 junction + 覆盖保护更稳，不回退 |
| 引入 RAG/图谱作为默认模式 | 体量大、edge-case 多、下架风险高；轻量模块为默认是正确取舍 |

---

## 落地优先级速览

| 序 | 事项 | 对应章节 | 收益 | 成本 |
|----|------|---------|------|------|
| 1 | 修 `checkPingqi` JS bug + 整甲子 sweep | P0 | 高（正确性） | 低 |
| 2 | 黄金基准持久化 + 修范围错配 | P1-1 | 高（评测可信度） | 中 |
| 3 | stable doc_id + 引用语法 + 可访问率门禁 | P1-2 | 高（临床溯源） | 中 |
| 4 | 免责声明单一权威来源 | P2-2 | 中（防漂移） | 低 |
| 5 | 渐进加载薄索引 | P1-3 | 中（context 优化） | 中 |
| 6 | 字形归一化 / 检索词压缩 | P1-4 | 中（白话提问） | 低 |
| 7 | 答案层断言（替代 evals） | P2-1 | 中（安全可观测） | 中 |
| 8 | openai.yaml / 跨平台 / MCP 审计 | P3 | 低（可移植） | 低 |

---

## 与既有文档的关系

- **不重复** `roadmap.md`：本文档是「依据 + 方案」，P0 是深读实证、P1–P3 是 nihaisha 对标建议；经审订后按所属 P 级并入 roadmap 的待办勾选。
- **不冲突** 既有不采纳决策（P7-3 / P7-4 / P8-3）。
- **需同步**：本篇 P1-1 若采纳「asset18–32 纳入默认检索」，将改变 `index.json` 归并口径与 `module-index.md` / README asset 表；README 数字由 `scripts/check_readme_numbers.py` 强制一致。