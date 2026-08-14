#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运气病机自动推理链

输入年份 -> 自动输出：
  1. 岁运病机（太过/不及/平气）
  2. 司天在泉病机 + 民病
  3. 客主加临病机（六步）
  4. 推荐治则
  5. 推荐方剂（三因司天方）

用法：
  python scripts/infer_pathogenesis.py 2026
  python scripts/infer_pathogenesis.py 2026 --json
  python scripts/infer_pathogenesis.py today
"""

import json
import sys
import os
from pathlib import Path

# 确保 scripts 目录在 path 中
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from calculate_yunqi_api import (
    calculate_yunqi_api,
    get_suiyun_code,
    get_sitian,
    get_zaiquan,
    get_keqi_six_steps,
    get_zhuqi_six_steps,
    check_pingqi,
)

KB_DIR = SCRIPT_DIR.parent / "rag-knowledge-base"


def _load_kb(filename: str) -> list:
    """加载知识库 JSON 文件的 entries。"""
    p = KB_DIR / filename
    if not p.exists():
        return []
    d = json.loads(p.read_text(encoding="utf-8"))
    return d.get("entries", [])


def _find_by_key(entries: list, key: str, field: str = "code") -> dict:
    """在 entries 中按 field 匹配 key。"""
    for e in entries:
        for f in (field, "key", "rag_key", "sitian_key", "zaiquan_key"):
            v = e.get(f, "")
            if v == key:
                return e
    return {}


def _find_sitian_entry(sitian_name: str, zaiquan_name: str) -> dict:
    """按司天/在泉名称匹配。"""
    sitian_kb = _load_kb("asset2_sitian_zaiquan.json")
    for e in sitian_kb:
        if e.get("sitian") == sitian_name and e.get("zaiquan") == zaiquan_name:
            return e
    # 退化匹配：只匹司天
    for e in sitian_kb:
        if e.get("sitian") == sitian_name:
            return e
    return {}


def _find_kezhujialin_entry(zhu_qi: str, ke_qi: str) -> dict:
    """按主气/客气匹配客主加临。"""
    kj_kb = _load_kb("asset3_kezhujialin.json")
    for e in kj_kb:
        if e.get("zhu_qi") == zhu_qi and e.get("ke_qi") == ke_qi:
            return e
    return {}


def _find_formula(rag_key: str) -> list:
    """按 rag_key 查找三因司天方。"""
    formula_kb = _load_kb("asset4_formula.json")
    return [e for e in formula_kb if e.get("rag_key") == rag_key]


def _find_disease_susceptibility(suiyun_code: str, sitian_key: str, zaiquan_key: str = "", extra_keys: list = None) -> list:
    """按岁运/司天/在泉/运气相合检索疾病易感性提示（asset33）。

    extra_keys：可选，P11 激活——把个人「先天运气」key（出生/胎孕岁运·司天·在泉）
    并入召回，使 asset33 的 earth/fire 等体质·易感性维度在个人场景被主动召回。
    """
    ds_kb = _load_kb("asset33_disease_susceptibility.json")
    # 组合 key：司天_在泉
    sitian_zaiquan_key = f"{sitian_key}_{zaiquan_key}" if zaiquan_key else ""
    match_keys = {suiyun_code, sitian_key, sitian_zaiquan_key}
    if extra_keys:
        match_keys.update(k for k in extra_keys if k)
    results = []
    for e in ds_kb:
        rag_key = e.get("rag_key", "")
        if rag_key in match_keys:
            results.append({
                "dimension": e.get("dimension", ""),
                "susceptible_diseases": e.get("susceptible_diseases", []),
                "susceptibility_direction": e.get("susceptibility_direction", ""),
                "pathogenesis": e.get("pathogenesis", ""),
                "regulation_direction": e.get("regulation_direction", ""),
                "evidence": e.get("evidence", ""),
                "source": e.get("source", ""),
            })
    return results


def infer_pathogenesis(year: int, congenital_keys: list = None) -> dict:
    """运气病机自动推理主函数。

    输入年份，输出完整的病机推理链字典。
    """
    # 1. 运气推算
    yq = calculate_yunqi_api(year)
    suiyun = yq.get("sui_yun", {})
    sitian_name = yq.get("si_tian", "")
    zaiquan_name = yq.get("zai_quan", "")
    tonghua = yq.get("tong_hua", {})

    # 2. 岁运病机
    suiyun_code = suiyun.get("code", "")
    suiyun_kb = _load_kb("asset1_suiyun.json")
    suiyun_entry = _find_by_key(suiyun_kb, suiyun_code, "code")

    # 3. 司天在泉病机
    sitian_entry = _find_sitian_entry(sitian_name, zaiquan_name)

    # 4. 客主加临病机（六步）
    kj_steps = yq.get("ke_zhu_jia_lin", [])
    six_steps = []
    for s in kj_steps:
        zq_name = s.get("zhu_qi", "")
        kq_name = s.get("ke_qi", "")
        kj_entry = _find_kezhujialin_entry(zq_name, kq_name)
        six_steps.append({
            "step": s.get("step_number", ""),
            "step_name": s.get("step_name", ""),
            "zhu_qi": zq_name,
            "ke_qi": kq_name,
            "relation": s.get("relation", "") or kj_entry.get("relation", ""),
            "shun_ni": s.get("shun_ni", "") or kj_entry.get("shun_ni", ""),
            "pathogenesis": kj_entry.get("pathogenesis", ""),
            "clinical_focus": kj_entry.get("clinical_focus", ""),
        })

    # 5. 推荐方剂
    formulas = _find_formula(suiyun_code)
    # 也查司天在泉方
    sitian_key = sitian_entry.get("sitian_key", "")
    if sitian_key:
        formulas_sitian = _find_formula(sitian_key)
        formulas.extend(formulas_sitian)

    # 6. 组装结果
    year_gz = yq.get("year_gz", "")
    result = {
        "year": year,
        "ganzhi": {
            "year": year_gz,
            "tiangan": yq.get("year_gan", ""),
            "dizhi": yq.get("year_zhi", ""),
        },
        "dayun": {
            "name": suiyun.get("name", ""),
            "wuxing": suiyun.get("element", ""),
            "taiguo": suiyun.get("status", ""),
            "code": suiyun_code,
        },
        "pingqi": {
            "is_pingqi": tonghua.get("pingqi", False),
            "condition": "平气" if tonghua.get("pingqi") else "非平气",
            "rule": "",
        },
        "sitian": {
            "name": sitian_name,
            "key": sitian_entry.get("sitian_key", ""),
        },
        "zaiquan": {
            "name": zaiquan_name,
            "key": sitian_entry.get("zaiquan_key", ""),
        },
        "suiyun_pathogenesis": {
            "code": suiyun_entry.get("code", ""),
            "name": suiyun_entry.get("name", ""),
            "pathogenesis": suiyun_entry.get("pathogenesis", ""),
            "classics_quote": suiyun_entry.get("classics_quote", ""),
            "organs_affected": suiyun_entry.get("organs_affected", []),
            "symptoms": suiyun_entry.get("symptoms", []),
            "treatment_principle": suiyun_entry.get("treatment_principle", ""),
            "dietary_advice": suiyun_entry.get("dietary_advice", ""),
        },
        "sitian_pathogenesis": {
            "pathogenesis": sitian_entry.get("sitian_pathogenesis", ""),
            "classics_quote": sitian_entry.get("sitian_classics_quote", ""),
            "symptoms": sitian_entry.get("sitian_symptoms", []),
            "affected_organ": sitian_entry.get("sitian_affected_organ", ""),
            "treatment_rule": sitian_entry.get("treatment_rule", ""),
        },
        "zaiquan_pathogenesis": {
            "pathogenesis": sitian_entry.get("zaiquan_pathogenesis", ""),
            "classics_quote": sitian_entry.get("zaiquan_classics_quote", ""),
            "symptoms": sitian_entry.get("zaiquan_symptoms", []),
            "affected_organ": sitian_entry.get("zaiquan_affected_organ", ""),
        },
        "six_steps": six_steps,
        "formulas": [
            {
                "name": f.get("name", ""),
                "source": f.get("source", ""),
                "applicable_pattern": f.get("applicable_pattern", ""),
                "indications": f.get("indications", ""),
                "ingredients": f.get("ingredients", ""),
                "clinical_notes": f.get("clinical_notes", ""),
            }
            for f in formulas
        ],
        "disease_susceptibility": _find_disease_susceptibility(suiyun_code, sitian_entry.get("sitian_key", ""), sitian_entry.get("zaiquan_key", ""), extra_keys=congenital_keys),
    }

    return result


def format_result(r: dict) -> str:
    """格式化为人类可读文本。"""
    lines = []
    y = r["year"]
    gz = r["ganzhi"]
    dy = r["dayun"]
    pq = r["pingqi"]
    st = r["sitian"]
    zq = r["zaiquan"]

    lines.append(f"╔══════════════════════════════════════════════════════════╗")
    lines.append(f"║  {y}年（{gz['year']}）运气病机推理报告")
    lines.append(f"╚══════════════════════════════════════════════════════════╝")
    lines.append("")

    # 岁运
    lines.append(f"【岁运】{dy['name']}（{dy['wuxing']}）")
    if pq["is_pingqi"]:
        lines.append(f"  ⚖ 平气之年（{pq.get('condition','')}）规则：{pq.get('rule','')}")
    else:
        lines.append(f"  {'太过' if '太过' in dy.get('taiguo','') else '不及' if '不及' in dy.get('taiguo','') else dy.get('taiguo','')}")

    sp = r["suiyun_pathogenesis"]
    if sp["pathogenesis"]:
        lines.append(f"  病机：{sp['pathogenesis']}")
    if sp["classics_quote"]:
        lines.append(f"  经典：{sp['classics_quote']}")
    if sp["organs_affected"]:
        lines.append(f"  受邪脏腑：{', '.join(sp['organs_affected'])}")
    if sp["symptoms"]:
        lines.append(f"  常见症状：{', '.join(sp['symptoms'])}")
    if sp["treatment_principle"]:
        lines.append(f"  治则：{sp['treatment_principle']}")
    if sp["dietary_advice"]:
        lines.append(f"  食养：{sp['dietary_advice']}")
    lines.append("")

    # 司天
    lines.append(f"【司天】{st['name']}")
    stp = r["sitian_pathogenesis"]
    if stp["pathogenesis"]:
        lines.append(f"  病机：{stp['pathogenesis']}")
    if stp["symptoms"]:
        lines.append(f"  民病：{', '.join(stp['symptoms'])}")
    if stp["affected_organ"]:
        lines.append(f"  病本：{stp['affected_organ']}")
    if stp["treatment_rule"]:
        lines.append(f"  治则：{stp['treatment_rule']}")
    lines.append("")

    # 在泉
    lines.append(f"【在泉】{zq['name']}")
    zqp = r["zaiquan_pathogenesis"]
    if zqp["pathogenesis"]:
        lines.append(f"  病机：{zqp['pathogenesis']}")
    if zqp["symptoms"]:
        lines.append(f"  民病：{', '.join(zqp['symptoms'])}")
    if zqp["affected_organ"]:
        lines.append(f"  病本：{zqp['affected_organ']}")
    lines.append("")

    # 客主加临
    lines.append("【客主加临六步】")
    for s in r["six_steps"]:
        rel = f" {s['relation']}（{s['shun_ni']}）" if s["relation"] else ""
        lines.append(f"  {s['step']}之气：主{s['zhu_qi']} 客{s['ke_qi']}{rel}")
        if s["pathogenesis"]:
            lines.append(f"    病机：{s['pathogenesis']}")
        if s["clinical_focus"]:
            lines.append(f"    临证：{s['clinical_focus']}")
    lines.append("")

    # 方剂
    if r["formulas"]:
        lines.append("【推荐方剂（三因司天方）】")
        for f in r["formulas"]:
            lines.append(f"  ▶ {f['name']}（《{f['source']}》）")
            if f["applicable_pattern"]:
                lines.append(f"    适应：{f['applicable_pattern']}")
            if f["indications"]:
                lines.append(f"    主治：{f['indications']}")
            if f["ingredients"]:
                lines.append(f"    组成：{f['ingredients']}")
            if f["clinical_notes"]:
                lines.append(f"    加减：{f['clinical_notes']}")
    else:
        lines.append("【推荐方剂】无直接匹配的三因司天方")

    lines.append("")
    lines.append("⚠ 以上为运气病机推理，临床应用须结合个体辨证，附免责声明。")
    return "\n".join(lines)


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(
        description="运气病机自动推理链：输入年份 -> 输出完整病机推理",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("year", help="年份（如 2026）或 today")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args(argv if argv is not None else None)

    if args.year.lower() == "today":
        from datetime import date
        year = date.today().year
    else:
        year = int(args.year)

    r = infer_pathogenesis(year)

    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(format_result(r))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
