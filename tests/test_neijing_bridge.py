#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P12 neijing_bridge 单元测试（不依赖外部网络，使用 vendored 快照）。

运行：python tests/test_neijing_bridge.py
"""
import os
import sys
import unittest.mock as mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))

import neijing_bridge as nb  # noqa: E402


def test_available():
    assert nb.neijing_available(), 'vendored 快照（scripts/lib/neijing_snapshot）应可用'


def test_discover_parses_22():
    root = nb.find_neijing_root()
    skills = nb.discover_neijing_skills(root)
    assert len(skills) == 22, f'应解析 22 个 skill，实际 {len(skills)}'
    for slug in ('yin-yang-balance', 'five-elements-network', 'qi-regulation'):
        assert slug in skills, f'缺少已知 skill: {slug}'
        sk = skills[slug]
        for key in ('R', 'I', 'E', 'B'):
            assert sk.sections.get(key), f'{slug} 缺少六节中的 {key}'
        assert sk.related, f'{slug} 应解析到 related_skills'


def test_select_fire_year():
    skills = nb.discover_neijing_skills(nb.find_neijing_root())
    ctx = nb.yunqi_context_from_parts('火', True, '少阴君火', '阳明燥金')
    sel = nb.select_skills(ctx, skills, top_n=3)
    assert any(s.skill.slug == 'yin-yang-balance' for s in sel), '火运年应入选 yin-yang-balance'
    assert not any(s.skill.slug in nb.CLINICAL_SLUGS for s in sel), '默认映射不应含临床 slug'


def test_build_framework_section():
    skills = nb.discover_neijing_skills(nb.find_neijing_root())
    ctx = nb.yunqi_context_from_parts('火', True, '少阴君火', '阳明燥金')
    sec = nb.build_methodology_for_ctx(ctx, top_n=3, with_safety=True)
    assert '## 内经方法论' in sec, '应含方法论章节标题'
    assert '出处' in sec, '应含章节出处引用'
    # 框架层默认不含三件套（报告尾部统一兜底）
    assert '临床安全提示' not in sec, '框架层默认不应含临床三件套'


def test_clinical_strip_and_safety():
    skills = nb.discover_neijing_skills(nb.find_neijing_root())
    clin_only = [
        nb.SelectedSkill(skill=skills[s], weight=1.0, reason='临床自检')
        for s in ('qi-regulation', 'excess-deficiency-decision', 'root-cause-priority')
        if s in skills
    ]
    sec = nb.build_methodology_section(clin_only, include_clinical=True, with_safety=True)
    assert '已剥离可执行操作步骤' in sec, '临床类应标注已剥离 E'
    # E 段可执行标记必须被剥离（拒诊拒方）
    assert '当 skill 被激活后' not in sec, '临床类应剥离 E 可执行步骤'
    assert '执业中医师' in sec, '临床类应含三件套免责'


def test_degrade_when_unavailable():
    ctx = nb.yunqi_context_from_parts('火', True, '少阴君火', '阳明燥金')
    with mock.patch.object(nb, 'find_neijing_root', return_value=None):
        assert nb.neijing_available() is False
        # 外部仓库缺失时优雅降级：返回空，绝不抛错
        assert nb.build_methodology_for_ctx(ctx, top_n=3) == ''
    # 空选择也返回空
    assert nb.build_methodology_section([]) == ''


if __name__ == '__main__':
    tests = [v for k, v in sorted(globals().items())
             if k.startswith('test_') and callable(v)]
    ok = 0
    for t in tests:
        try:
            t()
            print(f'[OK] {t.__name__}')
            ok += 1
        except AssertionError as e:
            print(f'[FAIL] {t.__name__}: {e}')
        except Exception as e:  # pragma: no cover
            print(f'[ERROR] {t.__name__}: {e}')
    print(f'{ok}/{len(tests)} passed')
    sys.exit(0 if ok == len(tests) else 1)
