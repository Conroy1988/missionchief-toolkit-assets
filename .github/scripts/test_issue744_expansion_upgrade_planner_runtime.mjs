#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';
import { JSDOM } from 'jsdom';


const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const source = fs.readFileSync(path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js'), 'utf8');
const start = source.indexOf('    function expansionPlannerText(');
const end = source.indexOf('    function vehicleTargetInfo(', start);
assert.ok(start >= 0 && end > start, 'Issue #744 Expansion Planner helpers are missing');

const shell = new JSDOM(`<!doctype html><html><body><section id="panel" class="mcms-open">
<select data-setting="expansion-planner-centre"></select><select data-setting="expansion-planner-building-type"></select>
<select data-setting="expansion-planner-operation"><option value="all">All</option><option value="level">Level</option><option value="extension">Extension</option></select>
<input data-setting="expansion-planner-budget"><input data-setting="expansion-planner-max-stations">
<select data-setting="expansion-planner-delay"><option value="1500">1.5 seconds</option></select>
<button data-action="load-expansion-planner"></button><button data-action="scan-expansion-planner"></button>
<button data-action="apply-expansion-planner"></button><button data-action="stop-expansion-planner"></button>
<button data-action="select-all-expansion-planner"></button><button data-action="clear-expansion-planner"></button>
<div data-expansion-planner></div></section></body></html>`, { url: 'https://www.missionchief.co.uk/' });

const expansionPlannerRuntime = {
    running: false, preparing: false, stopRequested: false, catalogPromise: null, scanPromise: null,
    dispatches: [{ id: '10', name: 'North Dispatch' }], typeLabels: { 0: 'Fire Station' }, buildings: [], catalogAt: 0,
    queue: [], summary: null, scannedAt: 0, scannedDispatchId: '', scannedTypeId: '', scannedOperationKind: '', scannedMaxStations: 0,
    selectedOperationIds: new Set(), currentBuildingId: '', currentItem: '', processed: 0, purchased: 0, skipped: 0,
    errors: 0, creditsSpent: 0, startedAt: 0, singleBuildingApi: '', lastReport: null, log: [],
};
const context = vm.createContext({
    console, Date, Set, Map, Array, Number, String, Object, Promise, Error, URL, URLSearchParams, Math, JSON,
    FormData: shell.window.FormData, DOMParser: shell.window.DOMParser, document: shell.window.document,
    pageWindow: { location: shell.window.location, confirm: () => true }, runtime: { destroyed: false },
    SCRIPT: { panelId: 'panel', version: '10.14.0', expansionPlannerReportState: 'upgrade-report' },
    state: { expansionPlanner: { dispatchId: '10', buildingTypeId: 'all-types', operationKind: 'all', creditBudget: '500000', maxStations: 100, delayMs: 1500 } },
    expansionPlannerRuntime,
    dispatchRecruitmentRuntime: { running: false, scanPromise: null, catalogPromise: null },
    stationIconCopierRuntime: { running: false, preparing: false, scanPromise: null, catalogPromise: null },
    DISPATCH_RECRUITMENT_ALL_CENTRES: 'all', DISPATCH_RECRUITMENT_ALL_TYPES: 'all-types',
    EXPANSION_PLANNER_OPERATION_OPTIONS: Object.freeze(['all', 'level', 'extension']),
    EXPANSION_PLANNER_DELAY_OPTIONS: Object.freeze([1000, 1500, 2000, 3000, 5000]),
    EXPANSION_PLANNER_SCAN_STATION_LIMIT: 500, EXPANSION_PLANNER_SCAN_CONCURRENCY: 4,
    EXPANSION_PLANNER_OPERATION_LIMIT: 1000, EXPANSION_PLANNER_APPLY_LIMIT: 100,
    EXPANSION_PLANNER_MAX_BUDGET: 2000000000, EXPANSION_PLANNER_REQUEST_TIMEOUT_MS: 15000,
    commandExperienceElement: id => shell.window.document.getElementById(id),
    parseDispatchRecruitmentCatalog: () => ({ dispatches: [], typeLabels: {} }),
    escapeHtml: value => String(value).replaceAll('&', '&amp;').replaceAll('"', '&quot;').replaceAll('<', '&lt;').replaceAll('>', '&gt;'),
    setInnerHtmlIfChanged(element, html) { if (!element || element.innerHTML === html) return false; element.innerHTML = html; return true; },
    updateUiSetProperty(element, property, value) { if (!element) return false; element[property] = value; return true; },
    clamp(value, min, max, fallback) { const number = Number(value); return Number.isFinite(number) ? Math.min(max, Math.max(min, number)) : fallback; },
    runtimeDelay: async () => true, runtimeFetch: async () => { throw new Error('runtimeFetch mock was not installed'); },
    renderDispatchRecruitmentPanel: () => {}, renderStationIconCopierPanel: () => {},
    showToast: () => {}, saveState: () => {}, toolkitAnalyticsRecordFeature: () => {},
    gmGetValueSafe: () => '', gmSetValueSafe: () => true, gmDeleteValueSafe: () => true,
});
vm.runInContext(source.slice(start, end), context, { filename: 'issue744-expansion-upgrade-planner.js' });

expansionPlannerRuntime.catalogPromise = Promise.resolve(['catalogue-in-flight']);
assert.deepEqual(Array.from(await context.loadExpansionPlannerCatalog()), ['catalogue-in-flight'], 'A concurrent load must await the authoritative in-flight catalogue');
expansionPlannerRuntime.catalogPromise = null;

const raw = { id: 101, caption: 'Central Fire', building_type: 0, leitstelle_building_id: 10, small_building: false, level: 2, latitude: 51.1, longitude: -1.1, extensions: [] };
const record = context.normaliseExpansionPlannerRecord(raw);
assert.equal(record.id, '101');
assert.equal(record.level, 2);

const parsed = html => new shell.window.DOMParser().parseFromString(html, 'text/html');
const nativePage = parsed(`<!doctype html><html><head><meta name="csrf-token" content="csrf-live"></head><body>
<div class="alert"><a data-method="post" href="/buildings/101/expand">Upgrade — 20,000 Credits</a><a data-method="post" href="/buildings/101/coins_expand">10 Coins</a></div>
<table id="ausbauten"><tbody><tr><td><b>Water Rescue Extension</b></td><td>
<a data-method="post" href="/buildings/101/extension/4">100.000 Credits</a>
<a data-method="post" href="/buildings/101/extension/4/coins">15 Coins</a>
<a href="/buildings/101/extension/5">50,000 Credits</a>
<a data-method="post" href="https://evil.example/buildings/101/extension/6">1 Credits</a>
</td></tr></tbody></table></body></html>`);
const actions = context.parseExpansionPlannerActions(nativePage, record, 'all');
assert.equal(actions.ambiguous, 0);
assert.deepEqual(Array.from(actions.operations, operation => [operation.kind, operation.label, operation.priceCredits, operation.actionPath]), [
    ['level', 'Upgrade', 20000, '/buildings/101/expand'],
    ['extension', 'Water Rescue Extension', 100000, '/buildings/101/extension/4'],
]);
assert.equal(actions.operations.some(operation => /coin/iu.test(operation.actionPath)), false, 'Coin actions must never enter the queue');

const ambiguousPage = parsed(`<meta name="csrf-token" content="x"><table id="ausbauten"><tr><td><b>Ambiguous</b></td><td><a data-method="post" href="/buildings/101/extension/9">10,000 Credits</a><a data-method="post" href="/buildings/101/extension/9">10,000 Credits</a></td></tr></table>`);
const ambiguous = context.parseExpansionPlannerActions(ambiguousPage, record, 'extension');
assert.equal(ambiguous.operations.length, 0);
assert.equal(ambiguous.ambiguous, 2);

const pendingRecord = context.normaliseExpansionPlannerRecord({ ...raw, extensions: [{ caption: 'Water Rescue', type_id: 4, enabled: false, available: false, available_at: '2026-08-25T10:00:00Z' }] });
assert.equal(context.expansionPlannerHasPendingConstruction(pendingRecord, nativePage), true);

const publicLevel = context.expansionPlannerPublicOperation(actions.operations[0], record, 'North Dispatch', 'Fire Station');
const publicExtension = context.expansionPlannerPublicOperation(actions.operations[1], record, 'North Dispatch', 'Fire Station');
expansionPlannerRuntime.queue = [publicLevel, publicExtension];
context.expansionPlannerSetTarget(publicLevel.operationId, true);
context.expansionPlannerSetTarget(publicExtension.operationId, true);
assert.deepEqual(Array.from(expansionPlannerRuntime.selectedOperationIds), [publicExtension.operationId], 'Only one approved operation may remain selected for a station');

const preparedAnchor = context.prepareExpansionPlannerSubmission(actions.operations[1], nativePage);
assert.equal(preparedAnchor.href, 'https://www.missionchief.co.uk/buildings/101/extension/4');
assert.equal(preparedAnchor.body.get('_method'), 'post');
assert.equal(preparedAnchor.body.get('authenticity_token'), 'csrf-live');

const formPage = parsed(`<table id="ausbauten"><tr><td><b>Drone Extension</b></td><td><form method="post" action="/buildings/101/extension/7"><input name="authenticity_token" value="form-token"><input name="unchanged" value="preserved"><button type="submit" name="buy" value="credits">Buy 75,000 Credits</button><button type="submit" name="buy" value="coins">Buy 15 Coins</button></form></td></tr></table>`);
const formActions = context.parseExpansionPlannerActions(formPage, record, 'extension');
assert.equal(formActions.operations.length, 1);
const preparedForm = context.prepareExpansionPlannerSubmission(formActions.operations[0], formPage);
assert.equal(preparedForm.body.get('authenticity_token'), 'form-token');
assert.equal(preparedForm.body.get('unchanged'), 'preserved');
assert.equal(preparedForm.body.get('buy'), 'credits');

const requests = [];
context.runtimeFetch = async (input, init = {}) => { requests.push({ url: String(input), init }); return { ok: true, status: 200, url: 'https://www.missionchief.co.uk/buildings/101' }; };
await context.submitExpansionPlannerOperation(preparedAnchor, publicExtension);
assert.equal(requests.length, 1);
assert.equal(requests[0].init.method, 'POST');
assert.equal(requests[0].init.credentials, 'same-origin');

context.runtimeFetch = async () => ({ ok: true, status: 200, url: 'https://evil.example/' });
await assert.rejects(context.submitExpansionPlannerOperation(preparedAnchor, publicExtension), error => error?.expansionPlannerFatal === true && error.message.includes('outside the authenticated'));

const changedPricePage = parsed(`<meta name="csrf-token" content="x"><table id="ausbauten"><tr><td><b>Water Rescue Extension</b></td><td><a data-method="post" href="/buildings/101/extension/4">120,000 Credits</a></td></tr></table>`);
assert.throws(() => context.expansionPlannerFindCurrentAction(changedPricePage, record, publicExtension), error => error?.expansionPlannerFatal === true && error.message.includes('unavailable or ambiguous'));

const beforeExtension = record;
const afterExtension = context.normaliseExpansionPlannerRecord({ ...raw, extensions: [{ caption: 'Water Rescue Extension', type_id: 4, enabled: false, available: false, available_at: '2026-08-22T10:00:00Z' }] });
let apiRecords = [beforeExtension, afterExtension];
let pages = [nativePage, parsed('<table id="ausbauten"><tr><td><b>Water Rescue Extension</b></td><td><span data-end-time="123">Building</span></td></tr></table>')];
let submitted = 0;
context.fetchExpansionPlannerBuilding = async () => apiRecords.shift();
context.fetchExpansionPlannerDocument = async () => ({ doc: pages.shift() });
context.submitExpansionPlannerOperation = async () => { submitted += 1; };
const applied = await context.applyExpansionPlannerOperation(publicExtension, 500000);
assert.equal(submitted, 1);
assert.match(applied.detail, /100,000 Credits verified/u);

apiRecords = [beforeExtension];
pages = [nativePage];
submitted = 0;
expansionPlannerRuntime.stopRequested = false;
context.fetchExpansionPlannerBuilding = async () => {
    expansionPlannerRuntime.stopRequested = true;
    return apiRecords.shift();
};
context.fetchExpansionPlannerDocument = async () => ({ doc: pages.shift() });
await assert.rejects(context.applyExpansionPlannerOperation(publicExtension, 500000), error => error?.expansionPlannerStoppedBeforeMutation === true && error.message.includes('before submission'));
assert.equal(submitted, 0, 'Stop during the final pre-purchase read must prevent the mutation request');
expansionPlannerRuntime.stopRequested = false;

const runOne = { ...publicLevel, buildingId: '101', operationId: '101:one', fingerprint: 'one', actionPath: '/buildings/101/expand', priceCredits: 20000 };
const runTwo = { ...publicExtension, buildingId: '102', name: 'West Fire', operationId: '102:two', fingerprint: 'two', actionPath: '/buildings/102/extension/4', priceCredits: 100000 };
expansionPlannerRuntime.queue = [runOne, runTwo];
expansionPlannerRuntime.selectedOperationIds = new Set([runOne.operationId, runTwo.operationId]);
expansionPlannerRuntime.scannedAt = Date.now();
expansionPlannerRuntime.scannedDispatchId = '10';
expansionPlannerRuntime.scannedTypeId = 'all-types';
expansionPlannerRuntime.scannedOperationKind = 'all';
expansionPlannerRuntime.scannedMaxStations = 100;
context.preflightExpansionPlannerSelection = async items => items;
let active = 0;
let maxActive = 0;
const order = [];
context.applyExpansionPlannerOperation = async item => {
    active += 1; maxActive = Math.max(maxActive, active); order.push(item.buildingId);
    await Promise.resolve(); active -= 1;
    return { record, detail: `${item.label} · ${item.priceCredits.toLocaleString()} Credits verified` };
};
context.renderExpansionPlannerPanel = () => {};
await context.startExpansionPlanner();
assert.deepEqual(order, ['101', '102']);
assert.equal(maxActive, 1, 'Purchases must never overlap');
assert.equal(expansionPlannerRuntime.purchased, 2);
assert.equal(expansionPlannerRuntime.creditsSpent, 120000);
assert.equal(expansionPlannerRuntime.lastReport.outcome, 'successful');

console.log('Issue #744 Expansion & Upgrade Planner runtime fixtures passed: native Credit-only parsing, ambiguity rejection, one-operation selection, CSRF preservation, verification and sequential execution are fail-closed.');
