#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""全量回归冒烟测试：覆盖主要 CLI 功能和流程。"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
ENV = os.environ.copy()
ENV['PYTHONIOENCODING'] = 'utf-8'

passed = 0
failed = 0


def run(name, args, check=None, max_output=260):
    global passed, failed
    try:
        result = subprocess.run(
            args,
            cwd=ROOT,
            env=ENV,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=90,
        )
        output = (result.stdout or '') + (result.stderr or '')
        ok = result.returncode == 0
        if ok and check:
            ok = bool(check(result, output))
        if ok:
            passed += 1
            print(f'[OK] {name}')
        else:
            failed += 1
            print(f'[FAIL] {name} (code={result.returncode})')
            print(output[:max_output])
        return result, output
    except Exception as exc:
        failed += 1
        print(f'[FAIL] {name}: {exc}')
        return None, ''


def has(text):
    return lambda result, output: text in output


def json_has(keys):
    def check(result, output):
        data = json.loads(result.stdout)
        cur = data
        for key in keys:
            cur = cur[key]
        return cur is not None
    return check


def _save_fixture(rel_path, content):
    """把命令 stdout 落盘为测试 fixture，供后续步骤复用。返回是否写入成功。"""
    path = ROOT / rel_path
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return True
    except Exception:
        return False


def main():
    global passed, failed
    print('=== CLI 全量功能测试 ===')

    # 单项推算脚本
    run('ganzhi_calc text', [PY, 'scripts/ganzhi_calc.py', '2026'], has('丙午'))
    run('ganzhi_calc json', [PY, 'scripts/ganzhi_calc.py', '2026', '--json'], json_has(['干支']))
    run('dayun_calc text', [PY, 'scripts/dayun_calc.py', '2026'], has('水运'))
    run('dayun_calc json', [PY, 'scripts/dayun_calc.py', '2026', '--json'], json_has(['大运']))
    run('keyun_calc text', [PY, 'scripts/keyun_calc.py', '2026'], has('客运初运'))
    run('keyun_calc json', [PY, 'scripts/keyun_calc.py', '2026', '--json'], json_has(['五步']))
    run('liuqi_calc text', [PY, 'scripts/liuqi_calc.py', '2026'], has('少阴君火'))
    run('liuqi_calc json', [PY, 'scripts/liuqi_calc.py', '2026', '--json'], json_has(['六步']))
    run('kezhujialin text', [PY, 'scripts/kezhujialin.py', '2026'], has('相得'))
    run('kezhujialin json', [PY, 'scripts/kezhujialin.py', '2026', '--json'], json_has(['六步']))

    # 统一 API 各模式
    run('calculate default', [PY, 'scripts/calculate_yunqi_api.py', '2026-06-29'], has('RAG检索键'))
    run('calculate --json', [PY, 'scripts/calculate_yunqi_api.py', '2026-06-29', '--json'], json_has(['rag_keys', 'current_step']))
    run('calculate --summary', [PY, 'scripts/calculate_yunqi_api.py', '2026-06-29', '--summary'], has('全年岁运'))
    run('calculate --focus current-step', [PY, 'scripts/calculate_yunqi_api.py', '2026-06-29', '--focus', 'current-step'], has('当前步位'))
    run('calculate --visual', [PY, 'scripts/calculate_yunqi_api.py', '2026-06-29', '--visual'], has('五运六气格局图'))
    run('calculate --explain', [PY, 'scripts/calculate_yunqi_api.py', '2026-06-29', '--explain'], has('带解释的运气格局'))
    run('calculate --html', [PY, 'scripts/calculate_yunqi_api.py', '2026-06-29', '--html'], has('HTML 报告已生成'))

    for audience in ['student', 'practitioner', 'researcher']:
        run(f'calculate --report-type {audience}', [PY, 'scripts/calculate_yunqi_api.py', '2026-06-29', '--report-type', audience], has('免责声明'))
        run(f'calculate --report-type {audience} --json', [PY, 'scripts/calculate_yunqi_api.py', '2026-06-29', '--report-type', audience, '--json'], json_has(['audience']))

    # 报告与可视化
    for audience in ['student', 'practitioner', 'researcher']:
        run(f'yunqi_report {audience}', [PY, 'scripts/yunqi_report.py', '2026', '--audience', audience], has('免责声明'))
        run(f'yunqi_report {audience} json', [PY, 'scripts/yunqi_report.py', '2026', '--audience', audience, '--json'], json_has(['report']))
    run('visualize_yunqi', [PY, 'scripts/visualize_yunqi.py', '2026-06-29'], has('六气步位推移'))
    run('generate_html_report', [PY, 'scripts/generate_html_report.py', '2026-06-29', 'reports/test-results/test-full.html'], has('HTML 报告已生成'))

    # 个人体质
    run('personal profile text', [PY, 'scripts/personal_yunqi_profile.py', '1990-05-20', '北京'], has('个人运气体质分析报告'))
    run('personal profile json', [PY, 'scripts/personal_yunqi_profile.py', '1990-05-20', '北京', '--json'], json_has(['birth_suiyun', 'code']))

    # 天气对齐（mock 模式避免 CI 依赖外网）
    run('constitution assessment demo text', [PY, 'scripts/constitution_assessment.py', '--demo'], has('九种体质评估报告'))
    run('constitution assessment demo json', [PY, 'scripts/constitution_assessment.py', '--demo', '--json'], json_has(['agent_context', 'constitution']))
    run('weather alignment mock text', [PY, 'scripts/weather_alignment.py', '2026-06-29', '--city', '杭州', '--mock'], has('天气对齐报告'))
    run('weather alignment mock json', [PY, 'scripts/weather_alignment.py', '2026-06-29', '--city', '杭州', '--mock', '--json'], json_has(['alignment', 'type']))
    run('weather constitution mock text', [PY, 'scripts/yunqi_weather_constitution.py', '2026-06-29', '--birth-date', '2003-04-19', '--city', '杭州', '--mock'], has('三维叠加报告'))
    run('weather constitution mock json', [PY, 'scripts/yunqi_weather_constitution.py', '2026-06-29', '--birth-date', '2003-04-19', '--city', '杭州', '--mock', '--json'], json_has(['combined_analysis', 'level']))
    run('advanced alignment mock text', [PY, 'scripts/advanced_alignment.py', '--date', '2026-06-29', '--birth-date', '2003-04-19', '--city', '杭州', '--constitution-demo', '--mock'], has('高级对齐综合报告'))
    run('advanced alignment mock json', [PY, 'scripts/advanced_alignment.py', '--date', '2026-06-29', '--birth-date', '2003-04-19', '--city', '杭州', '--constitution-demo', '--mock', '--json'], json_has(['advanced_synthesis', 'level']))

    # 报告融合：高级对齐 JSON 注入 yunqi_report
    run('generate advanced json fixture', [PY, 'scripts/advanced_alignment.py', '--date', '2026-06-29', '--birth-date', '2003-04-19', '--city', '杭州', '--constitution-demo', '--mock', '--json'], lambda r, o: (r.returncode == 0 and _save_fixture('reports/test-results/advanced-2026-06-29.json', r.stdout)))
    run('yunqi_report with advanced json', [PY, 'scripts/yunqi_report.py', '2026', '--audience', 'practitioner', '--advanced-json', 'reports/test-results/advanced-2026-06-29.json'], has('高级对齐'))
    run('yunqi_report with advanced json json', [PY, 'scripts/yunqi_report.py', '2026', '--audience', 'student', '--advanced-json', 'reports/test-results/advanced-2026-06-29.json', '--json'], json_has(['has_advanced_alignment']))

    # 报告融合：HTML 报告内置高级对齐章节
    def html_has_advanced(result, output):
        html_path = ROOT / 'reports/test-results/html-advanced-2026-06-29.html'
        return html_path.exists() and '高级对齐' in html_path.read_text(encoding='utf-8')
    run('generate_html_report with advanced', [PY, 'scripts/generate_html_report.py', '2026-06-29', 'reports/test-results/html-advanced-2026-06-29.html', '--with-advanced-alignment', '--birth-date', '2003-04-19', '--city', '杭州', '--constitution-demo', '--mock'], html_has_advanced)

    # ingest / validate / self-evolve
    run('ingest list categories', [PY, 'scripts/ingest_literature.py', '--list-categories'], has('classics'))
    run('validate single terminology', [PY, 'scripts/validate_knowledge_base.py', '--path', 'rag-knowledge-base/terminology.json'], has('校验通过'))
    run('self_evolve stats top_keys', [PY, 'scripts/self_evolve.py', 'stats', '--type', 'top_keys'], lambda r, o: True)
    run('self_evolve analyze blind_spots', [PY, 'scripts/self_evolve.py', 'analyze', '--type', 'blind_spots'], lambda r, o: True)
    run('self_evolve report', [PY, 'scripts/self_evolve.py', 'report'], has('自进化报告'))
    run('self_evolve monthly-report', [PY, 'scripts/self_evolve.py', 'monthly-report'], has('月度自进化报告'))

    # 全链路 demo
    run('demo_full_chain', [PY, 'scripts/demo_full_chain.py', '2026-06-29'], has('全链路演示完成'))

    # 术语库统计
    with open(ROOT / 'rag-knowledge-base' / 'terminology.json', encoding='utf-8') as f:
        terminology = json.load(f)
    if terminology.get('entry_count') == len(terminology.get('entries', [])) and terminology['entry_count'] >= 590:
        passed += 1
        print(f"[OK] terminology count {terminology['entry_count']}")
    else:
        failed += 1
        print('[FAIL] terminology count mismatch')

    print('=== 汇总 ===')
    print(f'通过: {passed}, 失败: {failed}')
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
