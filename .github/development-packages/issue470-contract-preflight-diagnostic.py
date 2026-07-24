#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
OUTPUT = ROOT / '.github/diagnostics/issue470-contract-preflight.txt'

result = subprocess.run(
    ['bash', '.github/scripts/run_userscript_preflight.sh', '--contracts'],
    cwd=ROOT,
    text=True,
    capture_output=True,
    timeout=600,
)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(
    'Issue #470 aggregate contract preflight diagnostic\n'
    f'exit={result.returncode}\n\n'
    '=== STDOUT ===\n'
    + result.stdout[-40000:]
    + '\n=== STDERR ===\n'
    + result.stderr[-40000:]
    + '\n',
    encoding='utf-8',
)
SELF.unlink(missing_ok=True)
print(f'Aggregate contract diagnostic captured with exit {result.returncode}.')
