#!/usr/bin/env node
'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..', '..');
const source = fs.readFileSync(path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js'), 'utf8');
const start = source.indexOf("    const TRANSPORT_SWEEP_RELEASE_CONFIRMATION_TEXT = 'Understood! We have released the patient.';");
const end = source.indexOf('    async function activateTransportSweepLssmRelease(candidate)', start);
assert.ok(start >= 0 && end > start, 'Transport Sweep release helpers are missing from the userscript');
const helperSource = source.slice(start, end);

function evidenceNode(text, options = {}) {
    return {
        textContent: text,
        isConnected: options.isConnected !== false,
        tagName: options.tagName || 'DIV',
        excluded: Boolean(options.excluded),
        closest() { return this.excluded ? {} : null; }
    };
}

function evidenceDocument(nodes = []) {
    return {
        nodes,
        body: { children: nodes },
        querySelectorAll() { return this.nodes; }
    };
}

const logs = [];
const state = {
    contexts: [],
    visibleRoots: []
};
const context = vm.createContext({
    console,
    Map,
    Set,
    Array,
    String,
    RegExp,
    SCRIPT: {
        panelId: 'toolkit-panel',
        transportSweepHudId: 'transport-sweep-hud'
    },
    transportSweepRuntime: {
        cleared: 0,
        processed: 0,
        errors: 0,
        confirmedReleaseKeys: new Set()
    },
    transportSweepDocumentContexts: () => state.contexts,
    transportSweepVisibleWindowRoots: () => state.visibleRoots,
    transportSweepElementVisible: element => Boolean(element?.isConnected),
    normaliseMissionId: value => {
        const text = String(value ?? '').trim();
        return /^\d+$/.test(text) ? text : null;
    },
    transportSweepLog: (message, level = 'info') => logs.push({ message, level })
});
vm.runInContext(helperSource, context, { filename: 'transport-sweep-release-helpers.js' });

const exact = 'Understood! We have released the patient.';
assert.match(context.transportSweepReleaseConfirmationSignature(exact), /understood! we have released the patient\./);

const stale = evidenceNode(exact);
const staleDoc = evidenceDocument([stale]);
state.contexts = [{ doc: staleDoc, label: 'top' }];
state.visibleRoots = [];
const staleBaseline = context.captureTransportSweepReleaseConfirmationBaseline();
assert.equal(context.transportSweepReleaseConfirmationVisible(staleBaseline), false, 'A stale pre-existing confirmation must not count');

const unrelated = evidenceNode('Mission window refreshed');
staleDoc.nodes.push(unrelated);
staleDoc.body.children = staleDoc.nodes;
assert.equal(context.transportSweepReleaseConfirmationVisible(staleBaseline), false, 'Unrelated DOM changes must not reactivate stale success text');

const replacementAlert = evidenceNode(exact);
staleDoc.nodes = [replacementAlert];
staleDoc.body.children = staleDoc.nodes;
assert.equal(context.transportSweepReleaseConfirmationVisible(staleBaseline), true, 'A replacement alert with the confirmed success text must count');

const pending = evidenceNode('Awaiting patient release');
const pendingDoc = evidenceDocument([pending]);
state.contexts = [{ doc: pendingDoc, label: 'top' }];
const pendingBaseline = context.captureTransportSweepReleaseConfirmationBaseline();
pending.textContent = exact;
assert.equal(context.transportSweepReleaseConfirmationVisible(pendingBaseline), true, 'A newly changed global alert must count');

const windowDoc = evidenceDocument([]);
state.contexts = [{ doc: windowDoc, label: 'top' }];
state.visibleRoots = [];
const windowBaseline = context.captureTransportSweepReleaseConfirmationBaseline();
state.visibleRoots = [evidenceNode(exact)];
assert.equal(context.transportSweepReleaseConfirmationVisible(windowBaseline), true, 'Success after lightbox/root replacement must count');

state.visibleRoots = [];
state.contexts = [{ doc: evidenceDocument([evidenceNode('No release confirmation')]), label: 'top' }];
assert.equal(context.transportSweepReleaseConfirmationVisible(context.captureTransportSweepReleaseConfirmationBaseline()), false, 'Unconfirmed release must remain uncounted');

const releaseKey = context.transportSweepReleaseKey('101', '202');
assert.equal(releaseKey, '101:202');
assert.equal(context.recordTransportSweepConfirmedRelease(releaseKey, 'Cleared patient'), true);
assert.equal(context.transportSweepRuntime.cleared, 1);
assert.equal(context.transportSweepRuntime.processed, 1);
assert.equal(context.transportSweepRuntime.errors, 0);
assert.equal(logs.length, 1);
assert.equal(context.recordTransportSweepConfirmedRelease(releaseKey, 'Duplicate mutation'), false, 'Repeated observers must not double-count a release');
assert.equal(context.transportSweepRuntime.cleared, 1);
assert.equal(context.transportSweepRuntime.processed, 1);
assert.equal(context.transportSweepRuntime.errors, 0);
assert.equal(logs.length, 1);
assert.equal(context.recordTransportSweepConfirmedRelease('', 'Missing identity'), false);

console.log('Transport Sweep runtime confirmation contract passed');
