#!/usr/bin/env python3
from __future__ import annotations

import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_COMMIT = 'f8dc390ef31de78c4f9a8819bd9411af277dfe3e'
PACKAGE_PATH = '.github/development-packages/issue-146-single-owner-hotfix-minified.py'
TEMP = ROOT / '.github' / 'development-packages' / 'issue-146-single-owner-hotfix.final.payload.py'

payload = subprocess.check_output(['git', 'show', f'{SOURCE_COMMIT}:{PACKAGE_PATH}'], cwd=ROOT, text=True)

write_anchor = "SOURCE.write_text(source, encoding='utf-8')\n\nfor relative in ("
contract_patch = """SOURCE.write_text(source, encoding='utf-8')

contract = CONTRACT_TEST.read_text(encoding='utf-8')
old_missing = '    missing = [marker for marker in required_markers if marker not in source]\\n'
new_missing = '    compact_source = re.sub(r"\\\\s+", "", source)\\n    missing = [marker for marker in required_markers if marker not in source and re.sub(r"\\\\s+", "", marker) not in compact_source]\\n'
if contract.count(old_missing) != 1:
    raise AssertionError('Mission Requirements whitespace-tolerant marker anchor missing or duplicated')
contract = contract.replace(old_missing, new_missing, 1)
old_insert_count = '    assert source.count("source.parentNode?.insertBefore(panel, source)") == 1\\n'
new_insert_count = '    assert compact_source.count("source.parentNode?.insertBefore(panel,source)") == 1\\n'
if contract.count(old_insert_count) != 1:
    raise AssertionError('Mission Requirements insertion-count anchor missing or duplicated')
contract = contract.replace(old_insert_count, new_insert_count, 1)
CONTRACT_TEST.write_text(contract, encoding='utf-8')

for relative in ("""
if payload.count(write_anchor) != 1:
    raise AssertionError('Issue #146 final contract patch anchor missing or duplicated')
payload = payload.replace(write_anchor, contract_patch, 1)

cleanup_anchor = "    '.github/development-packages/issue-146-single-owner-hotfix-budget.py',\n    '.github/diagnostics/issue-146-hotfix-failure.txt',"
cleanup_replacement = """    '.github/development-packages/issue-146-single-owner-hotfix-budget.py',
    '.github/development-packages/issue-146-single-owner-hotfix-minified.py',
    '.github/development-packages/issue-146-mission-requirements-single-owner-diagnostic.py',
    '.github/diagnostics/issue-146-hotfix-failure.txt',
    '.github/diagnostics/issue-146-mission-requirements-candidates.txt',
    '.github/diagnostics/issue-146-mission-requirements-ownership.txt',"""
if payload.count(cleanup_anchor) != 1:
    raise AssertionError('Issue #146 final cleanup anchor missing or duplicated')
payload = payload.replace(cleanup_anchor, cleanup_replacement, 1)

TEMP.write_text(payload, encoding='utf-8')
try:
    runpy.run_path(str(TEMP), run_name='__main__')
finally:
    TEMP.unlink(missing_ok=True)
