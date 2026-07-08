# 项目架构

本文档概述五运六气 AI Agent 技能包的主要架构边界、执行链路与运行时约定。

## 1. 架构目标

本项目不是传统单一 Python 库，而是面向 AI Agent 的技能包。核心目标是：

1. 用强规则脚本完成五运六气推算，避免凭记忆推算。
2. 用结构化 RAG 知识库（7 assets）补充病机、方药、注家、地域、体质知识。
3. **用思想层解读 + 概念哲学帮助人类理解运气学思想体系**（天人合一、气化、中和等）。
4. 用子技能目录承载不同知识层级，便于 AI Agent 路由。
5. 用报告、可视化、导出（思想摘要/卡片/PDF）输出可学习材料。
6. 用自进化系统（概念追踪 + 理解反馈 + 隐私保护）持续优化讲解质量。
7. 强化人类 UX（today、引导、颜色、onboarding）和 Agent 友好性。

## 2. 主链路

```text
用户输入（自然语言，可模糊）
  ↓
routing.md + prompts/onboarding_prompt.md（模糊意图先引导）
  ↓
SKILL.md / 子技能 SKILL.md
  ↓
scripts/calculate_yunqi_api.py（Python 主链路，支持 today / --level / --explain-concept / --export）
  ↓
rag-knowledge-base/ (7 assets) 精确检索
  ↓
yunqi-pathogenesis/ 病机分析
  ↓
yunqi_report.py / generate_html_report.py（含思想层解读 build_thought_layer_section）
  ↓
思想层解读 + 引导性反思问题 + 概念哲学
  ↓
export_thought.py（思想摘要 / Anki卡片 / PDF/HTML）
  ↓
reports/generated/ + scripts/self_evolve.py（概念追踪 + 理解反馈 + 隐私保护 + 自动记录）
```

## 3. 目录分工

| 目录 | 定位 |
|------|------|
| `scripts/` | 可执行工具、推算引擎（含 --level/--export）、export_thought.py、报告生成、自进化 CLI |
| `scripts/lib/` | 推算共享数据表与底层规则 |
| `rag-knowledge-base/` | RAG 结构化知识资产（7 assets） |
| `ganzhi-basics/` | 干支基础子技能 |
| `yunqi-calc/` | 五运六气推算子技能 |
| `yunqi-pathogenesis/` | 病机分析子技能 |
| `yunqi-clinical/` | 临床参考与养生调理子技能 |
| `yunqi-classics/` | 经典文献与研究资料子技能 |
| `prompts/` | onboarding + system prompt（思想伙伴语气） |
| `docs-generator/` | 报告模板与输出规范 |
| `advanced-alignment/` | 天气、地域、体质等高级对齐设计 |
| `agent-workflow/` | ReAct 工作流与 Agent 执行链路 |
| `prompts/` | System Prompt 与首次引导模板 |
| `case-journal/` | 医案模板与医学免责声明 |
| `self-evolve/` | 使用日志、盲区、反馈、报告等运行时数据 |
| `reports/examples/` | 示例报告与预览图，适合纳入仓库 |
| `reports/generated/` | 本地生成报告，默认不纳入版本控制 |
| `reports/test-results/` | 测试输出，默认不纳入版本控制 |
| `.github/workflows/` | CI 工作流 |
| `tests/` | 测试夹具与后续测试迁移目标 |

## 4. Python 主链路与 JS 可选接口

- Python 主链路：`scripts/calculate_yunqi_api.py`
  - 用于 AI Agent、RAG keys、报告、可视化与回归测试。
- JavaScript 可选接口：`scripts/calculate_yunqi_api.js`
  - 用于前端或 Node.js 集成。
  - 若 JS 与 Python 输出不一致，以 Python 为准。

## 5. 运行产物约定

运行产物不应与示例资产混在一起：

```text
reports/examples/      示例资产，可提交
reports/generated/     用户本地生成报告，忽略
reports/test-results/  测试输出，忽略
self-evolve/*          自进化运行时数据，忽略
```

## 6. 验证链路

推荐本地或 CI 执行：

```bash
python scripts/health_check.py
python scripts/validate_knowledge_base.py
python scripts/verify_expansion.py
python scripts/full_regression_test.py
node scripts/calculate_yunqi_api.js 2026-06-29 --json
```

## 7. 医学安全边界

所有病机、方药、针灸与养生内容均为传统中医运气学理论参考，不构成现代医学诊断或治疗建议。涉及临床内容时必须附加免责声明，并提醒具体诊疗须由执业医师辨证处理。
