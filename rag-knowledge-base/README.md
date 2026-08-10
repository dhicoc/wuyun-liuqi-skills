# RAG 知识库索引

本文档是 `rag-knowledge-base/` 的维护索引。知识库通过 `scripts/calculate_yunqi_api.py` 生成的 `rag_keys` 精确检索，为病机分析、报告生成、个人体质和高级对齐提供结构化资料。

## 字段级 Schema

各 RAG asset 的字段级 schema 位于：

```text
rag-knowledge-base/schemas/
```

| Asset | Schema |
|-------|--------|
| `asset1_suiyun.json` | `schemas/asset1_suiyun.schema.json` |
| `asset2_sitian_zaiquan.json` | `schemas/asset2_sitian_zaiquan.schema.json` |
| `asset3_kezhujialin.json` | `schemas/asset3_kezhujialin.schema.json` |
| `asset4_formula.json` | `schemas/asset4_formula.schema.json` |
| `asset5_commentary.json` | `schemas/asset5_commentary.schema.json` |
| `asset6_regional.json` | `schemas/asset6_regional.schema.json` |
| `asset7_constitution.json` | `schemas/asset7_constitution.schema.json` |
| `asset9_cases.json` | `schemas/asset9_cases.schema.json` |
| `asset10_suiyi_zhifa.json` | `schemas/asset10_suiyi_zhifa.schema.json` |
| `asset11_mingyi_cases.json` | `schemas/asset11_mingyi_cases.schema.json` |
| `asset12_xumingyi_cases.json` | `schemas/asset12_xumingyi_cases.schema.json` |
| `asset13_gujin_an_cases.json` | `schemas/asset13_gujin_an_cases.schema.json` |
| `asset14_dingganren_cases.json` | `schemas/asset14_dingganren_cases.schema.json` |
| `asset15_shanghan90_cases.json` | `schemas/asset15_shanghan90_cases.schema.json` |
| `asset16_ye_cases.json` | `schemas/asset16_ye_cases.schema.json` |
| `terminology.json` | `schemas/terminology.schema.json` |
| `index.json` | `schemas/index.schema.json` |

## 资产总览

| Asset | 文件 | 类型 | 主要用途 | 典型检索键 |
|-------|------|------|----------|------------|
| asset1 | `asset1_suiyun.json` | 岁运病机 | 五运太过/不及病机、症状、治则 | `water_excess`, `fire_deficient` |
| asset2 | `asset2_sitian_zaiquan.json` | 司天在泉 | 上下半年六气病机与治法 | `shaoyin_junhuo_sitian`, `yangming_zaojin_zaiquan` |
| asset3 | `asset3_kezhujialin.json` | 客主加临 | 六步主客气组合、顺逆、病机 | `zhu_shaoyang_ke_shaoyin` |
| asset4 | `asset4_formula.json` | 运气方 | 三因司天方、方药方向 | `water_excess` |
| asset5 | `asset5_commentary.json` | 历代注家 | 王冰、刘完素、张景岳等注家观点 | `related_yunqi_keys` |
| asset6 | `asset6_regional.json` | 地域修正 | 八大区域气候与体质倾向修正 | 地区名 / `region_id` |
| asset7 | `asset7_constitution.json` | 运气体质 | 出生年运气体质映射、岁运调理 | `fire_deficient` |
| asset9 | `asset9_cases.json` | 岁图医案 | 圣济总录六十甲子岁图医案（按 rag_key 检索） | `jiezi`, `bingyin` |
| asset10 | `asset10_suiyi_zhifa.json` | 岁宜治法 | 六气司天岁宜治法表 | 岁运 / 司天 |
| asset11 | `asset11_mingyi_cases.json` | 名医类案 | 明·江瓘，历代医案汇编 | `entry_id`, `category` |
| asset12 | `asset12_xumingyi_cases.json` | 续名医类案 | 清·魏之琇，续补名医案 | `entry_id`, `category` |
| asset13 | `asset13_gujin_an_cases.json` | 古今医案按 | 清·俞震，含"震按"辨证要点 | `entry_id`, `category` |
| asset14 | `asset14_dingganren_cases.json` | 丁甘仁医案 | 近代丁甘仁，临证实录 | `entry_id`, `category` |
| asset15 | `asset15_shanghan90_cases.json` | 伤寒九十论 | 宋·许叔微，伤寒经方医案 | `entry_id`, `category` |
| asset16 | `asset16_ye_cases.json` | 临证指南医案 | 清·叶桂，辨证精审含华岫云按语 | `entry_id`, `category` |
| asset17 | `asset17_wenyi_yunqi.json` | 运气瘟疫防治 | 清·刘奎《松峰说疫》卷六运气专篇：五运太过不及瘟疫侧重、六气司天民病、五郁治法、刚柔失守疫病专方 | `code`, `sitian_key`, `zaiquan_key`, `rag_key`, `ganzhi`, `category` |
| terminology | `terminology.json` | 术语库 | 学习解释、报告术语扩展 | term / pinyin / entry_id |

> asset11-16 六部历代名家医案库共 **901 条**临证真实医案，按 `entry_id` / `category` 可检索。

## 推荐检索顺序

```text
1. calculate_yunqi_api.py <date> --json
2. 读取 rag_keys.suiyun → asset1
3. 读取 rag_keys.sitian / rag_keys.zaiquan → asset2
4. 读取 rag_keys.current_step → asset3
5. 如需方药方向 → asset4
6. 如需注家观点 → asset5
7. 如用户提供地区 → asset6
8. 如用户提供出生日期或体质 → asset7
9. 如需教学解释 → terminology
10. 如需岁图医案 / 岁宜治法 / 历代名家临证医案 → asset9 / asset10 / asset11-16（按 `entry_id` 或 `category` 检索）
```

## 与脚本的关系

- `scripts/calculate_yunqi_api.py`：生成标准化 `rag_keys`。
- `scripts/demo_full_chain.py`：演示推算到 RAG 检索的完整链路。
- `scripts/validate_knowledge_base.py`：校验资产结构。
- `scripts/ingest_literature.py`：注入新文献或新增条目。

## 维护规则

1. 新增条目必须包含至少一个可检索键：`key` / `code` / `rag_key` / `sitian_key` / `zaiquan_key` / `constitution_code` / `region_id`。
2. 新增或修改资产后运行：

   ```bash
   python scripts/validate_knowledge_base.py
   python tests/full_regression_test.py
   ```

3. 涉及临床、方药、针灸的条目必须保留“仅供参考，须辨证论治”的安全边界。
4. 若新增资产文件，请同步更新本 README 与 `index.json`。
