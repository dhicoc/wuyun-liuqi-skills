#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主运五步太少（太/少）回归测试。

锁定 `scripts/lib/yunqi_data.py::get_zhuyun_five_steps` 的「太少相生」模型：
  - 主运五步次序固定为 木火土金水；
  - 以当年大运(中运)五行所在步的太少为锚，相邻步太少交替；
  - 初运(木)的太少由大运太少与交替次数共同决定。

若将来改动主运推算，本测试可防止「初运太/少」回归。

直接运行: python tests/test_zhun_taishao.py
pytest 运行: pytest tests/test_zhuyun_taishao.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")
sys.path.insert(0, SCRIPTS)
sys.path.insert(0, os.path.join(SCRIPTS, "lib"))

from yunqi_data import (  # noqa: E402
    get_zhuyun_five_steps,
    get_dayun,
    is_taiguo,
    WUYUN_STEP,
)

# 经典「太少相生」模型下的初运(木)太少期望值。
# 覆盖五运 × {太过, 不及} 共 10 种格局。
# 推导：初运木太 iff (大运太 且 大运步位为奇数:木土水) 或 (大运少 且 大运步位为偶数:火金)。
ZHUYUN_FIRST_STEP_EXPECTED = {
    # 木运 (步位1, 奇): 太→太, 少→少
    2022: "太",   # 壬(木)太过
    2017: "少",   # 丁(木)不及
    # 火运 (步位2, 偶): 太→少, 少→太
    2018: "少",   # 戊(火)太过
    2023: "太",   # 癸(火)不及
    # 土运 (步位3, 奇): 太→太, 少→少
    2024: "太",   # 甲(土)太过
    2019: "少",   # 己(土)不及
    # 金运 (步位4, 偶): 太→少, 少→太
    2020: "少",   # 庚(金)太过
    2025: "太",   # 乙(金)不及
    # 水运 (步位5, 奇): 太→太, 少→少
    2026: "太",   # 丙(水)太过
    2021: "少",   # 辛(水)不及
}


def _first_step_taishao(year):
    steps = get_zhuyun_five_steps(year)
    # steps: [(step_num, element, tai_shao), ...]; 初运 = step 1 (木)
    assert steps[0][1] == "木", f"{year}: 初运应为木, 实际 {steps[0][1]}"
    return steps[0][2]


def test_zhuyun_first_step_taishao_classical():
    """初运(木)的太少必须符合经典太少相生模型（10 种格局全覆盖）"""
    for year, expected in ZHUYUN_FIRST_STEP_EXPECTED.items():
        actual = _first_step_taishao(year)
        assert actual == expected, (
            f"{year}: 初运(木)太少应为「{expected}」, 实际「{actual}」"
        )


def test_zhuyun_alternates_taishao():
    """主运五步太少必须严格相邻交替（太↔少）"""
    for year in range(1984, 2044):
        steps = get_zhuyun_five_steps(year)
        taishao = [s[2] for s in steps]
        assert taishao[0] in ("太", "少")
        for i in range(4):
            assert taishao[i] != taishao[i + 1], (
                f"{year}: 主运第{i+1}步与第{i+2}步太少未交替 "
                f"({taishao[i]} / {taishao[i+1]})"
            )


def test_zhuyun_dayun_step_matches_dayun():
    """大运所在步的太少必须与大运太过/不及一致"""
    for year in range(1984, 2044):
        dayun, _ = get_dayun(year)
        taiguo = is_taiguo(year)
        steps = get_zhuyun_five_steps(year)
        idx = WUYUN_STEP[dayun] - 1
        assert steps[idx][1] == dayun, f"{year}: 大运{dayun}所在步元素不符"
        expected = "太" if taiguo else "少"
        assert steps[idx][2] == expected, (
            f"{year}: 大运{dayun}所在步太少应为「{expected}」, 实际「{steps[idx][2]}」"
        )


def test_zhuyun_five_steps_order():
    """主运五步固定次序必须为 木火土金水"""
    for year in range(1984, 2044):
        steps = get_zhuyun_five_steps(year)
        elems = [s[1] for s in steps]
        assert elems == ["木", "火", "土", "金", "水"], (
            f"{year}: 主运五步次序错误 {elems}"
        )


if __name__ == "__main__":
    tests = [
        test_zhuyun_first_step_taishao_classical,
        test_zhuyun_alternates_taishao,
        test_zhuyun_dayun_step_matches_dayun,
        test_zhuyun_five_steps_order,
    ]
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
    print(f"\n✅ all {len(tests)} zhuyun taishao tests passed")
