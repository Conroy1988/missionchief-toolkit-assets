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
assert.ok(start >= 0 && end > start, 'Issue #728 Station Icon Copier helpers are missing');

const shell = new JSDOM(`<!doctype html><html><body>
<section id="panel" class="mcms-open">
  <select data-setting="station-icon-centre"></select>
  <select data-setting="station-icon-source"></select>
  <select data-setting="station-icon-replace-mode"><option value="defaults">Protect</option><option value="all">Replace</option></select>
  <select data-setting="station-icon-delay"><option value="1500">1.5 seconds</option></select>
  <button data-action="load-station-icons"></button><button data-action="scan-station-icons"></button>
  <button data-action="apply-station-icons"></button><button data-action="stop-station-icons"></button>
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
    scannedDispatchId: '',
    scannedSourceBuildingId: '',
    scannedReplaceMode: '',
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
    state: { stationIconCopier: { dispatchId: '10', sourceBuildingId: '1', replaceMode: 'defaults', delayMs: 1500 } },
    stationIconCopierRuntime,
    dispatchRecruitmentRuntime: { running: false, catalogPromise: null, scanPromise: null },
    expansionPlannerRuntime: { running: false, preparing: false, scanPromise: null, catalogPromise: null },
    DISPATCH_RECRUITMENT_ALL_CENTRES: 'all',
    STATION_ICON_REPLACE_DEFAULTS: 'defaults',
    STATION_ICON_REPLACE_ALL: 'all',
    STATION_ICON_REPLACE_OPTIONS: Object.freeze(['defaults', 'all']),
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
    toolkitAnalyticsRecordFeature: () => {},
    runtimeDelay: async () => true,
    runtimeFetch: async () => { throw new Error('runtimeFetch mock was not installed'); },
});
vm.runInContext(source.slice(start, end), context, { filename: 'issue728-station-icon-copier.js' });

const rawBuildings = [
    { id: 1, caption: 'Source Fire', building_type: 0, small_building: false, leitstelle_building_id: 10, custom_icon_url: '/uploads/source.png', latitude: 51.1, longitude: -1.1 },
    { id: 2, caption: 'Default Fire', building_type: 0, small_building: false, leitstelle_building_id: 10, custom_icon_url: null, latitude: 51.2, longitude: -1.2 },
    { id: 3, caption: 'Custom Fire', building_type: 0, small_building: false, leitstelle_building_id: 10, custom_icon_url: '/uploads/custom.png', latitude: 51.3, longitude: -1.3 },
    { id: 4, caption: 'Small Fire', building_type: 0, small_building: true, leitstelle_building_id: 10, custom_icon_url: null },
    { id: 5, caption: 'Police', building_type: 6, small_building: false, leitstelle_building_id: 10, custom_icon_url: null },
    { id: 6, caption: 'Other Centre Fire', building_type: 0, small_building: false, leitstelle_building_id: 20, custom_icon_url: null },
    { id: 7, caption: 'Unassigned Fire', building_type: 0, small_building: false, leitstelle_building_id: null, custom_icon_url: null },
];
const buildings = rawBuildings.map(context.normaliseStationIconRecord);
const dispatches = [{ id: '10', name: 'North Dispatch' }, { id: '20', name: 'South Dispatch' }];
stationIconCopierRuntime.dispatches = dispatches;
stationIconCopierRuntime.typeLabels = { 0: 'Fire Station', 6: 'Police Station' };
stationIconCopierRuntime.buildings = buildings;

const protectedScan = context.buildStationIconCopyQueue(buildings, '10', '1', 'defaults', dispatches);
assert.deepEqual(Array.from(protectedScan.queue, item => item.buildingId), ['2']);
assert.equal(protectedScan.summary.protectedCustom, 1, 'Default mode must protect an existing custom icon');
assert.equal(protectedScan.summary.otherType, 2, 'Small Fire and Police must both be excluded by exact type/size');
assert.equal(protectedScan.summary.outsideDispatch, 1);
assert.equal(protectedScan.summary.unassigned, 1);
assert.equal(protectedScan.summary.sourceExcluded, 1);

const replacementScan = context.buildStationIconCopyQueue(buildings, '10', '1', 'all', dispatches);
assert.deepEqual(Array.from(replacementScan.queue, item => item.buildingId), ['3', '2'].sort((a, b) => buildings.find(item => item.id === a).caption.localeCompare(buildings.find(item => item.id === b).caption)));
assert.deepEqual(new Set(Array.from(replacementScan.queue, item => item.buildingId)), new Set(['2', '3']));

const allCentresScan = context.buildStationIconCopyQueue(buildings, 'all', '1', 'defaults', dispatches);
assert.deepEqual(new Set(Array.from(allCentresScan.queue, item => item.buildingId)), new Set(['2', '6']));
assert.equal(Object.keys(allCentresScan.summary.dispatchCounts).length, 2);

stationIconCopierRuntime.queue = protectedScan.queue;
stationIconCopierRuntime.summary = protectedScan.summary;
stationIconCopierRuntime.scannedAt = Date.now();
stationIconCopierRuntime.scannedDispatchId = '10';
stationIconCopierRuntime.scannedSourceBuildingId = '1';
stationIconCopierRuntime.scannedReplaceMode = 'defaults';
stationIconCopierRuntime.selectedBuildingIds = new Set(['2']);
context.renderStationIconCopierPanel();
assert.match(shell.window.document.querySelector('[data-station-icon-copier]').textContent, /Source Fire/u);
assert.match(shell.window.document.querySelector('[data-station-icon-copier]').textContent, /1 selected \/ 1 visible/u);
assert.equal(shell.window.document.querySelector('[data-action="apply-station-icons"]').disabled, false);
assert.equal(shell.window.document.querySelectorAll('[data-setting="station-icon-target"]').length, 1);

const target = protectedScan.queue[0];
const formDocument = new shell.window.DOMParser().parseFromString(`
<form action="/buildings/2" method="post">
  <input name="authenticity_token" value="csrf-token">
  <input name="_method" value="patch">
  <input name="building[caption]" value="Default Fire">
  <input name="building[building_type]" value="0">
  <input name="building[leitstelle_building_id]" value="10">
  <input name="building[small_building]" value="0">
  <input name="building[latitude]" value="51.2">
  <input name="building[longitude]" value="-1.2">
  <input name="building[personal_count_target]" value="400">
  <input type="file" name="building[image]">
  <button type="submit" name="commit" value="Save">Save</button>
</form>`, 'text/html');
const sourceBlob = new shell.window.Blob(['png-image'], { type: 'image/png' });
const sourceImage = { blob: sourceBlob, mime: 'image/png', width: 25, height: 25, pixelDigest: '25px:same', byteDigest: 'bytes', filename: 'station-icon.png' };
const prepared = context.prepareStationIconSubmission(formDocument, target, sourceImage);
assert.equal(prepared.action, 'https://www.missionchief.co.uk/buildings/2');
assert.equal(prepared.formData.get('authenticity_token'), 'csrf-token');
assert.equal(prepared.formData.get('_method'), 'patch');
assert.equal(prepared.formData.get('building[caption]'), 'Default Fire');
assert.equal(prepared.formData.get('building[personal_count_target]'), '400', 'Unrelated current native fields must be preserved');
assert.equal(prepared.formData.getAll('building[image]').length, 1);

const smallFieldForm = new shell.window.DOMParser().parseFromString('<form><input name="building[small_building]" value="0"><input type="checkbox" name="building[small_building]" value="1" checked></form>', 'text/html').querySelector('form');
assert.doesNotThrow(() => context.stationIconAssertFormValue(smallFieldForm, 'building[small_building]', true, { boolean: true }), 'Rails hidden + checked small-building controls must resolve to the submitted checked value');

assert.throws(
    () => context.prepareStationIconSubmission(
        new shell.window.DOMParser().parseFromString(formDocument.body.innerHTML.replace('</form>', '<input type="file" name="building[plan_image]"></form>'), 'text/html'),
        target,
        sourceImage,
    ),
    error => error?.stationIconFatal === true && error.message.includes('additional file upload'),
    'A second file control must stop before submission',
);

const submittedRequests = [];
context.runtimeFetch = async (input, init = {}) => {
    submittedRequests.push({ url: String(input), init });
    return { ok: true, status: 200, url: 'https://www.missionchief.co.uk/buildings/2' };
};
await context.submitStationIconForm(prepared, target);
assert.equal(submittedRequests.length, 1);
assert.equal(submittedRequests[0].init.method, 'POST');
assert.equal(submittedRequests[0].init.body, prepared.formData);
assert.equal(Object.keys(submittedRequests[0].init.headers).includes('Content-Type'), false, 'The browser must create the multipart boundary');

context.runtimeFetch = async () => ({ ok: true, status: 200, url: 'https://[unreadable' });
await assert.rejects(
    context.submitStationIconForm(prepared, target),
    error => error?.stationIconFatal === true && error.message.includes('unreadable destination'),
    'An unreadable post-submit destination must stop the complete run',
);

const baseline = context.normaliseStationIconRecord(rawBuildings[1]);
const verified = context.normaliseStationIconRecord({ ...rawBuildings[1], custom_icon_url: '/uploads/copied.png' });
let records = [baseline, verified];
let submitted = 0;
context.fetchStationIconBuilding = async () => records.shift();
context.fetchStationIconDocument = async () => ({ doc: formDocument });
context.submitStationIconForm = async () => { submitted += 1; };
context.fetchStationIconImage = async () => ({ ...sourceImage, blob: sourceBlob });
const applied = await context.applyStationIconToStation(target, { replaceMode: 'defaults' }, sourceImage);
assert.equal(applied.changed, true);
assert.equal(submitted, 1);

records = [context.normaliseStationIconRecord(rawBuildings[2])];
context.fetchStationIconBuilding = async () => records.shift();
context.fetchStationIconImage = async () => ({ ...sourceImage, blob: sourceBlob });
await assert.rejects(
    context.applyStationIconToStation({ ...target, buildingId: '3', name: 'Custom Fire', latitude: 51.3, longitude: -1.3, hasCustomIcon: true }, { replaceMode: 'defaults' }, sourceImage),
    error => error?.stationIconSafeSkip === true && error.message.includes('protected'),
);

records = [baseline, context.normaliseStationIconRecord({ ...rawBuildings[1], leitstelle_building_id: 20, custom_icon_url: '/uploads/copied.png' })];
context.fetchStationIconBuilding = async () => records.shift();
context.submitStationIconForm = async () => {};
await assert.rejects(
    context.applyStationIconToStation(target, { replaceMode: 'defaults' }, sourceImage),
    error => error?.stationIconFatal === true && error.message.includes('Dispatch Centre assignment changed'),
    'A post-submit assignment change must stop the complete run',
);

context.state.stationIconCopier = { dispatchId: '10', sourceBuildingId: '1', replaceMode: 'defaults', delayMs: 1500 };
stationIconCopierRuntime.queue = [
    { ...target, outcome: 'ready', outcomeDetail: '' },
    { ...target, buildingId: '8', name: 'Second Fire', outcome: 'ready', outcomeDetail: '' },
];
stationIconCopierRuntime.summary = protectedScan.summary;
stationIconCopierRuntime.scannedAt = Date.now();
stationIconCopierRuntime.scannedDispatchId = '10';
stationIconCopierRuntime.scannedSourceBuildingId = '1';
stationIconCopierRuntime.scannedReplaceMode = 'defaults';
stationIconCopierRuntime.selectedBuildingIds = new Set(['2', '8']);
context.prepareStationIconSource = async () => ({ ...sourceImage, record: buildings[0] });
let runCalls = 0;
context.applyStationIconToStation = async () => {
    runCalls += 1;
    throw context.stationIconSafetyStop('forced verification mismatch');
};
context.renderStationIconCopierPanel = () => {};
await context.startStationIconCopier();
assert.equal(runCalls, 1, 'A fatal verification failure must prevent the next station from starting');
assert.equal(stationIconCopierRuntime.processed, 1);
assert.equal(stationIconCopierRuntime.errors, 1);
assert.equal(stationIconCopierRuntime.running, false);
assert.ok(stationIconCopierRuntime.log.some(entry => /SAFETY STOP/u.test(entry.message)));

console.log('Issue #728 Station Icon Copier runtime contract passed: exact type/size scope, protected defaults, native form preservation, verification and fatal-stop behavior are proven');
