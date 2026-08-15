#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
index_distilled.py — 把 book-to-skill 风格蒸馏出的「单书研读框架」索引进项目 RAG。

作用：
  1. 将 rag-knowledge-base/distilled/<slug>/ 下的蒸馏 skill（SKILL.md/cheatsheet/patterns/chapters）
     抽取为结构化检索资产 asset34_yunqi_zhengzhi_gejue.json（首版 <slug> 固定为 yunqi-zhengzhi-gejue）。
  2. 在 rag-knowledge-base/index.json 注册该资产 entry（含 lookup_fields / example_keys / rag_key）。
  3. 打印下一步：需手动在 scripts/rag_search.py 的 ASSET_FILES 字典加 asset34 映射（脚本不改动源码）。

设计说明：
  - 蒸馏稿已是结构化 markdown，首版直接内嵌「已知抽取事实」生成资产，避免再解析 markdown 出错。
  - 未来换书：改 DISTILL_SLUG + 内嵌数据即可复用；也可扩展为解析 cheatsheet.md 自动抽取。
  - 安全：资产内每条 entry 均带 disclaimer（禁止据以开方），与蒸馏 skill 三件套一致。

用法（从仓库根执行）：
  python scripts/index_distilled.py
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAG_DIR = os.path.join(REPO_ROOT, "rag-knowledge-base")
DISTILL_SLUG = "yunqi-zhengzhi-gejue"
ASSET_ID = "asset34_yunqi_zhengzhi_gejue"
ASSET_FILE = f"{ASSET_ID}.json"

DISCLAIMER = "⚠️ 仅供中医运气学文献研读与学术框架整理，禁止据此自行诊断、开方或用药；临床须咨询执业中医师。"

# ---------------------------------------------------------------------------
# 内嵌抽取事实（源自蒸馏稿 cheatsheet.md / patterns.md / chapters，已校核）
# ---------------------------------------------------------------------------
WUYUN_SHIFANG = [
    {"gan": "壬", "yun": "木", "jiyun": "发生(太过)", "shouxie": "脾土", "fang": "苓术汤", "years": "壬申壬午壬辰壬寅壬子壬戌"},
    {"gan": "戊", "yun": "火", "jiyun": "赫曦(太过)", "shouxie": "肺金", "fang": "麦门冬汤", "years": "戊辰戊寅戊子戊戌戊申戊午"},
    {"gan": "甲", "yun": "土", "jiyun": "敦阜(太过)", "shouxie": "肾水", "fang": "附子山萸汤", "years": "甲子甲戌甲申甲午甲辰甲寅"},
    {"gan": "庚", "yun": "金", "jiyun": "坚成(太过)", "shouxie": "肝木", "fang": "牛膝木瓜汤", "years": "庚午庚辰庚寅庚子庚戌庚申"},
    {"gan": "丙", "yun": "水", "jiyun": "流衍(太过)", "shouxie": "心火", "fang": "川连茯苓汤", "years": "丙寅丙子丙戌丙申丙午丙辰"},
    {"gan": "丁", "yun": "木", "jiyun": "委和(不及)", "shouxie": "肝(燥)", "fang": "苁蓉牛膝汤", "years": "丁卯丁丑丁亥丁酉丁未丁巳"},
    {"gan": "癸", "yun": "火", "jiyun": "伏明(不及)", "shouxie": "心(寒)", "fang": "黄耆茯苓汤", "years": "癸酉癸未癸巳癸卯癸丑癸亥"},
    {"gan": "己", "yun": "土", "jiyun": "卑监(不及)", "shouxie": "脾(风)", "fang": "白术厚朴汤", "years": "己巳己卯己丑己亥己酉己未"},
    {"gan": "乙", "yun": "金", "jiyun": "从革(不及)", "shouxie": "肺(火)", "fang": "紫菀汤", "years": "乙丑乙亥乙酉乙未乙巳乙卯"},
    {"gan": "辛", "yun": "水", "jiyun": "涸流(不及)", "shouxie": "—(原文脱佚)", "fang": "待考", "years": "辛未辛巳辛卯辛丑辛亥辛酉"},
]

LIUQI_LIUFANG = [
    {"zhi": "子/午", "sitian": "少阴君火", "zaiquan": "阳明燥金", "fang": "正阳汤"},
    {"zhi": "丑/未", "sitian": "太阴湿土", "zaiquan": "太阳寒水", "fang": "备化汤"},
    {"zhi": "寅/申", "sitian": "少阳相火", "zaiquan": "厥阴风木", "fang": "升明汤"},
    {"zhi": "卯/酉", "sitian": "阳明燥金", "zaiquan": "少阴君火", "fang": "审平汤"},
    {"zhi": "辰/戌", "sitian": "太阳寒水", "zaiquan": "太阴湿土", "fang": "静顺汤"},
    {"zhi": "巳/亥", "sitian": "厥阴风木", "zaiquan": "少阳相火", "fang": "敷和汤"},
]

LIUYIN_ZHILI = [
    {"yin": "风淫", "zhi": "辛凉", "zuo": "苦甘", "bei": "甘缓、辛散"},
    {"yin": "热淫", "zhi": "咸寒", "zuo": "甘苦", "bei": "酸收、苦发"},
    {"yin": "湿淫", "zhi": "苦热", "zuo": "酸淡", "bei": "苦燥、淡泄"},
    {"yin": "火淫", "zhi": "咸冷", "zuo": "苦辛", "bei": "酸收、苦发"},
    {"yin": "燥淫", "zhi": "苦温", "zuo": "甘辛", "bei": "苦下"},
    {"yin": "寒淫", "zhi": "甘热", "zuo": "苦辛", "bei": "咸泻、辛润、苦坚"},
]

YUNCHOU_GEJUE = (
    "运气推算歌诀（源自王旭高按《内经》与张介宾《类经图翼》编订）："
    "司天歌——子午少阴君火、丑未太阴湿土、寅申少阳相火、卯酉阳明燥金、辰戌太阳寒水、巳亥厥阴风木；"
    "主运歌——初角终羽、太少相生，木大寒交、火春分、土芒种后、金处暑、水立冬，每运73日余；"
    "客运歌——甲己初宫、乙庚初商、丙辛初羽、丁壬初角、戊癸初征，以太少相生；"
    "主气歌——厥阴风木大寒初、少阴君火春分二、少阳相火小满三、太阴湿土大暑四、阳明燥金秋分五、太阳寒水小雪终；"
    "客气歌——子午寒水初、丑未风木、寅申君火、卯酉湿土、辰戌相火、巳亥燥金；"
    "天符岁会——天符(中运同天气，12年，执法，病速危)、太乙天符(天气运支三会，4年，贵人，病暴死)、"
    "岁会(中运同岁支，8年，行令，病徐持)、同天符/同岁会(中运同在泉，阳/阴年)。"
)

WANG_XUGAO_AN = (
    "王旭高核心按语（全书方法论灵魂）：运气方大旨不出《内经》六淫治例与五脏苦欲补泻之义；"
    "反对机械对应——『假令风木之年而得燥金之年之病，即从燥金之年方法求治；若谓其年必生某病必主某方，真是痴人说梦』；"
    "十六方『不过示人以规矩耳，病有万变，药亦万变，圆机之士，不须余赘』——强调活法，反对套方。"
)


def build_entries():
    return [
        {
            "entry_id": "gejue_cjk",
            "rag_key": "gejue_cjk",
            "category": "wuyun_shifang",
            "name": "五运十方（十干年大运方）",
            "summary": "十干年 → 五运太过/不及 → 受邪脏 → 运气方 的框架映射。",
            "mapping": WUYUN_SHIFANG,
            "source_quote": "distilled/yunqi-zhengzhi-gejue/cheatsheet.md#表1 ; patterns.md#模式1 ; chapters/ch02-wuyun-shifang.md",
            "disclaimer": DISCLAIMER,
        },
        {
            "entry_id": "gejue_sitian",
            "rag_key": "gejue_sitian",
            "category": "liuqi_liufang",
            "name": "六气六方（十二支年司天在泉方）",
            "summary": "十二支年 → 司天/在泉 → 客气方 的框架映射（方随六气加减）。",
            "mapping": LIUQI_LIUFANG,
            "source_quote": "distilled/yunqi-zhengzhi-gejue/cheatsheet.md#表2 ; patterns.md#模式2 ; chapters/ch03-liuqi-liufang.md",
            "disclaimer": DISCLAIMER,
        },
        {
            "entry_id": "gejue_liuyin",
            "rag_key": "gejue_liuyin",
            "category": "liuyin_zhili",
            "name": "六淫治例（风/热/湿/火/燥/寒）",
            "summary": "《内经》六淫通用治例原文（正治/佐/备），与五运十方、六气六方互为表里。",
            "mapping": LIUYIN_ZHILI,
            "source_quote": "distilled/yunqi-zhengzhi-gejue/chapters/ch06-liuyin-zhili.md ; cheatsheet.md#表3",
            "disclaimer": DISCLAIMER,
        },
        {
            "entry_id": "gejue_yunchou",
            "rag_key": "gejue_yunchou",
            "category": "yunchou_gejue",
            "name": "运气推算歌诀",
            "summary": YUNCHOU_GEJUE,
            "source_quote": "distilled/yunqi-zhengzhi-gejue/chapters/ch05-yunchou-gejue.md",
            "disclaimer": DISCLAIMER,
        },
        {
            "entry_id": "gejue_an",
            "rag_key": "gejue_an",
            "category": "wang_xugao_an",
            "name": "王旭高按语（反机械对应）",
            "summary": WANG_XUGAO_AN,
            "source_quote": "distilled/yunqi-zhengzhi-gejue/chapters/ch01-zonglun.md",
            "disclaimer": DISCLAIMER,
        },
    ]


def write_asset():
    asset = {
        "asset_id": ASSET_ID,
        "asset_name": "运气证治歌诀（王旭高）蒸馏研读框架",
        "asset_description": (
            "从《运气证治歌诀》（清·王旭高/王泰林，辑自陈无择《三因方》司天运气诸方）"
            "经 book-to-skill 风格蒸馏出的单书研读框架：五运十方、六气六方、运气推算歌诀、六淫治例，"
            "含歌诀原文与王旭高按语。与 asset4_formula（三因司天方现代化数据库）互补——"
            "本资产重『单书框架/歌诀/按语』，asset4 重『现代化病机/临床加减/现代研究』。"
        ),
        "data_source": "清·王旭高《运气证治歌诀》，辑自宋·陈无择《三因极一病证方论》卷四司天运气诸方",
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
    # 去重：若已注册则先移除旧 entry
    index["entries"] = [e for e in index["entries"] if e.get("asset_id") != ASSET_ID]
    index["entries"].append({
        "entry_id": f"rag_index_{ASSET_ID}",
        "entry_type": "asset_index",
        "title": "运气证治歌诀（王旭高）蒸馏框架",
        "file": ASSET_FILE,
        "asset_id": ASSET_ID,
        "asset_name": "运气证治歌诀（王旭高）蒸馏研读框架",
        "asset_category": "distilled_study",
        "description": "从《运气证治歌诀》蒸馏出的单书研读框架：五运十方、六气六方、运气推算歌诀、六淫治例，含歌诀原文与王旭高按语。与 asset4_formula 互补。",
        "total_entries": len(build_entries()),
        "lookup_fields": ["rag_key"],
        "example_keys": ["gejue_cjk", "gejue_sitian", "gejue_liuyin", "gejue_yunchou", "gejue_an"],
        "rag_key": ASSET_ID,
    })
    # total_entries 表示资产数
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
    print("[NEXT] 还需手动在 scripts/rag_search.py 的 ASSET_FILES 字典加：")
    print(f'    "asset34": "{ASSET_FILE}",')
    print(f'    "asset34_yunqi_zhengzhi_gejue": "{ASSET_FILE}",')
    print(f'    "yunqi_zhengzhi_gejue": "{ASSET_FILE}",')
    print(f'    "gejue": "{ASSET_FILE}",')
    print("然后即可：python scripts/rag_search.py --key gejue_cjk")
    return 0


if __name__ == "__main__":
    sys.exit(main())
