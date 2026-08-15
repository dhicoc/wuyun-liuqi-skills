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
import os
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
    # 蒸馏研读框架（book-to-skill 风格，源自《运气证治歌诀》王旭高）
    "asset34": "asset34_yunqi_zhengzhi_gejue.json",
    "asset34_yunqi_zhengzhi_gejue": "asset34_yunqi_zhengzhi_gejue.json",
    "yunqi_zhengzhi_gejue": "asset34_yunqi_zhengzhi_gejue.json",
    "gejue": "asset34_yunqi_zhengzhi_gejue.json",
    "yunqi_gejue": "asset34_yunqi_zhengzhi_gejue.json",
    "wuyun_shifang": "asset34_yunqi_zhengzhi_gejue.json",
    "liuqi_liufang": "asset34_yunqi_zhengzhi_gejue.json",
    # 蒸馏研读框架（book-to-skill 风格，源自《医宗金鉴·运气要诀》吴谦）
    "asset35": "asset35_yizong_jinjian_yunqi_yaojue.json",
    "asset35_yizong_jinjian_yunqi_yaojue": "asset35_yizong_jinjian_yunqi_yaojue.json",
    "yizong_jinjian_yunqi_yaojue": "asset35_yizong_jinjian_yunqi_yaojue.json",
    "yaojue": "asset35_yizong_jinjian_yunqi_yaojue.json",
    "yunqi_yaojue": "asset35_yizong_jinjian_yunqi_yaojue.json",
    # 蒸馏研读框架（book-to-skill 风格，源自《三因》卷五运气诸方·陈无择）
    "asset36": "asset36_sanyin_sitiansi_yunqi_fang.json",
    "asset36_sanyin_sitiansi_yunqi_fang": "asset36_sanyin_sitiansi_yunqi_fang.json",
    "sanyin_sitiansi_yunqi_fang": "asset36_sanyin_sitiansi_yunqi_fang.json",
    "sanyin": "asset36_sanyin_sitiansi_yunqi_fang.json",
    "sanyin_yunqi_fang": "asset36_sanyin_sitiansi_yunqi_fang.json",
    # 蒸馏研读框架（book-to-skill 风格，源自《类经图翼》卷一·卷二运气·张介宾）
    "asset37": "asset37_liejing_tuyi_yunqi.json",
    "asset37_liejing_tuyi_yunqi": "asset37_liejing_tuyi_yunqi.json",
    "liejing_tuyi_yunqi": "asset37_liejing_tuyi_yunqi.json",
    "liejing": "asset37_liejing_tuyi_yunqi.json",
    "liejing_tuyi": "asset37_liejing_tuyi_yunqi.json",
    "tuyi": "asset37_liejing_tuyi_yunqi.json",
    # —— 蒸馏研读框架 #5：宋·刘温舒《素问入式运气论奥》（专论·机制纵深层）——
    "asset38": "asset38_suwen_rushi_yunqi_lunao.json",
    "asset38_suwen_rushi_yunqi_lunao": "asset38_suwen_rushi_yunqi_lunao.json",
    "suwen_rushi_yunqi_lunao": "asset38_suwen_rushi_yunqi_lunao.json",
    "yunqi_lunao": "asset38_suwen_rushi_yunqi_lunao.json",
    "lunao": "asset38_suwen_rushi_yunqi_lunao.json",
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
    # 稳定唯一标识优先级：先 case_id/entry_id（医案/岁图类条目的稳定唯一键），
    # 次 key/id，再 code（如病机 asset 的 water_excess 等语义码），最后 rag_key/sitian_key。
    # 若把 code 提到 case_id 之前，asset9 岁图（code 非唯一、case_id 唯一）会撞 id；
    # 若把 rag_key 提前，医案（rag_key 是病证名「中风」，非唯一）也会撞 id。
    for key in ("case_id", "entry_id", "key", "id", "code", "rag_key", "sitian_key", "name", "term", "title"):
        if entry.get(key):
            return str(entry[key])
    return f"entry_{idx}"


def _entry_title(entry: Dict[str, Any], eid: str) -> str:
    for key in ("name", "term", "title", "formula_name", "region", "constitution"):
        if entry.get(key):
            return str(entry[key])
    return eid


# 稳定引用格式：yle:<asset文件名>:<entry_id>
# 例：yle:asset13_gujin_an_cases:gujin_001
# asset 文件名（如 asset13_gujin_an_cases）稳定；entry_id（gujin_001）为条目唯一标识。
YLI_REF_PREFIX = "yle:"


def _asset_basename(fname: str) -> str:
    """文件名去掉目录与 .json 后缀，作为稳定 asset 名。"""
    base = os.path.basename(fname)
    if base.endswith(".json"):
        base = base[:-5]
    return base


def make_ref(fname: str, eid: str) -> str:
    """生成稳定引用 yle:<asset>:<entry_id>。"""
    if not eid:
        return ""
    return f"{YLI_REF_PREFIX}{_asset_basename(fname)}:{eid}"


def parse_ref(ref: str):
    """把 yle: 引用拆成 (asset_basename, entry_id)。非 yle: 或无 ID 返回 (None, None)。"""
    if not ref or not ref.startswith(YLI_REF_PREFIX):
        return None, None
    body = ref[len(YLI_REF_PREFIX):]
    if ":" not in body:
        return None, None
    asset_name, eid = body.split(":", 1)
    return asset_name, eid


def resolve_ref(ref: str):
    """解析 yle: 引用，返回 (hit_dict | None, error_str|None)。

    hit_dict 含 asset_name/file/id/matched_fields/preview/title，供下游核验引用可访问。
    """
    asset_name, eid = parse_ref(ref)
    if not asset_name or not eid:
        return None, f"格式无效，应为 {YLI_REF_PREFIX}<asset>:<entry_id>: {ref!r}"
    # 由 asset 名定位 json 文件
    p = RAG_DIR / (asset_name + ".json")
    if not p.is_file():
        return None, f"未知 asset: {asset_name}"
    fname = p.name
    try:
        _, entries = load_entries(asset_name + ".json")
    except Exception as exc:
        return None, f"加载 {asset_name} 失败: {exc}"
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        # 优先用 case_id / entry_id 精确匹配（唯一标识）；否则回退 _entry_id
        cid = entry.get("case_id") or entry.get("entry_id")
        if (cid == eid) or (not cid and _entry_id(entry, i) == eid):
            preview = ""
            for key in ("explanation", "pathogenesis", "classics_quote", "description",
                        "treatment_principle", "summary", "source_quote", "formula"):
                if entry.get(key) and isinstance(entry[key], str):
                    preview = entry[key].strip().replace("\n", " ")[:180]
                    break
            return {
                "ref": make_ref(fname, str(cid or eid)),
                "asset_name": asset_name,
                "file": fname,
                "id": str(cid or eid),
                "title": _entry_title(entry, str(cid or eid)),
                "preview": preview,
            }, None
    return None, f"asset {asset_name} 中无 entry_id={eid}"


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


# ═══════════════════════════════════════════════════════════════
# 字形归一化：统一中医术语的异体字 / 繁简变体，提升检索召回
# ═══════════════════════════════════════════════════════════════
# 只收录「有明确对应、归一后不产生歧义」的常用变体，避免误改。
# 匹配顺序：先长串后单字（如「針刺」→「针刺」先于「針」→「针」）。
# 用法：对 entry 文本与查询词分别调用 _normalize 后做包含判断，不改 entry 原始值。
_NORM_MAP: List[Tuple[str, str]] = [
    # 针灸类（先长串后单字，顺序敏感）
    ("針刺", "针刺"), ("鍼刺", "针刺"),
    ("針灸", "针灸"), ("鍼灸", "针灸"),
    ("針", "针"), ("鍼", "针"),
    ("剌", "刺"),  # 異體「剌」vs「刺」
    # 穴位/经络异体（库内以简体为难；俞/腧 不同写法统一为「腧」）
    ("俞穴", "腧穴"),
    # 常用繁简（异体/繁体 → 简体；中医药高频）
    ("證", "证"), ("証", "证"),
    ("癥瘕", "症瘕"), ("癥", "症"),
    ("欝", "郁"), ("鬱", "郁"), ("鬰", "郁"),
    ("裏", "里"), ("裡", "里"),
    ("欬", "咳"), ("晝", "昼"), ("婦", "妇"),
    ("乾", "干"), ("發", "发"), ("餘", "余"),
    ("痺", "痹"), ("勞", "劳"), ("虛", "虚"),
    ("脈", "脉"), ("臟", "脏"), ("膽", "胆"),
    ("陰", "阴"), ("陽", "阳"), ("體", "体"),
    ("氣", "气"), ("衞", "卫"), ("衛", "卫"), ("營", "营"),
    ("風", "风"), ("熱", "热"), ("濕", "湿"), ("溼", "湿"),
    ("瀉", "泻"), ("㵼", "泻"), ("補", "补"), ("飲", "饮"),
    ("經", "经"), ("絡", "络"),
    ("滯", "滞"), ("痺", "痹"),
    ("惡", "恶"), ("嘔", "呕"), ("噁", "恶"),
    ("煩", "烦"), ("濁", "浊"),
    ("癰", "痈"),
    ("溫", "温"), ("瘧", "疟"),
    ("傷", "伤"),  # 伤寒/伤风/损伤
    ("脅", "胁"), ("脇", "胁"),  # 胸胁痛
    ("潰", "溃"), ("瘡", "疮"),
    ("癲", "癫"), ("癇", "痫"), ("痙", "痉"),
    ("瘻", "瘘"),
    ("攣", "挛"),  # 痉挛
    ("腫", "肿"), ("脹", "胀"), ("浮腫", "浮肿"),
    ("眥", "眦"),  # 目眦
]


def _normalize(text: str) -> str:
    """字形归一化：NFKC + 异体/繁简映射，返回归一化字符串。

    用于两处：
      1) entry 的拼接文本（score_entry_synonym / score_entry 内 text_all、title、各 val）
      2) 查询词（_expand_synonyms 内对原词 + 同义词）
    使「針刺」/「鍼灸」/「証」等异体与简体互通，提升检索召回。
    """
    if not text:
        return text
    s = text
    try:
        import unicodedata
        s = unicodedata.normalize("NFKC", s)
    except Exception:
        pass
    for a, b in _NORM_MAP:
        if a in s:
            s = s.replace(a, b)
    return s


def _expand_synonyms(terms: Sequence[str]) -> List[List[str]]:
    """将查询词扩展为同义词组列表。

    返回 [[原始词, 同义词1, ...], ...]
    每组内是 OR 关系（任一命中即可），组间是 AND 关系。
    每个词额外并入其「字形归一化」形式（异体/繁简→简体），
    使「針刺」等异体查询也能命中库内简体「针刺」。
    """
    expanded = []
    for t in terms:
        t = t.strip()
        if not t:
            continue
        norm = _normalize(t)
        group = [t]
        if norm != t and norm not in group:
            group.append(norm)  # 归一化形式作为同组 OR 备选
        # 同义词扩展：以「归一化简体」为主键查询，保证繁体/异体查询
        # 也能享受与简体一致的同义词组（如 痹证 → 痹/痹痛/风湿/关节痛）。
        syn_key = norm if norm != t else t
        if syn_key in _SYNONYM_MAP:
            for sy in _SYNONYM_MAP[syn_key]:
                if sy not in group:
                    group.append(sy)
        elif t in _SYNONYM_MAP:  # 兜底：原词本身在表中
            for sy in _SYNONYM_MAP[t]:
                if sy not in group:
                    group.append(sy)
        expanded.append(group)
    return expanded


def describe_terms(terms: Sequence[str]) -> List[Dict[str, Any]]:
    """返回检索词的『歧义消解』过程，供 --show-terms 展示。

    每个词返回：原词 / 规范化(异体繁简→简体) / 实际检索词（含同义词组的 OR 表）。
    """
    expanded = _expand_synonyms(terms)
    out = []
    for group in expanded:
        if not group:
            continue
        raw = group[0]
        out.append({
            "raw": raw,
            "normalized": _normalize(raw),
            "expanded_or": group,
        })
    return out


def score_entry_synonym(entry: Dict[str, Any], expanded_terms: List[List[str]]) -> Tuple[int, List[str], str]:
    """同义词感知的打分函数。每组内 OR，组间 AND。"""
    if not expanded_terms:
        return 0, [], ""

    fields = _flatten_strings(entry)
    blob_pairs = [(k, v) for k, v in fields]
    text_all = "\n".join(v for _, v in blob_pairs)
    text_lower = text_all.lower()
    # 归一化文本（异体/繁简→简体），与 _expand_synonyms 提供的归一化查询词对齐，
    # 使条目内异体写法（如「針灸」）也能被简体/异体查询命中。
    text_all_norm = _normalize(text_all)

    # 每组内至少一个词命中（AND 组间，OR 组内）
    group_hits = []
    for group in expanded_terms:
        found = False
        for t in group:
            tn = _normalize(t)
            if (t.lower() in text_lower or t in text_all) or (tn and tn in text_all_norm):
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
    title_norm = _normalize(title)

    for group in group_hits:
        best_t = None
        best_sc = 0
        for t in group:
            tl = t.lower()
            tn = _normalize(t)
            sc = 0
            if (t in title or tl in title.lower()) or (tn and tn in title_norm):
                sc += 8
            for key in ("code", "key", "rag_key", "term", "pinyin", "category"):
                val = str(entry.get(key) or "")
                valn = _normalize(val)
                if (t == val or tl == val.lower() or t in val) or (tn and (tn in valn or tn == valn)):
                    sc += 10
            for k, v in blob_pairs:
                if t in v or tl in v.lower():
                    sc += 2
                    if "quote" in k.lower() or "classics" in k.lower() or "pathogenesis" in k.lower():
                        sc += 2
                elif tn:
                    vn = _normalize(v)
                    if tn in vn:
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
            tn = _normalize(best_t)
            if (best_t in title or tl in title.lower()) or (tn and tn in title_norm):
                matched.append("title")
            for key in ("category", "code", "key", "rag_key"):
                val = str(entry.get(key) or "")
                if best_t in val or tl in val.lower():
                    matched.append(key)
            for k, v in blob_pairs:
                vn = _normalize(v)
                if (best_t in v or tl in v.lower()) or (tn and tn in vn):
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
    命中判定含字形归一化（异体/繁简→简体），见 _normalize。
    """
    fields = _flatten_strings(entry)
    blob_pairs = [(k, v) for k, v in fields]
    text_all = "\n".join(v for _, v in blob_pairs)
    text_lower = text_all.lower()
    text_all_norm = _normalize(text_all)
    terms_norm = [t.strip() for t in terms if t and t.strip()]
    if not terms_norm:
        return 0, [], ""

    for t in terms_norm:
        tn = _normalize(t)
        if not ((t.lower() in text_lower or t in text_all) or (tn and tn in text_all_norm)):
            return 0, [], ""

    score = 0
    matched: List[str] = []
    eid = _entry_id(entry, 0)
    title = _entry_title(entry, eid)
    title_norm = _normalize(title)

    for t in terms_norm:
        tl = t.lower()
        tn = _normalize(t)
        # 标题 / 主键加权
        if (t in title or tl in title.lower()) or (tn and tn in title_norm):
            score += 8
            matched.append("title")
        for key in ("code", "key", "rag_key", "term", "pinyin"):
            val = str(entry.get(key) or "")
            valn = _normalize(val)
            if (t == val or tl == val.lower() or t in val) or (tn and (tn == valn or tn in valn)):
                score += 10
                matched.append(key)
        # 字段命中
        for k, v in blob_pairs:
            matched_here = (t in v or tl in v.lower())
            vn = _normalize(v)
            if matched_here or (tn and tn in vn):
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
            "asset34",  # 蒸馏研读框架（book-to-skill 风格，源自《运气证治歌诀》）
            "asset35",  # 蒸馏研读框架（book-to-skill 风格，源自《医宗金鉴·运气要诀》）
            "asset36",  # 蒸馏研读框架（book-to-skill 风格，源自《三因》卷五运气诸方·陈无择）
            "asset37",  # 蒸馏研读框架（book-to-skill 风格，源自《类经图翼》卷一·卷二运气·张介宾）
            "asset38",  # 蒸馏研读框架（book-to-skill 风格，源自《素问入式运气论奥》·刘温舒）
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
                "ref": make_ref(fname, eid),
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
                "ref": make_ref(fname, eid),
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
                "ref": make_ref(fname, eid),
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


# 轻量免责声明：仅追加在「人类可读（非 JSON）」文献检索输出末尾。
# JSON 模式保持纯净（供程序消费），不混入文案。
RAG_DISCLAIMER = (
    "\n⚠️ 以上文献内容由知识库检索直接返回，仅供学习参考。"
    "涉及临床辨证、方药使用、体质调养，须由执业中医师四诊合参、辨证论治，"
    "本工具不提供医疗建议。"
)


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
    parser.add_argument(
        "--show-terms",
        action="store_true",
        help="关键词模式：打印检索词经『开素+同义词+字形归一化』歧义消解后的实际检索词表",
    )
    parser.add_argument(
        "--include-extra",
        action="store_true",
        help="关键词模式：主检索命中后自动补一轮更宽同义词检索追加入口（两段式，默认关，不改变现有结果）",
    )
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
            print(RAG_DISCLAIMER)
        return 0 if hits else 1

    # 模式 1：按日打包
    if args.date:
        bundle = fetch_by_date(args.date, full=args.full)
        if args.json:
            # full 时 entry 已在 hits 内
            print(json.dumps(bundle, ensure_ascii=False, indent=2))
        else:
            print(format_date_bundle(bundle))
            print(RAG_DISCLAIMER)
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
            print(RAG_DISCLAIMER)
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
            print(RAG_DISCLAIMER)
        return 0 if hits else 1

    # 模式 3：关键词
    if not args.terms:
        parser.print_help()
        print("\n" + list_assets())
        return 0

    # --show-terms：打印检索词歧义消解（原词 → 归一化 → 同义词 OR 表）
    if args.show_terms:
        terms_desc = describe_terms(args.terms)
        if args.json:
            print(json.dumps({"mode": "show_terms", "terms": terms_desc}, ensure_ascii=False, indent=2))
        else:
            print("检索词歧义消解：")
            for d in terms_desc:
                print(f"  {d['raw']} → 归一化 {d['normalized']} | OR组 {', '.join(d['expanded_or'])}")
        return 0

    hits = search(args.terms, assets=args.assets, limit=args.limit)
    # --include-extra：两段式补检索。主检索命中不足时，再按每组归一化核心词
    # 做一次更宽的 OR 检索，去重追加，扩大召回（不改变主检索排序）。
    if args.include_extra and len(hits) < args.limit:
        core_terms = []
        for d in describe_terms(args.terms):
            # 每组取「归一化核心词」作为宽 OR 候选（去掉多词 AND 限制）
            core = d["normalized"] or d["expanded_or"][0]
            if core not in core_terms:
                core_terms.append(core)
        extra = []
        for t in core_terms:
            extra.extend(search([t], assets=args.assets, limit=args.limit))
        seen = {h["id"] + "|" + h.get("asset", "") for h in hits}
        for h in extra:
            if h["id"] + "|" + h.get("asset", "") not in seen:
                seen.add(h["id"] + "|" + h.get("asset", ""))
                hits.append(h)
        hits = hits[:args.limit]

    if args.json:
        payload = {
            "terms": args.terms,
            "assets": args.assets,
            "count": len(hits),
            "hits": hits,
            "mode": "keyword",
        }
        # 仅当两段式补检索显式开启时才追加标记，保持默认 JSON 结构向后兼容
        if args.include_extra:
            payload["extra_expanded"] = True
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(format_text(hits, args.terms, mode="keyword"))
        print(RAG_DISCLAIMER)
    return 0 if hits else 1


if __name__ == "__main__":
    raise SystemExit(main())
