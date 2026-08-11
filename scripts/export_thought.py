#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出功能：思想摘要 / 卡片集 / PDF（专注“帮助理解运气学思想”）

用法示例:
  python scripts/export_thought.py today --format summary --output reports/generated/thought_2026.md
  python scripts/export_thought.py 2026 --format cards --output reports/generated/
  python scripts/export_thought.py 2026 --format pdf --output reports/generated/thought_report_2026.pdf
  python scripts/export_thought.py today --format all

支持:
- 纯文本思想摘要 (Markdown / 纯文本)：聚焦哲学、现代连接、反思问题
- 卡片集：Anki TSV + 可读 Markdown flashcards
- PDF：优先生成高质量 HTML（浏览器打印为PDF最佳），同时尝试 fpdf2 生成轻量 PDF

定位对齐：所有导出都强调“思想层解读”、概念哲学、现代比喻、反思问题，而非仅推算数据。
"""

import sys
import os
import argparse
from datetime import datetime
from pathlib import Path

from _common import setup_environment, resolve_year_or_date
setup_environment(add_lib=True, add_scripts=True)

from calculate_yunqi_api import calculate_yunqi_api  # noqa: E402
from yunqi_report import (  # noqa: E402
    build_thought_layer_section,
    CONCEPT_PHILOSOPHY,
    explain_concept,
    DISCLAIMER,
)
import ink_theme  # noqa: E402  scripts/lib（setup_environment 已注入 lib 路径）

# 可选 PDF
FPDF_AVAILABLE = False
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    pass


def get_year_and_data(date_input):
    """解析日期，返回年份 + 完整计算结果 + 思想相关数据"""
    date_str = resolve_year_or_date(str(date_input).strip())
    result = calculate_yunqi_api(date_str)

    year = result['yunqi_year']
    tg = result['year_gan']
    dz = result['year_zhi']
    dayun = result['sui_yun']['element']
    taiguo = result['sui_yun']['status'] == '太过'
    sitian = result['si_tian']
    zaiquan = result['zai_quan']
    tianfu = result['tong_hua']['tianfu']
    suihui = result['tong_hua']['suihui']
    pingqi = result['tong_hua']['pingqi']

    return {
        'date_str': date_str,
        'year': year,
        'tg': tg,
        'dz': dz,
        'dayun': dayun,
        'taiguo': taiguo,
        'sitian': sitian,
        'zaiquan': zaiquan,
        'tianfu': tianfu,
        'suihui': suihui,
        'pingqi': pingqi,
        'full_result': result,
    }


def generate_thought_summary(data, audience='student'):
    """生成纯文本/ Markdown 思想摘要（核心导出）"""
    year = data['year']
    tg, dz = data['tg'], data['dz']
    dayun = data['dayun']
    taiguo = data['taiguo']
    sitian = data['sitian']
    zaiquan = data['zaiquan']
    tianfu = data['tianfu']
    suihui = data['suihui']
    pingqi = data['pingqi']

    lines = []
    lines.append(f"# 五运六气 · 思想摘要（{year}年 {tg}{dz}）")
    lines.append("")
    lines.append("**核心定位**：本摘要聚焦运气学背后的宇宙观、生命观与实践启发，帮助你真正理解思想，而非仅记住结果。")
    lines.append("")

    # 思想层解读（完整复用）
    thought = build_thought_layer_section(
        year, tg, dz, dayun, taiguo, sitian, zaiquan,
        tianfu, suihui, pingqi
    )
    lines.append(thought)
    lines.append("")

    # 核心概念深度
    lines.append("## 核心概念 · 哲学 + 现代连接")
    lines.append("")

    key_concepts = ['天人合一', '气化', '中和', '天符']
    for cname in key_concepts:
        if cname in CONCEPT_PHILOSOPHY:
            c = CONCEPT_PHILOSOPHY[cname]
            lines.append(f"### {cname}")
            lines.append(f"- **哲学思想**：{c['philosophy']}")
            lines.append(f"- **现代比喻**：{c['modern']}")
            lines.append(f"- **本年示例**：{c.get('example', '结合当前格局体悟')}")
            lines.append("")

    # 反思问题（帮助内化）
    lines.append("## 引导性反思问题（推荐你写下来）")
    lines.append("")
    reflections = [
        f"今年（{tg}{dz}）的格局最触动你的是哪一点？它如何对应你当下的生活节奏或健康状态？",
        "‘太过则伤’或‘不及则侮’在你身上或周围人身上有什么具体体现？你会如何主动调和？",
        "天人合一在现代社会最难实践的一点是什么？你愿意从哪个小习惯开始？",
        "如果把这个格局看作一个‘老师’，它想教给你什么关于时间、节律、中道的智慧？",
        "结合你的体质或出生年份，这个格局给你最想记住的一个思想提醒是什么？",
    ]
    for i, q in enumerate(reflections, 1):
        lines.append(f"{i}. {q}")
    lines.append("")

    lines.append("## 实践小建议")
    lines.append("- 把上面 1-2 个反思问题记在笔记里，过 1-2 周再回顾。")
    lines.append("- 想深入某个概念？运行：`python scripts/calculate_yunqi_api.py today --explain-concept \"天人合一\"`")
    lines.append("- 想追踪理解进展：`python scripts/self_evolve.py report`")
    lines.append("")

    lines.append("---")
    lines.append(DISCLAIMER.strip() if isinstance(DISCLAIMER, str) else DISCLAIMER)
    lines.append("")

    return '\n'.join(lines)


# ── 古典打印 / 卡片样式（plain string；__LIGHT__/__PAPER_TEX__/__WASH__ 运行时替换）──
_PRINT_STYLE = """
@page{size:A4;margin:18mm 16mm}
*{box-sizing:border-box;margin:0;padding:0}
:root{__LIGHT__
  --text:var(--ink);--muted:var(--ink-3);
}
body{font-family:var(--sans);color:var(--ink);background:#f4efe4 url('__PAPER_TEX__');line-height:1.9;font-size:15px;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.cover{min-height:86vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;page-break-after:always}
.eyebrow{font-family:var(--serif);color:var(--vermilion);letter-spacing:.5em;font-size:.85rem;margin-bottom:2rem}
.vtitle{font-family:var(--serif);font-weight:900;font-size:5rem;letter-spacing:.18em;writing-mode:vertical-rl;color:var(--ink)}
.csub{font-family:var(--serif);font-size:1.35rem;color:var(--ink-3);margin-top:2rem;letter-spacing:.32em}
.meta{font-family:var(--serif);color:var(--ink-3);margin-top:1.1rem;font-size:1rem}
.seal{margin-top:2.2rem}
.cfoot{margin-top:3rem;font-family:var(--serif);color:var(--ink-4);font-size:.8rem;letter-spacing:.2em}
.content{max-width:680px;margin:0 auto}
.content h1{font-family:var(--serif);font-size:1.7rem;color:var(--ink);border-bottom:2px solid var(--ink);padding-bottom:.4rem;margin:1.4rem 0 1rem}
.content h2{font-family:var(--serif);font-size:1.28rem;color:var(--ink);margin:1.5rem 0 .7rem;padding-left:.8rem;border-left:4px solid var(--vermilion);break-after:avoid}
.content h3{font-family:var(--serif);font-size:1.08rem;color:var(--ink);margin:1.2rem 0 .5rem;break-after:avoid}
.content p{color:var(--ink-2);margin:.5rem 0}
.content ul,.content ol{color:var(--ink-2);margin:.5rem 0 .5rem 1.4rem}
.content li{margin:.3rem 0}
.content strong{color:var(--vermilion)}
.brush{height:22px;background:url('__WASH__') center/contain no-repeat;margin:1.4rem 0;opacity:.8}
@media print{.cover{min-height:auto}}
"""

_CARDS_STYLE = """
*{box-sizing:border-box;margin:0;padding:0}
:root{__LIGHT__
  --text:var(--ink);--muted:var(--ink-3);
}
body{font-family:var(--sans);color:var(--ink);background:var(--paper) url('__PAPER_TEX__');line-height:1.7}
.head{max-width:980px;margin:0 auto;padding:3.5rem 1.5rem 2rem;text-align:center;position:relative}
.eyebrow{font-family:var(--serif);color:var(--vermilion);letter-spacing:.4em;font-size:.8rem;margin-bottom:1rem}
.title{font-family:var(--serif);font-weight:900;font-size:2.6rem;color:var(--ink);letter-spacing:.1em}
.sub{color:var(--ink-3);font-family:var(--serif);margin-top:.8rem}
.seal{position:absolute;top:2.5rem;right:1.5rem}
.wall{max-width:980px;margin:0 auto;padding:1rem 1.5rem 3rem;display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:1.5rem}
.card{background:var(--card);border:1px solid var(--hairline);border-top:4px solid var(--vermilion);border-radius:6px;padding:1.3rem 1.3rem 1.1rem;position:relative;box-shadow:0 2px 10px rgba(28,26,23,.05)}
.cno{position:absolute;top:.9rem;right:1rem;font-family:var(--serif);color:var(--ink-4);font-size:.78rem}
.front{font-family:var(--serif);font-weight:700;font-size:1.02rem;color:var(--ink);line-height:1.6;padding-bottom:.7rem;border-bottom:1px solid var(--hairline);margin-bottom:.7rem}
.back{font-size:.9rem;color:var(--ink-2);line-height:1.75}
.foot{text-align:center;color:var(--ink-4);font-family:var(--serif);font-size:.8rem;letter-spacing:.15em;padding-bottom:2.5rem}
"""


def _md_to_html(md):
    """轻量 Markdown→HTML（适配 generate_thought_summary 的结构）。"""
    import re
    out = []
    in_ul = False
    in_ol = False

    def close():
        nonlocal in_ul, in_ol
        if in_ul:
            out.append('</ul>'); in_ul = False
        if in_ol:
            out.append('</ol>'); in_ol = False

    def inline(t):
        t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
        return t.replace('`', '')

    for raw in md.splitlines():
        line = raw.rstrip()
        s = line.strip()
        if not s:
            close(); continue
        if s == '---':
            close(); out.append('<div class="brush"></div>'); continue
        if line.startswith('### '):
            close(); out.append('<h3>' + inline(line[4:].strip()) + '</h3>'); continue
        if line.startswith('## '):
            close(); out.append('<h2>' + inline(line[3:].strip()) + '</h2>'); continue
        if line.startswith('# '):
            close(); out.append('<h1>' + inline(line[2:].strip()) + '</h1>'); continue
        m = re.match(r'^(\d+)\.\s+(.*)$', s)
        if m:
            if not in_ol:
                close(); out.append('<ol>'); in_ol = True
            out.append('<li>' + inline(m.group(2)) + '</li>'); continue
        if s.startswith('- '):
            if not in_ul:
                close(); out.append('<ul>'); in_ul = True
            out.append('<li>' + inline(s[2:]) + '</li>'); continue
        close(); out.append('<p>' + inline(line) + '</p>')
    close()
    return '\n'.join(out)


def generate_print_html(data, summary_md):
    """古典排版 A4 打印文档（封面竖排标题 + 印章 + 正文宋体），浏览器打印即得精美 PDF。"""
    year = data['year']
    tgdz = f"{data['tg']}{data['dz']}"
    idx = data.get('full_result', {}).get('sexagenary_index', '')
    seal_html = ink_theme.seal(tgdz)
    body = _md_to_html(summary_md)
    style = (_PRINT_STYLE
             .replace('__LIGHT__', ink_theme.css_vars('light'))
             .replace('__PAPER_TEX__', ink_theme.paper_texture(opacity=0.05))
             .replace('__WASH__', ink_theme.ink_wash(color='#1c1a17', opacity=0.10)))
    return f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>五运六气思想摘要 · {year} {tgdz}</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700;900&family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>{style}</style></head><body>
  <section class="cover">
    <div class="eyebrow">天人合一 · 气化流行</div>
    <h1 class="vtitle">五运六气</h1>
    <div class="csub">思想摘要</div>
    <div class="meta">{year}年（{tgdz}）· 第{idx}甲子</div>
    <div class="seal">{seal_html}</div>
    <div class="cfoot">宣纸水墨 · 打印版 · 浏览器「打印 → 另存为 PDF」</div>
  </section>
  <main class="content">{body}</main>
</body></html>'''


def _simple_print_html(summary_md, title):
    """无数据时的简化古典打印版（保底）。"""
    body = _md_to_html(summary_md)
    style = (_PRINT_STYLE
             .replace('__LIGHT__', ink_theme.css_vars('light'))
             .replace('__PAPER_TEX__', ink_theme.paper_texture(opacity=0.05))
             .replace('__WASH__', ink_theme.ink_wash(opacity=0.10)))
    return (f'<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>{title}</title>'
            f'<style>{style}</style></head><body><main class="content"><h1>{title}</h1>{body}</main></body></html>')


def _anki_front(text):
    return ('<div style="font-family:' + ink_theme.SERIF + ';font-size:1.05rem;color:#1c1a17;'
            'line-height:1.6;padding:14px 16px;border-left:4px solid #b23a2e;background:#fbf7ec;">'
            + text + '</div>')


def _anki_back(text):
    body = text.replace('\n', '<br>')
    return ('<div style="font-family:' + ink_theme.SANS + ';font-size:.95rem;color:#3a362f;'
            'line-height:1.7;padding:14px 16px;background:#f4efe4;border-top:1px solid #e0d6c2;">'
            + body + '</div>')


def generate_cards_preview(cards, data):
    """可视化卡组预览页（古典卡片墙，供审阅与分享）。"""
    year = data['year']
    tgdz = f"{data['tg']}{data['dz']}"
    seal_html = ink_theme.seal(tgdz)
    card_html = []
    for i, (f, b) in enumerate(cards, 1):
        back = b.replace('\n', '<br>')
        card_html.append(f'''
      <div class="card reveal" data-d="{i}">
        <div class="cno">{i:02d}</div>
        <div class="front">{f}</div>
        <div class="back">{back}</div>
      </div>''')
    style = (_CARDS_STYLE
             .replace('__LIGHT__', ink_theme.css_vars('light'))
             .replace('__PAPER_TEX__', ink_theme.paper_texture(opacity=0.05))
             + ink_theme.MOTION)
    return f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>运气思想卡片 · {year} {tgdz}</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700;900&family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>{style}</style>
<noscript><style>.reveal{{opacity:1!important;transform:none!important}}</style></noscript></head><body>
  <header class="head reveal">
    <div class="eyebrow">运气学思想 · 间隔重复卡组</div>
    <h1 class="title">思想卡片</h1>
    <p class="sub">{year}年（{tgdz}）· 共 {len(cards)} 张 · 配套 Anki TSV 可导入</p>
    <div class="seal">{seal_html}</div>
  </header>
  <main class="wall">{''.join(card_html)}</main>
  <footer class="foot">正面为问 · 背面为思想解答 · 宣纸水墨版<br>⚠ 思想卡片仅供学习参考，临床应用须由执业中医师辨证论治</footer>
{ink_theme.reveal_script()}
</body></html>'''


def generate_cards(data):
    """生成卡片集（Anki TSV[内嵌五行样式] + Markdown + 可视化预览 HTML）。"""
    year = data['year']
    tgdz = f"{data['tg']}{data['dz']}"
    cards = []

    # 1. 格局总思想
    cards.append((
        f"{year}年 {tgdz} 运气格局的核心思想是什么？",
        f"体现了「天人合一」与「盛极而衰 / 虚则受邪」的辩证。{ '太过之年提醒防“太过则伤”' if data['taiguo'] else '不及之年提醒主动培补、守中。' } 司天在泉告诉我们上半年与下半年的气机不同，需顺时而为。"
    ))

    # 2-5. 核心概念卡
    for cname in ['天人合一', '气化', '中和']:
        if cname in CONCEPT_PHILOSOPHY:
            c = CONCEPT_PHILOSOPHY[cname]
            cards.append((
                f"【思想】{cname} 的哲学含义？",
                f"哲学：{c['philosophy']}\n现代：{c['modern']}\n启发：{c.get('example', '')}"
            ))

    # 天符 / 特殊
    if data['tianfu'] or data['suihui']:
        cards.append((
            f"{tgdz} 年为什么是天符/岁会？思想意义？",
            "运与气（或地支）相合，外部条件相对有利。但顺势中仍需防偏盛。提醒我们‘天时地利人和’时更要守中道。"
        ))

    # 反思卡片（非常适合 Anki）
    cards.append((
        "今年运气格局教会我关于‘中和’的什么？",
        "太过与不及都是偏。理想状态是气机中正。平气年最接近中道，人亦当守中。"
    ))
    cards.append((
        "如何把天人合一落实到日常生活？",
        "尊重节气、顺应气候变化、根据体质调养。时间不是中性容器，而是充满节律的生命场。"
    ))

    # Anki TSV（字段内嵌古典样式，可直接导入 Anki）
    TAB = '\t'
    anki_lines = [f"Front{TAB}Back"]
    for front, back in cards:
        safe_front = _anki_front(front).replace(TAB, ' ').replace('\n', ' ')
        safe_back = _anki_back(back).replace(TAB, ' ').replace('\n', ' ')
        anki_lines.append(f"{safe_front}{TAB}{safe_back}")

    # Markdown 版
    md_lines = [f"# {year}年 {tgdz} · 运气学思想卡片集\n", "适合导入 Anki / Obsidian / Notion\n"]
    for i, (front, back) in enumerate(cards, 1):
        md_lines.append(f"## 卡片 {i}")
        md_lines.append(f"**正面**：{front}\n")
        md_lines.append(f"**背面**：\n{back}\n")
        md_lines.append("---\n")

    preview_html = generate_cards_preview(cards, data)
    return '\n'.join(anki_lines), '\n'.join(md_lines), preview_html


def generate_pdf(summary_text, output_path, title="五运六气思想摘要", data=None):
    """产出古典打印 HTML（浏览器转 PDF 的最佳路径）；若装有 fpdf2 则同时生成轻量 PDF。"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 古典打印 HTML（推荐：浏览器 Ctrl+P → 另存为 PDF，中文与排版最完整）
    html_path = output_path.with_suffix('.html')
    if data is not None:
        html_path.write_text(generate_print_html(data, summary_text), encoding='utf-8')
    else:
        html_path.write_text(_simple_print_html(summary_text, title), encoding='utf-8')

    if not FPDF_AVAILABLE:
        return (f"未安装 fpdf2，已生成古典打印 HTML：{html_path}\n"
                f"请用浏览器打开后「打印 → 另存为 PDF」，排版与中文最佳。")

    # fpdf2 轻量实现（纯文本版，中文支持有限）
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", size=14)
    pdf.cell(0, 10, title, ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Helvetica", size=10)

    for line in summary_text.splitlines():
        try:
            pdf.multi_cell(0, 6, line)
        except Exception:
            pdf.multi_cell(0, 6, line.encode('utf-8', errors='ignore').decode('latin-1', errors='ignore'))

    pdf.output(str(output_path))
    return (f"已生成 PDF：{output_path}\n（注意：基础字体中文受限）推荐改用古典打印 HTML 转 PDF：{html_path}")


def run_export(date_input: str, fmt: str = 'summary') -> int:
    """
    统一导出入口（供 calculate_yunqi_api / yunqi_cli 共用，避免逻辑重复）。

    参数:
        date_input: 日期或年份（today / YYYY-MM-DD / 2026）
        fmt: 导出类型 summary | cards | pdf | all
    返回:
        0 成功，2 失败
    """
    try:
        data = get_year_and_data(date_input)
        out_dir = Path('reports/generated/')
        year_str = str(data.get('year', 'unknown'))

        if fmt in ('summary', 'all'):
            summary = generate_thought_summary(data)
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / f'thought_summary_{year_str}.md').write_text(summary, encoding='utf-8')
            print(f'✅ 思想摘要已导出到 {out_dir}')
        if fmt in ('cards', 'all'):
            anki, cards_md, preview = generate_cards(data)
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / f'thought_cards_{year_str}.anki.tsv').write_text(anki, encoding='utf-8')
            (out_dir / f'thought_cards_{year_str}.md').write_text(cards_md, encoding='utf-8')
            (out_dir / f'thought_cards_{year_str}_preview.html').write_text(preview, encoding='utf-8')
            print(f'✅ 卡片集已导出（含可视化预览页）')
        if fmt in ('pdf', 'all'):
            summary = generate_thought_summary(data)
            msg = generate_pdf(summary, f'{out_dir}thought_{year_str}.pdf', data=data)
            print(msg)
        return 0
    except Exception as e:
        print(f'导出失败: {e}', file=sys.stderr)
        print('提示：可直接运行 python scripts/export_thought.py today --format all', file=sys.stderr)
        return 2


def main():
    parser = argparse.ArgumentParser(
        description="导出五运六气思想摘要、卡片集、PDF（专注思想理解）"
    )
    parser.add_argument('date', nargs='?', default='today',
                        help='日期：today / YYYY-MM-DD / 年份（如 2026）')
    parser.add_argument('--format', choices=['summary', 'cards', 'pdf', 'all'], default='summary',
                        help='导出类型')
    parser.add_argument('--output', '-o', default=None,
                        help='输出文件或目录（默认 reports/generated/）')
    parser.add_argument('--audience', default='student',
                        choices=['student', 'practitioner', 'researcher'])

    args = parser.parse_args()

    data = get_year_and_data(args.date)
    year = data['year']
    date_str = data['date_str']

    # 默认输出目录
    base_dir = Path('reports/generated')
    base_dir.mkdir(parents=True, exist_ok=True)

    if args.output:
        out = Path(args.output)
        if out.suffix or not out.is_dir():
            out_dir = out.parent
            stem = out.stem
        else:
            out_dir = out
            stem = f"thought_{year}"
        out_dir.mkdir(parents=True, exist_ok=True)
    else:
        out_dir = base_dir
        stem = f"thought_{year}_{date_str.replace('-', '')}"

    summary_text = generate_thought_summary(data, args.audience)

    results = []

    if args.format in ('summary', 'all'):
        md_path = out_dir / f"{stem}_summary.md"
        md_path.write_text(summary_text, encoding='utf-8')
        results.append(f"✅ 纯文本思想摘要：{md_path}")

    if args.format in ('cards', 'all'):
        anki_tsv, cards_md, preview_html = generate_cards(data)
        tsv_path = out_dir / f"{stem}_cards.anki.tsv"
        md_cards_path = out_dir / f"{stem}_cards.md"
        preview_path = out_dir / f"{stem}_cards_preview.html"
        tsv_path.write_text(anki_tsv, encoding='utf-8')
        md_cards_path.write_text(cards_md, encoding='utf-8')
        preview_path.write_text(preview_html, encoding='utf-8')
        results.append(f"✅ 卡片集 (Anki TSV)：{tsv_path}")
        results.append(f"✅ 卡片集 (Markdown)：{md_cards_path}")
        results.append(f"✅ 卡片集 (可视化预览)：{preview_path}")

    if args.format in ('pdf', 'all'):
        pdf_path = out_dir / f"{stem}.pdf"
        msg = generate_pdf(summary_text, pdf_path, title=f"五运六气思想摘要 - {year}年", data=data)
        results.append(f"✅ PDF 相关：{msg}")
        results.append(f"✅ 古典打印 HTML（浏览器转 PDF，推荐）：{pdf_path.with_suffix('.html')}")

    print("\n".join(results))
    print(f"\n日期：{date_str} | 年份：{year}")
    print("所有导出均围绕「思想理解」设计，可直接用于笔记、Anki、打印存档。")


if __name__ == '__main__':
    main()
