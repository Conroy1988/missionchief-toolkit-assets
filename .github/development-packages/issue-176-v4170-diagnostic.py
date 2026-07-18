#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / '.github' / 'development-packages' / 'issue-176-v4170-runner.py'
OUTPUT = ROOT / '.github' / 'diagnostics' / 'issue-176-v4170-result.txt'

with tempfile.TemporaryDirectory(prefix='issue-176-v4170-') as temp:
    clone = Path(temp) / 'repository'
    shutil.copytree(ROOT, clone, ignore=shutil.ignore_patterns('.git'))
    result = subprocess.run(
        ['python3', str(clone / RUNNER.relative_to(ROOT))],
        cwd=clone,
        text=True,
        capture_output=True,
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        f'exit_code={result.returncode}\n\n{result.stdout}\n{result.stderr}',
        encoding='utf-8',
    )
print(OUTPUT.relative_to(ROOT))
