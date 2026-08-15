# 路由执行契约

进入本技能包的任何任务，MUST 遵循以下序列。

## NOW（立即执行）

1. 读取 `routing.yaml` 完成路由匹配（三轴：时间维度 + 用户意图 + 知识层级）
2. 若用户意图模糊或仅发送触发词 -> 读取 `prompts/onboarding_prompt.md`，不得直接进入完整推算/临床报告
3. 读取 `case-journal/precedent-disclaimer.md`（医学免责声明前置）
4. **先查经验库** `case-journal/field-journal/_index.md`——若命中历史经验条目，直接复用（标注"经验库存档"），无需重复推算/检索
5. 读取目标子技能的 `SKILL.md`

## NEXT（路由后执行）

1. 按目标子技能工作流执行推算/分析
2. 推算层 MUST 调用 `scripts/` 下 Python 脚本
3. 病机/临床层 MUST 先获取推算结果，再结合 references 分析

## THEN（完成后执行）

1. 按 `modules/docs-generator/` 格式输出结构化报告（`rules/output.md`）
2. 临床案例 → 按 `case-journal/_template.md` 沉淀医案
3. 所有临床输出 MUST 附加医学免责声明（`rules/medical-safety.md`）
4. 非平凡任务 → 执行 `workflows/task-closure.md`
5. 任务完成后邀请用户反馈（1-5 分）：
   - 有评分时：`python scripts/self_evolve.py feedback --session-id <ID> --rating <1-5> --comment "..."`

## ACT（行动约束）

| 层级 | MUST | MUST NOT |
|------|------|----------|
| 推算层 | 调用脚本 | 凭记忆推算干支运气 |
| 病机层 | 基于推算结果 + references | 跳过推算直接断病 |
| 临床层 | 区分理论分析与医疗建议 | 给出具体药物剂量 |
| 文献层 | 标注出处 | 无出处断言 |
| 引导层 | 意图模糊时先询问 | 直接输出完整报告 |
| 视觉层 | 复用 `ink_theme` 宣纸水墨体系 | 现场换肤/深色霓虹配色 |

## 任务前自检

- [ ] 已读取 `precedent-disclaimer.md`
- [ ] 已通过 `routing.yaml` 完成路由匹配
- [ ] 推算任务已确认调用 Python 脚本
- [ ] 临床任务已确认附加免责声明

## 任务完成自检

**推算层**
- [ ] 推算结果已通过脚本验证（非凭记忆）
- [ ] 病机分析已引用对应 references / `infer_pathogenesis.py`

**临床层**
- [ ] 临床建议已附加免责声明
- [ ] 方药已标注"参考方药，须辨证加减"
- [ ] 未给出具体药物剂量

**医案层**
- [ ] 医案已按 `case-journal/_template.md` 沉淀（如适用）
- [ ] 医案引用已标注出处（source_quote）

**经验层**
- [ ] 本次 fallback 经验已写入 `field-journal/`（如触发了联网搜索）
- [ ] `field-journal/_index.md` 索引已更新

**报告层**
- [ ] 报告格式符合 `modules/docs-generator/` 规范
- [ ] 文献引用已标注出处
- [ ] 视觉产物（HTML/UI）已复用 `ink_theme` 宣纸水墨体系（非现场换肤）