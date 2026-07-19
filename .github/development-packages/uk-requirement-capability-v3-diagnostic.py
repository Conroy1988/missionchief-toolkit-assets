#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path('.github/development-packages/uk-requirement-capability-port-v3.py')
REPORT = ROOT / 'status' / 'uk-requirement-capability-diagnostic.txt'
with tempfile.TemporaryDirectory(prefix='uk-capability-v3-diagnostic-') as temp_dir:
    clone = Path(temp_dir) / 'repo'
    shutil.copytree(ROOT, clone, ignore=shutil.ignore_patterns('.git'))
    result = subprocess.run(['python3', str(PACKAGE)], cwd=clone, text=True, capture_output=True)
    REPORT.write_text('\n'.join([
        'UK requirement capability v3 diagnostic',
        f'exit_status={result.returncode}',
        '',
        'STDOUT:',
        result.stdout[-24000:],
        '',
        'STDERR:',
        result.stderr[-24000:],
        '',
    ]), encoding='utf-8')
Path(__file__).unlink()
print('Recorded isolated UK capability v3 diagnostic')
