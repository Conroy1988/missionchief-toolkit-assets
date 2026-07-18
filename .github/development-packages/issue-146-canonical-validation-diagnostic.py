#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_COMMIT = 'b2fda050cf213d2633eeee251b6706311578a088'
PACKAGE_PATH = '.github/development-packages/issue-146-single-owner-hotfix-release.py'
TEMP = ROOT / '.github' / 'development-packages' / 'issue-146-release.validate.payload.py'
REPORT = ROOT / '.github' / 'diagnostics' / 'issue-146-canonical-validation-failure.txt'

payload = subprocess.check_output(['git', 'show', f'{SOURCE_COMMIT}:{PACKAGE_PATH}'], cwd=ROOT, text=True)
TEMP.write_text(payload, encoding='utf-8')
package = subprocess.run([sys.executable, str(TEMP)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
validation = subprocess.run(
    [sys.executable, str(ROOT / '.github' / 'scripts' / 'validate_userscript.py')],
    cwd=ROOT,
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
) if package.returncode == 0 else None
output = package.stdout[-12000:]
if validation is not None:
    output += '\n\n--- canonical validation ---\n\n' + validation.stdout[-30000:]
subprocess.run(['git', 'reset', '--hard', 'HEAD'], cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
TEMP.unlink(missing_ok=True)
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(
    'Issue #146 canonical-validation diagnostic\n'
    '=========================================\n\n'
    f'Package return code: {package.returncode}\n'
    f'Validation return code: {validation.returncode if validation is not None else "not-run"}\n\n'
    'Bounded output:\n\n' + output + '\n',
    encoding='utf-8',
)
print('Issue #146 canonical-validation diagnostic written')
