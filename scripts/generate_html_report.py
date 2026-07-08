#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成五运六气 HTML 可视化报告
用法:
  python scripts/generate_html_report.py <YYYY-MM-DD> [输出路径]
示例:
  python scripts/generate_html_report.py 2026-06-29 reports/generated/wuyun-liuqi-report.html
"""
import sys
import os
import json
import subprocess

from _common import setup_environment
setup_environment(add_lib=False)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WUXING_COLORS = {
    '木': {'bg': '#0f3d2e', 'fg': '#4ade80', 'light': '#86efac', 'glow': 'rgba(74,222,128,0.45)'},
    '火': {'bg': '#4a0f0f', 'fg': '#fb7185', 'light': '#fda4af', 'glow': 'rgba(251,113,133,0.45)'},
    '土': {'bg': '#3d320f', 'fg': '#facc15', 'light': '#fde047', 'glow': 'rgba(250,204,21,0.45)'},
    '金': {'bg': '#2a2a2a', 'fg': '#e5e7eb', 'light': '#f3f4f6', 'glow': 'rgba(229,231,235,0.45)'},
    '水': {'bg': '#0a1f3d', 'fg': '#60a5fa', 'light': '#93c5fd', 'glow': 'rgba(96,165,250,0.45)'},
}

LIUQI_WUXING = {
    '厥阴风木': '木', '少阴君火': '火', '太阴湿土': '土',
    '少阳相火': '火', '阳明燥金': '金', '太阳寒水': '水',
}


def get_data(date_str):
    """直接调用（P0 优化：避免 subprocess 开销）"""
    # 确保 lib 路径可用
    sys.path.insert(0, os.path.join(BASE_DIR, 'scripts', 'lib'))
    from calculate_yunqi_api import calculate_yunqi_api
    return calculate_yunqi_api(date_str)


def fetch_advanced_alignment(date_str, birth_date=None, city=None, lat=None, lon=None,
                             mock=False, no_weather=False, timeout=10):
    """调用 advanced_alignment.py 获取高级对齐 JSON。"""
    script = os.path.join(BASE_DIR, 'scripts', 'advanced_alignment.py')
    args = [sys.executable, script, date_str, '--json']
    if birth_date:
        args += ['--birth-date', birth_date]
    if city:
        args += ['--city', city]
    if lat is not None:
        args += ['--lat', str(lat)]
    if lon is not None:
        args += ['--lon', str(lon)]
    if mock:
        args += ['--mock']
    if no_weather:
        args += ['--no-weather']
    args += ['--timeout', str(timeout)]
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    result = subprocess.run(
        args,
        capture_output=True, text=True, encoding='utf-8', env=env, timeout=max(60, timeout * 6),
    )
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def escape_html(text):
    if text is None:
        return ''
    return (str(text).replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;').replace('"', '&quot;'))


def render_advanced_alignment_section(advanced):
    """渲染高级对齐章节 HTML。advanced 为 advanced_alignment.py 的 JSON 输出。"""
    if not advanced:
        return ''
    synthesis = advanced.get('advanced_synthesis') or {}
    rows = []
    rows.append(f'<tr><th>综合等级</th><td>{escape_html(synthesis.get("label", ""))}（{escape_html(synthesis.get("level", ""))}）</td></tr>')
    rows.append(f'<tr><th>重点体质</th><td>{escape_html("、".join(synthesis.get("focus_constitutions") or []) or "未指定")}</td></tr>')
    rows.append(f'<tr><th>摘要</th><td>{escape_html(synthesis.get("summary", ""))}</td></tr>')
    layers = synthesis.get('layers') or []
    rows.append(f'<tr><th>已启用层</th><td>{escape_html("、".join(layers)) if layers else "仅基础运气"}</td></tr>')

    blocks = [f'''
    <section class="section">
      <h2 class="section-title font-serif">高级对齐</h2>
      <div style="overflow-x:auto">
        <table class="jialin-table">
          <tbody>
            {''.join(rows)}
          </tbody>
        </table>
      </div>
    ''']

    weather = advanced.get('weather_alignment')
    if weather:
        wq = weather.get('weather_qi') or {}
        al = weather.get('alignment') or {}
        w_rows = [
            f'<tr><th>天气六气</th><td>{escape_html(wq.get("pattern", ""))}</td></tr>',
            f'<tr><th>对齐类型</th><td>{escape_html(al.get("label", ""))}（{escape_html(al.get("type", ""))}）</td></tr>',
            f'<tr><th>调摄原则</th><td>{escape_html(al.get("care_principle", ""))}</td></tr>',
        ]
        blocks.append(f'''
        <div style="overflow-x:auto;margin-top:1rem">
          <table class="jialin-table">
            <thead><tr><th>天气对齐</th><th></th></tr></thead>
            <tbody>{''.join(w_rows)}</tbody>
          </table>
        </div>
        ''')

    profile = advanced.get('personal_profile')
    if profile:
        names = [item.get('name') for item in profile.get('birth_constitutions') or []]
        p_rows = [
            f'<tr><th>出生运气年</th><td>{escape_html(profile.get("birth_yunqi_year", ""))}（{escape_html(profile.get("birth_suiyun", {}).get("name", ""))}）</td></tr>',
            f'<tr><th>先天体质</th><td>{escape_html("、".join(names)) if names else "未匹配"}</td></tr>',
        ]
        blocks.append(f'''
        <div style="overflow-x:auto;margin-top:1rem">
          <table class="jialin-table">
            <thead><tr><th>出生运气体质</th><th></th></tr></thead>
            <tbody>{''.join(p_rows)}</tbody>
          </table>
        </div>
        ''')

    constitution = advanced.get('constitution_assessment')
    if constitution:
        c_rows = [
            f'<tr><th>主要体质</th><td>{escape_html(constitution.get("primary_type", ""))}（{escape_html(str(constitution.get("primary_score", "")))} 分）</td></tr>',
            f'<tr><th>兼夹/倾向</th><td>{escape_html("、".join(constitution.get("secondary_types") or []) or "无")}</td></tr>',
            f'<tr><th>调理重点</th><td>{escape_html(constitution.get("care_priority", ""))}</td></tr>',
        ]
        blocks.append(f'''
        <div style="overflow-x:auto;margin-top:1rem">
          <table class="jialin-table">
            <thead><tr><th>体质量表</th><th></th></tr></thead>
            <tbody>{''.join(c_rows)}</tbody>
          </table>
        </div>
        ''')

    regional = advanced.get('regional_alignment')
    if regional:
        r_rows = [
            f'<tr><th>地区</th><td>{escape_html(regional.get("region_name", ""))}</td></tr>',
            f'<tr><th>权重</th><td>五运 {escape_html(str(regional.get("wuyun_weight", "")))}；六气 {escape_html(str(regional.get("liuqi_weight", "")))}</td></tr>',
            f'<tr><th>影响因子</th><td>{escape_html("、".join(regional.get("affected_factors") or []) or "未提取")}</td></tr>',
            f'<tr><th>解释</th><td>{escape_html(regional.get("explanation", ""))}</td></tr>',
        ]
        blocks.append(f'''
        <div style="overflow-x:auto;margin-top:1rem">
          <table class="jialin-table">
            <thead><tr><th>地域修正</th><th></th></tr></thead>
            <tbody>{''.join(r_rows)}</tbody>
          </table>
        </div>
        ''')

    notes = synthesis.get('notes') or []
    if notes:
        note_items = ''.join(f'<li>{escape_html(n)}</li>' for n in notes)
        blocks.append(f'<ul style="margin-top:1rem;color:var(--muted);font-size:0.9rem;">{note_items}</ul>')

    blocks.append('</section>')
    return ''.join(blocks)


def element_color(name, key='fg'):
    wx = LIUQI_WUXING.get(name, '')
    return WUXING_COLORS.get(wx, WUXING_COLORS['金'])[key]


def generate_interpretation(data):
    """根据推算结果生成小白友好的解读"""
    sui_yun = data['sui_yun']
    si_tian = data['si_tian']
    zai_quan = data['zai_quan']
    current = data['current_step']

    # 全年气候基调
    if sui_yun['element'] == '水' and sui_yun['status'] == '太过':
        year_climate = "全年偏寒、湿气偏重，冬天可能更冷，夏天也偶有寒凉时段。"
        year_body = "肾、膀胱、心脑血管、关节相对容易受寒气影响。"
        year_food = "平时可多吃些温性食物，如生姜、羊肉、桂圆、红枣；少喝冰饮、少吃生冷瓜果。"
    elif sui_yun['element'] == '火' and sui_yun['status'] == '太过':
        year_climate = "全年偏热，炎夏可能格外明显。"
        year_body = "心、小肠、眼睛、血压容易上火。"
        year_food = "宜清淡，多吃绿豆、莲子、百合、梨；少吃辛辣、油炸、烧烤。"
    elif sui_yun['element'] == '木' and sui_yun['status'] == '太过':
        year_climate = "风气偏盛，春天风大，全年气候多变。"
        year_body = "肝、胆、眼睛、筋骨容易不舒。"
        year_food = "宜吃绿色蔬菜、菊花、枸杞；少饮酒、少熬夜。"
    elif sui_yun['element'] == '土' and sui_yun['status'] == '太过':
        year_climate = "湿气偏重，梅雨季节或长夏可能闷热潮湿。"
        year_body = "脾胃、消化系统容易受湿困。"
        year_food = "宜吃山药、薏米、茯苓、冬瓜；少吃甜腻、生冷、油腻。"
    elif sui_yun['element'] == '金' and sui_yun['status'] == '太过':
        year_climate = "燥气偏盛，秋冬干燥明显。"
        year_body = "肺、大肠、皮肤、呼吸道容易干燥不适。"
        year_food = "宜吃银耳、百合、梨、蜂蜜；少吃辛辣燥热。"
    else:
        year_climate = "全年气候相对平和，但仍需留意季节交替。"
        year_body = "注意顺应四时，保养正气。"
        year_food = "饮食均衡，随季节调整。"

    # 当前步位解读
    relation = current['relation']
    zhu_qi = current['zhu_qi']
    ke_qi = current['ke_qi']

    if '同气' in relation:
        step_climate = f"当前{zhu_qi}与{ke_qi}同气，相当于两种相似的能量叠加，气候特征会更明显。"
        step_body = "相关脏腑功能容易偏盛，可能出现上火、燥热、亢奋等表现。"
        step_tip = "注意劳逸结合，避免过度消耗；可适当清润、养阴。"
    elif '客气生主气' in relation:
        step_climate = f"当前{ke_qi}生助{zhu_qi}，气候相对和顺。"
        step_body = "身体适应较好，是调养的好时机。"
        step_tip = "可顺势调养对应脏腑，适度运动。"
    elif '客气克主气' in relation:
        step_climate = f"当前{ke_qi}克制{zhu_qi}，气候不调，像外环境给身体加了压力。"
        step_body = "容易出现不适，如感冒、肠胃紊乱、睡眠差等。"
        step_tip = "注意保暖、饮食清淡、作息规律，减少外出劳累。"
    elif '主气生客气' in relation:
        step_climate = f"当前{zhu_qi}生{ke_qi}，气机上逆，像内部能量被往外带。"
        step_body = "容易出现上火、头晕、情绪烦躁、失眠等。"
        step_tip = "保持情绪平稳，少熬夜，可饮菊花茶、绿豆汤清火。"
    else:
        step_climate = "当前气候相对平和。"
        step_body = "身体状态较稳定。"
        step_tip = "保持日常养生节奏即可。"

    # 上半年/下半年提示
    half_year = "上半年" if current['keqi_is_sitian'] or current['step_number'] <= 3 else "下半年"
    dominant = si_tian if half_year == "上半年" else zai_quan
    half_tip = f"现在处于{half_year}，{dominant}的影响较强。"

    return {
        'year_climate': year_climate,
        'year_body': year_body,
        'year_food': year_food,
        'step_climate': step_climate,
        'step_body': step_body,
        'step_tip': step_tip,
        'half_tip': half_tip,
        'metaphor': "运气好比一年的「天气剧本」，岁运是年度总调，司天在泉是上下半场主题，当前步位就是你现在正看的这一集。",
    }


def generate_html(data, advanced=None):
    date_str = data['date']
    year_gz = data['year_gz']
    sui_yun = data['sui_yun']
    si_tian = data['si_tian']
    zai_quan = data['zai_quan']
    current = data['current_step']

    # 六气圆环卡片
    qi_cards = []
    for step in data['ke_zhu_jia_lin']:
        is_current = step['step_number'] == current['step_number']
        zhu_wx = LIUQI_WUXING.get(step['zhu_qi'], '金')
        ke_wx = LIUQI_WUXING.get(step['ke_qi'], '金')
        cls = 'qi-card current' if is_current else 'qi-card'
        border = f"border-color: {WUXING_COLORS[ke_wx]['fg']};"
        glow = f"box-shadow: 0 0 28px {WUXING_COLORS[ke_wx]['glow']};" if is_current else ''
        badge = ''
        if step['keqi_is_sitian']:
            badge = '<span class="badge sitian">司天</span>'
        elif step['keqi_is_zaiquan']:
            badge = '<span class="badge zaiquan">在泉</span>'
        current_badge = '<span class="badge current-badge">当前</span>' if is_current else ''
        qi_cards.append(f'''
        <div class="{cls}" style="{border} {glow}">
          <div class="qi-step-num">{step['step_number']}</div>
          <div class="qi-name">{step['step_name'].split('(')[0]}</div>
          <div class="qi-pair">
            <span class="zhu" style="color:{WUXING_COLORS[zhu_wx]['fg']}">主 {step['zhu_qi']}</span>
            <span class="ke" style="color:{WUXING_COLORS[ke_wx]['fg']}">客 {step['ke_qi']}</span>
          </div>
          <div class="qi-relation">{step['relation']} · {step['shun_ni']}</div>
          <div class="qi-badges">{badge}{current_badge}</div>
        </div>
        ''')

    # 主运/客运时间轴
    yun_timeline = []
    for zy, ky in zip(data['zhu_yun'], data['ke_yun']):
        zy_color = WUXING_COLORS[zy['element']]['fg']
        ky_color = WUXING_COLORS[ky['element']]['fg']
        yun_timeline.append(f'''
        <div class="yun-step">
          <div class="yun-dot" style="background:{zy_color};box-shadow:0 0 12px {WUXING_COLORS[zy['element']]['glow']}"></div>
          <div class="yun-info">
            <div class="yun-label">第{zy['step']}运</div>
            <div class="yun-values">
              <span style="color:{zy_color}">主 {zy['tai_shao']}{zy['element']}运</span>
              <span class="yun-sep">|</span>
              <span style="color:{ky_color}">客 {ky['tai_shao']}{ky['element']}运</span>
            </div>
          </div>
        </div>
        ''')

    # 客主加临表格
    table_rows = []
    for step in data['ke_zhu_jia_lin']:
        is_current = step['step_number'] == current['step_number']
        row_cls = 'row-current' if is_current else ''
        zhu_wx = LIUQI_WUXING.get(step['zhu_qi'], '金')
        ke_wx = LIUQI_WUXING.get(step['ke_qi'], '金')
        shun_ni_cls = 'shun' if step['shun_ni'].startswith('相得') else 'ni'
        table_rows.append(f'''
        <tr class="{row_cls}">
          <td>{step['step_name'].split('(')[0]} {'★' if is_current else ''}</td>
          <td style="color:{WUXING_COLORS[zhu_wx]['fg']}">{step['zhu_qi']}</td>
          <td style="color:{WUXING_COLORS[ke_wx]['fg']}">{step['ke_qi']}</td>
          <td>{step['relation']}</td>
          <td class="{shun_ni_cls}">{step['shun_ni']}</td>
        </tr>
        ''')

    # 当前步位聚焦
    zhu_wx = LIUQI_WUXING.get(current['zhu_qi'], '金')
    ke_wx = LIUQI_WUXING.get(current['ke_qi'], '金')

    # 报告解读
    interp = generate_interpretation(data)

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>五运六气 · {date_str} · {year_gz}年</title>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700;900&family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>
:root {{
  --ink: #0b0f17;
  --surface: #111827;
  --surface-2: #1f2937;
  --gold: #d4af37;
  --gold-light: #f3e5ab;
  --muted: #94a3b8;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  font-family: 'Noto Sans SC', sans-serif;
  background: radial-gradient(ellipse at 50% 0%, #162032 0%, #0b0f17 60%);
  color: #f8fafc;
  min-height: 100vh;
}}
.font-serif {{ font-family: 'Noto Serif SC', serif; }}
.gold-text {{
  background: linear-gradient(135deg, var(--gold-light) 0%, var(--gold) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}}
.hero {{
  position: relative;
  padding: 4rem 1rem 3rem;
  text-align: center;
  overflow: hidden;
}}
.hero::before {{
  content: '';
  position: absolute;
  inset: 0;
  background: url('../wuyun-liuqi-skills.png') center/contain no-repeat;
  opacity: 0.12;
  filter: blur(2px);
  pointer-events: none;
}}
.hero-content {{ position: relative; z-index: 1; }}
.hero h1 {{ font-size: clamp(2.2rem, 7vw, 4.5rem); letter-spacing: 0.05em; }}
.hero .subtitle {{ color: var(--muted); font-size: 1.05rem; margin-top: 0.75rem; }}
.hero-badges {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 0.75rem; margin-top: 1.75rem; }}
.badge-hero {{
  padding: 0.5rem 1rem;
  border-radius: 999px;
  border: 1px solid rgba(212,175,55,0.35);
  background: rgba(17,24,39,0.7);
  color: var(--gold-light);
  font-size: 0.9rem;
  backdrop-filter: blur(6px);
}}
.section {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 2.5rem 1rem;
}}
.section-title {{
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--gold-light);
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.6rem;
}}
.section-title::before {{
  content: '';
  width: 4px;
  height: 1.4em;
  background: linear-gradient(180deg, var(--gold) 0%, transparent 100%);
  border-radius: 2px;
}}
.current-focus {{
  background: linear-gradient(135deg, rgba(212,175,55,0.12) 0%, rgba(17,24,39,0.9) 60%);
  border: 1px solid rgba(212,175,55,0.35);
  border-radius: 1.25rem;
  padding: 2rem;
  position: relative;
  overflow: hidden;
}}
.current-focus::after {{
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: {WUXING_COLORS[ke_wx]['glow']};
  filter: blur(60px);
  pointer-events: none;
}}
.focus-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.25rem;
  margin-top: 1.5rem;
}}
.focus-item {{
  background: rgba(17,24,39,0.7);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 0.875rem;
  padding: 1.25rem;
}}
.focus-item .label {{ color: var(--muted); font-size: 0.85rem; margin-bottom: 0.35rem; }}
.focus-item .value {{ font-size: 1.25rem; font-weight: 700; }}
.qi-ring {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
}}
.qi-card {{
  background: rgba(17,24,39,0.75);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 1rem;
  padding: 1.25rem 1rem;
  text-align: center;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  position: relative;
}}
.qi-card:hover {{ transform: translateY(-4px); }}
.qi-card.current {{
  background: rgba(17,24,39,0.95);
  border-width: 2px;
}}
.qi-step-num {{
  position: absolute;
  top: 0.6rem;
  left: 0.6rem;
  width: 1.6rem;
  height: 1.6rem;
  line-height: 1.6rem;
  border-radius: 50%;
  background: rgba(255,255,255,0.08);
  color: var(--muted);
  font-size: 0.75rem;
}}
.qi-card.current .qi-step-num {{ background: var(--gold); color: #0b0f17; font-weight: 700; }}
.qi-name {{ font-size: 1.15rem; font-weight: 700; color: var(--gold-light); margin-bottom: 0.75rem; }}
.qi-pair {{ display: flex; justify-content: center; gap: 0.75rem; font-size: 0.95rem; margin-bottom: 0.5rem; }}
.qi-relation {{ font-size: 0.8rem; color: var(--muted); }}
.qi-badges {{ display: flex; justify-content: center; gap: 0.35rem; margin-top: 0.75rem; }}
.badge {{
  font-size: 0.7rem;
  padding: 0.2rem 0.5rem;
  border-radius: 999px;
  border: 1px solid;
}}
.badge.sitian {{ color: #fb7185; border-color: rgba(251,113,133,0.4); }}
.badge.zaiquan {{ color: #e5e7eb; border-color: rgba(229,231,235,0.4); }}
.badge.current-badge {{ color: #0b0f17; background: var(--gold); border-color: var(--gold); font-weight: 700; }}
.yun-timeline {{
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: space-between;
}}
.yun-step {{
  flex: 1 1 160px;
  background: rgba(17,24,39,0.7);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 0.875rem;
  padding: 1.25rem;
  text-align: center;
}}
.yun-dot {{
  width: 1.25rem;
  height: 1.25rem;
  border-radius: 50%;
  margin: 0 auto 0.75rem;
}}
.yun-label {{ color: var(--muted); font-size: 0.8rem; margin-bottom: 0.35rem; }}
.yun-values {{ font-weight: 700; font-size: 1.05rem; }}
.yun-sep {{ color: var(--muted); margin: 0 0.4rem; }}
.jialin-table {{
  width: 100%;
  border-collapse: collapse;
  background: rgba(17,24,39,0.6);
  border-radius: 1rem;
  overflow: hidden;
}}
.jialin-table th, .jialin-table td {{
  padding: 0.9rem 1rem;
  text-align: left;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}}
.jialin-table th {{
  background: rgba(212,175,55,0.12);
  color: var(--gold-light);
  font-weight: 600;
  font-size: 0.85rem;
}}
.jialin-table tr:last-child td {{ border-bottom: none; }}
.jialin-table tr:hover {{ background: rgba(255,255,255,0.04); }}
.jialin-table .row-current {{ background: rgba(212,175,55,0.1); }}
.jialin-table .shun {{ color: #4ade80; }}
.jialin-table .ni {{ color: #fb7185; }}
.interpret-card {{
  background: rgba(17,24,39,0.75);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 1rem;
  padding: 1.5rem;
}}
.interpret-card h3 {{
  color: var(--gold-light);
  font-size: 1.05rem;
  margin: 0 0 0.75rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.4rem;
}}
.interpret-card p {{
  color: #e2e8f0;
  line-height: 1.7;
  margin: 0;
  font-size: 0.95rem;
}}
.metaphor {{
  background: linear-gradient(135deg, rgba(212,175,55,0.12) 0%, rgba(17,24,39,0.9) 70%);
  border: 1px solid rgba(212,175,55,0.25);
  border-radius: 1rem;
  padding: 1.5rem;
  color: var(--gold-light);
  font-size: 1rem;
  line-height: 1.8;
}}
.tag {{
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  margin-right: 0.35rem;
  background: rgba(212,175,55,0.15);
  color: var(--gold-light);
}}
.disclaimer {{
  margin-top: 3rem;
  padding: 1.5rem;
  border-radius: 1rem;
  background: rgba(248,113,113,0.08);
  border: 1px solid rgba(248,113,113,0.25);
  color: #fca5a5;
  font-size: 0.9rem;
  line-height: 1.7;
}}
.print-btn {{
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  z-index: 50;
  background: linear-gradient(135deg, var(--gold) 0%, #b8860b 100%);
  color: #0b0f17;
  font-weight: 700;
  padding: 0.75rem 1.25rem;
  border-radius: 999px;
  border: none;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(212,175,55,0.3);
  transition: transform 0.2s ease;
}}
.print-btn:hover {{ transform: translateY(-2px); }}
.tooltip {{
  position: relative;
  cursor: help;
  border-bottom: 1px dashed rgba(212,175,55,0.5);
}}
.tooltip::after {{
  content: attr(data-tip);
  position: absolute;
  bottom: 120%;
  left: 50%;
  transform: translateX(-50%);
  width: max-content;
  max-width: 260px;
  background: rgba(17,24,39,0.98);
  border: 1px solid rgba(212,175,55,0.35);
  color: #f8fafc;
  padding: 0.6rem 0.8rem;
  border-radius: 0.5rem;
  font-size: 0.8rem;
  line-height: 1.5;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease;
  z-index: 100;
}}
.tooltip:hover::after {{ opacity: 1; }}
@media print {{
  .print-btn {{ display: none; }}
  body {{ background: #fff; color: #111; }}
  .hero::before {{ opacity: 0.05; }}
}}
@media (max-width: 640px) {{
  .hero {{ padding: 2.5rem 1rem 2rem; }}
  .yun-timeline {{ flex-direction: column; }}
  .jialin-table th, .jialin-table td {{ padding: 0.7rem 0.5rem; font-size: 0.85rem; }}
}}
</style>
</head>
<body>
  <button class="print-btn" onclick="window.print()">导出 / 打印</button>

  <header class="hero">
    <div class="hero-content">
      <h1 class="font-serif gold-text">五运六气</h1>
      <p class="subtitle font-serif">{date_str} · {year_gz}年 · 第{data['sexagenary_index']}甲子 · 生肖{data['shengxiao']}</p>
      <div class="hero-badges">
        <span class="badge-hero">岁运：<span style="color:{element_color(sui_yun['element']+'运','fg')}">{sui_yun['name']}{sui_yun['status']}</span></span>
        <span class="badge-hero">司天：{si_tian}</span>
        <span class="badge-hero">在泉：{zai_quan}</span>
        <span class="badge-hero">日干支：{data['day_gz']}</span>
      </div>
    </div>
  </header>

  <main>
    <section class="section">
      <div class="current-focus">
        <h2 class="section-title font-serif" style="margin:0">当前步位聚焦</h2>
        <p style="color:var(--muted); margin-top:0.5rem;">{current['name']} · {current['date_range']['start']} 至 {current['date_range']['end']}</p>
        <div class="focus-grid">
          <div class="focus-item">
            <div class="label">主气</div>
            <div class="value" style="color:{element_color(current['zhu_qi'],'fg')}">{current['zhu_qi']}</div>
          </div>
          <div class="focus-item">
            <div class="label">客气</div>
            <div class="value" style="color:{element_color(current['ke_qi'],'fg')}">{current['ke_qi']}</div>
          </div>
          <div class="focus-item">
            <div class="label">关系</div>
            <div class="value">{current['relation']}</div>
          </div>
          <div class="focus-item">
            <div class="label">顺逆</div>
            <div class="value" style="color:{'#4ade80' if current['shun_ni'].startswith('相得') else '#fb7185'}">{current['shun_ni']}</div>
          </div>
        </div>
      </div>
    </section>

    <section class="section">
      <h2 class="section-title font-serif">报告解读</h2>
      <div class="metaphor" style="margin-bottom:1.5rem;">
        <strong>💡 一句话理解</strong>：{interp['metaphor']}<br>
        <span style="color:var(--muted);font-size:0.9rem;">今年整体是「{sui_yun['name']}{sui_yun['status']}」，上半年由「{si_tian}」主导，下半年由「{zai_quan}」主导。你现在正身处「{current['name']}」这一段。</span>
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem;">
        <div class="interpret-card">
          <h3><span class="tag">全年气候</span>这一年天气总基调</h3>
          <p>{interp['year_climate']}</p>
        </div>
        <div class="interpret-card">
          <h3><span class="tag">身体提示</span>哪些部位容易受影响</h3>
          <p>{interp['year_body']}</p>
        </div>
        <div class="interpret-card">
          <h3><span class="tag">饮食建议</span>怎么吃更顺应当年气</h3>
          <p>{interp['year_food']}</p>
        </div>
        <div class="interpret-card">
          <h3><span class="tag">当前气候</span>现在这段时间怎么样</h3>
          <p>{interp['step_climate']} {interp['half_tip']}</p>
        </div>
        <div class="interpret-card">
          <h3><span class="tag">近期注意</span>身体可能出现的信号</h3>
          <p>{interp['step_body']}</p>
        </div>
        <div class="interpret-card">
          <h3><span class="tag">生活调理</span>起居运动情绪建议</h3>
          <p>{interp['step_tip']}</p>
        </div>
      </div>
    </section>

    <section class="section">
      <h2 class="section-title font-serif">六气步位圆环</h2>
      <div class="qi-ring">
        {''.join(qi_cards)}
      </div>
    </section>

    <section class="section">
      <h2 class="section-title font-serif">五运推移</h2>
      <div class="yun-timeline">
        {''.join(yun_timeline)}
      </div>
    </section>

    <section class="section">
      <h2 class="section-title font-serif">客主加临顺逆</h2>
      <div style="overflow-x:auto">
        <table class="jialin-table">
          <thead>
            <tr>
              <th>步位</th>
              <th>主气</th>
              <th>客气</th>
              <th>关系</th>
              <th>顺逆</th>
            </tr>
          </thead>
          <tbody>
            {''.join(table_rows)}
          </tbody>
        </table>
      </div>
    </section>

    {render_advanced_alignment_section(advanced)}

    <section class="section">
      <h2 class="section-title font-serif">术语速查</h2>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1rem;color:var(--muted);font-size:0.9rem;">
        <div><strong class="gold-text">岁运</strong>：即大运，一年之总气，由年干决定。</div>
        <div><strong class="gold-text">司天</strong>：上半年主管之气，由年支决定。</div>
        <div><strong class="gold-text">在泉</strong>：下半年主管之气，与司天相对。</div>
        <div><strong class="gold-text">主气</strong>：六气固定次序，初之气厥阴风木至终之气太阳寒水。</div>
        <div><strong class="gold-text">客气</strong>：逐年流转之六气，以司天所在步位为第三气。</div>
        <div><strong class="gold-text">客主加临</strong>：客气与主气同处一步，按五行生克判断顺逆。</div>
      </div>
    </section>

    <section class="section">
      <div class="disclaimer">
        <strong>免责声明</strong>：以上分析基于中医运气学说理论推算，仅供参考。运气学说非现代医学诊断标准，具体诊疗须由执业中医师辨证论治。请勿据此自行用药或针灸。
      </div>
    </section>
  </main>

  <footer style="text-align:center;padding:2rem 1rem;color:var(--muted);font-size:0.8rem;">
    由 wuyun-liuqi-skills 自动生成 · {date_str}
  </footer>
</body>
</html>'''
    return html


def main():
    if len(sys.argv) < 2:
        print("用法: python scripts/generate_html_report.py <YYYY-MM-DD> [输出路径] [--with-advanced-alignment --birth-date YYYY-MM-DD --city 城市] [--mock] [--no-weather]")
        print("示例: python scripts/generate_html_report.py 2026-06-29 reports/generated/wuyun-liuqi-report.html")
        sys.exit(1)

    date_str = sys.argv[1]
    positional = []
    advanced_kwargs = {}
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--with-advanced-alignment':
            advanced_kwargs['enabled'] = True
        elif arg == '--birth-date' and i + 1 < len(sys.argv):
            advanced_kwargs['birth_date'] = sys.argv[i + 1]
            i += 1
        elif arg == '--city' and i + 1 < len(sys.argv):
            advanced_kwargs['city'] = sys.argv[i + 1]
            i += 1
        elif arg == '--lat' and i + 1 < len(sys.argv):
            advanced_kwargs['lat'] = float(sys.argv[i + 1])
            i += 1
        elif arg == '--lon' and i + 1 < len(sys.argv):
            advanced_kwargs['lon'] = float(sys.argv[i + 1])
            i += 1
        elif arg == '--mock':
            advanced_kwargs['mock'] = True
        elif arg == '--no-weather':
            advanced_kwargs['no_weather'] = True
        elif arg == '--timeout' and i + 1 < len(sys.argv):
            advanced_kwargs['timeout'] = int(sys.argv[i + 1])
            i += 1
        elif not arg.startswith('--'):
            positional.append(arg)
        i += 1

    output_path = positional[0] if positional else os.path.join(BASE_DIR, 'reports', 'generated', f'wuyun-liuqi-report-{date_str}.html')

    data = get_data(date_str)
    advanced = None
    if advanced_kwargs.get('enabled'):
        advanced = fetch_advanced_alignment(
            date_str,
            birth_date=advanced_kwargs.get('birth_date'),
            city=advanced_kwargs.get('city'),
            lat=advanced_kwargs.get('lat'),
            lon=advanced_kwargs.get('lon'),
            mock=advanced_kwargs.get('mock', False),
            no_weather=advanced_kwargs.get('no_weather', False),
            timeout=advanced_kwargs.get('timeout', 10),
        )
    html = generate_html(data, advanced=advanced)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    sys.stdout.write(f"✅ HTML 报告已生成：{output_path}\n")
    if advanced is None and advanced_kwargs.get('enabled'):
        sys.stdout.write("⚠️ 高级对齐获取失败，报告未包含高级对齐章节。\n")
    sys.stdout.flush()


if __name__ == '__main__':
    main()
