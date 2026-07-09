#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轻量「语义」检索（无外部 embedding / 无向量库）

方法：
- 将知识库条目文本切为字符 bigram + unigram
- 用 TF 加权后的余弦相似度排序
- 适合中医运气口语化提问（如「心火偏旺怎么办」「像中风前兆」）

不依赖 numpy；纯标准库。结果是近似语义，**精确推算仍用 --key / --date**。

用法:
  python scripts/rag_semantic.py 心火偏旺
  python scripts/rag_semantic.py 气候干燥 皮肤 咳嗽 --limit 5
  python scripts/rag_semantic.py 天人相应 --json
  python scripts/rag_search.py --semantic 心火偏旺
"""
from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from typing import Any, Dict, List, Optional, Sequence, Tuple

from _common import setup_environment, add_scripts_dir_to_path

setup_environment(add_lib=False)
add_scripts_dir_to_path()

import rag_search as rs  # noqa: E402

# 简单停用/噪声字符
_NOISE = set(" \t\n\r　，。、；：！？,.!?;:\"'（）()【】[]《》<>·—-…的了是在与及和或等")
_CACHE: Optional[List[Dict[str, Any]]] = None


def _tokenize(text: str) -> List[str]:
    """中文友好：unigram + bigram 字符特征。"""
    if not text:
        return []
    # 去掉过长空白
    s = re.sub(r"\s+", "", text)
    chars = [c for c in s if c not in _NOISE and not c.isdigit()]
    grams: List[str] = []
    for c in chars:
        grams.append(c)
    for i in range(len(chars) - 1):
        grams.append(chars[i] + chars[i + 1])
    return grams


def _tf(tokens: Sequence[str]) -> Dict[str, float]:
    if not tokens:
        return {}
    cnt = Counter(tokens)
    n = float(len(tokens))
    # sublinear tf
    return {t: 1.0 + math.log(c) for t, c in cnt.items()}


def _cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    # dot
    if len(a) > len(b):
        a, b = b, a
    dot = 0.0
    for k, v in a.items():
        if k in b:
            dot += v * b[k]
    if dot <= 0:
        return 0.0
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na <= 0 or nb <= 0:
        return 0.0
    return dot / (na * nb)


def _entry_document(entry: Dict[str, Any]) -> str:
    parts: List[str] = []
    for key in (
        "name", "term", "title", "code", "key", "rag_key",
        "pathogenesis", "explanation", "classics_quote", "description",
        "treatment_principle", "clinical_focus", "symptoms",
        "sitian", "zaiquan", "dietary_advice",
    ):
        val = entry.get(key)
        if isinstance(val, str) and val.strip():
            parts.append(val)
        elif isinstance(val, list):
            parts.extend(str(x) for x in val if x)
    # 兜底：整条扁平
    if len(parts) < 2:
        for _, v in rs._flatten_strings(entry):
            if isinstance(v, str) and len(v) > 4:
                parts.append(v)
    return "\n".join(parts)


def build_index(assets: Optional[Sequence[str]] = None) -> List[Dict[str, Any]]:
    """构建内存索引（带向量）。"""
    global _CACHE
    keys = list(assets) if assets else rs._default_asset_keys()
    docs: List[Dict[str, Any]] = []
    for ak in keys:
        try:
            fname, entries = rs.load_entries(ak)
        except FileNotFoundError:
            continue
        for i, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue
            text = _entry_document(entry)
            if len(text) < 8:
                continue
            tokens = _tokenize(text)
            vec = _tf(tokens)
            eid = rs._entry_id(entry, i)
            docs.append({
                "asset": ak,
                "file": fname,
                "id": eid,
                "title": rs._entry_title(entry, eid),
                "text": text,
                "vec": vec,
                "entry": entry,
            })
    _CACHE = docs
    return docs


def get_index(force: bool = False) -> List[Dict[str, Any]]:
    global _CACHE
    if _CACHE is None or force:
        return build_index()
    return _CACHE


def semantic_search(
    query: str,
    limit: int = 8,
    min_score: float = 0.02,
    assets: Optional[Sequence[str]] = None,
    full: bool = False,
) -> List[Dict[str, Any]]:
    """
    对口语查询做轻量相似度检索。
    返回结构与 rag_search.search 兼容，mode=semantic。
    """
    q = (query or "").strip()
    if not q:
        return []
    q_vec = _tf(_tokenize(q))
    if not q_vec:
        return []

    if assets:
        index = build_index(assets)
    else:
        index = get_index()

    scored: List[Tuple[float, Dict[str, Any]]] = []
    for doc in index:
        sc = _cosine(q_vec, doc["vec"])
        if sc >= min_score:
            scored.append((sc, doc))
    scored.sort(key=lambda x: -x[0])

    hits: List[Dict[str, Any]] = []
    for sc, doc in scored[:limit]:
        preview = doc["text"].replace("\n", " ").strip()
        if len(preview) > 180:
            preview = preview[:180] + "…"
        hit: Dict[str, Any] = {
            "score": round(sc, 4),
            "asset": doc["asset"],
            "file": doc["file"],
            "id": doc["id"],
            "title": doc["title"],
            "matched_fields": ["semantic"],
            "preview": preview,
            "mode": "semantic",
            "query": q,
        }
        if full:
            hit["entry"] = doc["entry"]
        hits.append(hit)
    return hits


def format_text(hits: List[Dict[str, Any]], query: str) -> str:
    lines = [
        f"语义检索（轻量）: {query}",
        f"命中: {len(hits)} 条（字符 n-gram 余弦，非外部 embedding）",
        "",
    ]
    if not hits:
        lines.append("（无结果。可换口语说法，或改用关键词 / --key 精确直取）")
        return "\n".join(lines)
    for i, h in enumerate(hits, 1):
        lines.append(f"{i}. [{h['score']:.3f}] {h['title']}  ({h['asset']} / {h['id']})")
        lines.append(f"   摘要: {h['preview']}")
        lines.append("")
    lines.append("提示: 精确推算请用 `rag_search --date today`；本模式适合模糊口语。")
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="轻量语义检索（字符 n-gram）")
    parser.add_argument("query", nargs="+", help="口语查询（可多词拼成一句）")
    parser.add_argument("--limit", type=int, default=8)
    parser.add_argument("--min-score", type=float, default=0.02)
    parser.add_argument("--asset", action="append", dest="assets")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--rebuild", action="store_true", help="强制重建索引")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.rebuild:
        build_index(args.assets)
    query = " ".join(args.query)
    hits = semantic_search(
        query,
        limit=args.limit,
        min_score=args.min_score,
        assets=args.assets,
        full=args.full,
    )
    if args.json:
        print(json.dumps({
            "query": query,
            "count": len(hits),
            "mode": "semantic",
            "hits": hits,
        }, ensure_ascii=False, indent=2))
    else:
        print(format_text(hits, query))
    return 0 if hits else 1


if __name__ == "__main__":
    raise SystemExit(main())
