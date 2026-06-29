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
"""

# -*- coding: utf-8 -*-
import json
import os
import sys
import io
import time
from collections import Counter, defaultdict
from datetime import datetime, date

# Windows 终端默认编码可能不是 UTF-8，强制设置 stdout/stderr 编码
if sys.platform == 'win32' and sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    except (AttributeError, io.UnsupportedOperation):
        pass


EVOLVE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "self-evolve")
LOG_DIR = os.path.join(EVOLVE_DIR, "logs")
STATS_DIR = os.path.join(EVOLVE_DIR, "stats")
FEEDBACK_DIR = os.path.join(EVOLVE_DIR, "feedback")
MISS_DIR = os.path.join(EVOLVE_DIR, "misses")
REPORT_DIR = os.path.join(EVOLVE_DIR, "reports")

for d in [EVOLVE_DIR, LOG_DIR, STATS_DIR, FEEDBACK_DIR, MISS_DIR, REPORT_DIR]:
    os.makedirs(d, exist_ok=True)


# ── 日志记录 ───────────────────────────────────────────

def log_usage(input_date: str, rag_keys: list[str], source: str = "cli"):
    """记录一次推算使用日志。"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "input_date": input_date,
        "rag_keys": rag_keys,
        "source": source,
    }
    log_file = os.path.join(LOG_DIR, f"{date.today().isoformat()}.jsonl")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def log_miss(query_key: str, context: str = ""):
    """记录一次 RAG 未命中（知识盲区）。"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "missed_key": query_key,
        "context": context,
    }
    miss_file = os.path.join(MISS_DIR, f"{date.today().isoformat()}_misses.jsonl")
    with open(miss_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def log_feedback(session_id: str, rating: int, comment: str = ""):
    """记录用户反馈。"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "rating": rating,
        "comment": comment,
    }
    fb_file = os.path.join(FEEDBACK_DIR, f"{date.today().isoformat()}_feedback.jsonl")
    with open(fb_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


# ── 统计分析 ───────────────────────────────────────────

def load_jsonl_lines(directory: str) -> list[dict]:
    """加载目录下所有 JSONL 文件的内容。"""
    entries = []
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
                    entries.append(json.loads(line))
    return entries


def stats_top_keys(top_n: int = 10) -> list[tuple[str, int]]:
    """统计最常查询的 rag_key 排名。"""
    logs = load_jsonl_lines(LOG_DIR)
    key_counter = Counter()
    for log_entry in logs:
        for key in log_entry.get("rag_keys", []):
            key_counter[key] += 1
    return key_counter.most_common(top_n)


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


def stats_low_coverage() -> list[str]:
    """检测哪些现有 RAG asset 的条目未被查询过。"""
    logs = load_jsonl_lines(LOG_DIR)
    queried_keys = set()
    for log_entry in logs:
        queried_keys.update(log_entry.get("rag_keys", []))

    # 扫描 rag-knowledge-base 下的所有 asset JSON
    rag_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rag-knowledge-base")
    all_keys = set()
    if os.path.exists(rag_dir):
        for fname in os.listdir(rag_dir):
            if fname.endswith(".json"):
                fpath = os.path.join(rag_dir, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        for entry in data.get("entries", []):
                            for key_field in ["rag_key", "code", "sitian_key", "zaiquan_key", "key"]:
                                if key_field in entry and entry[key_field]:
                                    all_keys.add(entry[key_field])
                    except:
                        pass

    low_coverage = all_keys - queried_keys
    return sorted(low_coverage)


# ── 报告生成 ───────────────────────────────────────────

def generate_report() -> str:
    """生成自进化报告。"""
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

    # 优化建议
    lines.append("## 优化建议")
    suggestions = []
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

    # stats
    stat_p = subparsers.add_parser("stats", help="统计分析")
    stat_p.add_argument("--type", choices=["top_keys", "daily", "blind_spots", "feedback", "low_coverage"],
                        default="top_keys")

    # analyze
    an_p = subparsers.add_parser("analyze", help="分析")
    an_p.add_argument("--type", choices=["blind_spots", "coverage_gaps"], default="blind_spots")

    # feedback
    fb_p = subparsers.add_parser("feedback", help="记录反馈")
    fb_p.add_argument("--session-id", "-s", required=True)
    fb_p.add_argument("--rating", "-r", type=int, required=True)
    fb_p.add_argument("--comment", "-c", default="")

    # report
    subparsers.add_parser("report", help="生成优化报告")

    # monthly-report
    subparsers.add_parser("monthly-report", help="生成月度自进化汇总报告")

    args = parser.parse_args()

    if args.command == "log":
        keys = [k.strip() for k in args.rag_keys.split(",")]
        result = log_usage(args.input, keys, args.source)
        print(f"已记录: {json.dumps(result, ensure_ascii=False)}")

    elif args.command == "stats":
        if args.type == "top_keys":
            for key, count in stats_top_keys():
                print(f"{key:40s} {count}次")
        elif args.type == "daily":
            for d in stats_daily_usage():
                print(f"{d['date']}: {d['count']}次")
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
        result = log_feedback(args.session_id, args.rating, args.comment)
        print(f"反馈已记录: {json.dumps(result, ensure_ascii=False)}")

    elif args.command == "report":
        report = generate_report()
        print(report)

    elif args.command == "monthly-report":
        report = generate_monthly_report()
        print(report)


if __name__ == "__main__":
    main()
