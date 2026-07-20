#!/usr/bin/env python3
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
FIX_PACKAGE = Path('.github/development-packages/issue-226-operational-capacity-fix.py')
REPORT = ROOT / 'status' / 'issue-226-fix-package-diagnostic.txt'
CLEANUP = [
    ROOT / FIX_PACKAGE,
    ROOT / '.github/development-packages/issue-226-operational-diagnostic.py',
    ROOT / 'status/issue-226-operational-diagnostic.txt',
]

with tempfile.TemporaryDirectory(prefix='mcms-issue-226-') as temporary:
    copied_root = Path(temporary) / 'repository'
    shutil.copytree(ROOT, copied_root, symlinks=True)
    process = subprocess.run(
        ['python3', str(FIX_PACKAGE)],
        cwd=copied_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    report = [
        'Issue #226 full hotfix package diagnostic',
        '',
        f'Exit code: {process.returncode}',
        '',
        '--- Captured output ---',
        process.stdout or '(no output)',
    ]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text('\n'.join(report), encoding='utf-8')

for path in CLEANUP:
    if path.exists():
        path.unlink()

print(f'Issue #226 package diagnostic captured exit code {process.returncode}')
