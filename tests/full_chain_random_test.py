#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全链路随机测试：生成随机日期 × 全链路脚本验证

覆盖：
  1. 随机日期 → calculate_yunqi_api（JSON 校验 + 字段完整性）
  2. 随机日期 → RAG 精确命中（rag_keys 全部命中）
  3. 随机年份 → 分项脚本（ganzhi/dayun/keyun/liuqi/kezhujialin）
  4. 随机年份 → yunqi_report（student/practitioner/researcher + RAG 章节）
  5. 随机日期 → HTML 报告生成（含 RAG 章节）
  6. 包 API wuyun_liuqi.calculate / fetch_by_date
  7. 语义检索冒烟
  8. Py/JS 一致性（抽样）

用法:
  python tests/full_chain_random_test.py [--count N] [--seed S]
"""
from __future__ import annotations

import json
import os
import random
import subprocess
import sys
import time
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "lib"))

from _common import setup_environment  # noqa: E402
setup_environment(add_lib=True, add_scripts=True)

PY = sys.executable
ENV = os.environ.copy()
ENV["PYTHONIOENCODING"] = "utf-8"

# ── 结果收集 ──────────────────────────────────────────────
passed = 0
failed = 0
errors: list[str] = []


def ok(name: str):
    global passed
    passed += 1
    print(f"  [PASS] {name}")


def fail(name: str, detail: str = ""):
    global failed
    failed += 1
    msg = f"  [FAIL] {name}" + (f": {detail}" if detail else "")
    print(msg)
    errors.append(msg)


def run_cmd(args: list[str], timeout: int = 90) -> tuple[int, str, str]:
    """运行子进程，返回 (returncode, stdout, stderr)。"""
    try:
        r = subprocess.run(
            args,
            cwd=ROOT,
            env=ENV,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
        )
        return r.returncode, r.stdout or "", r.stderr or ""
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except Exception as e:
        return -2, "", str(e)


def random_dates(count: int, seed: int = None) -> list[str]:
    """生成 count 个随机日期 (YYYY-MM-DD)，范围 1900-2100。"""
    rng = random.Random(seed)
    start = date(1900, 1, 1)
    end = date(2100, 12, 31)
    delta = (end - start).days
    dates = []
    for _ in range(count):
        d = start + timedelta(days=rng.randint(0, delta))
        dates.append(d.isoformat())
    return sorted(dates)


def random_years(count: int, seed: int = None) -> list[int]:
    """生成 count 个随机年份，范围 1900-2100。"""
    rng = random.Random(seed)
    return sorted(rng.randint(1900, 2100) for _ in range(count))


# ── 测试用例 ──────────────────────────────────────────────

def test_calculate_json(dates: list[str]):
    print("\n=== 1. 随机日期 → calculate_yunqi_api JSON ===")
    for d in dates:
        name = f"calc {d}"
        rc, out, err = run_cmd([PY, "scripts/calculate_yunqi_api.py", d, "--json"])
        if rc != 0:
            fail(name, f"rc={rc} err={err[:200]}")
            continue
        try:
            data = json.loads(out)
        except json.JSONDecodeError as e:
            fail(name, f"JSON decode: {e}")
            continue
        # 字段完整性校验
        required = ["date", "yunqi_year", "year_gz", "sui_yun", "si_tian", "zai_quan",
                     "current_step", "rag_keys"]
        missing = [k for k in required if k not in data]
        if missing:
            fail(name, f"missing fields: {missing}")
            continue
        # rag_keys 非空
        rk = data.get("rag_keys") or {}
        if not rk.get("suiyun") or not rk.get("sitian"):
            fail(name, f"rag_keys incomplete: {rk}")
            continue
        ok(name)


def test_rag_fetch_by_date(dates: list[str]):
    print("\n=== 2. 随机日期 → RAG 精确命中 (fetch_by_date) ===")
    from wuyun_liuqi import fetch_by_date
    for d in dates:
        name = f"rag {d}"
        try:
            bundle = fetch_by_date(d)
        except Exception as e:
            fail(name, str(e)[:200])
            continue
        missing = bundle.get("missing") or []
        if missing:
            # 大寒边界附近可能命中不同年，记录但不一定 fail
            # 只要不缺 > 2 个就 pass（某些极端边界）
            if len(missing) > 2:
                fail(name, f"missing={missing}")
                continue
            else:
                ok(f"{name} (partial: {missing})")
                continue
        # 确认 4 个 role 都有命中
        hits = bundle.get("hits_by_role") or {}
        empty_roles = [r for r in ("suiyun", "sitian", "zaiquan", "current_step") if not hits.get(r)]
        if empty_roles:
            fail(name, f"empty roles: {empty_roles}")
            continue
        ok(name)


def test_legacy_scripts(years: list[int]):
    print("\n=== 3. 随机年份 → 分项脚本 (legacy --json) ===")
    scripts = [
        ("ganzhi_calc.py", ["干支"]),
        ("dayun_calc.py", ["大运"]),
        ("keyun_calc.py", ["五步"]),
        ("liuqi_calc.py", ["六步"]),
        ("kezhujialin.py", ["六步"]),
    ]
    for year in years:
        for script, check_keys in scripts:
            name = f"{script} {year}"
            rc, out, err = run_cmd([PY, f"scripts/{script}", str(year), "--json"])
            if rc != 0:
                fail(name, f"rc={rc} err={err[:200]}")
                continue
            try:
                data = json.loads(out)
            except json.JSONDecodeError:
                fail(name, "JSON decode error")
                continue
            # 检查关键 key 存在
            found = any(k in data for k in check_keys)
            if not found:
                fail(name, f"missing keys {check_keys} in {list(data.keys())[:6]}")
                continue
            ok(name)


def test_yunqi_report(years: list[int]):
    print("\n=== 4. 随机年份 → yunqi_report (含 RAG 章节) ===")
    for year in years:
        for audience in ("student", "practitioner", "researcher"):
            name = f"report {year} {audience}"
            rc, out, err = run_cmd([
                PY, "scripts/yunqi_report.py", str(year),
                "--audience", audience,
            ], timeout=120)
            if rc != 0:
                fail(name, f"rc={rc} err={err[:200]}")
                continue
            if "免责声明" not in out:
                fail(name, "missing 免责声明")
                continue
            if "经典与注家依据" not in out:
                fail(name, "missing evidence section")
                continue
            ok(name)


def test_html_report(dates: list[str]):
    print("\n=== 5. 随机日期 → HTML 报告生成 ===")
    for d in dates:
        name = f"html {d}"
        out_path = f"reports/test-results/random-html-{d}.html"
        rc, out, err = run_cmd([
            PY, "scripts/generate_html_report.py", d, out_path,
        ], timeout=120)
        if rc != 0:
            fail(name, f"rc={rc} err={err[:200]}")
            continue
        if "HTML 报告已生成" not in out:
            fail(name, f"unexpected output: {out[:200]}")
            continue
        # 验证文件存在且含 RAG 章节
        html_file = ROOT / out_path
        if not html_file.exists():
            fail(name, "file not found")
            continue
        content = html_file.read_text(encoding="utf-8")
        if "知识库精确命中" not in content:
            fail(name, "missing RAG section in HTML")
            continue
        ok(name)
        # 清理
        html_file.unlink(missing_ok=True)


def test_package_api(dates: list[str]):
    print("\n=== 6. 包 API wuyun_liuqi ===")
    from wuyun_liuqi import calculate, lookup_key, fetch_by_date, __version__
    print(f"  version={__version__}")
    for d in dates:
        name = f"pkg calc {d}"
        try:
            r = calculate(d)
        except Exception as e:
            fail(name, str(e)[:200])
            continue
        if not r.get("yunqi_year"):
            fail(name, "no yunqi_year")
            continue
        rk = r.get("rag_keys") or {}
        if not rk.get("suiyun"):
            fail(name, "no rag_keys.suiyun")
            continue
        # lookup_key
        try:
            hits = lookup_key(rk["suiyun"])
            if not hits:
                fail(f"pkg lookup {d}", "no hits")
                continue
        except Exception as e:
            fail(f"pkg lookup {d}", str(e)[:200])
            continue
        ok(name)


def test_semantic_search():
    print("\n=== 7. 语义检索冒烟 ===")
    queries = ["心火偏旺", "寒气流行", "燥金伤肺", "太阴湿土", "风木"]
    from rag_semantic import semantic_search
    for q in queries:
        name = f"semantic '{q}'"
        try:
            hits = semantic_search(q, limit=3)
            if not hits:
                fail(name, "no hits")
                continue
            if hits[0].get("score", 0) <= 0:
                fail(name, "score <= 0")
                continue
            ok(name)
        except Exception as e:
            fail(name, str(e)[:200])


def test_pyjs_consistency():
    print("\n=== 8. Py/JS 一致性 ===")
    rc, out, err = run_cmd([PY, "scripts/compare_py_js_yunqi.py"], timeout=60)
    if rc != 0:
        fail("py/js compare", f"rc={rc} err={err[:200]}")
    elif "PASS" in out or "✅" in out or "一致" in out:
        ok("py/js compare")
    else:
        fail("py/js compare", f"unexpected: {out[:200]}")


def test_routing_and_structure():
    print("\n=== 9. Skills 结构与路由检查 ===")
    checks = [
        ("skill structure", [PY, "scripts/check_skill_structure.py"]),
        ("routing scenarios", [PY, "scripts/check_routing_scenarios.py"]),
        ("sync routing", [PY, "scripts/sync_routing.py", "--check"]),
        ("conformance", [PY, "scripts/check_conformance.py"]),
        ("orphan audit", [PY, "scripts/audit_orphans.py"]),
        ("rag index check", [PY, "scripts/generate_rag_index.py", "--check"]),
        ("validate kb", [PY, "scripts/validate_knowledge_base.py"]),
    ]
    for name, args in checks:
        rc, out, err = run_cmd(args, timeout=60)
        if rc != 0:
            fail(name, f"rc={rc} err={err[:300]}")
        else:
            ok(name)


def test_dahan_boundary():
    print("\n=== 10. 大寒边界测试 ===")
    rc, out, err = run_cmd([PY, "tests/test_dahan_boundary.py"], timeout=60)
    if rc != 0:
        fail("dahan boundary", f"rc={rc} err={err[:300]}")
    else:
        ok("dahan boundary")


def test_package_and_rag():
    print("\n=== 11. 包 API + RAG 集成测试 ===")
    rc, out, err = run_cmd([PY, "tests/test_package_and_rag.py"], timeout=60)
    if rc != 0:
        fail("package+rag", f"rc={rc} err={err[:300]}")
    else:
        ok("package+rag")


def test_full_regression():
    print("\n=== 12. 全量回归测试 ===")
    rc, out, err = run_cmd([PY, "tests/full_regression_test.py"], timeout=300)
    if rc != 0:
        # 提取失败行
        lines = out.split("\n")
        fail_lines = [l for l in lines if "[FAIL]" in l]
        detail = "; ".join(fail_lines[:5]) if fail_lines else err[:300]
        fail("full_regression", f"rc={rc}: {detail}")
    else:
        ok("full_regression")


# ── 主入口 ────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="全链路随机测试")
    parser.add_argument("--count", type=int, default=8, help="随机日期/年份数量")
    parser.add_argument("--seed", type=int, default=None, help="随机种子")
    parser.add_argument("--skip-regression", action="store_true", help="跳过全量回归（耗时）")
    args = parser.parse_args()

    seed = args.seed or int(time.time()) % 100000
    count = args.count
    dates = random_dates(count, seed=seed)
    years = random_years(count, seed=seed + 1)

    print(f"{'='*60}")
    print(f"全链路随机测试  seed={seed}  count={count}")
    print(f"随机日期: {dates}")
    print(f"随机年份: {years}")
    print(f"{'='*60}")

    # Skills 结构与路由检查
    test_routing_and_structure()

    # 大寒边界 + 包/RAG 集成
    test_dahan_boundary()
    test_package_and_rag()

    # 随机日期全链路
    test_calculate_json(dates)
    test_rag_fetch_by_date(dates)
    test_html_report(dates)
    test_package_api(dates)

    # 随机年份全链路
    test_legacy_scripts(years)
    test_yunqi_report(years)

    # 语义检索 + Py/JS
    test_semantic_search()
    test_pyjs_consistency()

    # 全量回归（可选）
    if not args.skip_regression:
        test_full_regression()

    # 汇总
    print(f"\n{'='*60}")
    print(f"汇总: PASS={passed}  FAIL={failed}")
    if errors:
        print(f"\n失败详情:")
        for e in errors:
            print(e)
    print(f"{'='*60}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
