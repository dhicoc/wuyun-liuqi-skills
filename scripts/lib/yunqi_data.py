# -*- coding: utf-8 -*-
"""
五运六气推算引擎 — 共享数据表
所有推算脚本均从此模块导入数据。
"""

# ═══════════════════════════════════════════════════════════════
# 天干地支
# ═══════════════════════════════════════════════════════════════

TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 天干阴阳: 阳干=太过, 阴干=不及
TIANGAN_YINYANG = {
    '甲': '阳', '丙': '阳', '戊': '阳', '庚': '阳', '壬': '阳',
    '乙': '阴', '丁': '阴', '己': '阴', '辛': '阴', '癸': '阴',
}

# 地支生肖
DIZHI_SHENGXIAO = {
    '子': '鼠', '丑': '牛', '寅': '虎', '卯': '兔',
    '辰': '龙', '巳': '蛇', '午': '马', '未': '羊',
    '申': '猴', '酉': '鸡', '戌': '狗', '亥': '猪',
}

# 地支五行（用于岁会判断）
DIZHI_WUXING = {
    '子': '水', '丑': '土', '寅': '木', '卯': '木',
    '辰': '土', '巳': '火', '午': '火', '未': '土',
    '申': '金', '酉': '金', '戌': '土', '亥': '水',
}

# ═══════════════════════════════════════════════════════════════
# 五行
# ═══════════════════════════════════════════════════════════════

WUXING = ['木', '火', '土', '金', '水']

# 五行相生: A 生 B
WUXING_SHENG = {
    '木': '火', '火': '土', '土': '金', '金': '水', '水': '木',
}

# 五行相克: A 克 B
WUXING_KE = {
    '木': '土', '土': '水', '水': '火', '火': '金', '金': '木',
}

# ═══════════════════════════════════════════════════════════════
# 天干化五运
# ═══════════════════════════════════════════════════════════════

TIANGAN_HUAYUN = {
    '甲': '土', '己': '土',    # 甲己化土
    '乙': '金', '庚': '金',    # 乙庚化金
    '丙': '水', '辛': '水',    # 丙辛化水
    '丁': '木', '壬': '木',    # 丁壬化木
    '戊': '火', '癸': '火',    # 戊癸化火
}

# 五运对应的主运步序位置 (1-5)
WUYUN_STEP = {
    '木': 1, '火': 2, '土': 3, '金': 4, '水': 5,
}

# ═══════════════════════════════════════════════════════════════
# 六气
# ═══════════════════════════════════════════════════════════════

# 地支化六气（司天）
DIZHI_HUAQI_SITIAN = {
    '子': '少阴君火', '午': '少阴君火',   # 子午少阴君火
    '丑': '太阴湿土', '未': '太阴湿土',   # 丑未太阴湿土
    '寅': '少阳相火', '申': '少阳相火',   # 寅申少阳相火
    '卯': '阳明燥金', '酉': '阳明燥金',   # 卯酉阳明燥金
    '辰': '太阳寒水', '戌': '太阳寒水',   # 辰戌太阳寒水
    '巳': '厥阴风木', '亥': '厥阴风木',   # 巳亥厥阴风木
}

# 司天-在泉配对（一阴对一阳，二阴对二阳，三阴对三阳）
SITIAN_ZAIQUAN_PAIR = {
    '厥阴风木': '少阳相火',   # 一阴 ↔ 一阳
    '少阴君火': '阳明燥金',   # 二阴 ↔ 二阳
    '太阴湿土': '太阳寒水',   # 三阴 ↔ 三阳
    '少阳相火': '厥阴风木',
    '阳明燥金': '少阴君火',
    '太阳寒水': '太阴湿土',
}

# 六气对应的五行
LIUQI_WUXING = {
    '厥阴风木': '木',
    '少阴君火': '火',
    '少阳相火': '火',
    '太阴湿土': '土',
    '阳明燥金': '金',
    '太阳寒水': '水',
}

# 六气阴阳归类
LIUQI_YINYANG = {
    '厥阴风木': '一阴',
    '少阴君火': '二阴',
    '太阴湿土': '三阴',
    '少阳相火': '一阳',
    '阳明燥金': '二阳',
    '太阳寒水': '三阳',
}

# 主气六步（固定，每年相同，按季节顺序）
ZHUQI_STEPS = [
    '厥阴风木',   # 初之气
    '少阴君火',   # 二之气
    '少阳相火',   # 三之气
    '太阴湿土',   # 四之气
    '阳明燥金',   # 五之气
    '太阳寒水',   # 终之气
]

# 客气循环序列（按阴阳推移：一阴→二阴→三阴→一阳→二阳→三阳）
# 此顺序中，相差3位的六气互为司天-在泉对
KEQI_CYCLE = [
    '厥阴风木',   # 一阴
    '少阴君火',   # 二阴
    '太阴湿土',   # 三阴
    '少阳相火',   # 一阳
    '阳明燥金',   # 二阳
    '太阳寒水',   # 三阳
]

# 六步主气对应的节气区间
ZHUQI_JIEQI = {
    1: ('大寒', '春分'),    # 初之气
    2: ('春分', '小满'),    # 二之气
    3: ('小满', '大暑'),    # 三之气
    4: ('大暑', '秋分'),    # 四之气
    5: ('秋分', '小雪'),    # 五之气
    6: ('小雪', '大寒'),    # 终之气
}

# 二十四节气（按顺序）
JIEQI_24 = [
    '立春', '雨水', '惊蛰', '春分', '清明', '谷雨',
    '立夏', '小满', '芒种', '夏至', '小暑', '大暑',
    '立秋', '处暑', '白露', '秋分', '寒露', '霜降',
    '立冬', '小雪', '大雪', '冬至', '小寒', '大寒',
]

# ═══════════════════════════════════════════════════════════════
# 辅助函数
# ═══════════════════════════════════════════════════════════════

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

# 六步名称
QI_STEP_NAMES = {
    1: '初之气(主大寒~春分)',
    2: '二之气(主春分~小满)',
    3: '三之气(主小满~大暑)',
    4: '四之气(主大暑~秋分)',
    5: '五之气(主秋分~小雪)',
    6: '终之气(主小雪~大寒)',
}

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
        return None


def get_jieqi_date(year, jieqi_name):
    """
    获取指定公历年份某节气的日期
    返回: (year, month, day) 元组
    
    大寒在年初(Jan)，需从前一年的 Lunar 表中获取
    其他节气(春分~小雪)在年中，从当年的 Lunar 表中获取
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
    
    # 兜底: 遍历法
    for month in range(1, 13):
        for day in range(1, 29):
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
    parts = date_str.split('-')
    solar_year = int(parts[0])
    solar_month = int(parts[1])
    solar_day = int(parts[2])
    
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
    parts = date_str.split('-')
    date_y = int(parts[0])
    date_m = int(parts[1])
    date_d = int(parts[2])
    
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
    
    parts = date_str.split('-')
    y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
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
