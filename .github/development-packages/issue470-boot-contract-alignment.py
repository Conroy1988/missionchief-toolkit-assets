#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
TEST = ROOT / '.github/scripts/test_boot_lifecycle_contract.py'

text = TEST.read_text(encoding='utf-8')

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

old_signature = 'function createBootEnvironment({ mapReadyAfter = 0, ensureReady = true, buildingVisibility = true } = {}) {'
new_signature = 'function createBootEnvironment({ mapReadyAfter = 0, ensureReady = true, ensureReadyAfter = null, buildingVisibility = true } = {}) {'
if text.count(old_signature) != 1:
    raise SystemExit(f'Boot environment signature anchor count changed: {text.count(old_signature)}')
text = text.replace(old_signature, new_signature, 1)

old_ensure = '    target.ensureUi = () => { ensureCalls += 1; return ensureReady; };'
new_ensure = '    target.ensureUi = () => { ensureCalls += 1; return ensureReadyAfter === null ? ensureReady : ensureCalls > ensureReadyAfter; };'
if text.count(old_ensure) != 1:
    raise SystemExit(f'Boot readiness anchor count changed: {text.count(old_ensure)}')
text = text.replace(old_ensure, new_ensure, 1)

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
    const direct = createBootEnvironment();
    direct.startBootAttemptCoordinator(100);
    assert.equal(direct.getEnsureCalls(), 1, "core UI readiness must be evaluated immediately");
    assert.equal(direct.getMapCalls(), 0, "launcher completion must not depend on Leaflet readiness");
    assert.deepEqual(direct.bootTimerDelays, []);
    assert.equal(direct.hasNamedTimer("runBootAttempt"), false);
    assert.equal(callCount(direct, "scheduleDeferredOperationalStartup"), 1);
    const directMetric = direct.calls.find(call => call.name === "recordStartupMetric");
    assert.equal(directMetric.args[2].bootAttempts, 1);

    const retried = createBootEnvironment({ ensureReadyAfter: 2 });
    retried.startBootAttemptCoordinator(100);
    assert.equal(retried.runNamedTimers("runBootAttempt", 5), 2, "core UI readiness should stop retries on the third total attempt");
    assert.equal(retried.getEnsureCalls(), 3);
    assert.equal(retried.getMapCalls(), 0);
    assert.equal(retried.bootTimerDelays.length, 2);
    assert.ok(retried.bootTimerDelays.every(delay => delay === fixtures.boot.earlyRetryDelayMs));
    assert.equal(retried.hasNamedTimer("runBootAttempt"), false);
    assert.equal(callCount(retried, "scheduleDeferredOperationalStartup"), 1);
    const retriedMetric = retried.calls.find(call => call.name === "recordStartupMetric");
    assert.equal(retriedMetric.args[2].bootAttempts, 3);
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
new_delayed = '''    const delayed = createBootEnvironment({ ensureReadyAfter: 3 });
    delayed.boot();
    assert.equal(delayed.runNamedTimers("runBootAttempt", 6), 3, "delayed core UI readiness should stop the retry chain immediately");
    assert.equal(delayed.getEnsureCalls(), 4);
    assert.equal(delayed.getMapCalls(), 0);
    assert.equal(delayed.bootTimerDelays.length, 3);
    assert.ok(delayed.bootTimerDelays.every(delay => delay === fixtures.boot.earlyRetryDelayMs));
    assert.equal(callCount(delayed, "scheduleDeferredOperationalStartup"), 1);
    const metric = delayed.calls.find(call => call.name === "recordStartupMetric");
    assert.equal(metric.args[2].bootAttempts, 4);

    const bounded = createBootEnvironment({ ensureReady: false });
    bounded.boot();
    assert.equal(
        bounded.runNamedTimers("runBootAttempt", fixtures.boot.maxAttempts),
        fixtures.boot.maxAttempts - 1,
        "failed core UI mounts must stop after the bounded retry ceiling"
    );
    assert.equal(bounded.getEnsureCalls(), fixtures.boot.maxAttempts);
    assert.equal(bounded.getMapCalls(), 0);
    assert.equal(callCount(bounded, "scheduleDeferredOperationalStartup"), 0);
    assert.equal(bounded.bootTimerDelays.length, fixtures.boot.maxAttempts - 1);
    assert.equal(bounded.bootTimerDelays[0], fixtures.boot.earlyRetryDelayMs);
    assert.ok(bounded.bootTimerDelays.includes(fixtures.boot.mediumRetryDelayMs));
    assert.equal(bounded.bootTimerDelays.at(-1), fixtures.boot.lateRetryDelayMs);
    assert.equal(bounded.hasNamedTimer("runBootAttempt"), false);
'''
if text.count(old_delayed) != 1:
    raise SystemExit(f'Boot retry fixture anchor count changed: {text.count(old_delayed)}')
text = text.replace(old_delayed, new_delayed, 1)

old_destroyed = '    const destroyed = createBootEnvironment({ mapReadyAfter: Number.POSITIVE_INFINITY, ensureReady: false });'
new_destroyed = '    const destroyed = createBootEnvironment({ ensureReady: false });'
if text.count(old_destroyed) != 1:
    raise SystemExit(f'Destroyed retry fixture anchor count changed: {text.count(old_destroyed)}')
text = text.replace(old_destroyed, new_destroyed, 1)

old_summary = 'console.log("Boot lifecycle contract passed: extracted boot coordinator and maintenance-task registration, runtime ownership, document-start, delayed map, hidden-tab resume, retry cancellation and teardown.");'
new_summary = 'console.log("Boot lifecycle contract passed: extracted map-independent boot coordinator and maintenance-task registration, runtime ownership, document-start, bounded core-UI retries, hidden-tab resume, retry cancellation and teardown.");'
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
        'Boot lifecycle contract still failed after map-independent coordinator alignment.\n'
        + result.stdout
        + result.stderr
    )

SELF.unlink(missing_ok=True)
print(result.stdout.strip())
