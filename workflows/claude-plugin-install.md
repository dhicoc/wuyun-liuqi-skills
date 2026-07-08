# Claude Code 插件安装工作流

> 当用户要求通过 Claude Code 插件市场安装本技能包时执行。

## 触发示例

- 「用 Claude Code 插件安装五运六气技能包」
- `/plugin install wuyun-liuqi-skills`
- 「把这个仓库加成 Claude Code 插件」

## 方式一：插件市场（推荐）

在 Claude Code 中执行：

```text
/plugin marketplace add dhicoc/wuyun-liuqi-skills
/plugin install wuyun-liuqi-skills@wuyun-liuqi-skills
```

更新：

```text
/plugin marketplace update
```

插件清单：`.claude-plugin/marketplace.json`、`.claude-plugin/plugin.json`。

## 方式二：全局技能链接（Cursor / 任意项目常驻）

```bash
python scripts/install.py --link-global
python scripts/health_check.py
python tests/verify_expansion.py
```

链接目标：

- `~/.claude/skills/wuyun-liuqi-skills/`
- `~/.cursor/skills/wuyun-liuqi-skills/`

## 方式三：在本仓库内使用

用 Claude Code / Cursor **打开** `wuyun-liuqi-skills` 文件夹即可；`CLAUDE.md` 与 `.claude/skills/wuyun-liuqi/SKILL.md` 会自动引导到 `SKILL.md`。

## 安装后确认

1. 对 Agent 说「五运六气」或「今天运气如何」
2. Agent 应读取 `SKILL.md` → 匹配 `routing.yaml` → 调用 `scripts/calculate_yunqi_api.py`
3. 运行 `python scripts/check_routing_scenarios.py` 确认路由场景通过

## 向用户报告模板

```text
✅ 五运六气技能包已安装
✅ 激活方式：<插件 / 全局链接 / 打开本文件夹>
✅ 验证：health_check + verify_expansion + routing_scenarios
下一步：直接问「今天运气怎么样」或「帮我学客主加临」
```