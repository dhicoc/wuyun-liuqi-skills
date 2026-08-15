# 输出规范规则（R6）

## MUST

- 综合报告遵循 `modules/docs-generator/SKILL.md`
- 文献引用标注出处（素问篇名 / 历代医家 / 现代文献）
- 医案使用 `case-journal/_template.md`，患者信息脱敏
- **引用医案/知识库条目时，摘录与稳定引用必须同时出现**：格式 `yle:<asset>:<entry_id>`（如 `yle:asset13_gujin_an_cases:gujin_001`）。asset 为知识库文件名（去 `.json`），entry_id 为条目稳定唯一键。可用 `scripts/resolve_ref.py` 反解并核验引用可访问；纯定位符（无摘录）不得单独作为医案回答。
- **任何面向读者的视觉产物必须复用宣纸水墨设计体系**：HTML 报告 / PDF / 卡片 / 时间轴 / Anki 等，一律复用 `scripts/lib/ink_theme.py` 导出的设计 token（五行正色、墨色阶、纸色、朱砂、宋体），**禁止 agent 现场自由发挥视觉风格**（如深色霓虹配色）。视觉产物须引用 ink_theme 导出的 CSS 变量（`--paper` / `--ink` / `--vermilion` / `--wx-*` 等）；agent 手写 HTML/UI 同样必须先调用 `ink_theme`。可用 `scripts/check_visual_consistency.py` 做一致性关卡。

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