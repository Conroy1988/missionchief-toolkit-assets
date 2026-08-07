#!/usr/bin/env node
'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..', '..');
const source = fs.readFileSync(path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js'), 'utf8');
const start = source.indexOf('    function transportSweepFallbackMissionIds(');
const end = source.indexOf('    function transportSweepHudElements()', start);
assert.ok(start >= 0 && end > start, 'Issue #694 iOS discovery helpers are missing');
const helperSource = source.slice(start, end);

const overlays = new Map([
    ['101', { userId: 'alliance-user', caption: 'Alliance Patient A', missingText: 'Patient transport required', patientsCount: 1, prisonersCount: 0, createdAt: 100 }],
    ['102', { userId: 'current-user', caption: 'Personal Patient', missingText: 'Patient transport required', patientsCount: 1, prisonersCount: 0, createdAt: 200 }],
    ['103', { userId: 'alliance-user', caption: 'Alliance Prisoner', missingText: 'Prisoner transport required', patientsCount: 0, prisonersCount: 1, createdAt: 300 }],
    ['104', { userId: 'alliance-user', caption: 'No Transport', missingText: 'Requires 2 fire engines', patientsCount: 1, prisonersCount: 0, createdAt: 400 }],
    ['105', { caption: 'Unknown Owner', missingText: 'Patient transport required', patientsCount: 1, prisonersCount: 0, createdAt: 500 }],
    ['106', { userId: 'alliance-user', caption: 'Stale Alliance Mission', missingText: 'Patient transport required', patientsCount: 1, prisonersCount: 0, createdAt: 600 }],
    ['107', { userId: 'alliance-user', caption: 'Alliance Patient B', missingText: '2 patients require transport', patientsCount: 2, prisonersCount: 0, createdAt: 700 }]
]);
const pageMissionIds = new Set(['101', '102', '103', '104', '105']);
const domEntries = [{ id: 'mission_107', getAttribute: () => null }];
const missionRoot = { querySelectorAll: () => domEntries };
const markerIndex = { markers: [] };
const runtime = {
    queue: [], missionsChecked: 0, scannedAt: 0, scanPromise: null, running: false,
    stopRequested: false, log: []
};
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
    MISSION_PROGRESS_PAGE_REFRESH_MS: 30_000,
    missionProgressPageLastSuccessAt: Date.now(),
    missionProgressPageMissionIds: pageMissionIds,
    missionProgressPageMissionRecords: new Map(),
    missionOverlayData: overlays,
    liveMissionSnapshots: new Map(),
    transportSweepRuntime: runtime,
    document: { querySelectorAll: () => [missionRoot] },
    normaliseMissionId,
    transportSweepMissionIdFromListEntry: entry => normaliseMissionId(String(entry?.id || '').match(/^mission_(\d+)$/u)?.[1]),
    missionIdFromMarker: marker => normaliseMissionId(marker?.missionId),
    getMissionMarkerIndex: () => markerIndex,
    missionSnapshotFromMarker: () => null,
    missionWatchOwnership: (_marker, missionId) => {
        const userId = overlays.get(missionId)?.userId;
        if (userId === 'current-user' || !userId) return 'personal';
        return 'alliance';
    },
    getMissionCaption: (_marker, missionId) => overlays.get(missionId)?.caption || '',
    getMissionCreatedAt: (_marker, missionId) => overlays.get(missionId)?.createdAt || 0,
    normaliseMissingRequirementText: value => String(value || '').trim(),
    isPersonalMissionLayer: () => false,
    transportRequirementFromSnapshot: snapshot => {
        const text = String(snapshot?.missingText || '').toLowerCase();
        if (!text.includes('transport')) return null;
        if (text.includes('prisoner')) return { type: 'prisoner', count: 1, label: 'Prisoner transport required' };
        if (!text.includes('patient')) return null;
        return { type: 'patient', count: Number(snapshot?.patientsCount) || 1, label: 'Patient transport required' };
    },
    renderTransportSweepPanel: () => {},
    transportSweepLog: message => runtime.log.push(message),
    scanInlineMissionMarkerData: () => 0,
    captureTransportSweepMissionListDataFromDocument: () => new Map(),
    hydrateTransportSweepMobileMissions: async () => 0,
    refreshMissionProgressFromPage: async () => {
        refreshCalls += 1;
        pageMissionIds.add('101');
        context.missionProgressPageLastSuccessAt = Date.now();
        return true;
    }
});
vm.runInContext(helperSource, context, { filename: 'issue694-ios-transport-discovery.js' });

const queue = context.buildTransportSweepQueue();
assert.deepEqual(Array.from(queue, item => item.missionId), ['101', '107']);
assert.equal(queue[1].count, 2);
assert.ok(!queue.some(item => item.missionId === '102'), 'Personal fallback missions must be excluded');
assert.ok(!queue.some(item => item.missionId === '103'), 'Prisoner fallback missions must be excluded');
assert.ok(!queue.some(item => item.missionId === '105'), 'Unknown fallback ownership must fail closed');
assert.ok(!queue.some(item => item.missionId === '106'), 'Stale overlays absent from current MissionChief data must be excluded');

pageMissionIds.clear();
domEntries.length = 0;
runtime.queue = [];
runtime.missionsChecked = 0;
(async () => {
    const refreshedQueue = await context.scanTransportSweepQueue();
    assert.equal(refreshCalls, 1, 'A zero-marker iOS scan must refresh current mission payloads once');
    assert.deepEqual(Array.from(refreshedQueue, item => item.missionId), ['101']);
    assert.equal(runtime.scanPromise, null, 'The manual scan lock must always be released');
    console.log('Issue #694 iOS Transport Sweep discovery runtime contract passed');
})().catch(error => {
    console.error(error);
    process.exitCode = 1;
});
