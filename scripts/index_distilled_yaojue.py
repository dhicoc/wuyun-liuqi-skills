#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
index_distilled_yaojue.py — 把《医宗金鉴·运气要诀》（清·吴谦）蒸馏稿索引进项目 RAG。

作用：
  1. 将 rag-knowledge-base/distilled/yizong-jinjian-yunqi-yaojue/ 下的蒸馏 skill
     抽取为结构化检索资产 asset35_yizong_jinjian_yunqi_yaojue.json（统一入口）。
  2. 在 rag-knowledge-base/index.json 注册该资产 entry（含 lookup_fields / example_keys / rag_key）。
  3. 打印下一步：需手动在 scripts/rag_search.py 的 ASSET_FILES 字典 + _default_asset_keys()
     白名单加 asset35 映射（脚本不改动源码）。

设计说明：
  - 蒸馏稿已是结构化 markdown，首版直接内嵌「已知抽取事实」生成资产，避免再解析 markdown 出错。
  - 安全：资产内每条 entry 均带 disclaimer（禁止据以开方），与蒸馏 skill 三件套一致。
  - 与 asset34（王旭高《运气证治歌诀》）并列：王旭高重「方」，本书重「运气推算全框架」。

用法（从仓库根执行）：
  python scripts/index_distilled_yaojue.py
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAG_DIR = os.path.join(REPO_ROOT, "rag-knowledge-base")
DISTILL_SLUG = "yizong-jinjian-yunqi-yaojue"
ASSET_ID = "asset35_yizong_jinjian_yunqi_yaojue"
ASSET_FILE = f"{ASSET_ID}.json"

DISCLAIMER = "⚠️ 仅供中医运气学文献研读与学术框架整理，禁止据此自行诊断、开方或用药；临床须咨询执业中医师。"

# ---------------------------------------------------------------------------
# 内嵌抽取事实（源自蒸馏稿 cheatsheet.md / patterns.md / chapters，已校核源文献）
# ---------------------------------------------------------------------------
TIANGAN = [
    {"gan": "甲", "yun": "阳土", "taishao": "太", "zangfu": "胃"},
    {"gan": "己", "yun": "阴土", "taishao": "少", "zangfu": "脾"},
    {"gan": "乙", "yun": "阴金", "taishao": "少", "zangfu": "肺"},
    {"gan": "庚", "yun": "阳金", "taishao": "太", "zangfu": "大肠"},
    {"gan": "丙", "yun": "阳水", "taishao": "太", "zangfu": "膀胱"},
    {"gan": "辛", "yun": "阴水", "taishao": "少", "zangfu": "肾"},
    {"gan": "丁", "yun": "阴木", "taishao": "少", "zangfu": "肝"},
    {"gan": "壬", "yun": "阳木", "taishao": "太", "zangfu": "胆"},
    {"gan": "戊", "yun": "阳火", "taishao": "太", "zangfu": "小肠"},
    {"gan": "癸", "yun": "阴火", "taishao": "少", "zangfu": "心"},
    {"gan": "相火属阳", "yun": "—", "taishao": "—", "zangfu": "三焦"},
    {"gan": "相火属阴", "yun": "—", "taishao": "—", "zangfu": "包络（心包络）"},
]

DIZHI = [
    {"zhi": "子、午", "liuqi": "少阴君火", "zangfu": "心、小肠", "sitian": "少阴君火", "zaiquan": "阳明燥金"},
    {"zhi": "丑、未", "liuqi": "太阴湿土", "zangfu": "脾、胃", "sitian": "太阴湿土", "zaiquan": "太阳寒水"},
    {"zhi": "寅、申", "liuqi": "少阳相火", "zangfu": "三焦、包络", "sitian": "少阳相火", "zaiquan": "厥阴风木"},
    {"zhi": "卯、酉", "liuqi": "阳明燥金", "zangfu": "肺、大肠", "sitian": "阳明燥金", "zaiquan": "少阴君火"},
    {"zhi": "辰、戌", "liuqi": "太阳寒水", "zangfu": "膀胱、肾", "sitian": "太阳寒水", "zaiquan": "太阴湿土"},
    {"zhi": "巳、亥", "liuqi": "厥阴风木", "zangfu": "肝、胆", "sitian": "厥阴风木", "zaiquan": "少阳相火"},
]

TIANFU = {
    "天符(中运同司天)": {"years": "丁巳丁亥(木)、戊子戊午戊寅戊申(火)、己丑己未(土)、乙卯乙酉(金)、丙辰丙戌(水)", "count": 12},
    "岁会(本运临本支)": {"years": "四正：丁卯、戊午、乙酉、丙子；四维：甲辰、甲戌、己丑、己未", "count": 8},
    "太乙天符(天符∩岁会)": {"years": "己丑、己未、乙酉、戊午", "count": 4},
    "同天符(阳年·在泉同中运)": {"years": "壬寅、壬申(木)、甲辰、甲戌(土)、庚子、庚午(金)", "count": 6},
    "同岁会(阴年·在泉同中运)": {"years": "辛丑、辛未(水)、癸卯、癸酉、癸巳、癸亥(火)", "count": 6},
    "南北政": {"years": "甲己一运南政年(12年)；余乙庚丙辛丁壬戊癸四运俱北政(48年)", "count": 60},
    "合计": {"years": "六十年中符会合计只得 28 年（太乙4含于天符12；岁会8中有4含于天符）", "count": 28},
}

WEIBING = [
    {"gui_shu": "诸风掉眩、暴强直", "zang": "肝木"},
    {"gui_shu": "诸痛痒疮、诸热", "zang": "心火"},
    {"gui_shu": "诸湿肿满、霍乱积饮", "zang": "脾土"},
    {"gui_shu": "诸气膹郁痿、诸燥", "zang": "肺金"},
    {"gui_shu": "诸寒收引、厥逆症瘕", "zang": "肾水"},
]
WEIBING_TAIGUO = [
    {"taiguo": "木太过（六壬）", "shou_xie": "脾土"},
    {"taiguo": "火太过（六戊）", "shou_xie": "肺金"},
    {"taiguo": "土太过（六甲）", "shou_xie": "肾水"},
    {"taiguo": "金太过（六庚）", "shou_xie": "肝木"},
    {"taiguo": "水太过（六丙）", "shou_xie": "心火"},
]

ZHINAN = {
    "主气六位(固定)": "初厥阴风木→二少阴君火→三少阳相火→四太阴湿土→五阳明燥金→六太阳寒水",
    "主运五位": "初木(风/春)→二火(暑/夏)→三土(湿/长夏)→四金(燥/秋)→五水(寒/冬)",
    "正化(令有余)": "寅、午、未、酉、戌、亥",
    "对化(令不足)": "子、丑、卯、辰、巳、申",
    "五运平气名": "木敷和、火升明、土备化、金审平、水静顺",
    "五运太过名(阳年)": "木发生、火赫曦、土敦阜、水流衍、金坚成",
    "五运不及名(阴年)": "木委和、火伏明、土卑监、金从革、水涸流",
}


def build_entries():
    return [
        {
            "entry_id": "yaojue_tiangan",
            "rag_key": "yaojue_tiangan",
            "category": "tiangan_zangfu",
            "name": "天干 → 化运 / 太少 / 合人脏腑",
            "summary": "五运化合（甲己土、乙庚金、丙辛水、丁壬木、戊癸火）+ 太少（阳干五太、阴干五少）+ 天干配脏腑。全书最有复用价值的映射。",
            "mapping": TIANGAN,
            "source_quote": "distilled/yizong-jinjian-yunqi-yaojue/cheatsheet.md#表1 ; chapters/ch05-zangfu.md ; 源文献 280-298 行",
            "disclaimer": DISCLAIMER,
        },
        {
            "entry_id": "yaojue_dizhi",
            "rag_key": "yaojue_dizhi",
            "category": "dizhi_sitian_zaiquan",
            "name": "地支 → 六气 / 脏腑 / 司天在泉（客气）",
            "summary": "十二支年 → 主六气 → 合人脏腑 → 司天/在泉。推算落点与客气六步的关键。",
            "mapping": DIZHI,
            "source_quote": "distilled/yizong-jinjian-yunqi-yaojue/cheatsheet.md#表2 ; chapters/ch04-liuqi.md ; chapters/ch05-zangfu.md ; 源文献 288-298,424-447 行",
            "disclaimer": DISCLAIMER,
        },
        {
            "entry_id": "yaojue_tianfu",
            "rag_key": "yaojue_tianfu",
            "category": "tianfu_suihui_nanbei",
            "name": "天符 / 岁会 / 太乙天符 / 同天符 / 同岁会 / 南北政",
            "summary": "运气格局符会判定（年份枚举）+ 南北政（甲己南政，余北政）。合计六十年符会 28 年。",
            "mapping": [{"name": k, "years": v["years"], "count": v["count"]} for k, v in TIANFU.items()],
            "source_quote": "distilled/yizong-jinjian-yunqi-yaojue/cheatsheet.md#表5 ; chapters/ch06-tianfu.md ; 源文献 625-705 行",
            "disclaimer": DISCLAIMER,
        },
        {
            "entry_id": "yaojue_weibing",
            "rag_key": "yaojue_weibing",
            "category": "yunqi_weibing",
            "name": "运气为病五藏归属 + 岁运太过受邪脏",
            "summary": "运气为病歌五藏归属（风掉眩肝、痛痒疮心、湿肿满脾、气膹郁痿肺、寒收引肾）+ 岁运太过→受邪脏（名异情同，统归五脏）。",
            "mapping": WEIBING + [{"gui_shu": t["taiguo"] + "→受邪", "zang": t["shou_xie"]} for t in WEIBING_TAIGUO],
            "source_quote": "distilled/yizong-jinjian-yunqi-yaojue/cheatsheet.md#表8 ; chapters/ch07-yunqi-weibing.md ; 源文献 965-1106 行",
            "disclaimer": DISCLAIMER,
        },
        {
            "entry_id": "yaojue_zhinan",
            "rag_key": "yaojue_zhinan",
            "category": "tuisuan_zhinan",
            "name": "运气推算指南（主气六位 / 主运五位 / 正化对化 / 五运平气太过不及名）",
            "summary": "推算工具链速记：主气六位、主运五位、正化对化地支、五运平气/太过/不及十（五）名。",
            "mapping": [{"item": k, "value": v} for k, v in ZHINAN.items()],
            "source_quote": "distilled/yizong-jinjian-yunqi-yaojue/cheatsheet.md#表3,#表4,#表7 ; chapters/ch03-wuyun.md ; chapters/ch04-liuqi.md ; 源文献 320-379,503-535,732-749 行",
            "disclaimer": DISCLAIMER,
        },
    ]


def write_asset():
    asset = {
        "asset_id": ASSET_ID,
        "asset_name": "医宗金鉴·运气要诀（清·吴谦）蒸馏研读框架",
        "asset_description": (
            "从《医宗金鉴》卷三十五「编辑运气要诀」（清·吴谦等编纂，奉敕编，源出《内经》运气要语）"
            "经 book-to-skill 风格蒸馏出的单书研读框架：太极阴阳、五行生克、五运六气、脏腑经络映射、"
            "天符岁会南北政、运气为病。重「运气推算全框架」——基本不载方剂，与王旭高《运气证治歌诀》"
            "（重方）互补：本书讲「推算框架广度」，王旭高讲「证治用方」。"
        ),
        "data_source": "清·吴谦等《医宗金鉴》卷三十五 编辑运气要诀（源出《内经》运气七篇）",
        "entries": build_entries(),
        "disclaimer": DISCLAIMER,
    }
    out = os.path.join(RAG_DIR, ASSET_FILE)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(asset, f, ensure_ascii=False, indent=2)
    return out


def register_index():
    idx_path = os.path.join(RAG_DIR, "index.json")
    with open(idx_path, encoding="utf-8") as f:
        index = json.load(f)
    index["entries"] = [e for e in index["entries"] if e.get("asset_id") != ASSET_ID]
    index["entries"].append({
        "entry_id": f"rag_index_{ASSET_ID}",
        "entry_type": "asset_index",
        "title": "医宗金鉴·运气要诀（清·吴谦）蒸馏框架",
        "file": ASSET_FILE,
        "asset_id": ASSET_ID,
        "asset_name": "医宗金鉴·运气要诀（清·吴谦）蒸馏研读框架",
        "asset_category": "distilled_study",
        "description": "从《医宗金鉴·运气要诀》蒸馏出的单书研读框架：太极阴阳、五行、五运六气、脏腑映射、天符岁会南北政、运气为病。与王旭高《运气证治歌诀》(asset34) 互补。",
        "total_entries": len(build_entries()),
        "lookup_fields": ["rag_key"],
        "example_keys": ["yaojue_tiangan", "yaojue_dizhi", "yaojue_tianfu", "yaojue_weibing", "yaojue_zhinan"],
        "rag_key": ASSET_ID,
    })
    index["total_entries"] = index.get("total_entries", 0) + 1
    with open(idx_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    return idx_path


def main():
    try:
        asset_out = write_asset()
        idx_out = register_index()
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1
    print(f"[OK] 生成资产: {asset_out}")
    print(f"[OK] 注册索引: {idx_out} (total_assets={json.load(open(idx_out, encoding='utf-8')).get('total_entries')})")
    print("[NEXT] 还需手动在 scripts/rag_search.py 做两处改动：")
    print("  1) ASSET_FILES 字典加：")
    print(f'     "asset35": "{ASSET_FILE}",')
    print(f'     "asset35_yizong_jinjian_yunqi_yaojue": "{ASSET_FILE}",')
    print(f'     "yizong_jinjian_yunqi_yaojue": "{ASSET_FILE}",')
    print(f'     "yaojue": "{ASSET_FILE}",')
    print(f'     "yunqi_yaojue": "{ASSET_FILE}",')
    print("  2) _default_asset_keys() 白名单元组加：")
    print('     "asset35",')
    print("然后即可：python scripts/rag_search.py --key yaojue_tiangan")
    return 0


if __name__ == "__main__":
    sys.exit(main())
