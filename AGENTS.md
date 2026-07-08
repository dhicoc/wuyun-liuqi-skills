# AGENTS.md — 五运六气技能包入口

中医运气学 AI Agent 技能包。正式规则在 `SKILL.md` 与 `routing.yaml`；本文件为薄壳，不重复规则正文。

<always-applicable>

**激活**：用户提到五运六气、运气、大运、司天在泉、客主加临、运气病机、七篇大论等 → 立即读取 `SKILL.md`。

**Always Read（每个运气任务）**

- `case-journal/precedent-disclaimer.md`
- `rules/calculation.md`
- `routing.yaml`
- `workflows/routing-contract.md`

**Red Flags**

- MUST NOT 凭记忆推算 → 必须调用 `scripts/` 下 Python 脚本
- 临床/方药/针灸 → 必须附加免责声明
- 意图模糊 → 先读 `prompts/onboarding_prompt.md`

</always-applicable>

<task-routing>

**Quick Routing**

路由单一真相源：`routing.yaml`（摘要见 `routing.md`）。

每个新任务：

1. 读取 `routing.yaml`
2. 匹配 `tasks` / `axes` / `trigger_examples`
3. 读取该路由 `required_reads` + Always Read
4. 执行 `workflow` 或 `script`

</task-routing>

## Auto-Triggers

- 新任务 → 重新匹配 `routing.yaml`
- 首次使用 → `workflows/bootstrap.md`
- Agent 全链路细节 → `README_AI.md`

冲突时：以 `SKILL.md`、`routing.yaml`、`workflows/routing-contract.md` 为准。