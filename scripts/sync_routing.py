#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 routing.yaml 同步 SKILL.md / routing.md 生成块（P3）

用法:
  python scripts/sync_routing.py --check   # 检测漂移（CI 默认）
  python scripts/sync_routing.py --write   # 写回生成块
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from _common import setup_environment, PROJECT_ROOT
setup_environment(add_lib=False)

ROOT = PROJECT_ROOT

from lib.routing_manifest import Manifest, Task, load_manifest, task_by_id  # noqa: E402

ALWAYS_START = "<!-- SYNC:ALWAYS_READ_START -->"
ALWAYS_END = "<!-- SYNC:ALWAYS_READ_END -->"
TASKS_START = "<!-- SYNC:COMMON_TASKS_START -->"
TASKS_END = "<!-- SYNC:COMMON_TASKS_END -->"
SUMMARY_START = "<!-- SYNC:TASKS_SUMMARY_START -->"
SUMMARY_END = "<!-- SYNC:TASKS_SUMMARY_END -->"


def display_always_read(manifest: Manifest) -> str:
    items = list(manifest.always_read)
    if "routing.yaml" not in items:
        # SKILL.md 固定插入 routing.yaml
        insert_at = min(2, len(items))
        items = items[:insert_at] + ["routing.yaml"] + items[insert_at:]
    return "\n".join(f"{i}. `{p}`" for i, p in enumerate(items, 1))


ROUTE_HINT_OVERRIDES: dict[str, str] = {
    "quick-lookup": "calculate_yunqi_api.py today --summary",
    "current-step": "--focus current-step",
    "full-year-analysis": "yunqi_report.py",
    "year-calc": "yunqi-calc/SKILL.md",
    "pathogenesis": "yunqi-pathogenesis/SKILL.md",
    "clinical": "yunqi-clinical/SKILL.md",
    "classics": "yunqi-classics/SKILL.md",
    "learn-concept": "--explain-concept",
    "personal-profile": "personal_yunqi_profile.py",
    "weather-alignment": "weather_alignment.py",
    "export-thought": "export_thought.py",
    "case-journal": "case-journal/_template.md",
    "claude-plugin-install": "workflows/claude-plugin-install.md",
}


def _route_hint(task: Task) -> str:
    if task.id in ROUTE_HINT_OVERRIDES:
        return ROUTE_HINT_OVERRIDES[task.id]
    if task.script:
        s = task.script.replace("python ", "").strip()
        s = re.sub(r"\s+<[^>]+>", "", s)
        return s
    if task.route:
        part = task.route.split("→")[0].strip()
        return part
    if task.workflow:
        return task.workflow
    return task.id


def _user_label(task: Task) -> str:
    zh = task.labels.get("zh", "")
    if "/" in zh:
        return zh.split("/")[-1].strip() if len(zh) > 12 else zh
    if task.trigger_examples:
        t = task.trigger_examples[0]
        if len(t) <= 16:
            return t
    return zh or task.id


# 与 SKILL.md 人工摘要一致的短标签（skill_sync 顺序优先）
SUMMARY_USER_OVERRIDES: dict[str, str] = {
    "quick-lookup": "今天/某日运气",
    "current-step": "最近/当前步位",
    "full-year-analysis": "完整年度分析",
    "year-calc": "推算某年运气",
    "pathogenesis": "运气病机",
    "clinical": "治法/方药/养生",
    "classics": "七篇大论/文献",
    "learn-concept": "学概念/思想",
    "personal-profile": "个人运气/体质",
    "weather-alignment": "结合天气",
    "export-thought": "导出摘要/卡片",
    "case-journal": "写医案",
    "claude-plugin-install": "Claude Code 插件",
}


def _user_label_short(task: Task) -> str:
    return SUMMARY_USER_OVERRIDES.get(task.id, _user_label(task))


def format_common_tasks_table(manifest: Manifest) -> str:
    ids = manifest.common_task_ids or [
        t.id for t in manifest.tasks if t.id not in {"other", "agent-rag", "self-evolve", "ganzhi-basics", "one-line-install"}
    ]
    lines = ["| 用户说 | 路由 |", "|--------|------|"]
    for tid in ids:
        task = task_by_id(manifest, tid)
        if not task:
            continue
        user = _user_label_short(task)
        hint = _route_hint(task)
        lines.append(f"| {user} | `tasks/{tid}` → `{hint}` |")
    return "\n".join(lines)


def format_routing_summary_table(manifest: Manifest) -> str:
    ids = manifest.common_task_ids or [t.id for t in manifest.tasks if t.trigger_examples and t.id != "other"]
    lines = ["| ID | 典型说法 | 入口 |", "|----|----------|------|"]
    for tid in ids[:16]:
        task = task_by_id(manifest, tid)
        if not task:
            continue
        zh = task.labels.get("zh", tid)
        hint = _route_hint(task)
        if len(hint) > 48:
            hint = hint[:45] + "..."
        lines.append(f"| {tid} | {zh} | `{hint}` |")
    lines.append("")
    lines.append("完整列表与触发词见 `routing.yaml` → `tasks`。Agent 路由场景证明见 `tests/routing_scenarios.json`。")
    return "\n".join(lines)


def replace_block(text: str, start: str, end: str, block: str) -> tuple[str, bool]:
    if start not in text or end not in text:
        return text, False
    expected = f"{start}\n{block}\n{end}"
    actual = start + text.split(start, 1)[1].split(end, 1)[0] + end
    if actual == expected:
        return text, False
    before = text.split(start, 1)[0]
    after = text.split(end, 1)[1]
    return before + expected + after, True


def check_or_write(path: Path, start: str, end: str, block: str, write: bool) -> tuple[bool, bool]:
    """返回 (ok, changed)"""
    if not path.is_file():
        print(f"FAIL: 缺少 {path.relative_to(ROOT)}")
        return False, False
    text = path.read_text(encoding="utf-8")
    if start not in text or end not in text:
        print(f"FAIL: {path.relative_to(ROOT)} 缺少同步标记 {start}")
        return False, False
    expected = f"{start}\n{block}\n{end}"
    actual = start + text.split(start, 1)[1].split(end, 1)[0] + end
    rel = path.relative_to(ROOT)
    if actual == expected:
        print(f"OK: {rel}")
        return True, False
    if write:
        new_text, _ = replace_block(text, start, end, block)
        path.write_text(new_text, encoding="utf-8")
        print(f"SYNC: {rel}")
        return True, True
    print(f"DRIFT: {rel}")
    return False, False


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true", help="仅检查漂移")
    group.add_argument("--write", action="store_true", help="写回生成块")
    args = parser.parse_args()
    write = args.write
    if not args.check and not args.write:
        write = False  # default check

    manifest = load_manifest(ROOT)
    if not manifest.common_task_ids:
        print("WARN: routing.yaml 未配置 skill_sync.common_tasks，使用默认列表")

    always_block = display_always_read(manifest)
    tasks_block = format_common_tasks_table(manifest)
    summary_block = format_routing_summary_table(manifest)

    print("=" * 50)
    print("  sync-routing")
    print("=" * 50)

    ok = True
    changed = False
    for path, start, end, block in [
        (ROOT / "SKILL.md", ALWAYS_START, ALWAYS_END, always_block),
        (ROOT / "SKILL.md", TASKS_START, TASKS_END, tasks_block),
        (ROOT / "routing.md", SUMMARY_START, SUMMARY_END, summary_block),
    ]:
        o, c = check_or_write(path, start, end, block, write)
        ok = ok and o
        changed = changed or c

    if not ok and not write:
        print("\n修复: python scripts/sync_routing.py --write")
        return 1
    if write and changed:
        print("\n已同步生成块。")
    elif write:
        print("\n生成块已是最新。")
    else:
        print("\n路由同步检查通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())