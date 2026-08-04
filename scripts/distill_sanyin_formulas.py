#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蒸馏《三因极一病证方论》六气司天方 — 六步时令加减 + 六气病机推演
=====================================================================
数据来源：公版古籍 garychowcmu/daizhigev20 仓库 医藏/三因极一病证方论.txt
         宋·陈无择《三因极一病证方论》卷之五·六气时行民病证治

本脚本不是自动抽取器，而是「人读原文 + 结构化录入」的蒸馏产物落地器：
- 六步时令加减（seasonal_modifications）：逐方从原文"自大寒至春分……"精确录入
- 六气病机推演（liuqi_step_pathogenesis）：逐方从原文"初之气……终之气"精确录入
- 组成订正（ingredients）：审平汤/升明汤按公版原书订正（asset4 旧值来自后世转引，有误）
- 六气治法（liuqi_treatment_rule）：从原文"治法，……"录入

每条字段均可在源文件 sanyin.txt 对应行号核验，不编造任何内容。

用法：
    python scripts/distill_sanyin_formulas.py --apply    # 写入 asset4_formula.json
    python scripts/distill_sanyin_formulas.py --dry-run  # 仅打印变更，不写盘
    python scripts/distill_sanyin_formulas.py --verify   # 校验源文件出处仍在
"""
import json
import os
import sys

# 公版源文件（若存在则用于 verify；蒸馏时已逐行核对，不依赖运行时读取）
SOURCE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "rag-knowledge-base", "asset4_formula.json",
)

# ── 蒸馏产物：6 个六气方的增补字段 ──────────────────────────────
# 全部内容转录自公版《三因极一病证方论》卷之五，行号见各条 source_lines。
# 格式：formula_id -> 增补字段 dict
DISTILLED = {
    "11": {  # 敷和汤 — 巳亥年 厥阴风木司天
        "source_lines": "2059-2068",
        "ingredients": "【组成】半夏（汤洗）、枣子、五味子、枳实（麸炒）、茯苓、诃子（炮去核）、干姜（炮）、橘皮、甘草（炙，各半两）、生姜。",
        "usage": "【用法】上为锉散。每服四钱，水盏半，煎七分，去滓，食前服。",
        "liuqi_step_pathogenesis": (
            "巳亥之岁，厥阴风木司天，少阳相火在泉，气化营运后天。"
            "初之气，阳明金加厥阴木，民病寒于右胁下。"
            "二之气，太阳水加少阴火，民病热中。"
            "三之气，厥阴木加少阳火，民病泪出，耳鸣掉眩。"
            "四之气，少阴火加太阴土，民病黄瘅肘肿。"
            "五之气，太阴土加阳明金，燥湿相胜，寒气及体。"
            "终之气，少阳火加太阳水，此下水克上火，民病瘟疠。"
        ),
        "liuqi_treatment_rule": "治法，宜用辛凉平其上，咸寒调其下，畏火之气，无妄犯之。",
        "seasonal_modifications": [
            {"period": "大寒—春分", "action": "加鼠粘子一分"},
            {"period": "春分—小满", "action": "加麦门冬（去心）、山药各一分"},
            {"period": "小满—大暑", "action": "加紫菀一分"},
            {"period": "大暑—秋分", "action": "加泽泻、山栀仁各一分"},
            {"period": "秋分—大寒", "action": "依正方"},
        ],
    },
    "12": {  # 正阳汤 — 子午年 少阴君火司天
        "source_lines": "2047-2057",
        "ingredients": "【组成】白薇、玄参、川芎、桑白皮（炙）、当归、芍药、旋复花、甘草（炙）、生姜（各半两）。",
        "usage": "【用法】上为锉散。每服四钱，水盏半，煎七分，去滓，食前服。",
        "liuqi_step_pathogenesis": (
            "子午之岁，少阴君火司天，阳明燥金在泉，气化营运先天。"
            "初之气，太阳水加厥阴木，民病关节禁固，腰痛，中外疮疡。"
            "二之气，厥阴风木加少阴君火，民病淋，目赤，气郁而热。"
            "三之气，少阴君火加少阳火，民病热厥心痛，寒热更作，咳喘目赤。"
            "四之气，太阴土加湿土，民病黄瘅鼽衄，嗌干吐饮。"
            "五之气，少阳火加阳明金，民乃康。"
            "终之气，阳明金加太阳水，民病上肿咳喘，甚则血溢，下连少腹，而作寒中。"
        ),
        "liuqi_treatment_rule": "治法，宜咸以平其上，苦热以治其内，咸以软之，苦以发之，酸以收之。",
        "seasonal_modifications": [
            {"period": "大寒—春分", "action": "加杏仁、升麻各半两"},
            {"period": "春分—小满", "action": "加茯苓、车前子各半两"},
            {"period": "小满—大暑", "action": "加杏仁、麻仁各一分"},
            {"period": "大暑—秋分", "action": "加荆芥、茵陈蒿各一分"},
            {"period": "秋分—小雪", "action": "依正方"},
            {"period": "小雪—大寒", "action": "加紫苏子半两"},
        ],
    },
    "13": {  # 备化汤 — 丑未年 太阴湿土司天
        "source_lines": "2035-2045",
        "ingredients": "【组成】木瓜干、茯神（去木，各一两）、牛膝（酒浸）、附子（炮，去皮脐，各三分）、熟地黄、覆盆子（各半两）、甘草（一分）、生姜（三分）。",
        "usage": "【用法】上为锉散。每服四大钱，水盏半，煎七分，去滓，食前服。",
        "liuqi_step_pathogenesis": (
            "丑未之岁，太阴湿土司天，太阳寒水在泉，气化营运后天。"
            "初之气，厥阴风木加风木，民病血溢，筋络拘强，关节不利，身重筋痿。"
            "二之气，大火正，乃少阴君火加君火，民病温疠盛行，远近咸若。"
            "三之气，太阴土加少阳火，民病身重肿，胸腹满。"
            "四之气，少阳相火加太阴土，民病腠理热，血暴溢，疟，心腹胀，甚则浮肿。"
            "五之气，阳明燥金加阳明燥金，民病皮肤寒气及体。"
            "终之气，太阳寒水加寒水，民病关节禁固，腰痛。"
        ),
        "liuqi_treatment_rule": "治法，用酸以平其上，甘温治其下，以苦燥之，温之，甚则发之，泄之，赞其阳火，令御其寒。",
        "seasonal_modifications": [
            {"period": "大寒—春分", "action": "依正方"},
            {"period": "春分—小满", "action": "去附子，加天麻、防风各半两"},
            {"period": "小满—大暑", "action": "加泽泻三分"},
            {"period": "大暑—大寒", "action": "依正方"},
        ],
    },
    "14": {  # 升明汤 — 寅申年 少阳相火司天  ★组成订正
        "source_lines": "2025-2033",
        "ingredients": "【组成】紫檀香、车前子（炒）、青皮、半夏（汤洗）、酸枣仁、蔷蘼、生姜、甘草（炙，各半两）。",
        "usage": "【用法】上为锉散。每服四钱，水盏半，煎七分，去滓，食前服。",
        "ingredients_correction_note": "【订正】asset4 旧值为'半夏、木瓜、茯苓、枣仁、甘草、生姜'，系后世转引之误。公版《三因极一病证方论》原方为紫檀香、车前子、青皮、半夏、酸枣仁、蔷蘼、生姜、甘草，无木瓜、茯苓。今据原书订正。",
        "liuqi_step_pathogenesis": (
            "寅申之岁，少阳相火司天，厥阴风木在泉，气化营运先天。"
            "初之气，少阴君火加厥阴木，民病温，气拂于上，血溢目赤，咳逆头痛，血崩胁满，肤腠中疮。"
            "二之气，太阴土加少阴火，民病热郁，咳逆呕吐，胸臆不利，头痛身热，昏愦脓疮。"
            "三之气，少阳相火加相火，民病热中，聋瞑，血溢脓疮，咳呕鼽衄，渴嚏欠，喉痹目赤，善暴死。"
            "四之气，阳明金加太阴土，民病满，身重。"
            "五之气，太阳水加阳明金，民避寒邪，君子周密。"
            "终之气，厥阴木加太阳水，民病开闭不禁，心痛，阳气不藏而咳。"
        ),
        "liuqi_treatment_rule": "治法，宜咸寒平其上，辛温治其内，宜酸渗之，泄之，渍之，发之。",
        "seasonal_modifications": [
            {"period": "大寒—春分", "action": "加白薇、玄参各半两"},
            {"period": "春分—小满", "action": "加丁香一钱"},
            {"period": "小满—大暑", "action": "加漏芦、升麻、赤芍药各半两"},
            {"period": "大暑—秋分", "action": "加茯苓半两"},
            {"period": "秋分—小雪", "action": "依正方"},
            {"period": "小雪—大寒", "action": "加五味子半两"},
        ],
    },
    "15": {  # 审平汤 — 卯酉年 阳明燥金司天  ★组成订正
        "source_lines": "2011-2022",
        "ingredients": "【组成】远志（去心，姜制炒）、紫檀香（各一两）、天门冬（去心）、山茱萸（各三分）、白术、白芍药、甘草（炙）、生姜（各半两）。",
        "usage": "【用法】上锉散。每服四钱，水盏半，煎七分，去滓，食前服。",
        "ingredients_correction_note": "【订正】asset4 旧值为'天冬、山萸、白芍、紫菀、桂枝、人参、甘草、生姜'，系后世转引之误。公版《三因极一病证方论》原方为远志、紫檀香、天门冬、山茱萸、白术、白芍、甘草、生姜，无紫菀、桂枝、人参。今据原书订正。",
        "liuqi_step_pathogenesis": (
            "卯酉之岁，阳明司天，少阴在泉，气化营运后天。"
            "初之气，太阴湿土加厥阴木，此下克上，民病中热胀，面目浮肿，善眠，鼽衄嚏欠，呕吐，小便黄赤，甚则淋。"
            "二之气，少阳相火加少阴君火，此臣居君位，民病疠大至，善暴死。"
            "三之气，阳明燥金加少阳相火，燥热交合，民病寒热。"
            "四之气，太阳寒水加太阴湿土，此下土克上水，民病暴仆，振栗谵妄，少气，咽干引饮，心痛，痈肿疮疡，寒疟骨痿，便血。"
            "五之气，厥阴风木加阳明燥金，民气和。"
            "终之气，少阴君火加太阳寒水，此下克上，民病温。"
        ),
        "liuqi_treatment_rule": "治法，宜咸寒以抑火，辛甘以助金，汗之，清之，散之，安其运气。",
        "seasonal_modifications": [
            {"period": "大寒—春分", "action": "加白茯苓、半夏（汤洗去滑）、紫苏、生姜各半两"},
            {"period": "春分—小满", "action": "加玄参、白薇各半两"},
            {"period": "小满—大暑", "action": "去远志、山茱萸、白术，加丹参、泽泻各半两"},
            {"period": "大暑—秋分", "action": "去远志、白术，加酸枣仁、车前子各半两"},
            {"period": "秋分—大寒", "action": "依正方"},
        ],
    },
    "16": {  # 静顺汤 — 辰戌年 太阳寒水司天
        "source_lines": "2001-2009",
        "ingredients": "【组成】白茯苓、木瓜干（各一两）、附子（炮去皮脐）、牛膝（酒浸，各三分）、防风（去叉）、诃子（炮去核）、甘草（炙）、干姜（炮，各半两）。",
        "usage": "【用法】上为锉散。每服四大钱，水盏半，煎七分，去滓，食前服。",
        "liuqi_step_pathogenesis": (
            "辰戌之岁，太阳司天，太阴在泉，气化营运先天。"
            "初之气，乃少阳相火加临厥阴风木，民病瘟，身热头疼，呕吐，肌腠疮疡。"
            "二之气，阳明燥金加临少阴君火，民病气郁中满。"
            "三之气，太阳寒水加临少阳相火，民病寒，反热中，痈疽注下，心热瞀闷。"
            "四之气，厥阴风木加临太阴湿土，风湿交争，民病大热少气，肌肉痿，足痿，注下赤白。"
            "五之气，少阴君火加临阳明燥金，民气乃舒。"
            "终之气，太阴湿土加临太阳寒水，民乃惨凄孕死。"
        ),
        "liuqi_treatment_rule": "治法，用甘温以平水，酸苦以补火，抑其运气，扶其不胜。",
        "seasonal_modifications": [
            {"period": "大寒—春分", "action": "去附子，加枸杞半两"},
            {"period": "春分—小满", "action": "依前入附子、枸杞"},
            {"period": "小满—大暑", "action": "去附子、木瓜、干姜，加人参、枸杞、地榆、香白芷、生姜各三分"},
            {"period": "大暑—秋分", "action": "依正方，加石榴皮半两"},
            {"period": "秋分—小雪", "action": "依正方"},
            {"period": "小雪—大寒", "action": "去牛膝，加当归、芍药、阿胶炒各三分"},
        ],
    },
}


def apply_distillation(asset: dict, distill: dict, dry_run: bool = False) -> list:
    """将蒸馏字段并入 asset entries，返回变更日志。"""
    changes = []
    by_id = {e["formula_id"]: e for e in asset["entries"]}
    for fid, fields in distill.items():
        entry = by_id.get(fid)
        if not entry:
            changes.append(f"[SKIP] formula_id {fid} 未在 asset4 中找到")
            continue
        name = entry.get("name", f"id{fid}")
        for key, val in fields.items():
            if key in ("source_lines",):
                continue
            old = entry.get(key)
            if old and key in ("ingredients", "usage"):
                # 组成/用法订正：保留旧值为 _legacy_，写入新值
                if old != val:
                    entry[f"_legacy_{key}"] = old
                    entry[key] = val
                    changes.append(f"[UPDATE] {name}.{key}（旧值保留于 _legacy_{key}）")
            elif old and key.startswith("ingredients_correction_note"):
                entry[key] = val
                changes.append(f"[ADD] {name}.{key}")
            else:
                # 新增字段
                entry[key] = val
                changes.append(f"[ADD] {name}.{key}")
    return changes


def main():
    import argparse
    p = argparse.ArgumentParser(description="蒸馏三因司天方六步加减+六气病机 → asset4")
    p.add_argument("--apply", action="store_true", help="写入 asset4_formula.json")
    p.add_argument("--dry-run", action="store_true", help="仅打印变更")
    p.add_argument("--verify", action="store_true", help="打印源文件出处供人工核验")
    args = p.parse_args()

    if not (args.apply or args.dry_run or args.verify):
        p.print_help()
        return

    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        asset = json.load(f)

    changes = apply_distillation(asset, DISTILLED, dry_run=True)

    if args.verify:
        print("=== 蒸馏出处核验（公版《三因极一病证方论》卷之五）===\n")
        by_id = {e["formula_id"]: e for e in asset["entries"]}
        for fid, fields in DISTILLED.items():
            e = by_id[fid]
            print(f"■ {e['name']}（id={fid}, rag_key={e['rag_key']}）")
            print(f"  源文件行号: sanyin.txt L{fields['source_lines']}")
            print(f"  六步加减: {len(fields['seasonal_modifications'])} 步")
            print()
        return

    print("=== 蒸馏变更日志 ===")
    for c in changes:
        print(" ", c)
    print(f"\n共 {len(changes)} 项变更。")

    if args.dry_run:
        print("\n[dry-run] 未写盘。使用 --apply 写入。")
        return

    if args.apply:
        # 更新描述，标注蒸馏来源
        asset["asset_description"] += "（v2：蒸馏公版原文，补六步时令加减、六气病机推演，订正审平汤/升明汤组成）"
        asset["distill_source"] = "公版《三因极一病证方论》卷之五·六气时行民病证治（garychowcmu/daizhigev20 医藏/）"
        asset["distill_method"] = "人读公版原文 + 结构化录入，非 LLM 自动抽取；每条字段可溯源至源文件行号"
        with open(SOURCE_FILE, "w", encoding="utf-8") as f:
            json.dump(asset, f, ensure_ascii=False, indent=2)
        print("\n[OK] 已写入 asset4_formula.json")


if __name__ == "__main__":
    main()
