#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wuyun-liuqi 健康检查脚本
检测：Python 环境、依赖安装、脚本可执行性、终端编码
用法:
  python scripts/health_check.py
"""
import sys
import os
import io
import subprocess

from _common import setup_environment, success, warning, error
setup_environment(add_lib=False)


def check_encoding():
    """检查当前 stdout 编码"""
    encoding = getattr(sys.stdout, 'encoding', None)
    is_utf8 = encoding is not None and encoding.lower() in ('utf-8', 'utf_8')
    return {
        'stdout_encoding': encoding,
        'utf8_ready': is_utf8,
    }


def check_dependency():
    """检查 lunar-python 是否已安装"""
    try:
        import lunar_python
        return {
            'lunar_python': 'OK',
            'version': getattr(lunar_python, '__version__', 'unknown'),
        }
    except ImportError as e:
        return {
            'lunar_python': 'MISSING',
            'error': str(e),
        }


def check_script(script_name):
    """检查单个脚本能否正常运行"""
    skill_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script_path = os.path.join(skill_root, 'scripts', script_name)
    if not os.path.exists(script_path):
        return {'exists': False, 'error': 'file not found'}

    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'

    # yunqi_report.py 需要年份参数，其余需要日期参数
    if script_name == 'yunqi_report.py':
        args = [sys.executable, script_path, '2026', '--json']
    else:
        args = [sys.executable, script_path, '2026-06-29', '--json']

    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding='utf-8',
        env=env,
    )
    try:
        output = result.stdout
        has_chinese = any('一' <= ch <= '鿿' for ch in output[:500])
        return {
            'exists': True,
            'returncode': result.returncode,
            'chinese_readable': has_chinese,
            'error': result.stderr[:300] if result.returncode != 0 else None,
        }
    except Exception as e:
        return {
            'exists': True,
            'returncode': result.returncode,
            'chinese_readable': False,
            'error': str(e),
        }


def main():
    from _common import setup_utf8_stdout
    setup_utf8_stdout()

    print('🔍 wuyun-liuqi 健康检查')
    print('=' * 40)

    enc = check_encoding()
    print(f"[编码] stdout 编码: {enc['stdout_encoding']}")
    print(f"       UTF-8 就绪: {'✅ 是' if enc['utf8_ready'] else '❌ 否'}")
    if not enc['utf8_ready']:
        print("       建议: 运行 setup.bat/setup.sh，或设置 PYTHONIOENCODING=utf-8")

    dep = check_dependency()
    print(f"\n[依赖] lunar-python: {dep['lunar_python']}")
    if dep['lunar_python'] != 'OK':
        print(f"       错误: {dep.get('error')}")
        print("       建议: pip install lunar-python")
        print("       注意: 未安装时将使用近似节气日期，推算精度降低")
    else:
        print("       ✓ 精确节气计算已启用")

    scripts_to_check = [
        'calculate_yunqi_api.py',
        'yunqi_report.py',
        'verify_expansion.py',
    ]
    print("\n[脚本]")
    script_statuses = {}
    for script in scripts_to_check:
        status = check_script(script)
        script_statuses[script] = status
        if not status['exists']:
            print(f"  ❌ {script}: 文件不存在")
            continue
        if status['returncode'] != 0:
            print(f"  ❌ {script}: 运行失败 ({status.get('error')})")
            continue
        if status['chinese_readable']:
            print(f"  ✅ {script}: 运行正常，中文输出可读")
        else:
            print(f"  ⚠️  {script}: 运行正常，但中文输出可能乱码")

    print('\n' + '=' * 40)
    all_ok = (
        enc['utf8_ready']
        and dep['lunar_python'] == 'OK'
        and all(s['returncode'] == 0 for s in script_statuses.values())
    )
    if all_ok:
        print(success('✅ 健康检查通过，环境就绪'))
        print('\n推荐下一步（直接复制运行）：')
        print('  python scripts/calculate_yunqi_api.py today --summary')
        print('  python scripts/demo_full_chain.py')
        print('  python scripts/calculate_yunqi_api.py today --report-type student')
        print('\n想看个人体质： python scripts/personal_yunqi_profile.py <出生日期> <城市>')
    else:
        print(error('❌ 健康检查未通过，请按上方建议修复'))
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())
