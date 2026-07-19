#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[2]
package_rel = Path('.github/development-packages/issue-215-version-status-auto-refresh.py')
report = root / '.github' / 'diagnostics' / 'issue-215-version-status-auto-refresh.txt'
report.parent.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix='issue-215-') as temp:
    clone = Path(temp) / 'repo'
    shutil.copytree(root, clone, ignore=shutil.ignore_patterns('.git'))
    result = subprocess.run(
        ['python3', str(package_rel)],
        cwd=clone,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = result.stdout or ''
    tail = '\n'.join(output.splitlines()[-120:])
    report.write_text(
        f'Issue #215 package diagnostic\nexit_status={result.returncode}\n\n{tail}\n',
        encoding='utf-8',
    )
Path(__file__).unlink()
print('Recorded Issue #215 package diagnostic')
