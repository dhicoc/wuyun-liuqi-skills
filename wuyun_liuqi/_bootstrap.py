# -*- coding: utf-8 -*-
"""
将 scripts/ 与 scripts/lib 加入 sys.path，便于复用现有实现。

仓库根目录解析顺序：
1. 环境变量 WUYUN_LIUQI_ROOT
2. 自本文件向上查找（含 scripts/calculate_yunqi_api.py 与 rag-knowledge-base）
3. 回退为包目录的上一级（editable 安装场景）
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


def _find_repo_root() -> Path:
    env = os.environ.get("WUYUN_LIUQI_ROOT", "").strip()
    if env:
        p = Path(env).expanduser().resolve()
        if p.is_dir():
            return p

    here = Path(__file__).resolve().parent
    for candidate in [here.parent, here, *list(here.parents)[:6]]:
        if (candidate / "scripts" / "calculate_yunqi_api.py").is_file() and (
            candidate / "rag-knowledge-base"
        ).is_dir():
            return candidate
    return here.parent


_ROOT = _find_repo_root()
_SCRIPTS = _ROOT / "scripts"
_LIB = _SCRIPTS / "lib"

for p in (_SCRIPTS, _LIB, _ROOT):
    s = str(p)
    if p.is_dir() and s not in sys.path:
        sys.path.insert(0, s)

# 初始化 UTF-8 / 环境（幂等）
try:
    from _common import setup_environment
    setup_environment(add_lib=True, add_scripts=True)
except Exception:
    pass

ROOT = _ROOT
SCRIPTS = _SCRIPTS
RAG_DIR = _ROOT / "rag-knowledge-base"


def ensure_runtime_ready() -> dict:
    """供冒烟测试：检查关键路径是否存在。"""
    return {
        "root": str(ROOT),
        "scripts_ok": (SCRIPTS / "calculate_yunqi_api.py").is_file(),
        "rag_ok": RAG_DIR.is_dir(),
        "rag_assets": (RAG_DIR / "asset1_suiyun.json").is_file(),
    }
