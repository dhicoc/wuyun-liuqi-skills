#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
README 数字一致性校验

自动统计仓库中的真实文件数，与 README.md / README_EN.md / SKILL.md 中声明的数字比对。
不一致则 CI 失败，防止数字滞后于代码。

用法：
    python scripts/check_readme_numbers.py
"""

import re
import os
import json
import glob
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def count_assets():
    """RAG asset JSON 文件数"""
    return len(list(ROOT.glob('rag-knowledge-base/asset*.json')))


def count_literature():
    """公版文献 .md 文件数（排除 README/corpus）"""
    files = [f for f in ROOT.glob('rag-knowledge-base/literature/*.md')
             if 'README' not in f.name and '_README' not in f.name]
    return len(files)


def count_guides():
    """蒸馏指南 .md 文件数"""
    return len(list(ROOT.glob('rag-knowledge-base/*_guide.md')))


def count_cases():
    """医案总条目数"""
    total = 0
    for f in ROOT.glob('rag-knowledge-base/asset*_cases.json'):
        d = json.load(open(f, encoding='utf-8'))
        total += len(d.get('entries', []))
    return total


def count_scripts():
    """Python 脚本数"""
    return len(list(ROOT.glob('scripts/*.py')))


def count_terminology():
    """术语库条目数"""
    f = ROOT / 'rag-knowledge-base' / 'terminology.json'
    d = json.load(open(f, encoding='utf-8'))
    if isinstance(d, list):
        return len(d)
    return len(d.get('entries', d.get('terms', [])))


def count_ci_tests():
    """CI 测试项数"""
    ci = ROOT / '.github' / 'workflows' / 'ci.yml'
    if not ci.exists():
        return 0
    return len(re.findall(r'^\s+- name:.*\n\s+run:', ci.read_text(encoding='utf-8'), re.MULTILINE))


def count_literature_chars():
    """公版文献总字数（万）"""
    total = 0
    for f in ROOT.glob('rag-knowledge-base/literature/*.md'):
        if 'README' in f.name or '_README' in f.name:
            continue
        total += len(f.read_text(encoding='utf-8'))
    return round(total / 10000, 1)


# 真实数字
ACTUAL = {
    'assets': count_assets(),
    'literature': count_literature(),
    'guides': count_guides(),
    'cases': count_cases(),
    'scripts': count_scripts(),
    'terminology': count_terminology(),
    'ci_tests': count_ci_tests(),
    'lit_chars': count_literature_chars(),
}


def check_file(filepath, checks):
    """检查单个文件中的数字是否与真实值一致"""
    if not filepath.exists():
        return []

    content = filepath.read_text(encoding='utf-8')
    errors = []

    for pattern, actual, label in checks:
        matches = re.findall(pattern, content)
        for m in matches:
            try:
                claimed = int(m)
                if claimed != actual:
                    errors.append(f'{filepath.name}: 声明 {label}={claimed}, 实际={actual}')
            except ValueError:
                pass

    return errors


def main():
    checks = [
        # (正则, 真实值, 标签)
        (r'(\d+)\s*个\s*RAG\s*asset', ACTUAL['assets'], 'asset 数'),
        (r'(\d+)\s*个\s*asset\s*JSON', ACTUAL['assets'], 'asset JSON 数'),
        (r'(\d+)\s*RAG\s*asset', ACTUAL['assets'], 'RAG asset 数'),
        (r'(\d+)\s*RAG\s*assets', ACTUAL['assets'], 'RAG assets 数'),
        (r'(\d+)\s*篇\s*公版文献', ACTUAL['literature'], '公版文献篇数'),
        (r'(\d+)\s*public-domain\s*texts', ACTUAL['literature'], 'public-domain texts'),
        (r'(\d+)\s*本\s*蒸馏指南', ACTUAL['guides'], '蒸馏指南数'),
        (r'(\d+)\s*distilled\s*guides', ACTUAL['guides'], 'distilled guides'),
        (r'(\d+)\s*条\s*真实医案', ACTUAL['cases'], '医案条数'),
        (r'(\d+)\s*real\s*cases', ACTUAL['cases'], 'real cases'),
        (r'(\d+)\s*个\s*脚本', ACTUAL['scripts'], '脚本数'),
        (r'(\d+)\s*scripts', ACTUAL['scripts'], 'scripts'),
        (r'(\d+)\s*条.*术语', ACTUAL['terminology'], '术语条数'),
    ]

    all_errors = []
    for fname in ['README.md', 'README_EN.md', 'SKILL.md']:
        fpath = ROOT / fname
        all_errors.extend(check_file(fpath, checks))

    # README_AI.md 只校验医案条数（其中措辞为「**N 条**临证真实医案」，
    # 现有通用正则因「临证」间隔不命中，故单独检查，避免其它数字误报）
    _ai = ROOT / 'README_AI.md'
    if _ai.exists():
        _ai_case_hits = re.findall(r'(\d+)\s*条\s*(?:临证\s*)?真实\s*医案', _ai.read_text(encoding='utf-8'))
        for m in _ai_case_hits:
            if int(m) != ACTUAL['cases']:
                all_errors.append(f'README_AI.md: 声明 医案条数={m}, 实际={ACTUAL["cases"]}')

    # 字数检查（万）
    for fname in ['README.md', 'SKILL.md']:
        fpath = ROOT / fname
        if not fpath.exists():
            continue
        content = fpath.read_text(encoding='utf-8')
        # 匹配 "XX.X 万字" 或 "XX.X万字"
        matches = re.findall(r'(\d+\.?\d*)\s*万字', content)
        for m in matches:
            claimed = float(m)
            if abs(claimed - ACTUAL['lit_chars']) > 5:  # 允许 5 万字误差
                all_errors.append(f'{fname}: 声明文献字数={m}万字, 实际={ACTUAL["lit_chars"]}万字')
        # 英文版用 K/M chars
        matches_en = re.findall(r'(\d+\.?\d*)\s*[KM]\s*chars', content)
        for m in matches_en:
            all_errors.append(f'{fname}: 英文字数标记需人工确认: {m}')

    # 输出结果
    print('=' * 50)
    print('  README 数字一致性校验')
    print('=' * 50)
    print()
    print(f'真实数字:')
    print(f'  asset:     {ACTUAL["assets"]}')
    print(f'  文献:      {ACTUAL["literature"]} 篇')
    print(f'  蒸馏指南:  {ACTUAL["guides"]} 本')
    print(f'  医案:      {ACTUAL["cases"]} 条')
    print(f'  脚本:      {ACTUAL["scripts"]} 个')
    print(f'  术语:      {ACTUAL["terminology"]} 条')
    print(f'  CI 测试:   {ACTUAL["ci_tests"]} 项')
    print(f'  文献字数:  {ACTUAL["lit_chars"]} 万字')
    print()

    if all_errors:
        print(f'❌ 发现 {len(all_errors)} 处不一致:')
        for e in all_errors:
            print(f'  - {e}')
        return 1
    else:
        print('✅ 全部数字一致')
        return 0


if __name__ == '__main__':
    sys.exit(main())
