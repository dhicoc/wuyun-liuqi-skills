# WuYun-LiuQi Skills — AI Agent Bootstrap

> **这是 AI Agent 的配置引导文件。如果你是 AI Agent，严格按以下流程执行。**

## 0. 安装与核心执行流程

> **AI Agent 请严格按以下流程执行。人类用户可参考「安装说明」手动操作。**

---

### 0.1 安装说明（人类用户手动安装用）

============================================
  五运六气 AI Agent 技能包 — 环境配置
============================================

[1/4] 检测 Python...
  ✓ Python: Python 3.13.7
[2/4] 安装 Python 依赖 (lunar-python)...
  ✓ lunar-python 已安装
[3/4] 创建自进化运行时目录...
  ✓ 目录已就绪
[4/4] 检测 Node.js (可选)...
  ✓ Node.js: v24.12.0
  → 如需使用 JS 版, 运行: npm install

============================================
  ✅ 环境配置完成!
============================================

快速试用:
  python scripts/calculate_yunqi_api.py 2026-06-27
  python scripts/demo_full_chain.py 2004-07-30
  python scripts/verify_expansion.py

更多用法见 README.md
============================================================
1. ´󺮱߽ç»عé²âÊÔ
============================================================

  ÊäÈë: 2026-01-15
  [OK] yunqi_year=2025
  [OK] year_gz=ÒÒËÈ
  [OK] sui_yun.code=metal_deficient
  [OK] day_gz ´æÔÚ
  [OK] si_tian ´æÔÚ
  [OK] zai_quan ´æÔÚ
  [OK] current_step.name ´æÔÚ
  [OK] rag_keys º¬ 4 ¸ö·ÖÀà

  ÊäÈë: 2026-01-20
  [OK] yunqi_year=2026
  [OK] year_gz=±ûÎç
  [OK] sui_yun.code=water_excess
  [OK] day_gz ´æÔÚ
  [OK] si_tian ´æÔÚ
  [OK] zai_quan ´æÔÚ
  [OK] current_step.name ´æÔÚ
  [OK] rag_keys º¬ 4 ¸ö·ÖÀà

  ÊäÈë: 2026-06-27
  [OK] yunqi_year=2026
  [OK] year_gz=±ûÎç
  [OK] sui_yun.code=water_excess
  [OK] day_gz ´æÔÚ
  [OK] si_tian ´æÔÚ
  [OK] zai_quan ´æÔÚ
  [OK] current_step.name ´æÔÚ
  [OK] rag_keys º¬ 4 ¸ö·ÖÀà

============================================================
2. RAG Asset JSON ÍêÕûÐԼì²é
============================================================

  asset1_suiyun.json:
  [OK] ÌõĿÊý >= 10 (ʵ¼Ê: 10)
  [OK] ×ֶÎ 'code' ȫ²¿´æÔÚ
  [OK] ×ֶÎ 'name' ȫ²¿´æÔÚ
  [OK] ×ֶÎ 'treatment_principle' ȫ²¿´æÔÚ

  asset2_sitian_zaiquan.json:
  [OK] ÌõĿÊý >= 6 (ʵ¼Ê: 6)
  [OK] ×ֶÎ 'sitian_key' ȫ²¿´æÔÚ
  [OK] ×ֶÎ 'zaiquan_key' ȫ²¿´æÔÚ

  asset3_kezhujialin.json:
  [OK] ÌõĿÊý >= 36 (ʵ¼Ê: 36)
  [OK] ×ֶÎ 'key' ȫ²¿´æÔÚ
  [OK] ×ֶÎ 'shun_ni' ȫ²¿´æÔÚ

  asset4_formula.json:
  [OK] ÌõĿÊý >= 16 (ʵ¼Ê: 16)
  [OK] ×ֶÎ 'formula_id' ȫ²¿´æÔÚ
  [OK] ×ֶÎ 'rag_key' ȫ²¿´æÔÚ
  [OK] ×ֶÎ 'name' ȫ²¿´æÔÚ
  [OK] ×ֶÎ 'ingredients' ȫ²¿´æÔÚ

  asset5_commentary.json:
  [OK] ÌõĿÊý >= 20 (ʵ¼Ê: 20)
  [OK] ×ֶÎ 'commentary_id' ȫ²¿´æÔÚ
  [OK] ×ֶÎ 'author' ȫ²¿´æÔÚ
  [OK] ×ֶÎ 'core_theory_title' ȫ²¿´æÔÚ

  asset6_regional.json:
  [OK] ÌõĿÊý >= 8 (ʵ¼Ê: 8)
  [OK] ×ֶÎ 'region_id' ȫ²¿´æÔÚ
  [OK] ×ֶÎ 'region_name' ȫ²¿´æÔÚ
  [OK] ×ֶÎ 'wuyun_modifier' ȫ²¿´æÔÚ

  asset7_constitution.json:
  [OK] ×ÜÌõĿ >= 18 (ʵ¼Ê: 18)
  [OK] birth_yunqi_mapping 9 Ìõ (ʵ¼Ê: 9)
  [OK] suiyun_constitution_adjustment 9 Ìõ (ʵ¼Ê: 9)
  [OK] birth º¬ constitution_name
  [OK] adj º¬ suiyun_code+suiyun_name

============================================================
3. Cross-Asset Key ¹ØÁªÐԼì²é
============================================================

  RAG ֪ʶ¿â×ÜΨһ¼üÊý: 104
  [OK] API rag_key values ¿ɱ» RAG asset ÃüÖÐ (4/4)
    API values: {'shaoyin_junhuo_sitian', 'zhu_shaoyang_ke_shaoyin', 'water_excess', 'yangming_zaojin_zaiquan'}
    ÒÑƥÅä: {'shaoyin_junhuo_sitian', 'water_excess', 'zhu_shaoyang_ke_shaoyin', 'yangming_zaojin_zaiquan'}

============================================================
4. ×Խø»¯ÒýÇæÆô¶¯¼ì²é
============================================================
  [OK] self_evolve.py log ³ɹ¦



---

### 0.2 AI Agent 自动安装与配置（AI 读完本文件后立即执行）

> **AI Agent 执行以下流程，用户无需手动操作。**

```text
0. 检测本包实际路径：由当前文件所在目录推导，记为 <SKILL_ROOT>
1. 检测操作系统：
   - Windows → 执行 scripts/setup.bat
   - Linux/macOS → 执行 bash scripts/setup.sh
2. 验证包结构完整性：
   - 必须存在：SKILL.md, routing.md, RULES.md
   - 必须存在：scripts/calculate_yunqi_api.py
   - 必须存在：rag-knowledge-base/ 目录及至少 5 个 asset 文件
3. 运行 setup 脚本后，确认依赖就绪（Python 3.8+ / lunar-python）
4. 读取 SKILL.md → 理解三轴路由（时间维度 + 用户意图 + 知识层级）
5. 读取 routing.md → 匹配用户任务到对应子技能
6. 读取 RULES.md → 执行行为规则链
7. 开始执行任务
```

## 1. 三轴路由矩阵

| 维度 | 分类 | 说明 |
|------|------|------|
| 时间维度 | 年份推算 / 日期推算 / 节气推算 | 决定推算精度 |
| 用户意图 | 学习推算 / 临床参考 / 文献检索 | 决定输出详细程度和报告风格 |
| 知识层级 | 基础推算 / 病机分析 / 临床应用 | 决定 RAG 知识库检索深度 |

### 路由决策逻辑

```
if 用户只需干支/大运/六气数值 → scripts/中单项推算脚本 + --json 输出
elif 用户需要临床分析 → calculate_yunqi_api.py → RAG 五层检索 → ReAct 推理 → 结构化报告
elif 用户需要学习讲解 → yunqi_report.py --audience student/practitioner/researcher
elif 用户询问经典文献 → 直接引用 rag-knowledge-base/ 对应条目 + 素问七篇大论
else → 全链路 demo_full_chain.py 演示
```

## 2. 推算引擎调用

### 统一计算接口（Agent 首选入口）

```python
# Python 版（推荐）
python scripts/calculate_yunqi_api.py <日期> --json

# 示例
python scripts/calculate_yunqi_api.py 2026-06-27 --json
```

输出格式：
```json
{
  "year": 2026,
  "ganzhi_year": "丙午",
  "dayun": "水运太过",
  "sitian": "少阳相火",
  "zaiquan": "厥阴风木",
  "keqi": ["厥阴风木","少阴君火","太阴湿土","少阳相火","阳明燥金","太阳寒水"],
  "rag_keys": ["fire_excess","shaoyang_xianghuo_sitian","jueyin_fengmu_zaiquan"]
}
```

### 单项推算

| 场景 | 命令 |
|------|------|
| 干支推算 | `python scripts/ganzhi_calc.py 2026` |
| 大运太过不及 | `python scripts/dayun_calc.py 2026` |
| 主运客运 | `python scripts/keyun_calc.py 2026` |
| 六气推算 | `python scripts/liuqi_calc.py 2026` |
| 客主加临 | `python scripts/kezhujialin.py 2026` |
| 综合报告 | `python scripts/yunqi_report.py 2026 --audience student` |

## 3. RAG 知识库（五层覆盖）

| 层 | Asset | 条目数 | 用途 | rag_key 示例 |
|----|-------|--------|------|-------------|
| 经典病机 | asset1-3 | 52 | 岁运/司天/客主加临病机 | `water_excess`, `shaoyin_junhuo_sitian` |
| 运气方剂 | asset4 | 16 | 三因司天方 | `formula_ma_hui` |
| 历代注家 | asset5 | 20 | 王冰→陆懋修 | `commentary_wangbing` |
| 地域修正 | asset6 | 8 | 气候区调整 | `region_south_china` |
| 运气体质 | asset7 | 18 | 体质×岁运 | `constitution_yin_deficiency` |

### 检索流程

```
1. calculate_yunqi_api.py 输出 rag_keys
2. 按顺序检索 asset1 → asset7
3. 每个 asset 用 rag_key 精确匹配 value
4. 将匹配到的知识传入 ReAct 工作流
```

## 4. ReAct 推理工作流

详细工作流规范见 [agent-workflow/react_workflow.md](agent-workflow/react_workflow.md)。

```
prompts/system_prompt.md → 加载 TCM 运气专家角色约束
  ↓
scripts/calculate_yunqi_api.py → 获取推算结果 + rag_keys
  ↓
rag-knowledge-base/ → 用 rag_keys 五层检索
  ↓
agent-workflow/react_workflow.md → 辨证推理循环
  ↓
advanced-alignment/ → (可选) 天气 API 对齐 + 体质交叉分析
  ↓
输出结构化报告 + 免责声明
  ↓
scripts/self_evolve.py → 自动记录本次推理
```

### System Prompt 约束

加载 [prompts/system_prompt.md](prompts/system_prompt.md) 后，AI 必须：
- 以 TCM 运气专家身份输出
- 禁止使用现代医学词汇（如"病毒""感染""抗生素"等）
- 使用传统中医六气病机措辞（如"火热""寒湿""风燥"等）
- 所有临床建议必须标注"仅供参考，具体诊疗须由执业中医师辨证论治"

## 5. 自进化引擎

每次推理完成后，自动调用：

```bash
# 自动记录本次推理
python scripts/self_evolve.py log --input <日期> --rag-keys <key1,key2> --source user_query

# 查看推理统计
python scripts/self_evolve.py stats

# 检测知识盲区
python scripts/self_evolve.py analyze

# 生成优化报告
python scripts/self_evolve.py report
```

## 6. 关键入口文件

| 文件 | 用途 |
|------|------|
| [SKILL.md](SKILL.md) | 总控入口 + 路由执行契约 |
| [routing.md](routing.md) | 三轴路由矩阵 |
| [RULES.md](RULES.md) | 行为规则链 |
| [agent-workflow/react_workflow.md](agent-workflow/react_workflow.md) | ReAct 推理工作流 |
| [prompts/system_prompt.md](prompts/system_prompt.md) | TCM 运气专家角色约束 |
| [scripts/calculate_yunqi_api.py](scripts/calculate_yunqi_api.py) | ★ 统一计算接口 |
| [scripts/self_evolve.py](scripts/self_evolve.py) | ★ 自进化引擎 |
| [scripts/verify_expansion.py](scripts/verify_expansion.py) | 67 项端到端验证 |
| [rag-knowledge-base/](rag-knowledge-base/) | 五层 RAG 知识库 |
| [case-journal/](case-journal/) | 医案沉淀系统 |

## 7. 故障处理

### 依赖缺失降级

| 缺失组件 | 降级行为 |
|---------|---------|
| lunar-python | 使用近似节气表（大寒=1月20日），精度降级但功能完整 |
| lunar-javascript | 同上，使用 JS 近似表 |
| Python 3.8+ | 降级为纯手动查表模式，提示用户安装 Python |
| Node.js | Python 版不受影响，JS 版不可用 |

### 大寒定年边界

```text
2026-01-15 → 运气年 2025(乙巳)
2026-01-20 → 运气年 2026(丙午)
2027-01-19 → 运气年 2026(丙午)  — 次年 1 月可能仍在上一年运气年
2027-01-20 → 运气年 2027(丁未)
```

关键规则：运气年以大寒节气为界，大寒前属上一年，大寒后属本年。

## 8. 输出规范

### Agent 结构化报告

```markdown
## 五运六气分析报告

**输入日期**: [日期] / **运气年**: [干支年]

### 1. 岁运
- [天干]年 → [五运] [太过/不及]
- 气候特征：[描述]
- 病机要点：[描述]

### 2. 司天在泉
- 司天：[六气] — [病机] — [治法]
- 在泉：[六气] — [病机] — [治法]

### 3. 客气六步
- 初之气：[六气] — [气候] — [病机]
- 二之气：[六气] — [气候] — [病机]
- ...（至六之气）

### 4. 客主加临
[顺逆分析]

### 5. 运气方剂参考
[推荐方剂 + 组成 + 加减]

### 6. 养生建议
[饮食/作息/穴位]

*免责声明：运气学说为中医传统理论，非现代医学诊断标准。*
```

### 语言要求

- 禁止现代医学术语（病毒、感染、抗生素等需替换为六气病机描述）
- 所有临床建议后附加医疗免责声明
- 输出 JSON 格式时，使用标准化键名（dayun, sitian, zaiquan, keqi, rag_keys 等）

---

> **执行完成后，如发现推理流程缺陷或知识盲区，自动记录到 self-evolve/ 或 case-journal/。**
