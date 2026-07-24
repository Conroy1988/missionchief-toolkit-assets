#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
TEST = ROOT / '.github/scripts/test_boot_lifecycle_contract.py'
COMPLETE = ROOT / '.github/development-packages/issue470-complete-boot-fixture.py'

text = TEST.read_text(encoding='utf-8')
old_schedule_target = '''    const target = {
        runtime: { destroyed: false },
        bootStarted: false,
        STARTUP_IDLE_TIMEOUT_MS: fixtures.startupIdleTimeoutMs,
        boot() {},
        runtimeRunWhenIdle(callback, timeout) { calls.push({ callback, timeout }); }
    };
'''
new_schedule_target = '''    const target = {
        runtime: { destroyed: false },
        bootStarted: false,
        STARTUP_IDLE_TIMEOUT_MS: fixtures.startupIdleTimeoutMs,
        boot() {},
        runBootIntegration(_label, callback) { return callback(); },
        runtimeRunWhenIdle(callback, timeout) { calls.push({ callback, timeout }); }
    };
'''
if text.count(old_schedule_target) != 1:
    raise SystemExit(f'Schedule-boot harness anchor count changed: {text.count(old_schedule_target)}')
TEST.write_text(text.replace(old_schedule_target, new_schedule_target, 1), encoding='utf-8')

if not COMPLETE.exists():
    raise SystemExit('Complete Issue #470 boot fixture package is missing')
runpy.run_path(str(COMPLETE), run_name='__main__')

for diagnostic in (
    ROOT / '.github/diagnostics/issue470-boot-contract-latest.txt',
    ROOT / '.github/diagnostics/issue470-current-coordinator.txt',
    ROOT / '.github/diagnostics/issue470-boot-contract-v3.txt',
    ROOT / '.github/diagnostics/issue470-final-boot-v4.txt',
    ROOT / '.github/diagnostics/issue470-complete-boot-v5.txt',
):
    diagnostic.unlink(missing_ok=True)
SELF.unlink(missing_ok=True)
print('Issue #470 absolute final boot lifecycle fixture correction passed.')
