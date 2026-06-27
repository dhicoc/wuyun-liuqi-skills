# 五运六气知识库文献注入指南

> 本文档说明如何将更多文献资料注入技能包，使其持续进化。
> 所有文献注入统一通过 `scripts/ingest_literature.py` 完成。

---

## 快速开始

把原始文献文本放到 `raw-texts/` 目录，执行：

```bash
# 批量注入目录下所有文献
python scripts/ingest_literature.py --batch ./raw-texts/ --output-dir rag-knowledge-base/
```

---

## 推荐注入的文献（按优先级排序）

### 第一优先：三因司天方（运气方剂）

这是最有临床价值的补充。《三因司天方》由宋·陈无择创立，根据运气格局预设 16 首专方。

推荐格式（raw-texts/formula__sanyin_sitianfang.txt）：

```
## 甲己岁 土运 备化汤
来源: 三因极一病证方论
主治: 土运不及（甲己年）——胸胁满、寒湿泄、腹胀
组成: 附子、白术、茯苓、陈皮、甘草、干姜、泽泻、桂心、牛膝
用法: 水煎服，不拘时服

## 乙庚岁 金运 审平汤
来源: 三因极一病证方论
主治: 金运太过（乙庚年）
组成: 天冬、山茱萸、白芍、甘草、紫菀、生姜、桂枝、人参
...
```

注入后生成 `asset4_formula.json`，RLH 检索时可按 rag_key 命中对应的运气方。

### 第二优先：历代医家运气专著

| 典籍 | 作者 | 朝代 | 核心贡献 | 建议 asset 分类 |
|------|------|------|----------|---------------|
| 《素问》王冰注 | 王冰 | 唐 | 七篇大论次注，首次系统整理运气学说 | `commentary` |
| 《素问玄机原病式》 | 刘完素 | 金 | "六气皆从火化"，将运气病机与火热论统一 | `commentary` |
| 《运气易览》 | 汪石山 | 明 | 运气推算图解化，平气判断详细规则 | `commentary` |
| 《类经图翼·运气》 | 张景岳 | 明 | 运气推算集大成，附图表 78 幅 | `commentary` |
| 《医宗金鉴·运气要诀》 | 吴谦 | 清 | 运气口诀化，便于记忆与应用 | `commentary` |
| 《三因司天方》缪问释 | 缪问 | 清 | 司天方详细方解与临床加减 | `both formula + commentary` |

### 第三优先：现代临床研究文献（近 40 年）

这是提升 Agent 回答信服力的关键。推荐关注：

1. **运气与传染病**：顾植山团队对 SARS、H1N1、COVID-19 的运气分析
2. **运气与气象医学**：运气年与实际气象数据的对照验证
3. **运气与体质**：不同出生年月人群的体质与疾病易感性研究
4. **运气临床案例**：按运气辨证论治的真实医案

推荐格式（raw-texts/clinical__vanguard_studies.txt）：

```
## 顾植山：SARS与2003年运气分析
来源: 中国中医基础医学杂志, 2004
样本量: 回顾性分析
主要发现: 2003年癸未年，太阴湿土司天，与SARS的湿毒瘀闭病机高度吻合
运气模式: taiyin_shitu_sitian  |  earth_deficient

## 2020年COVID-19运气分析
来源: 多中心研究, 2020-2021
样本量: 回顾性流行病学分析
主要发现: 庚子年金运太过+少阴君火司天，金火相争，肺热叶焦
运气模式: metal_excess + shaoyin_junhuo_sitian
...
```

注入后生成 `asset5_clinical.json`，Agent 回答时可以引用现代研究作为佐证。

### 第四优先：地域修正数据表

中国地域横跨寒温热三带，同一运气格局在不同地区表现截然不同。

推荐注入格式示例：

```
## 东北地区（高纬度）修正
纬度范围: 42°N - 53°N
特点: 冬季漫长，寒气偏盛
修正: 客气影响权重 +15%，主气影响权重 -15%
适用: 黑龙江、吉林、辽宁

## 华南地区（低纬度）修正
纬度范围: 20°N - 25°N
特点: 全年温暖，湿气偏盛
修正: 湿气相关病机权重 +20%，寒气病机权重 -20%
适用: 广东、广西、海南
...
```

注入后生成 `asset6_regional.json`，可在 `advanced-alignment/` 层引用。

---

## Agent 端如何利用新增文献

### 方式一：ReAct 工作流自动调用

RAG 检索逻辑会自动匹配新 asset：

```
calculate_yunqi_api("2026-06-27")
  → { rag_keys: ["water_excess", "shaoyin_junhuo_sitian", ...] }
  → 检索 asset1-6 所有 entries
  → 遇 matching key 的病机、方剂、临床证据一并返回
```

### 方式二：System Prompt 引用权重

在 `prompts/system_prompt.md` 中加入新文献源的角色指令：

```
## 可参考的文献源（按优先级）
1. 素问七篇大论（经典，最高权威）
2. 三因司天方（方剂，临床可用）
3. 历代运气注家（刘完素、张景岳等，拓展视角）
4. 现代运气临床研究（近40年，佐证参考）
```

### 方式三：Weather + Constitution 对齐增强

地域修正数据可连接到 `advanced-alignment/weather_integration.md`：

```
输入城市 → 获取天气 → 地域修正系数 → 运气分析
                        ↑
                   asset6_regional.json
```

---

## 文献注入规范

### 文件命名约定

```
{category}__{descriptive_name}.{txt|md|json}
```

- `formula__sanyin_sitianfang.txt`
- `commentary__liuwanSu_wenyi.txt`
- `clinical__COVID_studies.txt`
- `regional__china_zones.txt`

### 原始文本格式建议

管道支持三种输入格式：

1. **Markdown 分段**（推荐）— 用 `## 标题` 分隔，每段一个条目
2. **键值对** — 每行 `字段名: 值`，空行分隔条目
3. **JSON** — 完全预结构的 JSON 数组

优先使用 Markdown 格式——LLM 最容易生成，人也最容易阅读和校对。

### 注入后必做

```bash
# 1. 验证 JSON 合法性
python -c "import json; json.load(open('rag-knowledge-base/asset4_formula.json'))" && echo ✓

# 2. 验证键值关联
python -c "
import json
d = json.load(open('rag-knowledge-base/asset4_formula.json'))
keys = [e.get('rag_key','') for e in d['entries']]
print(f'条目数: {len(d[\"entries\"])}  有 rag_key: {sum(1 for k in keys if k)}')
"

# 3. 验证与推算引擎的关联
python scripts/calculate_yunqi_api.py 2026-06-27 --json | python -c "import sys,json; d=json.load(sys.stdin); print('rag_keys:', d['rag_keys'])"
```

---

## 技能包更新检查清单

每注入一批新文献后：

- [ ] 新 asset JSON 已放入 `rag-knowledge-base/`
- [ ] `SKILL.md` 模块总表已添加新行
- [ ] `routing.md` 已添加对应的路由
- [ ] `prompts/system_prompt.md` 已更新文献源说明
- [ ] 所有 JSON 经 `python -c "json.load(...)"` 验证
- [ ] 端到端测试通过：输入日期→推算→RAG检索→输出完整
