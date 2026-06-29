---
name: wuyun-liuqi
description: >
  五运六气（运气学）AI Agent 技能包。根据中医运气学说，推算任意年份的五运六气格局，
  分析气候-病机关联，提供运气治法与方药参考，索引经典文献。
  触发词：五运六气、运气、大运、主运客运、主气客气、司天在泉、客主加临、
  太过不及、天符岁会、运气病机、运气治法、七篇大论。
  面向人群：学生（学习推算）、医师（临床参考）、研究者（文献检索）。
---

# 五运六气总控入口

## 0. 首次安装与依赖检查（AI 首次读取后立即执行）

> **本 Skill 首次使用时，AI 必须自动完成以下安装流程，用户无需手动操作。**
> 如果已经执行过 README_AI.md 的自动配置，确认依赖就绪后直接跳到「路由执行契约」开始工作。

```text
0. 检测本包路径（由 SKILL.md 所在目录推导），记为 <SKILL_ROOT>

1. 检查 Python 依赖是否已安装：
   python -c "import lunar_python" 2>/dev/null && echo OK || echo MISSING

2. 如果缺失 → 执行安装脚本：
   Windows: powershell -File "<SKILL_ROOT>\scripts\setup.bat"
   Linux/macOS: bash <SKILL_ROOT>/scripts/setup.sh
   安装脚本自动：pip install -r requirements.txt（安装 lunar-python 等）

3. 验证安装结果并向用户报告：
   ✅ Python: lunar-python ✓
   ✅ 推算引擎: scripts/calculate_yunqi_api.py ✓
   ✅ RAG 知识库: rag-knowledge-base/ ✓
   ✅ 自进化引擎: scripts/self_evolve.py ✓
   ✅ 端到端验证: python scripts/verify_expansion.py（67 项测试）

4. 确认就绪后，继续执行以下工作流。
   如果 pip install 失败 → 降级使用近似节气表，告知用户精度受限
```

---

> 本技能包基于《黄帝内经·素问》七篇大论，运用天干地支推算年度气候与疾病规律。
> **重要声明**：运气学说为中医传统理论，非现代医学诊断标准。AI 输出的临床分析仅供参考，
> 具体诊疗须由执业中医师辨证论治。详见 `case-journal/precedent-disclaimer.md`。

## CRITICAL: 路由执行契约

进入本技能包的任何任务，MUST 遵循以下执行序列：

### NOW（立即执行）
1. 读取 `routing.md` 完成路由匹配（三轴：时间维度 + 用户意图 + 知识层级）
2. **如用户意图模糊或仅发送触发词，先读取 `prompts/onboarding_prompt.md` 进行轻量级引导，不得直接进入完整推算/临床报告流程**
3. 读取 `case-journal/precedent-disclaimer.md`（医学免责声明前置）
4. 读取目标子技能的 `SKILL.md`

### NEXT（路由后执行）
1. 按目标子技能工作流执行推算/分析
2. 推算层任务 MUST 调用 `scripts/` 下的 Python 脚本获取准确结果
3. 病机/临床层任务 MUST 先获取推算结果，再结合 references 文档分析

### THEN（完成后执行）
1. 按 `docs-generator/` 格式输出结构化报告
2. 如涉及临床案例，按 `case-journal/_template.md` 沉淀医案
3. 所有临床输出 MUST 附加医学免责声明
4. **（P2-8 新增）任务完成后，主动邀请用户提供反馈：**
   - 在报告末尾附加反馈入口话术：
     > 本次分析是否对您有帮助？如您愿意，可回复评分（1-5）和简短建议，我将记录到自进化引擎以持续优化输出质量。
   - 如用户提供了评分/建议，调用 `python scripts/self_evolve.py feedback --session-id <会话ID> --rating <1-5> --comment "..."` 记录反馈
   - 每月自动生成月度报告：`python scripts/self_evolve.py monthly-report`

### ACT（行动约束）
- 推算层：MUST 调用脚本，MUST NOT 凭记忆推算干支运气
- 病机层：MUST 基于推算结果分析，MUST 参考对应 references
- 临床层：MUST 区分"运气理论分析"与"具体医疗建议"
- 文献层：MUST 标注出处（素问篇名/历代医家/现代文献）
- **引导层：MUST 在意图模糊时先询问，MUST NOT 直接输出完整报告**

## 模块总表

| 模块 | 目录 | 适用场景 |
|------|------|----------|
| 干支基础 | `ganzhi-basics/` | 天干地支推算、六十甲子、节气与运气关系 |
| 运气推算 | `yunqi-calc/` | 大运/主运/客运、司天/在泉/客气、客主加临、太过不及、天符岁会 |
| 病机分析 | `yunqi-pathogenesis/` | 五运病机、六气病机、太过不及病机、运气合病 |
| 临床应用 | `yunqi-clinical/` | 运气治则治法、方药选择、针灸选穴、养生调理 |
| 经典文献 | `yunqi-classics/` | 素问七篇大论、历代运气学说、现代研究文献 |
| 报告生成 | `docs-generator/` | 运气综合分析报告、医案报告 |
| 医案沉淀 | `case-journal/` | 运气应用医案记录、经验积累 |
| **统一计算接口** | `scripts/calculate_yunqi_api.py(.js)` | **大寒定年 + 日期输入 + 标准化JSON输出**（LLM Agent 外挂大脑） |
| **RAG 知识库** | `rag-knowledge-base/` | **岁运/司天在泉/客主加临病机 key-value 检索**（3 个 Asset JSON） |
| **ReAct 工作流** | `agent-workflow/` | **Agent 推理链路规范**（查工具→查知识库→辨证推理闭环） |
| **System Prompt** | `prompts/system_prompt.md` | **TCM 运气专家角色约束 + 输出规范 + 措辞约束** |
| **高级对齐** | `advanced-alignment/` + `scripts/weather_alignment.py` + `scripts/personal_yunqi_profile.py` | **天气 API 对齐 + 体质报告交叉分析**（内外邪相合） |
| **RAG 知识库 v2** | `rag-knowledge-base/asset4_formula.json` | **三因司天方 16 方**（运气专方 key→方药检索） |
| **RAG 知识库 v3** | `rag-knowledge-base/asset5_commentary.json` | **历代注家运气学说 20 条**（王冰→陆懋修 11 家核心理论） |
| **RAG 知识库 v4** | `rag-knowledge-base/asset6_regional.json` | **地域运气修正 8 区**（东北→青藏，纬度/海拔/地貌修正系数） |
| **RAG 知识库 v5** | `rag-knowledge-base/asset7_constitution.json` | **运气与体质交叉分析 18 条**（9 体质出生运气映射 + 9 岁运调理方案） |
| **自进化引擎** | `self-evolve/` + `scripts/self_evolve.py` | **使用日志→盲区检测→优化报告→持续迭代**（从使用中自学习） |
## 免责声明前置文件读取顺序

| 顺序 | 文件 | 用途 |
|------|------|------|
| 1 | `case-journal/precedent-disclaimer.md` | 医学免责声明（MUST 最先读取） |
| 2 | `routing.md` | 三轴路由匹配 |
| 3 | 目标子技能 `SKILL.md` | 进入具体工作流 |

## 脚本依赖速查

| 脚本 | 用途 | 调用方式 |
|------|------|----------|
| `ganzhi_calc.py` | 年份→天干地支 | `python scripts/ganzhi_calc.py <年份>` |
| `dayun_calc.py` | 大运+太过不及+天符岁会 | `python scripts/dayun_calc.py <年份>` |
| `keyun_calc.py` | 主运+客运五步 | `python scripts/keyun_calc.py <年份>` |
| `liuqi_calc.py` | 司天在泉+客气六步+主气六步 | `python scripts/liuqi_calc.py <年份>` |
| `kezhujialin.py` | 客主加临顺逆分析 | `python scripts/kezhujialin.py <年份>` |
| `yunqi_report.py` | 综合报告（调用以上全部） | `python scripts/yunqi_report.py <年份> --audience <student\|practitioner\|researcher>` |
| **`calculate_yunqi_api.py`** | **日期→完整运气JSON（大寒定年）** | **`python scripts/calculate_yunqi_api.py <YYYY-MM-DD> --json`** |
| **`calculate_yunqi_api.js`** | **JS版统一接口（需 lunar-javascript）** | **`node scripts/calculate_yunqi_api.js <YYYY-MM-DD> --json`** |
| **`weather_alignment.py`** | **天气实况→六气转译→运气天气对齐（Open-Meteo，可 --mock）** | **`python scripts/weather_alignment.py <YYYY-MM-DD> --city <城市> --json`** |
| **`ingest_literature.py`** | **文献注入管道**（txt→结构化RAG JSON） | **`python scripts/ingest_literature.py --source <文件> --category <分类> --output <目标>`** |
| **`self_evolve.py`** | **自进化引擎**（日志/盲区/反馈/报告） | **`python scripts/self_evolve.py <log|stats|feedback|report> <参数>`** |

所有脚本支持 `--json` 参数输出机器可读格式。

**大寒定年规则**：`calculate_yunqi_api` 以大寒节气为运气年界，而非公历1月1日。
例如 `2026-01-15` → 运气年 2025（乙巳），`2026-01-20`（大寒）→ 运气年 2026（丙午）。
输出包含 `rag_keys` 字段，可直接用于 RAG 知识库检索。

---

## ACTION REQUIRED

执行任何运气推算任务前，确认以下事项：

- [ ] 已读取 `precedent-disclaimer.md`（医学免责声明）
- [ ] 已通过 `routing.md` 完成路由匹配
- [ ] 推算任务已确认调用对应 Python 脚本
- [ ] 临床任务已确认附加免责声明

## 任务完成自检

- [ ] 推算结果已通过脚本验证（非凭记忆推算）
- [ ] 病机分析已引用对应 references 文档
- [ ] 临床建议已附加医学免责声明
- [ ] 报告格式符合 `docs-generator/` 规范
- [ ] 如为医案，已按 `case-journal/_template.md` 沉淀
