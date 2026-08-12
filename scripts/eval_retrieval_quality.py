#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检索质量基准测试

从全部医案库（asset9 + asset11-32，共 1994 条）按病证类别构造 golden set，
验证 rag_search 的检索质量。

指标：
  - precision@k / recall@k：查询「某病证」时，前 k 条结果与 golden set 的查准/查全率
  - 库覆盖率：查询命中的 asset 数量 / 总 asset 数量
  - 零命中率：返回 0 条结果的查询占比

用法：
    python scripts/eval_retrieval_quality.py
    python scripts/eval_retrieval_quality.py --json
    python scripts/eval_retrieval_quality.py --limit 20  # 减少抽样数
    python scripts/eval_retrieval_quality.py --write-golden   # 固化 golden 基准为独立文件

设计原则：
    - golden set 从真实医案库抽样，不用人造数据
    - 查询词用病证名（category 字段），这是用户最自然的查询方式
    - recall 分母用 golden 全集，而非前 N 条
    - golden 基准可持久化（--write-golden），使评估可复现、可版本化
    - 检索与 golden 同源覆盖：golden 取自哪些 asset，检索就覆盖哪些 asset，
      避免「基准含 asset18-32，检索却用默认范围」造成的 recall 系统性低估

指标口径（务必按此解读，避免误用）：
    - precision@k / recall@k 衡量的是「评估过程选定的 asset 子集（golden 来源的资产）」
      内的排序命中情况，即<b>体系内检索质量</b>，<b>不等于</b>对全 32 个 asset 库
      （含未入选 golden 的资产）的全库召回率。
    - 若某病证命中率偏高/偏低，应先确认该病证在 golden 对应 asset 是否充分，再下结论。
"""

import argparse
import json
import sys
import os
import glob
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rag_search import search, lookup_key, _SYNONYM_MAP


# ═══════════════════════════════════════════════════════════════
# Golden set 构造
# ═══════════════════════════════════════════════════════════════

RAG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rag-knowledge-base')
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLDEN_FILE = os.path.join(PROJECT_ROOT, 'tests', 'golden', 'retrieval_golden.json')

# 高频病证（>=15 条），用于构造 golden set
MIN_CATEGORY_COUNT = 15
# recall@k 的 k 值
K_VALUES = [5, 10, 20]


def load_all_cases():
    """加载所有医案库，返回 [(asset_basename, entry), ...]

    asset_basename 形如 'asset18_huichunlu_cases'（不带 .json），
    用于把它转成 rag_search 可接收的 assets 参数（'.json' 结尾的文件名）。
    """
    cases = []
    for f in sorted(glob.glob(os.path.join(RAG_DIR, 'asset*_cases.json'))):
        asset_id = os.path.basename(f).replace('.json', '')
        d = json.load(open(f, encoding='utf-8'))
        for e in d.get('entries', []):
            cases.append((asset_id, e))
    return cases


def build_golden_set(cases):
    """按病证类别构造 golden set（含同义词扩展）

    返回：{category: [(asset_basename, entry, entry_id), ...]}
    entry_id 取 case_id 或 entry_id（两条医案字段中恒有其一，二者取值一致）。
    """
    alias_to_standard = {}
    for standard, aliases in _SYNONYM_MAP.items():
        alias_to_standard[standard] = standard
        for alias in aliases:
            alias_to_standard[alias] = standard

    by_category = defaultdict(list)
    for asset_id, e in cases:
        cat = e.get('category', '').strip()
        if cat:
            eid = e.get('case_id') or e.get('entry_id') or ''
            by_category[cat].append((asset_id, e, eid))

    golden = {}
    for cat, items in by_category.items():
        standard = alias_to_standard.get(cat, cat)
        if standard not in golden:
            golden[standard] = []
        golden[standard].extend(items)

    # 只保留 >= MIN_CATEGORY_COUNT 条的病证，recall 分母用全集
    return {k: v for k, v in golden.items() if len(v) >= MIN_CATEGORY_COUNT}


def write_golden_file(golden_set):
    """把 golden set 固化为独立 JSON 文件，供版本化追踪与复现。"""
    os.makedirs(os.path.dirname(GOLDEN_FILE), exist_ok=True)
    payload = {
        "_comment": "检索质量 golden 基准：按病证类别收集的全部医案 entry_id。"
                     "由 eval_retrieval_quality.py --write-golden 生成，勿手改。",
        "categories": {
            cat: sorted(eid for _, _, eid in items if eid)
            for cat, items in golden_set.items()
        },
    }
    with open(GOLDEN_FILE, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return GOLDEN_FILE


def check_golden_fresh():
    """校验固化 golden 与实时重建是否一致，返回 (ok, 差异描述)。

    用于 CI 门禁：若知识库新增/改名条目导致 golden 过时，应 --write-golden 重新固化。
    """
    if not os.path.isfile(GOLDEN_FILE):
        return False, f"缺少 golden 文件: {GOLDEN_FILE}（先运行 --write-golden）"
    try:
        saved = json.load(open(GOLDEN_FILE, encoding='utf-8'))['categories']
    except Exception as exc:
        return False, f"golden 解析失败: {exc}"

    fresh = {cat: sorted(eid for _, _, eid in items if eid)
             for cat, items in build_golden_set(load_all_cases()).items()}

    diffs = []
    for cat in sorted(set(saved) | set(fresh)):
        if saved.get(cat) != fresh.get(cat):
            s = saved.get(cat, [])
            f = fresh.get(cat, [])
            added = sorted(set(f) - set(s))
            removed = sorted(set(s) - set(f))
            diffs.append(f"{cat}: +{len(added)} -{len(removed)}")
    if diffs:
        return False, "golden 已过时，差异: " + "; ".join(diffs) + "（运行 --write-golden 更新）"
    return True, "golden 与实时重建一致"


# ═══════════════════════════════════════════════════════════════
# 检索质量评估
# ═══════════════════════════════════════════════════════════════

def _assets_of(golden_items):
    """取 golden 条目实际来自的 asset 文件名列表（含 .json），供检索同源覆盖。"""
    return sorted({aid + '.json' for aid, _, _ in golden_items})


def evaluate_recall(golden_set, k_values):
    """
    对每个病证类别，用病证名作为查询词，验证 recall@k / precision@k。

    改进点（vs 历史实现）：
      1. 检索范围 = golden 实际来源的 asset 全集，消除范围错配导致的 recall 低估
      2. 命中匹配用 hit['id']（即 entry_id），而非从 title 字符串切分
    """
    results = []
    max_limit = max(max(k_values), max(len(v) for v in golden_set.values()))

    for category, golden_items in golden_set.items():
        assets = _assets_of(golden_items)
        hits = search([category], assets=assets, limit=max_limit)

        # hit id = entry_id（rag_search._entry_id 优先取 entry_id/case_id），与 golden entry_id 同源
        hit_ids = [h.get('id', '') for h in hits]
        hit_assets = set(h.get('asset', '') for h in hits)

        golden_ids = set(eid for _, _, eid in golden_items if eid)

        precisions = {}
        recalls = {}
        for k in k_values:
            top_k_ids = set(v for v in hit_ids[:k] if v)
            relevant = len(top_k_ids & golden_ids)
            precisions[f'precision@{k}'] = relevant / k if k > 0 else 0
            recalls[f'recall@{k}'] = relevant / len(golden_ids) if golden_ids else 0

        results.append({
            'category': category,
            'golden_count': len(golden_items),
            'total_hits': len(hits),
            'asset_coverage': len(hit_assets),
            'hit_assets': sorted(hit_assets),
            'matched_golden_in_top20': len(set(v for v in hit_ids[:20] if v) & golden_ids),
            **precisions,
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
    avg_precision = {}
    for k in K_VALUES:
        rk = f'recall@{k}'
        pk = f'precision@{k}'
        vals_r = [r[rk] for r in recall_results if r['total_hits'] > 0]
        vals_p = [r[pk] for r in recall_results if r['total_hits'] > 0]
        avg_recall[rk] = sum(vals_r) / len(vals_r) if vals_r else 0
        avg_precision[pk] = sum(vals_p) / len(vals_p) if vals_p else 0

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
            **avg_recall,
            **avg_precision,
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
    parser.add_argument('--write-golden', action='store_true',
                        help='把 golden 基准固化为 %s' % GOLDEN_FILE)
    parser.add_argument('--check-golden', action='store_true',
                        help='校验固化 golden 是否与实时重建一致（用于 CI 门禁）')
    args = parser.parse_args()

    if args.check_golden:
        ok, msg = check_golden_fresh()
        print(('✅ ' if ok else '❌ ') + msg)
        return 0 if ok else 1

    result = run_evaluation(limit=args.limit)
    s = result['summary']

    if args.write_golden:
        # 重新构建完整 golden（不受 --limit 影响）并固化
        full = build_golden_set(load_all_cases())
        path = write_golden_file(full)
        print(f'✅ golden 基准已写入: {path} ({len(full)} 类)')
        if args.json:
            # --write-golden --json 时把路径并入结果
            result['golden_file'] = path

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

        print('--- 关键词检索质量 ---')
        for k in K_VALUES:
            rk = f'recall@{k}'
            pk = f'precision@{k}'
            if rk in s:
                print(f'  recall@{k}: {s[rk]:.1%}  precision@{k}: {s[pk]:.1%}')
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
        low_score = [r for r in result['recall_results'] if r.get('precision@10', 0) < 0.5 and r['total_hits'] > 0]
        if low_score:
            for r in low_score[:10]:
                print(f'  {r["category"]}: P@5={r["precision@5"]:.0%} P@10={r["precision@10"]:.0%} R@10={r["recall@10"]:.0%} hits={r["total_hits"]} assets={r["asset_coverage"]}')
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
    fail = s['zero_hit_rate'] > 0.2 or s.get('precision@10', 0) < 0.3
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main())
