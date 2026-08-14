#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医案库渐进加载路由哨兵（P1-3：按需渐进加载薄索引）

把 `rag-knowledge-base/yunqi_medical_cases_guide.md` 的病证→医案库路由表
固化为可编程的「薄索引」，让 Agent 在检索前先问本脚本拿到候选库清单，
再**只加载命中的医案库**，避免一次性把 22 部医案库(asset9/11-32)整包撑进上下文。

设计原则（对齐项目现有轻量/零依赖路线）：
  - 自包含：数据内置为 Python 常量，零外部依赖、零模型、可离线跑。
  - 确定性：`--syndrome` / `--rag-key` 给出明确的首选库/补充库，Agent 可解析。
  - 渐进：先给清单 → Agent 只开相关库 recheck → 满足才进库，不满足再开补充库。

一致性基线：本脚本数据源自 `yunqi_medical_cases_guide.md`（二手精炼键值，
回答「该查哪个库」）；guide 是完整笔记（可 Grep 定位原文/病机/注家）。
若增删库或病证路由，须同步改 guide 与本文件两处。

用法：
    python scripts/cases_routing.py --list-assets
    python scripts/cases_routing.py --syndrome 湿温
    python scripts/cases_routing.py --rag-key water_excess
    python scripts/cases_routing.py --syndrome 霍乱 --json
    python scripts/cases_routing.py --rag-key shaoyin_junhuo_sitian --json --force-load
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Dict, List

# ── 医案库速查（库 → (条数, 特色)）──
ASSETS: Dict[str, Dict[str, str]] = {
    "asset9":  {"count": "60",  "note": "圣济岁图，按 rag_key 检索；与推算直接对接"},
    "asset11": {"count": "102", "note": "名医类案（明·江瓘）历代名医验案汇编"},
    "asset12": {"count": "84",  "note": "续名医类案（清·魏之琇）名医案补充"},
    "asset13": {"count": "159", "note": "古今医案按（清·俞震）伤寒/痢疾/血症，含震按辨证"},
    "asset14": {"count": "177", "note": "丁甘仁医案 温病/内科，孟河医派"},
    "asset15": {"count": "49",  "note": "伤寒九十论（宋·许叔微）伤寒经方专库"},
    "asset16": {"count": "330", "note": "临证指南（清·叶桂）内科杂病最全，首选"},
    "asset17": {"count": "34",  "note": "松峰说疫·运气瘟疫，唯一按 rag_key 命中的医案库"},
    "asset18": {"count": "40",  "note": "回春录（王孟英）湿热温病"},
    "asset19": {"count": "138", "note": "张聿青医案 湿温伏暑、痰饮肝风"},
    "asset20": {"count": "120", "note": "吴鞠通医案 温病三焦辨证"},
    "asset21": {"count": "17",  "note": "寓意草（喻嘉言）议病式、伤寒危证、误治救逆"},
    "asset22": {"count": "23",  "note": "洄溪医案（徐灵胎）经方辨证、外科痈疽"},
    "asset23": {"count": "20",  "note": "花韵楼医案（顾德华·女医）妇科专库"},
    "asset24": {"count": "14",  "note": "诊余举隅录（陈廷儒）辨证法度"},
    "asset25": {"count": "15",  "note": "许氏医案（许恩普）验舌辨真、误治救逆、胎产"},
    "asset26": {"count": "14",  "note": "杏轩医案（程文囿·新安派）寒热真假、格阳证"},
    "asset27": {"count": "390", "note": "孙文垣医案（孙一奎）温补命门、大头疫、目疾"},
    "asset28": {"count": "8",   "note": "丛桂草堂医案（袁焯）痰饮闭塞、喉痧阴亏"},
    "asset29": {"count": "70",  "note": "外科正宗·外用（陈实功）痈疽疔疮外治"},
    "asset30": {"count": "108", "note": "立斋外科发挥（薛己）痈疽以气血为本"},
    "asset31": {"count": "64",  "note": "醉花窗医案（王堉）脉证互参、阴虚实热鉴别"},
    "asset32": {"count": "12",  "note": "医验随笔（沈奉江）温病痰喘、温毒发痘"},
}

# ── 病证 → (首选库列表, 补充库列表) ──
# 源：yunqi_medical_cases_guide.md 第二节「病证 → 首选医案库路由表」。
SYNDROME_ROUTE: Dict[str, Dict[str, List[str]]] = {
    # 外感时行
    "伤寒":  {"primary": ["asset15"], "supp": ["asset22"]},
    "风温":  {"primary": ["asset18"], "supp": ["asset20", "asset24"]},
    "春温":  {"primary": ["asset18"], "supp": ["asset20", "asset24"]},
    "暑温":  {"primary": ["asset18"], "supp": ["asset20", "asset26"]},
    "湿温":  {"primary": ["asset18"], "supp": ["asset19", "asset20"]},
    "伏暑":  {"primary": ["asset18"], "supp": ["asset19", "asset20"]},
    "冬温":  {"primary": ["asset18"], "supp": ["asset20"]},
    "温疫":  {"primary": ["asset17"], "supp": ["asset18", "asset20", "asset27"]},
    "瘟疫":  {"primary": ["asset17"], "supp": ["asset18", "asset20", "asset27"]},
    "疟":    {"primary": ["asset13"], "supp": ["asset20", "asset25"]},
    "霍乱":  {"primary": ["asset18"], "supp": ["asset17", "asset24", "asset19"]},
    "痢疾":  {"primary": ["asset13"], "supp": ["asset21", "asset14", "asset24"]},
    "大头瘟":{"primary": ["asset26"], "supp": ["asset21"]},
    # 内科杂病
    "咳嗽":  {"primary": ["asset16"], "supp": ["asset13", "asset14", "asset22", "asset26", "asset28"]},
    "痰饮":  {"primary": ["asset16"], "supp": ["asset19", "asset20"]},
    "痰证":  {"primary": ["asset16"], "supp": ["asset19", "asset20"]},
    "吐血":  {"primary": ["asset13"], "supp": ["asset16", "asset21", "asset22"]},
    "血症":  {"primary": ["asset13"], "supp": ["asset16", "asset21", "asset22"]},
    "肝风":  {"primary": ["asset16"], "supp": ["asset19", "asset20"]},
    "眩晕":  {"primary": ["asset16"], "supp": ["asset19", "asset20"]},
    "胃脘痛":{"primary": ["asset16"], "supp": ["asset14", "asset22", "asset25"]},
    "水肿":  {"primary": ["asset16"], "supp": ["asset22", "asset26"]},
    "肿胀":  {"primary": ["asset16"], "supp": ["asset22", "asset26"]},
    "中风":  {"primary": ["asset16"], "supp": ["asset19", "asset20", "asset25", "asset26"]},
    "痹证":  {"primary": ["asset16"], "supp": ["asset20", "asset22"]},
    "泄泻":  {"primary": ["asset16"], "supp": ["asset18", "asset24"]},
    "消渴":  {"primary": ["asset16"], "supp": ["asset22"]},
    "淋浊":  {"primary": ["asset16"], "supp": ["asset22"]},
    "遗精":  {"primary": ["asset16"], "supp": ["asset26"]},
    "怔忡":  {"primary": ["asset16"], "supp": ["asset22", "asset23"]},
    "不寐":  {"primary": ["asset16"], "supp": ["asset22", "asset23"]},
    "头痛":  {"primary": ["asset16"], "supp": ["asset19", "asset20"]},
    "胁痛":  {"primary": ["asset16"], "supp": ["asset19", "asset20"]},
    "虫痛":  {"primary": ["asset22"], "supp": ["asset25"]},
    "脱肛":  {"primary": ["asset25"], "supp": []},
    "目疾":  {"primary": ["asset25"], "supp": []},
    # 妇产儿科
    "妇科":  {"primary": ["asset23"], "supp": ["asset11", "asset24"]},
    "崩漏":  {"primary": ["asset23"], "supp": ["asset11", "asset24"]},
    "月经":  {"primary": ["asset23"], "supp": ["asset11", "asset24"]},
    "带下":  {"primary": ["asset23"], "supp": ["asset11", "asset24"]},
    "产后":  {"primary": ["asset23"], "supp": ["asset18", "asset26", "asset22"]},
    "胎产":  {"primary": ["asset23"], "supp": ["asset25", "asset26"]},
    "妊娠":  {"primary": ["asset23"], "supp": ["asset25", "asset26"]},
    "惊风":  {"primary": ["asset24"], "supp": ["asset21"]},
    "痘疫":  {"primary": ["asset17"], "supp": ["asset18", "asset22"]},
    # 外科五官
    "痈疽":  {"primary": ["asset29"], "supp": ["asset22", "asset21"]},
    "喉痹":  {"primary": ["asset25"], "supp": ["asset20", "asset22", "asset28"]},
    "疔疮":  {"primary": ["asset29"], "supp": ["asset22"]},
    "脱疽":  {"primary": ["asset29"], "supp": ["asset22"]},
    "下疳":  {"primary": ["asset22"], "supp": []},
    "乳癖":  {"primary": ["asset23"], "supp": []},
}

# ── 运气 rag_key → (病证倾向, 推荐医案库) ──
# 源：guide 第五节「运气病机 → 病证翻译对照」。
RAGKEY_ROUTE: Dict[str, Dict[str, List[str]]] = {
    "wood_excess":           {"syndrome": "肝风/眩晕/头痛/胁痛", "assets": ["asset16", "asset19", "asset20"]},
    "fire_excess":           {"syndrome": "暑温/温热/血证/咳嗽", "assets": ["asset18", "asset20"]},
    "earth_excess":          {"syndrome": "湿温/泄泻/霍乱/肿胀/痰饮", "assets": ["asset18", "asset19", "asset20"]},
    "metal_excess":          {"syndrome": "咳嗽/肺系/燥证", "assets": ["asset16", "asset22"]},
    "water_excess":          {"syndrome": "寒湿/霍乱/水肿/痹痛", "assets": ["asset17", "asset18", "asset24"]},
    "wood_deficient":        {"syndrome": "郁证/胁痛/脾胃", "assets": ["asset16", "asset19"]},
    "fire_deficient":        {"syndrome": "寒证/心悸", "assets": ["asset22", "asset26"]},
    "earth_deficient":       {"syndrome": "泄泻/脾胃/肝风", "assets": ["asset16", "asset19"]},
    "metal_deficient":       {"syndrome": "咳嗽/血证", "assets": ["asset16", "asset18"]},
    "water_deficient":       {"syndrome": "湿证/水肿", "assets": ["asset17", "asset19"]},
    "taiyin_shitu_sitian":   {"syndrome": "湿温/暑温/泄泻/痢疾", "assets": ["asset18", "asset19", "asset24"]},
    "shaoyin_junhuo_sitian": {"syndrome": "暑温/温热/血证", "assets": ["asset18", "asset20"]},
    "yangming_zaojin_sitian":{"syndrome": "燥咳/肺系", "assets": ["asset16", "asset22"]},
    "taiyang_hanshui_sitian":{"syndrome": "寒湿/痹痛", "assets": ["asset22", "asset24"]},
}

# 强制联动：高风险病证若命中，即使首选库无结果也必须读的额外库（对标 safety 强制联动）。
# key 为病证名；value 为强制追加库（保底检索，避免漏掉疫毒/外科急症）。
FORCE_LOAD_SYNDROMES: Dict[str, List[str]] = {
    "温疫": ["asset17", "asset18", "asset20"],
    "瘟疫": ["asset17", "asset18", "asset20"],
    "大头瘟": ["asset26", "asset21"],
    "痘疫": ["asset17"],
    "痈疽": ["asset29", "asset30"],
}


def _match_syndrome(query: str) -> List[str]:
    """在 SYNDROME_ROUTE 里做包含匹配，返回命中的病证 key 列表（含同义驱动的合并去重）。"""
    hits = []
    for key in SYNDROME_ROUTE:
        if query and (query in key or key in query):
            hits.append(key)
    return hits


def _unique(seq: List[str]) -> List[str]:
    seen: List[str] = []
    for x in seq:
        if x not in seen:
            seen.append(x)
    return seen


def route_syndrome(query: str) -> Dict:
    """按病证返回候选库（首选/补充/强制联动）。"""
    keys = _match_syndrome(query)
    primary: List[str] = []
    supp: List[str] = []
    force: List[str] = []
    matched = []
    for k in keys:
        matched.append(k)
        if k not in SYNDROME_ROUTE:
            continue
        primary.extend(SYNDROME_ROUTE[k]["primary"])
        supp.extend(SYNDROME_ROUTE[k]["supp"])
        if k in FORCE_LOAD_SYNDROMES:
            force.extend(FORCE_LOAD_SYNDROMES[k])
    return {
        "query": query,
        "matched_syndromes": _unique(matched),
        "primary_assets": _unique(primary),
        "supplement_assets": _unique([a for a in supp if a not in primary]),
        "force_load_assets": _unique([a for a in force if a not in primary]),
        "kind": "syndrome",
    }


def route_rag_key(key: str) -> Dict:
    """按运气 rag_key 返回（病证倾向 + 推荐库）。"""
    r = RAGKEY_ROUTE.get(key)
    if not r:
        return {"query": key, "matched_syndromes": [], "primary_assets": [],
                "supplement_assets": [], "force_load_assets": [], "kind": "rag_key",
                "error": f"未知 rag_key: {key}（可用: {list(RAGKEY_ROUTE)}）"}
    assets = list(r["assets"])
    primary = assets[:2]
    supp = assets[2:]
    return {
        "query": key,
        "rag_key": key,
        "syndrome_hint": r["syndrome"],
        "primary_assets": primary,
        "supplement_assets": supp,
        "force_load_assets": [],
        "kind": "rag_key",
    }


def list_assets() -> Dict:
    return {"assets": ASSETS, "kind": "list"}


def route_congenital(keys: List[str]) -> Dict:
    """「体质 → 易感性 → 病证」激活分支（P11）。

    按个人「先天运气」key（出生/胎孕 岁运·司天·在泉，来自 yunqi_susceptibility
    的 congenital_recall_keys）主动召回 asset33 易感性条目，并映射推荐医案库，
    使 asset33 的 earth/fire 等维度从「零查询」变为「按出生运气触发」。
    不新增任何知识库数据，仅做既有条目的关联路由。
    """
    from yunqi_susceptibility import recall_disease_susceptibility  # 延迟 import，避免循环依赖
    susc = recall_disease_susceptibility(keys)
    assets: List[str] = []
    for k in keys:
        if k in RAGKEY_ROUTE:
            assets.extend(RAGKEY_ROUTE[k]["assets"])
    return {
        "keys": keys,
        "susceptibility": susc,
        "primary_assets": _unique(assets[:2]),
        "supplement_assets": _unique([a for a in assets[2:] if a not in assets[:2]]),
        "force_load_assets": [],
        "kind": "congenital",
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="医案库渐进加载路由哨兵（P1-3 薄索引）")
    p.add_argument("--list-assets", action="store_true", help="列出全部医案库及特色")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--syndrome", help="病证名（如 湿温/霍乱/中风），返回首选+补充+强制库")
    g.add_argument("--rag-key", help="运气 rag_key（如 water_excess/shaoyin_junhuo_sitian），翻译成病证+库")
    g.add_argument("--congenital", help="先天运气 key 列表（逗号分隔，如 fire_deficient,yangming_zaojin_sitian），触发 asset33 易感性+医案库路由（P11 激活）")
    p.add_argument("--json", action="store_true", help="JSON 输出")
    p.add_argument("--force-load", action="store_true",
                   help="把常被忽略的大库（如 asset26/27/28/29/30）也纳入候选，供彻底检索")
    args = p.parse_args(argv)

    if args.list_assets:
        result = list_assets()
    elif args.syndrome:
        result = route_syndrome(args.syndrome)
    elif args.rag_key:
        result = route_rag_key(args.rag_key)
    elif args.congenital:
        keys = [k.strip() for k in args.congenital.split(",") if k.strip()]
        result = route_congenital(keys)
    else:
        p.print_help()
        return 2

    if args.force_load and isinstance(result.get("supplement_assets"), list):
        # 渐进封顶：强制联动时把大库也并入候选，避免首轮过窄。
        big = ["asset26", "asset27", "asset28", "asset29", "asset30"]
        result["supplement_assets"] = _unique(
            result["supplement_assets"] + [a for a in big if a not in result["primary_assets"]])

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        _print_human(result)
    return 0


def _print_human(r: Dict) -> None:
    q = r.get("query", "")
    if r.get("kind") == "list":
        print(f"医案库共 {len(r['assets'])} 个：")
        for name, info in r["assets"].items():
            print(f"  {name}: {info['count']}条 · {info['note']}")
        return
    print(f"查询: {q}")
    if r.get("error"):
        print(f"  ⚠️ {r['error']}")
        return
    if r.get("kind") == "congenital":
        print(f"  先天运气 key: {', '.join(r.get('keys', []))}")
        susc = r.get("susceptibility", [])
        if susc:
            print(f"  主动召回 asset33 易感性（{len(susc)} 条）:")
            for s in susc:
                diseases = '、'.join(s.get('susceptible_diseases', [])) or '—'
                print(f"    [{s['dimension']}·{s['rag_key']}] 易感: {diseases}")
        else:
            print("  asset33 中无直接对应条目。")
        print(f"  首选库: {', '.join(r['primary_assets']) or '—'}")
        print(f"  补充库: {', '.join(r['supplement_assets']) or '—'}")
        return
    if r.get("matched_syndromes"):
        print(f"  命中病证: {', '.join(r['matched_syndromes'])}")
    if r.get("rag_key"):
        print(f"  rag_key={r['rag_key']} → 病证倾向: {r.get('syndrome_hint','')}")
    print(f"  首选库: {', '.join(r['primary_assets']) or '—'}")
    print(f"  补充库: {', '.join(r['supplement_assets']) or '—'}")
    if r.get("force_load_assets"):
        print(f"  ⚠️ 强制联动库: {', '.join(r['force_load_assets'])}")
    # 给出可直接执行的 rag_search 命令
    all_hits = _unique(r["primary_assets"] + r["supplement_assets"])
    if all_hits:
        cmd = f"python scripts/rag_search.py {r.get('query','')} --asset " + ",".join(all_hits)
        print(f"\n  建议命令: {cmd}")


if __name__ == "__main__":
    sys.exit(main())