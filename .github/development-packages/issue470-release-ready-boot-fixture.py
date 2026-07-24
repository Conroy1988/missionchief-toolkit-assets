#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
TEST = ROOT / '.github/scripts/test_boot_lifecycle_contract.py'
COMPLETE = ROOT / '.github/development-packages/issue470-complete-boot-fixture.py'
ABSOLUTE = ROOT / '.github/development-packages/issue470-absolute-final-boot-fixture.py'

text = TEST.read_text(encoding='utf-8')
old_schedule_target = '''function testScheduleAndDocumentStart() {
    const calls = [];
    const target = {
        runtime: { destroyed: false },
        bootStarted: false,
        STARTUP_IDLE_TIMEOUT_MS: fixtures.startupIdleTimeoutMs,
        boot() {},
        runtimeRunWhenIdle(callback, timeout) { calls.push({ callback, timeout }); }
    };
'''
new_schedule_target = '''function testScheduleAndDocumentStart() {
    const calls = [];
    const scheduleTimers = [];
    const target = {
        Math,
        runtime: { destroyed: false },
        bootStarted: false,
        STARTUP_IDLE_TIMEOUT_MS: fixtures.startupIdleTimeoutMs,
        boot() {},
        runBootIntegration(_label, callback) { return callback(); },
        runtimeRunWhenIdle(callback, timeout) { calls.push({ callback, timeout }); },
        runtimeSetTimeout(callback, delay) {
            scheduleTimers.push({ callback, delay });
            return scheduleTimers.length;
        }
    };
'''
if text.count(old_schedule_target) != 1:
    raise SystemExit(f'Schedule-boot target anchor count changed: {text.count(old_schedule_target)}')
text = text.replace(old_schedule_target, new_schedule_target, 1)

old_schedule_assertions = '''    scheduleBoot();
    assert.equal(calls.length, 1);
    assert.equal(calls[0].callback, target.boot);
    assert.equal(calls[0].timeout, fixtures.startupIdleTimeoutMs);
    target.bootStarted = true;
    scheduleBoot();
    target.bootStarted = false;
    target.runtime.destroyed = true;
    scheduleBoot();
    assert.equal(calls.length, 1, "destroyed or already-started runtime must not reschedule boot");
'''
new_schedule_assertions = '''    scheduleBoot();
    assert.equal(calls.length, 1);
    assert.equal(calls[0].callback, target.boot);
    assert.equal(calls[0].timeout, fixtures.startupIdleTimeoutMs);
    assert.equal(scheduleTimers.length, 1, "scheduleBoot must install one bounded fallback timer");
    assert.equal(scheduleTimers[0].delay, Math.min(1200, fixtures.startupIdleTimeoutMs));
    target.bootStarted = true;
    scheduleBoot();
    target.bootStarted = false;
    target.runtime.destroyed = true;
    scheduleBoot();
    assert.equal(calls.length, 1, "destroyed or already-started runtime must not reschedule idle boot");
    assert.equal(scheduleTimers.length, 1, "destroyed or already-started runtime must not add a fallback timer");
'''
if text.count(old_schedule_assertions) != 1:
    raise SystemExit(f'Schedule-boot assertion anchor count changed: {text.count(old_schedule_assertions)}')
text = text.replace(old_schedule_assertions, new_schedule_assertions, 1)
TEST.write_text(text, encoding='utf-8')

if not COMPLETE.exists():
    raise SystemExit('Complete Issue #470 boot fixture package is missing')
runpy.run_path(str(COMPLETE), run_name='__main__')

ABSOLUTE.unlink(missing_ok=True)
for diagnostic in (
    ROOT / '.github/diagnostics/issue470-boot-contract-latest.txt',
    ROOT / '.github/diagnostics/issue470-current-coordinator.txt',
    ROOT / '.github/diagnostics/issue470-boot-contract-v3.txt',
    ROOT / '.github/diagnostics/issue470-final-boot-v4.txt',
    ROOT / '.github/diagnostics/issue470-complete-boot-v5.txt',
    ROOT / '.github/diagnostics/issue470-absolute-boot-v6.txt',
):
    diagnostic.unlink(missing_ok=True)
SELF.unlink(missing_ok=True)
print('Issue #470 release-ready boot lifecycle contract passed.')
