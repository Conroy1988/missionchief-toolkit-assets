#!/usr/bin/env python3
from __future__ import annotations

import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_COMMIT = 'b2fda050cf213d2633eeee251b6706311578a088'
PACKAGE_PATH = '.github/development-packages/issue-146-single-owner-hotfix-release.py'
TEMP = ROOT / '.github' / 'development-packages' / 'issue-146-single-owner-hotfix.publish.payload.py'

payload = subprocess.check_output(['git', 'show', f'{SOURCE_COMMIT}:{PACKAGE_PATH}'], cwd=ROOT, text=True)
write_anchor = "TEMP.write_text(payload, encoding='utf-8')\n"
patch = """duplicate_id = \"p=p&&a.includes(p)?p:a[0];p.id=SCRIPT.missionRequirementsPanelId;p.setAttribute?.('data-mcms-requirements-panel','1')\"
single_id = \"p=p&&a.includes(p)?p:a[0];p.setAttribute?.('data-mcms-requirements-panel','1')\"
if payload.count(duplicate_id) != 1:
    raise AssertionError('Issue #146 duplicate interface-ID anchor missing or duplicated')
payload = payload.replace(duplicate_id, single_id, 1)

TEMP.write_text(payload, encoding='utf-8')
"""
if payload.count(write_anchor) != 1:
    raise AssertionError('Issue #146 publish wrapper anchor missing or duplicated')
payload = payload.replace(write_anchor, patch, 1)

TEMP.write_text(payload, encoding='utf-8')
try:
    runpy.run_path(str(TEMP), run_name='__main__')
finally:
    TEMP.unlink(missing_ok=True)

for relative in (
    '.github/development-packages/issue-146-single-owner-hotfix-release.py',
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
