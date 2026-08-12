# 优化文档：对标 nihaisha-nishi-tcm 的工程质量升级

> 日期：2026-08-12
> 依据：本仓库五个子系统深度重读报告 + GitHub 仓库 `JuneYaooo/nihaisha-nishi-tcm`（约 1.9k star）一手实现调研。
> 定位：独立优化建议稿，供人工审订后并入 `references/roadmap.md`；本文档不改写既有决策（含 P7-3 / P7-4 / P8-3 不采纳项）。

---

## 完成度总览

> 更新：2026-08-12。已落地 **5/8** 项，全部经远端 CI 确认。

| 优先级 | 事项 | 提交 | 状态 |
|--------|------|------|------|
| P0 | 核心算法正确性（checkPingqi + sweep + 平气基线） | `5d7eb09` | ✅ |
| P1-1 | 黄金基准持久化 + 修范围错配 | `ff447fa` | ✅ |
| P1-2 | 稳定引用 (yle:) + 可访问率门禁 | `a984227` | ✅ |
| P2-2 | 免责声明单一权威来源 | `73e0172` | ✅ |
| P1-4 | 字形归一化检索 | `7ae45d6` | ✅ |
| P1-3 | 按需渐进加载薄索引 | — | ⏳ 未做 |
| P2-1 | 答案层断言 | — | ⏳ 未做 |
| P3 | 跨平台 / openai.yaml / MCP 审计 | — | ⏳ 未做 |

剩余可选：**P1-3**（asset18–32 大模块薄索引）、**P2-1**（答案层断言）、**P3**（跨平台）。

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

- [x] **修复 `scripts/lib/yunqi_data.js` 的 `checkPingqi` 漏判「不及同气相助」**（提交 `5d7eb09` ✅）
  - 现象（已实测）：Python `yunqi_data.py:206-207` 含 `sitian_elem == dayun → 平气`；JS `yunqi_data.js:172-180` 只实现 `!taiguo && sheng(sitian, dayun)`，漏掉「不及之年五行同气相助」。
  - 波及干支（6 个）：`乙卯、乙酉`（金不及·阳明燥金司天）、`丁巳、丁亥`（木不及·厥阴风木司天）、`己丑、己未`（土不及·太阴湿土司天）。
  - 现状：`compare_py_js_yunqi.py` 默认 5 个日期（2025/2026 前后）恰好都不落在这 6 干支上，**CI 全绿但 bug 真实存在**。
  - 结果：JS `checkPingqi` 补「规则二A 不及同气相助」，与 Python 三条规则对齐，整甲子 sweep 60/60 通过。
- [x] **给 `compare_py_js_yunqi.py` 加整甲子区间全字段 sweep**（提交 `5d7eb09` ✅）
  - 新增 `--sweep` 遍历 1984—2043 全部 60 干支，对 `CRITICAL_PATHS` 全字段对比；接入 CI。实测可将 6 个 bug 干支一网打尽（修复前 sweep 精确报出 6 项 `tong_hua.pingqi` 不一致）。
- [x] **`verify_cross_check.py` 补平气基线**（提交 `5d7eb09` ✅）
  - 新增 `verify_pingqi()`：9 个独立于算法的经典干支基线（平气正例 5 + 反例 4），源自 `modules/yunqi-calc/references/taiguo_buji.md`（《素问·五常政大论》《素问·六微旨大论》及王冰/张介宾注家）。验证项 52→61，61/61 通过。
- [ ] （待定）收敛两套日期归一化
  - `calculate_yunqi_api._resolve_date`（裸年份 → `-07-01`）与 `_common.resolve_year_or_date`（→ `-07-08`）行为不一致，易埋坑。（**未做**，不影响其它）

---

## P1：检索工程质量（nihaisha 可复用的最高价值）

### P1-1 黄金基准集持久化 + 修正范围错配 ✅

> 依据：nihaisha `evals/*.jsonl` + `reference_targets` 字段。
> 状态：已完成（提交 `ff447fa`）。

- [x] 将 `scripts/eval_retrieval_quality.py` 内联的 golden 集落成 `tests/golden/retrieval_golden.json`（JSON，32 类 / 1994 条医案），纳入 git 追踪。
- [x] 修正**基准与检索范围错配**：golden 含 asset18–32，检索却用默认范围。方案①已做——`evaluate_recall` 检索范围与 golden 同源覆盖（`_assets_of`）；未改动 `_default_asset_keys()`（保留产品默认范围语义）。
- [x] 命中 ID 提取改为结构化字段：改用 `hit['id']`（entry_id），不再从 `title.split("_")` 解析。
- [x] 顺带修复 `rag_search._entry_id` 优先级：把 `case_id/entry_id` 提到 `code` 之前，消除「医案的 rag_key（病证名非唯一）」与「asset9 岁图的 code（非唯一）」导致的 id 撞车。命中匹配、精确 key 检索、字段检索统一命中唯一标识。
- [x] 新增 `--write-golden`（固化基准）与 `--check-golden`（漂移校验，接入 CI）。
- [x] 指标改善：precision@5 87.5%→94.4%、precision@10 78.1%→93.1%、recall@20 39.3%→73.6%；痹证/儿科假阴性（P@10=0%）消除。
- [ ] （待定）指标口径加注「pool 内命中 ≠ 全库召回率」，防误读。

### P1-2 分层证据引用 + stable doc_id ✅

> 依据：nihaisha `pdf-evidence:<doc_id>#p<page>` / `text-evidence:<doc_id>#s<section>` + `source-manifest.json`。
> 状态：已完成（提交 `a984227`）。

- [x] 稳定引用语法定为 `yle:<asset文件名>:<entry_id>`（例 `yle:asset13_gujin_an_cases:gujin_001`，`yle:asset9_cases:shengji_jiazi`）。asset 文件名为稳定文档 ID；entry_id 为条目稳定唯一键。
- [x] `rag_search` 四个组装点（search / search_by_field / lookup_key / 各自 hit）统一输出 `ref` 字段（`make_ref`）。
- [x] 新增 `scripts/resolve_ref.py`：解析 `yle:` 引用（`resolve_ref`）、批量统计可访问率、`--list-assets`、`--selfcheck` 自测门禁。
- [x] `_entry_id` 改为稳定唯一键（case_id/entry_id 优先），全 asset 除 terminology（语义术语表，非定位目标）外 id 唯一。
- [x] 引用可访问率纳入 CI：`resolve_ref.py --selfcheck`（95/95=100%）。
- [ ] （待定）把「强制摘录 + 稳定引用同时出现」写入 `rules/output.md` / `case-journal/precedent-disclaimer.md`，作为 Agent 回答格式规则。

### P1-3 按需渐进加载 + 强制联动条件

> 依据：nihaisha `references/index.md` 的「文件 / 用途 / 何时打开」三列表格。

- [ ] 在 `rag-knowledge-base` 大模块（尤其 asset18–32 医案库）上方加「入口 → guide → 是否强制加载」薄索引，避免整包载入重量级条目。
- [ ] 为高风险类问题定义「强制联动」：如深针 / 急症 → 必读对应 safety 模块，不因主模块无命中而省略（对标 nihaisha 针灸 safety 模块强制加载）。

### P1-4 检索健壮性：字形归一化 + 检索词压缩 ✅

> 状态：已完成（提交 `7ae45d6`）。

- [x] 在 `rag_search.py` 增加 **`_NORM_MAP` + `_normalize()`**（NFKC + 70 项异体/繁简映射：針/鍼→针、證/証→证、氣→气、陰→阴、傷→伤、脅→胁、痺→痹 等），模型无关、离线可跑。
- [x] `_expand_synonyms`：查询词并入归一化形式作 OR 候选；同义词扩展改以「归一化简体」为主键，使繁体/异体查询（如 `痺證`）与简体（`痹证`）享受一致的医案同义词扩展。
- [x] `score_entry_synonym` / `score_entry`：命中判定加入归一化比对（text_all_norm / title_norm / 各字段 val_norm），条目内异体写法也能命中。
- [x] `rag_semantic.py` `_tokenize`：分词前先归一化，n-gram 语义检索同样支持繁简互通。
- [x] 验证：11 组简体/异体关键词检索结果逐组一致；语义检索 4 组一致；`eval_retrieval_quality --check-golden`、`resolve_ref --selfcheck`、`test_package_and_rag`、full_regression、routing/conformance 全 PASS。
- [ ] `--show-terms`（暴露检索词歧义消解过程）——未做，后续可选。
- [ ] （可选）两段式检索：主证据命中后自动补一轮「经典/注家」检索——未做，后续可选。

---

## P2：答案评测与安全可观测

### P2-1 答案评测增强（区别于 P7-3，需向读者说明）

> ⚠️ **与 P7-3「skill 级 evals — 不采纳」的关系**：P7-3 拒的是官方 skill 规范对 `evals/` 目录的形式要求（本项目 200+ 项 CI 断言已超）。本项不新增 evals 目录，而是**给既有 `report_quality_gate.py` / `verify_cross_check.py` 补"答案层"断言**，不重复不冲突。

- [ ] 给临床输出评测扩展 nihaisha 的题格字段：`expected_behavior(answer/clarify/abstain/safe_redirect)` + `forbidden_content` + `required_checks`，用于断言「MUST NOT 给剂量 / 必带免责」是否真成立。
- [ ] 增加 `pair_id` 鲁棒性配对：同类问题多次提问回答一致性（对标 nihaisha 62.5% 的坑，提醒规避）。
- [ ] 能力边界通过率：故意问出域题，断言 Agent **不越界**（对标 nihaisha 边界通过率仅 8.3%，说明"收紧边界"是刻意设计而非缺陷）。

### P2-2 免责声明单一权威来源 ✅

> 依据：现 DISCLAIMER / CLINICAL_SAFETY_NOTICE / EMERGENCY_NOTICE 在 4+ 文件硬拷贝重复，易措辞漂移。
> 状态：已完成（提交 `73e0172`）。

- [x] 三类声明收敛为单一权威源 `scripts/_safety_text.py`（纯常量、零依赖）：三件套 DISCLAIMER / CLINICAL_SAFETY_NOTICE / EMERGENCY_NOTICE + `EMERGENCY_NOTICE_PLAIN`（门禁用）+ `CONTEXT_DISCLAIMERS`（医案/体质/气象/时间轴场景变体）+ 三个单句 NOTICE。
- [x] `yunqi_report.py` / `clinical_safety.py` / `generate_html_report.py` / `visualize_timeline.py` / `generate_case_browser.py` / `personal_yunqi_profile.py` / `weather_alignment.py` 均改 import，删除本地硬拷贝。
- [x] `report_quality_gate.py`：删除未使用的死代码 `EMERGENCY_NOTICE`；`demo_text()` 改由权威源拼接，保证与真实报告一致。
- [x] 输出逐字校验：HTML 免责、case browser、timeline、practitioner 报告质量门禁（含快照比对）均与原一致，无措辞漂移、无重复拼接。
- [x] README/README_EN 脚本数 42→43、目录注释同步。
- [ ] 剂量脱敏：`redact_dosage` 正则对中文剂量表达（如「一两三」「二钱半」）有漏网风险（**未做**，独立于本项）。

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

| 序 | 事项 | 对应章节 | 状态 | 收益 | 成本 |
|----|------|---------|------|------|------|
| 1 | 修 `checkPingqi` JS bug + 整甲子 sweep | P0 | ✅ 完成（`5d7eb09`） | 高（正确性） | 低 |
| 2 | 黄金基准持久化 + 修范围错配 | P1-1 | ✅ 完成（`ff447fa`） | 高（评测可信度） | 中 |
| 3 | stable doc_id + 引用语法 + 可访问率门禁 | P1-2 | ✅ 完成（`a984227`） | 高（临床溯源） | 中 |
| 4 | 免责声明单一权威来源 | P2-2 | ✅ 完成（`73e0172`） | 中（防漂移） | 低 |
| 6 | 字形归一化 / 检索词压缩 | P1-4 | ✅ 完成（`7ae45d6`） | 中（白话提问） | 低 |
| 5 | 渐进加载薄索引 | P1-3 | ⏳ 未做（后续） | 中（context 优化） | 中 |
| 7 | 答案层断言（替代 evals） | P2-1 | ⏳ 未做（后续） | 中（安全可观测） | 中 |
| 8 | openai.yaml / 跨平台 / MCP 审计 | P3 | ⏳ 未做（后续） | 低（可移植） | 低 |

---

## 与既有文档的关系

- **不重复** `roadmap.md`：本文档是「依据 + 方案」，P0 是深读实证、P1–P3 是 nihaisha 对标建议；经审订后按所属 P 级并入 roadmap 的待办勾选。
- **不冲突** 既有不采纳决策（P7-3 / P7-4 / P8-3）。
- **需同步**：本篇 P1-1 若采纳「asset18–32 纳入默认检索」，将改变 `index.json` 归并口径与 `module-index.md` / README asset 表；README 数字由 `scripts/check_readme_numbers.py` 强制一致。