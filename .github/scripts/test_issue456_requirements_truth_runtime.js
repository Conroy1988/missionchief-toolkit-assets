#!/usr/bin/env node
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..', '..');
const source = fs.readFileSync(path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js'), 'utf8');
function extract(name, nextName) {
    const start = source.indexOf(`    function ${name}(`);
    const end = source.indexOf(`    function ${nextName}(`, start);
    if (start < 0 || end <= start) throw new Error(`Unable to extract ${name}`);
    return source.slice(start, end);
}
const sandbox = {
    console,
    OPERATIONAL_REQUIREMENT_GROUPS: ['vehicles', 'staff', 'other'],
    OPERATIONAL_REQUIREMENTS_PANEL_CLASS: 'mcms-operational-suite-panel',
    operationalRequirementsSortRows: rows => rows.slice(),
    operationalRequirementsEscapeHtml: value => String(value ?? ''),
    operationalRequirementsSelectedText: row => String(row?.selectedValue ?? 0),
    operationalRequirementsEnsureStyle: () => undefined,
    operationalRequirementsScheduleContext: () => undefined,
};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(`${extract('operationalRequirementsPanelHtml', 'operationalRequirementsMount')}\n${extract('operationalRequirementsMount', 'operationalRequirementsRenderContext')}\nglobalThis.panelHtml = operationalRequirementsPanelHtml; globalThis.mount = operationalRequirementsMount;`, sandbox);
const emptyModel = { requirementTexts: { vehicles: { remaining: '' }, staff: { remaining: '' }, other: { remaining: '' } } };
const pending = sandbox.panelHtml([], emptyModel, {}, false, { state: 'pending' });
if (pending.allCovered || pending.state !== 'pending' || /All displayed requirements covered/.test(pending.html)) throw new Error('pending empty source was falsely covered');
if (!/Waiting for MissionChief requirement data/.test(pending.html)) throw new Error('pending source warning missing');
const unparsed = sandbox.panelHtml([], emptyModel, {}, false, { state: 'unparsed' });
if (unparsed.allCovered || unparsed.state !== 'unparsed' || !/could not be interpreted safely/.test(unparsed.html)) throw new Error('unparsed source was not fail-safe');
const coveredRow = { key: 'fire-engine', requirement: 'Fire Engine', covered: true, remainingOnMission: 0, selectedValue: 0, missing: 1, driving: 1, selected: 0 };
const covered = sandbox.panelHtml([coveredRow], emptyModel, {}, false, { state: 'available' });
if (!covered.allCovered || covered.state !== 'covered') throw new Error('positively parsed covered row did not resolve green');
const openRow = { ...coveredRow, covered: false, remainingOnMission: 1, driving: 0 };
const open = sandbox.panelHtml([openRow], emptyModel, {}, false, { state: 'available' });
if (open.allCovered || open.state !== 'open' || !/1 requirement still open/.test(open.html)) throw new Error('open requirement was falsely covered');
const unresolvedModel = { requirementTexts: { vehicles: { remaining: '1 Unknown Vehicle' }, staff: { remaining: '' }, other: { remaining: '' } } };
const unresolved = sandbox.panelHtml([], unresolvedModel, {}, false, { state: 'available' });
if (unresolved.allCovered || unresolved.state !== 'open' || !/Unresolved MissionChief requirement/.test(unresolved.html)) throw new Error('unresolved text was falsely covered');
function fakePanel(doc) {
    return {
        isConnected: true, dataset: {}, attributes: {}, className: '', parentNode: null, nextSibling: null, ownerDocument: doc,
        setAttribute(name, value) { this.attributes[name] = String(value); },
        remove() { this.isConnected = false; },
    };
}
const doc = {
    panels: [],
    querySelectorAll(selector) { return selector === '[data-mcms-operational-suite="requirements"]' ? this.panels.filter(panel => panel.isConnected) : []; },
    createElement() { const panel = fakePanel(this); this.panels.push(panel); return panel; },
};
const parent = { insertBefore(panel, rootNode) { panel.parentNode = this; panel.nextSibling = rootNode; panel.isConnected = true; if (!doc.panels.includes(panel)) doc.panels.push(panel); } };
const requirementRoot = { parentNode: parent };
const first = fakePanel(doc); const second = fakePanel(doc); first.parentNode = parent; second.parentNode = parent; doc.panels.push(first, second);
const context = { doc, panel: null, minified: false, fingerprint: '' };
const mounted = sandbox.mount(context, requirementRoot);
if (mounted !== first || doc.panels.filter(panel => panel.isConnected).length !== 1) throw new Error('duplicate mounted panels were not reconciled');
if (typeof mounted.onclick !== 'function') throw new Error('authoritative panel toggle handler was not installed');
sandbox.mount(context, requirementRoot);
if (doc.panels.filter(panel => panel.isConnected).length !== 1) throw new Error('repeated mount created a duplicate panel');
console.log('Issue #456 requirements truth-state and dedupe runtime passed.');
