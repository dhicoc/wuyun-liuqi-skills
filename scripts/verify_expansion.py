#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""端到端验证 + 大寒边界回归测试"""
import json, subprocess, sys, os, io

# Windows 终端默认编码可能不是 UTF-8，强制设置 stdout/stderr 编码
if sys.platform == 'win32' and sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except (AttributeError, io.UnsupportedOperation):
        pass

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_PY = os.path.join(BASE, "scripts", "calculate_yunqi_api.py")
RAG_DIR = os.path.join(BASE, "rag-knowledge-base")

passed = 0
failed = 0

def check(desc, cond):
    global passed, failed
    if cond:
        print("  [OK] " + desc)
        passed += 1
    else:
        print("  [FAIL] " + desc)
        failed += 1

def run_api(date_str):
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    r = subprocess.run([sys.executable, '-X', 'utf8', API_PY, date_str, "--json"],
                       capture_output=True, cwd=os.path.dirname(API_PY), env=env)
    try:
        return json.loads(r.stdout)
    except:
        print("  STDERR: " + r.stderr.decode('utf-8', errors='replace')[:200])
        return None

# === 1. 大寒边界回归测试 ===
print("=" * 60)
print("1. 大寒边界回归测试")
print("=" * 60)

tests = {
    "2026-01-15": {"year": 2025, "gz": "乙巳", "code": "metal_deficient"},
    "2026-01-20": {"year": 2026, "gz": "丙午", "code": "water_excess"},
    "2026-06-27": {"year": 2026, "gz": "丙午", "code": "water_excess"},
}

for date_str, expected in tests.items():
    print("")
    print("  输入: " + date_str)
    d = run_api(date_str)
    if d is None:
        print("  [FAIL] API 调用失败")
        failed += 1
        continue
    check("yunqi_year=" + str(expected['year']), d.get("yunqi_year") == expected["year"])
    check("year_gz=" + expected['gz'], d.get("year_gz") == expected["gz"])
    check("sui_yun.code=" + expected['code'], d.get("sui_yun", {}).get("code") == expected["code"])
    check("day_gz 存在", bool(d.get("day_gz")))
    check("si_tian 存在", bool(d.get("si_tian")))
    check("zai_quan 存在", bool(d.get("zai_quan")))
    check("current_step.name 存在", bool(d.get("current_step", {}).get("name")))
    rk = d.get("rag_keys", {})
    check("rag_keys 含 4 个分类", len(rk) == 4 and isinstance(rk, dict))

# === 2. RAG Asset JSON 完整性 ===
print("")
print("=" * 60)
print("2. RAG Asset JSON 完整性检查")
print("=" * 60)

assets = {
    "asset1_suiyun.json": {"min_entries": 10, "keys": ["code", "name", "treatment_principle"]},
    "asset2_sitian_zaiquan.json": {"min_entries": 6, "keys": ["sitian_key", "zaiquan_key"]},
    "asset3_kezhujialin.json": {"min_entries": 36, "keys": ["key", "shun_ni"]},
    "asset4_formula.json": {"min_entries": 16, "keys": ["formula_id", "rag_key", "name", "ingredients"]},
    "asset5_commentary.json": {"min_entries": 20, "keys": ["commentary_id", "author", "core_theory_title"]},
    "asset6_regional.json": {"min_entries": 8, "keys": ["region_id", "region_name", "wuyun_modifier"]},
}

for fname, spec in assets.items():
    fpath = os.path.join(RAG_DIR, fname)
    print("")
    print("  " + fname + ":")
    if not os.path.exists(fpath):
        print("  [FAIL] 文件不存在")
        failed += 1
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except:
            print("  [FAIL] JSON 解析失败")
            failed += 1
            continue
    entries = data.get("entries", [])
    n = len(entries)
    check("条目数 >= " + str(spec['min_entries']) + " (实际: " + str(n) + ")", n >= spec['min_entries'])
    for k in spec["keys"]:
        has_key = all(k in e for e in entries)
        check("字段 '" + k + "' 全部存在", has_key)

# asset7 特殊处理（双 entry_type）
print("")
print("  asset7_constitution.json:")
fpath = os.path.join(RAG_DIR, "asset7_constitution.json")
with open(fpath, "r", encoding="utf-8") as f:
    data = json.load(f)
entries = data.get("entries", [])
check("总条目 >= 18 (实际: " + str(len(entries)) + ")", len(entries) >= 18)
birth = [e for e in entries if e.get("entry_type") == "birth_yunqi_mapping"]
adj = [e for e in entries if e.get("entry_type") == "suiyun_constitution_adjustment"]
check("birth_yunqi_mapping 9 条 (实际: " + str(len(birth)) + ")", len(birth) == 9)
check("suiyun_constitution_adjustment 9 条 (实际: " + str(len(adj)) + ")", len(adj) >= 9)
check("birth 含 constitution_name", all("constitution_name" in e for e in birth))
check("adj 含 suiyun_code+suiyun_name", all("suiyun_code" in e and "suiyun_name" in e for e in adj))

# === 3. Cross-Asset Key 关联性检查 ===
print("")
print("=" * 60)
print("3. Cross-Asset Key 关联性检查")
print("=" * 60)

# Collect all rag_keys from all assets
all_rag_keys = set()
for fname in os.listdir(RAG_DIR):
    if not fname.endswith(".json"):
        continue
    with open(os.path.join(RAG_DIR, fname), "r", encoding="utf-8") as f:
        data = json.load(f)
    for e in data.get("entries", []):
        for kf in ["rag_key", "code", "sitian_key", "zaiquan_key", "key"]:
            if kf in e and e[kf]:
                all_rag_keys.add(e[kf])

print("")
print("  RAG 知识库总唯一键数: " + str(len(all_rag_keys)))

# API rag_keys is a dict {group: specific_key}
api_d = run_api("2026-06-27")
api_rag_values = set(api_d.get("rag_keys", {}).values()) if api_d else set()
matched = api_rag_values & all_rag_keys
check("API rag_key values 可被 RAG asset 命中 (" + str(len(matched)) + "/" + str(len(api_rag_values)) + ")",
      len(matched) == len(api_rag_values) and len(api_rag_values) > 0)
print("    API values: " + str(api_rag_values))
print("    已匹配: " + str(matched))

# === 4. Self-evolve ===
print("")
print("=" * 60)
print("4. 自进化引擎启动检查")
print("=" * 60)
evolve_script = os.path.join(BASE, "scripts", "self_evolve.py")
if os.path.exists(evolve_script):
    r = subprocess.run([sys.executable, evolve_script, "log", "--input", "2026-06-27",
                       "--rag-keys", "water_excess,shaoyin_junhuo_sitian", "--source", "test"],
                       capture_output=True, cwd=os.path.dirname(evolve_script))
    out = r.stdout.decode('utf-8', errors='replace')
    check("self_evolve.py log 成功", r.returncode == 0)
    sys.stdout.write("    " + out.strip()[:80] + "\n")
    sys.stdout.flush()
else:
    print("  [WARN] 不存在，跳过")

# === 5. SKILL.md & routing.md ===
print("")
print("=" * 60)
print("5. 文档同步更新检查")
print("=" * 60)
for label, path in [("SKILL.md", os.path.join(BASE, "SKILL.md")),
                     ("routing.md", os.path.join(BASE, "routing.md"))]:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    found = any(kw in content for kw in ["asset4", "asset5", "asset6", "asset7", "self-evolve", "self_evolve", "ingest_literature"])
    check(label + " 含新增模块引用", found)

# === 6. 新增文件整体清单 ===
print("")
print("=" * 60)
print("6. 新增文件完整性清单")
print("=" * 60)
new_files = [
    "scripts/ingest_literature.py",
    "scripts/self_evolve.py",
    "scripts/verify_expansion.py",
    "scripts/health_check.py",
    "scripts/personal_yunqi_profile.py",
    "scripts/visualize_yunqi.py",
    "scripts/validate_knowledge_base.py",
    "scripts/generate_html_report.py",
    "self-evolve/README.md",
    "agent-workflow/self_evolve_hook.md",
    "prompts/onboarding_prompt.md",
    "rag-knowledge-base/asset4_formula.json",
    "rag-knowledge-base/asset5_commentary.json",
    "rag-knowledge-base/asset6_regional.json",
    "rag-knowledge-base/asset7_constitution.json",
    "rag-knowledge-base/terminology.json",
    "rag-knowledge-base/_entry_template.json",
    "rag-knowledge-base/LITERATURE_EXPANSION.md",
    "yunqi-classics/references/lingqu_jiugong_bafeng.md",
]
for rel in new_files:
    fpath = os.path.join(BASE, rel)
    exists = os.path.exists(fpath)
    sz = os.path.getsize(fpath) if exists else 0
    check(rel + " (" + str(sz) + " bytes)", exists)

# === SUMMARY ===
print("")
print("=" * 60)
print("验证结果: " + str(passed) + " 通过, " + str(failed) + " 失败")
print("=" * 60)
sys.exit(0 if failed == 0 else 1)
