#!/usr/bin/env python3
from __future__ import annotations
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / '.github/development-packages/issue458-performance-budget.py'
SELF = Path(__file__).resolve()
DIAGNOSTIC = ROOT / '.github/diagnostics/issue458-performance-apply-validator.txt'
if not ORIGINAL.exists():
    raise SystemExit('Original performance correction package is missing')
namespace = {'__file__': str(ORIGINAL), '__name__': '__main__'}
exec(compile(ORIGINAL.read_text(encoding='utf-8'), str(ORIGINAL), 'exec'), namespace)
ORIGINAL.unlink(missing_ok=True)
SELF.unlink(missing_ok=True)
result = subprocess.run(
    ['python3', '.github/scripts/validate_userscript.py'],
    cwd=ROOT,
    text=True,
    capture_output=True,
)
output = (result.stdout or '') + ('\n--- STDERR ---\n' + result.stderr if result.stderr else '')
subprocess.run(['git', 'restore', '--source=HEAD', '--worktree', '--', '.'], cwd=ROOT, check=True)
ORIGINAL.unlink(missing_ok=True)
SELF.unlink(missing_ok=True)
DIAGNOSTIC.parent.mkdir(parents=True, exist_ok=True)
DIAGNOSTIC.write_text(
    'Issue #458 v5.0.5 performance correction apply-state validator\n'
    f'exit_code={result.returncode}\n\n{output[-20000:]}',
    encoding='utf-8',
)
print(f'Captured apply-state validator exit {result.returncode}; production source restored.')
