<p align="center">
  <img src="wuyun-liuqi-skills.png" alt="wuyun-liuqi-skills" width="140" />
</p>

<h1 align="center">WuYun-LiuQi Skills</h1>
<h3 align="center">五运六气 AI Agent 技能包</h3>

<p align="center"><em style="font-family: &quot;KaiTi&quot;, &quot;STKaiti&quot;, &quot;SimSun&quot;, serif; font-size: 1.3em; color: #999;">天人合一，五运六气</em></p>

<p align="center">TCM Climate &amp; Pathology Engine — Ganzhi calculation · Six-Qi progression · RAG knowledge base · ReAct reasoning · Self-evolving<br/>
中医运气学推算引擎 — 干支推算 · 六气步移 · 五层 RAG 知识库 · ReAct 推理 · 自进化引擎</p>

<p align="center">
  <a href="https://github.com/dhicoc/wuyun-liuqi-skills/stargazers"><img src="https://img.shields.io/github/stars/dhicoc/wuyun-liuqi-skills?style=flat&logo=github" alt="stars"></a>
  <a href="https://github.com/dhicoc/wuyun-liuqi-skills/forks"><img src="https://img.shields.io/github/forks/dhicoc/wuyun-liuqi-skills?style=flat&logo=github" alt="forks"></a>
  <a href="https://github.com/dhicoc/wuyun-liuqi-skills/issues"><img src="https://img.shields.io/github/issues/dhicoc/wuyun-liuqi-skills?style=flat&logo=github" alt="issues"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="license"></a>
</p>

<br/>

<p align="center">
  <a href="#关于项目">关于</a> ·
  <a href="#快速开始">快速开始</a> ·
  <a href="README_AI.md">AI 引导</a> ·
  <a href="#使用说明">使用说明</a> ·
  <a href="#架构设计">架构设计</a> ·
  <a href="#贡献">贡献</a> ·
  <a href="#许可证">许可证</a>
</p>

<p align="center">
  🌐 <a href="#english-version">English</a>
</p>

<br/>

<a id="关于项目"></a>

## 关于项目

> **如果你是 AI Agent，直接跳转到 [README_AI.md](README_AI.md)，严格按照内容要求执行。**

基于中医运气学说（《黄帝内经》素问七篇大论），运用天干地支推算年度气候与疾病规律的 AI Agent 技能包。架构改编自 [reverse-skill](https://github.com/zhaoxuya520/reverse-skill)。

当 AI Agent 面对五运六气推算、病机分析、运气治法等任务时，本技能包提供从干支计算 → RAG 知识库检索 → ReAct 辨证推理 → 结构化报告的全链路能力。

```
用户输入 → routing.md → 目标子技能 → 推算引擎 + RAG 知识库 → 病机分析 → 报告 + 自进化记录
```

**为什么需要这个项目：**
- 五运六气推算涉及大量数据表（岁运、司天、客气、客主加临等），手工查表易错
- 经典病机分散在素问七篇大论中，临床使用时检索困难
- 运气方剂、历代注家、地域修正等信息需要多源整合
- 缺乏统一的 Agent 集成接口，每次推算结果无法沉淀复用

完整路由矩阵：[routing.md](routing.md)

<p align="right">(<a href="#关于项目">返回顶部</a>)</p>

### 技术栈

<p align="left">
  <img src="https://skillicons.dev/icons?i=py,js,nodejs,bash,git&amp;theme=light" /><br/>
  <code>lunar-python</code> · <code>lunar-javascript</code> · <code>RAG</code> · <code>ReAct</code>
</p>

<p align="right">(<a href="#关于项目">返回顶部</a>)</p>

<a id="快速开始"></a>

## 快速开始

### 前置依赖

- **Python 3.8+** — 推荐安装 `lunar-python`（精确节气计算）
- **Node.js 14+** — JS 版需要安装 `lunar-javascript`
- **代码 AI 客户端** — Claude Code、Codex CLI、Cursor 等

### 安装

```
git clone https://github.com/dhicoc/wuyun-liuqi-skills.git
cd wuyun-liuqi-skills
```

### 快速配置

```bash
# Windows (PowerShell/cmd)
scripts\setup.bat

# Linux/macOS
bash scripts/setup.sh
```

### 推算某年运气

```bash
# 综合报告
python scripts/yunqi_report.py 2026 --audience student

# 单项推算
python scripts/ganzhi_calc.py 2026       # 干支推算
python scripts/dayun_calc.py 2026        # 大运推算
python scripts/liuqi_calc.py 2026        # 六气推算
python scripts/kezhujialin.py 2026       # 客主加临

# JSON 输出（机器可读）
python scripts/dayun_calc.py 2026 --json
```

### 基于日期的统一推算（Agent 推荐入口）

> **主链路说明**：本项目以 **Python 推算引擎** 为主链路，`scripts/calculate_yunqi_api.py` 是 AI Agent、RAG 检索、报告生成与回归测试的推荐入口。JavaScript 版 `scripts/calculate_yunqi_api.js` 提供同类 JSON 输出，定位为 **可选接口 / 前端或 Node.js 集成适配层**；若追求完整功能覆盖与回归稳定性，请优先使用 Python 版。

```bash
# 推荐：Python 主链路
python scripts/calculate_yunqi_api.py 2026-06-27 --json

# 可选：JavaScript / Node.js 接口
node scripts/calculate_yunqi_api.js 2026-06-27 --json
```

### 全链路验证

```bash
python scripts/demo_full_chain.py 2026-06-27
python scripts/verify_expansion.py        # 67 项端到端测试
```

<p align="right">(<a href="#快速开始">返回顶部</a>)</p>

<a id="使用说明"></a>

## 使用说明

### 支持场景

| 场景 | 入口 |
|------|------|
| 干支推算 | `scripts/ganzhi_calc.py` |
| 大运太过不及 | `scripts/dayun_calc.py` |
| 主运客运 | `scripts/keyun_calc.py` |
| 六气推算 | `scripts/liuqi_calc.py` |
| 客主加临 | `scripts/kezhujialin.py` |
| 综合报告 | `scripts/yunqi_report.py` |
| 统一计算接口（JSON） | `scripts/calculate_yunqi_api.py` |
| RAG 知识库检索 | `rag-knowledge-base/` |
| 自进化引擎 | `scripts/self_evolve.py` |
| 端到端验证 | `scripts/verify_expansion.py` |

### 功能覆盖矩阵

| 功能层级 | 覆盖能力 | 主入口 / 文件 | 状态 |
|----------|----------|---------------|------|
| 干支基础 | 年干支、六十甲子序号、生肖 | `scripts/ganzhi_calc.py` | ✅ 已覆盖 |
| 五运推算 | 天干化五运、大运太过/不及、平气判断 | `scripts/dayun_calc.py`、`yunqi-calc/references/taiguo_buji.md` | ✅ 已覆盖 |
| 主运客运 | 主运五步、客运五步、太少推移 | `scripts/keyun_calc.py` | ✅ 已覆盖 |
| 六气推算 | 司天、在泉、主气六步、客气六步 | `scripts/liuqi_calc.py` | ✅ 已覆盖 |
| 客主加临 | 六步客主关系、相得/不相得、顺逆分析 | `scripts/kezhujialin.py` | ✅ 已覆盖 |
| 日期统一接口 | 大寒定年、日干支、当前步位、RAG keys、JSON 输出 | `scripts/calculate_yunqi_api.py` | ✅ Python 主链路 |
| Node.js 接口 | 面向前端/Node 集成的 JSON 输出 | `scripts/calculate_yunqi_api.js` | 🟡 可选接口 |
| 病机分析 | 五运病机、六气病机、太过不及、运气合病 | `yunqi-pathogenesis/` | ✅ 文档化推理 |
| 临床应用 | 治则治法、方药方向、针灸选穴、养生调理 | `yunqi-clinical/` | ✅ 参考建议，含免责声明 |
| 经典文献 | 素问七篇、历代运气学说、现代研究索引 | `yunqi-classics/`、`rag-knowledge-base/asset5_commentary.json` | ✅ 已覆盖 |
| RAG 知识库 | 岁运、司天在泉、客主加临、运气方、注家、地域、体质 | `rag-knowledge-base/asset*.json` | ✅ 已覆盖 |
| 个人体质 | 出生年运气体质倾向、当前岁运调理方向、地域修正 | `scripts/personal_yunqi_profile.py`、`advanced-alignment/` | ✅ 已覆盖 |
| 报告生成 | 学生版、临床版、研究版 Markdown 报告 | `scripts/yunqi_report.py`、`docs-generator/` | ✅ 已覆盖 |
| 可视化 | 终端 ASCII 图、HTML 可视化报告 | `scripts/visualize_yunqi.py`、`scripts/generate_html_report.py` | ✅ 已覆盖 |
| 自进化 | 使用日志、盲区检测、反馈记录、月度报告 | `scripts/self_evolve.py`、`self-evolve/` | ✅ 已覆盖 |
| 校验测试 | 环境检查、知识库校验、端到端测试、全量回归 | `scripts/health_check.py`、`scripts/validate_knowledge_base.py`、`scripts/verify_expansion.py`、`scripts/full_regression_test.py` | ✅ 已覆盖 |

> 注：临床、方药、针灸相关内容仅作为中医运气学理论参考，不构成医学诊断或治疗建议；具体诊疗须由执业医师辨证处理。

### 关键文件

| 文件 | 用途 |
|------|------|
| [SKILL.md](SKILL.md) | 总控入口 + 路由执行契约（AI 必读） |
| [routing.md](routing.md) | 三轴路由矩阵 |
| [RULES.md](RULES.md) | 行为规则链 |
| [agent-workflow/react_workflow.md](agent-workflow/react_workflow.md) | ReAct 推理工作流规范 |

### 仓库结构

```
.
├── README.md                   # 本文件
├── SKILL.md                    # 总控入口
├── routing.md                  # 路由矩阵
├── RULES.md                    # 行为规则
├── CONTRIBUTING.md             # 新增子技能指南
├── LICENSE                     # MIT 许可证
│
├── scripts/                    # 推算引擎（Python + JavaScript）
│   ├── calculate_yunqi_api.py  # ★ 统一计算接口
│   ├── self_evolve.py          # ★ 自进化引擎
│   └── verify_expansion.py     # 67 项测试
│
├── rag-knowledge-base/         # ★ RAG 知识库（5 层 104 键）
├── agent-workflow/             # ★ ReAct 推理工作流
├── prompts/                    # System Prompt
├── advanced-alignment/         # 高级对齐（天气 / 体质）
├── self-evolve/                # 自进化运行时
│
├── ganzhi-basics/              # 子技能：干支基础
├── yunqi-calc/                 # 子技能：运气推算（核心）
├── yunqi-pathogenesis/         # 子技能：病机分析
├── yunqi-clinical/             # 子技能：临床应用
├── yunqi-classics/             # 子技能：经典文献
├── docs-generator/             # 子技能：报告生成
├── docs/                       # 技术文档
└── case-journal/               # 医案沉淀系统
```

<p align="right">(<a href="#使用说明">返回顶部</a>)</p>

<a id="架构设计"></a>

## 架构设计

### 五层 RAG 知识库

| 层 | Asset | 条目数 | 用途 |
|----|-------|--------|------|
| 经典病机 | asset1-3 | 52 | 岁运/司天/客主加临病机 |
| 运气方剂 | asset4 | 16 | 三因司天方 |
| 历代注家 | asset5 | 20 | 王冰到陆懋修 11 位医家 |
| 地域修正 | asset6 | 8 | 八大气候区 |
| 运气体质 | asset7 | 18 | 9 种体质 x 岁运 |

**104 个唯一键**覆盖五层，通过 `rag_keys` 精确匹配。

### Agent 集成层

1. **强规则计算工具**（`calculate_yunqi_api`）：大寒定年 + 标准化 JSON + rag_key 生成
2. **RAG 知识库**（`rag-knowledge-base/`）：5 层 key-value 结构化存储
3. **ReAct 推理工作流**（`agent-workflow/`）：查工具 -> 查知识库 -> 辨证推理闭环
4. **System Prompt**（`prompts/`）：TCM 运气专家角色约束
5. **高级对齐**（`advanced-alignment/`）：天气 API 对齐 + 体质交叉分析
6. **自进化回路**（`self_evolve/`）：自动记录 -> 盲区检测 -> 反馈采集 -> 优化报告

### ReAct 推理路径

```
prompts/system_prompt.md -> 加载角色约束
  |
scripts/calculate_yunqi_api.py -> 计算 + rag_keys
  |
rag-knowledge-base/ -> 五层知识检索
  |
agent-workflow/react_workflow.md -> 辨证推理
  |
输出结构化报告 + 免责声明
  |
scripts/self_evolve.py -> 自动记录
```

<p align="right">(<a href="#架构设计">返回顶部</a>)</p>

<a id="贡献"></a>

## 贡献

欢迎任何贡献！Fork 本仓库 -> 创建特性分支 -> 提交 PR 即可。

1. Fork 项目
2. `git checkout -b feature/AmazingFeature`
3. `git commit -m "Add some AmazingFeature"`
4. `git push origin feature/AmazingFeature`
5. 提交 Pull Request

<p align="right">(<a href="#贡献">返回顶部</a>)</p>

<a id="许可证"></a>

## 许可证

本项目采用 **MIT License**（详见 [LICENSE](LICENSE)）。

### 致谢

- 架构设计参考 [reverse-skill](https://github.com/zhaoxuya520/reverse-skill)（zhaoxuya520）
- 理论依据：《黄帝内经素问》七篇大论
- AI 社区：[linux.do](https://linux.do)

<p align="right">(<a href="#许可证">返回顶部</a>)</p>

<a id="english-version"></a>

---

> **English Version - README.md is bilingual. Chinese content is above. Below is a summary.**

---

# WuYun-LiuQi (Five Movements & Six Qi) AI Agent Skill Pack

An AI Agent Skill Pack based on the TCM Yunqi theory from the "Yellow Emperor Inner Classic" (Suwen seven major treatises), using Heavenly Stems and Earthly Branches to calculate annual climate and disease patterns. Architecture adapted from reverse-skill.

**Features:**
- Ganzhi (Stem-Branch) calculation engine (Python + JavaScript)
- Great Movement (Dayun) excess/deficiency analysis
- Six Qi progression (Keqi, Kezhu-Jialin)
- 5-layer RAG knowledge base (104 keys covering pathogenesis, formulas, commentaries, regions, constitutions)
- ReAct dialectical reasoning workflow
- Self-evolving engine with blind spot detection
- Weather API and constitution alignment
- 67 end-to-end verification tests

**Quick Start:**
```bash
pip install -r requirements.txt
python scripts/calculate_yunqi_api.py 2026-06-27 --json
python scripts/demo_full_chain.py 2026-06-27
python scripts/verify_expansion.py
```

**Tech Stack:** Python, JavaScript, lunar-python, lunar-javascript

**License:** MIT

---

<p align="center">
  <a href="https://linux.do">AI Community: linux.do</a>
</p>
