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
    assert.equal(direct.runNamedTimers("runBootAttempt", 3), 2, "map readiness should stop retries after the third total attempt");
    assert.equal(direct.getMapCalls(), 3);
    assert.deepEqual(direct.bootTimerDelays, [
        fixtures.boot.initialDelayMs,
        fixtures.boot.earlyRetryDelayMs
    ]);
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
'''
new_delayed = '''    const delayed = createBootEnvironment({ mapReadyAfter: 3 });
    delayed.boot();
    assert.equal(delayed.runNamedTimers("runBootAttempt", 4), 3, "delayed map readiness should stop the retry chain immediately");
    assert.equal(delayed.getMapCalls(), 4);
    assert.deepEqual(delayed.bootTimerDelays, [fixtures.boot.initialDelayMs, fixtures.boot.earlyRetryDelayMs, fixtures.boot.earlyRetryDelayMs]);
'''
if text.count(old_delayed) != 1:
    raise SystemExit(f'Delayed coordinator fixture anchor count changed: {text.count(old_delayed)}')
text = text.replace(old_delayed, new_delayed, 1)

old_fallback = '''    const fallback = createBootEnvironment({ mapReadyAfter: Number.POSITIVE_INFINITY });
    fallback.boot();
    for (let attempt = 0; attempt < fixtures.boot.mapFallbackAttempt; attempt += 1) fallback.runNamedTimer("runBootAttempt");
    assert.equal(fallback.getMapCalls(), fixtures.boot.mapFallbackAttempt);
    assert.equal(callCount(fallback, "scheduleDeferredOperationalStartup"), 1, "UI must continue after bounded map fallback");
    assert.equal(fallback.bootTimerDelays.length, fixtures.boot.mapFallbackAttempt);
'''
new_fallback = '''    const fallback = createBootEnvironment({ mapReadyAfter: Number.POSITIVE_INFINITY });
    fallback.boot();
    assert.equal(
        fallback.runNamedTimers("runBootAttempt", fixtures.boot.mapFallbackAttempt),
        fixtures.boot.mapFallbackAttempt - 1,
        "bounded map fallback should include the immediate first attempt and leave no redundant retry"
    );
    assert.equal(fallback.getMapCalls(), fixtures.boot.mapFallbackAttempt);
    assert.equal(callCount(fallback, "scheduleDeferredOperationalStartup"), 1, "UI must continue after bounded map fallback");
    assert.equal(fallback.bootTimerDelays.length, fixtures.boot.mapFallbackAttempt - 1);
'''
if text.count(old_fallback) != 1:
    raise SystemExit(f'Fallback coordinator fixture anchor count changed: {text.count(old_fallback)}')
text = text.replace(old_fallback, new_fallback, 1)

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
        'Boot lifecycle contract still failed after Issue #470 alignment.\n'
        + result.stdout
        + result.stderr
    )

SELF.unlink(missing_ok=True)
print(result.stdout.strip())
