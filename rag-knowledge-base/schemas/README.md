# RAG Asset 字段级 Schema

本目录存放 `rag-knowledge-base/` 各 JSON 资产的字段级 JSON Schema，用于说明字段含义、必填字段、嵌套结构与维护约束。

## Schema 列表

| Asset | Schema | 说明 |
|-------|--------|------|
| `asset1_suiyun.json` | `asset1_suiyun.schema.json` | 岁运病机数据库 |
| `asset2_sitian_zaiquan.json` | `asset2_sitian_zaiquan.schema.json` | 司天在泉病机数据库 |
| `asset3_kezhujialin.json` | `asset3_kezhujialin.schema.json` | 客主加临病机库 |
| `asset4_formula.json` | `asset4_formula.schema.json` | 三因司天方 / 运气方剂 |
| `asset5_commentary.json` | `asset5_commentary.schema.json` | 历代注家观点 |
| `asset6_regional.json` | `asset6_regional.schema.json` | 地域运气修正 |
| `asset7_constitution.json` | `asset7_constitution.schema.json` | 运气与体质交叉分析 |
| `terminology.json` | `terminology.schema.json` | 术语解释库 |
| `index.json` | `index.schema.json` | RAG 资产索引 |

## 使用说明

当前项目的 `scripts/validate_knowledge_base.py` 会进行轻量结构校验和索引一致性校验；本目录 schema 用于字段级说明与后续扩展。若后续引入 `jsonschema` 依赖，可进一步执行严格 JSON Schema 校验。

维护建议：

1. 新增或修改 asset 字段时，同步更新对应 schema。
2. 新增 asset 文件时，同时新增 schema，并更新 `scripts/generate_rag_index.py` 的分类映射。
3. 修改 asset 后运行：

```bash
python scripts/generate_rag_index.py
python scripts/generate_rag_index.py --check
python scripts/validate_knowledge_base.py
python scripts/full_regression_test.py
```
