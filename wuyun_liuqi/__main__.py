# -*- coding: utf-8 -*-
"""python -m wuyun_liuqi → 委托 scripts/yunqi_cli.py"""
from __future__ import annotations

import sys

from wuyun_liuqi import _bootstrap


def main(argv=None) -> int:
    _bootstrap  # ensure path
    from yunqi_cli import main as cli_main  # type: ignore
    return int(cli_main(argv if argv is not None else sys.argv[1:]))


if __name__ == "__main__":
    raise SystemExit(main())
