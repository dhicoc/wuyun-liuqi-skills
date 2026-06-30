#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
临床安全输出守卫

用于统一处理方药、针灸、剂量等高风险输出：
- 方药仅保留“方向/参考”，必须提示须由执业中医师辨证加减。
- 针灸/艾灸仅作参考，必须提示需由执业针灸师操作。
- 自动移除或替换具体剂量表达。

用法：
  python scripts/clinical_safety.py --demo
  python scripts/clinical_safety.py --text "附子10克，针刺关元" --json
"""
import argparse
import json
import re
import sys
import io

if sys.platform == 'win32' and sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except (AttributeError, io.UnsupportedOperation):
        pass

FORMULA_NOTICE = '⚠️ 方药仅作传统运气学参考方向，须由执业中医师辨证加减；请勿自行购药、配伍或服用。'
ACUPUNCTURE_NOTICE = '⚠️ 针灸/艾灸/穴位仅作传统理论参考，须由执业针灸师操作；请勿自行针刺或重灸。'
GENERAL_MEDICAL_NOTICE = '⚠️ 以上内容不构成医学诊断或治疗建议；如有不适，请咨询执业医师。'
DOSE_PLACEHOLDER = '{剂量须由执业医师辨证确定}'

# 常见剂量/服用频率表达。尽量保守：只替换数字 + 明确剂量单位。
DOSE_PATTERNS = [
    re.compile(r'\d+(?:\.\d+)?\s*(?:克|g|G|钱|两|毫克|mg|MG|毫升|ml|ML|升|L)(?:\b)?'),
    re.compile(r'每(?:日|天|次|服)\s*\d+(?:\.\d+)?\s*(?:次|服|剂|丸|片|粒|袋)'),
    re.compile(r'\d+(?:\.\d+)?\s*(?:次/日|次/天|日\d+次)'),
]

FORMULA_KEYWORDS = ['方', '汤', '丸', '散', '药', '草', '附子', '黄芪', '党参', '肉桂', '针灸', '艾灸']
ACUPUNCTURE_KEYWORDS = ['穴', '针', '灸', '关元', '命门', '肾俞', '足三里', '涌泉', 'CV', 'BL', 'ST', 'KI']


def redact_dosage(text):
    """替换具体剂量表达。"""
    if not text:
        return text
    result = str(text)
    for pattern in DOSE_PATTERNS:
        result = pattern.sub(DOSE_PLACEHOLDER, result)
    return result


def contains_dose(text):
    if not text:
        return False
    text = str(text)
    return any(pattern.search(text) for pattern in DOSE_PATTERNS)


def has_any_keyword(text, keywords):
    if not text:
        return False
    text = str(text)
    return any(keyword in text for keyword in keywords)


def ensure_suffix(text, suffix):
    if not text:
        return text
    text = str(text)
    return text if suffix in text else f'{text}\n{suffix}'


def sanitize_formula_text(text):
    """方药/药膳文本安全化：去剂量 + 附加安全提示。"""
    if not text:
        return text
    sanitized = redact_dosage(text)
    return ensure_suffix(sanitized, FORMULA_NOTICE)


def sanitize_acupuncture_points(points):
    """穴位列表安全化：每个点标注须执业操作。"""
    if not points:
        return points
    safe_points = []
    for point in points:
        item = redact_dosage(str(point))
        if '需由执业针灸师操作' not in item:
            item = f'{item}（需由执业针灸师操作）'
        safe_points.append(item)
    return safe_points


def build_safety_metadata(formula_text=None, acupuncture_points=None, extra_text=None):
    formula_detected = bool(formula_text) or has_any_keyword(extra_text, FORMULA_KEYWORDS)
    acupuncture_detected = bool(acupuncture_points) or has_any_keyword(extra_text, ACUPUNCTURE_KEYWORDS)
    return {
        'formula_detected': formula_detected,
        'acupuncture_detected': acupuncture_detected,
        'dose_detected': contains_dose(formula_text) or contains_dose(extra_text),
        'rules': [
            'MUST NOT 给出具体药物剂量',
            '方药仅作参考方向，须辨证加减',
            '针灸/艾灸/穴位须由执业针灸师操作',
            '不得替代执业医师诊断与治疗',
        ],
        'notices': [notice for notice, enabled in [
            (FORMULA_NOTICE, formula_detected),
            (ACUPUNCTURE_NOTICE, acupuncture_detected),
            (GENERAL_MEDICAL_NOTICE, formula_detected or acupuncture_detected),
        ] if enabled],
    }


def sanitize_current_adjustment(adjustment):
    """安全化 personal_yunqi_profile 中的 current_adjustment。"""
    if not adjustment:
        return adjustment, build_safety_metadata()
    safe = dict(adjustment)
    safe['dietary_herbs'] = sanitize_formula_text(safe.get('dietary_herbs', ''))
    safe['acupuncture_points'] = sanitize_acupuncture_points(safe.get('acupuncture_points', []))
    # preventive_measures 中也可能出现方药/艾灸方向，保留方向但加提示与去剂量。
    if safe.get('preventive_measures'):
        safe['preventive_measures'] = redact_dosage(safe['preventive_measures'])
        if has_any_keyword(safe['preventive_measures'], FORMULA_KEYWORDS):
            safe['preventive_measures'] = ensure_suffix(safe['preventive_measures'], FORMULA_NOTICE)
        if has_any_keyword(safe['preventive_measures'], ACUPUNCTURE_KEYWORDS):
            safe['preventive_measures'] = ensure_suffix(safe['preventive_measures'], ACUPUNCTURE_NOTICE)
    meta = build_safety_metadata(
        formula_text=safe.get('dietary_herbs'),
        acupuncture_points=safe.get('acupuncture_points'),
        extra_text=safe.get('preventive_measures'),
    )
    return safe, meta


def demo_payload():
    text = '附子10克，肉桂3g，每日2次，针刺关元、足三里。'
    return {
        'input': text,
        'sanitized': sanitize_formula_text(text),
        'acupuncture_points': sanitize_acupuncture_points(['关元（CV4）', '足三里（ST36）']),
        'metadata': build_safety_metadata(formula_text=text, acupuncture_points=['关元']),
    }


def main():
    parser = argparse.ArgumentParser(description='临床安全输出守卫')
    parser.add_argument('--text', help='待安全化文本')
    parser.add_argument('--demo', action='store_true', help='输出示例')
    parser.add_argument('--json', action='store_true', help='输出 JSON')
    args = parser.parse_args()

    if args.demo:
        result = demo_payload()
    else:
        text = args.text or ''
        result = {
            'input': text,
            'sanitized': sanitize_formula_text(text),
            'dose_detected': contains_dose(text),
            'metadata': build_safety_metadata(formula_text=text),
        }

    if args.json:
        sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    else:
        sys.stdout.write(result.get('sanitized', '') + '\n')


if __name__ == '__main__':
    main()
