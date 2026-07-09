#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 路由场景检查（P2）

用法: python scripts/check_routing_scenarios.py [--strict]

验证用户话术 → routing.yaml task → 脚本/工作流/必读文件 的链路是否完整。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from _common import setup_utf8_stdout
setup_utf8_stdout()

ROOT = Path(__file__).resolve().parent.parent
ROUTING = ROOT / "routing.yaml"
SCENARIOS = ROOT / "tests" / "routing_scenarios.json"


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_task_block(yaml_text: str, task_id: str) -> str:
    """提取 routing.yaml 中单个 task 的 YAML 块（行文本）。"""
    lines = yaml_text.splitlines()
    block: list[str] = []
    in_task = False
    for line in lines:
        if re.match(r"^\s*-\s+id:\s*", line):
            current = re.sub(r"^\s*-\s+id:\s*", "", line).strip()
            in_task = current == task_id
            if in_task:
                block = [line]
            continue
        if in_task:
            if re.match(r"^\s*-\s+id:\s*", line):
                break
            block.append(line)
    return "\n".join(block)


def extract_section(yaml_text: str, section: str) -> str:
    """提取 routing.yaml 中某顶级节（如 cross_paths）的文本。"""
    lines = yaml_text.splitlines()
    out: list[str] = []
    in_section = False
    section_indent = 0
    for line in lines:
        if re.match(rf"^{section}:\s*$", line):
            in_section = True
            section_indent = len(line) - len(line.lstrip())
            out.append(line)
            continue
        if in_section:
            if line.strip() and not line.startswith(" " * (section_indent + 1)) and not line.startswith("\t"):
                break
            out.append(line)
    return "\n".join(out)


def extract_cross_path_block(yaml_text: str, path_id: str) -> str:
    section = extract_section(yaml_text, "cross_paths")
    return extract_task_block(section, path_id)


def fuzzy_workflow(yaml_text: str) -> str | None:
    m = re.search(r"fuzzy_intent:\s*\n(?:.*\n)*?\s+workflow:\s*(\S+)", yaml_text)
    return m.group(1) if m else None


def resolve_path(rel: str) -> Path:
    rel = rel.replace("\\", "/").strip("/")
    if rel.startswith("scripts/"):
        return ROOT / rel
    if rel.endswith("/"):
        return ROOT / rel
    p = ROOT / rel
    if p.is_file():
        return p
    if p.is_dir():
        return p
    # SKILL.md 或目录前缀
    for suffix in ("", "/SKILL.md"):
        candidate = ROOT / f"{rel}{suffix}"
        if candidate.exists():
            return candidate
    return p


def path_exists(rel: str) -> bool:
    p = resolve_path(rel)
    return p.exists()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="警告也失败")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    passed = 0

    if not ROUTING.is_file():
        errors.append("缺少 routing.yaml")
        print_summary(errors, warnings, passed)
        return 1

    if not SCENARIOS.is_file():
        errors.append("缺少 tests/routing_scenarios.json")
        print_summary(errors, warnings, passed)
        return 1

    routing_text = load_text(ROUTING)
    spec = json.loads(SCENARIOS.read_text(encoding="utf-8"))

    print("=" * 50)
    print("  Agent 路由场景检查")
    print("=" * 50)

    for rel in spec.get("always_read", []):
        if path_exists(rel):
            passed += 1
            print(f"  ✓ always_read: {rel}")
        else:
            errors.append(f"always_read 文件不存在: {rel}")

    for scenario in spec.get("scenarios", []):
        name = scenario["name"]
        task_id = scenario["task_id"]
        prompt = scenario.get("prompt", "")
        block = extract_task_block(routing_text, task_id)

        print(f"\n==> {name} ({task_id})")
        if not block:
            errors.append(f"{name}: task '{task_id}' 不存在")
            continue

        if prompt and prompt not in block:
            errors.append(f"{name}: trigger_examples 未含「{prompt}」")
        else:
            passed += 1
            print(f"  ✓ trigger: {prompt}")

        for key, needle in [
            ("expect_route", "route:"),
            ("expect_workflow", "workflow:"),
        ]:
            val = scenario.get(key)
            if val and val not in block:
                errors.append(f"{name}: 缺少 {key}={val}")
            elif val:
                passed += 1
                print(f"  ✓ {key}: {val}")

        for key in ("expect_script_contains", "expect_route_contains"):
            val = scenario.get(key)
            if val and val not in block:
                errors.append(f"{name}: task 块未含「{val}」")
            elif val:
                passed += 1
                print(f"  ✓ contains: {val}")

        for rel in scenario.get("expect_required_reads", []):
            if rel not in block:
                errors.append(f"{name}: required_reads 未含 {rel}")
            elif not path_exists(rel):
                errors.append(f"{name}: required_reads 路径不存在 {rel}")
            else:
                passed += 1
                print(f"  ✓ required_read: {rel}")

        route = scenario.get("expect_route")
        if route and not path_exists(route):
            errors.append(f"{name}: route 路径不存在 {route}")

    fuzzy_wf = fuzzy_workflow(routing_text)
    for scenario in spec.get("fuzzy_scenarios", []):
        name = scenario["name"]
        expect = scenario["expect_workflow"]
        print(f"\n==> [fuzzy] {name}")
        if fuzzy_wf != expect:
            errors.append(f"{name}: fuzzy_intent.workflow 应为 {expect}，实际 {fuzzy_wf}")
        else:
            passed += 1
            print(f"  ✓ fuzzy workflow: {expect}")
        if not path_exists(expect):
            errors.append(f"{name}: fuzzy workflow 文件不存在 {expect}")

    for cp in spec.get("cross_paths", []):
        name = cp["name"]
        path_id = cp["path_id"]
        block = extract_cross_path_block(routing_text, path_id)
        print(f"\n==> [cross_path] {name} ({path_id})")
        if not block:
            errors.append(f"{name}: cross_path '{path_id}' 不存在")
            continue
        for step in cp.get("expect_steps", []):
            if step not in block:
                errors.append(f"{name}: steps 未含 {step}")
            elif not path_exists(step):
                errors.append(f"{name}: step 路径不存在 {step}")
            else:
                passed += 1
                print(f"  ✓ step: {step}")

    # SKILL.md Common Tasks 与 routing tasks 对齐
    skill_md = ROOT / "SKILL.md"
    if skill_md.is_file():
        skill_text = load_text(skill_md)
        task_ids = re.findall(r"`tasks/([\w-]+)`", skill_text)
        for tid in task_ids:
            if not extract_task_block(routing_text, tid):
                warnings.append(f"SKILL.md 引用 tasks/{tid} 但 routing.yaml 无此 id")
            else:
                passed += 1

    print_summary(errors, warnings, passed)
    if errors:
        return 1
    if args.strict and warnings:
        return 1
    return 0


def print_summary(errors: list[str], warnings: list[str], passed: int) -> None:
    print("\n" + "=" * 50)
    if errors:
        print("错误:")
        for e in errors:
            print(f"  ✗ {e}")
    if warnings:
        print("警告:")
        for w in warnings:
            print(f"  ! {w}")
    print(f"\n汇总: {passed} 项通过, {len(errors)} 错误, {len(warnings)} 警告")
    if not errors and not warnings:
        print("  ✓ 全部通过")


if __name__ == "__main__":
    sys.exit(main())