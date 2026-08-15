# 五运六气六书研读工作流（蒸馏框架 × RAG 双轨）

> 本文档定义「五运六气六书（王旭高《运气证治歌诀》、吴谦《医宗金鉴·运气要诀》、陈无择《三因》卷五运气诸方、张介宾《类经图翼》卷一·卷二运气、刘温舒《素问入式运气论奥》、王肯堂/殷宅心《医学穷源集·卷二》运气专论）专题研读」的 Agent 工作流。
>
> **核心主张：蒸馏框架与 RAG 不是替代关系，而是互补。**
> - **蒸馏框架（distilled / asset34·35·36·37·38·39）** 负责「单书框架、歌诀原文、方源原文、象数基础、专论机制、专论灾变、一跳表查」——结构清晰、零歧义、适合讲清「这本书怎么讲」。六书互补：王旭高（歌诀层）、医宗金鉴（推算框架层）、三因（方源层）、类经图翼（图翼·象数基础层）、刘温舒（专论·机制纵深层）、王肯堂/殷宅心（专论·灾变纵深层）。
> - **RAG（asset1/2/4/5/6/10/14/17 等数十部文献）** 负责「跨书出处、现代化病机、临床加减、真实医案实证、温疫运气、地域」——适合回答「这本书之外，其他人/后世怎么用、有没有临床证据」。
>
> 配套路由：`routing.yaml → id: yunqi-gejue-distilled`（王旭高）/ `yizong-jinjian-yunqi-yaojue`（医宗金鉴）/ `sanyin-sitiansi-yunqi-fang`（三因）/ `liejing-tuyi-yunqi`（类经图翼）/ `suwen-rushi-yunqi-lunao`（刘温舒）/ `yixue-qiongyuanji-yunqi`（医学穷源集）。
> 配套蒸馏资产：`rag-knowledge-base/distilled/yunqi-zhengzhi-gejue/`（asset34）、`distilled/yizong-jinjian-yunqi-yaojue/`（asset35）、`distilled/sanyin-sitiansi-yunqi-fang/`（asset36）、`distilled/liejing-tuyi-yunqi/`（asset37）、`distilled/suwen-rushi-yunqi-lunao/`（asset38）、`distilled/yixue-qiongyuanji-yunqi/`（asset39）。
> 配套 RAG 索引：已注册为 `asset34_yunqi_zhengzhi_gejue`（`--key gejue_*`）、`asset35_yizong_jinjian_yunqi_yaojue`（`--key yaojue_*`）、`asset36_sanyin_sitiansi_yunqi_fang`（`--key sanyin_*`）、`asset37_liejing_tuyi_yunqi`（`--key liejing_*`）、`asset38_suwen_rushi_yunqi_lunao`（`--key lunao_*`）、`asset39_yixue_qiongyuanji_yunqi`（`--key qiongyuanji_*`）。

---

## 一、何时走本工作流（路由判定）

命中 `routing.yaml` 中 `yunqi-gejue-distilled` / `yizong-jinjian-yunqi-yaojue` / `sanyin-sitiansi-yunqi-fang` / `liejing-tuyi-yunqi` / `suwen-rushi-yunqi-lunao` / `yixue-qiongyuanji-yunqi` 任一任务的 `trigger_examples` 即走本流：

- 运气证治歌诀 / 王旭高歌诀 / 王泰林
- 十干运气方 / 六气六方 / 司天在泉方 / 运气推算歌诀
- 三因司天方（陈无择原方，王旭高辑订）
- 类经图翼 / 张景岳运气 / 运气象数 / 太极阴阳五行气数 / 五天五运 / 五音建运 / 正化对化 / 南北政 / 天符岁会
- 医学穷源集 / 王肯堂运气 / 太乙移宫 / 升降不前 / 三年化疫 / 刚柔失守 / 疫由人事 / 人定胜天 / 灾宫 / 方月图说 / 运气不验 / 六气本标中 / 药法补泻正味 / 十二经配天干

> 若用户问题属于「泛运气学框架」（非特指上述五书之一），仍走主 `react_workflow.md`；本流是「该书专题研读」的子流。

---

## 二、双轨分工（必读）

| 维度 | 蒸馏框架（distilled / asset34·35·36·37·38·39） | RAG（asset1/2/4/5/6/10/14/17…） |
|------|-------------------------------|--------------------------|
| 知识边界 | 单书（六书之一：歌诀/推算框架/方源/象数基础/专论机制/专论灾变） | 全库数十部文献（含后世临床/温疫/地域） |
| 最擅长 | 框架/歌诀/方源/象数基础/专论机制/专论灾变一跳直取 | 跨书出处、病机现代化、临床加减、真实医案、温疫运气、地域 |
| 典型问法 | 「壬年用什么方」「六气六方是哪六个」「甲己为何化土」「南北政脉不应」「纳音为何金先」「胜复如何闭环」「三年化疫怎么推」「运气为什么不验」「人定胜天」「药法补泻正味」「十二经配天干」 | 「这方后世怎么用」「有没有临床医案佐证」「瘟疫运气怎么讲」 |
| 取数命令 | `rag_search --key gejue_*` / `yaojue_*` / `sanyin_*` / `liejing_*` / `lunao_*` / `qiongyuanji_*` 或直接读 chapters | `rag_search --key <rag_key>` / 关键词检索 |
| 安全定位 | 框架整理，禁开方 | 文献实证，禁开方 |

**黄金法则**：先用蒸馏框架把「这本书的框架与歌诀」讲准讲全，再用 RAG 补「外部佐证与临床延伸」。两者结论冲突时，标注来源让用户判断，不替用户二选一。

---

## 三、研读推理链（ReAct 风格）

```
用户输入（年干支 / 方名 / 歌诀 / 临床疑问）
        │
        ▼
┌──────────────────────────────────────────────────────┐
│  Step 1  ROUTE   命中 yunqi-gejue-distilled            │
│          加载 distilled/SKILL.md（总控 + 与 RAG 协作指引）│
└──────────────────────┬───────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────┐
│  Step 2  FRAME   取单书框架（二选一）                   │
│   (a) rag_search --key gejue_cjk|sitian|liuyin|         │
│       yunchou|an  （已索引，带 provenance + 免责）       │
│   (b) 直接读 chapters/ch0X-*.md（更细的随气加减/方解）   │
└──────────────────────┬───────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────┐
│  Step 3  CROSS  跨书取证 / 临床延伸（按需，走 RAG）      │
│   方剂现代化病机/加减 → asset4（三因司天方现代化数据库）  │
│   岁运病机           → asset1（岁运病机）                │
│   司天在泉病机       → asset2（司天在泉）                │
│   岁运治法           → asset10（岁运治法）               │
│   真实医案实证       → asset14（丁甘仁医案）等           │
└──────────────────────┬───────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────┐
│  Step 4  MERGE   合并输出                              │
│   ① 本书框架（歌诀 + 王旭高按语）                        │
│   ② 外部佐证（出处 / 现代化病机 / 临床加减）              │
│   ③ 临床实证（医案，若有）                              │
│   ④ 安全声明（禁止据以开方，须咨询执业中医师）           │
└──────────────────────────────────────────────────────┘
```

**闭环特性**：Step 3 是对 Step 2 的补充而非必经；若问题纯属「背歌诀/查框架」，Step 3 可跳过。若 RAG 未命中（如某方后世无记录），明确说「库内未见延伸记载」，不编造。

---

## 四、取数速查（命令模板）

```bash
# 1) 蒸馏框架一跳直取（推荐，自带 provenance + 免责）
python scripts/rag_search.py --key gejue_cjk      # 五运十方（十干年大运方）
python scripts/rag_search.py --key gejue_sitian   # 六气六方（十二支年司天在泉方）
python scripts/rag_search.py --key gejue_liuyin   # 六淫治例（风/热/湿/火/燥/寒）
python scripts/rag_search.py --key gejue_yunchou  # 运气推算歌诀
python scripts/rag_search.py --key gejue_an        # 王旭高按语（反机械对应）

# 2) 跨书取证（RAG，指定资产更精准）
python scripts/rag_search.py --key <rag_key> --asset asset4   # 三因司天方现代化数据库
python scripts/rag_search.py 丁甘仁 运气         # 真实医案实证（关键词）
python scripts/rag_search.py --key water_excess  # 岁运病机（示例）

# 3) 关键词混合检索（自动跨 asset34 + 其他资产，证明统一检索）
python scripts/rag_search.py 王旭高
```

---

## 五、输出模板

> **【本书框架】** （来自《运气证治歌诀》王旭高 / 蒸馏稿）
>   <歌诀或框架要点，含王旭高按语>
>   📚 provenance: `distilled/yunqi-zhengzhi-gejue/...`
>
> **【外部佐证】** （来自 RAG 跨书检索）
>   <现代化病机 / 临床加减 / 后世用法，注明 asset 与 ref>
>   📚 provenance: `yle:asset4_...:...`
>
> **【临床实证】** （若有真实医案）
>   <医案要点，注明 asset14 等 ref>
>
> **⚠️ 安全声明**：以上内容仅供中医运气学文献研读与学术框架整理，
> 禁止据此自行诊断、开方或用药；临床须咨询执业中医师。

---

## 六、安全纪律（强制）

- 蒸馏稿已做三层安全包裹（SKILL.md 头警告 + cheatsheet 最高级警告 + ch07 最强警告）；本流输出必须带 **④ 安全声明**。
- **禁止**给出具体处方、剂量、煎服法供用户自用；方名仅作「学术引用」。
- 辛年涸流方原文脱佚，输出须标注「待考」，不得臆补。
- 王旭高按语核心是「反对机械对应、强调活法」——输出须体现此方法论，避免把运气方讲成「某年必主某方」。

---

## 七、示范问答（见 `rag-knowledge-base/distilled/yunqi-zhengzhi-gejue/EVAL_vs_RAG.md`）

该文档含 3 组「研读式问答对比 RAG」实录，展示双轨如何配合；本节仅给一个最小示例：

**问：壬年（如壬寅）运气病机与用方？**
- 蒸馏框架：`--key gejue_cjk` → 壬/木/发生(太过)/受邪脾土/苓术汤（years 含壬寅）。
- RAG 延伸：`--asset asset4` 查「苓术汤」现代化病机与临床加减；`--asset asset1` 查岁运「木太过」病机。
- 合并输出：框架（歌诀+方）+ 现代化病机 + 安全声明。

---

## 八、医宗金鉴·运气要诀研读（asset35，重推算框架）

《医宗金鉴》卷三十五「编辑运气要诀」（清·吴谦）是运气**推算全框架**教科书，
与《运气证治歌诀》（asset34，重方）互补：**本书讲「推算框架广度」，王旭高讲「证治用方」**。
本书基本不载方剂，核心是「气化格局 ↔ 脏腑病机 ↔ 病证归类」的推演体系。

### 取数速查（asset35，统一入口 key）

```bash
python scripts/rag_search.py --key yaojue_tiangan   # 天干→化运/太少/合人脏腑
python scripts/rag_search.py --key yaojue_dizhi     # 地支→六气/脏腑/司天在泉
python scripts/rag_search.py --key yaojue_tianfu    # 天符/岁会/太乙/同天符/同岁会/南北政
python scripts/rag_search.py --key yaojue_weibing   # 运气为病五藏归属 + 岁运太过受邪脏
python scripts/rag_search.py --key yaojue_zhinan    # 主气六位/主运五位/正化对化/五运名
# 或直接读 chapters/（更细的歌诀原文 + 注文）
```

### 跨书取证（RAG，按需）

- 岁运病机/岁运治法：`--asset asset1` / `--asset asset10`
- 司天在泉病机：`--asset asset2`
- 三因司天方现代化数据库（与王旭高本同源，含临床加减）：`--asset asset4`
- 真实医案实证：`--asset asset14`

### 双轨分工再强调

| 问法 | 走蒸馏（asset35） | 走 RAG |
|------|------------------|--------|
| "甲己化土怎么落到脏腑" | ✅ 1 跳查表 `yaojue_tiangan` | — |
| "子午年司天在泉与客气六步" | ✅ `yaojue_dizhi` + ch04 | — |
| "天符/岁会/太乙有哪些年" | ✅ `yaojue_tianfu`（枚举 28 年） | — |
| "卯酉年阳明司天主什么病" | ✅ ch07 客气主病歌原文 | `asset2`+`asset14` 补病机/医案 |
| "运气为病五藏归属原文" | ✅ ch07 运气为病歌 | `asset1` 现代化阐释 |

> 本书与王旭高本共同构成运气学的「推算框架 + 证治用方」双研读层；五者均由
> `routing.yaml` 的 `yunqi-gejue-distilled` / `yizong-jinjian-yunqi-yaojue` / `sanyin-sitiansi-yunqi-fang` / `liejing-tuyi-yunqi` / `suwen-rushi-yunqi-lunao` 任务路由，
> 且已并入 `rag_search.py` 默认检索范围（asset34 + asset35 + asset36 + asset37 + asset38），一次关键词检索即可同时命中五书与既有 RAG。

---

## 九、三因·卷五运气诸方研读（asset36，方源层）

宋·陈言（陈无择）《三因极一病证方论》卷之五「五运时气民病证治」「六气时行民病证治」是运气用方的**方源**——十六方（五运十方 + 六气六岁方）的药物组成、炮制分量、主治、煎服与随气加减，逐字照宋本底本。它与《运气证治歌诀》（asset34，歌诀层）、《医宗金鉴·运气要诀》（asset35，推算框架层）**互补而非替代**：

- **本书（陈无择本）**：重「方源」——十六方原文，是运气用方的「原方上游层」。
- **王旭高本（asset34）**：重「歌诀」——把方源编成方歌，便于记诵与证治对照。
- **医宗金鉴本（asset35）**：重「推算框架」——按年干支推算运气格局，落点五脏病机；基本不载具体方剂。

### 取数速查（asset36，统一入口 key）

```bash
python scripts/rag_search.py --key sanyin_yunfang   # 五运十方（天干→岁运方，10 方组成照底本）
python scripts/rag_search.py --key sanyin_qifang    # 六气六岁方（地支岁→司天在泉方，6 方）
python scripts/rag_search.py --key sanyin_fanli     # 六气凡例（四畏）+ 各气方随主气加减法
python scripts/rag_search.py --key sanyin_zhinan    # 按年干支取方指南（运方+气方+司天/在泉→方）
python scripts/rag_search.py --key sanyin_zonglun   # 总论与源流定位（方源层）
# 或直接读 chapters/（更细的十六方组成/煎服/加减原文）
```

### 跨书取证（RAG，按需）

- 岁运病机/岁运治法：`--asset asset1` / `--asset asset10`
- 司天在泉病机：`--asset asset2`
- 三因司天方现代化数据库（含临床加减/现代研究）：`--asset asset4`
- 真实医案实证：`--asset asset14`

### 三书三层（方源+歌诀+框架）互补（第四层·图翼象数基础见第十节；第五层·专论机制见第十一节）

| 层 | 书 | 蒸馏资产 | 重什么 | 典型问法 |
|----|----|----------|--------|----------|
| 方源层 | 陈无择《三因》卷五 | asset36 | 十六方原文（组成/分量/煎服/加减） | 「壬年用哪方、组成是什么」「辰戌年司天在泉与方名」 |
| 歌诀层 | 王旭高《运气证治歌诀》 | asset34 | 方歌、按语、证治对照 | 「十干运气方歌诀」「六淫治例」 |
| 推算框架层 | 吴谦《医宗金鉴·运气要诀》 | asset35 | 按年干支推算格局、天符岁会、南北政 | 「甲己化土怎么落脏腑」「天符岁会有哪些年」 |

### 双轨分工再强调

| 问法 | 走蒸馏（asset36） | 走 RAG |
|------|------------------|--------|
| "壬年用哪方、组成是什么" | ✅ 1 跳 `sanyin_yunfang` + ch02 | — |
| "辰戌年司天在泉与方名" | ✅ `sanyin_qifang` + ch03 | `asset2` 补病机 |
| "某方随主气怎么加减" | ✅ `sanyin_fanli`（六气凡例照底本） | `asset4`/`asset10` 补现代阐释 |
| "苓术汤后世怎么用/有无临床" | ✅ 方源原文 | `asset4`（现代化方剂研究）+ `asset14`（医案） |
| "运气为病五藏归属" | （在 asset35 ch07） | `asset1` 现代化阐释 |

---

## 十、类经图翼·卷一·卷二运气研读（asset37，图翼·象数基础层）

明·张介宾（张景岳）《类经图翼》卷一「运气上」、卷二「运气下」是运气学的**象数·哲学地基 + 图翼推算框架**——太极—阴阳—五行生成数—气数（卷一）与五运（五天五运/五音建运太少相生/主客运）、六气（正化对化/主客气/司天在泉）、天符岁会、南北政脉不应（卷二），逐字照明本底本。它**补全医宗金鉴《运气要诀》所缺的象数根基**，并加五音建运、南北政脉不应等深度，与三因《运气诸方》（方源层）、王旭高《运气证治歌诀》（歌诀层）、医宗金鉴《运气要诀》（推算框架广度层）**互补而非替代**：

- **本书（张介宾本）**：重「象数基础 + 图翼推算细节」——太极阴阳五行气数哲学地基、五天五运下临化运、五音太少相生链、主客运 73 日零 5 刻、正化对化、南北政脉不应，是运气学的「图翼·象数基础层」。
- **王旭高本（asset34）**：重「歌诀」——把运气治法编成方歌。
- **医宗金鉴本（asset35）**：重「推算框架广度」——按年干支推算格局，基本不载具体方剂。
- **三因本（asset36）**：重「方源」——十六方原文。

### 取数速查（asset37，统一入口 key）

```bash
python scripts/rag_search.py --key liejing_xiangshu   # 象数基础层（太极/阴阳/五行生成数/气数·卷一）
python scripts/rag_search.py --key liejing_wuyun     # 五运（五天五运/五音太少相生/主客运·卷二）
python scripts/rag_search.py --key liejing_liuqi     # 六气（正化对化/主客气/司天在泉/推六气法·卷二）
python scripts/rag_search.py --key liejing_tianfu    # 天符岁会（天符/太乙/岁会/同天符/同岁会·28年）
python scripts/rag_search.py --key liejing_nanbei    # 南北政（南北政说/脉不应/阴阳交/尺寸反）
python scripts/rag_search.py --key liejing_zonglun   # 总论与源流定位（图翼·象数基础层）
# 或直接读 chapters/（更细的卷一·卷二运气原文与图说）
```

### 跨书取证（RAG，按需）

- 岁运病机/岁运治法：`--asset asset1` / `--asset asset10`
- 司天在泉病机：`--asset asset2`
- 三因司天方现代化数据库（含临床加减/现代研究）：`--asset asset4`
- 历代注家运气学说（含张景岳本人条目）：`--asset asset5`
- 真实医案实证：`--asset asset14`

### 六书六层互补（必读定位）

| 层 | 书 | 蒸馏资产 | 重什么 | 典型问法 |
|----|----|----------|--------|----------|
| 专论·灾变纵深层 | 王肯堂/殷宅心《医学穷源集·卷二》运气专论 | asset39 | 系统讲刚柔失守三年化疫（甲子/丙寅/庚辰/壬午/戊申五年详例＋先补脏次泄气）、疫由人事（人定胜天）、太乙移宫九宫八风、升降不前/不迁正不退位、化数生成、流年灾宫、方月图说（运气不验之由）、山川方隅、六气本标中从化、药法摘录、十二经配天干 | 「三年化疫怎么推」「甲子什么疫」「运气为什么不验」「灾宫怎么算」「疫由人事/人定胜天」「六气本标中怎么分」「药法补泻正味」「十二经配天干」 |
| 专论·机制纵深层 | 刘温舒《素问入式运气论奥》 | asset38 | 第一本独立运气专著；卷上象数纵深（纳音/六化/五行本义/日刻/标本）+ 卷下机制纵深（胜复·五郁·六病·六脉·治法·五行胜复论＝亢害承制机制化） | 「纳音为何金先」「胜复如何闭环」「五郁如何治」「六气为病有哪些」「五行胜复论怎么讲」 |
| 图翼·象数基础层 | 张介宾《类经图翼》卷一·卷二 | asset37 | 太极—阴阳—五行生成数—气数根基 + 图翼推算细节（五音建运/南北政脉不应） | 「天一生水怎么解」「甲己为何化土」「五音太少相生链」「南北政脉不应怎么定上下」 |
| 方源层 | 陈无择《三因》卷五 | asset36 | 十六方原文（组成/分量/煎服/加减） | 「壬年用哪方、组成是什么」「辰戌年司天在泉与方名」 |
| 歌诀层 | 王旭高《运气证治歌诀》 | asset34 | 方歌、按语、证治对照 | 「十干运气方歌诀」「六淫治例」 |
| 推算框架层 | 吴谦《医宗金鉴·运气要诀》 | asset35 | 按年干支推算格局、天符岁会、南北政体例广度 | 「甲己化土怎么落脏腑」「天符岁会有哪些年」 |

### 双轨分工再强调

| 问法 | 走蒸馏（asset37） | 走 RAG |
|------|------------------|--------|
| "河图生成数怎么解（天一生水）" | ✅ 1 跳 `liejing_xiangshu` + ch02 | — |
| "甲己为何化土 / 五音太少相生链" | ✅ `liejing_wuyun` + ch03 | `asset5` 补注家异说 |
| "南北政脉不应怎么定上下" | ✅ `liejing_nanbei` + ch06 | `asset2` 补病机印证 |
| "天符岁会六十年共多少年" | ✅ `liejing_tianfu` + ch05（28年+总歌） | `asset5`/`asset36` 关联方源/注家 |
| "运气为病五藏归属原文" | ✅（在 asset35 ch07） | `asset1` 现代化阐释 |

> 六书共同构成运气学的「专论灾变 + 专论机制 + 象数基础 + 方源 + 歌诀 + 框架」六层研读体系，均由 `routing.yaml` 路由（`yunqi-gejue-distilled` / `yizong-jinjian-yunqi-yaojue` / `sanyin-sitiansi-yunqi-fang` / `liejing-tuyi-yunqi` / `suwen-rushi-yunqi-lunao` / `yixue-qiongyuanji-yunqi`），且已并入 `rag_search.py` 默认检索范围（asset34 + asset35 + asset36 + asset37 + asset38 + asset39），一次关键词检索即可同时命中六书与既有 RAG。

---

## 十一、素问入式运气论奥研读（asset38，专论·机制纵深层）

宋·刘温舒《素问入式运气论奥》（元符己卯 / 1099，已入《正统道藏》太玄部，公有领域）是运气学史上**第一本独立的运气专著**（承《素问》运气七篇、王冰次注、《玄珠密语》而专论之），定位为「专论·机制纵深层」。其独有纵深在：卷上象数（纳音／六化／五行本义／日刻／标本）+ 卷下机制（胜复·五郁·六病·六脉·治法·五行胜复论＝亢害承制机制化），填补四书在「气化失衡→自稳→病机」机制上的空白。与三因（方源）、王旭高（歌诀）、医宗金鉴（推算框架）、类经图翼（象数基础）**互补而非替代**：

- **本书（刘温舒本）**：重「专论机制」——把运气格局接到临床病机→治法，独有纳音/六化/胜复/五郁/六病/六脉/五行胜复论机制化。
- **王旭高本（asset34）**：歌诀层；**医宗金鉴本（asset35）**：推算框架层；**三因本（asset36）**：方源层；**类经图翼本（asset37）**：象数基础层。

### 取数速查（asset38，统一入口 key）

```bash
python scripts/rag_search.py --key lunao_zonglun          # 总论与源流定位（专论·机制纵深层，第一本运气专著·承前启后）
python scripts/rag_search.py --key lunao_xiangshu         # 象数基础层（五行本义/十干/十二支/纳音/六化/四时气候/日刻/标本/生成数 + 诸图图解）
python scripts/rag_search.py --key lunao_wuyun            # 五运（五天五运/五音建运/月建/纪运三纪/岁中五运）
python scripts/rag_search.py --key lunao_liuqi            # 六气（天地六气/主气/客气正化对化/天符岁会/南北政）
python scripts/rag_search.py --key lunao_chengzhi_yufa    # 亢害承制·胜复·五郁（机制纵深核心）+ 九宫分野 + 六十年客气
python scripts/rag_search.py --key lunao_bingji_zhiliao   # 六病·六脉·治法（病机→治法桥梁，必先岁气无伐天和）
python scripts/rag_search.py --key lunao_tu               # 诸图图解（枢要图/纪运图/起运诀/司天诀/太少相临图/手足经图/客气旁通图）
# 或直接读 chapters/（更细的逐字专论机制原文）
```

### 跨书取证（RAG，按需）

- 岁运病机/岁运治法：`--asset asset1` / `--asset asset10`
- 司天在泉病机：`--asset asset2`
- 三因司天方现代化数据库（含临床加减/现代研究）：`--asset asset4`
- 历代注家运气学说（含刘温舒条目）：`--asset asset5`
- 真实医案实证：`--asset asset14`

### 双轨分工再强调

| 问法 | 走蒸馏（asset38） | 走 RAG |
|------|------------------|--------|
| "纳音为何金先（独家纵横）" | ✅ 1 跳 `lunao_xiangshu` + ch02（同类娶妻隔八生子） | `asset5` 补注家异说 |
| "胜复如何闭环（亢害承制）" | ✅ `lunao_chengzhi_yufa` + ch05（论胜复第二十五＋五行胜复论） | `asset5`/`asset10` 补跨书病机印证 |
| "五郁如何治（木郁达之火郁发之…）" | ✅ `lunao_chengzhi_yufa`（五郁治法） | `asset1` 现代化病机 |
| "六气为病有哪些（病机桥梁）" | ✅ `lunao_bingji_zhiliao` + ch06（论六病第二十八） | `asset2`/`asset1` 补病机现代化 |
| "必先岁气无伐天和 / 六脉" | ✅ `lunao_bingji_zhiliao`（论六脉第二十九） | `asset14` 补医案 |
| "南北政推理本书与图翼之异" | ✅ ch04 诚实标注（甲己土运居中 vs 十干之首象君） | `asset37` 对观 |

> 本书与既有五书共同构成运气学的「专论灾变 + 专论机制 + 图翼象数 + 方源 + 歌诀 + 框架」**六层研读体系**，整体定位见第十节「六书六层互补（必读定位）」表。六书均由 `routing.yaml` 路由（`yunqi-gejue-distilled` / `yizong-jinjian-yunqi-yaojue` / `sanyin-sitiansi-yunqi-fang` / `liejing-tuyi-yunqi` / `suwen-rushi-yunqi-lunao` / `yixue-qiongyuanji-yunqi`），且已并入 `rag_search.py` 默认检索范围（asset34 + asset35 + asset36 + asset37 + asset38 + asset39），一次关键词检索即可同时命中六书与既有 RAG。

---

## 十二、医学穷源集·卷二 运气专论研读（asset39，专论·灾变纵深层）

明·王肯堂 撰、殷宅心 辑释《医学穷源集·卷二》运气专论，是运气学史上系统讲「刚柔失守三年化疫」与「运气不验因方月」及「疫由人事/人定胜天」的关键文献，定位为「专论·灾变纵深层」。其独有纵深在：太乙移宫九宫八风、左右升降不前/司天不迁正不退位、五年化疫详例（甲子土疫/丙寅水疫/庚辰金疫/壬午木疫/戊申火疫，各先补所胜脏次泄本运气）、疫由人事论（人定胜天）、化数生成、流年灾宫、方月图说（运气不验之由）、山川方隅气候不同论、六气本标中从化解、药法摘录（五味补泻/脏腑苦欲/六气客主补泻正味）、十二经配天干歌。它与三因（方源）、王旭高（歌诀）、医宗金鉴（推算框架）、类经图翼（象数基础）、刘温舒（专论机制）**互补而非替代**；尤其「灾变纵深」填补五书在「刚柔失守→三年化疫」与「运气不验之由」上的空白。

### 取数速查（asset39，统一入口 key）

```bash
python scripts/rag_search.py --key qiongyuanji_zonglun          # 运气总论（太过/不及/平气·亢害承制·六气各归不胜而为化·胜复郁发·验法四端）
python scripts/rag_search.py --key qiongyuanji_taiyi_shengjiang # 太乙移宫九宫八风（实风虚风/三虚）＋ 升降不前·不迁正·不退位
python scripts/rag_search.py --key qiongyuanji_sanshinian_huayi # 五运失守三年化疫（甲子/丙寅/庚辰/壬午/戊申五年详例）＋ 疫由人事论（人定胜天）
python scripts/rag_search.py --key qiongyuanji_huashu_zai      # 化数生成说（成数/生数·戊寅戊申例外）＋ 流年灾宫说
python scripts/rag_search.py --key qiongyuanji_fangyue         # 方月图说（运气不验之由）＋ 山川方隅气候不同论
python scripts/rag_search.py --key qiongyuanji_benbiaozhong    # 六气本标中从化解（从本/从本从标/从中）＋ 治病标本说
python scripts/rag_search.py --key qiongyuanji_yaofa           # 药法摘录（🛑 最强警告章）＋ 十二经配天干歌
# 或直接读 chapters/（更细的逐字专论原文）
```

### 跨书取证（RAG，按需）

- 岁运病机/岁运治法：`--asset asset1` / `--asset asset10`
- 司天在泉病机：`--asset asset2`
- 三因司天方现代化数据库（含临床加减/现代研究）：`--asset asset4`
- 历代注家运气学说（含王肯堂/殷宅心条目）：`--asset asset5`
- 真实医案实证：`--asset asset14`
- 温疫运气（补「三年化疫/木疫」后世发挥）：`--asset asset17`
- 地域运气（补山川方隅气候）：`--asset asset6`

### 双轨分工再强调

| 问法 | 走蒸馏（asset39） | 走 RAG |
|------|------------------|--------|
| "三年化疫怎么推（甲子什么疫）" | ✅ 1 跳 `qiongyuanji_sanshinian_huayi` + ch03（五年详例） | `asset17` 补温疫发挥、`asset5` 补注家 |
| "运气为什么不验" | ✅ `qiongyuanji_fangyue`（方月图说）＋ ch05 | `asset6` 补地域气候 |
| "灾宫怎么算（己年灾几宫）" | ✅ `qiongyuanji_huashu_zai` + ch04 | `asset37` 对观生成数 |
| "疫由人事/人定胜天" | ✅ `qiongyuanji_sanshinian_huayi`（疫由人事论） | `asset17` 补温疫学史 |
| "六气本标中怎么分" | ✅ `qiongyuanji_benbiaozhong` + ch06 | `asset38` 对观标本中见 |
| "药法补泻正味/十二经配天干" | ✅ `qiongyuanji_yaofa` + ch07（🛑 最强警告） | `asset4`/`asset10` 补方药剂法 |

> 本书与既有五书共同构成运气学的「专论灾变 + 专论机制 + 象数基础 + 方源 + 歌诀 + 框架」**六层研读体系**，整体定位见第十节「六书六层互补（必读定位）」表。六书均由 `routing.yaml` 路由（`yunqi-gejue-distilled` / `yizong-jinjian-yunqi-yaojue` / `sanyin-sitiansi-yunqi-fang` / `liejing-tuyi-yunqi` / `suwen-rushi-yunqi-lunao` / `yixue-qiongyuanji-yunqi`），且已并入 `rag_search.py` 默认检索范围（asset34 + asset35 + asset36 + asset37 + asset38 + asset39），一次关键词检索即可同时命中六书与既有 RAG。
