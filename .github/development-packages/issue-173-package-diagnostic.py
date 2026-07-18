#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET_REL = Path('.github/development-packages/issue-171-header-only-placement-v4164.py')
REPORT = ROOT / '.github' / 'diagnostics' / 'issue-173-package-result.txt'

with tempfile.TemporaryDirectory(prefix='issue-173-package-') as temp_dir:
    temp_root = Path(temp_dir) / 'repository'
    shutil.copytree(ROOT, temp_root, ignore=shutil.ignore_patterns('.git'))
    result = subprocess.run(
        ['python3', str(temp_root / TARGET_REL)],
        cwd=temp_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(
    f'exit_code={result.returncode}\n\n{result.stdout}',
    encoding='utf-8',
)
print(f'Wrote isolated Issue 173 package diagnostic with exit code {result.returncode}')
