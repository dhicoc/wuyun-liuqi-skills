# 任务闭环（Task Closure）

> 非平凡任务（推算、报告、临床参考、安装）结束前执行。格式/注释微调可跳过。

## 1. 30 秒自检

- [ ] 推算是否经 Python 脚本验证？（`rules/calculation.md`）
- [ ] 临床输出是否含免责声明？（`rules/medical-safety.md`）
- [ ] 路由是否匹配 `routing.yaml` 且无强行套模块？
- [ ] 报告格式是否符合 `docs-generator/`？

## 2. 记录门槛（2/3 原则）

仅当满足 **至少 2 条** 时，才沉淀为规则/经验：

1. **可复现** — 同类任务会再次遇到
2. **高成本** — 出错会误导用户或浪费大量 token
3. **非显而易见** — 读代码/脚本仍易再犯

| 类型 | 写入位置 |
|------|----------|
| MUST / MUST NOT 级约束 | `rules/*.md`（经确认） |
| 行为失误、踩坑 | `references/gotchas.md` |
| 使用统计、反馈 | `scripts/self_evolve.py` |

## 3. 自进化命令

```bash
# 使用日志
python scripts/self_evolve.py log --input <日期> --rag-keys <keys> --source task_closure

# 用户反馈（任务末尾邀请 1–5 分）
python scripts/self_evolve.py feedback --session-id <id> --rating <1-5> --comment "..."

# 提议规则盲区（待人工合并进 gotchas/rules）
python scripts/self_evolve.py rule-gap --category routing --description "..."
```

## 4. 月度回顾

```bash
python scripts/self_evolve.py monthly-report
```

报告含 `rule_gaps` 汇总时，优先处理高频盲区并更新 `references/gotchas.md`。