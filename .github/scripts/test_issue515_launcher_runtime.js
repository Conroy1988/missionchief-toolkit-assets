#!/usr/bin/env node
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..', '..');
const source = fs.readFileSync(path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js'), 'utf8');

function extractFunction(name) {
    const marker = `    function ${name}(`;
    const start = source.indexOf(marker);
    assert.ok(start >= 0, `${name} is missing`);
    const open = source.indexOf('{', start);
    let depth = 0;
    let quote = '';
    let escaped = false;
    for (let index = open; index < source.length; index += 1) {
        const char = source[index];
        if (quote) {
            if (escaped) escaped = false;
            else if (char === '\\') escaped = true;
            else if (char === quote) quote = '';
            continue;
        }
        if (char === '"' || char === "'" || char === '`') { quote = char; continue; }
        if (char === '{') depth += 1;
        if (char === '}') {
            depth -= 1;
            if (depth === 0) return source.slice(start, index + 1);
        }
    }
    throw new Error(`Could not extract ${name}`);
}

const helperSource = [
    'toolkitTopLevelDocument',
    'toolkitPrimaryMapElement',
    'toolkitControlHost',
    'toolkitApplyCommandBarState',
    'ensureUi',
].map(extractFunction).join('\n\n');

function styleNode() {
    return {
        values: new Map(),
        removeProperty(name) { this.values.delete(name); },
        setProperty(name, value, priority) { this.values.set(name, { value, priority }); },
    };
}

const filter = { style: styleNode() };
const pins = { style: styleNode() };
const icon = { textContent: '' };
const dock = {
    title: '',
    attrs: {},
    classList: { state: false, toggle(_name, value) { this.state = value; } },
    setAttribute(name, value) { this.attrs[name] = String(value); },
    querySelector(selector) { return selector === '.mcms-dock-toggle-icon' ? icon : null; },
};
const control = {
    attrs: {},
    setAttribute(name, value) { this.attrs[name] = String(value); },
    querySelector(selector) {
        if (selector === '.mcms-floating-filter') return filter;
        if (selector === '.mcms-screen-pins') return pins;
        if (selector === '.mcms-dock-toggle-btn') return dock;
        return null;
    },
};

function mapNode(doc, { mission = false, id = '' } = {}) {
    return {
        id,
        ownerDocument: doc,
        isConnected: true,
        closest() { return mission ? {} : null; },
    };
}

const view = {}; view.top = view;
const body = { name: 'body' };
const documentStub = {
    defaultView: view,
    body,
    documentElement: { name: 'html' },
    mainMap: null,
    maps: [],
    querySelector(selector) {
        if (selector === '#map') return this.mainMap;
        if (selector === '#control') return null;
        return null;
    },
    querySelectorAll() { return this.maps; },
    getElementById() { return null; },
};

const calls = [];
const sandbox = {
    console,
    Array,
    Boolean,
    String,
    document: documentStub,
    SCRIPT: { controlId: 'control', payoutFlashId: 'payout' },
    state: { commandBarOpen: true, economyMode: false, fullscreenMap: false, majorIncidentFeed: { enabled: false } },
    fullscreenMapTarget: null,
    settingsPanelActivated: false,
    operationalStartupComplete: true,
    getLargestLeafletMap: () => null,
    createControl: map => { calls.push(map); return control; },
    createPanel() {},
    ensureVersionStatusButton() {},
    findLeafletMapInstance: () => null,
    applyLeafletEconomyPolicy() {},
    scheduleEconomyLayerSync() {},
    scheduleMajorIncidentFeedRender() {},
    removeMajorIncidentFeed() {},
    applyMapFullscreenState() {},
    maybeShowUpdateBriefing() {},
    positionPayoutFlashOverlay() {},
};
vm.createContext(sandbox);
vm.runInContext(`${helperSource}\nthis.helpers={toolkitTopLevelDocument,toolkitPrimaryMapElement,toolkitControlHost,toolkitApplyCommandBarState,ensureUi};`, sandbox);
const helpers = sandbox.helpers;

assert.equal(helpers.toolkitTopLevelDocument(documentStub), true);
const childView = { top: view };
assert.equal(helpers.toolkitTopLevelDocument({ defaultView: childView }), false);
assert.equal(helpers.toolkitControlHost(null, documentStub), body, 'document fallback host must remain available before map discovery');

const missionMap = mapNode(documentStub, { mission: true });
const mainMap = mapNode(documentStub, { id: 'map' });
documentStub.mainMap = mainMap;
documentStub.maps = [missionMap, mainMap];
assert.equal(helpers.toolkitPrimaryMapElement(missionMap, documentStub), mainMap, 'main map must win over mission-window maps');
assert.equal(helpers.toolkitControlHost(missionMap, documentStub), mainMap);

helpers.toolkitApplyCommandBarState(control);
assert.equal(control.attrs['data-mcms-command-bar-open'], 'true');
assert.equal(dock.attrs['aria-expanded'], 'true');
assert.equal(icon.textContent, '▴');
sandbox.state.commandBarOpen = false;
helpers.toolkitApplyCommandBarState(control);
assert.equal(control.attrs['data-mcms-command-bar-open'], 'false');
assert.equal(filter.style.values.get('display').value, 'none');
assert.equal(pins.style.values.get('display').priority, 'important');
assert.equal(icon.textContent, '▾');

sandbox.state.commandBarOpen = true;
documentStub.mainMap = null;
documentStub.maps = [];
calls.length = 0;
assert.equal(helpers.ensureUi(), true);
assert.equal(calls.length, 1);
assert.equal(calls[0], null, 'launcher must mount through the document fallback before a map exists');

documentStub.mainMap = mainMap;
calls.length = 0;
assert.equal(helpers.ensureUi(), true);
assert.equal(calls[0], mainMap, 'launcher must bind to the primary map when available');

console.log('Issue #515 launcher runtime contract passed.');
