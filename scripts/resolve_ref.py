#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
稳定引用 (yle:) 解析器

把 RAG 检索产出的稳定引用 `yle:<asset>:<entry_id>` 反解回知识库具体条目，
供报告生成 / Agent 溯源核验引用是否可访问。

引用格式：
  yle:asset13_gujin_an_cases:gujin_001
  yle:asset1_suiyun:water_excess
asset 为知识库文件名（去 .json），entry_id 为条目唯一标识（医案取 case_id/entry_id，
非医案取 code/key/rag_key 等）。

用法：
    python scripts/resolve_ref.py yle:asset13_gujin_an_cases:gujin_001
    python scripts/resolve_ref.py yle:asset13_gujin_an_cases:gujin_001 --json
    python scripts/resolve_ref.py --refs ref1 ref2 ...        # 批量，输出可访问率
    python scripts/resolve_ref.py --list-assets                # 列出可解析的 asset
    python scripts/resolve_ref.py --selfcheck                  # 自测：可访问率门禁

退出码：
    0  全部引用可访问（或自测通过）
    1  存在不可访问引用 / 自测失败
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib'))

from rag_search import resolve_ref, parse_ref, ASSET_FILES  # noqa: E402


def _load(doc_ids):
    """批量解析引用，返回 (ok_list, bad_list)。
    ok_list: [ {ref, asset_name, id, title, preview} ]
    bad_list:[ {ref, error} ]
    """
    ok, bad = [], []
    for ref in doc_ids:
        hit, err = resolve_ref(ref)
        if err:
            bad.append({"ref": ref, "error": err})
        else:
            ok.append(hit)
    return ok, bad


def main():
    p = argparse.ArgumentParser(description="yle: 稳定引用解析器")
    p.add_argument("refs", nargs="*", help="一个或多个 yle: 引用")
    p.add_argument("--json", action="store_true", help="JSON 输出")
    p.add_argument("--list-assets", action="store_true", help="列出可解析 asset")
    p.add_argument("--selfcheck", action="store_true",
                   help="自测：从各 asset 生成引用并核验可访问率，用于 CI 门禁")
    args = p.parse_args()

    if args.list_assets:
        names = sorted({os.path.basename(f).replace('.json', '')
                        for f in ASSET_FILES.values() if f.endswith('.json')})
        print(json.dumps({"assets": names}, ensure_ascii=False, indent=2))
        return 0

    if args.selfcheck:
        # 从每个 asset 取第一条可检索条目，生成引用再反解，统计可访问率
        from rag_search import load_entries, _entry_id
        refs, cnt = [], 0
        for key, fname in sorted(ASSET_FILES.items()):
            if not fname.endswith('.json') or key == 'terminology':
                continue
            try:
                _, entries = load_entries(key)
            except Exception:
                continue
            base = os.path.basename(fname).replace('.json', '')
            for i, e in enumerate(entries):
                if not isinstance(e, dict):
                    continue
                eid = _entry_id(e, i)
                refs.append(f"yle:{base}:{eid}")
                cnt += 1
                break  # 每 asset 取一条即可
        ok, bad = _load(refs)
        rate = len(ok) / len(refs) if refs else 0
        if args.json:
            print(json.dumps({
                "total": len(refs),
                "ok": len(ok),
                "failed": len(bad),
                "accessibility_rate": round(rate, 4),
                "failed_refs": bad,
            }, ensure_ascii=False, indent=2))
        else:
            print(f"自测: {len(ok)}/{len(refs)} 引用可访问 ({rate:.1%})")
            for b in bad:
                print(f"  ❌ {b['ref']}: {b['error']}")
        return 0 if bad == [] else 1

    if not args.refs:
        p.print_help()
        return 2

    ok, bad = _load(args.refs)
    if args.json:
        print(json.dumps({
            "total": len(args.refs),
            "ok": len(ok), "failed": len(bad),
            "accessibility_rate": round(len(ok) / len(args.refs), 4),
            "results": ok, "errors": bad,
        }, ensure_ascii=False, indent=2))
    else:
        for h in ok:
            print(f"✅ {h['ref']}  →  {h['title'] or h['id']}")
            if h.get('preview'):
                print(f"      {h['preview']}")
        for b in bad:
            print(f"❌ {b['ref']}: {b['error']}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())