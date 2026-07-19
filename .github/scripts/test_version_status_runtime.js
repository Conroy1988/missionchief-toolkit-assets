#!/usr/bin/env node
'use strict';
const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const root = path.resolve(__dirname, '..', '..');
const source = fs.readFileSync(path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js'), 'utf8');
const startMarker = '    // Issue #153: stable live Toolkit version-status control.';
const endMarker = '    function createCleanExit() {';
const start = source.indexOf(startMarker);
const end = source.indexOf(endMarker, start);
assert(start >= 0 && end > start, 'unable to extract Issue #153 runtime block');
const block = source.slice(start, end);

class FakeClassList { constructor() { this.values = new Set(); } contains(value) { return this.values.has(value); } toggle(value, force) { const enabled = force === undefined ? !this.values.has(value) : Boolean(force); if (enabled) this.values.add(value); else this.values.delete(value); return enabled; } }
class FakeElement {
    constructor(tagName = 'div', ownerDocument = null) { this.tagName = String(tagName).toUpperCase(); this.ownerDocument = ownerDocument; this.id = ''; this.type = ''; this.className = ''; this.textContent = ''; this.title = ''; this.dataset = {}; this.attributes = new Map(); this.classList = new FakeClassList(); this.children = []; this.parentNode = null; this.queryMap = new Map(); this.listeners = new Map(); this.isConnected = true; }
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
    constructor() { this.nodes = new Set(); this.documentElement = new FakeElement('html', this); this.head = new FakeElement('head', this); this.body = new FakeElement('body', this); this.nodes.add(this.documentElement); this.nodes.add(this.head); this.nodes.add(this.body); }
    createElement(tagName) { return new FakeElement(tagName, this); }
    getElementById(id) { return Array.from(this.nodes).find(node => node.isConnected && node.id === id) || null; }
}

const localValues = new Map();
const openedUrls = [];
const listenedEvents = [];
const document = new FakeDocument();
const context = {
    console, URL, Promise, Date, Object, Array, Number, String, Error, JSON, RegExp, Math, Set,
    queueMicrotask,
    globalThis: null,
    SCRIPT: { name: 'MissionChief Map Command Toolkit', version: '4.20.0', controlId: 'mc-map-command-toolkit-control' },
    pageWindow: { localStorage: { getItem: key => localValues.has(key) ? localValues.get(key) : null, setItem: (key, value) => localValues.set(key, String(value)), removeItem: key => localValues.delete(key) }, open: url => { openedUrls.push(url); return { opener: {} }; }, fetch: null, AbortController },
    document,
    runtime: { destroyed: false, requests: new Set(), fetchControllers: new Set() },
    runtimeListen: (target, type, listener, options) => { target.addEventListener(type, listener, options); listenedEvents.push({ target, type, listener, options }); },
    runtimeSetTimeout: (callback, delay) => setTimeout(callback, delay),
    runtimeClearTimeout: timer => clearTimeout(timer),
    showToast: () => {},
};
context.globalThis = context;
vm.createContext(context);
vm.runInContext(block + `\nthis.__versionStatusApi = { constants: VERSION_STATUS, parse: versionStatusParse, compare: versionStatusCompare, validate: versionStatusValidateManifest, presentation: versionStatusPresentation, cacheFresh: versionStatusCacheIsFresh, failureCooling: versionStatusFailureCooling, ensureButton: ensureVersionStatusButton, requestManifest: versionStatusRequestManifest, runCheck: runVersionStatusCheck, render: versionStatusRender, model: () => versionStatusModel, reset: () => { versionStatusModel = { state: 'idle', manifest: null, checkedAt: 0, error: '' }; versionStatusCheckPromise = null; versionStatusHydrationPromise = null; versionStatusTimer = null; versionStatusRequest = null; } };` , context);
const api = context.__versionStatusApi;
const manifest = version => ({ schemaVersion: 1, channel: 'stable', version, releaseNotesUrl: `https://github.com/Conroy1988/missionchief-toolkit-assets/releases/tag/v${version}`, updateUrl: 'https://update.greasyfork.org/scripts/586018/MissionChief%20Map%20Command%20Toolkit.user.js', publishedAt: '2026-07-19T13:08:02Z' });

(async () => {
    assert.deepStrictEqual(Array.from(api.parse('4.15.10')), [4, 15, 10], 'stable semantic version parses numerically');
    assert.strictEqual(api.parse('4.15'), null, 'malformed installed version is rejected');
    assert.strictEqual(api.parse('4.20.0-beta.1'), null, 'prerelease version is not accepted as stable');
    assert.strictEqual(api.compare('4.15.10', '4.15.9'), 1, 'multi-digit patch versions compare numerically');
    assert.strictEqual(api.compare('4.16.0', '4.15.99'), 1, 'minor update compares numerically');
    assert.strictEqual(api.compare('bad', '4.15.9'), null, 'malformed comparison fails safely');

    const current = api.validate(manifest('4.20.0'));
    assert.strictEqual(api.presentation('4.20.0', current).state, 'latest', 'equal stable version displays LATEST');
    assert.strictEqual(api.presentation('4.20.0', current).destination, current.releaseNotesUrl, 'LATEST opens matching GitHub release notes');
    const patch = api.validate(manifest('4.20.1'));
    assert.strictEqual(api.presentation('4.20.0', patch).state, 'update', 'published patch update displays UPDATE');
    assert.strictEqual(api.presentation('4.20.0', patch).destination, patch.updateUrl, 'UPDATE opens Greasy Fork update URL');
    assert.throws(() => api.validate({ ...manifest('4.20.1-beta.1'), version: '4.20.1-beta.1' }), /stable semantic version/, 'draft or prerelease manifest is rejected');
    assert.throws(() => api.validate({ ...manifest('4.20.1'), releaseNotesUrl: 'https://example.com/release' }), /canonical/, 'non-canonical release URL is rejected');

    const now = 10_000_000;
    assert.strictEqual(api.cacheFresh({ checkedAt: now - (29 * 60 * 1000), manifest: current }, now), true, '29-minute successful cache is fresh');
    assert.strictEqual(api.cacheFresh({ checkedAt: now - (30 * 60 * 1000), manifest: current }, now), false, '30-minute successful cache is stale');
    assert.strictEqual(api.failureCooling({ failedAt: now - (9 * 60 * 1000) }, now), true, '9-minute failure remains in cooldown');
    assert.strictEqual(api.failureCooling({ failedAt: now - (10 * 60 * 1000) }, now), false, '10-minute failure cooldown expires');

    const control = document.createElement('div'); control.id = context.SCRIPT.controlId;
    const row = document.createElement('div'); const shell = document.createElement('div'); const economy = document.createElement('button'); economy.className = 'mcms-economy-btn';
    control.queryMap.set('.mcms-launch-row', row); row.queryMap.set('.mcms-economy-btn', economy);
    document.body.appendChild(control); control.appendChild(row); row.appendChild(shell); row.appendChild(economy);
    const first = api.ensureButton(); const second = api.ensureButton();
    assert.strictEqual(first, second, 'repeated Toolkit UI recovery does not duplicate version control');
    assert.strictEqual(document.getElementById(api.constants.buttonId), first, 'version control uses one collision-resistant ID');
    assert.strictEqual(row.children.indexOf(first), row.children.indexOf(economy) - 1, 'version control is placed immediately before Economy beside the main Toolkit shell');
    const styleText = document.getElementById(api.constants.styleId).textContent;
    assert(styleText.includes('data-mcms-tablet-active'), 'Tablet-specific version-control styling is present');
    assert(styleText.includes('data-mcms-mobile-active'), 'iOS/Mobile-specific version-control styling is present');

    context.GM_xmlhttpRequest = options => { queueMicrotask(() => options.ontimeout()); return { abort() {} }; };
    await assert.rejects(api.requestManifest(), /timed out/, 'network timeout rejects without reporting LATEST');
    context.GM_xmlhttpRequest = options => { queueMicrotask(() => options.onerror()); return { abort() {} }; };
    api.reset(); await api.runCheck(true); assert.strictEqual(api.model().state, 'error', 'rejected request renders retry/error state');
    context.GM_xmlhttpRequest = options => { queueMicrotask(() => options.onload({ status: 200, responseText: JSON.stringify(manifest('4.20.1')) })); return { abort() {} }; };
    api.reset(); await api.runCheck(true); assert.strictEqual(api.model().state, 'update', 'successful live response renders UPDATE');

    console.log('Version status runtime fixtures passed');
})().catch(error => { console.error(error); process.exit(1); });
