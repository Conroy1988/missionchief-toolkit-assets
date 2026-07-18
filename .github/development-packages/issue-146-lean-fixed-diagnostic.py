#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_COMMIT = '8e9da4504358b56ae4c5a1ed016ffeb519319f6c'
PACKAGE_PATH = '.github/development-packages/issue-146-single-owner-hotfix-lean.py'
TEMP = ROOT / '.github' / 'development-packages' / 'issue-146-lean-fixed.payload.py'
REPORT = ROOT / '.github' / 'diagnostics' / 'issue-146-lean-fixed-failure.txt'

payload = subprocess.check_output(['git', 'show', f'{SOURCE_COMMIT}:{PACKAGE_PATH}'], cwd=ROOT, text=True)
TEMP.write_text(payload, encoding='utf-8')
result = subprocess.run([sys.executable, str(TEMP)], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
output = result.stdout[-30000:]
subprocess.run(['git', 'reset', '--hard', 'HEAD'], cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
TEMP.unlink(missing_ok=True)
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(
    'Issue #146 corrected lean-package diagnostic\n'
    '============================================\n\n'
    f'Payload return code: {result.returncode}\n\n'
    'Bounded output:\n\n' + output + '\n',
    encoding='utf-8',
)
print('Issue #146 corrected lean-package diagnostic written')
