#!/usr/bin/env bash
# ============================================================
# wuyun-liuqi 一键环境配置脚本 (Linux/macOS)
# 用法: bash scripts/setup.sh
# ============================================================
set -e

# 强制 UTF-8 编码环境变量，解决终端中文乱码
export PYTHONIOENCODING=utf-8

SKILL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SKILL_ROOT"

echo "============================================"
echo "  五运六气 AI Agent 技能包 — 环境配置"
echo "============================================"
echo ""

# ---- 1. Python 检测 ----
echo "[1/4] 检测 Python..."
if command -v python3 &>/dev/null; then
    PY=python3
elif command -v python &>/dev/null; then
    PY=python
else
    echo "  [FAIL] 未找到 Python。请先安装 Python 3.8+。"
    exit 1
fi
echo "  ✓ Python: $($PY --version 2>&1)"

# ---- 2. 安装 lunar-python ----
echo "[2/4] 安装 Python 依赖 (lunar-python)..."
if $PY -c "import lunar_python" 2>/dev/null; then
    echo "  ✓ lunar-python 已安装"
else
    $PY -m pip install lunar-python --quiet
    echo "  ✓ lunar-python 安装完成"
fi

# ---- 3. 创建运行时目录 ----
echo "[3/4] 创建自进化运行时目录..."
mkdir -p self-evolve/logs self-evolve/misses self-evolve/feedback self-evolve/reports
echo "  ✓ 目录已就绪"

# ---- 4. Node.js (可选) ----
echo "[4/4] 检测 Node.js (可选)..."
if command -v node &>/dev/null; then
    echo "  ✓ Node.js: $(node --version)"
    if [ -f package.json ]; then
        echo "  → 如需使用 JS 版, 运行: npm install"
    fi
else
    echo "  - Node.js 未安装 (仅 Python 版可用, 不影响核心功能)"
fi

echo ""
echo "============================================"
echo "  ✅ 环境配置完成!"
echo "============================================"
echo ""
echo "下一步推荐（直接复制运行）："
echo "  $PY scripts/health_check.py"
echo "  $PY scripts/calculate_yunqi_api.py today --summary"
echo "  $PY scripts/install.py --link-global   （推荐：环境+全局技能注册）"
echo ""
echo "想立即看今天运气？直接运行上面第二条即可（支持 today / 无参数默认今天）。"
echo "更多用法见 README.md 和 docs/ux_optimization.md"
