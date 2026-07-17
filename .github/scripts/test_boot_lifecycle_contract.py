#!/usr/bin/env python3
"""Fixture-backed lifecycle contract for the exact Toolkit runtime and boot code."""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path

import full_userscript_audit as audit

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "MissionChief_Map_Command_Toolkit.user.js"
FIXTURE = ROOT / ".github" / "fixtures" / "boot-lifecycle-contract.json"
FUNCTION_NAMES = [
    "runtimeSetTimeout",
    "runtimeClearTimeout",
    "runtimeListen",
    "runtimeTrackObserver",
    "runtimeUntrackObserver",
    "runtimeOnCleanup",
    "runtimeRunWhenIdle",
    "boot",
    "scheduleBoot",
]


def extract_function(source: str, masked: str, name: str) -> str:
    pattern = re.compile(rf"\b(?:async\s+)?function\s+{re.escape(name)}\s*\(")
    matches = list(pattern.finditer(masked))
    if len(matches) != 1:
        raise AssertionError(f"Expected one declaration for {name}, found {len(matches)}")
    start = matches[0].start()
    parameter_open = masked.find("(", start)
    if parameter_open < 0:
        raise AssertionError(f"Parameter list not found for {name}")
    depth = 0
    parameter_close = None
    for index in range(parameter_open, len(masked)):
        char = masked[index]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                parameter_close = index
                break
    if parameter_close is None:
        raise AssertionError(f"Parameter list did not close for {name}")
    opening = masked.find("{", parameter_close + 1)
    closing = audit.matching_brace(masked, opening)
    if opening < 0 or closing is None:
        raise AssertionError(f"Unable to extract {name}")
    return source[start:closing + 1]


def extract_runtime_block(source: str) -> str:
    start = source.find("const RUNTIME_KEY =")
    marker = "pageWindow[RUNTIME_KEY] = runtime;"
    end = source.find(marker, start)
    if start < 0 or end < 0:
        raise AssertionError("Runtime ownership block not found")
    return source[start:end + len(marker)]


def extract_bootstrap_tail(source: str) -> str:
    start = source.rfind("if (document.readyState === 'loading')")
    end = source.rfind("})();")
    if start < 0 or end <= start:
        raise AssertionError("Final document-start bootstrap block not found")
    return source[start:end]


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    fixtures = json.loads(FIXTURE.read_text(encoding="utf-8"))
    masked = audit.mask_non_code(source)
    functions = {name: extract_function(source, masked, name) for name in FUNCTION_NAMES}
    runtime_block = extract_runtime_block(source)
    bootstrap_tail = extract_bootstrap_tail(source)

    assert fixtures["runtimeKey"] in runtime_block
    assert fixtures["replacementReason"] in runtime_block
    for task in fixtures["requiredTasks"]:
        assert f"runtimeRegisterTask('{task}'" in functions["boot"], f"Missing boot task {task}"
    for attribute in fixtures["cleanupRootAttributes"]:
        assert attribute in functions["boot"], f"Missing cleanup attribute {attribute}"

    replacements = {
        "__FIXTURES__": json.dumps(fixtures, ensure_ascii=False),
        "__RUNTIME_BLOCK__": runtime_block,
        "__RUNTIME_SET_TIMEOUT__": functions["runtimeSetTimeout"],
        "__RUNTIME_CLEAR_TIMEOUT__": functions["runtimeClearTimeout"],
        "__RUNTIME_LISTEN__": functions["runtimeListen"],
        "__RUNTIME_TRACK_OBSERVER__": functions["runtimeTrackObserver"],
        "__RUNTIME_UNTRACK_OBSERVER__": functions["runtimeUntrackObserver"],
        "__RUNTIME_ON_CLEANUP__": functions["runtimeOnCleanup"],
        "__RUNTIME_RUN_WHEN_IDLE__": functions["runtimeRunWhenIdle"],
        "__BOOT__": functions["boot"],
        "__SCHEDULE_BOOT__": functions["scheduleBoot"],
        "__BOOTSTRAP_TAIL__": bootstrap_tail,
    }
    harness = r'''"use strict";
const assert = require("node:assert/strict");
const fixtures = __FIXTURES__;

function createPageWindow({ idle = true } = {}) {
    let nextTimerId = 1;
    let nextIdleId = 1000;
    const timers = new Map();
    const idleCallbacks = new Map();
    const clearedTimeouts = [];
    const clearedIntervals = [];
    const cancelledFrames = [];
    const cancelledIdle = [];
    const target = {
        timers, idleCallbacks, clearedTimeouts, clearedIntervals, cancelledFrames, cancelledIdle,
        setTimeout(callback, delay = 0, ...args) {
            const id = nextTimerId++;
            timers.set(id, { callback, delay, args });
            return id;
        },
        clearTimeout(id) { clearedTimeouts.push(id); timers.delete(id); },
        setInterval() { return nextTimerId++; },
        clearInterval(id) { clearedIntervals.push(id); },
        requestAnimationFrame() { return nextTimerId++; },
        cancelAnimationFrame(id) { cancelledFrames.push(id); },
        addEventListener() {},
        removeEventListener() {},
        visualViewport: null,
        matchMedia() { return null; },
        performance: { now: () => 100 },
    };
    if (idle) {
        target.requestIdleCallback = (callback, options) => {
            const id = nextIdleId++;
            idleCallbacks.set(id, { callback, options });
            return id;
        };
        target.cancelIdleCallback = id => { cancelledIdle.push(id); idleCallbacks.delete(id); };
    }
    target.runTimer = id => {
        const timer = timers.get(id);
        assert.ok(timer, `Missing timer ${id}`);
        timers.delete(id);
        timer.callback(...timer.args);
    };
    target.runIdle = id => {
        const entry = idleCallbacks.get(id);
        assert.ok(entry, `Missing idle callback ${id}`);
        idleCallbacks.delete(id);
        entry.callback({ didTimeout: false, timeRemaining: () => 50 });
    };
    return target;
}

function installRuntime(pageWindow, SCRIPT) {
__RUNTIME_BLOCK__
    return runtime;
}

function buildRuntimeHelpers(pageWindow, runtime) {
    const STARTUP_IDLE_TIMEOUT_MS = fixtures.startupIdleTimeoutMs;
__RUNTIME_SET_TIMEOUT__
__RUNTIME_CLEAR_TIMEOUT__
__RUNTIME_LISTEN__
__RUNTIME_TRACK_OBSERVER__
__RUNTIME_UNTRACK_OBSERVER__
__RUNTIME_ON_CLEANUP__
__RUNTIME_RUN_WHEN_IDLE__
    return { runtimeSetTimeout, runtimeClearTimeout, runtimeListen, runtimeTrackObserver, runtimeUntrackObserver, runtimeOnCleanup, runtimeRunWhenIdle };
}

function testRuntimeOwnershipAndTeardown() {
    const key = fixtures.runtimeKey;
    const replaced = [];
    const pageWindow = createPageWindow();
    pageWindow[key] = {
        version: "4.14.7",
        destroyed: false,
        destroy(reason) { replaced.push(reason); this.destroyed = true; }
    };
    const runtime = installRuntime(pageWindow, { version: "4.14.8" });
    assert.equal(replaced.length, 1);
    assert.equal(replaced[0], fixtures.replacementReason);
    assert.equal(pageWindow[key], runtime);
    assert.equal(installRuntime(pageWindow, { version: "4.14.8" }), undefined, "same version must not create a duplicate runtime");
    assert.equal(pageWindow[key], runtime);

    const events = [];
    runtime.timeouts.add(11);
    runtime.intervals.add(12);
    runtime.animationFrames.add(13);
    runtime.waiters.add(value => events.push(`waiter:${value}`));
    runtime.requests.add({ abort() { events.push("request:abort"); } });
    runtime.fetchControllers.add({ abort() { events.push("controller:abort"); } });
    runtime.observers.add({ disconnect() { events.push("observer:disconnect"); } });
    runtime.listeners.push({ target: { removeEventListener(type) { events.push(`listener:${type}`); } }, type: "click", listener() {}, options: true });
    runtime.mapBindings.push({ map: { off(types) { events.push(`map:${types}`); } }, types: "move zoom", handler() {} });
    runtime.hookRestorers.push(() => events.push("restore:first"), () => events.push("restore:second"));
    runtime.cleanupCallbacks.push(() => events.push("cleanup:first"), () => events.push("cleanup:second"));
    runtime.destroy("fixture teardown");
    assert.equal(runtime.destroyed, true);
    assert.equal(pageWindow[key], undefined);
    assert.deepEqual(pageWindow.clearedTimeouts, [11]);
    assert.deepEqual(pageWindow.clearedIntervals, [12]);
    assert.deepEqual(pageWindow.cancelledFrames, [13]);
    assert.ok(events.includes("waiter:false"));
    assert.ok(events.includes("request:abort"));
    assert.ok(events.includes("controller:abort"));
    assert.ok(events.includes("observer:disconnect"));
    assert.ok(events.includes("listener:click"));
    assert.ok(events.includes("map:move zoom"));
    assert.ok(events.indexOf("restore:second") < events.indexOf("restore:first"));
    assert.ok(events.indexOf("cleanup:second") < events.indexOf("cleanup:first"));
    const count = events.length;
    runtime.destroy("duplicate teardown");
    assert.equal(events.length, count, "destroy must be idempotent");
}

function testRuntimeHelpers() {
    const pageWindow = createPageWindow();
    const runtime = { destroyed: false, timeouts: new Set(), listeners: [], observers: new Set(), cleanupCallbacks: [] };
    const helpers = buildRuntimeHelpers(pageWindow, runtime);
    let timerCalls = 0;
    const timerId = helpers.runtimeSetTimeout(() => { timerCalls += 1; }, 25);
    assert.ok(runtime.timeouts.has(timerId));
    pageWindow.runTimer(timerId);
    assert.equal(timerCalls, 1);
    assert.equal(runtime.timeouts.has(timerId), false);

    const blockedId = helpers.runtimeSetTimeout(() => { timerCalls += 10; }, 25);
    runtime.destroyed = true;
    pageWindow.runTimer(blockedId);
    assert.equal(timerCalls, 1, "destroyed runtime must suppress queued timeout callbacks");
    assert.equal(helpers.runtimeSetTimeout(() => {}, 1), null);

    runtime.destroyed = false;
    const eventTarget = { added: [], addEventListener(type) { this.added.push(type); } };
    helpers.runtimeListen(eventTarget, "focus", () => {}, { passive: true });
    assert.deepEqual(eventTarget.added, ["focus"]);
    assert.equal(runtime.listeners.length, 1);

    const observer = { disconnected: 0, disconnect() { this.disconnected += 1; } };
    helpers.runtimeTrackObserver(observer);
    assert.ok(runtime.observers.has(observer));
    helpers.runtimeUntrackObserver(observer);
    assert.equal(observer.disconnected, 1);
    assert.equal(runtime.observers.has(observer), false);
    runtime.destroyed = true;
    helpers.runtimeTrackObserver(observer);
    assert.equal(observer.disconnected, 2, "observer created after teardown must disconnect immediately");

    runtime.destroyed = false;
    let idleCalls = 0;
    const idleId = helpers.runtimeRunWhenIdle(deadline => { idleCalls += deadline.didTimeout ? 10 : 1; }, 80);
    assert.ok(pageWindow.idleCallbacks.has(idleId));
    pageWindow.runIdle(idleId);
    assert.equal(idleCalls, 1);
    assert.equal(runtime.cleanupCallbacks.length >= 1, true);

    const fallbackWindow = createPageWindow({ idle: false });
    const fallbackRuntime = { destroyed: false, timeouts: new Set(), listeners: [], observers: new Set(), cleanupCallbacks: [] };
    const fallback = buildRuntimeHelpers(fallbackWindow, fallbackRuntime);
    let fallbackCalls = 0;
    const fallbackId = fallback.runtimeRunWhenIdle(deadline => { fallbackCalls += deadline.didTimeout ? 1 : 10; }, 120);
    fallbackWindow.runTimer(fallbackId);
    assert.equal(fallbackCalls, 1, "idle fallback must eventually run");
}

function makeMagic(name, calls) {
    let proxy;
    const target = function (...args) { calls.push({ name, args }); return proxy; };
    proxy = new Proxy(target, {
        apply(_target, _thisArg, args) { calls.push({ name, args }); return proxy; },
        construct(_target, args) { calls.push({ name: `new ${name}`, args }); return proxy; },
        get(_target, property) {
            if (property === Symbol.toPrimitive) return () => 0;
            if (property === "then") return undefined;
            return makeMagic(`${name}.${String(property)}`, calls);
        },
        set() { return true; }
    });
    return proxy;
}

function makeEventTarget(name) {
    const listeners = new Map();
    const removed = [];
    return {
        name, listeners, removed,
        addEventListener(type, listener, options) {
            if (!listeners.has(type)) listeners.set(type, []);
            listeners.get(type).push({ listener, options });
        },
        removeEventListener(type, listener, options) { removed.push({ type, listener, options }); }
    };
}

function compileInSandbox(source, sandbox) {
    return Function("sandbox", `with (sandbox) { return (${source}); }`)(sandbox);
}

function createBootEnvironment({ mapReadyAfter = 0, ensureReady = true, buildingVisibility = true } = {}) {
    const calls = [];
    const target = {
        undefined,
        Boolean, Date, Math, Number, Promise, Map, Set, String, Array, Object,
        console: { debug() {} },
        runtime: { destroyed: false, cleanupCallbacks: [] },
        bootStarted: false,
        bootStartedAt: 0,
        operationalStartupComplete: true,
        state: {
            autoLoadAllVehicles: false,
            economyMode: false,
            visibility: { buildings: buildingVisibility },
            majorIncidentFeed: { enabled: false },
            autoNight: { enabled: false },
            stuckDetector: { enabled: false },
            resourceGap: { enabled: false },
            allianceCredits: false,
            unitCommitment: false,
            missionAge: false
        },
        SCRIPT: {
            name: "MissionChief Map Command Toolkit", version: "fixture",
            panelId: "panel", controlId: "control", payoutFlashId: "payout",
            criticalDrawerId: "critical"
        },
        STARTUP_SETTLE_WINDOW_MS: 10000,
        STARTUP_MUTATION_DEBOUNCE_MS: 500,
        DOM_REFRESH_DEBOUNCE_MS: 200,
        STARTUP_OBSERVER_DELAY_MS: 300,
        STARTUP_IDLE_TIMEOUT_MS: fixtures.startupIdleTimeoutMs,
        VEHICLE_API_REFRESH_MS: 120000,
        FALLBACK_MISSION_REFRESH_MS: 30000,
        BUILDING_VISIBILITY_RECHECK_MS: 10000,
        CRITICAL_PROGRESS_REFRESH_ACTIVE_MS: 1000,
        CRITICAL_PROGRESS_REFRESH_IDLE_MS: 10000,
        economyMapMoving: false,
        economyDeferredDomMutation: false,
        economyDeferredMapRefresh: false,
        dragState: null,
        mutationTimer: null,
        settingsPanelActivated: false,
        mainMutationObserverFallbackActive: false,
        suppressNextOutsideClick: false,
        transportSweepRuntime: { stopRequested: false },
        coverageGroup: null,
        payoutAudioContext: null,
        creditsValueObserver: null,
        desktopPanelResizeObserver: null,
        majorIncidentFeedResizeObserver: null,
        majorIncidentFeedObservedElement: null,
        majorIncidentFeedLayoutTimer: null,
        cachedMap: null,
        helpGuideDocumentCache: "cached",
        helpGuideLoadedAt: 123,
        missionSnapshotCache: new Map([["x", 1]]),
        missionPanelCache: new Map([["x", 1]]),
        missionOverlayVersions: new Map([["x", 1]]),
        markerRegistryCache: new Map([["x", 1]]),
        criticalMissionStableCache: new Map([["x", 1]]),
    };
    const documentTarget = makeEventTarget("document");
    const removedAttributes = [];
    Object.assign(documentTarget, {
        hidden: false,
        readyState: "complete",
        documentElement: { style: {}, removeAttribute(name) { removedAttributes.push(name); } },
        body: { style: {} },
        getElementById() { return null; },
        querySelector() { return null; }
    });
    const windowTarget = makeEventTarget("window");
    windowTarget.visualViewport = null;
    windowTarget.matchMedia = () => null;
    target.document = documentTarget;
    target.pageWindow = windowTarget;
    target.removedAttributes = removedAttributes;

    let nextTimerId = 1;
    const timers = new Map();
    const bootTimerDelays = [];
    target.runtimeSetTimeout = (callback, delay = 0, ...args) => {
        if (target.runtime.destroyed) return null;
        const id = nextTimerId++;
        const name = callback.name || "anonymous";
        if (name === "runBootAttempt") bootTimerDelays.push(delay);
        timers.set(id, {
            id, name, delay,
            run() {
                timers.delete(id);
                if (!target.runtime.destroyed) callback(...args);
            }
        });
        return id;
    };
    target.runtimeClearTimeout = id => timers.delete(id);
    target.timers = timers;
    target.bootTimerDelays = bootTimerDelays;
    target.runNamedTimer = name => {
        const timer = Array.from(timers.values()).find(entry => entry.name === name);
        assert.ok(timer, `Missing ${name} timer`);
        timer.run();
    };

    const listenerRecords = [];
    target.runtimeListen = (eventTarget, type, listener, options) => {
        if (target.runtime.destroyed) return listener;
        eventTarget.addEventListener(type, listener, options);
        listenerRecords.push({ target: eventTarget, type, listener, options });
        return listener;
    };
    target.listenerRecords = listenerRecords;
    target.runtimeTrackObserver = observer => { target.trackedObserver = observer; return observer; };
    target.runtimeUntrackObserver = observer => { calls.push({ name: "runtimeUntrackObserver", args: [observer] }); };
    target.runtimeOnCleanup = callback => { target.runtime.cleanupCallbacks.push(callback); return callback; };
    target.runtimeRegisterTask = (name, interval, callback, options) => {
        target.tasks.push({ name, interval, callback, options });
        return name;
    };
    target.tasks = [];
    target.runtimeRunWhenIdle = (callback, timeout) => { calls.push({ name: "runtimeRunWhenIdle", args: [callback, timeout] }); return 1; };
    target.runtimeWakeTaskScheduler = delay => calls.push({ name: "runtimeWakeTaskScheduler", args: [delay] });
    target.runtimeRunScheduledTasks = () => {};
    target.startupClock = () => 100;
    target.applyRootAttributes = () => calls.push({ name: "applyRootAttributes", args: [] });
    target.installAllianceBuildingsPageOptimisation = () => false;
    target.createCleanExit = () => calls.push({ name: "createCleanExit", args: [] });
    target.installMissionMarkerAddHook = () => calls.push({ name: "installMissionMarkerAddHook", args: [] });
    target.installRadioMessageHook = () => calls.push({ name: "installRadioMessageHook", args: [] });
    target.readCurrentCreditTotal = () => 1000;
    target.installCreditsUpdateHook = () => calls.push({ name: "installCreditsUpdateHook", args: [] });
    target.observeCreditValue = () => calls.push({ name: "observeCreditValue", args: [] });
    let ensureCalls = 0;
    let mapCalls = 0;
    target.ensureUi = () => { ensureCalls += 1; return ensureReady; };
    target.getLargestLeafletMap = () => { mapCalls += 1; return mapCalls > mapReadyAfter ? { id: "map" } : null; };
    target.getEnsureCalls = () => ensureCalls;
    target.getMapCalls = () => mapCalls;
    target.recordStartupMetric = (name, startedAt, extra) => calls.push({ name: "recordStartupMetric", args: [name, startedAt, extra] });
    target.scheduleMarkerStateSync = (...args) => calls.push({ name: "scheduleMarkerStateSync", args });
    target.scheduleDeferredOperationalStartup = (...args) => calls.push({ name: "scheduleDeferredOperationalStartup", args });
    target.connectMainMutationObserver = () => calls.push({ name: "connectMainMutationObserver", args: [] });
    target.MutationObserver = class {
        constructor(callback) { this.callback = callback; this.disconnected = false; }
        disconnect() { this.disconnected = true; }
    };
    for (const name of fixtures.requiredCleanupCalls) {
        target[name] = (...args) => { calls.push({ name, args }); return undefined; };
    }
    target.synchronisePersonalBuildingVisibility = (...args) => calls.push({ name: "synchronisePersonalBuildingVisibility", args });
    target.calls = calls;

    const sandbox = new Proxy(target, {
        has() { return true; },
        get(object, property) {
            if (property === Symbol.unscopables) return undefined;
            if (Reflect.has(object, property)) return Reflect.get(object, property);
            const magic = makeMagic(String(property), calls);
            Reflect.set(object, property, magic);
            return magic;
        },
        set(object, property, value) { Reflect.set(object, property, value); return true; }
    });
    target.boot = compileInSandbox(__BOOT_SOURCE__, sandbox);
    return target;
}

function callCount(env, name) { return env.calls.filter(call => call.name === name).length; }

function testBootLifecycle() {
    const initial = createBootEnvironment();
    initial.boot();
    initial.boot();
    assert.equal(callCount(initial, "applyRootAttributes"), 1, "boot must be idempotent");
    assert.equal(initial.runtime.cleanupCallbacks.length, 1);
    assert.deepEqual(new Set(initial.tasks.map(task => task.name)), new Set(fixtures.requiredTasks));
    const documentListeners = new Set(initial.listenerRecords.filter(item => item.target === initial.document).map(item => item.type));
    const windowListeners = new Set(initial.listenerRecords.filter(item => item.target === initial.pageWindow).map(item => item.type));
    for (const name of fixtures.requiredDocumentListeners) assert.ok(documentListeners.has(name), `Missing document listener ${name}`);
    for (const name of fixtures.requiredWindowListeners) assert.ok(windowListeners.has(name), `Missing window listener ${name}`);

    const delayed = createBootEnvironment({ mapReadyAfter: 3 });
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

    const destroyed = createBootEnvironment({ mapReadyAfter: Number.POSITIVE_INFINITY, ensureReady: false });
    destroyed.boot();
    destroyed.runNamedTimer("runBootAttempt");
    const ensureBeforeDestroy = destroyed.getEnsureCalls();
    destroyed.runtime.destroyed = true;
    destroyed.runNamedTimer("runBootAttempt");
    assert.equal(destroyed.getEnsureCalls(), ensureBeforeDestroy, "destroyed runtime must suppress retry callbacks");
    assert.equal(Array.from(destroyed.timers.values()).some(timer => timer.name === "runBootAttempt"), false);

    const visibility = createBootEnvironment();
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

    const cleanup = createBootEnvironment({ buildingVisibility: false });
    cleanup.boot();
    cleanup.runtime.cleanupCallbacks[0]("fixture teardown");
    assert.equal(cleanup.transportSweepRuntime.stopRequested, true);
    assert.equal(cleanup.state.visibility.buildings, false, "teardown must restore the stored building preference");
    for (const name of fixtures.cleanupCaches) assert.equal(cleanup[name].size, 0, `${name} must clear`);
    assert.deepEqual(new Set(cleanup.removedAttributes), new Set(fixtures.cleanupRootAttributes));
    for (const name of fixtures.requiredCleanupCalls) assert.ok(callCount(cleanup, name) >= 1, `Missing cleanup call ${name}`);
    assert.equal(cleanup.document.removed.length, 5, "manual drag listeners must be removed");
    assert.equal(cleanup.helpGuideDocumentCache, "");
    assert.equal(cleanup.helpGuideLoadedAt, 0);
}

function testScheduleAndDocumentStart() {
    const calls = [];
    const target = {
        runtime: { destroyed: false },
        bootStarted: false,
        STARTUP_IDLE_TIMEOUT_MS: fixtures.startupIdleTimeoutMs,
        boot() {},
        runtimeRunWhenIdle(callback, timeout) { calls.push({ callback, timeout }); }
    };
    const sandbox = new Proxy(target, {
        has() { return true; },
        get(object, property) { if (property === Symbol.unscopables) return undefined; return object[property]; },
        set(object, property, value) { object[property] = value; return true; }
    });
    const scheduleBoot = compileInSandbox(__SCHEDULE_BOOT_SOURCE__, sandbox);
    scheduleBoot();
    assert.equal(calls.length, 1);
    assert.equal(calls[0].callback, target.boot);
    assert.equal(calls[0].timeout, fixtures.startupIdleTimeoutMs);
    target.bootStarted = true;
    scheduleBoot();
    target.bootStarted = false;
    target.runtime.destroyed = true;
    scheduleBoot();
    assert.equal(calls.length, 1, "destroyed or already-started runtime must not reschedule boot");

    const runBootstrap = Function("document", "runtimeListen", "scheduleBoot", __BOOTSTRAP_SOURCE_STRING__);
    let scheduled = 0;
    const loadingDocument = { readyState: "loading" };
    const registrations = [];
    runBootstrap(loadingDocument, (target, type, listener, options) => registrations.push({ target, type, listener, options }), () => { scheduled += 1; });
    assert.equal(scheduled, 0);
    assert.equal(registrations.length, 1);
    assert.equal(registrations[0].type, "DOMContentLoaded");
    assert.deepEqual(registrations[0].options, { once: true });
    registrations[0].listener();
    assert.equal(scheduled, 1);

    scheduled = 0;
    runBootstrap({ readyState: "complete" }, () => { throw new Error("complete document must not register DOMContentLoaded"); }, () => { scheduled += 1; });
    assert.equal(scheduled, 1);
}

testRuntimeOwnershipAndTeardown();
testRuntimeHelpers();
testBootLifecycle();
testScheduleAndDocumentStart();
console.log("Boot lifecycle contract passed: runtime ownership, document-start, delayed map, hidden-tab resume, retry cancellation and teardown.");
'''
    replacements["__BOOT_SOURCE__"] = json.dumps(functions["boot"])
    replacements["__SCHEDULE_BOOT_SOURCE__"] = json.dumps(functions["scheduleBoot"])
    replacements["__BOOTSTRAP_SOURCE_STRING__"] = json.dumps(bootstrap_tail)
    for marker, value in replacements.items():
        harness = harness.replace(marker, value)

    with tempfile.TemporaryDirectory(prefix="mcms-boot-lifecycle-") as temp:
        harness_path = Path(temp) / "boot-lifecycle-contract.js"
        harness_path.write_text(harness, encoding="utf-8")
        subprocess.run(["node", "--check", str(harness_path)], cwd=ROOT, check=True)
        subprocess.run(["node", str(harness_path)], cwd=ROOT, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
