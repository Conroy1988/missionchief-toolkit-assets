#!/usr/bin/env python3
from __future__ import annotations

import runpy
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_PATH = '.github/development-packages/issue-146-single-owner-hotfix.py'
SOURCE_COMMIT = '5ab224083e37e5bdde980cb23ab3ffe90a608084'
TEMP = ROOT / '.github' / 'development-packages' / 'issue-146-single-owner-hotfix.payload.py'
FAILURE_REPORT = ROOT / '.github' / 'diagnostics' / 'issue-146-hotfix-failure.txt'

payload = subprocess.check_output(
    ['git', 'show', f'{SOURCE_COMMIT}:{PACKAGE_PATH}'],
    cwd=ROOT,
    text=True,
)
old_identity = "    const id = normaliseMissionId(match?.[1] ?? (/^\\d+$/.test(raw) ? raw : null));\n    if (id !== null) return `mission:${id}`;"
new_identity = "    const id = Number(match?.[1] ?? (/^\\d+$/.test(raw) ? raw : NaN));\n    if (Number.isSafeInteger(id) && id > 0) return `mission:${id}`;"
if payload.count(old_identity) != 1:
    raise AssertionError('Issue #146 identity conversion anchor missing or duplicated')
payload = payload.replace(old_identity, new_identity, 1)

duplicate_full_validation = 'run(sys.executable, str(ROOT / ".github" / "scripts" / "validate_userscript.py"))\n'
if payload.count(duplicate_full_validation) != 1:
    raise AssertionError('Issue #146 duplicate canonical validation anchor missing or duplicated')
payload = payload.replace(duplicate_full_validation, '', 1)

TEMP.write_text(payload, encoding='utf-8')
FAILURE_REPORT.unlink(missing_ok=True)
try:
    runpy.run_path(str(TEMP), run_name='__main__')
finally:
    TEMP.unlink(missing_ok=True)
