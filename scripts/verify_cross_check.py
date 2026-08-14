#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
推算引擎经典文献交叉验证

基于《医宗金鉴·运气要诀》《素问·天元纪大论》等公版经典中明确记载的
六十甲子运气同化格局，验证本项目推算引擎的正确性。

完全本地化，不依赖任何外部 API。

用法：
    python scripts/verify_cross_check.py
    python scripts/verify_cross_check.py --json

验证内容：
    1. 天符十二年（中运与司天同气）
    2. 岁会八年（中运临本支之位）
    3. 太乙天符四年（天符 + 岁会）
    4. 同天符六年（阳年，中运与在泉同气）
    5. 同岁会六年（阴年，中运与在泉同气）
    6. 六气正化对化（十二地支正化/对化判定）
    7. 五运齐化兼化（太过齐化、不及兼化）
    8. 平气判断（三条规则，依据 modules/yunqi-calc/references/taiguo_buji.md）

依据原文：
    「司天丁巳丁亥也火運火司天戊子戊午戊寅戊申也
     土運土司天己丑己未也金運金司天乙卯乙酉也
     水運水司天丙辰丙戌也共十二年」-- 天符十二年

    「木運臨卯丁卯年也火運臨午戊午年也金運臨酉
     乙酉年也水運臨子丙子年也此是四正土運臨四季
     甲辰甲戌己丑己未也此是四維共八年」-- 岁会八年

    「己丑己未乙酉戊午」-- 太乙天符四年

    「木運木在泉壬寅壬申也土運土在泉甲辰甲戌也
     金運金在泉庚子庚午也」-- 同天符六年（阳年）

    「水運水在泉辛丑辛未也火運火在泉癸邜癸酉癸
     巳癸亥也」-- 同岁会六年（阴年）
"""

import argparse
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib'))
from yunqi_data import (
    get_ganzhi, get_dayun, get_sitian, get_zaiquan,
    is_taiguo, check_tianfu, check_suihui, check_pingqi,
    check_tong_tianfu, check_tong_suihui,
    get_qihua, get_jianhua, get_zhengdui_huaqi,
    LIUQI_WUXING, DIZHI_WUXING, DIZHI_ZHENGDUI,
)

# ═══════════════════════════════════════════════════════════════
# 经典文献验证基线
# 依据：《医宗金鉴·运气要诀》天符太乙天符岁会同天符同岁会歌
# ═══════════════════════════════════════════════════════════════

# 天符十二年：中运五行 == 司天五行
# 原文：丁巳丁亥（木运/风木）、戊子戊午戊寅戊申（火运/君火相火）、
#       己丑己未（土运/湿土）、乙卯乙酉（金运/燥金）、丙辰丙戌（水运/寒水）
TIANFU_YEARS = {
    '丁巳', '丁亥',           # 木运，厥阴风木司天
    '戊子', '戊午',           # 火运，少阴君火司天
    '戊寅', '戊申',           # 火运，少阳相火司天
    '己丑', '己未',           # 土运，太阴湿土司天
    '乙卯', '乙酉',           # 金运，阳明燥金司天
    '丙辰', '丙戌',           # 水运，太阳寒水司天
}

# 岁会八年：大运五行临本辰之位（木临卯/火临午/金临酉/水临子/土临辰戌丑未）
# 四正：丁卯（木/卯木）、戊午（火/午火）、乙酉（金/酉金）、丙子（水/子水）
# 四维：甲辰甲戌（土/辰戌土）、己丑己未（土/丑未土）
SUIHUI_YEARS = {
    '丁卯', '戊午', '乙酉', '丙子',     # 四正
    '甲辰', '甲戌', '己丑', '己未',     # 四维
}

# 太乙天符四年：天符 + 岁会
# 原文：己丑己未、乙酉、戊午
TAIYI_TIANFU_YEARS = {'己丑', '己未', '乙酉', '戊午'}

# 同天符六年：阳年（太过），中运与在泉同气
# 原文：壬寅壬申（木运/风木在泉）、甲辰甲戌（土运/湿土在泉）、庚子庚午（金运/燥金在泉）
TONG_TIANFU_YEARS = {
    '壬寅', '壬申',           # 木运太过，厥阴风木在泉 -> 少阳相火司天
    '甲辰', '甲戌',           # 土运太过，太阴湿土在泉 -> 太阳寒水司天
    '庚子', '庚午',           # 金运太过，阳明燥金在泉 -> 少阴君火司天
}

# 同岁会六年：阴年（不及），中运与在泉同气
# 原文：辛丑辛未（水运/寒水在泉）、癸卯癸酉癸巳癸亥（火运/君火在泉）
TONG_SUIHUI_YEARS = {
    '辛丑', '辛未',           # 水运不及，太阳寒水在泉 -> 太阴湿土司天
    '癸卯', '癸酉', '癸巳', '癸亥',  # 火运不及，少阴君火在泉 -> 阳明燥金司天
}

# 六气正化对化（十二地支）
# 依据：《素问·天元纪大论》《医宗金鉴·运气要诀》六气正化对化图
ZHENGDUI_EXPECTED = {
    '午': ('少阴君火', '正化'), '子': ('少阴君火', '对化'),
    '未': ('太阴湿土', '正化'), '丑': ('太阴湿土', '对化'),
    '寅': ('少阳相火', '正化'), '申': ('少阳相火', '对化'),
    '酉': ('阳明燥金', '正化'), '卯': ('阳明燥金', '对化'),
    '辰': ('太阳寒水', '正化'), '戌': ('太阳寒水', '对化'),
    '巳': ('厥阴风木', '正化'), '亥': ('厥阴风木', '对化'),
}


def _year_to_ganzhi(year):
    """年份转干支"""
    gan, zhi = get_ganzhi(year)
    return f"{gan}{zhi}"


def _find_year_by_ganzhi(target_gz, start=1984, end=2043):
    """在 1984-2043 范围内找对应干支的年份（60甲子循环）"""
    for y in range(start, end + 1):
        if _year_to_ganzhi(y) == target_gz:
            return y
    return None


def verify_tianfu():
    """验证天符十二年"""
    results = []
    for gz in sorted(TIANFU_YEARS):
        year = _find_year_by_ganzhi(gz)
        if year is None:
            results.append({"gz": gz, "year": None, "expected": True, "actual": None, "pass": False})
            continue
        actual = check_tianfu(year)
        results.append({"gz": gz, "year": year, "expected": True, "actual": actual, "pass": actual == True})
    return results


def verify_suihui():
    """验证岁会八年（正向全命中 + 全甲子逆向无多报/无漏报）"""
    results = []
    # 正向：经典八年必须全部命中
    for gz in sorted(SUIHUI_YEARS):
        year = _find_year_by_ganzhi(gz)
        if year is None:
            continue
        actual = check_suihui(year)
        results.append({"gz": gz, "year": year, "expected": True, "actual": actual, "pass": actual == True})
    # 逆向：全甲子（1984-2043）扫描，凡命中的干支必须恰好等于经典八年集合
    # 此断言可接住「朴素判等把寅/巳/申/亥多算进来」这类回归（如壬寅/癸巳/庚申/辛亥）
    flagged = set()
    for year in range(1984, 2044):
        if check_suihui(year):
            flagged.add(_year_to_ganzhi(year))
    results.append({
        "gz": "全甲子逆向扫描", "year": None,
        "expected": "恰好 %d 年（%s）" % (len(SUIHUI_YEARS), "、".join(sorted(SUIHUI_YEARS))),
        "actual": "命中 %d 年（%s）" % (len(flagged), "、".join(sorted(flagged)) or "无"),
        "pass": (flagged == SUIHUI_YEARS),
    })
    return results


def verify_taiyi_tianfu():
    """验证太乙天符四年（正向全命中 + 全甲子逆向无多报）"""
    results = []
    for gz in sorted(TAIYI_TIANFU_YEARS):
        year = _find_year_by_ganzhi(gz)
        if year is None:
            continue
        actual = check_tianfu(year) and check_suihui(year)
        results.append({"gz": gz, "year": year, "expected": True, "actual": actual, "pass": actual == True})
    # 逆向：全甲子扫描，太乙天符命中集合必须恰好等于经典四年集合
    flagged = set()
    for year in range(1984, 2044):
        if check_tianfu(year) and check_suihui(year):
            flagged.add(_year_to_ganzhi(year))
    results.append({
        "gz": "全甲子逆向扫描", "year": None,
        "expected": "恰好 %d 年（%s）" % (len(TAIYI_TIANFU_YEARS), "、".join(sorted(TAIYI_TIANFU_YEARS))),
        "actual": "命中 %d 年（%s）" % (len(flagged), "、".join(sorted(flagged)) or "无"),
        "pass": (flagged == TAIYI_TIANFU_YEARS),
    })
    return results


def verify_tong_tianfu():
    """验证同天符六年"""
    results = []
    for gz in sorted(TONG_TIANFU_YEARS):
        year = _find_year_by_ganzhi(gz)
        if year is None:
            continue
        actual = check_tong_tianfu(year)
        results.append({"gz": gz, "year": year, "expected": True, "actual": actual, "pass": actual == True})
    return results


def verify_tong_suihui():
    """验证同岁会六年"""
    results = []
    for gz in sorted(TONG_SUIHUI_YEARS):
        year = _find_year_by_ganzhi(gz)
        if year is None:
            continue
        actual = check_tong_suihui(year)
        results.append({"gz": gz, "year": year, "expected": True, "actual": actual, "pass": actual == True})
    return results


def verify_zhengdui():
    """验证六气正化对化（十二地支）"""
    results = []
    for dz in ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']:
        expected = ZHENGDUI_EXPECTED[dz]
        # 找一个含此地支的年份
        for year in range(1984, 2044):
            _, yz = get_ganzhi(year)
            if yz == dz:
                qi, ztype = get_zhengdui_huaqi(year)
                results.append({
                    "dizhi": dz, "year": year,
                    "expected_qi": expected[0], "expected_type": expected[1],
                    "actual_qi": qi, "actual_type": ztype,
                    "pass": qi == expected[0] and ztype == expected[1],
                })
                break
    return results


def verify_qihua_jianhua():
    """验证齐化兼化逻辑（太过齐化、不及兼化）"""
    results = []
    # 太过之年应有齐化，不及之年应有兼化
    for year in [2024, 2026, 2025, 2027]:  # 甲辰(土太过)、丙午(水太过)、乙巳(金不及)、丁未(木不及)
        gz = _year_to_ganzhi(year)
        taiguo = is_taiguo(year)
        dayun, _ = get_dayun(year)
        if taiguo:
            qihua = get_qihua(year)
            jianhua = get_jianhua(year)
            # 太过应有齐化，无兼化
            ok = qihua is not None and jianhua is None
            results.append({"gz": gz, "year": year, "type": "太过",
                          "qihua": qihua, "jianhua": jianhua, "pass": ok})
        else:
            qihua = get_qihua(year)
            jianhua = get_jianhua(year)
            # 不及应有兼化，无齐化
            ok = jianhua is not None and qihua is None
            results.append({"gz": gz, "year": year, "type": "不及",
                          "qihua": qihua, "jianhua": jianhua, "pass": ok})
    return results


def verify_pingqi():
    """验证平气判断（据 modules/yunqi-calc/references/taiguo_buji.md 三条规则独立列举）

    依据：《素问·五常政大论》（意引「平气之年，气正令行」）、
          《素问·六微旨大论》（「亢则害，承乃制，制则生化」），
          及注家（王冰承制 / 张介宾得政得地）在 taiguo_buji.md 中的三段规则与示例。

    平气 = 太过/不及经司天之气调节后趋于平和：
      规则一   太过被抑:   太过之运 被 司天所克        → 平气  例戊辰(火太过·寒水司天)
      规则二A  不及同气相助: 不及之运 得 司天同气       → 平气  例丁巳(木不及·风木司天)
      规则二B  不及得司天所生: 不及之运 得 司天所生     → 平气  例癸亥(火不及·风木生火)
      反-太过同气  = 天符(同化更盛)  → 非平气  例戊午(火太过·君火司天)
      反-不及克运  = 不及更衰         → 非平气  例丁卯(木不及·燥金克木)
    """
    # (干支, 预期是否平气, 依据)
    CASES = [
        # ── 平气正例 ──
        ("戊辰", True,  "规则一 太过被抑：火太过·太阳寒水司天（水克火）"),
        ("丁巳", True,  "规则二A 不及同气相助：木不及·厥阴风木司天（同气，亦即天符）"),
        ("癸亥", True,  "规则二B 不及得司天生：火不及·厥阴风木司天（木生火）"),
        ("辛卯", True,  "规则二B 不及得司天生：水不及·阳明燥金司天（金生水）"),
        ("乙酉", True,  "规则二A 不及同气相助：金不及·阳明燥金司天（同气，亦即天符；历史 JS 漏判干支）"),
        # ── 平气反例 ──
        ("戊午", False, "反例 太过+司天同气 = 天符（同化更盛），非平气"),
        ("丙辰", False, "反例 太过+司天同气 = 天符（同化更盛），非平气"),
        ("丁卯", False, "反例 不及+司天克运 = 不及更衰，非平气"),
        ("丁酉", False, "反例 不及+司天克运 = 不及更衰，非平气"),
    ]
    results = []
    for gz, expected, basis in CASES:
        year = _find_year_by_ganzhi(gz)
        if year is None:
            results.append({"gz": gz, "year": None, "expected": expected,
                            "actual": None, "basis": basis, "pass": False})
            continue
        actual = check_pingqi(year)
        results.append({"gz": gz, "year": year, "expected": expected,
                        "actual": actual, "basis": basis, "pass": actual == expected})
    return results


def run_all():
    """运行全部验证"""
    suites = [
        ("天符十二年", verify_tianfu),
        ("岁会八年", verify_suihui),
        ("太乙天符四年", verify_taiyi_tianfu),
        ("同天符六年", verify_tong_tianfu),
        ("同岁会六年", verify_tong_suihui),
        ("六气正化对化", verify_zhengdui),
        ("五运齐化兼化", verify_qihua_jianhua),
        ("平气判断", verify_pingqi),
    ]
    
    all_results = {}
    total_pass = 0
    total_fail = 0
    
    for name, func in suites:
        items = func()
        passed = sum(1 for i in items if i.get("pass"))
        failed = len(items) - passed
        all_results[name] = {"items": items, "passed": passed, "failed": failed}
        total_pass += passed
        total_fail += failed
    
    all_results["summary"] = {
        "total_passed": total_pass,
        "total_failed": total_fail,
        "total": total_pass + total_fail,
        "status": "pass" if total_fail == 0 else "fail",
    }
    
    return all_results


def main():
    parser = argparse.ArgumentParser(description="推算引擎经典文献交叉验证（本地，无外部依赖）")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()
    
    results = run_all()
    
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        summary = results["summary"]
        print("=" * 60)
        print("  推算引擎经典文献交叉验证")
        print("  依据：《医宗金鉴·运气要诀》《素问·天元纪大论》")
        print("=" * 60)
        print()
        
        for name in [k for k in results if k != "summary"]:
            r = results[name]
            status = "✅" if r["failed"] == 0 else "❌"
            print(f"{status} {name}: {r['passed']}/{r['passed']+r['failed']} 通过")
            if r["failed"] > 0:
                for item in r["items"]:
                    if not item.get("pass"):
                        print(f"   ✗ {item}")
        
        print()
        s = results["summary"]
        print(f"总计: {s['total_passed']} 通过, {s['total_failed']} 失败, 共 {s['total']} 项")
        if s["status"] == "pass":
            print("✅ 全部通过")
        else:
            print("❌ 存在失败项")
        
    return 0 if results["summary"]["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
