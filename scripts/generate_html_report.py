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
from types import SimpleNamespace

from _common import setup_environment, add_scripts_dir_to_path
setup_environment(add_lib=False, add_scripts=True)

# 免责声明：单一权威源（见 _safety_text.py），HTML 正文统一引用。
from _safety_text import CONTEXT_DISCLAIMERS

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
    """直接调用 calculate_yunqi_api（避免 subprocess）。"""
    sys.path.insert(0, os.path.join(BASE_DIR, 'scripts', 'lib'))
    add_scripts_dir_to_path()
    from calculate_yunqi_api import calculate_yunqi_api
    return calculate_yunqi_api(date_str)


def fetch_advanced_alignment(date_str, birth_date=None, city=None, lat=None, lon=None,
                             mock=False, no_weather=False, timeout=10):
    """直接 import advanced_alignment，获取高级对齐 JSON。"""
    add_scripts_dir_to_path()
    try:
        import advanced_alignment as aa
        args = SimpleNamespace(
            date=date_str,
            date_arg=date_str,
            birth_date=birth_date,
            city=city,
            lat=lat,
            lon=lon,
            mock=mock,
            no_weather=no_weather,
            timeout=timeout,
            region=None,
            birth_place=None,
            residence_place=None,
            current_place=city,
            constitution_demo=False,
            constitution_file=None,
            constitution_scores=None,
            assessment_date=None,
            assessed_by='self-assessment',
            provider='mock' if mock else 'auto',
            baseline_years=5,
            no_baseline=False,
            cache_ttl=60,
            no_cache=False,
            strict=False,
            json=True,
        )
        return aa.generate_advanced_alignment(args)
    except Exception:
        return None


def write_html_report(date_str, output_path=None, advanced=None, advanced_kwargs=None,
                      with_rag_bundle=True):
    """
    可编程 API：生成 HTML 报告并写入文件。
    返回：成功提示字符串（与 CLI 输出一致）。

    with_rag_bundle: 是否包含 rag_keys 知识库精确命中章节（默认 True）。
    """
    if output_path is None:
        output_path = os.path.join(BASE_DIR, 'reports', 'generated', f'wuyun-liuqi-report-{date_str}.html')
    data = get_data(date_str)
    adv = advanced
    if adv is None and advanced_kwargs and advanced_kwargs.get('enabled'):
        adv = fetch_advanced_alignment(
            date_str,
            birth_date=advanced_kwargs.get('birth_date'),
            city=advanced_kwargs.get('city'),
            lat=advanced_kwargs.get('lat'),
            lon=advanced_kwargs.get('lon'),
            mock=advanced_kwargs.get('mock', False),
            no_weather=advanced_kwargs.get('no_weather', False),
            timeout=advanced_kwargs.get('timeout', 10),
        )
    html = generate_html(data, advanced=adv, with_rag_bundle=with_rag_bundle)
    parent = os.path.dirname(output_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    msg = f"✅ HTML 报告已生成：{output_path}\n"
    if adv is None and advanced_kwargs and advanced_kwargs.get('enabled'):
        msg += "⚠️ 高级对齐获取失败，报告未包含高级对齐章节。\n"
    return msg


def escape_html(text):
    if text is None:
        return ''
    return (str(text).replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;').replace('"', '&quot;'))


def render_rag_bundle_section(date_str, with_rag_bundle=True):
    """
    渲染知识库精确命中章节（与 yunqi_report.build_rag_bundle_section 对齐）。
    使用 rag_search.fetch_by_date(date_str)。
    """
    if not with_rag_bundle:
        return ''
    try:
        from rag_search import fetch_by_date
        bundle = fetch_by_date(date_str, full=False)
    except Exception:
        return ''

    rag_keys = bundle.get('rag_keys') or {}
    hits_by_role = bundle.get('hits_by_role') or {}
    role_labels = {
        'suiyun': '岁运',
        'sitian': '司天',
        'zaiquan': '在泉',
        'current_step': '当前步位',
    }
    cards = []
    for _ri, role in enumerate(('suiyun', 'sitian', 'zaiquan', 'current_step'), 1):
        key = rag_keys.get(role, '')
        label = role_labels.get(role, role)
        hits = hits_by_role.get(role) or []
        if not hits:
            body = '<p class="rag-empty">（暂未收录相关条目）</p>'
        else:
            items = []
            for h in hits[:2]:
                preview = (h.get('preview') or '').strip()
                # 跳过纯标识符/占位预览（无汉字），避免开发术语泄漏到读者报告
                if not preview or not any('\u4e00' <= ch <= '\u9fff' for ch in preview):
                    continue
                if len(preview) > 140:
                    preview = preview[:140] + '…'
                htitle = h.get('title') or ''
                title_html = (f'<div class="rag-hit-title">{escape_html(htitle)}</div>'
                              if htitle and htitle != h.get('id') else '')
                items.append(
                    f'<div class="rag-hit">'
                    f'{title_html}'
                    f'<p>{escape_html(preview)}</p>'
                    f'</div>'
                )
            body = ''.join(items) if items else '<p class="rag-empty">（暂未收录相关条目）</p>'
        cards.append(
            f'<div class="rag-card reveal" data-d="{_ri}">'
            f'<div class="rag-role">{escape_html(label)}</div>'
            f'{body}'
            f'</div>'
        )

    missing = bundle.get('missing') or []
    missing_labels = [role_labels.get(k, k) for k in missing]
    status = (
        f'<p class="rag-status warn">⚠️ 以下要点暂未收录：{escape_html("、".join(missing_labels))}</p>'
        if missing
        else '<p class="rag-status ok">✅ 本运气年全部核心要点均已在知识库收录</p>'
    )
    return f'''
    <section class="section" id="rag-bundle">
      <h2 class="section-title font-serif">知识库精确命中</h2>
      <p style="color:var(--muted);font-size:0.9rem;margin-bottom:1rem;">
        代表日 <code>{escape_html(bundle.get("date", date_str))}</code>
        · 运气年 {escape_html(str(bundle.get("yunqi_year", "")))}
        （{escape_html(bundle.get("year_gz", ""))}）
      </p>
      <div class="rag-grid">
        {''.join(cards)}
      </div>
      {status}
    </section>
    '''


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


# 古典雅致·宣纸水墨 样式表（plain string；__DARK__/__LIGHT__/__PAPER_TEX__/__WASH__ 运行时替换）
_STYLE = """
*{box-sizing:border-box;margin:0;padding:0}
:root{__DARK__
  --text:var(--ink); --muted:var(--ink-3);
}
html.light{__LIGHT__
  --text:var(--ink); --muted:var(--ink-3);
}
body{font-family:var(--sans);color:var(--ink);line-height:1.75;min-height:100vh;background:var(--paper);}
body::before{content:"";position:fixed;inset:0;background:url('__PAPER_TEX__');opacity:.5;pointer-events:none;z-index:0}
main,header,footer,.toolbar{position:relative;z-index:1}
.font-serif{font-family:var(--serif)}

/* 五行正色 */
.wx-mu{color:var(--wx-mu)}.wx-huo{color:var(--wx-huo)}.wx-tu{color:var(--wx-tu)}.wx-jin{color:var(--wx-jin)}.wx-shui{color:var(--wx-shui)}
.bgc-mu{background:var(--wx-mu)}.bgc-huo{background:var(--wx-huo)}.bgc-tu{background:var(--wx-tu)}.bgc-jin{background:var(--wx-jin)}.bgc-shui{background:var(--wx-shui)}

/* 顶部工具条 */
.toolbar{position:fixed;top:1rem;right:1rem;display:flex;gap:.5rem;z-index:60}
.tbtn{font-family:var(--serif);cursor:pointer;border-radius:999px;border:1px solid var(--hairline);background:var(--card);color:var(--ink);padding:.5rem 1rem;font-size:.85rem;box-shadow:0 6px 18px rgba(0,0,0,.16)}
.tbtn-primary{background:var(--vermilion);border-color:var(--vermilion);color:#f7f1e3;font-weight:700}

/* Hero */
.hero{border-bottom:1px solid var(--hairline);position:relative;overflow:hidden}
.hero-wash{position:absolute;inset:-15% -10%;background:url('__WASH__') center/cover no-repeat;pointer-events:none}
.hero-grid{position:relative;max-width:1080px;margin:0 auto;padding:4.5rem 1.5rem 3.2rem;display:flex;justify-content:space-between;align-items:flex-end;gap:2rem}
.hero-eyebrow{font-family:var(--serif);color:var(--vermilion);letter-spacing:.45em;font-size:.82rem;margin-bottom:1.3rem}
.vtitle{font-family:var(--serif);font-weight:900;color:var(--ink);font-size:clamp(3rem,8vw,5.2rem);line-height:1.02;letter-spacing:.06em}
@media(min-width:840px){.vtitle{writing-mode:vertical-rl;letter-spacing:.32em;font-size:clamp(3.2rem,10vh,5.6rem)}}
.hero-sub{color:var(--ink-3);font-family:var(--serif);margin-top:1.5rem;font-size:1rem;letter-spacing:.05em}
.hero-meta{display:flex;flex-wrap:wrap;gap:1.8rem;margin-top:2.1rem;list-style:none}
.hero-meta li{display:flex;flex-direction:column;gap:.2rem;padding-left:1rem;border-left:1px solid var(--hairline)}
.hero-meta span{font-size:.75rem;color:var(--ink-4);letter-spacing:.2em}
.hero-meta b{font-family:var(--serif);font-size:1.3rem;font-weight:700;color:var(--ink)}
.hero-meta b.wx-mu{color:var(--wx-mu)}.hero-meta b.wx-huo{color:var(--wx-huo)}.hero-meta b.wx-tu{color:var(--wx-tu)}.hero-meta b.wx-jin{color:var(--wx-jin)}.hero-meta b.wx-shui{color:var(--wx-shui)}
.hero-seal{flex-shrink:0;align-self:center;filter:drop-shadow(0 4px 10px rgba(0,0,0,.2))}

/* 章节 */
.section{max-width:1080px;margin:0 auto;padding:3rem 1.5rem}
.sec-title{font-family:var(--serif);font-size:1.45rem;font-weight:700;color:var(--ink);display:flex;align-items:baseline;gap:.9rem;margin-bottom:1.8rem}
.sec-no{font-family:var(--serif);color:var(--vermilion);font-size:.9rem;letter-spacing:.1em;border:1px solid var(--hairline);border-radius:3px;padding:.1rem .45rem;transform:translateY(-.15em)}
.section-title{font-family:var(--serif);font-size:1.45rem;font-weight:700;color:var(--ink);display:flex;align-items:center;gap:.6rem;margin-bottom:1.8rem}
.section-title::before{content:"";width:1.4rem;height:2px;background:var(--vermilion)}

/* 当前聚焦（编辑感通栏） */
.focus{border-top:1px solid var(--hairline);border-bottom:1px solid var(--hairline);padding:2.2rem 0;position:relative}
.focus-head{display:flex;flex-wrap:wrap;align-items:baseline;gap:1.1rem}
.focus-name{font-family:var(--serif);font-weight:900;font-size:clamp(1.7rem,3.5vw,2.4rem);color:var(--ink)}
.focus-range{color:var(--ink-4);font-size:.9rem;font-family:var(--serif)}
.focus-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));margin-top:2rem}
.fcell{padding:1.1rem 1.4rem;border-left:1px solid var(--hairline)}
.fcell:first-child{border-left:none;padding-left:0}
.fcell .lab{color:var(--ink-4);font-size:.78rem;letter-spacing:.16em;margin-bottom:.35rem}
.fcell .val{font-family:var(--serif);font-size:1.35rem;font-weight:700;color:var(--ink)}
.fcell .val.wx-mu{color:var(--wx-mu)}.fcell .val.wx-huo{color:var(--wx-huo)}.fcell .val.wx-tu{color:var(--wx-tu)}.fcell .val.wx-jin{color:var(--wx-jin)}.fcell .val.wx-shui{color:var(--wx-shui)}
.shun{color:var(--wx-mu)}.ni{color:var(--wx-huo)}

/* 解读 */
.metaphor{font-family:var(--serif);font-size:1.12rem;line-height:1.95;color:var(--ink-2);padding:1.3rem 0 1.3rem 1.6rem;border-left:3px solid var(--vermilion);margin:0 0 2.3rem;background:linear-gradient(90deg,var(--paper-2),transparent 65%)}
.metaphor strong{color:var(--vermilion)}
.metaphor-sub{display:block;color:var(--ink-3);font-size:.92rem;margin-top:.6rem}
.read-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:2rem 2.6rem}
.read-item{border-top:1px solid var(--hairline);padding-top:1.1rem}
.read-item .tag{display:inline-block;font-family:var(--serif);color:var(--vermilion);font-size:.76rem;letter-spacing:.22em;border:1px solid var(--hairline);border-radius:999px;padding:.14rem .65rem;margin-bottom:.55rem}
.read-item h3{font-family:var(--serif);font-size:1.05rem;color:var(--ink);margin-bottom:.5rem;font-weight:700}
.read-item p{color:var(--ink-2);font-size:.94rem;line-height:1.85}

/* 六气 */
.qi{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));border-top:1px solid var(--hairline);border-bottom:1px solid var(--hairline)}
.qstep{padding:1.5rem 1.1rem;border-left:1px solid var(--hairline);position:relative}
.qstep:first-child{border-left:none}
.qstep-no{position:absolute;top:.85rem;right:.95rem;color:var(--ink-4);font-size:.74rem;font-family:var(--serif);letter-spacing:.05em}
.qstep.is-current{background:linear-gradient(180deg,var(--paper-2),transparent);box-shadow:inset 0 3px 0 var(--vermilion)}
.qstep.is-current .qstep-no{color:var(--vermilion);font-weight:700}
.qstep-name{font-family:var(--serif);font-weight:700;font-size:1.12rem;color:var(--ink);margin-bottom:.8rem}
.qstep-pair{display:flex;flex-direction:column;gap:.25rem;font-size:.9rem;margin-bottom:.65rem}
.qstep-rel{color:var(--ink-4);font-size:.8rem}
.qstep-marks{margin-top:.75rem;display:flex;gap:.35rem;flex-wrap:wrap}
.mark{font-style:normal;font-family:var(--serif);font-size:.68rem;padding:.14rem .5rem;border:1px solid var(--hairline);border-radius:2px;color:var(--ink-3)}
.mark-sitian{color:var(--wx-huo);border-color:var(--wx-huo)}
.mark-zaiquan{color:var(--wx-jin);border-color:var(--wx-jin)}
.mark-cur{background:var(--vermilion);border-color:var(--vermilion);color:#f7f1e3;font-weight:700}

/* 五运 */
.yun{display:flex;flex-wrap:wrap;border-top:1px solid var(--hairline)}
.ystep{flex:1 1 150px;padding:1.4rem 1.1rem;border-left:1px solid var(--hairline);text-align:center}
.ystep:first-child{border-left:none}
.ydot{display:block;width:.85rem;height:.85rem;border-radius:50%;margin:0 auto .75rem;border:2px solid var(--paper)}
.ylabel{color:var(--ink-4);font-size:.76rem;letter-spacing:.18em;margin-bottom:.4rem;font-family:var(--serif)}
.yval{font-family:var(--serif);font-weight:700;font-size:1.02rem;color:var(--ink)}
.yval i{color:var(--ink-4);font-style:normal;margin:0 .4rem}

/* 客主加临表 */
.kztable{width:100%;border-collapse:collapse}
.kztable th{font-family:var(--serif);font-weight:700;color:var(--ink-3);font-size:.82rem;letter-spacing:.14em;text-align:left;padding:.7rem .9rem;border-bottom:2px solid var(--ink)}
.kztable td{padding:.85rem .9rem;border-bottom:1px solid var(--hairline);font-size:.95rem;color:var(--ink-2)}
.kztable tr.row-cur td{background:linear-gradient(90deg,var(--paper-2),transparent);border-left:3px solid var(--vermilion);color:var(--ink)}
.kztable tr.row-cur td:first-child{font-weight:700}

/* RAG / 高级对齐（复用旧类名） */
.rag-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1.4rem}
.rag-card{background:var(--card);border:1px solid var(--hairline);border-top:3px solid var(--vermilion);border-radius:5px;padding:1.1rem 1.2rem}
.rag-role{font-family:var(--serif);font-weight:700;color:var(--ink);margin-bottom:.65rem;font-size:.98rem}
.rag-role code{color:var(--ink-4);font-weight:400;font-size:.78rem}
.rag-hit{margin-bottom:.75rem}.rag-hit:last-child{margin-bottom:0}
.rag-hit-title{color:var(--ink);font-size:.92rem;margin-bottom:.25rem}
.rag-meta{color:var(--ink-4);font-size:.76rem;font-weight:400}
.rag-hit p{color:var(--ink-3);font-size:.86rem;line-height:1.6;margin:0}
.rag-empty{color:var(--ink-4);font-size:.88rem;margin:0}
.rag-status{margin-top:1rem;font-size:.9rem}
.rag-status.ok{color:var(--wx-mu)}.rag-status.warn{color:var(--wx-tu)}
.jialin-table{width:100%;border-collapse:collapse}
.jialin-table th{font-family:var(--serif);color:var(--ink-3);font-size:.82rem;letter-spacing:.1em;text-align:left;padding:.6rem .9rem;border-bottom:2px solid var(--ink);width:36%}
.jialin-table td{padding:.7rem .9rem;border-bottom:1px solid var(--hairline);color:var(--ink-2)}
.jialin-table tr:last-child td{border-bottom:none}

/* 术语 / 免责 / 页脚 */
.gloss{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1.1rem 2.2rem;color:var(--ink-3);font-size:.92rem;line-height:1.8}
.gloss b{color:var(--vermilion);font-family:var(--serif);margin-right:.3rem}
.disclaimer{border:1px solid var(--hairline);border-left:4px solid var(--vermilion);background:var(--card);padding:1.3rem 1.5rem;color:var(--ink-3);font-size:.88rem;line-height:1.85;border-radius:4px}
.disclaimer strong{color:var(--vermilion);font-family:var(--serif)}
.foot{text-align:center;padding:2.2rem 1rem;color:var(--ink-4);font-size:.8rem;font-family:var(--serif);letter-spacing:.1em;border-top:1px solid var(--hairline)}

@media(max-width:640px){
  .hero-grid{padding:3rem 1.2rem 2.4rem;flex-direction:column;align-items:flex-start}
  .hero-seal{align-self:flex-end}
  .section{padding:2.2rem 1.2rem}
  .kztable th,.kztable td{padding:.7rem .5rem;font-size:.85rem}
}

/* 打印 / 存 PDF：浅色墨版 */
@media print{
  :root{__LIGHT__
    --text:var(--ink); --muted:var(--ink-3);
  }
  html,body{background:#f4efe4!important;color:#1c1a17!important}
  body::before{opacity:.35}
  .screen-only,.toolbar{display:none!important}
  .section{padding:1.6rem 0;max-width:100%}
  .hero-grid{padding:1.6rem 0 1.4rem}
  .avoid-break{break-inside:avoid;page-break-inside:avoid}
  .focus,.qi,.yun,.metaphor,.kztable tr{break-inside:avoid}
}
"""


def generate_html(data, advanced=None, with_rag_bundle=True):
    import ink_theme  # scripts/lib（get_data 已注入路径）

    date_str = data['date']
    year_gz = data['year_gz']
    sui_yun = data['sui_yun']
    si_tian = data['si_tian']
    zai_quan = data['zai_quan']
    current = data['current_step']
    rag_bundle_html = render_rag_bundle_section(date_str, with_rag_bundle=with_rag_bundle)

    WX = {'木': 'mu', '火': 'huo', '土': 'tu', '金': 'jin', '水': 'shui'}

    def qc(qi_name):
        return WX.get(LIUQI_WUXING.get(qi_name, '金'), 'jin')

    # 六气步位（竖列节律，宣纸水墨）
    qi_cards = []
    for step in data['ke_zhu_jia_lin']:
        is_current = step['step_number'] == current['step_number']
        zc = qc(step['zhu_qi'])
        kc = qc(step['ke_qi'])
        badge = ''
        if step['keqi_is_sitian']:
            badge = '<em class="mark mark-sitian">司天</em>'
        elif step['keqi_is_zaiquan']:
            badge = '<em class="mark mark-zaiquan">在泉</em>'
        cur_badge = '<em class="mark mark-cur">当前</em>' if is_current else ''
        qi_cards.append(f'''
        <div class="qstep{' is-current' if is_current else ''} reveal" data-d="{step['step_number']}">
          <span class="qstep-no">{step['step_number']:02d}</span>
          <div class="qstep-name">{step['step_name'].split('(')[0]}</div>
          <div class="qstep-pair">
            <span class="wx-{zc}">主 · {step['zhu_qi']}</span>
            <span class="wx-{kc}">客 · {step['ke_qi']}</span>
          </div>
          <div class="qstep-rel">{step['relation']} · {step['shun_ni']}</div>
          <div class="qstep-marks">{badge}{cur_badge}</div>
        </div>''')

    # 五运推移
    yun_timeline = []
    for zy, ky in zip(data['zhu_yun'], data['ke_yun']):
        zc = WX.get(zy['element'], 'jin')
        kc = WX.get(ky['element'], 'jin')
        yun_timeline.append(f'''
        <div class="ystep reveal" data-d="{zy['step']}">
          <span class="ydot bgc-{zc}"></span>
          <div class="ylabel">第{zy['step']}运</div>
          <div class="yval"><span class="wx-{zc}">主 {zy['tai_shao']}{zy['element']}运</span><i>·</i><span class="wx-{kc}">客 {ky['tai_shao']}{ky['element']}运</span></div>
        </div>''')

    # 客主加临顺逆表
    table_rows = []
    for step in data['ke_zhu_jia_lin']:
        is_current = step['step_number'] == current['step_number']
        zc = qc(step['zhu_qi'])
        kc = qc(step['ke_qi'])
        shun = step['shun_ni'].startswith('相得')
        table_rows.append(f'''
        <tr class="{'row-cur' if is_current else ''}">
          <td>{step['step_name'].split('(')[0]}</td>
          <td class="wx-{zc}">{step['zhu_qi']}</td>
          <td class="wx-{kc}">{step['ke_qi']}</td>
          <td>{step['relation']}</td>
          <td class="{'shun' if shun else 'ni'}">{step['shun_ni']}</td>
        </tr>''')

    interp = generate_interpretation(data)

    # 解读卡片（带错峰揭示动画）
    _reads = [
        ('全年气候', '这一年天气总基调', interp['year_climate']),
        ('身体提示', '哪些部位容易受影响', interp['year_body']),
        ('饮食建议', '怎么吃更顺当年气', interp['year_food']),
        ('当前气候', '这段时间怎么样', interp['step_climate'] + ' ' + interp['half_tip']),
        ('近期注意', '身体可能出现的信号', interp['step_body']),
        ('生活调理', '起居运动情绪建议', interp['step_tip']),
    ]
    read_grid_html = ''.join(
        f'<div class="read-item reveal" data-d="{i}"><span class="tag">{escape_html(t)}</span>'
        f'<h3>{escape_html(h)}</h3><p>{escape_html(p)}</p></div>'
        for i, (t, h, p) in enumerate(_reads, 1)
    )

    sui_c = WX.get(sui_yun['element'], 'jin')
    cur_zhu_c = qc(current['zhu_qi'])
    cur_ke_c = qc(current['ke_qi'])
    cur_shun = current['shun_ni'].startswith('相得')
    year_num = data['yunqi_year']
    seal_html = ink_theme.seal(year_gz)

    style = (_STYLE
             .replace('__DARK__', ink_theme.css_vars('dark'))
             .replace('__LIGHT__', ink_theme.css_vars('light'))
             .replace('__PAPER_TEX__', ink_theme.paper_texture(opacity=0.05))
             .replace('__WASH__', ink_theme.ink_wash(color='#8a8375', opacity=0.13))
             + ink_theme.MOTION)

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>五运六气 · {date_str} · {year_gz}年</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700;900&family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>{style}</style>
<noscript><style>.reveal{{opacity:1!important;transform:none!important}}</style></noscript>
</head>
<body>
  <div class="screen-only toolbar">
    <button class="tbtn" onclick="document.documentElement.classList.toggle('light')">墨 / 纸</button>
    <button class="tbtn tbtn-primary" onclick="window.print()">印 · 存 PDF</button>
  </div>

  <header class="hero">
    <div class="hero-wash" aria-hidden="true"></div>
    <div class="hero-grid">
      <div class="hero-main">
        <div class="hero-eyebrow">天人合一 · 气化流行</div>
        <h1 class="vtitle">五运六气</h1>
        <p class="hero-sub">{year_num}年（{year_gz}）· 第{data['sexagenary_index']}甲子 · 生肖{data['shengxiao']} · {date_str}</p>
        <ul class="hero-meta">
          <li><span>岁运</span><b class="wx-{sui_c}">{sui_yun['name']}{sui_yun['status']}</b></li>
          <li><span>司天</span><b>{si_tian}</b></li>
          <li><span>在泉</span><b>{zai_quan}</b></li>
          <li><span>日干支</span><b>{data['day_gz']}</b></li>
        </ul>
      </div>
      <div class="hero-seal" aria-hidden="true">{seal_html}</div>
    </div>
  </header>

  <main>
    <section class="section">
      <div class="focus avoid-break reveal">
        <div class="focus-head">
          <h2 class="focus-name">当前步位 · {current['name']}</h2>
          <span class="focus-range">{current['date_range']['start']} — {current['date_range']['end']}</span>
        </div>
        <div class="focus-grid">
          <div class="fcell"><div class="lab">主气</div><div class="val wx-{cur_zhu_c}">{current['zhu_qi']}</div></div>
          <div class="fcell"><div class="lab">客气</div><div class="val wx-{cur_ke_c}">{current['ke_qi']}</div></div>
          <div class="fcell"><div class="lab">客主加临</div><div class="val">{current['relation']}</div></div>
          <div class="fcell"><div class="lab">顺逆</div><div class="val {'shun' if cur_shun else 'ni'}">{current['shun_ni']}</div></div>
        </div>
      </div>
    </section>

    <section class="section">
      <h2 class="sec-title reveal"><span class="sec-no">壹</span>报告解读</h2>
      <blockquote class="metaphor avoid-break reveal">
        <strong>一句话理解 ·</strong> {interp['metaphor']}
        <span class="metaphor-sub">今年整体为「{sui_yun['name']}{sui_yun['status']}」，上半年由「{si_tian}」主令，下半年由「{zai_quan}」主令；你此刻正行于「{current['name']}」。</span>
      </blockquote>
      <div class="read-grid">{read_grid_html}</div>
    </section>

    <section class="section avoid-break">
      <h2 class="sec-title reveal"><span class="sec-no">贰</span>六气步位</h2>
      <div class="qi">{''.join(qi_cards)}</div>
    </section>

    <section class="section avoid-break">
      <h2 class="sec-title reveal"><span class="sec-no">叁</span>五运推移</h2>
      <div class="yun">{''.join(yun_timeline)}</div>
    </section>

    <section class="section avoid-break">
      <h2 class="sec-title reveal"><span class="sec-no">肆</span>客主加临顺逆</h2>
      <div style="overflow-x:auto">
        <table class="kztable reveal">
          <thead><tr><th>步位</th><th>主气</th><th>客气</th><th>关系</th><th>顺逆</th></tr></thead>
          <tbody>{''.join(table_rows)}</tbody>
        </table>
      </div>
    </section>

    {rag_bundle_html}

    {render_advanced_alignment_section(advanced)}

    <section class="section">
      <h2 class="sec-title reveal"><span class="sec-no">伍</span>术语速查</h2>
      <div class="gloss reveal">
        <div><b>岁运</b>即大运，一年之总气，由年干所化。</div>
        <div><b>司天</b>主上半年之气，由年支所化。</div>
        <div><b>在泉</b>主下半年之气，与司天相对。</div>
        <div><b>主气</b>六气恒序，自初之气厥阴风木至终之气太阳寒水。</div>
        <div><b>客气</b>逐年流转之六气，以司天为第三气。</div>
        <div><b>客主加临</b>客气加于主气之上，按五行生克判顺逆。</div>
      </div>
    </section>

    <section class="section">
      <div class="disclaimer reveal"><strong>免责声明</strong>：{CONTEXT_DISCLAIMERS['general_report']}</div>
    </section>
  </main>

  <footer class="foot">五运六气 · 宣纸水墨版 · 由 wuyun-liuqi-skills 生成 · {date_str}</footer>
{ink_theme.reveal_script()}
</body>
</html>'''
    return html


def main():
    if len(sys.argv) < 2:
        print(
            "用法: python scripts/generate_html_report.py <YYYY-MM-DD> [输出路径] "
            "[--with-advanced-alignment --birth-date YYYY-MM-DD --city 城市] "
            "[--mock] [--no-weather] [--no-rag-bundle]"
        )
        print("示例: python scripts/generate_html_report.py 2026-06-29 reports/generated/wuyun-liuqi-report.html")
        sys.exit(1)

    date_str = sys.argv[1]
    positional = []
    advanced_kwargs = {}
    with_rag_bundle = True
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
        elif arg == '--no-rag-bundle':
            with_rag_bundle = False
        elif arg == '--timeout' and i + 1 < len(sys.argv):
            advanced_kwargs['timeout'] = int(sys.argv[i + 1])
            i += 1
        elif not arg.startswith('--'):
            positional.append(arg)
        i += 1

    output_path = positional[0] if positional else os.path.join(BASE_DIR, 'reports', 'generated', f'wuyun-liuqi-report-{date_str}.html')
    msg = write_html_report(
        date_str,
        output_path=output_path,
        advanced_kwargs=advanced_kwargs,
        with_rag_bundle=with_rag_bundle,
    )
    sys.stdout.write(msg)
    sys.stdout.flush()


if __name__ == '__main__':
    main()
