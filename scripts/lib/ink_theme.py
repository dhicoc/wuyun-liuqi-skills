# -*- coding: utf-8 -*-
"""
ink_theme —— 古典雅致·宣纸水墨 设计 token 与共享片段（唯一设计源）

供 generate_html_report.py / export_thought.py 复用，保证报告、PDF、Anki 三处产物
视觉一致。设计原则见项目根 .impeccable.md：墨分五色、五行正色、留白即气、
宋体为骨、屏印双态、装饰有意图。
"""
from __future__ import annotations

import base64

# ── 五行正色（低饱和，语义化）────────────────────────────────────────
# 每个五行给 (light, dark) 双值：浅色用于纸面/打印，深色主题用更亮的可读值。
WUXING = {
    '木': {'light': '#3e6b57', 'dark': '#8ab8a0'},   # 青木
    '火': {'light': '#b23a2e', 'dark': '#e08a7c'},   # 赤火（朱）
    '土': {'light': '#9a7b2d', 'dark': '#d0aa52'},   # 黄土（赭）
    '金': {'light': '#7a6c4f', 'dark': '#c8b88f'},   # 白金（古铜金）
    '水': {'light': '#33475f', 'dark': '#8aa3bf'},   # 黑水（玄青）
}

# 六气 → 五行
LIUQI_WUXING = {
    '厥阴风木': '木', '少阴君火': '火', '太阴湿土': '土',
    '少阳相火': '火', '阳明燥金': '金', '太阳寒水': '水',
}

# ── 墨色阶 / 纸色 / 朱砂 ───────────────────────────────────────────
INK = {  # 墨分五色：用浓淡建立层级
    'light': {
        '900': '#1c1a17',  # 主标题/正文浓
        '700': '#3a362f',  # 正文
        '500': '#6b6558',  # 次要
        '400': '#8a8375',  # 弱化
        '300': '#b3ab9b',  # 极弱
    },
    'dark': {
        '900': '#f0e9da',
        '700': '#d6cdbb',
        '500': '#a89e8a',
        '400': '#857c6a',
        '300': '#5d5647',
    },
}
PAPER = {
    'light': {'bg': '#f4efe4', 'bg2': '#ebe3d2', 'card': '#fbf7ec'},
    'dark': {'bg': '#161310', 'bg2': '#1e1a15', 'card': '#241f18'},
}
VERMILION = {'light': '#b23a2e', 'dark': '#e08a7c'}  # 朱砂
GOLD = {'light': '#8a6d3b', 'dark': '#c9a44e'}        # 落款金

SERIF = "'Noto Serif SC','Songti SC','Source Han Serif SC','SimSun',serif"
SANS = "'Noto Sans SC','PingFang SC','Microsoft YaHei',sans-serif"


def wuxing_of_liuqi(qi_name: str) -> str:
    return LIUQI_WUXING.get(qi_name, '金')


def wx_color(element: str, mode: str = 'light') -> str:
    """五行元素 → 正色。element ∈ {木,火,土,金,水}，mode ∈ {light,dark}。"""
    return WUXING.get(element, WUXING['金']).get(mode, WUXING['金']['light'])


def liuqi_color(qi_name: str, mode: str = 'light') -> str:
    return wx_color(wuxing_of_liuqi(qi_name), mode)


# ── SVG 辅助：印章 / 纸纹 / 笔触 ────────────────────────────────────
def _b64(svg: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode('utf-8')).decode('ascii')


def seal(text: str, size: int = 88, fg: str = '#f7f1e3', bg: str = '#b23a2e') -> str:
    """
    朱砂阴文方印（纯内联 SVG，无图片依赖）。
    1-2 字竖排；3-4 字按传统 2x2 回读（右上→右下→左上→左下）。
    """
    chars = [c for c in text if not c.isspace()][:4]
    if not chars:
        return ''
    cell = size / 2 if len(chars) > 2 else size
    if len(chars) <= 2:
        order = [(0, 0), (0, 1)][:len(chars)]
        w, h = size, size * len(chars) / 1.0 if len(chars) == 2 else size
        # 竖排两字：一个瘦高印
        if len(chars) == 2:
            w, h = size * 0.62, size
            order = [(0, 0), (0, 1)]
        else:
            w = h = size
    else:
        order = [(1, 0), (1, 1), (0, 0), (0, 1)][:len(chars)]  # 右上,右下,左上,左下
        w = h = size
    parts = []
    for ch, (cx, cy) in zip(chars, order):
        x = cx * (w / (1 if len(chars) <= 2 else 2)) + (w / (1 if len(chars) <= 2 else 2)) / 2
        y = cy * (h / (2 if len(chars) == 2 else (2 if len(chars) > 2 else 1))) + (h / (2 if len(chars) == 2 else (2 if len(chars) > 2 else 1))) / 2
        fs = min(w, h) / (2 if len(chars) > 2 else 1) * 0.6
        parts.append(
            f"<text x='{x:.1f}' y='{y:.1f}' fill='{fg}' font-family={SERIF!r} "
            f"font-size='{fs:.0f}' font-weight='700' text-anchor='middle' "
            f"dominant-baseline='central'>{ch}</text>"
        )
    svg = (
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{w:.0f}' height='{h:.0f}' "
        f"viewBox='0 0 {w:.0f} {h:.0f}' style='transform:rotate(-3deg);display:block'>"
        f"<rect x='2' y='2' width='{w-4:.0f}' height='{h-4:.0f}' rx='{min(w,h)*0.08:.0f}' "
        f"fill='{bg}' stroke='{fg}' stroke-opacity='0.35' stroke-width='2'/>"
        f"<rect x='{min(w,h)*0.09:.0f}' y='{min(w,h)*0.09:.0f}' width='{w-min(w,h)*0.18:.0f}' "
        f"height='{h-min(w,h)*0.18:.0f}' fill='none' stroke='{fg}' stroke-opacity='0.5' "
        f"stroke-width='1.2'/>"
        + ''.join(parts) + "</svg>"
    )
    return svg


def paper_texture(opacity: float = 0.04, freq: float = 0.9) -> str:
    """宣纸噪点纹理（SVG feTurbulence，作背景叠加层 data URI）。"""
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'>"
        f"<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='{freq}' numOctaves='2' stitchTiles='stitch'/>"
        "<feColorMatrix type='matrix' values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.6 0'/></filter>"
        f"<rect width='240' height='240' filter='url(#n)' opacity='{opacity}'/></svg>"
    )
    return _b64(svg)


def ink_wash(color: str = '#1c1a17', opacity: float = 0.10, w: int = 480, h: int = 120) -> str:
    """一缕水墨笔触（椭圆渐变 + 噪点），作章节分隔/页眉衬底 data URI。"""
    svg = (
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {w} {h}'>"
        f"<defs><radialGradient id='g' cx='50%' cy='50%' r='60%'>"
        f"<stop offset='0%' stop-color='{color}' stop-opacity='{opacity}'/>"
        f"<stop offset='70%' stop-color='{color}' stop-opacity='{opacity*0.4:.3f}'/>"
        f"<stop offset='100%' stop-color='{color}' stop-opacity='0'/>"
        "</radialGradient>"
        f"<filter id='r'><feTurbulence type='fractalNoise' baseFrequency='0.03 0.15' numOctaves='2'/>"
        f"<feDisplacementMap in='SourceGraphic' scale='18'/></filter></defs>"
        f"<ellipse cx='{w/2}' cy='{h/2}' rx='{w*0.46}' ry='{h*0.34}' fill='url(#g)' filter='url(#r)'/>"
        "</svg>"
    )
    return _b64(svg)


# ── 基础 CSS ─────────────────────────────────────────────────────────
def css_vars(mode: str = 'light') -> str:
    """返回 :root 变量定义（浅色）。mode='dark' 时返回深色覆盖块。"""
    i = INK['dark' if mode == 'dark' else 'light']
    p = PAPER['dark' if mode == 'dark' else 'light']
    v = VERMILION['dark' if mode == 'dark' else 'light']
    g = GOLD['dark' if mode == 'dark' else 'light']
    wx = {k: v[mode if mode in ('light', 'dark') else 'light'] for k, v in WUXING.items()}
    hairline = 'rgba(236,229,216,.16)' if mode == 'dark' else 'rgba(28,26,23,.16)'
    return f"""
  --paper:{p['bg']}; --paper-2:{p['bg2']}; --card:{p['card']};
  --ink:{i['900']}; --ink-2:{i['700']}; --ink-3:{i['500']}; --ink-4:{i['400']}; --ink-5:{i['300']};
  --vermilion:{v}; --gold:{g};
  --wx-mu:{wx['木']}; --wx-huo:{wx['火']}; --wx-tu:{wx['土']}; --wx-jin:{wx['金']}; --wx-shui:{wx['水']};
  --hairline:{hairline};
  --serif:{SERIF}; --sans:{SANS};
"""


# A4 打印（浅色墨版）：浏览器打印 / 另存为 PDF 时生效
PRINT_CSS = """
@page { size: A4; margin: 16mm 15mm; }
@media print {
  html, body { background: #f4efe4 !important; color: #1c1a17 !important; }
  body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .screen-only, .print-btn { display: none !important; }
  a { color: inherit; text-decoration: none; }
  .avoid-break { break-inside: avoid; page-break-inside: avoid; }
  .page-break { break-before: page; page-break-before: always; }
}
"""

# ── 交互动画（Apple 风：克制、有意图、尊重减弱动效；打印/无 JS 时自动失效）──
# 仅注入「屏幕产物」（报告 / 卡片预览）。PDF 打印版保持纯净。
MOTION = """
:root{
  --ease-out:cubic-bezier(0.32,0.72,0,1);
  --ease-spring:cubic-bezier(0.34,1.42,0.64,1);
  --dur-fast:.26s; --dur:.5s; --dur-slow:.85s;
}
@keyframes ink-rise{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:none}}
@keyframes ink-fade{from{opacity:0}to{opacity:1}}
@keyframes seal-stamp{0%{opacity:0;transform:scale(1.55) rotate(-14deg)}55%{opacity:1}100%{opacity:1;transform:scale(1) rotate(-3deg)}}
@keyframes current-pulse{0%,100%{box-shadow:inset 0 3px 0 var(--vermilion)}50%{box-shadow:inset 0 3px 0 var(--vermilion),0 0 0 1px var(--vermilion),0 10px 30px rgba(178,58,46,.20)}}
/* 入场揭示：由 IntersectionObserver 添加 .in 触发 */
.reveal{opacity:0;transform:translateY(22px);
  transition:opacity var(--dur-slow) var(--ease-out),transform var(--dur-slow) var(--ease-out),
             box-shadow var(--dur-fast) var(--ease-out),border-color var(--dur-fast) var(--ease-out);
  will-change:opacity,transform}
.reveal.in{opacity:1;transform:none}
.reveal[data-d="1"]{transition-delay:.07s}.reveal[data-d="2"]{transition-delay:.14s}
.reveal[data-d="3"]{transition-delay:.21s}.reveal[data-d="4"]{transition-delay:.28s}
.reveal[data-d="5"]{transition-delay:.35s}.reveal[data-d="6"]{transition-delay:.42s}
/* 印章落款：印泥钤盖感 */
.hero-seal,.seal{animation:seal-stamp .9s var(--ease-spring) both}
/* 当前步位：载入后轻脉冲一次，引而不发 */
.qstep.is-current{animation:current-pulse 2.8s var(--ease-out) .6s 1 both}
/* 悬停微交互：浮起 + 投影（刻意不用 transform，避免与揭示动画冲突） */
.qstep:hover{box-shadow:0 14px 34px rgba(28,26,23,.14);background:linear-gradient(180deg,var(--paper-2),transparent)}
.read-item:hover{border-top-color:var(--vermilion)}
.rag-card:hover,.card:hover{border-top-color:var(--vermilion);box-shadow:0 14px 34px rgba(28,26,23,.14)}
.kztable tbody tr{transition:background var(--dur-fast) var(--ease-out)}
.kztable tbody tr:hover td{background:var(--paper-2)}
/* 工具栏：毛玻璃 + 按压触感 */
.toolbar{background:transparent;backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px)}
.tbtn{transition:transform var(--dur-fast) var(--ease-out),box-shadow var(--dur-fast) var(--ease-out),filter var(--dur-fast) var(--ease-out)}
.tbtn:hover{transform:translateY(-1px);box-shadow:0 10px 24px rgba(0,0,0,.22)}
.tbtn:active{transform:translateY(1px) scale(.97)}
.tbtn-primary:hover{filter:brightness(1.07)}
/* Hero 衬底淡入（滚动视差由 JS 接管 transform） */
.hero-wash{animation:ink-fade 1.6s var(--ease-out) both}
@media (prefers-reduced-motion:reduce){
  .reveal{opacity:1!important;transform:none!important;transition:none!important}
  .hero-seal,.seal,.qstep.is-current,.hero-wash{animation:none!important}
  *{scroll-behavior:auto!important}
}
@media print{
  .reveal{opacity:1!important;transform:none!important}
  .hero-seal,.seal,.qstep.is-current,.hero-wash{animation:none!important}
  *{animation:none!important;transition:none!important}
}
"""


def reveal_script() -> str:
    """IntersectionObserver 揭示 + Hero 水墨滚动视差。无 JS / 减弱动效时全部可见。"""
    return """
<script>
(function(){
  var els = document.querySelectorAll('.reveal');
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce || !('IntersectionObserver' in window)) {
    els.forEach(function(el){ el.classList.add('in'); });
  } else {
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if (e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    els.forEach(function(el){ io.observe(el); });
  }
  var wash = document.querySelector('.hero-wash');
  if (wash && !reduce){
    var ticking = false;
    window.addEventListener('scroll', function(){
      if (!ticking){ requestAnimationFrame(function(){
        var y = window.scrollY || window.pageYOffset || 0;
        wash.style.transform = 'translate3d(0,' + (y * 0.12) + 'px,0)';
        ticking = false;
      }); ticking = true; }
    }, { passive: true });
  }
})();
</script>
"""
