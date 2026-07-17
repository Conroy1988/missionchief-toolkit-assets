#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github/development-packages/issue-94-lssm-transport-sweep.py"

text = PACKAGE.read_text(encoding="utf-8")
old = 'source = replace_once(source, old_confirm, new_confirm, "transport sweep confirmation")'
new = '''source = regex_replace_once(
    source,
    r"        const confirmed = pageWindow\\.confirm\\(`Transport Sweep will use MissionChief's visible co-admin controls.*?Continue\\?`\\);",
    new_confirm,
    "transport sweep confirmation",
)'''
if text.count(old) != 1:
    raise RuntimeError(f"Expected one confirmation replacement, found {text.count(old)}")
PACKAGE.write_text(text.replace(old, new, 1), encoding="utf-8")
runpy.run_path(str(PACKAGE), run_name="__main__")
PACKAGE.unlink(missing_ok=True)
print("Issue #94 package correction applied successfully")
