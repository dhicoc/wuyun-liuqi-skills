#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pip install -e . 后的独立安装冒烟

设计意图：
- 不依赖「当前 cwd 碰巧是仓库根」才能 import（但 editable 安装仍需要仓库数据文件）
- 验证：calculate / lookup_key / fetch_by_date / 路径解析

用法（在仓库根）:
  pip install -e ".[lunar]"
  python tests/smoke_pip_install.py

CI 中可在 install 后直接运行本脚本。
"""
from __future__ import annotations

import json
import sys


def main() -> int:
    print("pip/editable install smoke")
    print("=" * 40)

    try:
        import wuyun_liuqi
        from wuyun_liuqi import calculate, lookup_key, fetch_by_date
        from wuyun_liuqi._bootstrap import ensure_runtime_ready
    except Exception as e:
        print(f"[FAIL] import wuyun_liuqi: {e}")
        return 1

    print(f"[OK] version={getattr(wuyun_liuqi, '__version__', '?')}")

    runtime = ensure_runtime_ready()
    print(f"[OK] root={runtime['root']}")
    if not runtime["scripts_ok"]:
        print("[FAIL] scripts/calculate_yunqi_api.py not found — set WUYUN_LIUQI_ROOT?")
        return 1
    if not runtime["rag_ok"] or not runtime["rag_assets"]:
        print("[FAIL] rag-knowledge-base missing")
        return 1
    print("[OK] scripts + rag-knowledge-base resolved")

    try:
        r = calculate("2026-06-29")
    except Exception as e:
        print(f"[FAIL] calculate: {e}")
        return 1
    if r.get("yunqi_year") != 2026 or r.get("year_gz") != "丙午":
        print(f"[FAIL] unexpected result: {r.get('yunqi_year')} {r.get('year_gz')}")
        return 1
    print(f"[OK] calculate → {r['year_gz']} rag_keys={list((r.get('rag_keys') or {}).keys())}")

    try:
        hits = lookup_key(r["rag_keys"]["suiyun"])
        if not hits:
            print("[FAIL] lookup_key empty")
            return 1
        print(f"[OK] lookup_key → {hits[0].get('title')}")
    except Exception as e:
        print(f"[FAIL] lookup_key: {e}")
        return 1

    try:
        bundle = fetch_by_date("2026-06-29")
        if bundle.get("missing"):
            print(f"[FAIL] fetch_by_date missing={bundle['missing']}")
            return 1
        print(f"[OK] fetch_by_date → {len(bundle.get('hits') or [])} hits")
    except Exception as e:
        print(f"[FAIL] fetch_by_date: {e}")
        return 1

    # 可选：CLI 入口
    try:
        from wuyun_liuqi.__main__ import main as cli_main
        # 不真正跑完整 CLI，仅确认可 import
        print("[OK] wuyun_liuqi.__main__ importable")
    except Exception as e:
        print(f"[FAIL] __main__: {e}")
        return 1

    print("=" * 40)
    print("✅ pip install smoke passed")
    print(json.dumps({"status": "ok", "runtime": runtime}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
