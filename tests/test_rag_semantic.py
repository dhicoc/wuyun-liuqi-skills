#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rag_semantic 回归测试。

验证：
1. 无 embedding 依赖（CI）时自动降级为字符 n-gram，不崩溃、返回结构正确。
2. 强制 backend='embedding' 但无依赖时同样优雅降级。
3. 空查询返回 []。
4. 既有 _tokenize / _cosine 行为保持稳定（防回归）。

（embedding 真·语义路径需 `pip install -e ".[semantic]"` 后由人工/集成测试覆盖。）

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


def test_fallback_no_crash_and_structure():
    """无 embedding 依赖时降级 n-gram，返回结构正确、mode=semantic。"""
    hits = rsem.semantic_search("心火偏旺", backend="auto")
    assert isinstance(hits, list)
    for h in hits:
        assert set(["score", "asset", "id", "title", "mode"]).issubset(h.keys())
        assert h["mode"] == "semantic"  # CI 无依赖 → n-gram 降级
        assert isinstance(h["score"], (int, float))


def test_backend_embedding_falls_back_gracefully():
    """强制 embedding 但无依赖：不抛异常，返回 list（降级）。"""
    try:
        from sentence_transformers import SentenceTransformer  # noqa: F401
        have_dep = True
    except Exception:
        have_dep = False
    hits = rsem.semantic_search("气候干燥 咳嗽", backend="embedding")
    assert isinstance(hits, list)
    if hits:
        assert hits[0]["mode"] in ("semantic", "semantic-embedding")
    # 若确实无依赖，应降级为 n-gram
    if not have_dep:
        assert all(h["mode"] == "semantic" for h in hits)


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
        test_fallback_no_crash_and_structure,
        test_backend_embedding_falls_back_gracefully,
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
