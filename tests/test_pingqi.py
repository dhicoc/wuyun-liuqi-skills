#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
平气判定回归测试。

锁定 scripts/lib/yunqi_data.py::check_pingqi 的三条规则
（据 modules/yunqi-calc/references/taiguo_buji.md）：
  - 规则一  太过被抑:   大运太过 且 司天克大运      → 平气
  - 规则二A 不及同气相助: 大运不及 且 司天 == 大运   → 平气
  - 规则二B 不及得司天生运: 大运不及 且 司天生大运   → 平气

此前实现漏掉规则二A，导致「丁巳」等不及同气之年被误判为非平气。
本测试同时锁定非平气边界（太过同气=天符、不及被克=更衰）。

直接运行: python tests/test_pingqi.py
pytest 运行: pytest tests/test_pingqi.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, os.path.join(SCRIPTS, "lib"))

from yunqi_data import check_pingqi, get_ganzhi  # noqa: E402

# (年份, 期望干支, 期望平气, 命中规则)
PINGQI_CASES = [
    # 规则一：太过被抑
    (1988, "戊辰", True,  "规则一 太过被抑(太阳寒水司天克火运太过)"),
    (2018, "戊戌", True,  "规则一 太过被抑(太阳寒水司天克火运太过)"),
    # 规则二A：不及同气相助
    (1977, "丁巳", True,  "规则二A 不及同气相助(厥阴风木司天==木运不及)"),
    # 规则二B：不及得司天生运
    (1983, "癸亥", True,  "规则二B 不及得司天生运(厥阴风木司天生火运不及)"),
    # 非平气边界
    (2026, "丙午", False, "水运太过+少阴君火司天(运克天, 非平气)"),
    (1957, "丁酉", False, "木运不及+阳明燥金司天(司天克运, 不及更衰)"),
    (1978, "戊午", False, "火运太过+少阴君火司天(同气=天符, 非平气)"),
]


def test_pingqi_rules():
    for year, ganzhi_expected, expected, _rule in PINGQI_CASES:
        actual_gz = "".join(get_ganzhi(year))
        assert actual_gz == ganzhi_expected, (
            f"{year}: 期望干支 {ganzhi_expected}, 实际 {actual_gz}"
        )
        actual = check_pingqi(year)
        assert actual == expected, (
            f"{year}({ganzhi_expected}): 平气期望 {expected}, 实际 {actual} ({_rule})"
        )


def test_pingqi_rule2a_regression():
    """规则二A 专项（修复点）：不及 + 司天同气 必须判为平气"""
    # 丁巳(1977): 木运不及 + 厥阴风木司天(木) → 同气相助 → 平气
    assert check_pingqi(1977) is True
    # 丁亥: 木运不及 + 厥阴风木司天(木) → 同气相助 → 平气
    # 丁亥年: (Y-4)%10==3(丁) 且 (Y-4)%12==11(亥) → Y%60==3 → 1983? 校验由 get_ganzhi 兜底
    for y in range(1980, 2040):
        if "".join(get_ganzhi(y)) == "丁亥":
            assert check_pingqi(y) is True
            break


if __name__ == "__main__":
    tests = [test_pingqi_rules, test_pingqi_rule2a_regression]
    failed = []
    for t in tests:
        try:
            t()
            print(f"[PASS] {t.__name__}")
        except AssertionError as e:
            print(f"[FAIL] {t.__name__}: {e}")
            failed.append(t.__name__)
    if failed:
        print(f"\n❌ {len(failed)} test(s) failed: {failed}")
        sys.exit(1)
    print(f"\n✅ all {len(tests)} pingqi tests passed")
