#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OPT-05 医案关联图谱

按证型标签关联同类医案，支持：
  1. 同证型跨医家对比（如"孙一奎 vs 叶天士 治湿热"）
  2. 按药味关联（哪些医案共用同一方/同一药）
  3. 生成 case_relations.json 供 agent 检索

用法:
  python scripts/case_relations.py --build              # 构建 case_relations.json
  python scripts/case_relations.py --compare 孙一奎,叶天士 --tag 湿热
  python scripts/case_relations.py --compare 孙一奎,程文囿 --tag 中风
  python scripts/case_relations.py --related swy_174    # 查找相似医案
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from html import escape

SCRIPT_DIR = Path(__file__).parent
KB = SCRIPT_DIR.parent / "rag-knowledge-base"
RELATIONS_FILE = KB / "case_relations.json"


def load_all_cases():
    """加载全部医案。"""
    cases = []
    for f in sorted(KB.glob("asset*_*.json")):
        if "schema" in f.name:
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        if d.get("asset_type") != "case_library":
            continue
        aid = d.get("asset_id", "")
        aname = d.get("asset_name", "")
        for e in d.get("entries", []):
            cid = e.get("case_id") or e.get("entry_id", "")
            cases.append({
                "asset_id": aid,
                "asset_name": aname,
                "case_id": cid,
                "category": e.get("category", ""),
                "physician": e.get("physician", ""),
                "name": e.get("name", ""),
                "herbs": e.get("herbs", []),
                "formulas_referenced": e.get("formulas_referenced", []),
                "syndrome": e.get("syndrome", ""),
                "treatment": e.get("treatment", ""),
                "source_quote": e.get("source_quote", ""),
            })
    return cases


def build_relations(cases):
    """构建关联图谱 JSON。"""
    # 1. 按证型分组
    by_category = defaultdict(list)
    for c in cases:
        if c["category"]:
            by_category[c["category"]].append({
                "asset_id": c["asset_id"],
                "case_id": c["case_id"],
                "physician": c["physician"],
                "name": c["name"],
                "herbs": c["herbs"][:10],
                "formulas": c["formulas_referenced"][:5],
            })

    # 2. 按医家分组
    by_physician = defaultdict(list)
    for c in cases:
        if c["physician"]:
            by_physician[c["physician"]].append({
                "asset_id": c["asset_id"],
                "case_id": c["case_id"],
                "category": c["category"],
                "name": c["name"],
            })

    # 3. 按药味分组（共享同药味的医案）
    by_herb = defaultdict(list)
    for c in cases:
        for h in c["herbs"][:15]:
            by_herb[h].append({
                "asset_id": c["asset_id"],
                "case_id": c["case_id"],
                "physician": c["physician"],
                "category": c["category"],
                "name": c["name"],
            })

    # 4. 按方剂引用分组
    by_formula = defaultdict(list)
    for c in cases:
        for f in c["formulas_referenced"]:
            by_formula[f].append({
                "asset_id": c["asset_id"],
                "case_id": c["case_id"],
                "physician": c["physician"],
                "category": c["category"],
                "name": c["name"],
            })

    # 5. 跨医家同证型（有对比价值的）
    cross_compare = []
    for cat, items in by_category.items():
        phys_set = set(i["physician"] for i in items if i["physician"])
        if len(phys_set) >= 2 and len(items) >= 5:
            cross_compare.append({
                "category": cat,
                "total": len(items),
                "physicians": sorted(phys_set),
                "physician_count": len(phys_set),
                "cases": items,
            })
    cross_compare.sort(key=lambda x: (-x["physician_count"], -x["total"]))

    return {
        "total_cases": len(cases),
        "total_categories": len(by_category),
        "total_physicians": len(by_physician),
        "total_herbs": len(by_herb),
        "total_formulas": len(by_formula),
        "by_category": dict(by_category),
        "by_physician": dict(by_physician),
        "by_herb": dict(by_herb),
        "by_formula": dict(by_formula),
        "cross_compare": cross_compare,
    }


def cmd_build():
    """构建 case_relations.json。"""
    cases = load_all_cases()
    rel = build_relations(cases)
    RELATIONS_FILE.write_text(json.dumps(rel, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ 已生成: {RELATIONS_FILE} ({RELATIONS_FILE.stat().st_size // 1024}KB)")
    print(f"   医案: {rel['total_cases']} 条")
    print(f"   证型: {rel['total_categories']} 类")
    print(f"   医家: {rel['total_physicians']} 位")
    print(f"   药味: {rel['total_herbs']} 味")
    print(f"   方剂: {rel['total_formulas']} 首")
    print(f"   可对比证型: {len(rel['cross_compare'])} 类")


# 轻量免责声明：仅追加在「人类可读」医案对比/相似检索输出末尾。
CASE_DISCLAIMER = (
    "\n⚠️ 以上医案与方药信息仅供学习参考。涉及临床辨证、方药使用，"
    "须由执业中医师四诊合参、辨证论治，本工具不提供医疗建议。"
)


def cmd_compare(physicians, tag):
    """对比检索：跨医家同证型。"""
    if not RELATIONS_FILE.exists():
        print("请先运行 --build 构建 case_relations.json")
        return 1

    rel = json.loads(RELATIONS_FILE.read_text(encoding="utf-8"))
    by_cat = rel.get("by_category", {})

    if tag not in by_cat:
        print(f"未找到证型「{tag}」")
        print(f"可用证型: {', '.join(sorted(by_cat.keys())[:30])}...")
        return 1

    cases = by_cat[tag]
    phys_list = [p.strip() for p in physicians.split(",")]

    print(f"\n{'='*60}")
    print(f"证型「{tag}」跨医家对比（共 {len(cases)} 条）")
    print(f"{'='*60}")

    for phys in phys_list:
        matched = [c for c in cases if phys in c.get("physician", "")]
        print(f"\n【{phys}】({len(matched)} 条)")
        for c in matched[:8]:
            herbs_str = ", ".join(c.get("herbs", [])[:6])
            formulas_str = ", ".join(c.get("formulas", [])[:3])
            print(f"  {c['case_id']} | {c['name']}")
            if herbs_str:
                print(f"    药味: {herbs_str}")
            if formulas_str:
                print(f"    方剂: {formulas_str}")

    print(CASE_DISCLAIMER)
    return 0


def cmd_related(case_id):
    """查找与指定医案相似的其他医案。"""
    if not RELATIONS_FILE.exists():
        print("请先运行 --build 构建 case_relations.json")
        return 1

    rel = json.loads(RELATIONS_FILE.read_text(encoding="utf-8"))
    cases = load_all_cases()
    target = None
    for c in cases:
        if c["case_id"] == case_id:
            target = c
            break

    if not target:
        print(f"未找到医案 {case_id}")
        return 1

    print(f"\n{'='*60}")
    print(f"与 {case_id}（{target['name']}）相似的医案")
    print(f"{'='*60}")
    print(f"\n目标医案: {target['case_id']} | {target['category']} | {target['physician']}")
    print(f"药味: {', '.join(target['herbs'][:10])}")
    print(f"方剂: {', '.join(target['formulas_referenced'][:5])}")

    # 按证型找同类
    if target["category"]:
        same_cat = rel.get("by_category", {}).get(target["category"], [])
        others = [c for c in same_cat if c["case_id"] != case_id and c.get("physician") != target["physician"]]
        print(f"\n【同证型「{target['category']}」其他医家】({len(others)} 条)")
        for c in others[:8]:
            print(f"  {c['case_id']} | {c.get('physician','')} | {c['name']}")

    # 按共享药味找
    if target["herbs"]:
        print(f"\n【共享药味的医案】")
        by_herb = rel.get("by_herb", {})
        shared = set()
        for h in target["herbs"][:5]:
            for c in by_herb.get(h, []):
                if c["case_id"] != case_id and c.get("physician") != target["physician"]:
                    shared.add((c["case_id"], c.get("physician", ""), c.get("category", ""), c.get("name", "")))
        for cid, phys, cat, name in list(shared)[:8]:
            print(f"  {cid} | {phys} | {cat} | {name}")

    # 按共享方剂找
    if target["formulas_referenced"]:
        print(f"\n【共享方剂的医案】")
        by_formula = rel.get("by_formula", {})
        shared_f = set()
        for f in target["formulas_referenced"]:
            for c in by_formula.get(f, []):
                if c["case_id"] != case_id and c.get("physician") != target["physician"]:
                    shared_f.add((c["case_id"], c.get("physician", ""), c.get("category", ""), c.get("name", ""), f))
        for cid, phys, cat, name, formula in list(shared_f)[:8]:
            print(f"  {cid} | {phys} | {cat} | {name} (共引{formula})")

    print(CASE_DISCLAIMER)
    return 0


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description="OPT-05 医案关联图谱")
    parser.add_argument("--build", action="store_true", help="构建 case_relations.json")
    parser.add_argument("--compare", help="对比检索，如 --compare 孙一奎,叶天士 --tag 湿热")
    parser.add_argument("--tag", help="对比的证型标签")
    parser.add_argument("--related", help="查找与指定 case_id 相似的医案")
    args = parser.parse_args(argv if argv is not None else None)

    if args.build:
        cmd_build()
        return 0
    elif args.compare:
        return cmd_compare(args.compare, args.tag or "")
    elif args.related:
        return cmd_related(args.related)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
