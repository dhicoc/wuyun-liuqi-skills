#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
九种体质量表评估脚本

根据王琦九种体质分类思路，接收 0-100 转化分，输出主要体质、兼夹体质、
判定等级与 Agent 可注入的 constitution_alignment context。

用法：
  python scripts/constitution_assessment.py --demo
  python scripts/constitution_assessment.py --demo --json
  python scripts/constitution_assessment.py --scores '{"阳虚质":78,"气虚质":50,"平和质":35}' --json
  python scripts/constitution_assessment.py --file constitution_scores.json --json
  python scripts/constitution_assessment.py --template

输入 JSON 支持：
  1. 直接九种体质得分对象
  2. {"constitution_scores": {...}, "metadata": {...}}
  3. {"scores": {...}}
"""
import argparse
import json
import os
import sys
import io
from datetime import date

if sys.platform == 'win32' and sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except (AttributeError, io.UnsupportedOperation):
        pass

CONSTITUTION_TYPES = [
    '平和质', '气虚质', '阳虚质', '阴虚质', '痰湿质',
    '湿热质', '血瘀质', '气郁质', '特禀质',
]

TYPE_CODES = {
    '平和质': 'ping_he',
    '气虚质': 'qi_xu',
    '阳虚质': 'yang_xu',
    '阴虚质': 'yin_xu',
    '痰湿质': 'tan_shi',
    '湿热质': 'shi_re',
    '血瘀质': 'xue_yu',
    '气郁质': 'qi_yu',
    '特禀质': 'te_bing',
}

CODE_TO_TYPE = {v: k for k, v in TYPE_CODES.items()}

ALIASES = {
    # Chinese canonical
    **{name: name for name in CONSTITUTION_TYPES},
    # codes
    **CODE_TO_TYPE,
    # common English-ish aliases
    'balanced': '平和质', 'normal': '平和质', 'pinghe': '平和质',
    'qi_deficiency': '气虚质', 'qixu': '气虚质',
    'yang_deficiency': '阳虚质', 'yangxu': '阳虚质',
    'yin_deficiency': '阴虚质', 'yinxu': '阴虚质',
    'phlegm_dampness': '痰湿质', 'tanshi': '痰湿质',
    'damp_heat': '湿热质', 'shire': '湿热质',
    'blood_stasis': '血瘀质', 'xueyu': '血瘀质',
    'qi_stagnation': '气郁质', 'qiyu': '气郁质',
    'special_diathesis': '特禀质', 'tebing': '特禀质',
}

TYPE_DESCRIPTIONS = {
    '平和质': '阴阳气血调和，体态适中，面色红润，精力充沛，适应力较强。',
    '气虚质': '元气不足，易疲乏、气短懒言、自汗，卫表不固。',
    '阳虚质': '阳气不足，畏寒怕冷、手足不温，喜温饮食，脾肾阳虚倾向。',
    '阴虚质': '阴液亏少，口燥咽干、手足心热，易受燥热火邪影响。',
    '痰湿质': '痰湿凝聚，体形偏胖、口黏苔腻，脾运失健，湿邪易留。',
    '湿热质': '湿热内蕴，口苦口干、身重困倦，湿与热胶结。',
    '血瘀质': '血行不畅，肤色晦暗、易有瘀斑，寒凝或气滞可加重。',
    '气郁质': '气机郁滞，情志不畅、胸胁胀满、善太息，肝气郁结倾向。',
    '特禀质': '先天禀赋特异，易过敏，对风、燥、花粉、食物等较敏感。',
}

CARE_PRIORITIES = {
    '平和质': '平调阴阳，顺时作息，维持饮食、运动、情志均衡。',
    '气虚质': '益气健脾，固表护卫，避免过劳与久病耗气。',
    '阳虚质': '温阳散寒，健脾补肾，少食生冷，重视腰腹足部保暖。',
    '阴虚质': '滋阴润燥，清虚热，少辛辣熬夜，防火热燥邪伤津。',
    '痰湿质': '健脾化湿，少甜腻油腻，增加温和运动，防湿浊内停。',
    '湿热质': '清热化湿，饮食清淡，少辛辣酒酪，防湿热郁蒸。',
    '血瘀质': '行气活血，避寒保暖，规律运动，防寒凝气滞。',
    '气郁质': '疏肝理气，调畅情志，规律运动，避免长期压抑内耗。',
    '特禀质': '固表避敏，防风润燥，留意过敏诱因与环境变化。',
}

DEMO_INPUT = {
    'constitution_scores': {
        '平和质': 35,
        '气虚质': 50,
        '阳虚质': 78,
        '阴虚质': 25,
        '痰湿质': 30,
        '湿热质': 20,
        '血瘀质': 22,
        '气郁质': 28,
        '特禀质': 15,
    },
    'metadata': {
        'birth_date': '2003-04-19',
        'user_gender': 'unspecified',
        'notes': 'demo: 畏寒怕冷，手足不温，喜温饮食',
    }
}


def canonical_name(name):
    key = str(name).strip()
    return ALIASES.get(key, ALIASES.get(key.lower()))


def normalize_scores(raw_scores):
    if not isinstance(raw_scores, dict):
        raise ValueError('体质得分必须是 JSON 对象。')
    normalized = {name: 0.0 for name in CONSTITUTION_TYPES}
    seen = set()
    for key, value in raw_scores.items():
        name = canonical_name(key)
        if not name:
            raise ValueError(f'未知体质类型: {key}')
        try:
            score = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f'{key} 的得分必须是数字，当前: {value}') from exc
        if score < 0 or score > 100:
            raise ValueError(f'{key} 的得分必须在 0-100 之间，当前: {score}')
        normalized[name] = round(score, 2)
        seen.add(name)
    return normalized, sorted(seen)


def classify_score(score):
    if score >= 60:
        return '是'
    if score >= 40:
        return '倾向是'
    return '否'


def choose_primary(scores):
    biased_types = [name for name in CONSTITUTION_TYPES if name != '平和质']
    yes_biased = [name for name in biased_types if scores[name] >= 60]
    if yes_biased:
        return max(yes_biased, key=lambda name: scores[name])
    if scores['平和质'] >= 60 and all(scores[name] < 40 for name in biased_types):
        return '平和质'
    tendency_biased = [name for name in biased_types if scores[name] >= 40]
    if tendency_biased:
        return max(tendency_biased, key=lambda name: scores[name])
    return max(CONSTITUTION_TYPES, key=lambda name: scores[name])


def assess_constitution(raw_scores, metadata=None, assessment_date=None, assessed_by='self-assessment'):
    scores, provided_types = normalize_scores(raw_scores)
    classifications = {
        name: {
            'score': scores[name],
            'result': classify_score(scores[name]),
            'code': TYPE_CODES[name],
            'description': TYPE_DESCRIPTIONS[name],
        }
        for name in CONSTITUTION_TYPES
    }

    primary = choose_primary(scores)
    primary_score = scores[primary]

    secondary_types = []
    secondary_scores = {}
    for name in CONSTITUTION_TYPES:
        if name == primary:
            continue
        if scores[name] >= 40:
            secondary_types.append(name)
            secondary_scores[name] = scores[name]

    yes_types = [name for name in CONSTITUTION_TYPES if scores[name] >= 60]
    tendency_types = [name for name in CONSTITUTION_TYPES if 40 <= scores[name] < 60]

    if primary == '平和质' and not secondary_types:
        constitution_type = '平和质'
        interpretation = '平和质为主，暂未见明显偏颇体质倾向。'
    elif yes_types:
        constitution_type = primary
        interpretation = f'{primary}为主。' + (f"兼夹/倾向：{'、'.join(secondary_types)}。" if secondary_types else '')
    elif tendency_types:
        constitution_type = f'{primary}倾向'
        interpretation = f'未见 ≥60 分的明确偏颇体质，当前以{primary}倾向为主。'
    else:
        constitution_type = f'{primary}相对较高'
        interpretation = '各体质得分均未达倾向阈值，按最高得分作为观察重点。'

    context = {
        'context_type': 'constitution_alignment',
        'version': '1.0.0',
        'constitution': {
            'primary_type': primary,
            'primary_code': TYPE_CODES[primary],
            'primary_score': primary_score,
            'secondary_types': secondary_types,
            'secondary_codes': [TYPE_CODES[name] for name in secondary_types],
            'secondary_scores': secondary_scores,
            'yes_types': yes_types,
            'tendency_types': tendency_types,
        },
        'instruction': '请基于以上体质评估结果，结合五运六气推算、天气对齐和地域修正，生成个体化调理建议；须区分理论分析与具体医疗建议，并附加免责声明。'
    }

    return {
        'constitution_type': constitution_type,
        'constitution_scores': scores,
        'primary_type': primary,
        'primary_code': TYPE_CODES[primary],
        'primary_score': primary_score,
        'secondary_types': secondary_types,
        'secondary_codes': [TYPE_CODES[name] for name in secondary_types],
        'secondary_scores': secondary_scores,
        'yes_types': yes_types,
        'tendency_types': tendency_types,
        'classifications': classifications,
        'interpretation': interpretation,
        'care_priority': CARE_PRIORITIES[primary],
        'questionnaire_version': 'WangQi-2009',
        'assessment_date': assessment_date or date.today().isoformat(),
        'assessed_by': assessed_by,
        'metadata': metadata or {},
        'provided_types': provided_types,
        'agent_context': context,
        'disclaimer': '本体质评估仅依据用户提供的量表得分进行分类，不能替代执业中医师面诊辨证。'
    }


def parse_input_payload(args):
    if args.demo:
        return DEMO_INPUT
    if args.scores:
        return json.loads(args.scores)
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            return json.load(f)
    raise ValueError('请提供 --scores、--file，或使用 --demo。')


def extract_scores_and_metadata(payload):
    if not isinstance(payload, dict):
        raise ValueError('输入必须是 JSON 对象。')
    if 'constitution_scores' in payload:
        scores = payload['constitution_scores']
    elif 'scores' in payload:
        scores = payload['scores']
    else:
        # 允许直接传九种体质得分对象
        scores = {k: v for k, v in payload.items() if canonical_name(k)}
        if not scores:
            raise ValueError('未找到 constitution_scores / scores，也未识别到体质得分键。')
    metadata = payload.get('metadata', {}) if isinstance(payload.get('metadata', {}), dict) else {}
    return scores, metadata


def format_markdown(result):
    lines = [
        '# 九种体质评估报告',
        '',
        '## 基本信息',
        f"- 问卷版本：{result['questionnaire_version']}",
        f"- 评估日期：{result['assessment_date']}",
        f"- 评估方式：{result['assessed_by']}",
        '',
        '## 判定结果',
        f"- 主要体质：{result['primary_type']}（{result['primary_score']} 分）",
        f"- 综合判定：{result['constitution_type']}",
        f"- 兼夹/倾向体质：{'、'.join(result['secondary_types']) if result['secondary_types'] else '无'}",
        f"- 解释：{result['interpretation']}",
        f"- 调理重点：{result['care_priority']}",
        '',
        '## 得分明细',
        '| 体质 | 得分 | 判定 |',
        '|------|------|------|',
    ]
    for name in CONSTITUTION_TYPES:
        item = result['classifications'][name]
        lines.append(f"| {name} | {item['score']} | {item['result']} |")
    lines.extend([
        '',
        '## Agent Context',
        '可将 JSON 输出中的 `agent_context` 传入天气对齐、运气病机分析或报告生成流程。',
        '',
        f"> {result['disclaimer']}",
    ])
    return '\n'.join(lines)


def template_payload():
    return {
        'constitution_scores': {name: 0 for name in CONSTITUTION_TYPES},
        'metadata': {
            'birth_date': '2003-04-19',
            'user_age': None,
            'user_gender': 'unspecified',
            'notes': ''
        }
    }


def build_arg_parser():
    parser = argparse.ArgumentParser(description='九种体质量表评估脚本')
    parser.add_argument('--scores', help='JSON 字符串，包含 constitution_scores 或直接九种体质得分')
    parser.add_argument('--file', help='JSON 文件路径')
    parser.add_argument('--demo', action='store_true', help='使用内置演示数据')
    parser.add_argument('--template', action='store_true', help='输出输入模板 JSON')
    parser.add_argument('--json', action='store_true', help='输出 JSON')
    parser.add_argument('--assessment-date', help='评估日期 YYYY-MM-DD；默认今天')
    parser.add_argument('--assessed-by', default='self-assessment', help='评估方式，默认 self-assessment')
    return parser


def main():
    parser = build_arg_parser()
    args = parser.parse_args()
    try:
        if args.template:
            sys.stdout.write(json.dumps(template_payload(), ensure_ascii=False, indent=2) + '\n')
            return
        payload = parse_input_payload(args)
        scores, metadata = extract_scores_and_metadata(payload)
        result = assess_constitution(
            scores,
            metadata=metadata,
            assessment_date=args.assessment_date,
            assessed_by=args.assessed_by,
        )
        if args.json:
            sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        else:
            sys.stdout.write(format_markdown(result) + '\n')
    except Exception as exc:
        sys.stderr.write(f'❌ 体质评估失败：{exc}\n')
        sys.exit(1)


if __name__ == '__main__':
    main()
