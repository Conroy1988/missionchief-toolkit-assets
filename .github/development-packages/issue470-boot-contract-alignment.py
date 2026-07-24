#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
TEST = ROOT / '.github/scripts/test_boot_lifecycle_contract.py'

text = TEST.read_text(encoding='utf-8')

function_anchor = '''    "runtimeRunWhenIdle",
    "startBootAttemptCoordinator",
'''
function_replacement = '''    "runtimeRunWhenIdle",
    "runBootIntegration",
    "startBootAttemptCoordinator",
'''
if text.count(function_anchor) != 1:
    raise SystemExit(f'Boot helper function-list anchor count changed: {text.count(function_anchor)}')
text = text.replace(function_anchor, function_replacement, 1)

replacement_anchor = '''        "__RUNTIME_RUN_WHEN_IDLE__": functions["runtimeRunWhenIdle"],
        "__BOOT__": functions["boot"],
'''
replacement_value = '''        "__RUNTIME_RUN_WHEN_IDLE__": functions["runtimeRunWhenIdle"],
        "__BOOT_INTEGRATION__": functions["runBootIntegration"],
        "__BOOT__": functions["boot"],
'''
if text.count(replacement_anchor) != 1:
    raise SystemExit(f'Boot helper replacement-map anchor count changed: {text.count(replacement_anchor)}')
text = text.replace(replacement_anchor, replacement_value, 1)

compile_anchor = '''    target.startBootAttemptCoordinator = compileInSandbox(__BOOT_COORDINATOR_SOURCE__, sandbox);
    target.registerBootMaintenanceTasks = compileInSandbox(__BOOT_TASK_REGISTRATION_SOURCE__, sandbox);
'''
compile_value = '''    target.runBootIntegration = compileInSandbox(__BOOT_INTEGRATION_SOURCE__, sandbox);
    target.startBootAttemptCoordinator = compileInSandbox(__BOOT_COORDINATOR_SOURCE__, sandbox);
    target.registerBootMaintenanceTasks = compileInSandbox(__BOOT_TASK_REGISTRATION_SOURCE__, sandbox);
'''
if text.count(compile_anchor) != 1:
    raise SystemExit(f'Boot harness compile anchor count changed: {text.count(compile_anchor)}')
text = text.replace(compile_anchor, compile_value, 1)

bottom_anchor = '''    replacements["__BOOT_COORDINATOR_SOURCE__"] = json.dumps(functions["startBootAttemptCoordinator"])
    replacements["__BOOT_TASK_REGISTRATION_SOURCE__"] = json.dumps(functions["registerBootMaintenanceTasks"])
'''
bottom_value = '''    replacements["__BOOT_INTEGRATION_SOURCE__"] = json.dumps(functions["runBootIntegration"])
    replacements["__BOOT_COORDINATOR_SOURCE__"] = json.dumps(functions["startBootAttemptCoordinator"])
    replacements["__BOOT_TASK_REGISTRATION_SOURCE__"] = json.dumps(functions["registerBootMaintenanceTasks"])
'''
if text.count(bottom_anchor) != 1:
    raise SystemExit(f'Boot helper source-injection anchor count changed: {text.count(bottom_anchor)}')
text = text.replace(bottom_anchor, bottom_value, 1)

old_timer_helper = '''    target.runNamedTimer = name => {
        const timer = Array.from(timers.values()).find(entry => entry.name === name);
        assert.ok(timer, `Missing ${name} timer`);
        timer.run();
    };
'''
new_timer_helper = '''    target.runNamedTimer = name => {
        const timer = Array.from(timers.values()).find(entry => entry.name === name);
        assert.ok(timer, `Missing ${name} timer`);
        timer.run();
    };
    target.hasNamedTimer = name => Array.from(timers.values()).some(entry => entry.name === name);
    target.runNamedTimers = (name, limit) => {
        let runs = 0;
        while (runs < limit && target.hasNamedTimer(name)) {
            target.runNamedTimer(name);
            runs += 1;
        }
        return runs;
    };
'''
if text.count(old_timer_helper) != 1:
    raise SystemExit(f'Boot timer helper anchor count changed: {text.count(old_timer_helper)}')
text = text.replace(old_timer_helper, new_timer_helper, 1)

old_direct = '''function testBootAttemptCoordinatorDirectly() {
    const direct = createBootEnvironment({ mapReadyAfter: 2 });
    direct.startBootAttemptCoordinator(100);
    for (let attempt = 0; attempt < 3; attempt += 1) direct.runNamedTimer("runBootAttempt");
    assert.equal(direct.getMapCalls(), 3);
    assert.deepEqual(direct.bootTimerDelays, [
        fixtures.boot.initialDelayMs,
        fixtures.boot.earlyRetryDelayMs,
        fixtures.boot.earlyRetryDelayMs
    ]);
    assert.equal(callCount(direct, "scheduleDeferredOperationalStartup"), 1);
    const metric = direct.calls.find(call => call.name === "recordStartupMetric");
    assert.equal(metric.args[2].bootAttempts, 3);
}
'''
new_direct = '''function testBootAttemptCoordinatorDirectly() {
    const direct = createBootEnvironment({ mapReadyAfter: 2 });
    direct.startBootAttemptCoordinator(100);
    assert.equal(
        direct.runNamedTimers("runBootAttempt", 3),
        2,
        "the immediate first attempt plus two retries should complete when the map appears"
    );
    assert.equal(direct.getEnsureCalls(), 3);
    assert.equal(direct.getMapCalls(), 3);
    assert.deepEqual(direct.bootTimerDelays, [
        fixtures.boot.earlyRetryDelayMs,
        fixtures.boot.earlyRetryDelayMs
    ]);
    assert.equal(direct.hasNamedTimer("runBootAttempt"), false);
    assert.equal(callCount(direct, "scheduleDeferredOperationalStartup"), 1);
    const metric = direct.calls.find(call => call.name === "recordStartupMetric");
    assert.equal(metric.args[2].bootAttempts, 3);
}
'''
if text.count(old_direct) != 1:
    raise SystemExit(f'Direct coordinator fixture anchor count changed: {text.count(old_direct)}')
text = text.replace(old_direct, new_direct, 1)

old_delayed = '''    const delayed = createBootEnvironment({ mapReadyAfter: 3 });
    delayed.boot();
    for (let attempt = 0; attempt < 4; attempt += 1) delayed.runNamedTimer("runBootAttempt");
    assert.equal(delayed.getMapCalls(), 4);
    assert.deepEqual(delayed.bootTimerDelays, [fixtures.boot.initialDelayMs, fixtures.boot.earlyRetryDelayMs, fixtures.boot.earlyRetryDelayMs, fixtures.boot.earlyRetryDelayMs]);
    assert.equal(callCount(delayed, "scheduleDeferredOperationalStartup"), 1);
    const metric = delayed.calls.find(call => call.name === "recordStartupMetric");
    assert.equal(metric.args[2].bootAttempts, 4);

    const fallback = createBootEnvironment({ mapReadyAfter: Number.POSITIVE_INFINITY });
    fallback.boot();
    for (let attempt = 0; attempt < fixtures.boot.mapFallbackAttempt; attempt += 1) fallback.runNamedTimer("runBootAttempt");
    assert.equal(fallback.getMapCalls(), fixtures.boot.mapFallbackAttempt);
    assert.equal(callCount(fallback, "scheduleDeferredOperationalStartup"), 1, "UI must continue after bounded map fallback");
    assert.equal(fallback.bootTimerDelays.length, fixtures.boot.mapFallbackAttempt);
'''
new_delayed = '''    const delayed = createBootEnvironment({ mapReadyAfter: 3 });
    delayed.boot();
    assert.equal(
        delayed.runNamedTimers("runBootAttempt", 4),
        3,
        "delayed map readiness should stop the retry chain after the fourth total attempt"
    );
    assert.equal(delayed.getEnsureCalls(), 4);
    assert.equal(delayed.getMapCalls(), 4);
    assert.deepEqual(delayed.bootTimerDelays, [fixtures.boot.earlyRetryDelayMs, fixtures.boot.earlyRetryDelayMs, fixtures.boot.earlyRetryDelayMs]);
    assert.equal(delayed.hasNamedTimer("runBootAttempt"), false);
    assert.equal(callCount(delayed, "scheduleDeferredOperationalStartup"), 1);
    const metric = delayed.calls.find(call => call.name === "recordStartupMetric");
    assert.equal(metric.args[2].bootAttempts, 4);

    const fallback = createBootEnvironment({ mapReadyAfter: Number.POSITIVE_INFINITY });
    fallback.boot();
    assert.equal(
        fallback.runNamedTimers("runBootAttempt", fixtures.boot.mapFallbackAttempt),
        fixtures.boot.mapFallbackAttempt - 1,
        "bounded map fallback includes the immediate first attempt and must leave no redundant retry"
    );
    assert.equal(fallback.getEnsureCalls(), fixtures.boot.mapFallbackAttempt);
    assert.equal(fallback.getMapCalls(), fixtures.boot.mapFallbackAttempt);
    assert.equal(callCount(fallback, "scheduleDeferredOperationalStartup"), 1, "UI must continue after bounded map fallback");
    assert.equal(fallback.bootTimerDelays.length, fixtures.boot.mapFallbackAttempt - 1);
    assert.equal(fallback.hasNamedTimer("runBootAttempt"), false);
'''
if text.count(old_delayed) != 1:
    raise SystemExit(f'Delayed/fallback coordinator fixture anchor count changed: {text.count(old_delayed)}')
text = text.replace(old_delayed, new_delayed, 1)

old_summary = 'console.log("Boot lifecycle contract passed: extracted boot coordinator and maintenance-task registration, runtime ownership, document-start, delayed map, hidden-tab resume, retry cancellation and teardown.");'
new_summary = 'console.log("Boot lifecycle contract passed: extracted boot integration, immediate coordinator attempt, bounded map fallback, maintenance-task registration, runtime ownership, document-start, hidden-tab resume, retry cancellation and teardown.");'
if text.count(old_summary) != 1:
    raise SystemExit(f'Boot contract summary anchor count changed: {text.count(old_summary)}')
text = text.replace(old_summary, new_summary, 1)

TEST.write_text(text, encoding='utf-8')

env = dict(os.environ)
env['PYTHONDONTWRITEBYTECODE'] = '1'
result = subprocess.run(
    ['python3', '.github/scripts/test_boot_lifecycle_contract.py'],
    cwd=ROOT,
    env=env,
    text=True,
    capture_output=True,
    timeout=300,
)
if result.returncode != 0:
    raise SystemExit(
        'Boot lifecycle contract still failed after binding the real boot integration helper.\n'
        + result.stdout
        + result.stderr
    )

for diagnostic in (
    ROOT / '.github/diagnostics/issue470-boot-contract-latest.txt',
    ROOT / '.github/diagnostics/issue470-current-coordinator.txt',
):
    diagnostic.unlink(missing_ok=True)
SELF.unlink(missing_ok=True)
print(result.stdout.strip())
