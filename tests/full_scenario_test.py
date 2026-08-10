#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全流程全场景测试 —— 模拟真实用户使用五运六气技能包的各种场景。
覆盖：日期推算、年度报告、医案检索与白话呈现、个人体质、思想地图、
学习会话、导出、健康检查、RAG 精确/语义检索、综合联动。
"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
PY = sys.executable

PASS = 0
FAIL = 0
FAILED_CASES = []


def run(args, timeout=120):
    """运行命令，返回 (returncode, stdout, stderr)。"""
    r = subprocess.run([PY] + args, capture_output=True, text=True,
                       encoding="utf-8", cwd=ROOT, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def check(name, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  [PASS] {name}" + (f"  {detail}" if detail else ""))
    else:
        FAIL += 1
        FAILED_CASES.append(name)
        print(f"  [FAIL] {name}  {detail}")


def section(title):
    print(f"\n{'='*60}\n{title}\n{'='*60}")


# ============================================================
section("场景一：日期运气推算（教学/自学用户）")
# 1. 基础推算
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "calc", "2026-06-29"])
check("calc 2026-06-29 非交互推算", rc == 0 and "岁运" in out, f"rc={rc}")
check("calc 输出含司天在泉", "司天" in out and "在泉" in out)
# 2. JSON 输出结构化
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "calc", "2026-06-29", "--json"])
try:
    d = json.loads(out)
    check("calc --json 可解析", True)
    check("calc --json 含 rag_keys", "rag_keys" in d and "suiyun" in d["rag_keys"])
    check("calc --json 干支正确(丙午)", d.get("year_gz") == "丙午", d.get("year_gz"))
except Exception as e:
    check("calc --json 可解析", False, str(e))
# 3. 仅年份（无日期）
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "calc", "2026"])
check("calc 仅年份 2026", rc == 0 and "丙午" in out, f"rc={rc}")


section("场景二：年度综合报告（实践用户）")
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "report", "2026", "--audience", "practitioner", "--json"])
try:
    d = json.loads(out)
    check("report 2026 practitioner --json 可解析", True)
    check("report 含运气概述", "ganzhi" in d and "dayun" in d and "sitian" in d, f"ganzhi={d.get('ganzhi')}")
except Exception as e:
    check("report --json 可解析", False, str(e))
    check("report 文本输出", rc == 0, f"rc={rc}")


section("场景三：医案检索与白话呈现（查证用户）")
# 4. 按病证检索回春录医案
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "霍乱", "--asset", "asset18", "--json"])
try:
    d = json.loads(out)
    hits = d.get("hits", [])
    check("search 霍乱 asset18 命中", len(hits) >= 1, f"{len(hits)}条")
    if hits:
        h = hits[0]
        check("医案含白话字段", "title" in h and "preview" in h)
except Exception as e:
    check("search 霍乱 可解析", False, str(e))
# 5. 按运气格局精确检索岁图医案
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "--key", "water_excess", "--asset", "asset9", "--json"])
try:
    d = json.loads(out)
    check("search --key water_excess asset9 命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search --key water_excess", False, str(e))
# 6. 按日期综合召回（端到端）
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "--date", "2026-06-29", "--json"])
try:
    d = json.loads(out)
    check("search --date 综合召回", "hits_by_role" in d, f'roles={list(d.get("hits_by_role", {}).keys())[:4]}')
except Exception as e:
    check("search --date 综合召回", False, str(e))
# 7. 语义检索（自然口语）
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "--semantic", "心火偏旺", "--limit", "3", "--json"])
try:
    d = json.loads(out)
    check("语义检索 心火偏旺", "hits" in d, f'{len(d.get("hits", []))}条')
except Exception as e:
    check("语义检索", False, str(e))
# 7b. asset19 张聿青医案病证检索
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "湿温", "--asset", "asset19", "--json"])
try:
    d = json.loads(out)
    check("search 湿温 asset19 命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search 湿温 asset19", False, str(e))
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "--key", "zyq_020", "--asset", "asset19", "--json"])
try:
    d = json.loads(out)
    check("search --key zyq_020 asset19 精确命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search --key zyq_020", False, str(e))
# 7d. asset20 吴鞠通 + asset21 寓意草
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "风温", "--asset", "asset20", "--json"])
try:
    d = json.loads(out)
    check("search 风温 asset20 命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search 风温 asset20", False, str(e))
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "痢疾", "--asset", "asset21", "--json"])
try:
    d = json.loads(out)
    check("search 痢疾 asset21 命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search 痢疾 asset21", False, str(e))
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "--key", "yyc_001", "--asset", "asset21", "--json"])
try:
    d = json.loads(out)
    check("search --key yyc_001 asset21 精确命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search --key yyc_001", False, str(e))
# 7e. asset22 洄溪医案
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "伤寒", "--asset", "asset22", "--json"])
try:
    d = json.loads(out)
    check("search 伤寒 asset22 命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search 伤寒 asset22", False, str(e))
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "--key", "hx_001", "--asset", "asset22", "--json"])
try:
    d = json.loads(out)
    check("search --key hx_001 asset22 精确命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search --key hx_001", False, str(e))
# 7f. asset23 花韵楼医案（妇科）
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "崩漏", "--asset", "asset23", "--json"])
try:
    d = json.loads(out)
    check("search 崩漏 asset23 命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search 崩漏 asset23", False, str(e))
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "--key", "hyl_001", "--asset", "asset23", "--json"])
try:
    d = json.loads(out)
    check("search --key hyl_001 asset23 精确命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search --key hyl_001", False, str(e))
# 7g. asset24 诊余举隅录
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "霍乱", "--asset", "asset24", "--json"])
try:
    d = json.loads(out)
    check("search 霍乱 asset24 命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search 霍乱 asset24", False, str(e))
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "--key", "zj_001", "--asset", "asset24", "--json"])
try:
    d = json.loads(out)
    check("search --key zj_001 asset24 精确命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search --key zj_001", False, str(e))
# 7h. asset25 许氏医案
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "伤寒", "--asset", "asset25", "--json"])
try:
    d = json.loads(out)
    check("search 伤寒 asset25 命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search 伤寒 asset25", False, str(e))
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "--key", "xs_001", "--asset", "asset25", "--json"])
try:
    d = json.loads(out)
    check("search --key xs_001 asset25 精确命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search --key xs_001", False, str(e))
# 7i. asset26 杏轩医案
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "产后", "--asset", "asset26", "--json"])
try:
    d = json.loads(out)
    check("search 产后 asset26 命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search 产后 asset26", False, str(e))
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "--key", "xx_001", "--asset", "asset26", "--json"])
try:
    d = json.loads(out)
    check("search --key xx_001 asset26 精确命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search --key xx_001", False, str(e))
# 7j. asset27 孙文垣医案
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "便血", "--asset", "asset27", "--json"])
try:
    d = json.loads(out)
    check("search 便血 asset27 命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search 便血 asset27", False, str(e))
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "--key", "swy_001", "--asset", "asset27", "--json"])
try:
    d = json.loads(out)
    check("search --key swy_001 asset27 精确命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search --key swy_001", False, str(e))
# 7k. asset28 丛桂草堂医案
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "痰饮", "--asset", "asset28", "--json"])
try:
    d = json.loads(out)
    check("search 痰饮 asset28 命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search 痰饮 asset28", False, str(e))
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "--key", "cg_001", "--asset", "asset28", "--json"])
try:
    d = json.loads(out)
    check("search --key cg_001 asset28 精确命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search --key cg_001", False, str(e))
# 7l. asset29 外科正宗·外用医案
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "脱疽", "--asset", "asset29", "--json"])
try:
    d = json.loads(out)
    check("search 脱疽 asset29 命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search 脱疽 asset29", False, str(e))
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "--key", "wk_001", "--asset", "asset29", "--json"])
try:
    d = json.loads(out)
    check("search --key wk_001 asset29 精确命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search --key wk_001", False, str(e))
# 7m. asset30 立斋外科发挥·内外联动
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "痈疽", "--asset", "asset30", "--json"])
try:
    d = json.loads(out)
    check("search 痈疽 asset30 命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search 痈疽 asset30", False, str(e))
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "--key", "qi_blood_deficiency", "--asset", "asset30", "--json"])
try:
    d = json.loads(out)
    check("search --key qi_blood_deficiency asset30 内因联动命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search --key qi_blood_deficiency", False, str(e))
# 7n. asset31 醉花窗医案
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "中风", "--asset", "asset31", "--json"])
try:
    d = json.loads(out)
    check("search 中风 asset31 命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search 中风 asset31", False, str(e))
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "--key", "zhc_001", "--asset", "asset31", "--json"])
try:
    d = json.loads(out)
    check("search --key zhc_001 asset31 精确命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search --key zhc_001", False, str(e))
# 7o. asset32 医验随笔
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "温病", "--asset", "asset32", "--json"])
try:
    d = json.loads(out)
    check("search 温病 asset32 命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search 温病 asset32", False, str(e))
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "--key", "ysb_001", "--asset", "asset32", "--json"])
try:
    d = json.loads(out)
    check("search --key ysb_001 asset32 精确命中", d.get("count", 0) >= 1, f'{d.get("count")}条')
except Exception as e:
    check("search --key ysb_001", False, str(e))
# 7c. 医案白话转述模拟（模拟 agent 将文言医案转成大白话）
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "search", "霍乱", "--asset", "asset18", "--json"])
try:
    d = json.loads(out)
    hits = d.get("hits", [])
    if hits:
        h = hits[0]
        # 白话转述检测：preview 应含可读的病机描述
        preview = h.get("preview", "")
        has_plain = any(k in preview for k in ("暑湿", "气机", "转筋", "霍乱", "辨证", "治法"))
        check("医案 preview 可作白话转述素材", has_plain, preview[:40])
except Exception as e:
    check("医案白话转述素材", False, str(e))


section("场景四：个人运气体质（体质咨询用户）")
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "profile", "2003-04-19", "杭州", "--json"])
try:
    d = json.loads(out)
    check("profile 2003-04-19 杭州 可解析", True)
    check("profile 含体质信息", "birth_constitutions" in d or "constitution_assessment" in d, f'keys={list(d.keys())[:6]}')
except Exception as e:
    check("profile 可解析", False, str(e))


section("场景五：思想地图与学习（学习用户）")
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "map", "2026", "--format", "concept", "--json"])
check("map 2026 概念地图", rc == 0, f"rc={rc}")
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "learn", "2026", "--concept", "司天在泉", "--json"])
check("learn 司天在泉 学习会话", rc == 0, f"rc={rc}")


section("场景六：导出（内容创作者用户）")
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "export", "2026", "--format", "summary"])
check("export summary", rc == 0, f"rc={rc}")
gen_dir = os.path.join(ROOT, "reports", "generated")
thought_files = [f for f in os.listdir(gen_dir) if f.startswith("thought_") and "2026" in f] if os.path.isdir(gen_dir) else []
check("export 生成思想摘要文件", len(thought_files) >= 1, f"{thought_files[:3]}")


section("场景七：环境健康检查")
rc, out, err = run([os.path.join("scripts", "yunqi_cli.py"), "doctor"])
check("doctor 健康检查", rc == 0, f"rc={rc}")


section("场景八：完整演示链路")
rc, out, err = run([os.path.join("scripts", "demo_full_chain.py"), "2026-06-29"])
check("demo_full_chain 完整链路", rc == 0, f"rc={rc}")


section("场景九：天气+体质+运气三维（高级用户）")
rc, out, err = run([os.path.join("scripts", "yunqi_weather_constitution.py"), "2026-06-29",
                    "--birth-date", "2003-04-19", "--city", "杭州", "--mock", "--json"])
try:
    d = json.loads(out)
    check("天气×体质×运气 三维综合", True)
except Exception as e:
    check("天气×体质×运气 三维综合", False, str(e) + out[:200])


section("场景十：高级对齐综合")
rc, out, err = run([os.path.join("scripts", "advanced_alignment.py"), "--date", "2026-06-29",
                    "--birth-date", "2003-04-19", "--city", "杭州", "--constitution-demo", "--mock", "--json"])
try:
    d = json.loads(out)
    check("advanced_alignment 高级对齐", True)
except Exception as e:
    check("advanced_alignment 高级对齐", False, str(e) + out[:200])


# ============================================================
print(f"\n{'='*60}")
print(f"全流程全场景测试完成: PASS={PASS}  FAIL={FAIL}")
if FAILED_CASES:
    print(f"失败用例: {FAILED_CASES}")
print(f"{'='*60}")
sys.exit(1 if FAIL else 0)