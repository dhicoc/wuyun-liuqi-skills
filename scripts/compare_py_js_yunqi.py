#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python / JavaScript 运气推算一致性对比（optimization-sprint P3-3）

以 Python 为主真相源，对比 JS 版关键字段是否一致。

用法:
  python scripts/compare_py_js_yunqi.py
  python scripts/compare_py_js_yunqi.py 2026-01-15 2026-06-29
  python scripts/compare_py_js_yunqi.py --json

依赖: 本机可用 node + scripts/calculate_yunqi_api.js（lunar-javascript）
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional, Sequence, Tuple

from _common import setup_environment, add_scripts_dir_to_path

setup_environment(add_lib=True, add_scripts=True)
add_scripts_dir_to_path()

from calculate_yunqi_api import calculate_yunqi_api  # noqa: E402

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JS_ENTRY = os.path.join(SCRIPT_DIR, "calculate_yunqi_api.js")

# 与 Agent / RAG 强相关的关键路径（点号路径）
CRITICAL_PATHS = [
    "date",
    "yunqi_year",
    "year_gz",
    "year_gan",
    "year_zhi",
    "sexagenary_index",
    "shengxiao",
    "day_gz",
    "sui_yun.name",
    "sui_yun.element",
    "sui_yun.status",
    "sui_yun.code",
    "sui_yun.tiangan",
    "si_tian",
    "zai_quan",
    "current_step.step_number",
    "current_step.name",
    "current_step.zhu_qi",
    "current_step.ke_qi",
    "current_step.relation",
    "current_step.shun_ni",
    "tong_hua.tianfu",
    "tong_hua.suihui",
    "tong_hua.taiyi_tianfu",
    "tong_hua.pingqi",
    "rag_keys.suiyun",
    "rag_keys.sitian",
    "rag_keys.zaiquan",
    "rag_keys.current_step",
    "jieqi_dates.大寒",
    "jieqi_dates.大寒(终)",
]

DEFAULT_DATES = [
    "2026-01-15",  # 大寒前
    "2026-01-20",  # 大寒后
    "2025-01-19",
    "2025-01-20",
    "2026-06-29",
]


def _get_path(obj: Any, path: str) -> Any:
    cur = obj
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def run_js_api(date_str: str) -> Dict[str, Any]:
    """通过 node 调用 JS 版 calculateYunqiApi，返回 dict。"""
    if not os.path.isfile(JS_ENTRY):
        raise FileNotFoundError(f"找不到 JS 入口: {JS_ENTRY}")

    # 内联小脚本，避免依赖 CLI 参数解析差异
    node_src = (
        "const {calculateYunqiApi}=require(%s);"
        "const d=process.argv[1];"
        "process.stdout.write(JSON.stringify(calculateYunqiApi(d)));"
    ) % json.dumps(JS_ENTRY.replace("\\", "/"))

    result = subprocess.run(
        ["node", "-e", node_src, date_str],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=os.path.dirname(SCRIPT_DIR),
        timeout=60,
    )
    if result.returncode != 0:
        err = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"node 执行失败: {err}")
    raw = (result.stdout or "").strip()
    if not raw:
        raise RuntimeError("node 无输出")
    return json.loads(raw)


def compare_one(date_str: str) -> Dict[str, Any]:
    py = calculate_yunqi_api(date_str)
    js = run_js_api(date_str)
    mismatches: List[Dict[str, Any]] = []
    for path in CRITICAL_PATHS:
        pv = _get_path(py, path)
        jv = _get_path(js, path)
        if pv != jv:
            mismatches.append({"path": path, "python": pv, "javascript": jv})
    return {
        "date": date_str,
        "ok": len(mismatches) == 0,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "python_yunqi_year": py.get("yunqi_year"),
        "js_yunqi_year": js.get("yunqi_year"),
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="对比 Python / JavaScript 运气推算关键字段（以 Python 为准）",
        epilog="示例:\n  python scripts/compare_py_js_yunqi.py\n  python scripts/compare_py_js_yunqi.py 2026-06-29 --json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "dates",
        nargs="*",
        help="要对比的日期 YYYY-MM-DD；默认使用大寒边界 + 年中样例",
    )
    parser.add_argument("--json", action="store_true", help="输出 JSON 报告")
    args = parser.parse_args(list(argv) if argv is not None else None)

    dates = list(args.dates) if args.dates else list(DEFAULT_DATES)
    results: List[Dict[str, Any]] = []
    failed = 0

    try:
        # 先探测 node
        probe = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if probe.returncode != 0:
            print("错误: 需要可用的 node 命令", file=sys.stderr)
            return 2
    except FileNotFoundError:
        print("错误: 未找到 node，请安装 Node.js 后再运行", file=sys.stderr)
        return 2

    for d in dates:
        try:
            row = compare_one(d)
        except Exception as exc:
            row = {
                "date": d,
                "ok": False,
                "mismatch_count": -1,
                "mismatches": [],
                "error": str(exc),
            }
        results.append(row)
        if not row.get("ok"):
            failed += 1

    if args.json:
        payload = {
            "total": len(results),
            "passed": len(results) - failed,
            "failed": failed,
            "critical_paths": CRITICAL_PATHS,
            "results": results,
            "truth": "python",
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("Python ↔ JavaScript 运气一致性对比（关键字段）")
        print("=" * 50)
        for row in results:
            if row.get("error"):
                print(f"[ERROR] {row['date']}: {row['error']}")
                continue
            status = "PASS" if row["ok"] else "FAIL"
            print(
                f"[{status}] {row['date']}  "
                f"yunqi_year py={row.get('python_yunqi_year')} js={row.get('js_yunqi_year')}  "
                f"mismatches={row['mismatch_count']}"
            )
            for m in row.get("mismatches") or []:
                print(f"    · {m['path']}: py={m['python']!r}  js={m['javascript']!r}")
        print("=" * 50)
        print(f"合计: {len(results) - failed}/{len(results)} 通过")
        if failed:
            print("提示: 以 Python 输出为准；JS 偏差需同步 yunqi_data.js / calculate_yunqi_api.js")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
