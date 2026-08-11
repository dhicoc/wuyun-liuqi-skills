#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运气时间轴可视化 - OPT-07

生成全年运气时间轴 HTML（12 个月 × 六步 × 客气/主气/运），
标注关键节点（天符岁会、平气判定、太过不及、不相得逆步）。

用法:
  python scripts/visualize_timeline.py 2026
  python scripts/visualize_timeline.py 2026 --output timeline.html
"""

import json
import sys
from pathlib import Path
from html import escape

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from calculate_yunqi_api import calculate_yunqi_api
from lib.ink_theme import (
    wx_color, liuqi_color,
    css_vars, paper_texture, seal, MOTION,
)

KB = SCRIPT_DIR.parent / "rag-knowledge-base"


def _load_kj_entries():
    p = KB / "asset3_kezhujialin.json"
    if p.exists():
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
    year_gz = yq.get("year_gz", "")
    shengxiao = yq.get("shengxiao", "")

    step_ranges = [
        ("大寒~春分",), ("春分~小满",), ("小满~大暑",),
        ("大暑~秋分",), ("秋分~小雪",), ("小雪~大寒",),
    ]

    kj_entries = _load_kj_entries()
    suiyun_name = suiyun.get("name", "")
    suiyun_status = suiyun.get("status", "")
    suiyun_element = suiyun.get("element", "")
    suiyun_color = wx_color(suiyun_element)

    is_pingqi = tonghua.get("pingqi", False)
    is_tianfu = tonghua.get("tianfu", False)
    is_suihui = tonghua.get("suihui", False)

    six_steps = []
    for i, s in enumerate(kj_steps[:6]):
        zhu = s.get("zhu_qi", "")
        ke = s.get("ke_qi", "")
        rel = s.get("relation", "")
        shun_ni = s.get("shun_ni", "")
        kj_detail = _find_kj(kj_entries, zhu, ke)
        is_ni = "不相得" in shun_ni or "逆" in shun_ni
        six_steps.append({
            "step": i + 1,
            "name": s.get("step_name", f"{i+1}之气"),
            "zhu_qi": zhu, "ke_qi": ke,
            "zhu_color": liuqi_color(zhu), "ke_color": liuqi_color(ke),
            "relation": rel, "shun_ni": shun_ni, "is_ni": is_ni,
            "pathogenesis": kj_detail.get("pathogenesis", ""),
            "range": step_ranges[i][0] if i < len(step_ranges) else "",
            "is_sitian": s.get("keqi_is_sitian", False),
            "is_zaiquan": s.get("keqi_is_zaiquan", False),
        })

    zhu_yun_steps = [
        {"element": zy.get("element",""), "tai_shao": zy.get("tai_shao",""),
         "color": wx_color(zy.get("element",""))}
        for zy in zhu_yun[:5]
    ]

    return _build_html(year, year_gz, shengxiao, suiyun_name, suiyun_status,
                       suiyun_element, suiyun_color, sitian, zaiquan,
                       is_pingqi, is_tianfu, is_suihui, six_steps, zhu_yun_steps)


def _build_html(year, year_gz, shengxiao, suiyun_name, suiyun_status,
                suiyun_element, suiyun_color, sitian, zaiquan,
                is_pingqi, is_tianfu, is_suihui, six_steps, zhu_yun_steps):
    months = ["1月","2月","3月","4月","5月","6月","7月","8月","9月","10月","11月","12月"]

    # 徽章
    badges = []
    if is_pingqi: badges.append('<span class="badge badge-pingqi">⚖ 平气</span>')
    if is_tianfu: badges.append('<span class="badge badge-tianfu">★ 天符</span>')
    if is_suihui: badges.append('<span class="badge badge-suihui">◆ 岁会</span>')
    if suiyun_status == "太过":
        badges.append(f'<span class="badge badge-taiguo">↑ {suiyun_element}运太过</span>')
    elif suiyun_status == "不及":
        badges.append(f'<span class="badge badge-buji">↓ {suiyun_element}运不及</span>')
    badges_str = "".join(badges)

    seal_svg = seal(year_gz, size=72)

    # 六步卡片
    step_cards = []
    for s in six_steps:
        ni_class = " ni" if s["is_ni"] else ""
        rel_class = "relation-ni" if s["is_ni"] else "relation-shun"
        tag = ""
        if s["is_sitian"]: tag = '<span class="tag tag-sitian">司天</span>'
        elif s["is_zaiquan"]: tag = '<span class="tag tag-zaiquan">在泉</span>'
        step_cards.append(f"""      <div class="step-card{ni_class}">
        {tag}
        <div class="step-num">第{s["step"]}步 · {escape(s["name"])}</div>
        <div class="step-range">{escape(s["range"])}</div>
        <div class="qi-row"><span class="qi-dot" style="background:{s["zhu_color"]}"></span>主 {escape(s["zhu_qi"])}</div>
        <div class="qi-row"><span class="qi-dot" style="background:{s["ke_color"]}"></span>客 {escape(s["ke_qi"])}</div>
        <span class="relation {rel_class}">{escape(s["relation"])} · {escape(s["shun_ni"])}</span>
        <div class="pathogenesis">{escape(s["pathogenesis"][:100])}</div>
      </div>""")
    steps_html = "\n".join(step_cards)

    # 主运五步
    zy_items = []
    for zy in zhu_yun_steps:
        zy_items.append(f"""      <div class="zhu-yun-item">
        <div class="el"><span style="background:{zy["color"]};width:10px;height:10px;display:inline-block;border-radius:50%;margin-right:4px"></span>{escape(zy["element"])}</div>
        <div class="ts">{escape(zy["tai_shao"])}</div>
      </div>""")
    zy_html = "\n".join(zy_items)

    months_html = "".join(f"<div>{m}</div>" for m in months)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{year}年（{year_gz}）运气时间轴</title>
<style>
{css_vars('dark')}
{paper_texture(0.03)}
{MOTION}
body {{ background: var(--paper); font-family: var(--serif); color: var(--ink); margin: 0; padding: 2rem 1rem; }}
.container {{ max-width: 1200px; margin: 0 auto; }}
h1 {{ text-align: center; font-size: 2rem; margin-bottom: 0.3rem; }}
.subtitle {{ text-align: center; color: var(--ink-60); margin-bottom: 1rem; font-size: 1.1rem; }}
.overview {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }}
.overview-card {{ background: rgba(255,255,255,0.6); border: 1px solid var(--ink-20); border-radius: 8px; padding: 1rem; }}
.overview-card .label {{ font-size: 0.85rem; color: var(--ink-60); }}
.overview-card .value {{ font-size: 1.2rem; font-weight: 600; }}
.wx-badge {{ display: inline-block; width: 14px; height: 14px; border-radius: 50%; margin-right: 6px; vertical-align: middle; }}
.badges {{ text-align: center; margin-bottom: 1.5rem; }}
.badge {{ display: inline-block; padding: 3px 12px; margin: 0 4px; border-radius: 12px; font-size: 0.85rem; }}
.badge-tianfu {{ background: #b23a2e; color: #f7f1e3; }}
.badge-suihui {{ background: #8b6914; color: #f7f1e3; }}
.badge-pingqi {{ background: #2d6e4e; color: #f7f1e3; }}
.badge-taiguo {{ background: #c0392b; color: #f7f1e3; }}
.badge-buji {{ background: #2c3e50; color: #f7f1e3; }}
.section-title {{ font-size: 1.3rem; margin-bottom: 1rem; border-left: 4px solid var(--vermilion); padding-left: 10px; }}
.timeline {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px; }}
.step-card {{ background: rgba(255,255,255,0.7); border: 1px solid var(--ink-20); border-radius: 8px; padding: 0.8rem; position: relative; }}
.step-card.ni {{ border-color: var(--vermilion); box-shadow: 0 0 8px rgba(178,58,46,0.2); }}
.step-num {{ font-size: 0.8rem; color: var(--ink-60); }}
.step-range {{ font-size: 0.75rem; color: var(--ink-50); }}
.qi-row {{ display: flex; align-items: center; gap: 4px; margin: 4px 0; font-size: 0.9rem; }}
.qi-dot {{ width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }}
.relation {{ font-size: 0.75rem; padding: 2px 6px; border-radius: 8px; display: inline-block; margin: 4px 0; }}
.relation-shun {{ background: rgba(45,110,78,0.15); color: #2d6e4e; }}
.relation-ni {{ background: rgba(178,58,46,0.15); color: #b23a2e; }}
.pathogenesis {{ font-size: 0.8rem; color: var(--ink-70); margin-top: 6px; line-height: 1.5; }}
.tag {{ position: absolute; top: 6px; right: 6px; font-size: 0.65rem; padding: 1px 6px; border-radius: 8px; }}
.tag-sitian {{ background: var(--vermilion); color: #f7f1e3; }}
.tag-zaiquan {{ background: var(--gold); color: #f7f1e3; }}
.zhu-yun {{ display: flex; gap: 8px; margin-top: 1rem; }}
.zhu-yun-item {{ flex: 1; text-align: center; padding: 0.6rem; border-radius: 6px; background: rgba(255,255,255,0.6); border: 1px solid var(--ink-20); }}
.month-axis {{ display: grid; grid-template-columns: repeat(12, 1fr); margin-bottom: 6px; font-size: 0.75rem; color: var(--ink-60); }}
.month-axis div {{ text-align: center; }}
.disclaimer {{ text-align: center; margin-top: 2rem; padding: 1rem; font-size: 0.8rem; color: var(--ink-50); border-top: 1px dashed var(--ink-20); }}
</style>
</head>
<body>
<div class="container">
  <div style="text-align:center;margin-bottom:1rem">{seal_svg}</div>
  <h1>{year}年（{escape(year_gz)}）运气时间轴</h1>
  <div class="subtitle">{escape(shengxiao)}年 · {escape(sitian)}司天 · {escape(zaiquan)}在泉</div>
  <div class="badges">{badges_str}</div>
  <div class="overview">
    <div class="overview-card"><div class="label">岁运</div><div class="value"><span class="wx-badge" style="background:{suiyun_color}"></span>{escape(suiyun_name)} · {escape(suiyun_status)}</div></div>
    <div class="overview-card"><div class="label">司天（上半年）</div><div class="value"><span class="wx-badge" style="background:{liuqi_color(sitian)}"></span>{escape(sitian)}</div></div>
    <div class="overview-card"><div class="label">在泉（下半年）</div><div class="value"><span class="wx-badge" style="background:{liuqi_color(zaiquan)}"></span>{escape(zaiquan)}</div></div>
    <div class="overview-card"><div class="label">干支</div><div class="value">{escape(year_gz)} · {escape(shengxiao)}</div></div>
  </div>
  <div class="month-axis">{months_html}</div>
  <div class="timeline-section">
    <div class="section-title">六步客主加临</div>
    <div class="timeline">
{steps_html}
    </div>
  </div>
  <div class="timeline-section">
    <div class="section-title">主运五步（太少相生）</div>
    <div class="zhu-yun">
{zy_html}
    </div>
  </div>
  <div class="disclaimer">⚠ 以上为运气时间轴可视化，临床应用须结合个体辨证。公版典籍蒸馏，仅供学术研究。</div>
</div>
</body>
</html>"""


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description="生成运气时间轴 HTML")
    parser.add_argument("year", help="年份（如 2026）或 today")
    parser.add_argument("--output", "-o", default=None, help="输出文件路径")
    args = parser.parse_args(argv if argv is not None else None)

    if args.year.lower() == "today":
        from datetime import date
        year = date.today().year
    else:
        year = int(args.year)

    html = generate_timeline_html(year)

    if args.output:
        Path(args.output).write_text(html, encoding="utf-8")
        print(f"✅ 已生成: {args.output} ({len(html)} bytes)")
    else:
        print(html)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
