#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELF = Path(__file__).resolve()
TEST = ROOT / '.github/scripts/test_boot_lifecycle_contract.py'

text = TEST.read_text(encoding='utf-8')

start = text.index('function testBootAttemptCoordinatorDirectly() {')
end = text.index('\nfunction testBootMaintenanceTaskRegistrationDirectly()', start)
replacement = r'''function testBootAttemptCoordinatorDirectly() {
    const direct = createBootEnvironment({ mapReadyAfter: Number.POSITIVE_INFINITY });
    direct.startBootAttemptCoordinator(100);
    assert.equal(direct.getEnsureCalls(), 1, "the map-independent launcher should mount on the immediate coordinator attempt");
    assert.equal(direct.getMapCalls(), 0, "the coordinator must not wait for Leaflet after the core UI reports ready");
    assert.equal(direct.runNamedTimers("runBootAttempt", 3), 0, "a ready core UI must not leave redundant boot retries");
    assert.deepEqual(direct.bootTimerDelays, []);
    assert.equal(direct.hasNamedTimer("runBootAttempt"), false);
    assert.equal(callCount(direct, "scheduleDeferredOperationalStartup"), 1);
    const metric = direct.calls.find(call => call.name === "recordStartupMetric");
    assert.equal(metric.args[2].bootAttempts, 1);

    const retrying = createBootEnvironment({ mapReadyAfter: Number.POSITIVE_INFINITY, ensureReady: false });
    retrying.startBootAttemptCoordinator(100);
    assert.equal(retrying.getEnsureCalls(), 1, "an unavailable core UI must still perform the immediate first attempt");
    assert.equal(retrying.hasNamedTimer("runBootAttempt"), true, "an unavailable core UI must schedule a bounded retry");
    assert.equal(retrying.runNamedTimers("runBootAttempt", 3), 3);
    assert.equal(retrying.getEnsureCalls(), 4);
    assert.equal(retrying.bootTimerDelays.length, 4, "the initial failure and each retry should schedule the next bounded attempt");
    assert.equal(retrying.bootTimerDelays.every(delay => delay === fixtures.boot.earlyRetryDelayMs), true);
}'''
text = text[:start] + replacement + text[end:]

old = r'''    const delayed = createBootEnvironment({ mapReadyAfter: 3 });
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
    assert.equal(fallback.hasNamedTimer("runBootAttempt"), false);'''
new = r'''    const mapIndependent = createBootEnvironment({ mapReadyAfter: Number.POSITIVE_INFINITY });
    mapIndependent.boot();
    assert.equal(mapIndependent.getEnsureCalls(), 1, "boot should complete after the immediate map-independent UI mount");
    assert.equal(mapIndependent.getMapCalls(), 0, "boot completion must not depend on Leaflet readiness");
    assert.equal(mapIndependent.runNamedTimers("runBootAttempt", 4), 0);
    assert.equal(mapIndependent.hasNamedTimer("runBootAttempt"), false);
    assert.equal(callCount(mapIndependent, "scheduleDeferredOperationalStartup"), 1);
    const metric = mapIndependent.calls.find(call => call.name === "recordStartupMetric");
    assert.equal(metric.args[2].bootAttempts, 1);

    const fallback = createBootEnvironment({ mapReadyAfter: Number.POSITIVE_INFINITY, ensureReady: false });
    fallback.boot();
    assert.equal(
        fallback.runNamedTimers("runBootAttempt", fixtures.boot.mapFallbackAttempt),
        fixtures.boot.mapFallbackAttempt - 1,
        "bounded fallback includes the immediate first attempt and must leave no redundant retry"
    );
    assert.equal(fallback.getEnsureCalls(), fixtures.boot.mapFallbackAttempt);
    assert.equal(callCount(fallback, "scheduleDeferredOperationalStartup"), 1, "the runtime must continue after the bounded UI fallback");
    assert.equal(fallback.bootTimerDelays.length, fixtures.boot.mapFallbackAttempt - 1);
    assert.equal(fallback.hasNamedTimer("runBootAttempt"), false);'''
if text.count(old) != 1:
    raise SystemExit(f'Boot lifecycle map-dependent block count changed: {text.count(old)}')
text = text.replace(old, new, 1)

text = text.replace(
    'Boot lifecycle contract passed: extracted boot integration, immediate coordinator attempt, bounded map fallback, maintenance-task registration, runtime ownership, document-start, hidden-tab resume, retry cancellation and teardown.',
    'Boot lifecycle contract passed: extracted boot integration, immediate map-independent coordinator completion, bounded UI fallback, maintenance-task registration, runtime ownership, document-start, hidden-tab resume, retry cancellation and teardown.',
    1,
)
TEST.write_text(text, encoding='utf-8')

result = subprocess.run(
    ['bash', '.github/scripts/run_userscript_preflight.sh', '--contracts'],
    cwd=ROOT,
    text=True,
    capture_output=True,
    timeout=900,
)
if result.returncode != 0:
    raise SystemExit(
        'Issue #470 final contract preflight failed.\n\nSTDOUT:\n'
        + result.stdout[-80000:]
        + '\nSTDERR:\n'
        + result.stderr[-80000:]
    )

for path in (ROOT / '.github/development-packages').glob('issue470-*.py'):
    if path.resolve() != SELF.resolve():
        path.unlink(missing_ok=True)
for path in (ROOT / '.github/diagnostics').glob('issue470-*'):
    path.unlink(missing_ok=True)
SELF.unlink(missing_ok=True)
print(result.stdout.strip())
print('Issue #470 final boot lifecycle contract aligned and full contract preflight passed.')
