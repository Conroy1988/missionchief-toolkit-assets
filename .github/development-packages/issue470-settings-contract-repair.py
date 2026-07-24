#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
FIXTURE = ROOT / '.github/fixtures/settings-ui-contract.json'
DIAGNOSTIC = ROOT / '.github/diagnostics/issue470-contract-after-settings.txt'

fixture = json.loads(FIXTURE.read_text(encoding='utf-8'))
routes = fixture.get('extractedToggleEffectRoutes')
if not isinstance(routes, list) or not all(isinstance(route, str) and route for route in routes):
    raise SystemExit('Settings UI extractedToggleEffectRoutes fixture is malformed')
if 'missionAge' not in routes:
    routes.append('missionAge')
    routes.sort()
FIXTURE.write_text(json.dumps(fixture, indent=2) + '\n', encoding='utf-8')

result = subprocess.run(
    ['bash', '.github/scripts/run_userscript_preflight.sh', '--contracts'],
    cwd=ROOT,
    text=True,
    capture_output=True,
    timeout=600,
)

for path in (
    ROOT / '.github/diagnostics/issue470-contract-preflight.txt',
    ROOT / '.github/diagnostics/issue470-settings-route-diagnostic.json',
):
    path.unlink(missing_ok=True)

if result.returncode != 0:
    DIAGNOSTIC.parent.mkdir(parents=True, exist_ok=True)
    DIAGNOSTIC.write_text(
        'Issue #470 contract preflight after Settings UI repair\n'
        f'exit={result.returncode}\n\n'
        '=== STDOUT ===\n'
        + result.stdout[-50000:]
        + '\n=== STDERR ===\n'
        + result.stderr[-50000:]
        + '\n',
        encoding='utf-8',
    )
    SELF.unlink(missing_ok=True)
    print('Settings UI route fixture repaired; a later contract failure was captured for deterministic follow-up.')
else:
    DIAGNOSTIC.unlink(missing_ok=True)
    SELF.unlink(missing_ok=True)
    print(result.stdout.strip())
    print('Issue #470 aggregate contract preflight passed after Settings UI route repair.')
