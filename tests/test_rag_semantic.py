#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rag_semantic 回归测试。

验证：
1. 字符 n-gram 语义检索不崩溃、返回结构正确。
2. 空查询返回 []。
3. 既有 _tokenize / _cosine 行为保持稳定（防回归）。

直接运行: python tests/test_rag_semantic.py
pytest 运行: pytest tests/test_rag_semantic.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, os.path.join(SCRIPTS, "lib"))

import rag_semantic as rsem  # noqa: E402


def test_empty_query_returns_empty():
    assert rsem.semantic_search("") == []
    assert rsem.semantic_search("   ") == []


def test_no_crash_and_structure():
    """n-gram 语义检索返回结构正确、mode=semantic。"""
    hits = rsem.semantic_search("心火偏旺")
    assert isinstance(hits, list)
    for h in hits:
        assert set(["score", "asset", "id", "title", "mode"]).issubset(h.keys())
        assert h["mode"] == "semantic"
        assert isinstance(h["score"], (int, float))


def test_tokenize_stable():
    toks = rsem._tokenize("天地")
    assert toks == ["天", "地", "天地"]
    assert rsem._tokenize("") == []


def test_cosine_identical_is_one():
    a = {"天": 2.0, "地": 1.0}
    assert abs(rsem._cosine(a, dict(a)) - 1.0) < 1e-9
    assert rsem._cosine({}, a) == 0.0


if __name__ == "__main__":
    tests = [
        test_empty_query_returns_empty,
        test_no_crash_and_structure,
        test_tokenize_stable,
        test_cosine_identical_is_one,
    ]
    failed = []
    for t in tests:
        try:
            t()
            print(f"[PASS] {t.__name__}")
        except AssertionError as e:
            print(f"[FAIL] {t.__name__}: {e}")
            failed.append(t.__name__)
    if failed:
        print(f"\n❌ {len(failed)} test(s) failed: {failed}")
        sys.exit(1)
    print(f"\n✅ all {len(tests)} rag_semantic tests passed")
