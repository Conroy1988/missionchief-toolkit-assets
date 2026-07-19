#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[2]
package_rel = Path('.github/development-packages/issue-212-selected-units-hotfix-v2.py')
report = root / '.github' / 'diagnostics' / 'issue-212-hotfix-v2-report.txt'
report.parent.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix='issue-212-v2-') as tmp:
    clone = Path(tmp) / 'repo'
    shutil.copytree(root, clone, ignore=shutil.ignore_patterns('.git'))
    result = subprocess.run(['python3', str(package_rel)], cwd=clone, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    report.write_text(
        f'Issue #212 v4.20.4 v2 diagnostic\nexit_status={result.returncode}\n\n' + '\n'.join(result.stdout.splitlines()[-100:]) + '\n',
        encoding='utf-8',
    )
Path(__file__).unlink()
print(f'Captured Issue #212 v2 package result: {result.returncode}')
