#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG 知识库校验工具
====================
检查 rag-knowledge-base/ 下所有 JSON 文件的格式与必填字段。

用法：
  python scripts/validate_knowledge_base.py
  python scripts/validate_knowledge_base.py --path rag-knowledge-base/asset1_suiyun.json
  python scripts/validate_knowledge_base.py --template
"""
import json
import os
import sys
import io
import argparse

# 允许脚本直接导入 generate_rag_index.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from generate_rag_index import check_index as check_rag_index
except Exception:
    check_rag_index = None

# Windows 终端默认编码可能不是 UTF-8，强制设置 stdout/stderr 编码
if sys.platform == 'win32' and sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except (AttributeError, io.UnsupportedOperation):
        pass


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_RAG_DIR = os.path.join(BASE_DIR, "rag-knowledge-base")

# 各 asset 类型建议的通用字段（非强制，但会提醒）
COMMON_RECOMMENDED_FIELDS = [
    "asset_name", "asset_type", "description", "total_entries", "entries"
]

# entries 条目的通用推荐字段
ENTRY_RECOMMENDED_FIELDS = [
    "entry_id", "entry_type"
]


def is_legacy_asset(data: dict) -> bool:
    """判断是否为旧版 asset 格式（允许缺少部分推荐字段）。"""
    # 旧版 asset 通常有 asset_name/asset_id，但 entries 中没有 entry_id/entry_type
    if "entries" in data and isinstance(data["entries"], list):
        if len(data["entries"]) > 0:
            first = data["entries"][0]
            if isinstance(first, dict):
                # 如果有 code/key 等字段但无 entry_id，认为是旧版
                has_old_keys = any(k in first for k in ["code", "key", "sitian_key", "zaiquan_key", "formula_id", "commentary_id", "region_id", "constitution_name"])
                has_new_fields = "entry_id" in first or "entry_type" in first
                if has_old_keys and not has_new_fields:
                    return True
    # asset7 顶层有 entries 且 entries 已有 entry_id/entry_type，但顶层缺少 asset_type/description/total_entries，也视为 legacy
    if "entries" in data and isinstance(data["entries"], list):
        if len(data["entries"]) > 0:
            first = data["entries"][0]
            if isinstance(first, dict) and ("entry_id" in first or "entry_type" in first):
                # 顶层缺少标准字段时视为 legacy
                if not all(k in data for k in ["asset_type", "description", "total_entries"]):
                    return True
    return False


def load_json(path: str) -> dict | list:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_asset_file(path: str) -> list[str]:
    """校验单个 asset 文件，返回错误列表。"""
    errors = []
    try:
        data = load_json(path)
    except json.JSONDecodeError as e:
        return [f"JSON 解析失败: {e}"]
    except Exception as e:
        return [f"读取失败: {e}"]

    if not isinstance(data, dict):
        return ["根对象必须是 JSON 对象"]

    # 如果是旧版 asset，仅做宽松校验
    legacy = is_legacy_asset(data)

    # asset7_constitution 的顶层结构特殊：既有 entries 又有 birth_yunqi_mapping 等并列数组
    # 只要根是对象且有 entries 或至少一个分类键，即视为合法
    has_entries = isinstance(data.get("entries"), list)
    has_legacy_groups = any(isinstance(data.get(k), list) for k in ["birth_yunqi_mapping", "suiyun_constitution_adjustment"])

    # 通用字段检查
    for field in COMMON_RECOMMENDED_FIELDS:
        if field not in data:
            if not legacy and not has_legacy_groups:
                errors.append(f"缺少推荐字段: {field}")

    entries = data.get("entries")
    if entries is None and not has_legacy_groups:
        errors.append("缺少 entries 数组")
        return errors
    if entries is not None and not isinstance(entries, list):
        errors.append("entries 必须是数组")
        return errors

    if entries is not None:
        total = data.get("total_entries")
        if isinstance(total, int) and total != len(entries):
            errors.append(f"total_entries ({total}) 与 entries 实际数量 ({len(entries)}) 不一致")

        for idx, entry in enumerate(entries):
            if not isinstance(entry, dict):
                errors.append(f"entries[{idx}] 必须是对象")
                continue
            for field in ENTRY_RECOMMENDED_FIELDS:
                if field not in entry:
                    if not legacy:
                        errors.append(f"entries[{idx}] 缺少推荐字段: {field}")
            # 检查至少有一个可检索键
            # 术语库使用 term/pinyin/entry_id；其他 asset 使用 code/key/rag_key 等
            if entry.get("entry_type") == "terminology":
                term_key_fields = ["term", "pinyin", "entry_id"]
                if not any(k in entry and entry[k] for k in term_key_fields):
                    errors.append(f"entries[{idx}] 术语条目缺少可检索键（term/pinyin/entry_id 至少一个）")
            else:
                key_fields = ["key", "code", "rag_key", "sitian_key", "zaiquan_key", "constitution_code", "region_id", "commentary_id"]
                if not any(k in entry and entry[k] for k in key_fields):
                    errors.append(f"entries[{idx}] 缺少可检索键（{', '.join(key_fields)} 至少一个）")

    return errors


def validate_directory(directory: str) -> dict[str, list[str]]:
    """校验目录下所有 JSON 文件。"""
    results = {}
    for fname in sorted(os.listdir(directory)):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(directory, fname)
        if os.path.isfile(path):
            results[fname] = validate_asset_file(path)
    schema_dir = os.path.join(directory, "schemas")
    if os.path.isdir(schema_dir):
        for fname in sorted(os.listdir(schema_dir)):
            if not fname.endswith(".json"):
                continue
            path = os.path.join(schema_dir, fname)
            if os.path.isfile(path):
                try:
                    load_json(path)
                    results[f"schemas/{fname}"] = []
                except Exception as exc:
                    results[f"schemas/{fname}"] = [f"Schema JSON 读取失败: {exc}"]
    return results


def generate_template(output_path: str):
    """生成一个标准条目模板文件。"""
    template = {
        "asset_name": "asset_custom_example",
        "asset_type": "custom",
        "description": "示例 asset，请替换为实际描述",
        "total_entries": 1,
        "source_file": "example.txt",
        "entries": [
            {
                "entry_id": "custom_example_001",
                "entry_type": "custom_entry",
                "title": "示例条目",
                "source": "《黄帝内经·素问》示例篇",
                "text": "示例正文，请替换为实际内容。",
                "topic": "示例主题",
                "rag_key": "example_key"
            }
        ]
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(template, f, ensure_ascii=False, indent=2)
    print(f"模板已生成: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="校验 RAG 知识库 JSON 文件")
    parser.add_argument("--path", "-p", default=DEFAULT_RAG_DIR,
                        help="要校验的 JSON 文件或目录（默认 rag-knowledge-base/）")
    parser.add_argument("--template", "-t", action="store_true",
                        help="生成一个标准条目模板文件到指定路径")
    args = parser.parse_args()

    if args.template:
        output = args.path if args.path != DEFAULT_RAG_DIR else os.path.join(DEFAULT_RAG_DIR, "template_example.json")
        generate_template(output)
        return

    if os.path.isfile(args.path):
        results = {os.path.basename(args.path): validate_asset_file(args.path)}
    elif os.path.isdir(args.path):
        results = validate_directory(args.path)
        if check_rag_index and os.path.abspath(args.path) == os.path.abspath(DEFAULT_RAG_DIR):
            ok, index_errors, _ = check_rag_index(os.path.join(DEFAULT_RAG_DIR, 'index.json'), DEFAULT_RAG_DIR)
            results['index_consistency'] = [] if ok else index_errors
    else:
        print(f"路径不存在: {args.path}")
        sys.exit(1)

    total_files = len(results)
    error_files = 0
    total_errors = 0

    for fname, errors in results.items():
        if errors:
            error_files += 1
            total_errors += len(errors)
            print(f"\n❌ {fname} — {len(errors)} 个问题")
            for err in errors:
                print(f"   - {err}")
        else:
            print(f"✅ {fname} — 校验通过")

    print(f"\n{'='*40}")
    print(f"校验文件数: {total_files}")
    print(f"通过: {total_files - error_files}")
    print(f"失败: {error_files}")
    print(f"总问题数: {total_errors}")

    if error_files > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
