#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""兼容入口：实际测试已迁移到 tests/full_regression_test.py。

P1 优化：此文件仅为向后兼容。推荐直接运行：
  python tests/full_regression_test.py
"""
import os
import sys
import runpy

print("⚠️  [DEPRECATION] scripts/full_regression_test.py 已迁移到 tests/full_regression_test.py")
print("   请改用: python tests/full_regression_test.py")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, 'tests', 'full_regression_test.py')
runpy.run_path(TARGET, run_name='__main__')
