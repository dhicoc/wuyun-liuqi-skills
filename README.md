<p align="center">
  <img src="wuyun-liuqi-skills.png" alt="wuyun-liuqi-skills" width="140" />
</p>

<h1 align="center">WuYun-LiuQi Skills</h1>
<h3 align="center">五运六气 AI Agent 技能包</h3>

<p align="center"><em style="font-family: &quot;KaiTi&quot;, &quot;STKaiti&quot;, &quot;SimSun&quot;, serif; font-size: 1.3em; color: #999;">天人合一，五运六气</em></p>

<p align="center">帮助人类通过 AI Agent 理解《黄帝内经》运气学思想的技能包<br/>
AI Agent Skill Pack that enables humans to deeply understand WuYun-LiuQi (Five Movements and Six Qi) philosophy through natural conversation</p>

<p align="center">TCM Climate &amp; Pathology Engine — Ganzhi calculation · Six-Qi progression · RAG knowledge base · Public-domain literature distillation · Commentator perspectives · ReAct reasoning · Self-evolving<br/>
中医运气学推算引擎 — 干支推算 · 六气步移 · RAG 知识库 · 公版文献蒸馏 · 注家人格 · 岁图医案 · ReAct 推理 · 自进化引擎</p>

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

**核心定位**：人类将本技能包安装到自己的 AI Agent（Claude、Cursor 等）中后，Agent 就能成为一个可靠的“五运六气思想讲解员”和推算助手，帮助人类准确、系统地理解《黄帝内经》运气学这个古老而深刻的思想体系。

基于中医运气学说（《黄帝内经》素问七篇大论），本技能包让 AI Agent 能够：
- 进行严谨的干支运气推算（而非凭记忆或幻觉）
- 检索并运用结构化的经典知识（RAG）
- 按照正确的思维路径进行辨证推理
- 输出可学习的报告、解释和个人化参考

```
人类提问（关于运气） → Agent 激活本技能 → 推算引擎 + RAG 知识库 → 病机分析 + 思想解读 → 结构化报告 + 自进化
```

**为什么需要这个项目：**
- 五运六气思想体系复杂（大量数据表、严谨规则、分散在经典中），普通人难以系统掌握
- 一般大模型容易对干支、司天在泉、客主加临等内容产生幻觉或简化错误
- 人类需要一个能“教”而不是“猜”的助手，来真正理解运气学背后的宇宙观、时间观与生命观
- 缺乏专为 Agent 设计的、可靠的运气学知识与计算技能包

本技能包正是为了解决以上问题，让人类通过与 AI 的自然对话，深入了解五运六气这个思想。

完整路由（单一真相源）：[routing.yaml](routing.yaml) · 人类索引：[routing.md](routing.md)

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

### 快速配置（人类用户）—— 支持直接丢仓库地址

**最推荐的方式（接近一句话安装）：**

直接把下面内容复制给 Claude（或其他 AI）：

```
仓库地址：https://github.com/dhicoc/wuyun-liuqi-skills.git

请按 workflows/one-line-install.md 帮我把这个五运六气技能包完整安装好：
克隆仓库、运行 `python scripts/install.py --link-global`、验证通过。
```

AI 会完成：克隆 → `install.py --link-global`（自动注册全局技能）→ 验证。之后你在任意项目里说「五运六气」即可激活。

---

传统方式：

1. 把本技能包放在你的 AI Agent 能访问的位置。
2. 让 Agent 准备好运行环境：

```bash
# Windows (PowerShell/cmd)
scripts\setup.bat

# Linux/macOS
bash scripts/setup.sh
```

配置完成后，在与 Agent 的对话中直接说“五运六气”“今天运气怎么样”“帮我分析出生年份的运气”等，Agent 会自动使用本技能来帮助你理解这个思想。

### 跨工具薄壳（自动发现）

克隆本仓库到 Agent 可访问的位置后，以下入口文件会自动引导到 `SKILL.md` 与 `routing.yaml`：

| 工具 | 入口文件 |
|------|----------|
| Codex / Copilot / OpenCode | [AGENTS.md](AGENTS.md) |
| Claude Code | [CLAUDE.md](CLAUDE.md) + 可选 [.claude/skills/wuyun-liuqi/](.claude/skills/wuyun-liuqi/) |
| Cursor | [.cursor/rules/wuyun-liuqi.mdc](.cursor/rules/wuyun-liuqi.mdc) + [.cursor/skills/wuyun-liuqi/SKILL.md](.cursor/skills/wuyun-liuqi/SKILL.md) |

**一句话安装后的两种激活方式：**

| 场景 | 做法 | 适合 |
|------|------|------|
| A. 在本仓库用 | 用 Cursor/Claude **打开** `wuyun-liuqi-skills` 文件夹 | 初学、试用 |
| B. 在任意项目用 | `python scripts/install.py --link-global`（自动链接 Claude/Cursor 全局技能目录） | 日常常驻（推荐） |

场景 B 下，用户在别的项目里说「五运六气」也会激活；薄壳与 `SKILL.md` 仍在包内，无需手抄规则。详细步骤见 [workflows/one-line-install.md](workflows/one-line-install.md)。

**Claude Code 插件市场（场景 C）：**

```text
/plugin marketplace add dhicoc/wuyun-liuqi-skills
/plugin install wuyun-liuqi-skills@wuyun-liuqi-skills
```

详见 [workflows/claude-plugin-install.md](workflows/claude-plugin-install.md)。

### 技术入口（供 Agent 直接调用或调试）

> **主链路**：`scripts/calculate_yunqi_api.py`（支持 `today` / 默认今天 + 思想层）

```bash
# Agent 常用（快速 + 思想理解）
python scripts/calculate_yunqi_api.py today --summary
python scripts/calculate_yunqi_api.py today --level deep --explain-concept "天人合一"
python scripts/calculate_yunqi_api.py 2026-06-27 --json --export summary
```

## 使用说明

### 推荐使用方式

**最自然的方式**：把本技能包安装到你的 AI Agent 中，然后直接用自然语言提问（例如：“五运六气是什么思想？”“今年运气如何影响养生？”“我的出生年份运气和体质有什么关系？”）。

Agent 会自动调用本技能包的推算引擎、知识库和推理流程来帮助你理解运气学这个思想体系。

### 技术级入口（供 Agent 或调试使用）

| 场景 | 推荐入口 |
|------|----------|
| 日期运气快速了解 | `scripts/calculate_yunqi_api.py today --summary`（支持 today / 默认今天） |
| Agent / JSON 接口 | `scripts/calculate_yunqi_api.py <日期> --json` |
| 综合报告（学生/临床/研究版） | `scripts/yunqi_report.py <年份> --audience student\|practitioner\|researcher` |
| 个人出生运气 + 体质 | `scripts/personal_yunqi_profile.py <出生日期> [地区]` |
| 天气 × 运气 × 体质对齐 | `scripts/advanced_alignment.py --date <日期> --city <城市> --mock` |

### 人类常用提问示例（直接对你的 AI 说这些）

**理解思想：**
- "五运六气是什么思想？核心的宇宙观和生命观是什么？"
- "天人合一在运气学里怎么体现？"

**生活应用：**
- "今年运气对养生有什么启发？"
- "最近天气变化，和运气有关系吗？我该注意什么？"

**个人探索：**
- "我出生那年的运气格局，对我的体质或人生阶段有什么思想意义？"
- "请分析我当前运气 + 出生运气的整体思想启发"

**学习深入 / 思想理解：**
- "用简单语言解释司天在泉，然后再给哲学层面的解读"
- "天符和中和这两个概念怎么连起来理解运气学的辩证思想？"
- "请用 --level deep 解释今年格局的思想启发，并导出卡片集帮我复习"

**导出与复习：**
- "帮我导出今年运气的思想摘要和 Anki 卡片"
- "生成可打印的 PDF 思想报告"

### 功能覆盖矩阵

| 功能层级 | 覆盖能力 | 主入口 / 文件 | 状态 |
|----------|----------|---------------|------|
| 干支基础 | 年干支、六十甲子序号、生肖 | `scripts/calculate_yunqi_api.py`（统一入口） | ✅ 已覆盖 |
| 五运推算 | 天干化五运、大运太过/不及、平气判断 | `scripts/calculate_yunqi_api.py`、`modules/yunqi-calc/references/taiguo_buji.md` | ✅ 已覆盖 |
| 主运客运 | 主运五步、客运五步、太少推移 | `scripts/calculate_yunqi_api.py` | ✅ 已覆盖 |
| 六气推算 | 司天、在泉、主气六步、客气六步 | `scripts/calculate_yunqi_api.py` | ✅ 已覆盖 |
| 客主加临 | 六步客主关系、相得/不相得、顺逆分析 | `scripts/calculate_yunqi_api.py` | ✅ 已覆盖 |
| 日期统一接口 | 大寒定年、日干支、当前步位、RAG keys、JSON 输出 | `scripts/calculate_yunqi_api.py` | ✅ Python 主链路 |
| Node.js 接口 | 面向前端/Node 集成的 JSON 输出 | `scripts/calculate_yunqi_api.js` | 🟡 可选接口 |
| 病机分析 | 五运病机、六气病机、太过不及、运气合病 | `modules/yunqi-pathogenesis/` | ✅ 文档化推理 |
| 临床应用 | 治则治法、方药方向、针灸选穴、养生调理 | `modules/yunqi-clinical/` | ✅ 参考建议，含免责声明 |
| 经典文献 | 素问七篇、历代运气学说、现代研究索引 | `modules/yunqi-classics/`、`rag-knowledge-base/asset5_commentary.json` | ✅ 已覆盖 |
| RAG 知识库 | 岁运、司天在泉、客主加临、运气方、注家、地域、体质 | `rag-knowledge-base/asset*.json` | ✅ 已覆盖 |
| 公版文献库 | 35 篇公版五运六气文献原文（61.6 万字，先秦至清） | `rag-knowledge-base/literature/` | ✅ 已覆盖 |
| 公版蒸馏指南 | 10 本公版古籍蒸馏成可 Grep+Read 的结构化指南（五层注释链 + 35 篇分组合并） | `rag-knowledge-base/*_guide.md` | ✅ 已覆盖 |
| 注家人格 | 刘完素/张介宾可运行 perspective skill（深度注家扮演，nuwa 模式） | `perspectives/` | ✅ 已覆盖 |
| 岁图医案库 | 圣济总录六十甲子岁图蒸馏的 60 条运气医案，按 rag_key 可检索同格局逐年病机治法 | `rag-knowledge-base/asset9_cases.json`、`case-journal/cases/distilled_cases.md` | ✅ 已覆盖 |
| 历代名家医案库 | 6 部公版经典医案蒸馏（名医类案/续名医类案/古今医案按/丁甘仁/伤寒九十论/临证指南），共 901 条真实医案 | `rag-knowledge-base/asset11-16_*_cases.json` | ✅ 已覆盖 |
| 个人体质 | 出生年运气体质倾向、九种体质量表、当前岁运调理方向、地域修正 | `scripts/personal_yunqi_profile.py`、`scripts/constitution_assessment.py`、`advanced-alignment/` | ✅ 已覆盖 |
| 天气对齐 | 实时气象 × 运气格局交叉分析，判断内外邪相合/相背/兼夹 | `scripts/weather_alignment.py`、`advanced-alignment/weather_integration.md` | ✅ 已接入 |
| 天气 × 体质叠加 | 出生运气体质 × 当前岁运 × 天气实况三维分析 | `scripts/yunqi_weather_constitution.py` | ✅ 已接入 |
| 统一高级对齐 | 基础运气、出生运气体质、九种体质量表、天气对齐的统一入口 | `scripts/advanced_alignment.py` | ✅ 已接入 |
| 报告生成 | 学生版、临床版、研究版 Markdown 报告；支持注入高级对齐章节 | `scripts/yunqi_report.py --advanced-json`、`scripts/generate_html_report.py --with-advanced-alignment`、`modules/docs-generator/` | ✅ 已覆盖 |
| 可视化 | 终端 ASCII 图、HTML 可视化报告 | `scripts/visualize_yunqi.py`、`scripts/generate_html_report.py` | ✅ 已覆盖 |
| 自进化 | 使用日志 + 概念/哲学追踪 + 理解反馈 + 隐私哈希/清洗 + 月报 + 清理 + 自动建议 | `scripts/self_evolve.py`、`self-evolve/` | ✅ 已覆盖（含思想理解维度） |
| 校验测试 | 环境检查、知识库校验、端到端测试、全量回归（63/0） | `scripts/health_check.py`、`scripts/validate_knowledge_base.py`、`tests/verify_expansion.py`、`tests/full_regression_test.py` | ✅ 已覆盖 |
| 思想导出 | 纯文本思想摘要、Anki 卡片集、高质量 HTML/打印 PDF | `scripts/export_thought.py` / `calculate_yunqi_api.py --export` | ✅ 新增 |

> 注：临床、方药、针灸相关内容仅作为中医运气学理论参考，不构成医学诊断或治疗建议；具体诊疗须由执业医师辨证处理。

### 关键文件

| 文件 | 用途 |
|------|------|
| [SKILL.md](SKILL.md) | 总控路由入口（AI 必读） |
| [routing.yaml](routing.yaml) | 路由单一真相源 |
| [routing.md](routing.md) | 路由人类可读索引 |
| [AGENTS.md](AGENTS.md) / [CLAUDE.md](CLAUDE.md) | 跨工具薄壳 |
| [workflows/routing-contract.md](workflows/routing-contract.md) | 路由执行契约 |
| [RULES.md](RULES.md) | 行为规则索引 → `rules/` |
| [references/gotchas.md](references/gotchas.md) | 常见踩坑 |
| [references/module-index.md](references/module-index.md) | 模块地图（含五层注释链架构） |
| [workflows/task-closure.md](workflows/task-closure.md) | 任务闭环 |
| [agent-workflow/react_workflow.md](agent-workflow/react_workflow.md) | ReAct 推理工作流规范 |
| `rag-knowledge-base/*_guide.md` | 公版蒸馏指南（五层注释链 5 本 + 35 篇分组合并 5 册，Grep+Read 零依赖） |
| `rag-knowledge-base/literature/` | 35 篇公版文献原文（61.6 万字，零依赖基础层） |
| `rag-knowledge-base/asset9_cases.json` | 圣济总录 60 岁图医案（按 rag_key 可检索同格局医案） |
| `rag-knowledge-base/asset11-16_*_cases.json` | 6 部历代名家医案库（名医类案/续名医类案/古今医案按/丁甘仁/伤寒九十论/临证指南，共 901 条临证真实医案） |
| `rag-knowledge-base/asset17_wenyi_yunqi.json` | 松峰说疫·运气瘟疫防治库（五运瘟疫侧重、六气司天民病、五郁治法、刚柔失守疫病专方，34 条） |
| `rag-knowledge-base/asset18_huichunlu_cases.json` | 回春录·王孟英湿热温病医案库（外感温病/内科杂病/妇科/儿科，40 条） |
| `rag-knowledge-base/asset19_zhangyuqing_cases.json` | 张聿青医案库（湿温伏暑/痰饮肝风/虚损血证/内科杂病，138 条） |
| `rag-knowledge-base/asset20_wujutong_cases.json` | 吴鞠通医案库（温病三焦辨证/风温暑温伏暑/痹证痰饮，120 条） |
| `rag-knowledge-base/asset21_yuyicao_cases.json` | 寓意草医案库（议病式医案/伤寒危证/真阳上脱/误治救逆，17 条） |
| `rag-knowledge-base/asset22_huixi_cases.json` | 洄溪医案库（经方辨证/中风伤寒/温疫/痰喘/血痢/产后/外科痈疽，23 条） |
| `rag-knowledge-base/asset23_huayunlou_cases.json` | 花韵楼医案库（妇科专案/崩漏/月经/产后/胎产/乳癖，20 条） |
| `rag-knowledge-base/asset24_zhenyu_juji_cases.json` | 诊余举隅录医案库（辨证精审/霍乱/痢疾/泄泻/感冒/中风/经闭，14 条） |
| `rag-knowledge-base/asset25_xushi_cases.json` | 许氏医案库（断证如折狱/伤寒/痢疾/中风/胎产/误治救逆，15 条） |
| `rag-knowledge-base/asset26_xingxuan_cases.json` | 杏轩医案库（新安医派/产后感邪/格阳证/大头时疫/蓄瘀脱血，14 条） |
| `rag-knowledge-base/asset27_sunwenyuan_cases.json` | 孙文垣医案库（温补命门/大头疫/目疾虚实/产后发热/痰火胁痛，12 条） |
| `rag-knowledge-base/asset28_conggui_cases.json` | 丛桂草堂医案库（痰饮闭塞/喉痧阴亏/孕产寒痛/疮疡阴亏，8 条） |
| `rag-knowledge-base/asset29_waike_zhengzong.json` | 外科正宗·外用医案库（痈疽/疔疮/瘰疬/脱疽/咽喉/肺痈/腿痈/囊痈/臋痈/肛痈/痔漏/下疳/瘤/多骨疮/结毒/脚气/乳痈，70 条） |
| `rag-knowledge-base/asset30_lizhai_waike.json` | 立斋外科发挥·内外联动医案库（痈疽以气血为本，内因→外候联动，8 条） |
| `rag-knowledge-base/asset31_zuihuachuang_cases.json` | 醉花窗医案库（脉证互参/虚实鉴别/误治救逆，64 条） |
| `rag-knowledge-base/asset32_yiyan_suibi.json` | 医验随笔医案库（温病/痰喘/便秘/温毒发痘/疙瘩瘟，内外兼治，12 条） |
| [`perspectives/`](perspectives/README.md) | 注家人格 perspective skill（刘完素/张介宾，深度扮演） |

### 仓库结构

```
.
├── 入口与配置 ──────────────────────────────────────────────
├── SKILL.md                    # ★ 总控路由入口（AI 必读）
├── routing.yaml / routing.md   # ★ 路由真相源 / 人类索引
├── CLAUDE.md / AGENTS.md       # 跨工具薄壳（Claude / Codex / Copilot）
├── README.md / README_AI.md    # 开发者 / AI 引导
├── RULES.md                    # 行为规则索引 → rules/
├── CONTRIBUTING.md / LICENSE   # 贡献指南 / MIT
├── conformance.yaml            # 一致性配置
├── pyproject.toml / requirements.txt / package.json  # 依赖
│
├── 推算引擎 ────────────────────────────────────────────────
├── scripts/                    # 46 个 Python 脚本 + JS 可选接口
│   ├── calculate_yunqi_api.py  #   ★ 主链路（大寒定年 + rag_keys）
│   ├── rag_search.py           #   ★ RAG 键值检索
│   ├── yunqi_report.py         #   ★ 报告生成
│   ├── personal_yunqi_profile.py #   个人体质
│   ├── self_evolve.py          #   自进化引擎
│   └── …                       #   校验/同步/学习/导出等
├── wuyun_liuqi/                # 可导入 Python 包
│
├── 知识库（零依赖 Grep+Read）──────────────────────────────
├── rag-knowledge-base/         # ★ RAG asset + 蒸馏指南 + 文献原文
│   ├── asset1-32 *.json        #   32 个键值 asset（病机/方/注家/体质/医案/治法/瘟疫，含 21 部历代名家医案库）
│   ├── terminology.json        #   700 条术语
│   ├── *_guide.md              #   10 本公版蒸馏指南（五层注释链 + 35篇合并）
│   ├── literature/             #   35 篇公版文献原文（61.6 万字）
│   └── schemas/                #   asset JSON schema
├── teaching-modules/           # 10 个概念五段式教学模块
├── perspectives/               # 注家人格（刘完素/张介宾 perspective skill）
│
├── 子技能（routing.yaml 路由目标）─────────────────────────
├── modules/ganzhi-basics/              # 干支基础
├── modules/yunqi-calc/                 # 运气推算（核心）
├── modules/yunqi-pathogenesis/         # 病机分析
├── modules/yunqi-clinical/             # 临床应用
├── modules/yunqi-classics/             # 经典文献
├── modules/docs-generator/             # 报告生成
├── advanced-alignment/         # 天气/体质高级对齐
│
├── 规则与工作流 ────────────────────────────────────────────
├── rules/                      # medical-safety / calculation / agent-behavior / output
├── workflows/                  # bootstrap / routing-contract / task-closure
├── prompts/                    # system_prompt + expression_style（讲解人格）
├── agent-workflow/             # ReAct 推理工作流
├── self-evolve/                # 自进化运行时
│
├── 医案与报告 ──────────────────────────────────────────────
├── case-journal/               # 医案沉淀（模板 + 圣济岁图医案索引）
├── reports/                    # 报告样例 / 快照 / 测试输出
│
├── 测试与校验 ──────────────────────────────────────────────
├── tests/                      # 全量回归 / 端到端 / 大寒边界 / pip 冒烟
│
├── 工具集成 ────────────────────────────────────────────────
├── .claude-plugin/             # Claude Code 插件清单
├── .cursor/                    # Cursor 技能注册 + 规则
├── .github/workflows/          # CI
├── references/                 # script-index / module-index / gotchas
└── references/                 # 模块地图 / 架构 / 路线图 / SAG 评估
```

<p align="right">(<a href="#使用说明">返回顶部</a>)</p>

<a id="架构设计"></a>

## 架构设计

### RAG 知识库资产

| 层 | Asset | 条目数 | 用途 |
|----|-------|--------|------|
| 经典病机 | asset1-3 | 52 | 岁运/司天/客主加临病机 |
| 运气方剂 | asset4 | 16 | 三因司天方（含六步时令加减） |
| 历代注家 | asset5 | 30 | 王冰到高世栻 20 位医家 |
| 地域修正 | asset6 | 8 | 八大气候区 |
| 运气体质 | asset7 | 108 | 9 种体质 × 10 岁运完整覆盖 |
| **岁图医案** | **asset9** | **60** | **圣济总录六十甲子岁图医案，按 rag_key 可检索同格局逐年病机治法** |
| **岁宜治法** | **asset10** | **6** | **六气司天岁宜治法表（保命集气宜论）** |
| **名医类案** | **asset11** | **102** | **明·江瓘，历代医案汇编，按病证/rag_key 检索** |
| **续名医类案** | **asset12** | **84** | **清·魏之琇，续补名医类案，按病证检索** |
| **古今医案按** | **asset13** | **159** | **清·俞震，医案按语，含"震按"辨证要点** |
| **丁甘仁医案** | **asset14** | **177** | **近代丁甘仁，临证实录，孟河医派** |
| **伤寒九十论** | **asset15** | **49** | **宋·许叔微，伤寒经方医案** |
| **临证指南医案** | **asset16** | **330** | **清·叶桂（叶天士），辨病机精审，含华岫云按语** |
| **运气瘟疫防治** | **asset17** | **34** | **清·刘奎《松峰说疫》卷六：五运瘟疫侧重、六气司天民病、五郁治法、刚柔失守疫病专方** |
| **回春录医案** | **asset18** | **40** | **清·王孟英《回春录》（王氏医案）：湿热温病、内科杂病、妇科、儿科医案** |
| **张聿青医案** | **asset19** | **138** | **清·张乃修《张聿青医案》：湿温伏暑、痰饮肝风、虚损血证、内科杂病医案** |
| **吴鞠通医案** | **asset20** | **120** | **清·吴瑭《吴鞠通医案》：温病三焦辨证、风温暑温伏暑、痹证痰饮医案** |
| **寓意草医案** | **asset21** | **17** | **清·喻嘉言《寓意草》：议病式医案、伤寒危证、真阳上脱、误治救逆、痢疾疫情、肺痈痰病** |
| **洄溪医案** | **asset22** | **23** | **清·徐灵胎《洄溪医案》（王孟英编）：经方辨证、中风伤寒、温疫、痰喘、血痢、产后、外科痈疽** |
| **花韵楼医案** | **asset23** | **20** | **清·顾德华（女医）《花韵楼医案》：妇科专案，崩漏、月经不调、产后、胎产、乳癖** |
| **诊余举隅录** | **asset24** | **14** | **清·陈廷儒《诊余举隅录》：辨证精审，霍乱痢疾泄泻、感冒春温、中风、妇科经闭** |
| **许氏医案** | **asset25** | **15** | **清·许恩普《许氏医案》：断证如折狱，伤寒痢疾中风、胎产妇科、误治救逆** |
| **杏轩医案** | **asset26** | **184** | **清·程文囿（新安医派）《杏轩医案》：产后感邪、格阳证、大头时疫、半产血晕、蓄瘀脱血** |
| **孙文垣医案** | **asset27** | **258** | **明·孙一奎《孙文垣医案》：温补命门、大头疫、目疾虚实、产后发热、痰火胁痛、心痹** |
| **丛桂草堂医案** | **asset28** | **8** | **清·袁焯《丛桂草堂医案》：痰饮闭塞、喉痧阴亏、孕产寒痛、疮疡阴亏** |
| **外科正宗·外用医案** | **asset29** | **70** | **明·陈实功《外科正宗》：痈疽疔疮瘰疬脱疽，艾灸/火针/蟾酥饼/琥珀膏外治** |
| **立斋外科发挥·内外联动** | **asset30** | **108** | **明·薛己《立斋外科发挥》：痈疽以气血为本最忌攻伐，内因→外候联动** |
| **醉花窗医案** | **asset31** | **64** | **清·王堉《醉花窗医案》：脉证互参、阴虚实热脾虚肝郁鉴别、误治救逆** |
| **医验随笔** | **asset32** | **12** | **近代·沈奉江《医验随笔》：温病痰喘便秘、温毒发痘、疙瘩瘟，内外兼治** |

配合 **700 条术语库**（terminology.json），通过 `rag_keys` 精确匹配。asset9/asset10 按推算引擎输出的 rag_keys 索引，可召回同格局医案与岁宜治法；asset11-16 六部历代名家医案库（共 901 条）可按病证分类检索临证真实医案。

### 五层注释链（公版蒸馏指南）

RAG asset 是精炼键值（回答"是什么"）；下列五本公版古籍蒸馏成的 Markdown 指南是**可 Grep+Read 的原文与注解**（回答"为什么、怎么治、古人怎么看"），零脚本零模型依赖，Agent 直接阅读。五层从方药到本体论，覆盖同一临床问题的不同深度。

| 层 | 指南 | 来源 | 朝代·注家 | 回答什么 |
|----|------|------|----------|----------|
| 方药层 | `rag-knowledge-base/sanyin_sitianfang_guide.md` | 《三因极一病证方论》陈无择 | 宋 | 用什么方、六步怎么加减 |
| 教材层 | `rag-knowledge-base/yunqi_yaojue_pathogenesis_guide.md` | 《运气要诀》吴谦 | 清 | 病机歌诀、标准表述 |
| 病机层 | `rag-knowledge-base/suwen_xuanji_pathogenesis_guide.md` | 《素问玄机原病式》刘完素 | 金 | 逐症状辨病机、兼化是虚象 |
| 本体论层 | `rag-knowledge-base/leijing_tuyi_yunqi_philosophy_guide.md` | 《类经图翼》张介宾 | 明 | 太极阴阳五行本体、生克互藏 |
| 治法层 | `rag-knowledge-base/baoming_zhifa_guide.md` | 《素问病机气宜保命集》刘完素 | 金 | 病机十九条治则、六气岁宜治法 |

**用法**：Agent 推算出 `rag_key` 后，`rag_search --key` 取 asset 精炼结论；需引用原文、解释病机、给治法或做注家对照时，Grep 对应指南关键词定位后 Read。asset 与指南互补——asset 给结论，指南给依据。

**注家对照**：刘完素（寒凉派，"不可峻用辛温大热"）与张介宾（温补派，"阳气为本"）形成运气学史上最尖锐的立场的对立，两方原文均可 Grep，供 `prompts/expression_style.md` 注家对照模式调用。

**蒸馏原则**：仓库只放蒸馏产物，不放蒸馏工具（仿 nihaixia 模式）。五本指南均来自公版古籍，人读原文 + 结构化录入，逐字保留、不增删、不编造，每条可溯源至源文件行号。

### 35 篇文献库 + 蒸馏指南

除了上述五层注释链的五本，项目还接入了一套更大的公版文献库及其蒸馏产物：

**文献原文（基础层，零依赖 Grep+Read）**：`rag-knowledge-base/literature/` 收录 35 篇公版五运六气文献（约 61.6 万字，先秦至清代），含《素问》七篇大论全文、遗篇（刺法论/本病论）、《圣济总录》六十甲子岁图、《玄珠密语》、《运气易览》、《运气证治歌诀》等。详见 `rag-knowledge-base/literature/检索说明.md`。

**35 篇蒸馏指南（结构化速查，零依赖）**：从 35 篇原文蒸馏出的 5 个合并指南，Agent 可 Grep 关键词定位要点，不必通读长文：

| 指南 | 覆盖文献 | 用途 |
|------|---------|------|
| `rag-knowledge-base/suwen_qipian_yipian_guide.md` | 素问七篇大论 + 遗篇 9 篇 | 经文源头：天干配五运/标本中气/亢则害承乃制/病机十九条/六气治法/运气疫病刺法 |
| `rag-knowledge-base/shengji_xuanzhu_suichatu_guide.md` | 圣济总录岁图 + 玄珠密语 2 篇 | 逐年推演速查（按司天在泉六组示例）+ 王冰运气推演十七卷 |
| `rag-knowledge-base/mingqing_yunqi_zhuanzhu_guide.md` | 运气易览/松峰说疫/运气证治歌诀等 8 篇 | 明清运气推演与证治（含王旭高反刻板按语、李时珍五运六淫用药式） |
| `rag-knowledge-base/jinyuan_yijia_yunqi_guide.md` | 玄机原病式节录/医学启源/脾胃论/格致余论 4 篇 | 金元四家运气观（河间寒凉/易水/补土/养阴） |
| `rag-knowledge-base/xianqin_cunmu_yuanliu_guide.md` | 太始天元册/管子/月令等 10 篇 | 运学渊源（先秦思想源头）+ 已佚书目 + 晚清温病运气 |

**全部零依赖开箱即用**：文献库与蒸馏指南均通过 Grep+Read 检索，不依赖任何外部模型或向量数据库。

### 注家人格 Perspective Skills

五层注释链里的刘完素与张介宾，进一步做成**可运行的 perspective skill**（人物思维操作系统，采用 [女娲 · Skill造人术](https://github.com/alchaincyf/nuwa-skill) 模式）。Agent 激活后能**切换到注家视角**回答问题，而非"替注家说话"。

| Perspective | 注家 | 派别 | 核心立场 | 保真度 |
|-------------|------|------|----------|--------|
| `perspectives/liu-wansu-perspective/` | 刘完素（金） | 寒凉派 | 六气皆从火化、不可峻用辛温、兼化虚象不可误治 | 87/100 A |
| `perspectives/zhang-jiebin-perspective/` | 张介宾（明） | 温补派 | 阳气为本、五行互藏、生中有克克中有用、造化不可无制 | 88/100 A |

每个 perspective 含 `SKILL.md`（角色扮演规则 + 心智模型 + 决策启发式 + 表达 DNA + 诚实边界）+ `FIDELITY.md`（保真度评分卡）。素材为已蒸馏的公版指南，非从零调研。

**与 `expression_style.md` 的关系**：注家对照模式升级为两层——
- **轻量对照**（默认）：运气导师口吻概述"刘完素认为……张介宾却认为……我倾向……"
- **深度扮演**（用户要求"切换到河间/景岳"）：加载对应 perspective，让注家以第一人称"自己说话"——刘完素以"……者……也"断之，张介宾以"盖……故……"推之

### Agent 集成层

1. **强规则计算工具**（`calculate_yunqi_api`）：大寒定年 + 标准化 JSON + rag_key 生成
2. **RAG 知识库**（`rag-knowledge-base/`）：32 个键值 asset（含 asset9 岁图医案 + asset11-16 六部历代名家医案库 901 条 + asset17 运气瘟疫防治 + asset18 回春录医案 + asset19 张聿青医案 + asset20 吴鞠通医案 + asset21 寓意草医案 + asset22 洄溪医案 + asset23 花韵楼医案 + asset24 诊余举隅录 + asset25 许氏医案 + asset26 杏轩医案 + asset27 孙文垣医案 + asset28 丛桂草堂医案 + asset29 外科正宗外用医案 + asset30 立斋外科发挥 + asset31 醉花窗医案 + asset32 医验随笔）+ 10 本公版蒸馏指南（Grep+Read）+ 35 篇文献原文
3. **ReAct 推理工作流**（`agent-workflow/`）：查工具 -> 查知识库 -> 辨证推理闭环
4. **System Prompt**（`prompts/`）：TCM 运气专家角色约束（临床模式 + 讲解模式双语态）
5. **注家人格**（`perspectives/`）：刘完素/张介宾可运行 perspective skill（深度注家扮演）
6. **高级对齐**（`advanced-alignment/`）：天气 API 对齐 + 体质交叉分析
7. **自进化回路**（`self_evolve/`）：自动记录 -> 盲区检测 -> 反馈采集 -> 优化报告

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

> **English Version** — This README is bilingual. The Chinese documentation above is the canonical guide for AI Agents; the English section below provides a structured overview for international users and contributors.

---

# WuYun-LiuQi AI Agent Skill Pack

**WuYun-LiuQi** (Five Movements and Six Qi, 运气学) is an AI Agent skill pack designed to help humans deeply understand the ancient Yunqi thought system (天人合一 / Heaven-Human Oneness, 气化 / Qi transformation, 中和 / moderation, time rhythms, and life view) through accurate calculation, philosophical interpretation, and exportable study materials.

It is based on the Yunqi theory in the seven major Suwen treatises of the *Huangdi Neijing*. The pack provides rule-based Ganzhi/Yunqi calculation (Dahan boundary), a 32-asset RAG knowledge base (incl. 21 classical case libraries), thought-layer explanations, progressive learning depth, self-evolution with privacy, and tools to export thought summaries, Anki cards, and printable reports.

The project provides an end-to-end workflow focused on helping humans deeply understand the Yunqi thought system (天人合一, 气化, 中和, time rhythms, life view):

```text
User input (natural language) → routing + onboarding (fuzzy intent handling) → Python engine (Dahan boundary) → 32-asset RAG (incl. 21 classical case libraries) → pathogenesis + **thought-layer interpretation** → reports with guiding/reflection questions → visualization → self-evolution (concept tracking + understanding feedback + privacy) → export (plain-text thought summary / Anki cards / PDF/HTML)
```

Core value: Reliable calculation + philosophical interpretation + exportable study materials so humans can truly internalize the ideas rather than just receive numbers.

> Medical note: this project is for traditional TCM theory learning, research, and assisted reasoning only. It is **not** a medical diagnosis or treatment system. Clinical decisions must be made by qualified healthcare professionals.

## Primary Runtime

The **Python engine is the primary and recommended runtime**:

- `scripts/calculate_yunqi_api.py` is the main entry point (supports `today`, `--summary`, `--level`, `--explain-concept`, `--export`, thought-layer output).
- `scripts/export_thought.py` for dedicated thought-summary / Anki cards / PDF exports.
- `scripts/self_evolve.py` for usage tracking, concept-level understanding feedback, privacy-protected logs, and improvement reports.
- `scripts/calculate_yunqi_api.js` is an optional JavaScript / Node.js integration layer.
- Prefer Python for full features, stability, and the most complete regression coverage.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
npm install   # optional, only required for the Node.js interface

# Recommended: Python primary workflow (today support + thought focus)
python scripts/calculate_yunqi_api.py today --summary
python scripts/calculate_yunqi_api.py today --level deep --explain-concept "天人合一"
python scripts/calculate_yunqi_api.py 2026-06-27 --json --export all

# Export thought materials (summary / Anki cards / printable PDF)
python scripts/export_thought.py today --format all

# Self-evolution (concepts + understanding feedback + privacy)
python scripts/self_evolve.py stats --top-concepts 5
python scripts/self_evolve.py report

# Optional: Node.js interface
node scripts/calculate_yunqi_api.js 2026-06-27 --json

# Full-chain demo and verification
python scripts/demo_full_chain.py 2026-06-27
python tests/verify_expansion.py
python tests/full_regression_test.py   # 63 tests, 0 failures
```

## Feature Coverage Matrix

| Layer | Capability | Main Entry | Status |
|-------|------------|------------|--------|
| Ganzhi basics | Year Stem-Branch, sexagenary index, zodiac | `scripts/calculate_yunqi_api.py` (unified) | ✅ Covered |
| Five Movements | Dayun, excess/deficiency, Pingqi conditions | `scripts/calculate_yunqi_api.py` | ✅ Covered |
| Movement steps | Host movement and guest movement progression | `scripts/calculate_yunqi_api.py` | ✅ Covered |
| Six Qi | Sitian, Zaiquan, host Qi, guest Qi | `scripts/calculate_yunqi_api.py` | ✅ Covered |
| Kezhu-Jialin | Guest-host Qi relationship and favorable/unfavorable analysis | `scripts/calculate_yunqi_api.py` | ✅ Covered |
| Unified date API | Dahan year boundary, current Qi step, RAG keys, JSON output | `scripts/calculate_yunqi_api.py` | ✅ Primary Python path |
| Node.js API | JSON output for frontend / Node.js integrations | `scripts/calculate_yunqi_api.js` | 🟡 Optional |
| Pathogenesis | Five-movement, Six-Qi, excess/deficiency, combined Yunqi reasoning | `modules/yunqi-pathogenesis/` | ✅ Documented reasoning |
| Clinical reference | Treatment principles, formula direction, acupuncture references, lifestyle guidance | `modules/yunqi-clinical/` | ✅ Reference only |
| Classics | Suwen treatises, historical schools, modern research notes | `modules/yunqi-classics/` | ✅ Covered |
| RAG knowledge base | 16 structured assets (pathogenesis, formulas, commentaries, regional, constitution + 6 classical case libraries) | `rag-knowledge-base/asset*.json` | ✅ Covered |
| Personal profile | Birth-year Yunqi tendency, constitution score assessment, current-year adjustment, regional modifier | `scripts/personal_yunqi_profile.py`, `scripts/constitution_assessment.py` | ✅ Covered |
| Weather alignment | Real weather × Yunqi pattern alignment for same-direction, opposite, or mixed climate signals | `scripts/weather_alignment.py` | ✅ Covered |
| Weather × constitution | Birth Yunqi constitution × current-year Yunqi × weather reality combined analysis | `scripts/yunqi_weather_constitution.py` | ✅ Covered |
| Unified advanced alignment | Unified entry for base Yunqi, birth profile, constitution assessment, and weather alignment | `scripts/advanced_alignment.py` | ✅ Covered |
| Reports | Student, practitioner, and researcher report styles with optional advanced-alignment sections | `scripts/yunqi_report.py --advanced-json`, `scripts/generate_html_report.py --with-advanced-alignment` | ✅ Covered |
| Visualization | ASCII chart and HTML visual report | `scripts/visualize_yunqi.py`, `scripts/generate_html_report.py` | ✅ Covered |
| Self-evolution | Usage logs + philosophical concept tracking + understanding feedback + privacy (session hashing + PII sanitizing) + monthly reports + cleanup + auto suggestions | `scripts/self_evolve.py` | ✅ Covered (strong thought-understanding focus) |
| Thought export | Plain-text thought summaries, Anki card sets, high-quality HTML / browser-print PDF | `scripts/export_thought.py`, `calculate_yunqi_api.py --export` | ✅ New |
| Validation | Environment check, RAG validation, end-to-end tests, full regression (63/0) | `scripts/health_check.py`, `scripts/validate_knowledge_base.py`, `tests/verify_expansion.py`, `tests/full_regression_test.py` | ✅ Covered |

## Core Features

- Rule-based Yunqi calculation with Dahan (大寒) as the Yunqi year boundary (accurate, hallucination-free)
- Standardized JSON + rich text output for LLM / Agent integration
- **Thought-layer interpretation** in reports: philosophical explanations (天人合一, 气化, 中和), modern analogies, year-specific insights
- Progressive depth: `--level simple|standard|deep` and `--explain-concept`
- 32-asset RAG knowledge base (pathogenesis, formulas, commentaries, regional, constitution + 21 classical case libraries, 901+ cases)
- Weather & constitution advanced alignment (three-dimensional analysis)
- ReAct-style reasoning workflow
- Markdown / styled HTML report generation (student / practitioner / researcher)
- ASCII + visual reports
- **Export for study**: plain-text thought summaries, Anki flashcards (TSV + Markdown), high-quality printable HTML/PDF
- **Self-evolution engine**: automatic logging of usage + concepts, understanding-quality feedback, privacy (SHA256 session IDs + PII sanitization), cleanup, stats, and improvement suggestions
- Guiding questions and "next step" prompts to support reflection and deeper understanding
- Full regression (63/0) + knowledge validation scripts
- Strong human UX: `today` default, `--help`, colors, health-check guidance, fuzzy-input onboarding

## Repository Map

```text
scripts/                 Calculation engines, primary Python API (with --level/--explain-concept/--export), export_thought.py, weather alignment, reports, visualization
rag-knowledge-base/      Structured RAG assets (7 layers), README, and index.json
agent-workflow/          ReAct workflow specification + onboarding for vague inputs
prompts/                 Agent system prompts (thought-partner tone)
reports/examples/        Versioned sample reports and preview images
reports/generated/       Local generated reports (ignored by Git)
reports/test-results/    Test outputs (ignored by Git)
references/                    Module map, architecture, roadmap, evaluations (self-evolve, thought understanding, UX)
tests/                   Test fixtures; full_regression_test.py (63/0)
.github/workflows/       CI workflow
modules/ganzhi-basics/           Stem-Branch learning skill
modules/yunqi-calc/              Core Yunqi calculation skill
modules/yunqi-pathogenesis/      Pathogenesis reasoning skill
modules/yunqi-clinical/          Clinical reference and lifestyle guidance skill
modules/yunqi-classics/          Classical literature and research references
modules/docs-generator/          Report templates
advanced-alignment/      Weather and constitution alignment
self-evolve/             Logs + concept tracking + understanding feedback + privacy + reports + cleanup
case-journal/            Case record templates, disclaimers, and example cases
```

## Verification

```bash
python scripts/health_check.py
python scripts/validate_knowledge_base.py
python tests/verify_expansion.py
python tests/full_regression_test.py   # currently 63 tests, 0 failures
```

## Tech Stack

Python · JavaScript · Node.js · `lunar-python` · `lunar-javascript` · RAG · ReAct-style agent workflow

## License

MIT License. See [LICENSE](LICENSE).

---

<p align="center">
  <a href="https://linux.do">AI Community: linux.do</a>
</p>
