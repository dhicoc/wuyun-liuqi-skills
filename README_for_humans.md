# 五运六气技能包 — 给普通人的使用指南

> **一句话说明**：把这个文件夹给你的 AI（Claude、Cursor、Windsurf 等），它就能帮你真正理解“五运六气”这个古老的思想体系。

## 这是什么？

五运六气是《黄帝内经》里关于“天时如何影响人和气候”的深刻思想。它不是简单的算命，而是古人观察宇宙、时间、生命之间关系的智慧。

本技能包的作用是：**让你的 AI 成为一位靠谱的运气学老师**，而不是靠记忆或猜来回答。

当你问：
- “五运六气到底是什么思想？”
- “今年运气对我养生有什么启发？”
- “我出生那年的运气格局代表什么？”
- “最近天气和运气怎么对应？”

你的 AI 会调用本技能包进行准确推算 + 经典知识检索 + 思想解读。

---

## 如何安装（超级简单）

### 方法一：直接把仓库地址丢给 AI（推荐，最接近一句话安装）

把下面**内容**直接复制给 Claude（推荐）：

```
仓库地址：https://github.com/dhicoc/wuyun-liuqi-skills.git

请按 workflows/one-line-install.md 帮我把这个五运六气技能包完整安装好（包括思想层解读、导出卡片、self-evolve 等全部功能）。

执行流程：
1. git clone 仓库并进入目录。
2. 运行：python scripts/install.py --link-global
   （自动装依赖 + 注册到 Claude/Cursor 全局技能目录，之后任意项目都能用）
3. 验证：python scripts/health_check.py && python tests/verify_expansion.py
4. 若全局链接失败，用 --link-global --force；仍失败见 one-line-install.md 手动备用步骤。
5. 确认可用后，给我 3 个可以直接问你的使用示例（要包含思想层和导出）。
```

这样基本可以实现“直接丢仓库地址 + 一段话 → AI 引导完成安装 + 验证 + 可用”。

### 方法二：传统手动方式（依然很简单）

```bash
git clone https://github.com/dhicoc/wuyun-liuqi-skills.git
cd wuyun-liuqi-skills
```

然后在 AI 对话框里复制下面这段话：

```
请帮我准备五运六气技能包环境。
项目路径是： [把你刚才克隆的文件夹完整路径粘贴在这里]

请运行：
Windows: powershell -File scripts\setup.bat
macOS/Linux: bash scripts/setup.sh

运行完后告诉我结果，并确认已准备好使用。
```

AI 会自动帮你安装依赖（主要是 `lunar-python`）。

### 3. 开始对话

安装好后，直接用自然语言提问即可：

- “今天运气怎么样？”
- “帮我讲讲五运六气背后的思想”
- “2026年是丙午年，运气格局有什么特点？”
- “我1990年出生，运气和体质有什么关系？”

---

## 推荐提问方式（让 AI 更好地帮助你理解思想）

### 入门类
- “五运六气是什么？核心思想是什么？”
- “天人合一是如何通过运气学体现的？”
- “运气学的时间观和现代日历有什么不同？”

### 应用类
- “今年运气如何指导养生？”
- “我这个月要注意什么？用运气角度解释一下”
- “出生年份的运气格局，对性格或健康倾向有什么启发？”

### 导出与复习类（新）
- “导出今年运气的思想摘要和 Anki 卡片集”
- “生成可打印的思想层报告（PDF/HTML）”

### 深入类
- “请用简化版解释司天在泉，然后再给我深入版”
- “这个格局体现了什么宇宙观和生命观？”
- “把‘天符’这个概念和现代比喻连起来讲讲”

---

## 常用功能速查（给 AI 用）

你的 AI 可能会用到下面这些命令（你不用自己跑）：

- 快速了解今天/某天 + 思想解读：`python scripts/calculate_yunqi_api.py today --summary --level deep`
- 概念哲学 + 导出复习：`python scripts/calculate_yunqi_api.py today --explain-concept "天人合一"` 或 `export_thought.py today --format all`（思想摘要 + 卡片 + PDF/HTML）
- 完整报告：`python scripts/yunqi_report.py 2026 --audience student`
- 个人分析：`python scripts/personal_yunqi_profile.py 1990-05-20 北京`
- 查看自进化理解进展：`python scripts/self_evolve.py report` / `stats`

---

## 注意事项

- 这是一个**思想学习与理论参考工具**，不是医疗诊断系统。
- 所有输出都会带有免责声明，请理性看待。
- 本技能包会持续通过使用反馈自我进化，解释质量会越来越好。

---

## 下一步

把这个文件和整个 `wuyun-liuqi-skills` 文件夹一起给你的 AI，然后说：

> “我已经把五运六气技能包准备好了。请先简单介绍一下这个思想，然后问我今天想了解什么。”

然后就开始你的运气学探索之旅吧。

欢迎随时反馈使用感受，帮助这个技能变得更好！