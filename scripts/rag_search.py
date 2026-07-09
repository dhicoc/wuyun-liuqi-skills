#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG / 文献关键词检索（轻量，optimization-sprint Phase 5+）

对 rag-knowledge-base 下 JSON 资产与术语库做：
  1) 关键词 / 多词 AND 模糊检索
  2) rag_key / code / key **精确直取**
  3) 按日期拉取 calculate_yunqi_api 的 rag_keys 并批量精确命中（Agent 一键）

用法:
  python scripts/rag_search.py 司天
  python scripts/rag_search.py 木运 太过
  python scripts/rag_search.py --key water_excess
  python scripts/rag_search.py --key shaoyin_junhuo_sitian --full
  python scripts/rag_search.py --date 2026-06-29
  python scripts/rag_search.py --date today --json
  python scripts/rag_search.py --semantic 心火偏旺
  python scripts/rag_search.py --list-assets
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from _common import setup_environment, add_scripts_dir_to_path

setup_environment(add_lib=False)
add_scripts_dir_to_path()

ROOT = Path(__file__).resolve().parent.parent
RAG_DIR = ROOT / "rag-knowledge-base"

# 可检索资产
ASSET_FILES = {
    "asset1": "asset1_suiyun.json",
    "asset1_suiyun": "asset1_suiyun.json",
    "asset2": "asset2_sitian_zaiquan.json",
    "asset2_sitian_zaiquan": "asset2_sitian_zaiquan.json",
    "asset3": "asset3_kezhujialin.json",
    "asset3_kezhujialin": "asset3_kezhujialin.json",
    "asset4": "asset4_formula.json",
    "asset4_formula": "asset4_formula.json",
    "asset5": "asset5_commentary.json",
    "asset5_commentary": "asset5_commentary.json",
    "asset6": "asset6_regional.json",
    "asset6_regional": "asset6_regional.json",
    "asset7": "asset7_constitution.json",
    "asset7_constitution": "asset7_constitution.json",
    "terminology": "terminology.json",
    "term": "terminology.json",
    "index": "index.json",
}

# 模块级缓存：避免重复 open + json.load
_ENTRY_CACHE: Dict[str, Tuple[str, List[Dict[str, Any]]]] = {}


def _flatten_strings(obj: Any, prefix: str = "") -> List[Tuple[str, str]]:
    """递归抽取可搜索字符串字段。"""
    out: List[Tuple[str, str]] = []
    if obj is None:
        return out
    if isinstance(obj, str):
        if obj.strip():
            out.append((prefix or "text", obj))
        return out
    if isinstance(obj, (int, float, bool)):
        out.append((prefix or "value", str(obj)))
        return out
    if isinstance(obj, list):
        for i, item in enumerate(obj):
            out.extend(_flatten_strings(item, f"{prefix}[{i}]" if prefix else f"[{i}]"))
        return out
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else str(k)
            out.extend(_flatten_strings(v, p))
    return out


def _entry_id(entry: Dict[str, Any], idx: int) -> str:
    for key in ("code", "key", "rag_key", "entry_id", "sitian_key", "name", "term", "id", "title"):
        if entry.get(key):
            return str(entry[key])
    return f"entry_{idx}"


def _entry_title(entry: Dict[str, Any], eid: str) -> str:
    for key in ("name", "term", "title", "formula_name", "region", "constitution"):
        if entry.get(key):
            return str(entry[key])
    return eid


def load_entries(asset_key: str) -> Tuple[str, List[Dict[str, Any]]]:
    """加载资产 JSON，带模块级缓存。"""
    if asset_key in _ENTRY_CACHE:
        return _ENTRY_CACHE[asset_key]

    fname = ASSET_FILES.get(asset_key)
    if not fname:
        if asset_key.endswith(".json"):
            fname = asset_key
        else:
            raise FileNotFoundError(f"未知资产: {asset_key}")
    path = RAG_DIR / fname
    if not path.is_file():
        raise FileNotFoundError(f"文件不存在: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        result = (fname, data)
    elif isinstance(data, dict):
        if "entries" in data and isinstance(data["entries"], list):
            result = (fname, data["entries"])
        else:
            result = (fname, [data])
    else:
        result = (fname, [])

    _ENTRY_CACHE[asset_key] = result
    return result


def score_entry(entry: Dict[str, Any], terms: Sequence[str]) -> Tuple[int, List[str], str]:
    """
    返回 (score, matched_fields_snippet, preview)。
    所有 term 都必须命中（AND）；计分：标题/ code 命中加权。
    """
    fields = _flatten_strings(entry)
    blob_pairs = [(k, v) for k, v in fields]
    text_all = "\n".join(v for _, v in blob_pairs)
    text_lower = text_all.lower()
    terms_norm = [t.strip() for t in terms if t and t.strip()]
    if not terms_norm:
        return 0, [], ""

    for t in terms_norm:
        if t.lower() not in text_lower and t not in text_all:
            return 0, [], ""

    score = 0
    matched: List[str] = []
    eid = _entry_id(entry, 0)
    title = _entry_title(entry, eid)

    for t in terms_norm:
        tl = t.lower()
        # 标题 / 主键加权
        if t in title or tl in title.lower():
            score += 8
            matched.append("title")
        for key in ("code", "key", "rag_key", "term", "pinyin"):
            val = str(entry.get(key) or "")
            if t == val or tl == val.lower() or t in val:
                score += 10
                matched.append(key)
        # 字段命中
        for k, v in blob_pairs:
            if t in v or tl in v.lower():
                score += 2
                if k not in matched and len(matched) < 6:
                    matched.append(k)
                # 经典原文额外加分
                if "quote" in k.lower() or "classics" in k.lower() or "pathogenesis" in k.lower():
                    score += 2

    # 预览：优先 pathogenesis / explanation / classics_quote
    preview = ""
    for key in ("explanation", "pathogenesis", "classics_quote", "description", "treatment_principle", "summary"):
        if entry.get(key) and isinstance(entry[key], str):
            preview = entry[key].strip().replace("\n", " ")
            break
    if not preview:
        preview = text_all.strip().replace("\n", " ")[:200]
    if len(preview) > 180:
        preview = preview[:180] + "…"

    return score, matched, preview


def _default_asset_keys() -> List[str]:
    seen_files = set()
    keys: List[str] = []
    for k, f in ASSET_FILES.items():
        if f not in seen_files and k in (
            "asset1", "asset2", "asset3", "asset4", "asset5", "asset6", "asset7", "terminology"
        ):
            seen_files.add(f)
            keys.append(k)
    return keys


def search(
    terms: Sequence[str],
    assets: Optional[Sequence[str]] = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    keys = list(assets) if assets else _default_asset_keys()
    hits: List[Dict[str, Any]] = []
    for ak in keys:
        try:
            fname, entries = load_entries(ak)
        except FileNotFoundError:
            continue
        for i, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue
            sc, matched, preview = score_entry(entry, terms)
            if sc <= 0:
                continue
            eid = _entry_id(entry, i)
            hits.append({
                "score": sc,
                "asset": ak,
                "file": fname,
                "id": eid,
                "title": _entry_title(entry, eid),
                "matched_fields": list(dict.fromkeys(matched))[:8],
                "preview": preview,
                "mode": "keyword",
            })

    hits.sort(key=lambda x: (-x["score"], x["asset"], x["id"]))
    return hits[:limit]


# 精确匹配时检查的字段（与 calculate_yunqi_api.rag_keys 对齐）
_EXACT_ID_FIELDS = (
    "code", "key", "rag_key", "sitian_key", "zaiquan_key",
    "entry_id", "term", "pinyin", "id",
)


def _entry_matches_key(entry: Dict[str, Any], rag_key: str) -> Optional[str]:
    """若 entry 精确匹配 rag_key，返回命中字段名。"""
    target = rag_key.strip()
    if not target:
        return None
    tl = target.lower()
    for field in _EXACT_ID_FIELDS:
        val = entry.get(field)
        if val is None:
            continue
        s = str(val).strip()
        if s == target or s.lower() == tl:
            return field
    return None


def lookup_key(
    rag_key: str,
    assets: Optional[Sequence[str]] = None,
    full: bool = False,
) -> List[Dict[str, Any]]:
    """
    按 rag_key / code / key 等字段**精确**命中。
    例如: water_excess, shaoyin_junhuo_sitian, zhu_shaoyang_ke_shaoyin
    """
    keys = list(assets) if assets else _default_asset_keys()
    hits: List[Dict[str, Any]] = []
    for ak in keys:
        try:
            fname, entries = load_entries(ak)
        except FileNotFoundError:
            continue
        for i, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue
            field = _entry_matches_key(entry, rag_key)
            if not field:
                continue
            # 展示 id 优先用命中字段（司天/在泉同条时避免总显示 sitian_key）
            eid = str(entry.get(field) or _entry_id(entry, i))
            title = _entry_title(entry, eid)
            if field in ("sitian_key", "zaiquan_key") and entry.get("name"):
                title = str(entry.get("name"))
            elif field in ("sitian_key", "zaiquan_key"):
                # 配对条目：用司天/在泉中文名增强可读性
                parts = []
                if entry.get("sitian"):
                    parts.append(f"司天{entry['sitian']}")
                if entry.get("zaiquan"):
                    parts.append(f"在泉{entry['zaiquan']}")
                if parts:
                    title = " / ".join(parts)
            preview = ""
            for pk in ("explanation", "pathogenesis", "classics_quote", "description", "treatment_principle",
                       "sitian_pathogenesis", "zaiquan_pathogenesis"):
                if entry.get(pk) and isinstance(entry[pk], str):
                    preview = entry[pk].strip().replace("\n", " ")
                    break
            if not preview and field == "zaiquan_key":
                for pk in ("zaiquan_pathogenesis", "zaiquan_symptoms", "description"):
                    if entry.get(pk) and isinstance(entry[pk], str):
                        preview = entry[pk].strip().replace("\n", " ")
                        break
            if len(preview) > 180:
                preview = preview[:180] + "…"
            hit: Dict[str, Any] = {
                "score": 100,
                "asset": ak,
                "file": fname,
                "id": eid,
                "title": title,
                "matched_fields": [field],
                "preview": preview or eid,
                "mode": "exact_key",
                "query_key": rag_key,
            }
            if full:
                hit["entry"] = entry
            hits.append(hit)
    return hits


def fetch_by_date(
    date_str: str = "today",
    full: bool = False,
) -> Dict[str, Any]:
    """
    Agent 一键：推算日期 → rag_keys → 精确拉取知识库条目。
    返回 { date, yunqi_year, rag_keys, hits: {role: [hit,...]}, missing: [...] }
    """
    from calculate_yunqi_api import calculate_yunqi_api, _resolve_date

    resolved = _resolve_date(date_str)
    result = calculate_yunqi_api(resolved)
    rag_keys = result.get("rag_keys") or {}
    hits_by_role: Dict[str, List[Dict[str, Any]]] = {}
    missing: List[str] = []
    all_hits: List[Dict[str, Any]] = []

    for role, key in rag_keys.items():
        if not key:
            continue
        found = lookup_key(str(key), full=full)
        hits_by_role[role] = found
        if not found:
            missing.append(f"{role}:{key}")
        else:
            for h in found:
                h = dict(h)
                h["role"] = role
                all_hits.append(h)

    return {
        "date": resolved,
        "yunqi_year": result.get("yunqi_year"),
        "year_gz": result.get("year_gz"),
        "rag_keys": rag_keys,
        "hits_by_role": hits_by_role,
        "hits": all_hits,
        "missing": missing,
        "mode": "from_date",
    }


def format_text(hits: List[Dict[str, Any]], terms: Sequence[str], mode: str = "keyword") -> str:
    label = "精确键" if mode == "exact_key" else "检索词"
    lines = [
        f"{label}: {' AND '.join(terms) if terms else '(none)'}",
        f"命中: {len(hits)} 条",
        "",
    ]
    if not hits:
        lines.append("（无结果。可试 --key <rag_key> 精确直取，或 --date today 按日打包）")
        return "\n".join(lines)
    for i, h in enumerate(hits, 1):
        role = f" [{h['role']}]" if h.get("role") else ""
        lines.append(f"{i}. [{h['score']}]{role} {h['title']}  ({h['asset']} / {h['id']})")
        lines.append(f"   文件: {h['file']} · mode={h.get('mode', mode)}")
        if h.get("matched_fields"):
            lines.append(f"   字段: {', '.join(h['matched_fields'])}")
        lines.append(f"   摘要: {h['preview']}")
        lines.append("")
    lines.append("提示: --full 可在 --json 中附带完整 entry；临床内容须附免责声明。")
    return "\n".join(lines)


def format_date_bundle(bundle: Dict[str, Any]) -> str:
    lines = [
        f"日期: {bundle.get('date')} · 运气年 {bundle.get('yunqi_year')}（{bundle.get('year_gz')}）",
        f"rag_keys: {json.dumps(bundle.get('rag_keys') or {}, ensure_ascii=False)}",
        "",
    ]
    for role, hits in (bundle.get("hits_by_role") or {}).items():
        key = (bundle.get("rag_keys") or {}).get(role, "")
        lines.append(f"## {role} → `{key}`")
        if not hits:
            lines.append("  （未命中）")
        else:
            for h in hits:
                lines.append(f"  · {h['title']} ({h['asset']}/{h['id']})")
                lines.append(f"    {h['preview']}")
        lines.append("")
    missing = bundle.get("missing") or []
    if missing:
        lines.append("未命中: " + ", ".join(missing))
    else:
        lines.append("全部 rag_keys 均有知识库命中。")
    lines.append("")
    lines.append("提示: python scripts/rag_search.py --date today --json --full")
    return "\n".join(lines)


def list_assets() -> str:
    lines = ["可检索资产:", ""]
    seen = set()
    for k, f in sorted(ASSET_FILES.items()):
        if f in seen:
            continue
        seen.add(f)
        path = RAG_DIR / f
        status = "OK" if path.is_file() else "MISSING"
        lines.append(f"  --asset {k:<22} → {f}  [{status}]")
    lines += [
        "",
        "精确直取: --key water_excess",
        "按日打包: --date 2026-06-29  或  --date today",
    ]
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="RAG 知识库检索：关键词 AND / rag_key 精确直取 / 按日打包",
        epilog="""示例:
  python scripts/rag_search.py 司天 君火 --limit 5
  python scripts/rag_search.py --key water_excess --json
  python scripts/rag_search.py --date today --json
  python scripts/rag_search.py --date 2026-06-29 --full --json
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("terms", nargs="*", help="关键词（多个为 AND）")
    parser.add_argument(
        "--asset",
        action="append",
        dest="assets",
        help="限定资产，可多次。如 asset1 / terminology / asset5",
    )
    parser.add_argument("--key", "-k", action="append", dest="keys",
                        help="精确 rag_key/code（可多次）")
    parser.add_argument("--date", "-d", default=None,
                        help="按日期推算 rag_keys 并精确拉取（today / YYYY-MM-DD）")
    parser.add_argument("--semantic", "-s", default=None,
                        help="轻量语义/口语检索（字符 n-gram，无外部模型）")
    parser.add_argument("--full", action="store_true",
                        help="JSON 输出中附带完整 entry 对象")
    parser.add_argument("--limit", type=int, default=10, help="关键词/语义模式最多条数（默认 10）")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--list-assets", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.list_assets:
        print(list_assets())
        return 0

    # 模式 0：轻量语义
    if args.semantic:
        from rag_semantic import semantic_search, format_text as fmt_sem
        q = args.semantic
        if args.terms:
            q = (q + " " + " ".join(args.terms)).strip()
        hits = semantic_search(q, limit=args.limit, assets=args.assets, full=args.full)
        if args.json:
            print(json.dumps({
                "query": q,
                "count": len(hits),
                "mode": "semantic",
                "hits": hits,
            }, ensure_ascii=False, indent=2))
        else:
            print(fmt_sem(hits, q))
        return 0 if hits else 1

    # 模式 1：按日打包
    if args.date:
        bundle = fetch_by_date(args.date, full=args.full)
        if args.json:
            # full 时 entry 已在 hits 内
            print(json.dumps(bundle, ensure_ascii=False, indent=2))
        else:
            print(format_date_bundle(bundle))
        return 0 if not bundle.get("missing") else 1

    # 模式 2：精确 key
    if args.keys:
        all_hits: List[Dict[str, Any]] = []
        for k in args.keys:
            all_hits.extend(lookup_key(k, assets=args.assets, full=args.full))
        if args.json:
            print(json.dumps({
                "keys": args.keys,
                "count": len(all_hits),
                "hits": all_hits,
                "mode": "exact_key",
            }, ensure_ascii=False, indent=2))
        else:
            print(format_text(all_hits, args.keys, mode="exact_key"))
        return 0 if all_hits else 1

    # 模式 3：关键词
    if not args.terms:
        parser.print_help()
        print("\n" + list_assets())
        return 0

    hits = search(args.terms, assets=args.assets, limit=args.limit)
    if args.json:
        print(json.dumps({
            "terms": args.terms,
            "assets": args.assets,
            "count": len(hits),
            "hits": hits,
            "mode": "keyword",
        }, ensure_ascii=False, indent=2))
    else:
        print(format_text(hits, args.terms, mode="keyword"))
    return 0 if hits else 1


if __name__ == "__main__":
    raise SystemExit(main())
