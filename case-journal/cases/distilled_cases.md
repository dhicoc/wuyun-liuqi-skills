# 圣济总录六十甲子岁图医案 · 蒸馏索引

> 共蒸馏 60 个岁图医案（六十甲子完整），来自宋《政和圣济总录》运气门（公版）。
> 每条 = 一年的运气医案：岁运/司天在泉/六步客气病机与治法/年病机/年治法/原文摘录。
>
> 结构化数据：`rag-knowledge-base/asset9_cases.json`（可被 `rag_search --key` 按 rag_key 检索）
> 原文来源：`rag-knowledge-base/literature/圣济总录运气门（运气诸论·六十甲子岁图）.md`

## 检索方法

| 用户问 | Grep / 命令 | 定位 |
|--------|------------|------|
| 某格局同类医案 | `rag_search.py --key <rag_key> --asset asset9` | 按岁运/司天 rag_key 召回所有同格局岁图 |
| 某日运气同类医案 | `rag_search.py --date <日期>` | 按日推算 rag_keys 后批量命中含医案 |
| 某干支年医案 | Grep `甲子岁图` / `丙寅岁图` 等 | 本索引 / asset9 |
| 某步客气病机 | Grep `初之气`/`终之气` + 病机词 | asset9 six_steps |

## 按司天在泉六组分类

### 子午之岁（少阴君火司天 / 阳明燥金在泉）
| 干支 | 岁运 | case_id |
|------|------|---------|
| 甲子 | 土运太过 | shengji_jiazi |
| 庚午 | 金运太过 | shengji_gengwu |
| 丙子 | 水运太过 | shengji_bingzi |
| 壬午 | 木运太过 | shengji_renwu |
| 戊午 | 火运太过 | shengji_wuwu |

### 丑未之岁（太阴湿土司天 / 太阳寒水在泉）
| 干支 | 岁运 | case_id |
|------|------|---------|
| 乙丑 | 金运不及 | shengji_yichou |
| 辛未 | 水运不及 | shengji_xinwei |
| 丁丑 | 木运不及 | shengji_dingchou |
| 己未 | 土运不及 | shengji_jiwei |
| 癸未 | 火运不及 | shengji_guiwei |

### 寅申之岁（少阳相火司天 / 厥阴风木在泉）
| 干支 | 岁运 | case_id |
|------|------|---------|
| 丙寅 | 水运太过 | shengji_bingyin |
| 壬申 | 木运太过 | shengji_renshen |
| 庚申 | 金运太过 | shengji_gengshen |
| 戊申 | 火运太过 | shengji_wushen |
| 甲申 | 土运太过 | shengji_jiashen |

### 卯酉之岁（阳明燥金司天 / 少阴君火在泉）
| 干支 | 岁运 | case_id |
|------|------|---------|
| 丁卯 | 木运不及 | shengji_dingmao |
| 癸酉 | 火运不及 | shengji_guiyou |
| 辛卯 | 水运不及 | shengji_xinmao |
| 乙酉 | 金运不及 | shengji_yiyou |
| 己卯 | 土运不及 | shengji_jimao |

### 辰戌之岁（太阳寒水司天 / 太阴湿土在泉）
| 干支 | 岁运 | case_id |
|------|------|---------|
| 戊辰 | 火运太过 | shengji_wuchen |
| 甲戌 | 土运太过 | shengji_jiaxu |
| 庚辰 | 金运太过 | shengji_gengchen |
| 丙戌 | 水运太过 | shengji_bingxu |
| 壬辰 | 木运太过 | shengji_renchen |

### 巳亥之岁（厥阴风木司天 / 少阳相火在泉）
| 干支 | 岁运 | case_id |
|------|------|---------|
| 己巳 | 土运不及 | shengji_jisi |
| 乙亥 | 金运不及 | shengji_yihai |
| 辛巳 | 水运不及 | shengji_xinsi |
| 丁亥 | 木运不及 | shengji_dinghai |
| 癸巳 | 火运不及 | shengji_guisi |

（以上每组列代表年，完整 60 条见 asset9_cases.json）

## 与项目的关系

- **推算引擎联动**：`calculate_yunqi_api` 算出某日 rag_keys（suiyun/sitian/zaiquan）后，`rag_search --key <rag_key> --asset asset9` 召回所有同格局岁图医案——**这是按运气格局可检索的医案库**，nihaixia 按疾病分类的医案库做不到
- **与五层注释链互补**：五层注释链给"某格局该用什么方/什么病机/怎么治"的通则；asset9 给"该格局在六十甲子各年里的具体病机治法"的逐年实例
- **医案沉淀模板**：与 `case-journal/_template.md` 配套——asset9 是公版岁图医案，_template 是用户自己记录医案的模板

## 蒸馏说明

- 蒸馏方式：workflow 6 agent 并行，每个负责 10 个岁图，基于公版原文逐条提取
- 不编造：每条 source_quote 逐字保留原文关键句
- rag_key 映射：与项目 calculate_yunqi_api 输出的 rag_keys 同键（suiyun/sitian/zaiquan），确保推算结果能直接检索医案

---

> ⚠️ 免责：以上医案为公版中医古籍《政和圣济总录》原文结构化整理，仅作运气学理论参考。运气学说非现代医学诊断标准，具体诊疗须由执业中医师辨证论治。
