#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / '.github' / 'development-packages' / 'issue-176-custom-vehicle-badges.py'
text = PACKAGE.read_text(encoding='utf-8')
old = '''if map_count != 2:
    raise AssertionError(f"toggle UI maps: expected two missionRequirements entries, found {map_count}")'''
new = '''if map_count != 1:
    raise AssertionError(f"toggle UI map: expected one missionRequirements entry, found {map_count}")'''
if text.count(old) != 1:
    raise AssertionError(f'Expected one UI map count contract, found {text.count(old)}')
PACKAGE.write_text(text.replace(old, new, 1), encoding='utf-8')
subprocess.run(['python3', str(PACKAGE)], cwd=ROOT, check=True)
