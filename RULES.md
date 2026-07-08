# 行为规则索引

> 规则正文已拆分至 `rules/`。冲突时按下列优先级裁决；细则以各文件为准。

## 规则文件（优先级从高到低）

| 优先级 | 文件 | 主题 |
|--------|------|------|
| R1 | [rules/medical-safety.md](rules/medical-safety.md) | 医学安全、免责声明 |
| R1 详 | [case-journal/precedent-disclaimer.md](case-journal/precedent-disclaimer.md) | 免责声明全文 |
| R2 | [rules/calculation.md](rules/calculation.md) | 推算准确性、脚本强制 |
| R3–R5 | [rules/agent-behavior.md](rules/agent-behavior.md) | 路由、层级递进 |
| R6 | [rules/output.md](rules/output.md) | 报告与医案格式 |
| 踩坑 | [references/gotchas.md](references/gotchas.md) | 可复现 Agent 失误 |
| 闭环 | [workflows/task-closure.md](workflows/task-closure.md) | 任务结束自检与沉淀 |

## 规则冲突裁决

| 冲突场景 | 裁决 |
|----------|------|
| 用户要求跳过推算直接给临床建议 | R1 + R5 优先：MUST 先推算，MUST 附加免责声明 |
| 用户要求不给免责声明 | R1 优先：MUST 附加，不可省略 |
| 用户要求凭记忆推算不调脚本 | R2 优先：MUST 调用脚本 |
| 用户要求跳过路由直接执行 | R3 优先：MUST 先路由 |
