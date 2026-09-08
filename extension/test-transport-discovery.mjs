#!/usr/bin/env node
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
const require = createRequire(new URL('../.dev/test-deps/package.json', import.meta.url));
const { JSDOM } = require('jsdom');

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const source = fs.readFileSync(path.join(root, '.dev', 'chromium-extension', 'toolkit.js'), 'utf8');
const start = source.indexOf('    function transportSweepMissionIdFromListEntry(');
const end = source.indexOf('    function transportSweepHudElements()', start);
assert.ok(start >= 0 && end > start, 'Issue #696 mobile discovery helpers are missing');
const helperSource = source.slice(start, end);
const parserStart = source.indexOf('    function collectTransportSweepStaticCandidates(');
const parserEnd = source.indexOf('    async function transportSweepFetchMissionDocument(', parserStart);
const parserSource = source.slice(parserStart, parserEnd);
const refreshStart = source.indexOf('    async function refreshMissionProgressFromPage(');
const refreshEnd = source.indexOf('    function installMissionMarkerAddHook()', refreshStart);
assert.ok(refreshStart >= 0 && refreshEnd > refreshStart, 'Issue #696 mission-page refresh helper is missing');
const refreshSource = source.slice(refreshStart, refreshEnd);

let mobileHtml = `<!doctype html><html><body>
<div id="missions-panel-body">
  <div id="mission_list">
    <div id="mission_102" mission_id="102" class="missionSideBarEntry"><a href="/missions/102">Personal Patient</a><span class="mission_list_patient_icon"></span><strong>1</strong></div>
  </div>
  <div id="mission_list_alliance">
    <div id="mission_101" mission_id="101" class="missionSideBarEntry"><a href="/missions/101">Alliance Patient A</a><span class="mission_list_patient_icon"></span><strong>1</strong></div>
    <div id="mission_103" mission_id="103" class="missionSideBarEntry"><a href="/missions/103">Alliance Prisoner</a><span class="mission_list_patient_icon"></span><strong>1</strong></div>
    <div id="mission_104" mission_id="104" class="missionSideBarEntry"><a href="/missions/104">Alliance No Transport</a><span class="mission_list_patient_icon"></span><strong>1</strong></div>
    <div id="mission_107" mission_id="107" class="missionSideBarEntry"><a href="/missions/107">Alliance Patient B</a><span class="mission_list_patient_icon"></span><strong>2</strong></div>
    <div id="mission_108" mission_id="108" class="missionSideBarEntry"><a href="/missions/108">Alliance Fire</a></div>
  </div>
  <div id="mission_list_other">
    <div id="mission_105" mission_id="105" class="missionSideBarEntry"><a href="/missions/105">Unknown Owner</a><span class="mission_list_patient_icon"></span><strong>1</strong></div>
  </div>
</div>
</body></html>`;
assert.ok(!mobileHtml.includes('missionMarkerAdd'), 'The iOS fixture must not contain desktop marker scripts');
const emptyDocument = new JSDOM('<!doctype html><html><body></body></html>', { url: 'https://www.missionchief.co.uk/' }).window.document;
const missionDocuments = new Map([
    ['101', new JSDOM('<!doctype html><h1 id="missionH1">Alliance Patient A</h1><div class="alert alert-danger"><a class="btn btn-success" href="/vehicles/501">Choose hospital</a></div><table id="mission_vehicle_at_mission"><tr id="vehicle_row_501"><td class="building_list_fms_5">5</td><td><a href="/vehicles/501" vehicle_type_id="5">Alliance Ambulance</a></td></tr></table><div class="mission_patient"></div>').window.document],
    ['103', new JSDOM('<!doctype html><h1 id="missionH1">Alliance Prisoner</h1><div id="missing_text"><div data-requirement-type="prisoners">Prisoner transport required</div></div><div class="mission_prisoner"></div>').window.document],
    ['104', new JSDOM('<!doctype html><h1 id="missionH1">Alliance No Transport</h1><div id="missing_text"><div data-requirement-type="vehicles">Requires 2 fire engines</div></div><div class="mission_patient"></div>').window.document],
    ['107', new JSDOM('<!doctype html><h1 id="missionH1">Alliance Patient B</h1><div class="alert alert-danger"><a class="btn btn-success" href="/vehicles/507">Choose hospital</a><a class="btn btn-success" href="/vehicles/508">Choose hospital</a></div><table id="mission_vehicle_at_mission"><tr id="vehicle_row_507"><td class="building_list_fms_5">5</td><td><a href="/vehicles/507" vehicle_type_id="5">Alliance Ambulance B</a></td></tr><tr id="vehicle_row_508"><td class="building_list_fms_5">5</td><td><a href="/vehicles/508" vehicle_type_id="5">Alliance Ambulance C</a></td></tr></table><div class="mission_patient"></div><div class="mission_patient"></div>').window.document],
    ['108', new JSDOM('<!doctype html><h1 id="missionH1">Alliance Fire</h1><div id="missing_text"><div data-requirement-type="patients">Patient transport required</div></div>').window.document]
]);

const markerIndex = { markers: [] };
const runtime = { destroyed: false };
const sweep = { queue: [], missionsChecked: 0, scannedAt: 0, scanPromise: null, running: false, stopRequested: false, log: [] };
const fetchedMissionIds = [];
let refreshCalls = 0;
const normaliseMissionId = value => /^\d+$/u.test(String(value ?? '')) ? String(value) : null;
const context = vm.createContext({
    console,
    TRANSPORT_SWEEP_MAX_CANDIDATES_PER_MISSION: 100,
    transportSweepOwnVehicleIdSet: () => new Set(['999']),
    transportSweepVehicleIdFromHref: href => String(href).match(/\/vehicles\/(\d+)(?:$|[/?#])/)?.[1] || null,
    Date,
    Set,
    Map,
    Array,
    Number,
    String,
    Object,
    Promise,
    document: emptyDocument,
    DOMParser: emptyDocument.defaultView.DOMParser,
    runtime,
    transportSweepRuntime: sweep,
    missionProgressPageFetchPromise: null,
    missionProgressPageLastFetch: 0,
    missionProgressPageLastSuccessAt: 0,
    missionProgressPageMissionIds: new Set(),
    missionProgressPageMissionRecords: new Map(),
    personalVehicleApiCache: new Map(),
    missionOverlayData: new Map([
        ['106', { userId: 'alliance-user', caption: 'Stale Alliance Patient', missingText: 'Patient transport required', patientsCount: 1 }]
    ]),
    liveMissionSnapshots: new Map(),
    MISSION_PROGRESS_PAGE_REFRESH_MS: 30_000,
    TRANSPORT_SWEEP_MAX_MOBILE_DISCOVERY_MISSIONS: 80,
    TRANSPORT_SWEEP_MOBILE_DISCOVERY_CONCURRENCY: 4,
    normaliseMissionId,
    currentMissionUserId: () => 'current-user',
    parseMissionTimestamp: () => null,
    normaliseMissionCaption: value => String(value || '').replace(/\s+/g, ' ').trim(),
    normaliseMissingRequirementText: value => String(value || '').replace(/\s+/g, ' ').trim(),
    missionIdFromMarker: marker => normaliseMissionId(marker?.missionId),
    getMissionMarkerIndex: () => markerIndex,
    missionSnapshotFromMarker: marker => marker?.snapshot || null,
    missionWatchOwnership: (_marker, _missionId, snapshot = {}) => snapshot.ownership || (snapshot.userId === 'current-user' ? 'personal' : snapshot.userId ? 'alliance' : 'personal'),
    getMissionCaption: (_marker, missionId) => `Mission ${missionId}`,
    getMissionCreatedAt: () => 0,
    isPersonalMissionLayer: marker => Boolean(marker?.personal),
    transportRequirementFromSnapshot: snapshot => {
        const text = String(snapshot?.missingText || '').toLowerCase();
        if (!text.includes('transport')) return null;
        if (text.includes('prisoner')) return { type: 'prisoner', count: 1, label: 'Prisoner transport required' };
        if (!text.includes('patient')) return null;
        const count = Number(text.match(/\b(\d{1,2})\b/u)?.[1]) || Number(snapshot?.patientsCount) || 1;
        return { type: 'patient', count, label: 'Patient transport required' };
    },
    runtimeFetch: async requestPath => {
        assert.equal(requestPath, '/', 'The manual mobile refresh must use the current MissionChief page');
        refreshCalls += 1;
        return { ok: true, text: async () => mobileHtml };
    },
    captureMissionMarkerDataFromDocument: () => 0,
    scanInlineMissionMarkerData: () => 0,
    renderTransportSweepPanel: () => {},
    transportSweepLog: message => sweep.log.push(message),
    transportSweepFetchMissionDocument: async missionId => {
        fetchedMissionIds.push(String(missionId));
        const doc = missionDocuments.get(String(missionId));
        return doc ? { doc, htmlLength: doc.documentElement.outerHTML.length } : null;
    }
});
vm.runInContext(`${refreshSource}\n${parserSource}\n${helperSource}`, context, { filename: 'issue696-ios-transport-parity.js' });


// Reproduce the desktop extension case: known blank/non-transport sidebar values,
// an existing marker cache and stale positive/negative marker snapshots.
mobileHtml = mobileHtml.replace('Alliance Patient A</a>', 'Alliance Patient A</a><span class="missing_text"></span>')
    .replace('Alliance Patient B</a>', 'Alliance Patient B</a><span class="missing_text">Requires 2 fire engines</span>');
markerIndex.markers = [
    {missionId: '101', snapshot: {missingText: '', patientsCount: 1, ownership: 'alliance'}},
    {missionId: '104', snapshot: {missingText: 'Patient transport required', patientsCount: 1, ownership: 'alliance'}},
    {missionId: '107', snapshot: {missingText: 'Requires 2 fire engines', patientsCount: 2, ownership: 'alliance'}},
    {missionId: '102', personal: true, snapshot: {missingText: 'Patient transport required', patientsCount: 1, ownership: 'personal'}}
];
context.missionOverlayData.set('101', {missingText: '', missingTextKnown: true, patientsCount: 1, userId: 'alliance-user'});
// Transport rows need not have duplicate green Choose hospital links.
for (const id of ['101', '107']) missionDocuments.get(id).querySelector('.alert')?.remove();
const queue = await context.scanTransportSweepQueue();
assert.deepEqual(Array.from(queue, x => x.missionId), ['101', '107']);
assert.equal(queue[1].count, 2);
assert(!fetchedMissionIds.includes('102'), 'Personal mission was scanned');
assert(!fetchedMissionIds.includes('105'), 'Unknown-owner mission was scanned');
assert(!queue.some(x => x.missionId === '104'), 'Verified absence lost to stale marker transport');
assert(fetchedMissionIds.includes('101') && fetchedMissionIds.includes('107'), 'Known sidebar text suppressed mission-page verification');
assert.equal(sweep.discovery.failed, 0);

// Repeated scan rechecks live pages, rather than preserving the last positive result.
missionDocuments.set('101', missionDocuments.get('104'));
missionDocuments.delete('107');
const second = await context.scanTransportSweepQueue();
assert.equal(second.length, 0);
assert.equal(sweep.discovery.failed, 1);
assert(sweep.log.at(-1).startsWith('Scan incomplete:'), 'Network failure was presented as no transports');
assert.equal(sweep.scanPromise, null);

// A subsequent successful scan recovers without needing a page reload.
missionDocuments.set('107', missionDocuments.get('104'));
await context.scanTransportSweepQueue();
assert.equal(sweep.discovery.failed, 0);
assert.equal(sweep.log.at(-1), 'Scan complete: no active alliance patient transports found');

context.TRANSPORT_SWEEP_MAX_MOBILE_DISCOVERY_MISSIONS = 1;
await context.scanTransportSweepQueue();
assert.equal(sweep.discovery.unchecked, 0);
assert.equal(sweep.discovery.checked, sweep.discovery.candidates, 'A previous cap still leaves missions unchecked');
// All 84 current missions must be checked; the final four used to be omitted.
markerIndex.markers = [];
mobileHtml = '<div id="mission_list_alliance">' + Array.from({length:84}, (_, i) => `<div class="missionSideBarEntry" id="mission_${1000+i}"><a href="/missions/${1000+i}">Patient mission</a><span class="mission_list_patient_icon"></span><strong>1</strong></div>`).join('') + '</div>';
for(let i=0;i<84;i++) missionDocuments.set(String(1000+i),missionDocuments.get('104'));
missionDocuments.set('1083',new JSDOM('<h1 id="missionH1">Last mission</h1><table id="mission_vehicle_at_mission"><tr><td class="building_list_fms_5">5</td><td><a href="/vehicles/800" vehicle_type_id="5">Custom callsign</a></td></tr><tr><td class="building_list_fms_5">5</td><td><a href="/vehicles/999" vehicle_type_id="5">Own ambulance</a></td></tr></table>').window.document);
const tailQueue = await context.scanTransportSweepQueue();
assert.equal(sweep.discovery.checked,84);
assert.equal(sweep.discovery.unchecked,0);
assert.deepEqual(Array.from(tailQueue,x=>x.missionId),['1083']);
assert.equal(tailQueue[0].count,1,'Own vehicle was included');

const fetchStart=source.indexOf('    async function transportSweepFetchMissionDocument(');
const fetchEnd=source.indexOf('    async function transportSweepFetchMissionCandidates(',fetchStart);
const reads=[];
const fetchContext=vm.createContext({URL,DOMParser:emptyDocument.defaultView.DOMParser,runtime:{destroyed:false},transportSweepRuntime:{stopRequested:false},normaliseMissionId,TRANSPORT_SWEEP_MOBILE_REQUEST_TIMEOUT_MS:10000,pageWindow:{location:{origin:'https://www.missionchief.co.uk'}},runtimeFetch:async(url,options)=>{
 reads.push(options);
 return {ok:true,url:'https://www.missionchief.co.uk/missions/1083',text:async()=>reads.length===1?'<html><body><h1 id="missionH1">Mission shell</h1><!-- padding to exceed document size threshold ........................................ --></body></html>':missionDocuments.get('1083').documentElement.outerHTML};
}});
vm.runInContext(source.slice(fetchStart,fetchEnd),fetchContext);
const fetched=await fetchContext.transportSweepFetchMissionDocument('1083');
assert.equal(reads.length,2);
assert.equal(reads[0].headers['X-Requested-With'],'XMLHttpRequest');
assert(fetched.doc.querySelector('.building_list_fms_5'),'A shell page was preferred over vehicle content');
console.log('Transport regressions passed, including all 84 missions, final-mission discovery without green links, own-vehicle exclusion and AJAX/full-page fallback.');
fs.writeFileSync(path.join(root, '.dev/extension-transport-results.json'), JSON.stringify({passed: true, sourceSha256: createHash('sha256').update(source).digest('hex'), coverage: ['blank/unrelated sidebar', 'stale markers', 'request failure and recovery', 'all 84 missions checked', 'eligible mission after previous cutoff', 'status-5 patient vehicle without duplicate green link', 'own-vehicle exclusion', 'AJAX first and full-page fallback'], liveAccountVerification: 'pending user retest'}, null, 2));
