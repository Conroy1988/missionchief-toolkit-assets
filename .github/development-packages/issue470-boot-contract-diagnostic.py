#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
OUTPUT = ROOT / '.github/diagnostics/issue470-boot-contract-alignment.txt'

with tempfile.TemporaryDirectory(prefix='issue470-boot-contract-') as temporary:
    sandbox = Path(temporary) / 'repo'
    shutil.copytree(
        ROOT,
        sandbox,
        ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.pyo'),
    )
    env = dict(os.environ)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    package = subprocess.run(
        ['python3', '.github/development-packages/issue470-boot-contract-alignment.py'],
        cwd=sandbox,
        env=env,
        text=True,
        capture_output=True,
        timeout=300,
    )
    body = [
        'Issue #470 boot contract alignment diagnostic',
        f'package_exit={package.returncode}',
        '',
        '=== PACKAGE STDOUT ===',
        package.stdout,
        '=== PACKAGE STDERR ===',
        package.stderr,
    ]

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text('\n'.join(body), encoding='utf-8')
SELF.unlink(missing_ok=True)
print(OUTPUT.relative_to(ROOT))
