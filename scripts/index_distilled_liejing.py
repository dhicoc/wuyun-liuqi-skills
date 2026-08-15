#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
index_distilled_liejing.py — 把《类经图翼》卷一·卷二「运气」（明·张介宾/张景岳）蒸馏稿索引进项目 RAG。

作用：
  1. 将 rag-knowledge-base/distilled/liejing-tuyi-yunqi/ 下的蒸馏 skill
     抽取为结构化检索资产 asset37_liejing_tuyi_yunqi.json（统一入口）。
  2. 在 rag-knowledge-base/index.json 注册该资产 entry（category=distilled_study）。
  3. 打印下一步：需手动在 scripts/rag_search.py 的 ASSET_FILES 字典 + _default_asset_keys()
     白名单加 asset37 映射（脚本不改动源码）。

设计说明：
  - 与 asset34（王旭高《运气证治歌诀》·歌诀/证治层）、asset35（医宗金鉴《运气要诀》·推算框架层）、
    asset36（三因《运气诸方》·方源层）并列：本书 = 「图翼·象数基础」层
    （太极—阴阳—五行—气数之哲学地基 + 五音建运太少相生 + 南北政脉不应等深度），
    补全医宗金鉴推算框架所缺的象数根基。四书互补，非替代。
  - 每条 entry 均带 disclaimer（禁止据以开方/诊断），与蒸馏 skill 三件套一致。
  - entry 的 summary 显式收录关键古文与术语，保证关键词检索（如「天一生水」「南北政」「天符」「太少相生」）可命中融合。

用法（从仓库根执行）：
  python scripts/index_distilled_liejing.py
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAG_DIR = os.path.join(REPO_ROOT, "rag-knowledge-base")
DISTILL_SLUG = "liejing_tuyi_yunqi"
ASSET_ID = "asset37_liejing_tuyi_yunqi"
ASSET_FILE = f"{ASSET_ID}.json"

DISCLAIMER = "⚠️ 仅供中医运气学文献研读与学术框架整理，禁止据此自行诊断、开方或用药；临床须咨询执业中医师。"

# ---------------------------------------------------------------------------
# 内嵌抽取事实（源自蒸馏稿 chapters，已逐字校核明本底本 _source_liejing.md）
# ---------------------------------------------------------------------------
# 卷一·运气上：象数·哲学地基
XIANGSHU = [
    {"jie": "太极图论", "yaodian": "太极本无极，故曰太虚；太极动静而阴阳分；阴阳便是太极；理气阴阳之学实医道开卷第一义。"},
    {"jie": "阴阳体象", "yaodian": "阴阳者天地之道也，万物之纪纲，变化之父母，生杀之本始，神明之府也；由两仪而四象，由四象而五行。"},
    {"jie": "五行生成数解", "yaodian": "天一生水地六成之；地二生火天七成之；天三生木地八成之；地四生金天九成之；天五生土地十成之。太过者其数成，不及者其数生，土常以生也（甲丙戊庚壬五太应成，乙丁己辛癸五少应生）。"},
    {"jie": "五行统论", "yaodian": "木火土金水相生谓之顺，木土水火金相克谓之逆；干支所属五行：东方甲乙寅卯木，南方丙丁巳午火，西方庚辛申酉金，北方壬癸亥子水，辰戌丑未王四季，戊己中央皆属土。"},
    {"jie": "气数统论", "yaodian": "河图定数：生数为主居内，成数为配居外；至而至者和，至而不至来气不及也，未至而至来气有余也；太过被抑不及得助皆为平气。"},
]

# 卷二·运气下：五运（五天五运 / 五音建运太少相生 / 主运 / 客运）
WUYUN = {
    "五天五运(五天歌)": "木苍危室柳鬼宿，火丹牛女璧奎边，土黅心尾轸角度，金素亢氐昴毕前，水玄张翼娄胃是，下为运气上经天。",
    "五天五气经宿下临化运": "丹天火气经牛女壁奎下临戊癸→火运；黅天土气经心尾角轸下临甲己→土运；苍天木气经危室柳鬼下临丁壬→木运；素天金气经亢氐昴毕下临乙庚→金运；玄天水气经张翼娄胃下临丙辛→水运。",
    "五音建运太少相生链(逐字)": "甲阳土生乙少商→乙阴金生丙太羽→丙阳水生丁少角→丁阴木生戊太征→戊阳火生己少宫→己阴土生庚太商→庚阳金生辛少羽→辛阴水生壬太角→壬阳木生癸少征→癸阴火复生甲太宫。",
    "三气歌": "敷和发生委和木，升明赫曦伏明火，审平坚成从革金，备化敦阜卑监土，静顺流衍涸流水，平气太过不及数。",
    "主运图说": "每岁五运各得七十三日零五刻（始于大寒），必始于角而终于羽，主春木→夏火→长夏土→秋金→冬水，岁气分阴阳而主运有太少之异。",
    "客运图说": "客运亦一年五步各七十三日零五刻，以本年中运为初运而以次相生（主运则必春始于角而冬终于羽）；十年一主令而竟天干。",
}

# 卷二·运气下：六气（正化对化 / 主气 / 客气司天在泉 / 推六气法）
LIUQI = {
    "六气正化对化": "厥阴司巳亥（正亥对巳，木生亥）；少阴司子午（正午对子，君火当离位）；太阴司丑未（正未对丑，土王西南）；少阳司寅申（正寅对申，相火生寅）；阳明司卯酉（正酉对卯，金位西方）；太阳司辰戌（正戌对辰，水渐王乡）。",
    "主气六步(固定)": "厥阴木（初气，春分前六十日有奇）→少阴君火（二气）→少阳相火（三气）→太阴湿土（四气）→阳明燥金（五气）→太阳寒水（终气）。有常而无变。",
    "客气司天在泉": "客气以三阴三阳先后为序（厥阴一阴→少阴二阴→太阴三阴→少阳一阳→阳明二阳→太阳三阳）；司天位三之气，在泉位终之气；岁半前天气主之，岁半后地气主之。",
    "司天歌": "子午少阴为君火，丑未太阴临湿土，寅申少阳相火王，卯酉阳明燥金所，辰戌太阳寒水边，巳亥厥阴风木主。初气起地之左间，司天在泉对面数。",
    "推六气法": "司天前二位即初气，前一位即二气，本位司天为三气，后一位为四气，后二位为五气，后三位为终气（在泉）。掌中一轮，六气燎然在握。",
    "指掌法": "以巳亥为始起厥阴司天，子午位为少字，丑未位为太字，顺数到底皆其年分之司天；六气以「厥、少太、少阳太」六字尽之。",
}

# 卷二·运气下：天符岁会
TIANFU = {
    "天符": "应天为天符，中运之气与司天之气相同，共十二年；中执法者其病速而危。",
    "太乙天符": "天符兼岁会（天气运气岁支三者俱会），共四年：戊午、乙酉、己丑、己未；中贵人者其病暴而死。",
    "岁会": "承岁为岁直，中运之气与岁支相同，共八年（四正子午卯酉 + 辰戌丑未）；中行令者其病徐而持。",
    "同天符/同岁会": "中运与在泉相合，阳年曰同天符（六年），阴年曰同岁会（六年）。",
    "六十年统计": "天符十二 + 太乙天符四 + 岁会八 + 同天符六 + 同岁会六 = 分言三十六年；合言六十年中得二十八年（太乙天符已含于天符，岁会八年有四同于天符）。",
    "天符岁会总歌": "天符中运同天气，太乙全兼运会支；岁会运支须四正，辰戌丑未亦相宜；同天同岁泉同运，阴岁阳天不必疑。",
}

# 卷二·运气下：南北政
NANBEI = {
    "南北政说": "南北二政运有不同，上下阴阳脉有不应；以巳为南政（甲己年），余为北政。南政南面行令寸为上尺为下；北政北面受令尺应上寸应下，在泉应两寸司天应两尺。",
    "脉不应": "阴之所在脉乃沉细不应；北政三阴在下则寸不应，三阴在上则尺不应；南政三阴在天则寸不应，三阴在泉则尺不应；诸不应者反其诊则见矣。",
    "阴阳交/尺寸反": "阴阳交（死）：少阴所易之位非其脉，惟辰戌丑未寅申巳亥八年有之；尺寸反（死）：当尺不应而见于寸，惟子午卯酉年有之；必阴阳俱交/尺寸俱反始为死候，不可胶柱。",
    "南北政歌": "南政子午两寸沉，丑未巳亥左右寻（左右寸），卯酉两尺寅申左（左尺），辰戌右尺真分明；北政阳明沉两寸，太阳少阳左右应（左右寸），少阴两尺厥阴左（左尺），太阴右尺何须问。",
    "推原南北政说": "甲己为十干之首（六甲必起甲子月、甲己日必起甲子时），象君而为南政，余北面象臣而为北政；非「土为五行之尊」之说，乃花甲自然之理（奇门亦独以甲己为符头）。",
}

# 总论 / 源流定位
ZONGLUN = {
    "本书定位": "《类经图翼》卷一·卷二「运气」= 图翼·象数基础层：卷一立太极—阴阳—五行—气数之哲学地基（医道开卷第一义），卷二以图翼（图解+图说）展开五运六气推算全框架，补医宗金鉴推算框架广度所缺的象数根基，并加五音建运、南北政脉不应等深度。",
    "四书互补": "三因《运气诸方》(方源层) / 王旭高《运气证治歌诀》(歌诀层) / 医宗金鉴《运气要诀》(推算框架广度层) / 类经图翼(象数基础层)；四者互补非替代，本书为象数地基上游。",
    "活法锚点": "张介宾客气图解「不可胶柱」：客气所加乃胜制郁发之变，和则为生化不和则为灾伤，圆机之士当因常以察变，因此以察彼，与王旭高「反对机械对应」精神相通。",
    "源流": "明·张介宾（张景岳）《类经图翼》为《类经》附翼，以图解（图说文字存、原图缺）通运气全貌，是明代运气象数集成之作；其太极阴阳五行气数论述为后世运气学哲学根基。",
}


def build_entries():
    xiangshu_summary = (
        "卷一·运气上（象数·哲学地基，逐字照明本《类经图翼》）："
        + "；".join(f"{r['jie']}：{r['yaodian']}" for r in XIANGSHU)
        + "。此为运气「气化」之哲学根基——太极—阴阳—五行—气数，医道开卷第一义。"
    )
    return [
        {
            "entry_id": "liejing_xiangshu",
            "rag_key": "liejing_xiangshu",
            "category": "liejing_xiangshu",
            "name": "象数基础层（卷一·运气上：太极/阴阳/五行生成数/气数）",
            "summary": xiangshu_summary,
            "mapping": [{"item": r["jie"], "value": r["yaodian"]} for r in XIANGSHU],
            "source_quote": "distilled/liejing-tuyi-yunqi/chapters/ch02-xiangshu-jichu.md ; _source_liejing.md 卷一",
            "disclaimer": DISCLAIMER,
        },
        {
            "entry_id": "liejing_wuyun",
            "rag_key": "liejing_wuyun",
            "category": "liejing_wuyun",
            "name": "五运（卷二：五天五运/五音建运太少相生/主运/客运）",
            "summary": "卷二·运气下·五运（逐字照底本）：" + "；".join(f"{k}：{v}" for k, v in WUYUN.items()),
            "mapping": [{"item": k, "value": v} for k, v in WUYUN.items()],
            "source_quote": "distilled/liejing-tuyi-yunqi/chapters/ch03-wuyun.md ; _source_liejing.md 卷二·五运",
            "disclaimer": DISCLAIMER,
        },
        {
            "entry_id": "liejing_liuqi",
            "rag_key": "liejing_liuqi",
            "category": "liejing_liuqi",
            "name": "六气（卷二：正化对化/主气/客气司天在泉/推六气法）",
            "summary": "卷二·运气下·六气（逐字照底本）：" + "；".join(f"{k}：{v}" for k, v in LIUQI.items()),
            "mapping": [{"item": k, "value": v} for k, v in LIUQI.items()],
            "source_quote": "distilled/liejing-tuyi-yunqi/chapters/ch04-liuqi.md ; _source_liejing.md 卷二·六气",
            "disclaimer": DISCLAIMER,
        },
        {
            "entry_id": "liejing_tianfu",
            "rag_key": "liejing_tianfu",
            "category": "liejing_tianfu",
            "name": "天符岁会（卷二：天符/太乙天符/岁会/同天符同岁会）",
            "summary": "卷二·运气下·天符岁会（逐字照底本）：" + "；".join(f"{k}：{v}" for k, v in TIANFU.items()),
            "mapping": [{"item": k, "value": v} for k, v in TIANFU.items()],
            "source_quote": "distilled/liejing-tuyi-yunqi/chapters/ch05-tianfu-suihui.md ; _source_liejing.md 卷二·天符岁会",
            "disclaimer": DISCLAIMER,
        },
        {
            "entry_id": "liejing_nanbei",
            "rag_key": "liejing_nanbei",
            "category": "liejing_nanbei",
            "name": "南北政（卷二：南北政说/脉不应/阴阳交尺寸反/推原南北政）",
            "summary": "卷二·运气下·南北政（逐字照底本）：" + "；".join(f"{k}：{v}" for k, v in NANBEI.items()),
            "mapping": [{"item": k, "value": v} for k, v in NANBEI.items()],
            "source_quote": "distilled/liejing-tuyi-yunqi/chapters/ch06-nanbei-zheng.md ; _source_liejing.md 卷二·南北政",
            "disclaimer": DISCLAIMER,
        },
        {
            "entry_id": "liejing_zonglun",
            "rag_key": "liejing_zonglun",
            "category": "liejing_zonglun",
            "name": "总论与源流定位（图翼·象数基础层）",
            "summary": "；".join(f"{k}：{v}" for k, v in ZONGLUN.items()),
            "mapping": [{"item": k, "value": v} for k, v in ZONGLUN.items()],
            "source_quote": "distilled/liejing-tuyi-yunqi/chapters/ch01-zonglun.md ; chapters/ch08-shiyong-zhinan.md ; _source_liejing.md 卷三·定位",
            "disclaimer": DISCLAIMER,
        },
    ]


def write_asset():
    asset = {
        "asset_id": ASSET_ID,
        "asset_name": "类经图翼·运气（明·张介宾）蒸馏研读框架",
        "asset_description": (
            "从明·张介宾（张景岳）《类经图翼》卷一「运气上」、卷二「运气下」经 book-to-skill 风格"
            "蒸馏出的运气「图翼·象数基础」层框架：卷一立太极—阴阳—五行—气数之哲学地基"
            "（医道开卷第一义），卷二以图翼（图解+图说）展开五运六气推算全框架"
            "（五天五运、五音建运太少相生、主客运、正化对化、主客气、司天在泉、天符岁会、南北政脉不应），逐字照明本底本。"
            "本书补全医宗金鉴《运气要诀》（推算框架广度层，asset35）所缺的象数根基，"
            "并加五音建运、南北政脉不应等深度；与三因《运气诸方》(asset36·方源层)、"
            "王旭高《运气证治歌诀》(asset34·歌诀层) 四书互补，非替代。"
        ),
        "data_source": "明·张介宾（张景岳）《类经图翼》卷一·卷二 运气（公有领域，四库全书本）",
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
        "title": "类经图翼·运气（明·张介宾）蒸馏框架",
        "file": ASSET_FILE,
        "asset_id": ASSET_ID,
        "asset_name": "类经图翼·运气（明·张介宾）蒸馏研读框架",
        "asset_category": "distilled_study",
        "description": "从《类经图翼》卷一·卷二蒸馏出的运气「图翼·象数基础」层框架：太极—阴阳—五行—气数地基 + 五运六气推算全框架（五音建运太少相生/正化对化/主客气/司天在泉/天符岁会/南北政脉不应）。为医宗金鉴《运气要诀》(asset35)的象数根基上游，与三因(asset36·方源)/王旭高(asset34·歌诀)四书互补。",
        "total_entries": len(build_entries()),
        "lookup_fields": ["rag_key"],
        "example_keys": ["liejing_xiangshu", "liejing_wuyun", "liejing_liuqi", "liejing_tianfu", "liejing_nanbei", "liejing_zonglun"],
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
    print("  1) ASSET_FILES 字典加（接在 asset36 之后）：")
    print(f'     "asset37": "{ASSET_FILE}",')
    print(f'     "asset37_liejing_tuyi_yunqi": "{ASSET_FILE}",')
    print(f'     "liejing_tuyi_yunqi": "{ASSET_FILE}",')
    print(f'     "liejing": "{ASSET_FILE}",')
    print(f'     "liejing_tuyi": "{ASSET_FILE}",')
    print(f'     "tuyi": "{ASSET_FILE}",')
    print("  2) _default_asset_keys() 白名单元组加：")
    print('     "asset37",')
    print("然后即可：python scripts/rag_search.py --key liejing_xiangshu")
    return 0


if __name__ == "__main__":
    sys.exit(main())
