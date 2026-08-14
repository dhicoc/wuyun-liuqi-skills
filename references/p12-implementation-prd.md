# P12 实施 PRD · 与 `huangdi-neijing-skill` 功能级集成

> 状态：草稿（待审核）
> 依据：`references/roadmap.md` P12 条目 + 2026-08-14 对外部仓库的实地核查
> 关联：P8-1（已完成，仅交叉引用）→ P12 把静态映射升级为 runtime 联动

---

## 0. 审核摘要（先读这段）

外部仓库 `kangarooking/huangdi-neijing-skill` **真实可用、MIT、22 个 skill、结构优于预期**（每个 SKILL.md 带机器可读 `related_skills` YAML frontmatter，步骤为 R/I/A1/A2/E/B 六维）。P12 技术上完全可行。

但 roadmp P12 当前描述有 **2 处事实错误 + 1 处重大安全缺口**，本 PRD 已据实修正：

| # | roadmap 原文 | 实测事实 | PRD 修正 |
|---|---|---|---|
| 偏差1 | `npx skills add --skill <name>` 单装 | 仓库无任何 npx 机制，真实分发=克隆 + 读 `*/SKILL.md` | 改为「路径检测 + glob」，不依赖 npx |
| 偏差2 | 拼装其 `R/I/A/E` 步骤 | 实际是 `R/I/A1/A2/E/B` 六维 | bridge 解析全部六节，重点用 I/E/B |
| 缺口3 | （未提安全） | 灵枢多个 skill 涉针刺/临床决策 | **强制套用本项目 `_safety_text` 三件套 + 拒诊拒方红线** |

---

## 1. 背景与目标

### 1.1 背景
- P8-1 已完成「`teaching-modules/相关思维工具.md`：10 教学模块 ↔ 22 思维工具」的**静态交叉引用**，但运行链路里运气推算与内经方法论**没有真正联动**。
- 自进化盲区信号 + 2026-08-13 生态调研（`research-2026-08-13.md` §4）确认：`huangdi-neijing-skill` 与运气链高度互补（运气给「时空格局」，内经给「方法论框架」）。

### 1.2 目标
在 runtime 层打通两者，形成「**内经方法论 + 运气推算**」完整中医 Agent 能力栈：
- 输入「运气格局 + 体质/病证」→ 自动选 top-N 内经 skill → 拼装其方法论为报告「内经方法论」章节。
- 外部仓库为**可选依赖**，未安装时优雅降级，不阻塞主流程、不引入硬依赖。

### 1.3 非目标（明确不做）
- 不引入 `huangdi-neijing-skill` 的工具链（darwin-skill / cangjie-skill）。
- 不照搬/重分发其原文内容到 RAG（仅按需读取 SKILL.md 文本、保留其章节出处引用）。
- 不把内经内容当作医学建议或开方/针刺指令（见 §6 安全红线）。
- 不做真实 embedding 语义检索（沿用本项目 n-gram/字段精确匹配选型）。

---

## 2. 外部仓库核查事实（2026-08-14 实测）

| 项 | 结论 |
|---|---|
| 仓库 | `github.com/kangarooking/huangdi-neijing-skill`，默认分支 `main`，公开 |
| 许可证 | MIT（README + LICENSE 声明；可 vendored / 再分发） |
| 规模 | 22 skills = 素问 12 + 灵枢 10；`suwen/*/SKILL.md`、`lingshu/*/SKILL.md` |
| 每个 SKILL.md 结构 | YAML frontmatter（`name`/`description`/`source_book`/`source_chapter`/`tags`/`related_skills`）+ 六节 `## R/I/A1/A2/E/B` |
| `related_skills` | **机器可读**：`[{slug, relation}]`，relation ∈ `depends-on`/`composes-with`/`contrasts-with` |
| INDEX.md | 含 mermaid 关系图（同三类 relation）+ 推荐学习顺序 |
| 维护状态 | ⚠️ 仅 1 commit（2026-04-18），`cangjie-skill` RIA-TV++ AI 蒸馏，之后无更新 |
| 测试格式 | 每 skill 带 `test-prompts.json`（darwin-skill 兼容，本包不直接用） |

**已确认存在的 22 个 slug**（供映射表引用）：
- 素问(12)：`yin-yang-balance` `five-elements-network` `negative-feedback` `biao-ben-priority` `zheng-xie-assessment` `context-adaptation` `prevention-strategy` `cascade-prediction` `seasonal-regimen` `five-flavors-balance` `emotion-organ-proxy` `observation-inference`
- 灵枢(10)：`qi-regulation` `excess-deficiency-decision` `root-cause-priority` `observe-infer` `four-seas-regulation` `bottleneck-unblock` `timing-opportunity` `personalize-by-constitution` `body-mind-integration` `communicate-persuade`

---

## 3. 架构设计

### 3.1 新增模块 `scripts/neijing_bridge.py`

纯函数、零外部依赖（只依赖标准库 `re`/`pathlib`/`yaml`；`yaml` 走项目已有托管环境）。

```
neijing_bridge.py
├─ discover_neijing_skills(root_dir) -> dict[slug, NeijingSkill]
│     glob "**/SKILL.md" → 解析 frontmatter + 六节文本
├─ neijing_available() -> bool
│     检测 HUANGDI_NEIJING_SKILL_DIR 或默认克隆路径
├─ select_skills(yunqi_ctx, skills, top_n=3) -> list[SelectedSkill]
│     yunqi 维度 → 映射表加权 → related_skills 展开 → 排序取 top-N
└─ build_methodology_section(selected, with_safety=True) -> str
      拼装 Markdown「## 内经方法论」：每 skill 取 I(框架)+E(步骤)+B(边界)
      + 章节出处引用 + 临床类强制 _safety_text 三件套
```

### 3.2 数据模型
```python
@dataclass
class NeijingSkill:
    slug: str
    name: str
    source_book: str
    source_chapter: str
    tags: list[str]
    related: list[tuple[str, str]]   # (slug, relation)
    sections: dict[str, str]          # {"R":..., "I":..., "A1":..., "A2":..., "E":..., "B":...}

@dataclass
class SelectedSkill:
    skill: NeijingSkill
    weight: float
    reason: str          # 为何被选中（回链到运气维度，供报告解释）
```

### 3.3 集成点
- `yunqi_report.py`：`generate_report()` 新增 `with_neijing_methodology: bool = True` 形参；在「知识库/RAG 章节」之后、「临床安全提示」之前插入方法论章节（保证三件套免责包裹全部内容）。
- `personal_yunqi_profile.py`：`generate_profile()` 同理，在体质章节后追加。
- CLI：`--neijing` / `--no-neijing` 强制开/关（默认自动：可用则开）。

---

## 4. yunqi → neijing 映射表（初版草案）

输入来自运气包已算出的维度：岁运(五行+太过/不及)、司天、在泉、主气、运气相合、体质倾向、病证（可选）。

**A. 框架/调养类（默认纳入）**

| 运气维度 | 命中 slug | 权重 | 选择理由 |
|---|---|---|---|
| 火运 / 火不及 / 君相火 | `yin-yang-balance` | 高 | 阴虚则补阳、阳亢则制阳 |
| 任意五行 + 运气相合 | `five-elements-network` | 高 | 生克链推导系统连锁 |
| 金 / 阳明燥金在泉 | `emotion-organ-proxy` | 中 | 悲忧属肺；`five-elements-network` |
| 木 / 厥阴风木司天 | `cascade-prediction` | 中 | 木克土传变预判；`emotion-organ-proxy`(怒/肝) |
| 土运 / 太宫 | `five-flavors-balance` | 中 | 甘入脾；`five-elements-network` |
| 水 / 少阴 / 太阳 | `seasonal-regimen` | 中 | 冬藏；`yin-yang-balance` |
| 体质倾向·阴虚 | `yin-yang-balance` | 高 | 阴虚阳亢 |
| 体质倾向·阳虚 | `seasonal-regimen` + `prevention-strategy` | 高 | 养藏/治未病 |
| 体质倾向·土运防五脏 | `five-elements-network` + `five-flavors-balance` | 中 | 五脏乘侮防护 |
| 情志/压力信号 | `emotion-organ-proxy` + `body-mind-integration` | 中 | 情志脏腑 + 形神合一 |
| 时序/时机诉求 | `timing-opportunity` + `prevention-strategy` | 中 | 时机选择 + 欲病早治 |
| 个体化方案 | `personalize-by-constitution` + `context-adaptation` | 中 | 因人施术 + 因地制宜 |
| 观察推断需求 | `observation-inference` | 中 | 以外测内 |

**B. 临床/针刺类（默认排除或仅框架层，需最强免责）**

| slug | 处理 |
|---|---|
| `qi-regulation` `excess-deficiency-decision` `root-cause-priority` `four-seas-regulation` `observe-infer`（临床用法） | **默认不进入映射**；若用户显式问「针刺/治法」，仅输出其 I(框架) 与原文 R 段，剥离 E(可执行针刺步骤)，并强制 `_safety_text` 三件套 + 拒诊拒方 |

> 映射表落地为 `scripts/neijing_bridge.py` 内的 `YUNQI_NEIJING_MAP`（权重 + reason 模板），便于回归测试与人工校准。

---

## 5. 可选依赖与优雅降级

- **检测**：`neijing_available()` 依次检查
  1. 环境变量 `HUANGDI_NEIJING_SKILL_DIR`（用户自定义路径）
  2. 默认路径 `<repo>/.neijing/huangdi-neijing-skill`（见 §7 供给方式）
- **未安装时**：`with_neijing_methodology` 自动关闭，报告照常生成（核心能力零降级）；可选输出一行提示「内经方法论模块未安装，详见 README」。
- **解析失败/单文件损坏**：单个 SKILL.md 解析异常不影响整体，记日志跳过该 skill。
- **绝不**：因 neijing 缺失/异常导致运气主流程报错或退出非 0。

---

## 6. 安全红线（roadmap 缺失项，本 PRD 强制）

复用本项目单一权威源 `scripts/_safety_text.py`（DISCLAIMER / CLINICAL_SAFETY_NOTICE / EMERGENCY_NOTICE），**不重新硬拷贝文案**。

- **MUST**：`build_methodology_section()` 输出的任何含「临床/针刺/方药」语义的内容，末尾必须附三件套（与 `yunqi_report.py` practitioner 报告一致）。
- **MUST**：当命中 §4-B 临床/针刺类 skill，或用户话术涉及开方/针刺/治法时：
  - 仅保留框架层（I 段 + 原文 R 段章节引用），**剥离 E 段的可执行针刺/操作指令**；
  - 强制 `_safety_text.CLINICAL_SAFETY_NOTICE` + `EMERGENCY_NOTICE` + `DISCLAIMER`；
  - 触发与现有 R5「拒诊拒方」相同的拦截逻辑（不输出具体方/穴）。
- **SHOULD**：方法论章节开头标注「以下为《黄帝内经》方法论框架参考，非医学诊断/治疗建议，具体诊疗须执业中医师辨证论治」。
- **MAY**：保留 neijing SKILL.md 自带的 B(边界) 段（其已含「不替代专业医疗」等声明），与本项目声明互补。

---

## 7. 外部内容供给方式（待定：二选一）

| 方案 | 优点 | 缺点 | 建议 |
|---|---|---|---|
| **A. git submodule** | 跟踪上游、更新方便 | CI 需 `submodule update`；上游单 commit 无意义；嵌套仓库增加复杂度 | 次选 |
| **B. vendored 快照**（推荐） | 零网络依赖、CI 稳定、内容可控、可锁定 commit 哈希 | 需手动同步；占仓库空间（仅 SKILL.md 文本，极小） | **首选** |

- 推荐 B：将初始需要的 SKILL.md 快照置于 `scripts/lib/neijing_snapshot/`（或 `references/neijing-vendored/`），并在文件头注释锁定源 commit `17106a2`；提供 `scripts/sync_neijing_snapshot.py`（可选）从上游拉取更新。
- 无论 A/B，`neijing_available()` 都能找到内容；用户也可设 `HUANGDI_NEIJING_SKILL_DIR` 指向自己克隆的源仓库（实时读取，覆盖快照）。

---

## 8. 测试策略

- **单元测试** `tests/test_neijing_bridge.py`（**不依赖外部网络**，用 vendored 快照 / fixtures）：
  - `discover_neijing_skills` 解析 fixture → 断言 frontmatter + 六节齐全；
  - `select_skills` 给定固定 yunqi_ctx → 断言 top-N slug 集合符合映射表；
  - `build_methodology_section` → 断言含章节出处引用 + （临床类）含 `_safety_text` 三件套关键词；
  - `neijing_available()` 在缺失环境下返回 False 且不抛错。
- **集成用例（条件跳过）**：`full_regression_test.py` 新增 `neijing methodology`（仅当 `neijing_available()` 时运行；CI 用 vendored 快照故默认跑）。
- **回链断言**：验证「运气结论 → 回链到内经方法论条目」可稳定复现（同输入同输出）。
- **安全回归**：临床类 skill 被选中时，断言输出**不含**具体穴位/方剂操作、且含三件套。

---

## 9. 分阶段实施计划与验收

- **阶段 0 · 修正 roadmap**：把 P12 的 `npx skills add`→「路径检测」、`R/I/A/E`→`R/I/A1/A2/E/B`、补「临床安全红线」一条。（验收：roadmap 文案与本节一致）
- **阶段 1 · 只读解析器**：`neijing_bridge.py` 的 `discover_neijing_skills` + `neijing_available` + 数据模型。（验收：单元测试解析 fixture 通过）
- **阶段 2 · 映射与选择**：`YUNQI_NEIJING_MAP` + `select_skills`（含 related_skills 展开）。（验收：给定 yunqi_ctx 选 slug 符合映射表）
- **阶段 3 · 章节拼装 + 安全**：`build_methodology_section` + `_safety_text` 集成 + 临床类剥离。（验收：含出处引用；临床类含三件套且无操作指令）
- **阶段 4 · 报告集成 + 降级**：接入 `yunqi_report` / `personal_yunqi_profile` + CLI 开关 + 优雅降级。（验收：neijing 缺失时主流程零报错）
- **阶段 5 · 供给 + 测试 + CI**：vendored 快照（或 submodule）+ `tests/test_neijing_bridge.py` + full_regression 条件用例 + CI 绿。

---

## 10. 验收标准（交付定义）

1. `python scripts/neijing_bridge.py --selftest` 或等价单测全绿。
2. `yunqi_report.py 2026 --audience practitioner` 在 neijing 可用时输出含「## 内经方法论」章节，且免责声明完整。
3. 外部仓库缺失/损坏时，上述命令退出码 0、核心报告不变、仅少一章。
4. 临床类 skill 触发时，输出无具体针刺/开方指令、含三件套。
5. CI 全矩阵（Py3.10/3.11/3.12 × Node18/20/22）绿，无新增硬依赖。

---

## 11. 风险与缓解

| 风险 | 等级 | 缓解 |
|---|---|---|
| 外部仓库消失/改结构 | 中 | vendored 快照 + `neijing_available()` 降级；锁定 commit `17106a2` |
| 内经内容为 AI 蒸馏、非人工校勘 | 中 | 保留其原文章节出处引用；明确标注「补充框架非医疗建议」；不混入 RAG 知识库 |
| 误把内经内容当医疗建议 | 高 | §6 强制三件套 + 临床类剥离 + 复用 R5 拒诊拒方 |
| 引入硬依赖/网络耦合 | 中 | 零硬依赖；vendored 快照；可选 env 覆盖 |
| 映射表不准导致选错 skill | 低 | 映射表单测 + reason 回链可解释；related_skills 展开降误 |
| roadmap 描述误导实施 | 低 | 阶段 0 先修正（见 §0） |

---

## 12. 待你确认的开项（Open Questions）

1. **供给方式**：vendored 快照（推荐）还是 git submodule？
2. **默认 top-N**：3 是否合适？还是 2 / 4？
3. **初始 skill 范围**：§4-A 框架/调养类全纳入？§4-B 临床/针刺类默认排除是否合理？
4. **报告位置**：方法论章节放「知识库章节之后、临床安全提示之前」是否可接受？
5. **版本节奏**：P12 完成后是否打 tag（0.4.0）？还是保持「仅提交」惯例（同 P11）？
6. **是否先落阶段 0**（修正 roadmap 三处）再开工？

---

## 附：与现有 red-line 的对齐

本 PRD 的 §6 与项目既有 MUST/SHOULD/MAY 三级免责体系一致；`neijing_bridge` 不新增声明文案，全部复用 `_safety_text.py`。临床类 skill 的「剥离 E 段 + 拒诊拒方」直接复用 `clinical_safety.py` 的守卫逻辑（与 R2 病机方 / R5 拒诊拒方同源）。
