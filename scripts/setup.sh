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
echo "快速试用:"
echo "  $PY scripts/calculate_yunqi_api.py 2026-06-27"
echo "  $PY scripts/demo_full_chain.py 2004-07-30"
echo "  $PY scripts/verify_expansion.py"
echo ""
echo "更多用法见 README.md"
