#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = Path('.github/development-packages/issue-173-v4164-final-runner.py')
REPORT = ROOT / '.github' / 'diagnostics' / 'issue-175-runner3-result.txt'

with tempfile.TemporaryDirectory(prefix='issue-175-runner3-') as temp_dir:
    copy_root = Path(temp_dir) / 'repository'
    shutil.copytree(ROOT, copy_root, ignore=shutil.ignore_patterns('.git'))
    result = subprocess.run(
        ['python3', str(copy_root / TARGET)],
        cwd=copy_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(f'exit_code={result.returncode}\n\n{result.stdout}', encoding='utf-8')
print(f'Wrote current runner diagnostic: {result.returncode}')
