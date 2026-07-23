#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import py_compile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github" / "development-packages" / "issue378-compact-engine-source.py"

text = PACKAGE.read_text(encoding="utf-8")
old = "if not 1 <= len(chunks) <= 27:\n"
new = "if not 1 <= len(chunks) <= 28:\n"
if text.count(old) != 1:
    raise RuntimeError(f"expected one compact-engine chunk bound, found {text.count(old)}")
text = text.replace(old, new, 1)
PACKAGE.write_text(text, encoding="utf-8")
py_compile.compile(str(PACKAGE), doraise=True)
print("Allowed the 28 logical engine chunks that meet, but do not exceed, the 32,000-line ceiling.")
