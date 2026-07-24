#!/usr/bin/env python3
from __future__ import annotations

import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
FIXTURE = ROOT / '.github/fixtures/boot-lifecycle-contract.json'
ALIGNMENT = ROOT / '.github/development-packages/issue470-boot-contract-alignment.py'

fixture = json.loads(FIXTURE.read_text(encoding='utf-8'))
tasks = fixture.get('requiredTasks')
if not isinstance(tasks, list) or not all(isinstance(task, str) and task for task in tasks):
    raise SystemExit('Boot lifecycle requiredTasks fixture is malformed')
if 'ui-integrity' in tasks:
    raise SystemExit('Boot lifecycle fixture already contains ui-integrity; package is stale')

tasks.insert(0, 'ui-integrity')
FIXTURE.write_text(json.dumps(fixture, indent=2) + '\n', encoding='utf-8')

if not ALIGNMENT.exists():
    raise SystemExit('Issue #470 boot alignment package is missing')
runpy.run_path(str(ALIGNMENT), run_name='__main__')

for diagnostic in (
    ROOT / '.github/diagnostics/issue470-boot-contract-latest.txt',
    ROOT / '.github/diagnostics/issue470-current-coordinator.txt',
    ROOT / '.github/diagnostics/issue470-boot-contract-v3.txt',
):
    diagnostic.unlink(missing_ok=True)
SELF.unlink(missing_ok=True)
print('Issue #470 final boot lifecycle fixture correction passed.')
