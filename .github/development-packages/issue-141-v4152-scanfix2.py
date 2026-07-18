#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
TARGET = ROOT / ".github" / "development-packages" / "issue-141-v4152-scanfix.py"
DIAGNOSTICS = [
    ROOT / ".github" / "development-packages" / "issue-141-v4152-diagnostic.txt",
    ROOT / ".github" / "development-packages" / "issue-141-v4152-diagnostic2.txt",
]
source = TARGET.read_text(encoding="utf-8")
old = "scan_transform = 'source = replace_once(source, old_scan, new_scan, \"Mission Requirements direct native scan\")'"
new = "scan_transform = f'source = replace_once(source, {old_scan!r}, {new_scan!r}, \\\"Mission Requirements direct native scan\\\")'"
if source.count(old) != 1:
    raise AssertionError(f"Expected one scan interpolation anchor, found {source.count(old)}")
source = source.replace(old, new, 1)
namespace = {"__file__": str(TARGET), "__name__": "__main__"}
exec(compile(source, str(TARGET), "exec"), namespace, namespace)
for path in DIAGNOSTICS:
    path.unlink(missing_ok=True)
SELF.unlink(missing_ok=True)
