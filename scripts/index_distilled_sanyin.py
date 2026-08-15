#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
index_distilled_sanyin.py — 把《三因极一病证方论》卷五「运气诸方」（宋·陈无择）蒸馏稿索引进项目 RAG。

作用：
  1. 将 rag-knowledge-base/distilled/sanyin-sitiansi-yunqi-fang/ 下的蒸馏 skill
     抽取为结构化检索资产 asset36_sanyin_sitiansi_yunqi_fang.json（统一入口）。
  2. 在 rag-knowledge-base/index.json 注册该资产 entry（category=distilled_study）。
  3. 打印下一步：需手动在 scripts/rag_search.py 的 ASSET_FILES 字典 + _default_asset_keys()
     白名单加 asset36 映射（脚本不改动源码）。

设计说明：
  - 与 asset34（王旭高《运气证治歌诀》·歌诀/证治层）、asset35（医宗金鉴《运气要诀》·推算框架层）
    并列：本书 = 「方源」层（十六方药物组成 + 主治 + 岁运/司天在泉归属），为运气用方经典源流。
  - 每条 entry 均带 disclaimer（禁止据以开方），与蒸馏 skill 三件套一致。
  - entry 的 summary 显式收录方名与主要药名，保证关键词检索（如「静顺汤」「辰戌」「附子」）可命中融合。

用法（从仓库根执行）：
  python scripts/index_distilled_sanyin.py
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAG_DIR = os.path.join(REPO_ROOT, "rag-knowledge-base")
DISTILL_SLUG = "sanyin_sitiansi_yunqi_fang"
ASSET_ID = "asset36_sanyin_sitiansi_yunqi_fang"
ASSET_FILE = f"{ASSET_ID}.json"

DISCLAIMER = "⚠️ 仅供中医运气学文献研读与学术框架整理，禁止据此自行诊断、开方或用药；临床须咨询执业中医师。"

# ---------------------------------------------------------------------------
# 内嵌抽取事实（源自蒸馏稿 cheatsheet.md / chapters，已逐字校核宋本底本 _source_juanwu.md）
# ---------------------------------------------------------------------------
# 五运十方（天干 → 运方）：组成字符串为药名枚举（权威逐字组成见 chapters/ch02）
YUNFANG = [
    {"gan": "壬", "yun": "木", "taishao": "太过(发生)", "fang": "苓术汤",
     "zucheng": "白茯苓/厚朴(姜汁制炒)/白术/青皮/干姜(炮)/半夏(汤洗去滑)/草果(去皮)/甘草(炙)"},
    {"gan": "戊", "yun": "火", "taishao": "太过(赫曦)", "fang": "麦门冬汤",
     "zucheng": "麦门冬(去心)/香白芷/半夏(汤洗去滑)/竹叶/甘草(炙)/钟乳粉/桑白皮/紫菀(取茸)/人参"},
    {"gan": "甲", "yun": "土", "taishao": "太过(敦阜)", "fang": "附子山茱萸汤",
     "zucheng": "附子(炮去皮脐)/山茱萸/木瓜干/乌梅/半夏(汤洗去滑)/肉豆蔻/丁香/藿香"},
    {"gan": "庚", "yun": "金", "taishao": "太过(坚成)", "fang": "牛膝木瓜汤",
     "zucheng": "牛膝(酒浸)/木瓜/芍药/杜仲(姜制炒丝断)/枸杞子/黄松节/菟丝子(酒浸)/天麻/甘草(炙)"},
    {"gan": "丙", "yun": "水", "taishao": "太过(流衍)", "fang": "川连茯苓汤",
     "zucheng": "黄连/茯苓/麦门冬(去心)/车前子(炒)/通草/远志(姜汁制炒)/半夏(汤洗去滑)/黄芩/甘草(炙)"},
    {"gan": "丁", "yun": "木", "taishao": "不及(委和)", "fang": "苁蓉牛膝汤",
     "zucheng": "肉苁蓉(酒浸)/牛膝(酒浸)/木瓜干/白芍药/熟地黄/当归/甘草(炙)"},
    {"gan": "癸", "yun": "火", "taishao": "不及(伏明)", "fang": "黄芪茯神汤",
     "zucheng": "黄芪/茯神/远志(姜汁淹炒)/紫荷车/酸枣仁(炒)"},
    {"gan": "己", "yun": "土", "taishao": "不及(卑监)", "fang": "白术厚朴汤",
     "zucheng": "白术/厚朴(姜炒)/半夏(汤洗)/桂心/藿香/青皮/干姜(炮)/甘草(炙)"},
    {"gan": "乙", "yun": "金", "taishao": "不及(从革)", "fang": "紫菀汤",
     "zucheng": "紫菀茸/白芷/人参/甘草(炙)/黄芪/地骨皮/杏仁(去皮尖)/桑白皮(炙)"},
    {"gan": "辛", "yun": "水", "taishao": "不及(涸流)", "fang": "五味子汤",
     "zucheng": "五味子/附子(炮去皮脐)/巴戟(去心)/鹿茸(酥炙)/山茱萸/熟地黄/杜仲(制炒)"},
]

# 六气六岁方（地支岁 → 气方，每岁统司天+在泉）
QIFANG = [
    {"zhi": "辰、戌", "sitian": "太阳寒水", "zaiquan": "太阴湿土", "qi": "先天", "fang": "静顺汤",
     "zucheng": "白茯苓/木瓜干/附子(炮去皮脐)/牛膝(酒浸)/防风(去叉)/诃子(炮去核)/甘草(炙)/干姜(炮)"},
    {"zhi": "卯、酉", "sitian": "阳明燥金", "zaiquan": "少阴君火", "qi": "后天", "fang": "审平汤",
     "zucheng": "远志(姜制炒)/紫檀香/天门冬(去心)/山茱萸/白术/白芍药/甘草(炙)/生姜"},
    {"zhi": "寅、申", "sitian": "少阳相火", "zaiquan": "厥阴风木", "qi": "先天", "fang": "升明汤",
     "zucheng": "紫檀香/车前子(炒)/青皮/半夏(汤洗)/酸枣仁/薔蘼/生姜/甘草(炙)"},
    {"zhi": "丑、未", "sitian": "太阴湿土", "zaiquan": "太阳寒水", "qi": "后天", "fang": "备化汤",
     "zucheng": "木瓜干/茯神(去木)/牛膝(酒浸)/附子(炮去皮脐)/熟地黄/覆盆子/甘草/生姜"},
    {"zhi": "子、午", "sitian": "少阴君火", "zaiquan": "阳明燥金", "qi": "先天", "fang": "正阳汤",
     "zucheng": "白薇/玄参/川芎/桑白皮(炙)/当归/芍药/旋覆花/甘草(炙)/生姜"},
    {"zhi": "巳、亥", "sitian": "厥阴风木", "zaiquan": "少阳相火", "qi": "后天", "fang": "敷和汤",
     "zucheng": "半夏(汤洗)/枣子/五味子/枳实(麸炒)/茯苓/诃子(炮去核)/干姜(炮)/橘皮/甘草(炙)"},
]

# 六气凡例（四畏）+ 各气方随主气加减摘要
FANLI = {
    "四畏凡例(全文)": "凡六气，数起于上而终于下。岁半之前自大寒后天气主之；岁半之后自大暑之后地气主之；上下交互气交主之。司气以热用热无犯；司气以寒用寒无犯；司气以凉用凉无犯；司气以温用温无犯。司气同其主亦无犯；异主则少犯之，是谓四畏。若天气反时，可依时及胜其主则可犯，以平为期，不可过也。",
    "静顺汤(辰戌)加减": "大寒-春分去附子加枸杞；小满-大暑去附子木瓜干姜加人参枸杞地榆香白芷生姜；大暑-秋分加石榴皮；大寒-大寒(小雪后)去牛膝加当归芍药阿胶炒。",
    "审平汤(卯酉)加减": "大寒-春分加白茯苓半夏紫苏生姜；小满-大暑去远志山茱萸白术加丹参泽泻；大暑-秋分去远志白术加酸枣仁车前子。",
    "升明汤(寅申)加减": "大寒-春分加白薇玄参；小满-大暑加漏芦升麻赤芍药；大暑-秋分加茯苓；小雪-大寒加五味子。",
    "备化汤(丑未)加减": "春分-小满去附子加天麻防风；小满-大寒依正方(余季依正方)。",
    "正阳汤(子午)加减": "大寒-春分加杏仁升麻；小满-大暑加杏仁麻仁；大暑-秋分加荆芥茵陈蒿；小雪-大寒加紫苏子。",
    "敷和汤(巳亥)加减": "大寒-春分加鼠黏子；小满-大暑加紫菀；大暑-秋分加泽泻山栀仁。",
}

# 取方指南（按年干支回查运方/气方）
ZHINAN = {
    "天干→运方": "壬苓术汤/戊麦门冬汤/甲附子山茱萸汤/庚牛膝木瓜汤/丙川连茯苓汤/丁苁蓉牛膝汤/癸黄芪茯神汤/己白术厚朴汤/乙紫菀汤/辛五味子汤",
    "地支岁→气方": "辰戌静顺汤/卯酉审平汤/寅申升明汤/丑未备化汤/子午正阳汤/巳亥敷和汤",
    "司天→方": "太阳寒水静顺汤/阳明燥金审平汤/少阳相火升明汤/太阴湿土备化汤/少阴君火正阳汤/厥阴风木敷和汤",
    "在泉→方": "太阴湿土静顺汤/少阴君火审平汤/厥阴风木升明汤/太阳寒水备化汤/阳明燥金正阳汤/少阳相火敷和汤",
    "示例·壬寅年": "天干壬→苓术汤(木运太过)；地支寅→升明汤(少阳相火司天/厥阴风木在泉)。",
    "示例·戊申年": "天干戊→麦门冬汤(火运太过)；地支申→升明汤(少阳相火司天/厥阴风木在泉)。",
    "示例·甲辰年": "天干甲→附子山茱萸汤(土运太过)；地支辰→静顺汤(太阳寒水司天/太阴湿土在泉)。",
}

# 总论 / 源流定位
ZONGLUN = {
    "本书定位": "《三因》卷五运气诸方 = 运气用方「方源」层：十六方(五运十方+六气六岁方)的药物组成+炮制分量+主治+煎服+随气加减，逐字照宋本。",
    "源流": "陈无择十六方为后世运气用方经典源流；明代王旭高《运气证治歌诀》以歌诀体重述十干运方与六支气方(歌诀层)；清代《医宗金鉴·运气要诀》重推算框架(推算层)。三者互补非替代。",
    "岁运总纲": "六壬戊甲庚丙岁(五阳干)=木火土金水太过,五运先天；六丁癸己乙辛岁(五阴干)=木火土金水不及,五运后天。各以五味所胜调和,以平为期。",
    "方源价值": "本书给出「某运/某气年→对应原方+药物组成」的权威原文，是王旭高歌诀与医宗金鉴框架的方源上游。",
}


def build_entries():
    yunfang_summary = (
        "五运十方（按天干岁运，逐字照宋本《三因》卷五）："
        + "；".join(f"{r['gan']}({r['yun']}{r['taishao']})→{r['fang']}({r['zucheng']})" for r in YUNFANG)
        + "。岁运太过五方=壬戊甲庚丙(苓术/麦门冬/附子山茱萸/牛膝木瓜/川连茯苓)；不及五方=丁癸己乙辛(苁蓉牛膝/黄芪茯神/白术厚朴/紫菀/五味子)。"
    )
    qifang_summary = (
        "六气六岁方（按地支岁，每岁统司天+在泉，逐字照宋本）："
        + "；".join(f"{r['zhi']}({r['sitian']}司天/{r['zaiquan']}在泉,{r['qi']})→{r['fang']}({r['zucheng']})" for r in QIFANG)
        + "。"
    )
    return [
        {
            "entry_id": "sanyin_yunfang",
            "rag_key": "sanyin_yunfang",
            "category": "sanyin_yunfang",
            "name": "五运十方（天干 → 岁运方）",
            "summary": yunfang_summary,
            "mapping": YUNFANG,
            "source_quote": "distilled/sanyin-sitiansi-yunqi-fang/chapters/ch02-wuyun-shiyifang.md ; cheatsheet.md#表1,#表5 ; _source_juanwu.md",
            "disclaimer": DISCLAIMER,
        },
        {
            "entry_id": "sanyin_qifang",
            "rag_key": "sanyin_qifang",
            "category": "sanyin_qifang",
            "name": "六气六岁方（地支岁 → 司天在泉方）",
            "summary": qifang_summary,
            "mapping": QIFANG,
            "source_quote": "distilled/sanyin-sitiansi-yunqi-fang/chapters/ch03-liuqi-siyifang.md ; cheatsheet.md#表2,#表3,#表4 ; _source_juanwu.md",
            "disclaimer": DISCLAIMER,
        },
        {
            "entry_id": "sanyin_fanli",
            "rag_key": "sanyin_fanli",
            "category": "sanyin_fanli",
            "name": "六气凡例（四畏） + 各气方随主气加减法",
            "summary": "六气凡例「四畏」：" + FANLI["四畏凡例(全文)"] + " 各气方随主气(大寒/春分/小满/大暑/秋分/小雪)加减法见 mapping。运气用方第一红线：司气寒热温凉不可妄犯。",
            "mapping": [{"item": k, "value": v} for k, v in FANLI.items()],
            "source_quote": "distilled/sanyin-sitiansi-yunqi-fang/chapters/ch05-zhifa-fanli.md ; _source_juanwu.md",
            "disclaimer": DISCLAIMER,
        },
        {
            "entry_id": "sanyin_zhinan",
            "rag_key": "sanyin_zhinan",
            "category": "sanyin_zhinan",
            "name": "按年干支取方指南（运方 + 气方）",
            "summary": "按年干支回查运气用方：" + "；".join(f"{k}: {v}" for k, v in ZHINAN.items()),
            "mapping": [{"item": k, "value": v} for k, v in ZHINAN.items()],
            "source_quote": "distilled/sanyin-sitiansi-yunqi-fang/chapters/ch08-shiyong-zhinan.md ; cheatsheet.md",
            "disclaimer": DISCLAIMER,
        },
        {
            "entry_id": "sanyin_zonglun",
            "rag_key": "sanyin_zonglun",
            "category": "sanyin_zonglun",
            "name": "总论与源流定位（方源层）",
            "summary": "；".join(f"{k}：{v}" for k, v in ZONGLUN.items()),
            "mapping": [{"item": k, "value": v} for k, v in ZONGLUN.items()],
            "source_quote": "distilled/sanyin-sitiansi-yunqi-fang/chapters/ch01-zonglun.md ; chapters/ch06-yuanliu.md ; _source_juanwu.md",
            "disclaimer": DISCLAIMER,
        },
    ]


def write_asset():
    asset = {
        "asset_id": ASSET_ID,
        "asset_name": "三因极一病证方论·卷五运气诸方（宋·陈无择）蒸馏研读框架",
        "asset_description": (
            "从宋·陈言（陈无择）《三因极一病证方论》卷之五「五运时气民病证治」「六气时行民病证治」"
            "经 book-to-skill 风格蒸馏出的运气用方「方源」层框架：十六方（五运十方 + 六气六岁方）的"
            "药物组成、炮制分量、主治、煎服法与随气加减，逐字照宋本底本。"
            "本书是运气用方的经典源流——明代王旭高《运气证治歌诀》（歌诀/证治层）重述其方，"
            "清代《医宗金鉴·运气要诀》（推算框架层）重推算；三者互补，本书为「方源」上游。"
        ),
        "data_source": "宋·陈言（陈无择）《三因极一病证方论》卷之五 五运时气民病证治 / 六气时行民病证治（公有领域）",
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
        "title": "三因极一病证方论·卷五运气诸方（宋·陈无择）蒸馏框架",
        "file": ASSET_FILE,
        "asset_id": ASSET_ID,
        "asset_name": "三因极一病证方论·卷五运气诸方（宋·陈无择）蒸馏研读框架",
        "asset_category": "distilled_study",
        "description": "从《三因极一病证方论》卷五蒸馏出的运气用方「方源」层框架：十六方(五运十方+六气六岁方)组成/主治/岁运司天在泉归属。为王旭高《运气证治歌诀》(asset34)与医宗金鉴《运气要诀》(asset35)的方源上游。",
        "total_entries": len(build_entries()),
        "lookup_fields": ["rag_key"],
        "example_keys": ["sanyin_yunfang", "sanyin_qifang", "sanyin_fanli", "sanyin_zhinan", "sanyin_zonglun"],
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
    print(f'     "asset36": "{ASSET_FILE}",')
    print(f'     "asset36_sanyin_sitiansi_yunqi_fang": "{ASSET_FILE}",')
    print(f'     "sanyin_sitiansi_yunqi_fang": "{ASSET_FILE}",')
    print(f'     "sanyin": "{ASSET_FILE}",')
    print(f'     "sanyin_yunqi_fang": "{ASSET_FILE}",')
    print("  2) _default_asset_keys() 白名单元组加：")
    print('     "asset36",')
    print("然后即可：python scripts/rag_search.py --key sanyin_yunfang")
    return 0


if __name__ == "__main__":
    sys.exit(main())
