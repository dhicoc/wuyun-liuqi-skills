#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五运六气技能包 一键安装脚本

用法：
    python scripts/install.py
    python scripts/install.py --link-global
    python scripts/install.py --link-global --force

--link-global  将本仓库链接到 ~/.claude/skills/ 与 ~/.cursor/skills/（场景 B 常驻）
--force        已存在且指向其他路径时，先删除再重建链接
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

GLOBAL_SKILL_NAME = "wuyun-liuqi-skills"


def run_command(cmd, shell=False):
    print(f"→ 执行: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if result.stdout:
            print(result.stdout.strip())
        if result.returncode != 0:
            print(f"[WARN] 返回码: {result.returncode}")
            if result.stderr:
                print(result.stderr.strip())
            return False
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def global_skill_targets():
    home = Path.home()
    return {
        "claude": home / ".claude" / "skills" / GLOBAL_SKILL_NAME,
        "cursor": home / ".cursor" / "skills" / GLOBAL_SKILL_NAME,
    }


def _normalize(path: Path) -> Path:
    try:
        return path.resolve()
    except OSError:
        return path.absolute()


def _subprocess_text_kwargs():
    return {
        "capture_output": True,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
    }


def points_to_source(link_path: Path, source: Path) -> bool:
    """链接/联接/目录解析后是否指向 source。"""
    if not link_path.exists() and not link_path.is_symlink():
        return False
    try:
        return _normalize(link_path) == _normalize(source)
    except OSError:
        return False


def _is_link_like(path: Path) -> bool:
    if path.is_symlink():
        return True
    if not path.exists() or sys.platform != "win32":
        return False
    try:
        import stat

        return stat.S_ISLNK(os.lstat(path).st_mode)
    except OSError:
        return False


def remove_link_path(link_path: Path) -> bool:
    """删除符号链接或目录联接，不删除链接目标内容。"""
    if not link_path.exists() and not link_path.is_symlink():
        return True
    try:
        if link_path.is_symlink():
            link_path.unlink()
            return True
        if sys.platform == "win32":
            subprocess.run(
                ["cmd", "/c", "rmdir", str(link_path)],
                check=False,
                **_subprocess_text_kwargs(),
            )
            if not link_path.exists():
                return True
        if link_path.is_dir():
            link_path.rmdir()
            return True
        link_path.unlink()
        return True
    except OSError as e:
        print(f"  [ERROR] 无法删除已有路径 {link_path}: {e}")
        return False


def create_directory_link(source: Path, target: Path) -> Tuple[bool, str]:
    source = _normalize(source)
    target.parent.mkdir(parents=True, exist_ok=True)

    if sys.platform == "win32":
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(target), str(source)],
            **_subprocess_text_kwargs(),
        )
        if result.returncode == 0:
            return True, "junction"
        err = (result.stderr or result.stdout or "").strip()
        # 开发者模式或权限不足时尝试 symlink
        try:
            os.symlink(source, target, target_is_directory=True)
            return True, "symlink"
        except OSError as e:
            return False, err or str(e)

    try:
        os.symlink(source, target, target_is_directory=True)
        return True, "symlink"
    except OSError as e:
        return False, str(e)


def link_global_skill(source: Path, target: Path, force: bool) -> Tuple[bool, str]:
    source = _normalize(source)

    if target.exists() or target.is_symlink():
        if points_to_source(target, source):
            return True, f"已指向 {source}（跳过）"

        resolved = _normalize(target) if target.exists() else None
        if not force:
            kind = "链接" if _is_link_like(target) else "目录"
            dest = f" → {resolved}" if resolved else ""
            return False, f"已存在{kind} {target}{dest}；加 --force 覆盖"

        if not remove_link_path(target):
            if target.is_dir():
                try:
                    shutil.rmtree(target)
                except OSError as e:
                    hint = ""
                    if getattr(e, "winerror", None) == 5 or "Permission" in str(e):
                        hint = "（可先关闭 Claude Code/Cursor 后重试 --force）"
                    return False, f"无法删除已有目录: {e}{hint}"
            elif target.exists() or target.is_symlink():
                try:
                    target.unlink()
                except OSError as e:
                    return False, f"无法删除已有路径: {e}"

    ok, detail = create_directory_link(source, target)
    if ok:
        return True, f"已链接 → {source} ({detail})"
    return False, detail


def register_global_skills(root: Path, force: bool, step: int, total: int) -> None:
    print(f"\n[{step}/{total}] 全局技能目录注册 (--link-global)...")
    print(f"  源目录: {root}")
    results = []
    for name, target in global_skill_targets().items():
        ok, msg = link_global_skill(root, target, force)
        mark = "✓" if ok else "✗"
        print(f"  {mark} {name}: {target}")
        print(f"      {msg}")
        results.append(ok)

    if all(results):
        print("  ✓ 全局注册完成：可在任意项目中通过触发词激活技能")
    else:
        print("  [WARN] 部分注册失败；可手动执行 workflows/one-line-install.md 中的命令")


def parse_args():
    parser = argparse.ArgumentParser(description="五运六气技能包一键安装")
    parser.add_argument(
        "--link-global",
        action="store_true",
        help="链接到 ~/.claude/skills/ 与 ~/.cursor/skills/wuyun-liuqi-skills",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="与 --link-global 合用：覆盖已存在的错误链接或目录",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    total_steps = 8 if args.link_global else 7

    print("=" * 50)
    print("  五运六气技能包 — 一键环境安装")
    print("=" * 50)
    print()

    root = Path(__file__).parent.parent.resolve()
    os.chdir(root)

    print(f"[1/{total_steps}] 检测 Python 环境...")
    python_cmd = sys.executable
    print(f"  使用 Python: {python_cmd}")

    print(f"\n[2/{total_steps}] 安装核心依赖 (lunar-python)...")
    try:
        import lunar_python  # noqa: F401

        print("  ✓ lunar-python 已安装")
    except ImportError:
        print("  正在安装 lunar-python ...")
        success = run_command(
            [python_cmd, "-m", "pip", "install", "lunar-python", "--quiet"]
        )
        if success:
            print("  ✓ lunar-python 安装成功")
        else:
            print("  [WARN] pip 安装失败，请稍后手动执行：")
            print(f"    {python_cmd} -m pip install lunar-python")

    print(f"\n[3/{total_steps}] 创建自进化运行时目录...")
    dirs = [
        "self-evolve/logs",
        "self-evolve/misses",
        "self-evolve/feedback",
        "self-evolve/reports",
        "self-evolve/stats",
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    print("  ✓ 自进化目录已就绪")

    print(f"\n[4/{total_steps}] 运行平台 setup 脚本（补充检查）...")
    if sys.platform == "win32":
        print("  (Windows 环境已通过本脚本处理)")
    else:
        print("  (Linux/macOS 可选 bash scripts/setup.sh)")

    print(f"\n[5/{total_steps}] 检查技能结构（薄壳 + 路由）...")
    shell_files = [
        "SKILL.md",
        "routing.yaml",
        "AGENTS.md",
        "CLAUDE.md",
        ".cursor/skills/wuyun-liuqi/SKILL.md",
    ]
    for rel in shell_files:
        p = root / rel
        mark = "✓" if p.exists() else "✗"
        print(f"  {mark} {rel}")

    print(f"\n[6/{total_steps}] 基础推算验证...")
    try:
        result = subprocess.run(
            [python_cmd, "scripts/calculate_yunqi_api.py", "today", "--summary"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        if result.returncode == 0 and "运气" in (result.stdout or ""):
            print("  ✓ 基础推算功能正常（today --summary 可用）")
        else:
            print("  [INFO] 基础推算返回如下（可能正常）：")
            print((result.stdout or "")[:300])
    except Exception as e:
        print(f"  [WARN] 验证时出现问题: {e}")

    step_activate = 7
    if args.link_global:
        register_global_skills(root, args.force, 7, total_steps)
        step_activate = 8

    print(f"\n[{step_activate}/{total_steps}] 激活方式...")
    print(f"  技能包根目录: {root}")
    if args.link_global:
        print("  ✓ 已执行 --link-global：任意项目中说「五运六气」等触发词即可")
        for name, target in global_skill_targets().items():
            print(f"    · {name}: {target}")
    else:
        print()
        print("  场景 A — 打开本文件夹作为工作区（Cursor / Claude Code）")
        print("  场景 B — 任意项目常驻:")
        print(f"    python scripts/install.py --link-global")
        print("    详细步骤见 workflows/one-line-install.md")

    print("\n" + "=" * 50)
    print("  ✅ 安装流程完成！")
    print("=" * 50)
    print()
    print("试用语句：")
    print('  "今天运气怎么样？请用思想层解读解释"')
    print('  "解释天人合一这个概念，用深入版"')
    print()
    print("验证命令：")
    print(f"  {python_cmd} scripts/health_check.py")
    print(f"  {python_cmd} scripts/calculate_yunqi_api.py today --summary --level deep")


if __name__ == "__main__":
    main()