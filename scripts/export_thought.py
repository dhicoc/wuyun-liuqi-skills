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


def generate_cards(data):
    """生成卡片集（Anki TSV + Markdown 版）"""
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

    # Anki TSV
    TAB = '\t'
    anki_lines = [f"Front{TAB}Back"]
    for front, back in cards:
        safe_front = front.replace(TAB, ' ').replace('\n', ' ')
        safe_back = back.replace(TAB, ' ').replace('\n', '<br>')
        anki_lines.append(f"{safe_front}{TAB}{safe_back}")

    # Markdown 版
    md_lines = [f"# {year}年 {tgdz} · 运气学思想卡片集\n", "适合导入 Anki / Obsidian / Notion\n"]
    for i, (front, back) in enumerate(cards, 1):
        md_lines.append(f"## 卡片 {i}")
        md_lines.append(f"**正面**：{front}\n")
        md_lines.append(f"**背面**：\n{back}\n")
        md_lines.append("---\n")

    return '\n'.join(anki_lines), '\n'.join(md_lines)


def generate_pdf(summary_text, output_path, title="五运六气思想摘要"):
    """尝试生成 PDF（优先 fpdf2）。失败则给出 HTML 打印建议。"""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not FPDF_AVAILABLE:
        # 回退：生成一个专门用于打印的 HTML
        html_path = output_path.with_suffix('.html')
        html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>{title}</title>
<style>
body {{ font-family: "Noto Serif SC", "PingFang SC", "Microsoft YaHei", serif; line-height: 1.7; max-width: 720px; margin: 40px auto; padding: 20px; }}
h1,h2,h3 {{ color: #1f2937; }}
pre, code {{ background: #f8fafc; padding: 2px 6px; border-radius: 4px; }}
</style></head><body>
<h1>{title}</h1>
<pre style="white-space: pre-wrap; font-family: inherit;">{summary_text}</pre>
<p><em>提示：请用浏览器打开本 HTML，按 Ctrl+P → 选择“另存为 PDF”（推荐，保留排版与中文）。</em></p>
</body></html>"""
        html_path.write_text(html, encoding='utf-8')
        return f"PDF 依赖未安装（fpdf2）。已生成打印友好 HTML：{html_path}\n请打开后使用浏览器「打印 → 另存为 PDF」获得最佳效果。"

    # fpdf2 简单实现（纯文本版，中文支持有限）
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", size=14)
    pdf.cell(0, 10, title, ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Helvetica", size=10)

    # 简单分行处理（中文会乱码时用户可改用 HTML）
    for line in summary_text.splitlines():
        try:
            pdf.multi_cell(0, 6, line)
        except Exception:
            pdf.multi_cell(0, 6, line.encode('utf-8', errors='ignore').decode('latin-1', errors='ignore'))

    pdf.output(str(output_path))
    return f"已生成 PDF：{output_path}\n注意：基础字体对中文支持有限，推荐优先使用生成的 HTML 打印为 PDF（排版更好）。"


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
        anki_tsv, cards_md = generate_cards(data)
        tsv_path = out_dir / f"{stem}_cards.anki.tsv"
        md_cards_path = out_dir / f"{stem}_cards.md"
        tsv_path.write_text(anki_tsv, encoding='utf-8')
        md_cards_path.write_text(cards_md, encoding='utf-8')
        results.append(f"✅ 卡片集 (Anki)：{tsv_path}")
        results.append(f"✅ 卡片集 (Markdown)：{md_cards_path}")

    if args.format in ('pdf', 'all'):
        pdf_path = out_dir / f"{stem}.pdf"
        msg = generate_pdf(summary_text, pdf_path, title=f"五运六气思想摘要 - {year}年")
        # 同时生成高质量 HTML 版本（推荐用于 PDF）
        html_path = out_dir / f"{stem}_print.html"
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><title>五运六气思想摘要 - {year}</title>
<style>
body {{ max-width: 680px; margin: 40px auto; padding: 20px; font-family: "Noto Serif SC", "PingFang SC", "Microsoft YaHei", serif; line-height: 1.75; font-size: 15px; }}
h1, h2, h3 {{ color: #111827; }}
hr {{ border: none; border-top: 1px solid #ddd; }}
</style></head><body>
<pre style="white-space: pre-wrap; font-family: inherit;">{summary_text}</pre>
<p style="color:#666;font-size:12px;margin-top:2em;">提示：使用浏览器「打印 (Ctrl+P)」→「另存为 PDF」，可获得带样式的精美 PDF。</p>
</body></html>"""
        html_path.write_text(html_content, encoding='utf-8')
        results.append(f"✅ PDF 相关：{msg}")
        results.append(f"✅ 高质量打印 HTML（推荐转 PDF）：{html_path}")

    print("\n".join(results))
    print(f"\n日期：{date_str} | 年份：{year}")
    print("所有导出均围绕「思想理解」设计，可直接用于笔记、Anki、打印存档。")


if __name__ == '__main__':
    main()
