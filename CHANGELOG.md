# Changelog

本文件记录五运六气技能包的重要变更，遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [0.3.3] - 2026-08-14

### Changed
- **术语统一为《素问》原字「太一天符」**：代码输出展示名（推算 API、报告、RAG 索引 flag、思想图、苏格拉底提问）、对外术语与自撰文档（teaching module、SKILL.md、yunqi_tonghua.md / yunqi_hebing.md / jieqi.md / taiguo_bingji.md 及蒸馏指南自有表述）统一改用《素问》原字「太一天符」（一）；变量名 `TAIYI_TIANFU_YEARS` 等保持不变。
- **修正引文硬错**：`yunqi_hebing.md` 原误将《素问·六微旨大论》"太一天符为贵人" 写作「太乙天符」（注本用字），已改回《素问》原字；`teaching-modules/天符岁会.md` 引文补正——「三合为治」出自《素问·天元纪大论》（转引六微旨），「太一天符为贵人」明确归《六微旨大论》。
- **保留项**：历史文献原文（literature/）、以《医宗金鉴》为权威源的 `verify_cross_check.py`、张介宾/王旭高等注家原文引述，仍忠实保留「太乙天符」（乙），不改动原典；`terminology.json` 同时保留 `太乙天符`/`太一天符` 双检索入口；`routing.yaml` 增加「太一天符」短语且保留「太乙天符」以匹配用户习惯输入。

### Docs
- `tests/verify_against_suwen.py` 的类别键统一为「太一天符（素问原字，后世注本作太乙天符）」，与《素问》口径一致。

## [0.3.2] - 2026-08-14

### Added
- **《素问》独立文献交叉校验**：新增 `tests/verify_against_suwen.py`，以《黄帝内经·素问》运气七篇**原文枚举**（《六元正纪大论》《六微旨大论》含 file:line 出处）为唯一权威源，对全甲子（1984–2043）跑算法输出做五类（天符/岁会/太乙天符即素问原字「太一天符」/同天符/同岁会）全量逆向断言，证明算法与《素问》逐类恰好相等（无多无少）。
  - 与 `scripts/verify_cross_check.py`（权威源为《医宗金鉴·运气要诀》注本）相互独立，构成「算法 == 素问 == 医宗金鉴」三重互证，已接入 CI（步骤 `Suwen (素问) independent literature cross-check`）。
  - 5/5 类通过：天符 12 / 岁会 8 / 太一天符 4 / 同天符 6 / 同岁会 6。

### Docs
- `scripts/lib/yunqi_data.py` 的 `check_tianfu`、`calculate_yunqi_api.py` 的 `taiyi_tianfu` 布尔拼装处补《素问》六元正纪大论 / 六微旨大论出处注释，并注明素问原字「太一天符」（一）与后世注本「太乙天符」（乙）之异；`yunqi_data.js` / `calculate_yunqi_api.js` 同步。

## [0.3.1] - 2026-08-14

### Fixed
- **算法正确性·岁会（P0 级）**：`check_suihui`（`scripts/lib/yunqi_data.py` / `yunqi_data.js`）原用朴素判等「大运五行 == 地支五行」，误将寅/巳/申/亥 4 年（壬寅/癸巳/庚申/辛亥）收为岁会，实际命中 12 年而非经典 8 年。
  - 改为经典「运临本辰之位」判定（`DAYUN_BENCHEN` 表：木临卯、火临午、金临酉、水临子、土临辰戌丑未），岁会恰为 **8 年**。
  - 太乙天符 `taiyi_tianfu = check_tianfu and check_suihui` 经核实即为《医宗金鉴》经典定义（天符∩岁会，命中恰为经典四年：己丑/己未/乙酉/戊午），**保持布尔组合不变**，未被岁会 bug 带歪。
  - Py / JS 双引擎同步修复，`compare_py_js_yunqi.py` 一致性校验通过。
- **CI 盲区补齐**：`verify_cross_check.py` 的 `verify_suihui` / `verify_taiyi_tianfu` 由「仅正向遍历已知年」改为**全甲子（1984–2043）逆向断言**，要求命中集合恰好等于经典 8/4 年（无多无少），可接住此类朴素判等回归。验证基线 61 → **63** 项。
- **文档/术语对齐**：`yunqi_tonghua.md`、`modules/ganzhi-basics/references/jieqi.md`、`teaching-modules/天符岁会.md`、`rag-knowledge-base/terminology.json`（2 条）中的朴素「岁运五行 == 年支五行」定义统一修正为「运临本辰」，消除反向带偏 agent 检索输出的风险。

## [0.3.0] - 2026-08-13

### Added
- **P10 Parquet 数据导出**：`generate_rag_index.py` 新增 `--format parquet` 与 `--export-mode {index,rag,calendar}`。
  - `rag`：扁平化全部 RAG 条目为结构化表，字段覆盖岁运/司天/在泉/主气/运气相合五维度 + `rag_key` + `source_quote`（对齐 HF `datasets` 容器格式，导出**自有**结构化字段，不照搬/不重分发 pokkoa 散文 schema）。
  - `calendar`：生成 year×六步 的**全结构化**运气年表（1900–2100，宽年份跨度），比 pokkoa 的 311 条散文更有分析价值。
  - `index`：资产索引亦支持 Parquet。默认 JSON 路径零新增依赖（pyarrow 仅在 `--format parquet` 时懒加载）；新增 `parquet` extra（`pip install -e '.[parquet]'`）。

## [0.2.0] - 2026-08-13

### Added
- **工程优化（2026-08-12）**：对标 nihaisha-reverse 深度调研后的一轮检索/安全/正确性增强：
  - **P0 算法正确性**：修复 JS `checkPingqi` 漏判「不及同气相助」（波及乙卯/丁巳/己丑等 6 干支）；`compare_py_js_yunqi.py` 新增 `--sweep` 整甲子区间全字段校验（接入 CI）；`verify_cross_check.py` 补平气经典基线（验证项 52→61）。两套日期归一化收敛到 `-07-08`。
  - **P1-1 黄金基准**：`eval_retrieval_quality.py` 修正「基准含 asset18-32、检索却用默认范围」的错配，golden 落 `tests/golden/retrieval_golden.json` 持久化（`--write-golden` / `--check-golden`）；牌号修复 `rag_search._entry_id` 优先级（case_id/entry_id 提到 code 前）；指标 precision@10 78.1%→93.1%。补「体系内检索≠全库召回率」口径注释。
  - **P1-2 稳定引用**：新增 `yle:<asset>:<entry_id>` 引用语法，`rag_search` 四组装点统一输出 `ref`；新增 `resolve_ref.py`（解析/可访问率/`--selfcheck`）；引用规则写入 `rules/output.md`。
  - **P1-3 渐进加载**：新增 `cases_routing.py`，把病证→医案库路由固化为可编程薄索引（`--syndrome`/`--rag-key`/`--list-assets`/高风险病灶强制联动），避免整包 22 部库撑爆上下文。
  - **P1-4 检索健壮性**：新增 `_NORM_MAP`（70 项异体/繁简映射）+ `_normalize()`，关键词与语义检索共享（針/鍼→针、証→证、痺→痹 等）；新增 `--show-terms`（歧义消解展示）+ `--include-extra`（两段式补检索，默认关向后兼容）。
  - **P2-1 答案层断言**：`report_quality_gate` 新增 `check_answer_layer`（expected_behavior 语义判定 + 中文剂量/峻剂检测）+ `check_pair_consistency`（多轮鲁棒性）+ `check_boundary`（能力边界）；`tests/test_answer_layer.py` 扩到 22 例。
  - **P2-2 单一权威源**：免责声明收敛到 `_safety_text.py`，消除 7+ 文件硬拷贝漂移；`redact_dosage` 补中文剂量脱敏。

- **P7-1 推算算法覆盖度扩展**：`calculate_yunqi_api.py` / `.js` 新增三类运气推算字段：
  - `tong_hua` 增加 `tong_tianfu`（同天符：阳年中运与在泉同气）/ `tong_suihui`（同岁会：阴年中运与在泉同气）
  - `qi_hua`：五运齐化（太过之运，克我者来齐）/ 兼化（不及之运，克我者来兼）
  - `zheng_dui`：六气正化对化（十二地支配六气的正化/对化判定）
  - 依据：《医宗金鉴·运气要诀》《素问·五常政大论》《素问·天元纪大论》
  - Py/JS 双引擎同步，一致性校验通过
- **P7-2 疾病易感性 RAG**：新增 `asset33_disease_susceptibility.json`（12 条），基于公版学术文献蒸馏（33669 例 + 691 例高血压运气研究），覆盖岁运/司天/在泉/主气/运气相合五维度。`rag_search --asset asset33 高血压` 按疾病名检索，`infer_pathogenesis.py` 推理链自动匹配疾病易感性提示。
- **P7-2 扩展 疾病易感性全量覆盖**：asset33 从 12 条扩展到 33 条，补全 6 岁运（木不及/火不及/土太过/土不及/金太过/水太过）+ 4 司天（厥阴/少阳/阳明/太阳）+ 6 在泉 + 5 司天在泉组合，实现 28 个 rag_key 全覆盖。任意年份 `--date` 检索均命中 4 条疾病易感性数据。依据《素问·气交变大论》《素问·至真要大论》。
- **P7-1 经典文献交叉验证**：`scripts/verify_cross_check.py` 基于《医宗金鉴·运气要诀》蒸馏 52 项验证基线（天符12/岁会8/太乙天符4/同天符6/同岁会6/正化对化12/齐化兼化4），完全本地化无外部依赖，已纳入 CI
- **OPT-04 医案结构化字段**：自动提取 `herbs`（药味列表）+ `formulas_referenced`（方剂引用），1994 条中 68.2% 含药味、24.2% 含方剂引用。支持 `rag_search --field herbs 石膏` 精准检索。
- **OPT-Agent 医案白话解释能力**：system_prompt 路由表覆盖全 32 库（原仅 6 库），新增医案白话解释四段模板（医案故事/为什么这么治/原文存证/与运气关系）。
- **OPT-09 医案知识库浏览器**：`generate_case_browser.py` 生成 1994 条医案静态 HTML 浏览器，复用报告 UI 体系。
- **OPT-07 运气时间轴可视化**：`visualize_timeline.py` 生成全年六步客主加临时间轴 HTML，复用报告 UI 体系。
- **OPT-06 运气病机自动推理链**：`infer_pathogenesis.py` 实现年份→岁运病机→司天在泉→六步加临→推荐方剂五层推理闭环。
- **OPT-03 按字段检索**：`rag_search --field formula 茵陈` 按指定字段精准检索。
- **OPT-01 多库联合检索**：`rag_search --asset asset26,asset27` 逗号分隔跨库检索。
- **发布 0.2.0（文档去漂移 + 差异化定位）**：本包是**面向 AI Agent 的唯一即装即用五运六气技能形态**（同类多为传统 CLI/Web App）；1994 条逐字蒸馏医案，每条附 `source_quote` 原文存证，零占位零编造。本次固化 2026-08-12 工程批次，并将各文档计数统一到 CI 强制校验的权威值（医案 1994 · RAG asset 32 · 文献 51 · 指南 12 · 脚本 44 · 术语 700 · CI 步骤 36 · 回归 55/0 · 扩展验证 105/0）。

### Changed
- 孙文垣医案库（asset27）：12→390 条（覆盖率 98%），新增命门学说/新安医派视角
- 杏轩医案库（asset26）：14→184 条（覆盖率 93%），新增伤寒温病辨证/误治救逆
- 全库医案总数：~1100→1994 条（+894 条真实原文医案）

### Fixed
- 修复杏轩医案 case_id 重复（xx_014/15/20/145/146/147 → xx_153-158）

## [0.1.0] - 2026-08-10

### Added
- 五运六气推算引擎（干支/大运/司天在泉/客主加临/平气/太少）
- RAG 知识库（32 资产：岁运病机/司天在泉/客主加临/三因方/注家/体质/地域/术语 + 21 部医案库）
- HTML 可视化报告（宣纸水墨设计体系）
- ReAct 推理工作流 + 自进化引擎
- 注家人格（刘完素/张介宾）
- 内外联动机制（外科正宗/立斋外科）
- CI 自动化（Python 3.10/3.11/3.12 + Node 18/20/22 矩阵）
- 全链路测试（17 项：validate/index/regression/scenario/e2e/package/rag/pingqi/taishao/semantic/chain/random）
