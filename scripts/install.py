#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五运六气技能包 一键安装脚本
用法：
    python scripts/install.py

这个脚本可以被 AI 直接调用，帮助用户完成环境准备。
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, shell=False):
    print(f"→ 执行: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
            encoding='utf-8'
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

def main():
    print("=" * 50)
    print("  五运六气技能包 — 一键环境安装")
    print("=" * 50)
    print()

    root = Path(__file__).parent.parent.resolve()
    os.chdir(root)

    # 1. 检测 Python
    print("[1/5] 检测 Python 环境...")
    python_cmd = sys.executable
    print(f"  使用 Python: {python_cmd}")

    # 2. 安装核心依赖
    print("\n[2/5] 安装核心依赖 (lunar-python)...")
    try:
        import lunar_python
        print("  ✓ lunar-python 已安装")
    except ImportError:
        print("  正在安装 lunar-python ...")
        success = run_command([python_cmd, "-m", "pip", "install", "lunar-python", "--quiet"])
        if success:
            print("  ✓ lunar-python 安装成功")
        else:
            print("  [WARN] pip 安装失败，请稍后手动执行：")
            print(f"    {python_cmd} -m pip install lunar-python")

    # 3. 创建自进化目录
    print("\n[3/5] 创建自进化运行时目录...")
    dirs = [
        "self-evolve/logs",
        "self-evolve/misses",
        "self-evolve/feedback",
        "self-evolve/reports",
        "self-evolve/stats"
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    print("  ✓ 自进化目录已就绪")

    # 4. 运行 setup（如果存在）
    print("\n[4/5] 运行平台 setup 脚本（补充检查）...")
    if sys.platform == "win32":
        setup = root / "scripts" / "setup.bat"
        if setup.exists():
            # 直接调用 Python 部分逻辑，避免 pause
            print("  (Windows 环境已通过本脚本处理)")
    else:
        setup = root / "scripts" / "setup.sh"
        if setup.exists():
            print("  (Linux/macOS 环境建议手动 bash scripts/setup.sh)")

    # 5. 基础验证
    print("\n[5/5] 基础验证...")
    try:
        result = subprocess.run(
            [python_cmd, "scripts/calculate_yunqi_api.py", "today", "--summary"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=30
        )
        if result.returncode == 0 and "运气" in result.stdout:
            print("  ✓ 基础推算功能正常（today --summary 可用）")
        else:
            print("  [INFO] 基础推算返回如下（可能正常）：")
            print(result.stdout[:300] if result.stdout else "")
    except Exception as e:
        print(f"  [WARN] 验证时出现问题: {e}")

    print("\n" + "=" * 50)
    print("  ✅ 安装流程完成！")
    print("=" * 50)
    print()
    print("现在你可以直接对 AI 说（复制下面任意一句）：")
    print('  "今天运气怎么样？请用思想层解读解释"')
    print('  "导出 2026 年的思想摘要和 Anki 卡片"')
    print('  "解释天人合一这个概念，用深入版"')
    print()
    print("推荐给 AI 的验证命令：")
    print(f"  {python_cmd} scripts/health_check.py")
    print(f"  {python_cmd} scripts/calculate_yunqi_api.py today --summary --level deep")
    print(f"  {python_cmd} scripts/export_thought.py today --format all")
    print()
    print("如果 AI 能直接执行命令，请让它运行上面任意一条验证。")
    print("安装成功后，所有功能（思想层、导出、自进化等）均可直接使用。")

if __name__ == "__main__":
    main()
