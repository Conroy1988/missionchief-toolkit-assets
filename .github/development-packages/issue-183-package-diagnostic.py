#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / '.github' / 'development-packages' / 'issue-183-authoritative-requirements.py'
OUTPUT = ROOT / '.github' / 'diagnostics' / 'issue-183-package-result.txt'
with tempfile.TemporaryDirectory(prefix='issue-183-package-') as temp:
    clone = Path(temp) / 'repository'
    shutil.copytree(ROOT, clone, ignore=shutil.ignore_patterns('.git'))
    result = subprocess.run(['python3', str(clone / PACKAGE.relative_to(ROOT))], cwd=clone, text=True, capture_output=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(f'exit_code={result.returncode}\n\n--- STDOUT ---\n{result.stdout}\n--- STDERR ---\n{result.stderr}', encoding='utf-8')
print(OUTPUT.relative_to(ROOT))
