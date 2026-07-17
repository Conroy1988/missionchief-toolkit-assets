#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / ".github/development-packages/issue-94-dom-delta-lightbox-ownership.py"

text = ORIGINAL.read_text(encoding="utf-8")
anchor = '''    "required DOM-delta markers",
)
old_assertions ='''
insertion = '''    "required DOM-delta markers",
)
test = replace_once(
    test,
    '        "transportSweepRuntime.activeWindowRoot = transportSweepOwnedWindowRoot(root)",\\n',
    '',
    "remove obsolete v4.14.3 ownership marker",
)
old_assertions ='''
if text.count(anchor) != 1:
    raise RuntimeError(f"contract correction anchor expected once, found {text.count(anchor)}")
ORIGINAL.write_text(text.replace(anchor, insertion, 1), encoding="utf-8")

runpy.run_path(str(ORIGINAL), run_name="__main__")
ORIGINAL.unlink(missing_ok=True)
