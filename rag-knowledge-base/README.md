# RAG 知识库 (rag-knowledge-base)

> 五运六气 AI Agent 技能包的检索增强生成（RAG）知识库。
> 所有医学内容基于《黄帝内经·素问》七篇大论，使用中医传统术语。

## 知识库概览

本知识库包含三个结构化 JSON 数据资产，覆盖五运六气病机分析的三个层面：

| 资产 | 文件 | 条目数 | 覆盖范围 | 数据来源 |
|------|------|--------|----------|----------|
| asset1 | `asset1_suiyun.json` | 10 | 五运太过不及病机 | 素问·气交变大论、素问·五常政大论 |
| asset2 | `asset2_sitian_zaiquan.json` | 6（12半年节段） | 司天在泉病机与治法 | 素问·至真要大论 |
| asset3 | `asset3_kezhujialin.json` | 36 | 客主加临顺逆病机 | 素问·五运行大论、素问·至真要大论 |

## 与 LLM Agent 的配合使用

### 检索流程

```
年份输入 → scripts/ 推算引擎 → 运气格局（code/key） → RAG 知识库检索 → 病机分析
```

具体步骤：

1. **岁运病机检索**：由 `dayun_calc.py` 获取大运太过不及结果，提取 `code`（如 `water_excess`），在 `asset1_suiyun.json` 的 `entries` 数组中按 `code` 字段匹配，获取病机、症状、治则、饮食调理。

2. **司天在泉病机检索**：由 `liuqi_calc.py` 获取司天在泉结果，提取 `sitian_key`（如 `shaoyin_junhuo_sitian`），在 `asset2_sitian_zaiquan.json` 的 `entries` 数组中按 `sitian_key` 字段匹配，获取上下半年病机、症状及治法。

3. **客主加临病机检索**：由 `kezhujialin.py` 获取六步客主加临结果，对每一步生成 `key`（如 `zhu_shaoyang_ke_taiyang`），在 `asset3_kezhujialin.json` 的 `entries` 数组中按 `key` 字段匹配，获取顺逆关系、病机分析、临床关注重点。

### Key 命名规则

| 资产 | Key 格式 | 示例 |
|------|----------|------|
| asset1 | `{element}_{excess/deficient}` | `water_excess`、`wood_deficient` |
| asset2 | `{pinyin}_sitian` | `shaoyin_junhuo_sitian`、`taiyang_hanshui_sitian` |
| asset3 | `zhu_{zhu_pinyin}_ke_{ke_pinyin}` | `zhu_shaoyang_ke_taiyang`、`zhu_jueyin_ke_yangming` |

### Pinyin 映射表

| 六气 | Pinyin |
|------|--------|
| 厥阴风木 | jueyin |
| 少阴君火 | shaoyin |
| 太阴湿土 | taiyin |
| 少阳相火 | shaoyang |
| 阳明燥金 | yangming |
| 太阳寒水 | taiyang |

## 各资产结构说明

### asset1_suiyun.json — 岁运病机数据库

10 个条目，对应五运（木火土金水）各有太过与不及两种状态。

每个条目包含：

| 字段 | 说明 | 示例 |
|------|------|------|
| `code` | 岁运代码 | `water_excess` |
| `name` | 中文名称 | `水运太过` |
| `tiangan` | 对应天干 | `丙` |
| `tiangan_yinyang` | 天干阴阳 | `阳干` |
| `wuxing` | 五行 | `水` |
| `pathogenesis` | 病机描述（含内经原文引用） | — |
| `classics_quote` | 经典原文引用 | — |
| `organs_affected` | 受累脏腑列表 | — |
| `symptoms` | 主要症状列表（中医术语） | — |
| `sheng_fu` | 胜复规律 | `{sheng: ..., fu: ...}` |
| `treatment_principle` | 治则 | — |
| `dietary_advice` | 饮食调理 | — |
| `pingqi_condition` | 平气条件 | — |

### asset2_sitian_zaiquan.json — 司天在泉病机数据库

6 个条目，对应 6 组司天在泉配对，每组涵盖上下半年（共 12 个半年节段）。

每个条目包含：

| 字段 | 说明 | 示例 |
|------|------|------|
| `sitian` | 司天六气 | `少阴君火` |
| `zaiquan` | 在泉六气 | `阳明燥金` |
| `sitian_key` | 司天检索键 | `shaoyin_junhuo_sitian` |
| `zaiquan_key` | 在泉检索键 | `yangming_zaojin_zaiquan` |
| `sitian_pathogenesis` | 司天病机（上半年） | — |
| `sitian_symptoms` | 司天症状（上半年） | — |
| `zaiquan_pathogenesis` | 在泉病机（下半年） | — |
| `zaiquan_symptoms` | 在泉症状（下半年） | — |
| `treatment_rule` | 治法（含上下半年） | — |

### asset3_kezhujialin.json — 客主加临病机库

36 个条目，对应 6 主气 × 6 客气的全部组合。

每个条目包含：

| 字段 | 说明 | 示例 |
|------|------|------|
| `key` | 检索键 | `zhu_shaoyang_ke_taiyang` |
| `zhu_qi` | 主气 | `少阳相火` |
| `ke_qi` | 客气 | `太阳寒水` |
| `zhu_step` | 主气步次（含节气） | `三之气（小满~大暑）` |
| `zhu_wuxing` | 主气五行 | `火` |
| `ke_wuxing` | 客气五行 | `水` |
| `relation` | 五行关系 | `客气克主气（水克火）` |
| `shun_ni` | 顺逆判断 | `不相得（逆，最逆）` |
| `pathogenesis` | 病机分析 | — |
| `clinical_focus` | 临床关注重点 | — |

顺逆统计：相得（顺）15 种，不相得（逆）21 种。其中客气克主气（7 种）为最逆。

## 数据来源

所有医学内容均出自《黄帝内经·素问》以下篇章：

- **素问·气交变大论篇第六十九**：五运太过不及之气候、病机、症状
- **素问·五常政大论篇第七十**：五运平气、太过、不及之政令变化
- **素问·至真要大论篇第七十四**：六气司天在泉病机、六气淫胜治法、客主加临顺逆
- **素问·五运行大论篇第六十七**：五运六气运行规律

## 免责声明

> 运气学说为中医传统理论，非现代医学诊断标准。
> 本知识库所有内容仅供学术研究与传统医学学习参考，不构成任何医疗诊断或治疗建议。
> 具体诊疗须由执业中医师辨证论治，切勿据此自行用药或替代专业医疗服务。
