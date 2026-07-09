# -*- coding: utf-8 -*-
"""
五运六气可导入 API（渐进包骨架）

不搬迁 scripts/ 实现，仅通过 bootstrap 暴露稳定 import 面：

  from wuyun_liuqi import calculate, search, lookup_key, fetch_by_date
  from wuyun_liuqi import calculate_yunqi_api  # 别名

在仓库根目录执行:
  python -c "from wuyun_liuqi import calculate; print(calculate('today')['year_gz'])"
  python -m wuyun_liuqi calc today --summary

完整 CLI 仍推荐:
  python scripts/yunqi_cli.py ...
"""
from __future__ import annotations

from wuyun_liuqi.core import calculate, calculate_yunqi_api, resolve_date
from wuyun_liuqi.rag import search, lookup_key, fetch_by_date, semantic_search

__version__ = "0.1.0"
__all__ = [
    "__version__",
    "calculate",
    "calculate_yunqi_api",
    "resolve_date",
    "search",
    "lookup_key",
    "fetch_by_date",
    "semantic_search",
]
