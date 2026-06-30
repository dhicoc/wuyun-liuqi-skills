#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五运六气高级对齐统一入口

统一整合：
1. 基础运气推算：calculate_yunqi_api.py
2. 出生运气体质：personal_yunqi_profile.py（可选）
3. 九种体质量表：constitution_assessment.py（可选）
4. 天气实况对齐：weather_alignment.py（可选）
5. 天气 × 体质叠加：当同时具备出生日期与天气时自动生成

用法：
  python scripts/advanced_alignment.py --date 2026-06-29 --city 杭州 --mock
  python scripts/advanced_alignment.py --date 2026-06-29 --birth-date 2003-04-19 --city 杭州 --mock --json
  python scripts/advanced_alignment.py --date 2026-06-29 --birth-date 2003-04-19 --constitution-demo --city 杭州 --mock --json
  python scripts/advanced_alignment.py --date 2026-06-29 --constitution-file constitution_scores.json --json
"""
import argparse
import json
import os
import sys
import io

if sys.platform == 'win32' and sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except (AttributeError, io.UnsupportedOperation):
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from calculate_yunqi_api import calculate_yunqi_api  # noqa: E402
from constitution_assessment import (  # noqa: E402
    assess_constitution,
    extract_scores_and_metadata,
    parse_input_payload,
)
from personal_yunqi_profile import generate_profile, match_region, build_regional_explainable_modifier  # noqa: E402
from weather_alignment import (  # noqa: E402
    DISCLAIMER,
    fetch_climatology,
    fetch_weather,
    generate_result as generate_weather_result,
    resolve_location,
)
from yunqi_weather_constitution import synthesize as synthesize_birth_weather  # noqa: E402

CONSTITUTION_CODE_TO_NAME = {
    'ping_he': '平和质',
    'qi_xu': '气虚质',
    'yang_xu': '阳虚质',
    'yin_xu': '阴虚质',
    'tan_shi': '痰湿质',
    'shi_re': '湿热质',
    'xue_yu': '血瘀质',
    'qi_yu': '气郁质',
    'te_bing': '特禀质',
}


def has_location(args):
    return bool(args.city or (args.lat is not None and args.lon is not None) or args.mock or args.provider == 'mock')


def load_constitution_assessment(args):
    if not (args.constitution_demo or args.constitution_file or args.constitution_scores):
        return None

    class _Args:
        pass

    proxy = _Args()
    proxy.demo = args.constitution_demo
    proxy.file = args.constitution_file
    proxy.scores = args.constitution_scores
    payload = parse_input_payload(proxy)
    scores, metadata = extract_scores_and_metadata(payload)
    return assess_constitution(
        scores,
        metadata=metadata,
        assessment_date=args.assessment_date,
        assessed_by=args.assessed_by,
    )


def build_weather_alignment(date_str, args):
    if args.no_weather:
        return None
    if not has_location(args):
        return None

    use_mock = args.mock or args.provider == 'mock'
    city = args.city
    if use_mock and not city and (args.lat is None or args.lon is None):
        city = '杭州'
    location = resolve_location(
        city=city,
        lat=args.lat,
        lon=args.lon,
        timeout=args.timeout,
        no_cache=args.no_cache,
    )
    weather = fetch_weather(
        date_str,
        location,
        mock=use_mock,
        timeout=args.timeout,
        strict=args.strict,
        provider=args.provider,
        cache_ttl=args.cache_ttl,
        no_cache=args.no_cache,
    )
    climatology = fetch_climatology(
        date_str,
        location,
        years=0 if args.no_baseline else args.baseline_years,
        mock=use_mock,
        timeout=args.timeout,
        no_cache=args.no_cache,
    )
    return generate_weather_result(
        date_str,
        location,
        weather,
        climatology=climatology,
        as_mock=use_mock,
        provider=args.provider,
        cache_enabled=not args.no_cache,
        cache_ttl=args.cache_ttl,
    )


def build_personal_profile(date_str, birth_date, region=None):
    if not birth_date:
        return None
    return json.loads(generate_profile(birth_date, region=region, as_json=True, today=date_str))


def normalize_codes(codes):
    return [c for c in (codes or []) if c]


def build_regional_alignment(region=None, constitution=None):
    if not region:
        return None
    entry = match_region(region)
    return build_regional_explainable_modifier(entry, constitution_assessment=constitution) if entry else None


def build_location_entry(label, value=None, lat=None, lon=None, role='current'):
    if not value and (lat is None or lon is None):
        return None
    if lat is not None and lon is not None:
        resolved = {'name': value or label, 'latitude': float(lat), 'longitude': float(lon), 'source': f'{role}_coordinates'}
    else:
        try:
            resolved = resolve_location(city=value, lat=None, lon=None, timeout=10, no_cache=False)
        except Exception:
            resolved = {'name': value, 'latitude': None, 'longitude': None, 'source': f'{role}_unresolved'}
    regional = build_regional_alignment(value or resolved.get('name'))
    return {
        'role': role,
        'label': label,
        'input': value,
        'resolved': resolved,
        'regional_alignment': regional,
    }


def compare_location_differences(birth_place=None, residence_place=None, current_place=None):
    entries = [e for e in [birth_place, residence_place, current_place] if e]
    if not entries:
        return None
    region_names = []
    factor_sets = []
    for entry in entries:
        regional = entry.get('regional_alignment') or {}
        region_names.append(regional.get('region_name') or entry.get('resolved', {}).get('name'))
        factor_sets.append(set(regional.get('affected_factors') or []))
    unique_regions = sorted(set([r for r in region_names if r]))
    common_factors = sorted(set.intersection(*factor_sets)) if factor_sets and all(factor_sets) else []
    all_factors = sorted(set.union(*factor_sets)) if factor_sets else []
    diff_factors = sorted(set(all_factors) - set(common_factors))
    if len(unique_regions) <= 1:
        summary = '出生地、常住地、当前地地域修正基本一致，地域因素相对稳定。'
    else:
        summary = f'涉及 {len(unique_regions)} 个地域修正区域：{"、".join(unique_regions)}，需区分先天地域、长期居住与当下实况。'
    return {
        'status': 'ok',
        'locations': entries,
        'unique_regions': unique_regions,
        'common_factors': common_factors,
        'different_factors': diff_factors,
        'summary': summary,
    }


def synthesize_all(profile=None, weather_alignment=None, constitution=None, regional_alignment=None, location_difference=None):
    layers = []
    focus_codes = []
    notes = []

    if profile:
        birth_items = profile.get('birth_constitutions') or []
        birth_codes = normalize_codes([item.get('code') for item in birth_items])
        focus_codes.extend(birth_codes)
        if birth_codes:
            layers.append('birth_yunqi')
            notes.append(f"出生运气提示：{'、'.join(item.get('name', item.get('code', '')) for item in birth_items)}。")
    else:
        birth_codes = []

    if constitution:
        primary_code = constitution.get('primary_code')
        secondary_codes = constitution.get('secondary_codes') or []
        assessed_codes = normalize_codes([primary_code] + secondary_codes)
        focus_codes.extend(assessed_codes)
        layers.append('constitution_assessment')
        notes.append(f"量表评估提示：{constitution.get('primary_type')}为主，兼夹/倾向：{'、'.join(constitution.get('secondary_types') or []) or '无'}。")
    else:
        assessed_codes = []

    if weather_alignment:
        layers.append('weather_alignment')
        weather_qi = weather_alignment.get('weather_qi') or {}
        alignment = weather_alignment.get('alignment') or {}
        notes.append(f"天气实况为{weather_qi.get('pattern')}，对齐类型为{alignment.get('label')}。")
    else:
        weather_qi = {}

    if regional_alignment:
        layers.append('regional_alignment')
        notes.append(f"地域修正提示：{regional_alignment.get('region_name')}，五运权重 {regional_alignment.get('wuyun_weight')}，六气权重 {regional_alignment.get('liuqi_weight')}。")
        notes.extend(regional_alignment.get('overlap_notes') or [])

    if location_difference:
        layers.append('location_difference')
        notes.append(location_difference.get('summary', ''))
        if location_difference.get('different_factors'):
            notes.append(f"地域差异因子：{'、'.join(location_difference.get('different_factors'))}。")

    combined_birth_weather = None
    if profile and weather_alignment:
        combined_birth_weather = synthesize_birth_weather(profile, weather_alignment)
        focus_codes.extend(combined_birth_weather.get('triple_overlap') or [])
        focus_codes.extend(combined_birth_weather.get('birth_weather_overlap') or [])
        focus_codes.extend(combined_birth_weather.get('birth_suiyun_overlap') or [])

    overlap_assessed_birth = sorted(set(assessed_codes) & set(birth_codes))
    weather_affected_codes = set((combined_birth_weather or {}).get('weather_affected_codes') or [])
    overlap_assessed_weather = sorted(set(assessed_codes) & weather_affected_codes)
    triple = sorted(set(assessed_codes) & set(birth_codes) & weather_affected_codes)

    if triple:
        level = 'very_high'
        label = '量表体质、出生运气与天气实况三重同向'
        summary = '后天量表体质、先天出生运气倾向与天气实况偏性出现三重叠加，调摄优先级最高。'
    elif overlap_assessed_birth and overlap_assessed_weather:
        level = 'high'
        label = '量表体质同时受出生运气与天气牵动'
        summary = '量表体质与出生运气、天气实况均有交集，但不完全落在同一体质代码，宜按兼夹处理。'
    elif overlap_assessed_weather:
        level = 'medium_high'
        label = '量表体质受天气实况触发'
        summary = '当前天气六气偏性与量表评估体质同向，调摄上应优先顺应当下天气。'
    elif overlap_assessed_birth:
        level = 'medium_high'
        label = '量表体质与出生运气同向'
        summary = '量表评估体质与出生年运气体质倾向同向，提示先天后天同气相引。'
    elif combined_birth_weather:
        level = combined_birth_weather.get('level', 'medium')
        label = combined_birth_weather.get('label', '出生运气与天气叠加')
        summary = combined_birth_weather.get('summary', '')
    elif constitution:
        level = 'medium'
        label = '量表体质主导'
        summary = '当前以九种体质量表结果作为个体化调理主轴。'
    elif weather_alignment:
        level = 'baseline_weather'
        label = '天气对齐主导'
        summary = '当前以天气实况与运气格局对齐结果作为调摄参考。'
    elif profile:
        level = 'baseline_profile'
        label = '出生运气体质主导'
        summary = '当前以出生年运气体质倾向作为参考。'
    else:
        level = 'baseline_yunqi'
        label = '基础运气推算'
        summary = '未提供天气、出生日期或体质问卷，当前仅输出基础运气推算。'

    unique_focus = []
    for code in focus_codes:
        if code and code not in unique_focus:
            unique_focus.append(code)

    focus_names = [CONSTITUTION_CODE_TO_NAME.get(code, code) for code in unique_focus[:5]]
    return {
        'level': level,
        'label': label,
        'summary': summary,
        'layers': layers,
        'notes': notes,
        'focus_codes': unique_focus,
        'focus_constitutions': focus_names,
        'overlap_assessed_birth': overlap_assessed_birth,
        'overlap_assessed_weather': overlap_assessed_weather,
        'triple_overlap': triple,
        'birth_weather_synthesis': combined_birth_weather,
    }


def generate_advanced_alignment(args):
    date_str = args.date or args.date_arg
    if not date_str:
        raise ValueError('请通过 --date 或位置参数提供分析日期。')

    yunqi = calculate_yunqi_api(date_str)
    constitution = load_constitution_assessment(args)
    weather = build_weather_alignment(date_str, args)
    current_region = args.current_place or args.region or args.city
    birth_region = args.birth_place
    residence_region = args.residence_place
    profile_region = args.region or residence_region or current_region
    profile = build_personal_profile(date_str, args.birth_date, region=profile_region)
    regional_alignment = build_regional_alignment(region=current_region, constitution=constitution)
    birth_location = build_location_entry('出生地', value=birth_region, role='birth')
    residence_location = build_location_entry('常住地', value=residence_region, role='residence')
    current_location = build_location_entry('当前地', value=current_region, lat=args.lat, lon=args.lon, role='current')
    location_difference = compare_location_differences(birth_location, residence_location, current_location)
    synthesis = synthesize_all(
        profile=profile,
        weather_alignment=weather,
        constitution=constitution,
        regional_alignment=regional_alignment,
        location_difference=location_difference,
    )

    return {
        'date': date_str,
        'yunqi': yunqi,
        'personal_profile': profile,
        'constitution_assessment': constitution,
        'weather_alignment': weather,
        'regional_alignment': regional_alignment,
        'location_difference': location_difference,
        'advanced_synthesis': synthesis,
        'disclaimer': DISCLAIMER,
    }


def format_markdown(result):
    yq = result['yunqi']
    synthesis = result['advanced_synthesis']
    lines = [
        '# 五运六气高级对齐综合报告',
        '',
        '## 基础运气',
        f"- 日期：{result['date']}",
        f"- 运气年：{yq['yunqi_year']}（{yq['year_gz']}）",
        f"- 岁运：{yq['sui_yun']['name']}{yq['sui_yun']['status']}",
        f"- 司天 / 在泉：{yq['si_tian']} / {yq['zai_quan']}",
        f"- 当前步位：{yq['current_step']['name']}，主气 {yq['current_step']['zhu_qi']}，客气 {yq['current_step']['ke_qi']}",
        '',
        '## 已启用对齐层',
        f"- {', '.join(synthesis['layers']) if synthesis['layers'] else '仅基础运气'}",
        '',
        '## 综合判断',
        f"- 等级：{synthesis['label']}（{synthesis['level']}）",
        f"- 重点体质：{'、'.join(synthesis['focus_constitutions']) if synthesis['focus_constitutions'] else '未指定'}",
        f"- 摘要：{synthesis['summary']}",
    ]
    if synthesis.get('notes'):
        lines.append('- 分层提示：')
        for note in synthesis['notes']:
            lines.append(f"  - {note}")

    constitution = result.get('constitution_assessment')
    if constitution:
        lines.extend([
            '',
            '## 体质量表',
            f"- 主要体质：{constitution['primary_type']}（{constitution['primary_score']} 分）",
            f"- 兼夹/倾向：{'、'.join(constitution['secondary_types']) if constitution['secondary_types'] else '无'}",
            f"- 调理重点：{constitution['care_priority']}",
        ])

    weather = result.get('weather_alignment')
    if weather:
        lines.extend([
            '',
            '## 天气对齐',
            f"- 实况六气：{weather['weather_qi']['pattern']}",
            f"- 对齐类型：{weather['alignment']['label']}（{weather['alignment']['type']}）",
            f"- 调摄原则：{weather['alignment']['care_principle']}",
        ])

    regional = result.get('regional_alignment')
    if regional:
        lines.extend([
            '',
            '## 地域可解释修正',
            f"- 地区：{regional['region_name']}",
            f"- 五运权重：{regional['wuyun_weight']}；六气权重：{regional['liuqi_weight']}",
            f"- 影响因子：{'、'.join(regional.get('affected_factors') or []) or '未提取'}",
            f"- 地域解释：{regional['explanation']}",
        ])
        for note in regional.get('overlap_notes') or []:
            lines.append(f"  - {note}")

    location_diff = result.get('location_difference')
    if location_diff:
        lines.extend([
            '',
            '## 出生地 / 常住地 / 当前地差异',
            f"- 涉及区域：{'、'.join(location_diff.get('unique_regions') or []) or '未匹配'}",
            f"- 共同因子：{'、'.join(location_diff.get('common_factors') or []) or '无'}",
            f"- 差异因子：{'、'.join(location_diff.get('different_factors') or []) or '无'}",
            f"- 摘要：{location_diff.get('summary', '')}",
        ])
        for item in location_diff.get('locations') or []:
            regional_item = item.get('regional_alignment') or {}
            lines.append(f"  - {item.get('label')}：{item.get('resolved', {}).get('name')} → {regional_item.get('region_name', '未匹配')}")

    profile = result.get('personal_profile')
    if profile:
        names = [item.get('name') for item in profile.get('birth_constitutions') or []]
        lines.extend([
            '',
            '## 出生运气体质',
            f"- 出生日期：{profile['birth_date']}（运气年 {profile['birth_yunqi_year']}）",
            f"- 先天岁运：{profile['birth_suiyun']['name']}（{profile['birth_suiyun']['code']}）",
            f"- 匹配体质：{'、'.join(names) if names else '未匹配明确体质'}",
        ])

    lines.extend(['', result['disclaimer']])
    return '\n'.join(lines)


def build_arg_parser():
    parser = argparse.ArgumentParser(description='五运六气高级对齐统一入口')
    parser.add_argument('date_arg', nargs='?', help='分析日期，格式 YYYY-MM-DD；也可用 --date')
    parser.add_argument('--date', help='分析日期，格式 YYYY-MM-DD')
    parser.add_argument('--birth-date', help='出生日期，格式 YYYY-MM-DD')
    parser.add_argument('--city', help='城市名，如 杭州、北京、上海；默认作为当前地')
    parser.add_argument('--region', help='地域修正名；默认复用 current-place/city')
    parser.add_argument('--birth-place', help='出生地，用于地域差异分析')
    parser.add_argument('--residence-place', help='常住地，用于地域差异分析')
    parser.add_argument('--current-place', help='当前地；默认复用 city')
    parser.add_argument('--lat', type=float, help='纬度')
    parser.add_argument('--lon', type=float, help='经度')
    parser.add_argument('--constitution-demo', action='store_true', help='使用内置体质量表示例')
    parser.add_argument('--constitution-file', help='体质量表 JSON 文件')
    parser.add_argument('--constitution-scores', help='体质量表 JSON 字符串')
    parser.add_argument('--assessment-date', help='体质评估日期')
    parser.add_argument('--assessed-by', default='self-assessment', help='体质评估方式')
    parser.add_argument('--provider', choices=['auto', 'open-meteo', 'qweather', 'seniverse', 'mock'], default='auto')
    parser.add_argument('--mock', action='store_true', help='天气使用 mock 数据')
    parser.add_argument('--no-weather', action='store_true', help='不执行天气对齐')
    parser.add_argument('--baseline-years', type=int, default=5)
    parser.add_argument('--no-baseline', action='store_true')
    parser.add_argument('--cache-ttl', type=int, default=60)
    parser.add_argument('--no-cache', action='store_true')
    parser.add_argument('--strict', action='store_true')
    parser.add_argument('--timeout', type=int, default=10)
    parser.add_argument('--json', action='store_true', help='输出 JSON')
    return parser


def main():
    parser = build_arg_parser()
    args = parser.parse_args()
    try:
        result = generate_advanced_alignment(args)
        if args.json:
            sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        else:
            sys.stdout.write(format_markdown(result) + '\n')
    except Exception as exc:
        sys.stderr.write(f'❌ 高级对齐失败：{exc}\n')
        sys.exit(1)


if __name__ == '__main__':
    main()
