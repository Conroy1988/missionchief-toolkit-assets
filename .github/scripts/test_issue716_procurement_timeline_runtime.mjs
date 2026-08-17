#!/usr/bin/env node
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';


const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..', '..');
const source = fs.readFileSync(path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js'), 'utf8');

function extractFunction(name) {
    const marker = `    function ${name}(`;
    const start = source.indexOf(marker);
    assert.notEqual(start, -1, `${name} is missing`);
    const candidates = [
        source.indexOf('\n    function ', start + marker.length),
        source.indexOf('\n    async function ', start + marker.length),
        source.indexOf('\n    const ', start + marker.length),
    ].filter(index => index >= 0);
    const end = Math.min(...candidates);
    assert.ok(Number.isFinite(end) && end > start, `Unable to extract ${name}`);
    return source.slice(start, end).trim();
}

const now = Date.now();
const timelineEntries = [];
let scheduledSaves = 0;
const context = vm.createContext({
    console,
    Date,
    Set,
    Map,
    Array,
    Number,
    String,
    Object,
    Math,
    JSON,
    OPERATIONAL_TIMELINE_SCHEMA: 1,
    OPERATIONAL_TIMELINE_LIMIT: 1500,
    OPERATIONAL_TIMELINE_RETENTION_MS: 30 * 24 * 60 * 60 * 1000,
    OPERATIONAL_TIMELINE_TYPES: new Set(['mission', 'response', 'requirements', 'casualty', 'stalled', 'recovered', 'completed']),
    OPERATIONAL_TIMELINE_CATEGORIES: new Set(['mission', 'response', 'resource', 'completion']),
    OPERATIONAL_TIMELINE_SEVERITIES: new Set(['info', 'warning', 'critical', 'good']),
    PROCUREMENT_WINDOW_OPTIONS: Object.freeze([1, 7, 30]),
    operationalTimelineEntries: timelineEntries,
    operationalTimelineEventCounter: 0,
    operationalTimelineArmed: false,
    operationalTimelineMissionState: new Map(),
    operationalTimelineAbsentSince: new Map(),
    operationalIntelligenceView: 'timeline',
    operationalTimelineLoggingEnabled: () => true,
    operationalPressureIncludesAllianceMissions: () => false,
    operationalPressureMissionInScope: (snapshot, includeAllianceMissions) => snapshot?.source === 'personal' || Boolean(includeAllianceMissions && snapshot?.source === 'alliance' && snapshot?.qualified),
    resetOperationalTimelineMonitoring: () => {},
    operationalPressureRequirementKey: value => String(value || '').toLowerCase().replace(/[^a-z0-9]+/gu, '-').replace(/^-|-$/gu, ''),
    operationalTimelineSnapshotState: snapshot => snapshot,
    scheduleOperationalTimelineSave: () => { scheduledSaves += 1; },
    operationalPressureBoardOpen: () => false,
    renderOperationalPressureBoard: () => { throw new Error('A closed board must not render during capture'); },
});

const names = [
    'operationalTimelineText',
    'normaliseOperationalTimelineRequirement',
    'normaliseOperationalTimelineEntry',
    'validateOperationalTimelineState',
    'recordOperationalTimelineEvent',
    'operationalTimelineRequirementSummary',
    'updateOperationalTimelineFromSnapshots',
    'calculateProcurementBrainModel',
];
vm.runInContext(`${names.map(extractFunction).join('\n')}
this.__probe = {
    validate: validateOperationalTimelineState,
    record: recordOperationalTimelineEvent,
    update: updateOperationalTimelineFromSnapshots,
    model: calculateProcurementBrainModel,
};`, context, { filename: 'issue716-procurement-timeline-runtime.js' });

let persistenceClock = now;
let persistenceSaves = 0;
const persistenceDelays = [];
let persistenceContext;
persistenceContext = vm.createContext({
    Math,
    Number,
    Promise,
    Date: { now: () => persistenceClock },
    OPERATIONAL_TIMELINE_SAVE_DELAY_MS: 500,
    operationalTimelineSavePending: false,
    operationalTimelineSaveDueAt: 0,
    operationalTimelineSavePromise: null,
    runtime: { destroyed: false },
    runtimeDelay: async delay => {
        persistenceDelays.push(delay);
        persistenceClock += delay;
        return true;
    },
    saveOperationalTimelineState: () => {
        persistenceSaves += 1;
        persistenceContext.operationalTimelineSavePending = false;
        persistenceContext.operationalTimelineSaveDueAt = 0;
    },
});
vm.runInContext(`${extractFunction('scheduleOperationalTimelineSave')}
this.__schedule = scheduleOperationalTimelineSave;`, persistenceContext, { filename: 'issue716-timeline-persistence-runtime.js' });
const firstPersistence = persistenceContext.__schedule(500);
const rescheduledPersistence = persistenceContext.__schedule(900);
assert.strictEqual(rescheduledPersistence, firstPersistence, 'Timeline persistence created more than one pending save');
await firstPersistence;
assert.deepEqual(persistenceDelays, [900], 'Timeline persistence did not debounce to the latest deadline');
assert.equal(persistenceSaves, 1, 'Timeline persistence did not flush exactly once');
assert.equal(persistenceContext.operationalTimelineSavePromise, null, 'Timeline persistence did not release its completed promise');

const event = (overrides = {}) => ({
    id: `event-${Math.random()}`,
    timestamp: now,
    type: 'requirements',
    category: 'resource',
    severity: 'warning',
    missionId: '101',
    caption: 'Warehouse fire',
    source: 'personal',
    summary: 'Missing requirements updated.',
    signature: 'requirements:101:arv',
    details: { requirements: [{ kind: 'vehicle', key: 'armed-response', name: 'Armed Response Vehicle', count: 1 }] },
    ...overrides,
});

assert.deepEqual(Array.from(context.__probe.validate('{not-json', now)), []);
assert.deepEqual(Array.from(context.__probe.validate('x'.repeat(2_000_001), now)), []);
assert.deepEqual(Array.from(context.__probe.validate({ schema: 2, entries: [event()] }, now)), []);
assert.deepEqual(Array.from(context.__probe.validate({ schema: 1, entries: [event({ timestamp: now - 31 * 24 * 60 * 60 * 1000 })] }, now)), []);
const capped = context.__probe.validate({ schema: 1, entries: Array.from({ length: 1505 }, (_, index) => event({ id: `cap-${index}`, signature: `cap-${index}` })) }, now);
assert.equal(capped.length, 1500, 'Timeline state was not capped to 1,500 entries');
assert.equal(context.__probe.validate({ schema: 1, entries: [event({ missionId: '<script>' })] }, now).length, 0, 'Unsafe mission ID survived normalisation');

const snapshot = (missionId, overrides = {}) => ({
    missionId,
    caption: `Mission ${missionId}`,
    source: 'personal',
    requirements: [],
    requirementSignature: '',
    units: { total: 0, onScene: 0, travelling: 0 },
    patients: 0,
    prisoners: 0,
    stuck: false,
    lastSeen: now,
    ...overrides,
});

context.operationalTimelineLoggingEnabled = () => false;
assert.equal(context.__probe.update({ values: () => { throw new Error('logging-off path scanned missions'); } }, now), 0, 'Disabled logging did not return before mission processing');
context.operationalTimelineLoggingEnabled = () => true;

const baseline = new Map([
    ['101', snapshot('101')],
    ['102', snapshot('102')],
    ['alliance-hidden', snapshot('alliance-hidden', { source: 'alliance', qualified: true })],
]);
assert.equal(context.__probe.update(baseline, now), 0, 'First successful scan must be a quiet baseline');
assert.equal(timelineEntries.length, 0);
assert.equal(context.operationalTimelineMissionState.has('alliance-hidden'), false, 'Default logging scope retained an Alliance mission');

const arv = [{ kind: 'vehicle', key: 'armed-response', name: 'Armed Response Vehicle', count: 2 }];
const changed = new Map([
    ['101', snapshot('101', {
        requirements: arv,
        requirementSignature: 'vehicle:armed-response:2',
        units: { total: 2, onScene: 1, travelling: 1 },
        patients: 1,
        stuck: true,
    })],
    ['102', snapshot('102')],
    ['103', snapshot('103', {
        requirements: [{ kind: 'personnel', key: 'firearms-officers', name: 'Firearms Officers', count: 4 }],
        requirementSignature: 'personnel:firearms-officers:4',
    })],
]);
assert.equal(context.__probe.update(changed, now + 100), 6, 'Meaningful changes and a new mission were not fully captured');
assert.deepEqual(new Set(timelineEntries.map(item => item.type)), new Set(['requirements', 'response', 'casualty', 'stalled', 'mission']));
const afterChanges = timelineEntries.length;
assert.equal(context.__probe.update(changed, now + 200), 0, 'Unchanged snapshots generated duplicate events');
assert.equal(timelineEntries.length, afterChanges);

const without102 = new Map([...changed].filter(([missionId]) => missionId !== '102'));
assert.equal(context.__probe.update(without102, now + 300), 0, 'One missing scan must not imply mission completion');
assert.equal(context.__probe.update(without102, now + 1500), 1, 'Confirmed mission disappearance was not recorded');
assert.equal(timelineEntries[0].type, 'completed');
assert.equal(timelineEntries[0].missionId, '102');

const unique = event({ id: 'dedupe-one', missionId: '999', signature: 'dedupe:999', timestamp: now + 50 });
assert.ok(context.__probe.record(unique));
assert.equal(context.__probe.record({ ...unique, id: 'dedupe-two' }), null, 'Identical 30-second signal was not deduplicated');
assert.ok(scheduledSaves > 0, 'Timeline mutations did not schedule bounded persistence');

const history = [
    event({ missionId: 'a', timestamp: now - 60_000, signature: 'arv:a', details: { requirements: [{ kind: 'vehicle', key: 'armed-response', name: 'Armed Response Vehicle', count: 1 }] } }),
    event({ missionId: 'b', timestamp: now - 120_000, signature: 'dsu:b', details: { requirements: [{ kind: 'vehicle', key: 'dog-support-unit', name: 'Dog Support Unit', count: 1 }] } }),
    event({ missionId: 'c', timestamp: now - 180_000, signature: 'dsu:c', details: { requirements: [{ kind: 'vehicle', key: 'dog-support-unit', name: 'Dog Support Unit', count: 1 }] } }),
    event({ missionId: 'd', timestamp: now - 240_000, signature: 'staff:d', details: { requirements: [{ kind: 'personnel', key: 'firearms-officers', name: 'Firearms Officers', count: 2 }] } }),
    event({ missionId: 'e', timestamp: now - 300_000, signature: 'staff:e', details: { requirements: [{ kind: 'personnel', key: 'firearms-officers', name: 'Firearms Officers', count: 2 }] } }),
    event({ missionId: 'weak', timestamp: now - 360_000, signature: 'weak', details: { requirements: [{ kind: 'vehicle', key: 'hazmat-pod', name: 'HazMat Pod', count: 1 }] } }),
    event({ missionId: 'old', timestamp: now - 8 * 24 * 60 * 60 * 1000, signature: 'old', details: { requirements: [{ kind: 'vehicle', key: 'old-unit', name: 'Old Unit', count: 10 }] } }),
];
const pressure = {
    resourcePressure: {
        groups: [{
            key: 'armed-response',
            name: 'Armed Response Vehicle',
            demand: 2,
            shortfall: 1,
            unverified: 0,
            reserve: -1,
            conflict: true,
            missionIds: ['live-1', 'live-2'],
        }, {
            key: 'drone',
            name: 'Drone',
            demand: 1,
            shortfall: 0,
            unverified: 2,
            reserve: 2,
            conflict: false,
            missionIds: ['live-3'],
        }],
    },
};
const model = context.__probe.model(history, pressure, { now, windowDays: 7 });
assert.equal(model.windowDays, 7);
assert.equal(model.recommendations[0].key, 'armed-response', 'Live confirmed shortfall must lead the ranking');
assert.equal(model.recommendations[0].priority, 'critical');
assert.equal(model.recommendations[0].confidence, 'high');
assert.ok(model.recommendations.some(item => item.key === 'dog-support-unit'), 'Repeated vehicle demand was not recommended');
assert.ok(model.recommendations.some(item => item.key === 'drone' && item.currentUnverified === 2), 'Current location uncertainty was not surfaced for review');
const personnel = model.recommendations.find(item => item.key === 'firearms-officers');
assert.ok(personnel && /recruitment levels and training coverage/u.test(personnel.action));
assert.equal(model.recommendations.some(item => item.key === 'hazmat-pod'), false, 'One weak isolated signal should remain below recommendation threshold');
assert.equal(model.recommendations.some(item => item.key === 'old-unit'), false, 'Evidence outside the selected window was not expired');
assert.equal(model.recommendations[0].missionIds.length, 3, 'Live pressure mission evidence was not retained');

console.log('Issue #716 runtime contract passed: quiet baseline, meaningful event capture, dedupe/completion guards, bounded validation and deterministic procurement ranking are proven.');
