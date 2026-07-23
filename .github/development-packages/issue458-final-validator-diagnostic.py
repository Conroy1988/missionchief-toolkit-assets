#!/usr/bin/env python3
from __future__ import annotations
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
FINAL = ROOT / '.github/development-packages/issue458-performance-budget-final.py'
OUTPUT = ROOT / '.github/diagnostics/issue458-final-validator.txt'
if not FINAL.exists():
    raise SystemExit('Final performance package is missing')
with tempfile.TemporaryDirectory(prefix='issue458-final-validator-') as tmp:
    sandbox = Path(tmp) / 'repo'
    shutil.copytree(ROOT, sandbox, ignore=shutil.ignore_patterns('.git'))
    package = sandbox / '.github/development-packages/issue458-performance-budget-final.py'
    applied = subprocess.run(['python3', str(package)], cwd=sandbox, text=True, capture_output=True)
    validated = subprocess.run(['python3', '.github/scripts/validate_userscript.py'], cwd=sandbox, text=True, capture_output=True)
    checked = subprocess.run(['node', '--check', 'src/MissionChief_Map_Command_Toolkit.user.js'], cwd=sandbox, text=True, capture_output=True)
    report = (
        'Issue #458 final v5.0.5 publish-state diagnostic\n'
        f'package_exit={applied.returncode}\n'
        f'validator_exit={validated.returncode}\n'
        f'syntax_exit={checked.returncode}\n\n'
        '=== PACKAGE STDOUT ===\n' + (applied.stdout or '') +
        '\n=== PACKAGE STDERR ===\n' + (applied.stderr or '') +
        '\n=== VALIDATOR STDOUT ===\n' + (validated.stdout or '') +
        '\n=== VALIDATOR STDERR ===\n' + (validated.stderr or '') +
        '\n=== SYNTAX STDERR ===\n' + (checked.stderr or '')
    )
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(report[-30000:], encoding='utf-8')
SELF.unlink(missing_ok=True)
print(f'Captured final validator state: package={applied.returncode}, validator={validated.returncode}, syntax={checked.returncode}')
