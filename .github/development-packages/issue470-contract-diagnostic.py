#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
OUTPUT = ROOT / '.github/diagnostics/issue470-contract-lane.txt'
env = dict(os.environ)
env['PYTHONDONTWRITEBYTECODE'] = '1'
result = subprocess.run(
    ['bash', '.github/scripts/run_userscript_preflight.sh', '--contracts'],
    cwd=ROOT,
    env=env,
    text=True,
    capture_output=True,
    timeout=300,
)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(
    '\n'.join([
        'Issue #470 deterministic contract-lane diagnostic',
        f'exit={result.returncode}',
        '',
        '=== STDOUT ===',
        result.stdout,
        '=== STDERR ===',
        result.stderr,
    ]),
    encoding='utf-8',
)
SELF.unlink(missing_ok=True)
print(OUTPUT.relative_to(ROOT))
