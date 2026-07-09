#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
conformance.yaml 内容一致性检查（P3）

用法: python scripts/check_conformance.py [--strict]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from _common import setup_utf8_stdout
setup_utf8_stdout()

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "conformance.yaml"


def parse_conformance(text: str) -> tuple[list[dict], list[dict]]:
    """极简 YAML 解析：required_sections + required_files。"""
    sections: list[dict] = []
    files: list[dict] = []
    mode: str | None = None
    current: dict | None = None
    sub: str | None = None

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line == "required_sections:":
            mode = "sections"
            current = None
            sub = None
            continue
        if line == "required_files:":
            mode = "files"
            current = None
            sub = None
            continue
        if mode == "sections" and line.startswith("- file:"):
            current = {"file": line.split(":", 1)[1].strip(), "must_contain": []}
            sections.append(current)
            sub = None
            continue
        if mode == "sections" and current and line == "must_contain:":
            sub = "must_contain"
            continue
        if mode == "sections" and sub == "must_contain" and line.startswith("- "):
            val = line[2:].strip()
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            current["must_contain"].append(val)
            continue
        if mode == "files" and line.startswith("- path:"):
            files.append({"path": line.split(":", 1)[1].strip()})
            continue
    return sections, files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    passed = 0

    if not MANIFEST.is_file():
        print("缺少 conformance.yaml")
        return 1

    sections, files = parse_conformance(MANIFEST.read_text(encoding="utf-8"))

    print("=" * 50)
    print("  conformance 检查")
    print("=" * 50)

    for spec in sections:
        rel = spec["file"]
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"缺少文件: {rel}")
            continue
        body = path.read_text(encoding="utf-8")
        for needle in spec.get("must_contain", []):
            if needle not in body:
                errors.append(f"{rel} 缺少必含片段: {needle!r}")
            else:
                passed += 1
                print(f"  ✓ {rel} ⊃ {needle[:40]}")

    for spec in files:
        rel = spec["path"]
        if (ROOT / rel).is_file():
            passed += 1
            print(f"  ✓ 存在 {rel}")
        else:
            errors.append(f"缺少 required_file: {rel}")

    print("\n" + "=" * 50)
    if errors:
        print("错误:")
        for e in errors:
            print(f"  ✗ {e}")
    print(f"汇总: {passed} 通过, {len(errors)} 错误, {len(warnings)} 警告")

    if errors:
        return 1
    if args.strict and warnings:
        return 1
    if not errors:
        print("  ✓ 全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())