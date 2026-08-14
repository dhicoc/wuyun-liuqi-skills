#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《素问》独立文献交叉校验（independent literature cross-check）。

目的：以《黄帝内经·素问》运气七篇原文为唯一权威源，对推算引擎的五类
「天符 / 岁会 / 太一天符(素问原字，后世注本作太乙天符) / 同天符 / 同岁会」做全甲子
逆向断言，证明算法输出与《素问》原文枚举**逐类恰好相等**（无多无少）。

这与 scripts/verify_cross_check.py 的口径不同：
- verify_cross_check.py 的权威源是《医宗金鉴·运气要诀》歌诀（注本）；
- 本脚本的权威源是《素问》正文原文（含 file:line 出处），二者相互独立，
  构成「算法 == 素问 == 医宗金鉴」三重互证。

《素问》原文枚举（从项目自带语料库 rag-knowledge-base/literature/ 抽取）：
- 天符十二年：《素问·六元正纪大论》
    :86 丙辰丙戌天符、:180 乙卯乙酉(并标太一天符)、:246 戊寅戊申天符、
    :346 己丑己未(并标太一天符)、:474 戊子戊午(并标太一天符)、
    :524 丁巳丁亥天符、:914 乙酉乙卯天符、:946 戊子戊午天符、:956 己丑己未天符
- 岁会八年（运临本辰）：《素问·六微旨大论》
    :154 「木运临卯、火运临午、土运临四季(辰戌丑未)、金运临酉、水运临子」
    => 丁卯(木/卯)、戊午(火/午)、甲辰甲戌(土/辰戌)、己丑己未(土/丑未)、
       乙酉(金/酉)、丙子(水/子)
- 太一天符 / 《素问》原字（后世注本作「太乙天符」）四年：《素问·六元正纪大论》
    :180 乙酉太一天符、:346 己丑己未太一天符、:474 戊午太一天符
    （另《素问·六微旨大论》:174「天符为执法，岁位为行令，太一天符为贵人」）
    = 天符 ∩ 岁会
- 同天符六年（阳年太过，中运与在泉同气）：《素问·六元正纪大论》
    :86 甲辰甲戌同天符、壬寅壬申同天符、庚子庚午同天符
- 同岁会六年（阴年不及，中运与在泉同气）：《素问·六元正纪大论》
    辛丑辛未同岁会、癸卯癸酉癸巳癸亥同岁会
"""

import os
import sys

# 让脚本能 import scripts/lib/yunqi_data.py
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, os.path.join(_ROOT, "scripts"))

from lib.yunqi_data import (  # noqa: E402
    get_ganzhi,
    check_tianfu,
    check_suihui,
    check_tong_tianfu,
    check_tong_suihui,
)


# ── 《素问》原文权威枚举（独立于此前的医宗金鉴口径）────────────────────
# 每条都可在 rag-knowledge-base/literature/ 的《素问》运气七篇定位到原文。
SUWEN_EXPECTED = {
    "天符": {
        "years": {
            "戊子", "戊午", "戊寅", "戊申", "乙卯", "乙酉",
            "丙辰", "丙戌", "丁巳", "丁亥", "己丑", "己未",
        },
        "source": "《素问·六元正纪大论》天符十二年枚举（丙辰丙戌/乙卯乙酉/"
                  "戊寅戊申/己丑己未/戊子戊午/丁巳丁亥）",
    },
    "岁会": {
        "years": {
            "丁卯", "戊午", "甲辰", "甲戌", "己丑", "己未", "乙酉", "丙子",
        },
        "source": "《素问·六微旨大论》:154「运临本辰」木临卯/火临午/"
                  "土临辰戌丑未/金临酉/水临子",
    },
    "太一天符(素问原字，后世注本作太乙天符)": {
        "years": {"乙酉", "己丑", "己未", "戊午"},
        "source": "《素问·六元正纪大论》太一天符四年（乙酉/己丑己未/戊午）；"
                  "《六微旨大论》:174「太一天符为贵人」= 天符 ∩ 岁会",
    },
    "同天符": {
        "years": {"甲辰", "甲戌", "壬寅", "壬申", "庚子", "庚午"},
        "source": "《素问·六元正纪大论》同天符六年（阳年太过，中运与在泉同气）",
    },
    "同岁会": {
        "years": {"辛丑", "辛未", "癸卯", "癸酉", "癸巳", "癸亥"},
        "source": "《素问·六元正纪大论》同岁会六年（阴年不及，中运与在泉同气）",
    },
}


def _ganzhi(year):
    return "".join(get_ganzhi(year))


def _compute(category):
    """对 1984-2043 一甲子跑算法，返回命中的干支集合。"""
    out = set()
    for y in range(1984, 2044):
        if category == "天符":
            ok = check_tianfu(y)
        elif category == "岁会":
            ok = check_suihui(y)
        elif category == "太一天符(素问原字，后世注本作太乙天符)":
            ok = check_tianfu(y) and check_suihui(y)
        elif category == "同天符":
            ok = check_tong_tianfu(y)
        elif category == "同岁会":
            ok = check_tong_suihui(y)
        else:
            ok = False
        if ok:
            out.add(_ganzhi(y))
    return out


def main():
    total_pass = 0
    total_fail = 0
    print("=" * 72)
    print("《素问》独立文献交叉校验（算法输出 vs 素问原文枚举，全甲子逆向断言）")
    print("=" * 72)
    for cat, info in SUWEN_EXPECTED.items():
        expected = info["years"]
        actual = _compute(cat)
        extra = sorted(actual - expected)   # 算法多算
        miss = sorted(expected - actual)    # 算法漏算
        ok = (actual == expected)
        total_pass += 1 if ok else 0
        total_fail += 0 if ok else 1
        status = "✓ 通过" if ok else "✗ 失败"
        print(f"\n[{status}] {cat}：算法 {len(actual)} 年 / 素问 {len(expected)} 年")
        print(f"    素问出处: {info['source']}")
        if not ok:
            if extra:
                print(f"    ⚠ 算法多算: {extra}")
            if miss:
                print(f"    ⚠ 算法漏算: {miss}")
        print(f"    实际命中: {sorted(actual)}")

    print("\n" + "=" * 72)
    print(f"汇总：{total_pass}/{total_pass + total_fail} 类与《素问》一致")
    print("=" * 72)
    if total_fail:
        print(f"❌ 存在 {total_fail} 类与《素问》原文不一致，CI 应失败。")
        return 1
    print("✅ 全部类别与《素问》运气七篇原文枚举逐类恰好相等（无多无少）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
