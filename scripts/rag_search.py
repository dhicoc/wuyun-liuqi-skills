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

from _common import setup_environment, add_scripts_dir_to_path, PROJECT_ROOT

setup_environment(add_lib=False)
add_scripts_dir_to_path()

ROOT = PROJECT_ROOT
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
    "asset9": "asset9_cases.json",
    "asset9_cases": "asset9_cases.json",
    "cases": "asset9_cases.json",
    "asset10": "asset10_suiyi_zhifa.json",
    "asset10_suiyi": "asset10_suiyi_zhifa.json",
    "suiyi": "asset10_suiyi_zhifa.json",
    "asset11": "asset11_mingyi_cases.json",
    "asset11_mingyi": "asset11_mingyi_cases.json",
    "mingyi": "asset11_mingyi_cases.json",
    "asset12": "asset12_xumingyi_cases.json",
    "asset12_xumingyi": "asset12_xumingyi_cases.json",
    "xumingyi": "asset12_xumingyi_cases.json",
    "asset13": "asset13_gujin_an_cases.json",
    "asset13_gujin": "asset13_gujin_an_cases.json",
    "gujin": "asset13_gujin_an_cases.json",
    "asset14": "asset14_dingganren_cases.json",
    "asset14_ding": "asset14_dingganren_cases.json",
    "dingganren": "asset14_dingganren_cases.json",
    "asset15": "asset15_shanghan90_cases.json",
    "asset15_sh90": "asset15_shanghan90_cases.json",
    "shanghan90": "asset15_shanghan90_cases.json",
    "asset16": "asset16_ye_cases.json",
    "asset16_ye": "asset16_ye_cases.json",
    "linzheng": "asset16_ye_cases.json",
    "asset17": "asset17_wenyi_yunqi.json",
    "asset17_wenyi": "asset17_wenyi_yunqi.json",
    "wenyi": "asset17_wenyi_yunqi.json",
    "songfeng": "asset17_wenyi_yunqi.json",
    "asset18": "asset18_huichunlu_cases.json",
    "asset18_huichun": "asset18_huichunlu_cases.json",
    "huichunlu": "asset18_huichunlu_cases.json",
    "wangmengying": "asset18_huichunlu_cases.json",
    "asset19": "asset19_zhangyuqing_cases.json",
    "asset19_zhangyuqing": "asset19_zhangyuqing_cases.json",
    "zhangyuqing": "asset19_zhangyuqing_cases.json",
    "asset20": "asset20_wujutong_cases.json",
    "asset20_wujutong": "asset20_wujutong_cases.json",
    "wujutong": "asset20_wujutong_cases.json",
    "asset21": "asset21_yuyicao_cases.json",
    "asset21_yuyicao": "asset21_yuyicao_cases.json",
    "yuyicao": "asset21_yuyicao_cases.json",
    "asset22": "asset22_huixi_cases.json",
    "asset22_huixi": "asset22_huixi_cases.json",
    "huixi": "asset22_huixi_cases.json",
    "asset23": "asset23_huayunlou_cases.json",
    "asset23_huayunlou": "asset23_huayunlou_cases.json",
    "huayunlou": "asset23_huayunlou_cases.json",
    "asset24": "asset24_zhenyu_juji_cases.json",
    "asset24_zhenyu": "asset24_zhenyu_juji_cases.json",
    "zhenyujuji": "asset24_zhenyu_juji_cases.json",
    "asset25": "asset25_xushi_cases.json",
    "asset25_xushi": "asset25_xushi_cases.json",
    "xushi": "asset25_xushi_cases.json",
    "asset26": "asset26_xingxuan_cases.json",
    "asset26_xingxuan": "asset26_xingxuan_cases.json",
    "xingxuan": "asset26_xingxuan_cases.json",
    "asset27": "asset27_sunwenyuan_cases.json",
    "asset27_sunwenyuan": "asset27_sunwenyuan_cases.json",
    "sunwenyuan": "asset27_sunwenyuan_cases.json",
    "asset28": "asset28_conggui_cases.json",
    "asset28_conggui": "asset28_conggui_cases.json",
    "conggui": "asset28_conggui_cases.json",
    "asset29": "asset29_waike_zhengzong.json",
    "asset29_waike": "asset29_waike_zhengzong.json",
    "waike": "asset29_waike_zhengzong.json",
    "waikezhengzong": "asset29_waike_zhengzong.json",
    "asset30": "asset30_lizhai_waike.json",
    "asset30_lizhai": "asset30_lizhai_waike.json",
    "lizhai": "asset30_lizhai_waike.json",
    "waikefahui": "asset30_lizhai_waike.json",
    "asset31": "asset31_zuihuachuang_cases.json",
    "asset31_zuihuachuang": "asset31_zuihuachuang_cases.json",
    "zuihuachuang": "asset31_zuihuachuang_cases.json",
    "asset32": "asset32_yiyan_suibi.json",
    "asset32_yiyan": "asset32_yiyan_suibi.json",
    "yiyansuibi": "asset32_yiyan_suibi.json",
    "asset33": "asset33_disease_susceptibility.json",
    "asset33_disease_susceptibility": "asset33_disease_susceptibility.json",
    "disease": "asset33_disease_susceptibility.json",
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


# ═══════════════════════════════════════════════════════════════
# 同义词扩展：中医病证名 -> 常见别名/近义词
# ═══════════════════════════════════════════════════════════════

_SYNONYM_MAP: Dict[str, List[str]] = {
    "儿科": ["小儿", "幼科", "童", "婴", "孩"],
    "妊娠": ["妊", "孕", "怀妊", "怀孕", "胎"],
    "痹证": ["痹", "痹痛", "风湿", "关节痛"],
    "胃痛": ["胃脘痛", "胃疼", "脘痛", "心胃痛"],
    "疟疾": ["疟", "寒热往来", "间日疟"],
    "中风": ["中风口眼歪斜", "卒中", "半身不遂"],
    "伤寒": ["伤于寒", "太阳病"],
    "咳嗽": ["咳", "嗽", "咳逆"],
    "产后": ["产后病", "产褥"],
    "肿胀": ["肿", "浮肿", "水肿"],
    "痢疾": ["痢", "下痢", "赤白痢"],
    "血症": ["血证", "出血", "吐血", "衄血"],
    "泄泻": ["泻", "腹泻", "便溏"],
    "湿温": ["湿热", "湿病"],
    "痰饮": ["痰", "饮证"],
    "胁痛": ["胁肋痛", "胸胁痛"],
    "吐血": ["咯血", "呕血"],
    "虚损": ["虚劳", "亏损"],
}


def _expand_synonyms(terms: Sequence[str]) -> List[List[str]]:
    """将查询词扩展为同义词组列表。

    返回 [[原始词, 同义词1, ...], ...]
    每组内是 OR 关系（任一命中即可），组间是 AND 关系。
    """
    expanded = []
    for t in terms:
        t = t.strip()
        if not t:
            continue
        group = [t]
        if t in _SYNONYM_MAP:
            group.extend(_SYNONYM_MAP[t])
        expanded.append(group)
    return expanded


def score_entry_synonym(entry: Dict[str, Any], expanded_terms: List[List[str]]) -> Tuple[int, List[str], str]:
    """同义词感知的打分函数。每组内 OR，组间 AND。"""
    if not expanded_terms:
        return 0, [], ""

    fields = _flatten_strings(entry)
    blob_pairs = [(k, v) for k, v in fields]
    text_all = "\n".join(v for _, v in blob_pairs)
    text_lower = text_all.lower()

    # 每组内至少一个词命中（AND 组间，OR 组内）
    group_hits = []
    for group in expanded_terms:
        found = False
        for t in group:
            if t.lower() in text_lower or t in text_all:
                found = True
                break
        if not found:
            return 0, [], ""
        group_hits.append(group)

    # 打分
    score = 0
    matched: List[str] = []
    eid = _entry_id(entry, 0)
    title = _entry_title(entry, eid)

    for group in group_hits:
        best_t = None
        best_sc = 0
        for t in group:
            tl = t.lower()
            sc = 0
            if t in title or tl in title.lower():
                sc += 8
            for key in ("code", "key", "rag_key", "term", "pinyin", "category"):
                val = str(entry.get(key) or "")
                if t == val or tl == val.lower() or t in val:
                    sc += 10
            for k, v in blob_pairs:
                if t in v or tl in v.lower():
                    sc += 2
                    if "quote" in k.lower() or "classics" in k.lower() or "pathogenesis" in k.lower():
                        sc += 2
            if sc > best_sc:
                best_sc = sc
                best_t = t
        score += best_sc
        if best_t:
            # 记录命中的字段
            tl = best_t.lower()
            if best_t in title or tl in title.lower():
                matched.append("title")
            for key in ("category", "code", "key", "rag_key"):
                val = str(entry.get(key) or "")
                if best_t in val or tl in val.lower():
                    matched.append(key)
            for k, v in blob_pairs:
                if best_t in v or tl in v.lower():
                    if k not in matched and len(matched) < 6:
                        matched.append(k)

    # 预览
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
    """默认检索范围：核心病机 asset1-7 + 岁图医案 asset9 + 六部历代名家医案库 asset11-16 + 疾病易感性 asset33 + 术语。

    包含 asset11-16 医案库，使默认关键词/语义检索即可命中临证真实医案。
    包含 asset33 疾病易感性，使按日期检索时自动附带疾病易感性提示。
    """
    seen_files = set()
    keys: List[str] = []
    for k, f in ASSET_FILES.items():
        if f not in seen_files and k in (
            "asset1", "asset2", "asset3", "asset4", "asset5", "asset6", "asset7",
            "asset9", "asset10",
            "asset11", "asset12", "asset13", "asset14", "asset15", "asset16",
            "asset33",
            "terminology",
        ):
            seen_files.add(f)
            keys.append(k)
    return keys


def search(
    terms: Sequence[str],
    assets: Optional[Sequence[str]] = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    # 同义词扩展：将用户查询词扩展为同义词组，任一命中即可
    expanded_terms = _expand_synonyms(terms)
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
            sc, matched, preview = score_entry_synonym(entry, expanded_terms)
            if sc <= 0:
                continue
            eid = _entry_id(entry, i)
            # 医案 asset 加权：case 类 asset 排序时额外加分
            asset_bonus = 5 if any(p in ak for p in ('asset9', 'asset11', 'asset12', 'asset13', 'asset14',
                                                       'asset15', 'asset16', 'asset17', 'asset18', 'asset19',
                                                       'asset20', 'asset21', 'asset22', 'asset23', 'asset24',
                                                       'asset25', 'asset26', 'asset27', 'asset28', 'asset29',
                                                       'asset30', 'asset31', 'asset32')) else 0
            hits.append({
                "score": sc + asset_bonus,
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


def search_by_field(
    field: str,
    terms: Sequence[str],
    assets: Optional[Sequence[str]] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """按指定字段检索医案（如 field='formula', terms=['茵陈']）。

    支持的字段包括但不限于：formula, syndrome, treatment, chief_complaint,
    physician, category, source_quote, outcome, note, herbs, rag_key 等。
    多个 terms 为 AND 关系。
    """
    keys = list(assets) if assets else _default_asset_keys()
    hits: List[Dict[str, Any]] = []
    terms_norm = [t.strip() for t in terms if t and t.strip()]

    for ak in keys:
        try:
            fname, entries = load_entries(ak)
        except FileNotFoundError:
            continue
        for i, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue
            val = entry.get(field)
            if val is None:
                continue
            val_str = str(val)
            val_lower = val_str.lower()

            all_match = True
            for t in terms_norm:
                if t.lower() not in val_lower and t not in val_str:
                    all_match = False
                    break
            if not all_match:
                continue

            eid = _entry_id(entry, i)
            preview = val_str.strip().replace("\n", " ")
            if len(preview) > 180:
                preview = preview[:180] + "…"

            hits.append({
                "score": 100,
                "asset": ak,
                "file": fname,
                "id": eid,
                "title": _entry_title(entry, eid),
                "matched_fields": [field],
                "preview": preview,
                "mode": "field",
            })

    hits.sort(key=lambda x: (x["asset"], x["id"]))
    return hits[:limit]


# 精确匹配时检查的字段（与 calculate_yunqi_api.rag_keys 对齐）
# internal_key/external_key：内外联动字段（内因病机 key → 外候医案）
_EXACT_ID_FIELDS = (
    "code", "key", "rag_key", "sitian_key", "zaiquan_key",
    "entry_id", "term", "pinyin", "id", "category",
    "internal_key", "external_key",
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

    # 组合 key 检索：司天_在泉（如 taiyang_hanshui_sitian_taiyin_shitu_zaiquan）
    sitian_key = rag_keys.get("sitian", "")
    zaiquan_key = rag_keys.get("zaiquan", "")
    if sitian_key and zaiquan_key:
        combo_key = f"{sitian_key}_{zaiquan_key}"
        combo_hits = lookup_key(combo_key, full=full)
        if combo_hits:
            hits_by_role["sitian_zaiquan_combo"] = combo_hits
            for h in combo_hits:
                h = dict(h)
                h["role"] = "sitian_zaiquan_combo"
                all_hits.append(h)
        # 否则 combo_key 不在 missing 中（非必命中）

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
        help="限定资产，可多次或逗号分隔。如 asset1 / asset26,asset27 / terminology",
    )
    parser.add_argument("--key", "-k", action="append", dest="keys",
                        help="精确 rag_key/code（可多次）")
    parser.add_argument("--date", "-d", default=None,
                        help="按日期推算 rag_keys 并精确拉取（today / YYYY-MM-DD）")
    parser.add_argument("--semantic", "-s", default=None,
                        help="轻量语义/口语检索（字符 n-gram，无外部模型）")
    parser.add_argument("--field", default=None,
                        help="按指定字段检索（如 --field formula 茵陈 / --field syndrome 湿热 / --field physician 孙一奎）")
    parser.add_argument("--full", action="store_true",
                        help="JSON 输出中附带完整 entry 对象")
    parser.add_argument("--limit", type=int, default=10, help="关键词/语义模式最多条数（默认 10）")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--list-assets", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.list_assets:
        print(list_assets())
        return 0

    # 拆分逗号分隔的 asset 列表（支持 --asset asset26,asset27 形式）
    if args.assets:
        expanded = []
        for a in args.assets:
            expanded.extend(x.strip() for x in a.split(",") if x.strip())
        args.assets = expanded or None

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

    # 模式 2.5：按字段检索
    if args.field:
        if not args.terms:
            print("错误：--field 需要配合检索词，如 --field formula 茵陈")
            return 1
        hits = search_by_field(args.field, args.terms, assets=args.assets, limit=args.limit)
        if args.json:
            print(json.dumps({
                "field": args.field,
                "terms": args.terms,
                "assets": args.assets,
                "count": len(hits),
                "hits": hits,
                "mode": "field",
            }, ensure_ascii=False, indent=2))
        else:
            print(format_text(hits, args.terms, mode="field"))
        return 0 if hits else 1

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
