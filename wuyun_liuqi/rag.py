# -*- coding: utf-8 -*-
"""RAG 检索 API 薄封装。"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from wuyun_liuqi import _bootstrap  # noqa: F401

import rag_search as _rs  # type: ignore


def search(
    terms: Sequence[str],
    assets: Optional[Sequence[str]] = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """关键词 AND 检索。"""
    return _rs.search(terms, assets=assets, limit=limit)


def lookup_key(
    rag_key: str,
    assets: Optional[Sequence[str]] = None,
    full: bool = False,
) -> List[Dict[str, Any]]:
    """按 rag_key / code 精确直取。"""
    return _rs.lookup_key(rag_key, assets=assets, full=full)


def fetch_by_date(date_str: str = "today", full: bool = False) -> Dict[str, Any]:
    """日期 → rag_keys → 批量精确拉取（Agent 一键）。"""
    return _rs.fetch_by_date(date_str, full=full)


def semantic_search(
    query: str,
    limit: int = 8,
    min_score: float = 0.02,
    assets: Optional[Sequence[str]] = None,
    full: bool = False,
) -> List[Dict[str, Any]]:
    """轻量语义检索（字符 n-gram，无外部 embedding）。"""
    import rag_semantic as _sem  # type: ignore
    return _sem.semantic_search(
        query, limit=limit, min_score=min_score, assets=assets, full=full
    )
