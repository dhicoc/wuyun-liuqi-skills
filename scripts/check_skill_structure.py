#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能包结构健康检查（P1）
用法: python scripts/check_skill_structure.py [--strict]

默认: 错误 → exit 1，警告 → 打印但 exit 0
--strict: 警告也视为失败
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from _common import setup_utf8_stdout
setup_utf8_stdout()

ROOT = Path(__file__).resolve().parent.parent

SKILL_MD_MAX_LINES = 90
RULES_MD_MAX_LINES = 200
REFERENCES_MD_MAX_LINES = 300

THIN_SHELLS = [
    "AGENTS.md",
    "CLAUDE.md",
    "CODEX.md",
    "GEMINI.md",
    ".cursor/rules/wuyun-liuqi.mdc",
    ".cursor/skills/wuyun-liuqi/SKILL.md",
    ".claude/skills/wuyun-liuqi/SKILL.md",
]

REQUIRED_RULES = [
    "rules/medical-safety.md",
    "rules/calculation.md",
    "rules/agent-behavior.md",
    "rules/output.md",
]

REQUIRED_WORKFLOWS = [
    "workflows/bootstrap.md",
    "workflows/routing-contract.md",
    "workflows/task-closure.md",
    "workflows/one-line-install.md",
    "workflows/claude-plugin-install.md",
]

PLUGIN_FILES = [
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
]

PATH_PATTERN = re.compile(
    r"(?:^|[\s`>（(])([\w.-]+/(?:[\w./-]+\.(?:md|yaml|py|mdc)|SKILL\.md))"
)


def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def check_exists(errors: list, warnings: list, rel: str) -> None:
    if not (ROOT / rel).is_file():
        errors.append(f"缺少文件: {rel}")


def extract_routing_paths(yaml_text: str) -> set[str]:
    paths = set()
    for m in PATH_PATTERN.finditer(yaml_text):
        p = m.group(1).strip("/")
        if p.endswith((".md", ".yaml", ".py")) or p.endswith("SKILL.md"):
            paths.add(p.replace("\\", "/"))
    # 显式抓取 route/workflow/script 行中的路径
    for m in re.finditer(r"[\w.-]+/(?:[\w./-]+\.(?:md|yaml|py)|SKILL\.md)", yaml_text):
        paths.add(m.group(0).replace("\\", "/"))
    for m in re.finditer(r"(?:^|\s)(scripts/[\w_]+\.py)", yaml_text):
        paths.add(m.group(1))
    return paths


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="警告也失败")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []

    skill = ROOT / "SKILL.md"
    if skill.is_file():
        n = line_count(skill)
        if n > SKILL_MD_MAX_LINES:
            warnings.append(f"SKILL.md 超预算: {n} 行 (建议 ≤{SKILL_MD_MAX_LINES})")
        if "routing.yaml" not in skill.read_text(encoding="utf-8"):
            errors.append("SKILL.md 未引用 routing.yaml")
    else:
        errors.append("缺少 SKILL.md")

    routing = ROOT / "routing.yaml"
    if not routing.is_file():
        errors.append("缺少 routing.yaml")
    else:
        text = routing.read_text(encoding="utf-8")
        if "tasks:" not in text or "always_read:" not in text:
            errors.append("routing.yaml 缺少 tasks 或 always_read")
        for rel in extract_routing_paths(text):
            if rel.startswith("scripts/"):
                if not (ROOT / rel).is_file():
                    warnings.append(f"routing.yaml 引用脚本不存在: {rel}")
            elif "/" in rel and not rel.startswith("python "):
                candidate = ROOT / rel
                if not candidate.is_file():
                    warnings.append(f"routing.yaml 引用路径不存在: {rel}")

    ALWAYS_READ_SHELLS = [
        "AGENTS.md",
        "CLAUDE.md",
        "CODEX.md",
        "GEMINI.md",
        ".cursor/rules/wuyun-liuqi.mdc",
    ]

    for rel in THIN_SHELLS:
        check_exists(errors, warnings, rel)
        p = ROOT / rel
        if p.is_file():
            body = p.read_text(encoding="utf-8")
            if "routing.yaml" not in body:
                errors.append(f"{rel} 缺少 routing.yaml 引导")
            if "SKILL.md" not in body:
                errors.append(f"{rel} 缺少 SKILL.md 引导")
            if rel in ALWAYS_READ_SHELLS and "rules/calculation.md" not in body:
                errors.append(f"{rel} Always Read 缺少 rules/calculation.md")

    for rel in REQUIRED_RULES + REQUIRED_WORKFLOWS + PLUGIN_FILES:
        check_exists(errors, warnings, rel)

    scenarios = ROOT / "tests" / "routing_scenarios.json"
    if not scenarios.is_file():
        errors.append("缺少 tests/routing_scenarios.json")
    scenario_checker = ROOT / "scripts" / "check_routing_scenarios.py"
    if scenario_checker.is_file():
        import subprocess

        r = subprocess.run(
            [sys.executable, str(scenario_checker)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(ROOT),
        )
        if r.returncode != 0:
            errors.append("check_routing_scenarios.py 未通过")
            if r.stdout:
                for line in r.stdout.strip().splitlines()[-8:]:
                    errors.append(f"  {line}")

    for rel in ["references/gotchas.md", "references/script-index.md"]:
        check_exists(errors, warnings, rel)

    rules_index = ROOT / "RULES.md"
    if rules_index.is_file() and "rules/" not in rules_index.read_text(encoding="utf-8"):
        warnings.append("RULES.md 未索引 rules/ 目录")

    for rel in REQUIRED_RULES:
        p = ROOT / rel
        if p.is_file() and line_count(p) > RULES_MD_MAX_LINES:
            warnings.append(f"{rel} 较长: {line_count(p)} 行 (参考 ≤{RULES_MD_MAX_LINES})")

    gotchas = ROOT / "references/gotchas.md"
    if gotchas.is_file() and line_count(gotchas) > REFERENCES_MD_MAX_LINES:
        warnings.append(f"references/gotchas.md 较长: {line_count(gotchas)} 行")

    for script_name in [
        "sync_routing.py",
        "check_conformance.py",
        "audit_orphans.py",
    ]:
        checker = ROOT / "scripts" / script_name
        if not checker.is_file():
            errors.append(f"缺少 P3 脚本: scripts/{script_name}")
            continue
        import subprocess

        extra_args = ["--check"] if script_name == "sync_routing.py" else []
        r = subprocess.run(
            [sys.executable, str(checker), *extra_args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(ROOT),
        )
        if r.returncode != 0:
            errors.append(f"{script_name} 未通过")

    if not (ROOT / "conformance.yaml").is_file():
        errors.append("缺少 conformance.yaml")

    print("=" * 50)
    print("  技能结构检查")
    print("=" * 50)
    if errors:
        print("\n错误:")
        for e in errors:
            print(f"  ✗ {e}")
    if warnings:
        print("\n警告:")
        for w in warnings:
            print(f"  ! {w}")
    if not errors and not warnings:
        print("\n  ✓ 全部通过")
    else:
        print(f"\n汇总: {len(errors)} 错误, {len(warnings)} 警告")

    if errors:
        return 1
    if args.strict and warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())