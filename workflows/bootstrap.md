# 首次安装与依赖检查

> AI 首次进入本技能包时执行。若依赖已就绪，跳过本文件。

## 对人类的意义

当人类在对话中提到运气相关话题时，本技能让 AI 成为可靠的讲解者，帮助理解五运六气思想，而非仅凭记忆给出计算结果。

## 执行步骤

```text
0. 检测本包路径（由 SKILL.md 所在目录推导），记为 <SKILL_ROOT>

1. 检查 Python 依赖：
   python -c "import lunar_python" 2>/dev/null && echo OK || echo MISSING

2. 若缺失 → 执行安装脚本：
   Windows: powershell -File "<SKILL_ROOT>\scripts\setup.bat"
   Linux/macOS: bash <SKILL_ROOT>/scripts/setup.sh
   （自动 pip install -r requirements.txt）

3. 验证并向用户报告：
   ✅ Python: lunar-python
   ✅ 推算引擎: scripts/calculate_yunqi_api.py
   ✅ RAG 知识库: rag-knowledge-base/
   ✅ 自进化引擎: scripts/self_evolve.py
   ✅ 端到端验证: python tests/verify_expansion.py + python tests/full_regression_test.py

4. （可选）任意项目常驻：`python scripts/install.py --link-global`
5. 确认就绪后，按 workflows/routing-contract.md 开始工作。
   若 pip install 失败 → 降级使用近似节气表，告知用户精度受限。
```

一句话安装完整流程见 `workflows/one-line-install.md`。

## 人类用户手动安装

```bash
pip install -r requirements.txt
npm install          # 可选，仅 Node.js 接口需要
python scripts/health_check.py
```

快速试用：

```bash
python scripts/calculate_yunqi_api.py 2026-06-27 --json
python scripts/demo_full_chain.py 2026-06-27
python tests/verify_expansion.py
```