# 更新日志

## 2026-07-08（晚④）- P3 sync-routing + conformance + 孤儿审计

### 路由同步（单一真相源 → 生成块）
- **`scripts/sync_routing.py`**：`routing.yaml` → `SKILL.md` / `routing.md` 标记块（`--check` / `--write`）
- **`routing.yaml` → `skill_sync.common_tasks`**：Common Tasks 列表配置化
- **`scripts/lib/routing_manifest.py`**：共享 YAML 解析

### 质量门禁
- **`conformance.yaml`** + **`scripts/check_conformance.py`**：关键段落/文件必达
- **`scripts/audit_orphans.py`**：`rules/` / `workflows/` / `references/` 零引用审计

### CI
- 新增 sync-routing、conformance、audit_orphans 步骤

---

## 2026-07-08（晚③）- P2 Claude Code 插件 + Agent 路由场景测试

### Claude Code 插件化
- **`.claude-plugin/`**：`plugin.json`、`marketplace.json`
- **`workflows/claude-plugin-install.md`** + `routing.yaml` → `tasks/claude-plugin-install`

### Agent 场景测试
- **`tests/routing_scenarios.json`**：13 条任务路由 + 模糊意图 + 2 条 cross_path
- **`scripts/check_routing_scenarios.py`**：用户话术 → task → 脚本/工作流/文件存在性
- CI 与 `check_skill_structure.py` 联动

---

## 2026-07-08（晚②）- P1 规则分层 + 结构校验 + 任务闭环

### 规则工程
- **`rules/`**：`medical-safety`、`calculation`、`agent-behavior`、`output`
- **`RULES.md`** 改为索引；细则不再堆叠在单文件
- **`references/gotchas.md`** + **`workflows/task-closure.md`**

### 自进化闭环
- `self_evolve.py rule-gap`：记录规则/路由盲区 → 月度报告 `rule_gaps` 节

### 校验
- **`scripts/check_skill_structure.py`**：薄壳、routing 引用、行数预算
- CI 新增结构检查步骤

---

## 2026-07-08（晚）- P0 技能架构 + 一句话安装全局注册

### 技能工程（对齐 skill-based-architecture）
- **瘦身 `SKILL.md`**（≤90 行）：仅保留路由入口；安装/契约/脚本表迁至 `workflows/`、`references/`
- **`routing.yaml`**：路由单一真相源；`routing.md` 改为人类可读索引
- **跨工具薄壳**：`AGENTS.md`、`CLAUDE.md`、`CODEX.md`、`GEMINI.md`、`.cursor/rules/`、`.cursor/skills/`、`.claude/skills/`
- **新增** `workflows/one-line-install.md`、`workflows/routing-contract.md`、`references/script-index.md`、`references/module-index.md`

### 安装
- **`install.py --link-global`**：自动链接到 `~/.claude/skills/wuyun-liuqi-skills` 与 `~/.cursor/skills/wuyun-liuqi-skills`
- **`--force`**：覆盖错误旧链接/目录；权限占用时提示关闭 Claude/Cursor 后重试
- 一句话安装话术与 `routing.yaml` → `tasks/one-line-install` 已同步

### 文档
- 已更新：`README.md`、`README_AI.md`、`README_for_humans.md`、`workflows/`、`setup.bat`/`setup.sh`、`CONTRIBUTING.md`、`tests/verify_expansion.py`

---

## 2026-07-08 - 文档全面对齐 + 安装体验优化 + 功能增强

本次更新重点完成了项目文档与实际功能的完全对齐，并大幅优化了用户（尤其是直接把仓库地址丢给 AI）的安装体验，同时增强了核心“帮助人类通过 Agent 理解运气学思想”的能力。

### 新增功能
- **思想导出功能**（重大新增）
  - 新增 `scripts/export_thought.py`
  - 支持三种导出格式：
    - `summary`：纯文本思想摘要（聚焦哲学解读、现代比喻、反思问题）
    - `cards`：Anki 卡片集（.anki.tsv + 可读 .md）
    - `pdf` / `all`：高质量可打印 HTML（推荐浏览器打印为 PDF）+ 可选 fpdf2 直接 PDF
  - 在主入口 `calculate_yunqi_api.py` 中集成 `--export` 参数
- **一键 / 一句话安装优化**
  - 新增 `scripts/install.py`（专门为 AI 引导安装设计）
  - 支持直接把仓库地址丢给 AI 即可完成安装
  - 优化 `setup.bat` / `setup.sh`，安装后推荐运行 install.py 做最终确认
- **渐进式学习与概念解释**
  - `calculate_yunqi_api.py` 新增 `--level simple|standard|deep`
  - `--explain-concept "天人合一"` 支持哲学 + 现代 + 示例
- **自进化系统大幅增强**
  - 支持 `concepts` 参数（哲学概念追踪，如“思想层解读”“天人合一”）
  - 隐私保护：`session_id` 默认 SHA256 哈希（前 16 位），comment/context 自动 PII 清洗（邮箱、电话等）
  - `anonymize=True` 默认开启
  - 新增 `cleanup_old_data`、理解反馈类型、会话统计、概念演进追踪
  - 报告中自动生成基于理解质量的改进建议

### 文档全面对齐
- **所有主要文档已与项目现状完全同步**（消除文档与实现不一致问题）：
  - README.md（中英双语）
  - README_AI.md
  - SKILL.md + docs-generator/SKILL.md
  - README_for_humans.md（新增并完善）
  - routing.md、prompts/onboarding_prompt.md
  - docs/ 系列：
    - function-coverage.md
    - architecture.md
    - roadmap.md
    - optimization.md
    - ux_optimization.md
    - self_evolve_optimization.md
    - understanding_the_thought_optimization.md
    - SAG_INTEGRATION_EVALUATION.md
  - self-evolve/README.md
  - agent-workflow/self_evolve_hook.md
- 所有“待开始”状态已更新为实际完成状态
- 测试数据统一为：full_regression 63/0，verify_expansion 75/0
- 强化定位语言：“帮助人类通过 Agent 深入理解运气学思想体系”

### 用户体验与安装改进
- `calculate_yunqi_api.py` 改用 argparse，提供优秀 `--help`
- 默认支持 `today`（或无参数即今天）
- 所有主要输出末尾增加“下一步建议”和引导性反思问题
- 终端输出支持 ANSI 颜色高亮（太过/不及、相得/不相得等）
- onboarding 机制优化，对模糊意图先进行思想引导
- 健康检查和 setup 脚本增加更清晰的行动引导

### 其他改进
- 新增 `scripts/_common.py`（统一 UTF-8 和路径处理，消除样板代码）
- 新增 `scripts/smoke_full_chain.py`
- 更新 `scripts/lib/yunqi_constants.json`
- 大量脚本进行一致性优化和 bug 修复
- 报告快照更新以匹配思想层解读内容
- 自进化现在默认过滤测试数据 + 去重

### 测试验证
- full_regression_test.py：**63 通过，0 失败**
- verify_expansion.py：**75 通过，0 失败**
- smoke_full_chain 多次随机全链路通过

### 安装方式（现已极简）
用户可直接把仓库地址丢给 AI：
```
仓库地址：https://github.com/dhicoc/wuyun-liuqi-skills.git

请帮我把这个五运六气技能包完整安装好...
```
AI 会引导完成克隆 → `python scripts/install.py` → 验证 → 可用。

---

所有更改已推送到 `https://github.com/dhicoc/wuyun-liuqi-skills`

本次更新使项目在“文档一致性”和“普通用户 / AI 辅助安装”两个维度上达到了较高可用性，同时进一步强化了“思想理解”而非仅“推算”的核心定位。