# 第八章 取用指南（按年干支查运气格局 · 跨书取证 · 多轨衔接）

> 本章供「怎么用本蒸馏」之研读指引。所有内容仅供文献研读与学术框架对照，禁止据此自行诊断、开方或用药，须咨询执业中医师。

## 一、按年干支查运气格局（本书补足象数/图翼细节）
本项目的**通用运气推算**走 `modules/yunqi-calc/` 与 `scripts/calculate_yunqi_api.py`，可据年干支直接得到岁运、司天在泉、天符岁会、南北政等格局。**本书（图翼·象数基础层，asset37）补足通用推算所缺的象数根基与图翼细节**：
- 为何「甲己化土、戊癸化火」——查 `chapters/ch03-wuyun.md` 五天五运图解 / 月建夫妇化运三说。
- 五音太少相生链与初运太少——查 `chapters/ch03-wuyun.md` 五音建运太少相生 / 主客运图说。
- 主客运各 73 日零 5 刻、始于大寒——查 `chapters/ch03-wuyun.md`。
- 正化对化所司地支、主气六步、司天歌、推六气法、指掌法——查 `chapters/ch04-liuqi.md`。
- 南北政上下、脉不应、阴阳交尺寸反——查 `chapters/ch06-nanbei-zheng.md`。

> 读法：先用通用推算得到「当年格局」，再读本 skill 补「为什么如此、图翼如何解」，二者并观方见全貌。

## 二、跨书取证走 RAG（asset1/2/4/5/10/14）
需要跨书原文出处、岁运病机现代化解读、临床医案佐证时，调项目既有 RAG（`scripts/rag_search.py`）：
- `asset1`（岁运病机）、`asset2`（司天在泉）、`asset4`（方剂）、`asset5`（历代注家）、`asset10`（治法）、`asset14`（医案）。
- 例如答「甲己为何化土」：本 skill 给五天五运图解与推原南北政说（ch03/ch06），RAG 拉出 asset5 历代注家与 asset1 岁运病机佐证。

## 三、统一入口（已注册 asset37）
本蒸馏已注册为 `asset37_liejing_tuyi_yunqi`，统一入口 key 为 `liejing_*`：
- `liejing_xiangshu`（象数基础）、`liejing_wuyun`（五运）、`liejing_liuqi`（六气）、`liejing_tianfu`（天符岁会）、`liejing_nanbei`（南北政）、`liejing_zonglun`（总论）。
- 可直接 `rag_search --key liejing_*` 稳定命中（各 1 条，100% 精确键）；路由 `routing id: liejing-tuyi-yunqi` 已并入 `routing.yaml`，并与 asset34 / asset35 / asset36 同列默认检索范围。

## 四、与 asset34 / asset35 / asset36 双轨/多轨衔接
| 轨道 | 资产 | 用途 |
|------|------|------|
| 图翼·象数基础层（本书） | asset37 | 象数根基 + 图翼推算细节（五音建运、南北政脉不应） |
| 方源层 | asset36（三因） | 十六方组成/分量/主治/煎服 |
| 歌诀层 | asset34（王旭高） | 十干运方、六支气方、六淫治例方歌 |
| 推算框架广度层 | asset35（医宗金鉴） | 太极阴阳、五运六气、天符岁会、南北政体例广度 |

**多轨读法示例**：先用 asset35 / 通用推算推当年格局 → 用 asset37 补象数根基与图翼细节 → 用 asset34 取方歌助记诵 → 用 asset36 取原方组成 → 用 RAG（asset1/2/4/5/10/14）补跨书病机与医案。四书 + RAG 互补，非替代；任何落地到人的健康决定交执业中医师。

> 本章仅供文献研读，禁止据此自行诊断、开方或用药，须咨询执业中医师。
