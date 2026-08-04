#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地向量语义检索（bge-m3 via Ollama）—— 可选增强，非必需
=========================================================
⚠️ 本模块是【可选增强】，不是项目主链路。项目的主检索路径是：
  - 键值精确检索：rag_search.py --key <rag_key>（零依赖，Agent 主路径）
  - 关键词检索：  rag_search.py <关键词>（零依赖）
  - 直接阅读：    rag-knowledge-base/sanyin_sitianfang_guide.md 等（Grep+Read，零依赖）

只有当你需要"口语化语义检索"且本地已装 Ollama + bge-m3 时，才用本模块。
调用本地 Ollama 的 bge-m3 模型生成 1024 维向量，做余弦相似度检索。
返回结构与 rag_semantic.semantic_search 完全兼容，可作为其高质量替代。

与 rag_semantic.py 的区别：
- rag_semantic：纯标准库字符 n-gram 伪语义，无外部依赖，质量有限
- rag_vector：  真正的 bge-m3 向量检索，中文/中医古文语义区分能力强（但需 Ollama）

前置（仅在选用本模块时需要）：
- Ollama 已安装 bge-m3（ollama pull bge-m3）
- Ollama 服务在 http://localhost:11434（默认）

用法：
  python scripts/rag_vector.py 心火偏旺
  python scripts/rag_vector.py "岁水太过 寒气流行" --limit 5 --json
  python scripts/rag_vector.py "干燥咳嗽 皮肤干" --asset asset4
"""
import json
import os
import sys
import math
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional, Sequence, Tuple

from _common import setup_environment
setup_environment(add_lib=False)

from rag_search import ASSET_FILES, RAG_DIR, load_entries  # noqa: E402

# ── 配置 ──────────────────────────────────────────────
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = os.environ.get("WUYUN_EMBED_MODEL", "bge-m3")
EMBED_ENDPOINT = f"{OLLAMA_URL.rstrip('/')}/api/embeddings"

# 向量缓存：{文本 hash: 向量}，进程内避免重算
_VEC_CACHE: Dict[str, List[float]] = {}


def _embed_one(text: str) -> Optional[List[float]]:
    """调用 Ollama embeddings API，返回单条向量。"""
    key = text
    if key in _VEC_CACHE:
        return _VEC_CACHE[key]
    payload = json.dumps({"model": EMBED_MODEL, "prompt": text}).encode("utf-8")
    req = urllib.request.Request(
        EMBED_ENDPOINT, data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            vec = data.get("embedding")
            if vec:
                _VEC_CACHE[key] = vec
                return vec
    except urllib.error.URLError as e:
        print(f"[WARN] Ollama 不可达 ({e})。请确认 Ollama 已启动且 bge-m3 已 pull。",
              file=sys.stderr)
        return None
    except Exception as e:
        print(f"[WARN] 向量化失败: {e}", file=sys.stderr)
        return None
    return None


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    """余弦相似度。"""
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _entry_text(entry: Dict[str, Any]) -> str:
    """把一个 RAG 条目拼成可向量化的文本。"""
    parts = []
    for key in ("name", "applicable_pattern", "indications", "pathogenesis",
                "term", "explanation", "philosophy", "modern", "example",
                "formula_id", "rag_key"):
        val = entry.get(key)
        if val and isinstance(val, str):
            parts.append(val)
    return " ".join(parts)


def _entry_id(entry: Dict[str, Any], idx: int) -> str:
    for key in ("formula_id", "code", "key", "rag_key", "entry_id",
                "sitian_key", "name", "term", "id", "title"):
        if entry.get(key):
            return str(entry[key])
    return str(idx)


def _entry_title(entry: Dict[str, Any], eid: str) -> str:
    for key in ("name", "term", "title"):
        if entry.get(key):
            return str(entry[key])
    return eid


def vector_search(
    query: str,
    limit: int = 8,
    min_score: float = 0.3,
    assets: Optional[Sequence[str]] = None,
    full: bool = False,
) -> List[Dict[str, Any]]:
    """
    用 bge-m3 做向量语义检索。
    返回结构与 rag_semantic.semantic_search 兼容，mode=vector。
    """
    q = (query or "").strip()
    if not q:
        return []
    q_vec = _embed_one(q)
    if q_vec is None:
        return []

    # 选择资产
    if assets:
        asset_keys = list(assets)
    else:
        asset_keys = [k for k in ASSET_FILES if k != "index"]

    scored: List[Tuple[float, Dict[str, Any], str, str]] = []
    for ak in asset_keys:
        try:
            fname, entries = load_entries(ak)
        except Exception:
            continue
        for idx, entry in enumerate(entries):
            text = _entry_text(entry)
            if not text:
                continue
            ev = _embed_one(text)
            if ev is None:
                continue
            sc = _cosine(q_vec, ev)
            if sc >= min_score:
                eid = _entry_id(entry, idx)
                scored.append((sc, entry, eid, ak))

    scored.sort(key=lambda x: -x[0])

    hits: List[Dict[str, Any]] = []
    for sc, entry, eid, ak in scored[:limit]:
        text = _entry_text(entry)
        preview = text.replace("\n", " ").strip()
        if len(preview) > 180:
            preview = preview[:180] + "…"
        hit: Dict[str, Any] = {
            "score": round(sc, 4),
            "asset": ak,
            "file": ASSET_FILES.get(ak, ak),
            "id": eid,
            "title": _entry_title(entry, eid),
            "matched_fields": ["vector"],
            "preview": preview,
            "mode": "vector",
            "query": q,
            "model": EMBED_MODEL,
        }
        if full:
            hit["entry"] = entry
        hits.append(hits) if False else hits.append(hit)
    return hits


def format_text(hits: List[Dict[str, Any]], query: str) -> str:
    lines = [
        f"向量语义检索（{EMBED_MODEL} via Ollama）: {query}",
        f"命中: {len(hits)} 条（bge-m3 余弦相似度 ≥ 阈值）",
        "",
    ]
    if not hits:
        lines.append("（无结果。可降低阈值、换措辞，或改用 --key / --date 精确检索）")
        return "\n".join(lines)
    for h in hits:
        lines.append(f"  [{h['score']:.4f}] {h['asset']} · {h['title']}")
        lines.append(f"    {h['preview']}")
        lines.append("")
    return "\n".join(lines)


def main():
    import argparse
    p = argparse.ArgumentParser(description="bge-m3 本地向量语义检索")
    p.add_argument("query", help="口语/语义查询")
    p.add_argument("--limit", type=int, default=8)
    p.add_argument("--min-score", type=float, default=0.3, help="最低余弦阈值（默认 0.3）")
    p.add_argument("--asset", "-a", action="append", help="限定资产（可多次）")
    p.add_argument("--full", action="store_true", help="输出完整条目")
    p.add_argument("--json", action="store_true", help="JSON 输出")
    args = p.parse_args()

    hits = vector_search(
        args.query, limit=args.limit, min_score=args.min_score,
        assets=args.asset, full=args.full,
    )
    if args.json:
        print(json.dumps(hits, ensure_ascii=False, indent=2))
    else:
        print(format_text(hits, args.query))


if __name__ == "__main__":
    main()
