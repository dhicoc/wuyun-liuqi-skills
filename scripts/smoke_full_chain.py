#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全链路冒烟测试 + 随机数据生成器
生成随机日期，完整测试 skills 链路：
1. calculate_yunqi_api (核心推算 + rag_keys)
2. yunqi_report (报告生成)
3. demo_full_chain (推算 + RAG 检索演示)
4. advanced_alignment --mock (天气/体质高级对齐)
5. 可选：HTML 生成、self_evolve 记录

运行:
  python scripts/smoke_full_chain.py --count 10
  python scripts/smoke_full_chain.py --dates 2026-01-15,2030-06-01
"""
import argparse
import datetime
import json
import os
import random
import subprocess
import sys

from _common import setup_environment
setup_environment(add_lib=False)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable

def rand_date(start_year=1920, end_year=2040):
    year = random.randint(start_year, end_year)
    month = random.randint(1, 12)
    # 安全日，避免月末问题
    day = random.randint(1, 27)
    return f"{year:04d}-{month:02d}-{day:02d}"

def run_cmd(args, timeout=60):
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    res = subprocess.run(
        args, cwd=ROOT, env=env,
        capture_output=True, text=True, encoding='utf-8', timeout=timeout
    )
    return res

def test_core_api(date_str):
    r = run_cmd([PY, 'scripts/calculate_yunqi_api.py', date_str, '--json'])
    if r.returncode != 0:
        raise RuntimeError(f"API failed: {r.stderr[:200]}")
    data = json.loads(r.stdout)
    if 'yunqi_year' not in data or 'rag_keys' not in data:
        raise RuntimeError("Missing required fields in API response")
    # 再跑 summary
    r2 = run_cmd([PY, 'scripts/calculate_yunqi_api.py', date_str, '--summary'])
    if len(r2.stdout) < 30:
        raise RuntimeError("Summary too short")
    return data

def test_report(yunqi_year):
    r = run_cmd([PY, 'scripts/yunqi_report.py', str(yunqi_year), '--audience', 'student'])
    out = r.stdout
    if r.returncode != 0 or ('岁运' not in out and '司天' not in out):
        raise RuntimeError("Report generation suspicious")
    return True

def test_demo(date_str):
    r = run_cmd([PY, 'scripts/demo_full_chain.py', date_str], timeout=90)
    if r.returncode != 0 or len(r.stdout) < 100:
        raise RuntimeError("demo_full_chain failed or too short")
    return True

def test_advanced_mock(date_str, city):
    r = run_cmd([PY, 'scripts/advanced_alignment.py', '--date', date_str, '--city', city, '--mock', '--json'], timeout=90)
    if r.returncode != 0:
        raise RuntimeError(f"advanced failed: {r.stderr[:150]}")
    adv = json.loads(r.stdout)
    if not ('base_yunqi' in adv or 'advanced_synthesis' in adv):
        raise RuntimeError("advanced_alignment missing synthesis")
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=8, help='随机测试数量')
    parser.add_argument('--dates', type=str, default='', help='逗号分隔的具体日期列表')
    parser.add_argument('--seed', type=int, default=42)
    args = parser.parse_args()

    random.seed(args.seed)

    if args.dates:
        test_dates = [d.strip() for d in args.dates.split(',') if d.strip()]
    else:
        test_dates = [rand_date() for _ in range(args.count)]

    cities = ['北京', '杭州', '拉萨', '广州', '武汉']

    print("=" * 60)
    print("五运六气 Skills 全链路随机冒烟测试")
    print(f"测试日期: {len(test_dates)} 个")
    print("=" * 60)

    passed = 0
    failed = 0
    details = []

    for i, d in enumerate(test_dates, 1):
        city = random.choice(cities)
        print(f"\n[{i}/{len(test_dates)}] {d} @ {city}")
        try:
            data = test_core_api(d)
            yunqi_year = data['yunqi_year']
            print(f"  ✓ calculate_yunqi_api -> {yunqi_year}年 {data['year_gz']}")

            test_report(yunqi_year)
            print(f"  ✓ yunqi_report (student)")

            test_demo(d)
            print(f"  ✓ demo_full_chain")

            test_advanced_mock(d, city)
            print(f"  ✓ advanced_alignment --mock")

            # 可选：快速 HTML（不检查内容，只看是否崩溃）
            # run_cmd([PY, 'scripts/generate_html_report.py', d, 'reports/generated/smoke-test.html'], timeout=30)

            passed += 1
            details.append((d, 'PASS', yunqi_year))
        except Exception as e:
            failed += 1
            msg = str(e)[:120]
            print(f"  ✗ FAILED: {msg}")
            details.append((d, 'FAIL', msg))

    print("\n" + "=" * 60)
    print(f"结果: {passed} 通过, {failed} 失败")
    for d, status, info in details:
        print(f"  {status}: {d} -> {info}")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)
    print("全链路随机冒烟测试全部通过！")

if __name__ == '__main__':
    main()
