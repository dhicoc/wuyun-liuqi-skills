# 一句话安装工作流（AI 执行）

> 当用户粘贴仓库地址并要求「完整安装」时，按本流程执行。不要只装 pip 就结束。

## 触发示例

```
仓库地址：https://github.com/dhicoc/wuyun-liuqi-skills.git
请帮我把这个五运六气技能包完整安装好（包含所有依赖和验证）。
```

## 执行步骤

### 1. 获取代码

```bash
git clone https://github.com/dhicoc/wuyun-liuqi-skills.git
cd wuyun-liuqi-skills
```

若用户已在该仓库内，跳过 clone，记当前目录为 `<SKILL_ROOT>`。

### 2. 环境安装 + 全局注册（推荐）

```bash
python scripts/install.py --link-global
python scripts/health_check.py
python tests/verify_expansion.py
```

`--link-global` 会自动将本仓库链接到：

- `~/.claude/skills/wuyun-liuqi-skills/`
- `~/.cursor/skills/wuyun-liuqi-skills/`

用户无需手动 `mklink` / `ln -sf`。若链接已存在且指向错误路径，使用 `--link-global --force`。  
若提示「拒绝访问」，先关闭 Claude Code / Cursor 再重试（旧目录可能是完整 git 副本且文件被占用）。

仅装环境、不全局注册时：`python scripts/install.py`（场景 A：打开本文件夹使用）。

### 3. 确认薄壳就绪（P0 后必做）

检查以下文件存在（均在 `<SKILL_ROOT>` 内）：

- `SKILL.md`、`routing.yaml`
- `AGENTS.md`、`CLAUDE.md`
- `.cursor/skills/wuyun-liuqi/SKILL.md`

无需手改薄壳内容；它们会自动引导到 `SKILL.md` + `routing.yaml`。

### 4. Claude Code 插件（可选，场景 C）

```text
/plugin marketplace add dhicoc/wuyun-liuqi-skills
/plugin install wuyun-liuqi-skills@wuyun-liuqi-skills
```

详见 `workflows/claude-plugin-install.md`。

### 5. 按使用场景注册（二选一）

**场景 A — 在本仓库内使用（推荐新手）**

- 用 Cursor / Claude Code **直接打开** `wuyun-liuqi-skills` 文件夹作为工作区
- 薄壳自动生效：`CLAUDE.md` / `AGENTS.md` / `.cursor/rules/wuyun-liuqi.mdc`
- 用户在此工作区对话即可

**场景 B — 在任意项目里使用（推荐常驻，默认）**

```bash
python scripts/install.py --link-global
```

自动链接到 Claude / Cursor 全局技能目录。用户可在**任意项目**对话，提到「五运六气」等触发词即可激活。

手动备用（仅当 `--link-global` 失败时）：

| 平台 | 目标路径 |
|------|----------|
| Claude Code | `~/.claude/skills/wuyun-liuqi-skills/` |
| Cursor | `~/.cursor/skills/wuyun-liuqi-skills/` |

### 5. 向用户报告（必须包含）

```
✅ 代码已就绪：<SKILL_ROOT>
✅ Python 依赖：lunar-python
✅ 推算验证：calculate_yunqi_api.py today --summary
✅ 结构验证：verify_expansion.py 通过
✅ 激活方式：<场景 A 或 B 的具体说明>
```

附一句试用：「你可以直接问：今天运气怎么样？」

## 常见误区

| 误区 | 后果 | 正确做法 |
|------|------|----------|
| 只 `pip install` 不 clone | 无 SKILL/routing/脚本 | 必须 clone 完整仓库 |
| clone 到别的项目子目录但不注册 | 跨项目对话时技能不激活 | 场景 B 全局注册，或场景 A 打开该文件夹 |
| 手抄规则到 CLAUDE.md | 规则漂移 | 用薄壳/全局技能指向本包，不复制正文 |