# RAG 知识库索引

本文档是 `rag-knowledge-base/` 的维护索引。知识库通过 `scripts/calculate_yunqi_api.py` 生成的 `rag_keys` 精确检索，为病机分析、报告生成、个人体质和高级对齐提供结构化资料。

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
| terminology | `terminology.json` | 术语库 | 学习解释、报告术语扩展 | term / pinyin / entry_id |

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
   python scripts/full_regression_test.py
   ```

3. 涉及临床、方药、针灸的条目必须保留“仅供参考，须辨证论治”的安全边界。
4. 若新增资产文件，请同步更新本 README 与 `index.json`。
