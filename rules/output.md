# 输出规范规则（R6）

## MUST

- 综合报告遵循 `modules/docs-generator/SKILL.md`
- 文献引用标注出处（素问篇名 / 历代医家 / 现代文献）
- 医案使用 `case-journal/_template.md`，患者信息脱敏
- **引用医案/知识库条目时，摘录与稳定引用必须同时出现**：格式 `yle:<asset>:<entry_id>`（如 `yle:asset13_gujin_an_cases:gujin_001`）。asset 为知识库文件名（去 `.json`），entry_id 为条目稳定唯一键。可用 `scripts/resolve_ref.py` 反解并核验引用可访问；纯定位符（无摘录）不得单独作为医案回答。

## SHOULD

- 按受众调整深度：`student` | `practitioner` | `researcher`
- 任务结束邀请反馈 → `scripts/self_evolve.py feedback`
- 发现可复现 Agent 失误 → `workflows/task-closure.md` 记录门槛

## 报告类型

| 受众 | 入口 |
|------|------|
| 学生 | `yunqi_report.py --audience student` |
| 临床 | `yunqi_report.py --audience practitioner` |
| 研究 | `yunqi_report.py --audience researcher` |