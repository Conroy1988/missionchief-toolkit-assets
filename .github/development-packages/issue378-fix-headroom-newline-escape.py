#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import py_compile

ROOT = Path(__file__).resolve().parents[2]
SHELL_PACKAGE = ROOT / ".github" / "development-packages" / "issue378-operational-suite-shell.py"

text = SHELL_PACKAGE.read_text(encoding="utf-8")
old = '''HEADROOM_FIXTURE.write_text(json.dumps(headroom_fixture, indent=2) + "
", encoding="utf-8")'''
new = '''HEADROOM_FIXTURE.write_text(json.dumps(headroom_fixture, indent=2) + "\\n", encoding="utf-8")'''
if text.count(old) != 1:
    raise RuntimeError(f"expected one malformed fixture-newline anchor, found {text.count(old)}")
text = text.replace(old, new, 1)
SHELL_PACKAGE.write_text(text, encoding="utf-8")
py_compile.compile(str(SHELL_PACKAGE), doraise=True)
print("Corrected Issue #378 headroom fixture newline escaping and compiled the shell package.")
