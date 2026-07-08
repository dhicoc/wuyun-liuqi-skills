#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""兼容入口：实际测试已迁移到 tests/verify_expansion.py。

P1 优化：此文件仅为向后兼容。推荐直接运行：
  python tests/verify_expansion.py
"""
import os
import sys
import warnings
import runpy

print("⚠️  [DEPRECATION] scripts/verify_expansion.py 已迁移到 tests/verify_expansion.py")
print("   请改用: python tests/verify_expansion.py")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, 'tests', 'verify_expansion.py')
runpy.run_path(TARGET, run_name='__main__')
