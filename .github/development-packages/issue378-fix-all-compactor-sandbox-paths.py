#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import py_compile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github" / "development-packages" / "issue378-compact-engine-source.py"

text = PACKAGE.read_text(encoding="utf-8")
if "import os\n" not in text:
    anchor = "from pathlib import Path\n"
    if text.count(anchor) != 1:
        raise RuntimeError("compactor pathlib import anchor changed")
    text = text.replace(anchor, anchor + "import os\n", 1)
old = '        env={"PYTHONDONTWRITEBYTECODE": "1"},\n'
new = '        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},\n'
if text.count(old) != 2:
    raise RuntimeError(f"expected two isolated sandbox environments, found {text.count(old)}")
text = text.replace(old, new)
if text.count(new) != 2:
    raise RuntimeError("both compactor subprocess environments were not corrected")
PACKAGE.write_text(text, encoding="utf-8")
py_compile.compile(str(PACKAGE), doraise=True)
print("Preserved PATH and the full runner environment for both Issue #378 compactor subprocesses.")
