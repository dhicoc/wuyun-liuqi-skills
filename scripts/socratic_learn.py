#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
苏格拉底式运气学学习模式（optimization-sprint Phase 5）

定位：用提问引导学生理解思想，而非直接灌输结果。
支持：
  - 默认：导出完整学习会话（问题 + 参考思路 + 经典概念）
  - --interactive：终端逐步问答（适合人类自学；Agent 可走非交互导出）

用法:
  python scripts/socratic_learn.py today
  python scripts/socratic_learn.py 2026-06-29 --output reports/generated/learn.md
  python scripts/socratic_learn.py today --concept 天人合一
  python scripts/socratic_learn.py today --interactive
  python scripts/socratic_learn.py today --json
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from _common import setup_environment, BOLD, CYAN, GREEN, YELLOW, RESET, color, resolve_year_or_date

setup_environment(add_lib=True, add_scripts=True)

from calculate_yunqi_api import calculate_yunqi_api  # noqa: E402
from yunqi_report import CONCEPT_PHILOSOPHY, explain_concept  # noqa: E402


@dataclass
class LearnTurn:
    """一轮问答。"""
    id: str
    question: str
    hint: str
    reference: str
    concept: Optional[str] = None


def _sui_line(result: Dict[str, Any]) -> str:
    s = result.get("sui_yun") or {}
    return f"{s.get('name', '')}{s.get('status', '')}"


def build_session(result: Dict[str, Any], focus_concept: Optional[str] = None) -> List[LearnTurn]:
    """根据推算结果构造苏格拉底式问题序列。"""
    year = result.get("yunqi_year")
    gz = result.get("year_gz", "")
    sui = _sui_line(result)
    sitian = result.get("si_tian", "")
    zaiquan = result.get("zai_quan", "")
    step = result.get("current_step") or {}
    th = result.get("tong_hua") or {}
    rel = step.get("relation", "")
    shun = step.get("shun_ni", "")

    tong_bits = []
    if th.get("tianfu"):
        tong_bits.append("天符")
    if th.get("suihui"):
        tong_bits.append("岁会")
    if th.get("taiyi_tianfu"):
        tong_bits.append("太乙天符")
    if th.get("pingqi"):
        tong_bits.append("平气")
    tong = "、".join(tong_bits) if tong_bits else "无特殊同化"

    turns: List[LearnTurn] = [
        LearnTurn(
            id="open",
            question=(
                f"先不看标准答案：你认为 {year} 年（{gz}）的岁运是「{sui}」，"
                f"这意味着天地之气偏于哪一端？太过与不及在思想上的区别是什么？"
            ),
            hint="从「中和」出发：太过是气有余，不及是气不足，都是偏离中正。",
            reference=(
                f"本年岁运为 {sui}。"
                f"{explain_concept('中和')}"
            ),
            concept="中和",
        ),
        LearnTurn(
            id="sitian",
            question=(
                f"上半年司天为「{sitian}」，下半年在泉为「{zaiquan}」。"
                f"若把一年比作一篇文章，司天与在泉各扮演什么角色？"
                f"这与「天人合一」有何关系？"
            ),
            hint="司天主上半年气机提纲，在泉主下半年；人随天地之气升降出入。",
            reference=(
                f"司天 {sitian}、在泉 {zaiquan}。"
                f"{explain_concept('天人合一')}"
            ),
            concept="天人合一",
        ),
        LearnTurn(
            id="current_step",
            question=(
                f"当前步位为「{step.get('name', '')}」："
                f"主气 {step.get('zhu_qi', '')}，客气 {step.get('ke_qi', '')}，"
                f"关系为「{rel}」（{shun}）。"
                f"若主气像「常驻节律」、客气像「过客之气」，你如何理解相得与不相得？"
            ),
            hint="相得多为顺，气机较协调；不相得为逆，提示当令气机有冲突张力。",
            reference=(
                f"当前：{step.get('name')} | 主{step.get('zhu_qi')} / 客{step.get('ke_qi')} | "
                f"{rel} → {shun}。\n"
                f"{explain_concept('气化')}"
            ),
            concept="气化",
        ),
        LearnTurn(
            id="tonghua",
            question=(
                f"本年运气同化情况：{tong}。"
                f"天符、岁会、太乙天符分别强调「运」与「气」怎样的相遇？"
                f"偏盛之年在思想上为何既是机遇也是考验？"
            ),
            hint="运与气同调曰符会；顺势易成，亦易太过。",
            reference=(
                f"同化：{tong}。\n"
                f"{explain_concept('天符')}"
            ),
            concept="天符",
        ),
        LearnTurn(
            id="synthesis",
            question=(
                "综合以上：请用三句话向一位从未听过运气的朋友说明——"
                "什么是运气学、今年格局的关键一笔、以及它如何体现「中和」思想。"
            ),
            hint="不必背术语；抓住：天地节律、本年偏颇、回归中正的生活态度。",
            reference=(
                f"参考骨架：{year}年{gz}，岁运{sui}，司天{sitian}/在泉{zaiquan}，"
                f"当前{step.get('name')}（{rel}）。思想核心见天人合一与中和。"
            ),
            concept="天人合一",
        ),
    ]

    if focus_concept:
        cname = focus_concept.strip()
        base = CONCEPT_PHILOSOPHY.get(cname)
        if base:
            turns.insert(
                0,
                LearnTurn(
                    id="focus_concept",
                    question=(
                        f"我们先聚焦概念「{cname}」。"
                        f"不看定义：你生活中有没有体验过类似的现象？"
                        f"（例如节律、偏颇、环境与身体同步）"
                    ),
                    hint=base.get("modern", "从现代生活经验找类比。"),
                    reference=explain_concept(cname),
                    concept=cname,
                ),
            )
        else:
            turns.insert(
                0,
                LearnTurn(
                    id="focus_concept",
                    question=f"你想深入的概念是「{cname}」。你目前对它的理解是什么？还有哪些困惑？",
                    hint="可从字面、经典语境、与五运六气的关系三层展开。",
                    reference=explain_concept(cname),
                    concept=cname,
                ),
            )

    return turns


def session_to_markdown(result: Dict[str, Any], turns: List[LearnTurn]) -> str:
    date_str = result.get("date", "")
    year = result.get("yunqi_year")
    lines = [
        f"# 苏格拉底学习会话 · {year}年（{result.get('year_gz', '')}）",
        "",
        f"> 参考日: {date_str}  ·  生成: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "学习方式：先自行回答「问题」，再展开「参考思路」。不必追求标准答案，重在理解思想。",
        "",
        "## 本日格局速览（可先不看）",
        "",
        f"- 岁运: {_sui_line(result)}",
        f"- 司天 / 在泉: {result.get('si_tian')} / {result.get('zai_quan')}",
        f"- 当前步位: {(result.get('current_step') or {}).get('name')} · "
        f"{(result.get('current_step') or {}).get('relation')}",
        "",
        "---",
        "",
    ]
    for i, t in enumerate(turns, 1):
        lines.append(f"## 第 {i} 问 · {t.id}")
        lines.append("")
        lines.append(f"**问题**：{t.question}")
        lines.append("")
        lines.append(f"<details><summary>提示</summary>")
        lines.append("")
        lines.append(t.hint)
        lines.append("")
        lines.append("</details>")
        lines.append("")
        lines.append(f"<details><summary>参考思路</summary>")
        lines.append("")
        lines.append(t.reference)
        lines.append("")
        lines.append("</details>")
        lines.append("")
        if t.concept:
            lines.append(f"_关联概念: {t.concept}_")
            lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("## 结束反思")
    lines.append("")
    lines.append("1. 本轮哪一问最难？卡在术语还是思想？")
    lines.append("2. 若只用一个词概括本年气质，你会选哪个？为什么？")
    lines.append("3. 想继续：可运行 `python scripts/export_thought_map.py today` 看结构图。")
    lines.append("")
    lines.append("_由 socratic_learn.py 生成 · 理论学习用途，非医疗建议_")
    return "\n".join(lines)


def run_interactive(turns: List[LearnTurn]) -> None:
    """终端逐步问答。"""
    print(color("—— 苏格拉底学习（交互）——", CYAN))
    print("每问可先作答；直接回车跳过作答，仅看参考思路。输入 q 退出。\n")
    for i, t in enumerate(turns, 1):
        print(color(f"【第 {i}/{len(turns)} 问】", BOLD))
        print(t.question)
        print(color(f"提示: {t.hint}", YELLOW))
        try:
            ans = input(color("你的想法> ", GREEN)).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n已结束会话。")
            return
        if ans.lower() in ("q", "quit", "exit", "退出"):
            print("已结束会话。")
            return
        if ans:
            print(color("（已记录你的思考；以下是参考思路，非唯一标准）", CYAN))
        print()
        print(t.reference)
        print()
        print("-" * 40)
        print()
    print(color("本轮完成。建议回顾「结束反思」或导出 Markdown 会话。", GREEN))


def resolve_date(raw: str) -> str:
    return resolve_year_or_date(raw)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="苏格拉底式五运六气学习会话",
        epilog="示例:\n  python scripts/socratic_learn.py today\n  python scripts/socratic_learn.py today --interactive",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("date", nargs="?", default="today", help="today / YYYY-MM-DD / 年份")
    parser.add_argument("--concept", help="优先聚焦的概念，如 天人合一、中和、天符")
    parser.add_argument("--interactive", "-i", action="store_true", help="终端逐步问答")
    parser.add_argument("--output", "-o", default=None, help="导出 Markdown 路径")
    parser.add_argument("--json", action="store_true", help="输出会话 JSON（含问题结构）")
    parser.add_argument("--no-file", action="store_true", help="不写文件，仅打印")
    args = parser.parse_args(list(argv) if argv is not None else None)

    date_str = resolve_date(args.date)
    result = calculate_yunqi_api(date_str)
    turns = build_session(result, focus_concept=args.concept)

    if args.interactive:
        run_interactive(turns)
        # 交互后仍可导出
        if args.output or not args.no_file:
            md = session_to_markdown(result, turns)
            out = Path(args.output) if args.output else (
                Path("reports/generated") / f"socratic_{result['yunqi_year']}_{date_str.replace('-', '')}.md"
            )
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(md, encoding="utf-8")
            print(f"\n✅ 会话已保存: {out}")
        return 0

    payload_turns = [asdict(t) for t in turns]
    if args.json:
        print(json.dumps({
            "date": date_str,
            "yunqi_year": result.get("yunqi_year"),
            "year_gz": result.get("year_gz"),
            "turns": payload_turns,
        }, ensure_ascii=False, indent=2))
        return 0

    md = session_to_markdown(result, turns)
    if args.no_file and not args.output:
        print(md)
        return 0

    out = Path(args.output) if args.output else (
        Path("reports/generated") / f"socratic_{result['yunqi_year']}_{date_str.replace('-', '')}.md"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(f"✅ 苏格拉底学习会话已导出: {out}")
    print(f"   共 {len(turns)} 问 · 运气年 {result.get('yunqi_year')}（{result.get('year_gz')}）")
    print("   交互模式: python scripts/socratic_learn.py today --interactive")
    return 0


if __name__ == "__main__":
    sys.exit(main())
