#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import py_compile

ROOT = Path(__file__).resolve().parents[2]
SHELL_PACKAGE = ROOT / ".github" / "development-packages" / "issue378-operational-suite-shell.py"

text = SHELL_PACKAGE.read_text(encoding="utf-8")
replacements = {
    "old_headroom_check = '''    split_lines": "old_headroom_check = r'''    split_lines",
    "new_headroom_check = '''    split_lines": "new_headroom_check = r'''    split_lines",
}
for old, new in replacements.items():
    if text.count(old) != 1:
        raise RuntimeError(f"expected one headroom anchor declaration for {old!r}, found {text.count(old)}")
    text = text.replace(old, new, 1)

SHELL_PACKAGE.write_text(text, encoding="utf-8")
py_compile.compile(str(SHELL_PACKAGE), doraise=True)
print("Corrected Issue #378 raw headroom anchor escaping and compiled the shell package.")
