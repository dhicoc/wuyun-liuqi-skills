#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客运推算脚本 [legacy]

用法: python keyun_calc.py <年份> [--json]
输出: 客运五步（初运~终运），每步含五行+太少

客运规则:
  - 以大运为初运，按五行相生排列五步
  - 太过年：初运为太，太少交替
  - 不及年：初运为少，太少交替

推荐主入口:
  python scripts/calculate_yunqi_api.py today --summary
"""
import sys
import os
import json

from _common import setup_environment, build_year_cli_parser
setup_environment()  # 处理 UTF-8 + lib 路径

from yunqi_data import (
    get_dayun, is_taiguo, get_zhuyun_five_steps, get_keyun_five_steps,
    WUXING, WUXING_SHENG,
)


def calc(year):
    dayun, _ = get_dayun(year)
    taiguo = is_taiguo(year)

    zhuyun = get_zhuyun_five_steps(year)
    keyun = get_keyun_five_steps(year)

    step_names = ['初运', '二运', '三运', '四运', '终运']

    steps = []
    for i in range(5):
        zy = zhuyun[i]
        ky = keyun[i]
        steps.append({
            'step': step_names[i],
            '主运': f"{zy[2]}{zy[1]}运",  # e.g. 太木运
            '客运': f"{ky[2]}{ky[1]}运",  # e.g. 太土运
        })

    return {
        '年份': year,
        '大运': f"{dayun}运{'太过' if taiguo else '不及'}",
        '客运初运': f"{'太' if taiguo else '少'}{dayun}运",
        '五步': steps,
    }


def format_text(result):
    lines = [
        f"年份: {result['年份']}",
        f"大运: {result['大运']}",
        f"客运初运: {result['客运初运']}",
        "",
        "五步对比:",
        f"  {'步':<6} {'主运':<8} {'客运':<8}",
        f"  {'─'*30}",
    ]
    for s in result['五步']:
        lines.append(f"  {s['step']:<6} {s['主运']:<8} {s['客运']:<8}")
    return '\n'.join(lines)


if __name__ == '__main__':
    parser = build_year_cli_parser(
        'keyun_calc.py',
        '主运/客运五步推算',
        epilog='示例: python keyun_calc.py 2026 --json',
    )
    args = parser.parse_args()
    result = calc(args.year)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_text(result))
