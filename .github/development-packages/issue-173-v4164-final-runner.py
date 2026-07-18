#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / '.github' / 'development-packages' / 'issue-173-v4164-final.py'

lines = PACKAGE.read_text(encoding='utf-8').splitlines()
token = 'return{root,parent:root,before:root.firstChild||null}'
matches = [index for index, line in enumerate(lines) if token in line]
if len(matches) != 1:
    raise AssertionError(f'Expected one over-broad contract assertion, found {len(matches)}')
del lines[matches[0]]
PACKAGE.write_text('\n'.join(lines) + '\n', encoding='utf-8')
subprocess.run(['python3', str(PACKAGE)], cwd=ROOT, check=True)
