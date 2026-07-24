#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
TEST = ROOT / '.github/scripts/test_boot_lifecycle_contract.py'
FINAL = ROOT / '.github/development-packages/issue470-final-boot-fixture.py'

text = TEST.read_text(encoding='utf-8')
old_visibility = '''    const visibility = createBootEnvironment();
    visibility.boot();
    const listener = visibility.listenerRecords.find(item => item.target === visibility.document && item.type === "visibilitychange").listener;
    visibility.document.hidden = true;
    listener();
    assert.equal(callCount(visibility, "runtimeWakeTaskScheduler"), 0);
    assert.equal(visibility.getEnsureCalls(), 0);
    visibility.document.hidden = false;
    listener();
    assert.equal(callCount(visibility, "runtimeWakeTaskScheduler"), 1);
    assert.equal(visibility.getEnsureCalls(), 1);
'''
new_visibility = '''    const visibility = createBootEnvironment();
    visibility.boot();
    const ensureCallsAfterBoot = visibility.getEnsureCalls();
    const listener = visibility.listenerRecords.find(item => item.target === visibility.document && item.type === "visibilitychange").listener;
    visibility.document.hidden = true;
    listener();
    assert.equal(callCount(visibility, "runtimeWakeTaskScheduler"), 0);
    assert.equal(visibility.getEnsureCalls(), ensureCallsAfterBoot, "hidden-tab handling must not add a readiness check");
    visibility.document.hidden = false;
    listener();
    assert.equal(callCount(visibility, "runtimeWakeTaskScheduler"), 1);
    assert.equal(visibility.getEnsureCalls(), ensureCallsAfterBoot + 1, "visible-tab resume must perform exactly one readiness check");
'''
if text.count(old_visibility) != 1:
    raise SystemExit(f'Visibility lifecycle fixture anchor count changed: {text.count(old_visibility)}')
TEST.write_text(text.replace(old_visibility, new_visibility, 1), encoding='utf-8')

if not FINAL.exists():
    raise SystemExit('Final Issue #470 boot fixture package is missing')
runpy.run_path(str(FINAL), run_name='__main__')

for diagnostic in (
    ROOT / '.github/diagnostics/issue470-boot-contract-latest.txt',
    ROOT / '.github/diagnostics/issue470-current-coordinator.txt',
    ROOT / '.github/diagnostics/issue470-boot-contract-v3.txt',
    ROOT / '.github/diagnostics/issue470-final-boot-v4.txt',
):
    diagnostic.unlink(missing_ok=True)
SELF.unlink(missing_ok=True)
print('Issue #470 complete boot lifecycle fixture correction passed.')
