# 新增子技能指南

> 本指南说明如何为五运六气技能包新增子技能。改编自 reverse-skill 的 CONTRIBUTING.md。

## 目录结构模板

新增子技能时，按以下结构创建：

```
<skill-name>/
├── SKILL.md              # 必需：子技能入口
├── scripts/              # 可选：推算脚本（如有）
│   └── *.py
└── references/           # 可选：参考文档
    └── *.md
```

## SKILL.md 必需段落

每个子技能的 SKILL.md MUST 包含以下段落：

### 1. YAML Frontmatter

```yaml
---
name: <skill-name>
description: >
  一句话描述。MUST 包含触发词（用户可能说的关键词）。
---
```

### 2. 标题与适用范围

```markdown
## <技能名称>

### 适用范围
- 功能1
- 功能2
```

### 3. 依赖声明

推算层子技能：
```markdown
### 脚本依赖
| 脚本 | 用途 | 必需 |
|------|------|------|
```

病机/临床层子技能：
```markdown
### 前置依赖
MUST 先完成 yunqi-calc 推算获取运气格局。
```

文献层子技能：
```markdown
### 工具依赖
无（纯文献检索）
```

### 4. 推荐工作流

```markdown
### 推荐工作流
#### Step 1/N: <步骤名>
ACT: <具体操作>

#### Step 2/N: <步骤名>
ACT: <具体操作>
```

### 5. 常见误区

```markdown
### 常见误区
| 问题 | 原因 | 解决方案 |
|------|------|----------|
```

### 6. 输出要求

```markdown
### 输出要求
- MUST 包含的内容
- SHOULD 包含的内容
```

### 7. 路由上下文

```markdown
### 路由上下文
**上游入口**: <来源模块>
**下游出口**: <去向模块>
**同级关联**: <关联模块>
```

### 8. ACTION REQUIRED 与自检

```markdown
---

## ACTION REQUIRED
- [ ] 必查项1
- [ ] 必查项2

## 任务完成自检
- [ ] 自检项1
- [ ] 自检项2
```

## 集成步骤

新增子技能后，MUST 更新以下文件：

1. **`SKILL.md`**（总控）: 在模块总表中添加新模块
2. **`routing.md`**（路由）: 在对应轴添加路由条目
3. **`case-journal/_index.md`**: 如涉及新的医案分类，添加索引条目

## 脚本规范（如需新增推算脚本）

1. 脚本 MUST 放在 `scripts/` 目录下
2. 共享数据 MUST 从 `scripts/lib/yunqi_data.py` 导入
3. 脚本 MUST 支持 `--json` 参数输出 JSON 格式
4. 脚本 MUST 有 `--help` 或用法提示
5. 脚本 MUST 能独立运行（不依赖其他脚本运行结果）

## 文档规范

1. 所有 Markdown 文件使用 UTF-8 编码
2. 中文内容，技术术语可保留英文
3. 表格使用 Markdown 标准格式
4. 引用素问原文时 MUST 标注篇名
5. 引用历代医家时 MUST 标注作者+书名

## 验证清单

新增子技能后，逐项检查：

- [ ] SKILL.md 包含全部 8 个必需段落
- [ ] YAML frontmatter 的 name 和 description 正确
- [ ] 路由已在 routing.md 中注册
- [ ] 模块已在 SKILL.md 总控表中登记
- [ ] 脚本（如有）能独立运行并输出正确结果
- [ ] 参考文档（如有）内容完整且有交叉引用
- [ ] 常见误区表至少 3 行
- [ ] ACTION REQUIRED 和自检块包含 checkbox
