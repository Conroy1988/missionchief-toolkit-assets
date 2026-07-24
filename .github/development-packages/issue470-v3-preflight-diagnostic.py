#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
PACKAGE_DIR = ROOT / '.github/development-packages'
OUTPUT = ROOT / '.github/diagnostics/issue470-v3-preflight.txt'

with tempfile.TemporaryDirectory(prefix='issue470-v3-preflight-') as temporary:
    sandbox = Path(temporary) / 'repo'
    shutil.copytree(
        ROOT,
        sandbox,
        ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.pyo'),
    )
    env = dict(os.environ)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    result = subprocess.run(
        ['python3', '.github/development-packages/issue470-clean-fix.py'],
        cwd=sandbox,
        env=env,
        text=True,
        capture_output=True,
        timeout=300,
    )

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(
    '\n'.join([
        'Issue #470 v3 clean-package diagnostic',
        f'exit={result.returncode}',
        '',
        '=== STDOUT ===',
        result.stdout,
        '=== STDERR ===',
        result.stderr,
    ]),
    encoding='utf-8',
)

for pattern in (
    'issue470-clean.payload.*',
    'issue470-clean-v2.payload.*',
    'issue470-clean-v3.payload.*',
    'issue470-clean-fix.py',
):
    for path in PACKAGE_DIR.glob(pattern):
        path.unlink(missing_ok=True)
(ROOT / '.github/diagnostics/issue470-clean-preflight.txt').unlink(missing_ok=True)
SELF.unlink(missing_ok=True)
print(OUTPUT.relative_to(ROOT))
