#!/usr/bin/env node
'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..', '..');
const source = fs.readFileSync(path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js'), 'utf8');
const startMarker = '    // Issue #153 introduced the control; Issue #639 makes verified release discovery live and TKB-first.';
const endMarker = '    function createCleanExit() {';
const start = source.indexOf(startMarker);
const end = source.indexOf(endMarker, start);
assert.ok(start >= 0 && end > start, 'unable to extract version-status runtime block');
const block = source.slice(start, end);

class FakeClassList {
    constructor() { this.values = new Set(); }
    contains(value) { return this.values.has(value); }
    toggle(value, force) {
        const enabled = force === undefined ? !this.values.has(value) : Boolean(force);
        if (enabled) this.values.add(value); else this.values.delete(value);
        return enabled;
    }
}
class FakeElement {
    constructor(tagName = 'div', ownerDocument = null) {
        this.tagName = String(tagName).toUpperCase();
        this.ownerDocument = ownerDocument;
        this.id = '';
        this.type = '';
        this.className = '';
        this.textContent = '';
        this.title = '';
        this.dataset = {};
        this.attributes = new Map();
        this.classList = new FakeClassList();
        this.children = [];
        this.parentNode = null;
        this.queryMap = new Map();
        this.listeners = new Map();
        this.isConnected = true;
    }
    setAttribute(name, value) { this.attributes.set(name, String(value)); if (name === 'id') this.id = String(value); }
    getAttribute(name) { return this.attributes.get(name) || null; }
    querySelector(selector) { return this.queryMap.get(selector) || null; }
    addEventListener(type, listener) { const list = this.listeners.get(type) || []; list.push(listener); this.listeners.set(type, list); }
    appendChild(child) { child.parentNode = this; child.ownerDocument ||= this.ownerDocument; child.isConnected = true; this.children.push(child); child.ownerDocument?.nodes.add(child); return child; }
    insertBefore(child, reference) { if (child.parentNode) child.parentNode.children = child.parentNode.children.filter(item => item !== child); child.parentNode = this; child.ownerDocument ||= this.ownerDocument; child.isConnected = true; const index = this.children.indexOf(reference); if (index >= 0) this.children.splice(index, 0, child); else this.children.push(child); child.ownerDocument?.nodes.add(child); return child; }
    contains(node) { return this === node || this.children.some(child => child.contains?.(node)); }
    remove() { this.isConnected = false; if (this.parentNode) this.parentNode.children = this.parentNode.children.filter(child => child !== this); this.ownerDocument?.nodes.delete(this); }
}
class FakeDocument {
    constructor() {
        this.nodes = new Set();
        this.documentElement = new FakeElement('html', this);
        this.head = new FakeElement('head', this);
        this.body = new FakeElement('body', this);
        this.visibilityState = 'visible';
        this.nodes.add(this.documentElement);
        this.nodes.add(this.head);
        this.nodes.add(this.body);
    }
    createElement(tagName) { return new FakeElement(tagName, this); }
    getElementById(id) { return Array.from(this.nodes).find(node => node.isConnected && node.id === id) || null; }
    querySelector(selector) { return String(selector).startsWith('#') ? this.getElementById(String(selector).slice(1)) : null; }
}

const productUrl = 'https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/';
const localValues = new Map();
const openedUrls = [];
const listenedEvents = [];
const document = new FakeDocument();
const context = {
    console,
    URL,
    Promise,
    Date,
    Object,
    Array,
    Number,
    String,
    Error,
    JSON,
    RegExp,
    Math,
    Set,
    queueMicrotask,
    globalThis: null,
    SCRIPT: { name: 'MissionChief Map Command Toolkit', version: '10.2.9', controlId: 'mc-map-command-toolkit-control' },
    pageWindow: {
        localStorage: {
            getItem: key => localValues.has(key) ? localValues.get(key) : null,
            setItem: (key, value) => localValues.set(key, String(value)),
            removeItem: key => localValues.delete(key),
        },
        open: url => { openedUrls.push(url); return { opener: {} }; },
        fetch: null,
        AbortController,
    },
    document,
    runtime: { destroyed: false, requests: new Set(), fetchControllers: new Set() },
    runtimeListen: (target, type, listener, options) => { target.addEventListener(type, listener, options); listenedEvents.push({ target, type, listener, options }); },
    runtimeSetTimeout: (callback, delay) => setTimeout(callback, delay),
    runtimeClearTimeout: timer => clearTimeout(timer),
    toolkitCommandShellContextActive: () => true,
    showToast: () => undefined,
};
context.globalThis = context;
vm.createContext(context);
vm.runInContext(block + `
this.__versionStatusApi = {
  constants: VERSION_STATUS,
  parse: versionStatusParse,
  compare: versionStatusCompare,
  validate: versionStatusValidateManifest,
  presentation: versionStatusPresentation,
  cacheFresh: versionStatusCacheIsFresh,
  failureCooling: versionStatusFailureCooling,
  ensureButton: ensureVersionStatusButton,
  requestManifest: versionStatusRequestManifest,
  runCheck: runVersionStatusCheck,
  render: versionStatusRender,
  open: versionStatusOpen,
  model: () => versionStatusModel,
  nextDelay: versionStatusAutomaticDelay,
  schedule: scheduleVersionStatusCheck,
  dispose: disposeVersionStatus,
  timer: () => versionStatusTimer,
  request: () => versionStatusRequest,
  setModel: value => { versionStatusModel = { ...versionStatusModel, ...value }; },
  reset: () => {
    versionStatusModel = { state: 'idle', manifest: null, checkedAt: 0, failedAt: 0, error: '' };
    versionStatusCheckPromise = null;
    versionStatusHydrationPromise = null;
    versionStatusTimer = null;
    versionStatusRequest = null;
    versionStatusRequestToken += 1;
    versionStatusInitialCheckQueued = false;
  }
};`, context);
const api = context.__versionStatusApi;
const manifest = version => ({
    schemaVersion: 1,
    channel: 'stable',
    version,
    releaseNotesUrl: `https://github.com/Conroy1988/missionchief-toolkit-assets/releases/tag/v${version}`,
    updateUrl: 'https://tkb-gaming.scot/mission-chief-scripts/map-command-toolkit/install/',
    publishedAt: '2026-08-01T20:00:00Z',
});

function click(element, overrides = {}) {
    const listener = element.listeners.get('click')?.[0];
    assert.equal(typeof listener, 'function', 'button click listener missing');
    listener({ preventDefault() {}, shiftKey: false, ...overrides });
}

(async () => {
    assert.deepEqual(Array.from(api.parse('10.2.10')), [10, 2, 10]);
    assert.equal(api.parse('10.2'), null);
    assert.equal(api.parse('10.2.10-beta.1'), null);
    assert.equal(api.compare('10.2.10', '10.2.9'), 1, 'multi-digit patch comparison is numeric');
    assert.equal(api.compare('10.3.0', '10.2.99'), 1);
    assert.equal(api.compare('11.0.0', '10.99.99'), 1);

    const current = api.validate(manifest('10.2.9'));
    const patch = api.validate(manifest('10.2.10'));
    assert.equal(api.presentation('10.2.9', current).state, 'latest');
    assert.equal(api.presentation('10.2.9', patch).state, 'update');
    assert.equal(api.presentation('10.2.9', current).destination, productUrl);
    assert.equal(api.presentation('10.2.9', patch).destination, productUrl);
    assert.throws(() => api.validate({ ...manifest('10.2.10-beta.1'), version: '10.2.10-beta.1' }), /stable semantic version/);
    assert.throws(() => api.validate({ ...manifest('10.2.10'), releaseNotesUrl: 'https://example.com/release' }), /canonical/);

    const now = 10_000_000;
    assert.equal(api.cacheFresh({ checkedAt: now - 59_999, manifest: current }, now), true);
    assert.equal(api.cacheFresh({ checkedAt: now - 60_000, manifest: current }, now), false);
    assert.equal(api.failureCooling({ failedAt: now - 59_999 }, now), true);
    assert.equal(api.failureCooling({ failedAt: now - 60_000 }, now), false);
    assert.equal(api.constants.autoIntervalMs, 60_000);
    assert.equal(api.constants.cacheMs, 60_000);
    assert.equal(api.constants.failureCooldownMs, 60_000);
    assert.equal(api.constants.productUrl, productUrl);
    api.setModel({ state: 'latest', manifest: current, checkedAt: now, failedAt: 0, error: '' });
    assert.equal(api.nextDelay(now), 60_000, 'next successful check is scheduled for 60 seconds');
    api.setModel({ state: 'latest', manifest: current, checkedAt: now - 60_000, failedAt: now, error: 'offline' });
    assert.equal(api.nextDelay(now), 60_000, 'transient failure retry is scheduled for 60 seconds');

    const scheduledTimers = [];
    const clearedTimers = [];
    context.runtimeSetTimeout = (callback, delay) => { const timer = { callback, delay, cleared: false }; scheduledTimers.push(timer); return timer; };
    context.runtimeClearTimeout = timer => { if (timer) { timer.cleared = true; clearedTimers.push(timer); } };

    const control = document.createElement('div');
    control.id = context.SCRIPT.controlId;
    const row = document.createElement('div');
    const shell = document.createElement('div');
    const economy = document.createElement('button');
    economy.className = 'mcms-economy-btn';
    control.queryMap.set('.mcms-launch-row', row);
    row.queryMap.set('.mcms-economy-btn', economy);
    document.body.appendChild(control);
    control.appendChild(row);
    row.appendChild(shell);
    row.appendChild(economy);

    const first = api.ensureButton();
    const second = api.ensureButton();
    await Promise.resolve();
    assert.equal(first, second, 'repeated launcher reconciliation reuses one button');
    assert.equal(document.getElementById(api.constants.buttonId), first);
    assert.equal(row.children.indexOf(first), row.children.indexOf(economy) - 1);
    assert.equal(scheduledTimers.filter(timer => !timer.cleared).length, 1, 'button mount creates exactly one initial timer');
    assert.equal(scheduledTimers.at(-1).delay, api.constants.bootDelayMs, 'initial check is queued shortly after mount');
    assert.equal(first.getAttribute('aria-live'), 'polite');

    api.setModel({ state: 'latest', manifest: current, checkedAt: Date.now(), failedAt: 0, error: '' });
    api.render();
    assert.equal(first.dataset.label, 'LATEST');
    assert.equal(first.classList.contains('mcms-version-update-alert'), false);
    assert.match(first.title, /is current — open official Toolkit page/u);
    click(first);
    assert.equal(openedUrls.at(-1), productUrl, 'LATEST opens the official TKB product page');

    api.setModel({ state: 'update', manifest: patch, checkedAt: Date.now(), failedAt: 0, error: '' });
    api.render();
    assert.equal(first.dataset.label, 'UPDATE');
    assert.equal(first.classList.contains('mcms-version-update-alert'), true);
    assert.match(first.title, /10\.2\.10 available — open official update page/u);
    click(first);
    assert.equal(openedUrls.at(-1), productUrl, 'UPDATE opens the official TKB product page');
    assert.ok(openedUrls.every(url => url === productUrl), 'version button exposed a non-TKB destination');

    const alertStyle = document.getElementById(api.constants.alertStyleId).textContent;
    assert.match(alertStyle, /@keyframes mcmsVersionUpdateNeon/u);
    assert.match(alertStyle, /data-state="update"/u);
    assert.match(alertStyle, /prefers-reduced-motion:reduce/u);
    assert.match(alertStyle, /animation:none !important/u, 'reduced-motion update halo is static');
    assert.match(alertStyle, /box-shadow:0 0 7px/u, 'reduced-motion update halo remains conspicuous');
    const baseStyle = document.getElementById(api.constants.styleId).textContent;
    assert.match(baseStyle, /data-mcms-tablet-active/u);
    assert.match(baseStyle, /data-mcms-mobile-active/u);
    assert.match(baseStyle, /width:48px!important;min-width:48px!important;max-width:48px!important;height:48px!important/u);

    // A release appearing between scheduled checks changes the live state without reload.
    context.GM_xmlhttpRequest = options => { queueMicrotask(() => options.onload({ status: 200, responseText: JSON.stringify(manifest('10.2.9')) })); return { abort() {} }; };
    api.reset();
    await api.runCheck(true);
    assert.equal(api.model().state, 'latest');
    context.GM_xmlhttpRequest = options => { queueMicrotask(() => options.onload({ status: 200, responseText: JSON.stringify(manifest('10.2.10')) })); return { abort() {} }; };
    await api.runCheck(true);
    assert.equal(api.model().state, 'update');
    assert.equal(first.dataset.label, 'UPDATE');

    // Returning to current status removes both the alert class and animation state.
    context.GM_xmlhttpRequest = options => { queueMicrotask(() => options.onload({ status: 200, responseText: JSON.stringify(manifest('10.2.9')) })); return { abort() {} }; };
    await api.runCheck(true);
    assert.equal(api.model().state, 'latest');
    assert.equal(first.classList.contains('mcms-version-update-alert'), false);

    // Failure after a verified result preserves that result; failed first check remains neutral.
    context.GM_xmlhttpRequest = options => { queueMicrotask(() => options.onerror()); return { abort() {} }; };
    api.setModel({ state: 'update', manifest: patch, checkedAt: Date.now(), failedAt: 0, error: '' });
    await api.runCheck(true);
    assert.equal(api.model().state, 'update');
    assert.equal(api.model().manifest.version, '10.2.10');
    api.reset();
    await api.runCheck(true);
    assert.equal(api.model().state, 'error');
    assert.equal(api.model().manifest, null);
    assert.equal(first.dataset.label, 'CHECK', 'failed first check does not falsely render LATEST');

    // Concurrent callers share one in-flight request.
    let liveOptions = null;
    let requestCount = 0;
    context.GM_xmlhttpRequest = options => { requestCount += 1; liveOptions = options; return { abort() {} }; };
    api.reset();
    const pendingA = api.runCheck(true);
    const pendingB = api.runCheck(true);
    await Promise.resolve();
    assert.equal(requestCount, 1, 'overlapping checks created more than one request');
    liveOptions.onload({ status: 200, responseText: JSON.stringify(manifest('10.2.10')) });
    await Promise.all([pendingA, pendingB]);
    assert.equal(api.model().state, 'update');

    // Teardown clears the timer, aborts the request, and ignores its stale completion.
    let aborted = 0;
    let staleOptions = null;
    context.GM_xmlhttpRequest = options => { staleOptions = options; return { abort() { aborted += 1; options.onabort(); } }; };
    api.reset();
    const staleCheck = api.runCheck(true);
    await Promise.resolve();
    api.schedule(60_000, false);
    const activeTimer = api.timer();
    api.dispose();
    assert.equal(activeTimer.cleared, true, 'teardown did not clear the update timer');
    assert.equal(aborted, 1, 'teardown did not abort the in-flight update request');
    await staleCheck;
    assert.equal(document.getElementById(api.constants.buttonId), null);
    assert.equal(document.getElementById(api.constants.alertStyleId), null);
    staleOptions?.onload?.({ status: 200, responseText: JSON.stringify(manifest('99.0.0')) });
    assert.notEqual(api.model().manifest?.version, '99.0.0', 'stale response changed version state after teardown');

    // Hidden tabs do no background work; foreground recovery can schedule an immediate freshness check.
    api.reset();
    document.visibilityState = 'hidden';
    api.schedule(1234, false);
    const hiddenTimer = api.timer();
    await hiddenTimer.callback();
    assert.equal(api.timer(), null);
    document.visibilityState = 'visible';

    console.log('Version status runtime fixtures passed: 60-second verified cadence, semantic comparison, TKB-only navigation, neon accessibility, failure preservation, overlap prevention and teardown safety.');
})().catch(error => { console.error(error); process.exit(1); });
