#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检索质量基准测试

从 2124 条医案中按病证类别构造 golden set，验证 rag_search 的检索质量。

指标：
  - recall@k：查询「某病证」时，前 k 条结果中有多少条属于该病证
  - 库覆盖率：查询命中的 asset 数量 / 总 asset 数量
  - 零命中率：返回 0 条结果的查询占比

用法：
    python scripts/eval_retrieval_quality.py
    python scripts/eval_retrieval_quality.py --json
    python scripts/eval_retrieval_quality.py --limit 20  # 减少抽样数

设计原则：
    - golden set 从真实医案库抽样，不用人造数据
    - 查询词用病证名（category 字段），这是用户最自然的查询方式
    - 每个病证取前 N 条作为 golden，验证 recall@k
"""

import argparse
import json
import sys
import os
import glob
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag_search import search, lookup_key


# ═══════════════════════════════════════════════════════════════
# Golden set 构造
# ═══════════════════════════════════════════════════════════════

RAG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rag-knowledge-base')

# 高频病证（>=15 条），用于构造 golden set
MIN_CATEGORY_COUNT = 15
# 每个病证抽样条数（作为 golden set）
SAMPLES_PER_CATEGORY = 5
# recall@k 的 k 值
K_VALUES = [5, 10, 20]


def load_all_cases():
    """加载所有医案库，返回 [(asset_id, entry), ...]"""
    cases = []
    for f in sorted(glob.glob(os.path.join(RAG_DIR, 'asset*_cases.json'))):
        asset_id = os.path.basename(f).replace('.json', '')
        d = json.load(open(f, encoding='utf-8'))
        for e in d.get('entries', []):
            cases.append((asset_id, e))
    return cases


def build_golden_set(cases):
    """按病证类别构造 golden set

    返回：{category: [(asset_id, entry, case_id), ...]}
    """
    by_category = defaultdict(list)
    for asset_id, e in cases:
        cat = e.get('category', '').strip()
        if cat:
            by_category[cat].append((asset_id, e, e.get('case_id', e.get('entry_id', ''))))

    # 只保留 >= MIN_CATEGORY_COUNT 条的病证
    golden = {}
    for cat, items in by_category.items():
        if len(items) >= MIN_CATEGORY_COUNT:
            # 取前 SAMPLES_PER_CATEGORY 条作为 golden
            golden[cat] = items[:SAMPLES_PER_CATEGORY]

    return golden


# ═══════════════════════════════════════════════════════════════
# 检索质量评估
# ═══════════════════════════════════════════════════════════════

def evaluate_recall(golden_set, k_values):
    """
    对每个病证类别，用病证名作为查询词，验证 recall@k。

    recall@k = (前 k 条结果中属于该病证的条数) / min(k, golden_set 大小)
    """
    results = []

    for category, golden_items in golden_set.items():
        # 用病证名作为查询词
        hits = search([category], limit=max(k_values))

        # 从 hit 的 title 中提取 case_id（格式如 "xumingyi_050 咳嗽"）
        hit_case_ids = set()
        hit_assets = set()
        for h in hits:
            hid = h.get('id', '')
            title = h.get('title', '')
            # title 格式: "case_id category" 或 "category"
            # 尝试从 title 提取 case_id
            parts = title.split()
            for p in parts:
                if '_' in p and p != category:
                    hit_case_ids.add(p)
            # 也加入原始 id
            hit_case_ids.add(hid)
            hit_assets.add(h.get('asset', ''))

        # golden set 的 case_id
        golden_ids = set(item[2] for item in golden_items)

        # 计算 recall@k
        recalls = {}
        for k in k_values:
            top_k_ids = set()
            for h in hits[:k]:
                hid = h.get('id', '')
                title = h.get('title', '')
                parts = title.split()
                for p in parts:
                    if '_' in p and p != category:
                        top_k_ids.add(p)
                top_k_ids.add(hid)
            # 命中的 golden 条目数
            hit_count = len(top_k_ids & golden_ids)
            # recall = 命中数 / golden 总数
            recalls[f'recall@{k}'] = hit_count / len(golden_ids) if golden_ids else 0

        # 库覆盖率
        asset_coverage = len(hit_assets)

        results.append({
            'category': category,
            'golden_count': len(golden_items),
            'total_hits': len(hits),
            'asset_coverage': asset_coverage,
            'hit_assets': sorted(hit_assets),
            **recalls,
        })

    return results


def evaluate_field_search(golden_set):
    """
    按字段检索质量：用 herbs 字段验证能否召回含该药味的医案。
    """
    # 从 golden set 中提取高频药味
    herb_counts = defaultdict(int)
    for _, items in golden_set.items():
        for _, e, _ in items:
            for h in e.get('herbs', []):
                herb_counts[h] += 1

    # 取 Top 10 高频药味测试
    top_herbs = sorted(herb_counts.items(), key=lambda x: -x[1])[:10]

    results = []
    for herb, expected_count in top_herbs:
        # 用 --field herbs 检索
        hits = search([], assets=None, limit=50)
        # 这里简化：用关键词检索药味名
        herb_hits = search([herb], limit=20)
        actual_count = len(herb_hits)

        results.append({
            'herb': herb,
            'expected_in_golden': expected_count,
            'actual_hits': actual_count,
            'hit': actual_count > 0,
        })

    return results


def evaluate_exact_key():
    """
    精确 key 检索质量：验证推算引擎输出的 rag_key 能否命中知识库。
    """
    # 测试所有岁运 code
    suiyun_codes = [
        'wood_excess', 'wood_deficient', 'fire_excess', 'fire_deficient',
        'earth_excess', 'earth_deficient', 'metal_excess', 'metal_deficient',
        'water_excess', 'water_deficient',
    ]
    sitian_keys = [
        'jueyin_fengmu_sitian', 'shaoyin_junhuo_sitian', 'taiyin_shitu_sitian',
        'shaoyang_xianghuo_sitian', 'yangming_zaojin_sitian', 'taiyang_hanshui_sitian',
    ]

    results = []
    for key in suiyun_codes + sitian_keys:
        hits = lookup_key(key)
        results.append({
            'key': key,
            'hit_count': len(hits),
            'hit': len(hits) > 0,
        })

    return results


# ═══════════════════════════════════════════════════════════════
# 汇总报告
# ═══════════════════════════════════════════════════════════════

def run_evaluation(limit=None):
    """运行完整评估"""
    cases = load_all_cases()
    golden = build_golden_set(cases)

    if limit:
        # 限制测试的病证数量
        golden = dict(list(golden.items())[:limit])

    # 1. 关键词检索 recall@k
    recall_results = evaluate_recall(golden, K_VALUES)

    # 2. 按字段检索
    field_results = evaluate_field_search(golden)

    # 3. 精确 key 检索
    key_results = evaluate_exact_key()

    # 汇总指标
    total_queries = len(recall_results)
    zero_hit_queries = sum(1 for r in recall_results if r['total_hits'] == 0)

    avg_recall = {}
    for k in K_VALUES:
        key = f'recall@{k}'
        vals = [r[key] for r in recall_results if r['total_hits'] > 0]
        avg_recall[key] = sum(vals) / len(vals) if vals else 0

    avg_asset_coverage = sum(r['asset_coverage'] for r in recall_results) / total_queries if total_queries else 0

    # 精确 key 命中率
    key_total = len(key_results)
    key_hit = sum(1 for r in key_results if r['hit'])

    # 字段检索命中率
    field_total = len(field_results)
    field_hit = sum(1 for r in field_results if r['hit'])

    return {
        'summary': {
            'total_cases': len(cases),
            'total_categories': len(golden),
            'total_queries': total_queries,
            'zero_hit_queries': zero_hit_queries,
            'zero_hit_rate': zero_hit_queries / total_queries if total_queries else 0,
            **{f'avg_{k}': v for k, v in avg_recall.items()},
            'avg_asset_coverage': round(avg_asset_coverage, 1),
            'exact_key_total': key_total,
            'exact_key_hit': key_hit,
            'exact_key_rate': key_hit / key_total if key_total else 0,
            'field_search_total': field_total,
            'field_search_hit': field_hit,
            'field_search_rate': field_hit / field_total if field_total else 0,
        },
        'recall_results': recall_results,
        'field_results': field_results,
        'key_results': key_results,
    }


def main():
    parser = argparse.ArgumentParser(description='检索质量基准测试')
    parser.add_argument('--json', action='store_true', help='输出 JSON')
    parser.add_argument('--limit', type=int, default=None, help='限制测试病证数')
    args = parser.parse_args()

    result = run_evaluation(limit=args.limit)
    s = result['summary']

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print('=' * 60)
        print('  检索质量基准测试')
        print('=' * 60)
        print()
        print(f'医案总数: {s["total_cases"]}')
        print(f'测试病证数: {s["total_categories"]}')
        print(f'查询总数: {s["total_queries"]}')
        print()

        print('--- 关键词检索 recall@k ---')
        for k in K_VALUES:
            key = f'avg_recall@{k}'
            if key in s:
                print(f'  平均 recall@{k}: {s[key]:.1%}')
        print(f'  零命中率: {s["zero_hit_queries"]}/{s["total_queries"]} ({s["zero_hit_rate"]:.1%})')
        print(f'  平均库覆盖: {s["avg_asset_coverage"]} 个 asset')
        print()

        print('--- 精确 key 检索 ---')
        print(f'  命中: {s["exact_key_hit"]}/{s["exact_key_total"]} ({s["exact_key_rate"]:.1%})')
        print()

        print('--- 字段检索（药味）---')
        print(f'  命中: {s["field_search_hit"]}/{s["field_search_total"]} ({s["field_search_rate"]:.1%})')
        print()

        # 低分病证详情
        print('--- 低分病证（recall@10 < 50%）---')
        low_score = [r for r in result['recall_results'] if r.get('recall@10', 0) < 0.5 and r['total_hits'] > 0]
        if low_score:
            for r in low_score[:10]:
                print(f'  {r["category"]}: recall@5={r["recall@5"]:.0%} recall@10={r["recall@10"]:.0%} hits={r["total_hits"]} assets={r["asset_coverage"]}')
        else:
            print('  无低分病证 ✅')

        # 零命中病证
        zero = [r for r in result['recall_results'] if r['total_hits'] == 0]
        if zero:
            print()
            print('--- 零命中病证 ---')
            for r in zero:
                print(f'  ❌ {r["category"]}: 0 条命中')

    # 退出码：零命中率 > 20% 或平均 recall@10 < 30% 则失败
    fail = s['zero_hit_rate'] > 0.2 or s.get('avg_recall@10', 0) < 0.3
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main())
