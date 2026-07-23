#!/usr/bin/env python3
from __future__ import annotations

import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github" / "development-packages" / "issue391-retire-matrix.py"

text = PACKAGE.read_text(encoding="utf-8")
old = '''shared = []
for name in shared_names:
    token = f"    const {name} ="
    declaration_start = source.find(token)
    if declaration_start < 0 or source.count(token) != 1:
        raise RuntimeError(f"shared capability declaration count changed: {name}")
    if start <= declaration_start < end:
        shared.append(extract_declaration(source, name, start, end))
'''
new = '''shared = []
for name in shared_names:
    declaration_pattern = re.compile(rf"^\\s*const\\s+{re.escape(name)}\\s*=", re.MULTILINE)
    declaration_matches = list(declaration_pattern.finditer(source))
    if len(declaration_matches) != 1:
        raise RuntimeError(f"shared capability declaration count changed: {name} ({len(declaration_matches)})")
    declaration_start = declaration_matches[0].start()
    if start <= declaration_start < end:
        shared.append(extract_declaration(source, name, start, end))
'''
if text.count(old) != 1:
    raise RuntimeError("retirement declaration matcher anchor drifted")
text = text.replace(old, new)

old_cleanup = '''    ROOT / ".github" / "diagnostics" / "issue391-retirement-preflight-failure.txt",
)'''
new_cleanup = '''    ROOT / ".github" / "diagnostics" / "issue391-retirement-preflight-failure.txt",
    ROOT / ".github" / "diagnostics" / "issue391-retirement-preflight-failure-v2.txt",
    ROOT / ".github" / "diagnostics" / "issue391-shared-catalogue-map.txt",
)'''
if text.count(old_cleanup) != 1:
    raise RuntimeError("retirement diagnostic cleanup anchor drifted")
text = text.replace(old_cleanup, new_cleanup)

PACKAGE.write_text(text, encoding="utf-8")
py_compile.compile(str(PACKAGE), doraise=True)
print("Issue #391 declaration matcher corrected and retirement package compiled.")
