# Agent 行为规则（R3–R5）

## 路由（R3）

- **MUST** 先读 `routing.yaml` 匹配任务，再进入子技能
- **MUST NOT** 跳过路由直接执行
- 意图模糊 → `prompts/onboarding_prompt.md`
- 路由未命中 → `routing.yaml` → `on_miss`，不得强行匹配

## 知识层级（R5）

```text
推算层 → 病机层 → 临床层
文献层可随时穿插
```

- **MUST NOT** 无推算结果就断病机
- **MUST NOT** 无病机分析就给临床建议

## 任务闭环

非平凡任务结束前执行 `workflows/task-closure.md`（30 秒自检 + 可选沉淀）。

执行契约：`workflows/routing-contract.md`