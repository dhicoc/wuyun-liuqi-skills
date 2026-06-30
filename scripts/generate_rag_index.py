#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG 知识库索引生成与一致性检查工具

自动扫描 rag-knowledge-base/ 下的结构化 JSON 资产，生成 / 校验 index.json。

用法：
  python scripts/generate_rag_index.py
  python scripts/generate_rag_index.py --check
  python scripts/generate_rag_index.py --print
  python scripts/generate_rag_index.py --output rag-knowledge-base/index.json
"""
import argparse
import json
import os
import sys
import io
from copy import deepcopy

if sys.platform == 'win32' and sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except (AttributeError, io.UnsupportedOperation):
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAG_DIR = os.path.join(BASE_DIR, 'rag-knowledge-base')
DEFAULT_INDEX_PATH = os.path.join(RAG_DIR, 'index.json')

SKIP_FILES = {'index.json', '_entry_template.json'}
KEY_FIELDS = [
    'key', 'code', 'rag_key', 'sitian_key', 'zaiquan_key', 'constitution_code',
    'region_id', 'region_name', 'commentary_id', 'formula_id', 'term', 'pinyin',
    'entry_id', 'birth_yunqi_keys', 'suiyun_code', 'related_yunqi_keys',
]

ASSET_CATEGORY_BY_FILE = {
    'asset1_suiyun.json': 'suiyun_pathogenesis',
    'asset2_sitian_zaiquan.json': 'sitian_zaiquan_pathogenesis',
    'asset3_kezhujialin.json': 'kezhujialin_pathogenesis',
    'asset4_formula.json': 'yunqi_formula',
    'asset5_commentary.json': 'commentary',
    'asset6_regional.json': 'regional_modifier',
    'asset7_constitution.json': 'constitution_alignment',
    'terminology.json': 'terminology',
}

TITLE_BY_CATEGORY = {
    'suiyun_pathogenesis': '岁运病机资产',
    'sitian_zaiquan_pathogenesis': '司天在泉资产',
    'kezhujialin_pathogenesis': '客主加临资产',
    'yunqi_formula': '运气方资产',
    'commentary': '历代注家资产',
    'regional_modifier': '地域修正资产',
    'constitution_alignment': '运气体质资产',
    'terminology': '术语解释资产',
}

DESCRIPTION_BY_CATEGORY = {
    'suiyun_pathogenesis': '五运太过/不及病机、症状、治则。',
    'sitian_zaiquan_pathogenesis': '司天在泉上下半年六气病机与治法。',
    'kezhujialin_pathogenesis': '六步主客气组合、顺逆判断、病机分析。',
    'yunqi_formula': '三因司天方与运气方药方向。',
    'commentary': '历代注家运气学说观点。',
    'regional_modifier': '地域气候修正与体质倾向。',
    'constitution_alignment': '出生年运气体质映射与当前岁运调理。',
    'terminology': '术语解释库，用于教学和报告解释。',
}

PREFERRED_LOOKUP_FIELDS = {
    'asset1_suiyun.json': ['code'],
    'asset2_sitian_zaiquan.json': ['sitian_key', 'zaiquan_key', 'rag_key'],
    'asset3_kezhujialin.json': ['key', 'rag_key'],
    'asset4_formula.json': ['rag_key'],
    'asset5_commentary.json': ['related_yunqi_keys', 'commentary_id'],
    'asset6_regional.json': ['region_id', 'region_name'],
    'asset7_constitution.json': ['birth_yunqi_keys', 'suiyun_code', 'constitution_code'],
    'terminology.json': ['term', 'pinyin', 'entry_id'],
}


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def dump_json(data):
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False) + '\n'


def asset_files(rag_dir=RAG_DIR):
    files = []
    for name in os.listdir(rag_dir):
        if not name.endswith('.json') or name in SKIP_FILES:
            continue
        path = os.path.join(rag_dir, name)
        if os.path.isfile(path):
            files.append(name)
    return sorted(files, key=asset_sort_key)


def asset_sort_key(name):
    if name.startswith('asset'):
        digits = ''.join(ch for ch in name if ch.isdigit())
        return (0, int(digits or 0), name)
    if name == 'terminology.json':
        return (1, 0, name)
    return (2, 0, name)


def get_entries(data):
    entries = data.get('entries')
    return entries if isinstance(entries, list) else []


def infer_asset_id(filename, data):
    if data.get('asset_id'):
        return str(data['asset_id'])
    if filename == 'terminology.json':
        return 'terminology'
    return os.path.splitext(filename)[0].replace('_', '-')


def infer_asset_name(filename, data):
    return data.get('asset_name') or data.get('name') or os.path.splitext(filename)[0]


def infer_category(filename, data):
    return ASSET_CATEGORY_BY_FILE.get(filename) or data.get('asset_type') or 'custom_asset'


def infer_description(filename, data, category):
    return (
        data.get('asset_description')
        or data.get('description')
        or DESCRIPTION_BY_CATEGORY.get(category)
        or infer_asset_name(filename, data)
    )


def infer_lookup_fields(filename, entries):
    preferred = PREFERRED_LOOKUP_FIELDS.get(filename)
    if preferred:
        return preferred
    found = []
    for field in KEY_FIELDS:
        if any(isinstance(entry, dict) and entry.get(field) not in (None, '', []) for entry in entries):
            found.append(field)
    return found[:4] or ['entry_id']


def collect_example_keys(entries, lookup_fields, limit=3):
    examples = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        for field in lookup_fields:
            value = entry.get(field)
            values = value if isinstance(value, list) else [value]
            for item in values:
                if item in (None, '', []):
                    continue
                item = str(item)
                if item not in examples:
                    examples.append(item)
                if len(examples) >= limit:
                    return examples
    return examples


def build_index(rag_dir=RAG_DIR):
    entries = []
    for filename in asset_files(rag_dir):
        path = os.path.join(rag_dir, filename)
        data = load_json(path)
        if not isinstance(data, dict):
            continue
        asset_entries = get_entries(data)
        category = infer_category(filename, data)
        asset_id = infer_asset_id(filename, data)
        lookup_fields = infer_lookup_fields(filename, asset_entries)
        entry = {
            'entry_id': f'rag_index_{os.path.splitext(filename)[0]}',
            'entry_type': 'asset_index',
            'title': TITLE_BY_CATEGORY.get(category) or infer_asset_name(filename, data),
            'file': filename,
            'asset_id': asset_id,
            'asset_name': infer_asset_name(filename, data),
            'asset_category': category,
            'description': infer_description(filename, data, category),
            'total_entries': len(asset_entries),
            'lookup_fields': lookup_fields,
            'example_keys': collect_example_keys(asset_entries, lookup_fields),
            'rag_key': os.path.splitext(filename)[0],
        }
        entries.append(entry)

    return {
        'asset_name': 'wuyun-liuqi-rag-index',
        'asset_type': 'knowledge_base_index',
        'description': '五运六气 RAG 知识库资产索引。用于说明各 asset 的用途、检索键和维护状态。',
        'total_entries': len(entries),
        'primary_api': 'scripts/calculate_yunqi_api.py',
        'entries': entries,
        'maintenance': {
            'generate': 'python scripts/generate_rag_index.py',
            'check': 'python scripts/generate_rag_index.py --check',
            'validate': 'python scripts/validate_knowledge_base.py',
            'full_regression': 'python scripts/full_regression_test.py',
            'ingest': 'python scripts/ingest_literature.py',
        },
    }


def normalized(data):
    clone = deepcopy(data)
    return json.loads(json.dumps(clone, ensure_ascii=False, sort_keys=True))


def check_index(index_path=DEFAULT_INDEX_PATH, rag_dir=RAG_DIR):
    expected = build_index(rag_dir)
    if not os.path.exists(index_path):
        return False, ['index.json 不存在'], expected
    current = load_json(index_path)
    if normalized(current) != normalized(expected):
        return False, ['index.json 与自动生成结果不一致，请运行 python scripts/generate_rag_index.py 更新。'], expected
    return True, [], expected


def write_index(index_path=DEFAULT_INDEX_PATH, rag_dir=RAG_DIR):
    data = build_index(rag_dir)
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(dump_json(data))
    return data


def main():
    parser = argparse.ArgumentParser(description='生成或校验 rag-knowledge-base/index.json')
    parser.add_argument('--rag-dir', default=RAG_DIR, help='RAG 知识库目录')
    parser.add_argument('--output', default=DEFAULT_INDEX_PATH, help='输出 index.json 路径')
    parser.add_argument('--check', action='store_true', help='只检查 index.json 是否与自动生成结果一致')
    parser.add_argument('--print', action='store_true', help='打印自动生成的 index JSON，不写入文件')
    args = parser.parse_args()

    if args.print:
        sys.stdout.write(dump_json(build_index(args.rag_dir)))
        return

    if args.check:
        ok, errors, _ = check_index(args.output, args.rag_dir)
        if ok:
            print('✅ rag-knowledge-base/index.json 与自动生成结果一致')
            return
        for err in errors:
            print(f'❌ {err}')
        sys.exit(1)

    data = write_index(args.output, args.rag_dir)
    print(f"✅ RAG 索引已生成：{args.output}（{data['total_entries']} 个资产）")


if __name__ == '__main__':
    main()
