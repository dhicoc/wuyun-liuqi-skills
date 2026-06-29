#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五运六气 × 天气 × 体质三维叠加分析

将三个维度组合：
1. 出生日期 → 先天运气体质倾向（personal_yunqi_profile.py）
2. 指定日期与地点 → 运气 × 天气对齐（weather_alignment.py）
3. 当前岁运调理 → 体质易感性叠加判断

用法：
  python scripts/yunqi_weather_constitution.py 2026-06-29 --birth-date 2003-04-19 --city 杭州
  python scripts/yunqi_weather_constitution.py 2026-06-29 --birth-date 2003-04-19 --city 杭州 --mock --json
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

from personal_yunqi_profile import generate_profile  # noqa: E402
from weather_alignment import (  # noqa: E402
    DISCLAIMER,
    fetch_climatology,
    fetch_weather,
    generate_result as generate_weather_result,
    resolve_location,
)

CONSTITUTION_NAMES = {
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

WEATHER_QI_AFFECTS = {
    '寒': ['yang_xu', 'qi_xu', 'xue_yu'],
    '湿': ['tan_shi', 'shi_re', 'qi_xu', 'yang_xu'],
    '火热': ['yin_xu', 'shi_re', 'qi_yu', 'te_bing'],
    '暑热': ['yin_xu', 'shi_re', 'qi_xu'],
    '燥': ['yin_xu', 'te_bing', 'qi_xu'],
    '风': ['qi_yu', 'te_bing', 'xue_yu'],
}


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


def affected_by_weather(weather_qi):
    codes = []
    reasons = []
    for qi in weather_qi.get('qi', []):
        for code in WEATHER_QI_AFFECTS.get(qi, []):
            if code not in codes:
                codes.append(code)
        if qi in WEATHER_QI_AFFECTS:
            names = [CONSTITUTION_NAMES.get(c, c) for c in WEATHER_QI_AFFECTS[qi]]
            reasons.append(f'{qi}偏盛：较易影响{ "、".join(names) }')
    return codes, reasons


def synthesize(profile, weather_result):
    birth_constitutions = profile.get('birth_constitutions') or []
    birth_codes = [c.get('code') for c in birth_constitutions if c.get('code')]
    birth_names = [c.get('name') for c in birth_constitutions if c.get('name')]

    current_adjustment = profile.get('current_adjustment') or {}
    suiyun_affected = normalize_affected_constitutions(current_adjustment.get('most_affected_constitutions'))

    weather_affected, weather_reasons = affected_by_weather(weather_result.get('weather_qi') or {})

    birth_weather_overlap = sorted(set(birth_codes) & set(weather_affected))
    birth_suiyun_overlap = sorted(set(birth_codes) & set(suiyun_affected))
    triple_overlap = sorted(set(birth_codes) & set(weather_affected) & set(suiyun_affected))

    if triple_overlap:
        level = 'high'
        label = '先天体质、岁运与天气三重叠加'
        summary = '出生年运气体质倾向、当前岁运易感体质与天气实况偏性出现同向叠加，调理应优先处理该体质对应的易感方向。'
    elif birth_weather_overlap and birth_suiyun_overlap:
        level = 'medium_high'
        label = '先天体质分别受岁运与天气牵动'
        summary = '先天体质倾向同时被当前岁运与天气实况触发，但三者未完全落在同一体质代码上，宜按兼夹处理。'
    elif birth_weather_overlap:
        level = 'medium'
        label = '天气实况触发先天体质倾向'
        summary = '天气实况对应的六气偏性与出生年运气体质倾向相合，调理上需优先顺应当下天气。'
    elif birth_suiyun_overlap:
        level = 'medium'
        label = '当前岁运触发先天体质倾向'
        summary = '当前岁运调理条目提示的易感体质与出生年运气体质倾向相合，天气实况作为辅助参考。'
    elif weather_affected:
        level = 'baseline_weather'
        label = '天气实况主导'
        summary = '天气实况有明确六气偏性，但未直接命中出生年运气体质倾向，建议以天气调摄为主，先天体质为辅。'
    else:
        level = 'baseline'
        label = '未见明显叠加'
        summary = '未见先天体质、岁运与天气之间的明显同向叠加，维持顺时调摄即可。'

    focus_codes = triple_overlap or birth_weather_overlap or birth_suiyun_overlap or weather_affected[:3]
    focus_names = [CONSTITUTION_NAMES.get(code, code) for code in focus_codes]

    return {
        'level': level,
        'label': label,
        'summary': summary,
        'birth_constitutions': birth_constitutions,
        'birth_codes': birth_codes,
        'birth_names': birth_names,
        'weather_affected_codes': weather_affected,
        'weather_affected_names': [CONSTITUTION_NAMES.get(c, c) for c in weather_affected],
        'weather_reasons': weather_reasons,
        'suiyun_affected_codes': suiyun_affected,
        'suiyun_affected_names': [CONSTITUTION_NAMES.get(c, c) for c in suiyun_affected],
        'birth_weather_overlap': birth_weather_overlap,
        'birth_suiyun_overlap': birth_suiyun_overlap,
        'triple_overlap': triple_overlap,
        'focus_constitutions': focus_names,
        'care_principle': build_care_principle(weather_result, current_adjustment, focus_names),
    }


def build_care_principle(weather_result, current_adjustment, focus_names):
    weather_principle = (weather_result.get('alignment') or {}).get('care_principle') or ''
    lifestyle = (current_adjustment or {}).get('lifestyle_advice') or ''
    focus = '、'.join(focus_names) if focus_names else '当前体质偏性'
    pieces = []
    if weather_principle:
        pieces.append(f'天气调摄：{weather_principle}')
    pieces.append(f'体质重点：关注{focus}。')
    if lifestyle:
        pieces.append(f'岁运调理：{lifestyle[:160]}...')
    return ''.join(pieces)


def generate_combined(date_str, birth_date, city=None, region=None, lat=None, lon=None,
                      provider='auto', mock=False, baseline_years=5, no_baseline=False,
                      timeout=10, strict=False, no_cache=False, cache_ttl=60):
    location = resolve_location(city=city, lat=lat, lon=lon, timeout=timeout, no_cache=no_cache)
    weather = fetch_weather(
        date_str,
        location,
        mock=mock,
        timeout=timeout,
        strict=strict,
        provider=provider,
        cache_ttl=cache_ttl,
        no_cache=no_cache,
    )
    climatology = fetch_climatology(
        date_str,
        location,
        years=0 if no_baseline else baseline_years,
        mock=mock,
        timeout=timeout,
        no_cache=no_cache,
    )
    weather_result = generate_weather_result(
        date_str,
        location,
        weather,
        climatology=climatology,
        as_mock=mock,
        provider=provider,
        cache_enabled=not no_cache,
        cache_ttl=cache_ttl,
    )

    profile_json = generate_profile(birth_date, region=region or city, as_json=True, today=date_str)
    profile = json.loads(profile_json)
    synthesis = synthesize(profile, weather_result)

    return {
        'date': date_str,
        'birth_date': birth_date,
        'location': location,
        'region': region or city,
        'personal_profile': profile,
        'weather_alignment': weather_result,
        'combined_analysis': synthesis,
        'mock': bool(mock),
        'disclaimer': DISCLAIMER,
    }


def format_markdown(result):
    profile = result['personal_profile']
    weather = result['weather_alignment']
    combined = result['combined_analysis']
    loc = result['location']
    weather_qi = weather['weather_qi']
    alignment = weather['alignment']

    birth_names = combined.get('birth_names') or ['未匹配明确先天体质']
    focus = combined.get('focus_constitutions') or ['无明显重点体质']

    lines = [
        '# 五运六气 × 天气 × 体质三维叠加报告',
        '',
        '## 基本信息',
        f"- 分析日期：{result['date']}",
        f"- 出生日期：{result['birth_date']}（运气年 {profile['birth_yunqi_year']}）",
        f"- 地点：{loc['name']}（{loc['latitude']:.4f}, {loc['longitude']:.4f}）",
        f"- 先天岁运：{profile['birth_suiyun']['name']}（{profile['birth_suiyun']['code']}）",
        f"- 当前岁运：{profile['current_suiyun']['name']}（运气年 {profile['current_yunqi_year']}）",
        '',
        '## 先天体质倾向',
        f"- 匹配体质：{'、'.join(birth_names)}",
    ]
    for item in profile.get('birth_constitutions') or []:
        lines.append(f"  - {item.get('name')}：{item.get('description')}")

    lines.extend([
        '',
        '## 天气与运气对齐',
        f"- 实况六气：{weather_qi['pattern']}（{', '.join(weather_qi['qi']) if weather_qi['qi'] else '无明显偏盛'}）",
        f"- 天气对齐：{alignment['label']}（{alignment['type']}）",
        f"- 天气调摄：{alignment['care_principle']}",
        '',
        '## 三维叠加判断',
        f"- 叠加级别：{combined['label']}（{combined['level']}）",
        f"- 重点体质：{'、'.join(focus)}",
        f"- 判断摘要：{combined['summary']}",
    ])
    if combined.get('weather_reasons'):
        lines.append('- 天气影响体质依据：')
        for reason in combined['weather_reasons']:
            lines.append(f"  - {reason}")

    lines.extend([
        '',
        '## 综合调摄原则',
        combined['care_principle'],
        '',
        result['disclaimer'],
    ])
    return '\n'.join(lines)


def build_arg_parser():
    parser = argparse.ArgumentParser(description='五运六气 × 天气 × 体质三维叠加分析')
    parser.add_argument('date', help='分析日期，格式 YYYY-MM-DD')
    parser.add_argument('--birth-date', required=True, help='出生日期，格式 YYYY-MM-DD')
    parser.add_argument('--city', help='城市名，如 杭州、北京、上海')
    parser.add_argument('--region', help='地域修正名；默认复用 city')
    parser.add_argument('--lat', type=float, help='纬度')
    parser.add_argument('--lon', type=float, help='经度')
    parser.add_argument('--provider', choices=['auto', 'open-meteo', 'qweather', 'seniverse', 'mock'], default='auto')
    parser.add_argument('--mock', action='store_true', help='使用 mock 天气数据')
    parser.add_argument('--json', action='store_true', help='输出 JSON')
    parser.add_argument('--baseline-years', type=int, default=5)
    parser.add_argument('--no-baseline', action='store_true')
    parser.add_argument('--cache-ttl', type=int, default=60)
    parser.add_argument('--no-cache', action='store_true')
    parser.add_argument('--strict', action='store_true')
    parser.add_argument('--timeout', type=int, default=10)
    return parser


def main():
    parser = build_arg_parser()
    args = parser.parse_args()
    try:
        use_mock = args.mock or args.provider == 'mock'
        city = args.city
        if use_mock and not city and (args.lat is None or args.lon is None):
            city = '杭州'
        result = generate_combined(
            args.date,
            args.birth_date,
            city=city,
            region=args.region,
            lat=args.lat,
            lon=args.lon,
            provider=args.provider,
            mock=use_mock,
            baseline_years=args.baseline_years,
            no_baseline=args.no_baseline,
            timeout=args.timeout,
            strict=args.strict,
            no_cache=args.no_cache,
            cache_ttl=args.cache_ttl,
        )
        if args.json:
            sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        else:
            sys.stdout.write(format_markdown(result) + '\n')
    except Exception as exc:
        sys.stderr.write(f'❌ 三维叠加分析失败：{exc}\n')
        sys.exit(1)


if __name__ == '__main__':
    main()
