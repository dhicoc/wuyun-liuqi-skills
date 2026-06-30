#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五运六气综合报告生成器
用法: python yunqi_report.py <年份> [--audience student|practitioner|researcher] [--json] [--advanced-json <高级对齐JSON文件>]
"""
import sys
import os
import io
import json

# Windows 终端默认编码可能不是 UTF-8，强制设置 stdout/stderr 编码
if sys.platform == 'win32' and sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except (AttributeError, io.UnsupportedOperation):
        pass

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib'))
from yunqi_data import (
    get_ganzhi, get_dayun, is_taiguo, get_sitian, get_zaiquan,
    get_keqi_six_steps, get_zhuqi_six_steps, get_zhuyun_five_steps,
    get_keyun_five_steps, check_tianfu, check_suihui, check_pingqi,
    kezhujialin_relation, ZHUQI_JIEQI, LIUQI_WUXING, LIUQI_YINYANG,
    TIANGAN_YINYANG, DIZHI_WUXING, DIZHI_SHENGXIAO,
    get_sexagenary_index,
)

DISCLAIMER = (
    "\n> ⚠️ 免责声明：以上分析基于中医运气学说理论推算，仅供参考。"
    "运气学说非现代医学诊断标准，具体诊疗须由执业中医师辨证论治。"
    "请勿据此自行用药或针灸。\n"
)


def build_advanced_alignment_section(advanced):
    """根据 advanced_alignment.py 的 JSON 输出构建报告章节。"""
    if not advanced:
        return ''
    synthesis = advanced.get('advanced_synthesis') or {}
    sections = []
    sections.append("## 高级对齐\n")
    sections.append(f"- **综合等级**: {synthesis.get('label', '')}（{synthesis.get('level', '')}）")
    sections.append(f"- **重点体质**: {'、'.join(synthesis.get('focus_constitutions') or []) or '未指定'}")
    sections.append(f"- **摘要**: {synthesis.get('summary', '')}")
    layers = synthesis.get('layers') or []
    sections.append(f"- **已启用层**: {'、'.join(layers) if layers else '仅基础运气'}")

    weather = advanced.get('weather_alignment')
    if weather:
        wq = weather.get('weather_qi') or {}
        al = weather.get('alignment') or {}
        sections.append(f"- **天气六气**: {wq.get('pattern', '')}（{al.get('label', '')}）")
        sections.append(f"- **天气调摄**: {al.get('care_principle', '')}")

    profile = advanced.get('personal_profile')
    if profile:
        names = [item.get('name') for item in profile.get('birth_constitutions') or []]
        sections.append(f"- **出生运气年**: {profile.get('birth_yunqi_year', '')}（{profile.get('birth_suiyun', {}).get('name', '')}）")
        sections.append(f"- **先天体质**: {'、'.join(names) if names else '未匹配'}")

    constitution = advanced.get('constitution_assessment')
    if constitution:
        sections.append(f"- **体质量表**: {constitution.get('primary_type', '')}（{constitution.get('primary_score', '')} 分）")
        sections.append(f"- **兼夹/倾向**: {'、'.join(constitution.get('secondary_types') or []) or '无'}")
        sections.append(f"- **调理重点**: {constitution.get('care_priority', '')}")

    for note in synthesis.get('notes') or []:
        sections.append(f"  - {note}")
    sections.append("")
    return '\n'.join(sections)


def load_advanced_alignment(path):
    if not path:
        return None
    # 兼容 PowerShell 重定向可能产生的 UTF-16，以及 UTF-8 BOM。
    for encoding in ('utf-8', 'utf-8-sig', 'utf-16'):
        try:
            with open(path, 'r', encoding=encoding) as f:
                return json.load(f)
        except Exception:
            continue
    return None


def generate_report(year, audience='student', advanced=None):
    """生成综合报告"""
    # 获取全部推算数据
    tg, dz = get_ganzhi(year)
    dayun, _ = get_dayun(year)
    taiguo = is_taiguo(year)
    sitian = get_sitian(year)
    zaiquan = get_zaiquan(year)
    keqi = get_keqi_six_steps(year)
    zhuqi = get_zhuqi_six_steps()
    zhuyun = get_zhuyun_five_steps(year)
    keyun = get_keyun_five_steps(year)
    tianfu = check_tianfu(year)
    suihui = check_suihui(year)
    pingqi = check_pingqi(year)
    sx = DIZHI_SHENGXIAO[dz]
    idx = get_sexagenary_index(year)

    # 客主加临分析
    jialin_results = []
    xiangde = 0
    for i in range(6):
        kq = keqi[i][1]
        zq = zhuqi[i][1]
        rel, sn = kezhujialin_relation(kq, zq)
        jialin_results.append((i + 1, zq, kq, rel, sn))
        if sn.startswith('相得'):
            xiangde += 1

    # 构建报告
    sections = []

    # === 通用部分 ===
    sections.append(f"# {year}年（{tg}{dz}年）运气综合分析\n")
    sections.append(f"**六十甲子序号**: 第{idx}甲子 | **生肖**: {sx}\n")

    # 大运
    sections.append("## 一、大运\n")
    status = "平气" if pingqi else ("太过" if taiguo else "不及")
    sections.append(f"- **天干**: {tg}（{TIANGAN_YINYANG[tg]}干）")
    sections.append(f"- **大运**: {dayun}运{status}")
    if pingqi:
        sections.append(f"- **平气**: 是（太过被抑或不及得助）")
    sections.append(f"- **天符**: {'是' if tianfu else '否'} | **岁会**: {'是' if suihui else '否'} | **太乙天符**: {'是' if (tianfu and suihui) else '否'}\n")

    # 六气
    sections.append("## 二、六气格局\n")
    sections.append(f"- **司天**: {sitian}（{LIUQI_YINYANG[sitian]}）— 上半年主管")
    sections.append(f"- **在泉**: {zaiquan}（{LIUQI_YINYANG[zaiquan]}）— 下半年主管\n")

    # 主运客运
    sections.append("## 三、主运与客运\n")
    step_names = ['初运', '二运', '三运', '四运', '终运']
    sections.append(f"| 步 | 主运 | 客运 |")
    sections.append(f"|----|------|------|")
    for i in range(5):
        zy = zhuyun[i]
        ky = keyun[i]
        sections.append(f"| {step_names[i]} | {zy[2]}{zy[1]}运 | {ky[2]}{ky[1]}运 |")
    sections.append("")

    # 客气六步
    sections.append("## 四、客气六步\n")
    qi_step_names = ['初之气', '二之气', '三之气', '四之气', '五之气', '终之气']
    sections.append(f"| 步 | 节气 | 主气 | 客气 | 备注 |")
    sections.append(f"|----|------|------|------|------|")
    for i in range(6):
        jq = ZHUQI_JIEQI[i + 1]
        kq_name = keqi[i][1]
        zq_name = zhuqi[i][1]
        note = ''
        if keqi[i][2]:
            note = '司天'
        elif keqi[i][3]:
            note = '在泉'
        sections.append(f"| {qi_step_names[i]} | {jq[0]}~{jq[1]} | {zq_name} | {kq_name} | {note} |")
    sections.append("")

    # 客主加临
    sections.append("## 五、客主加临顺逆\n")
    sections.append(f"| 步 | 主气 | 客气 | 关系 | 顺逆 |")
    sections.append(f"|----|------|------|------|------|")
    for step, zq, kq, rel, sn in jialin_results:
        sections.append(f"| {qi_step_names[step-1]} | {zq} | {kq} | {rel} | {sn} |")
    sections.append(f"\n**相得**: {xiangde}步 | **不相得**: {6 - xiangde}步")
    overall = "和平之年（气候相对平和）" if xiangde >= 4 else "异常之年（气候变化较大）"
    sections.append(f"**总体判断**: {overall}\n")

    # === 按人群定制 ===
    if audience == 'student':
        sections.append("## 六、学习要点\n")
        sections.append(f"- {tg}年天干化{dayun}运（参考 yunqi-calc/references/tiangan_huayun.md）")
        sections.append(f"- {dz}年地支化{sitian}（参考 yunqi-calc/references/dizhi_huaqi.md）")
        sections.append(f"- 司天{sitian}与在泉{zaiquan}互为阴阳配对")
        sections.append(f"- 太过/不及: {'阳干太过' if taiguo else '阴干不及'}（参考 yunqi-calc/references/taiguo_buji.md）")
        if tianfu or suihui:
            tonghua = []
            if tianfu:
                tonghua.append("天符")
            if suihui:
                tonghua.append("岁会")
            sections.append(f"- 运气同化: {'、'.join(tonghua)}（参考 yunqi-calc/references/yunqi_tonghua.md）")
        sections.append("")

    elif audience == 'practitioner':
        sections.append("## 六、病机倾向\n")
        wuxing_bingji = {
            '木': '肝系病变（风证）', '火': '心系病变（热证）',
            '土': '脾系病变（湿证）', '金': '肺系病变（燥证）',
            '水': '肾系病变（寒证）',
        }
        sections.append(f"- 大运{dayun}运{'太过' if taiguo else '不及'}: {wuxing_bingji.get(dayun, '?')}")
        if taiguo:
            sections.append(f"  - 太过则本气偏盛，所胜受邪")
        else:
            sections.append(f"  - 不及则本气偏衰，所不胜来乘")
        sections.append(f"- 司天{sitian}: {wuxing_bingji.get(LIUQI_WUXING[sitian], '?')}（上半年）")
        sections.append(f"- 在泉{zaiquan}: {wuxing_bingji.get(LIUQI_WUXING[zaiquan], '?')}（下半年）")
        if xiangde < 4:
            sections.append(f"- 客主加临不相得多（{6 - xiangde}步），气候异常，需注意防范")
        sections.append("")
        sections.append("## 七、治法参考\n")
        sections.append(f"- 治则: {'抑其太过，扶其不胜' if taiguo else '扶其不足，抑其所不胜'}")
        sections.append("- 具体方药参考 yunqi-clinical/references/fangyao_xuanze.md")
        sections.append("- 针灸选穴参考 yunqi-clinical/references/zhenjiu_xuanxue.md")
        sections.append("- 养生调理参考 yunqi-clinical/references/yangsheng_tiaoli.md")
        sections.append("")

    elif audience == 'researcher':
        sections.append("## 六、文献关联\n")
        sections.append("- 素问·天元纪大论: 天干化运、地支化气总纲")
        sections.append("- 素问·气交变大论: 五运太过不及的气候病机")
        sections.append("- 素问·六元正纪大论: 六气六步主客加临")
        sections.append("- 素问·至真要大论: 六气病机治法")
        sections.append("")
        sections.append("## 七、研究要点\n")
        sections.append(f"- 本年大运{dayun}运{'太过' if taiguo else '不及'}，可对比历史同干年")
        sections.append(f"- 司天{sitian}在泉{zaiquan}，可检索同类年份的流行病学数据")
        sections.append(f"- 客主加临{xiangde}步相得{6-xiangde}步不相得，可分析气候异常程度")
        sections.append("- 参考文献详见 yunqi-classics/references/")
        sections.append("")

    # 高级对齐章节（可选）
    advanced_section = build_advanced_alignment_section(advanced)
    if advanced_section:
        sections.append(advanced_section)

    # 免责声明
    sections.append(DISCLAIMER)

    return '\n'.join(sections)


def main():
    if len(sys.argv) < 2:
        print("用法: python yunqi_report.py <年份> [--audience student|practitioner|researcher] [--json] [--advanced-json <高级对齐JSON文件>]")
        sys.exit(1)

    year = int(sys.argv[1])
    audience = 'student'
    advanced = None
    if '--audience' in sys.argv:
        idx = sys.argv.index('--audience')
        if idx + 1 < len(sys.argv):
            audience = sys.argv[idx + 1]
    if '--advanced-json' in sys.argv:
        idx = sys.argv.index('--advanced-json')
        if idx + 1 < len(sys.argv):
            advanced = load_advanced_alignment(sys.argv[idx + 1])

    if audience not in ('student', 'practitioner', 'researcher'):
        print(f"audience 必须是 student/practitioner/researcher，当前: {audience}")
        sys.exit(1)

    report = generate_report(year, audience, advanced=advanced)

    if '--json' in sys.argv:
        tg, dz = get_ganzhi(year)
        dayun, _ = get_dayun(year)
        sitian = get_sitian(year)
        zaiquan = get_zaiquan(year)
        result = {
            'year': year,
            'ganzhi': f'{tg}{dz}',
            'dayun': f'{dayun}运{"太过" if is_taiguo(year) else "不及"}',
            'sitian': sitian,
            'zaiquan': zaiquan,
            'tianfu': check_tianfu(year),
            'suihui': check_suihui(year),
            'pingqi': check_pingqi(year),
            'audience': audience,
            'has_advanced_alignment': advanced is not None,
            'report': report,
        }
        output = json.dumps(result, ensure_ascii=False, indent=2)
        sys.stdout.write(output + '\n')
    else:
        sys.stdout.write(report + '\n')
    sys.stdout.flush()


if __name__ == '__main__':
    main()
