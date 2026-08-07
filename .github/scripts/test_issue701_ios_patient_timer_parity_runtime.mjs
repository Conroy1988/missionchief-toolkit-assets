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
assert.ok(start >= 0 && end > start, 'Issue #701 patient-timer discovery helpers are missing');
const helperSource = source.slice(start, end);
const refreshStart = source.indexOf('    async function refreshMissionProgressFromPage(');
const refreshEnd = source.indexOf('    function installMissionMarkerAddHook()', refreshStart);
assert.ok(refreshStart >= 0 && refreshEnd > refreshStart, 'Issue #701 mission-page refresh helper is missing');
const refreshSource = source.slice(refreshStart, refreshEnd);

const missionEntries = Array.from({ length: 80 }, (_, index) => {
    const missionId = 10_001 + index;
    return `<div id="mission_${missionId}" mission_id="${missionId}" class="missionSideBarEntry"><a href="/missions/${missionId}">Alliance Patient ${index + 1}</a><span class="mission_list_patient_icon"></span><strong>1</strong></div>`;
}).join('');
const mobileHtml = `<!doctype html><html><body><div id="missions-panel-body"><div id="mission_list_alliance">${missionEntries}</div></div></body></html>`;
const document = new JSDOM('<!doctype html><html><body></body></html>', { url: 'https://www.missionchief.co.uk/' }).window.document;
const patientTimers = Array.from({ length: 80 }, (_, index) => ({
    patient_id: 20_001 + index,
    params: {
        id: 20_001 + index,
        mission_id: 10_001 + index,
        missing_text: index < 13 ? 'Patient transport required' : null
    }
}));

const markerIndex = { markers: [] };
const runtime = { destroyed: false };
const sweep = { queue: [], missionsChecked: 0, scannedAt: 0, scanPromise: null, running: false, stopRequested: false, log: [] };
let refreshCalls = 0;
let missionFetchCalls = 0;
const normaliseMissionId = value => /^\d+$/u.test(String(value ?? '')) ? String(value) : null;
const transportRequirementFromSnapshot = snapshot => {
    const text = String(snapshot?.missingText || '').toLowerCase();
    if (!text.includes('transport')) return null;
    if (text.includes('prisoner')) return { type: 'prisoner', count: 1, label: 'Prisoner transport required' };
    return { type: 'patient', count: Number(text.match(/\b(\d{1,2})\b/u)?.[1]) || Number(snapshot?.patientsCount) || 1, label: 'Patient transport required' };
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
    document,
    pageWindow: { patient_timers: patientTimers },
    DOMParser: document.defaultView.DOMParser,
    runtime,
    transportSweepRuntime: sweep,
    missionProgressPageFetchPromise: null,
    missionProgressPageLastFetch: 0,
    missionProgressPageLastSuccessAt: 0,
    missionProgressPageMissionIds: new Set(),
    missionProgressPageMissionRecords: new Map(),
    personalVehicleApiCache: new Map(),
    missionOverlayData: new Map(),
    liveMissionSnapshots: new Map(),
    MISSION_PROGRESS_PAGE_REFRESH_MS: 30_000,
    TRANSPORT_SWEEP_MAX_MOBILE_DISCOVERY_MISSIONS: 80,
    TRANSPORT_SWEEP_MOBILE_DISCOVERY_CONCURRENCY: 4,
    normaliseMissionId,
    currentMissionUserId: () => 'current-user',
    parseMissionTimestamp: () => null,
    normaliseMissionCaption: value => String(value || '').replace(/\s+/g, ' ').trim(),
    normaliseMissingRequirementText: value => String(value || '').replace(/\s+/g, ' ').trim(),
    transportRequirementFromSnapshot,
    missionIdFromMarker: marker => normaliseMissionId(marker?.missionId),
    getMissionMarkerIndex: () => markerIndex,
    missionSnapshotFromMarker: marker => marker?.snapshot || null,
    missionWatchOwnership: (_marker, _missionId, snapshot = {}) => snapshot.ownership || 'personal',
    getMissionCaption: (_marker, missionId) => `Mission ${missionId}`,
    getMissionCreatedAt: () => 0,
    isPersonalMissionLayer: marker => Boolean(marker?.personal),
    runtimeFetch: async requestPath => {
        assert.equal(requestPath, '/', 'The iOS scan must refresh the current mission list once');
        refreshCalls += 1;
        return { ok: true, text: async () => mobileHtml };
    },
    captureMissionMarkerDataFromDocument: () => 0,
    scanInlineMissionMarkerData: () => 0,
    renderTransportSweepPanel: () => {},
    transportSweepLog: message => sweep.log.push(message),
    transportSweepFetchMissionDocument: async () => {
        missionFetchCalls += 1;
        return null;
    }
});
vm.runInContext(`${refreshSource}\n${helperSource}`, context, { filename: 'issue701-ios-patient-timer-parity.js' });

const iosQueue = await context.scanTransportSweepQueue();
const iosMissionIds = Array.from(iosQueue, item => item.missionId);
assert.equal(refreshCalls, 1, 'The empty-registry iOS scan must refresh ownership data exactly once');
assert.equal(iosQueue.length, 13, 'The native iOS patient registry must recover all 13 transport missions');
assert.deepEqual(iosMissionIds, Array.from({ length: 13 }, (_, index) => String(10_001 + index)));
assert.equal(missionFetchCalls, 0, 'Complete native patient state must not depend on desktop-shaped mission HTML');
assert.ok(sweep.log.some(message => message.includes('Read 80 live iOS patient states · 13 transport missions identified')));

context.missionProgressPageLastSuccessAt = 0;
context.missionProgressPageMissionIds = new Set();
context.missionProgressPageMissionRecords = new Map();
markerIndex.markers = Array.from({ length: 80 }, (_, index) => ({
    missionId: String(10_001 + index),
    snapshot: {
        missionId: String(10_001 + index),
        caption: `Alliance Patient ${index + 1}`,
        missingText: index < 13 ? 'Patient transport required' : '',
        patientsCount: 1,
        prisonersCount: 0,
        ownership: 'alliance',
        createdAt: index + 1
    }
}));
const desktopMissionIds = Array.from(context.buildTransportSweepQueue(), item => item.missionId);
assert.deepEqual(iosMissionIds, desktopMissionIds, 'Physical-iPhone and desktop scans must return the same 13 missions');
assert.equal(sweep.scanPromise, null, 'The manual scan lock must always be released');
console.log('Issue #701 iOS native patient-timer parity runtime contract passed');
