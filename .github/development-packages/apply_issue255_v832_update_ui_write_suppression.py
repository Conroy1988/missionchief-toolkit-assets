#!/usr/bin/env python3
"""Execute the reviewed v8.3.2 Issue #255 package with narrow package-generation corrections."""
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

broken_help = '''if notice_count != 1: raise RuntimeError(f"help notice matches: {notice_count}
")'''
fixed_help = 'if notice_count != 1: raise RuntimeError(f"help notice matches: {notice_count}")'
if payload.count(broken_help) != 1:
    raise RuntimeError(f"reviewed help-copy newline defect count: {payload.count(broken_help)}")
payload = payload.replace(broken_help, fixed_help, 1)

broken_toggle = '''block = replace_count(block, "                btn.classList.toggle('mcms-on', on);", "                updateUiToggleClass(btn, 'mcms-on', on);", 2, "toggle button class writes")'''
fixed_toggle = '''block, toggle_class_count = re.subn(
    r"(?m)^(\\s+)btn\\.classList\\.toggle\\('mcms-on', on\\);$",
    lambda match: f"{match.group(1)}updateUiToggleClass(btn, 'mcms-on', on);",
    block,
)
if toggle_class_count != 2:
    raise RuntimeError(f"toggle button class writes: expected 2 matches, found {toggle_class_count}")'''
if payload.count(broken_toggle) != 1:
    raise RuntimeError(f"reviewed toggle-replacement defect count: {payload.count(broken_toggle)}")
payload = payload.replace(broken_toggle, fixed_toggle, 1)

check_anchor = '''for pattern, label in [
    (r"\\.classList\\.toggle\\(", "class toggle"),'''
dataset_fix = '''block, remaining_dataset_count = re.subn(
    r"(?m)^(\\s+)([A-Za-z_$][\\w$]*)\\.dataset\\.([A-Za-z_$][\\w$]*)\\s*=\\s*([^;\\n]+);$",
    lambda match: f"{match.group(1)}updateUiSetDataset({match.group(2)}, '{match.group(3)}', {match.group(4)});",
    block,
)
if remaining_dataset_count != 1:
    raise RuntimeError(f"remaining dataset writes: expected 1 match, found {remaining_dataset_count}")
for pattern, label in [
    (r"\\.classList\\.toggle\\(", "class toggle"),'''
if payload.count(check_anchor) != 1:
    raise RuntimeError(f"reviewed direct-write check anchor count: {payload.count(check_anchor)}")
payload = payload.replace(check_anchor, dataset_fix, 1)

runtime_path = ROOT / ".github/development-packages/.issue255-v832-runtime.py"
runtime_path.write_text(payload, encoding="utf-8")
try:
    code = compile(payload, str(runtime_path), "exec")
    namespace = {"__name__": "__main__", "__file__": str(runtime_path)}
    exec(code, namespace, namespace)
finally:
    runtime_path.unlink(missing_ok=True)
