#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视觉一致性检查（P3）— 宣纸水墨设计体系强制关卡

任何面向读者的视觉产物（HTML 报告 / PDF / 卡片 / 时间轴 / Anki 等）必须复用
`scripts/lib/ink_theme.py` 导出的宣纸水墨设计 token，禁止 agent 现场自由发挥
视觉风格（如深色霓虹配色）。本脚本是「硬约束」的可验证检查点：

  1. 扫描 `reports/**` 下所有 HTML/CSS 产物，若含视觉样式但未引用 ink_theme
     设计 token（--paper / --ink / --vermilion / --wx-* / --gold / ink_theme 等）
     → 报错。
  2. 扫描 `scripts/**/*.py` 中所有「内联输出 HTML 样式」的脚本（含 <style 或
     style=），要求引用 ink_theme（import 或字符串）；否则报错。这能抓住像
     visualize_yunqi.py 这类「脚本侧」却绕过 ink_theme 的视觉产物。

用法:
  python scripts/check_visual_consistency.py [--root <dir>] [--strict]
  python scripts/check_visual_consistency.py --scan-scripts   # 仅检查脚本侧

默认: 错误 → exit 1，警告 → 打印但 exit 0；--strict 时警告也失败。
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from _common import setup_utf8_stdout, PROJECT_ROOT
setup_utf8_stdout()

ROOT = PROJECT_ROOT

# 宣纸水墨设计 token 签名：命中任一即视为「已复用 ink_theme 设计体系」。
INK_SIGNATURE = (
    "ink_theme",      # 直接引用模块
    "--paper",        # ink_theme.css_vars() 导出的纸色变量
    "--ink",          # 墨色阶变量
    "--vermilion",    # 朱砂变量
    "--gold",         # 落款金变量
    "--wx-",          # 五行正色变量（--wx-木 等）
    "paper-texture",  # ink_theme.paper_texture()
    "ink-wash",       # ink_theme.ink_wash()
    "宣纸水墨",        # 主题标识
)

# 判定「这是视觉产物」的信号（HTML/CSS）。
VISUAL_SIGNAL_HTML = ("<style", "style=", "<svg", "background:", "color:", "--")

# 脚本侧：含以下片段即视为「输出带样式的 HTML」，须引用 ink_theme。
# 注意只用 <style 标签，或带 CSS 语义的 style="...:.../;..." —— 排除 rich
# 终端样式字符串（如 style="bold red"，无冒号/分号，不是 HTML 内联样式）。
_RE_INLINE_CSS = re.compile(r'style="[^"]*[:;]')
SCRIPT_EMITS_STYLE = ("<style",)
SCRIPT_EMITS_STYLE_RE = _RE_INLINE_CSS


def _git_ignored(paths: list[Path]) -> set[Path]:
    """返回被 .gitignore 忽略的路径集合（构建产物，不应作为源码检查）。"""
    if not paths:
        return set()
    try:
        proc = subprocess.run(
            ["git", "check-ignore", "--stdin"],
            input="\n".join(str(p) for p in paths),
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(ROOT),
        )
        ignored = set(Path(line) for line in proc.stdout.splitlines() if line.strip())
        return ignored
    except Exception:
        return set()

# 已知需要重构/豁免的视觉产物（临时；应在后续清理，不要长期依赖）。
# 形如相对 ROOT 的路径片段；匹配到则降级为警告而非错误。
ALLOWLIST_PARTIAL = (
    # 测试烟雾产物：由 CI 临时生成、非交付物，允许短期偏离；
    # 若它们来自未复用 ink_theme 的生成器，应修生成器而非此处。
    "reports/test-results/smoke_",
    "reports/test-results/_sprint_smoke",
    "reports/test-results/_html_rag_smoke",
)

# 构建产物目录（与 .gitignore 对齐）：交付物由脚本再生，不作为源码检查。
# 这些目录下的 HTML 即便被误提交（历史遗留）也不计入视觉一致性关卡。
BUILD_OUTPUT_PREFIXES = (
    "reports/generated/",
    "reports/test-results/",
)


def has_ink_signature(text: str) -> bool:
    return any(tok in text for tok in INK_SIGNATURE)


def is_visual_html(text: str) -> bool:
    return any(sig in text for sig in VISUAL_SIGNAL_HTML)


def is_allowlisted(path: Path) -> bool:
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    return any(rel.startswith(a) or a in rel for a in ALLOWLIST_PARTIAL)


def scan_html_css(errors: list, warnings: list, root: Path) -> None:
    candidates: list[Path] = []
    for pat in ("**/*.html", "**/*.htm", "**/*.css"):
        candidates.extend(sorted(root.glob(pat)))
    ignored = _git_ignored(candidates)  # 跳过构建产物（reports/generated 等）
    for p in candidates:
        rel = str(p.relative_to(root)).replace("\\", "/")
        if p in ignored:
            continue
        if any(rel.startswith(pre) or ("/" + pre) in ("/" + rel)
               for pre in BUILD_OUTPUT_PREFIXES):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:  # pragma: no cover
            warnings.append(f"读取失败 {p}: {e}")
            continue
        if p.suffix.lower() == ".css":
            visual = True
        else:
            if not is_visual_html(text):
                continue  # 纯数据/重定向 HTML，非视觉产物
            visual = True
        if not visual:
            continue
        if not has_ink_signature(text):
            rel = str(p.relative_to(ROOT)).replace("\\", "/")
            msg = f"视觉产物未复用 ink_theme 设计 token: {rel}"
            if is_allowlisted(p):
                warnings.append(msg + " （allowlist 临时降级）")
            else:
                errors.append(msg)


def scan_scripts(errors: list, warnings: list, root: Path) -> None:
    for p in sorted((root / "scripts").glob("*.py")):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        emits = ("<style" in text) or bool(SCRIPT_EMITS_STYLE_RE.search(text))
        if not emits:
            continue  # 不输出带样式的 HTML，跳过
        if not has_ink_signature(text):
            rel = str(p.relative_to(ROOT)).replace("\\", "/")
            msg = f"脚本输出内联样式 HTML 但未引用 ink_theme: {rel}"
            # 脚本侧默认视为错误（硬约束），但允许 --warn-scripts 降级。
            errors.append(msg)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--strict", action="store_true", help="警告也失败")
    ap.add_argument("--scan-scripts", action="store_true",
                    help="仅检查 scripts/** 内联 HTML 样式脚本")
    ap.add_argument("--no-scripts", action="store_true",
                    help="跳过 scripts/** 侧检查（仅检查 reports 产物）")
    args = ap.parse_args()

    root = Path(args.root)
    errors: list[str] = []
    warnings: list[str] = []

    print("=" * 50)
    print("  宣纸水墨视觉一致性检查")
    print("=" * 50)

    if not args.scan_scripts:
        scan_html_css(errors, warnings, root)
    if not args.no_scripts:
        scan_scripts(errors, warnings, root)

    if errors:
        print("\n错误:")
        for e in errors:
            print(f"  ✗ {e}")
    if warnings:
        print("\n警告:")
        for w in warnings:
            print(f"  ! {w}")
    if not errors and not warnings:
        print("\n  ✓ 全部视觉产物复用 ink_theme 设计体系")

    print(f"\n汇总: {len(errors)} 错误, {len(warnings)} 警告")
    if errors:
        return 1
    if args.strict and warnings:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
