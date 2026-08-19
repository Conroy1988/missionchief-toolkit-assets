#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';
import { JSDOM } from 'jsdom';


const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const source = fs.readFileSync(path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js'), 'utf8');
const start = source.indexOf('    function stationIconText(');
const end = source.indexOf('    function vehicleTargetInfo(', start);
const migrationStart = source.indexOf('    function normaliseStationIconDispatchSelection(');
const migrationEnd = source.indexOf('    function defaultState(', migrationStart);
assert.ok(start >= 0 && end > start, 'Issue #732 Station Icon consistency helpers are missing');
assert.ok(migrationStart >= 0 && migrationEnd > migrationStart, 'Issue #732 saved-scope migration helper is missing');

const shell = new JSDOM(`<!doctype html><html><body>
<section id="panel" class="mcms-open">
  <div data-station-icon-centres></div>
  <select data-setting="station-icon-source"></select>
  <select data-setting="station-icon-replace-mode"><option value="defaults">Defaults</option><option value="inconsistent">Inconsistent</option><option value="all">All</option></select>
  <select data-setting="station-icon-delay"><option value="1500">1.5 seconds</option></select>
  <button data-action="load-station-icons"></button><button data-action="scan-station-icons"></button>
  <button data-action="apply-station-icons"></button><button data-action="stop-station-icons"></button>
  <button data-action="select-all-station-icon-centres"></button><button data-action="clear-station-icon-centres"></button>
  <button data-action="select-all-station-icons"></button><button data-action="clear-station-icons"></button>
  <div data-station-icon-copier></div>
</section>
</body></html>`, { url: 'https://www.missionchief.co.uk/' });

const pageWindow = {
    location: shell.window.location,
    confirm: () => true,
    Image: shell.window.Image,
    URL: shell.window.URL,
};
const stationIconCopierRuntime = {
    running: false,
    preparing: false,
    stopRequested: false,
    catalogPromise: null,
    scanPromise: null,
    dispatches: [],
    typeLabels: {},
    buildings: [],
    catalogAt: 0,
    queue: [],
    summary: null,
    scannedAt: 0,
    scannedScopeKey: '',
    scannedSourceBuildingId: '',
    scannedReplaceMode: '',
    scannedSourceSignature: null,
    selectedBuildingIds: new Set(),
    currentBuildingId: '',
    currentItem: '',
    processed: 0,
    updated: 0,
    unchanged: 0,
    skipped: 0,
    errors: 0,
    sourceImage: null,
    singleBuildingApi: '',
    log: [],
};
const context = vm.createContext({
    console,
    Date,
    Set,
    Map,
    Array,
    Number,
    String,
    Object,
    Promise,
    Error,
    URL,
    Uint8Array,
    Math,
    FormData: shell.window.FormData,
    Blob: shell.window.Blob,
    DOMParser: shell.window.DOMParser,
    document: shell.window.document,
    pageWindow,
    runtime: { destroyed: false },
    SCRIPT: { panelId: 'panel' },
    state: { stationIconCopier: { dispatchIds: ['30', '10', '20'], sourceBuildingId: '1', replaceMode: 'inconsistent', delayMs: 1500 } },
    stationIconCopierRuntime,
    dispatchRecruitmentRuntime: { running: false, catalogPromise: null, scanPromise: null },
    DISPATCH_RECRUITMENT_ALL_CENTRES: 'all',
    STATION_ICON_REPLACE_DEFAULTS: 'defaults',
    STATION_ICON_REPLACE_INCONSISTENT: 'inconsistent',
    STATION_ICON_REPLACE_ALL: 'all',
    STATION_ICON_REPLACE_OPTIONS: Object.freeze(['defaults', 'inconsistent', 'all']),
    STATION_ICON_DELAY_OPTIONS: Object.freeze([1000, 1500, 2000, 3000, 5000]),
    STATION_ICON_SCAN_LIMIT: 2000,
    STATION_ICON_APPLY_LIMIT: 2000,
    STATION_ICON_REQUEST_TIMEOUT_MS: 15000,
    STATION_ICON_MAX_BYTES: 4 * 1024 * 1024,
    STATION_ICON_MAX_DIMENSION: 200,
    STATION_ICON_MIME_TYPES: Object.freeze(['image/png', 'image/jpeg']),
    commandExperienceElement: id => shell.window.document.querySelector(`#${id}`),
    parseDispatchRecruitmentCatalog: () => ({ dispatches: [], typeLabels: {} }),
    renderDispatchRecruitmentPanel: () => {},
    escapeHtml: value => String(value).replaceAll('&', '&amp;').replaceAll('"', '&quot;').replaceAll('<', '&lt;').replaceAll('>', '&gt;'),
    setInnerHtmlIfChanged(element, html) {
        if (!element || element.innerHTML === html) return false;
        element.innerHTML = html;
        return true;
    },
    updateUiSetProperty(element, property, value) {
        if (!element || Object.is(element[property], value)) return false;
        element[property] = value;
        return true;
    },
    showToast: () => {},
    saveState: () => {},
    updateUI: () => {},
    toolkitAnalyticsRecordFeature: () => {},
    runtimeDelay: async () => true,
    runtimeFetch: async () => { throw new Error('runtimeFetch mock was not installed'); },
});
vm.runInContext(source.slice(migrationStart, migrationEnd), context, { filename: 'issue732-station-icon-migration.js' });
vm.runInContext(source.slice(start, end), context, { filename: 'issue732-station-icon-consistency.js' });

assert.deepEqual(Array.from(context.normaliseStationIconDispatchSelection({ dispatchId: '17' })), ['17']);
assert.deepEqual(Array.from(context.normaliseStationIconDispatchSelection({ dispatchId: 'all' })), ['all']);
assert.deepEqual(Array.from(context.normaliseStationIconDispatchSelection({ dispatchIds: ['20', 'bad', '20', 10], dispatchId: '99' })), ['20', '10']);
assert.deepEqual(Array.from(context.normaliseStationIconDispatchSelection({ dispatchIds: [], dispatchId: '99' })), [], 'An explicitly cleared multi-centre scope must remain empty');

const rawBuildings = [
    { id: 1, caption: 'Source Fire', building_type: 0, small_building: false, leitstelle_building_id: 10, custom_icon_url: '/icons/source.png', latitude: 51.1, longitude: -1.1 },
    { id: 2, caption: 'North Default', building_type: 0, small_building: false, leitstelle_building_id: 10, custom_icon_url: null, latitude: 51.2, longitude: -1.2 },
    { id: 3, caption: 'South Match', building_type: 0, small_building: false, leitstelle_building_id: 20, custom_icon_url: '/icons/source.png', latitude: 51.3, longitude: -1.3 },
    { id: 4, caption: 'South Different', building_type: 0, small_building: false, leitstelle_building_id: 20, custom_icon_url: '/icons/different.png', latitude: 51.4, longitude: -1.4 },
    { id: 5, caption: 'West Unverified', building_type: 0, small_building: false, leitstelle_building_id: 30, custom_icon_url: '/icons/unverified.png', latitude: 51.5, longitude: -1.5 },
    { id: 6, caption: 'West Default', building_type: 0, small_building: false, leitstelle_building_id: 30, custom_icon_url: null, latitude: 51.6, longitude: -1.6 },
    { id: 7, caption: 'Outside Scope', building_type: 0, small_building: false, leitstelle_building_id: 40, custom_icon_url: null },
    { id: 8, caption: 'Small Fire', building_type: 0, small_building: true, leitstelle_building_id: 10, custom_icon_url: null },
];
const buildings = rawBuildings.map(context.normaliseStationIconRecord);
const dispatches = [
    { id: '10', name: 'North Dispatch' },
    { id: '20', name: 'South Dispatch' },
    { id: '30', name: 'West Dispatch' },
    { id: '40', name: 'Outside Dispatch' },
];
stationIconCopierRuntime.dispatches = dispatches;
stationIconCopierRuntime.typeLabels = { 0: 'Fire Station' };
stationIconCopierRuntime.buildings = buildings;

assert.equal(context.stationIconScopeKey(['30', '10', '20'], dispatches), '10,20,30', 'Scope freshness must be order independent');
assert.deepEqual(Array.from(context.stationIconResolvedDispatchIds(['20', '10'], dispatches)), ['10', '20']);
assert.deepEqual(new Set(Array.from(context.stationIconSourceChoices(['10', '20']), item => item.id)), new Set(['1', '3', '4']));

const plan = context.buildStationIconCopyQueue(buildings, ['10', '20', '30'], '1', 'inconsistent', dispatches);
assert.equal(plan.summary.exactType, 6, 'Score denominator must include source plus every exact-type station in scope');
assert.equal(plan.auditCandidates.length, 3);
assert.equal(plan.summary.pending, 3);
assert.equal(plan.summary.inconsistent, 2, 'Default icons are immediately inconsistent');

const sourceImage = { width: 25, height: 25, pixelDigest: 'pixels:source', byteDigest: 'bytes:source', mime: 'image/png' };
let auditDownloads = 0;
context.fetchStationIconImage = async url => {
    auditDownloads += 1;
    if (url.endsWith('/different.png')) return { width: 25, height: 25, pixelDigest: 'pixels:different', byteDigest: 'bytes:different', mime: 'image/png' };
    if (url.endsWith('/unverified.png')) throw new Error('host blocked audit');
    throw new Error(`Unexpected audit download: ${url}`);
};
const audited = await context.auditStationIconConsistency(plan, sourceImage);
assert.equal(auditDownloads, 2, 'A target using the exact source URL must reuse the in-memory signature cache');
assert.deepEqual(new Set(Array.from(audited.queue, item => item.buildingId)), new Set(['2', '4', '6']));
assert.equal(audited.summary.consistent, 2);
assert.equal(audited.summary.inconsistent, 3);
assert.equal(audited.summary.unverified, 1);
assert.equal(audited.summary.pending, 0);
assert.equal(context.stationIconConsistencyPercent(audited.summary), 33.3);
assert.deepEqual(
    JSON.parse(JSON.stringify({
        north: audited.summary.consistencyByDispatch['10'],
        south: audited.summary.consistencyByDispatch['20'],
        west: audited.summary.consistencyByDispatch['30'],
    })),
    {
        north: { dispatchId: '10', name: 'North Dispatch', total: 2, consistent: 1, inconsistent: 1, unverified: 0, pending: 0 },
        south: { dispatchId: '20', name: 'South Dispatch', total: 2, consistent: 1, inconsistent: 1, unverified: 0, pending: 0 },
        west: { dispatchId: '30', name: 'West Dispatch', total: 2, consistent: 0, inconsistent: 1, unverified: 1, pending: 0 },
    },
);
assert.equal(audited.auditCandidates.find(item => item.buildingId === '5').consistency, 'unverified');
assert.ok(!audited.queue.some(item => item.buildingId === '5'), 'Unverified custom icons must not enter inconsistency-only repair');

stationIconCopierRuntime.queue = audited.queue;
stationIconCopierRuntime.summary = audited.summary;
stationIconCopierRuntime.scannedAt = Date.now();
stationIconCopierRuntime.scannedScopeKey = '10,20,30';
stationIconCopierRuntime.scannedSourceBuildingId = '1';
stationIconCopierRuntime.scannedReplaceMode = 'inconsistent';
stationIconCopierRuntime.scannedSourceSignature = audited.sourceSignature;
stationIconCopierRuntime.selectedBuildingIds = new Set(audited.queue.map(item => item.buildingId));
context.renderStationIconCopierPanel();
const panelText = shell.window.document.querySelector('[data-station-icon-copier]').textContent;
assert.match(panelText, /33\.3%/u);
assert.match(panelText, /2 of 6 exact-type stations match/u);
assert.match(panelText, /Consistency by Dispatch Centre/u);
assert.match(panelText, /West Unverified/u);
assert.equal(shell.window.document.querySelectorAll('[data-setting="station-icon-centre-option"]:checked').length, 3);
assert.equal(shell.window.document.querySelectorAll('[data-setting="station-icon-target"]').length, 3);
assert.equal(shell.window.document.querySelector('[data-action="apply-station-icons"]').disabled, false);

const different = audited.queue.find(item => item.buildingId === '4');
assert.ok(different.auditSignature, 'A verified differing custom icon must retain its pre-write pixel signature');
context.fetchStationIconBuilding = async () => buildings.find(item => item.id === '4');
context.fetchStationIconImage = async () => ({ width: 25, height: 25, pixelDigest: 'pixels:changed-after-audit', byteDigest: 'changed', mime: 'image/png' });
await assert.rejects(
    context.applyStationIconToStation(different, { replaceMode: 'inconsistent' }, sourceImage),
    error => error?.stationIconSafeSkip === true && error.message.includes('changed after its pixel audit'),
    'A custom icon changed after scan must be protected before any form submission',
);

stationIconCopierRuntime.scannedSourceSignature = sourceImage;
context.fetchStationIconBuilding = async () => buildings[0];
context.fetchStationIconImage = async () => ({ width: 25, height: 25, pixelDigest: 'pixels:new-source', byteDigest: 'new', mime: 'image/png' });
await assert.rejects(
    context.prepareStationIconSource({ sourceBuildingId: '1', dispatchIds: ['10', '20', '30'] }),
    error => error.message.includes('source icon pixels changed'),
    'A changed source icon must invalidate the complete audited plan',
);

const repaired = audited.queue.find(item => item.buildingId === '2');
context.stationIconMoveConsistency(audited.summary, repaired, 'consistent');
assert.equal(context.stationIconConsistencyPercent(audited.summary), 50, 'A successful repair must improve the score without rescanning');
assert.equal(audited.summary.consistencyByDispatch['10'].consistent, 2);
assert.equal(audited.summary.consistencyByDispatch['10'].inconsistent, 0);

context.state.stationIconCopier.sourceBuildingId = '1';
context.stationIconSelectDispatches(false);
assert.deepEqual(Array.from(context.state.stationIconCopier.dispatchIds), []);
assert.equal(context.state.stationIconCopier.sourceBuildingId, '', 'Clearing the source centre must also clear its source station');
context.stationIconSelectDispatches(true);
assert.deepEqual(Array.from(context.state.stationIconCopier.dispatchIds), ['10', '20', '30', '40']);

console.log('Issue #732 Station Icon consistency runtime contract passed: multi-centre audit, URL caching, unverified protection, freshness checks, per-centre scoring and live score updates are proven');
