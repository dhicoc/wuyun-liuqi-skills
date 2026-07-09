# -*- coding: utf-8 -*-
"""核心推算 API 薄封装。"""
from __future__ import annotations

from typing import Any, Dict, Optional, Union
from datetime import date

from wuyun_liuqi import _bootstrap  # noqa: F401  — path side-effect

from calculate_yunqi_api import (  # type: ignore
    calculate_yunqi_api as _calculate_yunqi_api,
    _resolve_date as _resolve_date_impl,
)


def resolve_date(date_input: Optional[Union[str, date]] = None) -> str:
    """规范化日期：today / 今天 / YYYY-MM-DD / None。"""
    return _resolve_date_impl(date_input)


def calculate(date_str: Optional[Union[str, date]] = None) -> Dict[str, Any]:
    """
    统一运气推算（大寒定年）。

    等价于 scripts/calculate_yunqi_api.calculate_yunqi_api。
    """
    return _calculate_yunqi_api(date_str)


# 公开别名，兼容旧名
calculate_yunqi_api = calculate
