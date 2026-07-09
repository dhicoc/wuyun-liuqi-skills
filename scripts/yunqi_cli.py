#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五运六气统一 CLI（optimization-sprint Phase 5）

把分散脚本收拢为单一入口，兼容原有能力，不删除旧命令。

用法:
  python scripts/yunqi_cli.py --help
  python scripts/yunqi_cli.py calc today --summary
  python scripts/yunqi_cli.py report 2026 --audience student
  python scripts/yunqi_cli.py map today
  python scripts/yunqi_cli.py learn today
  python scripts/yunqi_cli.py learn today --interactive
  python scripts/yunqi_cli.py compare
  python scripts/yunqi_cli.py profile 2003-04-19 杭州
  python scripts/yunqi_cli.py interactive
  python scripts/yunqi_cli.py doctor
  python scripts/yunqi_cli.py search 司天
  python scripts/yunqi_cli.py dashboard

等价别名（若 PATH 不便，始终可用本文件）:
  python scripts/yunqi_cli.py <subcommand> ...
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from typing import List, Optional, Sequence

from _common import setup_environment, add_scripts_dir_to_path, color, CYAN, GREEN, YELLOW

setup_environment(add_lib=False, add_scripts=True)
add_scripts_dir_to_path()

SCRIPTS = os.path.dirname(os.path.abspath(__file__))


def _run_py(script: str, argv: List[str]) -> int:
    path = os.path.join(SCRIPTS, script)
    cmd = [sys.executable, path] + argv
    return subprocess.call(cmd)


def cmd_calc(args: argparse.Namespace) -> int:
    """委托 calculate_yunqi_api.py（保留全部旗标）。"""
    argv: List[str] = [args.date]
    if args.json:
        argv.append("--json")
    if args.summary:
        argv.append("--summary")
    if args.visual:
        argv.append("--visual")
    if args.html:
        argv.append("--html")
    if args.explain:
        argv.append("--explain")
    if args.focus:
        argv.extend(["--focus", args.focus])
    if args.report_type:
        argv.extend(["--report-type", args.report_type])
    if args.level and args.level != "standard":
        argv.extend(["--level", args.level])
    if args.explain_concept:
        argv.extend(["--explain-concept", args.explain_concept])
    if args.export:
        argv.extend(["--export", args.export])
    # 无任何输出旗标时默认 summary（CLI 友好）
    flags = (
        args.json or args.summary or args.visual or args.html or args.explain
        or args.focus or args.report_type or args.explain_concept or args.export
    )
    if not flags:
        argv.append("--summary")
    return _run_py("calculate_yunqi_api.py", argv)


def cmd_report(args: argparse.Namespace) -> int:
    year = args.year
    if year is None or str(year).lower() in ("today", "今天"):
        from calculate_yunqi_api import calculate_yunqi_api, _resolve_date
        year = str(calculate_yunqi_api(_resolve_date("today"))["yunqi_year"])
    argv = [str(year), "--audience", args.audience]
    if args.json:
        argv.append("--json")
    return _run_py("yunqi_report.py", argv)


def cmd_map(args: argparse.Namespace) -> int:
    argv = [args.date, "--format", args.format]
    if args.output:
        argv.extend(["--output", args.output])
    if args.json:
        argv.append("--json")
    return _run_py("export_thought_map.py", argv)


def cmd_learn(args: argparse.Namespace) -> int:
    argv = [args.date]
    if args.concept:
        argv.extend(["--concept", args.concept])
    if args.interactive:
        argv.append("--interactive")
    if args.output:
        argv.extend(["--output", args.output])
    if args.json:
        argv.append("--json")
    if args.no_file:
        argv.append("--no-file")
    return _run_py("socratic_learn.py", argv)


def cmd_compare(args: argparse.Namespace) -> int:
    argv = list(args.dates or [])
    if args.json:
        argv.append("--json")
    return _run_py("compare_py_js_yunqi.py", argv)


def cmd_profile(args: argparse.Namespace) -> int:
    argv = [args.birth_date]
    if args.city:
        argv.append(args.city)
    if args.json:
        argv.append("--json")
    return _run_py("personal_yunqi_profile.py", argv)


def cmd_export(args: argparse.Namespace) -> int:
    argv = [args.date, "--format", args.format]
    if args.output:
        argv.extend(["--output", args.output])
    return _run_py("export_thought.py", argv)


def cmd_doctor(args: argparse.Namespace) -> int:
    return _run_py("health_check.py", [])


def cmd_search(args: argparse.Namespace) -> int:
    argv: List[str] = list(args.terms or [])
    if args.list_assets:
        argv.append("--list-assets")
    if args.assets:
        for a in args.assets:
            argv.extend(["--asset", a])
    if getattr(args, "keys", None):
        for k in args.keys:
            argv.extend(["--key", k])
    if getattr(args, "date", None):
        argv.extend(["--date", args.date])
    if getattr(args, "semantic", None):
        argv.extend(["--semantic", args.semantic])
    if getattr(args, "full", False):
        argv.append("--full")
    if args.limit:
        argv.extend(["--limit", str(args.limit)])
    if args.json:
        argv.append("--json")
    return _run_py("rag_search.py", argv)


def cmd_dashboard(args: argparse.Namespace) -> int:
    argv: List[str] = []
    if args.json:
        argv.append("--json")
    if args.html:
        argv.append("--html")
    if args.output:
        argv.extend(["--output", args.output])
    if args.stdout:
        argv.append("--stdout")
    return _run_py("learning_dashboard.py", argv)


def cmd_interactive(_args: argparse.Namespace) -> int:
    """简易菜单交互。"""
    menu = """
  1) 今天运气摘要 (calc today --summary)
  2) 当前步位聚焦 (calc today --focus current-step)
  3) 苏格拉底学习会话 (learn today)
  4) 思想地图 (map today)
  5) 年度报告学生版 (report today)
  6) 健康检查 (doctor)
  7) 学习路径仪表盘 (dashboard)
  8) 文献检索提示 (search --list-assets)
  0) 退出
"""
    print(color("五运六气 · 统一入口", CYAN))
    print(menu)
    while True:
        try:
            choice = input(color("选择> ", GREEN)).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if choice in ("0", "q", "quit", "exit"):
            return 0
        if choice == "1":
            rc = _run_py("calculate_yunqi_api.py", ["today", "--summary"])
        elif choice == "2":
            rc = _run_py("calculate_yunqi_api.py", ["today", "--focus", "current-step"])
        elif choice == "3":
            rc = _run_py("socratic_learn.py", ["today"])
        elif choice == "4":
            rc = _run_py("export_thought_map.py", ["today", "--format", "both"])
        elif choice == "5":
            from calculate_yunqi_api import calculate_yunqi_api, _resolve_date
            y = calculate_yunqi_api(_resolve_date("today"))["yunqi_year"]
            rc = _run_py("yunqi_report.py", [str(y), "--audience", "student"])
        elif choice == "6":
            rc = _run_py("health_check.py", [])
        elif choice == "7":
            rc = _run_py("learning_dashboard.py", [])
        elif choice == "8":
            rc = _run_py("rag_search.py", ["--list-assets"])
        else:
            print(color("无效选项，请输入 0-8", YELLOW))
            continue
        if rc != 0:
            print(color(f"（子命令退出码 {rc}）", YELLOW))
        print()
        print(menu)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="yunqi_cli.py",
        description="五运六气统一命令行入口",
        epilog="""常用:
  python scripts/yunqi_cli.py calc today --summary
  python scripts/yunqi_cli.py learn today
  python scripts/yunqi_cli.py search 司天
  python scripts/yunqi_cli.py dashboard
  python scripts/yunqi_cli.py interactive

底层脚本仍可直接调用；本入口为聚合与发现层。
详见 docs/optimization-sprint.md
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", help="子命令")

    p_calc = sub.add_parser("calc", help="日期运气推算（主计算）")
    p_calc.add_argument("date", nargs="?", default="today")
    p_calc.add_argument("--json", action="store_true")
    p_calc.add_argument("--summary", action="store_true")
    p_calc.add_argument("--visual", action="store_true")
    p_calc.add_argument("--html", action="store_true")
    p_calc.add_argument("--explain", action="store_true")
    p_calc.add_argument("--focus", choices=["current-step"])
    p_calc.add_argument("--report-type", choices=["student", "practitioner", "researcher"])
    p_calc.add_argument("--level", choices=["simple", "standard", "deep"], default="standard")
    p_calc.add_argument("--explain-concept")
    p_calc.add_argument("--export", choices=["summary", "cards", "pdf", "all"])
    p_calc.set_defaults(func=cmd_calc)

    p_report = sub.add_parser("report", help="年度综合报告")
    p_report.add_argument("year", nargs="?", default="today", help="年份或 today")
    p_report.add_argument("--audience", choices=["student", "practitioner", "researcher"], default="student")
    p_report.add_argument("--json", action="store_true")
    p_report.set_defaults(func=cmd_report)

    p_map = sub.add_parser("map", help="思想地图 Mermaid")
    p_map.add_argument("date", nargs="?", default="today")
    p_map.add_argument("--format", choices=["concept", "structure", "both"], default="both")
    p_map.add_argument("--output", "-o")
    p_map.add_argument("--json", action="store_true")
    p_map.set_defaults(func=cmd_map)

    p_learn = sub.add_parser("learn", help="苏格拉底学习会话")
    p_learn.add_argument("date", nargs="?", default="today")
    p_learn.add_argument("--concept")
    p_learn.add_argument("--interactive", "-i", action="store_true")
    p_learn.add_argument("--output", "-o")
    p_learn.add_argument("--json", action="store_true")
    p_learn.add_argument("--no-file", action="store_true")
    p_learn.set_defaults(func=cmd_learn)

    p_cmp = sub.add_parser("compare", help="Py/JS 关键字段对比")
    p_cmp.add_argument("dates", nargs="*")
    p_cmp.add_argument("--json", action="store_true")
    p_cmp.set_defaults(func=cmd_compare)

    p_prof = sub.add_parser("profile", help="个人运气体质")
    p_prof.add_argument("birth_date", help="出生日期 YYYY-MM-DD")
    p_prof.add_argument("city", nargs="?", default=None)
    p_prof.add_argument("--json", action="store_true")
    p_prof.set_defaults(func=cmd_profile)

    p_exp = sub.add_parser("export", help="思想摘要/卡片/PDF")
    p_exp.add_argument("date", nargs="?", default="today")
    p_exp.add_argument("--format", choices=["summary", "cards", "pdf", "all"], default="summary")
    p_exp.add_argument("--output", "-o")
    p_exp.set_defaults(func=cmd_export)

    p_doc = sub.add_parser("doctor", help="环境健康检查")
    p_doc.set_defaults(func=cmd_doctor)

    p_search = sub.add_parser("search", help="RAG 检索（关键词 / --key / --date / --semantic）")
    p_search.add_argument("terms", nargs="*", help="关键词（多个 AND）")
    p_search.add_argument("--asset", action="append", dest="assets")
    p_search.add_argument("--key", "-k", action="append", dest="keys", help="精确 rag_key")
    p_search.add_argument("--date", "-d", default=None, help="按日打包 rag_keys")
    p_search.add_argument("--semantic", "-s", default=None, help="口语语义检索")
    p_search.add_argument("--full", action="store_true", help="JSON 附完整 entry")
    p_search.add_argument("--limit", type=int, default=10)
    p_search.add_argument("--json", action="store_true")
    p_search.add_argument("--list-assets", action="store_true")
    p_search.set_defaults(func=cmd_search)

    p_dash = sub.add_parser("dashboard", help="学习路径仪表盘")
    p_dash.add_argument("--json", action="store_true")
    p_dash.add_argument("--html", action="store_true")
    p_dash.add_argument("--output", "-o")
    p_dash.add_argument("--stdout", action="store_true")
    p_dash.set_defaults(func=cmd_dashboard)

    p_int = sub.add_parser("interactive", help="菜单交互模式")
    p_int.set_defaults(func=cmd_interactive)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    if not getattr(args, "command", None):
        parser.print_help()
        print()
        print(color("提示: 快速开始 → python scripts/yunqi_cli.py calc today --summary", CYAN))
        print(color("      学习模式 → python scripts/yunqi_cli.py learn today", CYAN))
        print(color("      文献检索 → python scripts/yunqi_cli.py search 司天", CYAN))
        print(color("      学习仪表盘 → python scripts/yunqi_cli.py dashboard", CYAN))
        return 0
    return int(args.func(args) or 0)


if __name__ == "__main__":
    sys.exit(main())
