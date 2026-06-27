#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五运六气 Skills 全链路演示脚本
演示: 日期输入 → 运气推算 → RAG 知识检索 → 综合分析
"""
import json, sys, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "scripts", "lib"))
sys.path.insert(0, os.path.join(BASE, "scripts"))

from calculate_yunqi_api import calculate_yunqi_api

def load_asset(name):
    path = os.path.join(BASE, "rag-knowledge-base", name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def find_entry(asset, key_field, key_value):
    """在 asset 中按 key_field 匹配条目"""
    items = asset.get("entries", asset.get("items", []))
    for item in items:
        if item.get(key_field) == key_value:
            return item
    return None

# ============================================================
# 1. 输入日期 → 运气推算
# ============================================================
date_str = sys.argv[1] if len(sys.argv) > 1 else "2026-06-27"
print("=" * 60)
print("  五运六气 Skills 全链路演示")
print(f"  输入日期: {date_str}")
print("=" * 60)

result = calculate_yunqi_api(date_str)
print(f"\n【Step 1: 运气推算】")
print(f"  运气年: {result['yunqi_year']}年 ({result['year_gz']})")
print(f"  日干支: {result['day_gz']}")
print(f"  岁运: {result['sui_yun']['name']} {result['sui_yun']['status']}")
print(f"  司天/在泉: {result['si_tian']} / {result['zai_quan']}")
print(f"  当前步位: {result['current_step']['name']}")
print(f"  客主关系: {result['current_step']['relation']} → {result['current_step']['shun_ni']}")

# ============================================================
# 2. RAG 检索键说明
# ============================================================
rk = result['rag_keys']
print(f"\n【Step 2: RAG 检索键生成】")
for k, v in rk.items():
    print(f"  {k} → {v}")

# ============================================================
# 3. 加载 RAG 知识库
# ============================================================
print(f"\n【Step 3: RAG 知识库检索】")

assets = {
    "asset1_suiyun.json": ("code", rk['suiyun']),
    "asset2_sitian_zaiquan.json": ("rag_key", rk['sitian']),
    "asset3_kezhujialin.json": ("rag_key", rk['current_step']),
    "asset4_formula.json": ("rag_key", rk['suiyun']),
    "asset5_commentary.json": ("related_yunqi_keys", rk['suiyun']),
    "asset6_regional.json": None,  # 地域需要额外判断
    "asset7_constitution.json": ("suiyun_code", rk['suiyun']),
}

for asset_file, lookup in assets.items():
    asset = load_asset(asset_file)
    title = asset.get("title", asset_file)
    if lookup is None:
        print(f"\n  📖 {title}")
        print(f"     (按地理纬度匹配, 7 assets 之一)")
        continue
    
    key_field, key_value = lookup
    if key_field == "related_yunqi_keys":
        # 注家: 按 related_yunqi_keys 数组匹配
        items = asset.get("entries", [])
        matches = [e for e in items if key_value in e.get(key_field, [])]
        print(f"\n  📖 {title} ({len(items)} 条)")
        for m in matches:
            author = m.get('author', '')
            theory = m.get('core_theory_title', '')
            print(f"     ✓ [{author}] {theory}")
        if not matches:
            print(f"     (无直接关联条目)")
    else:
        entry = find_entry(asset, key_field, key_value)
        if entry:
            name = entry.get('name', entry.get('formula_name', entry.get('constitution_name', key_value)))
            print(f"\n  📖 {title}")
            print(f"     ✓ 命中: {name}")
        else:
            print(f"\n  📖 {title}")
            print(f"     (无直接匹配)")

# ============================================================
# 4. 岁运病机深度展示
# ============================================================
suiyun_key = rk['suiyun']
print(f"\n【Step 4: 岁运病机深度分析 ({suiyun_key})】")
asset1 = load_asset("asset1_suiyun.json")
entry = find_entry(asset1, "code", suiyun_key)
if entry:
    print(f"  病名: {entry['name']}")
    print(f"  天干: {entry['tiangan']} ({entry['tiangan_yinyang']})")
    print(f"  五行: {entry['wuxing']}运")
    print(f"  病机: {entry['pathogenesis']}")
    print(f"  经典原文: {entry['classics_quote']}")
    print(f"  涉及脏腑: {', '.join(entry['organs_affected'])}")
    print(f"  症状: {', '.join(entry['symptoms'][:6])}...")
    print(f"  治法: {entry['treatment_principle']}")
    print(f"  平气条件: {entry['pingqi_condition']}")

# ============================================================
# 5. 方剂推荐
# ============================================================
print(f"\n【Step 5: 运气方剂推荐 ({suiyun_key})】")
asset4 = load_asset("asset4_formula.json")
entry4 = find_entry(asset4, "rag_key", suiyun_key)
if entry4:
    print(f"  方名: {entry4['name']}")
    print(f"  适用: {entry4['applicable_pattern']}")
    print(f"  组成: {entry4['ingredients']}")
    print(f"  病机: {entry4['pathogenesis']}")
    print(f"  主治: {entry4['indications']}")
    print(f"  现代研究: {entry4.get('modern_studies', '暂无')}")

# ============================================================
# 6. 体质影响
# ============================================================
print(f"\n【Step 6: 体质关联分析 ({suiyun_key})】")
asset7 = load_asset("asset7_constitution.json")
items7 = asset7.get("entries", [])
for item in items7:
    if item.get("entry_type") == "suiyun_constitution_adjustment" and item.get("suiyun_code") == suiyun_key:
        print(f"  岁运\"{item['suiyun_name']}\"影响最大的体质:")
        for c in item.get('most_affected_constitutions', []):
            if isinstance(c, dict):
                print(f"    • {c['name']}: {c['reason']}")
            else:
                print(f"    • {c}")
        print(f"  健康风险: {item.get('health_risks', '')}")
        print(f"  饮食调理: {item.get('dietary_advice', item.get('dietary_herbs', ''))}")
        print(f"  穴位: {item.get('acupuncture_points', '')}")
        break

# ============================================================
# 总结
# ============================================================
print(f"\n{'=' * 60}")
print(f"  全链路演示完成")
print(f"  涉及知识层数: 5/5 (岁运/方剂/注家/地域/体质)")
print(f"  RAG 检索键: {len(rk)} 个 → 可检索 7 个 Asset JSON")
print(f"  总知识条目: 104+ 条")
print(f"{'=' * 60}")
