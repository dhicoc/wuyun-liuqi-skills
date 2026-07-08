#!/usr/bin/env python3
"""
五运六气技能包自进化引擎 (Self-Evolution Engine)
=================================================
功能：
1. 使用日志记录（每次推算/推理的输入输出）
2. 高频病机统计（哪些病机组合被频繁查询）
3. 缺失覆盖检测（哪些 rag_key 被查询但未命中）
4. 反馈采集（用户对输出的评价）
5. 自优化建议（基于统计数据的改进建议）

用法：
  # 记录一次推算
  python scripts/self_evolve.py log --input "2026-06-27" --rag-keys water_excess,shaoyin_junhuo_sitian

  # 查看统计分析
  python scripts/self_evolve.py stats --type top_keys

  # 检测知识盲区
  python scripts/self_evolve.py analyze --type blind_spots

  # 记录用户反馈
  python scripts/self_evolve.py feedback --session-id xxx --rating 4 --comment "建议添加方药"

  # 生成优化报告
  python scripts/self_evolve.py report

  # 生成月度自进化汇总报告
  python scripts/self_evolve.py monthly-report

  # 记录规则/路由盲区（待合并进 gotchas 或 rules）
  python scripts/self_evolve.py rule-gap --category routing --description "..."
"""

# -*- coding: utf-8 -*-
import json
import os
import sys
import time
import hashlib
import re
from collections import Counter, defaultdict
from datetime import datetime, date

from _common import setup_environment
setup_environment(add_lib=False)


EVOLVE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "self-evolve")
LOG_DIR = os.path.join(EVOLVE_DIR, "logs")
STATS_DIR = os.path.join(EVOLVE_DIR, "stats")
FEEDBACK_DIR = os.path.join(EVOLVE_DIR, "feedback")
MISS_DIR = os.path.join(EVOLVE_DIR, "misses")
REPORT_DIR = os.path.join(EVOLVE_DIR, "reports")
RULE_GAP_FILE = os.path.join(EVOLVE_DIR, "rule-gaps.jsonl")

for d in [EVOLVE_DIR, LOG_DIR, STATS_DIR, FEEDBACK_DIR, MISS_DIR, REPORT_DIR]:
    os.makedirs(d, exist_ok=True)

# 隐私增强常量
_PRIVACY_SALT = "wuyun-liuqi-privacy-salt-v1"  # 固定盐，用于一致哈希
_PII_PATTERNS = [
    re.compile(r'[\w\.-]+@[\w\.-]+'),  # 邮箱
    re.compile(r'\b1[3-9]\d{9}\b'),     # 中国手机号
    re.compile(r'\b\d{15,18}\b'),       # 身份证号片段
    re.compile(r'[\u4e00-\u9fa5]{2,4}(先生|女士|老师|医生)'),  # 常见中文姓名+称呼
]

def _hash_session_id(session_id: str) -> str:
    """默认匿名化 session_id。"""
    if not session_id:
        return None
    h = hashlib.sha256((session_id + _PRIVACY_SALT).encode('utf-8')).hexdigest()
    return h[:16]  # 保留16字符用于聚合

def _sanitize_text(text: str) -> str:
    """清洗文本中的潜在 PII。"""
    if not text:
        return text
    sanitized = text
    for pattern in _PII_PATTERNS:
        sanitized = pattern.sub("[REDACTED]", sanitized)
    return sanitized


# ── 日志记录 ───────────────────────────────────────────

def log_usage(input_date: str, rag_keys: list[str], source: str = "cli", concepts: list[str] = None, session_id: str = None):
    """记录一次推算使用日志。
    concepts: 本次涉及的思想概念（如 ["天人合一", "气化", "中和"]），用于跟踪思想理解。
    session_id: 会话ID，用于追踪学习路径。
    """
    entry = {
        "timestamp": datetime.now().isoformat(),
        "input_date": input_date,
        "rag_keys": rag_keys,
        "source": source,
    }
    if concepts:
        entry["concepts"] = concepts
    if session_id:
        entry["session_id"] = _hash_session_id(session_id) if True else session_id  # 默认始终哈希
    log_file = os.path.join(LOG_DIR, f"{date.today().isoformat()}.jsonl")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def log_miss(query_key: str, context: str = "", anonymize: bool = True):
    """记录一次 RAG 未命中（知识盲区）。"""
    if anonymize:
        context = _sanitize_text(context)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "missed_key": query_key,
        "context": context,
    }
    miss_file = os.path.join(MISS_DIR, f"{date.today().isoformat()}_misses.jsonl")
    with open(miss_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def log_rule_gap(category: str, description: str, source: str = "task_closure"):
    """记录 Agent 规则/路由盲区，供月度报告与 gotchas 维护。"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "category": category,
        "description": _sanitize_text(description),
        "source": source,
        "status": "pending",
    }
    with open(RULE_GAP_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def stats_rule_gaps() -> list[dict]:
    """按 category 汇总 rule-gap。"""
    if not os.path.exists(RULE_GAP_FILE):
        return []
    counter = Counter()
    samples: dict[str, str] = {}
    with open(RULE_GAP_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            cat = entry.get("category", "unknown")
            counter[cat] += 1
            if cat not in samples:
                samples[cat] = entry.get("description", "")
    return [
        {"category": k, "count": v, "sample": samples.get(k, "")}
        for k, v in counter.most_common()
    ]


def log_feedback(session_id: str, rating: int, comment: str = "", feedback_type: str = "general", anonymize: bool = True):
    """记录用户反馈。
    feedback_type: general | understanding (教学/理解质量)
    anonymize: 是否默认匿名化（P0隐私增强）
    """
    if anonymize:
        session_id = _hash_session_id(session_id)
        comment = _sanitize_text(comment)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "rating": rating,
        "comment": comment,
        "feedback_type": feedback_type,
    }
    fb_file = os.path.join(FEEDBACK_DIR, f"{date.today().isoformat()}_feedback.jsonl")
    with open(fb_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


# ── 统计分析 ───────────────────────────────────────────

def load_jsonl_lines(directory: str, filter_test: bool = True, dedup: bool = True) -> list[dict]:
    """加载目录下所有 JSONL 文件的内容。
    filter_test: 过滤 source 为 'test' 的数据，提升数据质量。
    dedup: 简单去重（基于 timestamp + input + keys 的 hash），避免重复日志。
    """
    entries = []
    seen = set()
    if not os.path.exists(directory):
        return entries
    for fname in sorted(os.listdir(directory)):
        if not fname.endswith(".jsonl"):
            continue
        fpath = os.path.join(directory, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entry = json.loads(line)
                    if filter_test and entry.get("source") == "test":
                        continue
                    if dedup:
                        key = (entry.get("timestamp", ""), entry.get("input_date", ""), tuple(entry.get("rag_keys", [])))
                        key_hash = hash(key)
                        if key_hash in seen:
                            continue
                        seen.add(key_hash)
                    entries.append(entry)
    return entries


def stats_top_keys(top_n: int = 10) -> list[tuple[str, int]]:
    """统计最常查询的 rag_key 排名。"""
    logs = load_jsonl_lines(LOG_DIR)
    key_counter = Counter()
    for log_entry in logs:
        for key in log_entry.get("rag_keys", []):
            key_counter[key] += 1
    return key_counter.most_common(top_n)


def stats_top_concepts(top_n: int = 10) -> list[tuple[str, int]]:
    """统计最常涉及的思想概念排名（支持思想理解跟踪）。"""
    logs = load_jsonl_lines(LOG_DIR)
    concept_counter = Counter()
    for log_entry in logs:
        for c in log_entry.get("concepts", []):
            concept_counter[c] += 1
    return concept_counter.most_common(top_n)


def stats_blind_spots() -> list[dict]:
    """分析知识盲区：被查询但未命中的键。"""
    misses = load_jsonl_lines(MISS_DIR)
    miss_counter = Counter(m.get("missed_key", "unknown") for m in misses)
    return [{"key": k, "count": v} for k, v in miss_counter.most_common()]


def stats_feedback_summary() -> dict:
    """统计用户反馈汇总。"""
    feedbacks = load_jsonl_lines(FEEDBACK_DIR)
    if not feedbacks:
        return {"total": 0, "avg_rating": 0, "counts": {}}
    ratings = [f.get("rating", 0) for f in feedbacks]
    return {
        "total": len(feedbacks),
        "avg_rating": round(sum(ratings) / len(ratings), 2),
        "rating_distribution": dict(Counter(ratings)),
    }


def stats_daily_usage() -> list[dict]:
    """每日使用量趋势。"""
    logs = load_jsonl_lines(LOG_DIR)
    daily = Counter()
    for log_entry in logs:
        day = log_entry.get("timestamp", "")[:10]
        if day:
            daily[day] += 1
    return [{"date": k, "count": v} for k, v in sorted(daily.items())]


def stats_sessions() -> dict:
    """会话统计，用于学习路径分析。"""
    logs = load_jsonl_lines(LOG_DIR)
    sessions = defaultdict(list)
    for log in logs:
        sid = log.get("session_id")
        if sid:
            sessions[sid].append(log)
    return {
        "total_sessions": len(sessions),
        "avg_logs_per_session": round(sum(len(v) for v in sessions.values()) / len(sessions), 2) if sessions else 0,
        "multi_log_sessions": len([s for s in sessions.values() if len(s) > 1])
    }


def stats_concept_progression() -> list[dict]:
    """简单学习路径：按会话统计概念链和进步（P2）。"""
    logs = load_jsonl_lines(LOG_DIR)
    sessions = defaultdict(list)
    for log in logs:
        sid = log.get("session_id") or log.get("timestamp")[:16]  # fallback
        sessions[sid].append(log)
    progress = []
    for sid, entries in sessions.items():
        concepts = []
        for e in entries:
            concepts.extend(e.get("concepts", []))
        unique = list(dict.fromkeys(concepts))  # preserve order
        if len(unique) > 1:
            progress.append({"session": sid, "concept_chain": unique, "depth": len(unique)})
    return sorted(progress, key=lambda x: x["depth"], reverse=True)[:5]  # top depth


def stats_low_coverage() -> list[str]:
    """检测哪些现有 RAG asset 的条目未被查询过。改进：关联概念，过滤测试数据，只返回有意义条目。"""
    logs = load_jsonl_lines(LOG_DIR, filter_test=True)
    queried_keys = set()
    queried_concepts = set()
    for log_entry in logs:
        queried_keys.update(log_entry.get("rag_keys", []))
        queried_concepts.update(log_entry.get("concepts", []))

    # 扫描 rag-knowledge-base 下的所有 asset JSON
    rag_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rag-knowledge-base")
    all_keys = set()
    if os.path.exists(rag_dir):
        for fname in os.listdir(rag_dir):
            if fname.endswith(".json") and not fname.startswith("_"):
                fpath = os.path.join(rag_dir, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        for entry in data.get("entries", []):
                            for key_field in ["rag_key", "code", "sitian_key", "zaiquan_key", "key"]:
                                val = entry.get(key_field)
                                if val and isinstance(val, str) and not val.startswith("asset"):
                                    all_keys.add(val)
                    except:
                        pass

    low_coverage = all_keys - queried_keys
    # 额外：标记与未查询概念相关的低覆盖
    low_with_concept = [k for k in low_coverage if any(c.lower() in k.lower() for c in queried_concepts)] if queried_concepts else low_coverage
    return sorted(set(low_coverage) | set(low_with_concept))[:20]  # 限制输出


# ── 隐私与数据清理 ─────────────────────────────────────

def cleanup_old_data(days: int = 90, anonymize_existing: bool = False):
    """隐私增强：清理旧数据，可选匿名化历史记录。"""
    cutoff = (date.today() - __import__('datetime').timedelta(days=days)).isoformat()
    for d in [LOG_DIR, FEEDBACK_DIR, MISS_DIR]:
        for fname in os.listdir(d):
            if fname.endswith('.jsonl') and fname[:10] < cutoff:
                fpath = os.path.join(d, fname)
                if anonymize_existing:
                    # 简单重新匿名化（生产中更复杂）
                    with open(fpath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    new_lines = []
                    for line in lines:
                        try:
                            e = json.loads(line)
                            if 'session_id' in e and e['session_id']:
                                e['session_id'] = _hash_session_id(e['session_id'])
                            if 'comment' in e:
                                e['comment'] = _sanitize_text(e.get('comment', ''))
                            if 'context' in e:
                                e['context'] = _sanitize_text(e.get('context', ''))
                            new_lines.append(json.dumps(e, ensure_ascii=False) + '\n')
                        except:
                            new_lines.append(line)
                    with open(fpath, 'w', encoding='utf-8') as f:
                        f.writelines(new_lines)
                os.remove(fpath)
                print(f"已清理: {fpath}")
    print(f"隐私清理完成（保留最近 {days} 天）")

# ── 报告生成 ───────────────────────────────────────────

def generate_report(as_json: bool = False) -> str:
    """生成自进化报告。
    as_json: 返回 JSON 便于 Agent 解析（P1）。
    """
    if as_json:
        data = {
            "generated": datetime.now().isoformat(),
            "usage_count": len(load_jsonl_lines(LOG_DIR)),
            "top_keys": stats_top_keys(5),
            "top_concepts": stats_top_concepts(5),
            "blind_spots": stats_blind_spots()[:5],
            "feedback": stats_feedback_summary(),
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    lines = []
    lines.append("# 五运六气技能包自进化报告")
    lines.append(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")

    # 使用统计
    logs = load_jsonl_lines(LOG_DIR)
    lines.append(f"## 使用概况")
    lines.append(f"- 累计推算次数: {len(logs)}")
    lines.append(f"- 累计日志天数: {len(stats_daily_usage())}")
    lines.append("")

    # 高频 rag_key
    top_keys = stats_top_keys(5)
    if top_keys:
        lines.append("## 高频查询病机 TOP5")
        for key, count in top_keys:
            lines.append(f"- `{key}`: {count} 次")
        lines.append("")

    # 高频思想概念 (针对理解思想的优化)
    top_concepts = stats_top_concepts(5)
    if top_concepts:
        lines.append("## 高频思想概念 TOP5（理解跟踪）")
        for c, count in top_concepts:
            lines.append(f"- `{c}`: {count} 次涉及")
        lines.append("")

    # 知识盲区
    blind_spots = stats_blind_spots()
    if blind_spots:
        lines.append("## 知识盲区（未命中）")
        for spot in blind_spots[:5]:
            lines.append(f"- `{spot['key']}`: {spot['count']} 次未命中")
        lines.append("")

    # 低覆盖率
    low_cov = stats_low_coverage()
    if low_cov:
        lines.append("## 低覆盖率条目（从未被查询）")
        for key in low_cov[:10]:
            lines.append(f"- `{key}`")
        lines.append("")

    # 反馈
    fb = stats_feedback_summary()
    if fb["total"] > 0:
        lines.append(f"## 用户反馈")
        lines.append(f"- 反馈总数: {fb['total']}")
        lines.append(f"- 平均评分: {fb['avg_rating']}/5")
        lines.append("")

    # 思想理解专项反馈
    all_fb = load_jsonl_lines(FEEDBACK_DIR)
    understanding_fb = [f for f in all_fb if f.get("feedback_type") == "understanding"]
    if understanding_fb:
        u_ratings = [f.get("rating", 0) for f in understanding_fb]
        lines.append("## 思想理解质量反馈（teaching/understanding）")
        lines.append(f"- 理解反馈数: {len(understanding_fb)}")
        lines.append(f"- 平均理解评分: {round(sum(u_ratings)/len(u_ratings), 2)}/5")
        lines.append("  （此维度关注解释是否帮助用户理解运气学思想，而非仅计算准确性）")
        lines.append("")

    # 优化建议 - 增强思想理解
    lines.append("## 优化建议（思想理解导向）")
    suggestions = []
    if understanding_fb and round(sum(u_ratings)/len(u_ratings), 2) < 4:
        suggestions.append("理解评分偏低：优先优化思想层解读的哲学深度和现代比喻")
    if top_concepts:
        top_c = top_concepts[0][0]
        suggestions.append(f"高频概念 `{top_c}`：考虑在 report 中增加更多历史案例和思想演进")
    prog = stats_concept_progression()
    if prog:
        suggestions.append(f"检测到学习路径：用户在探索 {prog[0]['concept_chain']}，建议补充连贯解释")
    if not suggestions:
        suggestions.append("当前思想理解数据良好，建议继续扩展概念银行")
    for s in suggestions:
        lines.append(f"- {s}")
    lines.append("")

    lines.append("---")
    lines.append("_由 self_evolve.py 自动生成_")

    report = "\n".join(lines)
    report_path = os.path.join(REPORT_DIR, f"report_{date.today().isoformat()}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"报告已生成: {report_path}")
    return report


def generate_monthly_report() -> str:
    """生成月度自进化汇总报告。"""
    today = date.today()
    month_start = today.replace(day=1)
    # 简单处理：若今天是每月1号，则生成上月报告；否则生成当月到目前为止的汇总
    report_month = month_start
    month_label = report_month.strftime("%Y-%m")

    lines = []
    lines.append(f"# 五运六气技能包月度自进化报告（{month_label}）")
    lines.append(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("> 本月度报告汇总当月使用日志、用户反馈与知识盲区，用于持续优化技能包。")
    lines.append("")

    logs = load_jsonl_lines(LOG_DIR)
    month_logs = [log for log in logs if log.get("timestamp", "").startswith(month_label)]

    lines.append("## 使用概况")
    lines.append(f"- 本月累计推算次数: {len(month_logs)}")
    daily = Counter(log.get("timestamp", "")[:10] for log in month_logs)
    lines.append(f"- 活跃天数: {len(daily)}")
    lines.append("")

    # 高频 rag_key
    key_counter = Counter()
    for log in month_logs:
        for key in log.get("rag_keys", []):
            key_counter[key] += 1
    if key_counter:
        lines.append("## 高频查询病机 TOP10")
        for key, count in key_counter.most_common(10):
            lines.append(f"- `{key}`: {count} 次")
        lines.append("")

    # 本月高频思想概念
    concept_counter = Counter()
    for log in month_logs:
        for c in log.get("concepts", []):
            concept_counter[c] += 1
    if concept_counter:
        lines.append("## 本月高频思想概念 TOP5")
        for c, count in concept_counter.most_common(5):
            lines.append(f"- `{c}`: {count} 次")
        lines.append("")

    # 知识盲区
    misses = load_jsonl_lines(MISS_DIR)
    month_misses = [m for m in misses if m.get("timestamp", "").startswith(month_label)]
    miss_counter = Counter(m.get("missed_key", "unknown") for m in month_misses)
    if miss_counter:
        lines.append("## 本月知识盲区（未命中）")
        for key, count in miss_counter.most_common(10):
            lines.append(f"- `{key}`: {count} 次")
        lines.append("")

    # 反馈
    fb = stats_feedback_summary()
    if fb["total"] > 0:
        lines.append("## 用户反馈")
        lines.append(f"- 累计反馈总数: {fb['total']}")
        lines.append(f"- 平均评分: {fb['avg_rating']}/5")
        if fb.get("rating_distribution"):
            dist = fb["rating_distribution"]
            dist_str = ", ".join(f"{k}分:{v}" for k, v in sorted(dist.items()))
            lines.append(f"- 评分分布: {dist_str}")
        lines.append("")

    # 规则盲区
    rule_gaps = stats_rule_gaps()
    if rule_gaps:
        lines.append("## 规则/路由盲区（rule-gap）")
        for g in rule_gaps[:10]:
            sample = g.get("sample", "")
            if sample and len(sample) > 60:
                sample = sample[:60] + "…"
            lines.append(f"- `{g['category']}`: {g['count']} 次 — {sample}")
        lines.append("")
        lines.append("> 待确认项请合并进 `references/gotchas.md` 或 `rules/`（见 workflows/task-closure.md）")
        lines.append("")

    # 优化建议
    lines.append("## 优化建议")
    suggestions = []
    if rule_gaps:
        top = rule_gaps[0]
        suggestions.append(
            f"规则盲区 `{top['category']}` 出现 {top['count']} 次，建议更新 gotchas/rules"
        )
    if miss_counter:
        suggestions.append(f"补充高频未命中知识：{', '.join(k for k, _ in miss_counter.most_common(5))}")
    if key_counter:
        top = key_counter.most_common(1)[0][0]
        suggestions.append(f"高频查询 `{top}` 可考虑扩展临床案例与注家观点")
    if fb["total"] > 0 and fb.get("avg_rating", 5) < 4:
        suggestions.append("平均评分偏低，建议复盘近期输出质量并优化 report 模板")
    if not suggestions:
        suggestions.append("本月数据平稳，建议继续保持并关注新增路由场景")
    for s in suggestions:
        lines.append(f"- {s}")
    lines.append("")

    lines.append("---")
    lines.append("_由 self_evolve.py 自动生成_")

    report = "\n".join(lines)
    report_path = os.path.join(REPORT_DIR, f"monthly_report_{month_label}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"月度报告已生成: {report_path}")
    return report


# ── CLI ─────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="五运六气自进化引擎")
    subparsers = parser.add_subparsers(dest="command")

    # log
    log_p = subparsers.add_parser("log", help="记录使用日志")
    log_p.add_argument("--input", "-i", required=True)
    log_p.add_argument("--rag-keys", "-k", required=True)
    log_p.add_argument("--source", "-s", default="cli")
    log_p.add_argument("--session-id", default=None, help="会话ID，用于学习路径追踪")
    log_p.add_argument("--concepts", default=None, help="逗号分隔的思想概念，用于理解追踪")

    # stats
    stat_p = subparsers.add_parser("stats", help="统计分析")
    stat_p.add_argument("--type", choices=["top_keys", "top_concepts", "daily", "sessions", "concept_progress", "blind_spots", "feedback", "low_coverage"],
                        default="top_keys")

    # analyze
    an_p = subparsers.add_parser("analyze", help="分析")
    an_p.add_argument("--type", choices=["blind_spots", "coverage_gaps"], default="blind_spots")

    # feedback
    fb_p = subparsers.add_parser("feedback", help="记录反馈")
    fb_p.add_argument("--session-id", "-s", required=True)
    fb_p.add_argument("--rating", "-r", type=int, required=True)
    fb_p.add_argument("--comment", "-c", default="")
    fb_p.add_argument("--feedback-type", "-t", default="general", choices=["general", "understanding"],
                      help="反馈类型：general（通用）或 understanding（思想理解质量）")

    # report
    rep_p = subparsers.add_parser("report", help="生成优化报告")
    rep_p.add_argument("--json", action="store_true", help="输出 JSON 便于 Agent 解析")

    # monthly-report
    subparsers.add_parser("monthly-report", help="生成月度自进化汇总报告")

    # rule-gap
    rg_p = subparsers.add_parser("rule-gap", help="记录规则/路由盲区")
    rg_p.add_argument("--category", "-c", required=True,
                      choices=["routing", "calculation", "clinical", "output", "install", "other"])
    rg_p.add_argument("--description", "-d", required=True)
    rg_p.add_argument("--source", default="task_closure")

    # privacy cleanup
    clean_p = subparsers.add_parser("cleanup", help="隐私清理旧数据")
    clean_p.add_argument("--days", type=int, default=90)
    clean_p.add_argument("--anonymize-existing", action="store_true")

    args = parser.parse_args()

    if args.command == "log":
        keys = [k.strip() for k in args.rag_keys.split(",")]
        concepts = [c.strip() for c in args.concepts.split(",")] if args.concepts else None
        result = log_usage(args.input, keys, args.source, concepts=concepts, session_id=args.session_id)
        print(f"已记录: {json.dumps(result, ensure_ascii=False)}")

    elif args.command == "stats":
        if args.type == "top_keys":
            for key, count in stats_top_keys():
                print(f"{key:40s} {count}次")
        elif args.type == "top_concepts":
            for c, count in stats_top_concepts():
                print(f"{c:40s} {count}次")
        elif args.type == "daily":
            for d in stats_daily_usage():
                print(f"{d['date']}: {d['count']}次")
        elif args.type == "sessions":
            s = stats_sessions()
            print(f"总会话数: {s['total_sessions']}")
            print(f"平均每会话日志: {s['avg_logs_per_session']}")
            print(f"多日志会话(学习路径): {s['multi_log_sessions']}")
        elif args.type == "concept_progress":
            for p in stats_concept_progression():
                print(f"{p['session']}: {p['concept_chain']} (depth {p['depth']})")
        elif args.type == "blind_spots":
            for s in stats_blind_spots():
                print(f"{s['key']:40s} {s['count']}次")
        elif args.type == "feedback":
            fb = stats_feedback_summary()
            print(f"反馈总数: {fb['total']}, 平均评分: {fb.get('avg_rating', 'N/A')}")
        elif args.type == "low_coverage":
            for key in stats_low_coverage():
                print(f"{key}")

    elif args.command == "analyze":
        if args.type == "blind_spots":
            blind_spots = stats_blind_spots()
            if blind_spots:
                print(f"发现 {len(blind_spots)} 个知识盲区:")
                for s in blind_spots:
                    print(f"  - {s['key']} ({s['count']}次)")
                print("\n建议: 将这些键对应的知识补充到对应 RAG asset 中")
            else:
                print("暂未发现知识盲区")
        elif args.type == "coverage_gaps":
            low = stats_low_coverage()
            print(f"低覆盖条目: {len(low)} 个从未被查询")
            for key in low[:10]:
                print(f"  - {key}")

    elif args.command == "feedback":
        result = log_feedback(args.session_id, args.rating, args.comment, args.feedback_type)
        print(f"反馈已记录: {json.dumps(result, ensure_ascii=False)}")

    elif args.command == "report":
        report = generate_report(as_json=args.json)
        print(report)

    elif args.command == "monthly-report":
        report = generate_monthly_report()
        print(report)

    elif args.command == "rule-gap":
        result = log_rule_gap(args.category, args.description, args.source)
        print(f"规则盲区已记录: {json.dumps(result, ensure_ascii=False)}")

    elif args.command == "cleanup":
        cleanup_old_data(days=getattr(args, 'days', 90), anonymize_existing=getattr(args, 'anonymize_existing', False))


if __name__ == "__main__":
    main()
