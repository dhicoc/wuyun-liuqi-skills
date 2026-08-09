#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SKILL.md 端到端多场景全量测试（Agent 视角）

模拟 Agent 阅读 SKILL.md → 按 Common Tasks 路由匹配每个用户话术
→ 执行 routing.yaml 对应脚本 → 校验脚本成功且输出符合预期。

覆盖 SKILL.md 全部 13 个 Common Task 路由 + RAG 医案检索（含 asset11-16）。
用法: python tests/skill_e2e_test.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable

passed = 0
failed = 0


def run(name, args, check_fn=None, timeout=60):
    """执行命令并校验。返回 (ok, output)。"""
    global passed, failed
    try:
        r = subprocess.run(args, capture_output=True, text=True,
                           cwd=str(ROOT), timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"[FAIL] {name}: 超时")
        failed += 1
        return False, ""
    out = (r.stdout or "") + (r.stderr or "")
    ok = r.returncode == 0
    if check_fn:
        ok = ok and check_fn(r, out)
    mark = "PASS" if ok else "FAIL"
    if ok:
        passed += 1
    else:
        failed += 1
    detail = ""
    if not ok:
        tail = out.strip().splitlines()[-5:] if out.strip() else []
        detail = "\n       " + "\n       ".join(tail)
    print(f"  [{mark}] {name}{detail}")
    return ok, out


def has(needle):
    def _c(r, out):
        return needle in out
    return _c


def json_has(keys):
    def _c(r, out):
        try:
            d = json.loads(out)
        except Exception:
            return False
        return all(k in d for k in keys)
    return _c


def _chk(cond, name):
    """直接断言文件存在等布尔条件（不执行命令）。"""
    global passed, failed
    mark = "PASS" if cond else "FAIL"
    if cond:
        passed += 1
    else:
        failed += 1
    print(f"  [{mark}] {name}")


def main():
    global passed, failed
    print("=" * 62)
    print("  SKILL.md 端到端多场景全量测试")
    print("=" * 62)

    # ---- 前置：SKILL.md 路由完整性（Common Tasks 表中的路由目标存在）----
    print("\n== 0. SKILL.md 路由目标存在性 ==")
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    route_targets = {
        "quick-lookup": "calculate_yunqi_api.py",
        "year-calc": "modules/yunqi-calc/SKILL.md",
        "pathogenesis": "modules/yunqi-pathogenesis/SKILL.md",
        "clinical": "modules/yunqi-clinical/SKILL.md",
        "classics": "modules/yunqi-classics/SKILL.md",
        "learn-concept": "prompts/expression_style.md",
        "personal-profile": "personal_yunqi_profile.py",
        "weather-alignment": "weather_alignment.py",
        "export-thought": "export_thought.py",
        "case-journal": "case-journal/_template.md",
    }
    for label, target in route_targets.items():
        p = ROOT / target
        if not p.exists():  # 脚本类目标在 scripts/ 下
            p = ROOT / "scripts" / target
        ok = p.exists()
        mark = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1
        print(f"  [{mark}] 路由目标存在: {label} -> {target}")

    # ---- 1. 快速查今天运气（quick-lookup）----
    print("\n== 1. 快速查今天运气 ==")
    run("calculate today --summary", [PY, "scripts/calculate_yunqi_api.py", "today", "--summary"], has("全年岁运"))
    run("calculate 2026-06-29 json", [PY, "scripts/calculate_yunqi_api.py", "2026-06-29", "--json"], json_has(["rag_keys", "current_step"]))

    # ---- 2. 当前步位（current-step）----
    print("\n== 2. 当前步位 ==")
    run("focus current-step", [PY, "scripts/calculate_yunqi_api.py", "today", "--focus", "current-step"], has("当前步位"))

    # ---- 3. 完整年度分析（full-year-analysis）----
    print("\n== 3. 完整年度分析 ==")
    run("yunqi_report 2026 practitioner", [PY, "scripts/yunqi_report.py", "2026", "--audience", "practitioner"], has("经典与注家依据"))

    # ---- 4. 推算某年运气（year-calc）----
    print("\n== 4. 推算某年运气 ==")
    run("calculate 2026 丙午/水运", [PY, "scripts/calculate_yunqi_api.py", "2026"],
        lambda r, o: ("丙午" in o) and ("水运" in o))

    # ---- 5. 运气病机（pathogenesis）----
    print("\n== 5. 运气病机 ==")
    run("calculate json 病机", [PY, "scripts/calculate_yunqi_api.py", "2026-06-29", "--json"], json_has(["sui_yun", "si_tian", "rag_keys"]))

    # ---- 6. 治法/方药/养生（clinical）----
    print("\n== 6. 临床 ==")
    _chk((ROOT / "modules" / "yunqi-clinical" / "SKILL.md").exists(), "clinical SKILL.md 存在")

    # ---- 7. 经典文献（classics）----
    print("\n== 7. 经典文献 ==")
    _chk((ROOT / "modules" / "yunqi-classics" / "SKILL.md").exists(), "classics SKILL.md 存在")

    # ---- 8. 学概念/思想（learn-concept）----
    print("\n== 8. 学习概念 ==")
    run("calculate --explain-concept", [PY, "scripts/calculate_yunqi_api.py", "today", "--level", "deep", "--explain-concept", "客主加临"], has("客主加临"))
    run("socratic_learn json", [PY, "scripts/socratic_learn.py", "today", "--concept", "天人合一", "--no-file", "--json"], json_has(["date"]))

    # ---- 9. 个人运气/体质（personal-profile）----
    print("\n== 9. 个人运气/体质 ==")
    run("personal profile 1990", [PY, "scripts/personal_yunqi_profile.py", "1990-05-20", "北京"], has("个人运气体质分析报告"))

    # ---- 10. 结合天气（weather-alignment）----
    print("\n== 10. 天气对齐 ==")
    run("weather alignment mock", [PY, "scripts/weather_alignment.py", "2026-06-29", "--city", "杭州", "--mock"], has("天气对齐报告"))

    # ---- 11. 导出摘要/卡片（export-thought）----
    print("\n== 11. 导出思想材料 ==")
    run("export summary", [PY, "scripts/export_thought.py", "today", "--format", "summary", "--output", "reports/test-results/e2e-thought.md"], has("导出"))

    # ---- 12. 写医案/查岁图医案（case-journal）----
    print("\n== 12. 医案 ==")
    _chk((ROOT / "case-journal" / "_template.md").exists(), "case-journal 模板存在")
    run("rag_search 岁图医案", [PY, "scripts/rag_search.py", "--key", "shaoyin_junhuo_sitian", "--asset", "asset9"], has("asset9"))

    # ---- 13. RAG 医案检索（含 asset11-16 默认命中）----
    print("\n== 13. RAG 医案检索（asset11-16）==")
    run("默认检索命中医案库 asset16 肝风", [PY, "scripts/rag_search.py", "肝风", "--limit", "3"], has("asset16"))
    run("默认检索命中 asset14 诸痛", [PY, "scripts/rag_search.py", "诸痛", "--limit", "3"], has("asset14"))
    run("精确 category 咳嗽 asset16", [PY, "scripts/rag_search.py", "--key", "咳嗽", "--asset", "asset16"], has("ye_") or has("咳嗽"))
    run("语义检索 头痛呕吐", [PY, "scripts/rag_search.py", "--semantic", "头痛呕吐", "--limit", "3"], lambda r, o: r.returncode in (0, 1))
    run("按日打包 rag_keys", [PY, "scripts/rag_search.py", "--date", "2026-06-29"], has("rag_keys"))

    # ---- 14. 自进化 / 学习仪表盘 / 统一CLI ----
    print("\n== 14. 自进化 / 仪表盘 / CLI ==")
    run("self_evolve stats", [PY, "scripts/self_evolve.py", "stats", "--type", "top_keys"], lambda r, o: True)
    run("learning_dashboard", [PY, "scripts/learning_dashboard.py", "--stdout"], has("学习"))
    run("yunqi_cli doctor", [PY, "scripts/yunqi_cli.py", "doctor"], lambda r, o: True)

    # ---- 14b. 可视化报告 ----
    print("\n== 14b. 可视化报告 ==")
    run("visualize ASCII 六气步位推移", [PY, "scripts/visualize_yunqi.py", "2026-06-29"], has("六气步位推移"))
    run("visualize ASCII 司天", [PY, "scripts/visualize_yunqi.py", "2026-06-29"], has("司天"))
    _html_rag = lambda r, o: (ROOT / "reports/test-results/e2e-html.html").exists() and "知识库精确命中" in (ROOT / "reports/test-results/e2e-html.html").read_text(encoding="utf-8")
    run("generate_html 含 RAG 章节", [PY, "scripts/generate_html_report.py", "2026-06-29", "reports/test-results/e2e-html.html"], _html_rag)
    _html_adv = lambda r, o: (ROOT / "reports/test-results/e2e-html-adv.html").exists() and "高级对齐" in (ROOT / "reports/test-results/e2e-html-adv.html").read_text(encoding="utf-8")
    run("generate_html 含高级对齐", [PY, "scripts/generate_html_report.py", "2026-06-29", "reports/test-results/e2e-html-adv.html", "--with-advanced-alignment", "--birth-date", "2003-04-19", "--city", "杭州", "--constitution-demo", "--mock"], _html_adv)
    run("report_quality_gate demo", [PY, "scripts/report_quality_gate.py", "--demo", "--json"], json_has(["passed"]))

    # ---- 15. 免责声明（Always Read 安全边界）----
    print("\n== 15. 安全边界（免责声明）==")
    _chk((ROOT / "case-journal" / "precedent-disclaimer.md").exists(), "precedent-disclaimer 存在")
    run("report 含免责声明", [PY, "scripts/yunqi_report.py", "2026", "--audience", "practitioner"], has("免责声明"))

    print("\n" + "=" * 62)
    print(f"汇总: PASS={passed}  FAIL={failed}")
    print("=" * 62)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())