#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_distilled_integration.py — 蒸馏研读框架 RAG 整合回归/一致性检查

检查范围（pilot 副本内执行）：
  1. index.json 声明的 total_entries 与 rag-knowledge-base/asset*.json 实文件数一致。
  2. 每个蒸馏资产（通过 rag-knowledge-base/distilled/<slug>/SKILL.md 实体目录判定）：
       C1 文件落盘存在
       C2 在 rag_search.py 的 ASSET_FILES 中注册
       C3 在 rag_search.py 的 _default_asset_keys 白名单中（否则 --key 静默 0 命中）
       C4 routing.yaml 有对应 distilled/<slug>/SKILL.md 路由任务
       C5 entries 可加载且数量 == index 记录
       C6 每个 entry 的 rag_key 存在（结合 C3 即可精确命中）
  3. 关键词融合：跨蒸馏资产 + 既有资产都能命中（证明统一检索融合）。
  4. 集成冒烟：对每个蒸馏资产抽一个 example_key 跑真实 rag_search --key，确认命中且归属正确。

用法：
  python scripts/check_distilled_integration.py
  python scripts/check_distilled_integration.py --quiet
退出码：0 = 全绿；1 = 有 FAIL。
"""
import argparse
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAG_DIR = os.path.join(ROOT, "rag-knowledge-base")
ROUTING = os.path.join(ROOT, "routing.yaml")
RAG_SEARCH = os.path.join(HERE, "rag_search.py")


def load_index():
    with open(os.path.join(RAG_DIR, "index.json"), encoding="utf-8") as f:
        return json.load(f)


def load_rag_search_registry():
    """读取 rag_search.py 的 ASSET_FILES 与 _default_asset_keys（优先 import 真实符号）。"""
    asset_files = {}
    default_keys = []
    try:
        sys.path.insert(0, HERE)
        import importlib
        mod = importlib.import_module("rag_search")
        asset_files = dict(getattr(mod, "ASSET_FILES", {}) or {})
        default_keys = list(getattr(mod, "_default_asset_keys", lambda: [])() or [])
    except Exception as ex:  # noqa
        # import 失败才退到静态解析（通常不该发生）
        sys.stderr.write(f"[warn] import rag_search 失败，改用静态解析: {ex}\n")
        src = open(RAG_SEARCH, encoding="utf-8").read()
        for m in re.finditer(r'"([a-zA-Z0-9_]+)"\s*:\s*"([a-zA-Z0-9_]+\.json)"', src):
            asset_files.setdefault(m.group(1), m.group(2))
        # _default_asset_keys 以循环 + return keys 构建，静态解析改为：从 ASSET_FILES 取
        # 所有在白名单注释附近出现的 key 不可靠，故仅当 import 失败时报缺失由调用方处理。
    return asset_files, default_keys


def slug_of(asset_id):
    # asset35_yizong_jinjian_yunqi_yaojue -> yizong-jinjian-yunqi-yaojue
    _, _, rest = asset_id.partition("_")
    return rest.replace("_", "-")


def discover_distilled_assets(index_entries):
    """通过磁盘 rag-knowledge-base/distilled/<slug>/SKILL.md 判定蒸馏资产。

    不依赖 index.json 的 asset_category=='distilled_study'：canonical 的
    generate_rag_index.py 不会写该字段（否则会与 validate_knowledge_base 的
    index 一致性检查冲突）。蒸馏资产的真相源是 distilled/<slug>/SKILL.md 实体目录，
    由 index_distilled_*.py 注册、routing.yaml 路由、rag_search --key 取数。
    """
    distilled_dir = os.path.join(RAG_DIR, "distilled")
    slugs = set()
    if os.path.isdir(distilled_dir):
        for name in os.listdir(distilled_dir):
            if os.path.isfile(os.path.join(distilled_dir, name, "SKILL.md")):
                slugs.add(name)
    out = []
    for e in index_entries:
        aid = e.get("asset_id")
        if aid and slug_of(aid) in slugs:
            out.append(e)
    return out


def actual_asset_files():
    # 资产文件形如 assetNN_*.json；术语库特例 terminology.json（index 中资产 id=asset8_terminology）
    return sorted(
        f for f in os.listdir(RAG_DIR)
        if (re.match(r"^asset\d+_.*\.json$", f) or f == "terminology.json")
    )


def run_rag_search(keys=None, terms=None):
    cmd = [sys.executable, RAG_SEARCH]
    if keys:
        for k in keys:
            cmd += ["--key", k]
    if terms:
        cmd += terms
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=120,
                             cwd=ROOT, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        return out.stdout + out.stderr
    except Exception as e:  # noqa
        return f"__RAG_SEARCH_ERROR__ {e}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    fails = []
    infos = []

    index = load_index()
    declared_total = index.get("total_entries")
    entries = index.get("entries", [])
    index_files = sorted({e.get("file") for e in entries if e.get("file")})
    actual = actual_asset_files()
    actual_set = set(actual)

    # 1. total / 文件一致性（以 index 登记的 file 为准，兼容 terminology.json 特例命名）
    missing = [f for f in index_files if not os.path.exists(os.path.join(RAG_DIR, f))]
    orphans = [f for f in actual if f not in set(index_files)]
    count_ok = (declared_total == len(index_files))
    if missing:
        fails.append(f"[1] index 引用资产文件缺失: {missing}")
    if orphans:
        fails.append(f"[1] 磁盘存在未登记资产文件(orphan): {orphans}")
    if not count_ok:
        fails.append(f"[1] index.total_entries={declared_total} 但 index 登记文件数={len(index_files)}")
    if not (missing or orphans or not count_ok):
        infos.append(f"[1] total_entries={declared_total} == index 文件数 {len(index_files)}，无缺失/无 orphan ✅")

    asset_files, default_keys = load_rag_search_registry()
    routing_text = open(ROUTING, encoding="utf-8").read()

    distilled = discover_distilled_assets(entries)
    infos.append(f"    蒸馏资产数（distilled/<slug>/SKILL.md 实体目录）: {len(distilled)}")

    for e in distilled:
        aid = e.get("asset_id")
        fname = e.get("file")
        slug = slug_of(aid)
        route_marker = f"distilled/{slug}/SKILL.md"
        idx_total = e.get("total_entries")
        label = f"[{aid}]"

        # C1
        on_disk = os.path.exists(os.path.join(RAG_DIR, fname)) if fname else False
        if not on_disk:
            fails.append(f"{label} C1 文件缺失: {fname}")
        # C2/C3 用规范短键（asset34），_default_asset_keys 与 ASSET_FILES 均以短键登记
        short_key = re.match(r"asset\d+", aid).group(0)
        registered = short_key in asset_files and asset_files.get(short_key) == fname
        if not registered:
            fails.append(f"{label} C2 未在 ASSET_FILES 注册为 {fname}（short key={short_key}）")
        in_whitelist = short_key in default_keys
        if not in_whitelist:
            fails.append(f"{label} C3 不在 _default_asset_keys 白名单（--key 会静默 0 命中）")
        # C4
        routed = route_marker in routing_text
        if not routed:
            fails.append(f"{label} C4 routing.yaml 缺路由: {route_marker}")
        # C5 + C6
        rc = 0
        if on_disk:
            try:
                d = json.load(open(os.path.join(RAG_DIR, fname), encoding="utf-8"))
                ents = d.get("entries", [])
                rc = len(ents)
                if idx_total is not None and rc != idx_total:
                    fails.append(f"{label} C5 entries 数 {rc} != index {idx_total}")
                missing_keys = [x.get("rag_key") for x in ents if not x.get("rag_key")]
                if missing_keys:
                    fails.append(f"{label} C6 有 entry 缺 rag_key: {missing_keys}")
            except Exception as ex:  # noqa
                fails.append(f"{label} C5/C6 加载失败: {ex}")

        if not any(f.startswith(label) for f in fails):
            infos.append(f"{label} C1-C6 ✅ ({fname}, {rc} entries, route={routed}, whitelist={in_whitelist})")

    # 3+4. 集成冒烟 + 融合
    fusion_terms = ["司天在泉", "运气证治", "王旭高", "天干"]
    distilled_ids = {e.get("asset_id") for e in distilled}
    seen_distilled = set()
    seen_other_assets = set()
    smoke_results = []
    for e in distilled:
        ex = e.get("example_keys") or []
        if not ex:
            continue
        k = ex[0]
        out = run_rag_search(keys=[k])
        hit = (e.get("asset_id") in out) or (e.get("file", "").replace(".json", "") in out)
        if hit:
            smoke_results.append(f"    {e.get('asset_id')} --key {k} ✅ 命中")
        else:
            fails.append(f"[{e.get('asset_id')}] 冒烟 --key {k} 未命中（输出未含该资产）")
            smoke_results.append(f"    {e.get('asset_id')} --key {k} ❌ 未命中")

    for t in fusion_terms:
        out = run_rag_search(terms=[t])
        for aid in distilled_ids:
            if aid in out:
                seen_distilled.add(aid)
        # 其它资产（出现在 (assetXX / 或 文件: assetXX_*.json）
        for m in re.finditer(r"asset\d+", out):
            tok = m.group(0)
            if tok not in distilled_ids:
                seen_other_assets.add(tok)
        if not args.quiet:
            infos.append(f"    融合查询「{t}」命中资产: {sorted(set(re.findall(r'asset\d+', out)))}")

    if len(seen_distilled) < len(distilled_ids):
        fails.append(f"[融合] 仅 {len(seen_distilled)}/{len(distilled_ids)} 蒸馏资产被关键词命中: {sorted(seen_distilled)}")
    if not seen_other_assets:
        fails.append("[融合] 关键词未命中任何「既有（非蒸馏）」资产，跨书融合未证实")
    else:
        infos.append(f"[融合] 蒸馏资产命中 {len(seen_distilled)}/{len(distilled_ids)}；跨书命中既有资产: {sorted(seen_other_assets)} ✅")

    # 输出
    print("=" * 60)
    print("蒸馏研读框架 RAG 整合回归/一致性检查")
    print("=" * 60)
    for i in infos:
        print(i)
    print("-" * 60)
    for s in smoke_results:
        print(s)
    print("-" * 60)
    if fails:
        print("❌ FAIL:")
        for f in fails:
            print("   " + f)
        print(f"\n总计: {len(fails)} 项失败。")
        return 1
    else:
        print("✅ 全部检查通过（蒸馏资产整合一致，跨书融合正常）。")
        return 0


if __name__ == "__main__":
    sys.exit(main())
