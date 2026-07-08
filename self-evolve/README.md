# 五运六气技能包自进化系统

> 让技能包从每一次推算中学习，持续优化“帮助人类理解运气学思想”的质量。
> 支持概念/哲学追踪、理解反馈、隐私保护（session 哈希 + PII 清洗）、导出材料生成。

---

## 一、系统架构

自进化系统由以下核心模块组成：

```
self-evolve/
├── logs/          # 使用日志（按日期分文件）
├── stats/         # 缓存统计结果
├── feedback/      # 用户反馈记录
├── misses/        # RAG 未命中记录（知识盲区）
├── reports/       # 自进化报告
└── README.md      # 本文件
```

### 数据流

```
每次推算 ──→ log_usage() ──→ logs/YYYY-MM-DD.jsonl
RAG 未命中 ──→ log_miss() ──→ misses/YYYY-MM-DD_misses.jsonl
用户反馈 ──→ log_feedback() ──→ feedback/YYYY-MM-DD_feedback.jsonl
                          ↓
               self_evolve.py report
                          ↓
               reports/report_YYYY-MM-DD.md
                          ↓
               人工审查 → 更新 RAG assets
```

---

## 二、如何记录每次推算

### 2.1 手动记录（CLI）

每次完成推算后，立即执行：

```bash
python scripts/self_evolve.py log \
    --input "2026-06-27" \
    --rag-keys "water_excess,shaoyin_junhuo_sitian,earth_zaiquan" \
    --source "cli"
```

参数说明：

| 参数 | 说明 | 示例 |
|------|------|------|
| `--input` | 推算的输入日期 | `2026-06-27` |
| `--rag-keys` | 本次查询的所有 RAG 键，逗号分隔 | `water_excess,shaoyin_junhuo` |
| `--source` | 调用来源（cli / api / workflow） | `cli` |

### 2.2 自动记录（推荐）

在 `agent-workflow/react_workflow.md` 的 OUTPUT 阶段自动追加日志调用（含 concepts）。详见 `agent-workflow/self_evolve_hook.md`。

**当前增强**：
- 自动记录 concepts（包括“思想层解读”）
- session_id 默认 SHA256 哈希（隐私）
- feedback 支持 understanding 类型
- 支持 filter_test + dedup
- 报告包含理解质量洞察与改进建议
- 导出功能（export_thought）可与自进化数据结合使用复习材料

### 2.3 在 API 脚本中集成

在 `scripts/calculate_yunqi_api.py` 等 API 脚本中，在返回结果前插入：

```python
from scripts.self_evolve import log_usage
log_usage(input_date=date_str, rag_keys=rag_keys_used, source="api")
```

---

## 三、知识盲区检测

当 RAG 查询返回空结果时，应调用 `log_miss()` 记录：

```python
from scripts.self_evolve import log_miss
log_miss(query_key="shaoyin_junhuo_ke", context="2026-06-27 推算中缺少少阴君火客气的资料")
```

### 定期排查盲区

```bash
# 查看所有盲区排名
python scripts/self_evolve.py analyze --type blind_spots

# 查看具体哪些知识从未被查询
python scripts/self_evolve.py stats --type low_coverage
```

### 盲区处理流程

1. 使用 `analyze --type blind_spots` 列出所有盲区键
2. 对照 `rag-knowledge-base/` 下的 JSON asset 文件
3. 补充缺失的病机知识条目
4. 重新运行 `generate_report()` 确认盲区已消除

---

## 四、用户反馈采集

### 4.1 CLI 方式

```bash
python scripts/self_evolve.py feedback \
    --session-id "session_20260627_001" \
    --rating 4 \
    --comment "推算结果准确，建议补充对应的方药推荐"
```

### 4.2 评分标准

| 评分 | 含义 |
|------|------|
| 5 | 非常准确，完全满足需求 |
| 4 | 准确，略有不足 |
| 3 | 基本可用，有明显改进空间 |
| 2 | 不够准确，需要较大改进 |
| 1 | 不准确，未满足需求 |

### 4.3 反馈分析

```bash
# 查看反馈汇总
python scripts/self_evolve.py stats --type feedback
```

当平均评分低于 3.0 时，建议：
- 检查对应日期的 RAG 知识是否完整
- 审查推算逻辑是否有误
- 补充用户频繁提及的缺失内容

**隐私注意**：反馈默认匿名化 session_id 和清洗 comment 中的 PII。使用 `cleanup` 命令定期清理旧数据。

---

## 五、优化报告

### 5.1 生成报告

```bash
python scripts/self_evolve.py report
```

报告自动保存至 `self-evolve/reports/report_YYYY-MM-DD.md`，包含：

- 使用概况（累计推算次数、活跃天数）
- 高频查询病机 TOP5
- 知识盲区列表
- 低覆盖率条目（已有知识但从未被查询）
- 用户反馈汇总

### 5.2 报告驱动的优化循环

```
生成报告 → 分析盲区 → 补充 RAG 知识 → 验证改进 → 再次生成报告
```

建议每周至少执行一次完整的优化循环。

---

## 六、最佳实践

### 6.1 日常操作

| 频率 | 操作 |
|------|------|
| 每次推算后 | 调用 `log_usage()` 记录 |
| 每次 RAG 未命中 | 调用 `log_miss()` 记录 |
| 每次交互结束 | 邀请用户评分反馈 |
| 每日 | 运行 `stats --type daily` 检查使用趋势 |
| 每周 | 运行 `report` 生成优化报告 |
| 每两周 | 审查报告，补充 RAG 知识 |

### 6.2 自动化建议

在 `agent-workflow/workflow_config.json` 中添加钩子配置：

```json
{
  "hooks": {
    "after_calculation": "python scripts/self_evolve.py log --input {date} --rag-keys {keys} --source workflow",
    "on_miss": "python scripts/self_evolve.py log_miss --key {key} --context {context}"
  }
}
```

### 6.3 注意事项

- JSONL 日志文件按日期自动分割，无需手动清理
- 所有数据以纯文本存储，可直接用文本编辑器查看
- 统计函数自动扫描所有历史日志，无需指定日期范围
- `low_coverage` 检测依赖于 `rag-knowledge-base/` 目录下的 JSON asset 结构

### 6.4 隐私增强

自进化默认启用隐私保护：
- `session_id` 自动 SHA256 哈希（保留前16位用于统计聚合）。
- `comment` 和 `context` 自动清洗邮箱、手机号、常见姓名等 PII。
- 使用 `python scripts/self_evolve.py cleanup --days 90` 定期删除旧数据。
- 报告默认不包含原始敏感文本，仅统计和摘要。

如需调试，可在调用时传 `anonymize=False`（不推荐生产使用）。历史日志加载时建议保持匿名。
