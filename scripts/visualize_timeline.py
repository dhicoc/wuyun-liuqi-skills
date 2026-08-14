#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运气时间轴可视化 - OPT-07（复用可视化报告 UI 体系）

复用 generate_html_report.py 的 _STYLE + ink_theme 宣纸水墨设计，
生成全年运气时间轴 HTML。

用法:
  python scripts/visualize_timeline.py 2026
  python scripts/visualize_timeline.py 2026 --output timeline.html
"""

import sys
import os
from pathlib import Path
from html import escape

# 复用报告脚本的公共初始化
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
from _common import setup_environment, add_scripts_dir_to_path
setup_environment(add_lib=False, add_scripts=True)

from _safety_text import CONTEXT_DISCLAIMERS

from calculate_yunqi_api import calculate_yunqi_api
from generate_html_report import _STYLE, escape_html, LIUQI_WUXING
import ink_theme

KB = Path(__file__).resolve().parent.parent / "rag-knowledge-base"

# 六气→五行色映射（与报告一致）
WX = {'木': 'mu', '火': 'huo', '土': 'tu', '金': 'jin', '水': 'shui'}


def _qc(qi_name):
    return WX.get(LIUQI_WUXING.get(qi_name, '金'), 'jin')


def _load_kj_entries():
    p = KB / "asset3_kezhujialin.json"
    if p.exists():
        import json
        return json.loads(p.read_text(encoding="utf-8")).get("entries", [])
    return []


def _find_kj(kj_entries, zhu, ke):
    for e in kj_entries:
        if e.get("zhu_qi") == zhu and e.get("ke_qi") == ke:
            return e
    return {}


def generate_timeline_html(year: int) -> str:
    yq = calculate_yunqi_api(year)
    suiyun = yq.get("sui_yun", {})
    sitian = yq.get("si_tian", "")
    zaiquan = yq.get("zai_quan", "")
    tonghua = yq.get("tong_hua", {})
    kj_steps = yq.get("ke_zhu_jia_lin", [])
    zhu_yun = yq.get("zhu_yun", [])
    ke_yun = yq.get("ke_yun", [])
    year_gz = yq.get("year_gz", "")
    shengxiao = yq.get("shengxiao", "")
    sexagenary = yq.get("sexagenary_index", "")

    kj_entries = _load_kj_entries()
    suiyun_name = suiyun.get("name", "")
    suiyun_status = suiyun.get("status", "")
    suiyun_element = suiyun.get("element", "")
    suiyun_code = suiyun.get("code", "")
    suiyun_c = WX.get(suiyun_element, 'jin')
    si_c = _qc(sitian)
    zq_c = _qc(zaiquan)

    is_pingqi = tonghua.get("pingqi", False)
    is_tianfu = tonghua.get("tianfu", False)
    is_suihui = tonghua.get("suihui", False)

    # 六步卡片（复用报告 .qstep 样式）
    qi_cards = []
    for s in kj_steps[:6]:
        zhu = s.get("zhu_qi", "")
        ke = s.get("ke_qi", "")
        rel = s.get("relation", "")
        shun_ni = s.get("shun_ni", "")
        zc = _qc(zhu)
        kc = _qc(ke)
        is_ni = "不相得" in shun_ni or "逆" in shun_ni
        kj_detail = _find_kj(kj_entries, zhu, ke)
        pathogenesis = kj_detail.get("pathogenesis", "")
        clinical = kj_detail.get("clinical_focus", "")

        badge = ''
        if s.get("keqi_is_sitian"):
            badge = '<em class="mark mark-sitian">司天</em>'
        elif s.get("keqi_is_zaiquan"):
            badge = '<em class="mark mark-zaiquan">在泉</em>'
        ni_badge = f'<em class="mark mark-ni" style="color:var(--wx-huo);border-color:var(--wx-huo)">逆</em>' if is_ni else ''

        qi_cards.append(f'''
        <div class="qstep{' is-ni' if is_ni else ''} reveal" data-d="{s.get('step_number', 0)}">
          <span class="qstep-no">{s.get('step_number', 0):02d}</span>
          <div class="qstep-name">{escape_html(s.get('step_name', '').split('(')[0])}</div>
          <div class="qstep-pair">
            <span class="wx-{zc}">主 · {escape_html(zhu)}</span>
            <span class="wx-{kc}">客 · {escape_html(ke)}</span>
          </div>
          <div class="qstep-rel">{escape_html(rel)} · {escape_html(shun_ni)}</div>
          <div class="qstep-marks">{badge}{ni_badge}</div>
          {'<div class="qstep-path">'+escape_html(pathogenesis[:80])+'</div>' if pathogenesis else ''}
        </div>''')

    # 五运推移（复用报告 .yun 样式）
    yun_timeline = []
    for zy, ky in zip(zhu_yun[:5], ke_yun[:5]):
        zc = WX.get(zy.get("element", ""), 'jin')
        kc = WX.get(ky.get("element", ""), 'jin')
        yun_timeline.append(f'''
        <div class="ystep reveal" data-d="{zy.get('step', 0)}">
          <span class="ydot bgc-{zc}"></span>
          <div class="ylabel">第{zy.get('step', 0)}运</div>
          <div class="yval"><span class="wx-{zc}">主 {escape_html(zy.get('tai_shao', ''))}{escape_html(zy.get('element', ''))}运</span><i>·</i><span class="wx-{kc}">客 {escape_html(ky.get('tai_shao', ''))}{escape_html(ky.get('element', ''))}运</span></div>
        </div>''')

    # 徽章
    badges = []
    if is_pingqi:
        badges.append('<em class="badge-mark mark mark-cur">⚖ 平气</em>')
    if is_tianfu:
        badges.append('<em class="badge-mark mark mark-sitian">★ 天符</em>')
    if is_suihui:
        badges.append('<em class="badge-mark mark mark-zaiquan">◆ 岁会</em>')
    if suiyun_status == "太过":
        badges.append(f'<em class="badge-mark mark" style="color:var(--wx-huo);border-color:var(--wx-huo)">↑ {escape_html(suiyun_element)}运太过</em>')
    elif suiyun_status == "不及":
        badges.append(f'<em class="badge-mark mark" style="color:var(--wx-shui);border-color:var(--wx-shui)">↓ {escape_html(suiyun_element)}运不及</em>')
    badges_html = '<div class="badge-row">' + ''.join(badges) + '</div>' if badges else ''

    seal_html = ink_theme.seal(year_gz)

    # 复用报告 _STYLE + ink_theme 注入
    style = (_STYLE
             .replace('__DARK__', ink_theme.css_vars('dark'))
             .replace('__LIGHT__', ink_theme.css_vars('light'))
             .replace('__PAPER_TEX__', ink_theme.paper_texture(opacity=0.05))
             .replace('__WASH__', ink_theme.ink_wash(color='#8a8375', opacity=0.13))
             + ink_theme.MOTION)

    # 时间轴专属补充样式
    extra_style = '''
<style>
.qstep.is-ni{box-shadow:inset 0 3px 0 var(--wx-huo);background:linear-gradient(180deg,rgba(251,113,133,.06),transparent)}
.qstep-path{margin-top:.6rem;font-size:.78rem;color:var(--ink-4);line-height:1.5;border-top:1px dashed var(--hairline);padding-top:.4rem}
.badge-row{display:flex;gap:.5rem;flex-wrap:wrap;margin-top:1.2rem}
.badge-mark{font-size:.78rem!important;letter-spacing:.05em!important}
</style>'''

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>运气时间轴 · {year}年（{year_gz}）</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700;900&family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>{style}</style>
{extra_style}
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
        <div class="hero-eyebrow">气化流行 · 周年回环</div>
        <h1 class="vtitle">运气时间轴</h1>
        <p class="hero-sub">{year}年（{year_gz}）· 第{sexagenary}甲子 · 生肖{escape_html(shengxiao)}</p>
        <ul class="hero-meta">
          <li><span>岁运</span><b class="wx-{suiyun_c}">{escape_html(suiyun_name)}{escape_html(suiyun_status)}</b></li>
          <li><span>司天</span><b class="wx-{si_c}">{escape_html(sitian)}</b></li>
          <li><span>在泉</span><b class="wx-{zq_c}">{escape_html(zaiquan)}</b></li>
        </ul>
        {badges_html}
      </div>
      <div class="hero-seal" aria-hidden="true">{seal_html}</div>
    </div>
  </header>

  <main>
    <section class="section">
      <h2 class="sec-title reveal"><span class="sec-no">壹</span>六气步位 · 客主加临</h2>
      <div class="qi">{''.join(qi_cards)}</div>
    </section>

    <section class="section">
      <h2 class="sec-title reveal"><span class="sec-no">贰</span>五运推移 · 太少相生</h2>
      <div class="yun">{''.join(yun_timeline)}</div>
    </section>

    <section class="section">
      <div class="disclaimer reveal"><strong>免责声明</strong>：{CONTEXT_DISCLAIMERS['timeline']}</div>
    </section>
  </main>

  <footer class="foot">运气时间轴 · 宣纸水墨版 · 由 wuyun-liuqi-skills 生成 · {year}年（{year_gz}）</footer>
{ink_theme.reveal_script()}
</body>
</html>'''
    return html


def main(argv=None):
    import argparse
    import os
    import tempfile
    parser = argparse.ArgumentParser(description="生成运气时间轴 HTML（复用报告 UI）")
    parser.add_argument("year", help="年份（如 2026）或 today")
    parser.add_argument("--output", "-o", default=None,
                        help="输出文件路径（默认打印到 stdout；Windows 下 /tmp/... 会自动归一到系统临时目录）")
    args = parser.parse_args(argv if argv is not None else None)

    if args.year.lower() == "today":
        from datetime import date
        year = date.today().year
    else:
        year = int(args.year)

    html = generate_timeline_html(year)

    if args.output:
        out = args.output
        # Windows 下 `/tmp/x.html` 会被 Path 误解析为 `<盘符>:/tmp/x.html`，
        # 将 Unix 风格 /tmp 归一到系统临时目录，避免文件落到盘根。
        if os.name == "nt" and (out.startswith("/tmp/") or out == "/tmp"):
            rest = out[len("/tmp"):].lstrip("/")
            out_path = Path(tempfile.gettempdir()) / rest
        else:
            out_path = Path(out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding="utf-8")
        print(f"✅ 已生成: {out_path} ({len(html)} bytes)")
    else:
        print(html)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
