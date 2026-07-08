# 推算准确性规则（R2）

## MUST

- 干支、大运、六气、客主加临等可计算结果 → 调用 `scripts/` 下 **Python** 脚本
- 日期入口优先：`scripts/calculate_yunqi_api.py`（大寒定年、`rag_keys`）
- 需要机器可读结果时使用 `--json`

## MUST NOT

- 凭记忆或估算推算运气格局
- 跳过脚本直接给出司天在泉、岁运太过不及等数值结论

## SHOULD

- 关键结果与分项脚本交叉核对（如 `dayun_calc.py` 与 API 输出一致）
- JS 版仅在前端/Node 集成时使用；与 Python 不一致时 **以 Python 为准**

脚本索引：`references/script-index.md`