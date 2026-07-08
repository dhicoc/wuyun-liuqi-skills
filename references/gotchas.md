# Agent 常见失误（Gotchas）

> 可复现、高成本的 Agent 行为失误记录在此。记录门槛见 `workflows/task-closure.md`。

## 推算层

| 失误 | 正确做法 |
|------|----------|
| 凭记忆报司天在泉 | `python scripts/calculate_yunqi_api.py <日期> --json` |
| 公历 1 月 1 日当年运气 | 大寒定年：1 月大寒前属上一年运气 |
| 只读 routing.md 不全表 | 以 `routing.yaml` 为单一真相源 |

## 临床层

| 失误 | 正确做法 |
|------|----------|
| 给方药无免责声明 | 先读 `rules/medical-safety.md`，末尾附声明 |
| 给出具体克数剂量 | 仅方向性参考，标注须辨证 |

## 路由层

| 失误 | 正确做法 |
|------|----------|
| 仅触发词就输出完整临床报告 | 先 `prompts/onboarding_prompt.md` 澄清意图 |
| 跨项目对话技能不激活 | 运行 `install.py --link-global` 或打开技能包工作区 |

## 维护

满足记录门槛（重复 + 高成本 + 非显而易见）时，由 `self_evolve.py rule-gap` 提议，人工确认后写入本表。