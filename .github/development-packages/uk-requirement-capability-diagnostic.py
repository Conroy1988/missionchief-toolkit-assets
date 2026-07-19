#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path('.github/development-packages/uk-requirement-capability-port.py')
REPORT = ROOT / 'status' / 'uk-requirement-capability-diagnostic.txt'

with tempfile.TemporaryDirectory(prefix='uk-capability-diagnostic-') as temp_dir:
    clone = Path(temp_dir) / 'repo'
    shutil.copytree(ROOT, clone, ignore=shutil.ignore_patterns('.git'))
    result = subprocess.run(['python3', str(PACKAGE)], cwd=clone, text=True, capture_output=True)
    REPORT.write_text('\n'.join([
        'UK requirement capability port diagnostic',
        f'exit_status={result.returncode}',
        '',
        'STDOUT:',
        result.stdout[-16000:],
        '',
        'STDERR:',
        result.stderr[-16000:],
        '',
    ]), encoding='utf-8')

Path(__file__).unlink()
print('Recorded isolated UK capability port diagnostic')
