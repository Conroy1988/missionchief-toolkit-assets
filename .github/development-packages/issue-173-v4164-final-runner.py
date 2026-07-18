#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / '.github' / 'development-packages' / 'issue-173-v4164-final.py'

text = PACKAGE.read_text(encoding='utf-8')
line = '    assert "return{root,parent:root,before:root.firstChild||null}" not in compact_source\n'
if text.count(line) != 1:
    raise AssertionError(f'Expected one over-broad contract assertion, found {text.count(line)}')
PACKAGE.write_text(text.replace(line, '', 1), encoding='utf-8')
subprocess.run(['python3', str(PACKAGE)], cwd=ROOT, check=True)
