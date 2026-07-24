#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
OUTPUT = ROOT / '.github/diagnostics/issue470-ci-correction-validation.txt'

with tempfile.TemporaryDirectory(prefix='issue470-ci-correction-') as temporary:
    sandbox = Path(temporary) / 'repo'
    shutil.copytree(
        ROOT,
        sandbox,
        ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.pyo'),
    )
    env = dict(os.environ)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    package = subprocess.run(
        ['python3', '.github/development-packages/issue470-ci-correction.py'],
        cwd=sandbox,
        env=env,
        text=True,
        capture_output=True,
        timeout=300,
    )
    body = [
        'Issue #470 CI correction validation diagnostic',
        f'package_exit={package.returncode}',
        '',
        '=== PACKAGE STDOUT ===',
        package.stdout,
        '=== PACKAGE STDERR ===',
        package.stderr,
    ]
    if package.returncode == 0:
        validator = subprocess.run(
            ['python3', '.github/scripts/validate_userscript.py'],
            cwd=sandbox,
            env=env,
            text=True,
            capture_output=True,
            timeout=300,
        )
        syntax = subprocess.run(
            ['node', '--check', 'src/MissionChief_Map_Command_Toolkit.user.js'],
            cwd=sandbox,
            env=env,
            text=True,
            capture_output=True,
            timeout=120,
        )
        runtime = subprocess.run(
            ['node', '.github/scripts/test_issue470_menu_requirements_runtime.js'],
            cwd=sandbox,
            env=env,
            text=True,
            capture_output=True,
            timeout=120,
        )
        body.extend([
            f'validator_exit={validator.returncode}',
            f'syntax_exit={syntax.returncode}',
            f'runtime_exit={runtime.returncode}',
            '',
            '=== VALIDATOR STDOUT ===',
            validator.stdout,
            '=== VALIDATOR STDERR ===',
            validator.stderr,
            '=== SYNTAX STDOUT ===',
            syntax.stdout,
            '=== SYNTAX STDERR ===',
            syntax.stderr,
            '=== RUNTIME STDOUT ===',
            runtime.stdout,
            '=== RUNTIME STDERR ===',
            runtime.stderr,
        ])

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text('\n'.join(body), encoding='utf-8')
SELF.unlink(missing_ok=True)
print(OUTPUT.relative_to(ROOT))
