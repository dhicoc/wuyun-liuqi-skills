#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大运推算脚本
用法: python dayun_calc.py <年份>
输出: 大运五行、太过/不及、平气判断、天符/岁会/太乙天符
"""
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib'))
from yunqi_data import (
    get_dayun, is_taiguo, get_sitian, get_zaiquan,
    TIANGAN_HUAYUN, TIANGAN_YINYANG, LIUQI_WUXING, DIZHI_WUXING,
    get_ganzhi, check_tianfu, check_suihui, check_pingqi,
    WUXING_SHENG, WUXING_KE,
)


def calc(year):
    dayun, tg = get_dayun(year)
    taiguo = is_taiguo(year)
    sitian = get_sitian(year)
    zaiquan = get_zaiquan(year)
    sitian_elem = LIUQI_WUXING[sitian]
    _, dz = get_ganzhi(year)
    dz_elem = DIZHI_WUXING[dz]

    # 平气判断
    pingqi = check_pingqi(year)

    # 天符/岁会/太乙天符
    tianfu = check_tianfu(year)
    suihui = check_suihui(year)
    taiyi_tianfu = tianfu and suihui

    # 运气关系
    if taiguo:
        if pingqi:
            yun_status = "平气（太过被司天所抑）"
        elif sitian_elem == dayun:
            yun_status = "天符（运同司天）"
        elif WUXING_KE.get(sitian_elem) == dayun:
            yun_status = "太过被抑（司天克运）"
        elif WUXING_SHENG.get(dayun) == sitian_elem:
            yun_status = "运生司天（运太过而生司天）"
        else:
            yun_status = "太过"
    else:
        if pingqi:
            yun_status = "平气（不及得司天所生）"
        elif sitian_elem == dayun:
            yun_status = "天符（运同司天）"
        elif WUXING_SHENG.get(sitian_elem) == dayun:
            yun_status = "不及得助（司天生运）"
        elif WUXING_KE.get(dayun) == sitian_elem:
            yun_status = "运克司天（不及而克司天）"
        else:
            yun_status = "不及"

    # 顺化/逆化判断
    if WUXING_SHENG.get(dayun) == sitian_elem:
        yun_qi_relation = "运生气（顺化）"
    elif WUXING_SHENG.get(sitian_elem) == dayun:
        yun_qi_relation = "气生运（天符类）"
    elif WUXING_KE.get(dayun) == sitian_elem:
        yun_qi_relation = "运克气（不和）"
    elif WUXING_KE.get(sitian_elem) == dayun:
        yun_qi_relation = "气克运（天刑）"
    elif dayun == sitian_elem:
        yun_qi_relation = "运气同化（天符）"
    else:
        yun_qi_relation = "运气关系一般"

    result = {
        '年份': year,
        '天干': tg,
        '天干阴阳': TIANGAN_YINYANG[tg],
        '大运': f"{dayun}运",
        '太过不及': '太过' if taiguo else '不及',
        '平气': pingqi,
        '运气状态': yun_status,
        '司天': sitian,
        '司天五行': sitian_elem,
        '在泉': zaiquan,
        '在泉五行': LIUQI_WUXING[zaiquan],
        '地支五行': dz_elem,
        '天符': tianfu,
        '岁会': suihui,
        '太乙天符': taiyi_tianfu,
        '运气关系': yun_qi_relation,
    }
    return result


def format_text(result):
    lines = [
        f"年份: {result['年份']} ({result['天干']}{result.get('地支', '')})",
        f"天干: {result['天干']} ({result['天干阴阳']})",
        f"大运: {result['大运']}",
        f"太过/不及: {result['太过不及']}",
    ]
    if result['平气']:
        lines.append(f"平气: 是 — {result['运气状态']}")
    else:
        lines.append(f"平气: 否")
    lines.append(f"运气状态: {result['运气状态']}")
    lines.append(f"天符: {'是' if result['天符'] else '否'}")
    lines.append(f"岁会: {'是' if result['岁会'] else '否'}")
    lines.append(f"太乙天符: {'是' if result['太乙天符'] else '否'}")
    lines.append(f"运气关系: {result['运气关系']}")
    return '\n'.join(lines)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python dayun_calc.py <年份>")
        sys.exit(1)
    year = int(sys.argv[1])
    result = calc(year)

    if '--json' in sys.argv:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_text(result))
