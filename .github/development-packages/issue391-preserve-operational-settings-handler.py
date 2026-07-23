#!/usr/bin/env python3
from __future__ import annotations

import os
import py_compile
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RETIRE_REL = Path(".github/development-packages/issue391-retire-matrix.py")
RETIRE = ROOT / RETIRE_REL
FINAL_REL = Path(".github/development-packages/issue391-update-post-retirement-settings-contract.py")

text = RETIRE.read_text(encoding="utf-8")

old_boundary = '''start = source.index(start_marker)
end = source.index(end_marker, start)
old_block = source[start:end]
if len(old_block.splitlines()) != 1395:
    raise RuntimeError(f"Matrix retirement boundary drifted: {len(old_block.splitlines())} lines")

shared_names = (
'''
new_boundary = '''start = source.index(start_marker)
end = source.index(end_marker, start)
settings_handler_start = source.index("    function handleOperationalWindowSettingChange")
settings_handler_end = source.index("    function operationalFeatureStyle", settings_handler_start)
preserved_operational_settings_handler = source[settings_handler_start:settings_handler_end]
if settings_handler_start < start:
    source = source[:settings_handler_start] + source[settings_handler_end:]
    start = source.index(start_marker)
    end = source.index(end_marker, start)
old_block = source[start:end]
if len(old_block.splitlines()) != 1395:
    raise RuntimeError(f"Matrix retirement boundary drifted: {len(old_block.splitlines())} lines")

shared_names = (
'''
if text.count(old_boundary) != 1:
    raise RuntimeError(f"operational settings handler boundary anchor drifted: {text.count(old_boundary)}")
text = text.replace(old_boundary, new_boundary, 1)

insertion_anchor = '    + "".join(shared)\n'
if text.count(insertion_anchor) != 1:
    raise RuntimeError(f"operational settings handler insertion anchor drifted: {text.count(insertion_anchor)}")
text = text.replace(insertion_anchor, insertion_anchor + "    + preserved_operational_settings_handler\n", 1)

old_count = '''for name in shared_names:
    if source.count(f"const {name} =") != 1:
        raise RuntimeError(f"shared capability catalogue count changed: {name}")
if source.count("matrixRetired: true") < 1:
'''
new_count = '''for name in shared_names:
    if source.count(f"const {name} =") != 1:
        raise RuntimeError(f"shared capability catalogue count changed: {name}")
if source.count("function handleOperationalWindowSettingChange(") != 1:
    raise RuntimeError("operational settings handler declaration count changed during Matrix retirement")
if source.count("matrixRetired: true") < 1:
'''
if text.count(old_count) != 1:
    raise RuntimeError("operational settings handler count anchor drifted")
text = text.replace(old_count, new_count, 1)

RETIRE.write_text(text, encoding="utf-8")
py_compile.compile(str(RETIRE), doraise=True)

with tempfile.TemporaryDirectory(prefix="issue391-preserve-settings-handler-") as temporary:
    sandbox = Path(temporary) / "repo"
    shutil.copytree(ROOT, sandbox, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo"))
    result = subprocess.run(
        ["python3", str(sandbox / FINAL_REL)],
        cwd=sandbox,
        text=True,
        capture_output=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if result.returncode != 0:
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="")
        raise SystemExit("Operational settings handler preservation failed full retirement sandbox")

for obsolete in (
    ROOT / ".github" / "development-packages" / "issue391-preserve-handler-diagnostic-v2.py",
    ROOT / ".github" / "diagnostics" / "issue391-preserve-handler-failure.txt",
    ROOT / ".github" / "diagnostics" / "issue391-preserve-handler-failure-v2.txt",
    ROOT / ".github" / "diagnostics" / "issue391-operational-setting-router-map.txt",
    ROOT / ".github" / "diagnostics" / "issue391-operational-settings-slice-map.txt",
    ROOT / ".github" / "diagnostics" / "issue391-operational-suite-tail-map.txt",
    ROOT / ".github" / "diagnostics" / "issue391-post-retirement-settings-failure-v7.txt",
):
    obsolete.unlink(missing_ok=True)

print("Operational settings handler relocated and preserved; complete Matrix-retirement sandbox passed.")
