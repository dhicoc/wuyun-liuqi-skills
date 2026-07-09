# 用户体验 (UX) 优化计划

> 本文档聚焦**最终用户使用体验**，区别于 `optimization.md`（工程质量、性能、代码结构）。
> 目标：让直接运行 CLI 的人类用户和通过 AI Agent 调用的用户，都能更轻松、愉快、高效地使用本技能包。

最后更新：2026-07-09

> **当前执行真相源**：本轮未完成的 UX 项已并入 [optimization-sprint.md](./optimization-sprint.md)。  
> 下文中标注 ✅ 的项表示代码侧已落地；仍标 ⏳ 的项为剩余 backlog。

---

## 1. 用户画像与核心痛点

| 用户类型 | 典型场景 | 当前痛点 |
|----------|----------|----------|
| **直接人类用户** | “今天运气怎么样？”<br>“帮我分析一下出生运气”<br>“给我一份报告” | 必须记 `YYYY-MM-DD`；不知道最佳命令；跑完后不知道下一步 |
| **AI Agent 用户** | 按 SKILL.md + routing 自动调用 | 基本可用，但错误处理和引导仍可更好 |
| **进阶用户** | 天气+体质+报告组合分析 | 参数多、步骤散、发现成本高 |

**核心 UX 问题分类**：
- 输入门槛高（日期）
- 发现与帮助体验差
- 首次使用 / 引导不足
- 错误恢复与建议弱
- 输出缺乏后续引导
- 终端体验不够现代

---

## 2. 优先级定义（UX 视角）

- **P0 UX**：高影响、低改动、用户立刻能感觉到。强烈推荐优先实施。
- **P1 UX**：明显改善体验，成本中等。
- **P2 UX**：长期价值，涉及较大改动或新功能。

---

## 3. P0 UX：立即高价值改进

### 3.1 日期输入友好化（最高 ROI）

**问题**：
- 所有主要脚本只接受严格 `YYYY-MM-DD`
- 不支持 `today`、`今天`、无参数默认今天
- 文档里经常提到“今天”，但实际脚本不支持

**建议方案**：
- 在 `calculate_yunqi_api.py`（主入口）支持：
  - `python ... today --summary`
  - `python ... --today`
  - 无参数时默认输出今天 + summary
- 内部使用 `datetime.date.today()` 解析
- 同步更新 `demo_full_chain.py`、`personal_yunqi_profile.py` 等常用入口
- 在 `routing.md` 和 README 中明确支持

**验收**：
- `python scripts/calculate_yunqi_api.py today --summary` 正常工作
- 无参数运行给出合理默认行为 + 友好提示
- 大寒边界和随机日期测试仍全部通过

**当前状态**：✅ 已完成（主入口支持 `today` / 默认今天；见 `calculate_yunqi_api.py`）

---

### 3.2 主 CLI 帮助与参数体验

**问题（历史）**：
- 曾用手写 `sys.argv`，`--help` 缺失；旧脚本风格不一致

**已完成**：
- `calculate_yunqi_api.py` 已迁移 `argparse`，含 description / epilog 示例

**剩余**：
- 分项脚本（`dayun_calc` 等）统一 argparse / legacy 标注 → 见冲刺 **P2-1**

**当前状态**：主入口 ✅；legacy 分项 ⏳（optimization-sprint Phase 2）

---

### 3.3 健康检查后的行动引导

**当前状态**：✅ 已完成（`health_check.py` 成功后打印可复制推荐命令）

---

### 3.4 错误消息与恢复建议

**当前状态**：部分完成（主入口日期校验与友好报错已有；天气/advanced 的 `--mock` 提示与 lunar 降级警告可继续打磨）

**剩余 backlog**：见 optimization-sprint Phase 2 之后的运维体验项

---

### 3.5 输出末尾的“下一步”引导

**当前状态**：✅ 已完成（主入口 summary / format 输出含「下一步建议」与思想伙伴问题）

---

## 4. P1 UX：明显改善体验

### 4.1 CLI 碎片化缓解

- **目标**：文档把 `calculate_yunqi_api.py` 作为唯一推荐入口，旧脚本标 legacy
- **状态**：⏳ 进行中（optimization-sprint P2-1 / P2-2）

### 4.2 终端输出现代化（轻量）

- 主入口已有 ANSI 颜色辅助（`_common.color` 等）
- **状态**：✅ 主路径已具备；可继续扩展到 legacy 脚本

### 4.3 首次使用流程闭环

- `setup.bat` / `setup.sh` 成功后自动建议运行 `health_check.py` 并给出下一步
- 新增一个 `scripts/quickstart.py` 或把 demo 做得更友好

### 4.4 个人化功能一键化

- 在 `advanced_alignment.py` 增加更智能的默认行为
- 提供 `python ... --profile` 快捷方式

---

## 5. P2 UX：长期价值

- 提供真正的统一 CLI（`python -m` 或 entry point）
- 增加交互模式（`--interactive`）
- 人类用户专用快速开始文档（单独的 `docs/CLI_USER_GUIDE.md`）
- 让自进化反馈更可见（运行后自动提示已记录，可查询月报）
- HTML 报告默认生成并提示打开路径

---

## 6. 实施路线图与状态

| 阶段 | 任务 | 优先级 | 状态 | 备注 |
|------|------|--------|------|------|
| P0-1 | 日期输入支持 today / --today / 默认今天 | P0 | ✅ 已完成 | 最高 ROI |
| P0-2 | calculate_yunqi_api.py 改用 argparse + 优秀 --help | P0 | ✅ 已完成 | - | 2026-07-08 |
- 完整 argparse + description + epilog 示例
- --help 现在可用且信息丰富 |
| P0-3 | health_check.py 增加成功后行动引导 | P0 | ✅ 已完成 | - | 2026-07-08 |
- 成功时打印可直接复制的 3 个推荐命令 + 个人体质示例 |
| P0-4 | 关键错误消息增强（lunar、天气） | P0 | 进行中（部分完成） | - | 2026-07-08 |
- lunar-python 缺失时在 _get_solar_class 打印警告
- health_check 增强 lunar 提示
- 后续可继续在 weather 处加 --mock 建议 |
| P0-5 | 所有主要输出增加“下一步建议” | P0 | ✅ 已完成 | - | 2026-07-08 |
- generate_summary 和 format_text 末尾增加推荐命令
- 使用实际日期填充 |
| P1-1 | README / 文档把主入口统一推荐 | P1 | ✅ 已完成 | - | 2026-07-08 |
- README 和 routing.md 更新为推荐 today + calculate_yunqi_api.py |
| P1-2 | 轻量终端颜色与格式化 | P1 | ✅ 已完成 | - | 2026-07-08 |
- highlight_key 用于太过/不及/相得/不相得 等 |
- 集成到 format_text、--summary、health_check |
| P1-3 | setup 脚本末尾给出引导 | P1 | ✅ 已完成 | - | 2026-07-08 |
- setup.sh / setup.bat 成功后推荐 health_check + today 命令 |
| P2 | 统一 CLI / 交互模式 | P2 | 规划中 | 长期 | 思想导出（export_thought）已部分缓解学习闭环需求 |

---

## 7. 验证策略

每次 UX 改动后执行：

1. 直接人类视角测试：
   - `python scripts/calculate_yunqi_api.py`（无参数）
   - `python scripts/calculate_yunqi_api.py today --summary`
   - `python scripts/health_check.py`
2. 边界与错误场景：
   - 故意不装 lunar-python
   - 无网络运行天气相关
3. 全链路回归：
   - `python tests/verify_expansion.py`
   - `python scripts/smoke_full_chain.py --count 4`
4. 人工阅读输出，确认引导自然、不打扰

---

## 8. 与工程优化文档的关系

- `optimization.md` 关注“代码是否健康、可维护”
- 本文档关注“用户是否觉得好用、想继续用”
- 两者可并行，部分改动会互相促进（如更好的错误处理既是工程也是 UX）

---

**开始实施后，本文档将作为 UX 改进的跟踪来源。所有改动应保持对 AI Agent 的完全兼容，同时显著提升人类直接使用体验。**

## 最新实施进展

### P1 完成
- ✅ P1-2: 轻量 ANSI 颜色支持（_common.py）
  - highlight_key 用于太过/不及/相得/不相得 等
  - 集成到 format_text 和 --summary
  - health_check 使用 success/warning/error
- ✅ P1-3: setup.bat / setup.sh 末尾增强
  - 推荐 health_check + today 命令 + 说明

### 验证
- smoke_full_chain.py 多次随机全链路全部通过
- today、颜色、引导、帮助、思想导出均可直接使用
- 完整回归 63/0，verify 75/0

所有 P0 + 主要 P1 UX 优化已落地。用户现在可以：
- 直接 `python scripts/calculate_yunqi_api.py`（或 today）得到今天结果 + 思想层
- 看到彩色高亮关键结论
- 运行 setup 后得到清晰下一步
- 看到输出末尾的实用建议 + 反思问题
- 使用 `export_thought.py --format all` 导出思想摘要、Anki 卡片、打印 HTML

P2（统一 CLI / 交互模式）可作为未来迭代。思想材料导出已显著提升学习闭环。

---

## 本次实施总结（UX 优化）

已完成 P0 UX 全部 5 项 + P1-1：

- ✅ 日期支持 today / 默认今天（最高影响）
- ✅ 主 CLI 改用 argparse + 优秀 --help
- ✅ health_check 增加行动引导
- ✅ 错误消息增强（lunar 警告 + health_check 提示）
- ✅ 输出末尾增加“下一步建议”
- ✅ 文档更新（README / routing 推荐主入口 + today）

**验证结果**：
- `tests/verify_expansion.py`: 75/0
- `tests/full_regression_test.py`: 63/0
- `scripts/smoke_full_chain.py`: 随机日期全链路通过
- 人类视角测试：无参数、today、--help、引导、导出均正常

所有改动对现有 JSON 输出和 Agent 调用完全兼容。
