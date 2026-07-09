#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
包 API + RAG 精确检索 + 报告 RAG 章节 冒烟测试

用法:
  python tests/test_package_and_rag.py
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

SCRIPTS = os.path.join(ROOT, "scripts")
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, os.path.join(SCRIPTS, "lib"))

from _common import setup_environment  # noqa: E402
setup_environment(add_lib=True, add_scripts=True)


def _ok(name: str) -> None:
    print(f"[PASS] {name}")


def _fail(name: str, msg: str) -> None:
    print(f"[FAIL] {name}: {msg}")
    raise AssertionError(f"{name}: {msg}")


def test_package_import():
    try:
        from wuyun_liuqi import calculate, lookup_key, fetch_by_date, __version__
    except Exception as e:
        _fail("package_import", str(e))
    assert __version__
    r = calculate("2026-06-29")
    if r.get("yunqi_year") != 2026 or r.get("year_gz") != "丙午":
        _fail("package_calculate", f"unexpected {r.get('yunqi_year')} {r.get('year_gz')}")
    if "rag_keys" not in r:
        _fail("package_calculate", "missing rag_keys")
    hits = lookup_key(r["rag_keys"]["suiyun"])
    if not hits:
        _fail("package_lookup_key", "no hits for suiyun key")
    bundle = fetch_by_date("2026-06-29")
    if bundle.get("missing"):
        _fail("package_fetch_by_date", f"missing={bundle['missing']}")
    _ok("package_import_calculate_lookup_fetch")


def test_rag_exact_and_date():
    import rag_search as rs

    hits = rs.lookup_key("water_excess")
    if not hits:
        _fail("lookup_water_excess", "empty")
    ids = {h["id"] for h in hits}
    if "water_excess" not in ids and not any("water_excess" in str(h.get("id")) for h in hits):
        # asset1 uses code water_excess
        if not any(h.get("query_key") == "water_excess" for h in hits):
            _fail("lookup_water_excess", f"ids={ids}")

    bundle = rs.fetch_by_date("2026-06-29")
    for role in ("suiyun", "sitian", "zaiquan", "current_step"):
        if role not in (bundle.get("rag_keys") or {}):
            _fail("fetch_roles", f"missing rag_keys.{role}")
        if not (bundle.get("hits_by_role") or {}).get(role):
            _fail("fetch_roles", f"no hits for {role}")
    if bundle.get("missing"):
        _fail("fetch_roles", f"missing={bundle['missing']}")
    _ok("rag_exact_and_date")


def test_report_rag_section():
    from yunqi_report import generate_report, build_rag_bundle_section

    section = build_rag_bundle_section(2026, ref_date="2026-06-29")
    if "知识库精确命中" not in section:
        _fail("rag_section", "heading missing")
    if "water_excess" not in section and "水运" not in section:
        _fail("rag_section", "suiyun content missing")

    report = generate_report(2026, audience="student", with_rag_bundle=True, rag_ref_date="2026-06-29")
    if "知识库精确命中" not in report:
        _fail("report_bundle", "section not in report")

    report_off = generate_report(2026, audience="student", with_rag_bundle=False)
    if "知识库精确命中" in report_off:
        _fail("report_bundle_off", "section should be absent when disabled")
    _ok("report_rag_section")


def test_html_rag_section():
    import generate_html_report as ghr
    html = ghr.generate_html(ghr.get_data("2026-06-29"), with_rag_bundle=True)
    if "知识库精确命中" not in html or "water_excess" not in html:
        _fail("html_rag", "section missing in HTML")
    html_off = ghr.generate_html(ghr.get_data("2026-06-29"), with_rag_bundle=False)
    if "知识库精确命中" in html_off:
        _fail("html_rag_off", "should be absent")
    _ok("html_rag_section")


def test_semantic_search():
    from rag_semantic import semantic_search
    hits = semantic_search("心火偏旺", limit=3)
    if not hits:
        _fail("semantic", "no hits")
    if hits[0]["score"] <= 0:
        _fail("semantic", "score invalid")
    _ok("semantic_search")


def main() -> int:
    print("Package + RAG integration tests")
    print("=" * 40)
    test_package_import()
    test_rag_exact_and_date()
    test_report_rag_section()
    test_html_rag_section()
    test_semantic_search()
    print("=" * 40)
    print("✅ all package/rag tests passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError:
        raise SystemExit(1)
