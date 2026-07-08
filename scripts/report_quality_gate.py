#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告质量门禁

用于强化临床版报告免责声明、检测具体剂量、检测急症/严重症状提醒，并支持快照测试。

用法：
  python scripts/report_quality_gate.py --file report.md --audience practitioner
  python scripts/report_quality_gate.py --file report.md --snapshot reports/snapshots/practitioner.md
  python scripts/report_quality_gate.py --demo --json
"""
import argparse
import json
import os
import re
import sys

from _common import setup_environment
setup_environment(add_lib=False)

DISCLAIMER_REQUIRED = [
    '免责声明',
    '仅供参考',
    '非现代医学诊断标准',
    '执业中医师辨证论治',
    '请勿据此自行用药或针灸',
]
FORMULA_REQUIRED = ['方药仅作', '辨证加减', '请勿自行']
ACUPUNCTURE_REQUIRED = ['针灸', '执业针灸师']
EMERGENCY_NOTICE = '⚠️ 急症提醒：若出现胸痛、呼吸困难、意识障碍、大出血、剧烈腹痛、高热不退等严重症状，请立即联系急救或前往正规医疗机构就诊。'
EMERGENCY_KEYWORDS = ['胸痛', '呼吸困难', '意识障碍', '昏迷', '大出血', '咯血', '剧烈腹痛', '高热不退', '抽搐', '中风', '偏瘫']
DOSE_PATTERNS = [
    re.compile(r'\d+(?:\.\d+)?\s*(?:克|g|G|钱|两|毫克|mg|MG|毫升|ml|ML|升|L)(?:\b)?'),
    re.compile(r'每(?:日|天|次|服)\s*\d+(?:\.\d+)?\s*(?:次|服|剂|丸|片|粒|袋)'),
]


def read_text(path):
    for enc in ('utf-8', 'utf-8-sig', 'utf-16'):
        try:
            with open(path, 'r', encoding=enc) as f:
                return f.read()
        except Exception:
            continue
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()


def check_report(text, audience='student'):
    issues = []
    warnings = []
    for token in DISCLAIMER_REQUIRED:
        if token not in text:
            issues.append(f'缺少免责声明要素：{token}')

    if audience == 'practitioner':
        # 临床版更严格：必须明确“须辨证/勿自行用药或针灸”
        for token in ['具体诊疗', '辨证论治', '请勿据此自行用药或针灸']:
            if token not in text:
                issues.append(f'临床版缺少严格免责措辞：{token}')

    if any(k in text for k in ['方药', '方剂', '汤', '丸', '散']):
        if not any(token in text for token in FORMULA_REQUIRED):
            warnings.append('报告涉及方药，但未见完整“方药仅作参考/须辨证/请勿自行”提示。')

    if any(k in text for k in ['针灸', '穴位', '艾灸', '针刺']):
        if not all(token in text for token in ACUPUNCTURE_REQUIRED):
            warnings.append('报告涉及针灸/穴位，但未见“执业针灸师”操作提示。')

    dose_matches = []
    for pattern in DOSE_PATTERNS:
        dose_matches.extend(pattern.findall(text))
    if dose_matches:
        issues.append(f'发现疑似具体剂量表达：{dose_matches[:5]}')

    emergency_hits = [k for k in EMERGENCY_KEYWORDS if k in text]
    if emergency_hits and ('急症提醒' not in text and '立即' not in text):
        issues.append(f'检测到严重症状关键词但缺少急症提醒：{emergency_hits}')

    return {
        'passed': not issues,
        'issues': issues,
        'warnings': warnings,
        'emergency_hits': emergency_hits,
        'dose_detected': bool(dose_matches),
    }


def snapshot_check(text, snapshot_path, update=False):
    if update or not os.path.exists(snapshot_path):
        os.makedirs(os.path.dirname(snapshot_path), exist_ok=True)
        with open(snapshot_path, 'w', encoding='utf-8') as f:
            f.write(text)
        return {'snapshot': 'updated', 'passed': True}
    expected = read_text(snapshot_path)
    return {'snapshot': 'matched' if expected == text else 'mismatch', 'passed': expected == text}


def demo_text():
    return '# 临床版报告\n\n方药方向：温阳化湿。\n针灸参考：关元。\n\n⚠️ 免责声明：以上分析基于中医运气学说理论推算，仅供参考。运气学说非现代医学诊断标准，具体诊疗须由执业中医师辨证论治。请勿据此自行用药或针灸。\n\n⚠️ 方药仅作传统运气学参考方向，须由执业中医师辨证加减；请勿自行购药、配伍或服用。\n⚠️ 针灸/艾灸/穴位仅作传统理论参考，须由执业针灸师操作；请勿自行针刺或重灸。\n'


def main():
    parser = argparse.ArgumentParser(description='报告质量门禁')
    parser.add_argument('--file', help='报告文件路径')
    parser.add_argument('--audience', default='student', choices=['student', 'practitioner', 'researcher'])
    parser.add_argument('--snapshot', help='快照文件路径')
    parser.add_argument('--update-snapshot', action='store_true')
    parser.add_argument('--demo', action='store_true')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    if args.demo:
        text = demo_text()
    elif args.file:
        text = read_text(args.file)
    else:
        text = sys.stdin.read()

    result = check_report(text, audience=args.audience)
    if args.snapshot:
        snap = snapshot_check(text, args.snapshot, update=args.update_snapshot)
        result['snapshot'] = snap
        if not snap['passed']:
            result['passed'] = False
            result['issues'].append(f"报告快照不匹配：{snap['snapshot']}")

    if args.json:
        sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    else:
        if result['passed']:
            print('✅ 报告质量门禁通过')
        else:
            print('❌ 报告质量门禁失败')
            for issue in result['issues']:
                print(f'- {issue}')
        for warning in result['warnings']:
            print(f'⚠️ {warning}')
    sys.exit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
