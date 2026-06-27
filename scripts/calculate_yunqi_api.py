#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五运六气统一计算接口 (Step 1: 强规则底层计算工具)

核心函数: calculate_yunqi_api(date_str)
- 以大寒为年界，精确判断运气年份
- 返回标准化 JSON，可供 LLM Agent 直接解析
- 日干支由 lunar-python 精确计算

用法:
  python calculate_yunqi_api.py 2026-06-27
  python calculate_yunqi_api.py 2026-06-27 --json
  python calculate_yunqi_api.py 2026-01-15 --json  # 测试大寒边界

依赖: lunar-python (pip install lunar-python)
"""
import sys
import os
import json

# 添加 lib 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib'))
from yunqi_data import (
    TIANGAN, DIZHI, DIZHI_SHENGXIAO, TIANGAN_HUAYUN, TIANGAN_YINYANG,
    DIZHI_HUAQI_SITIAN, SITIAN_ZAIQUAN_PAIR, LIUQI_WUXING, LIUQI_PINYIN,
    WUXING, WUYUN_STEP, ZHUQI_STEPS, KEQI_CYCLE,
    SUIYUN_CODE, SUIYUN_EN, QI_STEP_NAMES,
    get_ganzhi, get_sexagenary_index, get_dayun, is_taiguo,
    get_sitian, get_zaiquan, get_keqi_six_steps, get_zhuqi_six_steps,
    get_zhuyun_five_steps, get_keyun_five_steps,
    kezhujialin_relation, check_tianfu, check_suihui, check_pingqi,
    get_yunqi_year, get_current_qi_step, get_day_ganzhi,
    get_suiyun_code, get_kezhujialin_detail, get_jieqi_date,
)


def calculate_yunqi_api(date_str):
    """
    五运六气统一计算接口
    
    参数: date_str - "YYYY-MM-DD" 格式日期字符串
    返回: 标准化 JSON 字典，包含:
      - year_gz: 年干支
      - day_gz: 日干支
      - sui_yun: 岁运 (name, status, code, tiangan)
      - si_tian: 司天
      - zai_quan: 在泉
      - current_step: 当前步位 (step_number, name, zhu_qi, ke_qi, relation)
      - tong_hua: 运气同化 (tianfu, suihui, taiyi_tianfu, pingqi)
      - zhu_yun: 主运五步
      - ke_yun: 客运五步
      - ke_qi_six_steps: 客气六步
      - ke_zhu_jia_lin: 客主加临六步分析
      - jieqi_dates: 六步节气边界日期
    """
    # 1. 确定运气年份 (大寒定年)
    yq_year = get_yunqi_year(date_str)
    
    # 2. 基本干支推算
    tg, dz = get_ganzhi(yq_year)
    idx = get_sexagenary_index(yq_year)
    sx = DIZHI_SHENGXIAO[dz]
    
    # 3. 日干支
    day_gz = get_day_ganzhi(date_str)
    
    # 4. 岁运
    dayun, dayun_tg = get_dayun(yq_year)
    taiguo = is_taiguo(yq_year)
    suiyun_code = get_suiyun_code(yq_year)
    
    # 5. 司天在泉
    sitian = get_sitian(yq_year)
    zaiquan = get_zaiquan(yq_year)
    
    # 6. 当前步位
    step_num, step_name, step_start, step_end = get_current_qi_step(date_str)
    step_detail = get_kezhujialin_detail(yq_year, step_num)
    
    # 7. 运气同化
    tianfu = check_tianfu(yq_year)
    suihui = check_suihui(yq_year)
    taiyi_tianfu = tianfu and suihui
    pingqi = check_pingqi(yq_year)
    
    # 8. 主运五步
    zhuyun_steps = get_zhuyun_five_steps(yq_year)
    zhu_yun = [
        {'step': s, 'element': e, 'tai_shao': ts}
        for s, e, ts in zhuyun_steps
    ]
    
    # 9. 客运五步
    keyun_steps = get_keyun_five_steps(yq_year)
    ke_yun = [
        {'step': s, 'element': e, 'tai_shao': ts}
        for s, e, ts in keyun_steps
    ]
    
    # 10. 客气六步
    keqi_steps = get_keqi_six_steps(yq_year)
    ke_qi_six = [
        {
            'step': s,
            'ke_qi': qi,
            'is_sitian': is_st,
            'is_zaiquan': is_zq,
        }
        for s, qi, is_st, is_zq in keqi_steps
    ]
    
    # 11. 客主加临六步
    ke_zhu_jia_lin = []
    for s in range(1, 7):
        detail = get_kezhujialin_detail(yq_year, s)
        ke_zhu_jia_lin.append(detail)
    
    # 12. 节气日期
    jieqi_dates = {}
    for jq_name in ['大寒', '春分', '小满', '大暑', '秋分', '小雪']:
        y, m, d = get_jieqi_date(yq_year, jq_name)
        jieqi_dates[jq_name] = f"{y}-{m:02d}-{d:02d}"
    next_y, next_m, next_d = get_jieqi_date(yq_year + 1, '大寒')
    jieqi_dates['大寒(终)'] = f"{next_y}-{next_m:02d}-{next_d:02d}"
    
    # 六气缩写 pinyin（无 xianghuo/junhuo/fengmu 等后缀，与 asset3 客主加临 key 格式匹配）
    liuqi_pinyin_short = {k: v.split('_')[0] for k, v in LIUQI_PINYIN.items()}
    
    # 构建标准化输出
    result = {
        'date': date_str,
        'yunqi_year': yq_year,
        'year_gz': f'{tg}{dz}',
        'year_gan': tg,
        'year_zhi': dz,
        'sexagenary_index': idx,
        'shengxiao': sx,
        'day_gz': day_gz,
        'sui_yun': {
            'name': f'{dayun}运',
            'element': dayun,
            'status': '太过' if taiguo else '不及',
            'code': suiyun_code,
            'tiangan': dayun_tg,
        },
        'si_tian': sitian,
        'zai_quan': zaiquan,
        'current_step': {
            'step_number': step_num,
            'name': step_name,
            'zhu_qi': step_detail['zhu_qi'],
            'ke_qi': step_detail['ke_qi'],
            'relation': step_detail['relation'],
            'shun_ni': step_detail['shun_ni'],
            'keqi_is_sitian': step_detail['keqi_is_sitian'],
            'keqi_is_zaiquan': step_detail['keqi_is_zaiquan'],
            'date_range': {
                'start': f"{step_start[0]}-{step_start[1]:02d}-{step_start[2]:02d}",
                'end': f"{step_end[0]}-{step_end[1]:02d}-{step_end[2]:02d}",
            },
        },
        'tong_hua': {
            'tianfu': tianfu,
            'suihui': suihui,
            'taiyi_tianfu': taiyi_tianfu,
            'pingqi': pingqi,
        },
        'zhu_yun': zhu_yun,
        'ke_yun': ke_yun,
        'ke_qi_six_steps': ke_qi_six,
        'ke_zhu_jia_lin': ke_zhu_jia_lin,
        'jieqi_dates': jieqi_dates,
        # RAG 检索键
        'rag_keys': {
            'suiyun': suiyun_code,
            'sitian': f'{LIUQI_PINYIN[sitian]}_sitian',
            'zaiquan': f'{LIUQI_PINYIN[zaiquan]}_zaiquan',
            'current_step': f'zhu_{liuqi_pinyin_short[step_detail["zhu_qi"]]}_ke_{liuqi_pinyin_short[step_detail["ke_qi"]]}',
        },
    }
    
    return result


def format_text(result):
    """格式化为可读文本"""
    lines = [
        f"日期: {result['date']}",
        f"运气年: {result['yunqi_year']}年 ({result['year_gz']})",
        f"六十甲子: 第{result['sexagenary_index']}甲子 | 生肖: {result['shengxiao']}",
        f"日干支: {result['day_gz'] or '未安装lunar-python，无法计算'}",
        "",
        f"【岁运】{result['sui_yun']['name']}{'太过' if result['sui_yun']['status']=='太过' else '不及'} (code: {result['sui_yun']['code']})",
        f"【司天】{result['si_tian']}",
        f"【在泉】{result['zai_quan']}",
        "",
        f"【当前步位】{result['current_step']['name']}",
        f"  主气: {result['current_step']['zhu_qi']}",
        f"  客气: {result['current_step']['ke_qi']}",
        f"  关系: {result['current_step']['relation']} → {result['current_step']['shun_ni']}",
    ]
    
    th = result['tong_hua']
    th_parts = []
    if th['tianfu']:
        th_parts.append('天符')
    if th['suihui']:
        th_parts.append('岁会')
    if th['taiyi_tianfu']:
        th_parts.append('太乙天符')
    if th['pingqi']:
        th_parts.append('平气')
    if th_parts:
        lines.append(f"【运气同化】{'、'.join(th_parts)}")
    else:
        lines.append("【运气同化】无特殊同化")
    
    lines.append("")
    lines.append("【主运五步】")
    for s in result['zhu_yun']:
        lines.append(f"  {s['step']}. {s['tai_shao']}{s['element']}运")
    
    lines.append("【客运五步】")
    for s in result['ke_yun']:
        lines.append(f"  {s['step']}. {s['tai_shao']}{s['element']}运")
    
    lines.append("")
    lines.append("【客气六步】")
    for s in result['ke_qi_six_steps']:
        tag = ''
        if s['is_sitian']:
            tag = ' ← 司天'
        elif s['is_zaiquan']:
            tag = ' ← 在泉'
        lines.append(f"  {s['step']}. {s['ke_qi']}{tag}")
    
    lines.append("")
    lines.append("【客主加临】")
    xiangde = 0
    buxiangde = 0
    for s in result['ke_zhu_jia_lin']:
        if s['shun_ni'].startswith('相得'):
            xiangde += 1
        else:
            buxiangde += 1
        tag = ''
        if s['keqi_is_sitian']:
            tag = ' (司天)'
        elif s['keqi_is_zaiquan']:
            tag = ' (在泉)'
        lines.append(f"  {s['step_number']}. 主{s['zhu_qi']} 客{s['ke_qi']}{tag} → {s['relation']} {s['shun_ni']}")
    lines.append(f"  相得: {xiangde}步 | 不相得: {buxiangde}步")
    
    lines.append("")
    lines.append("【RAG检索键】")
    for k, v in result['rag_keys'].items():
        lines.append(f"  {k}: {v}")
    
    return '\n'.join(lines)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python calculate_yunqi_api.py <YYYY-MM-DD> [--json]")
        print("示例: python calculate_yunqi_api.py 2026-06-27 --json")
        sys.exit(1)
    
    date_str = sys.argv[1]
    result = calculate_yunqi_api(date_str)
    
    if '--json' in sys.argv:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_text(result))
