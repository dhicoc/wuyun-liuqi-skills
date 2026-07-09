# -*- coding: utf-8 -*-
"""
共享环境初始化工具（P0 优化）

用途：
- 统一处理 Windows 控制台 UTF-8 输出问题（避免中文乱码）
- 统一将 scripts/lib 加入 sys.path，方便 from yunqi_data import ...

使用方式（推荐在每个脚本最前面）：
    from _common import setup_environment
    setup_environment()

或者只做 UTF-8：
    from _common import setup_utf8_stdout
    setup_utf8_stdout()

注意：
- 本模块故意不自动执行，必须显式调用。
- 所有新脚本和重构脚本都应使用本模块，逐步淘汰重复样板代码。
"""

import sys
import os
import io


def setup_utf8_stdout():
    """Windows 下强制 stdout/stderr 使用 UTF-8，避免中文乱码。"""
    if sys.platform == 'win32':
        try:
            if getattr(sys.stdout, 'encoding', None) != 'utf-8':
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
            if getattr(sys.stderr, 'encoding', None) != 'utf-8':
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
        except (AttributeError, io.UnsupportedOperation):
            # 在某些重定向或特殊环境（如某些 IDE）下可能不支持，静默降级
            pass


def add_lib_to_path():
    """将本脚本所在目录下的 lib/ 加入 sys.path（优先级最高）。"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    lib_dir = os.path.join(script_dir, 'lib')
    if lib_dir not in sys.path:
        sys.path.insert(0, lib_dir)


def ensure_importable_from_scripts(target_dir=None):
    """
    辅助函数：从任意位置确保可以 import scripts 下的模块。
    主要用于测试或外部调用。
    """
    if target_dir is None:
        # 默认假设调用者相对 scripts
        base = os.path.dirname(os.path.abspath(__file__))
    else:
        base = os.path.abspath(target_dir)
    if base not in sys.path:
        sys.path.insert(0, base)


def add_scripts_dir_to_path():
    """将本脚本所在目录加入 sys.path，用于同目录脚本直接 import（例如 constitution_assessment）。"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)


def setup_environment(add_lib=True, add_scripts=False):
    """
    一键初始化环境。

    参数:
        add_lib: 是否把 scripts/lib 加入路径（默认 True，绝大多数计算脚本需要）
        add_scripts: 是否把脚本所在目录加入路径（用于跨脚本直接 import 同级模块）
    """
    setup_utf8_stdout()
    if add_lib:
        add_lib_to_path()
    if add_scripts:
        add_scripts_dir_to_path()


# ═══════════════════════════════════════════════════════════════
# 轻量终端颜色支持 (UX P1-2，无额外依赖)
# 使用 ANSI 转义码，在不支持的环境会优雅降级
# ═══════════════════════════════════════════════════════════════

# 颜色代码
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"

def color(text, color_code):
    """包装文本为彩色（如果终端支持）。"""
    if not text:
        return text
    # 简单检测：Windows 旧版或非 tty 时可能不理想，但现代系统通常支持
    try:
        import sys
        if sys.stdout.isatty():
            return f"{color_code}{text}{RESET}"
    except Exception:
        pass
    return text

def highlight_key(text):
    """高亮关键运气术语：太过/不及、相得/不相得 等"""
    replacements = [
        ("太过", f"{RED}{BOLD}太过{RESET}"),
        ("不及", f"{YELLOW}{BOLD}不及{RESET}"),
        ("相得", f"{GREEN}{BOLD}相得{RESET}"),
        ("不相得", f"{RED}{BOLD}不相得{RESET}"),
        ("平气", f"{CYAN}{BOLD}平气{RESET}"),
        ("天符", f"{MAGENTA}{BOLD}天符{RESET}"),
        ("岁会", f"{MAGENTA}{BOLD}岁会{RESET}"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text

def success(text):
    return color(text, GREEN)

def warning(text):
    return color(text, YELLOW)

def error(text):
    return color(text, RED)


# ═══════════════════════════════════════════════════════════════
# Legacy 分项脚本 CLI 辅助（optimization-sprint P2-1）
# ═══════════════════════════════════════════════════════════════

def build_year_cli_parser(prog: str, description: str, epilog: str = None):
    """
    为 year 位置参数 + --json 的分项脚本构建 argparse。
    用法保持兼容：python xxx.py <年份> [--json]
    """
    import argparse
    legacy_note = (
        "\n\n[legacy] 分项入口。完整日期推算请优先使用：\n"
        "  python scripts/calculate_yunqi_api.py today --summary"
    )
    full_epilog = (epilog or "") + legacy_note
    parser = argparse.ArgumentParser(
        prog=prog,
        description=description,
        epilog=full_epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("year", type=int, help="公历年份，如 2026")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    return parser
