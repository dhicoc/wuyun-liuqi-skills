#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P11 验证：体质 / 易感性「激活」而非继续扩数据

背景（references/roadmap.md P11 + references/research-2026-08-13.md §5）：
  asset33 的 earth/fire 等「体质·易感性」条目**存在但零查询**——根因是个人
  档案路径从未把「出生/胎孕运气」作为召回 key 喂给 asset33，而非缺数据。
  本测试验证「激活」已生效：

  1. 覆盖度回升：扫描 1980–2010 出生年，断言先天运气召回的 asset33 rag_key
     并集同时覆盖 earth* 与 fire* 维度（即 earth/fire 不再零查询）。
  2. earth 维度被主动召回：存在样本出生年其先天易感性含 rag_key=earth_excess；
     fire 维度含 fire_deficient / fire_excess。
  3. §5 文献映射规则触发：出生 1990-05-20 的胎孕期运气（厥阴风木司天+少阳相火在泉）
     应触发「阳虚质倾向」体质倾向注释。
  4. 个人档案集成：generate_profile 文本含「先天运气·疾病易感性倾向」章节、
     含 asset33 召回条目、含「不替代临床诊断」红线。
  5. 路由激活分支：cases_routing.route_congenital 按先天运气 key 主动召回 asset33。
  6. 推理链 hook：infer_pathogenesis(congenital_keys=...) 在不改 base 输出的前提下
     追加召回条目（默认行为不变，报告快照不受影响）。

运行：
  python tests/verify_p11_congenital_activation.py
退出码 0 = 全部通过；非 0 = 存在未激活维度（P11 回归）。
"""

import os
import sys
import json
from pathlib import Path

# 让脚本可直接运行（CI 从仓库根执行）
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from yunqi_susceptibility import congenital_susceptibility  # noqa: E402
from personal_yunqi_profile import generate_profile  # noqa: E402
from cases_routing import route_congenital  # noqa: E402
from infer_pathogenesis import infer_pathogenesis  # noqa: E402


def _scan_years(start=1980, end=2010):
    outs = []
    for y in range(start, end + 1):
        outs.append(congenital_susceptibility(f"{y}-01-15"))
    return outs


def check_coverage():
    """覆盖度回升：earth* 与 fire* 维度均被先天运气主动召回。"""
    outs = _scan_years()
    keys = set()
    for o in outs:
        for s in o["susceptibility"]:
            keys.add(s["rag_key"])
    earth = any(k.startswith("earth") for k in keys)
    fire = any(k.startswith("fire") for k in keys)
    assert earth, f"earth* 维度零召回（keys={sorted(keys)}）——P11 未激活"
    assert fire, f"fire* 维度零召回（keys={sorted(keys)}）——P11 未激活"
    return f"召回 {len(keys)} 个 asset33 rag_key，earth/fire 均覆盖"


def check_earth_fire_explicit():
    """明确断言 earth_excess 与 fire 条目被主动召回。"""
    outs = _scan_years()
    all_keys = set()
    for o in outs:
        for s in o["susceptibility"]:
            all_keys.add(s["rag_key"])
    assert "earth_excess" in all_keys, "earth_excess 未被任何样本召回"
    assert ("fire_deficient" in all_keys) or ("fire_excess" in all_keys), \
        "fire_deficient/fire_excess 均未被召回"
    return "earth_excess 与 fire* 条目均被主动召回"


def check_yangxu_tendency():
    """§5 阳虚质规则：1990-05-20 胎孕期（厥阴风木司天+少阳相火在泉）触发阳虚质倾向。"""
    out = congenital_susceptibility("1990-05-20")
    names = [t["name"] for t in out["tendency"]]
    assert "阳虚质倾向" in names, f"阳虚质倾向未触发（tendency={names}）"
    # 触发组合的运气 key 应确实在召回 key 中（可解释性）
    keys = out["recall_keys"]
    assert "jueyin_fengmu_sitian" in keys and "shaoyang_xianghuo_zaiquan" in keys, \
        f"阳虚质触发组合 key 缺失（keys={keys}）"
    return "1990-05-20 胎孕期触发『阳虚质倾向』（厥阴风木司天+少阳相火在泉）"


def check_profile_integration():
    """个人档案集成：文本报告含激活章节 + 召回条目 + 红线。"""
    text = generate_profile("1990-05-20", as_json=False)
    assert "先天运气 · 疾病易感性倾向" in text, "个人档案缺少先天易感性章节"
    assert "asset33" in text, "个人档案未展示 asset33 召回"
    assert "不替代临床诊断" in text, "个人档案缺少临床免责红线"
    assert "阳虚质倾向" in text, "个人档案未呈现 §5 体质倾向"
    return "个人档案报告含激活章节 + asset33 召回 + 免责红线"


def check_routing_branch():
    """路由激活分支：route_congenital 按先天运气 key 主动召回 asset33。"""
    keys = ["earth_deficient", "jueyin_fengmu_sitian", "shaoyang_xianghuo_zaiquan"]
    r = route_congenital(keys)
    susc_keys = [s["rag_key"] for s in r["susceptibility"]]
    assert "earth_deficient" in susc_keys, "route_congenital 未召回 earth_deficient"
    assert "jueyin_fengmu_sitian" in susc_keys, "route_congenital 未召回厥阴风木司天"
    return f"route_congenital 召回 {len(susc_keys)} 条（含 earth/fire 维度）"


def check_infer_hook():
    """推理链 hook：congenital_keys 追加召回且 base 行为不变。"""
    base = infer_pathogenesis(2026)
    n_base = len(base["disease_susceptibility"])
    hooked = infer_pathogenesis(2026, congenital_keys=["fire_deficient", "earth_excess"])
    n_hook = len(hooked["disease_susceptibility"])
    assert n_hook >= n_base + 2, f"congenital_keys 未追加召回（{n_base}->{n_hook}）"
    # base 输出结构不被破坏（无 rag_key 注入，避免报告快照漂移）
    for d in base["disease_susceptibility"]:
        assert "rag_key" not in d, "infer_pathogenesis base 输出结构被改动"
    return f"infer_pathogenesis hook 追加 {n_hook - n_base} 条，base 结构不变"


CHECKS = [
    ("先天易感性覆盖度回升(earth/fire)", check_coverage),
    ("earth_excess 与 fire 条目主动召回", check_earth_fire_explicit),
    ("§5 阳虚质倾向规则触发", check_yangxu_tendency),
    ("个人档案激活章节集成", check_profile_integration),
    ("路由激活分支 route_congenital", check_routing_branch),
    ("推理链 congenital_keys hook", check_infer_hook),
]


def main():
    passed = 0
    failed = 0
    for name, fn in CHECKS:
        try:
            msg = fn()
            print(f"  [PASS] {name} — {msg}")
            passed += 1
        except AssertionError as e:
            print(f"  [FAIL] {name} — {e}")
            failed += 1
        except Exception as e:  # noqa: BLE001
            print(f"  [ERROR] {name} — {type(e).__name__}: {e}")
            failed += 1
    print(f"\nP11 激活验证：{passed} 通过 / {failed} 失败")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
