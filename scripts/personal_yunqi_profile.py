#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个人运气体质分析入口
根据出生日期 + 所在地区，输出先天运气体质倾向与当前调理建议。

用法:
  python scripts/personal_yunqi_profile.py <出生日期YYYY-MM-DD> [地区]
  python scripts/personal_yunqi_profile.py 1990-05-20 北京
  python scripts/personal_yunqi_profile.py 1990-05-20 --json
"""
import sys
import os
import io
import json
import subprocess
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from constitution_assessment import assess_constitution, extract_scores_and_metadata, parse_input_payload  # noqa: E402

# Windows 终端默认编码可能不是 UTF-8，强制设置 stdout/stderr 编码
if sys.platform == 'win32' and sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except (AttributeError, io.UnsupportedOperation):
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAG_DIR = os.path.join(BASE_DIR, 'rag-knowledge-base')


def load_json(filename):
    path = os.path.join(RAG_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_yunqi_year(date_str):
    """调用 calculate_yunqi_api.py 获取运气年份"""
    script = os.path.join(BASE_DIR, 'scripts', 'calculate_yunqi_api.py')
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    result = subprocess.run(
        [sys.executable, script, date_str, '--json'],
        capture_output=True, text=True, encoding='utf-8', env=env
    )
    data = json.loads(result.stdout)
    return data['yunqi_year'], data['sui_yun']['code'], data['sui_yun']['name']


def match_region(region_name):
    """根据地区名匹配地域修正条目"""
    if not region_name:
        return None
    regional = load_json('asset6_regional.json')
    region_name = region_name.strip()
    for entry in regional['entries']:
        if region_name in entry['region_name'] or entry['region_name'] in region_name:
            return entry
    # 模糊匹配：按关键字
    keywords = {
        '东北': '东北地区（黑吉辽）', '华北': '华北地区（京津冀晋）',
        '西北': '西北地区（陕甘宁青新）', '华东': '华东地区（江浙沪皖）',
        '华南': '华南地区（粤桂闽琼）', '华中': '华中地区（鄂湘赣豫）',
        '西南': '西南地区（川渝云贵）', '青藏': '青藏高原（青藏）',
        '北京': '华北地区（京津冀晋）', '天津': '华北地区（京津冀晋）',
        '河北': '华北地区（京津冀晋）', '山西': '华北地区（京津冀晋）',
        '上海': '华东地区（江浙沪皖）', '江苏': '华东地区（江浙沪皖）',
        '浙江': '华东地区（江浙沪皖）', '安徽': '华东地区（江浙沪皖）',
        '广东': '华南地区（粤桂闽琼）', '广西': '华南地区（粤桂闽琼）',
        '福建': '华南地区（粤桂闽琼）', '海南': '华南地区（粤桂闽琼）',
        '四川': '西南地区（川渝云贵）', '重庆': '西南地区（川渝云贵）',
        '云南': '西南地区（川渝云贵）', '贵州': '西南地区（川渝云贵）',
        '湖北': '华中地区（鄂湘赣豫）', '湖南': '华中地区（鄂湘赣豫）',
        '江西': '华中地区（鄂湘赣豫）', '河南': '华中地区（鄂湘赣豫）',
        '陕西': '西北地区（陕甘宁青新）', '甘肃': '西北地区（陕甘宁青新）',
        '宁夏': '西北地区（陕甘宁青新）', '青海': '西北地区（陕甘宁青新）',
        '新疆': '西北地区（陕甘宁青新）', '辽宁': '东北地区（黑吉辽）',
        '吉林': '东北地区（黑吉辽）', '黑龙江': '东北地区（黑吉辽）',
        '西藏': '青藏高原（青藏）', '青海': '青藏高原（青藏）',
    }
    full_name = keywords.get(region_name)
    if full_name:
        for entry in regional['entries']:
            if entry['region_name'] == full_name:
                return entry
    return None


def match_birth_constitution(suiyun_code):
    """根据出生年运代码匹配先天体质条目"""
    constitution = load_json('asset7_constitution.json')
    matches = []
    for entry in constitution['entries']:
        if entry.get('entry_type') != 'birth_yunqi_mapping':
            continue
        if suiyun_code in entry.get('birth_yunqi_keys', []):
            matches.append(entry)
    return matches


def match_current_adjustment(suiyun_code):
    """根据当前岁运代码匹配调理条目"""
    constitution = load_json('asset7_constitution.json')
    for entry in constitution['entries']:
        if entry.get('entry_type') != 'suiyun_constitution_adjustment':
            continue
        if entry.get('suiyun_code') == suiyun_code:
            return entry
    return None


def normalize_affected_constitutions(items):
    codes = []
    for item in items or []:
        if isinstance(item, str):
            codes.append(item)
        elif isinstance(item, dict):
            code = item.get('code') or item.get('constitution_code')
            if code:
                codes.append(code)
    return codes


def synthesize_innate_acquired(birth_constitutions, current_adjustment, constitution_assessment):
    """合成先天运气体质与后天量表体质。"""
    if not constitution_assessment:
        return None
    birth_codes = [c['constitution_code'] for c in birth_constitutions if c.get('constitution_code')]
    birth_names = [c['constitution_name'] for c in birth_constitutions if c.get('constitution_name')]
    primary_code = constitution_assessment.get('primary_code')
    secondary_codes = constitution_assessment.get('secondary_codes') or []
    assessed_codes = [c for c in [primary_code] + secondary_codes if c]
    current_affected = normalize_affected_constitutions((current_adjustment or {}).get('most_affected_constitutions'))

    innate_acquired_overlap = sorted(set(birth_codes) & set(assessed_codes))
    acquired_suiyun_overlap = sorted(set(assessed_codes) & set(current_affected))
    triple_overlap = sorted(set(birth_codes) & set(assessed_codes) & set(current_affected))

    if triple_overlap:
        level = 'high'
        label = '先天运气、后天体质与当前岁运三重同向'
        summary = '出生年运气体质倾向、量表评估体质与当前岁运易感体质出现同向叠加，调理应优先处理该体质偏性。'
    elif innate_acquired_overlap:
        level = 'medium_high'
        label = '先天运气与后天体质同向'
        summary = '出生年运气体质倾向与量表评估结果相合，提示先天后天同气相引。'
    elif acquired_suiyun_overlap:
        level = 'medium'
        label = '后天体质受当前岁运牵动'
        summary = '量表评估体质与当前岁运易感体质相合，调理以当前岁运与后天体质为主。'
    else:
        level = 'baseline'
        label = '先天后天未见明显同向叠加'
        summary = '出生年运气体质倾向与量表评估体质未见明显重合，建议分别参考，避免机械合并。'

    focus_codes = triple_overlap or innate_acquired_overlap or acquired_suiyun_overlap or assessed_codes[:2] or birth_codes[:2]
    code_to_name = {}
    for c in birth_constitutions:
        code_to_name[c.get('constitution_code')] = c.get('constitution_name')
    if constitution_assessment:
        code_to_name[constitution_assessment.get('primary_code')] = constitution_assessment.get('primary_type')
        for name, code in zip(constitution_assessment.get('secondary_types') or [], constitution_assessment.get('secondary_codes') or []):
            code_to_name[code] = name

    return {
        'level': level,
        'label': label,
        'summary': summary,
        'birth_codes': birth_codes,
        'birth_names': birth_names,
        'assessed_codes': assessed_codes,
        'assessed_primary': constitution_assessment.get('primary_type'),
        'assessed_secondary': constitution_assessment.get('secondary_types') or [],
        'current_suiyun_affected_codes': current_affected,
        'innate_acquired_overlap': innate_acquired_overlap,
        'acquired_suiyun_overlap': acquired_suiyun_overlap,
        'triple_overlap': triple_overlap,
        'focus_constitutions': [code_to_name.get(code, code) for code in focus_codes],
        'care_priority': constitution_assessment.get('care_priority', ''),
    }


def generate_profile(birth_date, region=None, as_json=False, today=None, constitution_assessment=None):
    birth_year, birth_suiyun_code, birth_suiyun_name = get_yunqi_year(birth_date)
    if today is None:
        today = date.today().isoformat()
    current_year, current_suiyun_code, current_suiyun_name = get_yunqi_year(today)

    birth_constitutions = match_birth_constitution(birth_suiyun_code)
    current_adjustment = match_current_adjustment(current_suiyun_code)
    region_entry = match_region(region) if region else None
    innate_acquired = synthesize_innate_acquired(birth_constitutions, current_adjustment, constitution_assessment)

    profile = {
        'birth_date': birth_date,
        'birth_yunqi_year': birth_year,
        'birth_suiyun': {
            'code': birth_suiyun_code,
            'name': birth_suiyun_name,
        },
        'region': region,
        'current_date': today,
        'current_yunqi_year': current_year,
        'current_suiyun': {
            'code': current_suiyun_code,
            'name': current_suiyun_name,
        },
        'birth_constitutions': [
            {
                'name': c['constitution_name'],
                'code': c['constitution_code'],
                'description': c['description'],
                'birth_year_analysis': c['birth_year_analysis'],
            }
            for c in birth_constitutions
        ],
        'current_adjustment': current_adjustment and {
            'name': current_adjustment['suiyun_name'],
            'most_affected_constitutions': current_adjustment.get('most_affected_constitutions', []),
            'health_risks': current_adjustment.get('health_risks', []),
            'lifestyle_advice': current_adjustment.get('lifestyle_advice', ''),
            'dietary_herbs': current_adjustment.get('dietary_herbs', ''),
            'acupuncture_points': current_adjustment.get('acupuncture_points', []),
            'preventive_measures': current_adjustment.get('preventive_measures', ''),
        },
        'regional_modifier': region_entry and {
            'region_name': region_entry['region_name'],
            'climate_characteristics': region_entry['climate_characteristics'],
            'wuyun_modifier': region_entry['wuyun_modifier'],
            'liuqi_modifier': region_entry['liuqi_modifier'],
            'constitution_tendency': region_entry['constitution_tendency'],
        },
        'constitution_assessment': constitution_assessment,
        'innate_acquired_synthesis': innate_acquired,
    }

    if as_json:
        return json.dumps(profile, ensure_ascii=False, indent=2)

    lines = [
        f"# 个人运气体质分析报告",
        f"",
        f"**出生日期**: {birth_date}（运气年 {birth_year}）",
        f"**先天岁运**: {birth_suiyun_name}（{birth_suiyun_code}）",
    ]
    if region:
        lines.append(f"**所在地区**: {region}")
    lines.append(f"**当前日期**: {today}（运气年 {current_year}，{current_suiyun_name}）")
    lines.append("")

    lines.append("## 一、先天体质倾向")
    if birth_constitutions:
        for c in birth_constitutions:
            lines.append(f"\n### {c['constitution_name']}")
            lines.append(f"{c['description']}")
            lines.append(f"\n{c['birth_year_analysis'][:200]}...")
    else:
        lines.append("未找到明确对应体质，建议结合九种体质量表综合判断。")
    lines.append("")

    lines.append("## 二、当前岁运调理方向")
    if current_adjustment:
        lines.append(f"当前为{current_adjustment['suiyun_name']}。")
        lines.append(f"\n**易发健康问题**：")
        for risk in current_adjustment.get('health_risks', []):
            lines.append(f"- {risk}")
        lines.append(f"\n**生活调养**：{current_adjustment.get('lifestyle_advice', '')}")
        lines.append(f"\n**饮食药膳**：{current_adjustment.get('dietary_herbs', '')}")
        if current_adjustment.get('acupuncture_points'):
            lines.append(f"\n**参考穴位**：{'、'.join(current_adjustment['acupuncture_points'][:5])}")
    else:
        lines.append("未找到当前岁运调理条目。")
    lines.append("")

    if constitution_assessment:
        lines.append("## 三、后天体质量表评估")
        lines.append(f"**主要体质**: {constitution_assessment['primary_type']}（{constitution_assessment['primary_score']}分）")
        secondaries = '、'.join(constitution_assessment.get('secondary_types') or []) or '无'
        lines.append(f"**兼夹/倾向体质**: {secondaries}")
        lines.append(f"**体质解释**: {constitution_assessment.get('interpretation', '')}")
        lines.append(f"**调理重点**: {constitution_assessment.get('care_priority', '')}")
        lines.append("")
        if innate_acquired:
            lines.append("## 四、先天运气体质 × 后天体质对比")
            lines.append(f"**叠加判断**: {innate_acquired['label']}（{innate_acquired['level']}）")
            lines.append(f"**重点体质**: {'、'.join(innate_acquired.get('focus_constitutions') or []) or '未指定'}")
            lines.append(f"**摘要**: {innate_acquired['summary']}")
            lines.append("")

    if region_entry:
        lines.append("## 地域运气修正")
        lines.append(f"**地区**: {region_entry['region_name']}")
        lines.append(f"**气候特征**: {region_entry['climate_characteristics']}")
        lines.append(f"**五运修正**: {region_entry['wuyun_modifier']['description']}")
        lines.append(f"**六气修正**: {region_entry['liuqi_modifier']['description']}")
        lines.append(f"**体质倾向**: {region_entry['constitution_tendency']}")
        lines.append("")

    lines.append(
        "> ⚠️ 免责声明：以上分析基于中医运气学说与体质学说理论推算，仅供参考。"
        "运气学说与体质学说非现代医学诊断标准，具体诊疗须由执业中医师辨证论治。"
        "请勿据此自行用药或针灸。"
    )

    return '\n'.join(lines)


def load_constitution_assessment_from_args(args):
    """解析 CLI 体质量表参数并返回评估结果。"""
    if not any(k in args for k in ('--constitution-demo', '--constitution-file', '--constitution-scores')):
        return None

    class _Args:
        pass

    proxy = _Args()
    proxy.demo = '--constitution-demo' in args
    proxy.file = None
    proxy.scores = None
    if '--constitution-file' in args:
        idx = args.index('--constitution-file')
        if idx + 1 < len(args):
            proxy.file = args[idx + 1]
    if '--constitution-scores' in args:
        idx = args.index('--constitution-scores')
        if idx + 1 < len(args):
            proxy.scores = args[idx + 1]
    payload = parse_input_payload(proxy)
    scores, metadata = extract_scores_and_metadata(payload)
    return assess_constitution(scores, metadata=metadata)


def main():
    if len(sys.argv) < 2:
        print("用法: python scripts/personal_yunqi_profile.py <出生日期YYYY-MM-DD> [地区] [--json] [--constitution-demo|--constitution-file <file>|--constitution-scores <json>]")
        print("示例: python scripts/personal_yunqi_profile.py 1990-05-20 北京")
        sys.exit(1)

    birth_date = sys.argv[1]
    region = None
    as_json = False
    constitution_assessment = load_constitution_assessment_from_args(sys.argv[2:])
    skip_next = False
    option_with_value = {'--constitution-file', '--constitution-scores'}
    for arg in sys.argv[2:]:
        if skip_next:
            skip_next = False
            continue
        if arg == '--json':
            as_json = True
        elif arg == '--constitution-demo':
            continue
        elif arg in option_with_value:
            skip_next = True
            continue
        elif arg.startswith('--'):
            continue
        elif not region:
            region = arg

    output = generate_profile(birth_date, region, as_json, today=None, constitution_assessment=constitution_assessment)
    sys.stdout.write(output)
    if not output.endswith('\n'):
        sys.stdout.write('\n')
    sys.stdout.flush()


if __name__ == '__main__':
    main()
