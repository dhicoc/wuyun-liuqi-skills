#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个性化学习路径仪表盘（optimization-sprint Phase 5）

汇总：
  - 自进化使用日志（概念 / rag_keys / 会话链）
  - 本地已生成的学习产物（socratic / thought_map / thought 摘要）
  - 推荐下一步（苏格拉底、地图、文献检索）

用法:
  python scripts/learning_dashboard.py
  python scripts/learning_dashboard.py --html
  python scripts/learning_dashboard.py --json
  python scripts/learning_dashboard.py --output reports/generated/learning_dashboard.md
"""
from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from _common import setup_environment, add_scripts_dir_to_path, PROJECT_ROOT

setup_environment(add_lib=False, add_scripts=True)
add_scripts_dir_to_path()

ROOT = PROJECT_ROOT
REPORTS_GEN = ROOT / "reports" / "generated"
CORE_CONCEPTS = ["天人合一", "气化", "中和", "天符"]


def _safe_import_self_evolve():
    try:
        import self_evolve as se
        return se
    except Exception:
        return None


def collect_self_evolve_stats() -> Dict[str, Any]:
    se = _safe_import_self_evolve()
    if se is None:
        return {
            "available": False,
            "top_concepts": [],
            "top_keys": [],
            "sessions": {},
            "progression": [],
            "daily": [],
            "feedback": {},
            "total_logs": 0,
        }
    logs = se.load_jsonl_lines(se.LOG_DIR)
    return {
        "available": True,
        "top_concepts": se.stats_top_concepts(10),
        "top_keys": se.stats_top_keys(10),
        "sessions": se.stats_sessions(),
        "progression": se.stats_concept_progression(),
        "daily": se.stats_daily_usage()[-14:],  # 近 14 天
        "feedback": se.stats_feedback_summary(),
        "total_logs": len(logs),
    }


def scan_learning_artifacts() -> Dict[str, List[Dict[str, str]]]:
    """扫描 reports/generated 下的学习相关文件。"""
    buckets = {
        "socratic": [],
        "thought_map": [],
        "thought_summary": [],
        "cards": [],
        "other": [],
    }
    if not REPORTS_GEN.is_dir():
        return buckets

    patterns = [
        ("socratic", re.compile(r"^socratic_.*\.md$", re.I)),
        ("thought_map", re.compile(r"^thought_map_.*\.md$", re.I)),
        ("thought_summary", re.compile(r".*thought.*summary.*\.md$|.*_summary\.md$", re.I)),
        ("cards", re.compile(r".*cards.*\.(md|tsv)$", re.I)),
    ]
    for p in sorted(REPORTS_GEN.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if not p.is_file():
            continue
        name = p.name
        matched = False
        for key, rx in patterns:
            if rx.search(name):
                buckets[key].append({
                    "name": name,
                    "path": str(p.relative_to(ROOT)).replace("\\", "/"),
                    "mtime": datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="seconds"),
                })
                matched = True
                break
        if not matched and name.endswith((".md", ".html")) and "thought" in name.lower():
            buckets["other"].append({
                "name": name,
                "path": str(p.relative_to(ROOT)).replace("\\", "/"),
                "mtime": datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="seconds"),
            })
    # 每类最多保留 8 条
    for k in buckets:
        buckets[k] = buckets[k][:8]
    return buckets


def concept_coverage(top_concepts: List[Tuple[str, int]]) -> List[Dict[str, Any]]:
    seen = {c: n for c, n in top_concepts}
    rows = []
    for c in CORE_CONCEPTS:
        n = seen.get(c, 0)
        rows.append({
            "concept": c,
            "hits": n,
            "status": "已接触" if n > 0 else "未接触",
            "recommend": None if n > 0 else f'python scripts/yunqi_cli.py learn today --concept {c}',
        })
    # 额外出现的概念
    for c, n in top_concepts:
        if c not in CORE_CONCEPTS and not str(c).startswith("level_"):
            rows.append({
                "concept": c,
                "hits": n,
                "status": "已接触",
                "recommend": None,
            })
    return rows


def build_recommendations(stats: Dict[str, Any], coverage: List[Dict[str, Any]]) -> List[str]:
    recs: List[str] = []
    untouched = [r["concept"] for r in coverage if r["status"] == "未接触" and r["concept"] in CORE_CONCEPTS]
    if untouched:
        recs.append(
            f"核心概念尚未接触：{', '.join(untouched)}。建议："
            f"`python scripts/yunqi_cli.py learn today --concept {untouched[0]}`"
        )
    else:
        recs.append("核心概念均有接触。可深化：`python scripts/yunqi_cli.py learn today --interactive`")

    if stats.get("total_logs", 0) == 0:
        recs.append("尚无使用日志。先运行：`python scripts/yunqi_cli.py calc today --summary`")
    else:
        recs.append("查看思想结构：`python scripts/yunqi_cli.py map today`")

    recs.append("文献检索：`python scripts/yunqi_cli.py search 司天` 或 `python scripts/rag_search.py 客主加临`")
    recs.append("导出复习：`python scripts/yunqi_cli.py export today --format cards`")
    return recs


def build_dashboard() -> Dict[str, Any]:
    stats = collect_self_evolve_stats()
    artifacts = scan_learning_artifacts()
    coverage = concept_coverage(stats.get("top_concepts") or [])
    recs = build_recommendations(stats, coverage)
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "self_evolve": stats,
        "concept_coverage": coverage,
        "artifacts": artifacts,
        "recommendations": recs,
    }


def to_markdown(data: Dict[str, Any]) -> str:
    se = data["self_evolve"]
    lines = [
        "# 五运六气 · 学习路径仪表盘",
        "",
        f"> 生成时间: {data['generated_at']}",
        "",
        "本页汇总你的**概念接触、使用轨迹、本地学习产物**，并给出下一步建议。",
        "",
        "## 1. 概览",
        "",
        f"- 自进化日志可用: **{'是' if se.get('available') else '否'}**",
        f"- 累计有效推算记录: **{se.get('total_logs', 0)}**",
        f"- 会话数: **{(se.get('sessions') or {}).get('total_sessions', 0)}**"
        f"（多步会话 {(se.get('sessions') or {}).get('multi_log_sessions', 0)}）",
        f"- 反馈均分: **{(se.get('feedback') or {}).get('avg_rating', 0)}** "
        f"/ 条数 {(se.get('feedback') or {}).get('total', 0)}",
        "",
        "## 2. 核心概念覆盖",
        "",
        "| 概念 | 接触次数 | 状态 |",
        "|------|----------|------|",
    ]
    for row in data["concept_coverage"]:
        if row["concept"] in CORE_CONCEPTS or row["hits"]:
            lines.append(f"| {row['concept']} | {row['hits']} | {row['status']} |")

    lines += ["", "## 3. 高频查询 TOP", ""]
    lines.append("### 思想概念")
    if se.get("top_concepts"):
        for c, n in se["top_concepts"][:8]:
            lines.append(f"- `{c}` × {n}")
    else:
        lines.append("- （暂无）")
    lines.append("")
    lines.append("### RAG keys")
    if se.get("top_keys"):
        for k, n in se["top_keys"][:8]:
            lines.append(f"- `{k}` × {n}")
    else:
        lines.append("- （暂无）")

    lines += ["", "## 4. 概念链（学习深度）", ""]
    prog = se.get("progression") or []
    if prog:
        for p in prog[:5]:
            chain = " → ".join(p.get("concept_chain") or [])
            lines.append(f"- depth={p.get('depth')}: {chain}")
    else:
        lines.append("- 暂无多概念会话链。学习时加 `--concept` 或开启概念解释可积累路径。")

    lines += ["", "## 5. 本地学习产物", ""]
    arts = data["artifacts"]
    labels = {
        "socratic": "苏格拉底会话",
        "thought_map": "思想地图",
        "thought_summary": "思想摘要",
        "cards": "复习卡片",
        "other": "其他",
    }
    for key, label in labels.items():
        items = arts.get(key) or []
        lines.append(f"### {label}（{len(items)}）")
        if not items:
            lines.append("- （无）")
        else:
            for it in items[:5]:
                lines.append(f"- `{it['path']}` · {it['mtime']}")
        lines.append("")

    lines += ["## 6. 推荐下一步", ""]
    for i, r in enumerate(data["recommendations"], 1):
        lines.append(f"{i}. {r}")
    lines += [
        "",
        "---",
        "",
        "_由 learning_dashboard.py 生成 · 见 docs/optimization-sprint.md_",
    ]
    return "\n".join(lines)


def to_html(data: Dict[str, Any]) -> str:
    """轻量 HTML，便于浏览器打开。"""
    md_like = to_markdown(data)
    # 极简：转义后 pre 展示 + 基础样式（避免依赖 markdown 库）
    escaped = (
        md_like.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"/>
<title>五运六气学习路径仪表盘</title>
<style>
  body {{ font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
         max-width: 820px; margin: 2rem auto; padding: 0 1.2rem; line-height: 1.65; color: #1f2937; }}
  pre {{ white-space: pre-wrap; background: #f8fafc; border: 1px solid #e5e7eb;
        border-radius: 8px; padding: 1.25rem; font-size: 14px; }}
  h1 {{ font-size: 1.4rem; }}
</style>
</head>
<body>
<h1>五运六气 · 学习路径仪表盘</h1>
<p style="color:#6b7280">生成：{data.get('generated_at','')}</p>
<pre>{escaped}</pre>
</body>
</html>
"""


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="生成个性化学习路径仪表盘")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    parser.add_argument("--html", action="store_true", help="同时/优先写 HTML")
    parser.add_argument("--output", "-o", default=None, help="输出路径（.md / .html / .json）")
    parser.add_argument("--stdout", action="store_true", help="打印 Markdown 到终端")
    args = parser.parse_args(list(argv) if argv is not None else None)

    data = build_dashboard()
    stamp = datetime.now().strftime("%Y%m%d")
    REPORTS_GEN.mkdir(parents=True, exist_ok=True)

    if args.json and not args.output:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    if args.output:
        out = Path(args.output)
    elif args.html:
        out = REPORTS_GEN / f"learning_dashboard_{stamp}.html"
    elif args.json:
        out = REPORTS_GEN / f"learning_dashboard_{stamp}.json"
    else:
        out = REPORTS_GEN / f"learning_dashboard_{stamp}.md"

    out.parent.mkdir(parents=True, exist_ok=True)
    suffix = out.suffix.lower()
    if suffix == ".json" or args.json and suffix == ".json":
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    elif suffix == ".html" or args.html:
        # 若用户指定 .md 但 --html，仍写 html 旁路
        if suffix != ".html":
            out = out.with_suffix(".html")
        out.write_text(to_html(data), encoding="utf-8")
    else:
        text = to_markdown(data)
        out.write_text(text, encoding="utf-8")
        if args.stdout:
            print(text)

    print(f"✅ 学习路径仪表盘已生成: {out}")
    print(f"   记录数={data['self_evolve'].get('total_logs', 0)} · 推荐 {len(data['recommendations'])} 条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
