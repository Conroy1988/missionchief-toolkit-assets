#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github" / "development-packages" / "issue391-retire-matrix.py"
text = PACKAGE.read_text(encoding="utf-8")

old = '''shared = [extract_declaration(source, name, start, end) for name in shared_names]
replacement = (
'''
new = '''shared = []
for name in shared_names:
    token = f"    const {name} ="
    declaration_start = source.find(token)
    if declaration_start < 0 or source.count(token) != 1:
        raise RuntimeError(f"shared capability declaration count changed: {name}")
    if start <= declaration_start < end:
        shared.append(extract_declaration(source, name, start, end))
replacement = (
'''
if text.count(old) != 1:
    raise RuntimeError("Issue #391 catalogue-scope correction anchor changed")
text = text.replace(old, new, 1)

old_diag = '''    ROOT / ".github" / "diagnostics" / "issue391-matrix-hook-map.txt",
)
'''
new_diag = '''    ROOT / ".github" / "diagnostics" / "issue391-matrix-hook-map.txt",
    ROOT / ".github" / "diagnostics" / "issue391-retirement-preflight-failure.txt",
)
'''
if text.count(old_diag) != 1:
    raise RuntimeError("Issue #391 diagnostic-cleanup correction anchor changed")
text = text.replace(old_diag, new_diag, 1)
PACKAGE.write_text(text, encoding="utf-8")
compile(text, str(PACKAGE), "exec")
print("Corrected Issue #391 shared-catalogue ownership and diagnostic cleanup.")
