#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五运六气 ASCII 可视化
基于 calculate_yunqi_api 输出，生成终端可显示的 ASCII 图表。

用法:
  python scripts/visualize_yunqi.py <YYYY-MM-DD>
"""
import sys
import os
import json
import subprocess

from _common import setup_environment
setup_environment(add_lib=False)  # 本脚本主要调用其他脚本，不一定需要 lib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_result(date_str):
    """直接调用（P0 优化）"""
    sys.path.insert(0, os.path.join(BASE_DIR, 'scripts', 'lib'))
    from calculate_yunqi_api import calculate_yunqi_api
    return calculate_yunqi_api(date_str)


def visualize(data):
    year_gz = data['year_gz']
    sui_yun = data['sui_yun']
    si_tian = data['si_tian']
    zai_quan = data['zai_quan']
    current_step = data['current_step']
    jieqi_dates = data['jieqi_dates']

    lines = []
    lines.append("")
    lines.append("        ☯ 五运六气格局图 ☯")
    lines.append("")

    # 上半部分：司天 + 岁运
    lines.append(f"           ┌─────────────┐")
    lines.append(f"           │  司天: {si_tian:<8}│")
    lines.append(f"           │  （上半年） │")
    lines.append(f"           └─────────────┘")
    lines.append("")
    lines.append(f"        岁运: {sui_yun['name']}{sui_yun['status']}")
    lines.append(f"        年柱: {year_gz}  ({data['yunqi_year']}年)")
    lines.append("")

    # 六步推移圆环
    lines.append("        【六气步位推移】")
    lines.append("")

    qi_names = ['初之气', '二之气', '三之气', '四之气', '五之气', '终之气']
    for i, step in enumerate(data['ke_zhu_jia_lin']):
        marker = "▶" if step['step_number'] == current_step['step_number'] else " "
        start_jq = list(jieqi_dates.keys())[i] if i < 6 else ''
        end_jq = list(jieqi_dates.keys())[i + 1] if i + 1 < 7 else '大寒(终)'
        if i == 5:
            start_jq = '小雪'
            end_jq = '大寒(终)'
        date_range = f"{jieqi_dates.get(start_jq, '')} ~ {jieqi_dates.get(end_jq, '')}"
        tag = ""
        if step['keqi_is_sitian']:
            tag = "[司天]"
        elif step['keqi_is_zaiquan']:
            tag = "[在泉]"
        lines.append(
            f"{marker} {qi_names[i]}: 主{step['zhu_qi']} 客{step['ke_qi']} {tag}"
        )
        if step['step_number'] == current_step['step_number']:
            lines.append(
                f"        ↳ 当前步位 | {step['relation']} | {step['shun_ni']}"
            )
            lines.append(f"        ↳ 时间: {date_range}")
    lines.append("")

    # 下半部分：在泉
    lines.append(f"           ┌─────────────┐")
    lines.append(f"           │  在泉: {zai_quan:<8}│")
    lines.append(f"           │  （下半年） │")
    lines.append(f"           └─────────────┘")
    lines.append("")

    # 主运/客运
    lines.append("        【五运推移】")
    lines.append("")
    zhuyun_str = "        主运: "
    for s in data['zhu_yun']:
        zhuyun_str += f"{s['tai_shao']}{s['element']} "
    lines.append(zhuyun_str)
    keyun_str = "        客运: "
    for s in data['ke_yun']:
        keyun_str += f"{s['tai_shao']}{s['element']} "
    lines.append(keyun_str)
    lines.append("")

    # 图例
    lines.append("        图例: ▶ 当前步位  [司天]  [在泉]")
    lines.append("")

    return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("用法: python scripts/visualize_yunqi.py <YYYY-MM-DD>")
        print("示例: python scripts/visualize_yunqi.py 2026-06-29")
        sys.exit(1)

    date_str = sys.argv[1]
    data = get_result(date_str)
    output = visualize(data)
    sys.stdout.write(output)
    sys.stdout.write('\n')
    sys.stdout.flush()


if __name__ == '__main__':
    main()
