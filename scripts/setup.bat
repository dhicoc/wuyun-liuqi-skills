@echo off
chcp 65001 >nul
REM ============================================================
REM wuyun-liuqi 一键环境配置脚本 (Windows)
REM 用法: scripts\setup.bat
REM ============================================================

setlocal enabledelayedexpansion
set "SKILL_ROOT=%~dp0.."
cd /d "%SKILL_ROOT%"

echo ============================================
echo   五运六气 AI Agent 技能包 — 环境配置
echo ============================================
echo.

REM ---- 1. Python 检测 ----
echo [1/4] 检测 Python...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo   [FAIL] 未找到 Python。请先安装 Python 3.8+。
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PY_VER=%%i
echo   ^✓ Python: %PY_VER%

REM ---- 2. 安装 lunar-python ----
echo [2/4] 安装 Python 依赖 (lunar-python)...
python -c "import lunar_python" 2>nul
if %ERRORLEVEL% equ 0 (
    echo   ^✓ lunar-python 已安装
) else (
    python -m pip install lunar-python --quiet
    if !ERRORLEVEL! equ 0 (
        echo   ^✓ lunar-python 安装完成
    ) else (
        echo   [WARN] pip 安装失败。请手动运行: pip install lunar-python
    )
)

REM ---- 3. 创建运行时目录 ----
echo [3/4] 创建自进化运行时目录...
if not exist "self-evolve\logs" mkdir "self-evolve\logs"
if not exist "self-evolve\misses" mkdir "self-evolve\misses"
if not exist "self-evolve\feedback" mkdir "self-evolve\feedback"
if not exist "self-evolve\reports" mkdir "self-evolve\reports"
echo   ^✓ 目录已就绪

REM ---- 4. Node.js (可选) ----
echo [4/4] 检测 Node.js (可选)...
node --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    for /f "tokens=*" %%i in ('node --version') do set NODE_VER=%%i
    echo   ^✓ Node.js: !NODE_VER!
    if exist package.json (
        echo   → 如需使用 JS 版, 运行: npm install
    )
) else (
    echo   - Node.js 未安装 (仅 Python 版可用, 不影响核心功能)
)

echo.
echo ============================================
echo   ✅ 环境配置完成!
echo ============================================
echo.
echo 快速试用:
echo   python scripts/calculate_yunqi_api.py 2026-06-27
echo   python scripts/demo_full_chain.py 2004-07-30
echo   python scripts/verify_expansion.py
echo.
echo 更多用法见 README.md
echo.
pause
