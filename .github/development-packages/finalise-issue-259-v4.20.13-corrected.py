#!/usr/bin/env python3
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github/development-packages/finalise-issue-259-v4.20.13.py"
text = PACKAGE.read_text(encoding="utf-8")
old = "resourceCandidate.root.queryHandler = selector => selector.includes('[id^=\"mission_water_holder\"]') ? holder : originalResourceQuery(selector);"
new = "resourceCandidate.root.queryHandler = selector => /mission_(?:water|foam|pump)_holder/.test(selector) ? holder : originalResourceQuery(selector);"
if text.count(old) != 1:
    raise RuntimeError("resource fixture correction anchor missing")
PACKAGE.write_text(text.replace(old, new, 1), encoding="utf-8")
runpy.run_path(str(PACKAGE), run_name="__main__")
PACKAGE.unlink()
