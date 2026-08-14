#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
先天运气 → 疾病易感性 主动召回（P11 激活，不扩数据）

设计意图（对照 references/roadmap.md P11 与 references/research-2026-08-13.md §5）：
  asset33 的 earth/fire 等「体质·易感性」条目**存在但零查询**——根因是个人
  档案路径从未把「出生/胎孕运气」作为召回 key 喂给 asset33，而非缺数据。
  本模块把个人档案的先天运气（出生年岁运/司天/在泉 + 胎孕期运气）作为一等
  输入，主动召回 asset33 中按 岁运/司天/在泉/运气相合 维度的既有条目，并套用
  §5 文献映射规则产出「体质倾向」注释，使 earth/fire 维度在个人场景被主动召回。

重要边界：
  - 所有召回均来自 asset33 **既有条目**，本模块不新增任何知识库数据。
  - 所有「体质倾向」结论为**统计性/关联性**证据（见各条 source），非因果，
    不替代临床诊断。调用方须保留既有免责声明。
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional

KB_DIR = Path(__file__).parent.parent / "rag-knowledge-base"

# 岁运 code 前缀 → 五行（用于「土运防五脏病」之类按元素触发的规则）
_ELEMENT_OF_CODE = {
    "wood": "wood", "fire": "fire", "earth": "earth",
    "metal": "metal", "water": "water",
}


def _load_kb(filename: str) -> list:
    p = KB_DIR / filename
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf-8")).get("entries", [])


def _element_of_suiyun(code: str) -> str:
    """从岁运 code（如 earth_deficient）提取五行元素。"""
    for prefix, elem in _ELEMENT_OF_CODE.items():
        if code.startswith(prefix):
            return elem
    return ""


# ─────────────────────────────────────────────────────────────────────────
# 1) asset33 主动召回（按 运气 key 列表）
# ─────────────────────────────────────────────────────────────────────────
def recall_disease_susceptibility(keys: List[str]) -> List[Dict]:
    """按给定 运气 key 列表主动召回 asset33 条目（去重，保留维度元信息）。

    keys 可含：岁运 code（fire_deficient / earth_excess …）、司天 key
    （jueyin_fengmu_sitian …）、在泉 key、司天_在泉 combo、运气相合 key
    （shunhua / tianfu …）。命中 rag_key ∈ keys 的条目全部返回。
    """
    if not keys:
        return []
    key_set = set(keys)
    ds_kb = _load_kb("asset33_disease_susceptibility.json")
    seen = set()
    results: List[Dict] = []
    for e in ds_kb:
        rag_key = e.get("rag_key", "")
        if rag_key in key_set and rag_key not in seen:
            seen.add(rag_key)
            results.append({
                "dimension": e.get("dimension", ""),
                "rag_key": rag_key,
                "susceptible_diseases": e.get("susceptible_diseases", []),
                "susceptibility_direction": e.get("susceptibility_direction", ""),
                "pathogenesis": e.get("pathogenesis", ""),
                "regulation_direction": e.get("regulation_direction", ""),
                "evidence": e.get("evidence", ""),
                "source": e.get("source", ""),
            })
    return results


# ─────────────────────────────────────────────────────────────────────────
# 2) §5 文献映射规则：运气组合 → 体质倾向（编码进推理，非数据扩写）
# ─────────────────────────────────────────────────────────────────────────
# 每条 when 条件命中「出生 或 胎孕」任一处运气即触发；trigger_keys 仅作可读提示。
CONSTITUTION_TENDENCY_RULES: List[Dict] = [
    {
        "name": "阳虚质倾向",
        "when": {"sitian_key": "jueyin_fengmu_sitian",
                 "zaiquan_key": "shaoyang_xianghuo_zaiquan"},
        "note": "厥阴风木司天 + 少阳相火在泉之年（上一年寒湿主令）→ 先天易感寒湿伤阳，"
                "阳虚质形成倾向增加。",
        "source": "research-2026-08-13 §5.1（韩玲等：胚胎期前 3 个月所禀运气影响体质形成）",
        "trigger_keys": ["jueyin_fengmu_sitian", "shaoyang_xianghuo_zaiquan"],
    },
    {
        "name": "阴虚质倾向",
        "when": {"suiyun_code": "fire_deficient",
                 "sitian_key": "yangming_zaojin_sitian"},
        "note": "岁运火运不及 + 阳明燥金司天 → 先天阴虚形成率增加"
                "（兼见少阴君火在泉、二之气主气时更显）。",
        "source": "research-2026-08-13 §5.1（阴虚质：岁运火运不及+阳明燥金司天/少阴君火在泉+二之气主气）",
        "trigger_keys": ["fire_deficient", "yangming_zaojin_sitian"],
    },
    {
        "name": "土运防五脏病",
        "when": {"suiyun_element": "earth"},
        "note": "土运之年（太过/不及）出生者，先天及发病运气中「土」多次出现，"
                "注意防五脏病（脾土为先）。",
        "source": "research-2026-08-13 §5.1（张轩等：先天五运六气源自「土」者后天易罹五脏病）",
        "trigger_keys": ["earth_excess", "earth_deficient"],
    },
]


def _luck_matches(luck: Dict, cond: Dict) -> bool:
    """判断某处运气（birth/fetal）是否满足规则 when 条件。"""
    if "suiyun_element" in cond:
        if _element_of_suiyun(luck.get("suiyun_code", "")) != cond["suiyun_element"]:
            return False
    if "suiyun_code" in cond:
        if luck.get("suiyun_code") != cond["suiyun_code"]:
            return False
    if "sitian_key" in cond:
        if luck.get("sitian_key") != cond["sitian_key"]:
            return False
    if "zaiquan_key" in cond:
        if luck.get("zaiquan_key") != cond["zaiquan_key"]:
            return False
    return True


def eval_constitution_tendency(congenital: Dict) -> List[Dict]:
    """对先天运气（出生+胎孕）套用 §5 规则，返回命中的体质倾向注释列表。

    congenital 形如 compute_congenital_yunqi 的返回值：
        {"birth": {suiyun_code, sitian_key, zaiquan_key, ...},
         "fetal": {suiyun_code, sitian_key, zaiquan_key, ...}}
    命中点（出生或胎孕任一满足）即触发；返回去重后的规则（含 name/note/source）。
    """
    luck_points = [congenital.get("birth", {}), congenital.get("fetal", {})]
    matched: List[Dict] = []
    for rule in CONSTITUTION_TENDENCY_RULES:
        cond = rule.get("when", {})
        if any(_luck_matches(lp, cond) for lp in luck_points):
            matched.append({
                "name": rule.get("name", ""),
                "note": rule.get("note", ""),
                "source": rule.get("source", ""),
            })
    return matched


# ─────────────────────────────────────────────────────────────────────────
# 3) 先天运气计算：出生年 + 胎孕期运气（权重参考「胎孕期前 3 个月」）
# ─────────────────────────────────────────────────────────────────────────
def _build_key_maps():
    """返回 (司天名→sitian_key, 在泉名→zaiquan_key) 两张独立映射表。

    注意：少阳相火等既可作司天也可作在泉，必须用两张表分别查，
    否则在泉名会被错映射到「作司天时」的 zaiquan_key。
    """
    kb = _load_kb("asset2_sitian_zaiquan.json")
    sitian_map: Dict[str, str] = {}
    zaiquan_map: Dict[str, str] = {}
    for e in kb:
        st = e.get("sitian")
        zq = e.get("zaiquan")
        if st:
            sitian_map[st] = e.get("sitian_key", "")
        if zq:
            zaiquan_map[zq] = e.get("zaiquan_key", "")
    return sitian_map, zaiquan_map


_SITIAN_MAP = None
_ZAIQUAN_MAP = None


def _luck_from_yunqi(yq: Dict) -> Dict:
    """从 calculate_yunqi_api 的输出抽取先天运气关键字段 + 司天/在泉 key。"""
    global _SITIAN_MAP, _ZAIQUAN_MAP
    if _SITIAN_MAP is None:
        _SITIAN_MAP, _ZAIQUAN_MAP = _build_key_maps()
    sitian_name = yq.get("si_tian", "")
    zaiquan_name = yq.get("zai_quan", "")
    sitian_key = _SITIAN_MAP.get(sitian_name, "")
    zaiquan_key = _ZAIQUAN_MAP.get(zaiquan_name, "")
    sui = yq.get("sui_yun", {})
    return {
        "yunqi_year": yq.get("yunqi_year", ""),
        "suiyun_code": sui.get("code", ""),
        "suiyun_name": sui.get("name", ""),
        "sitian_name": sitian_name,
        "zaiquan_name": zaiquan_name,
        "sitian_key": sitian_key,
        "zaiquan_key": zaiquan_key,
        "sitian_zaiquan_key": f"{sitian_key}_{zaiquan_key}" if (sitian_key and zaiquan_key) else "",
    }


def compute_congenital_yunqi(birth_date: str) -> Dict:
    """计算先天运气：出生年运气 + 胎孕期运气。

    胎孕期以受孕日 ≈ 出生日 - 280 天估算；「胎孕期前 3 个月」约为
    出生日 - 280 ~ -190 天，是体质形成权重最高的窗口（§5.1 韩玲等）。
    这里以受孕日运气代表胎孕期运气（与出生年运气可不同，从而扩大召回覆盖）。
    """
    from calculate_yunqi_api import calculate_yunqi_api  # 延迟 import，避免循环依赖

    b = date.fromisoformat(birth_date)
    yq_birth = calculate_yunqi_api(birth_date)
    birth = _luck_from_yunqi(yq_birth)

    conception = b - timedelta(days=280)
    yq_fetal = calculate_yunqi_api(conception.isoformat())
    fetal = _luck_from_yunqi(yq_fetal)

    return {
        "birth": birth,
        "fetal": fetal,
        "fetal_reference": conception.isoformat(),
        "note": "胎孕期运气以受孕日（出生日-280天）估算；胎孕期前3个月为体质形成权重最高窗口。",
    }


def congenital_recall_keys(congenital: Dict) -> List[str]:
    """从先天运气中提取用于 asset33 召回的全部 key（去重）。"""
    keys: List[str] = []
    for lp in (congenital.get("birth", {}), congenital.get("fetal", {})):
        for k in (lp.get("suiyun_code"), lp.get("sitian_key"),
                  lp.get("zaiquan_key"), lp.get("sitian_zaiquan_key")):
            if k and k not in keys:
                keys.append(k)
    return keys


def congenital_susceptibility(birth_date: str) -> Dict:
    """一站式：算先天运气 → 召回 asset33 → 套用 §5 体质倾向规则。

    返回 {"congenital": ..., "recall_keys": ..., "susceptibility": [...],
           "tendency": [...]}。供 personal_yunqi_profile / cases_routing 直接消费。
    """
    congenital = compute_congenital_yunqi(birth_date)
    keys = congenital_recall_keys(congenital)
    susc = recall_disease_susceptibility(keys)
    tendency = eval_constitution_tendency(congenital)
    return {
        "congenital": congenital,
        "recall_keys": keys,
        "susceptibility": susc,
        "tendency": tendency,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        prog='yunqi_susceptibility.py',
        description='计算先天运气·疾病易感性（出生 + 胎孕 -280d），主动召回 asset33。')
    parser.add_argument('birth_date', nargs='?', help='出生日期 YYYY-MM-DD')
    parser.add_argument('--year', help='仅给出生年份（如 1980），将用年中代表日期 1980-06-15')
    args = parser.parse_args()
    if args.year and not args.birth_date:
        bd = f"{args.year}-06-15"
    elif args.birth_date:
        bd = args.birth_date
    else:
        parser.print_help()
        sys.exit(1)
    out = congenital_susceptibility(bd)
    print(json.dumps(out, ensure_ascii=False, indent=2))
