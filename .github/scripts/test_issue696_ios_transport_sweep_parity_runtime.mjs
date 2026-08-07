#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';
import { JSDOM } from 'jsdom';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const source = fs.readFileSync(path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js'), 'utf8');
const start = source.indexOf('    function transportSweepMissionIdFromListEntry(');
const end = source.indexOf('    function transportSweepHudElements()', start);
assert.ok(start >= 0 && end > start, 'Issue #696 mobile discovery helpers are missing');
const helperSource = source.slice(start, end);
const refreshStart = source.indexOf('    async function refreshMissionProgressFromPage(');
const refreshEnd = source.indexOf('    function installMissionMarkerAddHook()', refreshStart);
assert.ok(refreshStart >= 0 && refreshEnd > refreshStart, 'Issue #696 mission-page refresh helper is missing');
const refreshSource = source.slice(refreshStart, refreshEnd);

const mobileHtml = `<!doctype html><html><body>
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
    ['101', new JSDOM('<!doctype html><h1 id="missionH1">Alliance Patient A</h1><div id="missing_text"><div data-requirement-type="patients">Patient transport required</div></div><div class="mission_patient"></div>').window.document],
    ['103', new JSDOM('<!doctype html><h1 id="missionH1">Alliance Prisoner</h1><div id="missing_text"><div data-requirement-type="prisoners">Prisoner transport required</div></div><div class="mission_prisoner"></div>').window.document],
    ['104', new JSDOM('<!doctype html><h1 id="missionH1">Alliance No Transport</h1><div id="missing_text"><div data-requirement-type="vehicles">Requires 2 fire engines</div></div><div class="mission_patient"></div>').window.document],
    ['107', new JSDOM('<!doctype html><h1 id="missionH1">Alliance Patient B</h1><div id="missing_text"><div data-requirement-type="patients">2 patients require transport</div></div><div class="mission_patient"></div><div class="mission_patient"></div>').window.document],
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
vm.runInContext(`${refreshSource}\n${helperSource}`, context, { filename: 'issue696-ios-transport-parity.js' });

const iosQueue = await context.scanTransportSweepQueue();
const iosMissionIds = Array.from(iosQueue, item => item.missionId);
assert.equal(refreshCalls, 1, 'An empty-registry iOS scan must refresh current mission-list HTML once');
assert.deepEqual(iosMissionIds, ['101', '107']);
assert.equal(iosQueue[1].count, 2);
assert.deepEqual(fetchedMissionIds.sort(), ['101', '103', '104', '107'], 'Only current, positively alliance-owned patient candidates may be hydrated');
assert.ok(!fetchedMissionIds.includes('102'), 'Personal missions must never be probed');
assert.ok(!fetchedMissionIds.includes('105'), 'Unknown-owner missions must never be probed');
assert.ok(!fetchedMissionIds.includes('108'), 'Alliance missions without a patient signal must not add requests');
assert.ok(!iosMissionIds.includes('106'), 'Stale overlays absent from current mobile mission data must remain excluded');

context.missionProgressPageLastSuccessAt = 0;
context.missionProgressPageMissionIds = new Set();
context.missionProgressPageMissionRecords = new Map();
markerIndex.markers = [
    { missionId: '101', snapshot: { missionId: '101', caption: 'Alliance Patient A', missingText: 'Patient transport required', patientsCount: 1, ownership: 'alliance', createdAt: 100 } },
    { missionId: '102', personal: true, snapshot: { missionId: '102', caption: 'Personal Patient', missingText: 'Patient transport required', patientsCount: 1, ownership: 'personal', createdAt: 200 } },
    { missionId: '103', snapshot: { missionId: '103', caption: 'Alliance Prisoner', missingText: 'Prisoner transport required', prisonersCount: 1, ownership: 'alliance', createdAt: 300 } },
    { missionId: '104', snapshot: { missionId: '104', caption: 'Alliance No Transport', missingText: 'Requires 2 fire engines', patientsCount: 1, ownership: 'alliance', createdAt: 400 } },
    { missionId: '107', snapshot: { missionId: '107', caption: 'Alliance Patient B', missingText: '2 patients require transport', patientsCount: 2, ownership: 'alliance', createdAt: 700 } }
];
const desktopMissionIds = Array.from(context.buildTransportSweepQueue(), item => item.missionId);
assert.deepEqual(iosMissionIds, desktopMissionIds, 'Desktop and real-mobile discovery must produce the same eligible mission IDs');
assert.equal(sweep.scanPromise, null, 'The manual scan lock must always be released');
console.log('Issue #696 iOS Transport Sweep real-mobile parity runtime contract passed');
