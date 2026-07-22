#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path('.github/development-packages/issue353-sergeant-recovery-v42036.py')
OUTPUT = ROOT / '.github/diagnostics/issue353-v42036-package.txt'

with tempfile.TemporaryDirectory(prefix='issue353-') as temp:
    work = Path(temp) / 'repository'
    shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc'))
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
    result = subprocess.run(
        [sys.executable, str(work / PACKAGE)],
        cwd=work,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=180,
    )
    report = [
        '# Issue 353 v4.20.36 package diagnostic',
        '',
        f'- Exit code: `{result.returncode}`',
        '',
        '## Standard output',
        '```text',
        result.stdout[-12000:].rstrip(),
        '```',
        '',
        '## Standard error',
        '```text',
        result.stderr[-12000:].rstrip(),
        '```',
        '',
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text('\n'.join(report), encoding='utf-8')
    print(f'Captured package diagnostic with exit code {result.returncode}')
