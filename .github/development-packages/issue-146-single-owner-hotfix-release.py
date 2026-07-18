#!/usr/bin/env python3
from __future__ import annotations

import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_COMMIT = '8e9da4504358b56ae4c5a1ed016ffeb519319f6c'
PACKAGE_PATH = '.github/development-packages/issue-146-single-owner-hotfix-lean.py'
TEMP = ROOT / '.github' / 'development-packages' / 'issue-146-single-owner-hotfix.release.payload.py'

payload = subprocess.check_output(['git', 'show', f'{SOURCE_COMMIT}:{PACKAGE_PATH}'], cwd=ROOT, text=True)
anchor = "contract = CONTRACT_TEST.read_text(encoding='utf-8')\nold_missing ="
replacement = """contract = CONTRACT_TEST.read_text(encoding='utf-8')
old_required_insert = '        \"source.parentNode?.insertBefore(panel, source)\",\\n'
new_required_insert = '        \"source.parentNode?.insertBefore(p, source)\",\\n'
if contract.count(old_required_insert) != 1:
    raise AssertionError('Mission Requirements required insertion marker missing or duplicated')
contract = contract.replace(old_required_insert, new_required_insert, 1)
old_missing ="""
if payload.count(anchor) != 1:
    raise AssertionError('Issue #146 release contract anchor missing or duplicated')
payload = payload.replace(anchor, replacement, 1)

TEMP.write_text(payload, encoding='utf-8')
try:
    runpy.run_path(str(TEMP), run_name='__main__')
finally:
    TEMP.unlink(missing_ok=True)

for relative in (
    '.github/development-packages/issue-146-single-owner-hotfix-lean.py',
    '.github/development-packages/issue-146-single-owner-hotfix-final.py',
    '.github/development-packages/issue-146-single-owner-hotfix-minified.py',
    '.github/development-packages/issue-146-single-owner-hotfix-budget.py',
    '.github/development-packages/issue-146-single-owner-hotfix-fast.py',
    '.github/development-packages/issue-146-single-owner-hotfix-corrected.py',
    '.github/diagnostics/issue-146-hotfix-failure.txt',
    '.github/diagnostics/issue-146-mission-requirements-candidates.txt',
    '.github/diagnostics/issue-146-mission-requirements-ownership.txt',
):
    (ROOT / relative).unlink(missing_ok=True)
