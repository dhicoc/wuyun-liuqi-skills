<p align="center">
  <img src="wuyun-liuqi-skills.png" alt="wuyun-liuqi-skills" width="140" />
</p>

<h1 align="center">wuyun-liuqi-skills</h1>
<h3 align="center">TCM Yunqi Skills Router · 五运六气技能路由包</h3>

<p align="center"><em style="font-family: KaiTi, STKaiti, SimSun, serif; font-size: 1.2em; color: #777;">天人合一，五运六气</em></p>

<p align="center">
  <a href="https://github.com/dhicoc/wuyun-liuqi-skills/stargazers"><img src="https://img.shields.io/github/stars/dhicoc/wuyun-liuqi-skills?style=flat&logo=github" alt="stars"></a>
  <a href="https://github.com/dhicoc/wuyun-liuqi-skills/forks"><img src="https://img.shields.io/github/forks/dhicoc/wuyun-liuqi-skills?style=flat&logo=github" alt="forks"></a>
  <a href="https://github.com/dhicoc/wuyun-liuqi-skills/issues"><img src="https://img.shields.io/github/issues/dhicoc/wuyun-liuqi-skills?style=flat&logo=github" alt="issues"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="license"></a>
</p>

<p align="center">
  AI 自动路由 + 确定性推算引擎 + RAG 知识库 + 自进化经验库<br/>
  支持 Claude Code / Cursor / Codex CLI / Cline / OpenClaw 等 AI 客户端
</p>

<br/>

<p align="center">
  <a href="#这是什么">这是什么</a> ·
  <a href="#适合谁用">适合谁用</a> ·
  <a href="#快速上手">快速上手</a> ·
  <a href="#核心能力">核心能力</a> ·
  <a href="#项目结构">项目结构</a> ·
  <a href="#贡献">贡献</a>
</p>

<p align="center">
  🌐 <a href="README_EN.md">English</a>
</p>

<br/>

---

<a id="这是什么"></a>

## 这是什么

> **如果你是 AI Agent，直接跳转到 [README_AI.md](README_AI.md)，严格按照内容要求执行。**

当用户对 AI Agent（Claude、Cursor、Codex 等）说「今年运气怎么样」「我出生那年的体质倾向」「历代医家怎么治头痛」时，这个技能包让 Agent 调用确定性推算引擎算出干支运气格局，从 1994 条真实医案中检索相关病机与治法，再用通俗语言讲给用户听——而不是凭记忆胡编。

```
用户提问（自然语言）
  -> routing.yaml 路由匹配
  -> calculate_yunqi_api.py 推算引擎（大寒定年，非幻觉）
  -> rag_search 检索 32 个 RAG asset（1994 条医案 + 33 条疾病易感性）
  -> infer_pathogenesis 病机推理链
  -> 通俗语言解释 + 免责声明
  -> self_evolve 自动沉淀经验
```

### 当前状态

| RAG asset | 医案条目 | 公版文献 | 蒸馏指南 | 推算脚本 | CI 测试 |
|---:|---:|---:|---:|---:|---:|
| 32 | 1994 | 51 篇 | 12 本 | 46 个 | 36 项 CI 校验全绿 |

路由核心由一个 `routing.yaml` 驱动，跨工具薄壳自动发现，推算引擎与知识库分离。

<p align="right">(<a href="#这是什么">返回顶部</a>)</p>

**为什么需要这个项目：**
- 大模型容易对干支、司天在泉、客主加临产生幻觉--本包用确定性推算引擎，大寒定年，结果可复现
- 运气知识分散在经典中，普通人难以系统掌握--本包把 51 篇公版文献蒸馏成可 Grep 的结构化指南
- 缺少专为 Agent 设计的运气学技能包--本包提供路由契约、ReAct 工作流、自进化经验库，开箱即用

> ⚠️ 运气学为中医传统理论，本包用于学习研究与辅助推理，不构成医学诊断或治疗建议。临床决策须由执业医师处理。

## 适合谁用

- **中医学生 / 研究者** —— 需要准确推算某年某步运气格局，检索历代医家临证经验
- **AI 应用开发者** —— 想给 Agent 加一个可靠的运气学能力，而非自己从头实现
- **运气学爱好者** —— 想通过自然对话理解天人合一、气化、中和这些思想，而不是背表格

## 快速上手

### 最短安装（推荐）

把下面这段话直接发给 Claude（或其他支持技能的 AI）：

```text
仓库地址：https://github.com/dhicoc/wuyun-liuqi-skills.git

请按 workflows/one-line-install.md 帮我安装五运六气技能包：
克隆仓库、运行 python scripts/install.py --link-global、验证通过。
```

AI 会完成：克隆 → 注册全局技能 → 验证。之后在任意项目里说「五运六气」即可激活。

### 手动安装

```bash
# 1. 克隆
git clone https://github.com/dhicoc/wuyun-liuqi-skills.git
cd wuyun-liuqi-skills

# 2. 装 Python 依赖（仅需 lunar-python，用于精确节气）
pip install -r requirements.txt

# 3. 可选：Node.js 接口依赖
npm install

# 4. 注册全局技能（Claude / Cursor 自动发现）
python scripts/install.py --link-global
```

环境要求：Python 3.8+ / Node.js 14+。

### 三十秒验证

```bash
# 算今天的运气
python scripts/calculate_yunqi_api.py today --summary

# 深度解读某个概念
python scripts/calculate_yunqi_api.py today --level deep --explain-concept "天人合一"

# 检索医案
python scripts/rag_search.py 头痛 --asset asset26,asset27
```

### 激活方式

| 场景 | 做法 | 适合 |
|------|------|------|
| 在本仓库用 | 用 Cursor / Claude 打开 `wuyun-liuqi-skills` 文件夹 | 初学、试用 |
| 在任意项目用 | `python scripts/install.py --link-global` | 日常常驻（推荐） |
| Claude Code 插件 | `/plugin marketplace add dhicoc/wuyun-liuqi-skills` → `/plugin install wuyun-liuqi-skills@wuyun-liuqi-skills` | Claude Code 用户 |

配置好后，直接对 Agent 说话即可：

- 「今年运气对养生有什么启发？」
- 「我出生那年的运气格局和体质有什么关系？」
- 「用简单语言解释司天在泉」
- 「历代医家怎么治头痛？给我对比孙一奎和叶天士」

## 核心能力

### 🔮 确定性推算引擎

干支推算 · 大运太过不及 · 司天在泉 · 客主加临六步 · 平气判定 · 天符岁会。Python 主链路 + JS 可选接口，双引擎一致性校验，大寒定年，结果可信。

```bash
python scripts/calculate_yunqi_api.py today --json    # Agent / JSON 接口
python scripts/calculate_yunqi_api.py 2026-06-27 --summary
```

### 📚 1994 条真实医案 · 21 部公版典籍

从维基文库公版原文逐字蒸馏，零占位、零编造，每条医案附 `source_quote` 原文存证。覆盖名医类案、续名医类案、古今医案按、丁甘仁、伤寒九十论、临证指南、回春录、张聿青、吴鞠通、寓意草、洄溪、花韵楼、杏轩（184 条）、孙文垣（390 条）等 21 部。

### 🔍 多维检索

| 检索方式 | 示例 |
|----------|------|
| 关键词检索 | `rag_search.py 头痛` |
| 跨库联合检索 | `rag_search.py 头痛 --asset asset26,asset27` |
| 按字段精准检索 | `rag_search.py --field herbs 石膏` |
| 口语语义检索 | `rag_search.py --semantic 心火偏旺` |
| 医案对比 | `case_relations.py --compare 孙一奎,叶桂 --tag 中风` |
| 相似医案发现 | `case_relations.py --related swy_174` |

### 🧠 Agent 自进化 Fallback

工具答不上来时，Agent 不拒绝、不硬编，而是：联网搜索 -> 总结回答（标注来源 + 免责声明）-> 沉淀经验到 `case-journal/field-journal/` -> 下次优先查经验库。越用越聪明。

### 📖 五层注释链（公版蒸馏指南）

| 层 | 指南 | 来源 | 回答什么 |
|----|------|------|----------|
| 方药层 | `sanyin_sitianfang_guide.md` | 《三因极一》陈无择 | 用什么方、六步怎么加减 |
| 教材层 | `yunqi_yaojue_pathogenesis_guide.md` | 《运气要诀》吴谦 | 病机歌诀、标准表述 |
| 病机层 | `sujwen_xuanji_pathogenesis_guide.md` | 《素问玄机原病式》刘完素 | 逐症状辨病机 |
| 本体论层 | `leijing_tuyi_yunqi_philosophy_guide.md` | 《类经图翼》张介宾 | 太极阴阳五行本体 |
| 治法层 | `baoming_zhifa_guide.md` | 《素问病机气宜保命集》刘完素 | 病机十九条治则 |

全部零依赖，Agent 直接 Grep + Read。

### 🎭 注家人格 Perspective

刘完素（寒凉派）与张介宾（温补派）做成可运行的 perspective skill，Agent 激活后能切换到注家视角回答问题，而非「替注家说话」。两方原文均可 Grep，形成运气学史上最尖锐的立场对照。

### 🏥 医学安全边界

- 所有临床输出强制附加免责声明
- 运气理论分析 ≠ 医疗建议，后者必须建议就医
- 方药标注「参考方药，须辨证加减」
- 不给出具体药物剂量

## 完整功能清单

> 共 46 个脚本 · 6 个子技能模块 · 10 个教学模块 · 2 个注家人格 · 32 个 RAG asset · 51 篇公版文献 · 12 本蒸馏指南

### 推算引擎（9 个）

| 功能 | 入口脚本 | 说明 |
|------|----------|------|
| 统一推算（主链路） | `calculate_yunqi_api.py` | 大寒定年 + 干支/大运/主运客运/司天在泉/客主加临，输出 JSON + rag_keys |
| JS 版推算 | `calculate_yunqi_api.js` | 面向前端/Node 集成，与 Python 双引擎一致性校验 |
| 聚合 CLI | `yunqi_cli.py` | calc/report/map/learn/search/dashboard 统一入口 |
| Py/JS 一致性校验 | `compare_py_js_yunqi.py` | 关键字段跨语言对比 |
| 病机推理链 | `infer_pathogenesis.py` | 岁运病机 -> 司天在泉病机 -> 六步加临 -> 推荐方剂 |
| 天气对齐 | `weather_alignment.py` | 实时气象 × 运气格局交叉（Open-Meteo，`--mock` 可测） |
| 天气 × 体质叠加 | `yunqi_weather_constitution.py` | 出生体质 × 当前岁运 × 天气实况三维分析 |
| 统一高级对齐 | `advanced_alignment.py` | 基础运气 + 体质 + 九种体质量表 + 天气对齐统一入口 |
| 个人运气体质 | `personal_yunqi_profile.py` | 出生年运气格局 + 体质倾向 + 调理方向 |

### 知识检索（5 个）

| 功能 | 入口脚本 | 说明 |
|------|----------|------|
| RAG 多维检索 | `rag_search.py` | 关键词 / `--key` 精确 / `--date` 按日 / `--field` 按字段 / `--asset` 多库 / `--semantic` 口语 |
| 轻量语义检索 | `rag_semantic.py` | 字符 n-gram 语义匹配，无需向量数据库 |
| 医案关联图谱 | `case_relations.py` | 跨医家对比 `--compare` + 相似医案发现 `--related` |
| 医案结构化字段提取 | `extract_structured_fields.py` | 提取 herbs（药味）+ formulas_referenced（方剂）字段 |
| 文献注入 RAG | `ingest_literature.py` | 将新文献注入 RAG 知识库 |

### 检索增强与引用（本轮新增）

| 功能 | 入口脚本 | 说明 |
|------|----------|------|
| 稳定引用解析 | `resolve_ref.py` | `yle:<asset>:<entry_id>` 反解 + 可访问率门禁（`--selfcheck`） |
| 医案渐进加载路由 | `cases_routing.py` | 按病证/运气拿首选+补充+强制联动库清单，避免整包载入 |
| 字形归一化检索 | `rag_search.py`（内建） | 异体/繁简互通（針/鍼→针、證→证、痺→痹 等 70 项），白话语义更准 |
| 检索词歧义消解 | `rag_search.py --show-terms` | 展示「原词→归一化→同义词 OR 表」 |
| 两段式补检索 | `rag_search.py --include-extra` | 主检索后按归一化核心词补一轮更宽 OR 检索（默认关） |

### 报告与导出（6 个）

| 功能 | 入口脚本 | 说明 |
|------|----------|------|
| 综合年度报告 | `yunqi_report.py` | 学生/临床/研究版 Markdown 报告，可选注入高级对齐章节与「内经方法论」章节（`--no-neijing` 关闭） |
| HTML 可视化报告 | `generate_html_report.py` | 宣纸水墨设计体系，深色屏幕/浅色打印双态 |
| 思想导出 | `export_thought.py` | 纯文本摘要 / Anki 卡片（TSV+MD）/ 可打印 HTML/PDF |
| 思想地图 | `export_thought_map.py` | Mermaid 概念图 + 年结构图 |
| 运气时间轴 | `visualize_timeline.py` | 年度六步时间轴 HTML |
| 医案浏览器 | `generate_case_browser.py` | 1994 条医案可视化浏览 HTML |

### 学习与教学（3 个）

| 功能 | 入口脚本 | 说明 |
|------|----------|------|
| 苏格拉底学习会话 | `socratic_learn.py` | 提问式引导学习，逐步深入 |
| 学习路径仪表盘 | `learning_dashboard.py` | 概念覆盖度 + 产物追踪 + 推荐下一步 |
| 全链路演示 | `demo_full_chain.py` | 推算 -> 检索 -> 病机 -> 报告端到端演示 |

### 自进化与运维（7 个）

| 功能 | 入口脚本 | 说明 |
|------|----------|------|
| 自进化引擎 | `self_evolve.py` | 日志 / 反馈 / 盲区检测 / 月报 / 清理 / 自动建议 |
| 环境检查 | `health_check.py` | 依赖、路径、配置完整性检查 |
| 知识库校验 | `validate_knowledge_base.py` | 32 个 asset JSON schema 校验 |
| RAG 索引生成 | `generate_rag_index.py` | 生成 / 刷新 RAG 检索索引 |
| 报告质量门禁 | `report_quality_gate.py` | 报告输出前的质量校验 |
| 路由同步 | `sync_routing.py` | 改 routing.yaml 后同步到各入口文件 |
| 临床安全检查 | `clinical_safety.py` | 临床输出免责声明合规检查 |

### 安装与校验（6 个）

| 功能 | 入口脚本 | 说明 |
|------|----------|------|
| 安装器 | `install.py` | `--link-global` 注册全局技能（Claude/Cursor 自动发现） |
| 一致性检查 | `check_conformance.py` | conformance.yaml 配置一致性 |
| 路由场景测试 | `check_routing_scenarios.py` | routing.yaml 路由命中回归 |
| 技能结构检查 | `check_skill_structure.py` | SKILL.md / routing.yaml 结构完整性 |
| 孤儿文件审计 | `audit_orphans.py` | 扫描未被路由引用的孤立文件 |
| 全链路冒烟测试 | `smoke_full_chain.py` | 快速端到端冒烟 |

### 子技能模块（6 个，routing.yaml 路由目标）

| 模块 | 目录 | 覆盖能力 |
|------|------|----------|
| 干支基础 | `modules/ganzhi-basics/` | 天干地支、六十甲子、生肖、节气与运气 |
| 运气推算 | `modules/yunqi-calc/` | 大运太过不及、主运客运五步、司天在泉、客主加临、平气、天符岁会 |
| 病机分析 | `modules/yunqi-pathogenesis/` | 五运病机、六气病机、运气合病、太过不及病机 |
| 临床应用 | `modules/yunqi-clinical/` | 治则治法、三因司天方、针灸选穴、养生调理（含免责声明） |
| 经典文献 | `modules/yunqi-classics/` | 素问七篇大论、历代运气学说、现代研究索引 |
| 报告生成 | `modules/docs-generator/` | 学生/临床/研究版报告模板 |

### 知识库资产

| 类别 | 数量 | 说明 |
|------|------|------|
| RAG 键值 asset | 32 个 | 病机/方剂/注家/地域/体质/岁图医案/瘟疫防治/历代名家医案 21 部 |
| 公版文献原文 | 51 篇 | 约 177.4 万字，先秦至清代，含素问七篇大论、遗篇、圣济岁图、玄珠密语等 |
| 公版蒸馏指南 | 12 本 | 五层注释链 5 本 + 35 篇分组合并 5 本 + 补充指南，Grep+Read 零依赖 |
| 术语库 | 700 条 | `terminology.json`，通过 rag_keys 精确匹配 |
| 历代医案总数 | 1994 条 | 21 部公版医案库，含 herbs + formulas_referenced 结构化字段 |

### 教学模块（10 个概念）

`teaching-modules/` 下每个概念一个五段式模块（原文 / 注家 / 解读 / 金句 / 误区 / 深度分层）：

天人合一 · 气化 · 中和 · 大运岁运 · 五运推移 · 太过不及 · 平气 · 司天在泉 · 客主加临 · 天符岁会

### 注家人格（2 个）

| Perspective | 注家 | 派别 | 核心立场 |
|-------------|------|------|----------|
| `perspectives/liu-wansu-perspective/` | 刘完素（金） | 寒凉派 | 六气皆从火化、不可峻用辛温、兼化虚象不可误治 |
| `perspectives/zhang-jiebin-perspective/` | 张介宾（明） | 温补派 | 阳气为本、五行互藏、生中有克克中有用 |

### 高级对齐

| 能力 | 说明 |
|------|------|
| 天气 × 运气 | 实时气象（Open-Meteo）× 运气格局，判断内外邪相合/相背/兼夹 |
| 体质 × 运气 | 九种体质量表 × 出生运气格局 × 当前岁运调理方向 |
| 地域修正 | 八大气候区地域修正因子 |
| 三维叠加 | 出生体质 × 当前岁运 × 天气实况统一分析 |

### CI 持续集成

- GitHub Actions 矩阵：Python 3.10/3.11/3.12 + Node 18/20/22
- 36 项 CI 校验步骤：validate · index · conformance · routing · regression · e2e · scenario · random-chain · answer-layer · retrieval-quality · cross-check · expansion · advanced-alignment 等
- 每次推送前本地跑通全部 CI 同款测试，全绿才推送

## 项目结构

```
.
├── SKILL.md                    # ★ 总控路由入口（AI 必读）
├── routing.yaml / routing.md   # ★ 路由真相源 / 人类索引
├── AGENTS.md / CLAUDE.md       # 跨工具薄壳（Codex / Claude）
├── scripts/                    # 46 个 Python 脚本 + JS 接口
│   ├── calculate_yunqi_api.py  #   ★ 主链路（大寒定年 + rag_keys）
│   ├── rag_search.py           #   ★ RAG 检索
│   ├── case_relations.py       #   医案对比 / 相似发现
│   ├── personal_yunqi_profile.py #   个人体质
│   ├── self_evolve.py          #   自进化引擎
│   └── …                       #   报告/导出/校验等
├── wuyun_liuqi/                # 可导入 Python 包
├── rag-knowledge-base/         # ★ 32 个 asset + 蒸馏指南 + 文献原文
│   ├── asset1-32 *.json        #   病机/方/注家/体质/医案（含 21 部医案库）
│   ├── *_guide.md              #   10 本公版蒸馏指南
│   └── literature/             #   51 篇公版文献原文（177.4 万字）
├── modules/                    # 子技能（routing.yaml 路由目标）
│   ├── ganzhi-basics/          #   干支基础
│   ├── yunqi-calc/             #   运气推算（核心）
│   ├── yunqi-pathogenesis/     #   病机分析
│   ├── yunqi-clinical/         #   临床应用
│   ├── yunqi-classics/         #   经典文献
│   └── docs-generator/         #   报告生成
├── perspectives/               # 注家人格（刘完素 / 张介宾）
├── rules/                      # medical-safety / calculation / agent-behavior
├── workflows/                  # bootstrap / routing-contract / task-closure
├── prompts/                    # system_prompt + expression_style
├── case-journal/               # 医案沉淀
├── tests/                      # 全量回归（36 项 CI 校验步骤）
└── .github/workflows/          # CI（Python 3.10/3.11/3.12 + Node 18/20/22）
```

## 验证

```bash
python scripts/health_check.py
python scripts/validate_knowledge_base.py
python tests/full_regression_test.py   # 等效 CI 校验（55 项回归 + 105 项扩展验证）
python tests/skill_full_feature_smoke.py --rounds 3   # 全功能全场景多轮冒烟（触发所有入口脚本 + 模块/教学/人格结构）
```

每次推送前本地跑通全部 CI 同款测试，全绿才推送。

## 贡献

欢迎 Fork → 特性分支 → PR。贡献前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

```bash
git checkout -b feature/your-feature
git commit -m "Add your feature"
git push origin feature/your-feature
# 提交 Pull Request
```

## 许可证

MIT License，详见 [LICENSE](LICENSE)。

## 相关项目

- [huangdi-neijing-skill](https://github.com/kangarooking/huangdi-neijing-skill) ⭐31 -- 把《黄帝内经》素问+灵枢蒸馏成 22 个思维方法论 skill，与本项目的运气推算能力互补；其方法论已 **vendored 快照**集成进报告「内经方法论」章节（详见 [`teaching-modules/相关思维工具.md`](teaching-modules/相关思维工具.md)）。

### 致谢

- 架构参考 [reverse-skill](https://github.com/zhaoxuya520/reverse-skill)
- 理论依据：《黄帝内经素问》七篇大论
- AI 社区：[linux.do](https://linux.do)
