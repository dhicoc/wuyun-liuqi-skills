#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医案知识库浏览器 - OPT-09

复用 generate_html_report.py 的 _STYLE + ink_theme 宣纸水墨设计体系，
生成静态 HTML 浏览器：按医家/朝代/病证分类浏览 1994 条医案 + 全文搜索。

用法:
  python scripts/generate_case_browser.py
  python scripts/generate_case_browser.py --output reports/case-browser.html
"""

import json
import sys
from pathlib import Path
from html import escape
from collections import Counter

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
from _common import setup_environment, add_scripts_dir_to_path
setup_environment(add_lib=True, add_scripts=True)

from _safety_text import CONTEXT_DISCLAIMERS

from generate_html_report import _STYLE, escape_html
import ink_theme  # scripts/lib（setup_environment 已注入路径）

KB = Path(__file__).resolve().parent.parent / "rag-knowledge-base"


def load_all_cases():
    libraries = []
    all_entries = []
    for f in sorted(KB.glob("asset*_*.json")):
        if "schema" in f.name:
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        if d.get("asset_type") != "case_library":
            continue
        asset_id = d.get("asset_id", f.stem)
        name = d.get("asset_name", "")
        cnt = d.get("entry_count", 0)
        libraries.append({"asset_id": asset_id, "name": name, "count": cnt})
        for e in d.get("entries", []):
            cid = e.get("case_id") or e.get("entry_id", "")
            all_entries.append({
                "asset_id": asset_id, "asset_name": name, "case_id": cid,
                "category": e.get("category", ""), "physician": e.get("physician", ""),
                "source": e.get("source", ""), "chief_complaint": e.get("chief_complaint", ""),
                "syndrome": e.get("syndrome", ""), "treatment": e.get("treatment", ""),
                "formula": e.get("formula", ""), "outcome": e.get("outcome", ""),
                "source_quote": e.get("source_quote", ""), "note": e.get("note", ""),
                "name": e.get("name", ""),
            })
    return libraries, all_entries


def generate_browser_html(libraries, all_entries):
    physician_stats = Counter(e["physician"] for e in all_entries if e["physician"])
    category_stats = Counter(e["category"] for e in all_entries if e["category"])
    total = len(all_entries)
    seal_html = ink_theme.seal("医案", size=72)

    def tags(data_attr, stats, limit=40):
        return "".join(
            f'<button class="filter-tag" data-{data_attr}="{escape_html(k)}">{escape_html(k)} <span class="tag-count">{v}</span></button>'
            for k, v in stats.most_common(limit)
        )

    lib_tags = "".join(
        f'<button class="filter-tag" data-asset="{escape_html(lib["asset_id"])}">{escape_html(lib["name"][:20])} <span class="tag-count">{lib["count"]}</span></button>'
        for lib in libraries
    )
    physician_tags = tags("physician", physician_stats, 30)
    category_tags = tags("category", category_stats, 40)
    entries_json = json.dumps(all_entries, ensure_ascii=False)

    style = (_STYLE
             .replace('__DARK__', ink_theme.css_vars('dark'))
             .replace('__LIGHT__', ink_theme.css_vars('light'))
             .replace('__PAPER_TEX__', ink_theme.paper_texture(opacity=0.05))
             .replace('__WASH__', ink_theme.ink_wash(color='#8a8375', opacity=0.13))
             + ink_theme.MOTION)

    # 读取补充样式和 JS
    extra_dir = SCRIPT_DIR / "lib"
    extra_css = (extra_dir / "case_browser_extra.css").read_text(encoding="utf-8") if (extra_dir / "case_browser_extra.css").exists() else ""
    browser_js = (extra_dir / "case_browser.js").read_text(encoding="utf-8") if (extra_dir / "case_browser.js").exists() else ""

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>医案知识库浏览器 · {total}条</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700;900&family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">
<style>{style}
{extra_css}</style>
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
        <div class="hero-eyebrow">公版典籍 · 真实医案</div>
        <h1 class="vtitle">医案知识库</h1>
        <p class="hero-sub">{total} 条真实医案 · {len(libraries)} 部典籍 · {len(physician_stats)} 位医家</p>
        <ul class="hero-meta">
          <li><span>总条目</span><b>{total}</b></li>
          <li><span>典籍库</span><b>{len(libraries)}</b></li>
          <li><span>医家</span><b>{len(physician_stats)}</b></li>
          <li><span>病证</span><b>{len(category_stats)}</b></li>
        </ul>
      </div>
      <div class="hero-seal" aria-hidden="true">{seal_html}</div>
    </div>
  </header>

  <main>
    <section class="section">
      <h2 class="sec-title reveal"><span class="sec-no">壹</span>检索</h2>
      <div class="search-bar reveal">
        <input type="text" id="search-input" placeholder="输入关键词（症状/方药/医家/病证）检索 {total} 条医案…">
      </div>
      <div class="filter-section reveal"><h3>按典籍库</h3><div class="filter-tags">{lib_tags}</div></div>
      <div class="filter-section reveal"><h3>按医家</h3><div class="filter-tags">{physician_tags}</div></div>
      <div class="filter-section reveal"><h3>按病证</h3><div class="filter-tags">{category_tags}</div></div>
    </section>

    <section class="section">
      <h2 class="sec-title reveal"><span class="sec-no">贰</span>医案列表</h2>
      <div class="result-info" id="result-info">显示全部 {total} 条</div>
      <div class="case-list" id="case-list"></div>
      <div class="no-result" id="no-result" style="display:none">未找到匹配医案</div>
    </section>

    <section class="section">
      <div class="disclaimer reveal"><strong>免责声明</strong>：{CONTEXT_DISCLAIMERS['medical_case']}</div>
    </section>
  </main>

  <footer class="foot">医案知识库浏览器 · 宣纸水墨版 · {total} 条医案 · 由 wuyun-liuqi-skills 生成</footer>

  <div class="case-detail-overlay" id="overlay" onclick="if(event.target===this)closeDetail()">
    <div class="case-detail" id="case-detail"></div>
  </div>

<script>
const ALL_CASES = {entries_json};
{browser_js}
</script>
{ink_theme.reveal_script()}
</body>
</html>'''


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description="生成医案知识库浏览器 HTML")
    parser.add_argument("--output", "-o", default="reports/case-browser.html")
    args = parser.parse_args(argv if argv is not None else None)

    libraries, all_entries = load_all_cases()
    html = generate_browser_html(libraries, all_entries)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"✅ 已生成: {out} ({len(html)} bytes, {len(all_entries)} 条医案)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
