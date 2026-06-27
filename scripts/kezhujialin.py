#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客主加临分析脚本
用法: python kezhujialin.py <年份>
输出: 六步客主加临顺逆分析

客主加临规则:
  - 客气与主气同气 → 相得（顺）
  - 客气生主气 → 相得（顺）
  - 客气克主气 → 不相得（逆）
  - 主气生客气 → 不相得（逆，下生上）
  - 主气克客气 → 不相得（逆，主克客）
"""
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib'))
from yunqi_data import (
    get_keqi_six_steps, get_zhuqi_six_steps,
    ZHUQI_JIEQI, LIUQI_WUXING, kezhujialin_relation,
    get_sitian, get_zaiquan, get_ganzhi,
)


def calc(year):
    tg, dz = get_ganzhi(year)
    sitian = get_sitian(year)
    zaiquan = get_zaiquan(year)
    keqi = get_keqi_six_steps(year)
    zhuqi = get_zhuqi_six_steps()

    step_names = ['初之气', '二之气', '三之气', '四之气', '五之气', '终之气']

    steps = []
    for i in range(6):
        kq_name = keqi[i][1]
        zq_name = zhuqi[i][1]
        jq = ZHUQI_JIEQI[i + 1]
        relation, shun_ni = kezhujialin_relation(kq_name, zq_name)
        steps.append({
            'step': step_names[i],
            '节气': f'{jq[0]}~{jq[1]}',
            '主气': zq_name,
            '客气': kq_name,
            '主气五行': LIUQI_WUXING[zq_name],
            '客气五行': LIUQI_WUXING[kq_name],
            '关系': relation,
            '顺逆': shun_ni,
            '备注': '司天' if keqi[i][2] else ('在泉' if keqi[i][3] else ''),
        })

    # 统计（注意: "不相得"包含"相得"子串，须用 startswith 精确匹配）
    xiangde_count = sum(1 for s in steps if s['顺逆'].startswith('相得'))
    bxiangde_count = 6 - xiangde_count

    return {
        '年份': year,
        '干支': f'{tg}{dz}',
        '司天': sitian,
        '在泉': zaiquan,
        '六步': steps,
        '相得步数': xiangde_count,
        '不相得步数': bxiangde_count,
        '总体': '和平之年' if xiangde_count >= 4 else '气候异常之年',
    }


def format_text(result):
    lines = [
        f"年份: {result['年份']} ({result['干支']}年)",
        f"司天: {result['司天']} | 在泉: {result['在泉']}",
        "",
        f"{'步':<6} {'节气':<10} {'主气':<8} {'客气':<8} {'关系':<12} {'顺逆':<12} {'备注'}",
        f"{'─'*70}",
    ]
    for s in result['六步']:
        lines.append(
            f"{s['step']:<6} {s['节气']:<10} {s['主气']:<8} {s['客气']:<8} "
            f"{s['关系']:<12} {s['顺逆']:<12} {s['备注']}"
        )
    lines.append('')
    lines.append(f"相得: {result['相得步数']}步 | 不相得: {result['不相得步数']}步")
    lines.append(f"总体判断: {result['总体']}")
    return '\n'.join(lines)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python kezhujialin.py <年份>")
        sys.exit(1)
    year = int(sys.argv[1])
    result = calc(year)

    if '--json' in sys.argv:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_text(result))
