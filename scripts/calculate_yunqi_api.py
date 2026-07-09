#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五运六气统一计算接口 (Step 1: 强规则底层计算工具)

核心函数: calculate_yunqi_api(date_str)
- 以大寒为年界，精确判断运气年份
- 返回标准化 JSON，可供 LLM Agent 直接解析
- 日干支由 lunar-python 精确计算

用法:
  python calculate_yunqi_api.py                  # 默认今天
  python calculate_yunqi_api.py today --summary
  python calculate_yunqi_api.py 2026-06-27 --json
  python calculate_yunqi_api.py 2026-01-15 --json  # 测试大寒边界

依赖: lunar-python (pip install lunar-python)
"""
from __future__ import annotations

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import date
from typing import Any, Dict, List, Optional, Union

from _common import setup_environment, color, highlight_key, RED, YELLOW, GREEN, CYAN, RESET, BOLD
setup_environment()  # 处理 UTF-8 + lib 路径

# 自进化自动记录（可选关闭）
try:
    from self_evolve import log_usage
    AUTO_LOG = True
except Exception:
    AUTO_LOG = False

from yunqi_data import (
    TIANGAN, DIZHI, DIZHI_SHENGXIAO, TIANGAN_HUAYUN, TIANGAN_YINYANG,
    DIZHI_HUAQI_SITIAN, SITIAN_ZAIQUAN_PAIR, LIUQI_WUXING, LIUQI_PINYIN,
    WUXING, WUYUN_STEP, ZHUQI_STEPS, KEQI_CYCLE,
    SUIYUN_CODE, SUIYUN_EN, QI_STEP_NAMES,
    get_ganzhi, get_sexagenary_index, get_dayun, is_taiguo,
    get_sitian, get_zaiquan, get_keqi_six_steps, get_zhuqi_six_steps,
    get_zhuyun_five_steps, get_keyun_five_steps,
    kezhujialin_relation, check_tianfu, check_suihui, check_pingqi,
    get_yunqi_year, get_current_qi_step, get_day_ganzhi,
    get_suiyun_code, get_kezhujialin_detail, get_jieqi_date,
    generate_summary, generate_current_step_focus,
)


def _resolve_date(date_input: Optional[Union[str, date]] = None) -> str:
    """
    UX 优化：支持 'today'、'今天'、None（默认今天）、或标准 YYYY-MM-DD。
    返回标准 YYYY-MM-DD 字符串。
    """
    if date_input is None:
        return date.today().isoformat()
    # datetime.date 及其子类（含 datetime）
    if isinstance(date_input, date):
        return date_input.isoformat()[:10]

    s = str(date_input).strip().lower()
    if s in ("today", "今天", "now", "当前", ""):
        return date.today().isoformat()

    # 否则假定是标准日期，让下游 _parse_date 做校验
    return str(date_input).strip()


def calculate_yunqi_api(date_str: Optional[Union[str, date]] = None) -> Dict[str, Any]:
    """
    五运六气统一计算接口
    
    参数: date_str - "YYYY-MM-DD" 格式日期字符串，支持 "today" / "今天" / None
    返回: 标准化 JSON 字典，包含:
      - year_gz: 年干支
      - day_gz: 日干支
      - sui_yun: 岁运 (name, status, code, tiangan)
      - si_tian: 司天
      - zai_quan: 在泉
      - current_step: 当前步位 (step_number, name, zhu_qi, ke_qi, relation)
      - tong_hua: 运气同化 (tianfu, suihui, taiyi_tianfu, pingqi)
      - zhu_yun: 主运五步
      - ke_yun: 客运五步
      - ke_qi_six_steps: 客气六步
      - ke_zhu_jia_lin: 客主加临六步分析
      - jieqi_dates: 六步节气边界日期
    """
    date_str = _resolve_date(date_str)

    # P1-3: 输入校验
    if not date_str or not isinstance(date_str, str):
        raise ValueError("date_str 必须是非空字符串，格式 YYYY-MM-DD")
    
    # 1. 确定运气年份 (大寒定年)
    yq_year = get_yunqi_year(date_str)
    
    # 2. 基本干支推算
    tg, dz = get_ganzhi(yq_year)
    idx = get_sexagenary_index(yq_year)
    sx = DIZHI_SHENGXIAO[dz]
    
    # 3. 日干支
    day_gz = get_day_ganzhi(date_str)
    
    # 4. 岁运
    dayun, dayun_tg = get_dayun(yq_year)
    taiguo = is_taiguo(yq_year)
    suiyun_code = get_suiyun_code(yq_year)
    
    # 5. 司天在泉
    sitian = get_sitian(yq_year)
    zaiquan = get_zaiquan(yq_year)
    
    # 6. 当前步位
    step_num, step_name, step_start, step_end = get_current_qi_step(date_str)
    step_detail = get_kezhujialin_detail(yq_year, step_num)
    
    # 7. 运气同化
    tianfu = check_tianfu(yq_year)
    suihui = check_suihui(yq_year)
    taiyi_tianfu = tianfu and suihui
    pingqi = check_pingqi(yq_year)
    
    # 8. 主运五步
    zhuyun_steps = get_zhuyun_five_steps(yq_year)
    zhu_yun = [
        {'step': s, 'element': e, 'tai_shao': ts}
        for s, e, ts in zhuyun_steps
    ]
    
    # 9. 客运五步
    keyun_steps = get_keyun_five_steps(yq_year)
    ke_yun = [
        {'step': s, 'element': e, 'tai_shao': ts}
        for s, e, ts in keyun_steps
    ]
    
    # 10. 客气六步
    keqi_steps = get_keqi_six_steps(yq_year)
    ke_qi_six = [
        {
            'step': s,
            'ke_qi': qi,
            'is_sitian': is_st,
            'is_zaiquan': is_zq,
        }
        for s, qi, is_st, is_zq in keqi_steps
    ]
    
    # 11. 客主加临六步
    ke_zhu_jia_lin = []
    for s in range(1, 7):
        detail = get_kezhujialin_detail(yq_year, s)
        ke_zhu_jia_lin.append(detail)
    
    # 12. 节气日期
    jieqi_dates = {}
    for jq_name in ['大寒', '春分', '小满', '大暑', '秋分', '小雪']:
        y, m, d = get_jieqi_date(yq_year, jq_name)
        jieqi_dates[jq_name] = f"{y}-{m:02d}-{d:02d}"
    next_y, next_m, next_d = get_jieqi_date(yq_year + 1, '大寒')
    jieqi_dates['大寒(终)'] = f"{next_y}-{next_m:02d}-{next_d:02d}"
    
    # 六气缩写 pinyin（无 xianghuo/junhuo/fengmu 等后缀，与 asset3 客主加临 key 格式匹配）
    liuqi_pinyin_short = {k: v.split('_')[0] for k, v in LIUQI_PINYIN.items()}
    
    # 构建标准化输出
    result = {
        'date': date_str,
        'yunqi_year': yq_year,
        'year_gz': f'{tg}{dz}',
        'year_gan': tg,
        'year_zhi': dz,
        'sexagenary_index': idx,
        'shengxiao': sx,
        'day_gz': day_gz,
        'sui_yun': {
            'name': f'{dayun}运',
            'element': dayun,
            'status': '太过' if taiguo else '不及',
            'code': suiyun_code,
            'tiangan': dayun_tg,
        },
        'si_tian': sitian,
        'zai_quan': zaiquan,
        'current_step': {
            'step_number': step_num,
            'name': step_name,
            'zhu_qi': step_detail['zhu_qi'],
            'ke_qi': step_detail['ke_qi'],
            'relation': step_detail['relation'],
            'shun_ni': step_detail['shun_ni'],
            'keqi_is_sitian': step_detail['keqi_is_sitian'],
            'keqi_is_zaiquan': step_detail['keqi_is_zaiquan'],
            'date_range': {
                'start': f"{step_start[0]}-{step_start[1]:02d}-{step_start[2]:02d}",
                'end': f"{step_end[0]}-{step_end[1]:02d}-{step_end[2]:02d}",
            },
        },
        'tong_hua': {
            'tianfu': tianfu,
            'suihui': suihui,
            'taiyi_tianfu': taiyi_tianfu,
            'pingqi': pingqi,
        },
        'zhu_yun': zhu_yun,
        'ke_yun': ke_yun,
        'ke_qi_six_steps': ke_qi_six,
        'ke_zhu_jia_lin': ke_zhu_jia_lin,
        'jieqi_dates': jieqi_dates,
        # RAG 检索键
        'rag_keys': {
            'suiyun': suiyun_code,
            'sitian': f'{LIUQI_PINYIN[sitian]}_sitian',
            'zaiquan': f'{LIUQI_PINYIN[zaiquan]}_zaiquan',
            'current_step': f'zhu_{liuqi_pinyin_short[step_detail["zhu_qi"]]}_ke_{liuqi_pinyin_short[step_detail["ke_qi"]]}',
        },
    }
    
    return result


def format_text(result: Dict[str, Any]) -> str:
    """格式化为可读文本 (带轻量颜色高亮)"""
    sui_status = result['sui_yun']['status']
    status_color = RED if sui_status == '太过' else YELLOW
    sui_line = f"【岁运】{result['sui_yun']['name']}{color(sui_status, status_color)} (code: {result['sui_yun']['code']})"

    lines = [
        f"日期: {result['date']}",
        f"运气年: {result['yunqi_year']}年 ({result['year_gz']})",
        f"六十甲子: 第{result['sexagenary_index']}甲子 | 生肖: {result['shengxiao']}",
        f"日干支: {result['day_gz'] or '未安装lunar-python，无法计算'}",
        "",
        highlight_key(sui_line),
        f"【司天】{result['si_tian']}",
        f"【在泉】{result['zai_quan']}",
        "",
        f"【当前步位】{result['current_step']['name']}",
        f"  主气: {result['current_step']['zhu_qi']}",
        f"  客气: {result['current_step']['ke_qi']}",
        f"  关系: {highlight_key(result['current_step']['relation'] + ' → ' + result['current_step']['shun_ni'])}",
    ]
    
    th = result['tong_hua']
    th_parts = []
    if th['tianfu']:
        th_parts.append('天符')
    if th['suihui']:
        th_parts.append('岁会')
    if th['taiyi_tianfu']:
        th_parts.append('太乙天符')
    if th['pingqi']:
        th_parts.append('平气')
    if th_parts:
        lines.append(f"【运气同化】{'、'.join(th_parts)}")
    else:
        lines.append("【运气同化】无特殊同化")
    
    lines.append("")
    lines.append("【主运五步】")
    for s in result['zhu_yun']:
        lines.append(f"  {s['step']}. {s['tai_shao']}{s['element']}运")
    
    lines.append("【客运五步】")
    for s in result['ke_yun']:
        lines.append(f"  {s['step']}. {s['tai_shao']}{s['element']}运")
    
    lines.append("")
    lines.append("【客气六步】")
    for s in result['ke_qi_six_steps']:
        tag = ''
        if s['is_sitian']:
            tag = ' ← 司天'
        elif s['is_zaiquan']:
            tag = ' ← 在泉'
        lines.append(f"  {s['step']}. {s['ke_qi']}{tag}")
    
    lines.append("")
    lines.append("【客主加临】")
    xiangde = 0
    buxiangde = 0
    for s in result['ke_zhu_jia_lin']:
        if s['shun_ni'].startswith('相得'):
            xiangde += 1
        else:
            buxiangde += 1
        tag = ''
        if s['keqi_is_sitian']:
            tag = ' (司天)'
        elif s['keqi_is_zaiquan']:
            tag = ' (在泉)'
        lines.append(f"  {s['step_number']}. 主{s['zhu_qi']} 客{s['ke_qi']}{tag} → {s['relation']} {s['shun_ni']}")
    lines.append(f"  相得: {xiangde}步 | 不相得: {buxiangde}步")
    
    lines.append("")
    lines.append("【RAG检索键】")
    for k, v in result['rag_keys'].items():
        lines.append(f"  {k}: {v}")

    # UX P0-5 + P1-3: 下一步 + 思想伙伴引导问题
    d = result.get('date', 'today')
    lines.append("")
    lines.append("下一步建议：")
    lines.append(f"  • 聚焦当前步位：  python scripts/calculate_yunqi_api.py {d} --focus current-step")
    lines.append(f"  • 学生版报告：    python scripts/calculate_yunqi_api.py {d} --report-type student")
    lines.append(f"  • 完整演示：      python scripts/demo_full_chain.py {d}")
    lines.append("")
    lines.append("思想伙伴问题（可回复继续对话）：")
    lines.append("  • 你对这个格局的‘中和’或‘偏盛’部分怎么理解？")
    lines.append("  • 想听听这个运气对养生或生活方式的思想启发吗？")
    
    return '\n'.join(lines)


def run_yunqi_report(
    yunqi_year: Union[int, str],
    audience: str = "student",
    as_json: bool = False,
) -> str:
    """生成年度综合报告（直接 import，避免 subprocess）。"""
    from _common import add_scripts_dir_to_path
    add_scripts_dir_to_path()
    import yunqi_report as yr
    from yunqi_data import (
        get_ganzhi, get_dayun, get_sitian, get_zaiquan,
        is_taiguo, check_tianfu, check_suihui, check_pingqi,
    )

    report = yr.generate_report(int(yunqi_year), audience, advanced=None)
    if not as_json:
        return report + ('\n' if not report.endswith('\n') else '')

    year = int(yunqi_year)
    tg, dz = get_ganzhi(year)
    dayun, _ = get_dayun(year)
    sitian = get_sitian(year)
    zaiquan = get_zaiquan(year)
    payload = {
        'year': year,
        'ganzhi': f'{tg}{dz}',
        'dayun': f'{dayun}运{"太过" if is_taiguo(year) else "不及"}',
        'sitian': sitian,
        'zaiquan': zaiquan,
        'tianfu': check_tianfu(year),
        'suihui': check_suihui(year),
        'pingqi': check_pingqi(year),
        'audience': audience,
        'has_advanced_alignment': False,
        'report': report,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + '\n'


def run_visualize(date_str: str) -> str:
    """生成 ASCII 可视化（直接 import）。"""
    from _common import add_scripts_dir_to_path
    add_scripts_dir_to_path()
    import visualize_yunqi as viz
    data = viz.get_result(date_str)
    output = viz.visualize(data)
    return output + ('\n' if not output.endswith('\n') else '')


def run_html_report(date_str: str) -> str:
    """生成 HTML 报告（直接 import）。"""
    from _common import add_scripts_dir_to_path
    add_scripts_dir_to_path()
    import generate_html_report as ghr
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'reports', 'generated', f'wuyun-liuqi-report-{date_str}.html',
    )
    return ghr.write_html_report(date_str, output_path)


def load_terminology() -> Dict[str, Any]:
    """加载术语解释库"""
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rag-knowledge-base', 'terminology.json')
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return {entry['term']: entry for entry in data.get('entries', [])}
    except Exception:
        return {}


def generate_explanation_output(result: Dict[str, Any]) -> str:
    """生成带术语解释的输出"""
    terminology = load_terminology()
    if not terminology:
        return "术语解释库暂不可用，请检查 rag-knowledge-base/terminology.json 是否存在。\n"

    # 需要解释的术语
    terms_to_explain = [
        ('岁运', result['sui_yun']['name'] + result['sui_yun']['status']),
        ('司天', result['si_tian']),
        ('在泉', result['zai_quan']),
        ('主气', result['current_step']['zhu_qi']),
        ('客气', result['current_step']['ke_qi']),
        ('客主加临', result['current_step']['relation']),
    ]

    lines = [
        f"日期: {result['date']}",
        f"运气年: {result['yunqi_year']}年 ({result['year_gz']})",
        "",
        "【带解释的运气格局】",
    ]

    for term, context in terms_to_explain:
        entry = terminology.get(term)
        if entry:
            lines.append(f"• {term}（{context}）：{entry['explanation']}")
        else:
            lines.append(f"• {term}（{context}）：暂无解释")

    # 六气术语解释
    for qi_name in set([result['si_tian'], result['zai_quan'], result['current_step']['zhu_qi'], result['current_step']['ke_qi']]):
        entry = terminology.get(qi_name)
        if entry:
            lines.append(f"• {qi_name}：{entry['explanation']}")

    # 添加其他相关术语
    extra_terms = ['太过', '不及', '平气', '天符', '岁会', '大寒']
    for term in extra_terms:
        if term in str(result) or (term == '平气' and result['tong_hua']['pingqi']):
            entry = terminology.get(term)
            if entry:
                lines.append(f"• {term}：{entry['explanation']}")

    lines.append("")
    lines.append("术语解释基于《黄帝内经·素问》七篇大论及中医基础理论。")
    return '\n'.join(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='calculate_yunqi_api.py',
        description='五运六气统一计算接口（主推荐入口）。支持日期推算、RAG key 生成、报告、摘要等。',
        epilog='''示例:
  python calculate_yunqi_api.py today --summary
  python calculate_yunqi_api.py 2026-06-27 --json
  python calculate_yunqi_api.py --report-type practitioner
  python calculate_yunqi_api.py today --focus current-step
  python calculate_yunqi_api.py 2026-01-15 --html reports/generated/report.html

日期支持: YYYY-MM-DD、today、今天（默认今天）
更多用法见 README 和 SKILL.md''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('date', nargs='?', default='today',
                        help='日期，格式 YYYY-MM-DD，或 today / 今天（默认今天）')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')
    parser.add_argument('--summary', action='store_true', help='输出自然语言摘要')
    parser.add_argument('--visual', action='store_true', help='生成 ASCII 可视化图')
    parser.add_argument('--html', action='store_true', help='生成 HTML 报告')
    parser.add_argument('--explain', action='store_true', help='带术语解释的输出')
    parser.add_argument('--focus', choices=['current-step'], default=None,
                        help='聚焦当前步位分析')
    parser.add_argument('--report-type', choices=['student', 'practitioner', 'researcher'],
                        default=None, help='生成指定受众的综合报告')
    parser.add_argument('--level', choices=['simple', 'standard', 'deep'], default='standard',
                        help='解释深度：simple（简化思想版）/ standard / deep（哲学深入）')
    parser.add_argument('--explain-concept', help='解释特定概念（如 天人合一、天符），返回哲学+现代+示例')
    parser.add_argument('--export', choices=['summary', 'cards', 'pdf', 'all'], default=None,
                        help='导出思想摘要/卡片集/PDF（专注理解）：summary | cards | pdf | all')

    args = parser.parse_args()

    date_str = _resolve_date(args.date)

    if args.explain_concept:
        try:
            from yunqi_report import explain_concept
            print(explain_concept(args.explain_concept))
            sys.exit(0)
        except Exception as e:
            print(f"概念解释错误: {e}")
            sys.exit(2)

    if args.export:
        try:
            # 直接调用导出逻辑（避免 sys.argv 污染）
            import export_thought as et
            date_to_use = args.date or 'today'
            # 构造内部数据并生成
            data = et.get_year_and_data(date_to_use)
            out_dir = 'reports/generated/'
            year_str = str(data.get('year', 'unknown'))
            if args.export in ('summary', 'all'):
                summary = et.generate_thought_summary(data)
                Path(out_dir).mkdir(parents=True, exist_ok=True)
                (Path(out_dir) / f'thought_summary_{year_str}.md').write_text(summary, encoding='utf-8')
                print(f'✅ 思想摘要已导出到 {out_dir}')
            if args.export in ('cards', 'all'):
                anki, cards_md = et.generate_cards(data)
                Path(out_dir).mkdir(parents=True, exist_ok=True)
                (Path(out_dir) / f'thought_cards_{year_str}.anki.tsv').write_text(anki, encoding='utf-8')
                (Path(out_dir) / f'thought_cards_{year_str}.md').write_text(cards_md, encoding='utf-8')
                print(f'✅ 卡片集已导出')
            if args.export in ('pdf', 'all'):
                summary = et.generate_thought_summary(data)
                msg = et.generate_pdf(summary, f'{out_dir}thought_{year_str}.pdf')
                print(msg)
            sys.exit(0)
        except Exception as e:
            print(f'导出失败: {e}')
            print('提示：可直接运行 python scripts/export_thought.py today --format all')
            sys.exit(2)

    try:
        result = calculate_yunqi_api(date_str)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(2)

    # 自进化：自动记录使用（支持思想概念）
    if AUTO_LOG:
        concepts = []
        if args.explain_concept:
            concepts.append(args.explain_concept)
        if args.level and args.level != "standard":
            concepts.append(f"level_{args.level}")
        try:
            log_usage(date_str, list(result.get("rag_keys", {}).values()) if result.get("rag_keys") else [], source="cli", concepts=concepts or None)
        except Exception:
            pass  # 不影响主流程

    # 友好提示（默认今天时）
    if args.date in (None, 'today', '今天') and not args.json:
        print(f"（已默认使用今天日期: {result['date']}）\n")

    if args.html:
        output = run_html_report(date_str)
        sys.stdout.write(output)
    elif args.focus:
        if args.focus == 'current-step':
            sys.stdout.write(generate_current_step_focus(result) + '\n')
        else:
            print(f"不支持的聚焦模式: {args.focus}")
            sys.exit(1)
    elif args.visual:
        output = run_visualize(date_str)
        sys.stdout.write(output)
    elif args.report_type:
        as_json = args.json
        output = run_yunqi_report(result['yunqi_year'], args.report_type, as_json)
        sys.stdout.write(output)
    elif args.explain:
        sys.stdout.write(generate_explanation_output(result) + '\n')
    elif args.json:
        output = json.dumps(result, ensure_ascii=False, indent=2)
        sys.stdout.write(output + '\n')
    elif args.summary:
        summary = highlight_key(generate_summary(result))
        sys.stdout.write(summary + '\n')
    else:
        sys.stdout.write(format_text(result) + '\n')
    sys.stdout.flush()
