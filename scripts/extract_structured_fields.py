#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OPT-04 医案结构化字段提取

从 formula 字段中自动提取：
  - herbs: 药味列表（如 ["柴胡","黄芩","石膏"]）
  - formulas_referenced: 引用方剂名列表（如 ["小柴胡汤","白虎汤"]）

提取后写回各 asset JSON，并更新 index.json。

用法:
  python scripts/extract_structured_fields.py          # 提取并写回
  python scripts/extract_structured_fields.py --check   # 仅统计不写回
"""

import json
import sys
import re
from pathlib import Path
from collections import Counter

SCRIPT_DIR = Path(__file__).parent
KB = SCRIPT_DIR.parent / "rag-knowledge-base"

# 常用方剂名词表（按长度降序匹配，避免"小柴胡汤"被"柴胡"截断）
KNOWN_FORMULAS = [
    "附子理中汤", "补中益气汤", "十全大补汤", "六味地黄丸", "桂附地黄丸",
    "小柴胡汤", "大柴胡汤", "白虎加人参汤", "白虎汤", "竹叶石膏汤",
    "大承气汤", "小承气汤", "调胃承气汤", "桃核承气汤", "当归龙荟丸",
    "六君子汤", "四君子汤", "参苓白术散", "归脾汤", "逍遥散",
    "丹栀逍遥散", "越鞠丸", "保和丸", "二陈汤", "温胆汤",
    "小建中汤", "黄芪建中汤", "理中汤", "四物汤", "八珍汤",
    "肾气丸", "八味丸", "真武汤", "桂枝汤", "麻黄汤", "葛根汤",
    "旋复花汤", "栝蒌薤白汤", "木香槟榔丸", "香连丸", "益元散",
    "龙胆泻肝汤", "羚角钩藤汤", "天麻钩藤饮", "镇肝熄风汤",
    "独活寄生汤", "大防风汤", "虎潜丸", "大造丸", "左归饮", "右归饮",
    "七制化痰丸", "牛黄清心丸", "安宫牛黄丸", "至宝丹", "紫雪丹",
    "苏合香丸", "独参汤", "生脉散", "生脉汤", "炙甘草汤",
    "甘麦大枣汤", "半夏厚朴汤", "旋覆代赭汤", "橘皮竹茹汤",
    "大黄蛰虫丸", "大黄牡丹汤", "薏苡附子败酱散", "苇茎汤",
    "五味消毒饮", "仙方活命饮", "托里消毒散", "十宣散",
    "补肺汤", "百合固金汤", "养阴清肺汤", "沙参麦冬汤",
    "藿香正气散", "平胃散", "藿朴夏苓汤", "三仁汤", "甘露消毒丹",
    "清营汤", "清宫汤", "增液汤", "增液承气汤", "调胃承气汤",
    "新加香薷饮", "香薷饮", "清暑益气汤", "清络饮",
    "达原饮", "升降散", "甘露饮", "玉女煎", "清燥救肺汤",
    "桑菊饮", "银翘散", "桑杏汤", "清燥救肺汤",
]

# 常用药味词表
KNOWN_HERBS = [
    "人参", "黄芪", "白术", "茯苓", "甘草", "当归", "白芍", "赤芍", "川芎",
    "生地黄", "熟地黄", "生地", "熟地", "麦冬", "麦门冬", "天冬", "天门冬",
    "五味子", "柴胡", "黄芩", "黄连", "黄柏", "知母", "石膏", "寒水石",
    "半夏", "半夏曲", "陈皮", "橘红", "枳壳", "枳实", "厚朴", "苍术",
    "薏苡仁", "薏仁", "泽泻", "猪苓", "木通", "车前子", "滑石", "栀子",
    "山栀子", "连翘", "金银花", "银花", "蒲公英", "牡丹皮", "丹皮", "丹参",
    "桃仁", "红花", "益母草", "香附", "木香", "槟榔", "山楂", "神曲",
    "麦芽", "谷芽", "莱菔子", "萝卜子", "桔梗", "前胡", "杏仁", "桑白皮",
    "地骨皮", "贝母", "栝蒌", "栝蒌仁", "天花粉", "竹茹", "枇杷叶",
    "紫菀", "款冬花", "百部", "葶苈子", "苏子", "紫苏子", "旋覆花",
    "代赭石", "龙骨", "牡蛎", "磁石", "朱砂", "琥珀", "远志", "酸枣仁",
    "柏子仁", "石菖蒲", "菖蒲", "郁金", "桂枝", "肉桂", "桂心", "桂皮",
    "附子", "大附子", "干姜", "炮姜", "生姜", "吴茱萸", "花椒", "川椒",
    "丁香", "小茴香", "乌药", "沉香", "藿香", "佩兰", "砂仁", "白豆蔻",
    "白蔻仁", "草豆蔻", "草果", "防风", "荆芥", "荆芥穗", "薄荷",
    "蝉蜕", "牛蒡子", "大力子", "桑叶", "菊花", "蔓荆子", "藁本",
    "白芷", "细辛", "羌活", "独活", "秦艽", "威灵仙", "木瓜", "五加皮",
    "桑寄生", "杜仲", "续断", "牛膝", "骨碎补", "狗脊", "鹿茸", "鹿角胶",
    "鹿角霜", "龟板", "龟甲", "鳖甲", "鳖甲", "阿胶", "何首乌", "枸杞子",
    "枸杞", "女贞子", "墨旱莲", "旱莲草", "淫羊藿", "巴戟天", "肉苁蓉",
    "菟丝子", "沙苑子", "补骨脂", "益智仁", "山茱萸", "山药", "莲子",
    "芡实", "金樱子", "覆盆子", "桑螵蛸", "乌梅", "五倍子", "罂粟壳",
    "御米壳", "诃子", "肉豆蔻", "赤石脂", "禹余粮", "地榆", "槐花",
    "槐角", "侧柏叶", "白茅根", "茅根", "小蓟", "大蓟", "蒲黄", "五灵脂",
    "乳香", "没药", "延胡索", "玄胡索", "川楝子", "荔枝核", "橘核",
    "青皮", "天麻", "钩藤", "石决明", "珍珠母", "羚羊角", "水牛角",
    "玄参", "元参", "紫草", "青黛", "大青叶", "板蓝根", "射干",
    "马勃", "山豆根", "胖大海", "麻黄", "葛根", "升麻", "柴胡",
    "淡豆豉", "豆豉", "大豆黄卷", "神曲", "鸡内金", "鸡肫皮",
    "使君子", "苦楝皮", "槟榔", "南瓜子", "鹤草芽", "雷丸",
    "贯众", "败酱草", "红藤", "白藓皮", "苦参", "蛇床子",
    "土茯苓", "萆薢", "石韦", "海金沙", "瞿麦", "扁蓄", "冬葵子",
    "玉米须", "金钱草", "虎杖", "地肤子", "白茅根",
]

# 去重并按长度降序（优先匹配长词）
KNOWN_FORMULAS = sorted(set(KNOWN_FORMULAS), key=len, reverse=True)
KNOWN_HERBS = sorted(set(KNOWN_HERBS), key=len, reverse=True)


def extract_herbs(formula_text: str) -> list:
    """从方药文本中提取药味列表。"""
    if not formula_text:
        return []
    found = []
    text = formula_text
    for h in KNOWN_HERBS:
        if h in text:
            found.append(h)
            # 避免子串重复匹配（如"白芍"和"赤芍"都含"芍"但不会，因为按词匹配）
            text = text.replace(h, " " * len(h))
    # 去重保序
    seen = set()
    result = []
    for h in found:
        if h not in seen:
            seen.add(h)
            result.append(h)
    return result


def extract_formulas(formula_text: str) -> list:
    """从方药文本中提取引用方剂名列表。"""
    if not formula_text:
        return []
    found = []
    for f in KNOWN_FORMULAS:
        if f in formula_text:
            found.append(f)
    # 去重保序
    seen = set()
    result = []
    for f in found:
        if f not in seen:
            seen.add(f)
            result.append(f)
    return result


def process_all(check_only=False):
    """处理全部医案库。"""
    stats = {
        "libraries": 0,
        "entries_total": 0,
        "entries_with_herbs": 0,
        "entries_with_formulas": 0,
        "top_herbs": Counter(),
        "top_formulas": Counter(),
    }

    for f in sorted(KB.glob("asset*_*.json")):
        if "schema" in f.name:
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        if d.get("asset_type") != "case_library":
            continue

        stats["libraries"] += 1
        modified = False
        for e in d.get("entries", []):
            stats["entries_total"] += 1
            formula = e.get("formula", "")

            herbs = extract_herbs(formula)
            formulas_ref = extract_formulas(formula)

            if herbs:
                stats["entries_with_herbs"] += 1
                stats["top_herbs"].update(herbs)
            if formulas_ref:
                stats["entries_with_formulas"] += 1
                stats["top_formulas"].update(formulas_ref)

            if not check_only:
                if herbs and not e.get("herbs"):
                    e["herbs"] = herbs
                    modified = True
                if formulas_ref and not e.get("formulas_referenced"):
                    e["formulas_referenced"] = formulas_ref
                    modified = True

        if not check_only and modified:
            d["entry_count"] = len(d.get("entries", []))
            f.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"  ✅ {f.name} 已写回结构化字段")
        else:
            print(f"  📊 {f.name} 统计完成")

    return stats


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description="OPT-04 医案结构化字段提取")
    parser.add_argument("--check", action="store_true", help="仅统计不写回")
    args = parser.parse_args(argv if argv is not None else None)

    print(f"模式: {'仅统计' if args.check else '提取并写回'}")
    print()

    stats = process_all(check_only=args.check)

    print()
    print(f"=== 统计 ===")
    print(f"库数: {stats['libraries']}")
    print(f"医案总数: {stats['entries_total']}")
    print(f"含药味字段: {stats['entries_with_herbs']} ({stats['entries_with_herbs']/stats['entries_total']*100:.1f}%)")
    print(f"含方剂引用: {stats['entries_with_formulas']} ({stats['entries_with_formulas']/stats['entries_total']*100:.1f}%)")
    print()
    print(f"高频药味 TOP20:")
    for h, cnt in stats["top_herbs"].most_common(20):
        print(f"  {h}: {cnt}")
    print()
    print(f"高频方剂 TOP20:")
    for f, cnt in stats["top_formulas"].most_common(20):
        print(f"  {f}: {cnt}")

    if not args.check:
        print()
        print("✅ 结构化字段已写回，请运行 generate_rag_index.py 更新索引")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
