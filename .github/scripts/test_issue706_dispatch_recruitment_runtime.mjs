#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';
import { JSDOM } from 'jsdom';


const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const source = fs.readFileSync(path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js'), 'utf8');
const start = source.indexOf('    const DISPATCH_RECRUITMENT_PHASE_META');
const end = source.indexOf('    function vehicleTargetInfo(', start);
assert.ok(start >= 0 && end > start, 'Issue #706 Dispatch Recruitment helpers are missing');

const shell = new JSDOM('<!doctype html><html><body></body></html>', { url: 'https://www.missionchief.co.uk/' });
const pageWindow = {
    location: shell.window.location,
    confirm: () => true,
};
const dispatchRecruitmentRuntime = {
    running: false,
    stopRequested: false,
    catalogPromise: null,
    scanPromise: null,
    dispatches: [],
    typeLabels: {},
    catalogAt: 0,
    queue: [],
    summary: null,
    scannedAt: 0,
    scannedDispatchId: '',
    selectedBuildingIds: new Set(),
    selectedTypeIds: new Set(),
    currentBuildingId: '',
    currentItem: '',
    processed: 0,
    updated: 0,
    unchanged: 0,
    skipped: 0,
    errors: 0,
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
    URLSearchParams,
    DOMParser: shell.window.DOMParser,
    document: shell.window.document,
    pageWindow,
    runtime: { destroyed: false },
    SCRIPT: { panelId: 'panel' },
    commandExperienceElement: id => shell.window.document.querySelector(`#${id}`),
    state: { dispatchRecruitment: { dispatchId: '77', hiringPhase: '3', personnelDesired: '5', delayMs: 1500 } },
    dispatchRecruitmentRuntime,
    DISPATCH_RECRUITMENT_ALL_CENTRES: 'all',
    DISPATCH_RECRUITMENT_HIRING_PHASE_OPTIONS: Object.freeze(['0', '1', '2', '3', 'automatic']),
    DISPATCH_RECRUITMENT_DELAY_OPTIONS: Object.freeze([1000, 1500, 2000, 3000, 5000]),
    DISPATCH_RECRUITMENT_SCAN_LIMIT: 2000,
    DISPATCH_RECRUITMENT_APPLY_LIMIT: 2000,
    DISPATCH_RECRUITMENT_PERSONNEL_MAX: 10000,
    DISPATCH_RECRUITMENT_REQUEST_TIMEOUT_MS: 12000,
    renderDispatchRecruitmentPanel: () => {},
    escapeHtml: value => String(value),
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
vm.runInContext(source.slice(start, end), context, { filename: 'issue706-dispatch-recruitment.js' });

const parsed = html => new shell.window.DOMParser().parseFromString(html, 'text/html');

const catalog = context.parseDispatchRecruitmentCatalog(parsed(`
    <select id="building_leitstelle_building_id" name="building[leitstelle_building_id]">
        <option value="">Please select</option>
        <option value="77">North Dispatch</option>
        <option value="88">South Dispatch</option>
    </select>
    <select id="building_building_type" name="building[building_type]">
        <option value="2">Fire Station</option>
        <option value="6">Police Station</option>
        <option value="22">Ambulance Station</option>
        <option value="future-opaque">Ignored non-native value</option>
    </select>
`));
assert.deepEqual(Array.from(catalog.dispatches, item => [item.id, item.name]), [['77', 'North Dispatch'], ['88', 'South Dispatch']]);
assert.deepEqual({ ...catalog.typeLabels }, { 2: 'Fire Station', 6: 'Police Station', 22: 'Ambulance Station' });

const tableHtml = `
    <table id="building_table"><tbody>
        <tr class="alliance_buildings_table_searchable">
            <td></td><td><a building_type="2" href="/buildings/101">Alpha Fire</a></td><td>5</td><td>2 days</td><td>17</td>
            <td><div id="building_personal_count_target_101">4</div><a class="personal_count_target_edit_button" building_id="101" href="/buildings/101/personalCountTarget">Edit</a></td>
            <td><a class="building_leitstelle_set_101 btn-success" href="/buildings/101/leitstelle-set/77">North Dispatch</a><a class="building_leitstelle_set_101" href="/buildings/101/leitstelle-set/88">South Dispatch</a></td>
        </tr>
        <tr class="alliance_buildings_table_searchable">
            <td></td><td><a building_type="6" href="/buildings/102">Bravo Police</a></td><td>4</td><td>Automatically</td><td>23</td>
            <td><div id="building_personal_count_target_102">7</div><a class="personal_count_target_edit_button" building_id="102" href="/buildings/102/personalCountTarget">Edit</a></td>
            <td><a class="building_leitstelle_set_102 btn-success" href="/buildings/102/leitstelle-set/77">North Dispatch</a></td>
        </tr>
        <tr class="alliance_buildings_table_searchable">
            <td></td><td><a building_type="22" href="/buildings/103">Unavailable Ambulance</a></td><td>2</td><td></td><td>8</td><td>3</td>
            <td><a class="building_leitstelle_set_103 btn-success" href="/buildings/103/leitstelle-set/77">North Dispatch</a></td>
        </tr>
        <tr class="alliance_buildings_table_searchable">
            <td></td><td><a building_type="2" href="/buildings/104">Other Centre Fire</a></td><td>5</td><td>Off</td><td>12</td>
            <td><div id="building_personal_count_target_104">3</div><a class="personal_count_target_edit_button" building_id="104" href="/buildings/104/personalCountTarget">Edit</a></td>
            <td><a class="building_leitstelle_set_104" href="/buildings/104/leitstelle-set/77">North Dispatch</a><a class="building_leitstelle_set_104 btn-success" href="/buildings/104/leitstelle-set/88">South Dispatch</a></td>
        </tr>
        <tr class="alliance_buildings_table_searchable">
            <td></td><td><a building_type="6" href="/buildings/105">Ambiguous Police</a></td><td>4</td><td>1 day</td><td>9</td>
            <td><div id="building_personal_count_target_105">2</div><a class="personal_count_target_edit_button" building_id="105" href="/buildings/105/personalCountTarget">Edit</a></td>
            <td><a class="building_leitstelle_set_105" href="/buildings/105/leitstelle-set/77">North Dispatch</a></td>
        </tr>
    </tbody></table>
`;
const table = parsed(tableHtml);
const scan = context.buildDispatchRecruitmentQueue(table, catalog.typeLabels, '77', catalog.dispatches);
assert.deepEqual(Array.from(scan.queue, item => item.buildingId), ['101', '102']);
assert.deepEqual(Array.from(scan.queue, item => item.dispatchId), ['77', '77']);
assert.deepEqual(Array.from(scan.queue, item => item.dispatchName), ['North Dispatch', 'North Dispatch']);
assert.deepEqual(Array.from(scan.queue, item => item.typeLabel), ['Fire Station', 'Police Station']);
assert.deepEqual(Array.from(scan.queue, item => item.currentPhase), ['2', 'automatic']);
assert.deepEqual(Array.from(scan.queue, item => item.currentDesired), [4, 7]);
assert.equal(scan.summary.eligible, 2);
assert.equal(scan.summary.outsideDispatch, 1);
assert.equal(scan.summary.unavailable, 2);
assert.deepEqual(Array.from(scan.summary.outsideDispatchNames), ['Other Centre Fire']);
assert.deepEqual(Array.from(scan.summary.unavailableNames), ['Unavailable Ambulance', 'Ambiguous Police']);
assert.deepEqual({ ...scan.summary.typeCounts }, { 2: 1, 6: 1 });
assert.deepEqual({ ...scan.summary.dispatchCounts }, { 77: 2 });

const allScan = context.buildDispatchRecruitmentQueue(table, catalog.typeLabels, 'all', catalog.dispatches);
assert.deepEqual(Array.from(allScan.queue, item => item.buildingId), ['101', '102', '104']);
assert.deepEqual(Array.from(allScan.queue, item => item.dispatchId), ['77', '77', '88']);
assert.deepEqual(Array.from(allScan.queue, item => item.dispatchName), ['North Dispatch', 'North Dispatch', 'South Dispatch']);
assert.equal(allScan.summary.eligible, 3);
assert.equal(allScan.summary.outsideDispatch, 0);
assert.equal(allScan.summary.unavailable, 2);
assert.deepEqual({ ...allScan.summary.dispatchCounts }, { 77: 2, 88: 1 });

const foreignRows = Array.from({ length: 39 }, (_, index) => {
    const id = String(200 + index);
    return `<tr class="alliance_buildings_table_searchable"><td></td><td><a building_type="2" href="/buildings/${id}">Foreign ${index + 1}</a></td><td>1</td><td>Off</td><td>1</td><td><div id="building_personal_count_target_${id}">1</div><a class="personal_count_target_edit_button" building_id="${id}" href="/buildings/${id}/personalCountTarget">Edit</a></td><td><a class="building_leitstelle_set_${id} btn-success" href="/buildings/${id}/leitstelle-set/88">South Dispatch</a></td></tr>`;
}).join('');
const foreignTable = parsed(`<table id="building_table"><tbody>${foreignRows}</tbody></table>`);
const foreignScan = context.buildDispatchRecruitmentQueue(foreignTable, catalog.typeLabels, '77', catalog.dispatches);
assert.equal(foreignScan.queue.length, 0, 'Rows assigned to another Dispatch Centre must never enter the mutable queue');
assert.equal(foreignScan.summary.eligible, 0);
assert.equal(foreignScan.summary.outsideDispatch, 39);
assert.equal(foreignScan.summary.unavailable, 0);
const allForeignScan = context.buildDispatchRecruitmentQueue(foreignTable, catalog.typeLabels, 'all', catalog.dispatches);
assert.equal(allForeignScan.queue.length, 39, 'ALL DISPATCH CENTRES must admit every exact assignment from the loaded catalogue');
assert.equal(allForeignScan.summary.eligible, 39);
assert.equal(allForeignScan.summary.outsideDispatch, 0);
assert.deepEqual({ ...allForeignScan.summary.dispatchCounts }, { 88: 39 });

dispatchRecruitmentRuntime.dispatches = catalog.dispatches;
dispatchRecruitmentRuntime.typeLabels = catalog.typeLabels;
dispatchRecruitmentRuntime.queue = scan.queue;
dispatchRecruitmentRuntime.summary = scan.summary;
dispatchRecruitmentRuntime.scannedAt = Date.now();
dispatchRecruitmentRuntime.scannedDispatchId = '77';
dispatchRecruitmentRuntime.selectedBuildingIds = new Set(['101', '102']);
dispatchRecruitmentRuntime.selectedTypeIds = new Set(['2', '6']);
shell.window.document.body.innerHTML = `
    <div id="panel">
        <select data-setting="dispatch-recruitment-centre"></select>
        <select data-setting="dispatch-recruitment-hiring-phase"><option value="3">3 days</option></select>
        <input data-setting="dispatch-recruitment-personnel" value="5">
        <select data-setting="dispatch-recruitment-delay"><option value="1500">1.5 seconds</option></select>
        <button data-action="load-dispatch-recruitment"></button>
        <button data-action="scan-dispatch-recruitment"></button>
        <button data-action="apply-dispatch-recruitment"></button>
        <button data-action="stop-dispatch-recruitment"></button>
        <button data-action="select-all-dispatch-recruitment"></button>
        <button data-action="clear-dispatch-recruitment"></button>
        <div data-dispatch-recruitment></div>
    </div>
`;
context.renderDispatchRecruitmentPanel();
assert.equal(shell.window.document.querySelector('[data-setting="dispatch-recruitment-centre"] option')?.value, 'all');
assert.match(shell.window.document.querySelector('[data-setting="dispatch-recruitment-centre"] option')?.textContent || '', /ALL DISPATCH CENTRES/u);
assert.equal(shell.window.document.querySelectorAll('[data-setting="dispatch-recruitment-type"]').length, 2);
assert.equal(shell.window.document.querySelectorAll('[data-setting="dispatch-recruitment-station"]').length, 2);
assert.match(shell.window.document.querySelector('[data-dispatch-recruitment]').textContent, /2 selected \/ 2 visible/u);
assert.match(shell.window.document.querySelector('[data-dispatch-recruitment]').textContent, /Other centres/u);
assert.match(shell.window.document.querySelector('[data-dispatch-recruitment]').textContent, /Other Centre Fire/u);
assert.equal(shell.window.document.querySelector('[data-action="apply-dispatch-recruitment"]').disabled, false);
dispatchRecruitmentRuntime.selectedTypeIds.delete('6');
context.renderDispatchRecruitmentPanel();
assert.equal(shell.window.document.querySelectorAll('[data-setting="dispatch-recruitment-station"]').length, 1, 'A disabled native type must leave only matching stations visible');
dispatchRecruitmentRuntime.selectedTypeIds.add('6');

context.state.dispatchRecruitment.dispatchId = 'all';
dispatchRecruitmentRuntime.queue = allScan.queue;
dispatchRecruitmentRuntime.summary = allScan.summary;
dispatchRecruitmentRuntime.scannedDispatchId = 'all';
dispatchRecruitmentRuntime.selectedBuildingIds = new Set(['101', '102', '104']);
dispatchRecruitmentRuntime.selectedTypeIds = new Set(['2', '6']);
context.renderDispatchRecruitmentPanel();
assert.equal(shell.window.document.querySelectorAll('[data-setting="dispatch-recruitment-station"]').length, 3);
assert.match(shell.window.document.querySelector('[data-dispatch-recruitment]').textContent, /3 selected \/ 3 visible/u);
assert.match(shell.window.document.querySelector('[data-dispatch-recruitment]').textContent, /2Centres/u);
assert.match(shell.window.document.querySelector('[data-dispatch-recruitment]').textContent, /South Dispatch/u);
assert.equal(shell.window.document.querySelector('[data-action="apply-dispatch-recruitment"]').disabled, false);
context.state.dispatchRecruitment.dispatchId = '77';
dispatchRecruitmentRuntime.queue = scan.queue;
dispatchRecruitmentRuntime.summary = scan.summary;
dispatchRecruitmentRuntime.scannedDispatchId = '77';
dispatchRecruitmentRuntime.selectedBuildingIds = new Set(['101', '102']);
dispatchRecruitmentRuntime.selectedTypeIds = new Set(['2', '6']);

const allScanRequests = [];
context.state.dispatchRecruitment.dispatchId = 'all';
dispatchRecruitmentRuntime.catalogAt = Date.now();
context.runtimeFetch = async input => {
    const url = new URL(String(input));
    allScanRequests.push(`${url.pathname}${url.search}`);
    if (url.pathname === '/buildings/77/leitstelle-buildings') return { ok: true, status: 200, url: url.href, text: async () => tableHtml };
    throw new Error(`Unexpected all-centres scan request: ${url.href}`);
};
const scannedAllCentres = await context.scanDispatchRecruitmentStations();
assert.deepEqual(allScanRequests, ['/buildings/77/leitstelle-buildings'], 'ALL DISPATCH CENTRES must reuse the native assignment matrix once rather than refetching it per centre');
assert.deepEqual(Array.from(scannedAllCentres, item => item.buildingId), ['101', '102', '104']);
assert.equal(dispatchRecruitmentRuntime.scannedDispatchId, 'all');
context.state.dispatchRecruitment.dispatchId = '77';
dispatchRecruitmentRuntime.queue = scan.queue;
dispatchRecruitmentRuntime.summary = scan.summary;
dispatchRecruitmentRuntime.scannedDispatchId = '77';
dispatchRecruitmentRuntime.selectedBuildingIds = new Set(['101', '102']);
dispatchRecruitmentRuntime.selectedTypeIds = new Set(['2', '6']);

const personnelFormHtml = `
    <form class="simple_form building_form" building_id="101" id="building_form_101" action="/buildings/101?personal_count_target_only=1" method="post">
        <input name="utf8" type="hidden" value="✓">
        <input type="hidden" name="_method" value="patch">
        <input type="hidden" name="authenticity_token" value="csrf-token">
        <input type="number" step="1" value="2" name="building[personal_count_target]" id="building_personal_count_target">
        <input type="submit" name="commit" value="Save">
    </form>
`;
const prepared = context.prepareDispatchRecruitmentPersonnelSubmission(parsed(personnelFormHtml), scan.queue[0], 5);
const preparedBody = new URLSearchParams(prepared.body);
assert.equal(prepared.action, 'https://www.missionchief.co.uk/buildings/101?personal_count_target_only=1');
assert.equal(preparedBody.get('_method'), 'patch');
assert.equal(preparedBody.get('authenticity_token'), 'csrf-token');
assert.equal(preparedBody.get('building[personal_count_target]'), '5');
assert.equal(preparedBody.get('commit'), 'Save');

assert.throws(
    () => context.prepareDispatchRecruitmentPersonnelSubmission(parsed(personnelFormHtml.replace('personal_count_target_only=1', 'coins=1')), scan.queue[0], 5),
    error => error?.dispatchRecruitmentSafeSkip === true,
    'An unexpected target form action must safely skip'
);

const hiring = parsed(`
    <a href="https://example.invalid/buildings/101/hire_do/3">external</a>
    <a href="/buildings/101/hire_do/coins">coin action</a>
    <a href="/buildings/101/hire_do/3">Hire for 3 days</a>
`);
assert.equal(context.dispatchRecruitmentNativeHireAction(hiring, '101', '3'), 'https://www.missionchief.co.uk/buildings/101/hire_do/3');
assert.equal(context.dispatchRecruitmentNativeHireAction(hiring, '101', 'automatic'), '');
assert.equal(context.dispatchRecruitmentRecordPhase({ hiring_automatic: true, hiring_phase: 0 }), 'automatic');
assert.equal(context.dispatchRecruitmentRecordPhase({ hiring_automatic: false, hiring_phase: 3 }), '3');

const baseline = {
    id: 101,
    leitstelle_building_id: 77,
    building_type: 2,
    personal_count_target: 2,
    hiring_phase: 0,
    hiring_automatic: false,
};
const verified = { ...baseline, personal_count_target: 5, hiring_phase: 3 };
const requests = [];
let apiRecords = [baseline, verified];
const response = (url, body = '') => ({ ok: true, status: 200, url, text: async () => body });
context.runtimeFetch = async (input, init = {}) => {
    const url = new URL(String(input));
    requests.push({ method: init.method || 'GET', path: `${url.pathname}${url.search}`, body: init.body || '' });
    if (url.pathname === '/api/buildings/101') {
        const record = apiRecords.shift();
        return { ...response(url.href), json: async () => record };
    }
    if (url.pathname === '/buildings/101/personalCountTarget') return response(url.href, personnelFormHtml);
    if (url.pathname === '/buildings/101/hire') return response(url.href, '<a href="/buildings/101/hire_do/3">Hire for 3 days</a>');
    if (url.pathname === '/buildings/101/hire_do/3') return response(url.href, '<p>Recruitment started</p>');
    if (url.pathname === '/buildings/101' && url.searchParams.get('personal_count_target_only') === '1') return response(url.href, '<p>Saved</p>');
    throw new Error(`Unexpected request: ${url.href}`);
};
const plan = { dispatchId: '77', hiringPhase: '3', personnelDesired: 5, delayMs: 1500 };
const applied = await context.applyDispatchRecruitmentStation(scan.queue[0], plan);
assert.equal(applied.changed, true);
assert.equal(applied.detail, 'Hiring Phase + Personnel (Desired)');
assert.deepEqual(requests.map(item => `${item.method} ${item.path}`), [
    'GET /api/buildings/101',
    'GET /buildings/101/personalCountTarget',
    'GET /buildings/101/hire',
    'GET /buildings/101/hire_do/3',
    'POST /buildings/101?personal_count_target_only=1',
    'GET /api/buildings/101',
]);
const submitted = new URLSearchParams(requests.find(item => item.method === 'POST').body);
assert.equal(submitted.get('building[personal_count_target]'), '5');

requests.length = 0;
apiRecords = [baseline];
const allCentresPlan = { dispatchId: 'all', hiringPhase: '0', personnelDesired: 2, delayMs: 1500 };
const allCentresNoChange = await context.applyDispatchRecruitmentStation(scan.queue[0], allCentresPlan);
assert.equal(allCentresNoChange.changed, false, 'ALL DISPATCH CENTRES must bind a station to its own scanned centre during the authoritative recheck');
assert.deepEqual(requests.map(item => `${item.method} ${item.path}`), ['GET /api/buildings/101']);

requests.length = 0;
apiRecords = [{ ...baseline, leitstelle_building_id: 88 }];
await assert.rejects(
    context.applyDispatchRecruitmentStation(scan.queue[0], plan),
    error => error?.dispatchRecruitmentSafeSkip === true && error.message.includes('no longer assigned'),
    'A station moved to another Dispatch Centre must be skipped before any native mutation'
);
assert.deepEqual(requests.map(item => `${item.method} ${item.path}`), ['GET /api/buildings/101']);

console.log('Issue #706 Dispatch Recruitment runtime contract passed: one-centre and all-centres scopes, dynamic types, exact native payloads, sequential actions and per-station membership verification are proven');
