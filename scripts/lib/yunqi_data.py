# -*- coding: utf-8 -*-
"""
五运六气推算引擎 — 共享数据表
所有推算脚本均从此模块导入数据。
"""

import functools
import calendar
import json
import os
import sys
from datetime import datetime

# P2: 从单一 JSON 加载核心常量，减少 py/js 维护负担
_CONST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'yunqi_constants.json')
with open(_CONST_PATH, 'r', encoding='utf-8') as f:
    _C = json.load(f)

# 重新导出为模块常量（保持向后兼容的名称）

# ═══════════════════════════════════════════════════════════════
# 天干地支 (从 yunqi_constants.json 加载)
# ═══════════════════════════════════════════════════════════════

TIANGAN = _C['TIANGAN']
DIZHI = _C['DIZHI']
TIANGAN_YINYANG = _C['TIANGAN_YINYANG']
DIZHI_SHENGXIAO = _C['DIZHI_SHENGXIAO']
DIZHI_WUXING = _C['DIZHI_WUXING']

# ═══════════════════════════════════════════════════════════════
# 五行 (从 JSON 加载)
# ═══════════════════════════════════════════════════════════════

WUXING = _C['WUXING']
WUXING_SHENG = _C['WUXING_SHENG']
WUXING_KE = _C['WUXING_KE']

# ═══════════════════════════════════════════════════════════════
# 天干化五运 (从 JSON)
# ═══════════════════════════════════════════════════════════════

TIANGAN_HUAYUN = _C['TIANGAN_HUAYUN']
WUYUN_STEP = {'木': 1, '火': 2, '土': 3, '金': 4, '水': 5}

# ═══════════════════════════════════════════════════════════════
# 六气 (从 JSON 加载)
# ═══════════════════════════════════════════════════════════════

DIZHI_HUAQI_SITIAN = _C['DIZHI_HUAQI_SITIAN']
SITIAN_ZAIQUAN_PAIR = _C['SITIAN_ZAIQUAN_PAIR']
LIUQI_WUXING = _C['LIUQI_WUXING']
LIUQI_YINYANG = _C['LIUQI_YINYANG']
ZHUQI_STEPS = _C['ZHUQI_STEPS']
KEQI_CYCLE = _C['KEQI_CYCLE']

# 六步主气对应的节气区间
ZHUQI_JIEQI = {
    1: ('大寒', '春分'),    # 初之气
    2: ('春分', '小满'),    # 二之气
    3: ('小满', '大暑'),    # 三之气
    4: ('大暑', '秋分'),    # 四之气
    5: ('秋分', '小雪'),    # 五之气
    6: ('小雪', '大寒'),    # 终之气
}

# 二十四节气（按顺序，从 JSON）
JIEQI_24 = _C['JIEQI_24']

# ═══════════════════════════════════════════════════════════════
# 辅助函数
# ═══════════════════════════════════════════════════════════════

def _parse_date(date_str):
    """
    健壮的日期解析 (P1-3 优化)
    接受 "YYYY-MM-DD"，返回 (year, month, day) int 元组。
    抛出清晰的 ValueError。
    """
    if not isinstance(date_str, str):
        raise ValueError(f"日期必须是字符串，得到: {type(date_str)}")
    date_str = date_str.strip()
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.year, dt.month, dt.day
    except ValueError as e:
        raise ValueError(f"日期格式无效，应为 YYYY-MM-DD，当前: {date_str}") from e


def get_ganzhi(year):
    """公历年份 → (天干, 地支)"""
    tg_idx = (year - 4) % 10
    dz_idx = (year - 4) % 12
    return TIANGAN[tg_idx], DIZHI[dz_idx]

def get_sexagenary_index(year):
    """公历年份 → 六十甲子序号 (1-60)"""
    return (year - 4) % 60 + 1

def get_dayun(year):
    """公历年份 → (大运五行, 天干)"""
    tg, _ = get_ganzhi(year)
    return TIANGAN_HUAYUN[tg], tg

def is_taiguo(year):
    """判断大运太过/不及: 阳干太过, 阴干不及"""
    tg, _ = get_ganzhi(year)
    return TIANGAN_YINYANG[tg] == '阳'

def get_sitian(year):
    """公历年份 → 司天六气"""
    _, dz = get_ganzhi(year)
    return DIZHI_HUAQI_SITIAN[dz]

def get_zaiquan(year):
    """公历年份 → 在泉六气"""
    sitian = get_sitian(year)
    return SITIAN_ZAIQUAN_PAIR[sitian]

def get_keqi_six_steps(year):
    """
    公历年份 → 客气六步
    返回列表 [(step_num, keqi_name, is_sitian, is_zaiquan), ...]
    司天在三之气, 在泉在终之气
    """
    sitian = get_sitian(year)
    sitian_idx = KEQI_CYCLE.index(sitian)
    steps = []
    for step in range(1, 7):
        idx = (sitian_idx + step - 3) % 6
        qi = KEQI_CYCLE[idx]
        is_st = (qi == sitian)
        zaiquan = get_zaiquan(year)
        is_zq = (qi == zaiquan)
        steps.append((step, qi, is_st, is_zq))
    return steps

def get_zhuqi_six_steps():
    """返回主气六步 (固定)"""
    return [(i+1, qi, False, False) for i, qi in enumerate(ZHUQI_STEPS)]

def sheng(a, b):
    """五行 a 生 b ?"""
    return WUXING_SHENG.get(a) == b

def ke(a, b):
    """五行 a 克 b ?"""
    return WUXING_KE.get(a) == b

def kezhujialin_relation(keqi, zhuqi):
    """
    客主加临顺逆分析
    返回: (关系描述, 顺逆)
    """
    keqi_elem = LIUQI_WUXING[keqi]
    zhuqi_elem = LIUQI_WUXING[zhuqi]

    if keqi_elem == zhuqi_elem:
        return "客主同气", "相得（顺）"
    elif sheng(keqi_elem, zhuqi_elem):
        return "客气生主气", "相得（顺）"
    elif sheng(zhuqi_elem, keqi_elem):
        return "主气生客气", "不相得（逆）"
    elif ke(keqi_elem, zhuqi_elem):
        return "客气克主气", "不相得（逆）"
    elif ke(zhuqi_elem, keqi_elem):
        return "主气克客气", "不相得（逆）"
    return "未知关系", "未知"

def check_tianfu(year):
    """天符: 大运五行 == 司天五行"""
    dayun, _ = get_dayun(year)
    sitian = get_sitian(year)
    sitian_elem = LIUQI_WUXING[sitian]
    return dayun == sitian_elem

def check_suihui(year):
    """岁会: 大运五行 == 地支五行"""
    dayun, _ = get_dayun(year)
    _, dz = get_ganzhi(year)
    dz_elem = DIZHI_WUXING[dz]
    return dayun == dz_elem

def check_pingqi(year):
    """
    平气判断:
    - 太过之年，大运被司天所克 → 平气
    - 不及之年，大运得司天所生 → 平气
    """
    dayun, _ = get_dayun(year)
    sitian = get_sitian(year)
    sitian_elem = LIUQI_WUXING[sitian]
    taiguo = is_taiguo(year)

    if taiguo:
        # 太过被司天所克 → 平气
        if ke(sitian_elem, dayun):
            return True
    else:
        # 不及得司天所生 → 平气
        if sheng(sitian_elem, dayun):
            return True
    return False

# ═══════════════════════════════════════════════════════════════
# 主运/客运计算
# ═══════════════════════════════════════════════════════════════

def get_zhuyun_five_steps(year):
    """
    主运五步: 木→火→土→金→水 (固定)
    太少交替: 由大运所在步的太过/不及决定
    返回: [(step, element, tai_shao), ...]
    """
    dayun, _ = get_dayun(year)
    dayun_step = WUYUN_STEP[dayun]  # 1-5
    taiguo = is_taiguo(year)

    # 大运所在步: 太过→太, 不及→少
    dayun_is_tai = taiguo

    # 太少交替: 从大运步推算
    # step_diff = dayun_step - target_step (mod 2 for alternation)
    steps = []
    for i in range(5):
        step_num = i + 1
        elem = WUXING[i]  # 木火土金水
        # 交替: dayun_step是太或少, 其余交替
        diff = (step_num - dayun_step) % 2
        if diff == 0:
            is_tai = dayun_is_tai
        else:
            is_tai = not dayun_is_tai
        tai_shao = "太" if is_tai else "少"
        steps.append((step_num, elem, tai_shao))
    return steps

def get_keyun_five_steps(year):
    """
    客运五步: 以大运为初运, 按五行相生排列
    太少交替: 太过年从太开始, 不及年从少开始
    返回: [(step, element, tai_shao), ...]
    """
    dayun, _ = get_dayun(year)
    taiguo = is_taiguo(year)
    start_tai = "太" if taiguo else "少"

    # 五行相生序列, 从大运开始
    elem = dayun
    elements = []
    for _ in range(5):
        elements.append(elem)
        elem = WUXING_SHENG[elem]

    steps = []
    is_tai = taiguo
    for i, elem in enumerate(elements):
        tai_shao = "太" if is_tai else "少"
        steps.append((i + 1, elem, tai_shao))
        is_tai = not is_tai
    return steps


# ═══════════════════════════════════════════════════════════════
# Step 1 增强: 大寒定年 + 日期相关推算
# ═══════════════════════════════════════════════════════════════

# 岁运代码映射 (五行_太过/不及)
SUIYUN_CODE = {
    ('木', True): 'wood_excess',    ('木', False): 'wood_deficient',
    ('火', True): 'fire_excess',    ('火', False): 'fire_deficient',
    ('土', True): 'earth_excess',   ('土', False): 'earth_deficient',
    ('金', True): 'metal_excess',   ('金', False): 'metal_deficient',
    ('水', True): 'water_excess',   ('水', False): 'water_deficient',
}

# 岁运英文名
SUIYUN_EN = {
    '木': 'wood', '火': 'fire', '土': 'earth',
    '金': 'metal', '水': 'water',
}

# 六气拼音映射 (用于生成 RAG key)
LIUQI_PINYIN = {
    '厥阴风木': 'jueyin_fengmu',
    '少阴君火': 'shaoyin_junhuo',
    '太阴湿土': 'taiyin_shitu',
    '少阳相火': 'shaoyang_xianghuo',
    '阳明燥金': 'yangming_zaojin',
    '太阳寒水': 'taiyang_hanshui',
}

# 六步名称 (从 JSON，键转 int 保持兼容)
QI_STEP_NAMES = {int(k): v for k, v in _C['QI_STEP_NAMES'].items()}

# 节气英文名映射 (lunar-python 用)
_JIEQI_EN_MAP = {
    '大寒': 'DA_HAN', '春分': 'CHUN_FEN', '小满': 'XIAO_MAN',
    '大暑': 'DA_SHU', '秋分': 'QIU_FEN', '小雪': 'XIAO_XUE',
}

# 退化方案: 无 lunar-python 时的近似日期
_JIEQI_FALLBACK = {
    '大寒': (1, 20), '春分': (3, 20), '小满': (5, 21),
    '大暑': (7, 23), '秋分': (9, 23), '小雪': (11, 22),
}

# 六步对应的节气边界 (起止节气名)
_QI_STEP_JIEQI = [
    ('大寒', '春分'),   # 初之气
    ('春分', '小满'),   # 二之气
    ('小满', '大暑'),   # 三之气
    ('大暑', '秋分'),   # 四之气
    ('秋分', '小雪'),   # 五之气
    ('小雪', '大寒'),   # 终之气
]


def _get_solar_class():
    """尝试导入 lunar-python 的 Solar 类"""
    try:
        from lunar_python import Solar
        return Solar
    except ImportError:
        # UX: 只警告一次
        if not getattr(_get_solar_class, '_warned', False):
            print("⚠️  未检测到 lunar-python，使用近似节气日期（精度降低）。建议: pip install lunar-python", file=sys.stderr)
            _get_solar_class._warned = True
        return None


@functools.lru_cache(maxsize=256)
def get_jieqi_date(year, jieqi_name):
    """
    获取指定公历年份某节气的日期
    返回: (year, month, day) 元组

    优化点（P0）：
    - 使用 lru_cache 显著减少重复 lunar-python 调用（calculate_yunqi_api 频繁调用）
    - 修复兜底遍历：原 range(1,29) 会漏掉 29/30/31 日
    """
    Solar = _get_solar_class()

    if Solar is None:
        # 退化方案: 使用近似日期
        m, d = _JIEQI_FALLBACK.get(jieqi_name, (1, 20))
        return (year, m, d)

    # 大寒在年初: 从前一年7月的 Lunar 表获取
    # (因为 lunar year 从立春开始, 大寒在 Jan 属于上一个 lunar year)
    if jieqi_name == '大寒':
        solar = Solar.fromYmd(year - 1, 7, 1)
    else:
        solar = Solar.fromYmd(year, 7, 1)

    lunar = solar.getLunar()
    jq_table = lunar.getJieQiTable()
    jq_en = _JIEQI_EN_MAP.get(jieqi_name)

    if jq_en and jq_en in jq_table:
        val = jq_table[jq_en]
        # JieQiTable 值可能是 Solar 对象或字符串
        if isinstance(val, str):
            parts = val.split('-')
            return (int(parts[0]), int(parts[1]), int(parts[2]))
        else:
            # Solar 对象
            return (val.getYear(), val.getMonth(), val.getDay())

    # 兜底: 遍历法（修复：使用 calendar 获取正确月末，或保守 range(1,32)）
    for month in range(1, 13):
        last_day = calendar.monthrange(year, month)[1]
        for day in range(1, last_day + 1):
            try:
                s = Solar.fromYmd(year, month, day)
                l = s.getLunar()
                jq = l.getJieQi()
                if jq and jieqi_name in jq:
                    return (year, month, day)
            except Exception:
                pass

    # 最终兜底
    m, d = _JIEQI_FALLBACK.get(jieqi_name, (1, 20))
    return (year, m, d)


def get_yunqi_year(date_str):
    """
    根据日期字符串确定运气年份 (以大寒为年界)
    
    运气年从大寒开始，到下一个大寒结束。
    例如: 2026-01-15 在 2025年大寒和2026年大寒之间 → 运气年 = 2025 (乙巳)
          2026-06-27 在 2026年大寒和2027年大寒之间 → 运气年 = 2026 (丙午)
    
    参数: date_str - "YYYY-MM-DD" 格式
    返回: 运气年份 (int)
    """
    solar_year, solar_month, solar_day = _parse_date(date_str)
    
    # 获取当年的大寒日期
    dahan_y, dahan_m, dahan_d = get_jieqi_date(solar_year, '大寒')
    
    # 判断日期是否在当年大寒之前
    if (solar_month < dahan_m) or (solar_month == dahan_m and solar_day < dahan_d):
        # 在当年大寒之前 → 运气年 = 前一年
        return solar_year - 1
    else:
        # 在当年大寒或之后 → 运气年 = 当年
        return solar_year


def get_current_qi_step(date_str):
    """
    根据日期确定当前所处的客气步位 (1-6)
    
    六步边界:
      初之气: 大寒 → 春分
      二之气: 春分 → 小满
      三之气: 小满 → 大暑
      四之气: 大暑 → 秋分
      五之气: 秋分 → 小雪
      终之气: 小雪 → 大寒(次年)
    
    参数: date_str - "YYYY-MM-DD" 格式
    返回: (step_number, step_name, start_jieqi, end_jieqi)
    """
    yq_year = get_yunqi_year(date_str)
    date_y, date_m, date_d = _parse_date(date_str)
    
    # 获取六步的节气边界日期
    # 初之气~五之气的起始节气在运气年当年
    # 终之气的结束节气(大寒)在次年
    jieqi_dates = {}
    for jieqi_name in ['大寒', '春分', '小满', '大暑', '秋分', '小雪']:
        jieqi_dates[jieqi_name] = get_jieqi_date(yq_year, jieqi_name)
    
    # 大寒(终之气结束)在次年
    next_dahan = get_jieqi_date(yq_year + 1, '大寒')
    
    date_tuple = (date_y, date_m, date_d)
    
    # 逐步判断
    step_boundaries = [
        (1, jieqi_dates['大寒'], jieqi_dates['春分']),
        (2, jieqi_dates['春分'], jieqi_dates['小满']),
        (3, jieqi_dates['小满'], jieqi_dates['大暑']),
        (4, jieqi_dates['大暑'], jieqi_dates['秋分']),
        (5, jieqi_dates['秋分'], jieqi_dates['小雪']),
        (6, jieqi_dates['小雪'], next_dahan),
    ]
    
    for step_num, start, end in step_boundaries:
        # 将日期转换为可比较的 (year, month, day) 元组
        # 大寒可能在运气年的1月(即 date_y == yq_year)
        # 也可能在次年1月(即 date_y == yq_year + 1)
        if date_tuple >= start and date_tuple < end:
            return (step_num, QI_STEP_NAMES[step_num], start, end)
    
    # 如果没匹配到（边界情况），返回初之气
    return (1, QI_STEP_NAMES[1], jieqi_dates['大寒'], jieqi_dates['春分'])


def get_day_ganzhi(date_str):
    """
    获取指定日期的日干支
    
    参数: date_str - "YYYY-MM-DD" 格式
    返回: 日干支字符串 (如 "壬申") 或 None
    """
    Solar = _get_solar_class()
    if Solar is None:
        return None
    
    y, m, d = _parse_date(date_str)
    solar = Solar.fromYmd(y, m, d)
    lunar = solar.getLunar()
    return lunar.getDayInGanZhi()


def get_suiyun_code(year):
    """获取岁运代码 (如 'water_excess')"""
    dayun, _ = get_dayun(year)
    taiguo = is_taiguo(year)
    return SUIYUN_CODE.get((dayun, taiguo), 'unknown')


def get_kezhujialin_detail(year, step_num):
    """
    获取指定步位的客主加临详细分析
    
    返回: {
        'step_number', 'step_name', 'zhu_qi', 'ke_qi',
        'relation', 'shun_ni', 'keqi_is_sitian', 'keqi_is_zaiquan'
    }
    """
    zhuqi_steps = get_zhuqi_six_steps()
    keqi_steps = get_keqi_six_steps(year)
    
    zhuqi = zhuqi_steps[step_num - 1][1]
    keqi_info = keqi_steps[step_num - 1]
    keqi = keqi_info[1]
    is_sitian = keqi_info[2]
    is_zaiquan = keqi_info[3]
    
    relation, shun_ni = kezhujialin_relation(keqi, zhuqi)
    
    return {
        'step_number': step_num,
        'step_name': QI_STEP_NAMES[step_num],
        'zhu_qi': zhuqi,
        'ke_qi': keqi,
        'relation': relation,
        'shun_ni': shun_ni,
        'keqi_is_sitian': is_sitian,
        'keqi_is_zaiquan': is_zaiquan,
    }


def generate_summary(result):
    """
    根据 calculate_yunqi_api 返回的结果生成一段自然语言摘要。
    摘要包含：年干支、岁运、司天在泉、当前步位、客主关系、近期关注重点。
    """
    date_str = result['date']
    year_gz = result['year_gz']
    yunqi_year = result['yunqi_year']
    sui_yun = result['sui_yun']
    si_tian = result['si_tian']
    zai_quan = result['zai_quan']
    step = result['current_step']

    # 计算客主加临顺逆统计
    xiangde = sum(1 for s in result['ke_zhu_jia_lin'] if s['shun_ni'].startswith('相得'))
    buxiangde = 6 - xiangde

    summary = (
        f"{date_str} 属于{yunqi_year}年（{year_gz}）。"
        f"全年岁运为{sui_yun['name']}{sui_yun['status']}，"
        f"上半年{si_tian}司天，下半年{zai_quan}在泉。"
        f"当前处于{step['name']}，主气为{step['zhu_qi']}，客气为{step['ke_qi']}，"
        f"二者{step['relation']}，{step['shun_ni']}。"
    )

    # 添加近期关注重点
    focus_points = []
    if step['keqi_is_sitian']:
        focus_points.append(f"司天{si_tian}之气当令，上半年气候特征明显")
    if step['keqi_is_zaiquan']:
        focus_points.append(f"在泉{zai_quan}之气当令，下半年气候特征明显")

    # 根据客主关系给出提示
    relation = step['relation']
    if '同气' in relation:
        focus_points.append(f"{step['zhu_qi']}同气偏盛，注意相关脏腑调养")
    elif '客气克主气' in relation:
        focus_points.append(f"客气克制主气，气候不调，注意防病")
    elif '主气生客气' in relation:
        focus_points.append(f"主气生客气，气机上逆，宜平和调理")

    # 岁运与司天综合提示
    sui_yun_element = sui_yun['element']
    sitian_element = LIUQI_WUXING.get(si_tian, '')
    if sui_yun_element and sitian_element:
        if WUXING_KE.get(sitian_element) == sui_yun_element:
            focus_points.append(f"司天{sitian_element}克岁运{sui_yun_element}，天刑之年，气候易有乖戾")
        elif WUXING_KE.get(sui_yun_element) == sitian_element:
            focus_points.append(f"岁运{sui_yun_element}克司天{sitian_element}，运盛于天，气候偏甚")
        elif sitian_element == sui_yun_element:
            focus_points.append(f"岁运与司天同气，{sui_yun_element}气偏盛")

    if focus_points:
        summary += " 近期关注：" + "；".join(focus_points) + "。"

    summary += f" 全年六步客主加临：{xiangde}步相得、{buxiangde}步不相得。"

    # UX P0-5 + P1-3: 下一步 + 思想伙伴引导
    summary += "\n\n下一步建议：\n"
    summary += "  • 聚焦当前步位：python scripts/calculate_yunqi_api.py " + result.get('date', 'today') + " --focus current-step\n"
    summary += "  • 生成学生报告：python scripts/calculate_yunqi_api.py " + result.get('date', 'today') + " --report-type student\n"
    summary += "  • 个人体质分析：python scripts/personal_yunqi_profile.py <出生日期> <城市>\n"
    summary += "\n思想伙伴问题：你对这个‘天人合一’的体现有什么自己的理解？想继续探讨吗？\n"

    return summary


def generate_current_step_focus(result):
    """
    聚焦当前步位，输出 concise 的近期关注点。
    """
    step = result['current_step']
    sui_yun = result['sui_yun']
    si_tian = result['si_tian']
    zai_quan = result['zai_quan']

    focus_points = []
    if step['keqi_is_sitian']:
        focus_points.append(f"司天{si_tian}当令")
    if step['keqi_is_zaiquan']:
        focus_points.append(f"在泉{zai_quan}当令")

    relation = step['relation']
    if '同气' in relation:
        focus_points.append(f"{step['zhu_qi']}同气偏盛")
    elif '客气克主气' in relation:
        focus_points.append("客气克主，气候不调")
    elif '主气生客气' in relation:
        focus_points.append("主气生客，气机上逆")
    elif '客气生主气' in relation:
        focus_points.append("客气生主，气候平和")

    focus_str = "；".join(focus_points) if focus_points else "无明显偏颇"

    return (
        f"当前步位：{step['name']}\n"
        f"时间范围：{step['date_range']['start']} ~ {step['date_range']['end']}\n"
        f"主气：{step['zhu_qi']} | 客气：{step['ke_qi']}\n"
        f"关系：{step['relation']} | {step['shun_ni']}\n"
        f"岁运背景：{sui_yun['name']}{sui_yun['status']}，{si_tian}司天/{zai_quan}在泉\n"
        f"近期关注：{focus_str}\n"
    )


if __name__ == '__main__':
    # 自测
    for y in [2024, 2025, 2026]:
        tg, dz = get_ganzhi(y)
        dayun, _ = get_dayun(y)
        sitian = get_sitian(y)
        zaiquan = get_zaiquan(y)
        print(f"{y}年 {tg}{dz} | 大运:{dayun}{'太过' if is_taiguo(y) else '不及'} | "
              f"司天:{sitian} | 在泉:{zaiquan}")
