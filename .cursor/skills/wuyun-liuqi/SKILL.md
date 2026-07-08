---
name: wuyun-liuqi
description: >
  五运六气（运气学）AI Agent 技能包。帮助人类准确理解《黄帝内经》运气学思想体系（天人合一、气化、中和、时间节律）。
  提供干支推算、思想解读、概念解释、导出复习材料、自进化优化。
  触发词：五运六气、运气、大运、主运客运、主气客气、司天在泉、客主加临、
  太过不及、天符岁会、运气病机、运气治法、七篇大论。
  面向：学生、医师（理论参考）、研究者。
---

# 五运六气（Cursor 注册入口）

正式技能内容在仓库根目录 **`SKILL.md`**。激活后立即读取该文件，并遵循其 Always Read 与 Common Tasks。

## Quick Routing

路由在根目录 `routing.yaml`（人类摘要：`routing.md`）。

每个新任务：

1. 读取 `routing.yaml`
2. 按 `labels`、`trigger_examples`、任务意图匹配
3. 读取该路由 `required_reads` + Always Read
4. 执行 `workflow` 或 `script`

首次使用另读：`workflows/bootstrap.md`