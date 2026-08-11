# 优化路线图

> 基于全量审计（2124 条医案、32 资产、17 项全链路测试全绿）后制定的系统优化计划。
> 每项优化独立可验证，按优先级分批实施。

## 一、RAG 检索能力升级（P0-P1）

### OPT-01 多库联合检索 `[P0]`
- **现状**：`--asset` 只支持单库或全局，无法指定"在孙文垣+杏轩+临证指南三个库中搜索"
- **目标**：`--asset` 支持逗号分隔多库（如 `--asset asset26,asset27,asset16`）
- **改动文件**：`scripts/rag_search.py`
- **验证**：`python scripts/rag_search.py 头痛 --asset asset26,asset27 --json` 返回跨库结果

### OPT-02 embedding 语义检索落地 `[P0]`
- **现状**：`rag_semantic.py` 是 n-gram 退化方案，`sentence-transformers` 已声明但未实际使用
- **目标**：接入 sentence-transformers，预计算全部医案 embedding 缓存，支持"以案找案"
- **改动文件**：`scripts/rag_semantic.py`、新增 `scripts/build_embeddings.py`
- **验证**：`python scripts/rag_search.py --semantic "湿热身黄小便不利" --json` 返回语义相似医案

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

## 实施记录

| 日期 | 优化项 | 状态 | 提交 |
|------|--------|------|------|
| 2026-08-11 | OPT-01 多库联合检索 | ✅ 已完成 | - |
| 2026-08-11 | OPT-02 embedding 语义检索 | ✅ 已有（安装依赖即启用） | - |
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
