# 自进化钩子：集成到 ReAct 工作流

> 将自进化机制无缝嵌入 ACT → OBSERVE → THINK → OUTPUT 循环。

---

## 一、工作流集成点

ReAct 标准循环：

```
ACT (行动) → OBSERVE (观察) → THINK (思考) → OUTPUT (输出)
                                                    │
                                                    ▼
                                          自进化钩子在此触发
```

在每个完整的 ACT→OBSERVE→THINK→OUTPUT 循环结束后，插入自进化日志记录。

---

## 二、钩子实现

### 2.1 OUTPUT 阶段后自动日志

在每个 OUTPUT 阶段的末尾插入以下步骤：

```
步骤 1: 收集本次循环的关键信息
  - input_date: 本次推算的日期（如 2026-06-27）
  - rag_keys_used: 本次查询的所有 RAG 键列表
  - session_id: 当前会话标识

步骤 2: 调用 log_usage()
  方式一（Python 直接调用）:
    from scripts.self_evolve import log_usage
    log_usage(
        input_date="2026-06-27",
        rag_keys=["water_excess", "shaoyin_junhuo_sitian"],
        source="react_workflow"
    )

  方式二（CLI 子进程调用）:
    python scripts/self_evolve.py log \
        --input "2026-06-27" \
        --rag-keys "water_excess,shaoyin_junhuo_sitian" \
        --source "react_workflow"

步骤 3: 记录到工作流上下文
  将日志结果附加到工作流状态中，供后续分析和报告使用。
```

### 2.2 RAG 未命中时的钩子

当 OBSERVE 阶段发现 RAG 查询返回空结果时：

```
步骤 1: 检测到 RAG 未命中
  - 识别缺失的 rag_key
  - 记录查询上下文（日期、病机组合等）

步骤 2: 调用 log_miss()
  方式一（Python 直接调用）:
    from scripts.self_evolve import log_miss
    log_miss(
        query_key="shaoyin_junhuo_ke",
        context="2026-06-27 推算中缺少少阴君火客气的资料"
    )

  方式二（CLI 子进程调用）:
    python scripts/self_evolve.py log_miss \
        --key "shaoyin_junhuo_ke" \
        --context "2026-06-27 推算中缺少少阴君火客气的资料"

步骤 3: 降级策略
  - 使用相近的 RAG 键尝试查找替代知识
  - 在 OUTPUT 中注明"该病机缺少完整知识，结果仅供参考"
```

### 2.3 交互结束时的反馈邀请

当整个推算会话结束时：

```
步骤 1: 生成反馈邀请
  在 OUTPUT 末尾附加：
    "本次推算结果对您有帮助吗？请评分（1-5分），您的反馈将帮助改进。"

步骤 2: 收集用户反馈（如果有）
  from scripts.self_evolve import log_feedback
  log_feedback(
      session_id="session_20260627_001",
      rating=4,
      comment="建议补充方药推荐"
  )

步骤 3: 如果评分低于 3 分，触发即时改进建议
  - 标记该次会话为"需改进"
  - 运行 analyze --type blind_spots 检查是否因知识缺失导致
```

---

## 三、工作流配置集成

### 3.1 workflow_config.json 配置

在 `agent-workflow/workflow_config.json` 中添加：

```json
{
  "hooks": {
    "self_evolution": {
      "enabled": true,
      "log_on_output": true,
      "log_on_miss": true,
      "invite_feedback": true,
      "feedback_threshold": 4,
      "auto_report_on_exit": false
    }
  }
}
```

| 配置项 | 类型 | 说明 |
|--------|------|------|
| `enabled` | bool | 是否启用自进化钩子 |
| `log_on_output` | bool | 每次 OUTPUT 后自动记录日志 |
| `log_on_miss` | bool | RAG 未命中时自动记录 |
| `invite_feedback` | bool | 交互结束时邀请用户反馈 |
| `feedback_threshold` | int | 低于此分数触发改进分析 |
| `auto_report_on_exit` | bool | 退出时自动生成报告 |

### 3.2 工作流状态集成

在工作流上下文中维护自进化状态：

```json
{
  "self_evolution": {
    "session_id": "session_20260627_001",
    "cycles_completed": 3,
    "last_log_timestamp": "2026-06-27T14:30:00",
    "misses_this_session": [],
    "feedback_given": false,
    "pending_improvements": []
  }
}
```

---

## 四、完整循环示例

以下是一个带自进化钩子的完整 ReAct 循环：

```
=== CYCLE START ===

[ACT] 用户输入日期 "2026-06-27"
      触发五运六气推算流程
      查询 RAG 知识库: water_excess, shaoyin_junhuo_sitian, earth_zaiquan

[OBSERVE] RAG 返回结果
          - water_excess → 命中（水运太过知识）
          - shaoyin_junhuo_sitian → 命中（少阴君火司天知识）
          - earth_zaiquan → 未命中 ← 触发 MISS 钩子

[THINK]  分析结果
          water_excess + shaoyin_junhuo_sitian 组合提示寒热错杂
          earth_zaiquan 缺失 → 使用默认值

[OUTPUT] 生成推算报告
          "2026年为丙午年，水运太过，少阴君火司天..."
          + [自进化钩子触发]
            1. log_usage(input="2026-06-27", keys=[water_excess, shaoyin_junhuo_sitian, earth_zaiquan])
            2. log_miss(key="earth_zaiquan", context="2026-06-27 推算")
            3. 附加反馈邀请: "本次结果对您有帮助吗？请评分（1-5分）"

=== CYCLE END ===
```

---

## 五、工作流模板代码

在 ReAct 工作流的主体逻辑中插入以下模板代码：

```python
# ── 自进化钩子 ──────────────────────────────────────
from scripts.self_evolve import log_usage, log_miss, log_feedback

def after_output_hook(input_date, rag_keys, session_id):
    """OUTPUT 阶段后的自进化钩子。"""
    # 1. 记录使用日志
    log_usage(input_date, rag_keys, source="react_workflow")

    # 2. 检测并记录未命中
    # （在 OBSERVE 阶段已由 RAG 查询函数调用 log_miss）

    # 3. 附加反馈邀请
    print("\n---")
    print("本次推算结果对您有帮助吗？请评分（1-5分），或回复 'skip' 跳过。")
    # 注：实际集成时，反馈采集由工作流调度器处理

def on_rag_miss_hook(query_key, context):
    """RAG 未命中时的钩子。"""
    log_miss(query_key, context)
    # 降级处理：尝试相近知识
    fallback_keys = {
        "earth_zaiquan": "earth",
        "shaoyin_junhuo_ke": "shaoyin_junhuo",
    }
    return fallback_keys.get(query_key)  # 返回降级键或 None
```

---

## 六、效果评估

集成自进化钩子后，可以衡量以下指标：

| 指标 | 基线 | 目标（4周后） |
|------|------|---------------|
| 知识盲区数量 | 初始值 | 减少 50% |
| 用户平均评分 | 初始值 | 提升至 4.0+ |
| RAG 命中率 | 初始值 | 提升至 90%+ |
| 每周使用量 | 初始值 | 持续增长 |

---

## 七、注意事项

1. **不要阻塞主流程**：自进化钩子应异步执行，不影响推算响应的速度
2. **日志容错**：日志记录失败不应影响主工作流，使用 try/except 包裹
3. **数据隐私**：日志中不记录用户身份信息，仅记录推算参数和 RAG 键
4. **定期审查**：每周审查报告，根据数据驱动决策更新 RAG 知识库
5. **反馈频率**：反馈邀请不要过于频繁，同一会话最多邀请一次
