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
        if (char === '}' && --depth === 0) return source.slice(start, index + 1);
    }
    throw new Error(`Could not extract ${name}`);
}

const helperSource = [
    'decodedPathname',
    'toolkitTopLevelDocument',
    'toolkitDocumentPathname',
    'toolkitCommandShellRouteEligible',
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

const view = { location: { pathname: '/' } };
view.top = view;
const documentStub = {
    defaultView: view,
    mainMap: null,
    mapOuter: null,
    maps: [],
    querySelector(selector) {
        if (selector === '#map') return this.mainMap;
        if (selector === '#map_outer') return this.mapOuter;
        if (selector === '#control') return null;
        return null;
    },
    querySelectorAll() { return this.maps; },
    getElementById() { return null; },
};

function mapNode({ mission = false, id = 'map' } = {}) {
    return {
        id,
        ownerDocument: documentStub,
        isConnected: true,
        classList: { contains: value => value === 'leaflet-container' },
        matches: () => false,
        closest: () => mission ? {} : null,
    };
}

const mainMap = mapNode();
const missionMap = mapNode({ mission: true, id: 'mission-map' });
const mapOuter = {
    contains: candidate => candidate === mainMap,
    querySelector: () => mainMap,
};
documentStub.mainMap = mainMap;
documentStub.mapOuter = mapOuter;
documentStub.maps = [missionMap];

const calls = [];
let teardownCount = 0;
const sandbox = {
    console,
    Array,
    Boolean,
    String,
    document: documentStub,
    location: view.location,
    SCRIPT: { controlId: 'control', payoutFlashId: 'payout' },
    state: { commandBarOpen: true, economyMode: false, fullscreenMap: false, majorIncidentFeed: { enabled: false }, autoHideDock: { enabled: false }, safeMode: { enabled: false } },
    autoHideDockRevealed: false,
    fullscreenMapTarget: null,
    settingsPanelActivated: false,
    operationalStartupComplete: true,
    mapMeasureRuntime: { active: false, map: null },
    isTouchLayoutActive: () => false,
    getLargestLeafletMap: () => documentStub.mainMap,
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
    maybeShowSetupWizard() { return false; },
    positionPayoutFlashOverlay() {},
    stopMapMeasure() {},
    teardownToolkitCommandShell() { teardownCount += 1; },
};
vm.createContext(sandbox);
vm.runInContext(`${helperSource}\nthis.helpers={toolkitTopLevelDocument,toolkitCommandShellRouteEligible,toolkitPrimaryMapElement,toolkitControlHost,toolkitApplyCommandBarState,ensureUi};`, sandbox);
const helpers = sandbox.helpers;

assert.equal(helpers.toolkitTopLevelDocument(documentStub), true);
const childView = { top: view, location: { pathname: '/missions/123' } };
assert.equal(helpers.toolkitTopLevelDocument({ defaultView: childView }), false);
assert.equal(helpers.toolkitControlHost(missionMap, documentStub), mainMap, 'canonical map wins over a mission-window map');

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
assert.equal(helpers.ensureUi(), true);
assert.equal(calls.at(-1), mainMap, 'launcher mounts on the canonical map');

view.location.pathname = '/missions/123';
assert.equal(helpers.ensureUi(), true, 'known non-map route settles without launcher recovery retries');
assert.equal(teardownCount, 1, 'standalone mission route tears down the launcher');
assert.equal(calls.length, 1, 'standalone mission route did not create a launcher');

view.location.pathname = '/';
documentStub.mainMap = null;
documentStub.mapOuter = null;
assert.equal(helpers.toolkitControlHost(null, documentStub), null, 'document/body fallback is retired');
assert.equal(helpers.ensureUi(), false, 'root route waits for positive canonical map evidence');
assert.equal(teardownCount, 2);

console.log('Issue #515 launcher runtime passed with Issue #638 canonical-map ownership hardening.');
