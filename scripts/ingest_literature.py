#!/usr/bin/env python3
"""
五运六气 文献注入管道 (Literature Ingestion Pipeline)
=====================================================
统一入口：将原始文献文本 → 结构化 RAG Asset JSON。

用法：
  # 注入三因司天方 (经典)
  python scripts/ingest_literature.py --source "./raw-texts/sanyin_sitianfang.txt" \
      --category formula --output rag-knowledge-base/asset4_formula.json

  # 注入现代临床研究文献
  python scripts/ingest_literature.py --source "./raw-texts/modern_clinical.txt" \
      --category clinical --output rag-knowledge-base/asset5_clinical.json

  # 注入地域修正数据
  python scripts/ingest_literature.py --source "./raw-texts/regional_tcm.txt" \
      --category regional --output rag-knowledge-base/asset6_regional.json

  # 批量注入目录下所有文献
  python scripts/ingest_literature.py --batch ./raw-texts/ --output-dir rag-knowledge-base/

输出格式：与现有 asset1-3 兼容的 JSON 结构。
"""

# -*- coding: utf-8 -*-
import json
import os
import re
import sys
import hashlib
from typing import Any

from _common import setup_environment
setup_environment(add_lib=False)


# ── 分类目录 ──────────────────────────────────────────────

CATEGORIES = {
    "classics": {  # 经典原文
        "asset_prefix": "classic",
        "entry_type": "classic_quote",
        "required_fields": ["title", "source", "text", "topic"],
        "description": "黄帝内经、难经等经典原文节选",
    },
    "commentary": {  # 历代注家
        "asset_prefix": "commentary",
        "entry_type": "commentary",
        "required_fields": ["author", "dynasty", "text", "target_topic"],
        "description": "王冰、刘完素、张景岳等历代医家注释",
    },
    "formula": {  # 运气方药
        "asset_prefix": "formula",
        "entry_type": "formula",
        "required_fields": ["name", "source", "indications", "ingredients"],
        "description": "三因司天方、历代运气方剂",
    },
    "clinical": {  # 现代临床研究
        "asset_prefix": "clinical",
        "entry_type": "clinical_study",
        "required_fields": ["title", "year", "sample_size", "findings", "yunqi_pattern"],
        "description": "运气理论与现代临床的结合研究",
    },
    "regional": {  # 地域修正
        "asset_prefix": "regional",
        "entry_type": "regional_correction",
        "required_fields": ["region", "description", "correction_type", "correction_value"],
        "description": "不同地理区域的运气推算修正系数",
    },
    "custom": {  # 自定义
        "asset_prefix": "custom",
        "entry_type": "custom_entry",
        "required_fields": [],
        "description": "用户自定义分类",
    },
}


# ── 解析器工厂 ────────────────────────────────────────────

def parse_format_json(text: str) -> list[dict]:
    """如果输入已是 JSON 格式，直接解析。"""
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "entries" in data:
            return data["entries"]
        return [data]
    except json.JSONDecodeError:
        return None


def parse_markdown_sections(text: str) -> list[dict]:
    """从 Markdown 按 ## 标题分段提取结构化内容。"""
    entries = []
    # 匹配二级标题：## 标题名\n内容
    pattern = re.compile(r"^##\s+(.+)$\n(.*?)(?=^##|\Z)", re.MULTILINE | re.DOTALL)
    for match in pattern.finditer(text):
        title = match.group(1).strip()
        body = match.group(2).strip()
        entries.append({
            "title": title,
            "body": body,
            "source": "markdown_section",
        })
    return entries


def parse_key_value_pairs(text: str) -> list[dict]:
    """解析键值对格式：key: value 每行一对。"""
    entries = []
    current = {}
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line:
            if current:
                entries.append(current)
                current = {}
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            current[key.strip().lower().replace(" ", "_")] = val.strip()
    if current:
        entries.append(current)
    return entries


def detect_format(text: str) -> str:
    """自动检测文本格式。"""
    text_stripped = text.strip()
    if text_stripped.startswith("{"):
        return "json"
    if text_stripped.startswith("["):
        return "json"
    if re.search(r"^##\s+", text_stripped, re.MULTILINE):
        return "markdown"
    if re.search(r"^[\w\u4e00-\u9fff]+:", text_stripped, re.MULTILINE):
        return "kv"
    return "plain"


def parse_text(text: str, category: str) -> list[dict]:
    """自动检测格式并解析。"""
    fmt = detect_format(text)
    if fmt == "json":
        return parse_format_json(text)
    if fmt == "markdown":
        return parse_markdown_sections(text)
    if fmt == "kv":
        return parse_key_value_pairs(text)
    # plain text — 按段落拆分
    return [{"body": p.strip()} for p in text.split("\n\n") if p.strip()]


# ── 验证器 ────────────────────────────────────────────────

def validate_entry(entry: dict, category: str) -> list[str]:
    """检查条目是否满足分类的必填字段。"""
    cat_info = CATEGORIES.get(category, CATEGORIES["custom"])
    missing = []
    for field in cat_info["required_fields"]:
        if field not in entry or not entry[field]:
            missing.append(field)
    return missing


def assign_entry_id(entry: dict, category: str) -> str:
    """为条目分配唯一 ID。"""
    key_material = json.dumps(entry, sort_keys=True, ensure_ascii=False)
    hash_suffix = hashlib.md5(key_material.encode("utf-8")).hexdigest()[:8]
    prefix = CATEGORIES.get(category, CATEGORIES["custom"])["asset_prefix"]
    return f"{prefix}_{hash_suffix}"


# ── 核心注入逻辑 ──────────────────────────────────────────

def ingest(
    source_path: str,
    category: str = "custom",
    validate: bool = True,
    verbose: bool = True,
) -> dict[str, Any]:
    """
    注入一篇文献到结构化格式。

    参数：
        source_path: 源文件路径（txt/md/json）
        category:   分类（classics/commentary/formula/clinical/regional/custom）
        validate:   是否校验必填字段
        verbose:    是否打印详细日志

    返回：
        {
            "asset": { ... },     # 可直接写入文件的完整 asset JSON
            "stats": { ... }      # 统计信息
        }
    """
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"源文件不存在: {source_path}")

    with open(source_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # 解析
    raw_entries = parse_text(raw_text, category)
    if not raw_entries:
        print(f"  [WARN] 未解析出任何条目: {source_path}")
        return {"asset": None, "stats": {"total": 0, "valid": 0, "invalid": 0}}

    # 验证 + 赋 ID
    cat_info = CATEGORIES.get(category, CATEGORIES["custom"])
    validated = []
    invalid = []
    for entry in raw_entries:
        entry["entry_type"] = cat_info["entry_type"]
        entry["entry_id"] = assign_entry_id(entry, category)
        if validate:
            missing = validate_entry(entry, category)
            if missing:
                invalid.append({"entry": entry, "missing_fields": missing})
                continue
        validated.append(entry)

    # 构造 asset
    source_basename = os.path.basename(source_path)
    asset = {
        "asset_name": f"asset_{cat_info['asset_prefix']}_{source_basename.split('.')[0]}",
        "asset_type": category,
        "description": cat_info["description"],
        "total_entries": len(validated),
        "source_file": source_basename,
        "entries": validated,
    }

    stats = {
        "total": len(raw_entries),
        "valid": len(validated),
        "invalid": len(invalid),
    }

    if verbose:
        print(f"  ✓ 解析完成: {source_basename}")
        print(f"    分类: {category}")
        print(f"    总条目: {stats['total']} → 有效: {stats['valid']}, 无效: {stats['invalid']}")
        if invalid:
            print(f"    警告: {len(invalid)} 条缺少必填字段")

    return {"asset": asset, "stats": stats}


def batch_ingest(
    source_dir: str,
    output_dir: str = "rag-knowledge-base",
    validate: bool = True,
) -> list[dict]:
    """
    批量注入目录下所有文献。

    命名约定：
      - {category}__{name}.txt   → 显式指定分类
      - {name}.txt               → 自动检测分类
    """
    os.makedirs(output_dir, exist_ok=True)

    results = []
    files = sorted(os.listdir(source_dir))

    for fname in files:
        if not fname.endswith((".txt", ".md", ".json")):
            continue
        fpath = os.path.join(source_dir, fname)

        # 从文件名推断分类：category__name.txt
        inferred_cat = "custom"
        if "__" in fname:
            cat_part = fname.split("__")[0]
            if cat_part in CATEGORIES:
                inferred_cat = cat_part

        try:
            result = ingest(fpath, category=inferred_cat, validate=validate)
            if result["asset"]:
                out_path = os.path.join(output_dir, f"{result['asset']['asset_name']}.json")
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(result["asset"], f, ensure_ascii=False, indent=2)
                result["output_path"] = out_path
                print(f"  → 写入: {out_path}")
            results.append(result)
        except Exception as e:
            print(f"  [ERROR] {fname}: {e}")

    return results


# ── CLI ───────────────────────────────────────────────────

def interactive_add_entry(category: str | None = None, output_path: str = "rag-knowledge-base/custom_entries.json") -> dict:
    """交互式添加单个条目到 RAG 知识库。"""
    import readline  # noqa: F401

    print("\n=== 交互式添加 RAG 知识库条目 ===")
    print("可用分类：")
    for key, info in CATEGORIES.items():
        print(f"  {key:12s} → {info['description']}")

    if category is None:
        category = input("\n请选择分类 (默认 custom): ").strip() or "custom"
    if category not in CATEGORIES:
        print(f"未知分类: {category}，已降级为 custom")
        category = "custom"

    cat_info = CATEGORIES[category]
    required = cat_info["required_fields"]

    print(f"\n已选择分类: {category}")
    print(f"必填字段: {', '.join(required) if required else '无'}")

    entry = {"entry_type": cat_info["entry_type"]}
    for field in required:
        value = input(f"  {field}: ").strip()
        if value:
            # 尝试解析 JSON 数组/对象
            try:
                parsed = json.loads(value)
                entry[field] = parsed
            except json.JSONDecodeError:
                entry[field] = value

    # 允许用户额外添加自定义字段
    print("\n是否添加额外字段? (直接回车结束)")
    while True:
        extra = input("  额外字段名 (或回车结束): ").strip()
        if not extra:
            break
        extra_value = input(f"  {extra} 的值: ").strip()
        try:
            entry[extra] = json.loads(extra_value)
        except json.JSONDecodeError:
            entry[extra] = extra_value

    # 验证
    missing = validate_entry(entry, category)
    if missing:
        print(f"[WARN] 缺少必填字段: {', '.join(missing)}")
        proceed = input("是否继续保存? (y/N): ").strip().lower()
        if proceed not in ("y", "yes"):
            print("已取消保存。")
            return {"saved": False, "entry": entry}

    entry["entry_id"] = assign_entry_id(entry, category)

    # 读取或创建 asset
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            asset = json.load(f)
    else:
        asset = {
            "asset_name": f"asset_{cat_info['asset_prefix']}_custom",
            "asset_type": category,
            "description": cat_info["description"],
            "total_entries": 0,
            "source_file": "interactive",
            "entries": [],
        }

    asset["entries"].append(entry)
    asset["total_entries"] = len(asset["entries"])

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(asset, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 已保存条目: {entry['entry_id']}")
    print(f"→ 输出文件: {output_path}")
    return {"saved": True, "entry": entry, "output_path": output_path}


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="五运六气文献注入管道 — 将原始文本转为结构化 RAG Asset JSON"
    )
    parser.add_argument("--source", "-s", help="单篇文献路径")
    parser.add_argument("--batch", "-b", help="批量处理目录")
    parser.add_argument("--category", "-c", default="custom",
                        choices=list(CATEGORIES.keys()),
                        help="文献分类")
    parser.add_argument("--output", "-o", default=None,
                        help="输出文件路径（单篇模式）")
    parser.add_argument("--output-dir", "-d", default="rag-knowledge-base",
                        help="输出目录（批量模式）")
    parser.add_argument("--no-validate", action="store_true",
                        help="跳过字段校验")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="交互式添加单个条目到 RAG 知识库")
    parser.add_argument("--interactive-category", default=None,
                        help="交互模式下的默认分类")
    parser.add_argument("--interactive-output", default="rag-knowledge-base/custom_entries.json",
                        help="交互模式下的输出文件路径")
    parser.add_argument("--list-categories", action="store_true",
                        help="列出所有可用分类")

    args = parser.parse_args()

    if args.interactive:
        interactive_add_entry(args.interactive_category, args.interactive_output)
        return

    if args.list_categories:
        print("可用分类：")
        for key, info in CATEGORIES.items():
            print(f"  {key:12s} → {info['description']}")
        return

    if args.batch:
        batch_ingest(args.batch, args.output_dir, validate=not args.no_validate)
        return

    if not args.source:
        parser.print_help()
        return

    result = ingest(args.source, args.category, validate=not args.no_validate)
    if result["asset"] is None:
        print("错误：未能解析出有效条目。")
        sys.exit(1)

    output_path = args.output or os.path.join(
        ".", f"{result['asset']['asset_name']}.json"
    )
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result["asset"], f, ensure_ascii=False, indent=2)
    print(f"\n→ 已写入: {output_path}")


if __name__ == "__main__":
    main()
