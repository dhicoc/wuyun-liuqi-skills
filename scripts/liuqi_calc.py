#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
六气推算脚本 [legacy]

用法: python liuqi_calc.py <年份> [--json]
输出: 司天、在泉、客气六步、主气六步

六气规则:
  - 司天 = 地支化气（上半年主管）
  - 在泉 = 司天之对化（下半年主管）
  - 客气六步: 按阴阳推移，司天为三之气，在泉为终之气
  - 主气六步: 每年固定，按季节顺序

推荐主入口:
  python scripts/calculate_yunqi_api.py today --summary
"""
import sys
import os
import json

from _common import setup_environment, build_year_cli_parser
setup_environment()  # 处理 UTF-8 + lib 路径

from yunqi_data import (
    get_sitian, get_zaiquan, get_keqi_six_steps, get_zhuqi_six_steps,
    ZHUQI_JIEQI, LIUQI_YINYANG, get_ganzhi,
)


def calc(year):
    tg, dz = get_ganzhi(year)
    sitian = get_sitian(year)
    zaiquan = get_zaiquan(year)
    keqi = get_keqi_six_steps(year)
    zhuqi = get_zhuqi_six_steps()

    step_names = ['初之气', '二之气', '三之气', '四之气', '五之气', '终之气']

    six_steps = []
    for i in range(6):
        kq = keqi[i]
        zq = zhuqi[i]
        jq = ZHUQI_JIEQI[i + 1]
        six_steps.append({
            'step': step_names[i],
            '节气': f'{jq[0]}~{jq[1]}',
            '主气': zq[1],
            '客气': kq[1],
            '客气阴阳': LIUQI_YINYANG[kq[1]],
            '备注': '司天' if kq[2] else ('在泉' if kq[3] else ''),
        })

    return {
        '年份': year,
        '干支': f'{tg}{dz}',
        '司天': sitian,
        '司天阴阳': LIUQI_YINYANG[sitian],
        '在泉': zaiquan,
        '在泉阴阳': LIUQI_YINYANG[zaiquan],
        '六步': six_steps,
    }


def format_text(result):
    lines = [
        f"年份: {result['年份']} ({result['干支']}年)",
        f"司天: {result['司天']} ({result['司天阴阳']}) — 上半年主管",
        f"在泉: {result['在泉']} ({result['在泉阴阳']}) — 下半年主管",
        "",
        f"{'步':<6} {'节气':<10} {'主气':<8} {'客气':<8} {'阴阳':<6} {'备注'}",
        f"{'─'*50}",
    ]
    for s in result['六步']:
        lines.append(
            f"{s['step']:<6} {s['节气']:<10} {s['主气']:<8} {s['客气']:<8} "
            f"{s['客气阴阳']:<6} {s['备注']}"
        )
    return '\n'.join(lines)


if __name__ == '__main__':
    parser = build_year_cli_parser(
        'liuqi_calc.py',
        '六气推算：司天在泉、主气客气六步',
        epilog='示例: python liuqi_calc.py 2026 --json',
    )
    args = parser.parse_args()
    result = calc(args.year)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_text(result))
