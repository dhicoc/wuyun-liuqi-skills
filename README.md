# 五运六气 AI Agent 技能包

> 基于中医运气学说（《黄帝内经》素问七篇大论），运用天干地支推算年度气候与疾病规律的 AI Agent 技能包。
>
> 架构改编自 [reverse-skill](https://github.com/zhaoxuya520/reverse-skill)（裁剪复用策略）。

> 本仓库可放置在任何目录。AI 会自动检测实际路径。下文 `<SKILL_ROOT>` 指实际安装路径。

---

## 0. AI 自动配置流程（AI Agent 首次读取本文后立即执行）

> **AI 读完本文件后，必须自动执行以下配置流程，用户无需手动操作。**

```text
0. 检测本包安装路径（由当前文件所在目录推导）
1. 检测操作系统的包管理器：
   - Windows → 执行 scripts/setup.bat
   - Linux/macOS → 执行 bash scripts/setup.sh
2. 配置脚本自动完成以下步骤：
   a. 检测 Python 版本
   b. 安装 lunar-python（pip install）
   c. 创建自进化运行时目录（logs/misses/feedback/reports）
   d. 可选检测 Node.js（仅 JS 版需要）
3. 确认所有依赖就绪后，读取 routing.md → 匹配用户任务 → 进入对应子技能
4. 开始执行任务
```

### 一句话配置（人类用户）

```bash
# Windows (PowerShell/cmd)
scripts\setup.bat

# Linux/macOS
bash scripts/setup.sh
```

配置完成后即可使用所有功能。

---

## 功能概览

- **推算层**：给定任意公历日期或年份，计算天干地支、大运太过不及、主运客运、司天在泉、客气六步、客主加临顺逆、天符岁会太乙天符
- **病机层**：基于推算结果分析五运病机、六气病机、太过不及胜复、运气合病
- **临床层**：运气治则治法、参考方药、针灸选穴、养生调理
- **文献层**：素问七篇大论索引、历代运气学说、现代研究概况
- **医案沉淀**：运气应用医案记录与索引
- **Agent 集成**：统一计算接口（大寒定年 + 标准化JSON）、RAG知识库（5 层 104 键）、ReAct推理工作流、System Prompt、天气/体质高级对齐、自进化引擎

## 快速开始

### 推算某年运气

```bash
# 综合报告（简明版，适合学生）
python scripts/yunqi_report.py 2026 --audience student

# 综合报告（临床版，适合医师）
python scripts/yunqi_report.py 2026 --audience practitioner

# 综合报告（研究版，适合研究者）
python scripts/yunqi_report.py 2026 --audience researcher

# 单项推算
python scripts/ganzhi_calc.py 2026       # 干支推算
python scripts/dayun_calc.py 2026        # 大运推算
python scripts/keyun_calc.py 2026        # 主运客运
python scripts/liuqi_calc.py 2026        # 六气推算
python scripts/kezhujialin.py 2026       # 客主加临

# JSON 输出（机器可读）
python scripts/dayun_calc.py 2026 --json
```

### 基于日期的统一推算（Agent 推荐入口）

```bash
# Python: 大寒定年，输出标准化 JSON（含 RAG 检索键）
python scripts/calculate_yunqi_api.py 2026-06-27 --json

# JavaScript: 同功能（需 npm install lunar-javascript）
node scripts/calculate_yunqi_api.js 2026-06-27 --json

# 大寒边界测试: 2026-01-15 → 运气年 2025(乙巳), 2026-01-20 → 运气年 2026(丙午)
python scripts/calculate_yunqi_api.py 2026-01-15 --json
python scripts/calculate_yunqi_api.py 2026-01-20 --json
```

### 全链路演示（推算 → RAG 检索 → 方剂 → 体质）

```bash
# 演示任意日期的完整分析流程
python scripts/demo_full_chain.py 2026-06-27
```

### 环境要求

- Python 3.8+，推荐安装 `lunar-python`（精确节气计算）：`pip install -r requirements.txt`
- Node.js 14+（JS版），需安装 `lunar-javascript`：`npm install`
- 无 lunar 库时自动降级为近似节气日期（大寒=1月20日）

## 目录结构

```
wuyun-liuqi/
├── SKILL.md                    # 总控入口 + 路由执行契约
├── routing.md                  # 三轴路由矩阵
├── RULES.md                    # 行为规则链
├── CONTRIBUTING.md             # 新增子技能指南
├── LICENSE                     # MIT 许可证
├── .gitignore
├── requirements.txt            # Python 依赖
├── package.json                # Node.js 依赖
├── README.md                   # 本文件
│
├── scripts/                    # 推算引擎（Python + JavaScript 双语言）
│   ├── lib/
│   │   ├── yunqi_data.py       # 共享数据表（Python）
│   │   └── yunqi_data.js       # 共享数据表（JavaScript）
│   ├── ganzhi_calc.py          # 干支推算
│   ├── dayun_calc.py           # 大运推算
│   ├── keyun_calc.py           # 主运客运
│   ├── liuqi_calc.py           # 六气推算
│   ├── kezhujialin.py          # 客主加临
│   ├── yunqi_report.py         # 综合报告
│   ├── calculate_yunqi_api.py  # ★ 统一计算接口（大寒定年 + JSON）
│   ├── calculate_yunqi_api.js  # ★ JS版统一接口
│   ├── ingest_literature.py    # ★ 文献注入管道
│   ├── self_evolve.py          # ★ 自进化引擎
│   ├── verify_expansion.py     # 端到端验证（67 项测试）
│   └── demo_full_chain.py      # 全链路演示
│
├── rag-knowledge-base/         # ★ RAG知识库（5 层覆盖）
│   ├── asset1_suiyun.json      # 岁运病机（10条）
│   ├── asset2_sitian_zaiquan.json # 司天在泉病机（6对）
│   ├── asset3_kezhujialin.json # 客主加临病机（36条）
│   ├── asset4_formula.json     # 三因司天方（16首运气方剂）
│   ├── asset5_commentary.json  # 历代注家（20条）
│   ├── asset6_regional.json    # 地域修正（8区）
│   ├── asset7_constitution.json # 运气体质交叉（18条）
│   ├── LITERATURE_EXPANSION.md # 文献扩充指南
│   └── README.md               # 知识库使用说明
│
├── self-evolve/                # ★ 自进化引擎
│   ├── README.md               # 使用指南
│   ├── logs/                   # 使用日志（gitignore）
│   ├── misses/                 # 盲区记录（gitignore）
│   ├── feedback/               # 反馈采集（gitignore）
│   └── reports/                # 优化报告（gitignore）
│
├── agent-workflow/             # ★ ReAct推理工作流
│   ├── react_workflow.md       # 工作流规范
│   ├── self_evolve_hook.md     # 自进化集成钩子
│   └── workflow_config.json    # 机器可读配置
│
├── prompts/                    # ★ System Prompt
│   └── system_prompt.md        # TCM运气专家角色
│
├── advanced-alignment/         # ★ 高级对齐
│   ├── weather_integration.md  # 天气API对齐
│   ├── constitution_alignment.md # 体质报告交叉分析
│   └── api_specs.json          # API规格定义
│
├── ganzhi-basics/              # 子技能1：干支基础
├── yunqi-calc/                 # 子技能2：运气推算（核心）
├── yunqi-pathogenesis/         # 子技能3：病机分析
├── yunqi-clinical/             # 子技能4：临床应用
├── yunqi-classics/             # 子技能5：经典文献
├── docs-generator/             # 子技能6：报告生成
├── docs/                       # 技术文档
└── case-journal/               # 医案沉淀系统
```

## 架构设计

### 五层 RAG 知识库

| 层 | Asset | 条目数 | 用途 |
|----|-------|--------|------|
| 经典病机 | asset1-3 | 52 | 岁运/司天/客主加临病机（素问七篇大论） |
| 运气方剂 | asset4 | 16 | 三因司天方（陈无择，含组成/病机/加减） |
| 历代注家 | asset5 | 20 | 王冰→陆懋修 11 位医家运气学说 |
| 地域修正 | asset6 | 8 | 东北/华北/西北/华东/华南/华中/西南/青藏 |
| 运气体质 | asset7 | 18 | 9 种王琦体质 × 运气出生映射 + 岁运调理 |

**104 个唯一键**覆盖经典原文、方剂、注家、地域、体质五层，通过 `rag_keys` 精确匹配。

### Agent 集成层

1. **强规则计算工具**（`calculate_yunqi_api`）：大寒定年 + 日期输入 + 标准化JSON输出 + rag_key 生成
2. **RAG 知识库**（`rag-knowledge-base/`）：5 层 key-value 结构化存储，精准检索
3. **ReAct 推理工作流**（`agent-workflow/`）：查工具→查知识库→辨证推理闭环
4. **System Prompt**（`prompts/`）：TCM 运气专家角色约束
5. **高级对齐**（`advanced-alignment/`）：天气 API 对齐 + 体质报告交叉分析
6. **自进化回路**（`self_evolve/`）：每次推理后自动记录 → 盲区检测 → 反馈采集 → 优化报告

### Agent ReAct 推理路径

```
prompts/system_prompt.md → 加载角色约束
  ↓
scripts/calculate_yunqi_api.py → 输入日期，获取标准化 JSON（含 rag_keys）
  ↓
rag-knowledge-base/ → 用 rag_keys 依次检索 5 层知识
  ↓
agent-workflow/react_workflow.md → 多层辨证推理
  ↓
advanced-alignment/ → (可选) 天气对齐 + 体质交叉分析
  ↓
输出结构化报告 + 免责声明
  ↓
scripts/self_evolve.py → 自动记录本次推理
```

### 验证

```bash
# 端到端验证（67项：大寒回归 + 资产完整性 + Key关联 + 自进化）
python scripts/verify_expansion.py
```

## 裁剪复用策略

从 reverse-skill 保留：
- 三轴路由矩阵（维度改为：时间维度 + 用户意图 + 知识层级）
- SKILL.md 标准格式（frontmatter + scope + workflow + pitfalls + 路由上下文）
- ACTION REQUIRED + 任务完成自检
- case-journal 经验沉淀系统（field-journal 的改造版）

从 reverse-skill 裁剪：
- manifest 驱动自举系统（五运六气不需要安装外部工具）
- bootstrap/ToolDiscovery/tool-index
- MCP 服务器注册
- 多平台 PowerShell/Bash 脚本对等（改用纯 Python）

## 免责声明

运气学说为中医传统理论，非现代医学诊断标准。本技能包输出的临床分析仅供参考，具体诊疗须由执业中医师辨证论治。

## 许可证

MIT License. 详见 [LICENSE](LICENSE)。

## 致谢

- 架构设计参考 [reverse-skill](https://github.com/zhaoxuya520/reverse-skill)（zhaoxuya520）
- 理论依据：《黄帝内经·素问》七篇大论

## 友情链接

[Linux.do](https://linux.do)是一个非常友好的社区。感谢LINUX.DO的所有人给我灵感和勇气。

---

> **English Version / 英文版**

---

# WuYun-LiuQi (Five Movements & Six Qi) AI Agent Skill Pack

> An AI Agent Skill Pack based on the TCM Yunqi (Fortune-Qi) theory from the "Yellow Emperor's Inner Classic" (Suwen seven major treatises), using Heavenly Stems and Earthly Branches to calculate annual climate and disease patterns.
>
> Architecture adapted from [reverse-skill](https://github.com/zhaoxuya520/reverse-skill) (reuse strategy with reduction).

This repository can be placed in any directory. The AI will auto-detect its actual path. `<SKILL_ROOT>` refers to the real installation path.

---

## 0. AI Auto-Configuration Flow (Execute Immediately After Reading)

> **After reading this file, the AI must automatically execute the following configuration — no manual operation required.**

```text
0. Detect the installation path (derived from this file's directory)
1. Detect OS package manager:
   - Windows → run scripts/setup.bat
   - Linux/macOS → run bash scripts/setup.sh
2. Setup script auto-completes:
   a. Check Python version
   b. Install lunar-python (pip install)
   c. Create self-evolution runtime dirs (logs/misses/feedback/reports)
   d. Optional: detect Node.js (JS version only)
3. Once dependencies are ready, read routing.md → match user task → enter corresponding sub-skill
4. Start task execution
```

### Quick Setup (Human Users)

```bash
# Windows (PowerShell/cmd)
scripts\setup.bat

# Linux/macOS
bash scripts/setup.sh
```

---

## Feature Overview

- **Calculation Layer**: Given any Gregorian date or year, compute Heavenly Stems & Earthly Branches, Great Movement (Dayun) excess/deficiency, Host/Guest Movement, Sitian-Zaiquan, Guest Qi six steps, Kezhu-Jialin (guest-host interaction), Tianfu-Suihui-Taiyi-Tianfu
- **Pathogenesis Layer**: Analyze Five Movements pathogenesis, Six Qi pathogenesis, excess-deficiency victory-recovery, combined disease patterns
- **Clinical Layer**: Treatment principles, formula references, acupuncture points, health cultivation
- **Literature Layer**: Suwen seven major treatise index, historical Yunqi theories, modern research overview
- **Case Sedimentation**: Yunqi application case records and index
- **Agent Integration**: Unified calculation API (Dahan year-definition + standardized JSON), RAG knowledge base (5 layers, 104 keys), ReAct reasoning workflow, System Prompt, weather/constitution alignment, self-evolving engine

## Quick Start

### Calculate Yearly Fortune

```bash
# Comprehensive report (student edition)
python scripts/yunqi_report.py 2026 --audience student

# Comprehensive report (practitioner edition)
python scripts/yunqi_report.py 2026 --audience practitioner

# Comprehensive report (researcher edition)
python scripts/yunqi_report.py 2026 --audience researcher

# Individual calculations
python scripts/ganzhi_calc.py 2026       # Ganzhi calculation
python scripts/dayun_calc.py 2026        # Great Movement
python scripts/keyun_calc.py 2026        # Host/Guest Movement
python scripts/liuqi_calc.py 2026        # Six Qi
python scripts/kezhujialin.py 2026       # Guest-Host interaction

# JSON output (machine-readable)
python scripts/dayun_calc.py 2026 --json
```

### Date-Based Unified Calculation (Agent Recommended Entry)

```bash
# Python: Dahan year-definition, standardized JSON output (with rag_keys)
python scripts/calculate_yunqi_api.py 2026-06-27 --json

# JavaScript: same function (requires npm install lunar-javascript)
node scripts/calculate_yunqi_api.js 2026-06-27 --json

# Dahan boundary test: 2026-01-15 → Fortune year 2025(Yisi), 2026-01-20 → Fortune year 2026(Bingwu)
python scripts/calculate_yunqi_api.py 2026-01-15 --json
python scripts/calculate_yunqi_api.py 2026-01-20 --json
```

### Full Chain Demo (Calculation → RAG → Formula → Constitution)

```bash
python scripts/demo_full_chain.py 2026-06-27
```

### Requirements

- Python 3.8+, recommended `lunar-python` (accurate solar term calculation): `pip install -r requirements.txt`
- Node.js 14+ (JS version), requires `lunar-javascript`: `npm install`
- Falls back to approximate solar term dates (Dahan = Jan 20) without lunar library

## Directory Structure

```
wuyun-liuqi/
├── SKILL.md                    # Main controller + routing execution contract
├── routing.md                  # 3-axis routing matrix
├── RULES.md                    # Behavior rule chain
├── CONTRIBUTING.md             # Guide for adding sub-skills
├── LICENSE                     # MIT License
├── .gitignore
├── requirements.txt            # Python dependencies
├── package.json                # Node.js dependencies
├── README.md                   # This file
│
├── scripts/                    # Calculation engines (Python + JavaScript)
│   ├── lib/
│   ├── ganzhi_calc.py          # Ganzhi calculation
│   ├── dayun_calc.py           # Great Movement
│   ├── keyun_calc.py           # Host/Guest Movement
│   ├── liuqi_calc.py           # Six Qi
│   ├── kezhujialin.py          # Guest-Host interaction
│   ├── yunqi_report.py         # Comprehensive report
│   ├── calculate_yunqi_api.py  # ★ Unified calculation API
│   ├── calculate_yunqi_api.js  # ★ JS unified API
│   ├── ingest_literature.py    # ★ Literature ingestion pipeline
│   ├── self_evolve.py          # ★ Self-evolving engine
│   ├── verify_expansion.py     # End-to-end verification (67 tests)
│   └── demo_full_chain.py      # Full chain demo
│
├── rag-knowledge-base/         # ★ RAG knowledge base (5 layers)
├── self-evolve/                # ★ Self-evolving engine
├── agent-workflow/             # ★ ReAct reasoning workflow
├── prompts/                    # ★ System Prompt
├── advanced-alignment/         # ★ Advanced alignment
├── ganzhi-basics/              # Sub-skill 1
├── yunqi-calc/                 # Sub-skill 2
├── yunqi-pathogenesis/         # Sub-skill 3
├── yunqi-clinical/             # Sub-skill 4
├── yunqi-classics/             # Sub-skill 5
├── docs-generator/             # Sub-skill 6
├── docs/                       # Technical docs
└── case-journal/               # Case sedimentation
```

## Architecture

### 5-Layer RAG Knowledge Base

| Layer | Assets | Entries | Purpose |
|-------|--------|---------|---------|
| Classic pathogenesis | asset1-3 | 52 | Year fortune/Sitian/Kezhu-Jialin |
| Yunqi formulas | asset4 | 16 | Sanyin Sitian formulas |
| Historical commentaries | asset5 | 20 | 11 scholars from Wang Bing to Lu Maoxiu |
| Regional correction | asset6 | 8 | 8 climate zones across China |
| Yunqi constitution | asset7 | 18 | 9 constitution types × fortune mapping |

**104 unique keys** covering classic texts, formulas, commentaries, regions, and constitutions — matched precisely via `rag_keys`.

### Agent Integration

1. **Rule-based calculation tool** (`calculate_yunqi_api`): Dahan year-definition + date input + standardized JSON output + rag_key generation
2. **RAG knowledge base** (`rag-knowledge-base/`): 5-layer key-value structured storage
3. **ReAct reasoning workflow** (`agent-workflow/`): Tool lookup → RAG lookup → dialectical reasoning loop
4. **System Prompt** (`prompts/`): TCM Yunqi expert role constraints
5. **Advanced alignment** (`advanced-alignment/`): Weather API alignment + constitution cross-analysis
6. **Self-evolving loop** (`self_evolve/`): Auto-record after each inference → blind spot detection → feedback collection → optimization report

### Agent ReAct Reasoning Path

```
prompts/system_prompt.md → Load role constraints
  ↓
scripts/calculate_yunqi_api.py → Input date, get standardized JSON (with rag_keys)
  ↓
rag-knowledge-base/ → Retrieve all 5 layers by rag_keys
  ↓
agent-workflow/react_workflow.md → Multi-layer dialectical reasoning
  ↓
advanced-alignment/ → (Optional) Weather alignment + constitution cross-analysis
  ↓
Output structured report + disclaimer
  ↓
scripts/self_evolve.py → Auto-record this inference
```

### Verification

```bash
# End-to-end verification (67 tests: Dahan regression + asset integrity + Key association + self-evolution)
python scripts/verify_expansion.py
```

## Reuse Strategy

Preserved from reverse-skill:
- 3-axis routing matrix (dimensions: time dimension + user intent + knowledge level)
- SKILL.md standard format (frontmatter + scope + workflow + pitfalls + routing context)
- ACTION REQUIRED + task completion self-check
- case-journal experience sedimentation system

Removed from reverse-skill:
- Manifest-driven bootstrap system (Yunqi requires no external tools)
- bootstrap/ToolDiscovery/tool-index
- MCP server registration
- Cross-platform PowerShell/Bash parity (pure Python only)

## Disclaimer

Yunqi theory is traditional Chinese medical theory, not a modern medical diagnostic standard. Clinical analysis output by this skill pack is for reference only. Actual diagnosis and treatment must be performed by licensed TCM practitioners.

## License

MIT License. See [LICENSE](LICENSE).

## Acknowledgements

- Architecture reference: [reverse-skill](https://github.com/zhaoxuya520/reverse-skill) (zhaoxuya520)
- Theoretical basis: Yellow Emperor's Inner Classic · Suwen, seven major treatises
