#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五运六气综合报告生成器
用法: python yunqi_report.py <年份> [--audience student|practitioner|researcher] [--json] [--advanced-json <高级对齐JSON文件>]
"""
import sys
import os
import json

from _common import setup_environment
setup_environment()  # 处理 UTF-8 + lib 路径

from yunqi_data import (
    get_ganzhi, get_dayun, is_taiguo, get_sitian, get_zaiquan,
    get_keqi_six_steps, get_zhuqi_six_steps, get_zhuyun_five_steps,
    get_keyun_five_steps, check_tianfu, check_suihui, check_pingqi,
    kezhujialin_relation, ZHUQI_JIEQI, LIUQI_WUXING, LIUQI_YINYANG,
    TIANGAN_YINYANG, DIZHI_WUXING, DIZHI_SHENGXIAO,
    get_sexagenary_index, get_suiyun_code,
)

# 自进化集成
try:
    from self_evolve import log_usage
    AUTO_SE = True
except Exception:
    AUTO_SE = False

DISCLAIMER = (
    "\n> ⚠️ 免责声明：以上分析基于中医运气学说理论推算，仅供参考。"
    "运气学说非现代医学诊断标准，具体诊疗须由执业中医师辨证论治。"
    "请勿据此自行用药或针灸。\n"
)

CLINICAL_SAFETY_NOTICE = (
    "\n> ⚠️ 临床安全提示：方药仅作传统运气学参考方向，须由执业中医师辨证加减；"
    "请勿自行购药、配伍或服用。针灸/艾灸/穴位仅作传统理论参考，"
    "须由执业针灸师操作；请勿自行针刺或重灸。\n"
)

EMERGENCY_NOTICE = (
    "\n> ⚠️ 急症提醒：若出现胸痛、呼吸困难、意识障碍、大出血、剧烈腹痛、高热不退等严重症状，"
    "请立即联系急救或前往正规医疗机构就诊。\n"
)

RAG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'rag-knowledge-base')

# P1: 简单缓存，避免报告生成时重复读取 JSON
_ASSET_CACHE = {}

def load_asset(filename):
    if filename in _ASSET_CACHE:
        return _ASSET_CACHE[filename]
    try:
        with open(os.path.join(RAG_DIR, filename), 'r', encoding='utf-8') as f:
            data = json.load(f)
        _ASSET_CACHE[filename] = data
        return data
    except Exception:
        return {}


def find_entry(asset, predicate):
    for entry in asset.get('entries', []):
        if predicate(entry):
            return entry
    return None


def find_suiyun_evidence(year):
    code = get_suiyun_code(year)
    entry = find_entry(load_asset('asset1_suiyun.json'), lambda e: e.get('code') == code)
    if not entry:
        return None
    return {
        'title': entry.get('name'),
        'source': 'rag-knowledge-base/asset1_suiyun.json',
        'key': code,
        'quote': entry.get('classics_quote'),
        'principle': entry.get('treatment_principle'),
    }


def find_sitian_zaiquan_evidence(sitian, zaiquan):
    asset = load_asset('asset2_sitian_zaiquan.json')
    entry = find_entry(asset, lambda e: e.get('sitian') == sitian and e.get('zaiquan') == zaiquan)
    if not entry:
        return None
    return {
        'source': 'rag-knowledge-base/asset2_sitian_zaiquan.json',
        'sitian_key': entry.get('sitian_key'),
        'zaiquan_key': entry.get('zaiquan_key'),
        'sitian_quote': entry.get('sitian_classics_quote'),
        'zaiquan_quote': entry.get('zaiquan_classics_quote'),
        'treatment_rule_quote': entry.get('treatment_rule_classics_quote'),
    }


def find_kezhujialin_evidence(step, zhu_qi, ke_qi):
    asset = load_asset('asset3_kezhujialin.json')
    entry = find_entry(asset, lambda e: e.get('zhu_qi') == zhu_qi and e.get('ke_qi') == ke_qi)
    if not entry:
        return None
    return {
        'source': 'rag-knowledge-base/asset3_kezhujialin.json',
        'key': entry.get('key'),
        'step': step,
        'pathogenesis': entry.get('pathogenesis'),
        'clinical_focus': entry.get('clinical_focus'),
    }


def find_commentary_evidence(suiyun_code=None):
    asset = load_asset('asset5_commentary.json')
    matches = []
    for entry in asset.get('entries', []):
        keys = entry.get('related_yunqi_keys') or []
        if suiyun_code and suiyun_code in keys:
            matches.append(entry)
    if not matches:
        # 通用注家观点兜底，保证报告能连接到注家资产
        matches = asset.get('entries', [])[:2]
    return [
        {
            'author': e.get('author'),
            'dynasty': e.get('dynasty'),
            'work': e.get('work'),
            'title': e.get('core_theory_title'),
            'source': 'rag-knowledge-base/asset5_commentary.json',
            'rag_key': e.get('rag_key'),
        }
        for e in matches[:3]
    ]


def build_evidence_section(year, sitian, zaiquan, jialin_results):
    suiyun = find_suiyun_evidence(year)
    sitian_zaiquan = find_sitian_zaiquan_evidence(sitian, zaiquan)
    suiyun_code = get_suiyun_code(year)
    commentaries = find_commentary_evidence(suiyun_code)
    lines = ['## 经典与注家依据\n']
    if suiyun:
        lines.append(f"- **岁运依据**（{suiyun['source']}，key: `{suiyun['key']}`）：{suiyun['quote']}")
        lines.append(f"  - 治则摘录：{suiyun['principle']}")
    if sitian_zaiquan:
        lines.append(f"- **司天依据**（{sitian_zaiquan['source']}，key: `{sitian_zaiquan['sitian_key']}`）：{sitian_zaiquan['sitian_quote']}")
        lines.append(f"- **在泉依据**（{sitian_zaiquan['source']}，key: `{sitian_zaiquan['zaiquan_key']}`）：{sitian_zaiquan['zaiquan_quote']}")
        lines.append(f"  - 治法原文：{sitian_zaiquan['treatment_rule_quote']}")
    # 选取不相得步位或第三步司天步位作为客主加临证据
    target = None
    for item in jialin_results:
        if not item[4].startswith('相得'):
            target = item
            break
    if not target and jialin_results:
        target = jialin_results[2] if len(jialin_results) >= 3 else jialin_results[0]
    if target:
        step, zq, kq, rel, sn = target
        evidence = find_kezhujialin_evidence(step, zq, kq)
        if evidence:
            lines.append(f"- **客主加临依据**（{evidence['source']}，key: `{evidence['key']}`）：{evidence['pathogenesis']}")
            lines.append(f"  - 临床关注：{evidence['clinical_focus']}")
    if commentaries:
        lines.append('- **历代注家关联**：')
        for item in commentaries:
            lines.append(f"  - {item.get('dynasty', '')}·{item.get('author', '')}《{item.get('work', '')}》：{item.get('title', '')}（{item.get('source')}，key: `{item.get('rag_key')}`）")
    lines.append('')
    return '\n'.join(lines)


def build_rag_bundle_section(year, ref_date=None):
    """
    将 rag_search.fetch_by_date 接入报告：按代表日 rag_keys 精确拉取知识库摘要。
    ref_date: 默认 year-07-08（大寒后、年中，属该运气年）。
    """
    try:
        from rag_search import fetch_by_date
    except Exception:
        return ''

    date_str = ref_date or f"{int(year)}-07-08"
    try:
        bundle = fetch_by_date(date_str, full=False)
    except Exception:
        return ''

    rag_keys = bundle.get('rag_keys') or {}
    hits_by_role = bundle.get('hits_by_role') or {}
    lines = [
        '## 知识库精确命中（按日 rag_keys）\n',
        f"> 代表日: `{bundle.get('date', date_str)}` · 运气年 {bundle.get('yunqi_year')}（{bundle.get('year_gz', '')}）  \n",
        f"> 直取键: `{json.dumps(rag_keys, ensure_ascii=False)}`\n",
    ]
    role_labels = {
        'suiyun': '岁运',
        'sitian': '司天',
        'zaiquan': '在泉',
        'current_step': '当前步位（代表日）',
    }
    for role in ('suiyun', 'sitian', 'zaiquan', 'current_step'):
        key = rag_keys.get(role, '')
        label = role_labels.get(role, role)
        hits = hits_by_role.get(role) or []
        lines.append(f"### {label} · `{key}`\n")
        if not hits:
            lines.append("- （未命中知识库）\n")
            continue
        # 每 role 最多 2 条，避免报告过长
        for h in hits[:2]:
            preview = (h.get('preview') or '').strip()
            if len(preview) > 160:
                preview = preview[:160] + '…'
            lines.append(
                f"- **{h.get('title', h.get('id'))}**"
                f"（{h.get('asset')}/{h.get('id')}）：{preview}"
            )
        lines.append('')

    missing = bundle.get('missing') or []
    if missing:
        lines.append(f"- ⚠️ 未命中: {', '.join(missing)}")
    else:
        lines.append("- ✅ 全部 rag_keys 均有知识库命中")
    lines.append('')
    lines.append(
        f"_完整 JSON：`python scripts/rag_search.py --date {date_str} --json` "
        f"或 `from wuyun_liuqi import fetch_by_date`_\n"
    )
    return '\n'.join(lines)


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

    regional = advanced.get('regional_alignment')
    if regional:
        sections.append(f"- **地域修正**: {regional.get('region_name', '')}；五运权重 {regional.get('wuyun_weight', '')}，六气权重 {regional.get('liuqi_weight', '')}")
        sections.append(f"- **地域因子**: {'、'.join(regional.get('affected_factors') or []) or '未提取'}")
        sections.append(f"- **地域解释**: {regional.get('explanation', '')}")

    for note in synthesis.get('notes') or []:
        sections.append(f"  - {note}")
    sections.append("")
    return '\n'.join(sections)


def build_thought_layer_section(year, tg, dz, dayun, taiguo, sitian, zaiquan, tianfu, suihui, pingqi):
    """
    P0: 新增“思想层解读”章节
    帮助用户理解运气格局背后的宇宙观与生命观，而非仅病机。
    """
    sections = ["## 思想层解读\n"]

    # 基础宇宙观
    sections.append("**运气学核心思想**：")
    sections.append("五运六气体现了《黄帝内经》“天人合一”的根本宇宙观——天地阴阳之气按固定节律运行，人体作为小宇宙必须与之相应。")
    sections.append("")

    # 具体格局解读
    sections.append(f"**{year}年（{tg}{dz}）格局的思想启发**：")

    if taiguo:
        sections.append("- 岁运太过之年，体现“盛极而衰”的辩证思想：阳干主事，气机偏盛，提醒人需防“太过则伤”。")
    else:
        sections.append("- 岁运不及之年，体现“虚则受邪”的思想：阴干主事，需主动培补，防“不及则侮”。")

    if tianfu:
        sections.append("- **天符**：运与气同，气机顺遂。思想上提示“顺时而为”，天地与人气相合之年，宜顺势而为而非强逆。")
    if suihui:
        sections.append("- **岁会**：运与地支五行相合。体现“天时地利人和”思想，提示该年外部条件相对有利，宜把握时机。")
    if pingqi:
        sections.append("- **平气**：太过被抑或不及得助。核心思想是“中和”——天地自行调节偏颇，人亦当守中道。")

    sections.append("")
    sections.append("**与现代生活的思想连接**：")
    sections.append("运气学提醒我们：时间不是中性的容器，而是充满节律的生命场。尊重节气、顺应气候、调和体质，正是对“天人合一”最朴素的实践。")

    sections.append("")
    sections.append("**核心概念哲学简释**：")
    sections.append("- **天人合一**：天地之气与人体之气同源同律，人体健康是天地节律在小宇宙的体现。")
    sections.append("- **气化**：万物皆由气化生、气化动、气化变。运气即天地之气的运行节律。")
    sections.append("- **中和**：太过与不及皆为偏，平气之年最接近“中道”，是天地自我调节的智慧。")

    sections.append("")
    return '\n'.join(sections)


# 核心概念哲学银行 (P0-2) —— 内置回退，模块目录缺失时使用
CONCEPT_PHILOSOPHY = {
    "天人合一": {
        "philosophy": "天地与人是一个整体的生命系统，运气是天地之气运行的节律，人必须与之相应才能健康。",
        "modern": "类似现代的生物钟、季节性情感障碍、环境医学，强调人与自然环境的同步。",
        "example": "当司天之气为风木时，肝气易动，养生宜顺肝而为。"
    },
    "气化": {
        "philosophy": "一切现象皆为气之化生、运动、变化。运气学研究天地之气的周期性化生规律。",
        "modern": "对应能量转换、生态系统循环、气候变化对生物的影响。",
        "example": "五运对应五行之气的化生，六气为阴阳之气的运动形式。"
    },
    "中和": {
        "philosophy": "太过与不及都是偏离，理想状态是气机中正平和。平气之年是天地自我调节的结果。",
        "modern": "类似稳态（homeostasis）、平衡饮食、中庸之道在健康中的应用。",
        "example": "平气年气候相对稳定，人体也易保持中和，不易生大病。"
    },
    "天符": {
        "philosophy": "运与气相合，天地之气与岁运同调，气机顺畅但也可能偏盛。",
        "modern": "顺势而为、环境与内在一致时的优势与风险。",
        "example": "天符年宜把握机遇，但防太过之气伤正。"
    }
}


# ── 教学模块目录加载 (teaching-modules/) ─────────────────────────────
# 从 teaching-modules/<concept>.md 读取 YAML frontmatter + Markdown 正文，
# 解析为统一 dict。frontmatter 必须含 philosophy/modern/example（兼容旧消费者）。
# 解析仅用 stdlib，避免引入 pyyaml 依赖。

_TEACHING_MODULES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "teaching-modules",
)


def _parse_yaml_frontmatter(text):
    """极简 YAML frontmatter 解析（仅支持 key: value 与 key: value 形式）。

    教学模块的 frontmatter 字段均为单行字符串，无需支持嵌套/列表。
    复杂字段（commentaries / common_misconceptions / depth_levels）放在正文 Markdown 里。
    """
    import re
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm_block = text[3:end].strip()
    body = text[end + 4:].lstrip("\n")
    meta = {}
    for line in fm_block.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, body


def load_concept(concept_name):
    """从 teaching-modules/ 加载一个概念模块，返回统一 dict。

    返回 dict 含旧字段（philosophy/modern/example）以兼容旧消费者，
    另含 concept/category/golden_quote 与正文 body。

    模块不存在或解析失败时返回 None（由调用方决定回退）。
    """
    # 支持概念名含·/空格的归一化：文件名用概念原名
    candidates = [
        os.path.join(_TEACHING_MODULES_DIR, f"{concept_name}.md"),
    ]
    # 容错：概念名里的·在文件名里保留，但也尝试替换
    safe = concept_name.replace("·", "").replace(" ", "")
    if safe != concept_name:
        candidates.append(os.path.join(_TEACHING_MODULES_DIR, f"{safe}.md"))

    for path in candidates:
        if os.path.isfile(path):
            for encoding in ("utf-8", "utf-8-sig"):
                try:
                    with open(path, "r", encoding=encoding) as f:
                        text = f.read()
                    break
                except Exception:
                    continue
            else:
                continue
            meta, body = _parse_yaml_frontmatter(text)
            if not meta:
                continue
            # 兼容旧消费者：确保三字段存在
            meta.setdefault("philosophy", "")
            meta.setdefault("modern", "")
            meta.setdefault("example", "")
            meta["body"] = body
            meta["_module_path"] = path
            return meta
    return None


def explain_concept(concept_name):
    """返回概念的讲解文本。

    优先从 teaching-modules/ 加载完整模块（五段式 + 思想层），
    模块缺失时回退到内置 CONCEPT_PHILOSOPHY（三字段简版），
    仍无则提示参考经典原文。
    """
    module = load_concept(concept_name)
    if module:
        lines = [f"**{concept_name}**"]
        if module.get("category"):
            lines.append(f"_分类：{module['category']}_")
        lines.append("")
        lines.append(f"- **哲学思想**：{module.get('philosophy', '')}")
        lines.append(f"- **现代比喻**：{module.get('modern', '')}")
        lines.append(f"- **示例**：{module.get('example', '')}")
        if module.get("golden_quote"):
            lines.append(f"- **金句**：{module['golden_quote']}")
        # 附正文（含原文/注家对照/解读/误区/深度分层）
        body = module.get("body", "").strip()
        if body:
            lines.append("")
            lines.append(body)
        return "\n".join(lines)
    if concept_name in CONCEPT_PHILOSOPHY:
        c = CONCEPT_PHILOSOPHY[concept_name]
        return f"**{concept_name}**：\n- 哲学思想：{c['philosophy']}\n- 现代比喻：{c['modern']}\n- 示例：{c['example']}"
    return f"**{concept_name}**：暂无详细哲学解读，请参考经典原文。"



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


def generate_report(year, audience='student', advanced=None, with_rag_bundle=True, rag_ref_date=None):
    """生成综合报告。

    with_rag_bundle: 是否附加按日 rag_keys 精确命中章节（默认开启）。
    rag_ref_date: 代表日 YYYY-MM-DD；默认 year-07-08。
    """
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

    # P0: 思想层解读（帮助理解思想而非仅结果）
    thought_section = build_thought_layer_section(year, tg, dz, dayun, taiguo, sitian, zaiquan, tianfu, suihui, pingqi)
    sections.append(thought_section)

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

    # 经典与注家依据
    sections.append(build_evidence_section(year, sitian, zaiquan, jialin_results))

    # 知识库精确命中（fetch_by_date / rag_keys）
    if with_rag_bundle:
        rag_section = build_rag_bundle_section(year, ref_date=rag_ref_date)
        if rag_section:
            sections.append(rag_section)

    # 高级对齐章节（可选）
    advanced_section = build_advanced_alignment_section(advanced)
    if advanced_section:
        sections.append(advanced_section)

    # 临床版强化安全与急症提醒
    if audience == 'practitioner':
        sections.append(CLINICAL_SAFETY_NOTICE)
        sections.append(EMERGENCY_NOTICE)

    # 免责声明
    sections.append(DISCLAIMER)

    # 自进化：自动记录报告生成（P0-1）
    if AUTO_SE:
        try:
            log_usage(str(year), [], source="yunqi_report", concepts=["思想层解读"])
        except Exception:
            pass

    return '\n'.join(sections)


def main():
    if len(sys.argv) < 2:
        print(
            "用法: python yunqi_report.py <年份> "
            "[--audience student|practitioner|researcher] [--json] "
            "[--advanced-json <文件>] [--no-rag-bundle] [--rag-date YYYY-MM-DD]"
        )
        sys.exit(1)

    year = int(sys.argv[1])
    audience = 'student'
    advanced = None
    with_rag_bundle = True
    rag_ref_date = None
    if '--audience' in sys.argv:
        idx = sys.argv.index('--audience')
        if idx + 1 < len(sys.argv):
            audience = sys.argv[idx + 1]
    if '--advanced-json' in sys.argv:
        idx = sys.argv.index('--advanced-json')
        if idx + 1 < len(sys.argv):
            advanced = load_advanced_alignment(sys.argv[idx + 1])
    if '--no-rag-bundle' in sys.argv:
        with_rag_bundle = False
    if '--rag-date' in sys.argv:
        idx = sys.argv.index('--rag-date')
        if idx + 1 < len(sys.argv):
            rag_ref_date = sys.argv[idx + 1]

    if audience not in ('student', 'practitioner', 'researcher'):
        print(f"audience 必须是 student/practitioner/researcher，当前: {audience}")
        sys.exit(1)

    report = generate_report(
        year,
        audience,
        advanced=advanced,
        with_rag_bundle=with_rag_bundle,
        rag_ref_date=rag_ref_date,
    )

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
