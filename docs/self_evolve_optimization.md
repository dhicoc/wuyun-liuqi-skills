# 自进化引擎 (Self-Evolution) 优化计划

## 1. 项目定位与自进化的角色

本项目的核心定位是：**让人类通过 AI Agent 深入理解《黄帝内经》运气学这个思想体系**（天人合一、气化流行、时间节律、中和之道等）。

自进化引擎（`scripts/self_evolve.py` + `self-evolve/`）是实现“持续优化”的关键闭环。它目前主要追踪**技术指标**（RAG key 命中率、盲区、基础评分），但对**“帮助人类理解思想”的质量**支持不足。

### 当前问题总结
- 日志主要记录 `rag_keys`（如 `water_excess`），缺乏对哲学概念（天人合一、气化、中和）的追踪。
- 反馈支持 `feedback_type="understanding"`，但集成不完整（CLI 缺失、报告未充分利用）。
- 缺少自动集成：主入口 `calculate_yunqi_api.py` 和报告生成默认不记录。
- 报告偏技术优化，缺少“教学/理解效果”洞察。
- 数据质量差（大量测试数据、无去重、会话关联弱）。
- 对 Agent 不友好：输出是纯文本，难以结构化推理“用户哪里理解困难”。

目标：让自进化从“技术覆盖优化”转向**“思想理解质量持续提升”**，支撑 Agent 成为更好的“运气学思想伙伴”。

---

## 2. 优化优先级

### P0（立即执行，高影响）
1. **自动集成日志记录**  
   在 `calculate_yunqi_api.py`、`yunqi_report.py` 等主入口自动调用 `log_usage`（含 concepts）。
2. **完善概念级 + 理解反馈追踪**  
   - `log_usage` 支持 `concepts` 参数。
   - CLI 支持 `--feedback-type understanding` 和 `--concepts`。
   - 统计函数新增 `top_concepts`、`understanding_feedback`。
3. **报告增强（思想理解维度）**  
   报告和月报增加“思想概念高频”、“理解质量反馈”、“教学改进建议”。

### P1（短期，高价值）
4. **数据质量与会话支持**  
   - 过滤测试数据、会话聚合、去重。
   - 记录 `session_id` 和 `concepts_explained`。
5. **Agent 友好输出**  
   增加 `--json` 支持，返回结构化洞察（便于 Agent 读取“理解盲区”）。
6. **低覆盖率与盲区优化**  
   改进 `stats_low_coverage`（只返回有意义的 key），并关联到思想概念。

### P2（中期，长期价值）
7. **学习路径与理解演进追踪**  
   记录用户连续提问的“概念链”，分析理解是否在进步。
8. **自动改进建议**  
   基于低分理解反馈，自动建议“此概念解释可补充 XX 比喻”或“扩展思想层解读”。
9. **可视化与仪表盘**  
   简单趋势图或增强报告（高频困惑概念、评分趋势）。
10. **隐私与健壮性**  
    更好错误处理、数据清理、敏感信息过滤。

---

## 3. 实施计划与状态

| 优先级 | 任务 | 描述 | 状态 | 验收 |
|--------|------|------|------|------|
| P0-1 | 自动日志集成 | 在 calculate_yunqi_api.py 和 yunqi_report.py 自动 log_usage（含 concepts） | ✅ 完成 | 运行 API 后日志自动生成 |
| P0-2 | 完善 CLI 与统计 | 支持 feedback_type 和 top_concepts；新增 understanding 统计 | ✅ 完成 | CLI 支持，top_concepts 可用 |
| P0-3 | 报告思想维度增强 | 月报/报告增加理解反馈章节和建议 | ✅ 完成 | 报告有思想理解章节 |
| P1-1 | 数据质量提升 | 过滤测试数据、支持 session_id、去重 | ✅ 完成 | load 默认 filter_test + dedup，session_id 支持，隐私哈希 |
| P1-2 | Agent 友好 JSON | stats/report 支持 --json 结构化输出 | ✅ 完成 | 自进化 CLI 支持 --json，report 生成结构化内容 |
| P1-3 | 低覆盖优化 | 改进 low_coverage + 关联概念 | ✅ 完成 | 过滤 test，关联未查询概念，返回有意义条目 |
| P2-1 | 学习路径追踪 | 记录概念链，分析进步 | ✅ 完成 | stats_concept_progression + sessions |
| P2-2 | 自动建议 | 基于反馈生成解释改进建议 | ✅ 完成 | 报告中基于 progress 和 understanding 给出建议 |
| P2-3 | 文档与集成 | 更新 README、hook、示例 | ✅ 完成 | 本文档 + self-evolve/README.md + agent-workflow/self_evolve_hook.md + CLI 示例 + privacy section |

---

## 4. 验证策略

- **功能验证**：运行 `python scripts/self_evolve.py <cmd>` 验证新参数/输出。
- **集成验证**：调用 `calculate_yunqi_api.py today --summary --explain-concept "天人合一"`，检查日志。
- **全链路冒烟**：使用 `scripts/smoke_full_chain.py` + 手动验证自进化数据。
- **报告验证**：生成 report/monthly-report，确认包含思想理解章节。
- **回归**：`tests/verify_expansion.py` + `tests/full_regression_test.py`。
- **定位对齐**：模拟 Agent 对话，验证是否能追踪“用户对思想的理解”。

---

## 5. 风险与注意

- 不要阻塞主流程：日志记录必须 try/except 包裹。
- 向后兼容：保留现有 CLI 行为。
- 数据迁移：历史日志无需改动，新字段可选。
- 隐私：concepts 和 feedback 不记录用户身份。**新增隐私增强计划见下文**。

## 6. 隐私增强专项计划（新增）

由于自进化涉及用户使用数据和反馈（尤其是“理解质量”反馈），隐私是关键信任点。当前系统存储明文 session_id、自由文本 comment/context，可能泄露间接身份或敏感想法。

### 隐私增强优先级

**P0（立即）**：
- 默认哈希 session_id（使用固定盐 + SHA256，保留前8位用于聚合）。
- 自动清洗 comment 和 context 中的潜在 PII（邮箱、手机号、姓名模式）。
- 添加 `anonymize=True` 参数到 log 函数，默认开启。

**P1**：
- 新增 `cleanup()` 函数：删除旧日志、匿名化历史数据。
- 报告中默认不包含原始 comment，仅统计和摘要。
- CLI 增加 `--no-privacy` 选项（用于调试）。

**P2**：
- 支持 per-log 隐私级别。
- 添加隐私声明到所有报告和 README。
- 定期自动清理（e.g., 保留90天）。

**验收**：
- session_id 在日志中为哈希值。
- 包含 "user@example.com" 的 comment 会被清洗为 "[REDACTED]"。
- 报告不泄露原始反馈文本。
- 向后兼容旧日志（加载时可选择是否反匿名）。

更新文档和代码后进行全链路测试。

**开始实施后，本文档作为跟踪依据。所有改动服务于“帮助人类通过 Agent 理解运气学思想”。**

## 实施总结

### 已完成（P0 全部 + P1 全部 + P2 核心 + 隐私增强）
- P0-1 ~ P0-3, P1-1 ~ P1-3, P2-1 ~ P2-3: 全部按计划实施
- 额外隐私增强（P0 完成）: 
  - 默认 session_id SHA256 哈希（16位）
  - comment/context 自动 PII 清洗（邮箱、电话、姓名）
  - log_* 函数支持 anonymize=True（默认）
  - 新增 cleanup_old_data(days, anonymize_existing)
  - CLI: python scripts/self_evolve.py cleanup --days 90
- load_jsonl_lines 支持 filter_test + dedup
- stats_sessions, concept_progression 增强学习路径
- self-evolve/README.md 新增隐私章节
- agent-workflow/self_evolve_hook.md 更新支持 concepts、anonymize、track_concepts
- 报告默认尊重隐私（不含原始敏感文本）

全链路验证通过（verify_expansion 75/0 + full_regression 63/0 + smoke + 专项测试，包括隐私哈希/清洗/dedup/session）。

**再次运行完整回归**：
- 最新运行: 通过: 63, 失败: 0

**清理测试数据**：
- reports/test-results/ 已清理（只剩 .gitkeep，101+ 项 artifact 已删除；清理后重新运行回归确认仍 63/0）
- 快照已更新为包含思想层解读的当前版本
- 再次运行完整回归确认: 63/0

**最新运行**（清理后）: 通过 63, 失败 0。背景任务确认一致。完整回归 63/0，verify_expansion 75/0。

**所有自进化优化（含隐私增强）已按优先级一步步完成！**

- 最终测试: verify_expansion 75/0, smoke_full_chain 通过, top_concepts 正常追踪思想概念。
- 报告快照已更新以包含思想层解读（质量门禁和 snapshot check 均通过）。已使用 Python UTF-8 正确同步 test-results 和 snapshot，确认两者 gate 和 snapshot check 均 "✅ 报告质量门禁通过"。full_regression 现在 0 失败。最新运行: 通过: 63, 失败: 0。
- 文档和 hook 已更新，支持新功能和隐私。
- 剩余待办（如 P1-4 渐进式学习）可作为未来迭代。

项目自进化现在更好地服务于“帮助人类通过 Agent 理解运气学思想”的定位。

**注意**：快照文件已使用 Python UTF-8 写入修复，以匹配新增的思想层解读内容。

**最终确认**：full_regression_test.py 干净通过（63/0）。所有自进化相关变更已完全验证。背景任务多次确认一致。最新后台任务 (call-6e7f09d5...) 确认: 63/0。测试数据已清理干净（0 artifact）。

- P0: 自动集成、CLI/统计、报告增强、隐私（哈希+清洗+cleanup）
- P1: 数据质量（filter+dedup+session）、Agent JSON、低覆盖优化
- P2: 学习路径、自动建议、文档集成

下一步可关注其他模块或实际使用数据积累。文档已最终更新。

---

## 2026-07-08 再次运行完整回归 + 清理测试数据（本次会话）

**执行**：
- 运行前先清理 `reports/test-results/*`（包括 .gitkeep 临时移除）
- 执行 `python -X utf8 tests/full_regression_test.py` （使用 subprocess + utf8 捕获，避免 shell 重定向乱码）
- 结果：`通过: 63, 失败: 0` ，全部 [OK]（包括 report quality gate、snapshot、self_evolve 各项、demo_full_chain）
- 运行后再次清理 test-results/ ，仅保留 `.gitkeep`

**验证**：
- 第二次（清理后）重跑回归：仍 `通过: 63, 失败: 0`
- 最终状态：`reports/test-results/` 仅含 `.gitkeep`（0 个测试 artifact）
- 快照检查与质量门禁全部通过（思想层解读内容已正确纳入 snapshot）
- smoke 覆盖已并入 full_regression（demo_full_chain OK）

**Git 工作区**：
- test-results 相关变更已清理干净
- snapshots/ 保持为当前包含思想层解读的版本（与 HEAD 有预期 diff，因之前优化新增内容；测试依赖此版本）

**结论**：回归干净、测试数已清零。所有 P0/P1/P2 自进化优化（含隐私）持续稳定通过验证。符合“再次运行完整回归 / 清理测试数”要求。

### 全链路测试
- verify_expansion: 75/0
- smoke_full_chain: 通过
- 自进化专项: top_concepts、sessions、concept_progress、report --json、auto log、understanding feedback 正常
- 数据质量: test source 过滤生效，会话支持
- 隐私: 哈希和清洗生效，原始数据不泄露

所有主要优化已完成。文档状态已更新。

---

**下一步**：按照 P0 优先级一步步实现（使用 todo 跟踪），每步更新本文档状态，最后全链路冒烟测试。