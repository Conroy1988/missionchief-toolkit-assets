#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
OUTPUT = ROOT / '.github/diagnostics/issue464-complete-v2-traceback.txt'
with tempfile.TemporaryDirectory(prefix='issue464-v2-trace-') as temp:
    sandbox = Path(temp) / 'repo'
    shutil.copytree(ROOT, sandbox, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc'))
    package = sandbox / '.github/development-packages/issue464-complete-v2.py'
    env = dict(os.environ)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    result = subprocess.run(['python3', str(package)], cwd=sandbox, env=env, text=True, capture_output=True)
    lines = [
        'Issue #464 complete-v2 package traceback',
        f'package_exit={result.returncode}',
        '',
        '=== PACKAGE STDOUT ===',
        result.stdout,
        '=== PACKAGE STDERR ===',
        result.stderr,
    ]
    if result.returncode == 0:
        validator = subprocess.run(['python3', '.github/scripts/validate_userscript.py'], cwd=sandbox, env=env, text=True, capture_output=True)
        syntax = subprocess.run(['node', '--check', 'src/MissionChief_Map_Command_Toolkit.user.js'], cwd=sandbox, env=env, text=True, capture_output=True)
        lines.extend([
            f'validator_exit={validator.returncode}',
            f'syntax_exit={syntax.returncode}',
            '',
            '=== VALIDATOR STDOUT ===', validator.stdout,
            '=== VALIDATOR STDERR ===', validator.stderr,
            '=== SYNTAX STDOUT ===', syntax.stdout,
            '=== SYNTAX STDERR ===', syntax.stderr,
        ])
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text('\n'.join(lines), encoding='utf-8')
SELF.unlink(missing_ok=True)
print(OUTPUT.relative_to(ROOT))
