# 优化文档：对标 nihaisha-nishi-tcm 的工程质量升级

> 日期：2026-08-12
> 依据：本仓库五个子系统深度重读报告 + GitHub 仓库 `JuneYaooo/nihaisha-nishi-tcm`（约 1.9k star）一手实现调研。
> 定位：独立优化建议稿，供人工审订后并入 `references/roadmap.md`；本文档不改写既有决策（含 P7-3 / P7-4 / P8-3 不采纳项）。

---

## 完成度总览

> 更新：2026-08-12。8 项全部完成经验证。各 P 项所列「待定/可选」子项已一并收齐（提交 `99414bf`），优化文档与代码状态一致。

| 优先级 | 事项 | 提交 | 状态 |
|--------|------|------|------|
| P0 | 核心算法正确性（checkPingqi + sweep + 平气基线） | `5d7eb09` | ✅ |
| P1-1 | 黄金基准持久化 + 修范围错配 | `ff447fa` | ✅ |
| P1-2 | 稳定引用 (yle:) + 可访问率门禁 | `a984227` | ✅ |
| P2-2 | 免责声明单一权威来源 | `73e0172` | ✅ |
| P1-4 | 字形归一化检索 | `7ae45d6` | ✅ |
| P1-3 | 医案渐进加载薄索引 | `c2068d6` | ✅ |
| P2-1 | 答案层断言（+ pair_id / 能力边界） | `a49891e` | ✅ |
| P3 | 跨平台：install.py 加 Codex | `18c7bb4` | ✅ 完成（mcps 已澄清为本地缓存） |

**一并收齐的待定/可选子项**（提交 `99414bf`）：两套日期归一化收敛 · 中文剂量脱敏 · 指标口径注释 ·
引用规则写入 rules/output.md · `--show-terms` · 两段式检索（`--include-extra`）· pair_id 鲁棒性 · 能力边界。

剩余可选补强（不涉及正确性/安全，可为空）：**openai.yaml**（多宿主结构化声明）、**轻量依赖原则注释**。（`mcps/` 已澄清为本地缓存，不处理。）

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
- [x] **收敛两套日期归一化**：`calculate_yunqi_api._resolve_date` 复用 `_common.resolve_year_or_date`，裸年份统一到 `-07-08`（提交 `99414bf`）。
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
- [x] 指标口径注明：`eval_retrieval_quality` 明确 precision/recall 是「体系内(eval 选定 asset 子集)检索质量」，≠ 全 32 asset 全库召回率，防误读（提交 `99414bf`）。

### P1-2 分层证据引用 + stable doc_id ✅

> 依据：nihaisha `pdf-evidence:<doc_id>#p<page>` / `text-evidence:<doc_id>#s<section>` + `source-manifest.json`。
> 状态：已完成（提交 `a984227`）。

- [x] 稳定引用语法定为 `yle:<asset文件名>:<entry_id>`（例 `yle:asset13_gujin_an_cases:gujin_001`，`yle:asset9_cases:shengji_jiazi`）。asset 文件名为稳定文档 ID；entry_id 为条目稳定唯一键。
- [x] `rag_search` 四个组装点（search / search_by_field / lookup_key / 各自 hit）统一输出 `ref` 字段（`make_ref`）。
- [x] 新增 `scripts/resolve_ref.py`：解析 `yle:` 引用（`resolve_ref`）、批量统计可访问率、`--list-assets`、`--selfcheck` 自测门禁。
- [x] `_entry_id` 改为稳定唯一键（case_id/entry_id 优先），全 asset 除 terminology（语义术语表，非定位目标）外 id 唯一。
- [x] 引用可访问率纳入 CI：`resolve_ref.py --selfcheck`（95/95=100%）。
- [x] 「强制摘录 + 稳定引用同时出现」写入 `rules/output.md`（yle: 引用格式），作为 Agent 回答格式规则（提交 `99414bf`）。

### P1-3 按需渐进加载 + 强制联动条件 ✅

> 依据：nihaisha `references/index.md` 的「文件 / 用途 / 何时打开」三列表格。
> 状态：已完成。

- [x] 新增 `scripts/cases_routing.py`：把 `yunqi_medical_cases_guide.md` 的病证→医案库路由表固化为**可编程薄索引**（零依赖、确定性）。Agent 检索前先调该脚本拿候选库清单，再只开命中库 → 渐进加载，避免整包 22 部医案库(asset9/11-32)撑爆上下文。
- [x] 接口：`--syndrome <病证>`（含包含匹配）→ 首选 + 补充 + 强制联动库；`--rag-key <key>` → 翻译成病证倾向 + 推荐库（14 组 rag_key 映射，源自 guide 第五节）；`--list-assets`（23 库速查）；`--json` / `--force-load`（大库保底）。
- [x] 高风险病证强制联动：`FORCE_LOAD_SYNDROMES` — 温疫/瘟疫/大头瘟/痘疫/痈疽自动附加强制库（如痈疽→追加 asset30 立斋外科）。
- [x] SKILL.md 新增「医案渐进加载（P1-3）」工具行；routing.yaml `case-journal` 任务 route 改为"先 cases_routing 得清单再按需检索"；sync_routing 重新生成一致。
- [x] CI 新增 `cases_routing.py` 四场景冒烟步骤。
- [x] README/EN 脚本数 43→44、CI 测试 34→35、目录注释同步；全回归 PASS。

### P1-4 检索健壮性：字形归一化 + 检索词压缩 ✅

> 状态：已完成（提交 `7ae45d6`）。

- [x] 在 `rag_search.py` 增加 **`_NORM_MAP` + `_normalize()`**（NFKC + 70 项异体/繁简映射：針/鍼→针、證/証→证、氣→气、陰→阴、傷→伤、脅→胁、痺→痹 等），模型无关、离线可跑。
- [x] `_expand_synonyms`：查询词并入归一化形式作 OR 候选；同义词扩展改以「归一化简体」为主键，使繁体/异体查询（如 `痺證`）与简体（`痹证`）享受一致的医案同义词扩展。
- [x] `score_entry_synonym` / `score_entry`：命中判定加入归一化比对（text_all_norm / title_norm / 各字段 val_norm），条目内异体写法也能命中。
- [x] `rag_semantic.py` `_tokenize`：分词前先归一化，n-gram 语义检索同样支持繁简互通。
- [x] 验证：11 组简体/异体关键词检索结果逐组一致；语义检索 4 组一致；`eval_retrieval_quality --check-golden`、`resolve_ref --selfcheck`、`test_package_and_rag`、full_regression、routing/conformance 全 PASS。
- [x] `--show-terms`：打印检索词歧义消解（原词→归一化→同义词 OR 组），服务白话提问（提交 `99414bf`）。
- [x] 两段式检索：`--include-extra` 主检索命中后自动按归一化核心词补一轮更宽 OR 检索（默认关，保持默认 JSON 向后兼容；提交 `99414bf`）。

---

## P2：答案评测与安全可观测

### P2-1 答案评测增强（区别于 P7-3，需向读者说明）✅

> ⚠️ **与 P7-3「skill 级 evals — 不采纳」的关系**：P7-3 拒的是官方 skill 规范对 `evals/` 目录的形式要求（本项目 200+ 项 CI 断言已超）。本项不新增 evals 目录，而是**扩展现有 `report_quality_gate.py` 补"答案层"断言**，不重复不冲突。

- [x] `report_quality_gate.py` 新增 `check_answer_layer(text, case)`：按用例题格做语义判定，而非只看关键词。`expected_behavior(answer/clarify/abstain/safe_redirect)` + `forbidden_content` + `required_checks`，断言「MUST NOT 给剂量 / 必带免责」是否真成立。
- [x] 新增 `_CHINESE_DOSE_RE`：覆盖 `DOSE_PATTERNS` 抓不到的中文数字剂量（一两/三钱/二钱半/每日二次/服多次），且**不误伤药名**（附子须辨证正常提及不算剂量）。
- [x] 行为判定：`abstain`/`safe_redirect` 为强制行为——该拒未拒、该转介未转介判 FAIL（不再只是 warning）；`clarify` 信息不足应澄清。
- [x] 新增 `tests/test_answer_layer.py`：16 条答案层断言用例（剂量禁区/行为判定/必备要素），融入 CI。全回归 PASS，纯增量不改 `check_report`。
- [x] `pair_id` 鲁棒性配对：`check_pair_consistency` 判断同一问题多轮是否一致遵守行为边界（提交 `99414bf`）。
- [x] 能力边界通过率：`check_boundary` 判定出域问题「应 abstain/redirect，不越界强行答」（提交 `99414bf`）。

### P2-2 免责声明单一权威来源 ✅

> 依据：现 DISCLAIMER / CLINICAL_SAFETY_NOTICE / EMERGENCY_NOTICE 在 4+ 文件硬拷贝重复，易措辞漂移。
> 状态：已完成（提交 `73e0172`）。

- [x] 三类声明收敛为单一权威源 `scripts/_safety_text.py`（纯常量、零依赖）：三件套 DISCLAIMER / CLINICAL_SAFETY_NOTICE / EMERGENCY_NOTICE + `EMERGENCY_NOTICE_PLAIN`（门禁用）+ `CONTEXT_DISCLAIMERS`（医案/体质/气象/时间轴场景变体）+ 三个单句 NOTICE。
- [x] `yunqi_report.py` / `clinical_safety.py` / `generate_html_report.py` / `visualize_timeline.py` / `generate_case_browser.py` / `personal_yunqi_profile.py` / `weather_alignment.py` 均改 import，删除本地硬拷贝。
- [x] `report_quality_gate.py`：删除未使用的死代码 `EMERGENCY_NOTICE`；`demo_text()` 改由权威源拼接，保证与真实报告一致。
- [x] 输出逐字校验：HTML 免责、case browser、timeline、practitioner 报告质量门禁（含快照比对）均与原一致，无措辞漂移、无重复拼接。
- [x] README/README_EN 脚本数 42→43、目录注释同步。
- [x] 剂量脱敏：`redact_dosage` 补中文数字剂量正则（一两/三钱/二钱半/每日二次），阿拉伯+中文都换占位符——安全优先宁多勿漏；纯药名（附子须辨证）不误伤（提交 `99414bf`）。

---

## P3：跨平台与工程可移植（低优先）

- [x] **`install.py --link-global` 增加 Codex 目标**（提交 `~/.codex/skills/`，支持 `CODEX_HOME` 环境变量优先）——「链接仓库→agent 帮忙装」从 Claude+Cursor 扩到 3 宿主。已隔离 HOME 实测三宿主链接全部创建成功。
- [x] `one-line-install.md` 宿主表补 Codex 目标路径。
- [ ] （可选）补 `agents/openai.yaml` 风格结构化 agent 声明——本项目已走 client-neutral（AGENTS.md 平台中立入口），openai.yaml 仅作按需可选，不强制。
- [ ] 明确把「轻量零依赖」固化为架构原则：核心仅 `lunar-python`，重依赖（若未来引向量/embedding）一律进 optional extras。
- [x] ~~审计 `mcps/`~~ **已澄清，不再处理**：`mcps/` 是**本地 Claude Code 运行时生成的 MCP 工具 schema 缓存**（浏览器自动化/Bazi/context7 等），非项目资产；已被 `.gitignore`（第 17 行 `mcps/`）排除，从不进入 git。早前「可接入 mcps/Bazi」的描述系误判，特此更正：**勿将其视为可复用资产**。用户已确认此目录不用管理。

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
| 5 | 渐进加载薄索引 | P1-3 | ✅ 完成（`c2068d6`） | 中（context 优化） | 中 |
| 7 | 答案层断言（替代 evals） | P2-1 | ✅ 完成（`a49891e`） | 中（安全可观测） | 中 |
| 8 | install.py 加 Codex / openai.yaml 可选 / 轻量原则 | P3 | ✅ install.py 完成（openai.yaml/轻量原则为可选补强） | 低（可移植） | 低 |

---

## 与既有文档的关系

- **不重复** `roadmap.md`：本文档是「依据 + 方案」，P0 是深读实证、P1–P3 是 nihaisha 对标建议；经审订后按所属 P 级并入 roadmap 的待办勾选。
- **不冲突** 既有不采纳决策（P7-3 / P7-4 / P8-3）。
- **需同步**：本篇 P1-1 若采纳「asset18–32 纳入默认检索」，将改变 `index.json` 归并口径与 `module-index.md` / README asset 表；README 数字由 `scripts/check_readme_numbers.py` 强制一致。