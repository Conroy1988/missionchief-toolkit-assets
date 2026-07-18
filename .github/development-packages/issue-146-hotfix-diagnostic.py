#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / '.github' / 'development-packages' / 'issue-146-single-owner-hotfix.py'
REPORT = ROOT / '.github' / 'diagnostics' / 'issue-146-hotfix-failure.txt'

result = subprocess.run(
    [sys.executable, str(TARGET)],
    cwd=ROOT,
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)
output = result.stdout[-30000:]
subprocess.run(['git', 'reset', '--hard', 'HEAD'], cwd=ROOT, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
TARGET.unlink(missing_ok=True)
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(
    'Issue #146 v4.15.3 hotfix diagnostic\n'
    '====================================\n\n'
    f'Payload return code: {result.returncode}\n\n'
    'Bounded output:\n\n' + output + '\n',
    encoding='utf-8',
)
print('Issue #146 bounded hotfix diagnostic written')
