#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容层孤儿/未激活审计（P3）

扫描 rules/、workflows/、references/ 中未被路由或文档引用的文件。

用法: python scripts/audit_orphans.py [--strict]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from _common import setup_utf8_stdout, PROJECT_ROOT
setup_utf8_stdout()

ROOT = PROJECT_ROOT

SCAN_DIRS = ["rules", "workflows", "references"]
REF_SOURCES = [
    "SKILL.md",
    "routing.yaml",
    "routing.md",
    "RULES.md",
    "AGENTS.md",
    "CLAUDE.md",
    "conformance.yaml",
    "tests/routing_scenarios.json",
    "workflows/routing-contract.md",
    "workflows/task-closure.md",
    "workflows/bootstrap.md",
    "workflows/one-line-install.md",
    "workflows/claude-plugin-install.md",
    "references/gotchas.md",
    "references/script-index.md",
    "references/module-index.md",
]

# 允许存在但不一定被内联引用的文件
ALLOW_ORPHAN = {
    "workflows/bootstrap.md",  # first_use 引用在 routing.yaml
    "workflows/one-line-install.md",
    "workflows/claude-plugin-install.md",
}

PATH_RE = re.compile(
    r"(?:`|\[|\(|>|^|\s)((?:rules|workflows|references)/[\w./-]+\.md)"
)


def collect_tier_files() -> set[str]:
    found: set[str] = set()
    for d in SCAN_DIRS:
        base = ROOT / d
        if not base.is_dir():
            continue
        for p in base.rglob("*.md"):
            found.add(p.relative_to(ROOT).as_posix())
    return found


def collect_refs() -> set[str]:
    refs: set[str] = set()
    for rel in REF_SOURCES:
        path = ROOT / rel
        if not path.is_file():
            continue
        if rel.endswith(".json"):
            text = path.read_text(encoding="utf-8")
            for m in re.finditer(r"[\w.-]+/(?:[\w./-]+\.md)", text):
                refs.add(m.group(0).replace("\\", "/"))
            continue
        text = path.read_text(encoding="utf-8")
        for m in PATH_RE.finditer(text):
            refs.add(m.group(1))
        for m in re.finditer(r"[\w.-]+/(?:[\w./-]+\.md)", text):
            refs.add(m.group(0).replace("\\", "/"))

    routing = ROOT / "routing.yaml"
    if routing.is_file():
        text = routing.read_text(encoding="utf-8")
        for m in re.finditer(r"[\w.-]+/(?:[\w./-]+\.md)", text):
            refs.add(m.group(0).replace("\\", "/"))
        # first_use / always_read 裸路径
        for m in re.finditer(r"^\s+-\s+([\w.-]+/[\w./-]+\.md)\s*$", text, re.M):
            refs.add(m.group(1))

    # 子目录互引
    for d in SCAN_DIRS:
        base = ROOT / d
        if not base.is_dir():
            continue
        for p in base.rglob("*.md"):
            text = p.read_text(encoding="utf-8")
            for m in PATH_RE.finditer(text):
                refs.add(m.group(1))

    return refs


def routing_activated_rules(manifest_text: str) -> set[str]:
    """rules/ 中被 always_read / required_reads / route 直接激活的路径。"""
    activated: set[str] = set()
    for m in re.finditer(r"[\w.-]+/(?:[\w./-]+\.md)", manifest_text):
        p = m.group(0)
        if p.startswith("rules/"):
            activated.add(p)
    return activated


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="孤儿视为失败")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    tier_files = collect_tier_files()
    refs = collect_refs()
    routing_text = (ROOT / "routing.yaml").read_text(encoding="utf-8") if (ROOT / "routing.yaml").is_file() else ""
    activated_rules = routing_activated_rules(routing_text)

    print("=" * 50)
    print("  内容层孤儿审计")
    print("=" * 50)
    print(f"  扫描: {len(tier_files)} 个 tier 文件, {len(refs)} 条入链引用\n")

    orphans: list[str] = []
    for rel in sorted(tier_files):
        if rel in refs or rel in ALLOW_ORPHAN:
            print(f"  ✓ 已引用 {rel}")
            continue
        # bootstrap 等在 routing.yaml first_use
        if rel.replace("\\", "/") in routing_text:
            print(f"  ✓ routing.yaml 提及 {rel}")
            continue
        orphans.append(rel)
        msg = f"零入链引用: {rel}"
        if args.strict:
            errors.append(msg)
        else:
            warnings.append(msg)
        print(f"  ! {msg}")

    print("\n--- rules/ 路由激活 ---")
    for rel in sorted(p for p in tier_files if p.startswith("rules/")):
        if rel in activated_rules or rel in refs:
            print(f"  ✓ 已激活 {rel}")
        else:
            w = f"rules 未在路由直接激活: {rel}"
            warnings.append(w)
            print(f"  ! {w}")

    print("\n" + "=" * 50)
    if errors:
        for e in errors:
            print(f"  ✗ {e}")
    if warnings:
        for w in warnings:
            print(f"  ! {w}")
    print(f"汇总: {len(orphans)} 孤儿, {len(errors)} 错误, {len(warnings)} 警告")

    if errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())