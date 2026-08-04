# 注家人格 Perspective Skills

> 把五运六气史上的对立注家做成可运行的 perspective skill（人物思维操作系统），Agent 激活后能**切换到注家视角**回答问题，而非"替注家说话"。
>
> 采用 [女娲 · Skill造人术](https://github.com/alchaincyf/nuwa-skill) 的 perspective skill 模式（SKILL.md + FIDELITY.md + 调研来源），素材为公版中医古籍（已蒸馏入 `rag-knowledge-base/`）。

## 两位注家：运气学史上最尖锐的对立

| Perspective | 注家 | 朝代 | 派别 | 核心立场 | 目录 |
|-------------|------|------|------|----------|------|
| `liu-wansu-perspective` | 刘完素（河间） | 金 | 寒凉派 | 六气皆从火化、不可峻用辛温大热、兼化是虚象不可误治 | `liu-wansu-perspective/` |
| `zhang-jiebin-perspective` | 张介宾（景岳） | 明 | 温补派 | 阳气为本命门为根、五行互藏、生中有克克中有用、造化不可无制 | `zhang-jiebin-perspective/` |

**对立张力**：刘完素戒辛温（"纵获一效其祸数作"），张介宾重温养（"阳气为本"）——同一运气学，一从火化立论，一从阳气温补立论。这两方原文都能在 `rag-knowledge-base/` Grep 到，Agent 可做真实注家对照。

## 激活方式

用户说以下任一即触发对应 perspective：
- **刘完素**：「刘完素视角」「河间怎么看」「寒凉派」「六气皆从火化」「切换到刘完素」「用河间的角度想想」
- **张介宾**：「张介宾视角」「张景岳怎么看」「温补派」「阳气为本」「切换到张介宾」「用景岳的角度想想」

激活后 Agent 直接以该注家第一人称回应，直到用户说「退出」「切回正常」。

## 与 expression_style.md 的关系

`prompts/expression_style.md` 的"注家对照模式"原本是**静态**的——我在 expression_style 里手写"王冰认为……张介宾却认为……我倾向……"。

现在升级为**动态可运行**：
- **轻量对照**（默认）：仍走 expression_style 注家对照模式，由运气导师口吻概述两方立场
- **深度扮演**（用户要求）：切换到对应 perspective skill，让注家"自己说话"——刘完素以"……者……也"断之，张介宾以"盖……故……"推之

两者互补：expression_style 适合快速概述分歧，perspective skill 适合深度沉浸式问答。

## 与蒸馏指南的关系

每个 perspective 的"调研来源"指向已蒸馏的公版指南：

| Perspective | 一手来源（蒸馏指南） |
|-------------|-------------------|
| 刘完素 | `rag-knowledge-base/suwen_xuanji_pathogenesis_guide.md`（病机+兼化）+ `baoming_zhifa_guide.md`（治法+寒凉宣言） |
| 张介宾 | `rag-knowledge-base/leijing_tuyi_yunqi_philosophy_guide.md`（太极阴阳五行+生克互藏） |

Agent 扮演时可 Grep 这些指南取原文佐证，确保"引用可分辨"（原话 vs 框架推断）。

## 保真度

每个 perspective 含 `FIDELITY.md`（保真度评分卡），按 nuwa-skill 的五维标准评估：
- 立场一致性 / 风格辨识度 / 边缘诚实度 / 来源透明度 / 结构完整度
- 两位均通过静态结构检查（等级A），待独立双 agent 实测补全动态评分

## 诚实边界（重要）

- perspective 呈现的是该注家**个人学术立场**，非现代医学共识
- 刘完素"六气皆从火化"与张介宾"阳气为本"是对立的两家之言，临床须辨证取舍
- 角色 Skill 激活时的免责声明仅首次说一次，但**临床/方药问题仍须切回临床模式并附项目免责声明**

---

> ⚠️ 免责：perspective skill 为公版古籍人物思维模拟，仅作运气学理论探讨参考，非现代医学诊断。临床诊疗须由执业中医师辨证施治。
