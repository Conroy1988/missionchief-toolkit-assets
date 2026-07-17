#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / ".github/development-packages/issue-94-multi-ambulance-loop.py"

text = TARGET.read_text(encoding="utf-8")
old = "updated, count = re.subn(pattern, replacement, text, count=1, flags=re.S)"
new = "updated, count = re.subn(pattern, lambda _match: replacement, text, count=1, flags=re.S)"
if text.count(old) != 1:
    raise RuntimeError("literal regex replacement helper was not found exactly once")
TARGET.write_text(text.replace(old, new, 1), encoding="utf-8")
runpy.run_path(str(TARGET), run_name="__main__")
TARGET.unlink(missing_ok=True)
