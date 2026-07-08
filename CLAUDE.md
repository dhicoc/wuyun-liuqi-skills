# CLAUDE.md — 五运六气技能包入口

正式规则在 `SKILL.md` 与 `routing.yaml`。本文件为 Claude Code 兼容薄壳。

<always-applicable>

**激活**：用户提到五运六气、运气、大运、司天在泉、客主加临、运气病机、七篇大论等 → 立即读取 `SKILL.md`。

**Always Read**

- `case-journal/precedent-disclaimer.md`
- `rules/calculation.md`
- `routing.yaml`
- `workflows/routing-contract.md`

**Red Flags**

- MUST NOT 凭记忆推算 → 必须调用 `scripts/` Python 脚本
- 临床/方药/针灸 → 必须附加免责声明
- 意图模糊 → `prompts/onboarding_prompt.md`

</always-applicable>

<task-routing>

任务路由在 `routing.yaml`。每个新任务：读 YAML → 匹配 `tasks`/`axes` → 读 `required_reads` → 执行 `workflow`/`script`。摘要：`routing.md`。

</task-routing>

## Auto-Triggers

- 新任务 → 重新匹配路由
- 首次使用 → `workflows/bootstrap.md`
- 可选原生技能桩：`.claude/skills/wuyun-liuqi/SKILL.md`（指向本包 `SKILL.md`）
- Claude Code 插件：`.claude-plugin/` → `workflows/claude-plugin-install.md`

冲突时：以 `SKILL.md`、`routing.yaml` 为准。