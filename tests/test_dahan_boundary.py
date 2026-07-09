#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大寒定年边界测试（optimization-sprint Phase 3）

用法:
  python tests/test_dahan_boundary.py
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, os.path.join(SCRIPTS, "lib"))

from _common import setup_environment  # noqa: E402
setup_environment(add_lib=True, add_scripts=True)

from calculate_yunqi_api import calculate_yunqi_api  # noqa: E402

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "dahan_boundary.json")


def main():
    with open(FIXTURE, "r", encoding="utf-8") as f:
        data = json.load(f)

    failed = []
    for case in data["cases"]:
        date = case["date"]
        expected = case["expected_yunqi_year"]
        result = calculate_yunqi_api(date)
        actual = result.get("yunqi_year")
        ok = actual == expected
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {date} → yunqi_year={actual} (expected {expected})")
        if not ok:
            failed.append((date, expected, actual))

    if failed:
        print(f"\n❌ {len(failed)} case(s) failed")
        sys.exit(1)
    print(f"\n✅ all {len(data['cases'])} dahan boundary cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
