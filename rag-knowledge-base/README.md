# RAG 知识库索引

本文档是 `rag-knowledge-base/` 的维护索引。知识库通过 `scripts/calculate_yunqi_api.py` 生成的 `rag_keys` 精确检索，为病机分析、报告生成、个人体质和高级对齐提供结构化资料。

## 字段级 Schema

各 RAG asset 的字段级 schema 位于：

```text
rag-knowledge-base/schemas/
```

| Asset | Schema |
|-------|--------|
| `asset1_suiyun.json` | `schemas/asset1_suiyun.schema.json` |
| `asset2_sitian_zaiquan.json` | `schemas/asset2_sitian_zaiquan.schema.json` |
| `asset3_kezhujialin.json` | `schemas/asset3_kezhujialin.schema.json` |
| `asset4_formula.json` | `schemas/asset4_formula.schema.json` |
| `asset5_commentary.json` | `schemas/asset5_commentary.schema.json` |
| `asset6_regional.json` | `schemas/asset6_regional.schema.json` |
| `asset7_constitution.json` | `schemas/asset7_constitution.schema.json` |
| `asset9_cases.json` | `schemas/asset9_cases.schema.json` |
| `asset10_suiyi_zhifa.json` | `schemas/asset10_suiyi_zhifa.schema.json` |
| `asset11_mingyi_cases.json` | `schemas/asset11_mingyi_cases.schema.json` |
| `asset12_xumingyi_cases.json` | `schemas/asset12_xumingyi_cases.schema.json` |
| `asset13_gujin_an_cases.json` | `schemas/asset13_gujin_an_cases.schema.json` |
| `asset14_dingganren_cases.json` | `schemas/asset14_dingganren_cases.schema.json` |
| `asset15_shanghan90_cases.json` | `schemas/asset15_shanghan90_cases.schema.json` |
| `asset16_ye_cases.json` | `schemas/asset16_ye_cases.schema.json` |
| `asset17_wenyi_yunqi.json` | `schemas/asset17_wenyi_yunqi.schema.json` |
| `asset18_huichunlu_cases.json` | `schemas/asset18_huichunlu_cases.schema.json` |
| `asset19_zhangyuqing_cases.json` | `schemas/asset19_zhangyuqing_cases.schema.json` |
| `asset20_wujutong_cases.json` | `schemas/asset20_wujutong_cases.schema.json` |
| `asset21_yuyicao_cases.json` | `schemas/asset21_yuyicao_cases.schema.json` |
| `asset22_huixi_cases.json` | `schemas/asset22_huixi_cases.schema.json` |
| `asset23_huayunlou_cases.json` | `schemas/asset23_huayunlou_cases.schema.json` |
| `asset24_zhenyu_juji_cases.json` | `schemas/asset24_zhenyu_juji_cases.schema.json` |
| `asset25_xushi_cases.json` | `schemas/asset25_xushi_cases.schema.json` |
| `asset26_xingxuan_cases.json` | `schemas/asset26_xingxuan_cases.schema.json` |
| `asset27_sunwenyuan_cases.json` | `schemas/asset27_sunwenyuan_cases.schema.json` |
| `asset28_conggui_cases.json` | `schemas/asset28_conggui_cases.schema.json` |
| `asset29_waike_zhengzong.json` | `schemas/asset29_waike_zhengzong.schema.json` |
| `asset30_lizhai_waike.json` | `schemas/asset30_lizhai_waike.schema.json` |
| `asset31_zuihuachuang_cases.json` | `schemas/asset31_zuihuachuang_cases.schema.json` |
| `asset32_yiyan_suibi.json` | `schemas/asset32_yiyan_suibi.schema.json` |
| `terminology.json` | `schemas/terminology.schema.json` |
| `index.json` | `schemas/index.schema.json` |

## 资产总览

| Asset | 文件 | 类型 | 主要用途 | 典型检索键 |
|-------|------|------|----------|------------|
| asset1 | `asset1_suiyun.json` | 岁运病机 | 五运太过/不及病机、症状、治则 | `water_excess`, `fire_deficient` |
| asset2 | `asset2_sitian_zaiquan.json` | 司天在泉 | 上下半年六气病机与治法 | `shaoyin_junhuo_sitian`, `yangming_zaojin_zaiquan` |
| asset3 | `asset3_kezhujialin.json` | 客主加临 | 六步主客气组合、顺逆、病机 | `zhu_shaoyang_ke_shaoyin` |
| asset4 | `asset4_formula.json` | 运气方 | 三因司天方、方药方向 | `water_excess` |
| asset5 | `asset5_commentary.json` | 历代注家 | 王冰、刘完素、张景岳等注家观点 | `related_yunqi_keys` |
| asset6 | `asset6_regional.json` | 地域修正 | 八大区域气候与体质倾向修正 | 地区名 / `region_id` |
| asset7 | `asset7_constitution.json` | 运气体质 | 出生年运气体质映射、岁运调理 | `fire_deficient` |
| asset9 | `asset9_cases.json` | 岁图医案 | 圣济总录六十甲子岁图医案（按 rag_key 检索） | `jiezi`, `bingyin` |
| asset10 | `asset10_suiyi_zhifa.json` | 岁宜治法 | 六气司天岁宜治法表 | 岁运 / 司天 |
| asset11 | `asset11_mingyi_cases.json` | 名医类案 | 明·江瓘，历代医案汇编 | `entry_id`, `category` |
| asset12 | `asset12_xumingyi_cases.json` | 续名医类案 | 清·魏之琇，续补名医案 | `entry_id`, `category` |
| asset13 | `asset13_gujin_an_cases.json` | 古今医案按 | 清·俞震，含"震按"辨证要点 | `entry_id`, `category` |
| asset14 | `asset14_dingganren_cases.json` | 丁甘仁医案 | 近代丁甘仁，临证实录 | `entry_id`, `category` |
| asset15 | `asset15_shanghan90_cases.json` | 伤寒九十论 | 宋·许叔微，伤寒经方医案 | `entry_id`, `category` |
| asset16 | `asset16_ye_cases.json` | 临证指南医案 | 清·叶桂，辨证精审含华岫云按语 | `entry_id`, `category` |
| asset17 | `asset17_wenyi_yunqi.json` | 运气瘟疫防治 | 清·刘奎《松峰说疫》卷六运气专篇：五运太过不及瘟疫侧重、六气司天民病、五郁治法、刚柔失守疫病专方 | `code`, `sitian_key`, `zaiquan_key`, `rag_key`, `ganzhi`, `category` |
| asset18 | `asset18_huichunlu_cases.json` | 回春录医案 | 清·王孟英《回春录》（王氏医案）：湿热温病、内科杂病、妇科、儿科医案 | `category`, `physician`, `rag_key`, `case_id` |
| asset19 | `asset19_zhangyuqing_cases.json` | 张聿青医案 | 清·张乃修《张聿青医案》：湿温伏暑、痰饮肝风、虚损血证、内科杂病医案 | `category`, `physician`, `rag_key`, `case_id` |
| asset20 | `asset20_wujutong_cases.json` | 吴鞠通医案 | 清·吴瑭《吴鞠通医案》：温病三焦辨证、风温暑温伏暑、痹证痰饮医案 | `category`, `physician`, `rag_key`, `case_id` |
| asset21 | `asset21_yuyicao_cases.json` | 寓意草医案 | 清·喻嘉言《寓意草》：议病式医案、伤寒危证、真阳上脱、误治救逆、痢疾疫情、肺痈痰病 | `category`, `physician`, `rag_key`, `case_id` |
| asset22 | `asset22_huixi_cases.json` | 洄溪医案 | 清·徐灵胎《洄溪医案》（王孟英编）：经方辨证、中风伤寒、温疫、痰喘、血痢、产后、外科痈疽 | `category`, `physician`, `rag_key`, `case_id` |
| asset23 | `asset23_huayunlou_cases.json` | 花韵楼医案 | 清·顾德华（女医）《花韵楼医案》：妇科专案，崩漏、月经不调、产后、胎产、乳癖 | `category`, `physician`, `rag_key`, `case_id` |
| asset24 | `asset24_zhenyu_juji_cases.json` | 诊余举隅录 | 清·陈廷儒《诊余举隅录》：辨证精审，霍乱痢疾泄泻、感冒春温、中风、妇科经闭 | `category`, `physician`, `rag_key`, `case_id` |
| asset25 | `asset25_xushi_cases.json` | 许氏医案 | 清·许恩普《许氏医案》：断证如折狱，伤寒痢疾中风、胎产妇科、误治救逆 | `category`, `physician`, `rag_key`, `case_id` |
| asset26 | `asset26_xingxuan_cases.json` | 杏轩医案 | 清·程文囿（新安医派）《杏轩医案》：产后感邪、格阳证、大头时疫、半产血晕、蓄瘀脱血 | `category`, `physician`, `rag_key`, `case_id` |
| asset27 | `asset27_sunwenyuan_cases.json` | 孙文垣医案 | 明·孙一奎《孙文垣医案》：温补命门、大头疫、目疾虚实、产后发热、痰火胁痛、心痹 | `category`, `physician`, `rag_key`, `case_id` |
| asset28 | `asset28_conggui_cases.json` | 丛桂草堂医案 | 清·袁焯《丛桂草堂医案》：痰饮闭塞、喉痧阴亏、孕产寒痛、疮疡阴亏 | `category`, `physician`, `rag_key`, `case_id` |
| asset29 | `asset29_waike_zhengzong.json` | 外科正宗·外用医案 | 明·陈实功《外科正宗》：痈疽疔疮瘰疬脱疽，艾灸/火针/蟾酥饼/琥珀膏外治 | `category`, `physician`, `rag_key`, `case_id` |
| asset30 | `asset30_lizhai_waike.json` | 立斋外科发挥·内外联动 | 明·薛己《立斋外科发挥》：痈疽以气血为本最忌攻伐，内因→外候联动 | `category`, `physician`, `rag_key`, `internal_key`, `external_key` |
| asset31 | `asset31_zuihuachuang_cases.json` | 醉花窗医案 | 清·王堉《醉花窗医案》：脉证互参、阴虚实热脾虚肝郁鉴别、误治救逆 | `category`, `physician`, `rag_key`, `case_id` |
| asset32 | `asset32_yiyan_suibi.json` | 医验随笔 | 近代·沈奉江（孟河马培之高足）《医验随笔》：温病痰喘便秘、温毒发痘、疙瘩瘟，内外兼治 | `category`, `physician`, `rag_key`, `case_id` |
| terminology | `terminology.json` | 术语库 | 学习解释、报告术语扩展 | term / pinyin / entry_id |

> asset11-16 六部历代名家医案库共 **901 条**临证真实医案，按 `entry_id` / `category` 可检索。

## 推荐检索顺序

```text
1. calculate_yunqi_api.py <date> --json
2. 读取 rag_keys.suiyun → asset1
3. 读取 rag_keys.sitian / rag_keys.zaiquan → asset2
4. 读取 rag_keys.current_step → asset3
5. 如需方药方向 → asset4
6. 如需注家观点 → asset5
7. 如用户提供地区 → asset6
8. 如用户提供出生日期或体质 → asset7
9. 如需教学解释 → terminology
10. 如需岁图医案 / 岁宜治法 / 历代名家临证医案 → asset9 / asset10 / asset11-16（按 `entry_id` 或 `category` 检索）
```

## 与脚本的关系

- `scripts/calculate_yunqi_api.py`：生成标准化 `rag_keys`。
- `scripts/demo_full_chain.py`：演示推算到 RAG 检索的完整链路。
- `scripts/validate_knowledge_base.py`：校验资产结构。
- `scripts/ingest_literature.py`：注入新文献或新增条目。

## 维护规则

1. 新增条目必须包含至少一个可检索键：`key` / `code` / `rag_key` / `sitian_key` / `zaiquan_key` / `constitution_code` / `region_id`。
2. 新增或修改资产后运行：

   ```bash
   python scripts/validate_knowledge_base.py
   python tests/full_regression_test.py
   ```

3. 涉及临床、方药、针灸的条目必须保留“仅供参考，须辨证论治”的安全边界。
4. 若新增资产文件，请同步更新本 README 与 `index.json`。
