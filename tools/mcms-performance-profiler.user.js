// ==UserScript==
// @name         MissionChief Toolkit Performance Profiler (Development Only)
// @namespace    https://github.com/Conroy1988/missionchief-toolkit-assets
// @version      0.2.0
// @description  Opt-in, privacy-bounded browser profiler for MissionChief Toolkit development.
// @author       Conroy1988
// @license      MIT
// @match        *://*.missionchief.co.uk/*
// @match        *://missionchief.co.uk/*
// @match        *://*.missionchief.com/*
// @match        *://missionchief.com/*
// @match        *://*.leitstellenspiel.de/*
// @match        *://leitstellenspiel.de/*
// @match        *://*.meldkamerspel.com/*
// @match        *://meldkamerspel.com/*
// @grant        none
// @run-at       document-start
// ==/UserScript==

(function exposeProfilerCore(root, factory) {
    'use strict';
    const core = factory();
    if (typeof module === 'object' && module.exports) module.exports = core;
    if (root && typeof root === 'object') root.__MCMS_PROFILER_CORE__ = core;
})(typeof globalThis !== 'undefined' ? globalThis : this, function createProfilerCore() {
    'use strict';

    const SCHEMA_VERSION = 2;
    const MUTATION_OBSERVER_OPTIONS = Object.freeze({ childList: true, subtree: true, attributes: true, characterData: true });
    const DEFAULT_LIMITS = Object.freeze({
        longTasks: 200,
        layoutShifts: 200,
        mutations: 500,
        runtimeSamples: 600,
        visibility: 100,
        resourceGroups: 100,
        renderEvents: 2000,
        scenarioTransitions: 100,
    });

    function finiteNumber(value, fallback = 0) {
        const number = Number(value);
        return Number.isFinite(number) ? number : fallback;
    }

    function boundedPush(list, value, limit) {
        const maximum = Math.max(1, Math.floor(finiteNumber(limit, 1)));
        list.push(value);
        if (list.length > maximum) list.splice(0, list.length - maximum);
        return list;
    }

    function collectionSize(value) {
        if (!value) return 0;
        if (Number.isFinite(Number(value.size))) return Math.max(0, Number(value.size));
        if (Number.isFinite(Number(value.length))) return Math.max(0, Number(value.length));
        return 0;
    }

    function runtimeSnapshot(runtime, at) {
        if (!runtime || typeof runtime !== 'object') return { at, present: false };
        return {
            at,
            present: true,
            version: typeof runtime.version === 'string' ? runtime.version : null,
            destroyed: runtime.destroyed === true,
            timeouts: collectionSize(runtime.timeouts),
            intervals: collectionSize(runtime.intervals),
            animationFrames: collectionSize(runtime.animationFrames),
            observers: collectionSize(runtime.observers),
            listeners: collectionSize(runtime.listeners),
            waiters: collectionSize(runtime.waiters),
            requests: collectionSize(runtime.requests),
            fetchControllers: collectionSize(runtime.fetchControllers),
            mapBindings: collectionSize(runtime.mapBindings),
            cleanupCallbacks: collectionSize(runtime.cleanupCallbacks),
        };
    }

    function safeHost(value, baseUrl) {
        try {
            const url = new URL(String(value || ''), String(baseUrl || 'https://invalid.local/'));
            return url.hostname || 'unknown';
        } catch (error) {
            return 'invalid';
        }
    }

    function browserMetadata(navigatorObject, windowObject) {
        const navigatorValue = navigatorObject || {};
        const windowValue = windowObject || {};
        return {
            userAgent: String(navigatorValue.userAgent || '').slice(0, 500),
            platform: String(navigatorValue.userAgentData?.platform || navigatorValue.platform || '').slice(0, 100),
            mobile: navigatorValue.userAgentData?.mobile === true,
            language: String(navigatorValue.language || '').slice(0, 30),
            hardwareConcurrency: finiteNumber(navigatorValue.hardwareConcurrency, 0),
            deviceMemory: finiteNumber(navigatorValue.deviceMemory, 0),
            viewport: {
                width: Math.max(0, finiteNumber(windowValue.innerWidth, 0)),
                height: Math.max(0, finiteNumber(windowValue.innerHeight, 0)),
                devicePixelRatio: Math.max(0, finiteNumber(windowValue.devicePixelRatio, 0)),
            },
        };
    }

    function cloneStartupMetrics(value) {
        if (!value || typeof value !== 'object') return {};
        const result = {};
        for (const [key, raw] of Object.entries(value)) {
            if (!/^[A-Za-z0-9_-]{1,80}$/.test(key)) continue;
            if (typeof raw === 'boolean' || typeof raw === 'string') result[key] = String(raw).slice(0, 100);
            else if (Number.isFinite(Number(raw))) result[key] = Number(raw);
        }
        return result;
    }

    const RENDER_PATHS = Object.freeze(['updateUI', 'renderOperationalPanels']);
    const SCENARIOS = Object.freeze([
        'unclassified',
        'idle-map',
        'settings-open-close',
        'mission-open-close',
        'unit-selection',
        'map-pan-zoom',
        'layout-change',
    ]);

    function safeRenderPath(value) {
        const name = String(value || '');
        return RENDER_PATHS.includes(name) ? name : null;
    }

    function safeScenario(value) {
        const name = String(value || '');
        return SCENARIOS.includes(name) ? name : 'unclassified';
    }

    function createSession(adapters = {}, options = {}) {
        const limits = { ...DEFAULT_LIMITS, ...(options.limits || {}) };
        const now = typeof adapters.now === 'function' ? adapters.now : () => Date.now();
        const monotonicNow = typeof adapters.monotonicNow === 'function' ? adapters.monotonicNow : now;
        const setIntervalFn = adapters.setInterval || ((callback, delay) => setInterval(callback, delay));
        const clearIntervalFn = adapters.clearInterval || (id => clearInterval(id));
        const getRuntime = typeof adapters.getRuntime === 'function' ? adapters.getRuntime : () => null;
        const getStartupMetrics = typeof adapters.getStartupMetrics === 'function' ? adapters.getStartupMetrics : () => ({});
        const getVisibility = typeof adapters.getVisibility === 'function' ? adapters.getVisibility : () => 'unknown';
        const addVisibilityListener = adapters.addVisibilityListener || (() => {});
        const removeVisibilityListener = adapters.removeVisibilityListener || (() => {});
        const createPerformanceObserver = adapters.createPerformanceObserver || (() => null);
        const createMutationObserver = adapters.createMutationObserver || (() => null);
        const scheduleRenderFinalizer = adapters.scheduleRenderFinalizer || (callback => setTimeout(callback, 0));
        const clearRenderFinalizer = adapters.clearRenderFinalizer || (id => clearTimeout(id));
        const sampleIntervalMs = Math.max(250, finiteNumber(options.sampleIntervalMs, 1000));
        const state = {
            active: false,
            startedAt: null,
            stoppedAt: null,
            startedMonotonic: null,
            longTasks: [],
            layoutShifts: [],
            mutations: [],
            runtimeSamples: [],
            visibility: [],
            resources: new Map(),
            droppedResourceGroups: 0,
            renderEvents: [],
            renderAggregates: new Map(),
            scenarioTransitions: [],
            currentScenario: 'unclassified',
            renderSequence: 0,
            totalMutationRecords: 0,
            pendingRenders: new Map(),
        };
        const handles = { performance: [], mutation: null, interval: null, visibility: null, renderFinalizers: new Map() };

        function recordResource(entry) {
            const host = safeHost(entry?.name, adapters.baseUrl);
            const initiator = String(entry?.initiatorType || 'unknown').slice(0, 50);
            const key = `${host}|${initiator}`;
            let group = state.resources.get(key);
            if (!group) {
                if (state.resources.size >= limits.resourceGroups) {
                    state.droppedResourceGroups += 1;
                    return;
                }
                group = { host, initiatorType: initiator, count: 0, durationMs: 0, transferBytes: 0 };
                state.resources.set(key, group);
            }
            group.count += 1;
            group.durationMs = Math.round((group.durationMs + Math.max(0, finiteNumber(entry?.duration, 0))) * 10) / 10;
            group.transferBytes += Math.max(0, finiteNumber(entry?.transferSize, 0));
        }

        function processPerformanceEntries(type, entries) {
            for (const entry of Array.from(entries || [])) {
                if (type === 'longtask') {
                    boundedPush(state.longTasks, {
                        startTime: finiteNumber(entry?.startTime, 0),
                        durationMs: finiteNumber(entry?.duration, 0),
                    }, limits.longTasks);
                } else if (type === 'layout-shift') {
                    boundedPush(state.layoutShifts, {
                        startTime: finiteNumber(entry?.startTime, 0),
                        value: finiteNumber(entry?.value, 0),
                        hadRecentInput: entry?.hadRecentInput === true,
                    }, limits.layoutShifts);
                } else if (type === 'resource') {
                    recordResource(entry);
                }
            }
        }

        function recordMutations(records) {
            const summary = {
                at: monotonicNow(),
                records: 0,
                childList: 0,
                attributes: 0,
                characterData: 0,
                addedNodes: 0,
                removedNodes: 0,
            };
            for (const record of Array.from(records || [])) {
                summary.records += 1;
                if (record?.type === 'childList') {
                    summary.childList += 1;
                    summary.addedNodes += collectionSize(record.addedNodes);
                    summary.removedNodes += collectionSize(record.removedNodes);
                } else if (record?.type === 'attributes') summary.attributes += 1;
                else if (record?.type === 'characterData') summary.characterData += 1;
            }
            if (summary.records) {
                state.totalMutationRecords += summary.records;
                boundedPush(state.mutations, summary, limits.mutations);
            }
        }

        function sampleRuntime() {
            boundedPush(state.runtimeSamples, runtimeSnapshot(getRuntime(), monotonicNow()), limits.runtimeSamples);
        }

        function setScenario(value) {
            const scenario = safeScenario(value);
            if (state.currentScenario === scenario) return scenario;
            state.currentScenario = scenario;
            boundedPush(state.scenarioTransitions, { at: monotonicNow(), scenario }, limits.scenarioTransitions);
            return scenario;
        }

        function aggregateRender(event) {
            const key = `${event.scenario}|${event.path}`;
            let aggregate = state.renderAggregates.get(key);
            if (!aggregate) {
                aggregate = {
                    scenario: event.scenario,
                    path: event.path,
                    attempts: 0,
                    changedAttempts: 0,
                    unchangedAttempts: 0,
                    totalDurationMs: 0,
                    maxDurationMs: 0,
                    mutationRecords: 0,
                };
                state.renderAggregates.set(key, aggregate);
            }
            aggregate.attempts += 1;
            aggregate.changedAttempts += event.changed ? 1 : 0;
            aggregate.unchangedAttempts += event.changed ? 0 : 1;
            aggregate.totalDurationMs = Math.round((aggregate.totalDurationMs + event.durationMs) * 1000) / 1000;
            aggregate.maxDurationMs = Math.max(aggregate.maxDurationMs, event.durationMs);
            aggregate.mutationRecords += event.mutationRecords;
        }

        function finalizeRender(token) {
            if (!token || !state.pendingRenders.has(token.id)) return false;
            state.pendingRenders.delete(token.id);
            const finalizer = handles.renderFinalizers.get(token.id);
            if (finalizer !== undefined) handles.renderFinalizers.delete(token.id);
            const mutationRecords = Math.max(0, state.totalMutationRecords - token.mutationRecordsBefore);
            const durationMs = Math.max(0, finiteNumber(token.endedAt ?? monotonicNow(), 0) - finiteNumber(token.startedAt, 0));
            const event = {
                id: token.id,
                path: token.path,
                scenario: token.scenario,
                startedAt: token.startedAt,
                durationMs: Math.round(durationMs * 1000) / 1000,
                mutationRecords,
                changed: mutationRecords > 0,
                depth: token.depth,
            };
            boundedPush(state.renderEvents, event, limits.renderEvents);
            aggregateRender(event);
            return true;
        }

        function beginRender(value) {
            const path = safeRenderPath(value);
            if (!state.active || !path) return null;
            const token = {
                id: ++state.renderSequence,
                path,
                scenario: state.currentScenario,
                startedAt: monotonicNow(),
                endedAt: null,
                mutationRecordsBefore: state.totalMutationRecords,
                depth: state.pendingRenders.size,
            };
            state.pendingRenders.set(token.id, token);
            return token;
        }

        function endRender(token) {
            if (!token || !state.pendingRenders.has(token.id)) return false;
            token.endedAt = monotonicNow();
            const id = scheduleRenderFinalizer(() => finalizeRender(token));
            handles.renderFinalizers.set(token.id, id);
            return true;
        }

        function flushPendingRenders() {
            for (const token of Array.from(state.pendingRenders.values())) {
                const id = handles.renderFinalizers.get(token.id);
                if (id !== undefined) {
                    try { clearRenderFinalizer(id); } catch (error) {}
                    handles.renderFinalizers.delete(token.id);
                }
                if (token.endedAt === null) token.endedAt = monotonicNow();
                finalizeRender(token);
            }
        }

        function recordVisibility() {
            boundedPush(state.visibility, { at: monotonicNow(), state: String(getVisibility() || 'unknown').slice(0, 30) }, limits.visibility);
        }

        function start() {
            if (state.active) return false;
            state.active = true;
            state.startedAt = now();
            state.stoppedAt = null;
            state.startedMonotonic = monotonicNow();
            for (const type of ['longtask', 'layout-shift', 'resource']) {
                try {
                    const observer = createPerformanceObserver(type, entries => processPerformanceEntries(type, entries));
                    if (observer) handles.performance.push(observer);
                } catch (error) {}
            }
            try { handles.mutation = createMutationObserver(recordMutations) || null; } catch (error) { handles.mutation = null; }
            handles.visibility = recordVisibility;
            addVisibilityListener(recordVisibility);
            recordVisibility();
            sampleRuntime();
            handles.interval = setIntervalFn(sampleRuntime, sampleIntervalMs);
            return true;
        }

        function stop() {
            if (!state.active) return false;
            flushPendingRenders();
            state.active = false;
            state.stoppedAt = now();
            for (const observer of handles.performance.splice(0)) {
                try { observer.disconnect?.(); } catch (error) {}
            }
            if (handles.mutation) {
                try { handles.mutation.disconnect?.(); } catch (error) {}
                handles.mutation = null;
            }
            if (handles.interval !== null) {
                try { clearIntervalFn(handles.interval); } catch (error) {}
                handles.interval = null;
            }
            if (handles.visibility) {
                try { removeVisibilityListener(handles.visibility); } catch (error) {}
                handles.visibility = null;
            }
            return true;
        }

        function reset() {
            stop();
            state.startedAt = null;
            state.stoppedAt = null;
            state.startedMonotonic = null;
            state.longTasks.length = 0;
            state.layoutShifts.length = 0;
            state.mutations.length = 0;
            state.runtimeSamples.length = 0;
            state.visibility.length = 0;
            state.resources.clear();
            state.droppedResourceGroups = 0;
            state.renderEvents.length = 0;
            state.renderAggregates.clear();
            state.scenarioTransitions.length = 0;
            state.currentScenario = 'unclassified';
            state.renderSequence = 0;
            state.totalMutationRecords = 0;
            state.pendingRenders.clear();
        }

        function report(metadata = {}) {
            const finishedAt = state.active ? now() : state.stoppedAt;
            return {
                schemaVersion: SCHEMA_VERSION,
                profilerVersion: '0.2.0',
                active: state.active,
                startedAt: state.startedAt,
                finishedAt,
                durationMs: state.startedAt === null || finishedAt === null ? 0 : Math.max(0, finiteNumber(finishedAt, 0) - finiteNumber(state.startedAt, 0)),
                page: {
                    host: String(metadata.host || '').slice(0, 200),
                    pathClass: String(metadata.pathClass || '').slice(0, 100),
                },
                browser: metadata.browser || {},
                startupMetrics: cloneStartupMetrics(getStartupMetrics()),
                longTasks: state.longTasks.slice(),
                layoutShifts: state.layoutShifts.slice(),
                mutations: state.mutations.slice(),
                runtimeSamples: state.runtimeSamples.slice(),
                visibility: state.visibility.slice(),
                resources: Array.from(state.resources.values()).sort((a, b) => b.durationMs - a.durationMs),
                droppedResourceGroups: state.droppedResourceGroups,
                currentScenario: state.currentScenario,
                scenarioTransitions: state.scenarioTransitions.slice(),
                renderEvents: state.renderEvents.slice(),
                renderMeasurements: Array.from(state.renderAggregates.values()).map(value => ({
                    ...value,
                    unchangedRatio: value.attempts ? Math.round((value.unchangedAttempts / value.attempts) * 10000) / 10000 : 0,
                    averageDurationMs: value.attempts ? Math.round((value.totalDurationMs / value.attempts) * 1000) / 1000 : 0,
                })).sort((a, b) => b.attempts - a.attempts || a.scenario.localeCompare(b.scenario) || a.path.localeCompare(b.path)),
                limits: { ...limits },
            };
        }

        return { state, start, stop, reset, report, processPerformanceEntries, recordMutations, sampleRuntime, setScenario, beginRender, endRender, finalizeRender, flushPendingRenders };
    }

    return {
        SCHEMA_VERSION,
        MUTATION_OBSERVER_OPTIONS,
        DEFAULT_LIMITS,
        finiteNumber,
        boundedPush,
        collectionSize,
        runtimeSnapshot,
        safeHost,
        browserMetadata,
        cloneStartupMetrics,
        RENDER_PATHS,
        SCENARIOS,
        safeRenderPath,
        safeScenario,
        createSession,
    };
});

(function installProfiler() {
    'use strict';
    if (typeof window === 'undefined' || typeof document === 'undefined') return;
    const core = window.__MCMS_PROFILER_CORE__;
    if (!core || window.__MCMS_PROFILER__) return;
    const RUNTIME_KEY = '__MC_MAP_COMMAND_TOOLKIT_RUNTIME__';
    const observers = [];

    function createPerformanceObserver(type, callback) {
        if (typeof window.PerformanceObserver !== 'function') return null;
        const supported = window.PerformanceObserver.supportedEntryTypes || [];
        if (!supported.includes(type)) return null;
        const observer = new window.PerformanceObserver(list => callback(list.getEntries()));
        observer.observe({ type, buffered: true });
        return observer;
    }

    function createMutationObserver(callback) {
        if (typeof window.MutationObserver !== 'function') return null;
        const observer = new window.MutationObserver(records => {
            const filtered = Array.from(records || []).filter(record => {
                const target = record?.target?.nodeType === 1 ? record.target : record?.target?.parentElement;
                return !target?.closest?.('#mcms-development-profiler');
            });
            if (filtered.length) callback(filtered);
        });
        const root = document.documentElement || document;
        observer.observe(root, core.MUTATION_OBSERVER_OPTIONS);
        return observer;
    }

    const session = core.createSession({
        now: () => Date.now(),
        monotonicNow: () => Number(window.performance?.now?.()) || Date.now(),
        setInterval: (callback, delay) => window.setInterval(callback, delay),
        clearInterval: id => window.clearInterval(id),
        getRuntime: () => window[RUNTIME_KEY] || null,
        getStartupMetrics: () => window.__MCMS_STARTUP_METRICS__ || {},
        getVisibility: () => document.visibilityState || 'unknown',
        addVisibilityListener: listener => document.addEventListener('visibilitychange', listener, { passive: true }),
        removeVisibilityListener: listener => document.removeEventListener('visibilitychange', listener, { passive: true }),
        createPerformanceObserver,
        createMutationObserver,
        scheduleRenderFinalizer: callback => window.setTimeout(callback, 0),
        clearRenderFinalizer: id => window.clearTimeout(id),
        baseUrl: window.location?.href || '',
    });

    function pathClass() {
        const path = String(window.location?.pathname || '');
        if (/\/missions?\//i.test(path)) return 'mission';
        if (/\/buildings?\//i.test(path)) return 'building';
        if (/\/vehicles?\//i.test(path)) return 'vehicle';
        if (/\/verband|\/alliance/i.test(path)) return 'alliance';
        return 'other';
    }

    function buildReport() {
        return session.report({
            host: String(window.location?.hostname || ''),
            pathClass: pathClass(),
            browser: core.browserMetadata(window.navigator, window),
        });
    }

    function downloadReport() {
        const report = JSON.stringify(buildReport(), null, 2);
        const blob = new Blob([report], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `mcms-performance-${Date.now()}.json`;
        link.style.display = 'none';
        (document.body || document.documentElement).appendChild(link);
        link.click();
        link.remove();
        setTimeout(() => URL.revokeObjectURL(url), 0);
    }

    function createPanel() {
        if (!document.body || document.getElementById('mcms-development-profiler')) return;
        const panel = document.createElement('section');
        panel.id = 'mcms-development-profiler';
        panel.setAttribute('aria-label', 'Toolkit development performance profiler');
        panel.style.cssText = 'position:fixed;right:12px;bottom:12px;z-index:2147483647;background:#111;color:#fff;border:1px solid #666;border-radius:8px;padding:8px;font:12px/1.3 system-ui;box-shadow:0 4px 18px #0008;display:flex;gap:6px;align-items:center;flex-wrap:wrap;max-width:min(620px,calc(100vw - 24px))';
        const status = document.createElement('strong');
        status.textContent = 'Profiler stopped';
        const makeButton = (label, action) => {
            const button = document.createElement('button');
            button.type = 'button';
            button.textContent = label;
            button.style.cssText = 'font:inherit;padding:4px 7px;cursor:pointer';
            button.addEventListener('click', action);
            return button;
        };
        const scenario = document.createElement('select');
        scenario.setAttribute('aria-label', 'Profiler scenario');
        scenario.style.cssText = 'font:inherit;padding:4px 7px;max-width:190px';
        for (const value of core.SCENARIOS) {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = value;
            scenario.appendChild(option);
        }
        scenario.addEventListener('change', () => {
            const selected = session.setScenario(scenario.value);
            scenario.value = selected;
            status.textContent = `Profiler ${session.state.active ? 'running' : 'stopped'} · ${selected}`;
        });
        panel.append(status, scenario,
            makeButton('Start', () => { session.start(); status.textContent = `Profiler running · ${session.state.currentScenario}`; }),
            makeButton('Stop', () => { session.stop(); status.textContent = `Profiler stopped · ${session.state.currentScenario}`; }),
            makeButton('Reset', () => { session.reset(); scenario.value = 'unclassified'; status.textContent = 'Profiler reset'; }),
            makeButton('Export', downloadReport));
        document.body.appendChild(panel);
    }

    const api = {
        version: '0.2.0',
        start: session.start,
        stop: session.stop,
        reset: session.reset,
        report: buildReport,
        setScenario: session.setScenario,
        beginRender: session.beginRender,
        endRender: session.endRender,
        export: downloadReport,
        destroy() {
            session.stop();
            document.getElementById('mcms-development-profiler')?.remove();
            for (const observer of observers.splice(0)) observer.disconnect?.();
            if (window.__MCMS_PROFILER__ === api) delete window.__MCMS_PROFILER__;
        },
    };
    window.__MCMS_PROFILER__ = api;

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', createPanel, { once: true });
    else createPanel();
})();
