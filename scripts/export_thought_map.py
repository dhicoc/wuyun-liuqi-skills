#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
思想地图导出（Mermaid）— optimization-sprint Phase 5 轻量实现

输出两类图：
1. 概念哲学关系图（天人合一 / 气化 / 中和 / 天符 等）
2. 某年/某日运气结构图（岁运 → 司天在泉 → 当前步位）

用法:
  python scripts/export_thought_map.py
  python scripts/export_thought_map.py today
  python scripts/export_thought_map.py 2026-06-29 --output reports/generated/thought_map.md
  python scripts/export_thought_map.py 2026 --format structure
  python scripts/export_thought_map.py --format both --json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from _common import setup_environment, resolve_year_or_date

setup_environment(add_lib=True, add_scripts=True)

from calculate_yunqi_api import calculate_yunqi_api  # noqa: E402
from yunqi_report import CONCEPT_PHILOSOPHY  # noqa: E402


def generate_concept_mermaid() -> str:
    """静态概念关系：运气学核心思想网络。"""
    lines = [
        "```mermaid",
        "flowchart TB",
        "  subgraph CORE[核心思想]",
        "    TH[天人合一]",
        "    QH[气化]",
        "    ZH[中和]",
        "  end",
        "  subgraph YUN[五运]",
        "    DY[大运/岁运]",
        "    ZY[主运五步]",
        "    KY[客运五步]",
        "  end",
        "  subgraph QI[六气]",
        "    ST[司天]",
        "    ZQ[在泉]",
        "    ZQ6[主气六步]",
        "    KQ6[客气六步]",
        "  end",
        "  subgraph HE[合化与加临]",
        "    TF[天符]",
        "    SH[岁会]",
        "    TY[太乙天符]",
        "    KJ[客主加临]",
        "  end",
        "  TH --> DY",
        "  TH --> ST",
        "  QH --> DY",
        "  QH --> ST",
        "  QH --> ZQ",
        "  ZH --> TF",
        "  ZH --> SH",
        "  DY --> ZY",
        "  DY --> KY",
        "  ST --> KQ6",
        "  ZQ --> KQ6",
        "  ZQ6 --> KJ",
        "  KQ6 --> KJ",
        "  DY --> TF",
        "  ST --> TF",
        "  DY --> SH",
        "  TF --> TY",
        "  SH --> TY",
        "```",
    ]
    # 附注：概念哲学短注
    notes = ["", "### 概念速览", ""]
    for name, c in CONCEPT_PHILOSOPHY.items():
        notes.append(f"- **{name}**：{c.get('philosophy', '')}")
    return "\n".join(lines + notes)


def generate_year_structure_mermaid(result: Dict[str, Any]) -> str:
    """基于某日推算结果的运气结构图。"""
    year = result.get("yunqi_year")
    gz = result.get("year_gz", "")
    sui = result.get("sui_yun") or {}
    step = result.get("current_step") or {}
    th = result.get("tong_hua") or {}

    sui_label = f"{sui.get('name', '')}{sui.get('status', '')}"
    step_label = f"{step.get('name', '')}\\n主{step.get('zhu_qi', '')}/客{step.get('ke_qi', '')}"
    rel = step.get("relation", "")
    tong_parts = []
    if th.get("tianfu"):
        tong_parts.append("天符")
    if th.get("suihui"):
        tong_parts.append("岁会")
    if th.get("taiyi_tianfu"):
        tong_parts.append("太乙天符")
    if th.get("pingqi"):
        tong_parts.append("平气")
    tong_label = "、".join(tong_parts) if tong_parts else "无特殊同化"

    # Mermaid 节点 ID 避免中文特殊字符问题：用 ASCII id
    lines = [
        "```mermaid",
        "flowchart TB",
        f"  Y[\"{year}年 {gz}\"]",
        f"  SY[\"岁运: {sui_label}\"]",
        f"  ST[\"司天: {result.get('si_tian', '')}\"]",
        f"  ZQ[\"在泉: {result.get('zai_quan', '')}\"]",
        f"  CS[\"当前: {step_label}\"]",
        f"  RL[\"客主: {rel}\"]",
        f"  TH[\"同化: {tong_label}\"]",
        "  Y --> SY",
        "  Y --> ST",
        "  Y --> ZQ",
        "  SY --> TH",
        "  ST --> TH",
        "  ST --> CS",
        "  ZQ --> CS",
        "  CS --> RL",
        "```",
    ]
    return "\n".join(lines)


def build_markdown(
    date_str: str,
    result: Optional[Dict[str, Any]],
    fmt: str,
) -> str:
    parts: List[str] = [
        f"# 五运六气思想地图",
        "",
        f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}  ·  参考日: {date_str}",
        "",
        "本图用于帮助理解运气学**概念关系**与**当年格局结构**，非临床诊断。",
        "",
    ]
    if fmt in ("concept", "both"):
        parts.append("## 1. 概念哲学关系图")
        parts.append("")
        parts.append(generate_concept_mermaid())
        parts.append("")
    if fmt in ("structure", "both") and result is not None:
        parts.append("## 2. 运气结构图（基于推算）")
        parts.append("")
        parts.append(
            f"- 运气年 **{result.get('yunqi_year')}**（{result.get('year_gz')}）"
            f" · 岁运 **{(result.get('sui_yun') or {}).get('name', '')}"
            f"{(result.get('sui_yun') or {}).get('status', '')}**"
        )
        parts.append(
            f"- 司天 **{result.get('si_tian')}** · 在泉 **{result.get('zai_quan')}**"
        )
        parts.append("")
        parts.append(generate_year_structure_mermaid(result))
        parts.append("")
        parts.append("### 反思问题")
        parts.append("")
        parts.append("1. 这张结构图里，哪一条边最能体现「天人合一」？")
        parts.append("2. 当前步位的客主关系，对你理解「中和」有何启发？")
        parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("_由 export_thought_map.py 生成 · 详见 docs/optimization-sprint.md_")
    return "\n".join(parts)


def resolve_input_date(raw: str) -> str:
    return resolve_year_or_date(raw)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="导出五运六气思想地图（Mermaid Markdown）",
        epilog="示例: python scripts/export_thought_map.py today --format both",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "date",
        nargs="?",
        default="today",
        help="日期 today / YYYY-MM-DD / 年份",
    )
    parser.add_argument(
        "--format",
        choices=["concept", "structure", "both"],
        default="both",
        help="concept=纯概念图, structure=当年结构, both=两者",
    )
    parser.add_argument("--output", "-o", default=None, help="输出 .md 路径")
    parser.add_argument("--json", action="store_true", help="同时打印元数据 JSON 到 stdout 摘要")
    args = parser.parse_args(argv)

    date_str = resolve_input_date(args.date)
    result: Optional[Dict[str, Any]] = None
    if args.format in ("structure", "both"):
        result = calculate_yunqi_api(date_str)

    md = build_markdown(date_str, result, args.format)

    if args.output:
        out = Path(args.output)
    else:
        year = (result or {}).get("yunqi_year") or date_str[:4]
        out = Path("reports/generated") / f"thought_map_{year}_{date_str.replace('-', '')}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")

    print(f"✅ 思想地图已导出: {out}")
    if args.json:
        meta = {
            "output": str(out),
            "date": date_str,
            "format": args.format,
            "yunqi_year": (result or {}).get("yunqi_year"),
            "year_gz": (result or {}).get("year_gz"),
        }
        print(json.dumps(meta, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
