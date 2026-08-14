#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
neijing_bridge.py · 与 `huangdi-neijing-skill` 的功能级只读桥接

设计原则（见 references/p12-implementation-prd.md）
=================================================
- 纯函数、零外部硬依赖：仅依赖标准库（`re`/`pathlib`/`os`/`sys`/`argparse`）
  以及本仓库本地模块 `_safety_text`（免责声明单一权威源）。
  `yaml` 为**可选**：可用时走 `yaml.safe_load`；不可用时走内置 best-effort 解析，
  以便任何环境都能解析 neijing SKILL.md。
- 只读：本模块不修改外部仓库、不拷贝其原文到 RAG、不引入网络耦合。
- 优雅降级：外部仓库缺失/损坏时，所有入口返回空或 False，**绝不**令运气主流程报错。

数据模型
========
NeijingSkill : 单个内经 skill 的解析结果（slug / 名称 / 出处 / 标签 / 关联 / 六节文本）
SelectedSkill: 被选中并附权重的 skill（含「为何被选中」的可解释理由，回链运气维度）

对外接口
========
- neijing_available() -> bool
- discover_neijing_skills(root_dir) -> dict[slug, NeijingSkill]
- select_skills(yunqi_ctx, skills, top_n=3, include_clinical=False) -> list[SelectedSkill]
- build_methodology_section(selected, include_clinical=False, with_safety=True) -> str
- build_methodology_for_ctx(yunqi_ctx, top_n=3, include_clinical=False, with_safety=True) -> str
- yunqi_context_from_parts(element, taiguo, sitian, zaiquan, constitution=None, **flags) -> dict

CLI
===
python scripts/neijing_bridge.py --selftest [--root <dir>]
"""

import os
import re
import sys
import argparse
from dataclasses import dataclass, field
from pathlib import Path

# 保证 `import _safety_text` 在脚本直接运行时可用（脚本所在目录即 sys.path[0]）。
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

# 六节固定键（顺序即 R/I/A1/A2/E/B）
SECTION_KEYS = ['R', 'I', 'A1', 'A2', 'E', 'B']

# 临床 / 针刺类 slug：默认不进映射，仅在用户显式要求治法/针刺且 include_clinical=True 时
# 以「框架层（I）+ 原文（R）+ 边界（B）」呈现，并强制剥离可执行步骤 E + 三件套免责。
CLINICAL_SLUGS = {
    'qi-regulation',
    'excess-deficiency-decision',
    'root-cause-priority',
    'four-seas-regulation',
    'observe-infer',
}

# 22 个已知 slug（供校验/调试参考，不影响解析）
KNOWN_SUWEN = {
    'yin-yang-balance', 'five-elements-network', 'negative-feedback', 'biao-ben-priority',
    'zheng-xie-assessment', 'context-adaptation', 'prevention-strategy', 'cascade-prediction',
    'seasonal-regimen', 'five-flavors-balance', 'emotion-organ-proxy', 'observation-inference',
}
KNOWN_LINGSHU = {
    'qi-regulation', 'excess-deficiency-decision', 'root-cause-priority', 'observe-infer',
    'four-seas-regulation', 'bottleneck-unblock', 'timing-opportunity',
    'personalize-by-constitution', 'body-mind-integration', 'communicate-persuade',
}

# 默认快照目录：<repo>/scripts/lib/neijing_snapshot（vendored，锁定 commit 17106a2）
_DEFAULT_SNAPSHOT_DIR = os.path.join(_SCRIPT_DIR, 'lib', 'neijing_snapshot')


# ───────────────────────────── 数据模型 ─────────────────────────────
@dataclass
class NeijingSkill:
    slug: str
    name: str
    source_book: str           # 完整出处，如 《黄帝内经·素问》 黄帝与岐伯等
    source_chapter: str        # 篇名，如 阴阳应象大论篇第五、...
    book_label: str            # 短标签：素问 / 灵枢 / ''
    tags: list = field(default_factory=list)
    related: list = field(default_factory=list)   # [(slug, relation), ...]
    sections: dict = field(default_factory=dict)  # {'R':..., 'I':..., ...}


@dataclass
class SelectedSkill:
    skill: NeijingSkill
    weight: float
    reason: str                # 为何被选中（回链运气维度，供报告解释）


# ───────────────────────── yaml（可选） ─────────────────────────
def _load_yaml(text):
    """优先用标准 yaml；不可用则走内置 best-effort 解析。"""
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text)
    except Exception:
        return _simple_yaml_parse(text)


def _strip_inline(s):
    return s.strip().strip('"').strip("'")


def _simple_yaml_parse(text):
    """
    best-effort YAML 子集解析：覆盖 neijing frontmatter 的实际形状
    （标量、`key: [a, b]` 行内列表、`key:` 后跟 `- item` 列表 /
     `- k: v` 映射项 / 缩进文本块）。仅用于无 yaml 环境的降级路径。
    """
    result = {}
    lines = text.splitlines()
    i = 0
    cur_key = None          # 当前列表容器 key
    cur_map_item = None     # 当前映射项 dict
    map_indent = None
    desc_key = None         # 当前文本块（如 description: |）key
    desc_indent = None
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            if desc_key is not None:
                result[desc_key] = (result.get(desc_key, '') + '\n')
            i += 1
            continue
        stripped = line.lstrip(' ')
        indent = len(line) - len(stripped)

        # 文本块（description）续行
        if desc_key is not None and indent > desc_indent and not stripped.startswith('- '):
            prev = result.get(desc_key, '')
            result[desc_key] = (prev.rstrip('\n') + ' ' + stripped) if prev.strip() else stripped
            i += 1
            continue
        # 映射项续行
        if cur_map_item is not None and indent > map_indent and ':' in stripped and not stripped.startswith('- '):
            k, _, v = stripped.partition(':')
            cur_map_item[k.strip()] = _strip_inline(v)
            i += 1
            continue
        # 列表项
        if stripped.startswith('- '):
            item = stripped[2:].strip()
            if cur_key is None:
                i += 1
                continue
            if ':' in item and not item.startswith('"'):
                k, _, v = item.partition(':')
                cur_map_item = {k.strip(): _strip_inline(v)}
                if not isinstance(result.get(cur_key), list):
                    result[cur_key] = []
                result[cur_key].append(cur_map_item)
                map_indent = indent
            else:
                cur_map_item = None
                if not isinstance(result.get(cur_key), list):
                    result[cur_key] = []
                result[cur_key].append(_strip_inline(item))
            i += 1
            continue
        # 普通 key
        if ':' in stripped:
            k, _, v = stripped.partition(':')
            k = k.strip()
            v = _strip_inline(v)
            if v == '':
                # 容器开始（列表或文本块），向前看一行判定
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines) and lines[j].lstrip(' ').startswith('- '):
                    result[k] = []
                    cur_key = k
                    cur_map_item = None
                    desc_key = None
                else:
                    result[k] = ''
                    cur_key = None
                    cur_map_item = None
                    desc_key = k
                    desc_indent = indent
            else:
                if v.startswith('[') and v.endswith(']'):
                    inner = v[1:-1]
                    result[k] = [_strip_inline(x) for x in inner.split(',') if x.strip()]
                else:
                    result[k] = v
                cur_key = None
                cur_map_item = None
                desc_key = None
            i += 1
            continue
        i += 1
    return result


# ───────────────────────── 解析 ─────────────────────────
def _parse_frontmatter(text):
    """返回 (frontmatter_dict_or_None, body_str)。无 frontmatter 时 (None, text)。"""
    lines = text.splitlines()
    if not lines or lines[0].strip() != '---':
        return None, text
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end = i
            break
    if end is None:
        return None, text
    fm_text = '\n'.join(lines[1:end])
    body = '\n'.join(lines[end + 1:])
    try:
        data = _load_yaml(fm_text)
    except Exception:
        data = None
    if not isinstance(data, dict):
        data = None
    return data, body


def _parse_sections(body):
    """从 SKILL.md 正文切出 R/I/A1/A2/E/B 六节文本。"""
    sections = {}
    cur = None
    buf = []
    for line in body.splitlines():
        m = re.match(r'^##\s+([A-Za-z0-9]+)\b', line)
        if m and m.group(1) in SECTION_KEYS:
            if cur is not None:
                sections[cur] = '\n'.join(buf).strip()
            cur = m.group(1)
            buf = []
            continue
        if re.match(r'^##\s', line):
            # 其它二级标题（如「## 相关 skills」「## 审计信息」）结束当前节
            if cur is not None:
                sections[cur] = '\n'.join(buf).strip()
                cur = None
                buf = []
            continue
        if cur is not None:
            buf.append(line)
    if cur is not None:
        sections[cur] = '\n'.join(buf).strip()
    return sections


def _clean_section(text):
    """去掉水平分隔线，返回整洁文本。"""
    if not text:
        return ''
    out = []
    for line in text.splitlines():
        s = line.strip()
        if s in ('---', '***', '___', '* * *'):
            continue
        out.append(line)
    return '\n'.join(out).strip()


def _book_label_from_parts(parts):
    if 'suwen' in parts:
        return '素问'
    if 'lingshu' in parts:
        return '灵枢'
    return ''


def discover_neijing_skills(root_dir):
    """
    只读解析 root_dir 下所有 `**/SKILL.md`。
    返回 dict[slug, NeijingSkill]；单文件解析异常不中断整体（记日志跳过）。
    slug 取 SKILL.md 直接父目录名（与外部仓库 22 slug 一致）。
    """
    root = Path(root_dir)
    skills = {}
    if not root.is_dir():
        return skills
    for path in sorted(root.rglob('SKILL.md')):
        try:
            text = path.read_text(encoding='utf-8')
        except Exception as exc:  # pragma: no cover - 文件损坏降级
            sys.stderr.write(f'[neijing_bridge] 跳过无法读取的 SKILL.md {path}: {exc}\n')
            continue
        try:
            fm, body = _parse_frontmatter(text)
            if fm is None:
                fm = {}
            slug = path.parent.name
            name = (fm.get('name') or slug)
            source_book = str(fm.get('source_book') or '')
            source_chapter = str(fm.get('source_chapter') or '')
            tags = fm.get('tags') or []
            if isinstance(tags, str):
                tags = [tags]
            related = []
            for entry in (fm.get('related_skills') or []):
                if isinstance(entry, dict):
                    rel_slug = entry.get('slug') or entry.get('name')
                    relation = entry.get('relation') or 'composes-with'
                    if rel_slug:
                        related.append((rel_slug, relation))
                elif isinstance(entry, str):
                    related.append((entry, 'composes-with'))
            sections = _parse_sections(body)
            skills[slug] = NeijingSkill(
                slug=slug,
                name=str(name),
                source_book=source_book,
                source_chapter=source_chapter,
                book_label=_book_label_from_parts(Path(path).parts),
                tags=[str(t) for t in tags],
                related=related,
                sections=sections,
            )
        except Exception as exc:  # pragma: no cover - 单文件降级
            sys.stderr.write(f'[neijing_bridge] 解析失败，跳过 {path}: {exc}\n')
            continue
    return skills


# ───────────────────────── 可用性与路径发现 ─────────────────────────
def _has_skill_md(directory):
    d = Path(directory)
    if not d.is_dir():
        return False
    try:
        next(d.rglob('SKILL.md'))
        return True
    except StopIteration:
        return False


def find_neijing_root():
    """
    返回可用根目录，优先级：
      1. 环境变量 HUANGDI_NEIJING_SKILL_DIR（用户自定义/实时克隆）
      2. vendored 快照 scripts/lib/neijing_snapshot
      3. <repo>/.neijing/huangdi-neijing-skill（用户克隆）
    都不存在返回 None。
    """
    candidates = []
    env = os.environ.get('HUANGDI_NEIJING_SKILL_DIR')
    if env:
        candidates.append(env)
    candidates.append(_DEFAULT_SNAPSHOT_DIR)
    repo_root = os.path.dirname(_SCRIPT_DIR)
    candidates.append(os.path.join(repo_root, '.neijing', 'huangdi-neijing-skill'))
    for c in candidates:
        if c and _has_skill_md(c):
            return c
    return None


def neijing_available():
    """外部仓库是否可用（供降级判断）。"""
    return find_neijing_root() is not None


# ───────────────────────── 运气上下文构建（纯函数） ─────────────────────────
def yunqi_context_from_parts(element, taiguo, sitian, zaiquan,
                             constitution=None, emotion_stress=False,
                             timing=False, personalize=False, observe=False,
                             bingzheng=None, clinical_request=False):
    """
    构造 select_skills 所需的 yunqi_ctx。纯函数，不依赖 yunqi_data。
    element : 大运五行单字 木/火/土/金/水
    taiguo  : 大运太过(True)/不及(False)
    sitian  : 司天六气，如 少阴君火
    zaiquan : 在泉六气，如 阳明燥金
    constitution : 体质倾向列表，可含 '阴虚'/'阳虚'/'土' 等（可选）
    emotion_stress/timing/personalize/observe : 触发式布尔开关
    bingzheng : 病证/诉求自由文本（可选，用于后续扩展）
    """
    return {
        'dayun': {'element': element, 'taiguo': bool(taiguo)},
        'sitian': sitian or '',
        'zaiquan': zaiquan or '',
        'constitution': list(constitution or []),
        'emotion_stress': bool(emotion_stress),
        'timing': bool(timing),
        'personalize': bool(personalize),
        'observe': bool(observe),
        'bingzheng': bingzheng or '',
        'clinical_request': bool(clinical_request),
    }


# ───────────────────────── 映射表（数据驱动，便于校准） ─────────────────────────
def _contains_any(s, subs):
    return any(sub and sub in (s or '') for sub in subs)


def _is_fire(c):
    if c.get('dayun', {}).get('element') == '火':
        return True
    return _contains_any(c.get('sitian'), ['君火', '相火']) or _contains_any(c.get('zaiquan'), ['君火', '相火'])


def _is_metal(c):
    if c.get('dayun', {}).get('element') == '金':
        return True
    return _contains_any(c.get('zaiquan'), ['燥金', '阳明'])


def _is_wood(c):
    if c.get('dayun', {}).get('element') == '木':
        return True
    return _contains_any(c.get('sitian'), ['风木', '厥阴'])


def _is_water(c):
    if c.get('dayun', {}).get('element') == '水':
        return True
    return (_contains_any(c.get('sitian'), ['少阴', '太阳', '寒水'])
            or _contains_any(c.get('zaiquan'), ['少阴', '太阳', '寒水']))


def _has_const(c, token):
    return any(token in x for x in (c.get('constitution') or []))


# 每条规则：命中则给 slug 加权，reason 回链运气维度。
YUNQI_NEIJING_MAP = [
    # 稳定骨干
    dict(slug='yin-yang-balance', weight=5, reason='阴阳为纲：盛虚方向总判（任一年运皆可参照）',
         match=lambda c: True),
    dict(slug='five-elements-network', weight=7, reason='五行生克：推导五运六气系统连锁',
         match=lambda c: True),
    # 火
    dict(slug='yin-yang-balance', weight=4, reason='火运/君相火：阴虚则补阳、阳亢则制阳',
         match=_is_fire),
    dict(slug='five-flavors-balance', weight=4, reason='火运：苦味入心，五味调和防过',
         match=lambda c: c.get('dayun', {}).get('element') == '火'),
    # 金
    dict(slug='emotion-organ-proxy', weight=6, reason='金/阳明燥金在泉：悲忧属肺',
         match=_is_metal),
    # 木
    dict(slug='cascade-prediction', weight=6, reason='木/厥阴风木司天：木克土传变预判',
         match=_is_wood),
    # 土
    dict(slug='five-flavors-balance', weight=6, reason='土运/太宫：甘入脾',
         match=lambda c: c.get('dayun', {}).get('element') == '土'),
    # 水
    dict(slug='seasonal-regimen', weight=6, reason='水/少阴/太阳：冬藏养阴',
         match=_is_water),
    # 体质
    dict(slug='yin-yang-balance', weight=4, reason='体质·阴虚：阴虚阳亢',
         match=lambda c: _has_const(c, '阴虚')),
    dict(slug='seasonal-regimen', weight=6, reason='体质·阳虚：养藏',
         match=lambda c: _has_const(c, '阳虚')),
    dict(slug='prevention-strategy', weight=6, reason='体质·阳虚/治未病：欲病早治',
         match=lambda c: _has_const(c, '阳虚')),
    dict(slug='five-flavors-balance', weight=3, reason='体质·土运防五脏：五味所伤防护',
         match=lambda c: _has_const(c, '土')),
    # 情志/压力
    dict(slug='emotion-organ-proxy', weight=5, reason='情志/压力：情志脏腑相关',
         match=lambda c: c.get('emotion_stress')),
    dict(slug='body-mind-integration', weight=5, reason='情志/压力：形神合一',
         match=lambda c: c.get('emotion_stress')),
    # 时序/时机
    dict(slug='timing-opportunity', weight=5, reason='时序/时机：时机选择',
         match=lambda c: c.get('timing')),
    dict(slug='prevention-strategy', weight=4, reason='时机/治未病：欲病早治',
         match=lambda c: c.get('timing')),
    # 个体化
    dict(slug='personalize-by-constitution', weight=5, reason='个体化：因人施术',
         match=lambda c: c.get('personalize')),
    dict(slug='context-adaptation', weight=5, reason='个体化：因地制宜',
         match=lambda c: c.get('personalize')),
    # 观察推断
    dict(slug='observation-inference', weight=5, reason='观察推断：以外测内',
         match=lambda c: c.get('observe')),
]

# related_skills 展开的权重（命中已选 skill 的关联项时叠加）
_RELATION_WEIGHT = {'depends-on': 4, 'composes-with': 3, 'contrasts-with': 1}

# 临床/针刺类规则：仅在 include_clinical=True（用户显式问治法/针刺）时启用。
# 全部指向 CLINICAL_SLUGS，命中后由 build_methodology_section 剥离 E + 强制三件套。
CLINICAL_NEIJING_MAP = [
    dict(slug='qi-regulation', weight=6, reason='显式治法/调气诉求：调气治本框架',
         match=lambda c: c.get('clinical_request')),
    dict(slug='excess-deficiency-decision', weight=5, reason='显式虚实/补泻诉求',
         match=lambda c: c.get('clinical_request')),
    dict(slug='root-cause-priority', weight=5, reason='显式求本/治根诉求',
         match=lambda c: c.get('clinical_request')),
    dict(slug='observe-infer', weight=4, reason='显式诊断/观察诉求',
         match=lambda c: c.get('clinical_request')),
    dict(slug='four-seas-regulation', weight=4, reason='显式气机调和诉求',
         match=lambda c: c.get('clinical_request')),
]


# ───────────────────────── 选择 ─────────────────────────
def select_skills(yunqi_ctx, skills, top_n=3, include_clinical=False):
    """
    由运气上下文选择 top-N 内经 skill。
    框架路径：1) 逐条规则加权；2) related_skills 多级展开叠加；3) 按权重降序取 top-N。
    临床路径（include_clinical=True）：在框架 top-N 之后，追加临床/针刺类 top-N
    （显式诉求驱动），去重后返回，保证「用户问治法」时临床框架必现。
    返回 list[SelectedSkill]。
    """
    weights = {}
    reasons = {}

    # 框架规则（仅框架 slug；临床 slug 不在框架映射中）
    for rule in YUNQI_NEIJING_MAP:
        slug = rule['slug']
        if slug in CLINICAL_SLUGS:
            continue
        if slug not in skills:
            continue
        try:
            ok = bool(rule['match'](yunqi_ctx))
        except Exception:
            ok = False
        if ok:
            weights[slug] = weights.get(slug, 0) + rule['weight']
            reasons[slug] = reasons[slug] + '；' + rule['reason'] if slug in reasons else rule['reason']

    # related_skills 多级展开（框架 → 框架；include_clinical 时框架 → 临床 也计入框架池）
    for slug in list(weights.keys()):
        skill = skills.get(slug)
        if not skill:
            continue
        for (rel_slug, relation) in skill.related:
            if rel_slug not in skills:
                continue
            if rel_slug in CLINICAL_SLUGS and not include_clinical:
                continue
            add = _RELATION_WEIGHT.get(relation, 2)
            weights[rel_slug] = weights.get(rel_slug, 0) + add
            reasons[rel_slug] = reasons.get(rel_slug, '') + f'；关联[{relation}]{slug}'

    ranked = sorted(weights.items(), key=lambda kv: (-kv[1], kv[0]))
    selected = [
        SelectedSkill(skill=skills[slug], weight=w, reason=reasons.get(slug, '').lstrip('；'))
        for slug, w in ranked[:top_n]
    ]

    # 临床/针刺类（仅显式 include_clinical）：追加并保证出现
    if include_clinical:
        c_weights = {}
        c_reasons = {}
        for rule in CLINICAL_NEIJING_MAP:
            slug = rule['slug']
            if slug not in skills:
                continue
            try:
                ok = bool(rule['match'](yunqi_ctx))
            except Exception:
                ok = False
            if ok:
                c_weights[slug] = c_weights.get(slug, 0) + rule['weight']
                c_reasons[slug] = c_reasons.get(slug, '') + '；' + rule['reason'] if slug in c_reasons else rule['reason']
        c_ranked = sorted(c_weights.items(), key=lambda kv: (-kv[1], kv[0]))
        existing = {s.skill.slug for s in selected}
        for slug, w in c_ranked[:top_n]:
            if slug in existing:
                continue
            selected.append(SelectedSkill(
                skill=skills[slug], weight=w,
                reason=c_reasons.get(slug, '').lstrip('；'),
            ))

    return selected


# ───────────────────────── 章节拼装 + 安全 ─────────────────────────
def build_methodology_section(selected, include_clinical=False, with_safety=True):
    """
    拼装 Markdown「## 内经方法论」章节。
    每 skill 取 I(框架)+E(步骤)+B(边界)，并附章节出处引用。
    临床类（include_clinical 时）仅保留 I + 原文 R + B，剥离 E，并强制三件套免责。
    返回字符串；空 selected 时返回 ''。
    """
    if not selected:
        return ''

    lines = ['## 内经方法论\n']
    lines.append('> 以下为《黄帝内经》方法论框架参考，非医学诊断/治疗建议，'
                 '具体诊疗须由执业中医师辨证论治。\n')

    any_clinical = False
    for i, sel in enumerate(selected, 1):
        sk = sel.skill
        is_clin = sk.slug in CLINICAL_SLUGS
        if is_clin:
            any_clinical = True
        book = sk.book_label or '内经'
        lines.append(f'### {i}. {sk.name}（{book}·{sk.source_chapter}）\n')
        lines.append(f'- 来源：`{sk.slug}`')
        lines.append(f'- 入选理由：{sel.reason}\n')

        I = _clean_section(sk.sections.get('I', ''))
        if I:
            lines.append('**方法论骨架（I）**\n' + I + '\n')

        if is_clin and include_clinical:
            R = _clean_section(sk.sections.get('R', ''))
            if R:
                lines.append('**原文依据（R，仅框架层）**\n' + R + '\n')
            lines.append('> ⚠️ 该条目为临床/针刺类框架，已剥离可执行操作步骤（E）；'
                         '具体治法、穴位、方药须由执业中医师操作，本工具不提供。\n')
        else:
            E = _clean_section(sk.sections.get('E', ''))
            if E:
                lines.append('**可执行步骤（E）**\n' + E + '\n')

        B = _clean_section(sk.sections.get('B', ''))
        if B:
            lines.append('**边界（B）**\n' + B + '\n')

        lines.append(f'> 出处：《{sk.source_book}》{sk.source_chapter}\n')

    if any_clinical and with_safety:
        try:
            from _safety_text import (  # 单一权威源，禁止硬拷贝
                CLINICAL_SAFETY_NOTICE, EMERGENCY_NOTICE, DISCLAIMER,
            )
            lines.append(CLINICAL_SAFETY_NOTICE)
            lines.append(EMERGENCY_NOTICE)
            lines.append(DISCLAIMER)
        except Exception:
            pass

    return '\n'.join(lines)


def build_methodology_for_ctx(yunqi_ctx, top_n=3, include_clinical=False, with_safety=True):
    """
    高层便捷入口：发现 → 选择 → 拼装。外部仓库不可用时返回 ''（绝不报错）。
    供 yunqi_report / personal_yunqi_profile 调用。
    """
    try:
        root = find_neijing_root()
        if not root:
            return ''
        skills = discover_neijing_skills(root)
        if not skills:
            return ''
        selected = select_skills(yunqi_ctx, skills, top_n=top_n, include_clinical=include_clinical)
        return build_methodology_section(selected, include_clinical=include_clinical, with_safety=with_safety)
    except Exception as exc:  # pragma: no cover - 降级保护
        sys.stderr.write(f'[neijing_bridge] 构建内经方法论章节失败（已降级跳过）：{exc}\n')
        return ''


# ───────────────────────── 自检 ─────────────────────────
def _selftest(root=None):
    root = root or find_neijing_root()
    if not root:
        print('SELFTEST: SKIPPED (neijing 仓库不可用；降级路径正常)')
        return 0
    skills = discover_neijing_skills(root)
    assert skills, 'discover_neijing_skills 应至少解析到一个 skill'
    # 校验已知 slug 的六节齐全
    for slug in ('yin-yang-balance', 'five-elements-network', 'qi-regulation'):
        assert slug in skills, f'缺少已知 skill: {slug}'
        sk = skills[slug]
        for key in ('R', 'I', 'E', 'B'):
            assert sk.sections.get(key), f'{slug} 缺少六节中的 {key}'
        assert sk.related, f'{slug} 应解析到 related_skills'
    # 选择：火运年应含 yin-yang-balance
    ctx_fire = yunqi_context_from_parts('火', True, '少阴君火', '阳明燥金')
    sel = select_skills(ctx_fire, skills, top_n=3)
    assert any(s.skill.slug == 'yin-yang-balance' for s in sel), '火运年应入选 yin-yang-balance'
    # 默认不应含临床 slug
    assert not any(s.skill.slug in CLINICAL_SLUGS for s in sel), '默认映射不应含临床 slug'
    # 临床显式模式：必须真正选中临床 slug、剥离 E、含三件套
    ctx_clin = yunqi_context_from_parts('木', False, '厥阴风木', '少阳相火',
                                        clinical_request=True)
    sel_clin = select_skills(ctx_clin, skills, top_n=3, include_clinical=True)
    clin_present = [s for s in sel_clin if s.skill.slug in CLINICAL_SLUGS]
    assert clin_present, 'include_clinical=True 且 clinical_request 时应选中临床 slug'

    # 临床-only 选择：验证 E（可执行步骤）被剥离、三件套就位
    clin_only = [SelectedSkill(skill=skills[s], weight=1.0, reason='临床自检')
                 for s in ('qi-regulation', 'excess-deficiency-decision', 'root-cause-priority')
                 if s in skills]
    section_clin = build_methodology_section(clin_only, include_clinical=True, with_safety=True)
    assert '已剥离可执行操作步骤' in section_clin, '临床类应标注已剥离 E'
    # E 段可执行标记（"当 skill 被激活后"）不应出现在临床-only 章节
    assert '当 skill 被激活后' not in section_clin, '临床类应剥离 E 可执行步骤'
    assert '执业中医师' in section_clin, '临床类应含三件套免责（拒诊拒方）'
    print(f'SELFTEST: OK ({len(skills)} skills parsed; top-N fire year = '
          f'{[s.skill.slug for s in sel]}; clinical = '
          f'{[s.skill.slug for s in clin_present]})')
    return 0


def main():
    parser = argparse.ArgumentParser(description='neijing_bridge 只读桥接自检')
    parser.add_argument('--selftest', action='store_true', help='运行只读解析/选择自检')
    parser.add_argument('--root', help='指定 neijing 根目录（覆盖自动发现）')
    args = parser.parse_args()

    if args.selftest:
        sys.exit(_selftest(root=args.root))

    # 默认行为：打印可用性 + 发现统计
    root = find_neijing_root()
    if not root:
        print('neijing 仓库不可用（HUANGDI_NEIJING_SKILL_DIR 未设置且无 vendored 快照）。')
        print('降级：运气主流程不受影响，仅缺少「内经方法论」章节。')
        sys.exit(0)
    skills = discover_neijing_skills(root)
    print(f'neijing 根目录: {root}')
    print(f'已解析 skill 数: {len(skills)}')
    print('slug 列表: ' + ', '.join(sorted(skills.keys())))


if __name__ == '__main__':
    main()
