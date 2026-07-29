#!/usr/bin/env python3
"""Execute the reviewed v8.3.2 Issue #255 package after correcting its generated help-copy newline."""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_PATH = ".github/development-packages/apply_issue255_v832_update_ui_write_suppression.py"
REVIEWED_COMMIT = "a4e0e3286bdc5e8c03bdf091fe0d2f9383c6edd3"

payload = subprocess.check_output(
    ["git", "show", f"{REVIEWED_COMMIT}:{PACKAGE_PATH}"],
    cwd=ROOT,
    text=True,
)

broken = '''if notice_count != 1: raise RuntimeError(f"help notice matches: {notice_count}
")'''
fixed = 'if notice_count != 1: raise RuntimeError(f"help notice matches: {notice_count}")'
if payload.count(broken) != 1:
    raise RuntimeError(f"reviewed help-copy newline defect count: {payload.count(broken)}")
payload = payload.replace(broken, fixed, 1)

runtime_path = ROOT / ".github/development-packages/.issue255-v832-runtime.py"
runtime_path.write_text(payload, encoding="utf-8")
try:
    code = compile(payload, str(runtime_path), "exec")
    namespace = {"__name__": "__main__", "__file__": str(runtime_path)}
    exec(code, namespace, namespace)
finally:
    runtime_path.unlink(missing_ok=True)
