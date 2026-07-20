#!/usr/bin/env node
'use strict';
const assert = require('node:assert/strict');
const path = require('node:path');
const core = require(path.resolve(__dirname, '..', '..', 'tools', 'mcms-performance-profiler.user.js'));

assert.equal(core.SCHEMA_VERSION, 1);

{
    const list = [];
    for (let index = 0; index < 5; index += 1) core.boundedPush(list, index, 3);
    assert.deepEqual(list, [2, 3, 4], 'bounded retention keeps the newest entries');
}

{
    const runtime = {
        version: '4.20.10', destroyed: false,
        timeouts: new Set([1, 2]), intervals: new Set([3]), animationFrames: new Set(),
        observers: new Set([{}]), listeners: [{}, {}], waiters: new Set(), requests: new Set([{}]),
        fetchControllers: new Set(), mapBindings: [], cleanupCallbacks: [() => {}],
    };
    assert.deepEqual(core.runtimeSnapshot(runtime, 15), {
        at: 15, present: true, version: '4.20.10', destroyed: false,
        timeouts: 2, intervals: 1, animationFrames: 0, observers: 1, listeners: 2,
        waiters: 0, requests: 1, fetchControllers: 0, mapBindings: 0, cleanupCallbacks: 1,
    });
    assert.deepEqual(core.runtimeSnapshot(null, 20), { at: 20, present: false });
}

{
    const startup = core.cloneStartupMetrics({
        coreUiReadyMs: 12.3,
        token: { secret: true },
        'bad key': 2,
        phase: 'ready',
    });
    assert.deepEqual(startup, { coreUiReadyMs: 12.3, phase: 'ready' });
}

{
    let clock = 1000;
    let intervalId = 0;
    const cleared = [];
    const visibilityListeners = new Set();
    const disconnected = [];
    const performanceCallbacks = new Map();
    let mutationCallback = null;
    const runtime = { version: '4.20.10', timeouts: new Set([1]), listeners: [] };
    const session = core.createSession({
        now: () => clock,
        monotonicNow: () => clock - 900,
        setInterval: () => { intervalId += 1; return intervalId; },
        clearInterval: id => cleared.push(id),
        getRuntime: () => runtime,
        getStartupMetrics: () => ({ coreUiReadyMs: 40 }),
        getVisibility: () => 'visible',
        addVisibilityListener: listener => visibilityListeners.add(listener),
        removeVisibilityListener: listener => visibilityListeners.delete(listener),
        createPerformanceObserver: (type, callback) => {
            performanceCallbacks.set(type, callback);
            return { disconnect: () => disconnected.push(type) };
        },
        createMutationObserver: callback => {
            mutationCallback = callback;
            return { disconnect: () => disconnected.push('mutation') };
        },
        baseUrl: 'https://www.missionchief.co.uk/missions/123',
    }, { limits: { longTasks: 2, mutations: 2, resourceGroups: 2 }, sampleIntervalMs: 250 });

    assert.equal(session.start(), true);
    assert.equal(session.start(), false, 'duplicate start is ignored');
    assert.equal(visibilityListeners.size, 1);
    performanceCallbacks.get('longtask')([
        { startTime: 1, duration: 55 }, { startTime: 2, duration: 60 }, { startTime: 3, duration: 65 },
    ]);
    performanceCallbacks.get('resource')([
        { name: 'https://cdn.example/a', initiatorType: 'script', duration: 10, transferSize: 100 },
        { name: 'https://cdn.example/b', initiatorType: 'script', duration: 20, transferSize: 200 },
        { name: 'https://api.example/c', initiatorType: 'fetch', duration: 30, transferSize: 300 },
        { name: 'https://third.example/d', initiatorType: 'img', duration: 40, transferSize: 400 },
    ]);
    mutationCallback([{ type: 'childList', addedNodes: [1, 2], removedNodes: [1] }]);
    mutationCallback([{ type: 'attributes' }]);
    mutationCallback([{ type: 'characterData' }]);
    clock = 1500;
    session.sampleRuntime();
    const report = session.report({ host: 'www.missionchief.co.uk', pathClass: 'mission', browser: { mobile: false } });
    assert.equal(report.schemaVersion, 1);
    assert.equal(report.longTasks.length, 2, 'long task retention is bounded');
    assert.equal(report.longTasks[0].startTime, 2);
    assert.equal(report.mutations.length, 2, 'mutation retention is bounded');
    assert.equal(report.resources.length, 2, 'resource groups are bounded');
    assert.equal(report.droppedResourceGroups, 1);
    assert.equal(report.startupMetrics.coreUiReadyMs, 40);
    assert.equal(report.runtimeSamples.at(-1).timeouts, 1);
    assert.equal(JSON.stringify(report).includes('/missions/123'), false, 'report contains no full page URL');
    assert.equal(session.stop(), true);
    assert.equal(session.stop(), false, 'duplicate stop is ignored');
    assert.deepEqual(cleared, [1]);
    assert.equal(visibilityListeners.size, 0);
    assert.deepEqual(new Set(disconnected), new Set(['longtask', 'layout-shift', 'resource', 'mutation']));
    session.reset();
    assert.equal(session.state.longTasks.length, 0);
    assert.equal(session.state.resources.size, 0);
}

console.log('Performance profiler contracts passed.');
