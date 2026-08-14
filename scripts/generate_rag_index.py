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
from copy import deepcopy

from _common import setup_environment
setup_environment(add_lib=False)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAG_DIR = os.path.join(BASE_DIR, 'rag-knowledge-base')
DEFAULT_INDEX_PATH = os.path.join(RAG_DIR, 'index.json')

SKIP_FILES = {'index.json', '_entry_template.json', 'case_relations.json', 'embeddings.json'}
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
    'wenyi_yunqi': '运气瘟疫防治资产',
    'suiyun_pathogenesis': '岁运病机资产',
    'sitian_zaiquan_pathogenesis': '司天在泉资产',
    'kezhujialin_pathogenesis': '客主加临资产',
    'yunqi_formula': '运气方资产',
    'commentary': '历代注家资产',
    'regional_modifier': '地域修正资产',
    'constitution_alignment': '运气体质资产',
    'terminology': '术语解释资产',
    'wenyi_yunqi': '运气瘟疫防治资产',
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
    'wenyi_yunqi': '松峰说疫运气瘟疫防治：五运太过不及瘟疫侧重、六气司天在泉民病、五郁治法、刚柔失守疫病专方。',
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
    'asset17_wenyi_yunqi.json': ['code', 'sitian_key', 'zaiquan_key', 'rag_key', 'ganzhi', 'category'],
    'asset18_huichunlu_cases.json': ['category', 'physician', 'rag_key', 'case_id'],
    'asset19_zhangyuqing_cases.json': ['category', 'physician', 'rag_key', 'case_id'],
    'asset20_wujutong_cases.json': ['category', 'physician', 'rag_key', 'case_id'],
    'asset21_yuyicao_cases.json': ['category', 'physician', 'rag_key', 'case_id'],
    'asset22_huixi_cases.json': ['category', 'physician', 'rag_key', 'case_id'],
    'asset23_huayunlou_cases.json': ['category', 'physician', 'rag_key', 'case_id'],
    'asset24_zhenyu_juji_cases.json': ['category', 'physician', 'rag_key', 'case_id'],
    'asset25_xushi_cases.json': ['category', 'physician', 'rag_key', 'case_id'],
    'asset26_xingxuan_cases.json': ['category', 'physician', 'rag_key', 'case_id'],
    'asset27_sunwenyuan_cases.json': ['category', 'physician', 'rag_key', 'case_id'],
    'asset28_conggui_cases.json': ['category', 'physician', 'rag_key', 'case_id'],
    'asset29_waike_zhengzong.json': ['category', 'physician', 'rag_key', 'case_id', 'internal_key', 'external_key'],
    'asset30_lizhai_waike.json': ['category', 'physician', 'rag_key', 'case_id', 'internal_key', 'external_key'],
    'asset31_zuihuachuang_cases.json': ['category', 'physician', 'rag_key', 'case_id'],
    'asset32_yiyan_suibi.json': ['category', 'physician', 'rag_key', 'case_id'],
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


# ---------------------------------------------------------------------------
# Parquet 导出（P10）
# ---------------------------------------------------------------------------
# 设计原则（见 references/research-2026-08-13.md §3.2）：
#   - 对齐 HuggingFace `datasets` 生态的 Parquet 容器格式，ML 研究者可直接 load_dataset 消费；
#   - 导出「自有结构化字段」，不照搬 pokkoa 的散文单列 schema、不重分发其内容与许可证；
#   - 默认 JSON 路径完全不变、零新增依赖（pyarrow 仅在 --format parquet 时懒加载）。

def require_pyarrow():
    try:
        import pyarrow as pa          # noqa: F401
        import pyarrow.parquet as pq  # noqa: F401
    except Exception:
        print(
            "❌ Parquet 导出需要 pyarrow：请先 `pip install pyarrow`"
            "（或 `pip install -e '.[parquet]'`）后重试。",
            file=sys.stderr,
        )
        sys.exit(2)
    return pa, pq


def _rows_to_table(rows, columns):
    """把 list[dict] 转成 pyarrow Table，按列做最小类型推断（bool/int/string）。"""
    pa, _ = require_pyarrow()
    cols = {c: [] for c in columns}
    for r in rows:
        for c in columns:
            v = r.get(c, None)
            if isinstance(v, (list, dict)):
                v = json.dumps(v, ensure_ascii=False)
            cols[c].append(v)
    arrays = []
    for c in columns:
        vals = cols[c]
        nonnull = [v for v in vals if v is not None]
        if nonnull and all(isinstance(v, bool) for v in nonnull):
            arrays.append(pa.array(vals, type=pa.bool_()))
        elif nonnull and all(isinstance(v, int) for v in nonnull):
            arrays.append(pa.array(vals, type=pa.int64()))
        else:
            arrays.append(pa.array(
                [str(v) if v is not None else None for v in vals],
                type=pa.string(),
            ))
    return pa.table(arrays, names=columns)


def write_parquet(rows, columns, path):
    _, pq = require_pyarrow()
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    pq.write_table(_rows_to_table(rows, columns), path)
    return len(rows)


# ---- RAG 条目扁平化导出 ---------------------------------------------------
RAG_COLUMNS = [
    'asset_id', 'asset_name', 'asset_category', 'entry_id', 'rag_key',
    'sui_yun', 'si_tian', 'zai_quan', 'zhu_qi', 'yun_qi_xiang_he',
    'source_quote', 'title', 'text',
    'category', 'physician', 'dynasty', 'disease', 'tags',
]


def _entry_text(entry):
    for k in ('text', 'content', 'preview', 'description', 'explanation'):
        v = entry.get(k)
        if isinstance(v, str) and v.strip():
            return v
    return ''


def _derive_yunqi_xianghe(entry, sui_yun, si_tian, zai_quan):
    if sui_yun and si_tian and zai_quan:
        return f'{sui_yun} + {si_tian}司天 + {zai_quan}在泉'
    return entry.get('yunqi_xianghe') or entry.get('yun_qi_xiang_he') or ''


def collect_rag_entries(rag_dir=RAG_DIR):
    """扁平化全部 RAG 条目，导出字段覆盖五维度 + rag_key + source_quote。"""
    rows = []
    for filename in asset_files(rag_dir):
        path = os.path.join(rag_dir, filename)
        data = load_json(path)
        if not isinstance(data, dict):
            continue
        asset_id = infer_asset_id(filename, data)
        asset_name = infer_asset_name(filename, data)
        category = infer_category(filename, data)
        for entry in get_entries(data):
            if not isinstance(entry, dict):
                continue
            sui_yun = entry.get('suiyun') or entry.get('suiyun_code') or entry.get('code') or ''
            si_tian = entry.get('sitian_key') or entry.get('sitian') or ''
            zai_quan = entry.get('zaiquan_key') or entry.get('zaiquan') or ''
            zhu_qi = entry.get('zhuqi') or ''
            yxh = _derive_yunqi_xianghe(entry, sui_yun, si_tian, zai_quan)
            src = entry.get('source_quote')
            if isinstance(src, list):
                src = ' | '.join(str(x) for x in src)
            rows.append({
                'asset_id': asset_id,
                'asset_name': asset_name,
                'asset_category': category,
                'entry_id': entry.get('entry_id') or entry.get('id') or '',
                'rag_key': entry.get('rag_key') or '',
                'sui_yun': sui_yun,
                'si_tian': si_tian,
                'zai_quan': zai_quan,
                'zhu_qi': zhu_qi,
                'yun_qi_xiang_he': yxh,
                'source_quote': src or '',
                'title': entry.get('title') or '',
                'text': _entry_text(entry),
                'category': entry.get('category') or '',
                'physician': entry.get('physician') or '',
                'dynasty': entry.get('dynasty') or '',
                'disease': entry.get('disease') or '',
                'tags': entry.get('tags') or '',
            })
    return rows


# ---- 结构化运气年表导出（对齐 pokkoa 的 year+month 粒度，但全结构化）--------
CALENDAR_COLUMNS = [
    'year', 'ganzhi', 'yunqi_year',
    'sui_yun_element', 'sui_yun_status', 'sui_yun_code', 'sui_yun_name',
    'si_tian', 'zai_quan', 'tong_hua', 'yun_qi_xiang_he',
    'step_number', 'step_name', 'zhu_qi', 'ke_qi', 'relation', 'shun_ni',
    'keqi_is_sitian', 'keqi_is_zaiquan', 'rag_key', 'source_quote',
]


def build_calendar(start_year=1900, end_year=2100):
    """生成 year × 六步 的结构化运气表（宽年份跨度，pokkoa 仅有 311 条散文）。"""
    from _common import add_lib_to_path
    add_lib_to_path()
    from yunqi_data import (
        get_ganzhi, get_dayun, get_sitian, get_zaiquan, get_suiyun_code,
        get_kezhujialin_detail, is_taiguo,
        check_tianfu, check_suihui, check_pingqi,
        check_tong_tianfu, check_tong_suihui, QI_STEP_NAMES,
    )
    rows = []
    for y in range(start_year, end_year + 1):
        tg, dz = get_ganzhi(y)
        dayun, _ = get_dayun(y)
        taiguo = is_taiguo(y)
        suiyun_code = get_suiyun_code(y)
        sitian = get_sitian(y)
        zaiquan = get_zaiquan(y)
        tianfu = check_tianfu(y)
        suihui = check_suihui(y)
        tong_tianfu = check_tong_tianfu(y)
        tong_suihui = check_tong_suihui(y)
        pingqi = check_pingqi(y)
        flags = []
        if tianfu:
            flags.append('天符')
        if suihui:
            flags.append('岁会')
        if tianfu and suihui:
            flags.append('太一天符')
        if tong_tianfu:
            flags.append('同天符')
        if tong_suihui:
            flags.append('同岁会')
        if pingqi:
            flags.append('平气')
        tong_hua = '、'.join(flags)
        sui_name = f'{dayun}运{"太过" if taiguo else "不及"}'
        yxh = f'{sui_name} + {sitian}司天 + {zaiquan}在泉' + (f'（{tong_hua}）' if tong_hua else '')
        for s in range(1, 7):
            det = get_kezhujialin_detail(y, s)
            rows.append({
                'year': y,
                'ganzhi': f'{tg}{dz}',
                'yunqi_year': y,
                'sui_yun_element': dayun,
                'sui_yun_status': '太过' if taiguo else '不及',
                'sui_yun_code': suiyun_code,
                'sui_yun_name': sui_name,
                'si_tian': sitian,
                'zai_quan': zaiquan,
                'tong_hua': tong_hua,
                'yun_qi_xiang_he': yxh,
                'step_number': s,
                'step_name': QI_STEP_NAMES[s],
                'zhu_qi': det['zhu_qi'],
                'ke_qi': det['ke_qi'],
                'relation': det['relation'],
                'shun_ni': det['shun_ni'],
                'keqi_is_sitian': det['keqi_is_sitian'],
                'keqi_is_zaiquan': det['keqi_is_zaiquan'],
                'rag_key': f'{suiyun_code}|{sitian}_sitian|{zaiquan}_zaiquan',
                'source_quote': '',
            })
    return rows


INDEX_COLUMNS = [
    'entry_id', 'entry_type', 'title', 'file', 'asset_id', 'asset_name',
    'asset_category', 'description', 'total_entries', 'lookup_fields',
    'example_keys', 'rag_key',
]


def main():
    parser = argparse.ArgumentParser(
        description='生成 / 校验 / 导出 rag-knowledge-base 索引与数据（支持 Parquet）')
    parser.add_argument('--rag-dir', default=RAG_DIR, help='RAG 知识库目录')
    parser.add_argument('--output', default=None, help='输出文件路径（默认按模式/格式推断）')
    parser.add_argument('--check', action='store_true', help='只检查 index.json 是否与自动生成结果一致')
    parser.add_argument('--print', action='store_true', help='打印自动生成的 index JSON，不写入文件')
    parser.add_argument('--format', choices=['json', 'parquet'], default='json',
                        help='输出格式（默认 json；parquet 需 pyarrow）')
    parser.add_argument('--export-mode', choices=['index', 'rag', 'calendar'], default='index',
                        help='导出内容：index(资产索引,默认) / rag(全部 RAG 条目) / calendar(结构化运气年表)')
    parser.add_argument('--year-range', nargs=2, type=int, default=[1900, 2100],
                        metavar=('START', 'END'),
                        help='calendar 模式的年份范围（含端点），默认 1900 2100')
    args = parser.parse_args()

    if args.print:
        sys.stdout.write(dump_json(build_index(args.rag_dir)))
        return

    if args.check:
        ok, errors, _ = check_index(args.output or DEFAULT_INDEX_PATH, args.rag_dir)
        if ok:
            print('✅ rag-knowledge-base/index.json 与自动生成结果一致')
            return
        for err in errors:
            print(f'❌ {err}')
        sys.exit(1)

    # ---- index 模式（默认） ----
    if args.export_mode == 'index':
        if args.format == 'parquet':
            path = args.output or os.path.join(args.rag_dir, 'index.parquet')
            n = write_parquet(build_index(args.rag_dir)['entries'], INDEX_COLUMNS, path)
            print(f"✅ RAG 索引 Parquet 已生成：{path}（{n} 个资产）")
        else:
            path = args.output or DEFAULT_INDEX_PATH
            data = write_index(path, args.rag_dir)
            print(f"✅ RAG 索引已生成：{path}（{data['total_entries']} 个资产）")
        return

    # ---- rag 模式 ----
    if args.export_mode == 'rag':
        rows = collect_rag_entries(args.rag_dir)
        if args.format == 'parquet':
            path = args.output or os.path.join(args.rag_dir, 'rag_entries.parquet')
            n = write_parquet(rows, RAG_COLUMNS, path)
            print(f"✅ RAG 条目 Parquet 已生成：{path}（{n} 条条目）")
        else:
            path = args.output or os.path.join(args.rag_dir, 'rag_entries.json')
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(dump_json(rows))
            print(f"✅ RAG 条目 JSON 已生成：{path}（{len(rows)} 条条目）")
        return

    # ---- calendar 模式 ----
    start, end = args.year_range
    rows = build_calendar(start, end)
    if args.format == 'parquet':
        path = args.output or os.path.join(args.rag_dir, 'yunqi_calendar.parquet')
        n = write_parquet(rows, CALENDAR_COLUMNS, path)
        print(f"✅ 运气年表 Parquet 已生成：{path}（{n} 行，{start}–{end}）")
    else:
        path = args.output or os.path.join(args.rag_dir, 'yunqi_calendar.json')
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(dump_json(rows))
        print(f"✅ 运气年表 JSON 已生成：{path}（{len(rows)} 行）")


if __name__ == '__main__':
    main()
