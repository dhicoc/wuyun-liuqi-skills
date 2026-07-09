#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五运六气统一 CLI（optimization-sprint Phase 5）

把分散脚本收拢为单一入口，兼容原有能力，不删除旧命令。

核心子命令（calc / report / search / doctor）直接 import 调用，
其余子命令仍通过 subprocess 委托（逐步迁移中）。

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
import json
import sys
from typing import List, Optional, Sequence

from _common import setup_environment, add_scripts_dir_to_path, color, CYAN, GREEN, YELLOW, resolve_year_or_date

setup_environment(add_lib=False, add_scripts=True)
add_scripts_dir_to_path()


# ── 直接 import 的核心子命令 ──────────────────────────


def cmd_calc(args: argparse.Namespace) -> int:
    """直接调用 calculate_yunqi_api（无 subprocess 开销）。"""
    from calculate_yunqi_api import calculate_yunqi_api, _resolve_date, format_text
    from _common import highlight_key
    from yunqi_data import generate_summary, generate_current_step_focus

    date_str = resolve_year_or_date(args.date)

    # --explain-concept 模式
    if args.explain_concept:
        try:
            from yunqi_report import explain_concept
            print(explain_concept(args.explain_concept))
            return 0
        except Exception as e:
            print(f"概念解释错误: {e}", file=sys.stderr)
            return 2

    # --export 模式
    if args.export:
        import export_thought as et
        return et.run_export(date_str, args.export)

    try:
        result = calculate_yunqi_api(date_str)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 2

    # 自进化记录
    try:
        from self_evolve import log_usage
        concepts = []
        if args.level and args.level != "standard":
            concepts.append(f"level_{args.level}")
        log_usage(date_str, list(result.get("rag_keys", {}).values()) if result.get("rag_keys") else [], source="cli", concepts=concepts or None)
    except Exception:
        pass

    # 友好提示（默认今天时）
    if args.date in (None, 'today', '今天') and not args.json:
        print(f"（已默认使用今天日期: {result['date']}）\n")

    if args.html:
        from calculate_yunqi_api import run_html_report
        sys.stdout.write(run_html_report(date_str))
    elif args.focus:
        if args.focus == 'current-step':
            sys.stdout.write(generate_current_step_focus(result) + '\n')
        else:
            print(f"不支持的聚焦模式: {args.focus}", file=sys.stderr)
            return 1
    elif args.visual:
        from calculate_yunqi_api import run_visualize
        sys.stdout.write(run_visualize(date_str))
    elif args.report_type:
        from calculate_yunqi_api import run_yunqi_report
        output = run_yunqi_report(result['yunqi_year'], args.report_type, args.json)
        sys.stdout.write(output)
    elif args.explain:
        from calculate_yunqi_api import generate_explanation_output
        sys.stdout.write(generate_explanation_output(result) + '\n')
    elif args.json:
        sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    elif args.summary:
        sys.stdout.write(highlight_key(generate_summary(result)) + '\n')
    else:
        # 无任何输出旗标时默认 summary
        sys.stdout.write(highlight_key(generate_summary(result)) + '\n')
    sys.stdout.flush()
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    """直接调用 yunqi_report.generate_report（无 subprocess 开销）。"""
    from calculate_yunqi_api import calculate_yunqi_api, _resolve_date, run_yunqi_report

    year = args.year
    if year is None or str(year).lower() in ("today", "今天"):
        year = calculate_yunqi_api(_resolve_date("today"))["yunqi_year"]

    output = run_yunqi_report(year, args.audience, args.json)
    sys.stdout.write(output)
    sys.stdout.flush()
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    """直接调用 health_check（无 subprocess 开销）。"""
    import health_check
    return health_check.main() if hasattr(health_check, 'main') else 0


def cmd_search(args: argparse.Namespace) -> int:
    """直接调用 rag_search（无 subprocess 开销）。"""
    import rag_search as rs

    cli_args: List[str] = list(args.terms or [])
    if args.list_assets:
        print(rs.list_assets())
        return 0
    if args.assets:
        # 资产限定
        pass
    if getattr(args, "keys", None):
        # 精确 key 模式
        all_hits = []
        for k in args.keys:
            all_hits.extend(rs.lookup_key(k, assets=args.assets, full=args.full))
        if args.json:
            print(json.dumps({"keys": args.keys, "count": len(all_hits), "hits": all_hits, "mode": "exact_key"}, ensure_ascii=False, indent=2))
        else:
            print(rs.format_text(all_hits, args.keys, mode="exact_key"))
        return 0 if all_hits else 1
    if getattr(args, "date", None):
        bundle = rs.fetch_by_date(args.date, full=args.full)
        if args.json:
            print(json.dumps(bundle, ensure_ascii=False, indent=2))
        else:
            print(rs.format_date_bundle(bundle))
        return 0 if not bundle.get("missing") else 1
    if getattr(args, "semantic", None):
        from rag_semantic import semantic_search, format_text as fmt_sem
        q = args.semantic
        if args.terms:
            q = (q + " " + " ".join(args.terms)).strip()
        hits = semantic_search(q, limit=args.limit, assets=args.assets, full=args.full)
        if args.json:
            print(json.dumps({"query": q, "count": len(hits), "mode": "semantic", "hits": hits}, ensure_ascii=False, indent=2))
        else:
            print(fmt_sem(hits, q))
        return 0 if hits else 1
    # 关键词模式
    if not args.terms:
        print(rs.list_assets())
        return 0
    hits = rs.search(args.terms, assets=args.assets, limit=args.limit)
    if args.json:
        print(json.dumps({"terms": args.terms, "count": len(hits), "hits": hits, "mode": "keyword"}, ensure_ascii=False, indent=2))
    else:
        print(rs.format_text(hits, args.terms, mode="keyword"))
    return 0 if hits else 1


# ── 仍用 subprocess 委托的子命令（逐步迁移中） ──────


def cmd_map(args: argparse.Namespace) -> int:
    argv = [args.date, "--format", args.format]
    if args.output:
        argv.extend(["--output", args.output])
    if args.json:
        argv.append("--json")
    import export_thought_map
    return export_thought_map.main(argv)


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
    import socratic_learn
    return socratic_learn.main(argv)


def cmd_compare(args: argparse.Namespace) -> int:
    argv = list(args.dates or [])
    if args.json:
        argv.append("--json")
    import compare_py_js_yunqi
    return compare_py_js_yunqi.main(argv)


def cmd_profile(args: argparse.Namespace) -> int:
    argv = [args.birth_date]
    if args.city:
        argv.append(args.city)
    if args.json:
        argv.append("--json")
    import personal_yunqi_profile
    return personal_yunqi_profile.main(argv)


def cmd_export(args: argparse.Namespace) -> int:
    import export_thought as et
    rc = et.run_export(args.date, args.format)
    if rc == 0 and args.output:
        # run_export 默认写到 reports/generated/，用户指定 --output 时需要额外复制
        import shutil
        from pathlib import Path
        year = et.get_year_and_data(args.date).get('year', 'unknown')
        for stem, ext in [(f'thought_summary_{year}', '.md'), (f'thought_cards_{year}', '.anki.tsv'), (f'thought_cards_{year}', '.md')]:
            src = Path('reports/generated') / stem
            if src.exists():
                dst = Path(args.output)
                if dst.is_dir() or not dst.suffix:
                    dst.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst / src.name)
                else:
                    shutil.copy2(src, dst)
    return rc


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
    import learning_dashboard
    return learning_dashboard.main(argv)


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
            # 直接调用 cmd_calc，避免 subprocess 开销
            ns = argparse.Namespace(date='today', json=False, summary=True, visual=False,
                                    html=False, explain=False, focus=None, report_type=None,
                                    level='standard', explain_concept=None, export=None)
            rc = cmd_calc(ns)
        elif choice == "2":
            ns = argparse.Namespace(date='today', json=False, summary=False, visual=False,
                                    html=False, explain=False, focus='current-step', report_type=None,
                                    level='standard', explain_concept=None, export=None)
            rc = cmd_calc(ns)
        elif choice == "3":
            import socratic_learn
            rc = socratic_learn.main(["today"])
        elif choice == "4":
            import export_thought_map
            rc = export_thought_map.main(["today", "--format", "both"])
        elif choice == "5":
            ns = argparse.Namespace(year='today', audience='student', json=False)
            rc = cmd_report(ns)
        elif choice == "6":
            rc = cmd_doctor(argparse.Namespace())
        elif choice == "7":
            import learning_dashboard
            rc = learning_dashboard.main([])
        elif choice == "8":
            ns = argparse.Namespace(terms=None, assets=None, keys=None, date=None,
                                    semantic=None, full=False, limit=10, json=False,
                                    list_assets=True)
            rc = cmd_search(ns)
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
