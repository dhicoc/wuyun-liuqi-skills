# 教学模块目录 (teaching-modules/)

> 可独立加载的运气学概念教学模块。每个模块对应一个高频概念，采用**五段式 + 思想层**结构，供「讲解模式」（`prompts/expression_style.md`）与 `--explain-concept` 调用。
>
> 这是本项目「知识表达从键值检索升级到可教学模块」的载体：RAG asset 回答"是什么"，教学模块回答"为什么古人这么看、怎么讲清楚、常见误区在哪"。

## 加载机制

- `scripts/yunqi_report.py::load_concept(name)` 读取本目录下 `<name>.md`，解析 YAML frontmatter + 正文。
- `explain_concept(name)` 优先调用 `load_concept`；模块缺失时回退到内置 `CONCEPT_PHILOSOPHY` 字典（向后兼容）。
- 模块 frontmatter 必须含 `philosophy` / `modern` / `example` 三字段（兼容旧消费者 `export_thought.py` / `export_thought_map.py` / `socratic_learn.py`）。

## 模块字段（五段式 + 思想层）

| 字段 | 说明 |
|------|------|
| `concept` | 概念名（与文件名一致） |
| `category` | 分类（根观念 / 格局 / 推移 / 同化 / 病机 / 治则） |
| `philosophy` | 哲学思想（一句话，兼容旧字段） |
| `modern` | 现代比喻（兼容旧字段） |
| `example` | 应用示例（兼容旧字段） |
| `original_text` | 经典原文 + 篇名 |
| `commentaries` | 注家观点对照（医家 → 观点，含分歧） |
| `my_reading` | 本项目综合解读（口语化、有立场，用运气导师人格） |
| `golden_quote` | 可引用金句 |
| `common_misconceptions` | 常见误区 → 纠正 |
| `depth_levels` | simple / standard / deep 三层展开 |

## 首批模块清单

| 概念 | 分类 | 文件 |
|------|------|------|
| 天人合一 | 根观念 | `天人合一.md` |
| 气化 | 根观念 | `气化.md` |
| 中和 | 根观念 | `中和.md` |
| 司天在泉 | 格局 | `司天在泉.md` |
| 客主加临 | 格局 | `客主加临.md` |
| 大运·岁运 | 格局 | `大运岁运.md` |
| 太过不及 | 格局 | `太过不及.md` |
| 平气 | 格局 | `平气.md` |
| 天符岁会 | 同化 | `天符岁会.md` |
| 五运推移 | 推移 | `五运推移.md` |

> 临床/病机层概念（六气病机、运气合病等）后续按需补充，归入 `yunqi-pathogenesis/` 联动。
