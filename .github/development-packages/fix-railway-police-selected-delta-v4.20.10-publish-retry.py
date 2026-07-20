#!/usr/bin/env python3
from pathlib import Path

PACKAGE = Path(__file__).with_name("fix-railway-police-selected-delta-v4.20.10.py")
namespace = {"__name__": "__main__", "__file__": str(PACKAGE)}
exec(compile(PACKAGE.read_text(encoding="utf-8"), str(PACKAGE), "exec"), namespace)
PACKAGE.unlink(missing_ok=True)
