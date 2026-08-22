#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';
import { JSDOM } from 'jsdom';


const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const source = fs.readFileSync(path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js'), 'utf8');
function extractFunction(name) {
    const marker = `    function ${name}(`;
    const start = source.indexOf(marker);
    assert.ok(start >= 0, `${name} is missing`);
    const brace = source.indexOf('{', start);
    let depth = 0;
    let quote = '';
    let escaped = false;
    for (let index = brace; index < source.length; index += 1) {
        const char = source[index];
        if (quote) {
            if (escaped) escaped = false;
            else if (char === '\\') escaped = true;
            else if (char === quote) quote = '';
            continue;
        }
        if (char === "'" || char === '"' || char === '`') { quote = char; continue; }
        if (char === '{') depth += 1;
        if (char === '}' && --depth === 0) return source.slice(start, index + 1);
    }
    throw new Error(`Unable to extract ${name}`);
}
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
    scannedTypeId: '',
    selectedBuildingIds: new Set(),
    matchingBuildingIds: new Set(),
    selectedTypeIds: new Set(),
    currentBuildingId: '',
    currentItem: '',
    processed: 0,
    updated: 0,
    partial: 0,
    unchanged: 0,
    skipped: 0,
    errors: 0,
    log: [],
};
let saveStateCalls = 0;
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
    state: { dispatchRecruitment: { dispatchId: '77', buildingTypeId: 'all-types', hiringPhase: '3', personnelDesired: '5', delayMs: 1500 } },
    dispatchRecruitmentRuntime,
    allianceCourseRuntime: { running: false, scanPromise: null },
    stationIconCopierRuntime: { running: false, scanPromise: null, catalogPromise: null },
    expansionPlannerRuntime: { running: false, preparing: false, scanPromise: null, catalogPromise: null },
    DISPATCH_RECRUITMENT_ALL_CENTRES: 'all',
    DISPATCH_RECRUITMENT_ALL_TYPES: 'all-types',
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
    updateUI: () => {},
    handleDeviceLayoutSettingChange: () => false,
    saveState: () => { saveStateCalls += 1; },
    toolkitAnalyticsRecordFeature: () => {},
    runtimeDelay: async () => true,
    runtimeFetch: async () => { throw new Error('runtimeFetch mock was not installed'); },
});
vm.runInContext(source.slice(start, end), context, { filename: 'issue706-dispatch-recruitment.js' });
vm.runInContext(extractFunction('captureDispatchRecruitmentPersonnelDraft'), context, { filename: 'issue706-dispatch-recruitment-draft.js' });
vm.runInContext(extractFunction('handleSettingChange'), context, { filename: 'issue706-dispatch-recruitment-settings.js' });

const parsed = html => new shell.window.DOMParser().parseFromString(html, 'text/html');

const catalogHtml = `
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
`;
const catalog = context.parseDispatchRecruitmentCatalog(parsed(catalogHtml));
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
        <tr class="alliance_buildings_table_searchable">
            <td></td><td><a building_type="2" href="/buildings/106">Retired Response Post</a></td><td>1</td><td>Off</td><td>0</td>
            <td><div id="building_personal_count_target_106">0</div><a class="personal_count_target_edit_button" building_id="106" href="/buildings/106/personalCountTarget">Edit</a></td>
            <td><a class="building_leitstelle_set_106 btn-success" href="/buildings/106/leitstelle-set/0">- None -</a><a class="building_leitstelle_set_106" href="/buildings/106/leitstelle-set/77">North Dispatch</a></td>
        </tr>
    </tbody></table>
`;
const matrixDocumentFor = buildingIds => {
    const ids = new Set(buildingIds.map(String));
    const matrix = parsed(tableHtml);
    for (const row of matrix.querySelectorAll('#building_table tr.alliance_buildings_table_searchable')) {
        const match = row.querySelector('a[href*="/buildings/"]')?.getAttribute('href')?.match(/^\/buildings\/(\d+)$/u);
        if (!match || !ids.has(match[1])) row.remove();
    }
    return matrix;
};
const matrixHtmlFor = buildingIds => matrixDocumentFor(buildingIds).documentElement.outerHTML;
const table = parsed(tableHtml);
const scan = context.buildDispatchRecruitmentQueue(table, catalog.typeLabels, '77', catalog.dispatches);
assert.deepEqual(Array.from(scan.queue, item => item.buildingId), ['101', '102']);
assert.deepEqual(Array.from(scan.queue, item => item.dispatchId), ['77', '77']);
assert.deepEqual(Array.from(scan.queue, item => item.dispatchName), ['North Dispatch', 'North Dispatch']);
assert.deepEqual(Array.from(scan.queue, item => item.typeLabel), ['Fire Station', 'Police Station']);
assert.deepEqual(Array.from(scan.queue, item => item.currentPhase), ['2', 'automatic']);
assert.deepEqual(Array.from(scan.queue, item => item.currentDesired), [4, 7]);
assert.equal(scan.summary.eligible, 2);
assert.equal(scan.summary.unassigned, 1);
assert.equal(scan.summary.outsideDispatch, 1);
assert.equal(scan.summary.unavailable, 2);
assert.deepEqual(Array.from(scan.summary.unassignedNames), ['Retired Response Post']);
assert.deepEqual(Array.from(scan.summary.outsideDispatchNames), ['Other Centre Fire']);
assert.deepEqual(Array.from(scan.summary.unavailableNames), ['Unavailable Ambulance', 'Ambiguous Police']);
assert.deepEqual({ ...scan.summary.typeCounts }, { 2: 1, 6: 1 });
assert.deepEqual({ ...scan.summary.dispatchCounts }, { 77: 2 });

const fireOnlyScan = context.buildDispatchRecruitmentQueue(table, catalog.typeLabels, '77', catalog.dispatches, '2');
assert.deepEqual(Array.from(fireOnlyScan.queue, item => item.buildingId), ['101'], 'A specific native building type must admit only exact type matches');
assert.deepEqual({ ...fireOnlyScan.summary.typeCounts }, { 2: 1 });
assert.equal(fireOnlyScan.summary.eligible, 1);
assert.equal(fireOnlyScan.summary.outsideType, 2);
const policeOnlyScan = context.buildDispatchRecruitmentQueue(table, catalog.typeLabels, '77', catalog.dispatches, '6');
assert.deepEqual(Array.from(policeOnlyScan.queue, item => item.buildingId), ['102']);
assert.deepEqual({ ...policeOnlyScan.summary.typeCounts }, { 6: 1 });

const allScan = context.buildDispatchRecruitmentQueue(table, catalog.typeLabels, 'all', catalog.dispatches);
assert.deepEqual(Array.from(allScan.queue, item => item.buildingId), ['101', '102', '104']);
assert.deepEqual(Array.from(allScan.queue, item => item.dispatchId), ['77', '77', '88']);
assert.deepEqual(Array.from(allScan.queue, item => item.dispatchName), ['North Dispatch', 'North Dispatch', 'South Dispatch']);
assert.equal(allScan.summary.eligible, 3);
assert.equal(allScan.summary.unassigned, 1);
assert.equal(allScan.summary.outsideDispatch, 0);
assert.equal(allScan.summary.unavailable, 2);
assert.deepEqual({ ...allScan.summary.dispatchCounts }, { 77: 2, 88: 1 });

const northMatrix = matrixDocumentFor(['101', '102', '103', '105', '106']);
const southMatrix = matrixDocumentFor(['104', '101']);
const mergedAllScan = context.buildDispatchRecruitmentQueue([northMatrix, southMatrix], catalog.typeLabels, 'all', catalog.dispatches);
assert.deepEqual(Array.from(mergedAllScan.queue, item => item.buildingId), ['101', '102', '104']);
assert.deepEqual(Array.from(mergedAllScan.queue, item => item.dispatchId), ['77', '77', '88']);
assert.equal(mergedAllScan.summary.duplicates, 1, 'Cross-matrix station rows must be deduplicated globally');
const conflictingMatrix = matrixDocumentFor(['101']);
conflictingMatrix.querySelector('.building_leitstelle_set_101[href$="/77"]')?.classList.remove('btn-success');
conflictingMatrix.querySelector('.building_leitstelle_set_101[href$="/88"]')?.classList.add('btn-success');
assert.throws(
    () => context.buildDispatchRecruitmentQueue([northMatrix, conflictingMatrix], catalog.typeLabels, 'all', catalog.dispatches),
    /Conflicting native Dispatch Centre or building-type evidence/u,
    'Contradictory centre evidence across matrices must abort rather than choose a row'
);
context.DISPATCH_RECRUITMENT_SCAN_LIMIT = 2;
const limitedAllScan = context.buildDispatchRecruitmentQueue([northMatrix, southMatrix], catalog.typeLabels, 'all', catalog.dispatches);
assert.deepEqual(Array.from(limitedAllScan.queue, item => item.buildingId), ['101', '102']);
assert.equal(limitedAllScan.summary.truncated, 1, 'The station safety limit must apply once to the globally deduplicated queue');
context.DISPATCH_RECRUITMENT_SCAN_LIMIT = 1;
const limitedPoliceScan = context.buildDispatchRecruitmentQueue([northMatrix, southMatrix], catalog.typeLabels, 'all', catalog.dispatches, '6');
assert.deepEqual(Array.from(limitedPoliceScan.queue, item => item.buildingId), ['102'], 'Unselected types must not consume the selected type safety limit');
assert.equal(limitedPoliceScan.summary.truncated, 0);
context.DISPATCH_RECRUITMENT_SCAN_LIMIT = 2000;

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

const unassignedRows = Array.from({ length: 39 }, (_, index) => {
    const id = String(300 + index);
    return `<tr class="alliance_buildings_table_searchable"><td></td><td><a building_type="2" href="/buildings/${id}">Retired ${index + 1}</a></td><td>1</td><td>Off</td><td>0</td><td><div id="building_personal_count_target_${id}">0</div><a class="personal_count_target_edit_button" building_id="${id}" href="/buildings/${id}/personalCountTarget">Edit</a></td><td><a class="building_leitstelle_set_${id} btn-success" href="/buildings/${id}/leitstelle-set/0">- None -</a><a class="building_leitstelle_set_${id}" href="/buildings/${id}/leitstelle-set/77">North Dispatch</a></td></tr>`;
}).join('');
const unassignedTable = parsed(`<table id="building_table"><tbody>${unassignedRows}</tbody></table>`);
for (const scope of ['77', 'all']) {
    const unassignedScan = context.buildDispatchRecruitmentQueue(unassignedTable, catalog.typeLabels, scope, catalog.dispatches);
    assert.equal(unassignedScan.queue.length, 0, `${scope} scope must never place unassigned rows in the mutable queue`);
    assert.equal(unassignedScan.summary.unassigned, 39);
    assert.equal(unassignedScan.summary.outsideDispatch, 0);
    assert.equal(unassignedScan.summary.unavailable, 0);
}

dispatchRecruitmentRuntime.dispatches = catalog.dispatches;
dispatchRecruitmentRuntime.typeLabels = catalog.typeLabels;
dispatchRecruitmentRuntime.queue = scan.queue;
dispatchRecruitmentRuntime.summary = scan.summary;
dispatchRecruitmentRuntime.scannedAt = Date.now();
dispatchRecruitmentRuntime.scannedDispatchId = '77';
dispatchRecruitmentRuntime.scannedTypeId = 'all-types';
dispatchRecruitmentRuntime.selectedBuildingIds = new Set(['101', '102']);
dispatchRecruitmentRuntime.selectedTypeIds = new Set(['2', '6']);
context.state.dispatchRecruitment.personnelDesired = '1000';
const savedBeforeDraft = saveStateCalls;
dispatchRecruitmentRuntime.scanPromise = Promise.resolve([]);
assert.equal(context.captureDispatchRecruitmentPersonnelDraft({ value: '400', matches: selector => selector === '[data-setting="dispatch-recruitment-personnel"]' }), true);
assert.equal(context.state.dispatchRecruitment.personnelDesired, '400', 'Personnel (Desired) draft reverted while a station scan was active');
assert.equal(saveStateCalls, savedBeforeDraft + 1, 'Personnel (Desired) draft was not persisted synchronously during a station scan');
context.handleSettingChange({
    dataset: { setting: 'dispatch-recruitment-personnel' },
    value: '450',
    matches: selector => selector === '[data-setting="dispatch-recruitment-personnel"]',
});
assert.equal(context.state.dispatchRecruitment.personnelDesired, '450', 'The delegated change path blocked a local Personnel (Desired) update during a station scan');
assert.equal(saveStateCalls, savedBeforeDraft + 2, 'The delegated change path did not persist Personnel (Desired) during a station scan');
dispatchRecruitmentRuntime.scanPromise = null;
context.state.dispatchRecruitment.personnelDesired = '5';
shell.window.document.body.innerHTML = `
    <div id="panel">
        <select data-setting="dispatch-recruitment-centre"></select>
        <select data-setting="dispatch-recruitment-building-type"></select>
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
assert.equal(shell.window.document.querySelector('[data-setting="dispatch-recruitment-building-type"] option')?.value, 'all-types');
assert.match(shell.window.document.querySelector('[data-setting="dispatch-recruitment-building-type"] option')?.textContent || '', /ALL BUILDING TYPES/u);
assert.equal(shell.window.document.querySelectorAll('[data-setting="dispatch-recruitment-type"]').length, 2);
assert.equal(shell.window.document.querySelectorAll('[data-setting="dispatch-recruitment-station"]').length, 2);
assert.match(shell.window.document.querySelector('[data-dispatch-recruitment]').textContent, /2 selected \/ 2 visible/u);
assert.match(shell.window.document.querySelector('[data-dispatch-recruitment]').textContent, /Other centres/u);
assert.match(shell.window.document.querySelector('[data-dispatch-recruitment]').textContent, /Other Centre Fire/u);
assert.equal(shell.window.document.querySelector('[data-action="apply-dispatch-recruitment"]').disabled, false);
dispatchRecruitmentRuntime.scanPromise = Promise.resolve([]);
context.renderDispatchRecruitmentPanel();
assert.equal(shell.window.document.querySelector('[data-setting="dispatch-recruitment-centre"]').disabled, true, 'Dispatch scope must stay locked while a station scan is active');
assert.equal(shell.window.document.querySelector('[data-setting="dispatch-recruitment-building-type"]').disabled, true, 'Building-type scope must stay locked while a station scan is active');
assert.equal(shell.window.document.querySelector('[data-setting="dispatch-recruitment-hiring-phase"]').disabled, false, 'Hiring Phase must remain editable during a station scan');
assert.equal(shell.window.document.querySelector('[data-setting="dispatch-recruitment-personnel"]').disabled, false, 'Personnel (Desired) must remain editable during a station scan');
assert.equal(shell.window.document.querySelector('[data-setting="dispatch-recruitment-delay"]').disabled, false, 'Delay must remain editable during a station scan');
assert.equal(shell.window.document.querySelector('[data-action="apply-dispatch-recruitment"]').disabled, true, 'Apply must stay locked while a station scan is active');
dispatchRecruitmentRuntime.scanPromise = null;
context.renderDispatchRecruitmentPanel();
assert.equal(context.setDispatchRecruitmentBuildingTypeScope('6'), true);
assert.equal(context.state.dispatchRecruitment.buildingTypeId, '6');
assert.equal(dispatchRecruitmentRuntime.queue.length, 0, 'Changing building type must invalidate the complete station queue');
assert.equal(dispatchRecruitmentRuntime.scannedAt, 0);
assert.equal(dispatchRecruitmentRuntime.scannedDispatchId, '');
assert.equal(dispatchRecruitmentRuntime.scannedTypeId, '');
assert.equal(shell.window.document.querySelector('[data-action="apply-dispatch-recruitment"]').disabled, true, 'Changing building type must leave Apply disabled until a fresh scan');
assert.equal(context.setDispatchRecruitmentBuildingTypeScope('unknown-native-type'), false);
assert.equal(context.state.dispatchRecruitment.buildingTypeId, '6', 'An unavailable type must not replace the valid scope');
context.state.dispatchRecruitment.buildingTypeId = '999';
dispatchRecruitmentRuntime.catalogAt = 0;
context.runtimeFetch = async input => {
    const url = new URL(String(input));
    if (url.pathname === '/buildings/new') return { ok: true, status: 200, url: url.href, text: async () => catalogHtml };
    throw new Error(`Unexpected catalogue request: ${url.href}`);
};
await context.loadDispatchRecruitmentCatalog({ force: true });
assert.equal(context.state.dispatchRecruitment.buildingTypeId, 'all-types', 'A saved type missing from the fresh native catalogue must fall back to ALL BUILDING TYPES');
context.state.dispatchRecruitment.buildingTypeId = 'all-types';
dispatchRecruitmentRuntime.queue = scan.queue;
dispatchRecruitmentRuntime.summary = scan.summary;
dispatchRecruitmentRuntime.scannedAt = Date.now();
dispatchRecruitmentRuntime.scannedDispatchId = '77';
dispatchRecruitmentRuntime.scannedTypeId = 'all-types';
dispatchRecruitmentRuntime.selectedBuildingIds = new Set(['101', '102']);
dispatchRecruitmentRuntime.selectedTypeIds = new Set(['2', '6']);
dispatchRecruitmentRuntime.selectedTypeIds.delete('6');
context.renderDispatchRecruitmentPanel();
assert.equal(shell.window.document.querySelectorAll('[data-setting="dispatch-recruitment-station"]').length, 1, 'A disabled native type must leave only matching stations visible');
dispatchRecruitmentRuntime.selectedTypeIds.add('6');

context.state.dispatchRecruitment.dispatchId = 'all';
dispatchRecruitmentRuntime.queue = allScan.queue;
dispatchRecruitmentRuntime.summary = allScan.summary;
dispatchRecruitmentRuntime.scannedDispatchId = 'all';
dispatchRecruitmentRuntime.scannedTypeId = 'all-types';
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
dispatchRecruitmentRuntime.scannedTypeId = 'all-types';
dispatchRecruitmentRuntime.selectedBuildingIds = new Set(['101', '102']);
dispatchRecruitmentRuntime.selectedTypeIds = new Set(['2', '6']);

const singleScanRequests = [];
context.state.dispatchRecruitment.dispatchId = '77';
dispatchRecruitmentRuntime.catalogAt = Date.now();
context.runtimeFetch = async input => {
    const url = new URL(String(input));
    singleScanRequests.push(`${url.pathname}${url.search}`);
    if (url.pathname === '/buildings/77/leitstelle-buildings') return { ok: true, status: 200, url: url.href, text: async () => matrixHtmlFor(['101', '102', '103', '105', '106']) };
    throw new Error(`Unexpected single-centre scan request: ${url.href}`);
};
const scannedSingleCentre = await context.scanDispatchRecruitmentStations();
assert.deepEqual(singleScanRequests, ['/buildings/77/leitstelle-buildings']);
assert.deepEqual(Array.from(scannedSingleCentre, item => item.buildingId), ['101', '102']);
assert.equal(dispatchRecruitmentRuntime.scannedDispatchId, '77');
assert.equal(dispatchRecruitmentRuntime.scannedTypeId, 'all-types');
assert.deepEqual(Array.from(dispatchRecruitmentRuntime.selectedBuildingIds), ['101', '102'], 'Stations differing from the configured plan must be selected after scanning');

context.state.dispatchRecruitment.hiringPhase = 'automatic';
context.state.dispatchRecruitment.personnelDesired = '7';
singleScanRequests.length = 0;
const matchingSingleCentre = await context.scanDispatchRecruitmentStations();
assert.deepEqual(singleScanRequests, ['/buildings/77/leitstelle-buildings']);
assert.deepEqual(Array.from(matchingSingleCentre, item => item.buildingId), ['101', '102']);
assert.deepEqual(Array.from(dispatchRecruitmentRuntime.selectedBuildingIds), ['101'], 'A station already matching Hiring Phase and Personnel (Desired) must remain unselected');
context.renderDispatchRecruitmentPanel();
const matchingStation = shell.window.document.querySelector('[data-setting="dispatch-recruitment-station"][value="102"]');
assert.equal(matchingStation?.checked, false, 'The matching station checkbox must render unchecked');
assert.match(matchingStation?.closest('label')?.textContent || '', /MATCHES/u, 'The matching station must be visibly distinguished from a manually excluded mismatch');

context.state.dispatchRecruitment.personnelDesired = '';
singleScanRequests.length = 0;
await context.scanDispatchRecruitmentStations();
assert.deepEqual(singleScanRequests, ['/buildings/77/leitstelle-buildings']);
assert.deepEqual(Array.from(dispatchRecruitmentRuntime.selectedBuildingIds), [], 'An incomplete plan must fail closed with no automatic station selection');
context.state.dispatchRecruitment.hiringPhase = '3';
context.state.dispatchRecruitment.personnelDesired = '5';

const fireTypeScanRequests = [];
context.state.dispatchRecruitment.buildingTypeId = '2';
dispatchRecruitmentRuntime.catalogAt = Date.now();
context.runtimeFetch = async input => {
    const url = new URL(String(input));
    fireTypeScanRequests.push(`${url.pathname}${url.search}`);
    if (url.pathname === '/buildings/77/leitstelle-buildings') return { ok: true, status: 200, url: url.href, text: async () => matrixHtmlFor(['101', '102', '103', '105', '106']) };
    throw new Error(`Unexpected type-scoped scan request: ${url.href}`);
};
const scannedFireStations = await context.scanDispatchRecruitmentStations();
assert.deepEqual(fireTypeScanRequests, ['/buildings/77/leitstelle-buildings']);
assert.deepEqual(Array.from(scannedFireStations, item => item.buildingId), ['101'], 'Fire Station scope must exclude every other native building type');
assert.equal(dispatchRecruitmentRuntime.scannedDispatchId, '77');
assert.equal(dispatchRecruitmentRuntime.scannedTypeId, '2');
assert.deepEqual(Array.from(dispatchRecruitmentRuntime.selectedBuildingIds), ['101']);
assert.deepEqual(Array.from(dispatchRecruitmentRuntime.selectedTypeIds), ['2']);

const allScanRequests = [];
const allScanProgress = [];
context.state.dispatchRecruitment.dispatchId = 'all';
context.state.dispatchRecruitment.buildingTypeId = 'all-types';
dispatchRecruitmentRuntime.catalogAt = Date.now();
context.runtimeFetch = async input => {
    const url = new URL(String(input));
    allScanRequests.push(`${url.pathname}${url.search}`);
    allScanProgress.push(dispatchRecruitmentRuntime.currentItem);
    assert.match(shell.window.document.querySelector('[data-dispatch-recruitment]').textContent, /Current:\s*Scanning/u);
    if (url.pathname === '/buildings/77/leitstelle-buildings') return { ok: true, status: 200, url: url.href, text: async () => matrixHtmlFor(['101', '102', '103', '105', '106']) };
    if (url.pathname === '/buildings/88/leitstelle-buildings') return { ok: true, status: 200, url: url.href, text: async () => matrixHtmlFor(['104', '101']) };
    throw new Error(`Unexpected all-centres scan request: ${url.href}`);
};
const scannedAllCentres = await context.scanDispatchRecruitmentStations();
assert.deepEqual(allScanRequests, ['/buildings/77/leitstelle-buildings', '/buildings/88/leitstelle-buildings'], 'ALL DISPATCH CENTRES must fetch every loaded native centre matrix exactly once');
assert.deepEqual(allScanProgress, ['Scanning 1 of 2 · North Dispatch', 'Scanning 2 of 2 · South Dispatch']);
assert.deepEqual(Array.from(scannedAllCentres, item => item.buildingId), ['101', '102', '104']);
assert.equal(dispatchRecruitmentRuntime.scannedDispatchId, 'all');
assert.equal(dispatchRecruitmentRuntime.scannedTypeId, 'all-types');

const failedScanRequests = [];
dispatchRecruitmentRuntime.queue = scannedAllCentres;
dispatchRecruitmentRuntime.scannedAt = Date.now();
dispatchRecruitmentRuntime.scannedDispatchId = 'all';
dispatchRecruitmentRuntime.scannedTypeId = 'all-types';
context.runtimeFetch = async input => {
    const url = new URL(String(input));
    failedScanRequests.push(`${url.pathname}${url.search}`);
    if (url.pathname === '/buildings/77/leitstelle-buildings') return { ok: true, status: 200, url: url.href, text: async () => matrixHtmlFor(['101', '102']) };
    if (url.pathname === '/buildings/88/leitstelle-buildings') return { ok: false, status: 503, url: url.href, text: async () => '' };
    throw new Error(`Unexpected failed scan request: ${url.href}`);
};
const failedAllCentres = await context.scanDispatchRecruitmentStations();
assert.deepEqual(failedScanRequests, ['/buildings/77/leitstelle-buildings', '/buildings/88/leitstelle-buildings']);
assert.deepEqual(Array.from(failedAllCentres), []);
assert.equal(dispatchRecruitmentRuntime.queue.length, 0, 'A failed centre must discard the entire scan queue');
assert.equal(dispatchRecruitmentRuntime.scannedAt, 0);
assert.equal(dispatchRecruitmentRuntime.scannedDispatchId, '');
assert.equal(shell.window.document.querySelector('[data-action="apply-dispatch-recruitment"]').disabled, true, 'Apply must remain disabled after an incomplete all-centres scan');
assert.match(dispatchRecruitmentRuntime.log[0]?.message || '', /HTTP 503/u);
context.state.dispatchRecruitment.dispatchId = '77';
dispatchRecruitmentRuntime.queue = scan.queue;
dispatchRecruitmentRuntime.summary = scan.summary;
dispatchRecruitmentRuntime.scannedDispatchId = '77';
dispatchRecruitmentRuntime.scannedTypeId = 'all-types';
dispatchRecruitmentRuntime.selectedBuildingIds = new Set(['101', '102']);
dispatchRecruitmentRuntime.selectedTypeIds = new Set(['2', '6']);

const personnelFormHtml = `
    <form class="simple_form building_form" building_id="101" id="building_form_101" action="/buildings/101?personal_count_target_only=1" method="post">
        <input name="utf8" type="hidden" value="✓">
        <input type="hidden" name="_method" value="put">
        <input type="hidden" name="authenticity_token" value="csrf-token">
        <input type="number" step="1" value="2" name="building[personal_count_target]" id="building_personal_count_target">
        <input type="submit" name="commit" value="Save">
    </form>
`;
const personnelFormWithoutQueryOrEmbeddedToken = `
    <form class="simple_form building_form" building_id="101" id="building_form_101" action="/buildings/101" method="post">
        <input name="utf8" type="hidden" value="✓">
        <input type="hidden" name="_method" value="put">
        <input type="number" step="1" value="2" name="building[personal_count_target]" id="building_personal_count_target">
        <input type="submit" name="commit" value="Save">
    </form>
`;
const csrfMeta = shell.window.document.createElement('meta');
csrfMeta.setAttribute('name', 'csrf-token');
csrfMeta.setAttribute('content', 'page-csrf-token');
shell.window.document.head.appendChild(csrfMeta);
const prepared = context.prepareDispatchRecruitmentPersonnelSubmission(parsed(personnelFormHtml), scan.queue[0], 400);
const preparedBody = new URLSearchParams(prepared.body);
assert.equal(prepared.action, 'https://www.missionchief.co.uk/buildings/101?personal_count_target_only=1');
assert.equal(preparedBody.get('_method'), 'put');
assert.equal(preparedBody.get('authenticity_token'), 'csrf-token');
assert.equal(preparedBody.get('building[personal_count_target]'), '400');
assert.equal(preparedBody.get('commit'), 'Save');
assert.equal(prepared.headers['X-CSRF-Token'], 'csrf-token');
assert.equal(prepared.headers['X-Requested-With'], 'XMLHttpRequest');
assert.deepEqual(Array.from(preparedBody.keys()).sort(), ['_method', 'authenticity_token', 'building[personal_count_target]', 'commit', 'utf8'].sort());
assert.equal(Array.from(preparedBody.keys()).some(name => /leitstelle/iu.test(name)), false, 'Personnel payloads must never contain a Dispatch Centre assignment field');

const preparedNativePartial = context.prepareDispatchRecruitmentPersonnelSubmission(parsed(personnelFormWithoutQueryOrEmbeddedToken), scan.queue[0], 400);
const preparedNativePartialBody = new URLSearchParams(preparedNativePartial.body);
assert.equal(preparedNativePartial.action, 'https://www.missionchief.co.uk/buildings/101?personal_count_target_only=1', 'The native personnel-only flag must be restored when the AJAX partial omits it from its form action');
assert.equal(preparedNativePartialBody.get('authenticity_token'), 'page-csrf-token', 'The current page CSRF meta token must protect a native partial that omits an embedded token');
assert.equal(preparedNativePartial.headers['X-CSRF-Token'], 'page-csrf-token');

assert.throws(
    () => context.prepareDispatchRecruitmentPersonnelSubmission(parsed(`${personnelFormHtml}${personnelFormHtml}`), scan.queue[0], 400),
    error => error?.dispatchRecruitmentSafeSkip === true && /ambiguous/u.test(error.message),
    'Multiple matching Personnel (Desired) forms must fail closed'
);

assert.throws(
    () => context.prepareDispatchRecruitmentPersonnelSubmission(parsed(personnelFormHtml.replace('personal_count_target_only=1', 'coins=1')), scan.queue[0], 5),
    error => error?.dispatchRecruitmentSafeSkip === true,
    'An unexpected target form action must safely skip'
);

assert.throws(
    () => context.prepareDispatchRecruitmentPersonnelSubmission(parsed(personnelFormHtml.replace('<input type="number"', '<input type="hidden" name="building[leitstelle_building_id]" value=""><input type="number"')), scan.queue[0], 400),
    error => error?.dispatchRecruitmentFatal === true && error.message.includes('additional building fields'),
    'An unexpected assignment field must trigger a run-level safety stop before submission'
);
assert.throws(
    () => context.dispatchRecruitmentGuardMutation('/buildings/101/leitstelle-set/0'),
    error => error?.dispatchRecruitmentFatal === true && error.message.includes('No request was sent'),
    'Dispatch Recruitment must categorically block the assignment endpoint'
);
assert.throws(
    () => context.dispatchRecruitmentGuardMutation('/buildings/101?personal_count_target_only=1', 'building%5Bleitstelle_building_id%5D='),
    error => error?.dispatchRecruitmentFatal === true,
    'Dispatch Recruitment must categorically block assignment fields in a payload'
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
const personnelVerified = { ...baseline, personal_count_target: 400 };
const verified = { ...personnelVerified, hiring_phase: 3 };
const requests = [];
let apiRecords = [baseline, baseline, personnelVerified, verified];
const response = (url, body = '') => ({ ok: true, status: 200, url, text: async () => body });
context.runtimeFetch = async (input, init = {}) => {
    const url = new URL(String(input));
    requests.push({ method: init.method || 'GET', path: `${url.pathname}${url.search}`, body: init.body || '', headers: init.headers || {} });
    if (url.pathname === '/api/buildings/101') {
        const record = apiRecords.shift();
        return { ...response(url.href), json: async () => record };
    }
    if (url.pathname === '/buildings/101/personalCountTarget') return response(url.href, personnelFormWithoutQueryOrEmbeddedToken);
    if (url.pathname === '/buildings/101/hire') return response(url.href, '<a href="/buildings/101/hire_do/3">Hire for 3 days</a>');
    if (url.pathname === '/buildings/101/hire_do/3') return response(url.href, '<p>Recruitment started</p>');
    if (url.pathname === '/buildings/101' && url.searchParams.get('personal_count_target_only') === '1') return response(url.href, '<p>Saved</p>');
    throw new Error(`Unexpected request: ${url.href}`);
};
const plan = { dispatchId: '77', hiringPhase: '3', personnelDesired: 400, delayMs: 1500 };
const applied = await context.applyDispatchRecruitmentStation(scan.queue[0], plan);
assert.equal(applied.changed, true);
assert.equal(applied.detail, 'Hiring Phase + Personnel (Desired)');
assert.deepEqual(requests.map(item => `${item.method} ${item.path}`), [
    'GET /api/buildings/101',
    'GET /buildings/101/personalCountTarget',
    'POST /buildings/101?personal_count_target_only=1',
    'GET /api/buildings/101',
    'GET /api/buildings/101',
    'GET /buildings/101/hire',
    'GET /buildings/101/hire_do/3',
    'GET /api/buildings/101',
]);
const submitted = new URLSearchParams(requests.find(item => item.method === 'POST').body);
assert.equal(submitted.get('building[personal_count_target]'), '400');
assert.equal(requests.find(item => item.method === 'POST').headers['X-CSRF-Token'], 'page-csrf-token');
assert.equal(requests.find(item => item.method === 'POST').headers['X-Requested-With'], 'XMLHttpRequest');

requests.length = 0;
apiRecords = [baseline];
const allCentresPlan = { dispatchId: 'all', hiringPhase: '0', personnelDesired: 2, delayMs: 1500 };
const allCentresNoChange = await context.applyDispatchRecruitmentStation(scan.queue[0], allCentresPlan);
assert.equal(allCentresNoChange.changed, false, 'ALL DISPATCH CENTRES must bind a station to its own scanned centre during the authoritative recheck');
assert.deepEqual(requests.map(item => `${item.method} ${item.path}`), ['GET /api/buildings/101']);

requests.length = 0;
const activeHiringBaseline = { ...baseline, hiring_phase: 3 };
const activeHiringPersonnelVerified = { ...activeHiringBaseline, personal_count_target: 400 };
apiRecords = [activeHiringBaseline, activeHiringPersonnelVerified, activeHiringPersonnelVerified];
let partialHireLoads = 0;
context.runtimeFetch = async (input, init = {}) => {
    const url = new URL(String(input));
    requests.push({ method: init.method || 'GET', path: `${url.pathname}${url.search}`, body: init.body || '' });
    if (url.pathname === '/api/buildings/101') return { ...response(url.href), json: async () => apiRecords.shift() };
    if (url.pathname === '/buildings/101/personalCountTarget') return response(url.href, personnelFormHtml);
    if (url.pathname === '/buildings/101' && url.searchParams.get('personal_count_target_only') === '1') return response(url.href, '<p>Saved</p>');
    if (url.pathname === '/buildings/101/hire') {
        const body = partialHireLoads++ === 0
            ? '<a href="/buildings/101/hire_do/0">Cancel recruitment phase</a>'
            : '<a href="/buildings/101/hire_do/3">Restore 3 days</a>';
        return response(url.href, body);
    }
    if (url.pathname === '/buildings/101/hire_do/0' || url.pathname === '/buildings/101/hire_do/3') return response(url.href, '<p>Recruitment action accepted</p>');
    throw new Error(`Unexpected partial-update request: ${url.href}`);
};
const partialPlan = { dispatchId: '77', hiringPhase: 'automatic', personnelDesired: 400, delayMs: 1500 };
const partial = await context.applyDispatchRecruitmentStation(scan.queue[0], partialPlan);
assert.equal(partial.changed, true);
assert.equal(partial.partial, true, 'Personnel (Desired) must remain independently applicable when a requested Hiring Phase is unavailable');
assert.equal(partial.record.personal_count_target, 400);
assert.match(partial.detail, /Personnel \(Desired\).*Hiring Phase/u);
assert.deepEqual(requests.map(item => `${item.method} ${item.path}`), [
    'GET /api/buildings/101',
    'GET /buildings/101/personalCountTarget',
    'POST /buildings/101?personal_count_target_only=1',
    'GET /api/buildings/101',
    'GET /buildings/101/hire',
    'GET /buildings/101/hire_do/0',
    'GET /buildings/101/hire',
    'GET /buildings/101/hire_do/3',
    'GET /api/buildings/101',
]);

requests.length = 0;
apiRecords = [baseline, { ...baseline, personal_count_target: 400, leitstelle_building_id: 88 }];
await assert.rejects(
    context.applyDispatchRecruitmentStation(scan.queue[0], { ...plan, hiringPhase: '0' }),
    error => error?.dispatchRecruitmentFatal === true && error.message.includes('Dispatch Centre changed'),
    'Any assignment change reported after Personnel (Desired) must stop the entire bulk run'
);
assert.deepEqual(requests.map(item => `${item.method} ${item.path}`), [
    'GET /api/buildings/101',
    'GET /buildings/101/personalCountTarget',
    'POST /buildings/101?personal_count_target_only=1',
    'GET /api/buildings/101',
]);

requests.length = 0;
apiRecords = [{ ...baseline, leitstelle_building_id: 88 }];
await assert.rejects(
    context.applyDispatchRecruitmentStation(scan.queue[0], plan),
    error => error?.dispatchRecruitmentSafeSkip === true && error.message.includes('no longer assigned'),
    'A station moved to another Dispatch Centre must be skipped before any native mutation'
);
assert.deepEqual(requests.map(item => `${item.method} ${item.path}`), ['GET /api/buildings/101']);

context.state.dispatchRecruitment = { dispatchId: '77', buildingTypeId: 'all-types', hiringPhase: '3', personnelDesired: '400', delayMs: 1500 };
dispatchRecruitmentRuntime.dispatches = catalog.dispatches;
dispatchRecruitmentRuntime.queue = scan.queue.map(item => ({ ...item, outcome: 'ready', outcomeDetail: '' }));
dispatchRecruitmentRuntime.summary = scan.summary;
dispatchRecruitmentRuntime.scannedAt = Date.now();
dispatchRecruitmentRuntime.scannedDispatchId = '77';
dispatchRecruitmentRuntime.scannedTypeId = 'all-types';
dispatchRecruitmentRuntime.selectedBuildingIds = new Set(['101', '102']);
dispatchRecruitmentRuntime.selectedTypeIds = new Set(['2', '6']);
shell.window.document.querySelector('[data-setting="dispatch-recruitment-hiring-phase"]').value = '3';
shell.window.document.querySelector('[data-setting="dispatch-recruitment-personnel"]').value = '400';
let guardedRunCalls = 0;
context.applyDispatchRecruitmentStation = async () => {
    guardedRunCalls += 1;
    throw context.dispatchRecruitmentSafetyStop('forced assignment mismatch');
};
await context.startDispatchRecruitment();
assert.equal(guardedRunCalls, 1, 'A fatal assignment invariant must prevent the next station from starting');
assert.equal(dispatchRecruitmentRuntime.processed, 1);
assert.equal(dispatchRecruitmentRuntime.errors, 1);
assert.equal(dispatchRecruitmentRuntime.running, false);
assert.ok(dispatchRecruitmentRuntime.log.some(entry => /SAFETY STOP/u.test(entry.message)));

console.log('Issues #706/#724/#726/#764 Dispatch Recruitment runtime contract passed: exact mismatch-first selection, explicit native type scope, stale-scan invalidation, complete matrices and mutation immutability are proven');
