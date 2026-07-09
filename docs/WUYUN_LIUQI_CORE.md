# 独立包 wuyun-liuqi-core 说明

> **位置（与本技能包并列，不在本目录内）**  
> `D:\HuaweiMoveData\Users\DELL\Desktop\claude\wuyun-liuqi-core`  
> 或相对：`../wuyun-liuqi-core`

## 是什么

把技能包 `scripts/` 里的**推算 / RAG / 报告**迁成正规 Python 包结构，单独一个工程文件夹维护。

本技能包（`wuyun-liuqi-skills`）**不删不改主链路**，继续：

```bash
python scripts/calculate_yunqi_api.py today --summary
```

新工程面向：

```python
from wuyun_liuqi import calculate, fetch_by_date
```

```bash
cd ../wuyun-liuqi-core
pip install -e ".[lunar]"
wuyun-liuqi calc today --summary
```

## 结构对照

| 技能包 scripts | core 包 |
|----------------|---------|
| `lib/yunqi_data.py` | `wuyun_liuqi/core/data.py` |
| `calculate_yunqi_api.py` | `wuyun_liuqi/core/calculate.py` |
| `rag_search.py` | `wuyun_liuqi/rag/search.py` |
| `rag_semantic.py` | `wuyun_liuqi/rag/semantic.py` |
| `yunqi_report.py` | `wuyun_liuqi/report/generator.py` |
| `rag-knowledge-base/` | `data/rag-knowledge-base/` |

## 测试

```bash
cd ../wuyun-liuqi-core
python tests/test_core.py
```

## 后续可选

- 技能包改为依赖 `wuyun-liuqi-core`（scripts 变薄 wrapper）
- HTML 报告 / 自进化仍留在技能包
