#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
OUTPUT = ROOT / '.github/diagnostics/issue464-final-package-traceback.txt'
PACKAGE = Path('.github/development-packages/issue464-complete.py')

with tempfile.TemporaryDirectory(prefix='issue464-final-trace-') as temp_dir:
    sandbox = Path(temp_dir) / 'repo'
    shutil.copytree(
        ROOT,
        sandbox,
        ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.pyo'),
    )
    result = subprocess.run(
        [sys.executable, str(sandbox / PACKAGE)],
        cwd=sandbox,
        capture_output=True,
        text=True,
        check=False,
    )
    lines = [
        'Issue #464 complete package traceback',
        f'exit_code={result.returncode}',
        '',
        '=== STDOUT ===',
        result.stdout,
        '=== STDERR ===',
        result.stderr,
        '=== REMAINING ISSUE464 FILES IN SANDBOX ===',
    ]
    for path in sorted(sandbox.rglob('*issue464*')):
        if path.is_file():
            lines.append(str(path.relative_to(sandbox)))
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text('\n'.join(lines) + '\n', encoding='utf-8')
SELF.unlink(missing_ok=True)
print(OUTPUT.relative_to(ROOT))
