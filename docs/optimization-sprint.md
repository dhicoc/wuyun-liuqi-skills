# 优化冲刺计划（Optimization Sprint）

> **状态文件**：本文件为本轮优化的**执行单一真相源**。  
> 完成一项任务后，必须更新对应状态列为 ✅，并记录完成日期。  
> 历史工程记录见 `docs/optimization.md`；UX 历史见 `docs/ux_optimization.md`；远期产品见 `docs/roadmap.md`。

| 字段 | 值 |
|------|-----|
| 创建日期 | 2026-07-09 |
| 目标 | 在功能已较完整的前提下，消除文档漂移、统一 CLI、收干净进程调用、提升可维护性与数据质量 |
| 原则 | 小步提交式改动；每阶段可验证；不破坏既有 CLI 兼容；推算仍禁止凭记忆 |
| 验收基线 | `health_check.py` + 关键 CLI 抽样；有破坏性改动时跑 `tests/verify_expansion.py` |

---

## 0. 背景与结论

### 0.1 已完成（不必重做）

| 类别 | 内容 |
|------|------|
| 工程 P0 | `_common.py` bootstrap、`get_jieqi_date` 缓存+兜底修复、RAG 缓存、日期解析统一 |
| 功能 P0–P5 | 体质/天气/高级对齐/思想导出/自进化核心/报告融合 |
| 主入口 UX | `calculate_yunqi_api.py` 已支持 `today`、`argparse`、`--help` |
| 常量同步 | `scripts/lib/yunqi_constants.json` 作为 Py/JS 表数据源 |

### 0.2 本轮真正要解决的问题

| ID | 问题 | 影响 |
|----|------|------|
| D1 | 优化/UX 文档仍写「待实施」，与代码不符 | 误导后续 Agent/维护者 |
| D2 | 自进化仅过滤 `source==test`，`test-key` 等噪声仍进报告 | 月报洞察失真 |
| E1 | 分项脚本仍手写 `sys.argv`，无统一 `--help` | 体验碎片化 |
| E2 | `calculate_yunqi_api` 的 `run_*` 与 HTML 高级对齐仍 subprocess | 慢、难测、编码脆弱 |
| E3 | scripts 平铺、无正式包 | 导入脆弱、难发布（本冲刺仅做准备，不全量重构） |
| P1 | 思想地图/交互学习等产品能力 | 远期，本冲刺只记 backlog |

---

## 1. 阶段总览

| 阶段 | 主题 | 优先级 | 状态 |
|------|------|--------|------|
| Phase 1 | 文档去漂移 + 自进化数据质量 | P0 | ✅ 完成 |
| Phase 2 | CLI 统一（legacy 脚本）+ 主路径去 subprocess | P0 | ✅ 完成 |
| Phase 3 | 测试加固（golden 边界 + Py/JS 对比） | P1 | ✅ 完成（全量 pytest 化仍属 backlog） |
| Phase 4 | 包结构准备 + 类型提示试点 | P2 | ✅ 主入口 typing + `wuyun_liuqi/` 轻量包骨架（scripts 未搬迁） |
| Phase 5 | 产品 backlog | P3 | ✅ 地图/苏格拉底/CLI/仪表盘/RAG 检索均已落地（轻量） |

图例：⏳ 待开始 · 🔄 进行中 · ✅ 完成 · ⏸ 暂缓

---

## 2. Phase 1 — 文档与数据质量

**目标**：让「文档说的」等于「代码做的」；自进化统计更干净。

### 2.1 任务清单

| ID | 任务 | 验收 | 状态 |
|----|------|------|------|
| P1-1 | 新建本冲刺文档 `docs/optimization-sprint.md` | 文件存在且含阶段/状态表 | ✅ 2026-07-09 |
| P1-2 | 修正 `docs/ux_optimization.md`：标记 today/argparse 已完成，更新剩余 UX 项 | 无「待实施」与主入口冲突描述 | ✅ 2026-07-09 |
| P1-3 | 修正 `docs/optimization.md` 文首问题总览与 P0 叙述，指向本冲刺文档 | 文首不再像全是待办；P0-3 状态与代码一致 | ✅ 2026-07-09 |
| P1-4 | 在 `docs/roadmap.md` 增加「当前冲刺」链接 | 指向本文件 | ✅ 2026-07-09 |
| P1-5 | 强化 `self_evolve.load_jsonl_lines` 噪声过滤 | 过滤 test-key、source 含 test/smoke/health、可疑 rag_keys | ✅ 2026-07-09 |
| P1-6 | 在 `references/module-index.md` 或 README 延伸索引中链到本冲刺文档 | 可发现 | ✅ 2026-07-09（module-index + SKILL.md） |

### 2.2 P1-5 过滤规则（实现约定）

默认 `filter_test=True` 时额外跳过：

1. `source` 大小写不敏感匹配：`test`、`smoke`、`health_check`、`ci`、`regression`
2. `rag_keys` 中任一 key 为：`test-key`、`test_key`、以 `test` 开头的占位 key
3. `input_date` 为明显占位：`test`、`dummy`、空字符串（若有）

可选：CLI `--include-test` 关闭过滤（分析调试用）。

---

## 3. Phase 2 — CLI 与进程调用

**目标**：旧脚本可发现、主路径无多余子进程。

### 3.1 任务清单

| ID | 任务 | 验收 | 状态 |
|----|------|------|------|
| P2-1 | 分项脚本统一 argparse：`ganzhi_calc` / `dayun_calc` / `keyun_calc` / `liuqi_calc` / `kezhujialin` | 均支持 `--help`、`--json`；原命令行为不变 | ✅ 2026-07-09 |
| P2-2 | 文档注明上述脚本为 **legacy 分项入口**；推荐 `calculate_yunqi_api.py` | `references/script-index.md` 更新 | ✅ 2026-07-09 |
| P2-3 | `calculate_yunqi_api.run_yunqi_report` 改为直接 import 函数 | 输出与原先一致；无 subprocess | ✅ 2026-07-09 |
| P2-4 | `run_visualize` 改为直接 import | 同上 | ✅ 2026-07-09 |
| P2-5 | `run_html_report` 改为直接 import `generate_html_report` 内可复用 API | 若无可导出函数则抽取 `write_html_report(date, path)` | ✅ 2026-07-09 |
| P2-6 | `generate_html_report.fetch_advanced_alignment` 改为直接 import `advanced_alignment` | mock 路径可用 | ✅ 2026-07-09 |

### 3.2 兼容约束

- 不删除任何公开 CLI 入口
- 参数名保持兼容（年份位置参数、`--json`）
- docstring 顶部可加：`[legacy] 推荐主入口：calculate_yunqi_api.py`

### 3.3 循环导入注意

- `calculate_yunqi_api` → `yunqi_report` / `visualize` / `generate_html_report` 应在函数内 lazy import
- `generate_html_report` → `calculate_yunqi_api` 已有；`advanced_alignment` 同样 lazy import

---

## 4. Phase 3 — 测试加固

| ID | 任务 | 验收 | 状态 |
|----|------|------|------|
| P3-1 | 新增 `tests/fixtures/dahan_boundary.json`：大寒前后边界日期 + 期望运气年 | 文件存在 | ✅ 2026-07-09 |
| P3-2 | 新增轻量测试脚本或断言：读 fixture 调 `calculate_yunqi_api` 校验运气年 | `python tests/test_dahan_boundary.py` 通过 | ✅ 2026-07-09 |
| P3-3 | Py/JS 同日 JSON 关键字段 diff | `python scripts/compare_py_js_yunqi.py` 通过 | ✅ 2026-07-09 |

---

## 5. Phase 4 — 结构与类型（轻量）

| ID | 任务 | 验收 | 状态 |
|----|------|------|------|
| P4-1 | 在 `docs/architecture.md` 记录目标包布局 `wuyun_liuqi/`，标注「渐进，未迁移」 | 有设计无强制搬家 | ✅ 2026-07-09 |
| P4-2 | 为核心 `calculate_yunqi_api` 公开函数补 typing（不全面改库） | 主要函数有返回类型注释 | ✅ 2026-07-09 |
| P4-3 | 轻量包 `wuyun_liuqi/` + `pyproject.toml` + `python -m wuyun_liuqi` | import calculate/search 可用 | ✅ 2026-07-09 |
| P4-4 | rag_key 精确直取 + `--date` 按日打包 | `--key` / `--date` 工作 | ✅ 2026-07-09 |

---

## 6. Phase 5 — 产品 Backlog

- [x] 思想地图（Mermaid 概念关系）→ `scripts/export_thought_map.py`（轻量 v1）
- [x] 苏格拉底交互学习模式 → `scripts/socratic_learn.py`（导出 + `--interactive`）
- [x] 统一 `yunqi` CLI / interactive → `scripts/yunqi_cli.py`
- [x] 个性化学习路径仪表盘 → `scripts/learning_dashboard.py` / `yunqi_cli.py dashboard`
- [x] 文献关键词检索（轻量，非向量）→ `scripts/rag_search.py` / `yunqi_cli.py search`

---

## 7. 每阶段验证清单

完成任一 Phase 后执行：

```bash
python scripts/health_check.py
python scripts/calculate_yunqi_api.py today --summary
python scripts/calculate_yunqi_api.py 2026-01-15 --json
python scripts/dayun_calc.py 2026 --json
```

Phase 2 额外：

```bash
python scripts/calculate_yunqi_api.py 2026-06-29 --report-type student
# 或触发 run_yunqi_report / HTML 的路径
python scripts/generate_html_report.py 2026-06-29 reports/generated/_sprint_smoke.html
```

Phase 3 额外：

```bash
python tests/test_dahan_boundary.py
python scripts/compare_py_js_yunqi.py
python tests/verify_expansion.py
```

思想地图 / 学习 / 统一 CLI：

```bash
python scripts/export_thought_map.py today --format both
python scripts/socratic_learn.py today
python scripts/yunqi_cli.py calc today --summary
python scripts/yunqi_cli.py learn today
python scripts/yunqi_cli.py search 司天
python scripts/yunqi_cli.py search --date today --json
python scripts/yunqi_cli.py dashboard
python scripts/yunqi_report.py 2026 --audience student
python tests/test_package_and_rag.py
python -m wuyun_liuqi calc today --summary
python scripts/yunqi_cli.py --help
```

有疑似推算回归时：

```bash
python tests/full_regression_test.py
```

---

## 8. 进度日志

| 日期 | 内容 |
|------|------|
| 2026-07-09 | 创建本文件；完成 Phase 1–3 主体与 Phase 4 文档准备 |
| 2026-07-09 | Phase 1：文档对齐 + `self_evolve` 噪声过滤 |
| 2026-07-09 | Phase 2：legacy argparse、`run_*`/`fetch_advanced_alignment` 去 subprocess |
| 2026-07-09 | Phase 3：`tests/fixtures/dahan_boundary.json` + `test_dahan_boundary.py` |
| 2026-07-09 | P3-3：`scripts/compare_py_js_yunqi.py`；P4-2：主入口 typing |
| 2026-07-09 | Phase 5 轻量：`scripts/export_thought_map.py` 思想地图 Mermaid |
| 2026-07-09 | Phase 5：`socratic_learn.py` + 统一入口 `yunqi_cli.py` |
| 2026-07-09 | Phase 5：`learning_dashboard.py` + `rag_search.py` |
| 2026-07-09 | P4-3/P4-4：`wuyun_liuqi` 包骨架；`rag_search --key/--date` |
| 2026-07-09 | 报告接入 RAG bundle；`tests/test_package_and_rag.py`；CI 扩展 |
| 2026-07-09 | HTML 同步 RAG 章节；pip install -e 冒烟；轻量语义检索 |

---

## 9. 相关文档索引

| 文档 | 用途 |
|------|------|
| `docs/optimization.md` | 历史工程优化与已完成项明细 |
| `docs/ux_optimization.md` | UX 专项（需与本冲刺同步状态） |
| `docs/self_evolve_optimization.md` | 自进化历史优化（多已完成） |
| `docs/roadmap.md` | 长期产品路线 |
| `references/script-index.md` | 脚本速查 |
| `references/gotchas.md` | Agent 踩坑 |

---

_维护约定：改代码不改本表状态 = 冲刺失败。每完成一个 ID，把状态改为 ✅ 并写日期。_
