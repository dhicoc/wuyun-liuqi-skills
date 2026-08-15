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
- 生成/手写任何视觉产物（HTML/UI/卡片/时间轴）→ 必须复用 `scripts/lib/ink_theme.py`（宣纸水墨），不得擅自换肤或现场手写配色

**工具速查（按用户问题类型，agent 首读即可见）**

| 用户问 | 调用 |
|---|---|
| 今年运气/推算 | `python scripts/calculate_yunqi_api.py today` |
| 今年什么病机/该用什么治法/三因司天方 | `python scripts/infer_pathogenesis.py today` |
| 历代医家怎么治某病 | `python scripts/rag_search.py <病证> --asset asset26,asset27,asset16` |
| 哪些医案用了某药/某方 | `python scripts/rag_search.py --field herbs 石膏` 或 `--field formulas_referenced 小柴胡汤` |
| 两位医家治某病有什么不同 | `python scripts/case_relations.py --compare 孙一奎,叶桂 --tag 中风` |
| 这个医案还有谁治过类似的 | `python scripts/case_relations.py --related swy_174` |
| 生成运气时间轴 | `python scripts/visualize_timeline.py 2026 --output timeline.html` |

**Fallback 策略（工具未命中时）**

当用户问题无法用上述工具回答时：
1. 联网搜索 -> 总结回答用户（标注来源 + 免责声明）
2. 沉淀经验到 `case-journal/field-journal/`（模板见 `_template.md`，索引更新 `_index.md`）
   - **source_quote MUST 填写**：从来源摘录原文，非自己改写；无原文时填"无原文存证，来源为二手资料"
   - **confidence MUST 选择**：高（学术论文/教材）/中（专业网站/百科）/低（博客/自媒体）
3. 下次类似问题：知识库命中则直接用；知识库未命中才查经验库，引用时标注"经验库存档（非原文）"+ 置信度

查询优先级：知识库(rag_search，有原文存证) -> 经验库(field-journal，非原文) -> 联网搜索 -> 沉淀

> ⚠️ 经验库条目不是公版医案原文，可信度取决于来源质量。低置信度条目不建议直接引用。

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