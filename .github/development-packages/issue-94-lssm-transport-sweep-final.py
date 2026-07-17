#!/usr/bin/env python3
from __future__ import annotations

import re
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / ".github/development-packages/issue-94-lssm-transport-sweep.py"
PREVIOUS = ROOT / ".github/development-packages/issue-94-lssm-transport-sweep-correction.py"

text = PACKAGE.read_text(encoding="utf-8")
old_confirmation = 'source = replace_once(source, old_confirm, new_confirm, "transport sweep confirmation")'
new_confirmation = '''source = regex_replace_once(
    source,
    r"        const confirmed = pageWindow\\.confirm\\(`Transport Sweep will use MissionChief's visible co-admin controls.*?Continue\\?`\\);",
    new_confirm,
    "transport sweep confirmation",
)'''
if text.count(old_confirmation) != 1:
    raise RuntimeError(f"Expected one confirmation replacement, found {text.count(old_confirmation)}")
text = text.replace(old_confirmation, new_confirmation, 1)

workflow_block = re.compile(
    r'\naudit = AUDIT_WORKFLOW\.read_text\(encoding="utf-8"\).*?AUDIT_WORKFLOW\.write_text\(audit, encoding="utf-8"\)\n',
    re.S,
)
text, count = workflow_block.subn('\n# Protected workflow registration is applied directly to the reviewed PR branch.\n', text, count=1)
if count != 1:
    raise RuntimeError(f"Expected one protected workflow block, found {count}")

PACKAGE.write_text(text, encoding="utf-8")
runpy.run_path(str(PACKAGE), run_name="__main__")
PACKAGE.unlink(missing_ok=True)
PREVIOUS.unlink(missing_ok=True)
print("Issue #94 final package applied without protected workflow mutation")
