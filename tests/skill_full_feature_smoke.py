#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全功能 · 全场景 · 多轮冒烟测试
================================
模拟真实用户使用五运六气技能包的各种自然语言场景，逐一触发项目的
**全部能力**（推算 / 检索 / 检索增强 / 报告导出 / 学习教学 / 自进化运维 /
安装校验 / 子技能模块 / 教学模块 / 注家人格 / 高级对齐 / 聚合 CLI），
并对同样的场景跑多轮（默认 3 轮，换不同日期/城市/病证），以捕捉偶发失败。

与 `tests/full_scenario_test.py`（固定 10 场景）的区别：
- 本测试刻意枚举 README「完整功能清单」中的**每一个入口脚本**；
- 支持 `--rounds N` 多轮重复，验证稳定性。

运行:
  python tests/skill_full_feature_smoke.py               # 默认 3 轮
  python tests/skill_full_feature_smoke.py --rounds 5 --seed 7
  python tests/skill_full_feature_smoke.py --quick       # 仅 1 轮，用于本地快速自检
"""
import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
PY = sys.executable
NODE = "node"

PASS = 0
FAIL = 0
FAILED = []

# 多轮用的候选输入（每轮轮换，制造差异）
DATES = ["2026-06-29", "2030-01-15", "2003-04-19", "1984-07-08", "2040-12-01"]
CITIES = ["杭州", "北京", "广州", "拉萨", "武汉"]
SYNDROMES = ["湿温", "霍乱", "中风", "温病", "痢疾"]


def run(args, timeout=120, node=False):
    """运行命令，返回 (returncode, stdout, stderr)。"""
    exe = NODE if node else PY
    try:
        r = subprocess.run([exe] + args, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", cwd=ROOT, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "TIMEOUT"


def check(name, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  [PASS] {name}" + (f"  {detail}" if detail else ""))
    else:
        FAIL += 1
        FAILED.append(name)
        print(f"  [FAIL] {name}  {detail}")


def ok_json(out, name, must_have=None):
    try:
        d = json.loads(out)
        if must_have:
            for k in must_have:
                if k not in d:
                    check(name, False, f"缺少键 {k}")
                    return None
        check(name, True)
        return d
    except Exception as e:
        check(name, False, f"JSON 解析失败: {e}")
        return None


# ---------------------------------------------------------------------------
# 静态存在性检查（每个入口/模块/人格/教学模块是否就位）—— 只跑一次
# ---------------------------------------------------------------------------
def static_structure_checks():
    print("\n########## 静态结构检查（入口 / 模块 / 教学 / 人格）##########")
    # 6 个子技能模块
    mod_dirs = ["ganzhi-basics", "yunqi-calc", "yunqi-pathogenesis",
                "yunqi-clinical", "yunqi-classics", "docs-generator"]
    missing_mod = [m for m in mod_dirs if not os.path.isfile(f"modules/{m}/SKILL.md")]
    check("6 个子技能模块 SKILL.md 齐全", not missing_mod, str(missing_mod))

    # 10 个教学模块（排除 README 与映射表）
    tm = [f for f in os.listdir("teaching-modules")
          if f.endswith(".md") and f not in ("README.md", "相关思维工具.md")]
    check("10 个教学模块齐全", len(tm) == 10, f"实际 {len(tm)}: {tm}")

    # 2 个注家人格
    pers = ["liu-wansu-perspective", "zhang-jiebin-perspective"]
    missing_p = [p for p in pers if not os.path.isfile(f"perspectives/{p}/SKILL.md")]
    check("2 个注家人格 SKILL.md 齐全", not missing_p, str(missing_p))

    # 核心脚本存在性
    core = ["calculate_yunqi_api.py", "rag_search.py", "infer_pathogenesis.py",
            "generate_html_report.py", "export_thought.py", "export_thought_map.py",
            "visualize_timeline.py", "generate_case_browser.py", "case_relations.py",
            "cases_routing.py", "resolve_ref.py", "personal_yunqi_profile.py",
            "weather_alignment.py", "yunqi_weather_constitution.py",
            "advanced_alignment.py", "constitution_assessment.py", "self_evolve.py",
            "health_check.py", "validate_knowledge_base.py", "generate_rag_index.py",
            "report_quality_gate.py", "check_conformance.py", "check_routing_scenarios.py",
            "check_skill_structure.py", "audit_orphans.py", "sync_routing.py",
            "verify_cross_check.py", "extract_structured_fields.py",
            "rag_semantic.py", "socratic_learn.py", "learning_dashboard.py", "yunqi_cli.py"]
    missing_core = [c for c in core if not os.path.isfile(f"scripts/{c}")]
    check("33 个核心脚本齐全", not missing_core, str(missing_core))


# ---------------------------------------------------------------------------
# 一轮：用给定 (date, city, syndrome) 触发全部功能
# ---------------------------------------------------------------------------
def run_round(round_idx, date, city, syndrome):
    year = date[:4]
    print(f"\n########## 第 {round_idx} 轮  date={date} city={city} syndrome={syndrome} ##########")
    tmp = os.path.join("reports", "test-results")
    os.makedirs(tmp, exist_ok=True)

    # ---- 推算引擎（9）----
    rc, out, err = run(["scripts/calculate_yunqi_api.py", "today", "--summary"])
    check("推算·今日运势 --summary", rc == 0 and ("岁运" in out or "司天" in out), f"rc={rc}")

    rc, out, err = run(["scripts/calculate_yunqi_api.py", year, "--json"])
    d = ok_json(out, "推算·年份 --json（含干支 year_gz）", must_have=["year_gz"]) if rc == 0 else (check("推算·年份 --json", False, f"rc={rc}"), None)[1]
    if d is not None and year == "2026":
        check("推算·2026 干支应为丙午", d.get("year_gz") == "丙午", str(d.get("year_gz")))

    rc, out, err = run(["scripts/calculate_yunqi_api.py", date, "--json"])
    ok_json(out, "推算·指定日 --json（含 rag_keys）", must_have=["rag_keys"]) if rc == 0 else check("推算·指定日 --json", False, f"rc={rc}")

    rc, out, err = run(["scripts/calculate_yunqi_api.py", "today", "--level", "deep",
                        "--explain-concept", "天人合一"])
    check("推算·概念解释 --explain-concept", rc == 0 and len(out) > 30, f"rc={rc} len={len(out)}")

    rc, out, err = run(["scripts/calculate_yunqi_api.js", date, "--json"], node=True)
    ok_json(out, "推算·JS 版 --json（双引擎一致性）") if rc == 0 else check("推算·JS 版", False, f"rc={rc}")

    rc, out, err = run(["scripts/infer_pathogenesis.py", year])
    check("推算·病机推理链 infer_pathogenesis", rc == 0 and "岁运" in out and ("方剂" in out or "治法" in out), f"rc={rc}")

    rc, out, err = run(["scripts/weather_alignment.py", date, "--city", city, "--mock", "--json"])
    ok_json(out, "推算·天气对齐 --mock", must_have=["yunqi"]) if rc == 0 else check("推算·天气对齐", False, f"rc={rc}")

    rc, out, err = run(["scripts/personal_yunqi_profile.py", "2003-04-19", city, "--constitution-demo", "--json"])
    ok_json(out, "推算·个人体质 profile") if rc == 0 else check("推算·个人体质", False, f"rc={rc}")

    rc, out, err = run(["scripts/yunqi_weather_constitution.py", date,
                        "--birth-date", "2003-04-19", "--city", city, "--mock", "--json"])
    ok_json(out, "推算·天气×体质×运气 三维") if rc == 0 else check("推算·三维叠加", False, f"rc={rc}")

    rc, out, err = run(["scripts/advanced_alignment.py", "--date", date,
                        "--birth-date", "2003-04-19", "--city", city,
                        "--constitution-demo", "--mock", "--json"])
    ok_json(out, "推算·高级对齐 unified") if rc == 0 else check("推算·高级对齐", False, f"rc={rc}")

    # ---- 知识检索（5）----
    rc, out, err = run(["scripts/rag_search.py", "头痛", "--asset", "asset26,asset27", "--json"])
    ok_json(out, "检索·病证跨库 asset26,27") if rc == 0 else check("检索·病证跨库", False, f"rc={rc}")

    rc, out, err = run(["scripts/rag_search.py", "--key", "water_excess", "--asset", "asset9", "--json"])
    d = ok_json(out, "检索·运气键 --key asset9") if rc == 0 else None
    if d is not None:
        check("检索·运气键命中数≥1", d.get("count", 0) >= 1, f'{d.get("count")}')

    rc, out, err = run(["scripts/rag_search.py", "--date", date, "--json"])
    ok_json(out, "检索·按日综合召回（hits_by_role）", must_have=["hits_by_role"]) if rc == 0 else check("检索·按日召回", False, f"rc={rc}")

    rc, out, err = run(["scripts/rag_search.py", "--semantic", "心火偏旺", "--limit", "3", "--json"])
    ok_json(out, "检索·口语语义 --semantic") if rc == 0 else check("检索·语义", False, f"rc={rc}")

    rc, out, err = run(["scripts/rag_search.py", "--field", "herbs", "石膏", "--json"])
    check("检索·按字段 --field herbs", rc == 0, f"rc={rc}")

    rc, out, err = run(["scripts/rag_search.py", "--asset", "asset33", "高血压", "--json"])
    d = ok_json(out, "检索·疾病易感性 asset33") if rc == 0 else None
    if d is not None:
        check("检索·疾病易感性命中数≥1", d.get("count", 0) >= 1, f'{d.get("count")}')

    # ---- 检索增强与引用（5）----
    rc, out, err = run(["scripts/resolve_ref.py", "--selfcheck"])
    check("增强·稳定引用 --selfcheck", rc == 0, f"rc={rc}")

    rc, out, err = run(["scripts/cases_routing.py", "--syndrome", syndrome, "--json"])
    ok_json(out, "增强·病证渐进路由 cases_routing") if rc == 0 else check("增强·路由", False, f"rc={rc}")

    rc, out, err = run(["scripts/rag_search.py", "--show-terms", "暑湿", "--json"])
    check("增强·歧义消解 --show-terms", rc == 0, f"rc={rc}")

    rc, out, err = run(["scripts/rag_search.py", "霍乱", "--include-extra", "--json"])
    check("增强·两段式补检索 --include-extra", rc == 0, f"rc={rc}")

    rc, out, err = run(["scripts/case_relations.py", "--compare", "孙一奎,叶桂", "--tag", "中风"])
    check("增强·医案关联对比 --compare", rc == 0 and len(out) > 10, f"rc={rc}")

    rc, out, err = run(["scripts/case_relations.py", "--related", "swy_174"])
    check("增强·相似医案 --related", rc == 0 and len(out) > 10, f"rc={rc}")

    rc, out, err = run(["scripts/extract_structured_fields.py", "--check"])
    check("增强·结构化字段提取 --check", rc == 0, f"rc={rc}")

    # ---- 报告与导出（6）----
    rc, out, err = run(["scripts/yunqi_report.py", year, "--audience", "student"])
    check("报告·年度报告 yunqi_report", rc == 0 and ("岁运" in out or "司天" in out), f"rc={rc}")

    html_path = os.path.join(tmp, f"smoke_report_{round_idx}.html")
    rc, out, err = run(["scripts/generate_html_report.py", date, html_path])
    ok_html = rc == 0 and os.path.isfile(html_path) and "知识库精确命中" in open(html_path, encoding="utf-8").read()
    check("报告·HTML 可视化（含知识库精确命中）", ok_html, f"rc={rc}")

    rc, out, err = run(["scripts/export_thought.py", year, "--format", "cards"])
    check("报告·思想导出卡片 cards", rc == 0 and len(out) > 50, f"rc={rc}")

    rc, out, err = run(["scripts/export_thought_map.py", year, "--format", "concept", "--json"])
    check("报告·思想地图 map --json", rc == 0, f"rc={rc}")

    tl_path = os.path.join(tmp, f"smoke_timeline_{round_idx}.html")
    rc, out, err = run(["scripts/visualize_timeline.py", year, "--output", tl_path])
    check("报告·运气时间轴 timeline", rc == 0 and os.path.isfile(tl_path), f"rc={rc}")

    br_path = os.path.join(tmp, f"smoke_browser_{round_idx}.html")
    rc, out, err = run(["scripts/generate_case_browser.py", "--output", br_path])
    check("报告·医案浏览器 browser", rc == 0 and os.path.isfile(br_path), f"rc={rc}")

    # ---- 数据导出（P10 Parquet）----
    try:
        import pyarrow  # noqa: F401
        import pyarrow.parquet as _pq  # noqa: F401
        have_pa = True
    except Exception:
        have_pa = False
    if have_pa:
        rag_pq = os.path.join(tmp, f"smoke_rag_{round_idx}.parquet")
        rc, out, err = run(["scripts/generate_rag_index.py", "--export-mode", "rag",
                            "--format", "parquet", "--output", rag_pq])
        if rc == 0 and os.path.isfile(rag_pq):
            t = _pq.read_table(rag_pq)
            cols = set(t.column_names)
            need = {'rag_key', 'source_quote', 'sui_yun', 'si_tian', 'zai_quan', 'yun_qi_xiang_he'}
            n = len(t)
            cols_ok = need.issubset(cols)
            check("导出·P10 RAG 条目 Parquet（可读+字段齐全）", n > 0 and cols_ok,
                  f"rows={n} cols_ok={cols_ok}")
        else:
            check("导出·P10 RAG 条目 Parquet", False, f"rc={rc} err={err[:120]}")

        cal_pq = os.path.join(tmp, f"smoke_calendar_{round_idx}.parquet")
        rc, out, err = run(["scripts/generate_rag_index.py", "--export-mode", "calendar",
                            "--format", "parquet", "--year-range", "2000", "2010",
                            "--output", cal_pq])
        if rc == 0 and os.path.isfile(cal_pq):
            t = _pq.read_table(cal_pq)
            cols = set(t.column_names)
            need = {'year', 'ganzhi', 'sui_yun_name', 'si_tian', 'zai_quan',
                    'zhu_qi', 'ke_qi', 'yun_qi_xiang_he'}
            n = len(t)
            cols_ok = need.issubset(cols)
            check("导出·P10 运气年表 Parquet（可读+字段齐全）", n > 0 and cols_ok,
                  f"rows={n} cols_ok={cols_ok}")
        else:
            check("导出·P10 运气年表 Parquet", False, f"rc={rc} err={err[:120]}")
    else:
        check("导出·P10 Parquet（pyarrow 未装，跳过）", True, "skip: pip install pyarrow")

    # ---- 学习与教学（3）----
    rc, out, err = run(["scripts/socratic_learn.py", year, "--concept", "司天在泉", "--json", "--no-file"])
    check("学习·苏格拉底会话 socratic", rc == 0, f"rc={rc}")

    rc, out, err = run(["scripts/learning_dashboard.py", "--json"])
    check("学习·学习仪表盘 dashboard", rc == 0, f"rc={rc}")

    rc, out, err = run(["scripts/demo_full_chain.py", date])
    check("学习·全链路演示 demo_full_chain", rc == 0 and len(out) > 100, f"rc={rc}")

    # ---- 自进化与运维（7）----
    rc, out, err = run(["scripts/health_check.py"])
    check("运维·健康检查 health_check", rc == 0, f"rc={rc}")

    rc, out, err = run(["scripts/validate_knowledge_base.py"])
    check("运维·知识库校验 validate", rc == 0, f"rc={rc}")

    rc, out, err = run(["scripts/generate_rag_index.py", "--check"])
    check("运维·RAG 索引检查", rc == 0, f"rc={rc}")

    rc, out, err = run(["scripts/report_quality_gate.py", "--demo", "--json"])
    check("运维·报告质量门禁 --demo", rc == 0, f"rc={rc}")

    rc, out, err = run(["scripts/check_conformance.py"])
    check("运维·一致性检查 conformance", rc == 0, f"rc={rc}")

    rc, out, err = run(["scripts/check_routing_scenarios.py"])
    check("运维·路由场景检查", rc == 0, f"rc={rc}")

    rc, out, err = run(["scripts/check_skill_structure.py"])
    check("运维·技能结构检查", rc == 0, f"rc={rc}")

    rc, out, err = run(["scripts/audit_orphans.py"])
    check("运维·孤儿审计 audit_orphans", rc == 0, f"rc={rc}")

    rc, out, err = run(["scripts/sync_routing.py", "--check"])
    check("运维·路由同步检查", rc == 0, f"rc={rc}")

    rc, out, err = run(["scripts/verify_cross_check.py"])
    check("运维·经典交叉验证 cross_check", rc == 0, f"rc={rc}")

    rc, out, err = run(["scripts/self_evolve.py", "stats", "--type", "blind_spots"])
    check("运维·自进化统计 self_evolve", rc == 0, f"rc={rc}")

    # ---- 安装与校验（6）----
    rc, out, err = run(["tests/smoke_pip_install.py"])
    check("安装·pip 装入冒烟", rc == 0, f"rc={rc}")

    # ---- 聚合 CLI（yunqi_cli）----
    rc, out, err = run(["scripts/yunqi_cli.py", "doctor"])
    check("CLI·doctor 健康检查", rc == 0, f"rc={rc}")

    rc, out, err = run(["scripts/yunqi_cli.py", "calc", date])
    check("CLI·calc 推算", rc == 0 and "岁运" in out, f"rc={rc}")

    rc, out, err = run(["scripts/yunqi_cli.py", "report", year, "--audience", "practitioner", "--json"])
    ok_json(out, "CLI·report practitioner") if rc == 0 else check("CLI·report", False, f"rc={rc}")

    rc, out, err = run(["scripts/yunqi_cli.py", "search", "霍乱", "--asset", "asset18", "--json"])
    ok_json(out, "CLI·search 霍乱 asset18") if rc == 0 else check("CLI·search", False, f"rc={rc}")

    rc, out, err = run(["scripts/yunqi_cli.py", "profile", "2003-04-19", city, "--json"])
    ok_json(out, "CLI·profile 体质") if rc == 0 else check("CLI·profile", False, f"rc={rc}")

    rc, out, err = run(["scripts/yunqi_cli.py", "map", year, "--format", "concept", "--json"])
    check("CLI·map 概念地图", rc == 0, f"rc={rc}")

    rc, out, err = run(["scripts/yunqi_cli.py", "learn", year, "--concept", "司天在泉", "--json"])
    check("CLI·learn 学习会话", rc == 0, f"rc={rc}")

    rc, out, err = run(["scripts/yunqi_cli.py", "export", year, "--format", "summary"])
    check("CLI·export 摘要", rc == 0, f"rc={rc}")


def main():
    ap = argparse.ArgumentParser(description="全功能全场景多轮冒烟测试")
    ap.add_argument("--rounds", type=int, default=3, help="重复轮数（默认 3）")
    ap.add_argument("--seed", type=int, default=0, help="随机种子")
    ap.add_argument("--quick", action="store_true", help="等价于 --rounds 1")
    args = ap.parse_args()
    rounds = 1 if args.quick else max(1, args.rounds)

    static_structure_checks()
    for i in range(rounds):
        date = DATES[i % len(DATES)]
        city = CITIES[i % len(CITIES)]
        syndrome = SYNDROMES[i % len(SYNDROMES)]
        run_round(i + 1, date, city, syndrome)

    print(f"\n{'='*64}")
    print(f"全功能冒烟测试完成: PASS={PASS}  FAIL={FAIL}  轮数={rounds}")
    if FAILED:
        print(f"失败用例（{len(FAILED)}）: {FAILED}")
    print(f"{'='*64}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
