#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE_REL = Path('.github/development-packages/issue391-preserve-operational-settings-handler.py')
OUTPUT = ROOT / '.github/diagnostics/issue391-preserve-handler-failure-v2.txt'

with tempfile.TemporaryDirectory(prefix='issue391-preserve-handler-diagnostic-v2-') as temporary:
    sandbox = Path(temporary) / 'repo'
    shutil.copytree(ROOT, sandbox, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.pyo'))
    result = subprocess.run(
        ['python3', str(sandbox / PACKAGE_REL)],
        cwd=sandbox,
        text=True,
        capture_output=True,
        env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
    )

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(
    'ISSUE391_PRESERVE_HANDLER_FAILURE_V2\n'
    f'returncode={result.returncode}\n\n'
    '=== STDOUT ===\n' + (result.stdout or '') + '\n'
    '=== STDERR ===\n' + (result.stderr or ''),
    encoding='utf-8',
)
print(f'Captured handler-preservation v2 failure: returncode={result.returncode}')
