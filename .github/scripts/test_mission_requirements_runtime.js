#!/usr/bin/env node
'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const root = path.resolve(__dirname, '..', '..');
const source = fs.readFileSync(path.join(root, 'src', 'MissionChief_Map_Command_Toolkit.user.js'), 'utf8');
const fixture = JSON.parse(fs.readFileSync(path.join(root, '.github', 'fixtures', 'mission-requirements-contract.json'), 'utf8'));
const startMarker = '    // Issue #133 clean-room live mission requirements matrix.';
const endMarker = '    function criticalMissionValueForEntry(entry) {';
const start = source.indexOf(startMarker);
const end = source.indexOf(endMarker, start);
assert(start >= 0 && end > start, 'unable to extract Issue #133 runtime block');
const block = source.slice(start, end);

const escapeHtml = value => String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');

class FakeClassList {
    constructor() { this.values = new Set(); }
    contains(value) { return this.values.has(value); }
    toggle(value, force) {
        const enabled = force === undefined ? !this.values.has(value) : Boolean(force);
        if (enabled) this.values.add(value);
        else this.values.delete(value);
        return enabled;
    }
}

class FakeElement {
    constructor(tagName = 'div', ownerDocument = null) {
        this.tagName = String(tagName).toUpperCase();
        this.ownerDocument = ownerDocument;
        this.dataset = {};
        this.attributes = new Map();
        this.classList = new FakeClassList();
        this.children = [];
        this.parentNode = null;
        this.isConnected = true;
        this.textContent = '';
        this.innerText = '';
        this.innerHTML = '';
        this.id = '';
        this.value = '';
        this.listeners = new Map();
        this.matchSet = new Set();
        this.queryMap = new Map();
        this.queryAllMap = new Map();
        this.queryHandler = null;
        this.queryAllHandler = null;
        this.closestMap = new Map();
    }
    setAttribute(name, value) {
        this.attributes.set(name, String(value));
        if (name === 'id') this.id = String(value);
    }
    getAttribute(name) {
        if (name === 'data-raw-html' && this._lssmActive) {
            return '<div data-requirement-type="personnel">Missing Personnel</div>';
        }
        if (name === 'id') return this.id || null;
        return this.attributes.has(name) ? this.attributes.get(name) : null;
    }
    matches(selector) { return this.matchSet.has(selector); }
    querySelector(selector) {
        if (this.queryHandler) {
            const value = this.queryHandler(selector);
            if (value !== undefined) return value;
        }
        return this.queryMap.get(selector) || null;
    }
    querySelectorAll(selector) {
        if (this.queryAllHandler) {
            const value = this.queryAllHandler(selector);
            if (value !== undefined) return value;
        }
        return this.queryAllMap.get(selector) || [];
    }
    closest(selector) { return this.closestMap.get(selector) || null; }
    addEventListener(type, listener) {
        const listeners = this.listeners.get(type) || [];
        listeners.push(listener);
        this.listeners.set(type, listeners);
    }
    appendChild(child) {
        child.parentNode = this;
        child.ownerDocument ||= this.ownerDocument;
        child.isConnected = true;
        this.children.push(child);
        child.ownerDocument?.nodes.add(child);
        return child;
    }
    insertBefore(child, reference) {
        child.parentNode = this;
        child.ownerDocument ||= this.ownerDocument;
        child.isConnected = true;
        const index = this.children.indexOf(reference);
        if (index >= 0) this.children.splice(index, 0, child);
        else this.children.push(child);
        child.ownerDocument?.nodes.add(child);
        return child;
    }
    remove() {
        this.isConnected = false;
        if (this.parentNode) this.parentNode.children = this.parentNode.children.filter(child => child !== this);
        this.ownerDocument?.nodes.delete(this);
    }
}

class FakeDocument {
    constructor() {
        this.nodes = new Set();
        this.documentElement = new FakeElement('html', this);
        this.head = new FakeElement('head', this);
        this.body = new FakeElement('body', this);
        this.defaultView = null;
        this.nodes.add(this.documentElement);
        this.nodes.add(this.head);
        this.nodes.add(this.body);
    }
    createElement(tagName) { return new FakeElement(tagName, this); }
    getElementById(id) { return Array.from(this.nodes).find(node => node.isConnected && node.id === id) || null; }
    querySelectorAll(selector) {
        if (selector === 'iframe, frame') return [];
        if (selector.startsWith('#')) {
            const node = this.getElementById(selector.slice(1));
            return node ? [node] : [];
        }
        if (selector === '[data-mcms-requirements-source-hidden="1"]') {
            return Array.from(this.nodes).filter(node => node.isConnected && node.dataset.mcmsRequirementsSourceHidden === '1');
        }
        return [];
    }
}

class FakeMutationObserver {
    static created = 0;
    constructor(callback) {
        this.callback = callback;
        this.connected = false;
        FakeMutationObserver.created += 1;
    }
    observe() { this.connected = true; }
    disconnect() { this.connected = false; }
}

let candidates = [];
let animationQueue = [];
let nextAnimationId = 1;
const trackedObservers = new Set();
const listenedEvents = [];
const flushAnimationFrames = () => {
    while (animationQueue.length) {
        const queue = animationQueue;
        animationQueue = [];
        for (const item of queue) item.callback();
    }
};

const context = {
    console,
    escapeHtml,
    SCRIPT: {
        missionRequirementsPanelId: 'mc-map-command-toolkit-mission-requirements',
        missionRequirementsDocumentStyleId: 'mcms-mission-requirements-document-style'
    },
    state: { missionRequirements: true, uiTheme: 'mapCommand' },
    pageWindow: { MutationObserver: FakeMutationObserver },
    document: {},
    MutationObserver: FakeMutationObserver,
    runtime: { destroyed: false },
    missionRequirementsScanTimer: null,
    missionRequirementsFeatureInstalled: false,
    missionRequirementsObservedDocuments: new WeakSet(),
    missionRequirementsObservedFrames: new WeakSet(),
    missionRequirementsRecords: new Map(),
    runtimeSetTimeout: () => 1,
    runtimeClearTimeout: () => {},
    runtimeRequestAnimationFrame: callback => {
        const id = nextAnimationId++;
        animationQueue.push({ id, callback });
        return id;
    },
    runtimeCancelAnimationFrame: id => { animationQueue = animationQueue.filter(item => item.id !== id); },
    runtimeTrackObserver: observer => { trackedObservers.add(observer); return observer; },
    runtimeUntrackObserver: observer => { observer?.disconnect?.(); trackedObservers.delete(observer); },
    runtimeListen: (target, type, listener, options) => { listenedEvents.push({ target, type, listener, options }); },
    runtimeOnCleanup: () => {},
    transportSweepDocumentContexts: () => Array.from(new Set(candidates.map(candidate => candidate.root?.ownerDocument).filter(Boolean))).map(doc => ({ doc })),
    missionValueWindowCandidates: () => candidates,
    mutationTouchesSelector: () => false,
    setInnerHtmlIfChanged: (element, html) => { if (element.innerHTML !== html) element.innerHTML = html; },
    isVisible: () => true,
};
vm.createContext(context);
vm.runInContext(
    block + `
this.__mcmsRequirements = {
    definitions: MISSION_REQUIREMENT_DEFINITIONS,
    parseText: missionRequirementsParseText,
    capacity: missionRequirementsCapacity,
    capacityText: missionRequirementsCapacityText,
    coverageRow: missionRequirementsCoverageRow,
    staffCapacity: missionRequirementsStaffCapacity,
    equipmentTypes: missionRequirementsEquipmentTypes,
    vehicleId: missionRequirementsVehicleId,
    collectUnits: missionRequirementsCollectUnits,
    aggregate: missionRequirementsAggregate,
    resolve: missionRequirementsResolve,
    overallState: missionRequirementsOverallState,
    lssmActive: missionRequirementsLssmActive,
    panelHtml: missionRequirementsPanelHtml,
    documentCss: missionRequirementsDocumentCss,
    scan: scanMissionRequirementsWindows,
    clear: clearMissionRequirementsPanels,
    observeDocument: observeMissionRequirementsDocument,
    records: missionRequirementsRecords
};`,
    context,
    { filename: 'mission-requirements-runtime.js' }
);
const api = context.__mcmsRequirements;

for (const testCase of fixture.parserCases) {
    const result = api.parseText(testCase.input, testCase.group);
    assert.deepStrictEqual(
        JSON.parse(JSON.stringify(result.requirements.map(item => ({ key: item.key, missing: item.missing })))),
        testCase.expected,
        testCase.name
    );
    assert.strictEqual(result.remaining, testCase.remaining, testCase.name);
}

for (const testCase of fixture.coverageCases) {
    const row = api.coverageRow(
        { key: testCase.name, requirement: testCase.name, missing: testCase.missing, group: 'vehicles', definition: {} },
        testCase.selected,
        testCase.enRoute
    );
    assert.strictEqual(row.covered, testCase.covered, `${testCase.name}: covered`);
    assert.strictEqual(row.definitelyOpen, testCase.definitelyOpen, `${testCase.name}: definitelyOpen`);
    assert.strictEqual(row.uncertain, testCase.uncertain, `${testCase.name}: uncertain`);
    assert.strictEqual(row.stillNeededText, testCase.stillNeededText, `${testCase.name}: still-needed range`);
}

const equipmentRow = {
    dataset: { equipmentTypes: 'drone, hazmat' },
    getAttribute(name) { return name === 'data-equipment-types' ? 'drone, hazmat' : null; },
    querySelectorAll() { return []; }
};
const equipmentCheckbox = {
    dataset: {},
    getAttribute() { return null; },
    querySelectorAll() { return []; },
    closest(selector) { return selector === 'tr' ? equipmentRow : null; }
};
assert.deepStrictEqual(Array.from(api.equipmentTypes(equipmentCheckbox)).sort(), ['drone', 'hazmat'], 'row-owned equipment metadata');

const boundedRow = {
    getAttribute(name) {
        if (name === 'data-min-personnel') return '2';
        if (name === 'data-max-personnel') return '6';
        return null;
    },
    querySelector() { return null; }
};
const boundedCheckbox = {
    getAttribute() { return null; },
    closest(selector) { return selector === 'tr' ? boundedRow : null; }
};
assert.deepStrictEqual(
    JSON.parse(JSON.stringify(api.staffCapacity(boundedCheckbox))),
    { min: 2, max: 6, known: false, value: 2 },
    'bounded personnel capacity'
);

const exactCheckbox = {
    getAttribute(name) { return name === 'data-current-personnel' ? '4' : null; },
    closest() { return null; }
};
assert.deepStrictEqual(
    JSON.parse(JSON.stringify(api.staffCapacity(exactCheckbox))),
    { min: 4, max: 4, known: true, value: 4 },
    'exact personnel capacity'
);

const factorRequirement = { group: 'vehicles', definition: { types: [5], equipment: [], factors: { 5: 2 } } };
const factorUnit = { typeId: 5, equipment: new Set(), staff: null, contributionKey: 'vehicle:1' };
assert.strictEqual(api.aggregate(factorRequirement, [factorUnit]).min, 2, 'capacity factor greater than one');

const pairedRequirement = { group: 'vehicles', definition: { types: [67, 74], equipment: [], factors: {} } };
const pairedUnits = [
    { typeId: 67, equipment: new Set(), staff: null, contributionKey: 'pair:10:11' },
    { typeId: 74, equipment: new Set(), staff: null, contributionKey: 'pair:10:11' },
];
const paired = api.aggregate(pairedRequirement, pairedUnits);
assert.strictEqual(paired.min, 1, 'towing vehicle and trailer must not double-count');
assert.strictEqual(paired.max, 1, 'paired maximum must remain one');

const genericTableSource = {
    matches() { return false; },
    querySelector(selector) { return selector.includes('table.table-striped') ? {} : null; }
};
assert.strictEqual(api.lssmActive({ root: { querySelector() { return null; } } }, genericTableSource), false, 'generic MissionChief table is not LSSM');
const nativeMissingSource = {
    matches(selector) { return selector === '.alert-missing-vehicles'; },
    classList: { contains(value) { return value === 'alert-missing-vehicles'; } },
    getAttribute() { return null; },
    closest() { return null; },
    querySelector() { return null; }
};
assert.strictEqual(
    api.lssmActive({ root: null }, nativeMissingSource),
    false,
    'MissionChief native missing alert must not be classified as LSSM'
);
const lssmSource = {
    matches(selector) { return selector === '.alert-missing-vehicles'; },
    classList: { contains(value) { return value === 'alert-missing-vehicles'; } },
    getAttribute(name) { return name === 'data-raw-html' ? '<div data-requirement-type="personnel">Missing Personnel</div>' : null; },
    closest() { return null; },
    querySelector() { return null; }
};
assert.strictEqual(api.lssmActive({ root: null }, lssmSource), true, 'active LSSM panel is detected by explicit ownership metadata');

const html = api.panelHtml([
    api.coverageRow(
        { key: 'ambulance', requirement: 'Ambulance', missing: 1, group: 'vehicles', definition: {} },
        { min: 1, max: 1, known: true },
        { min: 0, max: 0, known: true }
    )
], []);
for (const header of fixture.layout.requiredHeaders) assert(html.html.includes(header), `missing table header: ${header}`);
assert.strictEqual(html.stateName, 'success', 'covered panel state');

const css = api.documentCss().replace(/\s+/g, '').toLowerCase();
const normalPanelRule = css.split('.mcms-req-head', 1)[0];
for (const forbidden of fixture.layout.forbiddenNormalPanelPositioning) {
    assert(!normalPanelRule.includes(forbidden), `normal-flow panel contains ${forbidden}`);
}
assert(normalPanelRule.includes('position:relative!important'), 'normal-flow panel must be relative');
assert(normalPanelRule.includes('[data-mcms-requirements-source-hidden="1"]{display:none!important}'), 'native source hiding must be CSS-owned');
assert(css.includes('@media(max-width:767px)'), 'mobile breakpoint missing');

function makeVehicleElement(doc, vehicleId, typeId, options = {}) {
    const row = new FakeElement('tr', doc);
    const vehicle = new FakeElement('input', doc);
    vehicle.value = String(vehicleId);
    vehicle.setAttribute('vehicle_type_id', String(typeId));
    if (options.tractiveId !== undefined) vehicle.setAttribute('tractive_vehicle_id', String(options.tractiveId));
    if (options.staff !== undefined) vehicle.setAttribute('data-current-personnel', String(options.staff));
    if (options.equipment) row.setAttribute('data-equipment-types', options.equipment.join(','));
    vehicle.closestMap.set('tr', row);
    row.queryHandler = selector => selector === '[vehicle_type_id]' ? vehicle : null;
    row.queryAllHandler = () => [];
    return { row, vehicle };
}

function makeMissionCandidate(doc, requirementText = '1 Ambulance') {
    const missionRoot = new FakeElement('div', doc);
    const sourceNode = new FakeElement('div', doc);
    sourceNode.id = 'missing_text';
    sourceNode.innerText = requirementText;
    sourceNode.textContent = requirementText;
    sourceNode.queryAllHandler = selector => selector === '[data-requirement-type]' ? [] : [];
    sourceNode.queryHandler = selector => sourceNode._lssmActive && selector.includes('.alert-missing-vehicles') ? new FakeElement('div', doc) : null;
    sourceNode.matches = selector => sourceNode._lssmActive && selector === '.alert-missing-vehicles';
    missionRoot.appendChild(sourceNode);
    missionRoot.selectedUnits = [];
    missionRoot.enRouteRows = [];
    missionRoot.queryHandler = selector => {
        if (selector === '#missing_text') return sourceNode;
        if (selector.includes('.alert-missing-vehicles')) return sourceNode._lssmActive ? sourceNode : null;
        return null;
    };
    missionRoot.queryAllHandler = selector => {
        if (selector.includes('.vehicle_checkbox')) return missionRoot.selectedUnits;
        if (selector === '#mission_vehicle_driving tbody tr') return missionRoot.enRouteRows;
        if (selector === 'iframe, frame') return [];
        return [];
    };
    return { root: missionRoot, mount: missionRoot, source: sourceNode };
}

const unitDoc = new FakeDocument();
unitDoc.defaultView = { MutationObserver: FakeMutationObserver };
const unitCandidate = makeMissionCandidate(unitDoc, '2 Ambulances');
const normalAmbulance = makeVehicleElement(unitDoc, 101, 5);
const occupiedAmbulance = makeVehicleElement(unitDoc, 102, 5);
unitCandidate.root.selectedUnits = [normalAmbulance.vehicle, occupiedAmbulance.vehicle];
const ambulanceDefinition = api.definitions.find(definition => definition.key === 'ambulance');
const ambulanceParsed = {
    requirements: [{ key: 'ambulance', requirement: 'Ambulance', missing: 2, group: 'vehicles', definition: ambulanceDefinition }],
    unresolved: []
};
let resolved = api.resolve(unitCandidate, ambulanceParsed)[0];
assert.strictEqual(resolved.selectedMin, 2, 'normal and occupied selected lists must both count');
assert.strictEqual(resolved.covered, true, 'two selected ambulances cover two missing ambulances');
unitCandidate.root.selectedUnits = [normalAmbulance.vehicle];
resolved = api.resolve(unitCandidate, ambulanceParsed)[0];
assert.strictEqual(resolved.selectedMin, 1, 'checkbox deselection decrements selected capacity');
assert.strictEqual(resolved.definitelyOpen, true, 'deselection reopens the requirement');
const drivingAmbulance = makeVehicleElement(unitDoc, 201, 5);
unitCandidate.root.enRouteRows = [drivingAmbulance.row];
resolved = api.resolve(unitCandidate, ambulanceParsed)[0];
assert.strictEqual(resolved.enRouteMin, 1, 'newly en-route vehicle updates en-route capacity');
assert.strictEqual(resolved.stillNeededText, '1', 'en-route capacity reduces still needed');
assert.strictEqual(resolved.covered, true, 'selected plus en-route capacity covers the requirement');
unitCandidate.root.enRouteRows = [];
resolved = api.resolve(unitCandidate, ambulanceParsed)[0];
assert.strictEqual(resolved.enRouteMin, 0, 'arriving or removed en-route row is reconciled');

const lifecycleDoc = new FakeDocument();
lifecycleDoc.defaultView = { MutationObserver: FakeMutationObserver };
const lifecycleCandidate = makeMissionCandidate(lifecycleDoc);
const duplicateCandidate = { root: lifecycleCandidate.root, mount: lifecycleCandidate.mount, source: lifecycleCandidate.source };
candidates = [lifecycleCandidate, duplicateCandidate];
const observerBaseline = FakeMutationObserver.created;
api.observeDocument(lifecycleDoc);
api.observeDocument(lifecycleDoc);
assert.strictEqual(FakeMutationObserver.created, observerBaseline + 1, 'document observer must be installed once');
api.scan();
flushAnimationFrames();
assert.strictEqual(api.records.size, 1, 'repeated candidates in one document create one record');
assert.strictEqual(lifecycleDoc.querySelectorAll('#mc-map-command-toolkit-mission-requirements').length, 1, 'one requirements panel per document');
assert.strictEqual(lifecycleCandidate.source.dataset.mcmsRequirementsSourceHidden, '1', 'native source is hidden only while Toolkit owns the panel');
const recordObserverCount = FakeMutationObserver.created;
api.scan();
flushAnimationFrames();
assert.strictEqual(api.records.size, 1, 'repeated scans do not duplicate records');
assert.strictEqual(FakeMutationObserver.created, recordObserverCount, 'repeated scans do not duplicate record observers');

const replacementCandidate = makeMissionCandidate(lifecycleDoc, '2 Fire engines');
lifecycleCandidate.source.isConnected = false;
lifecycleCandidate.root.isConnected = false;
candidates = [replacementCandidate];
api.scan();
flushAnimationFrames();
assert.strictEqual(api.records.size, 1, 'mission-window replacement tears down the previous record');
assert.strictEqual(lifecycleDoc.querySelectorAll('#mc-map-command-toolkit-mission-requirements').length, 1, 'mission navigation retains one panel');
assert.strictEqual(replacementCandidate.source.dataset.mcmsRequirementsSourceHidden, '1', 'replacement mission source becomes owned');

replacementCandidate.source._lssmActive = true;
api.scan();
flushAnimationFrames();
assert.strictEqual(api.records.size, 0, 'LSSM activation after Toolkit load removes the Toolkit panel');
assert.strictEqual(replacementCandidate.source.dataset.mcmsRequirementsSourceHidden, undefined, 'LSSM takeover restores MissionChief source ownership');
replacementCandidate.source._lssmActive = false;
api.scan();
flushAnimationFrames();
assert.strictEqual(api.records.size, 1, 'Toolkit resumes when the LSSM equivalent is disabled');

const lssmFirstCandidate = makeMissionCandidate(new FakeDocument());
lssmFirstCandidate.root.ownerDocument.defaultView = { MutationObserver: FakeMutationObserver };
lssmFirstCandidate.source._lssmActive = true;
candidates = [lssmFirstCandidate];
api.scan();
flushAnimationFrames();
assert.strictEqual(api.records.size, 0, 'LSSM-first load order suppresses the Toolkit panel');

context.state.missionRequirements = false;
candidates = [replacementCandidate];
api.scan();
flushAnimationFrames();
assert.strictEqual(api.records.size, 0, 'disabling the feature removes every panel and observer record');
context.state.missionRequirements = true;
assert(listenedEvents.filter(event => event.type === 'change').length === 1, 'delegated checkbox change listener is installed once');
assert(trackedObservers.size >= 1, 'document lifecycle observer remains runtime-owned');

console.log('Mission requirements runtime fixtures passed');
