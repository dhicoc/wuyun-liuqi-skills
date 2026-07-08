#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
干支推算脚本
用法: python ganzhi_calc.py <年份>
输出: 天干、地支、六十甲子序号、生肖
"""
import sys
import os
import json

from _common import setup_environment
setup_environment()  # 处理 UTF-8 + lib 路径

from yunqi_data import TIANGAN, DIZHI, DIZHI_SHENGXIAO, get_ganzhi, get_sexagenary_index


def calc(year):
    tg, dz = get_ganzhi(year)
    idx = get_sexagenary_index(year)
    sx = DIZHI_SHENGXIAO[dz]
    return {
        '年份': year,
        '天干': tg,
        '地支': dz,
        '干支': f'{tg}{dz}',
        '六十甲子序号': idx,
        '生肖': sx,
    }


def format_text(result):
    lines = [
        f"年份: {result['年份']}",
        f"天干: {result['天干']}",
        f"地支: {result['地支']}",
        f"干支: {result['干支']}",
        f"六十甲子序号: {result['六十甲子序号']}",
        f"生肖: {result['生肖']}",
    ]
    return '\n'.join(lines)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python ganzhi_calc.py <年份>")
        sys.exit(1)
    year = int(sys.argv[1])
    result = calc(year)

    if '--json' in sys.argv:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_text(result))
