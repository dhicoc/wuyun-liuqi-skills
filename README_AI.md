# WuYun-LiuQi Skills — AI Agent Bootstrap

> **这是 AI Agent 的执行引导文件。若你是 AI Agent，请优先读取并遵循本文件；人类用户可将其视为自动化使用说明。**

---

## 0. 总原则

### 0.1 主链路优先级

本技能包以 **Python 推算引擎** 为主链路：

1. **首选入口**：`scripts/calculate_yunqi_api.py`
2. **主报告入口**：`scripts/yunqi_report.py`
3. **个人体质入口**：`scripts/personal_yunqi_profile.py`
4. **可视化入口**：`scripts/visualize_yunqi.py`、`scripts/generate_html_report.py`
5. **自进化入口**：`scripts/self_evolve.py`
6. **JS 可选接口**：`scripts/calculate_yunqi_api.js` 仅作为前端 / Node.js 集成适配层；若追求完整功能覆盖、回归稳定性和 Agent 集成一致性，请优先使用 Python 版。

### 0.2 医学安全边界

五运六气分析属于中医运气学理论推演：

- 可以输出：干支、岁运、司天在泉、客主加临、病机倾向、养生调理方向、文献依据。
- 必须区分：**运气理论分析** 与 **具体诊疗建议**。
- 不得替代执业医师辨证论治。
- 不得给出具体药物剂量。
- 涉及方药、针灸、临床判断时，必须附加免责声明。

标准免责声明：

> ⚠️ 免责声明：以上分析基于中医运气学说理论推算，仅供参考。运气学说非现代医学诊断标准，具体诊疗须由执业中医师辨证论治。请勿据此自行用药或针灸。

---

## 1. 安装与环境检查

### 1.1 人类用户手动安装

```bash
# 克隆后进入项目目录
pip install -r requirements.txt

# 可选：仅当需要 Node.js 接口时安装
npm install

# 环境检查
python scripts/health_check.py
```

快速试用：

```bash
python scripts/calculate_yunqi_api.py 2026-06-27 --json
python scripts/demo_full_chain.py 2026-06-27
python scripts/verify_expansion.py
```

### 1.2 AI Agent 自动检查流程

AI Agent 首次进入本技能包时执行：

```text
0. 确定技能包根目录，记为 <SKILL_ROOT>
1. 检查核心文件是否存在：
   - SKILL.md
   - routing.md
   - RULES.md
   - scripts/calculate_yunqi_api.py
   - rag-knowledge-base/
2. 检查 Python 依赖：
   - python -c "import lunar_python"
3. 若依赖缺失：
   - Windows → scripts/setup.bat
   - Linux/macOS → bash scripts/setup.sh
4. 运行健康检查：
   - python scripts/health_check.py
5. 读取执行契约：
   - SKILL.md
   - routing.md
   - case-journal/precedent-disclaimer.md
6. 根据用户输入匹配子技能并执行。
```

> 若用户只要求解释、总结或文档优化，不必运行完整推算链路；若任务涉及日期、年份、个人运气、病机或报告，必须调用 Python 脚本获取推算结果，不得凭记忆推算。

---

## 2. 三轴路由规则

所有任务按三轴路由：

| 维度 | 分类 | 决定内容 |
|------|------|----------|
| 时间维度 | 公历日期 / 公历年份 / 农历日期 / 当前时间 / 节气 | 决定调用日期 API、年份脚本或引导用户补充信息 |
| 用户意图 | 快速推算 / 完整报告 / 病机分析 / 养生调理 / 文献学习 / 个人体质 | 决定报告深度与子技能组合 |
| 知识层级 | 推算层 / 病机层 / 临床层 / 文献层 / Agent 层 | 决定是否进入 RAG、临床参考、经典文献或自进化流程 |

### 2.1 快速决策表

| 用户请求 | 推荐执行 |
|----------|----------|
| “算某日/今天运气” | `python scripts/calculate_yunqi_api.py <YYYY-MM-DD> --summary` |
| “给我 JSON / Agent 接口” | `python scripts/calculate_yunqi_api.py <YYYY-MM-DD> --json` |
| “当前步位/最近如何” | `python scripts/calculate_yunqi_api.py <YYYY-MM-DD> --focus current-step` |
| “生成可视化” | `python scripts/generate_html_report.py <YYYY-MM-DD>` |
| “完整年度报告” | `python scripts/yunqi_report.py <YYYY> --audience student|practitioner|researcher` |
| “个人运气/出生日期分析” | `python scripts/personal_yunqi_profile.py <出生日期> [地区]` |
| “病机/治法/养生” | 先调用 `calculate_yunqi_api.py --json`，再读取 `yunqi-pathogenesis/` 与 `yunqi-clinical/` |
| “经典依据/术语解释” | 读取 `yunqi-classics/`、`rag-knowledge-base/terminology.json` |
| “测试全部功能” | 运行 `health_check.py`、`verify_expansion.py`、`full_regression_test.py`，必要时补充用户指定日期的脚本测试 |

### 2.2 模糊输入处理

当用户只说“看看五运六气”“帮我分析”等，且没有日期、年份或意图时：

1. 不直接进入完整临床报告。
2. 先询问：日期/年份、关注方向、是否个人出生运气。
3. 可默认推荐：今天 + 快速摘要。

---

## 3. 推算引擎调用规范

### 3.1 统一日期接口（Agent 首选）

```bash
python scripts/calculate_yunqi_api.py <YYYY-MM-DD> --json
```

常用模式：

| 模式 | 命令 |
|------|------|
| 标准文本 | `python scripts/calculate_yunqi_api.py 2026-06-27` |
| JSON 输出 | `python scripts/calculate_yunqi_api.py 2026-06-27 --json` |
| 快速摘要 | `python scripts/calculate_yunqi_api.py 2026-06-27 --summary` |
| 当前步位 | `python scripts/calculate_yunqi_api.py 2026-06-27 --focus current-step` |
| ASCII 可视化 | `python scripts/calculate_yunqi_api.py 2026-06-27 --visual` |
| 术语解释 | `python scripts/calculate_yunqi_api.py 2026-06-27 --explain` |
| HTML 报告 | `python scripts/calculate_yunqi_api.py 2026-06-27 --html` |
| 学生/临床/研究报告 | `python scripts/calculate_yunqi_api.py 2026-06-27 --report-type student|practitioner|researcher` |

### 3.2 标准 JSON 字段

实际输出以 `calculate_yunqi_api.py --json` 为准，核心字段包括：

```json
{
  "date": "2026-06-27",
  "yunqi_year": 2026,
  "year_gz": "丙午",
  "year_gan": "丙",
  "year_zhi": "午",
  "sexagenary_index": 43,
  "shengxiao": "马",
  "day_gz": "...",
  "sui_yun": {
    "name": "水运",
    "element": "水",
    "status": "太过",
    "code": "water_excess",
    "tiangan": "丙"
  },
  "si_tian": "少阴君火",
  "zai_quan": "阳明燥金",
  "current_step": {
    "step_number": 3,
    "name": "三之气(主小满~大暑)",
    "zhu_qi": "少阳相火",
    "ke_qi": "少阴君火",
    "relation": "客主同气",
    "shun_ni": "相得（顺）"
  },
  "tong_hua": {
    "tianfu": false,
    "suihui": false,
    "taiyi_tianfu": false,
    "pingqi": false
  },
  "rag_keys": {
    "suiyun": "water_excess",
    "sitian": "shaoyin_junhuo_sitian",
    "zaiquan": "yangming_zaojin_zaiquan",
    "current_step": "zhu_shaoyang_ke_shaoyin"
  }
}
```

### 3.3 单项推算脚本

| 场景 | 命令 |
|------|------|
| 干支推算 | `python scripts/ganzhi_calc.py 2026 [--json]` |
| 大运太过不及 | `python scripts/dayun_calc.py 2026 [--json]` |
| 主运客运 | `python scripts/keyun_calc.py 2026 [--json]` |
| 六气推算 | `python scripts/liuqi_calc.py 2026 [--json]` |
| 客主加临 | `python scripts/kezhujialin.py 2026 [--json]` |
| 年度综合报告 | `python scripts/yunqi_report.py 2026 --audience student|practitioner|researcher` |

### 3.4 JavaScript 可选接口

```bash
node scripts/calculate_yunqi_api.js <YYYY-MM-DD> --json
```

使用规则：

- 仅在用户明确要求 Node.js、前端集成或 JS 接口时优先调用。
- 若 JS 与 Python 结果不一致，以 Python 结果为准。
- 若 Node.js 或 `lunar-javascript` 缺失，降级为 Python 主链路。

---

## 4. 功能覆盖矩阵

| 功能层级 | 覆盖能力 | 主入口 / 文件 | 状态 |
|----------|----------|---------------|------|
| 干支基础 | 年干支、六十甲子序号、生肖 | `scripts/ganzhi_calc.py` | ✅ 已覆盖 |
| 五运推算 | 天干化五运、大运太过/不及、平气判断 | `scripts/dayun_calc.py`、`yunqi-calc/` | ✅ 已覆盖 |
| 主运客运 | 主运五步、客运五步、太少推移 | `scripts/keyun_calc.py` | ✅ 已覆盖 |
| 六气推算 | 司天、在泉、主气六步、客气六步 | `scripts/liuqi_calc.py` | ✅ 已覆盖 |
| 客主加临 | 六步客主关系、相得/不相得、顺逆分析 | `scripts/kezhujialin.py` | ✅ 已覆盖 |
| 日期统一接口 | 大寒定年、日干支、当前步位、RAG keys、JSON 输出 | `scripts/calculate_yunqi_api.py` | ✅ Python 主链路 |
| Node.js 接口 | 前端 / Node.js 集成 JSON 输出 | `scripts/calculate_yunqi_api.js` | 🟡 可选接口 |
| 病机分析 | 五运病机、六气病机、胜复、运气合病 | `yunqi-pathogenesis/` | ✅ 文档化推理 |
| 临床应用 | 治则治法、方药方向、针灸选穴、养生调理 | `yunqi-clinical/` | ✅ 参考建议，需免责声明 |
| 经典文献 | 素问七篇、历代学说、现代研究 | `yunqi-classics/` | ✅ 已覆盖 |
| RAG 知识库 | 岁运、司天在泉、客主加临、方剂、注家、地域、体质 | `rag-knowledge-base/asset*.json` | ✅ 已覆盖 |
| 个人体质 | 出生年运气倾向、当前岁运调理、地域修正 | `scripts/personal_yunqi_profile.py` | ✅ 已覆盖 |
| 报告生成 | 学生版、临床版、研究版报告 | `scripts/yunqi_report.py`、`docs-generator/` | ✅ 已覆盖 |
| 可视化 | 终端 ASCII、HTML 可视化报告 | `scripts/visualize_yunqi.py`、`scripts/generate_html_report.py` | ✅ 已覆盖 |
| 自进化 | 使用日志、盲区检测、反馈、月度报告 | `scripts/self_evolve.py` | ✅ 已覆盖 |
| 校验测试 | 环境检查、知识库校验、端到端测试、全量回归 | `scripts/health_check.py`、`scripts/validate_knowledge_base.py`、`scripts/verify_expansion.py`、`scripts/full_regression_test.py` | ✅ 已覆盖 |

---

## 5. RAG 知识库调用

| 层 | Asset | 用途 | 典型 key |
|----|-------|------|----------|
| 岁运病机 | `asset1_suiyun.json` | 五运太过/不及病机 | `water_excess` |
| 司天在泉 | `asset2_sitian_zaiquan.json` | 上下半年六气病机 | `shaoyin_junhuo_sitian` |
| 客主加临 | `asset3_kezhujialin.json` | 当前步位主客关系 | `zhu_shaoyang_ke_shaoyin` |
| 运气方 | `asset4_formula.json` | 三因司天方与方药方向 | `water_excess` |
| 历代注家 | `asset5_commentary.json` | 王冰、刘完素、张景岳等观点 | related keys |
| 地域修正 | `asset6_regional.json` | 八大区域气候修正 | 地区名 / region_id |
| 体质交叉 | `asset7_constitution.json` | 出生运气体质、岁运调理 | `fire_deficient` |
| 术语解释 | `terminology.json` | 术语解释与教学辅助 | term / entry_id |

检索流程：

```text
1. 调用 calculate_yunqi_api.py 获取 rag_keys
2. 用 suiyun / sitian / zaiquan / current_step 精确检索 asset1-3
3. 如需方药方向，检索 asset4
4. 如需注家观点，检索 asset5
5. 如用户提供地区，检索 asset6
6. 如用户提供出生日期或体质，检索 asset7
7. 汇总进入结构化报告
```

---

## 6. ReAct 推理工作流

详细规范见：[agent-workflow/react_workflow.md](agent-workflow/react_workflow.md)。

```text
prompts/system_prompt.md → 加载 TCM 运气专家角色约束
  ↓
scripts/calculate_yunqi_api.py → 获取推算结果 + rag_keys
  ↓
rag-knowledge-base/ → 多层知识检索
  ↓
yunqi-pathogenesis/ → 病机分析
  ↓
yunqi-clinical/ → 治则、方药方向、针灸参考、养生调理
  ↓
advanced-alignment/ → 可选：天气对齐、地域修正、体质交叉
  ↓
docs-generator/ → 结构化报告
  ↓
scripts/self_evolve.py → 记录使用与反馈
```

### 6.1 输出措辞要求

- 使用传统运气学和中医病机措辞。
- 避免把运气推算包装成现代医学诊断。
- 涉及现代医学名词时，应说明其不属于运气理论本体，避免混用概念。
- 方药只给方向与参考，不给剂量。
- 针灸必须提示“需由执业针灸师操作”。

---

## 7. 自进化引擎

每次完成实质推算或报告后，可记录使用：

```bash
python scripts/self_evolve.py log \
  --input <日期或年份> \
  --rag-keys <key1,key2,key3> \
  --source user_query
```

常用命令：

| 场景 | 命令 |
|------|------|
| 使用统计 | `python scripts/self_evolve.py stats --type top_keys` |
| 盲区分析 | `python scripts/self_evolve.py analyze --type blind_spots` |
| 优化报告 | `python scripts/self_evolve.py report` |
| 月度报告 | `python scripts/self_evolve.py monthly-report` |
| 用户反馈 | `python scripts/self_evolve.py feedback --session-id <id> --rating <1-5> --comment "..."` |

---

## 8. 关键入口文件

| 文件 | 用途 |
|------|------|
| [SKILL.md](SKILL.md) | 总控入口 + 路由执行契约 |
| [routing.md](routing.md) | 三轴路由矩阵 |
| [RULES.md](RULES.md) | 行为规则链 |
| [case-journal/precedent-disclaimer.md](case-journal/precedent-disclaimer.md) | 医学免责声明 |
| [agent-workflow/react_workflow.md](agent-workflow/react_workflow.md) | ReAct 推理工作流 |
| [prompts/system_prompt.md](prompts/system_prompt.md) | TCM 运气专家角色约束 |
| [scripts/calculate_yunqi_api.py](scripts/calculate_yunqi_api.py) | ★ Python 主链路统一计算接口 |
| [scripts/calculate_yunqi_api.js](scripts/calculate_yunqi_api.js) | 可选 Node.js 接口 |
| [scripts/personal_yunqi_profile.py](scripts/personal_yunqi_profile.py) | 个人运气体质分析 |
| [scripts/self_evolve.py](scripts/self_evolve.py) | 自进化引擎 |
| [scripts/verify_expansion.py](scripts/verify_expansion.py) | 端到端验证 |
| [rag-knowledge-base/](rag-knowledge-base/) | RAG 知识库 |
| [rag-knowledge-base/index.json](rag-knowledge-base/index.json) | RAG 资产索引 |
| [docs/architecture.md](docs/architecture.md) | 项目架构说明 |
| [docs/function-coverage.md](docs/function-coverage.md) | 功能覆盖说明 |
| [docs/roadmap.md](docs/roadmap.md) | 后续路线图 |
| [reports/examples/](reports/examples/) | 示例报告与预览图 |
| [reports/generated/](reports/generated/) | 本地生成报告 |
| [reports/test-results/](reports/test-results/) | 测试输出 |
| [docs-generator/](docs-generator/) | 报告模板 |
| [advanced-alignment/](advanced-alignment/) | 天气、地域、体质高级对齐 |

---

## 9. 故障处理

### 9.1 依赖缺失降级

| 缺失组件 | 处理方式 |
|----------|----------|
| `lunar-python` | 运行 `pip install -r requirements.txt`；必要时使用近似节气表，提示精度降级 |
| Python 3.8+ | 提示用户安装 Python，无法完整执行主链路 |
| Node.js | 不影响 Python 主链路；仅 JS 可选接口不可用 |
| `lunar-javascript` | 运行 `npm install`；或直接降级为 Python 主链路 |
| RAG asset 缺失 | 先运行 `python scripts/validate_knowledge_base.py`，报告缺失文件 |

### 9.2 大寒定年边界

运气年以 **大寒** 为界，而非公历 1 月 1 日：

```text
2026-01-15 → 运气年 2025（乙巳）
2026-01-20 → 运气年 2026（丙午）
2027-01-19 → 运气年 2026（丙午）
2027-01-20 → 运气年 2027（丁未）
```

### 9.3 校验命令

```bash
python scripts/health_check.py
python scripts/validate_knowledge_base.py
python scripts/verify_expansion.py
python scripts/full_regression_test.py
```

---

## 10. 标准输出结构

```markdown
# 五运六气分析报告

## 基本信息
- 输入日期 / 年份：...
- 运气年：...
- 干支：...
- 推算脚本：scripts/calculate_yunqi_api.py

## 运气格局
- 岁运：...
- 司天：...
- 在泉：...
- 当前步位：...
- 客主加临：...

## 病机分析
- 五运病机：...
- 六气病机：...
- 胜复 / 顺逆：...

## 调理方向
- 起居：...
- 饮食：...
- 情志：...
- 方药 / 针灸参考：仅在用户明确需要时给出，且必须附免责声明。

## 术语解释 / 文献依据
- ...

⚠️ 免责声明：以上分析基于中医运气学说理论推算，仅供参考。运气学说非现代医学诊断标准，具体诊疗须由执业中医师辨证论治。请勿据此自行用药或针灸。
```

---

> **执行完成后，如发现知识盲区、脚本异常或用户反馈，应记录到 `self-evolve/`；如形成临床案例，应按 `case-journal/` 模板沉淀。**
