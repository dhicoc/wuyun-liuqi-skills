#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""兼容入口：实际测试已迁移到 tests/verify_expansion.py。"""
import os
import runpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = os.path.join(ROOT, 'tests', 'verify_expansion.py')
runpy.run_path(TARGET, run_name='__main__')
