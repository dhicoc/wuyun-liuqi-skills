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
- 讲解模式触发（学概念/思想/注家对照）→ 加载 `prompts/expression_style.md`，深度扮演加载 `perspectives/`
- 注家对照/引经据典 → 优先 Grep `rag-knowledge-base/*_guide.md`（蒸馏指南）或 `literature/`（原文）
- 同格局医案 → `rag_search --key <rag_key> --asset asset9`（圣济总录 60 岁图医案，按格局检索）
- 历代名家临证医案 → `rag_search --asset asset11/12/13/14/15/16`（名医类案/续名医类案/古今医案按/丁甘仁/伤寒九十论/临证指南，共 901 条，按病证检索）

</always-applicable>

<task-routing>

任务路由在 `routing.yaml`。每个新任务：读 YAML → 匹配 `tasks`/`axes` → 读 `required_reads` → 执行 `workflow`/`script`。摘要：`routing.md`。

</task-routing>

## Auto-Triggers

- 新任务 → 重新匹配路由
- 首次使用 → `workflows/bootstrap.md`
- 可选原生技能桩：`.claude/skills/wuyun-liuqi/SKILL.md`（指向本包 `SKILL.md`）
- Claude Code 插件：`.claude-plugin/` → `workflows/claude-plugin-install.md`
- 讲解模式（学概念/思想/天人合一/注家对照）→ `prompts/expression_style.md` + `teaching-modules/` + `rag-knowledge-base/*_guide.md`
- 深度注家扮演（刘完素/张介宾视角）→ `perspectives/`

冲突时：以 `SKILL.md`、`routing.yaml` 为准。